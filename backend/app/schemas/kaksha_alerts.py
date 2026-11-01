"""Pydantic schemas for Ashtakavarga Kaksha Transit Trigger Alert System."""

from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class KakshaAlertRequest(BirthInput):
    """Request payload for Ashtakavarga Kaksha Transit Trigger Alerts."""
    horizon_days: int = Field(
        90,
        ge=7,
        le=365,
        description="Forecast horizon in days (e.g. 30, 60, 90, 180, 365)"
    )
    planets: List[str] = Field(
        default=["Saturn", "Jupiter", "Mars"],
        description="Key trigger grahas to track (Saturn, Jupiter, Mars, Sun, Venus, Mercury)"
    )
    filter_domain: Optional[str] = Field(
        None,
        description="Filter domain: 'all', 'health', 'finances', 'career', 'lawsuits'"
    )
    ayanamsa: int = Field(1, description="Ayanamsa ID (1 = KP, 0 = Lahiri)")


class ActiveKakshaStatus(BaseModel):
    """Current active Kaksha for a planet today."""
    planet: str
    current_sign: str
    current_sign_index: int
    current_degree: float
    kaksha_number: int
    kaksha_lord: str
    kaksha_range: str
    has_bindu: bool
    status: str  # "Auspicious (Bindu = 1)" or "Inauspicious (Bindu = 0)"
    house_from_lagna: int
    days_remaining_in_kaksha: float


class KakshaAlertItem(BaseModel):
    """A distinct Kaksha transit crossing event with bindu evaluation."""
    id: str
    planet: str
    sign_name: str
    sign_index: int
    kaksha_number: int
    kaksha_lord: str
    kaksha_range: str
    start_date: str
    end_date: str
    duration_days: float
    has_bindu: bool
    is_favorable: bool
    house_from_lagna: int
    life_domains: List[str]  # e.g., ["health", "lawsuits", "finances", "career"]
    alert_badge: str  # "Favorable Trigger 🟢" or "Obstacle Warning 🔴"
    severity_level: str  # "High Opportunity", "Caution Required", "Neutral", "Favorable"
    guidance: str
    guidance_ta: str


class DomainAlertSummary(BaseModel):
    """Domain-specific impact count."""
    favorable_windows_count: int
    challenging_windows_count: int
    key_advice: str


class KakshaAlertsResponse(BaseModel):
    """Complete response containing active status and timeline of Kaksha triggers."""
    metadata: Optional[CalculationMetadata] = None
    natal_lagna_sign: str
    natal_lagna_sign_index: int
    horizon_days: int
    start_date: str
    end_date: str
    active_now: List[ActiveKakshaStatus]
    timeline_alerts: List[KakshaAlertItem]
    domain_summaries: Dict[str, DomainAlertSummary]
    total_auspicious_triggers: int
    total_inauspicious_triggers: int
    upcoming_peak_window: Optional[KakshaAlertItem] = None
    upcoming_critical_caution: Optional[KakshaAlertItem] = None
