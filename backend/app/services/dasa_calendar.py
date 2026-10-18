"""Calendar date and person age calculation utilities for Vimshottari Dasa.

Provides exact Gregorian date conversion from Julian Day and deterministic
calendar age calculation (years, months, days) honoring leap years, month boundaries,
and timezone offsets.
"""

import math
import calendar
from datetime import date
from typing import Optional, Tuple, Dict, Any


def jd_to_gregorian_datetime(
    jd: float,
    utc_offset_hours: float = 0.0,
) -> Tuple[int, int, int, int, int, int]:
    """Convert a Julian Day (UT1) into Gregorian (year, month, day, hour, minute, second).

    Uses the canonical astronomical algorithm with optional local timezone offset.
    """
    if jd is None or math.isnan(jd):
        raise ValueError("Invalid Julian Day")

    # Shift by local timezone offset if specified
    local_jd = jd + (utc_offset_hours / 24.0)

    i = math.floor(local_jd + 0.5)
    f = local_jd + 0.5 - i

    j = i + 32044
    k = math.floor((4 * j + 3) / 146097)
    l = j - math.floor((146097 * k) / 4)
    m = math.floor((4 * l + 3) / 1461)
    n = l - math.floor((1461 * m) / 4)
    p = math.floor((5 * n + 2) / 153)

    day = n - math.floor((153 * p + 2) / 5) + 1
    month = p + 3 - 12 * math.floor(p / 10)
    year = 100 * k + m - 4800 + math.floor(p / 10)

    total_seconds = int(round(f * 86400.0))
    if total_seconds >= 86400:
        total_seconds = 86399
    elif total_seconds < 0:
        total_seconds = 0

    hour = total_seconds // 3600
    minute = (total_seconds % 3600) // 60
    second = total_seconds % 60

    return int(year), int(month), int(day), int(hour), int(minute), int(second)


def gregorian_to_iso(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    include_time: bool = False,
) -> str:
    """Format calendar components into an ISO 8601 string."""
    if include_time:
        return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"
    return f"{year:04d}-{month:02d}-{day:02d}"


def calculate_calendar_age(
    birth_y: int,
    birth_m: int,
    birth_d: int,
    target_y: int,
    target_m: int,
    target_d: int,
) -> Optional[Tuple[int, int, int]]:
    """Calculate exact calendar age as (years, months, days) between two Gregorian dates.

    Honors variable month lengths, leap years, and calendar anniversary boundaries.
    Returns None if target date is before birth date.
    """
    if (target_y, target_m, target_d) < (birth_y, birth_m, birth_d):
        return None

    y = target_y - birth_y
    m = target_m - birth_m
    d = target_d - birth_d

    cur_y = target_y
    cur_m = target_m

    while d < 0:
        m -= 1
        cur_m -= 1
        if cur_m == 0:
            cur_m = 12
            cur_y -= 1
        days_in_prev = calendar.monthrange(cur_y, cur_m)[1]
        d += days_in_prev

    if m < 0:
        y -= 1
        m += 12

    return y, m, d


def format_calendar_age(
    age_tuple: Optional[Tuple[int, int, int]],
    lang: str = "en",
) -> str:
    """Format an age tuple (years, months, days) into readable text."""
    if age_tuple is None:
        return "வயது கிடைக்கவில்லை" if lang == "ta" else "Age unavailable"

    years, months, days = age_tuple

    if lang == "ta":
        y_unit = "ஆண்டுகள்" if years != 1 else "ஆண்டு"
        m_unit = "மாதங்கள்" if months != 1 else "மாதம்"
        d_unit = "நாட்கள்" if days != 1 else "நாள்"
        return f"{years} {y_unit}, {months} {m_unit}, {days} {d_unit}"

    y_unit = "years" if years != 1 else "year"
    m_unit = "months" if months != 1 else "month"
    d_unit = "days" if days != 1 else "day"
    return f"{years} {y_unit}, {months} {m_unit}, {days} {d_unit}"


def age_tuple_to_dict(
    age_tuple: Optional[Tuple[int, int, int]],
) -> Optional[Dict[str, int]]:
    """Convert an age tuple into a structured dictionary."""
    if age_tuple is None:
        return None
    return {
        "years": age_tuple[0],
        "months": age_tuple[1],
        "days": age_tuple[2],
    }
