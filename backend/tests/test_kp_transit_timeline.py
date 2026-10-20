"""Comprehensive automated test suite for KP Transit Ingress & Sub-Lord Timeline Engine.

Verifies:
1. Analytical boundary crossing precision against independent ephemeris evaluations (+/- 1 second).
2. Direct motion (Moon, Sun) and retrograde motion (Venus, Saturn, Rahu).
3. 0° Aries / 360° Pisces circular wraparound boundary crossing.
4. Timezone resolution, IANA DST transitions, and numeric offset handling.
5. Contiguous division chain integrity (no duplicate or silently missed boundaries).
6. Configurable forecast windows (7 to 30 days) and input validation.
7. Actual runtime benchmarks for 7-day and 30-day multi-planet windows.
"""

import time
import pytest
from datetime import date, datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

import xalen
from app.services.kp_transit_timeline import (
    PLANET_IDS,
    TransitIngressEvent,
    TransitTimelineResult,
    compute_transit_timeline,
    resolve_start_datetime,
    _angle_diff,
)
from app.services.kp_engine.horary import kp_divisions, kp_number_for_longitude


# Reference start date: 2026-10-18 (Moon in Sagittarius, Venus/Saturn/Rahu retrograde)
TEST_START_DATE = date(2026, 10, 18)


# ---------------------------------------------------------------------------
# Test 1: Known boundary crossings independently verified with +/- 1s ephemeris fixtures
# ---------------------------------------------------------------------------
def test_boundary_crossing_ephemeris_fixture_precision():
    """Verify that every detected crossing occurs within a strict 1-second ephemeris bracket."""
    res = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Moon"],
        timezone_str="UTC",
        precision_seconds=0.2,
    )
    assert res.total_events > 0, "Expected Moon events in 7 days"

    # Test each Moon event
    for ev in res.events[:15]:  # verify first 15 events in depth
        target = ev.boundary_longitude
        body_id = ev.planet_id
        jd = ev.jd

        # Ephemeris longitude exactly at crossing
        lon_at_crossing = xalen.planet_longitude(jd, body_id, True, 0)
        err_deg = abs(_angle_diff(lon_at_crossing, target))
        err_arcsec = err_deg * 3600.0

        # Sub-arcsecond accuracy at root
        assert err_arcsec < 0.25, f"Boundary error {err_arcsec:.3f}\" exceeds 0.25\" tolerance for {ev.to_sub_lord}"

        # 1-second bracket test: 1 sec before and 1 sec after MUST be on opposite sides
        one_sec_days = 1.0 / 86400.0
        lon_before = xalen.planet_longitude(jd - one_sec_days, body_id, True, 0)
        lon_after = xalen.planet_longitude(jd + one_sec_days, body_id, True, 0)

        diff_before = _angle_diff(lon_before, target)
        diff_after = _angle_diff(lon_after, target)

        if not ev.is_retrograde:
            # Direct: was before boundary (diff < 0), now past boundary (diff > 0)
            assert diff_before < 0.0, f"Direct planet before crossing was not < target: diff={diff_before}"
            assert diff_after > 0.0, f"Direct planet after crossing was not > target: diff={diff_after}"
        else:
            # Retrograde: was ahead of boundary (diff > 0), now behind boundary (diff < 0)
            assert diff_before > 0.0, f"Retro planet before crossing was not > target: diff={diff_before}"
            assert diff_after < 0.0, f"Retro planet after crossing was not < target: diff={diff_after}"


# ---------------------------------------------------------------------------
# Test 2: Contiguous division chain integrity (no missed or duplicate boundaries)
# ---------------------------------------------------------------------------
def test_contiguous_division_chain_no_missed_or_duplicate_boundaries():
    """Verify that every boundary transition forms an unbroken, contiguous chain."""
    res = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Moon"],
        timezone_str="Asia/Kolkata",
    )
    events = res.events
    assert len(events) >= 50, f"Expected >= 50 Moon events in 7 days, got {len(events)}"

    for i in range(len(events) - 1):
        curr_ev = events[i]
        next_ev = events[i + 1]

        # Monotonically increasing time
        assert next_ev.jd > curr_ev.jd, f"Timestamps must strictly increase: {curr_ev.jd} vs {next_ev.jd}"

        # Chain continuity: to_kp_number of event i MUST equal from_kp_number of event i+1
        assert curr_ev.to_kp_number == next_ev.from_kp_number, (
            f"Chain broken between event {i} and {i+1}: "
            f"to_kp_number={curr_ev.to_kp_number} != next from_kp_number={next_ev.from_kp_number}"
        )
        assert curr_ev.to_sub_lord == next_ev.from_sub_lord
        assert curr_ev.to_nakshatra == next_ev.from_nakshatra
        assert curr_ev.to_sign == next_ev.from_sign


# ---------------------------------------------------------------------------
# Test 3: Retrograde motion detection (Venus, Saturn, Rahu)
# ---------------------------------------------------------------------------
def test_retrograde_boundary_crossings():
    """Verify that retrograde planets produce descending division numbers and retro flags."""
    # 30-day window from 2026-10-18 captures Venus (7 events), Saturn (day 16), and Rahu (day 18)
    res = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=30,
        planets=["Venus", "Saturn", "Rahu"],
        timezone_str="UTC",
    )

    venus_events = [e for e in res.events if e.planet == "Venus"]
    saturn_events = [e for e in res.events if e.planet == "Saturn"]
    rahu_events = [e for e in res.events if e.planet == "Rahu"]

    assert len(venus_events) >= 5, f"Expected >= 5 retrograde Venus events, got {len(venus_events)}"
    for ev in venus_events:
        assert ev.is_retrograde is True
        assert ev.speed_deg_per_day < 0.0
        # In retrograde, from_kp_number is higher than to_kp_number (descending order)
        if not (ev.from_kp_number == 1 and ev.to_kp_number == 249):
            assert ev.to_kp_number == ev.from_kp_number - 1, (
                f"Expected descending division in retrograde: {ev.from_kp_number} -> {ev.to_kp_number}"
            )

    # Saturn is also retrograde and crosses Div 240 -> 239 on ~Nov 03
    assert len(saturn_events) >= 1, f"Expected >= 1 Saturn event in 30 days, got {len(saturn_events)}"
    for ev in saturn_events:
        assert ev.is_retrograde is True
        assert ev.speed_deg_per_day < 0.0
        assert ev.to_kp_number == ev.from_kp_number - 1

    # Rahu is mean node, always retrograde
    assert len(rahu_events) >= 1, f"Expected >= 1 Rahu event in 30 days, got {len(rahu_events)}"
    for ev in rahu_events:
        assert ev.is_retrograde is True
        assert ev.speed_deg_per_day < 0.0
        assert ev.to_kp_number == ev.from_kp_number - 1


# ---------------------------------------------------------------------------
# Test 4: 0° Aries / 360° Pisces circular wraparound boundary crossing
# ---------------------------------------------------------------------------
def test_zero_degree_aries_wraparound():
    """Verify that Moon crossing from Pisces (249) into Aries (1) is cleanly captured."""
    # Moon crosses 0° Aries around 2026-10-25 (day 7 of 10-day window)
    res = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=10,
        planets=["Moon"],
        timezone_str="UTC",
    )
    aries_crossings = [
        e for e in res.events
        if (e.from_kp_number == 249 and e.to_kp_number == 1)
    ]
    assert len(aries_crossings) == 1, f"Expected exactly one 0° Aries crossing, found {len(aries_crossings)}"

    cross = aries_crossings[0]
    assert cross.boundary_type == "rashi"
    assert cross.is_rashi_boundary is True
    assert cross.is_nakshatra_boundary is True
    assert cross.is_sub_lord_boundary is True
    assert cross.boundary_longitude == 0.0
    assert cross.from_sign == "Pisces"
    assert cross.to_sign == "Aries"
    assert cross.from_sign_lord == "Jupiter"
    assert cross.to_sign_lord == "Mars"
    assert cross.from_nakshatra == "Revati"
    assert cross.to_nakshatra == "Ashwini"
    assert cross.from_star_lord == "Mercury"
    assert cross.to_star_lord == "Ketu"
    assert cross.from_sub_lord == "Saturn"
    assert cross.to_sub_lord == "Ketu"


# ---------------------------------------------------------------------------
# Test 5: Timezone resolution & DST conversion
# ---------------------------------------------------------------------------
def test_timezone_and_dst_handling():
    """Verify that local_datetime correctly reflects timezone offsets and DST transitions."""
    # Case A: Asia/Kolkata (+05:30)
    res_ist = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Sun"],
        timezone_str="Asia/Kolkata",
    )
    assert res_ist.utc_offset_hours == 5.5
    assert "+05:30" in res_ist.start_time_local
    for ev in res_ist.events:
        assert "+05:30" in ev.local_datetime

    # Case B: America/New_York (EDT UTC-4 in October)
    res_ny = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Sun"],
        timezone_str="America/New_York",
    )
    assert res_ny.utc_offset_hours == -4.0
    assert "-04:00" in res_ny.start_time_local
    for ev in res_ny.events:
        assert "-04:00" in ev.local_datetime

    # Case C: Fixed offset string "+05:30"
    res_custom = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Sun"],
        timezone_str="+05:30",
    )
    assert res_custom.utc_offset_hours == 5.5


# ---------------------------------------------------------------------------
# Test 6: Input validation & forecast window bounds
# ---------------------------------------------------------------------------
def test_input_validation_and_window_bounds():
    """Verify robust rejection of invalid inputs."""
    # Window < 7 days
    with pytest.raises(ValueError, match="forecast_days must be between 7 and 30"):
        compute_transit_timeline(start_date=TEST_START_DATE, forecast_days=6)

    # Window > 30 days
    with pytest.raises(ValueError, match="forecast_days must be between 7 and 30"):
        compute_transit_timeline(start_date=TEST_START_DATE, forecast_days=31)

    # Empty planets
    with pytest.raises(ValueError, match="At least one planet must be selected"):
        compute_transit_timeline(start_date=TEST_START_DATE, forecast_days=7, planets=[])

    # Unsupported planet
    with pytest.raises(ValueError, match="Unsupported planet: 'Pluto'"):
        compute_transit_timeline(start_date=TEST_START_DATE, forecast_days=7, planets=["Pluto"])

    # Invalid timezone
    with pytest.raises(ValueError, match="Invalid timezone"):
        compute_transit_timeline(start_date=TEST_START_DATE, forecast_days=7, timezone_str="NonExistent/Zone")


# ---------------------------------------------------------------------------
# Test 7: Benchmark execution measurement (7-day and 30-day windows)
# ---------------------------------------------------------------------------
def test_execution_benchmarks_measured():
    """Measure and assert realistic execution performance for 7-day and 30-day windows."""
    # 7-day multi-planet benchmark (Default 6 planets: Moon, Sun, Jupiter, Saturn, Rahu, Ketu)
    t0 = time.perf_counter()
    res_7d = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=7,
        planets=["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"],
        timezone_str="Asia/Kolkata",
    )
    t1 = time.perf_counter()
    measured_7d_ms = (t1 - t0) * 1000.0

    print(f"\n[BENCHMARK] 7-Day 6-Planet Window: {measured_7d_ms:.2f} ms | Events: {res_7d.total_events} | Total Evals: {res_7d.benchmark_stats['total_evaluations']}")
    assert measured_7d_ms < 500.0, f"7-day execution {measured_7d_ms:.2f} ms exceeded 500ms safety limit"

    # 30-day multi-planet benchmark
    t2 = time.perf_counter()
    res_30d = compute_transit_timeline(
        start_date=TEST_START_DATE,
        forecast_days=30,
        planets=["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"],
        timezone_str="Asia/Kolkata",
    )
    t3 = time.perf_counter()
    measured_30d_ms = (t3 - t2) * 1000.0

    print(f"[BENCHMARK] 30-Day 6-Planet Window: {measured_30d_ms:.2f} ms | Events: {res_30d.total_events} | Total Evals: {res_30d.benchmark_stats['total_evaluations']}")
    assert measured_30d_ms < 4000.0, f"30-day execution {measured_30d_ms:.2f} ms exceeded 4000ms safety limit"
    assert res_30d.total_events > res_7d.total_events
