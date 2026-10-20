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
    ShodashvargaPlanetEntry,
    ShodashvargaAscendantEntry,
    ShodashvargaChartItem,
    ShodashvargaResponse,
    ShodashvargaRequest,
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

    # 6. Compute complete Shodashvarga (16 divisional charts)
    shodash_res = calculate_shodashvarga(
        planets=planets,
        ascendant=ascendant,
        metadata=calc_meta,
    )

    return VargaD1D9Response(
        metadata=calc_meta,
        ascendant=asc_pos,
        planets=varga_planets,
        summary=summary,
        d1_chart=d1_chart,
        d9_chart=d9_chart,
        shodashvarga=shodash_res,
    )


def calculate_varga_from_horoscope_dict(horoscope_data: Dict[str, Any]) -> VargaD1D9Response:
    """Helper to compute D1/D9 directly from an existing horoscope calculation snapshot dictionary."""
    planets = horoscope_data.get("planets") or []
    ascendant = horoscope_data.get("ascendant") or {}
    metadata = horoscope_data.get("metadata") or {}
    return calculate_varga_d1_d9(planets=planets, ascendant=ascendant, metadata=metadata)


# ============================================================================
# COMPLETE CLASSICAL SHODASHVARGA (16 DIVISIONAL CHARTS) ENGINE
# ============================================================================

SHODASHVARGA_KEYS: List[str] = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]

DIVISION_METADATA: Dict[str, Dict[str, Any]] = {
    "D1": {
        "number": 1,
        "name": "Rasi",
        "name_tamil": "ராசி",
        "significance": "Physical body, overall existence, vitality, and general destiny",
        "significance_tamil": "உடல், பொதுவான வாழ்வியல் மற்றும் அடிப்படை விதி",
        "span_deg": 30.0,
    },
    "D2": {
        "number": 2,
        "name": "Hora",
        "name_tamil": "ஹோரை",
        "significance": "Wealth, financial prosperity, assets, speech, and resources",
        "significance_tamil": "தனம், செல்வம் மற்றும் குடும்ப வளங்கள்",
        "span_deg": 15.0,
    },
    "D3": {
        "number": 3,
        "name": "Drekkana",
        "name_tamil": "திரேக்காணம்",
        "significance": "Siblings, courage, enterprise, vitality, and health of brothers/sisters",
        "significance_tamil": "சகோதரர்கள், தைரியம், வீரியம் மற்றும் முயற்சிகள்",
        "span_deg": 10.0,
    },
    "D4": {
        "number": 4,
        "name": "Chaturthamsa",
        "name_tamil": "சதுர்த்தாம்சம் (துர்யாம்சம்)",
        "significance": "Fixed assets, real estate, conveyances, home, and fortune",
        "significance_tamil": "நிலம், வீடு, வாகனம் மற்றும் நிலையான சொத்துக்கள்",
        "span_deg": 7.5,
    },
    "D7": {
        "number": 7,
        "name": "Saptamsa",
        "name_tamil": "சப்தாம்சம்",
        "significance": "Progeny, children, grandchildren, creative lineage, and happiness from offspring",
        "significance_tamil": "புத்திர பாக்கியம், குழந்தைகள் மற்றும் வம்ச விருத்தி",
        "span_deg": 30.0 / 7.0,
    },
    "D9": {
        "number": 9,
        "name": "Navamsa",
        "name_tamil": "நவாம்சம்",
        "significance": "Spouse, marriage, inner soul purpose, dharma, and general planetary potency",
        "significance_tamil": "களத்திரம், திருமணம், தர்மம் மற்றும் ஆன்ம பலம்",
        "span_deg": 10.0 / 3.0,
    },
    "D10": {
        "number": 10,
        "name": "Dasamsa",
        "name_tamil": "தசாம்சம் (ஸ்வர்க்காம்சம்)",
        "significance": "Career, profession, executive authority, public reputation, and worldly achievements",
        "significance_tamil": "தொழில், உத்தியோகம், சமூக அந்தஸ்து மற்றும் அதிகார பலம்",
        "span_deg": 3.0,
    },
    "D12": {
        "number": 12,
        "name": "Dwadasamsa",
        "name_tamil": "துவாதசாம்சம்",
        "significance": "Parents, maternal and paternal lineage, ancestral heritage, and longevity of elders",
        "significance_tamil": "பெற்றோர்கள், தாய்-தந்தை வழி பூர்வீக பரம்பரை",
        "span_deg": 2.5,
    },
    "D16": {
        "number": 16,
        "name": "Shodasamsa",
        "name_tamil": "ஷோடசாம்சம் (கலாம்சம்)",
        "significance": "Vehicles, conveyances, general luxuries, physical comforts, and vehicular safety",
        "significance_tamil": "வாகன சுகம், சொகுசு மற்றும் விபத்து இல்லாத பயணம்",
        "span_deg": 1.875,
    },
    "D20": {
        "number": 20,
        "name": "Vimsamsa",
        "name_tamil": "விம்சாம்சம்",
        "significance": "Spiritual inclinations, meditation, upasana, mantra siddhi, and devotion",
        "significance_tamil": "ஆன்மீக நாட்டம், உபாசனை, தியானம் மற்றும் தெய்வ அருள்",
        "span_deg": 1.5,
    },
    "D24": {
        "number": 24,
        "name": "Chaturvimsamsa",
        "name_tamil": "சதுர்விம்சாம்சம் (சித்தாமிசம்)",
        "significance": "Higher education, learning, intellectual scholarship, and academic wisdom",
        "significance_tamil": "உயர்கல்வி, ஞானம், கல்வி மேன்மை மற்றும் ஆராய்ச்சி",
        "span_deg": 1.25,
    },
    "D27": {
        "number": 27,
        "name": "Saptavimsamsa",
        "name_tamil": "சப்தவிம்சாம்சம் (பாகாம்சம்)",
        "significance": "Subconscious strengths, physical stamina, inherent vitality, and hidden vulnerabilities",
        "significance_tamil": "உடல் பலம், பலவீனம், மன உறுதி மற்றும் உள் ஆற்றல்",
        "span_deg": 10.0 / 9.0,
    },
    "D30": {
        "number": 30,
        "name": "Trimsamsa",
        "name_tamil": "திரிம்சாம்சம்",
        "significance": "Misfortunes, evils, chronic afflictions, doshas, character flaws, and moral trials",
        "significance_tamil": "அரிஷ்டம், நோய்கள், தோஷங்கள் மற்றும் துன்பங்கள்",
        "span_deg": 0.0,
    },
    "D40": {
        "number": 40,
        "name": "Khavedamsa",
        "name_tamil": "கவேதாம்சம் (சுவவேதாம்சம்)",
        "significance": "Subtle auspicious and inauspicious karmic effects, spiritual inclinations, and overall fortune",
        "significance_tamil": "சுப-அசுப பலன்கள் மற்றும் நுண்ணிய யோகங்கள்",
        "span_deg": 0.75,
    },
    "D45": {
        "number": 45,
        "name": "Akshavedamsa",
        "name_tamil": "அக்ஷவேதாம்சம்",
        "significance": "Holistic character, moral integrity, purity, and general fine-tuned life assessment",
        "significance_tamil": "ஒழுக்கம், நடத்தை, ஆளுமை மற்றும் தூய்மை",
        "span_deg": 2.0 / 3.0,
    },
    "D60": {
        "number": 60,
        "name": "Shashtyamsa",
        "name_tamil": "ஷஷ்டியாம்சம்",
        "significance": "Past-life karma, root-cause spiritual destiny, and supreme classical validation",
        "significance_tamil": "பூர்வ ஜென்ம கர்ம வினைகள் மற்றும் தலையெழுத்து",
        "span_deg": 0.5,
    },
}

# Classical 60 Shashtyamsa Deities per BPHS Ch. 6, Slokas 35-41
SHASHTYAMSA_DEITIES: List[Tuple[str, str, str]] = [
    ("Ghora", "கோரம்", "Malefic"),
    ("Rakshasa", "ராட்சஸம்", "Malefic"),
    ("Deva", "தேவம்", "Benefic"),
    ("Kubera", "குபேரம்", "Benefic"),
    ("Yaksha", "யக்ஷம்", "Benefic"),
    ("Kinnara", "கின்னரம்", "Benefic"),
    ("Bhrashta", "பிரஷ்டம்", "Malefic"),
    ("Kulaghna", "குலக்னம்", "Malefic"),
    ("Garala", "கரளம்", "Malefic"),
    ("Vahni", "வன்னி", "Malefic"),
    ("Maya", "மாயா", "Malefic"),
    ("Purishaka", "புரீஷகம்", "Malefic"),
    ("Apampati", "அபாம்பதி", "Benefic"),
    ("Marutwana", "மாருத்வானம்", "Benefic"),
    ("Kala", "காலம்", "Malefic"),
    ("Sarpa", "சர்ப்பம்", "Malefic"),
    ("Amrita", "அமிர்தம்", "Benefic"),
    ("Indu", "இந்து", "Benefic"),
    ("Mridu", "மிருது", "Benefic"),
    ("Komala", "கோமளம்", "Benefic"),
    ("Heramba", "ஹேரம்பம்", "Benefic"),
    ("Brahma", "பிரம்மா", "Benefic"),
    ("Vishnu", "விஷ்ணு", "Benefic"),
    ("Maheswara", "மகேஸ்வரம்", "Benefic"),
    ("Deva", "தேவம்", "Benefic"),
    ("Ardra", "ஆர்த்ரா", "Benefic"),
    ("Kalinasana", "கலிநாசனம்", "Benefic"),
    ("Kshiteesa", "க்ஷிதீசம்", "Benefic"),
    ("Kamalakara", "கமலாகரம்", "Benefic"),
    ("Gulika", "குளிகன்", "Malefic"),
    ("Mrityu", "மிருத்யு", "Malefic"),
    ("Kala", "காலம்", "Malefic"),
    ("Davagni", "தாவாக்கினி", "Malefic"),
    ("Ghora", "கோரம்", "Malefic"),
    ("Yama", "யமன்", "Malefic"),
    ("Kantaka", "கண்டகம்", "Malefic"),
    ("Sudha", "சுதா", "Benefic"),
    ("Amrita", "அமிர்தம்", "Benefic"),
    ("Poornachandra", "பூர்ணசந்திரன்", "Benefic"),
    ("Vishadagdha", "விஷதக்தம்", "Malefic"),
    ("Kulanasa", "குலநாசம்", "Malefic"),
    ("Vamshakshaya", "வம்சக்ஷயம்", "Malefic"),
    ("Utpata", "உத்பாதம்", "Malefic"),
    ("Kaalarupa", "காலரூபம்", "Malefic"),
    ("Saumya", "சௌமியம்", "Benefic"),
    ("Mridu", "மிருது", "Benefic"),
    ("Susheetala", "சுசீதளம்", "Benefic"),
    ("Damshtra", "தம்ஷ்ட்ரா", "Malefic"),
    ("Indumukha", "இந்துமுகம்", "Benefic"),
    ("Praveena", "பிரவீணம்", "Benefic"),
    ("Kalagni", "காலாக்கினி", "Malefic"),
    ("Dandayudha", "தண்டாயுதம்", "Malefic"),
    ("Nirmala", "நிர்மலம்", "Benefic"),
    ("Shubha", "சுபம்", "Benefic"),
    ("Ashubha", "அசுபம்", "Malefic"),
    ("Sheetala", "சீதளம்", "Benefic"),
    ("Sudha", "சுதா", "Benefic"),
    ("Payodhi", "பயோதி", "Benefic"),
    ("Bhramana", "பிரமணம்", "Malefic"),
    ("Indurekha", "இந்துரேகா", "Benefic"),
]


def calculate_divisional_placement(lon_deg: float, div_key: str) -> Dict[str, Any]:
    """Calculate exact divisional placement for any of the 16 classical Shodashvarga charts.
    
    Uses integer milli-arcsecond (mas) arithmetic to eliminate IEEE 754 precision issues on cusp boundaries.
    """
    total_mas = normalize_longitude_mas(lon_deg)
    d1_sign_idx = (total_mas // MAS_PER_SIGN) + 1
    rem_sign_mas = total_mas % MAS_PER_SIGN
    is_odd = (d1_sign_idx % 2 == 1)
    is_movable = d1_sign_idx in (1, 4, 7, 10)
    is_fixed = d1_sign_idx in (2, 5, 8, 11)
    is_dual = d1_sign_idx in (3, 6, 9, 12)

    shashtyamsa_deity = None
    shashtyamsa_deity_ta = None
    shashtyamsa_nature = None

    if div_key == "D1":
        div_sign = d1_sign_idx
        deg_in_sign = rem_sign_mas / float(MAS_PER_DEGREE)

    elif div_key == "D2":
        # Hora (15°): 2 parts of 54,000,000 mas
        k = min(1, rem_sign_mas // 54_000_000)
        if is_odd:
            div_sign = 5 if k == 0 else 4  # Sun (Leo) then Moon (Cancer)
        else:
            div_sign = 4 if k == 0 else 5  # Moon (Cancer) then Sun (Leo)
        deg_in_sign = ((rem_sign_mas % 54_000_000) * 2) / float(MAS_PER_DEGREE)

    elif div_key == "D3":
        # Drekkana (10°): 3 parts of 36,000,000 mas (1st, 5th, 9th from sign)
        k = min(2, rem_sign_mas // 36_000_000)
        div_sign = ((d1_sign_idx - 1 + 4 * k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 36_000_000) * 3) / float(MAS_PER_DEGREE)

    elif div_key == "D4":
        # Chaturthamsa (7.5°): 4 parts of 27,000,000 mas (1st, 4th, 7th, 10th from sign)
        k = min(3, rem_sign_mas // 27_000_000)
        div_sign = ((d1_sign_idx - 1 + 3 * k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 27_000_000) * 4) / float(MAS_PER_DEGREE)

    elif div_key == "D7":
        # Saptamsa (30°/7): 7 parts
        k = min(6, (rem_sign_mas * 7) // MAS_PER_SIGN)
        if is_odd:
            div_sign = ((d1_sign_idx - 1 + k) % 12) + 1
        else:
            div_sign = ((d1_sign_idx - 1 + 6 + k) % 12) + 1
        rem_part_mas = rem_sign_mas - (k * MAS_PER_SIGN // 7)
        deg_in_sign = min(29.999999, max(0.0, (rem_part_mas * 7) / float(MAS_PER_DEGREE)))

    elif div_key == "D9":
        # Navamsa (3°20'): 9 parts of 12,000,000 mas
        total_navamsa_idx = total_mas // 12_000_000
        div_sign = (total_navamsa_idx % 12) + 1
        deg_in_sign = ((total_mas % 12_000_000) * 9) / float(MAS_PER_DEGREE)

    elif div_key == "D10":
        # Dasamsa (3°): 10 parts of 10,800,000 mas
        k = min(9, rem_sign_mas // 10_800_000)
        if is_odd:
            div_sign = ((d1_sign_idx - 1 + k) % 12) + 1
        else:
            div_sign = ((d1_sign_idx - 1 + 8 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 10_800_000) * 10) / float(MAS_PER_DEGREE)

    elif div_key == "D12":
        # Dwadasamsa (2.5°): 12 parts of 9,000,000 mas (starts from sign itself)
        k = min(11, rem_sign_mas // 9_000_000)
        div_sign = ((d1_sign_idx - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 9_000_000) * 12) / float(MAS_PER_DEGREE)

    elif div_key == "D16":
        # Shodasamsa (1.875°): 16 parts of 6,750,000 mas
        k = min(15, rem_sign_mas // 6_750_000)
        start = 1 if is_movable else (5 if is_fixed else 9)
        div_sign = ((start - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 6_750_000) * 16) / float(MAS_PER_DEGREE)

    elif div_key == "D20":
        # Vimsamsa (1.5°): 20 parts of 5,400,000 mas
        k = min(19, rem_sign_mas // 5_400_000)
        start = 1 if is_movable else (9 if is_fixed else 5)
        div_sign = ((start - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 5_400_000) * 20) / float(MAS_PER_DEGREE)

    elif div_key == "D24":
        # Chaturvimsamsa (1.25°): 24 parts of 4,500,000 mas
        k = min(23, rem_sign_mas // 4_500_000)
        start = 5 if is_odd else 4
        div_sign = ((start - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 4_500_000) * 24) / float(MAS_PER_DEGREE)

    elif div_key == "D27":
        # Saptavimsamsa (1°6'40"): 27 parts of 4,000,000 mas
        total_nak_idx = total_mas // 4_000_000
        div_sign = (total_nak_idx % 12) + 1
        deg_in_sign = ((total_mas % 4_000_000) * 27) / float(MAS_PER_DEGREE)

    elif div_key == "D30":
        # Trimsamsa: unequal degree partitions
        # Odd: 0-5 Mars(Aries 1), 5-10 Saturn(Aquarius 11), 10-18 Jupiter(Sagittarius 9), 18-25 Mercury(Gemini 3), 25-30 Venus(Libra 7)
        # Even: 0-5 Venus(Taurus 2), 5-12 Mercury(Virgo 6), 12-20 Jupiter(Pisces 12), 20-25 Saturn(Capricorn 10), 25-30 Mars(Scorpio 8)
        if is_odd:
            if rem_sign_mas < 18_000_000:
                div_sign = 1
                deg_in_sign = (rem_sign_mas * 30.0) / 18_000_000.0
            elif rem_sign_mas < 36_000_000:
                div_sign = 11
                deg_in_sign = ((rem_sign_mas - 18_000_000) * 30.0) / 18_000_000.0
            elif rem_sign_mas < 64_800_000:
                div_sign = 9
                deg_in_sign = ((rem_sign_mas - 36_000_000) * 30.0) / 28_800_000.0
            elif rem_sign_mas < 90_000_000:
                div_sign = 3
                deg_in_sign = ((rem_sign_mas - 64_800_000) * 30.0) / 25_200_000.0
            else:
                div_sign = 7
                deg_in_sign = ((rem_sign_mas - 90_000_000) * 30.0) / 18_000_000.0
        else:
            if rem_sign_mas < 18_000_000:
                div_sign = 2
                deg_in_sign = (rem_sign_mas * 30.0) / 18_000_000.0
            elif rem_sign_mas < 43_200_000:
                div_sign = 6
                deg_in_sign = ((rem_sign_mas - 18_000_000) * 30.0) / 25_200_000.0
            elif rem_sign_mas < 72_000_000:
                div_sign = 12
                deg_in_sign = ((rem_sign_mas - 43_200_000) * 30.0) / 28_800_000.0
            elif rem_sign_mas < 90_000_000:
                div_sign = 10
                deg_in_sign = ((rem_sign_mas - 72_000_000) * 30.0) / 18_000_000.0
            else:
                div_sign = 8
                deg_in_sign = ((rem_sign_mas - 90_000_000) * 30.0) / 18_000_000.0

    elif div_key == "D40":
        # Khavedamsa (0.75°): 40 parts of 2,700,000 mas
        k = min(39, rem_sign_mas // 2_700_000)
        start = 1 if is_odd else 7
        div_sign = ((start - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 2_700_000) * 40) / float(MAS_PER_DEGREE)

    elif div_key == "D45":
        # Akshavedamsa (2/3°): 45 parts of 2,400,000 mas
        k = min(44, rem_sign_mas // 2_400_000)
        start = 1 if is_movable else (5 if is_fixed else 9)
        div_sign = ((start - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 2_400_000) * 45) / float(MAS_PER_DEGREE)

    elif div_key == "D60":
        # Shashtyamsa (0.5°): 60 parts of 1,800,000 mas
        k = min(59, rem_sign_mas // 1_800_000)
        div_sign = ((d1_sign_idx - 1 + k) % 12) + 1
        deg_in_sign = ((rem_sign_mas % 1_800_000) * 60) / float(MAS_PER_DEGREE)
        deity_idx = k if is_odd else (59 - k)
        deity_tuple = SHASHTYAMSA_DEITIES[deity_idx]
        shashtyamsa_deity = deity_tuple[0]
        shashtyamsa_deity_ta = deity_tuple[1]
        shashtyamsa_nature = deity_tuple[2]

    else:
        raise ValueError(f"Unknown divisional key: {div_key}")

    return {
        "division_id": div_key,
        "sign_index": div_sign,
        "sign_name": SIGN_NAMES_EN[div_sign],
        "sign_name_tamil": SIGN_NAMES_TA[div_sign],
        "degree_in_sign": min(29.999999, max(0.0, deg_in_sign)),
        "sign_lord": SIGN_LORDS[div_sign],
        "is_vargottama": (div_sign == d1_sign_idx),
        "shashtyamsa_deity": shashtyamsa_deity,
        "shashtyamsa_deity_tamil": shashtyamsa_deity_ta,
        "shashtyamsa_nature": shashtyamsa_nature,
    }


def calculate_shodashvarga(
    planets: List[Any],
    ascendant: Any,
    metadata: Optional[Any] = None,
) -> ShodashvargaResponse:
    """Calculate the complete set of 16 classical Shodashvarga charts per BPHS Ch. 6.
    
    Generates standardized chart rendering structures consumable by frontend chart components
    (SouthIndianChart and NorthIndianChart) for each of the 16 divisional charts.
    """
    # 1. Resolve Ascendant
    asc_deg = getattr(ascendant, "degree", None)
    if asc_deg is None and isinstance(ascendant, dict):
        asc_deg = ascendant.get("degree") or ascendant.get("longitude") or 0.0
    asc_lon = float(asc_deg)

    asc_divs: Dict[str, Dict[str, Any]] = {
        div_k: calculate_divisional_placement(asc_lon, div_k)
        for div_k in SHODASHVARGA_KEYS
    }

    # 2. Resolve Metadata
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

    # 3. Process Planets across all 16 divisions
    # planet_name -> {div_key: div_placement}
    planet_divisions: Dict[str, Dict[str, Dict[str, Any]]] = {}
    planet_meta_info: Dict[str, Dict[str, Any]] = {}

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

        planet_meta_info[name] = {
            "body_id": int(body_id),
            "speed": float(speed),
            "retro": bool(retro),
        }

        planet_divisions[name] = {
            div_k: calculate_divisional_placement(float(lon), div_k)
            for div_k in SHODASHVARGA_KEYS
        }

    # 4. Construct ShodashvargaChartItem for each of the 16 charts
    charts: Dict[str, ShodashvargaChartItem] = {}
    planet_vargas_map: Dict[str, Dict[str, int]] = {p_name: {} for p_name in planet_divisions}
    vargottama_planets_list: List[str] = []

    for div_k in SHODASHVARGA_KEYS:
        div_meta = DIVISION_METADATA[div_k]
        asc_div = asc_divs[div_k]
        div_asc_sign = asc_div["sign_index"]

        asc_entry = ShodashvargaAscendantEntry(
            sign_index=div_asc_sign,
            sign_name=asc_div["sign_name"],
            sign_name_tamil=asc_div["sign_name_tamil"],
            degree_in_sign=asc_div["degree_in_sign"],
            sign_lord=asc_div["sign_lord"],
            is_vargottama=asc_div["is_vargottama"],
            shashtyamsa_deity=asc_div["shashtyamsa_deity"],
            shashtyamsa_deity_tamil=asc_div["shashtyamsa_deity_tamil"],
            shashtyamsa_nature=asc_div["shashtyamsa_nature"],
        )

        chart_planets_payload: List[Dict[str, Any]] = []
        div_planets_entries: List[ShodashvargaPlanetEntry] = []

        for p_name, p_divs in planet_divisions.items():
            p_div = p_divs[div_k]
            p_sign = p_div["sign_index"]
            p_house = ((p_sign - div_asc_sign) % 12) + 1
            meta_p = planet_meta_info[p_name]

            planet_vargas_map[p_name][div_k] = p_sign

            if div_k == "D9" and p_div["is_vargottama"]:
                vargottama_planets_list.append(p_name)

            p_entry = ShodashvargaPlanetEntry(
                name=p_name,
                body_id=meta_p["body_id"],
                sign_index=p_sign,
                sign_name=p_div["sign_name"],
                sign_name_tamil=p_div["sign_name_tamil"],
                degree_in_sign=p_div["degree_in_sign"],
                house=p_house,
                sign_lord=p_div["sign_lord"],
                is_retrograde=meta_p["retro"],
                is_vargottama=p_div["is_vargottama"],
                shashtyamsa_deity=p_div["shashtyamsa_deity"],
                shashtyamsa_deity_tamil=p_div["shashtyamsa_deity_tamil"],
                shashtyamsa_nature=p_div["shashtyamsa_nature"],
            )
            div_planets_entries.append(p_entry)

            chart_planets_payload.append({
                "name": p_name,
                "sign_index": p_sign,
                "sign_name": p_div["sign_name"],
                "sign_name_tamil": p_div["sign_name_tamil"],
                "degree_in_sign": p_div["degree_in_sign"],
                "is_retrograde": meta_p["retro"],
            })

        chart_render_structure = {
            "metadata": meta_dict,
            "ascendant": {
                "sign_index": div_asc_sign,
                "sign_name": asc_div["sign_name"],
                "sign_name_tamil": asc_div["sign_name_tamil"],
                "degree_in_sign": asc_div["degree_in_sign"],
            },
            "planets": chart_planets_payload,
        }

        charts[div_k] = ShodashvargaChartItem(
            division_id=div_k,
            division_number=div_meta["number"],
            name=div_meta["name"],
            name_tamil=div_meta["name_tamil"],
            significance=div_meta["significance"],
            significance_tamil=div_meta["significance_tamil"],
            span_degrees=div_meta["span_deg"],
            ascendant=asc_entry,
            planets=div_planets_entries,
            chart=chart_render_structure,
        )

    # Key chart structures for direct consumption
    d1_chart = charts["D1"].chart
    d9_chart = charts["D9"].chart
    d10_chart = charts["D10"].chart
    d60_chart = charts["D60"].chart

    return ShodashvargaResponse(
        metadata=calc_meta,
        charts=charts,
        planet_vargas=planet_vargas_map,
        vargottama_planets=list(dict.fromkeys(vargottama_planets_list)),
        d1_chart=d1_chart,
        d9_chart=d9_chart,
        d10_chart=d10_chart,
        d60_chart=d60_chart,
    )


def calculate_shodashvarga_from_horoscope_dict(horoscope_data: Dict[str, Any]) -> ShodashvargaResponse:
    """Helper to compute Shodashvarga directly from an existing horoscope calculation snapshot dictionary."""
    planets = horoscope_data.get("planets") or []
    ascendant = horoscope_data.get("ascendant") or {}
    metadata = horoscope_data.get("metadata") or {}
    return calculate_shodashvarga(planets=planets, ascendant=ascendant, metadata=metadata)

