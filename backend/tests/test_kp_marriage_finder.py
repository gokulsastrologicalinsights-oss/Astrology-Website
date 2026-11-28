"""Tests for KP Marriage Promise, Timing & Date Finder (4-Stage Engine)."""

from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.services.kp_marriage_finder import (
    AVOID_TITHIS,
    AVOID_WEEKDAYS,
    calculate_kp_marriage_date,
)

client = TestClient(app)


def test_kp_marriage_finder_service_end_to_end():
    birth = BirthInput(
        birth_date="1995-05-15",
        birth_time="08:30:00",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
        place_name="Chennai",
    )
    res = calculate_kp_marriage_date(
        birth=birth,
        start_date=date(2026, 12, 1),
        years_ahead=2,
        ayanamsa_id=1,
        native_name="Test Native",
    )

    # 1. Promise Assessment (40 + 40 + 15 + 5 = 100 max)
    assert 0.0 <= res.promise.total_score <= 100.0
    assert res.promise.verdict in {"Strong", "Moderate", "Weak / Delayed"}
    assert len(res.promise.factors) == 4
    max_sum = sum(f.max_score for f in res.promise.factors)
    assert max_sum == 100.0

    # 2. 7th Cusp Analysis
    assert res.seventh_cusp.sign
    assert res.seventh_cusp.star_lord
    assert res.seventh_cusp.sub_lord
    assert res.seventh_cusp.sub_sub_lord
    assert len(res.seventh_cusp.target_lords) == 3

    # 3. Dasha-Bhukti-Antara Windows (max 25)
    assert len(res.dasha_windows) > 0
    for w in res.dasha_windows:
        assert 0.0 <= w.total_score <= 25.0
        assert w.dasha_score <= 10.0
        assert w.bhukti_score <= 10.0
        assert w.antara_score <= 5.0

    # 4. Candidate Dates respect Muhurta exclusions (no Tue/Sat, no Rikta/Ashtami/Navami)
    assert len(res.candidate_dates) > 0
    for cd in res.candidate_dates:
        assert cd.weekday_en not in {"Tuesday", "Saturday"}
        assert cd.score > 0.0
        assert cd.abhijit_window
        assert cd.rahu_kalam_avoid

    # 5. Composite weights (70 / 25 / 5)
    assert res.composite_weights["promise_70"] <= 70.0
    assert res.composite_weights["dasha_bhukti_25"] <= 25.0
    assert res.composite_weights["transit_muhurta_5"] <= 5.0


def test_kp_marriage_date_api_endpoint():
    payload = {
        "birth": {
            "birth_date": "1996-08-22",
            "birth_time": "14:15:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
            "place_name": "Chennai",
        },
        "native_name": "Arun",
        "start_date": "2026-12-01",
        "years_ahead": 2,
        "ayanamsa_id": 1,
    }
    resp = client.post("/api/v1/kp/timing/marriage-date", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["native_name"] == "Arun"
    assert "promise" in data
    assert "seventh_cusp" in data
    assert "dasha_windows" in data
    assert "candidate_dates" in data
    assert len(data["promise"]["factors"]) == 4


def test_kp_marriage_date_api_requires_birth_or_saved_id():
    resp = client.post("/api/v1/kp/timing/marriage-date", json={"years_ahead": 2})
    assert resp.status_code == 422
