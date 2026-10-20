"""Test suite for Phase 8 Composite Marriage Compatibility Assessment.

Verifies:
1. Consistent favorable inputs -> FAVOURABLE_UNDER_SELECTED_RULES.
2. Mixed inputs -> MIXED_OR_CONDITIONAL.
3. Conflicting traditional systems (Porutham Favorable vs Ashtakoota Unfavorable).
4. Dual tradition rejection -> UNFAVOURABLE_UNDER_SELECTED_RULES.
5. Missing foundational data -> INDETERMINATE.
6. Unsupported KP outputs handled gracefully.
7. Birth-time boundary sensitivity detected and recorded.
8. Existing individual Kuja Dosha preserved after mutual Samadosham mitigation.
9. Rajju tradition-specific critical veto (Rajju Thatu) -> UNFAVOURABLE.
10. Vedha tradition-specific critical veto -> UNFAVOURABLE.
11. Ashtakoota uncancelled Nadi Dosha critical veto -> UNFAVOURABLE.
12. No double-counting of scores (Porutham and Ashtakoota scores remain strictly unmerged).
13. No mixing of incompatible score scales (independent inspectable sections).
14. No invented weights or thresholds (exact canonical boundaries from RULE_SOURCE_REGISTER).
15. Deterministic repeated results across runs.
16. Input immutability (input contexts remain unaltered).
17. Explainability and source identifiers (decision path and rule citations populated).
18. Explicit indeterminate behavior for empty and partial inputs.
19. Partial input validation with partial category evaluations.
20. Bilingual disclaimer availability (English and Tamil).
21. Backward compatibility with existing result models.
22. Non-mutation of underlying calculation values.
"""

import copy
import pytest
from app.schemas.marriage import (
    TamilPoruthamSummary,
    AshtakootaSummary,
    PoruthamDetailItem,
    KootaDetailItem,
)
from app.services.marriage_engine.models import (
    Gender,
    CompatibilityOutcome,
    RuleEvaluationStatus,
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    DualVedicAnalysis,
    IndividualVedicAnalysis,
    IndividualKujaAssessment,
    VedicHouseFinding,
    MutualDoshaAnalysisResult,
    MutualKujaResult,
    PapasamyaResult,
    SamadoshamOutcome,
    PapasamyaVerdict,
    BidirectionalSynastryResult,
    MoonToMoonFinding,
    LagnaToLagnaFinding,
    MarriageLordCrossChartFinding,
    VenusJupiterCrossChartFinding,
    KpMarriageAnalysisResult,
    KpIndividualAnalysis,
    KpCslFinding,
    KpSignificatorsFinding,
    KpRulingPlanetsFinding,
    KpTimingFinding,
    KpPromiseVerdict,
    ConflictType,
    ConflictFinding,
    CategoryVerdict,
    CompositeMarriageAssessment,
)
from app.services.marriage_engine.composite_assessment import (
    evaluate_composite_marriage_assessment,
    COMPOSITE_DISCLAIMER_EN,
    COMPOSITE_DISCLAIMER_TA,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def favorable_porutham():
    """Favorable Tamil Porutham (8.0 matches, Rajju=PASS, Vedha=PASS)."""
    return TamilPoruthamSummary(
        poruthams={},
        total_score=8.0,
        max_score=10.0,
        aggregate_verdict="Uthama",
        rajju_status="PASS",
        vedha_status="PASS",
        summary_notes=["8 out of 10 Poruthams match favorably."],
    )


@pytest.fixture
def favorable_ashtakoota():
    """Favorable Ashtakoota (28.0 points, Nadi=Clear, Bhakoot=Clear)."""
    return AshtakootaSummary(
        kootas={},
        total_points=28.0,
        max_points=36.0,
        minimum_threshold=18.0,
        is_threshold_met=True,
        nadi_dosha_present=False,
        nadi_dosha_cancelled=False,
        bhakoot_dosha_present=False,
        bhakoot_dosha_cancelled=False,
        summary_notes=["28.0 points scored out of 36.0."],
    )


@pytest.fixture
def favorable_mutual_doshas():
    """Favorable Mutual Kuja Samadosham & Favorable Papasamya."""
    kuja = MutualKujaResult(
        status=RuleEvaluationStatus.NOT_DETECTED,
        mutual_balance=SamadoshamOutcome.MUTUALLY_MATCHED,
        groom_severity="None",
        bride_severity="None",
        groom_effective_intensity=0.0,
        bride_effective_intensity=0.0,
        triggering_comparison="Both charts free from Kuja",
        cancellations_or_mitigations_applied=["Both charts free from Kuja affliction."],
    )
    papa_g = PapasamyaResult(
        subject_role="groom",
        lagna_papam=1.0,
        moon_papam=1.0,
        venus_papam=1.5,
        total_papam=3.5,
        breakdown_by_planet={"Mars": 1.0, "Saturn": 1.0, "Rahu": 0.5, "Ketu": 0.5, "Sun": 0.5},
        placements_detail=[],
        explanation_en="Groom Papam",
        explanation_ta="மணமகன் பாபம்",
    )
    papa_b = PapasamyaResult(
        subject_role="bride",
        lagna_papam=1.0,
        moon_papam=1.0,
        venus_papam=1.5,
        total_papam=3.5,
        breakdown_by_planet={"Mars": 1.0, "Saturn": 1.0, "Rahu": 0.5, "Ketu": 0.5, "Sun": 0.5},
        placements_detail=[],
        explanation_en="Bride Papam",
        explanation_ta="மணமகள் பாபம்",
    )
    return MutualDoshaAnalysisResult(
        groom_kuja=None,
        bride_kuja=None,
        samadosham=kuja,
        groom_papasamya=papa_g,
        bride_papasamya=papa_b,
        papasamya_verdict=PapasamyaVerdict.FAVORABLE,
        papasamya_diff_percent=0.0,
        papasamya_explanation_en="Balanced",
        papasamya_explanation_ta="சமநிலை",
    )


def _build_test_chart_for_synastry(person_id: str, gender: Gender, lagna_sign: int, moon_sign: int) -> MarriageChartContext:
    from app.services.marriage_engine.models import SIGN_NAMES_EN, SIGN_NAMES_TA
    asc_degree = (lagna_sign - 1) * 30.0 + 15.0
    moon_degree = (moon_sign - 1) * 30.0 + 15.0
    moon_house = ((moon_sign - lagna_sign) % 12) + 1
    grahas = {
        "Moon": MarriagePlanet("Moon", 1, moon_degree, moon_sign, SIGN_NAMES_EN[moon_sign], SIGN_NAMES_TA[moon_sign], 15.0, moon_house, 1.0, False, 0, "Ashwini", 1, 1),
        "Venus": MarriagePlanet("Venus", 3, (lagna_sign - 1) * 30.0 + 10.0, lagna_sign, SIGN_NAMES_EN[lagna_sign], SIGN_NAMES_TA[lagna_sign], 10.0, 1, 1.0, False, 0, "Ashwini", 1, 1),
        "Jupiter": MarriagePlanet("Jupiter", 5, (lagna_sign - 1) * 30.0 + 20.0, lagna_sign, SIGN_NAMES_EN[lagna_sign], SIGN_NAMES_TA[lagna_sign], 20.0, 1, 1.0, False, 0, "Ashwini", 1, 1),
        "Mars": MarriagePlanet("Mars", 4, (lagna_sign - 1) * 30.0 + 5.0, lagna_sign, SIGN_NAMES_EN[lagna_sign], SIGN_NAMES_TA[lagna_sign], 5.0, 1, 1.0, False, 0, "Ashwini", 1, 1),
        "Sun": MarriagePlanet("Sun", 0, (lagna_sign - 1) * 30.0 + 25.0, lagna_sign, SIGN_NAMES_EN[lagna_sign], SIGN_NAMES_TA[lagna_sign], 25.0, 1, 1.0, False, 0, "Ashwini", 1, 1),
    }
    houses = {
        1: MarriageHouse(1, lagna_sign, SIGN_NAMES_EN[lagna_sign], SIGN_NAMES_TA[lagna_sign], asc_degree, 15.0, "Mars"),
        7: MarriageHouse(7, ((lagna_sign + 5) % 12) + 1, "Libra", "துலாம்", (asc_degree + 180.0) % 360.0, 15.0, "Venus"),
    }
    return MarriageChartContext(
        person_id=person_id,
        person_name=person_id,
        gender=gender,
        birth_date_iso="1995-05-15",
        birth_time_iso="06:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
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
        moon_nakshatra_idx=0,
        moon_nakshatra_name="Ashwini",
        moon_nakshatra_pada=1,
        moon_navamsa_sign_idx=1,
        grahas=grahas,
        houses=houses,
    )


@pytest.fixture
def favorable_synastry():
    """Favorable Bidirectional Synastry with Samasaptaka Moon and Lagna."""
    from app.services.marriage_engine.synastry import evaluate_bidirectional_synastry
    g_ctx = _build_test_chart_for_synastry("GROOM", Gender.MALE, lagna_sign=1, moon_sign=2)
    b_ctx = _build_test_chart_for_synastry("BRIDE", Gender.FEMALE, lagna_sign=7, moon_sign=8)
    return evaluate_bidirectional_synastry(g_ctx, b_ctx)


@pytest.fixture
def favorable_kp():
    """Favorable KP Marriage Analysis Result."""
    g_csl = KpCslFinding(
        person_id="GROOM", cusp_number=7, sub_lord="Jupiter",
        signified_houses=[2, 7, 11], supporting_houses_signified=[2, 7, 11],
        verdict=KpPromiseVerdict.FAVORABLE,
    )
    b_csl = KpCslFinding(
        person_id="BRIDE", cusp_number=7, sub_lord="Venus",
        signified_houses=[2, 7, 11], supporting_houses_signified=[2, 7, 11],
        verdict=KpPromiseVerdict.FAVORABLE,
    )
    g_ind = KpIndividualAnalysis(
        person_id="GROOM", person_name="Groom", gender=Gender.MALE,
        csl_7th=g_csl, significators=KpSignificatorsFinding(person_id="GROOM", target_house=7),
        ruling_planets=KpRulingPlanetsFinding(person_id="GROOM"),
        timing=KpTimingFinding(person_id="GROOM", overall_timing_verdict=KpPromiseVerdict.FAVORABLE),
    )
    b_ind = KpIndividualAnalysis(
        person_id="BRIDE", person_name="Bride", gender=Gender.FEMALE,
        csl_7th=b_csl, significators=KpSignificatorsFinding(person_id="BRIDE", target_house=7),
        ruling_planets=KpRulingPlanetsFinding(person_id="BRIDE"),
        timing=KpTimingFinding(person_id="BRIDE", overall_timing_verdict=KpPromiseVerdict.FAVORABLE),
    )
    return KpMarriageAnalysisResult(
        groom_analysis=g_ind,
        bride_analysis=b_ind,
        shared_ruling_planets=["Venus", "Jupiter"],
        ruling_planets_agreement_level="MODERATE",
    )


@pytest.fixture
def sample_chart_context():
    """Mock MarriageChartContext for testing non-mutation."""
    return MarriageChartContext(
        person_id="P_GROOM_01",
        person_name="Sundar",
        gender=Gender.MALE,
        birth_date_iso="1995-05-15",
        birth_time_iso="06:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ascendant_degree=55.0,
        ascendant_sign_idx=2,
        ascendant_sign_name="Taurus",
        ascendant_sign_name_tamil="ரிஷபம்",
        ascendant_nakshatra_idx=3,
        ascendant_nakshatra_name="Rohini",
        ascendant_nakshatra_pada=4,
        ascendant_navamsa_sign_idx=10,
        moon_degree=215.0,
        moon_sign_idx=8,
        moon_sign_name="Scorpio",
        moon_sign_name_tamil="விருச்சிகம்",
        moon_nakshatra_idx=16,
        moon_nakshatra_name="Anuradha",
        moon_nakshatra_pada=2,
        moon_navamsa_sign_idx=5,
        grahas={
            "Sun": MarriagePlanet("Sun", 30.0, 2, "Taurus", 2, "Krittika", 2, 10, 12, False, False),
            "Moon": MarriagePlanet("Moon", 215.0, 8, "Scorpio", 16, "Anuradha", 2, 5, 7, False, False),
            "Venus": MarriagePlanet("Venus", 10.0, 1, "Aries", 0, "Ashwini", 3, 3, 11, False, False),
            "Jupiter": MarriagePlanet("Jupiter", 240.0, 9, "Sagittarius", 18, "Mula", 1, 1, 6, False, False),
        },
        houses={
            1: MarriageHouse(1, 2, "Taurus", "ரிஷபம்", 55.0, 25.0, "Venus"),
            7: MarriageHouse(7, 8, "Scorpio", "விருச்சிகம்", 235.0, 25.0, "Mars"),
        },
    )


# ---------------------------------------------------------------------------
# Unit Tests (22 Tests)
# ---------------------------------------------------------------------------

def test_01_consistent_favorable_inputs(favorable_porutham, favorable_ashtakoota, favorable_mutual_doshas, favorable_synastry, favorable_kp):
    """Test 1: All lenses favorable -> FAVOURABLE_UNDER_SELECTED_RULES."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        mutual_doshas=favorable_mutual_doshas,
        synastry=favorable_synastry,
        kp_marriage=favorable_kp,
    )
    assert res.overall_outcome == CompatibilityOutcome.FAVOURABLE_UNDER_SELECTED_RULES
    assert res.category_verdicts["tamil_porutham"].status == "FAVORABLE"
    assert res.category_verdicts["ashtakoota"].status == "FAVORABLE"
    assert len(res.major_supportive_indicators) > 0


def test_02_mixed_inputs_verdict(favorable_porutham, favorable_mutual_doshas):
    """Test 2: Moderate Ashtakoota score (19.0) with favorable Porutham -> MIXED_OR_CONDITIONAL."""
    moderate_ashtakoota = AshtakootaSummary(
        kootas={}, total_points=19.0, max_points=36.0, minimum_threshold=18.0,
        is_threshold_met=True, nadi_dosha_present=False, bhakoot_dosha_present=False,
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=moderate_ashtakoota,
        mutual_doshas=favorable_mutual_doshas,
    )
    assert res.overall_outcome == CompatibilityOutcome.MIXED_OR_CONDITIONAL
    assert res.category_verdicts["ashtakoota"].status == "MIXED"


def test_03_conflicting_traditional_systems(favorable_porutham):
    """Test 3: Porutham Favorable (8.0) but Ashtakoota Unfavorable (14.0) -> TRADITIONAL_SYSTEM_DIVERGENCE recorded."""
    unfavorable_ashtakoota = AshtakootaSummary(
        kootas={}, total_points=14.0, max_points=36.0, minimum_threshold=18.0,
        is_threshold_met=False, nadi_dosha_present=False, bhakoot_dosha_present=False,
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=unfavorable_ashtakoota,
    )
    assert res.overall_outcome in (CompatibilityOutcome.MIXED_OR_CONDITIONAL, CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES)
    conflict_types = [c.conflict_type for c in res.conflicting_findings]
    assert ConflictType.TRADITIONAL_SYSTEM_DIVERGENCE in conflict_types


def test_04_dual_tradition_unfavorable():
    """Test 4: Both Tamil Porutham (< 5.0) and Ashtakoota (< 18.0) unfavorable -> UNFAVOURABLE_UNDER_SELECTED_RULES."""
    unf_porutham = TamilPoruthamSummary(
        poruthams={}, total_score=3.5, max_score=10.0, aggregate_verdict="Adhama",
        rajju_status="PASS", vedha_status="PASS",
    )
    unf_ashtakoota = AshtakootaSummary(
        kootas={}, total_points=12.0, max_points=36.0, minimum_threshold=18.0,
        is_threshold_met=False, nadi_dosha_present=False, bhakoot_dosha_present=False,
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=unf_porutham,
        ashtakoota=unf_ashtakoota,
    )
    assert res.overall_outcome == CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
    assert res.category_verdicts["tamil_porutham"].status == "UNFAVORABLE"
    assert res.category_verdicts["ashtakoota"].status == "UNFAVORABLE"


def test_05_missing_data_indeterminate():
    """Test 5: All components missing / None -> INDETERMINATE."""
    res = evaluate_composite_marriage_assessment()
    assert res.overall_outcome == CompatibilityOutcome.INDETERMINATE
    assert len(res.missing_or_uncertain_evidence) > 0


def test_06_unsupported_kp_outputs(favorable_porutham, favorable_ashtakoota):
    """Test 6: Unsupported / None KP outputs handled gracefully without failing composite evaluation."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        kp_marriage=None,
    )
    assert res.overall_outcome == CompatibilityOutcome.FAVOURABLE_UNDER_SELECTED_RULES
    assert res.category_verdicts["kp_promise"].status == "INDETERMINATE"
    assert "KP 7th Cuspal Sub-Lord Promise data missing or indeterminate." in res.missing_or_uncertain_evidence


def test_07_birth_time_boundary_sensitivity_detected(favorable_porutham, favorable_ashtakoota, favorable_synastry):
    """Test 7: Navamsa boundary proximity triggers BIRTH_TIME_BOUNDARY_SENSITIVITY conflict."""
    favorable_synastry.has_boundary_sensitivity = True
    favorable_synastry.boundary_sensitivity_notes = ["Moon within 12 arcmin of D9 boundary."]

    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        synastry=favorable_synastry,
    )
    conflict_types = [c.conflict_type for c in res.conflicting_findings]
    assert ConflictType.BIRTH_TIME_BOUNDARY_SENSITIVITY in conflict_types
    assert any("rectification" in r.lower() for r in res.recommended_astrologer_review)


def test_08_existing_individual_kuja_preserved_after_samadosham(favorable_porutham, favorable_ashtakoota):
    """Test 8: Individual Kuja Dosha is preserved in findings even when Samadosham reports MUTUALLY_MATCHED."""
    # Groom has active Kuja Dosha
    g_kuja = IndividualKujaAssessment(
        subject_role="groom", is_present=True, is_cancelled=False, severity="Medium",
        house_convention="South Indian (1, 2, 4, 7, 8, 12)",
        mars_longitude=215.0, mars_sign_index=8, mars_sign_name="Scorpio", mars_degree_in_sign=5.0,
        mars_house_from_lagna=7, mars_house_from_moon=1, mars_house_from_venus=6,
        effective_intensity_percent=60.0,
    )
    groom_vedic = IndividualVedicAnalysis(
        subject_role="groom", person_name="Groom", gender="male",
        lagna_sign_index=1, lagna_sign_name="Aries", lagna_sign_name_tamil="மேஷம்",
        lagna_degree=15.0, lagna_lord="Mars", lagna_lord_house=1, lagna_lord_dignity="Own",
        kuja_dosha=g_kuja,
    )

    # Mutual Samadosham matches it
    mk = MutualKujaResult(
        status=RuleEvaluationStatus.DETECTED,
        mutual_balance=SamadoshamOutcome.MUTUALLY_MATCHED,
        groom_severity="Medium", bride_severity="Medium",
        groom_effective_intensity=60.0, bride_effective_intensity=60.0,
        triggering_comparison="Equal Mars intensity",
        cancellations_or_mitigations_applied=["Equal Mars intensity balances mutual interaction."],
    )
    mutual_doshas = MutualDoshaAnalysisResult(
        groom_kuja=g_kuja, bride_kuja=None,
        samadosham=mk, groom_papasamya=None, bride_papasamya=None,
        papasamya_verdict=PapasamyaVerdict.FAVORABLE,
        papasamya_diff_percent=0.0,
        papasamya_explanation_en="",
        papasamya_explanation_ta="",
    )

    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        groom_vedic=groom_vedic,
        mutual_doshas=mutual_doshas,
    )
    # Check that individual Kuja finding is preserved
    assert res.groom_vedic.kuja_dosha.is_present is True
    # Check that conflict is recorded
    conflict_types = [c.conflict_type for c in res.conflicting_findings]
    assert ConflictType.INDIVIDUAL_DOSHA_VS_MUTUAL_MITIGATION in conflict_types


def test_09_rajju_tradition_critical_veto(favorable_ashtakoota):
    """Test 9: Rajju FAIL (Rajju Thatu) triggers UNFAVOURABLE_UNDER_SELECTED_RULES with tradition disclosure."""
    rajju_fail_porutham = TamilPoruthamSummary(
        poruthams={}, total_score=7.5, max_score=10.0, aggregate_verdict="Adhama",
        rajju_status="FAIL", vedha_status="PASS",
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=rajju_fail_porutham,
        ashtakoota=favorable_ashtakoota,
    )
    assert res.overall_outcome == CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
    assert res.category_verdicts["tamil_porutham"].status == "UNFAVORABLE"
    assert len(res.category_verdicts["tamil_porutham"].vetoes_applied) > 0
    assert "Rajju Thatu" in res.category_verdicts["tamil_porutham"].vetoes_applied[0]


def test_10_vedha_tradition_critical_veto(favorable_ashtakoota):
    """Test 10: Vedha FAIL triggers UNFAVOURABLE_UNDER_SELECTED_RULES."""
    vedha_fail_porutham = TamilPoruthamSummary(
        poruthams={}, total_score=8.0, max_score=10.0, aggregate_verdict="Adhama",
        rajju_status="PASS", vedha_status="FAIL",
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=vedha_fail_porutham,
        ashtakoota=favorable_ashtakoota,
    )
    assert res.overall_outcome == CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
    assert res.category_verdicts["tamil_porutham"].status == "UNFAVORABLE"
    assert len(res.category_verdicts["tamil_porutham"].vetoes_applied) > 0


def test_11_ashtakoota_nadi_dosha_veto(favorable_porutham):
    """Test 11: Active uncancelled Nadi Dosha in Ashtakoota triggers UNFAVOURABLE_UNDER_SELECTED_RULES."""
    nadi_fail_ashtakoota = AshtakootaSummary(
        kootas={}, total_points=16.0, max_points=36.0, minimum_threshold=18.0,
        is_threshold_met=False, nadi_dosha_present=True, nadi_dosha_cancelled=False,
        bhakoot_dosha_present=False,
    )
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=nadi_fail_ashtakoota,
    )
    assert res.overall_outcome == CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
    assert len(res.category_verdicts["ashtakoota"].vetoes_applied) > 0
    assert "Nadi Dosha" in res.category_verdicts["ashtakoota"].vetoes_applied[0]


def test_12_no_double_counting_of_scores(favorable_porutham, favorable_ashtakoota):
    """Test 12: Scores are preserved in their native scales (10.0 and 36.0) and never summed."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
    )
    # Porutham score remains 8.0/10.0
    assert res.tamil_porutham.total_score == 8.0
    assert res.tamil_porutham.max_score == 10.0
    # Ashtakoota points remain 28.0/36.0
    assert res.ashtakoota.total_points == 28.0
    assert res.ashtakoota.max_points == 36.0
    # Check that score summaries reflect exact unmerged scales
    assert "8.0/10.0" in res.category_verdicts["tamil_porutham"].score_summary
    assert "28.0/36.0" in res.category_verdicts["ashtakoota"].score_summary


def test_13_no_mixing_of_incompatible_scales(favorable_porutham, favorable_ashtakoota):
    """Test 13: Category verdicts preserve distinct traditions and scoring taxonomies."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
    )
    p_cv = res.category_verdicts["tamil_porutham"]
    a_cv = res.category_verdicts["ashtakoota"]

    assert p_cv.tradition != a_cv.tradition
    assert "Tamil" in p_cv.tradition
    assert "North Indian" in a_cv.tradition


def test_14_no_invented_weights_or_thresholds(favorable_porutham):
    """Test 14: Verifies threshold boundaries (e.g. 6.0 for Porutham favorable, 5.0 for mixed)."""
    # Boundary test: exactly 5.5 Porutham score
    p_5_5 = TamilPoruthamSummary(
        poruthams={}, total_score=5.5, max_score=10.0, aggregate_verdict="Madhyama",
        rajju_status="PASS", vedha_status="PASS",
    )
    res = evaluate_composite_marriage_assessment(tamil_porutham=p_5_5)
    assert res.category_verdicts["tamil_porutham"].status == "MIXED"

    # Boundary test: exactly 6.0 Porutham score
    p_6_0 = TamilPoruthamSummary(
        poruthams={}, total_score=6.0, max_score=10.0, aggregate_verdict="Uthama",
        rajju_status="PASS", vedha_status="PASS",
    )
    res2 = evaluate_composite_marriage_assessment(tamil_porutham=p_6_0)
    assert res2.category_verdicts["tamil_porutham"].status == "FAVORABLE"


def test_15_deterministic_repeated_results(favorable_porutham, favorable_ashtakoota, favorable_mutual_doshas):
    """Test 15: Composite evaluation produces strictly identical, deterministic results across runs."""
    res1 = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        mutual_doshas=favorable_mutual_doshas,
    )
    res2 = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        mutual_doshas=favorable_mutual_doshas,
    )
    assert res1.overall_outcome == res2.overall_outcome
    assert res1.decision_path == res2.decision_path
    assert res1.explanation_en == res2.explanation_en
    assert res1.explanation_ta == res2.explanation_ta
    assert len(res1.conflicting_findings) == len(res2.conflicting_findings)


def test_16_input_immutability(sample_chart_context, favorable_porutham):
    """Test 16: Input context and schemas are never mutated by the composite evaluator."""
    cloned_context = copy.deepcopy(sample_chart_context)
    cloned_porutham = copy.deepcopy(favorable_porutham)

    evaluate_composite_marriage_assessment(
        groom_chart=sample_chart_context,
        tamil_porutham=favorable_porutham,
    )
    assert sample_chart_context.person_id == cloned_context.person_id
    assert sample_chart_context.birth_date_iso == cloned_context.birth_date_iso
    assert favorable_porutham.total_score == cloned_porutham.total_score
    assert favorable_porutham.rajju_status == cloned_porutham.rajju_status


def test_17_explainability_and_source_identifiers(favorable_porutham, favorable_ashtakoota):
    """Test 17: Rule sources and decision path are populated for audit trail."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
    )
    assert len(res.rule_sources) >= 10
    assert "TAM-POR-01" in res.rule_sources
    assert "ASHTA-01" in res.rule_sources
    assert "RULE-MATRIX-08" in res.rule_sources
    assert len(res.decision_path) > 0


def test_18_explicit_indeterminate_behavior():
    """Test 18: Incomplete inputs produce explicit INDETERMINATE status with decision path note."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=None,
        ashtakoota=None,
        mutual_doshas=None,
    )
    assert res.overall_outcome == CompatibilityOutcome.INDETERMINATE
    assert any("Insufficient" in p for p in res.decision_path)


def test_19_partial_input_evaluation(favorable_porutham):
    """Test 19: Supplying only one tradition (Tamil Porutham) evaluates that tradition while marking others INDETERMINATE."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=None,
    )
    assert res.category_verdicts["tamil_porutham"].status == "FAVORABLE"
    assert res.category_verdicts["ashtakoota"].status == "INDETERMINATE"
    assert len(res.missing_or_uncertain_evidence) > 0


def test_20_bilingual_disclaimers():
    """Test 20: Both English and Tamil disclaimers are present and non-guarantee language is verified."""
    res = evaluate_composite_marriage_assessment()
    assert len(res.disclaimers) >= 2
    assert COMPOSITE_DISCLAIMER_EN in res.disclaimers
    assert COMPOSITE_DISCLAIMER_TA in res.disclaimers
    assert "Human agency" in res.disclaimers[0]
    assert "உறுதியான உத்திரவாதம்" in res.disclaimers[1]


def test_21_backward_compatibility_with_existing_result_models(favorable_porutham, favorable_ashtakoota, favorable_mutual_doshas, favorable_synastry, favorable_kp):
    """Test 21: Result models from Phases 1–7 are consumed directly without structural errors."""
    res = evaluate_composite_marriage_assessment(
        tamil_porutham=favorable_porutham,
        ashtakoota=favorable_ashtakoota,
        mutual_doshas=favorable_mutual_doshas,
        synastry=favorable_synastry,
        kp_marriage=favorable_kp,
    )
    assert isinstance(res, CompositeMarriageAssessment)
    assert res.tamil_porutham is favorable_porutham
    assert res.ashtakoota is favorable_ashtakoota
    assert res.mutual_doshas is favorable_mutual_doshas
    assert res.synastry is favorable_synastry
    assert res.kp_marriage is favorable_kp


def test_22_non_mutation_of_underlying_calculations(favorable_mutual_doshas):
    """Test 22: Underlying calculations (e.g. Papasamya totals) are identical before and after composite assessment."""
    orig_total = favorable_mutual_doshas.groom_papasamya.total_papam

    res = evaluate_composite_marriage_assessment(mutual_doshas=favorable_mutual_doshas)

    assert res.mutual_doshas.groom_papasamya.total_papam == orig_total
    assert res.category_verdicts["papasamya"].status == "FAVORABLE"
