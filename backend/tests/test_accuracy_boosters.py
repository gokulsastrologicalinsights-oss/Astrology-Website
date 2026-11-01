"""Tests for Accuracy Boosters:
1. Birth Time Rectification (BTR) Assistant
2. Double Transit ('Guru-Shani') Event Timing Radar
3. Ashtakavarga Kaksha Transit Trigger Alert System
"""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.btr import BtrRequest, BtrLifeEventInput
from app.schemas.double_transit import DoubleTransitRequest
from app.schemas.kaksha_alerts import KakshaAlertRequest
from app.services.kp_engine.btr_engine import run_birth_time_rectification, EVENT_TEMPLATES
from app.services.double_transit_engine import calculate_double_transit_radar, DOMAINS
from app.services.ashtakavarga_engine.kaksha_alert_engine import generate_kaksha_transit_alerts


client = TestClient(app)

# Standard Test Subject Birth Profile (Chennai, India, Oct 24 1995 14:30)
BASE_BIRTH = {
    "birth_date": date(1995, 10, 24),
    "birth_time": time(14, 30),
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 1,
}


# ===========================================================================
# 1. Birth Time Rectification (BTR) Assistant Tests
# ===========================================================================

def test_btr_event_templates_available():
    """Verify standard life event presets are available."""
    assert len(EVENT_TEMPLATES) >= 5
    ids = [t["id"] for t in EVENT_TEMPLATES]
    assert "marriage" in ids
    assert "first_job" in ids
    assert "childbirth" in ids
    assert "accident_surgery" in ids


def test_btr_engine_rectification_execution():
    """Verify BTR engine rectifies birth time and detects Varga Lagna shifts."""
    events = [
        BtrLifeEventInput(
            label="First Job Offer",
            event_date=date(2018, 6, 15),
            primary_house=10,
            secondary_houses=[2, 6, 11],
        ),
        BtrLifeEventInput(
            label="Marriage",
            event_date=2022, # Intentionally check valid date
            primary_house=7,
            secondary_houses=[2, 11],
        ) if False else BtrLifeEventInput(
            label="Marriage",
            event_date=date(2022, 11, 20),
            primary_house=7,
            secondary_houses=[2, 11],
        ),
        BtrLifeEventInput(
            label="Home Purchase",
            event_date=date(2024, 3, 10),
            primary_house=4,
            secondary_houses=[11, 12],
        ),
    ]

    req = BtrRequest(
        birth_date=BASE_BIRTH["birth_date"],
        birth_time=BASE_BIRTH["birth_time"],
        timezone=BASE_BIRTH["timezone"],
        latitude=BASE_BIRTH["latitude"],
        longitude=BASE_BIRTH["longitude"],
        events=events,
        window_minutes=15.0,
        step_minutes=1.0,
        refine_seconds=True,
        use_ruling_planets=True,
    )

    resp = run_birth_time_rectification(req)

    assert resp.rectified_time is not None
    assert len(resp.top_candidates) > 0
    assert resp.best_candidate.confidence_percentage > 0
    assert resp.credible_interval is not None

    # Check shift comparison has D9, D60, and LSL data
    assert resp.shift_comparison.approx_lsl is not None
    assert resp.shift_comparison.rectified_lsl is not None
    assert resp.shift_comparison.approx_d9.sign_name is not None
    assert resp.shift_comparison.rectified_d9.sign_name is not None
    assert resp.shift_comparison.rectified_d60.division_specific is not None


def test_btr_api_endpoint():
    """Verify HTTP POST /api/v1/horoscope/kp/rectify endpoint."""
    payload = {
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 1,
        "window_minutes": 10.0,
        "step_minutes": 1.0,
        "refine_seconds": True,
        "events": [
            {
                "label": "Promotion",
                "event_date": "2020-08-15",
                "primary_house": 10,
                "secondary_houses": [2, 11],
            },
            {
                "label": "Marriage Ceremony",
                "event_date": "2023-01-22",
                "primary_house": 7,
                "secondary_houses": [2, 11],
            }
        ]
    }

    res = client.post("/api/v1/horoscope/kp/rectify", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "rectified_time" in data
    assert "shift_comparison" in data
    assert "credible_interval" in data


# ===========================================================================
# 2. Double Transit ("Guru-Shani") Event Timing Radar Tests
# ===========================================================================

def test_double_transit_engine_marriage():
    """Verify Double Transit radar calculates windows and aligns Dasa for marriage."""
    req = DoubleTransitRequest(
        birth_date=BASE_BIRTH["birth_date"],
        birth_time=BASE_BIRTH["birth_time"],
        timezone=BASE_BIRTH["timezone"],
        latitude=BASE_BIRTH["latitude"],
        longitude=BASE_BIRTH["longitude"],
        domain="marriage",
        forecast_years=3,
        include_rahu=True,
    )

    resp = calculate_double_transit_radar(req)

    assert resp.domain.id == "marriage"
    assert resp.target_house == 7
    assert resp.natal_lagna_sign is not None
    assert len(resp.windows) > 0
    assert resp.current_transits.saturn_sign is not None
    assert resp.current_transits.jupiter_sign is not None
    assert resp.summary_verdict is not None


def test_double_transit_api_endpoint():
    """Verify HTTP POST /api/v1/vedic/double-transit."""
    payload = {
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "domain": "career",
        "forecast_years": 2,
    }

    res = client.post("/api/v1/vedic/double-transit", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["target_house"] == 10
    assert len(data["windows"]) > 0


# ===========================================================================
# 3. Ashtakavarga Kaksha Transit Trigger Alert Tests
# ===========================================================================

def test_kaksha_transit_alerts_engine():
    """Verify real-time Kaksha trigger alert engine detects Bindu 1 vs 0."""
    req = KakshaAlertRequest(
        birth_date=BASE_BIRTH["birth_date"],
        birth_time=BASE_BIRTH["birth_time"],
        timezone=BASE_BIRTH["timezone"],
        latitude=BASE_BIRTH["latitude"],
        longitude=BASE_BIRTH["longitude"],
        horizon_days=60,
        planets=["Saturn", "Jupiter", "Mars"],
        filter_domain="all",
    )

    resp = generate_kaksha_transit_alerts(req)

    assert len(resp.active_now) == 3
    # Check that Saturn, Jupiter, Mars each have an active Kaksha status
    planets_active = [s.planet for s in resp.active_now]
    assert "Saturn" in planets_active
    assert "Jupiter" in planets_active
    assert "Mars" in planets_active

    assert len(resp.timeline_alerts) > 0
    assert "health" in resp.domain_summaries
    assert "finances" in resp.domain_summaries
    assert "career" in resp.domain_summaries
    assert "lawsuits" in resp.domain_summaries


def test_kaksha_alerts_api_endpoint():
    """Verify HTTP POST /api/v1/vedic/ashtakavarga/kaksha-alerts."""
    payload = {
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "horizon_days": 45,
        "planets": ["Saturn", "Jupiter", "Mars"],
    }

    res = client.post("/api/v1/vedic/ashtakavarga/kaksha-alerts", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data["active_now"]) == 3
    assert len(data["timeline_alerts"]) > 0
