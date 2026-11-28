"""KP Monthly & Period Predictive Event Timing Schemas.

Pydantic models for calculating exact monthly and period event fructification
using KP 4-pillar principles (Cuspal Sub-Lord + DBAS Hierarchy + Transit Triggers).
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class KpMonthlyPredictionRequest(BaseModel):
    """Request model for KP monthly event timing prediction."""
    birth: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    native_name: Optional[str] = None
    year: int = Field(default=2026, description="Target year, e.g. 2026")
    month: int = Field(default=11, ge=1, le=12, description="Target month: 1..12 (11=November, 12=December)")
    ayanamsa_id: int = Field(default=1, description="0=Lahiri, 1=KP (default)")


class KpDbaSummary(BaseModel):
    """Active Vimshottari D-B-A-S-P hierarchy during the target month."""
    mahadasha: str
    mahadasha_ta: str
    antardasha: str
    antardasha_ta: str
    pratyantardasha: str
    pratyantardasha_ta: str
    sookshmadasha: Optional[str] = None
    sookshmadasha_ta: Optional[str] = None
    pranadasha: Optional[str] = None
    pranadasha_ta: Optional[str] = None
    period_start: str
    period_end: str
    active_date: str


class KpTransitSunSummary(BaseModel):
    """Transit movement of Sun and triggers during the target month."""
    month_name: str
    month_name_ta: str
    start_sign: str
    start_sign_ta: str
    end_sign: str
    end_sign_ta: str
    activated_stars: List[str]
    activated_stars_ta: List[str]
    summary_ta: str


class KpMonthlyEventItem(BaseModel):
    """Single life event evaluation for the specified month."""
    event_id: str
    title_en: str
    title_ta: str
    category: str
    icon: str
    status: str  # GUARANTEED, HIGHLY_FAVORABLE, MODERATE, CAUTION
    status_label_ta: str
    probability_score: int
    trigger_window_dates: str
    summary_verdict_ta: str
    detailed_analysis_ta: str
    cuspal_promise_ta: str
    dasha_bhukti_role_ta: str
    transit_trigger_ta: str
    actionable_remedy_ta: str
    primary_houses: List[int]
    supporting_houses: List[int]
    negating_houses: List[int]
    significator_planets: List[str]


class KpMonthlyPredictionResponse(BaseModel):
    """Comprehensive response with categorized guaranteed and favorable predictions."""
    year: int
    month: int
    month_label: str
    month_label_ta: str
    native_name: str
    dasha_hierarchy: KpDbaSummary
    transit_sun: KpTransitSunSummary
    guaranteed_events: List[KpMonthlyEventItem]
    favorable_events: List[KpMonthlyEventItem]
    moderate_events: List[KpMonthlyEventItem]
    caution_events: List[KpMonthlyEventItem]
    all_events: List[KpMonthlyEventItem]
    overall_month_summary_ta: str
    generated_at: str


# ---------------------------------------------------------------------------
# KP Marriage Promise, Timing & Date Finder Schemas
# ---------------------------------------------------------------------------

class KpMarriageDateRequest(BaseModel):
    """Request model for KP Marriage Date Finder."""
    birth: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    native_name: Optional[str] = None
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD search start (defaults to today)")
    years_ahead: int = Field(default=2, ge=1, le=5, description="Years ahead to scan Dasha-Bhukti-Antara (1-5)")
    ayanamsa_id: int = Field(default=1, description="0=Lahiri, 1=KP (default)")


class KpMarriagePromiseFactor(BaseModel):
    factor_key: str
    title_en: str
    title_ta: str
    score: float
    max_score: float
    lord: str
    lord_ta: str
    supporting_houses: List[int]
    obstacle_houses: List[int]
    detail_en: str
    detail_ta: str


class KpMarriagePromiseBreakdown(BaseModel):
    total_score: float
    verdict: str
    verdict_ta: str
    confidence: str
    confidence_ta: str
    summary_en: str
    summary_ta: str
    factors: List[KpMarriagePromiseFactor]


class KpMarriageTargetLord(BaseModel):
    priority: int
    role_en: str
    role_ta: str
    planet: str
    planet_ta: str
    stars_en: List[str]
    stars_ta: List[str]
    is_duplicate_role: bool = False


class KpMarriageCuspAnalysis(BaseModel):
    sign: str
    sign_ta: str
    degree_dms: str
    longitude: float
    sign_lord: str
    sign_lord_ta: str
    star: str
    star_ta: str
    star_lord: str
    star_lord_ta: str
    sub_lord: str
    sub_lord_ta: str
    sub_sub_lord: str
    sub_sub_lord_ta: str
    target_lords: List[KpMarriageTargetLord]


class KpMarriageDashaWindow(BaseModel):
    dasha_lord: str
    dasha_lord_ta: str
    bhukti_lord: str
    bhukti_lord_ta: str
    antara_lord: str
    antara_lord_ta: str
    start_date: str
    end_date: str
    dasha_score: float
    bhukti_score: float
    antara_score: float
    total_score: float
    rating: str
    rating_ta: str
    supporting_houses: List[int]
    obstacle_houses: List[int]
    is_current: bool = False


class KpMarriageCandidateDate(BaseModel):
    date: str
    weekday_en: str
    weekday_ta: str
    paksha: str
    paksha_ta: str
    tithi_en: str
    tithi_ta: str
    nakshatra_en: str
    nakshatra_ta: str
    nakshatra_lord: str
    nakshatra_lord_ta: str
    dasha_bhukti_antara: str
    dasha_bhukti_antara_ta: str
    abhijit_window: str
    rahu_kalam_avoid: str
    score: float
    match_tier: str
    match_tier_ta: str
    reasons_en: List[str]
    reasons_ta: List[str]


class KpMarriageDateResponse(BaseModel):
    native_name: str
    search_start_date: str
    search_end_date: str
    promise: KpMarriagePromiseBreakdown
    seventh_cusp: KpMarriageCuspAnalysis
    dasha_windows: List[KpMarriageDashaWindow]
    candidate_dates: List[KpMarriageCandidateDate]
    composite_weights: Dict[str, float]
    disclaimer_en: str
    disclaimer_ta: str
    generated_at: str
