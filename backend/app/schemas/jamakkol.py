"""Pydantic schemas for Jamakkol Prasanam (ஜாமக்கோள் பிரசன்னம்) API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JamakkolPrasanamRequest(BaseModel):
    query_datetime: str = Field(
        ...,
        description="ISO 8601 string of query moment (e.g. '2026-10-28T14:30:00')",
        examples=["2026-10-28T14:30:00"],
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographic latitude of astrologer / query place",
        examples=[13.0827],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographic longitude of astrologer / query place",
        examples=[80.2707],
    )
    timezone: str = Field(
        default="Asia/Kolkata",
        description="IANA Timezone string",
        examples=["Asia/Kolkata"],
    )
    ayanamsa_id: int = Field(
        default=0,
        description="Ayanamsa ID (0=Lahiri, 1=KP, 2=Raman)",
    )
    query_text: Optional[str] = Field(
        default=None,
        description="The specific question asked by the querent",
        examples=["Will my business partnership proposal succeed?"],
    )
    query_category: Optional[str] = Field(
        default="general",
        description="Query classification category",
        examples=["business_finance"],
    )
    querent_seed: Optional[int] = Field(
        default=None,
        ge=1,
        le=249,
        description="Optional querent seed number (1 to 108 or 1 to 249) to derive Arudham",
    )


class PillarDetail(BaseModel):
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    longitude: float
    degree_in_sign: float
    dms: str
    lord_en: str
    lord_ta: str
    nature: str
    nature_ta: str
    direction_en: str
    direction_ta: str
    nakshatra_name: Optional[str] = None
    pada: Optional[int] = None
    surya_veethi: Optional[str] = None
    surya_veethi_en: Optional[str] = None
    distance_from_arudham: Optional[int] = None
    calculation_basis: Optional[str] = None


class ThreePillars(BaseModel):
    udhayam: PillarDetail
    aarudham: PillarDetail
    kavippu: PillarDetail


class JamaGrahaItem(BaseModel):
    id: str
    name_en: str
    name_ta: str
    symbol: str
    classical_name_ta: str
    is_benefic: bool
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    degree_in_sign: float
    dms: str
    signification_en: str
    signification_ta: str
    color: str


class TransitPlanetItem(BaseModel):
    name_en: str
    name_ta: str
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    longitude: float
    degree_in_sign: float
    dms: str
    is_retrograde: bool
    speed: float
    nakshatra: str
    is_exalted: bool = False
    is_debilitated: bool = False


class HousePlacementItem(BaseModel):
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    nature: str
    nature_ta: str
    lord_en: str
    lord_ta: str
    direction_en: str
    direction_ta: str
    house_from_udhayam: int
    house_from_aarudham: int
    is_udhayam: bool
    is_aarudham: bool
    is_kavippu: bool
    jama_grahas: List[Dict[str, Any]]
    transit_planets: List[Dict[str, Any]]


class PredictionVerdict(BaseModel):
    status: str
    score: int
    verdict_title_en: str
    verdict_title_ta: str
    verdict_summary_en: str
    verdict_summary_ta: str
    pillar_dynamics_en: str
    pillar_dynamics_ta: str
    kavippu_impact_en: str
    kavippu_impact_ta: str
    directional_guidance_en: str
    directional_guidance_ta: str
    timing_of_event_en: str
    timing_of_event_ta: str
    category_specific_insights_en: List[str]
    category_specific_insights_ta: List[str]
    remedial_measures_en: List[str]
    remedial_measures_ta: List[str]


class JamamInfo(BaseModel):
    period_type: str
    jamam_number: int
    jamam_start_local: str
    jamam_end_local: str
    jamam_ruler_en: str
    jamam_ruler_ta: str
    jamam_ruler_symbol: str
    is_benefic_ruler: bool
    weekday_lord_en: str
    weekday_lord_ta: str
    progress_percent: float


class SolarInfo(BaseModel):
    sunrise_local: str
    sunset_local: str
    is_day: bool
    day_duration: str
    night_duration: str
    dinamana_ghatikas: float
    surya_veethi: str
    surya_veethi_en: str


class ClassicalRulesAnalysis(BaseModel):
    watch_time_relation: Dict[str, Any]
    facing_direction: Dict[str, Any]
    rising_nature: Dict[str, Any]
    subh_balance: Dict[str, Any]
    lord_connections: Dict[str, Any]
    kavippu_afflictions: Dict[str, Any]
    approaching_planets: List[Dict[str, Any]]
    crossed_planets: List[Dict[str, Any]]
    planets_in_udayam: List[Dict[str, Any]]
    exalted_debilitated_audit: Dict[str, Any]
    relationship_analysis: Optional[Dict[str, Any]] = None
    politics_govt_analysis: Optional[Dict[str, Any]] = None
    foreign_travel_analysis: Optional[Dict[str, Any]] = None
    court_case_analysis: Optional[Dict[str, Any]] = None
    loans_analysis: Optional[Dict[str, Any]] = None
    agriculture_borewell_rain_analysis: Optional[Dict[str, Any]] = None
    share_market_analysis: Optional[Dict[str, Any]] = None
    kavippu_bhava_effect: Optional[Dict[str, Any]] = None
    udayam_lord_thought: Optional[Dict[str, Any]] = None
    conjoined_inner_outer_planets: Optional[List[Dict[str, Any]]] = None
    parivartana_exchanges: Optional[List[Dict[str, Any]]] = None
    eighth_lord_in_udayam: Optional[Dict[str, Any]] = None
    snake_udayam_analysis: Optional[Dict[str, Any]] = None
    evil_spirits_black_magic_analysis: Optional[Dict[str, Any]] = None
    natural_unnatural_death_analysis: Optional[Dict[str, Any]] = None
    rain_disaster_catastrophe_analysis: Optional[Dict[str, Any]] = None
    muhurta_analysis: Optional[Dict[str, Any]] = None
    planet_attributes_table: Optional[Dict[str, Any]] = None


class JamakkolPrasanamResponse(BaseModel):
    query_datetime: str
    query_text: Optional[str] = None
    query_category: Optional[str] = "general"
    location: Dict[str, Any]
    solar_info: SolarInfo
    jamam_info: JamamInfo
    three_pillars: ThreePillars
    jama_grahas: List[JamaGrahaItem]
    transit_planets: List[TransitPlanetItem]
    house_placements: List[HousePlacementItem]
    prediction_verdict: PredictionVerdict
    classical_rules: ClassicalRulesAnalysis
