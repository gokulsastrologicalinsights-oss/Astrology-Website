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
    interpretation: str
    interpretation_en: str
    interpretation_ta: Optional[str] = None
    astrological_principle: str
    astrological_principle_en: str
    astrological_principle_ta: Optional[str] = None
    chart_evidence: List[str] = Field(default_factory=list)
    match_reasons: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    limitations: Optional[str] = None
    limitations_en: Optional[str] = None
    limitations_ta: Optional[str] = None


class EvaluateRulesRequest(BaseModel):
    horoscope: Optional[HoroscopeResponse] = None
    saved_horoscope_id: Optional[str] = None
    category_slug: Optional[str] = None  # None = evaluate all categories
    subcategory: Optional[str] = None
    chart_scope: Optional[str] = "both"  # "d1", "d9", "both"
    astrology_system: Optional[str] = "all"  # "vedic", "kp", "combined", "all"
    language: str = "en"  # "en" or "ta"
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
