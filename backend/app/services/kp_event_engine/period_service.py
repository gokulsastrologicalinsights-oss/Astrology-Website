"""KP Event Prediction Engine - Period Service.

Handles date parsing, chronological sorting, hierarchy extraction,
and timezone-aware running period detection with boundary-inclusive comparisons.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from zoneinfo import ZoneInfo
from .signification_normalizer import normalize_planet_name


@dataclass
class PeriodHierarchyItem:
    period_key: str
    mahadasha_lord: str
    bhukti_lord: str
    antara_lord: Optional[str]
    start_date: str
    end_date: str
    start_date_obj: Optional[date]
    end_date_obj: Optional[date]
    is_running: bool
    status: str = "ok"
    missing_fields: List[str] = None

    def __post_init__(self):
        if self.missing_fields is None:
            self.missing_fields = []


def parse_date_only(date_str: Optional[str]) -> Optional[date]:
    """Parses date string (YYYY-MM-DD or ISO timestamp) to a date object."""
    if not date_str:
        return None
    try:
        # Strip time if present
        clean_str = str(date_str).strip()
        if "T" in clean_str:
            clean_str = clean_str.split("T")[0]
        elif " " in clean_str:
            clean_str = clean_str.split(" ")[0]
        return date.fromisoformat(clean_str)
    except (ValueError, TypeError):
        return None


def get_current_date_in_tz(timezone_str: Optional[str] = None) -> date:
    """Returns today's date in the specified timezone (defaults to Asia/Kolkata or UTC)."""
    tz_name = (timezone_str or "Asia/Kolkata").strip()
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        try:
            tz = ZoneInfo("UTC")
        except Exception:
            return datetime.now().date()
    return datetime.now(tz).date()


def is_date_within_bounds(
    current_dt: date,
    start_dt: Optional[date],
    end_dt: Optional[date],
) -> bool:
    """Inclusive date-only boundary comparison: start_dt <= current_dt <= end_dt."""
    if start_dt is None or end_dt is None:
        return False
    return start_dt <= current_dt <= end_dt


def detect_running_period(
    start_date: Optional[str],
    end_date: Optional[str],
    current_date: Optional[str] = None,
    timezone_str: Optional[str] = None,
) -> bool:
    """Determines whether current date falls within [start_date, end_date] inclusively."""
    s_dt = parse_date_only(start_date)
    e_dt = parse_date_only(end_date)
    if not s_dt or not e_dt:
        return False

    c_dt = parse_date_only(current_date) if current_date else get_current_date_in_tz(timezone_str)
    if not c_dt:
        return False

    return is_date_within_bounds(c_dt, s_dt, e_dt)


def normalize_period_hierarchy(
    raw_periods: List[Dict[str, Any]],
    current_date: Optional[str] = None,
    timezone_str: Optional[str] = None,
) -> List[PeriodHierarchyItem]:
    """Validates and normalizes period list into chronological order with running detection."""
    c_dt = parse_date_only(current_date) if current_date else get_current_date_in_tz(timezone_str)

    items: List[PeriodHierarchyItem] = []
    for p in raw_periods:
        if hasattr(p, "model_dump"):
            p = p.model_dump()
        elif hasattr(p, "dict"):
            p = p.dict()

        md = normalize_planet_name(p.get("mahadasha_lord") or p.get("md_lord") or p.get("lord"))
        bd = normalize_planet_name(p.get("bhukti_lord") or p.get("ad_lord") or p.get("sub_lord"))
        ad = normalize_planet_name(p.get("antara_lord") or p.get("pd_lord"))

        s_str = str(p.get("start_date") or p.get("start") or "")
        e_str = str(p.get("end_date") or p.get("end") or "")
        s_dt = parse_date_only(s_str)
        e_dt = parse_date_only(e_str)

        missing_fields: List[str] = []
        if not md:
            missing_fields.append("mahadasha_lord")
        if not bd:
            missing_fields.append("bhukti_lord")
        if not s_dt:
            missing_fields.append("start_date")
        if not e_dt:
            missing_fields.append("end_date")

        period_key = f"{md or 'Unknown'}-{bd or 'Unknown'}"
        if ad:
            period_key += f"-{ad}"

        is_running = False
        status = "ok"
        if missing_fields:
            status = "missing_data"
        elif c_dt and s_dt and e_dt:
            is_running = is_date_within_bounds(c_dt, s_dt, e_dt)

        items.append(
            PeriodHierarchyItem(
                period_key=period_key,
                mahadasha_lord=md or "",
                bhukti_lord=bd or "",
                antara_lord=ad,
                start_date=s_str,
                end_date=e_str,
                start_date_obj=s_dt,
                end_date_obj=e_dt,
                is_running=is_running,
                status=status,
                missing_fields=missing_fields,
            )
        )

    # Sort chronologically by start date (missing dates at end)
    items.sort(key=lambda item: item.start_date_obj or date.max)
    return items
