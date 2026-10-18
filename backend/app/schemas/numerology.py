"""Numerology Data Schemas - Requests, Outputs, Matrix Structures, and Persistence.

Provides strictly typed, validated models for Traditional Numerology, Destiny Matrix,
Advanced Analysis (Lo Shu / Pinnacles), and Saved Reports.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re


# ------------------------------------------------------------------------------
# 1. Traditional Numerology Models
# ------------------------------------------------------------------------------

class TraditionalNumerologyRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of person")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    system_convention: str = Field("pythagorean", description="Calculation convention: 'pythagorean' or 'chaldean'")
    language: str = Field("en", description="Report language: 'en' or 'ta'")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v.strip()):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        parts = [int(p) for p in v.split("-")]
        year, month, day = parts[0], parts[1], parts[2]
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")
        if not (1 <= day <= 31):
            raise ValueError(f"Invalid day: {day}")
        if not (1900 <= year <= 2100):
            raise ValueError(f"Year out of reasonable range (1900-2100): {year}")
        return v.strip()

    @field_validator("system_convention")
    @classmethod
    def validate_convention(cls, v: str) -> str:
        val = v.strip().lower()
        if val not in ("pythagorean", "chaldean"):
            raise ValueError("System convention must be 'pythagorean' or 'chaldean'")
        return val


class TraditionalNumberDetail(BaseModel):
    number_name: str
    number_value: int
    calculation_method: str
    is_master: bool
    short_interpretation: str
    detailed_interpretation: str
    key_attributes: List[str]


class TraditionalNumerologyResponse(BaseModel):
    person_name: str
    birth_date: str
    system_convention: str
    engine_version: str
    life_path: TraditionalNumberDetail
    expression_destiny: TraditionalNumberDetail
    soul_urge: TraditionalNumberDetail
    personality: TraditionalNumberDetail
    birthday_number: TraditionalNumberDetail
    attitude_number: TraditionalNumberDetail
    maturity_number: TraditionalNumberDetail
    personal_year: TraditionalNumberDetail
    karmic_lessons: List[int]
    hidden_passion: List[int]
    strengths: List[str]
    challenges: List[str]
    career_tendencies: List[str]
    financial_tendencies: List[str]
    love_themes: List[str]
    overall_synthesis: str


# ------------------------------------------------------------------------------
# 2. Destiny Matrix Models
# ------------------------------------------------------------------------------

class DestinyMatrixRequest(BaseModel):
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    person_name: Optional[str] = Field(None, max_length=100)
    partner_birth_date: Optional[str] = Field(None, description="Optional partner birth date for compatibility")
    partner_name: Optional[str] = Field(None, max_length=100)
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v.strip()):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        return v.strip()


class MatrixNodeDetail(BaseModel):
    node_id: str
    label: str
    arcana_number: int
    arcana_name: str
    meaning: str
    positive_traits: str
    negative_traps: str
    recommendations: str


class PurposeBreakdown(BaseModel):
    personal_purpose: int # Sky + Earth (Ages 20-40)
    social_purpose: int   # Father + Mother Lines (Ages 40-60)
    spiritual_purpose: int # Personal + Social
    planetary_purpose: int # Social + Spiritual


class AgeTimelinePoint(BaseModel):
    age: int
    arcana_number: int
    theme: str
    description: str


class CompatibilityResult(BaseModel):
    person1_name: str
    person2_name: str
    relationship_purpose: int
    couple_karmic_task: int
    shared_finance: int
    love_harmony: int
    compatibility_synthesis: str


class DestinyMatrixResponse(BaseModel):
    birth_date: str
    person_name: Optional[str]
    engine_version: str
    day_arcana: MatrixNodeDetail
    month_arcana: MatrixNodeDetail
    year_arcana: MatrixNodeDetail
    karmic_tail_base: MatrixNodeDetail
    karmic_tail_triad: List[int]
    comfort_zone: MatrixNodeDetail
    father_spirit: MatrixNodeDetail
    mother_spirit: MatrixNodeDetail
    father_matter: MatrixNodeDetail
    mother_matter: MatrixNodeDetail
    love_line: MatrixNodeDetail
    money_line: MatrixNodeDetail
    purpose: PurposeBreakdown
    age_timeline: List[AgeTimelinePoint]
    compatibility: Optional[CompatibilityResult] = None
    strengths: List[str]
    challenges: List[str]
    career_tendencies: List[str]
    financial_tendencies: List[str]
    love_themes: List[str]
    overall_synthesis: str


# ------------------------------------------------------------------------------
# 3. Advanced Analysis Models (Lo Shu & Pinnacles)
# ------------------------------------------------------------------------------

class AdvancedAnalysisRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    language: str = Field("en", description="Language: 'en' or 'ta'")


class LoShuGridResult(BaseModel):
    grid_counts: Dict[str, int] # Counts of digits 1-9 in DOB
    planes: Dict[str, Dict[str, Any]] # Thought, Will, Action, Mental, Emotional, Practical
    arrows_of_strength: List[Dict[str, str]]
    arrows_of_weakness: List[Dict[str, str]]


class PinnacleChallengeResult(BaseModel):
    pinnacles: List[Dict[str, Any]]
    challenges: List[Dict[str, Any]]


class AdvancedAnalysisResponse(BaseModel):
    full_name: str
    birth_date: str
    engine_version: str
    unicode_derived_name_number: int
    lo_shu: LoShuGridResult
    pinnacles_challenges: PinnacleChallengeResult
    karmic_debts: List[Dict[str, Any]]
    karmic_lessons: List[int]
    dominant_vibrations: List[int]
    strengths: List[str]
    challenges: List[str]
    career_tendencies: List[str]
    financial_tendencies: List[str]
    love_themes: List[str]
    overall_synthesis: str


# ------------------------------------------------------------------------------
# 4. Report Persistence Models
# ------------------------------------------------------------------------------

class SaveNumerologyReportRequest(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=100)
    birth_date: str = Field(..., min_length=10, max_length=10)
    method: str = Field(..., pattern="^(traditional|destiny_matrix|advanced)$")
    system_convention: str
    calculation_data: Dict[str, Any]
    interpretation_data: Dict[str, Any]


class SavedNumerologyReportResponse(BaseModel):
    id: str
    user_id: str
    display_number: int
    person_name: str
    birth_date: str
    method: str
    system_convention: str
    calculation_data: Dict[str, Any]
    interpretation_data: Dict[str, Any]
    engine_version: str
    created_at: str
    updated_at: str


class NumerologyMetadataResponse(BaseModel):
    service: str
    engine_version: str
    methods: List[Dict[str, Any]]
    conventions: List[Dict[str, Any]]
    supported_languages: List[str]
    disclaimer: str
