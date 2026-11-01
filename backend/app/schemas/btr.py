"""Pydantic schemas for KP Birth Time Rectification (BTR) Assistant."""

from __future__ import annotations

from datetime import date, time
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class BtrLifeEventInput(BaseModel):
    """A dated past life event for rectification cross-checking."""
    label: str = Field(..., description="Event label, e.g. 'Marriage', 'First Job', 'Childbirth'")
    event_date: date = Field(..., description="Date of the event (YYYY-MM-DD)")
    primary_house: int = Field(..., ge=1, le=12, description="Primary KP house (1-12)")
    secondary_houses: List[int] = Field(default_factory=list, description="Secondary connecting houses (1-12)")
    event_time: Optional[time] = Field(time(12, 0), description="Approximate event time (default 12:00 noon)")


class BtrRequest(BirthInput):
    """Request payload for KP Birth Time Rectification scan."""
    events: List[BtrLifeEventInput] = Field(
        ...,
        min_length=1,
        description="List of 1 to 10 dated past life events (3-5 recommended)"
    )
    window_minutes: float = Field(
        30.0,
        ge=5.0,
        le=180.0,
        description="Search window in minutes around approximate birth time (+/- window)"
    )
    step_minutes: float = Field(
        1.0,
        ge=0.1,
        le=5.0,
        description="Coarse scan step in minutes (default 1.0 min)"
    )
    refine_seconds: bool = Field(
        True,
        description="Whether to perform fine-grained second-level refinement around the top candidate peak"
    )
    use_ruling_planets: bool = Field(
        True,
        description="Whether to cross-check KP Ruling Planets of the analysis moment"
    )
    siblings_count: Optional[int] = Field(
        None,
        ge=0,
        le=20,
        description="Optional biographical hint: number of siblings"
    )
    ayanamsa: int = Field(1, description="Ayanamsa ID (1 = KP Krishnamurti, 0 = Lahiri)")


class BtrEventBreakdown(BaseModel):
    """Breakdown of how a candidate matches a specific life event."""
    label: str
    event_date: str
    primary_house: int
    secondary_houses: List[int]
    lsl_hit: bool
    lsl_score: float
    mahadasha_lord: str
    antardasha_lord: str
    pratyantardasha_lord: str
    dasha_hit: bool
    dasha_score: float
    jupiter_transit_hit: Optional[bool] = None
    saturn_transit_hit: Optional[bool] = None


class VargaLagnaDetail(BaseModel):
    """Lagna detail in a divisional chart."""
    sign_index: int
    sign_name: str
    degree_in_sign: float
    division_specific: Optional[str] = None  # e.g., Pada for D9, Deity/Nature for D60


class BtrShiftComparison(BaseModel):
    """Compares the approximate birth time vs the rectified birth time."""
    approx_time: str
    rectified_time: str
    time_offset_seconds: float
    time_offset_formatted: str

    # Lagna Sub-Lord shift
    approx_lsl: str
    rectified_lsl: str
    lsl_changed: bool

    # D9 Navamsha Lagna shift
    approx_d9: VargaLagnaDetail
    rectified_d9: VargaLagnaDetail
    d9_changed: bool

    # D60 Shashtiamsha Lagna shift
    approx_d60: VargaLagnaDetail
    rectified_d60: VargaLagnaDetail
    d60_changed: bool

    explanation: str


class BtrCandidateDetail(BaseModel):
    """One candidate birth instant in the scan grid."""
    time_str: str
    offset_minutes: float
    offset_seconds: float
    offset_formatted: str
    lsl: str
    specificity: float
    lsl_score: float
    dasha_score: float
    rp_score: float
    identity_score: float
    total_score: float
    confidence_percentage: float
    strikes: int
    d9_sign: str
    d60_sign: str
    events: List[BtrEventBreakdown]


class BtrCredibleInterval(BaseModel):
    """Contiguous time interval containing high posterior mass."""
    start_time: str
    end_time: str
    peak_time: str
    spread_minutes: float
    posterior_mass_percentage: float


class BtrTransitSummary(BaseModel):
    """Summary of transit Jupiter and Saturn confirmation across events."""
    confirmed_tests: int
    total_tests: int
    match_percentage: float


class BtrResponse(BaseModel):
    """Complete KP Birth Time Rectification response."""
    metadata: Optional[CalculationMetadata] = None
    approx_birth_datetime: str
    rectified_birth_datetime: str
    rectified_time: str
    offset_seconds: float
    offset_formatted: str
    rectified_lsl: str
    best_candidate: BtrCandidateDetail
    shift_comparison: BtrShiftComparison
    credible_interval: BtrCredibleInterval
    transit_confirmation: Optional[BtrTransitSummary] = None
    top_candidates: List[BtrCandidateDetail]
    candidate_distribution: List[dict]  # for charting score vs time
    total_candidates_evaluated: int
    astrological_verdict: str
