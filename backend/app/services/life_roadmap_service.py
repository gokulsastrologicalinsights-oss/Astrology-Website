"""KP Automated Multi-Year Life Timeline Predictor (Life Roadmap) Service.

Evaluates a person's birth chart across the next 1, 3, or 5 years across all
5 major life domains simultaneously:
1. Career & Status
2. Relationships & Matrimony
3. Finance & Wealth
4. Relocation & Travel
5. Health & Caution

Evaluates all Dasha-Bhukti-Antara (DBA) periods against the 32-event KP rule registry.
"""

from __future__ import annotations
import logging
import uuid
from datetime import date, datetime, time as dt_time, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set
from zoneinfo import ZoneInfo

import xalen
from app.schemas.common import BirthInput
from app.schemas.life_roadmap import (
    LifeRoadmapRequest,
    LifeRoadmapResponse,
    LifeRoadmapOverallSummary,
    DomainScorecard,
    RoadmapPeriodItem,
    ScoredMilestone,
    HouseEvidence,
    LifeDomainInfo,
)
from app.services.dasa_service import generate_vimshottari_hierarchy
from app.services.ephemeris import calculate_full_horoscope
from app.services.kp_service import calculate_kp_chart
from app.services.timezone_utils import resolve_birth_datetime
from app.services.kp_event_engine import (
    EVENT_REGISTRY,
    EventRule,
    derive_planet_house_significations,
    derive_cusp_sub_lords_from_chart,
    extract_retrograde_status_from_chart,
    score_period_for_event,
    grade_scored_event,
)

logger = logging.getLogger(__name__)

# The 5 Core Life Domains
LIFE_DOMAINS: Dict[str, Dict[str, Any]] = {
    "career": {
        "id": "career",
        "name": "Career & Status",
        "name_ta": "தொழில் & அந்தஸ்து",
        "icon": "Briefcase",
        "color": "blue",
        "description": "Job promotions, employment shifts, business expansion, recognition, and official honors.",
        "events": [
            "Promotion",
            "Job",
            "Business start",
            "Partnership",
            "Government job",
            "Transfer",
            "Higher education",
            "Competitive exam",
            "Job loss",
        ],
    },
    "relationships": {
        "id": "relationships",
        "name": "Relationships & Matrimony",
        "name_ta": "திருமணம் & குடும்பம்",
        "icon": "Heart",
        "color": "rose",
        "description": "Marriage proposal windows, wedding fructification, courtship harmony, and family bliss.",
        "events": [
            "Marriage",
            "Love affair",
            "Second marriage",
            "Children",
            "Divorce / separation",
        ],
    },
    "finance": {
        "id": "finance",
        "name": "Finance & Wealth",
        "name_ta": "தனம் & சொத்து",
        "icon": "Coins",
        "color": "amber",
        "description": "Salary hikes, unexpected gains, property/vehicle purchase, loans, and investment inflows.",
        "events": [
            "Financial gain",
            "Speculation / lottery",
            "Inheritance / insurance",
            "Property purchase",
            "Vehicle purchase",
            "Property sale",
            "Loan repayment",
            "Loan taken",
        ],
    },
    "travel": {
        "id": "travel",
        "name": "Relocation & Travel",
        "name_ta": "பயணம் & இடமாற்றம்",
        "icon": "Plane",
        "color": "indigo",
        "description": "Foreign travel, visa clearances, overseas settlement, and residential relocations.",
        "events": [
            "Foreign travel",
            "Settlement abroad",
            "Change of residence",
            "Transfer",
            "Spiritual / pilgrimage",
        ],
    },
    "health": {
        "id": "health",
        "name": "Health & Caution",
        "name_ta": "ஆரோக்கியம் & பாதுகாப்பு",
        "icon": "ShieldAlert",
        "color": "red",
        "description": "Stress periods, vitality dips, surgical/medical attention phases, and legal challenges.",
        "events": [
            "Illness",
            "Recovery",
            "Accident / Surgery",
            "Critical longevity / Maraka period",
            "Miscarriage",
            "Litigation loss",
            "Litigation win",
            "Imprisonment",
        ],
    },
}

# Events where manifestation requires caution/care rather than celebrating
CAUTION_EVENTS: Set[str] = {
    "Illness",
    "Job loss",
    "Divorce / separation",
    "Accident / Surgery",
    "Critical longevity / Maraka period",
    "Miscarriage",
    "Litigation loss",
    "Imprisonment",
}

# Primary domain mapping for every event
EVENT_TO_DOMAIN_MAP: Dict[str, str] = {
    "Marriage": "relationships",
    "Love affair": "relationships",
    "Second marriage": "relationships",
    "Divorce / separation": "relationships",
    "Children": "relationships",
    "Miscarriage": "health",
    "Job": "career",
    "Promotion": "career",
    "Transfer": "career",
    "Job loss": "career",
    "Business start": "career",
    "Partnership": "career",
    "Government job": "career",
    "Higher education": "career",
    "Competitive exam": "career",
    "Financial gain": "finance",
    "Loan taken": "finance",
    "Loan repayment": "finance",
    "Speculation / lottery": "finance",
    "Inheritance / insurance": "finance",
    "Property purchase": "finance",
    "Property sale": "finance",
    "Vehicle purchase": "finance",
    "Change of residence": "travel",
    "Foreign travel": "travel",
    "Settlement abroad": "travel",
    "Spiritual / pilgrimage": "travel",
    "Illness": "health",
    "Recovery": "health",
    "Litigation win": "health",
    "Litigation loss": "health",
    "Imprisonment": "health",
    "Critical longevity / Maraka period": "health",
    "Accident / Surgery": "health",
}


def get_all_domains_info() -> List[LifeDomainInfo]:
    """Returns domain metadata for API consumers."""
    return [
        LifeDomainInfo(
            id=d["id"],
            name=d["name"],
            name_ta=d["name_ta"],
            icon=d["icon"],
            color=d["color"],
            description=d["description"],
            events=d["events"],
        )
        for d in LIFE_DOMAINS.values()
    ]


def _format_date_pretty(date_str: str) -> str:
    """Formats 'YYYY-MM-DD' to 'DD Mon YYYY'."""
    try:
        dt = date.fromisoformat(date_str.split("T")[0])
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str


def generate_life_roadmap(
    req: LifeRoadmapRequest,
    current_user: Optional[Dict[str, Any]] = None,
) -> LifeRoadmapResponse:
    """Core engine calculating multi-year Life Roadmap across 5 domains simultaneously."""
    # 1. Resolve birth parameters
    b_date_str = req.birth_date
    b_time_str = req.birth_time
    tz_str = req.timezone or "Asia/Kolkata"
    lat = req.latitude or 13.0827
    lon = req.longitude or 80.2707
    ayan_id = req.ayanamsa_id
    customer_name = req.customer_name or "Native"
    hsys_id = 2  # Placidus for KP

    horo_row: Optional[Dict[str, Any]] = None
    if req.horoscope_id:
        from app.services.horoscope_cache import get_cached_saved_horoscope
        user_id = current_user.get("id") if current_user else "guest"
        is_admin = current_user.get("role") == "admin" if current_user else False
        clean_id = req.horoscope_id.strip()
        horo_row = get_cached_saved_horoscope(
            clean_id=clean_id,
            user_id=str(user_id),
            is_admin=is_admin,
            include_calculation_result=True,
        )
        if horo_row:
            b_date_str = str(horo_row["birth_date"])
            b_time_str = str(horo_row["birth_time"])
            tz_str = horo_row.get("timezone") or tz_str
            lat = float(horo_row.get("latitude", lat))
            lon = float(horo_row.get("longitude", lon))
            customer_name = horo_row.get("name") or customer_name

    if not b_date_str or not b_time_str:
        raise ValueError("Birth date and birth time are required to calculate the Life Roadmap.")

    # 2. Compute full chart & KP chart
    birth_input = BirthInput(
        birth_date=b_date_str,
        birth_time=b_time_str,
        timezone=tz_str,
        latitude=lat,
        longitude=lon,
    )

    kp_chart = calculate_kp_chart(birth_input, ayanamsa_id=ayan_id, house_system_id=hsys_id)
    kp_dict = kp_chart.model_dump()

    full_horo = calculate_full_horoscope(
        birth_date=b_date_str,
        birth_time=b_time_str,
        timezone_str=tz_str,
        latitude=lat,
        longitude=lon,
        ayanamsa_id=ayan_id,
        house_system_id=hsys_id,
    )
    horo_dict = full_horo.model_dump()

    norm_sigs = derive_planet_house_significations(kp_dict.get("house_significators", {}))
    csl_map = derive_cusp_sub_lords_from_chart(kp_dict)
    retro_map = extract_retrograde_status_from_chart(horo_dict, kp_dict)

    # 3. Resolve timeline start and end dates
    try:
        tz_obj = ZoneInfo(tz_str)
    except Exception:
        tz_obj = ZoneInfo("Asia/Kolkata")

    today_date = datetime.now(tz_obj).date()
    start_eval_date = (
        date.fromisoformat(req.start_date.strip())
        if req.start_date
        else today_date
    )
    horizon_days = int(365.25 * req.horizon_years)
    end_eval_date = start_eval_date + timedelta(days=horizon_days)

    # 4. Generate 3-level Vimshottari hierarchy (Mahadasha -> Bhukti -> Antara)
    b_date_obj = date.fromisoformat(str(b_date_str).strip())
    # Handle time with or without seconds
    t_parts = str(b_time_str).strip().split(":")
    b_time_obj = dt_time(int(t_parts[0]), int(t_parts[1]), int(t_parts[2]) if len(t_parts) > 2 else 0)

    local_dt, utc_dt, birth_jd, _, offset_hours = resolve_birth_datetime(b_date_obj, b_time_obj, tz_str)
    moon_pos = xalen.planet_position(birth_jd, 1, True, ayan_id)

    dasa_tree, _ = generate_vimshottari_hierarchy(
        moon_lon=moon_pos["longitude"],
        birth_jd=birth_jd,
        birth_date=local_dt.date(),
        utc_offset_hours=offset_hours,
        depth=3,  # Level 1 (MD), Level 2 (BD), Level 3 (AD)
    )

    # 5. Extract matching Antara (DBA) periods intersecting [start_eval_date, end_eval_date]
    matched_ad_periods: List[Dict[str, Any]] = []
    for md_node in dasa_tree:
        for bd_node in getattr(md_node, "sub_periods", []):
            for ad_node in getattr(bd_node, "sub_periods", []):
                ad_start_str = ad_node.start_date_iso or ad_node.start_date
                ad_end_str = ad_node.end_date_iso or ad_node.end_date
                if not ad_start_str or not ad_end_str:
                    continue
                ad_start = date.fromisoformat(ad_start_str.split("T")[0])
                ad_end = date.fromisoformat(ad_end_str.split("T")[0])

                if ad_end >= start_eval_date and ad_start <= end_eval_date:
                    matched_ad_periods.append({
                        "mahadasha_lord": md_node.lord,
                        "bhukti_lord": bd_node.lord,
                        "antara_lord": ad_node.lord,
                        "start_date": ad_start_str.split("T")[0],
                        "end_date": ad_end_str.split("T")[0],
                        "start_date_obj": ad_start,
                        "end_date_obj": ad_end,
                    })

    # Sort chronologically
    matched_ad_periods.sort(key=lambda p: p["start_date_obj"])

    # 6. Evaluate all DBA periods against the 32-Event KP Registry
    domain_filter = req.filter_domain.lower().strip() if req.filter_domain else None
    if domain_filter == "all":
        domain_filter = None

    min_prob = req.min_probability.lower().strip() if req.min_probability else None

    roadmap_periods: List[RoadmapPeriodItem] = []
    running_period_key: Optional[str] = None
    all_scored_milestones_flat: List[ScoredMilestone] = []

    domain_green_tallies: Dict[str, int] = {k: 0 for k in LIFE_DOMAINS}
    domain_orange_tallies: Dict[str, int] = {k: 0 for k in LIFE_DOMAINS}
    domain_red_tallies: Dict[str, int] = {k: 0 for k in LIFE_DOMAINS}
    domain_caution_alerts: Dict[str, int] = {k: 0 for k in LIFE_DOMAINS}
    domain_peak_windows: Dict[str, Dict[str, Any]] = {}

    total_high_prob = 0
    total_moderate = 0
    total_caution_alerts = 0

    for period in matched_ad_periods:
        md_lord = period["mahadasha_lord"]
        bd_lord = period["bhukti_lord"]
        ad_lord = period["antara_lord"]
        s_date_str = period["start_date"]
        e_date_str = period["end_date"]
        s_date = period["start_date_obj"]
        e_date = period["end_date_obj"]

        is_running = (s_date <= today_date <= e_date)
        period_key = f"{md_lord} - {bd_lord} - {ad_lord}"
        if is_running and not running_period_key:
            running_period_key = period_key

        period_milestones: List[ScoredMilestone] = []
        period_domain_colors: Dict[str, str] = {}

        for ev_name, ev_rule in EVENT_REGISTRY.items():
            ev_domain_id = EVENT_TO_DOMAIN_MAP.get(ev_name, "career")
            if domain_filter and ev_domain_id != domain_filter:
                continue

            scored = score_period_for_event(
                event=ev_rule,
                md_lord=md_lord,
                bd_lord=bd_lord,
                antara_lord=ad_lord,
                significations=norm_sigs,
            )
            graded = grade_scored_event(
                event=ev_rule,
                scored=scored,
                csl_map=csl_map,
                all_significations=norm_sigs,
                retrograde_status=retro_map,
            )

            is_caution = ev_name in CAUTION_EVENTS

            # Interpret probability and UI status
            if is_caution:
                if graded.final_color == "green":
                    prob_level = "CAUTION"
                    status_lbl = "🔴 High Alert / Caution Window"
                    ui_color = "red"
                    domain_caution_alerts[ev_domain_id] += 1
                    total_caution_alerts += 1
                elif graded.final_color == "orange":
                    prob_level = "MODERATE"
                    status_lbl = "🟡 Precautionary / Stress Window"
                    ui_color = "orange"
                    domain_orange_tallies[ev_domain_id] += 1
                    total_moderate += 1
                else:
                    prob_level = "LOW"
                    status_lbl = "🟢 Protected / Low Risk"
                    ui_color = "green"
                    domain_green_tallies[ev_domain_id] += 1
            else:
                if graded.final_color == "green":
                    prob_level = "HIGH"
                    status_lbl = "🟢 High Probability / Favorable"
                    ui_color = "green"
                    domain_green_tallies[ev_domain_id] += 1
                    total_high_prob += 1
                elif graded.final_color == "orange":
                    prob_level = "MODERATE"
                    status_lbl = "🟡 Moderate / Delays"
                    ui_color = "orange"
                    domain_orange_tallies[ev_domain_id] += 1
                    total_moderate += 1
                else:
                    prob_level = "LOW"
                    status_lbl = "🔴 Restrained / Low Probability"
                    ui_color = "red"
                    domain_red_tallies[ev_domain_id] += 1

            # Check min_probability filter if requested
            if min_prob == "high_only" and prob_level not in ("HIGH", "CAUTION"):
                continue
            if min_prob == "high_and_moderate" and prob_level == "LOW":
                continue

            supp_evidence = [
                HouseEvidence(
                    house=hc.house,
                    level=hc.level,
                    weight=hc.weight,
                    contributing_lord=hc.contributing_lord,
                )
                for hc in scored.supporting_houses
            ]
            den_evidence = [
                HouseEvidence(
                    house=hc.house,
                    level=hc.level,
                    weight=hc.weight,
                    contributing_lord=hc.contributing_lord,
                )
                for hc in scored.denying_houses
            ]

            dom_meta = LIFE_DOMAINS.get(ev_domain_id, LIFE_DOMAINS["career"])

            milestone = ScoredMilestone(
                event_name=ev_name,
                domain_id=ev_domain_id,
                domain_name=dom_meta["name"],
                domain_name_ta=dom_meta["name_ta"],
                is_caution_type=is_caution,
                probability_level=prob_level,
                status_label=status_lbl,
                color=ui_color,
                grade=graded.grade,
                support_score=graded.support_score,
                denial_score=graded.denial_score,
                coverage=round(graded.coverage, 3),
                supporting_houses=supp_evidence,
                denying_houses=den_evidence,
                denied=graded.denied,
                hint=graded.hint,
                retrograde_note=graded.retrograde_note,
                csl_adjustment=graded.csl_adjustment,
            )

            period_milestones.append(milestone)

            # Track peak favorable window per domain
            if not is_caution and graded.final_color == "green":
                prev_best = domain_peak_windows.get(ev_domain_id)
                current_score = graded.support_score * 10 + int(graded.coverage * 100)
                if not prev_best or current_score > prev_best.get("score", 0):
                    domain_peak_windows[ev_domain_id] = {
                        "score": current_score,
                        "period": period_key,
                        "event": ev_name,
                        "dates": f"{_format_date_pretty(s_date_str)} – {_format_date_pretty(e_date_str)}",
                        "hint": graded.hint,
                    }

            # Register domain presence in this period
            if ev_domain_id not in period_domain_colors or ui_color == "green":
                period_domain_colors[ev_domain_id] = ui_color

        # Sort milestones in this period: HIGH/CAUTION first, then highest support score
        def _milestone_sort_key(m: ScoredMilestone):
            p_order = {"HIGH": 0, "CAUTION": 1, "MODERATE": 2, "LOW": 3}
            return (p_order.get(m.probability_level, 4), -m.support_score, -m.coverage)

        period_milestones.sort(key=_milestone_sort_key)

        # Select top milestones for period card
        top_m = period_milestones[:4]
        duration_days = (e_date - s_date).days

        # Primary period status:
        has_high_fav = any(m.probability_level == "HIGH" for m in period_milestones)
        has_caution = any(m.probability_level == "CAUTION" for m in period_milestones)

        if has_high_fav and not has_caution:
            primary_status = "green"
        elif has_caution:
            primary_status = "red"
        elif any(m.probability_level == "MODERATE" for m in period_milestones):
            primary_status = "orange"
        else:
            primary_status = "neutral"

        roadmap_period_item = RoadmapPeriodItem(
            period_key=period_key,
            mahadasha_lord=md_lord,
            bhukti_lord=bd_lord,
            antara_lord=ad_lord,
            start_date=s_date_str,
            end_date=e_date_str,
            start_display=_format_date_pretty(s_date_str),
            end_display=_format_date_pretty(e_date_str),
            duration_days=duration_days,
            is_running=is_running,
            primary_status=primary_status,
            domain_highlights=period_domain_colors,
            top_milestones=top_m,
            all_milestones=period_milestones,
        )
        roadmap_periods.append(roadmap_period_item)

        # Flatten important milestones for the upcoming highlights list
        for m in period_milestones:
            if m.probability_level in ("HIGH", "CAUTION"):
                all_scored_milestones_flat.append(m)

    # 7. Build Domain Scorecards
    domain_scorecards: List[DomainScorecard] = []
    for d_id, d_meta in LIFE_DOMAINS.items():
        g_c = domain_green_tallies[d_id]
        o_c = domain_orange_tallies[d_id]
        r_c = domain_red_tallies[d_id]
        c_c = domain_caution_alerts[d_id]

        peak = domain_peak_windows.get(d_id)
        peak_period = peak["period"] if peak else None
        peak_dates = peak["dates"] if peak else None
        peak_event = peak["event"] if peak else None

        if g_c >= 3:
            s_label = "Outstanding Growth / High Promise"
            s_color = "green"
            s_text = f"Multiple favorable windows ({g_c} strong triggers) support active initiatives in {d_meta['name']}."
        elif g_c >= 1:
            s_label = "Favorable Opportunity Windows"
            s_color = "green"
            s_text = f"Key breakthrough window indicated around {peak_dates or 'the horizon'} under {peak_event or 'supportive Dashas'}."
        elif c_c >= 2:
            s_label = "Precautionary / Heightened Caution"
            s_color = "red"
            s_text = f"Demands careful mitigation and proactive planning. {c_c} high-alert periods detected."
        elif o_c >= 3:
            s_label = "Gradual Progress / Delays"
            s_color = "orange"
            s_text = f"Moderate indicators; consistent follow-through will yield results despite intermediate delays."
        else:
            s_label = "Stable / Steady Phase"
            s_color = "orange"
            s_text = f"Standard planetary influences; focus on steady routine and consolidation in {d_meta['name']}."

        domain_scorecards.append(
            DomainScorecard(
                domain_id=d_id,
                domain_name=d_meta["name"],
                domain_name_ta=d_meta["name_ta"],
                icon=d_meta["icon"],
                color=d_meta["color"],
                summary_label=s_label,
                status_color=s_color,
                green_count=g_c,
                orange_count=o_c,
                red_count=r_c,
                caution_alert_count=c_c,
                peak_window_period=peak_period,
                peak_window_dates=peak_dates,
                peak_window_event=peak_event,
                summary_text=s_text,
            )
        )

    # 8. Identify Most Favorable Domain and Overall Verdict
    best_dom = max(
        LIFE_DOMAINS.keys(),
        key=lambda k: domain_green_tallies[k] - (domain_caution_alerts[k] * 2),
    )
    best_dom_name = LIFE_DOMAINS[best_dom]["name"]

    if total_high_prob >= 5:
        verdict = f"Dynamic multi-year cycle marked by strong expansion, particularly in {best_dom_name}."
    elif total_caution_alerts >= 4:
        verdict = "Transformational cycle requiring strategic patience, preventive wellness care, and risk avoidance."
    else:
        verdict = f"Balanced life progression with noteworthy high-probability windows primarily in {best_dom_name}."

    overall_summary = LifeRoadmapOverallSummary(
        total_dba_periods=len(roadmap_periods),
        total_evaluated_events=len(roadmap_periods) * len(EVENT_REGISTRY),
        high_probability_count=total_high_prob,
        moderate_count=total_moderate,
        caution_alerts_count=total_caution_alerts,
        running_period_key=running_period_key,
        most_favorable_domain=best_dom_name,
        executive_verdict=verdict,
    )

    # 9. Format Markdown Report
    lagna_name = horo_dict.get("ascendant", {}).get("sign_name", "Unknown")
    moon_sign_name = "Unknown"
    nakshatra_name = "Unknown"
    planets_raw = horo_dict.get("planets")
    if isinstance(planets_raw, list):
        for p in planets_raw:
            if p.get("name") == "Moon":
                moon_sign_name = p.get("sign_name", "Unknown")
                n_info = p.get("nakshatra") or {}
                if isinstance(n_info, dict) and n_info.get("name"):
                    nakshatra_name = f"{n_info.get('name')} (Pada {n_info.get('pada', 1)})"
                elif isinstance(n_info, str):
                    nakshatra_name = n_info
                break
    elif isinstance(planets_raw, dict):
        m_info = planets_raw.get("Moon", {})
        moon_sign_name = m_info.get("sign_name", "Unknown")
        n_info = m_info.get("nakshatra") or {}
        if isinstance(n_info, dict) and n_info.get("name"):
            nakshatra_name = f"{n_info.get('name')} (Pada {n_info.get('pada', 1)})"
        elif isinstance(n_info, str):
            nakshatra_name = n_info

    md_lines: List[str] = [
        f"# Multi-Year Life Roadmap ({req.horizon_years}-Year Strategic Horizon)",
        f"**Client**: {customer_name} | **Ascendant**: {lagna_name} | **Moon**: {moon_sign_name} ({nakshatra_name})",
        f"**Evaluation Horizon**: {_format_date_pretty(start_eval_date.isoformat())} to {_format_date_pretty(end_eval_date.isoformat())}",
        f"**Active Running Dasha**: {running_period_key or 'N/A'}",
        "",
        "## Executive Summary",
        verdict,
        "",
        f"- **Total Evaluated DBA Periods**: {len(roadmap_periods)}",
        f"- **High Probability Breakthrough Windows (🟢)**: {total_high_prob}",
        f"- **Moderate / Delayed Windows (🟡)**: {total_moderate}",
        f"- **High Alert Caution Windows (🔴)**: {total_caution_alerts}",
        "",
        "## Domain Performance Scorecards",
        "| Domain | Status | Strong Favorable | Caution Alerts | Best Upcoming Window |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for sc in domain_scorecards:
        best_win_str = f"{sc.peak_window_event} ({sc.peak_window_dates})" if sc.peak_window_dates else "Gradual progression"
        md_lines.append(
            f"| {sc.domain_name} | {sc.summary_label} | {sc.green_count} | {sc.caution_alert_count} | {best_win_str} |"
        )

    md_lines.append("")
    md_lines.append("## Chronological DBA Timeline & Milestones")
    for p in roadmap_periods:
        badge = " [RUNNING NOW]" if p.is_running else ""
        md_lines.append(f"### {p.period_key} ({p.start_display} – {p.end_display}){badge}")
        if not p.top_milestones:
            md_lines.append("_Steady routine period without extreme planetary peaks._")
        else:
            for m in p.top_milestones:
                md_lines.append(f"- **{m.status_label.split(' ')[0]} {m.event_name}** ({m.domain_name}): {m.hint}")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("*Indicative KP Astrology Life Roadmap. Confirm with Cuspal Sub-Lord arbiter and planetary transits before major life commitments.*")

    executive_md = "\n".join(md_lines)

    return LifeRoadmapResponse(
        customer_name=customer_name,
        lagna=lagna_name,
        moon_sign=moon_sign_name,
        nakshatra=nakshatra_name,
        current_date=today_date.isoformat(),
        start_date=start_eval_date.isoformat(),
        end_date=end_eval_date.isoformat(),
        horizon_years=req.horizon_years,
        running_period_key=running_period_key,
        overall_summary=overall_summary,
        domain_scorecards=domain_scorecards,
        chronological_periods=roadmap_periods,
        upcoming_key_milestones=all_scored_milestones_flat[:15],
        executive_roadmap_markdown=executive_md,
    )
