"""Tests for KP Daily Horoscope & Transit Service and API Endpoints."""

import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction


client = TestClient(app)


def test_compute_kp_daily_horoscope_all_12_rashis():
    """Verify that all 12 Rashis are calculated with complete predictions."""
    res = compute_kp_daily_horoscope(
        target_date="2026-11-09",
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
        ayanamsa_id=1,
    )
    assert isinstance(res, KpDailyHoroscopeResponse)
    assert res.total_rashis == 12
    assert len(res.predictions) == 12

    # Check date metadata
    assert res.date == "2026-11-09"
    assert res.day_of_week == "Monday"
    assert res.day_of_week_ta == "திங்கட்கிழமை"
    assert res.day_lord == "Moon"
    assert res.ayanamsa_name in ("KP", "Krishnamurti")

    expected_rashis = [
        ("Aries", "மேஷம்"),
        ("Taurus", "ரிஷபம்"),
        ("Gemini", "மிதுனம்"),
        ("Cancer", "கடகம்"),
        ("Leo", "சிம்மம்"),
        ("Virgo", "கன்னி"),
        ("Libra", "துலாம்"),
        ("Scorpio", "விருச்சிகம்"),
        ("Sagittarius", "தனுசு"),
        ("Capricorn", "மகரம்"),
        ("Aquarius", "கும்பம்"),
        ("Pisces", "மீனம்"),
    ]

    for idx, (en, ta) in enumerate(expected_rashis, start=1):
        p = res.predictions[idx - 1]
        assert p.rashi_id == idx
        assert p.rashi_name_en == en
        assert p.rashi_name_ta == ta
        assert 0 <= p.daily_score <= 100
        assert 1.0 <= p.daily_rating_stars <= 5.0
        assert p.day_sentiment in ("Excellent", "Favorable", "Mixed", "Challenging")

        # Check Brief statement
        assert len(p.brief_statement_en) > 10
        assert len(p.brief_statement_ta) > 10
        assert len(p.peak_highlight_en) > 5
        assert len(p.peak_highlight_ta) > 5
        assert len(p.caution_trap_en) > 5
        assert len(p.caution_trap_ta) > 5

        # Check Golden & Caution windows
        assert "-" in p.golden_hour_window
        assert "-" in p.caution_hour_window

        # Check Lucky attributes
        assert len(p.lucky_color_en) > 0
        assert len(p.lucky_direction_en) > 0
        assert 1 <= p.lucky_number <= 9

        # Check aspects: exactly 5 aspects
        assert len(p.aspects) == 5
        aspect_codes = {a.aspect_code for a in p.aspects}
        assert aspect_codes == {"career", "finance", "love", "health", "travel"}

        for asp in p.aspects:
            assert 0 <= asp.score <= 100
            assert 1.0 <= asp.rating_stars <= 5.0
            assert asp.status in ("Excellent", "Favorable", "Mixed", "Challenging")
            assert len(asp.insight_en) > 10
            assert len(asp.insight_ta) > 10
            assert len(asp.key_recommendation_en) > 5
            assert len(asp.key_recommendation_ta) > 5

        # Check Moon Sub-Lord hourly windows
        assert len(p.moon_sub_windows) >= 1
        for w in p.moon_sub_windows:
            assert w.sentiment in ("golden", "neutral", "caution")
            assert len(w.start_time) > 0
            assert len(w.end_time) > 0
            assert len(w.sub_lord) > 0
            assert len(w.advice_en) > 0
            assert len(w.advice_ta) > 0


def test_compute_kp_daily_horoscope_single_rashi():
    """Verify filtering by single rashi number and name."""
    res_num = compute_kp_daily_horoscope(target_date="2026-11-09", rashi_filter="8")
    assert res_num.total_rashis == 1
    assert res_num.predictions[0].rashi_id == 8
    assert res_num.predictions[0].rashi_name_en == "Scorpio"
    assert res_num.predictions[0].rashi_name_ta == "விருச்சிகம்"

    res_name = compute_kp_daily_horoscope(target_date="2026-11-09", rashi_filter="Leo")
    assert res_name.total_rashis == 1
    assert res_name.predictions[0].rashi_id == 5
    assert res_name.predictions[0].rashi_name_en == "Leo"
    assert res_name.predictions[0].rashi_name_ta == "சிம்மம்"


def test_api_get_daily_horoscope_endpoint():
    """Test GET /api/v1/kp/daily-horoscope."""
    response = client.get("/api/v1/kp/daily-horoscope?date=2026-11-09&rashi=1")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-11-09"
    assert data["total_rashis"] == 1
    pred = data["predictions"][0]
    assert pred["rashi_name_en"] == "Aries"
    assert "brief_statement_en" in pred
    assert "brief_statement_ta" in pred
    assert len(pred["aspects"]) == 5


def test_api_post_daily_horoscope_endpoint():
    """Test POST /api/v1/kp/daily-horoscope with JSON payload."""
    payload = {
        "target_date": "2026-11-09",
        "timezone": "Asia/Kolkata",
        "rashi": "all",
        "ayanamsa": 1,
    }
    response = client.post("/api/v1/kp/daily-horoscope", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rashis"] == 12
    assert len(data["predictions"]) == 12
