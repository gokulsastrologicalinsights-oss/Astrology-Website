"""Dedicated Varga (Divisional Charts) Engine for D1 Rasi and D9 Navamsa.

Mathematical Specification:
1. One zodiac circle = 360° = 1,296,000 arcseconds = 1,296,000,000 milli-arcseconds (mas).
2. Each Rasi (sign) = 30° = 108,000,000 mas.
3. Each Nakshatra = 13°20' = 48,000,000 mas.
4. Each Pada / Navamsa division = 3°20' = 12,000,000 mas.
5. 108 Navamsas in the zodiac = 9 full cycles of 12 zodiac signs starting from Aries (Mesha).
6. Integer milli-arcsecond arithmetic is used throughout to guarantee exact boundary resolution
   and prevent IEEE 754 floating-point truncation errors (e.g., 23°20'00" evaluating to 6.999999999).

Classical References:
- Brihat Parasara Hora Shastra (BPHS), Chapter 6: Varga Chakra (Navamsha starting from movable/fixed/dual signs).
- Jataka Parijata, Chapter 1, Sloka 58 & Vidyamadhaveeyam: Classical 24 Pushkara Navamsas.
"""

from typing import Dict, Any, List, Tuple, Optional
from app.schemas.common import CalculationMetadata
from app.schemas.varga import (
    VargaPlanetPosition,
    VargaAscendantPosition,
    VargaChartSummary,
    VargaD1D9Response,
)

# Canonical 12 Zodiac Signs
SIGN_NAMES_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

SIGN_NAMES_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

# Classical Sign Lords (Graha Adhipati)
SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# 27 Classical Nakshatras
NAKSHATRA_NAMES: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# 9 Vimshottari Lords cycled across 27 Nakshatras
VIMSHOTTARI_LORDS: List[str] = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

# Classical 24 Pushkara Navamsas (Jataka Parijata Ch. 1, Sloka 58)
# Key = D1 Sign index (1-12); Value = Set of 1-based Navamsa indices (1 to 9) within that sign.
# Fire Signs (1, 5, 9): 7th (Libra) & 9th (Sagittarius) Navamsa
# Earth Signs (2, 6, 10): 3rd (Pisces) & 5th (Taurus) Navamsa
# Air Signs (3, 7, 11): 6th (Pisces) & 8th (Taurus) Navamsa
# Water Signs (4, 8, 12): 1st (Cancer) & 3rd (Virgo) Navamsa
# Note: Every Pushkara Navamsa falls in a sign ruled by a natural benefic (Moon, Mercury, Venus, Jupiter).
PUSHKARA_NAVAMSAS: Dict[int, set[int]] = {
    1: {7, 9}, 5: {7, 9}, 9: {7, 9},
    2: {3, 5}, 6: {3, 5}, 10: {3, 5},
    3: {6, 8}, 7: {6, 8}, 11: {6, 8},
    4: {1, 3}, 8: {1, 3}, 12: {1, 3},
}

# Angular Constants in Integer Milli-Arcseconds (mas)
# 1 degree = 3,600 arcsec = 3,600,000 mas
MAS_PER_DEGREE: int = 3_600_000
MAS_PER_CIRCLE: int = 360 * MAS_PER_DEGREE       # 1,296,000,000 mas
MAS_PER_SIGN: int = 30 * MAS_PER_DEGREE          # 108,000,000 mas
MAS_PER_NAKSHATRA: int = 48_000_000              # (360 / 27) * 3,600,000 = 48,000,000 mas
MAS_PER_NAVAMSA: int = 12_000_000                # (360 / 108) * 3,600,000 = 12,000,000 mas


def normalize_longitude_mas(lon_deg: float) -> int:
    """Normalize longitude to [0, 360) and convert to exact integer milli-arcseconds."""
    norm = float(lon_deg) % 360.0
    if norm < 0.0:
        norm += 360.0
    total_mas = int(round(norm * MAS_PER_DEGREE)) % MAS_PER_CIRCLE
    return total_mas


def calculate_navamsa_from_longitude(lon_deg: float) -> Dict[str, Any]:
    """Calculate exact D1 sign, D9 Navamsa sign, degrees, and Nakshatra/pada using integer arithmetic.
    
    Guarantees zero floating-point division errors on exact boundaries.
    """
    total_mas = normalize_longitude_mas(lon_deg)

    # 1. D1 Rasi Calculation
    d1_sign_idx = (total_mas // MAS_PER_SIGN) + 1
    d1_rem_mas = total_mas % MAS_PER_SIGN
    d1_deg_in_sign = d1_rem_mas / float(MAS_PER_DEGREE)

    # 2. Nakshatra and Pada Calculation
    nak_idx = (total_mas // MAS_PER_NAKSHATRA) % 27
    nak_rem_mas = total_mas % MAS_PER_NAKSHATRA
    pada = (nak_rem_mas // MAS_PER_NAVAMSA) + 1  # 1 to 4
    star_lord = VIMSHOTTARI_LORDS[nak_idx % 9]
    nak_name = NAKSHATRA_NAMES[nak_idx]

    # 3. D9 Navamsa Calculation (108 continuous divisions across zodiac)
    total_navamsa_idx = total_mas // MAS_PER_NAVAMSA  # 0 to 107
    d9_sign_idx = (total_navamsa_idx % 12) + 1
    
    # Navamsa index within sign (1 to 9)
    navamsa_in_sign = (d1_rem_mas // MAS_PER_NAVAMSA) + 1
    
    # Degree in Navamsa sign: each 3°20' (12,000,000 mas) maps to 30° (108,000,000 mas) -> 9x scale
    rem_in_navamsa_mas = total_mas % MAS_PER_NAVAMSA
    d9_deg_in_sign = (rem_in_navamsa_mas * 9) / float(MAS_PER_DEGREE)

    # 4. Dignities & Special Status
    is_vargottama = (d1_sign_idx == d9_sign_idx)
    is_pushkara = navamsa_in_sign in PUSHKARA_NAVAMSAS.get(d1_sign_idx, set())

    return {
        "d1_longitude": (total_mas / float(MAS_PER_DEGREE)),
        "d1_sign_index": d1_sign_idx,
        "d1_sign_name": SIGN_NAMES_EN[d1_sign_idx],
        "d1_sign_name_tamil": SIGN_NAMES_TA[d1_sign_idx],
        "d1_degree_in_sign": d1_deg_in_sign,
        "d1_sign_lord": SIGN_LORDS[d1_sign_idx],
        "d9_sign_index": d9_sign_idx,
        "d9_sign_name": SIGN_NAMES_EN[d9_sign_idx],
        "d9_sign_name_tamil": SIGN_NAMES_TA[d9_sign_idx],
        "d9_degree_in_sign": d9_deg_in_sign,
        "d9_sign_lord": SIGN_LORDS[d9_sign_idx],
        "nakshatra_name": nak_name,
        "nakshatra_index": nak_idx,
        "pada": pada,
        "star_lord": star_lord,
        "navamsa_in_sign": navamsa_in_sign,
        "navamsa_index_in_sign": navamsa_in_sign,
        "is_vargottama": is_vargottama,
        "is_pushkara_navamsa": is_pushkara,
    }


def calculate_varga_d1_d9(
    planets: List[Any],
    ascendant: Any,
    metadata: Optional[Any] = None,
) -> VargaD1D9Response:
    """Construct complete D1 and D9 structures with whole-sign houses and chart rendering models.
    
    Parameters
    ----------
    planets : list
        List of PlanetInfo objects or dicts with `name`, `longitude`, `speed_deg_per_day`, etc.
    ascendant : object or dict
        AscendantInfo with `degree` / `longitude`.
    metadata : CalculationMetadata, optional
        Metadata instance or dict.
    """
    # 1. Resolve Ascendant
    asc_deg = getattr(ascendant, "degree", None)
    if asc_deg is None and isinstance(ascendant, dict):
        asc_deg = ascendant.get("degree") or ascendant.get("longitude") or 0.0

    asc_varga = calculate_navamsa_from_longitude(float(asc_deg))
    asc_pos = VargaAscendantPosition(
        d1_degree=asc_varga["d1_longitude"],
        d1_sign_index=asc_varga["d1_sign_index"],
        d1_sign_name=asc_varga["d1_sign_name"],
        d1_sign_name_tamil=asc_varga["d1_sign_name_tamil"],
        d1_degree_in_sign=asc_varga["d1_degree_in_sign"],
        d1_sign_lord=asc_varga["d1_sign_lord"],
        d9_sign_index=asc_varga["d9_sign_index"],
        d9_sign_name=asc_varga["d9_sign_name"],
        d9_sign_name_tamil=asc_varga["d9_sign_name_tamil"],
        d9_degree_in_sign=asc_varga["d9_degree_in_sign"],
        d9_sign_lord=asc_varga["d9_sign_lord"],
        is_vargottama=asc_varga["is_vargottama"],
        nakshatra_name=asc_varga["nakshatra_name"],
        nakshatra_index=asc_varga["nakshatra_index"],
        pada=asc_varga["pada"],
        star_lord=asc_varga["star_lord"],
    )

    d1_asc_sign = asc_pos.d1_sign_index
    d9_asc_sign = asc_pos.d9_sign_index

    # 2. Process Planets
    varga_planets: List[VargaPlanetPosition] = []
    vargottama_names: List[str] = []
    pushkara_names: List[str] = []

    # Rendering payloads for chart components
    d1_chart_planets: List[Dict[str, Any]] = []
    d9_chart_planets: List[Dict[str, Any]] = []

    for p in planets:
        name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else None)
        if not name:
            continue

        lon = getattr(p, "longitude", None) or (p.get("longitude") if isinstance(p, dict) else None)
        if lon is None:
            continue

        body_id = getattr(p, "body_id", 0) or (p.get("body_id", 0) if isinstance(p, dict) else 0)
        speed = getattr(p, "speed_deg_per_day", 1.0) or (p.get("speed_deg_per_day", 1.0) if isinstance(p, dict) else 1.0)
        retro = getattr(p, "is_retrograde", False) or (p.get("is_retrograde", False) if isinstance(p, dict) else False)

        pv = calculate_navamsa_from_longitude(float(lon))

        # Whole-sign houses: 1-12 relative to Lagna
        d1_house = ((pv["d1_sign_index"] - d1_asc_sign) % 12) + 1
        d9_house = ((pv["d9_sign_index"] - d9_asc_sign) % 12) + 1

        if pv["is_vargottama"]:
            vargottama_names.append(name)
        if pv["is_pushkara_navamsa"]:
            pushkara_names.append(name)

        pos_record = VargaPlanetPosition(
            name=name,
            body_id=int(body_id),
            d1_longitude=pv["d1_longitude"],
            d1_sign_index=pv["d1_sign_index"],
            d1_sign_name=pv["d1_sign_name"],
            d1_sign_name_tamil=pv["d1_sign_name_tamil"],
            d1_degree_in_sign=pv["d1_degree_in_sign"],
            d1_house=d1_house,
            d1_sign_lord=pv["d1_sign_lord"],
            d9_sign_index=pv["d9_sign_index"],
            d9_sign_name=pv["d9_sign_name"],
            d9_sign_name_tamil=pv["d9_sign_name_tamil"],
            d9_degree_in_sign=pv["d9_degree_in_sign"],
            d9_house=d9_house,
            d9_sign_lord=pv["d9_sign_lord"],
            is_vargottama=pv["is_vargottama"],
            is_pushkara_navamsa=pv["is_pushkara_navamsa"],
            is_retrograde=bool(retro),
            speed_deg_per_day=float(speed),
            nakshatra_name=pv["nakshatra_name"],
            nakshatra_index=pv["nakshatra_index"],
            pada=pv["pada"],
            star_lord=pv["star_lord"],
        )
        varga_planets.append(pos_record)

        # Build chart-compatible item for SouthIndianChart & NorthIndianChart
        d1_chart_planets.append({
            "name": name,
            "sign_index": pv["d1_sign_index"],
            "sign_name": pv["d1_sign_name"],
            "sign_name_tamil": pv["d1_sign_name_tamil"],
            "degree_in_sign": pv["d1_degree_in_sign"],
            "is_retrograde": bool(retro),
        })

        d9_chart_planets.append({
            "name": name,
            "sign_index": pv["d9_sign_index"],
            "sign_name": pv["d9_sign_name"],
            "sign_name_tamil": pv["d9_sign_name_tamil"],
            "degree_in_sign": pv["d9_degree_in_sign"],
            "is_retrograde": bool(retro),
        })

    # 3. Metadata resolution
    if isinstance(metadata, CalculationMetadata):
        calc_meta = metadata
    elif isinstance(metadata, dict):
        calc_meta = CalculationMetadata(
            engine=metadata.get("engine", "XALEN 0.6.0 (Rust)"),
            birth_utc_iso=metadata.get("birth_utc_iso", ""),
            julian_day_ut1=float(metadata.get("julian_day_ut1", 0.0)),
            local_timezone=metadata.get("local_timezone"),
            utc_offset_hours=metadata.get("utc_offset_hours"),
            coordinates=metadata.get("coordinates"),
            ayanamsa_id=int(metadata.get("ayanamsa_id", 0)),
            ayanamsa_name=metadata.get("ayanamsa_name", "Lahiri (Chitra Paksha)"),
            ayanamsa_deg=float(metadata.get("ayanamsa_deg", 24.1)),
            house_system_id=int(metadata.get("house_system_id", 0)),
            house_system_name=metadata.get("house_system_name", "Whole Sign"),
            calculation_frame=metadata.get("calculation_frame", "Geocentric Sidereal"),
            notes=metadata.get("notes", []),
        )
    else:
        calc_meta = CalculationMetadata(
            engine="XALEN 0.6.0 (Rust)",
            birth_utc_iso="",
            julian_day_ut1=0.0,
            ayanamsa_id=0,
            ayanamsa_name="Lahiri (Chitra Paksha)",
            ayanamsa_deg=24.1,
            house_system_id=0,
            house_system_name="Whole Sign",
        )

    meta_dict = calc_meta.model_dump()

    # 4. Standard Chart rendering structures consumable by frontend chart components
    d1_chart = {
        "metadata": meta_dict,
        "ascendant": {
            "sign_index": asc_pos.d1_sign_index,
            "sign_name": asc_pos.d1_sign_name,
            "sign_name_tamil": asc_pos.d1_sign_name_tamil,
            "degree_in_sign": asc_pos.d1_degree_in_sign,
        },
        "planets": d1_chart_planets,
    }

    d9_chart = {
        "metadata": meta_dict,
        "ascendant": {
            "sign_index": asc_pos.d9_sign_index,
            "sign_name": asc_pos.d9_sign_name,
            "sign_name_tamil": asc_pos.d9_sign_name_tamil,
            "degree_in_sign": asc_pos.d9_degree_in_sign,
        },
        "planets": d9_chart_planets,
    }

    # 5. Summary metrics
    summary = VargaChartSummary(
        vargottama_planets=vargottama_names,
        pushkara_navamsa_planets=pushkara_names,
        total_vargottama_count=len(vargottama_names),
        d9_lagna_sign=asc_pos.d9_sign_name,
        d9_lagna_sign_tamil=asc_pos.d9_sign_name_tamil,
    )

    return VargaD1D9Response(
        metadata=calc_meta,
        ascendant=asc_pos,
        planets=varga_planets,
        summary=summary,
        d1_chart=d1_chart,
        d9_chart=d9_chart,
    )


def calculate_varga_from_horoscope_dict(horoscope_data: Dict[str, Any]) -> VargaD1D9Response:
    """Helper to compute D1/D9 directly from an existing horoscope calculation snapshot dictionary."""
    planets = horoscope_data.get("planets") or []
    ascendant = horoscope_data.get("ascendant") or {}
    metadata = horoscope_data.get("metadata") or {}
    return calculate_varga_d1_d9(planets=planets, ascendant=ascendant, metadata=metadata)
