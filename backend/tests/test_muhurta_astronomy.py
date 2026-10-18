"""Unit tests for astronomical Panchanga and Muhurta calculation engine.

Covers:
- Precise sunrise and sunset across coordinates and seasons
- Dynamic 8-octant inauspicious periods (Rahu Kalam, Yamagandam, Gulika Kalam)
- 15-part daytime Muhurtas, Abhijit, and Dur Muhurta timings
- Tithi and Nakshatra boundary transitions
- Varjyam (Tyajyam) start ghatika and 4-ghatika duration
- Slot Lagna calculation and bhava placements
"""

import pytest
from datetime import date, datetime, timezone
from app.services.muhurta_engine.astronomy import (
    calculate_solar_sunrise_sunset,
    get_day_octant_periods,
    get_daytime_muhurtas,
    get_tithi_at_jd,
    get_nakshatra_at_jd,
    calculate_daily_panchangam,
    calculate_varjyam_and_amrita,
    get_slot_lagna_and_planets,
    datetime_to_jd,
    jd_to_datetime,
    VARJYAM_START_GHATIKA,
)


def test_sunrise_sunset_chennai():
    """Verify astronomical sunrise and sunset for Chennai (13.0827° N, 80.2707° E)."""
    test_date = date(2026, 10, 18)
    sr_utc, ss_utc, noon_utc = calculate_solar_sunrise_sunset(test_date, 13.0827, 80.2707)

    assert sr_utc < noon_utc < ss_utc
    day_duration_hours = (ss_utc - sr_utc).total_seconds() / 3600.0
    # Day length in Chennai in mid-October is between 11.5 and 12.0 hours
    assert 11.5 <= day_duration_hours <= 12.0


def test_sunrise_sunset_different_latitudes():
    """Verify sunrise and sunset calculation for high latitude (London 51.5074° N, -0.1278° W)."""
    summer_date = date(2026, 6, 21)
    sr_utc, ss_utc, _ = calculate_solar_sunrise_sunset(summer_date, 51.5074, -0.1278)
    summer_duration = (ss_utc - sr_utc).total_seconds() / 3600.0
    # Summer day in London is around 16.5 hours
    assert 15.5 <= summer_duration <= 17.5


def test_day_octants_and_rahu_kalam():
    """Verify dynamic 8-part octant division and Rahu Kalam for each weekday."""
    test_date = date(2026, 10, 18)  # Sunday (weekday_py = 6)
    sr_utc, ss_utc, _ = calculate_solar_sunrise_sunset(test_date, 13.0827, 80.2707)

    # Sunday: Rahu Kalam is 8th octant (last 1/8th of daytime)
    octants = get_day_octant_periods(sr_utc, ss_utc, weekday_py=6)
    rahu = octants["rahu_kalam"]
    assert rahu["part"] == 8
    rahu_end = datetime.fromisoformat(rahu["end_utc"])
    assert abs((rahu_end - ss_utc).total_seconds()) < 2.0  # Finishes exactly at sunset!

    # Monday (weekday_py = 0): Rahu Kalam is 2nd octant
    octants_mon = get_day_octant_periods(sr_utc, ss_utc, weekday_py=0)
    assert octants_mon["rahu_kalam"]["part"] == 2


def test_15_muhurtas_and_abhijit():
    """Verify 15-part daytime division and Abhijit Muhurta placement."""
    test_date = date(2026, 10, 18)  # Sunday
    sr_utc, ss_utc, _ = calculate_solar_sunrise_sunset(test_date, 13.0827, 80.2707)
    muhurtas = get_daytime_muhurtas(sr_utc, ss_utc, weekday_py=6)

    abhijit = muhurtas["abhijit"]
    ab_start = datetime.fromisoformat(abhijit["start_utc"])
    ab_end = datetime.fromisoformat(abhijit["end_utc"])
    assert ab_start < ab_end
    # Duration of 1/15th of approx 11.8 hours = ~47 minutes
    assert 40 <= abhijit["duration_minutes"] <= 55
    # On Sunday, Abhijit is clean of Dur Muhurta
    assert abhijit["is_dur_muhurta_clash"] is False

    # Wednesday (weekday_py = 2): Abhijit coincides with Dur Muhurta (8th muhurta)
    muhurtas_wed = get_daytime_muhurtas(sr_utc, ss_utc, weekday_py=2)
    assert muhurtas_wed["abhijit"]["is_dur_muhurta_clash"] is True


def test_varjyam_ghatika_calculation():
    """Verify 4-ghatika Varjyam calculation (Ashwini starts at 50th ghatika)."""
    start_utc = datetime(2026, 10, 18, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 10, 19, 0, 0, tzinfo=timezone.utc)  # 24 hours
    # Ashwini (nak_idx = 1) has start_ghatika 50
    varjyam, amrita = calculate_varjyam_and_amrita(1, start_utc, end_utc)
    assert varjyam["start_ghatika"] == 50.0
    # 4 ghatikas in a 24-hour nakshatra = 4/60 * 24 * 60 = 96 minutes
    assert abs(varjyam["duration_minutes"] - 96.0) < 1.0


def test_panchangam_comprehensive_payload():
    """Verify full daily Panchangam returns valid limbs and boundary timestamps."""
    res = calculate_daily_panchangam(
        event_date=date(2026, 10, 18),
        latitude=13.0827,
        longitude=80.2707,
        timezone_str="Asia/Kolkata",
    )
    assert "astronomical" in res
    assert "tithi" in res
    assert "nakshatra" in res
    assert "yoga" in res
    assert "karana" in res
    assert "inauspicious_periods" in res
    assert "auspicious_periods" in res

    # Tithi boundaries
    tithi = res["tithi"]
    t_start = datetime.fromisoformat(tithi["start_time_utc"])
    t_end = datetime.fromisoformat(tithi["end_time_utc"])
    assert t_start < t_end
    assert 1 <= tithi["number"] <= 30

    # Nakshatra boundaries
    nak = res["nakshatra"]
    n_start = datetime.fromisoformat(nak["start_time_utc"])
    n_end = datetime.fromisoformat(nak["end_time_utc"])
    assert n_start < n_end
    assert 1 <= nak["number"] <= 27


def test_slot_lagna_and_bhava_occupants():
    """Verify rising Ascendant and 12-bhava placement of planets."""
    slot_utc = datetime(2026, 10, 18, 6, 0, tzinfo=timezone.utc)
    res = get_slot_lagna_and_planets(slot_utc, 13.0827, 80.2707, ayanamsa_id=0)

    asc = res["ascendant"]
    assert 1 <= asc["sign_index"] <= 12
    assert "sign_name" in asc
    assert "sign_name_ta" in asc

    # Verify 9 Vedic planets mapped
    planets = res["planets"]
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p_name in planets
        assert 1 <= planets[p_name]["bhava"] <= 12
