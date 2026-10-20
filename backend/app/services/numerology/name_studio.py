"""Name Suggestion and Correction Studio Engine.

Deterministic, bounded analysis and spelling correction for Numerology.
Provides:
1. Multi-component name analysis (first, middle, surname, initials, full name).
2. Deterministic candidate generation (consonant doubling, vowel alternations, phonetic swaps, Tamil transliterations).
3. Bounded generation & deduplication.
4. Multi-dimensional scoring (Numerological harmony, pronunciation preservation, spelling simplicity).
5. Pythagorean and Chaldean support with transparent letter steps.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import re
import unicodedata

from app.services.numerology.traditional import (
    calculate_name_numbers,
    reduce_number,
    reduce_number_steps,
    get_letter_info,
    normalize_text,
    strip_latin_diacritics,
    get_ruling_planet,
    calculate_birth_psychic_number,
    calculate_life_path_detailed,
    TAMIL_CONSONANTS,
    TAMIL_INDEPENDENT_VOWELS,
    TAMIL_DEPENDENT_VOWELS,
)


# ------------------------------------------------------------------------------
# 1. Planetary & Numerological Harmony Rules (Cheiro / Vedic Tradition)
# ------------------------------------------------------------------------------

# Numerological friendship relationships for root numbers 1-9
# In traditional numerology:
# 1 (Sun): Friends with 1, 2, 3, 9; Neutral with 5; Incompatible with 6, 8
# 2 (Moon): Friends with 1, 2, 3; Neutral with 7; Incompatible with 8, 9
# 3 (Jupiter): Friends with 1, 2, 3, 9; Neutral with 5, 7; Incompatible with 6
# 4 (Rahu): Friends with 1, 4, 5, 6; Neutral with 2, 7; Incompatible with 8, 9
# 5 (Mercury): Friends with 1, 4, 5, 6; Neutral with 2, 3, 7, 8, 9 (Versatile)
# 6 (Venus): Friends with 4, 5, 6, 7; Neutral with 8; Incompatible with 1, 2, 3
# 7 (Ketu): Friends with 1, 4, 5, 6; Neutral with 2, 3, 8; Incompatible with none
# 8 (Saturn): Friends with 4, 5, 6, 7; Neutral with 3; Incompatible with 1, 2, 9
# 9 (Mars): Friends with 1, 2, 3, 9; Neutral with 5, 7; Incompatible with 2, 4, 6, 8
NUMEROLOGICAL_HARMONY: Dict[int, Dict[str, Set[int]]] = {
    1: {"friends": {1, 2, 3, 9}, "neutral": {5}, "enemies": {6, 8}},
    2: {"friends": {1, 2, 3}, "neutral": {7}, "enemies": {8, 9}},
    3: {"friends": {1, 2, 3, 9}, "neutral": {5, 7}, "enemies": {6}},
    4: {"friends": {1, 4, 5, 6}, "neutral": {2, 7}, "enemies": {8, 9}},
    5: {"friends": {1, 4, 5, 6}, "neutral": {2, 3, 7, 8, 9}, "enemies": set()},
    6: {"friends": {4, 5, 6, 7}, "neutral": {8}, "enemies": {1, 2, 3}},
    7: {"friends": {1, 4, 5, 6}, "neutral": {2, 3, 8}, "enemies": set()},
    8: {"friends": {4, 5, 6, 7}, "neutral": {3}, "enemies": {1, 2, 9}},
    9: {"friends": {1, 2, 3, 9}, "neutral": {5, 7}, "enemies": {2, 4, 6, 8}},
}

# Common auspicious business/name vibration targets in traditional numerology:
BALANCED_DEFAULT_TARGETS = [1, 3, 5, 6]


def get_root_number(val: int) -> int:
    """Return single-digit root 1-9 for harmony checking, reducing master numbers."""
    if val in (11, 22, 33):
        return reduce_number(val, preserve_master=False)
    return reduce_number(val, preserve_master=False) or 1


def assess_number_harmony(candidate_val: int, target_val: int) -> Tuple[float, str]:
    """Score numerical harmony between candidate expression and target number (0-100)."""
    if candidate_val == target_val:
        return 100.0, "Exact Target Match"

    c_root = get_root_number(candidate_val)
    t_root = get_root_number(target_val)

    if c_root == t_root:
        return 92.0, "Root Vibration Match"

    rules = NUMEROLOGICAL_HARMONY.get(t_root, {"friends": set(), "neutral": set(), "enemies": set()})

    if c_root in rules.get("friends", set()):
        score = 80.0
        desc = "Harmonious Friendly Vibration"
    elif c_root in rules.get("neutral", set()):
        score = 60.0
        desc = "Neutral Compatible Vibration"
    else:
        score = 30.0
        desc = "Challenging / Incompatible Vibration"

    # Master numbers receive an intuitive bonus if not an enemy
    if candidate_val in (11, 22, 33) and score >= 60.0:
        score = min(100.0, score + 8.0)
        desc += f" (Master Number {candidate_val})"

    return score, desc


# ------------------------------------------------------------------------------
# 2. Linguistic Levenshtein & Pronunciation Preservation Scoring
# ------------------------------------------------------------------------------

def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute classic Levenshtein edit distance between two strings."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0 = list(v1)

    return v1[len(s2)]


def extract_consonant_skeleton(word: str) -> str:
    """Extract upper-case consonant skeleton for phonetic structure comparison.
    Collapses repeated geminate consonants (e.g. LL -> L) since they share the same articulation.
    """
    clean = re.sub(r"[^A-Z]", "", word.upper())
    consonants = re.sub(r"[AEIOU]", "", clean)
    return re.sub(r"(.)\1+", r"\1", consonants)


def calculate_pronunciation_preservation(original: str, candidate: str) -> float:
    """Calculate pronunciation preservation score (0-100).
    Uses Levenshtein ratio and consonant skeleton matching.
    Explicitly avoids flawed Latin Soundex for Tamil/Indic names.
    """
    orig_clean = re.sub(r"[^\w]", "", original.upper())
    cand_clean = re.sub(r"[^\w]", "", candidate.upper())

    if not orig_clean or not cand_clean:
        return 0.0

    max_len = max(len(orig_clean), len(cand_clean))
    dist = levenshtein_distance(orig_clean, cand_clean)
    lev_ratio = max(0.0, (1.0 - (dist / max_len)))

    # Consonant skeleton bonus
    skel_orig = extract_consonant_skeleton(orig_clean)
    skel_cand = extract_consonant_skeleton(cand_clean)

    if skel_orig and skel_cand:
        skel_dist = levenshtein_distance(skel_orig, skel_cand)
        skel_ratio = max(0.0, 1.0 - (skel_dist / max(len(skel_orig), len(skel_cand))))
    else:
        skel_ratio = lev_ratio

    # 60% Levenshtein + 40% Consonant skeleton
    score = (lev_ratio * 60.0) + (skel_ratio * 40.0)
    return round(min(100.0, max(0.0, score)), 1)


def calculate_spelling_simplicity(original: str, candidate: str) -> float:
    """Calculate visual and spelling simplicity score (0-100).
    Penalizes triple repeated letters, excessive length bloating, or awkward clusters.
    """
    cand_upper = candidate.upper()
    score = 100.0

    # Penalize 3+ consecutive identical letters (e.g. 'GGG')
    if re.search(r"(.)\1\1", cand_upper):
        score -= 35.0

    # Penalize length expansion > 3 characters
    len_diff = abs(len(candidate) - len(original))
    if len_diff > 3:
        score -= (len_diff - 3) * 10.0
    elif len_diff > 1:
        score -= 5.0

    # Penalize weird end clusters (e.g. trailing triple consonants)
    if re.search(r"[BCDFGHJKLMNPQRSTVWXYZ]{4,}$", cand_upper):
        score -= 20.0

    return round(max(10.0, min(100.0, score)), 1)


# ------------------------------------------------------------------------------
# 3. Name Component Analysis (First, Middle, Surname, Initials)
# ------------------------------------------------------------------------------

def analyze_name_components(full_name: str, convention: str = "pythagorean") -> Dict[str, Any]:
    """Parse name into first, middle, surname, and initials, and calculate numbers for each."""
    normalized = normalize_text(full_name)
    raw_tokens = re.split(r"[\s\-_]+", normalized)
    tokens = [t.strip(".'\",:;!()[]{}/\\") for t in raw_tokens if t.strip(".'\",:;!()[]{}/\\")]

    if not tokens:
        tokens = [full_name.strip()]

    first_name = tokens[0] if len(tokens) >= 1 else ""
    surname = tokens[-1] if len(tokens) >= 2 else ""
    middle_names = tokens[1:-1] if len(tokens) > 2 else []

    # Initials identification
    initials: List[str] = []
    for t in tokens:
        if len(t) == 1 or (len(t) == 2 and t[1] == "."):
            initials.append(t[0].upper())
        else:
            initials.append(t[0].upper())
    initials_str = ". ".join(initials) + "."

    def build_component_data(comp_name: str, comp_type: str) -> Dict[str, Any]:
        if not comp_name:
            return {
                "component_type": comp_type,
                "text": "",
                "expression": 0,
                "compound_expression": 0,
                "soul_urge": 0,
                "personality": 0,
                "reduction_steps": [],
                "letter_mappings": [],
            }
        num_res = calculate_name_numbers(comp_name, convention=convention)
        return {
            "component_type": comp_type,
            "text": comp_name,
            "expression": num_res["expression"],
            "compound_expression": num_res["compound_expression"],
            "soul_urge": num_res["soul_urge"],
            "personality": num_res["personality"],
            "reduction_steps": num_res.get("expression_steps", []),
            "letter_mappings": num_res.get("letter_mappings", []),
        }

    full_res = calculate_name_numbers(full_name, convention=convention)
    components = [
        build_component_data(first_name, "First Name"),
    ]
    if middle_names:
        components.append(build_component_data(" ".join(middle_names), "Middle Name(s)"))
    if surname:
        components.append(build_component_data(surname, "Surname / Last Name"))
    components.append(build_component_data("".join(initials), "Initials Only"))

    return {
        "full_name": full_name,
        "convention": convention,
        "expression": full_res["expression"],
        "compound_expression": full_res["compound_expression"],
        "soul_urge": full_res["soul_urge"],
        "personality": full_res["personality"],
        "is_master": full_res["expression"] in (11, 22, 33),
        "reduction_steps": full_res.get("expression_steps", []),
        "letter_mappings": full_res.get("letter_mappings", []),
        "word_breakdowns": full_res.get("word_breakdowns", []),
        "components": components,
    }


# ------------------------------------------------------------------------------
# 4. Deterministic Candidate Spelling Generator
# ------------------------------------------------------------------------------

# Common geminate consonants for natural doubling
DOUBLABLE_CONSONANTS = {"L", "R", "S", "N", "T", "M", "P", "D", "K", "B", "G"}

# Indic/Tamil to English transliteration substitution rules
INDIC_TRANSLITERATION_RULES: List[Tuple[str, str]] = [
    ("TH", "T"),
    ("T", "TH"),
    ("DH", "D"),
    ("D", "DH"),
    ("BH", "B"),
    ("B", "BH"),
    ("PH", "P"),
    ("P", "PH"),
    ("KH", "K"),
    ("K", "KH"),
    ("GH", "G"),
    ("G", "GH"),
    ("SH", "S"),
    ("S", "SH"),
    ("AN", "AM"),
    ("AM", "AN"),
    ("EE", "I"),
    ("I", "EE"),
    ("OO", "U"),
    ("U", "OO"),
    ("A", "AA"),
    ("AA", "A"),
    ("V", "W"),
    ("W", "V"),
]


def generate_candidate_spellings(
    original_name: str,
    allow_vowel_changes: bool = True,
    allow_consonant_doubling: bool = True,
    allow_phonetic_replacements: bool = True,
    custom_variations: Optional[List[str]] = None,
    max_candidates: int = 30,
) -> List[Dict[str, str]]:
    """Generate deterministic, bounded candidate spelling variations.
    Returns list of dicts: {"name": candidate_str, "variation_type": str}
    """
    candidates: Dict[str, str] = {}  # name -> variation_type

    orig_clean = original_name.strip()
    if not orig_clean:
        return []

    # Preserve exact original capitalization style
    is_all_caps = orig_clean.isupper()
    is_title_case = orig_clean.istitle()

    def format_case(s: str) -> str:
        if is_all_caps:
            return s.upper()
        if is_title_case:
            return s.title()
        return s.capitalize()

    # 1. User-provided custom variations
    if custom_variations:
        for c in custom_variations:
            c_clean = c.strip()
            if c_clean and c_clean.lower() != orig_clean.lower():
                candidates[format_case(c_clean)] = "User Custom Spelling"

    # Split name into words to apply word-level variations
    words = orig_clean.split()
    if not words:
        words = [orig_clean]

    # Process primary word (usually first name or single name)
    for w_idx, target_word in enumerate(words):
        upper_word = target_word.upper()

        # --- Rule A: Consonant Doubling & De-doubling ---
        if allow_consonant_doubling:
            # Doubling: e.g. GOKUL -> GOKULL, ARUN -> ARUNN
            for i, ch in enumerate(upper_word):
                if ch in DOUBLABLE_CONSONANTS:
                    # Avoid triple repeating
                    if i + 1 < len(upper_word) and upper_word[i + 1] == ch:
                        continue
                    if i > 0 and upper_word[i - 1] == ch:
                        continue
                    doubled = upper_word[:i] + ch + ch + upper_word[i + 1:]
                    new_words = list(words)
                    new_words[w_idx] = doubled
                    cand_name = format_case(" ".join(new_words))
                    if cand_name.lower() != orig_clean.lower() and cand_name not in candidates:
                        candidates[cand_name] = f"Consonant Doubling ('{ch}' -> '{ch}{ch}')"

            # De-doubling: e.g. GOKULL -> GOKUL, KAVITHAA -> KAVITHA
            for ch in DOUBLABLE_CONSONANTS:
                double_pattern = ch + ch
                if double_pattern in upper_word:
                    dedoubled = upper_word.replace(double_pattern, ch, 1)
                    new_words = list(words)
                    new_words[w_idx] = dedoubled
                    cand_name = format_case(" ".join(new_words))
                    if cand_name.lower() != orig_clean.lower() and cand_name not in candidates:
                        candidates[cand_name] = f"Consonant De-doubling ('{double_pattern}' -> '{ch}')"

        # --- Rule B: Vowel Alternations ---
        if allow_vowel_changes:
            vowel_swaps = [
                ("EE", "I"),
                ("I", "EE"),
                ("OO", "U"),
                ("U", "OO"),
                ("EA", "E"),
                ("AI", "AY"),
                ("AY", "AI"),
                ("IE", "Y"),
                ("Y", "I"),
            ]
            for v_from, v_to in vowel_swaps:
                if v_from in upper_word:
                    swapped = upper_word.replace(v_from, v_to, 1)
                    new_words = list(words)
                    new_words[w_idx] = swapped
                    cand_name = format_case(" ".join(new_words))
                    if cand_name.lower() != orig_clean.lower() and cand_name not in candidates:
                        candidates[cand_name] = f"Vowel Alternation ('{v_from}' -> '{v_to}')"

            # Elongated terminal vowel (e.g. DEEPA -> DEEPAA)
            if upper_word.endswith("A") and not upper_word.endswith("AA"):
                elongated = upper_word + "A"
                new_words = list(words)
                new_words[w_idx] = elongated
                cand_name = format_case(" ".join(new_words))
                if cand_name not in candidates:
                    candidates[cand_name] = "Terminal Vowel Elongation ('A' -> 'AA')"
            elif upper_word.endswith("I") and not upper_word.endswith("EE"):
                elongated = upper_word[:-1] + "EE"
                new_words = list(words)
                new_words[w_idx] = elongated
                cand_name = format_case(" ".join(new_words))
                if cand_name not in candidates:
                    candidates[cand_name] = "Terminal Vowel Elongation ('I' -> 'EE')"

        # --- Rule C: Phonetic & Transliteration Swaps ---
        if allow_phonetic_replacements:
            for p_from, p_to in INDIC_TRANSLITERATION_RULES:
                if p_from in upper_word:
                    replaced = upper_word.replace(p_from, p_to, 1)
                    new_words = list(words)
                    new_words[w_idx] = replaced
                    cand_name = format_case(" ".join(new_words))
                    if cand_name.lower() != orig_clean.lower() and cand_name not in candidates:
                        candidates[cand_name] = f"Phonetic Transliteration ('{p_from}' -> '{p_to}')"

        if len(candidates) >= max_candidates * 2:
            break

    # Convert to structured list bounded by max_candidates
    result: List[Dict[str, str]] = []
    for cand_str, var_type in candidates.items():
        result.append({"name": cand_str, "variation_type": var_type})
        if len(result) >= max_candidates:
            break

    return result


# ------------------------------------------------------------------------------
# 5. Full Studio Recommendation & Ranking Engine
# ------------------------------------------------------------------------------

def generate_and_score_name_corrections(
    original_name: str,
    convention: str = "chaldean",
    target_number: Optional[int] = None,
    birth_date: Optional[str] = None,
    custom_variations: Optional[List[str]] = None,
    language: str = "en",
    max_candidates: int = 25,
    allow_vowel_changes: bool = True,
    allow_consonant_doubling: bool = True,
    allow_phonetic_replacements: bool = True,
) -> Dict[str, Any]:
    """Execute complete Name Correction Studio workflow:
    1. Analyze original name.
    2. Determine target number (explicit or from birth date Psychic/Life Path).
    3. Generate candidate variations deterministically.
    4. Compute numbers, multi-dimensional scores (Harmony, Pronunciation, Simplicity).
    5. Rank and return side-by-side candidates with transparent explanations.
    """
    # 1. Original analysis
    orig_analysis = analyze_name_components(original_name, convention=convention)

    # 2. Target number resolution
    target_source = "User Chosen"
    psychic_num: Optional[int] = None
    life_path_num: Optional[int] = None

    if target_number is not None:
        resolved_target = target_number
    elif birth_date:
        try:
            p_val, _, _ = calculate_birth_psychic_number(birth_date)
            lp_res = calculate_life_path_detailed(birth_date)
            psychic_num = p_val
            life_path_num = lp_res["life_path"]

            # In Cheiro numerology, the Name Number should harmonize with both
            # Birth/Psychic Number (Mulank) and Life Path (Bhagyank).
            # We choose the Birth Number as primary driver, or a mutual friend.
            resolved_target = psychic_num
            target_source = f"Psychic Number (Mulank = {psychic_num}) from DOB"
        except Exception:
            resolved_target = BALANCED_DEFAULT_TARGETS[2]  # 5 (Mercury - universally friendly)
            target_source = "Default Balanced (5 - Mercury)"
    else:
        # Default target: 5 (Mercury / versatile balance) or 1 (Sun / leadership)
        resolved_target = 5
        target_source = "Default Balanced (5 - Mercury)"

    # 3. Generate candidate spellings
    raw_candidates = generate_candidate_spellings(
        original_name=original_name,
        allow_vowel_changes=allow_vowel_changes,
        allow_consonant_doubling=allow_consonant_doubling,
        allow_phonetic_replacements=allow_phonetic_replacements,
        custom_variations=custom_variations,
        max_candidates=max_candidates,
    )

    # Always evaluate the original name as the baseline candidate #0
    all_candidates_to_score = [
        {"name": original_name, "variation_type": "Original Baseline"}
    ] + raw_candidates

    # 4. Score and calculate numbers for each candidate
    scored_candidates: List[Dict[str, Any]] = []

    for item in all_candidates_to_score:
        cand_name = item["name"]
        var_type = item["variation_type"]

        cand_calc = calculate_name_numbers(cand_name, convention=convention)
        expr = cand_calc["expression"]
        compound_expr = cand_calc["compound_expression"]
        soul = cand_calc["soul_urge"]
        pers = cand_calc["personality"]
        is_master = expr in (11, 22, 33)

        # Multi-dimensional scoring
        harmony_score, harmony_desc = assess_number_harmony(expr, resolved_target)
        pron_score = calculate_pronunciation_preservation(original_name, cand_name)
        simp_score = calculate_spelling_simplicity(original_name, cand_name)

        # Composite score weighting: 50% Numerology, 30% Pronunciation, 20% Simplicity
        composite = round(
            (harmony_score * 0.50) + (pron_score * 0.30) + (simp_score * 0.20),
            1,
        )

        matches_target = (expr == resolved_target)

        # Vibrational synthesis summary
        planet = get_ruling_planet(get_root_number(expr))
        vibrational_synthesis = (
            f"Expression {expr} (Compound {compound_expr}) under {convention.title()}; "
            f"Vibrates with {planet}. {harmony_desc}."
        )

        scored_candidates.append({
            "name": cand_name,
            "variation_type": var_type,
            "expression_number": expr,
            "compound_expression": compound_expr,
            "soul_urge_number": soul,
            "personality_number": pers,
            "is_master": is_master,
            "matches_target": matches_target,
            "harmony_score": harmony_score,
            "pronunciation_score": pron_score,
            "simplicity_score": simp_score,
            "composite_score": composite,
            "letter_mappings": cand_calc.get("letter_mappings", []),
            "word_breakdowns": cand_calc.get("word_breakdowns", []),
            "reduction_steps": cand_calc.get("expression_steps", []),
            "vibrational_synthesis": vibrational_synthesis,
        })

    # Sort candidates by:
    # 1. matches_target (exact matches first)
    # 2. composite_score descending
    # 3. pronunciation_score descending
    scored_candidates.sort(
        key=lambda c: (1 if c["matches_target"] else 0, c["composite_score"], c["pronunciation_score"]),
        reverse=True,
    )

    # 5. Explanations and formula documentation
    scoring_explanation = {
        "formula": "Composite Score = (Numerological Harmony × 50%) + (Pronunciation Preservation × 30%) + (Spelling Simplicity × 20%)",
        "weights": {
            "numerological_harmony": 0.50,
            "pronunciation_preservation": 0.30,
            "spelling_simplicity": 0.20,
        },
        "target_number": resolved_target,
        "target_source": target_source,
        "psychic_number": psychic_num,
        "life_path_number": life_path_num,
        "selected_convention": convention,
        "disclaimer": (
            "Numerological scoring reflects traditional astrological associations and linguistic edit distances. "
            "No number guarantees worldly outcomes or scientific causation. It is presented as an interpretive tool "
            "for personal self-reflection and aesthetic alignment."
        ),
    }

    return {
        "original_analysis": orig_analysis,
        "target_number": resolved_target,
        "target_source": target_source,
        "candidates": scored_candidates,
        "scoring_explanation": scoring_explanation,
    }
