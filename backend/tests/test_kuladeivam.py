"""Unit tests for Kuladeivam (Family Deity) Finding Engine."""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.kuladeivam import KuladeivamRequest, KuladeivamPrasannaRequest
from app.services.kuladeivam_service import KuladeivamService

client = TestClient(app)


def test_kuladeivam_horoscope_service():
    """Verify horoscope-based Kuladeivam calculation."""
    req = KuladeivamRequest(
        birth_date=date(1995, 10, 24),
        birth_time=time(14, 30, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ancestral_district="Madurai",
    )
    res = KuladeivamService.calculate_from_horoscope(req)
    assert res.analysis_mode == "horoscope"
    assert res.primary_deity is not None
    assert len(res.primary_deity.deity_name_ta) > 0
    assert len(res.primary_deity.traditional_forms_ta) > 0
    assert res.fifth_house.house_num == 5
    assert res.ninth_house.house_num == 9
    assert res.temple_landscape.primary_direction_ta != ""
    assert len(res.discovery_protocol.universal_refuge_temples) == 4


def test_kuladeivam_prasanna_service():
    """Verify horary Jamakkol prasanna based Kuladeivam calculation."""
    req = KuladeivamPrasannaRequest(
        query_datetime="2026-11-04T12:00:00",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
    )
    res = KuladeivamService.calculate_from_prasanna(req)
    assert res.analysis_mode == "prasanna"
    assert res.primary_deity is not None
    assert res.temple_landscape.primary_direction_en != ""
    assert res.dosha_analysis.status_ta != ""


def test_kuladeivam_api_endpoints():
    """Verify FastAPI router endpoints."""
    # 1. Horoscope POST
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "09:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 10.7905,
        "longitude": 79.1378,
        "ancestral_district": "Thanjavur",
    }
    resp = client.post("/api/v1/kuladeivam/find", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "primary_deity" in data
    assert "temple_landscape" in data
    assert "dosha_analysis" in data
    assert "discovery_protocol" in data

    # 2. Universal temples GET
    resp_temples = client.get("/api/v1/kuladeivam/universal-temples")
    assert resp_temples.status_code == 200
    temples = resp_temples.json()
    assert len(temples) == 4

    # 3. Deity catalog GET
    resp_catalog = client.get("/api/v1/kuladeivam/deity-catalog")
    assert resp_catalog.status_code == 200
    assert "Sun" in resp_catalog.json()
