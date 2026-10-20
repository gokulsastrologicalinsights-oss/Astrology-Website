"""Core data models, enums, taxonomy, and classical constants for the Marriage Compatibility Engine."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class CompatibilityOutcome(str, Enum):
    """Standardized top-level verdict taxonomy for marriage compatibility."""
    FAVOURABLE_UNDER_SELECTED_RULES = "FAVOURABLE_UNDER_SELECTED_RULES"
    MIXED_OR_CONDITIONAL = "MIXED_OR_CONDITIONAL"
    UNFAVOURABLE_UNDER_SELECTED_RULES = "UNFAVOURABLE_UNDER_SELECTED_RULES"
    INDETERMINATE = "INDETERMINATE"


class RuleEvaluationStatus(str, Enum):
    """Explicit lifecycle status for individual rule and dosha evaluations."""
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    CANCELLED_BY_RULE = "CANCELLED_BY_RULE"
    MITIGATED = "MITIGATED"
    MUTUALLY_MATCHED = "MUTUALLY_MATCHED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class PoruthamStatus(str, Enum):
    """Execution status for an individual Porutham rule."""
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"
    UNSUPPORTED = "UNSUPPORTED"


class PoruthamGrade(str, Enum):
    """Grading taxonomy for traditional Tamil Poruthams."""
    UTHAMA = "Uthama"       # Best / Highly Favorable
    MADHYAMA = "Madhyama"   # Average / Acceptable
    ADHAMA = "Adhama"       # Inauspicious / Unfavorable
    VARJYA = "Varjya"       # Strictly Forbidden / Severe Affliction


class GanaType(str, Enum):
    DEVA = "Deva"
    MANUSHYA = "Manushya"
    RAKSHASA = "Rakshasa"


class NadiType(str, Enum):
    ADI = "Adi"         # Vata
    MADHYA = "Madhya"   # Pitta
    ANTYA = "Antya"     # Kapha


class RajjuType(str, Enum):
    SHIRO = "Shiro"     # Head (Sirasu)
    KANTHA = "Kantha"   # Neck (Kazhuthu)
    UDARA = "Udara"     # Stomach (Vayiru)
    KATI = "Kati"       # Hip (Idai)
    PADA = "Pada"       # Foot (Padam)


class VashyaCategory(str, Enum):
    CHATUSHPADA = "Chatushpada"  # Quadruped / Four-legged
    DWIPADA = "Dwipada"          # Biped / Human
    JALACHARA = "Jalachara"      # Aquatic
    VANACHARA = "Vanachara"      # Wild / Forest beasts (Leo)
    KEETA = "Keeta"              # Insect / Scorpion


class DignityType(str, Enum):
    """Classical planetary dignity classifications."""
    EXALTED = "Exalted"
    MOOLATRIKONA = "Moolatrikona"
    OWN_SIGN = "Own Sign"
    FRIENDLY = "Friendly"
    NEUTRAL = "Neutral"
    INIMICAL = "Inimical"
    DEBILITATED = "Debilitated"


class FunctionalNature(str, Enum):
    """Parashari functional nature based on Lagna rulership."""
    YOGAKARAKA = "Yogakaraka"
    FUNCTIONAL_BENEFIC = "Functional Benefic"
    FUNCTIONAL_NEUTRAL = "Functional Neutral"
    FUNCTIONAL_MALEFIC = "Functional Malefic"


class SamadoshamOutcome(str, Enum):
    """Explicit outcomes for mutual Kuja Dosha (Samadosham) evaluation."""
    MUTUALLY_MATCHED = "MUTUALLY_MATCHED"          # Both have balanced Kuja Dosha (Doshasya samyam bhavati)
    CANCELLED_BY_RULE = "CANCELLED_BY_RULE"        # Cancelled by individual classical source rules
    MITIGATED = "MITIGATED"                        # Mild affliction balanced by counterpoise or benefic aspect
    NOT_MUTUALLY_MATCHED = "NOT_MUTUALLY_MATCHED"  # Severe uncancelled Kuja in one chart vs unafflicted partner
    INDETERMINATE = "INDETERMINATE"                # Incomplete or ambiguous chart data
    UNSUPPORTED = "UNSUPPORTED"                    # Rule unsupported or unverified


class PapasamyaVerdict(str, Enum):
    """Outcomes for South Indian Papasamya malefic point balance."""
    FAVORABLE = "FAVORABLE"            # Favorable balance (Groom >= Bride, diff <= 25%, or diff <= 10%)
    TOLERABLE = "TOLERABLE"            # Groom carries higher malefic load (25% - 50% excess), traditionally tolerated
    UNFAVORABLE = "UNFAVORABLE"        # Bride carries excess malefic load (> 25% excess over groom), strictly forbidden
    INDETERMINATE = "INDETERMINATE"    # Incomplete chart data


# ---------------------------------------------------------------------------
# Canonical Astronomical & Astrological Reference Constants
# ---------------------------------------------------------------------------

SIGN_NAMES_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

SIGN_NAMES_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# 27 Nakshatras (0-indexed: 0=Ashwini .. 26=Revati)
NAKSHATRA_NAMES_EN: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_NAMES_TA: List[str] = [
    "அசுவினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
    "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
    "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
]

NAKSHATRA_LORDS: List[str] = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

# Canonical Nakshatra Gana Mapping
NAKSHATRA_GANA: Dict[int, GanaType] = {
    0: GanaType.DEVA,       # Ashwini
    1: GanaType.MANUSHYA,   # Bharani
    2: GanaType.RAKSHASA,   # Krittika
    3: GanaType.MANUSHYA,   # Rohini
    4: GanaType.DEVA,       # Mrigashira
    5: GanaType.MANUSHYA,   # Ardra
    6: GanaType.DEVA,       # Punarvasu
    7: GanaType.DEVA,       # Pushya
    8: GanaType.RAKSHASA,   # Ashlesha
    9: GanaType.RAKSHASA,   # Magha
    10: GanaType.MANUSHYA,  # Purva Phalguni
    11: GanaType.MANUSHYA,  # Uttara Phalguni
    12: GanaType.DEVA,      # Hasta
    13: GanaType.RAKSHASA,  # Chitra
    14: GanaType.DEVA,      # Swati
    15: GanaType.RAKSHASA,  # Vishakha
    16: GanaType.DEVA,      # Anuradha
    17: GanaType.RAKSHASA,  # Jyeshtha
    18: GanaType.RAKSHASA,  # Mula
    19: GanaType.MANUSHYA,  # Purva Ashadha
    20: GanaType.MANUSHYA,  # Uttara Ashadha
    21: GanaType.DEVA,      # Shravana
    22: GanaType.RAKSHASA,  # Dhanishta
    23: GanaType.RAKSHASA,  # Shatabhisha
    24: GanaType.MANUSHYA,  # Purva Bhadrapada
    25: GanaType.MANUSHYA,  # Uttara Bhadrapada
    26: GanaType.DEVA,      # Revati
}

# Canonical Nakshatra Nadi Mapping (BPHS Ch. 81 & Muhurta Chintamani)
NAKSHATRA_NADI: Dict[int, NadiType] = {
    0: NadiType.ADI, 5: NadiType.ADI, 6: NadiType.ADI, 11: NadiType.ADI,
    12: NadiType.ADI, 17: NadiType.ADI, 18: NadiType.ADI, 23: NadiType.ADI, 24: NadiType.ADI,

    1: NadiType.MADHYA, 4: NadiType.MADHYA, 7: NadiType.MADHYA, 10: NadiType.MADHYA,
    13: NadiType.MADHYA, 16: NadiType.MADHYA, 19: NadiType.MADHYA, 22: NadiType.MADHYA, 25: NadiType.MADHYA,

    2: NadiType.ANTYA, 3: NadiType.ANTYA, 8: NadiType.ANTYA, 9: NadiType.ANTYA,
    14: NadiType.ANTYA, 15: NadiType.ANTYA, 20: NadiType.ANTYA, 21: NadiType.ANTYA, 26: NadiType.ANTYA,
}

# Canonical 5 Rajju (Pancha Rajju) Classification (Kalaprakasika Ch. 12)
NAKSHATRA_RAJJU: Dict[int, RajjuType] = {
    # Shiro Rajju (Head / Sirasu) - 3 stars
    4: RajjuType.SHIRO, 13: RajjuType.SHIRO, 22: RajjuType.SHIRO,
    # Kantha Rajju (Neck / Kazhuthu) - 6 stars
    3: RajjuType.KANTHA, 5: RajjuType.KANTHA, 12: RajjuType.KANTHA,
    14: RajjuType.KANTHA, 21: RajjuType.KANTHA, 23: RajjuType.KANTHA,
    # Udara Rajju (Stomach / Vayiru) - 6 stars
    2: RajjuType.UDARA, 6: RajjuType.UDARA, 11: RajjuType.UDARA,
    15: RajjuType.UDARA, 20: RajjuType.UDARA, 24: RajjuType.UDARA,
    # Kati Rajju (Hip / Idai) - 6 stars
    1: RajjuType.KATI, 7: RajjuType.KATI, 10: RajjuType.KATI,
    16: RajjuType.KATI, 19: RajjuType.KATI, 25: RajjuType.KATI,
    # Pada Rajju (Foot / Padam) - 6 stars
    0: RajjuType.PADA, 8: RajjuType.PADA, 9: RajjuType.PADA,
    17: RajjuType.PADA, 18: RajjuType.PADA, 26: RajjuType.PADA,
}

# 14 Yoni Animals (index 0 to 26 mapped to animal string)
NAKSHATRA_YONI_ANIMAL: Dict[int, str] = {
    0: "Horse", 1: "Elephant", 2: "Sheep", 3: "Serpent", 4: "Serpent",
    5: "Dog", 6: "Cat", 7: "Sheep", 8: "Cat", 9: "Rat",
    10: "Rat", 11: "Cow", 12: "Buffalo", 13: "Tiger", 14: "Buffalo",
    15: "Tiger", 16: "Deer", 17: "Deer", 18: "Dog", 19: "Monkey",
    20: "Mongoose", 21: "Monkey", 22: "Lion", 23: "Horse", 24: "Lion",
    25: "Cow", 26: "Elephant"
}

# 7 Classical Sworn Inimical Yoni Pairs (0 Points)
YONI_BITTER_ENEMIES: Set[Tuple[str, str]] = {
    ("Horse", "Buffalo"), ("Buffalo", "Horse"),
    ("Elephant", "Lion"), ("Lion", "Elephant"),
    ("Sheep", "Monkey"), ("Monkey", "Sheep"),
    ("Serpent", "Mongoose"), ("Mongoose", "Serpent"),
    ("Dog", "Deer"), ("Deer", "Dog"),
    ("Cat", "Rat"), ("Rat", "Cat"),
    ("Cow", "Tiger"), ("Tiger", "Cow"),
}

# 12 Mutually Repulsive Vedha Star Pairs (0-indexed)
VEDHA_PAIRS: Set[Tuple[int, int]] = {
    (0, 17), (17, 0),   # Ashwini <-> Jyeshtha
    (1, 16), (16, 1),   # Bharani <-> Anuradha
    (2, 15), (15, 2),   # Krittika <-> Vishakha
    (3, 14), (14, 3),   # Rohini <-> Swati
    (5, 21), (21, 5),   # Ardra <-> Shravana
    (6, 20), (20, 6),   # Punarvasu <-> Uttarashadha
    (7, 19), (19, 7),   # Pushya <-> Purvashadha
    (8, 18), (18, 8),   # Ashlesha <-> Mula
    (9, 26), (26, 9),   # Magha <-> Revati
    (10, 25), (25, 10), # Purva Phalguni <-> Uttara Bhadrapada
    (11, 24), (24, 11), # Uttara Phalguni <-> Purva Bhadrapada
    (12, 23), (23, 12), # Hasta <-> Shatabhisha
    # Mutual Vedha among the 3 Mars stars
    (4, 13), (13, 4),   # Mrigashira <-> Chitra
    (13, 22), (22, 13), # Chitra <-> Dhanishta
    (4, 22), (22, 4),   # Mrigashira <-> Dhanishta
}

# Sign Vashya Categories
SIGN_VASHYA_CATEGORY: Dict[int, VashyaCategory] = {
    1: VashyaCategory.CHATUSHPADA,  # Aries
    2: VashyaCategory.CHATUSHPADA,  # Taurus
    3: VashyaCategory.DWIPADA,      # Gemini
    4: VashyaCategory.JALACHARA,    # Cancer
    5: VashyaCategory.VANACHARA,    # Leo
    6: VashyaCategory.DWIPADA,      # Virgo
    7: VashyaCategory.DWIPADA,      # Libra
    8: VashyaCategory.KEETA,        # Scorpio
    9: VashyaCategory.DWIPADA,      # Sagittarius (1st half Dwipada dominant)
    10: VashyaCategory.CHATUSHPADA, # Capricorn (1st half Chatushpada dominant)
    11: VashyaCategory.DWIPADA,     # Aquarius
    12: VashyaCategory.JALACHARA,   # Pisces
}

# Parashari Aspects
PARASHARI_ASPECT_OFFSETS: Dict[str, Set[int]] = {
    "Sun": {7},
    "Moon": {7},
    "Mercury": {7},
    "Venus": {7},
    "Mars": {4, 7, 8},
    "Jupiter": {5, 7, 9},
    "Saturn": {3, 7, 10},
    "Rahu": {5, 7, 9},
    "Ketu": {5, 7, 9},
}

# Classical Combustion Orbs (degrees from Sun)
COMBUSTION_ORBS: Dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Mercury_Retro": 12.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Venus_Retro": 8.0,
    "Saturn": 15.0,
}

# Natural Planetary Relationships (Brihat Parashara Hora Shastra Ch. 15)
# 1 = Friend, 0 = Neutral, -1 = Enemy
PLANETARY_NATURAL_FRIENDSHIP: Dict[str, Dict[str, int]] = {
    "Sun": {"Sun": 1, "Moon": 1, "Mars": 1, "Jupiter": 1, "Mercury": 0, "Venus": -1, "Saturn": -1},
    "Moon": {"Sun": 1, "Moon": 1, "Mercury": 1, "Mars": 0, "Jupiter": 0, "Venus": 0, "Saturn": 0},
    "Mars": {"Sun": 1, "Moon": 1, "Mars": 1, "Jupiter": 1, "Venus": 0, "Saturn": 0, "Mercury": -1},
    "Mercury": {"Sun": 1, "Mercury": 1, "Venus": 1, "Mars": 0, "Jupiter": 0, "Saturn": 0, "Moon": -1},
    "Jupiter": {"Sun": 1, "Moon": 1, "Mars": 1, "Jupiter": 1, "Saturn": 0, "Mercury": -1, "Venus": -1},
    "Venus": {"Mercury": 1, "Saturn": 1, "Venus": 1, "Mars": 0, "Jupiter": 0, "Sun": -1, "Moon": -1},
    "Saturn": {"Mercury": 1, "Venus": 1, "Saturn": 1, "Jupiter": 0, "Sun": -1, "Moon": -1, "Mars": -1},
}

# Classical Exaltation Signs (BPHS Ch. 3)
EXALTATION_SIGNS: Dict[str, int] = {
    "Sun": 1,       # Aries
    "Moon": 2,      # Taurus
    "Mars": 10,     # Capricorn
    "Mercury": 6,   # Virgo
    "Jupiter": 4,   # Cancer
    "Venus": 12,    # Pisces
    "Saturn": 7,    # Libra
    "Rahu": 2,      # Taurus
    "Ketu": 8,      # Scorpio
}

# Classical Debilitation Signs (BPHS Ch. 3)
DEBILITATION_SIGNS: Dict[str, int] = {
    "Sun": 7,       # Libra
    "Moon": 8,      # Scorpio
    "Mars": 4,      # Cancer
    "Mercury": 12,  # Pisces
    "Jupiter": 10,  # Capricorn
    "Venus": 6,     # Virgo
    "Saturn": 1,    # Aries
    "Rahu": 8,      # Scorpio
    "Ketu": 2,      # Taurus
}

# Classical Own Signs (Swakshetra)
OWN_SIGNS: Dict[str, Set[int]] = {
    "Sun": {5},
    "Moon": {4},
    "Mars": {1, 8},
    "Mercury": {3, 6},
    "Jupiter": {9, 12},
    "Venus": {2, 7},
    "Saturn": {10, 11},
    "Rahu": {11},   # Aquarius co-ruler in standard Parashari
    "Ketu": {8},    # Scorpio co-ruler in standard Parashari
}

# Classical Moolatrikona Signs (BPHS Ch. 3)
MOOLATRIKONA_SIGNS: Dict[str, int] = {
    "Sun": 5,       # Leo
    "Moon": 2,      # Taurus
    "Mars": 1,      # Aries
    "Mercury": 6,   # Virgo
    "Jupiter": 9,   # Sagittarius
    "Venus": 7,     # Libra
    "Saturn": 11,   # Aquarius
}

NATURAL_BENEFICS: Set[str] = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS: Set[str] = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Parashari Functional Benefics, Malefics, and Yogakarakas by Lagna (BPHS Ch. 34)
LAGNA_PLANETARY_NATURE: Dict[str, Dict[str, Any]] = {
    "aries": {
        "yogakaraka": None,
        "benefics": {"Sun", "Jupiter", "Mars"},
        "malefics": {"Mercury", "Saturn", "Venus"},
        "neutral": {"Moon"},
    },
    "taurus": {
        "yogakaraka": "Saturn",  # 9th (Trikona) & 10th (Kendra)
        "benefics": {"Saturn", "Mercury", "Sun"},
        "malefics": {"Jupiter", "Mars", "Venus"},
        "neutral": {"Moon"},
    },
    "gemini": {
        "yogakaraka": None,
        "benefics": {"Venus", "Mercury"},
        "malefics": {"Mars", "Jupiter", "Sun"},
        "neutral": {"Moon", "Saturn"},
    },
    "cancer": {
        "yogakaraka": "Mars",  # 5th (Trikona) & 10th (Kendra)
        "benefics": {"Mars", "Moon", "Jupiter"},
        "malefics": {"Mercury", "Venus", "Saturn"},
        "neutral": {"Sun"},
    },
    "leo": {
        "yogakaraka": "Mars",  # 4th (Kendra) & 9th (Trikona)
        "benefics": {"Mars", "Sun", "Jupiter"},
        "malefics": {"Saturn", "Venus", "Mercury"},
        "neutral": {"Moon"},
    },
    "virgo": {
        "yogakaraka": None,
        "benefics": {"Venus", "Mercury"},
        "malefics": {"Mars", "Jupiter", "Moon"},
        "neutral": {"Sun", "Saturn"},
    },
    "libra": {
        "yogakaraka": "Saturn",  # 4th (Kendra) & 5th (Trikona)
        "benefics": {"Saturn", "Mercury", "Venus"},
        "malefics": {"Jupiter", "Sun", "Mars"},
        "neutral": {"Moon"},
    },
    "scorpio": {
        "yogakaraka": None,
        "benefics": {"Sun", "Moon", "Jupiter", "Mars"},
        "malefics": {"Mercury", "Venus"},
        "neutral": {"Saturn"},
    },
    "sagittarius": {
        "yogakaraka": None,
        "benefics": {"Sun", "Mars", "Jupiter"},
        "malefics": {"Venus", "Saturn"},
        "neutral": {"Moon", "Mercury"},
    },
    "capricorn": {
        "yogakaraka": "Venus",  # 5th (Trikona) & 10th (Kendra)
        "benefics": {"Venus", "Mercury", "Saturn"},
        "malefics": {"Mars", "Jupiter", "Moon"},
        "neutral": {"Sun"},
    },
    "aquarius": {
        "yogakaraka": "Venus",  # 4th (Kendra) & 9th (Trikona)
        "benefics": {"Venus", "Saturn"},
        "malefics": {"Jupiter", "Moon", "Mars"},
        "neutral": {"Sun", "Mercury"},
    },
    "pisces": {
        "yogakaraka": None,
        "benefics": {"Moon", "Mars", "Jupiter"},
        "malefics": {"Venus", "Sun", "Saturn"},
        "neutral": {"Mercury"},
    },
}

# Classical Tamil Vasya Map (Kalaprakasika Ch. 12 Slokas 26-28)
# Rasi Index (1-12) mapped to list of attracted Rasi indices (1-12)
TAMIL_VASYA_MAP: Dict[int, List[int]] = {
    1: [5, 8],     # Aries -> Leo, Scorpio
    2: [4, 7],     # Taurus -> Cancer, Libra
    3: [6],        # Gemini -> Virgo
    4: [8, 9],     # Cancer -> Scorpio, Sagittarius
    5: [7],        # Leo -> Libra
    6: [12, 3],    # Virgo -> Pisces, Gemini
    7: [10, 6],    # Libra -> Capricorn, Virgo
    8: [4],        # Scorpio -> Cancer
    9: [12],       # Sagittarius -> Pisces
    10: [1, 11],   # Capricorn -> Aries, Aquarius
    11: [1],       # Aquarius -> Aries
    12: [10],      # Pisces -> Capricorn
}

# Auspicious Eka Nakshatras (Kalaprakasika Ch. 12 Sloka 4) - permitted for same star matching (0-indexed)
EKA_NAKSHATRA_AUSPICIOUS: Set[int] = {
    3,   # Rohini
    5,   # Ardra
    9,   # Magha
    12,  # Hasta
    15,  # Vishakha
    21,  # Shravana
    25,  # Uttara Bhadrapada
    26,  # Revati
}

# ---------------------------------------------------------------------------
# North Indian Ashtakoota Reference Tables
# ---------------------------------------------------------------------------

SIGN_VARNA: Dict[int, str] = {
    1: "Kshatriya",  # Aries
    2: "Vaishya",    # Taurus
    3: "Shudra",     # Gemini
    4: "Brahmin",    # Cancer
    5: "Kshatriya",  # Leo
    6: "Vaishya",    # Virgo
    7: "Shudra",     # Libra
    8: "Brahmin",    # Scorpio
    9: "Kshatriya",  # Sagittarius
    10: "Vaishya",   # Capricorn
    11: "Shudra",    # Aquarius
    12: "Brahmin",   # Pisces
}

VARNA_RANKS: Dict[str, int] = {
    "Brahmin": 4,
    "Kshatriya": 3,
    "Vaishya": 2,
    "Shudra": 1,
}

_YONI_PAIRS_3_PTS: Set[Tuple[str, str]] = {
    ("Horse", "Elephant"), ("Elephant", "Horse"),
    ("Horse", "Deer"), ("Deer", "Horse"),
    ("Horse", "Monkey"), ("Monkey", "Horse"),
    ("Elephant", "Sheep"), ("Sheep", "Elephant"),
    ("Elephant", "Cow"), ("Cow", "Elephant"),
    ("Sheep", "Cow"), ("Cow", "Sheep"),
    ("Serpent", "Cat"), ("Cat", "Serpent"),
    ("Serpent", "Rat"), ("Rat", "Serpent"),
    ("Dog", "Cat"), ("Cat", "Dog"),
    ("Dog", "Monkey"), ("Monkey", "Dog"),
    ("Cat", "Deer"), ("Deer", "Cat"),
    ("Cat", "Monkey"), ("Monkey", "Cat"),
    ("Cat", "Mongoose"), ("Mongoose", "Cat"),
    ("Rat", "Monkey"), ("Monkey", "Rat"),
    ("Cow", "Buffalo"), ("Buffalo", "Cow"),
    ("Buffalo", "Deer"), ("Deer", "Buffalo"),
    ("Tiger", "Lion"), ("Lion", "Tiger"),
    ("Tiger", "Dog"), ("Dog", "Tiger"),
    ("Monkey", "Mongoose"), ("Mongoose", "Monkey"),
    ("Lion", "Dog"), ("Dog", "Lion"),
}

_YONI_PAIRS_1_PT: Set[Tuple[str, str]] = {
    ("Tiger", "Horse"), ("Horse", "Tiger"),
    ("Tiger", "Elephant"), ("Elephant", "Tiger"),
    ("Tiger", "Sheep"), ("Sheep", "Tiger"),
    ("Tiger", "Serpent"), ("Serpent", "Tiger"),
    ("Tiger", "Cat"), ("Cat", "Tiger"),
    ("Tiger", "Rat"), ("Rat", "Tiger"),
    ("Tiger", "Buffalo"), ("Buffalo", "Tiger"),
    ("Tiger", "Deer"), ("Deer", "Tiger"),
    ("Tiger", "Monkey"), ("Monkey", "Tiger"),
    ("Tiger", "Mongoose"), ("Mongoose", "Tiger"),
    ("Lion", "Horse"), ("Horse", "Lion"),
    ("Lion", "Sheep"), ("Sheep", "Lion"),
    ("Lion", "Serpent"), ("Serpent", "Lion"),
    ("Lion", "Cat"), ("Cat", "Lion"),
    ("Lion", "Rat"), ("Rat", "Lion"),
    ("Lion", "Cow"), ("Cow", "Lion"),
    ("Lion", "Buffalo"), ("Buffalo", "Lion"),
    ("Lion", "Deer"), ("Deer", "Lion"),
    ("Lion", "Monkey"), ("Monkey", "Lion"),
    ("Lion", "Mongoose"), ("Mongoose", "Lion"),
    ("Dog", "Elephant"), ("Elephant", "Dog"),
    ("Dog", "Sheep"), ("Sheep", "Dog"),
    ("Dog", "Cow"), ("Cow", "Dog"),
    ("Dog", "Buffalo"), ("Buffalo", "Dog"),
    ("Serpent", "Horse"), ("Horse", "Serpent"),
    ("Serpent", "Elephant"), ("Elephant", "Serpent"),
    ("Serpent", "Cow"), ("Cow", "Serpent"),
    ("Serpent", "Buffalo"), ("Buffalo", "Serpent"),
}

def get_yoni_koota_points(animal_a: str, animal_b: str) -> float:
    """Return points (0 to 4) for Yoni Koota between two animal archetypes."""
    if animal_a == animal_b:
        return 4.0
    if (animal_a, animal_b) in YONI_BITTER_ENEMIES or (animal_b, animal_a) in YONI_BITTER_ENEMIES:
        return 0.0
    if (animal_a, animal_b) in _YONI_PAIRS_3_PTS or (animal_b, animal_a) in _YONI_PAIRS_3_PTS:
        return 3.0
    if (animal_a, animal_b) in _YONI_PAIRS_1_PT or (animal_b, animal_a) in _YONI_PAIRS_1_PT:
        return 1.0
    return 2.0


# ---------------------------------------------------------------------------
# Internal Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PoruthamResult:
    """Standardized deterministic output contract for an individual Tamil Porutham."""
    rule_id: str
    name_en: str
    name_ta: str
    status: PoruthamStatus
    groom_input: Dict[str, Any]
    bride_input: Dict[str, Any]
    intermediate_calculation: Dict[str, Any]
    counting_direction: str
    applied_acceptance_criteria: str
    source_and_version: str
    explanation_en: str
    explanation_ta: str
    warnings: List[str] = field(default_factory=list)
    grade: Optional[PoruthamGrade] = None
    score: float = 0.0
    max_score: float = 1.0
    is_favorable: bool = False


@dataclass
class KootaResult:
    """Standardized deterministic output contract for an individual Ashtakoota factor."""
    koota_id: str
    name_en: str
    status: PoruthamStatus
    max_points: float
    earned_points: float
    raw_calculation: str
    groom_input: Dict[str, Any]
    bride_input: Dict[str, Any]
    intermediate_calculation: Dict[str, Any]
    description: str = ""
    classical_reference: str = ""
    is_dosha_present: bool = False
    is_cancelled: bool = False
    cancellation_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class MarriagePlanet:
    """Internal normalized representation of a celestial body for marriage analysis."""
    name: str
    body_id: int
    longitude: float               # 0.0 to 360.0
    sign_index: int                # 1 to 12
    sign_name: str
    sign_name_tamil: str
    degree_in_sign: float          # 0.0 to 30.0
    house: int                     # 1 to 12 from Lagna
    speed_deg_per_day: float = 1.0
    is_retrograde: bool = False
    is_combust: bool = False
    nakshatra_index: int = 0       # 0 to 26
    nakshatra_name: str = ""
    nakshatra_pada: int = 1        # 1 to 4
    navamsa_sign_index: int = 1    # 1 to 12 in D9


@dataclass
class MarriageHouse:
    """Internal normalized representation of a house cusp."""
    house_number: int              # 1 to 12
    sign_index: int                # 1 to 12
    sign_name: str
    sign_name_tamil: str
    cusp_degree: float             # 0.0 to 360.0
    degree_in_sign: float          # 0.0 to 30.0
    lord_name: str
    star_lord: str = ""
    sub_lord: str = ""
    occupants: List[str] = field(default_factory=list)


@dataclass
class MarriageChartContext:
    """Encapsulates a fully resolved horoscope context for marriage synastry."""
    person_id: str
    person_name: str
    gender: Gender
    birth_date_iso: str
    birth_time_iso: str
    timezone: str
    latitude: float
    longitude: float

    # Ascendant (Lagna)
    ascendant_degree: float
    ascendant_sign_idx: int
    ascendant_sign_name: str
    ascendant_sign_name_tamil: str
    ascendant_nakshatra_idx: int
    ascendant_nakshatra_name: str
    ascendant_nakshatra_pada: int
    ascendant_navamsa_sign_idx: int

    # Moon (Chandra)
    moon_degree: float
    moon_sign_idx: int
    moon_sign_name: str
    moon_sign_name_tamil: str
    moon_nakshatra_idx: int
    moon_nakshatra_name: str
    moon_nakshatra_pada: int
    moon_navamsa_sign_idx: int

    # Planets and Houses
    grahas: Dict[str, MarriagePlanet] = field(default_factory=dict)
    houses: Dict[int, MarriageHouse] = field(default_factory=dict)

    # Convenience shortcuts
    @property
    def sun(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Sun")

    @property
    def moon(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Moon")

    @property
    def mars(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Mars")

    @property
    def mercury(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Mercury")

    @property
    def jupiter(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Jupiter")

    @property
    def venus(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Venus")

    @property
    def saturn(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Saturn")

    @property
    def rahu(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Rahu")

    @property
    def ketu(self) -> Optional[MarriagePlanet]:
        return self.grahas.get("Ketu")

    def house_from(self, target_planet_or_sign: Any, reference_sign_idx: int) -> int:
        """Compute relative house number (1 to 12) from reference sign index."""
        if isinstance(target_planet_or_sign, str):
            planet = self.grahas.get(target_planet_or_sign)
            if not planet:
                return 1
            target_sign = planet.sign_index
        elif isinstance(target_planet_or_sign, int):
            target_sign = target_planet_or_sign
        else:
            return 1
        return ((target_sign - reference_sign_idx) % 12) + 1

    def get_house_lord(self, house_num: int) -> str:
        """Return ruling graha name of the specified house number."""
        h = self.houses.get(house_num)
        if h:
            return h.lord_name
        sign = ((self.ascendant_sign_idx + house_num - 2) % 12) + 1
        return SIGN_LORDS.get(sign, "Unknown")

    def get_planets_in_house(self, house_num: int) -> List[str]:
        """Return list of planet names occupying the given house."""
        return [p.name for p in self.grahas.values() if p.house == house_num]

    def is_conjoined(self, planet_a: str, planet_b: str, max_orb: float = 12.0) -> bool:
        """Check if two grahas are conjoined in the same sign within the orb."""
        pa = self.grahas.get(planet_a)
        pb = self.grahas.get(planet_b)
        if not pa or not pb:
            return False
        if pa.sign_index != pb.sign_index:
            return False
        sep = abs(pa.degree_in_sign - pb.degree_in_sign)
        return sep <= max_orb

    def has_aspect_on_graha(self, aspecting: str, target: str) -> bool:
        """Evaluate classical Parashari aspect from aspecting graha to target graha."""
        pa = self.grahas.get(aspecting)
        pt = self.grahas.get(target)
        if not pa or not pt or pa.sign_index == pt.sign_index:
            return False
        diff = ((pt.sign_index - pa.sign_index) % 12) + 1
        valid_offsets = PARASHARI_ASPECT_OFFSETS.get(aspecting, {7})
        return diff in valid_offsets

    def has_aspect_on_house(self, aspecting: str, house_num: int) -> bool:
        """Evaluate classical Parashari aspect from aspecting graha to a specific house (1 to 12)."""
        pa = self.grahas.get(aspecting)
        if not pa:
            return False
        diff = ((house_num - pa.house) % 12) + 1
        valid_offsets = PARASHARI_ASPECT_OFFSETS.get(aspecting, {7})
        return diff in valid_offsets


# ---------------------------------------------------------------------------
# Phase 4: Comprehensive Vedic Marriage Analysis Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class VedicHouseFinding:
    """Detailed Vedic analysis of an individual marriage-related house (2, 4, 5, 7, 8, 12)."""
    house_number: int
    house_name_en: str
    house_name_ta: str
    sign_index: int
    sign_name_en: str
    sign_name_ta: str
    cusp_degree: float
    lord_name: str
    lord_house: int
    lord_sign_index: int
    lord_sign_name: str
    lord_dignity: str
    occupants: List[str] = field(default_factory=list)
    aspecting_planets: List[str] = field(default_factory=list)
    supporting_influences: List[str] = field(default_factory=list)
    conflicting_influences: List[str] = field(default_factory=list)
    status: PoruthamStatus = PoruthamStatus.PASS
    summary_en: str = ""
    summary_ta: str = ""


@dataclass
class VedicSignificatorFinding:
    """Detailed Vedic analysis of an individual marriage significator (Karaka)."""
    planet_name: str
    sign_index: int
    sign_name: str
    house: int
    longitude: float
    natural_nature: str
    functional_nature: str
    dignity: str
    is_retrograde: bool
    is_combust: bool
    d9_sign_index: int
    d9_sign_name: str
    is_vargottama: bool
    is_pushkara_navamsa: bool
    conjunctions: List[str] = field(default_factory=list)
    aspects_received: List[str] = field(default_factory=list)
    shadbala_ratio: Optional[float] = None
    shadbala_strength: Optional[str] = None
    summary_en: str = ""
    summary_ta: str = ""


@dataclass
class NavamsaCrossFinding:
    """Detailed D1 and D9 Navamsa cross-validation analysis."""
    d9_lagna_sign_index: int
    d9_lagna_sign_name: str
    d9_lagna_lord: str
    d9_7th_sign_index: int
    d9_7th_sign_name: str
    d9_7th_lord: str
    d1_7th_lord_in_d9_sign: str
    d1_7th_lord_in_d9_house: int
    d1_7th_lord_in_d9_dignity: str
    d9_7th_lord_in_d1_sign: str
    d9_7th_lord_in_d1_house: int
    d9_7th_lord_in_d1_dignity: str
    venus_in_d9_sign: str
    venus_in_d9_house: int
    venus_in_d9_dignity: str
    jupiter_in_d9_sign: str
    jupiter_in_d9_house: int
    jupiter_in_d9_dignity: str
    navamsa_boundary_risk: bool
    boundary_distance_arcmin: float
    vargottama_planets: List[str] = field(default_factory=list)
    pushkara_navamsa_planets: List[str] = field(default_factory=list)
    synthesis_notes: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""


@dataclass
class IndividualKujaAssessment:
    """Explanation-ready individual Kuja / Manglik Dosha evaluation for one partner."""
    subject_role: str  # 'groom' or 'bride'
    is_present: bool
    is_cancelled: bool
    severity: str  # 'None', 'Cancelled', 'Mild', 'Moderate', 'High'
    house_convention: str
    mars_longitude: float
    mars_sign_index: int
    mars_sign_name: str
    mars_degree_in_sign: float
    mars_house_from_lagna: int
    mars_house_from_moon: int
    mars_house_from_venus: int
    effective_intensity_percent: float
    references_evaluated: Dict[str, Any] = field(default_factory=dict)
    triggering_conditions: List[str] = field(default_factory=list)
    cancellations_checked: List[str] = field(default_factory=list)
    cancellations_applied: List[str] = field(default_factory=list)
    source_and_version: str = "BPHS Ch. 81, Muhurta Chintamani, Brihat Samhita (v1.0)"
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class IndividualVedicAnalysis:
    """Complete individual Vedic marriage analysis for one individual (Groom or Bride)."""
    subject_role: str  # 'groom' or 'bride'
    person_name: str
    gender: str
    lagna_sign_index: int
    lagna_sign_name: str
    lagna_sign_name_tamil: str
    lagna_degree: float
    lagna_lord: str
    lagna_lord_house: int
    lagna_lord_dignity: str
    houses_analysis: Dict[int, VedicHouseFinding] = field(default_factory=dict)
    significators: Dict[str, VedicSignificatorFinding] = field(default_factory=dict)
    navamsa_cross_analysis: Optional[NavamsaCrossFinding] = None
    kuja_dosha: Optional[IndividualKujaAssessment] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    supporting_indicators: List[str] = field(default_factory=list)
    conflicting_indicators: List[str] = field(default_factory=list)
    uncertainty_warnings: List[str] = field(default_factory=list)
    rule_sources: List[str] = field(default_factory=list)
    summary_en: str = ""
    summary_ta: str = ""


@dataclass
class DualVedicAnalysis:
    """Pair-wise Vedic marriage analysis combining independent evaluations without composite scoring."""
    groom_analysis: IndividualVedicAnalysis
    bride_analysis: IndividualVedicAnalysis
    d9_cross_check_summary: str = ""
    venus_jupiter_resonance: str = ""
    key_observations: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 5: Mutual Doshas, Kuja Samadosham & Papasamya Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PapasamyaResult:
    """South Indian Papasamya malefic point allocations and breakdown."""
    subject_role: str
    lagna_papam: float
    moon_papam: float
    venus_papam: float
    total_papam: float
    breakdown_by_planet: Dict[str, float] = field(default_factory=dict)
    placements_detail: List[Dict[str, Any]] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""


@dataclass
class MutualKujaResult:
    """Mutual Kuja Dosha (Samadosham) analysis outcome and evidence."""
    status: SamadoshamOutcome
    mutual_balance: str  # 'BALANCED', 'GROOM_EXCESS', 'BRIDE_EXCESS', or 'NEITHER_AFFLICTED'
    groom_severity: str
    bride_severity: str
    groom_effective_intensity: float
    bride_effective_intensity: float
    triggering_comparison: Dict[str, Any] = field(default_factory=dict)
    cancellations_or_mitigations_applied: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class MutualDoshaAnalysisResult:
    """Complete mutual dosha analysis combining Kuja Samadosham, Papasamya, and partner-dependent doshas."""
    groom_kuja: Any  # KujaDoshaResult or IndividualKujaAssessment
    bride_kuja: Any
    samadosham: MutualKujaResult
    groom_papasamya: PapasamyaResult
    bride_papasamya: PapasamyaResult
    papasamya_verdict: PapasamyaVerdict
    papasamya_diff_percent: float
    papasamya_explanation_en: str
    papasamya_explanation_ta: str
    partner_dependent_doshas: Dict[str, Any] = field(default_factory=dict)
    active_doshas_with_exceptions: List[Dict[str, Any]] = field(default_factory=list)
    independent_vetoes_preserved: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 6: Bidirectional Vedic Synastry Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MoonToMoonFinding:
    """Bidirectional Moon-to-Moon cross-chart analysis between groom and bride.

    Evaluates Moon sign relationships, Nakshatra relationships, Moon sign lord
    relationships, and Pada resonance without recalculating Porutham or Ashtakoota.
    """
    groom_moon_sign_idx: int
    groom_moon_sign_name: str
    groom_moon_nakshatra_idx: int
    groom_moon_nakshatra_name: str
    groom_moon_nakshatra_pada: int
    groom_moon_lord: str

    bride_moon_sign_idx: int
    bride_moon_sign_name: str
    bride_moon_nakshatra_idx: int
    bride_moon_nakshatra_name: str
    bride_moon_nakshatra_pada: int
    bride_moon_lord: str

    # Moon sign relationship
    sign_distance_g_to_b: int          # house of bride Moon from groom Moon (1–12)
    sign_distance_b_to_g: int          # house of groom Moon from bride Moon (1–12)
    sign_relationship: str             # "Samasaptaka", "Trine", "Upachaya", "Inimical", etc.
    sign_assessment: str               # "Favorable", "Neutral", "Unfavorable"

    # Nakshatra relationship
    same_nakshatra: bool
    nakshatra_distance_g_to_b: int     # 1 to 27 inclusive
    nakshatra_distance_b_to_g: int     # 1 to 27 inclusive
    pada_resonance: str                # "Same", "Complementary", "Neutral"

    # Moon lord relationship
    moon_lord_relationship: str        # "Friends", "Neutrals", "Enemies", "Same"
    moon_lord_friendship_score: float  # 1.0=friends, 0.5=neutral, 0.0=enemies

    # Cross-chart Parashari aspects
    groom_moon_aspects_bride_moon: bool
    bride_moon_aspects_groom_moon: bool

    # Boundary sensitivity
    groom_navamsa_boundary_risk: bool
    bride_navamsa_boundary_risk: bool
    groom_boundary_arcmin: float
    bride_boundary_arcmin: float

    # Notes and explanations
    observations: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class LagnaToLagnaFinding:
    """Bidirectional Lagna (Ascendant) cross-chart analysis between groom and bride.

    Evaluates ascendant sign relationships, Lagna lord relationships,
    cross-chart house positions, and boundary sensitivity.

    Source: BPHS Ch. 9, 15; Phaladeepika Ch. 2.
    Note: Sign compatibility indicates structural resonance, not personality guarantee.
    """
    groom_lagna_sign_idx: int
    groom_lagna_sign_name: str
    groom_lagna_degree: float
    groom_lagna_lord: str
    groom_lagna_lord_sign_idx: int
    groom_lagna_lord_dignity: str

    bride_lagna_sign_idx: int
    bride_lagna_sign_name: str
    bride_lagna_degree: float
    bride_lagna_lord: str
    bride_lagna_lord_sign_idx: int
    bride_lagna_lord_dignity: str

    # Lagna sign relationship
    lagna_sign_distance_g_to_b: int    # House of bride Lagna from groom Lagna (1–12)
    lagna_sign_distance_b_to_g: int    # House of groom Lagna from bride Lagna (1–12)
    lagna_relationship: str            # "Samasaptaka", "Trine", "Kendra", "Inimical", etc.
    lagna_sign_assessment: str         # "Supportive", "Neutral", "Challenging"

    # Lagna lord relationship
    lagna_lord_relationship: str       # "Friends", "Neutrals", "Enemies", "Same"
    lagna_lord_friendship_score: float # 1.0=friends, 0.5=neutral, 0.0=enemies

    # Cross-chart house analysis
    groom_lagna_in_bride_chart_house: int  # Groom's Lagna sign as house in bride's chart
    bride_lagna_in_groom_chart_house: int  # Bride's Lagna sign as house in groom's chart

    # Cross-chart Parashari aspects between Lagna lords
    groom_lord_aspects_bride_lagna: bool
    bride_lord_aspects_groom_lagna: bool

    # Boundary sensitivity
    groom_lagna_boundary_risk: bool
    bride_lagna_boundary_risk: bool
    groom_lagna_boundary_arcmin: float
    bride_lagna_boundary_arcmin: float

    observations: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class MarriageLordCrossChartFinding:
    """Cross-chart analysis of 7th house lords (primary marriage significators).

    Evaluates how each partner's 7th lord falls in the other's chart,
    and how each partner's 7th lord relates to the other's marriage houses.

    Source: BPHS Ch. 18 (Kalatra Bhava); Phaladeepika Ch. 10.
    """
    # Groom's 7th lord in bride's chart
    groom_7th_lord: str
    groom_7th_lord_sign_idx: int
    groom_7th_lord_in_bride_house: int       # House from bride's Lagna
    groom_7th_lord_in_bride_dignity: str
    groom_7th_lord_aspects_bride_7th: bool
    groom_7th_lord_in_bride_marriage_house: bool  # In bride's 2,5,7,8,12

    # Bride's 7th lord in groom's chart
    bride_7th_lord: str
    bride_7th_lord_sign_idx: int
    bride_7th_lord_in_groom_house: int       # House from groom's Lagna
    bride_7th_lord_in_groom_dignity: str
    bride_7th_lord_aspects_groom_7th: bool
    bride_7th_lord_in_groom_marriage_house: bool  # In groom's 2,5,7,8,12

    # Mutual 7th lord relationship
    seventh_lord_mutual_relationship: str    # "Friends", "Neutrals", "Enemies", "Same"
    seventh_lord_friendship_score: float

    # Cross-chart aspects between 7th lords
    mutual_aspect_between_7th_lords: bool

    observations: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class VenusJupiterCrossChartFinding:
    """Cross-chart analysis of the primary marriage Karakas: Venus and Jupiter.

    For the groom: Venus is the primary Karaka for marriage and wife (Kalatra Karaka).
    For the bride: Jupiter is the primary Karaka for marriage and husband (Pati Karaka).

    Source: BPHS Ch. 32 (Karakatwa); Phaladeepika Ch. 10.
    """
    # Groom's Venus in bride's chart
    groom_venus_sign_idx: int
    groom_venus_sign_name: str
    groom_venus_in_bride_house: int         # House from bride's Lagna
    groom_venus_in_bride_dignity: str
    groom_venus_aspects_bride_7th: bool
    groom_venus_in_bride_marriage_house: bool

    # Bride's Jupiter in groom's chart
    bride_jupiter_sign_idx: int
    bride_jupiter_sign_name: str
    bride_jupiter_in_groom_house: int       # House from groom's Lagna
    bride_jupiter_in_groom_dignity: str
    bride_jupiter_aspects_groom_7th: bool
    bride_jupiter_in_groom_marriage_house: bool

    # Cross-Karaka relationship
    venus_jupiter_relationship: str         # Natural relationship between Venus and Jupiter
    venus_jupiter_friendship_score: float   # Always -0.5 (natural enemies) per BPHS Ch. 15

    # Cross aspects
    groom_venus_aspects_bride_jupiter: bool
    bride_jupiter_aspects_groom_venus: bool

    observations: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class BidirectionalSynastryResult:
    """Complete Phase 6 bidirectional Vedic synastry analysis.

    Aggregates all cross-chart findings without producing a composite compatibility verdict.
    The final verdict is reserved for Phase 7 (Deterministic Final Assessment).
    """
    groom_person_id: str
    bride_person_id: str

    moon_to_moon: MoonToMoonFinding
    lagna_to_lagna: LagnaToLagnaFinding
    marriage_lord_cross: MarriageLordCrossChartFinding
    venus_jupiter_cross: VenusJupiterCrossChartFinding

    # High-level synastry signals (read-only observations, no verdict)
    strong_indicators: List[str] = field(default_factory=list)
    mixed_indicators: List[str] = field(default_factory=list)
    weak_indicators: List[str] = field(default_factory=list)

    # Boundary sensitivity summary across all four dimensions
    has_boundary_sensitivity: bool = False
    boundary_sensitivity_notes: List[str] = field(default_factory=list)

    rule_sources: List[str] = field(default_factory=list)
    analysis_warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 7 — KP Marriage & Timing Adapter Models
# ---------------------------------------------------------------------------

class KpPromiseVerdict(str, Enum):
    """Standardized verdict taxonomy for KP cuspal and timing promises."""
    FAVORABLE = "FAVORABLE"
    MIXED = "MIXED"
    UNFAVORABLE = "UNFAVORABLE"
    INDETERMINATE = "INDETERMINATE"


@dataclass
class KpCslFinding:
    """KP Cuspal Sub-Lord evaluation for marriage promise (primarily 7th CSL).

    Rule reference: KP-MARR-01 (KP Reader II & III, Prof. K.S. Krishnamurti)
    Supporting houses: 2 (addition to family), 7 (spouse/union), 11 (fulfillment/attachment).
    Denying houses: 1 (12th to 2), 6 (12th to 7), 10 (12th to 11).
    """
    person_id: str
    cusp_number: int  # 7 for 7th CSL
    sub_lord: str
    star_lord: str = ""
    sign_lord: str = ""
    sub_sub_lord: Optional[str] = None
    signified_houses: List[int] = field(default_factory=list)
    supporting_houses_signified: List[int] = field(default_factory=list)  # Intersection with {2, 7, 11}
    denying_houses_signified: List[int] = field(default_factory=list)      # Intersection with {1, 6, 10}
    verdict: KpPromiseVerdict = KpPromiseVerdict.INDETERMINATE
    is_valid: bool = True
    explanation_en: str = ""
    explanation_ta: str = ""
    rule_sources: List[str] = field(default_factory=lambda: ["KP-MARR-01"])
    warnings: List[str] = field(default_factory=list)


@dataclass
class KpHouseSignificatorLevelFinding:
    """4-tier KP house significators (Bhaav Nirdeshan).

    Levels per classical KP:
    - Level A: Planets in star of occupants of the house (strongest)
    - Level B: Occupants of the house
    - Level C: Planets in star of house lord
    - Level D: Lord of the house
    """
    house: int
    level_a: List[str] = field(default_factory=list)
    level_b: List[str] = field(default_factory=list)
    level_c: List[str] = field(default_factory=list)
    level_d: List[str] = field(default_factory=list)
    all_significators: List[str] = field(default_factory=list)


@dataclass
class KpSignificatorsFinding:
    """KP 4-tier significators aggregation for key marriage houses.

    Rule reference: KP-MARR-02 (KP Reader II)
    Target houses: 2, 7, 11 (favorable), and 1, 6, 10 (denial).
    """
    person_id: str
    target_house: int  # Usually 7
    significators_by_house: Dict[int, KpHouseSignificatorLevelFinding] = field(default_factory=dict)
    all_marriage_significators: List[str] = field(default_factory=list)    # Signifying 2, 7, or 11
    all_detrimental_significators: List[str] = field(default_factory=list)  # Signifying 1, 6, or 10
    explanation_en: str = ""
    explanation_ta: str = ""
    rule_sources: List[str] = field(default_factory=lambda: ["KP-MARR-02"])
    warnings: List[str] = field(default_factory=list)


@dataclass
class KpRulingPlanetsFinding:
    """KP Ruling Planets (RP) extraction and agreement.

    Rule reference: KP-MARR-03 (KP Reader III)
    Standard RPs:
    - Day Lord
    - Ascendant Sign Lord, Star Lord, Sub Lord
    - Moon Sign Lord, Star Lord, Sub Lord
    """
    person_id: str
    day_lord: str = ""
    ascendant_sign_lord: str = ""
    ascendant_star_lord: str = ""
    ascendant_sub_lord: str = ""
    moon_sign_lord: str = ""
    moon_star_lord: str = ""
    moon_sub_lord: str = ""
    ruling_planets_list: List[str] = field(default_factory=list)
    shared_with_partner: List[str] = field(default_factory=list)
    agreement_score: float = 0.0
    explanation_en: str = ""
    explanation_ta: str = ""
    rule_sources: List[str] = field(default_factory=lambda: ["KP-MARR-03"])
    warnings: List[str] = field(default_factory=list)


@dataclass
class KpDasaBhuktiTimingPeriod:
    """Individual Vimshottari period analyzed for marriage timing fruitfulness."""
    level: str  # "Mahadasha", "Antardasha" / "Bhukti", "Pratyantardasha"
    lord: str
    signified_houses: List[int] = field(default_factory=list)
    supports_marriage: bool = False
    denies_marriage: bool = False
    timing_favorability: str = "NEUTRAL"  # FAVORABLE, MIXED, UNFAVORABLE, NEUTRAL


@dataclass
class KpTimingFinding:
    """KP Vimshottari timing alignment assessment.

    Rule reference: KP-MARR-03 (KP Reader II & III)
    Evaluates current and upcoming Dasa-Bhukti periods for activation of 2, 7, 11.
    """
    person_id: str
    current_mahadasha: Optional[KpDasaBhuktiTimingPeriod] = None
    current_bhukti: Optional[KpDasaBhuktiTimingPeriod] = None
    current_pratyantar: Optional[KpDasaBhuktiTimingPeriod] = None
    upcoming_promising_periods: List[KpDasaBhuktiTimingPeriod] = field(default_factory=list)
    overall_timing_verdict: KpPromiseVerdict = KpPromiseVerdict.INDETERMINATE
    explanation_en: str = ""
    explanation_ta: str = ""
    rule_sources: List[str] = field(default_factory=lambda: ["KP-MARR-03"])
    warnings: List[str] = field(default_factory=list)


@dataclass
class KpIndividualAnalysis:
    """Complete KP marriage evaluation for a single individual."""
    person_id: str
    person_name: str
    gender: Gender
    csl_7th: KpCslFinding
    significators: KpSignificatorsFinding
    ruling_planets: KpRulingPlanetsFinding
    timing: KpTimingFinding
    overall_promise_verdict: KpPromiseVerdict = KpPromiseVerdict.INDETERMINATE
    rule_sources: List[str] = field(default_factory=list)
    disclaimers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class KpMarriageAnalysisResult:
    """Complete read-only KP marriage and timing evaluation for a couple.

    Provides 7th CSL promise, 4-tier significators, RP agreement, and Vimshottari
    timing synchronicity without final composite compatibility verdict (Phase 8).
    """
    groom_analysis: KpIndividualAnalysis
    bride_analysis: KpIndividualAnalysis
    shared_ruling_planets: List[str] = field(default_factory=list)
    ruling_planets_agreement_level: str = "NONE"  # STRONG, MODERATE, LOW, NONE
    timing_synchronicity_notes: List[str] = field(default_factory=list)
    disclaimers: List[str] = field(default_factory=list)
    rule_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 8 — Composite Marriage Compatibility Assessment Models
# ---------------------------------------------------------------------------

class ConflictType(str, Enum):
    """Taxonomy of astrological divergence and conflict types."""
    TRADITIONAL_SYSTEM_DIVERGENCE = "TRADITIONAL_SYSTEM_DIVERGENCE"
    PORUTHAM_VS_VEDIC_INDIVIDUAL = "PORUTHAM_VS_VEDIC_INDIVIDUAL"
    INDIVIDUAL_DOSHA_VS_MUTUAL_MITIGATION = "INDIVIDUAL_DOSHA_VS_MUTUAL_MITIGATION"
    SYNASTRY_POLARITY_CONFLICT = "SYNASTRY_POLARITY_CONFLICT"
    KP_PROMISE_VS_COMPATIBILITY = "KP_PROMISE_VS_COMPATIBILITY"
    BIRTH_TIME_BOUNDARY_SENSITIVITY = "BIRTH_TIME_BOUNDARY_SENSITIVITY"
    MISSING_OR_UNSUPPORTED_DATA = "MISSING_OR_UNSUPPORTED_DATA"


@dataclass
class ConflictFinding:
    """Documented divergence or conflict between traditions, lenses, or chart factors."""
    conflict_type: ConflictType
    title_en: str
    title_ta: str
    finding_a: str
    finding_b: str
    resolution_principle: str
    explanation_en: str
    explanation_ta: str
    rule_sources: List[str] = field(default_factory=list)


@dataclass
class CategoryVerdict:
    """Evaluated verdict for one independent astrological lens or tradition."""
    category_id: str
    category_name_en: str
    category_name_ta: str
    status: str  # "FAVORABLE", "MIXED", "UNFAVORABLE", "INDETERMINATE"
    tradition: str
    score_summary: str = ""
    key_factors: List[str] = field(default_factory=list)
    vetoes_applied: List[str] = field(default_factory=list)


@dataclass
class CompositeMarriageAssessment:
    """Complete Phase 8 composite marriage compatibility assessment.

    Synthesizes:
    1. Tamil 10 Poruthams (original score and status)
    2. North Indian Ashtakoota (original points out of 36)
    3. Groom & Bride individual Vedic marriage analysis (7th house, Karakas, D9)
    4. Mutual Kuja Dosha & South Indian Papasamya analysis
    5. Bidirectional Vedic Synastry (Moon, Lagna, 7th Lords, Karakas)
    6. Read-Only KP 7th CSL promise, 4-tier significators, and Vimshottari timing

    Preserves independent scores, identifies conflicting evidence, and formulates
    deterministic, non-guarantee bilingual conclusions.
    """
    groom_person_id: str
    bride_person_id: str
    groom_name: str = ""
    bride_name: str = ""

    overall_outcome: CompatibilityOutcome = CompatibilityOutcome.INDETERMINATE
    category_verdicts: Dict[str, CategoryVerdict] = field(default_factory=dict)

    # Underlying independent assessments (preserved without alteration)
    tamil_porutham: Optional[Any] = None       # TamilPoruthamSummary
    ashtakoota: Optional[Any] = None           # AshtakootaSummary
    groom_vedic: Optional[Any] = None          # IndividualVedicAnalysis
    bride_vedic: Optional[Any] = None          # IndividualVedicAnalysis
    mutual_doshas: Optional[Any] = None        # MutualDoshaAnalysisResult
    synastry: Optional[Any] = None             # BidirectionalSynastryResult
    kp_marriage: Optional[Any] = None          # KpMarriageAnalysisResult

    # Explainability & Synthesis layers
    major_supportive_indicators: List[str] = field(default_factory=list)
    major_challenging_indicators: List[str] = field(default_factory=list)
    conflicting_findings: List[ConflictFinding] = field(default_factory=list)
    missing_or_uncertain_evidence: List[str] = field(default_factory=list)
    recommended_astrologer_review: List[str] = field(default_factory=list)
    decision_path: List[str] = field(default_factory=list)

    disclaimers: List[str] = field(default_factory=list)
    rule_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    explanation_en: str = ""
    explanation_ta: str = ""





