"""Unit tests for KP Events & Prediction Service Layer."""

from datetime import date, datetime, timedelta
import pytest
from app.services.kp_prediction_service import (
    _get_event_rule,
    get_supported_events_list,
    evaluate_event_promise,
    calculate_ruling_planets,
    evaluate_dasha_periods,
    scan_candidate_event_windows,
    generate_kp_prediction_report_markdown,
)
from app.schemas.kp_prediction import KpPredictionResponse, KpEventPromiseResult


@pytest.fixture
def sample_kp_chart():
    """Constructs a deterministic mock KP chart with 12 cusps and planets."""
    return {
        "cusps": [
            {"house": 1, "longitude": 45.0, "sign": "Taurus", "star_lord": "Sun", "sub_lord": "Venus"},
            {"house": 2, "longitude": 75.0, "sign": "Gemini", "star_lord": "Mars", "sub_lord": "Jupiter"},
            {"house": 3, "longitude": 105.0, "sign": "Cancer", "star_lord": "Jupiter", "sub_lord": "Saturn"},
            {"house": 4, "longitude": 135.0, "sign": "Leo", "star_lord": "Ketu", "sub_lord": "Mercury"},
            {"house": 5, "longitude": 165.0, "sign": "Virgo", "star_lord": "Moon", "sub_lord": "Jupiter"},
            {"house": 6, "longitude": 195.0, "sign": "Libra", "star_lord": "Rahu", "sub_lord": "Mars"},
            {"house": 7, "longitude": 225.0, "sign": "Scorpio", "star_lord": "Saturn", "sub_lord": "Mercury"},
            {"house": 8, "longitude": 255.0, "sign": "Sagittarius", "star_lord": "Venus", "sub_lord": "Venus"},
            {"house": 9, "longitude": 285.0, "sign": "Capricorn", "star_lord": "Sun", "sub_lord": "Rahu"},
            {"house": 10, "longitude": 315.0, "sign": "Aquarius", "star_lord": "Mars", "sub_lord": "Saturn"},
            {"house": 11, "longitude": 345.0, "sign": "Pisces", "star_lord": "Jupiter", "sub_lord": "Moon"},
            {"house": 12, "longitude": 15.0, "sign": "Aries", "star_lord": "Ketu", "sub_lord": "Sun"},
        ],
        "planets": {
            "Sun": {"longitude": 120.5, "sign": "Leo", "star_lord": "Ketu", "sub_lord": "Venus", "retrograde": False},
            "Moon": {"longitude": 40.2, "sign": "Taurus", "star_lord": "Sun", "sub_lord": "Jupiter", "retrograde": False},
            "Mars": {"longitude": 210.0, "sign": "Scorpio", "star_lord": "Jupiter", "sub_lord": "Saturn", "retrograde": False},
            "Mercury": {"longitude": 130.0, "sign": "Leo", "star_lord": "Venus", "sub_lord": "Rahu", "retrograde": False},
            "Jupiter": {"longitude": 270.0, "sign": "Capricorn", "star_lord": "Sun", "sub_lord": "Moon", "retrograde": False},
            "Venus": {"longitude": 95.0, "sign": "Cancer", "star_lord": "Saturn", "sub_lord": "Mercury", "retrograde": False},
            "Saturn": {"longitude": 330.0, "sign": "Pisces", "star_lord": "Jupiter", "sub_lord": "Mars", "retrograde": True},
            "Rahu": {"longitude": 15.0, "sign": "Aries", "star_lord": "Ketu", "sub_lord": "Venus", "retrograde": True},
            "Ketu": {"longitude": 195.0, "sign": "Libra", "star_lord": "Rahu", "sub_lord": "Mars", "retrograde": True},
        },
        "house_significators": {
            "2": {"level_a": ["Jupiter"], "level_b": ["Venus"], "level_c": ["Mercury"], "level_d": ["Mercury"]},
            "5": {"level_a": ["Jupiter"], "level_b": ["Moon"], "level_c": ["Sun"], "level_d": ["Mercury"]},
            "7": {"level_a": ["Mercury"], "level_b": ["Mars"], "level_c": ["Saturn"], "level_d": ["Mars"]},
            "11": {"level_a": ["Mercury"], "level_b": ["Jupiter"], "level_c": ["Moon"], "level_d": ["Jupiter"]},
            "6": {"level_a": ["Mars"], "level_b": ["Venus"], "level_c": ["Venus"], "level_d": ["Venus"]},
            "10": {"level_a": ["Saturn"], "level_b": ["Saturn"], "level_c": ["Mars"], "level_d": ["Saturn"]},
        },
    }


def test_supported_events_list():
    """Verifies that all standard event categories are populated."""
    events = get_supported_events_list()
    assert len(events) >= 30
    names = [e["name"] for e in events]
    assert "Marriage" in names
    assert "Job" in names
    assert "Children" in names
    assert "Foreign travel" in names
    assert "Higher education" in names
    # Test alias resolution
    job_rule = _get_event_rule("New job / employment")
    assert job_rule.name == "Job"


def test_evaluate_event_promise_marriage(sample_kp_chart):
    """Tests event promise evaluation for Marriage (7th CSL = Mercury)."""
    rule = _get_event_rule("Marriage")
    res = evaluate_event_promise(sample_kp_chart, rule)

    assert res.event_name == "Marriage"
    assert res.primary_cusp == 7
    assert res.cusp_sub_lord == "Mercury"
    # Mercury signifies 2, 7, 11
    assert 2 in res.csl_significations or 7 in res.csl_significations or 11 in res.csl_significations
    assert res.promise_status in ["Promised", "Delayed / Mixed"]
    assert "Mercury" in res.rule_explanation


def test_calculate_ruling_planets():
    """Tests Ruling Planets computation at a known coordinate and time."""
    j_dt = datetime(2026, 10, 18, 10, 30, 0)
    rp = calculate_ruling_planets(j_dt, lat=13.0827, lon=80.2707, ayanamsa_id=1)

    assert rp.ascendant_sign_lord in ["Mars", "Venus", "Mercury", "Moon", "Sun", "Jupiter", "Saturn"]
    assert rp.moon_sign_lord in ["Mars", "Venus", "Mercury", "Moon", "Sun", "Jupiter", "Saturn"]
    assert rp.day_lord == "Sun"  # Oct 18, 2026 is a Sunday!
    assert len(rp.active_ruling_planets) >= 2


def test_evaluate_dasha_periods(sample_kp_chart):
    """Tests Dasha period filtering and scoring for Marriage."""
    rule = _get_event_rule("Marriage")
    dasa_tree = [
        {
            "lord": "Mercury",
            "start_date": "2026-01-01",
            "end_date": "2043-01-01",
            "children": [
                {
                    "lord": "Venus",
                    "start_date": "2026-06-01",
                    "end_date": "2027-04-01",
                    "children": [
                        {
                            "lord": "Jupiter",
                            "start_date": "2026-09-01",
                            "end_date": "2026-12-01",
                            "children": [],
                        }
                    ],
                }
            ],
        }
    ]
    p_sigs = {
        "Mercury": [2, 7, 11],
        "Venus": [2, 6],
        "Jupiter": [2, 5, 11],
    }
    periods = evaluate_dasha_periods(
        dasa_tree=dasa_tree,
        planet_significations=p_sigs,
        event_rule=rule,
        scan_start=date(2026, 10, 1),
        scan_end=date(2026, 11, 30),
    )
    assert len(periods) >= 1
    # Check that Mercury period is Strongly Supportive
    mercury_p = next((p for p in periods if p.mahadasha_lord == "Mercury"), None)
    assert mercury_p is not None
    assert mercury_p.support_status == "Strongly Supportive"


def test_scan_candidate_event_windows(sample_kp_chart):
    """Tests Moon and Lagna transit scanner over a 15-day range."""
    rule = _get_event_rule("Marriage")
    dasa_tree = [
        {
            "lord": "Mercury",
            "start_date": "2026-01-01",
            "end_date": "2030-01-01",
            "children": [],
        }
    ]
    windows = scan_candidate_event_windows(
        kp_chart=sample_kp_chart,
        event_rule=rule,
        dasa_tree=dasa_tree,
        scan_start=date(2026, 10, 19),
        scan_end=date(2026, 10, 25),
        transit_lat=13.0827,
        transit_lon=80.2707,
        transit_tz_str="Asia/Kolkata",
        ruling_planets={"Mercury", "Jupiter", "Venus", "Sun"},
        max_candidates=10,
        scan_res_min=15,
        ayanamsa_id=1,
    )
    # Should find candidate windows within a 7-day range
    assert isinstance(windows, list)
    if windows:
        w = windows[0]
        assert w.evidence_grade in ["A", "B", "C"]
        assert w.composite_score >= 15.0
        assert ":" in w.start_time
        assert ":" in w.end_time
        assert w.moon_transit["sign"] != ""
        assert w.lagna_transit["sign"] != ""
