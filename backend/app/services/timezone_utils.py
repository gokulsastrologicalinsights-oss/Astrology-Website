"""Timezone parsing and Julian Day conversion utilities."""

import re
from datetime import date, time, datetime, timezone as dt_timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Tuple
import xalen


def parse_offset_to_timedelta(offset_str: str) -> timedelta:
    """Parse string offset like '+05:30', '-04:00', '+0530', '+05' into a timedelta."""
    pattern = re.compile(r"^([+-])(\d{2}):?(\d{2})?$")
    match = pattern.match(offset_str.strip())
    if not match:
        raise ValueError(f"Invalid numeric timezone offset: '{offset_str}'. Expected format like '+05:30' or '-04:00'")
    sign = 1 if match.group(1) == "+" else -1
    hours = int(match.group(2))
    minutes = int(match.group(3)) if match.group(3) else 0
    if hours > 14 or minutes > 59:
        raise ValueError(f"Timezone offset out of range: '{offset_str}'")
    return timedelta(hours=sign * hours, minutes=sign * minutes)


def resolve_birth_datetime(
    birth_date: date,
    birth_time: time,
    tz_string: str,
) -> Tuple[datetime, datetime, float, str, float]:
    """Convert local birth date, time, and timezone string into:
    (local_datetime, utc_datetime, julian_day, timezone_identifier, utc_offset_hours)
    """
    tz_clean = tz_string.strip()
    if tz_clean.upper() in ("UTC", "Z", "+00:00", "-00:00", "+00", "-00"):
        local_dt = datetime.combine(birth_date, birth_time, tzinfo=dt_timezone.utc)
        utc_dt = local_dt
        tz_name = "UTC"
        offset_hours = 0.0
    elif tz_clean.startswith(("+", "-")):
        offset_td = parse_offset_to_timedelta(tz_clean)
        custom_tz = dt_timezone(offset_td)
        local_dt = datetime.combine(birth_date, birth_time, tzinfo=custom_tz)
        utc_dt = local_dt.astimezone(dt_timezone.utc)
        tz_name = tz_clean
        offset_hours = offset_td.total_seconds() / 3600.0
    else:
        try:
            iana_tz = ZoneInfo(tz_clean)
            local_dt = datetime.combine(birth_date, birth_time, tzinfo=iana_tz)
            utc_dt = local_dt.astimezone(dt_timezone.utc)
            tz_name = tz_clean
            offset_td = local_dt.utcoffset()
            offset_hours = offset_td.total_seconds() / 3600.0 if offset_td else 0.0
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Unknown timezone: '{tz_string}'. Provide a valid IANA name (e.g. 'Asia/Kolkata') or offset ('+05:30')") from exc

    # Compute fractional hour in UTC
    hour_float = (
        utc_dt.hour
        + (utc_dt.minute / 60.0)
        + (utc_dt.second / 3600.0)
        + (utc_dt.microsecond / 3_600_000_000.0)
    )

    jd = xalen.julian_day(utc_dt.year, utc_dt.month, utc_dt.day, hour_float)
    return local_dt, utc_dt, jd, tz_name, offset_hours


def local_to_utc_and_jd(
    birth_date: date,
    birth_time: time,
    tz_string: str,
) -> Tuple[datetime, float]:
    """Convert a local birth date, time, and timezone string into UTC datetime and Julian Day (UT1)."""
    _, utc_dt, jd, _, _ = resolve_birth_datetime(birth_date, birth_time, tz_string)
    return utc_dt, jd
