"""Data models, astronomical helpers, and classical astrological primitives for the Unified Dosha Engine."""

from typing import Dict, List, Set, Tuple, Optional, Any


SEVEN_GRAHAS: Tuple[str, ...] = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
NINE_GRAHAS: Tuple[str, ...] = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

KENDRA_HOUSES: Set[int] = {1, 4, 7, 10}
TRIKONA_HOUSES: Set[int] = {1, 5, 9}
UPACHAYA_HOUSES: Set[int] = {3, 6, 10, 11}
DUSTHANA_HOUSES: Set[int] = {6, 8, 12}

# Sign index (1-12) to Sign Names
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

# Sign index to Ruling Graha
SIGN_LORDS: Dict[int, str] = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}

# Own Signs
OWN_SIGNS: Dict[str, Set[int]] = {
    "Sun": {5},
    "Moon": {4},
    "Mars": {1, 8},
    "Mercury": {3, 6},
    "Jupiter": {9, 12},
    "Venus": {2, 7},
    "Saturn": {10, 11},
}

# Exaltation Signs
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

# Debilitation Signs
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

# Classical Parashari full aspects (relative house distance)
PARASHARI_ASPECTS: Dict[str, Set[int]] = {
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

# Marana Karaka Sthana (House positions where planets lose vitality)
MKS_HOUSES: Dict[str, int] = {
    "Sun": 12,
    "Moon": 8,
    "Mars": 7,
    "Mercury": 7,
    "Jupiter": 3,
    "Venus": 6,
    "Saturn": 1,
    "Rahu": 9,
}

NATURAL_MALEFICS: Set[str] = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
NATURAL_BENEFICS: Set[str] = {"Jupiter", "Venus", "Mercury", "Moon"}

# Gandmool Nakshatras (Ruled by Ketu and Mercury at sign junctions)
GANDMOOL_NAKSHATRAS: Set[int] = {1, 9, 10, 18, 19, 27}

# Standard Classical Combustion Orbs in degrees
COMBUSTION_ORBS: Dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}

NAKSHATRA_NAMES_EN: Dict[int, str] = {
    1: "Ashwini", 2: "Bharani", 3: "Krittika", 4: "Rohini", 5: "Mrigashira",
    6: "Ardra", 7: "Punarvasu", 8: "Pushya", 9: "Ashlesha", 10: "Magha",
    11: "Purva Phalguni", 12: "Uttara Phalguni", 13: "Hasta", 14: "Chitra", 15: "Swati",
    16: "Vishakha", 17: "Anuradha", 18: "Jyeshtha", 19: "Moola", 20: "Purva Ashadha",
    21: "Uttara Ashadha", 22: "Shravana", 23: "Dhanishta", 24: "Shatabhisha", 25: "Purva Bhadrapada",
    26: "Uttara Bhadrapada", 27: "Revati"
}

NAKSHATRA_NAMES_TA: Dict[int, str] = {
    1: "அசுவினி", 2: "பரணி", 3: "கிருத்திகை", 4: "ரோகிணி", 5: "மிருகசீரிஷம்",
    6: "திருவாதிரை", 7: "புனர்பூசம்", 8: "பூசம்", 9: "ஆயில்யம்", 10: "மகம்",
    11: "பூரம்", 12: "உத்திரம்", 13: "அஸ்தம்", 14: "சித்திரை", 15: "சுவாதி",
    16: "விசாகம்", 17: "அனுஷம்", 18: "கேட்டை", 19: "மூலம்", 20: "பூராடம்",
    21: "உத்திராடம்", 22: "திருவோணம்", 23: "அவிட்டம்", 24: "சதயம்", 25: "பூரட்டாதி",
    26: "உத்திரட்டாதி", 27: "ரேவதி"
}


class DoshaPlanet:
    """Normalized internal representation of a celestial body for Dosha analysis."""

    def __init__(
        self,
        name: str,
        sign_index: int,
        longitude: float,
        degree_in_sign: float,
        house: int,
        is_retrograde: bool = False,
    ):
        self.name = name
        self.sign_index = sign_index
        self.longitude = longitude % 360.0
        self.degree_in_sign = degree_in_sign
        self.house = house
        self.is_retrograde = is_retrograde
        self.nakshatra_index = int((self.longitude % 360.0) / (360.0 / 27.0)) + 1
        pada_span = (360.0 / 27.0) / 4.0
        deg_in_nak = (self.longitude % 360.0) % (360.0 / 27.0)
        self.nakshatra_pada = min(4, int(deg_in_nak / pada_span) + 1)


class DoshaChartContext:
    """Encapsulates chart data and classical relationship evaluations for dosha detection."""

    def __init__(
        self,
        planets: List[Any],
        ascendant_sign_idx: int,
        houses: Optional[List[Any]] = None,
        ascendant_degree: Optional[float] = None,
    ):
        self.ascendant_sign_idx = ascendant_sign_idx
        self.houses = houses or []
        self.grahas: Dict[str, DoshaPlanet] = {}

        # Resolve exact Ascendant longitude
        if ascendant_degree is not None:
            self.ascendant_longitude = ascendant_degree % 360.0
        elif self.houses and len(self.houses) > 0:
            h1 = self.houses[0]
            cusp = h1.get("cusp_degree") if isinstance(h1, dict) else getattr(h1, "cusp_degree", None)
            if cusp is not None:
                self.ascendant_longitude = float(cusp) % 360.0
            else:
                self.ascendant_longitude = float((ascendant_sign_idx - 1) * 30.0 + 15.0)
        else:
            self.ascendant_longitude = float((ascendant_sign_idx - 1) * 30.0 + 15.0)

        # Normalize planets
        for p in planets:
            p_name = p.get("name") if isinstance(p, dict) else getattr(p, "name", None)
            if not p_name:
                continue

            sign_idx = p.get("sign_index") if isinstance(p, dict) else getattr(p, "sign_index", None)
            lon = p.get("longitude") if isinstance(p, dict) else getattr(p, "longitude", None)
            deg_in_sign = p.get("degree_in_sign") if isinstance(p, dict) else getattr(p, "degree_in_sign", None)
            is_retro = p.get("is_retrograde", False) if isinstance(p, dict) else getattr(p, "is_retrograde", False)

            if lon is not None and sign_idx is None:
                sign_idx = int((lon % 360.0) // 30.0) + 1
            if lon is not None and deg_in_sign is None:
                deg_in_sign = lon % 30.0

            if sign_idx is None:
                continue

            house_num = ((sign_idx - self.ascendant_sign_idx) % 12) + 1
            self.grahas[p_name] = DoshaPlanet(
                name=p_name,
                sign_index=sign_idx,
                longitude=lon if lon is not None else float((sign_idx - 1) * 30 + 15),
                degree_in_sign=deg_in_sign if deg_in_sign is not None else 15.0,
                house=house_num,
                is_retrograde=bool(is_retro),
            )

        # Convenient accessors
        self.moon = self.grahas.get("Moon")
        self.venus = self.grahas.get("Venus")
        self.mars = self.grahas.get("Mars")
        self.jupiter = self.grahas.get("Jupiter")
        self.saturn = self.grahas.get("Saturn")
        self.sun = self.grahas.get("Sun")
        self.rahu = self.grahas.get("Rahu")
        self.ketu = self.grahas.get("Ketu")
        self.mercury = self.grahas.get("Mercury")

        self.moon_sign_idx = self.moon.sign_index if self.moon else 1
        self.venus_sign_idx = self.venus.sign_index if self.venus else 1

    def house_from(self, planet_name: str, ref_sign_idx: int) -> int:
        """Calculate the house occupied by a planet from a specific reference sign (1-12)."""
        graha = self.grahas.get(planet_name)
        if not graha:
            return 1
        return ((graha.sign_index - ref_sign_idx) % 12) + 1

    def get_house_lord(self, house_num: int) -> str:
        """Determine ruling planet of house_num (1-12) from Lagna."""
        sign_of_house = ((self.ascendant_sign_idx - 1 + house_num - 1) % 12) + 1
        return SIGN_LORDS[sign_of_house]

    def get_planets_in_house(self, house_num: int) -> List[str]:
        """List planets occupying house_num (1-12) from Lagna."""
        return [g.name for g in self.grahas.values() if g.house == house_num]

    def get_planets_in_sign(self, sign_idx: int) -> List[str]:
        """List planets occupying a given zodiac sign index (1-12)."""
        return [g.name for g in self.grahas.values() if g.sign_index == sign_idx]

    def is_conjoined(self, graha_a: str, graha_b: str, max_orb_deg: Optional[float] = None) -> bool:
        """Check if two grahas occupy the same zodiac sign, optionally within max_orb_deg."""
        a = self.grahas.get(graha_a)
        b = self.grahas.get(graha_b)
        if not a or not b:
            return False
        if a.sign_index != b.sign_index:
            return False
        if max_orb_deg is not None:
            return abs(a.degree_in_sign - b.degree_in_sign) <= max_orb_deg
        return True

    def angular_separation(self, graha_a: str, graha_b: str) -> float:
        """Compute the shortest angular separation in degrees (0 to 180) between two grahas."""
        a = self.grahas.get(graha_a)
        b = self.grahas.get(graha_b)
        if not a or not b:
            return 180.0
        diff = abs(a.longitude - b.longitude) % 360.0
        return min(diff, 360.0 - diff)

    def has_aspect_on_house(self, aspecting_graha: str, target_house: int) -> bool:
        """Check if aspecting_graha casts a classical Parashari full aspect onto target_house (1-12 from Lagna)."""
        graha = self.grahas.get(aspecting_graha)
        if not graha:
            return False
        dist = ((target_house - graha.house) % 12) + 1
        aspects = PARASHARI_ASPECTS.get(aspecting_graha, {7})
        return dist in aspects

    def has_aspect_on_graha(self, aspecting_graha: str, target_graha: str) -> bool:
        """Check if aspecting_graha casts a classical Parashari full aspect onto target_graha."""
        target = self.grahas.get(target_graha)
        if not target:
            return False
        return self.has_aspect_on_house(aspecting_graha, target.house)

    def is_exalted(self, graha: str) -> bool:
        """Check if graha is in its classical exaltation sign."""
        g = self.grahas.get(graha)
        return bool(g and g.sign_index == EXALTATION_SIGNS.get(graha))

    def is_debilitated(self, graha: str) -> bool:
        """Check if graha is in its classical debilitation sign."""
        g = self.grahas.get(graha)
        return bool(g and g.sign_index == DEBILITATION_SIGNS.get(graha))

    def is_own_sign(self, graha: str) -> bool:
        """Check if graha is situated in its own sign."""
        g = self.grahas.get(graha)
        return bool(g and g.sign_index in OWN_SIGNS.get(graha, set()))

    def is_combust(self, graha: str) -> bool:
        """Check if graha is combust with Sun within standard classical orbs."""
        if graha == "Sun" or graha in ("Rahu", "Ketu"):
            return False
        if not self.sun or graha not in self.grahas:
            return False
        max_orb = COMBUSTION_ORBS.get(graha, 12.0)
        return self.angular_separation("Sun", graha) <= max_orb

    @staticmethod
    def is_gandanta_zone(longitude: float) -> Tuple[bool, str, str]:
        """Check if a celestial coordinate (0-360) falls in the classical water-fire Gandanta junctions.

        The three canonical Gandantas occur at:
        1. Revati-Ashwini: Pisces 26°40' (356.6667°) to Aries 3°20' (3.3333°)
        2. Ashlesha-Magha: Cancer 26°40' (116.6667°) to Leo 3°20' (123.3333°)
        3. Jyeshtha-Moola: Scorpio 26°40' (236.6667°) to Sagittarius 3°20' (243.3333°)

        Returns:
            (is_gandanta, junction_name_en, junction_name_ta)
        """
        lon = longitude % 360.0
        if lon >= 356.666667 or lon <= 3.333333:
            return True, "Revati–Ashwini Gandanta (Meena–Mesha Sandhi)", "ரேவதி–அசுவினி கண்டாந்தம் (மீன–மேஷ சந்தி)"
        if 116.666667 <= lon <= 123.333333:
            return True, "Ashlesha–Magha Gandanta (Karkataka–Simha Sandhi)", "ஆயில்யம்–மகம் கண்டாந்தம் (கடக–சிம்ம சந்தி)"
        if 236.666667 <= lon <= 243.333333:
            return True, "Jyeshtha–Moola Gandanta (Vrischika–Dhanus Sandhi)", "கேட்டை–மூலம் கண்டாந்தம் (விருச்சிக–தனுசு சந்தி)"
        return False, "", ""

