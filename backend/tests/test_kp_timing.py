"""Unit tests for KP Monthly & Period Predictive Event Timing Engine."""

import pytest
from datetime import date, time
from app.schemas.common import BirthInput
from app.services.kp_timing_service import calculate_kp_monthly_prediction


def test_kp_monthly_prediction_november_2026():
    birth = BirthInput(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
    )
    res = calculate_kp_monthly_prediction(birth, year=2026, month=11)
    
    assert res.year == 2026
    assert res.month == 11
    assert "நவம்பர்" in res.month_label_ta
    assert res.dasha_hierarchy.mahadasha != ""
    assert res.dasha_hierarchy.antardasha != ""
    assert res.dasha_hierarchy.pratyantardasha != ""
    assert len(res.transit_sun.activated_stars) > 0
    assert len(res.all_events) == 11
    # Check that at least some events are categorized
    total_categorized = (
        len(res.guaranteed_events)
        + len(res.favorable_events)
        + len(res.moderate_events)
        + len(res.caution_events)
    )
    assert total_categorized == 11
    for ev in res.all_events:
        assert ev.trigger_window_dates != ""
        assert ev.summary_verdict_ta != ""
        assert ev.cuspal_promise_ta != ""
        assert ev.actionable_remedy_ta != ""


def test_kp_monthly_prediction_december_2026():
    birth = BirthInput(
        birth_date=date(1995, 10, 22),
        birth_time=time(6, 15),
        latitude=11.0168,
        longitude=76.9558,
        timezone="Asia/Kolkata",
    )
    res = calculate_kp_monthly_prediction(birth, year=2026, month=12)
    assert res.month == 12
    assert "டிசம்பர்" in res.month_label_ta
    assert len(res.all_events) == 11
