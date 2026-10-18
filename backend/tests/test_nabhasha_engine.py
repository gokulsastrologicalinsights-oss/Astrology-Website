"""Automated tests for Nabhasha Yoga calculation engine and API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.nabhasha_engine.detector import detect_nabhasha_yogas

client = TestClient(app)


def test_ashraya_rajju():
    """All 7 planets in Chara (Movable) signs: Aries(1), Cancer(4), Libra(7), Capricorn(10)."""
    # Lagna in Aries (1), planets in 1, 4, 7, 10
    planets = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 4},
        {"name": "Mars", "sign_index": 7},
        {"name": "Mercury", "sign_index": 10},
        {"name": "Jupiter", "sign_index": 1},
        {"name": "Venus", "sign_index": 4},
        {"name": "Saturn", "sign_index": 7},
        {"name": "Rahu", "sign_index": 2},  # Should be excluded
        {"name": "Ketu", "sign_index": 8},  # Should be excluded
    ]
    res = detect_nabhasha_yogas(planets, ascendant_sign_idx=1)
    yoga_names = [y.name for y in res.all_qualifying_yogas]
    assert "Rajju" in yoga_names
    assert res.distribution.distinct_signs_count == 4


def test_ashraya_musala():
    """All 7 planets in Sthira (Fixed) signs: Taurus(2), Leo(5), Scorpio(8), Aquarius(11)."""
    planets = [
        {"name": "Sun", "sign_index": 2},
        {"name": "Moon", "sign_index": 5},
        {"name": "Mars", "sign_index": 8},
        {"name": "Mercury", "sign_index": 11},
        {"name": "Jupiter", "sign_index": 2},
        {"name": "Venus", "sign_index": 5},
        {"name": "Saturn", "sign_index": 8},
    ]
    res = detect_nabhasha_yogas(planets, ascendant_sign_idx=1)
    yoga_names = [y.name for y in res.all_qualifying_yogas]
    assert "Musala" in yoga_names


def test_ashraya_nala():
    """All 7 planets in Dvisvabhava (Dual) signs: Gemini(3), Virgo(6), Sagittarius(9), Pisces(12)."""
    planets = [
        {"name": "Sun", "sign_index": 3},
        {"name": "Moon", "sign_index": 6},
        {"name": "Mars", "sign_index": 9},
        {"name": "Mercury", "sign_index": 12},
        {"name": "Jupiter", "sign_index": 3},
        {"name": "Venus", "sign_index": 6},
        {"name": "Saturn", "sign_index": 9},
    ]
    res = detect_nabhasha_yogas(planets, ascendant_sign_idx=1)
    yoga_names = [y.name for y in res.all_qualifying_yogas]
    assert "Nala" in yoga_names


def test_dala_mala_and_sarpa():
    """Mala: Benefics in Kendras, Malefics outside. Sarpa: Malefics in Kendras, Benefics outside."""
    # Mala test: Lagna Aries(1). Kendras are 1, 4, 7, 10.
    # Benefics: Moon, Mercury, Jupiter, Venus in 1, 4. Malefics: Sun, Mars, Saturn in 2, 3.
    planets_mala = [
        {"name": "Moon", "sign_index": 1},      # House 1 (Kendra)
        {"name": "Mercury", "sign_index": 4},   # House 4 (Kendra)
        {"name": "Jupiter", "sign_index": 7},   # House 7 (Kendra)
        {"name": "Venus", "sign_index": 10},    # House 10 (Kendra)
        {"name": "Sun", "sign_index": 2},       # House 2 (Panaphara)
        {"name": "Mars", "sign_index": 3},      # House 3 (Apoklima)
        {"name": "Saturn", "sign_index": 5},    # House 5 (Panaphara)
    ]
    res_mala = detect_nabhasha_yogas(planets_mala, ascendant_sign_idx=1)
    assert any(y.name == "Mala" for y in res_mala.all_qualifying_yogas)

    # Sarpa test: Malefics in Kendras, Benefics outside
    planets_sarpa = [
        {"name": "Sun", "sign_index": 1},       # House 1 (Kendra)
        {"name": "Mars", "sign_index": 4},      # House 4 (Kendra)
        {"name": "Saturn", "sign_index": 7},    # House 7 (Kendra)
        {"name": "Moon", "sign_index": 2},      # House 2 (Panaphara)
        {"name": "Mercury", "sign_index": 3},   # House 3 (Apoklima)
        {"name": "Jupiter", "sign_index": 5},   # House 5 (Panaphara)
        {"name": "Venus", "sign_index": 6},     # House 6 (Apoklima)
    ]
    res_sarpa = detect_nabhasha_yogas(planets_sarpa, ascendant_sign_idx=1)
    assert any(y.name == "Sarpa" for y in res_sarpa.all_qualifying_yogas)


def test_aakriti_shakata_and_vihaga():
    """Shakata (1 & 7 only), Vihaga (4 & 10 only)."""
    # Lagna Aries(1). Shakata: 1 and 7.
    planets_shakata = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 7},
        {"name": "Mars", "sign_index": 1},
        {"name": "Mercury", "sign_index": 7},
        {"name": "Jupiter", "sign_index": 1},
        {"name": "Venus", "sign_index": 7},
        {"name": "Saturn", "sign_index": 1},
    ]
    res_shakata = detect_nabhasha_yogas(planets_shakata, ascendant_sign_idx=1)
    assert any(y.name == "Shakata" for y in res_shakata.all_qualifying_yogas)
    assert res_shakata.primary_yoga.name == "Shakata"

    # Vihaga: 4 and 10 only
    planets_vihaga = [
        {"name": "Sun", "sign_index": 4},
        {"name": "Moon", "sign_index": 10},
        {"name": "Mars", "sign_index": 4},
        {"name": "Mercury", "sign_index": 10},
        {"name": "Jupiter", "sign_index": 4},
        {"name": "Venus", "sign_index": 10},
        {"name": "Saturn", "sign_index": 4},
    ]
    res_vihaga = detect_nabhasha_yogas(planets_vihaga, ascendant_sign_idx=1)
    assert any(y.name == "Vihaga" for y in res_vihaga.all_qualifying_yogas)


def test_aakriti_shringataka_and_hala():
    """Shringataka (1, 5, 9), Hala (2, 6, 10 or 3, 7, 11 or 4, 8, 12)."""
    # Lagna Aries(1). Shringataka: 1, 5, 9
    planets_shring = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 5},
        {"name": "Mars", "sign_index": 9},
        {"name": "Mercury", "sign_index": 1},
        {"name": "Jupiter", "sign_index": 5},
        {"name": "Venus", "sign_index": 9},
        {"name": "Saturn", "sign_index": 1},
    ]
    res_shring = detect_nabhasha_yogas(planets_shring, ascendant_sign_idx=1)
    assert any(y.name == "Shringataka" for y in res_shring.all_qualifying_yogas)

    # Hala: 2, 6, 10
    planets_hala = [
        {"name": "Sun", "sign_index": 2},
        {"name": "Moon", "sign_index": 6},
        {"name": "Mars", "sign_index": 10},
        {"name": "Mercury", "sign_index": 2},
        {"name": "Jupiter", "sign_index": 6},
        {"name": "Venus", "sign_index": 10},
        {"name": "Saturn", "sign_index": 2},
    ]
    res_hala = detect_nabhasha_yogas(planets_hala, ascendant_sign_idx=1)
    assert any(y.name == "Hala" for y in res_hala.all_qualifying_yogas)


def test_aakriti_kamala_and_vapi():
    """Kamala: 1, 4, 7, 10 occupied. Vapi: Panaphara or Apoklima only."""
    # Kamala: 1, 4, 7, 10
    planets_kamala = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 4},
        {"name": "Mars", "sign_index": 7},
        {"name": "Mercury", "sign_index": 10},
        {"name": "Jupiter", "sign_index": 1},
        {"name": "Venus", "sign_index": 4},
        {"name": "Saturn", "sign_index": 7},
    ]
    res_kamala = detect_nabhasha_yogas(planets_kamala, ascendant_sign_idx=1)
    assert any(y.name == "Kamala" for y in res_kamala.all_qualifying_yogas)
    assert res_kamala.primary_yoga.name == "Kamala"

    # Vapi: all in Panaphara (2, 5, 8, 11)
    planets_vapi = [
        {"name": "Sun", "sign_index": 2},
        {"name": "Moon", "sign_index": 5},
        {"name": "Mars", "sign_index": 8},
        {"name": "Mercury", "sign_index": 11},
        {"name": "Jupiter", "sign_index": 2},
        {"name": "Venus", "sign_index": 5},
        {"name": "Saturn", "sign_index": 8},
    ]
    res_vapi = detect_nabhasha_yogas(planets_vapi, ascendant_sign_idx=1)
    assert any(y.name == "Vapi" for y in res_vapi.all_qualifying_yogas)


def test_aakriti_continuous_four_houses():
    """Yupa (1-4), Ishu (4-7), Shakti (7-10), Danda (10-1)."""
    # Yupa: 1, 2, 3, 4
    planets_yupa = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 2},
        {"name": "Mars", "sign_index": 3},
        {"name": "Mercury", "sign_index": 4},
        {"name": "Jupiter", "sign_index": 1},
        {"name": "Venus", "sign_index": 2},
        {"name": "Saturn", "sign_index": 3},
    ]
    res_yupa = detect_nabhasha_yogas(planets_yupa, ascendant_sign_idx=1)
    assert any(y.name == "Yupa" for y in res_yupa.all_qualifying_yogas)

    # Ishu: 4, 5, 6, 7
    planets_ishu = [
        {"name": "Sun", "sign_index": 4},
        {"name": "Moon", "sign_index": 5},
        {"name": "Mars", "sign_index": 6},
        {"name": "Mercury", "sign_index": 7},
        {"name": "Jupiter", "sign_index": 4},
        {"name": "Venus", "sign_index": 5},
        {"name": "Saturn", "sign_index": 6},
    ]
    res_ishu = detect_nabhasha_yogas(planets_ishu, ascendant_sign_idx=1)
    assert any(y.name == "Ishu" for y in res_ishu.all_qualifying_yogas)

    # Shakti: 7, 8, 9, 10
    planets_shakti = [
        {"name": "Sun", "sign_index": 7},
        {"name": "Moon", "sign_index": 8},
        {"name": "Mars", "sign_index": 9},
        {"name": "Mercury", "sign_index": 10},
        {"name": "Jupiter", "sign_index": 7},
        {"name": "Venus", "sign_index": 8},
        {"name": "Saturn", "sign_index": 9},
    ]
    res_shakti = detect_nabhasha_yogas(planets_shakti, ascendant_sign_idx=1)
    assert any(y.name == "Shakti" for y in res_shakti.all_qualifying_yogas)

    # Danda: 10, 11, 12, 1
    planets_danda = [
        {"name": "Sun", "sign_index": 10},
        {"name": "Moon", "sign_index": 11},
        {"name": "Mars", "sign_index": 12},
        {"name": "Mercury", "sign_index": 1},
        {"name": "Jupiter", "sign_index": 10},
        {"name": "Venus", "sign_index": 11},
        {"name": "Saturn", "sign_index": 12},
    ]
    res_danda = detect_nabhasha_yogas(planets_danda, ascendant_sign_idx=1)
    assert any(y.name == "Danda" for y in res_danda.all_qualifying_yogas)


def test_aakriti_continuous_seven_houses():
    """Nauka (1-7), Kuta (4-10), Chhatra (7-1), Chapa (10-4)."""
    # Nauka: 1, 2, 3, 4, 5, 6, 7
    planets_nauka = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 2},
        {"name": "Mars", "sign_index": 3},
        {"name": "Mercury", "sign_index": 4},
        {"name": "Jupiter", "sign_index": 5},
        {"name": "Venus", "sign_index": 6},
        {"name": "Saturn", "sign_index": 7},
    ]
    res_nauka = detect_nabhasha_yogas(planets_nauka, ascendant_sign_idx=1)
    assert any(y.name == "Nauka" for y in res_nauka.all_qualifying_yogas)

    # Chhatra: 7, 8, 9, 10, 11, 12, 1
    planets_chhatra = [
        {"name": "Sun", "sign_index": 7},
        {"name": "Moon", "sign_index": 8},
        {"name": "Mars", "sign_index": 9},
        {"name": "Mercury", "sign_index": 10},
        {"name": "Jupiter", "sign_index": 11},
        {"name": "Venus", "sign_index": 12},
        {"name": "Saturn", "sign_index": 1},
    ]
    res_chhatra = detect_nabhasha_yogas(planets_chhatra, ascendant_sign_idx=1)
    assert any(y.name == "Chhatra" for y in res_chhatra.all_qualifying_yogas)


def test_aakriti_chakra_and_samudra():
    """Chakra: 1, 3, 5, 7, 9, 11. Samudra: 2, 4, 6, 8, 10, 12."""
    planets_chakra = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 3},
        {"name": "Mars", "sign_index": 5},
        {"name": "Mercury", "sign_index": 7},
        {"name": "Jupiter", "sign_index": 9},
        {"name": "Venus", "sign_index": 11},
        {"name": "Saturn", "sign_index": 1},
    ]
    res_chakra = detect_nabhasha_yogas(planets_chakra, ascendant_sign_idx=1)
    assert any(y.name == "Chakra" for y in res_chakra.all_qualifying_yogas)

    planets_samudra = [
        {"name": "Sun", "sign_index": 2},
        {"name": "Moon", "sign_index": 4},
        {"name": "Mars", "sign_index": 6},
        {"name": "Mercury", "sign_index": 8},
        {"name": "Jupiter", "sign_index": 10},
        {"name": "Venus", "sign_index": 12},
        {"name": "Saturn", "sign_index": 2},
    ]
    res_samudra = detect_nabhasha_yogas(planets_samudra, ascendant_sign_idx=1)
    assert any(y.name == "Samudra" for y in res_samudra.all_qualifying_yogas)


def test_sankhya_yogas_counts():
    """Test Sankhya Yogas from 1 to 7 distinct signs."""
    # Gola: 1 sign
    p_gola = [{"name": p, "sign_index": 3} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]
    assert any(y.name == "Gola" for y in detect_nabhasha_yogas(p_gola, 1).all_qualifying_yogas)

    # Yuga: 2 signs
    p_yuga = [
        {"name": "Sun", "sign_index": 3},
        {"name": "Moon", "sign_index": 3},
        {"name": "Mars", "sign_index": 3},
        {"name": "Mercury", "sign_index": 8},
        {"name": "Jupiter", "sign_index": 8},
        {"name": "Venus", "sign_index": 8},
        {"name": "Saturn", "sign_index": 8},
    ]
    assert any(y.name == "Yuga" for y in detect_nabhasha_yogas(p_yuga, 1).all_qualifying_yogas)

    # Veena: 7 distinct signs
    p_veena = [
        {"name": "Sun", "sign_index": 1},
        {"name": "Moon", "sign_index": 2},
        {"name": "Mars", "sign_index": 4},
        {"name": "Mercury", "sign_index": 6},
        {"name": "Jupiter", "sign_index": 8},
        {"name": "Venus", "sign_index": 10},
        {"name": "Saturn", "sign_index": 12},
    ]
    assert any(y.name == "Veena" for y in detect_nabhasha_yogas(p_veena, 1).all_qualifying_yogas)


def test_nabhasha_api_endpoint():
    """Test POST /api/v1/vedic/nabhasha endpoint."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 2,
    }
    response = client.post("/api/v1/vedic/nabhasha", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "primary_yoga" in data
    assert "all_qualifying_yogas" in data
    assert len(data["all_qualifying_yogas"]) >= 1
    assert data["primary_yoga"] is not None
    assert data["primary_yoga"]["is_primary"] is True
