"""Isolated KP Second-Marriage Rules Module.

Implements the three classical KP second-marriage rules:
- Rule 1 (7th Cusp Sub-Lord): (Mercury/Jupiter OR Gem/Vir/Pis) AND signifies {2, 11}.
- Rule 2 (2nd Cusp Sub-Lord): Signifies {7, 11}.
- Rule 3 (9th Cusp Sub-Lord): Signifies {2, 9, 11} (Context: 2nd spouse as 1st spouse's younger sibling).

Deterministic, side-effect-free, and non-mutating.
"""

from app.services.second_marriage_rules.models import (
    EventEngineComparisonResult,
    RuleConditionResult,
    RuleEvaluationStatus,
    SecondMarriageAnalysisResult,
    SecondMarriageRuleResult,
    SecondMarriageSummary,
    SummaryVerdict,
)
from app.services.second_marriage_rules.rules import (
    RULE_1_ALLOWED_PLANETS,
    RULE_1_ALLOWED_SIGNS,
    RULE_1_ASSUMPTIONS,
    RULE_1_ID,
    RULE_1_NAME,
    RULE_1_SOURCE_ID,
    RULE_1_SOURCE_TEXT,
    RULE_1_SUPPORTIVE_HOUSES,
    RULE_2_ASSUMPTIONS,
    RULE_2_ID,
    RULE_2_NAME,
    RULE_2_SOURCE_ID,
    RULE_2_SOURCE_TEXT,
    RULE_2_SUPPORTIVE_HOUSES,
    RULE_3_ASSUMPTIONS,
    RULE_3_ID,
    RULE_3_NAME,
    RULE_3_SOURCE_ID,
    RULE_3_SOURCE_TEXT,
    RULE_3_SUPPORTIVE_HOUSES,
    evaluate_rule_1,
    evaluate_rule_2,
    evaluate_rule_3,
    normalize_house_numbers,
    normalize_planet_name,
    normalize_sign_name,
)
from app.services.second_marriage_rules.evaluator import (
    AdaptedKpChartData,
    adapt_kp_chart_data,
    compare_with_existing_event_engine,
    evaluate_second_marriage_rules,
)

__all__ = [
    "RuleEvaluationStatus",
    "SummaryVerdict",
    "RuleConditionResult",
    "SecondMarriageRuleResult",
    "SecondMarriageSummary",
    "SecondMarriageAnalysisResult",
    "EventEngineComparisonResult",
    "RULE_1_ID",
    "RULE_1_NAME",
    "RULE_1_SOURCE_ID",
    "RULE_1_SOURCE_TEXT",
    "RULE_1_ASSUMPTIONS",
    "RULE_1_ALLOWED_PLANETS",
    "RULE_1_ALLOWED_SIGNS",
    "RULE_1_SUPPORTIVE_HOUSES",
    "RULE_2_ID",
    "RULE_2_NAME",
    "RULE_2_SOURCE_ID",
    "RULE_2_SOURCE_TEXT",
    "RULE_2_ASSUMPTIONS",
    "RULE_2_SUPPORTIVE_HOUSES",
    "RULE_3_ID",
    "RULE_3_NAME",
    "RULE_3_SOURCE_ID",
    "RULE_3_SOURCE_TEXT",
    "RULE_3_ASSUMPTIONS",
    "RULE_3_SUPPORTIVE_HOUSES",
    "evaluate_rule_1",
    "evaluate_rule_2",
    "evaluate_rule_3",
    "normalize_planet_name",
    "normalize_sign_name",
    "normalize_house_numbers",
    "AdaptedKpChartData",
    "adapt_kp_chart_data",
    "evaluate_second_marriage_rules",
    "compare_with_existing_event_engine",
]
