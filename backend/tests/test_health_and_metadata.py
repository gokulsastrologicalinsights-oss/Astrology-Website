"""Automated tests for Health and Metadata endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Gokul's Astrological Insights API"
    assert data["status"] == "operational"
    assert "documentation" in data
    assert "health" in data
    assert "metadata" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Gokul's Astrological Insights API"
    assert "timestamp_utc" in data
    engine = data["engine"]
    assert engine["name"] == "XALEN Ephemeris & Vedic Astrological Engine"
    assert engine["version"] == "0.6.0"
    assert engine["rust_core_available"] is True
    assert engine["error"] is None


def test_metadata_endpoint():
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "XALEN Ephemeris & Vedic Astrological Engine"
    assert data["version"] == "1.0.0"
    assert "Phase D" in data["verified_phases"]
    assert data["kp_sub_divisions"] == 249

    # Ayanamsas
    ayanamsa_ids = [a["id"] for a in data["supported_ayanamsas"]]
    assert 0 in ayanamsa_ids  # Lahiri
    assert 1 in ayanamsa_ids  # KP

    # Houses
    house_ids = [h["id"] for h in data["supported_house_systems"]]
    assert 0 in house_ids  # WholeSign
    assert 2 in house_ids  # Placidus

    # Languages
    lang_codes = [l["code"] for l in data["supported_languages"]]
    assert "en" in lang_codes
    assert "ta" in lang_codes

    # Capabilities & limitations
    cap_ids = [c["id"] for c in data["chart_capabilities"]]
    assert "vedic_horoscope" in cap_ids
    assert "vimshottari_dasa" in cap_ids
    assert "kp_astrology" in cap_ids

    assert len(data["limitations"]) > 0
