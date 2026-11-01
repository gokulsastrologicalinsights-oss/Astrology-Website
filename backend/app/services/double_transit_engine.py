"""Double Transit ('Guru-Shani') Event Timing Radar Engine.

Implements the classical Vedic 'Double Transit Principle' (Guru-Shani Samyama):
A major event (Marriage, Career Promotion, Childbirth, Property Acquisition)
manifests when both Saturn (the karmic sanctioner) and Jupiter (the divine grace)
simultaneously aspect or occupy the concerned house or its lord, supported by Dasa.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.double_transit import (
    DoubleTransitDomainConfig,
    DoubleTransitRequest,
    DoubleTransitResponse,
    DoubleTransitWindow,
    PlanetaryTransitSummary,
)
from app.services.kp_engine.constants import SIGN_LORDS
from app.services.kp_engine.dasha import current_periods
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.kp_engine.vedic import normalize_longitude, sign_name
from app.services.timezone_utils import resolve_birth_datetime


# Canonical 12 Signs
SIGN_NAMES_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS_BY_INDEX: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Domain Specifications
DOMAINS: Dict[str, DoubleTransitDomainConfig] = {
    "marriage": DoubleTransitDomainConfig(
        id="marriage",
        name_en="Marriage & Sacred Union",
        name_ta="திருமணம் மற்றும் வாழ்க்கைத்துணை",
        target_house=7,
        facilitating_houses=[2, 11],
        karakas=["Venus", "Jupiter"],
        description="Fructification of marriage requires Saturn and Jupiter to activate the 7th house (spouse/marriage) or 7th lord, supported by 2nd (family) and 11th (wishes).",
    ),
    "career": DoubleTransitDomainConfig(
        id="career",
        name_en="Career Milestone & Promotion",
        name_ta="தொழில் உயர்வு & உத்தியோக வெற்றி",
        target_house=10,
        facilitating_houses=[1, 2, 6, 11],
        karakas=["Sun", "Saturn", "Jupiter"],
        description="High professional honors, job changes, or promotions trigger when Saturn and Jupiter simultaneously illuminate the 10th house or 10th lord.",
    ),
    "childbirth": DoubleTransitDomainConfig(
        id="childbirth",
        name_en="Childbirth & Progeny Blessing",
        name_ta="குழந்தைப் பிறப்பு & சந்தான பாக்கியம்",
        target_house=5,
        facilitating_houses=[2, 11],
        karakas=["Jupiter"],
        description="Conception and childbirth occur when the 5th house (putra bhava) or 5th lord receives simultaneous sanction from Jupiter and Saturn.",
    ),
    "wealth": DoubleTransitDomainConfig(
        id="wealth",
        name_en="Wealth & Financial Windfall",
        name_ta="தன யோகம் & பெருஞ்செல்வம்",
        target_house=2,
        facilitating_houses=[11, 5, 9],
        karakas=["Jupiter", "Venus", "Mercury"],
        description="Massive wealth accumulation, liquid profits, or assets occur when Jupiter and Saturn aspect the 2nd (Dhāna) or 11th (Labha) houses.",
    ),
    "property": DoubleTransitDomainConfig(
        id="property",
        name_en="Property & Real Estate Acquisition",
        name_ta="சொத்து & நிலம் வாங்குதல்",
        target_house=4,
        facilitating_houses=[11, 12],
        karakas=["Mars", "Venus"],
        description="Buying a house, land, or luxury vehicle fructifies under the double transit influence over the 4th house (Sukha/Bhumi) or 4th lord.",
    ),
    "foreign": DoubleTransitDomainConfig(
        id="foreign",
        name_en="Foreign Travel & Relocation",
        name_ta="வெளிநாட்டுப் பயணம் & குடியேற்றம்",
        target_house=12,
        facilitating_houses=[9, 3],
        karakas=["Rahu", "Saturn"],
        description="Overseas travel, foreign settlement, or international visas manifest when Jupiter and Saturn simultaneously activate the 12th or 9th houses.",
    ),
    "health": DoubleTransitDomainConfig(
        id="health",
        name_en="Health Recovery & Vitality Revival",
        name_ta="ஆரோக்கிய மீட்சி & நோய் நிவாரணம்",
        target_house=1,
        facilitating_houses=[5, 9],
        karakas=["Sun", "Jupiter"],
        description="Overcoming chronic health conditions or undergoing successful medical interventions occurs when the 1st house (Ascendant) receives Jupiter's divine healing aspect with Saturn's stabilizing karmic sanction.",
    ),
}


def _saturn_aspects(sign_idx: int) -> Set[int]:
    """Signs (1-12) aspected or occupied by Saturn transiting in sign_idx (1-12).
    Occupies 1st, aspects 3rd, 7th, 10th (inclusive).
    """
    return {
        sign_idx,
        ((sign_idx - 1 + 2) % 12) + 1,  # 3rd house
        ((sign_idx - 1 + 6) % 12) + 1,  # 7th house
        ((sign_idx - 1 + 9) % 12) + 1,  # 10th house
    }


def _jupiter_aspects(sign_idx: int) -> Set[int]:
    """Signs (1-12) aspected or occupied by Jupiter transiting in sign_idx (1-12).
    Occupies 1st, aspects 5th, 7th, 9th (inclusive).
    """
    return {
        sign_idx,
        ((sign_idx - 1 + 4) % 12) + 1,  # 5th house
        ((sign_idx - 1 + 6) % 12) + 1,  # 7th house
        ((sign_idx - 1 + 8) % 12) + 1,  # 9th house
    }


def _rahu_aspects(sign_idx: int) -> Set[int]:
    """Signs (1-12) aspected or occupied by Rahu (5th, 7th, 9th aspects + occupation)."""
    return {
        sign_idx,
        ((sign_idx - 1 + 4) % 12) + 1,
        ((sign_idx - 1 + 6) % 12) + 1,
        ((sign_idx - 1 + 8) % 12) + 1,
    }


def _house_to_sign(lagna_sign_idx: int, house_num: int) -> int:
    """Calculates the zodiac sign index (1-12) of a house (1-12) from Lagna."""
    return ((lagna_sign_idx - 1 + (house_num - 1)) % 12) + 1


def _describe_saturn_aspect(sat_sign: int, target_sign: int) -> Tuple[bool, bool, str]:
    """Determines whether Saturn occupies or aspects target_sign, and returns detail."""
    diff = ((target_sign - sat_sign) % 12)
    if diff == 0:
        return True, True, "Occupation"
    elif diff == 2:
        return True, False, "3rd Special Aspect"
    elif diff == 6:
        return True, False, "7th Direct Aspect"
    elif diff == 9:
        return True, False, "10th Special Aspect"
    return False, False, "None"


def _describe_jupiter_aspect(jup_sign: int, target_sign: int) -> Tuple[bool, bool, str]:
    """Determines whether Jupiter occupies or aspects target_sign, and returns detail."""
    diff = ((target_sign - jup_sign) % 12)
    if diff == 0:
        return True, True, "Occupation"
    elif diff == 4:
        return True, False, "5th Trine Aspect (Guru Drishti)"
    elif diff == 6:
        return True, False, "7th Direct Aspect (Guru Drishti)"
    elif diff == 8:
        return True, False, "9th Trine Aspect (Guru Drishti)"
    return False, False, "None"


def calculate_double_transit_radar(request: DoubleTransitRequest) -> DoubleTransitResponse:
    """Computes Double Transit Event Timing Radar over a 1 to 5 year horizon."""
    domain_key = request.domain.lower() if request.domain else "marriage"
    domain_cfg = DOMAINS.get(domain_key, DOMAINS["marriage"])

    ayanamsa_str = "lahiri" if request.ayanamsa == 0 else "kp"
    eph = SwissEphemeris(ayanamsa=ayanamsa_str, node="true")

    # 1. Natal Chart baseline
    local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
        request.birth_date, request.birth_time, request.timezone
    )
    birth_ut = utc_dt.replace(tzinfo=None)

    natal_positions = eph.sidereal_positions(birth_jd)
    _cusps, natal_asc, _mc, _armc = eph.houses(
        birth_jd, request.latitude, request.longitude
    )

    natal_lagna_sign_idx = int((natal_asc % 360.0) // 30.0) + 1
    natal_lagna_sign_name = SIGN_NAMES_ORDER[natal_lagna_sign_idx - 1]

    # Target house sign & lord
    target_sign_idx = _house_to_sign(natal_lagna_sign_idx, domain_cfg.target_house)
    target_house_lord = SIGN_LORDS_BY_INDEX[target_sign_idx]

    # Natal position of the target house lord
    lord_natal_lon = natal_positions.get(target_house_lord, (0.0, 0.0))[0]
    lord_natal_sign_idx = int((lord_natal_lon % 360.0) // 30.0) + 1

    natal_moon_lon = natal_positions["Moon"][0]

    # 2. Scanning Horizon: 15-day time steps over forecast_years
    today = date.today()
    start_dt = datetime.combine(today, datetime.min.time())
    horizon_days = request.forecast_years * 365
    step_days = 15
    n_steps = horizon_days // step_days

    # Capture initial slow-moving transit positions for summary
    start_jd = eph.jd_ut(start_dt)
    init_transits = eph.sidereal_positions(start_jd)
    sat_init_lon = init_transits["Saturn"][0]
    jup_init_lon = init_transits["Jupiter"][0]
    rahu_init_lon = init_transits["Rahu"][0]

    current_transits_summary = PlanetaryTransitSummary(
        saturn_sign=SIGN_NAMES_ORDER[int(sat_init_lon // 30)],
        saturn_degree=round(sat_init_lon % 30.0, 2),
        jupiter_sign=SIGN_NAMES_ORDER[int(jup_init_lon // 30)],
        jupiter_degree=round(jup_init_lon % 30.0, 2),
        rahu_sign=SIGN_NAMES_ORDER[int(rahu_init_lon // 30)],
        rahu_degree=round(rahu_init_lon % 30.0, 2),
    )

    # Collect time slices
    raw_slices = []
    for step in range(n_steps + 1):
        cur_dt = start_dt + timedelta(days=step * step_days)
        cur_jd = eph.jd_ut(cur_dt)
        pos = eph.sidereal_positions(cur_jd)

        sat_lon = pos["Saturn"][0]
        jup_lon = pos["Jupiter"][0]
        rahu_lon = pos["Rahu"][0]

        sat_sign = int(sat_lon // 30.0) + 1
        jup_sign = int(jup_lon // 30.0) + 1
        rahu_sign = int(rahu_lon // 30.0) + 1

        sat_asp_house, sat_occ_house, sat_type_house = _describe_saturn_aspect(sat_sign, target_sign_idx)
        sat_asp_lord, sat_occ_lord, sat_type_lord = _describe_saturn_aspect(sat_sign, lord_natal_sign_idx)
        sat_active = sat_asp_house or sat_asp_lord
        sat_aspect_str = sat_type_house if sat_asp_house else (f"{sat_type_lord} on Lord" if sat_asp_lord else "None")

        jup_asp_house, jup_occ_house, jup_type_house = _describe_jupiter_aspect(jup_sign, target_sign_idx)
        jup_asp_lord, jup_occ_lord, jup_type_lord = _describe_jupiter_aspect(jup_sign, lord_natal_sign_idx)
        jup_active = jup_asp_house or jup_asp_lord
        jup_aspect_str = jup_type_house if jup_asp_house else (f"{jup_type_lord} on Lord" if jup_asp_lord else "None")

        double_transit = sat_active and jup_active

        # Rahu aspect
        rahu_active = (target_sign_idx in _rahu_aspects(rahu_sign)) or (lord_natal_sign_idx in _rahu_aspects(rahu_sign))

        # Dasa cross-check at this moment
        try:
            d_pers = current_periods(natal_moon_lon, birth_ut, cur_dt, depth=2)
            md_lord = d_pers[1].lord
            ad_lord = d_pers[2].lord
        except Exception:
            md_lord = "Unknown"
            ad_lord = "Unknown"

        # Check if Dasa lords rule target house or karakas
        dasa_hits = []
        if md_lord == target_house_lord:
            dasa_hits.append(f"MD Lord {md_lord} rules House {domain_cfg.target_house}")
        if ad_lord == target_house_lord:
            dasa_hits.append(f"AD Lord {ad_lord} rules House {domain_cfg.target_house}")
        if md_lord in domain_cfg.karakas:
            dasa_hits.append(f"MD Lord {md_lord} is natural Karaka")
        if ad_lord in domain_cfg.karakas:
            dasa_hits.append(f"AD Lord {ad_lord} is natural Karaka")

        dasa_confirms = len(dasa_hits) > 0
        dasa_detail = "; ".join(dasa_hits) if dasa_hits else f"Running {md_lord}-{ad_lord} (Neutral)"

        raw_slices.append({
            "date": cur_dt.date(),
            "sat_sign": sat_sign,
            "sat_aspect_str": sat_aspect_str,
            "sat_active": sat_active,
            "sat_occ": sat_occ_house,
            "jup_sign": jup_sign,
            "jup_aspect_str": jup_aspect_str,
            "jup_active": jup_active,
            "jup_occ": jup_occ_house,
            "double_transit": double_transit,
            "rahu_sign": rahu_sign,
            "rahu_active": rahu_active,
            "md_lord": md_lord,
            "ad_lord": ad_lord,
            "dasa_confirms": dasa_confirms,
            "dasa_detail": dasa_detail,
        })

    # 3. Merge adjacent slices into contiguous event windows
    windows: List[DoubleTransitWindow] = []
    if raw_slices:
        cur_win_start = raw_slices[0]["date"]
        cur_state = (
            raw_slices[0]["double_transit"],
            raw_slices[0]["sat_sign"],
            raw_slices[0]["jup_sign"],
            raw_slices[0]["md_lord"],
            raw_slices[0]["ad_lord"],
        )
        cur_slice_group = [raw_slices[0]]

        for sl in raw_slices[1:]:
            sl_state = (
                sl["double_transit"],
                sl["sat_sign"],
                sl["jup_sign"],
                sl["md_lord"],
                sl["ad_lord"],
            )
            # If alignment condition changed meaningfully or 4 months elapsed, split window
            if sl_state != cur_state:
                # Close current window
                cur_win_end = cur_slice_group[-1]["date"]
                rep = cur_slice_group[len(cur_slice_group) // 2]
                duration_m = round((cur_win_end - cur_win_start).days / 30.4, 1)

                # Determine scoring & status
                if rep["double_transit"] and rep["dasa_confirms"]:
                    lvl = "Peak Alignment (Guru-Shani + Dasa)"
                    prob = 92
                elif rep["double_transit"]:
                    lvl = "High (Double Transit Active)"
                    prob = 78
                elif rep["dasa_confirms"] and (rep["sat_active"] or rep["jup_active"]):
                    lvl = "Moderate Opportunity (Single Transit + Dasa)"
                    prob = 62
                else:
                    lvl = "Dormant Window"
                    prob = 35

                sat_s_name = SIGN_NAMES_ORDER[rep["sat_sign"] - 1]
                jup_s_name = SIGN_NAMES_ORDER[rep["jup_sign"] - 1]
                rahu_s_name = SIGN_NAMES_ORDER[rep["rahu_sign"] - 1]

                rationale_en = (
                    f"Saturn in {sat_s_name} ({rep['sat_aspect_str']}) and Jupiter in {jup_s_name} "
                    f"({rep['jup_aspect_str']}) target House {domain_cfg.target_house} ({domain_cfg.name_en}). "
                    f"Vimshottari Dasha running: {rep['md_lord']}-{rep['ad_lord']}."
                )
                rationale_ta = (
                    f"சனி பகவான் {sat_s_name} ராசியிலும் ({rep['sat_aspect_str']}), குரு பகவான் {jup_s_name} "
                    f"ராசியிலும் ({rep['jup_aspect_str']}) நின்று {domain_cfg.target_house}-ம் வீட்டைப் பார்க்கின்றனர். "
                    f"நடப்பு திசா-புக்தி: {rep['md_lord']}-{rep['ad_lord']}."
                )

                windows.append(
                    DoubleTransitWindow(
                        start_date=str(cur_win_start),
                        end_date=str(cur_win_end),
                        duration_months=max(0.5, duration_m),
                        saturn_transit_sign=sat_s_name,
                        saturn_transit_sign_index=rep["sat_sign"],
                        saturn_aspects_target=rep["sat_active"],
                        saturn_occupies_target=rep["sat_occ"],
                        saturn_aspect_type=rep["sat_aspect_str"],
                        jupiter_transit_sign=jup_s_name,
                        jupiter_transit_sign_index=rep["jup_sign"],
                        jupiter_aspects_target=rep["jup_active"],
                        jupiter_occupies_target=rep["jup_occ"],
                        jupiter_aspect_type=rep["jup_aspect_str"],
                        double_transit_active=rep["double_transit"],
                        rahu_transit_sign=rahu_s_name,
                        rahu_transit_sign_index=rep["rahu_sign"],
                        rahu_activates_target=rep["rahu_active"],
                        running_mahadasha=rep["md_lord"],
                        running_antardasha=rep["ad_lord"],
                        dasa_confirms_event=rep["dasa_confirms"],
                        dasa_connection_details=rep["dasa_detail"],
                        alignment_level=lvl,
                        probability_percentage=prob,
                        astrological_rationale=rationale_en,
                        astrological_rationale_ta=rationale_ta,
                    )
                )

                # Reset
                cur_win_start = sl["date"]
                cur_state = sl_state
                cur_slice_group = [sl]
            else:
                cur_slice_group.append(sl)

        # Append trailing window
        if cur_slice_group:
            cur_win_end = cur_slice_group[-1]["date"]
            rep = cur_slice_group[len(cur_slice_group) // 2]
            duration_m = round((cur_win_end - cur_win_start).days / 30.4, 1)
            if rep["double_transit"] and rep["dasa_confirms"]:
                lvl = "Peak Alignment (Guru-Shani + Dasa)"
                prob = 92
            elif rep["double_transit"]:
                lvl = "High (Double Transit Active)"
                prob = 78
            elif rep["dasa_confirms"] and (rep["sat_active"] or rep["jup_active"]):
                lvl = "Moderate Opportunity (Single Transit + Dasa)"
                prob = 62
            else:
                lvl = "Dormant Window"
                prob = 35

            sat_s_name = SIGN_NAMES_ORDER[rep["sat_sign"] - 1]
            jup_s_name = SIGN_NAMES_ORDER[rep["jup_sign"] - 1]
            rahu_s_name = SIGN_NAMES_ORDER[rep["rahu_sign"] - 1]

            windows.append(
                DoubleTransitWindow(
                    start_date=str(cur_win_start),
                    end_date=str(cur_win_end),
                    duration_months=max(0.5, duration_m),
                    saturn_transit_sign=sat_s_name,
                    saturn_transit_sign_index=rep["sat_sign"],
                    saturn_aspects_target=rep["sat_active"],
                    saturn_occupies_target=rep["sat_occ"],
                    saturn_aspect_type=rep["sat_aspect_str"],
                    jupiter_transit_sign=jup_s_name,
                    jupiter_transit_sign_index=rep["jup_sign"],
                    jupiter_aspects_target=rep["jup_active"],
                    jupiter_occupies_target=rep["jup_occ"],
                    jupiter_aspect_type=rep["jup_aspect_str"],
                    double_transit_active=rep["double_transit"],
                    rahu_transit_sign=rahu_s_name,
                    rahu_transit_sign_index=rep["rahu_sign"],
                    rahu_activates_target=rep["rahu_active"],
                    running_mahadasha=rep["md_lord"],
                    running_antardasha=rep["ad_lord"],
                    dasa_confirms_event=rep["dasa_confirms"],
                    dasa_connection_details=rep["dasa_detail"],
                    alignment_level=lvl,
                    probability_percentage=prob,
                    astrological_rationale=(
                        f"Saturn in {sat_s_name} ({rep['sat_aspect_str']}) and Jupiter in {jup_s_name} "
                        f"({rep['jup_aspect_str']}) target House {domain_cfg.target_house} ({domain_cfg.name_en}). "
                        f"Vimshottari Dasha running: {rep['md_lord']}-{rep['ad_lord']}."
                    ),
                    astrological_rationale_ta=(
                        f"சனி பகவான் {sat_s_name} ராசியிலும் ({rep['sat_aspect_str']}), குரு பகவான் {jup_s_name} "
                        f"ராசியிலும் ({rep['jup_aspect_str']}) நின்று {domain_cfg.target_house}-ம் வீட்டைப் பார்க்கின்றனர். "
                        f"நடப்பு திசா-புக்தி: {rep['md_lord']}-{rep['ad_lord']}."
                    ),
                )
            )

    # Filter Peak Windows (probability >= 75%)
    peak_windows = [w for w in windows if w.probability_percentage >= 75]

    if peak_windows:
        best_win = peak_windows[0]
        summary_en = (
            f"Double Transit confirms fruition for {domain_cfg.name_en}! "
            f"The primary favorable window opens between {best_win.start_date} and {best_win.end_date} "
            f"({best_win.duration_months} months), with Jupiter in {best_win.jupiter_transit_sign} and "
            f"Saturn in {best_win.saturn_transit_sign} jointly sanctifying House {domain_cfg.target_house}."
        )
        summary_ta = (
            f"குரு-சனி இரட்டை கோச்சார ஆய்வுப்படி {domain_cfg.name_ta} கைகூடும் காலம் உறுதியாகியுள்ளது! "
            f"முக்கிய சுப காலம்: {best_win.start_date} முதல் {best_win.end_date} வரை "
            f"({best_win.duration_months} மாதங்கள்). குரு {best_win.jupiter_transit_sign} மற்றும் "
            f"சனி {best_win.saturn_transit_sign} இணைந்து {domain_cfg.target_house}-ம் வீட்டை ஆசிர்வதிக்கின்றனர்."
        )
    else:
        summary_en = (
            f"No intense double-transit confluence occurs immediately for {domain_cfg.name_en} within this horizon. "
            f"Moderate windows are highlighted below where supportive Mahadashas bridge the planetary transits."
        )
        summary_ta = (
            f"இந்த காலவரம்பில் {domain_cfg.name_ta}க்கான தீவிர இரட்டை கோச்சார சேர்க்கை உடனடியாக இல்லை. "
            f"ஆயினும் திசா பலன் சாதகமாக உள்ள மிதமான காலங்கள் கீழே சுட்டிக்காட்டப்பட்டுள்ளன."
        )

    end_date = start_dt + timedelta(days=horizon_days)

    return DoubleTransitResponse(
        domain=domain_cfg,
        target_house=domain_cfg.target_house,
        target_house_lord=target_house_lord,
        natal_lagna_sign=natal_lagna_sign_name,
        natal_lagna_sign_index=natal_lagna_sign_idx,
        analysis_start_date=str(today),
        analysis_end_date=str(end_date.date()),
        current_transits=current_transits_summary,
        windows=windows,
        peak_windows=peak_windows,
        summary_verdict=summary_en,
        summary_verdict_ta=summary_ta,
    )
