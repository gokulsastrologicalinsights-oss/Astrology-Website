"""Ephemeris service integrating XALEN astronomical engine with Vedic data models."""

from typing import Dict, Any, List, Tuple
import xalen
import xalen.swe as xswe
from app.schemas.horoscope import (
    PlanetInfo,
    HouseInfo,
    AscendantInfo,
    NakshatraDetail,
    PanchangInfo,
    TithiInfo,
    YogaInfo,
    HoroscopeResponse,
)


ZODIAC_SIGNS: Dict[int, Tuple[str, str]] = {
    1: ("Aries", "மேஷம்"),
    2: ("Taurus", "ரிஷபம்"),
    3: ("Gemini", "மிதுனம்"),
    4: ("Cancer", "கடகம்"),
    5: ("Leo", "சிம்மம்"),
    6: ("Virgo", "கன்னி"),
    7: ("Libra", "துலாம்"),
    8: ("Scorpio", "விருச்சிகம்"),
    9: ("Sagittarius", "தனுசு"),
    10: ("Capricorn", "மகரம்"),
    11: ("Aquarius", "கும்பம்"),
    12: ("Pisces", "மீனம்"),
}

BODIES_CONFIG = [
    ("Sun", 0),
    ("Moon", 1),
    ("Mars", 4),
    ("Mercury", 2),
    ("Jupiter", 5),
    ("Venus", 3),
    ("Saturn", 6),
    ("Rahu", 9),
    ("Ketu", 13),
    ("Uranus", 7),
    ("Neptune", 8),
    ("Pluto", 11),
]

AYANAMSA_NAMES = {
    0: ("Lahiri", "Chitrapaksha Lahiri — Standard Vedic ayanamsa defined by Indian Calendar Reform Committee"),
    1: ("KP", "Krishnamurti Paddhati — Standard Krishnamurti ayanamsa for KP sub-lord astrology"),
    2: ("Raman", "Dr. B.V. Raman ayanamsa"),
    3: ("Fagan-Bradley", "Western Sidereal Fagan-Bradley system"),
    4: ("True Chitra", "Astronomically anchored to Spica (Alpha Virginis) at 180°"),
    5: ("True Revati", "Astronomically anchored to Zeta Piscium at 359° 50'"),
    6: ("Surya Siddhanta", "Traditional Surya Siddhanta mean ayanamsa"),
    7: ("Yukteswar", "Sri Yukteswar Holy Science epoch ayanamsa"),
    11: ("Pushya Paksha", "P.V.R. Narasimha Rao Pushya-paksha ayanamsa"),
}

HOUSE_SYSTEM_NAMES = {
    0: ("WholeSign", "Whole Sign (Rashi-Bhava) — One sign per house, standard Vedic"),
    1: ("Equal", "Equal House from Ascendant degree"),
    2: ("Placidus", "Placidus semi-arc system — Standard KP system and Western classical"),
    3: ("Koch", "Koch / GOH birthplace semi-arc system"),
    5: ("Regiomontanus", "Regiomontanus equatorial house system"),
    10: ("Sripati", "Sripati / Porphyry unequal bhava system common in North India"),
}


def get_sign_info(longitude_deg: float) -> Tuple[int, str, str, float]:
    """Return (sign_index 1-12, sign_name_en, sign_name_ta, degree_in_sign 0-30)."""
    norm = longitude_deg % 360.0
    sign_idx = int(norm // 30.0) + 1
    deg_in_sign = norm % 30.0
    name_en, name_ta = ZODIAC_SIGNS[sign_idx]
    return sign_idx, name_en, name_ta, deg_in_sign


def get_nakshatra_detail(sidereal_lon: float) -> NakshatraDetail:
    """Query XALEN's nakshatra function and construct NakshatraDetail."""
    nak_raw = xalen.nakshatra(sidereal_lon)
    return NakshatraDetail(
        name=nak_raw["name"],
        index=int(nak_raw["index"]),
        pada=int(nak_raw["pada"]),
        lord=nak_raw["lord"],
        deity=nak_raw["deity"],
    )


def compute_planetary_positions(
    jd: float,
    ayanamsa_id: int,
    include_outer: bool = True,
) -> List[PlanetInfo]:
    """Compute apparent geocentric sidereal planetary positions, speeds, retrogrades, and nakshatras."""
    planets: List[PlanetInfo] = []
    bodies_to_calc = BODIES_CONFIG if include_outer else BODIES_CONFIG[:9]

    for name, body_id in bodies_to_calc:
        # Full 6-tuple state + retrograde from XALEN
        pos = xalen.planet_position(jd, body_id, True, ayanamsa_id)
        lon = pos["longitude"]
        sign_idx, sign_name, sign_tamil, deg_in_sign = get_sign_info(lon)
        nak_detail = get_nakshatra_detail(lon)

        planets.append(
            PlanetInfo(
                name=name,
                body_id=body_id,
                longitude=lon,
                latitude=pos["latitude"],
                distance_au=pos["distance"],
                speed_deg_per_day=pos["lon_speed"],
                is_retrograde=pos["is_retrograde"],
                sign_index=sign_idx,
                sign_name=sign_name,
                sign_name_tamil=sign_tamil,
                degree_in_sign=deg_in_sign,
                nakshatra=nak_detail,
            )
        )

    return planets


def compute_ascendant_and_houses(
    jd: float,
    lat: float,
    lon: float,
    ayanamsa_id: int,
    house_system_id: int,
) -> Tuple[AscendantInfo, AscendantInfo, List[HouseInfo]]:
    """Compute sidereal Ascendant, MC, and 12 house cusps."""
    # Use xalen.swe drop-in for sub-tenth arcsecond true-equinox Placidus/equal houses
    aya_val = xalen.ayanamsa(jd, ayanamsa_id)

    # Set sidereal mode in xswe
    xswe_ayanamsa_map = {
        0: xswe.SIDM_LAHIRI,
        1: xswe.SIDM_KRISHNAMURTI,
        2: xswe.SIDM_RAMAN,
        3: xswe.SIDM_FAGAN_BRADLEY,
        4: xswe.SIDM_TRUE_CITRA,
        5: xswe.SIDM_TRUE_REVATI,
        7: xswe.SIDM_YUKTESWAR,
    }
    if ayanamsa_id in xswe_ayanamsa_map:
        xswe.set_sid_mode(xswe_ayanamsa_map[ayanamsa_id], 0, 0)
    else:
        xswe.set_sid_mode(xswe.SIDM_LAHIRI, 0, 0)

    # Map house system to char code
    hsys_code = b"P"  # Placidus
    if house_system_id == 0:
        hsys_code = b"W"  # Whole Sign
    elif house_system_id == 1:
        hsys_code = b"E"  # Equal
    elif house_system_id == 3:
        hsys_code = b"K"  # Koch
    elif house_system_id == 5:
        hsys_code = b"R"  # Regiomontanus
    elif house_system_id == 10:
        hsys_code = b"O"  # Porphyry (Sripati base in Swiss Ephemeris)

    if ayanamsa_id in xswe_ayanamsa_map:
        cusps_raw, ascmc_raw = xswe.houses_ex(jd, lat, lon, hsys_code, xswe.FLG_SIDEREAL)
    else:
        # Custom ayanamsas: compute tropical houses and apply exact XALEN ayanamsa offset
        cusps_trop, ascmc_trop = xswe.houses_ex(jd, lat, lon, hsys_code, 0)
        cusps_raw = [(c - aya_val) % 360.0 for c in cusps_trop]
        ascmc_raw = [(a - aya_val) % 360.0 for a in ascmc_trop]

    # Ascendant
    asc_deg = ascmc_raw[0] % 360.0
    asc_sign_idx, asc_sign, asc_tamil, asc_in_sign = get_sign_info(asc_deg)
    asc_nak = get_nakshatra_detail(asc_deg)
    ascendant = AscendantInfo(
        degree=asc_deg,
        sign_index=asc_sign_idx,
        sign_name=asc_sign,
        sign_name_tamil=asc_tamil,
        degree_in_sign=asc_in_sign,
        nakshatra=asc_nak,
    )

    if house_system_id == 0:
        # Canonical Vedic Sidereal Whole Sign (Rashi Bhava):
        # House 1 cusp begins at 0° of the Ascendant's sidereal sign: (asc_sign_idx - 1) * 30.0
        # Subsequent houses advance by 30° per sign, strictly aligning with sidereal rashi boundaries.
        cusps_raw = [float(((asc_sign_idx - 1 + (h - 1)) % 12) * 30.0) for h in range(1, 13)]

    # Midheaven (MC)
    mc_deg = ascmc_raw[1] % 360.0
    mc_sign_idx, mc_sign, mc_tamil, mc_in_sign = get_sign_info(mc_deg)
    mc_nak = get_nakshatra_detail(mc_deg)
    midheaven = AscendantInfo(
        degree=mc_deg,
        sign_index=mc_sign_idx,
        sign_name=mc_sign,
        sign_name_tamil=mc_tamil,
        degree_in_sign=mc_in_sign,
        nakshatra=mc_nak,
    )

    # 12 Houses
    houses: List[HouseInfo] = []
    for h_num in range(1, 13):
        cusp_deg = cusps_raw[h_num - 1] % 360.0
        h_sign_idx, h_sign, h_tamil, h_in_sign = get_sign_info(cusp_deg)
        h_nak = get_nakshatra_detail(cusp_deg)
        houses.append(
            HouseInfo(
                house_number=h_num,
                cusp_degree=cusp_deg,
                sign_index=h_sign_idx,
                sign_name=h_sign,
                sign_name_tamil=h_tamil,
                degree_in_sign=h_in_sign,
                nakshatra=h_nak.name,
                pada=h_nak.pada,
                star_lord=h_nak.lord,
            )
        )

    return ascendant, midheaven, houses


def compute_birth_panchang(jd: float, ayanamsa_id: int) -> PanchangInfo:
    """Compute the five limbs of Panchang at the given Julian Day."""
    pan = xalen.panchang(jd, ayanamsa_id)
    tithi_raw = pan["tithi"]
    yoga_raw = pan["yoga"]

    return PanchangInfo(
        tithi=TithiInfo(
            number=int(tithi_raw["number"]),
            name=tithi_raw["name"],
            paksha=tithi_raw["paksha"],
        ),
        nakshatra=pan["nakshatra"],
        yoga=YogaInfo(
            number=int(yoga_raw["number"]),
            name=yoga_raw["name"],
        ),
        karana=pan["karana"],
        vara=pan["vara"],
    )


def calculate_full_horoscope(
    birth_date,
    birth_time,
    timezone_str: str,
    latitude: float,
    longitude: float,
    ayanamsa_id: int = 0,
    house_system_id: int = 2,
    include_panchang: bool = True,
    include_outer_planets: bool = True,
    include_nabhasha: bool = True,
    include_ashtakavarga: bool = True,
    include_vedic_yogas: bool = True,
    include_varga: bool = True,
    gender: str = "male",
) -> HoroscopeResponse:
    """Calculate full horoscope including planetary positions, houses, panchang, Nabhasha Yogas, Ashtakavarga, and Vedic Yogas."""
    from app.services.timezone_utils import resolve_birth_datetime
    from app.schemas.common import CalculationMetadata
    from app.services.nabhasha_engine import detect_nabhasha_yogas
    from app.services.ashtakavarga_engine import calculate_ashtakavarga
    from app.services.yoga_engine import calculate_vedic_yogas
    from app.services.varga_engine import calculate_varga_d1_d9

    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(
        birth_date,
        birth_time,
        timezone_str,
    )

    ascendant, midheaven, houses = compute_ascendant_and_houses(
        jd=jd,
        lat=latitude,
        lon=longitude,
        ayanamsa_id=ayanamsa_id,
        house_system_id=house_system_id,
    )

    planets = compute_planetary_positions(
        jd=jd,
        ayanamsa_id=ayanamsa_id,
        include_outer=include_outer_planets,
    )

    panchang = compute_birth_panchang(jd, ayanamsa_id) if include_panchang else None

    # Classical Vedic Extensions
    nabhasha_yogas = detect_nabhasha_yogas(planets, ascendant.sign_index) if include_nabhasha else None
    ashtakavarga = calculate_ashtakavarga(planets, ascendant.sign_index) if include_ashtakavarga else None
    vedic_yogas = calculate_vedic_yogas(
        planets=planets,
        ascendant_sign_idx=ascendant.sign_index,
        houses=houses,
        gender=gender,
    ) if include_vedic_yogas else None

    aya_name, aya_desc = AYANAMSA_NAMES.get(ayanamsa_id, (f"Custom ({ayanamsa_id})", "Sidereal mode"))
    hsys_name, hsys_desc = HOUSE_SYSTEM_NAMES.get(house_system_id, (f"Custom ({house_system_id})", "House system"))
    aya_val = xalen.ayanamsa(jd, ayanamsa_id)

    metadata = CalculationMetadata(
        birth_utc_iso=utc_dt.isoformat(),
        julian_day_ut1=jd,
        local_timezone=tz_name,
        utc_offset_hours=offset_hours,
        coordinates={"latitude": latitude, "longitude": longitude},
        ayanamsa_id=ayanamsa_id,
        ayanamsa_name=aya_name,
        ayanamsa_deg=round(aya_val, 6),
        house_system_id=house_system_id,
        house_system_name=hsys_name,
        engine="XALEN 0.6.0 (Rust)",
        notes=[
            f"Calculated with {aya_name} ayanamsa ({aya_val:.4f}°) and {hsys_name} house cusps.",
            "All coordinates geocentric apparent sidereal; houses computed via true obliquity.",
        ],
    )

    varga_d1_d9 = calculate_varga_d1_d9(
        planets=planets,
        ascendant=ascendant,
        metadata=metadata,
    ) if include_varga else None

    return HoroscopeResponse(
        metadata=metadata,
        ascendant=ascendant,
        midheaven=midheaven,
        planets=planets,
        houses=houses,
        panchang=panchang,
        nabhasha_yogas=nabhasha_yogas,
        ashtakavarga=ashtakavarga,
        vedic_yogas=vedic_yogas,
        varga_d1_d9=varga_d1_d9,
    )

