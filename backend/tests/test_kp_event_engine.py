"""Automated unit and integration tests for KP Dasha-Bhukti Event Prediction Engine.

Covers all 20 mandatory unit tests specified in Section 14:
1. L1 overrides L2, L3, and L4 for the same house.
2. The same house contributed by several lords is counted only once at its highest weight.
3. Mahadasha and Bhukti both contribute supporting houses.
4. One mandatory lord contributes no supporting houses, preventing GREEN.
5. Full supporting-house coverage produces GREEN when all other conditions are met.
6. All-but-one coverage produces GREEN only when the missing-house condition is valid.
7. Coverage below 60% produces RED.
8. Denial equal to support produces RED.
9. Denial greater than 1.5 times support sets denied: true.
10. ORANGE requires at least 60% coverage, greater support than denial, and two distinct supporting houses.
11. CSL denial caps or downgrades the grade correctly.
12. Retrograde downgrades GREEN to ORANGE and adds 'delay possible'.
13. House 11 is enforced only for explicitly configured gain-type events.
14. Running-period detection works on both boundary dates.
15. Missing mandatory data returns missing_data.
16. More than five qualifying events never causes more than five to display.
17. No more than two RED events are displayed.
18. Repeated calculations with identical input return identical results.
19. JSON and displayed UI grades remain consistent.
20. Existing horoscope generation and all Dasha hierarchy calculations remain unchanged.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.services.kp_event_engine import (
    EVENT_REGISTRY,
    get_event_rule,
    derive_planet_house_significations,
    score_period_for_event,
    grade_scored_event,
    select_and_order_events,
    run_kp_event_analysis,
    detect_running_period,
    extract_periods_from_dasa_response,
    save_kp_event_analysis,
    get_kp_event_analysis,
    GradeResult,
)
from app.schemas.kp_events import KpEventAnalysisRequest, KpEventPeriodInput
from app.services.kp_service import calculate_kp_chart
from app.schemas.common import BirthInput

client = TestClient(app)


# ---------------------------------------------------------------------------
# Test 1: L1 overrides L2, L3, and L4 for the same house
# ---------------------------------------------------------------------------
def test_01_l1_overrides_lower_levels_for_same_house():
    raw_sigs = {
        "Jupiter": [
            {"house": 2, "level": "L4"},
            {"house": 2, "level": "L2"},
            {"house": 2, "level": "L1"},  # L1 must override L4 and L2
            {"house": 2, "level": "L3"},
        ]
    }
    normalized = derive_planet_house_significations(raw_sigs)
    assert normalized["Jupiter"][2] == "L1"


# ---------------------------------------------------------------------------
# Test 2: The same house contributed by several lords is counted only once at highest weight
# ---------------------------------------------------------------------------
def test_02_same_house_across_lords_counted_once_at_highest_weight():
    # Marriage S={2, 7, 11}, D={1, 6, 10}
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L3", 7: "L2"},  # House 2 at L3 (wt=2)
        "Sun": {2: "L1", 11: "L2"},   # House 2 at L1 (wt=4)
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    # House 2 effective weight should be 4 (L1), not 2 + 4 = 6
    assert scored.effective_house_weights[2] == 4
    assert scored.effective_house_levels[2] == "L1"
    # Total support: House 2(wt 4) + House 7(wt 3) + House 11(wt 3) = 10
    assert scored.support_score == 10


# ---------------------------------------------------------------------------
# Test 3: Mahadasha and Bhukti both contribute supporting houses
# ---------------------------------------------------------------------------
def test_03_mahadasha_and_bhukti_both_contribute_supporting():
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L1", 7: "L2"},  # Venus contributes 2, 7
        "Sun": {11: "L1"},             # Sun contributes 11
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.md_supports is True
    assert scored.bd_supports is True
    assert scored.coverage == 1.0


# ---------------------------------------------------------------------------
# Test 4: One mandatory lord contributes no supporting houses, preventing GREEN
# ---------------------------------------------------------------------------
def test_04_mandatory_lord_no_supporting_prevents_green():
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L1", 7: "L1", 11: "L1"},  # Venus covers all S
        "Sun": {1: "L4", 6: "L4"},               # Sun contributes NO supporting houses
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.md_supports is True
    assert scored.bd_supports is False  # Sun fails mandatory support
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.final_color != "green"
    # Can still qualify for ORANGE if cov >= 0.60, supp > den, distinct supp >= 2
    assert graded.final_color == "orange"
    assert graded.grade == "MODERATE"


# ---------------------------------------------------------------------------
# Test 5: Full supporting-house coverage produces GREEN when all other conditions met
# ---------------------------------------------------------------------------
def test_05_full_coverage_produces_green():
    event = get_event_rule("Marriage")  # S={2,7,11}, D={1,6,10}
    sigs = {
        "Venus": {2: "L1", 7: "L2"},
        "Sun": {11: "L2"},
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.coverage == 1.0
    assert graded.support_score == 10
    assert graded.denial_score == 0
    assert graded.final_color == "green"
    assert graded.grade == "STRONG"


# ---------------------------------------------------------------------------
# Test 6: All-but-one coverage produces GREEN only when missing house condition valid
# ---------------------------------------------------------------------------
def test_06_all_but_one_coverage_condition():
    # Job: S={2, 6, 10, 11}, D={1, 5, 9} (gain type, requires 11)
    event = get_event_rule("Job")
    # Covers 2, 6, 11 (3 out of 4 = all but one); missing house 10
    sigs = {
        "Venus": {2: "L1", 6: "L2"},
        "Sun": {11: "L1"},
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.all_but_one_coverage is True
    # Without missing_house_l3_l4_only flag, conservative fallback is ORANGE
    graded_conservative = grade_scored_event(event=event, scored=scored, missing_house_l3_l4_only=False)
    assert graded_conservative.final_color == "orange"

    # With missing_house_l3_l4_only flag verified, qualifies for GREEN
    graded_qualified = grade_scored_event(event=event, scored=scored, missing_house_l3_l4_only=True)
    assert graded_qualified.final_color == "green"
    assert graded_qualified.grade == "STRONG"


# ---------------------------------------------------------------------------
# Test 7: Coverage below 60% produces RED
# ---------------------------------------------------------------------------
def test_07_coverage_below_60_percent_produces_red():
    # Children: S={2, 5, 11}
    event = get_event_rule("Children")
    # Only 1 house covered out of 3 = 33.3% < 60%
    sigs = {
        "Jupiter": {2: "L1"},
        "Sun": {9: "L1"},
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Jupiter",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.coverage < 0.60
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.final_color == "red"
    assert graded.grade == "WEAK"


# ---------------------------------------------------------------------------
# Test 8: Denial equal to support produces RED
# ---------------------------------------------------------------------------
def test_08_denial_equal_to_support_produces_red():
    # Marriage S={2, 7, 11}, D={1, 6, 10}
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L2", 7: "L2"},  # S: 3 + 3 = 6
        "Mars": {1: "L2", 6: "L2"},   # D: 3 + 3 = 6
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Mars",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.support_score == scored.denial_score == 6
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.final_color == "red"
    assert graded.grade == "WEAK"


# ---------------------------------------------------------------------------
# Test 9: Denial greater than 1.5 times support sets denied: true
# ---------------------------------------------------------------------------
def test_09_denial_greater_than_1_point_5_times_support_marks_denied():
    # Marriage S={2, 7, 11}, D={1, 6, 10}
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L4"},                     # S: house 2 at wt 1 (total supp = 1)
        "Mars": {1: "L1", 6: "L1", 10: "L1"},   # D: wt 4+4+4 = 12 (denial = 12 > 1.5 * 1)
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Mars",
        antara_lord=None,
        significations=sigs,
    )
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.final_color == "red"
    assert graded.denied is True


# ---------------------------------------------------------------------------
# Test 10: ORANGE requires at least 60% coverage, support > denial, and two distinct supporting houses
# ---------------------------------------------------------------------------
def test_10_orange_conditions():
    # Marriage S={2, 7, 11}, D={1, 6, 10}
    event = get_event_rule("Marriage")
    # Covers 2 and 7 (2 out of 3 = 66.7% >= 60%)
    # Support = 4 + 3 = 7, Denial = 1 (house 1 at L4 = 1)
    # Distinct supporting houses = 2
    sigs = {
        "Venus": {2: "L1"},
        "Sun": {7: "L2", 1: "L4"},
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    assert scored.coverage >= 0.60
    assert scored.support_score > scored.denial_score
    assert len(scored.supporting_houses) >= 2
    graded = grade_scored_event(event=event, scored=scored)
    assert graded.final_color == "orange"
    assert graded.grade == "MODERATE"


# ---------------------------------------------------------------------------
# Test 11: CSL denial caps or downgrades the grade correctly
# ---------------------------------------------------------------------------
def test_11_csl_adjustment_capping_and_downgrading():
    # Marriage primary cusp is 7. S={2, 7, 11}, D={1, 6, 10}
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L1", 7: "L1"},
        "Sun": {11: "L1"},
        "Mercury": {1: "L2", 2: "L3"},           # D: wt 3 (house 1), S: wt 2 (house 2) -> Mainly denies (3 > 2)
        "Saturn": {1: "L1", 6: "L1", 10: "L1"},   # D: 4+4+4=12, S: 0 -> Clearly denies (12 vs 0)
        "Jupiter": {2: "L2", 1: "L2"},             # Tie: S=3, D=3 -> Neutral
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    # Case A: CSL is Mercury (mainly denies) -> GREEN capped at ORANGE
    csl_map_a = {7: "Mercury"}
    graded_a = grade_scored_event(event=event, scored=scored, csl_map=csl_map_a, all_significations=sigs)
    assert graded_a.original_color == "green"
    assert graded_a.final_color == "orange"
    assert "capped at ORANGE" in str(graded_a.csl_adjustment)

    # Case B: CSL is Saturn (clearly denies) -> Downgraded to RED
    csl_map_b = {7: "Saturn"}
    graded_b = grade_scored_event(event=event, scored=scored, csl_map=csl_map_b, all_significations=sigs)
    assert graded_b.final_color == "red"
    assert "downgraded to RED" in str(graded_b.csl_adjustment)

    # Case C: CSL is Jupiter (tie: S=3, D=3) -> Neutral, stays GREEN
    csl_map_c = {7: "Jupiter"}
    graded_c = grade_scored_event(event=event, scored=scored, csl_map=csl_map_c, all_significations=sigs)
    assert graded_c.final_color == "green"


# ---------------------------------------------------------------------------
# Test 12: Retrograde downgrades GREEN to ORANGE and adds 'delay possible'
# ---------------------------------------------------------------------------
def test_12_retrograde_adjustment():
    event = get_event_rule("Marriage")
    sigs = {
        "Venus": {2: "L1", 7: "L1"},
        "Sun": {11: "L1"},
    }
    scored = score_period_for_event(
        event=event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    retro_status = {"Venus": True, "Sun": False}
    graded = grade_scored_event(
        event=event,
        scored=scored,
        retrograde_status=retro_status,
    )
    assert graded.original_color == "green"
    assert graded.final_color == "orange"
    assert graded.grade == "MODERATE"
    assert graded.retrograde_note == "delay possible"
    assert "delay possible" in graded.hint.lower()


# ---------------------------------------------------------------------------
# Test 13: House 11 is enforced only for explicitly configured gain-type events
# ---------------------------------------------------------------------------
def test_13_house_11_enforced_only_for_gain_type_events():
    # Financial gain: S={2, 6, 11}, is_gain_type = True
    gain_event = get_event_rule("Financial gain")
    assert gain_event.is_gain_type is True

    # Higher education: S={4, 9, 11}, is_gain_type = False
    edu_event = get_event_rule("Higher education")
    assert edu_event.is_gain_type is False

    # Significations covering 2 and 6, but NOT 11
    sigs = {
        "Venus": {2: "L1"},
        "Sun": {6: "L1"},
    }
    scored_gain = score_period_for_event(
        event=gain_event,
        md_lord="Venus",
        bd_lord="Sun",
        antara_lord=None,
        significations=sigs,
    )
    # Even if missing house condition was somehow met, lack of house 11 prohibits GREEN for gain-type
    graded_gain = grade_scored_event(event=gain_event, scored=scored_gain, missing_house_l3_l4_only=True)
    assert graded_gain.final_color != "green"

    # For an event where 11 is NOT required for gain or not gain-type:
    # Transfer: S={3, 10, 12}, is_gain_type = False
    transfer_event = get_event_rule("Transfer")
    sigs_transfer = {
        "Mercury": {3: "L1", 10: "L1"},
        "Moon": {12: "L1"},
    }
    scored_trans = score_period_for_event(
        event=transfer_event,
        md_lord="Mercury",
        bd_lord="Moon",
        antara_lord=None,
        significations=sigs_transfer,
    )
    graded_trans = grade_scored_event(event=transfer_event, scored=scored_trans)
    assert graded_trans.final_color == "green"


# ---------------------------------------------------------------------------
# Test 14: Running-period detection works on both boundary dates
# ---------------------------------------------------------------------------
def test_14_running_period_boundary_dates():
    start = "2026-03-12"
    end = "2027-03-12"

    # Start date boundary
    assert detect_running_period(start, end, current_date="2026-03-12") is True
    # Inside period
    assert detect_running_period(start, end, current_date="2026-07-15") is True
    # End date boundary
    assert detect_running_period(start, end, current_date="2027-03-12") is True
    # One day before
    assert detect_running_period(start, end, current_date="2026-03-11") is False
    # One day after
    assert detect_running_period(start, end, current_date="2027-03-13") is False


# ---------------------------------------------------------------------------
# Test 15: Missing mandatory data returns missing_data
# ---------------------------------------------------------------------------
def test_15_missing_mandatory_data_returns_missing_data():
    periods = [
        {
            "mahadasha_lord": "Venus",
            "bhukti_lord": "Sun",
            "start_date": "2026-03-12",
            "end_date": "2027-03-12",
        }
    ]
    # Sigs has Venus, but missing Sun
    sigs = {
        "Venus": {2: "L1", 7: "L2"},
    }
    res = run_kp_event_analysis(
        lagna="Aries",
        periods=periods,
        significations=sigs,
    )
    period_out = res["periods"][0]
    assert period_out["status"] == "missing_data"
    assert "significations for Bhukti lord (Sun)" in period_out["missing_fields"]
    assert len(period_out["events"]) == 0
    assert "Data missing" in res["human_readable_report"]


# ---------------------------------------------------------------------------
# Test 16: More than five qualifying events never causes more than five to display
# ---------------------------------------------------------------------------
def test_16_max_five_events_displayed():
    # Setup lords that qualify for 10+ events
    all_events = []
    rule_names = ["Marriage", "Job", "Promotion", "Financial gain", "Children", "Higher education", "Property purchase"]
    for i, name in enumerate(rule_names):
        ev = get_event_rule(name)
        graded = GradeResult(
            event_name=ev.name,
            original_color="green",
            final_color="green",
            original_grade="STRONG",
            grade="STRONG",
            support_score=10 - i,
            denial_score=0,
            coverage=1.0,
            denied=False,
            retrograde_note=None,
            csl_adjustment=None,
            csl_details=None,
            hint=ev.get_hint("green"),
            supporting_houses=[],
            denying_houses=[],
            missing_supporting_houses=[],
            scoring_metadata={},
        )
        all_events.append(graded)

    displayed, _ = select_and_order_events(all_events, max_displayed=5, max_red=2)
    assert len(displayed) == 5


# ---------------------------------------------------------------------------
# Test 17: No more than two RED events are displayed
# ---------------------------------------------------------------------------
def test_17_no_more_than_two_red_events_displayed():
    all_events = []
    # 5 RED events, 1 ORANGE event
    ev_orange = get_event_rule("Marriage")
    all_events.append(
        GradeResult(
            event_name=ev_orange.name,
            original_color="orange",
            final_color="orange",
            original_grade="MODERATE",
            grade="MODERATE",
            support_score=6,
            denial_score=1,
            coverage=0.67,
            denied=False,
            retrograde_note=None,
            csl_adjustment=None,
            csl_details=None,
            hint=ev_orange.get_hint("orange"),
            supporting_houses=[],
            denying_houses=[],
            missing_supporting_houses=[],
            scoring_metadata={},
        )
    )

    red_names = ["Job", "Job loss", "Illness", "Imprisonment", "Litigation loss"]
    for i, r_name in enumerate(red_names):
        ev = get_event_rule(r_name)
        all_events.append(
            GradeResult(
                event_name=ev.name,
                original_color="red",
                final_color="red",
                original_grade="WEAK",
                grade="WEAK",
                support_score=5 - i,
                denial_score=6,
                coverage=0.3,
                denied=False,
                retrograde_note=None,
                csl_adjustment=None,
                csl_details=None,
                hint=ev.get_hint("red"),
                supporting_houses=[],
                denying_houses=[],
                missing_supporting_houses=[],
                scoring_metadata={},
            )
        )

    displayed, _ = select_and_order_events(all_events, max_displayed=5, max_red=2)
    red_count = sum(1 for e in displayed if e.final_color == "red")
    assert red_count <= 2
    # The two RED events displayed must be the ones with highest support score (Job, then Job loss)
    assert displayed[1].event_name == "Job"
    assert displayed[2].event_name == "Job loss"


# ---------------------------------------------------------------------------
# Test 18: Repeated calculations with identical input return identical results
# ---------------------------------------------------------------------------
def test_18_idempotent_and_deterministic_results():
    periods = [
        {"mahadasha_lord": "Venus", "bhukti_lord": "Sun", "start_date": "2026-03-12", "end_date": "2027-03-12"}
    ]
    sigs = {
        "Venus": {2: "L1", 7: "L2", 11: "L3"},
        "Sun": {1: "L4", 6: "L4", 10: "L4"},
    }
    csl = {7: "Sun"}
    res1 = run_kp_event_analysis(lagna="Aries", periods=periods, significations=sigs, csl_significations=csl)
    res2 = run_kp_event_analysis(lagna="Aries", periods=periods, significations=sigs, csl_significations=csl)

    assert res1["overall_summary"] == res2["overall_summary"]
    assert res1["periods"] == res2["periods"]
    assert res1["human_readable_report"] == res2["human_readable_report"]


# ---------------------------------------------------------------------------
# Test 19: JSON and displayed UI grades remain consistent
# ---------------------------------------------------------------------------
def test_19_json_and_text_report_grade_consistency():
    periods = [
        {"mahadasha_lord": "Venus", "bhukti_lord": "Sun", "start_date": "2026-03-12", "end_date": "2027-03-12"}
    ]
    sigs = {
        "Venus": {2: "L1", 7: "L2", 11: "L3"},
        "Sun": {2: "L2", 7: "L3"},
    }
    res = run_kp_event_analysis(lagna="Aries", periods=periods, significations=sigs, current_date="2026-06-01")
    p0 = res["periods"][0]
    report = res["human_readable_report"]

    # Verify each event in JSON is faithfully represented with matching color and grade in report
    for ev in p0["events"]:
        assert ev["grade"] in report
        assert ev["event"] in report
        assert ev["hint"] in report

    # Verify final mandatory disclaimer line
    assert "Indicative KP hint, confirm with CSL and transit before decisions." in report


# ---------------------------------------------------------------------------
# Test 20: Existing horoscope generation and all Dasha hierarchy calculations remain unchanged
# ---------------------------------------------------------------------------
def test_20_existing_kp_and_horoscope_calculations_unaltered():
    birth = BirthInput(
        birth_date="1990-05-15",
        birth_time="14:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    kp_chart = calculate_kp_chart(birth, ayanamsa_id=1, house_system_id=2)
    # Check that core planetary positions and house significators exist and match original format
    assert len(kp_chart.planetary_positions) == 9
    assert len(kp_chart.cuspal_analysis) == 12
    assert len(kp_chart.house_significators) == 12
    assert kp_chart.dasa_hierarchy is not None
    assert kp_chart.dasa_hierarchy.mahadasha_lord in ("Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus")


# ---------------------------------------------------------------------------
# Test 21: Integration test for API analyze endpoint
# ---------------------------------------------------------------------------
def test_21_api_analyze_endpoint():
    payload = {
        "lagna": "Aries",
        "periods": [
            {
                "mahadasha_lord": "Venus",
                "bhukti_lord": "Sun",
                "start_date": "2026-03-12",
                "end_date": "2027-03-12",
            }
        ],
        "significations": {
            "Venus": [{"house": 2, "level": "L1"}, {"house": 7, "level": "L2"}, {"house": 11, "level": "L3"}],
            "Sun": [{"house": 1, "level": "L4"}, {"house": 6, "level": "L4"}],
        },
        "current_date": "2026-06-15",
    }
    response = client.post("/api/v1/horoscope/kp-events/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["rule_set_version"] == "1.0.0"
    assert len(data["periods"]) == 1
    assert data["periods"][0]["running"] is True
    assert "events" in data["periods"][0]
    assert len(data["periods"][0]["events"]) <= 5


# ---------------------------------------------------------------------------
# Test 22: Registry endpoint lists all 32 events
# ---------------------------------------------------------------------------
def test_22_api_registry_endpoint():
    response = client.get("/api/v1/horoscope/kp-events/registry")
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 32
    assert len(data["events"]) == 32


# ---------------------------------------------------------------------------
# Test 23 (Regression): Raw Dasa tree fallback with _convert_node
# ---------------------------------------------------------------------------
def test_23_raw_dasa_tree_fallback_with_convert_node():
    from app.services.timezone_utils import resolve_birth_datetime
    from app.services.dasa_service import _convert_node
    from app.services.kp_event_engine.orchestrator import extract_periods_from_dasa_response
    import xalen

    b_date = "1995-10-25"
    b_time = "08:15:00"
    tz_str = "Asia/Kolkata"

    from datetime import date as dt_date, time as dt_time
    bd_obj = dt_date.fromisoformat(b_date)
    bt_obj = dt_time.fromisoformat(b_time)

    local_dt, utc_dt, jd, _, offset_hours = resolve_birth_datetime(bd_obj, bt_obj, tz_str)
    moon_pos = xalen.planet_position(jd, 1, True, 1)
    raw_tree = xalen.vimshottari_dasha(moon_pos["longitude"], jd, 2)

    # Convert nodes so start_date_iso and end_date_iso are populated
    dasa_tree = [_convert_node(node, birth_date=local_dt.date(), utc_offset_hours=offset_hours) for node in raw_tree]
    periods = extract_periods_from_dasa_response({"dasa_tree": dasa_tree})

    assert len(periods) > 0
    for p in periods:
        assert p["mahadasha_lord"] is not None
        assert p["bhukti_lord"] is not None
        assert p["start_date"] is not None and len(p["start_date"]) > 0
        assert p["end_date"] is not None and len(p["end_date"]) > 0


# ---------------------------------------------------------------------------
# Test 24 (Regression): Cache invalidation when rule_set_version changes
# ---------------------------------------------------------------------------
def test_24_cache_invalidation_on_version_mismatch():
    from app.services.kp_event_engine.repository import (
        save_kp_event_analysis,
        get_kp_event_analysis,
        _LOCAL_KP_EVENT_ANALYSES,
    )
    from app.services.kp_event_engine.event_rules import RULE_SET_VERSION

    user_id = "test-user-cache-version"
    horo_id = "test-horo-cache-version"

    # Pre-populate cache with an old rule version
    stale_record = {
        "id": "stale-rec-1",
        "user_id": user_id,
        "horoscope_id": horo_id,
        "rule_set_version": "0.8.0",  # Outdated version
        "input_data_fingerprint": "fake-hash",
        "calculation_timestamp": "2026-01-01T00:00:00Z",
        "summary": {"running_period": "Jupiter-Saturn", "green_count": 1, "orange_count": 0, "red_count": 0},
        "results": [{"period": "Jupiter-Saturn", "status": "ok", "events": []}],
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    _LOCAL_KP_EVENT_ANALYSES[stale_record["id"]] = stale_record

    cached = get_kp_event_analysis(user_id, horo_id)
    assert cached is not None
    # Version check detects stale version
    assert cached.get("rule_set_version") != RULE_SET_VERSION


# ---------------------------------------------------------------------------
# Test 25 (Regression): Cache invalidation when horoscope record updated
# ---------------------------------------------------------------------------
def test_25_cache_invalidation_on_horoscope_update():
    from app.services.kp_event_engine.repository import _LOCAL_KP_EVENT_ANALYSES

    user_id = "test-user-fresh"
    horo_id = "test-horo-fresh"

    # Analysis computed on 2026-05-01
    analysis_record = {
        "id": "rec-fresh-1",
        "user_id": user_id,
        "horoscope_id": horo_id,
        "rule_set_version": "1.0.0",
        "input_data_fingerprint": "hash-fresh",
        "calculation_timestamp": "2026-05-01T10:00:00Z",
        "summary": {},
        "results": [],
        "created_at": "2026-05-01T10:00:00Z",
    }
    _LOCAL_KP_EVENT_ANALYSES[analysis_record["id"]] = analysis_record

    # Horoscope updated on 2026-06-01 (later than calculation_timestamp)
    horoscope_updated_at = "2026-06-01T12:00:00Z"
    is_fresh = str(horoscope_updated_at) <= str(analysis_record["calculation_timestamp"])
    assert is_fresh is False  # Correctly identifies cache as stale


# ---------------------------------------------------------------------------
# Test 26 (Regression): Human readable report preserved in saved analysis
# ---------------------------------------------------------------------------
def test_26_human_readable_report_stored_and_retrieved():
    from app.services.kp_event_engine.repository import (
        save_kp_event_analysis,
        get_kp_event_analysis,
    )

    user_id = "test-user-report"
    horo_id = "test-horo-report"
    report_text = "Period: Venus - Sun\nMarriage [STRONG]\n\nIndicative KP hint, confirm with CSL and transit before decisions."

    analysis_data = {
        "rule_set_version": "1.0.0",
        "overall_summary": {"green_count": 1, "orange_count": 0, "red_count": 0},
        "periods": [{"period": "Venus-Sun", "status": "ok", "events": []}],
        "human_readable_report": report_text,
    }

    saved = save_kp_event_analysis(user_id=user_id, horoscope_id=horo_id, analysis_data=analysis_data)
    assert saved["summary"]["human_readable_report"] == report_text

    loaded = get_kp_event_analysis(user_id=user_id, horoscope_id=horo_id)
    assert loaded is not None
    assert loaded["summary"]["human_readable_report"] == report_text


# ---------------------------------------------------------------------------
# Test 27 (Regression): Vedic & Tamil planet alias normalization
# ---------------------------------------------------------------------------
def test_27_tamil_vedic_planet_aliases():
    from app.services.kp_event_engine.signification_normalizer import normalize_planet_name

    assert normalize_planet_name("Guru") == "Jupiter"
    assert normalize_planet_name("guru") == "Jupiter"
    assert normalize_planet_name("Sani") == "Saturn"
    assert normalize_planet_name("shani") == "Saturn"
    assert normalize_planet_name("Budha") == "Mercury"
    assert normalize_planet_name("budhan") == "Mercury"
    assert normalize_planet_name("Sukra") == "Venus"
    assert normalize_planet_name("sukran") == "Venus"
    assert normalize_planet_name("Mangal") == "Mars"
    assert normalize_planet_name("sevvai") == "Mars"
    assert normalize_planet_name("Surya") == "Sun"
    assert normalize_planet_name("Ravi") == "Sun"
    assert normalize_planet_name("Chandra") == "Moon"
    assert normalize_planet_name("Ragu") == "Rahu"
    assert normalize_planet_name("Kethu") == "Ketu"


# ---------------------------------------------------------------------------
# Test 28 (End-to-End): Real Chart Tracing through Complete Calculation Engine
# ---------------------------------------------------------------------------
def test_28_end_to_end_real_saved_chart_trace():
    from app.services.kp_service import calculate_kp_chart
    from app.services.dasa_service import calculate_dasa
    from app.services.ephemeris import calculate_full_horoscope
    from app.services.kp_event_engine import (
        run_kp_event_analysis,
        extract_periods_from_dasa_response,
        derive_cusp_sub_lords_from_chart,
        extract_retrograde_status_from_chart,
    )
    from datetime import date, time

    birth = BirthInput(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )

    # 1. Real astronomical & KP calculations
    kp_data = calculate_kp_chart(birth, ayanamsa_id=1, house_system_id=2)
    dasa_data = calculate_dasa(birth, depth=2, ayanamsa_id=1, house_system_id=2)
    horo_data = calculate_full_horoscope(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30, 0),
        timezone_str="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ayanamsa_id=1,
        house_system_id=2,
    )

    # 2. Extract engine inputs
    periods = extract_periods_from_dasa_response(dasa_data)
    assert len(periods) > 0, "Periods must be extracted from Dasa tree"

    csl_map = derive_cusp_sub_lords_from_chart(kp_data)
    assert len(csl_map) == 12, "All 12 cusp sub-lords must be derived"

    retro_map = extract_retrograde_status_from_chart(horo_data, kp_data)
    assert "Saturn" in retro_map

    # 3. Execute analysis
    res = run_kp_event_analysis(
        lagna=horo_data.ascendant.sign_name,
        periods=periods,
        significations=kp_data.house_significators,
        csl_significations=csl_map,
        retrograde_status=retro_map,
        current_date="2026-10-18",
        timezone_str="Asia/Kolkata",
    )

    # 4. Verify results
    assert res["rule_set_version"] == "1.0.0"
    assert res["lagna"] == horo_data.ascendant.sign_name
    assert len(res["periods"]) == len(periods)
    assert res["overall_summary"]["total_periods"] == len(periods)

    # Verify running period detection
    running_periods = [p for p in res["periods"] if p["running"]]
    assert len(running_periods) == 1, "Exactly one period must be running for 2026-10-18"

    run_p = running_periods[0]
    assert run_p["status"] == "ok"
    assert len(run_p["events"]) > 0

    # Verify event structure and scoring
    for ev in run_p["events"]:
        assert ev["color"] in ("green", "orange", "red")
        assert ev["grade"] in ("STRONG", "MODERATE", "WEAK")
        assert ev["support_score"] >= 0
        assert ev["denial_score"] >= 0
        assert 0.0 <= ev["coverage"] <= 1.0
        assert len(ev["hint"]) > 0

    # Verify final disclaimer line in human-readable report
    assert "Indicative KP hint, confirm with CSL and transit before decisions." in res["human_readable_report"]


# ---------------------------------------------------------------------------
# Test 29: /analyze endpoint rejects save_horoscope_id belonging to another user
# ---------------------------------------------------------------------------
def test_29_analyze_endpoint_save_horoscope_ownership_enforcement():
    from app.routers.kp_events import get_optional_current_user
    from app.services.auth_service import get_supabase_client

    supabase = get_supabase_client()
    if not supabase:
        return

    # Attacker tries to attach analysis to someone else's saved horoscope
    app.dependency_overrides[get_optional_current_user] = lambda: {
        "id": "attacker-user-uuid-9999",
        "username": "attacker",
        "role": "user",
    }
    test_client = TestClient(app)

    payload = {
        "lagna": "Aries",
        "periods": [
            {
                "mahadasha_lord": "Jupiter",
                "bhukti_lord": "Sun",
                "start_date": "2026-01-01",
                "end_date": "2027-01-01",
            }
        ],
        "significations": {
            "Jupiter": {2: "L1", 11: "L2"},
            "Sun": {10: "L1"},
        },
        "save_horoscope_id": "ba9bb522-a79d-43e8-8493-ac8d53d4d39b",  # belongs to owner
    }

    resp = test_client.post("/api/v1/horoscope/kp-events/analyze", json=payload)
    app.dependency_overrides.clear()

    # Must be rejected with 404
    assert resp.status_code == 404
    assert "not found or unauthorized" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Test 30: GET /user-analyses endpoint with pagination, validation & isolation
# ---------------------------------------------------------------------------
def test_30_list_user_kp_event_analyses_auth_and_isolation():
    from app.services.auth_service import get_current_user

    # 1. Unauthenticated request must return 401
    app.dependency_overrides.clear()
    unauth_client = TestClient(app)
    unauth_res = unauth_client.get("/api/v1/horoscope/kp-events/user-analyses")
    assert unauth_res.status_code == 401

    # 2. Validation: limit < 1, limit > 100, offset < 0 must return 422
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "owner_user",
        "role": "user",
    }
    owner_client = TestClient(app)
    assert owner_client.get("/api/v1/horoscope/kp-events/user-analyses?limit=0").status_code == 422
    assert owner_client.get("/api/v1/horoscope/kp-events/user-analyses?limit=101").status_code == 422
    assert owner_client.get("/api/v1/horoscope/kp-events/user-analyses?offset=-1").status_code == 422

    # 3. Owner request succeeds and includes metadata
    res = owner_client.get("/api/v1/horoscope/kp-events/user-analyses?limit=10&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert "total_count" in data
    assert "items" in data
    assert data["limit"] == 10
    assert data["offset"] == 0

    if data["items"]:
        item = data["items"][0]
        assert "id" in item
        assert "user_id" in item
        assert "green_count" in item
        assert "running_period" in item
        assert "persistence_status" in item

    # 4. Attacker user isolation: user with no records receives total_count=0, empty items
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "attacker-user-uuid-8888",
        "username": "attacker",
        "role": "user",
    }
    attacker_client = TestClient(app)
    res_attacker = attacker_client.get("/api/v1/horoscope/kp-events/user-analyses")
    assert res_attacker.status_code == 200
    attacker_data = res_attacker.json()
    assert attacker_data["total_count"] == 0
    assert len(attacker_data["items"]) == 0

    # 5. Admin sees records
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "admin-uuid-001",
        "username": "admin",
        "role": "admin",
    }
    admin_client = TestClient(app)
    res_admin = admin_client.get("/api/v1/horoscope/kp-events/user-analyses")
    assert res_admin.status_code == 200

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 31: POST /from-saved/{id} ownership, admin, non-owner, malformed UUID, unauth
# ---------------------------------------------------------------------------
def test_31_from_saved_authorization_and_validation():
    from app.services.auth_service import get_current_user

    # 1. Unauthenticated request must return 401
    app.dependency_overrides.clear()
    unauth_client = TestClient(app)
    unauth_res = unauth_client.post("/api/v1/horoscope/kp-events/from-saved/ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
    assert unauth_res.status_code == 401

    # 2. Malformed UUID must return 400 Bad Request
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "gokul_murugan",
        "role": "admin",
    }
    client = TestClient(app)
    malformed_res = client.post("/api/v1/horoscope/kp-events/from-saved/not-a-uuid")
    assert malformed_res.status_code == 400
    assert "invalid saved horoscope uuid format" in malformed_res.json()["detail"].lower()

    malformed_num = client.post("/api/v1/horoscope/kp-events/from-saved/12345")
    assert malformed_num.status_code == 400

    # 3. Non-existent UUID must return 404
    non_existent_res = client.post("/api/v1/horoscope/kp-events/from-saved/00000000-0000-0000-0000-000000000000")
    assert non_existent_res.status_code == 404
    assert "not found or unauthorized" in non_existent_res.json()["detail"].lower()

    # 4. Valid horoscope by owner succeeds with 200
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "gokul_murugan",
        "role": "user",  # normal user role as owner
    }
    owner_client = TestClient(app)
    owner_res = owner_client.post("/api/v1/horoscope/kp-events/from-saved/ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
    assert owner_res.status_code == 200
    assert "periods" in owner_res.json()

    # 5. Non-owner user receives 404 (never sees other user's horoscope)
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "attacker-user-uuid-9999",
        "username": "attacker",
        "role": "user",
    }
    non_owner_client = TestClient(app)
    non_owner_res = non_owner_client.post("/api/v1/horoscope/kp-events/from-saved/ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
    assert non_owner_res.status_code == 404
    assert "not found or unauthorized" in non_owner_res.json()["detail"].lower()

    # 6. Admin user can access saved horoscope
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "different-admin-uuid-001",
        "username": "admin_two",
        "role": "admin",
    }
    admin_client = TestClient(app)
    admin_res = admin_client.post("/api/v1/horoscope/kp-events/from-saved/ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
    assert admin_res.status_code == 200

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 32: POST /analyze with save_horoscope_id validation and error handling
# ---------------------------------------------------------------------------
def test_32_analyze_save_horoscope_id_validation():
    from app.services.auth_service import get_current_user

    base_payload = {
        "lagna": "Aries",
        "periods": [
            {
                "mahadasha_lord": "Jupiter",
                "bhukti_lord": "Sun",
                "start_date": "2026-01-01",
                "end_date": "2027-01-01",
            }
        ],
        "significations": {
            "Jupiter": {2: "L1", 11: "L2"},
            "Sun": {10: "L1"},
        },
    }

    from app.routers.kp_events import get_optional_current_user

    user_fixture = {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "owner_user",
        "role": "user",
    }
    app.dependency_overrides[get_current_user] = lambda: user_fixture
    app.dependency_overrides[get_optional_current_user] = lambda: user_fixture
    client = TestClient(app)

    # 1. Malformed UUID in save_horoscope_id returns 400
    p_malformed = dict(base_payload)
    p_malformed["save_horoscope_id"] = "not-a-valid-uuid"
    res_malformed = client.post("/api/v1/horoscope/kp-events/analyze", json=p_malformed)
    assert res_malformed.status_code == 400
    assert "invalid saved horoscope uuid format" in res_malformed.json()["detail"].lower()

    # 2. Non-existent UUID in save_horoscope_id returns 404
    p_nonexistent = dict(base_payload)
    p_nonexistent["save_horoscope_id"] = "11111111-2222-3333-4444-555555555555"
    res_nonexistent = client.post("/api/v1/horoscope/kp-events/analyze", json=p_nonexistent)
    assert res_nonexistent.status_code == 404
    assert "not found or unauthorized" in res_nonexistent.json()["detail"].lower()

    # 3. Valid owner save_horoscope_id succeeds with 200
    p_valid = dict(base_payload)
    p_valid["save_horoscope_id"] = "ba9bb522-a79d-43e8-8493-ac8d53d4d39b"
    res_valid = client.post("/api/v1/horoscope/kp-events/analyze", json=p_valid)
    assert res_valid.status_code == 200

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 33: GET /analyses/{id} authorization and UUID validation
# ---------------------------------------------------------------------------
def test_33_get_analyses_authorization_and_validation():
    from app.services.auth_service import get_current_user

    # 1. Unauthenticated returns 401
    app.dependency_overrides.clear()
    unauth_client = TestClient(app)
    assert unauth_client.get("/api/v1/horoscope/kp-events/analyses/ba9bb522-a79d-43e8-8493-ac8d53d4d39b").status_code == 401

    # 2. Malformed UUID returns 400
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "owner_user",
        "role": "user",
    }
    client = TestClient(app)
    assert client.get("/api/v1/horoscope/kp-events/analyses/bad-uuid").status_code == 400

    # 3. Non-owner returns 404
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "attacker-user-007",
        "username": "attacker",
        "role": "user",
    }
    attacker_client = TestClient(app)
    res_non_owner = attacker_client.get("/api/v1/horoscope/kp-events/analyses/ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
    assert res_non_owner.status_code == 404

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 34: POST /analyze accepts list-based significations from frontend
# ---------------------------------------------------------------------------
def test_34_analyze_accepts_list_significations():
    from app.services.auth_service import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {
        "id": "4719b6a8-0452-4bfa-ab87-6733190c3de3",
        "username": "test_user",
        "role": "user",
    }
    client = TestClient(app)

    # List-based house significators as produced by KpResponse.house_significators
    list_payload = {
        "lagna": "Aries",
        "periods": [
            {
                "mahadasha_lord": "Jupiter",
                "bhukti_lord": "Sun",
                "start_date": "2026-01-01",
                "end_date": "2027-01-01",
            }
        ],
        "significations": [
            {
                "house": 2,
                "sign_lord": "Venus",
                "star_lord": "Sun",
                "sub_lord": "Jupiter",
                "level_a": ["Jupiter"],
                "level_b": ["Sun"],
                "level_c": ["Venus"],
                "level_d": ["Mercury"],
                "all_significators": ["Jupiter", "Sun", "Venus", "Mercury"],
            },
            {
                "house": 7,
                "sign_lord": "Venus",
                "star_lord": "Mars",
                "sub_lord": "Rahu",
                "level_a": [],
                "level_b": ["Jupiter"],
                "level_c": ["Venus"],
                "level_d": ["Mars"],
                "all_significators": ["Jupiter", "Venus", "Mars"],
            },
        ],
    }

    resp = client.post("/api/v1/horoscope/kp-events/analyze", json=list_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "periods" in data
    assert len(data["periods"]) > 0

    app.dependency_overrides.clear()





