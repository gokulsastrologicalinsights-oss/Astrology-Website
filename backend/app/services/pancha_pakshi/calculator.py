"""Pancha Pakshi Shastra - Computational Engine.

Implements high-precision astronomical bio-rhythm calculations based on Sage Agastya's system.
Computes native's Janma Pakshi, 5 major day/night Yamams, 25 day + 25 night sub-periods (அந்தரங்கள்),
golden action windows, and Padupakshi caution windows.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo

from app.services.muhurta_engine.astronomy import (
    calculate_solar_sunrise_sunset,
    datetime_to_jd,
    get_tithi_at_jd,
)
from app.services.pancha_pakshi.constants import (
    BIRDS,
    BIRD_MAP,
    ACTIVITIES,
    SHUKLA_PAKSHA_STAR_BIRD,
    KRISHNA_PAKSHA_STAR_BIRD,
    SHUKLA_DAY_TABLE,
    SHUKLA_NIGHT_TABLE,
    KRISHNA_DAY_TABLE,
    KRISHNA_NIGHT_TABLE,
    ACTIVITY_CYCLE_ORDER,
)


def get_birth_bird(birth_nakshatra_idx: int, birth_paksha: str) -> Dict[str, Any]:
    """Determine native's ruling birth bird (Janma Pakshi) from Janma Nakshatra and Paksha."""
    normalized_paksha = "shukla" if "shukla" in birth_paksha.lower() or "valar" in birth_paksha.lower() else "krishna"
    
    star_idx = max(1, min(27, birth_nakshatra_idx))
    bird_id = (
        SHUKLA_PAKSHA_STAR_BIRD.get(star_idx, "vulture")
        if normalized_paksha == "shukla"
        else KRISHNA_PAKSHA_STAR_BIRD.get(star_idx, "peacock")
    )
    return BIRD_MAP[bird_id]


def build_sub_periods(
    major_start_utc: datetime,
    major_end_utc: datetime,
    major_activity_id: str,
    major_yamam_idx: int,
    period_type: str,
    tz: ZoneInfo,
) -> List[Dict[str, Any]]:
    """Subdivide a major Yamam into 5 equal Antara (sub) periods."""
    major_dur_secs = (major_end_utc - major_start_utc).total_seconds()
    sub_dur_secs = major_dur_secs / 5.0
    major_act = ACTIVITIES[major_activity_id]

    start_idx = ACTIVITY_CYCLE_ORDER.index(major_activity_id)

    sub_periods: List[Dict[str, Any]] = []
    for s_idx in range(5):
        sub_act_id = ACTIVITY_CYCLE_ORDER[(start_idx + s_idx) % 5]
        sub_act = ACTIVITIES[sub_act_id]

        s_start_utc = major_start_utc + timedelta(seconds=s_idx * sub_dur_secs)
        s_end_utc = major_start_utc + timedelta(seconds=(s_idx + 1) * sub_dur_secs)

        s_start_local = s_start_utc.astimezone(tz)
        s_end_local = s_end_utc.astimezone(tz)

        # Weighted power score (70% major yamam + 30% sub-yamam)
        combined_power = round((major_act["power_score"] * 0.70) + (sub_act["power_score"] * 0.30))

        if combined_power >= 80:
            rating = "golden"
            rating_label_en = "Golden Victory Window"
            rating_label_ta = "தங்க வெற்றித் தருணம்"
        elif combined_power >= 50:
            rating = "favorable"
            rating_label_en = "Favorable / Dynamic"
            rating_label_ta = "சுப / சுறுசுறுப்பான நேரம்"
        elif combined_power >= 25:
            rating = "neutral"
            rating_label_en = "Moderate / Routine"
            rating_label_ta = "சாதாரண நேரம்"
        else:
            rating = "danger"
            rating_label_en = "Padupakshi / Critical Caution"
            rating_label_ta = "படுபட்சி / எச்சரிக்கை நேரம்"

        sub_periods.append({
            "sub_index": s_idx + 1,
            "global_sub_index": (major_yamam_idx - 1) * 5 + s_idx + 1,
            "period_type": period_type,
            "major_activity": major_act["id"],
            "major_activity_en": major_act["name_en"],
            "major_activity_ta": major_act["name_ta"],
            "sub_activity": sub_act["id"],
            "sub_activity_en": sub_act["name_en"],
            "sub_activity_ta": sub_act["name_ta"],
            "power_score": combined_power,
            "rating": rating,
            "rating_label_en": rating_label_en,
            "rating_label_ta": rating_label_ta,
            "color": sub_act["color"],
            "start_time_utc": s_start_utc.isoformat(),
            "end_time_utc": s_end_utc.isoformat(),
            "start_time_local": s_start_local.strftime("%H:%M:%S"),
            "end_time_local": s_end_local.strftime("%H:%M:%S"),
            "duration_minutes": round(sub_dur_secs / 60.0, 1),
            "recommended_en": major_act["recommended_en"][:2] if combined_power >= 50 else [],
            "recommended_ta": major_act["recommended_ta"][:2] if combined_power >= 50 else [],
            "avoid_en": major_act["avoid_en"] if combined_power < 50 else [],
            "avoid_ta": major_act["avoid_ta"] if combined_power < 50 else [],
        })

    return sub_periods


def calculate_pancha_pakshi_bio_rhythms(
    target_date: date,
    latitude: float,
    longitude: float,
    timezone_str: str,
    birth_nakshatra_idx: int,
    birth_paksha: str = "shukla",
) -> Dict[str, Any]:
    """Calculate comprehensive Pancha Pakshi 5-Yamam and 25-Antara bio-rhythms for a specific date and observer location."""
    tz = ZoneInfo(timezone_str)

    # 1. Native's birth bird
    birth_bird = get_birth_bird(birth_nakshatra_idx, birth_paksha)
    birth_bird_id = birth_bird["id"]

    # 2. Astronomical solar boundaries
    sunrise_utc, sunset_utc, solar_noon_utc = calculate_solar_sunrise_sunset(target_date, latitude, longitude)
    next_sunrise_utc, _, _ = calculate_solar_sunrise_sunset(target_date + timedelta(days=1), latitude, longitude)

    local_sunrise_dt = sunrise_utc.astimezone(tz)
    weekday_py = local_sunrise_dt.weekday()  # 0=Mon..6=Sun

    # 3. Target date's actual astronomical paksha from Tithi at sunrise
    sunrise_jd = datetime_to_jd(sunrise_utc)
    tithi_idx, tithi_name, tithi_paksha, _ = get_tithi_at_jd(sunrise_jd)
    target_is_shukla = (tithi_idx <= 15)
    target_paksha = "shukla" if target_is_shukla else "krishna"
    target_paksha_ta = "வளர்பிறை" if target_is_shukla else "தேய்பிறை"

    # 4. Day & Night durations
    day_duration_secs = (sunset_utc - sunrise_utc).total_seconds()
    if day_duration_secs <= 0:
        day_duration_secs = 12 * 3600.0
    day_yamam_secs = day_duration_secs / 5.0

    night_duration_secs = (next_sunrise_utc - sunset_utc).total_seconds()
    if night_duration_secs <= 0:
        night_duration_secs = 12 * 3600.0
    night_yamam_secs = night_duration_secs / 5.0

    # 5. Select Agastya activity matrices
    day_matrix = SHUKLA_DAY_TABLE[weekday_py] if target_is_shukla else KRISHNA_DAY_TABLE[weekday_py]
    night_matrix = SHUKLA_NIGHT_TABLE[weekday_py] if target_is_shukla else KRISHNA_NIGHT_TABLE[weekday_py]

    # 6. Build 5 Major Day Yamams + 25 Day Antaras
    day_yamams: List[Dict[str, Any]] = []
    all_day_antaras: List[Dict[str, Any]] = []

    for y_idx in range(5):
        y_start_utc = sunrise_utc + timedelta(seconds=y_idx * day_yamam_secs)
        y_end_utc = sunrise_utc + timedelta(seconds=(y_idx + 1) * day_yamam_secs)

        # Activity of each bird in this yamam
        all_birds_activities: Dict[str, str] = {}
        ruling_bird_id = ""
        for b in BIRDS:
            b_act = day_matrix[b["id"]][y_idx]
            all_birds_activities[b["id"]] = b_act
            if b_act == "ruling":
                ruling_bird_id = b["id"]

        native_act_id = day_matrix[birth_bird_id][y_idx]
        native_act = ACTIVITIES[native_act_id]

        y_start_local = y_start_utc.astimezone(tz)
        y_end_local = y_end_utc.astimezone(tz)

        # 5 Sub-periods for native's bird
        sub_list = build_sub_periods(
            major_start_utc=y_start_utc,
            major_end_utc=y_end_utc,
            major_activity_id=native_act_id,
            major_yamam_idx=y_idx + 1,
            period_type="day",
            tz=tz,
        )
        all_day_antaras.extend(sub_list)

        day_yamams.append({
            "yamam_index": y_idx + 1,
            "period_type": "day",
            "name_en": f"Day Yamam {y_idx + 1}",
            "name_ta": f"பகல் ஜாமம் {y_idx + 1}",
            "native_activity": native_act["id"],
            "native_activity_en": native_act["name_en"],
            "native_activity_ta": native_act["name_ta"],
            "power_score": native_act["power_score"],
            "nature": native_act["nature"],
            "color": native_act["color"],
            "ruling_bird": BIRD_MAP[ruling_bird_id]["name_en"],
            "ruling_bird_ta": BIRD_MAP[ruling_bird_id]["name_ta"],
            "start_time_utc": y_start_utc.isoformat(),
            "end_time_utc": y_end_utc.isoformat(),
            "start_time_local": y_start_local.strftime("%H:%M:%S"),
            "end_time_local": y_end_local.strftime("%H:%M:%S"),
            "duration_minutes": round(day_yamam_secs / 60.0, 1),
            "sub_periods": sub_list,
            "all_birds_state": all_birds_activities,
        })

    # 7. Build 5 Major Night Yamams + 25 Night Antaras
    night_yamams: List[Dict[str, Any]] = []
    all_night_antaras: List[Dict[str, Any]] = []

    for y_idx in range(5):
        y_start_utc = sunset_utc + timedelta(seconds=y_idx * night_yamam_secs)
        y_end_utc = sunset_utc + timedelta(seconds=(y_idx + 1) * night_yamam_secs)

        all_birds_activities: Dict[str, str] = {}
        ruling_bird_id = ""
        for b in BIRDS:
            b_act = night_matrix[b["id"]][y_idx]
            all_birds_activities[b["id"]] = b_act
            if b_act == "ruling":
                ruling_bird_id = b["id"]

        native_act_id = night_matrix[birth_bird_id][y_idx]
        native_act = ACTIVITIES[native_act_id]

        y_start_local = y_start_utc.astimezone(tz)
        y_end_local = y_end_utc.astimezone(tz)

        sub_list = build_sub_periods(
            major_start_utc=y_start_utc,
            major_end_utc=y_end_utc,
            major_activity_id=native_act_id,
            major_yamam_idx=y_idx + 1,
            period_type="night",
            tz=tz,
        )
        all_night_antaras.extend(sub_list)

        night_yamams.append({
            "yamam_index": y_idx + 1,
            "period_type": "night",
            "name_en": f"Night Yamam {y_idx + 1}",
            "name_ta": f"இரவு ஜாமம் {y_idx + 1}",
            "native_activity": native_act["id"],
            "native_activity_en": native_act["name_en"],
            "native_activity_ta": native_act["name_ta"],
            "power_score": native_act["power_score"],
            "nature": native_act["nature"],
            "color": native_act["color"],
            "ruling_bird": BIRD_MAP[ruling_bird_id]["name_en"],
            "ruling_bird_ta": BIRD_MAP[ruling_bird_id]["name_ta"],
            "start_time_utc": y_start_utc.isoformat(),
            "end_time_utc": y_end_utc.isoformat(),
            "start_time_local": y_start_local.strftime("%H:%M:%S"),
            "end_time_local": y_end_local.strftime("%H:%M:%S"),
            "duration_minutes": round(night_yamam_secs / 60.0, 1),
            "sub_periods": sub_list,
            "all_birds_state": all_birds_activities,
        })

    all_antaras = all_day_antaras + all_night_antaras

    # 8. Filter Golden Action Windows (>= 80% power) and Padupakshi Windows (<= 25% power)
    golden_windows = [a for a in all_antaras if a["power_score"] >= 80]
    padupakshi_windows = [a for a in all_antaras if a["power_score"] <= 25]

    return {
        "target_date": target_date.isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
        },
        "astronomical": {
            "sunrise_utc": sunrise_utc.isoformat(),
            "sunrise_local": local_sunrise_dt.strftime("%H:%M:%S"),
            "sunset_utc": sunset_utc.isoformat(),
            "sunset_local": sunset_utc.astimezone(tz).strftime("%H:%M:%S"),
            "next_sunrise_local": next_sunrise_utc.astimezone(tz).strftime("%H:%M:%S"),
            "day_length_hours": round(day_duration_secs / 3600.0, 2),
            "night_length_hours": round(night_duration_secs / 3600.0, 2),
            "tithi": {
                "number": tithi_idx,
                "name": tithi_name,
                "paksha": tithi_paksha,
            },
            "target_paksha": target_paksha,
            "target_paksha_ta": target_paksha_ta,
        },
        "birth_details": {
            "nakshatra_number": birth_nakshatra_idx,
            "birth_paksha": birth_paksha,
        },
        "birth_bird": birth_bird,
        "day_yamam_duration_minutes": round(day_yamam_secs / 60.0, 1),
        "night_yamam_duration_minutes": round(night_yamam_secs / 60.0, 1),
        "sub_period_duration_minutes": round((day_yamam_secs / 5.0) / 60.0, 1),
        "day_yamams": day_yamams,
        "night_yamams": night_yamams,
        "all_antaras": all_antaras,
        "golden_windows": golden_windows,
        "padupakshi_windows": padupakshi_windows,
        "total_golden_windows": len(golden_windows),
        "total_padupakshi_windows": len(padupakshi_windows),
    }
