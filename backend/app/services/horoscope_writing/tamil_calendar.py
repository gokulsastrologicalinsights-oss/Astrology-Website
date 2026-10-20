"""Tamil Solar Calendar & Multi-Era Astronomical Calculations.

Provides high-precision calculations for:
1. 60-Year Tamil Jovian Cycle (பிரபவ முதல் அட்சய வரை)
2. 12 Tamil Solar Months (சித்திரை முதல் பங்குனி வரை)
3. Astronomical Tamil Solar Date based on sidereal Sun ingress (Sankranti) and sunset rules
4. Ayanam (உத்தராயணம் / தட்சிணாயனம்)
5. 6 Ritus (வசந்த, கிரீஷ்ம, வர்ஷ, சரத், ஹேமந்த, சிசிர ருதுக்கள்)
6. Calendar Eras:
   - Salivahana Saka Era (சகாப்தம்)
   - Kali Yuga Era (கலியுகாதி)
   - Kollam Era (கொல்லம் ஆண்டு)
   - Hijri Era (ஹிஜிரி)
"""

import math
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional
import xalen
import xalen.swe as swe

# 60 Tamil Jovian Years (1-indexed: 1 = Prabhava .. 60 = Akshaya)
TAMIL_YEARS_60: Dict[int, Tuple[str, str]] = {
    1: ("Prabhava", "பிரபவ"),
    2: ("Vibhava", "விபவ"),
    3: ("Shukla", "சுக்கில"),
    4: ("Pramodoota", "பிரமோதூத"),
    5: ("Prajotpatti", "பிரஜோற்பத்தி"),
    6: ("Angirasa", "ஆங்கீரச"),
    7: ("Srimukha", "ஸ்ரீமுக"),
    8: ("Bhava", "பவ"),
    9: ("Yuva", "யுவ"),
    10: ("Dhatru", "தாது"),
    11: ("Ishvara", "ஈஸ்வர"),
    12: ("Bahudhanya", "வெகுதானிய"),
    13: ("Pramathi", "பிரமாதி"),
    14: ("Vikrama", "விக்ரம"),
    15: ("Vishu", "விஷு"),
    16: ("Chitrabanu", "சித்திரபானு"),
    17: ("Subhanu", "சுபானு"),
    18: ("Dharana", "தாரண"),
    19: ("Parthiba", "பார்த்திப"),
    20: ("Viya", "விய"),
    21: ("Sarvajittu", "சர்வசித்து"),
    22: ("Sarvadhari", "சர்வதாரி"),
    23: ("Virodhi", "விரோதி"),
    24: ("Vikruti", "விக்ருதி"),
    25: ("Kara", "கர"),
    26: ("Nandana", "நந்தன"),
    27: ("Vijaya", "விஜய"),
    28: ("Jaya", "ஜய"),
    29: ("Manmatha", "மன்மத"),
    30: ("Dunmukhi", "துன்முகி"),
    31: ("Hevilambi", "ஹேவிளம்பி"),
    32: ("Vilambi", "விளம்பி"),
    33: ("Vikari", "விகாரி"),
    34: ("Sarvari", "சார்வரி"),
    35: ("Plava", "பிலவ"),
    36: ("Subakruthu", "சுபகிருது"),
    37: ("Sobakruthu", "சோபகிருது"),
    38: ("Krodhi", "குரோதி"),
    39: ("Visvavasu", "விசுவாசு"),
    40: ("Parabhava", "பராபவ"),
    41: ("Plavanga", "பிலவங்க"),
    42: ("Kilaka", "கீலக"),
    43: ("Saumya", "சௌமிய"),
    44: ("Sadharana", "சாதாரண"),
    45: ("Virodhikrutha", "விரோதிகிருது"),
    46: ("Paridhabi", "பரிதாபி"),
    47: ("Pramadheesa", "பிரமாதீச"),
    48: ("Ananda", "ஆனந்த"),
    49: ("Rakshasa", "ராட்சச"),
    50: ("Nala", "நள"),
    51: ("Pingala", "பிங்கள"),
    52: ("Kalayukthi", "காளயுக்தி"),
    53: ("Siddharthi", "சித்தார்த்தி"),
    54: ("Raudhri", "ரௌத்திரி"),
    55: ("Dunmathi", "துன்மதி"),
    56: ("Dhundhubhi", "துந்துபி"),
    57: ("Rudhrodhkari", "ருத்ரோத்காரி"),
    58: ("Raktakshi", "ரக்தாட்சி"),
    59: ("Krodhana", "குரோதன"),
    60: ("Akshaya", "அட்சய"),
}

# 12 Tamil Solar Months (1 to 12 matching Sun sign Aries to Pisces)
TAMIL_MONTHS: Dict[int, Dict[str, Any]] = {
    1: {"name_en": "Chithirai", "name_ta": "சித்திரை", "sign_idx": 1, "sign_en": "Aries", "sign_ta": "மேஷம்"},
    2: {"name_en": "Vaikasi", "name_ta": "வைகாசி", "sign_idx": 2, "sign_en": "Taurus", "sign_ta": "ரிஷபம்"},
    3: {"name_en": "Aani", "name_ta": "ஆனி", "sign_idx": 3, "sign_en": "Gemini", "sign_ta": "மிதுனம்"},
    4: {"name_en": "Aadi", "name_ta": "ஆடி", "sign_idx": 4, "sign_en": "Cancer", "sign_ta": "கடகம்"},
    5: {"name_en": "Aavani", "name_ta": "ஆவணி", "sign_idx": 5, "sign_en": "Leo", "sign_ta": "சிம்மம்"},
    6: {"name_en": "Purattasi", "name_ta": "புரட்டாசி", "sign_idx": 6, "sign_en": "Virgo", "sign_ta": "கன்னி"},
    7: {"name_en": "Aippasi", "name_ta": "ஐப்பசி", "sign_idx": 7, "sign_en": "Libra", "sign_ta": "துலாம்"},
    8: {"name_en": "Karthigai", "name_ta": "கார்த்திகை", "sign_idx": 8, "sign_en": "Scorpio", "sign_ta": "விருச்சிகம்"},
    9: {"name_en": "Margazhi", "name_ta": "மார்கழி", "sign_idx": 9, "sign_en": "Sagittarius", "sign_ta": "தனுசு"},
    10: {"name_en": "Thai", "name_ta": "தை", "sign_idx": 10, "sign_en": "Capricorn", "sign_ta": "மகரம்"},
    11: {"name_en": "Masi", "name_ta": "மாசி", "sign_idx": 11, "sign_en": "Aquarius", "sign_ta": "கும்பம்"},
    12: {"name_en": "Panguni", "name_ta": "பங்குனி", "sign_idx": 12, "sign_en": "Pisces", "sign_ta": "மீனம்"},
}

# 6 Vedic / Tamil Ritus (Seasons)
RITU_MAPPING: Dict[int, Dict[str, str]] = {
    1: {"name_en": "Vasanta", "name_ta": "வசந்த ருது", "desc": "இளவேனில் பருவம்"},
    2: {"name_en": "Vasanta", "name_ta": "வசந்த ருது", "desc": "இளவேனில் பருவம்"},
    3: {"name_en": "Grishma", "name_ta": "கிரீஷ்ம ருது", "desc": "முதுவேனில் பருவம்"},
    4: {"name_en": "Grishma", "name_ta": "கிரீஷ்ம ருது", "desc": "முதுவேனில் பருவம்"},
    5: {"name_en": "Varsha", "name_ta": "வர்ஷ ருது", "desc": "கார் காலம்"},
    6: {"name_en": "Varsha", "name_ta": "வர்ஷ ருது", "desc": "கார் காலம்"},
    7: {"name_en": "Sharad", "name_ta": "சரத் ருது", "desc": "குளிர் காலம்"},
    8: {"name_en": "Sharad", "name_ta": "சரத் ருது", "desc": "குளிர் காலம்"},
    9: {"name_en": "Hemanta", "name_ta": "ஹேமந்த ருது", "desc": "முன்பனி காலம்"},
    10: {"name_en": "Hemanta", "name_ta": "ஹேமந்த ருது", "desc": "முன்பனி காலம்"},
    11: {"name_en": "Shishira", "name_ta": "சிசிர ருது", "desc": "பின்பனி காலம்"},
    12: {"name_en": "Shishira", "name_ta": "சிசிர ருது", "desc": "பின்பனி காலம்"},
}


def find_sun_ingress_jd(target_sign_idx: int, ref_jd: float, ayanamsa_id: int = 0) -> float:
    """Find the exact Julian Day when the sidereal Sun entered target_sign_idx (1=Aries .. 12=Pisces).
    Searches backwards up to 35 days from ref_jd using high-precision bisection.
    """
    target_deg = float((target_sign_idx - 1) * 30.0)
    low_jd = ref_jd - 35.0
    high_jd = ref_jd

    for _ in range(32):
        mid_jd = (low_jd + high_jd) / 2.0
        sun_trop = swe.calc_ut(mid_jd, swe.SE_SUN, 0)[0][0]
        aya = xalen.ayanamsa(mid_jd, ayanamsa_id)
        sun_sid = (sun_trop - aya) % 360.0

        diff = (sun_sid - target_deg) % 360.0
        if diff < 180.0:
            high_jd = mid_jd
        else:
            low_jd = mid_jd

    return (low_jd + high_jd) / 2.0


def calculate_astronomical_tamil_calendar(
    birth_date: date,
    birth_time,
    latitude: float,
    longitude: float,
    timezone_str: str = "Asia/Kolkata",
    ayanamsa_id: int = 0,
) -> Dict[str, Any]:
    """Calculate exact astronomical Tamil year, month, date, Ayanam, Ritu, and historical eras.
    
    Standard Tamil Drik (Thirukanitha) Ingress Rule:
    - If the Sun's transit (Sankranti) into a sidereal sign occurs between sunrise and sunset (daytime),
      that same civil day is Day 1 of the new Tamil month.
    - If the transit occurs after sunset or before next sunrise, the subsequent civil day is Day 1.
    """
    from zoneinfo import ZoneInfo
    from app.services.muhurta_engine.astronomy import calculate_solar_sunrise_sunset

    tz = ZoneInfo(timezone_str)
    # 1. Julian Day at birth local time
    birth_dt_local = datetime.combine(birth_date, birth_time).replace(tzinfo=tz)
    birth_dt_utc = birth_dt_local.astimezone(timezone.utc)
    
    birth_h = (
        birth_dt_utc.hour
        + birth_dt_utc.minute / 60.0
        + birth_dt_utc.second / 3600.0
        + birth_dt_utc.microsecond / 3600000000.0
    )
    birth_jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day, birth_h)

    # 2. Sidereal Sun position at birth
    sun_trop = swe.calc_ut(birth_jd, swe.SE_SUN, 0)[0][0]
    ayanamsa_deg = xalen.ayanamsa(birth_jd, ayanamsa_id)
    sun_sid = (sun_trop - ayanamsa_deg) % 360.0

    month_idx = int(sun_sid // 30.0) + 1
    deg_in_sign = sun_sid % 30.0
    month_info = TAMIL_MONTHS[month_idx]

    # 3. Find exact Sankranti moment for this month
    ingress_jd = find_sun_ingress_jd(month_idx, birth_jd, ayanamsa_id)
    iy, im, iday, ih_float = swe.revjul(ingress_jd)
    tot_sec = int(round(ih_float * 3600.0))
    ingress_dt_utc = datetime(
        iy, im, iday, tot_sec // 3600, (tot_sec % 3600) // 60, tot_sec % 60, tzinfo=timezone.utc
    )
    ingress_dt_local = ingress_dt_utc.astimezone(tz)
    ingress_date_local = ingress_dt_local.date()

    # Determine sunset on the day of ingress
    _, sunset_utc, _ = calculate_solar_sunrise_sunset(ingress_date_local, latitude, longitude)
    sunset_local = sunset_utc.astimezone(tz)

    # If ingress occurs after sunset, Day 1 is the next civil day
    if ingress_dt_local > sunset_local:
        day_1_date = ingress_date_local + timedelta(days=1)
    else:
        day_1_date = ingress_date_local

    # Calculate Tamil Date (1-indexed)
    tamil_date_num = (birth_date - day_1_date).days + 1
    # Safeguard if birth occurred on the same day prior to ingress:
    if tamil_date_num < 1:
        tamil_date_num = 1

    # 4. Tamil Year Calculation (60-year Jovian Cycle)
    # The Jovian cycle restarts in Mid-April (Mesha Sankranti / Chithirai 1)
    # 1987 Chithirai 1 began Prabhava (Year 1).
    is_after_new_year = (month_idx > 1) or (month_idx == 1 and tamil_date_num >= 1)
    # If in early January to mid-April (Margazhi/Thai/Masi/Panguni), year belongs to previous cycle year
    jovian_offset = (birth_date.year - 1987) if is_after_new_year else (birth_date.year - 1988)
    year_index = (jovian_offset % 60) + 1
    year_en, year_ta = TAMIL_YEARS_60[year_index]

    # 5. Ayanam (உத்தராயணம் / தட்சிணாயனம்)
    # Uttarayana: Sun moves north from Makara (270°) to Mithuna (90°) [Months 10, 11, 12, 1, 2, 3]
    # Dakshinayana: Sun moves south from Kataka (90°) to Dhanus (270°) [Months 4, 5, 6, 7, 8, 9]
    if month_idx in [10, 11, 12, 1, 2, 3]:
        ayanam_en = "Uttarayana"
        ayanam_ta = "உத்தராயணம்"
    else:
        ayanam_en = "Dakshinayana"
        ayanam_ta = "தட்சிணாயனம்"

    # 6. Ritu (Season)
    ritu_info = RITU_MAPPING[month_idx]

    # 7. Calendar Eras
    # Salivahana Saka: Started 78 CE. If after Chithirai, Year - 78, else Year - 79.
    saka_year = (birth_date.year - 78) if is_after_new_year else (birth_date.year - 79)

    # Kali Yuga: Began Feb 3102 BCE (Julian Day 588465.5).
    kali_year = (birth_date.year + 3102) if is_after_new_year else (birth_date.year + 3101)

    # Kollam Era: Began Aug 825 CE (Chingam / Simha Sankranti = Aavani).
    is_after_kollam_new_year = (month_idx >= 5)
    kollam_year = (birth_date.year - 824) if is_after_kollam_new_year else (birth_date.year - 825)

    # Hijri Era (Islamic Lunar Calendar)
    # Standard astronomical approximation from Julian Day
    # Epoch: July 16, 622 CE (JD 1948439.5)
    hijri_year = int(((birth_jd - 1948439.5) * 30.0) / 10631.0) + 1

    return {
        "tamil_year_index": year_index,
        "tamil_year_en": year_en,
        "tamil_year_ta": year_ta,
        "tamil_month_index": month_idx,
        "tamil_month_en": month_info["name_en"],
        "tamil_month_ta": month_info["name_ta"],
        "tamil_date": tamil_date_num,
        "sun_sign_en": month_info["sign_en"],
        "sun_sign_ta": month_info["sign_ta"],
        "sun_degree_in_sign": round(deg_in_sign, 4),
        "ayanam_en": ayanam_en,
        "ayanam_ta": ayanam_ta,
        "ritu_en": ritu_info["name_en"],
        "ritu_ta": ritu_info["name_ta"],
        "saka_year": saka_year,
        "kali_year": kali_year,
        "kollam_year": kollam_year,
        "hijri_year": hijri_year,
        "gregorian_year": birth_date.year,
        "gregorian_date_str": birth_date.strftime("%d-%m-%Y"),
        "panchangam_system": "திருக்கணிதம் (Drik Siddhanta)",
        "calculation_method": "சித்ரபக்ஷ லஹரி அயனாம்சம், திருக்கணித வானியல் முறை",
    }
