"""Vimshottari Dasa calculation service supporting complete 5-level hierarchy and birth balance."""

import logging
from datetime import date
from typing import Dict, Any, List, Optional, Tuple
import xalen

logger = logging.getLogger(__name__)

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.dasa import (
    DasaPeriodNode,
    ActivePeriodPath,
    DasaResponse,
    DasaBalanceDuration,
    BirthDasaBalance,
    BenefitBhavasDetail,
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
from app.services.kp_engine.constants import (
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_YEARS,
    VIMSHOTTARI_INDEX,
)
from app.services.kp_engine.vedic import (
    STAR_SPAN_DEG,
    normalize_longitude,
    star_index,
    star_lord,
    sub_info,
    sub_sub_info,
    sub_sub_sub_info,
    sub_sub_sub_sub_info,
)

LEVEL_NAMES: List[str] = [
    "Mahadasha",
    "Antardasha",
    "Pratyantardasha",
    "Sookshmadasha",
    "Pranadasha",
]


def days_to_balance_duration(days: float) -> DasaBalanceDuration:
    """Format days into a structured DasaBalanceDuration with exact years, months, days."""
    years_float = days / 365.25
    total_days = max(days, 0.0)
    years = int(total_days // 365.25)
    remaining_days = total_days - (years * 365.25)
    months = int(remaining_days // 30.4375)
    d = int(round(remaining_days - (months * 30.4375)))
    if d >= 30:
        months += 1
        d = 0
    if months >= 12:
        years += 1
        months = 0
    formatted = f"{years} Years, {months} Months, {d} Days"
    return DasaBalanceDuration(
        years=years,
        months=months,
        days=d,
        total_days=round(total_days, 6),
        total_years=round(years_float, 8),
        formatted=formatted,
    )


def _convert_node(
    raw_node: Dict[str, Any],
    birth_date: Optional[date] = None,
    utc_offset_hours: float = 0.0,
) -> DasaPeriodNode:
    """Recursively convert a raw dictionary into a DasaPeriodNode with exact dates and age."""
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
    dur_days = raw_node.get("duration_days", end_jd - start_jd)
    dur_years = raw_node.get("duration_years", dur_days / 365.25)
    return DasaPeriodNode(
        lord=raw_node["lord"],
        level=level,
        start_jd=start_jd,
        end_jd=end_jd,
        duration_days=dur_days,
        duration_years=dur_years,
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


def generate_vimshottari_hierarchy(
    moon_lon: float,
    birth_jd: float,
    birth_date: Optional[date] = None,
    utc_offset_hours: float = 0.0,
    depth: int = 5,
) -> Tuple[List[DasaPeriodNode], BirthDasaBalance]:
    """Generate exact 5-level Vimshottari hierarchy anchored to birth Dasa balance."""
    norm_moon = normalize_longitude(moon_lon)
    s_idx = star_index(norm_moon)
    star_start = s_idx * STAR_SPAN_DEG
    star_end = star_start + STAR_SPAN_DEG
    md_lord = star_lord(norm_moon)

    full_md_days = VIMSHOTTARI_YEARS[md_lord] * 365.25
    rem_fraction = (star_end - norm_moon) / STAR_SPAN_DEG
    rem_md_days = rem_fraction * full_md_days
    elapsed_md_days = full_md_days - rem_md_days
    theo_md_start_jd = birth_jd - elapsed_md_days
    theo_md_end_jd = birth_jd + rem_md_days

    sub = sub_info(norm_moon)
    subsub = sub_sub_info(norm_moon)
    sub3 = sub_sub_sub_info(norm_moon)
    sub4 = sub_sub_sub_sub_info(norm_moon)

    rem_ad_days = (sub.end_deg - norm_moon) / STAR_SPAN_DEG * full_md_days
    rem_pd_days = (subsub.end_deg - norm_moon) / STAR_SPAN_DEG * full_md_days
    rem_sd_days = (sub3.end_deg - norm_moon) / STAR_SPAN_DEG * full_md_days
    rem_prd_days = (sub4.end_deg - norm_moon) / STAR_SPAN_DEG * full_md_days

    full_ad_days = full_md_days * (VIMSHOTTARI_YEARS[sub.lord] / 120.0)
    full_pd_days = full_ad_days * (VIMSHOTTARI_YEARS[subsub.lord] / 120.0)
    full_sd_days = full_pd_days * (VIMSHOTTARI_YEARS[sub3.lord] / 120.0)

    # Next Dasa transition calculation
    next_dasa_jd = birth_jd + rem_md_days
    ny, nm, nd, nh, nmin, ns = jd_to_gregorian_datetime(next_dasa_jd, utc_offset_hours)
    next_dasa_iso = gregorian_to_iso(ny, nm, nd, nh, nmin, ns, include_time=False)

    by, bm, bd, bh, bmin, bs = jd_to_gregorian_datetime(birth_jd, utc_offset_hours)
    birth_date_str = f"{by:04d}-{bm:02d}-{bd:02d}"
    birth_time_str = f"{bh:02d}:{bmin:02d}:{bs:02d}"

    nak_detail = get_nakshatra_detail(norm_moon)

    birth_dasa_balance = BirthDasaBalance(
        birth_date=birth_date_str,
        birth_time=birth_time_str,
        moon_sidereal_deg=round(norm_moon, 6),
        nakshatra_name=nak_detail.name,
        nakshatra_pada=nak_detail.pada,
        nakshatra_lord=nak_detail.lord,
        starting_mahadasha_lord=md_lord,
        mahadasha_full_duration=days_to_balance_duration(full_md_days),
        elapsed_duration=days_to_balance_duration(elapsed_md_days),
        remaining_balance=days_to_balance_duration(rem_md_days),
        starting_bhukti_lord=sub.lord,
        starting_bhukti_remaining=days_to_balance_duration(rem_ad_days),
        starting_antharam_lord=subsub.lord,
        starting_antharam_remaining=days_to_balance_duration(rem_pd_days),
        starting_sookshamam_lord=sub3.lord,
        starting_pranam_lord=sub4.lord,
        next_dasa_transition_date=next_dasa_iso,
        next_dasa_transition_jd=next_dasa_jd,
    )

    def create_node(
        lord: str,
        level_name: str,
        start_jd: float,
        end_jd: float,
        sub_periods: List[DasaPeriodNode],
        is_active_at_birth: bool = False,
        theo_start_jd: Optional[float] = None,
        theo_end_jd: Optional[float] = None,
    ) -> DasaPeriodNode:
        if theo_start_jd is None:
            theo_start_jd = start_jd
        if theo_end_jd is None:
            theo_end_jd = end_jd

        sy, sm, sd, sh, smin, ss = jd_to_gregorian_datetime(start_jd, utc_offset_hours)
        ey, em, ed, eh, emin, es = jd_to_gregorian_datetime(end_jd, utc_offset_hours)

        include_time = level_name in ("Sookshmadasha", "Pranadasha")
        start_date_iso = gregorian_to_iso(sy, sm, sd, sh, smin, ss, include_time=include_time)
        end_date_iso = gregorian_to_iso(ey, em, ed, eh, emin, es, include_time=include_time)

        dur_days = end_jd - start_jd
        dur_years = dur_days / 365.25

        theo_dur_days = theo_end_jd - theo_start_jd
        theo_dur_years = theo_dur_days / 365.25

        tsy, tsm, tsd, tsh, tsmin, tss = jd_to_gregorian_datetime(theo_start_jd, utc_offset_hours)
        tey, tem, ted, teh, temin, tes = jd_to_gregorian_datetime(theo_end_jd, utc_offset_hours)
        theo_start_date_iso = gregorian_to_iso(tsy, tsm, tsd, tsh, tsmin, tss, include_time=include_time)
        theo_end_date_iso = gregorian_to_iso(tey, tem, ted, teh, temin, tes, include_time=include_time)

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

        return DasaPeriodNode(
            lord=lord,
            level=level_name,
            start_jd=start_jd,
            end_jd=end_jd,
            duration_days=dur_days,
            duration_years=dur_years,
            start_date_iso=start_date_iso,
            end_date_iso=end_date_iso,
            start_age=start_age,
            end_age=end_age,
            start_age_dict=start_age_dict,
            end_age_dict=end_age_dict,
            theoretical_start_jd=theo_start_jd,
            theoretical_end_jd=theo_end_jd,
            theoretical_duration_days=theo_dur_days,
            theoretical_duration_years=theo_dur_years,
            theoretical_start_date_iso=theo_start_date_iso,
            theoretical_end_date_iso=theo_end_date_iso,
            is_active=False,
            is_active_at_birth=is_active_at_birth,
            sub_periods=sub_periods,
        )

    def build_children(
        parent_lord: str,
        parent_theo_start_jd: float,
        parent_theo_end_jd: float,
        current_level: int,
        target_depth: int,
        is_birth_chain: bool = False,
    ) -> List[DasaPeriodNode]:
        if current_level > target_depth:
            return []

        children: List[DasaPeriodNode] = []
        parent_theo_dur = parent_theo_end_jd - parent_theo_start_jd
        level_name = LEVEL_NAMES[current_level - 1]
        parent_pos = VIMSHOTTARI_INDEX[parent_lord]

        curr_theo_jd = parent_theo_start_jd
        for i in range(9):
            lord = VIMSHOTTARI_ORDER[(parent_pos + i) % 9]
            if i == 8:
                c_theo_dur = parent_theo_end_jd - curr_theo_jd
                c_theo_end_jd = parent_theo_end_jd
            else:
                c_theo_dur = parent_theo_dur * (VIMSHOTTARI_YEARS[lord] / 120.0)
                c_theo_end_jd = curr_theo_jd + c_theo_dur
            c_theo_start_jd = curr_theo_jd
            curr_theo_jd = c_theo_end_jd

            if not is_birth_chain:
                c_start_jd = c_theo_start_jd
                c_end_jd = c_theo_end_jd
                sub_ch = build_children(
                    lord,
                    c_theo_start_jd,
                    c_theo_end_jd,
                    current_level + 1,
                    target_depth,
                    is_birth_chain=False,
                )
                children.append(
                    create_node(
                        lord,
                        level_name,
                        c_start_jd,
                        c_end_jd,
                        sub_ch,
                        is_active_at_birth=False,
                        theo_start_jd=c_theo_start_jd,
                        theo_end_jd=c_theo_end_jd,
                    )
                )
            else:
                # 1. Fully completed before birth
                if c_theo_end_jd <= birth_jd + 1e-7:
                    continue

                # 2. Spans birth instant -> active at birth (clipped to birth_jd)
                if c_theo_start_jd <= birth_jd < c_theo_end_jd:
                    c_start_jd = birth_jd
                    c_end_jd = c_theo_end_jd
                    sub_ch = build_children(
                        lord,
                        c_theo_start_jd,
                        c_theo_end_jd,
                        current_level + 1,
                        target_depth,
                        is_birth_chain=True,
                    )
                    children.append(
                        create_node(
                            lord,
                            level_name,
                            c_start_jd,
                            c_end_jd,
                            sub_ch,
                            is_active_at_birth=True,
                            theo_start_jd=c_theo_start_jd,
                            theo_end_jd=c_theo_end_jd,
                        )
                    )
                else:
                    # 3. Starts after birth -> full normal duration
                    c_start_jd = c_theo_start_jd
                    c_end_jd = c_theo_end_jd
                    sub_ch = build_children(
                        lord,
                        c_theo_start_jd,
                        c_theo_end_jd,
                        current_level + 1,
                        target_depth,
                        is_birth_chain=False,
                    )
                    children.append(
                        create_node(
                            lord,
                            level_name,
                            c_start_jd,
                            c_end_jd,
                            sub_ch,
                            is_active_at_birth=False,
                            theo_start_jd=c_theo_start_jd,
                            theo_end_jd=c_theo_end_jd,
                        )
                    )

        return children

    mahadashas: List[DasaPeriodNode] = []
    curr_jd = birth_jd
    md_pos = VIMSHOTTARI_INDEX[md_lord]
    for c in range(9):
        lord = VIMSHOTTARI_ORDER[(md_pos + c) % 9]
        if c == 0:
            dur = rem_md_days
            end_jd = curr_jd + dur
            sub_ch = build_children(
                lord,
                theo_md_start_jd,
                theo_md_end_jd,
                2,
                depth,
                is_birth_chain=True,
            )
            mahadashas.append(
                create_node(
                    lord,
                    LEVEL_NAMES[0],
                    curr_jd,
                    end_jd,
                    sub_ch,
                    is_active_at_birth=True,
                    theo_start_jd=theo_md_start_jd,
                    theo_end_jd=theo_md_end_jd,
                )
            )
            curr_jd = end_jd
        else:
            full_years = VIMSHOTTARI_YEARS[lord]
            dur = full_years * 365.25
            end_jd = curr_jd + dur
            sub_ch = build_children(
                lord,
                curr_jd,
                end_jd,
                2,
                depth,
                is_birth_chain=False,
            )
            mahadashas.append(
                create_node(
                    lord,
                    LEVEL_NAMES[0],
                    curr_jd,
                    end_jd,
                    sub_ch,
                    is_active_at_birth=False,
                    theo_start_jd=curr_jd,
                    theo_end_jd=end_jd,
                )
            )
            curr_jd = end_jd

    return mahadashas, birth_dasa_balance


def mark_active_periods(tree: List[DasaPeriodNode], target_jd: float) -> None:
    """Mark is_active=True along the active period branch."""
    curr_list = tree
    while curr_list:
        matched = None
        for node in curr_list:
            if node.start_jd <= target_jd < node.end_jd:
                matched = node
                break
        if not matched and curr_list and target_jd == curr_list[-1].end_jd:
            matched = curr_list[-1]
        if matched:
            matched.is_active = True
            curr_list = matched.sub_periods
        else:
            break


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
    depth: int = 5,
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

    # Compute Vimshottari Dasa hierarchy anchored to birth balance
    dasa_tree, birth_balance = generate_vimshottari_hierarchy(
        moon_lon=moon_lon,
        birth_jd=birth_jd,
        birth_date=birth.birth_date,
        utc_offset_hours=offset_hours,
        depth=depth,
    )

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
        logger.warning("Could not enrich Dasa tree with Benefit Bhavas: %s", exc)

    birth_dasa_lord = dasa_tree[0].lord if dasa_tree else "Unknown"
    birth_balance_years = dasa_tree[0].duration_years if dasa_tree else 0.0
    birth_balance_formatted = format_balance(birth_balance_years)

    # Resolve active period if target_date provided
    active_period = None
    if target_date:
        target_jd = xalen.julian_day(target_date.year, target_date.month, target_date.day, 12.0)
        mark_active_periods(dasa_tree, target_jd)
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
        engine="XALEN 0.6.0 (Rust) + Precision Vedic Engine",
        notes=[
            f"Vimshottari Dasa calculated from exact birth balance down to depth {depth}.",
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
        birth_dasa_balance=birth_balance,
        dasa_tree=dasa_tree,
        active_period=active_period,
    )


def calculate_direct_dasa(
    moon_sidereal_deg: float,
    birth_jd: float,
    depth: int = 5,
    target_date: Optional[date] = None,
) -> DasaResponse:
    """Calculate Vimshottari Dasa directly from known Moon sidereal longitude and Julian Day."""
    moon_lon = normalize_longitude(moon_sidereal_deg)
    nak_detail = get_nakshatra_detail(moon_lon)

    by, bm, bd, _, _, _ = jd_to_gregorian_datetime(birth_jd, 0.0)
    direct_birth_date = date(by, bm, bd)

    dasa_tree, birth_balance = generate_vimshottari_hierarchy(
        moon_lon=moon_lon,
        birth_jd=birth_jd,
        birth_date=direct_birth_date,
        utc_offset_hours=0.0,
        depth=depth,
    )

    birth_dasa_lord = dasa_tree[0].lord if dasa_tree else "Unknown"
    birth_balance_years = dasa_tree[0].duration_years if dasa_tree else 0.0
    birth_balance_formatted = format_balance(birth_balance_years)

    active_period = None
    if target_date:
        target_jd = xalen.julian_day(target_date.year, target_date.month, target_date.day, 12.0)
        mark_active_periods(dasa_tree, target_jd)
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
        engine="XALEN 0.6.0 (Rust) + Precision Vedic Engine",
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
        birth_dasa_balance=birth_balance,
        dasa_tree=dasa_tree,
        active_period=active_period,
    )
