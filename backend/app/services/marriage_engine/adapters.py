"""Chart data adapters for the Marriage Compatibility Engine.

Converts verified XALEN ephemeris outputs, HoroscopeResponse objects, or raw birth inputs
into strongly-typed MarriageChartContext instances with exact Nakshatra, Pada, D1, and D9
Navamsa coordinates.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Union

from app.schemas.common import BirthInput
from app.schemas.horoscope import HoroscopeResponse, PlanetInfo, HouseInfo, AscendantInfo
from app.services.ephemeris import calculate_full_horoscope, get_sign_info, get_nakshatra_detail
from app.services.varga_engine import calculate_navamsa_from_longitude
from app.services.marriage_engine.models import (
    Gender,
    MarriagePlanet,
    MarriageHouse,
    MarriageChartContext,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    COMBUSTION_ORBS,
)
from app.services.marriage_engine.validation import (
    validate_coordinates,
    validate_timezone,
    validate_gender,
    validate_chart_context,
    MissingChartDataError,
)


def _calc_angular_separation(lon1: float, lon2: float) -> float:
    """Return smallest angular separation between two ecliptic points [0, 180]."""
    diff = abs((lon1 % 360.0) - (lon2 % 360.0))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def build_chart_context_from_horoscope_response(
    horoscope: Union[HoroscopeResponse, Dict[str, Any]],
    person_id: str,
    person_name: str,
    gender: Union[Gender, str],
    birth_date_iso: Optional[str] = None,
    birth_time_iso: Optional[str] = None,
    timezone_str: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> MarriageChartContext:
    """Transform a HoroscopeResponse (or saved horoscope calculation snapshot) into MarriageChartContext."""
    gender_enum = validate_gender(gender if isinstance(gender, str) else gender.value, Gender.MALE)

    # If dict, access keys; if object, access attributes
    def get_attr(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # 1. Ascendant
    asc_data = get_attr(horoscope, "ascendant")
    if not asc_data:
        raise MissingChartDataError(f"Missing ascendant in horoscope data for {person_name}")

    asc_deg = float(get_attr(asc_data, "degree", 0.0)) % 360.0
    asc_sign_idx = int(get_attr(asc_data, "sign_index", int(asc_deg // 30.0) + 1))
    asc_sign_name = str(get_attr(asc_data, "sign_name", SIGN_NAMES_EN.get(asc_sign_idx, "Aries")))
    asc_sign_name_ta = str(get_attr(asc_data, "sign_name_tamil", SIGN_NAMES_TA.get(asc_sign_idx, "மேஷம்")))

    # Ascendant Nakshatra and Navamsa
    asc_nav = calculate_navamsa_from_longitude(asc_deg)
    asc_nak_idx = int(asc_nav["nakshatra_index"])
    asc_nak_name = NAKSHATRA_NAMES_EN[asc_nak_idx]
    asc_nak_pada = int(asc_nav.get("pada", asc_nav.get("nakshatra_pada", 1)))
    asc_nav_sign_idx = int(asc_nav["d9_sign_index"])

    # 2. Extract metadata
    meta = get_attr(horoscope, "metadata", {})
    resolved_birth_utc = get_attr(meta, "birth_utc_iso", "")
    resolved_tz = timezone_str or get_attr(meta, "local_timezone", "Asia/Kolkata")
    coords = get_attr(meta, "coordinates", {})
    resolved_lat = latitude if latitude is not None else get_attr(coords, "latitude", 13.0827)
    resolved_lon = longitude if longitude is not None else get_attr(coords, "longitude", 80.2707)

    # 3. Parse Planets
    planets_raw = get_attr(horoscope, "planets", [])
    grahas: Dict[str, MarriagePlanet] = {}

    sun_lon = 0.0
    # First pass: find Sun's longitude for combustion evaluation
    for p in planets_raw:
        p_name = get_attr(p, "name")
        if p_name == "Sun":
            sun_lon = float(get_attr(p, "longitude", 0.0)) % 360.0
            break

    moon_planet_found: Optional[MarriagePlanet] = None

    for p in planets_raw:
        p_name = str(get_attr(p, "name"))
        b_id = int(get_attr(p, "body_id", 0))
        p_lon = float(get_attr(p, "longitude", 0.0)) % 360.0
        p_sign_idx = int(get_attr(p, "sign_index", int(p_lon // 30.0) + 1))
        p_sign_name = str(get_attr(p, "sign_name", SIGN_NAMES_EN.get(p_sign_idx, "Unknown")))
        p_sign_name_ta = str(get_attr(p, "sign_name_tamil", SIGN_NAMES_TA.get(p_sign_idx, "")))
        p_deg_in_sign = float(get_attr(p, "degree_in_sign", p_lon % 30.0))
        p_speed = float(get_attr(p, "speed_deg_per_day", 1.0))
        p_retro = bool(get_attr(p, "is_retrograde", False))

        # Navamsa & Nakshatra
        p_nav = calculate_navamsa_from_longitude(p_lon)
        p_nak_idx = int(p_nav["nakshatra_index"])
        p_nak_name = NAKSHATRA_NAMES_EN[p_nak_idx]
        p_nak_pada = int(p_nav.get("pada", p_nav.get("nakshatra_pada", 1)))
        p_nav_sign_idx = int(p_nav["d9_sign_index"])

        # House number (1-12) from Lagna sign index
        p_house = ((p_sign_idx - asc_sign_idx) % 12) + 1

        # Combustion evaluation
        is_combust = False
        if p_name not in ("Sun", "Rahu", "Ketu"):
            sep = _calc_angular_separation(sun_lon, p_lon)
            orb_key = f"{p_name}_Retro" if (p_retro and f"{p_name}_Retro" in COMBUSTION_ORBS) else p_name
            orb = COMBUSTION_ORBS.get(orb_key, COMBUSTION_ORBS.get(p_name, 0.0))
            is_combust = sep <= orb

        m_planet = MarriagePlanet(
            name=p_name,
            body_id=b_id,
            longitude=p_lon,
            sign_index=p_sign_idx,
            sign_name=p_sign_name,
            sign_name_tamil=p_sign_name_ta,
            degree_in_sign=p_deg_in_sign,
            house=p_house,
            speed_deg_per_day=p_speed,
            is_retrograde=p_retro,
            is_combust=is_combust,
            nakshatra_index=p_nak_idx,
            nakshatra_name=p_nak_name,
            nakshatra_pada=p_nak_pada,
            navamsa_sign_index=p_nav_sign_idx,
        )
        grahas[p_name] = m_planet
        if p_name == "Moon":
            moon_planet_found = m_planet

    if not moon_planet_found:
        raise MissingChartDataError(f"Missing Moon in planets list for {person_name}")

    # 4. Parse Houses
    houses_raw = get_attr(horoscope, "houses", [])
    houses: Dict[int, MarriageHouse] = {}

    if houses_raw and len(houses_raw) >= 12:
        for h in houses_raw:
            h_num = int(get_attr(h, "house_number", 1))
            h_cusp = float(get_attr(h, "cusp_degree", 0.0)) % 360.0
            h_sign_idx = int(get_attr(h, "sign_index", int(h_cusp // 30.0) + 1))
            h_sign_name = str(get_attr(h, "sign_name", SIGN_NAMES_EN.get(h_sign_idx, "Unknown")))
            h_sign_name_ta = str(get_attr(h, "sign_name_tamil", SIGN_NAMES_TA.get(h_sign_idx, "")))
            h_deg_in_sign = float(get_attr(h, "degree_in_sign", h_cusp % 30.0))
            h_lord = SIGN_LORDS.get(h_sign_idx, "Unknown")
            h_star_lord = str(get_attr(h, "star_lord", ""))

            houses[h_num] = MarriageHouse(
                house_number=h_num,
                sign_index=h_sign_idx,
                sign_name=h_sign_name,
                sign_name_tamil=h_sign_name_ta,
                cusp_degree=h_cusp,
                degree_in_sign=h_deg_in_sign,
                lord_name=h_lord,
                star_lord=h_star_lord,
            )
    else:
        # Canonical Whole-Sign fallback if houses list is omitted
        for h_num in range(1, 13):
            h_sign_idx = ((asc_sign_idx + h_num - 2) % 12) + 1
            h_cusp = float((h_sign_idx - 1) * 30.0)
            houses[h_num] = MarriageHouse(
                house_number=h_num,
                sign_index=h_sign_idx,
                sign_name=SIGN_NAMES_EN[h_sign_idx],
                sign_name_tamil=SIGN_NAMES_TA[h_sign_idx],
                cusp_degree=h_cusp,
                degree_in_sign=0.0,
                lord_name=SIGN_LORDS[h_sign_idx],
            )

    # Populate house occupants
    for p in grahas.values():
        if 1 <= p.house <= 12 and p.house in houses:
            houses[p.house].occupants.append(p.name)

    ctx = MarriageChartContext(
        person_id=person_id,
        person_name=person_name,
        gender=gender_enum,
        birth_date_iso=birth_date_iso or resolved_birth_utc[:10] if resolved_birth_utc else "1990-01-01",
        birth_time_iso=birth_time_iso or resolved_birth_utc[11:19] if resolved_birth_utc else "12:00:00",
        timezone=resolved_tz,
        latitude=resolved_lat,
        longitude=resolved_lon,
        ascendant_degree=asc_deg,
        ascendant_sign_idx=asc_sign_idx,
        ascendant_sign_name=asc_sign_name,
        ascendant_sign_name_tamil=asc_sign_name_ta,
        ascendant_nakshatra_idx=asc_nak_idx,
        ascendant_nakshatra_name=asc_nak_name,
        ascendant_nakshatra_pada=asc_nak_pada,
        ascendant_navamsa_sign_idx=asc_nav_sign_idx,
        moon_degree=moon_planet_found.longitude,
        moon_sign_idx=moon_planet_found.sign_index,
        moon_sign_name=moon_planet_found.sign_name,
        moon_sign_name_tamil=moon_planet_found.sign_name_tamil,
        moon_nakshatra_idx=moon_planet_found.nakshatra_index,
        moon_nakshatra_name=moon_planet_found.nakshatra_name,
        moon_nakshatra_pada=moon_planet_found.nakshatra_pada,
        moon_navamsa_sign_idx=moon_planet_found.navamsa_sign_index,
        grahas=grahas,
        houses=houses,
    )

    validate_chart_context(ctx)
    return ctx


def build_chart_context_from_birth_input(
    birth: BirthInput,
    person_id: str,
    person_name: str,
    gender: Union[Gender, str],
    ayanamsa_id: int = 0,
    house_system_id: int = 0,
) -> MarriageChartContext:
    """Compute astronomical chart using verified XALEN ephemeris and return MarriageChartContext."""
    lat, lon = validate_coordinates(birth.latitude, birth.longitude)
    tz_str = validate_timezone(birth.timezone)
    gender_enum = validate_gender(gender if isinstance(gender, str) else gender.value, Gender.MALE)

    horoscope_res = calculate_full_horoscope(
        birth_date=birth.birth_date,
        birth_time=birth.birth_time,
        timezone_str=tz_str,
        latitude=lat,
        longitude=lon,
        ayanamsa_id=ayanamsa_id,
        house_system_id=house_system_id,
        include_panchang=True,
        include_outer_planets=True,
        include_nabhasha=False,
        include_ashtakavarga=False,
        include_vedic_yogas=False,
        include_varga=True,
        include_doshas=False,
        gender=gender_enum.value,
    )

    return build_chart_context_from_horoscope_response(
        horoscope=horoscope_res,
        person_id=person_id,
        person_name=person_name,
        gender=gender_enum,
        birth_date_iso=birth.birth_date.isoformat(),
        birth_time_iso=birth.birth_time.isoformat(),
        timezone_str=tz_str,
        latitude=lat,
        longitude=lon,
    )
