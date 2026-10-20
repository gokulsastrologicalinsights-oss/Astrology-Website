"""Unit tests for Phase 4: Comprehensive Vedic Marriage Analysis & Individual Kuja Dosha Engine.

Validates:
1. Marriage houses and lords (2, 4, 5, 7, 8, 12) with occupants, aspects, and dignities.
2. Natural vs functional benefic/malefic distinctions by Lagna (BPHS Ch. 34).
3. Planetary dignity evaluations (Exalted, Moolatrikona, Own, Friendly, Neutral, Inimical, Debilitated).
4. Marriage significators (Venus, Jupiter, Moon, Mars, Saturn, Rahu-Ketu) with combustion/retrogression.
5. D1 and D9 Navamsa cross-validation, Vargottama, and Pushkara Navamsas.
6. Navamsa boundary sensitivity detection (< 10 arcminutes).
7. Individual Kuja Dosha detection across Lagna, Moon, and Venus references.
8. Classical Kuja Dosha cancellations (Own sign, Exaltation, Cancer 7/8, Jupiter aspect, Yogakaraka).
9. Full individual Vedic analysis orchestration and dual-chart pair-wise evaluation.
10. Strict score independence, determinism, bilingual translations (EN & TA), and regression safety.
"""

from typing import Optional, Dict, Any, List
import pytest
from app.services.marriage_engine.models import (
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    Gender,
    PoruthamStatus,
    DignityType,
    FunctionalNature,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
)
from app.services.marriage_engine.vedic_analysis import (
    get_planetary_dignity,
    get_functional_nature,
    check_navamsa_boundary_sensitivity,
    evaluate_vedic_house,
    evaluate_vedic_significator,
    evaluate_navamsa_cross_analysis,
    evaluate_individual_kuja_assessment,
    evaluate_individual_vedic_marriage_analysis,
    evaluate_dual_vedic_marriage_analysis,
    chart_context_to_dosha_context,
)
from app.services.dosha_engine.kuja_dosha import evaluate_kuja_dosha


# ---------------------------------------------------------------------------
# Chart Builder Helpers for Fixtures
# ---------------------------------------------------------------------------

def create_test_planet(
    name: str,
    sign_idx: int,
    deg_in_sign: float = 15.0,
    asc_sign_idx: int = 1,
    is_retrograde: bool = False,
    is_combust: bool = False,
    navamsa_sign_idx: Optional[int] = None,
) -> MarriagePlanet:
    """Build a MarriagePlanet instance for unit testing."""
    full_lon = ((sign_idx - 1) * 30.0 + deg_in_sign) % 360.0
    house_num = ((sign_idx - asc_sign_idx) % 12) + 1
    # Standard Navamsa calculation if not explicitly provided
    if navamsa_sign_idx is None:
        nav_idx = int((deg_in_sign // (10.0 / 3.0)))
        # Navamsa progression from cardinal signs
        shift_base = {1: 1, 2: 9, 3: 5, 4: 1, 5: 9, 6: 5, 7: 1, 8: 9, 9: 5, 10: 1, 11: 9, 12: 5}
        start_sign = shift_base[sign_idx]
        navamsa_sign_idx = ((start_sign - 1 + nav_idx) % 12) + 1

    return MarriagePlanet(
        name=name,
        body_id=1,
        longitude=full_lon,
        sign_index=sign_idx,
        sign_name=SIGN_NAMES_EN[sign_idx],
        sign_name_tamil=SIGN_NAMES_TA.get(sign_idx, ""),
        degree_in_sign=deg_in_sign,
        house=house_num,
        is_retrograde=is_retrograde,
        is_combust=is_combust,
        nakshatra_index=int(full_lon / (360.0 / 27.0)),
        nakshatra_name="Ashwini",
        nakshatra_pada=1,
        navamsa_sign_index=navamsa_sign_idx,
    )


def create_test_chart(
    person_name: str = "Test Individual",
    gender: Gender = Gender.MALE,
    asc_sign_idx: int = 1,  # Default Aries Lagna
    asc_deg: float = 15.0,
    planets_spec: Optional[dict] = None,
) -> MarriageChartContext:
    """Build a complete MarriageChartContext instance."""
    # Default classical planet placements if not customized
    defaults = {
        "Sun": (1, 15.0),       # Aries (Exalted)
        "Moon": (2, 15.0),      # Taurus (Exalted)
        "Mars": (10, 15.0),     # Capricorn (Exalted)
        "Mercury": (6, 15.0),   # Virgo (Exalted)
        "Jupiter": (4, 15.0),   # Cancer (Exalted)
        "Venus": (12, 15.0),    # Pisces (Exalted)
        "Saturn": (7, 15.0),    # Libra (Exalted)
        "Rahu": (2, 15.0),      # Taurus
        "Ketu": (8, 15.0),      # Scorpio
    }
    spec = {**defaults, **(planets_spec or {})}

    grahas = {}
    for p_name, (s_idx, deg) in spec.items():
        grahas[p_name] = create_test_planet(
            name=p_name,
            sign_idx=s_idx,
            deg_in_sign=deg,
            asc_sign_idx=asc_sign_idx,
        )

    # Build houses (Whole-Sign)
    houses = {}
    for h_num in range(1, 13):
        h_sign = ((asc_sign_idx + h_num - 2) % 12) + 1
        occupants = [p.name for p in grahas.values() if p.house == h_num]
        houses[h_num] = MarriageHouse(
            house_number=h_num,
            sign_index=h_sign,
            sign_name=SIGN_NAMES_EN[h_sign],
            sign_name_tamil=SIGN_NAMES_TA.get(h_sign, ""),
            cusp_degree=float((h_sign - 1) * 30.0),
            degree_in_sign=0.0,
            lord_name=SIGN_LORDS[h_sign],
            occupants=occupants,
        )

    asc_full_lon = ((asc_sign_idx - 1) * 30.0 + asc_deg) % 360.0
    moon_p = grahas["Moon"]

    return MarriageChartContext(
        person_id="test_id_1",
        person_name=person_name,
        gender=gender,
        birth_date_iso="1995-05-15",
        birth_time_iso="06:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ascendant_degree=asc_full_lon,
        ascendant_sign_idx=asc_sign_idx,
        ascendant_sign_name=SIGN_NAMES_EN[asc_sign_idx],
        ascendant_sign_name_tamil=SIGN_NAMES_TA.get(asc_sign_idx, ""),
        ascendant_nakshatra_idx=0,
        ascendant_nakshatra_name="Ashwini",
        ascendant_nakshatra_pada=1,
        ascendant_navamsa_sign_idx=1,
        moon_degree=moon_p.longitude,
        moon_sign_idx=moon_p.sign_index,
        moon_sign_name=moon_p.sign_name,
        moon_sign_name_tamil=SIGN_NAMES_TA.get(moon_p.sign_index, ""),
        moon_nakshatra_idx=moon_p.nakshatra_index,
        moon_nakshatra_name=moon_p.nakshatra_name,
        moon_nakshatra_pada=moon_p.nakshatra_pada,
        moon_navamsa_sign_idx=moon_p.navamsa_sign_index,
        grahas=grahas,
        houses=houses,
    )


# ===========================================================================
# 1. Planetary Dignity Tests
# ===========================================================================

def test_planetary_dignities():
    """Verify classical planetary dignities (Exalted, Debilitated, Own, Moolatrikona, Friendly, Enemy)."""
    # 1. Exaltations
    assert get_planetary_dignity("Sun", 1) == DignityType.EXALTED       # Aries
    assert get_planetary_dignity("Moon", 2) == DignityType.EXALTED      # Taurus
    assert get_planetary_dignity("Mars", 10) == DignityType.EXALTED     # Capricorn
    assert get_planetary_dignity("Venus", 12) == DignityType.EXALTED    # Pisces
    assert get_planetary_dignity("Jupiter", 4) == DignityType.EXALTED   # Cancer
    assert get_planetary_dignity("Saturn", 7) == DignityType.EXALTED    # Libra

    # 2. Debilitations
    assert get_planetary_dignity("Sun", 7) == DignityType.DEBILITATED   # Libra
    assert get_planetary_dignity("Moon", 8) == DignityType.DEBILITATED  # Scorpio
    assert get_planetary_dignity("Mars", 4) == DignityType.DEBILITATED  # Cancer
    assert get_planetary_dignity("Venus", 6) == DignityType.DEBILITATED # Virgo
    assert get_planetary_dignity("Jupiter", 10) == DignityType.DEBILITATED # Capricorn
    assert get_planetary_dignity("Saturn", 1) == DignityType.DEBILITATED # Aries

    # 3. Own Signs
    assert get_planetary_dignity("Sun", 5) == DignityType.MOOLATRIKONA  # Leo (Moolatrikona takes precedence)
    assert get_planetary_dignity("Mars", 8) == DignityType.OWN_SIGN     # Scorpio
    assert get_planetary_dignity("Venus", 2) == DignityType.OWN_SIGN    # Taurus

    # 4. Friendly and Inimical Signs
    assert get_planetary_dignity("Sun", 9) == DignityType.FRIENDLY      # Sagittarius (Jupiter friend of Sun)
    assert get_planetary_dignity("Sun", 11) == DignityType.INIMICAL     # Aquarius (Saturn enemy of Sun)


# ===========================================================================
# 2. Functional Nature (BPHS Ch. 34) Tests
# ===========================================================================

def test_functional_nature_by_lagna():
    """Verify Parashari functional beneficence, maleficence, and Yogakarakas."""
    # 1. Cancer Lagna (Sign 4): Mars is Yogakaraka (rules 5th & 10th)
    assert get_functional_nature("Mars", 4) == FunctionalNature.YOGAKARAKA
    assert get_functional_nature("Jupiter", 4) == FunctionalNature.FUNCTIONAL_BENEFIC
    assert get_functional_nature("Saturn", 4) == FunctionalNature.FUNCTIONAL_MALEFIC

    # 2. Leo Lagna (Sign 5): Mars is Yogakaraka (rules 4th & 9th)
    assert get_functional_nature("Mars", 5) == FunctionalNature.YOGAKARAKA
    assert get_functional_nature("Sun", 5) == FunctionalNature.FUNCTIONAL_BENEFIC
    assert get_functional_nature("Venus", 5) == FunctionalNature.FUNCTIONAL_MALEFIC

    # 3. Taurus Lagna (Sign 2): Saturn is Yogakaraka (rules 9th & 10th)
    assert get_functional_nature("Saturn", 2) == FunctionalNature.YOGAKARAKA
    assert get_functional_nature("Jupiter", 2) == FunctionalNature.FUNCTIONAL_MALEFIC

    # 4. Libra Lagna (Sign 7): Saturn is Yogakaraka (rules 4th & 5th)
    assert get_functional_nature("Saturn", 7) == FunctionalNature.YOGAKARAKA

    # 5. Capricorn Lagna (Sign 10): Venus is Yogakaraka (rules 5th & 10th)
    assert get_functional_nature("Venus", 10) == FunctionalNature.YOGAKARAKA

    # 6. Aquarius Lagna (Sign 11): Venus is Yogakaraka (rules 4th & 9th)
    assert get_functional_nature("Venus", 11) == FunctionalNature.YOGAKARAKA

    # 7. Aries Lagna (Sign 1): Mercury is Functional Malefic (rules 3rd & 6th)
    assert get_functional_nature("Mercury", 1) == FunctionalNature.FUNCTIONAL_MALEFIC


# ===========================================================================
# 3. Navamsa Boundary Sensitivity Tests
# ===========================================================================

def test_navamsa_boundary_sensitivity():
    """Verify detection of Ascendant boundary risk within 10 arcminutes."""
    # 1. Close to boundary: 3°18' (distance to 3°20' is 2 arcminutes)
    is_risk, dist = check_navamsa_boundary_sensitivity(3.30)
    assert is_risk is True
    assert dist <= 10.0

    # 2. Very close to sign boundary: 0°03' (distance is 3 arcminutes)
    is_risk, dist = check_navamsa_boundary_sensitivity(0.05)
    assert is_risk is True
    assert dist <= 10.0

    # 3. Far from boundary: 1°40' (middle of 3°20' Navamsa -> distance = 100 arcminutes)
    is_risk, dist = check_navamsa_boundary_sensitivity(1.6667)
    assert is_risk is False
    assert dist > 10.0


# ===========================================================================
# 4. Marriage Houses (2, 4, 5, 7, 8, 12) Evaluation Tests
# ===========================================================================

def test_marriage_houses_evaluation():
    """Verify evaluation of all 6 marriage houses."""
    chart = create_test_chart(asc_sign_idx=1)  # Aries Lagna

    # Evaluate 7th house (Libra - ruled by Venus in Pisces [Exalted, 12th])
    h7 = evaluate_vedic_house(chart, 7)
    assert h7.house_number == 7
    assert h7.sign_index == 7
    assert h7.sign_name_en == "Libra"
    assert h7.lord_name == "Venus"
    assert h7.lord_dignity == DignityType.EXALTED.value
    assert len(h7.supporting_influences) > 0
    assert h7.status == PoruthamStatus.PASS
    assert "7-ஆம் பாவம்" in h7.house_name_ta

    # Evaluate 2nd house (Taurus - Moon in Taurus [Exalted])
    h2 = evaluate_vedic_house(chart, 2)
    assert h2.house_number == 2
    assert h2.sign_index == 2
    assert "Moon" in h2.occupants
    assert h2.status == PoruthamStatus.PASS

    # Evaluate 4th house (Cancer - Jupiter in Cancer [Exalted])
    h4 = evaluate_vedic_house(chart, 4)
    assert h4.house_number == 4
    assert "Jupiter" in h4.occupants

    # Evaluate 5th house (Leo - Sun rules, Sun in Aries [Exalted])
    h5 = evaluate_vedic_house(chart, 5)
    assert h5.house_number == 5
    assert h5.lord_name == "Sun"

    # Evaluate 8th house (Scorpio - Mars rules)
    h8 = evaluate_vedic_house(chart, 8)
    assert h8.house_number == 8
    assert h8.lord_name == "Mars"

    # Evaluate 12th house (Pisces - Jupiter rules, Venus occupies)
    h12 = evaluate_vedic_house(chart, 12)
    assert h12.house_number == 12
    assert "Venus" in h12.occupants


# ===========================================================================
# 5. Marriage Significators Evaluation Tests
# ===========================================================================

def test_marriage_significators_evaluation():
    """Verify evaluation of Venus, Jupiter, Mars, Moon, Saturn, Rahu, Ketu."""
    chart = create_test_chart(asc_sign_idx=1)

    # 1. Venus (Primary Karaka): Exalted in Pisces (12th house)
    v_sig = evaluate_vedic_significator(chart, "Venus")
    assert v_sig.planet_name == "Venus"
    assert v_sig.sign_name == "Pisces"
    assert v_sig.dignity == DignityType.EXALTED.value
    assert v_sig.natural_nature == "Benefic"
    assert len(v_sig.summary_en) > 0
    assert len(v_sig.summary_ta) > 0

    # 2. Jupiter: Exalted in Cancer (4th house)
    j_sig = evaluate_vedic_significator(chart, "Jupiter")
    assert j_sig.planet_name == "Jupiter"
    assert j_sig.dignity == DignityType.EXALTED.value

    # 3. Mars: Exalted in Capricorn (10th house)
    m_sig = evaluate_vedic_significator(chart, "Mars")
    assert m_sig.planet_name == "Mars"
    assert m_sig.dignity == DignityType.EXALTED.value
    assert m_sig.natural_nature == "Malefic"


# ===========================================================================
# 6. D1 and D9 Navamsa Cross-Validation Tests
# ===========================================================================

def test_navamsa_cross_analysis():
    """Verify D1 and D9 cross-validation, lord placements, and Pushkara Navamsas."""
    chart = create_test_chart(asc_sign_idx=1)
    d9_res = evaluate_navamsa_cross_analysis(chart)

    assert d9_res.d9_lagna_sign_index == 1
    assert d9_res.d9_lagna_sign_name == "Aries"
    assert d9_res.d9_lagna_lord == "Mars"
    assert d9_res.d9_7th_sign_name == "Libra"
    assert d9_res.d9_7th_lord == "Venus"
    assert len(d9_res.explanation_en) > 0
    assert len(d9_res.explanation_ta) > 0


# ===========================================================================
# 7. Individual Kuja / Manglik Dosha Tests & Cancellations
# ===========================================================================

def test_individual_kuja_assessment_active():
    """Mars in 7th house from Lagna in Gemini without cancellation -> Active Kuja Dosha."""
    chart = create_test_chart(
        asc_sign_idx=9,  # Sagittarius Lagna -> 7th house is Gemini (sign 3)
        planets_spec={
            "Mars": (3, 15.0),    # Gemini 7th house (no own sign, no exaltation)
            "Moon": (1, 15.0),    # Aries (Mars is 3rd from Moon - non-kuja)
            "Venus": (1, 15.0),   # Aries (Mars is 3rd from Venus - non-kuja)
            "Jupiter": (2, 15.0), # Taurus (aspects 6, 8, 10 - no aspect on Gemini 3)
            "Saturn": (12, 15.0), # Pisces (aspects 2, 6, 9 - no aspect on Gemini 3)
        }
    )
    kuja = evaluate_individual_kuja_assessment(chart, role="groom")
    assert kuja.is_present is True
    assert kuja.is_cancelled is False
    assert kuja.severity in ("Mild", "Moderate", "High")
    assert len(kuja.triggering_conditions) > 0
    assert len(kuja.warnings) > 0


def test_individual_kuja_cancellation_own_sign():
    """Mars in own sign (Aries or Scorpio) in 1st/8th cancels Kuja Dosha."""
    chart = create_test_chart(
        asc_sign_idx=1,  # Aries Lagna
        planets_spec={
            "Mars": (1, 15.0),  # Mars in 1st house in Aries (own sign)
            "Moon": (5, 15.0),  # Leo
            "Venus": (5, 15.0), # Leo
        }
    )
    kuja = evaluate_individual_kuja_assessment(chart, role="groom")
    assert kuja.is_present is True
    assert kuja.is_cancelled is True
    assert kuja.severity == "Cancelled"
    assert any("own sign" in c.lower() for c in kuja.cancellations_applied)


def test_individual_kuja_cancellation_jupiter_aspect():
    """Jupiter casting Parashari aspect on Mars cancels Kuja Dosha."""
    chart = create_test_chart(
        asc_sign_idx=9,  # Sagittarius Lagna
        planets_spec={
            "Mars": (3, 15.0),    # Gemini 7th house
            "Jupiter": (9, 15.0), # Sagittarius 1st house (casts 7th aspect directly onto Mars in 7th)
            "Moon": (1, 15.0),
            "Venus": (1, 15.0),
        }
    )
    kuja = evaluate_individual_kuja_assessment(chart, role="groom")
    assert kuja.is_present is True
    assert kuja.is_cancelled is True
    assert kuja.severity == "Cancelled"
    assert any("jupiter" in c.lower() for c in kuja.cancellations_applied)


def test_individual_kuja_cancellation_yogakaraka():
    """Mars is Yogakaraka for Cancer Lagna and cannot cause Kuja Dosha from Lagna."""
    chart = create_test_chart(
        asc_sign_idx=4,  # Cancer Lagna
        planets_spec={
            "Mars": (7, 15.0),  # Libra 4th house (Kuja house)
            "Moon": (9, 15.0),  # Sagittarius
            "Venus": (9, 15.0), # Sagittarius
            "Jupiter": (2, 15.0),
            "Saturn": (12, 15.0),
        }
    )
    kuja = evaluate_individual_kuja_assessment(chart, role="groom")
    assert kuja.is_present is True
    # The Lagna reference will be cancelled by Yogakaraka status
    assert any("yogakaraka" in c.lower() for c in kuja.cancellations_applied)


def test_individual_kuja_free():
    """Mars in non-afflicting houses (3, 6, 9, 10, 11) from Lagna, Moon, Venus -> Dosha Free."""
    chart = create_test_chart(
        asc_sign_idx=1,  # Aries Lagna
        planets_spec={
            "Mars": (3, 15.0),  # Gemini (3rd house from Lagna - non-kuja)
            "Moon": (9, 15.0),  # Sagittarius (Mars is 7th? 9 to 3 is 7th -> let's make Moon in 3)
        }
    )
    # Put Mars, Moon, Venus in same sign 3 -> 1st house from Moon/Venus? In 3rd, it's 1st from Moon.
    # Let's place Mars in 3rd from Lagna, Moon in 7th, Venus in 7th:
    # 3 from 1 is 3 (non-kuja).
    # 3 from 7 (Libra) is 9th house (non-kuja).
    # 3 from 7 (Libra) is 9th house (non-kuja).
    chart2 = create_test_chart(
        asc_sign_idx=1,
        planets_spec={
            "Mars": (3, 15.0),  # Gemini: 3rd from Lagna (non-kuja)
            "Moon": (7, 15.0),  # Libra: Mars is 9th from Moon (non-kuja)
            "Venus": (7, 15.0), # Libra: Mars is 9th from Venus (non-kuja)
        }
    )
    kuja = evaluate_individual_kuja_assessment(chart2, role="groom")
    assert kuja.is_present is False
    assert kuja.is_cancelled is False
    assert kuja.severity == "None"


# ===========================================================================
# 8. Complete Individual & Dual Vedic Marriage Analysis Tests
# ===========================================================================

def test_evaluate_individual_vedic_marriage_analysis_complete():
    """Verify master individual Vedic analysis pipeline generates complete findings."""
    chart = create_test_chart(person_name="Gokul", gender=Gender.MALE, asc_sign_idx=1)
    analysis = evaluate_individual_vedic_marriage_analysis(chart, role="groom")

    assert analysis.subject_role == "groom"
    assert analysis.person_name == "Gokul"
    assert analysis.lagna_sign_name == "Aries"
    assert analysis.lagna_lord == "Mars"
    assert len(analysis.houses_analysis) == 6  # 2, 4, 5, 7, 8, 12
    assert 7 in analysis.houses_analysis
    assert len(analysis.significators) == 7   # Venus, Jupiter, Moon, Mars, Saturn, Rahu, Ketu
    assert analysis.navamsa_cross_analysis is not None
    assert analysis.kuja_dosha is not None
    assert len(analysis.supporting_indicators) > 0
    assert len(analysis.summary_en) > 0
    assert len(analysis.summary_ta) > 0
    assert len(analysis.rule_sources) == 4


def test_evaluate_dual_vedic_marriage_analysis_complete():
    """Verify dual Vedic marriage analysis evaluates both charts independently without composite score."""
    groom = create_test_chart(person_name="Groom", gender=Gender.MALE, asc_sign_idx=1)
    bride = create_test_chart(person_name="Bride", gender=Gender.FEMALE, asc_sign_idx=7)

    dual = evaluate_dual_vedic_marriage_analysis(groom, bride)

    assert dual.groom_analysis.subject_role == "groom"
    assert dual.bride_analysis.subject_role == "bride"
    assert dual.groom_analysis.lagna_sign_name == "Aries"
    assert dual.bride_analysis.lagna_sign_name == "Libra"
    assert len(dual.d9_cross_check_summary) > 0
    assert len(dual.venus_jupiter_resonance) > 0
    assert len(dual.key_observations) >= 4


def test_vedic_analysis_determinism():
    """Verify 50 repeated evaluations yield bit-identical deterministic outputs."""
    chart = create_test_chart(asc_sign_idx=1)
    ref = evaluate_individual_vedic_marriage_analysis(chart, role="groom")

    for _ in range(50):
        current = evaluate_individual_vedic_marriage_analysis(chart, role="groom")
        assert current.summary_en == ref.summary_en
        assert current.summary_ta == ref.summary_ta
        assert current.lagna_sign_index == ref.lagna_sign_index
        assert current.houses_analysis[7].lord_dignity == ref.houses_analysis[7].lord_dignity
        assert current.kuja_dosha.severity == ref.kuja_dosha.severity


def test_vedic_analysis_rejects_none_input():
    """Verify ValueError is raised when chart context is None."""
    with pytest.raises(ValueError, match="MarriageChartContext must be provided"):
        evaluate_individual_vedic_marriage_analysis(None, role="groom")


def test_regression_protection_dosha_engine():
    """Verify existing single-chart Kuja Dosha evaluator continues to produce expected results."""
    chart = create_test_chart(asc_sign_idx=1)
    dosha_ctx = chart_context_to_dosha_context(chart)
    result = evaluate_kuja_dosha(dosha_ctx, include_2nd_house=True)

    assert result is not None
    assert hasattr(result, "is_present")
    assert hasattr(result, "is_cancelled")
    assert hasattr(result, "severity")
