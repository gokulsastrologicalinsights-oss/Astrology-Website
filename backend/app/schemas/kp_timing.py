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
