"""Automated tests for Vimshottari Dasa endpoint (POST /api/v1/horoscope/dasa)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_DASA_PAYLOAD = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "depth": 2,
    "target_date": "2026-10-17",
}


def test_dasa_valid_chart():
    response = client.post("/api/v1/horoscope/dasa", json=VALID_DASA_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    assert 0.0 <= data["moon_sidereal_deg"] < 360.0
    assert data["nakshatra"]["name"] == "Uttara Ashadha"
    assert data["birth_dasa_lord"] == "Sun"
    assert 0.0 < data["birth_balance_years"] <= 6.0  # Sun total period is 6 years
    assert "Years" in data["birth_balance_formatted"]

    # 9 Mahadashas returned
    tree = data["dasa_tree"]
    assert len(tree) == 9
    assert tree[0]["lord"] == "Sun"
    assert tree[0]["level"] == "Mahadasha"

    # Depth 2 check: each Mahadasha has 9 Antardashas
    for md in tree:
        assert len(md["sub_periods"]) == 9
        for ad in md["sub_periods"]:
            assert ad["level"] == "Antardasha"

    # Active period check
    active = data["active_period"]
    assert active is not None
    assert active["mahadasha"] == "Rahu"
    assert active["antardasha"] == "Moon"
    assert active["target_date_iso"] == "2026-10-17"


def test_dasa_depth_boundaries():
    # Depth = 1 (Mahadasha only, no subperiods)
    res_d1 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 1})
    assert res_d1.status_code == 200
    d1_data = res_d1.json()
    assert len(d1_data["dasa_tree"]) == 9
    assert len(d1_data["dasa_tree"][0]["sub_periods"]) == 0

    # Depth = 3 (Mahadasha -> Antardasha -> Pratyantardasha)
    res_d3 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 3})
    assert res_d3.status_code == 200
    d3_data = res_d3.json()
    assert len(d3_data["dasa_tree"][0]["sub_periods"][0]["sub_periods"]) == 9
    assert d3_data["active_period"]["pratyantardasha"] == "Rahu"

    # Depth = 4 (up to Sookshma)
    res_d4 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 4})
    assert res_d4.status_code == 200

    # Depth = 5 (up to Prana)
    res_d5 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 5})
    assert res_d5.status_code == 200


def test_dasa_invalid_depth():
    # Depth = 0 (violates ge=1)
    res_d0 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 0})
    assert res_d0.status_code == 422

    # Depth = 6 (violates le=5)
    res_d6 = client.post("/api/v1/horoscope/dasa", json={**VALID_DASA_PAYLOAD, "depth": 6})
    assert res_d6.status_code == 422


def test_dasa_direct_endpoint():
    # Direct calculation with Moon at 45.0 degrees (Rohini, Moon lord)
    direct_payload = {
        "moon_sidereal_deg": 45.0,
        "birth_jd": 2451545.0,
        "depth": 2,
        "target_date": "2005-01-01",
    }
    response = client.post("/api/v1/horoscope/dasa/direct", json=direct_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nakshatra"]["name"] == "Rohini"
    assert data["birth_dasa_lord"] == "Moon"
    assert abs(data["birth_balance_years"] - 6.25) < 1e-4
    assert len(data["dasa_tree"]) == 9
