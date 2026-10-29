"""Schemas for Life Partner & Spouse Nature, Character and Type Prediction.

Based on classical Vedic principles, BPHS (Kalatra Bhava), Phaladeepika Ch. 10,
Bhrigu Nandi Nadi, and comprehensive 4-step spouse astrology.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import BirthInput, CalculationMetadata


class SpousePlanetInfluence(BaseModel):
    """Influence of a planet in or aspecting the 7th house on spouse character."""
    planet: str
    planet_tamil: str
    status: str = Field(..., description="'OCCUPANT' or 'ASPECT'")
    influence_type: str
    influence_type_tamil: str
    spouse_type_en: str
    spouse_type_ta: str
    characteristics_en: List[str]
    characteristics_ta: List[str]
    positives_en: List[str]
    positives_ta: List[str]
    watchouts_en: List[str]
    watchouts_ta: List[str]


class SeventhLordElementalAnalysis(BaseModel):
    """Analysis of the 7th lord's placement and elemental temperament."""
    lord_planet: str
    lord_planet_tamil: str
    sign: str
    sign_tamil: str
    sign_number: int
    house_placement: int
    dignity: str
    dignity_tamil: str
    element: str = Field(..., description="'Fire', 'Earth', 'Air', or 'Water'")
    element_tamil: str
    elemental_traits_en: List[str]
    elemental_traits_ta: List[str]
    description_en: str
    description_ta: str


class SpouseSignAnalysis(BaseModel):
    """Baseline temperament determined by the zodiac sign of the 7th house."""
    sign: str
    sign_tamil: str
    sign_number: int
    ruler: str
    ruler_tamil: str
    temperament_en: str
    temperament_ta: str
    core_traits_en: List[str]
    core_traits_ta: List[str]


class DesireVsRealityAnalysis(BaseModel):
    """Classical comparison between Lagna 7th (Worldly Reality) and Moon 7th (Mind's Desire)."""
    lagna_sign: str
    lagna_sign_tamil: str
    seventh_from_lagna_sign: str
    seventh_from_lagna_sign_tamil: str
    reality_description_en: str
    reality_description_ta: str

    moon_sign: str
    moon_sign_tamil: str
    seventh_from_moon_sign: str
    seventh_from_moon_sign_tamil: str
    desire_description_en: str
    desire_description_ta: str

    synthesis_en: str
    synthesis_ta: str


class SpouseKarakasAnalysis(BaseModel):
    """Significators of marriage: Venus (Universal/Wife), Jupiter & Mars (Husband)."""
    venus_sign: str
    venus_sign_tamil: str
    venus_house: int
    venus_dignity: str
    venus_dignity_tamil: str
    venus_description_en: str
    venus_description_ta: str

    jupiter_sign: str
    jupiter_sign_tamil: str
    jupiter_house: int
    jupiter_dignity: str
    jupiter_dignity_tamil: str
    jupiter_description_en: str
    jupiter_description_ta: str

    mars_sign: str
    mars_sign_tamil: str
    mars_house: int
    mars_dignity: str
    mars_dignity_tamil: str
    mars_description_en: str
    mars_description_ta: str

    mars_venus_synergy_en: str
    mars_venus_synergy_ta: str
    gender_specific_insight_en: str
    gender_specific_insight_ta: str


class NavamsaD9SpouseProfile(BaseModel):
    """Spouse profile through Navamsa (D9) representing inner nature and enduring marriage reality."""
    d9_lagna_sign: str
    d9_lagna_sign_tamil: str
    d9_seventh_sign: str
    d9_seventh_sign_tamil: str
    d9_seventh_lord: str
    d9_seventh_lord_tamil: str
    d9_seventh_occupants: List[str] = Field(default_factory=list)
    inner_nature_en: str
    inner_nature_ta: str
    marital_bond_en: str
    marital_bond_ta: str


class SpouseTraitScores(BaseModel):
    """Quantitative and qualitative ratings of key partner dimensions."""
    romantic_loving_score: int = Field(..., ge=0, le=100)
    romantic_loving_analysis_en: str
    romantic_loving_analysis_ta: str

    loyalty_faithfulness_score: int = Field(..., ge=0, le=100)
    loyalty_faithfulness_analysis_en: str
    loyalty_faithfulness_analysis_ta: str

    intelligence_education_score: int = Field(..., ge=0, le=100)
    intelligence_education_analysis_en: str
    intelligence_education_analysis_ta: str

    physical_charm_score: int = Field(..., ge=0, le=100)
    physical_charm_analysis_en: str
    physical_charm_analysis_ta: str


class SpouseRemedies(BaseModel):
    """Astrological remedies, lifestyle, fasting and gemstones to strengthen marital harmony."""
    primary_gemstone_en: str
    primary_gemstone_ta: str
    fasting_day_en: str
    fasting_day_ta: str
    auspicious_colors_en: List[str]
    auspicious_colors_ta: List[str]
    mantra_en: str
    mantra_ta: str
    practical_advice_en: str
    practical_advice_ta: str


class SpousePredictionRequest(BaseModel):
    """Request payload for life partner and spouse prediction."""
    birth: BirthInput
    gender: Optional[str] = Field("male", description="'male', 'female', or 'other'")


class SpousePredictionResponse(BaseModel):
    """Complete structured response for Life Partner & Spouse Prediction."""
    native_gender: str
    ascendant_sign: str
    ascendant_sign_tamil: str
    moon_sign: str
    moon_sign_tamil: str

    seventh_sign: SpouseSignAnalysis
    seventh_lord: SeventhLordElementalAnalysis
    planets_in_seventh: List[SpousePlanetInfluence]
    aspecting_planets: List[SpousePlanetInfluence]

    desire_vs_reality: DesireVsRealityAnalysis
    karakas: SpouseKarakasAnalysis
    navamsa_d9: NavamsaD9SpouseProfile
    trait_scores: SpouseTraitScores
    remedies: SpouseRemedies

    summary_headline_en: str
    summary_headline_ta: str
    summary_text_en: str
    summary_text_ta: str

    metadata: CalculationMetadata
