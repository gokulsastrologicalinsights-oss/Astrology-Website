"""Pydantic schemas for Double Transit ('Guru-Shani') Event Timing Radar."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class DoubleTransitDomainConfig(BaseModel):
    """Configuration for an event domain."""
    id: str
    name_en: str
    name_ta: str
    target_house: int
    facilitating_houses: List[int]
    karakas: List[str]
    description: str


class DoubleTransitRequest(BirthInput):
    """Request payload for Double Transit Event Timing Radar."""
    domain: str = Field(
        "marriage",
        description="Life event domain: marriage, career, childbirth, wealth, property, foreign, health"
    )
    forecast_years: int = Field(
        3,
        ge=1,
        le=5,
        description="Forecast horizon in years (1 to 5 years, default 3)"
    )
    include_rahu: bool = Field(
        True,
        description="Whether to also evaluate Rahu's catalytic transit aspect"
    )
    ayanamsa: int = Field(1, description="Ayanamsa ID (1 = KP, 0 = Lahiri)")


class DoubleTransitWindow(BaseModel):
    """A distinct time window with planetary transit alignment."""
    start_date: str
    end_date: str
    duration_months: float

    # Planetary Positions & Aspects
    saturn_transit_sign: str
    saturn_transit_sign_index: int
    saturn_aspects_target: bool
    saturn_occupies_target: bool
    saturn_aspect_type: str  # "Occupation", "3rd Aspect", "7th Aspect", "10th Aspect", "None"

    jupiter_transit_sign: str
    jupiter_transit_sign_index: int
    jupiter_aspects_target: bool
    jupiter_occupies_target: bool
    jupiter_aspect_type: str  # "Occupation", "5th Aspect", "7th Aspect", "9th Aspect", "None"

    double_transit_active: bool

    rahu_transit_sign: Optional[str] = None
    rahu_transit_sign_index: Optional[int] = None
    rahu_activates_target: Optional[bool] = None

    # Dasa Alignment
    running_mahadasha: str
    running_antardasha: str
    dasa_confirms_event: bool
    dasa_connection_details: str

    # Scoring & Status
    alignment_level: str  # "Peak Alignment (Guru-Shani + Dasa)", "High (Double Transit Active)", "Moderate", "Dormant"
    probability_percentage: int
    astrological_rationale: str
    astrological_rationale_ta: str


class PlanetaryTransitSummary(BaseModel):
    """Overview of slow-moving transit positions at the start of analysis."""
    saturn_sign: str
    saturn_degree: float
    jupiter_sign: str
    jupiter_degree: float
    rahu_sign: str
    rahu_degree: float


class DoubleTransitResponse(BaseModel):
    """Complete Double Transit Radar response."""
    metadata: Optional[CalculationMetadata] = None
    domain: DoubleTransitDomainConfig
    target_house: int
    target_house_lord: str
    natal_lagna_sign: str
    natal_lagna_sign_index: int
    analysis_start_date: str
    analysis_end_date: str
    current_transits: PlanetaryTransitSummary
    windows: List[DoubleTransitWindow]
    peak_windows: List[DoubleTransitWindow]
    summary_verdict: str
    summary_verdict_ta: str
