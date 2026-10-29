"""Pydantic schemas for Remedies & Pariharam knowledge base and services."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceReferenceResponse(BaseModel):
    """Canonical classical source reference citation."""
    id: Optional[str] = None
    code: str = Field(..., description="Short canonical identifier, e.g. 'BPHS'")
    title_en: str = Field(..., description="English title")
    title_sa: Optional[str] = Field(None, description="Sanskrit title")
    author: Optional[str] = Field(None, description="Traditional author / sage")
    tradition: str = Field(..., description="Tradition: vedic, puranic, tantric, classical_jyotish, etc.")
    canonical_status: str = Field(..., description="primary_shastra, purana, stotra_samhita, regional_tradition")
    description: Optional[str] = None
    is_published: bool = True


class ProblemTaxonomyItem(BaseModel):
    """Categorized life problem for remedy mapping."""
    id: Optional[str] = None
    slug: str = Field(..., description="Stable slug identifier, e.g. 'career_delay'")
    category: str = Field(..., description="Category: career, relationships_marriage, health_wellness, etc.")
    name_en: str = Field(..., description="English title")
    name_ta: str = Field(..., description="Tamil title")
    description_en: Optional[str] = None
    description_ta: Optional[str] = None
    primary_karakas: List[str] = Field(default_factory=list, description="Primary natural planetary significators")
    governing_houses: List[int] = Field(default_factory=list, description="Governing Bhavas (1-12)")
    display_order: int = 0
    is_published: bool = True
    verification_status: str = "verified"


class ProblemTaxonomyListResponse(BaseModel):
    """Response containing list of verified problem taxonomy items."""
    total_count: int
    categories: List[str]
    items: List[ProblemTaxonomyItem]


class RemedyItem(BaseModel):
    """Remedy item in the catalog."""
    id: Optional[str] = None
    code: str = Field(..., description="Unique remedy code, e.g. 'REM_SUN_MANTRA_01'")
    graha: str = Field(..., description="Planetary association: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu, universal")
    remedy_type: str = Field(..., description="Type: mantra, worship, charity, fasting, temple")
    name_en: str
    name_ta: str
    description_en: str
    description_ta: str
    deity_en: str
    deity_ta: str
    sanskrit_text: Optional[str] = Field(None, description="Authentic Devanagari Sanskrit text")
    transliteration_iast: Optional[str] = Field(None, description="IAST standard transliteration")
    transliteration_ta: Optional[str] = Field(None, description="Tamil script phonetic transliteration")
    meaning_en: Optional[str] = None
    meaning_ta: Optional[str] = None
    procedure_en: str
    procedure_ta: str
    japa_count: Optional[int] = Field(108, description="Prescribed recitation count")
    timing_recommendation_en: Optional[str] = None
    timing_recommendation_ta: Optional[str] = None
    source_reference_id: Optional[str] = None
    source_code: Optional[str] = None
    source_verse_or_page: Optional[str] = None
    is_pacification_only: bool = Field(False, description="True if only for pacifying afflicted malefics (e.g. Daan)")
    problem_slugs: List[str] = Field(default_factory=list, description="Associated problem categories")
    is_published: bool = True
    verification_status: str = "verified"


class RemedyListResponse(BaseModel):
    """Paginated or filtered remedy list response."""
    total_count: int
    items: List[RemedyItem]


class NavagrahaTempleItem(BaseModel):
    """Authentic Kaveri Delta Navagraha Temple record."""
    id: Optional[str] = None
    code: str = Field(..., description="Temple code, e.g. 'TEMPLE_SURYANAR_KOVIL'")
    graha: str = Field(..., description="Navagraha planet: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu")
    name_en: str
    name_ta: str
    presiding_deity_en: str
    presiding_deity_ta: str
    graha_deity_en: str
    graha_deity_ta: str
    place_name_en: str
    place_name_ta: str
    district_en: str
    district_ta: str
    state: str = "Tamil Nadu"
    latitude: float
    longitude: float
    visiting_day_en: str
    visiting_day_ta: str
    significance_en: str
    significance_ta: str
    remedy_offerings_en: str
    remedy_offerings_ta: str
    source_tradition: str = "Kaveri Delta Navagraha Sthalam"
    is_published: bool = True
    verification_status: str = "verified"


class NavagrahaTempleListResponse(BaseModel):
    """Response containing Tamil Navagraha temples."""
    total_count: int
    items: List[NavagrahaTempleItem]


class ContentValidationCheck(BaseModel):
    """Status of an individual content validation check."""
    check_name: str
    is_valid: bool
    details: str


class ContentValidationReport(BaseModel):
    """Report detailing bilingual, mantra, and Unicode fidelity."""
    total_remedies_audited: int
    total_problems_audited: int
    total_temples_audited: int
    checks: List[ContentValidationCheck]
    all_passed: bool


class RemedyEligibilityRequest(BaseModel):
    """Request to test remedy suitability safeguards against chart rules."""
    ascendant_sign: str = Field(..., description="Ascendant sign name, e.g. 'Taurus'")
    graha: str = Field(..., description="Planet to evaluate, e.g. 'saturn'")
    remedy_type: str = Field(..., description="Type of remedy, e.g. 'charity' or 'mantra'")


class RemedyEligibilityResponse(BaseModel):
    """Eligibility determination with Vedic safeguards (e.g. Yogakaraka protection)."""
    graha: str
    ascendant_sign: str
    remedy_type: str
    is_eligible: bool
    is_yogakaraka: bool
    is_functional_benefic: bool
    is_functional_malefic: bool
    restriction_reason: Optional[str] = None
    safe_alternative_recommendation: Optional[str] = None
    requires_manual_astrologer_review: bool = False
    is_review_gated: bool = False


class NeechaBhangaAssessment(BaseModel):
    """Detailed classical evaluation of planetary debilitation and cancellation factors."""
    graha: str = Field(..., description="Affected planet: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu")
    d1_sign: str = Field(..., description="D1 Rasi sign where planet is placed")
    d1_house: Optional[int] = Field(None, description="House bhava (1-12) from Lagna")
    is_d1_debilitated: bool = Field(True, description="True if planet is in its classical debilitation sign in D1")

    # D9 Navamsa dignity factors
    d9_data_status: str = Field("verified", description="'verified', 'unavailable', 'insufficient_data'")
    d9_sign: Optional[str] = Field(None, description="D9 Navamsa sign where planet is placed")
    d9_house: Optional[int] = Field(None, description="House in D9 relative to D9 Lagna")
    is_d9_exalted: bool = Field(False, description="True if planet is in its classical exaltation sign in D9 Navamsa")
    is_d9_own_sign: bool = Field(False, description="True if planet is in its own ruled sign in D9 Navamsa")
    is_vargottama: bool = Field(False, description="True if planet occupies identical sign in D1 and D9")

    # Cancellation & Yoga status
    cancellation_status: str = Field(
        ...,
        description="'none', 'cancellation_indicator_present', 'complete_nbry_qualifying', 'nbry_neutralized_by_combustion', 'insufficient_data'"
    )
    has_cancellation_indicator: bool = Field(False, description="True if at least one validated classical cancellation factor is present")
    is_complete_nbry: bool = Field(False, description="True if full Neecha Bhanga Raja Yoga qualifies per classical rules")
    is_combust: bool = Field(False, description="True if solar combustion neutralizes Raja Yoga potency per Phaladeepika Ch. 6")

    # Classical citations & criteria
    qualifying_criteria: List[str] = Field(default_factory=list, description="List of validated classical cancellation rules met")
    rule_identifiers: List[str] = Field(default_factory=list, description="Canonical scripture citations")

    # Explanation & evidence
    severity: str = Field("moderate", description="'mild', 'moderate', 'high'")
    reason_en: str = Field(..., description="Detailed English explanation with classical justification")
    reason_ta: str = Field(..., description="Detailed Tamil explanation with classical justification")
    supporting_placements: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic placement details (dispositor, exaltation lord, kendras)")
    confidence_status: str = Field("high", description="'high', 'medium', 'conditional', 'unresolved'")
    unresolved_interpretation: Optional[str] = Field(None, description="Traditional interpretive disputes or nuances if any")


class ChartFactorExplanation(BaseModel):
    """Specific diagnosed astrological condition with classical shastra citations."""
    factor_type: str = Field(..., description="Condition type: debilitation, combustion, dusthana, kuja_dosha, running_dasa, nodal_axis, etc.")
    graha: str = Field(..., description="Affected planet: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu")
    house: Optional[int] = Field(None, description="House bhava (1-12) if applicable")
    title_en: str
    title_ta: str
    description_en: str
    description_ta: str
    rule_reference: str = Field(..., description="Classical rule citation (e.g. 'BPHS Ch. 34', 'Phaladeepika Ch. 20')")
    is_confirmed: bool = Field(True, description="True if confirmed by chart mathematics; False if interpretive suggestion")
    severity: str = Field("moderate", description="mild, moderate, high")
    neecha_bhanga: Optional[NeechaBhangaAssessment] = Field(None, description="Detailed D9-aware Neecha Bhanga evaluation if factor is debilitation")


class RecommendedRemedy(BaseModel):
    """Ranked personalized remedy recommendation linked to diagnosed factors."""
    remedy: RemedyItem
    relevance_score: int = Field(..., ge=0, le=100, description="Deterministic ranking score (0-100)")
    priority_tier: str = Field("recommended", description="essential, recommended, optional")
    reason_en: str
    reason_ta: str
    matching_factors: List[str] = Field(default_factory=list)
    yogakaraka_warning: Optional[str] = None
    temple: Optional[NavagrahaTempleItem] = None


class ChartContextSummary(BaseModel):
    """Extracted natal context from calculation output."""
    lagna_sign: str
    lagna_lord: Optional[str] = None
    moon_sign: str
    moon_nakshatra: str
    sun_sign: str
    running_mahadasha: Optional[str] = None
    running_bhukti: Optional[str] = None
    yogakaraka_planets: List[str] = Field(default_factory=list)
    functional_benefics: List[str] = Field(default_factory=list)
    functional_malefics: List[str] = Field(default_factory=list)
    combust_planets: List[str] = Field(default_factory=list)
    debilitated_planets: List[str] = Field(default_factory=list)
    exalted_planets: List[str] = Field(default_factory=list)
    dusthana_planets: Dict[str, List[str]] = Field(default_factory=dict, description="Planets in 6th, 8th, 12th houses")
    kuja_dosha_status: str = Field("none", description="none, present, cancelled")
    kuja_dosha_details: Optional[str] = None
    d9_data_status: str = Field("verified", description="'verified', 'unavailable', 'insufficient_data'")
    d9_planetary_signs: Dict[str, str] = Field(default_factory=dict, description="Planet -> D9 Navamsa sign name")
    vargottama_planets: List[str] = Field(default_factory=list, description="List of Vargottama planets")
    neecha_bhanga_assessments: List[NeechaBhangaAssessment] = Field(default_factory=list, description="Detailed Neecha Bhanga assessments for debilitated planets")


class RemedyAnalysisResponse(BaseModel):
    """Complete personalized remedy analysis for a birth chart."""
    horoscope_id: Optional[str] = None
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    calculation_timestamp: str
    chart_context: ChartContextSummary
    diagnosed_factors: List[ChartFactorExplanation] = Field(default_factory=list)
    recommendations: List[RecommendedRemedy] = Field(default_factory=list)
    total_recommendations: int = 0
    is_stale: bool = False
    input_fingerprint: str
    status: str = "complete" # "complete", "insufficient_data"
    sannu_rituals_diagnostic: Optional[Dict[str, Any]] = Field(None, description="Sannu Ahmed Vedic Rituals & Karma Diagnostic (Nakshatra rituals, doshas, 3-fold karma, propitiation vs empowerment)")


class LiveRemedyAnalysisRequest(BaseModel):
    """Request payload for running live remedy analysis on active birth inputs or chart dict."""
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ayanamsa: Optional[int] = 0
    chart_snapshot: Optional[Dict[str, Any]] = None


class SaveRemedyReportRequest(BaseModel):
    """Request payload to save an astrologer-reviewed remedy report."""
    horoscope_id: str
    input_data_fingerprint: str
    person_name: Optional[str] = None
    review_status: str = Field("draft", description="'draft', 'reviewed', 'approved'")
    astrologer_notes: Optional[str] = None
    selected_remedy_codes: List[str] = Field(default_factory=list)
    language: str = Field("en", description="'en' or 'ta'")
    analysis_snapshot: RemedyAnalysisResponse


class SavedRemedyReportResponse(BaseModel):
    """Saved remedy report record from Supabase."""
    id: str
    horoscope_id: str
    user_id: str
    person_name: Optional[str] = None
    input_data_fingerprint: str
    review_status: str
    astrologer_notes: Optional[str] = None
    selected_remedy_codes: List[str] = Field(default_factory=list)
    language: str
    analysis_snapshot: RemedyAnalysisResponse
    created_at: str
    updated_at: str


class SavedRemedyReportsListResponse(BaseModel):
    """List response of saved remedy reports."""
    total_count: int
    reports: List[SavedRemedyReportResponse]


# ==============================================================================
# Kaveri Delta Navagraha Pilgrimage Circuit Schemas
# ==============================================================================

class PilgrimageTempleStop(BaseModel):
    """An individual temple stop along a Navagraha pilgrimage circuit."""
    order_in_day: int
    code: str
    graha: str
    graha_name_en: str
    graha_name_ta: str
    name_en: str
    name_ta: str
    presiding_deity_en: str
    presiding_deity_ta: str
    place_name_en: str
    place_name_ta: str
    district_en: str
    district_ta: str
    latitude: float
    longitude: float
    visiting_time_window_en: str
    visiting_time_window_ta: str
    darshan_timings_en: str
    darshan_timings_ta: str
    special_ritual_en: str
    special_ritual_ta: str
    remedy_offerings_en: str
    remedy_offerings_ta: str
    distance_from_previous_km: float = 0.0
    driving_minutes_from_previous: int = 0
    is_chart_priority: bool = False
    priority_level: Optional[str] = None  # "high", "essential", "moderate"
    chart_priority_reason_en: Optional[str] = None
    chart_priority_reason_ta: Optional[str] = None


class PilgrimageDayPlan(BaseModel):
    """Day itinerary in a multi-day or single-day pilgrimage."""
    day_number: int
    title_en: str
    title_ta: str
    base_camp_en: str
    base_camp_ta: str
    recommended_start_time: str
    total_distance_km: float
    estimated_travel_time_hours: float
    temple_stops: List[PilgrimageTempleStop]
    practical_tips_en: List[str] = Field(default_factory=list)
    practical_tips_ta: List[str] = Field(default_factory=list)


class PilgrimageCircuitResponse(BaseModel):
    """Complete Navagraha Pilgrimage Circuit Itinerary."""
    circuit_id: str
    title_en: str
    title_ta: str
    summary_en: str
    summary_ta: str
    base_hub_en: str = "Kumbakonam"
    base_hub_ta: str = "கும்பகோணம்"
    total_temples: int = 9
    total_distance_km: float
    day_plans: List[PilgrimageDayPlan]
    chart_priorities_present: bool = False
    rahu_kalam_guidelines_en: str
    rahu_kalam_guidelines_ta: str
    dress_code_and_customs_en: str
    dress_code_and_customs_ta: str


class PersonalizedPilgrimageRequest(BaseModel):
    """Request for generating a chart-aware Navagraha pilgrimage circuit."""
    horoscope_id: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ayanamsa: Optional[int] = 0
    chart_snapshot: Optional[Dict[str, Any]] = None
    circuit_type: str = Field("2_day", description="'1_day_express', '2_day_comprehensive', 'chart_priority_only'")


# ==============================================================================
# Astrological Gemstone (Ratna) & Rudraksha Advisory Schemas
# ==============================================================================

class RudrakshaItem(BaseModel):
    mukhi: int
    name_en: str
    name_ta: str
    ruling_deity_en: str
    ruling_deity_ta: str
    ruling_graha: str
    ruling_graha_en: str
    ruling_graha_ta: str
    chakra_en: str
    chakra_ta: str
    beeja_mantra_sanskrit: str
    beeja_mantra_en: str
    beeja_mantra_ta: str
    astrological_benefits_en: str
    astrological_benefits_ta: str
    doshas_mitigated_en: List[str]
    doshas_mitigated_ta: List[str]
    who_should_wear_en: str
    who_should_wear_ta: str
    wearing_protocol_en: str
    wearing_protocol_ta: str
    is_pratikula_remedy: bool = True


class RudrakshaRecommendationSummary(BaseModel):
    primary_bead: RudrakshaItem
    secondary_bead: Optional[RudrakshaItem] = None
    universal_bead: RudrakshaItem
    personal_alignment_reason_en: str
    personal_alignment_reason_ta: str
    wearing_instructions_en: List[str] = Field(default_factory=list)
    wearing_instructions_ta: List[str] = Field(default_factory=list)


class GemstoneRecommendation(BaseModel):
    """Classical gemstone prescription for a specific auspicious house ruler."""
    category_code: str  # "life_stone", "lucky_stone", "fortune_stone", "secondary_support"
    category_name_en: str
    category_name_ta: str
    governing_purpose_en: str
    governing_purpose_ta: str
    graha: str
    graha_name_en: str
    graha_name_ta: str
    house_lordships: List[int]
    primary_gem_en: str
    primary_gem_ta: str
    primary_gem_sanskrit: str
    upratna_substitutes_en: List[str]
    upratna_substitutes_ta: List[str]
    prescribed_metal_en: str
    prescribed_metal_ta: str
    ideal_finger_en: str
    ideal_finger_ta: str
    minimum_carats: float
    minimum_rattis: Optional[float] = None
    weight_guideline_formula_en: Optional[str] = None
    weight_guideline_formula_ta: Optional[str] = None
    energization_day_en: str
    energization_day_ta: str
    consecration_mantra_sanskrit: str
    consecration_mantra_ta: str
    gayatri_mantra_sanskrit: Optional[str] = None
    gayatri_mantra_ta: Optional[str] = None
    cleansing_vidhi_en: str
    cleansing_vidhi_ta: str
    safety_status: str  # "auspicious", "caution_required", "prohibited"
    is_eligible: bool
    astrological_justification_en: str
    astrological_justification_ta: str
    incompatible_gems_warning_en: Optional[str] = None
    incompatible_gems_warning_ta: Optional[str] = None


class ProhibitedGemstoneItem(BaseModel):
    """Gemstone strictly prohibited due to Dusthana, Maraka, or functional malefic status."""
    graha: str
    graha_name_en: str
    graha_name_ta: str
    primary_gem_en: str
    primary_gem_ta: str
    reason_en: str
    reason_ta: str
    dusthana_houses_ruled: List[int] = Field(default_factory=list)
    is_functional_malefic: bool = True
    safe_alternative_en: str
    safe_alternative_ta: str


class GemstoneAdvisoryResponse(BaseModel):
    """Complete 3-pillar gemstone prescription and safety audit for a native."""
    lagna_sign: str
    moon_sign: Optional[str] = None
    running_mahadasha: Optional[str] = None
    running_bhukti: Optional[str] = None
    body_weight_kg: Optional[float] = None
    life_stone: GemstoneRecommendation
    lucky_stone: GemstoneRecommendation
    fortune_stone: GemstoneRecommendation
    secondary_support_stone: Optional[GemstoneRecommendation] = None
    prohibited_gemstones: List[ProhibitedGemstoneItem] = Field(default_factory=list)
    anukula_vs_pratikula_doctrine_en: Optional[Dict[str, Any]] = None
    anukula_vs_pratikula_doctrine_ta: Optional[Dict[str, Any]] = None
    karma_doctrine_en: Optional[Dict[str, Any]] = None
    karma_doctrine_ta: Optional[Dict[str, Any]] = None
    grahabalabal_principles_en: Optional[Dict[str, Any]] = None
    grahabalabal_principles_ta: Optional[Dict[str, Any]] = None
    consecration_protocol_en: Optional[Dict[str, Any]] = None
    consecration_protocol_ta: Optional[Dict[str, Any]] = None
    recommended_rudraksha: Optional[RudrakshaRecommendationSummary] = None
    rudraksha_catalog: List[RudrakshaItem] = Field(default_factory=list)
    conflicting_combinations_warning_en: List[str] = Field(default_factory=list)
    conflicting_combinations_warning_ta: List[str] = Field(default_factory=list)
    general_wearing_rules_en: List[str] = Field(default_factory=list)
    general_wearing_rules_ta: List[str] = Field(default_factory=list)
    mandatory_review_notice_en: str
    mandatory_review_notice_ta: str


class GemstoneAdvisoryRequest(BaseModel):
    """Payload to request gemstone prescription and safety audit."""
    ascendant_sign: Optional[str] = None
    horoscope_id: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ayanamsa: Optional[int] = 0
    body_weight_kg: Optional[float] = None
    chart_snapshot: Optional[Dict[str, Any]] = None


class RudrakshaCatalogResponse(BaseModel):
    """Response containing full 1-to-14 Mukhi Rudraksha catalogue."""
    total_beads: int
    items: List[RudrakshaItem]


class RudrakshaRecommendationRequest(BaseModel):
    """Request for personalized Rudraksha recommendations."""
    ascendant_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    running_mahadasha: Optional[str] = None
    running_bhukti: Optional[str] = None
    horoscope_id: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ayanamsa: Optional[int] = 0
    has_kuja_dosha: bool = False
    has_sade_sati: bool = False
    has_kaal_sarp: bool = False
    debilitated_planets: List[str] = Field(default_factory=list)
    combust_planets: List[str] = Field(default_factory=list)


# ─── Sannu Ahmed Rituals & Remedies Schemas ──────────────────────────────────

class NakshatraRitualItem(BaseModel):
    """Sacred geometry, sound, and offering rituals for one of the 27 Nakshatras."""
    number: int
    name: str
    name_ta: str
    ruling_planet: str
    ruling_deity: str
    ruling_deity_ta: str
    karmic_theme: str
    animal_yoni: str
    yoni_instinct: str
    tattva: str
    symbol: str
    esoteric_symbol_meaning: str
    sacred_geometry: str
    sound_mantra: str
    sound_mantra_bija: Optional[str] = None
    sound_mantra_ta: str
    japa_count: int = 108
    offerings_dravya: str
    ritual_procedure: str
    sacred_tree: str


class NakshatraRitualsListResponse(BaseModel):
    """Response containing all 27 Nakshatras sacred rituals."""
    total_nakshatras: int
    items: List[NakshatraRitualItem]


class SannuKnowledgeOverviewResponse(BaseModel):
    """Overview of Sannu Ahmed's Vedic Astrology Rituals & Remedies knowledge base."""
    source: Dict[str, Any]
    karma_architecture: Dict[str, Any]
    soul_body_circuit: Dict[str, Any]
    propitiation_vs_empowerment: Dict[str, Any]
    planetary_weakness_atlas: Dict[str, Any]
    house_weakness_manifestation: Dict[str, Any]
    nakshatra_doshas: Dict[str, Any]
    sacred_timing_rules: Dict[str, Any]


class KarmaRitualsAnalysisRequest(BaseModel):
    """Request payload to diagnose chart karma and rituals using Sannu Ahmed's framework."""
    horoscope_id: Optional[str] = None
    ascendant_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    moon_nakshatra: Optional[str] = None
    running_mahadasha: Optional[str] = None
    running_bhukti: Optional[str] = None
    chart_snapshot: Optional[Dict[str, Any]] = None


class SannuKarmaDiagnosticResponse(BaseModel):
    """Full Sannu Ahmed Karma and Rituals diagnostic response."""
    moon_nakshatra_ritual: Optional[Dict[str, Any]] = None
    detected_nakshatra_doshas: List[Dict[str, Any]] = Field(default_factory=list)
    threefold_karma_blueprint: Dict[str, Any]
    psychological_and_karmic_diagnostics: List[Dict[str, Any]] = Field(default_factory=list)
    propitiation_vs_empowerment_status: List[Dict[str, Any]] = Field(default_factory=list)
    sacred_timing_and_routine: Dict[str, Any]




