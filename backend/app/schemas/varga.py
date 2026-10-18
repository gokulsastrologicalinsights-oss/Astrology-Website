"""Pydantic schemas for D1 Rasi and D9 Navamsa divisional charts."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class VargaPlanetPosition(BaseModel):
    """Detailed position of a planet across D1 (Rasi) and D9 (Navamsa) charts."""
    name: str = Field(..., description="Planet name (e.g. Sun, Moon, Mars)")
    body_id: int = Field(..., description="XALEN astronomical body ID")
    
    # D1 (Rasi Chakra)
    d1_longitude: float = Field(..., description="Absolute sidereal longitude [0, 360)")
    d1_sign_index: int = Field(..., ge=1, le=12, description="D1 sign index (1=Aries .. 12=Pisces)")
    d1_sign_name: str = Field(..., description="D1 English sign name")
    d1_sign_name_tamil: str = Field(..., description="D1 Tamil sign name")
    d1_degree_in_sign: float = Field(..., ge=0.0, lt=30.0, description="D1 degree within sign [0, 30)")
    d1_house: int = Field(..., ge=1, le=12, description="D1 whole-sign house relative to D1 Lagna (1-12)")
    d1_sign_lord: str = Field(..., description="Lord of the D1 sign")
    
    # D9 (Navamsa Chakra)
    d9_sign_index: int = Field(..., ge=1, le=12, description="D9 Navamsa sign index (1=Aries .. 12=Pisces)")
    d9_sign_name: str = Field(..., description="D9 English sign name")
    d9_sign_name_tamil: str = Field(..., description="D9 Tamil sign name")
    d9_degree_in_sign: float = Field(..., ge=0.0, lt=30.0, description="D9 degree within Navamsa sign [0, 30)")
    d9_house: int = Field(..., ge=1, le=12, description="D9 whole-sign house relative to D9 Navamsa Lagna (1-12)")
    d9_sign_lord: str = Field(..., description="Lord of the D9 sign")
    
    # Classical Dignities & Highlights
    is_vargottama: bool = Field(..., description="True if planet occupies identical sign in D1 and D9")
    is_pushkara_navamsa: bool = Field(..., description="True if placement falls in classical Pushkara Navamsa per Jataka Parijata Ch. 1")
    
    # Motion & Nakshatra
    is_retrograde: bool = Field(..., description="True if planet is in retrograde motion")
    speed_deg_per_day: float = Field(..., description="Signed daily motion speed in degrees/day")
    nakshatra_name: str = Field(..., description="Name of the Nakshatra")
    nakshatra_index: int = Field(..., ge=0, le=26, description="0-based Nakshatra index (0=Ashwini .. 26=Revati)")
    pada: int = Field(..., ge=1, le=4, description="Quarter/pada within Nakshatra (1-4)")
    star_lord: str = Field(..., description="Vimshottari ruler of the Nakshatra")


class VargaAscendantPosition(BaseModel):
    """Detailed position of Ascendant (Lagna) across D1 and D9 charts."""
    d1_degree: float = Field(..., description="Absolute sidereal Ascendant longitude [0, 360)")
    d1_sign_index: int = Field(..., ge=1, le=12, description="D1 sign index (1=Aries .. 12=Pisces)")
    d1_sign_name: str = Field(..., description="D1 English sign name")
    d1_sign_name_tamil: str = Field(..., description="D1 Tamil sign name")
    d1_degree_in_sign: float = Field(..., ge=0.0, lt=30.0, description="D1 degree within sign [0, 30)")
    d1_sign_lord: str = Field(..., description="Lord of the D1 Lagna sign")
    
    d9_sign_index: int = Field(..., ge=1, le=12, description="D9 Navamsa sign index (1=Aries .. 12=Pisces)")
    d9_sign_name: str = Field(..., description="D9 English sign name")
    d9_sign_name_tamil: str = Field(..., description="D9 Tamil sign name")
    d9_degree_in_sign: float = Field(..., ge=0.0, lt=30.0, description="D9 degree within Navamsa sign [0, 30)")
    d9_sign_lord: str = Field(..., description="Lord of the D9 Navamsa Lagna sign")
    
    is_vargottama: bool = Field(..., description="True if Ascendant occupies identical sign in D1 and D9")
    nakshatra_name: str = Field(..., description="Name of the Nakshatra")
    nakshatra_index: int = Field(..., ge=0, le=26, description="0-based Nakshatra index")
    pada: int = Field(..., ge=1, le=4, description="Quarter/pada within Nakshatra (1-4)")
    star_lord: str = Field(..., description="Vimshottari ruler of the Nakshatra")


class VargaChartSummary(BaseModel):
    """Summary metrics of D1 and D9 charts."""
    vargottama_planets: List[str] = Field(default_factory=list, description="Names of planets with Vargottama dignity")
    pushkara_navamsa_planets: List[str] = Field(default_factory=list, description="Names of planets in Pushkara Navamsa")
    total_vargottama_count: int = Field(..., description="Total count of Vargottama planets")
    d9_lagna_sign: str = Field(..., description="Navamsa Ascendant sign (English)")
    d9_lagna_sign_tamil: str = Field(..., description="Navamsa Ascendant sign (Tamil)")


class VargaD1D9Response(BaseModel):
    """Complete D1 Rasi and D9 Navamsa response payload with chart rendering structures."""
    metadata: CalculationMetadata
    ascendant: VargaAscendantPosition
    planets: List[VargaPlanetPosition]
    summary: VargaChartSummary
    d1_chart: Dict[str, Any] = Field(..., description="Standard format consumable by SouthIndianChart and NorthIndianChart")
    d9_chart: Dict[str, Any] = Field(..., description="Standard format consumable by SouthIndianChart and NorthIndianChart")


class VargaD1D9Request(BaseModel):
    """Request payload for D1/D9 calculation supporting both ad-hoc birth inputs and saved horoscopes."""
    saved_horoscope_id: Optional[str] = Field(None, description="Optional ID of saved horoscope to calculate D1/D9 from")
    
    # Optional ad-hoc birth input fields (required if saved_horoscope_id is not provided)
    birth_date: Optional[str] = Field(None, description="Birth date YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="Birth time HH:MM:SS")
    timezone: Optional[str] = Field("Asia/Kolkata", description="IANA timezone or offset")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    ayanamsa: int = Field(0, description="Ayanamsa ID (0=Lahiri, 1=KP)")
    house_system: int = Field(0, description="House System ID (0=WholeSign)")
