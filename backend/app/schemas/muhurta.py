"""Pydantic schemas for Muhurta and Panchanga endpoints."""

from typing import List, Dict, Any, Optional
from datetime import date as dt_date, datetime as dt_datetime
from pydantic import BaseModel, Field


class PanchangRequest(BaseModel):
    date: dt_date = Field(..., description="Date for calculation in YYYY-MM-DD")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Observer geographic latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Observer geographic longitude")
    timezone: str = Field(default="Asia/Kolkata", description="IANA Timezone Identifier")
    ayanamsa_id: int = Field(default=0, ge=0, le=20, description="Ayanamsa ID (0=Lahiri, 1=KP)")


class FindMuhurtaRequest(BaseModel):
    occasion_code: str = Field(..., min_length=2, description="Occasion identifier (e.g. marriage, griha_pravesham)")
    start_date: dt_date = Field(..., description="Search range start date")
    end_date: dt_date = Field(..., description="Search range end date")
    latitude: float = Field(default=13.0827, ge=-90.0, le=90.0)
    longitude: float = Field(default=80.2707, ge=-180.0, le=180.0)
    location_name: str = Field(default="Chennai, Tamil Nadu, India")
    timezone: str = Field(default="Asia/Kolkata")
    preferred_time_range: str = Field(default="morning", description="morning, afternoon, evening, all_day")
    ayanamsa_id: int = Field(default=0)
    tradition: str = Field(default="south_indian")
    custom_rules: Optional[Dict[str, Any]] = None
    birth_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional native/groom/bride birth star (1..27) and moon sign (1..12)",
    )
    limit: int = Field(default=50, ge=1, le=200)


class CandidateSlot(BaseModel):
    id: str
    event_date: str
    weekday: str
    weekday_ta: str
    start_time_local: str
    end_time_local: str
    start_time_utc: str
    end_time_utc: str
    duration_minutes: int
    status: str
    score: int
    explanation: str
    passed_rules: List[Dict[str, Any]]
    failed_rules: List[Dict[str, Any]]
    advisories: List[Dict[str, Any]]
    incomplete_checks: List[Dict[str, Any]]
    tithi: Dict[str, Any]
    nakshatra: Dict[str, Any]
    yoga: Dict[str, Any]
    karana: Dict[str, Any]
    ascendant: Dict[str, Any]
    planets: Dict[str, Any]
    inauspicious_periods: Dict[str, Any]
    auspicious_periods: Dict[str, Any]


class FindMuhurtaResponse(BaseModel):
    occasion: Dict[str, Any]
    search_params: Dict[str, Any]
    total_candidates: int
    candidates: List[CandidateSlot]
    calendar_summary: Dict[str, Any]


class SaveMuhurtaRequest(BaseModel):
    title: Optional[str] = None
    occasion_code: str
    occasion_name: str
    event_date: str
    start_time: str
    end_time: str
    local_start_time: str
    local_end_time: str
    duration_minutes: int = 45
    location_name: str
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"
    ayanamsa_id: int = 0
    tradition: str = "south_indian"
    score: int = 80
    status: str = "meets_configured_rules"
    panchang_summary: Dict[str, Any]
    lagna_summary: Dict[str, Any]
    rule_evaluations: Dict[str, Any]
    birth_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    client_name: Optional[str] = None


class UpdateSavedMuhurtaRequest(BaseModel):
    title: Optional[str] = None
    client_name: Optional[str] = None
    notes: Optional[str] = None


class SavedMuhurtaItem(BaseModel):
    id: str
    user_id: str
    display_number: int
    title: str
    occasion_code: str
    occasion_name: str
    event_date: str
    start_time: str
    end_time: str
    local_start_time: str
    local_end_time: str
    duration_minutes: int
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    ayanamsa_id: int
    tradition: str
    score: int
    status: str
    panchang_summary: Dict[str, Any]
    lagna_summary: Dict[str, Any]
    rule_evaluations: Dict[str, Any]
    birth_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    client_name: Optional[str] = None
    created_at: str
    updated_at: str


class SavedMuhurtaListResponse(BaseModel):
    count: int
    items: List[SavedMuhurtaItem]


class CustomOccasionRequest(BaseModel):
    code: str = Field(..., min_length=2)
    name_en: str = Field(..., min_length=2)
    name_ta: Optional[str] = None
    category: str = Field(default="custom")
    description_en: Optional[str] = None
    description_ta: Optional[str] = None
    icon: str = Field(default="Sparkles")
    rules: Optional[Dict[str, Any]] = None
