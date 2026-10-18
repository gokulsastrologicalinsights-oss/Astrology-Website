"""Independent mathematical validation and real horoscope data verification for Vedic Yoga Engine."""

import pytest
from app.services.ephemeris import calculate_full_horoscope
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


def _make_planet(name: str, sign_idx: int, lon: float, deg_in_sign: float = 15.0, retro: bool = False):
    return PlanetInfo(
        name=name,
        body_id=0,
        longitude=lon,
        latitude=0.0,
        distance_au=1.0,
        speed_deg_per_day=1.0,
        is_retrograde=retro,
        sign_index=sign_idx,
        sign_name="Sign",
        sign_name_tamil="ராசி",
        degree_in_sign=deg_in_sign,
        nakshatra=_make_dummy_nakshatra()
    )


class TestRealHoroscopeAndMathematicalVerification:
    """Rigorous end-to-end tests validating classical mathematics against real and canonical charts."""

    def test_real_chart_chennai_1990(self):
        """Verify real chart: 1990-05-15, 14:30:00, Asia/Kolkata, Chennai (13.0827° N, 80.2707° E)."""
        from datetime import date, time
        horoscope = calculate_full_horoscope(
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30, 0),
            timezone_str="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
            ayanamsa_id=0,  # Lahiri
            house_system_id=2,  # Placidus
            include_vedic_yogas=True,
        )

        assert horoscope.vedic_yogas is not None
        yogas = horoscope.vedic_yogas.yogas
        summary = horoscope.vedic_yogas.summary

        # Check Ascendant
        assert horoscope.ascendant.sign_name == "Virgo"
        assert horoscope.ascendant.sign_index == 6

        # Check planetary placements in Rasi:
        # Virgo Lagna (Sign 6, House 1)
        planets_by_name = {p.name: p for p in horoscope.planets}
        sun = planets_by_name["Sun"]
        moon = planets_by_name["Moon"]
        mars = planets_by_name["Mars"]
        merc = planets_by_name["Mercury"]
        jup = planets_by_name["Jupiter"]
        ven = planets_by_name["Venus"]
        sat = planets_by_name["Saturn"]

        # Sun is in Taurus (Sign 2, House 9 from Virgo)
        assert sun.sign_index == 2
        # Moon is in Capricorn (Sign 10, House 5 from Virgo)
        assert moon.sign_index == 10
        # Mars is in Aquarius (Sign 11, House 6 from Virgo)
        assert mars.sign_index == 11
        # Mercury is in Aries (Sign 1, House 8 from Virgo)
        assert merc.sign_index == 1
        # Jupiter is in Gemini (Sign 3, House 10 from Virgo)
        assert jup.sign_index == 3
        # Venus is in Pisces (Sign 12, House 7 from Virgo - Exalted!)
        assert ven.sign_index == 12
        # Saturn is in Capricorn (Sign 10, House 5 from Virgo, retrograde in own sign!)
        assert sat.sign_index == 10

        # --- Independent Mathematical Yoga Derivations for this chart: ---

        # 1. Malavya Yoga (Panch Mahapurusha):
        # Venus is in Pisces (House 7, a Kendra from Virgo Lagna!). Pisces is Venus's EXALTATION sign!
        # Therefore, Venus MUST qualify for Malavya Yoga!
        malavya = next(y for y in yogas if y.id == "malavya_yoga")
        assert malavya.is_qualifying is True
        assert malavya.status == "Qualifying"

        # 2. Gajakesari Yoga:
        # Moon is in Capricorn (Sign 10, House 5).
        # Jupiter is in Gemini (Sign 3, House 10).
        # Distance from Moon (House 5) to Jupiter (House 10) = ((10 - 5) % 12) + 1 = 6 (6th house from Moon - Dusthana!).
        # Distance from Moon is 6, which is NOT a Kendra from Moon.
        # Therefore, Gajakesari Yoga must NOT qualify!
        gajakesari = next(y for y in yogas if y.id == "gajakesari_yoga")
        assert gajakesari.is_qualifying is False
        assert gajakesari.status == "Not Qualifying"

        # 3. Sakata Yoga:
        # Distance from Jupiter (House 10) to Moon (House 5) = ((5 - 10) % 12) + 1 = 8 (8th house from Jupiter!).
        # Moon is 8th from Jupiter -> Classical Sakata formation!
        # Cancellation: Is Moon in a Kendra (1, 4, 7, 10) from Lagna?
        # Moon is in House 5 (Trikona, not Kendra!).
        # Therefore, Sakata is NOT cancelled and qualifies!
        sakata = next(y for y in yogas if y.id == "sakata_yoga")
        assert sakata.is_qualifying is True
        assert sakata.status == "Qualifying"

        # 4. Sunapha / Anapha / Kemadruma:
        # Moon is in Capricorn (House 5).
        # 2nd from Moon = House 6 (Aquarius). Mars is in House 6!
        # Because Mars (valid graha) is in the 2nd from Moon, Sunapha Yoga MUST qualify!
        sunapha = next(y for y in yogas if y.id == "sunapha_yoga")
        assert sunapha.is_qualifying is True
        # And because 2nd from Moon is occupied, Kemadruma does NOT form!
        kemadruma = next(y for y in yogas if y.id == "kemadruma_yoga")
        assert kemadruma.is_qualifying is False
        assert kemadruma.status == "Not Qualifying"

        # 5. Harsha / Sarala / Vimala (Vipareeta Raja):
        # Virgo Lagna: 6th house is Aquarius (lord Saturn).
        # Saturn is in Sagittarius (House 4, NOT Dusthana). Harsha = False.
        # 8th house is Aries (lord Mars).
        # Mars is in Aquarius (House 6, a Dusthana!).
        # Therefore, Sarala Yoga (8th lord in 6th) MUST qualify!
        sarala = next(y for y in yogas if y.id == "sarala_yoga")
        assert sarala.is_qualifying is True
        assert sarala.status == "Qualifying"

        # 6. Summary metrics integrity
        assert summary.total_qualifying > 0
        assert summary.mahapurusha_yogas_count >= 1  # Malavya
        assert summary.vipareeta_yogas_count >= 1    # Sarala

    def test_navamsa_exaltation_nbry(self):
        """Test Neecha Bhanga Raja Yoga through Navamsa (D9) Exaltation."""
        # Mars is debilitated in Cancer (Sign 4). Exaltation sign of Mars is Capricorn (Sign 10).
        # Cancer is a Water sign. Navamsas of Cancer:
        # 1: Cancer (4), 2: Leo (5), 3: Virgo (6), 4: Libra (7), 5: Scorpio (8), 6: Sagittarius (9), 7: Capricorn (10) -> 20°00' to 23°20' Cancer!
        # Longitude in Cancer: 3 signs * 30 + 21.0° = 111.0° longitude.
        mars_lon = 111.0  # 21° Cancer
        planets = [
            _make_planet("Mars", 4, mars_lon, deg_in_sign=21.0),
            _make_planet("Sun", 8, 235.0),
            _make_planet("Moon", 8, 230.0),
            _make_planet("Mercury", 8, 225.0),
            _make_planet("Jupiter", 8, 220.0),
            _make_planet("Venus", 8, 215.0),
            _make_planet("Saturn", 8, 210.0),
        ]
        # Place all dispositors in house 8 (non-kendra, no aspect) so only Navamsa condition can pass!
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry_mars = next((y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_mars"), None)
        assert nbry_mars is not None
        assert nbry_mars.is_qualifying is True
        assert nbry_mars.status == "Qualifying"
        assert any("Navamsha" in c.detail for c in nbry_mars.conditions if c.passed)

    def test_budha_aditya_combustion_distinction(self):
        """Test Budha-Aditya Yoga with deep combustion vs wide conjunction."""
        # Deep combustion: Sun at 40.0° (Taurus 10°), Mercury at 42.0° (Taurus 12°) -> diff = 2° (Combust!)
        planets_combust = [
            _make_planet("Sun", 2, 40.0, deg_in_sign=10.0),
            _make_planet("Mercury", 2, 42.0, deg_in_sign=12.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 5, 130.0),
            _make_planet("Jupiter", 7, 190.0),
            _make_planet("Venus", 8, 220.0),
            _make_planet("Saturn", 9, 250.0),
        ]
        res1 = calculate_vedic_yogas(planets_combust, ascendant_sign_idx=1)
        ba1 = next(y for y in res1.yogas if y.id == "budha_aditya_yoga")
        assert ba1.is_qualifying is True
        combustion_cond1 = next(c for c in ba1.conditions if "Combustion" in c.condition)
        assert combustion_cond1.passed is False
        assert "within combustion orb" in combustion_cond1.detail

        # Beyond combustion: Sun at 32.0° (Taurus 2°), Mercury at 56.0° (Taurus 26°) -> diff = 24° (> 14°)
        planets_non_combust = [
            _make_planet("Sun", 2, 32.0, deg_in_sign=2.0),
            _make_planet("Mercury", 2, 56.0, deg_in_sign=26.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 5, 130.0),
            _make_planet("Jupiter", 7, 190.0),
            _make_planet("Venus", 8, 220.0),
            _make_planet("Saturn", 9, 250.0),
        ]
        res2 = calculate_vedic_yogas(planets_non_combust, ascendant_sign_idx=1)
        ba2 = next(y for y in res2.yogas if y.id == "budha_aditya_yoga")
        assert ba2.is_qualifying is True
        combustion_cond2 = next(c for c in ba2.conditions if "Combustion" in c.condition)
        assert combustion_cond2.passed is True
        assert "beyond combustion orb" in combustion_cond2.detail

    def test_dainya_parivartana_dusthana_exchange(self):
        """Test Parivartana between 2nd house lord (Venus) and 8th house lord (Mars)."""
        # Aries Lagna: House 2 = Taurus (Venus), House 8 = Scorpio (Mars).
        # Exchange: Venus in Scorpio (Sign 8, House 8) and Mars in Taurus (Sign 2, House 2).
        planets = [
            _make_planet("Venus", 8, 220.0),  # In Scorpio (Mars's sign)
            _make_planet("Mars", 2, 45.0),    # In Taurus (Venus's sign)
            _make_planet("Sun", 1, 10.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mercury", 3, 70.0),
            _make_planet("Jupiter", 9, 250.0),
            _make_planet("Saturn", 11, 310.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dainya = next((y for y in res.yogas if "dainya_parivartana" in y.id), None)
        assert dainya is not None
        assert dainya.is_qualifying is True
        assert dainya.category == "Parivartana"
        assert "Venus" in dainya.planets_involved
        assert set(dainya.relevant_houses) == {2, 8}

    def test_canonical_multi_mahapurusha_chart(self):
        """Test canonical classical chart with multiple Mahapurusha and Raja Yogas.
        Cancer Lagna (Sign 4, House 1):
        - Jupiter in Cancer (Sign 4, House 1, Exalted) -> Hamsa Yoga, Lagna Lord
        - Moon in Cancer (Sign 4, House 1, Own Sign) -> Gajakesari Yoga (Jupiter conjunct Moon)
        - Mars in Capricorn (Sign 10, House 7, Exalted) -> Ruchaka Yoga (in Kendra!)
        - Saturn in Libra (Sign 7, House 4, Exalted) -> Shasha Yoga (in Kendra!)
        - Venus in Pisces (Sign 12, House 9, Exalted) -> 9th house Trikona
        - Sun in Aries (Sign 1, House 10, Exalted) -> 10th house Kendra
        - Mercury in Gemini (Sign 3, House 12, Own Sign)
        """
        planets = [
            _make_planet("Jupiter", 4, 95.0),    # Exalted in House 1 (Hamsa)
            _make_planet("Moon", 4, 105.0),      # House 1 (Gajakesari with Jup)
            _make_planet("Mars", 10, 280.0),     # Exalted in House 7 (Ruchaka)
            _make_planet("Saturn", 7, 200.0),    # Exalted in House 4 (Shasha)
            _make_planet("Venus", 12, 345.0),    # Exalted in House 9
            _make_planet("Sun", 1, 10.0),        # Exalted in House 10
            _make_planet("Mercury", 3, 75.0),    # House 12
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=4)
        summary = res.summary

        # Check Mahapurusha Yogas
        hamsa = next(y for y in res.yogas if y.id == "hamsa_yoga")
        ruchaka = next(y for y in res.yogas if y.id == "ruchaka_yoga")
        shasha = next(y for y in res.yogas if y.id == "sasa_yoga")
        bhadra = next(y for y in res.yogas if y.id == "bhadra_yoga")
        malavya = next(y for y in res.yogas if y.id == "malavya_yoga")

        assert hamsa.is_qualifying is True
        assert ruchaka.is_qualifying is True
        assert shasha.is_qualifying is True
        assert bhadra.is_qualifying is False    # Mercury is in 12th house (not Kendra)
        assert malavya.is_qualifying is False   # Venus is in 9th house (not Kendra)

        # Check Gajakesari (Jupiter conjunct Moon in House 1)
        gajakesari = next(y for y in res.yogas if y.id == "gajakesari_yoga")
        assert gajakesari.is_qualifying is True

        # Check Dharma-Karmadhipati:
        # Cancer Lagna: 9th lord = Jupiter, 10th lord = Mars.
        # Jupiter in House 1 and Mars in House 7 cast 7th mutual aspects on each other!
        dk = next(y for y in res.yogas if y.id == "dharma_karmadhipati_yoga")
        assert dk.is_qualifying is True
        assert dk.status == "Qualifying"

        # Check Yogakaraka Mars for Cancer Lagna (Mars rules 5th and 10th):
        yk_mars = next(y for y in res.yogas if y.id == "yogakaraka_raja_yoga_mars")
        assert yk_mars.is_qualifying is True

        assert summary.mahapurusha_yogas_count == 3
        assert summary.raja_yogas_count >= 2

    def test_kemadruma_uncancelled_vs_cancelled(self):
        """Test Kemadruma Yoga: active when uncancelled, and cancelled by each classical rule."""
        # Uncancelled: Moon in Taurus (Sign 2, House 2), 2nd from Moon (House 3) and 12th from Moon (House 1) empty.
        # Kendras from Lagna: 1, 4, 7, 10 (all empty).
        # Kendras from Moon: 2, 5, 8, 11 (all empty).
        # Flanks of Moon: 1, 3 (empty).
        # Place all other planets in House 6 (Sign 6, Virgo) and House 9 (Sign 9, Sagittarius).
        # None aspect Moon in House 2!
        planets_active = [
            _make_planet("Moon", 2, 45.0),
            _make_planet("Sun", 6, 160.0),       # House 6
            _make_planet("Mars", 6, 165.0),      # House 6
            _make_planet("Mercury", 6, 170.0),   # House 6
            _make_planet("Saturn", 6, 175.0),    # House 6
            _make_planet("Jupiter", 9, 250.0),   # House 9 (aspects 1, 3, 5 - does not aspect 2!)
            _make_planet("Venus", 6, 180.0),     # House 6
        ]
        res1 = calculate_vedic_yogas(planets_active, ascendant_sign_idx=1)
        kema1 = next(y for y in res1.yogas if y.id == "kemadruma_yoga")
        assert kema1.is_qualifying is True
        assert kema1.status == "Qualifying"

        # Cancelled by Kendra from Lagna: Place Jupiter in 4th house (Sign 4, Cancer, Kendra from Lagna!)
        planets_cancelled_kendra = [
            _make_planet("Moon", 2, 45.0),
            _make_planet("Sun", 3, 75.0),
            _make_planet("Jupiter", 4, 105.0),   # House 4 (Kendra from Lagna -> Cancels!)
            _make_planet("Mars", 6, 165.0),
            _make_planet("Mercury", 6, 175.0),
            _make_planet("Venus", 8, 230.0),
            _make_planet("Saturn", 6, 170.0),
        ]
        res2 = calculate_vedic_yogas(planets_cancelled_kendra, ascendant_sign_idx=1)
        kema2 = next(y for y in res2.yogas if y.id == "kemadruma_yoga")
        assert kema2.is_qualifying is False
        assert kema2.status == "Cancelled"
        assert "Lagna" in kema2.cancellation_reason

    def test_yogakaraka_dignity_guard(self):
        """Test single-planet lordship guard: Saturn rules 9 and 10 for Taurus Lagna.
        Formation qualifies as Yogakaraka, while placement condition notes Dusthana or strong dignity.
        """
        # Taurus Lagna (Sign 2, House 1).
        # Saturn in Sagittarius (Sign 9, House 8 - Dusthana!)
        planets_dusthana = [
            _make_planet("Saturn", 9, 255.0),    # House 8 (Dusthana!)
            _make_planet("Sun", 1, 15.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 5, 130.0),
            _make_planet("Mercury", 2, 45.0),
            _make_planet("Jupiter", 3, 75.0),
            _make_planet("Venus", 11, 315.0),
        ]
        res_dusthana = calculate_vedic_yogas(planets_dusthana, ascendant_sign_idx=2)
        dk_dusthana = next(y for y in res_dusthana.yogas if y.id == "dharma_karmadhipati_yoga")
        assert dk_dusthana.is_qualifying is True
        assert dk_dusthana.status == "Qualifying"
        assert "Dusthana" in dk_dusthana.conditions[0].detail

        # Now place Saturn in Libra (Sign 7, House 6 - Exalted in 6th house!)
        # Exalted Yogakaraka must NOT be disqualified by a blanket 6th house rule!
        planets_exalted_in_6th = [
            _make_planet("Saturn", 7, 200.0),    # Exalted in Libra (House 6)
            _make_planet("Sun", 1, 15.0),
            _make_planet("Moon", 4, 100.0),
            _make_planet("Mars", 5, 130.0),
            _make_planet("Mercury", 2, 45.0),
            _make_planet("Jupiter", 3, 75.0),
            _make_planet("Venus", 12, 345.0),
        ]
        res_exalted = calculate_vedic_yogas(planets_exalted_in_6th, ascendant_sign_idx=2)
        dk_exalted = next(y for y in res_exalted.yogas if y.id == "dharma_karmadhipati_yoga")
        assert dk_exalted.is_qualifying is True
        assert dk_exalted.status == "Qualifying"
        assert "strongly placed" in dk_exalted.conditions[0].detail

