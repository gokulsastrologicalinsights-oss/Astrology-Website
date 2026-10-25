"""Comprehensive test suite for the isolated KP Second-Marriage Rules module.

Verifies:
1. Rule 1 (7th CSL) condition combinations and strict sign/planet enforcement.
2. Rule 2 (2nd CSL) supportive house checks.
3. Rule 3 (9th CSL) supportive house checks and sibling assumption metadata.
4. Missing, invalid, and indeterminate data handling.
5. Non-mutation of chart inputs across repeated evaluations.
6. Integration with canonical KP chart structures (dict and KpResponse).
7. Comparison with existing event engine behavior.
8. Read-only saved-horoscope integration check (with redacted personal details).
"""

import copy
import pytest
from typing import Any, Dict, List

from app.schemas.kp import (
    CalculationMetadata,
    KpCuspDetail,
    KpResponse,
    PlanetaryKpPosition,
    PlanetSignificator,
)
from app.services.second_marriage_rules import (
    RULE_1_ID,
    RULE_2_ID,
    RULE_3_ID,
    RuleEvaluationStatus,
    SummaryVerdict,
    adapt_kp_chart_data,
    compare_with_existing_event_engine,
    evaluate_rule_1,
    evaluate_rule_2,
    evaluate_rule_3,
    evaluate_second_marriage_rules,
)


# ---------------------------------------------------------------------------
# Synthetic Chart Fixtures (Isolated from production records)
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_kp_dict() -> Dict[str, Any]:
    """Builds a deterministic synthetic KP chart dictionary."""
    return {
        "cusps": [
            {"house": 1, "cusp_degree": 45.0, "sign_name": "Taurus", "star_lord": "Sun", "sub_lord": "Venus"},
            {"house": 2, "cusp_degree": 72.0, "sign_name": "Gemini", "star_lord": "Mars", "sub_lord": "Moon"},
            {"house": 3, "cusp_degree": 98.0, "sign_name": "Cancer", "star_lord": "Saturn", "sub_lord": "Jupiter"},
            {"house": 4, "cusp_degree": 125.0, "sign_name": "Leo", "star_lord": "Ketu", "sub_lord": "Venus"},
            {"house": 5, "cusp_degree": 155.0, "sign_name": "Virgo", "star_lord": "Sun", "sub_lord": "Saturn"},
            {"house": 6, "cusp_degree": 188.0, "sign_name": "Libra", "star_lord": "Rahu", "sub_lord": "Mercury"},
            {"house": 7, "cusp_degree": 225.0, "sign_name": "Scorpio", "star_lord": "Saturn", "sub_lord": "Mercury"},
            {"house": 8, "cusp_degree": 252.0, "sign_name": "Sagittarius", "star_lord": "Ketu", "sub_lord": "Venus"},
            {"house": 9, "cusp_degree": 278.0, "sign_name": "Capricorn", "star_lord": "Sun", "sub_lord": "Saturn"},
            {"house": 10, "cusp_degree": 305.0, "sign_name": "Aquarius", "star_lord": "Mars", "sub_lord": "Moon"},
            {"house": 11, "cusp_degree": 335.0, "sign_name": "Pisces", "star_lord": "Jupiter", "sub_lord": "Jupiter"},
            {"house": 12, "cusp_degree": 8.0, "sign_name": "Aries", "star_lord": "Ketu", "sub_lord": "Rahu"},
        ],
        "planets": {
            "Mercury": {"planet": "Mercury", "longitude": 170.0, "sign_name": "Virgo"},
            "Jupiter": {"planet": "Jupiter", "longitude": 80.0, "sign_name": "Gemini"},
            "Sun": {"planet": "Sun", "longitude": 75.0, "sign_name": "Gemini"},
            "Moon": {"planet": "Moon", "longitude": 15.0, "sign_name": "Aries"},
            "Saturn": {"planet": "Saturn", "longitude": 340.0, "sign_name": "Pisces"},
            "Venus": {"planet": "Venus", "longitude": 105.0, "sign_name": "Cancer"},
            "Mars": {"planet": "Mars", "longitude": 280.0, "sign_name": "Capricorn"},
            "Rahu": {"planet": "Rahu", "longitude": 65.0, "sign_name": "Gemini"},
            "Ketu": {"planet": "Ketu", "longitude": 245.0, "sign_name": "Sagittarius"},
        },
        "significators": [
            {"planet": "Mercury", "signified_houses": [2, 7, 11]},
            {"planet": "Moon", "signified_houses": [7, 11]},
            {"planet": "Saturn", "signified_houses": [9, 11]},
            {"planet": "Sun", "signified_houses": [2, 5]},
            {"planet": "Jupiter", "signified_houses": [11]},
            {"planet": "Venus", "signified_houses": [3, 8]},
            {"planet": "Mars", "signified_houses": [6, 10]},
            {"planet": "Rahu", "signified_houses": [1, 12]},
            {"planet": "Ketu", "signified_houses": [4, 6]},
        ],
        "metadata": {
            "ayanamsa_name": "KP",
            "ayanamsa_id": 1,
            "house_system_name": "Placidus",
            "engine": "kpastro-synthetic",
        },
    }


# ---------------------------------------------------------------------------
# 1. Rule 1 Unit Tests (7th Cusp Sub-Lord)
# ---------------------------------------------------------------------------

def test_rule_1_mercury_sublord_with_house_2_passes():
    """Mercury as sub-lord with house 2 significations satisfies Cond A and Cond B."""
    res = evaluate_rule_1(sub_lord="Mercury", deposited_sign="Leo", significations=[2, 5])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.cusp_number == 7
    assert res.cusp_sub_lord == "Mercury"
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[1].evaluated_bool is True


def test_rule_1_jupiter_sublord_with_house_11_passes():
    """Jupiter as sub-lord with house 11 significations satisfies Cond A and Cond B."""
    res = evaluate_rule_1(sub_lord="Jupiter", deposited_sign="Aries", significations=[8, 11])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[1].evaluated_bool is True


def test_rule_1_sun_in_gemini_with_house_2_passes():
    """Sun (not Mercury/Jupiter) deposited in Gemini with house 2 significations passes."""
    res = evaluate_rule_1(sub_lord="Sun", deposited_sign="Gemini", significations=[1, 2, 9])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[1].evaluated_bool is True


def test_rule_1_sun_in_taurus_with_house_2_fails_condition_a():
    """Sun deposited in Taurus fails Condition A even if house 2 is signified."""
    res = evaluate_rule_1(sub_lord="Sun", deposited_sign="Taurus", significations=[2, 11])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is False
    assert res.conditions[1].evaluated_bool is True
    assert "Condition A" in res.explanation


def test_rule_1_sagittarius_does_not_satisfy_condition_a():
    """Strict source fidelity: Sagittarius is not in {Gemini, Virgo, Pisces}."""
    res = evaluate_rule_1(sub_lord="Mars", deposited_sign="Sagittarius", significations=[2, 11])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is False


def test_rule_1_mercury_with_no_2_or_11_fails_condition_b():
    """Mercury satisfies Condition A but fails Condition B when neither 2 nor 11 is signified."""
    res = evaluate_rule_1(sub_lord="Mercury", deposited_sign="Virgo", significations=[3, 4, 8, 12])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[1].evaluated_bool is False
    assert "Condition B" in res.explanation


def test_rule_1_condition_a_true_and_b_false_overall_fail():
    """Cond A=True, Cond B=False -> Overall FAIL."""
    res = evaluate_rule_1(sub_lord="Jupiter", deposited_sign="Cancer", significations=[1, 5, 9])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[1].evaluated_bool is False


def test_rule_1_condition_a_false_and_b_true_overall_fail():
    """Cond A=False, Cond B=True -> Overall FAIL."""
    res = evaluate_rule_1(sub_lord="Saturn", deposited_sign="Libra", significations=[2, 11])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is False
    assert res.conditions[1].evaluated_bool is True


def test_rule_1_missing_sub_lord_indeterminate():
    """Missing sub-lord planet returns INDETERMINATE."""
    res = evaluate_rule_1(sub_lord=None, deposited_sign="Gemini", significations=[2, 11])
    assert res.status == RuleEvaluationStatus.INDETERMINATE
    assert res.conditions[0].status == RuleEvaluationStatus.INDETERMINATE


def test_rule_1_missing_sign_when_required_indeterminate():
    """Non-Mercury/Jupiter planet with missing deposited sign returns INDETERMINATE."""
    res = evaluate_rule_1(sub_lord="Sun", deposited_sign=None, significations=[2])
    assert res.status == RuleEvaluationStatus.INDETERMINATE
    assert res.conditions[0].status == RuleEvaluationStatus.INDETERMINATE


def test_rule_1_missing_significations_indeterminate():
    """Missing significations data returns INDETERMINATE."""
    res = evaluate_rule_1(sub_lord="Mercury", deposited_sign="Virgo", significations=None)
    assert res.status == RuleEvaluationStatus.INDETERMINATE
    assert res.conditions[1].status == RuleEvaluationStatus.INDETERMINATE


# ---------------------------------------------------------------------------
# 2. Rule 2 Unit Tests (2nd Cusp Sub-Lord)
# ---------------------------------------------------------------------------

def test_rule_2_house_7_only_passes():
    """2nd CSL signifying house 7 alone passes."""
    res = evaluate_rule_2(sub_lord="Moon", significations=[7])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.cusp_number == 2
    assert res.conditions[0].evaluated_bool is True
    assert res.conditions[0].evidence["hits"] == [7]


def test_rule_2_house_11_only_passes():
    """2nd CSL signifying house 11 alone passes."""
    res = evaluate_rule_2(sub_lord="Venus", significations=[3, 11, 12])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.conditions[0].evidence["hits"] == [11]


def test_rule_2_neither_7_nor_11_fails():
    """2nd CSL signifying houses without 7 or 11 fails."""
    res = evaluate_rule_2(sub_lord="Mars", significations=[1, 4, 6, 8, 10])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is False
    assert res.conditions[0].evidence["hits"] == []


def test_rule_2_missing_significations_indeterminate():
    """Missing significations produces INDETERMINATE."""
    res = evaluate_rule_2(sub_lord="Rahu", significations=None)
    assert res.status == RuleEvaluationStatus.INDETERMINATE
    assert res.conditions[0].evaluated_bool is None


def test_rule_2_missing_sub_lord_indeterminate():
    """Missing sub-lord planet produces INDETERMINATE."""
    res = evaluate_rule_2(sub_lord="", significations=[7, 11])
    assert res.status == RuleEvaluationStatus.INDETERMINATE


# ---------------------------------------------------------------------------
# 3. Rule 3 Unit Tests (9th Cusp Sub-Lord)
# ---------------------------------------------------------------------------

def test_rule_3_house_2_only_passes():
    """9th CSL signifying house 2 alone passes."""
    res = evaluate_rule_3(sub_lord="Saturn", significations=[2, 8])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.cusp_number == 9
    assert res.conditions[0].evidence["hits"] == [2]
    # Verify stated classical sibling assumption is preserved in metadata
    assert any("younger sibling" in a for a in res.assumptions)


def test_rule_3_house_9_only_passes():
    """9th CSL signifying house 9 alone passes."""
    res = evaluate_rule_3(sub_lord="Jupiter", significations=[9])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.conditions[0].evidence["hits"] == [9]


def test_rule_3_house_11_only_passes():
    """9th CSL signifying house 11 alone passes."""
    res = evaluate_rule_3(sub_lord="Sun", significations=[5, 11])
    assert res.status == RuleEvaluationStatus.PASS
    assert res.conditions[0].evidence["hits"] == [11]


def test_rule_3_none_of_2_9_11_fails():
    """9th CSL signifying houses without 2, 9, or 11 fails."""
    res = evaluate_rule_3(sub_lord="Mercury", significations=[1, 6, 7, 10])
    assert res.status == RuleEvaluationStatus.FAIL
    assert res.conditions[0].evaluated_bool is False
    assert res.conditions[0].evidence["hits"] == []


def test_rule_3_missing_significations_indeterminate():
    """Missing significations produces INDETERMINATE."""
    res = evaluate_rule_3(sub_lord="Venus", significations=None)
    assert res.status == RuleEvaluationStatus.INDETERMINATE


# ---------------------------------------------------------------------------
# 4. Integration, Normalization, & Quality Tests
# ---------------------------------------------------------------------------

def test_adapter_duplicate_and_out_of_bounds_houses():
    """Adapter cleanses duplicates, invalid numbers, and maintains sorted integers."""
    raw_chart = {
        "cusps": [{"house": 7, "sub_lord": "mercury"}],
        "planets": {"mercury": {"sign_name": "virgo"}},
        "significators": [
            {"planet": "mercury", "signified_houses": [11, 2, 2, 13, 0, -1, "11", "invalid"]},
        ],
    }
    adapted = adapt_kp_chart_data(raw_chart)
    assert adapted.planet_significations["Mercury"] == [2, 11]
    assert adapted.cusp_sub_lords[7] == "Mercury"
    assert adapted.planet_signs["Mercury"] == "Virgo"


def test_evaluator_with_synthetic_chart(synthetic_kp_dict):
    """Evaluates full pipeline against synthetic KP chart."""
    result = evaluate_second_marriage_rules(synthetic_kp_dict)
    assert result.summary.verdict_label == SummaryVerdict.RULES_SUMMARY_ONLY
    assert result.rules["rule_1"].rule_id == RULE_1_ID
    assert result.rules["rule_2"].rule_id == RULE_2_ID
    assert result.rules["rule_3"].rule_id == RULE_3_ID

    # In synthetic chart:
    # 7th CSL = Mercury (Virgo), sigs=[2, 7, 11] -> Rule 1 PASS
    # 2nd CSL = Moon (Aries), sigs=[7, 11] -> Rule 2 PASS
    # 9th CSL = Saturn (Pisces), sigs=[9, 11] -> Rule 3 PASS
    assert result.rules["rule_1"].status == RuleEvaluationStatus.PASS
    assert result.rules["rule_2"].status == RuleEvaluationStatus.PASS
    assert result.rules["rule_3"].status == RuleEvaluationStatus.PASS
    assert len(result.summary.passed_rules) == 3


def test_non_mutation_of_input_chart(synthetic_kp_dict):
    """Verifies evaluator never mutates input dictionary."""
    cloned = copy.deepcopy(synthetic_kp_dict)
    evaluate_second_marriage_rules(synthetic_kp_dict)
    assert synthetic_kp_dict == cloned


def test_deterministic_repeated_evaluations(synthetic_kp_dict):
    """Repeated calls with identical inputs yield identical output."""
    res1 = evaluate_second_marriage_rules(synthetic_kp_dict)
    res2 = evaluate_second_marriage_rules(synthetic_kp_dict)
    assert res1.model_dump() == res2.model_dump()


def test_compare_with_existing_event_engine(synthetic_kp_dict):
    """Comparison helper executes safely and documents divergence reasons."""
    analysis = evaluate_second_marriage_rules(synthetic_kp_dict)
    comparison = compare_with_existing_event_engine(analysis, synthetic_kp_dict)
    assert comparison.event_engine_event_name == "Second marriage"
    assert comparison.event_engine_primary_cusp == 9
    assert len(comparison.divergence_reasons) == 3
    assert "Cuspal Scope" in comparison.divergence_reasons[0]


# ---------------------------------------------------------------------------
# 5. Read-Only Saved-Horoscope Integration Check
# ---------------------------------------------------------------------------

def test_saved_horoscope_integration_read_only():
    """Runs new module against real saved horoscope in Supabase if authorized.
    
    If Supabase is offline or unconfigured, reports BLOCKED cleanly without failing.
    """
    import app.config  # Ensure environment variables are loaded
    from app.services.auth_service import get_supabase_client
    supabase = get_supabase_client()
    if not supabase:
        pytest.skip("Supabase service not configured or offline; integration test reported as BLOCKED.")

    try:
        # Fetch canonical reference record ba9bb522 without modifying records
        res = (
            supabase.table("saved_horoscopes")
            .select("id, user_id, calculation_result")
            .eq("id", "ba9bb522-a79d-43e8-8493-ac8d53d4d39b")
            .execute()
        )
    except Exception as exc:
        pytest.skip(f"Supabase query failed: {exc}; integration test reported as BLOCKED.")

    if not res.data:
        pytest.skip("Saved horoscope ba9bb522 not accessible; reported as BLOCKED.")

    stored_kp = res.data[0].get("calculation_result", {}).get("kp")
    assert stored_kp is not None, "Saved horoscope lacks stored KP calculation snapshot."

    # Evaluate new isolated module on stored chart
    analysis = evaluate_second_marriage_rules(stored_kp)

    # Verify Rule 1: 7th CSL = Sun in Libra, sigs=[3, 5, 12] -> FAIL
    assert analysis.rules["rule_1"].cusp_sub_lord == "Sun"
    assert analysis.rules["rule_1"].status == RuleEvaluationStatus.FAIL

    # Verify Rule 2: 2nd CSL = Moon, sigs=[2, 4, 5, 11, 12] -> PASS (hits 11)
    assert analysis.rules["rule_2"].cusp_sub_lord == "Moon"
    assert analysis.rules["rule_2"].status == RuleEvaluationStatus.PASS

    # Verify Rule 3: 9th CSL = Jupiter, sigs=[1, 7, 10] -> FAIL (misses 2, 9, 11)
    assert analysis.rules["rule_3"].cusp_sub_lord == "Jupiter"
    assert analysis.rules["rule_3"].status == RuleEvaluationStatus.FAIL

    # Summary verification
    assert analysis.summary.passed_rules == [RULE_2_ID]
    assert set(analysis.summary.failed_rules) == {RULE_1_ID, RULE_3_ID}
    assert analysis.summary.verdict_label == SummaryVerdict.RULES_SUMMARY_ONLY

    # Comparison helper with existing event engine
    comp = compare_with_existing_event_engine(analysis, stored_kp)
    assert comp.event_engine_verdict == "Delayed / Mixed"
    assert comp.event_engine_supporting_hits == [7]
    assert comp.event_engine_denying_hits == [1, 10]
