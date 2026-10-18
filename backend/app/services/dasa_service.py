"""Vimshottari Dasa calculation service using XALEN engine."""

import logging
from datetime import date
from typing import Dict, Any, List, Optional
import xalen

logger = logging.getLogger(__name__)

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.dasa import (
    DasaPeriodNode,
    ActivePeriodPath,
    DasaResponse,
)
from app.services.timezone_utils import resolve_birth_datetime
from app.services.ephemeris import (
    compute_planetary_positions,
    compute_ascendant_and_houses,
    get_nakshatra_detail,
    AYANAMSA_NAMES,
    HOUSE_SYSTEM_NAMES,
)
from app.services.benefit_bhavas import (
    build_horoscope_planet_contexts,
    enrich_dasa_tree,
)
from app.services.dasa_calendar import (
    jd_to_gregorian_datetime,
    gregorian_to_iso,
    calculate_calendar_age,
    format_calendar_age,
    age_tuple_to_dict,
)


def _convert_node(
    raw_node: Dict[str, Any],
    birth_date: Optional[date] = None,
    utc_offset_hours: float = 0.0,
) -> DasaPeriodNode:
    """Recursively convert a raw dictionary from XALEN into a DasaPeriodNode with exact dates and age."""
    start_jd = raw_node["start_jd"]
    end_jd = raw_node["end_jd"]
    level = raw_node["level"]

    sy, sm, sd, sh, smin, ss = jd_to_gregorian_datetime(start_jd, utc_offset_hours)
    ey, em, ed, eh, emin, es = jd_to_gregorian_datetime(end_jd, utc_offset_hours)

    include_time = level in ("Sookshmadasha", "Pranadasha")
    start_date_iso = gregorian_to_iso(sy, sm, sd, sh, smin, ss, include_time=include_time)
    end_date_iso = gregorian_to_iso(ey, em, ed, eh, emin, es, include_time=include_time)

    start_age = None
    end_age = None
    start_age_dict = None
    end_age_dict = None

    if birth_date is not None:
        start_age_tuple = calculate_calendar_age(birth_date.year, birth_date.month, birth_date.day, sy, sm, sd)
        end_age_tuple = calculate_calendar_age(birth_date.year, birth_date.month, birth_date.day, ey, em, ed)
        start_age = format_calendar_age(start_age_tuple)
        end_age = format_calendar_age(end_age_tuple)
        start_age_dict = age_tuple_to_dict(start_age_tuple)
        end_age_dict = age_tuple_to_dict(end_age_tuple)

    sub_nodes = [
        _convert_node(sub, birth_date=birth_date, utc_offset_hours=utc_offset_hours)
        for sub in raw_node.get("sub_periods", [])
    ]
    return DasaPeriodNode(
        lord=raw_node["lord"],
        level=level,
        start_jd=start_jd,
        end_jd=end_jd,
        duration_days=raw_node["duration_days"],
        duration_years=raw_node["duration_years"],
        start_date_iso=start_date_iso,
        end_date_iso=end_date_iso,
        start_age=start_age,
        end_age=end_age,
        start_age_dict=start_age_dict,
        end_age_dict=end_age_dict,
        sub_periods=sub_nodes,
    )


def format_balance(years_float: float) -> str:
    """Format fractional years into Years, Months, Days."""
    total_days = years_float * 365.25
    years = int(total_days // 365.25)
    remaining_days = total_days - (years * 365.25)
    months = int(remaining_days // 30.4375)
    days = int(round(remaining_days - (months * 30.4375)))
    if days >= 30:
        months += 1
        days = 0
    if months >= 12:
        years += 1
        months = 0
    return f"{years} Years, {months} Months, {days} Days"


def find_active_period(
    tree: List[DasaPeriodNode],
    target_jd: float,
    target_date_iso: str,
    birth_date: Optional[date] = None,
    utc_offset_hours: float = 0.0,
) -> Optional[ActivePeriodPath]:
    """Find the active Dasa path down the hierarchy at a given target Julian Day."""
    if not tree:
        return None

    # Check bounds
    if target_jd < tree[0].start_jd or target_jd >= tree[-1].end_jd:
        return None

    curr_list = tree
    levels = ["mahadasha", "antardasha", "pratyantardasha", "sookshmadasha", "pranadasha"]
    found_lords: Dict[str, Optional[str]] = {lvl: None for lvl in levels}

    for lvl_name in levels:
        matched_node = None
        for node in curr_list:
            if node.start_jd <= target_jd < node.end_jd:
                matched_node = node
                break
        if matched_node is None:
            # Check edge case at exact end of last period
            if curr_list and target_jd == curr_list[-1].end_jd:
                matched_node = curr_list[-1]
            else:
                break
        found_lords[lvl_name] = matched_node.lord
        curr_list = matched_node.sub_periods
        if not curr_list:
            break

    if not found_lords["mahadasha"]:
        return None

    target_age = None
    target_age_dict = None
    if birth_date is not None:
        ty, tm, td, _, _, _ = jd_to_gregorian_datetime(target_jd, utc_offset_hours)
        target_age_tuple = calculate_calendar_age(birth_date.year, birth_date.month, birth_date.day, ty, tm, td)
        target_age = format_calendar_age(target_age_tuple)
        target_age_dict = age_tuple_to_dict(target_age_tuple)

    return ActivePeriodPath(
        mahadasha=found_lords["mahadasha"],
        antardasha=found_lords["antardasha"],
        pratyantardasha=found_lords["pratyantardasha"],
        sookshmadasha=found_lords["sookshmadasha"],
        pranadasha=found_lords["pranadasha"],
        target_jd=target_jd,
        target_date_iso=target_date_iso,
        target_age=target_age,
        target_age_dict=target_age_dict,
    )


def calculate_dasa(
    birth: BirthInput,
    depth: int = 2,
    ayanamsa_id: int = 0,
    house_system_id: int = 0,
    target_date: Optional[date] = None,
) -> DasaResponse:
    """Calculate Vimshottari Dasa tree for a birth chart with Four-Category Benefit Bhavas."""
    local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
        birth.birth_date,
        birth.birth_time,
        birth.timezone,
    )

    # Calculate sidereal Moon position
    # Body ID 1 = Moon
    moon_pos = xalen.planet_position(birth_jd, 1, True, ayanamsa_id)
    moon_lon = moon_pos["longitude"] % 360.0

    nak_detail = get_nakshatra_detail(moon_lon)

    # Compute Vimshottari Dasa tree via XALEN
    raw_tree = xalen.vimshottari_dasha(moon_lon, birth_jd, depth)
    dasa_tree = [
        _convert_node(node, birth_date=birth.birth_date, utc_offset_hours=offset_hours)
        for node in raw_tree
    ]

    # Calculate Four-Category Benefit Bhavas independently for every node in dasa_tree
    try:
        planets = compute_planetary_positions(birth_jd, ayanamsa_id, include_outer=False)
        ascendant, midheaven, houses = compute_ascendant_and_houses(
            birth_jd, birth.latitude, birth.longitude, ayanamsa_id, house_system_id
        )
        planet_contexts = build_horoscope_planet_contexts(
            planets,
            ascendant_sign_idx=ascendant.sign_index,
            cusps=[h.cusp_degree for h in houses],
            houses=houses,
        )
        enrich_dasa_tree(dasa_tree, planet_contexts)
    except Exception as exc:
        # If horoscope positions/houses cannot be calculated, leave benefit_bhavas as None (unavailable)
        logger.warning("Could not enrich Dasa tree with Benefit Bhavas: %s", exc)

    birth_dasa_lord = dasa_tree[0].lord if dasa_tree else "Unknown"
    birth_balance_years = dasa_tree[0].duration_years if dasa_tree else 0.0
    birth_balance_formatted = format_balance(birth_balance_years)

    # Resolve active period if target_date provided
    active_period = None
    if target_date:
        target_jd = xalen.julian_day(target_date.year, target_date.month, target_date.day, 12.0)
        active_period = find_active_period(
            dasa_tree,
            target_jd,
            target_date.isoformat(),
            birth_date=birth.birth_date,
            utc_offset_hours=offset_hours,
        )

    aya_name, aya_desc = AYANAMSA_NAMES.get(ayanamsa_id, (f"Custom ({ayanamsa_id})", "Sidereal mode"))
    hsys_name, _ = HOUSE_SYSTEM_NAMES.get(house_system_id, (f"Custom ({house_system_id})", ""))

    aya_deg = xalen.ayanamsa(birth_jd, ayanamsa_id)

    metadata = CalculationMetadata(
        birth_utc_iso=utc_dt.isoformat(),
        julian_day_ut1=birth_jd,
        local_timezone=tz_name,
        utc_offset_hours=offset_hours,
        coordinates={"latitude": birth.latitude, "longitude": birth.longitude},
        ayanamsa_id=ayanamsa_id,
        ayanamsa_name=aya_name,
        ayanamsa_deg=round(aya_deg, 6),
        house_system_id=house_system_id,
        house_system_name=hsys_name,
        engine="XALEN 0.6.0 (Rust)",
        notes=[
            f"Vimshottari Dasa calculated using 365.25 days/year standard cycle down to depth {depth}.",
            f"Moon sidereal longitude: {moon_lon:.6f}° in {nak_detail.name} Pada {nak_detail.pada}.",
            "Four-Category Benefit Bhavas computed for each planetary period: Star Lord Occupied | Star Lord Owned | Period Lord Occupied | Period Lord Owned.",
        ],
    )

    return DasaResponse(
        metadata=metadata,
        moon_sidereal_deg=round(moon_lon, 6),
        nakshatra=nak_detail,
        birth_dasa_lord=birth_dasa_lord,
        birth_balance_years=round(birth_balance_years, 6),
        birth_balance_formatted=birth_balance_formatted,
        dasa_tree=dasa_tree,
        active_period=active_period,
    )


def calculate_direct_dasa(
    moon_sidereal_deg: float,
    birth_jd: float,
    depth: int = 2,
    target_date: Optional[date] = None,
) -> DasaResponse:
    """Calculate Vimshottari Dasa directly from known Moon sidereal longitude and Julian Day."""
    moon_lon = moon_sidereal_deg % 360.0
    nak_detail = get_nakshatra_detail(moon_lon)

    by, bm, bd, _, _, _ = jd_to_gregorian_datetime(birth_jd, 0.0)
    direct_birth_date = date(by, bm, bd)

    raw_tree = xalen.vimshottari_dasha(moon_lon, birth_jd, depth)
    dasa_tree = [
        _convert_node(node, birth_date=direct_birth_date, utc_offset_hours=0.0)
        for node in raw_tree
    ]

    birth_dasa_lord = dasa_tree[0].lord if dasa_tree else "Unknown"
    birth_balance_years = dasa_tree[0].duration_years if dasa_tree else 0.0
    birth_balance_formatted = format_balance(birth_balance_years)

    active_period = None
    if target_date:
        target_jd = xalen.julian_day(target_date.year, target_date.month, target_date.day, 12.0)
        active_period = find_active_period(
            dasa_tree,
            target_jd,
            target_date.isoformat(),
            birth_date=direct_birth_date,
            utc_offset_hours=0.0,
        )

    metadata = CalculationMetadata(
        birth_utc_iso="",
        julian_day_ut1=birth_jd,
        local_timezone="UTC",
        utc_offset_hours=0.0,
        coordinates={"latitude": 0.0, "longitude": 0.0},
        ayanamsa_id=0,
        ayanamsa_name="Direct Moon Input",
        ayanamsa_deg=0.0,
        house_system_id=0,
        house_system_name="N/A",
        engine="XALEN 0.6.0 (Rust)",
        notes=[
            f"Direct Dasa calculation from specified Moon longitude {moon_lon:.6f}° and JD {birth_jd}."
        ],
    )

    return DasaResponse(
        metadata=metadata,
        moon_sidereal_deg=round(moon_lon, 6),
        nakshatra=nak_detail,
        birth_dasa_lord=birth_dasa_lord,
        birth_balance_years=round(birth_balance_years, 6),
        birth_balance_formatted=birth_balance_formatted,
        dasa_tree=dasa_tree,
        active_period=active_period,
    )
