"""Traditional Tamil Horoscope Writing Engine Calculations.

Implements classical shastra rules for the six-page Tamil horoscope booklet:
- Page 1: நிகழும் ஆண்டு மற்றும் ஜனன விவரங்கள் (Birth particulars, Udayadhi Nazhigai, Ahas, Panchang limbs, Transitions, Vara Yoga)
- Page 2: தினசுத்திப் படலம் (Calendar Eras & Calculations)
- Page 3: உடுமகா திசை (Vimshottari Dasa in Nazhigai & Vinadi, Dasa balance, full timeline)
- Page 4: குறிப்பு (Horoscope classifications, Tree, Animal, Bird, Gana, Rajju, Nadi)
- Page 5: ஸ்ரீ படுபட்சி பலன் (Pancha Pakshi Shastra & Guidelines)
- Page 6: அர்ச்சனை பேப்பரில் பலன் (Archana slip recommendations, Entrance direction, Lucky Day/Color/Stone/Deity)
"""

from datetime import date, time, datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo
import math

import xalen
import xalen.swe as swe

from app.schemas.common import BirthInput
from app.services.muhurta_engine.astronomy import (
    calculate_solar_sunrise_sunset,
    get_nakshatra_at_jd,
    find_nakshatra_transition,
    get_tithi_at_jd,
    find_tithi_transition,
    calculate_varjyam_and_amrita,
    NAKSHATRAS,
    TITHI_TAMIL,
    YOGA_NAMES,
    KARANA_NAMES,
    WEEKDAY_NAMES_TA,
)
from app.services.marriage_engine.models import (
    NAKSHATRA_NAMES_TA,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    NAKSHATRA_GANA,
    NAKSHATRA_RAJJU,
    GanaType,
    RajjuType,
)
from app.services.kp_engine.constants import VIMSHOTTARI_YEARS, VIMSHOTTARI_ORDER
from app.services.horoscope_writing.tamil_calendar import calculate_astronomical_tamil_calendar

# 27 Nakshatras - Traditional Tamil Names (1-indexed)
NAKSHATRA_LIST_TA = [
    "அசுவினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
    "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
    "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
]

# 27 Yogas in Tamil
YOGA_NAMES_TA = [
    "விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்யம்", "சோபனம்", "அதிகண்டம்",
    "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்",
    "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதிபாதம்", "வரியான்",
    "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்ரம்",
    "பிராமியம்", "ஐந்திரம்", "வைதிருதி"
]

# 11 Karanas in Tamil
KARANA_NAMES_TA: Dict[str, str] = {
    "Bava": "பவம்",
    "Balava": "பாலவம்",
    "Kaulava": "கௌலவம்",
    "Taitila": "தைதுலை",
    "Garija": "கரசை",
    "Vanija": "வணிசை",
    "Vishti": "பத்திரை (விஷ்டி)",
    "Shakuni": "சகுனி",
    "Chatushpada": "சதுஷ்பாதம்",
    "Naga": "நாகவம்",
    "Kimstughna": "கிம்ஸ்துக்னம்",
}

# Graha Names in Tamil
GRAHA_NAMES_TA: Dict[str, str] = {
    "Ketu": "கேது",
    "Venus": "சுக்கிரன்",
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Rahu": "ராகு",
    "Jupiter": "குரு",
    "Saturn": "சனி",
    "Mercury": "புதன்",
}

# 27 Sacred Trees (Sthala Vriksham / மரம்) in Tamil
NAKSHATRA_TREES_TA: Dict[int, str] = {
    1: "எட்டி",
    2: "நெல்லி",
    3: "அத்தி",
    4: "நாவல்",
    5: "கருங்காலி",
    6: "செங்காலி",
    7: "மூங்கில்",
    8: "அரசு",
    9: "புன்னை",
    10: "ஆலமரம்",
    11: "பலாமரம்",
    12: "அலரி / இலந்தை",
    13: "அத்தி",
    14: "வில்வம்",
    15: "மருதம்",
    16: "விளா",
    17: "மகிழம்",
    18: "பராய்",
    19: "மரா மரம்",
    20: "வஞ்சி",
    21: "பலா",
    22: "எருக்கு",
    23: "வன்னி",
    24: "கடம்பு",
    25: "தேமா",
    26: "வேம்பு",
    27: "இலுப்பை",
}

# 27 Animals (மிருகம்) in Tamil
NAKSHATRA_ANIMALS_TA: Dict[int, str] = {
    1: "குதிரை",
    2: "யானை",
    3: "ஆடு",
    4: "பாம்பு",
    5: "பாம்பு",
    6: "நாய்",
    7: "பூனை",
    8: "ஆடு",
    9: "பூனை",
    10: "எலி",
    11: "எலி",
    12: "பசு / மாடு",
    13: "எருமை",
    14: "புலி",
    15: "எருமை",
    16: "புலி",
    17: "மான்",
    18: "மான்",
    19: "நாய்",
    20: "குரங்கு",
    21: "கீரி",
    22: "குரங்கு",
    23: "சிங்கம்",
    24: "குதிரை",
    25: "சிங்கம்",
    26: "பசு / மாடு",
    27: "யானை",
}

# 27 Birds (பட்சி) in Tamil (Traditional Astrological Birds)
NAKSHATRA_BIRDS_TA: Dict[int, str] = {
    1: "புள்ளு (பருந்து)",
    2: "காகம்",
    3: "மயில்",
    4: "ஆந்தை",
    5: "கோழி",
    6: "செம்போத்து",
    7: "அன்னம்",
    8: "நீர்க்காகம்",
    9: "சக்கரவாகம்",
    10: "ஆண் கழுகு",
    11: "பெண் கழுகு",
    12: "வண்டு",
    13: "பருந்து",
    14: "மரங்கொத்தி",
    15: "தேனீ",
    16: "செங்குயில்",
    17: "வானம்பாடி",
    18: "சக்கரவாகப் புள்",
    19: "செம்பருந்து",
    20: "கௌதாரி",
    21: "அன்னப்பறவை",
    22: "நாரை",
    23: "பொன்வண்டு",
    24: "கடற்காகம்",
    25: "உள்ளான்",
    26: "கொக்கு",
    27: "வானம்பாடி",
}

# Nadi (நாடி) classification: 3 Nadis (வாத, பித்த, சிலேத்தும நாடி)
NAKSHATRA_NADI_TA: Dict[int, str] = {
    # Vata / Adi (வாத நாடி / ஆதி)
    1: "வாத நாடி (ஆதி)", 6: "வாத நாடி (ஆதி)", 7: "வாத நாடி (ஆதி)", 12: "வாத நாடி (ஆதி)",
    13: "வாத நாடி (ஆதி)", 18: "வாத நாடி (ஆதி)", 19: "வாத நாடி (ஆதி)", 24: "வாத நாடி (ஆதி)", 25: "வாத நாடி (ஆதி)",
    # Pitta / Madhya (பித்த நாடி / மத்திய)
    2: "பித்த நாடி (மத்திய)", 5: "பித்த நாடி (மத்திய)", 8: "பித்த நாடி (மத்திய)", 11: "பித்த நாடி (மத்திய)",
    14: "பித்த நாடி (மத்திய)", 17: "பித்த நாடி (மத்திய)", 20: "பித்த நாடி (மத்திய)", 23: "பித்த நாடி (மத்திய)", 26: "பித்த நாடி (மத்திய)",
    # Kapha / Antya (சிலேத்தும நாடி / அந்திய)
    3: "சிலேத்தும நாடி (அந்திய)", 4: "சிலேத்தும நாடி (அந்திய)", 9: "சிலேத்தும நாடி (அந்திய)", 10: "சிலேத்தும நாடி (அந்திய)",
    15: "சிலேத்தும நாடி (அந்திய)", 16: "சிலேத்தும நாடி (அந்திய)", 21: "சிலேத்தும நாடி (அந்திய)", 22: "சிலேத்தும நாடி (அந்திய)", 27: "சிலேத்தும நாடி (அந்திய)",
}

# Rajju Names in Tamil
RAJJU_MAP_TA: Dict[RajjuType, str] = {
    RajjuType.SHIRO: "சிரசு ரஜ்ஜு (தலை)",
    RajjuType.KANTHA: "கண்ட ரஜ்ஜு (கழுத்து)",
    RajjuType.UDARA: "உதர ரஜ்ஜு (வயிறு)",
    RajjuType.KATI: "கடி ரஜ்ஜு (இடை)",
    RajjuType.PADA: "பாத ரஜ்ஜு (கால்)",
}

# Gana Names in Tamil
GANA_MAP_TA: Dict[GanaType, str] = {
    GanaType.DEVA: "தேவ கணம்",
    GanaType.MANUSHYA: "மனித கணம்",
    GanaType.RAKSHASA: "ராட்சச கணம்",
}

# Classical Pancha Pakshi Assignment (27 stars -> 5 birds)
PANCHA_PAKSHI_BIRDS = ["வல்லூறு", "ஆந்தை", "காகம்", "கோழி", "மயில்"]
PANCHA_PAKSHI_BIRDS_EN = ["Vulture", "Owl", "Crow", "Cock", "Peacock"]

PANCHA_PAKSHI_STAR_MAP: Dict[int, str] = {
    # அசுவினி முதல் மிருகசீரிஷம் வரை: வல்லூறு
    1: "வல்லூறு", 2: "வல்லூறு", 3: "வல்லூறு", 4: "வல்லூறு", 5: "வல்லூறு",
    # திருவாதிரை முதல் பூரம் வரை: ஆந்தை
    6: "ஆந்தை", 7: "ஆந்தை", 8: "ஆந்தை", 9: "ஆந்தை", 10: "ஆந்தை", 11: "ஆந்தை",
    # உத்திரம் முதல் விசாகம் வரை: காகம்
    12: "காகம்", 13: "காகம்", 14: "காகம்", 15: "காகம்", 16: "காகம்",
    # அனுஷம் முதல் திருவோணம் வரை: கோழி
    17: "கோழி", 18: "கோழி", 19: "கோழி", 20: "கோழி", 21: "கோழி", 22: "கோழி",
    # அவிட்டம் முதல் ரேவதி வரை: மயில்
    23: "மயில்", 24: "மயில்", 25: "மயில்", 26: "மயில்", 27: "மயில்",
}

# Weekday + Nakshatra -> Vara Yoga (அமிர்த யோகம், சித்த யோகம், மரண யோகம்)
# Weekday: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
VARA_YOGA_RULES: Dict[int, Dict[str, List[int]]] = {
    6: {  # Sunday (ஞாயிறு)
        "amrita": [13],  # Hasta
        "siddha": [3, 12, 21, 8, 4, 7, 26],  # Krittika, U Phalguni, U Ashadha, Pushya, Rohini, Punarvasu, U Bhadra
        "marana": [2, 9, 18, 16, 10, 11, 20, 25],  # Bharani, Ashlesha, Jyeshtha, Vishakha, Magha, P Phalguni, P Ashadha, P Bhadra
    },
    0: {  # Monday (திங்கள்)
        "amrita": [12, 21],  # U Phalguni, U Ashadha
        "siddha": [4, 5, 7, 14, 13, 17, 22, 23, 27],  # Rohini, Mrigashira, Punarvasu, Chitra, Hasta, Anuradha, Shravana, Dhanishta, Revati
        "marana": [3, 15, 24, 19, 18],  # Krittika, Swati, Shatabhisha, Mula, Jyeshtha
    },
    1: {  # Tuesday (செவ்வாய்)
        "amrita": [],
        "siddha": [1, 8, 13, 17, 26],  # Ashwini, Pushya, Hasta, Anuradha, U Bhadrapada
        "marana": [18, 22, 3],  # Jyeshtha, Shravana, Krittika
    },
    2: {  # Wednesday (புதன்)
        "amrita": [4, 5, 13, 17, 27],  # Rohini, Mrigashira, Hasta, Anuradha, Revati
        "siddha": [1, 3, 8, 12, 14, 21],  # Ashwini, Krittika, Pushya, U Phalguni, Chitra, U Ashadha
        "marana": [2, 9, 6],  # Bharani, Ashlesha, Ardra
    },
    3: {  # Thursday (வியாழன்)
        "amrita": [8, 7, 21, 26, 27],  # Pushya, Punarvasu, U Ashadha, U Bhadrapada, Revati
        "siddha": [1, 2, 4, 5, 14, 15],  # Ashwini, Bharani, Rohini, Mrigashira, Chitra, Swati
        "marana": [19, 24, 18],  # Mula, Shatabhisha, Jyeshtha
    },
    4: {  # Friday (வெள்ளி)
        "amrita": [1, 5, 13, 17, 27],  # Ashwini, Mrigashira, Hasta, Anuradha, Revati
        "siddha": [8, 12, 14, 16, 21, 22],  # Pushya, U Phalguni, Chitra, Vishakha, U Ashadha, Shravana
        "marana": [2, 4, 6],  # Bharani, Rohini, Ardra
    },
    5: {  # Saturday (சனி)
        "amrita": [4, 15, 22],  # Rohini, Swati, Shravana
        "siddha": [2, 5, 7, 14, 16, 17, 24],  # Bharani, Mrigashira, Punarvasu, Chitra, Vishakha, Anuradha, Shatabhisha
        "marana": [12, 20, 26],  # U Phalguni, P Ashadha, U Bhadrapada
    },
}

# Rasi Sign Entrance Directions (வாசல் திசை)
# Agni (Fire) = East, Prithvi (Earth) = South, Vayu (Air) = West, Jala (Water) = North
SIGN_DIRECTIONS: Dict[int, Tuple[str, str]] = {
    1: ("East", "கிழக்கு வாசல்"),
    2: ("South", "தெற்கு வாசல்"),
    3: ("West", "மேற்கு வாசல்"),
    4: ("North", "வடக்கு வாசல்"),
    5: ("East", "கிழக்கு வாசல்"),
    6: ("South", "தெற்கு வாசல்"),
    7: ("West", "மேற்கு வாசல்"),
    8: ("North", "வடக்கு வாசல்"),
    9: ("East", "கிழக்கு வாசல்"),
    10: ("South", "தெற்கு வாசல்"),
    11: ("West", "மேற்கு வாசல்"),
    12: ("North", "வடக்கு வாசல்"),
}

# Planetary Recommendations for Lucky Day, Color, Gem, and Worship Deity
PLANET_RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "Sun": {
        "day": "ஞாயிறு",
        "color": "சிவப்பு, மாணிக்கச் சிவப்பு",
        "gem": "மாணிக்கம் (Ruby)",
        "deity": "சிவபெருமான், சூரிய நாராயணர்",
    },
    "Moon": {
        "day": "திங்கள்",
        "color": "வெள்ளை, முத்து வெண்மை",
        "gem": "முத்து (Pearl)",
        "deity": "அம்பாள், பார்வதி தேவி",
    },
    "Mars": {
        "day": "செவ்வாய்",
        "color": "சிகப்பு, பவள நிறம்",
        "gem": "பவளம் (Red Coral)",
        "deity": "முருகப்பெருமான்",
    },
    "Mercury": {
        "day": "புதன்",
        "color": "பச்சை, மரகதப் பச்சை",
        "gem": "மரகதம் (Emerald)",
        "deity": "மகாவிஷ்ணு, பெருமாள்",
    },
    "Jupiter": {
        "day": "வியாழன்",
        "color": "மஞ்சள், பொன்னிறம்",
        "gem": "புஷ்பராகம் (Yellow Sapphire)",
        "deity": "தட்சிணாமூர்த்தி, குரு பகவான்",
    },
    "Venus": {
        "day": "வெள்ளி",
        "color": "வெள்ளை, வைர வெண்மை",
        "gem": "வைரம் (Diamond)",
        "deity": "மகாலட்சுமி",
    },
    "Saturn": {
        "day": "சனி",
        "color": "நீலம், கருநீலம்",
        "gem": "நீலக்கல் (Blue Sapphire)",
        "deity": "சனீஸ்வர பகவான், ஆஞ்சநேயர்",
    },
    "Rahu": {
        "day": "ஞாயிறு / செவ்வாய் (ராகு காலம்)",
        "color": "கரும் சாம்பல், நீல நிறம்",
        "gem": "கோமேதகம் (Hessonite)",
        "deity": "துர்க்கை அம்மன்",
    },
    "Ketu": {
        "day": "வியாழன் / செவ்வாய்",
        "color": "பலவண்ணம், செம்பழுப்பு",
        "gem": "வைடூரியம் (Cat's Eye)",
        "deity": "விநாயகப் பெருமான்",
    },
}


def format_nazhigai_vinadi(nazhigai: int, vinadi: int) -> str:
    """Format nazhigai and vinadi into canonical Tamil string."""
    return f"{nazhigai:02d} நாழிகை {vinadi:02d} விநாடி"


def seconds_to_nazhigai_vinadi(seconds: float) -> Tuple[int, int]:
    """Convert total seconds into (nazhigai, vinadi).
    1 Nazhigai = 24 minutes = 1440 seconds.
    1 Vinadi = 24 seconds.
    """
    tot = max(0.0, seconds)
    naz = int(tot // 1440.0)
    rem = tot % 1440.0
    vin = int(round(rem / 24.0))
    if vin >= 60:
        naz += 1
        vin = 0
    return naz, vin


def calculate_traditional_horoscope_writing_data(
    birth_date: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    timezone_str: str = "Asia/Kolkata",
    ayanamsa_id: int = 0,
    house_system_id: int = 0,
    panchanga_system: str = "thirukanitha",
    person_name: str = "Native",
    gender: str = "male",
    entrance_direction_basis: str = "rasi",
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Comprehensive calculator for all six pages of traditional Tamil horoscope writing."""
    tz = ZoneInfo(timezone_str)
    birth_dt_local = datetime.combine(birth_date, birth_time).replace(tzinfo=tz)
    birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

    # 1. Astronomical Tamil Calendar & Eras
    cal_data = calculate_astronomical_tamil_calendar(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        timezone_str=timezone_str,
        ayanamsa_id=ayanamsa_id,
    )

    # 2. Birth JD & Ephemeris
    birth_h = (
        birth_dt_utc.hour
        + birth_dt_utc.minute / 60.0
        + birth_dt_utc.second / 3600.0
        + birth_dt_utc.microsecond / 3600000000.0
    )
    birth_jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day, birth_h)
    ayanamsa_deg = xalen.ayanamsa(birth_jd, ayanamsa_id)

    # 3. Sunrise, Sunset & Day/Night Lengths
    sunrise_utc, sunset_utc, _ = calculate_solar_sunrise_sunset(birth_date, latitude, longitude)
    sunrise_local = sunrise_utc.astimezone(tz)
    sunset_local = sunset_utc.astimezone(tz)

    # Check if born before today's sunrise (belongs to previous civil day's solar day)
    is_born_before_sunrise = birth_dt_local < sunrise_local
    if is_born_before_sunrise:
        prev_date = birth_date - timedelta(days=1)
        prev_sunrise_utc, _, _ = calculate_solar_sunrise_sunset(prev_date, latitude, longitude)
        ref_sunrise_local = prev_sunrise_utc.astimezone(tz)
    else:
        ref_sunrise_local = sunrise_local

    # Elapsed time from sunrise to birth (Udayadhi)
    udayadhi_duration = birth_dt_local - ref_sunrise_local
    udayadhi_sec = udayadhi_duration.total_seconds()
    udayadhi_naz, udayadhi_vin = seconds_to_nazhigai_vinadi(udayadhi_sec)
    udayadhi_hours = int(udayadhi_sec // 3600)
    udayadhi_mins = int((udayadhi_sec % 3600) // 60)

    # Daylight duration (Ahas / அகஸ்)
    daylight_sec = (sunset_local - sunrise_local).total_seconds()
    ahas_naz, ahas_vin = seconds_to_nazhigai_vinadi(daylight_sec)
    ahas_hours = int(daylight_sec // 3600)
    ahas_mins = int((daylight_sec % 3600) // 60)

    # Night duration
    night_sec = 86400.0 - daylight_sec
    night_naz, night_vin = seconds_to_nazhigai_vinadi(night_sec)

    # Day / Night Classification (காலம்)
    is_day_birth = (birth_dt_local >= sunrise_local) and (birth_dt_local < sunset_local)
    kalam_str = "பகல்" if is_day_birth else "இரவு"

    # Weekday (கிழமை)
    # If born before sunrise, traditional Vedic weekday is the previous day
    effective_weekday_date = (birth_date - timedelta(days=1)) if is_born_before_sunrise else birth_date
    weekday_py = effective_weekday_date.weekday()  # 0=Mon..6=Sun
    # Weekday in Tamil
    weekday_ta_names = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
    weekday_ta = weekday_ta_names[weekday_py]
    weekday_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday_py]

    # 4. Planetary & House positions at birth
    from app.services.ephemeris import compute_ascendant_and_houses, compute_planetary_positions
    ascendant, _, houses = compute_ascendant_and_houses(
        jd=birth_jd,
        lat=latitude,
        lon=longitude,
        ayanamsa_id=ayanamsa_id,
        house_system_id=house_system_id,
    )
    planets = compute_planetary_positions(birth_jd, ayanamsa_id, include_outer=False)
    planet_map = {p.name: p for p in planets}
    moon = planet_map["Moon"]

    # 5. Moon & Nakshatra Calculations
    moon_sid = moon.longitude % 360.0
    nak_span = 360.0 / 27.0  # 13.33333333°
    nak_idx = int(moon_sid // nak_span) + 1
    nak_idx = max(1, min(27, nak_idx))
    deg_in_nak = moon_sid % nak_span
    pada_span = nak_span / 4.0  # 3.33333333°
    nak_pada = int(deg_in_nak // pada_span) + 1
    nak_pada = max(1, min(4, nak_pada))
    nak_name_ta = NAKSHATRA_LIST_TA[nak_idx - 1]
    nak_lord_en = NAKSHATRAS[nak_idx - 1]["lord"]
    nak_lord_ta = GRAHA_NAMES_TA.get(nak_lord_en, nak_lord_en)

    # Transitions for Nakshatra (Start/End)
    nak_start_jd = find_nakshatra_transition(birth_jd, ayanamsa_id, forward=False)
    nak_end_jd = find_nakshatra_transition(birth_jd, ayanamsa_id, forward=True)
    
    # Convert transition JDs to local datetime
    def jd_to_local_dt(target_jd: float) -> datetime:
        y, m, d, h_fl = swe.revjul(target_jd)
        tot_s = int(round(h_fl * 3600.0))
        return datetime(y, m, d, tot_s // 3600, (tot_s % 3600) // 60, tot_s % 60, tzinfo=timezone.utc).astimezone(tz)

    nak_start_local = jd_to_local_dt(nak_start_jd)
    nak_end_local = jd_to_local_dt(nak_end_jd)

    prev_nak_idx = (nak_idx - 2) % 27 + 1
    next_nak_idx = (nak_idx % 27) + 1
    prev_nak_name_ta = NAKSHATRA_LIST_TA[prev_nak_idx - 1]
    next_nak_name_ta = NAKSHATRA_LIST_TA[next_nak_idx - 1]

    # 6. Tithi & Transition
    tithi_idx, tithi_name_en, paksha_en, tithi_progress = get_tithi_at_jd(birth_jd)
    tithi_name_ta = TITHI_TAMIL[tithi_idx - 1]
    paksha_ta = "வளர்பிறை" if paksha_en == "Shukla" else "தேய்பிறை"
    tithi_start_jd = find_tithi_transition(birth_jd, forward=False)
    tithi_end_jd = find_tithi_transition(birth_jd, forward=True)
    tithi_end_local = jd_to_local_dt(tithi_end_jd)

    # 7. Yoga & Karana
    sun_pos = planet_map["Sun"].longitude % 360.0
    yoga_sum = (moon_sid + sun_pos) % 360.0
    yoga_idx = int(yoga_sum // (360.0 / 27.0)) + 1
    yoga_idx = max(1, min(27, yoga_idx))
    yoga_name_ta = YOGA_NAMES_TA[yoga_idx - 1]

    # Karana (60 Karanas in a lunar month, 2 per tithi)
    diff_tithi = (moon_sid - sun_pos) % 360.0
    karana_num = int(diff_tithi // 6.0) + 1
    if karana_num == 1:
        karana_name_en = "Kimstughna"
    elif karana_num >= 58:
        fixed_map = {58: "Shakuni", 59: "Chatushpada", 60: "Naga"}
        karana_name_en = fixed_map.get(karana_num, "Naga")
    else:
        repeating = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"]
        karana_name_en = repeating[(karana_num - 2) % 7]
    karana_name_ta = KARANA_NAMES_TA.get(karana_name_en, karana_name_en)

    # 8. Tyajyam (தியாஜ்ஜியம் / Varjyam)
    varjyam_info, _ = calculate_varjyam_and_amrita(
        nak_idx=nak_idx,
        nak_start_utc=nak_start_local.astimezone(timezone.utc),
        nak_end_utc=nak_end_local.astimezone(timezone.utc),
    )
    varjyam_start_local = datetime.fromisoformat(varjyam_info["start_utc"]).astimezone(tz)
    varjyam_end_local = datetime.fromisoformat(varjyam_info["end_utc"]).astimezone(tz)
    varjyam_start_ghatika = varjyam_info["start_ghatika"]
    varjyam_start_naz = int(varjyam_start_ghatika)
    varjyam_start_vin = int(round((varjyam_start_ghatika - varjyam_start_naz) * 60))
    tyajyam_str = (
        f"{varjyam_start_naz:02d} நா {varjyam_start_vin:02d} வி முதல் "
        f"4 நாழிகை (மணி {varjyam_start_local.strftime('%H:%M')} - {varjyam_end_local.strftime('%H:%M')})"
    )

    # 9. Vara Yoga (வார யோகம்)
    day_rules = VARA_YOGA_RULES.get(weekday_py, {})
    if nak_idx in day_rules.get("amrita", []):
        vara_yoga_ta = "அமிர்த யோகம்"
    elif nak_idx in day_rules.get("siddha", []):
        vara_yoga_ta = "சித்த யோகம்"
    elif nak_idx in day_rules.get("marana", []):
        vara_yoga_ta = "மரண யோகம்"
    else:
        vara_yoga_ta = "சித்த யோகம்"

    # 10. Rising Lagna & Balance (லக்ன இருப்பு)
    asc_deg_in_sign = ascendant.degree_in_sign
    rem_asc_deg = 30.0 - asc_deg_in_sign
    rem_asc_d = int(rem_asc_deg)
    rem_asc_m = int(round((rem_asc_deg - rem_asc_d) * 60.0))
    # Approximate sign rising nazhigai (average 5 nazhigai = 30°)
    rem_asc_naz = (rem_asc_deg / 30.0) * 5.0
    lagna_naz = int(rem_asc_naz)
    lagna_vin = int(round((rem_asc_naz - lagna_naz) * 60))
    lagna_iruppu_str = f"{rem_asc_d}° {rem_asc_m:02d}' ({lagna_naz:02d} நா {lagna_vin:02d} வி)"

    # 11. Vimshottari Dasa in Traditional Nazhigai & Balance (Page 3)
    # Total nakshatra span = 60 Nazhigai. 1 Pada = 15 Nazhigai.
    fraction_in_nak = deg_in_nak / nak_span
    deg_in_pada = deg_in_nak % pada_span
    fraction_in_pada = deg_in_pada / pada_span

    pada_sentrathu_naz_fl = fraction_in_pada * 15.0
    pada_sentrathu_naz = int(pada_sentrathu_naz_fl)
    pada_sentrathu_vin = int(round((pada_sentrathu_naz_fl - pada_sentrathu_naz) * 60))

    pada_nindrathu_naz_fl = 15.0 - pada_sentrathu_naz_fl
    pada_nindrathu_naz = int(pada_nindrathu_naz_fl)
    pada_nindrathu_vin = int(round((pada_nindrathu_naz_fl - pada_nindrathu_naz) * 60))

    # Dasa elapsed & balance
    dasa_full_years = VIMSHOTTARI_YEARS[nak_lord_en]
    elapsed_years_fl = dasa_full_years * fraction_in_nak
    rem_years_fl = dasa_full_years * (1.0 - fraction_in_nak)

    def convert_years_to_ymd_nv(y_fl: float) -> Tuple[int, int, int, int, int]:
        total_days = y_fl * 365.25
        y = int(total_days // 365.25)
        rem_days = total_days - (y * 365.25)
        m = int(rem_days // 30.4375)
        d_fl = rem_days - (m * 30.4375)
        d = int(d_fl)
        rem_day_fraction = d_fl - d
        # Fractional day into nazhigai and vinadi (1 day = 60 nazhigai)
        naz_fl = rem_day_fraction * 60.0
        naz = int(naz_fl)
        vin = int(round((naz_fl - naz) * 60.0))
        if vin >= 60:
            naz += 1
            vin = 0
        if naz >= 60:
            d += 1
            naz = 0
        if d >= 30:
            m += 1
            d = 0
        if m >= 12:
            y += 1
            m = 0
        return y, m, d, naz, vin

    el_y, el_m, el_d, el_naz, el_vin = convert_years_to_ymd_nv(elapsed_years_fl)
    rem_y, rem_m, rem_d, rem_naz, rem_vin = convert_years_to_ymd_nv(rem_years_fl)

    dasa_sentrathu_str = f"{el_y} ஆ, {el_m} மா, {el_d} நா ({el_naz} நா {el_vin} வி)"
    dasa_iruppu_str = f"{rem_y} ஆ, {rem_m} மா, {rem_d} நா ({rem_naz} நா {rem_vin} வி)"

    # Sequential Dasa Timeline for the Booklet
    start_lord_idx = VIMSHOTTARI_ORDER.index(nak_lord_en)
    dasa_sequence: List[Dict[str, Any]] = []
    current_start_date = birth_date
    current_rem_days = rem_years_fl * 365.25
    first_end_date = birth_date + timedelta(days=int(round(current_rem_days)))

    dasa_sequence.append({
        "order": 1,
        "lord_en": nak_lord_en,
        "lord_ta": nak_lord_ta,
        "total_years": dasa_full_years,
        "balance_str": dasa_iruppu_str,
        "start_date": birth_date.strftime("%d-%m-%Y"),
        "end_date": first_end_date.strftime("%d-%m-%Y"),
        "duration_years": round(rem_years_fl, 2),
    })

    iter_start_date = first_end_date
    for i in range(1, 9):
        lord = VIMSHOTTARI_ORDER[(start_lord_idx + i) % 9]
        dur_y = VIMSHOTTARI_YEARS[lord]
        iter_end_date = iter_start_date + timedelta(days=int(round(dur_y * 365.25)))
        dasa_sequence.append({
            "order": i + 1,
            "lord_en": lord,
            "lord_ta": GRAHA_NAMES_TA.get(lord, lord),
            "total_years": dur_y,
            "balance_str": f"{dur_y} ஆண்டுகள்",
            "start_date": iter_start_date.strftime("%d-%m-%Y"),
            "end_date": iter_end_date.strftime("%d-%m-%Y"),
            "duration_years": dur_y,
        })
        iter_start_date = iter_end_date

    # 12. Classifications for Page 4 (குறிப்பு)
    animal_ta = NAKSHATRA_ANIMALS_TA.get(nak_idx, "குறிப்பிடப்படவில்லை")
    bird_ta = NAKSHATRA_BIRDS_TA.get(nak_idx, "குறிப்பிடப்படவில்லை")
    tree_ta = NAKSHATRA_TREES_TA.get(nak_idx, "குறிப்பிடப்படவில்லை")
    
    gana_enum = NAKSHATRA_GANA.get(nak_idx - 1, GanaType.MANUSHYA)
    gana_ta = GANA_MAP_TA.get(gana_enum, "மனித கணம்")

    rajju_enum = NAKSHATRA_RAJJU.get(nak_idx - 1, RajjuType.UDARA)
    rajju_ta = RAJJU_MAP_TA.get(rajju_enum, "உதர ரஜ்ஜு")

    nadi_ta = NAKSHATRA_NADI_TA.get(nak_idx, "வாத நாடி (ஆதி)")

    # 13. Padupakshi Shastra for Page 5 (ஸ்ரீ படுபட்சி பலன்)
    birth_pakshi_ta = PANCHA_PAKSHI_STAR_MAP.get(nak_idx, "வல்லூறு")
    
    # Auspicious states based on paksha
    if paksha_ta == "வளர்பிறை":
        pakshi_strength_desc = (
            f"வளர்பிறை காலத்தில் {birth_pakshi_ta} பட்சி அரசாளும் மற்றும் ஊண் கொள்ளும் வேளைகள் "
            "மிகவும் மேன்மையான பலன்களைத் தரும். முக்கிய சுப காரியங்கள், தொழில் தொடக்கம், ஒப்பந்தங்கள் "
            "இக்காலத்தில் செய்வது பூரண வெற்றியை ஈட்டும்."
        )
        pakshi_dominant_state = "அரசு & ஊண் (உயர்ந்த ஆதிக்க நிலை)"
    else:
        pakshi_strength_desc = (
            f"தேய்பிறை காலத்தில் {birth_pakshi_ta} பட்சி நடை மற்றும் துயில் நிலைகளில் எச்சரிக்கையுடன் இருக்க வேண்டும். "
            "சாவு வேளைகளில் புதிய முயற்சிகளையும் நீண்ட பிரயாணங்களையும் தவிர்ப்பது உத்தமமானது."
        )
        pakshi_dominant_state = "நடை & துயில் (கட்டுப்படுத்தப்பட்ட நிலை)"

    # 14. Archana Slip Recommendations for Page 6 (அர்ச்சனை பேப்பரில் பலன்)
    # Rasi Lord & Nakshatra Lord for default recommendations
    rasi_idx = moon.sign_index
    rasi_name_ta = moon.sign_name_tamil
    rasi_lord_en = SIGN_LORDS[rasi_idx]
    
    # Entrance Direction: Derivation based on choice
    lagna_idx = ascendant.sign_index
    lagna_name_ta = ascendant.sign_name_tamil

    if entrance_direction_basis == "lagna":
        calc_entrance_dir = SIGN_DIRECTIONS.get(lagna_idx, ("East", "கிழக்கு வாசல்"))[1]
    else:  # default 'rasi'
        calc_entrance_dir = SIGN_DIRECTIONS.get(rasi_idx, ("East", "கிழக்கு வாசல்"))[1]

    # Recommendations based on Rasi / Nakshatra Lord
    primary_recom = PLANET_RECOMMENDATIONS.get(rasi_lord_en, PLANET_RECOMMENDATIONS["Sun"])
    
    default_lucky_day = primary_recom["day"]
    default_lucky_color = primary_recom["color"]
    default_lucky_gem = primary_recom["gem"]
    default_deity = primary_recom["deity"]

    # Apply Overrides if present
    overrides = overrides or {}
    active_entrance_dir = overrides.get("entrance_direction") or calc_entrance_dir
    active_lucky_day = overrides.get("lucky_day") or default_lucky_day
    active_lucky_color = overrides.get("lucky_color") or default_lucky_color
    active_lucky_gem = overrides.get("lucky_gem") or default_lucky_gem
    active_deity = overrides.get("worship_deity") or default_deity

    # 15. Assemble the structured multi-page response payload
    return {
        "metadata": {
            "engine": "XALEN Ephemeris & Shastric Panchanga Engine",
            "version": "1.0.0",
            "panchanga_system": panchanga_system,
            "ayanamsa_name": "Lahiri (Chitrapaksha)",
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        },
        "person_details": {
            "name": person_name,
            "gender": gender,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "birth_time": birth_time.strftime("%H:%M:%S"),
            "birth_place": f"{latitude:.4f}°N, {longitude:.4f}°E",
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
        },
        "page1_birth_details": {
            "tamil_year": cal_data["tamil_year_ta"],
            "tamil_month": cal_data["tamil_month_ta"],
            "tamil_date": cal_data["tamil_date"],
            "tamil_year_month_date": f"{cal_data['tamil_year_ta']} வருடம், {cal_data['tamil_month_ta']} மாதம் {cal_data['tamil_date']} ஆம் தேதி",
            "weekday": weekday_ta,
            "ayanam": cal_data["ayanam_ta"],
            "ritu": cal_data["ritu_ta"],
            "paksha": paksha_ta,
            "tithi": f"{tithi_name_ta} (முடிவு: {tithi_end_local.strftime('%H:%M')} மணி)",
            "prev_nakshatra": f"{prev_nak_name_ta} (முடிவு: {nak_start_local.strftime('%H:%M')} மணி)",
            "birth_nakshatra": f"{nak_name_ta} - பாதம் {nak_pada} (முடிவு: {nak_end_local.strftime('%H:%M')} மணி)",
            "next_nakshatra": f"{next_nak_name_ta} (ஆரம்பம்: {nak_end_local.strftime('%H:%M')} மணி)",
            "nama_yoga": yoga_name_ta,
            "karana": karana_name_ta,
            "tyajyam": tyajyam_str,
            "ahas": f"{ahas_naz:02d} நாழிகை {ahas_vin:02d} விநாடி ({ahas_hours} மணி {ahas_mins:02d} நிமிடம்)",
            "birth_time": birth_time.strftime("%H:%M:%S"),
            "udayadhi_nazhigai": f"{udayadhi_naz:02d} நாழிகை {udayadhi_vin:02d} விநாடி",
            "udayadhi_hours": f"{udayadhi_hours} மணி {udayadhi_mins:02d} நிமிடம்",
            "sunrise": sunrise_local.strftime("%H:%M:%S"),
            "sunset": sunset_local.strftime("%H:%M:%S"),
            "udaya_lagna": f"{lagna_name_ta} லக்னம் ({asc_deg_in_sign:.2f}°)",
            "vara_yoga": vara_yoga_ta,
        },
        "page2_dinasuthi": {
            "saka_year": f"{cal_data['saka_year']} சகாப்தம்",
            "kali_year": f"{cal_data['kali_year']} கலியுகாதி",
            "hijri_year": f"{cal_data['hijri_year']} ஹிஜிரி",
            "kollam_year": f"{cal_data['kollam_year']} கொல்லம் ஆண்டு",
            "english_year": birth_date.year,
            "english_date": birth_date.strftime("%d-%m-%Y"),
            "tamil_month_date": f"{cal_data['tamil_month_ta']} {cal_data['tamil_date']}",
            "panchangam": "திருக்கணிதம்" if panchanga_system == "thirukanitha" else "வாக்கியம்",
            "calculation_method": cal_data["calculation_method"],
        },
        "page3_udumaka_dasa": {
            "param_nazhigai": "60 நாழிகை 00 விநாடி",
            "pada_duration": "15 நாழிகை 00 விநாடி",
            "birth_pada": nak_pada,
            "pada_sentrathu": f"{pada_sentrathu_naz:02d} நாழிகை {pada_sentrathu_vin:02d} விநாடி",
            "pada_nindrathu": f"{pada_nindrathu_naz:02d} நாழிகை {pada_nindrathu_vin:02d} விநாடி",
            "dasa_lord": nak_lord_ta,
            "dasa_full_years": f"{dasa_full_years} ஆண்டுகள்",
            "dasa_sentrathu": dasa_sentrathu_str,
            "dasa_iruppu": dasa_iruppu_str,
            "dasa_sequence": dasa_sequence,
        },
        "page4_kurippu": {
            "udayadhi_mani": f"{udayadhi_hours} மணி {udayadhi_mins:02d} நிமிடம்",
            "lagna_iruppu": lagna_iruppu_str,
            "ahas": f"{ahas_naz:02d} நா {ahas_vin:02d} வி",
            "kalam_ontrukku": "1 நாழிகை = 24 நிமிடங்கள்",
            "kalam": kalam_str,
            "lagna": lagna_name_ta,
            "rasi": rasi_name_ta,
            "nakshatra": nak_name_ta,
            "pada": nak_pada,
            "mrigam": animal_ta,
            "pakshi": bird_ta,
            "maram": tree_ta,
            "gana": gana_ta,
            "rajju": rajju_ta,
            "nadi": nadi_ta,
        },
        "page5_padupakshi": {
            "birth_nakshatra": f"{nak_name_ta} (பாதம் {nak_pada})",
            "uyir_pakshi": birth_pakshi_ta,
            "paksha": paksha_ta,
            "valarpirai_guidance": "ஊண் மற்றும் அரசு வேளைகளில் சுப காரியங்கள் செய்ய பூரண வெற்றி கிட்டும்.",
            "theypirai_guidance": "சாவு மற்றும் துயில் வேளைகளில் புதிய முதலீடுகள், முக்கிய முடிவுகளைத் தவிர்க்கவும்.",
            "dominant_state": pakshi_dominant_state,
            "detailed_guidance": pakshi_strength_desc,
            "five_birds_list": PANCHA_PAKSHI_BIRDS,
        },
        "page6_archana_slip": {
            "rasi": rasi_name_ta,
            "nakshatra": nak_name_ta,
            "lagna": lagna_name_ta,
            "birth_date": birth_date.strftime("%d-%m-%Y"),
            "tamil_date": f"{cal_data['tamil_month_ta']} {cal_data['tamil_date']}",
            # Active values (with astrologer overrides applied)
            "entrance_direction": active_entrance_dir,
            "lucky_day": active_lucky_day,
            "lucky_color": active_lucky_color,
            "lucky_gem": active_lucky_gem,
            "worship_deity": active_deity,
            # Original calculated defaults (for resetting)
            "calculated_entrance_direction": calc_entrance_dir,
            "calculated_lucky_day": default_lucky_day,
            "calculated_lucky_color": default_lucky_color,
            "calculated_lucky_gem": default_lucky_gem,
            "calculated_worship_deity": default_deity,
            "entrance_direction_basis": entrance_direction_basis,
        },
        "overrides": overrides,
    }
