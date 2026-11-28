"""KP Marriage Promise, Timing & Date Refinement Engine.

Implements the 4-stage KP Marriage Date methodology:
1. Marriage Promise Assessment Engine (100-point scale: 7th House 40, Venus 40, Lagna 15, 9th House 5)
2. Dasha-Bhukti-Antara Timing Engine (25-point scale: Dasha 10, Bhukti 10, Antara 5)
3. 7th Cusp Analysis Engine (Degree, Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord & Target Stars)
4. Marriage Date Refinement Engine (Muhurta Panchangam + 7th Cusp Star/Sub/Sub-Sub alignment)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

from app.schemas.common import BirthInput
from app.schemas.kp_timing import (
    KpMarriageCandidateDate,
    KpMarriageCuspAnalysis,
    KpMarriageDashaWindow,
    KpMarriageDateRequest,
    KpMarriageDateResponse,
    KpMarriagePromiseBreakdown,
    KpMarriagePromiseFactor,
    KpMarriageTargetLord,
)
from app.services.kp_engine.chart import BirthInfo, Chart, compute_chart
from app.services.kp_engine.constants import NAKSHATRAS, VIMSHOTTARI_ORDER
from app.services.kp_engine.dasha import (
    Period,
    antardashas_of,
    mahadasha_timeline,
    pratyantardashas_of,
)
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.kp_engine.vedic import format_longitude
from app.services.kp_timing_service import PLANET_NAMES_TA, SIGN_NAMES_TA, STAR_NAMES_TA
from app.services.muhurta_engine.astronomy import calculate_daily_panchangam
from app.services.timezone_utils import resolve_birth_datetime

SUPPORTING_HOUSES: Set[int] = {2, 7, 11}
MILD_SUPPORT_HOUSES: Set[int] = {5}
OBSTACLE_HOUSES: Set[int] = {6, 8, 12}
DENIAL_HOUSES: Set[int] = {1, 6, 10}

# Nakshatra lord mapping (1-indexed 1..27 -> Vimshottari lord)
NAKSHATRA_LORD_MAP: Dict[str, str] = {
    name: VIMSHOTTARI_ORDER[idx % 9] for idx, name in enumerate(NAKSHATRAS)
}

STARS_BY_LORD: Dict[str, List[str]] = {lord: [] for lord in VIMSHOTTARI_ORDER}
for _idx, _star in enumerate(NAKSHATRAS):
    STARS_BY_LORD[VIMSHOTTARI_ORDER[_idx % 9]].append(_star)

# Auspicious Tithis for Vivaha (avoiding Pratipada 1/16, Chaturthi 4/19, Ashtami 8/23, Navami 9/24, Chaturdashi 14/29, Amavasya 30)
AUSPICIOUS_TITHIS: Set[int] = {2, 3, 5, 7, 10, 11, 12, 13, 17, 18, 20, 22, 25, 26, 27, 28}
AVOID_TITHIS: Set[int] = {1, 4, 8, 9, 14, 16, 19, 23, 24, 29, 30}
# Avoid Tuesday (2) and Saturday (6) (weekday_number is 1=Mon .. 7=Sun)
AVOID_WEEKDAYS: Set[int] = {2, 6}

DISCLAIMER_EN = (
    "KP marriage timing combines natal promise heuristics (40/40/15/5), Vimshottari Dasha-Bhukti-Antara "
    "significations, 7th cusp Star/Sub/Sub-Sub lords, and Panchangam Muhurta rules. These represent "
    "astrological propensities rather than a scientific or guaranteed prediction of an exact wedding date."
)
DISCLAIMER_TA = (
    "KP திருமண கால கணிப்பு என்பது பிறப்பு கொடுப்பினை (40/40/15/5), தசா-புத்தி-அந்தரம், 7ஆம் பாவ முனை "
    "நட்சத்திர-உபநட்சத்திர அதிபதிகள் மற்றும் முகூர்த்த பஞ்சாங்க விதிகளின் அடிப்படையிலான ஜோதிட வழிகாட்டுதலே; "
    "இது 100% உறுதியான தேதி உத்தரவாதம் அல்ல."
)


def _planet_houses(chart: Chart, planet: str) -> Set[int]:
    return {s.house for s in chart.planet_significators.get(planet, [])}


def _score_lord_for_marriage(
    chart: Chart,
    planet: str,
    max_score: float,
    extra_support: Optional[Set[int]] = None,
) -> Tuple[float, List[int], List[int]]:
    """Score a planet's marriage support (0..max_score) from its signified houses."""
    houses = _planet_houses(chart, planet)
    support_set = SUPPORTING_HOUSES | (extra_support or set())
    pos_hits = sorted(houses & support_set)
    neg_hits = sorted(houses & OBSTACLE_HOUSES)

    # Base proportion from supporting hits (2, 7, 11 carry strongest weight)
    core_hits = len(houses & SUPPORTING_HOUSES)
    mild_hits = len(houses & MILD_SUPPORT_HOUSES)

    if core_hits >= 3:
        ratio = 1.0
    elif core_hits == 2:
        ratio = 0.85
    elif core_hits == 1:
        ratio = 0.62
    elif mild_hits > 0:
        ratio = 0.40
    elif houses & (extra_support or set()):
        ratio = 0.35
    else:
        ratio = 0.15

    # Penalty for 6, 8, 12 obstacle significations
    neg_count = len(neg_hits)
    if neg_count == 1:
        ratio -= 0.15
    elif neg_count == 2:
        ratio -= 0.30
    elif neg_count >= 3:
        ratio -= 0.45

    ratio = max(0.05, min(1.0, ratio))
    return round(ratio * max_score, 1), pos_hits, neg_hits


def assess_marriage_promise(chart: Chart) -> KpMarriagePromiseBreakdown:
    """Engine A: 100-point Marriage Promise Assessment (40 + 40 + 15 + 5)."""
    cusp_7 = chart.cusps[6]
    cusp_1 = chart.cusps[0]
    cusp_9 = chart.cusps[8]
    venus = next((p for p in chart.planets if p.name == "Venus"), None)

    # 1. 7th House Signification (40 pts): Sub-Lord (25) + Star-Lord (10) + Sub-Sub-Lord (5)
    s7_sub, p7_sub, n7_sub = _score_lord_for_marriage(chart, cusp_7.sub_lord, 25.0)
    s7_star, p7_star, n7_star = _score_lord_for_marriage(chart, cusp_7.star_lord, 10.0)
    s7_subsub, p7_ss, n7_ss = _score_lord_for_marriage(chart, cusp_7.sub_sub_lord, 5.0)
    score_7th = round(min(40.0, s7_sub + s7_star + s7_subsub), 1)
    pos_7 = sorted(set(p7_sub + p7_star + p7_ss))
    neg_7 = sorted(set(n7_sub + n7_star + n7_ss))

    # 2. Venus Signification (40 pts): Venus itself (20) + Venus Sub-Lord (15) + Venus Star-Lord (5)
    if venus:
        sv_self, pv_self, nv_self = _score_lord_for_marriage(chart, "Venus", 20.0)
        sv_sub, pv_sub, nv_sub = _score_lord_for_marriage(chart, venus.sub_lord, 15.0)
        sv_star, pv_star, nv_star = _score_lord_for_marriage(chart, venus.star_lord, 5.0)
        score_venus = round(min(40.0, sv_self + sv_sub + sv_star), 1)
        pos_v = sorted(set(pv_self + pv_sub + pv_star))
        neg_v = sorted(set(nv_self + nv_sub + nv_star))
        venus_note_en = f"Venus in house {venus.house} (Star: {venus.star_lord}, Sub: {venus.sub_lord})"
        venus_note_ta = (
            f"சுக்கிரன் {venus.house}ஆம் பாவத்தில் "
            f"(நட்சத்திரம்: {PLANET_NAMES_TA.get(venus.star_lord, venus.star_lord)}, "
            f"உபநட்சத்திரம்: {PLANET_NAMES_TA.get(venus.sub_lord, venus.sub_lord)})"
        )
    else:
        score_venus = 20.0
        pos_v, neg_v = [], []
        venus_note_en = "Venus position unavailable"
        venus_note_ta = "சுக்கிரன் நிலை கிடைக்கவில்லை"

    # 3. Lagna Promise (15 pts): 1st Cusp Sub-Lord
    score_lagna, pos_1, neg_1 = _score_lord_for_marriage(
        chart, cusp_1.sub_lord, 15.0, extra_support={1}
    )

    # 4. 9th House Promise / Divine Grace (5 pts): 9th Cusp Sub-Lord
    score_9th, pos_9, neg_9 = _score_lord_for_marriage(
        chart, cusp_9.sub_lord, 5.0, extra_support={9}
    )

    total = round(min(100.0, score_7th + score_venus + score_lagna + score_9th), 1)

    if total >= 70.0:
        verdict = "Strong"
        verdict_ta = "வலுவான கொடுப்பினை"
        confidence = "High"
        confidence_ta = "உயர் நம்பகத்தன்மை"
        summary_en = (
            "Strong natal marriage promise (2, 7, 11 support is well-aligned). "
            "Favorable Dasha-Bhukti-Antara periods and 7th cusp star transits can fructify marriage promptly."
        )
        summary_ta = (
            "திருமணக் கொடுப்பினை வலுவாக உள்ளது (2, 7, 11 பாவத் தொடர்புகள் சாதகம்). "
            "சாதகமான தசா-புத்தி-அந்தரம் மற்றும் 7ஆம் பாவ நட்சத்திர நாட்களில் திருமணம் விரைவில் கைகூடும்."
        )
    elif total >= 45.0:
        verdict = "Moderate"
        verdict_ta = "மிதமான கொடுப்பினை"
        confidence = "Moderate"
        confidence_ta = "மிதமான நம்பகத்தன்மை"
        summary_en = (
            "Moderate marriage promise with mixed supporting (2, 7, 11) and obstacle (6, 8, 12) links. "
            "Marriage is supported during strong Dasha-Bhukti-Antara windows, though timing may require patience."
        )
        summary_ta = (
            "திருமணக் கொடுப்பினை மிதமாக உள்ளது (சாதக பாவங்களுடன் 6, 8, 12 தொடர்புகளும் கலந்திருக்கின்றன). "
            "வலுவான தசா-புத்தி-அந்தர காலங்களில் திருமணம் நடைபெறும்."
        )
    else:
        verdict = "Weak / Delayed"
        verdict_ta = "பலவீனமான / தாமதக் கொடுப்பினை"
        confidence = "Low"
        confidence_ta = "குறைந்த நம்பகத்தன்மை (காலம் தள்ளிப்போகலாம்)"
        summary_en = (
            "Natal marriage promise shows notable 6, 8, 12 obstructions or weak 2, 7, 11 linkage. "
            "Per KP principles, an exact single date cannot be guaranteed; focus on broader favorable Bhukti/Antara windows."
        )
        summary_ta = (
            "7ஆம் பாவம் மற்றும் சுக்கிரனில் 6, 8, 12 தொடர்புகள் அதிகம் உள்ளதால் கொடுப்பினை பலவீனமாக உள்ளது. "
            "எனவே ஒரே ஒரு குறிப்பிட்ட தேதியை உறுதியாகக் கூறாமல், சாதகமான புத்தி-அந்தர காலங்களைக் கவனிக்க வேண்டும்."
        )

    factors = [
        KpMarriagePromiseFactor(
            factor_key="seventh_house",
            title_en="7th House Signification (Bhava Karaka)",
            title_ta="7ஆம் பாவக் காரகம் (திருமண பாவம்)",
            score=score_7th,
            max_score=40.0,
            lord=cusp_7.sub_lord,
            lord_ta=PLANET_NAMES_TA.get(cusp_7.sub_lord, cusp_7.sub_lord),
            supporting_houses=pos_7,
            obstacle_houses=neg_7,
            detail_en=f"7th Cusp Sub-Lord: {cusp_7.sub_lord} (Star: {cusp_7.star_lord}, Sub-Sub: {cusp_7.sub_sub_lord})",
            detail_ta=(
                f"7ஆம் பாவ உபநட்சத்திர அதிபதி: {PLANET_NAMES_TA.get(cusp_7.sub_lord, cusp_7.sub_lord)} "
                f"(நட்சத்திரம்: {PLANET_NAMES_TA.get(cusp_7.star_lord, cusp_7.star_lord)})"
            ),
        ),
        KpMarriagePromiseFactor(
            factor_key="venus",
            title_en="Venus Signification (Kalathra Karaka)",
            title_ta="சுக்கிரன் (கிரகக் காரகம்)",
            score=score_venus,
            max_score=40.0,
            lord="Venus",
            lord_ta=PLANET_NAMES_TA["Venus"],
            supporting_houses=pos_v,
            obstacle_houses=neg_v,
            detail_en=venus_note_en,
            detail_ta=venus_note_ta,
        ),
        KpMarriagePromiseFactor(
            factor_key="lagna",
            title_en="Lagna Promise (General Support)",
            title_ta="லக்னக் கொடுப்பினை",
            score=score_lagna,
            max_score=15.0,
            lord=cusp_1.sub_lord,
            lord_ta=PLANET_NAMES_TA.get(cusp_1.sub_lord, cusp_1.sub_lord),
            supporting_houses=pos_1,
            obstacle_houses=neg_1,
            detail_en=f"1st Cusp Sub-Lord: {cusp_1.sub_lord}",
            detail_ta=f"லக்ன உபநட்சத்திர அதிபதி: {PLANET_NAMES_TA.get(cusp_1.sub_lord, cusp_1.sub_lord)}",
        ),
        KpMarriagePromiseFactor(
            factor_key="ninth_house",
            title_en="9th House (Bhagya / Divine Grace)",
            title_ta="9ஆம் பாவம் (தெய்வ அனுக்கிரகம்)",
            score=score_9th,
            max_score=5.0,
            lord=cusp_9.sub_lord,
            lord_ta=PLANET_NAMES_TA.get(cusp_9.sub_lord, cusp_9.sub_lord),
            supporting_houses=pos_9,
            obstacle_houses=neg_9,
            detail_en=f"9th Cusp Sub-Lord: {cusp_9.sub_lord}",
            detail_ta=f"9ஆம் பாவ உபநட்சத்திர அதிபதி: {PLANET_NAMES_TA.get(cusp_9.sub_lord, cusp_9.sub_lord)}",
        ),
    ]

    return KpMarriagePromiseBreakdown(
        total_score=total,
        verdict=verdict,
        verdict_ta=verdict_ta,
        confidence=confidence,
        confidence_ta=confidence_ta,
        summary_en=summary_en,
        summary_ta=summary_ta,
        factors=factors,
    )


def analyze_seventh_cusp(chart: Chart) -> KpMarriageCuspAnalysis:
    """Engine C: 7th Cusp Degree, Star, Sub, Sub-Sub Lords & Target Nakshatras."""
    cusp_7 = chart.cusps[6]
    deg_in_sign = cusp_7.longitude % 30.0
    deg_str = format_longitude(deg_in_sign, arcsec=False)

    # Priority order per Section 11: Sub Lord (1), Star Lord (2), Sub-Sub Lord (3)
    target_entries: List[Tuple[int, str, str, str]] = [
        (1, "Sub Lord (7th Cusp)", "7ஆம் பாவ உபநட்சத்திர அதிபதி", cusp_7.sub_lord),
        (2, "Star Lord (7th Cusp)", "7ஆம் பாவ நட்சத்திர அதிபதி", cusp_7.star_lord),
        (3, "Sub-Sub Lord (7th Cusp)", "7ஆம் பாவ உப-உபநட்சத்திர அதிபதி", cusp_7.sub_sub_lord),
    ]

    target_lords: List[KpMarriageTargetLord] = []
    seen_lords: Set[str] = set()
    for priority, role_en, role_ta, lord in target_entries:
        stars_en = STARS_BY_LORD.get(lord, [])
        stars_ta = [STAR_NAMES_TA.get(s, s) for s in stars_en]
        target_lords.append(
            KpMarriageTargetLord(
                priority=priority,
                role_en=role_en,
                role_ta=role_ta,
                planet=lord,
                planet_ta=PLANET_NAMES_TA.get(lord, lord),
                stars_en=stars_en,
                stars_ta=stars_ta,
                is_duplicate_role=lord in seen_lords,
            )
        )
        seen_lords.add(lord)

    return KpMarriageCuspAnalysis(
        sign=cusp_7.sign,
        sign_ta=SIGN_NAMES_TA.get(cusp_7.sign, cusp_7.sign),
        degree_dms=deg_str,
        longitude=round(cusp_7.longitude, 4),
        sign_lord=cusp_7.sign_lord,
        sign_lord_ta=PLANET_NAMES_TA.get(cusp_7.sign_lord, cusp_7.sign_lord),
        star=cusp_7.star,
        star_ta=STAR_NAMES_TA.get(cusp_7.star, cusp_7.star),
        star_lord=cusp_7.star_lord,
        star_lord_ta=PLANET_NAMES_TA.get(cusp_7.star_lord, cusp_7.star_lord),
        sub_lord=cusp_7.sub_lord,
        sub_lord_ta=PLANET_NAMES_TA.get(cusp_7.sub_lord, cusp_7.sub_lord),
        sub_sub_lord=cusp_7.sub_sub_lord,
        sub_sub_lord_ta=PLANET_NAMES_TA.get(cusp_7.sub_sub_lord, cusp_7.sub_sub_lord),
        target_lords=target_lords,
    )


def find_favorable_dasha_windows(
    chart: Chart,
    birth_local_dt: datetime,
    search_start: date,
    search_end: date,
    top_n: int = 8,
) -> List[KpMarriageDashaWindow]:
    """Engine B: Score Dasha (10) + Bhukti (10) + Antara (5) = 25 points over search range."""
    moon_pos = next(p for p in chart.planets if p.name == "Moon")
    maha_list = mahadasha_timeline(moon_pos.longitude, epochs=1)
    bal = chart.balance
    today = date.today()

    start_dt = datetime.combine(search_start, datetime.min.time())
    end_dt = datetime.combine(search_end, datetime.max.time())

    windows: List[KpMarriageDashaWindow] = []

    for md_idx, md in enumerate(maha_list):
        md_start, md_end = md.as_datetimes(birth_local_dt)
        if md_end < start_dt or md_start > end_dt:
            continue

        md_is_partial = (md_idx == 0)
        ad_list = antardashas_of(md, balance=bal if md_is_partial else None)
        d_score, d_pos, d_neg = _score_lord_for_marriage(chart, md.lord, 10.0)

        for ad_idx, ad in enumerate(ad_list):
            ad_abs = Period(ad.lord, md.start_days + ad.start_days, md.start_days + ad.end_days, 2)
            ad_start, ad_end = ad_abs.as_datetimes(birth_local_dt)
            if ad_end < start_dt or ad_start > end_dt:
                continue

            ad_is_partial = md_is_partial and (ad_idx == 0)
            pd_list = pratyantardashas_of(ad, balance=bal if md_is_partial else None, md_is_partial=md_is_partial)
            b_score, b_pos, b_neg = _score_lord_for_marriage(chart, ad.lord, 10.0)

            for pd in pd_list:
                pd_abs = Period(pd.lord, ad_abs.start_days + pd.start_days, ad_abs.start_days + pd.end_days, 3)
                pd_start, pd_end = pd_abs.as_datetimes(birth_local_dt)
                if pd_end < start_dt or pd_start > end_dt:
                    continue

                # Venus Antara gets a slight Kalathra Karaka boost per Section 6
                a_score, a_pos, a_neg = _score_lord_for_marriage(chart, pd.lord, 5.0)
                if pd.lord == "Venus" and a_score < 4.5:
                    a_score = min(5.0, round(a_score + 0.8, 1))

                total_25 = round(d_score + b_score + a_score, 1)
                all_pos = sorted(set(d_pos + b_pos + a_pos))
                all_neg = sorted(set(d_neg + b_neg + a_neg))

                clipped_start = max(pd_start.date(), search_start)
                clipped_end = min(pd_end.date(), search_end)
                is_current = pd_start.date() <= today <= pd_end.date()

                if total_25 >= 17.5:
                    rating, rating_ta = "Highly Favorable", "மிகச் சாதகமான காலம்"
                elif total_25 >= 13.0:
                    rating, rating_ta = "Favorable", "சாதகமான காலம்"
                else:
                    rating, rating_ta = "Moderate", "மிதமான காலம்"

                windows.append(
                    KpMarriageDashaWindow(
                        dasha_lord=md.lord,
                        dasha_lord_ta=PLANET_NAMES_TA.get(md.lord, md.lord),
                        bhukti_lord=ad.lord,
                        bhukti_lord_ta=PLANET_NAMES_TA.get(ad.lord, ad.lord),
                        antara_lord=pd.lord,
                        antara_lord_ta=PLANET_NAMES_TA.get(pd.lord, pd.lord),
                        start_date=clipped_start.isoformat(),
                        end_date=clipped_end.isoformat(),
                        dasha_score=d_score,
                        bhukti_score=b_score,
                        antara_score=a_score,
                        total_score=total_25,
                        rating=rating,
                        rating_ta=rating_ta,
                        supporting_houses=all_pos,
                        obstacle_houses=all_neg,
                        is_current=is_current,
                    )
                )

    windows.sort(key=lambda w: (w.total_score, w.is_current), reverse=True)
    return windows[:top_n]


def _fmt_utc_window(period: Dict[str, Any], tz: ZoneInfo) -> str:
    """Format a panchangam {start_utc, end_utc} dict into local HH:MM - HH:MM."""
    s_raw = period.get("start_utc") or period.get("start_local")
    e_raw = period.get("end_utc") or period.get("end_local")
    if not s_raw or not e_raw:
        return "—"
    try:
        s_dt = datetime.fromisoformat(s_raw).astimezone(tz)
        e_dt = datetime.fromisoformat(e_raw).astimezone(tz)
        return f"{s_dt.strftime('%H:%M')} - {e_dt.strftime('%H:%M')}"
    except Exception:
        return f"{s_raw} - {e_raw}"


def refine_marriage_dates(
    cusp_analysis: KpMarriageCuspAnalysis,
    top_windows: List[KpMarriageDashaWindow],
    latitude: float,
    longitude: float,
    timezone_str: str,
    ayanamsa_id: int,
    max_scan_days: int = 75,
    max_results: int = 15,
) -> List[KpMarriageCandidateDate]:
    """Engine D: Scan top Antara windows with Panchangam Muhurta + 7th Cusp Star/Sub/Sub-Sub alignment."""
    if not top_windows:
        return []

    sub_lord = cusp_analysis.sub_lord
    star_lord = cusp_analysis.star_lord
    sub_sub_lord = cusp_analysis.sub_sub_lord

    candidates: List[KpMarriageCandidateDate] = []
    seen_dates: Set[str] = set()
    scanned_days = 0

    for win in top_windows[:4]:
        if scanned_days >= max_scan_days:
            break
        w_start = date.fromisoformat(win.start_date)
        w_end = date.fromisoformat(win.end_date)
        cur = w_start
        while cur <= w_end and scanned_days < max_scan_days:
            d_iso = cur.isoformat()
            # Fast pre-filter: skip Tuesday (1) and Saturday (5) before running Panchangam ephemeris
            if d_iso in seen_dates or cur.weekday() in (1, 5):
                cur += timedelta(days=1)
                continue
            seen_dates.add(d_iso)
            scanned_days += 1

            panchang = calculate_daily_panchangam(
                event_date=cur,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                ayanamsa_id=ayanamsa_id,
            )

            weekday_num = panchang["vara"]["weekday_number"]
            tithi_num = panchang["tithi"]["number"]
            paksha = panchang["tithi"]["paksha"]
            nak_name = panchang["nakshatra"]["name"]
            nak_name_ta = panchang["nakshatra"]["name_ta"]
            nak_lord = panchang["nakshatra"]["lord"]

            # Hard cultural Muhurta filters from Section 7 Step 4:
            # Avoid Tuesday/Saturday and Ashtami/Navami/Pratipada/Rikta/Amavasya
            if weekday_num in AVOID_WEEKDAYS:
                cur += timedelta(days=1)
                continue
            if tithi_num in AVOID_TITHIS:
                cur += timedelta(days=1)
                continue

            # Match against 7th Cusp priority lords (Sub -> Star -> Sub-Sub -> Venus)
            match_reasons_en: List[str] = []
            match_reasons_ta: List[str] = []
            kp_star_score = 0.0

            if nak_lord == sub_lord:
                kp_star_score += 45.0
                match_reasons_en.append(f"Nakshatra ruled by 7th Cusp Sub-Lord ({sub_lord})")
                match_reasons_ta.append(
                    f"7ஆம் பாவ உபநட்சத்திர அதிபதி ({PLANET_NAMES_TA.get(sub_lord, sub_lord)}) நட்சத்திரம்"
                )
            elif nak_lord == star_lord:
                kp_star_score += 35.0
                match_reasons_en.append(f"Nakshatra ruled by 7th Cusp Star-Lord ({star_lord})")
                match_reasons_ta.append(
                    f"7ஆம் பாவ நட்சத்திர அதிபதி ({PLANET_NAMES_TA.get(star_lord, star_lord)}) நட்சத்திரம்"
                )
            elif nak_lord == sub_sub_lord:
                kp_star_score += 28.0
                match_reasons_en.append(f"Nakshatra ruled by 7th Cusp Sub-Sub-Lord ({sub_sub_lord})")
                match_reasons_ta.append(
                    f"7ஆம் பாவ உப-உபநட்சத்திர அதிபதி ({PLANET_NAMES_TA.get(sub_sub_lord, sub_sub_lord)}) நட்சத்திரம்"
                )
            elif nak_lord == "Venus":
                kp_star_score += 20.0
                match_reasons_en.append("Nakshatra ruled by Kalathra Karaka Venus")
                match_reasons_ta.append("களத்திர காரகன் சுக்கிரன் நட்சத்திரம்")

            # Require either a KP 7th-cusp/Venus star match OR an auspicious Shukla Paksha Muhurta
            muhurta_score = 0.0
            if paksha == "Shukla":
                muhurta_score += 20.0
                match_reasons_en.append("Shukla Paksha (Waxing Moon)")
                match_reasons_ta.append("வளர்பிறை சுப தினம்")
            else:
                muhurta_score += 6.0

            if tithi_num in AUSPICIOUS_TITHIS:
                muhurta_score += 15.0

            # Dasha window contribution (0..20)
            dasha_contrib = round((win.total_score / 25.0) * 20.0, 1)
            total_date_score = round(min(100.0, kp_star_score + muhurta_score + dasha_contrib), 1)

            if kp_star_score == 0.0 and paksha != "Shukla":
                cur += timedelta(days=1)
                continue

            if kp_star_score >= 40.0 and paksha == "Shukla":
                tier, tier_ta = "Prime KP + Muhurta Match", "மிகச் சிறந்த KP + முகூர்த்த தினம்"
            elif kp_star_score >= 28.0:
                tier, tier_ta = "7th Cusp Star Match", "7ஆம் பாவ முனை நட்சத்திரப் பொருத்தம்"
            else:
                tier, tier_ta = "Auspicious Muhurta Day", "சுப முகூர்த்த தினம்"

            abhijit = panchang["auspicious_periods"]["abhijit"]
            rahu = panchang["inauspicious_periods"]["rahu_kalam"]
            tz_obj = ZoneInfo(timezone_str)

            candidates.append(
                KpMarriageCandidateDate(
                    date=d_iso,
                    weekday_en=panchang["vara"]["name_en"],
                    weekday_ta=panchang["vara"]["name_ta"],
                    paksha=paksha,
                    paksha_ta="வளர்பிறை" if paksha == "Shukla" else "தேய்பிறை",
                    tithi_en=panchang["tithi"]["name"],
                    tithi_ta=panchang["tithi"]["name_ta"],
                    nakshatra_en=nak_name,
                    nakshatra_ta=nak_name_ta,
                    nakshatra_lord=nak_lord,
                    nakshatra_lord_ta=PLANET_NAMES_TA.get(nak_lord, nak_lord),
                    dasha_bhukti_antara=f"{win.dasha_lord} - {win.bhukti_lord} - {win.antara_lord}",
                    dasha_bhukti_antara_ta=(
                        f"{win.dasha_lord_ta} - {win.bhukti_lord_ta} - {win.antara_lord_ta}"
                    ),
                    abhijit_window=_fmt_utc_window(abhijit, tz_obj),
                    rahu_kalam_avoid=_fmt_utc_window(rahu, tz_obj),
                    score=total_date_score,
                    match_tier=tier,
                    match_tier_ta=tier_ta,
                    reasons_en=match_reasons_en,
                    reasons_ta=match_reasons_ta,
                )
            )
            cur += timedelta(days=1)

    candidates.sort(key=lambda c: (c.score, c.paksha == "Shukla"), reverse=True)
    return candidates[:max_results]


def calculate_kp_marriage_date(
    birth: BirthInput,
    start_date: Optional[date] = None,
    years_ahead: int = 2,
    ayanamsa_id: int = 1,
    native_name: str = "Native",
) -> KpMarriageDateResponse:
    """Run all 4 KP Marriage Date Finder engines and assemble the unified report."""
    local_dt, _, _, tz_name, offset_hours = resolve_birth_datetime(
        birth.birth_date,
        birth.birth_time,
        birth.timezone,
    )

    ayan_mode = "kp" if ayanamsa_id == 1 else "lahiri"
    birth_info = BirthInfo(
        date=local_dt.date(),
        time=local_dt.time(),
        latitude=birth.latitude,
        longitude=birth.longitude,
        tz_hours=offset_hours,
        place=getattr(birth, "place_name", "") or "",
    )
    eph = SwissEphemeris(ayanamsa=ayan_mode, node="mean")
    chart = compute_chart(birth_info, ayanamsa=ayan_mode, node="mean", eph=eph)

    s_date = start_date or date.today()
    e_date = s_date + timedelta(days=365 * max(1, min(5, years_ahead)))

    promise = assess_marriage_promise(chart)
    cusp_7 = analyze_seventh_cusp(chart)
    dasha_windows = find_favorable_dasha_windows(
        chart=chart,
        birth_local_dt=local_dt.replace(tzinfo=None),
        search_start=s_date,
        search_end=e_date,
        top_n=8,
    )
    candidate_dates = refine_marriage_dates(
        cusp_analysis=cusp_7,
        top_windows=dasha_windows,
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone_str=tz_name,
        ayanamsa_id=ayanamsa_id,
    )

    # Composite 70 / 25 / 5 summary
    promise_weighted = round((promise.total_score / 100.0) * 70.0, 1)
    best_dasha_score = dasha_windows[0].total_score if dasha_windows else 0.0
    dasha_weighted = round(best_dasha_score, 1)  # already out of 25
    transit_weighted = round(((candidate_dates[0].score / 100.0) * 5.0) if candidate_dates else 2.5, 1)

    return KpMarriageDateResponse(
        native_name=native_name,
        search_start_date=s_date.isoformat(),
        search_end_date=e_date.isoformat(),
        promise=promise,
        seventh_cusp=cusp_7,
        dasha_windows=dasha_windows,
        candidate_dates=candidate_dates,
        composite_weights={
            "promise_70": promise_weighted,
            "dasha_bhukti_25": dasha_weighted,
            "transit_muhurta_5": transit_weighted,
            "overall_100": round(promise_weighted + dasha_weighted + transit_weighted, 1),
        },
        disclaimer_en=DISCLAIMER_EN,
        disclaimer_ta=DISCLAIMER_TA,
        generated_at=datetime.now().isoformat(),
    )
