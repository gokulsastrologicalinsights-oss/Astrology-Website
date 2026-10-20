"""Pydantic schemas for Traditional Tamil Horoscope Writing Module."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class HoroscopeWritingRequest(BaseModel):
    """Request model for calculating traditional Tamil horoscope writing."""
    birth_input: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    person_name: Optional[str] = Field(default="Native", description="Name of the native")
    gender: Optional[str] = Field(default="male", description="Gender of the native")
    panchanga_system: str = Field(default="thirukanitha", description="Panchanga system: thirukanitha or vakkiya")
    ayanamsa_id: int = Field(default=0, description="Ayanamsa index: 0=Lahiri, 1=KP")
    house_system_id: int = Field(default=0, description="House system index: 0=Whole Sign")
    entrance_direction_basis: str = Field(default="rasi", description="Basis for entrance direction: rasi or lagna")
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Astrologer editable overrides")


class HoroscopeWritingResponse(BaseModel):
    """Response model containing all 6 pages of calculated traditional horoscope data."""
    metadata: Dict[str, Any]
    person_details: Dict[str, Any]
    page1_birth_details: Dict[str, Any]
    page2_dinasuthi: Dict[str, Any]
    page3_udumaka_dasa: Dict[str, Any]
    page4_kurippu: Dict[str, Any]
    page5_padupakshi: Dict[str, Any]
    page6_archana_slip: Dict[str, Any]
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HoroscopeWritingPdfRequest(BaseModel):
    """Request to generate and stream the 6-page traditional Tamil PDF."""
    birth_input: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    person_name: Optional[str] = "Native"
    gender: Optional[str] = "male"
    panchanga_system: str = "thirukanitha"
    ayanamsa_id: int = 0
    house_system_id: int = 0
    entrance_direction_basis: str = "rasi"
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # Alternatively, direct pre-calculated dictionary
    precalculated_data: Optional[Dict[str, Any]] = None


class HoroscopeWritingSaveRequest(BaseModel):
    """Request to persist generated horoscope writing document in database."""
    horoscope_id: Optional[str] = None
    person_name: str
    birth_date: str
    birth_time: str
    birth_place: Optional[str] = None
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"
    panchanga_system: str = "thirukanitha"
    calculated_data: Dict[str, Any]
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HoroscopeWritingSaveResponse(BaseModel):
    """Response returned upon saving a horoscope writing document."""
    success: bool
    id: str
    persistence_target: str
    message: str
    created_at: str


class SavedHoroscopeWritingItem(BaseModel):
    """Saved horoscope writing document item."""
    id: str
    user_id: str
    horoscope_id: Optional[str] = None
    person_name: str
    birth_date: str
    birth_time: str
    birth_place: Optional[str] = None
    latitude: float
    longitude: float
    timezone: str
    panchanga_system: str
    calculated_data: Dict[str, Any]
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: str
    updated_at: str
    persistence_target: Optional[str] = "supabase"


class SavedHoroscopeWritingListResponse(BaseModel):
    """Response containing list of saved horoscope writing documents."""
    success: bool
    count: int
    items: List[SavedHoroscopeWritingItem]


class HoroscopeWritingUpdateRequest(BaseModel):
    """Request to update an existing saved horoscope writing document."""
    person_name: Optional[str] = None
    birth_place: Optional[str] = None
    panchanga_system: Optional[str] = None
    calculated_data: Optional[Dict[str, Any]] = None
    overrides: Optional[Dict[str, Any]] = None
