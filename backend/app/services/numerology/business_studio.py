"""Business & Brand Numerology Studio Engine.

Provides deterministic analysis, corporate normalization, multi-founder partnership alignment,
industry vibrational harmonies, and candidate brand ranking under Pythagorean and Chaldean traditions.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import re

from app.services.numerology.traditional import (
    calculate_name_numbers,
    reduce_number,
    reduce_number_steps,
    get_letter_info,
    normalize_text,
    get_ruling_planet,
    calculate_birth_psychic_number,
    calculate_life_path_detailed,
)
from app.services.numerology.name_studio import (
    NUMEROLOGICAL_HARMONY,
    get_root_number,
    assess_number_harmony,
    calculate_pronunciation_preservation,
    calculate_spelling_simplicity,
    generate_candidate_spellings,
)

# ------------------------------------------------------------------------------
# 1. Corporate Legal Suffixes & Normalization
# ------------------------------------------------------------------------------

# Ordered from longest/most specific to shortest
CORPORATE_SUFFIXES: List[str] = [
    r"\bPRIVATE\s+LIMITED\b",
    r"\bPVT\.?\s*LTD\.?\b",
    r"\bLIMITED\s+LIABILITY\s+PARTNERSHIP\b",
    r"\bLIMITED\s+LIABILITY\s+COMPANY\b",
    r"\bPUBLIC\s+LIMITED\s+COMPANY\b",
    r"\bCO\.?\s*LTD\.?\b",
    r"\bLIMITED\b",
    r"\bLTD\.?\b",
    r"\bLLP\b",
    r"\bINCORPORATED\b",
    r"\bINC\.?\b",
    r"\bCORPORATION\b",
    r"\bCORP\.?\b",
    r"\bLLC\b",
    r"\bPLC\b",
    r"\bGMBH\b",
    r"\bS\.?A\.?\b",
    r"\bB\.?V\.?\b",
    r"\bN\.?V\.?\b",
]

COMPILED_SUFFIX_REGEXES = [
    (re.compile(pattern, re.IGNORECASE), pattern.replace(r"\b", "").replace(r"\s+", " ").replace("\\", ""))
    for pattern in CORPORATE_SUFFIXES
]


def normalize_business_name(legal_name: str) -> Dict[str, Any]:
    """Parse and normalize legal business name into cleaned brand name, detected suffixes, and acronym.
    Never silently discards suffixes; exposes both representations transparently.
    """
    clean_legal = legal_name.strip()
    detected_suffixes: List[str] = []
    brand_working = clean_legal

    for regex, label in COMPILED_SUFFIX_REGEXES:
        match = regex.search(brand_working)
        if match:
            matched_str = match.group(0).strip(" .")
            if matched_str.upper() not in [s.upper() for s in detected_suffixes]:
                detected_suffixes.append(matched_str)
            # Remove suffix from brand string
            brand_working = regex.sub("", brand_working).strip(" ,.-&")

    # Clean residual trailing punctuation
    brand_name = re.sub(r"[\s,.-]+$", "", brand_working).strip()
    if not brand_name:
        brand_name = clean_legal

    # Extract Acronym (first letter of each significant word)
    words = [w for w in re.split(r"[\s\-_]+", brand_name) if w and w[0].isalnum()]
    acronym = "".join(w[0].upper() for w in words) if words else clean_legal[:3].upper()

    return {
        "full_legal_name": clean_legal,
        "cleaned_brand_name": brand_name,
        "detected_suffixes": detected_suffixes,
        "acronym": acronym,
        "is_modified": brand_name.lower() != clean_legal.lower(),
    }


# ------------------------------------------------------------------------------
# 2. Industry Vibrations & Traditional Classifications
# ------------------------------------------------------------------------------

# Traditional numerological and planetary archetypes for business sectors.
# Documented as traditional interpretive associations, not deterministic predictors.
INDUSTRY_PROFILES: Dict[str, Dict[str, Any]] = {
    "technology": {
        "name": "Technology, Software & AI",
        "primary_numbers": [5, 4, 1],
        "secondary_numbers": [7],
        "planetary_ruler": "Mercury (Budha) & Rahu / Uranus",
        "traditional_rationale": (
            "Mercury rules data transmission, computational logic, communication, and commercial speed. "
            "Rahu governs disruptive breakthroughs, high technology, and unconventional platforms."
        ),
    },
    "retail": {
        "name": "Retail, E-commerce & Consumer Goods",
        "primary_numbers": [5, 6, 3],
        "secondary_numbers": [2],
        "planetary_ruler": "Mercury (Trade) & Venus (Consumer Aesthetics)",
        "traditional_rationale": (
            "Number 5 energizes foot traffic and digital transactions. Number 6 attracts consumer appeal, "
            "lifestyle desirability, and brand loyalty. Number 3 fosters market expansion."
        ),
    },
    "education": {
        "name": "Education, Publishing & Consulting",
        "primary_numbers": [3, 5, 7],
        "secondary_numbers": [1],
        "planetary_ruler": "Jupiter (Guru) & Mercury (Budha)",
        "traditional_rationale": (
            "Jupiter is the cosmic teacher governing wisdom, higher knowledge, curriculum, and mentorship. "
            "Number 7 drives research rigor and analytical inquiry."
        ),
    },
    "healthcare": {
        "name": "Healthcare, Medicine & Wellness",
        "primary_numbers": [1, 2, 9],
        "secondary_numbers": [6, 3],
        "planetary_ruler": "Sun (Surya - Vitality) & Moon (Chandra - Care)",
        "traditional_rationale": (
            "Sun governs cellular vitality and health recovery. Moon governs psychological empathy and nursing. "
            "Mars (9) brings diagnostic precision and surgical mastery."
        ),
    },
    "finance": {
        "name": "Finance, Banking & Professional Services",
        "primary_numbers": [8, 3, 5],
        "secondary_numbers": [1],
        "planetary_ruler": "Saturn (Shani - Wealth Structures) & Jupiter (Prosperity)",
        "traditional_rationale": (
            "Number 8 establishes corporate endurance, fiduciary trust, asset governance, and institutional authority. "
            "Number 3 attracts continuous liquidity and venture growth."
        ),
    },
    "manufacturing": {
        "name": "Manufacturing, Real Estate & Heavy Industry",
        "primary_numbers": [8, 4, 9],
        "secondary_numbers": [1],
        "planetary_ruler": "Saturn (Earth/Metals) & Mars (Land/Structures)",
        "traditional_rationale": (
            "Saturn governs heavy machinery, industrial durability, and long manufacturing cycles. "
            "Mars and Rahu govern immovable property, construction, and engineering infrastructure."
        ),
    },
    "astrology": {
        "name": "Astrology, Spiritual & Metaphysical Services",
        "primary_numbers": [7, 3, 9],
        "secondary_numbers": [2, 11],
        "planetary_ruler": "Ketu (Intuition) & Jupiter (Vedic Vidya)",
        "traditional_rationale": (
            "Ketu governs esoteric wisdom, intuitive perception, and unseen forces. Jupiter governs "
            "Dharma and authentic Jyotish shastra. Number 9 provides astronomical calculation power."
        ),
    },
    "creative": {
        "name": "Creative Arts, Entertainment & Media",
        "primary_numbers": [3, 6, 5],
        "secondary_numbers": [2],
        "planetary_ruler": "Venus (Shukra - Fine Arts) & Jupiter (Creative Speech)",
        "traditional_rationale": (
            "Venus commands design elegance, cinematic vision, and sensory enjoyment. Number 3 commands "
            "stage presence, literary publishing, and charismatic oratory."
        ),
    },
    "other": {
        "name": "General Enterprise & Diversified Business",
        "primary_numbers": [1, 3, 5, 6],
        "secondary_numbers": [8],
        "planetary_ruler": "Universal Auspicious Business Vibrations",
        "traditional_rationale": (
            "Classic auspicious enterprise numbers: 1 (Initiative & Market Leadership), 3 (Growth & Goodwill), "
            "5 (Commercial Agility & Versatility), and 6 (Customer Magnetism & Harmony)."
        ),
    },
}


def score_industry_harmony(expression_num: int, industry_key: str) -> Tuple[float, str]:
    """Calculate industry vibrational harmony (0-100) based on traditional sector correspondences."""
    category = INDUSTRY_PROFILES.get(industry_key.lower(), INDUSTRY_PROFILES["other"])
    primary = category["primary_numbers"]
    secondary = category["secondary_numbers"]

    root_expr = get_root_number(expression_num)

    if expression_num in primary or root_expr in primary:
        return 100.0, f"Primary Industry Match ({category['name']})"
    if expression_num in secondary or root_expr in secondary:
        return 80.0, f"Secondary Industry Harmony ({category['name']})"

    # General planetary friendliness against the first primary number
    lead_target = primary[0]
    base_score, _ = assess_number_harmony(expression_num, lead_target)
    desc = f"Moderate Alignment with {category['name']}"
    return max(40.0, min(75.0, base_score)), desc


# ------------------------------------------------------------------------------
# 3. Founder & Multi-Partner Compatibility Engine
# ------------------------------------------------------------------------------

def evaluate_single_founder_harmony(
    founder: Dict[str, Any],
    brand_expression: int,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Calculate a single founder's compatibility against the brand name vibration."""
    founder_name = founder.get("name", "").strip()
    birth_date = founder.get("birth_date", "").strip() if founder.get("birth_date") else None
    role = founder.get("role", "Founder")
    share = founder.get("share_percentage")

    psychic_num: Optional[int] = None
    lp_num: Optional[int] = None
    psychic_harmony: Optional[float] = None
    lp_harmony: Optional[float] = None

    if birth_date:
        try:
            p_val, _, _ = calculate_birth_psychic_number(birth_date)
            lp_res = calculate_life_path_detailed(birth_date)
            psychic_num = p_val
            lp_num = lp_res["life_path"]

            score_p, _ = assess_number_harmony(brand_expression, psychic_num)
            score_lp, _ = assess_number_harmony(brand_expression, lp_num)
            psychic_harmony = score_p
            lp_harmony = score_lp

            # 50% Psychic (Innate disposition) + 50% Life Path (Destiny trajectory)
            alignment_score = round((score_p * 0.5) + (score_lp * 0.5), 1)
        except Exception:
            birth_date = None

    if not birth_date:
        # Fall back to founder's personal name expression
        f_name_calc = calculate_name_numbers(founder_name, convention=convention)
        f_expr = f_name_calc["expression"]
        score_name, _ = assess_number_harmony(brand_expression, f_expr)
        alignment_score = round(score_name, 1)

    # Classify alignment qualitative level
    if alignment_score >= 85:
        level = "Excellent"
        notes = f"Strong mutual resonance between brand ({brand_expression}) and {founder_name}."
    elif alignment_score >= 65:
        level = "Harmonious"
        notes = f"Supportive commercial relationship with positive cooperative flow."
    elif alignment_score >= 50:
        level = "Neutral"
        notes = f"Neutral vibrational interaction; success depends primarily on operational execution."
    else:
        level = "Challenging"
        notes = f"Contrasting planetary polarities; recommended to balance with favorable brand colors or secondary partners."

    return {
        "name": founder_name,
        "birth_date": birth_date,
        "role": role,
        "share_percentage": share,
        "psychic_number": psychic_num,
        "life_path_number": lp_num,
        "name_expression": calculate_name_numbers(founder_name, convention=convention)["expression"],
        "psychic_harmony_score": psychic_harmony,
        "life_path_harmony_score": lp_harmony,
        "alignment_score": alignment_score,
        "alignment_level": level,
        "notes": notes,
    }


def evaluate_partnership_matrix(
    founders: List[Dict[str, Any]],
    brand_expression: int,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Evaluate multi-founder partnership harmony against brand name."""
    if not founders:
        return {
            "overall_partnership_score": 100.0,
            "has_friction": False,
            "founder_results": [],
            "synthesis": "Sole proprietorship / public entity mode (no founders specified).",
        }

    results: List[Dict[str, Any]] = []
    total_weight = 0.0
    weighted_sum = 0.0

    has_friction = False
    friction_founders: List[str] = []

    for f in founders:
        if not f.get("name", "").strip():
            continue
        eval_res = evaluate_single_founder_harmony(f, brand_expression, convention=convention)
        results.append(eval_res)

        score = eval_res["alignment_score"]
        if score < 50:
            has_friction = True
            friction_founders.append(eval_res["name"])

        share = eval_res.get("share_percentage")
        if share is not None and share > 0:
            weighted_sum += (score * share)
            total_weight += share
        else:
            weighted_sum += score
            total_weight += 1.0

    if not results:
        return {
            "overall_partnership_score": 100.0,
            "has_friction": False,
            "founder_results": [],
            "synthesis": "No valid founder names provided.",
        }

    overall_score = round(weighted_sum / total_weight, 1)

    if has_friction:
        synthesis = (
            f"Overall partnership score: {overall_score}%. Note: Contrasting vibrational alignment detected for: "
            f"{', '.join(friction_founders)}. Consider harmonizing with appropriate brand sub-headings or launch dates."
        )
    else:
        synthesis = (
            f"Overall partnership harmony: {overall_score}%. Positive planetary alignment across all {len(results)} partner(s)."
        )

    return {
        "overall_partnership_score": overall_score,
        "has_friction": has_friction,
        "friction_founders": friction_founders,
        "founder_results": results,
        "synthesis": synthesis,
    }


# ------------------------------------------------------------------------------
# 4. Tagline & Domain/Handle Analysis
# ------------------------------------------------------------------------------

def analyze_tagline(
    tagline: str,
    brand_expression: int,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Calculate tagline / slogan numerological vibration and synergy with the brand name."""
    clean = tagline.strip()
    if not clean:
        return {}

    calc = calculate_name_numbers(clean, convention=convention)
    slogan_expr = calc["expression"]
    synergy_score, desc = assess_number_harmony(slogan_expr, brand_expression)

    return {
        "tagline": clean,
        "expression_number": slogan_expr,
        "compound_expression": calc["compound_expression"],
        "synergy_score": synergy_score,
        "synergy_interpretation": (
            f"Tagline expression {slogan_expr} ({calc['compound_expression']}) has {desc.lower()} "
            f"with brand expression {brand_expression}."
        ),
    }


def analyze_domain_or_handle(
    handle: str,
    brand_expression: int,
    convention: str = "chaldean",
) -> Dict[str, Any]:
    """Analyze domain or social handle vibration, stripping protocol, TLD, and @ symbols."""
    clean = handle.strip()
    if not clean:
        return {}

    # Strip URL prefixes
    clean_handle = re.sub(r"^https?://(www\.)?", "", clean, flags=re.IGNORECASE)
    # Strip TLD (.com, .io, .ai, .in, .co.in, etc.)
    clean_handle = re.sub(r"\.[a-z]{2,}(\.[a-z]{2,})?(/.*)?$", "", clean_handle, flags=re.IGNORECASE)
    # Strip leading @ or trailing slashes
    clean_handle = clean_handle.lstrip("@").rstrip("/")

    if not clean_handle:
        clean_handle = clean

    calc = calculate_name_numbers(clean_handle, convention=convention)
    handle_expr = calc["expression"]
    matches_brand = (handle_expr == brand_expression)

    return {
        "raw_handle": clean,
        "clean_handle": clean_handle,
        "expression_number": handle_expr,
        "compound_expression": calc["compound_expression"],
        "matches_brand": matches_brand,
    }


# ------------------------------------------------------------------------------
# 5. Business Candidate Evaluation & Studio Workflow
# ------------------------------------------------------------------------------

def evaluate_business_brand_candidates(
    legal_name: str,
    brand_name: Optional[str] = None,
    tagline: Optional[str] = None,
    domain_or_handle: Optional[str] = None,
    convention: str = "chaldean",
    industry_category: str = "other",
    founders: Optional[List[Dict[str, Any]]] = None,
    custom_candidates: Optional[List[str]] = None,
    max_candidates: int = 25,
    language: str = "en",
) -> Dict[str, Any]:
    """Execute complete Business & Brand Numerology Studio evaluation:
    1. Normalize legal vs brand name and extract corporate suffixes.
    2. Analyze industry vibration profiles.
    3. Generate and score candidates (Legal, Normalized Brand, Acronym, Variations, Custom).
    4. Compute multi-founder partnership matrix for each candidate.
    5. Evaluate tagline and domain synergy.
    6. Return ranked candidates with transparent letter mappings and composite scores.
    """
    founders_list = founders or []
    norm = normalize_business_name(legal_name)
    eff_brand = (brand_name.strip() if brand_name and brand_name.strip() else norm["cleaned_brand_name"])

    # 1. Candidate Generation Pool
    candidate_pool: List[Tuple[str, str]] = []  # (name, candidate_type)

    # Candidate 0: Full Legal Name (Baseline)
    candidate_pool.append((norm["full_legal_name"], "Full Legal Entity Name"))

    # Candidate 1: Normalized Brand Name
    if eff_brand.lower() != norm["full_legal_name"].lower():
        candidate_pool.append((eff_brand, "Public Brand Name (Suffixes Stripped)"))

    # Candidate 2: Acronym / Short Form
    if norm["acronym"] and norm["acronym"].lower() != eff_brand.lower():
        candidate_pool.append((norm["acronym"], "Acronym / Short Trading Form"))

    # Candidate 3: User Custom Candidates
    if custom_candidates:
        for c in custom_candidates:
            c_clean = c.strip()
            if c_clean and c_clean.lower() not in [p[0].lower() for p in candidate_pool]:
                candidate_pool.append((c_clean, "User Custom Proposal"))

    # Candidate 4: Algorithmic Spelling Variations of the Brand Name
    algo_variations = generate_candidate_spellings(
        original_name=eff_brand,
        allow_vowel_changes=True,
        allow_consonant_doubling=True,
        allow_phonetic_replacements=True,
        max_candidates=max_candidates,
    )
    for v in algo_variations:
        cand_str = v["name"].strip()
        if cand_str.lower() not in [p[0].lower() for p in candidate_pool]:
            candidate_pool.append((cand_str, f"Brand Tuning: {v['variation_type']}"))

    # 2. Evaluate all candidates in pool
    scored_candidates: List[Dict[str, Any]] = []

    for name_str, cand_type in candidate_pool[:max_candidates]:
        name_calc = calculate_name_numbers(name_str, convention=convention)
        expr = name_calc["expression"]
        comp = name_calc["compound_expression"]
        soul = name_calc["soul_urge"]
        pers = name_calc["personality"]
        is_master = expr in (11, 22, 33)

        # A. Industry Harmony
        ind_score, ind_desc = score_industry_harmony(expr, industry_category)

        # B. Multi-Founder Alignment
        partner_matrix = evaluate_partnership_matrix(founders_list, expr, convention=convention)
        founder_score = partner_matrix["overall_partnership_score"]

        # C. Pronunciation & Simplicity (relative to eff_brand)
        pron_score = calculate_pronunciation_preservation(eff_brand, name_str)
        simp_score = calculate_spelling_simplicity(eff_brand, name_str)

        # D. Composite Business Score
        # 35% Founder Harmony + 25% Industry Alignment + 20% Pronunciation + 20% Simplicity
        composite = round(
            (founder_score * 0.35)
            + (ind_score * 0.25)
            + (pron_score * 0.20)
            + (simp_score * 0.20),
            1,
        )

        planet = get_ruling_planet(get_root_number(expr))
        synthesis = (
            f"Vibrates with {planet} (Expression {expr}, Compound {comp}). "
            f"Industry: {ind_desc}. Partnership Alignment: {founder_score}%."
        )

        scored_candidates.append({
            "name": name_str,
            "candidate_type": cand_type,
            "expression_number": expr,
            "compound_expression": comp,
            "soul_urge_number": soul,
            "personality_number": pers,
            "is_master": is_master,
            "industry_harmony_score": ind_score,
            "founder_harmony_score": founder_score,
            "pronunciation_score": pron_score,
            "simplicity_score": simp_score,
            "composite_score": composite,
            "is_favorable": composite >= 75.0,
            "vibrational_synthesis": synthesis,
            "letter_mappings": name_calc.get("letter_mappings", []),
            "reduction_steps": name_calc.get("expression_steps", []),
            "founder_alignments": partner_matrix["founder_results"],
        })

    # Sort candidates by composite_score descending
    scored_candidates.sort(key=lambda c: c["composite_score"], reverse=True)

    # 3. Dedicated Legal vs Brand Baseline Extraction
    legal_analysis = next(
        (c for c in scored_candidates if c["name"].lower() == norm["full_legal_name"].lower()),
        scored_candidates[0] if scored_candidates else None,
    )
    brand_analysis = next(
        (c for c in scored_candidates if c["name"].lower() == eff_brand.lower()),
        legal_analysis,
    )

    # 4. Tagline & Domain Analysis
    tagline_result = analyze_tagline(tagline, brand_analysis["expression_number"], convention=convention) if tagline else None
    domain_result = analyze_domain_or_handle(domain_or_handle, brand_analysis["expression_number"], convention=convention) if domain_or_handle else None

    # 5. Partnership Summary for primary Brand
    brand_partner_matrix = evaluate_partnership_matrix(founders_list, brand_analysis["expression_number"], convention=convention)

    # 6. Industry Metadata
    ind_data = INDUSTRY_PROFILES.get(industry_category.lower(), INDUSTRY_PROFILES["other"])

    # 7. Scoring Explanation
    scoring_explanation = {
        "formula": (
            "Composite Business Score = (Founder Harmony × 35%) + (Industry Alignment × 25%) "
            "+ (Pronunciation Preservation × 20%) + (Spelling Simplicity × 20%)"
        ),
        "weights": {
            "founder_harmony": 0.35,
            "industry_alignment": 0.25,
            "pronunciation_preservation": 0.20,
            "spelling_simplicity": 0.20,
        },
        "industry_profile": {
            "key": industry_category,
            "name": ind_data["name"],
            "primary_numbers": ind_data["primary_numbers"],
            "planetary_ruler": ind_data["planetary_ruler"],
            "rationale": ind_data["traditional_rationale"],
        },
        "selected_convention": convention,
        "disclaimer": (
            "Business and brand numerological evaluations are traditional interpretive frameworks for aesthetic, "
            "vibrational, and cultural alignment. They do not constitute financial advice or guarantee commercial success."
        ),
    }

    return {
        "legal_name": norm["full_legal_name"],
        "normalized_brand_name": eff_brand,
        "acronym": norm["acronym"],
        "detected_suffixes": norm["detected_suffixes"],
        "system_convention": convention,
        "industry_category": industry_category,
        "industry_vibrations": ind_data,
        "legal_analysis": legal_analysis,
        "brand_analysis": brand_analysis,
        "tagline_analysis": tagline_result,
        "domain_analysis": domain_result,
        "partnership_matrix": brand_partner_matrix,
        "candidates": scored_candidates,
        "scoring_explanation": scoring_explanation,
    }
