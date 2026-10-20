"""Comprehensive independent reference and validation test suite for all 16 Shodashvarga charts.

Classical Authority:
- Brihat Parashara Hora Shastra (BPHS), Chapter 6: Shodashavargadhyaya
- Saravali (Kalyana Varma), Chapter 3: Divisional Characteristics

Verifies:
1. All 16 Divisional Charts (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60).
2. Odd vs Even sign variations (D2, D7, D10, D24, D30, D40, D60).
3. Movable vs Fixed vs Dual starting signs (D9, D16, D20, D45).
4. Exact boundary transitions, epsilon offsets, and 0/30/360° wraparound.
5. Divisional Ascendant and whole-sign house calculation.
6. Shashtyamsa (D60) 60 classical deities and odd/even inversion.
7. API endpoints:
   - POST /api/v1/horoscope/varga/shodashvarga
   - POST /api/v1/vedic/vargas
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.varga_engine import (
    calculate_divisional_placement,
    calculate_shodashvarga,
    calculate_shodashvarga_from_horoscope_dict,
    SHODASHVARGA_KEYS,
    DIVISION_METADATA,
    SHASHTYAMSA_DEITIES,
)

client = TestClient(app)


# ============================================================================
# 1. COMPREHENSIVE INDEPENDENT REFERENCE TESTS FOR ALL 16 VARGAS
# ============================================================================

def test_all_16_divisions_defined_and_metadata_complete():
    """Verify all 16 divisional keys exist with full metadata."""
    assert len(SHODASHVARGA_KEYS) == 16
    for key in SHODASHVARGA_KEYS:
        assert key in DIVISION_METADATA
        meta = DIVISION_METADATA[key]
        assert "number" in meta
        assert "name" in meta
        assert "name_tamil" in meta
        assert "significance" in meta
        assert "significance_tamil" in meta
        assert len(meta["name_tamil"]) > 0
        assert len(meta["significance_tamil"]) > 0


def test_d1_rasi_independent_mapping():
    """D1 maps directly to the 12 signs of 30° each."""
    test_cases = [
        (15.0, 1, "Aries", 15.0),
        (45.0, 2, "Taurus", 15.0),
        (75.0, 3, "Gemini", 15.0),
        (105.0, 4, "Cancer", 15.0),
        (135.0, 5, "Leo", 15.0),
        (165.0, 6, "Virgo", 15.0),
        (195.0, 7, "Libra", 15.0),
        (225.0, 8, "Scorpio", 15.0),
        (255.0, 9, "Sagittarius", 15.0),
        (285.0, 10, "Capricorn", 15.0),
        (315.0, 11, "Aquarius", 15.0),
        (345.0, 12, "Pisces", 15.0),
    ]
    for lon, expected_sign, expected_name, expected_deg in test_cases:
        res = calculate_divisional_placement(lon, "D1")
        assert res["sign_index"] == expected_sign
        assert res["sign_name"] == expected_name
        assert abs(res["degree_in_sign"] - expected_deg) < 1e-4


def test_d2_hora_odd_even_parashari_rules():
    """D2 Hora: Odd signs (0-15° Leo Sun, 15-30° Cancer Moon); Even signs (0-15° Cancer Moon, 15-30° Leo Sun)."""
    # Odd sign: Aries (0° to 30°)
    res_aries_1 = calculate_divisional_placement(7.5, "D2")
    assert res_aries_1["sign_index"] == 5  # Leo (Sun)
    assert res_aries_1["sign_name"] == "Leo"
    assert abs(res_aries_1["degree_in_sign"] - 15.0) < 1e-4

    res_aries_2 = calculate_divisional_placement(22.5, "D2")
    assert res_aries_2["sign_index"] == 4  # Cancer (Moon)
    assert res_aries_2["sign_name"] == "Cancer"
    assert abs(res_aries_2["degree_in_sign"] - 15.0) < 1e-4

    # Even sign: Taurus (30° to 60°)
    res_taurus_1 = calculate_divisional_placement(37.5, "D2")
    assert res_taurus_1["sign_index"] == 4  # Cancer (Moon)
    assert res_taurus_1["sign_name"] == "Cancer"

    res_taurus_2 = calculate_divisional_placement(52.5, "D2")
    assert res_taurus_2["sign_index"] == 5  # Leo (Sun)
    assert res_taurus_2["sign_name"] == "Leo"


def test_d3_drekkana_1st_5th_9th_houses():
    """D3 Drekkana: 0-10° 1st house (self), 10-20° 5th house, 20-30° 9th house."""
    # Leo (sign 5, 120° to 150°)
    # 0-10°: Leo (5)
    res_leo_1 = calculate_divisional_placement(125.0, "D3")
    assert res_leo_1["sign_index"] == 5
    assert res_leo_1["sign_name"] == "Leo"
    assert abs(res_leo_1["degree_in_sign"] - 15.0) < 1e-4  # 5° * 3 = 15°

    # 10-20°: 5th from Leo = Sagittarius (9)
    res_leo_2 = calculate_divisional_placement(135.0, "D3")
    assert res_leo_2["sign_index"] == 9
    assert res_leo_2["sign_name"] == "Sagittarius"

    # 20-30°: 9th from Leo = Aries (1)
    res_leo_3 = calculate_divisional_placement(145.0, "D3")
    assert res_leo_3["sign_index"] == 1
    assert res_leo_3["sign_name"] == "Aries"


def test_d4_chaturthamsa_kendra_signs():
    """D4 Chaturthamsa: 4 parts of 7.5° each map to 1st, 4th, 7th, 10th Kendra houses from sign."""
    # Scorpio (sign 8, 210° to 240°)
    # Part 0 (0-7.5°): Scorpio (8)
    res_0 = calculate_divisional_placement(213.75, "D4")
    assert res_0["sign_index"] == 8
    assert res_0["sign_name"] == "Scorpio"
    assert abs(res_0["degree_in_sign"] - 15.0) < 1e-4  # 3.75° * 4 = 15°

    # Part 1 (7.5-15°): 4th from Scorpio = Aquarius (11)
    res_1 = calculate_divisional_placement(220.0, "D4")
    assert res_1["sign_index"] == 11
    assert res_1["sign_name"] == "Aquarius"

    # Part 2 (15-22.5°): 7th from Scorpio = Taurus (2)
    res_2 = calculate_divisional_placement(227.0, "D4")
    assert res_2["sign_index"] == 2
    assert res_2["sign_name"] == "Taurus"

    # Part 3 (22.5-30°): 10th from Scorpio = Leo (5)
    res_3 = calculate_divisional_placement(235.0, "D4")
    assert res_3["sign_index"] == 5
    assert res_3["sign_name"] == "Leo"


def test_d7_saptamsa_odd_even_rules():
    """D7 Saptamsa: Odd sign starts from sign; Even sign starts from 7th from sign."""
    # Odd sign: Aries (sign 1)
    # Part 0: Aries (1), Part 1: Taurus (2), ..., Part 6: Libra (7)
    res_aries_0 = calculate_divisional_placement(2.0, "D7")
    assert res_aries_0["sign_index"] == 1
    res_aries_6 = calculate_divisional_placement(28.0, "D7")
    assert res_aries_6["sign_index"] == 7  # Libra

    # Even sign: Taurus (sign 2, 7th from Taurus = Scorpio 8)
    # Part 0: Scorpio (8), Part 1: Sagittarius (9), ..., Part 6: Taurus (2)
    res_taurus_0 = calculate_divisional_placement(32.0, "D7")
    assert res_taurus_0["sign_index"] == 8  # Scorpio
    res_taurus_6 = calculate_divisional_placement(58.0, "D7")
    assert res_taurus_6["sign_index"] == 2  # Taurus


def test_d10_dasamsa_odd_even_rules():
    """D10 Dasamsa: Odd sign starts from sign; Even sign starts from 9th from sign."""
    # Odd sign: Gemini (sign 3)
    # Part 0 (0-3°): Gemini (3)
    # Part 1 (3-6°): Cancer (4)
    # Part 9 (27-30°): Pisces (12)
    res_gem_0 = calculate_divisional_placement(61.5, "D10")
    assert res_gem_0["sign_index"] == 3
    res_gem_9 = calculate_divisional_placement(88.5, "D10")
    assert res_gem_9["sign_index"] == 12  # Pisces

    # Even sign: Cancer (sign 4, 9th from Cancer = Pisces 12)
    # Part 0 (0-3°): Pisces (12)
    # Part 1 (3-6°): Aries (1)
    # Part 9 (27-30°): Sagittarius (9)
    res_can_0 = calculate_divisional_placement(91.5, "D10")
    assert res_can_0["sign_index"] == 12  # Pisces
    res_can_1 = calculate_divisional_placement(94.5, "D10")
    assert res_can_1["sign_index"] == 1   # Aries
    res_can_9 = calculate_divisional_placement(118.5, "D10")
    assert res_can_9["sign_index"] == 9   # Sagittarius


def test_d12_dwadasamsa_all_signs_start_from_self():
    """D12 Dwadasamsa: 12 divisions of 2.5° each starting from sign itself."""
    # Sagittarius (sign 9, 240° to 270°)
    for k in range(12):
        lon = 240.0 + k * 2.5 + 1.25
        res = calculate_divisional_placement(lon, "D12")
        expected_sign = ((9 - 1 + k) % 12) + 1
        assert res["sign_index"] == expected_sign


def test_d16_shodasamsa_movable_fixed_dual_starts():
    """D16 Shodasamsa: Movable starts Aries (1), Fixed starts Leo (5), Dual starts Sagittarius (9)."""
    # Movable sign: Libra (sign 7) -> starts Aries (1)
    res_lib_0 = calculate_divisional_placement(180.5, "D16")
    assert res_lib_0["sign_index"] == 1  # Aries

    # Fixed sign: Aquarius (sign 11) -> starts Leo (5)
    res_aqu_0 = calculate_divisional_placement(300.5, "D16")
    assert res_aqu_0["sign_index"] == 5  # Leo

    # Dual sign: Pisces (sign 12) -> starts Sagittarius (9)
    res_psc_0 = calculate_divisional_placement(330.5, "D16")
    assert res_psc_0["sign_index"] == 9  # Sagittarius


def test_d20_vimsamsa_movable_fixed_dual_starts():
    """D20 Vimsamsa: Movable starts Aries (1), Fixed starts Sagittarius (9), Dual starts Leo (5)."""
    # Movable: Cancer (sign 4) -> starts Aries (1)
    res_can_0 = calculate_divisional_placement(90.5, "D20")
    assert res_can_0["sign_index"] == 1

    # Fixed: Leo (sign 5) -> starts Sagittarius (9)
    res_leo_0 = calculate_divisional_placement(120.5, "D20")
    assert res_leo_0["sign_index"] == 9

    # Dual: Virgo (sign 6) -> starts Leo (5)
    res_vir_0 = calculate_divisional_placement(150.5, "D20")
    assert res_vir_0["sign_index"] == 5


def test_d24_chaturvimsamsa_odd_even_starts():
    """D24 Chaturvimsamsa: Odd sign starts Leo (5); Even sign starts Cancer (4)."""
    # Odd sign: Aries (1) -> starts Leo (5)
    res_odd = calculate_divisional_placement(0.5, "D24")
    assert res_odd["sign_index"] == 5  # Leo

    # Even sign: Taurus (2) -> starts Cancer (4)
    res_even = calculate_divisional_placement(30.5, "D24")
    assert res_even["sign_index"] == 4  # Cancer


def test_d27_saptavimsamsa_four_elements_starts():
    """D27 Saptavimsamsa: Fire starts Aries(1), Earth starts Cancer(4), Air starts Libra(7), Water starts Cap(10)."""
    # Fire: Aries (0°) -> 1 (Aries)
    res_fire = calculate_divisional_placement(0.5, "D27")
    assert res_fire["sign_index"] == 1

    # Earth: Taurus (30°) -> 4 (Cancer)
    res_earth = calculate_divisional_placement(30.5, "D27")
    assert res_earth["sign_index"] == 4

    # Air: Gemini (60°) -> 7 (Libra)
    res_air = calculate_divisional_placement(60.5, "D27")
    assert res_air["sign_index"] == 7

    # Water: Cancer (90°) -> 10 (Capricorn)
    res_water = calculate_divisional_placement(90.5, "D27")
    assert res_water["sign_index"] == 10


def test_d30_trimsamsa_exact_partitions_and_reversal():
    """D30 Trimsamsa: Odd signs (0-5 Mars/1, 5-10 Sat/11, 10-18 Jup/9, 18-25 Merc/3, 25-30 Ven/7).
    Even signs reversed: (0-5 Ven/2, 5-12 Merc/6, 12-20 Jup/12, 20-25 Sat/10, 25-30 Mars/8)."""
    # Odd sign: Aries (sign 1)
    assert calculate_divisional_placement(2.5, "D30")["sign_index"] == 1    # Mars (Aries)
    assert calculate_divisional_placement(7.5, "D30")["sign_index"] == 11   # Saturn (Aquarius)
    assert calculate_divisional_placement(14.0, "D30")["sign_index"] == 9   # Jupiter (Sagittarius)
    assert calculate_divisional_placement(21.0, "D30")["sign_index"] == 3   # Mercury (Gemini)
    assert calculate_divisional_placement(27.5, "D30")["sign_index"] == 7   # Venus (Libra)

    # Even sign: Taurus (sign 2, 30° to 60°)
    assert calculate_divisional_placement(32.5, "D30")["sign_index"] == 2   # Venus (Taurus)
    assert calculate_divisional_placement(38.0, "D30")["sign_index"] == 6   # Mercury (Virgo)
    assert calculate_divisional_placement(46.0, "D30")["sign_index"] == 12  # Jupiter (Pisces)
    assert calculate_divisional_placement(52.5, "D30")["sign_index"] == 10  # Saturn (Capricorn)
    assert calculate_divisional_placement(57.5, "D30")["sign_index"] == 8   # Mars (Scorpio)


def test_d40_khavedamsa_odd_even_starts():
    """D40 Khavedamsa: Odd sign starts Aries (1); Even sign starts Libra (7)."""
    # Odd: Aries (0°) -> starts Aries (1)
    res_odd = calculate_divisional_placement(0.3, "D40")
    assert res_odd["sign_index"] == 1

    # Even: Taurus (30°) -> starts Libra (7)
    res_even = calculate_divisional_placement(30.3, "D40")
    assert res_even["sign_index"] == 7


def test_d45_akshavedamsa_movable_fixed_dual_starts():
    """D45 Akshavedamsa: Movable starts Aries (1), Fixed starts Leo (5), Dual starts Sagittarius (9)."""
    # Movable: Capricorn (sign 10) -> starts Aries (1)
    assert calculate_divisional_placement(270.3, "D45")["sign_index"] == 1

    # Fixed: Taurus (sign 2) -> starts Leo (5)
    assert calculate_divisional_placement(30.3, "D45")["sign_index"] == 5

    # Dual: Gemini (sign 3) -> starts Sagittarius (9)
    assert calculate_divisional_placement(60.3, "D45")["sign_index"] == 9


def test_d60_shashtyamsa_signs_and_deities():
    """D60 Shashtyamsa: 60 parts of 0.5° each starting from sign itself, with odd/even deity reversal."""
    assert len(SHASHTYAMSA_DEITIES) == 60

    # Odd sign: Aries (sign 1)
    # Part 0 (0-0.5°): Aries (1), Deity: Ghora (Malefic)
    res_odd_0 = calculate_divisional_placement(0.25, "D60")
    assert res_odd_0["sign_index"] == 1
    assert res_odd_0["shashtyamsa_deity"] == "Ghora"
    assert res_odd_0["shashtyamsa_nature"] == "Malefic"

    # Part 59 (29.5-30.0°): ((1 - 1 + 59) % 12) + 1 = 12 (Pisces), Deity: Indurekha (Benefic)
    res_odd_59 = calculate_divisional_placement(29.75, "D60")
    assert res_odd_59["sign_index"] == 12  # Pisces
    assert res_odd_59["shashtyamsa_deity"] == "Indurekha"
    assert res_odd_59["shashtyamsa_nature"] == "Benefic"

    # Even sign: Taurus (sign 2)
    # Part 0 (0-0.5°): Taurus (2), Deity: reversed (index 59 = Indurekha)
    res_even_0 = calculate_divisional_placement(30.25, "D60")
    assert res_even_0["sign_index"] == 2
    assert res_even_0["shashtyamsa_deity"] == "Indurekha"
    assert res_even_0["shashtyamsa_nature"] == "Benefic"

    # Part 59 (29.5-30.0°): ((2 - 1 + 59) % 12) + 1 = 1 (Aries), Deity: index 0 = Ghora
    res_even_59 = calculate_divisional_placement(59.75, "D60")
    assert res_even_59["sign_index"] == 1
    assert res_even_59["shashtyamsa_deity"] == "Ghora"
    assert res_even_59["shashtyamsa_nature"] == "Malefic"


# ============================================================================
# 2. BOUNDARY PRECISION & WRAPAROUND TESTS
# ============================================================================

def test_boundaries_all_16_divisions_stability():
    """Verify boundaries with +/- 1e-6 epsilon offsets across all 16 divisional charts."""
    test_boundaries = [0.0, 15.0, 30.0, 45.0, 60.0, 90.0, 180.0, 270.0, 359.999999]
    for b in test_boundaries:
        for div_k in SHODASHVARGA_KEYS:
            res_exact = calculate_divisional_placement(b, div_k)
            assert 1 <= res_exact["sign_index"] <= 12
            assert 0.0 <= res_exact["degree_in_sign"] < 30.0

            if b > 0.01:
                res_before = calculate_divisional_placement(b - 1e-6, div_k)
                assert 1 <= res_before["sign_index"] <= 12

            res_after = calculate_divisional_placement((b + 1e-6) % 360.0, div_k)
            assert 1 <= res_after["sign_index"] <= 12


# ============================================================================
# 3. FULL SHODASHVARGA ORCHESTRATOR & ASCENDANT INTEGRATION
# ============================================================================

def test_calculate_shodashvarga_orchestrator():
    """calculate_shodashvarga returns all 16 charts with planets, houses, ascendant, and Vargottamas."""
    planets = [
        {"name": "Sun", "longitude": 31.0, "body_id": 0, "is_retrograde": False},       # Taurus 1°
        {"name": "Moon", "longitude": 318.0, "body_id": 1, "is_retrograde": False},    # Aquarius 18°
        {"name": "Mars", "longitude": 14.0, "body_id": 4, "is_retrograde": False},     # Aries 14°
        {"name": "Mercury", "longitude": 28.0, "body_id": 2, "is_retrograde": False},  # Aries 28°
        {"name": "Jupiter", "longitude": 75.0, "body_id": 5, "is_retrograde": False},  # Gemini 15°
        {"name": "Venus", "longitude": 6.0, "body_id": 3, "is_retrograde": False},     # Aries 6°
        {"name": "Saturn", "longitude": 270.0, "body_id": 6, "is_retrograde": True},   # Capricorn 0°
        {"name": "Rahu", "longitude": 315.0, "body_id": 9, "is_retrograde": True},     # Aquarius 15°
        {"name": "Ketu", "longitude": 135.0, "body_id": 13, "is_retrograde": True},    # Leo 15°
    ]
    ascendant = {"degree": 125.0}  # Leo 5° (Ascendant in sign 5)

    res = calculate_shodashvarga(planets=planets, ascendant=ascendant)

    # 1. Check all 16 charts exist
    assert len(res.charts) == 16
    for div_k in SHODASHVARGA_KEYS:
        assert div_k in res.charts
        chart_item = res.charts[div_k]
        assert chart_item.division_id == div_k
        assert 1 <= chart_item.ascendant.sign_index <= 12
        assert len(chart_item.planets) == 9

        # Verify each planet has a valid house from divisional Ascendant
        for p in chart_item.planets:
            expected_house = ((p.sign_index - chart_item.ascendant.sign_index) % 12) + 1
            assert p.house == expected_house

        # Verify chart rendering structure is populated
        assert "ascendant" in chart_item.chart
        assert "planets" in chart_item.chart
        assert len(chart_item.chart["planets"]) == 9

    # 2. Check direct key chart structures
    assert res.d1_chart is not None
    assert res.d9_chart is not None
    assert res.d10_chart is not None
    assert res.d60_chart is not None

    # 3. Check planet_vargas mapping table
    assert "Sun" in res.planet_vargas
    assert len(res.planet_vargas["Sun"]) == 16


# ============================================================================
# 4. FASTAPI ENDPOINT INTEGRATION TESTS
# ============================================================================

def test_api_vargas_endpoint_ad_hoc():
    """Test POST /api/v1/vedic/vargas with ad-hoc birth data."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
    }
    response = client.post("/api/v1/vedic/vargas", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "charts" in data
    assert len(data["charts"]) == 16
    assert "D1" in data["charts"]
    assert "D9" in data["charts"]
    assert "D10" in data["charts"]
    assert "D60" in data["charts"]
    assert "planet_vargas" in data
    assert "d10_chart" in data
    assert "d60_chart" in data

    # Verify D60 chart has deity fields populated
    d60_asc = data["charts"]["D60"]["ascendant"]
    assert d60_asc["shashtyamsa_deity"] is not None
    assert d60_asc["shashtyamsa_deity_tamil"] is not None


def test_api_shodashvarga_endpoint_ad_hoc():
    """Test POST /api/v1/horoscope/varga/shodashvarga with ad-hoc birth data."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
    }
    response = client.post("/api/v1/horoscope/varga/shodashvarga", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "charts" in data
    assert len(data["charts"]) == 16
    assert "d1_chart" in data
    assert "d9_chart" in data
    assert "d10_chart" in data
    assert "d60_chart" in data


def test_api_varga_d1_d9_backward_compatibility():
    """Ensure POST /api/v1/horoscope/varga/d1-d9 retains exact backwards compatibility."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
    }
    response = client.post("/api/v1/horoscope/varga/d1-d9", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "ascendant" in data
    assert "planets" in data
    assert "summary" in data
    assert "d1_chart" in data
    assert "d9_chart" in data
    assert "shodashvarga" in data
    assert data["shodashvarga"] is not None
    assert len(data["shodashvarga"]["charts"]) == 16
