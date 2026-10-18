"""Classical Ashtakavarga Bindu Contribution Tables per Brihat Parashara Hora Shastra Chapter 66.

Public Domain Sanskrit Astrological Canon.
"""

from typing import Dict, Tuple

# The 7 classical planets for which Bhinnashtakavarga is calculated
PLANETS_7: Tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# The 8 contributors: 7 planets + Ascendant (Lagna)
CONTRIBUTORS_8: Tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Lagna",
)

# Canonical expected total bindus per planet
EXPECTED_TOTALS: Dict[str, int] = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}

# Grand total of Sarvashtakavarga across 12 signs
TOTAL_SAV_BINDUS = 337

# Canonical Contribution Rules: Target Planet -> Contributor -> Beneficial Houses from Contributor's Sign
# BPHS Chapter 66 Verses 2 through 40
ASHTAKAVARGA_CONTRIBUTIONS: Dict[str, Dict[str, Tuple[int, ...]]] = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 10, 11),
        "Mars": (2, 3, 5, 6, 9, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 4, 7, 8, 10, 11, 12),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 5, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
}

# Rashi Gunaka (Sign Multipliers for Shodhya Pinda per BPHS Ch. 69)
# Aries=7, Taurus=10, Gemini=8, Cancer=4, Leo=10, Virgo=5, Libra=7, Scorpio=8, Sagittarius=9, Capricorn=5, Aquarius=11, Pisces=12
RASHI_GUNAKA: Dict[int, int] = {
    1: 7,
    2: 10,
    3: 8,
    4: 4,
    5: 10,
    6: 5,
    7: 7,
    8: 8,
    9: 9,
    10: 5,
    11: 11,
    12: 12,
}

# Graha Gunaka (Planet Multipliers for Shodhya Pinda per BPHS Ch. 69)
GRAHA_GUNAKA: Dict[str, int] = {
    "Sun": 5,
    "Moon": 5,
    "Mars": 8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus": 7,
    "Saturn": 5,
}

# Dual-lordship pairs for Ekadhipatya Shodhana
# (Planet, Sign 1, Sign 2)
DUAL_LORDSHIP_PAIRS = (
    ("Mars", 1, 8),      # Aries, Scorpio
    ("Venus", 2, 7),     # Taurus, Libra
    ("Mercury", 3, 6),   # Gemini, Virgo
    ("Jupiter", 9, 12),  # Sagittarius, Pisces
    ("Saturn", 10, 11),  # Capricorn, Aquarius
)
