"""Pydantic schemas for Medical Astrology analysis and rule registry.

STRICT SAFETY RESTRICTIONS:
This is a classical and KP astrological research engine for educational purposes only.
It NEVER generates medical diagnoses, clinical probabilities, onset predictions,
lifespan/death predictions, or medical treatments.
"""

from typing import List, Optional, Dict, Any
from datetime import date, time
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


class MedicalAstrologyRequest(BaseModel):
    """Request payload for Medical Astrology evaluation supporting both ad-hoc birth input and saved horoscopes."""
    saved_horoscope_id: Optional[str] = Field(None, description="Optional ID of saved horoscope to evaluate directly")
    birth_date: Optional[date] = Field(None, description="Birth date in ISO format YYYY-MM-DD")
    birth_time: Optional[time] = Field(None, description="Local birth time in ISO format HH:MM or HH:MM:SS (24-hour)")
    timezone: Optional[str] = Field("Asia/Kolkata", description="IANA time zone name or UTC offset")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Geographic latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Geographic longitude in decimal degrees")
    ayanamsa: int = Field(0, description="Ayanamsa ID (0=Lahiri, 1=KP, 2=Raman, etc.)")
    house_system: int = Field(0, description="House System ID (0=WholeSign, 1=Equal, 2=Placidus, etc.)")
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female') for gender-specific yogas")


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
    remedy_en: Optional[str] = Field(None, description="Traditional remedial measures in English")
    remedy_ta: Optional[str] = Field(None, description="Traditional remedial measures in Tamil")


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
    dr_krishna_kumar_compendium: Optional["DrKrishnaKumarCompendium"] = Field(
        None, description="Dr. S. Krishna Kumar Medical Astrology compendium and research module"
    )
    dr_chatterjee_compendium: Optional["DrChatterjeeCompendium"] = Field(
        None, description="Dr. S. S. Chatterjee Advance Medical Astrology compendium and research module"
    )
    max_heindel_compendium: Optional["MaxHeindelCompendium"] = Field(
        None, description="Max Heindel & Augusta Foss Heindel Rosicrucian Astro-Diagnosis & Classical Medical Astrology compendium"
    )
    jane_ridder_patrick_compendium: Optional["JaneRidderPatrickCompendium"] = Field(
        None, description="Jane Ridder-Patrick 'A Handbook of Medical Astrology' compendium and research module"
    )
    heinrich_daath_compendium: Optional["HeinrichDaathCompendium"] = Field(
        None, description="Heinrich Däath 'Medical Astrology' (Astrological Manuals, No. IX) classical compendium and research module"
    )


class NakshatraMedicalDetail(BaseModel):
    number: int = Field(..., description="Nakshatra sequence number (1-27)")
    name: str = Field(..., description="Nakshatra name in English")
    name_ta: str = Field(..., description="Nakshatra name in Tamil")
    body_part_en: str = Field(..., description="Governed body region in English")
    body_part_ta: str = Field(..., description="Governed body region in Tamil")
    devata: str = Field(..., description="Presiding Nakshatra Devata")
    disease_tendency_en: str = Field(..., description="Classical disease vulnerability in English")
    disease_tendency_ta: str = Field(..., description="Classical disease vulnerability in Tamil")
    propitiation_en: str = Field(..., description="Vedic propitiation method in English")
    propitiation_ta: str = Field(..., description="Vedic propitiation method in Tamil")


class GestationalMonthDetail(BaseModel):
    month: int = Field(..., description="Gestational month (1-10)")
    ruling_planet: str = Field(..., description="Governing Graha according to classical texts")
    sanskrit_term: str = Field(..., description="Sanskrit developmental stage name")
    stage_en: str = Field(..., description="Developmental stage description in English")
    stage_ta: str = Field(..., description="Developmental stage description in Tamil")
    description_en: str = Field(..., description="Classical clinical commentary in English")
    description_ta: str = Field(..., description="Classical clinical commentary in Tamil")


class ProgenyShapaDetail(BaseModel):
    id: str = Field(..., description="Unique shapa identifier")
    shapa_name: str = Field(..., description="Name of the curse/dosha in English")
    shapa_name_ta: str = Field(..., description="Name of the curse/dosha in Tamil")
    afflicted_karaka: str = Field(..., description="Primary planetary significator afflicted")
    cause_en: str = Field(..., description="Karmic or causal origin in English")
    cause_ta: str = Field(..., description="Karmic or causal origin in Tamil")
    combinations: List[str] = Field(default_factory=list, description="Classical planetary combinations")
    remedy_en: str = Field(..., description="Classical Vedic propitiation in English")
    remedy_ta: str = Field(..., description="Classical Vedic propitiation in Tamil")
    is_indicated: bool = Field(False, description="Whether this shapa is indicated in the native's chart")
    chart_observation: Optional[str] = Field(None, description="Specific chart placement observation")


class ClinicalCaseStudy(BaseModel):
    id: str = Field(..., description="Case study ID")
    title_en: str = Field(..., description="Case title in English")
    title_ta: str = Field(..., description="Case title in Tamil")
    patient_profile: str = Field(..., description="Patient background & birth details")
    disease_diagnosed: str = Field(..., description="Medical diagnosis studied")
    astrological_indicators: List[str] = Field(default_factory=list, description="Key planetary signatures")
    dasha_timing: str = Field(..., description="Dasha / Bhukti timing of onset or surgery")
    key_takeaway: str = Field(..., description="Clinical & astrological lesson from Dr. Krishna Kumar")


class TatwaNavadwaraDetail(BaseModel):
    tatwa_en: str = Field(..., description="Pancha Bhoota element in English")
    tatwa_ta: str = Field(..., description="Pancha Bhoota element in Tamil")
    planet: str = Field(..., description="Governing planet")
    sense_en: str = Field(..., description="Subtle sense / Tanmatra in English")
    sense_ta: str = Field(..., description="Subtle sense / Tanmatra in Tamil")
    body_parts_en: str = Field(..., description="Anatomical governance in English")
    body_parts_ta: str = Field(..., description="Anatomical governance in Tamil")
    abhimani_devata: str = Field(..., description="Presiding Abhimani Devata")


class DrKrishnaKumarCompendium(BaseModel):
    book_title: str = Field(
        "A Book on Medical Astrology: Horoscope or Stethoscope (Diagnosis of Diseases, Problems in Progeny, Their Remedies)",
        description="Book Title",
    )
    book_title_ta: str = Field(
        "மருத்துவ ஜோதிடம்: ஜாதகமா அல்லது ஸ்டெதாஸ்கோப்பா (நோய் கண்டறிதல், சந்தான தோஷங்கள் மற்றும் பரிகாரங்கள்)",
        description="Book Title in Tamil",
    )
    author: str = Field(
        "Dr. S. Krishna Kumar, Chairman Bangalore Chapter of Indian Council of Astrological Sciences (Regd.) Chennai",
        description="Author details",
    )
    publisher: str = Field(
        "Bhartiya Prachya Evam Sanatan Vigyan Sansthan, Delhi",
        description="Publisher details",
    )
    salient_features: List[str] = Field(
        default_factory=list, description="Key highlights and methodology from the treatise"
    )
    native_moon_star: Optional[NakshatraMedicalDetail] = Field(
        None, description="Native's Moon Nakshatra medical profile"
    )
    native_lagna_star: Optional[NakshatraMedicalDetail] = Field(
        None, description="Native's Lagna Nakshatra medical profile"
    )
    all_27_nakshatras: List[NakshatraMedicalDetail] = Field(
        default_factory=list, description="Complete 27 Nakshatra medical matrix"
    )
    gestational_months: List[GestationalMonthDetail] = Field(
        default_factory=list, description="10 Gestational Months fetal growth guide"
    )
    progeny_shapas: List[ProgenyShapaDetail] = Field(
        default_factory=list, description="9 Progeny curses and classical remedies"
    )
    case_studies: List[ClinicalCaseStudy] = Field(
        default_factory=list, description="12 Documented clinical case histories"
    )
    tatwas_and_senses: List[TatwaNavadwaraDetail] = Field(
        default_factory=list, description="5 Tatwas, Tanmatras, and Navadwaras"
    )
    manasika_buddhi_yogas: List[MedicalRule] = Field(
        default_factory=list, description="Mental and intellectual yogas evaluated"
    )
    organ_specific_yogas: List[MedicalRule] = Field(
        default_factory=list, description="Organ-specific medical yogas evaluated"
    )
    caesarean_vs_normal_delivery_observation: Optional[str] = Field(
        None, description="Classical astrological assessment of delivery mode"
    )
    sperm_potency_observation: Optional[str] = Field(
        None, description="Classical Beeja / Veeryanu potency evaluation"
    )


# ===========================================================================
# Dr. S. S. Chatterjee "Advance Medical Astrology" Specific Research Schemas
# ===========================================================================

class SaptaDhatuDetail(BaseModel):
    dhatu_number: int = Field(..., description="Dhatu sequence index (1-7)")
    dhatu_name_en: str = Field(..., description="English anatomical tissue name (e.g. Blood, Bone, Marrow, Semen)")
    dhatu_name_ta: str = Field(..., description="Tamil name of Dhatu")
    sanskrit_term: str = Field(..., description="Classical Ayurvedic term (Rasa, Rakta, Mamsa, Medas, Asthi, Majja, Shukra/Snayu)")
    governing_planet: str = Field(..., description="Governing Graha according to Dr. S.S. Chatterjee & Classical treatises")
    physiological_function_en: str = Field(..., description="Biological and physiological role in body")
    physiological_function_ta: str = Field(..., description="Biological and physiological role in Tamil")
    status: str = Field(..., description="'Balanced' | 'Afflicted' | 'Weakened' | 'Fortified'")
    observations_en: str = Field(..., description="Observation based on governing planet dignity and aspects")
    observations_ta: str = Field(..., description="Observation in Tamil")


class EndocrineGlandDetail(BaseModel):
    gland_name_en: str = Field(..., description="Endocrine gland name")
    gland_name_ta: str = Field(..., description="Gland name in Tamil")
    governing_planets: List[str] = Field(..., description="Planets governing this gland according to Dr. Chatterjee")
    hormones_secreted: str = Field(..., description="Key hormones secreted (e.g., Insulin, Thyroxine, Adrenaline)")
    physiological_role_en: str = Field(..., description="Metabolic and systemic role in English")
    physiological_role_ta: str = Field(..., description="Metabolic and systemic role in Tamil")
    status: str = Field(..., description="'Balanced' | 'Vulnerable' | 'Afflicted'")
    observations_en: str = Field(..., description="Assessment based on governing planets' chart strength")
    observations_ta: str = Field(..., description="Assessment in Tamil")


class TridoshaSiteDetail(BaseModel):
    site_en: str = Field(..., description="Anatomical location: Head, Neck, Chest, Abdomen, Legs")
    site_ta: str = Field(..., description="Anatomical location in Tamil")
    governing_signs: str = Field(..., description="Governing zodiac signs")
    vata_manifestation: str = Field(..., description="Vata expression (e.g., Thrombosis, Palsy, Bronchial asthma)")
    pitta_manifestation: str = Field(..., description="Pitta expression (e.g., Meningitis, Laryngitis, Bronchitis)")
    kapha_manifestation: str = Field(..., description="Kapha expression (e.g., Brain edema, Goiter, Pleurisy)")


class DeathPointCalculation(BaseModel):
    formula: str = Field("Ascendant Longitude + Sun Longitude + Moon Longitude + Jupiter Longitude (mod 360°)", description="Formula defined by Dr. S.S. Chatterjee (1989)")
    longitude_deg: float = Field(..., description="Computed Mrityu/Chidra Point in zodiac (0-360°)")
    sign_index: int = Field(..., description="Sign index (1-12)")
    sign_name_en: str = Field(..., description="Sign name in English")
    sign_name_ta: str = Field(..., description="Sign name in Tamil")
    degree_in_sign: float = Field(..., description="Degree within sign (0-30°)")
    nakshatra_name: str = Field(..., description="Nakshatra of the Death Point")
    nakshatra_pada: int = Field(..., description="Pada of the Nakshatra (1-4)")
    transit_saturn_aspect_active: bool = Field(..., description="Whether transit Saturn casts aspect (1st, 3rd, 7th, 10th Drishti) on Death Point")
    aspect_details_en: str = Field(..., description="Description of transit Saturn aspect to this point")
    aspect_details_ta: str = Field(..., description="Description of transit Saturn aspect in Tamil")


class DiabetesMellitusAssessment(BaseModel):
    venus_status: str = Field(..., description="Venus condition (ruler of glands & endocrine secretions)")
    jupiter_status: str = Field(..., description="Jupiter condition (ruler of liver glycogen reserves & recovery)")
    virgo_status: str = Field(..., description="Virgo / 6th house of zodiac (pancreatic region) status")
    sixth_house_status: str = Field(..., description="6th house from natal Lagna status")
    affliction_score: int = Field(..., description="Number of diabetic indicators triggered (0-5)")
    risk_level: str = Field(..., description="'Low' | 'Moderate' | 'High'")
    symptoms_noted: List[str] = Field(default_factory=list, description="Classical clinical symptoms documented by Dr. Chatterjee")
    remedial_measures_en: List[str] = Field(default_factory=list, description="Natural and dietetic therapies recommended by Dr. Chatterjee")
    remedial_measures_ta: List[str] = Field(default_factory=list, description="Natural and dietetic therapies in Tamil")


class ModernComplexDiseaseDetail(BaseModel):
    name_en: str = Field(..., description="Disease name")
    name_ta: str = Field(..., description="Tamil name")
    key_symptoms: str = Field(..., description="Key clinical symptoms from text")
    astrological_indicators: str = Field(..., description="Astrological indicators identified by Dr. Chatterjee")


class NaturalRemediesGuide(BaseModel):
    planetary_colour_therapy: List[Dict[str, str]] = Field(default_factory=list, description="Colours associated with each planet and dietary items")
    metal_charged_waters: List[Dict[str, str]] = Field(default_factory=list, description="Copper, Silver, Gold, and Iron charged water therapies")
    fasting_and_diet: List[str] = Field(default_factory=list, description="Dietary discipline, salt reduction, Tuesday/Saturday fasting")
    vega_dharana_urges: List[Dict[str, str]] = Field(default_factory=list, description="13 non-suppressible natural urges and their pathological consequences")


class DrChatterjeeCompendium(BaseModel):
    book_title: str = Field("Advance Medical Astrology", description="English treatise title")
    book_title_ta: str = Field("அட்வான்ஸ் மருத்துவ ஜோதிடம்", description="Tamil treatise title")
    author: str = Field("Dr. S. S. Chatterjee, Ph.D. (BHU), Ex-Executive Engineer PDIL, Recipient of Shri Santhanam Award", description="Author citation")
    publisher: str = Field("Rave Publication, Sumerpur", description="Publisher citation")
    salient_features: List[str] = Field(default_factory=list, description="Core methodology and highlights")
    death_point: DeathPointCalculation = Field(..., description="Dr. Chatterjee's signature Death Point and Saturn aspect analysis")
    parijata_longevity_eval: Dict[str, Any] = Field(default_factory=dict, description="Parijata Yoga & Kendra/Trikona longevity analysis")
    sapta_dhatus: List[SaptaDhatuDetail] = Field(default_factory=list, description="Seven planetary tissue matrix")
    endocrine_glands: List[EndocrineGlandDetail] = Field(default_factory=list, description="Endocrine gland planetary governance")
    tridosha_sites: List[TridoshaSiteDetail] = Field(default_factory=list, description="Anatomical site Tridosha chart")
    diabetes_assessment: DiabetesMellitusAssessment = Field(..., description="Special Diabetes Mellitus (Madhumeha) analytical module")
    modern_diseases: List[ModernComplexDiseaseDetail] = Field(default_factory=list, description="10 modern 21st-century complex diseases")
    natural_remedies: NaturalRemediesGuide = Field(..., description="Comprehensive natural remedies, colour therapy, and metal waters")
    golden_rules: List[MedicalRule] = Field(default_factory=list, description="Evaluated rules from Dr. Chatterjee's 241 Golden Rules")
    case_studies: List[Dict[str, Any]] = Field(default_factory=list, description="Documented illustrative clinical cases from Dr. Chatterjee's diary")


# ===========================================================================
# Max Heindel & Augusta Foss Heindel "Astro-Diagnosis: A Guide to Healing" Schemas
# ===========================================================================

class HeindelSignAnatomy(BaseModel):
    sign_index: int = Field(..., description="Zodiac sign index (1-12)")
    sign_name_en: str = Field(..., description="Zodiac sign name in English")
    sign_name_ta: str = Field(..., description="Zodiac sign name in Tamil")
    manilius_rulership: str = Field(..., description="Classical Marcus Manilius (1st century AD) head-to-toe body rulership")
    heindel_anatomical_systems: List[str] = Field(default_factory=list, description="Specific anatomical structures and organs ruled by this sign")
    pathological_qualities: str = Field(..., description="Pathological disposition (e.g. Hot, dry, inflammatory, cold, sluggish)")
    physiological_afflictions: List[str] = Field(default_factory=list, description="Common physiological afflictions and clinical vulnerabilities")
    temperament_and_healing_reaction: str = Field(..., description="Psychological response to illness and healing tendencies")
    is_native_ascendant: bool = Field(False, description="Whether this is native's rising sign")
    is_native_sun_sign: bool = Field(False, description="Whether this is native's Sun sign")
    is_native_moon_sign: bool = Field(False, description="Whether this is native's Moon sign")


class HeindelPlanetPhysiology(BaseModel):
    planet: str = Field(..., description="Planet name")
    planet_ta: str = Field(..., description="Planet name in Tamil")
    salient_keyword: str = Field(..., description="Salient keyword (Life, Coalition, Reason, Fecundation, Obstruction, Idealism, Dynamic Energy, Altruism, Divinity)")
    anatomical_rulership: str = Field(..., description="Governed organs and physiological fluids")
    pathological_quality: str = Field(..., description="Qualities: Hot, cold, moist, dry, vital, contracting, expansive, spasmodic, comatose")
    positive_expression: str = Field(..., description="Healthy manifestation when well-aspected")
    afflicted_expression: str = Field(..., description="Pathological manifestation when afflicted")
    chart_status: str = Field("Neutral", description="Native's chart condition: Exalted, Strong, Afflicted, Neutral")


class HeindelViciousCircle(BaseModel):
    cross_name: str = Field(..., description="Cross name: Cardinal / Equinoctial, Fixed, or Mutable / Common")
    cross_name_ta: str = Field(..., description="Cross name in Tamil")
    signs_involved: List[str] = Field(default_factory=list, description="Signs constituting the four arms of the cross")
    organ_sympathies: str = Field(..., description="Sympathetic organ axis")
    clinical_mechanism: str = Field(..., description="Clinical mechanism of disease reflection")
    clinical_examples: List[str] = Field(default_factory=list, description="Textbook examples from Heindel")
    is_native_cross_active: bool = Field(False, description="Whether native has Ascendant or key afflictions in this cross")
    chart_notes: Optional[str] = Field(None, description="Observations regarding native's planets in this cross")


class HeindelNailDiagnosis(BaseModel):
    nail_type_en: str = Field(..., description="Nail diagnosis category (Heart, Liver, Lungs, Nerves, Spine, Blood, Thumb)")
    nail_type_ta: str = Field(..., description="Nail diagnosis category in Tamil")
    physical_indicators: str = Field(..., description="Specific morphology, half-moon color, ridges, curvature")
    pathological_significance: str = Field(..., description="Underlying constitutional or organic weakness indicated")
    constitutional_correlation: str = Field(..., description="Astrological correlation (Zodiac sign, element, or planet)")
    remedial_and_hygiene_guidance: str = Field(..., description="Practical hygienic guidance from Heindel")


class HeindelPlanetaryAntidote(BaseModel):
    afflicting_planet: str = Field(..., description="Afflicted or excessive planet (e.g. Mars, Saturn)")
    afflicting_metal: str = Field(..., description="Metal of the afflicting planet (e.g. Iron, Lead)")
    antidote_planet: str = Field(..., description="Antidoting planet (e.g. Venus, Jupiter)")
    antidote_metal: str = Field(..., description="Antidote metal (e.g. Copper for Mars, Tin for Saturn)")
    antidote_gem: str = Field(..., description="Harmonizing gemstone")
    antidote_color: str = Field(..., description="Harmonizing color")
    polarity_law: str = Field(..., description="Rosicrucian polarity dynamic")
    practical_application: str = Field(..., description="Dietary, atmospheric, or talismanic instructions")


class HeindelAphorism(BaseModel):
    number: int = Field(..., description="Aphorism number (1-43)")
    category: str = Field(..., description="Lunar Cycles | Surgical Precaution | Natal Constitution | Planetary Hours | Fixed Stars")
    aphorism_en: str = Field(..., description="Aphorism text in English")
    aphorism_ta: str = Field(..., description="Aphorism text in Tamil")
    practical_implication: str = Field(..., description="Clinical & lifestyle application for the patient and healer")


class HeindelNebularSpot(BaseModel):
    name: str = Field(..., description="Nebular spot name (Pleiades, Ascelli, Antares)")
    zodiac_degree: str = Field(..., description="Zodiac position: 29° Taurus, 6° Leo, 8° Sagittarius")
    pathological_focus: str = Field("Ocular Affections / Eyesight Impairment", description="Primary physical affection")
    esoteric_mitigation: str = Field(..., description="Spiritual compensation: awakening of inner second-sight when well-aspected")
    native_chart_proximity: bool = Field(False, description="Whether Sun, Moon, or malefics are within orb of this nebular spot")
    chart_details: Optional[str] = Field(None, description="Details of any planetary conjunction in native's chart")


class MaxHeindelCompendium(BaseModel):
    book_title: str = Field("Astro-Diagnosis: A Guide to Healing & The Message of the Stars", description="English treatise title")
    book_title_ta: str = Field("ஜோதிட நோய்நிர்ணயம்: குணமளிக்கும் வழிகாட்டி மற்றும் விண்மீன்களின் செய்தி", description="Tamil treatise title")
    authors: str = Field("Max Heindel & Augusta Foss Heindel (The Rosicrucian Fellowship, Oceanside, California)", description="Authors citation")
    historical_foundation: str = Field("Marcus Manilius (1st century AD Astronomica) & Western Rosicrucian Astro-Diagnosis", description="Historical provenance")
    core_philosophy_en: str = Field(..., description="Core philosophy: Spiritual etiology, laws of right living, and healer's role")
    core_philosophy_ta: str = Field(..., description="Core philosophy in Tamil")
    healer_injunctions: List[Dict[str, str]] = Field(default_factory=list, description="19 Golden Injunctions for the Healer")
    signs_anatomy: List[HeindelSignAnatomy] = Field(default_factory=list, description="Complete 12-sign anatomical & pathological guide")
    planets_physiology: List[HeindelPlanetPhysiology] = Field(default_factory=list, description="Planetary physiology & pathological qualities")
    sense_organs_affinities: List[Dict[str, str]] = Field(default_factory=list, description="Astrological affinities of Eyes, Ears, Nose, Tongue")
    vicious_circles: List[HeindelViciousCircle] = Field(default_factory=list, description="The Three Vicious Circles (Cardinal, Fixed, Mutable)")
    nail_and_hand_diagnosis: List[HeindelNailDiagnosis] = Field(default_factory=list, description="Astro-Dermatoglyphics: 12 nail types, thumb proportions & mounts")
    planetary_antidotes: List[HeindelPlanetaryAntidote] = Field(default_factory=list, description="Rosicrucian mineralogical & color antidotes")
    nebular_spots: List[HeindelNebularSpot] = Field(default_factory=list, description="Critical fixed star nebular spots (Pleiades, Ascelli, Antares)")
    aphorisms: List[HeindelAphorism] = Field(default_factory=list, description="The 43 Golden Aphorisms of Astro-Diagnosis")
    chart_evaluation: Dict[str, Any] = Field(default_factory=dict, description="Native chart evaluation against Heindel principles")
    matched_rules: List[MedicalRule] = Field(default_factory=list, description="Heindel specific medical rules active in chart")


# ===========================================================================
# Jane Ridder-Patrick "A Handbook of Medical Astrology" Schemas
# ===========================================================================

class JaneDecumbitureEvaluation(BaseModel):
    ascendant_degree: float = Field(..., description="Ascendant degree in sign (0-30)")
    is_asc_early_or_late: bool = Field(False, description="Stricture: Ascendant < 3° or > 27°")
    asc_stricture_note: Optional[str] = Field(None, description="Observation on Ascendant stricture")
    moon_in_via_combusta: bool = Field(False, description="Stricture: Moon in 15° Libra to 15° Scorpio (195°-225°)")
    moon_void_of_course: bool = Field(False, description="Stricture: Moon Void of Course")
    saturn_in_seventh: bool = Field(False, description="Stricture: Saturn in 7th house (practitioner error warning)")
    seventh_house_afflicted: bool = Field(False, description="Stricture: 7th cusp afflicted or 7th lord Rx")
    asc_lord_combust_or_saturn_in_first: bool = Field(False, description="Stricture: Ascendant lord combust or Saturn in 1st")
    critical_days_cycle_en: str = Field(..., description="Critical days (Moon at 45°, 90°, 135°, 180° for acute; Sun for chronic)")
    critical_days_cycle_ta: str = Field(..., description="Critical days in Tamil")
    sidedness_indicator: str = Field(..., description="Body orientation: Masculine/diurnal = Right/Front; Feminine/nocturnal = Left/Back")


class JaneArabianParts(BaseModel):
    part_of_sickness_deg: float = Field(..., description="Ascendant + Mars - Saturn (0-360°)")
    part_of_sickness_sign: str = Field(..., description="Zodiac sign of Part of Sickness")
    part_of_sickness_coord: str = Field(..., description="Formatted coordinate")
    part_of_surgery_deg: float = Field(..., description="Ascendant + Saturn - Mars (0-360°)")
    part_of_surgery_sign: str = Field(..., description="Zodiac sign of Part of Surgery")
    part_of_surgery_coord: str = Field(..., description="Formatted coordinate")
    part_of_death_deg: float = Field(..., description="Ascendant + 8th cusp - Moon (0-360°)")
    part_of_death_sign: str = Field(..., description="Zodiac sign of Part of Death")
    part_of_death_coord: str = Field(..., description="Formatted coordinate")
    clinical_notes_en: str = Field(..., description="Clinical interpretation of Arabian Parts in Medical Astrology")
    clinical_notes_ta: str = Field(..., description="Clinical interpretation of Arabian Parts in Tamil")


class JaneElementalAnalysis(BaseModel):
    air_count: int = Field(0, description="Planets in Air signs")
    fire_count: int = Field(0, description="Planets in Fire signs")
    water_count: int = Field(0, description="Planets in Water signs")
    earth_count: int = Field(0, description="Planets in Earth signs")
    moon_element: str = Field(..., description="Element of natal Moon")
    dominant_element: str = Field(..., description="Dominant element")
    deficient_element: str = Field(..., description="Deficient or low element")
    dietary_balancing_en: str = Field(..., description="Dietary and lifestyle balancing according to Jane Ridder-Patrick")
    dietary_balancing_ta: str = Field(..., description="Dietary and lifestyle balancing in Tamil")
    herbal_classes_indicated: List[str] = Field(default_factory=list, description="Indicated herbal classes (e.g. Alteratives, Demulcents, Nervines)")


class JaneCellSaltCorrespondence(BaseModel):
    sign: str = Field(..., description="Zodiac sign")
    sign_ta: str = Field(..., description="Zodiac sign in Tamil")
    cell_salt: str = Field(..., description="Biochemic tissue salt (Carey & Perry)")
    abbreviation: str = Field(..., description="Standard abbreviation (e.g. Kali phos)")
    physiological_action_en: str = Field(..., description="Physiological action")
    physiological_action_ta: str = Field(..., description="Physiological action in Tamil")
    is_native_sign: bool = Field(False, description="Whether Sun, Moon, or Ascendant is in this sign")


class JaneBachFlowerCorrespondence(BaseModel):
    sign: str = Field(..., description="Zodiac sign")
    sign_ta: str = Field(..., description="Zodiac sign in Tamil")
    flower_remedy: str = Field(..., description="Bach Flower remedy (Peter Damian)")
    emotional_archetype_en: str = Field(..., description="Emotional and soul indication")
    emotional_archetype_ta: str = Field(..., description="Emotional and soul indication in Tamil")
    is_native_sign: bool = Field(False, description="Whether Sun, Moon, or Ascendant is in this sign")


class JaneAcupunctureMeridian(BaseModel):
    sign: str = Field(..., description="Zodiac sign")
    sign_ta: str = Field(..., description="Zodiac sign in Tamil")
    meridian: str = Field(..., description="Acupuncture meridian (Ebertin)")
    meridian_ta: str = Field(..., description="Acupuncture meridian in Tamil")
    is_native_sign: bool = Field(False, description="Whether Sun, Moon, or Ascendant is in this sign")


class JaneRidderPatrickCompendium(BaseModel):
    book_title: str = Field("A Handbook of Medical Astrology (Second Edition, Revised and Enlarged)", description="Treatise title")
    book_title_ta: str = Field("மருத்துவ ஜோதிட கையேடு (இரண்டாம் பதிப்பு - ஜேன் ரிடர்-பேட்ரிக்)", description="Tamil treatise title")
    author: str = Field("Jane Ridder-Patrick, Ph.D., N.D., M.N.I.M.H. (Edinburgh, Scotland)", description="Author citation")
    publisher: str = Field("CrabApple Press, Edinburgh", description="Publisher")
    alphabet_framework: Dict[str, str] = Field(default_factory=dict, description="Astrological Alphabet: Planets=WHAT, Signs=WHERE, Aspects=HOW, Houses=WHICH, Transits=WHEN")
    three_crosses: List[Dict[str, Any]] = Field(default_factory=list, description="Cardinal (Regulation), Fixed (Vital Functions), Mutable (Metabolic) and reflex actions")
    decumbiture: JaneDecumbitureEvaluation = Field(..., description="Decumbiture chart diagnostics, strictures, hours, and critical days")
    arabian_parts: JaneArabianParts = Field(..., description="Part of Sickness, Part of Surgery, Part of Death calculated for native")
    elemental_analysis: JaneElementalAnalysis = Field(..., description="Ayurvedic/Western element balance & dietary balancing")
    culpeper_therapeutic_rules: List[Dict[str, str]] = Field(default_factory=list, description="Nicholas Culpeper's 7 Rules for Astrological Therapeutics")
    stages_of_therapy: List[Dict[str, str]] = Field(default_factory=list, description="3 Stages of Astrological Therapy: Identification, Exploration, Upgrading")
    cell_salts: List[JaneCellSaltCorrespondence] = Field(default_factory=list, description="12 Biochemic Cell Salts (Carey & Perry)")
    bach_flowers: List[JaneBachFlowerCorrespondence] = Field(default_factory=list, description="12 Bach Flower Remedies (Peter Damian)")
    acupuncture_meridians: List[JaneAcupunctureMeridian] = Field(default_factory=list, description="12 Acupuncture Meridians (Ebertin)")
    matched_rules: List[MedicalRule] = Field(default_factory=list, description="Active chart-matched rules from Jane Ridder-Patrick")


# ===========================================================================
# Heinrich Däath "Medical Astrology" (Astrological Manuals, IX) Schemas
# ===========================================================================

class DaathSignAnatomy(BaseModel):
    sign_index: int = Field(..., description="Zodiac sign index (1-12)")
    sign_name_en: str = Field(..., description="Zodiac sign name in English")
    sign_name_ta: str = Field(..., description="Zodiac sign name in Tamil")
    symbolic_quality: str = Field(..., description="Symbolic quality (e.g. Hot, dry, sterile, inflammatory)")
    principal_bones: List[str] = Field(default_factory=list, description="Principal bones dominated by this sign")
    muscles: List[str] = Field(default_factory=list, description="Principal muscles governed")
    arteries: List[str] = Field(default_factory=list, description="Arterial supply governed")
    veins: List[str] = Field(default_factory=list, description="Venous network governed")
    morbid_actions: List[str] = Field(default_factory=list, description="Documented morbid actions and typical diseases")
    kidney_pelvis_distinction: Optional[str] = Field(None, description="Critical physiological distinction (e.g. Libra cortical filtration vs Scorpio renal pelvis retention/calculus)")
    is_native_ascendant: bool = Field(False, description="Whether this is native's rising sign")
    is_native_sun_sign: bool = Field(False, description="Whether this is native's Sun sign")
    is_native_moon_sign: bool = Field(False, description="Whether this is native's Moon sign")
    is_native_sixth_house: bool = Field(False, description="Whether this is native's 6th house sign")


class DaathPlanetAction(BaseModel):
    planet: str = Field(..., description="Planet name")
    planet_ta: str = Field(..., description="Planet name in Tamil")
    esoteric_title: str = Field(..., description="Classical title (e.g. Dwadasatma, Mumia Evestrum, Spiritus, Adech, Rudhira, Corpus Limbus)")
    biodynamic_motion: str = Field(..., description="Biodynamic vector mode")
    polarity: str = Field(..., description="Positive / Tonic or Negative / Atonic or Convertible")
    functional_group: str = Field(..., description="Vital Energy, Natural/Expulsive, Mental, Nutritive, Retentive")
    tissue_building: str = Field(..., description="Vital, Fluidic/Cleansing, Nerve-tissue, Cellular, Fibrous, Cartilaginous/Osseous")
    elemental_degrees: str = Field(..., description="Hot/Cold and Dry/Moist degrees (+ intense, - remiss)")
    salient_pathognomy: str = Field(..., description="Salient pathognomic signs (plus or minus)")
    typical_drugs: List[str] = Field(default_factory=list, description="Typical pharmaceutical/herbal simples")
    typical_plants: List[str] = Field(default_factory=list, description="Typical botanical plants")
    therapeutic_properties: List[str] = Field(default_factory=list, description="Therapeutic actions")
    metals_minerals: List[str] = Field(default_factory=list, description="Associated metals and minerals")
    native_chart_condition: str = Field("Neutral", description="Native's chart status (Tonic / Atonic / Perverted / Balanced)")


class DaathAntipathicTherapy(BaseModel):
    category: str = Field(..., description="Disease condition or diathesis")
    category_ta: str = Field(..., description="Disease condition in Tamil")
    opposing_polarity_rule: str = Field(..., description="Contraria contrariis curantur therapeutic principle")
    afflicting_planetary_force: str = Field(..., description="Root planetary cause (e.g. Saturnine cold/cachexy, Martial heat/fevers)")
    curative_planetary_remedy: str = Field(..., description="Antipathic remedy planet (e.g. Mars ferrum/tonics for Saturn; Saturn antimony/cold for Mars)")
    substances_and_application: str = Field(..., description="Specific substances, dietary applications, and physiological action")


class DaathPlanetaryPeriod(BaseModel):
    planet: str = Field(..., description="Governing planet")
    planet_ta: str = Field(..., description="Planet in Tamil")
    start_age: int = Field(..., description="Starting age in years")
    end_age: int = Field(..., description="Ending age in years")
    age_label: str = Field(..., description="Age period label")
    age_label_ta: str = Field(..., description="Age period label in Tamil")
    biological_development: str = Field(..., description="Physiological maturation focus of this life period")
    astrological_vulnerability: str = Field(..., description="Vulnerabilities if this governing planet is afflicted in radix or directions")
    is_native_current_age: bool = Field(False, description="Whether native is currently within this age span")


class DaathDecumbitureCriticalDays(BaseModel):
    lunar_critical_cycles: List[Dict[str, str]] = Field(default_factory=list, description="7th, 14th, 21st day lunar aspects in acute febrile illnesses")
    lunar_phases_metabolism: List[Dict[str, str]] = Field(default_factory=list, description="New Moon (systole/low ebb), Full Moon (diastole/fluidic plenitude), Quarters")
    climacteric_seven_year_law: str = Field(..., description="Uranus 84-year / 7-year per sign cycle & progressed lunar quarters (7th day = 7th year)")
    climacteric_seven_year_law_ta: str = Field(..., description="Climacteric law in Tamil")


class DaathStrengthEvaluation(BaseModel):
    drikbalam_aspect_summary: str = Field(..., description="Aspect strength: Trine (anabolic) vs Square/Opp (katabolic) vs Conjunction (interdependent)")
    sthanabalam_summary: str = Field(..., description="Positional strength across the 12 dignities (Atchi Ucha to Atinicha)")
    nisargikabalam_mutual_receptions: List[str] = Field(default_factory=list, description="Planetary sign receptions / mutual exchanges (e.g. Mars in Cancer + Moon in Aries)")
    mundane_strength_summary: str = Field(..., description="Angular houses (1, 4, 7, 10) vs Cadent disease houses (6, 12, 3, 9)")
    motional_strength_summary: str = Field(..., description="Daily speed, station, retrogradation status (e.g. Retrograde Jupiter weakened)")
    directional_hexis_vs_diathesis: str = Field(..., description="Hexis (permanent habit in radix) vs Diathesis (transient disposition by direction)")


class HeinrichDaathCompendium(BaseModel):
    book_title: str = Field("Medical Astrology (Astrological Manuals, No. IX)", description="English book title")
    book_title_ta: str = Field("மருத்துவ ஜோதிடம் (கைநூல் 9 - ஹென்ரிச் டாத் & ஆலன் லியோ)", description="Tamil book title")
    author: str = Field("Heinrich Däath (Foreword & Editorial by Alan Leo, Modern Astrology, London)", description="Author citation")
    publisher: str = Field("L. N. Fowler & Co., Imperial Arcade & 'Modern Astrology' Office, West Hampstead, London", description="Publisher")
    historical_foundation: str = Field("Ancient Egyptian Jatromathematics & Paracelsian Adept Medicine (Medicina Adepta)", description="Historical foundation")
    core_philosophy_en: str = Field(..., description="Core philosophy: Microcosm/Macrocosm, Adelphixis, and Vibration")
    core_philosophy_ta: str = Field(..., description="Core philosophy in Tamil")
    signs_anatomy: List[DaathSignAnatomy] = Field(default_factory=list, description="Comprehensive 12-sign anatomical rulership with bones, muscles, vessels & morbid actions")
    planets_biodynamics: List[DaathPlanetAction] = Field(default_factory=list, description="9-planet biodynamics, polarities, tissues, pathognomy, and materia medica")
    temperaments_and_crosses: Dict[str, Any] = Field(default_factory=dict, description="4 Trigons / Temperaments (Sanguine, Choleric, Nervous, Lymphatic) and 3 Crosses")
    antipathic_therapeutics: List[DaathAntipathicTherapy] = Field(default_factory=list, description="Contraria Contrariis Curantur therapeutics")
    seven_ages_of_man: List[DaathPlanetaryPeriod] = Field(default_factory=list, description="The Seven Ages of Man (Planetary Life-Periods 0-4y to 64y+)")
    decumbiture_and_cycles: DaathDecumbitureCriticalDays = Field(..., description="Decumbiture lunar critical days and 7-year climacteric laws")
    strength_evaluation: DaathStrengthEvaluation = Field(..., description="5-fold strength evaluation: Aspect, Positional, Natural, Motional, Directional")
    matched_rules: List[MedicalRule] = Field(default_factory=list, description="Active chart-matched classical rules from Heinrich Däath")


# Rebuild forward references for Pydantic v2
MedicalAstrologyResponse.model_rebuild()
