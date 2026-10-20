"""Automated tests for Shadbala (Six-fold Planetary Strength) engine and API endpoints.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 23.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.horoscope import (
    AscendantInfo,
    HouseInfo,
    NakshatraDetail,
    PanchangInfo,
    PlanetInfo,
    TithiInfo,
    YogaInfo,
)
from app.schemas.shadbala import SHADBALA_REQUIRED_VIRUPAS
from app.services.shadbala_engine.calculator import NAISARGIKA_BALA, calculate_shadbala
from app.services.shadbala_engine.cheshta_bala import calc_cheshta_bala
from app.services.shadbala_engine.dig_bala import calc_dig_bala
from app.services.shadbala_engine.kala_bala import (
    calc_abda_bala,
    calc_ayana_bala,
    calc_hora_bala,
    calc_masa_bala,
    calc_nathonnatha_bala,
    calc_paksha_bala,
    calc_tribhaga_bala,
    calc_vara_bala,
)
from app.services.shadbala_engine.models import (
    AscendantCtx,
    BirthCtx,
    ChartCtx,
    HouseCtx,
    PlanetCtx,
)
from app.services.shadbala_engine.sthana_bala import (
    calc_drekkana_bala,
    calc_kendradi_bala,
    calc_ojhayugma_bala,
    calc_saptavargaja_bala,
    calc_uchcha_bala,
)

client = TestClient(app)


def _make_dummy_nakshatra(name: str = "Ashwini", lord: str = "Ketu") -> NakshatraDetail:
    return NakshatraDetail(
        name=name,
        index=1,
        pada=1,
        lord=lord,
        deity="Ashvins",
    )


def _make_sample_chart_data():
    """Create a standard test chart with all 7 planets + Ascendant + 12 houses."""
    nak = _make_dummy_nakshatra()

    planets = [
        PlanetInfo(
            name="Sun", body_id=0, longitude=10.0, latitude=0.0, distance_au=1.0,
            speed_deg_per_day=1.0, is_retrograde=False, sign_index=1,
            sign_name="Aries", sign_name_tamil="மேஷம்", degree_in_sign=10.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Moon", body_id=1, longitude=45.0, latitude=1.0, distance_au=0.0025,
            speed_deg_per_day=13.2, is_retrograde=False, sign_index=2,
            sign_name="Taurus", sign_name_tamil="ரிஷபம்", degree_in_sign=15.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Mars", body_id=4, longitude=298.0, latitude=0.5, distance_au=1.5,
            speed_deg_per_day=-0.2, is_retrograde=True, sign_index=10,
            sign_name="Capricorn", sign_name_tamil="மகரம்", degree_in_sign=28.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Mercury", body_id=2, longitude=165.0, latitude=0.1, distance_au=1.1,
            speed_deg_per_day=1.4, is_retrograde=False, sign_index=6,
            sign_name="Virgo", sign_name_tamil="கன்னி", degree_in_sign=15.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Jupiter", body_id=5, longitude=95.0, latitude=0.2, distance_au=5.2,
            speed_deg_per_day=0.08, is_retrograde=False, sign_index=4,
            sign_name="Cancer", sign_name_tamil="கடகம்", degree_in_sign=5.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Venus", body_id=3, longitude=357.0, latitude=-0.3, distance_au=0.72,
            speed_deg_per_day=1.1, is_retrograde=False, sign_index=12,
            sign_name="Pisces", sign_name_tamil="மீனம்", degree_in_sign=27.0,
            nakshatra=nak,
        ),
        PlanetInfo(
            name="Saturn", body_id=6, longitude=200.0, latitude=-1.2, distance_au=9.5,
            speed_deg_per_day=-0.04, is_retrograde=True, sign_index=7,
            sign_name="Libra", sign_name_tamil="துலாம்", degree_in_sign=20.0,
            nakshatra=nak,
        ),
        # Rahu & Ketu should be ignored
        PlanetInfo(
            name="Rahu", body_id=9, longitude=120.0, latitude=0.0, distance_au=0.0,
            speed_deg_per_day=-0.05, is_retrograde=True, sign_index=5,
            sign_name="Leo", sign_name_tamil="சிம்மம்", degree_in_sign=0.0,
            nakshatra=nak,
        ),
    ]

    ascendant = AscendantInfo(
        degree=15.0,
        sign_index=1,
        sign_name="Aries",
        sign_name_tamil="மேஷம்",
        degree_in_sign=15.0,
        nakshatra=nak,
    )

    houses = [
        HouseInfo(
            house_number=i,
            cusp_degree=float((i - 1) * 30),
            sign_index=i,
            sign_name=f"Sign_{i}",
            sign_name_tamil=f"ராசி_{i}",
            degree_in_sign=0.0,
            nakshatra="Ashwini",
            pada=1,
            star_lord="Ketu",
        )
        for i in range(1, 13)
    ]

    panchang = PanchangInfo(
        tithi=TithiInfo(number=3, name="Tritiya", paksha="Shukla"),
        nakshatra="Rohini",
        yoga=YogaInfo(number=2, name="Priti"),
        karana="Kaulava",
        vara="Ravivara",
    )

    return planets, ascendant, houses, panchang


# ---------------------------------------------------------------------------
# Unit tests for individual Balas
# ---------------------------------------------------------------------------

def test_uchcha_bala_exact_exaltation_and_debilitation():
    """Verify Uchcha Bala yields exactly 60 at exaltation and 0 at debilitation."""
    # Sun exalted at 10° Aries (lon = 10.0)
    p_exalt = PlanetCtx("Sun", 0, 10.0, 10.0, 1, 1.0, False, "Ketu")
    assert pytest.approx(calc_uchcha_bala(p_exalt), 0.01) == 60.0

    # Sun debilitated at 10° Libra (lon = 190.0)
    p_debil = PlanetCtx("Sun", 0, 190.0, 10.0, 7, 1.0, False, "Rahu")
    assert pytest.approx(calc_uchcha_bala(p_debil), 0.01) == 0.0

    # Mars exalted at 28° Capricorn (lon = 298.0)
    p_mars_exalt = PlanetCtx("Mars", 4, 298.0, 28.0, 10, 0.5, False, "Sun")
    assert pytest.approx(calc_uchcha_bala(p_mars_exalt), 0.01) == 60.0


def test_naisargika_bala_fixed_classical_values():
    """Verify fixed Naisargika Bala values correspond exactly to BPHS Ch. 23."""
    expected = {
        "Sun": 60.00,
        "Moon": 51.43,
        "Venus": 42.86,
        "Jupiter": 34.29,
        "Mercury": 25.71,
        "Mars": 17.14,
        "Saturn": 8.57,
    }
    for planet, val in expected.items():
        assert NAISARGIKA_BALA[planet] == val


def test_dig_bala_best_and_worst_houses():
    """Verify Dig Bala achieves 60 at optimal direction and 0 at opposite direction."""
    houses = [HouseCtx(i, i) for i in range(1, 13)]
    asc = AscendantCtx(15.0, 1, 15.0)
    birth = BirthCtx("2000-01-01", "12:00", "UTC", 0.0, 0.0)

    # Ascendant = 15°. h10 (South) = 285°, h4 (North) = 105°, h7 (West) = 195°, h1 (East) = 15°
    # Sun best in 10th (285°) -> 60 virupas; worst in 4th (105°) -> 0 virupas
    p_sun_10 = PlanetCtx("Sun", 0, 285.0, 15.0, 10, 1.0, False, "Mars")
    ctx_sun_10 = ChartCtx([p_sun_10], houses, asc, birth, "Ravivara", 285.0, 0.0, True)
    assert calc_dig_bala(p_sun_10, ctx_sun_10) == 60.0

    p_sun_4 = PlanetCtx("Sun", 0, 105.0, 15.0, 4, 1.0, False, "Saturn")
    ctx_sun_4 = ChartCtx([p_sun_4], houses, asc, birth, "Ravivara", 105.0, 0.0, False)
    assert calc_dig_bala(p_sun_4, ctx_sun_4) == 0.0

    # Jupiter best in 1st (15°) -> 60 virupas; worst in 7th (195°) -> 0 virupas
    p_jup_1 = PlanetCtx("Jupiter", 5, 15.0, 15.0, 1, 0.08, False, "Ketu")
    ctx_jup_1 = ChartCtx([p_jup_1], houses, asc, birth, "Ravivara", 0.0, 0.0, True)
    assert calc_dig_bala(p_jup_1, ctx_jup_1) == 60.0

    # Saturn best in 7th (195°) -> 60 virupas; worst in 1st (15°) -> 0 virupas
    p_sat_7 = PlanetCtx("Saturn", 6, 195.0, 15.0, 7, 0.03, False, "Rahu")
    ctx_sat_7 = ChartCtx([p_sat_7], houses, asc, birth, "Ravivara", 0.0, 0.0, True)
    assert calc_dig_bala(p_sat_7, ctx_sat_7) == 60.0

    # Venus best in 4th (105°) -> 60 virupas; worst in 10th (285°) -> 0 virupas
    p_ven_4 = PlanetCtx("Venus", 3, 105.0, 15.0, 4, 1.0, False, "Moon")
    ctx_ven_4 = ChartCtx([p_ven_4], houses, asc, birth, "Ravivara", 0.0, 0.0, True)
    assert calc_dig_bala(p_ven_4, ctx_ven_4) == 60.0



def test_cheshta_bala_rules():
    """Verify Cheshta Bala rules for retrograde planets and luminaries."""
    # Retrograde planet gets 60
    p_retro = PlanetCtx("Mars", 4, 100.0, 10.0, 4, -0.2, True, "Saturn")
    assert calc_cheshta_bala(p_retro) == 60.0

    # Sun and Moon always get 30
    p_sun = PlanetCtx("Sun", 0, 10.0, 10.0, 1, 1.0, False, "Ketu")
    p_moon = PlanetCtx("Moon", 1, 45.0, 15.0, 2, 13.0, False, "Venus")
    assert calc_cheshta_bala(p_sun) == 30.0
    assert calc_cheshta_bala(p_moon) == 30.0


def test_kala_bala_nathonnatha():
    """Verify Nathonnatha Bala assigns 60 to diurnal grahas by day and nocturnal grahas by night."""
    houses = [HouseCtx(i, i) for i in range(1, 13)]
    asc = AscendantCtx(0.0, 1, 0.0)
    birth = BirthCtx("2000-01-01", "12:00", "UTC", 0.0, 0.0)

    p_sun = PlanetCtx("Sun", 0, 0.0, 0.0, 1, 1.0, False, "")
    p_moon = PlanetCtx("Moon", 1, 0.0, 0.0, 1, 13.0, False, "")
    p_merc = PlanetCtx("Mercury", 2, 0.0, 0.0, 1, 1.0, False, "")

    # Day birth: Sun, Jupiter, Venus get 60; Moon, Mars, Saturn get 0; Mercury gets 30
    ctx_day = ChartCtx([p_sun, p_moon, p_merc], houses, asc, birth, "Ravivara", 0.0, 0.0, True)
    assert calc_nathonnatha_bala(p_sun, ctx_day) == 60.0
    assert calc_nathonnatha_bala(p_moon, ctx_day) == 0.0
    assert calc_nathonnatha_bala(p_merc, ctx_day) == 30.0

    # Night birth
    ctx_night = ChartCtx([p_sun, p_moon, p_merc], houses, asc, birth, "Ravivara", 0.0, 0.0, False)
    assert calc_nathonnatha_bala(p_sun, ctx_night) == 0.0
    assert calc_nathonnatha_bala(p_moon, ctx_night) == 60.0
    assert calc_nathonnatha_bala(p_merc, ctx_night) == 30.0


# ---------------------------------------------------------------------------
# Master Orchestrator Invariant Tests
# ---------------------------------------------------------------------------

def test_shadbala_returns_exact_seven_classical_planets():
    """Verify exactly 7 planets are returned and Rahu/Ketu are excluded."""
    planets, ascendant, houses, panchang = _make_sample_chart_data()
    response = calculate_shadbala(
        planets=planets,
        ascendant=ascendant,
        houses=houses,
        panchang=panchang,
    )
    returned_names = [p.planet for p in response.planets]
    assert len(returned_names) == 7
    expected = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert set(returned_names) == expected
    assert "Rahu" not in returned_names
    assert "Ketu" not in returned_names


def test_shadbala_mathematical_consistency():
    """Verify sum of components equals total virupas, rupas = virupas/60, ratio = total/required."""
    planets, ascendant, houses, panchang = _make_sample_chart_data()
    response = calculate_shadbala(
        planets=planets,
        ascendant=ascendant,
        houses=houses,
        panchang=panchang,
    )

    for p in response.planets:
        # 1. Total virupas == sum of six component balas
        expected_total = (
            p.sthana_bala.total
            + p.dig_bala
            + p.kala_bala.total
            + p.cheshta_bala
            + p.naisargika_bala
            + p.drik_bala
        )
        assert pytest.approx(p.total_virupas, 0.01) == expected_total

        # 2. Total rupas == total_virupas / 60
        assert pytest.approx(p.total_rupas, 0.01) == (p.total_virupas / 60.0)

        # 3. Ratio == total_virupas / required_virupas
        expected_ratio = p.total_virupas / p.required_virupas
        assert pytest.approx(p.ratio, 0.01) == expected_ratio

        # 4. is_strong boolean flag
        assert p.is_strong == (p.ratio >= 1.0)

        # 5. Required virupas matches canonical dictionary
        assert p.required_virupas == SHADBALA_REQUIRED_VIRUPAS[p.planet]


def test_shadbala_ranking_integrity():
    """Verify ranks are unique 1-7 and correctly ordered by total virupas descending."""
    planets, ascendant, houses, panchang = _make_sample_chart_data()
    response = calculate_shadbala(
        planets=planets,
        ascendant=ascendant,
        houses=houses,
        panchang=panchang,
    )

    ranks = [p.rank for p in response.planets]
    assert set(ranks) == {1, 2, 3, 4, 5, 6, 7}

    # Verify descending ordering
    totals = [p.total_virupas for p in response.planets]
    assert totals == sorted(totals, reverse=True)

    # Strongest planet is rank 1, weakest is rank 7
    assert response.strongest_planet == response.planets[0].planet
    assert response.weakest_planet == response.planets[-1].planet


# ---------------------------------------------------------------------------
# API Integration Tests
# ---------------------------------------------------------------------------

def test_shadbala_api_endpoint():
    """Verify POST /api/v1/vedic/shadbala returns HTTP 200 and valid schema."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
        "include_panchang": True,
        "gender": "male",
    }
    response = client.post("/api/v1/vedic/shadbala", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "planets" in data
    assert len(data["planets"]) == 7
    assert "strongest_planet" in data
    assert "weakest_planet" in data
    assert len(data["calculation_notes"]) > 0

    # Validate individual planet fields
    for p in data["planets"]:
        assert "planet" in p
        assert "sthana_bala" in p
        assert "dig_bala" in p
        assert "kala_bala" in p
        assert "cheshta_bala" in p
        assert "naisargika_bala" in p
        assert "drik_bala" in p
        assert "total_virupas" in p
        assert "total_rupas" in p
        assert "ratio" in p
        assert "is_strong" in p
        assert "rank" in p
        assert 1 <= p["rank"] <= 7


def test_metadata_endpoint_includes_shadbala():
    """Verify GET /api/v1/metadata exposes Shadbala capability and removes draft status."""
    resp = client.get("/api/v1/metadata")
    assert resp.status_code == 200
    data = resp.json()

    # Capability present
    cap_ids = [c["id"] for c in data["chart_capabilities"]]
    assert "shadbala_planetary_strength" in cap_ids

    # Limitations updated (no mention of Shadbala in draft status)
    for lim in data["limitations"]:
        assert "Shadbala" not in lim


def test_rules_inventory_includes_shadbala_rule():
    """Verify GET /api/v1/rules/inventory includes RULE-SHADBALA-01 with Implemented status."""
    resp = client.get("/api/v1/rules/inventory")
    assert resp.status_code == 200
    data = resp.json()

    rule_ids = [r["rule_id"] for r in data]
    assert "RULE-SHADBALA-01" in rule_ids

    shadbala_rule = next(r for r in data if r["rule_id"] == "RULE-SHADBALA-01")
    assert shadbala_rule["status"] == "Implemented"
    assert "app/services/shadbala_engine" in shadbala_rule["documentation_ref"]


# ---------------------------------------------------------------------------
# Independent Reference Tests with Pre-established Expected Values
# ---------------------------------------------------------------------------

def test_saptavargaja_bala_classical_compound_dignities():
    """Verify exact 7-varga positions and Panchadha Maitri scoring for an independently calculated case."""
    # Saturn at Capricorn 1°31'34" (lon = 271.5261)
    # D1 = Capricorn (Own sign = 30)
    # D2 = Cancer (Even sign, 0-15° = Moon/Cancer)
    # D3 = Capricorn (0-10° = same sign = Own sign = 30)
    # D7 = Cancer (Even sign, part 0 = 7th from Cap = Cancer)
    # D9 = Capricorn (Earthy sign, part 0 = Capricorn = Own sign = 30)
    # D12 = Capricorn (Part 0 = Capricorn = Own sign = 30)
    # D30 = Taurus (Even sign, 0-5° = Venus/Taurus)
    saturn = PlanetCtx("Saturn", 6, 271.5261, 1.5261, 10, -0.0168, True, "Sun")
    moon = PlanetCtx("Moon", 1, 271.8948, 1.8948, 10, 12.33, False, "Sun")
    venus = PlanetCtx("Venus", 3, 348.9502, 18.9502, 12, 1.14, False, "Mercury")
    houses = [HouseCtx(i, i) for i in range(1, 13)]
    asc = AscendantCtx(154.4, 6, 4.4)
    birth = BirthCtx("1990-05-15", "14:30:00", "Asia/Kolkata", 13.08, 80.27)
    ctx = ChartCtx([saturn, moon, venus], houses, asc, birth, "Mangalavara", 30.55, 271.89, True)

    score = calc_saptavargaja_bala(saturn, ctx)
    # Four own-sign placements (D1, D3, D9, D12) yield 4 * 30 = 120 virupas minimum
    assert score >= 120.0
    assert pytest.approx(score, 0.01) == 146.25


def test_ayana_bala_solstitial_extremes():
    """Verify Ayana Bala reaches maximum near Summer Solstice and minimum near Winter Solstice."""
    houses = [HouseCtx(i, i) for i in range(1, 13)]
    asc = AscendantCtx(0.0, 1, 0.0)
    birth = BirthCtx("2000-06-21", "12:00:00", "UTC", 0.0, 0.0)

    # Sun at ~66.15° sidereal (approx 90° Sayana, Summer Solstice, declination ~+23.44°)
    p_sun_summer = PlanetCtx("Sun", 0, 66.15, 6.15, 3, 1.0, False, "Rahu")
    ctx_summer = ChartCtx([p_sun_summer], houses, asc, birth, "Ravivara", 66.15, 0.0, True)
    ayana_summer = calc_ayana_bala(p_sun_summer, ctx_summer)
    assert ayana_summer > 55.0  # Near maximum 60 virupas

    # Sun at ~246.15° sidereal (approx 270° Sayana, Winter Solstice, declination ~-23.44°)
    p_sun_winter = PlanetCtx("Sun", 0, 246.15, 6.15, 9, 1.0, False, "Ketu")
    ctx_winter = ChartCtx([p_sun_winter], houses, asc, birth, "Ravivara", 246.15, 0.0, True)
    ayana_winter = calc_ayana_bala(p_sun_winter, ctx_winter)
    assert ayana_winter < 5.0  # Near minimum 0 virupas


def test_independent_reference_chart_chennai_1990():
    """Independently verified benchmark test for reference birth: Chennai, 1990-05-15 14:30 IST."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
        "include_panchang": True,
        "gender": "male",
    }
    response = client.post("/api/v1/vedic/shadbala", json=payload)
    assert response.status_code == 200
    data = response.json()

    # 1. Classical strength expectation:
    # Jupiter (exalted in D12/D30, Kendra 10th, maximum Ayana Bala 58.87) is rank 1
    # Venus (exalted in D1 Pisces, Kendra 7th, Diurnal Day) is rank 2
    assert data["strongest_planet"] in ("Jupiter", "Venus")

    # 2. All 7 planets have total virupas in realistic BPHS range (300 to 600)
    for p in data["planets"]:
        assert 300.0 <= p["total_virupas"] <= 600.0
        assert p["ratio"] > 0.0
        assert p["total_rupas"] == pytest.approx(p["total_virupas"] / 60.0, 0.01)

    # 3. Exactly 7 planets, ranked 1 through 7
    ranks = [p["rank"] for p in data["planets"]]
    assert ranks == [1, 2, 3, 4, 5, 6, 7]


