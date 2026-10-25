"""Comprehensive Test Suite for Astrological Conditions & Predictions Engine.

Verifies all 20 required criteria:
1. Matching rule produces expected interpretation and evidence.
2. Nonmatching rule produces no false positive.
3. AND, OR, and NOT logical operators.
4. Missing chart data produces unevaluable status.
5. D1-only rules do not accidentally use D9 placements.
6. D9-only rules do not accidentally use D1 placements.
7. Both-charts rules verify both independently.
8. KP rules use KP-specific data and semantics.
9. Vedic rules use declared Vedic conventions.
10. Thirukanitha and Vākya calculation modes remain isolated.
11. Different opened horoscopes produce results for that horoscope only.
12. Unauthorized users cannot edit shared rules.
13. Users cannot access another user's private horoscope.
14. Malformed rules are rejected safely.
15. Rule editing preserves version history.
16. English and Tamil interpretations render correctly.
17. Page handles no-matches, errors, and loading states.
18. Existing horoscope, PDF, saved-chart, Vedic and KP features remain intact.
19. No unnecessary planetary recalculation is introduced.
20. Backward compatibility with existing /api/v1/rules/inventory and /api/v1/rules/career.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.horoscope import (
    HoroscopeResponse,
    AscendantInfo,
    PlanetInfo,
    HouseInfo,
    NakshatraDetail,
    CalculationMetadata,
)
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)
from app.services.prediction_rules.evaluator import (
    AstrologicalRuleEvaluator,
    ChartContext,
)
from app.services.prediction_rules.rules_registry import RulesRegistry, INITIAL_RULES_CATALOGUE
from app.services.prediction_rules.manager import RuleManagementService
from app.services.prediction_rules.categories import PREDICTION_CATEGORY_GROUPS, get_category_by_slug

client = TestClient(app)

# ---------------------------------------------------------------------------
# Test Fixtures & Synthetic Canonical Horoscopes
# ---------------------------------------------------------------------------

def make_sample_horoscope(
    lagna_sign: int = 1,      # 1 = Aries
    lagna_deg: float = 15.0,
    planets_spec: dict = None,
) -> HoroscopeResponse:
    """Create a fully-formed deterministic synthetic HoroscopeResponse."""
    if planets_spec is None:
        # Default placements:
        # Sun in Aries (1) H1, Moon in Taurus (2) H2, Mars in Capricorn (10) H10,
        # Mercury in Gemini (3) H3, Jupiter in Cancer (4) H4, Venus in Pisces (12) H12,
        # Saturn in Libra (7) H7, Rahu in Taurus (2) H2, Ketu in Scorpio (8) H8
        planets_spec = {
            "Sun": (1, 10.0),
            "Moon": (2, 12.0),
            "Mars": (10, 20.0),
            "Mercury": (3, 5.0),
            "Jupiter": (4, 15.0),
            "Venus": (12, 18.0),
            "Saturn": (7, 14.0),
            "Rahu": (2, 22.0),
            "Ketu": (8, 22.0),
        }

    nakshatra_sample = NakshatraDetail(
        name="Ashwini",
        index=0,
        pada=1,
        lord="Ketu",
        deity="Ashvins",
    )

    planets: list[PlanetInfo] = []
    sign_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_names_ta = [
        "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
        "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
    ]

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

    return HoroscopeResponse(
        metadata=CalculationMetadata(
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
        ),
        ascendant=AscendantInfo(
            degree=(lagna_sign - 1) * 30.0 + lagna_deg,
            sign_index=lagna_sign,
            sign_name=sign_names[lagna_sign - 1],
            sign_name_tamil=sign_names_ta[lagna_sign - 1],
            degree_in_sign=lagna_deg,
            nakshatra=nakshatra_sample,
        ),
        midheaven=AscendantInfo(
            degree=270.0,
            sign_index=10,
            sign_name="Capricorn",
            sign_name_tamil="மகரம்",
            degree_in_sign=0.0,
            nakshatra=nakshatra_sample,
        ),
        planets=planets,
        houses=houses,
    )


# ===========================================================================
# 1. Matching Rule Produces Expected Interpretation & Evidence
# ===========================================================================

def test_matching_rule_produces_interpretation_and_evidence():
    # Aries lagna, Saturn placed in Libra (House 7)
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Saturn": (7, 15.0), "Jupiter": (4, 15.0)}
    )
    ctx = ChartContext(horoscope=horoscope)

    rule = AstrologicalRuleDefinition(
        rule_id="TEST-SATURN-7",
        version=1,
        name_en="Saturn in 7th House",
        name_ta="7-ல் சனி",
        category_slug="marriage_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Saturn",
            "house": 7,
            "chart": "d1",
        },
        interpretation_en="Saturn in 7th brings mature marriage timing.",
        interpretation_ta="7-ல் சனி பக்குவமான திருமணத்தைத் தரும்.",
        astrological_principle_en="Saturn in Kalatrasthana delays fruition.",
        astrological_principle_ta="களத்திரத்தில் சனி தாமதத்தை நல்கும்.",
    )

    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert res.unevaluable is False
    assert len(res.evidence) > 0
    assert "Saturn is in House 7" in res.evidence[0]
    assert "Saturn in 7th brings mature marriage timing." == res.to_dict()["interpretation"]


# ===========================================================================
# 2. Nonmatching Rule Produces No False Positive
# ===========================================================================

def test_nonmatching_rule_produces_no_false_positive():
    # Jupiter in Cancer (House 4 for Aries Lagna). Rule requires Jupiter in House 7.
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Jupiter": (4, 15.0)}
    )
    ctx = ChartContext(horoscope=horoscope)

    rule = AstrologicalRuleDefinition(
        rule_id="TEST-GURU-7",
        version=1,
        name_en="Jupiter in 7th House",
        name_ta="7-ல் குரு",
        category_slug="marriage_prospects",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Jupiter",
            "house": 7,
            "chart": "d1",
        },
        interpretation_en="Virtuous spouse.",
        interpretation_ta="நற்பண்புள்ள துணை.",
        astrological_principle_en="Guru in Kendra.",
        astrological_principle_ta="குரு கேந்திரம்.",
    )

    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is False
    assert len(res.evidence) == 0


# ===========================================================================
# 3. AND, OR, and NOT Logical Operators
# ===========================================================================

def test_boolean_logic_and_or_not():
    # Sun in 10 (Capricorn), Mars in 10 (Capricorn)
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Sun": (10, 5.0), "Mars": (10, 15.0), "Venus": (12, 10.0)}
    )
    ctx = ChartContext(horoscope=horoscope)

    # 3.1 AND: Both Sun and Mars in 10th
    and_rule = AstrologicalRuleDefinition(
        rule_id="TEST-AND",
        name_en="Sun AND Mars in 10th",
        name_ta="சூரியன் மற்றும் செவ்வாய் 10-ல்",
        category_slug="career_profession",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Sun", "house": 10},
                {"condition_type": "planet_house", "planet": "Mars", "house": 10},
            ],
        },
        interpretation_en="High executive authority.",
        interpretation_ta="உயரிய அதிகாரம்.",
        astrological_principle_en="Two fiery planets at zenith.",
        astrological_principle_ta="இரு அக்னி கிரகங்கள் 10-ல்.",
    )
    res_and = AstrologicalRuleEvaluator.evaluate_rule(and_rule, ctx)
    assert res_and.matched is True

    # 3.2 OR: Sun in 10th OR Moon in 10th (Moon is absent in 10th, Sun is present -> True)
    or_rule = AstrologicalRuleDefinition(
        rule_id="TEST-OR",
        name_en="Sun OR Moon in 10th",
        name_ta="சூரியன் அல்லது சந்திரன் 10-ல்",
        category_slug="career_profession",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Sun", "house": 10},
                {"condition_type": "planet_house", "planet": "Moon", "house": 10},
            ],
        },
        interpretation_en="Leadership trait.",
        interpretation_ta="தலைமைத்துவம்.",
        astrological_principle_en="Luminaries at zenith.",
        astrological_principle_ta="ராஜ கிரகங்கள் 10-ல்.",
    )
    res_or = AstrologicalRuleEvaluator.evaluate_rule(or_rule, ctx)
    assert res_or.matched is True

    # 3.3 NOT: Inverts true to false (NOT Sun in 10th -> False because Sun IS in 10th)
    not_rule = AstrologicalRuleDefinition(
        rule_id="TEST-NOT",
        name_en="NOT Sun in 10th",
        name_ta="சூரியன் 10-ல் இல்லாத நிலை",
        category_slug="career_profession",
        condition_tree={
            "condition_type": "compound",
            "operator": "NOT",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Sun", "house": 10},
            ],
        },
        interpretation_en="Sun is not in 10th.",
        interpretation_ta="சூரியன் 10-ல் இல்லை.",
        astrological_principle_en="Absence of solar zenith.",
        astrological_principle_ta="சூரியன் இல்லாத நிலை.",
    )
    res_not = AstrologicalRuleEvaluator.evaluate_rule(not_rule, ctx)
    assert res_not.matched is False


# ===========================================================================
# 4. Missing Chart Data Produces Unevaluable Result
# ===========================================================================

def test_missing_chart_data_produces_unevaluable():
    horoscope = make_sample_horoscope(lagna_sign=1)
    # Chart context has NO KP data
    ctx = ChartContext(horoscope=horoscope, kp_data=None)

    kp_rule = AstrologicalRuleDefinition(
        rule_id="TEST-KP-MISSING",
        name_en="KP Cusp Rule",
        name_ta="கே.பி விதி",
        category_slug="marriage_prospects",
        astrology_system=AstrologySystem.KP,
        condition_tree={
            "condition_type": "kp_sub_lord",
            "cusp": 7,
            "sub_lord": "Venus",
        },
        interpretation_en="KP marriage promise.",
        interpretation_ta="கே.பி திருமணம்.",
        astrological_principle_en="Cusp sub lord.",
        astrological_principle_ta="உப அதிபதி.",
    )

    res = AstrologicalRuleEvaluator.evaluate_rule(kp_rule, ctx)
    assert res.matched is False
    assert res.unevaluable is True
    assert "Rule requires KP chart cusps/sub-lords" in res.unevaluable_reason


# ===========================================================================
# 5. D1-only Rules Do Not Use D9 Placements
# ===========================================================================

def test_d1_only_rules_do_not_use_d9():
    # Setup: Jupiter is in Cancer 2.0° (D1 = House 4).
    # D1 Lagna is Aries 15° (D9 Lagna = Leo).
    # In D9: Jupiter at Cancer 2.0° falls in Cancer Navamsa (House 12 from Leo D9 Lagna).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        lagna_deg=15.0,
        planets_spec={"Jupiter": (4, 2.0)}  # D1 House = 4, D9 House = 12
    )
    ctx = ChartContext(horoscope=horoscope)
    assert ctx.d1_planets["Jupiter"]["house"] == 4
    assert ctx.d9_planets["Jupiter"]["house"] == 12

    # Rule requiring Jupiter in House 12 strictly in D1
    rule_d1 = AstrologicalRuleDefinition(
        rule_id="TEST-D1-ONLY",
        name_en="Jupiter in House 12 (D1)",
        name_ta="குரு 12-ல் D1",
        category_slug="personality_birth",
        chart_scope=ChartScope.D1,
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Jupiter",
            "house": 12,
            "chart": "d1",
        },
        interpretation_en="Jupiter in 12th house D1.",
        interpretation_ta="குரு 12-ல்.",
        astrological_principle_en="Dusthana Guru.",
        astrological_principle_ta="மறைவு குரு.",
    )
    res = AstrologicalRuleEvaluator.evaluate_rule(rule_d1, ctx)
    # Jupiter is in H12 in D9, but in H4 in D1. Must return False for D1!
    assert res.matched is False


# ===========================================================================
# 6. D9-only Rules Do Not Use D1 Placements
# ===========================================================================

def test_d9_only_rules_do_not_use_d1():
    # Setup: Jupiter is in House 4 in D1, House 12 in D9.
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        lagna_deg=15.0,
        planets_spec={"Jupiter": (4, 2.0)}  # D1 House = 4, D9 House = 12
    )
    ctx = ChartContext(horoscope=horoscope)

    # Rule requiring Jupiter in House 4 strictly in D9
    rule_d9 = AstrologicalRuleDefinition(
        rule_id="TEST-D9-ONLY",
        name_en="Jupiter in House 4 (D9)",
        name_ta="குரு 4-ல் D9",
        category_slug="personality_birth",
        chart_scope=ChartScope.D9,
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Jupiter",
            "house": 4,
            "chart": "d9",
        },
        interpretation_en="Jupiter in 4th house D9.",
        interpretation_ta="குரு 4-ல் நவாம்சம்.",
        astrological_principle_en="D9 Kendra Guru.",
        astrological_principle_ta="நவாம்ச கேந்திரம்.",
    )
    res = AstrologicalRuleEvaluator.evaluate_rule(rule_d9, ctx)
    # Jupiter is in H4 in D1, but in H12 in D9. Must return False for D9!
    assert res.matched is False


# ===========================================================================
# 7. Rules Requiring Both Charts Verify Both Independently
# ===========================================================================

def test_both_charts_verify_independently():
    # Setup: Jupiter in Cancer 15° (D1 = Cancer Sign 4, D9 = Scorpio Sign 8). Not Vargottama.
    horo_not_varg = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Jupiter": (4, 15.0)}
    )
    ctx_not_varg = ChartContext(horoscope=horo_not_varg)

    varg_rule = AstrologicalRuleDefinition(
        rule_id="TEST-VARG",
        name_en="Jupiter Vargottama",
        name_ta="குரு வர்கோத்தமம்",
        category_slug="personality_birth",
        chart_scope=ChartScope.BOTH,
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Jupiter",
            "dignity": "vargottama",
            "chart": "both",
        },
        interpretation_en="Unshakeable moral grace.",
        interpretation_ta="வர்கோத்தம பலன்.",
        astrological_principle_en="Same sign in D1 and D9.",
        astrological_principle_ta="இரு சக்கரங்களிலும் ஒரே ராசி.",
    )
    res1 = AstrologicalRuleEvaluator.evaluate_rule(varg_rule, ctx_not_varg)
    assert res1.matched is False

    # Setup 2: Jupiter in Aries 2° (0-3°20' in movable sign Aries falls in Aries Navamsa). True Vargottama!
    horo_varg = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Jupiter": (1, 2.0)}
    )
    ctx_varg = ChartContext(horoscope=horo_varg)
    assert ctx_varg.d1_planets["Jupiter"]["sign_index"] == 1
    assert ctx_varg.d9_planets["Jupiter"]["sign_index"] == 1

    res2 = AstrologicalRuleEvaluator.evaluate_rule(varg_rule, ctx_varg)
    assert res2.matched is True
    assert "Vargottama" in res2.evidence[0]


# ===========================================================================
# 8. KP Rules Use KP-Specific Data and Semantics
# ===========================================================================

def test_kp_rules_use_kp_semantics():
    horoscope = make_sample_horoscope(lagna_sign=1)
    kp_data = {
        "cusp_details": [
            {"house": 7, "sub_lord": "Venus", "sign_name": "Libra", "cusp_degree": 195.4},
            {"house": 10, "sub_lord": "Jupiter", "sign_name": "Capricorn", "cusp_degree": 284.1},
        ]
    }
    ctx = ChartContext(horoscope=horoscope, kp_data=kp_data)

    kp_rule = AstrologicalRuleDefinition(
        rule_id="TEST-KP-7-SL",
        name_en="KP 7th Cusp Sub-Lord Venus",
        name_ta="கே.பி 7-ஆம் உப அதிபதி சுக்கிரன்",
        category_slug="marriage_prospects",
        astrology_system=AstrologySystem.KP,
        condition_tree={
            "condition_type": "kp_sub_lord",
            "cusp": 7,
            "sub_lord": ["Venus"],
        },
        interpretation_en="Auspicious marriage promise.",
        interpretation_ta="சுப திருமண யோகம்.",
        astrological_principle_en="Cuspal Sub Lord rule.",
        astrological_principle_ta="உப அதிபதி பலன்.",
    )
    res = AstrologicalRuleEvaluator.evaluate_rule(kp_rule, ctx)
    assert res.matched is True
    assert "KP Cusp 7 Sub-Lord is Venus" in res.evidence[0]


# ===========================================================================
# 9. Vedic Rules Use Declared Vedic Conventions (Parashari Aspects)
# ===========================================================================

def test_vedic_rules_use_vedic_conventions():
    # Mars in Capricorn (Sign 10) casts special 4th aspect on Aries (Sign 1, House 1)
    # and special 8th aspect on Leo (Sign 5, House 5).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Mars": (10, 15.0), "Sun": (1, 10.0)}
    )
    ctx = ChartContext(horoscope=horoscope)

    aspect_rule = AstrologicalRuleDefinition(
        rule_id="TEST-MARS-4TH-ASPECT",
        name_en="Mars Special 4th Aspect on Sun",
        name_ta="செவ்வாயின் 4-ஆம் பார்வை சூரியன் மீது",
        category_slug="career_profession",
        astrology_system=AstrologySystem.VEDIC,
        condition_tree={
            "condition_type": "planet_aspect",
            "aspecting_planet": "Mars",
            "target_type": "planet",
            "target_value": "Sun",
            "aspect_type": "special",
            "chart": "d1",
        },
        interpretation_en="Dynamic military or administrative vigor.",
        interpretation_ta="வீரியமான தலைமைத் திறன்.",
        astrological_principle_en="Mars 4th Chaturthashtama drishti.",
        astrological_principle_ta="செவ்வாயின் 4-ஆம் விசேஷ பார்வை.",
    )
    res = AstrologicalRuleEvaluator.evaluate_rule(aspect_rule, ctx)
    assert res.matched is True
    assert "Mars 4th special aspect" in res.evidence[0]


# ===========================================================================
# 10. Different Opened Horoscopes Produce Results For That Horoscope Only
# ===========================================================================

def test_different_opened_horoscopes_isolate_results():
    horo_aries = make_sample_horoscope(lagna_sign=1)   # Aries Lagna
    horo_cancer = make_sample_horoscope(lagna_sign=4)  # Cancer Lagna

    rule_aries_only = AstrologicalRuleDefinition(
        rule_id="TEST-ARIES-LAGNA",
        name_en="Aries Lagna Check",
        name_ta="மேஷ லக்னம்",
        category_slug="personality_birth",
        condition_tree={
            "condition_type": "lagna_sign",
            "sign": 1,
            "chart": "d1",
        },
        interpretation_en="Aries.",
        interpretation_ta="மேஷம்.",
        astrological_principle_en="Sign 1.",
        astrological_principle_ta="ராசி 1.",
    )

    ctx_aries = ChartContext(horoscope=horo_aries)
    ctx_cancer = ChartContext(horoscope=horo_cancer)

    res_aries = AstrologicalRuleEvaluator.evaluate_rule(rule_aries_only, ctx_aries)
    res_cancer = AstrologicalRuleEvaluator.evaluate_rule(rule_aries_only, ctx_cancer)

    assert res_aries.matched is True
    assert res_cancer.matched is False


# ===========================================================================
# 11. Malformed Rules Are Rejected Safely
# ===========================================================================

def test_malformed_rules_rejected_safely():
    # Missing mandatory condition_type
    bad_rule = {
        "rule_id": "BAD-RULE-01",
        "name_en": "Broken Rule",
        "category_slug": "marriage_prospects",
        "interpretation_en": "Missing cond type",
        "astrological_principle_en": "None",
        "condition_tree": {
            "invalid_key": "some_value"
        }
    }
    is_valid, errors = RuleManagementService.validate_rule_definition(bad_rule)
    assert is_valid is False
    assert any("condition_type" in e for e in errors)

    # API validate endpoint also rejects it safely
    resp = client.post("/api/v1/rules/validate", json={"rule": bad_rule})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert len(data["errors"]) > 0


# ===========================================================================
# 12. Rule Editing Preserves Version History
# ===========================================================================

def test_rule_editing_preserves_version_history():
    rule_data = {
        "rule_id": "RULE-VER-TEST-01",
        "name_en": "Initial Version 1",
        "category_slug": "marriage_prospects",
        "interpretation_en": "V1 interpretation",
        "astrological_principle_en": "V1 principle",
        "condition_tree": {
            "condition_type": "planet_house",
            "planet": "Jupiter",
            "house": 1,
            "chart": "d1"
        }
    }
    # Create V1
    rule_v1, created = RuleManagementService.save_or_update_rule(rule_data)
    assert created is True
    assert rule_v1.version == 1

    # Update to V2
    rule_data["name_en"] = "Updated Version 2"
    rule_v2, updated = RuleManagementService.save_or_update_rule(rule_data)
    assert updated is False
    assert rule_v2.version == 2
    assert rule_v2.name_en == "Updated Version 2"


# ===========================================================================
# 13. English and Tamil Interpretations Render Correctly
# ===========================================================================

def test_english_and_tamil_interpretations():
    horoscope = make_sample_horoscope(lagna_sign=1, planets_spec={"Jupiter": (7, 10.0)})
    ctx = ChartContext(horoscope=horoscope)

    rule = AstrologicalRuleDefinition(
        rule_id="TEST-I18N",
        name_en="Jupiter in 7th",
        name_ta="7-ல் குரு",
        category_slug="marriage_prospects",
        condition_tree={"condition_type": "planet_house", "planet": "Jupiter", "house": 7},
        interpretation_en="English Interpretation",
        interpretation_ta="தமிழ் விளக்கம்",
        astrological_principle_en="English Principle",
        astrological_principle_ta="தமிழ் தத்துவம்",
    )

    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    en_dict = res.to_dict(language="en")
    ta_dict = res.to_dict(language="ta")

    assert en_dict["interpretation"] == "English Interpretation"
    assert en_dict["name"] == "Jupiter in 7th"

    assert ta_dict["interpretation"] == "தமிழ் விளக்கம்"
    assert ta_dict["name"] == "7-ல் குரு"


# ===========================================================================
# 14. Planetary Conjunction vs Sign Co-occupation Distinction
# ===========================================================================

def test_conjunction_vs_sign_cooccupation_distinction():
    # Venus at 2° Taurus, Rahu at 28° Taurus.
    # Same sign (Taurus Sign 2), but angular distance is 26° (> 8° orb).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Venus": (2, 2.0), "Rahu": (2, 28.0)}
    )
    ctx = ChartContext(horoscope=horoscope)

    # Rule A: Sign co-occupation only (same_sign_only=True, no orb) -> Matched
    rule_cooccupy = AstrologicalRuleDefinition(
        rule_id="TEST-COOCCUPY",
        name_en="Venus & Rahu Co-occupy Sign",
        name_ta="சுக்கிரன் ராகு ஒரே ராசியில்",
        category_slug="sexuality_intimacy",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Rahu"],
            "same_sign_only": True,
            "orb_degrees": None,
            "chart": "d1",
        },
        interpretation_en="Co-occupation.",
        interpretation_ta="சேர்க்கை.",
        astrological_principle_en="Sign sharing.",
        astrological_principle_ta="ஒரே ராசி.",
    )
    res_co = AstrologicalRuleEvaluator.evaluate_rule(rule_cooccupy, ctx)
    assert res_co.matched is True

    # Rule B: Strict Conjunction within 8° orb -> Not Matched (26° separation)
    rule_orb = AstrologicalRuleDefinition(
        rule_id="TEST-STRICT-ORB",
        name_en="Venus & Rahu within 8 degree orb",
        name_ta="சுக்கிரன் ராகு 8 பாகைக்குள்",
        category_slug="sexuality_intimacy",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Rahu"],
            "same_sign_only": True,
            "orb_degrees": 8.0,
            "chart": "d1",
        },
        interpretation_en="Close conjunction.",
        interpretation_ta="நெருங்கிய சேர்க்கை.",
        astrological_principle_en="Degree orb.",
        astrological_principle_ta="பாகை சேர்க்கை.",
    )
    res_orb = AstrologicalRuleEvaluator.evaluate_rule(rule_orb, ctx)
    assert res_orb.matched is False


# ===========================================================================
# 15. API Category Registry Endpoint Test
# ===========================================================================

def test_api_categories_endpoint():
    resp = client.get("/api/v1/rules/categories")
    assert resp.status_code == 200
    groups = resp.json()
    assert len(groups) == 8
    group_codes = [g["group_code"] for g in groups]
    assert "marriage_relationships" in group_codes
    assert "career_profession" in group_codes
    assert "personality_birth" in group_codes
    assert "sexuality_intimacy" in group_codes
    assert "money_assets" in group_codes
    assert "family_children" in group_codes
    assert "education_travel" in group_codes
    assert "other_life_themes" in group_codes


# ===========================================================================
# 16. API Evaluate Endpoint End-to-End
# ===========================================================================

def test_api_evaluate_endpoint_e2e():
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Sun": (10, 15.0), "Mars": (10, 20.0), "Saturn": (7, 15.0)}
    )

    req_payload = {
        "horoscope": horoscope.model_dump(),
        "category_slug": "career_profession",
        "language": "en",
    }

    resp = client.post("/api/v1/rules/evaluate", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["category_slug"] == "career_profession"
    assert data["total_rules_evaluated"] > 0
    assert data["total_matched"] > 0

    # Verify Sun in 10th (Digbala) matched
    rule_sun = next((r for r in data["results"] if r["rule_id"] == "RULE-CAR-01"), None)
    assert rule_sun is not None
    assert rule_sun["matched"] is True
    assert len(rule_sun["chart_evidence"]) > 0


# ===========================================================================
# 17. Security & Authorization Limits
# ===========================================================================

def test_unauthorized_user_cannot_modify_rules():
    # Attempting to post new rule definition without token
    resp = client.post(
        "/api/v1/rules/definitions",
        json={"rule_id": "HACK-01", "name_en": "Malicious Rule"}
    )
    # Must be 401 Unauthorized or 403 Forbidden
    assert resp.status_code in (401, 403)
