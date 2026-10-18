"""Comprehensive automated tests for 5-level Vimshottari Dasa hierarchy and calendar age calculations.

Covers:
1. 5-level hierarchy serialization and correct nesting.
2. Exact label mapping for all 5 levels (Mahadasha, Antardasha, Pratyantardasha, Sookshmadasha, Pranadasha).
3. Parent/child boundary containment and sibling contiguity.
4. Duration preservation within 0.001 day tolerance.
5. Exact calendar age calculation across leap days, month-ends, Dec/Jan boundaries, and anniversaries.
6. Local timezone consistency and Julian Day conversion.
7. Active period detection using half-open intervals [start_jd, end_jd) down to Prana level.
8. Error handling and unavailable states for malformed inputs or dates outside range.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.services.dasa_calendar import (
    calculate_calendar_age,
    format_calendar_age,
    jd_to_gregorian_datetime,
    gregorian_to_iso,
)

client = TestClient(app)

SAMPLE_CHART = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "depth": 5,
    "target_date": "2026-10-17",
}


# ===========================================================================
# 1. Exact Calendar Age Calculation Unit Tests
# ===========================================================================

def test_calendar_age_basic_anniversary():
    # Exactly on birthday
    age = calculate_calendar_age(1990, 5, 15, 2024, 5, 15)
    assert age == (34, 0, 0)
    assert format_calendar_age(age) == "34 years, 0 months, 0 days"
    assert format_calendar_age(age, lang="ta") == "34 ஆண்டுகள், 0 மாதங்கள், 0 நாட்கள்"


def test_calendar_age_birth_day():
    # Born on same day -> 0y 0m 0d
    age = calculate_calendar_age(1990, 5, 15, 1990, 5, 15)
    assert age == (0, 0, 0)
    assert format_calendar_age(age) == "0 years, 0 months, 0 days"


def test_calendar_age_sample_from_prompt():
    # 24 years, 3 months, 6 days
    age1 = calculate_calendar_age(1990, 5, 15, 2014, 8, 21)
    assert age1 == (24, 3, 6)
    assert format_calendar_age(age1) == "24 years, 3 months, 6 days"

    # 25 years, 0 months, 12 days
    age2 = calculate_calendar_age(1980, 8, 30, 2005, 9, 11)
    assert age2 == (25, 0, 12)
    assert format_calendar_age(age2) == "25 years, 0 months, 12 days"

    # 26 years, 11 months, 28 days
    age3 = calculate_calendar_age(1980, 8, 30, 2007, 8, 27)
    assert age3 == (26, 11, 28)
    assert format_calendar_age(age3) == "26 years, 11 months, 28 days"


def test_calendar_age_leap_day_birth():
    # Born on Feb 29 in leap year 2000
    # Day before 1 year: 2001-02-28
    age_before = calculate_calendar_age(2000, 2, 29, 2001, 2, 28)
    assert age_before == (0, 11, 30)

    # Reaching 1 full year on 2001-03-01
    age_common = calculate_calendar_age(2000, 2, 29, 2001, 3, 1)
    assert age_common == (1, 0, 0)

    # Next leap year anniversary: 2004-02-29
    age_leap = calculate_calendar_age(2000, 2, 29, 2004, 2, 29)
    assert age_leap == (4, 0, 0)


def test_calendar_age_crossing_december_january():
    # Born 1990-12-25, target 1991-01-05 -> 11 days old
    age = calculate_calendar_age(1990, 12, 25, 1991, 1, 5)
    assert age == (0, 0, 11)


def test_calendar_age_month_end_31st():
    # Born 2020-01-31, target 2020-03-01 (Feb 2020 has 29 days)
    age1 = calculate_calendar_age(2020, 1, 31, 2020, 3, 1)
    assert age1 == (0, 0, 30)

    # Target 2020-03-02 -> exactly 1 full month
    age2 = calculate_calendar_age(2020, 1, 31, 2020, 3, 2)
    assert age2 == (0, 1, 0)


def test_calendar_age_target_before_birth():
    # Target date before birth must return None and formatted as unavailable
    age = calculate_calendar_age(1990, 5, 15, 1989, 5, 15)
    assert age is None
    assert format_calendar_age(age) == "Age unavailable"
    assert format_calendar_age(age, lang="ta") == "வயது கிடைக்கவில்லை"


# ===========================================================================
# 2. Julian Day to Gregorian Conversion Verification
# ===========================================================================

def test_jd_to_gregorian_j2000():
    # J2000.0 is 2000-01-01 12:00:00 UT
    y, m, d, h, mn, s = jd_to_gregorian_datetime(2451545.0, 0.0)
    assert (y, m, d, h, mn, s) == (2000, 1, 1, 12, 0, 0)
    assert gregorian_to_iso(y, m, d) == "2000-01-01"


def test_jd_to_gregorian_with_timezone_offset():
    # At 2451545.0 with +05:30 offset (+5.5h) -> 17:30:00 local time
    y, m, d, h, mn, s = jd_to_gregorian_datetime(2451545.0, 5.5)
    assert (y, m, d, h, mn, s) == (2000, 1, 1, 17, 30, 0)
    assert gregorian_to_iso(y, m, d, h, mn, s, include_time=True) == "2000-01-01T17:30:00"


# ===========================================================================
# 3. Full 5-Level Hierarchy API Response & Structure Verification
# ===========================================================================

def test_dasa_five_level_hierarchy_serialization():
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    data = res.json()

    tree = data["dasa_tree"]
    assert len(tree) == 9, "Must return exactly 9 Mahadashas"

    # Level 1: Mahadashas
    m0 = tree[0]
    assert m0["level"] == "Mahadasha"
    assert m0["lord"] == "Sun"
    assert m0["start_date_iso"] == "1990-05-15"
    assert m0["start_age"] == "0 years, 0 months, 0 days"
    assert m0["end_date_iso"] is not None
    assert m0["end_age"] is not None
    assert len(m0["sub_periods"]) == 9

    # Level 2: Antardashas (Bhuktis)
    a0 = m0["sub_periods"][0]
    assert a0["level"] == "Antardasha"
    assert a0["lord"] == "Sun"
    assert a0["start_date_iso"] == "1990-05-15"
    assert a0["start_age"] == "0 years, 0 months, 0 days"
    assert len(a0["sub_periods"]) == 9

    # Level 3: Pratyantardashas (Antarams)
    p0 = a0["sub_periods"][0]
    assert p0["level"] == "Pratyantardasha"
    assert p0["lord"] == "Sun"
    assert p0["start_date_iso"] == "1990-05-15"
    assert p0["start_age"] == "0 years, 0 months, 0 days"
    assert len(p0["sub_periods"]) == 9

    # Level 4: Sookshmadashas (Sookshmas)
    s0 = p0["sub_periods"][0]
    assert s0["level"] == "Sookshmadasha"
    assert s0["lord"] == "Sun"
    assert "T" in s0["start_date_iso"]  # Time included for sub-daily precision
    assert s0["start_age"] == "0 years, 0 months, 0 days"
    assert len(s0["sub_periods"]) == 9

    # Level 5: Pranadashas (Pranas)
    pr0 = s0["sub_periods"][0]
    assert pr0["level"] == "Pranadasha"
    assert pr0["lord"] == "Sun"
    assert "T" in pr0["start_date_iso"]
    assert pr0["start_age"] == "0 years, 0 months, 0 days"
    assert len(pr0["sub_periods"]) == 0, "Pranadasha is the 5th and final terminal level"


def test_dasa_five_level_containment_and_durations():
    """Verify that every child period is strictly contained within parent boundaries
    and that child duration sums equal the parent duration within 0.001 day tolerance.
    """
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    data = res.json()

    def check_node(node, depth=1):
        subs = node.get("sub_periods", [])
        if not subs:
            return

        assert abs(subs[0]["start_jd"] - node["start_jd"]) < 1e-4, f"Start mismatch at depth {depth}"
        assert abs(subs[-1]["end_jd"] - node["end_jd"]) < 1e-4, f"End mismatch at depth {depth}"

        prev_end = subs[0]["start_jd"]
        total_child_days = 0.0

        for child in subs:
            # Containment
            assert child["start_jd"] >= node["start_jd"] - 1e-5
            assert child["end_jd"] <= node["end_jd"] + 1e-5
            # Sibling contiguity (no gaps or overlaps)
            assert abs(child["start_jd"] - prev_end) < 1e-4
            prev_end = child["end_jd"]
            total_child_days += child["duration_days"]

            # Verify that dates and ages exist
            assert child["start_date_iso"] is not None
            assert child["end_date_iso"] is not None
            assert child["start_age"] is not None
            assert child["end_age"] is not None

            check_node(child, depth + 1)

        # Duration preservation within 0.001 day tolerance
        assert abs(total_child_days - node["duration_days"]) < 0.001

    for maha in data["dasa_tree"]:
        check_node(maha)


# ===========================================================================
# 4. Active Period Detection at all 5 levels with Target Age
# ===========================================================================

def test_active_period_detection_all_five_levels():
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    data = res.json()

    active = data["active_period"]
    assert active is not None
    assert active["mahadasha"] == "Rahu"
    assert active["antardasha"] == "Moon"
    assert active["pratyantardasha"] == "Rahu"
    assert active["sookshmadasha"] == "Mercury"
    assert active["pranadasha"] == "Moon"
    assert active["target_date_iso"] == "2026-10-17"
    assert active["target_age"] == "36 years, 5 months, 2 days"
    assert active["target_age_dict"] == {"years": 36, "months": 5, "days": 2}


def test_target_date_outside_range():
    # Date prior to birth (1980-01-01 < 1990-05-15)
    res_before = client.post(
        "/api/v1/horoscope/dasa",
        json={**SAMPLE_CHART, "target_date": "1980-01-01"},
    )
    assert res_before.status_code == 200
    assert res_before.json()["active_period"] is None

    # Date after 120-year cycle (2120-01-01 > 2110)
    res_after = client.post(
        "/api/v1/horoscope/dasa",
        json={**SAMPLE_CHART, "target_date": "2120-01-01"},
    )
    assert res_after.status_code == 200
    assert res_after.json()["active_period"] is None


def test_backward_compatibility_depths():
    # Depth 1: Mahadashas only, sub_periods empty
    r1 = client.post("/api/v1/horoscope/dasa", json={**SAMPLE_CHART, "depth": 1})
    assert r1.status_code == 200
    d1 = r1.json()
    assert len(d1["dasa_tree"]) == 9
    assert len(d1["dasa_tree"][0]["sub_periods"]) == 0
    assert d1["dasa_tree"][0]["start_age"] is not None

    # Depth 2: Mahadasha + Antardasha
    r2 = client.post("/api/v1/horoscope/dasa", json={**SAMPLE_CHART, "depth": 2})
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2["dasa_tree"][0]["sub_periods"]) == 9
    assert len(d2["dasa_tree"][0]["sub_periods"][0]["sub_periods"]) == 0
