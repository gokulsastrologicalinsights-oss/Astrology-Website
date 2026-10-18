"""KP Transit Ingress and Sub-Lord Timeline Service.

Computes exact high-precision transit boundary crossings for Vedic planets using
the native XALEN ephemeris and Krishnamurti Paddhati (KP) 249 sub-division mathematics.

Detects:
1. Rashi Ingress (Zodiac sign change and sign lord change)
2. Nakshatra Ingress (Star change and star lord change)
3. KP Sub-Lord Ingress (Cuspal sub-lord change)

Uses deterministic bracketed bisection root-finding with adaptive distance-to-boundary
sampling to resolve crossing timestamps to sub-second clock accuracy without external
API calls or duplicate ephemeris engines.
"""

from __future__ import annotations

import time as pytime
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import xalen
from app.services.kp_engine.horary import (
    HoraryDiv,
    kp_divisions,
    kp_number_for_longitude,
)
from app.services.kp_engine.vedic import normalize_longitude, point_info
from app.services.timezone_utils import parse_offset_to_timedelta


# Planet name to XALEN body ID mapping
PLANET_IDS: Dict[str, int] = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Rahu": 9,   # Mean North Node
    "Ketu": 13,  # Mean South Node (Rahu + 180°)
}

DEFAULT_PLANETS: List[str] = ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"]

# Conservative theoretical maximum planetary speeds (deg/day) for adaptive step boundaries
MAX_PLANET_SPEEDS: Dict[str, float] = {
    "Moon": 16.0,
    "Mercury": 2.5,
    "Venus": 1.5,
    "Sun": 1.2,
    "Mars": 0.8,
    "Jupiter": 0.3,
    "Saturn": 0.15,
    "Rahu": 0.1,
    "Ketu": 0.1,
}

# Minimum step sizes in days to guarantee single-division bracketing
# Moon moves up to ~15.5 deg/day. In 10 min (1/144 day), it moves <= 0.11 deg << 0.67 deg (smallest sub)
MIN_STEP_DAYS: Dict[str, float] = {
    "Moon": 10.0 / 1440.0,     # 10 minutes
    "Mercury": 20.0 / 1440.0,  # 20 minutes
    "Venus": 20.0 / 1440.0,    # 20 minutes
    "Sun": 20.0 / 1440.0,      # 20 minutes
    "Mars": 20.0 / 1440.0,     # 20 minutes
    "Jupiter": 60.0 / 1440.0,  # 60 minutes
    "Saturn": 60.0 / 1440.0,   # 60 minutes
    "Rahu": 60.0 / 1440.0,     # 60 minutes
    "Ketu": 60.0 / 1440.0,     # 60 minutes
}

# Maximum step bounds in days when far from any division boundary
MAX_STEP_DAYS: Dict[str, float] = {
    "Moon": 30.0 / 1440.0,     # 30 minutes
    "Mercury": 4.0 / 24.0,     # 4 hours
    "Venus": 4.0 / 24.0,       # 4 hours
    "Sun": 6.0 / 24.0,         # 6 hours
    "Mars": 4.0 / 24.0,        # 4 hours
    "Jupiter": 12.0 / 24.0,    # 12 hours
    "Saturn": 24.0 / 24.0,     # 24 hours (1 day)
    "Rahu": 24.0 / 24.0,       # 24 hours (1 day)
    "Ketu": 24.0 / 24.0,       # 24 hours (1 day)
}


@dataclass(frozen=True)
class TransitIngressEvent:
    """Represents a single planetary boundary crossing event in the timeline."""
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TransitTimelineResult:
    """Full transit timeline result with metadata and benchmark diagnostics."""
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
    events: List[TransitIngressEvent]
    truncated: bool = False
    benchmark_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["events"] = [e.to_dict() for e in self.events]
        return data


def resolve_start_datetime(
    start_date: date | datetime,
    start_time: Optional[time] = None,
    tz_string: str = "UTC",
) -> Tuple[datetime, datetime, float, ZoneInfo | dt_timezone, str, float]:
    """Parse start date/time and timezone into:
    (local_dt, utc_dt, start_jd, tz_obj, tz_name, utc_offset_hours).
    """
    tz_clean = tz_string.strip() if tz_string else "UTC"

    # Resolve timezone object
    if tz_clean.upper() in ("UTC", "Z", "+00:00", "-00:00", "+00", "-00"):
        tz_obj = dt_timezone.utc
        tz_name = "UTC"
        offset_hours = 0.0
    elif tz_clean.startswith(("+", "-")):
        offset_td = parse_offset_to_timedelta(tz_clean)
        tz_obj = dt_timezone(offset_td)
        tz_name = tz_clean
        offset_hours = offset_td.total_seconds() / 3600.0
    else:
        try:
            tz_obj = ZoneInfo(tz_clean)
            tz_name = tz_clean
            ref_dt = datetime.combine(
                start_date if isinstance(start_date, date) else start_date.date(),
                start_time or time(0, 0),
                tzinfo=tz_obj,
            )
            offset_td = ref_dt.utcoffset()
            offset_hours = offset_td.total_seconds() / 3600.0 if offset_td else 0.0
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Invalid timezone: '{tz_string}'. Provide a valid IANA name or offset.") from exc

    # Resolve local and UTC datetimes
    if isinstance(start_date, datetime):
        if start_date.tzinfo is None:
            local_dt = start_date.replace(tzinfo=tz_obj)
        else:
            local_dt = start_date.astimezone(tz_obj)
    else:
        t = start_time or time(0, 0, 0)
        local_dt = datetime.combine(start_date, t, tzinfo=tz_obj)

    utc_dt = local_dt.astimezone(dt_timezone.utc)
    offset_td = local_dt.utcoffset()
    offset_hours = offset_td.total_seconds() / 3600.0 if offset_td else 0.0

    hour_float = (
        utc_dt.hour
        + (utc_dt.minute / 60.0)
        + (utc_dt.second / 3600.0)
        + (utc_dt.microsecond / 3_600_000_000.0)
    )
    start_jd = xalen.julian_day(utc_dt.year, utc_dt.month, utc_dt.day, hour_float)

    return local_dt, utc_dt, start_jd, tz_obj, tz_name, offset_hours


def jd_to_datetimes(
    jd: float,
    target_tz: ZoneInfo | dt_timezone,
) -> Tuple[datetime, datetime]:
    """Convert Julian Day to (utc_datetime, local_datetime)."""
    # Julian Day 2440587.5 is Unix epoch 1970-01-01 00:00:00 UTC
    unix_seconds = (jd - 2440587.5) * 86400.0
    utc_dt = datetime.fromtimestamp(unix_seconds, tz=dt_timezone.utc)
    local_dt = utc_dt.astimezone(target_tz)
    return utc_dt, local_dt


def _angle_diff(angle: float, target: float) -> float:
    """Signed angular distance in (-180, +180] degrees from target to angle."""
    return (angle - target + 180.0) % 360.0 - 180.0


def _bisect_boundary(
    body_id: int,
    t_start: float,
    t_end: float,
    target_lon: float,
    ayanamsa_id: int,
    tol_seconds: float = 0.5,
    max_iter: int = 30,
) -> Tuple[float, int]:
    """Use bracketed bisection to find exact Julian Day where planet crosses target_lon.

    Returns (jd_cross, iterations_count).
    """
    tol_days = tol_seconds / 86400.0
    a, b = t_start, t_end

    def f(t: float) -> float:
        lon = xalen.planet_longitude(t, body_id, True, ayanamsa_id)
        return _angle_diff(lon, target_lon)

    fa = f(a)
    fb = f(b)

    # Check if boundary is already within tolerance
    if abs(fa) < 1e-7:
        return a, 1
    if abs(fb) < 1e-7:
        return b, 1

    iterations = 0
    while (b - a) > tol_days and iterations < max_iter:
        mid = 0.5 * (a + b)
        iterations += 1
        fmid = f(mid)

        if abs(fmid) < 1e-7:
            return mid, iterations

        if fa * fmid <= 0.0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    jd_cross = 0.5 * (a + b)
    return jd_cross, iterations


def _scan_planet_timeline(
    planet_name: str,
    body_id: int,
    start_jd: float,
    end_jd: float,
    ayanamsa_id: int,
    target_tz: ZoneInfo | dt_timezone,
    divs: List[HoraryDiv],
    precision_seconds: float = 0.5,
) -> Tuple[List[TransitIngressEvent], int, int]:
    """Scan timeline for a single planet using bracketed adaptive distance-to-boundary sampling.

    Returns (events, step_evaluations, bisection_evaluations).
    """
    events: List[TransitIngressEvent] = []
    step_evals = 0
    bisection_evals = 0

    v_max = MAX_PLANET_SPEEDS.get(planet_name, 1.5)
    s_min = MIN_STEP_DAYS.get(planet_name, 20.0 / 1440.0)
    s_max = MAX_STEP_DAYS.get(planet_name, 4.0 / 24.0)

    curr_jd = start_jd
    curr_lon = xalen.planet_longitude(curr_jd, body_id, True, ayanamsa_id)
    curr_num = kp_number_for_longitude(curr_lon)
    step_evals += 1

    while curr_jd < end_jd:
        # Adaptive step based on distance to current division boundaries
        d = divs[curr_num - 1]
        dist_start = (curr_lon - d.start_deg) % 360.0
        dist_end = (d.end_deg - curr_lon) % 360.0
        dist = min(dist_start, dist_end)

        safe_step = max(min((dist / v_max) * 0.6, s_max), s_min)
        next_jd = min(curr_jd + safe_step, end_jd)

        next_lon = xalen.planet_longitude(next_jd, body_id, True, ayanamsa_id)
        next_num = kp_number_for_longitude(next_lon)
        step_evals += 1

        if curr_num != next_num:
            # Recursive bracket resolution if step spanned more than 1 division
            def resolve_interval(t1: float, t2: float, d1: int, d2: int):
                nonlocal bisection_evals, step_evals
                if d1 == d2:
                    return

                # Check if d1 and d2 are direct neighbors (or 249 <-> 1 wrap)
                is_direct_step = (d2 == d1 + 1) or (d1 == 249 and d2 == 1)
                is_retro_step = (d2 == d1 - 1) or (d1 == 1 and d2 == 249)

                if is_direct_step or is_retro_step:
                    div1 = divs[d1 - 1]
                    div2 = divs[d2 - 1]

                    if is_direct_step:
                        target_lon = 0.0 if d1 == 249 else div1.end_deg
                    else:
                        target_lon = 0.0 if d1 == 1 else div1.start_deg

                    # Bisect
                    jd_cross, iters = _bisect_boundary(
                        body_id=body_id,
                        t_start=t1,
                        t_end=t2,
                        target_lon=target_lon,
                        ayanamsa_id=ayanamsa_id,
                        tol_seconds=precision_seconds,
                    )
                    bisection_evals += iters

                    # Compute state at crossing
                    pos_at_cross = xalen.planet_position(jd_cross, body_id, True, ayanamsa_id)
                    speed = pos_at_cross["lon_speed"]
                    is_retro = pos_at_cross["is_retrograde"]

                    utc_dt, local_dt = jd_to_datetimes(jd_cross, target_tz)

                    is_rashi = div1.sign != div2.sign
                    is_nakshatra = div1.star != div2.star
                    is_sub = (div1.sub_lord != div2.sub_lord) or is_rashi

                    if is_rashi:
                        b_type = "rashi"
                    elif is_nakshatra:
                        b_type = "nakshatra"
                    else:
                        b_type = "sub_lord"

                    event = TransitIngressEvent(
                        planet=planet_name,
                        planet_id=body_id,
                        utc_datetime=utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        local_datetime=local_dt.isoformat(),
                        jd=jd_cross,
                        boundary_type=b_type,
                        boundary_longitude=target_lon,
                        is_retrograde=is_retro,
                        speed_deg_per_day=speed,
                        from_sign=div1.sign,
                        to_sign=div2.sign,
                        from_sign_lord=div1.sign_lord,
                        to_sign_lord=div2.sign_lord,
                        is_rashi_boundary=is_rashi,
                        from_nakshatra=div1.star,
                        to_nakshatra=div2.star,
                        from_star_lord=div1.star_lord,
                        to_star_lord=div2.star_lord,
                        is_nakshatra_boundary=is_nakshatra,
                        from_sub_lord=div1.sub_lord,
                        to_sub_lord=div2.sub_lord,
                        from_kp_number=div1.number,
                        to_kp_number=div2.number,
                        is_sub_lord_boundary=is_sub,
                        calculation_precision_seconds=precision_seconds,
                    )
                    events.append(event)
                else:
                    # Subdivide interval to isolate single boundary crossings
                    t_mid = 0.5 * (t1 + t2)
                    l_mid = xalen.planet_longitude(t_mid, body_id, True, ayanamsa_id)
                    d_mid = kp_number_for_longitude(l_mid)
                    step_evals += 1
                    resolve_interval(t1, t_mid, d1, d_mid)
                    resolve_interval(t_mid, t2, d_mid, d2)

            resolve_interval(curr_jd, next_jd, curr_num, next_num)
            curr_num = next_num
            curr_lon = next_lon

        curr_jd = next_jd

    return events, step_evals, bisection_evals


def compute_transit_timeline(
    start_date: date | datetime,
    start_time: Optional[time] = None,
    forecast_days: Optional[int | float] = None,
    timezone_str: str = "UTC",
    planets: Optional[List[str]] = None,
    ayanamsa_id: int = 0,
    precision_seconds: float = 0.5,
    end_date: Optional[date | datetime] = None,
    end_time: Optional[time] = None,
    max_events: Optional[int] = None,
) -> TransitTimelineResult:
    """Compute high-precision KP Transit Timeline over a 7-30 day window.

    Args:
        start_date: Starting calendar date or datetime.
        start_time: Optional time of day (defaults to 00:00:00).
        forecast_days: Length of timeline window (7 to 30 days). Used if end_date is None.
        timezone_str: Local timezone identifier (IANA or numeric offset).
        planets: List of planets to analyze (default: Moon, Sun, Jupiter, Saturn, Rahu, Ketu).
        ayanamsa_id: 0 = Lahiri (default), 1 = Krishnamurti.
        precision_seconds: Convergence tolerance in seconds for bisection (default: 0.5s).
        end_date: Optional ending calendar date or datetime.
        end_time: Optional ending time of day.
        max_events: Optional limit on the number of returned events (for truncation).

    Returns:
        TransitTimelineResult containing sorted ingress events and benchmark metrics.
    """
    t_start_bench = pytime.perf_counter()

    selected_planets = planets if planets is not None else DEFAULT_PLANETS
    if not selected_planets:
        raise ValueError("At least one planet must be selected")

    for p in selected_planets:
        if p not in PLANET_IDS:
            raise ValueError(f"Unsupported planet: '{p}'. Supported planets: {list(PLANET_IDS.keys())}")

    # Resolve start datetimes and JD
    local_start_dt, utc_start_dt, start_jd, tz_obj, tz_name, utc_offset_hours = resolve_start_datetime(
        start_date=start_date,
        start_time=start_time,
        tz_string=timezone_str,
    )

    # Resolve end datetimes and JD
    if end_date is not None:
        local_end_dt, utc_end_dt, end_jd, _, _, _ = resolve_start_datetime(
            start_date=end_date,
            start_time=end_time or time(0, 0, 0),
            tz_string=timezone_str,
        )
        if end_jd <= start_jd:
            raise ValueError("end_date must be strictly after start_date")
        calc_days = end_jd - start_jd
        if calc_days < 7.0 - 1e-4 or calc_days > 30.0 + 1e-4:
            raise ValueError(f"forecast window must be between 7 and 30 days (got {calc_days:.2f} days)")
        effective_forecast_days = round(calc_days, 4)
    else:
        f_days = 7.0 if forecast_days is None else float(forecast_days)
        if f_days < 7.0 or f_days > 30.0:
            raise ValueError(f"forecast_days must be between 7 and 30 (got {f_days})")
        effective_forecast_days = f_days
        end_jd = start_jd + effective_forecast_days
        utc_end_dt, local_end_dt = jd_to_datetimes(end_jd, tz_obj)

    # Pre-cached KP divisions
    divs = kp_divisions()

    all_events: List[TransitIngressEvent] = []
    total_step_evals = 0
    total_bisection_evals = 0

    ayanamsa_name = "Lahiri" if ayanamsa_id == 0 else ("KP" if ayanamsa_id == 1 else f"Ayanamsa_{ayanamsa_id}")

    for planet in selected_planets:
        body_id = PLANET_IDS[planet]

        p_events, s_evals, b_evals = _scan_planet_timeline(
            planet_name=planet,
            body_id=body_id,
            start_jd=start_jd,
            end_jd=end_jd,
            ayanamsa_id=ayanamsa_id,
            target_tz=tz_obj,
            divs=divs,
            precision_seconds=precision_seconds,
        )
        all_events.extend(p_events)
        total_step_evals += s_evals
        total_bisection_evals += b_evals

    # Chronologically sort all events by Julian Day
    all_events.sort(key=lambda ev: ev.jd)

    # Apply max_events limit if specified
    truncated = False
    if max_events is not None and max_events > 0:
        if len(all_events) > max_events:
            all_events = all_events[:max_events]
            truncated = True

    t_end_bench = pytime.perf_counter()
    duration_ms = (t_end_bench - t_start_bench) * 1000.0

    return TransitTimelineResult(
        start_time_utc=utc_start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        start_time_local=local_start_dt.isoformat(),
        end_time_utc=utc_end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_time_local=local_end_dt.isoformat(),
        timezone=tz_name,
        utc_offset_hours=utc_offset_hours,
        ayanamsa_id=ayanamsa_id,
        ayanamsa_name=ayanamsa_name,
        forecast_days=effective_forecast_days,
        planets_analyzed=selected_planets,
        total_events=len(all_events),
        events=all_events,
        truncated=truncated,
        benchmark_stats={
            "duration_ms": round(duration_ms, 2),
            "total_evaluations": total_step_evals + total_bisection_evals,
            "step_evaluations": total_step_evals,
            "bisection_evaluations": total_bisection_evals,
        },
    )
