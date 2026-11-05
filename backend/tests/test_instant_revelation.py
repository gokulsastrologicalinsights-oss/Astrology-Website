"""Unit and integration tests for Instant Revelation & Teleprompter."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.instant_revelation import InstantRevelationRequest
from app.services.instant_revelation.engine import InstantRevelationEngine

client = TestClient(app)


def test_instant_revelation_engine_direct():
    req = InstantRevelationRequest(
        birth_date="1990-05-15",
        birth_time="14:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        name="Arun Kumar",
        gender="male",
        consultation_time="2026-11-05T17:00:00+05:30",
    )
    res = InstantRevelationEngine.analyze(req)

    assert res.name == "Arun Kumar"
    assert res.birth_date == "1990-05-15"
    assert res.current_age > 30
    assert len(res.current_dasa_summary) > 0
    assert len(res.current_dasa_summary_ta) > 0

    # Pillar 1: Mind Reader
    assert len(res.primary_arrival_reason_en) > 0
    assert len(res.primary_arrival_reason_ta) > 0
    assert len(res.arrival_reason_bullets) >= 1
    assert any(b.category == "mind_reading" for b in res.arrival_reason_bullets)

    # Pillar 2: Past Hits
    assert len(res.past_verifiable_hits) >= 1
    for hit in res.past_verifiable_hits:
        assert hit.shock_factor in ("EXTREME", "HIGH", "MODERATE")
        assert len(hit.script_en) > 0
        assert len(hit.script_ta) > 0

    # Pillar 3: Personal & Domestic Identifiers
    assert len(res.personal_and_home_markers) >= 2
    vastu_marker = next((m for m in res.personal_and_home_markers if m.id == "marker-vastu"), None)
    assert vastu_marker is not None
    assert len(vastu_marker.script_ta) > 0

    # Pillar 4: Future Windows
    assert len(res.future_windows) >= 1
    for win in res.future_windows:
        assert win.status in ("RED_ALERT", "PREPARATION", "GOLDEN_BREAKTHROUGH")
        assert len(win.script_en) > 0
        assert len(win.script_ta) > 0

    # Pillar 5: Turn-Key Remedy
    assert len(res.instant_remedy_en) > 0
    assert len(res.instant_remedy_ta) > 0
    assert len(res.temple_recommendation_en) > 0

    # The 5 Shock Amplifiers
    # 1. Career Calling
    assert len(res.career_calling_en) > 0
    assert len(res.career_calling_ta) > 0
    assert len(res.career_fields) > 0

    # 2. Birth Order
    assert len(res.family_birth_order_en) > 0
    assert len(res.family_birth_order_ta) > 0

    # 3. Gochara Transits
    assert len(res.gochara_saturn_phase) > 0
    assert len(res.gochara_saturn_verdict_en) > 0
    assert len(res.gochara_saturn_verdict_ta) > 0
    assert len(res.gochara_jupiter_verdict_en) > 0
    assert len(res.gochara_jupiter_verdict_ta) > 0

    # 4. Medical Vulnerability
    assert len(res.medical_organ_vulnerability_en) > 0
    assert len(res.medical_organ_vulnerability_ta) > 0
    assert len(res.vulnerable_organs) > 0

    # The 4 Ultra-Precision Nadi Shockers (Option B)
    # 1. Spouse & In-Laws Secrets
    assert len(res.spouse_secrets_en) > 0
    assert len(res.spouse_secrets_ta) > 0

    # 2. Vehicle & Conveyance Marker
    assert len(res.vehicle_marker_en) > 0
    assert len(res.vehicle_marker_ta) > 0

    # 3. Ancestral Land Rift
    assert len(res.ancestral_land_rift_en) > 0
    assert len(res.ancestral_land_rift_ta) > 0

    # 4. Childhood Balarishta
    assert len(res.childhood_balarishta_en) > 0
    assert len(res.childhood_balarishta_ta) > 0

    # Quick Glance Teleprompter
    assert len(res.quick_glance_teleprompter_en) == 5
    assert len(res.quick_glance_teleprompter_ta) == 5


def test_instant_revelation_api_endpoint():
    payload = {
        "birth_date": "1995-10-24",
        "birth_time": "08:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "name": "Priya",
        "gender": "female",
    }
    response = client.post("/api/v1/instant-revelation/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Priya"
    assert "primary_arrival_reason_en" in data
    assert "past_verifiable_hits" in data
    assert len(data["past_verifiable_hits"]) > 0


def test_diversity_of_ultra_shockers_across_different_birth_charts():
    # Chart A: 1985-03-20 06:00 (Pisces Lagna)
    req_a = InstantRevelationRequest(
        birth_date="1985-03-20",
        birth_time="06:00:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        name="Chart A (Pisces)",
        gender="male",
    )
    res_a = InstantRevelationEngine.analyze(req_a)

    # Chart B: 1996-11-15 19:30 (Taurus Lagna)
    req_b = InstantRevelationRequest(
        birth_date="1996-11-15",
        birth_time="19:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        name="Chart B (Taurus)",
        gender="female",
    )
    res_b = InstantRevelationEngine.analyze(req_b)

    # Confirm that Ultra-Nadi answers are customized and distinctly different
    assert res_a.vehicle_marker_en != res_b.vehicle_marker_en
    assert res_a.vehicle_marker_ta != res_b.vehicle_marker_ta
    assert res_a.spouse_secrets_en != res_b.spouse_secrets_en
    assert res_a.spouse_secrets_ta != res_b.spouse_secrets_ta
    assert res_a.childhood_balarishta_en != res_b.childhood_balarishta_en
    assert res_a.childhood_balarishta_ta != res_b.childhood_balarishta_ta
