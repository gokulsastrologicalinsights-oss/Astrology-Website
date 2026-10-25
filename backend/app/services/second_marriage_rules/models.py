"""Data models and schemas for the isolated KP Second-Marriage Rules module.

Defines deterministic, typed structures for rule definitions, condition evaluations,
per-rule outcomes, summary aggregation, and event engine comparison.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RuleEvaluationStatus(str, Enum):
    """Evaluation status for an astrological rule or condition."""
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"


class SummaryVerdict(str, Enum):
    """Discriminator label for rule-level summary aggregation."""
    RULES_SUMMARY_ONLY = "RULES_SUMMARY_ONLY"


class RuleConditionResult(BaseModel):
    """Result of evaluating a single sub-condition within a rule."""
    condition_id: str = Field(..., description="Unique condition code (e.g., R1_COND_A, R1_COND_B)")
    condition_name: str = Field(..., description="Short human-readable name of the condition")
    status: RuleEvaluationStatus = Field(..., description="PASS, FAIL, or INDETERMINATE")
    evaluated_bool: Optional[bool] = Field(
        None,
        description="Boolean outcome (True/False) if evaluable; None if INDETERMINATE",
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured computation evidence supporting the outcome",
    )
    explanation: str = Field(..., description="Human-readable explanation of this condition result")


class SecondMarriageRuleResult(BaseModel):
    """Comprehensive result for an individual KP second-marriage rule."""
    rule_id: str = Field(..., description="Standard rule code (e.g., KP-SM-RULE-1)")
    rule_name: str = Field(..., description="Formal rule title")
    source_identifier: str = Field(..., description="Bibliographic or extracted citation identifier")
    source_text: str = Field(..., description="Verbatim extracted rule text from classical source")
    rule_version: str = Field("1.0.0", description="Semantic rule logic version")
    assumptions: List[str] = Field(
        default_factory=list,
        description="Stated classical/interpretive assumptions underlying this rule",
    )
    status: RuleEvaluationStatus = Field(..., description="Overall rule verdict: PASS, FAIL, or INDETERMINATE")
    cusp_number: int = Field(..., description="Governing cusp evaluated (2, 7, or 9)")
    cusp_sub_lord: Optional[str] = Field(None, description="Sub-lord planet of the cusp")
    deposited_sign: Optional[str] = Field(None, description="Zodiac sign where the sub-lord is deposited")
    significations_used: List[int] = Field(
        default_factory=list,
        description="Houses signified by the sub-lord across ABCD significator tiers",
    )
    conditions: List[RuleConditionResult] = Field(
        default_factory=list,
        description="Individual condition breakdowns",
    )
    explanation: str = Field(..., description="Full explanatory narrative for the rule verdict")


class SecondMarriageSummary(BaseModel):
    """Summary of rule outcomes strictly labeled as RULES_SUMMARY_ONLY."""
    verdict_label: SummaryVerdict = Field(
        default=SummaryVerdict.RULES_SUMMARY_ONLY,
        description="Strictly labeled to prevent treating rule tallies as definitive life event predictions",
    )
    passed_rules: List[str] = Field(default_factory=list, description="IDs of rules that passed")
    failed_rules: List[str] = Field(default_factory=list, description="IDs of rules that failed")
    indeterminate_rules: List[str] = Field(default_factory=list, description="IDs of rules that were indeterminate")
    summary_text: str = Field(..., description="Factual recap of which rules passed and failed")
    epistemological_disclaimer: str = Field(
        default=(
            "Passing or failing an astrological software rule verifies compliance with the encoded "
            "source text conditions; it does not constitute empirical or scientific evidence of a "
            "native's future marital history or relationship destiny."
        ),
        description="Mandatory disclaimer distinguishing software verification from empirical prophecy",
    )


class SecondMarriageAnalysisResult(BaseModel):
    """Complete container for the 3 isolated KP second-marriage rules."""
    rules: Dict[str, SecondMarriageRuleResult] = Field(
        ...,
        description="Results keyed by rule identifier (rule_1, rule_2, rule_3)",
    )
    summary: SecondMarriageSummary = Field(..., description="Non-predictive rules summary")
    chart_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Redacted chart information and calculation engine provenance",
    )


class EventEngineComparisonResult(BaseModel):
    """Comparison between the new isolated 3-rule module and the existing event engine."""
    isolated_rules_verdicts: Dict[str, RuleEvaluationStatus] = Field(
        ...,
        description="Verdicts for Rule 1 (7th CSL), Rule 2 (2nd CSL), and Rule 3 (9th CSL)",
    )
    event_engine_event_name: str = Field("Second marriage", description="Event name in existing event engine")
    event_engine_primary_cusp: int = Field(9, description="Cusp evaluated by existing event engine")
    event_engine_verdict: Optional[str] = Field(
        None,
        description="Status from existing event engine (e.g. Promised, Delayed / Mixed, Denied / Weak)",
    )
    event_engine_supporting_hits: List[int] = Field(
        default_factory=list,
        description="Houses satisfying event engine supporting set [2, 7, 9, 11]",
    )
    event_engine_denying_hits: List[int] = Field(
        default_factory=list,
        description="Houses triggering event engine denying set [1, 6, 8, 10]",
    )
    divergence_reasons: List[str] = Field(
        default_factory=list,
        description="Documented architectural reasons why verdicts can diverge",
    )
    comparison_summary: str = Field(..., description="Summary explanation of the comparison")
