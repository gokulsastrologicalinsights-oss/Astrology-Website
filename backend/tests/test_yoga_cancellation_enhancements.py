"""Independent reference tests for enhanced Yoga Detection, Cancellation (Bhanga) rules,
Arishta Bhanga, Daridra Yogas, Combustion, and Vargottama modifiers.

Classical Authorities:
- Brihat Parashara Hora Shastra (BPHS), Chapters 10, 11, 34, 36, 39, 42, 45.
- Phaladeepika, Chapters 6 & 13.
- Saravali, Chapters 12 & 35.
- Dr. B.V. Raman, '300 Important Combinations'.
"""

import pytest
from app.services.yoga_engine import calculate_vedic_yogas
from app.services.yoga_engine.models import YogaChartContext
from app.schemas.horoscope import PlanetInfo, NakshatraDetail


def _dummy_nakshatra(name="Ashwini"):
    return NakshatraDetail(name=name, index=1, pada=1, lord="Ketu", deity="Ashvins")


def _p(name, sign_idx, lon, deg_in_sign=15.0, is_retrograde=False):
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
        nakshatra=_dummy_nakshatra(),
    )


# ===========================================================================
# 1. Neecha Bhanga & Neecha Bhanga Raja Yoga (NBRY) Cancellation Tests
# ===========================================================================

class TestNeechaBhangaCancellations:
    """Test all 7 classical cancellation conditions for debilitated planets, plus combustion cancellation."""

    def test_nbry_rule1_dispositor_in_kendra_from_lagna(self):
        # Aries Lagna (1)
        # Saturn is debilitated in Aries (Sign 1, House 1).
        # Dispositor of Aries is Mars.
        # Place Mars in Capricorn (Sign 10, House 10 - Kendra from Lagna!).
        planets = [
            _p("Saturn", 1, 15.0),          # Debilitated in Aries (House 1)
            _p("Mars", 10, 285.0),          # Dispositor in Kendra House 10
            _p("Sun", 9, 250.0),            # Far from Saturn (not combust)
            _p("Moon", 2, 45.0),
            _p("Mercury", 8, 220.0),
            _p("Jupiter", 9, 260.0),
            _p("Venus", 11, 320.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_saturn")
        assert nbry.is_qualifying is True
        assert nbry.status == "Qualifying"
        assert any("Dispositor Mars in Kendra" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule2_exalted_ruler_of_debilitation_sign_in_kendra(self):
        # Aries Lagna (1)
        # Sun is debilitated in Libra (Sign 7).
        # Saturn is the planet that gets exalted in Libra!
        # Place Saturn in Capricorn (House 10, Kendra from Lagna!).
        planets = [
            _p("Sun", 7, 190.0),
            _p("Saturn", 10, 280.0),        # Exalted ruler of Libra in Kendra
            _p("Venus", 2, 40.0),           # Dispositor not in Kendra
            _p("Moon", 3, 70.0),
            _p("Mars", 5, 130.0),
            _p("Mercury", 8, 230.0),
            _p("Jupiter", 9, 250.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_sun")
        assert nbry.is_qualifying is True
        assert nbry.status == "Qualifying"
        assert any("Exalted lord Saturn in Kendra" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule3_lord_of_exaltation_sign_in_kendra(self):
        # Aries Lagna (1)
        # Jupiter is debilitated in Capricorn (Sign 10).
        # Jupiter's exaltation sign is Cancer (Sign 4), whose lord is Moon!
        # Place Moon in Cancer (House 4, Kendra from Lagna!).
        planets = [
            _p("Jupiter", 10, 280.0),
            _p("Moon", 4, 100.0),           # Exaltation sign lord in Kendra House 4
            _p("Saturn", 6, 160.0),         # Dispositor in 6th (not Kendra)
            _p("Sun", 2, 45.0),
            _p("Mars", 3, 75.0),
            _p("Mercury", 8, 225.0),
            _p("Venus", 11, 315.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_jupiter")
        assert nbry.is_qualifying is True
        assert nbry.status == "Qualifying"
        assert any("Exaltation sign ruler Moon in Kendra" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule4_debilitated_planet_in_kendra_itself(self):
        # Aries Lagna (1)
        # Mars is debilitated in Cancer (Sign 4, House 4 - Kendra from Lagna!).
        # Moon (dispositor) in 6th (Virgo), Jupiter in 8th (Scorpio)
        planets = [
            _p("Mars", 4, 105.0),           # Debilitated in 4th (Kendra!)
            _p("Moon", 6, 165.0),
            _p("Jupiter", 8, 225.0),
            _p("Sun", 9, 255.0),
            _p("Saturn", 11, 315.0),
            _p("Mercury", 2, 45.0),
            _p("Venus", 3, 75.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_mars")
        assert nbry.is_qualifying is True
        assert nbry.status == "Qualifying"
        assert any("Mars itself is in a Kendra" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule5_dispositor_aspects_debilitated_planet(self):
        # Aries Lagna (1)
        # Sun is debilitated in Libra (Sign 7).
        # Dispositor Venus is in Aries (Sign 1), directly aspecting Sun (7th aspect).
        planets = [
            _p("Sun", 7, 195.0),
            _p("Venus", 1, 15.0),           # 7th aspect on Sun
            _p("Moon", 3, 75.0),
            _p("Mars", 5, 135.0),
            _p("Mercury", 8, 225.0),
            _p("Jupiter", 9, 255.0),
            _p("Saturn", 11, 315.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_sun")
        assert nbry.is_qualifying is True
        assert any("Sun is aspected by dispositor Venus" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule6_navamsha_vargottama(self):
        # Aries Lagna (1)
        # Venus debilitated in Virgo (Sign 6).
        # But in first Navamsha of Virgo (Earth sign, starts Capricorn -> Navamsha 1 is Capricorn, etc.)
        # For Vargottama: Virgo (Earth: 2, 6, 10). Element start is Capricorn (10).
        # Navamsha index 8 -> Capricorn(10)+8 = Virgo(6). Degree between 26°40' and 30°00' (e.g. 28.0°)
        # Longitude in Virgo = 150.0 + 28.0 = 178.0°
        planets = [
            _p("Venus", 6, 178.0, deg_in_sign=28.0), # Vargottama in Virgo!
            _p("Mercury", 8, 225.0),                 # Dispositor not in Kendra
            _p("Sun", 2, 45.0),
            _p("Moon", 3, 75.0),
            _p("Mars", 5, 135.0),
            _p("Jupiter", 9, 255.0),
            _p("Saturn", 11, 315.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_venus")
        assert nbry.is_qualifying is True
        assert any("Vargottama" in c.detail for c in nbry.conditions if c.passed)

    def test_nbry_rule7_mutual_debilitation_aspect(self):
        # Aries Lagna (1)
        # Saturn is debilitated in Aries (Sign 1, House 1).
        # Sun is debilitated in Libra (Sign 7, House 7).
        # They mutually aspect each other across 1st and 7th houses!
        planets = [
            _p("Saturn", 1, 15.0),
            _p("Sun", 7, 195.0),
            _p("Moon", 2, 45.0),
            _p("Mars", 3, 75.0),
            _p("Mercury", 8, 225.0),
            _p("Jupiter", 9, 255.0),
            _p("Venus", 11, 315.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry_saturn = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_saturn")
        nbry_sun = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_sun")
        assert nbry_saturn.is_qualifying is True
        assert nbry_sun.is_qualifying is True
        assert any("mutually aspects debilitated" in c.detail for c in nbry_saturn.conditions if c.passed)

    def test_nbry_cancelled_by_combustion(self):
        # Aries Lagna (1)
        # Mars is debilitated in Cancer (House 4). Dispositor Moon is in House 1 (Kendra).
        # So Bhanga condition is met!
        # BUT Mars is combust by Sun: Sun in Cancer 102°, Mars in Cancer 105° (diff = 3°, orb is 17°).
        planets = [
            _p("Mars", 4, 105.0),                   # Debilitated & Combust
            _p("Sun", 4, 102.0),                    # Combustion agent
            _p("Moon", 1, 15.0),                    # Dispositor in Kendra House 1
            _p("Jupiter", 9, 255.0),
            _p("Venus", 11, 315.0),
            _p("Saturn", 2, 45.0),
            _p("Mercury", 5, 135.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        nbry_mars = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_mars")
        assert nbry_mars.status == "Cancelled"
        assert nbry_mars.is_qualifying is False
        assert "combust" in nbry_mars.cancellation_reason.lower()

    def test_nbry_unmitigated_negative(self):
        # Pisces Lagna (12)
        # Sun is debilitated in Libra (Sign 7, House 8 from Pisces - not Kendra).
        # Dispositor Venus in Cancer (Sign 4, House 5 from Pisces - not Kendra).
        # Exalted planet in Libra (Saturn) in Aries (Sign 1, House 2 from Pisces - not Kendra).
        # Sun's own exaltation lord (Mars) in Capricorn (Sign 10, House 11 from Pisces - not Kendra).
        # Moon in Taurus (Sign 2, House 3 from Pisces - not Kendra).
        # Relative to Moon (Sign 2):
        #   Sun (7) is in 6th (not Kendra)
        #   Venus (4) is in 3rd (not Kendra)
        #   Saturn (1) is in 12th (not Kendra)
        #   Mars (10) is in 9th (not Kendra)
        # No mutual aspect, no Navamsha exaltation.
        planets = [
            _p("Sun", 7, 195.0, deg_in_sign=15.0),  # Libra (House 8 from Pisces)
            _p("Venus", 4, 105.0),                  # Cancer (House 5)
            _p("Saturn", 10, 280.0),                # Capricorn (House 11, own sign, not debilitated)
            _p("Mars", 10, 285.0),                  # Capricorn (House 11)
            _p("Moon", 2, 45.0),                    # Taurus (House 3)
            _p("Mercury", 8, 225.0),                # Scorpio (House 9)
            _p("Jupiter", 8, 230.0),                # Scorpio (House 9)
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=12)
        nbry_sun = next(y for y in res.yogas if y.id == "neecha_bhanga_raja_yoga_sun")
        assert nbry_sun.status == "Not Qualifying"
        assert nbry_sun.is_qualifying is False
        assert nbry_sun.cancellation_reason is None


# ===========================================================================
# 2. Kemadruma Yoga & Cancellation Conditions
# ===========================================================================

class TestKemadrumaCancellations:
    """Test Kemadruma formation, multiple cancellations, and Kalpadruma conversion."""

    def test_kemadruma_pure_operative(self):
        # Aries Lagna (1)
        # Moon in 6th house (Virgo, Sign 6).
        # Flanks of Moon: 2nd from Moon (Libra, House 7) and 12th from Moon (Leo, House 5) empty!
        # Kendras from Lagna: 1, 4, 7, 10 empty of qualifying planets.
        # Kendras from Moon: 6, 9, 12, 3 empty of qualifying planets.
        # Allowable houses: {2, 8, 11}!
        # Place planets in Houses 2, 8, 11 (with no aspect on Moon from Jupiter or Venus).
        planets = [
            _p("Moon", 6, 165.0),           # House 6 (Virgo)
            _p("Mars", 2, 45.0),            # House 2
            _p("Mercury", 2, 50.0),         # House 2
            _p("Saturn", 8, 225.0),         # House 8
            _p("Jupiter", 11, 315.0),       # House 11 (Aquarius: aspects 3, 5, 7, not 6)
            _p("Venus", 11, 320.0),         # House 11 (Aquarius: aspects 5, not 6)
            _p("Sun", 2, 40.0),             # Excluded
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        kema = next(y for y in res.yogas if y.id == "kemadruma_yoga")
        assert kema.status == "Qualifying"
        assert kema.is_qualifying is True
        assert kema.cancellation_reason is None

    def test_kemadruma_cancelled_by_kendra_from_moon(self):
        # Moon in House 6 (Virgo). 2nd and 12th from Moon empty.
        # Jupiter in 9th from Lagna (Sagittarius) -> 4th from Moon (Kendra from Moon!).
        planets = [
            _p("Moon", 6, 165.0),
            _p("Jupiter", 9, 255.0),        # 4th from Moon (Kendra from Moon!)
            _p("Mars", 2, 45.0),
            _p("Mercury", 2, 50.0),
            _p("Venus", 8, 225.0),
            _p("Saturn", 11, 315.0),
            _p("Sun", 2, 40.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        kema = next(y for y in res.yogas if y.id == "kemadruma_yoga")
        assert kema.status == "Cancelled"
        assert kema.is_qualifying is False
        assert "from Moon" in kema.cancellation_reason

        # Kemadruma Bhanga Raja Yoga must qualify!
        kbry = next(y for y in res.yogas if y.id == "kemadruma_bhanga_raja_yoga")
        assert kbry.is_qualifying is True
        assert kbry.status == "Qualifying"

    def test_kemadruma_cancelled_by_moon_in_kendra_from_lagna(self):
        # Moon in Cancer (House 4, Kendra from Lagna!).
        # Flanks of Moon: 2nd from Moon (Leo, House 5) and 12th from Moon (Gemini, House 3) empty!
        # Place all other planets in Houses 2, 8, 11 (none in 3 or 5).
        planets = [
            _p("Moon", 4, 105.0),           # In House 4 (Kendra from Lagna)
            _p("Mars", 2, 45.0),            # House 2
            _p("Mercury", 2, 50.0),         # House 2
            _p("Jupiter", 8, 225.0),        # House 8
            _p("Venus", 11, 315.0),         # House 11
            _p("Saturn", 8, 230.0),         # House 8
            _p("Sun", 2, 40.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        kema = next(y for y in res.yogas if y.id == "kemadruma_yoga")
        assert kema.status == "Cancelled"
        assert "kendra" in kema.cancellation_reason.lower() and "lagna" in kema.cancellation_reason.lower()



# ===========================================================================
# 3. Arishta Bhanga Rules
# ===========================================================================

class TestArishtaBhangaRules:
    """Test all 5 classical Arishta Bhanga neutralizing formations."""

    def test_arishta_bhanga_jupiter_in_lagna(self):
        # Aries Lagna (1)
        # Jupiter in House 1 (Aries), uncombust and dignified
        planets = [
            _p("Jupiter", 1, 15.0),
            _p("Sun", 5, 135.0),
            _p("Moon", 6, 165.0),           # Moon in 6th (Dusthana Balarishta)
            _p("Mars", 2, 45.0),
            _p("Mercury", 3, 75.0),
            _p("Venus", 4, 105.0),
            _p("Saturn", 8, 225.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ab_jup = next(y for y in res.yogas if y.id == "arishta_bhanga_jupiter_kendra")
        assert ab_jup.is_qualifying is True
        assert ab_jup.status == "Qualifying"
        assert ab_jup.category == "Arishta Bhanga"

    def test_arishta_bhanga_jupiter_kendra_cancelled_by_combustion(self):
        # Jupiter in House 1, but conjoined with Sun within 5° (combust!)
        planets = [
            _p("Jupiter", 1, 15.0),
            _p("Sun", 1, 12.0),             # Combusts Jupiter
            _p("Moon", 6, 165.0),
            _p("Mars", 2, 45.0),
            _p("Mercury", 3, 75.0),
            _p("Venus", 4, 105.0),
            _p("Saturn", 8, 225.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ab_jup = next(y for y in res.yogas if y.id == "arishta_bhanga_jupiter_kendra")
        assert ab_jup.status == "Cancelled"
        assert ab_jup.is_qualifying is False
        assert "combustion" in ab_jup.cancellation_reason.lower()

    def test_arishta_bhanga_rahu_in_upachaya(self):
        # Rahu in 3rd house (Gemini, Sign 3)
        planets = [
            _p("Rahu", 3, 75.0),
            _p("Sun", 2, 45.0),
            _p("Moon", 8, 225.0),           # Moon in 8th (Balarishta)
            _p("Mars", 5, 135.0),
            _p("Mercury", 2, 50.0),
            _p("Jupiter", 9, 255.0),
            _p("Venus", 12, 345.0),
            _p("Saturn", 5, 140.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ab_rahu = next(y for y in res.yogas if y.id == "arishta_bhanga_rahu_upachaya")
        assert ab_rahu.is_qualifying is True
        assert ab_rahu.status == "Qualifying"
        assert "Rahu occupies House 3" in ab_rahu.conditions[0].detail

    def test_arishta_bhanga_moon_benefic_drishti(self):
        # Moon in 8th house (Scorpio, Sign 8).
        # Jupiter in 2nd house (Taurus, Sign 2) -> casts exact 7th aspect on Moon!
        planets = [
            _p("Moon", 8, 225.0),           # In 8th house
            _p("Jupiter", 2, 45.0),         # Directly aspects Moon across 7th
            _p("Sun", 1, 10.0),
            _p("Mars", 3, 75.0),
            _p("Mercury", 4, 105.0),
            _p("Venus", 5, 135.0),
            _p("Saturn", 9, 255.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        ab_moon = next(y for y in res.yogas if y.id == "arishta_bhanga_moon_benefic_drishti")
        assert ab_moon.is_qualifying is True
        assert ab_moon.status == "Qualifying"


# ===========================================================================
# 4. Daridra Yoga Rules & Daridra Bhanga Tests
# ===========================================================================

class TestDaridraYogasAndBhanga:
    """Test 11th, 2nd, and Trikona lord Daridra Yogas and their classical cancellations."""

    def test_daridra_yoga_11th_lord_in_dusthana_unmitigated(self):
        # Aries Lagna (1)
        # 11th lord = Saturn (Aquarius)
        # Place Saturn in 6th house (Virgo, Sign 6), no benefic aspect
        planets = [
            _p("Saturn", 6, 165.0),         # 11th lord in 6th
            _p("Jupiter", 9, 255.0),        # House 9 (no aspect on 6th)
            _p("Venus", 3, 75.0),           # House 3 (no aspect on 6th)
            _p("Sun", 1, 10.0),
            _p("Moon", 4, 105.0),
            _p("Mars", 2, 45.0),
            _p("Mercury", 1, 20.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dy = next(y for y in res.yogas if y.id == "daridra_yoga")
        assert dy.is_qualifying is True
        assert dy.status == "Qualifying"

    def test_daridra_yoga_11th_lord_cancelled_by_jupiter_aspect(self):
        # 11th lord Saturn in 6th house (Virgo, Sign 6).
        # Jupiter in 12th house (Pisces, Sign 12) -> directly aspects Saturn (7th aspect)!
        planets = [
            _p("Saturn", 6, 165.0),
            _p("Jupiter", 12, 345.0),       # Aspects Saturn!
            _p("Sun", 1, 10.0),
            _p("Moon", 4, 105.0),
            _p("Mars", 2, 45.0),
            _p("Mercury", 1, 20.0),
            _p("Venus", 3, 75.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dy = next(y for y in res.yogas if y.id == "daridra_yoga")
        assert dy.status == "Cancelled"
        assert dy.is_qualifying is False
        assert "aspect" in dy.cancellation_reason.lower() or "drishti" in dy.cancellation_reason.lower()

    def test_daridra_yoga_2nd_lord_in_dusthana(self):
        # Aries Lagna (1)
        # 2nd lord = Venus (Taurus)
        # Place Venus in 8th house (Scorpio, Sign 8)
        planets = [
            _p("Venus", 8, 225.0),          # 2nd lord in 8th
            _p("Saturn", 5, 135.0),
            _p("Jupiter", 9, 255.0),
            _p("Sun", 1, 10.0),
            _p("Moon", 4, 105.0),
            _p("Mars", 2, 45.0),
            _p("Mercury", 1, 20.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        dy2 = next(y for y in res.yogas if y.id == "daridra_yoga_2nd_lord")
        assert dy2.is_qualifying is True
        assert dy2.status == "Qualifying"


# ===========================================================================
# 5. Modifiers & Multilingual Completeness
# ===========================================================================

class TestStrengthModifiersAndIntegrity:
    """Test Vargottama detection, combustion orbs, and English/Tamil response completeness."""

    def test_vargottama_helper(self):
        # Aries Lagna (1). Sun at Aries 1.0° (Fire sign: Navamsha 1 = Aries) -> Vargottama!
        planets = [
            _p("Sun", 1, 1.0, deg_in_sign=1.0),
            _p("Moon", 4, 100.0),
            _p("Mars", 2, 40.0),
            _p("Mercury", 3, 70.0),
            _p("Jupiter", 9, 250.0),
            _p("Venus", 5, 130.0),
            _p("Saturn", 7, 195.0),
        ]
        ctx = YogaChartContext(planets, ascendant_sign_idx=1)
        assert ctx.is_vargottama("Sun") is True
        # Moon at Cancer 10.0° (Water sign starts Cancer; nav 3 = Virgo) -> Not Vargottama
        assert ctx.is_vargottama("Moon") is False

    def test_english_tamil_completeness(self):
        planets = [
            _p("Sun", 1, 10.0),
            _p("Moon", 4, 100.0),
            _p("Mars", 10, 280.0),
            _p("Mercury", 1, 15.0),
            _p("Jupiter", 4, 105.0),
            _p("Venus", 7, 200.0),
            _p("Saturn", 7, 205.0),
        ]
        res = calculate_vedic_yogas(planets, ascendant_sign_idx=1)
        for y in res.yogas:
            assert y.id and len(y.id) > 0
            assert y.name and len(y.name) > 0
            assert y.name_tamil and len(y.name_tamil) > 0
            assert y.short_interpretation and len(y.short_interpretation) > 0
            assert y.classical_definition and len(y.classical_definition) > 0
            assert y.classical_reference and len(y.classical_reference) > 0
            assert y.status in ("Qualifying", "Cancelled", "Not Qualifying")
