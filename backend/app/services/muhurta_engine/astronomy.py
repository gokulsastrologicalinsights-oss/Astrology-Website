"""Astronomical Panchanga and Muhurta calculation services.

Provides high-precision calculations for:
- Exact Sunrise, Sunset, Solar Noon, Daytime & Nighttime lengths
- Dynamic Daytime Octants (Rahu Kalam, Yamagandam, Gulika Kalam)
- 15 Daytime Muhurtas (Abhijit Muhurta, Dur Muhurtas)
- Tithi with exact boundary transitions (start & end timestamps)
- Nakshatra with exact boundary transitions (start & end timestamps)
- Yoga and Karana
- Varjyam (Tyajyam) and Amrita Kalam windows
- Rising Ascendant (Lagna) and planetary house placements
"""

import math
from datetime import datetime, date, time, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo
import xalen
import xalen.swe as swe

# 27 Vedic Nakshatras with lords and deities
NAKSHATRAS = [
    {"index": 1, "name": "Ashwini", "name_ta": "அசுவினி", "lord": "Ketu"},
    {"index": 2, "name": "Bharani", "name_ta": "பரணி", "lord": "Venus"},
    {"index": 3, "name": "Krittika", "name_ta": "கார்த்திகை", "lord": "Sun"},
    {"index": 4, "name": "Rohini", "name_ta": "ரோகிணி", "lord": "Moon"},
    {"index": 5, "name": "Mrigashira", "name_ta": "மிருகசீரிஷம்", "lord": "Mars"},
    {"index": 6, "name": "Ardra", "name_ta": "திருவாதிரை", "lord": "Rahu"},
    {"index": 7, "name": "Punarvasu", "name_ta": "புனர்பூசம்", "lord": "Jupiter"},
    {"index": 8, "name": "Pushya", "name_ta": "பூசம்", "lord": "Saturn"},
    {"index": 9, "name": "Ashlesha", "name_ta": "ஆயில்யம்", "lord": "Mercury"},
    {"index": 10, "name": "Magha", "name_ta": "மகம்", "lord": "Ketu"},
    {"index": 11, "name": "Purva Phalguni", "name_ta": "பூரம்", "lord": "Venus"},
    {"index": 12, "name": "Uttara Phalguni", "name_ta": "உத்திரம்", "lord": "Sun"},
    {"index": 13, "name": "Hasta", "name_ta": "அஸ்தம்", "lord": "Moon"},
    {"index": 14, "name": "Chitra", "name_ta": "சித்திரை", "lord": "Mars"},
    {"index": 15, "name": "Swati", "name_ta": "சுவாதி", "lord": "Rahu"},
    {"index": 16, "name": "Vishakha", "name_ta": "விசாகம்", "lord": "Jupiter"},
    {"index": 17, "name": "Anuradha", "name_ta": "அனுஷம்", "lord": "Saturn"},
    {"index": 18, "name": "Jyeshtha", "name_ta": "கேட்டை", "lord": "Mercury"},
    {"index": 19, "name": "Moola", "name_ta": "மூலம்", "lord": "Ketu"},
    {"index": 20, "name": "Purva Ashadha", "name_ta": "பூராடம்", "lord": "Venus"},
    {"index": 21, "name": "Uttara Ashadha", "name_ta": "உத்திராடம்", "lord": "Sun"},
    {"index": 22, "name": "Shravana", "name_ta": "திருவோணம்", "lord": "Moon"},
    {"index": 23, "name": "Dhanishta", "name_ta": "அவிட்டம்", "lord": "Mars"},
    {"index": 24, "name": "Shatabhisha", "name_ta": "சதயம்", "lord": "Rahu"},
    {"index": 25, "name": "Purva Bhadrapada", "name_ta": "பூரட்டாதி", "lord": "Jupiter"},
    {"index": 26, "name": "Uttara Bhadrapada", "name_ta": "உத்திரட்டாதி", "lord": "Saturn"},
    {"index": 27, "name": "Revati", "name_ta": "ரேவதி", "lord": "Mercury"},
]

# Starting ghatika (out of 60) for Varjyam (Tyajyam) for each Nakshatra
VARJYAM_START_GHATIKA: Dict[int, float] = {
    1: 50.0, 2: 24.0, 3: 30.0, 4: 40.0, 5: 14.0, 6: 21.0, 7: 30.0, 8: 20.0, 9: 32.0,
    10: 30.0, 11: 20.0, 12: 18.0, 13: 21.0, 14: 20.0, 15: 14.0, 16: 14.0, 17: 10.0, 18: 14.0,
    19: 56.0, 20: 24.0, 21: 20.0, 22: 10.0, 23: 10.0, 24: 18.0, 25: 16.0, 26: 24.0, 27: 30.0,
}

# Starting ghatika (out of 60) for Amrita Kalam
AMRITA_START_GHATIKA: Dict[int, float] = {
    1: 28.0, 2: 48.0, 3: 54.0, 4: 52.0, 5: 38.0, 6: 35.0, 7: 54.0, 8: 44.0, 9: 56.0,
    10: 54.0, 11: 44.0, 12: 42.0, 13: 45.0, 14: 44.0, 15: 38.0, 16: 38.0, 17: 34.0, 18: 38.0,
    19: 20.0, 20: 48.0, 21: 44.0, 22: 34.0, 23: 34.0, 24: 42.0, 25: 40.0, 26: 48.0, 27: 54.0,
}

TITHI_NAMES = [
    "Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashti", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dvadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashti", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dvadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

TITHI_TAMIL = [
    "சுக்ல பிரதமை", "சுக்ல துவிதியை", "சுக்ல திருதியை", "சுக்ல சதுர்த்தி", "சுக்ல பஞ்சமி",
    "சுக்ல சஷ்டி", "சுக்ல சப்தமி", "சுக்ல அஷ்டமி", "சுக்ல நவமி", "சுக்ல தசமி",
    "சுக்ல ஏகாதசி", "சுக்ல துவாதசி", "சுக்ல திரயோதசி", "சுக்ல சதுர்தசி", "பௌர்ணமி",
    "கிருஷ்ண பிரதமை", "கிருஷ்ண துவிதியை", "கிருஷ்ண திருதியை", "கிருஷ்ண சதுர்த்தி", "கிருஷ்ண பஞ்சமி",
    "கிருஷ்ண சஷ்டி", "கிருஷ்ண சப்தமி", "கிருஷ்ண அஷ்டமி", "கிருஷ்ண நவமி", "கிருஷ்ண தசமி",
    "கிருஷ்ண ஏகாதசி", "கிருஷ்ண துவாதசி", "கிருஷ்ண திரயோதசி", "கிருஷ்ண சதுர்தசி", "அமாவாசை"
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
    "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi",
    "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti"
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

WEEKDAY_NAMES_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_NAMES_TA = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
WEEKDAY_VARA = ["Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara", "Ravivara"]

ZODIAC_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
ZODIAC_NAMES_TA = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
    "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]


def datetime_to_jd(dt_utc: datetime) -> float:
    """Convert a UTC datetime to Julian Day (UT1)."""
    h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0 + dt_utc.microsecond / 3600000000.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, h)


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day (UT1) back to UTC datetime."""
    year, month, day, hour_float = swe.revjul(jd)
    total_seconds = int(round(hour_float * 3600.0))
    hours = total_seconds // 3600
    rem = total_seconds % 3600
    minutes = rem // 60
    seconds = rem % 60
    if hours >= 24:
        hours = 23
        minutes = 59
        seconds = 59
    return datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc)


def calculate_solar_sunrise_sunset(event_date: date, latitude: float, longitude: float) -> Tuple[datetime, datetime, datetime]:
    """Calculate exact Astronomical Sunrise, Sunset, and Solar Noon in UTC using NOAA solar algorithm.
    Returns (sunrise_utc, sunset_utc, solar_noon_utc).
    """
    year, month, day = event_date.year, event_date.month, event_date.day
    day_of_year = (datetime(year, month, day) - datetime(year, 1, 1)).days + 1
    lng_hour = longitude / 15.0

    times: List[datetime] = []
    # 0: Sunrise, 1: Sunset
    for is_sunrise in [True, False]:
        t_base = day_of_year + ((6.0 if is_sunrise else 18.0) - lng_hour) / 24.0
        m = (0.9856 * t_base) - 3.289
        l = (m + (1.916 * math.sin(math.radians(m))) + (0.020 * math.sin(math.radians(2 * m))) + 282.634) % 360.0
        
        # Right Ascension
        ra = (math.degrees(math.atan(0.91764 * math.tan(math.radians(l))))) % 360.0
        l_quadrant = (math.floor(l / 90.0)) * 90.0
        ra_quadrant = (math.floor(ra / 90.0)) * 90.0
        ra = (ra + (l_quadrant - ra_quadrant)) / 15.0

        # Declination
        sin_dec = 0.39782 * math.sin(math.radians(l))
        cos_dec = math.cos(math.asin(sin_dec))

        # Zenith standard 90.8333 deg (50 arcmin depression for solar disk + refraction)
        zenith = 90.8333
        cos_h = (math.cos(math.radians(zenith)) - (sin_dec * math.sin(math.radians(latitude)))) / (cos_dec * math.cos(math.radians(latitude)))
        cos_h = max(-1.0, min(1.0, cos_h))

        h = (360.0 - math.degrees(math.acos(cos_h))) if is_sunrise else math.degrees(math.acos(cos_h))
        h = h / 15.0

        local_mean_time = h + ra - (0.06571 * t_base) - 6.622
        ut = (local_mean_time - lng_hour) % 24.0

        hours = int(ut)
        rem_min = (ut - hours) * 60.0
        minutes = int(rem_min)
        seconds = int((rem_min - minutes) * 60.0)
        times.append(datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc))

    sunrise_utc = times[0]
    sunset_utc = times[1]

    # Calculate Solar Noon
    daylight_secs = (sunset_utc - sunrise_utc).total_seconds()
    if daylight_secs < 0:
        daylight_secs += 86400.0
    solar_noon_utc = sunrise_utc + timedelta(seconds=daylight_secs / 2.0)

    return sunrise_utc, sunset_utc, solar_noon_utc


def get_day_octant_periods(sunrise_utc: datetime, sunset_utc: datetime, weekday_py: int) -> Dict[str, Dict[str, Any]]:
    """Calculate the 8 daytime octants: Rahu Kalam, Yamagandam, Gulika Kalam based on weekday.
    weekday_py: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun.
    """
    day_duration_secs = (sunset_utc - sunrise_utc).total_seconds()
    part_secs = day_duration_secs / 8.0

    # 1-indexed octants (1..8)
    rahu_octants = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
    yama_octants = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
    guli_octants = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    def octant_window(part_num: int) -> Dict[str, Any]:
        start = sunrise_utc + timedelta(seconds=(part_num - 1) * part_secs)
        end = sunrise_utc + timedelta(seconds=part_num * part_secs)
        return {
            "part": part_num,
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "duration_minutes": round(part_secs / 60.0, 1),
        }

    return {
        "rahu_kalam": octant_window(rahu_octants[weekday_py]),
        "yamagandam": octant_window(yama_octants[weekday_py]),
        "gulikai": octant_window(guli_octants[weekday_py]),
    }


def get_daytime_muhurtas(sunrise_utc: datetime, sunset_utc: datetime, weekday_py: int) -> Dict[str, Any]:
    """Calculate the 15 daytime muhurtas (each 1/15th of daylight length).
    Includes Abhijit Muhurta (8th muhurta) and Dur Muhurtas.
    """
    day_duration_secs = (sunset_utc - sunrise_utc).total_seconds()
    muhurta_secs = day_duration_secs / 15.0

    # 8th Muhurta is Abhijit
    abhijit_start = sunrise_utc + timedelta(seconds=7 * muhurta_secs)
    abhijit_end = sunrise_utc + timedelta(seconds=8 * muhurta_secs)

    # Dur Muhurta 1-indexed parts
    # Sun(6): 14; Mon(0): 8, 9; Tue(1): 4, 11; Wed(2): 8; Thu(3): 6, 7; Fri(4): 4, 9; Sat(5): 2, 3
    dur_muhurta_parts = {
        6: [14],
        0: [8, 9],
        1: [4, 11],
        2: [8],
        3: [6, 7],
        4: [4, 9],
        5: [2, 3],
    }

    dur_windows = []
    for part in dur_muhurta_parts.get(weekday_py, []):
        d_start = sunrise_utc + timedelta(seconds=(part - 1) * muhurta_secs)
        d_end = sunrise_utc + timedelta(seconds=part * muhurta_secs)
        dur_windows.append({
            "part": part,
            "start_utc": d_start.isoformat(),
            "end_utc": d_end.isoformat(),
            "duration_minutes": round(muhurta_secs / 60.0, 1),
        })

    is_abhijit_tainted = (weekday_py == 2)  # On Wednesday, Abhijit coincides with Dur Muhurta

    return {
        "abhijit": {
            "start_utc": abhijit_start.isoformat(),
            "end_utc": abhijit_end.isoformat(),
            "duration_minutes": round(muhurta_secs / 60.0, 1),
            "is_dur_muhurta_clash": is_abhijit_tainted,
        },
        "dur_muhurtas": dur_windows,
        "muhurta_duration_minutes": round(muhurta_secs / 60.0, 1),
    }


def get_moon_and_sun_longitudes(jd: float, ayanamsa_id: int = 0) -> Tuple[float, float, float, float]:
    """Returns (moon_tropical, sun_tropical, moon_sidereal, sun_sidereal) in degrees 0-360."""
    moon_trop = swe.calc_ut(jd, swe.SE_MOON, 0)[0][0] % 360.0
    sun_trop = swe.calc_ut(jd, swe.SE_SUN, 0)[0][0] % 360.0
    ayanamsa_deg = xalen.ayanamsa(jd, ayanamsa_id)
    moon_sid = (moon_trop - ayanamsa_deg) % 360.0
    sun_sid = (sun_trop - ayanamsa_deg) % 360.0
    return moon_trop, sun_trop, moon_sid, sun_sid


def get_tithi_at_jd(jd: float) -> Tuple[int, str, str, float]:
    """Calculate Tithi at Julian Day.
    Returns (tithi_number 1..30, tithi_name, paksha, progress_fraction 0..1).
    """
    moon_trop, sun_trop, _, _ = get_moon_and_sun_longitudes(jd)
    diff = (moon_trop - sun_trop) % 360.0
    tithi_idx = int(diff // 12.0) + 1
    tithi_idx = max(1, min(30, tithi_idx))
    progress = (diff % 12.0) / 12.0
    paksha = "Shukla" if tithi_idx <= 15 else "Krishna"
    name = TITHI_NAMES[tithi_idx - 1]
    return tithi_idx, name, paksha, progress


def find_tithi_transition(jd_anchor: float, forward: bool = True) -> float:
    """Find the exact JD timestamp when the current Tithi transitions (ends or starts).
    Uses binary search over a +/- 30-hour span.
    """
    current_tithi, _, _, _ = get_tithi_at_jd(jd_anchor)
    target_boundary = (current_tithi if forward else current_tithi - 1) * 12.0
    
    low_jd = jd_anchor
    high_jd = jd_anchor + (1.3 if forward else -1.3)
    if not forward:
        low_jd, high_jd = high_jd, low_jd

    for _ in range(24):
        mid_jd = (low_jd + high_jd) / 2.0
        m_trop, s_trop, _, _ = get_moon_and_sun_longitudes(mid_jd)
        diff = (m_trop - s_trop) % 360.0
        
        # Handle wrap around 360 for Amavasya/Pratipada
        if target_boundary == 360.0 or target_boundary == 0.0:
            if forward:
                is_after = diff < 60.0 and (m_trop - s_trop) >= 0.0
            else:
                is_after = diff >= 300.0
        else:
            is_after = (diff >= target_boundary)

        if is_after == forward:
            high_jd = mid_jd
        else:
            low_jd = mid_jd

    return (low_jd + high_jd) / 2.0


def get_nakshatra_at_jd(jd: float, ayanamsa_id: int = 0) -> Tuple[int, str, str, int, float]:
    """Calculate Nakshatra at Julian Day.
    Returns (nakshatra_index 1..27, name, lord, pada 1..4, progress_fraction 0..1).
    """
    _, _, moon_sid, _ = get_moon_and_sun_longitudes(jd, ayanamsa_id)
    span = 360.0 / 27.0  # 13 deg 20 min = 13.33333333 deg
    nak_idx = int(moon_sid // span) + 1
    nak_idx = max(1, min(27, nak_idx))
    deg_in_nak = moon_sid % span
    pada = int(deg_in_nak // (span / 4.0)) + 1
    pada = max(1, min(4, pada))
    progress = deg_in_nak / span
    nak_info = NAKSHATRAS[nak_idx - 1]
    return nak_idx, nak_info["name"], nak_info["lord"], pada, progress


def find_nakshatra_transition(jd_anchor: float, ayanamsa_id: int = 0, forward: bool = True) -> float:
    """Find the exact JD timestamp when the current Nakshatra transitions (ends or starts).
    Uses binary search over a +/- 30-hour span.
    """
    nak_idx, _, _, _, _ = get_nakshatra_at_jd(jd_anchor, ayanamsa_id)
    span = 360.0 / 27.0
    target_deg = (nak_idx if forward else nak_idx - 1) * span

    low_jd = jd_anchor
    high_jd = jd_anchor + (1.3 if forward else -1.3)
    if not forward:
        low_jd, high_jd = high_jd, low_jd

    for _ in range(24):
        mid_jd = (low_jd + high_jd) / 2.0
        _, _, moon_sid, _ = get_moon_and_sun_longitudes(mid_jd, ayanamsa_id)
        if target_deg == 360.0 or target_deg == 0.0:
            is_after = (moon_sid < 60.0) if forward else (moon_sid >= 300.0)
        else:
            is_after = (moon_sid >= target_deg)

        if is_after == forward:
            high_jd = mid_jd
        else:
            low_jd = mid_jd

    return (low_jd + high_jd) / 2.0


def calculate_varjyam_and_amrita(nak_idx: int, nak_start_utc: datetime, nak_end_utc: datetime) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Calculate the 4-ghatika Varjyam (Tyajyam) and Amrita Kalam intervals for the Nakshatra span.
    1 ghatika = 1/60th of nakshatra duration.
    Varjyam lasts 4 ghatikas.
    """
    nak_duration_secs = (nak_end_utc - nak_start_utc).total_seconds()
    ghatika_secs = nak_duration_secs / 60.0

    # 1. Varjyam
    varjyam_start_ghatika = VARJYAM_START_GHATIKA.get(nak_idx, 30.0)
    varjyam_start = nak_start_utc + timedelta(seconds=varjyam_start_ghatika * ghatika_secs)
    varjyam_end = varjyam_start + timedelta(seconds=4.0 * ghatika_secs)

    # 2. Amrita Kalam
    amrita_start_ghatika = AMRITA_START_GHATIKA.get(nak_idx, 42.0)
    amrita_start = nak_start_utc + timedelta(seconds=amrita_start_ghatika * ghatika_secs)
    amrita_end = amrita_start + timedelta(seconds=4.0 * ghatika_secs)

    varjyam_info = {
        "start_utc": varjyam_start.isoformat(),
        "end_utc": varjyam_end.isoformat(),
        "start_ghatika": varjyam_start_ghatika,
        "duration_minutes": round((4.0 * ghatika_secs) / 60.0, 1),
    }

    amrita_info = {
        "start_utc": amrita_start.isoformat(),
        "end_utc": amrita_end.isoformat(),
        "start_ghatika": amrita_start_ghatika,
        "duration_minutes": round((4.0 * ghatika_secs) / 60.0, 1),
    }

    return varjyam_info, amrita_info


def calculate_daily_panchangam(
    event_date: date,
    latitude: float,
    longitude: float,
    timezone_str: str,
    ayanamsa_id: int = 0,
) -> Dict[str, Any]:
    """Calculate comprehensive, location-specific daily Panchangam for a single date.
    All intervals respect transitions during the day.
    """
    tz = ZoneInfo(timezone_str)
    sunrise_utc, sunset_utc, solar_noon_utc = calculate_solar_sunrise_sunset(event_date, latitude, longitude)
    sunrise_jd = datetime_to_jd(sunrise_utc)

    # Day of week
    local_sunrise_dt = sunrise_utc.astimezone(tz)
    weekday_py = local_sunrise_dt.weekday()  # 0=Mon..6=Sun
    weekday_en = WEEKDAY_NAMES_EN[weekday_py]
    weekday_ta = WEEKDAY_NAMES_TA[weekday_py]
    vara_name = WEEKDAY_VARA[weekday_py]

    # Inauspicious octants (Rahu, Yama, Gulikai)
    octants = get_day_octant_periods(sunrise_utc, sunset_utc, weekday_py)

    # 15 Muhurtas (Abhijit, Dur Muhurtas)
    muhurtas = get_daytime_muhurtas(sunrise_utc, sunset_utc, weekday_py)

    # Tithi at sunrise & transition
    tithi_idx, tithi_name, paksha, _ = get_tithi_at_jd(sunrise_jd)
    tithi_start_jd = find_tithi_transition(sunrise_jd, forward=False)
    tithi_end_jd = find_tithi_transition(sunrise_jd, forward=True)
    tithi_start_utc = jd_to_datetime(tithi_start_jd)
    tithi_end_utc = jd_to_datetime(tithi_end_jd)

    # Nakshatra at sunrise & transition
    nak_idx, nak_name, nak_lord, nak_pada, _ = get_nakshatra_at_jd(sunrise_jd, ayanamsa_id)
    nak_start_jd = find_nakshatra_transition(sunrise_jd, ayanamsa_id, forward=False)
    nak_end_jd = find_nakshatra_transition(sunrise_jd, ayanamsa_id, forward=True)
    nak_start_utc = jd_to_datetime(nak_start_jd)
    nak_end_utc = jd_to_datetime(nak_end_jd)

    # Varjyam and Amrita Kalam for the current Nakshatra
    varjyam_info, amrita_info = calculate_varjyam_and_amrita(nak_idx, nak_start_utc, nak_end_utc)

    # Yoga and Karana at sunrise
    _, _, moon_sid, sun_sid = get_moon_and_sun_longitudes(sunrise_jd, ayanamsa_id)
    yoga_sum = (moon_sid + sun_sid) % 360.0
    yoga_idx = int(yoga_sum // (360.0 / 27.0)) + 1
    yoga_idx = max(1, min(27, yoga_idx))
    yoga_name = YOGA_NAMES[yoga_idx - 1]

    # Karana (each tithi has 2 karanas = 6 deg each)
    moon_trop, sun_trop, _, _ = get_moon_and_sun_longitudes(sunrise_jd)
    diff = (moon_trop - sun_trop) % 360.0
    karana_num = int(diff // 6.0) + 1  # 1..60
    if karana_num == 1:
        karana_name = "Kimstughna"
    elif karana_num >= 58:
        if karana_num == 58:
            karana_name = "Shakuni"
        elif karana_num == 59:
            karana_name = "Chatushpada"
        else:
            karana_name = "Naga"
    else:
        repeating = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"]
        karana_name = repeating[(karana_num - 2) % 7]

    return {
        "date": event_date.isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
        },
        "astronomical": {
            "sunrise_utc": sunrise_utc.isoformat(),
            "sunrise_local": sunrise_utc.astimezone(tz).strftime("%H:%M:%S"),
            "sunset_utc": sunset_utc.isoformat(),
            "sunset_local": sunset_utc.astimezone(tz).strftime("%H:%M:%S"),
            "solar_noon_utc": solar_noon_utc.isoformat(),
            "solar_noon_local": solar_noon_utc.astimezone(tz).strftime("%H:%M:%S"),
            "day_length_hours": round((sunset_utc - sunrise_utc).total_seconds() / 3600.0, 2),
        },
        "vara": {
            "weekday_number": weekday_py + 1,
            "name_en": weekday_en,
            "name_ta": weekday_ta,
            "sanskrit_name": vara_name,
        },
        "tithi": {
            "number": tithi_idx,
            "name": tithi_name,
            "name_ta": TITHI_TAMIL[tithi_idx - 1],
            "paksha": paksha,
            "start_time_utc": tithi_start_utc.isoformat(),
            "start_time_local": tithi_start_utc.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time_utc": tithi_end_utc.isoformat(),
            "end_time_local": tithi_end_utc.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
        },
        "nakshatra": {
            "number": nak_idx,
            "name": nak_name,
            "name_ta": NAKSHATRAS[nak_idx - 1]["name_ta"],
            "lord": nak_lord,
            "pada": nak_pada,
            "start_time_utc": nak_start_utc.isoformat(),
            "start_time_local": nak_start_utc.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time_utc": nak_end_utc.isoformat(),
            "end_time_local": nak_end_utc.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
        },
        "yoga": {
            "number": yoga_idx,
            "name": yoga_name,
        },
        "karana": {
            "number": karana_num,
            "name": karana_name,
        },
        "inauspicious_periods": octants,
        "auspicious_periods": {
            "abhijit": muhurtas["abhijit"],
            "amrita_kalam": amrita_info,
        },
        "varjyam": varjyam_info,
        "dur_muhurtas": muhurtas["dur_muhurtas"],
    }


def get_slot_lagna_and_planets(
    slot_utc: datetime,
    latitude: float,
    longitude: float,
    ayanamsa_id: int = 0,
) -> Dict[str, Any]:
    """Calculate the rising Lagna and planetary placements in whole-sign bhavas for a candidate time slot."""
    jd = datetime_to_jd(slot_utc)
    from app.services.ephemeris import compute_ascendant_and_houses, compute_planetary_positions

    ascendant, _, houses = compute_ascendant_and_houses(
        jd=jd,
        lat=latitude,
        lon=longitude,
        ayanamsa_id=ayanamsa_id,
        house_system_id=0,  # Whole Sign for Vedic Muhurta
    )

    planets = compute_planetary_positions(
        jd=jd,
        ayanamsa_id=ayanamsa_id,
        include_outer=False,  # Vedic traditional 9 bodies (Navagraha)
    )

    # Determine bhava for each planet relative to Lagna (1..12)
    asc_sign = ascendant.sign_index  # 1..12
    planet_bhavas: Dict[str, Dict[str, Any]] = {}
    bhavas_occupants: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

    for p in planets:
        # Whole sign bhava calculation: (planet_sign - asc_sign) % 12 + 1
        bhava_num = ((p.sign_index - asc_sign) % 12) + 1
        bhavas_occupants[bhava_num].append(p.name)
        planet_bhavas[p.name] = {
            "sign_index": p.sign_index,
            "sign_name": p.sign_name,
            "sign_name_ta": p.sign_name_tamil,
            "degree_in_sign": round(p.degree_in_sign, 2),
            "bhava": bhava_num,
            "is_retrograde": p.is_retrograde,
        }

    return {
        "ascendant": {
            "sign_index": ascendant.sign_index,
            "sign_name": ascendant.sign_name,
            "sign_name_ta": ascendant.sign_name_tamil,
            "degree_in_sign": round(ascendant.degree_in_sign, 2),
            "nakshatra": ascendant.nakshatra.name,
            "pada": ascendant.nakshatra.pada,
        },
        "planets": planet_bhavas,
        "bhava_occupants": bhavas_occupants,
    }
