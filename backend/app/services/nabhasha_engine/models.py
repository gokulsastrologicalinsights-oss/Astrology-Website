"""Taxonomies, constants, and data models for Nabhasha Yoga detection."""

from typing import Set, Dict, Tuple

# The 7 classical planets forming Nabhasha Yogas per BPHS Ch. 35
# Rahu and Ketu are strictly excluded.
NABHASHA_GRAHAS: Tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# Natural Benefics and Malefics in classical astrology
NATURAL_BENEFICS: Set[str] = {"Moon", "Mercury", "Jupiter", "Venus"}
NATURAL_MALEFICS: Set[str] = {"Sun", "Mars", "Saturn"}

# Sign Modalities (1-indexed: 1=Aries .. 12=Pisces)
CHARA_SIGNS: Set[int] = {1, 4, 7, 10}       # Movable (Aries, Cancer, Libra, Capricorn)
STHIRA_SIGNS: Set[int] = {2, 5, 8, 11}      # Fixed (Taurus, Leo, Scorpio, Aquarius)
DVISVABHAVA_SIGNS: Set[int] = {3, 6, 9, 12} # Dual (Gemini, Virgo, Sagittarius, Pisces)

# House Classifications (1-indexed from Lagna)
KENDRA_HOUSES: Set[int] = {1, 4, 7, 10}
PANAPHARA_HOUSES: Set[int] = {2, 5, 8, 11}
APOKLIMA_HOUSES: Set[int] = {3, 6, 9, 12}
TRIKONA_HOUSES: Set[int] = {1, 5, 9}

# Sankhya Yoga map based on number of distinct occupied signs (1-7)
SANKHYA_YOGAS: Dict[int, Tuple[str, str]] = {
    1: ("Gola", "All 7 planets occupy only a single sign. Bestows focus, solitude, unconventional lifestyle."),
    2: ("Yuga", "All 7 planets occupy two distinct signs. Indicates resourcefulness, duality, struggle followed by stability."),
    3: ("Shula", "All 7 planets occupy three distinct signs. Gives courage, sharp intellect, and assertive spirit."),
    4: ("Kedara", "All 7 planets occupy four distinct signs. Associated with agricultural wealth, patience, and steady prosperity."),
    5: ("Pasha", "All 7 planets occupy five distinct signs. Bestows extensive social ties, skillful management, and commercial acumen."),
    6: ("Damini", "All 7 planets occupy six distinct signs. Endows broad generosity, administrative capacity, and benevolent intellect."),
    7: ("Veena", "All 7 planets occupy seven distinct signs. Represents artistic brilliance, aesthetic eloquence, and love of music/learning."),
}
