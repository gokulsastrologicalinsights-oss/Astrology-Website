"""Integration tests for Muhurta and Panchanga FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_occasions_endpoint():
    """Verify listing of default system occasions."""
    response = client.get("/api/v1/muhurta/occasions")
    assert response.status_code == 200
    data = response.json()
    assert "occasions" in data
    assert len(data["occasions"]) >= 15
    codes = [o["code"] for o in data["occasions"]]
    assert "marriage" in codes
    assert "griha_pravesham" in codes
    assert "shop_opening" in codes
    assert "vehicle_purchase" in codes
    assert "namakaranam" in codes or "naming_ceremony" in codes


def test_panchang_endpoint():
    """Verify location-specific Panchang calculation endpoint."""
    payload = {
        "date": "2026-10-18",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "ayanamsa_id": 0,
    }
    response = client.post("/api/v1/muhurta/panchang", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-10-18"
    assert "tithi" in data
    assert "nakshatra" in data
    assert "inauspicious_periods" in data
    assert "rahu_kalam" in data["inauspicious_periods"]
    assert "horas" in data
    assert len(data["horas"]["all_horas"]) == 24
    assert "sun_sign" in data
    assert "moon_sign" in data


def test_hora_endpoint():
    """Verify dedicated 24-Hora calculation endpoint."""
    payload = {
        "date": "2026-10-18",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "ayanamsa_id": 0,
    }
    response = client.post("/api/v1/muhurta/hora", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "day_horas" in data
    assert len(data["day_horas"]) == 12
    assert "night_horas" in data
    assert len(data["night_horas"]) == 12
    assert "all_horas" in data
    assert len(data["all_horas"]) == 24
    assert data["day_lord"]["name_en"] == "Sun"


def test_find_muhurtas_endpoint():
    """Verify search and candidate ranking over a date range."""
    payload = {
        "occasion_code": "marriage",
        "start_date": "2026-10-18",
        "end_date": "2026-10-20",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "preferred_time_range": "morning",
        "ayanamsa_id": 0,
        "limit": 20,
    }
    response = client.post("/api/v1/muhurta/find", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert len(data["candidates"]) > 0
    assert "calendar_summary" in data

    candidate = data["candidates"][0]
    assert "status" in candidate
    assert "score" in candidate
    assert "tithi" in candidate
    assert "ascendant" in candidate
    assert "explanation" in candidate


def test_find_muhurtas_invalid_date_range():
    """Verify validation error when start_date > end_date."""
    payload = {
        "occasion_code": "marriage",
        "start_date": "2026-10-25",
        "end_date": "2026-10-18",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
    }
    response = client.post("/api/v1/muhurta/find", json=payload)
    assert response.status_code == 422
