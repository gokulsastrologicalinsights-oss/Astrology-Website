"""Schemas for POST /api/v1/horoscope/kp."""

from typing import List, Dict, Any, Optional
from datetime import date, time
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class KpRequest(BirthInput):
    ayanamsa: int = Field(1, description="Ayanamsa ID (default 1 = KP Krishnamurti)")
    house_system: int = Field(2, description="House System ID (default 2 = Placidus)")


class PlanetaryKpPosition(BaseModel):
    planet: str
    body_id: int
    longitude: float
    sign_index: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    kp_number: int  # 1-249


class KpCuspDetail(BaseModel):
    house: int
    cusp_degree: float
    sign_index: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    promise: str  # Positive, Negative, Mixed
    sub_sub_lord: Optional[str] = None


class SignificatorStrengthEntry(BaseModel):
    house: int
    type: str  # StarLord, Occupant, Owner, Aspecting


class PlanetSignificator(BaseModel):
    planet: str
    signified_houses: List[int]
    strength_order: List[SignificatorStrengthEntry]


class HouseSignificatorEntry(BaseModel):
    house: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    level_a: List[str]  # Planets in star of occupants (strongest)
    level_b: List[str]  # House occupants
    level_c: List[str]  # Planets in star of house lord
    level_d: List[str]  # House sign lord
    all_significators: List[str]  # Unique significators ordered by strength (A -> B -> C -> D)


class RulingPlanetEntry(BaseModel):
    role: str
    planet: str


class RulingPlanetsDetail(BaseModel):
    day_lord: str
    ascendant_sign_lord: str
    ascendant_star_lord: str
    ascendant_sub_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    moon_sub_lord: str
    ruling_planets_list: List[str]
    details: List[RulingPlanetEntry]


class KpDasaPeriod(BaseModel):
    level: int           # 1 (MD), 2 (AD), 3 (PD), 4 (SD), 5 (PrD)
    level_name: str      # Mahadasha, Antardasha, Pratyantardasha, Sookshmadasha, Pranadasha
    vedic_name: str      # Dasa, Bhukti, Andharam, Soochamam, Pranam
    lord: str
    start_date: str      # ISO format
    end_date: str        # ISO format
    duration_days: float


class KpDasaBalance(BaseModel):
    birth_epoch: str
    mahadasha_lord: str
    mahadasha_balance_years: float
    mahadasha_balance_days: float
    antardasha_lord: str
    antardasha_balance_days: float
    pratyantardasha_lord: str
    pratyantardasha_balance_days: float
    sookshmadasha_lord: str
    sookshmadasha_balance_days: float
    pranadasha_lord: str
    pranadasha_balance_days: float
    current_periods: List[KpDasaPeriod]
    mahadashas: List[KpDasaPeriod]


class KpResponse(BaseModel):
    metadata: CalculationMetadata
    planetary_positions: List[PlanetaryKpPosition]
    cuspal_analysis: List[KpCuspDetail]
    significators: List[PlanetSignificator]
    house_significators: Optional[List[HouseSignificatorEntry]] = None
    ruling_planets: Optional[RulingPlanetsDetail] = None
    dasa_hierarchy: Optional[KpDasaBalance] = None


class HoraryKpRequest(BaseModel):
    horary_number: int = Field(..., ge=1, le=249, description="Horary query number (1-249)")
    question_text: Optional[str] = Field(None, description="Querent question or consultation label")
    question_date: date = Field(..., description="Date of question (YYYY-MM-DD)")
    question_time: time = Field(..., description="Exact local time of question (HH:MM or HH:MM:SS)")
    timezone: str = Field(..., description="IANA timezone name, e.g. Asia/Kolkata")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of the query location")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of the query location")
    location_name: Optional[str] = Field(None, description="Location name / city")
    ayanamsa: int = Field(1, description="Ayanamsa ID (default 1 = KP Krishnamurti)")
    house_system: int = Field(2, description="House System ID (default 2 = Placidus)")


class HoraryDivisionDetail(BaseModel):
    number: int
    start_degree: float
    end_degree: float
    mid_degree: float
    sign: str
    sign_lord: str
    star: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    pada: int


class HoraryKpResponse(BaseModel):
    metadata: CalculationMetadata
    horary_number: int
    horary_division: HoraryDivisionDetail
    question_text: Optional[str] = None
    question_datetime: str
    location_name: Optional[str] = None
    ascendant_degree: float
    planetary_positions: List[PlanetaryKpPosition]
    cuspal_analysis: List[KpCuspDetail]
    significators: List[PlanetSignificator]
    house_significators: List[HouseSignificatorEntry]
    ruling_planets: RulingPlanetsDetail
    dasa_hierarchy: Optional[KpDasaBalance] = None


class SaveKpChartRequest(BaseModel):
    chart_type: str = Field("natal", description="'natal' or 'horary'")
    title: str = Field(..., min_length=1, description="Chart title or querent label")
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    horary_number: Optional[int] = Field(None, ge=1, le=249)
    question_text: Optional[str] = None
    question_date: Optional[str] = None
    question_time: Optional[str] = None
    location_name: str = Field("Unknown Location", min_length=1)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    timezone: str = Field(..., min_length=1)
    ayanamsa_id: int = Field(1, description="1 = KP, 0 = Lahiri")
    house_system_id: int = Field(2, description="2 = Placidus")
    calculation_result: Dict[str, Any] = Field(..., description="Full calculation snapshot")
    saved_horoscope_id: Optional[str] = None


class SavedKpChartItem(BaseModel):
    id: str
    user_id: str
    display_number: int
    chart_type: str
    title: str
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    horary_number: Optional[int] = None
    question_text: Optional[str] = None
    question_date: Optional[str] = None
    question_time: Optional[str] = None
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    ayanamsa_id: int
    house_system_id: int
    engine_version: str
    calculation_result: Dict[str, Any]
    saved_horoscope_id: Optional[str] = None
    created_at: str
    updated_at: str


class SavedKpChartListResponse(BaseModel):
    charts: List[SavedKpChartItem]
    total_count: int



