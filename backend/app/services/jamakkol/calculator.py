"""Jamakkol Prasanam (ஜாமக்கோள் பிரசன்னம்) computational engine.

Executes precise calculations for:
1. Dynamic 8 Day & 8 Night Jamams (16 total per 24 hours) based on exact local Sunrise & Sunset.
2. The 3 Core Pillars: Udhayam (உதயம்), Aarudham (ஆருடம்), and Kavippu (கவிப்பு).
3. The 8 Outer Jama Grahas mapped into the 8 Chara & Ubhaya signs (anti-clockwise).
4. Real-time Transit Planets (Vaanveethi Grahas) + Gulika/Mandi using the Swiss Ephemeris.
5. House placements counted from Udhayam and Aarudham.
6. Full classical rules implementation:
   - Snapshot Watch Time Predictions (Udayam & Arudam Relation 1/1, 5/9, 3/11, 2/12, 6/8, 1/7, 4/10)
   - Ardhomukha / Urdhomukha / Triyangmukha facing rules
   - Sirosodayam / Pristodaya / Siropristodaya rising sign rules
   - Subh Udayam (Leo-Cap) & Subh Arudam (Aqua-Can) balance
   - Udayam & 10th/11th Lord connection & Parivartana
   - Kavippu in 2nd / 11th and afflicted planets
   - Approaching vs Crossed planets (Past, Present & Future)
   - Query karakatwa detection & verification from 10th Lord and approaching planets
"""

import math
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo

from app.services.muhurta_engine.astronomy import (
    calculate_solar_sunrise_sunset,
    datetime_to_jd,
)
from app.services.ephemeris import (
    compute_planetary_positions,
    get_sign_info,
    get_nakshatra_detail,
)
from app.services.jamakkol.constants import (
    ZODIAC_SIGNS,
    JAMA_SIGNS_ANTICLOCKWISE,
    JAMA_GRAHAS,
    JAMA_GRAHA_INDEX,
    WEEKDAY_TO_DAY_LORD,
    NIGHT_START_LORD,
    SURYA_VEETHI_RULES,
    DIRECTIONS_MAP,
    PLANET_DIGNITIES,
    SIGN_LORDS,
    SUBH_UDAYAM_SIGNS,
    SUBH_ARUDAM_SIGNS,
    PLANET_QUERY_KARAKATWAS,
    RELATIONSHIP_KARAKAS,
    GOVT_POLITICS_KARAKAS,
    COMMODITY_KARAKAS,
    KAVIPPU_BHAVA_EFFECTS,
    UDAYAM_LORD_THOUGHT_EFFECTS,
    PLANET_ATTRIBUTES,
    JEEVA_KARAKA_MAP,
    BLACK_MAGIC_SORCERER_KARAKAS,
    APPROACHING_PLANET_MUHURTA_SIGNIFICATIONS,
)


def format_dms(degrees_val: float) -> str:
    """Format decimal degrees into standard DD° MM' SS\" string."""
    deg = int(degrees_val)
    rem = (degrees_val - deg) * 60.0
    minutes = int(rem)
    seconds = int(round((rem - minutes) * 60.0))
    if seconds >= 60:
        minutes += 1
        seconds = 0
    if minutes >= 60:
        deg += 1
        minutes = 0
    return f"{deg:02d}° {minutes:02d}' {seconds:02d}\""


def calculate_jamakkol_prasanam(
    query_dt_str: str,
    latitude: float,
    longitude: float,
    tz_str: str = "Asia/Kolkata",
    ayanamsa_id: int = 0,
    query_text: Optional[str] = None,
    query_category: Optional[str] = "general",
    querent_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Calculate complete Jamakkol Prasanam chart and predictions."""
    tz = ZoneInfo(tz_str)

    # 1. Parse target datetime
    try:
        query_dt_local = datetime.fromisoformat(query_dt_str)
        if query_dt_local.tzinfo is None:
            query_dt_local = query_dt_local.replace(tzinfo=tz)
        else:
            query_dt_local = query_dt_local.astimezone(tz)
    except Exception:
        query_dt_local = datetime.now(tz)

    query_dt_utc = query_dt_local.astimezone(timezone.utc)
    target_date = query_dt_local.date()

    # 2. Compute Sunrise & Sunset for target date, previous date, and next date
    sr_curr_utc, ss_curr_utc, _ = calculate_solar_sunrise_sunset(target_date, latitude, longitude)
    sr_prev_utc, ss_prev_utc, _ = calculate_solar_sunrise_sunset(target_date - timedelta(days=1), latitude, longitude)
    sr_next_utc, ss_next_utc, _ = calculate_solar_sunrise_sunset(target_date + timedelta(days=1), latitude, longitude)

    sr_curr_local = sr_curr_utc.astimezone(tz)
    ss_curr_local = ss_curr_utc.astimezone(tz)
    sr_prev_local = sr_prev_utc.astimezone(tz)
    ss_prev_local = ss_prev_utc.astimezone(tz)
    sr_next_local = sr_next_utc.astimezone(tz)

    # 3. Determine if Day or Night period and identify running Vedic Day
    if query_dt_local >= sr_curr_local:
        if query_dt_local < ss_curr_local:
            is_day = True
            period_type = "Day"
            period_start = sr_curr_local
            period_end = ss_curr_local
            vedic_date = target_date
        else:
            is_day = False
            period_type = "Night"
            period_start = ss_curr_local
            period_end = sr_next_local
            vedic_date = target_date
    else:
        is_day = False
        period_type = "Night"
        period_start = ss_prev_local
        period_end = sr_curr_local
        vedic_date = target_date - timedelta(days=1)

    # 4. Compute Jamam details (8 subdivisions of the active period)
    period_duration_sec = (period_end - period_start).total_seconds()
    jamam_duration_sec = period_duration_sec / 8.0
    elapsed_period_sec = (query_dt_local - period_start).total_seconds()

    jamam_number = min(8, max(1, int(elapsed_period_sec // jamam_duration_sec) + 1))
    jamam_start_local = period_start + timedelta(seconds=(jamam_number - 1) * jamam_duration_sec)
    jamam_end_local = period_start + timedelta(seconds=jamam_number * jamam_duration_sec)
    elapsed_in_jamam_fraction = (query_dt_local - jamam_start_local).total_seconds() / jamam_duration_sec
    elapsed_in_jamam_fraction = max(0.0, min(1.0, elapsed_in_jamam_fraction))

    # Day Lord from Vedic date's weekday
    vedic_weekday = vedic_date.weekday()  # 0=Mon ... 6=Sun
    day_lord_id = WEEKDAY_TO_DAY_LORD[vedic_weekday]
    day_lord_meta = JAMA_GRAHAS[JAMA_GRAHA_INDEX[day_lord_id]]

    if is_day:
        start_planet_idx = JAMA_GRAHA_INDEX[day_lord_id]
        active_jamam_planet_idx = (start_planet_idx + (jamam_number - 1)) % 8
    else:
        night_start_planet_id = NIGHT_START_LORD[day_lord_id]
        start_planet_idx = JAMA_GRAHA_INDEX[night_start_planet_id]
        active_jamam_planet_idx = (start_planet_idx + (jamam_number - 1)) % 8

    active_jamam_ruler = JAMA_GRAHAS[active_jamam_planet_idx]

    # 5. Astronomical transit planetary positions
    jd = datetime_to_jd(query_dt_utc)
    raw_planets = compute_planetary_positions(jd, ayanamsa_id=ayanamsa_id, include_outer=False)

    transit_planets: List[Dict[str, Any]] = []
    sun_lon = 0.0
    for p in raw_planets:
        sign_info = ZODIAC_SIGNS[p.sign_index]
        p_dignity = PLANET_DIGNITIES.get(p.name, {})
        is_exalted = (p.sign_index == p_dignity.get("exalted"))
        is_debilitated = (p.sign_index == p_dignity.get("debilitated"))

        p_data = {
            "name_en": p.name,
            "name_ta": p.sign_name_tamil,
            "sign_index": p.sign_index,
            "sign_name_en": sign_info["name_en"],
            "sign_name_ta": sign_info["name_ta"],
            "longitude": round(p.longitude, 4),
            "degree_in_sign": round(p.degree_in_sign, 4),
            "dms": format_dms(p.degree_in_sign),
            "is_retrograde": p.is_retrograde,
            "speed": round(p.speed_deg_per_day, 4),
            "nakshatra": f"{p.nakshatra.name} (Pada {p.nakshatra.pada})",
            "is_exalted": is_exalted,
            "is_debilitated": is_debilitated,
        }
        transit_planets.append(p_data)
        if p.name == "Sun":
            sun_lon = p.longitude

    # Gulika / Mandi
    mandi_sign_idx = (vedic_weekday + (jamam_number * 2)) % 12 + 1
    mandi_sign_info = ZODIAC_SIGNS[mandi_sign_idx]
    transit_planets.append({
        "name_en": "Gulika (Mandi)",
        "name_ta": "குளிகன் (மாந்தி)",
        "sign_index": mandi_sign_idx,
        "sign_name_en": mandi_sign_info["name_en"],
        "sign_name_ta": mandi_sign_info["name_ta"],
        "longitude": round((mandi_sign_idx - 1) * 30.0 + 15.0, 4),
        "degree_in_sign": 15.0,
        "dms": "15° 00' 00\"",
        "is_retrograde": False,
        "speed": 0.0,
        "nakshatra": "Shatabhisha (Pada 1)",
        "is_exalted": False,
        "is_debilitated": False,
    })

    # 6. Surya Veethi (Sun's Path)
    sun_sign_idx = int(sun_lon // 30.0) + 1
    surya_veethi_info = SURYA_VEETHI_RULES.get(
        sun_sign_idx,
        {"veethi_id": "rishabha", "name_en": "Rishabha Veethi", "name_ta": "ரிஷப வீதி", "anchor_sign": 2}
    )

    # 7. Calculate Udhayam (உதயம்)
    # Starts at Sun's longitude and progresses 360 degrees across the 8 Jamams (day or night)
    progress_ratio = max(0.0, min(1.0, elapsed_period_sec / period_duration_sec))
    udhayam_lon = (sun_lon + (progress_ratio * 360.0)) % 360.0
    udhayam_sign_idx = int(udhayam_lon // 30.0) + 1
    udhayam_deg_in_sign = udhayam_lon % 30.0
    udhayam_nak = get_nakshatra_detail(udhayam_lon)
    udhayam_sign_meta = ZODIAC_SIGNS[udhayam_sign_idx]

    udhayam_data = {
        "sign_index": udhayam_sign_idx,
        "sign_name_en": udhayam_sign_meta["name_en"],
        "sign_name_ta": udhayam_sign_meta["name_ta"],
        "longitude": round(udhayam_lon, 4),
        "degree_in_sign": round(udhayam_deg_in_sign, 4),
        "dms": format_dms(udhayam_deg_in_sign),
        "lord_en": udhayam_sign_meta["lord_en"],
        "lord_ta": udhayam_sign_meta["lord_ta"],
        "nakshatra_name": udhayam_nak.name,
        "pada": udhayam_nak.pada,
        "nature": udhayam_sign_meta["nature"],
        "nature_ta": udhayam_sign_meta["nature_ta"],
        "rising_nature": udhayam_sign_meta["rising_nature"],
        "rising_nature_ta": udhayam_sign_meta["rising_nature_ta"],
        "direction_en": udhayam_sign_meta["direction_en"],
        "direction_ta": udhayam_sign_meta["direction_ta"],
    }

    # 8. Calculate Aarudham (ஆருடம்)
    if querent_seed is not None and 1 <= querent_seed <= 249:
        aarudham_sign_idx = ((querent_seed - 1) % 12) + 1
        aarudham_deg_in_sign = (((querent_seed - 1) % 9) * 3.333333) % 30.0
        aarudham_lon = (aarudham_sign_idx - 1) * 30.0 + aarudham_deg_in_sign
        calc_basis = f"Querent Seed Number ({querent_seed})"
    else:
        m = query_dt_local.minute
        s = query_dt_local.second
        block_idx = m // 5  # 0 to 11
        aarudham_sign_idx = block_idx + 1
        block_progress = ((m % 5) * 60.0 + s) / 300.0
        aarudham_deg_in_sign = block_progress * 30.0
        aarudham_lon = (aarudham_sign_idx - 1) * 30.0 + aarudham_deg_in_sign
        calc_basis = f"5-Minute Clock Window ({m:02d}:{s:02d})"

    aarudham_sign_meta = ZODIAC_SIGNS[aarudham_sign_idx]
    aarudham_nak = get_nakshatra_detail(aarudham_lon)

    aarudham_data = {
        "sign_index": aarudham_sign_idx,
        "sign_name_en": aarudham_sign_meta["name_en"],
        "sign_name_ta": aarudham_sign_meta["name_ta"],
        "longitude": round(aarudham_lon, 4),
        "degree_in_sign": round(aarudham_deg_in_sign, 4),
        "dms": format_dms(aarudham_deg_in_sign),
        "lord_en": aarudham_sign_meta["lord_en"],
        "lord_ta": aarudham_sign_meta["lord_ta"],
        "nakshatra_name": aarudham_nak.name,
        "pada": aarudham_nak.pada,
        "nature": aarudham_sign_meta["nature"],
        "nature_ta": aarudham_sign_meta["nature_ta"],
        "rising_nature": aarudham_sign_meta["rising_nature"],
        "rising_nature_ta": aarudham_sign_meta["rising_nature_ta"],
        "direction_en": aarudham_sign_meta["direction_en"],
        "direction_ta": aarudham_sign_meta["direction_ta"],
        "calculation_basis": calc_basis,
    }

    # 9. Calculate Kavippu (கவிப்பு)
    anchor_sign = surya_veethi_info["anchor_sign"]
    dist_arudha_to_veethi = (anchor_sign - aarudham_sign_idx) % 12
    if dist_arudha_to_veethi <= 0:
        dist_arudha_to_veethi += 12

    kavippu_sign_idx = (udhayam_sign_idx + dist_arudha_to_veethi - 1) % 12
    if kavippu_sign_idx == 0:
        kavippu_sign_idx = 12

    kavippu_deg_in_sign = (30.0 - (aarudham_deg_in_sign % 30.0)) % 30.0
    kavippu_lon = (kavippu_sign_idx - 1) * 30.0 + kavippu_deg_in_sign
    kavippu_sign_meta = ZODIAC_SIGNS[kavippu_sign_idx]

    kavippu_data = {
        "sign_index": kavippu_sign_idx,
        "sign_name_en": kavippu_sign_meta["name_en"],
        "sign_name_ta": kavippu_sign_meta["name_ta"],
        "longitude": round(kavippu_lon, 4),
        "degree_in_sign": round(kavippu_deg_in_sign, 4),
        "dms": format_dms(kavippu_deg_in_sign),
        "lord_en": kavippu_sign_meta["lord_en"],
        "lord_ta": kavippu_sign_meta["lord_ta"],
        "surya_veethi": surya_veethi_info["name_ta"],
        "surya_veethi_en": surya_veethi_info["name_en"],
        "distance_from_arudham": dist_arudha_to_veethi,
        "nature": kavippu_sign_meta["nature"],
        "nature_ta": kavippu_sign_meta["nature_ta"],
        "direction_en": kavippu_sign_meta["direction_en"],
        "direction_ta": kavippu_sign_meta["direction_ta"],
    }

    # 10. Place 8 Outer Jama Grahas
    # The active Jamam ruler is placed in Pisces (sign 12, index 0 in JAMA_SIGNS_ANTICLOCKWISE)
    # Other 7 planets follow sequentially in the 8-planet order around JAMA_SIGNS_ANTICLOCKWISE
    jama_graha_placements: List[Dict[str, Any]] = []
    outer_deg_in_sign = round((1.0 - elapsed_in_jamam_fraction) * 30.0, 2)

    for offset in range(8):
        planet_idx = (active_jamam_planet_idx + offset) % 8
        sign_idx = JAMA_SIGNS_ANTICLOCKWISE[offset]
        p_meta = JAMA_GRAHAS[planet_idx]
        s_meta = ZODIAC_SIGNS[sign_idx]

        jama_graha_placements.append({
            "id": p_meta["id"],
            "name_en": p_meta["name_en"],
            "name_ta": p_meta["name_ta"],
            "symbol": p_meta["symbol"],
            "classical_name_ta": p_meta["classical_name_ta"],
            "is_benefic": p_meta["is_benefic"],
            "sign_index": sign_idx,
            "sign_name_en": s_meta["name_en"],
            "sign_name_ta": s_meta["name_ta"],
            "degree_in_sign": outer_deg_in_sign,
            "dms": format_dms(outer_deg_in_sign),
            "signification_en": p_meta["signification_en"],
            "signification_ta": p_meta["signification_ta"],
            "color": p_meta["color"],
        })

    # 11. Build 12 House Placements from Udhayam
    house_placements: List[Dict[str, Any]] = []
    for s_idx in range(1, 13):
        sign_meta = ZODIAC_SIGNS[s_idx]
        house_from_udhayam = ((s_idx - udhayam_sign_idx) % 12) + 1
        house_from_aarudham = ((s_idx - aarudham_sign_idx) % 12) + 1

        is_udhayam_sign = (s_idx == udhayam_sign_idx)
        is_aarudham_sign = (s_idx == aarudham_sign_idx)
        is_kavippu_sign = (s_idx == kavippu_sign_idx)

        j_in_sign = [g for g in jama_graha_placements if g["sign_index"] == s_idx]
        t_in_sign = [p for p in transit_planets if p["sign_index"] == s_idx]

        house_placements.append({
            "sign_index": s_idx,
            "sign_name_en": sign_meta["name_en"],
            "sign_name_ta": sign_meta["name_ta"],
            "nature": sign_meta["nature"],
            "nature_ta": sign_meta["nature_ta"],
            "lord_en": sign_meta["lord_en"],
            "lord_ta": sign_meta["lord_ta"],
            "direction_en": sign_meta["direction_en"],
            "direction_ta": sign_meta["direction_ta"],
            "house_from_udhayam": house_from_udhayam,
            "house_from_aarudham": house_from_aarudham,
            "is_udhayam": is_udhayam_sign,
            "is_aarudham": is_aarudham_sign,
            "is_kavippu": is_kavippu_sign,
            "jama_grahas": j_in_sign,
            "transit_planets": t_in_sign,
        })

    # 12. Classical Jamakkol Shastra Rules Execution Engine
    classical_rules = evaluate_classical_jamakkol_rules(
        udhayam_data=udhayam_data,
        aarudham_data=aarudham_data,
        kavippu_data=kavippu_data,
        sun_sign_idx=sun_sign_idx,
        transit_planets=transit_planets,
        jama_graha_placements=jama_graha_placements,
    )

    # 13. Synthesize Predictions using the Classical Rules Results
    prediction = synthesize_jamakkol_prediction(
        udhayam_data=udhayam_data,
        aarudham_data=aarudham_data,
        kavippu_data=kavippu_data,
        active_jamam_ruler=active_jamam_ruler,
        jama_graha_placements=jama_graha_placements,
        transit_planets=transit_planets,
        query_category=query_category or "general",
        classical_rules=classical_rules,
    )

    # 14. Solar & Duration strings
    day_duration_sec = (ss_curr_local - sr_curr_local).total_seconds()
    night_duration_sec = (sr_next_local - ss_curr_local).total_seconds()

    day_hours = int(day_duration_sec // 3600)
    day_mins = int((day_duration_sec % 3600) // 60)
    night_hours = int(night_duration_sec // 3600)
    night_mins = int((night_duration_sec % 3600) // 60)

    dinamana_ghatikas = round(day_duration_sec / 1440.0, 2)

    return {
        "query_datetime": query_dt_local.isoformat(),
        "query_text": query_text,
        "query_category": query_category,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": tz_str,
        },
        "solar_info": {
            "sunrise_local": sr_curr_local.strftime("%I:%M %p"),
            "sunset_local": ss_curr_local.strftime("%I:%M %p"),
            "is_day": is_day,
            "day_duration": f"{day_hours}h {day_mins}m",
            "night_duration": f"{night_hours}h {night_mins}m",
            "dinamana_ghatikas": dinamana_ghatikas,
            "surya_veethi": surya_veethi_info["name_ta"],
            "surya_veethi_en": surya_veethi_info["name_en"],
        },
        "jamam_info": {
            "period_type": period_type,
            "jamam_number": jamam_number,
            "jamam_start_local": jamam_start_local.strftime("%I:%M %p"),
            "jamam_end_local": jamam_end_local.strftime("%I:%M %p"),
            "jamam_ruler_en": active_jamam_ruler["name_en"],
            "jamam_ruler_ta": active_jamam_ruler["name_ta"],
            "jamam_ruler_symbol": active_jamam_ruler["symbol"],
            "is_benefic_ruler": active_jamam_ruler["is_benefic"],
            "weekday_lord_en": day_lord_meta["name_en"],
            "weekday_lord_ta": day_lord_meta["name_ta"],
            "progress_percent": round(elapsed_in_jamam_fraction * 100, 1),
        },
        "three_pillars": {
            "udhayam": udhayam_data,
            "aarudham": aarudham_data,
            "kavippu": kavippu_data,
        },
        "jama_grahas": jama_graha_placements,
        "transit_planets": transit_planets,
        "house_placements": house_placements,
        "prediction_verdict": prediction,
        "classical_rules": classical_rules,
    }


def evaluate_classical_jamakkol_rules(
    udhayam_data: Dict[str, Any],
    aarudham_data: Dict[str, Any],
    kavippu_data: Dict[str, Any],
    sun_sign_idx: int,
    transit_planets: List[Dict[str, Any]],
    jama_graha_placements: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Execute all classical Jamakkol rules provided in the treatise."""
    u_sign = udhayam_data["sign_index"]
    a_sign = aarudham_data["sign_index"]
    k_sign = kavippu_data["sign_index"]
    u_lon = udhayam_data["longitude"]

    # 1. Snapshot Watch Time Predictions (Udayam & Arudam Relation)
    # 1. Same House = Success
    # 2. 5/9 = Success
    # 3. 3/11 = Success
    # 4. 2/12 = Failure
    # 5. 6/8 = Failure
    # 6. 1/7 = Delay and Failure
    # 7. 4/10 = Failure
    rel_house = ((a_sign - u_sign) % 12) + 1
    if rel_house == 1:
        watch_type = "1/1 (Same House)"
        watch_res = "Success"
        watch_en = "Udayam and Arudam fall in the exact same house. Clear and immediate success!"
        watch_ta = "உதயமும் ஆருடமும் ஒரே ராசியில் இணைந்துள்ளன. காரிய சித்தி நிச்சயம் உண்டாகும்!"
    elif rel_house in [5, 9]:
        watch_type = "5/9 (Trikona)"
        watch_res = "Success"
        watch_en = f"Aarudham is in the {rel_house}th house (5/9 Trikona) from Udayam. Divine grace brings auspicious success!"
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவகத்தில் (5/9 திரிகோணத்தில்) உள்ளது. சுப காரிய சித்தி நிச்சயமாகும்!"
    elif rel_house in [3, 11]:
        watch_type = "3/11 (Upachaya / Labha)"
        watch_res = "Success"
        watch_en = f"Aarudham is in the {rel_house}th house (3/11) from Udayam. Firm endeavor brings profitable success!"
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவகத்தில் (3/11 ஸ்தானத்தில்) உள்ளது. விடாமுயற்சியால் வெற்றி மற்றும் லாபம் கிட்டும்!"
    elif rel_house in [2, 12]:
        watch_type = "2/12 (Dvi-Dvadasha)"
        watch_res = "Failure"
        watch_en = f"Aarudham is in the {rel_house}th house (2/12) from Udayam. Indicates expenditure, loss, or failure."
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவகத்தில் (2/12 விரய ஸ்தானத்தில்) உள்ளது. தேவையற்ற விரயம் அல்லது தோல்வி."
    elif rel_house in [6, 8]:
        watch_type = "6/8 (Shadashtaka)"
        watch_res = "Failure"
        watch_en = f"Aarudham is in the {rel_house}th house (6/8 Shadashtaka) from Udayam. Severe friction, debt, or failure."
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவகத்தில் (6/8 சஷ்டாஷ்டகத்தில்) உள்ளது. பகை, விவாதம், கடன் அல்லது தோல்வி."
    elif rel_house == 7:
        watch_type = "1/7 (Samasaptaka)"
        watch_res = "Delay and Failure"
        watch_en = "Aarudham is in the 7th house (1/7) from Udayam. Opposition causes prolonged delay and failure."
        watch_ta = "உதயத்திற்கு ஆருடம் 7-ம் பாவகத்தில் (1/7 சமசப்தமத்தில்) உள்ளது. கடுமையான தாமதம் மற்றும் இறுதியில் தோல்வி."
    elif rel_house in [4, 10]:
        watch_type = "4/10 (Kendra Clash)"
        watch_res = "Failure"
        watch_en = f"Aarudham is in the {rel_house}th house (4/10 Kendra) from Udayam. Conflicting actions lead to failure."
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவகத்தில் (4/10 கேந்திரத்தில்) உள்ளது. முரண்பாடான நிலைமைகளால் காரியத் தோல்வி."
    else:
        watch_type = f"House {rel_house}"
        watch_res = "Failure"
        watch_en = f"Aarudham is in house {rel_house} from Udayam."
        watch_ta = f"உதயத்திற்கு ஆருடம் {rel_house}-ம் பாவத்தில் உள்ளது."

    watch_time_relation = {
        "relation_type": watch_type,
        "house_from_udayam": rel_house,
        "result": watch_res,
        "description_en": watch_en,
        "description_ta": watch_ta,
    }

    # Planets currently in Udayam & Arudam
    planets_in_u = [p for p in transit_planets if p["sign_index"] == u_sign]
    planets_in_a = [p for p in transit_planets if p["sign_index"] == a_sign]
    has_planets_in_u = (len(planets_in_u) > 0)
    has_planets_in_u_or_a = (len(planets_in_u) > 0 or len(planets_in_a) > 0)

    # 2. Facing Direction (Ardhomukha, Urdhomukha, Triyangmukha)
    # Only used when no planet in Udayam!
    # a) Ardhomukha = Downward facing = Kendra to Sun = from Sun 1,4,7,10 -> Failure
    # b) Urdhomukha = Upward looking = Sun's 12th house, from there count 1,4,7,10 (12,3,6,9) -> Success
    # c) Triyangmukha = Both Up and Down = Sun's 2nd house, from there count 1,4,7,10 (2,5,8,11) -> Success after Failure
    h_from_sun = ((u_sign - sun_sign_idx) % 12) + 1
    if h_from_sun in [1, 4, 7, 10]:
        facing_type = "Ardhomukha"
        facing_name_ta = "அர்த்தோமுகம் (கீழ்நோக்கு - சூரியனுக்கு 1,4,7,10)"
        facing_verdict = "Failure"
        facing_en = "Udayam is Ardhomukha (Downward facing, Kendra to Sun 1,4,7,10). Predicts failure."
        facing_ta = "உதயம் சூரியனுக்கு கேந்திரத்தில் (1,4,7,10) அர்த்தோமுகமாக இருப்பதால் காரியத் தோல்வியைக் குறிக்கும்."
    elif h_from_sun in [12, 3, 6, 9]:
        facing_type = "Urdhomukha"
        facing_name_ta = "ஊர்த்துவமுகம் (மேல்நோக்கு - சூரியனுக்கு 12,3,6,9)"
        facing_verdict = "Success"
        facing_en = "Udayam is Urdhomukha (Upward looking, 12th from Sun & its Kendras 12,3,6,9). Predicts success!"
        facing_ta = "உதயம் சூரியனுக்கு 12-ம் பாவம் சார்ந்த (12,3,6,9) ஊர்த்துவமுகமாக உள்ளதால் காரிய வெற்றியைத் தரும்!"
    else:  # [2, 5, 8, 11]
        facing_type = "Triyangmukha"
        facing_name_ta = "திரியங்முகம் (இருபுற நோக்கு - சூரியனுக்கு 2,5,8,11)"
        facing_verdict = "Success after Failure"
        facing_en = "Udayam is Triyangmukha (Both Up and Down, 2nd from Sun & its Kendras 2,5,8,11). Predicts success after initial struggle."
        facing_ta = "உதயம் சூரியனுக்கு 2-ம் பாவம் சார்ந்த (2,5,8,11) திரியங்முகமாக உள்ளதால் ஆரம்பத் தோல்விக்குப் பின் வெற்றி கிட்டும்."

    facing_direction = {
        "facing_type": facing_type,
        "facing_name_ta": facing_name_ta,
        "house_from_sun": h_from_sun,
        "applicable": not has_planets_in_u,
        "result": facing_verdict if not has_planets_in_u else "Overridden (Planets in Udayam)",
        "description_en": facing_en if not has_planets_in_u else f"{facing_en} (Note: Overridden by planets present in Udayam).",
        "description_ta": facing_ta if not has_planets_in_u else f"{facing_ta} (குறிப்பு: உதயத்தில் கிரகம் இருப்பதால் இது இரண்டாம்பட்சமாகும்).",
    }

    # 3. Rising Nature (Sirosodayam / Pristodaya / Siropristodaya)
    # Only used when no planet in Udayam and Arudam!
    # 1. Sirosodayam = Success (Gemini, Leo, Virgo, Libra, Scorpio, Aquarius)
    # 2. Pristodaya = Failure (Aries, Taurus, Cancer, Sagittarius, Capricorn)
    # 3. Siropristodaya = Success after delay (Pisces)
    rising_type = udhayam_data["rising_nature"]
    if rising_type == "Sirosodayam":
        rising_verdict = "Success"
        rising_en = "Udayam is Sirosodayam (Head-rising sign). Signifies auspicious success!"
        rising_ta = "உதயம் சிரோதய ராசியாகும் (தலைப்பகுதி முதலில் உதிக்கும்). காரிய வெற்றி நிச்சயம்!"
    elif rising_type == "Pristodaya":
        rising_verdict = "Failure"
        rising_en = "Udayam is Pristodaya (Hind-rising sign). Signifies obstacles or failure."
        rising_ta = "உதயம் பிருஷ்டோதய ராசியாகும் (பின்பகுதி முதலில் உதிக்கும்). காரியத் தடை அல்லது தோல்வி."
    else:  # Siropristodaya (Pisces)
        rising_verdict = "Success after delay"
        rising_en = "Udayam is Siropristodaya (Pisces). Signifies victory after temporary delay."
        rising_ta = "உதயம் சிரோபிருஷ்டோதய ராசியாகும் (மீனம்). சிறு காலதாமதத்திற்குப் பின் வெற்றி கிட்டும்."

    rising_nature = {
        "nature_type": rising_type,
        "nature_name_ta": udhayam_data["rising_nature_ta"],
        "applicable": not has_planets_in_u_or_a,
        "result": rising_verdict if not has_planets_in_u_or_a else "Overridden (Planets present)",
        "description_en": rising_en if not has_planets_in_u_or_a else f"{rising_en} (Overridden by planets in Udayam/Arudam).",
        "description_ta": rising_ta if not has_planets_in_u_or_a else f"{rising_ta} (உதயம்/ஆருடத்தில் கிரகம் உள்ளதால் இது இரண்டாம்பட்சமாகும்).",
    }

    # 4. Subh Udayam & Subh Arudam Balance
    # Only when no planet in Udayam and Arudam!
    # Subh Udayam = Leo to Capricorn (5,6,7,8,9,10)
    # Subh Arudam = Aquarius to Cancer (11,12,1,2,3,4)
    # Both Subh = Favourable
    # Both Asubh = Unfavourable
    is_subh_u = (u_sign in SUBH_UDAYAM_SIGNS)
    is_subh_a = (a_sign in SUBH_ARUDAM_SIGNS)
    if is_subh_u and is_subh_a:
        subh_result = "Both Subh (Favourable)"
        subh_en = "Both Udayam (Leo-Cap) and Arudam (Aqua-Cancer) are in Subh alignment. Results are highly favourable!"
        subh_ta = "உதயம் (சுப உதயம்) மற்றும் ஆருடம் (சுப ஆருடம்) இரண்டும் சுப அமைப்பில் உள்ளன. மிகச் சிறந்த நற்பலன் உண்டாகும்!"
    elif not is_subh_u and not is_subh_a:
        subh_result = "Both Asubh (Unfavourable)"
        subh_en = "Both Udayam and Arudam fall into Asubh alignments. Results are unfavourable."
        subh_ta = "உதயம் மற்றும் ஆருடம் இரண்டும் அசுப அமைப்பில் உள்ளன. காரியத்தில் தோல்வி அல்லது விரயம் நேரலாம்."
    else:
        subh_result = "Mixed Balance"
        subh_en = "One pillar is Subh and the other is Asubh. Results will be moderate and mixed."
        subh_ta = "ஒன்று சுப அமைப்பிலும் மற்றொன்று அசுப அமைப்பிலும் உள்ளது. மத்திமமான கலப்பு பலன்கள் உண்டாகும்."

    subh_balance = {
        "is_subh_udayam": is_subh_u,
        "is_subh_arudam": is_subh_a,
        "applicable": not has_planets_in_u_or_a,
        "result": subh_result,
        "description_en": subh_en,
        "description_ta": subh_ta,
    }

    # 5. Predictions of Success & Failure: Lord Connections
    # Udayam Lord, 10th Lord, 11th Lord
    u_lord = SIGN_LORDS[u_sign]
    tenth_sign = ((u_sign + 9 - 1) % 12) + 1
    tenth_lord = SIGN_LORDS[tenth_sign]
    eleventh_sign = ((u_sign + 10 - 1) % 12) + 1
    eleventh_lord = SIGN_LORDS[eleventh_sign]

    # Find where the lords are located
    u_lord_planet = next((p for p in transit_planets if p["name_en"] == u_lord), None)
    tenth_lord_planet = next((p for p in transit_planets if p["name_en"] == tenth_lord), None)
    eleventh_lord_planet = next((p for p in transit_planets if p["name_en"] == eleventh_lord), None)

    u_lord_sign = u_lord_planet["sign_index"] if u_lord_planet else u_sign
    tenth_lord_sign = tenth_lord_planet["sign_index"] if tenth_lord_planet else tenth_sign
    eleventh_lord_sign = eleventh_lord_planet["sign_index"] if eleventh_lord_planet else eleventh_sign

    # 1. Udayam and 10th Lord getting connected -> Indicates Success
    # 2. Udayam and 11th Lord connection -> Indicates Success
    # 3. Exchange between Udayam and 10th Lord -> Success
    # 4. Exchange between Udayam and 11th Lord -> Success
    parivartana_10th = (u_lord_sign == tenth_sign and tenth_lord_sign == u_sign)
    parivartana_11th = (u_lord_sign == eleventh_sign and eleventh_lord_sign == u_sign)

    tenth_connected = False
    tenth_conn_type = None
    if parivartana_10th:
        tenth_connected = True
        tenth_conn_type = "Parivartana (Exchange of Signs)"
    elif u_lord_sign == tenth_lord_sign:
        tenth_connected = True
        tenth_conn_type = "Conjunction (Yuti)"
    elif tenth_lord_sign == u_sign:
        tenth_connected = True
        tenth_conn_type = "10th Lord in Udayam"
    elif u_lord_sign == tenth_sign:
        tenth_connected = True
        tenth_conn_type = "Udayam Lord in 10th House"
    elif ((tenth_lord_sign - u_lord_sign) % 12) + 1 == 7:
        tenth_connected = True
        tenth_conn_type = "Mutual 7th Aspect"

    eleventh_connected = False
    eleventh_conn_type = None
    if parivartana_11th:
        eleventh_connected = True
        eleventh_conn_type = "Parivartana (Exchange of Signs)"
    elif u_lord_sign == eleventh_lord_sign:
        eleventh_connected = True
        eleventh_conn_type = "Conjunction (Yuti)"
    elif eleventh_lord_sign == u_sign:
        eleventh_connected = True
        eleventh_conn_type = "11th Lord in Udayam"
    elif u_lord_sign == eleventh_sign:
        eleventh_connected = True
        eleventh_conn_type = "Udayam Lord in 11th House"
    elif ((eleventh_lord_sign - u_lord_sign) % 12) + 1 == 7:
        eleventh_connected = True
        eleventh_conn_type = "Mutual 7th Aspect"

    # Udayam Lord in Debilitation check
    u_lord_debilitated = False
    if u_lord in PLANET_DIGNITIES:
        u_lord_debilitated = (u_lord_sign == PLANET_DIGNITIES[u_lord]["debilitated"])

    # 10th Lord Bhava from Udayam (Verification of Query)
    tenth_lord_bhava = ((tenth_lord_sign - u_sign) % 12) + 1
    bhava_significations = {
        1: ("Self, vitality, personal ambitions, reputation", "சுய கௌரவம், உடல் நலம், தலைமை"),
        2: ("Wealth, finance, family assets, speech", "பணம், குடும்பம், வாக்கு வன்மை"),
        3: ("Brothers, courage, short journeys, agreements", "சகோதரம், தைரியம், குறுகிய பயணம், ஒப்பந்தம்"),
        4: ("Mother, vehicles, land, property, residence", "தாய், வீடு, நிலம், வாகனம், சுகம்"),
        5: ("Children, speculation, love, intellect, creative pursuits", "பிள்ளைகள், பூர்வீகம், காதல், பங்குச்சந்தை"),
        6: ("Debts, litigation, enemies, diseases, legal battles", "கடன், நோய், எதிரிகள், வழக்கு"),
        7: ("Spouse, marriage, business partner, foreign client", "மனைவி/கணவர், திருமணம், கூட்டாளி, வெளிநாட்டு விவகாரம்"),
        8: ("Longevity, sudden crisis, secrets, inheritance, insurance", "ஆயுள், மறைமுக விவகாரம், திடீர் சிக்கல், உயில்"),
        9: ("Father, higher education, long journey, temple, luck", "தந்தை, உயர்கல்வி, வெளிநாட்டுப் பயணம், ஆலயம், பாக்கியம்"),
        10: ("Career, government business, status, profession", "உத்தியோகம், தொழில், அரசு காரியம், பதவி"),
        11: ("Profit, fulfillment of desire, elder sibling, gains", "லாபம், நினைத்த காரிய சித்தி, மூத்த சகோதரன்"),
        12: ("Foreign relocation, hospital, heavy expenses, secrets", "வெளிநாடு, மருத்துவமனை, விரயம், ஆன்மீகம்"),
    }
    t_bhava_en, t_bhava_ta = bhava_significations.get(tenth_lord_bhava, ("General", "பொது"))

    lord_connections = {
        "udayam_lord": u_lord,
        "tenth_lord": tenth_lord,
        "eleventh_lord": eleventh_lord,
        "tenth_lord_connected": tenth_connected,
        "tenth_lord_connection_type": tenth_conn_type,
        "eleventh_lord_connected": eleventh_connected,
        "eleventh_lord_connection_type": eleventh_conn_type,
        "parivartana_udayam_10th": parivartana_10th,
        "parivartana_udayam_11th": parivartana_11th,
        "udayam_lord_debilitated": u_lord_debilitated,
        "tenth_lord_bhava": tenth_lord_bhava,
        "tenth_lord_query_signification_en": f"10th Lord {tenth_lord} resides in {tenth_lord_bhava}th house from Udayam: Question relates to {t_bhava_en}.",
        "tenth_lord_query_signification_ta": f"10-ம் அதிபதி {tenth_lord} உதயத்திற்கு {tenth_lord_bhava}-ம் பாவகத்தில் அமர்ந்துள்ளார்: வினா '{t_bhava_ta}' சார்ந்தது என சரிபார்க்கப்படுகிறது.",
    }

    # 6. Kavippu in 2nd / 11th & Afflicted Planets
    k_bhava = ((k_sign - u_sign) % 12) + 1
    kavippu_in_2nd = (k_bhava == 2)
    kavippu_in_11th = (k_bhava == 11)

    # Planets conjunct with Kavippu (lose their significations)
    planets_with_kavippu = [
        p for p in transit_planets if p["sign_index"] == k_sign
    ]
    jama_with_kavippu = [
        g for g in jama_graha_placements if g["sign_index"] == k_sign
    ]

    k_bhava_en, k_bhava_ta = bhava_significations.get(k_bhava, ("Matter", "காரியம்"))
    if kavippu_in_2nd:
        k_meaning_en = "Kavippu in 2nd to Udayam: Direct indication of financial hindrance, loss, or speech obstruction!"
        k_meaning_ta = "கவிப்பு உதயத்திற்கு 2-ம் பாவத்தில் விழுந்துள்ளது: தன நஷ்டம், வாக்கு தோஷம் அல்லது குடும்பத் தடையைக் காட்டும்!"
    elif kavippu_in_11th:
        k_meaning_en = "Kavippu in 11th to Udayam: Direct denial or obstruction in realizing gains and fulfillment of desires!"
        k_meaning_ta = "கவிப்பு உதயத்திற்கு 11-ம் பாவத்தில் விழுந்துள்ளது: லாபத் தடை மற்றும் நினைத்த காரியம் நிறைவேறுவதில் முடக்கம்!"
    else:
        k_meaning_en = f"Kavippu in {k_bhava}th house from Udayam: Conceals, obstructs, or afflicts {k_bhava_en}."
        k_meaning_ta = f"கவிப்பு உதயத்திற்கு {k_bhava}-ம் பாவத்தில் விழுந்துள்ளது: '{k_bhava_ta}' விவகாரத்தில் மறைமுகத் தடைகளை உருவாக்கும்."

    kavippu_afflictions = {
        "kavippu_bhava_from_udayam": k_bhava,
        "kavippu_in_2nd": kavippu_in_2nd,
        "kavippu_in_11th": kavippu_in_11th,
        "afflicted_transit_planets": [p["name_en"] for p in planets_with_kavippu],
        "afflicted_jama_grahas": [g["name_en"] for g in jama_with_kavippu],
        "afflicted_bhava_meaning_en": k_meaning_en,
        "afflicted_bhava_meaning_ta": k_meaning_ta,
    }

    # 7. Approaching vs Crossed Planets (Past, Present & Future)
    # 1. Approaching Udayam: Planet trailing behind Udayam (12th house or lower degree in 1st house) -> Present & Future
    # 2. Crossed Udayam: Planet ahead of Udayam (2nd house or ahead in 1st house) -> Past
    approaching: List[Dict[str, Any]] = []
    crossed: List[Dict[str, Any]] = []
    in_udayam: List[Dict[str, Any]] = []

    for p in transit_planets:
        p_sign = p["sign_index"]
        p_lon = p["longitude"]
        h_from_u = ((p_sign - u_sign) % 12) + 1

        karakatwa = PLANET_QUERY_KARAKATWAS.get(p["name_en"], {"en": "General", "ta": "பொது"})

        if h_from_u == 1:
            in_udayam.append({
                "name_en": p["name_en"],
                "name_ta": p["name_ta"],
                "degree": p["dms"],
                "is_debilitated": p.get("is_debilitated", False),
                "karakatwa_en": karakatwa["en"],
                "karakatwa_ta": karakatwa["ta"],
            })
            if p_lon < u_lon:
                approaching.append({
                    "name_en": p["name_en"],
                    "name_ta": p["name_ta"],
                    "location": "In Udayam (Approaching Lagna degree)",
                    "timeline": "Present & Future",
                    "karakatwa_en": karakatwa["en"],
                    "karakatwa_ta": karakatwa["ta"],
                })
            else:
                crossed.append({
                    "name_en": p["name_en"],
                    "name_ta": p["name_ta"],
                    "location": "In Udayam (Crossed Lagna degree)",
                    "timeline": "Past events",
                    "karakatwa_en": karakatwa["en"],
                    "karakatwa_ta": karakatwa["ta"],
                })
        elif h_from_u == 12:
            approaching.append({
                "name_en": p["name_en"],
                "name_ta": p["name_ta"],
                "location": "12th House (Approaching Udayam)",
                "timeline": "Present & Future",
                "karakatwa_en": karakatwa["en"],
                "karakatwa_ta": karakatwa["ta"],
            })
        elif h_from_u == 2:
            crossed.append({
                "name_en": p["name_en"],
                "name_ta": p["name_ta"],
                "location": "2nd House (Crossed Udayam)",
                "timeline": "Past events",
                "karakatwa_en": karakatwa["en"],
                "karakatwa_ta": karakatwa["ta"],
            })

    # 8. Exalted & Debilitated Audit (Debilitated in Udayam rule)
    exalted_list = [p["name_en"] for p in transit_planets if p.get("is_exalted", False)]
    debilitated_list = [p["name_en"] for p in transit_planets if p.get("is_debilitated", False)]
    debilitated_in_udayam = any(p.get("is_debilitated", False) for p in planets_in_u)

    exalted_debilitated_audit = {
        "exalted_planets": exalted_list,
        "debilitated_planets": debilitated_list,
        "debilitated_in_udayam": debilitated_in_udayam,
        "chatterbox_warning": debilitated_in_udayam,
        "warning_text_en": (
            "Debilitated planet in Udayam: Querent will ask a question which he is incapable of performing, "
            "and will keep talking like a chatterbox."
            if debilitated_in_udayam
            else "No debilitated planet in Udayam."
        ),
        "warning_text_ta": (
            "உதயத்தில் நீச கிரகம் உள்ளது: கேள்வியாளர் தனது சக்திக்கு மீறிய, செய்ய இயலாத காரியத்தைப் பற்றிப் பேசுவார், "
            "வீண் பேச்சாளராக (Chatterbox) இருப்பார்."
            if debilitated_in_udayam
            else "உதயத்தில் நீச கிரகம் இல்லை."
        ),
    }

    # 9. Classical Relationship Prasanam Analysis
    relationships_eval: Dict[str, Any] = {}
    for rel_key, rel_meta in RELATIONSHIP_KARAKAS.items():
        karak_planet_name = rel_meta["planet"]
        t_planet = next((p for p in transit_planets if p["name_en"] == karak_planet_name or (karak_planet_name == "Snake" and p["name_en"] in ["Rahu", "Ketu"])), None)
        j_planet = next((g for g in jama_graha_placements if g["name_en"] == karak_planet_name), None)

        is_exalted = t_planet.get("is_exalted", False) if t_planet else False
        is_debilitated = t_planet.get("is_debilitated", False) if t_planet else False
        planet_sign = t_planet["sign_index"] if t_planet else (j_planet["sign_index"] if j_planet else 1)
        planet_has_kavippu = (planet_sign == k_sign) or (j_planet is not None and j_planet["sign_index"] == k_sign)

        karak_bhava_num = rel_meta["house"]
        karak_bhava_sign = ((u_sign + karak_bhava_num - 2) % 12) + 1
        bhava_has_kavippu = (karak_bhava_sign == k_sign)

        if is_exalted and not planet_has_kavippu and not bhava_has_kavippu:
            verdict = "Highly Favorable (100% Yes)"
            verdict_ta = "மிகவும் சாதகமானது (100% உதவி கிட்டும்)"
            desc_en = f"{rel_meta['en']} karaka ({karak_planet_name}) is exalted and completely free from Kavippu. Full support and harmony assured!"
            desc_ta = f"{rel_meta['ta']} காரகர் ({karak_planet_name}) உச்சம் பெற்று கவிப்பு தாக்கமின்றி உள்ளார். பூரண ஆதரவும் நன்மையும் கிட்டும்!"
        elif is_exalted and planet_has_kavippu:
            verdict = "Capable but Unwilling"
            verdict_ta = "வசதியிருந்தும் உதவ மாட்டார்"
            desc_en = f"{rel_meta['en']} karaka ({karak_planet_name}) is exalted but afflicted by Kavippu: Has wealth and resources but will NOT take care or assist."
            desc_ta = f"{rel_meta['ta']} காரகர் ({karak_planet_name}) உச்சம் பெற்று கவிப்புடன் உள்ளார்: வசதி வாய்ப்புகள் இருந்தாலும் உதவ மாட்டார்."
        elif is_debilitated or planet_has_kavippu or bhava_has_kavippu:
            verdict = "Unfavorable / Obstruction"
            verdict_ta = "சாதகமற்றது / ஆதரவு இல்லை"
            desc_en = f"{rel_meta['en']} karaka or signifying house ({karak_bhava_num}th) is afflicted by debilitation or Kavippu. Relationship lacks support."
            desc_ta = f"{rel_meta['ta']} காரகர் அல்லது {karak_bhava_num}-ம் பாவம் நீசம்/கவிப்பால் பாதிக்கப்பட்டுள்ளது. ஆதரவோ உதவியோ கிட்டாது."
        else:
            verdict = "Neutral / Moderate"
            verdict_ta = "சாதாரண நிலை"
            desc_en = f"{rel_meta['en']} karaka is in normal disposition."
            desc_ta = f"{rel_meta['ta']} காரகர் இயல்பான நிலையில் உள்ளார்."

        relationships_eval[rel_key] = {
            "title_en": rel_meta["en"],
            "title_ta": rel_meta["ta"],
            "planet": karak_planet_name,
            "karak_bhava": karak_bhava_num,
            "verdict": verdict,
            "verdict_ta": verdict_ta,
            "description_en": desc_en,
            "description_ta": desc_ta,
        }

    # 10. Politics & Government Post Analysis
    fifth_sign = ((u_sign + 5 - 2) % 12) + 1
    kavippu_in_5th = (k_sign == fifth_sign)

    sun_planet = next((p for p in transit_planets if p["name_en"] == "Sun"), None)
    sun_exalted = sun_planet.get("is_exalted", False) if sun_planet else False
    sun_debilitated = sun_planet.get("is_debilitated", False) if sun_planet else False
    sun_has_kavippu = (sun_planet["sign_index"] == k_sign) if sun_planet else False

    jupiter_planet = next((p for p in transit_planets if p["name_en"] == "Jupiter"), None)
    jupiter_exalted = jupiter_planet.get("is_exalted", False) if jupiter_planet else False
    jupiter_debilitated = jupiter_planet.get("is_debilitated", False) if jupiter_planet else False
    jupiter_has_kavippu = (jupiter_planet["sign_index"] == k_sign) if jupiter_planet else False

    saturn_planet = next((p for p in transit_planets if p["name_en"] == "Saturn"), None)
    saturn_exalted = saturn_planet.get("is_exalted", False) if saturn_planet else False
    saturn_has_kavippu = (saturn_planet["sign_index"] == k_sign) if saturn_planet else False

    central_govt_ticket = not jupiter_debilitated and not jupiter_has_kavippu
    u_lord_is_exalted = (u_lord_sign == PLANET_DIGNITIES.get(u_lord, {}).get("exalted", -1))
    powerful_post_favorable = (u_lord_is_exalted or sun_exalted) and not kavippu_in_5th
    panchayat_favorable = saturn_exalted and not saturn_has_kavippu

    posts_breakdown: Dict[str, Any] = {}
    for post_key, post_meta in GOVT_POLITICS_KARAKAS.items():
        karak_planets = post_meta["planets"]
        afflicted = False
        reasons_en = []
        reasons_ta = []
        for kp in karak_planets:
            tp = next((p for p in transit_planets if p["name_en"] == kp or (kp == "Snake" and p["name_en"] in ["Rahu", "Ketu"])), None)
            if tp:
                if tp.get("is_debilitated", False):
                    afflicted = True
                    reasons_en.append(f"{kp} is debilitated")
                    reasons_ta.append(f"{kp} நீசமடைந்துள்ளது")
                if tp["sign_index"] == k_sign:
                    afflicted = True
                    reasons_en.append(f"{kp} is with Kavippu")
                    reasons_ta.append(f"{kp} கவிப்புடன் உள்ளது")
        if kavippu_in_5th:
            afflicted = True
            reasons_en.append("Kavippu in 5th house (Politics karaka bhava)")
            reasons_ta.append("அரசியல் காரக 5-ம் பாவத்தில் கவிப்பு")

        status = "Unfavorable" if afflicted else "Favorable"
        status_ta = "வாய்ப்பு குறைவு / தடை" if afflicted else "சாதகமான சூழல் / வெற்றி வாய்ப்பு"
        posts_breakdown[post_key] = {
            "post_en": post_meta["en"],
            "post_ta": post_meta["ta"],
            "status": status,
            "status_ta": status_ta,
            "reasons_en": ", ".join(reasons_en) if reasons_en else "Planets dignified and unblemished",
            "reasons_ta": ", ".join(reasons_ta) if reasons_ta else "காரக கிரகங்கள் பலமுடன் உள்ளன",
        }

    politics_analysis = {
        "kavippu_in_5th_house": kavippu_in_5th,
        "powerful_post_eligible": powerful_post_favorable,
        "central_govt_ticket_eligible": central_govt_ticket,
        "panchayat_election_favorable": panchayat_favorable,
        "sun_afflicted": sun_debilitated or sun_has_kavippu,
        "posts_breakdown": posts_breakdown,
        "summary_en": (
            "Powerful position in politics is promised." if powerful_post_favorable else
            "Political aspirations face obstruction due to 5th house Kavippu or planet afflictions."
        ),
        "summary_ta": (
            "அரசியலில் உயர் பதவி அல்லது வெற்றி வாய்ப்பு பிரகாசமாக உள்ளது." if powerful_post_favorable else
            "5-ம் பாவத்தில் கவிப்பு அல்லது கிரக பலவீனத்தால் அரசியல் காரியங்களில் தடைகள் ஏற்படலாம்."
        ),
    }

    # 11. Foreign Travel & Citizenship Analysis
    ninth_sign = ((u_sign + 9 - 2) % 12) + 1
    eleventh_sign = ((u_sign + 11 - 2) % 12) + 1
    twelfth_sign = ((u_sign + 12 - 2) % 12) + 1

    ninth_lord = SIGN_LORDS[ninth_sign]
    twelfth_lord = SIGN_LORDS[twelfth_sign]

    ninth_lord_p = next((p for p in transit_planets if p["name_en"] == ninth_lord), None)
    eleventh_lord_p = next((p for p in transit_planets if p["name_en"] == eleventh_lord), None)
    twelfth_lord_p = next((p for p in transit_planets if p["name_en"] == twelfth_lord), None)

    snake_approaching = any(p["name_en"] in ["Snake", "Rahu"] for p in approaching)

    afflicted_travel_lords = []
    if ninth_lord_p and (ninth_lord_p.get("is_debilitated", False) or ninth_lord_p["sign_index"] == k_sign):
        afflicted_travel_lords.append(f"9th Lord {ninth_lord}")
    if eleventh_lord_p and (eleventh_lord_p.get("is_debilitated", False) or eleventh_lord_p["sign_index"] == k_sign):
        afflicted_travel_lords.append(f"11th Lord {eleventh_lord}")
    if twelfth_lord_p and (twelfth_lord_p.get("is_debilitated", False) or twelfth_lord_p["sign_index"] == k_sign):
        afflicted_travel_lords.append(f"12th Lord {twelfth_lord}")

    kavippu_in_travel_houses = []
    if k_sign == ninth_sign:
        kavippu_in_travel_houses.append("9th House")
    if k_sign == eleventh_sign:
        kavippu_in_travel_houses.append("11th House")
    if k_sign == twelfth_sign:
        kavippu_in_travel_houses.append("12th House")

    can_travel = (snake_approaching or u_lord_is_exalted) and not (len(afflicted_travel_lords) > 0 or len(kavippu_in_travel_houses) > 0)

    citizenship_favorable = not (
        (ninth_lord_p and (ninth_lord_p.get("is_debilitated", False) or ninth_lord_p["sign_index"] == k_sign)) or
        (twelfth_lord_p and (twelfth_lord_p.get("is_debilitated", False) or twelfth_lord_p["sign_index"] == k_sign)) or
        k_sign in [ninth_sign, twelfth_sign]
    )

    arudam_house_from_u = ((a_sign - u_sign) % 12) + 1
    purpose_map = {
        1: ("Personal Relocation / Self-settlement", "சுய குடியேற்றம் / சொந்த முயற்சி"),
        2: ("Earning Wealth / Financial Contract", "தன லாபம் / நிதி ஈட்டுதல்"),
        3: ("Short Assignment / Transfer", "குறுகிய கால பணி / இடமாற்றம்"),
        4: ("Family Relocation / Property Settlement", "குடும்பத்துடன் வாசம் / சொத்து காரணங்கள்"),
        5: ("Child Birth / Creative Pursuit / Spiritual Pilgrimage", "குழந்தை பிறப்பு / கலை / ஆன்மீகம்"),
        6: ("Medical Treatment / Employment / Disease Cure", "மருத்துவ சிகிச்சை / ஒப்பந்த வேலை"),
        7: ("Spouse Reunion / Business Partnership / Foreign Client", "மனைவி/கணவருடன் இணைதல் / சர்வதேச கூட்டு தொழில்"),
        8: ("Emergency Relocation / Research / Crisis Relief", "ஆராய்ச்சி பணி / அவசர பயணம்"),
        9: ("Higher Education / University / Spiritual Pilgrimage", "உயர்கல்வி / பல்கலைக்கழக படிப்பு / யாத்திரை"),
        10: ("Career Advancement / Job Employment / Corporate Posting", "வேலை / உத்தியோக உயர்வு / சர்வதேச பணி"),
        11: ("Fulfillment of Dream / Extreme Wealth Accumulation", "நினைத்த காரிய வெற்றி / பெரும் பொருளாதார லாபம்"),
        12: ("Permanent Residency / Emigration / Spiritual Retreat", "நிரந்தர குடியுரிமை / மோட்சம் / வெளிநாட்டு வாசம்"),
    }
    purp_en, purp_ta = purpose_map.get(arudam_house_from_u, ("Foreign Travel", "வெளிநாட்டுப் பயணம்"))

    foreign_travel_analysis = {
        "snake_approaching_udayam": snake_approaching,
        "udayam_lord_exalted": u_lord_is_exalted,
        "can_travel": can_travel,
        "citizenship_green_card_favorable": citizenship_favorable,
        "travel_purpose_en": f"Arudam in {arudam_house_from_u}th house from Udayam: {purp_en}",
        "travel_purpose_ta": f"உதயத்திற்கு ஆருடம் {arudam_house_from_u}-ம் பாவகத்தில் உள்ளது: {purp_ta}",
        "afflicted_lords": afflicted_travel_lords,
        "kavippu_in_travel_houses": kavippu_in_travel_houses,
        "verdict_en": (
            "100% Foreign travel confirmed! Snake approaching Udayam / Udayam lord exalted."
            if can_travel
            else "Foreign travel faces denial or cancellation due to Kavippu or 9th/11th/12th lord affliction."
        ),
        "verdict_ta": (
            "100% வெளிநாட்டுப் பயணம் உறுதியாகிறது! பாம்பு கிரகம் உதயத்தை அணுகுகிறது அல்லது உதயாதிபதி உச்சம்."
            if can_travel
            else "9, 11, 12-ம் பாவகங்களில் கவிப்பு அல்லது அதிபதிகள் பலவீனத்தால் பயணத்தில் தடை உண்டாகும்."
        ),
    }

    # 12. Court Case & Litigation Analysis
    u_lord_bhava = ((u_lord_sign - u_sign) % 12) + 1
    u_lord_in_3_or_11_exalted = (u_lord_bhava in [3, 11]) and u_lord_is_exalted

    seventh_sign = ((u_sign + 7 - 2) % 12) + 1
    seventh_lord = SIGN_LORDS[seventh_sign]
    seventh_lord_p = next((p for p in transit_planets if p["name_en"] == seventh_lord), None)
    seventh_lord_has_kavippu = (seventh_lord_p["sign_index"] == k_sign) if seventh_lord_p else False
    kavippu_in_7th = (k_sign == seventh_sign)

    querent_wins_via_opponent_kavippu = (kavippu_in_7th or seventh_lord_has_kavippu)
    querent_loses_kavippu_11 = (k_bhava == 11)

    merc_p = next((p for p in transit_planets if p["name_en"] == "Mercury"), None)
    merc_debilitated = merc_p.get("is_debilitated", False) if merc_p else False

    planets_in_u_names = [p["name_en"] for p in planets_in_u]
    moon_in_u = "Moon" in planets_in_u_names
    venus_in_u = "Venus" in planets_in_u_names
    jupiter_in_u = "Jupiter" in planets_in_u_names
    snake_in_u = any(n in ["Snake", "Rahu", "Ketu"] for n in planets_in_u_names)

    if u_lord_in_3_or_11_exalted:
        court_verdict_en = "Querent victory for sure! (Udayam Lord exalted in 3rd/11th house)."
        court_verdict_ta = "வழக்கில் கேள்வியாளருக்கு உறுதியான வெற்றி! (உதயாதிபதி 3 அல்லது 11-ல் உச்சம்)."
    elif querent_wins_via_opponent_kavippu:
        court_verdict_en = "QUERENT WINS! Opponent (7th house / 7th lord) is struck down by Kavippu."
        court_verdict_ta = "கேள்வியாளருக்கு வெற்றி! எதிராளியைக் குறிக்கும் 7-ம் பாவம்/அதிபதி கவிப்பால் வீழ்ச்சியடைகிறது."
    elif querent_loses_kavippu_11:
        court_verdict_en = "Querent faces setback/loss! (Kavippu in 11th house denies victory)."
        court_verdict_ta = "கேள்வியாளருக்கு பாதகமான முடிவு! (11-ல் கவிப்பு வெற்றியையும் சாதகமான தீர்ப்பையும் முடக்குகிறது)."
    else:
        court_verdict_en = "Court proceeding requires strong evidence and sustained advocacy."
        court_verdict_ta = "வழக்கில் தெளிவான ஆதாரங்களுடன் பொறுமையாக செயல்பட வேண்டும்."

    court_case_analysis = {
        "udayam_lord_in_3_or_11_exalted": u_lord_in_3_or_11_exalted,
        "kavippu_in_7th_house": kavippu_in_7th,
        "seventh_lord_has_kavippu": seventh_lord_has_kavippu,
        "kavippu_in_11th_house": querent_loses_kavippu_11,
        "mercury_debilitated": merc_debilitated,
        "moon_in_udayam_fast_verdict": moon_in_u,
        "venus_in_udayam_money_victory": venus_in_u,
        "jupiter_in_udayam_settlement": jupiter_in_u,
        "snake_in_udayam_crisis": snake_in_u,
        "verdict_en": court_verdict_en,
        "verdict_ta": court_verdict_ta,
    }

    # 13. Loans & Financial Debt Analysis
    sixth_sign = ((u_sign + 6 - 2) % 12) + 1
    sixth_lord = SIGN_LORDS[sixth_sign]
    sixth_lord_p = next((p for p in transit_planets if p["name_en"] == sixth_lord), None)
    sixth_lord_afflicted = (
        (sixth_lord_p and (sixth_lord_p.get("is_debilitated", False) or sixth_lord_p["sign_index"] == k_sign)) or
        (k_sign == sixth_sign)
    )
    kavippu_in_2_or_11 = (k_bhava in [2, 11])

    loan_approved = (u_lord_is_exalted or jupiter_exalted) and not sixth_lord_afflicted and not kavippu_in_2_or_11

    loan_scale_en = []
    loan_scale_ta = []
    if jupiter_exalted or not jupiter_debilitated:
        loan_scale_en.append("Jupiter supports huge institutional / bank funding")
        loan_scale_ta.append("குரு பலம் பெரிய அளவிலான வங்கி கடனை பெற்றுத்தரும்")
    if venus_in_u or (next((p for p in transit_planets if p["name_en"] == "Venus"), None) or {}).get("is_exalted", False):
        loan_scale_en.append("Venus indicates sanction of lakhs / crores in funds")
        loan_scale_ta.append("சுக்கிரன் லட்சக்கணக்கிலான பெரும் நிதியை குறிக்கிறது")
    if merc_p and not merc_debilitated:
        loan_scale_en.append("Mercury ensures fast documentation & cheque release")
        loan_scale_ta.append("புதன் விரைவான ஆவண ஒப்புதலையும் காசோலை விடுவிப்பையும் உறுதி செய்கிறது")

    loans_analysis = {
        "loan_approved": loan_approved,
        "sixth_lord_afflicted": sixth_lord_afflicted,
        "kavippu_in_2_or_11": kavippu_in_2_or_11,
        "scale_indicators_en": loan_scale_en,
        "scale_indicators_ta": loan_scale_ta,
        "verdict_en": (
            "Loan sanction and fund release highly favorable!"
            if loan_approved
            else "Cannot obtain loan or severe hurdles in approval (Afflicted 6th/2nd/11th house)."
        ),
        "verdict_ta": (
            "கடன் ஒப்புதல் மற்றும் பண வரவு மிகச் சாதகமாக முடியும்!"
            if loan_approved
            else "கடன் கிடைப்பது கடினம் அல்லது 6/2/11-ல் கவிப்பால் பெரும் இழுபறி உண்டாகும்."
        ),
    }

    # 14. Agriculture, Borewell & Rain Analysis
    fourth_sign = ((u_sign + 4 - 2) % 12) + 1
    kavippu_in_4th = (k_sign == fourth_sign)

    first_app = approaching[0] if approaching else None
    crop_map = {
        "Sun": ("Paddy, wheat, red gram, timber, medicinal plants", "நெல், கோதுமை, துவரை, மரப்பயிர்கள், மூலிகைகள்"),
        "Moon": ("Paddy, sugarcane, watery crops, vegetables, flowers", "நெல், கரும்பு, நீர் சார்ந்த பயிர்கள், காய்கறி, பூக்கள்"),
        "Mars": ("Red chillies, pulses, ginger, garlic, coffee/tea", "மிளகாய், துவரை, இஞ்சி, பூண்டு, தோட்டக்கலை"),
        "Mercury": ("Green leafy vegetables, pulses, bananas, grass", "பச்சை காய்கறிகள், பாசிப்பயறு, வாழை, தீவனப் பயிர்கள்"),
        "Jupiter": ("Turmeric, sugarcane, yellow fruits, grains", "மஞ்சள், கரும்பு, மாமரங்கள், நெல், தானியங்கள்"),
        "Venus": ("Cotton, flowers, jasmine, exotic fruits, cash crops", "பருத்தி, மல்லிகை, மலர்கள், பணப்பயிர்கள்"),
        "Saturn": ("Sesame (Til), oilseeds, black gram, ironwood", "எள், எண்ணெய் வித்துக்கள், உளுந்து, பனை"),
        "Snake": ("Roots, tubers, poisonous plants, spices", "கிழங்கு வகைகள், பூச்சிக்கொல்லி சார்ந்த பயிர்கள், நறுமணப் பொருட்கள்"),
        "Rahu": ("Roots, tubers, poisonous plants, spices", "கிழங்கு வகைகள், பூச்சிக்கொல்லி சார்ந்த பயிர்கள், நறுமணப் பொருட்கள்"),
        "Ketu": ("Medicinal roots, pulses, traditional grains", "மூலிகைகள், கொள்ளு, பாரம்பரிய தானியங்கள்"),
    }
    app_planet_name = first_app["name_en"] if first_app else "Moon"
    crop_en, crop_ta = crop_map.get(app_planet_name, ("General crops", "பொதுவான பயிர்கள்"))

    watery_signs = [4, 8, 12]
    rain_expected = False
    for p in approaching:
        if p["name_en"] in ["Moon", "Venus"]:
            tp = next((x for x in transit_planets if x["name_en"] == p["name_en"]), None)
            if tp and tp["sign_index"] in watery_signs:
                rain_expected = True
                break

    moon_p = next((p for p in transit_planets if p["name_en"] == "Moon"), None)
    venus_p = next((p for p in transit_planets if p["name_en"] == "Venus"), None)
    moon_has_k = (moon_p["sign_index"] == k_sign) if moon_p else False
    venus_has_k = (venus_p["sign_index"] == k_sign) if venus_p else False
    borewell_water = not (kavippu_in_4th or k_bhava == 11 or moon_has_k or venus_has_k)

    snake_with_k = (k_sign in [p["sign_index"] for p in transit_planets if p["name_en"] in ["Rahu", "Ketu"]]) or any(g["sign_index"] == k_sign for g in jama_graha_placements if g["name_en"] == "Snake")

    if borewell_water:
        if moon_in_u or venus_in_u:
            depth_en = "Shallow depth (Sweet water will be struck quickly at low depth)"
            depth_ta = "குறைந்த ஆழத்திலேயே நல்ல குடிநீர் கிட்டும்"
        elif "Saturn" in planets_in_u_names:
            depth_en = "Deep borewell required (Deep rock drilling)"
            depth_ta = "அதிக ஆழம் தோண்ட வேண்டும் (பாறைகளைத் தாண்டி நீர் கிட்டும்)"
        elif snake_in_u:
            depth_en = "Very deep borewell required (Extreme depth)"
            depth_ta = "மிக அதிக ஆழத்தில் நீர் கிட்டும்"
        else:
            depth_en = "Moderate depth (Standard regional borewell level)"
            depth_ta = "மத்திம ஆழத்தில் நீர் ஊற்று பிறக்கும்"
    else:
        depth_en = "Dry borewell / Water obstruction"
        depth_ta = "தண்ணீர் கிடைக்க வாய்ப்பில்லை / வறண்ட போர்வெல்"

    u_dir = udhayam_data["direction_en"]
    u_dir_ta = udhayam_data["direction_ta"]

    agriculture_borewell_rain_analysis = {
        "kavippu_in_4th_house": kavippu_in_4th,
        "crop_indicated_en": f"{app_planet_name} approaching: {crop_en}",
        "crop_indicated_ta": f"{app_planet_name} உதயத்தை அணுகுகிறது: {crop_ta}",
        "rain_expected": rain_expected,
        "rain_verdict_en": "Rain will come! Watery planet (Moon/Venus) approaching in watery sign." if rain_expected else "Rain is doubtful / dry weather.",
        "rain_verdict_ta": "மழை நிச்சயம் பொழியும்! ஜல ராசியில் சுப கிரகம் உதயத்தை அணுகுகிறது." if rain_expected else "மழை வாய்ப்பு குறைவு / வறண்ட வானிலை.",
        "borewell_water_available": borewell_water,
        "borewell_drilling_bit_warning": snake_with_k,
        "water_depth_en": depth_en,
        "water_depth_ta": depth_ta,
        "water_direction_en": f"Udayam Direction: {u_dir}",
        "water_direction_ta": f"உதய திசை: {u_dir_ta}",
    }

    # 15. Share Market & Commodities
    share_market_loss = (kavippu_in_5th or k_bhava in [1, 2, 11])
    can_buy_shares = not share_market_loss

    commodities_eval: Dict[str, Any] = {}
    for com_key, com_meta in COMMODITY_KARAKAS.items():
        c_planet = com_meta["planet"]
        cp = next((p for p in transit_planets if p["name_en"] == c_planet), None)
        c_exalted = cp.get("is_exalted", False) if cp else False
        c_debilitated = cp.get("is_debilitated", False) if cp else False
        c_has_k = (cp["sign_index"] == k_sign) if cp else False

        if c_exalted and not c_has_k:
            price_trend = "Bullish / Price Will Rise (ஏற்றம்)"
            trend_type = "bullish"
        elif c_debilitated or c_has_k:
            price_trend = "Bearish / Price Will Fall (இறக்கம் / சரிவு)"
            trend_type = "bearish"
        else:
            price_trend = "Range-bound / Steady (நிலையான போக்கு)"
            trend_type = "steady"

        commodities_eval[com_key] = {
            "commodity_en": com_meta["en"],
            "commodity_ta": com_meta["ta"],
            "planet": c_planet,
            "trend": price_trend,
            "trend_type": trend_type,
        }

    share_market_analysis = {
        "can_buy_shares": can_buy_shares,
        "kavippu_in_speculative_house": share_market_loss,
        "verdict_en": (
            "Share market investment favorable! 5th, 2nd, and 11th houses free from Kavippu."
            if can_buy_shares
            else "Do NOT buy shares! Kavippu in speculative houses causes sudden financial collapse."
        ),
        "verdict_ta": (
            "பங்குச்சந்தை முதலீடு சாதகமானது! 5, 2, 11-ம் பாவங்கள் கவிப்பின்றி சுபமாக உள்ளன."
            if can_buy_shares
            else "பங்குச்சந்தையில் முதலீடு செய்ய வேண்டாம்! கவிப்பு நஷ்டத்தை ஏற்படுத்தும்."
        ),
        "commodities": commodities_eval,
    }

    # 16. Conjoined Inner and Outer Planets (இரட்டிப்பு பலன் / Magnified Results)
    conjoined = []
    for sign_i in range(1, 13):
        t_in_s = [p["name_en"] for p in transit_planets if p["sign_index"] == sign_i]
        j_in_s = [g["name_en"] for g in jama_graha_placements if g["sign_index"] == sign_i]
        if t_in_s and j_in_s:
            s_meta = ZODIAC_SIGNS[sign_i]
            conjoined.append({
                "sign_index": sign_i,
                "sign_name_en": s_meta["name_en"],
                "sign_name_ta": s_meta["name_ta"],
                "transit_planets": t_in_s,
                "jama_grahas": j_in_s,
                "effect_en": f"Inner transit ({', '.join(t_in_s)}) and Outer Jama ({', '.join(j_in_s)}) conjoined in {s_meta['name_en']}: Magnifies the event results twofold (Double Impact)!",
                "effect_ta": f"உள் கிரகமும் ({', '.join(t_in_s)}) வெளி ஜாம கிரகமும் ({', '.join(j_in_s)}) {s_meta['name_ta']} ராசியில் இணைந்துள்ளன: இரட்டிப்பு பலன் (Double Impact) உண்டாகும்!",
            })

    # 17. Parivartana (Mutual Sign Exchange) between planets
    parivartanas = []
    checked_pairs = set()
    for p1 in transit_planets:
        lord_of_p1_sign = SIGN_LORDS[p1["sign_index"]]
        p2 = next((x for x in transit_planets if x["name_en"] == lord_of_p1_sign), None)
        if p2 and p2["name_en"] != p1["name_en"]:
            pair_key = tuple(sorted([p1["name_en"], p2["name_en"]]))
            if pair_key not in checked_pairs:
                checked_pairs.add(pair_key)
                lord_of_p2_sign = SIGN_LORDS[p2["sign_index"]]
                if lord_of_p2_sign == p1["name_en"]:
                    parivartanas.append({
                        "planet_1": p1["name_en"],
                        "sign_1": ZODIAC_SIGNS[p1["sign_index"]]["name_en"],
                        "planet_2": p2["name_en"],
                        "sign_2": ZODIAC_SIGNS[p2["sign_index"]]["name_en"],
                        "description_en": f"Parivartana between {p1['name_en']} and {p2['name_en']}: Results will be exchanged or reversed.",
                        "description_ta": f"{p1['name_en']} மற்றும் {p2['name_en']} இடையே பரிவர்த்தனை: காரிய பலன்கள் பரஸ்பரம் மாறும்.",
                    })

    # 18. 8th Lord in Udayam (Chronic lingering problems)
    eighth_sign = ((u_sign + 8 - 2) % 12) + 1
    eighth_lord = SIGN_LORDS[eighth_sign]
    eighth_lord_in_u = any(p["name_en"] == eighth_lord for p in planets_in_u)
    eighth_lord_analysis = {
        "eighth_lord": eighth_lord,
        "is_in_udayam": eighth_lord_in_u,
        "warning_en": (
            f"8th Lord {eighth_lord} resides in Udayam: Chronic, lingering problems and persistent stress."
            if eighth_lord_in_u
            else "8th Lord does not afflict Udayam."
        ),
        "warning_ta": (
            f"8-ம் அதிபதி {eighth_lord} உதயத்தில் உள்ளார்: நீண்ட கால நாள்பட்ட சிக்கல் மற்றும் மன அழுத்தம் உண்டாகும்."
            if eighth_lord_in_u
            else "8-ம் அதிபதி உதயத்தை பாதிக்கவில்லை."
        ),
    }

    # 19. Snake Approaching / in Udayam Analysis
    snake_udayam_analysis = {
        "snake_approaching": snake_approaching,
        "snake_in_udayam": snake_in_u,
        "effect_en": (
            "Snake (Rahu) approaching or in Udayam: Warning of hidden crises, outsider complications, or infections; "
            "however, highly auspicious for foreign travel and pregnancy/conception!"
            if (snake_approaching or snake_in_u)
            else "Snake has no direct adverse grip on Udayam."
        ),
        "effect_ta": (
            "பாம்பு (ராகு) உதயத்தை அணுகுகிறது/உதயத்தில் உள்ளது: அந்நிய நபர்களால் சிக்கல் அல்லது விஷக் காய்ச்சல் எச்சரிக்கை; "
            "ஆயினும் வெளிநாட்டுப் பயணம் மற்றும் புத்திர பாக்கியத்திற்கு இது மிகவும் உகந்தது!"
            if (snake_approaching or snake_in_u)
            else "பாம்பு கிரகம் உதயத்தை நேரடியாக பற்றவில்லை."
        ),
    }

    # 20. Kavippu Bhava (1-12) & Udayam Lord Thought (1-12) Lookups
    kavippu_bhava_effect = KAVIPPU_BHAVA_EFFECTS.get(k_bhava, {
        "en": f"Kavippu in {k_bhava}th house from Udayam.",
        "ta": f"உதயத்திற்கு {k_bhava}-ம் பாவகத்தில் கவிப்பு.",
    })

    udayam_lord_thought = UDAYAM_LORD_THOUGHT_EFFECTS.get(u_lord_bhava, {
        "en": f"Udayam Lord in {u_lord_bhava}th house from Udayam.",
        "ta": f"உதயாதிபதி உதயத்திற்கு {u_lord_bhava}-ம் பாவகத்தில் உள்ளார்.",
    })

    # 21. Evil Spirits & Black Magic Analysis (பில்லி சூனியம் & துஷ்ட சக்தி)
    mandi_p = next((p for p in transit_planets if "Mandi" in p["name_en"] or "Gulika" in p["name_en"]), None)
    mandi_sign = mandi_p["sign_index"] if mandi_p else 1

    # Rule 1: Udayam Lord with Mandi -> Person under evil spirits
    querent_evil_spirits = (u_lord_sign == mandi_sign)

    # Rule 2: Planet with Mandi -> That Jeeva Karaka is affected by black magic
    planets_with_mandi = [
        p["name_en"] for p in transit_planets
        if p["sign_index"] == mandi_sign and "Mandi" not in p["name_en"] and "Gulika" not in p["name_en"]
    ]
    jeeva_afflicted = []
    for p_name in planets_with_mandi:
        jk = JEEVA_KARAKA_MAP.get(p_name)
        if jk:
            jeeva_afflicted.append({
                "planet": p_name,
                "person_en": jk["en"],
                "person_ta": jk["ta"],
            })

    # Rule 3: Snake coming towards Udayam + Black magic query -> Predict YES
    black_magic_present = snake_approaching or querent_evil_spirits

    # Rule 4: Planet with Kavippu reveals the nature of the perpetrator
    perpetrator_planet = None
    for p in transit_planets:
        if p["sign_index"] == k_sign and "Mandi" not in p["name_en"] and "Gulika" not in p["name_en"]:
            perpetrator_planet = p["name_en"]
            break
    if not perpetrator_planet:
        for g in jama_graha_placements:
            if g["sign_index"] == k_sign:
                perpetrator_planet = g["name_en"]
                break
    if not perpetrator_planet:
        perpetrator_planet = SIGN_LORDS.get(k_sign, "Saturn")

    perpetrator_info = BLACK_MAGIC_SORCERER_KARAKAS.get(perpetrator_planet, {
        "en": "Hidden adversary / Unknown third party",
        "ta": "மறைமுக எதிரி / அடையாளம் தெரியாத நபர்",
    })

    # Rule 5: When Udayam and Udayam Lord are strong, black magic cannot harm
    u_has_benefics = any(p["name_en"] in ["Jupiter", "Venus", "Mercury"] for p in planets_in_u)
    udayam_immune = (u_lord_is_exalted or u_has_benefics) and (k_sign != u_sign) and not querent_evil_spirits

    # Rule 6: Mandi in 4th house -> Residence is haunted
    mandi_bhava = ((mandi_sign - u_sign) % 12) + 1
    haunted_residence = (mandi_bhava == 4)

    # Rule 7 & 8: Saturn, Rahu, Ketu, Mandi combinations
    saturn_sign = saturn_planet["sign_index"] if saturn_planet else 10
    rahu_p = next((p for p in transit_planets if p["name_en"] in ["Rahu", "Snake"]), None)
    ketu_p = next((p for p in transit_planets if p["name_en"] == "Ketu"), None)
    rahu_sign = rahu_p["sign_index"] if rahu_p else 1
    ketu_sign = ketu_p["sign_index"] if ketu_p else 7

    sa_ra_mandi_combined = (saturn_sign == mandi_sign and rahu_sign == mandi_sign)
    sa_ke_mandi_combined = (saturn_sign == mandi_sign and ketu_sign == mandi_sign)

    evil_spirits_black_magic_analysis = {
        "querent_under_evil_spirits": querent_evil_spirits,
        "black_magic_present": black_magic_present,
        "black_magic_cannot_harm_querent": udayam_immune,
        "haunted_residence_mandi_in_4th": haunted_residence,
        "mandi_bhava_from_udayam": mandi_bhava,
        "afflicted_jeeva_karakas": jeeva_afflicted,
        "perpetrator_profile": {
            "planet": perpetrator_planet,
            "description_en": perpetrator_info["en"],
            "description_ta": perpetrator_info["ta"],
        },
        "divine_trance_or_hallucination": sa_ke_mandi_combined,
        "severe_evil_possession_transit": sa_ra_mandi_combined,
        "summary_en": (
            "Udayam and Udayam Lord are powerfully fortified: Black magic cannot harm the querent!"
            if udayam_immune
            else (
                "Evil spirits or black magic influence detected (Udayam Lord / Snake affliction)."
                if black_magic_present or querent_evil_spirits
                else "No acute evil spirits or occult affliction observed."
            )
        ),
        "summary_ta": (
            "உதயமும் உதயாதிபதியும் பலமாக உள்ளதால் பில்லி, சூனியத்தால் எவ்வித பாதிப்பும் ஏற்படுத்த இயலாது!"
            if udayam_immune
            else (
                "துஷ்ட சக்தி அல்லது மாந்திரீக தாக்கம் பிரசன்னத்தில் புலப்படுகிறது."
                if black_magic_present or querent_evil_spirits
                else "துஷ்ட சக்தி அல்லது செய்வினை தோஷங்கள் பிரசன்னத்தில் இல்லை."
            )
        ),
    }

    # 22. Natural or Unnatural Death Analysis (இயற்கை மரணம் vs துர்மரணம்)
    jupiter_sign = jupiter_planet["sign_index"] if jupiter_planet else 4
    jup_influences_udayam = (jupiter_sign in [u_sign, u_lord_sign]) or (((jupiter_sign - u_sign) % 12) + 1 in [5, 7, 9])
    mandi_influences_udayam = (mandi_sign in [u_sign, u_lord_sign]) or (((mandi_sign - u_sign) % 12) + 1 == 7)

    natural_unnatural_death_analysis = {
        "jupiter_influences_udayam": jup_influences_udayam,
        "mandi_influences_udayam": mandi_influences_udayam,
        "death_nature": "Natural Death (Peaceful transition with Jupiter's grace)" if jup_influences_udayam and not mandi_influences_udayam else (
            "Unnatural Death (Accident, trauma, poison or sudden crisis via Mandi)" if mandi_influences_udayam else "Standard Health & Longevity Cycle"
        ),
        "death_nature_ta": "இயற்கை மரணம் (குருவின் ஆசியுடன் கூடிய சாந்தமான முக்தி)" if jup_influences_udayam and not mandi_influences_udayam else (
            "துர்மரணம் (விபத்து, தற்கொலை, விஷம், மாந்தி தோஷத்தால் திடீர் கண்டம்)" if mandi_influences_udayam else "இயல்பான ஆயுள் மற்றும் உடல் நலம்"
        ),
    }

    # 23. Rain, Natural Disaster & Catastrophe (இயற்கை பேரிடர் & புயல் பாதுகாப்பு)
    saturn_approaching = any(p["name_en"] == "Saturn" for p in approaching)
    saturn_in_3rd = (saturn_planet is not None and ((saturn_planet["sign_index"] - u_sign) % 12) + 1 == 3)
    cyclone_protection = (saturn_approaching or saturn_in_3rd or u_lord_debilitated)

    rain_disaster_catastrophe_analysis = {
        "cyclone_protection_active": cyclone_protection,
        "cyclone_verdict_en": (
            "Cyclone Protection Active! Saturn approaching Udayam, Saturn in 3rd, or Udayam Lord debilitated: "
            "That place will NOT be affected by cyclone or stormy destruction!"
            if cyclone_protection
            else "Standard weather vulnerability; precautionary storm alerts apply."
        ),
        "cyclone_verdict_ta": (
            "புயல் பாதிப்பு ஏற்படாது! சனி உதயத்தை நெருங்குவதாலோ, 3-ல் சனி இருப்பதாலோ, அல்லது உதயாதிபதி நீசத்தாலோ "
            "அப்பகுதிக்கு புயலால் எவ்வித பெரும் சேதமும் உண்டாகாது!"
            if cyclone_protection
            else "இயல்பான வானிலை நிலவரம்; புயல் முன்னெச்சரிக்கைகள் அவசியம்."
        ),
        "calamity_significations": {
            "snake_mass_casualty": "Snake signifies mass-scale calamity, major transport disaster or epidemic",
            "mars_riots_earthquake_fire": "Mars signifies earthquakes, riots, strikes, and fire disasters",
            "moon_venus_rain_floods": "Moon & Venus signify heavy rains, dam overflow, and water inundation",
        },
    }

    # 24. Muhurata Analysis (Classical Jamakkol Shastra Muhurta)
    # 24.1 Marriage Muhurta
    # Udayam = Groom (Male), Arudam = Bride (Female)
    a_lord = SIGN_LORDS[a_sign]
    a_lord_p = next((p for p in transit_planets if p["name_en"] == a_lord), None)
    a_lord_sign = a_lord_p["sign_index"] if a_lord_p else a_sign
    a_lord_is_debilitated = (a_lord_sign == PLANET_DIGNITIES.get(a_lord, {}).get("debilitated", -1))

    seventh_from_a_sign = ((a_sign + 7 - 2) % 12) + 1
    seventh_from_a_lord = SIGN_LORDS[seventh_from_a_sign]
    seventh_from_a_lord_p = next((p for p in transit_planets if p["name_en"] == seventh_from_a_lord), None)
    seventh_from_a_lord_has_k = (seventh_from_a_lord_p["sign_index"] == k_sign) if seventh_from_a_lord_p else False

    kavippu_in_7_from_u = (k_sign == seventh_sign)
    kavippu_in_7_from_a = (k_sign == seventh_from_a_sign)
    kavippu_in_u_or_a = (k_sign in [u_sign, a_sign])

    u_a_relation_house = ((a_sign - u_sign) % 12) + 1
    u_a_favorable_relation = u_a_relation_house in [3, 11, 5, 9]

    lords_debilitated = (u_lord_debilitated or a_lord_is_debilitated)
    lords_with_kavippu = (u_lord_sign == k_sign or a_lord_sign == k_sign)
    sevenths_with_kavippu = (seventh_lord_has_kavippu or seventh_from_a_lord_has_k or kavippu_in_7_from_u or kavippu_in_7_from_a)

    marriage_muhurta_auspicious = (
        not lords_debilitated and
        not lords_with_kavippu and
        not kavippu_in_u_or_a and
        not sevenths_with_kavippu and
        u_a_favorable_relation
    )

    # 24.2 Couple Reunion after Separation
    venus_p = next((p for p in transit_planets if p["name_en"] == "Venus"), None)
    venus_exalted = venus_p.get("is_exalted", False) if venus_p else False
    taurus_libra_udayam = u_sign in [2, 7]
    couple_reunion_golden_hour = taurus_libra_udayam and venus_exalted

    approaching_benefic = next((p for p in approaching if p["name_en"] in ["Jupiter", "Moon", "Venus", "Mercury"]), None)
    reunion_mediator_advice_en = ""
    reunion_mediator_advice_ta = ""
    if approaching_benefic:
        app_name = approaching_benefic["name_en"]
        relative_label = JEEVA_KARAKA_MAP.get(app_name, {}).get("en", "Relative")
        relative_label_ta = JEEVA_KARAKA_MAP.get(app_name, {}).get("ta", "உறவினர்")
        reunion_mediator_advice_en = f"{app_name} approaching Udayam: Groom's {relative_label} should visit and negotiate with bride's parents - Reunion will be successful!"
        reunion_mediator_advice_ta = f"{app_name} உதயத்தை அணுகுகிறது: மணமகனின் {relative_label_ta} பெண் வீட்டாரிடம் பேசி சமரசம் பேசினால் தம்பதியர் மீண்டும் இணைவர்!"

    # 24.3 Business Muhurta
    # Saturn, 10th lord, UD lord not with Kavippu; Kavippu not in 2, 11
    business_muhurta_favorable = not (
        saturn_has_kavippu or
        (tenth_lord_sign == k_sign) or
        (u_lord_sign == k_sign) or
        (k_bhava in [2, 11])
    )

    # 24.4 Construction Muhurta
    # Kavippu not in 4th or with Mars/Venus
    mars_p = next((p for p in transit_planets if p["name_en"] == "Mars"), None)
    mars_has_k = (mars_p["sign_index"] == k_sign) if mars_p else False
    construction_muhurta_favorable = not (kavippu_in_4th or mars_has_k or venus_has_k)

    # 24.5 Document & Call Muhurta
    # Mercury debilitated or Kavippu in 3rd -> failure
    kavippu_in_3rd = (k_bhava == 3)
    documentation_call_favorable = not (merc_debilitated or kavippu_in_3rd)

    # 24.6 Loan Muhurta
    # Benefic approaching, Kavippu not in U, A -> Loan easily sanctioned and repaid
    # If Sa, Snake, Ma approaching or deb in U, or Kavippu in 6, 11, 2 -> DO NOT APPLY
    malefic_approaching = any(p["name_en"] in ["Saturn", "Snake", "Rahu", "Mars"] for p in approaching)
    loan_muhurta_favorable = (approaching_benefic is not None) and not kavippu_in_u_or_a and not malefic_approaching and not debilitated_in_udayam and not (k_bhava in [6, 11, 2])

    # 24.7 Approaching Planet Advice for Current Jamam
    primary_approaching_name = approaching[0]["name_en"] if approaching else "None"
    approaching_muhurta_info = APPROACHING_PLANET_MUHURTA_SIGNIFICATIONS.get(primary_approaching_name, {
        "en": "General steady conditions; proceed with standard astrological considerations.",
        "ta": "இயல்பான காரிய நகர்வு; பொதுவான பஞ்சாங்க சுப நேரம் பார்த்து செயல்படவும்.",
        "auspicious_for": ["General Actions"],
    })

    muhurta_analysis = {
        "marriage_muhurta": {
            "is_auspicious": marriage_muhurta_auspicious,
            "verdict_en": "Highly Auspicious Marriage Muhurta! Both Udayam and Arudam, lords, and 7th houses are pure and harmoniously aligned." if marriage_muhurta_auspicious else "Inauspicious for Marriage: Affliction by Kavippu, debilitation, or conflicting Udayam-Arudam distance.",
            "verdict_ta": "மிகச் சிறந்த திருமண முகூர்த்தம்! உதயம், ஆருடம், அதிபதிகள் மற்றும் 7-ம் பாவகங்கள் சுபமாக பொருந்தியுள்ளன." if marriage_muhurta_auspicious else "திருமணத்திற்கு உகந்த நேரம் அல்ல: கவிப்பு தாக்கம், நீசம் அல்லது உதயம்-ஆருட முரண்பாடு உள்ளது.",
            "udayam_groom_sign": ZODIAC_SIGNS[u_sign]["name_en"],
            "arudam_bride_sign": ZODIAC_SIGNS[a_sign]["name_en"],
            "u_a_distance": u_a_relation_house,
            "lords_debilitated": lords_debilitated,
            "lords_with_kavippu": lords_with_kavippu,
            "sevenths_afflicted": sevenths_with_kavippu,
        },
        "couple_reunion": {
            "is_golden_hour": couple_reunion_golden_hour,
            "mediator_advice_en": reunion_mediator_advice_en or "Ensure elders mediate when benefics approach Udayam.",
            "mediator_advice_ta": reunion_mediator_advice_ta or "சுப கிரகங்கள் உதயத்தை நெருங்கும் நேரத்தில் பெரியவர்கள் பேசி சமரசம் செய்யவும்.",
        },
        "business_startup_muhurta": {
            "is_auspicious": business_muhurta_favorable,
            "verdict_en": "Auspicious for starting new business venture (Saturn, 10th Lord, and Udayam Lord unblemished)." if business_muhurta_favorable else "Postpone new business launch (Afflicted 10th Lord, Saturn, or 2/11 Kavippu).",
            "verdict_ta": "புதிய தொழில் தொடங்குவதற்கு மிகவும் உகந்த நேரம்!" if business_muhurta_favorable else "புதிய தொழில் தொடங்குவதை ஒத்திவைக்கவும் (சனி/10-ம் அதிபதி/கவிப்பு தோஷம்).",
        },
        "construction_muhurta": {
            "is_auspicious": construction_muhurta_favorable,
            "verdict_en": "Favorable for laying foundation stone and starting construction." if construction_muhurta_favorable else "Avoid starting construction now (Kavippu in 4th house or with Mars/Venus).",
            "verdict_ta": "பூமி பூஜை மற்றும் புதிய கட்டடப் பணிகளைத் தொடங்க உகந்த நேரம்!" if construction_muhurta_favorable else "கட்டடப் பணிகளை இப்போது தொடங்க வேண்டாம் (4-ல் கவிப்பு அல்லது செவ்வாய்/சுக்கிரன் கவிப்பு).",
        },
        "documentation_call_muhurta": {
            "is_auspicious": documentation_call_favorable,
            "verdict_en": "Favorable for signing agreements, drafting petitions, and high-stakes calls." if documentation_call_favorable else "High risk of failure or dispute in agreements, documentation, and calls (Mercury debilitated or Kavippu in 3rd).",
            "verdict_ta": "ஒப்பந்தங்கள் கையெழுத்திட மற்றும் முக்கிய தொலைபேசி அழைப்புகளுக்கு உகந்த நேரம்!" if documentation_call_favorable else "பத்திரங்கள், உடன்படிக்கைகள் மற்றும் முக்கிய பேச்சுவார்த்தைகளில் தோல்வி நேரலாம் (புதன் நீசம் / 3-ல் கவிப்பு).",
        },
        "loan_application_muhurta": {
            "is_auspicious": loan_muhurta_favorable,
            "verdict_en": "Apply for loan now! Benefic approaching Udayam ensures swift approval and easy repayment." if loan_muhurta_favorable else "Do NOT apply for loans during this window (Malefic approaching, or Kavippu in 2/6/11).",
            "verdict_ta": "கடன் விண்ணப்பம் செய்ய மிகவும் உகந்த நேரம்! எளிதில் ஒப்புதல் கிட்டும், கடனை சுலபமாக அடைக்கலாம்." if loan_muhurta_favorable else "இப்போது கடனுக்கு விண்ணப்பிக்க வேண்டாம் (அசுப கிரக நெருக்கம் அல்லது 2,6,11-ல் கவிப்பு).",
        },
        "travel_muhurta": {
            "saturn_approaching_delay": saturn_approaching,
            "verdict_en": "Severe delay and obstructions in travel! Avoid starting journey when Saturn approaches Udayam." if saturn_approaching else "Journey can be undertaken safely.",
            "verdict_ta": "பயணத்தில் கடுமையான தாமதமும் தடைகளும் உண்டாகும்! சனி உதயத்தை நெருங்கும் போது பயணத்தை தவிர்க்கவும்." if saturn_approaching else "பயணத்தை தாராளமாக மேற்கொள்ளலாம்.",
        },
        "current_approaching_signification": {
            "planet": primary_approaching_name,
            "advice_en": approaching_muhurta_info["en"],
            "advice_ta": approaching_muhurta_info["ta"],
            "auspicious_activities": approaching_muhurta_info["auspicious_for"],
        },
    }

    # 25. Planetary Attributes Table (Rays, Age, Height, Places, Directions)
    planet_attributes_table = PLANET_ATTRIBUTES

    return {
        "watch_time_relation": watch_time_relation,
        "facing_direction": facing_direction,
        "rising_nature": rising_nature,
        "subh_balance": subh_balance,
        "lord_connections": lord_connections,
        "kavippu_afflictions": kavippu_afflictions,
        "approaching_planets": approaching,
        "crossed_planets": crossed,
        "planets_in_udayam": in_udayam,
        "exalted_debilitated_audit": exalted_debilitated_audit,
        "relationship_analysis": relationships_eval,
        "politics_govt_analysis": politics_analysis,
        "foreign_travel_analysis": foreign_travel_analysis,
        "court_case_analysis": court_case_analysis,
        "loans_analysis": loans_analysis,
        "agriculture_borewell_rain_analysis": agriculture_borewell_rain_analysis,
        "share_market_analysis": share_market_analysis,
        "kavippu_bhava_effect": kavippu_bhava_effect,
        "udayam_lord_thought": udayam_lord_thought,
        "conjoined_inner_outer_planets": conjoined,
        "parivartana_exchanges": parivartanas,
        "eighth_lord_in_udayam": eighth_lord_analysis,
        "snake_udayam_analysis": snake_udayam_analysis,
        "evil_spirits_black_magic_analysis": evil_spirits_black_magic_analysis,
        "natural_unnatural_death_analysis": natural_unnatural_death_analysis,
        "rain_disaster_catastrophe_analysis": rain_disaster_catastrophe_analysis,
        "muhurta_analysis": muhurta_analysis,
        "planet_attributes_table": planet_attributes_table,
    }


def synthesize_jamakkol_prediction(
    udhayam_data: Dict[str, Any],
    aarudham_data: Dict[str, Any],
    kavippu_data: Dict[str, Any],
    active_jamam_ruler: Dict[str, Any],
    jama_graha_placements: List[Dict[str, Any]],
    transit_planets: List[Dict[str, Any]],
    query_category: str = "general",
    classical_rules: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Analyze chart taking into account all classical rules and Diamond principles."""
    u_sign = udhayam_data["sign_index"]
    a_sign = aarudham_data["sign_index"]
    k_sign = kavippu_data["sign_index"]

    house_u_to_a = ((a_sign - u_sign) % 12) + 1
    house_u_to_k = ((k_sign - u_sign) % 12) + 1
    house_a_to_k = ((k_sign - a_sign) % 12) + 1

    watch_res = classical_rules["watch_time_relation"]["result"] if classical_rules else "Success"

    # Base scoring from Watch Time Relation
    if watch_res == "Success":
        score = 75
    elif watch_res == "Delay and Failure":
        score = 42
    else:  # Failure
        score = 28

    # Apply 10th and 11th Lord connection bonuses
    if classical_rules:
        l_conn = classical_rules["lord_connections"]
        if l_conn["tenth_lord_connected"] or l_conn["parivartana_udayam_10th"]:
            score += 15
        if l_conn["eleventh_lord_connected"] or l_conn["parivartana_udayam_11th"]:
            score += 15
        if l_conn["udayam_lord_debilitated"]:
            score -= 25

        # Kavippu in 2nd or 11th penalties
        k_aff = classical_rules["kavippu_afflictions"]
        if k_aff["kavippu_in_2nd"] or k_aff["kavippu_in_11th"]:
            score -= 20

        # Debilitated in Udayam penalty
        if classical_rules["exalted_debilitated_audit"]["debilitated_in_udayam"]:
            score -= 20

        # Facing direction (if no planet in Udayam)
        facing = classical_rules["facing_direction"]
        if facing["applicable"]:
            if facing["facing_type"] == "Urdhomukha":
                score += 15
            elif facing["facing_type"] == "Ardhomukha":
                score -= 15
            elif facing["facing_type"] == "Triyangmukha":
                score += 5

    # Direct Kavippu on Aarudham penalty
    if k_sign == a_sign:
        score -= 30
    if k_sign == u_sign:
        score -= 25

    score = max(5, min(95, score))

    # Formulate status
    if score >= 65 and k_sign != a_sign:
        status = "favorable"
        verdict_title_en = "Favorable - Clear Success (காரிய சித்தி உண்டாகும்)"
        verdict_title_ta = "சுப பலன் - காரிய சித்தி நிச்சயம் உண்டாகும்"
        verdict_summary_en = (
            f"The horary chart confirms clear success. {classical_rules['watch_time_relation']['description_en'] if classical_rules else ''} "
            f"Planetary lords and Jamam influences align favorably."
        )
        verdict_summary_ta = (
            f"பிரசன்னக் கட்டம் காரிய வெற்றியை உறுதி செய்கிறது. {classical_rules['watch_time_relation']['description_ta'] if classical_rules else ''} "
            f"இறையருளும் கிரக பலமும் காரிய அனுகூலத்திற்குத் துணை நிற்கின்றன."
        )
    elif score >= 40:
        status = "delayed_success"
        verdict_title_en = "Delayed Success / Struggle (தாமதத்திற்குப் பின் வெற்றி)"
        verdict_title_ta = "மத்திம பலன் - கடும் முயற்சி & தாமதத்திற்குப் பின் வெற்றி"
        verdict_summary_en = (
            f"The matter faces temporary hurdles. {classical_rules['watch_time_relation']['description_en'] if classical_rules else ''} "
            f"Patience and strategic adjustments will eventually yield success."
        )
        verdict_summary_ta = (
            f"காரியம் உடனடியாக முடியாமல் தாமதப்படும். {classical_rules['watch_time_relation']['description_ta'] if classical_rules else ''} "
            f"பொறுமையுடன் மறுபரிசீலனை செய்து அணுகினால் நற்பலன் கிட்டும்."
        )
    else:
        status = "unfavorable"
        verdict_title_en = "Obstruction / Failure (தடை / தோல்வி / எச்சரிக்கை)"
        verdict_title_ta = "அசுப பலன் - காரியத் தடை அல்லது தோல்வி"
        verdict_summary_en = (
            f"The classical rules indicate negative outcome. {classical_rules['watch_time_relation']['description_en'] if classical_rules else ''} "
            f"Postponing the initiative is strongly advised."
        )
        verdict_summary_ta = (
            f"சாஸ்திர விதிகள் காரியத் தடையைக் காட்டுகின்றன. {classical_rules['watch_time_relation']['description_ta'] if classical_rules else ''} "
            f"புதிய முடிவுகளையோ முதலீடுகளையோ சில காலம் ஒத்திவைப்பது மிக நலம்."
        )

    # Directional Guidance (Lost objects, movement, travel)
    primary_dir = DIRECTIONS_MAP.get(a_sign, {"en": "North", "ta": "வடக்கு", "ruler": "Kubera"})
    directional_en = (
        f"The primary vibrational direction is {primary_dir['en']} "
        f"(Governed by {primary_dir['ruler']}). Lost items, beneficial allies, or the source of news lies in this quadrant."
    )
    directional_ta = (
        f"பிரசன்னத்தின் முதன்மை திசை: {primary_dir['ta']} (அதிபதி: {primary_dir['ruler']}). "
        f"காணாமல் போன பொருள், உதவி புரியும் நபர் அல்லது சுபச் செய்தி இத்திசையிலிருந்து வர வாய்ப்புண்டு."
    )

    # Timing of Event (சம்பவ காலம்)
    u_nature = udhayam_data["nature"]
    deg_diff = abs(aarudham_data["longitude"] - udhayam_data["longitude"]) % 30.0
    units = max(1, int(round(deg_diff / 5.0)))

    if u_nature == "Chara":
        timing_en = f"Very swift development: approximately {units} to {units * 2} days (or hours if urgent)."
        timing_ta = f"மிக விரைவான காரிய நகர்வு: சுமார் {units} முதல் {units * 2} நாட்களுக்குள் (அல்லது அவசர காரியமாயின் சில மணி நேரங்களில்)."
    elif u_nature == "Sthira":
        timing_en = f"Steady and gradual: will materialize in {units} to {units * 2} months."
        timing_ta = f"நிலையான மற்றும் நிதானமான பலன்: சுமார் {units} முதல் {units * 2} மாதங்களுக்குள் முழுமையடையும்."
    else:
        timing_en = f"Dual / fluctuating: progress will emerge within {units} to {units * 2} weeks."
        timing_ta = f"இரு தன்மை கொண்ட நகர்வு: சுமார் {units} முதல் {units * 2} வாரங்களுக்குள் சாதகமான விடை கிடைக்கும்."

    # Category insights
    cat_insights_en: List[str] = []
    cat_insights_ta: List[str] = []

    if query_category == "business_finance":
        if house_u_to_a in [1, 5, 9, 3, 11]:
            cat_insights_en.append("Highly favorable for commercial transactions, profit extraction, and capital recovery.")
            cat_insights_ta.append("வியாபார கொடுக்கல் வாங்கல், தன லாபம் மற்றும் முதலீடு மீட்பிற்கு மிகவும் உகந்த நேரம்.")
        else:
            cat_insights_en.append("Check terms of payment carefully; audit fine print before releasing large sums.")
            cat_insights_ta.append("பணப் பரிவர்த்தனைகளில் விழிப்புணர்வு தேவை; பெரிய தொகை தருவதற்கு முன் ஆவணங்களை சரிபார்க்கவும்.")
    elif query_category == "career_job":
        if house_u_to_a in [1, 5, 9, 11]:
            cat_insights_en.append("Job interview or promotion prospects are strong; superiors will favorably recognize credentials.")
            cat_insights_ta.append("வேலை வாய்ப்பு, நேர்காணல் மற்றும் பதவி உயர்வு விவகாரங்கள் சாதகமாக முடியும்; மேலதிகாரிகள் ஏற்பர்.")
        else:
            cat_insights_en.append("Workplace politics or pending approvals may cause temporary stall; remain patient.")
            cat_insights_ta.append("அலுவலகத்தில் மறைமுகப் போட்டிகள் அல்லது ஒப்புதலில் தாமதம் ஏற்படலாம்; விவேகத்துடன் அணுகவும்.")
    elif query_category == "health_illness":
        if k_sign in [u_sign, a_sign]:
            cat_insights_en.append("Proper medical diagnosis and expert second opinion recommended; hidden roots of symptoms must be examined.")
            cat_insights_ta.append("நோய் கண்டறிதலில் கூடுதல் கவனம் தேவை; நிபுணத்துவ மருத்துவ ஆலோசனை பெற்று மருந்து உட்கொள்ளவும்.")
        else:
            cat_insights_en.append("Vitality is recovering; timely treatment and nutritional care will bring speedy relief.")
            cat_insights_ta.append("உடல் நலம் சீராகி வருகிறது; முறையான மருத்துவம் மற்றும் ஓய்வு மூலம் விரைவில் பூரண குணம் கிட்டும்.")
    elif query_category == "lost_property":
        if k_sign == a_sign:
            cat_insights_en.append("The article is veiled under cloth, inside a closed container, or in dark concealed storage.")
            cat_insights_ta.append("காணாமல் போன பொருள் ஒரு மூடிய பெட்டியில், துணிகளுக்கு அடியில் அல்லது இருட்டான இடத்தில் மறைந்துள்ளது.")
        else:
            cat_insights_en.append(f"The lost item is recoverable towards the {primary_dir['en']} direction near water, altar, or books.")
            cat_insights_ta.append(f"பொருளை மீட்க வாய்ப்புள்ளது; {primary_dir['ta']} திசையில் நீர்நிலை, பூஜை அறை அல்லது ஆவணங்கள் உள்ள இடத்தில் தேடவும்.")
    else:
        cat_insights_en.append(f"Ruling Jamam Lord {active_jamam_ruler['name_en']} dictates the pace of events during this 90-minute window.")
        cat_insights_ta.append(f"தற்போதைய 90 நிமிட ஜாமத்தின் நாதன் {active_jamam_ruler['name_ta']} காரியத்தின் விரைவு மற்றும் முடிவை நிர்ணயிக்கிறார்.")

    # Remedies
    remedies_en: List[str] = [
        f"Chant the sacred Gayatri mantra or prayer associated with Jamam Lord {active_jamam_ruler['name_en']}.",
        f"Offer a ghee lamp facing the {primary_dir['en']} direction to dissolve the shadowy veil of Kavippu.",
        "Perform charity of food or grain to needy living beings or birds before undertaking final action.",
    ]
    remedies_ta: List[str] = [
        f"தற்போதைய ஜாம நாதன் {active_jamam_ruler['name_ta']}க்குரிய காயத்ரி மந்திரம் அல்லது இஷ்ட தெய்வ பிரார்த்தனை செய்தல் நலம்.",
        f"கவிப்பின் மறைமுக தோஷம் நீங்க, {primary_dir['ta']} திசை நோக்கி தூய நெய் தீபம் ஏற்றி வழிபடவும்.",
        "முக்கிய காரியத்திற்கு புறப்படும் முன் பட்சிகளுக்கோ அல்லது ஏழை எளியோருக்கோ சிறு தானம் வழங்குவது காரிய வெற்றியைத் தரும்.",
    ]

    return {
        "status": status,
        "score": score,
        "verdict_title_en": verdict_title_en,
        "verdict_title_ta": verdict_title_ta,
        "verdict_summary_en": verdict_summary_en,
        "verdict_summary_ta": verdict_summary_ta,
        "pillar_dynamics_en": classical_rules["watch_time_relation"]["description_en"] if classical_rules else "",
        "pillar_dynamics_ta": classical_rules["watch_time_relation"]["description_ta"] if classical_rules else "",
        "kavippu_impact_en": classical_rules["kavippu_afflictions"]["afflicted_bhava_meaning_en"] if classical_rules else "",
        "kavippu_impact_ta": classical_rules["kavippu_afflictions"]["afflicted_bhava_meaning_ta"] if classical_rules else "",
        "directional_guidance_en": directional_en,
        "directional_guidance_ta": directional_ta,
        "timing_of_event_en": timing_en,
        "timing_of_event_ta": timing_ta,
        "category_specific_insights_en": cat_insights_en,
        "category_specific_insights_ta": cat_insights_ta,
        "remedial_measures_en": remedies_en,
        "remedial_measures_ta": remedies_ta,
    }
