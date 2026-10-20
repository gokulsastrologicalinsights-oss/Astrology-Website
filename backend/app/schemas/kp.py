"""Schemas for POST /api/v1/horoscope/kp."""

from typing import List, Dict, Any, Optional
from datetime import date, time, datetime
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.common import BirthInput, CalculationMetadata


class KpRequest(BirthInput):
    ayanamsa: int = Field(1, description="Ayanamsa ID (default 1 = KP Krishnamurti)")
    house_system: int = Field(2, description="House System ID (default 2 = Placidus)")


class PlanetaryKpPosition(BaseModel):
    planet: str
    body_id: int
    longitude: float
    sign_index: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    kp_number: int  # 1-249


class KpCuspDetail(BaseModel):
    house: int
    cusp_degree: float
    sign_index: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    promise: str  # Positive, Negative, Mixed
    sub_sub_lord: Optional[str] = None


class SignificatorStrengthEntry(BaseModel):
    house: int
    type: str  # StarLord, Occupant, Owner, Aspecting


class PlanetSignificator(BaseModel):
    planet: str
    signified_houses: List[int]
    strength_order: List[SignificatorStrengthEntry]


class HouseSignificatorEntry(BaseModel):
    house: int
    sign_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    level_a: List[str]  # Planets in star of occupants (strongest)
    level_b: List[str]  # House occupants
    level_c: List[str]  # Planets in star of house lord
    level_d: List[str]  # House sign lord
    all_significators: List[str]  # Unique significators ordered by strength (A -> B -> C -> D)


class RulingPlanetEntry(BaseModel):
    role: str
    planet: str


class RulingPlanetsDetail(BaseModel):
    day_lord: str
    ascendant_sign_lord: str
    ascendant_star_lord: str
    ascendant_sub_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    moon_sub_lord: str
    ruling_planets_list: List[str]
    details: List[RulingPlanetEntry]


class KpDasaPeriod(BaseModel):
    level: int           # 1 (MD), 2 (AD), 3 (PD), 4 (SD), 5 (PrD)
    level_name: str      # Mahadasha, Antardasha, Pratyantardasha, Sookshmadasha, Pranadasha
    vedic_name: str      # Dasa, Bhukti, Andharam, Soochamam, Pranam
    lord: str
    start_date: str      # ISO format
    end_date: str        # ISO format
    duration_days: float


class KpDasaBalance(BaseModel):
    birth_epoch: str
    mahadasha_lord: str
    mahadasha_balance_years: float
    mahadasha_balance_days: float
    antardasha_lord: str
    antardasha_balance_days: float
    pratyantardasha_lord: str
    pratyantardasha_balance_days: float
    sookshmadasha_lord: str
    sookshmadasha_balance_days: float
    pranadasha_lord: str
    pranadasha_balance_days: float
    current_periods: List[KpDasaPeriod]
    mahadashas: List[KpDasaPeriod]


class KpResponse(BaseModel):
    metadata: CalculationMetadata
    planetary_positions: List[PlanetaryKpPosition]
    cuspal_analysis: List[KpCuspDetail]
    significators: List[PlanetSignificator]
    house_significators: Optional[List[HouseSignificatorEntry]] = None
    ruling_planets: Optional[RulingPlanetsDetail] = None
    dasa_hierarchy: Optional[KpDasaBalance] = None


class HoraryKpRequest(BaseModel):
    horary_number: int = Field(..., ge=1, le=249, description="Horary query number (1-249)")
    question_text: Optional[str] = Field(None, description="Querent question or consultation label")
    question_date: date = Field(..., description="Date of question (YYYY-MM-DD)")
    question_time: time = Field(..., description="Exact local time of question (HH:MM or HH:MM:SS)")
    timezone: str = Field(..., description="IANA timezone name, e.g. Asia/Kolkata")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of the query location")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of the query location")
    location_name: Optional[str] = Field(None, description="Location name / city")
    ayanamsa: int = Field(1, description="Ayanamsa ID (default 1 = KP Krishnamurti)")
    house_system: int = Field(2, description="House System ID (default 2 = Placidus)")


class HoraryDivisionDetail(BaseModel):
    number: int
    start_degree: float
    end_degree: float
    mid_degree: float
    sign: str
    sign_lord: str
    star: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    pada: int


class HoraryKpResponse(BaseModel):
    metadata: CalculationMetadata
    horary_number: int
    horary_division: HoraryDivisionDetail
    question_text: Optional[str] = None
    question_datetime: str
    location_name: Optional[str] = None
    ascendant_degree: float
    planetary_positions: List[PlanetaryKpPosition]
    cuspal_analysis: List[KpCuspDetail]
    significators: List[PlanetSignificator]
    house_significators: List[HouseSignificatorEntry]
    ruling_planets: RulingPlanetsDetail
    dasa_hierarchy: Optional[KpDasaBalance] = None


class SaveKpChartRequest(BaseModel):
    chart_type: str = Field("natal", description="'natal' or 'horary'")
    title: str = Field(..., min_length=1, description="Chart title or querent label")
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    horary_number: Optional[int] = Field(None, ge=1, le=249)
    question_text: Optional[str] = None
    question_date: Optional[str] = None
    question_time: Optional[str] = None
    location_name: str = Field("Unknown Location", min_length=1)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    timezone: str = Field(..., min_length=1)
    ayanamsa_id: int = Field(1, description="1 = KP, 0 = Lahiri")
    house_system_id: int = Field(2, description="2 = Placidus")
    calculation_result: Dict[str, Any] = Field(..., description="Full calculation snapshot")
    saved_horoscope_id: Optional[str] = None
    customer_full_name: Optional[str] = None
    customer_phone: Optional[str] = None
    country_code: Optional[str] = "+91"
    customer_id: Optional[str] = None
    normalized_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None


class SavedKpChartItem(BaseModel):
    id: str
    user_id: str
    display_number: int
    chart_type: str
    title: str
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    horary_number: Optional[int] = None
    question_text: Optional[str] = None
    question_date: Optional[str] = None
    question_time: Optional[str] = None
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    ayanamsa_id: int
    house_system_id: int
    engine_version: str
    calculation_result: Dict[str, Any]
    saved_horoscope_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_phone: Optional[str] = None
    country_code: Optional[str] = None
    normalized_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    created_at: str
    updated_at: str


class SavedKpChartListResponse(BaseModel):
    charts: List[SavedKpChartItem]
    total_count: int


# ===========================================================================
# KP Transit Timeline Schemas (Phase 2)
# ===========================================================================

ALLOWED_TRANSIT_PLANETS = {
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
}


class TransitTimelineRequest(BaseModel):
    """Input payload for KP Transit Ingress and Sub-Lord Timeline."""
    start_date: date = Field(..., description="Start date in ISO format YYYY-MM-DD", examples=["2026-10-18"])
    start_time: Optional[time] = Field(default=time(0, 0, 0), description="Optional start time in ISO format HH:MM or HH:MM:SS (defaults to 00:00:00)")
    end_date: Optional[date] = Field(default=None, description="Optional end date in ISO format YYYY-MM-DD")
    end_time: Optional[time] = Field(default=None, description="Optional end time in ISO format HH:MM or HH:MM:SS")
    forecast_days: Optional[int] = Field(default=None, ge=7, le=30, description="Calculation window duration in days (7 to 30 days). If omitted and end_date is not provided, defaults to 7.")
    timezone: str = Field(default="UTC", description="Explicit IANA timezone (e.g. 'Asia/Kolkata', 'UTC') or numeric offset (e.g. '+05:30')")
    planets: Optional[List[str]] = Field(
        default=None,
        description="Explicit list of planets to analyze. Allowed: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu. Defaults to [Moon, Sun, Jupiter, Saturn, Rahu, Ketu].",
    )
    ayanamsa: int = Field(default=0, description="Sidereal ayanamsa ID: 0 = Lahiri (default), 1 = KP Krishnamurti")
    max_events: Optional[int] = Field(default=500, ge=1, le=1000, description="Sensible ceiling on number of returned events (1 to 1000, default 500)")

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        tz = v.strip() if v else ""
        if not tz:
            raise ValueError("timezone cannot be empty")
        if tz.upper() in ("UTC", "Z", "+00:00", "-00:00", "+00", "-00"):
            return tz
        if tz.startswith(("+", "-")):
            offset_pattern = re.compile(r"^[+-]\d{2}(:?\d{2})?$")
            if not offset_pattern.match(tz):
                raise ValueError(f"Invalid timezone offset format: '{tz}'. Use format like '+05:30' or '-04:00'.")
            return tz
        try:
            ZoneInfo(tz)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Invalid timezone: '{tz}'. Provide a valid IANA name (e.g. 'Asia/Kolkata') or offset.") from exc
        return tz

    @field_validator("planets")
    @classmethod
    def validate_planets(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            if len(v) == 0:
                raise ValueError("planets list cannot be empty when provided")
            invalid = [p for p in v if p not in ALLOWED_TRANSIT_PLANETS]
            if invalid:
                raise ValueError(f"Unsupported planet(s): {invalid}. Allowed: {sorted(ALLOWED_TRANSIT_PLANETS)}")
            # Preserve order and eliminate duplicate entries
            seen = set()
            deduped = []
            for p in v:
                if p not in seen:
                    seen.add(p)
                    deduped.append(p)
            return deduped
        return v

    @field_validator("ayanamsa")
    @classmethod
    def validate_ayanamsa(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError(f"ayanamsa must be 0 (Lahiri) or 1 (KP), got {v}")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "TransitTimelineRequest":
        if self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be earlier than start_date")
            st = self.start_time or time(0, 0, 0)
            et = self.end_time or time(0, 0, 0)
            dt_start = datetime.combine(self.start_date, st)
            dt_end = datetime.combine(self.end_date, et)
            duration_days = (dt_end - dt_start).total_seconds() / 86400.0
            if duration_days < 7.0 - 1e-4 or duration_days > 30.0 + 1e-4:
                raise ValueError(f"Calculation window duration must be between 7 and 30 days (got {duration_days:.2f} days)")
        return self


class TransitIngressEventSchema(BaseModel):
    """Schema for a single planetary boundary crossing event."""
    planet: str
    planet_id: int
    utc_datetime: str
    local_datetime: str
    jd: float
    boundary_type: str            # "rashi" | "nakshatra" | "sub_lord"
    boundary_longitude: float     # degrees [0, 360)
    is_retrograde: bool
    speed_deg_per_day: float

    # Rashi / Sign transition
    from_sign: str
    to_sign: str
    from_sign_lord: str
    to_sign_lord: str
    is_rashi_boundary: bool

    # Nakshatra / Star transition
    from_nakshatra: str
    to_nakshatra: str
    from_star_lord: str
    to_star_lord: str
    is_nakshatra_boundary: bool

    # KP Sub-Lord transition
    from_sub_lord: str
    to_sub_lord: str
    from_kp_number: int
    to_kp_number: int
    is_sub_lord_boundary: bool

    calculation_precision_seconds: float = 0.5


class TransitTimelineBenchmarkStats(BaseModel):
    """Execution diagnostics and evaluation counts."""
    duration_ms: float
    total_evaluations: int
    step_evaluations: int
    bisection_evaluations: int


class TransitTimelineResponse(BaseModel):
    """Full KP transit timeline response with window metadata and chronological events."""
    start_time_utc: str
    start_time_local: str
    end_time_utc: str
    end_time_local: str
    timezone: str
    utc_offset_hours: float
    ayanamsa_id: int
    ayanamsa_name: str
    forecast_days: float
    planets_analyzed: List[str]
    total_events: int
    truncated: bool = False
    events: List[TransitIngressEventSchema]
    benchmark_stats: Optional[TransitTimelineBenchmarkStats] = None




