"""Numerology Data Schemas - Requests, Outputs, Matrix Structures, and Persistence.

Provides strictly typed, validated models for Traditional Numerology, Destiny Matrix,
Advanced Analysis (Lo Shu / Pinnacles), and Saved Reports.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# ------------------------------------------------------------------------------
# 1. Traditional Numerology Models
# ------------------------------------------------------------------------------

class TraditionalNumerologyRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of person")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    system_convention: str = Field("pythagorean", description="Calculation convention: 'pythagorean' or 'chaldean'")
    language: str = Field("en", description="Report language: 'en' or 'ta'")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Full name cannot be empty.")
        # Ensure name contains at least one valid alphabet or letter character
        if not any(c.isalpha() for c in cleaned):
            raise ValueError("Full name must contain at least one valid alphabet or letter character.")
        return cleaned

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
    raw_value: Optional[int] = None
    reduction_steps: Optional[List[str]] = None


class LetterMapping(BaseModel):
    char: str
    value: int
    is_vowel: bool
    word: str


class WordBreakdown(BaseModel):
    word: str
    letter_sum: int
    vowel_sum: int
    consonant_sum: int
    reduced_expression: int


class KarmicDebtItem(BaseModel):
    number: int
    source: str
    title: str
    description: str
    remedy_focus: str


class CalculationBreakdown(BaseModel):
    system_convention: str
    source_birth_date: str
    birth_date_digits: List[int]
    life_path_period_reduction: Dict[str, Any]
    life_path_full_sum: Dict[str, Any]
    birth_number_reduction: Dict[str, Any]
    letter_mappings: List[LetterMapping]
    word_breakdowns: List[WordBreakdown]
    expression_reduction: List[str]
    soul_urge_reduction: List[str]
    personality_reduction: List[str]
    maturity_reduction: List[str]


class TraditionalNumerologyResponse(BaseModel):
    person_name: str
    birth_date: str
    system_convention: str
    engine_version: str
    birth_psychic_number: Optional[TraditionalNumberDetail] = None
    life_path: TraditionalNumberDetail
    expression_destiny: TraditionalNumberDetail
    soul_urge: TraditionalNumberDetail
    personality: TraditionalNumberDetail
    birthday_number: TraditionalNumberDetail
    attitude_number: TraditionalNumberDetail
    maturity_number: TraditionalNumberDetail
    personal_year: TraditionalNumberDetail
    karmic_debts: List[KarmicDebtItem] = Field(default_factory=list)
    calculation_breakdown: Optional[CalculationBreakdown] = None
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
    method: str = Field(..., pattern="^(traditional|destiny_matrix|advanced|name_correction|business|phone|vehicle|property|marriage|family)$")
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

class ExportNumerologyPdfRequest(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=100)
    birth_date: Optional[str] = None
    method: str = Field(..., pattern="^(traditional|destiny_matrix|advanced|name_correction|business|phone|vehicle|property|marriage|family)$")
    system_convention: str = "pythagorean"
    language: str = Field("en", pattern="^(en|ta)$")
    calculation_data: Dict[str, Any]
    interpretation_data: Optional[Dict[str, Any]] = None
    display_number: Optional[int] = None
    report_id: Optional[str] = None


class NumerologyMetadataResponse(BaseModel):
    service: str
    engine_version: str
    methods: List[Dict[str, Any]]
    conventions: List[Dict[str, Any]]
    supported_languages: List[str]
    disclaimer: str


# ------------------------------------------------------------------------------
# 5. Name Analysis & Correction Studio Models
# ------------------------------------------------------------------------------

class NameComponentDetail(BaseModel):
    component_type: str
    text: str
    expression: int
    compound_expression: int
    soul_urge: int
    personality: int
    reduction_steps: List[str]
    letter_mappings: List[LetterMapping] = Field(default_factory=list)


class NameAnalysisRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Name to analyze")
    system_convention: str = Field("pythagorean", pattern="^(pythagorean|chaldean)$")
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Name cannot be empty or blank")
        cleaned = re.sub(r"[\s\.\-_',;:!\?\"/\\()\[\]{}]+", "", s)
        if not cleaned:
            raise ValueError("Name must contain alphabetic characters, not just punctuation")
        return s


class NameAnalysisResponse(BaseModel):
    full_name: str
    convention: str
    engine_version: str
    expression: int
    compound_expression: int
    soul_urge: int
    personality: int
    is_master: bool
    reduction_steps: List[str]
    letter_mappings: List[LetterMapping]
    word_breakdowns: List[WordBreakdown]
    components: List[NameComponentDetail]


class NameCorrectionRequest(BaseModel):
    original_name: str = Field(..., min_length=1, max_length=100, description="Original baseline name")
    system_convention: str = Field("chaldean", pattern="^(pythagorean|chaldean)$")
    target_number: Optional[int] = Field(None, description="Explicit target number (1-9, 11, 22, 33)")
    birth_date: Optional[str] = Field(None, description="Optional birth date in YYYY-MM-DD for harmony matching")
    custom_variations: Optional[List[str]] = Field(default_factory=list, description="User-entered alternative spellings")
    language: str = Field("en", description="Language: 'en' or 'ta'")
    max_candidates: int = Field(25, ge=1, le=50, description="Max candidate suggestions (1-50)")
    allow_vowel_changes: bool = Field(True, description="Enable vowel alternations (ee/i, oo/u, etc.)")
    allow_consonant_doubling: bool = Field(True, description="Enable natural consonant doubling/dedoubling")
    allow_phonetic_replacements: bool = Field(True, description="Enable phonetic & transliteration equivalents (th/t, d/dh, etc.)")

    @field_validator("original_name")
    @classmethod
    def validate_original_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Original name cannot be empty")
        cleaned = re.sub(r"[\s\.\-_',;:!\?\"/\\()\[\]{}]+", "", s)
        if not cleaned:
            raise ValueError("Original name must contain alphabetic characters, not just punctuation")
        return s

    @field_validator("target_number")
    @classmethod
    def validate_target(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33):
                raise ValueError("Target number must be 1-9 or master number 11, 22, 33")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v_clean = v.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v_clean):
                raise ValueError("Birth date must be in YYYY-MM-DD format")
            return v_clean
        return None


class NameCandidateResult(BaseModel):
    name: str
    variation_type: str
    expression_number: int
    compound_expression: int
    soul_urge_number: int
    personality_number: int
    is_master: bool
    matches_target: bool
    harmony_score: float
    pronunciation_score: float
    simplicity_score: float
    composite_score: float
    letter_mappings: List[LetterMapping] = Field(default_factory=list)
    word_breakdowns: List[WordBreakdown] = Field(default_factory=list)
    reduction_steps: List[str] = Field(default_factory=list)
    vibrational_synthesis: str


class NameCorrectionResponse(BaseModel):
    original_name: str
    system_convention: str
    engine_version: str
    target_number: int
    target_source: str
    original_analysis: NameAnalysisResponse
    candidates: List[NameCandidateResult]
    scoring_explanation: Dict[str, Any]


# ------------------------------------------------------------------------------
# 6. Business & Brand Numerology Studio Models
# ------------------------------------------------------------------------------

class FounderInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD")
    role: Optional[str] = Field(None, description="Founder role e.g. CEO, Managing Partner")
    share_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Equity or partnership share")

    @field_validator("birth_date")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if v:
            clean = v.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
                raise ValueError("Founder birth date must be in YYYY-MM-DD format")
            return clean
        return None


class FounderEvaluationResult(BaseModel):
    name: str
    birth_date: Optional[str] = None
    role: Optional[str] = None
    share_percentage: Optional[float] = None
    psychic_number: Optional[int] = None
    life_path_number: Optional[int] = None
    name_expression: int
    psychic_harmony_score: Optional[float] = None
    life_path_harmony_score: Optional[float] = None
    alignment_score: float
    alignment_level: str
    notes: str


class TaglineAnalysisResult(BaseModel):
    tagline: str
    expression_number: int
    compound_expression: int
    synergy_score: float
    synergy_interpretation: str


class DomainHandleAnalysisResult(BaseModel):
    raw_handle: str
    clean_handle: str
    expression_number: int
    compound_expression: int
    matches_brand: bool


class BusinessCandidateResult(BaseModel):
    name: str
    candidate_type: str
    expression_number: int
    compound_expression: int
    soul_urge_number: int
    personality_number: int
    is_master: bool
    industry_harmony_score: float
    founder_harmony_score: float
    pronunciation_score: float
    simplicity_score: float
    composite_score: float
    is_favorable: bool
    vibrational_synthesis: str
    letter_mappings: List[LetterMapping] = Field(default_factory=list)
    reduction_steps: List[str] = Field(default_factory=list)
    founder_alignments: List[FounderEvaluationResult] = Field(default_factory=list)


class BusinessNumerologyRequest(BaseModel):
    legal_name: str = Field(..., min_length=1, max_length=120, description="Full registered legal company name")
    brand_name: Optional[str] = Field(None, max_length=100, description="Optional public brand or trade name")
    tagline: Optional[str] = Field(None, max_length=200, description="Brand slogan or tagline")
    domain_or_handle: Optional[str] = Field(None, max_length=100, description="Website domain or social handle")
    system_convention: str = Field("chaldean", pattern="^(pythagorean|chaldean)$")
    industry_category: str = Field(
        "other",
        pattern="^(technology|retail|education|healthcare|finance|manufacturing|astrology|creative|other)$",
    )
    founders: List[FounderInput] = Field(default_factory=list)
    custom_candidates: List[str] = Field(default_factory=list)
    max_candidates: int = Field(25, ge=1, le=50)
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("legal_name")
    @classmethod
    def validate_legal_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Legal company name cannot be empty")
        cleaned = re.sub(r"[\s\.\-_',;:!\?\"/\\()\[\]{}]+", "", s)
        if not cleaned:
            raise ValueError("Company name must contain alphabetic characters, not just punctuation")
        return s


class BusinessNumerologyResponse(BaseModel):
    legal_name: str
    normalized_brand_name: str
    acronym: str
    detected_suffixes: List[str]
    system_convention: str
    industry_category: str
    industry_vibrations: Dict[str, Any]
    engine_version: str
    legal_analysis: BusinessCandidateResult
    brand_analysis: BusinessCandidateResult
    tagline_analysis: Optional[TaglineAnalysisResult] = None
    domain_analysis: Optional[DomainHandleAnalysisResult] = None
    partnership_matrix: Dict[str, Any]
    candidates: List[BusinessCandidateResult]
    scoring_explanation: Dict[str, Any]


# ------------------------------------------------------------------------------
# 7. Phone & Mobile Number Numerology Models
# ------------------------------------------------------------------------------

class PhoneAnalysisDetail(BaseModel):
    digits: str
    digit_count: int
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    frequencies: Dict[str, int]
    dominant_digits: List[int]
    missing_digits: List[int]
    zero_count: int
    ruling_planet: str
    keyword: str
    vibrational_meaning: str
    patterns: Dict[str, Any]


class PhoneCandidateResult(BaseModel):
    raw_input: str
    masked_phone: str
    national_number: str
    formatted_national: str
    display_international: str
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    frequencies: Dict[str, int]
    dominant_digits: List[int]
    missing_digits: List[int]
    zero_count: int
    ruling_planet: str
    keyword: str
    vibrational_meaning: str
    patterns: Dict[str, Any]
    personal_compatibility: Optional[Dict[str, Any]] = None
    industry_compatibility: Optional[Dict[str, Any]] = None
    personal_score: Optional[float] = None
    industry_score: Optional[float] = None
    vanity_score: float
    composite_score: float
    is_favorable: bool


class PhoneNumerologyRequest(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=30, description="Phone number to analyze")
    system_convention: str = Field("chaldean", pattern="^(pythagorean|chaldean)$")
    include_country_code: bool = Field(False, description="Analyze full number including country code instead of national subscriber digits")
    birth_date: Optional[str] = Field(None, description="Optional owner birth date YYYY-MM-DD for personal harmony")
    industry_category: Optional[str] = Field(
        None,
        pattern="^(technology|retail|education|healthcare|finance|manufacturing|astrology|creative|other)$",
        description="Optional business industry sector"
    )
    candidate_numbers: List[str] = Field(default_factory=list, description="Alternative candidate numbers to compare")
    max_candidates: int = Field(25, ge=1, le=50)
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Phone number cannot be empty")
        if not re.match(r"^[\+]?[0-9\s\-\(\)\.]+$", s):
            raise ValueError("Phone number contains invalid characters. Only digits, spaces, hyphens, and parentheses are allowed.")
        digits = re.sub(r"\D", "", s)
        if len(digits) < 7:
            raise ValueError(f"Phone number too short ({len(digits)} digits). Minimum 7 digits required.")
        if len(digits) > 15:
            raise ValueError(f"Phone number exceeds ITU-T E.164 maximum ({len(digits)} digits). Maximum 15 digits allowed.")
        return s

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        s = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        return s


class PhoneNumerologyResponse(BaseModel):
    raw_input: str
    masked_phone: str
    national_number: str
    formatted_national: str
    all_digits: str
    display_international: str
    detected_country_code: Optional[str] = None
    detected_country_name: Optional[str] = None
    is_indian_mobile: bool
    system_convention: str
    include_country_code: bool
    engine_version: str
    primary_analysis: PhoneAnalysisDetail
    national_analysis: PhoneAnalysisDetail
    international_analysis: PhoneAnalysisDetail
    missing_digits_analysis: List[Dict[str, Any]]
    zero_significance: str
    personal_compatibility: Optional[Dict[str, Any]] = None
    industry_compatibility: Optional[Dict[str, Any]] = None
    candidates: List[PhoneCandidateResult]
    scoring_explanation: Dict[str, Any]


# ------------------------------------------------------------------------------
# 8. Vehicle & Asset Registration Number Numerology Models
# ------------------------------------------------------------------------------

class VehicleOwnerInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD")
    role: Optional[str] = Field("Primary Owner", description="Owner role e.g. Primary Driver, Co-Driver, Spouse")
    is_primary: bool = Field(True, description="Whether this driver is the primary user")

    @field_validator("birth_date")
    @classmethod
    def validate_dob(cls, v: str) -> str:
        clean = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        return clean


class VehicleOwnerEvaluation(BaseModel):
    name: str
    birth_date: str
    role: str
    is_primary: bool
    psychic_number: int
    life_path_number: int
    psychic_harmony_score: float
    life_path_harmony_score: float
    personal_score: float
    level: str
    synthesis: str


class VehicleAnalysisDetail(BaseModel):
    calculation_mode: str
    mode_label: str
    source_string: str
    character_mappings: List[Dict[str, Any]]
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    ruling_planet: str
    keyword: str
    vibrational_meaning: str


class VehicleCandidateResult(BaseModel):
    raw_input: str
    normalized_registration: str
    plate_classification: str
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    rto_code: Optional[str] = None
    series_letters: Optional[str] = None
    numeric_digits: str
    calculation_mode: str
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    patterns: Dict[str, Any]
    vanity_score: float
    usage_score: Optional[float] = None
    owner_score: Optional[float] = None
    composite_score: float
    is_favorable: bool


class VehicleNumerologyRequest(BaseModel):
    registration_number: str = Field(..., min_length=2, max_length=25, description="Vehicle registration plate number")
    system_convention: str = Field("chaldean", pattern="^(pythagorean|chaldean)$")
    calculation_mode: str = Field(
        "digits_only",
        pattern="^(digits_only|numeric_all|full_alphanumeric)$",
        description="Calculation mode: digits_only, numeric_all, or full_alphanumeric",
    )
    vehicle_usage: str = Field(
        "personal",
        pattern="^(personal|family|commercial|fleet)$",
        description="Vehicle intended usage archetype",
    )
    primary_birth_date: Optional[str] = Field(None, description="Optional primary owner birth date in YYYY-MM-DD")
    primary_owner_name: Optional[str] = Field(None, max_length=100, description="Optional primary owner name")
    co_owners: List[VehicleOwnerInput] = Field(default_factory=list, description="Optional co-drivers or co-owners")
    candidate_numbers: List[str] = Field(default_factory=list, description="Alternative candidate plate numbers to compare")
    max_candidates: int = Field(25, ge=1, le=50)
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("registration_number")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Registration number cannot be empty.")
        if not re.match(r"^[A-Za-z0-9\s\-\.]+$", s):
            raise ValueError("Registration number contains invalid characters. Only letters, digits, spaces, and hyphens are permitted.")
        clean_len = len(re.sub(r"[\s\-\.]+", "", s))
        if clean_len < 2:
            raise ValueError("Registration number is too short.")
        if clean_len > 16:
            raise ValueError("Registration number exceeds maximum length of 16 characters.")
        return s

    @field_validator("primary_birth_date")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        s = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            raise ValueError("Primary owner birth date must be in YYYY-MM-DD format")
        return s


class VehicleNumerologyResponse(BaseModel):
    raw_input: str
    normalized_registration: str
    formatted_registration: str
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    rto_code: Optional[str] = None
    series_letters: Optional[str] = None
    numeric_digits: str
    is_valid_indian_format: bool
    plate_classification: str
    system_convention: str
    calculation_mode: str
    vehicle_usage: str
    engine_version: str
    primary_analysis: VehicleAnalysisDetail
    digits_only_analysis: VehicleAnalysisDetail
    numeric_all_analysis: VehicleAnalysisDetail
    full_alphanumeric_analysis: VehicleAnalysisDetail
    patterns: Dict[str, Any]
    vanity_score: float
    usage_alignment: Dict[str, Any]
    owner_alignments: List[VehicleOwnerEvaluation]
    overall_owner_score: Optional[float] = None
    candidates: List[VehicleCandidateResult]
    scoring_explanation: Dict[str, Any]
    disclaimer: str


# ------------------------------------------------------------------------------
# 9. House, Flat & Property Numerology Models
# ------------------------------------------------------------------------------

class PropertyResidentInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD")
    role: Optional[str] = Field("Resident", description="Resident role e.g. Spouse, Child, Parent, Co-Owner")
    is_primary: bool = Field(False, description="Whether this is the primary resident/owner")

    @field_validator("birth_date")
    @classmethod
    def validate_dob(cls, v: str) -> str:
        clean = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
            raise ValueError("Resident birth date must be in YYYY-MM-DD format")
        return clean


class PropertyResidentEvaluation(BaseModel):
    name: str
    birth_date: str
    role: str
    is_primary: bool
    psychic_number: int
    life_path_number: int
    psychic_harmony_score: float
    life_path_harmony_score: float
    personal_score: float
    level: str
    synthesis: str


class PropertyComponentDetail(BaseModel):
    component_name: str
    component_label: str
    calculation_mode: Optional[str] = None
    source_string: str
    included_characters: List[str]
    character_mappings: List[Dict[str, Any]]
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    ruling_planet: str
    keyword: str
    vibrational_meaning: str
    formula_explanation: Optional[str] = None


class PropertyCandidateInput(BaseModel):
    door_flat_number: Optional[str] = None
    building_number: Optional[str] = None
    floor_number: Optional[str] = None
    plot_number: Optional[str] = None
    building_name: Optional[str] = None
    label: Optional[str] = None


class PropertyCandidateResult(BaseModel):
    label: str
    door_flat_number: Optional[str] = None
    building_number: Optional[str] = None
    floor_number: Optional[str] = None
    plot_number: Optional[str] = None
    building_name: Optional[str] = None
    calculation_mode: str
    compound_sum: int
    root_number: int
    single_root: int
    is_master: bool
    reduction_steps: List[str]
    ruling_planet: str
    keyword: str
    usage_score: float
    owner_score: Optional[float] = None
    composite_score: float
    is_favorable: bool


class PropertyNumerologyRequest(BaseModel):
    property_category: str = Field(
        "apartment_flat",
        pattern="^(independent_house|apartment_flat|commercial_office|commercial_shop|plot_land|multi_unit)$",
        description="Type of property",
    )
    tenure_type: str = Field(
        "purchased",
        pattern="^(purchased|rental)$",
        description="Tenure: purchased or rental",
    )
    door_flat_number: Optional[str] = Field(None, max_length=50, description="Door or flat number e.g. 4B, 102")
    building_number: Optional[str] = Field(None, max_length=50, description="Building or tower number e.g. Tower 3")
    block_or_wing: Optional[str] = Field(None, max_length=50, description="Block or wing e.g. Wing A")
    floor_number: Optional[str] = Field(None, max_length=20, description="Floor level e.g. 4, 12, Ground")
    plot_number: Optional[str] = Field(None, max_length=50, description="Plot number e.g. Plot 42")
    building_name: Optional[str] = Field(None, max_length=100, description="Project, building, or society name")
    facing_direction: Optional[str] = Field(
        None,
        description="Facing direction: North, North-East, East, South-East, South, South-West, West, North-West",
    )
    property_usage: str = Field(
        "residential_living",
        pattern="^(residential_living|commercial_business|rental_investment|creative_studio|spiritual_wellness)$",
        description="Property intended usage",
    )
    system_convention: str = Field("chaldean", pattern="^(pythagorean|chaldean)$")
    calculation_mode: str = Field(
        "door_number",
        pattern="^(door_number|building_number|floor_number|plot_number|combined_property|full_alphanumeric)$",
        description="Active calculation mode",
    )
    primary_birth_date: Optional[str] = Field(None, description="Head of household birth date in YYYY-MM-DD")
    primary_owner_name: Optional[str] = Field(None, max_length=100, description="Primary owner name")
    co_residents: List[PropertyResidentInput] = Field(default_factory=list, description="Family or co-residents")
    candidate_properties: List[PropertyCandidateInput] = Field(default_factory=list, description="Alternative properties to compare")
    max_candidates: int = Field(25, ge=1, le=50)
    language: str = Field("en", description="Language: 'en' or 'ta'")

    @field_validator("primary_birth_date")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        s = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            raise ValueError("Primary resident birth date must be in YYYY-MM-DD format")
        return s


class PropertyNumerologyResponse(BaseModel):
    property_category: str
    tenure_type: str
    door_flat_number: str
    building_number: str
    block_or_wing: str
    floor_number: str
    plot_number: str
    building_name: str
    facing_direction: Optional[str] = None
    full_identifier: str
    system_convention: str
    calculation_mode: str
    property_usage: str
    primary_analysis: PropertyComponentDetail
    door_analysis: PropertyComponentDetail
    building_analysis: PropertyComponentDetail
    floor_analysis: PropertyComponentDetail
    plot_analysis: PropertyComponentDetail
    combined_analysis: PropertyComponentDetail
    full_alphanumeric_analysis: PropertyComponentDetail
    usage_alignment: Dict[str, Any]
    vastu_alignment: Optional[Dict[str, Any]] = None
    resident_alignments: List[PropertyResidentEvaluation]
    overall_household_score: Optional[float] = None
    candidates: List[PropertyCandidateResult]
    scoring_explanation: Dict[str, Any]
    disclaimer: str


# ------------------------------------------------------------------------------
# 9. Marriage Compatibility by Numerology Studio Models
# ------------------------------------------------------------------------------

class MarriagePersonInput(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of person")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    preferred_name: Optional[str] = Field(None, max_length=100)
    surname_initials: Optional[str] = Field(None, max_length=50)
    relationship_status: Optional[str] = Field(None, description="e.g. dating, engaged, married, partnership")
    language: Optional[str] = Field("en", description="Language preference: 'en' or 'ta'")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        s = v.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        parts = [int(p) for p in s.split("-")]
        year, month, day = parts[0], parts[1], parts[2]
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")
        if not (1 <= day <= 31):
            raise ValueError(f"Invalid day: {day}")
        if not (1900 <= year <= 2100):
            raise ValueError(f"Year out of reasonable range (1900-2100): {year}")
        return s


class MarriagePersonProfile(BaseModel):
    person_label: str
    full_name: Optional[str] = None
    preferred_name: Optional[str] = None
    surname_initials: Optional[str] = None
    birth_date: str
    birth_psychic_number: int
    birth_psychic_compound: int
    birth_psychic_planet: str
    birth_psychic_archetype: str
    birth_psychic_reduction_steps: List[str]
    life_path_number: int
    life_path_compound: int
    life_path_planet: str
    life_path_archetype: str
    life_path_reduction_steps: List[str]
    is_life_path_master: bool
    expression_number: Optional[int] = None
    expression_compound: Optional[int] = None
    expression_planet: Optional[str] = None
    expression_reduction_steps: Optional[List[str]] = None
    is_expression_master: Optional[bool] = False
    soul_urge_number: Optional[int] = None
    soul_urge_compound: Optional[int] = None
    personality_number: Optional[int] = None
    personality_compound: Optional[int] = None
    master_numbers: List[int] = Field(default_factory=list)
    karmic_debts: List[Dict[str, Any]] = Field(default_factory=list)
    key_attributes: List[str] = Field(default_factory=list)


class MarriageComponentComparison(BaseModel):
    component_name: str
    person_a_number: int
    person_b_number: int
    person_a_label: str
    person_b_label: str
    score: float
    weight: float
    harmony_level: str
    planetary_dynamic: str
    interpretation: str


class MarriageNumerologyRequest(BaseModel):
    person_a: MarriagePersonInput
    person_b: MarriagePersonInput
    system_convention: str = Field("pythagorean", pattern="^(pythagorean|chaldean)$")
    language: str = Field("en", pattern="^(en|ta)$")


class MarriageNumerologyResponse(BaseModel):
    system_convention: str
    engine_version: str
    relationship_status: Optional[str] = None
    person_a_profile: MarriagePersonProfile
    person_b_profile: MarriagePersonProfile
    psychic_compatibility: MarriageComponentComparison
    life_path_compatibility: MarriageComponentComparison
    expression_compatibility: Optional[MarriageComponentComparison] = None
    soul_urge_compatibility: Optional[MarriageComponentComparison] = None
    personality_compatibility: Optional[MarriageComponentComparison] = None
    emotional_themes: List[str]
    communication_themes: List[str]
    shared_strengths: List[str]
    potential_challenges: List[str]
    conversation_prompts: List[str]
    growth_recommendations: List[str]
    overall_score: float
    overall_harmony_level: str
    overall_synthesis: str
    scoring_formula_explanation: Dict[str, Any]
    disclaimer: str


# ------------------------------------------------------------------------------
# 12. Family & Baby Numerology Studio Models
# ------------------------------------------------------------------------------

class FamilyMemberInput(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[str] = Field(None, min_length=10, max_length=10)
    role: Optional[str] = None
    relationship: Optional[str] = None
    gender: Optional[str] = None
    preferred_name: Optional[str] = None
    surname: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_roles(cls, data: Any) -> Any:
        if isinstance(data, dict):
            r = data.get("role") or data.get("relationship") or "child"
            data["role"] = r.lower()
        return data


class FamilyMemberEvaluation(BaseModel):
    id: str
    name: str
    role: str
    birth_date: Optional[str] = None
    birth_psychic_number: Optional[int] = None
    birth_psychic_planet: Optional[str] = None
    life_path_number: Optional[int] = None
    life_path_planet: Optional[str] = None
    is_life_path_master: bool = False
    expression_number: Optional[int] = None
    compound_expression: Optional[int] = None
    soul_urge_number: Optional[int] = None
    personality_number: Optional[int] = None
    karmic_debts: List[int] = []
    archetype: str
    element: str
    reduction_steps: List[str] = []
    short_summary: str


class BabyNameCandidateResult(BaseModel):
    name: str
    is_generated: bool
    variation_type: str
    pythagorean_expression: int
    pythagorean_compound: int
    chaldean_expression: int
    chaldean_compound: int
    active_expression: int
    active_compound: int
    soul_urge: int
    personality: int
    ruling_planet: str
    archetype: str
    dob_harmony_score: int
    parent_harmony_score: int
    pronunciation_score: int
    simplicity_score: int
    composite_score: int
    is_master: bool
    reduction_steps: List[str]
    letter_mappings: List[LetterMapping]
    vibrational_synthesis: str


class FamilyPairwiseComparison(BaseModel):
    person_a_id: str
    person_a_name: str
    person_a_role: str
    person_b_id: str
    person_b_name: str
    person_b_role: str
    relationship_type: str
    psychic_harmony_score: int
    life_path_harmony_score: int
    expression_harmony_score: Optional[int] = None
    composite_harmony_score: int
    harmony_level: str
    planetary_dynamic: str
    shared_strengths: List[str]
    growth_edges: List[str]
    nurturing_prompt: str


class FamilyDistributionItem(BaseModel):
    number: int
    count: int
    percentage: float
    ruling_planet: str
    element: str
    members_with_number: List[str] = []


class FamilyNumerologyRequest(BaseModel):
    family_name: Optional[str] = Field("Family", max_length=100)
    members: List[FamilyMemberInput] = Field(..., min_length=1, max_length=20)
    candidate_names: Optional[List[str]] = None
    baby_candidates: Optional[List[str]] = None
    baby_dob: Optional[str] = Field(None, min_length=10, max_length=10)
    surname: Optional[str] = None
    target_root: Optional[int] = Field(None, ge=1, le=9)
    target_root_number: Optional[int] = Field(None, ge=1, le=9)
    system_convention: str = Field("pythagorean", pattern="^(pythagorean|chaldean)$")
    generate_suggestions: bool = True
    auto_generate_variations: Optional[bool] = None
    language: str = Field("en", pattern="^(en|ta)$")

    @model_validator(mode="before")
    @classmethod
    def normalize_request_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("candidate_names") and data.get("baby_candidates"):
                data["candidate_names"] = data["baby_candidates"]
            if data.get("target_root") is None and data.get("target_root_number"):
                data["target_root"] = data["target_root_number"]
            if "generate_suggestions" not in data and "auto_generate_variations" in data:
                data["generate_suggestions"] = data["auto_generate_variations"]
        return data


class FamilyNumerologyResponse(BaseModel):
    family_name: str
    system_convention: str
    language: str
    members_evaluated: List[FamilyMemberEvaluation]
    pairwise_comparisons: List[FamilyPairwiseComparison]
    number_distribution: List[FamilyDistributionItem]
    dominant_vibrations: List[int]
    missing_vibrations: List[int]
    elemental_balance: Dict[str, Any]
    baby_name_candidates: List[BabyNameCandidateResult]
    overall_family_harmony_score: int
    overall_family_harmony_level: str
    scoring_formula_explanation: Dict[str, Any]
    family_strengths: List[str]
    family_challenges: List[str]
    reflection_questions: List[str]
    overall_synthesis: str
    engine_version: str
    disclaimer: str





