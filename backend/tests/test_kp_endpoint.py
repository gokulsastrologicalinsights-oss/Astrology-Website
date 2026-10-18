"""Automated tests for KP (Krishnamurti Paddhati) endpoint (POST /api/v1/horoscope/kp)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_KP_PAYLOAD = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 1,       # KP Krishnamurti
    "house_system": 2,  # Placidus
}


def test_kp_valid_chart():
    response = client.post("/api/v1/horoscope/kp", json=VALID_KP_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    # Metadata check
    meta = data["metadata"]
    assert meta["ayanamsa_name"] == "KP"
    assert meta["house_system_name"] == "Placidus"
    assert "kpastro" in meta["engine"]

    # 1. Planetary Positions (9 Vedic Grahas)
    planets = data["planetary_positions"]
    assert len(planets) == 9
    expected_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        assert p["planet"] in expected_names
        assert 0.0 <= p["longitude"] < 360.0
        assert 1 <= p["sign_index"] <= 12
        assert p["sign_lord"] in ("Mars", "Venus", "Mercury", "Moon", "Sun", "Jupiter", "Saturn")
        assert p["star_lord"] in ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
        assert p["sub_lord"] in ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
        assert p["sub_sub_lord"] in ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
        # Canonical KP 249 table number must be in range 1..249
        assert 1 <= p["kp_number"] <= 249

    # 2. Cuspal Analysis (12 House Cusps)
    cusps = data["cuspal_analysis"]
    assert len(cusps) == 12
    for idx, c in enumerate(cusps, start=1):
        assert c["house"] == idx
        assert 0.0 <= c["cusp_degree"] < 360.0
        assert 1 <= c["sign_index"] <= 12
        assert c["promise"] in ("Positive", "Negative", "Mixed")

    # 3. Significators (9 Planets)
    significators = data["significators"]
    assert len(significators) == 9
    for s in significators:
        assert s["planet"] in expected_names
        assert isinstance(s["signified_houses"], list)
        for h in s["signified_houses"]:
            assert 1 <= h <= 12
        for entry in s["strength_order"]:
            assert 1 <= entry["house"] <= 12
            assert entry["type"] in ("StarLord", "Occupant", "Owner", "Aspecting")

    # 4. House Significators (Bhaav Nirdeshan: 12 Bhavas with A, B, C, D tiers)
    house_sigs = data["house_significators"]
    assert len(house_sigs) == 12
    for idx, hs in enumerate(house_sigs, start=1):
        assert hs["house"] == idx
        assert isinstance(hs["level_a"], list)
        assert isinstance(hs["level_b"], list)
        assert isinstance(hs["level_c"], list)
        assert isinstance(hs["level_d"], list)
        assert hs["sub_lord"] in expected_names

    # 5. Ruling Planets (RPs)
    rp = data["ruling_planets"]
    assert rp["day_lord"] in expected_names
    assert rp["ascendant_sign_lord"] in expected_names
    assert rp["moon_sign_lord"] in expected_names
    assert len(rp["ruling_planets_list"]) > 0

    # 6. 5-Level KP Vimshottari Dasa Hierarchy
    dasa = data["dasa_hierarchy"]
    assert dasa["mahadasha_lord"] in expected_names
    assert dasa["antardasha_lord"] in expected_names
    assert dasa["pratyantardasha_lord"] in expected_names
    assert dasa["sookshmadasha_lord"] in expected_names
    assert dasa["pranadasha_lord"] in expected_names
    # Monotonic balance ordering: PrD <= SD <= PD <= AD <= MD
    assert dasa["pranadasha_balance_days"] <= dasa["sookshmadasha_balance_days"] + 1e-6
    assert dasa["sookshmadasha_balance_days"] <= dasa["pratyantardasha_balance_days"] + 1e-6
    assert dasa["pratyantardasha_balance_days"] <= dasa["antardasha_balance_days"] + 1e-6
    assert dasa["antardasha_balance_days"] <= dasa["mahadasha_balance_days"] + 1e-6
    assert len(dasa["current_periods"]) == 5
    assert len(dasa["mahadashas"]) == 9


def test_kp_invalid_inputs():
    # Bad latitude
    res_bad_lat = client.post("/api/v1/horoscope/kp", json={**VALID_KP_PAYLOAD, "latitude": 100.0})
    assert res_bad_lat.status_code == 422

    # Bad timezone
    res_bad_tz = client.post("/api/v1/horoscope/kp", json={**VALID_KP_PAYLOAD, "timezone": "Invalid/Zone"})
    assert res_bad_tz.status_code == 422
