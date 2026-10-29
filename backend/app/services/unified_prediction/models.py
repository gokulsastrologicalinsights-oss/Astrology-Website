"""Data models and enums for the Unified KP + Vedic Marriage Prediction Engine.

This module defines the strict Pydantic V2 schemas, enumerations, and provenance
metadata types used throughout the unified marriage prediction pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from app.schemas.common import BirthInput, CalculationMetadata


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EventVerdict(str, Enum):
    """Deterministic top-level event verdict for user-facing output."""
    EVENT_INDICATED = "EVENT_INDICATED"
    EVENT_NOT_INDICATED = "EVENT_NOT_INDICATED"
    INDETERMINATE = "INDETERMINATE"


class TimingStatus(str, Enum):
    """Status of the timing evaluation, completely decoupled from natal verdict."""
    WINDOW_FOUND = "WINDOW_FOUND"
    NO_WINDOW_IN_RANGE = "NO_WINDOW_IN_RANGE"
    TIMING_NOT_DETERMINABLE = "TIMING_NOT_DETERMINABLE"
    NOT_EVALUATED = "NOT_EVALUATED"


class PromiseVerdict(str, Enum):
    """Tradition-specific natal promise determination."""
    PROMISED = "PROMISED"
    DENIED = "DENIED"
    INDETERMINATE = "INDETERMINATE"


class KPInternalModifier(str, Enum):
    """Internal explanatory modifier for KP promise resolution."""
    PROMISED_SMOOTH = "PROMISED_SMOOTH"
    PROMISED_WITH_OBSTACLES = "PROMISED_WITH_OBSTACLES"
    PROMISED_DELAYED = "PROMISED_DELAYED"
    DENIED_AT_ROOT = "DENIED_AT_ROOT"
    DENIED_AT_FRUITION = "DENIED_AT_FRUITION"
    INDETERMINATE_DATA = "INDETERMINATE_DATA"


class VedicInternalModifier(str, Enum):
    """Internal explanatory modifier for Vedic promise resolution."""
    PROMISED_FAVORABLE = "PROMISED_FAVORABLE"
    PROMISED_WITH_OBSTACLES = "PROMISED_WITH_OBSTACLES"
    DENIED_COMPOUND = "DENIED_COMPOUND"
    INDETERMINATE_DATA = "INDETERMINATE_DATA"


class RuleProvenanceTag(str, Enum):
    """Rigorous classification of source authority."""
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    PROJECT_ENGINEERING_POLICY = "PROJECT_ENGINEERING_POLICY"


class ScanStatus(str, Enum):
    """Status of continuous Placidus cusp birth-time sensitivity scan."""
    STABLE = "STABLE"
    BOUNDARY_CROSSING_DETECTED = "BOUNDARY_CROSSING_DETECTED"
    SCAN_FAILED_OR_INCOMPLETE = "SCAN_FAILED_OR_INCOMPLETE"


# ---------------------------------------------------------------------------
# Sensitivity Schemas
# ---------------------------------------------------------------------------

class CuspCrossingDetail(BaseModel):
    """Details of a single KP sub-lord boundary crossing within the uncertainty window."""
    crossing_time_iso: str = Field(
        ...,
        description="Exact transition timestamp in ISO 8601 second resolution"
    )
    delta_seconds: float = Field(
        ...,
        description="Time offset in seconds from nominal birth time (negative = earlier, positive = later)"
    )
    boundary_longitude_deg: float = Field(
        ...,
        description="Exact zodiac longitude (degrees) of the traversed sub-lord boundary"
    )
    from_sub_lord: str = Field(
        ...,
        description="Sub-lord immediately before the boundary transition"
    )
    to_sub_lord: str = Field(
        ...,
        description="Sub-lord immediately after the boundary transition"
    )
    verdict_impact: str = Field(
        ...,
        description="'VERDICT_PRESERVED' if adjacent sub-lord yields identical promise, else 'VERDICT_FLIPPED'"
    )


class SensitivityToleranceGuarantee(BaseModel):
    """Mathematical and numerical limits of the sensitivity scan."""
    mesh_step_seconds: float = Field(
        5.0,
        description="Initial base mesh step for adaptive subdivision in seconds"
    )
    max_recursion_depth: int = Field(
        6,
        description="Maximum bisection/adaptive subdivision recursion depth"
    )
    time_tolerance_seconds: float = Field(
        0.5,
        description="Root bracketing time convergence tolerance in seconds"
    )
    longitude_tolerance_deg: float = Field(
        1e-6,
        description="Longitude convergence tolerance in degrees"
    )
    disclaimer: str = Field(
        "Numerical second-level root-finding establishes software stability against boundary discontinuities; "
        "it does not establish that human birth times are known to the second or that real-world life events "
        "are deterministically scheduled to an exact second.",
        description="Scientific and interpretive boundary disclaimer"
    )


class BirthTimeSensitivityReport(BaseModel):
    """Full diagnostic report of birth-time sensitivity across uncertainty interval."""
    is_sensitive: bool = Field(
        ...,
        description="True if an interior boundary crossing flips the promise verdict or scan fails"
    )
    uncertainty_seconds: float = Field(
        ...,
        description="Evaluated half-window uncertainty (+/- delta t in seconds)"
    )
    scan_status: ScanStatus = Field(
        ...,
        description="Execution status of continuous adaptive subdivision scan"
    )
    nominal_sub_lord: str = Field(
        ...,
        description="7th cusp sub-lord at nominal birth time"
    )
    nominal_cusp_degree: float = Field(
        ...,
        description="7th cusp sidereal longitude at nominal birth time"
    )
    crossings: List[CuspCrossingDetail] = Field(
        default_factory=list,
        description="List of detected boundary crossings within the uncertainty interval"
    )
    tolerance_guarantee: SensitivityToleranceGuarantee = Field(
        default_factory=SensitivityToleranceGuarantee,
        description="Numerical specifications of the scan"
    )
    error_detail: Optional[str] = Field(
        None,
        description="Reason for scan failure if scan_status is SCAN_FAILED_OR_INCOMPLETE"
    )


# ---------------------------------------------------------------------------
# Tradition Details
# ---------------------------------------------------------------------------

class KPPromiseDetail(BaseModel):
    """Detailed evaluation of KP natal marriage promise."""
    verdict: PromiseVerdict
    internal_modifier: KPInternalModifier
    cuspal_sub_lord_7: str
    star_lord_of_csl: str
    star_lord_significations: List[int]
    sub_lord_significations: List[int]
    is_csl_retrograde: bool = False
    is_star_lord_retrograde: bool = False
    rule_id: str
    rule_provenance: RuleProvenanceTag
    explanation: str


class VedicPromiseDetail(BaseModel):
    """Detailed evaluation of Vedic natal marriage promise."""
    verdict: PromiseVerdict
    internal_modifier: VedicInternalModifier
    seventh_lord_d1: str
    seventh_house_sign_d1: str
    seventh_lord_house_d1: int
    venus_combustion: bool
    venus_debilitation: bool
    venus_dusthana: bool
    kuja_dosha_present: bool
    kuja_dosha_cancelled: bool
    d9_seventh_sign: str
    d9_seventh_lord: str
    d9_venus_sign: str
    d9_afflicted: bool
    compound_denial_gates_met: int
    rule_id: str
    rule_provenance: RuleProvenanceTag
    explanation: str


# ---------------------------------------------------------------------------
# Timing Schemas
# ---------------------------------------------------------------------------

class TimingWindow(BaseModel):
    """A qualified temporal window for marriage fructification."""
    start_date: str = Field(..., description="Start date of the timing window (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the timing window (YYYY-MM-DD)")
    mahadasha: str
    antardasha: str
    pratyantardasha: Optional[str] = None
    double_transit_active: bool = Field(
        ...,
        description="True if Jupiter and Saturn simultaneously aspect or transit qualifying points"
    )
    kp_significator_confluence: bool = Field(
        ...,
        description="True if Dasha lords are primary Level A/B KP significators of 2, 7, 11"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Algorithmic confluence score (0.0 to 1.0) based on Dasha + Transit alignment"
    )


class UnifiedTimingReport(BaseModel):
    """Summary of timing evaluation over the requested interval."""
    best_window: Optional[TimingWindow] = None
    evaluated_windows_count: int = 0
    search_start_date: str
    search_end_date: str
    rule_provenance: RuleProvenanceTag = RuleProvenanceTag.SOURCE_VERIFIED


# ---------------------------------------------------------------------------
# Request & Response Payloads
# ---------------------------------------------------------------------------

class UnifiedMarriageRequest(BaseModel):
    """Input request payload for Unified Marriage Prediction."""
    birth: BirthInput
    birth_time_uncertainty_seconds: float = Field(
        120.0,
        ge=0.0,
        le=1800.0,
        description="Birth time uncertainty window (+/- delta t in seconds, max 1800s / 30m)"
    )
    start_year: Optional[int] = Field(
        None,
        description="Optional start year for timing scan (defaults to birth_year + 18)"
    )
    end_year: Optional[int] = Field(
        None,
        description="Optional end year for timing scan (defaults to start_year + 10)"
    )
    force_timing_scan: bool = Field(
        False,
        description="Force execution of Vimshottari & Double Transit timing scan even if marriage promise is INDETERMINATE."
    )

    @model_validator(mode="after")
    def validate_timing_range(self) -> UnifiedMarriageRequest:
        if self.start_year is not None and self.end_year is not None:
            if self.end_year < self.start_year:
                raise ValueError("end_year cannot be earlier than start_year")
        return self


class UnifiedMarriageResponse(BaseModel):
    """Deterministic output payload for Unified Marriage Prediction."""
    final_verdict: EventVerdict
    timing_status: TimingStatus
    kp_promise: KPPromiseDetail
    vedic_promise: VedicPromiseDetail
    birth_time_sensitivity: BirthTimeSensitivityReport
    timing: Optional[UnifiedTimingReport] = None
    reconciliation_rule_id: str = "UNI-MARR-REC-001"
    reconciliation_provenance: RuleProvenanceTag = RuleProvenanceTag.PROJECT_ENGINEERING_POLICY
    metadata: CalculationMetadata
