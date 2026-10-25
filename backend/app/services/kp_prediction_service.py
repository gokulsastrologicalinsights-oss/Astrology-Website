"""KP Events & Prediction Service Layer.

Implements clean-room KP event promise analysis, ruling planets evaluation,
Vimshottari Dasha-Bhukti-Antara period filtering, Moon transit candidate scanning,
Ascendant time-window scanning, and transparent evidence grading.

Powered exclusively by the native XALEN ephemeris engine.
"""

from __future__ import annotations
import math
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import time as pytime
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from zoneinfo import ZoneInfo

import xalen
import xalen.swe as xswe

from app.schemas.kp_prediction import (
    KpPredictionRequest,
    KpPredictionResponse,
    KpEventPromiseResult,
    KpDashaPeriodResult,
    RulingPlanetsInfo,
    KpCandidateTimeWindow,
)
from app.services.kp_engine.vedic import (
    normalize_longitude,
    point_info,
    sign_name,
    sign_lord_of_longitude,
    star_name,
    star_lord,
    sub_lord,
    sub_sub_lord,
    sub_info,
    sub_sub_info,
    star_span,
)
from app.services.kp_event_engine.event_rules import EVENT_REGISTRY, EventRule
from app.services.timezone_utils import resolve_birth_datetime


# Day lords from classical astrology (Sunday = 0 to Saturday = 6)
WEEKDAY_LORDS: List[str] = [
    "Moon",     # Monday (Python weekday 0)
    "Mars",     # Tuesday (1)
    "Mercury",  # Wednesday (2)
    "Jupiter",  # Thursday (3)
    "Venus",    # Friday (4)
    "Saturn",   # Saturday (5)
    "Sun",      # Sunday (6)
]

# Application / XALEN ayanamsa IDs: 0 = Lahiri, 1 = KP (Krishnamurti)
AYANAMSA_LAHIRI = 0
AYANAMSA_KP = 1
DEFAULT_AYANAMSA_ID = AYANAMSA_KP


def _get_xswe_sidm_mode(ayanamsa_id: int) -> int:
    """Maps application / XALEN ayanamsa ID (0=Lahiri, 1=KP) to Swiss Ephemeris SIDM constant."""
    if ayanamsa_id == AYANAMSA_LAHIRI:
        return xswe.SIDM_LAHIRI
    return xswe.SIDM_KRISHNAMURTI


def _angle_diff(angle: float, target: float) -> float:
    """Signed angular distance in (-180, +180] degrees from target to angle."""
    return (angle - target + 180.0) % 360.0 - 180.0


def _jd_to_utc_and_local(jd: float, tz_obj: ZoneInfo) -> Tuple[datetime, datetime]:
    """Convert Julian Day to (utc_dt, local_dt)."""
    unix_seconds = (jd - 2440587.5) * 86400.0
    utc_dt = datetime.fromtimestamp(unix_seconds, tz=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(tz_obj)
    return utc_dt, local_dt


def _bisect_lagna_boundary(
    transit_lat: float,
    transit_lon: float,
    t_start_jd: float,
    t_end_jd: float,
    target_lon: float,
    ayanamsa_id: int,
    tol_seconds: float = 0.5,
    max_iter: int = 25,
) -> Tuple[float, int]:
    """Uses bracketed bisection on XALEN / Placidus houses to find the exact Julian Day
    where the Ascendant crosses target_lon within tol_seconds precision.
    """
    xswe.set_sid_mode(_get_xswe_sidm_mode(ayanamsa_id), 0, 0)
    tol_days = tol_seconds / 86400.0
    a, b = t_start_jd, t_end_jd

    def f(t: float) -> float:
        _, ascmc = xswe.houses_ex(t, transit_lat, transit_lon, b"P", xswe.FLG_SIDEREAL)
        asc = ascmc[0] % 360.0
        return _angle_diff(asc, target_lon)

    fa = f(a)
    fb = f(b)

    if abs(fa) < 1e-7:
        return a, 1
    if abs(fb) < 1e-7:
        return b, 1

    if fa * fb > 0:
        span = b - a
        a_wide = a - span * 0.5
        b_wide = b + span * 0.5
        fa_w = f(a_wide)
        fb_w = f(b_wide)
        if fa_w * fb_w <= 0:
            a, b = a_wide, b_wide
            fa, fb = fa_w, fb_w
        else:
            return (a if abs(fa) < abs(fb) else b), 1

    iterations = 0
    while (b - a) > tol_days and iterations < max_iter:
        iterations += 1
        mid = (a + b) / 2.0
        fmid = f(mid)
        if abs(fmid) < 1e-7:
            return mid, iterations
        if fa * fmid <= 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    return (a + b) / 2.0, iterations


def _bisect_moon_boundary(
    t_start_jd: float,
    t_end_jd: float,
    target_lon: float,
    ayanamsa_id: int,
    tol_seconds: float = 0.5,
    max_iter: int = 25,
) -> Tuple[float, int]:
    """Uses bracketed bisection on Moon sidereal longitude to find exact crossing of target_lon."""
    tol_days = tol_seconds / 86400.0
    a, b = t_start_jd, t_end_jd

    def f(t: float) -> float:
        lon = xalen.planet_longitude(t, 1, True, ayanamsa_id)
        return _angle_diff(lon, target_lon)

    fa = f(a)
    fb = f(b)

    if abs(fa) < 1e-7:
        return a, 1
    if abs(fb) < 1e-7:
        return b, 1

    if fa * fb > 0:
        span = b - a
        a_wide = a - span * 0.5
        b_wide = b + span * 0.5
        fa_w = f(a_wide)
        fb_w = f(b_wide)
        if fa_w * fb_w <= 0:
            a, b = a_wide, b_wide
            fa, fb = fa_w, fb_w
        else:
            return (a if abs(fa) < abs(fb) else b), 1

    iterations = 0
    while (b - a) > tol_days and iterations < max_iter:
        iterations += 1
        mid = (a + b) / 2.0
        fmid = f(mid)
        if abs(fmid) < 1e-7:
            return mid, iterations
        if fa * fmid <= 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    return (a + b) / 2.0, iterations


EVENT_ALIASES: Dict[str, str] = {
    "new job / employment": "Job",
    "new job": "Job",
    "job change": "Job",
    "employment": "Job",
    "child birth": "Children",
    "childbirth": "Children",
    "pregnancy": "Children",
    "business": "Business start",
    "foreign job": "Settlement abroad",
    "passport / visa": "Foreign travel",
    "education": "Higher education",
    "property": "Property purchase",
    "vehicle": "Vehicle purchase",
}


def _get_event_rule(event_name: str) -> EventRule:
    """Retrieves validated EventRule from registry or raises ValueError."""
    # Match exact or case-insensitive
    if event_name in EVENT_REGISTRY:
        return EVENT_REGISTRY[event_name]
    
    clean_name = event_name.strip().lower()
    if clean_name in EVENT_ALIASES:
        return EVENT_REGISTRY[EVENT_ALIASES[clean_name]]

    for k, v in EVENT_REGISTRY.items():
        if k.lower() == clean_name:
            return v
    raise ValueError(f"Unsupported event category: '{event_name}'.")


def get_supported_events_list() -> List[Dict[str, Any]]:
    """Returns list of supported event categories with their metadata."""
    out = []
    for rule in EVENT_REGISTRY.values():
        out.append({
            "name": rule.name,
            "category": rule.category,
            "primary_cusp": rule.primary_cusp,
            "supporting_houses": rule.supporting_houses,
            "denying_houses": rule.denying_houses,
            "is_gain_type": rule.is_gain_type,
            "description": rule.description,
        })
    return out


def evaluate_event_promise(
    kp_chart: Dict[str, Any],
    event_rule: EventRule,
) -> KpEventPromiseResult:
    """Evaluates the natal promise for a specific event using CSL and significators."""
    primary_cusp = event_rule.primary_cusp
    cusps = kp_chart.get("cusps") or kp_chart.get("cuspal_analysis") or []
    if not cusps or len(cusps) < primary_cusp:
        raise ValueError("Invalid KP chart: Missing cusp data.")

    # Find the cusp corresponding to primary_cusp
    cusp_data = None
    for c in cusps:
        if c.get("house") == primary_cusp:
            cusp_data = c
            break
    if not cusp_data and len(cusps) >= primary_cusp:
        cusp_data = cusps[primary_cusp - 1]

    if not cusp_data:
        raise ValueError(f"Could not locate cusp data for house {primary_cusp}")

    csl = cusp_data.get("sub_lord", "")
    csl_star = cusp_data.get("star_lord", "")
    cusp_sign = cusp_data.get("sign_name") or cusp_data.get("sign", "")
    cusp_deg = float(cusp_data.get("cusp_degree") or cusp_data.get("longitude", 0.0))

    # Planetary details from chart
    planets_raw = kp_chart.get("planets") or {}
    if isinstance(planets_raw, list):
        planets = {p.get("planet"): p for p in planets_raw if isinstance(p, dict)}
    elif isinstance(planets_raw, dict):
        planets = planets_raw
    else:
        planets = {}

    if not planets and "planetary_positions" in kp_chart:
        p_list = kp_chart.get("planetary_positions") or []
        planets = {p.get("planet"): p for p in p_list if isinstance(p, dict)}

    csl_planet = planets.get(csl, {})
    is_csl_retro = bool(csl_planet.get("retrograde", False) or csl_planet.get("is_retrograde", False))
    csl_star_lord = csl_planet.get("star_lord", "")
    star_planet = planets.get(csl_star_lord, {})
    is_star_retro = bool(star_planet.get("retrograde", False) or star_planet.get("is_retrograde", False))

    # Significators of CSL (Level A, B, C, D)
    csl_signified_houses: Set[int] = set()

    # Check PlanetSignificator list in significators
    if "significators" in kp_chart and isinstance(kp_chart["significators"], list):
        for sig_item in kp_chart["significators"]:
            if isinstance(sig_item, dict) and sig_item.get("planet") == csl:
                for h in sig_item.get("signified_houses", []):
                    csl_signified_houses.add(int(h))

    # Check house_significators
    house_sigs = kp_chart.get("house_significators")
    if isinstance(house_sigs, dict):
        for h_str, sig_data in house_sigs.items():
            try:
                h_num = int(h_str)
            except (ValueError, TypeError):
                continue
            all_planets = (
                sig_data.get("level_a", [])
                + sig_data.get("level_b", [])
                + sig_data.get("level_c", [])
                + sig_data.get("level_d", [])
            )
            if csl in all_planets:
                csl_signified_houses.add(h_num)
    elif isinstance(house_sigs, list):
        for h_entry in house_sigs:
            if isinstance(h_entry, dict):
                h_num = int(h_entry.get("house", 0))
                all_planets = (
                    h_entry.get("level_a", [])
                    + h_entry.get("level_b", [])
                    + h_entry.get("level_c", [])
                    + h_entry.get("level_d", [])
                )
                if csl in all_planets:
                    csl_signified_houses.add(h_num)

    # In case house_significators not pre-computed, fallback to planet_significations if present
    if not csl_signified_houses and "planet_significations" in kp_chart:
        csl_signified_houses = set(kp_chart["planet_significations"].get(csl, []))

    # If still empty, include at least the cusp house where CSL is deposited
    if not csl_signified_houses:
        csl_signified_houses = {primary_cusp}

    supporting_set = set(event_rule.supporting_houses)
    denying_set = set(event_rule.denying_houses)

    supporting_hits = sorted(list(csl_signified_houses.intersection(supporting_set)))
    denying_hits = sorted(list(csl_signified_houses.intersection(denying_set)))

    # Determine promise status
    if len(supporting_hits) >= 2 or (len(supporting_hits) >= 1 and len(denying_hits) == 0):
        if is_csl_retro or is_star_retro:
            promise_status = "Delayed / Mixed"
            explanation = (
                f"The {primary_cusp}th Cuspal Sub-Lord ({csl}) signifies supporting house(s) "
                f"{supporting_hits}. However, retrograde motion ({csl if is_csl_retro else csl_star_lord}) "
                f"indicates fruition will require perseverance or face initial delays."
            )
        else:
            promise_status = "Promised"
            explanation = (
                f"The {primary_cusp}th Cuspal Sub-Lord ({csl}) signifies supporting house(s) "
                f"{supporting_hits} for {event_rule.name}. The natal horoscope clearly promises this event."
            )
    elif len(supporting_hits) > 0 and len(denying_hits) > 0:
        promise_status = "Delayed / Mixed"
        explanation = (
            f"The {primary_cusp}th Cuspal Sub-Lord ({csl}) signifies supporting houses {supporting_hits} "
            f"alongside obstructing houses {denying_hits}. Mixed indications suggest progress with hurdles."
        )
    else:
        promise_status = "Denied / Weak"
        explanation = (
            f"The {primary_cusp}th Cuspal Sub-Lord ({csl}) does not connect to primary supporting houses "
            f"{event_rule.supporting_houses}. Astrological promise for {event_rule.name} is weak in natal chart."
        )

    return KpEventPromiseResult(
        event_name=event_rule.name,
        category=event_rule.category,
        primary_cusp=primary_cusp,
        cusp_degree=round(cusp_deg, 4),
        cusp_sign=cusp_sign,
        cusp_star_lord=csl_star,
        cusp_sub_lord=csl,
        csl_significations=sorted(list(csl_signified_houses)),
        supporting_houses=event_rule.supporting_houses,
        denying_houses=event_rule.denying_houses,
        promise_status=promise_status,
        is_csl_retrograde=is_csl_retro,
        is_star_lord_retrograde=is_star_retro,
        supporting_hits=supporting_hits,
        denying_hits=denying_hits,
        rule_explanation=explanation,
    )


def calculate_ruling_planets(
    judgement_dt: datetime,
    lat: float,
    lon: float,
    ayanamsa_id: int = DEFAULT_AYANAMSA_ID,
) -> RulingPlanetsInfo:
    """Computes the Ruling Planets (RP) obtaining at the place and moment of judgement."""
    # Convert local judgement datetime to UTC and Julian Day
    if judgement_dt.tzinfo is None:
        judgement_dt = judgement_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    utc_dt = judgement_dt.astimezone(ZoneInfo("UTC"))
    hour_float = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = xalen.julian_day(utc_dt.year, utc_dt.month, utc_dt.day, hour_float)

    # 1. Ascendant at judgement moment & place
    xswe.set_sid_mode(_get_xswe_sidm_mode(ayanamsa_id), 0, 0)
    _, ascmc = xswe.houses_ex(jd, lat, lon, b"P", xswe.FLG_SIDEREAL)
    asc_deg = ascmc[0] % 360.0
    asc_info = point_info(asc_deg)
    asc_sign_lord = asc_info.sign_lord
    asc_star_lord = asc_info.star_lord

    # 2. Moon at judgement moment
    moon_lon = xalen.planet_longitude(jd, 1, True, ayanamsa_id)
    moon_info = point_info(moon_lon)
    moon_sign_lord = moon_info.sign_lord
    moon_star_lord = moon_info.star_lord

    # 3. Day Lord (from weekday of local datetime)
    day_lord = WEEKDAY_LORDS[judgement_dt.weekday()]

    # 4. Check retrograde status of planets
    # Planet IDs: Sun:0, Moon:1, Mercury:2, Venus:3, Mars:4, Jupiter:5, Saturn:6, Rahu:9, Ketu:13
    planet_retro: Dict[str, bool] = {}
    body_map = {
        "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4, "Jupiter": 5, "Saturn": 6,
        "Rahu": 9, "Ketu": 13,
    }
    for p_name, b_id in body_map.items():
        if p_name in ("Rahu", "Ketu", "Sun", "Moon"):
            # In classical KP, only natural planets (Mars, Mercury, Jupiter, Venus, Saturn)
            # count as retrograde for star-rejection
            planet_retro[p_name] = False
        else:
            pos = xalen.planet_position(jd, b_id, True, ayanamsa_id)
            planet_retro[p_name] = bool(pos.get("is_retrograde", False))

    raw_rps = [
        ("Ascendant Star Lord", asc_star_lord),
        ("Ascendant Sign Lord", asc_sign_lord),
        ("Moon Star Lord", moon_star_lord),
        ("Moon Sign Lord", moon_sign_lord),
        ("Day Lord", day_lord),
    ]

    active_rps: List[str] = []
    rejected_rps: List[Dict[str, str]] = []

    for role, p in raw_rps:
        # Check if planet sits in the star of a retrograde planet
        b_id = body_map.get(p, 0)
        p_lon = xalen.planet_longitude(jd, b_id, True, ayanamsa_id)
        p_star_ruler = star_lord(p_lon)
        if planet_retro.get(p_star_ruler, False):
            rejected_rps.append({
                "planet": p,
                "role": role,
                "reason": f"Sits in the star of retrograde planet {p_star_ruler}.",
            })
        else:
            if p not in active_rps:
                active_rps.append(p)

    return RulingPlanetsInfo(
        judgement_time=judgement_dt.isoformat(),
        judgement_place=f"{lat:.4f}, {lon:.4f}",
        ascendant_sign_lord=asc_sign_lord,
        ascendant_star_lord=asc_star_lord,
        moon_sign_lord=moon_sign_lord,
        moon_star_lord=moon_star_lord,
        day_lord=day_lord,
        active_ruling_planets=active_rps,
        rejected_ruling_planets=rejected_rps,
    )


def evaluate_dasha_periods(
    dasa_tree: List[Dict[str, Any]],
    planet_significations: Dict[str, List[int]],
    event_rule: EventRule,
    scan_start: date,
    scan_end: date,
) -> List[KpDashaPeriodResult]:
    """Evaluates Vimshottari Dasha periods spanning the candidate scan window."""
    supporting_set = set(event_rule.supporting_houses)
    denying_set = set(event_rule.denying_houses)
    results: List[KpDashaPeriodResult] = []

    today_str = date.today().isoformat()

    def process_period(node: Dict[str, Any], level: int, parent_md: str, parent_ad: Optional[str]):
        p_lord = node.get("lord", "")
        start_str = str(node.get("start_date") or node.get("start_date_iso") or "").split("T")[0]
        end_str = str(node.get("end_date") or node.get("end_date_iso") or "").split("T")[0]
        if not start_str or not end_str:
            return

        try:
            s_date = date.fromisoformat(start_str)
            e_date = date.fromisoformat(end_str)
        except ValueError:
            return

        children = node.get("children") or node.get("sub_periods") or []

        # Check overlap with [scan_start, scan_end]
        if e_date < scan_start or s_date > scan_end:
            # Recurse if children might overlap
            for child in children:
                process_period(child, level + 1, parent_md, p_lord if level == 1 else parent_ad)
            return

        is_running = (s_date <= date.today() <= e_date)
        sig_houses = planet_significations.get(p_lord, [])
        s_hits = set(sig_houses).intersection(supporting_set)
        d_hits = set(sig_houses).intersection(denying_set)

        if len(s_hits) >= 2 or (len(s_hits) >= 1 and len(d_hits) == 0):
            status = "Strongly Supportive"
            explanation = f"{p_lord} strongly signifies supporting houses {sorted(list(s_hits))}."
        elif len(s_hits) >= 1 and len(d_hits) >= 1:
            status = "Supportive"
            explanation = f"{p_lord} signifies supporting houses {sorted(list(s_hits))} alongside {sorted(list(d_hits))}."
        elif len(d_hits) >= 1:
            status = "Unfavorable"
            explanation = f"{p_lord} signifies obstructing houses {sorted(list(d_hits))}."
        else:
            status = "Mixed"
            explanation = f"{p_lord} has neutral signification {sig_houses}."

        results.append(
            KpDashaPeriodResult(
                level=level,
                mahadasha_lord=parent_md if level > 1 else p_lord,
                bhukti_lord=p_lord if level == 2 else parent_ad,
                antara_lord=p_lord if level == 3 else None,
                start_date=start_str,
                end_date=end_str,
                is_running=is_running,
                signified_houses=sorted(sig_houses),
                support_status=status,
                scoring_explanation=explanation,
            )
        )

        for child in children:
            process_period(child, level + 1, parent_md if level > 1 else p_lord, p_lord if level == 2 else parent_ad)

    for md_node in dasa_tree:
        process_period(md_node, 1, md_node.get("lord", ""), None)

    return results


def scan_candidate_event_windows(
    kp_chart: Dict[str, Any],
    event_rule: EventRule,
    dasa_tree: List[Dict[str, Any]],
    scan_start: date,
    scan_end: date,
    transit_lat: float,
    transit_lon: float,
    transit_tz_str: str,
    ruling_planets: Set[str],
    max_candidates: int = 30,
    scan_res_min: int = 5,
    ayanamsa_id: int = DEFAULT_AYANAMSA_ID,
    scan_mode: str = "standard",
    deep_refinement_target: str = "sub_lord",
    deep_max_intervals_to_refine: int = 15,
    return_benchmark_metrics: bool = False,
    timeout_seconds: float = 10.0,
) -> Union[List[KpCandidateTimeWindow], Tuple[List[KpCandidateTimeWindow], Dict[str, Any]]]:
    """Scans candidate dates (Moon transit) and time windows (Ascendant transit)
    gated by Vimshottari Dasha periods and Ruling Planets.

    Supports 'standard' (coarse grid) and 'deep' (adaptive bisection to sub-second precision).
    """
    t_start_perf = pytime.perf_counter()
    tz = ZoneInfo(transit_tz_str)
    supporting_houses = set(event_rule.supporting_houses)

    # Derive planet house significations map
    house_sigs = kp_chart.get("house_significators") or {}
    planet_sigs: Dict[str, Set[int]] = {}
    if isinstance(house_sigs, dict):
        for h_str, s_data in house_sigs.items():
            try:
                h_num = int(h_str)
            except (ValueError, TypeError):
                continue
            all_p = s_data.get("level_a", []) + s_data.get("level_b", []) + s_data.get("level_c", []) + s_data.get("level_d", [])
            for p in all_p:
                if p not in planet_sigs:
                    planet_sigs[p] = set()
                planet_sigs[p].add(h_num)
    elif isinstance(house_sigs, list):
        for s_entry in house_sigs:
            if isinstance(s_entry, dict):
                h_num = int(s_entry.get("house", 0))
                all_p = s_entry.get("level_a", []) + s_entry.get("level_b", []) + s_entry.get("level_c", []) + s_entry.get("level_d", [])
                for p in all_p:
                    if p not in planet_sigs:
                        planet_sigs[p] = set()
                    planet_sigs[p].add(h_num)

    if not planet_sigs and "significators" in kp_chart and isinstance(kp_chart["significators"], list):
        for sig_item in kp_chart["significators"]:
            if isinstance(sig_item, dict):
                p_name = sig_item.get("planet")
                for h in sig_item.get("signified_houses", []):
                    if p_name not in planet_sigs:
                        planet_sigs[p_name] = set()
                    planet_sigs[p_name].add(int(h))

    # Effective significators for the event (planets that signify at least one supporting house)
    event_significator_planets: Set[str] = {
        p for p, houses in planet_sigs.items() if houses.intersection(supporting_houses)
    }

    # Combined target pool = Ruling Planets | Event Significators
    target_pool = ruling_planets.union(event_significator_planets)
    if not target_pool:
        # Fallback to all planet names if empty
        target_pool = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

    # Helper: Find active dasha chain for a specific datetime
    def get_dasha_chain_at(dt_target: datetime) -> Tuple[List[str], bool]:
        target_date = dt_target.date()
        chain = []
        is_fav = False
        for md in dasa_tree:
            s_md = str(md.get("start_date") or md.get("start_date_iso") or "").split("T")[0]
            e_md = str(md.get("end_date") or md.get("end_date_iso") or "").split("T")[0]
            if not s_md or not e_md:
                continue
            try:
                md_start = date.fromisoformat(s_md)
                md_end = date.fromisoformat(e_md)
            except ValueError:
                continue

            if md_start <= target_date <= md_end:
                chain.append(md.get("lord", ""))
                ad_list = md.get("children") or md.get("sub_periods") or []
                for ad in ad_list:
                    s_ad = str(ad.get("start_date") or ad.get("start_date_iso") or "").split("T")[0]
                    e_ad = str(ad.get("end_date") or ad.get("end_date_iso") or "").split("T")[0]
                    if not s_ad or not e_ad:
                        continue
                    try:
                        ad_start = date.fromisoformat(s_ad)
                        ad_end = date.fromisoformat(e_ad)
                    except ValueError:
                        continue

                    if ad_start <= target_date <= ad_end:
                        chain.append(ad.get("lord", ""))
                        pd_list = ad.get("children") or ad.get("sub_periods") or []
                        for pd in pd_list:
                            s_pd = str(pd.get("start_date") or pd.get("start_date_iso") or "").split("T")[0]
                            e_pd = str(pd.get("end_date") or pd.get("end_date_iso") or "").split("T")[0]
                            if not s_pd or not e_pd:
                                continue
                            try:
                                pd_start = date.fromisoformat(s_pd)
                                pd_end = date.fromisoformat(e_pd)
                            except ValueError:
                                continue

                            if pd_start <= target_date <= pd_end:
                                chain.append(pd.get("lord", ""))
                                break
                        break
                break

        # Check if lords in chain signify supporting houses
        fav_count = sum(1 for p in chain if planet_sigs.get(p, set()).intersection(supporting_houses))
        is_fav = (fav_count >= 2) if len(chain) >= 2 else (fav_count >= 1)
        return chain, is_fav

    # Step 1: Scan candidate Moon transit dates
    # Sample daily in 6-hour intervals (06:00, 12:00, 18:00) to detect qualifying Moon sign & star & sub lords
    candidate_moon_days: Set[date] = set()
    current_day = scan_start
    while current_day <= scan_end:
        is_candidate_day = False
        for sample_hour in (6, 12, 18):
            sample_dt = datetime.combine(current_day, time(sample_hour, 0), tzinfo=tz)
            utc_dt = sample_dt.astimezone(ZoneInfo("UTC"))
            hour_float = utc_dt.hour + utc_dt.minute / 60.0
            jd = xalen.julian_day(utc_dt.year, utc_dt.month, utc_dt.day, hour_float)
            m_lon = xalen.planet_longitude(jd, 1, True, ayanamsa_id)
            m_info = point_info(m_lon)

            # Moon qualifies if its sign lord, star lord, or sub lord matches target pool
            matches = 0
            if m_info.sign_lord in target_pool:
                matches += 1
            if m_info.star_lord in target_pool:
                matches += 1
            if m_info.sub_lord in target_pool:
                matches += 1

            if matches >= 2:
                is_candidate_day = True
                break

        if is_candidate_day:
            candidate_moon_days.add(current_day)

        current_day += timedelta(days=1)

    # If no days passed strict 2-match threshold, relax to 1-match
    if not candidate_moon_days:
        current_day = scan_start
        while current_day <= scan_end:
            candidate_moon_days.add(current_day)
            current_day += timedelta(days=2)  # sample alternate days

    xswe.set_sid_mode(_get_xswe_sidm_mode(ayanamsa_id), 0, 0)

    # Step 2: For candidate days, scan Ascendant (Lagna) windows across the full range
    candidate_windows: List[KpCandidateTimeWindow] = []
    max_scan_cap = max(max_candidates * 10, 300)

    for c_date in sorted(list(candidate_moon_days)):
        if len(candidate_windows) >= max_scan_cap:
            break

        # Scan 24 hours of c_date with step scan_res_min
        current_minute = 0
        window_start_dt: Optional[datetime] = None
        window_last_dt: Optional[datetime] = None
        window_moon_info: Optional[Any] = None
        window_lagna_info: Optional[Any] = None

        while current_minute < 1440:
            h = current_minute // 60
            m = current_minute % 60
            step_dt = datetime.combine(c_date, time(h, m), tzinfo=tz)
            utc_dt = step_dt.astimezone(ZoneInfo("UTC"))
            hour_float = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            jd = xalen.julian_day(utc_dt.year, utc_dt.month, utc_dt.day, hour_float)

            # Ascendant calculation
            try:
                _, ascmc = xswe.houses_ex(jd, transit_lat, transit_lon, b"P", xswe.FLG_SIDEREAL)
                asc_deg = ascmc[0] % 360.0
                lagna_info = point_info(asc_deg)
            except Exception:
                current_minute += scan_res_min
                continue

            # Qualifying condition for Lagna transit:
            # Lagna Sign Lord, Star Lord, Sub Lord, or Sub-sub Lord is in target pool
            lagna_hits = 0
            if lagna_info.sign_lord in target_pool:
                lagna_hits += 1
            if lagna_info.star_lord in target_pool:
                lagna_hits += 1
            if lagna_info.sub_lord in target_pool:
                lagna_hits += 1
            if lagna_info.sub_sub_lord in target_pool:
                lagna_hits += 1

            is_qualifying = (lagna_hits >= 2)

            if is_qualifying:
                if window_start_dt is None:
                    window_start_dt = step_dt
                    # Capture Moon state at window start
                    m_lon = xalen.planet_longitude(jd, 1, True, ayanamsa_id)
                    window_moon_info = point_info(m_lon)
                window_last_dt = step_dt
                window_lagna_info = lagna_info
            else:
                if window_start_dt is not None and window_last_dt is not None:
                    # Close out window if length >= 10 mins
                    dur_min = (window_last_dt - window_start_dt).total_seconds() / 60.0
                    if dur_min >= 10.0:
                        cand = _build_candidate_window(
                            window_start_dt,
                            window_last_dt,
                            transit_tz_str,
                            window_moon_info,
                            window_lagna_info,
                            get_dasha_chain_at(window_start_dt),
                            event_rule,
                            ruling_planets,
                            planet_sigs,
                            target_pool,
                            scan_res_min,
                        )
                        candidate_windows.append(cand)
                    window_start_dt = None
                    window_last_dt = None

            current_minute += scan_res_min

        # Close out trailing window at midnight
        if window_start_dt is not None and window_last_dt is not None:
            dur_min = (window_last_dt - window_start_dt).total_seconds() / 60.0
            if dur_min >= 10.0:
                cand = _build_candidate_window(
                    window_start_dt,
                    window_last_dt,
                    transit_tz_str,
                    window_moon_info,
                    window_lagna_info,
                    get_dasha_chain_at(window_start_dt),
                    event_rule,
                    ruling_planets,
                    planet_sigs,
                    target_pool,
                    scan_res_min,
                )
                candidate_windows.append(cand)

    # Rank all coarse candidate windows across the entire scan range
    candidate_windows.sort(key=lambda w: (-w.composite_score, w.date, w.start_time))

    # Phase 2: If deep scan mode is active, adaptively refine the top candidate windows
    intervals_refined_count = 0
    if scan_mode == "deep" and candidate_windows:
        num_to_refine = min(len(candidate_windows), deep_max_intervals_to_refine, max_candidates)
        refined_list: List[KpCandidateTimeWindow] = []
        for i in range(num_to_refine):
            if (pytime.perf_counter() - t_start_perf) > timeout_seconds:
                refined_list.extend(candidate_windows[i:])
                break
            w_coarse = candidate_windows[i]
            try:
                w_refined = _refine_candidate_window_deep(
                    cand=w_coarse,
                    scan_res_min=scan_res_min,
                    transit_lat=transit_lat,
                    transit_lon=transit_lon,
                    tz_str=transit_tz_str,
                    event_rule=event_rule,
                    ruling_planets=ruling_planets,
                    planet_sigs=planet_sigs,
                    target_pool=target_pool,
                    get_dasha_chain_at=get_dasha_chain_at,
                    ayanamsa_id=ayanamsa_id,
                    refinement_target=deep_refinement_target,
                )
                refined_list.append(w_refined)
                intervals_refined_count += 1
            except Exception as exc:
                w_coarse.refinement_resolution = f"Coarse fallback: {exc}"
                refined_list.append(w_coarse)

        if len(candidate_windows) > num_to_refine:
            refined_list.extend(candidate_windows[num_to_refine:])

        candidate_windows = refined_list
        candidate_windows.sort(key=lambda w: (0 if w.scan_mode == "deep" else 1, -w.composite_score, w.date, w.start_time))

    elapsed_ms = round((pytime.perf_counter() - t_start_perf) * 1000.0, 2)
    benchmark_metrics = {
        "scan_mode": scan_mode,
        "deep_refinement_target": deep_refinement_target,
        "execution_time_ms": elapsed_ms,
        "candidate_moon_days_count": len(candidate_moon_days),
        "coarse_windows_evaluated": len(candidate_windows),
        "intervals_refined": intervals_refined_count,
        "astronomical_precision_seconds": 0.5 if scan_mode == "deep" else float(scan_res_min * 60),
    }

    final_windows = candidate_windows[:max_candidates]
    if return_benchmark_metrics:
        return final_windows, benchmark_metrics
    return final_windows


def _build_candidate_window(
    start_dt: datetime,
    end_dt: datetime,
    tz_str: str,
    moon_info: Any,
    lagna_info: Any,
    dasha_tuple: Tuple[List[str], bool],
    event_rule: EventRule,
    ruling_planets: Set[str],
    planet_sigs: Dict[str, Set[int]],
    target_pool: Set[str],
    scan_res_min: int = 5,
) -> KpCandidateTimeWindow:
    """Constructs and scores a single KpCandidateTimeWindow."""
    dasha_chain, dasha_fav = dasha_tuple
    dasha_str = " > ".join(dasha_chain) if dasha_chain else "Dasha active"

    # Matched ruling planets (sign, star, and sub lords of Moon and Lagna)
    matched_rps: Set[str] = set()
    for p in [moon_info.sign_lord, moon_info.star_lord, moon_info.sub_lord,
              lagna_info.sign_lord, lagna_info.star_lord, lagna_info.sub_lord]:
        if p in ruling_planets:
            matched_rps.add(p)

    # Activated supporting houses
    activated_houses: Set[int] = set()
    for p in [moon_info.star_lord, moon_info.sub_lord, lagna_info.star_lord, lagna_info.sub_lord]:
        activated_houses.update(planet_sigs.get(p, set()).intersection(set(event_rule.supporting_houses)))

    # Composite scoring:
    # Dasha support: 40 pts
    # Moon alignment: 25 pts
    # Lagna alignment: 25 pts
    # RP resonance / Fine alignment: 10 pts
    score = 0.0
    if dasha_fav:
        score += 40.0
    else:
        score += 20.0

    # Moon transit alignment with target pool (supporting significators + ruling planets)
    moon_hits = (1 if moon_info.star_lord in target_pool else 0) + (1 if moon_info.sub_lord in target_pool else 0)
    score += (moon_hits / 2.0) * 25.0

    # Lagna transit alignment with target pool
    lagna_hits = (1 if lagna_info.star_lord in target_pool else 0) + (1 if lagna_info.sub_lord in target_pool else 0)
    score += (lagna_hits / 2.0) * 25.0

    # Ruling planet resonance (or fine sub-sub lord alignment if RPs not enabled)
    if ruling_planets:
        rp_ratio = min(len(matched_rps) / 3.0, 1.0)
        score += rp_ratio * 10.0
    else:
        extra_hits = (1 if moon_info.sign_lord in target_pool else 0) + (1 if lagna_info.sign_lord in target_pool else 0)
        score += (extra_hits / 2.0) * 10.0

    score = round(min(max(score, 15.0), 98.0), 1)

    if score >= 75.0:
        grade = "A"
    elif score >= 50.0:
        grade = "B"
    else:
        grade = "C"

    explanation = (
        f"Transit Moon in {moon_info.sign} ({moon_info.star} / Sub: {moon_info.sub_lord}) with "
        f"Ascendant in {lagna_info.sign} (Sub: {lagna_info.sub_lord}). "
        f"Ruling planets [{', '.join(sorted(list(matched_rps)))}] active. "
        f"Running Dasha ({dasha_str}) {'strongly supports' if dasha_fav else 'moderately connects to'} the event."
    )

    return KpCandidateTimeWindow(
        id=str(uuid.uuid4())[:8],
        date=start_dt.strftime("%Y-%m-%d"),
        start_time=start_dt.strftime("%H:%M:%S"),
        end_time=end_dt.strftime("%H:%M:%S"),
        timezone=tz_str,
        evidence_grade=grade,
        composite_score=score,
        dasha_chain=dasha_str,
        dasha_favorable=dasha_fav,
        moon_transit={
            "sign": moon_info.sign,
            "sign_lord": moon_info.sign_lord,
            "star": moon_info.star,
            "star_lord": moon_info.star_lord,
            "sub_lord": moon_info.sub_lord,
            "sub_sub_lord": moon_info.sub_sub_lord,
        },
        lagna_transit={
            "sign": lagna_info.sign,
            "sign_lord": lagna_info.sign_lord,
            "star": lagna_info.star,
            "star_lord": lagna_info.star_lord,
            "sub_lord": lagna_info.sub_lord,
            "sub_sub_lord": lagna_info.sub_sub_lord,
        },
        ruling_planets_matched=sorted(list(matched_rps)),
        supporting_houses_activated=sorted(list(activated_houses)),
        explanation=explanation,
        scan_mode="standard",
        refinement_resolution=f"{scan_res_min}m (coarse grid)",
        precision_seconds=float(scan_res_min * 60),
        transit_transitions=None,
    )


def _refine_candidate_window_deep(
    cand: KpCandidateTimeWindow,
    scan_res_min: int,
    transit_lat: float,
    transit_lon: float,
    tz_str: str,
    event_rule: EventRule,
    ruling_planets: Set[str],
    planet_sigs: Dict[str, Set[int]],
    target_pool: Set[str],
    get_dasha_chain_at: Any,
    ayanamsa_id: int,
    refinement_target: str = "sub_lord",
) -> KpCandidateTimeWindow:
    """Performs adaptive bisection on Ascendant and Moon transit boundaries for a candidate window."""
    tz = ZoneInfo(tz_str)

    # Parse candidate window start & end times
    start_dt = datetime.strptime(f"{cand.date} {cand.start_time}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    end_dt = datetime.strptime(f"{cand.date} {cand.end_time}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

    start_utc = start_dt.astimezone(ZoneInfo("UTC"))
    end_utc = end_dt.astimezone(ZoneInfo("UTC"))

    h_start = start_utc.hour + start_utc.minute / 60.0 + start_utc.second / 3600.0
    start_jd = xalen.julian_day(start_utc.year, start_utc.month, start_utc.day, h_start)

    h_end = end_utc.hour + end_utc.minute / 60.0 + end_utc.second / 3600.0
    end_jd = xalen.julian_day(end_utc.year, end_utc.month, end_utc.day, h_end)

    xswe.set_sid_mode(_get_xswe_sidm_mode(ayanamsa_id), 0, 0)

    # Lagna at start and end
    _, ascmc_start = xswe.houses_ex(start_jd, transit_lat, transit_lon, b"P", xswe.FLG_SIDEREAL)
    asc_deg_start = ascmc_start[0] % 360.0

    _, ascmc_end = xswe.houses_ex(end_jd, transit_lat, transit_lon, b"P", xswe.FLG_SIDEREAL)
    asc_deg_end = ascmc_end[0] % 360.0

    if refinement_target == "sub_sub_lord":
        div_start = sub_sub_info(asc_deg_start)
        div_end = sub_sub_info(asc_deg_end)
    else:
        div_start = sub_info(asc_deg_start)
        div_end = sub_info(asc_deg_end)

    lambda_ingress = div_start.start_deg
    lambda_egress = div_end.end_deg

    # Bracket for ingress around start_jd:
    step_days = (scan_res_min * 1.5) / 1440.0
    jd_ingress, iter_in = _bisect_lagna_boundary(
        transit_lat, transit_lon,
        start_jd - step_days, start_jd + step_days,
        lambda_ingress, ayanamsa_id, tol_seconds=0.5
    )

    # Bracket for egress around end_jd:
    jd_egress, iter_out = _bisect_lagna_boundary(
        transit_lat, transit_lon,
        end_jd - step_days, end_jd + step_days,
        lambda_egress, ayanamsa_id, tol_seconds=0.5
    )

    # Convert refined JD to datetimes
    refined_start_utc, refined_start_local = _jd_to_utc_and_local(jd_ingress, tz)
    refined_end_utc, refined_end_local = _jd_to_utc_and_local(jd_egress, tz)

    # Sanity checks on refined timestamps
    if refined_start_local >= refined_end_local or (refined_end_local - refined_start_local).total_seconds() < 60.0:
        refined_start_local = start_dt
        refined_end_local = end_dt
        jd_ingress = start_jd
        jd_egress = end_jd

    jd_mid = (jd_ingress + jd_egress) / 2.0
    _, refined_mid_local = _jd_to_utc_and_local(jd_mid, tz)

    # Check Moon transit during the refined interval
    m_lon_start = xalen.planet_longitude(jd_ingress, 1, True, ayanamsa_id)
    m_lon_end = xalen.planet_longitude(jd_egress, 1, True, ayanamsa_id)
    m_lon_mid = xalen.planet_longitude(jd_mid, 1, True, ayanamsa_id)

    moon_crossed = False
    moon_cross_time = None
    moon_from_sub = None
    moon_to_sub = None

    if refinement_target == "sub_sub_lord":
        m_div_start = sub_sub_info(m_lon_start)
        m_div_end = sub_sub_info(m_lon_end)
        if m_div_start.lord != m_div_end.lord:
            moon_crossed = True
            jd_moon_cross, _ = _bisect_moon_boundary(
                jd_ingress, jd_egress, m_div_start.end_deg, ayanamsa_id, tol_seconds=0.5
            )
            _, m_cross_local = _jd_to_utc_and_local(jd_moon_cross, tz)
            moon_cross_time = m_cross_local.strftime("%H:%M:%S")
            moon_from_sub = m_div_start.lord
            moon_to_sub = m_div_end.lord
        else:
            moon_from_sub = m_div_start.lord
            moon_to_sub = m_div_start.lord
    else:
        m_div_start = sub_info(m_lon_start)
        m_div_end = sub_info(m_lon_end)
        if m_div_start.lord != m_div_end.lord:
            moon_crossed = True
            jd_moon_cross, _ = _bisect_moon_boundary(
                jd_ingress, jd_egress, m_div_start.end_deg, ayanamsa_id, tol_seconds=0.5
            )
            _, m_cross_local = _jd_to_utc_and_local(jd_moon_cross, tz)
            moon_cross_time = m_cross_local.strftime("%H:%M:%S")
            moon_from_sub = m_div_start.lord
            moon_to_sub = m_div_end.lord
        else:
            moon_from_sub = m_div_start.lord
            moon_to_sub = m_div_start.lord

    # Midpoint states for Moon and Lagna
    refined_moon_info = point_info(m_lon_mid)
    _, ascmc_mid = xswe.houses_ex(jd_mid, transit_lat, transit_lon, b"P", xswe.FLG_SIDEREAL)
    refined_lagna_info = point_info(ascmc_mid[0] % 360.0)

    # Re-evaluate Dasha periods across refined window
    dasha_start_chain, _ = get_dasha_chain_at(refined_start_local)
    dasha_mid_chain, dasha_mid_fav = get_dasha_chain_at(refined_mid_local)
    dasha_end_chain, _ = get_dasha_chain_at(refined_end_local)
    dasha_transition = (dasha_start_chain != dasha_end_chain)
    dasha_str = " > ".join(dasha_mid_chain) if dasha_mid_chain else cand.dasha_chain

    # Re-evaluate ruling planets resonance at midpoint
    matched_rps: Set[str] = set()
    for p in [refined_moon_info.sign_lord, refined_moon_info.star_lord, refined_moon_info.sub_lord,
              refined_lagna_info.sign_lord, refined_lagna_info.star_lord, refined_lagna_info.sub_lord]:
        if p in ruling_planets:
            matched_rps.add(p)

    activated_houses: Set[int] = set()
    for p in [refined_moon_info.star_lord, refined_moon_info.sub_lord,
              refined_lagna_info.star_lord, refined_lagna_info.sub_lord]:
        activated_houses.update(planet_sigs.get(p, set()).intersection(set(event_rule.supporting_houses)))

    # Re-score composite evidence
    score = 0.0
    if dasha_mid_fav:
        score += 40.0
    else:
        score += 20.0

    moon_hits = (1 if refined_moon_info.star_lord in target_pool else 0) + (1 if refined_moon_info.sub_lord in target_pool else 0)
    score += (moon_hits / 2.0) * 25.0

    lagna_hits = (1 if refined_lagna_info.star_lord in target_pool else 0) + (1 if refined_lagna_info.sub_lord in target_pool else 0)
    score += (lagna_hits / 2.0) * 25.0

    if ruling_planets:
        rp_ratio = min(len(matched_rps) / 3.0, 1.0)
        score += rp_ratio * 10.0
    else:
        extra_hits = (1 if refined_moon_info.sign_lord in target_pool else 0) + (1 if refined_lagna_info.sign_lord in target_pool else 0)
        score += (extra_hits / 2.0) * 10.0

    score = round(min(max(score, 15.0), 98.0), 1)

    if score >= 75.0:
        grade = "A"
    elif score >= 50.0:
        grade = "B"
    else:
        grade = "C"

    transitions_dict = {
        "refinement_level": refinement_target,
        "astronomical_precision_seconds": 0.5,
        "lagna_ingress_time": refined_start_local.strftime("%H:%M:%S"),
        "lagna_egress_time": refined_end_local.strftime("%H:%M:%S"),
        "lagna_ingress_degree": round(div_start.start_deg, 4),
        "lagna_egress_degree": round(div_end.end_deg, 4),
        "lagna_sub_lord": refined_lagna_info.sub_lord,
        "lagna_sub_sub_lord": refined_lagna_info.sub_sub_lord,
        "moon_sub_lord_ingress_in_window": moon_crossed,
        "moon_crossing_time": moon_cross_time,
        "moon_from_sub_lord": moon_from_sub,
        "moon_to_sub_lord": moon_to_sub,
        "dasha_transition_in_window": dasha_transition,
        "dasha_chain_at_midpoint": dasha_str,
        "disclaimer": (
            "Transit boundary timestamps reflect astronomical ingress/egress "
            "derived from XALEN/Placidus bisection. Favorable astrological transit resonance "
            "does not guarantee deterministic occurrence of events."
        ),
    }

    refined_explanation = (
        f"Deep Scan refined (±0.5s bisection): Transit Moon in {refined_moon_info.sign} "
        f"({refined_moon_info.star} / Sub: {refined_moon_info.sub_lord}) with Lagna in {refined_lagna_info.sign} "
        f"(Sub: {refined_lagna_info.sub_lord}, Sub-Sub: {refined_lagna_info.sub_sub_lord}). "
        f"Ruling planets [{', '.join(sorted(list(matched_rps)))}] active. "
        f"Running Dasha ({dasha_str}) {'strongly supports' if dasha_mid_fav else 'moderately connects to'} the event."
    )
    if moon_crossed and moon_cross_time:
        refined_explanation += f" Moon ingresses into {moon_to_sub} sub at {moon_cross_time}."

    return KpCandidateTimeWindow(
        id=cand.id,
        date=cand.date,
        start_time=refined_start_local.strftime("%H:%M:%S"),
        end_time=refined_end_local.strftime("%H:%M:%S"),
        timezone=tz_str,
        evidence_grade=grade,
        composite_score=score,
        dasha_chain=dasha_str,
        dasha_favorable=dasha_mid_fav,
        moon_transit={
            "sign": refined_moon_info.sign,
            "sign_lord": refined_moon_info.sign_lord,
            "star": refined_moon_info.star,
            "star_lord": refined_moon_info.star_lord,
            "sub_lord": refined_moon_info.sub_lord,
            "sub_sub_lord": refined_moon_info.sub_sub_lord,
        },
        lagna_transit={
            "sign": refined_lagna_info.sign,
            "sign_lord": refined_lagna_info.sign_lord,
            "star": refined_lagna_info.star,
            "star_lord": refined_lagna_info.star_lord,
            "sub_lord": refined_lagna_info.sub_lord,
            "sub_sub_lord": refined_lagna_info.sub_sub_lord,
        },
        ruling_planets_matched=sorted(list(matched_rps)),
        supporting_houses_activated=sorted(list(activated_houses)),
        explanation=refined_explanation,
        scan_mode="deep",
        refinement_resolution="0.5s (adaptive bisection)",
        precision_seconds=0.5,
        transit_transitions=transitions_dict,
    )


def generate_kp_prediction_report_markdown(resp: KpPredictionResponse) -> str:
    """Generates clean, printable/downloadable GitHub-flavored markdown report."""
    md = []
    md.append(f"# KP Event Analysis & Timing Report: {resp.event_promise.event_name}")
    md.append(f"**Customer:** {resp.customer_name or 'Native'} | **Date:** {date.today().isoformat()}")
    md.append(f"**Calculation Engine:** {resp.calculation_convention}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Natal Event Promise Analysis")
    p = resp.event_promise
    md.append(f"- **Event Category:** {p.category}")
    md.append(f"- **Primary Cusp:** {p.primary_cusp}th House ({p.cusp_sign} {p.cusp_degree}°)")
    md.append(f"- **Cuspal Sub-Lord (CSL):** **{p.cusp_sub_lord}** (Star Lord: {p.cusp_star_lord})")
    md.append(f"- **CSL Signified Houses:** {p.csl_significations}")
    md.append(f"- **Supporting Houses:** {p.supporting_houses} | **Obstructing Houses:** {p.denying_houses}")
    md.append(f"- **Astrological Promise:** **{p.promise_status}**")
    md.append(f"> {p.rule_explanation}")
    md.append("")

    if resp.ruling_planets:
        rp = resp.ruling_planets
        md.append("## 2. Ruling Planets at Judgement Moment")
        md.append(f"- **Judgement Time:** {rp.judgement_time} ({rp.judgement_place})")
        md.append(f"- **Ascendant Lords:** Sign: {rp.ascendant_sign_lord} | Star: {rp.ascendant_star_lord}")
        md.append(f"- **Moon Lords:** Sign: {rp.moon_sign_lord} | Star: {rp.moon_star_lord}")
        md.append(f"- **Day Lord:** {rp.day_lord}")
        md.append(f"- **Active Ruling Planets:** {', '.join(rp.active_ruling_planets)}")
        if rp.rejected_ruling_planets:
            md.append("- **Rejected RPs (Retrograde Star):** " + ", ".join([f"{r['planet']} ({r['reason']})" for r in rp.rejected_ruling_planets]))
        md.append("")

    md.append("## 3. Supporting Dasha-Bhukti Periods")
    if resp.candidate_dasha_periods:
        md.append("| Period Level | Lords | Start Date | End Date | Status |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for dp in resp.candidate_dasha_periods[:8]:
            lords_str = dp.mahadasha_lord
            if dp.bhukti_lord:
                lords_str += f" > {dp.bhukti_lord}"
            if dp.antara_lord:
                lords_str += f" > {dp.antara_lord}"
            md.append(f"| Level {dp.level} | {lords_str} | {dp.start_date} | {dp.end_date} | {dp.support_status} |")
    else:
        md.append("No active Dasha periods identified within the specified date range.")
    md.append("")

    md.append("## 4. Candidate Event Dates & Time Windows")
    is_deep = any(w.scan_mode == "deep" for w in resp.candidate_windows) or (resp.scan_parameters.get("scan_mode") == "deep")
    if is_deep:
        md.append(f"> **Deep Scan Mode Active:** Candidate intervals adaptively refined using XALEN ephemeris bisection to sub-second astronomical precision (±0.5s).")
        md.append("")
        md.append("| Date | Time Window | Resolution | Grade | Score | Dasha Chain | Transit Details & Exact Boundaries |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for w in resp.candidate_windows:
            moon_desc = f"{w.moon_transit['sign']} ({w.moon_transit['sub_lord']})"
            lagna_desc = f"{w.lagna_transit['sign']} (Sub: {w.lagna_transit['sub_lord']})"
            res_str = w.refinement_resolution or "0.5s bisection"
            trans_info = ""
            if w.transit_transitions:
                tt = w.transit_transitions
                trans_info = f"<br><sub>Ingress: {tt.get('lagna_ingress_time')} ({tt.get('lagna_ingress_degree')}°) | Egress: {tt.get('lagna_egress_time')}</sub>"
                if tt.get("moon_sub_lord_ingress_in_window"):
                    trans_info += f"<br><sub>Moon crossed to {tt.get('moon_to_sub_lord')} @ {tt.get('moon_crossing_time')}</sub>"
            md.append(f"| {w.date} | {w.start_time} - {w.end_time} | {res_str} | **Grade {w.evidence_grade}** | {w.composite_score} | {w.dasha_chain} | Moon: {moon_desc}, Lagna: {lagna_desc}{trans_info} |")
    else:
        if resp.candidate_windows:
            md.append("| Date | Time Window | Grade | Score | Dasha Chain | Transit Details |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for w in resp.candidate_windows:
                moon_desc = f"{w.moon_transit['sign']} ({w.moon_transit['sub_lord']})"
                lagna_desc = f"{w.lagna_transit['sign']} ({w.lagna_transit['sub_lord']})"
                md.append(f"| {w.date} | {w.start_time} - {w.end_time} | **Grade {w.evidence_grade}** | {w.composite_score} | {w.dasha_chain} | Moon: {moon_desc}, Lagna: {lagna_desc} |")
        else:
            md.append("No qualifying event windows met the required threshold within the scanned date range.")
    md.append("")

    md.append("## 5. Important Astrological Disclaimer")
    md.append(f"> {resp.limitations_disclaimer}")
    md.append(f"> *Note:* {resp.birth_time_accuracy_warning}")
    if is_deep:
        md.append("")
        md.append("> **Astronomical Precision vs. Predictive Outcome:** Deep Scan calculates the exact mathematical timestamps when the transit Ascendant and Moon enter and depart the KP sub-divisions with sub-second astronomical precision. High transit alignment indicates celestial harmony according to KP theory, but does NOT guarantee real-world event fruition at the calculated second.")

    return "\n".join(md)
