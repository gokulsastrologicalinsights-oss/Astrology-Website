"""Muhurta Date-Range Scanner and Candidate Ranking Engine.

Searches across the specified date range and identifies candidate intervals
that satisfy occasion rules, ranking them transparently by eligibility and score.
"""

from datetime import datetime, date, time, timedelta, timezone
from typing import Dict, Any, List, Optional
from zoneinfo import ZoneInfo
import uuid

from app.services.muhurta_engine.astronomy import (
    calculate_daily_panchangam,
    get_slot_lagna_and_planets,
)
from app.services.muhurta_engine.rules import evaluate_muhurta_slot
from app.services.muhurta_engine.occasions import get_occasion_by_code, DEFAULT_OCCASIONS


def find_candidate_muhurtas(
    occasion_code: str,
    start_date: date,
    end_date: date,
    latitude: float,
    longitude: float,
    timezone_str: str,
    preferred_time_range: str = "morning",  # "morning" (06-12), "afternoon" (12-16), "evening" (16-20), "all_day" (06-20)
    ayanamsa_id: int = 0,
    custom_rules: Optional[Dict[str, Any]] = None,
    birth_details: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Finds and ranks candidate Muhurta intervals across the date range.

    Returns:
        Dict containing:
        - occasion: Dict
        - search_params: Dict
        - total_candidates: int
        - candidates: List[Dict] (ranked)
        - calendar_summary: Dict[date_str, Dict] (for calendar badge display)
    """
    tz = ZoneInfo(timezone_str)
    occasion = get_occasion_by_code(occasion_code)
    if not occasion:
        occasion = DEFAULT_OCCASIONS[0]

    rules = custom_rules or occasion.get("rules", {})

    # Define local hour boundaries based on preference
    if preferred_time_range == "morning":
        hour_start, hour_end = 6, 12
    elif preferred_time_range == "afternoon":
        hour_start, hour_end = 12, 16
    elif preferred_time_range == "evening":
        hour_start, hour_end = 16, 20
    else:  # all_day or custom
        hour_start, hour_end = 6, 20

    candidates: List[Dict[str, Any]] = []
    calendar_summary: Dict[str, Dict[str, Any]] = {}

    current_date = start_date
    delta_day = timedelta(days=1)

    while current_date <= end_date:
        date_str = current_date.isoformat()
        daily_panchang = calculate_daily_panchangam(
            event_date=current_date,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            ayanamsa_id=ayanamsa_id,
        )

        sunrise_dt = datetime.fromisoformat(daily_panchang["astronomical"]["sunrise_utc"]).astimezone(tz)
        sunset_dt = datetime.fromisoformat(daily_panchang["astronomical"]["sunset_utc"]).astimezone(tz)

        # Generate candidate slot intervals (approx 45 to 60 minutes) between sunrise and sunset
        # within preferred time range
        day_candidates: List[Dict[str, Any]] = []

        slot_start_hour = max(hour_start, sunrise_dt.hour)
        slot_end_hour = min(hour_end, sunset_dt.hour + 1)

        # Iterate in 45-minute steps
        step_minutes = 45
        cur_slot_start = datetime(current_date.year, current_date.month, current_date.day, slot_start_hour, 0, tzinfo=tz)
        day_limit_time = datetime(current_date.year, current_date.month, current_date.day, slot_end_hour, 0, tzinfo=tz)

        while cur_slot_start + timedelta(minutes=step_minutes) <= day_limit_time:
            cur_slot_end = cur_slot_start + timedelta(minutes=step_minutes)
            slot_mid = cur_slot_start + timedelta(minutes=step_minutes / 2.0)

            slot_start_utc = cur_slot_start.astimezone(timezone.utc)
            slot_end_utc = cur_slot_end.astimezone(timezone.utc)
            slot_mid_utc = slot_mid.astimezone(timezone.utc)

            # Lagna & Planets at midpoint of candidate window
            lagna_planets = get_slot_lagna_and_planets(
                slot_utc=slot_mid_utc,
                latitude=latitude,
                longitude=longitude,
                ayanamsa_id=ayanamsa_id,
            )

            # Evaluate against rules
            eval_res = evaluate_muhurta_slot(
                slot_start_utc=slot_start_utc,
                slot_end_utc=slot_end_utc,
                daily_panchang=daily_panchang,
                lagna_planets=lagna_planets,
                rules=rules,
                birth_details=birth_details,
            )

            candidate_obj = {
                "id": str(uuid.uuid4()),
                "event_date": date_str,
                "weekday": daily_panchang["vara"]["name_en"],
                "weekday_ta": daily_panchang["vara"]["name_ta"],
                "start_time_local": cur_slot_start.strftime("%H:%M"),
                "end_time_local": cur_slot_end.strftime("%H:%M"),
                "start_time_utc": slot_start_utc.isoformat(),
                "end_time_utc": slot_end_utc.isoformat(),
                "duration_minutes": step_minutes,
                "status": eval_res["status"],
                "score": eval_res["score"],
                "explanation": eval_res["explanation"],
                "passed_rules": eval_res["passed_rules"],
                "failed_rules": eval_res["failed_rules"],
                "advisories": eval_res["advisories"],
                "incomplete_checks": eval_res["incomplete_checks"],
                "tithi": daily_panchang["tithi"],
                "nakshatra": daily_panchang["nakshatra"],
                "yoga": daily_panchang["yoga"],
                "karana": daily_panchang["karana"],
                "ascendant": lagna_planets["ascendant"],
                "planets": lagna_planets["planets"],
                "inauspicious_periods": {
                    "rahu_kalam": {
                        "start_local": datetime.fromisoformat(daily_panchang["inauspicious_periods"]["rahu_kalam"]["start_utc"]).astimezone(tz).strftime("%H:%M"),
                        "end_local": datetime.fromisoformat(daily_panchang["inauspicious_periods"]["rahu_kalam"]["end_utc"]).astimezone(tz).strftime("%H:%M"),
                    },
                    "yamagandam": {
                        "start_local": datetime.fromisoformat(daily_panchang["inauspicious_periods"]["yamagandam"]["start_utc"]).astimezone(tz).strftime("%H:%M"),
                        "end_local": datetime.fromisoformat(daily_panchang["inauspicious_periods"]["yamagandam"]["end_utc"]).astimezone(tz).strftime("%H:%M"),
                    },
                    "varjyam": {
                        "start_local": datetime.fromisoformat(daily_panchang["varjyam"]["start_utc"]).astimezone(tz).strftime("%H:%M"),
                        "end_local": datetime.fromisoformat(daily_panchang["varjyam"]["end_utc"]).astimezone(tz).strftime("%H:%M"),
                    },
                },
                "auspicious_periods": {
                    "abhijit": {
                        "start_local": datetime.fromisoformat(daily_panchang["auspicious_periods"]["abhijit"]["start_utc"]).astimezone(tz).strftime("%H:%M"),
                        "end_local": datetime.fromisoformat(daily_panchang["auspicious_periods"]["abhijit"]["end_utc"]).astimezone(tz).strftime("%H:%M"),
                    },
                    "amrita_kalam": {
                        "start_local": datetime.fromisoformat(daily_panchang["auspicious_periods"]["amrita_kalam"]["start_utc"]).astimezone(tz).strftime("%H:%M"),
                        "end_local": datetime.fromisoformat(daily_panchang["auspicious_periods"]["amrita_kalam"]["end_utc"]).astimezone(tz).strftime("%H:%M"),
                    },
                },
            }

            day_candidates.append(candidate_obj)
            candidates.append(candidate_obj)
            cur_slot_start += timedelta(minutes=step_minutes)

        # Calendar summary status for this date
        if any(c["status"] == "meets_configured_rules" for c in day_candidates):
            day_badge = "auspicious"
        elif any(c["status"] == "meets_rules_with_advisories" for c in day_candidates):
            day_badge = "moderate"
        elif any(c["status"] == "incomplete" for c in day_candidates):
            day_badge = "incomplete"
        else:
            day_badge = "restricted"

        calendar_summary[date_str] = {
            "badge": day_badge,
            "total_slots": len(day_candidates),
            "best_score": max((c["score"] for c in day_candidates), default=0),
            "weekday": daily_panchang["vara"]["name_en"],
            "tithi": daily_panchang["tithi"]["name"],
            "nakshatra": daily_panchang["nakshatra"]["name"],
        }

        current_date += delta_day

    # Ranking:
    # 1. status priority: meets_configured_rules (0) > meets_rules_with_advisories (1) > incomplete (2) > fails_mandatory_rules (3)
    # 2. score descending
    # 3. start_time ascending
    status_weights = {
        "meets_configured_rules": 0,
        "meets_rules_with_advisories": 1,
        "incomplete": 2,
        "fails_mandatory_rules": 3,
    }

    candidates.sort(key=lambda c: (status_weights.get(c["status"], 4), -c["score"], c["start_time_utc"]))

    return {
        "occasion": {
            "code": occasion["code"],
            "name_en": occasion["name_en"],
            "name_ta": occasion["name_ta"],
            "category": occasion["category"],
        },
        "search_params": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
            "preferred_time_range": preferred_time_range,
            "ayanamsa_id": ayanamsa_id,
        },
        "total_candidates": len(candidates),
        "candidates": candidates[:limit],
        "calendar_summary": calendar_summary,
    }
