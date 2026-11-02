"""Test suite for Kalyana Varma's Saravali classical rules codification."""

import pytest
from app.schemas.horoscope import (
    HoroscopeResponse,
    AscendantInfo,
    PlanetInfo,
    HouseInfo,
    NakshatraDetail,
    CalculationMetadata,
)
from app.services.prediction_rules.saravali_rules import SARAVALI_RULES
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.manager import RuleManagementService
from app.services.prediction_rules.categories import PREDICTION_CATEGORY_GROUPS, get_category_by_slug
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from app.services.yoga_engine.models import YogaChartContext
from app.services.yoga_engine.evaluators.raja_yogas import evaluate_raja_yogas
from app.services.yoga_engine.evaluators.arishta import evaluate_arishta_yogas


def make_test_horoscope(planets_spec: dict, lagna_sign: int = 1) -> HoroscopeResponse:
    """Create a synthetic HoroscopeResponse for testing rules."""
    nakshatra_sample = NakshatraDetail(name="Ashwini", index=0, pada=1, lord="Ketu", deity="Ashvins")
    sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sign_names_ta = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]

    planets: list[PlanetInfo] = []
    for p_name, (s_idx, deg) in planets_spec.items():
        planets.append(
            PlanetInfo(
                name=p_name,
                body_id=1,
                longitude=(s_idx - 1) * 30.0 + deg,
                latitude=0.0,
                distance_au=1.0,
                speed_deg_per_day=1.0,
                is_retrograde=False,
                sign_index=s_idx,
                sign_name=sign_names[s_idx - 1],
                sign_name_tamil=sign_names_ta[s_idx - 1],
                degree_in_sign=deg,
                nakshatra=nakshatra_sample,
            )
        )

    houses: list[HouseInfo] = []
    for h in range(1, 13):
        h_sign = ((lagna_sign - 1 + h - 1) % 12) + 1
        houses.append(
            HouseInfo(
                house_number=h,
                cusp_degree=(h_sign - 1) * 30.0,
                sign_index=h_sign,
                sign_name=sign_names[h_sign - 1],
                sign_name_tamil=sign_names_ta[h_sign - 1],
                degree_in_sign=0.0,
                nakshatra="Ashwini",
                pada=1,
                star_lord="Ketu",
            )
        )

    asc = AscendantInfo(
        degree=(lagna_sign - 1) * 30.0 + 15.0,
        sign_index=lagna_sign,
        sign_name=sign_names[lagna_sign - 1],
        sign_name_tamil=sign_names_ta[lagna_sign - 1],
        degree_in_sign=15.0,
        nakshatra=nakshatra_sample,
    )

    mid = AscendantInfo(
        degree=270.0,
        sign_index=10,
        sign_name="Capricorn",
        sign_name_tamil="மகரம்",
        degree_in_sign=0.0,
        nakshatra=nakshatra_sample,
    )

    meta = CalculationMetadata(
        engine="XALEN Ephemeris",
        birth_utc_iso="1995-04-15T09:30:00Z",
        julian_day_ut1=2449822.8958,
        local_timezone="Asia/Kolkata",
        utc_offset_hours=5.5,
        coordinates={"latitude": 13.0827, "longitude": 80.2707},
        ayanamsa_id=0,
        ayanamsa_name="Lahiri",
        ayanamsa_deg=23.75,
        house_system_id=0,
        house_system_name="WholeSign",
    )

    return HoroscopeResponse(
        metadata=meta,
        ascendant=asc,
        midheaven=mid,
        planets=planets,
        houses=houses,
    )


def test_saravali_rules_count_and_uniqueness():
    """Verify total rule count and uniqueness of rule IDs."""
    assert len(SARAVALI_RULES) >= 200
    rule_ids = [r.rule_id for r in SARAVALI_RULES]
    assert len(rule_ids) == len(set(rule_ids)), "Duplicate rule IDs found in SARAVALI_RULES"


def test_saravali_rules_validation():
    """Ensure all Saravali rules strictly pass AST validation without errors."""
    for rule in SARAVALI_RULES:
        is_valid, errors = RuleManagementService.validate_rule_definition(rule.model_dump())
        assert is_valid, f"Rule {rule.rule_id} failed validation: {errors}"


def test_saravali_categories_and_subcategories():
    """Verify all Saravali rules have registered categories and subcategories."""
    saravali_cat = get_category_by_slug("saravali_classics")
    assert saravali_cat is not None
    valid_subcats = {s["slug"] for s in saravali_cat.get("subcategories", [])}

    for rule in SARAVALI_RULES:
        assert rule.category_slug == "saravali_classics"
        assert rule.subcategory in valid_subcats, f"Rule {rule.rule_id} has invalid subcategory: {rule.subcategory}"


def test_rules_registry_contains_saravali():
    """Verify RulesRegistry includes all Saravali rules."""
    saravali_in_registry = RulesRegistry.get_rules_for_category("saravali_classics")
    assert len(saravali_in_registry) >= 200
    assert RulesRegistry.count() >= 595


def test_saravali_bhava_phala_evaluation():
    """Test evaluation of Bhava Phala rules on a synthetic test chart."""
    # Sun in Aries (1) H1, Moon in Taurus (2) H2, Mars in Aries (1) H1
    # Mercury in Taurus (2) H2, Jupiter in Cancer (4) H4, Saturn in Libra (7) H7
    # Venus in Pisces (12) H12, Rahu in Gemini (3) H3, Ketu in Sagittarius (9) H9
    planets_spec = {
        "Sun": (1, 10.0),
        "Moon": (2, 3.0),
        "Mars": (1, 15.0),
        "Mercury": (2, 10.0),
        "Jupiter": (4, 5.0),
        "Saturn": (7, 20.0),
        "Venus": (12, 27.0),
        "Rahu": (3, 15.0),
        "Ketu": (9, 15.0),
    }
    horo = make_test_horoscope(planets_spec, lagna_sign=1)
    ctx = ChartContext(horoscope=horo)

    # 1. Sun in 1st house should match
    sun_1_rule = RulesRegistry.get_rule_by_id("RULE-SARAVALI-BHAVA-SUN-01")
    assert sun_1_rule is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(sun_1_rule, ctx)
    assert res.matched is True

    # 2. Conjunction Sun + Mars in 1st house should match
    sun_mars_conj = RulesRegistry.get_rule_by_id("RULE-SARAVALI-CONJ-SUN-MAR")
    assert sun_mars_conj is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(sun_mars_conj, ctx)
    assert res.matched is True

    # 3. Two planets in Angles (Sun and Jupiter) should match
    sun_jup_kendra = RulesRegistry.get_rule_by_id("RULE-SARAVALI-KENDRA-SUN-JUP")
    assert sun_jup_kendra is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(sun_jup_kendra, ctx)
    assert res.matched is True

    # 4. Multi-planet exaltation: Sun (Aries), Moon (Taurus), Jupiter (Cancer), Saturn (Libra), Venus (Pisces) = 5 exalted!
    exalt_3 = RulesRegistry.get_rule_by_id("RULE-SARAVALI-RAJA-EXALTED-3PLANETS")
    assert exalt_3 is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(exalt_3, ctx)
    assert res.matched is True


def test_yoga_engine_saravali_additions():
    """Verify Pushkala, Chandradhi, and Lagnadhi yogas evaluate in Yoga engine."""
    # Test chart with:
    # Lagna: Aries (Sign 1)
    # Moon: Taurus (Sign 2), Moon dispositor = Venus
    # Venus in 10th (Capricorn - Kendra)
    # Jupiter in 1st (Aries - Kendra, in Lagna)
    # Mercury in 7th (Libra - in 6th from Moon)
    class P:
        def __init__(self, name, sign_index, deg):
            self.name = name
            self.sign_index = sign_index
            self.longitude = (sign_index - 1) * 30.0 + deg
            self.degree_in_sign = deg
            self.is_retrograde = False

    planets = [
        P("Sun", 10, 10.0),
        P("Moon", 2, 9.0),      # Taurus 9.0° -> Exactly Saravali fateful degree!
        P("Mars", 1, 15.0),
        P("Mercury", 7, 15.0),
        P("Jupiter", 1, 5.0),
        P("Venus", 10, 15.0),
        P("Saturn", 11, 15.0),
        P("Rahu", 3, 15.0),
        P("Ketu", 9, 15.0),
    ]

    ctx = YogaChartContext(planets=planets, ascendant_sign_idx=1)

    # 1. Raja Yogas
    raja_results = evaluate_raja_yogas(ctx)
    yoga_ids = {y.id: y for y in raja_results}

    assert "pushkala_yoga" in yoga_ids
    pushkala = yoga_ids["pushkala_yoga"]
    assert pushkala.is_qualifying is True

    # 2. Arishta Fateful Degrees of the Moon
    arishta_results = evaluate_arishta_yogas(ctx)
    arishta_ids = {y.id: y for y in arishta_results}

    assert "saravali_moon_fateful_degrees" in arishta_ids
    fatal_moon = arishta_ids["saravali_moon_fateful_degrees"]
    assert fatal_moon.is_qualifying is True
    # And since Jupiter is in Lagna (Kendra), status should be Mitigated!
    assert fatal_moon.status == "Mitigated"
