"""Pydantic schemas for Feature 1: Automated Multi-Year Life Timeline Predictor (Life Roadmap).

Evaluates birth chart across 1, 3, or 5 years across all major life domains simultaneously:
- Career & Status
- Relationships & Matrimony
- Finance & Wealth
- Relocation & Travel
- Health & Caution
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LifeDomainInfo(BaseModel):
    id: str
    name: str
    name_ta: str
    icon: str
    color: str
    description: str
    events: List[str]


class HouseEvidence(BaseModel):
    house: int
    level: str
    weight: int
    contributing_lord: Optional[str] = None


class ScoredMilestone(BaseModel):
    event_name: str
    domain_id: str
    domain_name: str
    domain_name_ta: str
    is_caution_type: bool
    probability_level: str  # "HIGH", "MODERATE", "CAUTION", "LOW"
    status_label: str       # e.g. "🟢 High Probability / Favorable", "🟡 Moderate / Delays", "🔴 Caution / Restrained"
    color: str              # "green", "orange", "red"
    grade: str              # "STRONG", "MODERATE", "WEAK"
    support_score: int
    denial_score: int
    coverage: float
    supporting_houses: List[HouseEvidence]
    denying_houses: List[HouseEvidence]
    denied: bool
    hint: str
    retrograde_note: Optional[str] = None
    csl_adjustment: Optional[str] = None


class DomainScorecard(BaseModel):
    domain_id: str
    domain_name: str
    domain_name_ta: str
    icon: str
    color: str
    summary_label: str
    status_color: str  # "green", "orange", "red"
    green_count: int
    orange_count: int
    red_count: int
    caution_alert_count: int
    peak_window_period: Optional[str] = None
    peak_window_dates: Optional[str] = None
    peak_window_event: Optional[str] = None
    summary_text: str


class RoadmapPeriodItem(BaseModel):
    period_key: str  # e.g. "Jupiter - Saturn - Mercury"
    mahadasha_lord: str
    bhukti_lord: str
    antara_lord: Optional[str] = None
    start_date: str
    end_date: str
    start_display: str
    end_display: str
    duration_days: int
    is_running: bool
    primary_status: str  # "green", "orange", "red"
    domain_highlights: Dict[str, str] = Field(default_factory=dict)  # domain_id -> color
    top_milestones: List[ScoredMilestone] = Field(default_factory=list)
    all_milestones: List[ScoredMilestone] = Field(default_factory=list)


class LifeRoadmapRequest(BaseModel):
    horoscope_id: Optional[str] = Field(
        None,
        description="UUID of saved horoscope. If supplied, birth chart data is loaded automatically.",
    )
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD format")
    birth_time: Optional[str] = Field(None, description="Birth time in HH:MM or HH:MM:SS format")
    timezone: Optional[str] = Field("Asia/Kolkata", description="Timezone name")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    place_name: Optional[str] = Field(None, description="Birthplace city or state")
    customer_name: Optional[str] = Field(None, description="Customer or native name")

    horizon_years: int = Field(
        3,
        ge=1,
        le=10,
        description="Horizon span in years: 1 (Immediate), 3 (Medium-Term), or 5 (Strategic Life Planning)",
    )
    start_date: Optional[str] = Field(
        None,
        description="Timeline evaluation start date (YYYY-MM-DD). Defaults to current date.",
    )
    filter_domain: Optional[str] = Field(
        None,
        description="Optional filter by domain: 'career', 'relationships', 'finance', 'travel', 'health', or 'all'",
    )
    min_probability: Optional[str] = Field(
        None,
        description="Optional probability filter: 'high_only', 'high_and_moderate', or 'all'",
    )
    ayanamsa_id: int = Field(1, description="Ayanamsa ID (1 = KP Krishnamurti, 0 = Lahiri)")


class LifeRoadmapOverallSummary(BaseModel):
    total_dba_periods: int
    total_evaluated_events: int
    high_probability_count: int
    moderate_count: int
    caution_alerts_count: int
    running_period_key: Optional[str] = None
    most_favorable_domain: Optional[str] = None
    executive_verdict: str


class LifeRoadmapResponse(BaseModel):
    customer_name: Optional[str] = None
    lagna: Optional[str] = None
    moon_sign: Optional[str] = None
    nakshatra: Optional[str] = None
    current_date: str
    start_date: str
    end_date: str
    horizon_years: int
    running_period_key: Optional[str] = None
    overall_summary: LifeRoadmapOverallSummary
    domain_scorecards: List[DomainScorecard]
    chronological_periods: List[RoadmapPeriodItem]
    upcoming_key_milestones: List[ScoredMilestone]
    executive_roadmap_markdown: str
