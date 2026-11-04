"""Schemas for Kuladeivam (குலதெய்வம்) Finding and Analysis Engine.

Deterministic, classical Tamil and Vedic astrology rules for identifying:
- 5th and 9th House lineage deities (D1 & D9)
- Grama Devata vs Agamic Vedic deities
- Deity gender, form, and planetary karakatwa
- Temple direction and sacred landscape markers
- Kuladeivam dosha / affliction diagnostics
- Universal prayer protocol for discovering unknown family deities
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class KuladeivamRequest(BirthInput):
    """Input payload for Horoscope-based Kuladeivam identification."""
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female')")
    ayanamsa: int = Field(0, description="Ayanamsa ID (0=Lahiri, 1=KP, 2=Raman)")
    house_system: int = Field(0, description="House system ID (0=WholeSign, 1=Equal, 2=Placidus)")
    ancestral_district: Optional[str] = Field(None, description="Optional ancestral district in Tamil Nadu or South India")
    community_tradition: Optional[str] = Field(None, description="Optional community or kula tradition if known")


class KuladeivamPrasannaRequest(BaseModel):
    """Input payload for Horary/Jamakkol Prasanna based Kuladeivam query."""
    query_datetime: str = Field(..., description="Query ISO datetime string (e.g. '2026-11-04T12:00:00')")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of query location")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of query location")
    timezone: str = Field("Asia/Kolkata", description="IANA timezone")
    ayanamsa_id: int = Field(0, description="Ayanamsa ID (0=Lahiri)")
    querent_seed: Optional[int] = Field(None, ge=1, le=249, description="Horary seed number 1-249")
    ancestral_district: Optional[str] = Field(None, description="Ancestral district if known")


class DeityIndicator(BaseModel):
    """Detailed deity profile deduced from horoscope/prasanna."""
    deity_name_ta: str
    deity_name_en: str
    deity_category_ta: str
    deity_category_en: str
    gender_ta: str
    gender_en: str
    governing_planet_ta: str
    governing_planet_en: str
    governing_house_ta: str
    governing_house_en: str
    sign_name_ta: str
    sign_name_en: str
    sign_tattva_ta: str
    sign_tattva_en: str
    prominence_score: int
    traditional_forms_ta: List[str]
    traditional_forms_en: List[str]
    description_ta: str
    description_en: str


class TempleLandscape(BaseModel):
    """Physical and directional attributes of the ancestral temple."""
    primary_direction_ta: str
    primary_direction_en: str
    alternate_direction_ta: Optional[str] = None
    alternate_direction_en: Optional[str] = None
    landscape_nature_ta: str
    landscape_nature_en: str
    temple_setting_ta: str
    temple_setting_en: str
    associated_sacred_tree_ta: str
    associated_sacred_tree_en: str
    distance_indication_ta: str
    distance_indication_en: str


class KuladeivamDoshaAnalysis(BaseModel):
    """Assessment of whether the family deity blessing is active or blocked."""
    status_ta: str
    status_en: str
    is_afflicted: bool
    affliction_factors_ta: List[str]
    affliction_factors_en: List[str]
    explanation_ta: str
    explanation_en: str
    traditional_symptoms_ta: List[str]
    traditional_symptoms_en: List[str]
    mitigation_steps_ta: List[str]
    mitigation_steps_en: List[str]


class UniversalRefugeTemple(BaseModel):
    temple_name_ta: str
    temple_name_en: str
    location_ta: str
    location_en: str
    spiritual_significance_ta: str
    spiritual_significance_en: str


class UnknownDeityDiscoveryProtocol(BaseModel):
    """Classical procedure for families who have lost trace of their Kuladeivam."""
    title_ta: str
    title_en: str
    overview_ta: str
    overview_en: str
    steps_ta: List[str]
    steps_en: List[str]
    deepam_procedure_ta: str
    deepam_procedure_en: str
    pongal_offering_ta: str
    pongal_offering_en: str
    coin_knot_ritual_ta: str
    coin_knot_ritual_en: str
    universal_refuge_temples: List[UniversalRefugeTemple]


class HouseAnalysisDetails(BaseModel):
    house_num: int
    sign_name_ta: str
    sign_name_en: str
    sign_lord_ta: str
    sign_lord_en: str
    sign_tattva_ta: str
    sign_tattva_en: str
    sign_gender_ta: str
    sign_gender_en: str
    occupants_ta: List[str]
    occupants_en: List[str]
    aspecting_grahas_ta: List[str]
    aspecting_grahas_en: List[str]
    navamsha_sign_ta: str
    navamsha_sign_en: str
    navamsha_lord_ta: str
    navamsha_lord_en: str


class KuladeivamResponse(BaseModel):
    """Complete synthesized response for Kuladeivam search."""
    analysis_mode: str  # "horoscope" or "prasanna"
    native_summary: Dict[str, Any]
    fifth_house: HouseAnalysisDetails
    ninth_house: HouseAnalysisDetails
    primary_deity: DeityIndicator
    secondary_deity: Optional[DeityIndicator] = None
    temple_landscape: TempleLandscape
    dosha_analysis: KuladeivamDoshaAnalysis
    discovery_protocol: UnknownDeityDiscoveryProtocol
    lineage_insights_ta: List[str]
    lineage_insights_en: List[str]
    classical_references: List[str]
