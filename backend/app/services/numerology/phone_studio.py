"""Phone & Mobile Number Numerology Analyzer Engine.

Provides deterministic numerological analysis of personal and commercial phone numbers:
1. Normalization & Country Calling Code Extraction:
   - Preserves original input for display.
   - Extracts domestic national subscriber digits and international dial code.
   - Supports both National Subscriber calculation (standard in traditional numerology)
     and Full International calculation.
2. Core Numerical Metrics:
   - Digit count, total digit sum (compound number), and reduced root number (1-9 / master numbers).
   - Frequency distribution of each digit from 0 to 9.
   - Missing digits analysis with traditional Vedic / Lo Shu energetic meanings.
   - Traditional significance of zero (0) as amplifier, void, or cyclical catalyst.
3. Rhythm & Pattern Analysis:
   - Repeated doublets, triplets, quadruplets, ascending/descending sequences.
   - Vanity / Memorability Score (0-100) reflecting commercial recall and phonetic rhythm.
4. Profile Alignment:
   - Personal harmony with owner's Birth/Psychic and Life Path numbers.
   - Commercial harmony with 9 industry sectors and planetary rulers.
5. Candidate Comparison & Ranking:
   - Deterministic multi-candidate ranking for selecting new SIM or VIP numbers.
6. Privacy & Security:
   - Masking of phone numbers for server logs (never logs full numbers in plain text).
   - Explicit disclaimer: this is a traditional symbolic and cultural interpretation tool,
     not a telecommunications, carrier, or caller-ID verification service.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from .traditional import reduce_number, reduce_number_steps, get_ruling_planet
from .name_studio import NUMEROLOGICAL_HARMONY, get_root_number, assess_number_harmony
from .business_studio import INDUSTRY_PROFILES, score_industry_harmony


# ------------------------------------------------------------------------------
# 1. Country Codes & Phone Normalization
# ------------------------------------------------------------------------------

# Common international calling codes mapping (code -> country name)
COMMON_COUNTRY_CODES: Dict[str, str] = {
    "91": "India",
    "1": "USA / Canada",
    "44": "United Kingdom",
    "65": "Singapore",
    "971": "United Arab Emirates",
    "61": "Australia",
    "60": "Malaysia",
    "49": "Germany",
    "33": "France",
    "81": "Japan",
    "94": "Sri Lanka",
}

# Sorted by descending length so +971 is matched before +91 or +9
SORTED_COUNTRY_PREFIXES = sorted(COMMON_COUNTRY_CODES.keys(), key=lambda k: len(k), reverse=True)


def mask_phone_number(phone_str: str) -> str:
    """Mask phone number for privacy-safe logging (e.g. '+91 98**** *210').
    Ensures full numbers are never exposed in server logs.
    """
    clean = re.sub(r"[^\d+]", "", phone_str)
    if len(clean) <= 4:
        return "****"
    if clean.startswith("+"):
        prefix = clean[:4]
        suffix = clean[-3:]
        masked_middle = "*" * (len(clean) - 7)
        return f"{prefix}{masked_middle}{suffix}"
    prefix = clean[:2]
    suffix = clean[-2:]
    masked_middle = "*" * (len(clean) - 4)
    return f"{prefix}{masked_middle}{suffix}"


def normalize_phone_number(raw_input: str) -> Dict[str, Any]:
    """Parse, clean, and validate phone number into display, national, and international formats.

    Raises:
        ValueError: If input contains invalid characters, is empty, or violates ITU-T E.164 bounds (7-15 digits).
    """
    if not raw_input or not raw_input.strip():
        raise ValueError("Phone number cannot be empty.")

    cleaned_str = raw_input.strip()

    # Reject invalid characters: allow digits, spaces, hyphens, parentheses, dots, leading plus
    if not re.match(r"^[\+]?[0-9\s\-\(\)\.]+$", cleaned_str):
        raise ValueError(
            "Phone number contains invalid characters. Only digits, spaces, hyphens, parentheses, and a leading '+' are permitted."
        )

    # Extract all digits
    all_digits = re.sub(r"\D", "", cleaned_str)

    if len(all_digits) < 7:
        raise ValueError(f"Phone number too short ({len(all_digits)} digits). Must have at least 7 digits.")
    if len(all_digits) > 15:
        raise ValueError(f"Phone number exceeds ITU-T E.164 standard ({len(all_digits)} digits). Maximum is 15 digits.")

    is_international = cleaned_str.startswith("+") or cleaned_str.startswith("00")
    if cleaned_str.startswith("00"):
        # Strip 00 international dial prefix
        all_digits_no_prefix = all_digits[2:]
    else:
        all_digits_no_prefix = all_digits

    detected_country_code: Optional[str] = None
    detected_country_name: Optional[str] = None
    national_number = all_digits

    # Check international prefixes if marked with + or 00, or if length indicates an Indian 12-digit number (91...)
    if is_international:
        for prefix in SORTED_COUNTRY_PREFIXES:
            if all_digits_no_prefix.startswith(prefix):
                # Ensure the remaining national number has at least 6 digits
                remainder = all_digits_no_prefix[len(prefix):]
                if len(remainder) >= 6:
                    detected_country_code = prefix
                    detected_country_name = COMMON_COUNTRY_CODES[prefix]
                    national_number = remainder
                    break
    elif len(all_digits) == 12 and all_digits.startswith("91"):
        # Auto-detect standard Indian 12-digit e.g. 919876543210
        detected_country_code = "91"
        detected_country_name = "India"
        national_number = all_digits[2:]
    elif len(all_digits) == 11 and all_digits.startswith("0"):
        # Strip domestic trunk prefix 0 (e.g. 09876543210 -> 9876543210)
        national_number = all_digits[1:]

    # Check if national number is a valid 10-digit Indian mobile
    is_indian_mobile = (
        len(national_number) == 10 and national_number[0] in ("6", "7", "8", "9")
    )
    if is_indian_mobile and not detected_country_name:
        detected_country_name = "India (Presumed)"
        detected_country_code = "91"

    # Standard formatted display: e.g. +91 98765 43210
    if len(national_number) == 10:
        formatted_national = f"{national_number[:5]} {national_number[5:]}"
    elif len(national_number) == 7:
        formatted_national = f"{national_number[:3]}-{national_number[3:]}"
    else:
        formatted_national = national_number

    if detected_country_code:
        display_international = f"+{detected_country_code} {formatted_national}"
    else:
        display_international = formatted_national

    return {
        "raw_input": cleaned_str,
        "masked_input": mask_phone_number(cleaned_str),
        "all_digits": all_digits,
        "national_number": national_number,
        "formatted_national": formatted_national,
        "detected_country_code": detected_country_code,
        "detected_country_name": detected_country_name,
        "display_international": display_international,
        "is_indian_mobile": is_indian_mobile,
    }


# ------------------------------------------------------------------------------
# 2. Traditional Significance of Digits, Zero, and Missing Numbers
# ------------------------------------------------------------------------------

DIGIT_VIBRATION_MEANINGS: Dict[int, Dict[str, str]] = {
    1: {
        "planet": "Sun (Surya)",
        "keyword": "Leadership, Independence, Authority",
        "effect": "Enhances executive presence, initiative, decision-making, and individual autonomy.",
    },
    2: {
        "planet": "Moon (Chandra)",
        "keyword": "Partnership, Diplomacy, Intuition",
        "effect": "Fosters relationship building, customer empathy, receptive listening, and mediation.",
    },
    3: {
        "planet": "Jupiter (Guru)",
        "keyword": "Expansion, Optimism, Wisdom",
        "effect": "Stimulates creative expression, public relations, academic or advisory authority, and joy.",
    },
    4: {
        "planet": "Rahu (North Node)",
        "keyword": "Organization, Discipline, Systemization",
        "effect": "Builds operational stability, procedural rigor, technical architecture, and perseverance.",
    },
    5: {
        "planet": "Mercury (Budha)",
        "keyword": "Commerce, Communication, Agility",
        "effect": "Drives rapid sales transactions, omnichannel versatility, fast responses, and public networking.",
    },
    6: {
        "planet": "Venus (Shukra)",
        "keyword": "Harmony, Luxury, Client Hospitality",
        "effect": "Attracts customer affection, aesthetic appreciation, premium service rapport, and domestic trust.",
    },
    7: {
        "planet": "Ketu (South Node)",
        "keyword": "Analytical Depth, Research, Spiritual Insight",
        "effect": "Aids investigation, technical research, counseling, specialized consulting, and discernment.",
    },
    8: {
        "planet": "Saturn (Shani)",
        "keyword": "Executive Governance, Wealth Accumulation, Durability",
        "effect": "Anchors commercial governance, institutional credibility, financial management, and long-term contracts.",
    },
    9: {
        "planet": "Mars (Mangala)",
        "keyword": "Dynamic Energy, Decisive Action, Humanitarian Zeal",
        "effect": "Promotes high-tempo execution, bold leadership, emergency responsiveness, and competitive assertiveness.",
    },
    0: {
        "planet": "Cosmic Void / Cipher (Brahma / Infinity)",
        "keyword": "Amplification, Cyclical Reset, Latent Potential",
        "effect": "Acts as an intensifying magnifier for the adjacent digits. Multiple zeros represent sudden transformational resets or spiritual infinity.",
    },
}

MISSING_DIGIT_LESSONS: Dict[int, str] = {
    1: "Missing 1: May indicate hesitation in taking proactive leadership; benefits from cultivating decisive independence.",
    2: "Missing 2: May reflect impatience in diplomatic dialogues; benefits from deliberate active listening.",
    3: "Missing 3: Indicates potential reserve in self-expression or marketing; benefits from structured promotional outreach.",
    4: "Missing 4: Points to a need for strict operational routines, records, and follow-through discipline.",
    5: "Missing 5: Suggests resistance to sudden routine changes or rapid mobile communications; benefits from agility.",
    6: "Missing 6: Represents a need to nurture long-term client relationships and focus on quality and hospitality.",
    7: "Missing 7: Indicates a tendency to make surface conclusions; benefits from deeper due diligence and analytical verification.",
    8: "Missing 8: Highlights a need for structured financial budgeting, formal contracts, and long-term asset management.",
    9: "Missing 9: Suggests potential reluctance to push projects through to final completion; benefits from decisive closure.",
}


# ------------------------------------------------------------------------------
# 3. Sequence, Pattern & Vanity Rhythm Scoring
# ------------------------------------------------------------------------------

def analyze_patterns_and_rhythm(digits: str) -> Dict[str, Any]:
    """Detect repeated sequences, consecutive runs, mirror groupings, and compute a Vanity/Rhythm score (0-100)."""
    repeats: List[Dict[str, Any]] = []
    sequences: List[Dict[str, Any]] = []
    mirrors: List[str] = []

    # 1. Consecutive identical repeats (e.g. 777, 8888, 99)
    i = 0
    while i < len(digits):
        run_char = digits[i]
        run_len = 1
        while i + 1 < len(digits) and digits[i + 1] == run_char:
            run_len += 1
            i += 1
        if run_len >= 2:
            label = "Doublet" if run_len == 2 else "Triplet" if run_len == 3 else f"{run_len}-Repeat"
            repeats.append({
                "digit": int(run_char),
                "count": run_len,
                "pattern": run_char * run_len,
                "label": label,
            })
        i += 1

    # 2. Consecutive ascending or descending runs of length >= 3 (e.g. 123, 456, 987)
    for length in range(4, 2, -1):
        for start_idx in range(len(digits) - length + 1):
            sub = digits[start_idx:start_idx + length]
            int_sub = [int(c) for c in sub]
            is_asc = all(int_sub[k + 1] - int_sub[k] == 1 for k in range(len(int_sub) - 1))
            is_desc = all(int_sub[k] - int_sub[k + 1] == 1 for k in range(len(int_sub) - 1))
            if is_asc:
                sequences.append({"sequence": sub, "type": "Ascending", "length": length})
            elif is_desc:
                sequences.append({"sequence": sub, "type": "Descending", "length": length})

    # Deduplicate overlapping sequences
    deduped_seqs: List[Dict[str, Any]] = []
    seen_subs = set()
    for s in sequences:
        if s["sequence"] not in seen_subs:
            seen_subs.add(s["sequence"])
            deduped_seqs.append(s)

    # 3. Symmetrical 3-digit or 4-digit mirror patterns (e.g. 707, 1221, 5005)
    for idx in range(len(digits) - 2):
        if digits[idx] == digits[idx + 2] and digits[idx] != digits[idx + 1]:
            mirrors.append(digits[idx:idx + 3])
    for idx in range(len(digits) - 3):
        if digits[idx:idx + 2] == digits[idx + 2:idx + 4][::-1]:
            mirrors.append(digits[idx:idx + 4])
    mirrors = list(dict.fromkeys(mirrors))

    # 4. Vanity & Memorability Score Calculation (0-100)
    # Rewards patterns that make a number easy to remember and dial
    vanity_score = 45.0  # baseline standard number

    # Repeated digit clusters reward
    for r in repeats:
        if r["count"] == 2:
            vanity_score += 6.0
        elif r["count"] == 3:
            vanity_score += 15.0
        elif r["count"] >= 4:
            vanity_score += 25.0

    # Sequential runs reward
    for s in deduped_seqs:
        vanity_score += 8.0 * s["length"]

    # Mirrors reward
    vanity_score += len(mirrors) * 4.0

    # Ending with clean round numbers (e.g. ending in 00, 000, 777)
    if digits.endswith("000"):
        vanity_score += 18.0
    elif digits.endswith("00"):
        vanity_score += 10.0
    elif len(repeats) > 0 and repeats[-1]["pattern"] == digits[-repeats[-1]["count"]:]:
        vanity_score += 12.0

    vanity_score = max(30.0, min(100.0, round(vanity_score, 1)))

    return {
        "repeats": repeats,
        "sequences": deduped_seqs,
        "mirrors": mirrors,
        "vanity_score": vanity_score,
        "is_vip_vanity": vanity_score >= 75.0,
    }


# ------------------------------------------------------------------------------
# 4. Complete Single Phone Number Numerology Calculation
# ------------------------------------------------------------------------------

def calculate_single_phone_numerology(
    digits_str: str,
    convention: str = "chaldean",
    preserve_master: bool = True,
) -> Dict[str, Any]:
    """Calculate core numerological properties of a given digit string."""
    digits_list = [int(d) for d in digits_str if d.isdigit()]
    if not digits_list:
        return {
            "digits": "",
            "compound_sum": 0,
            "root_number": 0,
            "is_master": False,
            "reduction_steps": [],
            "frequencies": {str(i): 0 for i in range(10)},
            "dominant_digits": [],
            "missing_digits": list(range(1, 10)),
            "ruling_planet": "None",
            "vibrational_meaning": "No numeric digits found.",
        }

    compound_sum = sum(digits_list)
    root_number, steps = reduce_number_steps(compound_sum, preserve_master=preserve_master)
    is_master = root_number in (11, 22, 33)

    # Digit frequency map (0-9)
    frequencies: Dict[str, int] = {str(i): 0 for i in range(10)}
    for d in digits_list:
        frequencies[str(d)] += 1

    # Find dominant digits (highest count >= 2)
    max_count = max(frequencies.values()) if frequencies else 0
    dominant_digits = [
        int(digit) for digit, count in frequencies.items()
        if count == max_count and count >= 2 and digit != "0"
    ]

    # Missing digits (1-9)
    missing_digits = [i for i in range(1, 10) if frequencies[str(i)] == 0]
    zero_count = frequencies["0"]

    # Single-digit root for ruling planet
    single_root = get_root_number(root_number)
    planet_data = get_ruling_planet(single_root)
    if isinstance(planet_data, dict):
        planet_name = planet_data.get("en", "Unknown")
    else:
        planet_name = str(planet_data)
    meaning_data = DIGIT_VIBRATION_MEANINGS.get(single_root, DIGIT_VIBRATION_MEANINGS[1])

    # Pattern and rhythm analysis
    pattern_data = analyze_patterns_and_rhythm(digits_str)

    return {
        "digits": digits_str,
        "digit_count": len(digits_list),
        "compound_sum": compound_sum,
        "root_number": root_number,
        "single_root": single_root,
        "is_master": is_master,
        "reduction_steps": steps,
        "frequencies": frequencies,
        "dominant_digits": dominant_digits,
        "missing_digits": missing_digits,
        "zero_count": zero_count,
        "ruling_planet": planet_name,
        "keyword": meaning_data["keyword"],
        "vibrational_meaning": meaning_data["effect"],
        "patterns": pattern_data,
    }


# ------------------------------------------------------------------------------
# 5. Profile & Industry Compatibility Evaluation
# ------------------------------------------------------------------------------

def evaluate_phone_dob_compatibility(
    phone_root: int,
    birth_date_str: str,
) -> Dict[str, Any]:
    """Compare phone root number against user's Psychic (Day) and Life Path numbers."""
    from .traditional import calculate_birth_psychic_number, calculate_life_path_detailed

    psychic_val, _, _ = calculate_birth_psychic_number(birth_date_str)
    lp_res = calculate_life_path_detailed(birth_date_str)
    lp_val = lp_res["life_path"]

    score_psychic, psychic_desc = assess_number_harmony(phone_root, psychic_val)
    score_lp, lp_desc = assess_number_harmony(phone_root, lp_val)

    # 50% Psychic resonance (daily conversation and temperament) + 50% Life Path (destiny opportunities)
    personal_score = round((score_psychic * 0.5) + (score_lp * 0.5), 1)

    level = (
        "Harmonious" if personal_score >= 80.0
        else "Complementary" if personal_score >= 60.0
        else "Neutral" if personal_score >= 45.0
        else "Tension"
    )

    synthesis = (
        f"Phone vibration {phone_root} resonates with your Psychic {psychic_val} ({psychic_desc}) "
        f"and Life Path {lp_val} ({lp_desc}). Overall Personal Affinity: {level} ({personal_score}%)."
    )

    return {
        "birth_date": birth_date_str,
        "psychic_number": psychic_val,
        "life_path_number": lp_val,
        "psychic_harmony_score": score_psychic,
        "life_path_harmony_score": score_lp,
        "personal_score": personal_score,
        "level": level,
        "synthesis": synthesis,
    }


def evaluate_phone_industry_compatibility(
    phone_root: int,
    industry_category: str,
) -> Dict[str, Any]:
    """Compare phone root number against business sector planetary archetypes."""
    score, desc = score_industry_harmony(phone_root, industry_category)
    profile = INDUSTRY_PROFILES.get(industry_category, INDUSTRY_PROFILES["other"])

    level = (
        "Optimal Commercial Match" if score >= 90.0
        else "Favorable Sector Resonance" if score >= 75.0
        else "Moderate Utility" if score >= 50.0
        else "Low Alignment"
    )

    return {
        "industry_category": industry_category,
        "industry_name": profile["name"],
        "planetary_ruler": profile["planetary_ruler"],
        "primary_numbers": profile["primary_numbers"],
        "secondary_numbers": profile["secondary_numbers"],
        "score": score,
        "level": level,
        "description": desc,
    }


# ------------------------------------------------------------------------------
# 6. Multi-Candidate Phone Comparison & Ranking Engine
# ------------------------------------------------------------------------------

def evaluate_phone_candidates(
    candidates_list: List[str],
    convention: str = "chaldean",
    birth_date: Optional[str] = None,
    industry_category: Optional[str] = None,
    max_candidates: int = 25,
) -> List[Dict[str, Any]]:
    """Audit, score, and rank candidate phone numbers deterministically."""
    results: List[Dict[str, Any]] = []
    seen_normalized: Set[str] = set()

    for raw in candidates_list[:max_candidates]:
        if not raw or not raw.strip():
            continue
        try:
            norm = normalize_phone_number(raw)
            clean_national = norm["national_number"]
            if clean_national in seen_normalized:
                continue
            seen_normalized.add(clean_national)

            # Calculate numerical properties on national subscriber digits
            calc_res = calculate_single_phone_numerology(clean_national, convention=convention)

            # Personal compatibility
            dob_eval: Optional[Dict[str, Any]] = None
            personal_score = 70.0
            if birth_date:
                try:
                    dob_eval = evaluate_phone_dob_compatibility(calc_res["root_number"], birth_date)
                    personal_score = dob_eval["personal_score"]
                except Exception:
                    pass

            # Industry compatibility
            ind_eval: Optional[Dict[str, Any]] = None
            industry_score = 70.0
            if industry_category:
                try:
                    ind_eval = evaluate_phone_industry_compatibility(calc_res["root_number"], industry_category)
                    industry_score = ind_eval["score"]
                except Exception:
                    pass

            vanity_score = calc_res["patterns"]["vanity_score"]

            # Weighted Composite Score
            if birth_date and industry_category:
                composite = round((personal_score * 0.40) + (industry_score * 0.30) + (vanity_score * 0.30), 1)
            elif birth_date:
                composite = round((personal_score * 0.60) + (vanity_score * 0.40), 1)
            elif industry_category:
                composite = round((industry_score * 0.60) + (vanity_score * 0.40), 1)
            else:
                composite = vanity_score

            results.append({
                "raw_input": norm["raw_input"],
                "masked_phone": norm["masked_input"],
                "national_number": norm["national_number"],
                "formatted_national": norm["formatted_national"],
                "display_international": norm["display_international"],
                "country_name": norm["detected_country_name"],
                "country_code": norm["detected_country_code"],
                "compound_sum": calc_res["compound_sum"],
                "root_number": calc_res["root_number"],
                "single_root": calc_res["single_root"],
                "is_master": calc_res["is_master"],
                "reduction_steps": calc_res["reduction_steps"],
                "frequencies": calc_res["frequencies"],
                "dominant_digits": calc_res["dominant_digits"],
                "missing_digits": calc_res["missing_digits"],
                "zero_count": calc_res["zero_count"],
                "ruling_planet": calc_res["ruling_planet"],
                "keyword": calc_res["keyword"],
                "vibrational_meaning": calc_res["vibrational_meaning"],
                "patterns": calc_res["patterns"],
                "personal_compatibility": dob_eval,
                "industry_compatibility": ind_eval,
                "personal_score": personal_score if birth_date else None,
                "industry_score": industry_score if industry_category else None,
                "vanity_score": vanity_score,
                "composite_score": composite,
                "is_favorable": composite >= 70.0,
            })
        except Exception:
            # Skip unparseable inputs in candidate list
            continue

    # Sort descending by composite score
    results.sort(key=lambda r: r["composite_score"], reverse=True)
    return results


# ------------------------------------------------------------------------------
# 7. Main Pipeline Entrypoint
# ------------------------------------------------------------------------------

def analyze_phone_numerology_full(
    phone_number: str,
    convention: str = "chaldean",
    include_country_code: bool = False,
    birth_date: Optional[str] = None,
    industry_category: Optional[str] = None,
    candidate_numbers: Optional[List[str]] = None,
    language: str = "en",
    max_candidates: int = 25,
) -> Dict[str, Any]:
    """Execute complete Phone & Mobile Number Numerology Analysis pipeline."""
    # 1. Normalize and parse primary number
    norm = normalize_phone_number(phone_number)

    # 2. Dual Calculations: National Subscriber Number vs Full International Number
    national_calc = calculate_single_phone_numerology(norm["national_number"], convention=convention)
    international_calc = calculate_single_phone_numerology(norm["all_digits"], convention=convention)

    # Select active baseline based on include_country_code toggle
    active_calc = international_calc if include_country_code else national_calc

    # 3. Personal Compatibility
    personal_eval: Optional[Dict[str, Any]] = None
    if birth_date and birth_date.strip():
        personal_eval = evaluate_phone_dob_compatibility(active_calc["root_number"], birth_date.strip())

    # 4. Industry Alignment
    industry_eval: Optional[Dict[str, Any]] = None
    if industry_category and industry_category.strip():
        industry_eval = evaluate_phone_industry_compatibility(active_calc["root_number"], industry_category.strip())

    # 5. Missing Digits Analysis text
    missing_analysis: List[Dict[str, Any]] = []
    for m in active_calc["missing_digits"]:
        missing_analysis.append({
            "digit": m,
            "lesson": MISSING_DIGIT_LESSONS.get(m, ""),
        })

    # Zero significance explanation
    zero_count = active_calc["zero_count"]
    if zero_count == 0:
        zero_meaning = "No zeros present: Steady, direct manifestation of all operative digits without cyclical resets."
    elif zero_count == 1:
        zero_meaning = "Single zero: Gently expands the energy of preceding digits, providing spiritual depth and buffer."
    else:
        zero_meaning = f"{zero_count} zeros present: Amplifies adjoining digits significantly. Indicates cyclical transformations, clean breaks, and new beginnings."

    # 6. Candidate Numbers Evaluation
    candidates_eval: List[Dict[str, Any]] = []
    pool = [phone_number]
    if candidate_numbers:
        pool.extend(candidate_numbers)

    candidates_eval = evaluate_phone_candidates(
        candidates_list=pool,
        convention=convention,
        birth_date=birth_date,
        industry_category=industry_category,
        max_candidates=max_candidates,
    )

    # 7. Scoring Methodology & Transparency Metadata
    scoring_explanation = {
        "selected_basis": "National Subscriber Digits (Standard)" if not include_country_code else "Full Digits with Country Code",
        "formula": (
            "Composite = 40% Personal Harmony + 30% Industry Alignment + 30% Vanity & Rhythm Score"
            if birth_date and industry_category
            else "Composite = 60% Personal Harmony + 40% Vanity & Rhythm Score" if birth_date
            else "Composite = 60% Industry Alignment + 40% Vanity & Rhythm Score" if industry_category
            else "Composite = 100% Vanity, Memorability & Rhythm Score"
        ),
        "weights": {
            "personal_harmony": 0.40 if (birth_date and industry_category) else 0.60 if birth_date else 0.0,
            "industry_match": 0.30 if (birth_date and industry_category) else 0.60 if industry_category else 0.0,
            "vanity_rhythm": 0.30 if (birth_date or industry_category) else 1.0,
        },
        "privacy_notice": "Phone numbers are evaluated for symbolic vibration only. We do not query telecom providers, verify network routing, or store subscriber identity.",
        "disclaimer": (
            "Phone & Mobile Number Numerology is a traditional interpretive framework for reflection on symbolic harmony, "
            "memorability, and cultural resonance. It does not guarantee personal wealth, business fortune, or telecommunications deliverability."
        ),
    }

    return {
        "raw_input": norm["raw_input"],
        "masked_phone": norm["masked_input"],
        "national_number": norm["national_number"],
        "formatted_national": norm["formatted_national"],
        "all_digits": norm["all_digits"],
        "display_international": norm["display_international"],
        "detected_country_code": norm["detected_country_code"],
        "detected_country_name": norm["detected_country_name"],
        "is_indian_mobile": norm["is_indian_mobile"],
        "system_convention": convention,
        "include_country_code": include_country_code,
        "engine_version": "1.0.0",
        "primary_analysis": active_calc,
        "national_analysis": national_calc,
        "international_analysis": international_calc,
        "missing_digits_analysis": missing_analysis,
        "zero_significance": zero_meaning,
        "personal_compatibility": personal_eval,
        "industry_compatibility": industry_eval,
        "candidates": candidates_eval,
        "scoring_explanation": scoring_explanation,
    }
