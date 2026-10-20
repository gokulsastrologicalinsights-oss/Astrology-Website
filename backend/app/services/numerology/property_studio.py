"""House, Flat & Property Numerology Engine.

Provides deterministic numerological and architectural alignment analysis for real estate:
1. Property Categories & Usages:
   - Independent houses, villas, apartments, flats, commercial offices, shops, plots/land, multi-unit buildings.
   - Tenure: Purchased (freehold/long-term) vs Rental (lease/tenancy).
   - Usages: Residential living, commercial trade, rental investment, creative studio, spiritual wellness.
2. Component Parsing & Separate Calculations:
   - Door / Flat number (micro intimate energy).
   - Building / Tower number (collective community structure).
   - Floor number (vertical elemental elevation).
   - Plot number (earth anchoring vibration).
   - Combined property formula (transparent arithmetic sum of active components).
   - Full alphanumeric property identifier (including project/building name via Chaldean or Pythagorean).
3. Vibrational Archetypes & Master Numbers:
   - Numbers 1-9 and Master Numbers 11, 22, 33 with domestic/commercial architectural archetypes.
4. Traditional Vastu Shastra Directional Alignment:
   - 8 Cardinal and Intercardinal orientations (North, North-East, East, South-East, South, South-West, West, North-West)
     mapping to classical deities, elements, and ruling planets.
5. Resident & Family Compatibility:
   - Primary owner and co-residents' Psychic (Birth) and Life Path number alignment.
   - Household collective harmony scoring.
6. Multi-Property Comparison & Ranking:
   - Deterministic ranking of up to 25 property candidates.
7. Ethical Disclaimers:
   - Symbolic and philosophical exploration tool. Does not guarantee wealth, safety, structural integrity,
     legal clearance, or official availability.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from .traditional import (
    reduce_number,
    reduce_number_steps,
    get_ruling_planet,
    PYTHAGOREAN_MAP,
    CHALDEAN_MAP,
    calculate_birth_psychic_number,
    calculate_life_path_detailed,
)
from .name_studio import assess_number_harmony


# ------------------------------------------------------------------------------
# 1. Classical Vastu Directional Reference
# ------------------------------------------------------------------------------

VASTU_DIRECTIONS_MAP: Dict[str, Dict[str, Any]] = {
    "North": {
        "sanskrit": "Uttara",
        "deity": "Kubera (Lord of Wealth)",
        "element": "Water (Jala)",
        "ruling_planet": "Mercury (Budha)",
        "energy_type": "Prosperity, cash flow, mental clarity, and commercial opportunity.",
        "favorable_numbers": [1, 5, 6],
    },
    "North-East": {
        "sanskrit": "Ishanya",
        "deity": "Shiva / Ishana (Supreme Cosmic Intelligence)",
        "element": "Water / Ether (Jala-Akasha)",
        "ruling_planet": "Jupiter (Guru)",
        "energy_type": "Spiritual grace, academic wisdom, family health, and holistic harmony.",
        "favorable_numbers": [3, 1, 9],
    },
    "East": {
        "sanskrit": "Purva",
        "deity": "Indra / Surya (Vitality & Social Prominence)",
        "element": "Fire / Air (Agni-Vayu)",
        "ruling_planet": "Sun (Surya)",
        "energy_type": "Physical vitality, executive prestige, government recognition, and family honor.",
        "favorable_numbers": [1, 3, 5],
    },
    "South-East": {
        "sanskrit": "Agneya",
        "deity": "Agni (Cosmic Fire of Transformation)",
        "element": "Fire (Agni)",
        "ruling_planet": "Venus (Shukra)",
        "energy_type": "Vital drive, financial passion, culinary richness, and creative ambition.",
        "favorable_numbers": [6, 9, 1],
    },
    "South": {
        "sanskrit": "Dakshina",
        "deity": "Yama (Righteousness & Order)",
        "element": "Earth / Fire (Prithvi-Agni)",
        "ruling_planet": "Mars (Mangala)",
        "energy_type": "Discipline, structural endurance, decisive leadership, and sound boundary control.",
        "favorable_numbers": [9, 8, 3],
    },
    "South-West": {
        "sanskrit": "Nairrutya",
        "deity": "Nirriti / Pitrus (Ancestral Grounding & Stability)",
        "element": "Earth (Prithvi)",
        "ruling_planet": "Rahu",
        "energy_type": "Heavy anchoring, master stability, relationship longevity, and accumulated wealth retention.",
        "favorable_numbers": [4, 8, 6],
    },
    "West": {
        "sanskrit": "Pashchima",
        "deity": "Varuna (Cosmic Ocean & Material Fruition)",
        "element": "Air / Water (Vayu-Jala)",
        "ruling_planet": "Saturn (Shani)",
        "energy_type": "Material gains, commercial harvesting, sustained industry, and social networking.",
        "favorable_numbers": [8, 5, 7],
    },
    "North-West": {
        "sanskrit": "Vayavya",
        "deity": "Vayu (Wind & Movement)",
        "element": "Air (Vayu)",
        "ruling_planet": "Moon (Chandra)",
        "energy_type": "Speedy transition, communication, travel, guests, and beneficial commercial turnover.",
        "favorable_numbers": [2, 5, 7],
    },
}


# ------------------------------------------------------------------------------
# 2. Property Vibrational Archetypes (1-9 & 11, 22, 33)
# ------------------------------------------------------------------------------

PROPERTY_VIBRATIONAL_ARCHETYPES: Dict[int, Dict[str, str]] = {
    1: {
        "keyword": "Leadership, Independence & Pioneer Spirit",
        "effect": "Resonates with the Sun. Fosters strong individuality, decisive authority, executive presence, and self-made ambition. Highly beneficial for entrepreneurs, senior executives, and solo innovators. Best kept bright, uncluttered, and open to morning sunlight.",
    },
    2: {
        "keyword": "Harmony, Serenity & Nurturing Peace",
        "effect": "Resonates with the Moon. Radiates gentle warmth, emotional sensitivity, warm domestic hospitality, and peaceful cohabitation. Ideal for young families, counseling spaces, and romantic retreats. Favors comfortable furnishings, soft pastel tones, and soothing water elements.",
    },
    3: {
        "keyword": "Expansion, Optimism & Creative Abundance",
        "effect": "Resonates with Jupiter (Guru). Fosters joyful celebration, creative productivity, educational pursuits, and expansive horizons. Excellent for growing families, teachers, writers, artists, and homes where guests and children frequently gather.",
    },
    4: {
        "keyword": "Stability, Security & Grounded Foundation",
        "effect": "Resonates with Rahu / Uranus. Represents solid brick-and-mortar stability, physical security, organized routine, and pragmatic durability. Encourages steady wealth accumulation through disciplined labor. Demands regular structural maintenance and mindful decluttering.",
    },
    5: {
        "keyword": "Dynamism, Adaptability & Commercial Flow",
        "effect": "Resonates with Mercury (Budha). Characterized by high energy, frequent travel, lively communication, and social adaptability. Highly suited for digital nomads, sales professionals, lively urban apartments, and shared enterprise hubs.",
    },
    6: {
        "keyword": "Luxury, Domestic Warmth & Aesthetic Grace",
        "effect": "Resonates with Venus (Shukra). The quintessential home vibration; radiates aesthetic beauty, loving relationships, family solidarity, comfort, and gracious hospitality. Perfect for long-term family residences, pet lovers, beautiful gardens, and interior design enthusiasts.",
    },
    7: {
        "keyword": "Contemplation, Sanctuary & Inner Wisdom",
        "effect": "Resonates with Ketu / Neptune. A tranquil, introspective haven supporting deep meditation, philosophical study, psychological healing, and quiet research. Excellent for spiritual practitioners, writers, and analysts who require serene personal space away from public clamor.",
    },
    8: {
        "keyword": "Authority, Executive Power & Material Legacy",
        "effect": "Resonates with Saturn (Shani). Embodies monumental prestige, corporate governance, financial mastery, and generational legacy. Favors large estates, corporate headquarters, and ambitious leaders who act with unwavering ethical discipline and patience.",
    },
    9: {
        "keyword": "Courage, Humanitarian Warmth & Global Reach",
        "effect": "Resonates with Mars (Mangala). Radiates energetic vitality, generous community spirit, dynamic completion of projects, and universal goodwill. Suited for healthcare professionals, social leaders, teachers, and active individuals committed to inspiring the world.",
    },
    11: {
        "keyword": "Master Intuition & Elevated Sanctuary",
        "effect": "Master Number 11 brings acute intuitive clarity, creative inspiration, and an elevated energetic frequency. Functions best as an enlightened sanctuary for artists, spiritual visionaries, and healers who maintain a clean, peaceful atmosphere.",
    },
    22: {
        "keyword": "Master Architecture & Global Enterprise",
        "effect": "Master Number 22 embodies large-scale vision, institutional development, and structural mastery. Suited for significant residential estates, architectural firms, community foundations, and leaders building enduring societal infrastructure.",
    },
    33: {
        "keyword": "Master Blessing & Protective Service",
        "effect": "Master Number 33 radiates profound compassionate protection, universal love, and selfless hospitality. Creates a safe haven that uplifts everyone who crosses the threshold, favoring philanthropic endeavors and deeply caring family environments.",
    },
}


# ------------------------------------------------------------------------------
# 3. Property Usages Archetypes & Planetary Rulers
# ------------------------------------------------------------------------------

PROPERTY_USE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "residential_living": {
        "name": "Residential & Family Living",
        "primary_numbers": [2, 6, 3],
        "secondary_numbers": [1, 9],
        "planetary_rulers": "Venus (6), Moon (2), Jupiter (3)",
        "description": "Favors peaceful domestic harmony, health, mutual care, restful sleep, and loving family relationships.",
    },
    "commercial_business": {
        "name": "Commercial Office & Workspace",
        "primary_numbers": [1, 5, 8],
        "secondary_numbers": [3, 9],
        "planetary_rulers": "Sun (1), Mercury (5), Saturn (8)",
        "description": "Favors professional authority, executive dealmaking, commercial revenue, client acquisition, and enterprise scaling.",
    },
    "rental_investment": {
        "name": "Rental & Capital Investment",
        "primary_numbers": [8, 6, 4],
        "secondary_numbers": [5, 1],
        "planetary_rulers": "Saturn (8), Venus (6), Rahu (4)",
        "description": "Favors consistent rental yield, tenant longevity, asset appreciation, and solid physical property preservation.",
    },
    "creative_studio": {
        "name": "Creative Studio & Innovation Hub",
        "primary_numbers": [3, 5, 1],
        "secondary_numbers": [6, 11],
        "planetary_rulers": "Jupiter (3), Mercury (5), Sun (1)",
        "description": "Favors breakthrough creative inspiration, digital innovation, artistic production, and lively expressive work.",
    },
    "spiritual_wellness": {
        "name": "Spiritual Haven & Wellness Clinic",
        "primary_numbers": [7, 9, 2],
        "secondary_numbers": [3, 33],
        "planetary_rulers": "Ketu (7), Mars/Jupiter (9/3), Moon (2)",
        "description": "Favors holistic healing, meditation, psychological sanctuary, yoga therapy, and profound restful contemplation.",
    },
}


# ------------------------------------------------------------------------------
# 4. Character Mapping & Numerical Engine
# ------------------------------------------------------------------------------

def calculate_property_character_mapping(
    target_string: str,
    convention: str = "chaldean",
) -> Tuple[List[Dict[str, Any]], int]:
    """Map each character (letters and digits) to its numerical value according to chosen convention.

    In both Pythagorean and Chaldean systems:
    - Digits '0'-'9' keep their face numerical value.
    - Letters 'A'-'Z' are mapped via PYTHAGOREAN_MAP (1-9) or CHALDEAN_MAP (1-8).
    - Punctuation, slashes, hash signs, and spaces have value 0 and are omitted.

    Returns:
        Tuple of (mappings_list, total_sum)
    """
    map_dict = CHALDEAN_MAP if convention.lower() == "chaldean" else PYTHAGOREAN_MAP
    mappings: List[Dict[str, Any]] = []
    total_sum = 0

    clean_str = re.sub(r"[^A-Z0-9]", "", target_string.upper())

    for char in clean_str:
        if char.isdigit():
            val = int(char)
            char_type = "digit"
        elif char in map_dict:
            val = map_dict[char]
            char_type = "letter"
        else:
            val = 0
            char_type = "unknown"

        mappings.append({
            "char": char,
            "value": val,
            "type": char_type,
        })
        total_sum += val

    return mappings, total_sum


def analyze_property_component(
    source_str: str,
    component_name: str,
    component_label: str,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Calculate transparent numerical reduction for a single property component."""
    if not source_str or not source_str.strip():
        return {
            "component_name": component_name,
            "component_label": component_label,
            "calculation_mode": component_name,
            "source_string": "",
            "included_characters": [],
            "character_mappings": [],
            "compound_sum": 0,
            "root_number": 0,
            "single_root": 0,
            "is_master": False,
            "reduction_steps": ["0"],
            "ruling_planet": "None",
            "keyword": "Unspecified Component",
            "vibrational_meaning": "This property component was not provided.",
        }

    clean_input = source_str.strip()
    mappings, compound_sum = calculate_property_character_mapping(clean_input, convention)

    root_num, reduction_steps = reduce_number_steps(compound_sum, preserve_master=True)
    single_root = reduce_number(root_num, preserve_master=False)
    is_master = root_num in (11, 22, 33)

    planet_data = get_ruling_planet(root_num) if root_num > 0 else {"en": "Neutral"}
    planet_name = planet_data.get("en", str(planet_data)) if isinstance(planet_data, dict) else str(planet_data)

    archetype = PROPERTY_VIBRATIONAL_ARCHETYPES.get(
        root_num,
        PROPERTY_VIBRATIONAL_ARCHETYPES.get(single_root, PROPERTY_VIBRATIONAL_ARCHETYPES[1]),
    )

    parts_expr = " + ".join([f"{m['char']}({m['value']})" for m in mappings]) if mappings else "0"
    formula_step = f"{parts_expr} = {compound_sum}"

    all_steps = [formula_step]
    if reduction_steps and reduction_steps[0] != str(compound_sum):
        all_steps.extend(reduction_steps)
    elif len(reduction_steps) > 1:
        all_steps.extend(reduction_steps[1:])

    return {
        "component_name": component_name,
        "component_label": component_label,
        "calculation_mode": component_name,
        "source_string": clean_input,
        "included_characters": [m["char"] for m in mappings],
        "character_mappings": mappings,
        "compound_sum": compound_sum,
        "root_number": root_num,
        "single_root": single_root,
        "is_master": is_master,
        "reduction_steps": all_steps,
        "ruling_planet": planet_name,
        "keyword": archetype["keyword"],
        "vibrational_meaning": archetype["effect"],
    }


# ------------------------------------------------------------------------------
# 5. Combined Property Formula & Synthesis Engine
# ------------------------------------------------------------------------------

def calculate_combined_property_formula(
    door_res: Dict[str, Any],
    building_res: Dict[str, Any],
    floor_res: Dict[str, Any],
    plot_res: Dict[str, Any],
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Calculate transparent Combined Property vibration.

    Formula Convention:
    Sum of all active, non-empty components' unreduced totals:
    Combined Total = Door Compound + Floor Compound + Building Compound + Plot Compound
    Reduction then reduces this total to its root vibration (preserving master numbers 11, 22, 33).
    """
    active_components: List[Tuple[str, int]] = []
    if door_res["compound_sum"] > 0:
        active_components.append(("Door " + door_res["source_string"], door_res["compound_sum"]))
    if floor_res["compound_sum"] > 0:
        active_components.append(("Floor " + floor_res["source_string"], floor_res["compound_sum"]))
    if building_res["compound_sum"] > 0:
        active_components.append(("Building " + building_res["source_string"], building_res["compound_sum"]))
    if plot_res["compound_sum"] > 0:
        active_components.append(("Plot " + plot_res["source_string"], plot_res["compound_sum"]))

    if not active_components:
        # Fallback if no components provided
        return {
            "component_name": "combined_property",
            "component_label": "Combined Property Formula",
            "source_string": "No components specified",
            "included_characters": [],
            "character_mappings": [],
            "compound_sum": 0,
            "root_number": 0,
            "single_root": 0,
            "is_master": False,
            "reduction_steps": ["0"],
            "ruling_planet": "None",
            "keyword": "Unspecified Property",
            "vibrational_meaning": "No numerical components were available to synthesize.",
            "formula_explanation": "Combined Property = 0",
        }

    compound_sum = sum(val for _, val in active_components)
    root_num, reduction_steps = reduce_number_steps(compound_sum, preserve_master=True)
    single_root = reduce_number(root_num, preserve_master=False)
    is_master = root_num in (11, 22, 33)

    planet_data = get_ruling_planet(root_num) if root_num > 0 else {"en": "Neutral"}
    planet_name = planet_data.get("en", str(planet_data)) if isinstance(planet_data, dict) else str(planet_data)

    archetype = PROPERTY_VIBRATIONAL_ARCHETYPES.get(
        root_num,
        PROPERTY_VIBRATIONAL_ARCHETYPES.get(single_root, PROPERTY_VIBRATIONAL_ARCHETYPES[1]),
    )

    comp_expr = " + ".join([f"{name}({val})" for name, val in active_components])
    formula_step = f"{comp_expr} = {compound_sum}"

    all_steps = [formula_step]
    if reduction_steps and reduction_steps[0] != str(compound_sum):
        all_steps.extend(reduction_steps)
    elif len(reduction_steps) > 1:
        all_steps.extend(reduction_steps[1:])

    all_chars: List[str] = []
    for c_res in (door_res, floor_res, building_res, plot_res):
        all_chars.extend(c_res["included_characters"])

    return {
        "component_name": "combined_property",
        "component_label": "Combined Property Formula",
        "calculation_mode": "combined_property",
        "source_string": ", ".join([f"{name}" for name, _ in active_components]),
        "included_characters": all_chars,
        "character_mappings": [],
        "compound_sum": compound_sum,
        "root_number": root_num,
        "single_root": single_root,
        "is_master": is_master,
        "reduction_steps": all_steps,
        "ruling_planet": planet_name,
        "keyword": archetype["keyword"],
        "vibrational_meaning": archetype["effect"],
        "formula_explanation": (
            "Synthesizes door threshold, floor level, building shell, and plot soil into an overarching "
            f"dwelling vibration under {convention.capitalize()} conventions."
        ),
    }


# ------------------------------------------------------------------------------
# 6. Usage & Vastu Directional Evaluation
# ------------------------------------------------------------------------------

def evaluate_property_usage_harmony(property_root: int, usage_type: str = "residential_living") -> Dict[str, Any]:
    """Score resonance of the property's root number with its intended usage archetype."""
    use_key = usage_type.lower() if usage_type.lower() in PROPERTY_USE_ARCHETYPES else "residential_living"
    archetype = PROPERTY_USE_ARCHETYPES[use_key]

    single_root = reduce_number(property_root, preserve_master=False)

    if single_root in archetype["primary_numbers"]:
        score = 95.0
        level = "Optimal Archetypal Match"
        desc = f"Number {property_root} is an exemplary match for {archetype['name']}, channeling {archetype['planetary_rulers']}."
    elif single_root in archetype["secondary_numbers"]:
        score = 80.0
        level = "Favorable Alignment"
        desc = f"Number {property_root} provides strong complementary support for {archetype['name']}."
    elif single_root == 4 or single_root == 8:
        score = 65.0
        level = "Pragmatic Foundation (Requires Maintenance)"
        desc = f"Number {property_root} offers structured longevity; periodic repairs and disciplined spatial order are recommended."
    else:
        score = 55.0
        level = "Moderate General Resonance"
        desc = f"Number {property_root} operates neutrally for {archetype['name']}."

    return {
        "property_usage": use_key,
        "usage_name": archetype["name"],
        "planetary_rulers": archetype["planetary_rulers"],
        "primary_numbers": archetype["primary_numbers"],
        "secondary_numbers": archetype["secondary_numbers"],
        "score": score,
        "level": level,
        "description": desc,
    }


def evaluate_property_vastu_facing(facing_direction: Optional[str], property_root: int) -> Optional[Dict[str, Any]]:
    """Evaluate Vastu orientation harmony with property vibration."""
    if not facing_direction or not facing_direction.strip():
        return None

    # Normalize direction string: e.g. 'north', 'northeast', 'north-east', 'NE', 'N'
    dir_clean = facing_direction.strip()
    matched_dir: Optional[str] = None

    for k in VASTU_DIRECTIONS_MAP.keys():
        if k.lower() == dir_clean.lower() or k.lower().replace("-", "") == dir_clean.lower().replace("-", ""):
            matched_dir = k
            break

    if not matched_dir:
        # Check abbreviations
        abbr_map = {
            "N": "North", "NE": "North-East", "E": "East", "SE": "South-East",
            "S": "South", "SW": "South-West", "W": "West", "NW": "North-West",
        }
        matched_dir = abbr_map.get(dir_clean.upper())

    if not matched_dir:
        return None

    vastu_info = VASTU_DIRECTIONS_MAP[matched_dir]
    single_root = reduce_number(property_root, preserve_master=False)

    if single_root in vastu_info["favorable_numbers"]:
        alignment_score = 95.0
        alignment_level = "High Vastu Resonance"
        notes = f"Property root {property_root} synergizes naturally with {matched_dir} ({vastu_info['sanskrit']}), governed by {vastu_info['deity']}."
    else:
        alignment_score = 70.0
        alignment_level = "Balanced Elemental Compatibility"
        notes = f"Property root {property_root} operates in healthy elemental balance with {matched_dir} ({vastu_info['element']})."

    return {
        "facing_direction": matched_dir,
        "sanskrit_name": vastu_info["sanskrit"],
        "presiding_deity": vastu_info["deity"],
        "element": vastu_info["element"],
        "ruling_planet": vastu_info["ruling_planet"],
        "energy_type": vastu_info["energy_type"],
        "alignment_score": alignment_score,
        "alignment_level": alignment_level,
        "notes": notes,
    }


# ------------------------------------------------------------------------------
# 7. Resident & Family Compatibility
# ------------------------------------------------------------------------------

def evaluate_single_resident_compatibility(
    property_root: int,
    birth_date_str: str,
    name: str = "Resident",
    is_primary: bool = True,
    role: str = "Primary Resident",
) -> Dict[str, Any]:
    """Compare property root number against a resident's Psychic and Life Path numbers."""
    psychic_val, _, _ = calculate_birth_psychic_number(birth_date_str)
    lp_res = calculate_life_path_detailed(birth_date_str)
    lp_val = lp_res["life_path"]

    score_psychic, psychic_desc = assess_number_harmony(property_root, psychic_val)
    score_lp, lp_desc = assess_number_harmony(property_root, lp_val)

    # 50% Psychic harmony (daily domestic comfort & mood) + 50% Life Path (long-term life destiny)
    personal_score = round((score_psychic * 0.5) + (score_lp * 0.5), 1)

    level = (
        "Harmonious" if personal_score >= 80.0
        else "Complementary" if personal_score >= 60.0
        else "Neutral" if personal_score >= 45.0
        else "Tension"
    )

    synthesis = (
        f"Property vibration {property_root} aligns with {name}'s Psychic {psychic_val} ({psychic_desc}) "
        f"and Life Path {lp_val} ({lp_desc}). Alignment: {level} ({personal_score}%)."
    )

    return {
        "name": name,
        "birth_date": birth_date_str,
        "is_primary": is_primary,
        "role": role,
        "psychic_number": psychic_val,
        "life_path_number": lp_val,
        "psychic_harmony_score": score_psychic,
        "life_path_harmony_score": score_lp,
        "personal_score": personal_score,
        "level": level,
        "synthesis": synthesis,
    }


# ------------------------------------------------------------------------------
# 8. Candidate Comparison & Multi-Property Evaluation
# ------------------------------------------------------------------------------

def evaluate_property_candidates(
    candidates_list: List[Dict[str, Any]],
    calculation_mode: str = "door_number",
    convention: str = "chaldean",
    property_usage: str = "residential_living",
    primary_birth_date: Optional[str] = None,
    primary_owner_name: Optional[str] = None,
    max_candidates: int = 25,
) -> List[Dict[str, Any]]:
    """Evaluate and rank up to 25 candidate properties deterministically."""
    results: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for cand_item in candidates_list:
        door_str = cand_item.get("door_flat_number", "")
        bldg_str = cand_item.get("building_number", "")
        floor_str = cand_item.get("floor_number", "")
        plot_str = cand_item.get("plot_number", "")
        bldg_name = cand_item.get("building_name", "")
        label_str = cand_item.get("label") or f"{door_str} {bldg_name}".strip() or "Candidate Property"

        # Deduplication key
        key = f"{door_str}|{floor_str}|{bldg_str}|{plot_str}|{bldg_name}".strip().upper()
        if not key or key in seen:
            continue
        seen.add(key)

        door_res = analyze_property_component(door_str, "door_number", "Door / Flat Number", convention)
        bldg_res = analyze_property_component(bldg_str, "building_number", "Building / Tower Number", convention)
        floor_res = analyze_property_component(floor_str, "floor_number", "Floor Number", convention)
        plot_res = analyze_property_component(plot_str, "plot_number", "Plot Number", convention)
        combined_res = calculate_combined_property_formula(door_res, bldg_res, floor_res, plot_res, convention)

        # Full alphanumeric with building name if available
        full_str = f"{door_str} {bldg_str} {bldg_name} {plot_str}".strip()
        full_res = analyze_property_component(full_str, "full_alphanumeric", "Full Alphanumeric Identifier", convention)

        # Select target analysis based on mode
        if calculation_mode == "building_number":
            active_res = bldg_res
        elif calculation_mode == "floor_number":
            active_res = floor_res
        elif calculation_mode == "plot_number":
            active_res = plot_res
        elif calculation_mode == "combined_property":
            active_res = combined_res
        elif calculation_mode == "full_alphanumeric":
            active_res = full_res
        else:
            active_res = door_res

        root_num = active_res["root_number"]

        # Usage match score
        usage_res = evaluate_property_usage_harmony(root_num, property_usage)
        usage_score = usage_res["score"]

        # Owner score
        owner_score: Optional[float] = None
        if primary_birth_date:
            try:
                drv_res = evaluate_single_resident_compatibility(
                    property_root=root_num,
                    birth_date_str=primary_birth_date,
                    name=primary_owner_name or "Owner",
                )
                owner_score = drv_res["personal_score"]
            except Exception:
                owner_score = None

        # Composite score calculation:
        # If owner DOB provided: 60% Owner Resonance + 40% Usage Match
        # If no owner DOB: 100% Usage Match
        if owner_score is not None:
            composite = round((owner_score * 0.60) + (usage_score * 0.40), 1)
        else:
            composite = round(usage_score, 1)

        is_fav = composite >= 70.0

        results.append({
            "label": label_str,
            "door_flat_number": door_str,
            "building_number": bldg_str,
            "floor_number": floor_str,
            "plot_number": plot_str,
            "building_name": bldg_name,
            "calculation_mode": calculation_mode,
            "compound_sum": active_res["compound_sum"],
            "root_number": root_num,
            "single_root": active_res["single_root"],
            "is_master": active_res["is_master"],
            "reduction_steps": active_res["reduction_steps"],
            "ruling_planet": active_res["ruling_planet"],
            "keyword": active_res["keyword"],
            "usage_score": usage_score,
            "owner_score": owner_score,
            "composite_score": composite,
            "is_favorable": is_fav,
        })

        if len(results) >= max_candidates:
            break

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results


# ------------------------------------------------------------------------------
# 9. Full Property Studio Orchestration Pipeline
# ------------------------------------------------------------------------------

def analyze_property_numerology_full(
    property_category: str = "apartment_flat",
    tenure_type: str = "purchased",
    door_flat_number: Optional[str] = None,
    building_number: Optional[str] = None,
    block_or_wing: Optional[str] = None,
    floor_number: Optional[str] = None,
    plot_number: Optional[str] = None,
    building_name: Optional[str] = None,
    facing_direction: Optional[str] = None,
    property_usage: str = "residential_living",
    convention: str = "chaldean",
    calculation_mode: str = "door_number",
    primary_birth_date: Optional[str] = None,
    primary_owner_name: Optional[str] = None,
    co_residents: Optional[List[Dict[str, Any]]] = None,
    candidate_properties: Optional[List[Dict[str, Any]]] = None,
    language: str = "en",
    max_candidates: int = 25,
) -> Dict[str, Any]:
    """Execute comprehensive property numerology and architectural synthesis."""
    # 1. Analyze Individual Components
    door_str = (door_flat_number or "").strip()
    bldg_str = (building_number or "").strip()
    floor_str = (floor_number or "").strip()
    plot_str = (plot_number or "").strip()
    wing_str = (block_or_wing or "").strip()
    name_str = (building_name or "").strip()

    door_analysis = analyze_property_component(door_str, "door_number", "Door / Flat Number", convention)
    building_analysis = analyze_property_component(bldg_str, "building_number", "Building / Tower Number", convention)
    floor_analysis = analyze_property_component(floor_str, "floor_number", "Floor Number", convention)
    plot_analysis = analyze_property_component(plot_str, "plot_number", "Plot Number", convention)

    # 2. Combined Property Formula
    combined_analysis = calculate_combined_property_formula(
        door_analysis, building_analysis, floor_analysis, plot_analysis, convention
    )

    # 3. Full Alphanumeric Identifier
    parts: List[str] = []
    if door_str: parts.append(door_str)
    if wing_str: parts.append(wing_str)
    if bldg_str: parts.append(bldg_str)
    if name_str: parts.append(name_str)
    if plot_str: parts.append(plot_str)
    full_ident = " ".join(parts).strip() or door_str or "Property"

    full_alphanumeric_analysis = analyze_property_component(
        full_ident, "full_alphanumeric", "Full Alphanumeric Identifier", convention
    )

    # 4. Select Primary Analysis based on active mode
    if calculation_mode == "building_number":
        primary_analysis = building_analysis
    elif calculation_mode == "floor_number":
        primary_analysis = floor_analysis
    elif calculation_mode == "plot_number":
        primary_analysis = plot_analysis
    elif calculation_mode == "combined_property":
        primary_analysis = combined_analysis
    elif calculation_mode == "full_alphanumeric":
        primary_analysis = full_alphanumeric_analysis
    else:
        primary_analysis = door_analysis

    # 5. Usage Compatibility
    usage_alignment = evaluate_property_usage_harmony(primary_analysis["root_number"], property_usage)

    # 6. Vastu Shastra Directional Alignment
    vastu_alignment = evaluate_property_vastu_facing(facing_direction, primary_analysis["root_number"])

    # 7. Resident & Family Compatibility
    resident_evaluations: List[Dict[str, Any]] = []
    overall_household_score: Optional[float] = None

    if primary_birth_date and primary_birth_date.strip():
        primary_eval = evaluate_single_resident_compatibility(
            property_root=primary_analysis["root_number"],
            birth_date_str=primary_birth_date.strip(),
            name=primary_owner_name or "Primary Resident",
            is_primary=True,
            role="Head of Household",
        )
        resident_evaluations.append(primary_eval)

    if co_residents:
        for co in co_residents:
            co_dob = co.get("birth_date")
            if co_dob and co_dob.strip():
                co_eval = evaluate_single_resident_compatibility(
                    property_root=primary_analysis["root_number"],
                    birth_date_str=co_dob.strip(),
                    name=co.get("name") or "Family Member",
                    is_primary=False,
                    role=co.get("role") or "Resident",
                )
                resident_evaluations.append(co_eval)

    if resident_evaluations:
        scores = [r["personal_score"] for r in resident_evaluations]
        if len(resident_evaluations) > 1 and resident_evaluations[0]["is_primary"]:
            co_avg = sum(scores[1:]) / len(scores[1:])
            overall_household_score = round((scores[0] * 0.6) + (co_avg * 0.4), 1)
        else:
            overall_household_score = round(sum(scores) / len(scores), 1)

    # 8. Candidate Property Comparison
    cands_input = candidate_properties or []
    candidate_results = evaluate_property_candidates(
        candidates_list=cands_input,
        calculation_mode=calculation_mode,
        convention=convention,
        property_usage=property_usage,
        primary_birth_date=primary_birth_date,
        primary_owner_name=primary_owner_name,
        max_candidates=max_candidates,
    )

    # 9. Transparent Scoring Explanation & Ethical Notice
    scoring_explanation = {
        "active_mode": calculation_mode,
        "system_convention": convention,
        "calculation_rules": {
            "door_number": "Focuses strictly on the immediate door or flat unit number. Traditional domestic standard.",
            "building_number": "Evaluates the collective building or tower shell number.",
            "floor_number": "Reflects elemental elevation above ground level.",
            "plot_number": "Reflects foundational land and cadastral soil vibration.",
            "combined_property": "Arithmetically sums all provided door, floor, building, and plot components.",
            "full_alphanumeric": f"Encodes full property title including building name via {convention.capitalize()} letter values.",
        },
        "vastu_integration": "Interprets traditional cardinal and intercardinal orientations according to Mayamata and classical treatises.",
        "resident_harmony": "Compares dwelling root with the owner's Psychic (Day) and Life Path numbers.",
    }

    disclaimer = (
        "Property numerology and Vastu directional reflections provide traditional symbolic and cultural perspectives "
        "on spatial harmony. They do not predict or guarantee financial returns, capital appreciation, physical safety, "
        "structural stability, or legal title clearance. Heuristic interpretations are classical traditions, not scientific claims."
    )

    return {
        "property_category": property_category,
        "tenure_type": tenure_type,
        "door_flat_number": door_str,
        "building_number": bldg_str,
        "block_or_wing": wing_str,
        "floor_number": floor_str,
        "plot_number": plot_str,
        "building_name": name_str,
        "facing_direction": facing_direction,
        "full_identifier": full_ident,
        "system_convention": convention,
        "calculation_mode": calculation_mode,
        "property_usage": property_usage,
        "primary_analysis": primary_analysis,
        "door_analysis": door_analysis,
        "building_analysis": building_analysis,
        "floor_analysis": floor_analysis,
        "plot_analysis": plot_analysis,
        "combined_analysis": combined_analysis,
        "full_alphanumeric_analysis": full_alphanumeric_analysis,
        "usage_alignment": usage_alignment,
        "vastu_alignment": vastu_alignment,
        "resident_alignments": resident_evaluations,
        "overall_household_score": overall_household_score,
        "candidates": candidate_results,
        "scoring_explanation": scoring_explanation,
        "disclaimer": disclaimer,
    }
