"""Schemas for POST /api/v1/horoscope/dasa."""

from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.horoscope import NakshatraDetail


class DasaRequest(BirthInput):
    depth: int = Field(2, ge=1, le=5, description="Nesting depth (1=Maha, 2=Antar, 3=Pratyantar, 4=Sookshma, 5=Prana)")
    ayanamsa: int = Field(0, description="Ayanamsa ID for sidereal Moon calculation (default 0 = Lahiri)")
    house_system: int = Field(0, description="House System ID (default 0 = WholeSign)")
    target_date: Optional[date] = Field(None, description="Optional target date to query currently active Dasa-Bhukti path")


class DirectDasaRequest(BaseModel):
    """Calculate Dasa directly from known Moon longitude and Julian Day."""
    moon_sidereal_deg: float = Field(..., ge=0.0, lt=360.0, description="Moon's sidereal longitude in degrees [0, 360)")
    birth_jd: float = Field(..., description="Julian Day of birth (UT1)")
    depth: int = Field(2, ge=1, le=5, description="Hierarchy depth (1 to 5)")
    target_date: Optional[date] = Field(None, description="Optional date to find active period")


class DasaPeriodNode(BaseModel):
    lord: str
    level: str
    start_jd: float
    end_jd: float
    duration_days: float
    duration_years: float
    start_date_iso: Optional[str] = None
    end_date_iso: Optional[str] = None
    start_age: Optional[str] = None
    end_age: Optional[str] = None
    start_age_dict: Optional[Dict[str, int]] = None
    end_age_dict: Optional[Dict[str, int]] = None
    star_lord: Optional[str] = None
    benefit_bhavas: Optional[str] = None
    period_lord_occupied: Optional[int] = None
    star_lord_occupied: Optional[int] = None
    period_lord_owned: List[int] = Field(default_factory=list)
    star_lord_owned: List[int] = Field(default_factory=list)
    sub_periods: List["DasaPeriodNode"] = Field(default_factory=list)


DasaPeriodNode.model_rebuild()


class ActivePeriodPath(BaseModel):
    mahadasha: str
    antardasha: Optional[str] = None
    pratyantardasha: Optional[str] = None
    sookshmadasha: Optional[str] = None
    pranadasha: Optional[str] = None
    target_jd: float
    target_date_iso: str
    target_age: Optional[str] = None
    target_age_dict: Optional[Dict[str, int]] = None


class DasaResponse(BaseModel):
    metadata: CalculationMetadata
    moon_sidereal_deg: float
    nakshatra: NakshatraDetail
    birth_dasa_lord: str
    birth_balance_years: float
    birth_balance_formatted: str
    dasa_tree: List[DasaPeriodNode]
    active_period: Optional[ActivePeriodPath] = None
