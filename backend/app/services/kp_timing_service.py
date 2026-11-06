"""KP Monthly & Period Predictive Event Timing Service.

Calculates definite monthly event fructification based strictly on Prof. K.S. Krishnamurti's
KP System principles:
1. Cuspal Sub-Lord (CSL) Natal Promise (விதி)
2. Running Dasa-Bhukti-Antara-Sookshma-Prana (DBAS) Hierarchy (நடப்பு கால பலன்)
3. Transit of Sun & Moon - The Golden Monthly/Daily Trigger (கோச்சார இயக்கம்)
4. Definite Fructification Classification (கண்டிப்பாக நடந்து தீரும் / சாதகம் / எச்சரிக்கை)
"""

from __future__ import annotations
import calendar
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

from app.schemas.common import BirthInput
from app.schemas.kp_timing import (
    KpDbaSummary,
    KpMonthlyEventItem,
    KpMonthlyPredictionRequest,
    KpMonthlyPredictionResponse,
    KpTransitSunSummary,
)
from app.services.dasa_service import calculate_dasa
from app.services.kp_engine.chart import BirthInfo, compute_chart
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.kp_engine.significators import house_of_longitude
from app.services.kp_engine.vedic import point_info
from app.services.timezone_utils import resolve_birth_datetime

MONTH_NAMES_EN = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTH_NAMES_TA = [
    "", "ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்",
    "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"
]

PLANET_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி பகவான்",
    "Rahu": "ராகு",
    "Ketu": "கேது",
}

SIGN_NAMES_TA: Dict[str, str] = {
    "Aries": "மேஷம்",
    "Taurus": "ரிஷபம்",
    "Gemini": "மிதுனம்",
    "Cancer": "கடகம்",
    "Leo": "சிம்மம்",
    "Virgo": "கன்னி",
    "Libra": "துலாம்",
    "Scorpio": "விருச்சிகம்",
    "Sagittarius": "தனுசு",
    "Capricorn": "மகரம்",
    "Aquarius": "கும்பம்",
    "Pisces": "மீனம்",
}

STAR_NAMES_TA: Dict[str, str] = {
    "Ashwini": "அசுவினி", "Bharani": "பரணி", "Krittika": "கிருத்திகை",
    "Rohini": "ரோகிணி", "Mrigashira": "மிருகசீரிஷம்", "Ardra": "திருவாதிரை",
    "Punarvasu": "புனர்பூசம்", "Pushya": "பூசம்", "Ashlesha": "ஆயில்யம்",
    "Magha": "மகம்", "Purva Phalguni": "பூரம்", "Uttara Phalguni": "உத்திரம்",
    "Hasta": "அஸ்தம்", "Chitra": "சித்திரை", "Swati": "சுவாதி",
    "Vishakha": "விசாகம்", "Anuradha": "அனுஷம்", "Jyeshtha": "கேட்டை",
    "Mula": "மூலம்", "Purva Ashadha": "பூராடம்", "Uttara Ashadha": "உத்திராடம்",
    "Shravana": "திருவோணம்", "Dhanishta": "அவிட்டம்", "Shatabhisha": "சதயம்",
    "Purva Bhadrapada": "பூரட்டாதி", "Uttara Bhadrapada": "உத்திரட்டாதி", "Revati": "ரேவதி",
}

# Core Event Domain Rules in KP Astrology
EVENT_RULES_DEFINITIONS = [
    {
        "id": "career_job_promotion",
        "title_en": "Career Growth, New Job & Promotion",
        "title_ta": "புதிய வேலை / உத்தியோக உயர்வு / தொழில் முன்னேற்றம்",
        "category": "career",
        "icon": "Briefcase",
        "primary_houses": [10],
        "supporting_houses": [2, 6, 10, 11],
        "negating_houses": [1, 5, 9, 12],
        "action_advice_ta": "முக்கியமான வேலை விண்ணப்பங்கள், நேர்காணல்கள் மற்றும் மேலதிகாரிகளுடனான பேச்சுவார்த்தைகளை இந்த சுப தினங்களில் முடிக்கவும்.",
    },
    {
        "id": "wealth_money_gain",
        "title_en": "Wealth Accumulation & Liquid Cash Gains",
        "title_ta": "தன வரவு / சேமிப்பு அதிகரிப்பு / திடீர் பண வரவு",
        "category": "finance",
        "icon": "Coins",
        "primary_houses": [2],
        "supporting_houses": [2, 6, 11],
        "negating_houses": [5, 8, 12],
        "action_advice_ta": "நிலுவையில் உள்ள தொகைகளை வசூலிக்கவும், லாபகரமான முதலீடுகளைச் செய்யவும் இது சிறந்த காலக்கட்டம்.",
    },
    {
        "id": "marriage_relationship",
        "title_en": "Marriage Union & Auspicious Relationship",
        "title_ta": "திருமண வரன் அமைதல் / சுப காரிய வெற்றி / தாம்பத்ய ஒற்றுமை",
        "category": "marriage",
        "icon": "Heart",
        "primary_houses": [7],
        "supporting_houses": [2, 7, 11],
        "negating_houses": [1, 6, 10],
        "action_advice_ta": "மணமகன்/மணமகள் பார்த்தல், நிச்சயதார்த்தம் மற்றும் குடும்பப் பேச்சுவார்த்தைகளுக்கு இந்த சாதகமான நாட்களைப் பயன்படுத்தவும்.",
    },
    {
        "id": "property_purchase",
        "title_en": "Property, Land & Real Estate Acquisition",
        "title_ta": "சொத்து / நிலம் / வீடு வாங்கும் யோகம்",
        "category": "property",
        "icon": "Home",
        "primary_houses": [4],
        "supporting_houses": [4, 11, 12],
        "negating_houses": [3, 5, 8],
        "action_advice_ta": "பத்திரம் பதிவு செய்தல், சொத்து முன்முயற்சிகள் எடுக்க மற்றும் புதிய வீடு குடிபுக சிறந்த காலம்.",
    },
    {
        "id": "vehicle_purchase",
        "title_en": "New Vehicle / Automobile Acquisition",
        "title_ta": "புதிய வாகனம் வாங்கும் பாக்கியம்",
        "category": "vehicle",
        "icon": "Car",
        "primary_houses": [4],
        "supporting_houses": [4, 11],
        "negating_houses": [3],
        "action_advice_ta": "புதிய இருசக்கர/நான்கு சக்கர வாகனம் வாங்கவும், முன்பதிவு செய்யவும் உகந்த காலகட்டம்.",
    },
    {
        "id": "foreign_travel",
        "title_en": "Foreign Travel, Relocation & Visa Clearance",
        "title_ta": "வெளிநாட்டுப் பயணம் / விசா அனுமதி / தொலைதூர இடமாற்றம்",
        "category": "travel",
        "icon": "Plane",
        "primary_houses": [12],
        "supporting_houses": [3, 9, 12],
        "negating_houses": [4, 11],
        "action_advice_ta": "விசா நேர்காணல், பாஸ்போர்ட் விண்ணப்பம் மற்றும் வெளிநாட்டு வேலை முயற்சிகளுக்கு நற்பலன் தரும்.",
    },
    {
        "id": "exam_education_success",
        "title_en": "Competitive Exams, Certification & Academic Victory",
        "title_ta": "போட்டித் தேர்வு வெற்றி / உயர் கல்வி / நேர்காணல் சித்தி",
        "category": "education",
        "icon": "GraduationCap",
        "primary_houses": [4, 9],
        "supporting_houses": [4, 6, 9, 11],
        "negating_houses": [3, 8, 12],
        "action_advice_ta": "தேர்வு எழுத, ஆராய்ச்சி அல்லது புதிய சான்றிதழ் படிப்புகளைத் தொடங்க சாதகமான நாட்கள்.",
    },
    {
        "id": "childbirth_progeny",
        "title_en": "Childbirth, Progeny & Family Happiness",
        "title_ta": "குழந்தை பாக்கியம் / குடும்பத்தில் மழலை நற்செய்தி",
        "category": "childbirth",
        "icon": "Baby",
        "primary_houses": [5],
        "supporting_houses": [2, 5, 11],
        "negating_houses": [1, 4, 10],
        "action_advice_ta": "சிகிச்சைகள் தொடங்க மற்றும் மங்களகரமான நற்செய்திகளைப் பெற சுப காலம்.",
    },
    {
        "id": "debt_clearance_litigation",
        "title_en": "Debt Relief, Enemy Subjugation & Court Victory",
        "title_ta": "கடன் அடைதல் / எதிரிகள் பணிதல் / வழக்கு வெற்றி",
        "category": "litigation_debts",
        "icon": "Scale",
        "primary_houses": [6],
        "supporting_houses": [6, 11],
        "negating_houses": [8, 12],
        "action_advice_ta": "நீதிமன்ற சமரச பேச்சுவார்த்தைகள் மற்றும் கடன்களை முழுமையாக அடைக்க ஏற்ற காலம்.",
    },
    {
        "id": "health_recovery",
        "title_en": "Health Vitality & Complete Recovery from Ailments",
        "title_ta": "உடல் நலம் சீராதல் / நோய் நீங்குதல் / ஆரோக்கிய மீட்சி",
        "category": "health",
        "icon": "Activity",
        "primary_houses": [1],
        "supporting_houses": [1, 5, 11],
        "negating_houses": [6, 8, 12],
        "action_advice_ta": "ஆரோக்கியம் பலப்படும்; மருத்துவச் சிகிச்சைகளிலிருந்து விடுபட்டு புத்துணர்ச்சி பெறலாம்.",
    },
    {
        "id": "caution_expenditure",
        "title_en": "Caution: Sudden Expenses & Mental Agitation",
        "title_ta": "எச்சரிக்கை: திடீர் விரயம் / தேவையற்ற அலைச்சல் / மன அமைதியின்மை",
        "category": "caution",
        "icon": "AlertTriangle",
        "primary_houses": [8, 12],
        "supporting_houses": [8, 12],
        "negating_houses": [2, 11],
        "action_advice_ta": "புதிய பெரிய முதலீடுகளைத் தவிர்க்கவும்; பணம் கொடுக்கல் வாங்கலில் கவனமாக இருக்கவும்.",
    },
]


def _get_planet_ta(name: str) -> str:
    return PLANET_NAMES_TA.get(name, name)


def _get_sign_ta(name: str) -> str:
    return SIGN_NAMES_TA.get(name, name)


def _get_star_ta(name: str) -> str:
    return STAR_NAMES_TA.get(name, name)


def calculate_kp_monthly_prediction(
    birth: BirthInput,
    year: int,
    month: int,
    ayanamsa_id: int = 1,
) -> KpMonthlyPredictionResponse:
    """Computes high-certainty KP monthly predictions for the target year and month."""
    # 1. Parse birth parameters
    birth_local_dt, birth_utc_dt, jd_ut, tz_name, tz_hours = resolve_birth_datetime(
        birth.birth_date, birth.birth_time, birth.timezone
    )

    b_info = BirthInfo(
        date=birth_local_dt.date(),
        time=birth_local_dt.time(),
        latitude=birth.latitude,
        longitude=birth.longitude,
        tz_hours=tz_hours,
        place="",
    )

    # 2. Compute Natal KP Chart
    eph = SwissEphemeris(ayanamsa="kp")
    chart = compute_chart(b_info, ayanamsa="kp", eph=eph)

    # Pre-calculate simplified significators: planet -> set of signified houses
    planet_houses: Dict[str, Set[int]] = {}
    for p, sigs in chart.planet_significators.items():
        planet_houses[p] = {s.house for s in sigs}

    # Cusp sub-lords: 1..12 -> planet name
    csl = chart.cusp_sublords

    # 3. Calculate Running Dasa Hierarchy for the Target Month (mid-month: 15th)
    _, num_days_in_month = calendar.monthrange(year, month)
    target_mid_date = date(year, month, min(15, num_days_in_month))
    
    dasa_res = calculate_dasa(
        birth=birth,
        depth=5,
        ayanamsa_id=ayanamsa_id,
        target_date=target_mid_date,
    )

    act = dasa_res.active_period
    md_lord = act.mahadasha if act else "Jupiter"
    ad_lord = act.antardasha if act else "Saturn"
    pd_lord = act.pratyantardasha if act else "Mercury"
    sd_lord = act.sookshmadasha if act else "Venus"
    prd_lord = act.pranadasha if act else "Sun"

    # Find the active dates for the running Antara/Bhukti
    period_start_str = f"{year}-{month:02d}-01"
    period_end_str = f"{year}-{month:02d}-{num_days_in_month:02d}"

    dba_summary = KpDbaSummary(
        mahadasha=md_lord,
        mahadasha_ta=_get_planet_ta(md_lord),
        antardasha=ad_lord,
        antardasha_ta=_get_planet_ta(ad_lord),
        pratyantardasha=pd_lord,
        pratyantardasha_ta=_get_planet_ta(pd_lord),
        sookshmadasha=sd_lord,
        sookshmadasha_ta=_get_planet_ta(sd_lord) if sd_lord else None,
        pranadasha=prd_lord,
        pranadasha_ta=_get_planet_ta(prd_lord) if prd_lord else None,
        period_start=period_start_str,
        period_end=period_end_str,
        active_date=target_mid_date.isoformat(),
    )

    # 4. Ephemeris Transit Scan of Sun & Moon for every day in this month
    sun_daily_points: List[Tuple[date, Any]] = []
    activated_stars_set: Set[str] = set()

    for d in range(1, num_days_in_month + 1):
        cur_date = date(year, month, d)
        cur_dt = datetime.combine(cur_date, time(5, 30))  # standard morning transit time
        jd_val = eph.jd_ut(cur_dt)
        pos = eph.sidereal_positions(jd_val)
        sun_lon = pos["Sun"][0]
        pi = point_info(sun_lon)
        sun_daily_points.append((cur_date, pi))
        activated_stars_set.add(pi.star)

    first_sun_pi = sun_daily_points[0][1]
    last_sun_pi = sun_daily_points[-1][1]

    transit_sun_summary = KpTransitSunSummary(
        month_name=MONTH_NAMES_EN[month],
        month_name_ta=MONTH_NAMES_TA[month],
        start_sign=first_sun_pi.sign,
        start_sign_ta=_get_sign_ta(first_sun_pi.sign),
        end_sign=last_sun_pi.sign,
        end_sign_ta=_get_sign_ta(last_sun_pi.sign),
        activated_stars=list(activated_stars_set),
        activated_stars_ta=[_get_star_ta(s) for s in activated_stars_set],
        summary_ta=(
            f"சூரியன் {MONTH_NAMES_TA[month]} மாதத்தில் {_get_sign_ta(first_sun_pi.sign)} முதல் "
            f"{_get_sign_ta(last_sun_pi.sign)} ராசி வரை சஞ்சரிக்கிறார். இக்காலத்தில் "
            f"{', '.join(_get_star_ta(s) for s in list(activated_stars_set)[:3])} நட்சத்திரங்களின் "
            f"வழியாகப் பயணம் செய்து சுப பலன்களை இயக்குகிறார்."
        ),
    )

    # 5. Evaluate Event Categories
    guaranteed_list: List[KpMonthlyEventItem] = []
    favorable_list: List[KpMonthlyEventItem] = []
    moderate_list: List[KpMonthlyEventItem] = []
    caution_list: List[KpMonthlyEventItem] = []
    all_events_list: List[KpMonthlyEventItem] = []

    # Significant DBA lords
    active_dba_lords = [md_lord, ad_lord, pd_lord]

    for rule in EVENT_RULES_DEFINITIONS:
        event_id = rule["id"]
        title_ta = rule["title_ta"]
        title_en = rule["title_en"]
        cat = rule["category"]
        icon = rule["icon"]
        pri_houses = rule["primary_houses"]
        supp_houses = set(rule["supporting_houses"])
        neg_houses = set(rule["negating_houses"])

        # A. Cuspal Sub-Lord Promise (Rule of Natal Chart)
        # Check primary cusp sub-lord
        pri_csl_planet = csl.get(pri_houses[0], "Jupiter")
        pri_csl_houses = planet_houses.get(pri_csl_planet, set())
        
        csl_supports = bool(pri_csl_houses.intersection(supp_houses))
        csl_negates = bool(pri_csl_houses.intersection(neg_houses))

        # CSL Promise text
        if csl_supports and not csl_negates:
            csl_promise_ta = (
                f"{pri_houses[0]}-ஆம் பாவ உப-நட்சத்திர நாதன் {_get_planet_ta(pri_csl_planet)} "
                f"சுப பாவங்களான {', '.join(str(h) for h in sorted(pri_csl_houses.intersection(supp_houses)))} "
                f"ஆகியவற்றை குறிப்பதால், இந்த காரியம் ஜாதகத்தில் முழுமையாக அனுமதிக்கப்பட்டுள்ளது."
            )
        elif csl_supports:
            csl_promise_ta = (
                f"{pri_houses[0]}-ஆம் பாவ உப-நட்சத்திர நாதன் {_get_planet_ta(pri_csl_planet)} "
                f"கலவையான பலன்களைக் காட்டுகிறார் (ஆதரவு மற்றும் விரயம்)."
            )
        else:
            csl_promise_ta = (
                f"{pri_houses[0]}-ஆம் பாவ உப-நட்சத்திர நாதன் {_get_planet_ta(pri_csl_planet)} "
                f"நேரடி சுப பாவங்களைத் தொடர்பு கொள்ளாததால் மிதமான பலன்."
            )

        # B. Dasa - Bhukti - Antara Connection
        md_houses = planet_houses.get(md_lord, set())
        ad_houses = planet_houses.get(ad_lord, set())
        pd_houses = planet_houses.get(pd_lord, set())

        # Scoring and Fruitful Significators identification
        supp_hit_count = 0
        neg_hit_count = 0
        fruitful_planets: Set[str] = set()

        # Add primary cusp sub-lord if supportive
        if csl_supports:
            fruitful_planets.add(pri_csl_planet)

        # Check all planets that signify the supporting houses (Grade A, B, C)
        for p, hset in planet_houses.items():
            if hset.intersection(supp_houses):
                # If planet is in active DBA lords or owns/occupies primary house
                if p in active_dba_lords or p == pri_csl_planet:
                    fruitful_planets.add(p)

        for lord, hset in [(md_lord, md_houses), (ad_lord, ad_houses), (pd_lord, pd_houses)]:
            s_hits = hset.intersection(supp_houses)
            n_hits = hset.intersection(neg_houses)
            if s_hits:
                supp_hit_count += len(s_hits) * 2
                fruitful_planets.add(lord)
            if n_hits:
                neg_hit_count += len(n_hits)

        # C. Scan Sun transit days that trigger this event
        # Sun triggers when Sun's SUB-LORD (tightest trigger) or STAR-LORD matches fruitful significators
        candidate_days: List[int] = []
        sub_candidate_days: List[int] = []

        for cur_date, pi in sun_daily_points:
            # Check if Sun's Sub-Lord or Star-Lord is a fruitful significator
            is_sub_match = pi.sub_lord in fruitful_planets
            is_star_match = pi.star_lord in fruitful_planets
            if is_sub_match:
                sub_candidate_days.append(cur_date.day)
            if is_sub_match or is_star_match:
                candidate_days.append(cur_date.day)

        # Use the most specific window (sub-lord matches first if available)
        effective_days = sub_candidate_days if len(sub_candidate_days) >= 3 else candidate_days

        # Date window formatting
        if effective_days:
            # Group into contiguous spans or take min/max
            start_day = effective_days[0]
            end_day = effective_days[-1]
            trigger_window = f"{MONTH_NAMES_TA[month]} {start_day}, {year} முதல் {MONTH_NAMES_TA[month]} {end_day}, {year} வரை"
            transit_trigger_ta = (
                f"கோச்சார சூரியன் {MONTH_NAMES_TA[month]} {start_day} முதல் {end_day} வரை "
                f"காரிய சித்தி தரும் சுப கிரகங்களின் (உப-நட்சத்திரத்தில்) சஞ்சரிப்பதால் "
                f"இக்காலத்தில் பலன் நேரடியாக வெளிப்படும்."
            )
        else:
            mid_start = min(10, num_days_in_month)
            mid_end = min(22, num_days_in_month)
            trigger_window = f"{MONTH_NAMES_TA[month]} {mid_start}, {year} முதல் {MONTH_NAMES_TA[month]} {mid_end}, {year} வரை"
            transit_trigger_ta = (
                f"நடப்பு மாதத்தின் இரண்டாம் பகுதியில் கோச்சார கிரக நிலைகள் சாதகமாக உள்ளன."
            )

        # D. Dasa-Bhukti Role Text
        dba_role_ta = (
            f"நடப்பு தசா நாதன் {_get_planet_ta(md_lord)}, புத்தி நாதன் {_get_planet_ta(ad_lord)}, "
            f"அந்தர நாதன் {_get_planet_ta(pd_lord)} ஆவர். "
            f"புத்தி நாதன் {_get_planet_ta(ad_lord)} "
            f"{', '.join(str(h) for h in sorted(ad_houses))} பாவங்களை இயக்குவதால் பலன் தீர்மானிக்கப்படுகிறது."
        )

        # E. Determine Status and Grade
        # Special logic for caution_expenditure
        if cat == "caution":
            if neg_hit_count >= 3 or (8 in ad_houses or 12 in ad_houses):
                status = "CAUTION"
                status_label = "எச்சரிக்கை / விரயக் காலம்"
                score = 85
                summary_verdict = (
                    f"இந்த {MONTH_NAMES_TA[month]} மாதத்தில் தேவையற்ற பண விரயங்கள், வீண் அலைச்சல் மற்றும் மன உளைச்சல் ஏற்பட "
                    f"வாய்ப்புகள் அதிகம். நிதானமாகச் செயல்பட வேண்டும்."
                )
            else:
                status = "MODERATE"
                status_label = "சுமாரான அலைச்சல்"
                score = 45
                summary_verdict = f"பெரிய விரயங்கள் இல்லை; எனினும் வரவு-செலவில் கவனமாக இருப்பது நல்லது."
        else:
            # Positive events
            if csl_supports and (supp_hit_count >= 4) and bool(candidate_days) and (neg_hit_count <= 2):
                status = "GUARANTEED"
                status_label = "100% கண்டிப்பாக நடந்து தீரும்"
                score = 95
                summary_verdict = (
                    f"KP தத்துவப்படி இந்த {MONTH_NAMES_TA[month]} மாதத்தில் இக்காரியம் **100% கண்டிப்பாக நடந்து தீரும்!** "
                    f"பாவ உப-நாதன் உத்தரவாதத்துடன் தசா-புத்தி மற்றும் கோச்சார சூரியன் ஒன்று கூடி பலனைத் தருகின்றன."
                )
            elif csl_supports and supp_hit_count >= 2:
                status = "HIGHLY_FAVORABLE"
                status_label = "மிக சாதகமான சூழல் (85-90%)"
                score = 85
                summary_verdict = (
                    f"இந்த {MONTH_NAMES_TA[month]} மாதத்தில் மிக அனுகூலமான வாய்ப்புகள் கூடி வரும். "
                    f"சிறிய முயற்சிகள் கூட பெரும் வெற்றியைத் தரும்."
                )
            elif supp_hit_count > neg_hit_count:
                status = "MODERATE"
                status_label = "முயற்சி தேவை / சுமாரான பலன்"
                score = 60
                summary_verdict = (
                    f"வாய்ப்புகள் உண்டு; ஆனால் தாமதங்கள் ஏற்படலாம். தீவிர முயற்சிக்குப் பிறகே காரியம் கைகூடும்."
                )
            else:
                status = "CAUTION"
                status_label = "காரியத் தடை / சாதகமற்ற காலம்"
                score = 30
                summary_verdict = (
                    f"இந்த {MONTH_NAMES_TA[month]} மாதத்தில் இக்காரியத்தைத் தொடங்குவதைத் தவிர்க்கவும். "
                    f"தடைகளும் காலதாமதமும் ஏற்பட வாய்ப்புள்ளது."
                )

        detailed_analysis_ta = (
            f"**KP ஆய்வுக் குறிப்பு:** காரிய ஸ்தானம்: {', '.join(str(h) for h in pri_houses)}. "
            f"துணை ஸ்தானங்கள்: {', '.join(str(h) for h in sorted(supp_houses))}. "
            f"நடப்பு காலத்தில் புத்தி நாதன் {_get_planet_ta(ad_lord)} "
            f"மற்றும் அந்தர நாதன் {_get_planet_ta(pd_lord)} ஆகியோரின் பலம் மேலோங்கியுள்ளது. "
            f"{transit_trigger_ta}"
        )

        event_item = KpMonthlyEventItem(
            event_id=event_id,
            title_en=title_en,
            title_ta=title_ta,
            category=cat,
            icon=icon,
            status=status,
            status_label_ta=status_label,
            probability_score=score,
            trigger_window_dates=trigger_window,
            summary_verdict_ta=summary_verdict,
            detailed_analysis_ta=detailed_analysis_ta,
            cuspal_promise_ta=csl_promise_ta,
            dasha_bhukti_role_ta=dba_role_ta,
            transit_trigger_ta=transit_trigger_ta,
            actionable_remedy_ta=rule["action_advice_ta"],
            primary_houses=pri_houses,
            supporting_houses=sorted(supp_houses),
            negating_houses=sorted(neg_houses),
            significator_planets=[_get_planet_ta(p) for p in sorted(fruitful_planets)],
        )

        all_events_list.append(event_item)

        if status == "GUARANTEED":
            guaranteed_list.append(event_item)
        elif status == "HIGHLY_FAVORABLE":
            favorable_list.append(event_item)
        elif status == "MODERATE":
            moderate_list.append(event_item)
        elif status == "CAUTION":
            caution_list.append(event_item)

    # Sort guaranteed and favorable by score desc
    guaranteed_list.sort(key=lambda x: x.probability_score, reverse=True)
    favorable_list.sort(key=lambda x: x.probability_score, reverse=True)

    # Overall month summary
    month_name_ta = MONTH_NAMES_TA[month]
    guaranteed_count = len(guaranteed_list)
    favorable_count = len(favorable_list)

    if guaranteed_count > 0:
        overall_summary = (
            f"{month_name_ta} {year}-ஆம் ஆண்டு KP கணிதப்படி மிகச் சிறப்பான சாதகமான மாதமாகும். "
            f"மொத்தம் {guaranteed_count} முக்கிய காரியங்கள் கண்டிப்பாக நடந்து தீரும் என்ற உன்னத அமைப்பில் உள்ளன. "
            f"{favorable_count} காரியங்களுக்கு மிக நல்ல வாய்ப்புகள் உள்ளன. "
            f"குறிப்பிடப்பட்டுள்ள சுப தினங்களில் உங்கள் முக்கிய முயற்சிகளைத் தொடங்கினால் 100% வெற்றி நிச்சயம்!"
        )
    else:
        overall_summary = (
            f"{month_name_ta} {year}-ஆம் ஆண்டு மிதமான மற்றும் எச்சரிக்கையுடன் செயல்பட வேண்டிய மாதமாகும். "
            f"சுமாரான வாய்ப்புகள் உள்ள காரியங்களில் கூடுதல் கவனம் தேவை."
        )

    return KpMonthlyPredictionResponse(
        year=year,
        month=month,
        month_label=f"{MONTH_NAMES_EN[month]} {year}",
        month_label_ta=f"{MONTH_NAMES_TA[month]} {year}",
        native_name=getattr(birth, "name", "") or "ஜாதகர்",
        dasha_hierarchy=dba_summary,
        transit_sun=transit_sun_summary,
        guaranteed_events=guaranteed_list,
        favorable_events=favorable_list,
        moderate_events=moderate_list,
        caution_events=caution_list,
        all_events=all_events_list,
        overall_month_summary_ta=overall_summary,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
