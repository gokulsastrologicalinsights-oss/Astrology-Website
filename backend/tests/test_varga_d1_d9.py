"""Comprehensive test suite for D1 Rasi & D9 Navamsa calculation engine and API endpoints.

Tests:
1. Exact integer arithmetic & boundary safety across all 108 Navamsas (including epsilon offsets).
2. Elemental cycle sequence (Fire -> Aries, Earth -> Cap, Air -> Libra, Water -> Cancer).
3. Vargottama dignities (Movable pada 1, Fixed pada 5, Dual pada 9).
4. Classical 24 Pushkara Navamsa identification per Jataka Parijata Ch. 1, Sloka 58.
5. Canonical reference chart verification against native XALEN ephemeris.
6. FastAPI endpoints: POST /api/v1/horoscope/varga/d1-d9 and GET /api/v1/horoscope/varga/d1-d9/{id}.
"""

import math
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.varga_engine import (
    calculate_navamsa_from_longitude,
    normalize_longitude_mas,
    calculate_varga_d1_d9,
    calculate_varga_from_horoscope_dict,
    MAS_PER_NAVAMSA,
    MAS_PER_CIRCLE,
)
from app.services.ephemeris import calculate_full_horoscope
from app.schemas.varga import VargaD1D9Request

client = TestClient(app)


# ============================================================================
# 1. MATHEMATICAL & BOUNDARY PRECISION TESTS (All 108 Navamsas)
# ============================================================================

def test_108_navamsa_boundaries_exact_and_epsilons():
    """Verify that every single one of the 108 boundaries resolves strictly and monotonically."""
    for i in range(108):
        boundary_deg = i * (10.0 / 3.0)
        
        # Test exact boundary
        res_exact = calculate_navamsa_from_longitude(boundary_deg)
        expected_d1_sign = (i // 9) + 1
        expected_nav_idx_in_sign = (i % 9) + 1
        
        assert res_exact["d1_sign_index"] == expected_d1_sign, f"Boundary {i} exact D1 sign mismatch"
        assert res_exact["navamsa_index_in_sign"] == expected_nav_idx_in_sign, f"Boundary {i} exact navamsa index mismatch"
        assert 0.0 <= res_exact["d9_degree_in_sign"] < 30.0, f"Boundary {i} degree range invalid"
        
        # Test slightly inside (boundary + 1e-6)
        res_inside = calculate_navamsa_from_longitude(boundary_deg + 1e-6)
        assert res_inside["d1_sign_index"] == expected_d1_sign
        assert res_inside["navamsa_index_in_sign"] == expected_nav_idx_in_sign
        
        # Test slightly before (boundary - 1e-6, unless i == 0 which is 359.999999)
        if i > 0:
            res_before = calculate_navamsa_from_longitude(boundary_deg - 1e-6)
            prev_expected_d1_sign = ((i - 1) // 9) + 1
            prev_expected_nav_idx = ((i - 1) % 9) + 1
            assert res_before["d1_sign_index"] == prev_expected_d1_sign
            assert res_before["navamsa_index_in_sign"] == prev_expected_nav_idx


def test_zero_and_360_degree_wraparound():
    """Verify 0.0 deg Aries and 360.0 wraparound."""
    res_0 = calculate_navamsa_from_longitude(0.0)
    assert res_0["d1_sign_index"] == 1  # Aries
    assert res_0["d9_sign_index"] == 1  # Aries (Fire movable -> starts in Aries)
    assert res_0["navamsa_index_in_sign"] == 1
    assert res_0["is_vargottama"] is True
    assert res_0["nakshatra_name"] == "Ashwini"
    assert res_0["pada"] == 1

    res_360 = calculate_navamsa_from_longitude(360.0)
    assert res_360["d1_sign_index"] == 1
    assert res_360["d9_sign_index"] == 1
    assert res_360["is_vargottama"] is True

    res_359_999 = calculate_navamsa_from_longitude(359.999999)
    assert res_359_999["d1_sign_index"] == 12  # Pisces
    assert res_359_999["d9_sign_index"] == 12  # Pisces (Water dual -> 9th navamsa is Pisces)
    assert res_359_999["navamsa_index_in_sign"] == 9
    assert res_359_999["is_vargottama"] is True
    assert res_359_999["nakshatra_name"] == "Revati"
    assert res_359_999["pada"] == 4


# ============================================================================
# 2. ELEMENTAL CYCLE SEQUENCE TESTS
# ============================================================================

def test_elemental_cycle_starting_signs():
    """Verify the 4 elemental starting signs: Fire -> 1, Earth -> 10, Air -> 7, Water -> 4."""
    # Fire signs: Aries (0°), Leo (120°), Sagittarius (240°)
    for fire_deg in [0.001, 120.001, 240.001]:
        res = calculate_navamsa_from_longitude(fire_deg)
        assert res["navamsa_index_in_sign"] == 1
        assert res["d9_sign_index"] == 1, f"Fire sign at {fire_deg} must start in Aries (1)"

    # Earth signs: Taurus (30°), Virgo (150°), Capricorn (270°)
    for earth_deg in [30.001, 150.001, 270.001]:
        res = calculate_navamsa_from_longitude(earth_deg)
        assert res["navamsa_index_in_sign"] == 1
        assert res["d9_sign_index"] == 10, f"Earth sign at {earth_deg} must start in Capricorn (10)"

    # Air signs: Gemini (60°), Libra (180°), Aquarius (300°)
    for air_deg in [60.001, 180.001, 300.001]:
        res = calculate_navamsa_from_longitude(air_deg)
        assert res["navamsa_index_in_sign"] == 1
        assert res["d9_sign_index"] == 7, f"Air sign at {air_deg} must start in Libra (7)"

    # Water signs: Cancer (90°), Scorpio (210°), Pisces (330°)
    for water_deg in [90.001, 210.001, 330.001]:
        res = calculate_navamsa_from_longitude(water_deg)
        assert res["navamsa_index_in_sign"] == 1
        assert res["d9_sign_index"] == 4, f"Water sign at {water_deg} must start in Cancer (4)"


# ============================================================================
# 3. VARGOTTAMA DIGNITY TESTS
# ============================================================================

def test_vargottama_rules():
    """Verify exactly 12 Vargottama positions across the zodiac:
    - Movable (1, 4, 7, 10): 1st Navamsa (0° - 3°20')
    - Fixed (2, 5, 8, 11): 5th Navamsa (13°20' - 16°40')
    - Dual (3, 6, 9, 12): 9th Navamsa (26°40' - 30°00')
    """
    vargottama_count = 0
    for sign_idx in range(1, 13):
        base_lon = (sign_idx - 1) * 30.0
        for nav_idx in range(1, 10):
            test_lon = base_lon + (nav_idx - 1) * (10.0 / 3.0) + 1.0  # mid-navamsa
            res = calculate_navamsa_from_longitude(test_lon)
            if res["is_vargottama"]:
                vargottama_count += 1
                assert res["d1_sign_index"] == res["d9_sign_index"]
                
                # Check classical position
                if sign_idx in [1, 4, 7, 10]:  # Movable
                    assert nav_idx == 1, f"Movable sign {sign_idx} must be Vargottama at Navamsa 1"
                elif sign_idx in [2, 5, 8, 11]:  # Fixed
                    assert nav_idx == 5, f"Fixed sign {sign_idx} must be Vargottama at Navamsa 5"
                elif sign_idx in [3, 6, 9, 12]:  # Dual
                    assert nav_idx == 9, f"Dual sign {sign_idx} must be Vargottama at Navamsa 9"

    assert vargottama_count == 12, "There must be exactly 12 Vargottama zones across the 108 Navamsas"


# ============================================================================
# 4. PUSHKARA NAVAMSA TESTS (Jataka Parijata Ch. 1, Sloka 58)
# ============================================================================

def test_pushkara_navamsa_24_classical_positions():
    """Verify exactly 24 Pushkara Navamsas exist and all are ruled by natural benefics."""
    pushkara_count = 0
    benefic_signs = {2, 3, 4, 6, 7, 9, 12}  # Taurus, Gemini, Cancer, Virgo, Libra, Sagittarius, Pisces
    
    for sign_idx in range(1, 13):
        base_lon = (sign_idx - 1) * 30.0
        for nav_idx in range(1, 10):
            test_lon = base_lon + (nav_idx - 1) * (10.0 / 3.0) + 1.0
            res = calculate_navamsa_from_longitude(test_lon)
            if res["is_pushkara_navamsa"]:
                pushkara_count += 1
                assert res["d9_sign_index"] in benefic_signs, f"Pushkara Navamsa at sign {sign_idx} nav {nav_idx} must be benefic ruled"
                
                # Verify classical definitions:
                if sign_idx in [1, 5, 9]:
                    assert nav_idx in [7, 9], f"Fire sign {sign_idx} Pushkara must be 7 or 9"
                elif sign_idx in [2, 6, 10]:
                    assert nav_idx in [3, 5], f"Earth sign {sign_idx} Pushkara must be 3 or 5"
                elif sign_idx in [3, 7, 11]:
                    assert nav_idx in [6, 8], f"Air sign {sign_idx} Pushkara must be 6 or 8"
                elif sign_idx in [4, 8, 12]:
                    assert nav_idx in [1, 3], f"Water sign {sign_idx} Pushkara must be 1 or 3"

    assert pushkara_count == 24, "There must be exactly 24 Pushkara Navamsas across the 108 Navamsas"


# ============================================================================
# 5. CANONICAL REFERENCE CHART INTEGRATION TEST
# ============================================================================

def test_canonical_reference_chart_d1_d9():
    """Calculates canonical chart (Chennai, 1990-05-15 14:30:00 IST) and verifies D1 and D9."""
    full_horo = calculate_full_horoscope(
        birth_date="1990-05-15",
        birth_time="14:30:00",
        timezone_str="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ayanamsa_id=0,
        house_system_id=0,
        include_varga=True,
    )

    assert full_horo.varga_d1_d9 is not None
    varga = full_horo.varga_d1_d9

    # Ascendant checks
    # Chennai 1990-05-15 14:30 IST Ascendant is Virgo (approx 150° + ~11° = ~161°)
    assert varga.ascendant.d1_sign_name == "Virgo"
    assert varga.ascendant.d1_sign_index == 6
    # D1 degree should be within Virgo
    assert 0.0 <= varga.ascendant.d1_degree_in_sign < 30.0
    # D9 Ascendant
    assert 1 <= varga.ascendant.d9_sign_index <= 12

    # Check planets count
    assert len(varga.planets) >= 9
    planet_map = {p.name: p for p in varga.planets}
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p_name in planet_map
        p = planet_map[p_name]
        assert 1 <= p.d1_sign_index <= 12
        assert 1 <= p.d9_sign_index <= 12
        assert 1 <= p.d1_house <= 12
        assert 1 <= p.d9_house <= 12
        assert 0.0 <= p.d1_degree_in_sign < 30.0
        assert 0.0 <= p.d9_degree_in_sign < 30.0

    # Chart formatting structures check
    assert "ascendant" in varga.d1_chart
    assert "planets" in varga.d1_chart
    assert "ascendant" in varga.d9_chart
    assert "planets" in varga.d9_chart
    assert varga.summary.total_vargottama_count == len(varga.summary.vargottama_planets)


# ============================================================================
# 6. FASTAPI ENDPOINT TESTS
# ============================================================================

def test_varga_post_ad_hoc_endpoint_success():
    """POST /api/v1/horoscope/varga/d1-d9 with valid birth data succeeds."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
    }
    resp = client.post("/api/v1/horoscope/varga/d1-d9", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "ascendant" in data
    assert "planets" in data
    assert "summary" in data
    assert "d1_chart" in data
    assert "d9_chart" in data
    assert data["ascendant"]["d1_sign_name"] == "Virgo"


def test_varga_post_ad_hoc_endpoint_validation_error():
    """POST /api/v1/horoscope/varga/d1-d9 with missing parameters returns 422."""
    payload = {
        "birth_date": "1990-05-15",
        # Missing birth_time, lat, lon
    }
    resp = client.post("/api/v1/horoscope/varga/d1-d9", json=payload)
    assert resp.status_code == 422


def test_varga_post_saved_horoscope_unauthenticated():
    """POST /api/v1/horoscope/varga/d1-d9 with saved_horoscope_id but no bearer token returns 401."""
    payload = {
        "saved_horoscope_id": "00000000-0000-0000-0000-000000000001",
    }
    resp = client.post("/api/v1/horoscope/varga/d1-d9", json=payload)
    assert resp.status_code == 401


def test_varga_get_saved_horoscope_unauthenticated():
    """GET /api/v1/horoscope/varga/d1-d9/{id} without token returns 401."""
    resp = client.get("/api/v1/horoscope/varga/d1-d9/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 401


def test_varga_calculate_endpoint_includes_varga():
    """POST /api/v1/horoscope/calculate includes varga_d1_d9 when requested."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
        "include_varga": True,
    }
    resp = client.post("/api/v1/horoscope/calculate", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "varga_d1_d9" in data
    assert data["varga_d1_d9"] is not None
    assert data["varga_d1_d9"]["ascendant"]["d1_sign_name"] == "Virgo"
