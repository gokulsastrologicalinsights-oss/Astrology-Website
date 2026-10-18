"""KP (Krishnamurti Paddhati) service integrating dedicated kpastro calculation engine."""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.kp import (
    PlanetaryKpPosition,
    KpCuspDetail,
    PlanetSignificator,
    SignificatorStrengthEntry,
    HouseSignificatorEntry,
    RulingPlanetEntry,
    RulingPlanetsDetail,
    KpDasaPeriod,
    KpDasaBalance,
    KpResponse,
    HoraryKpRequest,
    HoraryKpResponse,
    HoraryDivisionDetail,
)
import swisseph as swe
from app.services.timezone_utils import resolve_birth_datetime
from app.services.kp_engine import compute_chart, BirthInfo
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.kp_engine.horary import (
    kp_number_for_longitude,
    kp_divisions,
    compute_horary_cusps,
)
from app.services.kp_engine.vedic import sign_index, point_info
from app.services.kp_engine.dasha import (
    current_periods,
    dasha_balance,
    mahadasha_timeline,
)
from app.services.kp_engine.significators import (
    planet_significations,
    house_significations,
    cusp_sub_lords,
    ruling_planets,
)

# Traditional 9 Vedic Grahas used in KP Astrology
PLANET_BODY_IDS: Dict[str, int] = {
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

FAVORABLE_HOUSES: Dict[int, set] = {
    1: {1, 2, 3, 10, 11},
    2: {2, 6, 10, 11},
    3: {3, 5, 11},
    4: {4, 11, 12},
    5: {2, 5, 11},
    6: {6, 10, 11},
    7: {2, 7, 11},
    8: {8, 11, 2},
    9: {9, 11, 1},
    10: {2, 6, 10, 11},
    11: {1, 2, 11},
    12: {2, 6, 11, 12},
}

UNFAVORABLE_HOUSES: Dict[int, set] = {
    1: {6, 8, 12},
    2: {1, 8, 12},
    3: {2, 8, 12},
    4: {3, 8},
    5: {1, 4, 8, 12},
    6: {5, 12},
    7: {1, 6, 12},
    8: {1, 7, 12},
    9: {8, 12},
    10: {5, 9, 12},
    11: {8, 12},
    12: {8},
}


def evaluate_cuspal_promise(house: int, csl_planet: str, planet_significators: dict) -> str:
    """Evaluate KP cuspal promise based on Cuspal Sub-Lord significations."""
    sig_entries = planet_significators.get(csl_planet, [])
    signified = {s.house for s in sig_entries}
    fav = signified & FAVORABLE_HOUSES.get(house, set())
    unfav = signified & UNFAVORABLE_HOUSES.get(house, set())
    if fav and not unfav:
        return "Positive"
    elif unfav and not fav:
        return "Negative"
    elif len(fav) > len(unfav):
        return "Positive"
    elif len(unfav) > len(fav):
        return "Negative"
    return "Mixed"


def calculate_kp_chart(
    birth: BirthInput,
    ayanamsa_id: int = 1,  # Default KP Krishnamurti ayanamsa
    house_system_id: int = 2,  # Default Placidus semi-arc
) -> KpResponse:
    """Calculate complete KP natal horoscope using dedicated kpastro calculation engine."""
    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(
        birth.birth_date,
        birth.birth_time,
        birth.timezone,
    )

    # 1. Initialize BirthInfo and compute full KP chart
    birth_info = BirthInfo(
        date=local_dt.date(),
        time=local_dt.time(),
        latitude=birth.latitude,
        longitude=birth.longitude,
        tz_hours=offset_hours,
        place=getattr(birth, "birth_place", "") or "",
    )

    ayanamsa_mode = "kp" if ayanamsa_id == 1 else "lahiri" if ayanamsa_id == 0 else "kp"
    chart = compute_chart(birth_info, ayanamsa=ayanamsa_mode)

    # 2. Planetary positions (9 Grahas)
    planetary_kp_list: List[PlanetaryKpPosition] = []
    for p in chart.planets:
        body_id = PLANET_BODY_IDS.get(p.name, 0)
        s_idx = sign_index(p.longitude) + 1
        planetary_kp_list.append(
            PlanetaryKpPosition(
                planet=p.name,
                body_id=body_id,
                longitude=round(p.longitude, 6),
                sign_index=s_idx,
                sign_name=p.sign,
                sign_lord=p.sign_lord,
                star_lord=p.star_lord,
                sub_lord=p.sub_lord,
                sub_sub_lord=p.sub_sub_lord,
                kp_number=kp_number_for_longitude(p.longitude),
            )
        )

    # 3. 12 Sidereal Placidus Cusps and CSL Analysis
    cuspal_list: List[KpCuspDetail] = []
    for c in chart.cusps:
        s_idx = sign_index(c.longitude) + 1
        promise = evaluate_cuspal_promise(c.house, c.sub_lord, chart.planet_significators)
        cuspal_list.append(
            KpCuspDetail(
                house=c.house,
                cusp_degree=round(c.longitude, 6),
                sign_index=s_idx,
                sign_name=c.sign,
                sign_lord=c.sign_lord,
                star_lord=c.star_lord,
                sub_lord=c.sub_lord,
                sub_sub_lord=c.sub_sub_lord,
                promise=promise,
            )
        )

    # 4. Planetary Significators (Grah Nirdeshan: 4-level strength)
    significators_list: List[PlanetSignificator] = []
    for p in chart.planets:
        p_name = p.name
        sigs = chart.planet_significators.get(p_name, [])
        signified_houses = sorted(list({s.house for s in sigs}))

        strength_entries: List[SignificatorStrengthEntry] = []
        for s in sigs:
            if s.by_star_lord:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="StarLord"))
        for s in sigs:
            if s.by_occupation:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="Occupant"))
        for s in sigs:
            if s.by_sign_lordship:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="Owner"))

        significators_list.append(
            PlanetSignificator(
                planet=p_name,
                signified_houses=signified_houses,
                strength_order=strength_entries,
            )
        )

    # 5. House Significators (Bhaav Nirdeshan: 4 tiers A, B, C, D)
    house_significators_list: List[HouseSignificatorEntry] = []
    for i, c in enumerate(chart.cusps):
        h = c.house
        tier_entries = chart.house_significators[i] if i < len(chart.house_significators) else []
        level_a = [p for p, tier in tier_entries if tier == 2]
        level_b = [p for p, tier in tier_entries if tier == 1]
        level_c = [p for p, tier in tier_entries if tier == 4]
        level_d = [p for p, tier in tier_entries if tier == 3]

        all_sigs: List[str] = []
        for p in level_a + level_b + level_c + level_d:
            if p not in all_sigs:
                all_sigs.append(p)

        house_significators_list.append(
            HouseSignificatorEntry(
                house=h,
                sign_name=c.sign,
                sign_lord=c.sign_lord,
                star_lord=c.star_lord,
                sub_lord=c.sub_lord,
                sub_sub_lord=c.sub_sub_lord,
                level_a=level_a,
                level_b=level_b,
                level_c=level_c,
                level_d=level_d,
                all_significators=all_sigs,
            )
        )

    # 6. Ruling Planets (RPs)
    asc_info = point_info(chart.ascendant)
    moon_lon = chart.planet_lon.get("Moon", 0.0)
    moon_info = point_info(moon_lon)
    ruling_details = [RulingPlanetEntry(role=rp.source, planet=rp.planet) for rp in chart.ruling]
    ruling_list = [rp.planet for rp in chart.ruling]
    day_lord = next((rp.planet for rp in chart.ruling if "day lord" in rp.source.lower()), "")

    ruling_planets = RulingPlanetsDetail(
        day_lord=day_lord,
        ascendant_sign_lord=asc_info.sign_lord,
        ascendant_star_lord=asc_info.star_lord,
        ascendant_sub_lord=asc_info.sub_lord,
        moon_sign_lord=moon_info.sign_lord,
        moon_star_lord=moon_info.star_lord,
        moon_sub_lord=moon_info.sub_lord,
        ruling_planets_list=ruling_list,
        details=ruling_details,
    )

    # 7. 5-Level Vimshottari Dasa Hierarchy
    level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshmadasha", "Pranadasha"]
    vedic_names = ["Dasa", "Bhukti", "Andharam", "Soochamam", "Pranam"]

    cur_periods_list: List[KpDasaPeriod] = []
    active_dict = current_periods(moon_lon, local_dt, local_dt, depth=5)
    for lvl in range(1, 6):
        if lvl in active_dict:
            p = active_dict[lvl]
            s_dt = local_dt + timedelta(days=p.start_days)
            e_dt = local_dt + timedelta(days=p.end_days)
            cur_periods_list.append(
                KpDasaPeriod(
                    level=lvl,
                    level_name=level_names[lvl - 1],
                    vedic_name=vedic_names[lvl - 1],
                    lord=p.lord,
                    start_date=s_dt.isoformat(),
                    end_date=e_dt.isoformat(),
                    duration_days=round(p.duration_days, 4),
                )
            )

    md_list: List[KpDasaPeriod] = []
    for p in chart.mahadashas:
        s_dt = local_dt + timedelta(days=p.start_days)
        e_dt = local_dt + timedelta(days=p.end_days)
        md_list.append(
            KpDasaPeriod(
                level=1,
                level_name="Mahadasha",
                vedic_name="Dasa",
                lord=p.lord,
                start_date=s_dt.isoformat(),
                end_date=e_dt.isoformat(),
                duration_days=round(p.duration_days, 4),
            )
        )

    dasa_hierarchy = KpDasaBalance(
        birth_epoch=local_dt.isoformat(),
        mahadasha_lord=chart.balance.mahadasha_lord,
        mahadasha_balance_years=round(chart.balance.mahadasha_years, 6),
        mahadasha_balance_days=round(chart.balance.mahadasha_days, 4),
        antardasha_lord=chart.balance.active_ad_lord,
        antardasha_balance_days=round(chart.balance.active_ad_days, 4),
        pratyantardasha_lord=chart.balance.active_pd_lord,
        pratyantardasha_balance_days=round(chart.balance.active_pd_days, 4),
        sookshmadasha_lord=chart.balance.active_sd_lord,
        sookshmadasha_balance_days=round(chart.balance.active_sd_days, 4),
        pranadasha_lord=chart.balance.active_prd_lord,
        pranadasha_balance_days=round(chart.balance.active_prd_days, 4),
        current_periods=cur_periods_list,
        mahadashas=md_list,
    )

    metadata = CalculationMetadata(
        birth_utc_iso=utc_dt.isoformat(),
        julian_day_ut1=chart.jd_ut,
        local_timezone=tz_name,
        utc_offset_hours=offset_hours,
        coordinates={"latitude": birth.latitude, "longitude": birth.longitude},
        ayanamsa_id=ayanamsa_id,
        ayanamsa_name="KP" if ayanamsa_id == 1 else "Lahiri",
        ayanamsa_deg=round(chart.ayanamsa, 6),
        house_system_id=house_system_id,
        house_system_name="Placidus",
        engine="kpastro 0.3.3 (Swiss Ephemeris / Krishnamurti Paddhati)",
        notes=[
            f"KP 249 sub-division table and significators computed with KP ayanamsa ({chart.ayanamsa:.4f}°) and Placidus house cusps.",
            "Sub-sub-lord and 5-level Dasa hierarchy (Dasa, Bhukti, Andharam, Soochamam, Pranam) follow validated Vimshottari 120-year proportions.",
            "Bhaav Nirdeshan 4-fold significator tiers (A, B, C, D) and Cuspal Sub-Lord arbiter analysis computed.",
            "Ruling planets calculated from ascendant, Moon, and weekday lords.",
        ],
    )

    return KpResponse(
        metadata=metadata,
        planetary_positions=planetary_kp_list,
        cuspal_analysis=cuspal_list,
        significators=significators_list,
        house_significators=house_significators_list,
        ruling_planets=ruling_planets,
        dasa_hierarchy=dasa_hierarchy,
    )


def calculate_horary_chart(request: HoraryKpRequest) -> HoraryKpResponse:
    """Calculate authentic KP Horary (Prashna 1-249) chart.

    In authentic Krishnamurti Paddhati Horary:
    - The querent's number (1-249) fixes Cusp 1 to the exact division midpoint.
    - The 12 Placidus cusps are computed by inverting the ARMC with Swiss Ephemeris.
    - All planetary positions, Moon, and Vimshottari Dasa are computed at the exact question-moment timestamp.
    - 4-tier significators (A, B, C, D) and Cuspal Sub-Lord arbiter analysis are evaluated.
    - Ruling planets are derived from the question moment (Day Lord, Moon Sign/Star/Sub, Asc Sign/Star/Sub).
    """
    if not (1 <= request.horary_number <= 249):
        raise ValueError(f"Horary number must be between 1 and 249, got {request.horary_number}")

    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(
        request.question_date,
        request.question_time,
        request.timezone,
    )

    # 1. Retrieve the KP 1-249 division details
    divisions = kp_divisions()
    div = divisions[request.horary_number - 1]
    mid_info = point_info(div.mid_deg)
    horary_division = HoraryDivisionDetail(
        number=div.number,
        start_degree=round(div.start_deg, 6),
        end_degree=round(div.end_deg, 6),
        mid_degree=round(div.mid_deg, 6),
        sign=div.sign,
        sign_lord=div.sign_lord,
        star=div.star,
        star_lord=div.star_lord,
        sub_lord=div.sub_lord,
        sub_sub_lord=mid_info.sub_sub_lord,
        pada=mid_info.pada,
    )

    # 2. Ephemeris setup and True Obliquity
    ayanamsa_mode = "kp" if request.ayanamsa == 1 else "lahiri" if request.ayanamsa == 0 else "kp"
    eph = SwissEphemeris(ayanamsa=ayanamsa_mode)
    ayan = eph.ayanamsa(jd)
    arr, _ = swe.calc_ut(jd, swe.ECL_NUT)
    eps = arr[0]

    # 3. Compute 12 Placidus cusps pinned to the Horary Ascendant midpoint
    cusps, asc, mc = compute_horary_cusps(div.mid_deg, request.latitude, ayan, eps)

    # 4. Planetary positions at question moment
    sider = eph.sidereal_positions(jd)
    positions = {name: lon for name, (lon, _) in sider.items()}

    planetary_kp_list: List[PlanetaryKpPosition] = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        lon, speed = sider[name]
        body_id = PLANET_BODY_IDS.get(name, 0)
        s_idx = sign_index(lon) + 1
        p_info = point_info(lon)
        planetary_kp_list.append(
            PlanetaryKpPosition(
                planet=name,
                body_id=body_id,
                longitude=round(lon, 6),
                sign_index=s_idx,
                sign_name=p_info.sign,
                sign_lord=p_info.sign_lord,
                star_lord=p_info.star_lord,
                sub_lord=p_info.sub_lord,
                sub_sub_lord=p_info.sub_sub_lord,
                kp_number=kp_number_for_longitude(lon),
            )
        )

    # 5. Significator mappings (planet and house)
    planet_sigs_raw = planet_significations(positions, cusps)
    house_sigs_raw = house_significations(positions, cusps)

    # 6. 12 House Cusps and Cuspal Sub-Lord analysis
    cuspal_list: List[KpCuspDetail] = []
    for i, c_lon in enumerate(cusps):
        h = i + 1
        c_info = point_info(c_lon)
        s_idx = sign_index(c_lon) + 1
        promise = evaluate_cuspal_promise(h, c_info.sub_lord, planet_sigs_raw)
        cuspal_list.append(
            KpCuspDetail(
                house=h,
                cusp_degree=round(c_lon, 6),
                sign_index=s_idx,
                sign_name=c_info.sign,
                sign_lord=c_info.sign_lord,
                star_lord=c_info.star_lord,
                sub_lord=c_info.sub_lord,
                sub_sub_lord=c_info.sub_sub_lord,
                promise=promise,
            )
        )

    # 7. Planetary Significators (4-level strength)
    significators_list: List[PlanetSignificator] = []
    for p_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        sigs = planet_sigs_raw.get(p_name, [])
        signified_houses = sorted(list({s.house for s in sigs}))

        strength_entries: List[SignificatorStrengthEntry] = []
        for s in sigs:
            if s.by_star_lord:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="StarLord"))
        for s in sigs:
            if s.by_occupation:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="Occupant"))
        for s in sigs:
            if s.by_sign_lordship:
                strength_entries.append(SignificatorStrengthEntry(house=s.house, type="Owner"))

        significators_list.append(
            PlanetSignificator(
                planet=p_name,
                signified_houses=signified_houses,
                strength_order=strength_entries,
            )
        )

    # 8. House Significators (4 tiers A, B, C, D)
    house_significators_list: List[HouseSignificatorEntry] = []
    for i, c_lon in enumerate(cusps):
        h = i + 1
        c_info = point_info(c_lon)
        tier_entries = house_sigs_raw[i] if i < len(house_sigs_raw) else []
        level_a = [p for p, tier in tier_entries if tier == 2]
        level_b = [p for p, tier in tier_entries if tier == 1]
        level_c = [p for p, tier in tier_entries if tier == 4]
        level_d = [p for p, tier in tier_entries if tier == 3]

        all_sigs: List[str] = []
        for p in level_a + level_b + level_c + level_d:
            if p not in all_sigs:
                all_sigs.append(p)

        house_significators_list.append(
            HouseSignificatorEntry(
                house=h,
                sign_name=c_info.sign,
                sign_lord=c_info.sign_lord,
                star_lord=c_info.star_lord,
                sub_lord=c_info.sub_lord,
                sub_sub_lord=c_info.sub_sub_lord,
                level_a=level_a,
                level_b=level_b,
                level_c=level_c,
                level_d=level_d,
                all_significators=all_sigs,
            )
        )

    # 9. Ruling Planets at Question Moment
    asc_info = point_info(asc)
    moon_lon = positions.get("Moon", 0.0)
    moon_info = point_info(moon_lon)
    ruling_raw = ruling_planets(asc, moon_lon, local_dt.weekday())
    ruling_details = [RulingPlanetEntry(role=rp.source, planet=rp.planet) for rp in ruling_raw]
    ruling_list = [rp.planet for rp in ruling_raw]
    day_lord = next((rp.planet for rp in ruling_raw if "day lord" in rp.source.lower()), "")

    ruling_planets_obj = RulingPlanetsDetail(
        day_lord=day_lord,
        ascendant_sign_lord=asc_info.sign_lord,
        ascendant_star_lord=asc_info.star_lord,
        ascendant_sub_lord=asc_info.sub_lord,
        moon_sign_lord=moon_info.sign_lord,
        moon_star_lord=moon_info.star_lord,
        moon_sub_lord=moon_info.sub_lord,
        ruling_planets_list=ruling_list,
        details=ruling_details,
    )

    # 10. 5-Level Vimshottari Dasa Hierarchy from Moon's longitude
    level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshmadasha", "Pranadasha"]
    vedic_names = ["Dasa", "Bhukti", "Andharam", "Soochamam", "Pranam"]

    cur_periods_list: List[KpDasaPeriod] = []
    active_dict = current_periods(moon_lon, local_dt, local_dt, depth=5)
    for lvl in range(1, 6):
        if lvl in active_dict:
            p = active_dict[lvl]
            s_dt = local_dt + timedelta(days=p.start_days)
            e_dt = local_dt + timedelta(days=p.end_days)
            cur_periods_list.append(
                KpDasaPeriod(
                    level=lvl,
                    level_name=level_names[lvl - 1],
                    vedic_name=vedic_names[lvl - 1],
                    lord=p.lord,
                    start_date=s_dt.isoformat(),
                    end_date=e_dt.isoformat(),
                    duration_days=round(p.duration_days, 4),
                )
            )

    balance = dasha_balance(moon_lon)
    mds = mahadasha_timeline(moon_lon)
    md_list: List[KpDasaPeriod] = []
    for p in mds:
        s_dt = local_dt + timedelta(days=p.start_days)
        e_dt = local_dt + timedelta(days=p.end_days)
        md_list.append(
            KpDasaPeriod(
                level=1,
                level_name="Mahadasha",
                vedic_name="Dasa",
                lord=p.lord,
                start_date=s_dt.isoformat(),
                end_date=e_dt.isoformat(),
                duration_days=round(p.duration_days, 4),
            )
        )

    dasa_hierarchy = KpDasaBalance(
        birth_epoch=local_dt.isoformat(),
        mahadasha_lord=balance.mahadasha_lord,
        mahadasha_balance_years=round(balance.mahadasha_years, 6),
        mahadasha_balance_days=round(balance.mahadasha_days, 4),
        antardasha_lord=balance.active_ad_lord,
        antardasha_balance_days=round(balance.active_ad_days, 4),
        pratyantardasha_lord=balance.active_pd_lord,
        pratyantardasha_balance_days=round(balance.active_pd_days, 4),
        sookshmadasha_lord=balance.active_sd_lord,
        sookshmadasha_balance_days=round(balance.active_sd_days, 4),
        pranadasha_lord=balance.active_prd_lord,
        pranadasha_balance_days=round(balance.active_prd_days, 4),
        current_periods=cur_periods_list,
        mahadashas=md_list,
    )

    metadata = CalculationMetadata(
        birth_utc_iso=utc_dt.isoformat(),
        julian_day_ut1=jd,
        local_timezone=tz_name,
        utc_offset_hours=offset_hours,
        coordinates={"latitude": request.latitude, "longitude": request.longitude},
        ayanamsa_id=request.ayanamsa,
        ayanamsa_name="KP" if request.ayanamsa == 1 else "Lahiri",
        ayanamsa_deg=round(ayan, 6),
        house_system_id=request.house_system,
        house_system_name="Placidus",
        engine="kpastro 0.3.3 (Swiss Ephemeris / Krishnamurti Paddhati Horary)",
        notes=[
            f"KP Horary Number #{request.horary_number} fixed to midpoint {horary_division.mid_degree:.4f}° ({horary_division.sign} / {horary_division.star_lord} / {horary_division.sub_lord}).",
            "12 Placidus cusps derived from Swiss Ephemeris ARMC inversion with micro-arcsecond convergence.",
            "Planetary positions and Vimshottari Dasa calculated for exact question moment.",
            "Bhaav Nirdeshan 4-fold significator tiers (A, B, C, D) and Cuspal Sub-Lord arbiter analysis computed.",
            "Ruling planets calculated from ascendant, Moon, and weekday lords at question time.",
        ],
    )

    return HoraryKpResponse(
        metadata=metadata,
        horary_number=request.horary_number,
        horary_division=horary_division,
        question_text=request.question_text,
        question_datetime=local_dt.isoformat(),
        location_name=request.location_name,
        ascendant_degree=round(asc, 6),
        planetary_positions=planetary_kp_list,
        cuspal_analysis=cuspal_list,
        significators=significators_list,
        house_significators=house_significators_list,
        ruling_planets=ruling_planets_obj,
        dasa_hierarchy=dasa_hierarchy,
    )

