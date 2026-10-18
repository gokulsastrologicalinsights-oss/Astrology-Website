"""Automated test suite for the Vedic Yoga Calculation Engine."""

import pytest
from app.services.yoga_engine import calculate_vedic_yogas
from app.services.yoga_engine.models import YogaChartContext
from app.schemas.horoscope import PlanetInfo, NakshatraDetail


def _make_dummy_nakshatra(name="Ashwini"):
    return NakshatraDetail(
        name=name,
        index=1,
        pada=1,
        lord="Ketu",
        deity="Ashvins"
    )


def _make_planet(name, sign_idx, lon, deg_in_sign=15.0, is_retrograde=False):
    return PlanetInfo(
        name=name,
        body_id=0,
        longitude=lon,
        latitude=0.0,
        distance_au=1.0,
        speed_deg_per_day=1.0,
        is_retrograde=is_retrograde,
        sign_index=sign_idx,
        sign_name="Sign",
        sign_name_tamil="ராசி",
        degree_in_sign=deg_in_sign,
        nakshatra=_make_dummy_nakshatra()
    )


class TestVedicYogaEngine:
    """Tests for individual and aggregated classical Vedic Yogas."""

    def test_gajakesari_positive_kendra_from_moon(self):
        # Aries Lagna (1)
        # Moon in Cancer (Sign 4, House 4)
        # Jupiter in Capricorn (Sign 10, House 10) -> 7th from Moon (Kendra!)
        planets = [
            _make_planet("Moon", 4, 95.0),
            _make_planet("Jupiter", 10, 275.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Mars", 1, 15.0),
            _make_planet("Mercury", 2, 35.0),
            _make_planet("Venus", 3, 65.0),
            _make_planet("Saturn", 5, 125.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        gaj = next((y for y in res.yogas if y.id == "gajakesari_yoga"), None)
        assert gaj is not None
        assert gaj.is_qualifying is True
        assert gaj.status == "Qualifying"
        assert "Moon" in gaj.planets_involved
        assert "Jupiter" in gaj.planets_involved

    def test_gajakesari_negative_non_kendra(self):
        # Moon in Aries (Sign 1, House 1)
        # Jupiter in Taurus (Sign 2, House 2) -> 2nd from Moon (Not Kendra)
        planets = [
            _make_planet("Moon", 1, 10.0),
            _make_planet("Jupiter", 2, 40.0),
            _make_planet("Sun", 3, 70.0),
            _make_planet("Mars", 6, 160.0),
            _make_planet("Mercury", 8, 220.0),
            _make_planet("Venus", 12, 340.0),
            _make_planet("Saturn", 3, 80.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        gaj = next((y for y in res.yogas if y.id == "gajakesari_yoga"), None)
        assert gaj is not None
        assert gaj.is_qualifying is False
        assert gaj.status == "Not Qualifying"

    def test_budha_aditya_conjunction_and_combustion(self):
        # Sun and Mercury in Gemini (Sign 3)
        # Degree difference 2 deg -> combust
        planets = [
            _make_planet("Sun", 3, 65.0, deg_in_sign=5.0),
            _make_planet("Mercury", 3, 67.0, deg_in_sign=7.0),
            _make_planet("Moon", 1, 10.0),
            _make_planet("Mars", 2, 40.0),
            _make_planet("Jupiter", 5, 130.0),
            _make_planet("Venus", 6, 160.0),
            _make_planet("Saturn", 9, 250.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ba = next((y for y in res.yogas if y.id == "budha_aditya_yoga"), None)
        assert ba is not None
        assert ba.is_qualifying is True
        # Condition 2 checks combustion notice
        assert any("combustion" in c.condition.lower() for c in ba.conditions)

    def test_chandra_mangala_yoga(self):
        # Moon and Mars in Taurus (Sign 2)
        planets = [
            _make_planet("Moon", 2, 40.0),
            _make_planet("Mars", 2, 45.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Mercury", 3, 70.0),
            _make_planet("Jupiter", 4, 100.0),
            _make_planet("Venus", 5, 130.0),
            _make_planet("Saturn", 6, 160.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        cm = next((y for y in res.yogas if y.id == "chandra_mangala_yoga"), None)
        assert cm is not None
        assert cm.is_qualifying is True
        assert cm.category == "Dhana Yoga"

    def test_panch_mahapurusha_all_five(self):
        # Chart with all 5 Mahapurusha planets in Kendra own/exaltation
        # Aries Lagna (1)
        # Mars in Capricorn (Sign 10, House 10, Exalted) -> Ruchaka
        # Mercury in Virgo (Sign 6, House 6? No, in Gemini Sign 3 House 3? No, let's put in Virgo with Gemini Lagna!)
        # Let's test them with specific Lagnas:
        # Aries Lagna:
        # Mars in Aries (1, own) -> Ruchaka
        # Saturn in Libra (7, exalted) -> Shasha
        # Jupiter in Cancer (4, exalted) -> Hamsa
        # Venus in Libra (7, own) -> Malavya
        planets = [
            _make_planet("Mars", 1, 15.0),          # House 1, own sign Aries -> Ruchaka
            _make_planet("Jupiter", 4, 105.0),      # House 4, exalted Cancer -> Hamsa
            _make_planet("Saturn", 7, 195.0),       # House 7, exalted Libra -> Shasha
            _make_planet("Venus", 7, 205.0),        # House 7, own Libra -> Malavya
            _make_planet("Mercury", 6, 165.0),      # House 6, Virgo -> Not Kendra from Aries
            _make_planet("Sun", 5, 135.0),
            _make_planet("Moon", 2, 45.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ruchaka = next(y for y in res.yogas if y.id == "ruchaka_yoga")
        hamsa = next(y for y in res.yogas if y.id == "hamsa_yoga")
        sasa = next(y for y in res.yogas if y.id == "sasa_yoga")
        malavya = next(y for y in res.yogas if y.id == "malavya_yoga")
        bhadra = next(y for y in res.yogas if y.id == "bhadra_yoga")

        assert ruchaka.is_qualifying is True
        assert hamsa.is_qualifying is True
        assert sasa.is_qualifying is True
        assert malavya.is_qualifying is True
        assert bhadra.is_qualifying is False # In 6th, not Kendra

    def test_dharma_karmadhipati_yoga(self):
        # Aries Lagna (1)
        # 9th Lord = Jupiter (rules Sagittarius, Sign 9)
        # 10th Lord = Saturn (rules Capricorn, Sign 10)
        # Place Jupiter and Saturn in Leo (Sign 5, 5th house) conjunct
        planets = [
            _make_planet("Jupiter", 5, 130.0),
            _make_planet("Saturn", 5, 135.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 1, 20.0),
            _make_planet("Mercury", 2, 45.0),
            _make_planet("Venus", 3, 75.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dk = next(y for y in res.yogas if y.id == "dharma_karmadhipati_yoga")
        assert dk.is_qualifying is True
        assert dk.status == "Qualifying"

    def test_neecha_bhanga_raja_yoga_cancellation(self):
        # Aries Lagna (1)
        # Sun is debilitated in Libra (Sign 7, 7th house)
        # Dispositor of Libra is Venus.
        # Place Venus in Aries (House 1, Kendra from Lagna!) -> Cancels Sun's debilitation!
        planets = [
            _make_planet("Sun", 7, 190.0),          # Debilitated in Libra
            _make_planet("Venus", 1, 15.0),         # Dispositor in Kendra House 1
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 1, 25.0),
            _make_planet("Mercury", 8, 220.0),
            _make_planet("Jupiter", 9, 250.0),
            _make_planet("Saturn", 11, 310.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next((y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_sun"), None)
        assert nbry is not None
        assert nbry.is_qualifying is True
        assert nbry.status == "Qualifying"

    def test_vipareeta_raja_yogas(self):
        # Aries Lagna (1)
        # 6th lord = Mercury (rules Virgo, 6)
        # 8th lord = Mars (rules Scorpio, 8)
        # 12th lord = Jupiter (rules Pisces, 12)
        # Place Mercury in 8th (Scorpio, Sign 8) -> Harsha Yoga!
        # Place Mars in 6th (Virgo, Sign 6) -> Sarala Yoga!
        # Place Jupiter in 12th (Pisces, Sign 12) -> Vimala Yoga!
        planets = [
            _make_planet("Mercury", 8, 220.0),
            _make_planet("Mars", 6, 160.0),
            _make_planet("Jupiter", 12, 340.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 2, 40.0),
            _make_planet("Venus", 3, 70.0),
            _make_planet("Saturn", 4, 100.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        harsha = next(y for y in res.yogas if y.id == "harsha_yoga")
        sarala = next(y for y in res.yogas if y.id == "sarala_yoga")
        vimala = next(y for y in res.yogas if y.id == "vimala_yoga")

        assert harsha.is_qualifying is True
        assert sarala.is_qualifying is True
        assert vimala.is_qualifying is True

    def test_kemadruma_and_bhanga_cancellation(self):
        # Moon in Aries (Sign 1, House 1).
        # 2nd from Moon (Taurus, Sign 2) and 12th from Moon (Pisces, Sign 12) are empty.
        # But Jupiter is in House 4 (Cancer, Kendra from Lagna)!
        # Kemadruma is formed, but cancelled by planets in Kendra from Lagna!
        planets = [
            _make_planet("Moon", 1, 15.0),
            _make_planet("Jupiter", 4, 105.0),      # Kendra from Lagna
            _make_planet("Sun", 5, 135.0),
            _make_planet("Mars", 7, 195.0),         # Kendra from Lagna
            _make_planet("Mercury", 5, 140.0),
            _make_planet("Venus", 6, 165.0),
            _make_planet("Saturn", 8, 225.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        kema = next(y for y in res.yogas if y.id == "kemadruma_yoga")
        assert kema.status == "Cancelled"
        assert kema.is_qualifying is False
        assert kema.cancellation_reason is not None

    def test_sakata_and_bhanga_cancellation(self):
        # Moon in Virgo (Sign 6, House 6)
        # Jupiter in Aries (Sign 1, House 1) -> Moon is 6th from Jupiter (Sakata formation)
        # But Moon in House 6 is NOT Kendra from Lagna. So Sakata qualifies!
        planets_uncancelled = [
            _make_planet("Jupiter", 1, 15.0),
            _make_planet("Moon", 6, 165.0),
            _make_planet("Sun", 2, 45.0),
            _make_planet("Mars", 3, 75.0),
            _make_planet("Mercury", 2, 50.0),
            _make_planet("Venus", 4, 105.0),
            _make_planet("Saturn", 5, 135.0),
        ]
        res1 = calculate_vedic_yogas(planets_uncancelled, ascendant_sign_idx=1)
        sakata1 = next(y for y in res1.yogas if y.id == "sakata_yoga")
        assert sakata1.status == "Qualifying"
        assert sakata1.is_qualifying is True

        # Now Moon in Cancer (House 4, Kendra from Lagna)
        # Jupiter in Aquarius (Sign 11, House 11) -> Moon is 6th from Jupiter
        # Because Moon is in House 4 (Kendra from Lagna), Sakata is cancelled!
        planets_cancelled = [
            _make_planet("Jupiter", 11, 315.0),
            _make_planet("Moon", 4, 105.0),         # Kendra from Lagna
            _make_planet("Sun", 2, 45.0),
            _make_planet("Mars", 3, 75.0),
            _make_planet("Mercury", 2, 50.0),
            _make_planet("Venus", 8, 225.0),
            _make_planet("Saturn", 9, 255.0),
        ]
        res2 = calculate_vedic_yogas(planets_cancelled, ascendant_sign_idx=1)
        sakata2 = next(y for y in res2.yogas if y.id == "sakata_yoga")
        assert sakata2.status == "Cancelled"
        assert sakata2.is_qualifying is False
        assert "Lagna" in sakata2.cancellation_reason

    def test_parivartana_maha_exchange(self):
        # Aries Lagna (1)
        # 1st lord is Mars (owns Aries 1 and Scorpio 8)
        # 5th lord is Sun (owns Leo 5)
        # Exchange: Mars in Leo (Sign 5) and Sun in Aries (Sign 1)
        planets = [
            _make_planet("Mars", 5, 130.0),
            _make_planet("Sun", 1, 15.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mercury", 2, 40.0),
            _make_planet("Jupiter", 9, 250.0),
            _make_planet("Venus", 3, 70.0),
            _make_planet("Saturn", 11, 310.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        maha = next((y for y in res.yogas if "maha_parivartana" in y.id), None)
        assert maha is not None
        assert maha.is_qualifying is True
        assert "Mars" in maha.planets_involved
        assert "Sun" in maha.planets_involved

    def test_dhana_yoga_2_11_lords(self):
        # Aries Lagna (1)
        # 2nd lord = Venus (Taurus)
        # 11th lord = Saturn (Aquarius)
        # Conjoin Venus and Saturn in 11th house (Aquarius, Sign 11)
        planets = [
            _make_planet("Venus", 11, 310.0),
            _make_planet("Saturn", 11, 315.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 2, 40.0),
            _make_planet("Mercury", 3, 70.0),
            _make_planet("Jupiter", 9, 250.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dy = next(y for y in res.yogas if y.id == "dhana_yoga_2_11")
        assert dy.is_qualifying is True
        assert dy.category == "Dhana Yoga"

    def test_vasumathi_yoga_corrected(self):
        # All 3 benefics (Jupiter, Venus, Mercury) in Upachayas (3, 6, 10, 11) from Lagna
        # Aries Lagna (1):
        # Mercury in Gemini (House 3, Upachaya)
        # Jupiter in Virgo (House 6, Upachaya)
        # Venus in Capricorn (House 10, Upachaya)
        planets = [
            _make_planet("Mercury", 3, 70.0),
            _make_planet("Jupiter", 6, 160.0),
            _make_planet("Venus", 10, 280.0),
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 2, 40.0),
            _make_planet("Saturn", 8, 220.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        vasu = next(y for y in res.yogas if y.id == "vasumathi_yoga")
        assert vasu.is_qualifying is True
        assert vasu.status == "Qualifying"

    def test_summary_counts_integrity(self):
        planets = [
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 10, 280.0),
            _make_planet("Mercury", 1, 15.0),
            _make_planet("Jupiter", 4, 105.0),
            _make_planet("Venus", 7, 200.0),
            _make_planet("Saturn", 7, 205.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        assert res.summary.total_evaluated > 20
        assert res.summary.total_qualifying > 0
        assert (
            res.summary.raja_yogas_count
            + res.summary.dhana_yogas_count
            + res.summary.mahapurusha_yogas_count
            + res.summary.vipareeta_yogas_count
            + res.summary.other_classical_count
        ) >= res.summary.total_qualifying


def test_vedic_yogas_endpoint():
    """Test POST /api/v1/vedic/yogas endpoint via FastAPI TestClient."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
        "include_panchang": False,
        "include_outer_planets": False,
        "include_nabhasha": False,
        "include_ashtakavarga": False,
        "include_vedic_yogas": True,
        "gender": "male"
    }
    response = client.post("/api/v1/vedic/yogas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "yogas" in data
    assert data["summary"]["total_evaluated"] > 0
    assert len(data["yogas"]) == data["summary"]["total_evaluated"]


def test_full_horoscope_includes_vedic_yogas():
    """Test that POST /api/v1/horoscope/calculate includes vedic_yogas in response."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    payload = {
        "birth_date": "1995-10-25",
        "birth_time": "08:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "ayanamsa": 0,
        "house_system": 0,
        "include_panchang": True,
        "include_outer_planets": True,
        "include_nabhasha": True,
        "include_ashtakavarga": True,
        "include_vedic_yogas": True,
    }
    response = client.post("/api/v1/horoscope/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "vedic_yogas" in data
    assert data["vedic_yogas"] is not None
    assert data["vedic_yogas"]["summary"]["total_qualifying"] >= 0

