"""KP Daily Horoscope & Transit Engine.

Computes daily astrological forecasts for all 12 Rashis (Mesha to Meena) using the
Krishnamurti Paddhati (KP) system, high-precision XALEN ephemeris, and real-time transits.

Generates:
1. Executive Brief Statement of the Day (English & Tamil)
2. Peak Highlight & Caution Trap
3. Granular Aspect Predictions (Career, Finance, Love, Health, Travel)
4. Moon Sub-Lord hourly timeline windows (Golden, Neutral, Caution)
5. Daily KP Remediations, Lucky colors, numbers, and directions
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

import xalen

from app.schemas.kp_daily_horoscope import (
    KpAspectPrediction,
    KpDailyHoroscopeResponse,
    MoonSubLordWindow,
    RashiDailyPrediction,
)
from app.services.ephemeris import AYANAMSA_NAMES
from app.services.kp_engine.constants import (
    NAKSHATRAS,
    PLANET_ABBR,
    SIGN_LORDS,
    SIGNS,
    SIGNS_RULED_BY,
    VIMSHOTTARI_ORDER,
)
from app.services.kp_engine.vedic import normalize_longitude, point_info
from app.services.timezone_utils import resolve_birth_datetime

logger = logging.getLogger(__name__)

# Traditional 9 Vedic Grahas
PLANET_IDS: Dict[str, int] = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Rahu": 9,
    "Ketu": 13,
}

# 12 Rashis mapping: index 1-12 -> (English, Tamil, Sign Lord)
RASHI_METADATA: Dict[int, Tuple[str, str, str]] = {
    1: ("Aries", "மேஷம்", "Mars"),
    2: ("Taurus", "ரிஷபம்", "Venus"),
    3: ("Gemini", "மிதுனம்", "Mercury"),
    4: ("Cancer", "கடகம்", "Moon"),
    5: ("Leo", "சிம்மம்", "Sun"),
    6: ("Virgo", "கன்னி", "Mercury"),
    7: ("Libra", "துலாம்", "Venus"),
    8: ("Scorpio", "விருச்சிகம்", "Mars"),
    9: ("Sagittarius", "தனுசு", "Jupiter"),
    10: ("Capricorn", "மகரம்", "Saturn"),
    11: ("Aquarius", "கும்பம்", "Saturn"),
    12: ("Pisces", "மீனம்", "Jupiter"),
}

SIGN_TO_INDEX: Dict[str, int] = {
    "Aries": 1, "Mesha": 1, "Mesham": 1, "மேஷம்": 1,
    "Taurus": 2, "Vrishabha": 2, "Rishabham": 2, "ரிஷபம்": 2,
    "Gemini": 3, "Mithuna": 3, "Mithunam": 3, "மிதுனம்": 3,
    "Cancer": 4, "Karka": 4, "Kadagam": 4, "கடகம்": 4,
    "Leo": 5, "Simha": 5, "Simmam": 5, "சிம்மம்": 5,
    "Virgo": 6, "Kanya": 6, "Kanni": 6, "கன்னி": 6,
    "Libra": 7, "Tula": 7, "Thulaam": 7, "துலாம்": 7,
    "Scorpio": 8, "Vrischika": 8, "Viruchigam": 8, "விருச்சிகம்": 8,
    "Sagittarius": 9, "Dhanu": 9, "Dhanusu": 9, "தனுசு": 9,
    "Capricorn": 10, "Makara": 10, "Magaram": 10, "மகரம்": 10,
    "Aquarius": 11, "Kumbha": 11, "Kumbam": 11, "கும்பம்": 11,
    "Pisces": 12, "Meena": 12, "Meenam": 12, "மீனம்": 12,
}

WEEKDAY_INFO: List[Tuple[str, str, str]] = [
    ("Monday", "திங்கட்கிழமை", "Moon"),
    ("Tuesday", "செவ்வாய்க்கிழமை", "Mars"),
    ("Wednesday", "புதன்கிழமை", "Mercury"),
    ("Thursday", "வியாழக்கிழமை", "Jupiter"),
    ("Friday", "வெள்ளிக்கிழமை", "Venus"),
    ("Saturday", "சனிக்கிழமை", "Saturn"),
    ("Sunday", "ஞாயிற்றுக்கிழமை", "Sun"),
]

LUCKY_ATTRIBUTES: Dict[str, Dict[str, Any]] = {
    "Sun": {"color_en": "Ruby Red & Gold", "color_ta": "சிவப்பு & பொன் நிறம்", "num": 1, "dir_en": "East", "dir_ta": "கிழக்கு"},
    "Moon": {"color_en": "Pearl White & Silver", "color_ta": "முத்து வெள்ளை & வெள்ளி", "num": 2, "dir_en": "North-West", "dir_ta": "வடமேற்கு"},
    "Mars": {"color_en": "Coral Red & Crimson", "color_ta": "பவள சிவப்பு & அடர் சிவப்பு", "num": 9, "dir_en": "South", "dir_ta": "தெற்கு"},
    "Mercury": {"color_en": "Emerald Green & Mint", "color_ta": "மரகத பச்சை & புதினா", "num": 5, "dir_en": "North", "dir_ta": "வடக்கு"},
    "Jupiter": {"color_en": "Golden Yellow & Saffron", "color_ta": "தங்க மஞ்சள் & காவி", "num": 3, "dir_en": "North-East", "dir_ta": "வடகிழக்கு"},
    "Venus": {"color_en": "Pure White & Pastel Blue", "color_ta": "தூய வெள்ளை & இளநீலம்", "num": 6, "dir_en": "South-East", "dir_ta": "தென்கிழக்கு"},
    "Saturn": {"color_en": "Dark Blue & Charcoal", "color_ta": "அடர் நீலம் & சாம்பல்", "num": 8, "dir_en": "West", "dir_ta": "மேற்கு"},
    "Rahu": {"color_en": "Smoky Grey & Navy", "color_ta": "புகை சாம்பல் & நீலம்", "num": 4, "dir_en": "South-West", "dir_ta": "தென்மேற்கு"},
    "Ketu": {"color_en": "Multi-color & Ochre", "color_ta": "பல்வண்ணம் & பழுப்பு", "num": 7, "dir_en": "North-East", "dir_ta": "வடகிழக்கு"},
}

KP_DAILY_REMEDIES: Dict[str, Tuple[str, str]] = {
    "Sun": (
        "Offer water to the rising Sun or recite the Gayatri Mantra for leadership and clarity.",
        "காலை நேரத்தில் சூரிய நமஸ்காரம் செய்யவும் அல்லது காயத்ரி மந்திரம் சொல்லி பணியைத் தொடங்கவும்."
    ),
    "Moon": (
        "Stay hydrated and avoid emotionally charged decisions during evening hours; respect maternal figures.",
        "அமைதியுடன் முடிவெடுக்கவும்; மாலை நேரத்தில் உணர்ச்சிவசப்படுவதைத் தவிர்க்கவும்; தாயாரின் ஆசி பெறவும்."
    ),
    "Mars": (
        "Channel high physical energy into disciplined work; avoid road haste and sharp verbal reactions.",
        "வேகத்தை விவேகமாகப் பயன்படுத்தவும்; அவசர பயணங்கள் மற்றும் சூடான வாக்குவாதங்களைத் தவிர்க்கவும்."
    ),
    "Mercury": (
        "Ideal for clear written communication, accounts reconciliation, and closing pending negotiations.",
        "கணக்குகள் மற்றும் முக்கிய ஆவணங்களை சரிபார்க்கவும்; எழுத்துப்பூர்வ தகவல் பரிமாற்றம் நன்மை தரும்."
    ),
    "Jupiter": (
        "Seek counsel from mentors or elders; auspicious for investments and ethical decision-making.",
        "பெரியோர்கள் அல்லது குருவின் ஆலோசனை பெறவும்; சுப மற்றும் நிதி சார்ந்த காரியங்களுக்கு உகந்தது."
    ),
    "Venus": (
        "Fosters harmonious interpersonal relations, creative expression, and mutually rewarding deals.",
        "பேச்சுவார்த்தைகளில் நிதானம் மற்றும் இனிமை காக்கவும்; கலை மற்றும் கூட்டாண்மை பணிகளுக்கு சிறந்தது."
    ),
    "Saturn": (
        "Embrace patience, meticulous attention to detail, and assist people who serve or assist you.",
        "பொறுமையும் விடாமுயற்சியும் கைகொடுக்கும்; வேலை ஆட்களிடம் கனிவாக நடப்பது தடையை நீக்கும்."
    ),
    "Rahu": (
        "Double-check digital transactions and contracts; avoid speculative risks or impulsive leaps.",
        "ஆன்லைன் பணப்பரிவர்த்தனைகளில் விழிப்புணர்வு தேவை; அவசர ஊக முதலீடுகளைத் தவிர்க்கவும்."
    ),
    "Ketu": (
        "Spend a few minutes in mindful introspection; trust intuition on spiritual and research tasks.",
        "தியானம் மற்றும் ஆன்மீக சிந்தனைக்கு நேரம் ஒதுக்குங்கள்; உள்ளுணர்வு வழிகாட்டுதலைப் பின்பற்றவும்."
    ),
}


def _calc_house_relative(sign_idx: int, ref_rashi_idx: int) -> int:
    """Calculates house number (1-12) of sign_idx relative to ref_rashi_idx."""
    return ((sign_idx - ref_rashi_idx) % 12) + 1


def _get_planet_signified_houses(
    planet_name: str,
    planet_lon: float,
    ref_rashi_idx: int,
    planet_positions: Dict[str, float],
) -> Tuple[Set[int], str, str]:
    """Calculates the houses signified by a planet for a reference Rashi under KP rules:
    - Planet yields results of its STAR LORD (Occupied house + Owned houses of Star Lord)
    - Planet also signifies its own occupied and owned houses
    - SUB LORD qualifies the outcome
    """
    p_info = point_info(planet_lon)
    star_lord = p_info.star_lord
    sub_lord = p_info.sub_lord

    signified: Set[int] = set()

    # 1. Star Lord's Placement and Lordships
    if star_lord in planet_positions:
        sl_lon = planet_positions[star_lord]
        sl_sign_idx = int(sl_lon // 30.0) + 1
        signified.add(_calc_house_relative(sl_sign_idx, ref_rashi_idx))
    for s_name in SIGNS_RULED_BY.get(star_lord, ()):
        s_idx = SIGNS.index(s_name) + 1
        signified.add(_calc_house_relative(s_idx, ref_rashi_idx))

    # 2. Planet's own Placement and Lordships
    p_sign_idx = int(planet_lon // 30.0) + 1
    signified.add(_calc_house_relative(p_sign_idx, ref_rashi_idx))
    for s_name in SIGNS_RULED_BY.get(planet_name, ()):
        s_idx = SIGNS.index(s_name) + 1
        signified.add(_calc_house_relative(s_idx, ref_rashi_idx))

    return signified, star_lord, sub_lord


def _score_aspect(
    active_houses: Set[int],
    benefic_houses: Set[int],
    malefic_houses: Set[int],
    base_weight: float = 1.0,
) -> Tuple[int, float, str]:
    """Scores an aspect between 0-100 and computes stars (1.0 to 5.0) and status."""
    benefic_matches = active_houses.intersection(benefic_houses)
    malefic_matches = active_houses.intersection(malefic_houses)

    # Base baseline is 50
    score = 50.0 + (len(benefic_matches) * 16.0) - (len(malefic_matches) * 14.0)
    score = max(15.0, min(95.0, score * base_weight))
    final_score = int(round(score))

    stars = round(1.0 + (final_score / 100.0) * 4.0, 1)

    if final_score >= 78:
        status = "Excellent"
    elif final_score >= 62:
        status = "Favorable"
    elif final_score >= 46:
        status = "Mixed"
    else:
        status = "Challenging"

    return final_score, stars, status


def _build_career_prediction(
    rashi_name_en: str,
    rashi_name_ta: str,
    score: int,
    status: str,
    houses: List[int],
    sub_lord: str,
) -> Tuple[str, str, str, str]:
    """Builds career aspect insights in English and Tamil."""
    if status == "Excellent":
        en = f"Major planetary support for professional progress. Active KP houses {houses} indicate strong backing from superiors, success in ongoing negotiations, and potential advancement."
        ta = f"தொழில் மற்றும் உத்தியோகத்தில் மிகச் சிறந்த முன்னேற்றம். KP பாவகங்கள் {houses} சாதகமாக உள்ளதால் அதிகாரிகளின் ஆதரவு, வியாபார விரிவு மற்றும் பணிகளில் வெற்றி கிட்டும்."
        rec_en = "Seize initiative on critical projects; schedule high-stakes pitches and client meetings today."
        rec_ta = "முக்கியமான புதிய முயற்சிகள் மற்றும் கூட்டாண்மை பேச்சுவார்த்தைகளை தைரியமாக முன்னெடுக்கலாம்."
    elif status == "Favorable":
        en = f"Steady and constructive workday. With houses {houses} activated under {sub_lord}'s sub, routine tasks proceed smoothly without roadblocks."
        ta = f"பணிகளில் நிலையான சாதகமான சூழல் நிலவும். {sub_lord} உப-அதிபதியின் ஆதிக்கத்தால் தடைப்பட்ட வேலைகள் சுமுகமாக நிறைவேறும்."
        rec_en = "Focus on closing pending deliverables and organizing tomorrow's pipeline."
        rec_ta = "நிலுவையில் உள்ள பணிகளை முடிப்பதில் கவனம் செலுத்துங்கள்; புதிய திட்டங்களை திட்டமிடுங்கள்."
    elif status == "Mixed":
        en = f"Work demands extra tact and patience. House influences suggest mixed signals from team members and mild workload surges."
        ta = f"வேலைச்சுமை சற்று கூடும்; சக ஊழியர்களிடம் நிதானத்தைக் கடைப்பிடிப்பது நல்லது."
        rec_en = "Stick to established protocols; avoid taking unilateral workplace decisions."
        rec_ta = "அலுவலக விவாதங்களில் அமைதி காக்கவும்; மேலதிகாரிகளின் வழிகாட்டுதலைப் பின்பற்றவும்."
    else:
        en = f"Challenging transit alignment. Influences on houses 8 or 12 require caution against misunderstandings and office politics."
        ta = f"பணியிடத்தில் விழிப்புணர்வு தேவை. 8 அல்லது 12-ம் பாவக தாக்கத்தால் தேவையற்ற அலைச்சல் அல்லது கருத்து வேறுபாடு ஏற்படலாம்."
        rec_en = "Postpone performance reviews or sensitive confrontations; keep communications strictly written."
        rec_ta = "வாக்குவாதங்களைத் தவிர்த்து அமைதி காக்கவும்; அவசர முடிவுகளை ஒத்திவைக்கவும்."

    return en, ta, rec_en, rec_ta


def _build_finance_prediction(
    rashi_name_en: str,
    rashi_name_ta: str,
    score: int,
    status: str,
    houses: List[int],
    sub_lord: str,
) -> Tuple[str, str, str, str]:
    """Builds finance aspect insights in English and Tamil."""
    if status in ("Excellent", "Favorable"):
        en = f"Promising financial trajectory. Inflow houses {houses} support clearance of pending dues, business profits, and smart budget allocations."
        ta = f"பணவரவு திருப்திகரமாக இருக்கும். {houses}-ம் பாவகங்கள் பலப்படுவதால் பழைய பாக்கிகள் வசூலாக வாய்ப்புள்ளது; நிதி நிலை உயரும்."
        rec_en = "Favorable for recovering outstanding payments or planning strategic savings."
        rec_ta = "வர வேண்டிய பாக்கிகளை வசூலிக்க முயற்சி செய்யவும்; சேமிப்பைத் திட்டமிட உகந்த நாள்."
    elif status == "Mixed":
        en = f"Balanced cash flow. Normal earnings balanced by household or family obligations. KP houses {houses} advise measured spending."
        ta = f"வரவும் செலவும் சமமாக இருக்கும். குடும்ப தேவைகளுக்காக சிறு விரயங்கள் ஏற்படலாம்."
        rec_en = "Differentiate strictly between essential needs and luxury indulgences."
        rec_ta = "அத்தியாவசியத் தேவைகளுக்கு மட்டும் செலவிடவும்; தேவையற்ற வாங்குதல்களைத் தவிர்க்கவும்."
    else:
        en = f"Heightened fiscal sensitivity. Houses 8 and 12 indicate sudden outflows or impulse purchases."
        ta = f"எதிர்பாராத செலவுகள் ஏற்படக்கூடும். பண விஷயங்களில் எச்சரிக்கையும் சேமிப்பில் கவனமும் தேவை."
        rec_en = "Avoid lending, borrowing, or speculative trading today."
        rec_ta = "கடன் கொடுப்பது, வாங்குவது மற்றும் பங்குச் சந்தை ஊகங்களைத் தவிர்க்கவும்."

    return en, ta, rec_en, rec_ta


def _build_love_prediction(
    rashi_name_en: str,
    rashi_name_ta: str,
    score: int,
    status: str,
    houses: List[int],
    sub_lord: str,
) -> Tuple[str, str, str, str]:
    """Builds love & relationship aspect insights in English and Tamil."""
    if status in ("Excellent", "Favorable"):
        en = f"Heartwarming harmony with partner and family. Connecting houses {houses} foster mutual warmth, affectionate conversations, and joyful moments."
        ta = f"குடும்பத்திலும் தம்பதியர் இடையேயும் மகிழ்ச்சியும் ஒற்றுமையும் பெருகும். {houses}-ம் பாவக ஆதரவால் புரிதல் கூடும்."
        rec_en = "Express appreciation openly; plan an evening together or family gathering."
        rec_ta = "குடும்பத்தினருடன் மனம் திறந்து பேசி மகிழ்ச்சியைப் பகிர்ந்து கொள்ளுங்கள்."
    elif status == "Mixed":
        en = f"Stable emotional ground, though minor difference of opinions may arise regarding domestic responsibilities."
        ta = f"குடும்பத்தில் சிறு கருத்து வேறுபாடுகள் வரலாம்; விட்டுக் கொடுத்துச் செல்வது அமைதியைத் தரும்."
        rec_en = "Listen attentively without becoming defensive; accommodate each other's pace."
        rec_ta = "துணையின் கருத்துக்கு மதிப்பு கொடுங்கள்; தேவையற்ற பிடிவாதத்தைத் தவிர்க்கவும்."
    else:
        en = f"Emotional friction possible. With houses 6 or 8 active, words can be easily misinterpreted."
        ta = f"உணர்ச்சிவசப்படுவதைத் தவிர்க்கவும். பேச்சில் நிதானம் காப்பது உறவை சுமுகமாக வைத்திருக்கும்."
        rec_en = "Avoid discussing sensitive past grievances today; give space when tensions rise."
        rec_ta = "பழைய கசப்பான விஷயங்களைப் பேச வேண்டாம்; அமைதியான அணுகுமுறை நலம் பயக்கும்."

    return en, ta, rec_en, rec_ta


def _build_health_prediction(
    rashi_name_en: str,
    rashi_name_ta: str,
    score: int,
    status: str,
    houses: List[int],
    sub_lord: str,
) -> Tuple[str, str, str, str]:
    """Builds health & vitality aspect insights in English and Tamil."""
    if status in ("Excellent", "Favorable"):
        en = f"High physical stamina and mental optimism. Houses {houses} enhance immunity and prompt quick recovery from any fatigue."
        ta = f"உடல் ஆரோக்கியமும் மன உற்சாகமும் நிறைந்திருக்கும். சுறுசுறுப்புடன் செயல்பட்டு அன்றாட பணிகளை விரைந்து முடிப்பீர்கள்."
        rec_en = "Maintain hydration and an active fitness routine."
        rec_ta = "போதுமான தண்ணீர் பருகவும்; உடற்பயிற்சி மற்றும் யோகாவைத் தொடரவும்."
    elif status == "Mixed":
        en = f"Moderate energy reserves. Mental overactivity or screen strain might cause mild lethargy by dusk."
        ta = f"உடல் உழைப்பால் மாலை நேரத்தில் சிறு அசதி ஏற்படலாம். உணவுக் கட்டுப்பாடு தேவை."
        rec_en = "Take intermittent screen breaks; adhere to disciplined meal timings."
        rec_ta = "நேரத்திற்கு சத்தான உணவு உண்ணவும்; தகுந்த ஓய்வு எடுத்துக் கொள்ளவும்."
    else:
        en = f"Stress vulnerability noted under houses 6 or 8. Guard against digestive sensitivity and sleep disruption."
        ta = f"உடல்நலத்தில் சிறு உபாதைகள் (அஜீரணம், தலைவலி) வரக்கூடும். அலைச்சலைக் குறைப்பது நல்லது."
        rec_en = "Avoid oily/spicy outside food; practice calming breathing exercises."
        rec_ta = "எண்ணெய் உணவுகளைத் தவிர்க்கவும்; போதுமான உறக்கம் மற்றும் ஓய்வு அவசியம்."

    return en, ta, rec_en, rec_ta


def _build_travel_prediction(
    rashi_name_en: str,
    rashi_name_ta: str,
    score: int,
    status: str,
    houses: List[int],
    sub_lord: str,
) -> Tuple[str, str, str, str]:
    """Builds travel & studies aspect insights in English and Tamil."""
    if status in ("Excellent", "Favorable"):
        en = f"Fruitful movements and clear mental focus. Houses {houses} favor academic success, insightful research, and smooth short journeys."
        ta = f"பயணங்கள் அனுகூலமாக அமையும். கல்வி மற்றும் புதிய விஷயங்களைக் கற்றுக்கொள்வதில் மனம் எளிதில் ஈடுபடும்."
        rec_en = "Great for submitting assignments, attending seminars, or finalizing trip plans."
        rec_ta = "தேர்வுகள், நேர்காணல்கள் மற்றும் குறுகிய தூர பயணங்கள் நல்ல பலன் தரும்."
    elif status == "Mixed":
        en = f"Ordinary travel and academic flow. Check schedules and transport timings in advance."
        ta = f"வழக்கமான பயணங்கள்; புறப்படும் முன் வாகனங்கள் மற்றும் நேரத்தை சரிபார்த்துக் கொள்ளவும்."
        rec_en = "Leave early to cushion against minor traffic or schedule bottlenecks."
        rec_ta = "பயணத்தின் போது அவசரத்தைத் தவிர்க்க முன் கூட்டியே புறப்படவும்."
    else:
        en = f"Delays or fatigue on the road indicated by houses 8/12. Concentration may waver."
        ta = f"பயணங்களில் காலதாமதம் ஏற்படலாம்; படிப்பில் கவனச்சிதறல் ஏற்படாமல் பார்த்துக் கொள்ளவும்."
        rec_en = "Postpone non-essential long travel; keep emergency vehicle checks."
        rec_ta = "தேவையற்ற தூரப் பயணங்களைத் தவிர்க்கவும்; கவனமாக வாகனம் ஓட்டவும்."

    return en, ta, rec_en, rec_ta


def _sample_moon_transit_day(
    target_date: date,
    tz_obj: ZoneInfo,
    ayanamsa_id: int,
) -> List[Dict[str, Any]]:
    """Samples the Moon's position across the 24-hour day to record Sub-Lord transitions."""
    samples: List[Dict[str, Any]] = []
    step_minutes = 20
    sample_count = 72

    for i in range(sample_count):
        t_minute = i * step_minutes
        h = t_minute // 60
        m = t_minute % 60
        sample_dt = datetime.combine(target_date, time(h, m), tzinfo=tz_obj)
        _, _, jd, _, _ = resolve_birth_datetime(target_date, time(h, m), str(tz_obj))

        pos = xalen.planet_position(jd, PLANET_IDS["Moon"], True, ayanamsa_id)
        lon = pos["longitude"]
        p_info = point_info(lon)

        samples.append({
            "time_str": sample_dt.strftime("%I:%M %p"),
            "sub_lord": p_info.sub_lord,
            "star_lord": p_info.star_lord,
            "star_name": p_info.star,
        })
    return samples


def _generate_moon_sub_windows(
    moon_samples: List[Dict[str, Any]],
    ref_rashi_idx: int,
    planet_positions: Dict[str, float],
) -> List[MoonSubLordWindow]:
    """Builds Moon Sub-Lord hourly windows with sentiment and advice from precomputed samples."""
    windows: List[MoonSubLordWindow] = []
    current_segment: Optional[Dict[str, Any]] = None

    for sample in moon_samples:
        time_str = sample["time_str"]
        sub_l = sample["sub_lord"]
        star_l = sample["star_lord"]
        star_n = sample["star_name"]

        if current_segment is None:
            current_segment = {
                "start_time": time_str,
                "end_time": time_str,
                "sub_lord": sub_l,
                "star_lord": star_l,
                "star_name": star_n,
            }
        elif current_segment["sub_lord"] != sub_l or current_segment["star_name"] != star_n:
            current_segment["end_time"] = time_str
            windows.append(_build_window_entry(current_segment, ref_rashi_idx, planet_positions))
            current_segment = {
                "start_time": time_str,
                "end_time": time_str,
                "sub_lord": sub_l,
                "star_lord": star_l,
                "star_name": star_n,
            }

    if current_segment:
        current_segment["end_time"] = "11:59 PM"
        windows.append(_build_window_entry(current_segment, ref_rashi_idx, planet_positions))

    return windows


def _build_window_entry(
    seg: Dict[str, Any],
    ref_rashi_idx: int,
    planet_positions: Dict[str, float],
) -> MoonSubLordWindow:
    """Builds a MoonSubLordWindow object from segment data."""
    sub_l = seg["sub_lord"]
    star_l = seg["star_lord"]
    star_n = seg["star_name"]

    # Calculate houses signified by this sub-lord for this Rashi
    signified: Set[int] = set()
    if sub_l in planet_positions:
        sl_lon = planet_positions[sub_l]
        sl_sign = int(sl_lon // 30.0) + 1
        signified.add(_calc_house_relative(sl_sign, ref_rashi_idx))
    for s_name in SIGNS_RULED_BY.get(sub_l, ()):
        s_idx = SIGNS.index(s_name) + 1
        signified.add(_calc_house_relative(s_idx, ref_rashi_idx))

    houses_list = sorted(list(signified))

    # Evaluate sentiment
    favorable_houses = {1, 2, 3, 5, 10, 11}
    challenging_houses = {6, 8, 12}

    fav_hits = signified.intersection(favorable_houses)
    chal_hits = signified.intersection(challenging_houses)

    if len(fav_hits) >= 2 and len(chal_hits) == 0:
        sentiment = "golden"
        adv_en = f"Auspicious window under {sub_l} sub. Ideal for deals, money recovery, and crucial talks."
        adv_ta = f"{sub_l} உப-அதிபதி ஆதிக்கம் உள்ள பொன்னான நேரம். சுப காரியங்கள் மற்றும் பேச்சுவார்த்தைக்கு உகந்தது."
    elif len(chal_hits) >= 2 or (8 in signified and 12 in signified):
        sentiment = "caution"
        adv_en = f"Caution window under {sub_l} sub activating houses {houses_list}. Avoid heated debates and hasty expense."
        adv_ta = f"{sub_l} உப-அதிபதி ஆதிக்க நேரம். விவாதங்கள் மற்றும் அவசர செலவுகளைத் தவிர்ப்பது நல்லது."
    else:
        sentiment = "neutral"
        adv_en = f"Balanced window. Favorable for routine and systematic execution of tasks."
        adv_ta = f"சாதாரண நேரம். அன்றாட பணிகளை சீராக செய்து முடிக்க ஏற்றது."

    return MoonSubLordWindow(
        start_time=seg["start_time"],
        end_time=seg["end_time"],
        star_name=star_n,
        star_lord=star_l,
        sub_lord=sub_l,
        sentiment=sentiment,
        activated_houses=houses_list,
        advice_en=adv_en,
        advice_ta=adv_ta,
    )


def compute_kp_daily_horoscope(
    target_date: Optional[date | str] = None,
    timezone_str: str = "Asia/Kolkata",
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    rashi_filter: Optional[str] = "all",
    ayanamsa_id: int = 1,  # 1 = Krishnamurti KP
) -> KpDailyHoroscopeResponse:
    """Computes comprehensive KP daily predictions for requested or all 12 Rashis."""
    # 1. Parse date
    tz_clean = timezone_str.strip() if timezone_str else "Asia/Kolkata"
    try:
        tz_obj = ZoneInfo(tz_clean)
    except Exception:
        tz_obj = ZoneInfo("Asia/Kolkata")

    now_local = datetime.now(tz_obj)
    if target_date is None:
        calc_date = now_local.date()
    elif isinstance(target_date, str):
        calc_date = datetime.strptime(target_date.strip(), "%Y-%m-%d").date()
    else:
        calc_date = target_date

    # 2. Weekday and Day Lord
    weekday_idx = calc_date.weekday()  # Monday is 0, Sunday is 6
    day_name_en, day_name_ta, day_lord = WEEKDAY_INFO[weekday_idx]

    # 3. Calculate noon JD for planetary transit baseline
    noon_time = time(12, 0, 0)
    _, _, noon_jd, _, _ = resolve_birth_datetime(calc_date, noon_time, str(tz_obj))

    # Planetary positions at noon
    planet_positions: Dict[str, float] = {}
    for p_name, p_id in PLANET_IDS.items():
        pos = xalen.planet_position(noon_jd, p_id, True, ayanamsa_id)
        planet_positions[p_name] = pos["longitude"]

    # Midday Moon KP Breakdown
    moon_info = point_info(planet_positions["Moon"])
    moon_sign_noon = moon_info.sign
    moon_star_noon = moon_info.star
    moon_sub_noon = moon_info.sub_lord

    aya_name = AYANAMSA_NAMES.get(ayanamsa_id, ("KP", ""))[0]

    # Precompute Moon's Sub-Lord transit samples once for the day
    moon_samples = _sample_moon_transit_day(calc_date, tz_obj, ayanamsa_id)

    # 4. Resolve Rashis to evaluate
    rashis_to_calc: List[int] = []
    if not rashi_filter or str(rashi_filter).strip().lower() in ("all", "0", ""):
        rashis_to_calc = list(range(1, 13))
    elif str(rashi_filter).strip().isdigit():
        r_num = int(str(rashi_filter).strip())
        if 1 <= r_num <= 12:
            rashis_to_calc = [r_num]
        else:
            rashis_to_calc = list(range(1, 13))
    else:
        clean_name = str(rashi_filter).strip().capitalize()
        matched = SIGN_TO_INDEX.get(clean_name, None)
        if matched:
            rashis_to_calc = [matched]
        else:
            rashis_to_calc = list(range(1, 13))

    predictions: List[RashiDailyPrediction] = []

    for r_idx in rashis_to_calc:
        r_en, r_ta, sign_lord = RASHI_METADATA[r_idx]

        # Evaluate houses signified by all planets relative to r_idx
        all_active_houses: Set[int] = set()
        planet_signified_map: Dict[str, Set[int]] = {}

        for p_name, p_lon in planet_positions.items():
            sig_houses, sl, sb = _get_planet_signified_houses(p_name, p_lon, r_idx, planet_positions)
            planet_signified_map[p_name] = sig_houses
            all_active_houses.update(sig_houses)

        # Evaluate the 5 Core Aspects
        # 1. Career (2, 6, 10, 11 vs 5, 8, 12)
        career_active = all_active_houses.intersection({2, 5, 6, 8, 10, 11, 12})
        c_score, c_stars, c_status = _score_aspect(career_active, {2, 6, 10, 11}, {5, 8, 12})
        c_en, c_ta, c_rec_en, c_rec_ta = _build_career_prediction(r_en, r_ta, c_score, c_status, sorted(list(career_active)), moon_sub_noon)
        career_aspect = KpAspectPrediction(
            aspect_code="career",
            aspect_name="Career & Profession",
            aspect_name_tamil="தொழில் & உத்தியோகம்",
            score=c_score,
            rating_stars=c_stars,
            status=c_status,
            signified_houses=sorted(list(career_active)),
            insight_en=c_en,
            insight_ta=c_ta,
            key_recommendation_en=c_rec_en,
            key_recommendation_ta=c_rec_ta,
        )

        # 2. Finance (2, 6, 11 vs 5, 8, 12)
        finance_active = all_active_houses.intersection({2, 5, 6, 8, 11, 12})
        f_score, f_stars, f_status = _score_aspect(finance_active, {2, 6, 11}, {5, 8, 12})
        f_en, f_ta, f_rec_en, f_rec_ta = _build_finance_prediction(r_en, r_ta, f_score, f_status, sorted(list(finance_active)), moon_sub_noon)
        finance_aspect = KpAspectPrediction(
            aspect_code="finance",
            aspect_name="Wealth & Finance",
            aspect_name_tamil="தனம் & பணவரவு",
            score=f_score,
            rating_stars=f_stars,
            status=f_status,
            signified_houses=sorted(list(finance_active)),
            insight_en=f_en,
            insight_ta=f_ta,
            key_recommendation_en=f_rec_en,
            key_recommendation_ta=f_rec_ta,
        )

        # 3. Love & Family (2, 5, 7, 11 vs 6, 8, 12)
        love_active = all_active_houses.intersection({2, 5, 6, 7, 8, 11, 12})
        l_score, l_stars, l_status = _score_aspect(love_active, {2, 5, 7, 11}, {6, 8, 12})
        l_en, l_ta, l_rec_en, l_rec_ta = _build_love_prediction(r_en, r_ta, l_score, l_status, sorted(list(love_active)), moon_sub_noon)
        love_aspect = KpAspectPrediction(
            aspect_code="love",
            aspect_name="Love & Family",
            aspect_name_tamil="குடும்பம் & உறவுகள்",
            score=l_score,
            rating_stars=l_stars,
            status=l_status,
            signified_houses=sorted(list(love_active)),
            insight_en=l_en,
            insight_ta=l_ta,
            key_recommendation_en=l_rec_en,
            key_recommendation_ta=l_rec_ta,
        )

        # 4. Health & Vitality (1, 11 vs 6, 8, 12)
        health_active = all_active_houses.intersection({1, 6, 8, 11, 12})
        h_score, h_stars, h_status = _score_aspect(health_active, {1, 11}, {6, 8, 12})
        h_en, h_ta, h_rec_en, h_rec_ta = _build_health_prediction(r_en, r_ta, h_score, h_status, sorted(list(health_active)), moon_sub_noon)
        health_aspect = KpAspectPrediction(
            aspect_code="health",
            aspect_name="Health & Vitality",
            aspect_name_tamil="உடல்நலம் & உற்சாகம்",
            score=h_score,
            rating_stars=h_stars,
            status=h_status,
            signified_houses=sorted(list(health_active)),
            insight_en=h_en,
            insight_ta=h_ta,
            key_recommendation_en=h_rec_en,
            key_recommendation_ta=h_rec_ta,
        )

        # 5. Travel & Studies (3, 4, 9, 11 vs 8, 12)
        travel_active = all_active_houses.intersection({3, 4, 8, 9, 11, 12})
        t_score, t_stars, t_status = _score_aspect(travel_active, {3, 4, 9, 11}, {8, 12})
        t_en, t_ta, t_rec_en, t_rec_ta = _build_travel_prediction(r_en, r_ta, t_score, t_status, sorted(list(travel_active)), moon_sub_noon)
        travel_aspect = KpAspectPrediction(
            aspect_code="travel",
            aspect_name="Travel & Studies",
            aspect_name_tamil="பயணம் & கல்வி",
            score=t_score,
            rating_stars=t_stars,
            status=t_status,
            signified_houses=sorted(list(travel_active)),
            insight_en=t_en,
            insight_ta=t_ta,
            key_recommendation_en=t_rec_en,
            key_recommendation_ta=t_rec_ta,
        )

        aspect_list = [career_aspect, finance_aspect, love_aspect, health_aspect, travel_aspect]

        # Overall Day Score & Sentiment
        daily_score = int(round((c_score * 0.3) + (f_score * 0.25) + (l_score * 0.2) + (h_score * 0.15) + (t_score * 0.1)))
        daily_rating_stars = round(1.0 + (daily_score / 100.0) * 4.0, 1)

        if daily_score >= 76:
            day_sentiment = "Excellent"
        elif daily_score >= 60:
            day_sentiment = "Favorable"
        elif daily_score >= 45:
            day_sentiment = "Mixed"
        else:
            day_sentiment = "Challenging"

        # Generate Moon Sub-Lord hourly windows
        sub_windows = _generate_moon_sub_windows(moon_samples, r_idx, planet_positions)

        golden_wins = [w for w in sub_windows if w.sentiment == "golden"]
        caution_wins = [w for w in sub_windows if w.sentiment == "caution"]

        golden_str = f"{golden_wins[0].start_time} - {golden_wins[0].end_time}" if golden_wins else "10:30 AM - 12:45 PM"
        caution_str = f"{caution_wins[0].start_time} - {caution_wins[0].end_time}" if caution_wins else "04:30 PM - 06:00 PM"

        # Construct Daily Executive Brief Statement
        if day_sentiment == "Excellent":
            brief_en = f"A powerful and high-momentum day for {r_en} natives. Active KP significators strongly boost professional negotiations, financial gains, and recognition."
            brief_ta = f"{r_ta} ராசிக்கு இன்று புதிய வெற்றிகளையும் பணவரவையும் தரும் சிறப்பான நாள். முக்கிய முயற்சிகளை தைரியமாக முன்னெடுக்கலாம்."
            peak_en = f"Peak planetary alignment activates houses {c_status} with Moon transit, making the morning window ideal for career and money triumphs."
            peak_ta = f"சந்திரனின் உப-அதிபதி சாதகமாக இருப்பதால் காலையில் எடுக்கப்படும் நிதி மற்றும் தொழில் முயற்சிகளில் எதிர்பாராத லாபம் கிட்டும்."
            caution_en = "Avoid complacency; ensure all verbal agreements are formally documented."
            caution_ta = "அலட்சியத்தைத் தவிர்க்கவும்; நிதி விவகாரங்களை முறையாகக் கையாளவும்."
        elif day_sentiment == "Favorable":
            brief_en = f"A constructive and steady day ahead for {r_en}. Tasks flow smoothly with favorable support from peers and financial stability."
            brief_ta = f"{r_ta} ராசிக்கு இன்று மனநிறைவும் நற்பலன்களும் தரும் சுமுகமான நாள். நிலுவைப் பணிகள் எளிதாக முடியும்."
            peak_en = f"Harmonious house activations favor strategic meetings, family conversations, and completing pending tasks."
            peak_ta = f"பணிகள் தடையின்றி நடக்கும்; சுப விசேஷங்கள் மற்றும் குடும்ப உறவுகளில் மகிழ்ச்சி நிலவும்."
            caution_en = "Be mindful of minor timing delays during the afternoon transit change."
            caution_ta = "மதிய நேரத்தில் சிறு காலதாமதங்கள் வரலாம்; திட்டமிட்டு செயல்படவும்."
        elif day_sentiment == "Mixed":
            brief_en = f"A moderately paced day calling for patience and balanced priorities for {r_en}. Maintain a calm demeanor amid shifting workloads."
            brief_ta = f"{r_ta} ராசிக்கு இன்று நிதானமும் பொறுமையும் தேவைப்படும் நாள். வரவுக்கு ஏற்ற செலவுகள் இருக்கும்."
            peak_en = "Creative focus and independent research yield positive breakthroughs."
            peak_ta = "தனிப்பட்ட பணிகளிலும் சிந்தனைகளிலும் புதிய தெளிவு பிறக்கும்."
            caution_en = "Refrain from heated arguments or impulsive expenditures during caution hours."
            caution_ta = "வாக்குவாதங்களை தவிர்க்கவும்; தேவையற்ற விரயங்களில் கவனம் தேவை."
        else:
            brief_en = f"A demanding day requiring extra vigilance and tact for {r_en}. Keep expectations realistic and prioritize health and tranquility."
            brief_ta = f"{r_ta} ராசிக்கு இன்று விழிப்புணர்வுடன் செயல்பட வேண்டிய நாள். புதிய காரியங்களைத் தள்ளிப்போடுவது நல்லது."
            peak_en = "Good day for quiet introspective tasks, spiritual grounding, and restructuring routine habits."
            peak_ta = "தியானம், இறை வழிபாடு மற்றும் அன்றாட கடமைகளை அமைதியாக முடிப்பதற்கு உகந்தது."
            caution_en = f"Vulnerable window active between {caution_str}; strictly defer major investments or signing documents."
            caution_ta = f"{caution_str} நேரத்தில் முக்கியமான ஒப்பந்தங்கள் மற்றும் புதிய முயற்சிகளைத் தவிர்க்கவும்."

        # Lucky attributes based on dominant favorable lord or day lord
        dominant_lord = moon_sub_noon if moon_sub_noon in LUCKY_ATTRIBUTES else day_lord
        lucky_attr = LUCKY_ATTRIBUTES.get(dominant_lord, LUCKY_ATTRIBUTES["Jupiter"])
        remedy_pair = KP_DAILY_REMEDIES.get(dominant_lord, KP_DAILY_REMEDIES["Jupiter"])

        pred = RashiDailyPrediction(
            rashi_id=r_idx,
            rashi_name_en=r_en,
            rashi_name_ta=r_ta,
            sign_lord=sign_lord,
            daily_score=daily_score,
            daily_rating_stars=daily_rating_stars,
            day_sentiment=day_sentiment,
            brief_statement_en=brief_en,
            brief_statement_ta=brief_ta,
            peak_highlight_en=peak_en,
            peak_highlight_ta=peak_ta,
            caution_trap_en=caution_en,
            caution_trap_ta=caution_ta,
            golden_hour_window=golden_str,
            caution_hour_window=caution_str,
            lucky_color_en=lucky_attr["color_en"],
            lucky_color_ta=lucky_attr["color_ta"],
            lucky_number=lucky_attr["num"],
            lucky_direction_en=lucky_attr["dir_en"],
            lucky_direction_ta=lucky_attr["dir_ta"],
            daily_remedy_en=remedy_pair[0],
            daily_remedy_ta=remedy_pair[1],
            aspects=aspect_list,
            moon_sub_windows=sub_windows,
        )
        predictions.append(pred)

    return KpDailyHoroscopeResponse(
        date=calc_date.isoformat(),
        day_of_week=day_name_en,
        day_of_week_ta=day_name_ta,
        day_lord=day_lord,
        moon_sign_at_noon=moon_sign_noon,
        moon_star_at_noon=moon_star_noon,
        moon_sub_lord_at_noon=moon_sub_noon,
        ayanamsa_name=aya_name,
        total_rashis=len(predictions),
        predictions=predictions,
        calculated_at=now_local.isoformat(),
    )
