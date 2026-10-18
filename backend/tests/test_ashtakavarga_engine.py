"""Automated tests for Ashtakavarga engine, BAV, SAV, Shodhana, and API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ashtakavarga_engine.calculator import calculate_ashtakavarga
from app.services.ashtakavarga_engine.shodhana import (
    apply_trikona_shodhana,
    apply_ekadhipatya_shodhana,
    compute_shodhya_pinda,
)
from app.services.ashtakavarga_engine.tables import (
    EXPECTED_TOTALS,
    TOTAL_SAV_BINDUS,
    PLANETS_7,
    RASHI_GUNAKA,
    GRAHA_GUNAKA,
)

client = TestClient(app)


def test_ashtakavarga_expected_totals_and_sav_invariant():
    """Verify that every planet produces its exact canonical bindu total, and SAV sums to 337."""
    # Arbitrary chart configuration
    planets = [
        {"name": "Sun", "sign_index": 2},       # Taurus
        {"name": "Moon", "sign_index": 4},      # Cancer
        {"name": "Mars", "sign_index": 10},     # Capricorn
        {"name": "Mercury", "sign_index": 3},   # Gemini
        {"name": "Jupiter", "sign_index": 9},   # Sagittarius
        {"name": "Venus", "sign_index": 12},    # Pisces
        {"name": "Saturn", "sign_index": 7},    # Libra
        {"name": "Rahu", "sign_index": 11},    # Must be ignored
        {"name": "Ketu", "sign_index": 5},     # Must be ignored
    ]
    ascendant_sign_idx = 1 # Aries

    result = calculate_ashtakavarga(planets, ascendant_sign_idx)

    # 1. Check individual BAV totals
    for p_name, expected in EXPECTED_TOTALS.items():
        bav = result.bhinnashtakavarga[p_name]
        assert bav.total_bindus == expected, f"{p_name} BAV total {bav.total_bindus} != expected {expected}"
        assert sum(bav.sign_bindus.values()) == expected
        assert sum(bav.house_bindus.values()) == expected

    # 2. Check Sarvashtakavarga grand total
    sav_total = sum(result.sarvashtakavarga.sign_bindus.values())
    assert sav_total == TOTAL_SAV_BINDUS, f"SAV total {sav_total} != {TOTAL_SAV_BINDUS}"
    assert result.sarvashtakavarga.total_bindus == TOTAL_SAV_BINDUS
    assert result.validation_status == "PASSED"


def test_trikona_shodhana_math():
    """Verify Trikona Shodhana subtraction by minimum in each trinal triad."""
    # Custom bindus for 12 signs
    # Triad 1 (Fire: 1, 5, 9): 4, 3, 5 -> min is 3 -> result should be 1, 0, 2
    # Triad 2 (Earth: 2, 6, 10): 6, 6, 6 -> min is 6 -> result should be 0, 0, 0
    # Triad 3 (Air: 3, 7, 11): 5, 0, 4 -> min is 0 -> result should be 5, 0, 4 (unchanged)
    # Triad 4 (Water: 4, 8, 12): 7, 2, 1 -> min is 1 -> result should be 6, 1, 0
    sign_bindus = {
        1: 4, 5: 3, 9: 5,
        2: 6, 6: 6, 10: 6,
        3: 5, 7: 0, 11: 4,
        4: 7, 8: 2, 12: 1,
    }
    reduced = apply_trikona_shodhana(sign_bindus)

    assert reduced[1] == 1
    assert reduced[5] == 0
    assert reduced[9] == 2

    assert reduced[2] == 0
    assert reduced[6] == 0
    assert reduced[10] == 0

    assert reduced[3] == 5
    assert reduced[7] == 0
    assert reduced[11] == 4

    assert reduced[4] == 6
    assert reduced[8] == 1
    assert reduced[12] == 0


def test_ekadhipatya_shodhana_math():
    """Verify Ekadhipatya Shodhana dual-lordship rules."""
    # Mars owns Aries(1) and Scorpio(8)
    # Case A: Neither occupied, unequal (e.g. 1 has 4, 8 has 2) -> both become smaller (2, 2)
    trikona_reduced = {s: 0 for s in range(1, 13)}
    trikona_reduced[1] = 4
    trikona_reduced[8] = 2

    planet_signs = {"Sun": 3, "Moon": 5} # neither 1 nor 8 is occupied
    ek_reduced = apply_ekadhipatya_shodhana(trikona_reduced, planet_signs)
    assert ek_reduced[1] == 2
    assert ek_reduced[8] == 2

    # Case B: Neither occupied, equal (e.g. 1 has 3, 8 has 3) -> both become 0
    trikona_reduced[1] = 3
    trikona_reduced[8] = 3
    ek_reduced = apply_ekadhipatya_shodhana(trikona_reduced, planet_signs)
    assert ek_reduced[1] == 0
    assert ek_reduced[8] == 0

    # Case C: Both occupied -> no reduction
    planet_signs = {"Mars": 1, "Venus": 8}
    trikona_reduced[1] = 5
    trikona_reduced[8] = 3
    ek_reduced = apply_ekadhipatya_shodhana(trikona_reduced, planet_signs)
    assert ek_reduced[1] == 5
    assert ek_reduced[8] == 3

    # Case D: One occupied, other unoccupied
    # Sign 1 occupied (Mars), Sign 8 unoccupied
    planet_signs = {"Mars": 1}
    # Sub-case: unoccupied > occupied (8 has 4, 1 has 2) -> unoccupied reduced to equal occupied
    trikona_reduced[1] = 2
    trikona_reduced[8] = 4
    ek_reduced = apply_ekadhipatya_shodhana(trikona_reduced, planet_signs)
    assert ek_reduced[1] == 2
    assert ek_reduced[8] == 2

    # Sub-case: unoccupied <= occupied (8 has 2, 1 has 3) -> unoccupied eliminated (0)
    trikona_reduced[1] = 3
    trikona_reduced[8] = 2
    ek_reduced = apply_ekadhipatya_shodhana(trikona_reduced, planet_signs)
    assert ek_reduced[1] == 3
    assert ek_reduced[8] == 0


def test_shodhya_pinda_math():
    """Verify Rashi Pinda, Graha Pinda, and Shodhya Pinda formulas."""
    # Test grid with known bindus in signs 1 (Aries) and 5 (Leo)
    # Rashi Gunaka: Aries=7, Leo=10
    reduced = {s: 0 for s in range(1, 13)}
    reduced[1] = 2  # Aries: 2 * 7 = 14
    reduced[5] = 3  # Leo: 3 * 10 = 30
    # Expected Rashi Pinda = 14 + 30 = 44

    # Planets: Sun in Aries(1) [Gunaka=5], Jupiter in Leo(5) [Gunaka=10]
    # Expected Graha Pinda = (2 * 5) + (3 * 10) = 10 + 30 = 40
    # Expected Shodhya Pinda = 44 + 40 = 84
    planet_signs = {"Sun": 1, "Jupiter": 5}

    r_pinda, g_pinda, s_pinda = compute_shodhya_pinda(reduced, planet_signs)
    assert r_pinda == 44
    assert g_pinda == 40
    assert s_pinda == 84


def test_ashtakavarga_api_endpoint():
    """Test POST /api/v1/vedic/ashtakavarga endpoint."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 2,
    }
    response = client.post("/api/v1/vedic/ashtakavarga", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "bhinnashtakavarga" in data
    assert "sarvashtakavarga" in data
    assert data["sarvashtakavarga"]["total_bindus"] == 337
    assert data["validation_status"] == "PASSED"

    # Verify all 7 planets are present
    for p in PLANETS_7:
        assert p in data["bhinnashtakavarga"]
        bav = data["bhinnashtakavarga"][p]
        assert bav["total_bindus"] == EXPECTED_TOTALS[p]
        assert bav["trikona_reduced"] is not None
        assert bav["ekadhipatya_reduced"] is not None
        assert bav["shodhya_pinda"] is not None
