"""Common Pydantic models for birth inputs, location, and API errors."""

from datetime import date, time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
import re


class BirthInput(BaseModel):
    """Input payload representing a birth event with location and timezone."""
    birth_date: date = Field(
        ...,
        description="Birth date in ISO format YYYY-MM-DD",
        examples=["1995-10-24"]
    )
    birth_time: time = Field(
        ...,
        description="Local birth time in ISO format HH:MM or HH:MM:SS (24-hour)",
        examples=["14:30:00"]
    )
    timezone: str = Field(
        ...,
        description="IANA time zone name (e.g. 'Asia/Kolkata', 'America/New_York') or UTC offset string (e.g. '+05:30', '-04:00')",
        examples=["Asia/Kolkata"]
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographic latitude in decimal degrees (-90 to +90)",
        examples=[13.0827]
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographic longitude in decimal degrees (-180 to +180, positive East)",
        examples=[80.2707]
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone_format(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("timezone cannot be empty")
        # Check if valid offset pattern: ±HH:MM or ±HHMM or ±HH
        offset_pattern = re.compile(r"^[+-]\d{2}(:?\d{2})?$")
        if offset_pattern.match(v) or v.upper() == "UTC":
            return v
        # Otherwise, basic string sanity check for IANA zone names (letters, underscores, slashes)
        iana_pattern = re.compile(r"^[A-Za-z0-9_\-+]+(/[A-Za-z0-9_\-+]+)*$")
        if not iana_pattern.match(v):
            raise ValueError(f"Invalid timezone format: '{v}'. Use IANA name ('Asia/Kolkata') or offset ('+05:30').")
        return v


class CalculationMetadata(BaseModel):
    """Metadata describing the calculated astronomical context."""
    engine: str = "XALEN 0.6.0 (Rust)"
    birth_utc_iso: str
    julian_day_ut1: float
    local_timezone: Optional[str] = None
    utc_offset_hours: Optional[float] = None
    coordinates: Optional[Dict[str, float]] = None
    ayanamsa_id: int
    ayanamsa_name: str
    ayanamsa_deg: float = 0.0
    house_system_id: int
    house_system_name: str
    calculation_frame: str = "Geocentric Sidereal"
    notes: List[str] = Field(default_factory=list)



class ErrorResponse(BaseModel):
    """Structured error model returned on failures."""
    error: str
    detail: Optional[str] = None
    code: str = "BAD_REQUEST"
