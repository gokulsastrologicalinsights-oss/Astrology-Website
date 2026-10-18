"""KP Event Prediction Engine - Output Formatter.

Generates human-readable text output matching the exact Section 9 specification,
and strict JSON API response payloads matching the Section 10 schema.
"""

from __future__ import annotations
from datetime import date
from typing import Dict, List, Optional, Any
from .grading_service import GradeResult
from .period_service import PeriodHierarchyItem, parse_date_only

DISCLAIMER_LINE = "Indicative KP hint, confirm with CSL and transit before decisions."

COLOR_EMOJIS = {
    "green": "🟢",
    "STRONG": "🟢",
    "orange": "🟠",
    "MODERATE": "🟠",
    "red": "🔴",
    "WEAK": "🔴",
}


def format_display_date(date_str: Optional[str]) -> str:
    """Formats date to '12 Mar 2026' style if parseable, otherwise returns string."""
    if not date_str:
        return ""
    dt = parse_date_only(date_str)
    if dt:
        # e.g. 12 Mar 2026
        return dt.strftime("%d %b %Y")
    return str(date_str).strip()


def format_human_readable_period(
    period_item: PeriodHierarchyItem,
    displayed_events: List[GradeResult],
) -> str:
    """Formats a single period entry into the exact Section 9 human-readable text block."""
    lines: List[str] = []

    # 1. Period header
    # e.g., PERIOD: Venus - Sun (12 Mar 2026 to 12 Mar 2027) — RUNNING NOW
    lords_str = f"{period_item.mahadasha_lord} - {period_item.bhukti_lord}"
    if period_item.antara_lord:
        lords_str += f" - {period_item.antara_lord}"

    s_fmt = format_display_date(period_item.start_date)
    e_fmt = format_display_date(period_item.end_date)
    date_range_str = f"({s_fmt} to {e_fmt})" if s_fmt and e_fmt else ""

    running_badge = " — RUNNING NOW" if period_item.is_running else ""
    lines.append(f"PERIOD: {lords_str} {date_range_str}{running_badge}".strip())
    lines.append("")

    # If missing mandatory data
    if period_item.status == "missing_data" or not displayed_events:
        missing_desc = ", ".join(period_item.missing_fields) if period_item.missing_fields else "required significator data"
        lines.append(f"Data missing: {missing_desc}")
        lines.append("")
        return "\n".join(lines)

    # 2. Events in period
    for ev in displayed_events:
        emoji = COLOR_EMOJIS.get(ev.final_color, "⚪")
        lines.append(f"{emoji} {ev.event_name} — {ev.grade}")

        # Supporting houses
        if ev.supporting_houses:
            supp_parts = [f"{h['house']}({h['level']})" for h in ev.supporting_houses]
            lines.append(f"Supporting houses from Lagna: {', '.join(supp_parts)}")
        else:
            lines.append("Supporting houses from Lagna: none")

        # Denying houses
        if ev.denying_houses:
            den_parts = [f"{h['house']}({h['level']})" for h in ev.denying_houses]
            lines.append(f"Denying houses present: {', '.join(den_parts)}")
        else:
            lines.append("Denying houses present: none")

        # Hint (<= 20 words)
        lines.append(f"Hint: {ev.hint}")
        lines.append("")

    return "\n".join(lines)


def format_human_readable_report(
    period_blocks: List[str],
) -> str:
    """Combines all period text blocks and appends the mandatory final disclaimer line."""
    report = "\n\n".join([b.strip() for b in period_blocks if b.strip()])
    report += f"\n\n{DISCLAIMER_LINE}\n"
    return report


def build_api_response_payload(
    period_item: PeriodHierarchyItem,
    displayed_events: List[GradeResult],
    all_events: Optional[List[GradeResult]] = None,
) -> Dict[str, Any]:
    """Generates a JSON API object conforming to the Section 10 schema."""
    period_key = f"{period_item.mahadasha_lord}-{period_item.bhukti_lord}"
    if period_item.antara_lord:
        period_key += f"-{period_item.antara_lord}"

    if period_item.status == "missing_data":
        return {
            "period": period_key,
            "mahadasha_lord": period_item.mahadasha_lord,
            "bhukti_lord": period_item.bhukti_lord,
            "antara_lord": period_item.antara_lord,
            "start": period_item.start_date,
            "end": period_item.end_date,
            "start_date": period_item.start_date,
            "end_date": period_item.end_date,
            "running": bool(period_item.is_running),
            "is_running": bool(period_item.is_running),
            "status": "missing_data",
            "missing_fields": period_item.missing_fields,
            "events": [],
            "summary": {
                "green_count": 0,
                "orange_count": 0,
                "red_count": 0,
            },
        }

    green_count = sum(1 for e in displayed_events if e.final_color == "green")
    orange_count = sum(1 for e in displayed_events if e.final_color == "orange")
    red_count = sum(1 for e in displayed_events if e.final_color == "red")

    events_payload: List[Dict[str, Any]] = []
    for e in displayed_events:
        events_payload.append({
            "event": e.event_name,
            "color": e.final_color,
            "grade": e.grade,
            "support_score": e.support_score,
            "denial_score": e.denial_score,
            "coverage": round(e.coverage, 4),
            "supporting": e.supporting_houses,
            "denying": e.denying_houses,
            "denied": e.denied,
            "retrograde_note": e.retrograde_note,
            "csl_adjustment": e.csl_adjustment,
            "hint": e.hint,
            "scoring_metadata": e.scoring_metadata,
        })

    all_events_payload: List[Dict[str, Any]] = []
    if all_events:
        for e in all_events:
            all_events_payload.append({
                "event": e.event_name,
                "color": e.final_color,
                "grade": e.grade,
                "support_score": e.support_score,
                "denial_score": e.denial_score,
                "coverage": round(e.coverage, 4),
                "supporting": e.supporting_houses,
                "denying": e.denying_houses,
                "denied": e.denied,
                "retrograde_note": e.retrograde_note,
                "csl_adjustment": e.csl_adjustment,
                "hint": e.hint,
            })

    return {
        "period": period_key,
        "mahadasha_lord": period_item.mahadasha_lord,
        "bhukti_lord": period_item.bhukti_lord,
        "antara_lord": period_item.antara_lord,
        "start": period_item.start_date,
        "end": period_item.end_date,
        "start_date": period_item.start_date,
        "end_date": period_item.end_date,
        "running": bool(period_item.is_running),
        "is_running": bool(period_item.is_running),
        "status": "ok",
        "events": events_payload,
        "all_events": all_events_payload,
        "summary": {
            "green_count": green_count,
            "orange_count": orange_count,
            "red_count": red_count,
        },
    }
