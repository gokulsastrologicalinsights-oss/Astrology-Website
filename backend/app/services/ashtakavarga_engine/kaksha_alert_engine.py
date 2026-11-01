"""Ashtakavarga Kaksha Transit Trigger Alert Engine.

Classical Reference:
- Brihat Parashara Hora Shastra (BPHS), Chapter 67 (Kaksha Vibhaga).
- Dr. B.V. Raman, 'Ashtakavarga System of Direction', Chapter 6 (Transits).

Each sign (30°) is divided into 8 Kakshas (3°45' each) ruled in speed order:
Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.

In classical practice, major events trigger when a transiting planet crosses a
Kaksha where the donor contributed a Bindu (1 = Auspicious / Favorable)
or Rekha (0 = Inauspicious / Obstacle).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.ashtakavarga import PrastaraDetail
from app.schemas.kaksha_alerts import (
    ActiveKakshaStatus,
    DomainAlertSummary,
    KakshaAlertItem,
    KakshaAlertRequest,
    KakshaAlertsResponse,
)
from app.services.ashtakavarga_engine.calculator import calculate_ashtakavarga
from app.services.ashtakavarga_engine.kaksha import (
    KAKSHA_RANGES,
    KAKSHA_WIDTH_DEG,
    SIGN_NAMES_EN,
    get_kaksha_division_for_degree,
)
from app.services.ashtakavarga_engine.prastara import (
    KAKSHA_CONTRIBUTOR_ORDER,
    compute_all_prastara_matrices,
)
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.timezone_utils import resolve_birth_datetime


# Canonical speeds in deg/day for remaining days estimation
MEAN_SPEEDS: Dict[str, float] = {
    "Saturn": 0.033,
    "Jupiter": 0.083,
    "Mars": 0.524,
    "Sun": 0.985,
    "Venus": 1.15,
    "Mercury": 1.20,
}


def _evaluate_life_domains_and_guidance(
    planet: str,
    house_from_lagna: int,
    has_bindu: bool,
    kaksha_lord: str,
    sign_name: str,
) -> Tuple[List[str], str, str, str]:
    """Generates life domain tags, severity level, and classical actionable guidance."""
    domains: List[str] = []

    # Map house domains
    if house_from_lagna in (1, 6, 8, 12):
        domains.append("health")
    if house_from_lagna in (2, 5, 9, 11, 12):
        domains.append("finances")
    if house_from_lagna in (1, 6, 10, 11):
        domains.append("career")
    if house_from_lagna in (6, 8, 7):
        domains.append("lawsuits")

    if not domains:
        domains = ["career", "finances"]

    # Guidance based on planet & bindu
    if has_bindu:
        severity = "High Opportunity" if planet in ("Jupiter", "Saturn") else "Favorable"
        if "health" in domains and planet == "Jupiter":
            en = f"Transiting {planet} in Kaksha #{kaksha_lord} ({sign_name}) holds 1 Bindu: Exceptional window for healing, recovery from fatigue, and successful medical treatments."
            ta = f"{sign_name} ராசியில் {kaksha_lord} கக்ஷாவில் குரு 1 பிந்துவுடன் சஞ்சரிப்பதால்: பூரண உடல் நலம், ஆரோக்கிய மீட்சி மற்றும் மருத்துவ சிகிச்சைகளுக்கு மிகச் சிறந்த காலம்."
        elif "finances" in domains and planet in ("Jupiter", "Venus"):
            en = f"{planet} transit with 1 Bindu in House {house_from_lagna}: Auspicious period for investments, business settlements, capital expansion, and unexpected profits."
            ta = f"{house_from_lagna}-ம் வீட்டில் {planet} 1 பிந்துவுடன் சஞ்சரிப்பதால்: முதலீடுகள், புதிய வர்த்தக ஒப்பந்தங்கள் மற்றும் பணவரவிற்கு மிகுந்த சுப பலன் கிட்டும்."
        elif "career" in domains and planet in ("Saturn", "Sun"):
            en = f"Transiting {planet} with 1 Bindu in House {house_from_lagna}: Solid breakthrough in career, promotion opportunities, executive approval, and leadership recognition."
            ta = f"{house_from_lagna}-ம் வீட்டில் {planet} 1 பிந்துவுடன் இருப்பதால்: தொழில் மேன்மை, புதிய பொறுப்புகள், பதவி உயர்வு மற்றும் மேலதிகாரிகளின் ஆதரவு உண்டாகும்."
        elif "lawsuits" in domains and planet in ("Mars", "Saturn"):
            en = f"Mars/Saturn in 1-Bindu Kaksha in House {house_from_lagna}: Clear advantage in legal disputes, negotiations, overcoming competitors, and achieving amicable settlements."
            ta = f"வழக்குகள் மற்றும் போட்டிகளில் வெற்றி பெற சாதகமான காலம். சமரசப் பேச்சுவார்த்தைகள் நன்மையில் முடியும்."
        else:
            en = f"Favorable Kaksha transit for {planet}: Harmonious conditions to initiate projects and finalize key commitments."
            ta = f"{planet} கிரகம் சுப கக்ஷாவில் சஞ்சரிப்பதால்: புதிய முயற்சிகளைத் தொடங்கவும் நல்ல முடிவுகளை எடுக்கவும் உகந்த நேரம்."
    else:
        severity = "Caution Required"
        if "health" in domains and planet in ("Mars", "Saturn"):
            en = f"Transiting {planet} in 0-Bindu Kaksha (House {house_from_lagna}): Heightened vulnerability to inflammation, fatigue, or accidental sprains. Guard diet and avoid reckless driving."
            ta = f"{house_from_lagna}-ம் வீட்டில் {planet} பிந்து இன்றி (0) சஞ்சரிப்பதால்: உடல் சோர்வு, உஷ்ண உபாதைகள் மற்றும் கவனக்குறைவால் ஏற்படும் காயங்கள் குறித்து எச்சரிக்கை தேவை."
        elif "finances" in domains:
            en = f"Transiting {planet} has 0 Bindu in House {house_from_lagna}: Delay major speculative investments, beware fraudulent promises, and strictly curb impulse expenses."
            ta = f"பணவிஷயங்களில் கூடுதல் விழிப்புணர்வு தேவை. புதிய ஊக வணிகம், கடன் கொடுத்தல் மற்றும் அவசர செலவுகளைத் தவிர்க்கவும்."
        elif "career" in domains:
            en = f"0-Bindu Kaksha alert for {planet}: Postpone confrontations with superiors, double-check compliance documents, and avoid impulsive job resignations."
            ta = f"பணியிடத்தில் மேலதிகாரிகளுடன் வாக்குவாதங்களைத் தவிர்க்கவும். புதிய மாற்றங்களை தற்காலிகமாக தள்ளிப்போடுவது நல்லது."
        elif "lawsuits" in domains:
            en = f"Zero Bindu in House {house_from_lagna}: Unfavorable window for initiating fresh lawsuits or signing contentious contracts. Maintain a low profile in disputes."
            ta = f"வழக்கு விவகாரங்களில் விவேகம் தேவை. புதிய சட்ட நடவடிக்கைகளை தொடங்குவதை தவிர்க்கவும்."
        else:
            en = f"0-Bindu Kaksha for {planet}: Temporary obstacles and sluggish progress. Practice patience and avoid haste."
            ta = f"தற்காலிக தாமதங்கள் மற்றும் தடைகள் ஏற்படலாம். நிதானத்துடன் செயல்படுவது வெற்றி தரும்."

    return domains, severity, en, ta


def generate_kaksha_transit_alerts(request: KakshaAlertRequest) -> KakshaAlertsResponse:
    """Computes real-time Ashtakavarga Kaksha Transit triggers & chronological timeline alerts."""
    ayanamsa_str = "lahiri" if request.ayanamsa == 0 else "kp"
    eph = SwissEphemeris(ayanamsa=ayanamsa_str, node="true")

    # 1. Calculate natal chart & Prastara matrices
    local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
        request.birth_date, request.birth_time, request.timezone
    )

    natal_positions = eph.sidereal_positions(birth_jd)
    _cusps, natal_asc, _mc, _armc = eph.houses(birth_jd, request.latitude, request.longitude)
    natal_lagna_idx = int((natal_asc % 360.0) // 30.0) + 1
    natal_lagna_name = SIGN_NAMES_EN[natal_lagna_idx]

    # Convert natal positions for Ashtakavarga engine: list of dicts with name & sign_index
    av_planet_list = [
        {"name": p, "sign_index": int((pos[0] % 360.0) // 30.0) + 1}
        for p, pos in natal_positions.items()
    ]
    av_resp = calculate_ashtakavarga(av_planet_list, natal_lagna_idx, include_prastara=True)
    prastara_dict = av_resp.prastara or {}

    # 2. Today's Active Kaksha Status
    today = date.today()
    today_dt = datetime.combine(today, datetime.min.time())
    today_jd = eph.jd_ut(today_dt)
    today_pos = eph.sidereal_positions(today_jd)

    tracked_planets = [p for p in request.planets if p in prastara_dict]
    if not tracked_planets:
        tracked_planets = ["Saturn", "Jupiter", "Mars"]

    active_status_list: List[ActiveKakshaStatus] = []
    for p in tracked_planets:
        p_lon = today_pos[p][0] % 360.0
        p_sign_idx = int(p_lon // 30.0) + 1
        p_deg_in_sign = p_lon % 30.0
        k_num, k_lord, k_start, k_end, k_range = get_kaksha_division_for_degree(p_deg_in_sign)

        # Check bindu
        prastara = prastara_dict[p]
        donor_map = {row.contributor: row.sign_bindus for row in prastara.rows}
        has_bindu = donor_map.get(k_lord, {}).get(p_sign_idx, 0) == 1

        house_from_lagna = ((p_sign_idx - natal_lagna_idx) % 12) + 1
        speed = max(0.01, MEAN_SPEEDS.get(p, 0.1))
        deg_left_in_kaksha = k_end - p_deg_in_sign
        days_left = round(deg_left_in_kaksha / speed, 1)

        active_status_list.append(
            ActiveKakshaStatus(
                planet=p,
                current_sign=SIGN_NAMES_EN[p_sign_idx],
                current_sign_index=p_sign_idx,
                current_degree=round(p_deg_in_sign, 2),
                kaksha_number=k_num,
                kaksha_lord=k_lord,
                kaksha_range=k_range,
                has_bindu=has_bindu,
                status="Auspicious (Bindu = 1) 🟢" if has_bindu else "Inauspicious (Bindu = 0) 🔴",
                house_from_lagna=house_from_lagna,
                days_remaining_in_kaksha=max(0.5, days_left),
            )
        )

    # 3. Step forward through the horizon to build chronological Kaksha Timeline
    horizon_days = max(7, min(365, request.horizon_days))
    end_date = today + timedelta(days=horizon_days)

    # We sample daily or every 2 days to record exact Kaksha entries
    step_days = 2
    n_steps = horizon_days // step_days

    # Track Kaksha history for each planet
    planet_intervals: Dict[str, List[dict]] = {p: [] for p in tracked_planets}

    for step in range(n_steps + 1):
        cur_dt = today_dt + timedelta(days=step * step_days)
        cur_jd = eph.jd_ut(cur_dt)
        pos = eph.sidereal_positions(cur_jd)

        for p in tracked_planets:
            p_lon = pos[p][0] % 360.0
            p_sign_idx = int(p_lon // 30.0) + 1
            p_deg_in_sign = p_lon % 30.0
            k_num, k_lord, k_start, k_end, k_range = get_kaksha_division_for_degree(p_deg_in_sign)

            prastara = prastara_dict[p]
            donor_map = {row.contributor: row.sign_bindus for row in prastara.rows}
            has_bindu = donor_map.get(k_lord, {}).get(p_sign_idx, 0) == 1
            house_from_lagna = ((p_sign_idx - natal_lagna_idx) % 12) + 1

            planet_intervals[p].append({
                "date": cur_dt.date(),
                "sign_idx": p_sign_idx,
                "kaksha_num": k_num,
                "kaksha_lord": k_lord,
                "kaksha_range": k_range,
                "has_bindu": has_bindu,
                "house_from_lagna": house_from_lagna,
            })

    # Group continuous Kaksha intervals for each planet
    raw_alerts: List[KakshaAlertItem] = []
    for p in tracked_planets:
        intervals = planet_intervals[p]
        if not intervals:
            continue

        cur_start = intervals[0]["date"]
        cur_state = (
            intervals[0]["sign_idx"],
            intervals[0]["kaksha_num"],
            intervals[0]["kaksha_lord"],
            intervals[0]["has_bindu"],
        )
        cur_group = [intervals[0]]

        for item in intervals[1:]:
            st = (
                item["sign_idx"],
                item["kaksha_num"],
                item["kaksha_lord"],
                item["has_bindu"],
            )
            if st != cur_state:
                # Close current interval
                cur_end = cur_group[-1]["date"]
                rep = cur_group[len(cur_group) // 2]
                dur_days = max(1.0, float((cur_end - cur_start).days))
                sign_name = SIGN_NAMES_EN[rep["sign_idx"]]

                domains, severity, en_guide, ta_guide = _evaluate_life_domains_and_guidance(
                    planet=p,
                    house_from_lagna=rep["house_from_lagna"],
                    has_bindu=rep["has_bindu"],
                    kaksha_lord=rep["kaksha_lord"],
                    sign_name=sign_name,
                )

                # Filter by domain if specified
                req_filter = request.filter_domain.lower() if request.filter_domain else "all"
                if req_filter == "all" or req_filter in domains:
                    badge = "Favorable Trigger 🟢" if rep["has_bindu"] else "Obstacle Warning 🔴"
                    raw_alerts.append(
                        KakshaAlertItem(
                            id=f"{p}_{cur_start}_{rep['kaksha_num']}",
                            planet=p,
                            sign_name=sign_name,
                            sign_index=rep["sign_idx"],
                            kaksha_number=rep["kaksha_num"],
                            kaksha_lord=rep["kaksha_lord"],
                            kaksha_range=rep["kaksha_range"],
                            start_date=str(cur_start),
                            end_date=str(cur_end),
                            duration_days=dur_days,
                            has_bindu=rep["has_bindu"],
                            is_favorable=rep["has_bindu"],
                            house_from_lagna=rep["house_from_lagna"],
                            life_domains=domains,
                            alert_badge=badge,
                            severity_level=severity,
                            guidance=en_guide,
                            guidance_ta=ta_guide,
                        )
                    )

                # Reset
                cur_start = item["date"]
                cur_state = st
                cur_group = [item]
            else:
                cur_group.append(item)

        # Close tail
        if cur_group:
            cur_end = cur_group[-1]["date"]
            rep = cur_group[len(cur_group) // 2]
            dur_days = max(1.0, float((cur_end - cur_start).days))
            sign_name = SIGN_NAMES_EN[rep["sign_idx"]]
            domains, severity, en_guide, ta_guide = _evaluate_life_domains_and_guidance(
                planet=p,
                house_from_lagna=rep["house_from_lagna"],
                has_bindu=rep["has_bindu"],
                kaksha_lord=rep["kaksha_lord"],
                sign_name=sign_name,
            )
            req_filter = request.filter_domain.lower() if request.filter_domain else "all"
            if req_filter == "all" or req_filter in domains:
                badge = "Favorable Trigger 🟢" if rep["has_bindu"] else "Obstacle Warning 🔴"
                raw_alerts.append(
                    KakshaAlertItem(
                        id=f"{p}_{cur_start}_{rep['kaksha_num']}",
                        planet=p,
                        sign_name=sign_name,
                        sign_index=rep["sign_idx"],
                        kaksha_number=rep["kaksha_num"],
                        kaksha_lord=rep["kaksha_lord"],
                        kaksha_range=rep["kaksha_range"],
                        start_date=str(cur_start),
                        end_date=str(cur_end),
                        duration_days=dur_days,
                        has_bindu=rep["has_bindu"],
                        is_favorable=rep["has_bindu"],
                        house_from_lagna=rep["house_from_lagna"],
                        life_domains=domains,
                        alert_badge=badge,
                        severity_level=severity,
                        guidance=en_guide,
                        guidance_ta=ta_guide,
                    )
                )

    # Sort alerts chronologically
    raw_alerts.sort(key=lambda a: a.start_date)

    # Metrics
    ausp_count = sum(1 for a in raw_alerts if a.has_bindu)
    inausp_count = sum(1 for a in raw_alerts if not a.has_bindu)

    # Find upcoming peak window and upcoming critical caution
    peak_win = next((a for a in raw_alerts if a.has_bindu and a.severity_level == "High Opportunity"), None)
    if not peak_win:
        peak_win = next((a for a in raw_alerts if a.has_bindu), None)

    caution_win = next((a for a in raw_alerts if not a.has_bindu and a.severity_level == "Caution Required"), None)

    # Domain summary cards
    domain_summaries: Dict[str, DomainAlertSummary] = {
        "health": DomainAlertSummary(
            favorable_windows_count=sum(1 for a in raw_alerts if "health" in a.life_domains and a.has_bindu),
            challenging_windows_count=sum(1 for a in raw_alerts if "health" in a.life_domains and not a.has_bindu),
            key_advice="Prioritize vitality and restorative care during 0-Bindu Mars/Saturn crossings.",
        ),
        "finances": DomainAlertSummary(
            favorable_windows_count=sum(1 for a in raw_alerts if "finances" in a.life_domains and a.has_bindu),
            challenging_windows_count=sum(1 for a in raw_alerts if "finances" in a.life_domains and not a.has_bindu),
            key_advice="Schedule financial closures and investments during 1-Bindu Jupiter/Venus Kakshas.",
        ),
        "career": DomainAlertSummary(
            favorable_windows_count=sum(1 for a in raw_alerts if "career" in a.life_domains and a.has_bindu),
            challenging_windows_count=sum(1 for a in raw_alerts if "career" in a.life_domains and not a.has_bindu),
            key_advice="Seek promotions and initiate negotiations when Saturn or Jupiter transits 1-Bindu Kakshas.",
        ),
        "lawsuits": DomainAlertSummary(
            favorable_windows_count=sum(1 for a in raw_alerts if "lawsuits" in a.life_domains and a.has_bindu),
            challenging_windows_count=sum(1 for a in raw_alerts if "lawsuits" in a.life_domains and not a.has_bindu),
            key_advice="File legal petitions or pursue settlements only when Mars or Saturn commands a Bindu.",
        ),
    }

    return KakshaAlertsResponse(
        natal_lagna_sign=natal_lagna_name,
        natal_lagna_sign_index=natal_lagna_idx,
        horizon_days=horizon_days,
        start_date=str(today),
        end_date=str(end_date),
        active_now=active_status_list,
        timeline_alerts=raw_alerts,
        domain_summaries=domain_summaries,
        total_auspicious_triggers=ausp_count,
        total_inauspicious_triggers=inausp_count,
        upcoming_peak_window=peak_win,
        upcoming_critical_caution=caution_win,
    )
