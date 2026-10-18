"""Schemas for POST /api/v1/horoscope/calculate."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


from app.schemas.nabhasha import NabhashaResponse
from app.schemas.ashtakavarga import AshtakavargaResponse
from app.schemas.yoga import VedicYogaResponse


class HoroscopeRequest(BirthInput):
    ayanamsa: int = Field(0, description="Ayanamsa ID (0=Lahiri, 1=KP, 2=Raman, etc.)")
    house_system: int = Field(0, description="House System ID (0=WholeSign, 1=Equal, 2=Placidus, etc.)")
    include_panchang: bool = Field(True, description="Compute five limbs of birth Panchang")
    include_outer_planets: bool = Field(True, description="Include Uranus, Neptune, and Pluto")
    include_nabhasha: bool = Field(True, description="Compute classical Nabhasha Yogas per BPHS Ch. 35")
    include_ashtakavarga: bool = Field(True, description="Compute classical Ashtakavarga BAV/SAV and Shodhana per BPHS Ch. 66-69")
    include_vedic_yogas: bool = Field(True, description="Compute classical Vedic Yogas (Gajakesari, Raja, Dhana, Mahapurusha, etc.)")
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female') for gender-specific yogas")


class NakshatraDetail(BaseModel):
    name: str
    index: int
    pada: int
    lord: str
    deity: str


class PlanetInfo(BaseModel):
    name: str
    body_id: int
    longitude: float
    latitude: float
    distance_au: float
    speed_deg_per_day: float
    is_retrograde: bool
    sign_index: int       # 1-12 (1=Aries .. 12=Pisces)
    sign_name: str
    sign_name_tamil: str
    degree_in_sign: float # 0.0 to 30.0
    nakshatra: NakshatraDetail


class HouseInfo(BaseModel):
    house_number: int     # 1-12
    cusp_degree: float    # 0.0 to 360.0
    sign_index: int       # 1-12
    sign_name: str
    sign_name_tamil: str
    degree_in_sign: float
    nakshatra: str
    pada: int
    star_lord: str


class AscendantInfo(BaseModel):
    degree: float
    sign_index: int
    sign_name: str
    sign_name_tamil: str
    degree_in_sign: float
    nakshatra: NakshatraDetail


class TithiInfo(BaseModel):
    number: int
    name: str
    paksha: str


class YogaInfo(BaseModel):
    number: int
    name: str


class PanchangInfo(BaseModel):
    tithi: TithiInfo
    nakshatra: str
    yoga: YogaInfo
    karana: str
    vara: str  # Weekday name (e.g. Ravivara, Somavara)


class HoroscopeResponse(BaseModel):
    metadata: CalculationMetadata
    ascendant: AscendantInfo
    midheaven: AscendantInfo
    planets: List[PlanetInfo]
    houses: List[HouseInfo]
    panchang: Optional[PanchangInfo] = None
    nabhasha_yogas: Optional[NabhashaResponse] = None
    ashtakavarga: Optional[AshtakavargaResponse] = None
    vedic_yogas: Optional[VedicYogaResponse] = None
