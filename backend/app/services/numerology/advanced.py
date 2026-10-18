"""Advanced Numerology Analysis Engine.

Integrates compatible Yuan deterministic frameworks:
1. Universal Unicode code-point name reduction for multi-script support.
2. 3x3 Lo Shu Magic Square grid and the 8 Arrows of Pythagoras.
3. The 4 Life Pinnacles and 4 Life Challenges with milestone age periods.
4. Karmic Debt detection (13, 14, 16, 19) and Karmic Lessons identification.
Zero external AI dependencies; strictly deterministic mathematics.
"""

import re
import unicodedata
from typing import Dict, List, Any
from app.services.numerology.traditional import (
    reduce_number,
    PYTHAGOREAN_MAP,
    VOWELS,
)


# ------------------------------------------------------------------------------
# 1. Yuan Unicode Code-Point Reducer
# ------------------------------------------------------------------------------

def derive_unicode_name_number(name: str) -> int:
    """Derives a single deterministic vibration from any Unicode string
    according to the Yuan framework specifications.
    """
    total = 0
    clean = name.strip()
    for char in clean:
        if char.isspace() or char in "-_.,'\"/\\":
            continue
        up = char.upper()
        if up in PYTHAGOREAN_MAP:
            total += PYTHAGOREAN_MAP[up]
        else:
            # Yuan algorithm: sum digits of unicode decimal code point
            cp = ord(char)
            sum_cp = sum(int(d) for d in str(cp))
            reduced_cp = reduce_number(sum_cp, preserve_master=False) or 1
            total += reduced_cp

    return reduce_number(total, preserve_master=True) or 1


# ------------------------------------------------------------------------------
# 2. Lo Shu 3x3 Magic Square & Arrows of Pythagoras
# ------------------------------------------------------------------------------

# Lo Shu standard positions:
# 4 | 9 | 2
# 3 | 5 | 7
# 8 | 1 | 6

def calculate_lo_shu_grid(birth_date: str, lang: str = "en") -> Dict[str, Any]:
    """Calculate Lo Shu grid digit frequencies and arrows of strength/weakness."""
    clean_dob = re.sub(r"\D", "", birth_date)
    counts: Dict[str, int] = {str(i): 0 for i in range(1, 10)}
    for char in clean_dob:
        if char in counts:
            counts[char] += 1

    has = {i: counts[str(i)] > 0 for i in range(1, 10)}
    is_ta = (lang == "ta")

    # Arrows of Strength (All 3 numbers present)
    arrows_strength: List[Dict[str, str]] = []
    # Arrows of Weakness (All 3 numbers absent)
    arrows_weakness: List[Dict[str, str]] = []

    arrow_definitions = [
        # Horizontal Planes
        ([4, 9, 2], "Arrow of Intellect & Mental Clarity", "அறிவு மற்றும் தெளிவான சிந்தனை அம்பு",
         "Arrow of Poor Memory & Distraction", "மறதி மற்றும் கவனச்சிதறல் அம்பு"),
        ([3, 5, 7], "Arrow of Emotional Balance & Spirituality", "ஆன்மீகம் மற்றும் உணர்ச்சி சமநிலை அம்பு",
         "Arrow of Skepticism & Disillusionment", "சந்தேகம் மற்றும் ஏமாற்ற அம்பு"),
        ([8, 1, 6], "Arrow of Practicality & Grounded Action", "நடைமுறை சாத்தியம் மற்றும் செயல் அம்பு",
         "Arrow of Disorder & Impracticality", "திட்டமிடலின்மை மற்றும் குழப்ப அம்பு"),
        # Vertical Planes
        ([4, 3, 8], "Arrow of the Planner & Strategist", "திட்டமிடுபவர் மற்றும் வியூக அம்பு",
         "Arrow of Disorganization", "முறைப்படுத்தப்படாத உழைப்பு அம்பு"),
        ([9, 5, 1], "Arrow of Determination & Willpower", "அசைக்க முடியாத மன உறுதி அம்பு",
         "Arrow of Procrastination & Indecision", "தள்ளிப்போடுதல் மற்றும் தயக்க அம்பு"),
        ([2, 7, 6], "Arrow of Activity & Physical Dynamism", "சுறுசுறுப்பு மற்றும் தொடர் செயல் அம்பு",
         "Arrow of Hesitation & Lethargy", "சோம்பல் மற்றும் தாமத அம்பு"),
        # Diagonals
        ([1, 5, 9], "Arrow of Manifestation & Relentless Drive", "வெற்றி மற்றும் லட்சிய வேட்கை அம்பு",
         "Arrow of Lack of Drive", "முயற்சியின்மை அம்பு"),
        ([3, 5, 7], "Arrow of Mystic Sensitivity", "உள்ளுணர்வு மற்றும் ஆன்மீக ஒளி அம்பு",
         "Arrow of Material Skepticism", "பொருள்முதல்வாத அம்பு"),
    ]

    for nums, str_en, str_ta, w_en, w_ta in arrow_definitions:
        all_present = all(has[n] for n in nums)
        all_absent = all(not has[n] for n in nums)

        if all_present:
            arrows_strength.append({
                "numbers": "-".join(str(n) for n in nums),
                "name": str_ta if is_ta else str_en,
                "description": f"Possesses strong vibration in {nums} plane." if not is_ta else f"{nums} எண்களின் ஒருங்கிணைந்த சக்தி உங்களிடம் உள்ளது.",
            })
        elif all_absent:
            arrows_weakness.append({
                "numbers": "-".join(str(n) for n in nums),
                "name": w_ta if is_ta else w_en,
                "description": f"Absence of {nums} calls for conscious cultivation of these qualities." if not is_ta else f"{nums} எண்கள் விடுபட்டுள்ளதால் இந்த குணங்களை வளர்த்துக் கொள்ள வேண்டும்.",
            })

    # Plane breakdowns
    planes = {
        "mental": {
            "name": "Mental Plane (4-9-2)" if not is_ta else "மன ஆய்வுத்தளம் (4-9-2)",
            "present_count": sum(counts[str(n)] for n in [4, 9, 2]),
            "description": "Governs logic, analytical memory, and intellectual processing." if not is_ta else "தர்க்கம், நினைவாற்றல் மற்றும் அறிவார்ந்த சிந்தனையை குறிக்கிறது.",
        },
        "emotional": {
            "name": "Emotional / Soul Plane (3-5-7)" if not is_ta else "உணர்வுத்தளம் (3-5-7)",
            "present_count": sum(counts[str(n)] for n in [3, 5, 7]),
            "description": "Governs feelings, artistic expression, empathy, and spirituality." if not is_ta else "உணர்வுகள், கலை ஆர்வம் மற்றும் ஆன்மீக பக்குவத்தை குறிக்கிறது.",
        },
        "practical": {
            "name": "Practical / Material Plane (8-1-6)" if not is_ta else "செயல்தளம் (8-1-6)",
            "present_count": sum(counts[str(n)] for n in [8, 1, 6]),
            "description": "Governs physical endurance, financial pragmatism, and daily execution." if not is_ta else "உடல் உழைப்பு, நிதி மேலாண்மை மற்றும் அன்றாட செயல்களை குறிக்கிறது.",
        },
        "thought": {
            "name": "Thought Plane (4-3-8)" if not is_ta else "சிந்தனைத்தளம் (4-3-8)",
            "present_count": sum(counts[str(n)] for n in [4, 3, 8]),
            "description": "Governs visionary strategy, conceptualization, and structured planning." if not is_ta else "நீண்ட கால திட்டமிடல் மற்றும் தொலைநோக்கு பார்வையை குறிக்கிறது.",
        },
        "will": {
            "name": "Willpower Plane (9-5-1)" if not is_ta else "மன உறுதித்தளம் (9-5-1)",
            "present_count": sum(counts[str(n)] for n in [9, 5, 1]),
            "description": "Governs tenacity, persevering courage, and unyielding ambition." if not is_ta else "விடாமுயற்சி, தளராத நம்பிக்கை மற்றும் லட்சியத்தை குறிக்கிறது.",
        },
        "action": {
            "name": "Action Plane (2-7-6)" if not is_ta else "இயக்கத்தளம் (2-7-6)",
            "present_count": sum(counts[str(n)] for n in [2, 7, 6]),
            "description": "Governs prompt physical execution, communication, and movement." if not is_ta else "உடனடி செயல்பாடு, பேச்சுத்திறன் மற்றும் சுறுசுறுப்பை குறிக்கிறது.",
        },
    }

    return {
        "grid_counts": counts,
        "planes": planes,
        "arrows_of_strength": arrows_strength,
        "arrows_of_weakness": arrows_weakness,
    }


# ------------------------------------------------------------------------------
# 3. Pinnacles & Challenges Cycles
# ------------------------------------------------------------------------------

def calculate_pinnacles_and_challenges(birth_date: str, lang: str = "en") -> Dict[str, Any]:
    """Calculate the 4 major Life Pinnacles and 4 Challenges with age milestones."""
    parts = birth_date.strip().split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    r_m = reduce_number(month, False)
    r_d = reduce_number(day, False)
    r_y = reduce_number(sum(int(x) for x in str(year)), False)

    lp = reduce_number(r_m + r_d + r_y, preserve_master=False)

    # Pinnacle age boundaries
    end_p1 = max(27, 36 - lp)
    end_p2 = end_p1 + 9
    end_p3 = end_p2 + 9

    # Pinnacles
    p1 = reduce_number(r_m + r_d, preserve_master=True)
    p2 = reduce_number(r_d + r_y, preserve_master=True)
    p3 = reduce_number(p1 + p2, preserve_master=True)
    p4 = reduce_number(r_m + r_y, preserve_master=True)

    # Challenges
    c1 = abs(r_m - r_d)
    c2 = abs(r_d - r_y)
    c3 = abs(c1 - c2)
    c4 = abs(r_m - r_y)

    is_ta = (lang == "ta")

    pinnacle_meanings = {
        1: ("Leadership, independence, developing original initiatives", "சுயசார்பு மற்றும் தலைமைப் பண்பு"),
        2: ("Cooperation, diplomacy, harmonious relationships", "ஒற்றுமை, சமாதானம் மற்றும் நல்லுறவு"),
        3: ("Artistic creativity, self-expression, joy, public visibility", "கலை, பேச்சுத்திறன் மற்றும் மகிழ்ச்சி"),
        4: ("Hard work, disciplined foundations, building lasting structures", "கடின உழைப்பு மற்றும் நிலையான அடித்தளம்"),
        5: ("Freedom, dynamic travel, adapting to exciting transformations", "சுதந்திரம், பயணம் மற்றும் புதிய மாற்றங்கள்"),
        6: ("Family responsibility, community service, love, mentorship", "குடும்ப பொறுப்பு, சேவை மற்றும் அரவணைப்பு"),
        7: ("Spiritual growth, scientific research, deep solitary study", "ஆன்மீக ஞானம் மற்றும் ஆழ்ந்த ஆராய்ச்சி"),
        8: ("Material empowerment, business executive authority, wealth", "வணிக வெற்றி மற்றும் நிதி மேலாண்மை"),
        9: ("Philanthropy, universal humanitarian compassion, closure", "மனிதநேய அறப்பணி மற்றும் தியாகம்"),
        11: ("Spiritual illumination, inspiration, high intuition", "ஆன்மீக விழிப்புணர்வு மற்றும் உள்ளுணர்வு"),
        22: ("Master building, creating structures of lasting global benefit", "உலகளாவிய பெரும் சாதனைகள் படைத்தல்"),
        33: ("Master teaching, universal compassionate healing", "உலகளாவிய கருணை மற்றும் போதனை"),
    }

    pinnacles_out = [
        {
            "pinnacle_number": 1,
            "value": p1,
            "age_span": f"Age 0 - {end_p1}",
            "theme": pinnacle_meanings.get(p1, pinnacle_meanings[1])[1 if is_ta else 0],
        },
        {
            "pinnacle_number": 2,
            "value": p2,
            "age_span": f"Age {end_p1 + 1} - {end_p2}",
            "theme": pinnacle_meanings.get(p2, pinnacle_meanings[1])[1 if is_ta else 0],
        },
        {
            "pinnacle_number": 3,
            "value": p3,
            "age_span": f"Age {end_p2 + 1} - {end_p3}",
            "theme": pinnacle_meanings.get(p3, pinnacle_meanings[1])[1 if is_ta else 0],
        },
        {
            "pinnacle_number": 4,
            "value": p4,
            "age_span": f"Age {end_p3 + 1}+",
            "theme": pinnacle_meanings.get(p4, pinnacle_meanings[1])[1 if is_ta else 0],
        },
    ]

    challenge_meanings = {
        0: ("The Challenge of Choice: Complete freedom with total responsibility", "முழுமையான சுதந்திரமும் பொறுப்பும் கொண்ட தேர்வு"),
        1: ("Overcoming insecurity or resisting overbearing domination", "தாழ்வு மனப்பான்மை அல்லது ஆதிக்கத்தை தவிர்த்தல்"),
        2: ("Managing hypersensitivity, seeking self-confidence in relationships", "அதிக உணர்ச்சிவசப்படுதலை கட்டுப்படுத்துதல்"),
        3: ("Preventing scattered creative focus and superficial chatter", "கவனச்சிதறலைத் தவிர்த்து இலக்கில் நிலைத்திருத்தல்"),
        4: ("Avoiding laziness or stubborn rigidity in work routines", "சோம்பல் மற்றும் பிடிவாதத்தை கைவிட்டு உழைத்தல்"),
        5: ("Overcoming fear of change or reckless impulsive indulgence", "மாற்றத்தைக் கண்டு அஞ்சாமல் விவேகமாக செயல்படுதல்"),
        6: ("Releasing impossible perfectionism and domestic tyranny", "அளவுக்கு மீறிய குறை காணும் போக்கை தவிர்த்தல்"),
        7: ("Overcoming cynicism, loneliness, and emotional aloofness", "அவநம்பிக்கை மற்றும் தனிமை மனப்பான்மையை வெல்லுதல்"),
        8: ("Balancing material ambitions with ethical integrity", "பொருளாதார ஆசைகளுடன் நேர்மையை கடைபிடித்தல்"),
    }

    challenges_out = [
        {
            "challenge_number": 1,
            "value": c1,
            "age_span": f"Age 0 - {end_p1}",
            "theme": challenge_meanings.get(c1, challenge_meanings[0])[1 if is_ta else 0],
        },
        {
            "challenge_number": 2,
            "value": c2,
            "age_span": f"Age {end_p1 + 1} - {end_p2}",
            "theme": challenge_meanings.get(c2, challenge_meanings[0])[1 if is_ta else 0],
        },
        {
            "challenge_number": 3,
            "value": c3,
            "age_span": "Main Lifetime Challenge",
            "theme": challenge_meanings.get(c3, challenge_meanings[0])[1 if is_ta else 0],
        },
        {
            "challenge_number": 4,
            "value": c4,
            "age_span": f"Age {end_p3 + 1}+",
            "theme": challenge_meanings.get(c4, challenge_meanings[0])[1 if is_ta else 0],
        },
    ]

    return {
        "pinnacles": pinnacles_out,
        "challenges": challenges_out,
    }


# ------------------------------------------------------------------------------
# 4. Karmic Debt Detection & Missing Numbers
# ------------------------------------------------------------------------------

def detect_karmic_debts(birth_date: str, name: str, lang: str = "en") -> List[Dict[str, Any]]:
    """Detect presence of karmic debt numbers 13, 14, 16, and 19."""
    parts = birth_date.strip().split("-")
    day = int(parts[2])
    debts = []
    is_ta = (lang == "ta")

    # Day of birth checks
    karmic_catalog = {
        13: {
            "title_en": "Karmic Debt 13: The Debt of Discipline & Hard Work",
            "title_ta": "கர்ம கடன் 13: ஒழுக்கம் மற்றும் கடின உழைப்பின் கடன்",
            "desc_en": "Requires steadfast perseverance. Avoid shortcuts; lasting success arrives through orderly effort.",
            "desc_ta": "குறுக்கு வழிகளைத் தவிர்த்து நேர்மையான உழைப்பினால் மட்டுமே நிலையான வெற்றியை அடைய முடியும்.",
        },
        14: {
            "title_en": "Karmic Debt 14: The Debt of Freedom & Moderation",
            "title_ta": "கர்ம கடன் 14: சுதந்திரம் மற்றும் மிதவாதத்தின் கடன்",
            "desc_en": "Demands self-control and moderation. Avoid chaotic escapism, addictions, or constant restlessness.",
            "desc_ta": "சுயக்கட்டுப்பாடு அவசியம். வீண் சலனங்கள் மற்றும் தவறான பழக்கங்களிலிருந்து விடுபட வேண்டும்.",
        },
        16: {
            "title_en": "Karmic Debt 16: The Debt of Ego Dissolution & Humility",
            "title_ta": "கர்ம கடன் 16: அகந்தை அழிவு மற்றும் பணிவின் கடன்",
            "desc_en": "Calls for genuine spiritual humility. False pride will crumble to allow authentic, loving rebirth.",
            "desc_ta": "போலி கர்வத்தை கைவிட்டு ஆன்மீக பணிவுடன் வாழ வேண்டும். தூய அன்பே வாழ்வின் பலம்.",
        },
        19: {
            "title_en": "Karmic Debt 19: The Debt of Interdependence & Power",
            "title_ta": "கர்ம கடன் 19: கூட்டுறவு மற்றும் அதிகாரத்தின் கடன்",
            "desc_en": "Learn to cooperate and receive help gracefully rather than ruling over others with stubborn isolation.",
            "desc_ta": "மற்றவர்களின் ஆதரவை மதித்து, சர்வாதிகாரப் போக்கை கைவிட்டு அனைவருடனும் இணைந்து வாழ வேண்டும்.",
        },
    }

    if day in karmic_catalog:
        item = karmic_catalog[day]
        debts.append({
            "number": day,
            "origin": f"Day of Birth ({day})",
            "title": item["title_ta"] if is_ta else item["title_en"],
            "description": item["desc_ta"] if is_ta else item["desc_en"],
        })

    return debts


# ------------------------------------------------------------------------------
# 5. Advanced Analysis Orchestrator
# ------------------------------------------------------------------------------

def calculate_advanced_analysis(name: str, birth_date: str, lang: str = "en") -> Dict[str, Any]:
    """Execute complete Advanced Analysis orchestrator integrating all modules."""
    unicode_number = derive_unicode_name_number(name)
    lo_shu = calculate_lo_shu_grid(birth_date, lang)
    pinnacles_challenges = calculate_pinnacles_and_challenges(birth_date, lang)
    karmic_debts = detect_karmic_debts(birth_date, name, lang)

    # Karmic lessons (digits 1-9 missing from name)
    clean_name = re.sub(r"[^A-Za-z]", "", unicodedata.normalize("NFKD", name)).upper()
    name_digits = [PYTHAGOREAN_MAP[c] for c in clean_name if c in PYTHAGOREAN_MAP]
    freq = {i: name_digits.count(i) for i in range(1, 10)}
    missing_lessons = [i for i in range(1, 10) if freq[i] == 0]
    dominant = [i for i, cnt in freq.items() if cnt == max(freq.values()) and cnt > 0]

    is_ta = (lang == "ta")

    strengths = [
        ("Multi-script Unicode resonance reinforces vibrational harmony" if not is_ta else "யுனிகோட் அடிப்படையிலான அதிர்வு சமநிலை"),
        (f"Dominant character frequencies in Number(s) {dominant}" if not is_ta else f"பெயரில் ஆதிக்கம் செலுத்தும் எண்கள் {dominant}"),
    ]

    challenges = [
        (f"Consciously cultivate missing karmic lesson vibration(s): {missing_lessons}" if not is_ta else f"விடுபட்ட எண்களின் ஆற்றலை வளர்த்துக் கொள்ள வேண்டும்: {missing_lessons}"),
    ]

    careers = [
        ("Advanced strategic architecture and cross-cultural initiatives" if not is_ta else "வியூக திட்டமிடல் மற்றும் சர்வதேச ஒருங்கிணைப்பு பணிகள்"),
        ("Systems analysis aligned with your dominant Lo Shu active plane" if not is_ta else "லோ-ஷூ கட்டத்தின்படி வலுவான தளத்தில் சிறந்து விளங்கும் பணி"),
    ]

    finances = [
        ("Long-term asset growth accelerated during harmonious pinnacle transitions" if not is_ta else "உயர் கால சுழற்சிகளில் திட்டமிட்ட முதலீடுகள் நல்ல லாபம் தரும்"),
    ]

    loves = [
        ("Relational maturity deepened by resolving mutual challenge cycles" if not is_ta else "சவால் காலங்களில் பரஸ்பர விட்டுக் கொடுக்கும் மனப்பான்மையால் அன்பு நிலைக்கும்"),
    ]

    synthesis = (
        f"Advanced multi-dimensional analysis indicates a unified Unicode vibration of {unicode_number}. "
        f"Your Lo Shu magic square features {len(lo_shu['arrows_of_strength'])} active Arrow(s) of Strength, "
        f"balancing your primary challenge cycle ({pinnacles_challenges['challenges'][2]['value']}). "
        "By applying methodical discipline to your missing karmic frequencies, steady progress is assured."
        if not is_ta else
        f"மேம்பட்ட பகுப்பாய்வு உங்கள் ஒருங்கிணைந்த அதிர்வு எண் {unicode_number} என காட்டுகிறது. "
        f"உங்கள் லோ-ஷூ கட்டம் {len(lo_shu['arrows_of_strength'])} நேர்மறை பலம் தரும் அம்புகளைக் கொண்டுள்ளது. "
        "கர்ம கடன்களையும் விடுபட்ட பாடங்களையும் விவேகத்தோடு கையாள்வது முழு வெற்றியைத் தரும்."
    )

    return {
        "unicode_derived_name_number": unicode_number,
        "lo_shu": lo_shu,
        "pinnacles_challenges": pinnacles_challenges,
        "karmic_debts": karmic_debts,
        "karmic_lessons": missing_lessons,
        "dominant_vibrations": dominant,
        "strengths": strengths,
        "challenges": challenges,
        "career_tendencies": careers,
        "financial_tendencies": finances,
        "love_themes": loves,
        "overall_synthesis": synthesis,
    }
