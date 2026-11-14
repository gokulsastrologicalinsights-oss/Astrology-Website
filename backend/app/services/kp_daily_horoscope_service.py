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

MOON_HOUSE_INTERPRETATIONS: Dict[int, Dict[str, str]] = {
    1: {
        "title_en": "Moon in 1st House (Janma Rashi)",
        "title_ta": "1-ம் இடத்தில் சந்திரன் (ஜன்ம ராசி)",
        "brief_en": "High personal vitality, self-confidence, and independent initiatives take center stage. Favorable for personal planning and leadership.",
        "brief_ta": "உற்சாகமும் தன்னம்பிக்கையும் கூடும் நாள். சுயமாக சிந்தித்து எடுக்கும் புதிய முடிவுகள் மற்றும் தனிப்பட்ட திட்டங்கள் வெற்றி பெறும்.",
        "peak_en": "Clarity of vision and inner energy empower you to tackle demanding tasks independently.",
        "peak_ta": "மனதில் புது உற்சாகம் பிறக்கும்; சுயமாக செயல்பட்டு எடுத்த காரியத்தை வெற்றிகரமாக முடிப்பீர்கள்.",
        "caution_en": "Avoid impulsive ego reactions when dealing with colleagues.",
        "caution_ta": "முன்கோபத்தைத் தவிர்த்து நிதானமாகப் பேசுவது சுமுகமான சூழலைத் தரும்.",
    },
    2: {
        "title_en": "Moon in 2nd House (Dhana & Family)",
        "title_ta": "2-ம் இடத்தில் சந்திரன் (தன & குடும்ப ஸ்தானம்)",
        "brief_en": "Strong financial inflows, clearance of pending dues, and pleasant interactions with family members.",
        "brief_ta": "பணப்புழக்கம் சரளமாக இருக்கும்; கொடுக்கல்-வாங்கல் சுமுகமாகும். குடும்பத்தினரிடம் இனிமையான பேச்சு அமைதியைத் தரும்.",
        "peak_en": "Pending receivables or unexpected monetary gains clear up financial bottlenecks.",
        "peak_ta": "வர வேண்டிய பழைய பாக்கிகள் வசூலாகும்; நிதி நிலை கணிசமாக உயரும்.",
        "caution_en": "Weigh your words carefully in domestic conversations to maintain warmth.",
        "caution_ta": "குடும்ப விவகாரங்களில் அடுத்தவர் மனதை புண்படுத்தாமல் பேசவும்.",
    },
    3: {
        "title_en": "Moon in 3rd House (Courage & Movement)",
        "title_ta": "3-ம் இடத்தில் சந்திரன் (தைரிய & முயற்சி ஸ்தானம்)",
        "brief_en": "Favorable for courageous decisions, effective short-distance travel, and successful negotiations.",
        "brief_ta": "தைரியமும் சுறுசுறுப்பும் கூடும் நாள். குறுகிய தூர பயணங்கள், தகவல் பரிமாற்றம் மற்றும் புதிய முயற்சிகள் அனுகூலமாகும்.",
        "peak_en": "Written communications, presentations, and phone deals move forward without resistance.",
        "peak_ta": "பேச்சுவார்த்தைகள் மற்றும் குறுகிய தூர பயணங்களால் புதிய வாய்ப்புகள் திறக்கும்.",
        "caution_en": "Verify travel documents and schedules to prevent minor commuting rush.",
        "caution_ta": "பயணங்களின் போது அவசரப்படாமல் முன் கூட்டியே திட்டமிட்டு புறப்படவும்.",
    },
    4: {
        "title_en": "Moon in 4th House (Home & Happiness)",
        "title_ta": "4-ம் இடத்தில் சந்திரன் (சுக & தாய் ஸ்தானம்)",
        "brief_en": "Domestic joy, support from maternal figures, and satisfaction regarding residence or vehicle matters.",
        "brief_ta": "தாய்வழி ஆதரவும் குடும்பத்தில் மன அமைதியும் நிலவும். வீடு, வாகனம் சார்ந்த விவகாரங்கள் சுமுகமாக முடியும்.",
        "peak_en": "Peaceful atmosphere at home and positive breakthroughs in property or educational tasks.",
        "peak_ta": "குடும்பத்துடன் நேரம் செலவிடவும், வீட்டு உபயோகப் பொருட்கள் வாங்கவும் உகந்தது.",
        "caution_en": "Do not let domestic pre-occupations distract you during business meetings.",
        "caution_ta": "வேலை நேரத்தில் குடும்பக் கவலைகளை ஒதுக்கி வைத்து பணியில் கவனம் செலுத்தவும்.",
    },
    5: {
        "title_en": "Moon in 5th House (Poorva Punya & Intellect)",
        "title_ta": "5-ம் இடத்தில் சந்திரன் (பூர்வ புண்ணிய ஸ்தானம்)",
        "brief_en": "Sharp intellect, joyful communication with children/loved ones, and success in creative pursuits.",
        "brief_ta": "புத்தி கூர்மையும் உள்ளுணர்வும் பளிச்சிடும். கலை, காதல் மற்றும் கல்வி சார்ந்த விஷயங்களில் அனுகூலமான நற்பலன்கள் கிட்டும்.",
        "peak_en": "Intuitive insights and creative problem-solving lead to well-deserved praise.",
        "peak_ta": "கலை மற்றும் புதிய சிந்தனைகளில் வெற்றி; பிள்ளைகள் மூலம் நற்செய்தி கிடைக்கும்.",
        "caution_en": "Avoid highly speculative market gambles; stick to calculated investments.",
        "caution_ta": "ஊக வணிகம் மற்றும் அவசர முதலீடுகளைத் தவிர்த்து நிதானம் காக்கவும்.",
    },
    6: {
        "title_en": "Moon in 6th House (Victory over Hurdles)",
        "title_ta": "6-ம் இடத்தில் சந்திரன் (சத்ரு ஜெய ஸ்தானம்)",
        "brief_en": "Success over workplace competition, loan/debt settlement, and high productivity in routine responsibilities.",
        "brief_ta": "எதிர்ப்புகளையும் போட்டிகளையும் எளிதில் முறியடிக்கும் நாள். நிலுவைக் கடன்கள் வசூலாகும்; வேலைகளில் சுறுசுறுப்பு கூடும்.",
        "peak_en": "Crush competitive bottlenecks and resolve complex pending office assignments.",
        "peak_ta": "போட்டிகள், வழக்குகள் மற்றும் கடன் விவகாரங்களில் சாதகமான தீர்வு கிட்டும்.",
        "caution_en": "Watch your diet and hydration to prevent mild acidity or fatigue.",
        "caution_ta": "நேரத்திற்கு சத்தான உணவு உண்ணவும்; அஜீரண கோளாறுகளில் கவனம் தேவை.",
    },
    7: {
        "title_en": "Moon in 7th House (Partnership & Harmony)",
        "title_ta": "7-ம் இடத்தில் சந்திரன் (களத்திர & கூட்டாண்மை ஸ்தானம்)",
        "brief_en": "Harmony with life partner, fruitful business client meetings, and mutually rewarding social ties.",
        "brief_ta": "கணவன்-மனைவி இடையே அன்யோன்யம் கூடும்; வாடிக்கையாளர்கள் மற்றும் கூட்டாளிகளுடன் சுமுக ஒப்பந்தங்கள் ஏற்படும்.",
        "peak_en": "Collaborative joint ventures and client agreements close smoothly.",
        "peak_ta": "புதிய வாடிக்கையாளர்கள் அறிமுகமாவார்கள்; கூட்டுத் தொழிலில் நல்ல லாபம் உண்டு.",
        "caution_en": "Avoid stubbornness; be willing to meet your counterpart halfway.",
        "caution_ta": "விட்டுக்கொடுத்துச் செல்வது குடும்பத்திலும் தொழிலிலும் ஒற்றுமையை வளர்க்கும்.",
    },
    8: {
        "title_en": "Moon in 8th House (Chandrashtama - Caution)",
        "title_ta": "8-ம் இடத்தில் சந்திரன் (சந்திராஷ்டமம்)",
        "brief_en": "Caution day requiring emotional patience and calm focus. Strictly avoid entering arguments or signing risky new contracts.",
        "brief_ta": "இன்று சந்திராஷ்டமம் உள்ளதால் மன அமைதியும் கூடுதல் விழிப்புணர்வும் அவசியம். புதிய முயற்சிகள், வீண் விவாதங்களைத் தவிர்க்கவும்.",
        "peak_en": "Excellent day for deep meditation, self-introspection, and clearing back-office clutter.",
        "peak_ta": "தியானம், அமைதியான பணிகள் மற்றும் ஆன்மீக வழிபாட்டிற்கு உகந்த நன்னாள்.",
        "caution_en": "Chandrashtama is active: do not lend money, drive cautiously, and defer important signatures.",
        "caution_ta": "சந்திராஷ்டமம்: கடன் கொடுக்கல் வாங்கல் வேண்டாம்; கவனமாக வாகனம் ஓட்டவும்.",
    },
    9: {
        "title_en": "Moon in 9th House (Bhagya & Fortune)",
        "title_ta": "9-ம் இடத்தில் சந்திரன் (பாக்கிய ஸ்தானம்)",
        "brief_en": "Auspicious fortune, guidance from elders or mentors, and rewarding long-distance travel.",
        "brief_ta": "தந்தையார் மற்றும் பெரியோர்களின் ஆசி கிட்டும். தெய்வீக அனுகூலம், சுப பயணங்கள் மற்றும் புண்ணிய காரியங்களில் மனம் ஈடுபடும்.",
        "peak_en": "Divine grace smooths out previous difficulties; luck favors higher studies and pilgrimage.",
        "peak_ta": "தொட்ட காரியங்களில் தெய்வ அருள் துணை நிற்கும்; தொலைதூரப் பயணங்கள் கைகூடும்.",
        "caution_en": "Honor your moral commitments; avoid taking shortcuts on ethics.",
        "caution_ta": "பெரியோர்களின் ஆலோசனைகளை அலட்சியம் செய்யாமல் மதித்து நடக்கவும்.",
    },
    10: {
        "title_en": "Moon in 10th House (Career & Honor)",
        "title_ta": "10-ம் இடத்தில் சந்திரன் (தொழில் & கர்ம ஸ்தானம்)",
        "brief_en": "Peak professional momentum, leadership commendation from superiors, and career advancement.",
        "brief_ta": "உத்தியோகத்தில் மதிப்பு, மரியாதை கூடும் பொன்னான நாள். மேலதிகாரிகளின் பாராட்டு மற்றும் தொழில் வளர்ச்சி கைகூடும்.",
        "peak_en": "High professional standing: take charge of leadership presentations and corporate meetings.",
        "peak_ta": "வேலையில் புதிய பொறுப்புகள் மற்றும் அங்கீகாரம் தேடி வரும்; செல்வாக்கு உயரும்.",
        "caution_en": "Do not neglect family commitments while chasing ambitious deadlines.",
        "caution_ta": "அலுவலக வேலைகளில் மூழ்கி குடும்பத்தினரை புறக்கணிக்க வேண்டாம்.",
    },
    11: {
        "title_en": "Moon in 11th House (Labha & Prosperity)",
        "title_ta": "11-ம் இடத்தில் சந்திரன் (லாப ஸ்தானம்)",
        "brief_en": "Outstanding financial gains, realization of cherished goals, and enthusiastic support from friends.",
        "brief_ta": "தொட்டதெல்லாம் துலங்கும் அதிர்ஷ்டகரமான நாள்! எதிர்பாராத பணவரவு, நட்பு வட்டார ஆதரவு மற்றும் எண்ணங்கள் யாவும் நிறைவேறும்.",
        "peak_en": "Exceptional gains across multiple streams: projects bear fruit and long-awaited news arrives.",
        "peak_ta": "பணவரவு பன்மடங்கு பெருகும்; புதிய ஒப்பந்தங்கள் மூலம் எதிர்பாராத லாபம் கிடைக்கும்.",
        "caution_en": "Invest surplus income wisely rather than spending on ephemeral luxuries.",
        "caution_ta": "வரும் லாபத்தை பயனுள்ள வழிகளில் சேமிக்கவும்; தேவையற்ற ஆடம்பரத்தை தவிர்க்கவும்.",
    },
    12: {
        "title_en": "Moon in 12th House (Expenditure & Peace)",
        "title_ta": "12-ம் இடத்தில் சந்திரன் (விரய ஸ்தானம்)",
        "brief_en": "Subha-vyaya (auspicious expenditures), long journey, and peaceful solitude for spiritual and restful recovery.",
        "brief_ta": "சுப காரியங்களுக்காகவும் குடும்பத்திற்காகவும் சுப விரயங்கள் ஏற்படும். தூரப் பயணங்கள் மற்றும் ஆன்மீக அமைதிக்கு ஏற்ற நாள்.",
        "peak_en": "Ideal for charitable donations, research analysis, foreign connections, and restful sleep.",
        "peak_ta": "சுபச்செலவுகள் ஏற்படும்; ஆன்மீக மற்றும் தர்ம காரியங்களில் மனம் நிறைவு பெறும்.",
        "caution_en": "Strictly monitor expenses; avoid shopping without a fixed budget checklist.",
        "caution_ta": "பட்ஜெட் இன்றி செலவு செய்வதைத் தவிர்க்கவும்; பணப்பரிவர்த்தனையில் கவனம் தேவை.",
    },
}

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

# Canonical Lucky Attributes per Rashi (1: Mesha to 12: Meena)
# Based on Sign Lord, Element (Agni=East, Bhoomi=South, Vayu=West, Jala=North), and Vedic/KP traditions
RASHI_LUCKY_ATTRIBUTES: Dict[int, Dict[str, Any]] = {
    1: {  # Aries / மேஷம் (Lord: Mars, Fire -> East)
        "color_en": "Coral Red & Crimson",
        "color_ta": "பவள சிவப்பு & அடர் சிவப்பு",
        "num": 9,
        "dir_en": "East",
        "dir_ta": "கிழக்கு",
    },
    2: {  # Taurus / ரிஷபம் (Lord: Venus, Earth -> South)
        "color_en": "Pure White & Pastel Blue",
        "color_ta": "தூய வெள்ளை & இளநீலம்",
        "num": 6,
        "dir_en": "South",
        "dir_ta": "தெற்கு",
    },
    3: {  # Gemini / மிதுனம் (Lord: Mercury, Air -> West)
        "color_en": "Emerald Green & Mint",
        "color_ta": "மரகத பச்சை & புதினா",
        "num": 5,
        "dir_en": "West",
        "dir_ta": "மேற்கு",
    },
    4: {  # Cancer / கடகம் (Lord: Moon, Water -> North)
        "color_en": "Pearl White & Silver",
        "color_ta": "முத்து வெள்ளை & வெள்ளி",
        "num": 2,
        "dir_en": "North",
        "dir_ta": "வடக்கு",
    },
    5: {  # Leo / சிம்மம் (Lord: Sun, Fire -> East)
        "color_en": "Ruby Red & Gold",
        "color_ta": "சிவப்பு & பொன் நிறம்",
        "num": 1,
        "dir_en": "East",
        "dir_ta": "கிழக்கு",
    },
    6: {  # Virgo / கன்னி (Lord: Mercury, Earth -> South)
        "color_en": "Emerald Green & Light Grey",
        "color_ta": "மரகத பச்சை & சாம்பல்",
        "num": 5,
        "dir_en": "South",
        "dir_ta": "தெற்கு",
    },
    7: {  # Libra / துலாம் (Lord: Venus, Air -> West)
        "color_en": "Pure White & Pastel Blue",
        "color_ta": "தூய வெள்ளை & இளநீலம்",
        "num": 6,
        "dir_en": "West",
        "dir_ta": "மேற்கு",
    },
    8: {  # Scorpio / விருச்சிகம் (Lord: Mars, Water -> North)
        "color_en": "Deep Red & Maroon",
        "color_ta": "அடர் சிவப்பு & மெரூன்",
        "num": 9,
        "dir_en": "North",
        "dir_ta": "வடக்கு",
    },
    9: {  # Sagittarius / தனுசு (Lord: Jupiter, Fire -> East)
        "color_en": "Golden Yellow & Saffron",
        "color_ta": "தங்க மஞ்சள் & காவி",
        "num": 3,
        "dir_en": "East",
        "dir_ta": "கிழக்கு",
    },
    10: {  # Capricorn / மகரம் (Lord: Saturn, Earth -> South)
        "color_en": "Dark Blue & Charcoal",
        "color_ta": "அடர் நீலம் & சாம்பல்",
        "num": 8,
        "dir_en": "South",
        "dir_ta": "தெற்கு",
    },
    11: {  # Aquarius / கும்பம் (Lord: Saturn, Air -> West)
        "color_en": "Sky Blue & Navy",
        "color_ta": "நீலம் & வான நீலம்",
        "num": 8,
        "dir_en": "West",
        "dir_ta": "மேற்கு",
    },
    12: {  # Pisces / மீனம் (Lord: Jupiter, Water -> North)
        "color_en": "Golden Yellow & Rose",
        "color_ta": "மஞ்சள் & இளஞ்சிவப்பு",
        "num": 3,
        "dir_en": "North",
        "dir_ta": "வடக்கு",
    },
}

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


def _score_aspect_for_rashi(
    aspect_code: str,
    moon_house: int,
    lord_house: int,
    jup_house: int,
    active_houses: Set[int],
) -> Tuple[int, float, str]:
    """Computes realistic, astrologically distinct score for each Rashi aspect."""
    base = 50.0

    if aspect_code == "career":
        # Benefic houses: 10, 11, 6, 2. Malefic: 8, 12, 5
        if moon_house == 10:
            base += 32.0  # Karma Sthana Moon!
        elif moon_house == 11:
            base += 28.0
        elif moon_house == 6:
            base += 20.0
        elif moon_house == 2:
            base += 16.0
        elif moon_house == 8:
            base -= 28.0  # Chandrashtama!
        elif moon_house == 12:
            base -= 20.0
        elif moon_house == 5:
            base -= 10.0
        elif moon_house in (1, 3, 7, 9):
            base += 10.0

        if lord_house in (1, 10, 11, 6):
            base += 8.0
        elif lord_house in (8, 12):
            base -= 8.0

    elif aspect_code == "finance":
        # Benefic: 2, 11, 6. Malefic: 12, 8, 5
        if moon_house == 11:
            base += 35.0  # Labha Sthana Moon!
        elif moon_house == 2:
            base += 30.0  # Dhana Sthana Moon!
        elif moon_house == 6:
            base += 15.0
        elif moon_house == 12:
            base -= 30.0  # Vyaya Sthana Moon!
        elif moon_house == 8:
            base -= 25.0  # Chandrashtama!
        elif moon_house in (1, 5, 9):
            base += 12.0

        if jup_house in (2, 5, 9, 11):
            base += 8.0
        elif jup_house in (6, 8, 12):
            base -= 6.0

    elif aspect_code == "love":
        # Benefic: 7, 2, 5, 11. Malefic: 6, 8, 12
        if moon_house == 7:
            base += 34.0  # Kalathra Sthana Moon!
        elif moon_house == 5:
            base += 28.0  # Romance/Creativity!
        elif moon_house in (2, 11):
            base += 18.0
        elif moon_house in (6, 8):
            base -= 26.0  # Conflict/Chandrashtama
        elif moon_house == 12:
            base -= 16.0
        elif moon_house in (1, 4):
            base += 10.0

    elif aspect_code == "health":
        # Benefic: 1, 11. Malefic: 8, 6, 12
        if moon_house == 8:
            base -= 35.0  # Chandrashtama heavy toll on mental peace & health
        elif moon_house == 6:
            base -= 24.0  # Roga Sthana
        elif moon_house == 12:
            base -= 18.0  # Fatigue/Vyaya
        elif moon_house == 1:
            base += 30.0  # High vitality in Janma
        elif moon_house in (11, 5, 9):
            base += 20.0
        else:
            base += 8.0

        if lord_house in (6, 8, 12):
            base -= 8.0
        else:
            base += 6.0

    elif aspect_code == "travel":
        # Benefic: 3, 9, 4, 11. Malefic: 8, 12
        if moon_house in (3, 9):
            base += 32.0  # Movement / Bhagya
        elif moon_house in (4, 11):
            base += 18.0
        elif moon_house == 8:
            base -= 24.0
        elif moon_house == 12:
            base -= 12.0
        else:
            base += 8.0

    final_score = int(max(20.0, min(96.0, round(base))))
    stars = round(1.0 + (final_score / 100.0) * 4.0, 1)

    if final_score >= 76:
        status = "Excellent"
    elif final_score >= 60:
        status = "Favorable"
    elif final_score >= 45:
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

        # 1. Rashi-relative key house positions
        moon_lon = planet_positions["Moon"]
        moon_sign_idx = int(moon_lon // 30.0) + 1
        moon_house = ((moon_sign_idx - r_idx) % 12) + 1

        lord_lon = planet_positions.get(sign_lord, moon_lon)
        lord_sign_idx = int(lord_lon // 30.0) + 1
        lord_house = ((lord_sign_idx - r_idx) % 12) + 1

        jup_lon = planet_positions.get("Jupiter", 0.0)
        jup_sign_idx = int(jup_lon // 30.0) + 1
        jup_house = ((jup_sign_idx - r_idx) % 12) + 1

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
        c_score, c_stars, c_status = _score_aspect_for_rashi("career", moon_house, lord_house, jup_house, career_active)
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
        f_score, f_stars, f_status = _score_aspect_for_rashi("finance", moon_house, lord_house, jup_house, finance_active)
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
        l_score, l_stars, l_status = _score_aspect_for_rashi("love", moon_house, lord_house, jup_house, love_active)
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
        h_score, h_stars, h_status = _score_aspect_for_rashi("health", moon_house, lord_house, jup_house, health_active)
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
        t_score, t_stars, t_status = _score_aspect_for_rashi("travel", moon_house, lord_house, jup_house, travel_active)
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

        # Construct Dynamic, Rashi-Specific Daily Executive Brief Statement
        m_interp = MOON_HOUSE_INTERPRETATIONS.get(moon_house, MOON_HOUSE_INTERPRETATIONS[1])
        brief_en = f"{r_en} ({m_interp['title_en']}): {m_interp['brief_en']}"
        brief_ta = f"{r_ta} ({m_interp['title_ta']}): {m_interp['brief_ta']}"
        peak_en = m_interp["peak_en"]
        peak_ta = m_interp["peak_ta"]
        caution_en = m_interp["caution_en"]
        caution_ta = m_interp["caution_ta"]

        # Lucky attributes and direction specific to each Rashi
        lucky_attr = RASHI_LUCKY_ATTRIBUTES.get(r_idx, RASHI_LUCKY_ATTRIBUTES[1])
        remedy_pair = KP_DAILY_REMEDIES.get(sign_lord, KP_DAILY_REMEDIES["Jupiter"])

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


# Re-export weekly & monthly calculators for unified service access
from app.services.kp_period_horoscope_service import (
    compute_kp_weekly_horoscope,
    compute_kp_monthly_horoscope,
)
