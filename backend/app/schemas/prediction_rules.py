"""Pydantic schemas for Prediction Rules API."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.schemas.horoscope import HoroscopeResponse


class SubcategorySchema(BaseModel):
    slug: str
    name_en: str
    name_ta: str
    description_en: str
    description_ta: str


class CategoryGroupSchema(BaseModel):
    group_code: str
    group_name_en: str
    group_name_ta: str
    display_order: int
    subcategories: List[SubcategorySchema]


class EvaluatedRuleItem(BaseModel):
    rule_id: str
    version: int
    name: str
    name_en: str
    name_ta: Optional[str] = None
    category_slug: str
    subcategory: Optional[str] = None
    astrology_system: str
    chart_scope: str
    calculation_mode: str = "thirukanitha"
    severity: str
    status: str  # "matched", "not_matched", "unevaluable"
    matched: bool
    unevaluable: bool = False
    unevaluable_reason: Optional[str] = None
    interpretation: Optional[str] = ""
    interpretation_en: Optional[str] = ""
    interpretation_ta: Optional[str] = None
    astrological_principle: Optional[str] = ""
    astrological_principle_en: Optional[str] = ""
    astrological_principle_ta: Optional[str] = None
    chart_evidence: List[str] = Field(default_factory=list)
    match_reasons: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    applicable_gender: Optional[str] = "both"
    limitations: Optional[str] = None
    limitations_en: Optional[str] = None
    limitations_ta: Optional[str] = None


class RuleSynthesisItem(BaseModel):
    synthesis_id: str
    category: str
    title_en: str
    title_ta: str
    verdict_type: str  # e.g. "protection_overcomes_delay", "affliction_mitigated", "balanced"
    verdict_badge_en: str
    verdict_badge_ta: str
    summary_en: str
    summary_ta: str
    detailed_analysis_en: Optional[str] = None
    detailed_analysis_ta: Optional[str] = None
    dignity_analysis_en: Optional[str] = None
    dignity_analysis_ta: Optional[str] = None
    interacting_rule_ids: List[str] = Field(default_factory=list)
    participating_planets: List[str] = Field(default_factory=list)


class EvaluateRulesRequest(BaseModel):
    horoscope: Optional[HoroscopeResponse] = None
    saved_horoscope_id: Optional[str] = None
    category_slug: Optional[str] = None  # None = evaluate all categories
    subcategory: Optional[str] = None
    chart_scope: Optional[str] = "both"  # "d1", "d9", "both"
    astrology_system: Optional[str] = "all"  # "vedic", "kp", "combined", "all"
    language: str = "en"  # "en" or "ta"
    gender: Optional[str] = None  # "male", "female", "all"
    dasa: Optional[Dict[str, Any]] = None
    kp: Optional[Dict[str, Any]] = None
    custom_rules: Optional[List[Dict[str, Any]]] = None


class EvaluateRulesResponse(BaseModel):
    total_rules_evaluated: int
    total_matched: int
    total_unevaluable: int
    category_slug: Optional[str] = None
    subcategory: Optional[str] = None
    language: str = "en"
    results: List[EvaluatedRuleItem]
    syntheses: Optional[List[RuleSynthesisItem]] = Field(default_factory=list)


class RuleValidationRequest(BaseModel):
    rule: Dict[str, Any]


class RuleValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)


class RuleTestRequest(BaseModel):
    rule: Dict[str, Any]
    horoscope: Optional[HoroscopeResponse] = None
    saved_horoscope_id: Optional[str] = None
    dasa: Optional[Dict[str, Any]] = None
    kp: Optional[Dict[str, Any]] = None
    language: str = "en"
