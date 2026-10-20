"""Integration tests for KP Events & Prediction FastAPI Router."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_list_events():
    """Tests GET /api/v1/kp-prediction/events endpoint."""
    resp = client.get("/api/v1/kp-prediction/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_events"] >= 30
    events = data["events"]
    assert any(e["name"] == "Marriage" for e in events)
    assert any(e["name"] == "Job" for e in events)


def test_api_scan_direct_input():
    """Tests POST /api/v1/kp-prediction/scan with direct birth input."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "place_name": "Chennai",
        "event_name": "Marriage",
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "scan_resolution_minutes": 15,
        "max_candidates": 5,
        "include_ruling_planets": True,
    }
    resp = client.post("/api/v1/kp-prediction/scan", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "event_promise" in data
    assert data["event_promise"]["event_name"] == "Marriage"
    assert data["event_promise"]["primary_cusp"] == 7
    assert data["event_promise"]["promise_status"] in ["Promised", "Delayed / Mixed", "Denied / Weak"]

    assert "candidate_dasha_periods" in data
    assert "candidate_windows" in data
    assert "report_markdown" in data
    assert len(data["report_markdown"]) > 100
    assert "calculation_convention" in data


def test_api_scan_invalid_event():
    """Tests POST /api/v1/kp-prediction/scan with an invalid event name."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "event_name": "Winning The Megamillions Lottery Tomorrow",
    }
    resp = client.post("/api/v1/kp-prediction/scan", json=payload)
    assert resp.status_code == 422
    assert "Unsupported event category" in resp.json()["detail"]


def test_api_scan_missing_coordinates():
    """Tests POST /api/v1/kp-prediction/scan with missing coordinates."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "event_name": "Marriage",
    }
    resp = client.post("/api/v1/kp-prediction/scan", json=payload)
    assert resp.status_code == 422
    assert "latitude" in resp.json()["detail"] or "coordinates" in resp.json()["detail"]
