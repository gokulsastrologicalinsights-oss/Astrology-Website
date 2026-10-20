"""Traditional Numerology Engine.

Implements Pythagorean and Chaldean calculation conventions, master-number (11, 22, 33)
preservation, transparent letter-to-number reduction steps, Tamil & Unicode support,
karmic debt detection (13, 14, 16, 19), birth/psychic number (Mulank), and comprehensive
bilingual (English/Tamil) interpretations.
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Any, Optional

ENGINE_VERSION = "1.0.0"

# ------------------------------------------------------------------------------
# 1. Letter to Number Mappings
# ------------------------------------------------------------------------------

# Pythagorean Alphabet Map (1-9 Western standard)
PYTHAGOREAN_MAP: Dict[str, int] = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 6, "P": 7, "Q": 8, "R": 9,
    "S": 1, "T": 2, "U": 3, "V": 4, "W": 5, "X": 6, "Y": 7, "Z": 8,
}

# Chaldean Alphabet Map (1-8; 9 is reserved as sacred and separate from letters)
CHALDEAN_MAP: Dict[str, int] = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

LATIN_VOWELS = {"A", "E", "I", "O", "U"}
VOWELS = LATIN_VOWELS

# Tamil Script Classical Phonetic (Akshar Anka) Mapping
TAMIL_INDEPENDENT_VOWELS: Dict[str, int] = {
    "அ": 1, "ஆ": 1,
    "இ": 1, "ஈ": 1,
    "உ": 6, "ஊ": 6,
    "எ": 5, "ஏ": 5, "ஐ": 5,
    "ஒ": 7, "ஓ": 7, "ஔ": 7,
    "ஃ": 1,  # Ayutha Ezhuthu
}

TAMIL_DEPENDENT_VOWELS: Dict[str, int] = {
    "\u0bbe": 1,  # ா
    "\u0bbf": 1,  # ி
    "\u0bc0": 1,  # ீ
    "\u0bc1": 6,  # ு
    "\u0bc2": 6,  # ூ
    "\u0bc6": 5,  # ெ
    "\u0bc7": 5,  # ே
    "\u0bc8": 5,  # ை
    "\u0bca": 7,  # ொ
    "\u0bcb": 7,  # ோ
    "\u0bcc": 7,  # ௌ
}

TAMIL_CONSONANTS: Dict[str, int] = {
    "க": 2, "ங": 5,
    "ச": 6, "ஞ": 5,
    "ட": 4, "ண": 5,
    "த": 4, "ந": 5,
    "ப": 8, "ம": 4,
    "ய": 1, "ர": 2, "ல": 3, "வ": 6, "ழ": 5, "ள": 3, "ற": 2, "ன": 5,
    "ஜ": 1, "ஷ": 5, "ஸ": 3, "ஹ": 5,
}

TAMIL_PULLI = "\u0bcd"  # ் virama / halant (value 0)


# ------------------------------------------------------------------------------
# 2. Number Reduction Helpers with Transparent Steps
# ------------------------------------------------------------------------------

def reduce_number(val: int, preserve_master: bool = True) -> int:
    """Deterministically reduce an integer by summing digits.
    Preserves master numbers 11, 22, and 33 when preserve_master is True.
    """
    if val <= 0:
        return 0
    while val > 9:
        if preserve_master and val in (11, 22, 33):
            break
        val = sum(int(d) for d in str(val))
    return val


def reduce_number_steps(val: int, preserve_master: bool = True) -> Tuple[int, List[str]]:
    """Deterministically reduce an integer and record all intermediate reduction steps."""
    if val <= 0:
        return 0, ["0"]
    steps: List[str] = [str(val)]
    curr = val
    while curr > 9:
        if preserve_master and curr in (11, 22, 33):
            steps.append(f"Master Number {curr} preserved")
            break
        digits = [int(d) for d in str(curr)]
        curr = sum(digits)
        step_str = f"{' + '.join(str(d) for d in digits)} = {curr}"
        steps.append(step_str)
        if preserve_master and curr in (11, 22, 33):
            steps.append(f"Master Number {curr} preserved")
            break
    return curr, steps


def strip_latin_diacritics(text: str) -> str:
    """Strip accents from Latin characters (e.g. 'é' -> 'e', 'ñ' -> 'n') while preserving non-Latin scripts."""
    result = []
    for c in text:
        decomposed = unicodedata.normalize("NFKD", c)
        if decomposed and decomposed[0].isascii() and decomposed[0].isalpha():
            result.append(decomposed[0])
        else:
            result.append(c)
    return "".join(result)


def normalize_text(text: str) -> str:
    """Normalize text: strip accents from Latin characters while preserving Unicode scripts and words."""
    cleaned = strip_latin_diacritics(text.strip())
    return unicodedata.normalize("NFC", cleaned)


def get_letter_info(char: str, convention: str = "pythagorean") -> Tuple[int, bool, bool]:
    """Retrieve number value, whether character is a vowel, and whether it is a valid letter.
    Returns: (value, is_vowel, is_valid_letter)
    """
    # Check Latin letters (case insensitive)
    up = char.upper()
    mapping = CHALDEAN_MAP if convention == "chaldean" else PYTHAGOREAN_MAP
    if up in mapping:
        return mapping[up], up in LATIN_VOWELS, True

    # Check Tamil Independent Vowels
    if char in TAMIL_INDEPENDENT_VOWELS:
        return TAMIL_INDEPENDENT_VOWELS[char], True, True

    # Check Tamil Dependent Vowel Signs (Matras)
    if char in TAMIL_DEPENDENT_VOWELS:
        return TAMIL_DEPENDENT_VOWELS[char], True, True

    # Check Tamil Consonants
    if char in TAMIL_CONSONANTS:
        return TAMIL_CONSONANTS[char], False, True

    # Check Tamil Pulli (modifier with 0 numeric weight)
    if char == TAMIL_PULLI:
        return 0, False, False

    # Check other Unicode alphabetic characters
    if char.isalpha():
        cp = ord(char)
        sum_digits = sum(int(d) for d in str(cp))
        val = reduce_number(sum_digits, preserve_master=False) or 1
        return val, False, True

    # Punctuation / spaces / symbols
    return 0, False, False


def get_letter_value(char: str, convention: str = "pythagorean") -> int:
    """Legacy helper mapping character to number with Unicode code-point fallback."""
    val, _, is_valid = get_letter_info(char, convention)
    return val if is_valid else (1 if char.isalpha() else 0)


# ------------------------------------------------------------------------------
# 3. Core Traditional Numerology Calculations
# ------------------------------------------------------------------------------

def calculate_birth_psychic_number(birth_date: str) -> Tuple[int, str, Dict[str, Any]]:
    """Calculate Birth Number / Psychic Number (Mulank / Driver) from day of birth (1-31).
    In Vedic/Cheiro tradition, this is the root day reduction (1-9) representing innate psychic disposition.
    """
    parts = birth_date.strip().split("-")
    day = int(parts[2])
    
    reduced, steps = reduce_number_steps(day, preserve_master=False)
    master_reduced, _ = reduce_number_steps(day, preserve_master=True)

    method_str = f"Birth day ({day}) -> {' -> '.join(steps)}"
    detail_data = {
        "raw_day": day,
        "reduced_value": reduced,
        "master_value": master_reduced,
        "is_master": master_reduced in (11, 22),
        "reduction_steps": steps,
        "planet": get_ruling_planet(reduced),
    }
    return reduced, method_str, detail_data


def calculate_birthday_number(birth_date: str) -> Tuple[int, str]:
    """Calculate Birthday number from day of birth (1-31), preserving master numbers 11 and 22."""
    day = int(birth_date.strip().split("-")[2])
    b_num = reduce_number(day, preserve_master=True)
    method_str = f"Birth day {day} reduced to {b_num}"
    return b_num, method_str


def calculate_life_path_detailed(birth_date: str) -> Dict[str, Any]:
    """Calculate Life Path number with full breakdown of both Period reduction and Full-sum methods."""
    parts = birth_date.strip().split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    r_month, month_steps = reduce_number_steps(month, preserve_master=True)
    r_day, day_steps = reduce_number_steps(day, preserve_master=True)
    r_year, year_steps = reduce_number_steps(sum(int(d) for d in str(year)), preserve_master=True)

    period_total = r_month + r_day + r_year
    lp_period, period_reduction_steps = reduce_number_steps(period_total, preserve_master=True)

    # Full sum of all digits (DD/MM/YYYY)
    all_digits = [int(d) for d in re.sub(r"\D", "", birth_date)]
    full_sum = sum(all_digits)
    lp_full, full_sum_steps = reduce_number_steps(full_sum, preserve_master=True)

    method_str = (
        f"Period Method: Reduced Month ({r_month}) + Reduced Day ({r_day}) + Reduced Year ({r_year}) "
        f"= {period_total} -> {lp_period}"
    )

    return {
        "life_path": lp_period,
        "method_str": method_str,
        "compound_period_total": period_total,
        "period_breakdown": {
            "month": {"raw": month, "reduced": r_month, "steps": month_steps},
            "day": {"raw": day, "reduced": r_day, "steps": day_steps},
            "year": {"raw": year, "reduced": r_year, "steps": year_steps},
            "period_total": period_total,
            "reduction_steps": period_reduction_steps,
        },
        "full_sum_breakdown": {
            "digits": all_digits,
            "sum": full_sum,
            "reduced": lp_full,
            "steps": full_sum_steps,
        },
    }


def calculate_life_path(birth_date: str) -> Tuple[int, str]:
    """Calculate Life Path number from YYYY-MM-DD birthdate (maintains backward compatibility)."""
    res = calculate_life_path_detailed(birth_date)
    return res["life_path"], res["method_str"]


def calculate_attitude_number(birth_date: str) -> Tuple[int, str]:
    """Calculate Attitude/Sun number from month + day."""
    parts = birth_date.strip().split("-")
    month = int(parts[1])
    day = int(parts[2])
    att, steps = reduce_number_steps(month + day, preserve_master=True)
    method_str = f"Month ({month}) + Day ({day}) = {month + day} -> {att}"
    return att, method_str


def calculate_personal_year(birth_date: str, target_year: int = 2026) -> Tuple[int, str]:
    """Calculate Personal Year for given target year."""
    parts = birth_date.strip().split("-")
    month = int(parts[1])
    day = int(parts[2])
    r_month = reduce_number(month, False)
    r_day = reduce_number(day, False)
    r_year = reduce_number(target_year, False)
    total = r_month + r_day + r_year
    py, steps = reduce_number_steps(total, preserve_master=True)
    method_str = f"Month ({r_month}) + Day ({r_day}) + Target Year {target_year} ({r_year}) = {total} -> {py}"
    return py, method_str


def calculate_name_numbers(name: str, convention: str = "pythagorean") -> Dict[str, Any]:
    """Calculate Expression, Soul Urge, Personality, Karmic Lessons, and Hidden Passion with transparent letter steps."""
    normalized = normalize_text(name)
    words = re.split(r"[\s\-_]+", normalized)

    letter_mappings: List[Dict[str, Any]] = []
    word_breakdowns: List[Dict[str, Any]] = []

    all_vals: List[int] = []
    vowel_vals: List[int] = []
    consonant_vals: List[int] = []

    for raw_word in words:
        word = raw_word.strip(".'\",:;!()[]{}/\\")
        if not word:
            continue
        w_all: List[int] = []
        w_vowels: List[int] = []
        w_consonants: List[int] = []

        # Iterate over characters in word, ignoring punctuation dots/apostrophes
        for char in word:
            if char in ".'\",:;!()[]{}/\\":
                continue
            val, is_vowel, is_valid = get_letter_info(char, convention)
            if not is_valid:
                continue

            letter_mappings.append({
                "char": char,
                "value": val,
                "is_vowel": is_vowel,
                "word": word,
            })
            w_all.append(val)
            all_vals.append(val)
            if is_vowel:
                w_vowels.append(val)
                vowel_vals.append(val)
            else:
                w_consonants.append(val)
                consonant_vals.append(val)

        if w_all:
            word_sum = sum(w_all)
            word_vowel_sum = sum(w_vowels)
            word_consonant_sum = sum(w_consonants)
            w_red, _ = reduce_number_steps(word_sum, preserve_master=True)
            word_breakdowns.append({
                "word": word,
                "letter_sum": word_sum,
                "vowel_sum": word_vowel_sum,
                "consonant_sum": word_consonant_sum,
                "reduced_expression": w_red,
            })

    # If no valid characters, fallback to safe 0
    sum_expr = sum(all_vals)
    expr, expr_steps = reduce_number_steps(sum_expr, preserve_master=True)

    sum_soul = sum(vowel_vals)
    soul, soul_steps = reduce_number_steps(sum_soul, preserve_master=True)

    sum_pers = sum(consonant_vals)
    pers, pers_steps = reduce_number_steps(sum_pers, preserve_master=True)

    # Frequency analysis for Karmic Lessons & Hidden Passion
    freq: Dict[int, int] = {i: 0 for i in range(1, 10)}
    for v in all_vals:
        single_digit = reduce_number(v, preserve_master=False)
        if 1 <= single_digit <= 9:
            freq[single_digit] += 1

    karmic_lessons = [num for num, count in freq.items() if count == 0]
    max_count = max(freq.values()) if freq.values() else 0
    hidden_passion = [num for num, count in freq.items() if count == max_count and max_count > 0]

    return {
        "expression": expr,
        "compound_expression": sum_expr,
        "expression_method": f"Sum of letters ({sum_expr}) reduced under {convention.title()} -> {' -> '.join(expr_steps)}",
        "expression_steps": expr_steps,
        "soul_urge": soul,
        "compound_soul_urge": sum_soul,
        "soul_urge_method": f"Sum of vowels ({sum_soul}) reduced -> {' -> '.join(soul_steps)}",
        "soul_urge_steps": soul_steps,
        "personality": pers,
        "compound_personality": sum_pers,
        "personality_method": f"Sum of consonants ({sum_pers}) reduced -> {' -> '.join(pers_steps)}",
        "personality_steps": pers_steps,
        "letter_mappings": letter_mappings,
        "word_breakdowns": word_breakdowns,
        "karmic_lessons": karmic_lessons,
        "hidden_passion": hidden_passion,
    }


def calculate_maturity_number(life_path: int, expression: int) -> Tuple[int, str]:
    """Calculate Maturity / Divine Purpose number = Life Path + Expression."""
    total = life_path + expression
    mat, steps = reduce_number_steps(total, preserve_master=True)
    method_str = f"Life Path ({life_path}) + Expression ({expression}) = {total} -> {mat}"
    return mat, method_str


# ------------------------------------------------------------------------------
# 4. Karmic Debt Detection (13, 14, 16, 19)
# ------------------------------------------------------------------------------

KARMIC_DEBT_CATALOG: Dict[int, Dict[str, str]] = {
    13: {
        "title_en": "Karmic Debt 13/4: Discipline, Order & Perseverance",
        "title_ta": "கர்ம கடன் 13/4: ஒழுக்கம் மற்றும் கடின உழைப்பின் கடன்",
        "desc_en": "Points to past-life tendency toward shortcuts or procrastination. Requires steadfast, methodical work without cutting corners. True fulfillment arrives through structured order.",
        "desc_ta": "குறுக்கு வழிகளைத் தவிர்த்து, ஒழுக்கமான உழைப்பினால் மட்டுமே நிலையான வெற்றியை அடைய முடியும். அசைக்க முடியாத விடாமுயற்சி உங்கள் வாழ்வின் பாடம்.",
        "remedy_en": "Maintain consistent daily schedules, embrace detail-oriented responsibilities, and avoid complaining about hard work.",
        "remedy_ta": "தினசரி திட்டமிடல், சோம்பலைத் தவிர்த்தல் மற்றும் நேர்மையான தொடர் உழைப்பை வழக்கமாக்குங்கள்.",
    },
    14: {
        "title_en": "Karmic Debt 14/5: Freedom, Moderation & Temperance",
        "title_ta": "கர்ம கடன் 14/5: சுதந்திரம், சுயக்கட்டுப்பாடு மற்றும் மிதவாதம்",
        "desc_en": "Originates from past misuse of personal liberty, sensory indulgence, or escapism. Demands internal moderation amidst life's constant fluctuations.",
        "desc_ta": "சுதந்திரத்தை தவறாகப் பயன்படுத்தாமல் சுயக்கட்டுப்பாட்டோடு வாழ வேண்டும். அதீத ஆசைகளையும் சலனங்களையும் கட்டுப்படுத்துவது அவசியம்.",
        "remedy_en": "Practice mindfulness, guard against restless impulsive changes, and establish stable emotional and physical commitments.",
        "remedy_ta": "தியானம், உணர்ச்சி சமநிலை மற்றும் நிலையான கொள்கைகளை பின்பற்றுங்கள்.",
    },
    16: {
        "title_en": "Karmic Debt 16/7: Ego Dissolution, Humility & Spiritual Rebirth",
        "title_ta": "கர்ம கடன் 16/7: அகந்தை அழிவு, ஆன்மீகப் பணிவு மற்றும் மறுமலர்ச்சி",
        "desc_en": "The 'Fallen Tower' vibration. Challenges false pride, emotional grandiosity, or self-centered attachments. When external structures crumble, genuine spiritual wisdom is born.",
        "desc_ta": "போலி கர்வத்தை கைவிட்டு ஆன்மீக பணிவுடன் வாழ வேண்டும். மாயையான வெளிப்புற தோற்றங்களை விட உள்ளுணர்வின் தூய்மையே சாஸ்வதமானது.",
        "remedy_en": "Cultivate deep self-awareness, practice unpretentious humility, and choose spiritual growth over superficial status.",
        "remedy_ta": "பணிவு, பிறரிடம் அன்பு பாராட்டுதல் மற்றும் ஆன்மீக தேடலில் ஈடுபடுதல் நலம் பயக்கும்.",
    },
    19: {
        "title_en": "Karmic Debt 19/1: Interdependence, Mutual Respect & True Leadership",
        "title_ta": "கர்ம கடன் 19/1: கூட்டுறவு, பரஸ்பர மரியாதை மற்றும் தூய தலைமை",
        "desc_en": "Points to past misuse of authority or refusal to accept assistance. Teaches that solitary stubbornness leads to isolation, whereas true power lies in receptive cooperation.",
        "desc_ta": "சர்வாதிகாரப் போக்கை கைவிட்டு மற்றவர்களின் ஆலோசனையையும் ஆதரவையும் மதித்து அனைவருடனும் இணைந்து வாழ வேண்டும்.",
        "remedy_en": "Ask for and accept help gracefully, listen attentively to others' perspectives, and lead with empathy rather than domination.",
        "remedy_ta": "மற்றவர்களின் தேவைகளை உணர்ந்து, ஆதரவை ஏற்றுக்கொண்டு தோழமையுடன் வழிநடத்துங்கள்.",
    },
}


def detect_karmic_debts(
    birth_date: str,
    name: str,
    lang: str = "en",
    lp_compound: Optional[int] = None,
    expr_compound: Optional[int] = None,
    soul_compound: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Detect karmic debt numbers 13, 14, 16, and 19 across Day of Birth, Life Path, Expression, and Soul Urge."""
    debts: List[Dict[str, Any]] = []
    seen: set = set()
    is_ta = (lang == "ta")

    # 1. Day of Birth
    day = int(birth_date.strip().split("-")[2])
    if day in KARMIC_DEBT_CATALOG:
        cat = KARMIC_DEBT_CATALOG[day]
        debts.append({
            "number": day,
            "source": f"Day of Birth ({day})",
            "title": cat["title_ta"] if is_ta else cat["title_en"],
            "description": cat["desc_ta"] if is_ta else cat["desc_en"],
            "remedy_focus": cat["remedy_ta"] if is_ta else cat["remedy_en"],
        })
        seen.add((day, "day"))

    # 2. Life Path compound
    if lp_compound and lp_compound in KARMIC_DEBT_CATALOG and (lp_compound, "lp") not in seen:
        cat = KARMIC_DEBT_CATALOG[lp_compound]
        debts.append({
            "number": lp_compound,
            "source": f"Life Path Compound Total ({lp_compound})",
            "title": cat["title_ta"] if is_ta else cat["title_en"],
            "description": cat["desc_ta"] if is_ta else cat["desc_en"],
            "remedy_focus": cat["remedy_ta"] if is_ta else cat["remedy_en"],
        })
        seen.add((lp_compound, "lp"))

    # 3. Expression compound
    if expr_compound and expr_compound in KARMIC_DEBT_CATALOG and (expr_compound, "expr") not in seen:
        cat = KARMIC_DEBT_CATALOG[expr_compound]
        debts.append({
            "number": expr_compound,
            "source": f"Expression Name Total ({expr_compound})",
            "title": cat["title_ta"] if is_ta else cat["title_en"],
            "description": cat["desc_ta"] if is_ta else cat["desc_en"],
            "remedy_focus": cat["remedy_ta"] if is_ta else cat["remedy_en"],
        })
        seen.add((expr_compound, "expr"))

    # 4. Soul Urge compound
    if soul_compound and soul_compound in KARMIC_DEBT_CATALOG and (soul_compound, "soul") not in seen:
        cat = KARMIC_DEBT_CATALOG[soul_compound]
        debts.append({
            "number": soul_compound,
            "source": f"Soul Urge Vowels Total ({soul_compound})",
            "title": cat["title_ta"] if is_ta else cat["title_en"],
            "description": cat["desc_ta"] if is_ta else cat["desc_en"],
            "remedy_focus": cat["remedy_ta"] if is_ta else cat["remedy_en"],
        })
        seen.add((soul_compound, "soul"))

    return debts


def get_ruling_planet(num: int) -> Dict[str, str]:
    """Map root number to Vedic and Western planetary ruler."""
    planets = {
        1: {"en": "Sun (Surya)", "ta": "சூரியன் (Surya)"},
        2: {"en": "Moon (Chandra)", "ta": "சந்திரன் (Chandra)"},
        3: {"en": "Jupiter (Guru)", "ta": "குரு / வியாழன் (Guru)"},
        4: {"en": "Rahu / Uranus", "ta": "ராகு (Rahu)"},
        5: {"en": "Mercury (Budha)", "ta": "புதன் (Budha)"},
        6: {"en": "Venus (Shukra)", "ta": "சுக்கிரன் (Shukra)"},
        7: {"en": "Ketu / Neptune", "ta": "கேது (Ketu)"},
        8: {"en": "Saturn (Shani)", "ta": "சனி (Shani)"},
        9: {"en": "Mars (Mangala)", "ta": "செவ்வாய் (Mangala)"},
        11: {"en": "Moon / Neptune (Master Intuition)", "ta": "சந்திரன் / நெப்டியூன்"},
        22: {"en": "Rahu / Pluto (Master Architect)", "ta": "ராகு / புளூட்டோ"},
        33: {"en": "Jupiter / Venus (Master Teacher)", "ta": "குரு / சுக்கிரன்"},
    }
    return planets.get(num, planets[1])


# ------------------------------------------------------------------------------
# 5. Verified Interpretations Database (Bilingual English & Tamil)
# ------------------------------------------------------------------------------

INTERPRETATIONS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "life_path": {
        1: {
            "title_en": "The Pioneer & Independent Leader",
            "title_ta": "முன்னோடி மற்றும் சுதந்திர தலைவர்",
            "short_en": "Individualistic, driven, ambitious, and original.",
            "short_ta": "தனித்துவமானவர், லட்சியம் கொண்டவர், தலைமைப் பண்பு மிக்கவர்.",
            "detailed_en": "Life Path 1 signifies an innate drive to initiate and lead. You thrive when pioneering new pathways, taking responsibility, and maintaining independence.",
            "detailed_ta": "எண் 1 புதிய பாதைகளை அமைத்து வழிநடத்தும் ஆற்றலைத் தரும். சுதந்திரமும் லட்சியமும் உங்கள் வாழ்வின் அடிப்படை தூண்கள்.",
            "attributes": ["Leadership", "Initiative", "Autonomy", "Courage"],
        },
        2: {
            "title_en": "The Peacemaker & Diplomat",
            "title_ta": "அமைதி விரும்பி மற்றும் தூதர்",
            "short_en": "Intuitive, diplomatic, harmonious, and supportive.",
            "short_ta": "உள்ளுணர்வு மிக்கவர், சமாதானப் பிரியர், மற்றவர்களை அரவணைப்பவர்.",
            "detailed_en": "Life Path 2 focuses on harmony, relationships, and balance. You possess great sensitivity, acute intuition, and an exceptional ability to mediate.",
            "detailed_ta": "எண் 2 ஒற்றுமை மற்றும் நல்லுறவை குறிக்கிறது. மற்றவர்களின் உணர்வுகளை புரிந்து கொண்டு ஆதரவளிக்கும் பண்பு கொண்டது.",
            "attributes": ["Diplomacy", "Empathy", "Patience", "Cooperation"],
        },
        3: {
            "title_en": "The Creative Communicator",
            "title_ta": "படைப்பாற்றல் பேச்சாளர்",
            "short_en": "Expressive, artistic, optimistic, and charming.",
            "short_ta": "சுயவெளிப்பாடு, கலை ஆர்வம், உற்சாகம் மற்றும் நற்பண்பு.",
            "detailed_en": "Life Path 3 radiates creative energy, joy, and charisma. Your mission involves inspiring others through writing, speech, art, and vibrant social connection.",
            "detailed_ta": "எண் 3 கலை, பேச்சு மற்றும் எழுத்து மூலம் உலகிற்கு நேர்மறை சக்தியை வழங்கும் ஆற்றலைத் தருகிறது.",
            "attributes": ["Creativity", "Optimism", "Self-Expression", "Social Grace"],
        },
        4: {
            "title_en": "The Master Builder & Foundation Maker",
            "title_ta": "நம்பகமான அமைப்பாளர்",
            "short_en": "Methodical, practical, grounded, and resilient.",
            "short_ta": "திட்டமிட்டு உழைப்பவர், நம்பகமானவர், ஒழுக்கமானவர்.",
            "detailed_en": "Life Path 4 is built upon discipline, order, and endurance. You excel at turning visionary concepts into concrete, long-lasting structures.",
            "detailed_ta": "எண் 4 ஒழுக்கம், விடாமுயற்சி மற்றும் உறுதியான அஸ்திவாரத்தை அமைக்கும் பணியை குறிக்கிறது.",
            "attributes": ["Order", "Reliability", "Practicality", "Endurance"],
        },
        5: {
            "title_en": "The Dynamic Explorer & Catalyst",
            "title_ta": "இயக்கமும் சுதந்திரமும் கொண்டவர்",
            "short_en": "Adventurous, versatile, freedom-loving, and adaptable.",
            "short_ta": "சாகச விரும்பி, மாற்றம் மற்றும் பன்முகத்தன்மை கொண்டவர்.",
            "detailed_en": "Life Path 5 thrives on change, travel, and personal freedom. You learn through dynamic real-world experience and inspire transformation.",
            "detailed_ta": "எண் 5 சுதந்திரம், பயணம் மற்றும் புதிய அனுபவங்களை தேடும் உள்ளத்தை பிரதிபலிக்கிறது.",
            "attributes": ["Adaptability", "Curiosity", "Versatility", "Resourcefulness"],
        },
        6: {
            "title_en": "The Nurturer & Harmonizer",
            "title_ta": "பாதுகாப்பாளர் மற்றும் வழிகாட்டி",
            "short_en": "Responsible, compassionate, loving, and supportive.",
            "short_ta": "பொறுப்புணர்ச்சி, குடும்ப பாசம் மற்றும் கருணை கொண்டவர்.",
            "detailed_en": "Life Path 6 carries the vibration of service, home, and care. You are naturally drawn to healing, mentoring, and creating beauty.",
            "detailed_ta": "எண் 6 குடும்பம், சமூக சேவை மற்றும் அன்பை மையமாகக் கொண்ட ஒரு அமைதியான பாதையாகும்.",
            "attributes": ["Responsibility", "Compassion", "Mentorship", "Community"],
        },
        7: {
            "title_en": "The Seeker of Truth & Analytical Mind",
            "title_ta": "மெய்யறிவு மற்றும் ஆராய்ச்சியாளர்",
            "short_en": "Analytical, philosophical, introspective, and observant.",
            "short_ta": "ஆராய்ச்சி மனம், ஆன்மீக சிந்தனை மற்றும் கூர்மையான புத்தி.",
            "detailed_en": "Life Path 7 is dedicated to uncovering deeper truths, scientific rigor, and spiritual wisdom. You require solitude to reflect and analyze.",
            "detailed_ta": "எண் 7 ஆன்மீக ஞானம், அறிவியல் ஆய்வு மற்றும் ஆழ்ந்த தத்துவ ஆராய்ச்சியை குறிக்கிறது.",
            "attributes": ["Wisdom", "Intuition", "Investigation", "Inner Peace"],
        },
        8: {
            "title_en": "The Visionary Leader & Manifestor",
            "title_ta": "நிர்வாகி மற்றும் சாதனையாளர்",
            "short_en": "Strategic, ambitious, efficient, and authoritative.",
            "short_ta": "நிர்வாக திறன், நிதி ஆளுமை மற்றும் பெருவெற்றி பெறுபவர்.",
            "detailed_en": "Life Path 8 commands material mastery, business leadership, and financial discernment. Your life teaches the balanced use of power and wealth.",
            "detailed_ta": "எண் 8 நிர்வாக ஆற்றல், வணிக வெற்றி மற்றும் அதிகாரத்தை நல்ல முறையில் வழிநடத்துதலை குறிக்கிறது.",
            "attributes": ["Authority", "Financial Acumen", "Efficiency", "Ambition"],
        },
        9: {
            "title_en": "The Humanitarian & Universal Soul",
            "title_ta": "மனிதநேயர் மற்றும் தியாகி",
            "short_en": "Altruistic, compassionate, visionary, and worldly.",
            "short_ta": "உலகளாவிய பார்வை, கருணை மற்றும் அறப்பணி சிந்தனை.",
            "detailed_en": "Life Path 9 embodies universal brotherhood, artistic depth, and philanthropy. You are destined to leave the world better than you found it.",
            "detailed_ta": "எண் 9 சமுதாய நலம், கருணை மற்றும் தன்னலமற்ற சேவையின் அடையாளமாகும்.",
            "attributes": ["Humanitarianism", "Broad Vision", "Generosity", "Idealism"],
        },
        11: {
            "title_en": "Master Number 11: The Intuitive Illuminator",
            "title_ta": "மாஸ்டர் எண் 11: உள்ளுணர்வு ஒளிவிளக்கு",
            "short_en": "High intuition, inspirational, spiritual, and visionary.",
            "short_ta": "உயர்ந்த உள்ளுணர்வு, ஊக்கமளிக்கும் தன்மை, ஆன்மீக வழிகாட்டி.",
            "detailed_en": "Master Number 11 bridges the material and spiritual realms. You are endowed with acute psychic awareness and the capacity to uplift humanity.",
            "detailed_ta": "மாஸ்டர் எண் 11 ஆன்மீக வெளிச்சத்தையும் உள்ளுணர்வு வழிகாட்டுதலையும் வழங்கும் சிறப்பு வாய்ந்தது.",
            "attributes": ["Spiritual Insight", "Inspiration", "Visionary", "High Sensitivity"],
        },
        22: {
            "title_en": "Master Number 22: The Master Builder",
            "title_ta": "மாஸ்டர் எண் 22: மாபெரும் நிர்மாணிப்பாளர்",
            "short_en": "Grand architect, pragmatic visionary, and international reach.",
            "short_ta": "உலகளாவிய திட்டங்கள், பெரும் சாதனைகள் புரியும் வலிமை.",
            "detailed_en": "Master Number 22 translates lofty spiritual ideals into practical, tangible monuments and systems that serve generations to come.",
            "detailed_ta": "மாஸ்டர் எண் 22 பெரும் கனவுகளை நிஜமாக்கும் அபார நிர்வாக மற்றும் கட்டமைப்பு திறனைக் குறிக்கிறது.",
            "attributes": ["Master Building", "Global Vision", "Pragmatism", "Large Impact"],
        },
        33: {
            "title_en": "Master Number 33: The Master Teacher & Healer",
            "title_ta": "மாஸ்டர் எண் 33: போதகர் மற்றும் ஆற்றுப்படுத்துபவர்",
            "short_en": "Selfless compassion, cosmic guidance, and profound devotion.",
            "short_ta": "தன்னலமற்ற அன்பு, உலகிற்கான வழிகாட்டி மற்றும் மாபெரும் ஆசான்.",
            "detailed_en": "Master Number 33 represents the pinnacle of spiritual nurturing and universal devotion. You guide others through love and wisdom.",
            "detailed_ta": "மாஸ்டர் எண் 33 தெய்வீக அன்பு, கருணை மற்றும் உலகளாவிய ஆசானாக விளங்கும் ஆன்மீக ஆற்றலை குறிக்கிறது.",
            "attributes": ["Universal Love", "Cosmic Wisdom", "Selflessness", "Healing"],
        },
    }
}


def get_interpretation_for_number(category: str, num: int, lang: str = "en") -> Dict[str, Any]:
    """Retrieve structured interpretation from database with safe fallback."""
    cat_data = INTERPRETATIONS.get(category, INTERPRETATIONS["life_path"])
    item = cat_data.get(num)
    if not item:
        # Fallback to single digit reduction
        reduced = reduce_number(num, preserve_master=False)
        item = cat_data.get(reduced, cat_data[1])

    is_ta = (lang == "ta")
    return {
        "title": item["title_ta"] if is_ta else item["title_en"],
        "short": item["short_ta"] if is_ta else item["short_en"],
        "detailed": item["detailed_ta"] if is_ta else item["detailed_en"],
        "attributes": item.get("attributes", []),
    }


def generate_synthesized_reports(
    lp: int, expr: int, soul: int, pers: int, convention: str, lang: str = "en"
) -> Dict[str, Any]:
    """Synthesizes strengths, challenges, career, finance, and love themes deterministically."""
    is_ta = (lang == "ta")

    strengths_map = {
        1: ("Decisive leadership and pioneering courage", "துணிச்சலான தலைமை மற்றும் முன்னோடி தைரியம்"),
        2: ("Diplomatic mediation and deep empathy", "அமைதியான பேச்சுவார்த்தை மற்றும் இரக்க குணம்"),
        3: ("Creative brilliance and magnetic communication", "படைப்பாற்றல் மற்றும் வசீகரமான பேச்சு"),
        4: ("Unyielding reliability and structural discipline", "அசைக்க முடியாத நம்பகத்தன்மை மற்றும் ஒழுக்கம்"),
        5: ("Swift adaptability and innovative resourcefulness", "விரைவான தகவமைப்பு மற்றும் புதுமை சிந்தனை"),
        6: ("Generous mentorship and domestic harmony", "தாராளமான வழிகாட்டல் மற்றும் குடும்ப ஒற்றுமை"),
        7: ("Penetrating analytical mind and spiritual intuition", "கூர்மையான ஆய்வுத்திறன் மற்றும் ஆன்மீக ஞானம்"),
        8: ("Strategic mastery and organizational authority", "வியூகத் திட்டமிடல் மற்றும் நிர்வாக ஆளுமை"),
        9: ("Universal philanthropy and global vision", "மனிதநேய சிந்தனை மற்றும் உலகளாவிய பார்வை"),
        11: ("Profound psychic insight and inspirational vision", "ஆழ்ந்த உள்ளுணர்வு மற்றும் உத்வேகப் பார்வை"),
        22: ("Transformative systems architecture and global achievement", "பெரும் திட்டங்களை நிறைவேற்றும் ஆற்றல்"),
        33: ("Cosmic empathy and unconditional healing guidance", "தெய்வீக வழிகாட்டல் மற்றும் தன்னலமற்ற சேவை"),
    }

    challenges_map = {
        1: ("Guarding against stubbornness and overbearing impulsiveness", "பிடிவாதம் மற்றும் அதீத அவசரத்தை தவிர்த்தல்"),
        2: ("Avoiding hypersensitivity, indecision, or dependency", "அதிக உணர்ச்சிவசப்படுதல் மற்றும் தயக்கத்தை தவிர்த்தல்"),
        3: ("Preventing scattered focus and superficial commitments", "கவனச்சிதறல் மற்றும் அரைகுறை வேலைகளை தவிர்த்தல்"),
        4: ("Avoiding excessive rigidity and resistance to innovation", "அதிக இறுக்கம் மற்றும் மாற்றத்தை எதிர்க்கும் போக்கை தவிர்த்தல்"),
        5: ("Guarding against restlessness, impatience, and escapism", "பொறுமையின்மை மற்றும் சலனத்தை கட்டுப்படுத்துதல்"),
        6: ("Avoiding martyrdom, perfectionism, or over-interference", "மற்றவர் விவகாரங்களில் அதீத தலையீட்டை தவிர்த்தல்"),
        7: ("Overcoming cynicism, isolation, and emotional detachment", "தனிமை மற்றும் மனக்கசப்பை கடந்து பழகுதல்"),
        8: ("Preventing workaholism and purely materialistic fixation", "பொருளாதார பேராசை மற்றும் அதீத வேலைச்சுமையை தவிர்த்தல்"),
        9: ("Navigating emotional boundary fatigue and unrealistic idealism", "அளவுக்கு மீறிய எதிர்பார்ப்புகளை கட்டுப்படுத்துதல்"),
        11: ("Balancing nervous intensity and grounding spiritual visions", "மன அழுத்தத்தை குறைத்து யதார்த்தமாக செயல்படுதல்"),
        22: ("Preventing overwhelming stress under high responsibility", "பெரிய பொறுப்புகளினால் ஏற்படும் அழுத்தத்தை தவிர்த்தல்"),
        33: ("Protecting personal well-being while carrying others' burdens", "தன்னலம் பேணி மற்றவர்களுக்கு உதவுதல்"),
    }

    career_map = {
        1: ("Entrepreneurship, Technology Leadership, Executive Management", "தொழில் முனைவு, நிர்வாக தலைமை, தொழில்நுட்ப வழிகாட்டி"),
        2: ("Counseling, Diplomacy, Strategic Human Resources, Partnerships", "ஆலோசனை, மனிதவள மேம்பாடு, சமரச நிர்வாகம்"),
        3: ("Media, Creative Arts, Publishing, Public Relations, Marketing", "ஊடகம், கலைத்துறை, விளம்பரம், எழுத்து"),
        4: ("Engineering, Architecture, Financial Operations, Project Management", "பொறியியல், கட்டடக் கலை, நிதி மேலாண்மை, திட்ட மேற்பார்வை"),
        5: ("Global Commerce, Travel, Public Speaking, Agile Consulting", "சர்வதேச வர்த்தகம், சுற்றுலா, ஆலோசனை, பேச்சாளர்"),
        6: ("Healthcare, Education, Interior Architecture, Social Enterprise", "மருத்துவ சேவை, கல்வித்துறை, சமூக நல நிறுவனங்கள்"),
        7: ("Data Science, Scientific Research, Philosophy, Specialized Diagnostics", "தரவு அறிவியல், ஆராய்ச்சி, தத்துவம், துல்லிய பகுப்பாய்வு"),
        8: ("Investment Banking, Corporate Strategy, Law, Real Estate Development", "முதலீட்டு வங்கி, நிறுவன உத்தி, சட்டம், ரியல் எஸ்டேட்"),
        9: ("Non-Profit Leadership, Cultural Diplomacy, Environmental Stewardship", "தொண்டு நிறுவனங்கள், கலாச்சார தூதுவர், சூழலியல்"),
        11: ("Spiritual Advisory, Cutting-Edge Innovation, Transformative Mentoring", "ஆன்மீக வழிகாட்டுதல், நவீன புதுமை கண்டுபிடிப்புகள்"),
        22: ("Mega-Infrastructure, International Organizations, Civic Institutions", "மாபெரும் சர்வதேச அமைப்புகள், அரசு நிர்வாக திட்டங்கள்"),
        33: ("Higher Humanitarian Institutions, Holistic Healing, Global Philanthropy", "மனிதநேய சேவை, ஆன்மீக ஆசிரமங்கள், உலக அறக்கட்டளைகள்"),
    }

    lp_k = lp if lp in strengths_map else reduce_number(lp, False)
    expr_k = expr if expr in strengths_map else reduce_number(expr, False)
    soul_k = soul if soul in strengths_map else reduce_number(soul, False)

    str_lp = strengths_map.get(lp_k, strengths_map[1])
    str_expr = strengths_map.get(expr_k, strengths_map[1])
    chal_lp = challenges_map.get(lp_k, challenges_map[1])
    chal_expr = challenges_map.get(expr_k, challenges_map[1])
    car_lp = career_map.get(lp_k, career_map[1])
    car_expr = career_map.get(expr_k, career_map[1])

    strengths = [str_lp[1] if is_ta else str_lp[0], str_expr[1] if is_ta else str_expr[0]]
    challenges = [chal_lp[1] if is_ta else chal_lp[0], chal_expr[1] if is_ta else chal_expr[0]]
    careers = [car_lp[1] if is_ta else car_lp[0], car_expr[1] if is_ta else car_expr[0]]

    financial_tendencies = [
        ("Structured wealth accumulation through deliberate planning" if not is_ta else "திட்டமிட்ட உழைப்பின் மூலம் நிலையான பொருளாதார வளர்ச்சி"),
        ("Strongest gains materialize when aligning investments with personal core values" if not is_ta else "மதிப்புகளுக்கு முன்னுரிமை தரும் முதலீடுகள் சிறப்பான லாபத்தை தரும்"),
    ]

    love_themes = [
        ("Seeks intellectual resonance and reciprocal authenticity in relationships" if not is_ta else "பரஸ்பர நம்பிக்கை மற்றும் அறிவார்ந்த புரிதலை விரும்புகிறார்"),
        ("Harmony deepens when partners respect your inner rhythm and independence" if not is_ta else "சுதந்திரமும் சுயமரியாதையும் காக்கப்படும் போது அன்பு பெருகும்"),
    ]

    overall_synthesis = (
        f"Your profile combines the foundational life direction of Number {lp} with the outward expression of Number {expr}. "
        f"Under the {convention.title()} convention, your soul vibration ({soul}) indicates a quest for meaningful contribution, "
        f"while your personality ({pers}) presents a dependable, engaging demeanor to society. "
        "Through balanced discipline and clear ethical boundaries, your highest potential is realized."
        if not is_ta else
        f"உங்கள் ஜாதகம் எண் {lp} வாழ்க்கை பாதையையும், எண் {expr} வெளிப்பாட்டு தன்மையையும் இணைக்கிறது. "
        f"{convention.title()} முறைப்படி, உங்கள் உள்ளுணர்வு அதிர்வு ({soul}) சமுதாயத்திற்கு அர்த்தமுள்ள பங்களிப்பை அளிக்க விழைகிறது. "
        "ஒழுக்கமும் நேர்மையான உழைப்பும் உங்கள் முழுமையான வெற்றியை உறுதி செய்யும்."
    )

    return {
        "strengths": strengths,
        "challenges": challenges,
        "career_tendencies": careers,
        "financial_tendencies": financial_tendencies,
        "love_themes": love_themes,
        "overall_synthesis": overall_synthesis,
    }
