"""Comprehensive Parameterized Regression Suite for Global Birth-Balance Dasa Timelines.

Validates the canonical Vimshottari theoretical clipping behavior across:
- All 9 Mahadasha lords (Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)
- Multiple birth-balance scenarios:
    1. Near beginning (5% elapsed)
    2. Near middle (50% elapsed)
    3. Near end (95% elapsed)
    4. Near Bhukti boundary (within 0.001 deg of boundary)
    5. Near Mahadasha boundary (within 0.0001 deg of 0% and 100%)
- Exact mathematical duration preservation across all 5 levels.
- Sibling contiguity (zero gaps, zero overlaps).
- Theoretical start and end Julian days and dates.
- KP sub lord alignment at birth instant.
- FastAPI endpoint `/api/v1/horoscope/dasa` contract compliance.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.services.dasa_service import (
    generate_vimshottari_hierarchy,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_YEARS,
    VIMSHOTTARI_INDEX,
    STAR_SPAN_DEG,
    sub_info,
    sub_sub_info,
    sub_sub_sub_info,
    sub_sub_sub_sub_info,
    star_lord,
    star_index,
)
from app.schemas.dasa import DasaPeriodNode

client = TestClient(app)

# Base start degrees of the 9 nakshatras in the first 120 degrees of the zodiac
NAKSHATRA_STARTS = {
    "Ketu": 0.0 * STAR_SPAN_DEG,      # Ashwini: 0°
    "Venus": 1.0 * STAR_SPAN_DEG,     # Bharani: 13° 20'
    "Sun": 2.0 * STAR_SPAN_DEG,       # Krittika: 26° 40'
    "Moon": 3.0 * STAR_SPAN_DEG,      # Rohini: 40°
    "Mars": 4.0 * STAR_SPAN_DEG,      # Mrigashira: 53° 20'
    "Rahu": 5.0 * STAR_SPAN_DEG,      # Ardra: 66° 40'
    "Jupiter": 6.0 * STAR_SPAN_DEG,   # Punarvasu: 80°
    "Saturn": 7.0 * STAR_SPAN_DEG,    # Pushya: 93° 20'
    "Mercury": 8.0 * STAR_SPAN_DEG,   # Ashlesha: 106° 40'
}

BIRTH_JD_EPOCH = 2448026.875  # 1990-05-15 14:30:00 UT
BIRTH_DATE = date(1990, 5, 15)


def get_test_longitudes():
    """Generate parameterized test cases covering all 9 lords and 5 balance scenarios."""
    cases = []
    for lord in VIMSHOTTARI_ORDER:
        start_deg = NAKSHATRA_STARTS[lord]
        span = STAR_SPAN_DEG

        # 1. Near beginning: 5% elapsed
        cases.append((lord, "near_beginning", start_deg + 0.05 * span))

        # 2. Near middle: 50% elapsed
        cases.append((lord, "near_middle", start_deg + 0.50 * span))

        # 3. Near end: 95% elapsed
        cases.append((lord, "near_end", start_deg + 0.95 * span))

        # 4. Near Bhukti boundary: end of first Bhukti
        f1 = VIMSHOTTARI_YEARS[lord] / 120.0
        boundary_deg = start_deg + f1 * span
        cases.append((lord, "near_bhukti_boundary_before", boundary_deg - 0.001))
        cases.append((lord, "near_bhukti_boundary_after", boundary_deg + 0.001))

        # 5. Near Mahadasha boundary
        cases.append((lord, "near_mahadasha_start_boundary", start_deg + 0.0001))
        cases.append((lord, "near_mahadasha_end_boundary", start_deg + span - 0.0001))

    return cases


@pytest.mark.parametrize("expected_lord, scenario, moon_lon", get_test_longitudes())
def test_vimshottari_hierarchy_global_invariants(expected_lord: str, scenario: str, moon_lon: float):
    """Verify all 10 mathematical and structural requirements across every lord and scenario."""
    depth = 5
    tree, balance = generate_vimshottari_hierarchy(
        moon_lon=moon_lon,
        birth_jd=BIRTH_JD_EPOCH,
        birth_date=BIRTH_DATE,
        utc_offset_hours=5.5,
        depth=depth,
    )

    # Invariant 1: Exactly 9 Mahadashas generated
    assert len(tree) == 9

    # Invariant 2: First Mahadasha lord matches Nakshatra lord
    first_md = tree[0]
    assert first_md.lord == expected_lord
    assert first_md.is_active_at_birth is True

    # Invariant 3: Mahadasha 0 displayed start is exact birth instant
    assert abs(first_md.start_jd - BIRTH_JD_EPOCH) < 1e-9

    # Invariant 4: Theoretical start is before birth, theoretical end matches displayed end
    full_md_years = VIMSHOTTARI_YEARS[expected_lord]
    full_md_days = full_md_years * 365.25
    assert first_md.theoretical_start_jd is not None
    assert first_md.theoretical_end_jd is not None
    assert first_md.theoretical_start_jd <= BIRTH_JD_EPOCH + 1e-7
    assert first_md.theoretical_end_jd > BIRTH_JD_EPOCH
    assert abs((first_md.theoretical_end_jd - first_md.theoretical_start_jd) - full_md_days) < 1e-4
    assert abs(first_md.end_jd - first_md.theoretical_end_jd) < 1e-7

    # Invariant 5: Active Bhukti lord at birth matches KP sub lord
    expected_sub = sub_info(moon_lon % 360.0)
    displayed_bhuktis = first_md.sub_periods
    assert len(displayed_bhuktis) >= 1
    first_bhukti = displayed_bhuktis[0]
    assert first_bhukti.lord == expected_sub.lord
    assert first_bhukti.is_active_at_birth is True

    # Invariant 6: First displayed Bhukti begins at birth instant and contains ONLY remaining duration
    assert abs(first_bhukti.start_jd - BIRTH_JD_EPOCH) < 1e-9
    assert first_bhukti.theoretical_start_jd is not None
    assert first_bhukti.theoretical_start_jd <= BIRTH_JD_EPOCH + 1e-7
    assert abs(first_bhukti.duration_days - (first_bhukti.theoretical_end_jd - BIRTH_JD_EPOCH)) < 1e-7

    # Invariant 7: Subsequent Bhuktis preserve their full canonical durations
    for subsequent_bhukti in displayed_bhuktis[1:]:
        assert subsequent_bhukti.is_active_at_birth is False
        b_lord = subsequent_bhukti.lord
        expected_canonical_dur = full_md_days * (VIMSHOTTARI_YEARS[b_lord] / 120.0)
        assert abs(subsequent_bhukti.duration_days - expected_canonical_dur) < 1e-4
        assert abs(subsequent_bhukti.start_jd - subsequent_bhukti.theoretical_start_jd) < 1e-7
        assert abs(subsequent_bhukti.end_jd - subsequent_bhukti.theoretical_end_jd) < 1e-7

    # Invariant 8: All displayed Bhuktis sum to parent Mahadasha duration (Dasa Irupu)
    total_bhukti_days = sum(b.duration_days for b in displayed_bhuktis)
    assert abs(total_bhukti_days - first_md.duration_days) < 1e-4

    # Invariant 9: Sibling contiguity: no gaps or overlaps between Bhuktis
    prev_end = first_bhukti.start_jd
    for b in displayed_bhuktis:
        assert abs(b.start_jd - prev_end) < 1e-7
        prev_end = b.end_jd
    assert abs(displayed_bhuktis[-1].end_jd - first_md.end_jd) < 1e-7

    # Invariant 10: Recursive verification down all 5 levels for the active-at-birth lineage
    active_node = first_md
    for lvl_idx in range(1, depth):
        subs = active_node.sub_periods
        assert len(subs) >= 1
        active_child = subs[0]
        assert active_child.is_active_at_birth is True
        assert abs(active_child.start_jd - BIRTH_JD_EPOCH) < 1e-9

        # Sum of child durations equals active parent remaining duration
        sum_child_dur = sum(c.duration_days for c in subs)
        assert abs(sum_child_dur - active_node.duration_days) < 1e-4

        # Non-active siblings in this list have full canonical duration
        for subsequent_child in subs[1:]:
            assert subsequent_child.is_active_at_birth is False
            assert subsequent_child.theoretical_duration_days is not None
            assert abs(subsequent_child.duration_days - subsequent_child.theoretical_duration_days) < 1e-4

        active_node = active_child

    # Invariant 11: Subsequent Mahadashas (cycles 2..9) have 9 full subperiods
    for subsequent_md in tree[1:]:
        assert subsequent_md.is_active_at_birth is False
        assert len(subsequent_md.sub_periods) == 9
        for b in subsequent_md.sub_periods:
            assert b.is_active_at_birth is False
            assert abs(b.duration_days - b.theoretical_duration_days) < 1e-4


def test_dasa_api_endpoint_global_contract():
    """Verify API endpoint serializes theoretical fields and correct Bhukti balance."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "depth": 5,
    }
    res = client.post("/api/v1/horoscope/dasa", json=payload)
    assert res.status_code == 200
    data = res.json()

    first_md = data["dasa_tree"][0]
    assert first_md["is_active_at_birth"] is True
    assert "theoretical_start_jd" in first_md
    assert "theoretical_end_jd" in first_md
    assert "theoretical_duration_days" in first_md
    assert "theoretical_start_date_iso" in first_md
    assert "theoretical_end_date_iso" in first_md

    # First Bhukti
    first_bhukti = first_md["sub_periods"][0]
    assert first_bhukti["is_active_at_birth"] is True
    assert first_bhukti["start_date_iso"].startswith("1990-05-15")
    assert first_bhukti["theoretical_start_date_iso"] is not None
    # Theoretical start is before birth
    assert first_bhukti["theoretical_start_date_iso"] < first_bhukti["start_date_iso"]

    # Subsequent Bhuktis have matching displayed and theoretical dates
    for subsequent_bhukti in first_md["sub_periods"][1:]:
        assert subsequent_bhukti["is_active_at_birth"] is False
        assert subsequent_bhukti["start_date_iso"] == subsequent_bhukti["theoretical_start_date_iso"].split("T")[0]
