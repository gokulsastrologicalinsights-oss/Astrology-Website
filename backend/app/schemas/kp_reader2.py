"""Pydantic schemas for KP Reader 2 (Fundamental Principles) endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SignClassificationSchema(BaseModel):
    sign: str
    polarity: str
    gender: str
    hemisphere: str
    cardinality_type: str
    element: str
    mobility: str
    guna: str
    fertility: str
    speech_type: str
    is_violent: bool
    is_human: bool
    is_bestial: bool
    is_dual: bool
    is_bicorporal: bool
    ascension_north: str
    ascension_south: str


class SignSignificationSchema(BaseModel):
    sign_name: str
    sanskrit_name: str
    symbol: str
    start_degree: float
    end_degree: float
    ruling_planet: str
    exaltation_planet: Optional[str] = None
    debilitation_planet: Optional[str] = None
    detriment_planet: Optional[str] = None
    constellations_included: List[str]
    physical_appearance: str
    mental_tendencies: str
    characteristics: str
    health_and_diseases: List[str]
    body_parts: List[str]
    finance_and_fortune: str
    romance_and_marriage: str
    ideal_partner_signs: List[str]
    domestic_environments: str
    professions: List[str]
    places: List[str]
    direction: str
    products: List[str]
    countries_and_cities: List[str]
    handwriting: str
    lucky_days: List[str]
    lucky_numbers: List[int]
    lucky_stones: List[str]
    lucky_colors: List[str]


class HouseSignificationSchema(BaseModel):
    house: int
    sanskrit_name: str
    primary_matters: List[str]
    anatomical_parts: List[str]
    relatives_signified: List[str]
    favorable_conjunctions: List[str]
    unfavorable_conjunctions: List[str]
    karakas: List[str]
    detailed_signification: str


class PlanetSignificationSchema(BaseModel):
    planet: str
    sanskrit_name: str
    nature: str
    gender: str
    governs_body_parts: List[str]
    pathology_and_diseases: List[str]
    mental_qualities: List[str]
    professions: List[str]
    places: List[str]
    products_and_minerals: List[str]
    lucky_day: str
    lucky_numbers: List[int]
    lucky_stone: str
    lucky_color: str
    kp_special_doctrine: str


class AstrologerAptitudeRequest(BaseModel):
    mercury_sign: str = Field(..., description="Zodiac sign of natal Mercury")
    moon_sign: str = Field(..., description="Zodiac sign of natal Moon")
    uranus_sign: Optional[str] = Field(None, description="Zodiac sign of Uranus")
    saturn_sign: Optional[str] = Field(None, description="Zodiac sign of Saturn")
    jupiter_sign: Optional[str] = Field(None, description="Zodiac sign of Jupiter")
    mars_sign: Optional[str] = Field(None, description="Zodiac sign of Mars")
    ascendant_sign: Optional[str] = Field(None, description="Zodiac sign of Ascendant (Lagna)")
    mercury_house: Optional[int] = Field(None, ge=1, le=12, description="House containing Mercury (1-12)")
    moon_house: Optional[int] = Field(None, ge=1, le=12, description="House containing Moon (1-12)")
    jupiter_house: Optional[int] = Field(None, ge=1, le=12, description="House containing Jupiter (1-12)")
    saturn_house: Optional[int] = Field(None, ge=1, le=12, description="House containing Saturn (1-12)")
    uranus_house: Optional[int] = Field(None, ge=1, le=12, description="House containing Uranus (1-12)")
    is_moon_mercury_aspect: bool = Field(False, description="Whether Moon and Mercury form harmonious aspect")
    is_saturn_mercury_aspect: bool = Field(False, description="Whether Saturn and Mercury form harmonious aspect")
    is_jupiter_mercury_aspect: bool = Field(False, description="Whether Jupiter and Mercury form harmonious aspect")
    is_uranus_mercury_aspect: bool = Field(False, description="Whether Uranus and Mercury form harmonious aspect")


class AstrologerAptitudeResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    aptitude_grade: str
    factors_present: List[str]
    recommendations: List[str]
    reasons: List[str]


class SpeechFertilityRequest(BaseModel):
    cusp_2_sign: str = Field(..., description="Sign on 2nd cusp (Vocal organs)")
    cusp_5_sign: str = Field(..., description="Sign on 5th cusp (Children)")
    cusp_11_sign: str = Field(..., description="Sign on 11th cusp (Fulfillment of children)")
    mercury_sign: Optional[str] = None
    mercury_afflicted_by_saturn_mars: bool = False
    planets_in_5th: Optional[List[str]] = None
    planets_in_11th: Optional[List[str]] = None


class SpeechFertilityResponse(BaseModel):
    speech_condition: str
    speech_reasons: List[str]
    fertility_promise: str
    fertility_reasons: List[str]


class KarmaEvaluationRequest(BaseModel):
    lagna_aspect_from_jupiter_or_9th_lord: bool = False
    moon_aspect_from_jupiter_or_9th_lord: bool = False
    dasa_lord_aspect_from_jupiter_or_9th_lord: bool = False
    jupiter_or_9th_lord_in_lagna_or_moon: bool = False


class KarmaEvaluationResponse(BaseModel):
    karma_type: str
    severity_level: str
    mitigation_potential: str
    chart_indications: List[str]
    philosophical_counsel: str


class FortunaRequest(BaseModel):
    ascendant_deg: float = Field(..., ge=0.0, le=360.0, description="Ascendant longitude in degrees")
    moon_deg: float = Field(..., ge=0.0, le=360.0, description="Moon longitude in degrees")
    sun_deg: float = Field(..., ge=0.0, le=360.0, description="Sun longitude in degrees")
    is_day_birth: bool = Field(True, description="True if Sun is above horizon (day birth), False if night birth")


class FortunaResponse(BaseModel):
    longitude: float
    sign: str
    sign_lord: str
    star: str
    star_lord: str
    sub_lord: str
    is_day_birth: bool
    formula_used: str
    signification: str
