"""KP Event Prediction Engine - Signification Normalizer.

Validates and normalizes planetary names, house numbers (1-12), and
4-tier strength levels (L1=4, L2=3, L3=2, L4=1). Ensures L1 overrides
L2, L3, and L4 for the same house, and extracts clean significations
directly from the existing KP calculation engine without inventing data.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, Any

LEVEL_WEIGHTS: Dict[str, int] = {
    "L1": 4,
    "L2": 3,
    "L3": 2,
    "L4": 1,
}

WEIGHT_TO_LEVEL: Dict[int, str] = {
    4: "L1",
    3: "L2",
    2: "L3",
    1: "L4",
}

CANONICAL_PLANETS: Dict[str, str] = {
    "sun": "Sun",
    "su": "Sun",
    "surya": "Sun",
    "suryan": "Sun",
    "ravi": "Sun",
    "moon": "Moon",
    "mo": "Moon",
    "chandra": "Moon",
    "chandran": "Moon",
    "mars": "Mars",
    "ma": "Mars",
    "mangal": "Mars",
    "mangala": "Mars",
    "sevvai": "Mars",
    "mercury": "Mercury",
    "me": "Mercury",
    "budh": "Mercury",
    "budha": "Mercury",
    "budhan": "Mercury",
    "jupiter": "Jupiter",
    "ju": "Jupiter",
    "guru": "Jupiter",
    "vyazhan": "Jupiter",
    "venus": "Venus",
    "ve": "Venus",
    "sukra": "Venus",
    "sukran": "Venus",
    "shukra": "Venus",
    "shukran": "Venus",
    "saturn": "Saturn",
    "sa": "Saturn",
    "shani": "Saturn",
    "sani": "Saturn",
    "saniswaran": "Saturn",
    "rahu": "Rahu",
    "ra": "Rahu",
    "ragu": "Rahu",
    "ketu": "Ketu",
    "ke": "Ketu",
    "kethu": "Ketu",
}


def normalize_planet_name(raw_name: Optional[str]) -> Optional[str]:
    """Normalize graha name to standard title case (e.g., 'jupiter' -> 'Jupiter')."""
    if not raw_name:
        return None
    cleaned = raw_name.strip().lower()
    return CANONICAL_PLANETS.get(cleaned) or raw_name.strip().capitalize()


def normalize_strength_level(raw_level: Any) -> Optional[str]:
    """Normalize strength level string or integer to 'L1', 'L2', 'L3', 'L4'."""
    if isinstance(raw_level, int):
        return WEIGHT_TO_LEVEL.get(raw_level)
    if isinstance(raw_level, str):
        cleaned = raw_level.strip().upper()
        if cleaned in LEVEL_WEIGHTS:
            return cleaned
        # Support Tier A, B, C, D mapping
        tier_map = {"A": "L1", "TIER_A": "L1", "B": "L2", "TIER_B": "L2", "C": "L3", "TIER_C": "L3", "D": "L4", "TIER_D": "L4"}
        if cleaned in tier_map:
            return tier_map[cleaned]
    return None


def derive_planet_house_significations(
    raw_significations: Any,
) -> Dict[str, Dict[int, str]]:
    """Normalizes input significations into a canonical mapping:
    planet -> {house_number (1-12): level ('L1' | 'L2' | 'L3' | 'L4')}.

    Guarantees that when the same planet signifies a house at multiple levels,
    the highest strength level (L1 > L2 > L3 > L4) strictly overrides lower levels.
    """
    normalized: Dict[str, Dict[int, str]] = {}

    if not raw_significations:
        return normalized

    # Case A: Dict of planet -> list of house entries or dict of houses
    if isinstance(raw_significations, dict):
        for planet_key, house_entries in raw_significations.items():
            planet = normalize_planet_name(str(planet_key))
            if not planet:
                continue
            p_map = normalized.setdefault(planet, {})

            if isinstance(house_entries, list):
                for entry in house_entries:
                    h: Optional[int] = None
                    lvl: Optional[str] = None
                    if isinstance(entry, dict):
                        h_val = entry.get("house") or entry.get("house_number")
                        if h_val is not None and 1 <= int(h_val) <= 12:
                            h = int(h_val)
                        lvl = normalize_strength_level(entry.get("level") or entry.get("tier") or entry.get("weight"))
                    elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                        if 1 <= int(entry[0]) <= 12:
                            h = int(entry[0])
                        lvl = normalize_strength_level(entry[1])

                    if h is not None and lvl is not None:
                        curr_lvl = p_map.get(h)
                        if curr_lvl is None or LEVEL_WEIGHTS[lvl] > LEVEL_WEIGHTS[curr_lvl]:
                            p_map[h] = lvl

            elif isinstance(house_entries, dict):
                for h_key, lvl_val in house_entries.items():
                    try:
                        h = int(h_key)
                        if not (1 <= h <= 12):
                            continue
                    except (ValueError, TypeError):
                        continue
                    lvl = normalize_strength_level(lvl_val)
                    if lvl:
                        curr_lvl = p_map.get(h)
                        if curr_lvl is None or LEVEL_WEIGHTS[lvl] > LEVEL_WEIGHTS[curr_lvl]:
                            p_map[h] = lvl

    # Case B: List of HouseSignificatorEntry (from KpResponse.house_significators)
    elif isinstance(raw_significations, list):
        for item in raw_significations:
            # item can be dict or Pydantic HouseSignificatorEntry
            h_val = getattr(item, "house", None) if hasattr(item, "house") else (item.get("house") if isinstance(item, dict) else None)
            if h_val is None or not (1 <= int(h_val) <= 12):
                continue
            h = int(h_val)

            level_a = getattr(item, "level_a", None) if hasattr(item, "level_a") else (item.get("level_a") if isinstance(item, dict) else None) or []
            level_b = getattr(item, "level_b", None) if hasattr(item, "level_b") else (item.get("level_b") if isinstance(item, dict) else None) or []
            level_c = getattr(item, "level_c", None) if hasattr(item, "level_c") else (item.get("level_c") if isinstance(item, dict) else None) or []
            level_d = getattr(item, "level_d", None) if hasattr(item, "level_d") else (item.get("level_d") if isinstance(item, dict) else None) or []

            def record(planet_list: List[str], lvl: str):
                for p_raw in planet_list:
                    p = normalize_planet_name(p_raw)
                    if not p:
                        continue
                    p_map = normalized.setdefault(p, {})
                    curr_lvl = p_map.get(h)
                    if curr_lvl is None or LEVEL_WEIGHTS[lvl] > LEVEL_WEIGHTS[curr_lvl]:
                        p_map[h] = lvl

            record(level_a, "L1")
            record(level_b, "L2")
            record(level_c, "L3")
            record(level_d, "L4")

    return normalized


def derive_cusp_sub_lords_from_chart(kp_data: Any) -> Dict[int, str]:
    """Extracts cuspal sub-lords (1-12) from KpResponse or cuspal analysis."""
    csl_map: Dict[int, str] = {}
    if not kp_data:
        return csl_map

    cusp_list = getattr(kp_data, "cuspal_analysis", None)
    if cusp_list is None and isinstance(kp_data, dict):
        cusp_list = kp_data.get("cuspal_analysis") or kp_data.get("cusps")

    if isinstance(cusp_list, list):
        for item in cusp_list:
            h = getattr(item, "house", None) if hasattr(item, "house") else (item.get("house") if isinstance(item, dict) else None)
            sl = getattr(item, "sub_lord", None) if hasattr(item, "sub_lord") else (item.get("sub_lord") if isinstance(item, dict) else None)
            if h is not None and sl:
                p = normalize_planet_name(str(sl))
                if p:
                    csl_map[int(h)] = p

    # Also check house_significators for sub_lord
    if len(csl_map) < 12:
        house_sigs = getattr(kp_data, "house_significators", None)
        if house_sigs is None and isinstance(kp_data, dict):
            house_sigs = kp_data.get("house_significators")
        if isinstance(house_sigs, list):
            for item in house_sigs:
                h = getattr(item, "house", None) if hasattr(item, "house") else (item.get("house") if isinstance(item, dict) else None)
                sl = getattr(item, "sub_lord", None) if hasattr(item, "sub_lord") else (item.get("sub_lord") if isinstance(item, dict) else None)
                if h is not None and sl and int(h) not in csl_map:
                    p = normalize_planet_name(str(sl))
                    if p:
                        csl_map[int(h)] = p

    return csl_map


def extract_retrograde_status_from_chart(
    horoscope_data: Any,
    kp_data: Optional[Any] = None,
) -> Dict[str, bool]:
    """Extracts retrograde status for each planet from horoscope or KP chart."""
    retro_map: Dict[str, bool] = {
        "Sun": False,
        "Moon": False,
        "Mars": False,
        "Mercury": False,
        "Jupiter": False,
        "Venus": False,
        "Saturn": False,
        "Rahu": True,  # Lunar nodes always retrograde in mean motion
        "Ketu": True,
    }

    # 1. Inspect horoscope planets
    planets_list = None
    if horoscope_data:
        planets_list = getattr(horoscope_data, "planets", None)
        if planets_list is None and isinstance(horoscope_data, dict):
            planets_list = horoscope_data.get("planets")

    if isinstance(planets_list, list):
        for p in planets_list:
            name = getattr(p, "name", None) if hasattr(p, "name") else (p.get("name") if isinstance(p, dict) else None)
            is_ret = getattr(p, "is_retrograde", None) if hasattr(p, "is_retrograde") else (p.get("is_retrograde") if isinstance(p, dict) else None)
            norm_p = normalize_planet_name(name)
            if norm_p and is_ret is not None:
                retro_map[norm_p] = bool(is_ret)

    # 2. Also inspect KP planetary positions if speed or retrograde is present
    if kp_data:
        kp_positions = getattr(kp_data, "planetary_positions", None)
        if kp_positions is None and isinstance(kp_data, dict):
            kp_positions = kp_data.get("planetary_positions")
        if isinstance(kp_positions, list):
            for p in kp_positions:
                name = getattr(p, "planet", None) if hasattr(p, "planet") else (p.get("planet") if isinstance(p, dict) else None)
                is_ret = getattr(p, "retrograde", None) if hasattr(p, "retrograde") else (p.get("retrograde") if isinstance(p, dict) else None)
                norm_p = normalize_planet_name(name)
                if norm_p and is_ret is not None:
                    retro_map[norm_p] = bool(is_ret)

    return retro_map


def validate_mandatory_lords_significations(
    mahadasha_lord: Optional[str],
    bhukti_lord: Optional[str],
    significations: Dict[str, Dict[int, str]],
) -> Tuple[bool, List[str]]:
    """Checks whether Mahadasha and Bhukti lords are present and have valid significations.
    Returns (is_valid, missing_fields).
    """
    missing: List[str] = []
    norm_md = normalize_planet_name(mahadasha_lord)
    norm_bd = normalize_planet_name(bhukti_lord)

    if not norm_md:
        missing.append("mahadasha_lord")
    elif norm_md not in significations or not significations[norm_md]:
        missing.append(f"significations for Mahadasha lord ({norm_md})")

    if not norm_bd:
        missing.append("bhukti_lord")
    elif norm_bd not in significations or not significations[norm_bd]:
        missing.append(f"significations for Bhukti lord ({norm_bd})")

    return (len(missing) == 0, missing)
