"""Marriage Compatibility by Numerology Studio Engine.

Deterministic, rule-based couple numerology analysis comparing Person A and Person B.
Provides:
1. Individual Profiles: Birth/Psychic Number (Mulank), Life Path Number (Bhagyank),
   Expression, Soul Urge, Personality numbers, Master numbers (11, 22, 33), and Karmic Debts (13, 14, 16, 19).
2. Couple Compatibility Analysis:
   - Birth/Psychic Number compatibility
   - Life Path compatibility
   - Name/Expression compatibility (when names supplied)
   - Soul Urge (Emotional longing) and Personality (Communication) compatibility
3. Emotional and Communication themes
4. Shared strengths and potential areas of disagreement
5. Practical conversation prompts for relationship growth
6. Transparent weighted scoring with documented limitations and ethical disclaimers.
7. Support for Pythagorean and Chaldean conventions with bilingual (English/Tamil) presentation.
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
    detect_karmic_debts,
    get_interpretation_for_number,
    ENGINE_VERSION,
)
from app.services.numerology.name_studio import (
    NUMEROLOGICAL_HARMONY,
    get_root_number,
)

# ------------------------------------------------------------------------------
# 1. Number Archetype Titles & Planetary Rulerships
# ------------------------------------------------------------------------------

NUMBER_ARCHETYPES: Dict[int, Dict[str, str]] = {
    1: {"en": "The Pioneer & Initiator", "ta": "முன்னோடி மற்றும் வழிநடத்துபவர்"},
    2: {"en": "The Peacemaker & Empath", "ta": "அமைதி விரும்பி மற்றும் ஆதரவாளர்"},
    3: {"en": "The Creative Expresser", "ta": "படைப்பாற்றல் பேச்சாளர்"},
    4: {"en": "The Practical Anchor", "ta": "நம்பகமான அமைப்பாளர்"},
    5: {"en": "The Dynamic Explorer", "ta": "சுதந்திர சாகச விரும்பி"},
    6: {"en": "The Nurturing Guardian", "ta": "பாதுகாப்பாளர் மற்றும் வழிகாட்டி"},
    7: {"en": "The Analytical Seeker", "ta": "மெய்யறிவு ஆராய்ச்சியாளர்"},
    8: {"en": "The Visionary Leader", "ta": "நிர்வாகி மற்றும் சாதனையாளர்"},
    9: {"en": "The Universal Humanitarian", "ta": "உலகளாவிய மனிதநேயர்"},
    11: {"en": "Master Intuitive Illuminator", "ta": "மாஸ்டர் உள்ளுணர்வு ஒளிவிளக்கு"},
    22: {"en": "Master Pragmatic Architect", "ta": "மாஸ்டர் மாபெரும் நிர்மாணிப்பாளர்"},
    33: {"en": "Master Compassionate Teacher", "ta": "மாஸ்டர் தெய்வீக ஆசான்"},
}

PLANET_DYNAMIC_DESCRIPTIONS: Dict[Tuple[int, int], Dict[str, str]] = {
    (1, 1): {
        "en": "Dual Sun Energies: Mutual respect for ambition and leadership; both must consciously share the spotlight.",
        "ta": "இரு சூரிய அதிர்வுகள்: பரஸ்பர லட்சியம் மற்றும் தலைமைத்துவ மரியாதை; சமமாக அங்கீகரிக்கப்பட வேண்டும்.",
    },
    (1, 2): {
        "en": "Sun & Moon: Classical complementary polarity; the dynamic initiator meets the intuitive supporter.",
        "ta": "சூரியன் மற்றும் சந்திரன்: செவ்வியல் இணைவு; தொடங்கும் ஆற்றலும் அரவணைக்கும் உள்ளமும் இணைகிறது.",
    },
    (1, 3): {
        "en": "Sun & Jupiter: Expansive enthusiasm; optimistic synergy where action meets creative imagination.",
        "ta": "சூரியன் மற்றும் குரு: பெரும் உற்சாகம்; லட்சியமும் படைப்புத்திறனும் இணையும் நல்வாய்ப்பு.",
    },
    (1, 4): {
        "en": "Sun & Rahu: Innovation meets structure; 1 initiates visionary ideas while 4 builds stable execution.",
        "ta": "சூரியன் மற்றும் ராகு: புதிய சிந்தனைகளும் உறுதியான செயல்வடிவமும் இணையும் தளம்.",
    },
    (1, 5): {
        "en": "Sun & Mercury: High-velocity momentum; mutual enthusiasm for progress, innovation, and lively discourse.",
        "ta": "சூரியன் மற்றும் புதன்: துரித வேகம்; புதிய மாற்றங்கள் மற்றும் அறிவார்ந்த உரையாடல்கள்.",
    },
    (1, 6): {
        "en": "Sun & Venus: Contrasting priorities; 1 seeks independence and public triumph while 6 prioritizes domestic devotion.",
        "ta": "சூரியன் மற்றும் சுக்கிரன்: மாறுபட்ட விருப்பங்கள்; 1 தனித்துவத்தையும் 6 குடும்ப அமைதியையும் விரும்பும்.",
    },
    (1, 7): {
        "en": "Sun & Ketu: Extroverted leadership meets introverted contemplation; requires giving 7 space for quiet reflection.",
        "ta": "சூரியன் மற்றும் கேது: வெளிப்படையான தலைமையும் உள்முக சிந்தனையும்; தனிப்பட்ட அமைதிக்கு இடம் தர வேண்டும்.",
    },
    (1, 8): {
        "en": "Sun & Saturn: Power and endurance; two powerful wills that flourish when spheres of responsibility are distinctly demarcated.",
        "ta": "சூரியன் மற்றும் சனி: ஆளுமையும் உறுதியும்; பொறுப்புகளை பிரித்துக் கொண்டு செயல்பட வேண்டிய கூட்டாண்மை.",
    },
    (1, 9): {
        "en": "Sun & Mars: Fiery alliance; immense shared drive, courage, and vitality; requires tempering hot temperaments with patience.",
        "ta": "சூரியன் மற்றும் செவ்வாய்: அக்னி கூட்டுறவு; தீரமும் வேகமும் மிக்கது; கோபத்தை தவிர்த்து பொறுமையைக் கடைப்பிடிக்க வேண்டும்.",
    },
}


def resolve_planet_name(num: int, lang: str = "en") -> str:
    """Return localized string for planetary ruler, unwrapping dictionary if needed."""
    p_dict = get_ruling_planet(num)
    if isinstance(p_dict, dict):
        return p_dict.get("ta" if lang == "ta" else "en", p_dict.get("en", "Unknown"))
    return str(p_dict)


# ------------------------------------------------------------------------------
# 2. Pair Compatibility Scoring
# ------------------------------------------------------------------------------

def score_pair_compatibility(num1: int, num2: int, lang: str = "en") -> Tuple[float, str, str, str]:
    """Score numerical harmony between two root or master numbers (0-100).
    Returns (score, level, planetary_dynamic, interpretation).
    """
    is_ta = (lang == "ta")
    r1 = get_root_number(num1)
    r2 = get_root_number(num2)
    is_master1 = num1 in (11, 22, 33)
    is_master2 = num2 in (11, 22, 33)

    rules1 = NUMEROLOGICAL_HARMONY.get(r1, {"friends": set(), "neutral": set(), "enemies": set()})
    rules2 = NUMEROLOGICAL_HARMONY.get(r2, {"friends": set(), "neutral": set(), "enemies": set()})

    is_mutual_friends = (r2 in rules1.get("friends", set())) and (r1 in rules2.get("friends", set()))
    is_enemy1 = r2 in rules1.get("enemies", set())
    is_enemy2 = r1 in rules2.get("enemies", set())
    is_both_enemies = is_enemy1 and is_enemy2
    is_one_enemy = is_enemy1 or is_enemy2

    p1 = resolve_planet_name(r1, lang=lang)
    p2 = resolve_planet_name(r2, lang=lang)
    planet_pair = f"{p1} & {p2}"

    if num1 == num2:
        score = 92.0
        level = "ஒரே அலைவரிசை இணக்கம்" if is_ta else "Identical Core Wavelength"
        interp = (
            f"இருவரும் எண் {num1} அதிர்வைப் பகிர்ந்து கொள்கிறார்கள். பரஸ்பர இயல்புகள் இயல்பாகவே புரிகிறது."
            if is_ta else
            f"Both share the core vibration of Number {num1}, creating immediate intuitive recognition and shared instinct."
        )
    elif r1 == r2:
        score = 88.0
        level = "அடிப்படைக் கூட்டு இணக்கம்" if is_ta else "Root Harmonic Resonance"
        interp = (
            f"இருவரின் அடிப்படை எண் {r1} ஒன்றாக இருப்பதால் உணர்வுபூர்வமான புரிதலும் பரஸ்பர மரியாதையும் இயல்பாக அமைகிறது."
            if is_ta else
            f"Root vibration {r1} aligns both profiles, offering strong underlying empathy despite differing compound expressions."
        )
    elif is_mutual_friends:
        score = 85.0
        level = "இயற்கையான நட்பு இணக்கம்" if is_ta else "Harmonious Natural Alliance"
        interp = (
            f"எண் {num1} மற்றும் எண் {num2} ஆகியவை ஜோதிட நட்பு கிரகங்களால் ஆளப்படுகின்றன. இது இயல்பான ஆதரவையும் மகிழ்ச்சியையும் தரும்."
            if is_ta else
            f"Numbers {num1} and {num2} enjoy mutual planetary friendship, fostering natural support, shared humor, and easy compromise."
        )
    elif not is_one_enemy:
        # One friend + one neutral, or both neutral
        if (r2 in rules1.get("friends", set())) or (r1 in rules2.get("friends", set())):
            score = 75.0
            level = "ஆதரவான சமநிலை" if is_ta else "Supportive Complement"
            interp = (
                f"எண் {num1} மற்றும் எண் {num2} ஆகியவை நட்பு மற்றும் நடுநிலை அதிர்வுகளைக் கொண்டுள்ளன. ஒருவருக்கொருவர் கற்றுக்கொள்ள உதவும்."
                if is_ta else
                f"Numbers {num1} and {num2} blend friendly and neutral vibrations, allowing comfortable coexistence with opportunities for personal growth."
            )
        else:
            score = 65.0
            level = "நடுநிலை சமச்சீர் நிலை" if is_ta else "Neutral Growth Balance"
            interp = (
                f"எண் {num1} மற்றும் எண் {num2} நடுநிலை ஆற்றலைக் கொண்டுள்ளன. தொடர் உரையாடலும் தெளிவான திட்டமிடலும் இணக்கத்தை வளர்க்கும்."
                if is_ta else
                f"Numbers {num1} and {num2} hold neutral energetic polarity; deliberate communication and conscious appreciation bridge natural differences."
            )
    elif is_both_enemies:
        score = 42.0
        level = "மாறுபட்ட ஆற்றல் / கவனம் தேவை" if is_ta else "Dynamic Friction / High Growth"
        interp = (
            f"எண் {num1} மற்றும் எண் {num2} மாறுபட்ட கிரக அதிர்வுகளைக் கொண்டுள்ளன. பரஸ்பர சுதந்திரத்தை மதித்து, பொறுமையுடன் செயல்பட வேண்டும்."
            if is_ta else
            f"Numbers {num1} and {num2} carry contrasting planetary rulers, highlighting differing instincts that require patience and mature boundaries."
        )
    else:
        score = 52.0
        level = "மாறுபட்ட துருவங்கள்" if is_ta else "Contrasting Polarities"
        interp = (
            f"எண் {num1} மற்றும் எண் {num2} கலவையான அணுகுமுறையைக் கொண்டுள்ளன. வேறுபாடுகளை பலவீனமாகக் கருதாமல் பலமாக மாற்ற முடியும்."
            if is_ta else
            f"Numbers {num1} and {num2} present mixed friendly and frictional polarities; clear agreements on finances and routines foster stability."
        )

    # Slight master number boost for higher spiritual empathy
    if is_master1 or is_master2:
        score = min(98.0, score + 3.0)

    # Check custom pair dynamic
    key = (min(r1, r2), max(r1, r2))
    dynamic_desc = PLANET_DYNAMIC_DESCRIPTIONS.get(key, {}).get("ta" if is_ta else "en")
    if not dynamic_desc:
        dynamic_desc = (
            f"{p1} மற்றும் {p2} கிரகங்களின் கூட்டமைப்பு."
            if is_ta else
            f"Interaction between {p1} and {p2} planetary archetypes."
        )

    return round(score, 1), level, planet_pair, interp + " " + dynamic_desc


# ------------------------------------------------------------------------------
# 3. Individual Profile Extraction
# ------------------------------------------------------------------------------

def compute_single_person_profile(
    full_name: Optional[str],
    birth_date: str,
    preferred_name: Optional[str] = None,
    surname_initials: Optional[str] = None,
    convention: str = "pythagorean",
    language: str = "en",
    person_label: str = "Person",
) -> Dict[str, Any]:
    """Compute complete individual numerology profile for marriage compatibility analysis."""
    is_ta = (language == "ta")

    # 1. Birth/Psychic Number (Mulank)
    psychic_num, psychic_method, psychic_data = calculate_birth_psychic_number(birth_date)
    psychic_planet = resolve_planet_name(psychic_num, lang=language)
    psychic_archetype = NUMBER_ARCHETYPES.get(psychic_num, {}).get("ta" if is_ta else "en", f"Vibration {psychic_num}")

    # 2. Life Path Number (Bhagyank)
    lp_res = calculate_life_path_detailed(birth_date)
    lp_num = lp_res["life_path"]
    lp_compound = lp_res["compound_period_total"]
    lp_planet = resolve_planet_name(lp_num, lang=language)
    lp_archetype = NUMBER_ARCHETYPES.get(lp_num, {}).get("ta" if is_ta else "en", f"Vibration {lp_num}")
    lp_steps = lp_res.get("period_reduction_steps", [str(lp_compound), str(lp_num)])
    is_lp_master = lp_num in (11, 22, 33)

    # 3. Optional Name Numbers (Expression, Soul Urge, Personality)
    clean_name = (full_name or "").strip()
    has_name = bool(clean_name and any(c.isalpha() for c in clean_name))

    expr_num: Optional[int] = None
    expr_compound: Optional[int] = None
    expr_planet: Optional[str] = None
    expr_steps: Optional[List[str]] = None
    is_expr_master: bool = False

    soul_num: Optional[int] = None
    soul_compound: Optional[int] = None

    pers_num: Optional[int] = None
    pers_compound: Optional[int] = None

    master_numbers_detected: Set[int] = set()
    if is_lp_master:
        master_numbers_detected.add(lp_num)
    if psychic_data.get("is_master"):
        master_numbers_detected.add(psychic_data.get("master_value", 11))

    if has_name:
        name_res = calculate_name_numbers(clean_name, convention=convention)
        expr_num = name_res["expression"]
        expr_compound = name_res["compound_expression"]
        expr_planet = resolve_planet_name(expr_num, lang=language)
        expr_steps = name_res["expression_steps"]
        is_expr_master = expr_num in (11, 22, 33)
        if is_expr_master:
            master_numbers_detected.add(expr_num)

        soul_num = name_res["soul_urge"]
        soul_compound = name_res["compound_soul_urge"]
        if soul_num in (11, 22, 33):
            master_numbers_detected.add(soul_num)

        pers_num = name_res["personality"]
        pers_compound = name_res["compound_personality"]
        if pers_num in (11, 22, 33):
            master_numbers_detected.add(pers_num)

    # 4. Karmic Debts Detection
    debts = detect_karmic_debts(
        birth_date=birth_date,
        name=clean_name if has_name else "",
        lang=language,
        lp_compound=lp_compound,
        expr_compound=expr_compound,
        soul_compound=soul_compound,
    )

    # 5. Key Attributes
    interp = get_interpretation_for_number("life_path", lp_num, lang=language)
    key_attributes = interp.get("attributes", [])

    return {
        "person_label": person_label,
        "full_name": clean_name if has_name else None,
        "preferred_name": (preferred_name or "").strip() or None,
        "surname_initials": (surname_initials or "").strip() or None,
        "birth_date": birth_date.strip(),
        "birth_psychic_number": psychic_num,
        "birth_psychic_compound": psychic_data.get("raw_day", int(birth_date.split("-")[2])),
        "birth_psychic_planet": psychic_planet,
        "birth_psychic_archetype": psychic_archetype,
        "birth_psychic_reduction_steps": psychic_data.get("reduction_steps", [str(psychic_num)]),
        "life_path_number": lp_num,
        "life_path_compound": lp_compound,
        "life_path_planet": lp_planet,
        "life_path_archetype": lp_archetype,
        "life_path_reduction_steps": lp_steps,
        "is_life_path_master": is_lp_master,
        "expression_number": expr_num,
        "expression_compound": expr_compound,
        "expression_planet": expr_planet,
        "expression_reduction_steps": expr_steps,
        "is_expression_master": is_expr_master,
        "soul_urge_number": soul_num,
        "soul_urge_compound": soul_compound,
        "personality_number": pers_num,
        "personality_compound": pers_compound,
        "master_numbers": sorted(list(master_numbers_detected)),
        "karmic_debts": debts,
        "key_attributes": key_attributes,
    }


# ------------------------------------------------------------------------------
# 4. Themes, Strengths, Challenges & Conversation Prompts Generator
# ------------------------------------------------------------------------------

def generate_relationship_themes(
    prof_a: Dict[str, Any],
    prof_b: Dict[str, Any],
    lang: str = "en",
) -> Dict[str, Any]:
    """Deterministically synthesize emotional themes, communication rhythms,
    shared strengths, potential challenges, and practical conversation prompts.
    """
    is_ta = (lang == "ta")
    lp_a = prof_a["life_path_number"]
    lp_b = prof_b["life_path_number"]
    psy_a = prof_a["birth_psychic_number"]
    psy_b = prof_b["birth_psychic_number"]
    soul_a = prof_a.get("soul_urge_number")
    soul_b = prof_b.get("soul_urge_number")
    pers_a = prof_a.get("personality_number")
    pers_b = prof_b.get("personality_number")

    strengths: List[str] = []
    challenges: List[str] = []
    emotional_themes: List[str] = []
    communication_themes: List[str] = []
    conversation_prompts: List[str] = []
    growth_recommendations: List[str] = []

    # 1. Emotional Themes
    if soul_a is not None and soul_b is not None:
        if soul_a == soul_b:
            emotional_themes.append(
                f"இருவரும் ஒரே ஆன்ம விருப்ப எண்ணான {soul_a}-ஐக் கொண்டுள்ளதால் உணர்ச்சிபூர்வமான நெருக்கம் எளிதாகிறது."
                if is_ta else
                f"Both share Soul Urge Number {soul_a}, pointing to identical core emotional longings and a shared romantic language."
            )
        else:
            emotional_themes.append(
                f"ஆன்ம எண் {soul_a} மற்றும் எண் {soul_b} உணர்ச்சித் தேவைகளில் மாறுபட்ட வெளிப்பாடுகளைக் காட்டுகின்றன."
                if is_ta else
                f"Soul Urge {soul_a} and Soul Urge {soul_b} express inner vulnerability differently, inviting patient emotional listening."
            )
    else:
        # Fallback to Psychic/Mulank for emotional baseline
        emotional_themes.append(
            f"பிறந்த நாள் எண்கள் {psy_a} மற்றும் {psy_b} அடிப்படை மனோபாவத்தை பிரதிபலிக்கின்றன."
            if is_ta else
            f"Day Numbers {psy_a} and {psy_b} shape day-to-day emotional reactions and instinctual comfort zones."
        )

    # 2. Communication Themes
    if pers_a is not None and pers_b is not None:
        communication_themes.append(
            f"வெளிப்புற ஆளுமை எண்கள் {pers_a} மற்றும் {pers_b} சமூக சூழலில் எவ்வாறு தொடர்பு கொள்கிறார்கள் என்பதை விளக்குகின்றன."
            if is_ta else
            f"Personality Numbers {pers_a} and {pers_b} define social presentation and everyday conversation rhythms."
        )
    else:
        communication_themes.append(
            f"வாழ்க்கை பாதை எண்கள் {lp_a} மற்றும் {lp_b} கருத்து பரிமாற்றத்தில் தங்களின் இயல்பான பாணியைக் காட்டுகின்றன."
            if is_ta else
            f"Life Path trajectories {lp_a} and {lp_b} govern how both partners frame priorities during discussions."
        )

    # 3. Shared Strengths
    if lp_a == lp_b:
        strengths.append(
            f"இருவரும் ஒரே வாழ்க்கை பாதை எண் ({lp_a}) கொண்டிருப்பதால் வாழ்க்கையின் முக்கிய லட்சியங்களில் உடனடி ஒருமித்த கருத்து எட்டப்படுகிறது."
            if is_ta else
            f"Shared Life Path {lp_a} creates instinctual alignment on major life milestones, core values, and life purpose."
        )
    else:
        strengths.append(
            f"எண் {lp_a} மற்றும் எண் {lp_b} இணைந்து ஒரு முழுமையான கூட்டுறவை உருவாக்கும் சமநிலையான பண்புகளை வழங்குகின்றன."
            if is_ta else
            f"The combination of Life Path {lp_a} and {lp_b} offers complementary strengths, balancing action with reflection."
        )

    if psy_a in NUMEROLOGICAL_HARMONY.get(get_root_number(psy_b), {}).get("friends", set()):
        strengths.append(
            "பிறந்த எண்கள் பரஸ்பர நட்புடன் இருப்பதால் அன்றாட பழக்கவழக்கங்களில் இனிமையான புரிதல் நிலவுகிறது."
            if is_ta else
            "Friendly Psychic Numbers cultivate effortless daily rapport, shared humor, and comfortable domestic coexistence."
        )

    if (prof_a.get("master_numbers") or prof_b.get("master_numbers")):
        strengths.append(
            "ஜாதகத்தில் மாஸ்டர் எண்கள் (11, 22, 33) அமைந்திருப்பதால் ஆழமான ஆன்மீக உணர்வும் பரஸ்பர ஊக்கமும் கிடைக்கிறது."
            if is_ta else
            "Presence of Master Numbers endows the relationship with elevated intuitive awareness and profound mutual growth."
        )

    # Ensure at least 3 strengths
    if len(strengths) < 3:
        strengths.append(
            "சுயமரியாதையும் வெளிப்படையான கருத்து பரிமாற்றமும் உறவை மேலும் வலிமைப்படுத்தும் தூண்களாகும்."
            if is_ta else
            "Both partners possess resilient individual qualities that reinforce mutual respect and long-term stability."
        )

    # 4. Potential Challenges / Growth Areas
    if psy_a in NUMEROLOGICAL_HARMONY.get(get_root_number(psy_b), {}).get("enemies", set()):
        challenges.append(
            f"பிறந்த எண்கள் {psy_a} மற்றும் {psy_b} மாறுபட்ட வேகத்தைக் காட்டுவதால் முக்கிய முடிவுகளில் அவசரப்படாமல் ஆலோசிக்க வேண்டும்."
            if is_ta else
            f"Contrasting Psychic Numbers {psy_a} and {psy_b} indicate different instinctual tempos; avoid rushing decisions under stress."
        )

    if (lp_a in (1, 8) and lp_b in (1, 8)):
        challenges.append(
            "இருவருமே வலுவான தலைமை பண்பு கொண்டிருப்பதால் குடும்ப மற்றும் நிதி முடிவுகளில் பொறுப்புகளை முன்கூட்டியே பகிர்ந்து கொள்ள வேண்டும்."
            if is_ta else
            "Both carry potent leadership and executive vibrations; prevent power struggles by demarcating clear spheres of autonomy."
        )
    elif (lp_a in (4, 7) and lp_b in (3, 5)):
        challenges.append(
            "ஒருவர் ஒழுங்கையும் திட்டமிடலையும் விரும்ப, மற்றொருவர் சுதந்திரத்தையும் மாற்றத்தையும் விரும்புவதால் வாழ்க்கை முறையில் சமரசம் தேவை."
            if is_ta else
            "Balancing routine and structure with spontaneity requires conscious pacing so neither partner feels constrained or overwhelmed."
        )

    extra_growth_points = [
        (
            "அன்றாட பணிச்சுமையின் போது உணர்வுகளை உள்ளடக்காமல் மனம் திறந்து பேசுவது அவசியமாகும்."
            if is_ta else
            "Occasional misalignments in communication styles are easily resolved when neither partner assumes unspoken intent."
        ),
        (
            "முடிவெடுக்கும் வேகத்தில் உள்ள நுட்பமான வேறுபாடுகளைப் புரிந்து கொண்டு ஒருவருக்கொருவர் அவகாசம் தர வேண்டும்."
            if is_ta else
            "Subtle differences in decision-making pacing benefit from intentional check-ins before major financial or family steps."
        ),
    ]
    for egp in extra_growth_points:
        if len(challenges) >= 2:
            break
        if egp not in challenges:
            challenges.append(egp)

    # 5. Practical Conversation Prompts for the Couple
    conversation_prompts.append(
        "நிதி திட்டமிடல், சேமிப்பு மற்றும் நீண்ட கால பாதுகாப்பு குறித்து நமது எதிர்பார்ப்புகள் என்ன?"
        if is_ta else
        "How do our individual views on financial security, saving, and investments harmoniously align for our future?"
    )
    conversation_prompts.append(
        "மன அழுத்தமான தருணங்களில் நாம் எவ்வாறு ஆதரவளிக்க விரும்புகிறோம் — அமைதியாக இருப்பதா அல்லது உடனே பேசுவதா?"
        if is_ta else
        "During periods of stress, what type of support helps most — reflective quiet space or active verbal processing?"
    )
    conversation_prompts.append(
        "நமது தனிப்பட்ட சுதந்திரத்திற்கும் குடும்ப கூட்டாண்மைக்கும் இடையே எவ்வாறு ஆரோக்கியமான எல்லைகளை அமைப்பது?"
        if is_ta else
        "What does healthy individual autonomy look like within our committed partnership?"
    )
    conversation_prompts.append(
        "வாழ்க்கையின் முக்கிய லட்சியங்களை அடைவதில் அடுத்த 3–5 ஆண்டுகளில் நாம் ஒருவருக்கொருவர் எவ்வாறு துணை நிற்கப் போகிறோம்?"
        if is_ta else
        "Over the next 3 to 5 years, how can we actively champion each other's creative, professional, and personal goals?"
    )

    # 6. Growth Recommendations
    growth_recommendations.append(
        "ஒவ்வொரு வாரமும் பரஸ்பர உணர்வுகளைப் பகிர்ந்து கொள்ளும் அமைதியான நேரத்தை ஒதுக்குங்கள்."
        if is_ta else
        "Establish a regular weekly check-in free from digital distractions to exchange appreciations and align priorities."
    )
    growth_recommendations.append(
        "முடிவுகளில் இருவரின் பலங்களையும் முழுமையாகப் பயன்படுத்தி பரஸ்பர மரியாதையை முன்னிறுத்துங்கள்."
        if is_ta else
        "Honor your differences as a shared asset rather than friction, leveraging one partner's intuition alongside the other's practicality."
    )

    return {
        "emotional_themes": emotional_themes,
        "communication_themes": communication_themes,
        "shared_strengths": strengths,
        "potential_challenges": challenges,
        "conversation_prompts": conversation_prompts,
        "growth_recommendations": growth_recommendations,
    }


# ------------------------------------------------------------------------------
# 5. Full Marriage Compatibility Pipeline
# ------------------------------------------------------------------------------

def analyze_marriage_numerology_full(
    person_a_input: Dict[str, Any],
    person_b_input: Dict[str, Any],
    convention: str = "pythagorean",
    language: str = "en",
) -> Dict[str, Any]:
    """Execute complete deterministic marriage compatibility analysis pipeline."""
    is_ta = (language == "ta")
    conv = convention.strip().lower()
    if conv not in ("pythagorean", "chaldean"):
        conv = "pythagorean"

    # 1. Compute Individual Profiles
    prof_a = compute_single_person_profile(
        full_name=person_a_input.get("full_name"),
        birth_date=person_a_input["birth_date"],
        preferred_name=person_a_input.get("preferred_name"),
        surname_initials=person_a_input.get("surname_initials"),
        convention=conv,
        language=language,
        person_label="Person A",
    )
    prof_b = compute_single_person_profile(
        full_name=person_b_input.get("full_name"),
        birth_date=person_b_input["birth_date"],
        preferred_name=person_b_input.get("preferred_name"),
        surname_initials=person_b_input.get("surname_initials"),
        convention=conv,
        language=language,
        person_label="Person B",
    )

    # 2. Evaluate Core Compatibility Components
    # Component 1: Psychic/Birth Number (Mulank)
    psy_score, psy_level, psy_planet, psy_interp = score_pair_compatibility(
        prof_a["birth_psychic_number"],
        prof_b["birth_psychic_number"],
        lang=language,
    )
    # Component 2: Life Path Number (Bhagyank)
    lp_score, lp_level, lp_planet, lp_interp = score_pair_compatibility(
        prof_a["life_path_number"],
        prof_b["life_path_number"],
        lang=language,
    )

    # Component 3 & 4: Name-derived comparisons (Expression, Soul Urge, Personality)
    has_both_names = bool(prof_a["expression_number"] and prof_b["expression_number"])

    expr_comp: Optional[Dict[str, Any]] = None
    soul_comp: Optional[Dict[str, Any]] = None
    pers_comp: Optional[Dict[str, Any]] = None

    if has_both_names:
        expr_s, expr_lvl, expr_pl, expr_in = score_pair_compatibility(
            prof_a["expression_number"],
            prof_b["expression_number"],
            lang=language,
        )
        expr_comp = {
            "component_name": "Expression / Destiny Compatibility",
            "person_a_number": prof_a["expression_number"],
            "person_b_number": prof_b["expression_number"],
            "person_a_label": prof_a["full_name"] or "Person A",
            "person_b_label": prof_b["full_name"] or "Person B",
            "score": expr_s,
            "weight": 0.20,
            "harmony_level": expr_lvl,
            "planetary_dynamic": expr_pl,
            "interpretation": expr_in,
        }

        soul_s, soul_lvl, soul_pl, soul_in = score_pair_compatibility(
            prof_a["soul_urge_number"],
            prof_b["soul_urge_number"],
            lang=language,
        )
        soul_comp = {
            "component_name": "Soul Urge / Emotional Longing",
            "person_a_number": prof_a["soul_urge_number"],
            "person_b_number": prof_b["soul_urge_number"],
            "person_a_label": prof_a["full_name"] or "Person A",
            "person_b_label": prof_b["full_name"] or "Person B",
            "score": soul_s,
            "weight": 0.15,
            "harmony_level": soul_lvl,
            "planetary_dynamic": soul_pl,
            "interpretation": soul_in,
        }

        pers_s, pers_lvl, pers_pl, pers_in = score_pair_compatibility(
            prof_a["personality_number"],
            prof_b["personality_number"],
            lang=language,
        )
        pers_comp = {
            "component_name": "Personality / Outer Communication",
            "person_a_number": prof_a["personality_number"],
            "person_b_number": prof_b["personality_number"],
            "person_a_label": prof_a["full_name"] or "Person A",
            "person_b_label": prof_b["full_name"] or "Person B",
            "score": pers_s,
            "weight": 0.0,  # Informational component
            "harmony_level": pers_lvl,
            "planetary_dynamic": pers_pl,
            "interpretation": pers_in,
        }

    # 3. Overall Weighted Score Calculation
    if has_both_names:
        weights = {
            "life_path": 0.40,
            "birth_psychic": 0.25,
            "expression": 0.20,
            "soul_urge": 0.15,
        }
        weighted_sum = (
            (lp_score * weights["life_path"]) +
            (psy_score * weights["birth_psychic"]) +
            (expr_comp["score"] * weights["expression"]) +
            (soul_comp["score"] * weights["soul_urge"])
        )
        overall_score = round(weighted_sum, 1)
        formula_str = (
            "40% Life Path + 25% Birth/Psychic + 20% Expression + 15% Soul Urge"
            if not is_ta else
            "40% வாழ்க்கை பாதை + 25% பிறந்த எண் + 20% வெளிப்பாட்டு எண் + 15% ஆன்ம எண்"
        )
    else:
        weights = {
            "life_path": 0.60,
            "birth_psychic": 0.40,
        }
        weighted_sum = (
            (lp_score * weights["life_path"]) +
            (psy_score * weights["birth_psychic"])
        )
        overall_score = round(weighted_sum, 1)
        formula_str = (
            "60% Life Path + 40% Birth/Psychic (Name numbers omitted)"
            if not is_ta else
            "60% வாழ்க்கை பாதை + 40% பிறந்த எண் (பெயர் எண்கள் சேர்க்கப்படவில்லை)"
        )

    # 4. Overall Harmony Level Classification
    if overall_score >= 85.0:
        overall_level = "அபாரமான அலைவரிசை இணக்கம்" if is_ta else "Exceptional Resonance"
        level_summary = (
            "இருவரின் எண்களும் ஆழமான இயற்கை இணக்கத்தையும் பரஸ்பர ஆதரவையும் கொண்டுள்ளன."
            if is_ta else
            "Both profiles reflect outstanding natural harmony, supportive planetary alignments, and organic empathy."
        )
    elif overall_score >= 72.0:
        overall_level = "சிறந்த இணக்க நிலை" if is_ta else "High Harmonic Compatibility"
        level_summary = (
            "நட்பு மற்றும் சமநிலையான ஆற்றல்கள் ஒன்றிணைந்து மகிழ்ச்சியான உறவுக்கு வழிகோலுகின்றன."
            if is_ta else
            "Friendly and balanced vibrational dynamics foster an encouraging, stable, and affectionate partnership."
        )
    elif overall_score >= 58.0:
        overall_level = "மிதமான வளர்ச்சி இணக்கம்" if is_ta else "Moderate Growth Alignment"
        level_summary = (
            "நடுநிலையான அதிர்வுகள்; தெளிவான எல்லைகளும் பரஸ்பர புரிதலும் உறவை மேலும் செழுமைப்படுத்தும்."
            if is_ta else
            "Neutral and complementary dynamics offer balanced stability; active dialogue and shared goals strengthen harmony."
        )
    else:
        overall_level = "கவனமான புரிதல் தேவைப்படும் நிலை" if is_ta else "Dynamic / Requires Conscious Alignment"
        level_summary = (
            "மாறுபட்ட கிரக அதிர்வுகள்; சவால்களை முதிர்ச்சியுடன் அணுகி ஒருவருக்கொருவர் இடமளிப்பது அவசியம்."
            if is_ta else
            "Contrasting planetary temperaments suggest rich growth potential achieved through deliberate patience, emotional listening, and clear boundaries."
        )

    # 5. Relationship Themes, Strengths, Challenges, and Prompts
    rel_themes = generate_relationship_themes(prof_a, prof_b, lang=language)

    # 6. Overall Synthesis
    name_a = prof_a["full_name"] or prof_a["preferred_name"] or "Person A"
    name_b = prof_b["full_name"] or prof_b["preferred_name"] or "Person B"
    overall_synthesis = (
        f"{name_a} (Life Path {prof_a['life_path_number']}, Psychic {prof_a['birth_psychic_number']}) and "
        f"{name_b} (Life Path {prof_b['life_path_number']}, Psychic {prof_b['birth_psychic_number']}) share a composite "
        f"harmony score of {overall_score}/100 under the {conv.title()} tradition. {level_summary}"
        if not is_ta else
        f"{name_a} (வாழ்க்கை பாதை {prof_a['life_path_number']}, பிறந்த எண் {prof_a['birth_psychic_number']}) மற்றும் "
        f"{name_b} (வாழ்க்கை பாதை {prof_b['life_path_number']}, பிறந்த எண் {prof_b['birth_psychic_number']}) ஆகியோரின் "
        f"கூட்டு இணக்க மதிப்பெண் {overall_score}/100 ({conv.title()} முறை). {level_summary}"
    )

    disclaimer = (
        "Numerological compatibility analysis is designed for personal insight, philosophical reflection, and communication enrichment. "
        "It does not predict relationship longevity, marriage timing, or destiny, and should not replace mutual respect, honest dialogue, "
        "and personal commitment."
        if not is_ta else
        "எண் கணித திருமணப் பொருத்த பகுப்பாய்வு சுய சிந்தனை, உரையாடல் மற்றும் தனிப்பட்ட வளர்ச்சிக்காக மட்டுமே வடிவமைக்கப்பட்டுள்ளது. "
        "இது எதிர்கால நிகழ்வுகளையோ திருமண காலத்தையோ முன்கூட்டியே கணிக்காது. பரஸ்பர அன்பும் புரிதலுமே எந்தவொரு உறவின் அடித்தளமாகும்."
    )

    psychic_comp = {
        "component_name": "Birth / Psychic Number (Mulank) Alignment",
        "person_a_number": prof_a["birth_psychic_number"],
        "person_b_number": prof_b["birth_psychic_number"],
        "person_a_label": name_a,
        "person_b_label": name_b,
        "score": psy_score,
        "weight": weights["birth_psychic"],
        "harmony_level": psy_level,
        "planetary_dynamic": psy_planet,
        "interpretation": psy_interp,
    }

    life_path_comp = {
        "component_name": "Life Path Number (Bhagyank) Alignment",
        "person_a_number": prof_a["life_path_number"],
        "person_b_number": prof_b["life_path_number"],
        "person_a_label": name_a,
        "person_b_label": name_b,
        "score": lp_score,
        "weight": weights["life_path"],
        "harmony_level": lp_level,
        "planetary_dynamic": lp_planet,
        "interpretation": lp_interp,
    }

    return {
        "system_convention": conv,
        "engine_version": ENGINE_VERSION,
        "relationship_status": person_a_input.get("relationship_status") or person_b_input.get("relationship_status"),
        "person_a_profile": prof_a,
        "person_b_profile": prof_b,
        "psychic_compatibility": psychic_comp,
        "life_path_compatibility": life_path_comp,
        "expression_compatibility": expr_comp,
        "soul_urge_compatibility": soul_comp,
        "personality_compatibility": pers_comp,
        "emotional_themes": rel_themes["emotional_themes"],
        "communication_themes": rel_themes["communication_themes"],
        "shared_strengths": rel_themes["shared_strengths"],
        "potential_challenges": rel_themes["potential_challenges"],
        "conversation_prompts": rel_themes["conversation_prompts"],
        "growth_recommendations": rel_themes["growth_recommendations"],
        "overall_score": overall_score,
        "overall_harmony_level": overall_level,
        "overall_synthesis": overall_synthesis,
        "scoring_formula_explanation": {
            "formula": formula_str,
            "weights": weights,
            "has_name_derived_comparison": has_both_names,
            "methodology": (
                "Scores evaluate classical planetary friendships and root number harmony under Cheiro/Pythagorean rules. "
                "Life Path carries the highest weight representing long-term trajectory, followed by the daily psychic nature."
            ),
        },
        "disclaimer": disclaimer,
    }
