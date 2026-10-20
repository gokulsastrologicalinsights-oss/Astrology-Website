"""Unit tests for Phase 6: Bidirectional Vedic Horoscope Synastry Engine.

Validates:
1. Moon-to-Moon (Chandra) synastry axes (Samasaptaka, Trikona, Shadashtaka, Upachaya, Eka Rasi).
2. Moon sign lord friendship calculations and direct aspects.
3. Lagna-to-Lagna (Ascendant) synastry axes, lord relationships, cross-chart house overlays.
4. Marriage-Lord (7th Lord) cross-chart placements, dignities, and activation of marriage houses.
5. Venus & Jupiter cross-chart Karaka interactions and aspects.
6. Navamsa boundary sensitivity detection (< 10 arcminutes).
7. Top-level pipeline `evaluate_bidirectional_synastry`.
8. Complete mathematical determinism.
"""

from __future__ import annotations
import pytest
from typing import Dict, Any, Optional

from app.services.marriage_engine.models import (
    Gender,
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    MoonToMoonFinding,
    LagnaToLagnaFinding,
    MarriageLordCrossChartFinding,
    VenusJupiterCrossChartFinding,
    BidirectionalSynastryResult,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
)
from app.services.marriage_engine.synastry import (
    evaluate_moon_to_moon_synastry,
    evaluate_lagna_to_lagna_synastry,
    evaluate_marriage_lord_cross_synastry,
    evaluate_venus_jupiter_cross_synastry,
    evaluate_bidirectional_synastry,
    MARRIAGE_HOUSES,
)


# ---------------------------------------------------------------------------
# Test Helpers & Fixtures
# ---------------------------------------------------------------------------

def _create_test_planet(
    name: str,
    sign_index: int,
    house: int,
    degree_in_sign: float = 15.0,
    is_retrograde: bool = False,
) -> MarriagePlanet:
    """Helper to build a MarriagePlanet."""
    longitude = (sign_index - 1) * 30.0 + degree_in_sign
    return MarriagePlanet(
        name=name,
        body_id=0,
        longitude=longitude,
        sign_index=sign_index,
        sign_name=SIGN_NAMES_EN[sign_index],
        sign_name_tamil=SIGN_NAMES_TA[sign_index],
        degree_in_sign=degree_in_sign,
        house=house,
        speed_deg_per_day=1.0,
        is_retrograde=is_retrograde,
        nakshatra_index=((sign_index - 1) * 9 // 4) % 27,
        nakshatra_name="Ashwini",
        nakshatra_pada=1,
        navamsa_sign_index=1,
    )


def _build_synastry_test_chart(
    person_id: str,
    gender: Gender,
    lagna_sign: int,
    moon_sign: int,
    moon_nakshatra_idx: int = 0,
    moon_pada: int = 1,
    ascendant_degree_in_sign: float = 15.0,
    moon_degree_in_sign: float = 15.0,
    extra_planets: Optional[Dict[str, MarriagePlanet]] = None,
) -> MarriageChartContext:
    """Helper to construct a comprehensive MarriageChartContext for synastry testing."""
    asc_degree = (lagna_sign - 1) * 30.0 + ascendant_degree_in_sign
    moon_degree = (moon_sign - 1) * 30.0 + moon_degree_in_sign

    moon_house = ((moon_sign - lagna_sign) % 12) + 1
    grahas: Dict[str, MarriagePlanet] = {
        "Moon": MarriagePlanet(
            name="Moon",
            body_id=1,
            longitude=moon_degree,
            sign_index=moon_sign,
            sign_name=SIGN_NAMES_EN[moon_sign],
            sign_name_tamil=SIGN_NAMES_TA[moon_sign],
            degree_in_sign=moon_degree_in_sign,
            house=moon_house,
            nakshatra_index=moon_nakshatra_idx,
            nakshatra_name=SIGN_NAMES_EN[moon_sign],
            nakshatra_pada=moon_pada,
            navamsa_sign_index=1,
        ),
        "Venus": _create_test_planet("Venus", sign_index=2, house=((2 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Jupiter": _create_test_planet("Jupiter", sign_index=4, house=((4 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Mars": _create_test_planet("Mars", sign_index=1, house=((1 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Saturn": _create_test_planet("Saturn", sign_index=10, house=((10 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Sun": _create_test_planet("Sun", sign_index=5, house=((5 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Mercury": _create_test_planet("Mercury", sign_index=3, house=((3 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Rahu": _create_test_planet("Rahu", sign_index=2, house=((2 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
        "Ketu": _create_test_planet("Ketu", sign_index=8, house=((8 - lagna_sign) % 12) + 1, degree_in_sign=10.0),
    }

    if extra_planets:
        grahas.update(extra_planets)

    houses: Dict[int, MarriageHouse] = {}
    for h in range(1, 13):
        sign = ((lagna_sign + h - 2) % 12) + 1
        houses[h] = MarriageHouse(
            house_number=h,
            sign_index=sign,
            sign_name=SIGN_NAMES_EN[sign],
            sign_name_tamil=SIGN_NAMES_TA[sign],
            cusp_degree=(sign - 1) * 30.0 + 15.0,
            degree_in_sign=15.0,
            lord_name=SIGN_LORDS[sign],
        )

    return MarriageChartContext(
        person_id=person_id,
        person_name=person_id,
        gender=gender,
        birth_date_iso="1992-05-15",
        birth_time_iso="10:30:00",
        timezone="Asia/Kolkata",
        latitude=13.08,
        longitude=80.27,
        ascendant_degree=asc_degree,
        ascendant_sign_idx=lagna_sign,
        ascendant_sign_name=SIGN_NAMES_EN[lagna_sign],
        ascendant_sign_name_tamil=SIGN_NAMES_TA[lagna_sign],
        ascendant_nakshatra_idx=0,
        ascendant_nakshatra_name="Ashwini",
        ascendant_nakshatra_pada=1,
        ascendant_navamsa_sign_idx=1,
        moon_degree=moon_degree,
        moon_sign_idx=moon_sign,
        moon_sign_name=SIGN_NAMES_EN[moon_sign],
        moon_sign_name_tamil=SIGN_NAMES_TA[moon_sign],
        moon_nakshatra_idx=moon_nakshatra_idx,
        moon_nakshatra_name="Ashwini",
        moon_nakshatra_pada=moon_pada,
        moon_navamsa_sign_idx=1,
        grahas=grahas,
        houses=houses,
    )


# ---------------------------------------------------------------------------
# 1. Moon-to-Moon Tests
# ---------------------------------------------------------------------------

class TestMoonToMoonSynastry:
    """Test suite for evaluate_moon_to_moon_synastry."""

    def test_samasaptaka_moon_axis(self):
        """Opposite Moon signs (1/7 axis e.g., Aries-Libra) is Favorable Samasaptaka."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)   # Aries Moon
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=7) # Libra Moon

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.sign_distance_g_to_b == 7
        assert res.sign_distance_b_to_g == 7
        assert "Samasaptaka" in res.sign_relationship
        assert res.sign_assessment == "Favorable"
        assert res.groom_moon_aspects_bride_moon is True
        assert res.bride_moon_aspects_groom_moon is True

    def test_trikona_moon_axis(self):
        """Trine Moon signs (1/5 or 1/9 axis e.g., Aries-Leo) is Favorable Trikona."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1) # Aries
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=5) # Leo

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.sign_distance_g_to_b == 5
        assert res.sign_distance_b_to_g == 9
        assert "Trikona" in res.sign_relationship
        assert res.sign_assessment == "Favorable"

    def test_shadashtaka_moon_axis_different_lords(self):
        """6/8 Moon axis with different lords (Aries-Virgo) is Unfavorable."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1) # Aries (Mars)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=6) # Virgo (Mercury)

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.sign_distance_g_to_b == 6
        assert res.sign_distance_b_to_g == 8
        assert "Shadashtaka" in res.sign_relationship
        assert res.sign_assessment == "Unfavorable"

    def test_shadashtaka_moon_axis_same_lord_mitigated(self):
        """6/8 Moon axis with same lord (Aries-Scorpio both Mars) is Neutral (mitigated)."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1) # Aries (Mars)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=8) # Scorpio (Mars)

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.sign_distance_g_to_b == 8
        assert res.sign_distance_b_to_g == 6
        assert "Shadashtaka" in res.sign_relationship
        assert res.sign_assessment == "Neutral"
        assert res.groom_moon_lord == res.bride_moon_lord == "Mars"

    def test_upachaya_moon_axis(self):
        """3/11 Moon axis (e.g. Aries-Gemini) is Favorable Upachaya."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1) # Aries
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=3) # Gemini

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.sign_distance_g_to_b == 3
        assert res.sign_distance_b_to_g == 11
        assert "Upachaya" in res.sign_relationship
        assert res.sign_assessment == "Favorable"

    def test_navamsa_boundary_sensitivity_on_moon(self):
        """Moon within 10 arcminutes of Navamsa boundary sets boundary risk flag."""
        # 3°20' = 3.33333° Navamsa span. 0.05° = 3 arcminutes from boundary.
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1, moon_degree_in_sign=0.05)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=5, moon_degree_in_sign=15.0)

        res = evaluate_moon_to_moon_synastry(groom, bride)
        assert res.groom_navamsa_boundary_risk is True
        assert res.bride_navamsa_boundary_risk is False
        assert any("boundary" in w.lower() for w in res.warnings)


# ---------------------------------------------------------------------------
# 2. Lagna-to-Lagna Tests
# ---------------------------------------------------------------------------

class TestLagnaToLagnaSynastry:
    """Test suite for evaluate_lagna_to_lagna_synastry."""

    def test_samasaptaka_lagna_axis(self):
        """Mutual 7th Lagna axis (e.g., Aries-Libra) is Supportive."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=7, moon_sign=1)

        res = evaluate_lagna_to_lagna_synastry(groom, bride)
        assert res.lagna_sign_distance_g_to_b == 7
        assert res.lagna_sign_distance_b_to_g == 7
        assert res.lagna_sign_assessment == "Supportive"
        assert res.groom_lagna_in_bride_chart_house == 7
        assert res.bride_lagna_in_groom_chart_house == 7

    def test_trikona_lagna_axis(self):
        """Trine Lagna axis (e.g., Aries-Sagittarius, 1/9) is Supportive."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=9, moon_sign=1)

        res = evaluate_lagna_to_lagna_synastry(groom, bride)
        assert res.lagna_sign_distance_g_to_b == 9
        assert res.lagna_sign_distance_b_to_g == 5
        assert res.lagna_sign_assessment == "Supportive"

    def test_shadashtaka_lagna_axis(self):
        """6/8 Lagna axis (e.g., Aries-Virgo) is Challenging."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=6, moon_sign=1)

        res = evaluate_lagna_to_lagna_synastry(groom, bride)
        assert res.lagna_sign_distance_g_to_b == 6
        assert res.lagna_sign_assessment == "Challenging"

    def test_lagna_lord_natural_friendship(self):
        """Lagna lords Sun (Leo) and Mars (Aries) are mutual friends."""
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=5, moon_sign=1) # Leo (Sun)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=1) # Aries (Mars)

        res = evaluate_lagna_to_lagna_synastry(groom, bride)
        assert res.lagna_lord_relationship == "Friends"
        assert res.lagna_lord_friendship_score == 1.0


# ---------------------------------------------------------------------------
# 3. Marriage-Lord (7th Lord) Cross-Chart Tests
# ---------------------------------------------------------------------------

class TestMarriageLordCrossSynastry:
    """Test suite for evaluate_marriage_lord_cross_synastry."""

    def test_7th_lords_activation_of_marriage_houses(self):
        """Verify cross-placement of 7th lords in each other's marital houses."""
        # Groom: Lagna Aries (1) -> 7th house is Libra (7), lord is Venus.
        # Venus is at sign 2 (Taurus).
        # Bride: Lagna Taurus (2) -> Groom's Venus (sign 2) falls in Bride's 1st house (sign 2 from 2 = 1).
        # Bride: Lagna Taurus (2) -> 7th house is Scorpio (8), lord is Mars.
        # Mars is at sign 1 (Aries).
        # Groom: Lagna Aries (1) -> Bride's Mars (sign 1) falls in Groom's 1st house.
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=2, moon_sign=1)

        res = evaluate_marriage_lord_cross_synastry(groom, bride)
        assert res.groom_7th_lord == "Venus"
        assert res.bride_7th_lord == "Mars"
        assert res.groom_7th_lord_in_bride_house == 1
        assert res.bride_7th_lord_in_groom_house == 1
        assert res.seventh_lord_friendship_score >= 0.0

    def test_groom_7th_lord_in_bride_7th_house(self):
        """Groom's 7th lord falling in Bride's 7th house directly."""
        # Bride: Lagna Aries (1), 7th house is Libra (7).
        # Groom: 7th lord placed in Libra (sign 7).
        mars_sign_7 = _create_test_planet("Venus", sign_index=7, house=7)
        groom = _build_synastry_test_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=1,
            extra_planets={"Venus": mars_sign_7}
        )
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=1)

        res = evaluate_marriage_lord_cross_synastry(groom, bride)
        assert res.groom_7th_lord_in_bride_house == 7
        assert res.groom_7th_lord_in_bride_marriage_house is True


# ---------------------------------------------------------------------------
# 4. Venus & Jupiter Cross-Chart Tests
# ---------------------------------------------------------------------------

class TestVenusJupiterCrossSynastry:
    """Test suite for evaluate_venus_jupiter_cross_synastry."""

    def test_venus_and_jupiter_cross_placement(self):
        """Verify cross-placements and aspect evaluations."""
        # Groom: Venus in sign 2. Bride Lagna = 1 (Aries) -> house 2 (Kutumba - marriage house!)
        # Bride: Jupiter in sign 4. Groom Lagna = 1 (Aries) -> house 4 (Sukha - marriage house!)
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=1)

        res = evaluate_venus_jupiter_cross_synastry(groom, bride)
        assert res.groom_venus_in_bride_house == 2
        assert res.groom_venus_in_bride_marriage_house is True
        assert res.bride_jupiter_in_groom_house == 4
        assert res.bride_jupiter_in_groom_marriage_house is True
        assert res.venus_jupiter_friendship_score == 0.0  # Natural enemies/tension between Guru and Shukra

    def test_direct_aspect_venus_to_7th_house(self):
        """Venus in sign 1 aspects sign 7 (7th house) directly."""
        venus_sign_1 = _create_test_planet("Venus", sign_index=1, house=1)
        groom = _build_synastry_test_chart("g", Gender.MALE, lagna_sign=1, moon_sign=1, extra_planets={"Venus": venus_sign_1})
        bride = _build_synastry_test_chart("b", Gender.FEMALE, lagna_sign=1, moon_sign=1)

        res = evaluate_venus_jupiter_cross_synastry(groom, bride)
        # Sign 1 to Sign 7 is offset 7 -> direct Parashari aspect!
        assert res.groom_venus_aspects_bride_7th is True


# ---------------------------------------------------------------------------
# 5. Top-Level Bidirectional Synastry Pipeline & Determinism
# ---------------------------------------------------------------------------

class TestBidirectionalSynastryPipeline:
    """Test suite for evaluate_bidirectional_synastry pipeline."""

    def test_pipeline_returns_complete_structure(self):
        """Full pipeline produces valid BidirectionalSynastryResult."""
        groom = _build_synastry_test_chart("g1", Gender.MALE, lagna_sign=1, moon_sign=1)
        bride = _build_synastry_test_chart("b1", Gender.FEMALE, lagna_sign=7, moon_sign=7)

        result = evaluate_bidirectional_synastry(groom, bride)
        assert isinstance(result, BidirectionalSynastryResult)
        assert result.groom_person_id == "g1"
        assert result.bride_person_id == "b1"
        assert isinstance(result.moon_to_moon, MoonToMoonFinding)
        assert isinstance(result.lagna_to_lagna, LagnaToLagnaFinding)
        assert isinstance(result.marriage_lord_cross, MarriageLordCrossChartFinding)
        assert isinstance(result.venus_jupiter_cross, VenusJupiterCrossChartFinding)
        assert len(result.rule_sources) >= 5
        assert len(result.moon_to_moon.explanation_en) > 10
        assert len(result.moon_to_moon.explanation_ta) > 5

    def test_pipeline_strict_determinism(self):
        """Calling evaluate_bidirectional_synastry multiple times on identical inputs produces identical results."""
        groom = _build_synastry_test_chart("g_det", Gender.MALE, lagna_sign=4, moon_sign=9)
        bride = _build_synastry_test_chart("b_det", Gender.FEMALE, lagna_sign=10, moon_sign=3)

        res1 = evaluate_bidirectional_synastry(groom, bride)
        res2 = evaluate_bidirectional_synastry(groom, bride)

        assert res1.moon_to_moon.sign_distance_g_to_b == res2.moon_to_moon.sign_distance_g_to_b
        assert res1.lagna_to_lagna.lagna_sign_distance_g_to_b == res2.lagna_to_lagna.lagna_sign_distance_g_to_b
        assert res1.marriage_lord_cross.groom_7th_lord_in_bride_house == res2.marriage_lord_cross.groom_7th_lord_in_bride_house
        assert res1.strong_indicators == res2.strong_indicators
        assert res1.has_boundary_sensitivity == res2.has_boundary_sensitivity
