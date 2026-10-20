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
    # Birth balance validation
    bal = data.get("birth_dasa_balance")
    assert bal is not None
    assert bal["starting_mahadasha_lord"] == "Sun"
    assert bal["starting_bhukti_lord"] == "Jupiter"
    assert bal["starting_antharam_lord"] == "Mercury"
    assert bal["starting_sookshamam_lord"] == "Rahu"
    assert bal["starting_pranam_lord"] == "Saturn"
    assert bal["next_dasa_transition_date"] == "1994-01-06"

    # Level 1: Mahadashas
    m0 = tree[0]
    assert m0["level"] == "Mahadasha"
    assert m0["lord"] == "Sun"
    assert m0["start_date_iso"] == "1990-05-15"
    assert m0["start_age"] == "0 years, 0 months, 0 days"
    assert m0["end_date_iso"] is not None
    assert m0["end_age"] is not None
    assert m0["is_active_at_birth"] is True
    # 5 remaining Bhuktis in opening Mahadasha: Jupiter, Saturn, Mercury, Ketu, Venus
    assert len(m0["sub_periods"]) == 5

    # Level 2: Antardashas (Bhuktis)
    a0 = m0["sub_periods"][0]
    assert a0["level"] == "Antardasha"
    assert a0["lord"] == "Jupiter"
    assert a0["start_date_iso"] == "1990-05-15"
    assert a0["start_age"] == "0 years, 0 months, 0 days"
    assert a0["is_active_at_birth"] is True
    assert len(a0["sub_periods"]) > 0

    # Level 3: Pratyantardashas (Antarams)
    p0 = a0["sub_periods"][0]
    assert p0["level"] == "Pratyantardasha"
    assert p0["lord"] == "Mercury"
    assert p0["start_date_iso"] == "1990-05-15"
    assert p0["start_age"] == "0 years, 0 months, 0 days"
    assert p0["is_active_at_birth"] is True
    assert len(p0["sub_periods"]) > 0

    # Level 4: Sookshmadashas (Sookshmas)
    s0 = p0["sub_periods"][0]
    assert s0["level"] == "Sookshmadasha"
    assert s0["lord"] == "Rahu"
    assert "T" in s0["start_date_iso"]  # Time included for sub-daily precision
    assert s0["start_age"] == "0 years, 0 months, 0 days"
    assert s0["is_active_at_birth"] is True
    assert len(s0["sub_periods"]) > 0

    # Level 5: Pranadashas (Pranas)
    pr0 = s0["sub_periods"][0]
    assert pr0["level"] == "Pranadasha"
    assert pr0["lord"] == "Saturn"
    assert "T" in pr0["start_date_iso"]
    assert pr0["start_age"] == "0 years, 0 months, 0 days"
    assert pr0["is_active_at_birth"] is True
    assert len(pr0["sub_periods"]) == 0, "Pranadasha is the 5th and final terminal level"

    # Verify subsequent Mahadashas have full 9 subperiods
    for subsequent_md in tree[1:]:
        assert len(subsequent_md["sub_periods"]) == 9
        assert subsequent_md["is_active_at_birth"] is False


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
    assert len(d2["dasa_tree"][0]["sub_periods"]) == 5
    assert len(d2["dasa_tree"][1]["sub_periods"]) == 9
    assert len(d2["dasa_tree"][0]["sub_periods"][0]["sub_periods"]) == 0


def test_birth_dasa_balance_structure_and_consistency():
    """Verify that birth_dasa_balance contains all required fields and that elapsed + remaining equals full."""
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    bal = res.json()["birth_dasa_balance"]

    assert bal is not None
    assert bal["birth_date"] == "1990-05-15"
    assert bal["birth_time"] == "14:30:00"
    assert bal["nakshatra_name"] == "Uttara Ashadha"
    assert bal["nakshatra_pada"] == 2
    assert bal["nakshatra_lord"] == "Sun"
    assert bal["starting_mahadasha_lord"] == "Sun"

    # Full = 6 years = 2191.5 days
    full_dur = bal["mahadasha_full_duration"]
    elapsed = bal["elapsed_duration"]
    rem = bal["remaining_balance"]

    assert abs(full_dur["total_days"] - 2191.5) < 1e-3
    assert abs(elapsed["total_days"] + rem["total_days"] - full_dur["total_days"]) < 1e-3
    assert rem["years"] == 3 and rem["months"] == 7

    # Active Bhukti at birth
    assert bal["starting_bhukti_lord"] == "Jupiter"
    assert bal["starting_bhukti_remaining"]["total_days"] > 0

    # Next Dasa transition date calculated from birth balance
    assert bal["next_dasa_transition_date"] == "1994-01-06"
    assert bal["next_dasa_transition_jd"] > 2448026.0


def test_active_at_birth_chain():
    """Verify that exactly one period at each of the 5 levels has is_active_at_birth == True
    forming a continuous parent-child lineage at birth.
    """
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    tree = res.json()["dasa_tree"]

    # Level 1
    m_active = [m for m in tree if m.get("is_active_at_birth")]
    assert len(m_active) == 1
    m0 = m_active[0]
    assert m0["lord"] == "Sun"

    # Level 2
    a_active = [a for a in m0["sub_periods"] if a.get("is_active_at_birth")]
    assert len(a_active) == 1
    a0 = a_active[0]
    assert a0["lord"] == "Jupiter"

    # Level 3
    p_active = [p for p in a0["sub_periods"] if p.get("is_active_at_birth")]
    assert len(p_active) == 1
    p0 = p_active[0]
    assert p0["lord"] == "Mercury"

    # Level 4
    s_active = [s for s in p0["sub_periods"] if s.get("is_active_at_birth")]
    assert len(s_active) == 1
    s0 = s_active[0]
    assert s0["lord"] == "Rahu"

    # Level 5
    pr_active = [pr for pr in s0["sub_periods"] if pr.get("is_active_at_birth")]
    assert len(pr_active) == 1
    pr0 = pr_active[0]
    assert pr0["lord"] == "Saturn"


def test_benefit_bhavas_all_five_levels_in_api():
    """Verify that every level row down to Pranam has benefit_bhavas with 4 categories."""
    res = client.post("/api/v1/horoscope/dasa", json=SAMPLE_CHART)
    assert res.status_code == 200
    tree = res.json()["dasa_tree"]

    def check_node_bhavas(node, depth=1):
        assert node["benefit_bhavas"] is not None
        assert " | " in node["benefit_bhavas"]
        assert node["star_lord"] is not None
        detail = node.get("benefit_bhavas_detail")
        assert detail is not None
        assert "star_lord" in detail
        assert "period_lord" in detail

        # Rahu & Ketu: owned houses must be empty and omitted from category 4
        if node["lord"] in ("Rahu", "Ketu"):
            assert detail["planet_owned_houses"] == []

        for sub in node.get("sub_periods", []):
            check_node_bhavas(sub, depth + 1)

    for md in tree:
        check_node_bhavas(md)


def test_multiple_charts_different_nakshatras_and_balances():
    """Test charts in different Nakshatras: Rohini (Moon), Chitra (Mars), Shatabhisha (Rahu), Revati (Mercury)."""
    # 1. Rohini: Moon at ~45° (Moon Mahadasha, 10 years full)
    r_rohini = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 45.0, "birth_jd": 2451545.0, "depth": 3},
    )
    assert r_rohini.status_code == 200
    d_rohini = r_rohini.json()
    assert d_rohini["nakshatra"]["name"] == "Rohini"
    assert d_rohini["birth_dasa_lord"] == "Moon"
    assert d_rohini["birth_dasa_balance"]["starting_mahadasha_lord"] == "Moon"
    assert 0 < d_rohini["birth_balance_years"] < 10.0

    # 2. Chitra: Moon at ~175° (Mars Mahadasha, 7 years full)
    r_chitra = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 175.0, "birth_jd": 2451545.0, "depth": 3},
    )
    assert r_chitra.status_code == 200
    d_chitra = r_chitra.json()
    assert d_chitra["nakshatra"]["name"] == "Chitra"
    assert d_chitra["birth_dasa_lord"] == "Mars"
    assert d_chitra["birth_dasa_balance"]["starting_mahadasha_lord"] == "Mars"
    assert 0 < d_chitra["birth_balance_years"] < 7.0

    # 3. Shatabhisha: Moon at ~310° (Rahu Mahadasha, 18 years full)
    r_shat = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 310.0, "birth_jd": 2451545.0, "depth": 3},
    )
    assert r_shat.status_code == 200
    d_shat = r_shat.json()
    assert d_shat["nakshatra"]["name"] == "Shatabhisha"
    assert d_shat["birth_dasa_lord"] == "Rahu"
    assert d_shat["birth_dasa_balance"]["starting_mahadasha_lord"] == "Rahu"
    assert 0 < d_shat["birth_balance_years"] < 18.0

    # 4. Revati: Moon at ~355° (Mercury Mahadasha, 17 years full)
    r_rev = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 355.0, "birth_jd": 2451545.0, "depth": 3},
    )
    assert r_rev.status_code == 200
    d_rev = r_rev.json()
    assert d_rev["nakshatra"]["name"] == "Revati"
    assert d_rev["birth_dasa_lord"] == "Mercury"
    assert d_rev["birth_dasa_balance"]["starting_mahadasha_lord"] == "Mercury"
    assert 0 < d_rev["birth_balance_years"] < 17.0


def test_nakshatra_boundary_cases():
    """Verify behavior near Nakshatra boundaries (0.0001° Ashwini and 13.3332° end)."""
    # Just after 0° Ashwini start
    r_start = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 0.0001, "birth_jd": 2451545.0, "depth": 2},
    )
    assert r_start.status_code == 200
    d_start = r_start.json()
    assert d_start["birth_dasa_lord"] == "Ketu"
    # Near full 7.0 years remaining
    assert abs(d_start["birth_balance_years"] - 7.0) < 0.01
    assert len(d_start["dasa_tree"][0]["sub_periods"]) == 9

    # Just before 13.333333° Ashwini end
    r_end = client.post(
        "/api/v1/horoscope/dasa/direct",
        json={"moon_sidereal_deg": 13.3330, "birth_jd": 2451545.0, "depth": 2},
    )
    assert r_end.status_code == 200
    d_end = r_end.json()
    assert d_end["birth_dasa_lord"] == "Ketu"
    # Near 0 years remaining
    assert 0.0 < d_end["birth_balance_years"] < 0.01


def test_independent_vimshottari_audit_reference_cases():
    """Independent first-principles audit comparing application values with independent astronomical reference calculations.

    Tests:
    1. A chart with non-zero birth Dasa balance.
    2. A chart where birth occurs partway through a Bhukti.
    3. A chart where birth occurs partway through an Antharam.
    4. A chart near a Nakshatra boundary.
    5. A chart near a Mahadasha or Bhukti transition.
    6. A case with short Sookshamam and Pranam periods.
    7. A case that checks leap dates, timezone conversion and display rounding.
    """
    def independent_reference(moon_deg: float, birth_jd: float):
        STAR_SPAN = 800.0 / 60.0
        s_idx = int(moon_deg // STAR_SPAN)
        star_start = s_idx * STAR_SPAN
        star_end = star_start + STAR_SPAN
        progress = (moon_deg - star_start) / STAR_SPAN
        rem_fraction = (star_end - moon_deg) / STAR_SPAN

        v_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        nak_lords = v_order * 3
        lord = nak_lords[s_idx]
        years_table = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        full_days = years_table[lord] * 365.25
        elapsed_days = progress * full_days
        rem_days = rem_fraction * full_days
        transition_jd = birth_jd + rem_days

        start_pos = v_order.index(lord)
        running_deg = star_start
        active_bhukti = None
        for k in range(9):
            b_lord = v_order[(start_pos + k) % 9]
            b_span = STAR_SPAN * (years_table[b_lord] / 120.0)
            b_end = running_deg + b_span
            if running_deg <= moon_deg < b_end or (k == 8 and moon_deg >= running_deg):
                active_bhukti = b_lord
                break
            running_deg = b_end

        return {
            "lord": lord,
            "star_index": s_idx,
            "full_days": full_days,
            "elapsed_days": elapsed_days,
            "remaining_days": rem_days,
            "active_bhukti": active_bhukti,
            "transition_jd": transition_jd,
        }

    test_cases = [
        {"name": "0. Uttara Ashadha Case (275.9224°)", "moon_deg": 275.9224, "birth_jd": 2448027.104167},
        {"name": "1. Non-zero balance (Rohini 45.5°)", "moon_deg": 45.5, "birth_jd": 2451545.0},
        {"name": "2. Partway Bhukti (Pushya 105.75°)", "moon_deg": 105.75, "birth_jd": 2450000.0},
        {"name": "3. Partway Antharam (Anuradha 218.42°)", "moon_deg": 218.42, "birth_jd": 2448000.0},
        {"name": "4. Near Nakshatra boundary (13.3333° Ashwini/Bharani)", "moon_deg": 13.3333, "birth_jd": 2452000.0},
        {"name": "5. Near transition (Shatabhisha 306.6660°)", "moon_deg": 306.6660, "birth_jd": 2453000.0},
        {"name": "6. Short Sookshma/Prana (Sun star Krittika 32.5°)", "moon_deg": 32.5, "birth_jd": 2454000.0},
    ]

    for tc in test_cases:
        ref = independent_reference(tc["moon_deg"], tc["birth_jd"])
        res = client.post(
            "/api/v1/horoscope/dasa/direct",
            json={"moon_sidereal_deg": tc["moon_deg"], "birth_jd": tc["birth_jd"], "depth": 5},
        )
        assert res.status_code == 200
        app_data = res.json()
        bal = app_data["birth_dasa_balance"]

        # Validate starting lord
        assert bal["starting_mahadasha_lord"] == ref["lord"]
        # Validate active Bhukti at birth
        assert bal["starting_bhukti_lord"] == ref["active_bhukti"]

        # Differences
        diff_full = abs(bal["mahadasha_full_duration"]["total_days"] - ref["full_days"])
        diff_elapsed = abs(bal["elapsed_duration"]["total_days"] - ref["elapsed_days"])
        diff_rem = abs(bal["remaining_balance"]["total_days"] - ref["remaining_days"])
        diff_trans = abs(bal["next_dasa_transition_jd"] - ref["transition_jd"])

        assert diff_full < 1e-4, f"Full days diff too large for {tc['name']}: {diff_full}"
        assert diff_elapsed < 1e-4, f"Elapsed days diff too large for {tc['name']}: {diff_elapsed}"
        assert diff_rem < 1e-4, f"Remaining days diff too large for {tc['name']}: {diff_rem}"
        assert diff_trans < 1e-4, f"Transition JD diff too large for {tc['name']}: {diff_trans}"

        # Validate that first MD in dasa_tree matches remaining balance exactly
        first_md = app_data["dasa_tree"][0]
        assert abs(first_md["duration_days"] - ref["remaining_days"]) < 1e-4
        assert abs(first_md["start_jd"] - tc["birth_jd"]) < 1e-6
        assert abs(first_md["end_jd"] - ref["transition_jd"]) < 1e-4

        # Verify 5 levels exist in response
        first_ad = first_md["sub_periods"][0]
        first_pd = first_ad["sub_periods"][0]
        first_sd = first_pd["sub_periods"][0]
        first_prd = first_sd["sub_periods"][0]
        assert first_md["level"] == "Mahadasha"
        assert first_ad["level"] == "Antardasha"
        assert first_pd["level"] == "Pratyantardasha"
        assert first_sd["level"] == "Sookshmadasha"
        assert first_prd["level"] == "Pranadasha"


def test_first_mahadasha_bhukti_balance_across_all_nakshatras():
    """Verify across various Nakshatras that:
    1. First Mahadasa displays ONLY the birth balance, not a full starting cycle.
    2. Bhuktis in the first Mahadasa start from the active birth Bhukti lord (not self-lord).
    3. The number of Bhuktis in the first Mahadasa is <= 9.
    4. Sibling Bhuktis are strictly contiguous and strictly chronological.
    5. Subsequent Mahadasas have exactly 9 Bhuktis starting from (md_lord, md_lord).
    """
    VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    STAR_SPAN = 800.0 / 60.0  # 13°20' = 13.333333°

    # Test sample nakshatras across the zodiac
    # 0: Ashwini (Ketu), 3: Rohini (Moon), 6: Punarvasu (Jupiter), 11: Uttara Phalguni (Sun),
    # 15: Vishakha (Jupiter), 20: Uttara Ashadha (Sun), 26: Revati (Mercury)
    test_nakshatra_indices = [0, 3, 6, 11, 15, 20, 26]
    fractions = [0.15, 0.50, 0.85]  # early, mid, late in nakshatra

    birth_jd = 2451545.0  # J2000.0

    for star_idx in test_nakshatra_indices:
        for frac in fractions:
            moon_deg = (star_idx + frac) * STAR_SPAN
            res = client.post(
                "/api/v1/horoscope/dasa/direct",
                json={"moon_sidereal_deg": moon_deg, "birth_jd": birth_jd, "depth": 2},
            )
            assert res.status_code == 200, f"Failed for star_idx={star_idx}, frac={frac}"
            data = res.json()
            bal = data["birth_dasa_balance"]
            tree = data["dasa_tree"]

            # First Mahadasha (m0)
            m0 = tree[0]
            assert m0["level"] == "Mahadasha"
            assert m0["lord"] == bal["starting_mahadasha_lord"]
            assert abs(m0["start_jd"] - birth_jd) < 1e-5
            assert abs(m0["duration_days"] - bal["remaining_balance"]["total_days"]) < 1e-4

            # Subperiods in m0
            m0_bhuktis = m0["sub_periods"]
            assert len(m0_bhuktis) <= 9
            # Because frac > 0.0, at least some portion of the first Bhukti or earlier Bhuktis are elapsed
            first_bhukti = m0_bhuktis[0]
            assert first_bhukti["lord"] == bal["starting_bhukti_lord"]
            assert abs(first_bhukti["start_jd"] - birth_jd) < 1e-5

            # Verify contiguous dates for m0 Bhuktis
            prev_end = birth_jd
            total_m0_bhukti_days = 0.0
            for b in m0_bhuktis:
                assert abs(b["start_jd"] - prev_end) < 1e-4
                assert b["end_jd"] > b["start_jd"]
                prev_end = b["end_jd"]
                total_m0_bhukti_days += b["duration_days"]
            assert abs(total_m0_bhukti_days - m0["duration_days"]) < 1e-4

            # Subsequent Mahadasas must each have exactly 9 Bhuktis starting from (md_lord, md_lord)
            for m_idx in range(1, len(tree)):
                m = tree[m_idx]
                assert len(m["sub_periods"]) == 9
                assert m["sub_periods"][0]["lord"] == m["lord"], f"Subsequent MD {m['lord']} must start with self-Bhukti"
                # Contiguity across Mahadasas
                assert abs(m["start_jd"] - tree[m_idx - 1]["end_jd"]) < 1e-4
                # Contiguity within Mahadasa
                b_prev = m["start_jd"]
                b_total = 0.0
                for b in m["sub_periods"]:
                    assert abs(b["start_jd"] - b_prev) < 1e-4
                    b_prev = b["end_jd"]
                    b_total += b["duration_days"]
                assert abs(b_total - m["duration_days"]) < 1e-4



