"""Schemas for Instant KP Horary / Prashna (1-249) Automated Event Predictor."""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.kp import HoraryDivisionDetail, PlanetaryKpPosition, KpCuspDetail


class OutcomeVerdict(str, Enum):
    YES = "YES"             # Promised / காரிய சித்தி உண்டு
    DELAYED = "DELAYED"     # With Effort / தாமதத்துடன் சித்தி
    NO = "NO"               # Denied / சாதகமற்றது


class HoraryTopicInfo(BaseModel):
    id: str
    name_en: str
    name_ta: str
    sample_query_en: str
    sample_query_ta: str
    category: str
    primary_cusp: int
    supporting_houses: List[int]
    denying_houses: List[int]
    icon: Optional[str] = None


class InstantHoraryPredictionRequest(BaseModel):
    horary_number: int = Field(..., ge=1, le=249, description="Querent seed number between 1 and 249")
    question_topic: str = Field(..., description="Topic identifier (e.g., 'visa', 'job', 'court_case', 'marriage', etc.) or custom question")
    question_text: Optional[str] = Field(None, description="Querent specific question text, e.g. 'Will I get this visa?'")
    question_date: Optional[str] = Field(None, description="Date of query (YYYY-MM-DD), defaults to current date")
    question_time: Optional[str] = Field(None, description="Local time of query (HH:MM or HH:MM:SS), defaults to current time")
    timezone: str = Field("Asia/Kolkata", description="IANA timezone name, e.g. 'Asia/Kolkata'")
    latitude: float = Field(13.0827, ge=-90.0, le=90.0, description="Latitude of query location")
    longitude: float = Field(80.2707, ge=-180.0, le=180.0, description="Longitude of query location")
    location_name: Optional[str] = Field("Chennai, India", description="Location name or city")
    ayanamsa: int = Field(1, description="Ayanamsa ID (1 = KP Krishnamurti, 0 = Lahiri)")


class TimingWindow(BaseModel):
    dasha_mahadasha: str
    dasha_bhukti: str
    dasha_antara: str
    dasha_window_start: str
    dasha_window_end: str
    moon_transit_star: str
    moon_transit_star_ta: str
    moon_transit_sign: str
    moon_transit_sign_ta: str
    moon_transit_lord: str
    moon_transit_lord_ta: str
    moon_transit_start: str
    moon_transit_end: str
    summary_en: str
    summary_ta: str


class AstrologicalExplanation(BaseModel):
    summary_en: str
    summary_ta: str
    primary_cusp_analysis_en: str
    primary_cusp_analysis_ta: str
    csl_connection_en: str
    csl_connection_ta: str
    ruling_planets_en: str
    ruling_planets_ta: str
    timing_explanation_en: str
    timing_explanation_ta: str


class InstantHoraryPredictionResponse(BaseModel):
    horary_number: int
    horary_division: HoraryDivisionDetail
    question_topic: str
    question_text: str
    query_timestamp: str
    location_name: str
    
    # Primary Cusp & CSL Details
    primary_cusp: int
    primary_cusp_name_en: str
    primary_cusp_name_ta: str
    supporting_houses: List[int]
    denying_houses: List[int]
    cusp_sub_lord: str
    cusp_sub_lord_ta: str
    cusp_star_lord: str
    cusp_star_lord_ta: str
    cusp_sub_sub_lord: Optional[str] = None
    cusp_longitude: float
    csl_signified_houses: List[int]
    supporting_hits: List[int]
    denying_hits: List[int]
    is_csl_retrograde: bool
    is_star_lord_retrograde: bool
    
    # Verdict Card Data
    outcome: OutcomeVerdict
    outcome_label_en: str
    outcome_label_ta: str
    outcome_badge: str  # "success" | "warning" | "danger"
    confidence_score: int  # 0 to 100
    
    # Ruling Planets
    ruling_planets: List[str]
    rp_matching_planets: List[str]
    rp_agreement: bool
    
    # Timing of Fructification
    timing: TimingWindow
    
    # Dual-Language Explanations
    explanation: AstrologicalExplanation
    
    # Full Horary Chart Snapshot
    ascendant_degree: float
    planetary_positions: List[PlanetaryKpPosition]
    cuspal_analysis: List[KpCuspDetail]
