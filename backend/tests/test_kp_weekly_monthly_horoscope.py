"""Tests for KP Weekly & Monthly Horoscope and Transit Prediction Services."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.kp_daily_horoscope import (
    KpMonthlyHoroscopeResponse,
    KpWeeklyHoroscopeResponse,
    RashiMonthlyPrediction,
    RashiWeeklyPrediction,
)
from app.services.kp_period_horoscope_service import (
    compute_kp_monthly_horoscope,
    compute_kp_weekly_horoscope,
)

client = TestClient(app)


def test_compute_kp_weekly_horoscope_all_rashis():
    """Verify weekly horoscope calculates 12 Rashis with transits and Chandrashtama."""
    res = compute_kp_weekly_horoscope(
        target_date="2026-11-14",
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
        ayanamsa_id=1,
    )
    assert isinstance(res, KpWeeklyHoroscopeResponse)
    assert res.total_rashis == 12
    assert len(res.predictions) == 12
    assert res.start_date == "2026-11-09"
    assert res.end_date == "2026-11-15"
    assert "Nov 09, 2026" in res.week_label_en
    assert "நவம்பர் 2026" in res.week_label_ta

    for p in res.predictions:
        assert isinstance(p, RashiWeeklyPrediction)
        assert 1 <= p.rashi_id <= 12
        assert 0 <= p.weekly_score <= 100
        assert 1.0 <= p.weekly_rating_stars <= 5.0
        assert p.week_sentiment in ("Excellent", "Favorable", "Mixed", "Challenging")
        assert len(p.brief_statement_en) > 10
        assert len(p.brief_statement_ta) > 10
        assert len(p.chandrashtama_days_ta) > 0
        assert len(p.lucky_days_ta) > 0
        assert len(p.weekly_remedy_ta) > 0

        # Aspects check
        assert len(p.aspects) == 5
        aspect_codes = {a.aspect_code for a in p.aspects}
        assert aspect_codes == {"career", "finance", "love", "health", "travel"}

        # Transit summary check
        ts = p.transit_summary
        assert ts.rashi_id == p.rashi_id
        assert len(ts.transit_overview_en) > 20
        assert len(ts.transit_overview_ta) > 20
        assert len(ts.planet_transits) >= 7

        for tm in ts.planet_transits:
            assert 1 <= tm.house_relative <= 12
            assert tm.status in ("favorable", "neutral", "caution")
            assert len(tm.impact_summary_en) > 5
            assert len(tm.impact_summary_ta) > 5


def test_compute_kp_monthly_horoscope_all_rashis():
    """Verify monthly horoscope calculates 12 Rashis with transits and date spans."""
    res = compute_kp_monthly_horoscope(
        year=2026,
        month=11,
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
        ayanamsa_id=1,
    )
    assert isinstance(res, KpMonthlyHoroscopeResponse)
    assert res.year == 2026
    assert res.month == 11
    assert res.start_date == "2026-11-01"
    assert res.end_date == "2026-11-30"
    assert res.month_name_en == "November 2026"
    assert res.month_name_ta == "நவம்பர் 2026"
    assert res.total_rashis == 12
    assert len(res.predictions) == 12

    for p in res.predictions:
        assert isinstance(p, RashiMonthlyPrediction)
        assert 1 <= p.rashi_id <= 12
        assert 0 <= p.monthly_score <= 100
        assert 1.0 <= p.monthly_rating_stars <= 5.0
        assert p.month_sentiment in ("Excellent", "Favorable", "Mixed", "Challenging")
        assert len(p.brief_statement_en) > 10
        assert len(p.brief_statement_ta) > 10
        assert len(p.chandrashtama_dates_ta) > 0
        assert len(p.auspicious_dates_ta) > 0
        assert len(p.monthly_remedy_ta) > 0

        # Aspects check
        assert len(p.aspects) == 5

        # Transit summary check
        ts = p.transit_summary
        assert ts.rashi_id == p.rashi_id
        assert len(ts.transit_overview_en) > 20
        assert len(ts.transit_overview_ta) > 20
        assert len(ts.planet_transits) >= 7


def test_weekly_endpoint_get_and_post():
    """Verify HTTP GET and POST for weekly horoscope endpoint."""
    # GET
    res_get = client.get("/api/v1/kp/weekly-horoscope?date=2026-11-14&rashi=Aries")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["total_rashis"] == 1
    assert data_get["predictions"][0]["rashi_name_en"] == "Aries"
    assert "transit_summary" in data_get["predictions"][0]

    # POST
    payload = {"target_date": "2026-11-14", "rashi": "all", "ayanamsa": 1}
    res_post = client.post("/api/v1/kp/weekly-horoscope", json=payload)
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["total_rashis"] == 12


def test_monthly_endpoint_get_and_post():
    """Verify HTTP GET and POST for monthly horoscope endpoint."""
    # GET
    res_get = client.get("/api/v1/kp/monthly-horoscope?year=2026&month=11&rashi=Leo")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["total_rashis"] == 1
    assert data_get["predictions"][0]["rashi_name_en"] == "Leo"
    assert "transit_summary" in data_get["predictions"][0]

    # POST
    payload = {"year": 2026, "month": 11, "rashi": "all", "ayanamsa": 1}
    res_post = client.post("/api/v1/kp/monthly-horoscope", json=payload)
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["total_rashis"] == 12
