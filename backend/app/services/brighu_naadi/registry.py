"""Brighu Naadi Classical Dataset & Rule Registry.

Compiled from Dr. N. Srinivasan Shastry's foundational treatise:
"Brighu Naadi Sangraha: (Pearls of Brighu Naadi)" (Sagar Publications).
"""

from typing import Dict, Any, List

BRIGHU_NAADI_METADATA: Dict[str, Any] = {
    "book_title": "Brighu Naadi Sangraha (Pearls of Brighu Naadi)",
    "book_title_ta": "பிருகு நாடி சங்கிரகம் (பிருகு நாடியின் முத்துக்கள்)",
    "author": "Dr. N. Srinivasan Shastry (Astrological Science Celebrity)",
    "publisher": "Sagar Publications, New Delhi",
    "core_philosophy_en": (
        "In Brighu Naadi astrology, Sage Brighu does not rely solely on the Ascendant (Lagna); instead, "
        "Jupiter is treated as the prime Life Force (Jeeva Karaka / Native) and all 12 Bhavas are reckoned "
        "from Jupiter. Saturn is the Action/Profession significator (Karma Karaka). Rahu and Ketu represent "
        "the mouth/entrance and tail/liberation of the Kalapurusha and the family circle. Planetary transits "
        "in rounds (Jupiter's 12-year cycle and Saturn's 30-year cycle) dynamically trigger life events "
        "without complicated calculations."
    ),
    "core_philosophy_ta": (
        "பிருகு நாடி ஜோதிட முறையில் மகரிஷி பிருகு லக்னத்தை மட்டுமே முதன்மையாகக் கொள்ளாமல், குரு பகவானை 'ஜீவ காரகன்' "
        "(உயிர் ஆற்றல் / ஜாதகர்) எனக் கருதி, குரு நின்ற ராசியிலிருந்தே 12 பாவகப் பலன்களையும் கணிக்கிறார். "
        "சனி பகவான் 'கர்ம காரகன்' (தொழில், செயல், கடன், தடைகள்) ஆவார். ராகு மற்றும் கேது ஆகியோர் காலபுருஷனின் வாய் மற்றும் "
        "வாலாகவும், குடும்ப வட்டமாகவும் விளங்குகின்றனர். குருவின் 12 ஆண்டு சுற்றுக்களும், சனியின் 30 ஆண்டு சுற்றுக்களும் "
        "சம்பவங்கள் நிகழும் வயதை வினாடிகளில் துல்லியமாகத் தீர்மானிக்கின்றன."
    ),
}

# ---------------------------------------------------------------------------
# Vastu & Birth Environment Rules
# ---------------------------------------------------------------------------

# 1. Road in front of birth house from Rahu-Ketu axis (pp. xix, 111-112)
# Aries/Libra, Gemini/Sagittarius, Leo/Aquarius => East to West
# Taurus/Scorpio, Cancer/Capricorn, Virgo/Pisces => South to North
ROAD_DIRECTION_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    2: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
    3: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    4: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
    5: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    6: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
    7: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    8: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
    9: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    10: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
    11: {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"},
    12: {"en": "South to North", "ta": "தெற்கு முதல் வடக்கு வரை"},
}

# 2. Main Entrance Door Facing from Rahu sign (pp. 112-113)
# Fiery (Aries 1, Leo 5, Sagittarius 9) => East
# Earthy (Taurus 2, Virgo 6, Capricorn 10) => South
# Airy (Gemini 3, Libra 7, Aquarius 11) => West
# Watery (Cancer 4, Scorpio 8, Pisces 12) => North
DOOR_FACING_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "Facing East", "ta": "கிழக்கு நோக்கிய தலைவாசல்"},
    2: {"en": "Facing South", "ta": "தெற்கு நோக்கிய தலைவாசல்"},
    3: {"en": "Facing West", "ta": "மேற்கு நோக்கிய தலைவாசல்"},
    4: {"en": "Facing North", "ta": "வடக்கு நோக்கிய தலைவாசல்"},
    5: {"en": "Facing East", "ta": "கிழக்கு நோக்கிய தலைவாசல்"},
    6: {"en": "Facing South", "ta": "தெற்கு நோக்கிய தலைவாசல்"},
    7: {"en": "Facing West", "ta": "மேற்கு நோக்கிய தலைவாசல்"},
    8: {"en": "Facing North", "ta": "வடக்கு நோக்கிய தலைவாசல்"},
    9: {"en": "Facing East", "ta": "கிழக்கு நோக்கிய தலைவாசல்"},
    10: {"en": "Facing South", "ta": "தெற்கு நோக்கிய தலைவாசல்"},
    11: {"en": "Facing West", "ta": "மேற்கு நோக்கிய தலைவாசல்"},
    12: {"en": "Facing North", "ta": "வடக்கு நோக்கிய தலைவாசல்"},
}

# 3. City / Town Sector of Birth from Rahu sign (pp. 114-115)
CITY_SECTOR_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "Eastern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் கிழக்கு பகுதி"},
    2: {"en": "Southern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் தெற்கு பகுதி"},
    3: {"en": "Western part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் மேற்கு பகுதி"},
    4: {"en": "Northern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் வடக்கு பகுதி"},
    5: {"en": "Eastern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் கிழக்கு பகுதி"},
    6: {"en": "Southern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் தெற்கு பகுதி"},
    7: {"en": "Western part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் மேற்கு பகுதி"},
    8: {"en": "Northern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் வடக்கு பகுதி"},
    9: {"en": "Eastern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் கிழக்கு பகுதி"},
    10: {"en": "Southern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் தெற்கு பகுதி"},
    11: {"en": "Western part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் மேற்கு பகுதி"},
    12: {"en": "Northern part of the City / Village / Town", "ta": "ஊர் / நகரத்தின் வடக்கு பகுதி"},
}

# 4. Temple / Shrine near birthplace from Sun sign (pp. 86-87)
TEMPLE_NEAR_BIRTH_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "Hanuman Temple / Durga Temple", "ta": "ஸ்ரீ அனுமன் / துர்க்கை அம்மன் ஆலயம்"},
    2: {"en": "Goddess Lakshmi Temple", "ta": "ஸ்ரீ மகாலட்சுமி ஆலயம்"},
    3: {"en": "Vishnu Temple", "ta": "ஸ்ரீ மகாவிஷ்ணு / பெருமாள் ஆலயம்"},
    4: {"en": "Snake God (Nagaraja) Temple", "ta": "நாகராஜா / பாம்பு புற்று ஆலயம்"},
    5: {"en": "Shiva Temple", "ta": "ஸ்ரீ சிவபெருமான் ஆலயம்"},
    6: {"en": "Vishnu Temple", "ta": "ஸ்ரீ மகாவிஷ்ணு ஆலயம்"},
    7: {"en": "Kanyakaparameshwari / Devi Temple", "ta": "ஸ்ரீ கன்னிகாபரமேஸ்வரி / தேவி ஆலயம்"},
    8: {"en": "Kali / Shakthi Temple", "ta": "ஸ்ரீ காளி / உக்கிர பராசக்தி ஆலயம்"},
    9: {"en": "Lord Ganesha / Saibaba Temple", "ta": "ஸ்ரீ கணபதி / சாயிபாபா ஆலயம்"},
    10: {"en": "Bhairava Temple", "ta": "ஸ்ரீ கால பைரவர் ஆலயம்"},
    11: {"en": "Waters / Sacred River / Holy Spring", "ta": "புனித நதி / தீர்த்தக்கரை / திருக்குளம்"},
    12: {"en": "Cremation Ground / Sacred Ashram / Hermitage", "ta": "தவ ஆசிரமம் / முக்தி பீடம் / மயான பூமி"},
}

# 5. Spouse arrival direction (Venus for male, Mars for female) (pp. xix, xx)
SPOUSE_DIRECTION_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "East", "ta": "கிழக்கு திசை"},
    2: {"en": "South", "ta": "தெற்கு திசை"},
    3: {"en": "West", "ta": "மேற்கு திசை"},
    4: {"en": "North", "ta": "வடக்கு திசை"},
    5: {"en": "East", "ta": "கிழக்கு திசை"},
    6: {"en": "South", "ta": "தெற்கு திசை"},
    7: {"en": "West", "ta": "மேற்கு திசை"},
    8: {"en": "North", "ta": "வடக்கு திசை"},
    9: {"en": "East", "ta": "கிழக்கு திசை"},
    10: {"en": "South", "ta": "தெற்கு திசை"},
    11: {"en": "West", "ta": "மேற்கு திசை"},
    12: {"en": "North", "ta": "வடக்கு திசை"},
}

# ---------------------------------------------------------------------------
# Exact Milestone Timing Tables
# ---------------------------------------------------------------------------

# Marriage Ages (Jupiter having Venus in houses 2 to 12) (pp. 38-39)
MARRIAGE_AGE_BY_VENUS_FROM_JUPITER: Dict[int, List[int]] = {
    2: [24, 25],
    3: [26, 27],
    4: [15, 16],
    5: [16, 22],
    6: [29, 30],
    7: [18, 19],
    8: [20, 21],
    9: [22],
    10: [22],
    11: [22, 23],
    12: [24, 30],
}

# Name & Fame / Promotion Ages (Jupiter having Sun in houses 2 to 12) (pp. 40-41)
FAME_AGE_BY_SUN_FROM_JUPITER: Dict[int, List[int]] = {
    2: [31, 43, 55],
    3: [32, 38, 44],
    4: [34, 40, 46],
    5: [28, 34, 46],
    6: [35, 41],
    7: [31, 36, 43, 48],
    8: [37, 50],
    9: [44, 50],
    10: [45, 57],
    11: [28, 34, 40, 46, 52],
    12: [36, 42, 47],
}

# Land / House Construction / Property Ages (Mars having Jupiter in houses 2 to 12) (pp. 104-105)
PROPERTY_AGE_BY_JUPITER_FROM_MARS: Dict[int, List[int]] = {
    2: [36, 48],
    3: [35, 47],
    4: [34, 46],
    5: [33, 45],
    6: [32, 44],
    7: [31, 43],
    8: [30, 42],
    9: [29, 41],
    10: [28, 40],
    11: [27, 39],
    12: [26, 38],
}

# Financial Prosperity Peak Ages (Venus in houses from Jupiter) (pp. 90-91)
FINANCE_AGE_BY_VENUS_FROM_JUPITER: Dict[int, List[int]] = {
    2: [25, 32, 38, 44, 50, 56],
    3: [27, 33, 39, 45, 51, 57],
    4: [28, 34, 40, 46, 52, 58],
    5: [29, 35, 41, 47, 53, 59],
    6: [24, 30, 36, 42, 48, 54],
    7: [25, 31, 37, 43, 49, 55],
    8: [26, 32, 38, 44, 50, 56],
    9: [21, 27, 33, 34, 51, 57],
    10: [22, 28, 34, 40, 46, 52, 58],
    11: [23, 29, 35, 41, 47, 53, 59],
    12: [24, 30, 36, 42, 48, 54, 60],
}

# Career Start & Change Ages (Saturn having Venus in houses 3 to 12) (pp. 58-60)
CAREER_AGE_BY_VENUS_FROM_SATURN: Dict[int, Dict[str, Any]] = {
    3: {"start": 8, "change": 21},
    4: {"start": 10, "change": 25},
    5: {"start": 12, "change": 26},
    6: {"start": 15, "change": 22},
    7: {"start": 18, "change": 24},
    8: {"start": 20, "change": 31},
    9: {"start": 22, "change": 35},
    10: {"start": 25, "change": None},
    11: {"start": 22, "change": None},
    12: {"start": 30, "change": None},
}

# Accident Caution Ages (Rahu having Mars in houses 2 to 12) (pp. 116-117)
ACCIDENT_AGE_BY_MARS_FROM_RAHU: Dict[int, List[int]] = {
    2: [18, 36, 54],
    3: [17, 35, 52],
    4: [15, 33, 51],
    5: [3, 31, 49],
    6: [12, 30, 48],
    7: [10, 28, 46],
    8: [9, 27, 45],
    9: [7, 25, 43, 61],
    10: [6, 24, 42, 60],
    11: [4, 12, 30, 48, 56],
    12: [3, 21, 39, 57, 65],
}

# Infant & Childhood Danger of Death Ages (Ketu in houses 1 to 12 from Jupiter) (pp. 118-120)
INFANT_DANGER_AGE_BY_KETU_FROM_JUPITER: Dict[int, List[int]] = {
    1: [1, 2],
    2: [2, 3],
    3: [3, 4],
    4: [4, 5],
    5: [5, 6],
    6: [6, 7],
    7: [7, 8],
    8: [8, 9],
    9: [9, 10],
    10: [10, 11],
    11: [11, 12],
    12: [12, 13],
}

# Relocation / Change of Place Ages (Saturn having Moon in houses 2 to 12) (pp. 70-71)
RELOCATION_AGE_BY_MOON_FROM_SATURN: Dict[int, List[int]] = {
    2: [5, 20, 32],
    3: [7, 21, 37],
    4: [10, 25, 40],
    5: [12, 27, 42],
    6: [15, 30, 45],
    7: [17, 32, 47],
    8: [20, 35, 50],
    9: [7, 22, 37, 52],
    10: [10, 25, 40, 55],
    11: [12, 27, 42, 57],
    12: [17, 30, 45, 60],
}

# Father's Longevity / Demise Ages (Saturn having Sun in houses 1 to 12) (pp. 60-61)
FATHER_CRITICAL_AGE_BY_SUN_FROM_SATURN: Dict[int, List[int]] = {
    1: [30],
    2: [36],
    3: [31],
    4: [32],
    5: [42],
    6: [30, 37],
    7: [32],
    8: [35, 37],
    9: [52],
    10: [31, 42],
    11: [42],
    12: [45],
}

# Mother's Longevity / Demise Ages (Saturn having Moon in houses 2 to 12) (pp. 61-62)
MOTHER_CRITICAL_AGE_BY_MOON_FROM_SATURN: Dict[int, List[int]] = {
    2: [28, 29],
    3: [30],
    4: [32],
    5: [35],
    6: [38],
    7: [40],
    8: [43],
    9: [45],
    10: [31, 57],
    11: [48, 50],
    12: [25],
}

# Female Horoscope: Husband's Demise / Critical Ages (Saturn having Mars in houses 2 to 12) (pp. 69-70)
FEMALE_HUSBAND_CRITICAL_AGE_BY_MARS_FROM_SATURN: Dict[int, List[int]] = {
    2: [52, 60],
    3: [55, 62],
    4: [57, 65],
    5: [60, 67],
    6: [32, 40, 60],
    7: [52, 60, 35, 42, 62],
    8: [37, 45, 65],
    9: [40, 70],
    10: [42, 72],
    11: [45, 75],
    12: [47, 77],
}

# ---------------------------------------------------------------------------
# Physical Constitution, Appearance & Health Vulnerabilities
# ---------------------------------------------------------------------------

SUN_SIGN_CONSTITUTION: Dict[int, Dict[str, str]] = {
    1: {"organ_en": "Head / Brain", "organ_ta": "தலை / மூளை", "desc_en": "Prone to migraines, tension, and heat rushes to the head", "desc_ta": "ஒற்றைத் தலைவலி, உஷ்ணக் கோளாறுகள் மற்றும் தலை நரம்பு உபாதைகள்"},
    2: {"organ_en": "Face & Voice", "organ_ta": "முகம் & குரல்", "desc_en": "Reddish countenance and commanding, loud or harsh voice", "desc_ta": "சிவந்த முகம், எடுப்பான தோற்றம் மற்றும் கம்பீரமான/கரகரப்பான குரல்"},
    3: {"organ_en": "Shoulders & Arms", "organ_ta": "தோள்பட்டை & கைகள்", "desc_en": "Powerful shoulders, muscular dexterity, and athletic arms", "desc_ta": "வலிமையான தோள்பட்டைகள், சுறுசுறுப்பான கைகள் மற்றும் உடல் திறன்"},
    4: {"organ_en": "Heart & Chest", "organ_ta": "இதயம் & மார்பகம்", "desc_en": "Strong, noticeable heartbeats and sensitivity in chest tissues", "desc_ta": "துரிதமான இதயத் துடிப்பு மற்றும் மார்பு சார்ந்த உணர்திறன்"},
    5: {"organ_en": "Stomach & Spine", "organ_ta": "வயிறு & தண்டுவடம்", "desc_en": "Vigorous digestive fire (Agni), great appetite, and sturdy back", "desc_ta": "அதிக பசி, வலுவான செரிமான தீ மற்றும் உறுதியான முதுகுத்தண்டு"},
    6: {"organ_en": "Intestines", "organ_ta": "குடல் பகுதி", "desc_en": "Well-toned intestinal muscular action and sensitive digestive absorption", "desc_ta": "நன்கு இயங்கும் குடல் தசைகள் மற்றும் செரிமான உறிஞ்சுதல் திறன்"},
    7: {"organ_en": "Lumbar & General Symmetry", "organ_ta": "இடுப்பு & உடல் சமச்சீர்", "desc_en": "Harmonious, symmetrical, and attractive bodily proportion", "desc_ta": "கவர்ச்சிகரமான, சமச்சீரான மற்றும் அழகுமிக்க உடல் கட்டமைப்பு"},
    8: {"organ_en": "Secrets & Excretory System", "organ_ta": "மர்ம உறுப்புகள் & சிறுநீரகம்", "desc_en": "Heat accumulation in secret organs and excess urination tendency", "desc_ta": "மர்ம ஸ்தானங்களில் உஷ்ண மிகுதி மற்றும் அதிக சிறுநீர் வெளியேற்றம்"},
    9: {"organ_en": "Thighs & Hips", "organ_ta": "தொடைகள் & இடுப்பு", "desc_en": "Well-formed, muscular thighs and firm, shapely hips", "desc_ta": "உறுதியான தொடைகள் மற்றும் சீரான இடுப்பு வடிவமைப்பு"},
    10: {"organ_en": "Knees & Joints", "organ_ta": "முழங்கால் மூட்டுகள்", "desc_en": "Prominent, large knee caps with vulnerability to stiffness", "desc_ta": "பெரிய முழங்கால் மூட்டுகள் மற்றும் மூட்டு பிடிப்புக்கான வாய்ப்பு"},
    11: {"organ_en": "Calves & Ankles", "organ_ta": "கால் முட்டி & கணுக்கால்", "desc_en": "Finely contoured, endurance-rich calf muscles", "desc_ta": "அழகான, வலிமையான கெண்டைக்கால் மற்றும் கணுக்கால் தசைகள்"},
    12: {"organ_en": "Feet & Toes", "organ_ta": "பாதங்கள் & விரல்கள்", "desc_en": "Strong, resilient feet capable of prolonged standing or travel", "desc_ta": "நீண்ட தூரம் நடக்கும் ஆற்றல் கொண்ட வலுவான பாதங்கள்"},
}

RAHU_SIGN_AFFLICTIONS: Dict[int, Dict[str, str]] = {
    1: {"organ_en": "Head", "organ_ta": "தலை", "desc_en": "Problems, neurological tensions, or injuries to the head", "desc_ta": "தலைவலி, நரம்புத் தளர்ச்சி அல்லது தலைப்பகுதியில் உபாதைகள்"},
    2: {"organ_en": "Throat / Neck", "organ_ta": "தொண்டை / கழுத்து", "desc_en": "Afflictions in the throat, thyroid, or vocal regions", "desc_ta": "தொண்டை வலி, குரல்வளை அல்லது தைராய்டு சார்ந்த தொந்தரவுகள்"},
    3: {"organ_en": "Arms / Shoulders", "organ_ta": "கைகள் / தோள்பட்டை", "desc_en": "Pain or spasms in shoulders, clavicles, and arms", "desc_ta": "தோள்பட்டை வலி, கைகளில் நரம்பு சுளுக்கு அல்லது பிடிப்பு"},
    4: {"organ_en": "Heart / Breast", "organ_ta": "இதயம் / மார்பு", "desc_en": "Chest congestion, anxiety, and heart palpitation issues", "desc_ta": "மார்பு படபடப்பு, சுவாச அடைப்பு அல்லது மனக்கலக்கம்"},
    5: {"organ_en": "Stomach / Spine", "organ_ta": "வயிறு / தண்டுவடம்", "desc_en": "Gastric irritation, spine stiffness, and solar plexus discomfort", "desc_ta": "வயிற்று உப்புசம், வாயுத் தொல்லை மற்றும் முதுகுத்தண்டு வலி"},
    6: {"organ_en": "Lumbar Section", "organ_ta": "இடுப்பு பகுதி", "desc_en": "Pain or weakness in the lumbar vertebrae and kidneys", "desc_ta": "இடுப்பு தண்டுவடம் மற்றும் சிறுநீரக பகுதியில் பலவீனம்"},
    7: {"organ_en": "Groins / Pelvis", "organ_ta": "அடிவயிறு / இடுப்பு மூட்டு", "desc_en": "Problems in the lower abdominal groin walls and urinary tract", "desc_ta": "அடிவயிற்று வலி, இடுப்பு தசைப்பிடிப்பு மற்றும் சிறுநீர் உபாதை"},
    8: {"organ_en": "Secrets / Genitals", "organ_ta": "மர்ம உறுப்புகள்", "desc_en": "Afflictions in excretory and reproductive organs", "desc_ta": "மர்ம உறுப்புகள், மூலம் மற்றும் பிறப்புறுப்பு சார்ந்த உபாதைகள்"},
    9: {"organ_en": "Thighs / Hips", "organ_ta": "தொடைகள் / இடுப்பு", "desc_en": "Sciatica, muscle pulling, and thigh weakness", "desc_ta": "சயாடிகா நரம்பு வலி மற்றும் தொடைகளில் தசை இறுக்கம்"},
    10: {"organ_en": "Knees", "organ_ta": "முழங்கால்கள்", "desc_en": "Joint friction, rheumatic stiffness, or knee injuries", "desc_ta": "முழங்கால் மூட்டு வலி மற்றும் வாத பிடிப்புகள்"},
    11: {"organ_en": "Legs / Ankles", "organ_ta": "கால்கள் / கணுக்கால்", "desc_en": "Circulation sluggishness, cramps, and ankle sprains", "desc_ta": "இரத்த ஓட்டக் குறைபாடு, கால் நரம்பு சுருட்டல் மற்றும் கணுக்கால் வலி"},
    12: {"organ_en": "Feet", "organ_ta": "பாதங்கள்", "desc_en": "Foot burning sensation, heel pain, or lymphatic swellings", "desc_ta": "கால் எரிச்சல், குதிகால் வலி மற்றும் பாத வீக்கம்"},
}

KETU_SIGN_DANGERS: Dict[int, Dict[str, str]] = {
    1: {"type_en": "Electricity & Poisoning", "type_ta": "மின்சாரம் & விஷக்கடி", "desc_en": "Danger of electric shock, burns, or toxic exposure", "desc_ta": "மின்சார அதிர்ச்சி, தீக்காயம் அல்லது விஷக் காய்ச்சல் எச்சரிக்கை"},
    2: {"type_en": "Skin Allergies & Throat Problem", "type_ta": "தோல் ஒவ்வாமை & தொண்டை", "desc_en": "Vulnerability to acute throat infections and dermal allergies", "desc_ta": "தீவிர தொண்டை அழற்சி மற்றும் தோல் ஒவ்வாமை கோளாறுகள்"},
    3: {"type_en": "Falling from Height & Mind", "type_ta": "உயரத்திலிருந்து விழுதல் & மனம்", "desc_en": "Risk of falls from stairs/heights and nervous mental distress", "desc_ta": "உயரமான இடத்திலிருந்து தவறி விழுதல் மற்றும் மன உளைச்சல்"},
    4: {"type_en": "Drowning & Water Hazards", "type_ta": "நீரில் கண்டம் & மூழ்குதல்", "desc_en": "Danger near rivers, wells, pools, and deep waters", "desc_ta": "ஆறு, குளம், கிணறு மற்றும் நீர்நிலைகளில் எச்சரிக்கை தேவை"},
    5: {"type_en": "Stomach, Spinal Troubles & Fire", "type_ta": "வயிறு, தண்டுவடம் & தீக்காயம்", "desc_en": "Risk of gastric ulcers, spinal issues, or fire accidents", "desc_ta": "வயிற்றுப் புண், முதுகுத்தண்டு வலி மற்றும் நெருப்பினால் கண்டம்"},
    6: {"type_en": "Intestinal Disorders", "type_ta": "குடல் அழற்சி & கோளாறு", "desc_en": "Bowel inflammation, colitis, or enteric complications", "desc_ta": "குடல் புண், செரிமானக் கோளாறு மற்றும் பெருங்குடல் உபாதைகள்"},
    7: {"type_en": "Electricity & Drug Reactions", "type_ta": "மின்சாரம் & மருந்து ஒவ்வாமை", "desc_en": "Danger of adverse medication reactions and electrical currents", "desc_ta": "மருந்துகளின் பக்கவிளைவுகள் மற்றும் மின்சாதன விபத்துக்கள்"},
    8: {"type_en": "Electricity, Poisoning, Vehicles & Fire", "type_ta": "மின்சாரம், விஷம், வாகனம் & தீ", "desc_en": "Multi-hazard caution: electrical shock, bites, vehicle skid, or fire", "desc_ta": "விஷம், மின்சாரம், வாகன விபத்து அல்லது தீ விபத்து எச்சரிக்கை"},
    9: {"type_en": "Falling from Heights", "type_ta": "உயரத்திலிருந்து தவறி விழுதல்", "desc_en": "Danger of falls during hill trekking, stairways, or balconies", "desc_ta": "மலைப்பாதை, மாடிப்படி அல்லது உயரமான இடங்களிலிருந்து வீழ்ச்சி"},
    10: {"type_en": "Drowning & Water Swells", "type_ta": "நீரில் ஆபத்து / மூழ்குதல்", "desc_en": "Caution around marshlands, rivers, and swimming water", "desc_ta": "ஆழமான நீர்நிலைகளில் நீராடும் போது எச்சரிக்கை அவசியம்"},
    11: {"type_en": "Drowning & Fluidic Hazards", "type_ta": "நீரினால் கண்டம்", "desc_en": "Water hazards, damp environments, and deep currents", "desc_ta": "வெள்ளப்பெருக்கு, நீரோடை மற்றும் ஈரமான பகுதிகளில் பாதுகாப்பு தேவை"},
    12: {"type_en": "Falling from Heights & Isolation", "type_ta": "உயரத்திலிருந்து வீழ்ச்சி", "desc_en": "Accidental slips from elevation and solitary physical danger", "desc_ta": "உயரத்திலிருந்து சறுக்கி விழுதல் மற்றும் பாத விபத்துக்கள்"},
}

# ---------------------------------------------------------------------------
# Classical Planetary Yogas & Combinations Library (200+ canonical rules)
# ---------------------------------------------------------------------------

BRIGHU_NAADI_RULES_DATABASE: List[Dict[str, Any]] = [
    # --- Jupiter as Life Force (Jeeva Karaka) ---
    {
        "rule_id": "BN-JUP-001",
        "category": "life_force",
        "title_en": "Jupiter in Scorpio",
        "title_ta": "விருச்சிகத்தில் குரு பகவான்",
        "pattern": {"planet": "Jupiter", "sign": 8},
        "interpretation_en": "The native will be an intensely ambitious, determined person with occult depth.",
        "interpretation_ta": "ஜாதகர் மிகுந்த லட்சிய வெறி, அசைக்க முடியாத மன உறுதி மற்றும் ஆழ்ந்த ரகசிய அறிவு கொண்டவராக இருப்பார்.",
        "source_page": "Page 21",
    },
    {
        "rule_id": "BN-JUP-002",
        "category": "education",
        "title_en": "Jupiter Next to Mercury (2nd House to Mercury)",
        "title_ta": "புதனுக்கு அடுத்த வீட்டில் குரு",
        "pattern": {"relative_house": {"from": "Mercury", "to": "Jupiter", "house": 2}},
        "interpretation_en": "The native will take keen interest in Vedic studies, philosophy, and sacred literature.",
        "interpretation_ta": "ஜாதகர் வேத சாஸ்திரங்கள், தத்துவங்கள் மற்றும் உயர்ந்த ஆன்மீக நூல்களில் தீவிர ஈடுபாடு கொள்வார்.",
        "source_page": "Page 21",
    },
    {
        "rule_id": "BN-JUP-003",
        "category": "profession",
        "title_en": "Jupiter has Saturn and Rahu in 7th House",
        "title_ta": "குருவுக்கு 7-ஆம் வீட்டில் சனியும் ராகுவும்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": ["Saturn", "Rahu"], "house": 7}},
        "interpretation_en": "The native will experience servitude or work as a modestly compensated employee.",
        "interpretation_ta": "ஜாதகர் ஆரம்பத்தில் குறைந்த சம்பளத்தில் பிறரிடம் வேலை செய்யும் அமைப்பைப் பெறுவார்.",
        "source_page": "Page 21",
    },
    {
        "rule_id": "BN-JUP-004",
        "category": "family",
        "title_en": "Jupiter in Aquarius with Sun in Leo (7th to Jupiter)",
        "title_ta": "கும்பத்தில் குரு, சிம்மத்தில் (7-ல்) சூரியன்",
        "pattern": {"planet": "Jupiter", "sign": 11, "has_planet_in_house": {"from": "Jupiter", "planet": "Sun", "house": 7}},
        "interpretation_en": "The native's father will be highly honored by the Government or high authorities.",
        "interpretation_ta": "ஜாதகரின் தந்தை அரசாங்கத்தாலும் மேலதிகாரிகளாலும் கௌரவிக்கப்பட்டு பெருமை அடைவார்.",
        "source_page": "Page 21",
    },
    {
        "rule_id": "BN-JUP-005",
        "category": "family",
        "title_en": "Jupiter Having Mars in 12th House",
        "title_ta": "குருவுக்கு 12-ஆம் வீட்டில் செவ்வாய்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Mars", "house": 12}},
        "interpretation_en": "The native will have an elder brother.",
        "interpretation_ta": "ஜாதகருக்கு மூத்த சகோதரன் (அண்ணன்) இருப்பார்.",
        "source_page": "Page 21",
    },
    {
        "rule_id": "BN-JUP-006",
        "category": "family",
        "title_en": "Jupiter Having Mars in 2nd House",
        "title_ta": "குருவுக்கு 2-ஆம் வீட்டில் செவ்வாய்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Mars", "house": 2}},
        "interpretation_en": "The native will have a younger brother and earnings through landed property.",
        "interpretation_ta": "ஜாதகருக்கு இளைய சகோதரன் அமைவார் மற்றும் பூமி/நிலங்கள் மூலம் வருமானம் உண்டாகும்.",
        "source_page": "Page 22",
    },
    {
        "rule_id": "BN-JUP-007",
        "category": "wealth",
        "title_en": "Jupiter with Venus (Guru-Sukra Conjunction)",
        "title_ta": "குரு - சுக்கிரன் சேர்க்கை",
        "pattern": {"conjunction": ["Jupiter", "Venus"]},
        "interpretation_en": "The native is born into wealth and enjoys immense material comforts and luxuries.",
        "interpretation_ta": "ஜாதகர் வசதியான குடும்பத்தில் பிறப்பார்; செல்வம், சொகுசு மற்றும் சகல யோகங்களையும் அனுபவிப்பார்.",
        "source_page": "Page 22",
    },
    {
        "rule_id": "BN-JUP-008",
        "category": "life_force",
        "title_en": "Jupiter in Retrograde Motion",
        "title_ta": "வக்கிர குருவின் பலன்",
        "pattern": {"planet_is_retrograde": "Jupiter"},
        "interpretation_en": "The native will shine and develop in places far away from their birth town.",
        "interpretation_ta": "ஜாதகர் தனது சொந்த ஊரை விட்டு வெளியூர்களிலோ அல்லது வெளிநாட்டிலோ சென்று பெரும் புகழும் முன்னேற்றமும் பெறுவார்.",
        "source_page": "Page 22",
    },
    {
        "rule_id": "BN-JUP-009",
        "category": "profession",
        "title_en": "Jupiter has Sun in 7th House",
        "title_ta": "குருவுக்கு 7-ஆம் வீட்டில் சூரியன்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Sun", "house": 7}},
        "interpretation_en": "The native will earn high government recognition, honors, and prestigious status.",
        "interpretation_ta": "ஜாதகருக்கு அரசு மரியாதை, உயர்பதவி மற்றும் சமுதாய அந்தஸ்து கிட்டும்.",
        "source_page": "Page 22",
    },
    {
        "rule_id": "BN-JUP-010",
        "category": "education",
        "title_en": "Jupiter with Mercury (Budha-Guru Sambandha)",
        "title_ta": "குருவுடன் புதன் சேர்க்கை",
        "pattern": {"conjunction": ["Jupiter", "Mercury"]},
        "interpretation_en": "The native possesses sharp intellect, legal acumen, and aptitude for teaching and commerce.",
        "interpretation_ta": "ஜாதகர் கூர்மையான புத்தி கூர்மை, சட்ட அறிவு மற்றும் கல்வித் துறையில் மேன்மை அடைவார்.",
        "source_page": "Page 22",
    },
    {
        "rule_id": "BN-JUP-011",
        "category": "life_force",
        "title_en": "Jupiter in Gemini, Sagittarius, or Pisces (41-Year Golden Turning Point)",
        "title_ta": "மிதுனம், தனுசு அல்லது மீனத்தில் குரு (41 வயது பொற்காலம்)",
        "pattern": {"planet_in_any_sign": {"planet": "Jupiter", "signs": [3, 9, 12]}},
        "interpretation_en": "The prime golden period, supreme prosperity, and highest rise in life occurs after 41 years of age.",
        "interpretation_ta": "ஜாதகருக்கு 41 வயதிற்குப் பின்னரே அசாத்திய முன்னேற்றம், தொழில் உயர்வு மற்றும் அசைக்க முடியாத செல்வ செழிப்பு உண்டாகும்.",
        "source_page": "Page 18",
    },
    {
        "rule_id": "BN-JUP-012",
        "category": "property",
        "title_en": "Jupiter Having Mars in 4th House",
        "title_ta": "குருவுக்கு 4-ஆம் வீட்டில் செவ்வாய்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Mars", "house": 4}},
        "interpretation_en": "The native will construct own house or purchase prime landed property during Jupiter's 4th round.",
        "interpretation_ta": "ஜாதகர் குருவின் 4-வது சுற்றில் சொந்த வீடு கட்டுவார் அல்லது விளைநிலங்கள் வாங்குவார்.",
        "source_page": "Page 23",
    },
    {
        "rule_id": "BN-JUP-013",
        "category": "marriage",
        "title_en": "Jupiter having Venus in 2nd House",
        "title_ta": "குருவுக்கு 2-ஆம் வீட்டில் சுக்கிரன்",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Venus", "house": 2}},
        "interpretation_en": "Marriage is fructified at age 24–25; native enjoys sudden wealth and financial rise after marriage.",
        "interpretation_ta": "24 முதல் 25 வயதில் திருமணம் கைகூடும்; திருமணத்திற்குப் பின் அபரிமிதமான பண வரவும் யோகமும் உண்டாகும்.",
        "source_page": "Page 25, 38",
    },
    {
        "rule_id": "BN-JUP-014",
        "category": "spiritual",
        "title_en": "Jupiter and Saturn Conjoined with Ketu Next House",
        "title_ta": "குருவும் சனியும் இணைந்து அடுத்த வீட்டில் கேது",
        "pattern": {"conjunction": ["Jupiter", "Saturn"], "relative_house": {"from": "Jupiter", "to": "Ketu", "house": 2}},
        "interpretation_en": "The native is born by divine blessing and holds exceptional spiritual depth and karmic grace.",
        "interpretation_ta": "ஜாதகர் தெய்வ சங்கல்பத்தாலும் முன்னோர்களின் புண்ணியத்தாலும் பிறந்த பாக்கியசாலி ஆவார்.",
        "source_page": "Page 25",
    },
    {
        "rule_id": "BN-JUP-015",
        "category": "family",
        "title_en": "Jupiter Has No Planets Behind Him (12th House Empty)",
        "title_ta": "குருவுக்கு பின்னால் கிரகங்கள் இல்லாத நிலை (12-ல் கிரகம் இல்லை)",
        "pattern": {"house_empty_from": {"from": "Jupiter", "house": 12}},
        "interpretation_en": "The native is the eldest son/child in the family line.",
        "interpretation_ta": "ஜாதகர் குடும்பத்தின் மூத்த மகனாக / முதல் வாரிசாகப் பிறப்பார்.",
        "source_page": "Page 26",
    },
    {
        "rule_id": "BN-JUP-016",
        "category": "health",
        "title_en": "Jupiter Having Ketu in 2nd House",
        "title_ta": "குருவுக்கு 2-ஆம் வீட்டில் கேது",
        "pattern": {"relative_house": {"from": "Jupiter", "to": "Ketu", "house": 2}},
        "interpretation_en": "Native attains deep Vedic wisdom, but must protect against nervous weakness and fatigue.",
        "interpretation_ta": "ஜாதகர் ஆன்மீக மற்றும் சாஸ்திர ஞானம் பெறுவார்; நரம்பு பலவீனத்தை சீராகப் பராமரிக்க வேண்டும்.",
        "source_page": "Page 26",
    },

    # --- Saturn as Karma Karaka (Action & Profession) ---
    {
        "rule_id": "BN-SAT-001",
        "category": "profession",
        "title_en": "Saturn with Sun (Sani-Surya Sambandha)",
        "title_ta": "சனி - சூரியன் சேர்க்கை / பார்வை",
        "pattern": {"conjunction": ["Saturn", "Sun"]},
        "interpretation_en": "The native will secure Government employment or hold a public sector administrative post.",
        "interpretation_ta": "ஜாதகர் அரசு வேலை அல்லது பொதுத்துறை நிறுவனத்தில் அதிகாரமிக்க பொறுப்பைப் பெறுவார்.",
        "source_page": "Page 44, 55",
    },
    {
        "rule_id": "BN-SAT-002",
        "category": "profession",
        "title_en": "Saturn in Leo (Simha Sani)",
        "title_ta": "சிம்மத்தில் சனி பகவான்",
        "pattern": {"planet": "Saturn", "sign": 5},
        "interpretation_en": "The native achieves government employment and executive career recognition.",
        "interpretation_ta": "ஜாதகர் அரசு சம்பந்தப்பட்ட பணிகளில் அமர்வார் மற்றும் நிர்வாகப் பெருமை பெறுவார்.",
        "source_page": "Page 44",
    },
    {
        "rule_id": "BN-SAT-003",
        "category": "profession",
        "title_en": "Saturn with Mars in 10th House or Scorpio 10th",
        "title_ta": "சனிக்கு 10-ல் செவ்வாய் அல்லது விருச்சிகத்தில் சனி",
        "pattern": {"relative_house": {"from": "Saturn", "to": "Mars", "house": 10}},
        "interpretation_en": "The native's profession will be in iron, steel, heavy engineering, machinery, or factories.",
        "interpretation_ta": "ஜாதகர் இரும்பு, எஃகு, கனரக இயந்திரங்கள் அல்லது தொழிற்சாலை சார்ந்த தொழிலில் ஈடுபடுவார்.",
        "source_page": "Page 45",
    },
    {
        "rule_id": "BN-SAT-004",
        "category": "profession",
        "title_en": "Saturn Retrograde with Mars and Venus in 11th from Saturn",
        "title_ta": "வக்கிர சனி, சனிக்கு 11-ல் செவ்வாய் மற்றும் சுக்கிரன்",
        "pattern": {"planet_is_retrograde": "Saturn", "relative_house": {"from": "Saturn", "to": ["Mars", "Venus"], "house": 11}},
        "interpretation_en": "The native will earn high fame and status in career, rising to extraordinary financial heights.",
        "interpretation_ta": "ஜாதகர் தொழிலில் மாபெரும் புகழும் வெற்றியும் பெற்று அபார செல்வ நிலையை அடைவார்.",
        "source_page": "Page 45",
    },
    {
        "rule_id": "BN-SAT-005",
        "category": "wealth",
        "title_en": "Saturn Having Venus in 2nd House (in Taurus or Libra)",
        "title_ta": "சனிக்கு 2-ல் சுக்கிரன் (ரிஷபம் அல்லது துலாமில்)",
        "pattern": {"relative_house": {"from": "Saturn", "to": "Venus", "house": 2}},
        "interpretation_en": "The native deals in gold, jewelry, bullion, fine gems, and high financial assets.",
        "interpretation_ta": "ஜாதகர் தங்கம், வைர நகைகள், நிதி நிறுவனங்கள் மற்றும் சொகுசுப் பொருட்கள் மூலம் தனலாபம் ஈட்டுவார்.",
        "source_page": "Page 46",
    },
    {
        "rule_id": "BN-SAT-006",
        "category": "profession",
        "title_en": "Saturn with Ketu (Sani-Ketu Sambandha)",
        "title_ta": "சனி - கேது சேர்க்கை",
        "pattern": {"conjunction": ["Saturn", "Ketu"]},
        "interpretation_en": "The native's livelihood involves machinery, chemical department, or esoteric/astrological practice; temporary service break.",
        "interpretation_ta": "ஜாதகரின் தொழில் இயந்திரங்கள், ரசாயனம் அல்லது ஆன்மீகம்/ஜோதிடம் சார்ந்தது; இடையில் ஒருமுறை உத்தியோக மாறுதல் ஏற்படும்.",
        "source_page": "Page 47, 50",
    },
    {
        "rule_id": "BN-SAT-007",
        "category": "profession",
        "title_en": "Saturn in Gemini or Virgo with Mercury (Budha-Sani)",
        "title_ta": "மிதுனம்/கன்னியில் சனி, புதன் தொடர்பு",
        "pattern": {"planet_in_any_sign": {"planet": "Saturn", "signs": [3, 6]}},
        "interpretation_en": "The native thrives as an advocate, legal counsel, commercial trader, or chartered auditor.",
        "interpretation_ta": "ஜாதகர் புகழ்பெற்ற வழக்கறிஞர், ஆடிட்டர் அல்லது வர்த்தக வணிகராக மேன்மை அடைவார்.",
        "source_page": "Page 47, 51",
    },
    {
        "rule_id": "BN-SAT-008",
        "category": "profession",
        "title_en": "Saturn with Sun and Rahu",
        "title_ta": "சனி, சூரியன், ராகு சேர்க்கை",
        "pattern": {"conjunction": ["Saturn", "Sun", "Rahu"]},
        "interpretation_en": "The native will achieve extraordinary eminence as a noted surgeon or forensic specialist.",
        "interpretation_ta": "ஜாதகர் தலைசிறந்த அறுவை சிகிச்சை நிபுணராகவோ (Surgeon) அல்லது மருத்துவரோ பரிமளிப்பார்.",
        "source_page": "Page 52",
    },
    {
        "rule_id": "BN-SAT-009",
        "category": "profession",
        "title_en": "Saturn with Moon in Foreign Sign or 10th Lord in Cancer",
        "title_ta": "சனி - சந்திரன் சேர்க்கை அல்லது சனிக்கு 10-ல் சந்திரன்",
        "pattern": {"conjunction": ["Saturn", "Moon"]},
        "interpretation_en": "The native will hold foreign employment, international assignments, or water-related commerce.",
        "interpretation_ta": "ஜாதகர் வெளிநாட்டில் உத்தியோகம் புரிவார் அல்லது கடல் கடந்து சென்று பொருளீட்டுவார்.",
        "source_page": "Page 53, 55",
    },
    {
        "rule_id": "BN-SAT-010",
        "category": "profession",
        "title_en": "Saturn in Scorpio with Rahu in Sagittarius & Mars Next",
        "title_ta": "விருச்சிகத்தில் சனி, தனுசில் ராகு, அடுத்து செவ்வாய்",
        "pattern": {"planet": "Saturn", "sign": 8, "has_planet_in_house": {"from": "Saturn", "planet": "Rahu", "house": 2}},
        "interpretation_en": "The native's profession will pertain to timber, furniture, dry wood, and forest produce.",
        "interpretation_ta": "ஜாதகர் மர வியாபாரம், மரத்தளவாடங்கள் (Furnitures) மற்றும் வனப் பொருட்கள் தொழிலில் தனலாபம் பெறுவார்.",
        "source_page": "Page 48",
    },
    {
        "rule_id": "BN-SAT-011",
        "category": "profession",
        "title_en": "Saturn with Mercury having Venus Next House",
        "title_ta": "சனி, புதன் இணைந்து அடுத்த வீட்டில் சுக்கிரன்",
        "pattern": {"conjunction": ["Saturn", "Mercury"], "relative_house": {"from": "Saturn", "to": "Venus", "house": 2}},
        "interpretation_en": "The native will be a wealthy merchant and independent commercial business owner.",
        "interpretation_ta": "ஜாதகர் பெரும் வர்த்தக வியாபாரியாகவும், சொந்த தொழில் அதிபராகவும் திகழ்வார்.",
        "source_page": "Page 50",
    },
    {
        "rule_id": "BN-SAT-012",
        "category": "career",
        "title_en": "Saturn Alone with No Planets in 2nd and 12th Houses",
        "title_ta": "சனிக்கு 2 மற்றும் 12-ல் கிரகங்கள் இல்லாத தனித்த சனி",
        "pattern": {"house_empty_from": {"from": "Saturn", "house": 2}, "house_empty_from_2": {"from": "Saturn", "house": 12}},
        "interpretation_en": "The native is fiercely self-made, independent, and forges their own destiny without reliance on others.",
        "interpretation_ta": "ஜாதகர் யாருடைய ஆதரவையும் எதிர்பாராமல் சுயமாக உழைத்து முன்னுக்கு வரும் தனித்தன்மை வாய்ந்தவர்.",
        "source_page": "Page 68",
    },

    # --- Mercury: Education, Intelligence & Trade ---
    {
        "rule_id": "BN-MER-001",
        "category": "education",
        "title_en": "Mercury Exalted (in Virgo)",
        "title_ta": "புதன் உச்சம் (கன்னியில்)",
        "pattern": {"planet": "Mercury", "sign": 6},
        "interpretation_en": "The native is blessed with acute intellectual capacity, computational brilliancy, and scholastic distinction.",
        "interpretation_ta": "ஜாதகர் அபார புத்தி கூர்மை, கணிதத் திறன் மற்றும் உயர்ந்த கல்வித் தேர்ச்சி பெற்றிருப்பார்.",
        "source_page": "Page 72",
    },
    {
        "rule_id": "BN-MER-002",
        "category": "education",
        "title_en": "Mercury Exalted with Venus",
        "title_ta": "புதன் உச்சத்தில் சுக்கிரனுடன் சேர்க்கை",
        "pattern": {"planet": "Mercury", "sign": 6, "conjunction": ["Mercury", "Venus"]},
        "interpretation_en": "The native has peerless aesthetic intellect, eloquence, and thrives in higher intellectual pursuits.",
        "interpretation_ta": "ஜாதகர் கலை நயம் வாய்ந்த உயர்ந்த அறிவாளியாகத் திகழ்ந்து வாழ்வில் பெரும் பிரகாசம் அடைவார்.",
        "source_page": "Page 72",
    },
    {
        "rule_id": "BN-MER-003",
        "category": "education",
        "title_en": "Mercury with Mars (Budha-Kuja Sambandha)",
        "title_ta": "புதன் - செவ்வாய் சேர்க்கை",
        "pattern": {"conjunction": ["Mercury", "Mars"]},
        "interpretation_en": "Native faces technical examinations or intermittent hurdles/breaks in formal education.",
        "interpretation_ta": "ஜாதகரின் கல்வியில் ஒருமுறை தற்காலிகத் தடைகள் அல்லது தொழில்நுட்பக் கல்விக்கான மாறுதல்கள் உண்டாகும்.",
        "source_page": "Page 72, 74",
    },
    {
        "rule_id": "BN-MER-004",
        "category": "education",
        "title_en": "Mercury in Taurus with Ketu",
        "title_ta": "ரிஷபத்தில் புதனுடன் கேது",
        "pattern": {"planet": "Mercury", "sign": 2, "conjunction": ["Mercury", "Ketu"]},
        "interpretation_en": "The native masters Law, Jurisprudence, and high-level financial Accountancy.",
        "interpretation_ta": "ஜாதகர் சட்டக் கல்வி (Law) மற்றும் கணக்கியலில் (Accountancy) நிபுணத்துவம் பெறுவார்.",
        "source_page": "Page 76",
    },
    {
        "rule_id": "BN-MER-005",
        "category": "education",
        "title_en": "Mercury and Venus Together",
        "title_ta": "புதன் - சுக்கிரன் சேர்க்கை",
        "pattern": {"conjunction": ["Mercury", "Venus"]},
        "interpretation_en": "Extraordinary intelligence, refined artistic taste, and exquisite handwriting.",
        "interpretation_ta": "அபார புத்தி கூர்மை, அழகிய கையெழுத்து மற்றும் நுண்கலைகளில் இயல்பான தேர்ச்சி.",
        "source_page": "Page 76",
    },
    {
        "rule_id": "BN-MER-006",
        "category": "spiritual",
        "title_en": "Mercury Having Moon in 2nd and Ketu in 5th from Moon",
        "title_ta": "புதனுக்கு 2-ல் சந்திரன், சந்திரனுக்கு 5-ல் கேது",
        "pattern": {"relative_house": {"from": "Mercury", "to": "Moon", "house": 2}},
        "interpretation_en": "The native is deeply well-versed in Vedic philosophy, occult sciences, and Astrology.",
        "interpretation_ta": "ஜாதகர் வேதங்கள், ஜோதிட சாஸ்திரம் மற்றும் மறைஞானக் கலைகளில் கரை கண்ட ஞானியாவார்.",
        "source_page": "Page 76",
    },

    # --- Sun: Father, Royalty & Physical Constitution ---
    {
        "rule_id": "BN-SUN-001",
        "category": "family",
        "title_en": "Sun with Mars (Surya-Kuja)",
        "title_ta": "சூரியன் - செவ்வாய் சேர்க்கை",
        "pattern": {"conjunction": ["Sun", "Mars"]},
        "interpretation_en": "The native inherits ancestral landed property and real estate from the father.",
        "interpretation_ta": "ஜாதகருக்கு தந்தை வழி பூர்வீக நிலபுலன்கள் மற்றும் சொத்துக்கள் நிச்சயமாகக் கிட்டும்.",
        "source_page": "Page 79",
    },
    {
        "rule_id": "BN-SUN-002",
        "category": "profession",
        "title_en": "Sun with Saturn in Leo",
        "title_ta": "சிம்மத்தில் சூரியனும் சனியும் சேர்க்கை",
        "pattern": {"planet": "Sun", "sign": 5, "conjunction": ["Sun", "Saturn"]},
        "interpretation_en": "The native holds government service in machinery, engineering, or industrial departments.",
        "interpretation_ta": "ஜாதகர் அரசு இயந்திரவியல் துறை, பொறியியல் அல்லது கனரக அரசுப் பிரிவுகளில் பணிபுரிவார்.",
        "source_page": "Page 79",
    },
    {
        "rule_id": "BN-SUN-003",
        "category": "health",
        "title_en": "Sun, Mars, and Rahu in Conjunction",
        "title_ta": "சூரியன், செவ்வாய், ராகு சேர்க்கை",
        "pattern": {"conjunction": ["Sun", "Mars", "Rahu"]},
        "interpretation_en": "Vulnerability to blood heating, skin eruptions, and cellular inflammation.",
        "interpretation_ta": "இரத்த உஷ்ணம், சருமக் கொப்புளங்கள் மற்றும் தசை அழற்சிக்கு வாய்ப்புள்ளதால் முன்னெச்சரிக்கை தேவை.",
        "source_page": "Page 79",
    },
    {
        "rule_id": "BN-SUN-004",
        "category": "wealth",
        "title_en": "Sun and Venus in Aries, Mercury in Taurus",
        "title_ta": "மேஷத்தில் சூரியன்-சுக்கிரன், ரிஷபத்தில் புதன்",
        "pattern": {"planet": "Sun", "sign": 1, "conjunction": ["Sun", "Venus"], "planet_in_sign": {"planet": "Mercury", "sign": 2}},
        "interpretation_en": "The native's father is exceptionally wealthy, dealing in banking, finance, or bullion.",
        "interpretation_ta": "ஜாதகரின் தந்தை நிதி நிறுவனம் அல்லது நகை வியாபாரம் மூலம் பெரும் கோடீஸ்வரராகத் திகழ்வார்.",
        "source_page": "Page 80",
    },

    # --- Venus: Marriage, Spouse & Luxury ---
    {
        "rule_id": "BN-VEN-001",
        "category": "marriage",
        "title_en": "Venus Exalted (in Pisces)",
        "title_ta": "சுக்கிரன் உச்சம் (மீனத்தில்)",
        "pattern": {"planet": "Venus", "sign": 12},
        "interpretation_en": "The native is blessed with a wealthy, noble, devout, and very beautiful wife.",
        "interpretation_ta": "ஜாதகருக்கு அழகும், நற்குணமும், செல்வச் செழிப்பும் கொண்ட சிறந்த மனைவி அமைவார்.",
        "source_page": "Page 89, 95",
    },
    {
        "rule_id": "BN-VEN-002",
        "category": "marriage",
        "title_en": "Venus in Mars Sign (Aries or Scorpio)",
        "title_ta": "செவ்வாயின் வீட்டில் சுக்கிரன் (மேஷம் / விருச்சிகம்)",
        "pattern": {"planet_in_any_sign": {"planet": "Venus", "signs": [1, 8]}},
        "interpretation_en": "The spouse of the native arrives from a known family or close relational circle.",
        "interpretation_ta": "ஜாதகரின் வாழ்க்கைத்துணை ஏற்கெனவே அறிமுகமான சொந்தக் குடும்பத்திலிருந்தே அமையும்.",
        "source_page": "Page 92",
    },
    {
        "rule_id": "BN-VEN-003",
        "category": "marriage",
        "title_en": "Venus and Mars Exchange Signs (Parivartana)",
        "title_ta": "சுக்கிரன் - செவ்வாய் பரிவர்த்தனை",
        "pattern": {"sign_exchange": ["Venus", "Mars"]},
        "interpretation_en": "The native possesses magnetic personal charisma, captivating the opposite sex effortlessly.",
        "interpretation_ta": "ஜாதகர் கவர்ச்சிகரமான ஆளுமையுடன் மற்றவர்களை எளிதில் ஈர்க்கும் காந்த சக்தி கொண்டிருப்பார்.",
        "source_page": "Page 92",
    },
    {
        "rule_id": "BN-VEN-004",
        "category": "marriage",
        "title_en": "Venus and Jupiter Conjoined in Cancer",
        "title_ta": "கடகத்தில் குரு - சுக்கிரன் சேர்க்கை",
        "pattern": {"planet": "Venus", "sign": 4, "conjunction": ["Venus", "Jupiter"]},
        "interpretation_en": "The native marries an extraordinarily beautiful, pious, and virtuous woman.",
        "interpretation_ta": "ஜாதகர் பேரழகும் ஆன்மீகப் பக்தியும் கொண்ட சிறந்த குணவதியை மணப்பார்.",
        "source_page": "Page 97",
    },
    {
        "rule_id": "BN-VEN-005",
        "category": "wealth",
        "title_en": "Venus and Saturn in Taurus",
        "title_ta": "ரிஷபத்தில் சுக்கிரனும் சனியும்",
        "pattern": {"planet": "Venus", "sign": 2, "conjunction": ["Venus", "Saturn"]},
        "interpretation_en": "The native becomes exceedingly wealthy through sustained property, luxury, and investments.",
        "interpretation_ta": "ஜாதகர் நிலையான சொத்துக்கள் மற்றும் தொழில் முதலீடுகள் மூலம் பெரும் கோடீஸ்வரராவார்.",
        "source_page": "Page 93",
    },

    # --- Mars: Land, Property & Energy ---
    {
        "rule_id": "BN-MAR-001",
        "category": "property",
        "title_en": "Mars and Jupiter in Capricorn",
        "title_ta": "மகரத்தில் செவ்வாய் - குரு சேர்க்கை",
        "pattern": {"planet": "Mars", "sign": 10, "conjunction": ["Mars", "Jupiter"]},
        "interpretation_en": "The native owns expansive landed properties, agriculture fields, and real estate estates.",
        "interpretation_ta": "ஜாதகர் பரந்த விளைநிலங்கள், விவசாயப் பண்ணைகள் மற்றும் ரியல் எஸ்டேட் சொத்துக்களைப் பெறுவார்.",
        "source_page": "Page 98",
    },
    {
        "rule_id": "BN-MAR-002",
        "category": "property",
        "title_en": "Mars Aspects 4th House from Jupiter",
        "title_ta": "குருவுக்கு 4-ஆம் வீட்டை செவ்வாய் பார்த்தல்",
        "pattern": {"aspects_house_from": {"aspecting_planet": "Mars", "from_planet": "Jupiter", "target_house": 4}},
        "interpretation_en": "The native will construct their own grand residence or acquire high-value landed property.",
        "interpretation_ta": "ஜாதகர் கம்பீரமான சொந்த வீட்டைக் கட்டுவார் மற்றும் நிலம் வாங்கும் யோகம் பெறுவார்.",
        "source_page": "Page 99",
    },
    {
        "rule_id": "BN-MAR-003",
        "category": "health",
        "title_en": "Mars with Sun in Cancer",
        "title_ta": "கடகத்தில் செவ்வாய் - சூரியன் சேர்க்கை",
        "pattern": {"planet": "Mars", "sign": 4, "conjunction": ["Mars", "Sun"]},
        "interpretation_en": "Vulnerability to blood sugar imbalances or diabetes; dietary care advised.",
        "interpretation_ta": "இரத்த சர்க்கரை மற்றும் செரிமானக் கோளாறுகளுக்கு வாய்ப்புள்ளதால் உணவுப் பழக்கத்தில் கவனம் தேவை.",
        "source_page": "Page 101",
    },

    # --- Moon: Mother, Mind & Travel ---
    {
        "rule_id": "BN-MOON-001",
        "category": "travel",
        "title_en": "Moon Exalted or in Pisces",
        "title_ta": "சந்திரன் உச்சம் அல்லது மீனத்தில் சந்திரன்",
        "pattern": {"planet_in_any_sign": {"planet": "Moon", "signs": [2, 12]}},
        "interpretation_en": "The native undertakes frequent overseas tours, foreign journeys, and overseas voyages.",
        "interpretation_ta": "ஜாதகர் அடிக்கடி வெளிநாடுகளுக்குப் பயணம் செய்து கடல் கடந்து சென்று மேன்மை அடைவார்.",
        "source_page": "Page 106",
    },
    {
        "rule_id": "BN-MOON-002",
        "category": "family",
        "title_en": "Moon in Leo (Simha Chandra)",
        "title_ta": "சிம்மத்தில் சந்திரன்",
        "pattern": {"planet": "Moon", "sign": 5},
        "interpretation_en": "The mother of the native lives like a queen, commanding dignity, honor, and royal respect.",
        "interpretation_ta": "ஜாதகரின் தாயார் ராணியைப் போல கம்பீரமாகவும், குடும்பத்தில் பெரும் மரியாதையுடனும் வாழ்வார்.",
        "source_page": "Page 108",
    },
    {
        "rule_id": "BN-MOON-003",
        "category": "wealth",
        "title_en": "Moon with Venus (Chandra-Sukra)",
        "title_ta": "சந்திரன் - சுக்கிரன் சேர்க்கை",
        "pattern": {"conjunction": ["Moon", "Venus"]},
        "interpretation_en": "The native's mother is a wealthy, prosperous woman; native enjoys liquid financial fluidity.",
        "interpretation_ta": "ஜாதகரின் தாயார் செல்வச் செழிப்புடன் திகழ்வார்; ஜாதகருக்கும் பணப்புழக்கம் தாராளமாக இருக்கும்.",
        "source_page": "Page 109",
    },

    # --- Miscellaneous Special Naadi Yogas ---
    {
        "rule_id": "BN-MISC-001",
        "category": "life_force",
        "title_en": "Jupiter & Venus Encircle All Other Planets (Subha-Kartari)",
        "title_ta": "குருவும் சுக்கிரனும் அனைத்து கிரகங்களையும் சூழ்ந்துள்ள அமைப்பு",
        "pattern": {"special_encircle": True},
        "interpretation_en": "The native leads an illustrious, royal, and wealthy life with widespread respect.",
        "interpretation_ta": "ஜாதகர் சகல சௌபாக்கியங்களும் நிறைந்த அரச வாழ்க்கையையும் உயரிய சமூக மரியாதையையும் அனுபவிப்பார்.",
        "source_page": "Page 43",
    },
    {
        "rule_id": "BN-MISC-002",
        "category": "profession",
        "title_en": "Sun in Scorpio and Saturn in Libra",
        "title_ta": "விருச்சிகத்தில் சூரியன், துலாமில் சனி",
        "pattern": {"planet": "Sun", "sign": 8, "planet_in_sign": {"planet": "Saturn", "sign": 7}},
        "interpretation_en": "The native holds a prestigious, elevated post in Government departments.",
        "interpretation_ta": "ஜாதகர் அரசுத் துறைகளில் மிக உயர்ந்த அதிகாரமிக்க உயர் பதவியை வகிப்பார்.",
        "source_page": "Page 125",
    },
]

# ===========================================================================
# ACADEMIC RESEARCH ADDITION: BHRIGU NANDI NADI (R. G. RAO SYSTEM)
# Paper: "A Study of the Basic Rules in Bhrigu Nandi Nadi"
# Authors: A. Jagadeesan (Ph.D Research Scholar) & Dr. K. Jothimani (HOD & Assoc. Prof)
# School of Vedic Astrology, Vels Institute of Science, Technology & Advanced Studies (VISTAS)
# Citation: IJCRME, Vol. 7, Issue 2, pp. 23-31, 2022. ISSN: 2455-5428.
# ===========================================================================

BHRIGU_NANDI_NADI_RESEARCH_METADATA: Dict[str, Any] = {
    "paper_title": "A Study of the Basic Rules in Bhrigu Nandi Nadi",
    "paper_title_ta": "பிருகு நந்தி நாடியின் அடிப்படைக் கோட்பாடுகள் பற்றிய ஆய்வு",
    "authors": [
        "A. Jagadeesan (Full Time Ph.D Research Scholar)",
        "Dr. K. Jothimani (HOD & Associate Professor)",
    ],
    "institution": "School of Vedic Astrology, Vels Institute of Science, Technology & Advanced Studies (VISTAS), Chennai, Tamil Nadu",
    "journal": "International Journal of Current Research and Modern Education (IJCRME)",
    "volume_issue_pages": "Volume 7, Issue 2, pp. 23-31, 2022",
    "issn": "2455-5428",
    "impact_factor": "6.925",
    "system_founder": "Mr. R. G. Rao (Astrological Grandfather of Bhrigu Nandi Nadi)",
    "summary_en": (
        "Comprehensive academic formulation of Mr. R. G. Rao's 20 golden Bhrigu Nandi Nadi predictive rules. "
        "Considers directional trines (1, 5, 9), planetary friendships/enmities, 2nd and 12th flanking dynamics, "
        "retrograde reverse vectors, Rahu-Ketu division causing career outside, planetary interchanges (Parivartana), "
        "gender-differentiated Jeeva Karakas (Jupiter for male, Venus for female), and Saturn's vocational profiles."
    ),
    "summary_ta": (
        "ஆர். ஜி. ராவ் அவர்களின் பிருகு நந்தி நாடி முறையின் 20 அடிப்படைக் கணிப்பு விதிகள், திசை வழி சேர்க்கைகள் (1, 5, 9), "
        "நாடி நட்பு-பகை அட்டவணை, 2-12 அண்டை கிரகங்களின் தாக்கம், வக்ர கிரகங்களின் பின்நோக்கிய இயக்கம், "
        "ராகு-கேது பிரிக்கும் வெளியூர் வேலை யோகம், பரிவர்த்தனை விதிகள், பாலின ரீதியான ஜீவ காரகர் நிர்ணயம் "
        "(ஆண்களுக்கு குரு, பெண்களுக்கு சுக்கிரன்), மற்றும் சனியின் 12 ராசி தொழில் பலன்கள் ஆகியவற்றின் விரிவான ஆய்வு."
    ),
}

# 1. Classical Nadi Friendship & Enmity Matrix (R. G. Rao System)
BNN_PLANETARY_FRIENDSHIP: Dict[str, Dict[str, List[str]]] = {
    "Sun": {
        "friendly": ["Moon", "Mars", "Mercury", "Jupiter"],
        "inimical": ["Venus", "Saturn", "Rahu", "Ketu"],
    },
    "Moon": {
        "friendly": ["Sun", "Mars", "Jupiter", "Mercury"],
        "inimical": ["Venus", "Ketu", "Saturn", "Rahu"],
    },
    "Mars": {
        "friendly": ["Moon", "Jupiter", "Venus", "Sun", "Ketu"],
        "inimical": ["Mercury", "Rahu", "Saturn"],
    },
    "Mercury": {
        "friendly": ["Saturn", "Venus", "Sun", "Rahu"],
        "inimical": ["Mars", "Moon", "Jupiter", "Ketu"],
    },
    "Jupiter": {
        "friendly": ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "Moon"],
        "inimical": ["Mercury", "Venus"],
    },
    "Venus": {
        "friendly": ["Mars", "Mercury", "Saturn", "Rahu"],
        "inimical": ["Sun", "Moon", "Ketu", "Jupiter"],
    },
    "Saturn": {
        "friendly": ["Mercury", "Jupiter", "Venus", "Rahu"],
        "inimical": ["Sun", "Mars", "Moon", "Ketu"],
    },
    "Rahu": {
        "friendly": ["Mercury", "Saturn", "Venus", "Jupiter"],
        "inimical": ["Moon", "Mars", "Sun"],
    },
    "Ketu": {
        "friendly": ["Mars", "Jupiter"],
        "inimical": ["Venus", "Saturn", "Mercury", "Moon", "Sun"],
    },
}

# 2. Four Cardinal Directions in Bhrigu Nandi Nadi
BNN_DIRECTIONS: Dict[str, Dict[str, Any]] = {
    "East": {
        "element": "Fire",
        "element_ta": "நெருப்பு தத்துவம்",
        "signs": [1, 5, 9],  # Aries, Leo, Sagittarius
        "signs_en": ["Aries", "Leo", "Sagittarius"],
        "signs_ta": ["மேஷம்", "சிம்மம்", "தனுசு"],
    },
    "South": {
        "element": "Earth",
        "element_ta": "நில தத்துவம்",
        "signs": [2, 6, 10],  # Taurus, Virgo, Capricorn
        "signs_en": ["Taurus", "Virgo", "Capricorn"],
        "signs_ta": ["ரிஷபம்", "கன்னி", "மகரம்"],
    },
    "West": {
        "element": "Air",
        "element_ta": "காற்று தத்துவம்",
        "signs": [3, 7, 11],  # Gemini, Libra, Aquarius
        "signs_en": ["Gemini", "Libra", "Aquarius"],
        "signs_ta": ["மிதுனம்", "துலாம்", "கும்பம்"],
    },
    "North": {
        "element": "Water",
        "element_ta": "நீர் தத்துவம்",
        "signs": [4, 8, 12],  # Cancer, Scorpio, Pisces
        "signs_en": ["Cancer", "Scorpio", "Pisces"],
        "signs_ta": ["கடகம்", "விருச்சிகம்", "மீனம்"],
    },
}

# 3. 20 Golden Rules of Bhrigu Nandi Nadi (A. Jagadeesan & Dr. K. Jothimani, 2022)
BNN_20_GOLDEN_RULES: List[Dict[str, Any]] = [
    {
        "rule_number": 1,
        "title_en": "Activation of Karakatvas via 2nd, 12th, 7th, 5th, and 9th Houses",
        "title_ta": "2, 12, 7 மற்றும் 5, 9 ஆம் வீடுகளின் மூலம் காரகத்துவங்கள் இயங்குதல்",
        "principle_en": (
            "A planet's karakatvas act effectively only when planets occupy the 2nd, 12th, 7th, or 5th and 9th "
            "from its placement. Planets in the 1st, 5th, and 9th share the same directional trine and act as if conjoined."
        ),
        "principle_ta": (
            "ஒரு கிரகத்தின் காரகத்துவங்கள் அதற்கு 2, 12, 7 அல்லது 5, 9 ஆகிய வீடுகளில் பிற கிரகங்கள் நின்றால் மட்டுமே "
            "முழுமையாகச் செயல்படும். 1, 5, 9 ஆகிய திரிகோணங்களில் நிற்கும் கிரகங்கள் ஒரே திசையில் நின்று இணைந்து செயல்படுகின்றன."
        ),
        "source_ref": "Rule 1, IJCRME 2022, pp. 23-24",
    },
    {
        "rule_number": 2,
        "title_en": "Cooperation of Planets in the Same Direction by Degree Order",
        "title_ta": "ஒரே திசையில் உள்ள கிரகங்கள் பாகை வரிசைப்படி இணைந்து பலன் தருதல்",
        "principle_en": (
            "Planets occupying signs of the same direction work together as a unified team. "
            "Their longitudinal degrees define the chronological sequence of their combined expression (e.g., Saturn 2° -> Mercury 10° -> Jupiter 24°)."
        ),
        "principle_ta": (
            "ஒரே திசைக்குரிய ராசிகளில் நிற்கும் கிரகங்கள் ஒன்றிணைந்து செயல்படுகின்றன. அவற்றின் பாகை அளவுகளே பலன்கள் "
            "வெளிப்படும் கால வரிசையைத் தீர்மானிக்கின்றன (எ.கா: சனி 2°, புதன் 10°, குரு 24° எனில் சனி + புதன் + குரு சேர்க்கையாகும்)."
        ),
        "source_ref": "Rule 2, IJCRME 2022, p. 24",
    },
    {
        "rule_number": 3,
        "title_en": "Direct 7th Sign Impact: Auspicious if Friendly, Adverse if Inimical",
        "title_ta": "7-ஆம் வீட்டில் உள்ள கிரகத்தின் நேரடித் தாக்கம் (நட்பு எனில் சுபம், பகை எனில் அசுபம்)",
        "principle_en": (
            "A planet in the 7th sign to a karaka exerts direct polar aspect. If friendly, it confers profound blessing "
            "(e.g., Jupiter 7th to Moon grants vitality to mother and travel profits). If inimical, it causes friction and adversity "
            "(e.g., Mars and Saturn in 7th cause industry trouble, sibling disunity, and accident hazard)."
        ),
        "principle_ta": (
            "ஒரு கிரகத்திற்கு 7-ஆம் வீட்டில் நிற்கும் கிரகம் நட்பு கிரகமாக இருந்தால் நற்பலன்களையும், பகை கிரகமாக இருந்தால் தீய பலன்களையும் தரும். "
            "(சந்திரனுக்கு 7-ல் குரு நின்றால் தாய்க்கு நீண்ட ஆயுளும் பிரயாண லாபமும்; செவ்வாயும் சனியும் 7-ல் நின்றால் தொழிலில் தடையும் விபத்து கண்டமும் ஏற்படும்)."
        ),
        "source_ref": "Rule 3, IJCRME 2022, p. 24",
    },
    {
        "rule_number": 4,
        "title_en": "Flanking by 2nd and 12th Houses: Subha/Papa Kartari Dynamics",
        "title_ta": "2 மற்றும் 12-ஆம் வீடுகளில் நிற்கும் கிரகங்களின் சுப/பாப கர்த்தாரி பலன்கள்",
        "principle_en": (
            "When friendly planets occupy the 2nd and 12th houses of a planet, favorable karakatva benefits manifest effortlessly. "
            "If inimical planets occupy the 2nd and 12th (e.g., Sun and Mars flanking Saturn), the native suffers frequent job transfers, "
            "vocational insecurity, industry shutdowns, and a restless work atmosphere."
        ),
        "principle_ta": (
            "ஒரு கிரகத்திற்கு 2 மற்றும் 12-ஆம் வீடுகளில் நட்பு கிரகங்கள் இருந்தால் நற்பலன்களும், பகை கிரகங்கள் இருந்தால் பாதகமான பலன்களும் உண்டாகும். "
            "(சனிக்கு இருபுறமும் சூரியனும் செவ்வாயும் நின்றால் அடிக்கடி வேலை மாற்றம், வேலை இழப்பு மற்றும் பணியிடத்தில் அமைதியின்மை ஏற்படும்)."
        ),
        "source_ref": "Rule 4, IJCRME 2022, p. 24",
    },
    {
        "rule_number": 5,
        "title_en": "Exaltation Blockade: Hostile Planets in 2nd and 12th Houses",
        "title_ta": "உச்ச கிரகம் ஆயினும் 2, 12-ல் பகை கிரகங்கள் நின்றால் உச்ச பலன் தடைபடுதல்",
        "principle_en": (
            "Even if a planet is exalted, if it is flanked by hostile planets in the 2nd and 12th houses, "
            "its exalted beneficence is blocked and neutralized. (e.g., Exalted Moon with Rahu in 2nd and Saturn in 12th cannot give exalted fruits, "
            "causing psychological strain to mother)."
        ),
        "principle_ta": (
            "ஒரு கிரகம் உச்சம் பெற்றிருந்தாலும், அதன் 2 மற்றும் 12-ஆம் வீடுகளில் பகை கிரகங்கள் நின்றால் உச்ச பலன்கள் தடைபடும். "
            "(சந்திரன் ரிஷபத்தில் உச்சம் பெற்றாலும் 2-ல் ராகுவும் 12-ல் சனியும் நின்றால் தாயாருக்கு மன உளைச்சலும் நரம்பு உபாதைகளும் ஏற்படும்)."
        ),
        "source_ref": "Rule 5, IJCRME 2022, pp. 24-25",
    },
    {
        "rule_number": 6,
        "title_en": "Retrograde Planet in 2nd House Reversing Harm into Karaka",
        "title_ta": "2-ஆம் வீட்டில் உள்ள பகை கிரகம் வக்ரம் பெற்று பின்னோக்கித் தாக்கும் விதி",
        "principle_en": (
            "If an inimical planet in the 2nd house to a karaka becomes retrograde, it reverses backward into the karaka's sign, "
            "inflicting active damage. (e.g., Mercury with retrograde inimical Mars in 2nd bars brother's academic progress)."
        ),
        "principle_ta": (
            "ஒரு கிரகத்திற்கு 2-ஆம் வீட்டில் நிற்கும் பகை கிரகம் வக்ரம் பெற்றால், அது பின்னோக்கி நகர்ந்து அந்த கிரகத்தின் காரகத்துவத்தை பாதிக்கும். "
            "(புதனுக்கு 2-ல் பகை கிரகமான செவ்வாய் வக்ரம் பெற்று நின்றால் சகோதரனின் கல்விக்கு தடை ஏற்படும்)."
        ),
        "source_ref": "Rule 6, IJCRME 2022, p. 25",
    },
    {
        "rule_number": 7,
        "title_en": "Hierarchy of Influence: 7th House > 2nd House > 12th House",
        "title_ta": "காரகத்துவ தாக்கத்தின் வரிசை: 7-ஆம் வீடு > 2-ஆம் வீடு > 12-ஆம் வீடு",
        "principle_en": (
            "The planet situated in the 7th house exerts the strongest, most direct influence on the karaka. "
            "The next strongest impact is delivered by the 2nd house planet, followed by the 12th house planet."
        ),
        "principle_ta": (
            "ஒரு கிரகத்தின் காரகத்துவத்தை மிகவும் தீவிரமாக பாதிப்பது 7-ஆம் வீட்டில் நிற்கும் கிரகம் ஆகும். "
            "அதற்கு அடுத்தபடியாக 2-ஆம் வீட்டில் உள்ள கிரகமும், பின்னர் 12-ஆம் வீட்டில் உள்ள கிரகமும் தாக்கம் செலுத்துகின்றன."
        ),
        "source_ref": "Rule 7, IJCRME 2022, p. 25",
    },
    {
        "rule_number": 8,
        "title_en": "Isolated Exalted Planet Neutralized without Geometric Support",
        "title_ta": "தனித்து நிற்கும் உச்ச கிரகம் (2, 12, 7, 5, 9-ல் கிரகங்கள் இல்லாவிடில் பலனற்றிருத்தல்)",
        "principle_en": (
            "If an exalted planet does not have any planets occupying its 2nd, 12th, 7th, 5th, or 9th signs, "
            "it remains passive and neutral, unable to dispense its exalted fruits."
        ),
        "principle_ta": (
            "ஒரு கிரகம் உச்சம் பெற்றிருந்தாலும், அதன் 2, 12, 7, 5, 9 ஆகிய வீடுகளில் எந்த ஒரு கிரகமும் அமையாவிடில், "
            "அந்த உச்ச கிரகம் நற்பலன்களைத் தராமல் செயலற்று மௌனமாக இருக்கும்."
        ),
        "source_ref": "Rule 8, IJCRME 2022, p. 25",
    },
    {
        "rule_number": 9,
        "title_en": "Debilitated Planet Uplifted by Friendly Planetary Network",
        "title_ta": "நீச கிரகம் 2, 12, 7, 5, 9-ல் நட்பு கிரகங்கள் பெற்றால் நீசபங்கம் அடைந்து சிறத்தல்",
        "principle_en": (
            "Even if a karaka planet is debilitated, if it receives friendly planets in the 2nd, 12th, 7th, 5th, or 9th houses, "
            "it sheds debility and performs its causal benefits splendidly (e.g., Debilitated Mercury flanked by Venus in 12th, Sun in 2nd, "
            "Jupiter in 5th, Saturn in 9th gives superb scholastic intellect)."
        ),
        "principle_ta": (
            "ஒரு கிரகம் நீசம் பெற்றிருந்தாலும், அதற்கு 2, 12, 7, 5, 9 ஆகிய வீடுகளில் நட்பு கிரகங்கள் அமைந்தால் நீச தோஷம் நீங்கி சிறந்த பலன்களை வழங்கும். "
            "(புதன் மீனத்தில் நீசம் பெற்றாலும் 12-ல் சுக்கிரன், 2-ல் சூரியன், 5-ல் குரு, 9-ல் சனி அமையப் பெற்றால் உயரிய கல்வி ஞானம் கிட்டும்)."
        ),
        "source_ref": "Rule 9, IJCRME 2022, pp. 25-26",
    },
    {
        "rule_number": 10,
        "title_en": "Rahu-Ketu Bisection: Division of Jupiter and Saturn Causing Profession Outside",
        "title_ta": "ராகு-கேது அச்சு குருவையும் சனியையும் பிரிப்பதால் வெளியூர்/வெளிநாட்டு வேலை யோகம்",
        "principle_en": (
            "The Rahu-Ketu axis bisects the horoscope into two distinct halves. When Jeeva Karaka (Jupiter) is situated on one side "
            "of the nodal axis and Karma Karaka (Saturn) is situated on the opposite side, the native's profession is established outside their native place or abroad."
        ),
        "principle_ta": (
            "ஜாதகத்தில் ராகு-கேது அச்சு ஜாதகத்தை இரண்டு பிரிவுகளாகப் பிரிக்கிறது. இந்த அச்சின் ஒரு புறத்தில் குருவும் (ஜீவன்) "
            "மறுபுறத்தில் சனியும் (கர்மம்) அமைந்தால், ஜாதகருக்கு பிறந்த ஊருக்கு வெளியே அல்லது வெளிநாட்டில் உத்தியோகம் அமையும்."
        ),
        "source_ref": "Rule 10, IJCRME 2022, p. 26",
    },
    {
        "rule_number": 11,
        "title_en": "Debilitation Cancellation via Friendly Mutual Interchange",
        "title_ta": "நட்பு கிரகங்களின் பரிவர்த்தனையால் நீசம் நீங்கி ஆட்சி பலம் பெறுதல்",
        "principle_en": (
            "If a debilitated planet enters into a mutual house interchange (Parivartana) with a friendly planet, "
            "its debilitation is immediately cancelled, functioning as if residing in its own sign with full dignity."
        ),
        "principle_ta": (
            "நீசம் பெற்ற கிரகம் ஒரு நட்பு கிரகத்துடன் பரிவர்த்தனை செய்யும்போது, அதன் நீசத்தன்மை விலகி சொந்த வீட்டில் ஆட்சி பலம் பெற்றதைப் போல நற்பலன்களைத் தரும்."
        ),
        "source_ref": "Rule 11, IJCRME 2022, p. 26",
    },
    {
        "rule_number": 12,
        "title_en": "Debilitated Planet Restores Sovereignty upon Returning Home in Parivartana",
        "title_ta": "பரிவர்த்தனையால் நீச கிரகம் சொந்த ராசிக்குச் சென்று ஆட்சி பலம் பெறுதல்",
        "principle_en": (
            "When a debilitated planet interchanges houses and effectively occupies its own home sign, "
            "debility dissolves completely, conferring ruling power and executive stability."
        ),
        "principle_ta": (
            "நீசமடைந்த கிரகம் பரிவர்த்தனை மூலம் தனது சொந்த வீட்டிற்கு செல்லும் போது நீசம் முற்றிலும் நீங்கி பூரண ஆட்சி பலத்தைப் பெறுகிறது."
        ),
        "source_ref": "Rule 12, IJCRME 2022, p. 26",
    },
    {
        "rule_number": 13,
        "title_en": "Combustion Evil Vanishes through Planetary Interchange",
        "title_ta": "பரிவர்த்தனையால் அஸ்தமன தோஷம் நீங்கி பலம் பெறுதல்",
        "principle_en": (
            "If a planet is combust by proximity to the Sun but participates in a mutual house interchange with another planet, "
            "the evil of combustion disappears as it secures its own sign strength."
        ),
        "principle_ta": (
            "சூரியனுடன் இணைந்து அஸ்தமனம் பெற்ற கிரகம் பரிவர்த்தனை அடையும் போது, அஸ்தமன தோஷம் மறைந்து தனது சுய பலத்தை மீட்டெடுக்கிறது."
        ),
        "source_ref": "Rule 13, IJCRME 2022, p. 26",
    },
    {
        "rule_number": 14,
        "title_en": "Retrograde Planet Moves toward 12th House with Half-Sight Aspect",
        "title_ta": "வக்ர கிரகம் 12-ஆம் வீட்டை நோக்கி நகர்ந்து பின்னோக்கிய பார்வை செலுத்துதல்",
        "principle_en": (
            "A retrograde planet shifts its active energy vector toward the 12th house from its sign, "
            "casting a backward half-aspect that can neutralize dangers or rescue vulnerable planets situated behind it."
        ),
        "principle_ta": (
            "வக்ர கிரகம் தான் நின்ற ராசிக்கு 12-ஆம் வீட்டை நோக்கி பின்னோக்கி நகர்ந்து, தனது பார்வை மூலம் பின்னால் உள்ள கிரகங்களின் தோஷங்களை நீக்கி காக்கும்."
        ),
        "source_ref": "Rule 14, IJCRME 2022, p. 26",
    },
    {
        "rule_number": 15,
        "title_en": "Mutual Interchange of Two Debilitated Planets Cancels Harm",
        "title_ta": "இரு நீச கிரகங்கள் தங்களுக்குள் பரிவர்த்தனை செய்தால் இருவருக்கும் ஆட்சி பலம் கிட்டுதல்",
        "principle_en": (
            "When two debilitated planets interchange signs with each other (e.g., Mars in Cancer and Moon in Scorpio), "
            "both shedding debility harm and gaining the sovereign status of their own signs."
        ),
        "principle_ta": (
            "இரண்டு நீச கிரகங்கள் தங்களுக்குள் வீடுகளை பரிவர்த்தனை செய்து கொண்டால் (எ.கா: கடகத்தில் செவ்வாய், விருச்சிகத்தில் சந்திரன்), "
            "இருவரின் நீச தோஷமும் விலகி சொந்த வீட்டில் ஆட்சி பெற்ற சுப பலன் உண்டாகும்."
        ),
        "source_ref": "Rule 15, IJCRME 2022, pp. 26-27",
    },
    {
        "rule_number": 16,
        "title_en": "Debilitated Planet Attains Exaltation through Planetary Interchange",
        "title_ta": "பரிவர்த்தனை மூலம் நீச கிரகம் உச்ச பலனை எட்டுதல்",
        "principle_en": (
            "In planetary interchange, a debilitated planet can transition directly into its exaltation sign "
            "(e.g., Debilitated Mercury in Pisces interchanging with Jupiter in Virgo enters Virgo where Mercury is exalted)."
        ),
        "principle_ta": (
            "பரிவர்த்தனையின் மூலம் நீசமடைந்த கிரகம் தனது உச்ச ராசிக்குச் சென்று உச்ச பலனைப் பெற முடியும் (மீனத்தில் உள்ள நீச புதன் கன்னியில் உள்ள குருவுடன் பரிவர்த்தனை ஆகும்போது கன்னிக்கு சென்று உச்சமடைகிறார்)."
        ),
        "source_ref": "Rule 16, IJCRME 2022, p. 27",
    },
    {
        "rule_number": 17,
        "title_en": "Exalted Planet Weakened by Moving into Inimical Sign in Interchange",
        "title_ta": "பரிவர்த்தனையால் உச்ச கிரகம் பகை கிரகத்தின் தொடர்பால் பலவீனமடைதல்",
        "principle_en": (
            "An exalted planet can lose its pristine potency if, through planetary interchange or transit displacement, "
            "an inimical planet occupies its dispositor sign, diminishing its auspicious output."
        ),
        "principle_ta": (
            "உச்சம் பெற்ற கிரகமாயினும் பரிவர்த்தனையின் போது பகை கிரகத்தின் சேர்க்கை அல்லது பார்வைக்கு ஆளானால் அதன் உச்ச பலம் குறைய வாய்ப்புண்டு."
        ),
        "source_ref": "Rule 17, IJCRME 2022, p. 27",
    },
    {
        "rule_number": 18,
        "title_en": "Transmission of Retrograde Nature through House Interchange",
        "title_ta": "வக்ர கிரகத்துடன் பரிவர்த்தனை செய்யும் சாதாரண கிரகமும் வக்ர பலனைப் பெறுதல்",
        "principle_en": (
            "When a non-retrograde planet enters into a house interchange with a retrograde planet, "
            "the non-retrograde planet absorbs the retrograde characteristics and behaves as a retrograde body."
        ),
        "principle_ta": (
            "நேர்கதியில் உள்ள ஒரு கிரகம், வக்ரம் பெற்ற மற்றொரு கிரகத்துடன் பரிவர்த்தனை செய்தால், நேர்கதி கிரகமும் வக்ர தன்மையைப் பெற்று பின்னோக்கிய பலன்களைத் தரும்."
        ),
        "source_ref": "Rule 18, IJCRME 2022, p. 27",
    },
    {
        "rule_number": 19,
        "title_en": "12th House Inimical Planet Spares Karaka when Retrograde",
        "title_ta": "12-ஆம் வீட்டில் உள்ள பகை கிரகம் வக்ரமடைந்தால் காரகத்தை தாக்காமல் பின்வாங்குதல்",
        "principle_en": (
            "A 12th house planet normally advances forward toward the karaka. However, if that 12th house inimical planet is RETROGRADE, "
            "it moves backward away from the karaka, sparing the karaka planet from affliction."
        ),
        "principle_ta": (
            "12-ஆம் வீட்டில் நிற்கும் கிரகம் பொதுவாக காரகத்தை நோக்கி முன்னேறும். ஆனால் அந்த 12-ஆம் வீட்டுப் பகை கிரகம் வக்ரம் பெற்றிருந்தால் "
            "அது பின்னோக்கி விலகிச் செல்வதால் காரக கிரகம் எந்த பாதிப்பும் இன்றி தப்பித்துவிடும்."
        ),
        "source_ref": "Rule 19, IJCRME 2022, pp. 27-28",
    },
    {
        "rule_number": 20,
        "title_en": "2nd House Inimical Planet Harms Karaka when Retrograde",
        "title_ta": "2-ஆம் வீட்டில் உள்ள பகை கிரகம் வக்ரமடைந்து பின்னோக்கி வந்து காரகத்தை தாக்குதல்",
        "principle_en": (
            "An inimical planet in the 2nd house has normally already crossed and moved past the karaka planet. "
            "However, if that 2nd house inimical planet becomes RETROGRADE, it reverses backward and strikes the karaka, triggering vulnerabilities."
        ),
        "principle_ta": (
            "2-ஆம் வீட்டில் நிற்கும் பகை கிரகம் ஏற்கனவே காரகத்தைக் கடந்து சென்றுவிட்டதாகக் கருதப்படும். ஆனால் அது வக்ரம் அடைந்தால் "
            "மீண்டும் பின்னோக்கி நகர்ந்து வந்து காரக கிரகத்தை கடுமையாகப் பாதிக்கும் (எ.கா: செவ்வாய்க்கு 2-ல் உள்ள சனி வக்ரமடைந்து செவ்வாயைப் பார்ப்பதால் சகோதர ஒற்றுமையின்மையும் விபத்துக்களும் ஏற்படும்)."
        ),
        "source_ref": "Rule 20, IJCRME 2022, p. 28",
    },
]

# 4. Saturn's Vocational Indications in 12 Zodiac Signs (A. Jagadeesan & Dr. K. Jothimani, 2022)
BNN_SATURN_SIGN_CAREERS: Dict[int, Dict[str, str]] = {
    1: {
        "en": "Machinery, mechanical roads, civil/mechanical engineering, uniformed services, military, defense, and police departments.",
        "ta": "எந்திரவியல், மெக்கானிக்கல் பணிகள், பொறியியல் துறை, சீருடைப் பணியாளர்கள், ராணுவம் மற்றும் காவல்துறை.",
    },
    2: {
        "en": "Monetary business, automotive industry, moneylending/interest, banking, treasury, software, and computer industries.",
        "ta": "நிதித்துறை, வாகன உற்பத்தி/விற்பனை, வட்டித் தொழில், வங்கித்துறை, கணினி மென்பொருள் தொழினுட்பம்.",
    },
    3: {
        "en": "Intellectual practice, writing, journalism, speech, mass communication, sports, commercial brokerage, publishing, and agencies.",
        "ta": "புத்திபூர்வமான பணிகள், எழுத்து, பத்திரிகை, மக்கள் தொடர்பு, விளையாட்டு, வர்த்தக புரோக்கரேஜ், பதிப்பகம் மற்றும் ஏஜென்சி தொழில்.",
    },
    4: {
        "en": "Hostel management, nursing, healthcare service, dairy, saline/water industries, astrology, clerical work, groceries, and agriculture.",
        "ta": "விடுதி நிர்வாகம், நர்சிங், மருத்துவ நல்வாழ்வு பணி, பால்பண்ணை, குடிநீர்/திரவ வர்த்தகம், ஜோதிடம், எழுத்தர் பணி, மளிகை மற்றும் விவசாயம்.",
    },
    5: {
        "en": "Government service, public administrative authority, medical professions, fine arts, electronics, and management with strict executive command.",
        "ta": "அரசுப் பணி, பொது நிர்வாக அதிகாரம், மருத்துவத்துறை, நுண்கலை, மின்னணுவியல் மற்றும் கடுமையான கட்டுப்பாட்டுடன் கூடிய தலைமைப் பொறுப்புகள்.",
    },
    6: {
        "en": "Highly lucrative commerce, stock market, real estate, brokerage, agro-based industries, building construction materials, and crop farming.",
        "ta": "அதிக லாபகரமான வர்த்தகம், பங்குச் சந்தை, ரியல் எஸ்டேட், புரோக்கரேஜ், விவசாய சார் தொழில்கள், கட்டுமானப் பொருட்கள் மற்றும் பயிர் உற்பத்தி.",
    },
    7: {
        "en": "Exalted Saturn: Legal luminary, judge, legal counsel, luxury garments, interior decoration, engineering, fashion design, and automotive trade.",
        "ta": "சனி உச்சம்: வழக்கறிஞர், நீதிபதி, ஆடை ஆபரணங்கள், உள் அலங்காரம், பொறியியல் துறை, பேஷன் டிசைனிங் மற்றும் சொகுசு வாகனத் தொழில்.",
    },
    8: {
        "en": "Heavy machinery, metallurgical engineering, land management, elemental discovery, mineral research, astrology, and esoteric investigations.",
        "ta": "கனரக எந்திரங்கள், உலோகப் பொறியியல், நில மேலாண்மை, தாதுப் பொருட்கள் ஆராய்ச்சி, ஜோதிடம் மற்றும் மறைபொருள் சாஸ்திரங்கள்.",
    },
    9: {
        "en": "Honorable legal profession, professorship, teachers, banking management, government treasury, law enforcement, and accounting.",
        "ta": "கௌரவமிக்க சட்டத்துறை, பேராசிரியர், ஆசிரியர் பணி, வங்கி மேலாளர், அரசு கருவூலம், நீதித்துறை மற்றும் கணக்கியல்.",
    },
    10: {
        "en": "Fertilizer industry, oil commerce, mining, restaurants, food enterprises, technological machinery, agriculture, and water management.",
        "ta": "உரத் தொழில், எண்ணெய் வர்த்தகம், சுரங்கம், உணவகம், உணவுப் பொருட்கள், நவீன எந்திரவியல், விவசாயம் மற்றும் நீர் மேலாண்மை.",
    },
    11: {
        "en": "Astrology, spirituality, higher teaching, psychology, scientific research, executive management, aviation, defense, and aeronautics.",
        "ta": "ஜோதிடம், ஆன்மீகம், உயர் கல்வி, உளவியல், அறிவியல் ஆராய்ச்சி, நிர்வாகப் பொறுப்பு, விமானத்துறை மற்றும் பாதுகாப்பு துறை.",
    },
    12: {
        "en": "Law, medicine, history, religion, asceticism, priesthood, banking, judiciary, philosophy, charitable trusts, and high social prestige.",
        "ta": "சட்டம், மருத்துவம், வரலாறு, மதம், துறவறம், ஆலயப் பணிகள், வங்கித்துறை, நீதித்துறை, தத்துவம், அறக்கட்டளைகள் மற்றும் உயரிய சமூக அந்தஸ்து.",
    },
}

# 5. Planetary Industries Catalogue in Bhrigu Nandi Nadi
BNN_PLANETARY_INDUSTRIES: Dict[str, Dict[str, str]] = {
    "Sun": {
        "en": "Government professions, administrative bureaucracies, magistrates, medical surgeons, auditors, paternal enterprise, politics, leadership, and electronics.",
        "ta": "அரசுப் பணிகள், பொது நிர்வாகம், நீதிபதிகள், அறுவை சிகிச்சை மருத்துவம், தணிக்கை, தந்தை வழி தொழில், அரசியல், தலைமை மற்றும் எலக்ட்ரானிக்ஸ்.",
    },
    "Moon": {
        "en": "Jobs related to women, travel industries, sailors, navy, nursing, dairy, liquid commerce, restaurants, textiles, sewing, irrigation, and laundry.",
        "ta": "பெண்கள் சார்ந்த பணிகள், பயணத்துறை, மாலுமிகள், கடற்படை, நர்சிங், பால்பண்ணை, திரவ வர்த்தகம், உணவகம், ஜவுளி, தையல், நீர்ப்பாசனம் மற்றும் சலவைத்தொழில்.",
    },
    "Mars": {
        "en": "Civil engineering, military, defense, construction, electrical engineering, landholding, surveyors, drivers, surgeons, miners, and uniformed personnel.",
        "ta": "சிவில் என்ஜினியரிங், ராணுவம், பாதுகாப்பு, கட்டுமானம், மின்பொறியியல், நிலபுலன்கள், நில அளவையாளர், ஓட்டுநர், அறுவை சிகிச்சை மற்றும் சீருடைப் பணிகள்.",
    },
    "Mercury": {
        "en": "Commercial business, teaching, lecturers, accounting, auditing, poetry, writing, journalism, book publishing, insurance, postal, law, and real estate brokerage.",
        "ta": "வணிக வியாபாரம், ஆசிரியர், விரிவுரையாளர், கணக்கியல், தணிக்கை, கவிதை, எழுத்து, பத்திரிகை, பதிப்பகம், காப்பீடு, அஞ்சல்துறை, சட்டம் மற்றும் புரோக்கரேஜ்.",
    },
    "Jupiter": {
        "en": "Barter and commerce, public administration, university professors, judges, legal advisors, government treasuries, spiritual institutions, finance, gold, and medicine.",
        "ta": "வர்த்தகம், அரசு நிர்வாகம், பல்கலைக்கழக பேராசிரியர், நீதிபதிகள், சட்ட ஆலோசகர்கள், அரசு கருவூலம், ஆன்மீக நிறுவனங்கள், நிதி, தங்கம் மற்றும் சித்தா/ஹோமியோபதி மருத்துவம்.",
    },
    "Venus": {
        "en": "Arts, music, 3-star/5-star luxury hotels, restaurant entertainment, cosmetics, jewelry, film stars, dance, perfumes, luxury transportation, and fashion.",
        "ta": "கலைத்துறை, இசை, நட்சத்திர உணவகங்கள், அழகு சாதனங்கள், நகைக்கடைகள், சினிமா, நடனம், வாசனை திரவியங்கள், ஆடம்பர வாகனங்கள் மற்றும் பேஷன் அலங்காரம்.",
    },
    "Saturn": {
        "en": "Agriculture, crop farming, physiotherapy, mining, petrol pumps, physical labor, leather, underground industries, wage labor, oilseeds, and astrology.",
        "ta": "விவசாயம், பயிர் உற்பத்தி, பிசியோதெரபி, சுரங்கம், பெட்ரோல் பங்க், உடலுழைப்பு, தோல் தொழில், பூமிக்கடி பணிகள், கூலித்தொழில், எண்ணெய் வித்துக்கள் மற்றும் ஜோதிடம்.",
    },
    "Rahu": {
        "en": "Radio, television, space exploration, espionage, cinema, photography, Xerox, electronic media, pharmaceuticals, synthetic chemicals, and unconventional wealth.",
        "ta": "வானொலி, தொலைக்காட்சி, விண்வெளிப் பயணம், உளவுத்துறை, சினிமா, புகைப்படம், ஜெராக்ஸ் கடை, மின்னணு ஊடகம், மருந்தகம் மற்றும் நவீன தொழினுட்பங்கள்.",
    },
    "Ketu": {
        "en": "Foreign trade, spiritual monasteries, temple service, fingerprinting, yoga, meditation, occult healing, thread weaving, textiles, and radiology/diagnostics.",
        "ta": "வெளிநாட்டு வர்த்தகம், ஆன்மீக மடங்கள், ஆலயப் பணி, கைரேகை, யோகா, தியானம், மறைபொருள் மருத்துவம், நூல் நெசவு, ஜவுளி மற்றும் கதிர்வீச்சு/ஸ்கேன் பரிசோதனை.",
    },
}

