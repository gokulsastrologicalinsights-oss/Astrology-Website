"""Input validation contracts and boundary sanitizers for the Marriage Compatibility Engine."""

from __future__ import annotations
import math
import re
from datetime import date, time
from typing import Any, Dict, Optional, Tuple

from app.schemas.common import BirthInput
from app.services.marriage_engine.models import Gender, MarriageChartContext


class MarriageValidationError(ValueError):
    """Raised when input data for marriage compatibility fails validation."""
    pass


class MissingChartDataError(MarriageValidationError):
    """Raised when mandatory astronomical positions are missing from a chart context."""
    pass


class InvalidCoordinateError(MarriageValidationError):
    """Raised when geographic coordinates are outside valid physical bounds."""
    pass


def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """Validate geographic coordinates.

    - Latitude must be in [-90.0, 90.0]
    - Longitude must be in [-180.0, 180.0]
    - Must be finite numbers
    """
    if not math.isfinite(latitude):
        raise InvalidCoordinateError(f"Latitude must be a finite number, got {latitude}")
    if not math.isfinite(longitude):
        raise InvalidCoordinateError(f"Longitude must be a finite number, got {longitude}")

    if latitude < -90.0 or latitude > 90.0:
        raise InvalidCoordinateError(f"Latitude {latitude} is outside valid range [-90.0, 90.0]")
    if longitude < -180.0 or longitude > 180.0:
        raise InvalidCoordinateError(f"Longitude {longitude} is outside valid range [-180.0, 180.0]")

    return latitude, longitude


def validate_timezone(tz_str: str) -> str:
    """Validate timezone string format."""
    s = (tz_str or "").strip()
    if not s:
        raise MarriageValidationError("Timezone string cannot be empty.")

    offset_pattern = re.compile(r"^[+-]\d{2}(:?\d{2})?$")
    if offset_pattern.match(s) or s.upper() == "UTC":
        return s

    iana_pattern = re.compile(r"^[A-Za-z0-9_\-+]+(/[A-Za-z0-9_\-+]+)*$")
    if not iana_pattern.match(s):
        raise MarriageValidationError(f"Invalid timezone format: '{s}'. Use IANA name ('Asia/Kolkata') or offset ('+05:30').")

    return s


def validate_gender(val: Optional[Any], default: Gender) -> Gender:
    """Normalize and validate gender string into Gender enum."""
    if val is None:
        return default
    if isinstance(val, Gender):
        return val
    raw = getattr(val, "value", val)
    cleaned = str(raw).strip().lower()
    if cleaned in ("male", "m", "groom", "man", "boy"):
        return Gender.MALE
    elif cleaned in ("female", "f", "bride", "woman", "girl"):
        return Gender.FEMALE
    else:
        raise MarriageValidationError(f"Invalid gender '{val}'. Allowed values are 'male' or 'female'.")


def validate_chart_context(ctx: MarriageChartContext) -> None:
    """Validate that a resolved MarriageChartContext contains all required astrological primitives."""
    if not ctx.person_id:
        raise MissingChartDataError("Chart context missing person_id.")

    # Ascendant validation
    if not math.isfinite(ctx.ascendant_degree) or not (0.0 <= ctx.ascendant_degree < 360.0):
        raise MissingChartDataError(f"Invalid ascendant degree {ctx.ascendant_degree}")
    if not (1 <= ctx.ascendant_sign_idx <= 12):
        raise MissingChartDataError(f"Invalid ascendant sign index {ctx.ascendant_sign_idx}")
    if not (0 <= ctx.ascendant_nakshatra_idx <= 26):
        raise MissingChartDataError(f"Invalid ascendant nakshatra index {ctx.ascendant_nakshatra_idx}")
    if not (1 <= ctx.ascendant_nakshatra_pada <= 4):
        raise MissingChartDataError(f"Invalid ascendant nakshatra pada {ctx.ascendant_nakshatra_pada}")

    # Moon validation
    if not math.isfinite(ctx.moon_degree) or not (0.0 <= ctx.moon_degree < 360.0):
        raise MissingChartDataError(f"Invalid Moon degree {ctx.moon_degree}")
    if not (1 <= ctx.moon_sign_idx <= 12):
        raise MissingChartDataError(f"Invalid Moon sign index {ctx.moon_sign_idx}")
    if not (0 <= ctx.moon_nakshatra_idx <= 26):
        raise MissingChartDataError(f"Invalid Moon nakshatra index {ctx.moon_nakshatra_idx}")
    if not (1 <= ctx.moon_nakshatra_pada <= 4):
        raise MissingChartDataError(f"Invalid Moon nakshatra pada {ctx.moon_nakshatra_pada}")

    # Essential planets
    required_grahas = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    for g_name in required_grahas:
        if g_name not in ctx.grahas:
            raise MissingChartDataError(f"Mandatory graha '{g_name}' is missing from chart context.")
        p = ctx.grahas[g_name]
        if not math.isfinite(p.longitude) or not (0.0 <= p.longitude < 360.0):
            raise MissingChartDataError(f"Invalid longitude {p.longitude} for {g_name}")
        if not (1 <= p.sign_index <= 12):
            raise MissingChartDataError(f"Invalid sign index {p.sign_index} for {g_name}")
        if not (1 <= p.house <= 12):
            raise MissingChartDataError(f"Invalid house number {p.house} for {g_name}")

    # Houses validation
    if len(ctx.houses) < 12:
        raise MissingChartDataError(f"Incomplete houses table: found {len(ctx.houses)} houses, expected 12.")
    for h_num in range(1, 13):
        if h_num not in ctx.houses:
            raise MissingChartDataError(f"Missing house #{h_num} in houses table.")
        h = ctx.houses[h_num]
        if not (1 <= h.sign_index <= 12):
            raise MissingChartDataError(f"Invalid sign index {h.sign_index} on house {h_num} cusp.")
