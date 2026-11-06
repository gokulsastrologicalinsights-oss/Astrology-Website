"""Upcoming Milestone Windows Scanner for KP Predictive Narrative Engine.

Pinpoints specific monthly windows over the next 12–24 months for career leaps,
financial gains, and matrimonial progress with plain-language action plans.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.kp_narrative import MilestoneWindowItem
from app.services.kp_engine.dasha import (
    mahadasha_timeline,
    antardashas_of,
    pratyantardashas_of,
    dasha_balance,
)
from .constants import PLANET_NAMES_TA
from .natal_evaluator import _get_planet_signified_houses

TAMIL_MONTHS: Dict[int, str] = {
    1: "ஜனவரி",
    2: "பிப்ரவரி",
    3: "மார்ச்",
    4: "ஏப்ரல்",
    5: "மே",
    6: "ஜூன்",
    7: "ஜூலை",
    8: "ஆகஸ்ட்",
    9: "செப்டம்பர்",
    10: "அக்டோபர்",
    11: "நவம்பர்",
    12: "டிசம்பர்",
}

ENGLISH_MONTHS: Dict[int, str] = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def _format_window_title(s_dt: datetime, e_dt: datetime) -> Tuple[str, str]:
    """Generates e.g. ('Dec 2026 – Feb 2027', 'டிசம்பர் 2026 – பிப்ரவரி 2027')."""
    s_en = f"{ENGLISH_MONTHS[s_dt.month]} {s_dt.year}"
    e_en = f"{ENGLISH_MONTHS[e_dt.month]} {e_dt.year}"
    title_en = f"{s_en} – {e_en}" if s_en != e_en else s_en

    s_ta = f"{TAMIL_MONTHS[s_dt.month]} {s_dt.year}"
    e_ta = f"{TAMIL_MONTHS[e_dt.month]} {e_dt.year}"
    title_ta = f"{s_ta} – {e_ta}" if s_ta != e_ta else s_ta

    return title_en, title_ta


def scan_upcoming_milestone_windows(
    kp_chart: Any,
    birth_dt: datetime,
    start_dt: datetime,
    months_ahead: int = 24,
) -> List[MilestoneWindowItem]:
    """Scans the next 12-24 months and detects milestone windows for Career, Finance, and Matrimony."""
    end_dt = start_dt + timedelta(days=int(months_ahead * 30.4375))
    moon_lon = 0.0
    planets_dict = getattr(kp_chart, "planets", {})
    if isinstance(planets_dict, dict) and "Moon" in planets_dict:
        moon_lon = getattr(planets_dict["Moon"], "longitude", 0.0)
    elif hasattr(kp_chart, "planet_lon") and isinstance(kp_chart.planet_lon, dict):
        moon_lon = kp_chart.planet_lon.get("Moon", 0.0)

    bal = dasha_balance(moon_lon)
    all_mds = mahadasha_timeline(moon_lon)

    # Collect sub-periods covering start_dt to end_dt
    windows_raw: List[Dict[str, Any]] = []

    for md in all_mds:
        md_start = birth_dt + timedelta(days=md.start_days)
        md_end = birth_dt + timedelta(days=md.end_days)
        if md_end <= start_dt or md_start >= end_dt:
            continue

        ads = antardashas_of(md, bal)
        for ad in ads:
            ad_start = md_start + timedelta(days=ad.start_days)
            ad_end = md_start + timedelta(days=ad.end_days)
            if ad_end <= start_dt or ad_start >= end_dt:
                continue

            md_partial = md.start_days == 0
            pds = pratyantardashas_of(ad, bal, md_is_partial=md_partial)
            for pd in pds:
                pd_start = ad_start + timedelta(days=pd.start_days)
                pd_end = ad_start + timedelta(days=pd.end_days)
                if pd_end <= start_dt or pd_start >= end_dt:
                    continue

                w_s = max(start_dt, pd_start)
                w_e = min(end_dt, pd_end)
                if (w_e - w_s).days < 14:
                    continue  # skip tiny windows under 2 weeks

                # Combined signified houses of MD, AD, and PD lords
                sig_md = set(_get_planet_signified_houses(md.lord, kp_chart))
                sig_ad = set(_get_planet_signified_houses(ad.lord, kp_chart))
                sig_pd = set(_get_planet_signified_houses(pd.lord, kp_chart))
                combo_sig = sig_md | sig_ad | sig_pd

                windows_raw.append({
                    "start": w_s,
                    "end": w_e,
                    "md": md.lord,
                    "ad": ad.lord,
                    "pd": pd.lord,
                    "sig": combo_sig,
                    "duration_days": (w_e - w_s).days,
                })

    milestones: List[MilestoneWindowItem] = []
    w_idx = 1

    # 1. Evaluate Career Milestones (Houses 2, 6, 10, 11 vs 5, 8, 12)
    career_candidates = []
    for w in windows_raw:
        supp = len(w["sig"] & {2, 6, 10, 11})
        chal = len(w["sig"] & {5, 8, 12})
        score = supp * 2 - chal
        if supp >= 2 and score >= 2:
            career_candidates.append((score, w))

    career_candidates.sort(key=lambda x: x[0], reverse=True)
    if career_candidates:
        best_c = career_candidates[0][1]
        t_en, t_ta = _format_window_title(best_c["start"], best_c["end"])
        md_ta = PLANET_NAMES_TA.get(best_c['md'], best_c['md'])
        ad_ta = PLANET_NAMES_TA.get(best_c['ad'], best_c['ad'])
        pd_ta = PLANET_NAMES_TA.get(best_c['pd'], best_c['pd'])
        milestones.append(
            MilestoneWindowItem(
                id=f"win-career-{w_idx}",
                domain="career",
                domain_label_en="Career & Professional Elevation",
                domain_label_ta="தொழில் உயர்வு & வேலை வாய்ப்புகள்",
                window_title_en=t_en,
                window_title_ta=t_ta,
                start_date=best_c["start"].strftime("%Y-%m-%d"),
                end_date=best_c["end"].strftime("%Y-%m-%d"),
                active_dba=f"{best_c['md']} MD – {best_c['ad']} AD – {best_c['pd']} PD",
                status="Golden Opportunity",
                status_ta="பொற்காலம் (மிகச் சிறந்த பலன்)",
                headline_en="Major Career Breakthrough & Promotion Window",
                headline_ta="தொழில் முன்னேற்றம் மற்றும் உத்தியோக பதவி உயர்வுக்கான சிறந்த காலம்",
                plain_narrative_en=(
                    f"During this timeframe ({t_en}), planetary influences strongly support your workplace growth. "
                    f"You will experience supportive management reception, favorable appraisals, or breakthrough interviews for senior roles. "
                    f"Any initiative to expand responsibilities will be rewarded with long-term prestige."
                ),
                plain_narrative_ta=(
                    f"இந்தக் காலகட்டத்தில் ({t_ta}) {md_ta} மற்றும் {ad_ta} அமைப்பானது உங்கள் தொழில் வாழ்க்கையில் உன்னதமான திருப்புமுனையை உண்டாக்கும். "
                    f"வேலை தேடுபவர்களுக்கு சிறந்த ஊதியத்துடன் கூடிய புதிய உத்தியோகம் அமையும். உத்தியோகத்தில் உள்ளவர்களுக்கு நீண்ட நாள் எதிர்பார்த்த "
                    f"பதவி உயர்வு மற்றும் சம்பள உயர்வு கைகூடும்."
                ),
                action_plan_en=[
                    "Submit formal requests for performance review or title progression.",
                    "Attend interviews or pitch major new client proposals.",
                    "Update certifications and articulate accomplishments directly to decision-makers.",
                ],
                action_plan_ta=[
                    "பதவி உயர்வு அல்லது சம்பள உயர்வு குறித்து நிர்வாகத்திடம் வெளிப்படையாக கோரிக்கை வைக்கவும்.",
                    "புதிய வேலைக்கான நேர்முகத் தேர்வுகளில் கலந்து கொள்ளவும் அல்லது புதிய தொழில் விரிவாக்கங்களை தொடங்கவும்.",
                    "உங்கள் திறமைகளை வெளிப்படுத்தி மேலதிகாரிகளின் நன்மதிப்பை பெறுங்கள்.",
                ],
            )
        )
        w_idx += 1

    # 2. Evaluate Financial Milestone (Houses 2, 6, 11 vs 5, 8, 12)
    fin_candidates = []
    for w in windows_raw:
        supp = len(w["sig"] & {2, 6, 11})
        chal = len(w["sig"] & {5, 8, 12})
        score = supp * 2 - chal
        if supp >= 2 and score >= 2:
            fin_candidates.append((score, w))

    fin_candidates.sort(key=lambda x: x[0], reverse=True)
    if fin_candidates:
        # Pick one that doesn't completely overlap with career if possible, or pick top
        best_f = fin_candidates[0][1]
        for _, fc in fin_candidates:
            if milestones and fc["start"] != best_c["start"]:
                best_f = fc
                break

        t_en, t_ta = _format_window_title(best_f["start"], best_f["end"])
        md_ta = PLANET_NAMES_TA.get(best_f['md'], best_f['md'])
        ad_ta = PLANET_NAMES_TA.get(best_f['ad'], best_f['ad'])
        pd_ta = PLANET_NAMES_TA.get(best_f['pd'], best_f['pd'])
        milestones.append(
            MilestoneWindowItem(
                id=f"win-finance-{w_idx}",
                domain="finance",
                domain_label_en="Financial Accumulation & Wealth",
                domain_label_ta="தன வரவு & சேமிப்பு பெருக்கம்",
                window_title_en=t_en,
                window_title_ta=t_ta,
                start_date=best_f["start"].strftime("%Y-%m-%d"),
                end_date=best_f["end"].strftime("%Y-%m-%d"),
                active_dba=f"{best_f['md']} MD – {best_f['ad']} AD – {best_f['pd']} PD",
                status="Favorable Window",
                status_ta="சாதகமான சூழல் (தன லாபம்)",
                headline_en="Strong Wealth Liquidity & Debt Resolution Window",
                headline_ta="பணப்புழக்க வளர்ச்சி மற்றும் கடன்கள் தீரும் நற்காலம்",
                plain_narrative_en=(
                    f"A highly encouraging financial corridor ({t_en}) where incoming cash balances improve significantly. "
                    f"Pending dues, arrears, or bonuses get cleared smoothly. You will have surplus capital to clear past obligations "
                    f"or begin purchasing tangible real assets."
                ),
                plain_narrative_ta=(
                    f"இக்காலகட்டத்தில் ({t_ta}) பண வரவு தாராளமாக இருக்கும். வர வேண்டிய பழைய பாக்கிகள் வசூலாகும். "
                    f"கடன் சுமைகளை குறைக்கவும், நிலம், வாகனம் அல்லது பொன் ஆபரணங்கள் வாங்கிச் சேர்க்கவும் இது மிகச் சிறந்த வாய்ப்பாகும்."
                ),
                action_plan_en=[
                    "Channel incoming surplus funds to pay down high-interest liabilities.",
                    "Lock funds in secure long-term investments rather than keeping them idle.",
                    "Negotiate favorable rates for any intended asset or property acquisition.",
                ],
                action_plan_ta=[
                    "வரும் உபரி பணத்தைக் கொண்டு பழைய கடன்களை அடைக்க முன்னுரிமை கொடுங்கள்.",
                    "பணத்தை சும்மா வைத்திருக்காமல் நிலையான முதலீடுகளில் அல்லது தங்கத்தில் சேமியுங்கள்.",
                    "சொத்து அல்லது வாகனம் வாங்கும் திட்டங்களை இக்காலத்தில் துவங்கலாம்.",
                ],
            )
        )
        w_idx += 1

    # 3. Evaluate Matrimonial Progress (Houses 2, 7, 11 vs 1, 6, 10, 12)
    mat_candidates = []
    for w in windows_raw:
        supp = len(w["sig"] & {2, 7, 11})
        chal = len(w["sig"] & {1, 6, 10})
        score = supp * 2 - chal
        if supp >= 2:
            mat_candidates.append((score, w))

    mat_candidates.sort(key=lambda x: x[0], reverse=True)
    if mat_candidates:
        best_m = mat_candidates[0][1]
        for _, mc in mat_candidates:
            if len(milestones) >= 2 and mc["start"] not in [m.start_date for m in milestones]:
                best_m = mc
                break

        t_en, t_ta = _format_window_title(best_m["start"], best_m["end"])
        md_ta = PLANET_NAMES_TA.get(best_m['md'], best_m['md'])
        ad_ta = PLANET_NAMES_TA.get(best_m['ad'], best_m['ad'])
        pd_ta = PLANET_NAMES_TA.get(best_m['pd'], best_m['pd'])
        milestones.append(
            MilestoneWindowItem(
                id=f"win-matrimony-{w_idx}",
                domain="matrimony",
                domain_label_en="Matrimonial Union & Harmony",
                domain_label_ta="திருமணம் & குடும்ப சுபநிகழ்ச்சிகள்",
                window_title_en=t_en,
                window_title_ta=t_ta,
                start_date=best_m["start"].strftime("%Y-%m-%d"),
                end_date=best_m["end"].strftime("%Y-%m-%d"),
                active_dba=f"{best_m['md']} MD – {best_m['ad']} AD – {best_m['pd']} PD",
                status="Golden Opportunity",
                status_ta="பொற்காலம் (சுபகாரிய சித்தி)",
                headline_en="Alliance Settlement & Auspicious Family Celebrations",
                headline_ta="சுபகாரியப் பேச்சுவார்த்தைகள் சுபமாக முடிவடையும் காலம்",
                plain_narrative_en=(
                    f"For unmarried natives, {t_en} is an optimal window for finalized matrimonial alliances and wedding celebrations. "
                    f"Mutual chemistry and family concurrence align effortlessly. For married couples, this period revitalizes romantic warmth "
                    f"and strengthens partnership solidarity."
                ),
                plain_narrative_ta=(
                    f"திருமணம் ஆகாதவர்களுக்கு ({t_ta}) நல்ல வரன் அமைந்து சுபநிகழ்ச்சிகள் முடிவாகும் பொன்னான காலமாகும். "
                    f"இருவீட்டார் சம்மதமும் இனிதே கைகூடும். திருமணமான தம்பதியரிடையே அன்பும் பரஸ்பர ஆதரவும் பெருகி இல்லறம் சிறக்கும்."
                ),
                action_plan_en=[
                    "Accelerate matrimonial search and finalize auspicious engagement dates.",
                    "Prioritize quality couple time and resolve past domestic misunderstandings.",
                    "Engage family elders positively in relationship discussions.",
                ],
                action_plan_ta=[
                    "வரன் பார்க்கும் முயற்சிகளை தீவிரப்படுத்தி நிச்சயதார்த்தத்தை முடிவு செய்யலாம்.",
                    "குடும்பத்தாரோடு மனம் விட்டுப் பேசி மகிழ்ச்சியான சுபநிகழ்ச்சிகளை திட்டமிடுங்கள்.",
                    "வாழ்க்கைத் துணையுடன் ஆன்மீகத் தலங்களுக்கு சென்று ஆசி பெறுங்கள்.",
                ],
            )
        )
        w_idx += 1

    # Fallback if no window scored high enough: generate realistic 2-month outlook
    if not milestones and windows_raw:
        first_w = windows_raw[0]
        t_en, t_ta = _format_window_title(first_w["start"], first_w["end"])
        milestones.append(
            MilestoneWindowItem(
                id="win-general-1",
                domain="career",
                domain_label_en="General Steady Progress",
                domain_label_ta="பொதுவான சீரான முன்னேற்றம்",
                window_title_en=t_en,
                window_title_ta=t_ta,
                start_date=first_w["start"].strftime("%Y-%m-%d"),
                end_date=first_w["end"].strftime("%Y-%m-%d"),
                active_dba=f"{first_w['md']} MD – {first_w['ad']} AD – {first_w['pd']} PD",
                status="Favorable Window",
                status_ta="சாதகமான சூழல்",
                headline_en="Consolidation and Steady Progression",
                headline_ta="நிலையான உழைப்பு மற்றும் வளர்ச்சி தரும் காலம்",
                plain_narrative_en=f"A steady phase ({t_en}) for focusing on core daily work and gradual savings growth.",
                plain_narrative_ta=f"இந்தக் காலகட்டம் ({t_ta}) அன்றாடப் பணிகளில் கவனம் செலுத்தி படிப்படியாக சேமிப்பை உயர்த்தும் சீரான காலமாகும்.",
                action_plan_en=["Maintain steady daily routines and avoid speculative hazards."],
                action_plan_ta=["தினசரி கடமைகளை சரிவர செய்து, புதிய வீண் கடன் வாங்குவதை தவிர்க்கவும்."],
            )
        )

    return milestones
