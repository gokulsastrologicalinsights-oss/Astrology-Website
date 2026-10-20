"""KP Events & Prediction Schemas.

Pydantic models for event promise assessment, Dasha period evaluation,
transit candidate scanning, and comprehensive report generation.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KpPredictionRequest(BaseModel):
    """Request payload for KP Event Prediction & Transit Scanner."""
    horoscope_id: Optional[str] = Field(
        None,
        description="UUID of existing saved horoscope. If provided, birth details are loaded automatically.",
    )
    # Direct input fallback if horoscope_id is not used
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD format")
    birth_time: Optional[str] = Field(None, description="Birth time in HH:MM or HH:MM:SS format")
    timezone: Optional[str] = Field(None, description="IANA timezone name, e.g. 'Asia/Kolkata'")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    place_name: Optional[str] = Field(None, description="Birthplace name")
    customer_name: Optional[str] = Field(None, description="Customer or native name for report display")

    # Event selection
    event_name: str = Field(
        ...,
        description="Standardized event name from KP registry, e.g. 'Marriage', 'New job / employment', 'Children'",
    )

    # Scanner parameters
    start_date: Optional[str] = Field(
        None,
        description="Scan range start date (YYYY-MM-DD). Defaults to today if omitted.",
    )
    end_date: Optional[str] = Field(
        None,
        description="Scan range end date (YYYY-MM-DD). Defaults to start_date + 60 days.",
    )
    scan_resolution_minutes: int = Field(
        5,
        ge=1,
        le=60,
        description="Lagna time-window scanning step size in minutes (default 5 min).",
    )
    max_candidates: int = Field(
        30,
        ge=1,
        le=100,
        description="Maximum number of candidate windows to return.",
    )
    scan_mode: str = Field(
        "standard",
        description="Scan mode: 'standard' (coarse 5m grid) or 'deep' (adaptive bisection to exact KP sub-lord/sub-sub-lord boundaries).",
    )
    deep_refinement_target: str = Field(
        "sub_lord",
        description="Refinement boundary level for deep scan: 'sub_lord' or 'sub_sub_lord'.",
    )
    deep_max_intervals_to_refine: int = Field(
        15,
        ge=1,
        le=50,
        description="Maximum number of candidate coarse intervals to adaptively refine.",
    )

    # Astrologer Judgement / Ruling Planets parameters
    include_ruling_planets: bool = Field(
        True,
        description="Whether to evaluate and require/score Ruling Planets resonance.",
    )
    judgement_datetime: Optional[str] = Field(
        None,
        description="ISO datetime of query/judgement. Defaults to current server time.",
    )
    judgement_latitude: Optional[float] = Field(
        None,
        description="Latitude of astrologer / place of judgement.",
    )
    judgement_longitude: Optional[float] = Field(
        None,
        description="Longitude of astrologer / place of judgement.",
    )
    judgement_timezone: Optional[str] = Field(
        None,
        description="Timezone of astrologer / place of judgement.",
    )


class KpEventPromiseResult(BaseModel):
    """Astrological promise analysis for the selected event in the natal chart."""
    event_name: str
    category: str
    primary_cusp: int
    cusp_degree: float
    cusp_sign: str
    cusp_star_lord: str
    cusp_sub_lord: str
    csl_significations: List[int]
    supporting_houses: List[int]
    denying_houses: List[int]
    promise_status: str  # "Promised" | "Delayed / Mixed" | "Denied / Weak"
    is_csl_retrograde: bool
    is_star_lord_retrograde: bool
    supporting_hits: List[int]
    denying_hits: List[int]
    rule_explanation: str


class KpDashaPeriodResult(BaseModel):
    """Vimshottari Dasha-Bhukti-Antara period evaluation for the event."""
    level: int
    mahadasha_lord: str
    bhukti_lord: Optional[str] = None
    antara_lord: Optional[str] = None
    start_date: str
    end_date: str
    is_running: bool
    signified_houses: List[int]
    support_status: str  # "Strongly Supportive" | "Supportive" | "Mixed" | "Unfavorable"
    scoring_explanation: str


class RulingPlanetsInfo(BaseModel):
    """Ruling Planets obtaining at the moment and place of judgement."""
    judgement_time: str
    judgement_place: str
    ascendant_sign_lord: str
    ascendant_star_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    day_lord: str
    active_ruling_planets: List[str]
    rejected_ruling_planets: List[Dict[str, str]]


class KpCandidateTimeWindow(BaseModel):
    """A qualified candidate date and time window for the event."""
    id: str
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM:SS
    end_time: str  # HH:MM:SS
    timezone: str
    evidence_grade: str  # "A" (High) | "B" (Moderate) | "C" (Speculative)
    composite_score: float
    dasha_chain: str
    dasha_favorable: bool
    moon_transit: Dict[str, Any]
    lagna_transit: Dict[str, Any]
    ruling_planets_matched: List[str]
    supporting_houses_activated: List[int]
    explanation: str
    scan_mode: str = Field("standard", description="Scan mode used for this candidate window ('standard' or 'deep')")
    refinement_resolution: Optional[str] = Field(None, description="Calculation resolution description, e.g. '0.5s (adaptive bisection)'")
    precision_seconds: Optional[float] = Field(None, description="Astronomical boundary calculation precision in seconds")
    transit_transitions: Optional[Dict[str, Any]] = Field(None, description="Detailed ingress/egress transition coordinates, boundary longitudes, and planet speeds")


class KpPredictionResponse(BaseModel):
    """Complete KP Events & Prediction analysis response."""
    horoscope_id: Optional[str] = None
    customer_name: Optional[str] = None
    birth_details: Dict[str, Any]
    calculation_convention: str
    birth_time_accuracy_warning: str
    event_promise: KpEventPromiseResult
    ruling_planets: Optional[RulingPlanetsInfo] = None
    candidate_dasha_periods: List[KpDashaPeriodResult]
    candidate_windows: List[KpCandidateTimeWindow]
    total_windows_found: int
    scan_parameters: Dict[str, Any]
    limitations_disclaimer: str
    report_markdown: str
