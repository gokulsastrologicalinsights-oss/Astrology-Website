"""Pydantic schemas for Medical Astrology analysis and rule registry.

STRICT SAFETY RESTRICTIONS:
This is a classical and KP astrological research engine for educational purposes only.
It NEVER generates medical diagnoses, clinical probabilities, onset predictions,
lifespan/death predictions, or medical treatments.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import CalculationMetadata

SAFETY_DISCLAIMER_EN = (
    "Medical Astrology presents traditional astrological interpretations for educational "
    "and research purposes only. Astrological combinations cannot diagnose, confirm or predict "
    "disease. For health concerns, consult a qualified healthcare professional."
)

SAFETY_DISCLAIMER_TA = (
    "மருத்துவ ஜோதிடம் பாரம்பரிய ஜோதிட விளக்கங்களை கல்வி மற்றும் ஆராய்ச்சி நோக்கங்களுக்காக மட்டுமே "
    "வழங்குகிறது. ஜோதிடக் கிரக அமைப்புகளால் நோயைக் கண்டறியவோ, உறுதிப்படுத்தவோ, எதிர்காலத்தில் ஏற்படும் "
    "எனக் கணிக்கவோ முடியாது. உடல்நலம் குறித்த கவலைகளுக்கு தகுதியான மருத்துவ நிபுணரை அணுகவும்."
)


class MedicalConditionItem(BaseModel):
    condition: str = Field(..., description="Description of the classical or KP condition")
    passed: bool = Field(..., description="Whether this condition is satisfied in the chart")
    detail: str = Field(..., description="Evaluated chart value or explanation")


class MedicalRule(BaseModel):
    id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="English rule name")
    name_tamil: str = Field(..., description="Tamil rule name")
    source: str = Field(..., description="Classical text or documented authority (e.g., BPHS, Phaladeepika, KP Reader)")
    chapter_verse: str = Field(..., description="Chapter, verse or page citation")
    category: str = Field(..., description="Vedic Birth Chart | Vedic House Lord | Vedic Conjunction/Aspect | Vedic Mitigation | KP 6th Cusp Sub-Lord | KP Dasha Signification")
    system: str = Field(..., description="'vedic' or 'kp'")
    required_placements: str = Field(..., description="Required planetary or cuspal placements")
    mandatory_conditions: List[str] = Field(default_factory=list, description="Mandatory conditions that must be fulfilled")
    traditional_interpretation: str = Field(..., description="Documented traditional textual interpretation in English")
    interpretation_tamil: str = Field(..., description="Documented traditional textual interpretation in Tamil")
    anatomical_system: str = Field(..., description="Body system or organ governed according to classical texts")
    modifiers: Optional[str] = Field(None, description="Documented classical modifiers or dignity changes")
    conflicting_indications: Optional[str] = Field(None, description="Opposing or mitigating rules (e.g. Arishta Bhanga)")
    is_active: bool = Field(..., description="Whether rule conditions are fulfilled in the chart")
    status: str = Field(..., description="'Qualifying' | 'Mitigated' | 'Not Qualifying'")
    triggered_positions: List[str] = Field(default_factory=list, description="Exact positions that triggered the rule")
    planets_involved: List[str] = Field(default_factory=list, description="Planets involved in the combination")
    relevant_houses: List[int] = Field(default_factory=list, description="Houses involved in the combination")
    conditions: List[MedicalConditionItem] = Field(default_factory=list, description="Condition verification items")


class HouseHealthAnalysis(BaseModel):
    house_number: int = Field(..., description="House number (1, 6, 8, or 12)")
    sign_index: int = Field(..., description="Zodiac sign index (1-12)")
    sign_name_en: str = Field(..., description="Sign name in English")
    sign_name_ta: str = Field(..., description="Sign name in Tamil")
    lord: str = Field(..., description="Lord of this house")
    lord_house: Optional[int] = Field(None, description="House occupied by the lord")
    lord_sign: Optional[str] = Field(None, description="Sign occupied by the lord")
    lord_dignity: str = Field(..., description="Dignity: Exalted, Debilitated, Own Sign, Friendly, Neutral, Inimical, Combust")
    occupants: List[str] = Field(default_factory=list, description="Planets occupying this house")
    aspecting_planets: List[str] = Field(default_factory=list, description="Planets casting full aspect onto this house")
    anatomical_system_en: str = Field(..., description="Anatomical areas governed in English")
    anatomical_system_ta: str = Field(..., description="Anatomical areas governed in Tamil")
    traditional_summary_en: str = Field(..., description="Traditional health interpretation in English")
    traditional_summary_ta: str = Field(..., description="Traditional health interpretation in Tamil")
    afflictions: List[str] = Field(default_factory=list, description="Documented afflictions found")
    mitigations: List[str] = Field(default_factory=list, description="Documented mitigating factors found")


class AnatomicalSystemMapping(BaseModel):
    system_name_en: str = Field(..., description="System name (e.g., Nervous & Skin, Digestive & Intestinal)")
    system_name_ta: str = Field(..., description="System name in Tamil")
    organs_en: str = Field(..., description="Organs governed in English")
    organs_ta: str = Field(..., description="Organs governed in Tamil")
    sign_governance: str = Field(..., description="Governing zodiac sign from Kalapurusha")
    planetary_governance: str = Field(..., description="Governing graha according to classical texts")
    status: str = Field(..., description="'Balanced' | 'Afflicted' | 'Mitigated' | 'Neutral'")
    observations_en: str = Field(..., description="Classical observations in English")
    observations_ta: str = Field(..., description="Classical observations in Tamil")


class BirthChartPerspective(BaseModel):
    lagna_analysis: HouseHealthAnalysis = Field(..., description="Analysis of 1st house (vitality & constitution)")
    sixth_house_analysis: HouseHealthAnalysis = Field(..., description="Analysis of 6th house (acute roga & immunity)")
    eighth_house_analysis: HouseHealthAnalysis = Field(..., description="Analysis of 8th house (chronic factors & endurance)")
    twelfth_house_analysis: HouseHealthAnalysis = Field(..., description="Analysis of 12th house (hospitalization & recuperation)")
    triggered_rules: List[MedicalRule] = Field(default_factory=list, description="Classical rules satisfied by birth chart")
    conflicting_indications: List[str] = Field(default_factory=list, description="Classical conflicting or mitigating indications")
    anatomical_mappings: List[AnatomicalSystemMapping] = Field(default_factory=list, description="12-sign Kalapurusha anatomical audit")


class TransitInfluence(BaseModel):
    planet: str = Field(..., description="Planet name")
    sign_index: int = Field(..., description="Current transit sign (1-12)")
    sign_name_en: str = Field(..., description="Sign name in English")
    sign_name_ta: str = Field(..., description="Sign name in Tamil")
    degree: float = Field(..., description="Degree in sign")
    house_from_lagna: int = Field(..., description="House occupied relative to natal Lagna")
    is_retrograde: bool = Field(False, description="Whether transiting planet is retrograde")
    traditional_symbolism_en: str = Field(..., description="Documented transit influence in English")
    traditional_symbolism_ta: str = Field(..., description="Documented transit influence in Tamil")


class CurrentPeriodPerspective(BaseModel):
    mahadasha: str = Field(..., description="Active Mahadasha lord")
    bhukti: Optional[str] = Field(None, description="Active Antardasha / Bhukti lord")
    antara: Optional[str] = Field(None, description="Active Pratyantardasha / Antara lord")
    start_date_iso: Optional[str] = Field(None, description="Start date of active sub-period")
    end_date_iso: Optional[str] = Field(None, description="End date of active sub-period")
    matching_rules: List[MedicalRule] = Field(default_factory=list, description="Classical rules matching active period lords")
    transits: List[TransitInfluence] = Field(default_factory=list, description="Verified live planetary transits relative to natal houses")
    traditional_synthesis_en: str = Field(..., description="Traditional period explanation in English (non-diagnostic)")
    traditional_synthesis_ta: str = Field(..., description="Traditional period explanation in Tamil (non-diagnostic)")


class HistoricalPeriodItem(BaseModel):
    period_name: str = Field(..., description="Period label, e.g. 'Jupiter - Saturn'")
    lord: str = Field(..., description="Primary lord")
    sub_lord: Optional[str] = Field(None, description="Sub-lord / Bhukti lord")
    start_date_iso: str = Field(..., description="Start date ISO")
    end_date_iso: str = Field(..., description="End date ISO")
    age_range: str = Field(..., description="Approximate age range")
    traditional_rules: List[MedicalRule] = Field(default_factory=list, description="Relevant classical rules for period lords")
    traditional_notes_en: str = Field(..., description="Traditional astrological notes in English")
    traditional_notes_ta: str = Field(..., description="Traditional astrological notes in Tamil")


class HistoricalPeriodPerspective(BaseModel):
    periods: List[HistoricalPeriodItem] = Field(default_factory=list, description="Timeline of past and current astrological periods")


class VedicMedicalAnalysis(BaseModel):
    birth_chart: BirthChartPerspective = Field(..., description="Perspective A: Birth-chart research")
    current_period: CurrentPeriodPerspective = Field(..., description="Perspective B: Current-period research")
    historical_periods: HistoricalPeriodPerspective = Field(..., description="Perspective C: Historical period research")


class SignificatorSourceDetail(BaseModel):
    house: int = Field(..., description="House number (1-12)")
    source_type: str = Field(..., description="Significator mechanism: StarLord, Occupant, Owner, Aspecting")
    planet_channel: Optional[str] = Field(None, description="Planet agency or transmitting channel (e.g. Rahu -> Mercury)")
    level_name_en: str = Field(..., description="KP level name in English")
    level_name_ta: str = Field(..., description="KP level name in Tamil")
    description_en: str = Field(..., description="Source explanation in English")
    description_ta: str = Field(..., description="Source explanation in Tamil")


class KpCslAnalysis(BaseModel):
    cusp_number: int = Field(..., description="Cusp number (e.g. 6, 1, 8, 12)")
    cusp_degree: Optional[float] = Field(None, description="Cusp longitude degree")
    sign_name: Optional[str] = Field(None, description="Cusp zodiac sign")
    sign_lord: Optional[str] = Field(None, description="Cusp sign lord")
    cusp_star_lord: Optional[str] = Field(None, description="Cusp star lord")
    csl_planet: str = Field(..., description="Cuspal Sub-Lord planet")
    csl_star_lord: str = Field(..., description="Star-Lord of the CSL planet")
    star_lord: str = Field(..., description="Star-Lord (alias for csl_star_lord for backward compatibility)")
    sub_lord: Optional[str] = Field(None, description="Sub-sub lord if applicable")
    signified_houses: List[int] = Field(default_factory=list, description="Houses signified by the CSL through stellar dynamics")
    signification_details: List[SignificatorSourceDetail] = Field(default_factory=list, description="Source provenance of each signified house")
    primary_signification_en: str = Field(..., description="KP interpretation in English")
    primary_signification_ta: str = Field(..., description="KP interpretation in Tamil")
    anatomical_rulership_en: str = Field(..., description="Anatomical rulership of the CSL in English")
    anatomical_rulership_ta: str = Field(..., description="Anatomical rulership of the CSL in Tamil")
    
    # 4 Category Tri-State Evaluations: "present" | "not_found" | "data_unavailable"
    recovery_status: str = Field("not_found", description="Status for Recovery (houses 1, 5, 11)")
    disease_status: str = Field("not_found", description="Status for Disease (house 6)")
    chronic_status: str = Field("not_found", description="Status for Chronic / Surgery (house 8)")
    hospitalization_status: str = Field("not_found", description="Status for Hospitalization (house 12)")

    # Booleans for backward compatibility
    recovery_signified: bool = Field(False, description="Whether 1, 5, or 11 are signified (health recovery / negation of roga)")
    disease_signified: bool = Field(False, description="Whether 6 is signified (acute roga)")
    chronic_signified: bool = Field(False, description="Whether 8 is signified (chronic / surgical vulnerability)")
    hospitalization_signified: bool = Field(False, description="Whether 12 is signified (confinement / medical expense)")

    # Breakdown house lists
    recovery_houses: List[int] = Field(default_factory=list, description="Houses from [1, 5, 11] present")
    disease_houses: List[int] = Field(default_factory=list, description="House 6 if present")
    chronic_houses: List[int] = Field(default_factory=list, description="House 8 if present")
    hospitalization_houses: List[int] = Field(default_factory=list, description="House 12 if present")

    # Data provenance and status
    is_data_available: bool = Field(True, description="Whether CSL and significator calculation data were successfully resolved")
    missing_data_reason: Optional[str] = Field(None, description="Reason if calculation data is incomplete")
    calculation_provenance: str = Field("KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)", description="Calculation methodology provenance")



class KpDasaSignification(BaseModel):
    period_level: str = Field(..., description="Mahadasha / Bhukti / Antara")
    lord: str = Field(..., description="Lord name")
    signified_houses: List[int] = Field(default_factory=list, description="Signified houses")
    indication_en: str = Field(..., description="KP temporal indication in English")
    indication_ta: str = Field(..., description="KP temporal indication in Tamil")


class KpMedicalAnalysis(BaseModel):
    sixth_csl: KpCslAnalysis = Field(..., description="6th Cusp Sub-Lord evaluation (primary disease significator)")
    lagna_csl: Optional[KpCslAnalysis] = Field(None, description="1st Cusp Sub-Lord evaluation (physical vitality)")
    eighth_csl: Optional[KpCslAnalysis] = Field(None, description="8th Cusp Sub-Lord evaluation (chronic stress & accidents)")
    twelfth_csl: Optional[KpCslAnalysis] = Field(None, description="12th Cusp Sub-Lord evaluation (hospitalization & bed rest)")
    current_dasa_significations: List[KpDasaSignification] = Field(default_factory=list, description="KP significations of active Dasa-Bhukti lords")
    kp_rules: List[MedicalRule] = Field(default_factory=list, description="KP medical rules evaluated")
    recovery_indicators: List[str] = Field(default_factory=list, description="KP combinations indicating recovery (1, 5, 11)")
    susceptibility_indicators: List[str] = Field(default_factory=list, description="KP combinations indicating vulnerability (6, 8, 12)")


class MedicalAstrologyResponse(BaseModel):
    metadata: Optional[CalculationMetadata] = None
    rule_set_version: str = Field("1.0.0", description="Rule set version")
    disclaimer_en: str = Field(SAFETY_DISCLAIMER_EN, description="Mandatory English safety disclaimer")
    disclaimer_ta: str = Field(SAFETY_DISCLAIMER_TA, description="Mandatory Tamil safety disclaimer")
    vedic_analysis: VedicMedicalAnalysis = Field(..., description="Vedic analytical system")
    kp_analysis: Optional[KpMedicalAnalysis] = Field(None, description="KP analytical system")
