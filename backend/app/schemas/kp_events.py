"""Pydantic schemas for KP Dasha-Bhukti Event Prediction Engine.

Strictly follows Section 4 (Input Data Contract) and Section 10 (JSON API Response).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class KpEventPeriodInput(BaseModel):
    mahadasha_lord: str = Field(..., description="Lord of the Mahadasha (e.g. Venus)")
    bhukti_lord: str = Field(..., description="Lord of the Bhukti / Antardasha (e.g. Sun)")
    antara_lord: Optional[str] = Field(None, description="Optional Lord of the Antara / Pratyantardasha")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD or ISO format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD or ISO format")


class KpEventAnalysisRequest(BaseModel):
    lagna: Optional[str] = Field(None, description="Horoscope ascendant sign (e.g. Aries)")
    periods: List[KpEventPeriodInput] = Field(..., description="Chronological periods to analyze")
    significations: Dict[str, Any] = Field(
        ...,
        description="Significations mapping: planet -> list of {house, level} or house -> levels",
    )
    csl_significations: Optional[Dict[str, str]] = Field(
        None,
        description="Cuspal Sub-Lord mapping: house (1-12) -> planet name",
    )
    retrograde_status: Optional[Dict[str, bool]] = Field(
        None,
        description="Retrograde status per planet: planet -> boolean",
    )
    current_date: Optional[str] = Field(None, description="Optional target date in YYYY-MM-DD format")
    timezone: Optional[str] = Field("Asia/Kolkata", description="Timezone name for running period detection")
    filter_category: Optional[str] = Field(None, description="Optional category filter (e.g. Career, Relationship)")
    filter_grade: Optional[str] = Field(None, description="Optional grade filter ('green', 'orange', 'red')")
    filter_event: Optional[str] = Field(None, description="Optional event name filter (e.g. Marriage)")
    running_only: Optional[bool] = Field(False, description="Whether to return only the active running period")
    save_horoscope_id: Optional[str] = Field(None, description="Optional saved horoscope UUID to persist analysis with")


class HouseSignificationDetail(BaseModel):
    house: int
    level: str
    weight: int


class EventGradingDetail(BaseModel):
    event: str
    color: str  # green, orange, red
    grade: str  # STRONG, MODERATE, WEAK
    support_score: int
    denial_score: int
    coverage: float
    supporting: List[HouseSignificationDetail]
    denying: List[HouseSignificationDetail]
    denied: bool
    retrograde_note: Optional[str] = None
    csl_adjustment: Optional[str] = None
    hint: str
    scoring_metadata: Optional[Dict[str, Any]] = None


class PeriodSummaryCounts(BaseModel):
    green_count: int
    orange_count: int
    red_count: int


class PeriodAnalysisResult(BaseModel):
    period: str
    mahadasha_lord: str
    bhukti_lord: str
    antara_lord: Optional[str] = None
    start: str
    end: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    running: bool
    is_running: Optional[bool] = None
    status: str = "ok"
    missing_fields: Optional[List[str]] = Field(default_factory=list)
    events: List[EventGradingDetail]
    all_events: Optional[List[EventGradingDetail]] = Field(default_factory=list)
    summary: PeriodSummaryCounts


class OverallAnalysisSummary(BaseModel):
    rule_set_version: str
    total_periods: int
    running_period: Optional[str] = None
    green_count: int
    orange_count: int
    red_count: int
    persistence_status: Optional[str] = "database"
    persistence_warning: Optional[str] = None


class KpEventAnalysisResponse(BaseModel):
    rule_set_version: str
    lagna: Optional[str] = None
    current_date: str
    timezone: str
    overall_summary: OverallAnalysisSummary
    periods: List[PeriodAnalysisResult]
    human_readable_report: str
    persistence_status: Optional[str] = "database"
    persistence_warning: Optional[str] = None


class SavedHoroscopeAnalysisRequest(BaseModel):
    filter_category: Optional[str] = None
    filter_grade: Optional[str] = None
    filter_event: Optional[str] = None
    running_only: Optional[bool] = False
    regenerate: Optional[bool] = False


class UserKpAnalysisSummary(BaseModel):
    id: str
    user_id: str
    horoscope_id: Optional[str] = None
    rule_set_version: str = "1.0.0"
    calculation_timestamp: str
    created_at: str
    updated_at: str
    running_period: Optional[str] = None
    total_periods: int = 0
    green_count: int = 0
    orange_count: int = 0
    red_count: int = 0
    persistence_status: str = "database"
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    display_number: Optional[int] = None
    lagna: Optional[str] = None


class UserKpAnalysisListResponse(BaseModel):
    total_count: int
    limit: int
    offset: int
    items: List[UserKpAnalysisSummary]

