"""Reusable calculation service for Four-Category Benefit Bhavas.

Order of Categories:
1. Star Lord Occupied House — the house occupied by the period lord's Nakshatra star lord.
2. Star Lord Owned Houses   — the houses owned by that star lord.
3. Period Lord Occupied House — the house occupied by the planet ruling the current period.
4. Period Lord Owned Houses   — the houses owned by the planet ruling the current period.

Rahu & Ketu Exception:
- Rahu and Ketu have no owned houses under the validated system convention.
- If the star lord is Rahu or Ketu, category 2 is omitted.
- If the period lord is Rahu or Ketu, category 4 is omitted.
- Only the applicable category is omitted; remaining categories are NOT shifted.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

# The 9 traditional grahas in Vimshottari order (used for nakshatra cycle)
VIMSHOTTARI_LORDS: Tuple[str, ...] = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
)

# Standard span of each Nakshatra in degrees (360° / 27)
NAKSHATRA_SPAN_DEG: float = 360.0 / 27.0  # 13° 20' = 13.333333333333334°

# Signs ruled by each planet under canonical Vedic / KP rules
# Rahu and Ketu do not own any signs.
SIGNS_RULED_BY: Dict[str, Tuple[str, ...]] = {
    "Sun": ("Leo",),
    "Moon": ("Cancer",),
    "Mars": ("Aries", "Scorpio"),
    "Mercury": ("Gemini", "Virgo"),
    "Jupiter": ("Sagittarius", "Pisces"),
    "Venus": ("Taurus", "Libra"),
    "Saturn": ("Capricorn", "Aquarius"),
    "Rahu": (),
    "Ketu": (),
}

# Sign to ruler mapping (1-indexed zodiac)
ZODIAC_SIGNS: Tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SIGN_LORDS: Dict[str, str] = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

PLANET_ALIASES: Dict[str, str] = {
    "sun": "Sun",
    "surya": "Sun",
    "su": "Sun",
    "moon": "Moon",
    "chandra": "Moon",
    "mo": "Moon",
    "mars": "Mars",
    "mangal": "Mars",
    "mangala": "Mars",
    "sevvai": "Mars",
    "ma": "Mars",
    "mercury": "Mercury",
    "budh": "Mercury",
    "budha": "Mercury",
    "me": "Mercury",
    "jupiter": "Jupiter",
    "guru": "Jupiter",
    "ju": "Jupiter",
    "venus": "Venus",
    "sukra": "Venus",
    "sukran": "Venus",
    "shukra": "Venus",
    "shukran": "Venus",
    "ve": "Venus",
    "saturn": "Saturn",
    "shani": "Saturn",
    "sani": "Saturn",
    "sa": "Saturn",
    "rahu": "Rahu",
    "ra": "Rahu",
    "ketu": "Ketu",
    "ke": "Ketu",
}


def normalize_planet_name(name: str) -> str:
    """Normalize any planet alias to canonical title-case English name."""
    if not name:
        return ""
    clean = name.strip().lower()
    return PLANET_ALIASES.get(clean, name.strip().title())


def resolve_star_lord(longitude: float) -> str:
    """Determine the Nakshatra star lord of any sidereal longitude [0, 360)."""
    norm = longitude % 360.0
    nak_idx = int(norm // NAKSHATRA_SPAN_DEG)
    return VIMSHOTTARI_LORDS[nak_idx % 9]


def house_of_longitude(lon: float, cusps: List[float]) -> int:
    """Calculate the house (1-12) containing a given longitude relative to 12 cusps.
    
    Compatible with Placidus, Equal, Koch, and WholeSign cusps.
    Uses relative modular offset from cusp 1 to avoid 0° boundary discontinuities.
    """
    if not cusps or len(cusps) < 12:
        return 1
    lon_norm = lon % 360.0
    c0 = cusps[0] % 360.0
    lon_rel = (lon_norm - c0) % 360.0

    for i in range(12):
        c_rel = (cusps[i] - c0) % 360.0
        nxt_rel = (cusps[i + 1] - c0) % 360.0 if i < 11 else 360.0
        if c_rel <= lon_rel < nxt_rel:
            return i + 1
    return 12


def get_planet_occupied_house(
    planet_lon: Optional[float],
    cusps: Optional[List[float]] = None,
    ascendant_sign_idx: Optional[int] = None,
    prefer_rashi: bool = True,
) -> Optional[int]:
    """Calculate the house occupied by a planet.
    
    In Vedic Vimshottari Dasa Benefit Bhavas, the planet's house occupancy
    is canonically determined by Rashi-Bhava (sign relative to the Ascendant sign).
    - If prefer_rashi is True and ascendant_sign_idx is provided, uses Rashi offset.
    - Otherwise, if cusps are provided (Placidus, Equal, etc.), uses house_of_longitude.
    - Fallback to Rashi offset if available.
    - If required data is missing, returns None (unavailable).
    """
    if planet_lon is None:
        return None

    if prefer_rashi and ascendant_sign_idx is not None and 1 <= ascendant_sign_idx <= 12:
        planet_sign = int((planet_lon % 360.0) // 30.0) + 1
        return ((planet_sign - ascendant_sign_idx + 12) % 12) + 1

    if cusps and len(cusps) >= 12:
        return house_of_longitude(planet_lon, cusps)

    if ascendant_sign_idx is not None and 1 <= ascendant_sign_idx <= 12:
        planet_sign = int((planet_lon % 360.0) // 30.0) + 1
        return ((planet_sign - ascendant_sign_idx + 12) % 12) + 1

    return None


def get_planet_owned_houses(
    planet_name: str,
    ascendant_sign_idx: Optional[int] = None,
    cusps: Optional[List[float]] = None,
    house_sign_names: Optional[List[str]] = None,
    prefer_rashi: bool = True,
) -> List[int]:
    """Calculate the houses owned by a planet.
    
    Rahu and Ketu own NO houses under the validated system convention (returns empty list).
    For other grahas:
    - If prefer_rashi is True and ascendant_sign_idx is provided (Canonical Vedic Rashi-Bhava),
      calculates rashi house offsets.
    - Else if house_sign_names is provided (from HoroscopeResponse.houses), finds houses where sign lord matches.
    - Fallback to WholeSign calculation from ascendant_sign_idx.
    Returns sorted list of 1-based house numbers.
    """
    canonical_planet = normalize_planet_name(planet_name)
    if canonical_planet in ("Rahu", "Ketu"):
        return []

    # Method 1: Canonical Vedic Rashi-Bhava from ascendant_sign_idx
    if prefer_rashi and ascendant_sign_idx is not None and 1 <= ascendant_sign_idx <= 12:
        owned_signs = SIGNS_RULED_BY.get(canonical_planet, ())
        owned = []
        for s_name in owned_signs:
            s_idx = ZODIAC_SIGNS.index(s_name) + 1
            h = ((s_idx - ascendant_sign_idx + 12) % 12) + 1
            owned.append(h)
        return sorted(owned)

    # Method 2: Cuspal sign names provided
    if house_sign_names and len(house_sign_names) == 12:
        owned = [
            h + 1
            for h, s_name in enumerate(house_sign_names)
            if SIGN_LORDS.get(s_name) == canonical_planet
        ]
        if owned:
            return sorted(owned)

    # Method 3: WholeSign calculation from ascendant_sign_idx
    if ascendant_sign_idx is not None and 1 <= ascendant_sign_idx <= 12:
        owned_signs = SIGNS_RULED_BY.get(canonical_planet, ())
        owned = []
        for s_name in owned_signs:
            s_idx = ZODIAC_SIGNS.index(s_name) + 1
            h = ((s_idx - ascendant_sign_idx + 12) % 12) + 1
            owned.append(h)
        return sorted(owned)

    return []


def format_benefit_bhavas(
    cat1_star_lord_occ: Optional[int],
    cat2_star_lord_own: List[int],
    cat3_period_lord_occ: Optional[int],
    cat4_period_lord_own: List[int],
    star_lord: str,
    period_lord: str,
) -> str:
    """Format available categories into compact pipe-separated string.
    
    Retains commas between multiple house numbers within the same category.
    Ommits category 2 if star_lord is Rahu or Ketu.
    Ommits category 4 if period_lord is Rahu or Ketu.
    Reports 'Unavailable' if an occupied house cannot be determined.
    """
    canonical_sl = normalize_planet_name(star_lord)
    canonical_pl = normalize_planet_name(period_lord)

    available_groups: List[str] = []

    # Category 1: Star Lord Occupied House
    if cat1_star_lord_occ is not None:
        available_groups.append(str(cat1_star_lord_occ))
    else:
        available_groups.append("Unavailable")

    # Category 2: Star Lord Owned Houses (OMITTED for Rahu and Ketu)
    if canonical_sl not in ("Rahu", "Ketu"):
        if cat2_star_lord_own:
            available_groups.append(", ".join(str(h) for h in sorted(cat2_star_lord_own)))
        else:
            available_groups.append("Unavailable")

    # Category 3: Period Lord Occupied House
    if cat3_period_lord_occ is not None:
        available_groups.append(str(cat3_period_lord_occ))
    else:
        available_groups.append("Unavailable")

    # Category 4: Period Lord Owned Houses (OMITTED for Rahu and Ketu)
    if canonical_pl not in ("Rahu", "Ketu"):
        if cat4_period_lord_own:
            available_groups.append(", ".join(str(h) for h in sorted(cat4_period_lord_own)))
        else:
            available_groups.append("Unavailable")

    return " | ".join(available_groups)


class BenefitBhavasResult(BaseModel):
    """Complete structured breakdown and display string for a period lord."""
    period_lord: str
    star_lord: str
    star_lord_occupied: Optional[int] = None
    star_lord_owned: List[int] = Field(default_factory=list)
    period_lord_occupied: Optional[int] = None
    period_lord_owned: List[int] = Field(default_factory=list)
    formatted: str


class PlanetChartContext(BaseModel):
    """Natal horoscope context for a single planet."""
    name: str
    longitude: float
    star_lord: str
    occupied_house: Optional[int] = None
    owned_houses: List[int] = Field(default_factory=list)


def build_horoscope_planet_contexts(
    planets: List[Any],
    ascendant_sign_idx: int,
    cusps: Optional[List[float]] = None,
    houses: Optional[List[Any]] = None,
    prefer_rashi: bool = True,
) -> Dict[str, PlanetChartContext]:
    """Build a fast lookup dictionary of PlanetChartContext for all grahas in a horoscope."""
    contexts: Dict[str, PlanetChartContext] = {}

    house_sign_names = [h.sign_name for h in houses] if houses and len(houses) == 12 else None

    # Index planets by normalized name
    raw_planet_map: Dict[str, Any] = {}
    for p in planets:
        name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else None)
        if name:
            raw_planet_map[normalize_planet_name(name)] = p

    for lord in VIMSHOTTARI_LORDS:
        p_obj = raw_planet_map.get(lord)
        lon = None
        star_lord = None

        if p_obj:
            lon = getattr(p_obj, "longitude", None)
            if lon is None and isinstance(p_obj, dict):
                lon = p_obj.get("longitude")

            # Check if nakshatra.lord already exists
            nak = getattr(p_obj, "nakshatra", None) or (p_obj.get("nakshatra") if isinstance(p_obj, dict) else None)
            if nak:
                star_lord = getattr(nak, "lord", None) or (nak.get("lord") if isinstance(nak, dict) else None)

        if lon is not None:
            if not star_lord:
                star_lord = resolve_star_lord(lon)
            occ_house = get_planet_occupied_house(
                lon,
                cusps=cusps,
                ascendant_sign_idx=ascendant_sign_idx,
                prefer_rashi=prefer_rashi,
            )
        else:
            occ_house = None
            star_lord = "Unknown"

        owned = get_planet_owned_houses(
            lord,
            ascendant_sign_idx=ascendant_sign_idx,
            cusps=cusps,
            house_sign_names=house_sign_names,
            prefer_rashi=prefer_rashi,
        )

        contexts[lord] = PlanetChartContext(
            name=lord,
            longitude=lon if lon is not None else 0.0,
            star_lord=star_lord or "Unknown",
            occupied_house=occ_house,
            owned_houses=owned,
        )

    return contexts


def calculate_benefit_bhavas(
    period_lord: str,
    planet_contexts: Dict[str, PlanetChartContext],
) -> BenefitBhavasResult:
    """Calculate Benefit Bhavas for a specific period lord given chart planet contexts."""
    canonical_pl = normalize_planet_name(period_lord)
    pl_context = planet_contexts.get(canonical_pl)

    if pl_context is None or pl_context.occupied_house is None:
        # Period lord data missing or incomplete
        star_lord = pl_context.star_lord if pl_context else "Unknown"
        return BenefitBhavasResult(
            period_lord=canonical_pl,
            star_lord=star_lord,
            star_lord_occupied=None,
            star_lord_owned=[],
            period_lord_occupied=None,
            period_lord_owned=[],
            formatted="Unavailable",
        )

    star_lord = pl_context.star_lord
    canonical_sl = normalize_planet_name(star_lord)
    sl_context = planet_contexts.get(canonical_sl)

    sl_occ = sl_context.occupied_house if sl_context else None
    sl_own = sl_context.owned_houses if sl_context else []
    pl_occ = pl_context.occupied_house
    pl_own = pl_context.owned_houses

    formatted = format_benefit_bhavas(
        cat1_star_lord_occ=sl_occ,
        cat2_star_lord_own=sl_own,
        cat3_period_lord_occ=pl_occ,
        cat4_period_lord_own=pl_own,
        star_lord=canonical_sl,
        period_lord=canonical_pl,
    )

    return BenefitBhavasResult(
        period_lord=canonical_pl,
        star_lord=canonical_sl,
        star_lord_occupied=sl_occ,
        star_lord_owned=sl_own if canonical_sl not in ("Rahu", "Ketu") else [],
        period_lord_occupied=pl_occ,
        period_lord_owned=pl_own if canonical_pl not in ("Rahu", "Ketu") else [],
        formatted=formatted,
    )


def enrich_dasa_tree(
    dasa_tree: List[Any],
    planet_contexts: Dict[str, PlanetChartContext],
) -> None:
    """Recursively enrich all nodes at all 5 Dasa levels with independent Benefit Bhavas.
    
    Never copies a parent's Benefit Bhavas into a child period.
    """
    for node in dasa_tree:
        lord = getattr(node, "lord", None) or (node.get("lord") if isinstance(node, dict) else None)
        if lord:
            res = calculate_benefit_bhavas(lord, planet_contexts)
            if isinstance(node, dict):
                node["star_lord"] = res.star_lord
                node["benefit_bhavas"] = res.formatted
                node["period_lord_occupied"] = res.period_lord_occupied
                node["star_lord_occupied"] = res.star_lord_occupied
                node["period_lord_owned"] = res.period_lord_owned
                node["star_lord_owned"] = res.star_lord_owned
            else:
                setattr(node, "star_lord", res.star_lord)
                setattr(node, "benefit_bhavas", res.formatted)
                setattr(node, "period_lord_occupied", res.period_lord_occupied)
                setattr(node, "star_lord_occupied", res.star_lord_occupied)
                setattr(node, "period_lord_owned", res.period_lord_owned)
                setattr(node, "star_lord_owned", res.star_lord_owned)

        sub_periods = getattr(node, "sub_periods", None) or (node.get("sub_periods") if isinstance(node, dict) else None)
        if sub_periods:
            enrich_dasa_tree(sub_periods, planet_contexts)
