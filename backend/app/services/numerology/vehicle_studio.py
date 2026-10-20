"""Vehicle & Asset Registration Number Numerology Engine.

Provides deterministic numerological analysis of motor vehicle registration plates:
1. Registration Plate Parsing:
   - Supports Indian vehicle registration formats (e.g., TN 09 AB 1234, MH 12 CD 5678, DL 3C AB 1234, 22 BH 1234 AA).
   - Component extraction: State/Territory code, RTO/District code, Running series letters, Numeric digits.
   - Cleans and normalizes formatting while preserving original input for display.
   - Supports custom, international, and flexible plates gracefully.
2. Calculation Conventions:
   - 'digits_only': Numeric registration digits only (standard traditional Indian vehicle numerology).
   - 'numeric_all': Numeric prefix (RTO digits) + registration digits.
   - 'full_alphanumeric': Full plate characters mapped via Pythagorean (1-9) or Chaldean (1-8).
3. Pattern, Rhythm & Vanity / Memorability Score:
   - Detects VIP Single Digits (0001, 0007), Quad repeats (9999), Triples (777), Doubles (11),
     Ascending runs (1234), Descending runs (4321), and Mirror palindromes (1221).
   - Computes deterministic 0-100 Vanity Score.
4. Vehicle Usage Compatibility:
   - Personal, Family, Commercial, Fleet archetypal planetary resonance.
5. Owner & Co-Driver Alignment:
   - Primary owner and optional co-drivers' Psychic (Birth) and Life Path number alignment.
6. Candidate Comparison & Ranking:
   - Evaluates up to 25 candidate plates for auctions or new vehicle selection.
7. Disclaimers & Ethics:
   - Symbolic and philosophical exploration tool. Does not predict or guarantee safety,
     accident avoidance, mechanical longevity, or official RTO availability.
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
# 1. State & Territory Reference Mapping
# ------------------------------------------------------------------------------

INDIAN_STATES_UTS: Dict[str, str] = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "CH": "Chandigarh",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "DN": "Dadra and Nagar Haveli",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HP": "Himachal Pradesh",
    "HR": "Haryana",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "OR": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TR": "Tripura",
    "TS": "Telangana",
    "TG": "Telangana",
    "UK": "Uttarakhand",
    "UA": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
    "BH": "Bharat Series (Pan-India)",
}


# ------------------------------------------------------------------------------
# 2. Registration Parsing & Normalization
# ------------------------------------------------------------------------------

def parse_vehicle_registration(raw_input: str) -> Dict[str, Any]:
    """Parse raw vehicle registration string into standard plate components.

    Handles:
    - Standard Indian: 'TN 09 AB 1234', 'MH 12 CD 5678', 'KA 01 1234', 'TN09AB1234'
    - Delhi Style: 'DL 3C AB 1234', 'DL 01 C 1234'
    - Bharat (BH) Series: '22 BH 1234 AA'
    - Custom / International / General Alphanumeric Plates

    Returns:
        Dict with raw_input, compact_registration, formatted_registration,
        state_code, state_name, rto_code, series_letters, numeric_digits,
        is_valid_indian_format, plate_classification.
    """
    if not raw_input or not raw_input.strip():
        raise ValueError("Vehicle registration number cannot be empty.")

    cleaned = raw_input.strip().upper()

    # Reject prohibited special characters (allow alphanumeric, spaces, hyphens, dots)
    if not re.match(r"^[A-Z0-9\s\-\.]+$", cleaned):
        raise ValueError(
            "Registration number contains invalid characters. Only letters, digits, spaces, and hyphens are permitted."
        )

    # Compact string without separators
    compact = re.sub(r"[\s\-\.]+", "", cleaned)

    if len(compact) < 2:
        raise ValueError(f"Registration number '{raw_input}' is too short.")
    if len(compact) > 16:
        raise ValueError(f"Registration number '{raw_input}' exceeds maximum length of 16 characters.")

    # 1. Check Bharat (BH) series: e.g. 22 BH 1234 AA or 22BH1234AA
    bh_match = re.match(r"^(\d{2})BH(\d{1,4})([A-Z]{1,2})$", compact)
    if bh_match:
        year_prefix = bh_match.group(1)
        digits = bh_match.group(2)
        series = bh_match.group(3)
        formatted = f"{year_prefix} BH {digits} {series}"
        return {
            "raw_input": raw_input.strip(),
            "compact_registration": compact,
            "formatted_registration": formatted,
            "state_code": "BH",
            "state_name": "Bharat Series (Pan-India)",
            "rto_code": year_prefix,
            "series_letters": series,
            "numeric_digits": digits,
            "is_valid_indian_format": True,
            "plate_classification": "Bharat (BH) Pan-India Series",
        }

    # 2. Check Standard Indian Plate (including Delhi variations):
    # Pattern: State (2 letters) + RTO (1 digit + 1 letter like 3C, OR 2 digits, OR 1 digit) + Series (0-3 letters) + Digits (1-4 digits)
    # Examples: TN 09 AB 1234, DL 3C AB 1234, MH 12 1234, KA 01 M 5
    indian_match = re.match(r"^([A-Z]{2})(\d[A-Z]|\d{2}|\d)([A-Z]{0,3})(\d{1,4})$", compact)
    if indian_match:
        state_code = indian_match.group(1)
        if state_code in INDIAN_STATES_UTS:
            rto_code = indian_match.group(2)
            series = indian_match.group(3) or ""
            digits = indian_match.group(4)
            state_name = INDIAN_STATES_UTS[state_code]

            parts = [state_code, rto_code]
            if series:
                parts.append(series)
            parts.append(digits)
            formatted = " ".join(parts)

            return {
                "raw_input": raw_input.strip(),
                "compact_registration": compact,
                "formatted_registration": formatted,
                "state_code": state_code,
                "state_name": state_name,
                "rto_code": rto_code,
                "series_letters": series,
                "numeric_digits": digits,
                "is_valid_indian_format": True,
                "plate_classification": "Standard Indian State Series",
            }

    # 3. Fallback: General Alphanumeric / Custom / International Plate
    # Extract trailing digits as numeric digits if present, else all digits
    all_digits = re.findall(r"\d+", compact)
    numeric_digits = all_digits[-1] if all_digits else ""
    letters_only = re.sub(r"\d+", "", compact)

    # Heuristic State extraction: first 2 letters if start with letters
    state_code = compact[:2] if len(compact) >= 2 and compact[:2].isalpha() else None
    state_name = INDIAN_STATES_UTS.get(state_code) if state_code else None

    # Formatted display with spaces around numeric boundaries
    formatted = re.sub(r"([A-Z]+)(\d+)", r"\1 \2 ", compact).strip()
    formatted = re.sub(r"(\d+)([A-Z]+)", r"\1 \2", formatted)

    return {
        "raw_input": raw_input.strip(),
        "compact_registration": compact,
        "formatted_registration": formatted,
        "state_code": state_code,
        "state_name": state_name or "Custom / International",
        "rto_code": None,
        "series_letters": letters_only or "",
        "numeric_digits": numeric_digits or compact,
        "is_valid_indian_format": False,
        "plate_classification": "Custom / International Plate",
    }


# ------------------------------------------------------------------------------
# 3. Number Reduction & Letter Mapping Engine
# ------------------------------------------------------------------------------

def calculate_vehicle_character_mapping(
    target_string: str,
    convention: str = "chaldean",
) -> Tuple[List[Dict[str, Any]], int]:
    """Map each character (letters and digits) to its numerical value according to the chosen system.

    In both Pythagorean and Chaldean systems:
    - Digits '0'-'9' keep their face numerical value.
    - Letters 'A'-'Z' are mapped via PYTHAGOREAN_MAP (1-9) or CHALDEAN_MAP (1-8).
    - Spaces, hyphens, and punctuation have value 0 and are omitted from calculation.

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


# Traditional archetypes and descriptions for vehicle roots 1-9 & Master Numbers
VEHICLE_VIBRATIONAL_ARCHETYPES: Dict[int, Dict[str, str]] = {
    1: {
        "keyword": "Leadership, Pioneer & Vitality",
        "effect": "Associated with the Sun. Gives strong executive presence, commanding visibility, confidence on highways, and swift independent movement. Highly favorable for entrepreneurs, senior executives, and primary lead cars.",
    },
    2: {
        "keyword": "Harmony, Serenity & Smooth Flow",
        "effect": "Associated with the Moon. Brings gentle vibration, comfortable leisurely journeys, and passenger comfort. Ideal for family cars and shared commutes, favoring calm and patient driving.",
    },
    3: {
        "keyword": "Expansion, Optimism & Good Fortune",
        "effect": "Associated with Jupiter (Guru). Promotes pleasant travel, educational or professional journeys, good fellowship, and expansive horizons. Excellent for family tours, consultants, and educational transit.",
    },
    4: {
        "keyword": "Structure, Utility & Practical Stability",
        "effect": "Associated with Rahu / Uranus. Represents solid engineering, rugged endurance, and functional dependability. Benefits from regular mechanical servicing, disciplined speed, and pragmatic use.",
    },
    5: {
        "keyword": "Speed, Adaptability & Commercial Agility",
        "effect": "Associated with Mercury (Budha). Highly dynamic vibration favoring frequent trips, inter-city mobility, commercial trade, and quick transit. Perfect for marketing professionals, delivery fleets, and daily commuters.",
    },
    6: {
        "keyword": "Luxury, Comfort & Aesthetic Elegance",
        "effect": "Associated with Venus (Shukra). Radiates grace, luxurious comfort, visual beauty, and protective care. Highly auspicious for luxury sedans, bridal cars, hospitality vehicles, and design professionals.",
    },
    7: {
        "keyword": "Introspection, Solitude & Safe Haven",
        "effect": "Associated with Ketu / Neptune. A quiet, contemplative vibration favoring solo travel, peaceful scenic routes, and research journeys. Fosters mindful driving and serene personal space.",
    },
    8: {
        "keyword": "Endurance, Power & Heavy Duty Utility",
        "effect": "Associated with Saturn (Shani). Embodies immense physical durability, authoritative presence, and commercial longevity. Outstanding for SUVs, heavy transport, industrial machinery, and long-distance haulage.",
    },
    9: {
        "keyword": "Dynamic Energy, Courage & Swift Action",
        "effect": "Associated with Mars (Mangala). Full of brisk vitality, decisive momentum, and spirited agility. Best suited for high-performance sports cars, emergency response, and confident, alert drivers.",
    },
    11: {
        "keyword": "Master Intuition & Elevated Guidance",
        "effect": "Master Number 11 vibrates with acute driver intuition, heightened situational awareness, and inspirational journeys. Brings an elevated protective aura when driven with mindfulness.",
    },
    22: {
        "keyword": "Master Builder & Global Architecture",
        "effect": "Master Number 22 embodies large-scale enterprise, grand commercial fleets, and enduring durability across vast distances. Connects practical engineering with ambitious journeys.",
    },
    33: {
        "keyword": "Master Blessing & Protective Service",
        "effect": "Master Number 33 radiates compassionate service, safety for all occupants, and joyful journeys. Ideal for family vans, community transport, and philanthropic ventures.",
    },
}


def analyze_vehicle_mode(
    source_str: str,
    mode_name: str,
    mode_label: str,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Perform full numerical breakdown for a specific vehicle calculation mode."""
    mappings, compound_sum = calculate_vehicle_character_mapping(source_str, convention)

    root_num, reduction_steps = reduce_number_steps(compound_sum, preserve_master=True)
    single_root = reduce_number(root_num, preserve_master=False)
    is_master = root_num in (11, 22, 33)

    planet_data = get_ruling_planet(root_num)
    planet_name = planet_data.get("en", str(planet_data)) if isinstance(planet_data, dict) else str(planet_data)

    archetype = VEHICLE_VIBRATIONAL_ARCHETYPES.get(
        root_num,
        VEHICLE_VIBRATIONAL_ARCHETYPES.get(single_root, VEHICLE_VIBRATIONAL_ARCHETYPES[1]),
    )

    # Detailed character breakdown string for formula transparency
    parts_expr = " + ".join([f"{m['char']}({m['value']})" for m in mappings]) if mappings else "0"
    formula_step = f"{parts_expr} = {compound_sum}"

    all_steps = [formula_step]
    if reduction_steps and reduction_steps[0] != str(compound_sum):
        all_steps.extend(reduction_steps)
    elif len(reduction_steps) > 1:
        all_steps.extend(reduction_steps[1:])

    return {
        "calculation_mode": mode_name,
        "mode_label": mode_label,
        "source_string": source_str,
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
# 4. Pattern Detection & Vanity / Memorability Score
# ------------------------------------------------------------------------------

def analyze_vehicle_patterns(numeric_digits: str) -> Dict[str, Any]:
    """Detect repetitive clusters, sequences, mirror numbers, and compute Vanity Score (0-100)."""
    digits_clean = re.sub(r"\D", "", numeric_digits)

    # If no numeric digits, evaluate with fallback
    if not digits_clean:
        return {
            "vanity_score": 20.0,
            "pattern_tags": ["Standard Plate"],
            "pattern_classification": "Standard Number",
            "is_vip_number": False,
            "repeats": [],
            "is_ascending": False,
            "is_descending": False,
            "is_mirror": False,
            "details": "No distinct numeric sequence detected.",
        }

    pattern_tags: List[str] = []
    bonus = 0.0

    # 1. Single-digit Super VIPs (e.g. 1, 7, 0001, 0007, 0009)
    int_val = int(digits_clean)
    if int_val in (1, 7, 9):
        pattern_tags.append(f"Super VIP Single Digit ({digits_clean})")
        bonus += 65.0
    elif 1 <= int_val <= 9:
        pattern_tags.append(f"VIP Single Digit ({digits_clean})")
        bonus += 50.0

    # 2. Quad Repetitions (e.g. 1111, 7777, 9999, 0000)
    quads = re.findall(r"(\d)\1{3}", digits_clean)
    if quads:
        pattern_tags.append(f"VIP Quad ({quads[0] * 4})")
        bonus += 60.0

    # 3. Triple Repetitions (e.g. 777, 999, 000)
    triples = re.findall(r"(\d)\1{2}", digits_clean)
    if triples and not quads:
        pattern_tags.append(f"VIP Triple ({triples[0] * 3})")
        bonus += 40.0

    # 4. Double Doubles / Pairs (e.g. 1122, 2244, 9900)
    pairs = re.findall(r"(\d)\1", digits_clean)
    if len(pairs) >= 2 and not quads and not triples:
        pattern_tags.append("Double Pair Cluster")
        bonus += 25.0
    elif len(pairs) == 1 and not quads and not triples:
        pattern_tags.append(f"Double Digit ({pairs[0] * 2})")
        bonus += 15.0

    # 5. Mirror / Palindrome (e.g. 1221, 8008, 1001, 121)
    is_mirror = len(digits_clean) >= 3 and digits_clean == digits_clean[::-1]
    if is_mirror:
        pattern_tags.append(f"Mirror Palindrome ({digits_clean})")
        bonus += 35.0

    # 6. Ascending Sequences (e.g. 1234, 4567, 789)
    is_ascending = False
    if len(digits_clean) >= 3:
        nums = [int(d) for d in digits_clean]
        if all(nums[i] + 1 == nums[i + 1] for i in range(len(nums) - 1)):
            is_ascending = True
            pattern_tags.append(f"Ascending Run ({digits_clean})")
            bonus += 40.0

    # 7. Descending Sequences (e.g. 4321, 9876)
    is_descending = False
    if len(digits_clean) >= 3:
        nums = [int(d) for d in digits_clean]
        if all(nums[i] - 1 == nums[i + 1] for i in range(len(nums) - 1)):
            is_descending = True
            pattern_tags.append(f"Descending Run ({digits_clean})")
            bonus += 30.0

    # 8. Symmetrical 2-digit rhythm (e.g. 1212, 4545, 1010)
    if len(digits_clean) == 4 and digits_clean[:2] == digits_clean[2:] and not quads:
        pattern_tags.append(f"Twin Rhythm ({digits_clean[:2]}-{digits_clean[2:]})")
        bonus += 35.0

    # Base memorability based on length and simplicity
    base_score = 30.0
    if len(digits_clean) <= 2:
        base_score += 20.0
    elif len(set(digits_clean)) <= 2:
        base_score += 15.0

    vanity_score = min(100.0, round(base_score + bonus, 1))
    is_vip = vanity_score >= 70.0

    classification = (
        "Super VIP / Auction Elite" if vanity_score >= 85.0
        else "VIP Premium Sequence" if vanity_score >= 70.0
        else "Distinctive Memorable Plate" if vanity_score >= 50.0
        else "Standard Registration"
    )

    if not pattern_tags:
        pattern_tags.append("Balanced Distribution")

    details = f"Vanity Score: {vanity_score}/100. Patterns identified: {', '.join(pattern_tags)}."

    return {
        "vanity_score": vanity_score,
        "pattern_tags": pattern_tags,
        "pattern_classification": classification,
        "is_vip_number": is_vip,
        "repeats": list(set(quads + triples + pairs)),
        "is_ascending": is_ascending,
        "is_descending": is_descending,
        "is_mirror": is_mirror,
        "details": details,
    }


# ------------------------------------------------------------------------------
# 5. Vehicle Usage Compatibility (Personal, Family, Commercial, Fleet)
# ------------------------------------------------------------------------------

VEHICLE_USE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "personal": {
        "name": "Personal & Executive Travel",
        "primary_numbers": [1, 5, 6],
        "secondary_numbers": [3, 9],
        "planetary_rulers": "Sun (1), Venus (6), Mercury (5)",
        "description": "Favors individual driving comfort, commanding leadership presence, agility, and aesthetic personal pride.",
    },
    "family": {
        "name": "Family & Household Journeys",
        "primary_numbers": [2, 3, 6],
        "secondary_numbers": [1, 7],
        "planetary_rulers": "Moon (2), Jupiter (3), Venus (6)",
        "description": "Favors tranquil passenger comfort, mutual care, joyful outings, safety consciousness, and harmonious shared travels.",
    },
    "commercial": {
        "name": "Commercial & Client Logistics",
        "primary_numbers": [5, 1, 8],
        "secondary_numbers": [3, 6],
        "planetary_rulers": "Mercury (5), Sun (1), Saturn (8)",
        "description": "Favors active business trade, client acquisition, punctuality, commercial turnaround, and revenue generation.",
    },
    "fleet": {
        "name": "Heavy Duty Fleet & Transport",
        "primary_numbers": [8, 9, 1],
        "secondary_numbers": [4, 5],
        "planetary_rulers": "Saturn (8), Mars (9), Sun (1)",
        "description": "Favors physical endurance, mechanical discipline, robust long-haul transport, and structural operational stamina.",
    },
}


def evaluate_vehicle_usage_harmony(vehicle_root: int, usage_type: str = "personal") -> Dict[str, Any]:
    """Score the resonance of the vehicle's root number with its intended usage archetype."""
    use_key = usage_type.lower() if usage_type.lower() in VEHICLE_USE_ARCHETYPES else "personal"
    archetype = VEHICLE_USE_ARCHETYPES[use_key]

    single_root = reduce_number(vehicle_root, preserve_master=False)

    if single_root in archetype["primary_numbers"]:
        score = 95.0
        level = "Optimal Archetypal Match"
        desc = f"Number {vehicle_root} is an exemplary match for {archetype['name']}, channeling {archetype['planetary_rulers']}."
    elif single_root in archetype["secondary_numbers"]:
        score = 80.0
        level = "Favorable Alignment"
        desc = f"Number {vehicle_root} provides strong complementary support for {archetype['name']}."
    elif single_root == 4 or single_root == 8:
        # 4 and 8 require disciplined maintenance
        score = 65.0
        level = "Pragmatic Utility (Requires Maintenance)"
        desc = f"Number {vehicle_root} brings structural duty; regular vehicle servicing and careful driving are recommended."
    else:
        score = 55.0
        level = "Moderate General Resonance"
        desc = f"Number {vehicle_root} operates neutrally for {archetype['name']}."

    return {
        "vehicle_usage": use_key,
        "usage_name": archetype["name"],
        "planetary_rulers": archetype["planetary_rulers"],
        "primary_numbers": archetype["primary_numbers"],
        "secondary_numbers": archetype["secondary_numbers"],
        "score": score,
        "level": level,
        "description": desc,
    }


# ------------------------------------------------------------------------------
# 6. Owner & Multi-Driver Compatibility Evaluation
# ------------------------------------------------------------------------------

def evaluate_single_driver_compatibility(
    vehicle_root: int,
    birth_date_str: str,
    name: str = "Owner",
    is_primary: bool = True,
    role: str = "Primary Driver",
) -> Dict[str, Any]:
    """Compare vehicle root number against a specific driver's Psychic and Life Path numbers."""
    psychic_val, _, _ = calculate_birth_psychic_number(birth_date_str)
    lp_res = calculate_life_path_detailed(birth_date_str)
    lp_val = lp_res["life_path"]

    score_psychic, psychic_desc = assess_number_harmony(vehicle_root, psychic_val)
    score_lp, lp_desc = assess_number_harmony(vehicle_root, lp_val)

    # 50% Psychic harmony (daily temperament behind the wheel) + 50% Life Path (long-term journey destiny)
    personal_score = round((score_psychic * 0.5) + (score_lp * 0.5), 1)

    level = (
        "Harmonious" if personal_score >= 80.0
        else "Complementary" if personal_score >= 60.0
        else "Neutral" if personal_score >= 45.0
        else "Tension"
    )

    synthesis = (
        f"Vehicle vibration {vehicle_root} aligns with {name}'s Psychic {psychic_val} ({psychic_desc}) "
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
# 7. Candidate Comparison & Ranking Engine
# ------------------------------------------------------------------------------

def evaluate_vehicle_candidates(
    candidates_list: List[str],
    calculation_mode: str = "digits_only",
    convention: str = "chaldean",
    vehicle_usage: str = "personal",
    primary_birth_date: Optional[str] = None,
    primary_owner_name: Optional[str] = None,
    max_candidates: int = 25,
) -> List[Dict[str, Any]]:
    """Evaluate and rank up to 25 candidate vehicle registration numbers deterministically."""
    results: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for cand_raw in candidates_list:
        if not cand_raw or not cand_raw.strip():
            continue

        cand_str = cand_raw.strip()
        compact_key = re.sub(r"[\s\-\.]+", "", cand_str).upper()
        if compact_key in seen:
            continue
        seen.add(compact_key)

        try:
            parsed = parse_vehicle_registration(cand_str)
        except Exception:
            continue

        # Determine target string based on calculation mode
        if calculation_mode == "digits_only":
            target_str = parsed["numeric_digits"] or parsed["compact_registration"]
            mode_lbl = "Numeric Digits Only"
        elif calculation_mode == "numeric_all":
            prefix_nums = re.findall(r"\d+", parsed["rto_code"] or "")
            target_str = "".join(prefix_nums) + parsed["numeric_digits"]
            mode_lbl = "Numeric Prefix + Digits"
        else:
            target_str = parsed["compact_registration"]
            mode_lbl = "Full Alphanumeric Plate"

        # Calculate numerical breakdown
        cand_mode_res = analyze_vehicle_mode(target_str, calculation_mode, mode_lbl, convention)
        root_num = cand_mode_res["root_number"]

        # Pattern & Vanity
        patterns = analyze_vehicle_patterns(parsed["numeric_digits"])
        vanity_score = patterns["vanity_score"]

        # Usage score
        usage_res = evaluate_vehicle_usage_harmony(root_num, vehicle_usage)
        usage_score = usage_res["score"]

        # Owner score
        owner_score: Optional[float] = None
        if primary_birth_date:
            try:
                drv_res = evaluate_single_driver_compatibility(
                    vehicle_root=root_num,
                    birth_date_str=primary_birth_date,
                    name=primary_owner_name or "Owner",
                )
                owner_score = drv_res["personal_score"]
            except Exception:
                owner_score = None

        # Composite score calculation:
        # If owner DOB provided: 40% Owner Resonance + 30% Vanity Score + 30% Vehicle Usage
        # If no owner DOB: 60% Vanity Score + 40% Vehicle Usage
        if owner_score is not None:
            composite = round((owner_score * 0.40) + (vanity_score * 0.30) + (usage_score * 0.30), 1)
        else:
            composite = round((vanity_score * 0.60) + (usage_score * 0.40), 1)

        is_fav = composite >= 70.0

        results.append({
            "raw_input": cand_str,
            "normalized_registration": parsed["formatted_registration"],
            "plate_classification": parsed["plate_classification"],
            "state_code": parsed["state_code"],
            "state_name": parsed["state_name"],
            "rto_code": parsed["rto_code"],
            "series_letters": parsed["series_letters"],
            "numeric_digits": parsed["numeric_digits"],
            "calculation_mode": calculation_mode,
            "compound_sum": cand_mode_res["compound_sum"],
            "root_number": root_num,
            "single_root": cand_mode_res["single_root"],
            "is_master": cand_mode_res["is_master"],
            "reduction_steps": cand_mode_res["reduction_steps"],
            "patterns": patterns,
            "vanity_score": vanity_score,
            "usage_score": usage_score,
            "owner_score": owner_score,
            "composite_score": composite,
            "is_favorable": is_fav,
        })

        if len(results) >= max_candidates:
            break

    # Sort descending by composite_score, then vanity_score
    results.sort(key=lambda x: (x["composite_score"], x["vanity_score"]), reverse=True)
    return results


# ------------------------------------------------------------------------------
# 8. Full Vehicle Studio Orchestration Pipeline
# ------------------------------------------------------------------------------

def analyze_vehicle_numerology_full(
    registration_number: str,
    convention: str = "chaldean",
    calculation_mode: str = "digits_only",
    vehicle_usage: str = "personal",
    primary_birth_date: Optional[str] = None,
    primary_owner_name: Optional[str] = None,
    co_owners: Optional[List[Dict[str, Any]]] = None,
    candidate_numbers: Optional[List[str]] = None,
    language: str = "en",
    max_candidates: int = 25,
) -> Dict[str, Any]:
    """Execute end-to-end vehicle registration numerological analysis."""
    # 1. Parse plate
    parsed = parse_vehicle_registration(registration_number)

    # 2. Compute the 3 distinct calculation modes:
    # A. Digits Only (Numeric registration digits e.g. '1234')
    digits_str = parsed["numeric_digits"] or parsed["compact_registration"]
    digits_only_res = analyze_vehicle_mode(
        source_str=digits_str,
        mode_name="digits_only",
        mode_label="Numeric Registration Digits Only",
        convention=convention,
    )

    # B. Numeric All (RTO numeric prefix + registration digits e.g. '091234')
    rto_digits = re.findall(r"\d+", parsed["rto_code"] or "")
    numeric_all_str = "".join(rto_digits) + (parsed["numeric_digits"] or "")
    if not numeric_all_str:
        numeric_all_str = digits_str
    numeric_all_res = analyze_vehicle_mode(
        source_str=numeric_all_str,
        mode_name="numeric_all",
        mode_label="Numeric Prefix + Registration Digits",
        convention=convention,
    )

    # C. Full Alphanumeric Plate (e.g. 'TN09AB1234')
    full_alphanumeric_res = analyze_vehicle_mode(
        source_str=parsed["compact_registration"],
        mode_name="full_alphanumeric",
        mode_label="Full Alphanumeric Plate",
        convention=convention,
    )

    # Select primary analysis based on user requested calculation_mode
    if calculation_mode == "numeric_all":
        primary_res = numeric_all_res
    elif calculation_mode == "full_alphanumeric":
        primary_res = full_alphanumeric_res
    else:
        primary_res = digits_only_res

    # 3. Pattern & Vanity Analysis
    patterns = analyze_vehicle_patterns(parsed["numeric_digits"])
    vanity_score = patterns["vanity_score"]

    # 4. Vehicle Usage Resonance
    usage_alignment = evaluate_vehicle_usage_harmony(primary_res["root_number"], vehicle_usage)

    # 5. Owner & Co-Driver Alignment
    driver_evaluations: List[Dict[str, Any]] = []
    overall_owner_score: Optional[float] = None

    if primary_birth_date and primary_birth_date.strip():
        primary_eval = evaluate_single_driver_compatibility(
            vehicle_root=primary_res["root_number"],
            birth_date_str=primary_birth_date.strip(),
            name=primary_owner_name or "Primary Owner",
            is_primary=True,
            role="Primary Owner",
        )
        driver_evaluations.append(primary_eval)

    if co_owners:
        for co in co_owners:
            co_dob = co.get("birth_date")
            if co_dob and co_dob.strip():
                co_eval = evaluate_single_driver_compatibility(
                    vehicle_root=primary_res["root_number"],
                    birth_date_str=co_dob.strip(),
                    name=co.get("name") or "Co-Driver",
                    is_primary=False,
                    role=co.get("role") or "Co-Driver",
                )
                driver_evaluations.append(co_eval)

    if driver_evaluations:
        scores = [d["personal_score"] for d in driver_evaluations]
        # Primary driver has 60% weight if multiple drivers exist
        if len(driver_evaluations) > 1 and driver_evaluations[0]["is_primary"]:
            co_avg = sum(scores[1:]) / len(scores[1:])
            overall_owner_score = round((scores[0] * 0.6) + (co_avg * 0.4), 1)
        else:
            overall_owner_score = round(sum(scores) / len(scores), 1)

    # 6. Candidate Comparison
    cands_input = candidate_numbers or []
    candidate_results = evaluate_vehicle_candidates(
        candidates_list=cands_input,
        calculation_mode=calculation_mode,
        convention=convention,
        vehicle_usage=vehicle_usage,
        primary_birth_date=primary_birth_date,
        primary_owner_name=primary_owner_name,
        max_candidates=max_candidates,
    )

    # 7. Scoring Explanation & Summary
    scoring_explanation = {
        "active_mode": calculation_mode,
        "system_convention": convention,
        "calculation_rules": {
            "digits_only": "Focuses strictly on the vehicle's 4-digit unique registration number. Traditional Indian standard.",
            "numeric_all": "Combines RTO district numeric digits with registration digits to reflect regional vibration.",
            "full_alphanumeric": f"Encodes all state, RTO, and series letters using {convention.capitalize()} letter values (A-Z) combined with digits.",
        },
        "vanity_scoring": "Vanity score measures sequence recall, single-digit rarity (0001/0007), quad/triple repeats, and mirror symmetry.",
        "usage_weighting": "Evaluates planetary archetypal harmony with personal, family, commercial, or heavy fleet usage.",
    }

    disclaimer = (
        "Vehicle registration numerological analysis is a traditional symbolic reflection tool intended for personal "
        "exploration and cultural appreciation. It does not evaluate mechanical roadworthiness, vehicle safety, accident "
        "avoidance, legal fitness, or official government RTO availability. No unauthorized database lookups are performed."
    )

    return {
        "raw_input": parsed["raw_input"],
        "normalized_registration": parsed["formatted_registration"],
        "formatted_registration": parsed["formatted_registration"],
        "state_code": parsed["state_code"],
        "state_name": parsed["state_name"],
        "rto_code": parsed["rto_code"],
        "series_letters": parsed["series_letters"],
        "numeric_digits": parsed["numeric_digits"],
        "is_valid_indian_format": parsed["is_valid_indian_format"],
        "plate_classification": parsed["plate_classification"],
        "system_convention": convention,
        "calculation_mode": calculation_mode,
        "vehicle_usage": vehicle_usage,
        "primary_analysis": primary_res,
        "digits_only_analysis": digits_only_res,
        "numeric_all_analysis": numeric_all_res,
        "full_alphanumeric_analysis": full_alphanumeric_res,
        "patterns": patterns,
        "vanity_score": vanity_score,
        "usage_alignment": usage_alignment,
        "owner_alignments": driver_evaluations,
        "overall_owner_score": overall_owner_score,
        "candidates": candidate_results,
        "scoring_explanation": scoring_explanation,
        "disclaimer": disclaimer,
    }
