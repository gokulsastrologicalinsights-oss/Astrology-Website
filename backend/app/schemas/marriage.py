"""Pydantic v2 schemas for the Comprehensive Vedic + KP Marriage Compatibility Engine."""

from __future__ import annotations
import uuid
from datetime import date, time
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.dosha import KujaDoshaResult


class MarriagePartnerInput(BaseModel):
    """Input payload representing one partner in a marriage compatibility evaluation."""
    name: Optional[str] = Field("Individual", description="Name of the individual")
    gender: Optional[str] = Field(None, description="Gender: 'male' or 'female'")
    birth_date: Optional[date] = Field(None, description="Birth date in ISO format YYYY-MM-DD", examples=["1992-04-14"])
    birth_time: Optional[time] = Field(None, description="Local birth time in ISO format HH:MM:SS (24-hour)", examples=["05:30:00"])
    is_birth_time_approximate: bool = Field(False, description="Flag indicating if birth time is approximate or uncertain")
    timezone: Optional[str] = Field(None, description="IANA timezone (e.g. 'Asia/Kolkata') or UTC offset string", examples=["Asia/Kolkata"])
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Geographic latitude in decimal degrees (-90 to +90)", examples=[13.0827])
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Geographic longitude in decimal degrees (-180 to +180)", examples=[80.2707])
    birth_input: Optional[BirthInput] = Field(None, description="Direct birth coordinates and time alternative")
    saved_horoscope_id: Optional[str] = Field(None, description="UUID of a saved horoscope in Supabase")

    @model_validator(mode="after")
    def validate_partner_data(self) -> MarriagePartnerInput:
        if self.saved_horoscope_id:
            clean_id = self.saved_horoscope_id.strip()
            try:
                uuid.UUID(clean_id)
            except Exception:
                raise ValueError(f"Invalid saved horoscope UUID: '{self.saved_horoscope_id}'")
            return self

        # If birth_input is supplied, populate fields
        if self.birth_input:
            if not self.birth_date:
                self.birth_date = self.birth_input.birth_date
            if not self.birth_time:
                self.birth_time = self.birth_input.birth_time
            if not self.timezone:
                self.timezone = self.birth_input.timezone
            if self.latitude is None:
                self.latitude = self.birth_input.latitude
            if self.longitude is None:
                self.longitude = self.birth_input.longitude

        # Check required fields for direct calculation
        missing = []
        if not self.birth_date:
            missing.append("birth_date")
        if not self.birth_time:
            missing.append("birth_time")
        if not self.timezone:
            missing.append("timezone")
        if self.latitude is None:
            missing.append("latitude")
        if self.longitude is None:
            missing.append("longitude")

        if missing:
            raise ValueError(f"Incomplete birth parameters. Missing: {', '.join(missing)} or provide saved_horoscope_id.")

        # Astronomical year validation
        if self.birth_date.year < 1800 or self.birth_date.year > 2100:
            raise ValueError(f"Birth year {self.birth_date.year} out of supported astronomical ephemeris range (1800-2100).")

        return self


# Backwards compatibility alias
MarriagePartyInput = MarriagePartnerInput


class MarriageCompatibilityRequest(BaseModel):
    """Request payload for dual-horoscope marriage compatibility calculation."""
    groom: MarriagePartnerInput = Field(..., description="Groom's birth particulars or saved horoscope ID")
    bride: MarriagePartnerInput = Field(..., description="Bride's birth particulars or saved horoscope ID")
    rule_system: str = Field("all", description="Evaluation mode: 'all', 'tamil_porutham', 'ashtakoota', 'vedic_kp'")
    ayanamsa_id: int = Field(0, description="Ayanamsa ID (0=Lahiri Chitrapaksha standard, 1=KP Krishnamurti)")
    house_system_id: int = Field(0, description="House System ID (0=WholeSign, 2=Placidus)")
    include_timing: bool = Field(True, description="Evaluate Dasa-Bhukti matrimonial timing windows")
    include_kp: bool = Field(True, description="Evaluate KP 7th Cuspal Sub-Lord and significators")


class PersonProfileSummary(BaseModel):
    """Astronomical and astrological profile summary for one partner."""
    name: str
    gender: str
    birth_date: str
    birth_time: str
    timezone: str
    latitude: float
    longitude: float
    ascendant_sign: str
    ascendant_sign_tamil: str
    ascendant_degree: float
    ascendant_nakshatra: str
    ascendant_pada: int
    ascendant_navamsa_sign: str
    moon_sign: str
    moon_sign_tamil: str
    moon_degree: float
    moon_nakshatra: str
    moon_nakshatra_tamil: str
    moon_pada: int
    moon_navamsa_sign: str
    venus_sign: str
    mars_sign: str
    jupiter_sign: str


class PoruthamDetailItem(BaseModel):
    """Result for an individual Tamil Porutham (e.g. Dina, Gana, Rajju, Vedha)."""
    rule_id: str
    name_en: str
    name_ta: str
    status: str
    grade: str = Field(..., description="'Uthama', 'Madhyama', 'Adhama', or 'Varjya'")
    score: float = Field(..., description="Earned score: 1.0 (Full), 0.5 (Partial), or 0.0 (None)")
    max_score: float = Field(1.0, description="Maximum possible score for this Porutham")
    is_favorable: bool
    groom_input: Optional[Dict[str, Any]] = None
    bride_input: Optional[Dict[str, Any]] = None
    intermediate_calculation: Optional[Dict[str, Any]] = None
    counting_direction: Optional[str] = None
    applied_acceptance_criteria: Optional[str] = None
    source_and_version: Optional[str] = None
    description: str
    description_tamil: str
    classical_reference: str
    warnings: List[str] = Field(default_factory=list)


class TamilPoruthamSummary(BaseModel):
    """Summary of the traditional Tamil 10 Porutham evaluation."""
    poruthams: Dict[str, PoruthamDetailItem]
    total_score: float = Field(..., description="Aggregate score out of 10 (e.g. 7.5)")
    max_score: float = Field(10.0, description="Maximum possible score (10.0)")
    aggregate_verdict: str = Field(..., description="'Uthama' (>=7), 'Madhyama' (5-6.5), or 'Adhama' (<5)")
    rajju_status: str = Field(..., description="'PASS' (Different Rajju) or 'FAIL' (Same Rajju - Rajju Thatu)")
    vedha_status: str = Field(..., description="'PASS' (No Vedha) or 'FAIL' (Mutual Vedha detected)")
    summary_notes: List[str] = Field(default_factory=list)


class KootaDetailItem(BaseModel):
    """Result for an individual North Indian Ashtakoota factor."""
    koota_id: str
    name_en: str
    status: str = Field("PASS", description="'PASS', 'FAIL', 'INDETERMINATE', or 'UNSUPPORTED'")
    max_points: float
    earned_points: float
    raw_calculation: str
    groom_input: Optional[Dict[str, Any]] = None
    bride_input: Optional[Dict[str, Any]] = None
    intermediate_calculation: Optional[Dict[str, Any]] = None
    is_dosha_present: bool = False
    is_cancelled: bool = False
    cancellation_reason: Optional[str] = None
    description: str
    classical_reference: str
    warnings: List[str] = Field(default_factory=list)


class AshtakootaSummary(BaseModel):
    """Summary of the North Indian 36-point Ashtakoota matching."""
    kootas: Dict[str, KootaDetailItem]
    total_points: float = Field(..., description="Total points scored out of 36.0")
    max_points: float = Field(36.0, description="Maximum possible points (36.0)")
    minimum_threshold: float = Field(18.0, description="Classical minimum passing threshold (18.0)")
    is_threshold_met: bool = Field(..., description="True if total_points >= 18.0")
    nadi_dosha_present: bool = False
    nadi_dosha_cancelled: bool = False
    bhakoot_dosha_present: bool = False
    bhakoot_dosha_cancelled: bool = False
    summary_notes: List[str] = Field(default_factory=list)


class DoshaExceptionItem(BaseModel):
    """Detailed exception and cancellation trace for a detected dosha."""
    dosha_id: str
    name_en: str
    status: str = Field(..., description="RuleEvaluationStatus enum string")
    trigger_placement: str
    cancellation_checked: List[str] = Field(default_factory=list)
    cancellation_applied: List[str] = Field(default_factory=list)
    explanation: str


class PapasamyaDetail(BaseModel):
    """South Indian Papasamya point allocations across reference frames."""
    subject_role: Optional[str] = None
    lagna_papam: float
    moon_papam: float
    venus_papam: float
    total_papam: float
    breakdown_by_planet: Dict[str, float]
    placements_detail: List[Dict[str, Any]] = Field(default_factory=list)
    explanation_en: Optional[str] = None
    explanation_ta: Optional[str] = None


class DoshaAnalysisSummary(BaseModel):
    """Comparative and mutual Dosha evaluation across both horoscopes."""
    groom_kuja: KujaDoshaResult
    bride_kuja: KujaDoshaResult
    mutual_kuja_balance: str = Field(..., description="'BALANCED', 'GROOM_EXCESS', 'BRIDE_EXCESS', or 'NEITHER_AFFLICTED'")
    samadosham_status: Optional[str] = Field(None, description="SamadoshamOutcome enum string")
    samadosham_explanation_en: Optional[str] = None
    samadosham_explanation_ta: Optional[str] = None
    groom_papasamya: PapasamyaDetail
    bride_papasamya: PapasamyaDetail
    papasamya_verdict: str = Field(..., description="'FAVORABLE', 'TOLERABLE', or 'UNFAVORABLE'")
    papasamya_diff_percent: Optional[float] = None
    papasamya_explanation_en: Optional[str] = None
    papasamya_explanation_ta: Optional[str] = None
    active_doshas_with_exceptions: List[DoshaExceptionItem] = Field(default_factory=list)
    partner_dependent_doshas: Dict[str, Any] = Field(default_factory=dict)
    independent_vetoes_preserved: List[str] = Field(default_factory=list)


class VedicHouseAnalysis(BaseModel):
    """Detailed Vedic analysis of an individual marriage-related house (2, 4, 5, 7, 8, 12)."""
    house_number: int
    house_name_en: str
    house_name_ta: str
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    cusp_degree: float
    lord_name: str
    lord_house: int
    lord_sign_index: int
    lord_sign_name: str
    lord_dignity: str
    occupants: List[str] = Field(default_factory=list)
    aspecting_planets: List[str] = Field(default_factory=list)
    supporting_influences: List[str] = Field(default_factory=list)
    conflicting_influences: List[str] = Field(default_factory=list)
    status: str = "PASS"
    summary_en: str = ""
    summary_ta: str = ""


class VedicSignificatorAnalysis(BaseModel):
    """Detailed Vedic analysis of an individual marriage significator (Karaka)."""
    planet_name: str
    sign_index: int
    sign_name: str
    house: int
    longitude: float
    natural_nature: str
    functional_nature: str
    dignity: str
    is_retrograde: bool
    is_combust: bool
    d9_sign_index: int
    d9_sign_name: str
    is_vargottama: bool
    is_pushkara_navamsa: bool
    conjunctions: List[str] = Field(default_factory=list)
    aspects_received: List[str] = Field(default_factory=list)
    shadbala_ratio: Optional[float] = None
    shadbala_strength: Optional[str] = None
    summary_en: str = ""
    summary_ta: str = ""


class NavamsaCrossAnalysis(BaseModel):
    """Detailed D1 and D9 Navamsa cross-validation analysis."""
    d9_lagna_sign_index: int
    d9_lagna_sign_name: str
    d9_lagna_lord: str
    d9_7th_sign_index: int
    d9_7th_sign_name: str
    d9_7th_lord: str
    d1_7th_lord_in_d9_sign: str
    d1_7th_lord_in_d9_house: int
    d1_7th_lord_in_d9_dignity: str
    d9_7th_lord_in_d1_sign: str
    d9_7th_lord_in_d1_house: int
    d9_7th_lord_in_d1_dignity: str
    venus_in_d9_sign: str
    venus_in_d9_house: int
    venus_in_d9_dignity: str
    jupiter_in_d9_sign: str
    jupiter_in_d9_house: int
    jupiter_in_d9_dignity: str
    navamsa_boundary_risk: bool
    boundary_distance_arcmin: float
    vargottama_planets: List[str] = Field(default_factory=list)
    pushkara_navamsa_planets: List[str] = Field(default_factory=list)
    synthesis_notes: List[str] = Field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""


class IndividualKujaAssessmentItem(BaseModel):
    """Explanation-ready individual Kuja / Manglik Dosha evaluation for one partner."""
    subject_role: str
    is_present: bool
    is_cancelled: bool
    severity: str
    house_convention: str
    mars_longitude: float
    mars_sign_index: int
    mars_sign_name: str
    mars_degree_in_sign: float
    mars_house_from_lagna: int
    mars_house_from_moon: int
    mars_house_from_venus: int
    effective_intensity_percent: float
    references_evaluated: Dict[str, Any] = Field(default_factory=dict)
    triggering_conditions: List[str] = Field(default_factory=list)
    cancellations_checked: List[str] = Field(default_factory=list)
    cancellations_applied: List[str] = Field(default_factory=list)
    source_and_version: str = "BPHS Ch. 81, Muhurta Chintamani, Brihat Samhita (v1.0)"
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = Field(default_factory=list)


class IndividualVedicAnalysisItem(BaseModel):
    """Complete individual Vedic marriage analysis for one individual (Groom or Bride)."""
    subject_role: str
    person_name: str
    gender: str
    lagna_sign_index: int
    lagna_sign_name: str
    lagna_sign_name_tamil: str
    lagna_degree: float
    lagna_lord: str
    lagna_lord_house: int
    lagna_lord_dignity: str
    houses_analysis: Dict[int, Any] = Field(default_factory=dict)
    significators: Dict[str, Any] = Field(default_factory=dict)
    navamsa_cross_analysis: Optional[NavamsaCrossAnalysis] = None
    kuja_dosha: Optional[IndividualKujaAssessmentItem] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    supporting_indicators: List[str] = Field(default_factory=list)
    conflicting_indicators: List[str] = Field(default_factory=list)
    uncertainty_warnings: List[str] = Field(default_factory=list)
    rule_sources: List[str] = Field(default_factory=list)
    summary_en: str = ""
    summary_ta: str = ""


class VedicMarriageSummary(BaseModel):
    """Vedic 7th house, marriage lords, significator, and D9 Navamsa findings."""
    groom_7th_lord: str
    groom_7th_house_sign: str
    bride_7th_lord: str
    bride_7th_house_sign: str
    d9_cross_check_summary: str
    venus_jupiter_resonance: str
    key_observations: List[str] = Field(default_factory=list)
    groom_details: Optional[IndividualVedicAnalysisItem] = None
    bride_details: Optional[IndividualVedicAnalysisItem] = None


class KpMarriageSummary(BaseModel):
    """KP 7th Cuspal Sub-Lord and significators alignment."""
    groom_7th_csl_planet: str
    groom_7th_csl_promise: str = Field(..., description="'Positive', 'Negative', or 'Mixed'")
    bride_7th_csl_planet: str
    bride_7th_csl_promise: str = Field(..., description="'Positive', 'Negative', or 'Mixed'")
    significators_agreement: str
    supporting_houses_active: List[int] = Field(default_factory=list)
    denying_houses_active: List[int] = Field(default_factory=list)


class TimingAnalysisSummary(BaseModel):
    """Dasa-Bhukti marriage period synchronization."""
    groom_active_dasa_bhukti: str
    bride_active_dasa_bhukti: str
    matrimonial_window_assessment: str


# ---------------------------------------------------------------------------
# Phase 8 & 9: Composite Assessment Models & Errors
# ---------------------------------------------------------------------------

class CategoryVerdictModel(BaseModel):
    """Evaluated verdict for one independent astrological lens or tradition."""
    category_id: str
    category_name_en: str
    category_name_ta: str
    status: str = Field(..., description="'FAVORABLE', 'MIXED', 'UNFAVORABLE', or 'INDETERMINATE'")
    tradition: str
    score_summary: str = ""
    key_factors: List[str] = Field(default_factory=list)
    vetoes_applied: List[str] = Field(default_factory=list)


class ConflictFindingModel(BaseModel):
    """Documented divergence or conflict between traditions, lenses, or chart factors."""
    conflict_type: str
    title_en: str
    title_ta: str
    finding_a: str
    finding_b: str
    resolution_principle: str
    explanation_en: str
    explanation_ta: str
    rule_sources: List[str] = Field(default_factory=list)


class CompositeAssessmentSummary(BaseModel):
    """Deterministic, explainable single final compatibility assessment per RULE_SOURCE_REGISTER.md Section 8."""
    overall_outcome: str = Field(..., description="CompatibilityOutcome enum string: FAVOURABLE_UNDER_SELECTED_RULES, MIXED_OR_CONDITIONAL, UNFAVOURABLE_UNDER_SELECTED_RULES, INDETERMINATE")
    overall_outcome_label_en: str
    overall_outcome_label_ta: str
    category_verdicts: Dict[str, CategoryVerdictModel] = Field(default_factory=dict)
    major_supportive_indicators: List[str] = Field(default_factory=list)
    major_challenging_indicators: List[str] = Field(default_factory=list)
    conflicting_findings: List[ConflictFindingModel] = Field(default_factory=list)
    missing_or_uncertain_evidence: List[str] = Field(default_factory=list)
    recommended_astrologer_review: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)
    rule_sources: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""


class FinalAssessmentSummary(BaseModel):
    """Deterministic, explainable single final compatibility assessment (legacy/compat format)."""
    verdict: str = Field(..., description="CompatibilityOutcome enum string")
    verdict_label_en: str
    verdict_label_ta: str
    primary_strengths: List[str] = Field(default_factory=list)
    primary_concerns: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    scientific_disclaimer: str
    reproducibility_fingerprint: str


class MarriageCompatibilityError(BaseModel):
    """Structured error model for validation and calculation failures."""
    error: str = Field(..., description="Error classification")
    detail: str = Field(..., description="Detailed description of the error")
    code: str = Field("BAD_REQUEST", description="Error code identifier")
    missing_fields: Optional[List[str]] = Field(None, description="Optional list of missing parameters")


class MarriageCompatibilityResponse(BaseModel):
    """Complete root response payload for marriage compatibility calculation."""
    metadata: CalculationMetadata
    groom_profile: PersonProfileSummary
    bride_profile: PersonProfileSummary
    composite_assessment: CompositeAssessmentSummary
    tamil_porutham: Optional[TamilPoruthamSummary] = None
    ashtakoota: Optional[AshtakootaSummary] = None
    dosha_analysis: Optional[Union[DoshaAnalysisSummary, Dict[str, Any]]] = None
    synastry: Optional[Dict[str, Any]] = None
    kp_marriage: Optional[Union[KpMarriageSummary, Dict[str, Any]]] = None
    vedic_marriage: Optional[VedicMarriageSummary] = None
    timing_analysis: Optional[TimingAnalysisSummary] = None
    groom_vedic: Optional[Union[IndividualVedicAnalysisItem, Dict[str, Any]]] = None
    bride_vedic: Optional[Union[IndividualVedicAnalysisItem, Dict[str, Any]]] = None
    final_assessment: FinalAssessmentSummary


class RuleRegisterItem(BaseModel):
    """Metadata describing an approved astrological rule in the engine."""
    rule_id: str
    name: str
    tradition: str
    classical_source: str
    approval_status: str
    description: str


class RuleRegisterResponse(BaseModel):
    """Response payload for GET /api/v1/marriage-compatibility/rules."""
    engine_name: str
    ruleset_version: str
    rules: List[RuleRegisterItem]


# ---------------------------------------------------------------------------
# Phase 11C: Saved Marriage Compatibility Report Persistence Models
# ---------------------------------------------------------------------------

class SaveMarriageCompatibilityReportRequest(BaseModel):
    """Request payload to persist a completed marriage compatibility calculation snapshot."""
    title: str = Field(..., min_length=1, max_length=200, description="Title of the saved compatibility report")
    groom_name: str = Field(..., min_length=1, max_length=100, description="Groom's name")
    bride_name: str = Field(..., min_length=1, max_length=100, description="Bride's name")
    groom_birth_date: Union[date, str] = Field(..., description="Groom birth date YYYY-MM-DD")
    bride_birth_date: Union[date, str] = Field(..., description="Bride birth date YYYY-MM-DD")
    groom_is_approximate: bool = Field(False, description="Flag indicating if groom birth time is approximate")
    bride_is_approximate: bool = Field(False, description="Flag indicating if bride birth time is approximate")
    groom_saved_horoscope_id: Optional[str] = Field(None, description="UUID of groom's saved horoscope in Supabase")
    bride_saved_horoscope_id: Optional[str] = Field(None, description="UUID of bride's saved horoscope in Supabase")
    rule_system: str = Field("all", description="Evaluation mode used for calculation")
    ayanamsa_id: int = Field(0, description="Ayanamsa ID used")
    house_system_id: int = Field(0, description="House system ID used")
    include_kp: bool = Field(True, description="Whether KP was evaluated")
    include_timing: bool = Field(True, description="Whether timing was evaluated")
    overall_outcome: str = Field(..., description="Overall outcome enum string")
    porutham_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Tamil Porutham score (0.0 to 10.0)")
    ashtakoota_points: Optional[float] = Field(None, ge=0.0, le=36.0, description="Ashtakoota points (0.0 to 36.0)")
    samadosham_status: Optional[str] = Field(None, description="Samadosham outcome string")
    papasamya_verdict: Optional[str] = Field(None, description="Papasamya balance verdict")
    ruling_planets_agreement: Optional[str] = Field(None, description="KP ruling planets agreement")
    report_data: Dict[str, Any] = Field(..., description="Complete calculation result snapshot JSON")
    engine_version: str = Field("1.0.0", description="Engine version used")
    report_schema_version: str = Field("1.0.0", description="Schema version of saved report")

    @field_validator("title", "groom_name", "bride_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace only.")
        return cleaned

    @field_validator("groom_saved_horoscope_id", "bride_saved_horoscope_id")
    @classmethod
    def validate_horoscope_uuid(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = v.strip()
        try:
            uuid.UUID(clean)
            return clean
        except Exception:
            raise ValueError(f"Invalid horoscope UUID format: '{v}'")

    @field_validator("overall_outcome")
    @classmethod
    def validate_outcome(cls, v: str) -> str:
        valid_outcomes = {
            "FAVOURABLE_UNDER_SELECTED_RULES",
            "MIXED_OR_CONDITIONAL",
            "UNFAVOURABLE_UNDER_SELECTED_RULES",
            "INDETERMINATE",
        }
        clean = v.strip()
        if clean not in valid_outcomes:
            raise ValueError(f"Invalid overall_outcome '{v}'. Must be one of: {sorted(valid_outcomes)}")
        return clean


class UpdateMarriageReportMetadataRequest(BaseModel):
    """Request payload to update mutable metadata for a saved marriage compatibility report.
    Only title, groom_name, bride_name, groom_saved_horoscope_id, and bride_saved_horoscope_id can be updated.
    All calculation data, parameters, scores, and snapshots are strictly immutable.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated report title")
    groom_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated groom name")
    bride_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated bride name")
    groom_saved_horoscope_id: Optional[str] = Field(None, description="Updated or cleared groom saved horoscope UUID")
    bride_saved_horoscope_id: Optional[str] = Field(None, description="Updated or cleared bride saved horoscope UUID")

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "groom_name", "bride_name")
    @classmethod
    def validate_non_empty_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace only.")
        return cleaned

    @field_validator("groom_saved_horoscope_id", "bride_saved_horoscope_id")
    @classmethod
    def validate_horoscope_uuid_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        clean = v.strip()
        try:
            uuid.UUID(clean)
            return clean
        except Exception:
            raise ValueError(f"Invalid horoscope UUID format: '{v}'")


class SavedMarriageReportSummaryResponse(BaseModel):
    """Summary of a saved marriage compatibility report for listings."""
    id: str
    user_id: str
    display_number: int
    title: str
    groom_name: str
    bride_name: str
    groom_birth_date: str
    bride_birth_date: str
    groom_is_approximate: bool
    bride_is_approximate: bool
    groom_saved_horoscope_id: Optional[str] = None
    bride_saved_horoscope_id: Optional[str] = None
    rule_system: str
    ayanamsa_id: int
    house_system_id: int
    include_kp: bool
    include_timing: bool
    overall_outcome: str
    porutham_score: Optional[float] = None
    ashtakoota_points: Optional[float] = None
    samadosham_status: Optional[str] = None
    papasamya_verdict: Optional[str] = None
    ruling_planets_agreement: Optional[str] = None
    engine_version: str
    report_schema_version: str
    created_at: str
    updated_at: str


class SavedMarriageReportDetailResponse(SavedMarriageReportSummaryResponse):
    """Detailed response for a single saved report, including full calculation snapshot."""
    report_data: Dict[str, Any]


class SavedMarriageReportListResponse(BaseModel):
    """Response payload for listing saved marriage compatibility reports."""
    reports: List[SavedMarriageReportSummaryResponse]
    total_count: int
    limit: int
    offset: int
