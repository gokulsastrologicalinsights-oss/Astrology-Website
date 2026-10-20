"""Test suite for Phase 7 Read-Only KP Marriage & Timing Adapter.

Verifies:
1. Supporting-house evidence (2, 7, 11) -> FAVORABLE.
2. Denying-house evidence (1, 6, 10) -> UNFAVORABLE.
3. Mixed evidence (both supporting and denying) -> MIXED.
4. Missing 7th CSL -> INDETERMINATE with warnings and is_valid=False.
5. Missing significators -> graceful handling.
6. Neutral / unsupported significations -> INDETERMINATE.
7. 4-tier KP house significators extraction (A, B, C, D).
8. Ruling Planets (RP) extraction and agreement calculation (STRONG, MODERATE, LOW, NONE).
9. Vimshottari Dasa-Bhukti timing evaluation (FAVORABLE, MIXED, UNFAVORABLE).
10. Missing birth data handling in MarriageChartContext.
11. Deterministic repeated results.
12. Non-mutation of input context.
13. Complete couple evaluation with bilingual explanations (EN/TA) and non-guarantee disclaimers.
"""

import copy
import pytest
from app.schemas.common import BirthInput
from app.schemas.kp import (
    KpResponse,
    KpCuspDetail,
    PlanetSignificator,
    HouseSignificatorEntry,
    RulingPlanetsDetail,
    KpDasaPeriod,
    KpDasaBalance,
)
from app.services.marriage_engine.models import (
    Gender,
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    KpPromiseVerdict,
    KpCslFinding,
    KpSignificatorsFinding,
    KpRulingPlanetsFinding,
    KpTimingFinding,
    KpIndividualAnalysis,
    KpMarriageAnalysisResult,
)
from app.services.marriage_engine.kp_adapter import (
    evaluate_kp_csl_promise,
    extract_kp_significators,
    evaluate_kp_ruling_planets,
    evaluate_kp_timing,
    evaluate_individual_kp_analysis,
    evaluate_kp_marriage_analysis,
    KP_SUPPORTING_HOUSES,
    KP_DENYING_HOUSES,
    DISCLAIMER_EN,
    DISCLAIMER_TA,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_planet_significators():
    """Standardized dictionary of planetary house significations."""
    return {
        "Jupiter": [2, 7, 11],       # Pure supporting
        "Saturn": [1, 6, 10],        # Pure denying
        "Venus": [2, 6, 7, 10],      # Mixed supporting & denying
        "Mercury": [3, 4, 5, 8, 9],  # Neutral
        "Mars": [7],                 # Single supporting
        "Moon": [6],                 # Single denying
        "Sun": [2, 11],              # Supporting
        "Rahu": [1, 10],             # Denying
        "Ketu": [12],                # Neutral / Moksha
    }


@pytest.fixture
def sample_chart_context():
    """Mock MarriageChartContext for testing non-mutation and adapters."""
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
# Unit Tests
# ---------------------------------------------------------------------------

def test_csl_supporting_houses_favorable(mock_planet_significators):
    """Test 1: 7th CSL signifying houses {2, 7, 11} returns FAVORABLE."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="Jupiter",
        planet_significators=mock_planet_significators,
        person_id="P_TEST_01",
    )
    assert finding.is_valid is True
    assert finding.verdict == KpPromiseVerdict.FAVORABLE
    assert set(finding.supporting_houses_signified) == {2, 7, 11}
    assert len(finding.denying_houses_signified) == 0
    assert "KP-MARR-01" in finding.rule_sources
    assert "Auspicious marital promise" in finding.explanation_en
    assert "நன்மையான திருமண வாக்குறுதி" in finding.explanation_ta


def test_csl_denying_houses_unfavorable(mock_planet_significators):
    """Test 2: 7th CSL signifying houses {1, 6, 10} returns UNFAVORABLE."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="Saturn",
        planet_significators=mock_planet_significators,
        person_id="P_TEST_02",
    )
    assert finding.is_valid is True
    assert finding.verdict == KpPromiseVerdict.UNFAVORABLE
    assert set(finding.denying_houses_signified) == {1, 6, 10}
    assert len(finding.supporting_houses_signified) == 0
    assert "separating/denying houses" in finding.explanation_en
    assert "பிரிவினை அல்லது சவாலான" in finding.explanation_ta


def test_csl_mixed_houses_verdict(mock_planet_significators):
    """Test 3: 7th CSL signifying both supporting {2, 7} and denying {6, 10} returns MIXED."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="Venus",
        planet_significators=mock_planet_significators,
        person_id="P_TEST_03",
    )
    assert finding.is_valid is True
    assert finding.verdict == KpPromiseVerdict.MIXED
    assert set(finding.supporting_houses_signified) == {2, 7}
    assert set(finding.denying_houses_signified) == {6, 10}
    assert "dual significations" in finding.explanation_en
    assert "கலவையான திருமண வாக்குறுதி" in finding.explanation_ta


def test_csl_missing_planet_indeterminate():
    """Test 4: Missing or empty 7th CSL planet returns INDETERMINATE with is_valid=False."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="",
        planet_significators={"Jupiter": [2, 7, 11]},
        person_id="P_TEST_04",
    )
    assert finding.is_valid is False
    assert finding.verdict == KpPromiseVerdict.INDETERMINATE
    assert len(finding.warnings) > 0
    assert "missing or invalid" in finding.explanation_en


def test_csl_missing_significators_indeterminate():
    """Test 5: CSL planet with no mapped significations returns INDETERMINATE with warning."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="Uranus",  # Not in traditional 9 grahas map
        planet_significators={"Jupiter": [2, 7, 11]},
        person_id="P_TEST_05",
    )
    assert finding.verdict == KpPromiseVerdict.INDETERMINATE
    assert len(finding.warnings) > 0
    assert len(finding.signified_houses) == 0


def test_csl_neutral_houses_indeterminate(mock_planet_significators):
    """Test 6: CSL planet signifying only neutral houses {3, 4, 5, 8, 9} returns INDETERMINATE."""
    finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet="Mercury",
        planet_significators=mock_planet_significators,
        person_id="P_TEST_06",
    )
    assert finding.verdict == KpPromiseVerdict.INDETERMINATE
    assert len(finding.supporting_houses_signified) == 0
    assert len(finding.denying_houses_signified) == 0
    assert "neutral houses" in finding.explanation_en


def test_extract_4_tier_significators():
    """Test 7: Extract 4-tier KP house significators (Levels A, B, C, D) without fabricating data."""
    mock_house_sigs = [
        HouseSignificatorEntry(
            house=7,
            sign_name="Scorpio",
            sign_lord="Mars",
            star_lord="Saturn",
            sub_lord="Jupiter",
            sub_sub_lord="Venus",
            level_a=["Moon", "Saturn"],
            level_b=["Jupiter"],
            level_c=[],
            level_d=["Mars"],
            all_significators=["Moon", "Saturn", "Jupiter", "Mars"],
        ),
        HouseSignificatorEntry(
            house=2,
            sign_name="Taurus",
            sign_lord="Venus",
            star_lord="Sun",
            sub_lord="Moon",
            sub_sub_lord="Jupiter",
            level_a=["Sun"],
            level_b=[],
            level_c=["Mercury"],
            level_d=["Venus"],
            all_significators=["Sun", "Mercury", "Venus"],
        ),
    ]

    finding = extract_kp_significators(
        target_house=7,
        house_significators=mock_house_sigs,
        planet_significators=[],
        person_id="P_TEST_07",
    )
    assert "KP-MARR-02" in finding.rule_sources
    assert 7 in finding.significators_by_house
    assert finding.significators_by_house[7].level_a == ["Moon", "Saturn"]
    assert finding.significators_by_house[7].level_b == ["Jupiter"]
    assert finding.significators_by_house[7].level_c == []
    assert finding.significators_by_house[7].level_d == ["Mars"]
    assert set(finding.all_marriage_significators).issuperset({"Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"})


def test_ruling_planets_agreement():
    """Test 8: Ruling Planets (RP) extraction and agreement calculation."""
    groom_rp = RulingPlanetsDetail(
        day_lord="Moon",
        ascendant_sign_lord="Venus",
        ascendant_star_lord="Mars",
        ascendant_sub_lord="Jupiter",
        moon_sign_lord="Mars",
        moon_star_lord="Saturn",
        moon_sub_lord="Mercury",
        ruling_planets_list=["Moon", "Venus", "Mars", "Jupiter", "Saturn"],
        details=[],
    )

    bride_rp = RulingPlanetsDetail(
        day_lord="Sun",
        ascendant_sign_lord="Jupiter",
        ascendant_star_lord="Mars",
        ascendant_sub_lord="Venus",
        moon_sign_lord="Mercury",
        moon_star_lord="Venus",
        moon_sub_lord="Saturn",
        ruling_planets_list=["Sun", "Jupiter", "Mars", "Venus", "Mercury"],
        details=[],
    )

    finding = evaluate_kp_ruling_planets(
        ruling_planets_detail=groom_rp,
        partner_ruling_planets_detail=bride_rp,
        person_id="P_GROOM",
    )
    assert "KP-MARR-03" in finding.rule_sources
    assert set(finding.shared_with_partner) == {"Venus", "Mars", "Jupiter"}
    assert finding.agreement_score > 0.0
    assert "Shared with partner" in finding.explanation_en
    assert "பொதுவான கிரகங்கள்" in finding.explanation_ta


def test_timing_evaluation_favorable_and_unfavorable():
    """Test 9: Vimshottari Dasa-Bhukti timing favorability."""
    sig_map = {
        "Jupiter": [2, 7, 11],
        "Venus": [2, 11],
        "Saturn": [1, 6, 10],
    }

    # Case A: Favorable active Dasa & Bhukti
    fav_periods = [
        KpDasaPeriod(level=1, level_name="Mahadasha", vedic_name="Dasa", lord="Jupiter", start_date="", end_date="", duration_days=5000),
        KpDasaPeriod(level=2, level_name="Antardasha", vedic_name="Bhukti", lord="Venus", start_date="", end_date="", duration_days=800),
    ]
    fav_timing = evaluate_kp_timing(fav_periods, sig_map, person_id="P_TIMING_01")
    assert fav_timing.overall_timing_verdict == KpPromiseVerdict.FAVORABLE
    assert fav_timing.current_mahadasha.timing_favorability == "FAVORABLE"
    assert fav_timing.current_bhukti.timing_favorability == "FAVORABLE"

    # Case B: Unfavorable active Bhukti
    unfav_periods = [
        KpDasaPeriod(level=1, level_name="Mahadasha", vedic_name="Dasa", lord="Saturn", start_date="", end_date="", duration_days=6000),
        KpDasaPeriod(level=2, level_name="Antardasha", vedic_name="Bhukti", lord="Saturn", start_date="", end_date="", duration_days=1000),
    ]
    unfav_timing = evaluate_kp_timing(unfav_periods, sig_map, person_id="P_TIMING_02")
    assert unfav_timing.overall_timing_verdict == KpPromiseVerdict.UNFAVORABLE


def test_missing_birth_data_handling():
    """Test 10: Missing birth datetime in chart context handled gracefully without crash."""
    invalid_context = MarriageChartContext(
        person_id="P_NO_DATA",
        person_name="Anand",
        gender=Gender.MALE,
        birth_date_iso=None,  # Missing
        birth_time_iso=None,  # Missing
        timezone="Asia/Kolkata",
        latitude=None,        # Missing
        longitude=None,
        ascendant_degree=0.0,
        ascendant_sign_idx=1,
        ascendant_sign_name="Aries",
        ascendant_sign_name_tamil="மேஷம்",
        ascendant_nakshatra_idx=0,
        ascendant_nakshatra_name="Ashwini",
        ascendant_nakshatra_pada=1,
        ascendant_navamsa_sign_idx=1,
        moon_degree=0.0,
        moon_sign_idx=1,
        moon_sign_name="Aries",
        moon_sign_name_tamil="மேஷம்",
        moon_nakshatra_idx=0,
        moon_nakshatra_name="Ashwini",
        moon_nakshatra_pada=1,
        moon_navamsa_sign_idx=1,
    )

    analysis = evaluate_individual_kp_analysis(invalid_context)
    assert analysis.overall_promise_verdict == KpPromiseVerdict.INDETERMINATE
    assert analysis.csl_7th.is_valid is False
    assert len(analysis.warnings) > 0


def test_deterministic_repeated_results(mock_planet_significators):
    """Test 11: Adapter produces strictly identical, deterministic results across consecutive runs."""
    res1 = evaluate_kp_csl_promise(7, "Jupiter", mock_planet_significators, person_id="P_DET")
    res2 = evaluate_kp_csl_promise(7, "Jupiter", mock_planet_significators, person_id="P_DET")

    assert res1.verdict == res2.verdict
    assert res1.supporting_houses_signified == res2.supporting_houses_signified
    assert res1.denying_houses_signified == res2.denying_houses_signified
    assert res1.explanation_en == res2.explanation_en
    assert res1.explanation_ta == res2.explanation_ta


def test_non_mutation_of_input_context(sample_chart_context):
    """Test 12: Input MarriageChartContext is never mutated by the KP adapter."""
    cloned_context = copy.deepcopy(sample_chart_context)

    # Execute individual analysis
    evaluate_individual_kp_analysis(sample_chart_context)

    assert sample_chart_context.person_id == cloned_context.person_id
    assert sample_chart_context.birth_date_iso == cloned_context.birth_date_iso
    assert sample_chart_context.birth_time_iso == cloned_context.birth_time_iso
    assert sample_chart_context.ascendant_degree == cloned_context.ascendant_degree
    assert sample_chart_context.moon_degree == cloned_context.moon_degree
    assert len(sample_chart_context.grahas) == len(cloned_context.grahas)


def test_complete_couple_analysis_with_disclaimers():
    """Test 13: Full evaluate_kp_marriage_analysis returns structured result with disclaimers."""
    # Build two mock BirthInput instances
    groom_birth = BirthInput(
        birth_date="1995-05-15",
        birth_time="06:30",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
    )
    bride_birth = BirthInput(
        birth_date="1997-08-20",
        birth_time="10:15",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
    )

    couple_res = evaluate_kp_marriage_analysis(groom_birth, bride_birth)

    assert isinstance(couple_res, KpMarriageAnalysisResult)
    assert couple_res.groom_analysis.csl_7th.is_valid is True
    assert couple_res.bride_analysis.csl_7th.is_valid is True
    assert couple_res.ruling_planets_agreement_level in ("STRONG", "MODERATE", "LOW", "NONE")
    assert len(couple_res.disclaimers) >= 2
    assert DISCLAIMER_EN in couple_res.disclaimers
    assert DISCLAIMER_TA in couple_res.disclaimers
    assert len(couple_res.rule_sources) == 3
    assert set(couple_res.rule_sources) == {"KP-MARR-01", "KP-MARR-02", "KP-MARR-03"}
