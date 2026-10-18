"""KP Event Prediction Engine - Analysis Orchestrator.

Orchestrates the entire end-to-end analysis:
1. Normalizes input significations, retrograde status, and CSL arbiter map.
2. Evaluates every period against configured KP event house configurations.
3. Produces Section 10 compliant JSON payloads and Section 9 human-readable reports.
4. Provides helpers to extract analysis directly from a KpResponse or saved horoscope.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple
from datetime import date, datetime

from .event_rules import (
    EventRule,
    EVENT_REGISTRY,
    RULE_SET_VERSION,
    get_event_rule,
    list_all_events,
)
from .signification_normalizer import (
    derive_planet_house_significations,
    derive_cusp_sub_lords_from_chart,
    extract_retrograde_status_from_chart,
    validate_mandatory_lords_significations,
    normalize_planet_name,
)
from .scoring_service import score_period_for_event
from .grading_service import grade_scored_event, GradeResult
from .period_service import (
    PeriodHierarchyItem,
    normalize_period_hierarchy,
    get_current_date_in_tz,
    parse_date_only,
)
from .selection_service import select_and_order_events
from .formatter import (
    format_human_readable_period,
    format_human_readable_report,
    build_api_response_payload,
)


def run_kp_event_analysis(
    lagna: Optional[str],
    periods: List[Dict[str, Any]],
    significations: Any,
    csl_significations: Optional[Dict[Any, str]] = None,
    retrograde_status: Optional[Dict[str, bool]] = None,
    current_date: Optional[str] = None,
    timezone_str: Optional[str] = "Asia/Kolkata",
    filter_category: Optional[str] = None,
    filter_grade: Optional[str] = None,
    filter_event: Optional[str] = None,
    running_only: bool = False,
    downgrade_on_antara_retrograde: bool = True,
    missing_house_l3_l4_only: bool = False,
) -> Dict[str, Any]:
    """Core analysis orchestrator conforming strictly to Section 4-10 requirements."""
    # 1. Normalize significations
    norm_sigs = derive_planet_house_significations(significations)

    # 2. Normalize CSL map (cusp 1..12 -> planet)
    norm_csl: Dict[int, str] = {}
    if csl_significations:
        for k, v in csl_significations.items():
            try:
                h = int(k)
                if 1 <= h <= 12 and v:
                    p = normalize_planet_name(str(v))
                    if p:
                        norm_csl[h] = p
            except (ValueError, TypeError):
                continue

    # 3. Normalize retrograde status
    norm_retro: Dict[str, bool] = {}
    if retrograde_status:
        for k, v in retrograde_status.items():
            p = normalize_planet_name(k)
            if p:
                norm_retro[p] = bool(v)

    # 4. Resolve current date in configured timezone
    c_dt = parse_date_only(current_date) if current_date else get_current_date_in_tz(timezone_str)
    effective_current_date_str = c_dt.isoformat() if c_dt else datetime.now().date().isoformat()

    # 5. Normalize period list and chronological running detection
    normalized_periods = normalize_period_hierarchy(
        periods,
        current_date=effective_current_date_str,
        timezone_str=timezone_str,
    )

    # Filter events to evaluate
    candidate_rules: List[EventRule] = list_all_events()
    if filter_category:
        c_low = filter_category.lower().strip()
        candidate_rules = [e for e in candidate_rules if e.category.lower() == c_low]
    if filter_event:
        e_low = filter_event.lower().strip()
        candidate_rules = [e for e in candidate_rules if e.name.lower() == e_low]

    analyzed_periods: List[Dict[str, Any]] = []
    text_blocks: List[str] = []

    total_green = 0
    total_orange = 0
    total_red = 0
    active_period_found: Optional[str] = None

    for p_item in normalized_periods:
        # Check running filter
        if running_only and not p_item.is_running:
            continue

        if p_item.is_running and not active_period_found:
            active_period_found = p_item.period_key

        # Validate mandatory Mahadasha and Bhukti data
        is_valid, missing_fields = validate_mandatory_lords_significations(
            p_item.mahadasha_lord,
            p_item.bhukti_lord,
            norm_sigs,
        )

        if not is_valid:
            p_item.status = "missing_data"
            p_item.missing_fields = missing_fields
            payload = build_api_response_payload(p_item, [])
            analyzed_periods.append(payload)
            text_blocks.append(format_human_readable_period(p_item, []))
            continue

        # Evaluate candidate events for this period
        all_graded: List[GradeResult] = []
        for ev in candidate_rules:
            scored = score_period_for_event(
                event=ev,
                md_lord=p_item.mahadasha_lord,
                bd_lord=p_item.bhukti_lord,
                antara_lord=p_item.antara_lord,
                significations=norm_sigs,
            )
            graded = grade_scored_event(
                event=ev,
                scored=scored,
                csl_map=norm_csl,
                all_significations=norm_sigs,
                retrograde_status=norm_retro,
                downgrade_on_antara_retrograde=downgrade_on_antara_retrograde,
                missing_house_l3_l4_only=missing_house_l3_l4_only,
            )

            # Apply grade filter if set
            if filter_grade:
                fg = filter_grade.lower().strip()
                if graded.final_color != fg and graded.grade.lower() != fg:
                    continue

            all_graded.append(graded)

        # Select and order events (Section 7: max 5, max 2 RED)
        displayed_events, all_sorted_events = select_and_order_events(
            all_graded,
            max_displayed=5,
            max_red=2,
        )

        # Tally summary
        for e in displayed_events:
            if e.final_color == "green":
                total_green += 1
            elif e.final_color == "orange":
                total_orange += 1
            elif e.final_color == "red":
                total_red += 1

        payload = build_api_response_payload(p_item, displayed_events, all_sorted_events)
        analyzed_periods.append(payload)
        text_blocks.append(format_human_readable_period(p_item, displayed_events))

    human_readable_report = format_human_readable_report(text_blocks)

    overall_summary = {
        "rule_set_version": RULE_SET_VERSION,
        "total_periods": len(analyzed_periods),
        "running_period": active_period_found,
        "green_count": total_green,
        "orange_count": total_orange,
        "red_count": total_red,
    }

    return {
        "rule_set_version": RULE_SET_VERSION,
        "lagna": lagna,
        "current_date": effective_current_date_str,
        "timezone": timezone_str,
        "overall_summary": overall_summary,
        "periods": analyzed_periods,
        "human_readable_report": human_readable_report,
    }


def extract_periods_from_dasa_response(
    dasa_data: Any,
    max_periods: Optional[int] = 100,
) -> List[Dict[str, Any]]:
    """Extracts Mahadasha and Bhukti periods from DasaResponse or DasaPeriodNode tree."""
    periods: List[Dict[str, Any]] = []
    if not dasa_data:
        return periods

    tree = getattr(dasa_data, "dasa_tree", None)
    if tree is None and isinstance(dasa_data, dict):
        tree = dasa_data.get("dasa_tree")

    if not isinstance(tree, list):
        return periods

    for md_node in tree:
        md_lord = getattr(md_node, "lord", None) if hasattr(md_node, "lord") else (md_node.get("lord") if isinstance(md_node, dict) else None)
        sub_periods = getattr(md_node, "sub_periods", None) if hasattr(md_node, "sub_periods") else (md_node.get("sub_periods") if isinstance(md_node, dict) else None)

        if isinstance(sub_periods, list) and len(sub_periods) > 0:
            for ad_node in sub_periods:
                bd_lord = getattr(ad_node, "lord", None) if hasattr(ad_node, "lord") else (ad_node.get("lord") if isinstance(ad_node, dict) else None)
                s_date = getattr(ad_node, "start_date_iso", None) if hasattr(ad_node, "start_date_iso") else (ad_node.get("start_date_iso") if isinstance(ad_node, dict) else None)
                if not s_date:
                    s_date = getattr(ad_node, "start_date", None) if hasattr(ad_node, "start_date") else (ad_node.get("start_date") if isinstance(ad_node, dict) else None)
                e_date = getattr(ad_node, "end_date_iso", None) if hasattr(ad_node, "end_date_iso") else (ad_node.get("end_date_iso") if isinstance(ad_node, dict) else None)
                if not e_date:
                    e_date = getattr(ad_node, "end_date", None) if hasattr(ad_node, "end_date") else (ad_node.get("end_date") if isinstance(ad_node, dict) else None)

                periods.append({
                    "mahadasha_lord": md_lord,
                    "bhukti_lord": bd_lord,
                    "start_date": s_date,
                    "end_date": e_date,
                })
                if max_periods and len(periods) >= max_periods:
                    return periods
        else:
            # If no sub_periods, include Mahadasha with self as Bhukti
            s_date = getattr(md_node, "start_date_iso", None) if hasattr(md_node, "start_date_iso") else (md_node.get("start_date_iso") if isinstance(md_node, dict) else None)
            if not s_date:
                s_date = getattr(md_node, "start_date", None) if hasattr(md_node, "start_date") else (md_node.get("start_date") if isinstance(md_node, dict) else None)
            e_date = getattr(md_node, "end_date_iso", None) if hasattr(md_node, "end_date_iso") else (md_node.get("end_date_iso") if isinstance(md_node, dict) else None)
            if not e_date:
                e_date = getattr(md_node, "end_date", None) if hasattr(md_node, "end_date") else (md_node.get("end_date") if isinstance(md_node, dict) else None)
            periods.append({
                "mahadasha_lord": md_lord,
                "bhukti_lord": md_lord,
                "start_date": s_date,
                "end_date": e_date,
            })

    return periods
