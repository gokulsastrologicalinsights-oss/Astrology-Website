"""Pydantic schemas for KP Reader 3 (Predictive Stellar Astrology) endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class Kp249DivisionSchema(BaseModel):
    """Schema representing one of the 249 KP sub-divisions."""
    number: int = Field(..., ge=1, le=249, description="KP division number (1-249)")
    sign: str = Field(..., description="Zodiac sign name")
    sign_lord: str = Field(..., description="Ruler of the zodiac sign")
    star: str = Field(..., description="Nakshatra (constellation) name")
    star_lord: str = Field(..., description="Vimshottari ruler of the constellation")
    sub_lord: str = Field(..., description="KP Sub-Lord planet")
    start_deg: float = Field(..., description="Absolute start longitude in degrees (0-360)")
    end_deg: float = Field(..., description="Absolute end longitude in degrees (0-360)")
    sign_start_deg: float = Field(..., description="Sign-relative start degree (0-30)")
    sign_end_deg: float = Field(..., description="Sign-relative end degree (0-30)")
    start_dms: str = Field(..., description="Absolute start longitude formatted as D°MM'SS\"")
    end_dms: str = Field(..., description="Absolute end longitude formatted as D°MM'SS\"")
    sign_start_dms: str = Field(..., description="Sign-relative start formatted as D°MM'SS\"")
    sign_end_dms: str = Field(..., description="Sign-relative end formatted as D°MM'SS\"")
    span_arcmin: float = Field(..., description="Span of this sub in arc-minutes")
    body_parts: str = Field(..., description="Anatomical areas ruled per KP Reader 3")
    diseases: List[str] = Field(default_factory=list, description="Medical/pathological vulnerabilities")
    mental_qualities: str = Field(..., description="Psychological and mental temperament")
    professions: List[str] = Field(default_factory=list, description="Suitable careers and vocations")


class Kp249TableResponse(BaseModel):
    """Response containing 249 table divisions."""
    total_divisions: int = Field(249, description="Total count of divisions (always 249)")
    divisions: List[Kp249DivisionSchema] = Field(..., description="List of 249 KP sub-divisions")


class CuspalSubLordItemSchema(BaseModel):
    """KP analysis of a single house cusp and its Sub-Lord."""
    house: int = Field(..., ge=1, le=12, description="House cusp number (1-12)")
    longitude: float = Field(..., description="Sidereal longitude in degrees")
    longitude_dms: str = Field(..., description="Sidereal longitude in D°MM'SS\"")
    sign: str = Field(..., description="Sign containing the cusp")
    sign_lord: str = Field(..., description="Sign Lord (Ownership)")
    star: str = Field(..., description="Constellation containing the cusp")
    star_lord: str = Field(..., description="Star Lord (Primary Event Indicator)")
    sub_lord: str = Field(..., description="Sub-Lord (Decisive Arbiter of the Bhava)")
    sub_sub_lord: str = Field(..., description="Sub-sub-lord")
    pada: int = Field(..., ge=1, le=4, description="Pada (Quarter) 1-4")
    division_249_number: int = Field(..., ge=1, le=249, description="KP 249 division number")
    division_span_dms: str = Field(..., description="Division start and end DMS")
    promise: str = Field(..., description="Evaluated cuspal promise: Positive, Negative, or Mixed")
    favorable_houses: List[int] = Field(default_factory=list, description="Houses favorable for this Bhava")
    unfavorable_houses: List[int] = Field(default_factory=list, description="Houses unfavorable for this Bhava")
    reader3_ruling: str = Field(..., description="KP Reader 3 analytical commentary")
    sub_significations: Dict[str, Any] = Field(default_factory=dict, description="Medical and vocational profile")


class CuspalSubLordsRequest(BaseModel):
    """Request to compute Cuspal Sub-Lords."""
    cusp_longitudes: Optional[List[float]] = Field(None, min_length=12, max_length=12, description="12 sidereal cusp longitudes")
    birth: Optional[BirthInput] = Field(None, description="Optional birth details to calculate Placidus cusps")
    planet_significators: Optional[Dict[str, List[int]]] = Field(None, description="Optional planet -> signified houses map")


class CuspalSubLordsResponse(BaseModel):
    """Response containing 12 Cuspal Sub-Lords analysis."""
    cuspal_sub_lords: List[CuspalSubLordItemSchema] = Field(..., description="12 Cuspal Sub-Lords")
    calculation_notes: str = Field(..., description="KP Reader 3 cuspal doctrine explanation")


class PlanetarySubLordItemSchema(BaseModel):
    """KP analysis of a planet's sub-lord agency and 3-tier decomposition."""
    planet: str = Field(..., description="Graha name (Sun, Moon, etc.)")
    longitude: float = Field(..., description="Sidereal longitude in degrees")
    longitude_dms: str = Field(..., description="Sidereal longitude in D°MM'SS\"")
    house: int = Field(..., ge=1, le=12, description="House occupied (1-12)")
    sign: str = Field(..., description="Zodiac sign occupied")
    sign_lord: str = Field(..., description="Sign Lord")
    star: str = Field(..., description="Nakshatra occupied")
    star_lord: str = Field(..., description="Star Lord")
    sub_lord: str = Field(..., description="Sub-Lord")
    sub_sub_lord: str = Field(..., description="Sub-Sub-Lord")
    pada: int = Field(..., ge=1, le=4, description="Pada (Quarter) 1-4")
    division_249_number: int = Field(..., ge=1, le=249, description="KP 249 division number")
    division_span_dms: str = Field(..., description="Division span DMS")
    source_planet: str = Field(..., description="Tier 1: Planet as Source of light / Instrument")
    nature_star_lord: str = Field(..., description="Tier 2: Star Lord governing the Nature of Result")
    decision_sub_lord: str = Field(..., description="Tier 3: Sub-Lord as the Decisive Qualifier")
    star_houses_for_lagna: List[int] = Field(default_factory=list, description="Houses owned by star lord for this Lagna")
    sub_significations: Dict[str, Any] = Field(default_factory=dict, description="Medical and vocational profile")
    reader3_interpretation: str = Field(..., description="KP Reader 3 predictive synthesis")


class PlanetarySubLordsRequest(BaseModel):
    """Request to compute Planetary Sub-Lords."""
    planet_positions: Optional[Dict[str, float]] = Field(None, description="Mapping of planet -> sidereal longitude")
    cusp_longitudes: Optional[List[float]] = Field(None, description="Optional 12 house cusp longitudes")
    lagna_sign: Optional[str] = Field(None, description="Optional Lagna sign name (e.g. 'Aries', 'Leo')")
    birth: Optional[BirthInput] = Field(None, description="Optional birth details to calculate planetary positions")


class PlanetarySubLordsResponse(BaseModel):
    """Response containing planetary sub-lords analysis."""
    lagna_sign: str = Field(..., description="Lagna sign considered")
    planetary_sub_lords: Dict[str, PlanetarySubLordItemSchema] = Field(..., description="Planetary sub-lord profiles")
    three_tier_doctrine: str = Field(..., description="Summary of the 3-Tier KP Agency doctrine")


class TwinDivergenceRequest(BaseModel):
    """Request to analyze twin birth divergence via KP Sub-Lord mechanics."""
    lagna1_deg: float = Field(..., description="Sidereal Ascendant degree of Twin 1 (0-360)")
    lagna2_deg: float = Field(..., description="Sidereal Ascendant degree of Twin 2 (0-360)")


class TwinDivergenceResponse(BaseModel):
    """Response demonstrating how changing sub-lords explain twin divergence."""
    lagna1_deg: float
    lagna2_deg: float
    twin1_sub_lord: str
    twin2_sub_lord: str
    twin1_div_number: int
    twin2_div_number: int
    twin1_professions: List[str]
    twin2_professions: List[str]
    twin1_medical: List[str]
    twin2_medical: List[str]
    reader3_explanation: str


class LagnaStarSignificationResponse(BaseModel):
    """Response containing Reader 3 star significations for a Lagna."""
    lagna: str = Field(..., description="Lagna sign name")
    star_significations: Dict[str, Dict[str, Any]] = Field(..., description="Star lord -> houses owned and nature")
