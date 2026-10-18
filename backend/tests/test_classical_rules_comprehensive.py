"""Comprehensive automated verification of all classical Vedic Yoga rules.

Covers positive qualifying cases, borderline failures, multiple Ascendants,
independent cancellations, and exact classical gradations.
"""

import pytest
from app.services.yoga_engine import calculate_vedic_yogas
from app.schemas.horoscope import PlanetInfo, NakshatraDetail


def _dummy_nak():
    return NakshatraDetail(name="Ashwini", index=1, pada=1, lord="Ketu", deity="Ashvins")


def _planet(name: str, sign_idx: int, lon: float = None, deg_in_sign: float = 15.0, retro: bool = False):
    if lon is None:
        lon = (sign_idx - 1) * 30.0 + deg_in_sign
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
        nakshatra=_dummy_nak()
    )


class TestClassicalPanchMahapurushaBorderlines:
    """Verify Panch Mahapurusha: Kendra requirement vs Non-Kendra borderline failures."""

    def test_ruchaka_own_sign_in_kendra_passes(self):
        # Aries Lagna (1): Mars in Aries (House 1, Kendra + Own sign)
        planets = [_planet("Mars", 1), _planet("Sun", 2), _planet("Moon", 3), _planet("Mercury", 4),
                   _planet("Jupiter", 5), _planet("Venus", 6), _planet("Saturn", 7)]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ruchaka = next(y for y in res.yogas if y.id == "ruchaka_yoga")
        assert ruchaka.is_qualifying is True

    def test_ruchaka_own_sign_in_non_kendra_fails(self):
        # Pisces Lagna (12): Mars in Aries (House 2, Own sign, but House 2 is NOT Kendra!)
        planets = [_planet("Mars", 1), _planet("Sun", 3), _planet("Moon", 4), _planet("Mercury", 5),
                   _planet("Jupiter", 6), _planet("Venus", 7), _planet("Saturn", 8)]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=12)
        ruchaka = next(y for y in res.yogas if y.id == "ruchaka_yoga")
        assert ruchaka.is_qualifying is False
        assert ruchaka.status == "Not Qualifying"
        # Condition 1 (Kendra) failed
        assert ruchaka.conditions[0].passed is False

    def test_bhadra_exalted_in_kendra_vs_dusthana(self):
        # Gemini Lagna (3): Mercury in Virgo (Sign 6, House 4 - Kendra + Exalted!) -> Passes
        planets_pass = [_planet("Mercury", 6), _planet("Sun", 1), _planet("Moon", 2), _planet("Mars", 4),
                        _planet("Jupiter", 5), _planet("Venus", 7), _planet("Saturn", 8)]
        res_pass = calculate_vedic_yogas(planets_pass, ascendant_sign_idx=3)
        bhadra = next(y for y in res_pass.yogas if y.id == "bhadra_yoga")
        assert bhadra.is_qualifying is True

        # Aries Lagna (1): Mercury in Virgo (Sign 6, House 6 - Dusthana, NOT Kendra!) -> Fails
        planets_fail = [_planet("Mercury", 6), _planet("Sun", 2), _planet("Moon", 3), _planet("Mars", 4),
                        _planet("Jupiter", 5), _planet("Venus", 7), _planet("Saturn", 8)]
        res_fail = calculate_vedic_yogas(planets_fail, ascendant_sign_idx=1)
        bhadra_fail = next(y for y in res_fail.yogas if y.id == "bhadra_yoga")
        assert bhadra_fail.is_qualifying is False


class TestMultipleAscendantsRajaAndDhanaYogas:
    """Verify Kendra-Trikona Raja Yogas and Dhana Yogas across distinct Ascendants."""

    def test_leo_lagna_raja_and_dharma_karmadhipati(self):
        # Leo Lagna (Sign 5, House 1):
        # 4th Lord = Mars (Scorpio 8), 5th Lord = Jupiter (Sagittarius 9).
        # Place Mars and Jupiter conjoined in House 1 (Leo) -> 4th + 5th Raja Yoga!
        # 9th Lord = Mars (Aries 1), 10th Lord = Venus (Taurus 2).
        # Place Venus conjoined with Mars in House 1 -> Dharma-Karmadhipati also qualifies!
        planets = [
            _planet("Mars", 5),       # 4th & 9th Lord in House 1
            _planet("Jupiter", 5),    # 5th Lord in House 1
            _planet("Venus", 5),      # 10th Lord in House 1
            _planet("Sun", 6),        # 1st Lord in House 2
            _planet("Moon", 7),
            _planet("Mercury", 8),
            _planet("Saturn", 9),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=5)
        # Check 4-5 Raja Yoga
        ry_4_5 = next(y for y in res.yogas if y.id == "raja_yoga_4_5")
        assert ry_4_5.is_qualifying is True

        # Check Dharma-Karmadhipati Yoga (9th Lord Mars + 10th Lord Venus)
        dk = next(y for y in res.yogas if y.id == "dharma_karmadhipati_yoga")
        assert dk.is_qualifying is True
        assert "Mars" in dk.planets_involved
        assert "Venus" in dk.planets_involved

    def test_gemini_lagna_dhana_yoga_2_11(self):
        # Gemini Lagna (Sign 3, House 1):
        # 2nd Lord = Moon (Cancer 4), 11th Lord = Mars (Aries 1).
        # Conjunction of Moon and Mars in Aries (House 11):
        # Qualifies 2nd & 11th Lord Dhana Yoga AND Chandra-Mangala Yoga!
        planets = [
            _planet("Moon", 1),       # Conjoined in Aries (House 11)
            _planet("Mars", 1),       # Conjoined in Aries (House 11)
            _planet("Sun", 2),
            _planet("Mercury", 3),
            _planet("Jupiter", 4),
            _planet("Venus", 5),
            _planet("Saturn", 6),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=3)
        dhana_2_11 = next(y for y in res.yogas if y.id == "dhana_yoga_2_11")
        assert dhana_2_11.is_qualifying is True

        cm = next(y for y in res.yogas if y.id == "chandra_mangala_yoga")
        assert cm.is_qualifying is True
        assert cm.category == "Dhana Yoga"

    def test_capricorn_lagna_single_planet_dhana_yoga_1_2(self):
        # Capricorn Lagna (Sign 10, House 1):
        # 1st Lord = Saturn (Capricorn 10), 2nd Lord = Saturn (Aquarius 11).
        # Saturn rules both 1st and 2nd houses.
        # When Saturn is in Capricorn (House 1, own sign Kendra):
        planets = [
            _planet("Saturn", 10),    # House 1, Own Sign
            _planet("Sun", 11),
            _planet("Moon", 12),
            _planet("Mars", 1),
            _planet("Mercury", 2),
            _planet("Jupiter", 3),
            _planet("Venus", 4),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=10)
        dhana_1_2 = next(y for y in res.yogas if y.id == "dhana_yoga_1_2")
        assert dhana_1_2.is_qualifying is True
        assert "Saturn" in dhana_1_2.planets_involved


class TestVasumathiYogaGradations:
    """Verify Vasumathi Yoga full (3 benefics), partial (2 benefics), and failure (1 benefic)."""

    def test_full_vasumathi_from_lagna(self):
        # Aries Lagna (1): Upachaya houses are 3 (Gemini), 6 (Virgo), 10 (Capricorn), 11 (Aquarius).
        # Place Jupiter in 3 (Gemini 3), Venus in 6 (Virgo 6), Mercury in 10 (Capricorn 10).
        planets = [
            _planet("Jupiter", 3),    # House 3
            _planet("Venus", 6),      # House 6
            _planet("Mercury", 10),   # House 10
            _planet("Sun", 1),
            _planet("Moon", 1),
            _planet("Mars", 2),
            _planet("Saturn", 4),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        vasu = next(y for y in res.yogas if y.id == "vasumathi_yoga")
        assert vasu.is_qualifying is True
        assert vasu.status == "Qualifying"

    def test_partial_vasumathi_two_benefics(self):
        # Aries Lagna (1): Jupiter in 3, Venus in 11, but Mercury in 1 (not Upachaya).
        planets = [
            _planet("Jupiter", 3),    # House 3 (Upachaya)
            _planet("Venus", 11),     # House 11 (Upachaya)
            _planet("Mercury", 1),    # House 1 (NOT Upachaya)
            _planet("Sun", 2),
            _planet("Moon", 2),       # Moon in 2 -> Moon Upachayas are 4, 7, 11, 12 (none have 3 benefics)
            _planet("Mars", 4),
            _planet("Saturn", 5),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        vasu = next(y for y in res.yogas if y.id == "vasumathi_yoga")
        assert vasu.is_qualifying is False
        assert vasu.status == "Partially Qualifying"

    def test_vasumathi_failure_one_benefic(self):
        # Aries Lagna (1): Only Jupiter in Upachaya (3). Venus in 4, Mercury in 5.
        planets = [
            _planet("Jupiter", 3),    # House 3
            _planet("Venus", 4),      # House 4
            _planet("Mercury", 5),    # House 5
            _planet("Sun", 1),
            _planet("Moon", 1),
            _planet("Mars", 2),
            _planet("Saturn", 7),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        vasu = next(y for y in res.yogas if y.id == "vasumathi_yoga")
        assert vasu.is_qualifying is False
        assert vasu.status == "Not Qualifying"


class TestLunarAndSolarExclusions:
    """Verify strict exclusion of Sun, Rahu, and Ketu from Lunar and Solar formations."""

    def test_sunapha_excludes_rahu(self):
        # Aries Lagna (1): Moon in Cancer (Sign 4, House 4).
        # 2nd from Moon is Leo (Sign 5, House 5).
        # If ONLY Rahu is in Leo (Sign 5), Sunapha must NOT qualify!
        planets = [
            _planet("Moon", 4),
            _planet("Rahu", 5),       # Node in 2nd from Moon
            _planet("Sun", 8),
            _planet("Mars", 9),
            _planet("Mercury", 10),
            _planet("Jupiter", 11),
            _planet("Venus", 12),
            _planet("Saturn", 1),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        sunapha = next(y for y in res.yogas if y.id == "sunapha_yoga")
        assert sunapha.is_qualifying is False
        assert sunapha.status == "Not Qualifying"

    def test_sunapha_excludes_sun(self):
        # Moon in Cancer (Sign 4). Sun in Leo (Sign 5, 2nd from Moon).
        # Sun cannot cause Sunapha (Sunapha requires planets OTHER than Sun).
        planets = [
            _planet("Moon", 4),
            _planet("Sun", 5),        # Sun in 2nd from Moon
            _planet("Mars", 8),
            _planet("Mercury", 9),
            _planet("Jupiter", 10),
            _planet("Venus", 11),
            _planet("Saturn", 12),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        sunapha = next(y for y in res.yogas if y.id == "sunapha_yoga")
        assert sunapha.is_qualifying is False

    def test_dhurdhura_both_flanks_occupied(self):
        # Moon in Cancer (Sign 4).
        # 2nd from Moon (Leo 5) has Mars. 12th from Moon (Gemini 3) has Jupiter.
        # Qualifies Dhurdhura Yoga!
        planets = [
            _planet("Moon", 4),
            _planet("Mars", 5),       # 2nd from Moon
            _planet("Jupiter", 3),    # 12th from Moon
            _planet("Sun", 8),
            _planet("Mercury", 9),
            _planet("Venus", 10),
            _planet("Saturn", 11),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dhur = next(y for y in res.yogas if y.id == "dhurdhura_yoga")
        assert dhur.is_qualifying is True
        assert dhur.status == "Qualifying"
        assert "Mars" in dhur.planets_involved
        assert "Jupiter" in dhur.planets_involved


class TestParivartanaAllThreeCategories:
    """Verify Maha, Kahala, and Dainya Parivartana classifications."""

    def test_maha_parivartana_1_and_9(self):
        # Aries Lagna (1): 1st Lord Mars in Sagittarius (Sign 9), 9th Lord Jupiter in Aries (Sign 1).
        # Both 1 and 9 are auspicious -> Maha Parivartana.
        planets = [
            _planet("Mars", 9),       # In 9th house (Jupiter's sign)
            _planet("Jupiter", 1),    # In 1st house (Mars's sign)
            _planet("Sun", 2),
            _planet("Moon", 3),
            _planet("Mercury", 4),
            _planet("Venus", 5),
            _planet("Saturn", 6),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        maha = next((y for y in res.yogas if "maha_parivartana" in y.id), None)
        assert maha is not None
        assert maha.is_qualifying is True
        assert maha.category == "Parivartana"

    def test_kahala_parivartana_3_and_11(self):
        # Aries Lagna (1): 3rd Lord Mercury in Aquarius (Sign 11), 11th Lord Saturn in Gemini (Sign 3).
        # Involves 3rd lord with auspicious lord -> Kahala Parivartana.
        planets = [
            _planet("Mercury", 11),   # In 11th house (Saturn's sign)
            _planet("Saturn", 3),     # In 3rd house (Mercury's sign)
            _planet("Sun", 1),
            _planet("Moon", 2),
            _planet("Mars", 4),
            _planet("Jupiter", 5),
            _planet("Venus", 6),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        kahala = next((y for y in res.yogas if "kahala_parivartana" in y.id), None)
        assert kahala is not None
        assert kahala.is_qualifying is True
        assert kahala.category == "Parivartana"

    def test_dainya_parivartana_6_and_10(self):
        # Aries Lagna (1): 6th Lord Mercury in Capricorn (Sign 10), 10th Lord Saturn in Virgo (Sign 6).
        # Involves Dusthana lord (6th) -> Dainya Parivartana.
        planets = [
            _planet("Mercury", 10),   # In 10th house (Saturn's sign)
            _planet("Saturn", 6),     # In 6th house (Mercury's sign)
            _planet("Sun", 1),
            _planet("Moon", 2),
            _planet("Mars", 3),
            _planet("Jupiter", 4),
            _planet("Venus", 5),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dainya = next((y for y in res.yogas if "dainya_parivartana" in y.id), None)
        assert dainya is not None
        assert dainya.is_qualifying is True
        assert dainya.category == "Parivartana"
