"""Family & Baby Numerology Studio computation engine.

Features:
1. Multi-generational family group profiles (parents, children, grandparents, siblings, household).
2. Baby name numerology evaluating user candidates and generating deterministic spelling variations under Pythagorean and Chaldean traditions.
3. Multi-dimensional candidate scoring (DOB harmony, parents harmony, pronunciation, simplicity, composite score).
4. Parent-child, sibling, and pairwise compatibility matrix with planetary dynamics, shared nurturing strengths, growth edges, and parenting dialogue prompts.
5. Family-wide vibrational summary: 1-9 root frequency distribution, dominant/missing vibrations, elemental balance, and non-deterministic ethical guidance.
"""

from collections import Counter
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.services.numerology.traditional import (
    calculate_name_numbers,
    reduce_number,
    reduce_number_steps,
    get_letter_info,
    normalize_text,
    get_ruling_planet,
    calculate_birth_psychic_number,
    calculate_life_path_detailed,
    detect_karmic_debts,
    get_interpretation_for_number,
    ENGINE_VERSION,
)
from app.services.numerology.name_studio import (
    NUMEROLOGICAL_HARMONY,
    assess_number_harmony,
    calculate_pronunciation_preservation,
    calculate_spelling_simplicity,
    generate_candidate_spellings,
    get_root_number,
)
from app.services.numerology.marriage_studio import (
    NUMBER_ARCHETYPES,
    PLANET_DYNAMIC_DESCRIPTIONS,
)

# ------------------------------------------------------------------------------
# 1. Elemental Classifications for Root Numbers 1-9
# ------------------------------------------------------------------------------

ELEMENT_MAP: Dict[int, str] = {
    1: "Fire",       # Sun (Surya) - Vitality, will, inspiration
    2: "Water",      # Moon (Chandra) - Emotion, intuition, empathy
    3: "Air/Ether",  # Jupiter (Guru) - Expansion, intellect, wisdom
    4: "Earth",      # Rahu - Stability, structure, practical boundaries
    5: "Air/Ether",  # Mercury (Budha) - Adaptability, speech, curiosity
    6: "Earth",      # Venus (Shukra) - Harmony, aesthetic, family nurturance
    7: "Water",      # Ketu - Deep introspection, mystical inquiry
    8: "Earth",      # Saturn (Shani) - Responsibility, perseverance, karma
    9: "Fire",       # Mars (Mangala) - Passion, courage, humanitarian drive
    11: "Air/Ether", # Master Illuminator
    22: "Earth",     # Master Pragmatic Architect
    33: "Water",     # Master Compassionate Guide
}

ROLE_TITLES: Dict[str, Dict[str, str]] = {
    "father": {"en": "Father / Parent 1", "ta": "தந்தை"},
    "mother": {"en": "Mother / Parent 2", "ta": "தாய்"},
    "parent": {"en": "Parent", "ta": "பெற்றோர்"},
    "child": {"en": "Child", "ta": "குழந்தை"},
    "baby": {"en": "Baby / Newborn", "ta": "பச்சிளங்குழந்தை"},
    "grandfather": {"en": "Grandfather", "ta": "தாத்தா"},
    "grandmother": {"en": "Grandmother", "ta": "பாட்டி"},
    "sibling": {"en": "Sibling", "ta": "உடன்பிறப்பு"},
    "other": {"en": "Household Member", "ta": "குடும்ப உறுப்பினர்"},
}


def resolve_planet_name(num: Optional[int], lang: str = "en") -> str:
    """Safely resolve ruling planet name to a localized string."""
    if not num:
        return "Unknown"
    p = get_ruling_planet(num)
    if isinstance(p, dict):
        return p.get(lang, p.get("en", "Unknown"))
    return str(p)


def get_harmony_score(val_a: Optional[int], val_b: Optional[int]) -> Tuple[float, str]:
    """Safely obtain numerical harmony score and description between two vibrations."""
    if not val_a or not val_b:
        return 75.0, "Neutral"
    res = assess_number_harmony(val_a, val_b)
    if isinstance(res, (tuple, list)):
        return float(res[0]), str(res[1])
    return float(res), "Harmonious"


# ------------------------------------------------------------------------------
# 2. Individual Family Member Computation
# ------------------------------------------------------------------------------

def compute_family_member_profile(
    *args: Any,
    system_convention: str = "pythagorean",
    language: str = "en",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Compute individual numerology profile for a single family member.
    
    Accepts a dictionary, positional args (id, name, role, birth_date, convention, language), or kwargs.
    """
    data: Dict[str, Any] = {}
    if args:
        if len(args) == 1 and isinstance(args[0], dict):
            data.update(args[0])
        else:
            arg_names = ["id", "name", "role", "birth_date", "convention", "language"]
            for i, a in enumerate(args):
                if i < len(arg_names):
                    data[arg_names[i]] = a
    data.update(kwargs)

    mem_id = str(data.get("id") or data.get("member_id") or "member")
    name = (data.get("name") or data.get("preferred_name") or "").strip()
    dob_str = (data.get("birth_date") or "").strip()
    role = (data.get("role") or data.get("relationship") or "child").lower()
    surname = (data.get("surname") or "").strip()
    conv = data.get("convention") or system_convention or "pythagorean"
    lang = data.get("language") or language or "en"

    psychic_num: Optional[int] = None
    psychic_planet: Optional[str] = None
    life_path_num: Optional[int] = None
    life_path_planet: Optional[str] = None
    is_lp_master = False
    reduction_steps: List[str] = []

    # 1. Date of Birth analysis if valid DOB provided (YYYY-MM-DD)
    if dob_str and len(dob_str) == 10 and dob_str[4] == "-" and dob_str[7] == "-":
        try:
            parts = [int(p) for p in dob_str.split("-")]
            d = parts[2]
            psy_num, _, psy_data = calculate_birth_psychic_number(dob_str)
            psychic_num = psy_num
            raw_planet = psy_data.get("planet")
            if isinstance(raw_planet, dict):
                psychic_planet = raw_planet.get(lang, raw_planet.get("en", "Unknown"))
            else:
                psychic_planet = str(raw_planet) if raw_planet else resolve_planet_name(psychic_num, lang)

            lp_res = calculate_life_path_detailed(dob_str)
            life_path_num = lp_res["life_path"]
            life_path_planet = resolve_planet_name(life_path_num, lang)
            is_lp_master = life_path_num in (11, 22, 33)
            reduction_steps.append(
                f"DOB {dob_str}: Day {d} -> Psychic {psychic_num}; Life Path Period Sum -> {life_path_num}"
            )
        except Exception:
            pass

    # 2. Name analysis if name provided
    expression_num: Optional[int] = None
    compound_expr: Optional[int] = None
    soul_urge_num: Optional[int] = None
    personality_num: Optional[int] = None
    karmic_debts: List[int] = []

    full_display_name = f"{name} {surname}".strip() if surname and surname not in name else name
    if full_display_name:
        name_res = calculate_name_numbers(full_display_name, convention=conv)
        expression_num = name_res["expression"]
        compound_expr = name_res["compound_expression"]
        soul_urge_num = name_res["soul_urge"]
        personality_num = name_res["personality"]
        reduction_steps.append(
            f"Name '{full_display_name}' ({conv.capitalize()}): Compound {compound_expr} -> Expression {expression_num}"
        )

        kd_items = detect_karmic_debts(
            birth_date=dob_str if (dob_str and len(dob_str) == 10) else "2000-01-01",
            name=full_display_name,
            lang=lang,
            lp_compound=life_path_num,
            expr_compound=compound_expr,
            soul_compound=soul_urge_num,
        )
        karmic_debts = [k["number"] for k in kd_items]

    # Archetype & element
    primary_num = life_path_num or psychic_num or expression_num or 1
    archetype_data = NUMBER_ARCHETYPES.get(primary_num, NUMBER_ARCHETYPES.get(1, {}))
    archetype_str = archetype_data.get(lang, archetype_data.get("en", "The Initiator"))
    element_str = ELEMENT_MAP.get(primary_num, "Air/Ether")

    # Short summary
    role_label = ROLE_TITLES.get(role, {}).get(lang, role.capitalize())
    short_summary = f"{role_label} • Archetype: {archetype_str} ({element_str} Element)"
    if psychic_num and life_path_num:
        short_summary += f" • Mulank {psychic_num} / Bhagyank {life_path_num}"

    ruling_planet_final = life_path_planet or psychic_planet or get_ruling_planet(primary_num)

    return {
        "id": mem_id,
        "name": full_display_name or role.capitalize(),
        "role": role,
        "relationship": role,
        "birth_date": dob_str or None,
        "birth_psychic_number": psychic_num,
        "birth_psychic_planet": psychic_planet,
        "life_path_number": life_path_num,
        "life_path_planet": life_path_planet,
        "is_life_path_master": is_lp_master,
        "expression_number": expression_num,
        "compound_expression": compound_expr,
        "soul_urge_number": soul_urge_num,
        "personality_number": personality_num,
        "karmic_debts": karmic_debts,
        "archetype": archetype_str,
        "archetype_label": archetype_str,
        "ruling_planet": ruling_planet_final,
        "dominant_vibration": primary_num,
        "element": element_str,
        "reduction_steps": reduction_steps,
        "short_summary": short_summary,
        "has_birth_data": bool(dob_str),
        "has_name_data": bool(full_display_name),
    }


# ------------------------------------------------------------------------------
# 3. Pairwise Harmony & Nurturing Prompts
# ------------------------------------------------------------------------------

def _determine_relationship_label(role_a: str, role_b: str, lang: str = "en") -> str:
    r_a, r_b = role_a.lower(), role_b.lower()
    parents = {"father", "mother", "parent"}
    children = {"child", "baby", "son", "daughter"}

    if (r_a in parents and r_b in children) or (r_b in parents and r_a in children):
        return "பெற்றோர்–குழந்தை பிணைப்பு" if lang == "ta" else "parent-child"
    if r_a in parents and r_b in parents:
        return "பெற்றோர் கூட்டாண்மை" if lang == "ta" else "parenting partnership"
    if (r_a in children and r_b in children) or r_a == "sibling" or r_b == "sibling":
        return "உடன்பிறப்பு நல்லிணக்கம்" if lang == "ta" else "sibling"
    if "grand" in r_a or "grand" in r_b:
        return "தலைமுறை இணைப்பு" if lang == "ta" else "intergenerational"
    return "குடும்ப பிணைப்பு" if lang == "ta" else "family resonance"


def evaluate_family_pair(
    person_a: Dict[str, Any],
    person_b: Dict[str, Any],
    language: str = "en",
) -> Dict[str, Any]:
    """Evaluate pairwise numerological synergy between two family members."""
    id_a = person_a.get("id", "")
    id_b = person_b.get("id", "")
    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")
    role_a = person_a.get("role") or person_a.get("relationship") or "member"
    role_b = person_b.get("role") or person_b.get("relationship") or "member"

    rel_label = _determine_relationship_label(role_a, role_b, language)

    # 1. Psychic number harmony
    psy_a = person_a.get("birth_psychic_number")
    psy_b = person_b.get("birth_psychic_number")
    psy_score = round(get_harmony_score(psy_a, psy_b)[0]) if psy_a and psy_b else 75

    # 2. Life Path harmony
    lp_a = person_a.get("life_path_number")
    lp_b = person_b.get("life_path_number")
    lp_score = round(get_harmony_score(lp_a, lp_b)[0]) if lp_a and lp_b else 75

    # 3. Expression harmony
    ex_a = person_a.get("expression_number")
    ex_b = person_b.get("expression_number")
    ex_score = round(get_harmony_score(ex_a, ex_b)[0]) if ex_a and ex_b else None

    # Weighted Composite
    if ex_score is not None and lp_a and psy_a and lp_b and psy_b:
        composite_score = round((lp_score * 0.45) + (psy_score * 0.40) + (ex_score * 0.15))
    elif lp_a and psy_a and lp_b and psy_b:
        composite_score = round((lp_score * 0.55) + (psy_score * 0.45))
    elif ex_score is not None:
        composite_score = ex_score
    else:
        composite_score = 75

    # Harmony Level
    if composite_score >= 88:
        level = "உயர்ந்த ஆன்ம இணக்கம்" if language == "ta" else "Exceptional"
    elif composite_score >= 76:
        level = "ஆரோக்கியமான நல்லுறவு" if language == "ta" else "Harmonious"
    elif composite_score >= 65:
        level = "சமநிலை தேவைப்படும் பிணைப்பு" if language == "ta" else "Dynamic Growth"
    else:
        level = "பொறுமையும் வழிகாட்டலும் தேவை" if language == "ta" else "Neutral"

    # Planetary flow
    plan_a = person_a.get("life_path_planet") or person_a.get("birth_psychic_planet") or "Sun"
    plan_b = person_b.get("life_path_planet") or person_b.get("birth_psychic_planet") or "Moon"
    planetary_dynamic = f"{plan_a} ↔ {plan_b} Flow"

    # Nurturing Strengths & Growth Edges
    root_a = lp_a or psy_a or 1
    root_b = lp_b or psy_b or 1
    shared_strengths: List[str] = []
    growth_edges: List[str] = []

    if root_a == root_b:
        shared_strengths.append(
            "ஒரே அதிர்வு கொண்டிருப்பதால் பரஸ்பர உணர்வுகளை மிக எளிதில் புரிந்து கொள்ளும் இயல்பு."
            if language == "ta"
            else "Shared core vibration creates natural mirroring and intuitive mutual empathy."
        )
        growth_edges.append(
            "இருவருக்கும் ஒரே விதமான பிடிவாதம் அல்லது உணர்ச்சி வெளிப்பாடு ஏற்பட வாய்ப்புண்டு."
            if language == "ta"
            else "Identical temperaments may amplify shared stubbornness during stressful moments."
        )
        nurturing_prompt = (
            "இருவரின் தனித்துவமான ஆர்வங்களை அங்கீகரித்து ஒருவருக்கொருவர் இடம் கொடுப்பது எப்படி?"
            if language == "ta"
            else "How can you validate each other's independence while celebrating your shared traits?"
        )
    else:
        shared_strengths.append(
            f"ஒருவரின் வலிமை ({person_a.get('archetype', 'Archetype A')}) மற்றவரின் தேவையை ({person_b.get('archetype', 'Archetype B')}) நிறைவு செய்கிறது."
            if language == "ta"
            else f"Complementary qualities: {person_a.get('archetype', 'A')} gracefully balances {person_b.get('archetype', 'B')}."
        )
        growth_edges.append(
            "இருவரின் முடிவெடுக்கும் வேகமும் எதிர்பார்ப்புகளும் வேறுபடலாம்; அமைதியான உரையாடல் தேவை."
            if language == "ta"
            else "Different communication rhythms — one may need immediate action while the other needs reflective space."
        )
        nurturing_prompt = (
            "குழந்தையின் அல்லது உறுப்பினரின் இயல்பான வேகத்தை மதித்து பொறுமையுடன் வழிகாட்டுவது எப்படி?"
            if language == "ta"
            else "How can you adapt your expectations to match this family member's natural tempo without rushing them?"
        )

    return {
        "person_a_id": id_a,
        "person_a_name": name_a,
        "member_a_name": name_a,
        "person_a_role": role_a,
        "person_b_id": id_b,
        "person_b_name": name_b,
        "member_b_name": name_b,
        "person_b_role": role_b,
        "relationship_type": rel_label,
        "psychic_harmony_score": psy_score,
        "life_path_harmony_score": lp_score,
        "expression_harmony_score": ex_score,
        "composite_harmony_score": composite_score,
        "compatibility_score": composite_score,
        "harmony_level": level,
        "planetary_dynamic": planetary_dynamic,
        "shared_strengths": shared_strengths,
        "growth_edges": growth_edges,
        "nurturing_prompt": nurturing_prompt,
        "parenting_dialogue_prompt": nurturing_prompt,
    }


# ------------------------------------------------------------------------------
# 4. Baby Name Candidates Evaluation
# ------------------------------------------------------------------------------

def evaluate_baby_name_candidates(
    candidate_names: Optional[List[str]] = None,
    parents_members: Optional[List[Dict[str, Any]]] = None,
    baby_dob: Optional[str] = None,
    surname: Optional[str] = None,
    target_root: Optional[int] = None,
    system_convention: str = "pythagorean",
    generate_suggestions: bool = True,
    language: str = "en",
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """Analyze baby candidate names and generate deterministic variations under Pythagorean/Chaldean."""
    raw_candidates = candidate_names or kwargs.get("candidates") or []
    parents = parents_members or kwargs.get("parents") or []
    b_dob = baby_dob or kwargs.get("baby_birth_date")
    target_r = target_root or kwargs.get("target_root_number")
    conv = kwargs.get("convention") or system_convention or "pythagorean"
    gen_variations = kwargs.get("auto_generate_variations") if "auto_generate_variations" in kwargs else generate_suggestions
    parent_vibs = kwargs.get("parent_vibrations") or []

    all_candidates: List[Tuple[str, bool, str]] = []
    seen_names: Set[str] = set()

    # 1. Process user candidate names
    for raw in raw_candidates:
        clean = raw.strip()
        if clean and clean.upper() not in seen_names:
            seen_names.add(clean.upper())
            all_candidates.append((clean, False, "user_provided"))

            if gen_variations and len(all_candidates) < 15:
                variations = generate_candidate_spellings(clean, max_candidates=6)
                for var_name, var_type in variations:
                    if var_name.upper() not in seen_names:
                        seen_names.add(var_name.upper())
                        all_candidates.append((var_name, True, var_type))

    # Baby DOB targets if known
    baby_psy_target: Optional[int] = None
    baby_lp_target: Optional[int] = None
    if b_dob and len(b_dob) == 10 and b_dob[4] == "-" and b_dob[7] == "-":
        try:
            baby_psy_target, _, _ = calculate_birth_psychic_number(b_dob)
            baby_lp_target = calculate_life_path_detailed(b_dob)["life_path"]
        except Exception:
            pass

    # Parent anchor numbers
    parent_numbers: List[int] = list(parent_vibs)
    for p in parents:
        if p.get("life_path_number"):
            parent_numbers.append(p["life_path_number"])
        if p.get("birth_psychic_number"):
            parent_numbers.append(p["birth_psychic_number"])
    if not parent_numbers:
        parent_numbers = [1, 3, 5, 6]  # universal auspicious vibrations if no parents entered

    results: List[Dict[str, Any]] = []

    for name_text, is_gen, var_type in all_candidates:
        full_tested_name = f"{name_text} {surname}".strip() if surname else name_text

        # 1. Pythagorean numbers
        pyth_res = calculate_name_numbers(full_tested_name, convention="pythagorean")
        pyth_expr = pyth_res["expression"]
        pyth_comp = pyth_res["compound_expression"]

        # 2. Chaldean numbers
        chald_res = calculate_name_numbers(full_tested_name, convention="chaldean")
        chald_expr = chald_res["expression"]
        chald_comp = chald_res["compound_expression"]

        active_res = pyth_res if conv.lower() == "pythagorean" else chald_res
        active_expr = active_res["expression"]
        active_comp = active_res["compound_expression"]
        soul_urge = active_res["soul_urge"]
        personality = active_res["personality"]
        is_master = active_expr in (11, 22, 33)

        # 3. DOB Harmony Score
        if baby_lp_target and baby_psy_target:
            score_lp, _ = get_harmony_score(active_expr, baby_lp_target)
            score_psy, _ = get_harmony_score(active_expr, baby_psy_target)
            dob_harmony = round((score_lp * 0.60) + (score_psy * 0.40))
        elif baby_psy_target:
            score_psy, _ = get_harmony_score(active_expr, baby_psy_target)
            dob_harmony = round(score_psy)
        else:
            dob_harmony = 80

        # 4. Parents Harmony Score
        parent_scores = [get_harmony_score(active_expr, p_num)[0] for p_num in parent_numbers]
        parent_harmony = round(sum(parent_scores) / len(parent_scores)) if parent_scores else 80

        # 5. Target Root match boost
        target_boost = 0
        if target_r and active_expr == target_r:
            target_boost = 10

        # 6. Pronunciation & Simplicity
        ref_orig = raw_candidates[0] if raw_candidates else name_text
        pron_score = calculate_pronunciation_preservation(ref_orig, name_text)
        simp_score = calculate_spelling_simplicity(ref_orig, name_text)

        # Master number bonus
        master_bonus = 6 if is_master else 0

        # Composite Score
        composite_score = round(
            (dob_harmony * 0.35)
            + (parent_harmony * 0.30)
            + (pron_score * 0.15)
            + (simp_score * 0.20)
            + target_boost
            + master_bonus
        )
        composite_score = min(100, max(0, composite_score))

        arch_data = NUMBER_ARCHETYPES.get(active_expr, NUMBER_ARCHETYPES.get(1, {}))
        arch_title = arch_data.get(language, arch_data.get("en", "The Initiator"))
        planet = resolve_planet_name(active_expr, language)

        combined_harmony = round((dob_harmony + parent_harmony) / 2)
        vibrational_meaning = (
            f"அதிர்வு எண் {active_expr} ({arch_title}) • ஆளும் கிரகம்: {planet}. "
            f"பெற்றோர் மற்றும் குழந்தையின் எண்களுடன் {combined_harmony}% ஏற்புத்திறன் கொண்டது."
            if language == "ta"
            else f"Vibration Root {active_expr} ({arch_title}) • Ruling Planet: {planet}. "
                 f"Resonates with {combined_harmony}% family harmony and balanced acoustic clarity."
        )

        reduction_steps = [
            f"Pythagorean: Compound {pyth_comp} -> Root {pyth_expr}",
            f"Chaldean: Compound {chald_comp} -> Root {chald_expr}",
            f"Active Selection ({conv.capitalize()}): Compound {active_comp} -> Root {active_expr}",
        ]

        results.append({
            "name": name_text,
            "candidate_name": name_text,
            "is_generated": is_gen,
            "variation_type": var_type.replace("_", " ").title(),
            "pythagorean_expression": pyth_expr,
            "pythagorean_compound": pyth_comp,
            "chaldean_expression": chald_expr,
            "chaldean_compound": chald_comp,
            "active_expression": active_expr,
            "active_compound": active_comp,
            "soul_urge": soul_urge,
            "personality": personality,
            "ruling_planet": planet,
            "archetype": arch_title,
            "dob_harmony_score": dob_harmony,
            "parent_harmony_score": parent_harmony,
            "parents_harmony_score": parent_harmony,
            "pronunciation_score": pron_score,
            "simplicity_score": simp_score,
            "composite_score": composite_score,
            "is_master": is_master,
            "reduction_steps": reduction_steps,
            "letter_mappings": active_res["letter_mappings"],
            "vibrational_synthesis": vibrational_meaning,
        })

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results


# ------------------------------------------------------------------------------
# 5. Full Family Studio Orchestrator
# ------------------------------------------------------------------------------

def analyze_family_numerology_full(
    family_name: str = "Family",
    members: Optional[List[Dict[str, Any]]] = None,
    candidate_names: Optional[List[str]] = None,
    baby_dob: Optional[str] = None,
    surname: Optional[str] = None,
    target_root: Optional[int] = None,
    system_convention: str = "pythagorean",
    generate_suggestions: bool = True,
    language: str = "en",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Execute complete Family & Baby Numerology Studio computation."""
    f_name = (family_name or "Family").strip() or ("குடும்பம்" if language == "ta" else "The Family")
    raw_members = members if members is not None else kwargs.get("members_data") or []
    raw_candidates = candidate_names if candidate_names is not None else kwargs.get("baby_candidates") or []
    gen_suggestions = kwargs.get("auto_generate_variations") if "auto_generate_variations" in kwargs else generate_suggestions
    target_r = target_root or kwargs.get("target_root_number")
    convention = "chaldean" if (system_convention or kwargs.get("convention") or "").lower() == "chaldean" else "pythagorean"
    lang = "ta" if language == "ta" else "en"

    # 1. Evaluate all family members
    evaluated_members: List[Dict[str, Any]] = []
    parents: List[Dict[str, Any]] = []

    for m in raw_members:
        prof = compute_family_member_profile(m, system_convention=convention, language=lang)
        evaluated_members.append(prof)
        if prof["role"] in ("father", "mother", "parent"):
            parents.append(prof)

    # 2. Pairwise Harmonization
    pairwise_comparisons: List[Dict[str, Any]] = []
    n = len(evaluated_members)
    for i in range(n):
        for j in range(i + 1, n):
            pair_res = evaluate_family_pair(evaluated_members[i], evaluated_members[j], language=lang)
            pairwise_comparisons.append(pair_res)

    # Average Family Harmony Score
    if pairwise_comparisons:
        overall_score = round(sum(p["composite_harmony_score"] for p in pairwise_comparisons) / len(pairwise_comparisons))
    else:
        overall_score = 85

    if overall_score >= 85:
        overall_level = "மிகச் சிறந்த குடும்ப ஒற்றுமை" if lang == "ta" else "Harmonious Collective Resonance"
    elif overall_score >= 72:
        overall_level = "வளரக்கூடிய நல்லுறவு" if lang == "ta" else "Balanced & Supportive Dynamics"
    else:
        overall_level = "புரிதலும் பொறுமையும் தேவை" if lang == "ta" else "Conscious Family Dialogue Needed"

    # 3. Family-Wide Number Distribution (1-9)
    all_numbers: List[int] = []
    for em in evaluated_members:
        if em.get("birth_psychic_number"):
            all_numbers.append(get_root_number(em["birth_psychic_number"]))
        if em.get("life_path_number"):
            all_numbers.append(get_root_number(em["life_path_number"]))

    total_count = len(all_numbers) or 1
    counts = Counter(all_numbers)

    number_distribution: List[Dict[str, Any]] = []
    for digit in range(1, 10):
        c = counts.get(digit, 0)
        pct = round((c / total_count) * 100, 1)
        carrying_members = [
            em["name"] for em in evaluated_members
            if em.get("birth_psychic_number") == digit or em.get("life_path_number") == digit
        ]
        number_distribution.append({
            "number": digit,
            "count": c,
            "percentage": pct,
            "ruling_planet": resolve_planet_name(digit, lang),
            "element": ELEMENT_MAP.get(digit, "Air/Ether"),
            "members_with_number": carrying_members,
        })

    # Dominant and missing vibrations
    dominant: List[int] = [d["number"] for d in number_distribution if d["count"] > 1]
    if not dominant:
        dominant = [d["number"] for d in sorted(number_distribution, key=lambda x: x["count"], reverse=True)[:2] if d["count"] > 0]
    missing: List[int] = [d["number"] for d in number_distribution if d["count"] == 0]

    # Elemental balance
    element_counts: Dict[str, int] = {"Fire": 0, "Water": 0, "Air": 0, "Earth": 0}
    for num in all_numbers:
        el = ELEMENT_MAP.get(num, "Air/Ether")
        if "Fire" in el:
            element_counts["Fire"] += 1
        elif "Water" in el:
            element_counts["Water"] += 1
        elif "Earth" in el:
            element_counts["Earth"] += 1
        else:
            element_counts["Air"] += 1

    dom_element = max(element_counts, key=element_counts.get) if all_numbers else "Balanced"
    elemental_balance: Dict[str, Any] = {
        "Fire": element_counts["Fire"],
        "Water": element_counts["Water"],
        "Air": element_counts["Air"],
        "Earth": element_counts["Earth"],
        "dominant_element": dom_element,
    }

    # 4. Evaluate Baby Candidates
    baby_candidates_results = evaluate_baby_name_candidates(
        candidate_names=raw_candidates,
        parents_members=parents,
        baby_dob=baby_dob,
        surname=surname,
        target_root=target_r,
        system_convention=convention,
        generate_suggestions=gen_suggestions,
        language=lang,
    )

    # 5. Qualitative Family Themes
    family_strengths: List[str] = [
        "குடும்ப உறுப்பினர்களிடையே பரஸ்பர ஆதரவு மற்றும் அன்பான பரிமாற்றம்."
        if lang == "ta"
        else "Diverse foundational vibrations bring versatile problem-solving and mutual encouragement.",
    ]
    if dominant:
        dom_planets = [resolve_planet_name(d, lang) for d in dominant]
        family_strengths.append(
            f"முதன்மை அதிர்வுகள் ({', '.join(map(str, dominant))}) குடும்பத்திற்கு வலுவான ஒற்றுமையையும் வழிகாட்டலையும் தருகின்றன."
            if lang == "ta"
            else f"Dominant root vibration(s) {', '.join(map(str, dominant))} ({', '.join(dom_planets)}) foster core family resilience."
        )

    family_challenges: List[str] = [
        "வேலைப்பளு மற்றும் அவசர முடிவுகளின் போது ஒருவரின் தனிப்பட்ட அமைதிக்கு இடையூறு ஏற்படாமல் காப்பது அவசியம்."
        if lang == "ta"
        else "Balancing active group schedules with individual requirements for quiet contemplation and decompression.",
    ]
    if missing:
        family_challenges.append(
            f"குடும்பத்தில் இல்லாத அதிர்வுகளை ({', '.join(map(str, missing))}) திட்டமிட்ட ஒழுங்கு மற்றும் பொறுமை மூலம் வளர்த்துக் கொள்ள வேண்டும்."
            if lang == "ta"
            else f"Unrepresented vibrations ({', '.join(map(str, missing))}) invite the family to consciously cultivate the missing virtues of structure or adaptability."
        )

    reflection_questions: List[str] = [
        "குழந்தையின் தனிப்பட்ட ஆர்வங்களை எந்தவித எதிர்பார்ப்புமின்றி நாம் எவ்வாறு உற்சாகப்படுத்துகிறோம்?"
        if lang == "ta"
        else "How do we actively celebrate our child's authentic interests without imposing parental projections?",
        "குடும்ப முடிவுகளை எடுக்கும் போது அனைவரின் கருத்துக்களுக்கும் சமமான மதிப்பளிக்கப்படுகிறதா?"
        if lang == "ta"
        else "During major household transitions, do we give space for every family member to voice their emotional comfort level?",
        "வேற்றுமைகளை முரண்பாடாக பார்க்காமல், ஒருவருக்கொருவர் கற்றுக்கொள்ளும் வாய்ப்பாக எவ்வாறு மாற்றலாம்?"
        if lang == "ta"
        else "How can contrasting individual temperaments be transformed into cooperative learning opportunities rather than friction points?",
    ]

    synthesis_text = (
        f"'{f_name}' குடும்பத்திற்கான எண் கணித பகுப்பாய்வு {overall_score}% நல்லிணக்க மதிப்பீட்டுடன் அமைந்துள்ளது. "
        f"{len(evaluated_members)} உறுப்பினர்களின் அதிர்வுகள் ஒருங்கிணைக்கப்பட்டு, குழந்தைகளின் நல்வாழ்விற்கான வழிகாட்டல்கள் தொகுக்கப்பட்டுள்ளன."
        if lang == "ta"
        else f"Comprehensive family vibrational analysis for '{f_name}' reflects an overall harmony score of {overall_score}% ({overall_level}). "
             f"Synthesizes {len(evaluated_members)} household members across multi-generational dimensions and baby naming resonance."
    )

    scoring_explanation = {
        "formula": "Weighted Average of Multi-Member Pairwise Matrices: 50% Life Path Synergy + 40% Psychic Alignment + 10% Name Vibration",
        "composite_scale": "0 to 100 non-deterministic philosophical harmony scale",
        "system": f"{convention.capitalize()} Tradition",
        "baby_candidate_weights": "50% Parent/DOB Resonance + 30% Spelling Simplicity + 20% Acoustic Clarity",
    }

    disclaimer_text = (
        "எண் கணித பகுப்பாய்வுகள் தனிநபர் மற்றும் குடும்ப சுய ஆய்வுக்காக மட்டுமே வழங்கப்படுகின்றன. "
        "இவை குழந்தையின் எதிர்காலம், ஆரோக்கியம் அல்லது குடும்ப உறவுகளின் உத்தரவாதங்கள் அல்ல. "
        "பெற்றோரின் அன்பு, புரிதல், நல்வழிகாட்டல் மற்றும் விவேகமே குடும்பத்தின் அமைதிக்கு உறுதுணையானவை."
        if lang == "ta"
        else "Numerological calculations and family compatibility assessments are provided for self-reflection, philosophical enrichment, "
             "and constructive dialogue. They are not deterministic scientific predictions or medical/psychological evaluations. "
             "No number guarantees a child's future health, behaviour, or achievement. Parental empathy, respectful communication, and unconditional love remain paramount."
    )

    return {
        "family_name": f_name,
        "system_convention": convention,
        "language": lang,
        "members": evaluated_members,
        "members_evaluated": evaluated_members,
        "pairwise_dynamics": pairwise_comparisons,
        "pairwise_comparisons": pairwise_comparisons,
        "distribution": number_distribution,
        "number_distribution": number_distribution,
        "dominant_vibrations": dominant,
        "missing_vibrations": missing,
        "elemental_balance": elemental_balance,
        "candidate_names": baby_candidates_results,
        "baby_name_candidates": baby_candidates_results,
        "family_harmony_score": overall_score,
        "overall_family_harmony_score": overall_score,
        "overall_family_harmony_level": overall_level,
        "scoring_formula_explanation": scoring_explanation,
        "family_strengths": family_strengths,
        "family_challenges": family_challenges,
        "reflection_prompts": reflection_questions,
        "reflection_questions": reflection_questions,
        "overall_synthesis": synthesis_text,
        "engine_version": ENGINE_VERSION,
        "disclaimer": disclaimer_text,
    }
