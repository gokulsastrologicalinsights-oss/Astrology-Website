"""Models, constants, and astrological calculation primitives for the Vedic Yoga Engine."""

from typing import Dict, List, Set, Tuple, Optional, Any


SEVEN_GRAHAS: Tuple[str, ...] = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
NINE_GRAHAS: Tuple[str, ...] = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

NATURAL_BENEFICS: Set[str] = {"Jupiter", "Venus", "Mercury"}
NATURAL_MALEFICS: Set[str] = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

KENDRA_HOUSES: Set[int] = {1, 4, 7, 10}
TRIKONA_HOUSES: Set[int] = {1, 5, 9}
UPACHAYA_HOUSES: Set[int] = {3, 6, 10, 11}
DUSTHANA_HOUSES: Set[int] = {6, 8, 12}
DHANA_HOUSES: Set[int] = {2, 5, 9, 11}

# Sign index (1-12) to Ruling Planet
SIGN_LORDS: Dict[int, str] = {
    1: "Mars",      # Aries
    2: "Venus",     # Taurus
    3: "Mercury",   # Gemini
    4: "Moon",      # Cancer
    5: "Sun",       # Leo
    6: "Mercury",   # Virgo
    7: "Venus",     # Libra
    8: "Mars",      # Scorpio
    9: "Jupiter",   # Sagittarius
    10: "Saturn",   # Capricorn
    11: "Saturn",   # Aquarius
    12: "Jupiter",  # Pisces
}

# Planet to Own Signs
OWN_SIGNS: Dict[str, Set[int]] = {
    "Sun": {5},
    "Moon": {4},
    "Mars": {1, 8},
    "Mercury": {3, 6},
    "Jupiter": {9, 12},
    "Venus": {2, 7},
    "Saturn": {10, 11},
}

# Planet to Exaltation Sign
EXALTATION_SIGNS: Dict[str, int] = {
    "Sun": 1,       # Aries
    "Moon": 2,      # Taurus
    "Mars": 10,     # Capricorn
    "Mercury": 6,   # Virgo
    "Jupiter": 4,   # Cancer
    "Venus": 12,    # Pisces
    "Saturn": 7,    # Libra
    "Rahu": 2,      # Taurus (also Gemini per some traditions)
    "Ketu": 8,      # Scorpio (also Sagittarius per some traditions)
}

# Planet to Debilitation Sign
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

# Planet to Moolatrikona Sign
MOOLATRIKONA_SIGNS: Dict[str, int] = {
    "Sun": 5,       # Leo
    "Moon": 2,      # Taurus
    "Mars": 1,      # Aries
    "Mercury": 6,   # Virgo
    "Jupiter": 9,   # Sagittarius
    "Venus": 7,     # Libra
    "Saturn": 11,   # Aquarius
}

# Special Graha Drishti (Parashari full aspects by relative house count)
# 1st from self is 1 (conjunction); 7th is standard opposition
SPECIAL_ASPECTS: Dict[str, Set[int]] = {
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


def count_houses_inclusive(from_house: int, to_house: int) -> int:
    """Return inclusive house distance from from_house to to_house (1 to 12)."""
    return ((to_house - from_house) % 12) + 1


def get_nth_house(from_house: int, n: int) -> int:
    """Return the nth house counting inclusively from from_house (1 to 12)."""
    return ((from_house - 1 + (n - 1)) % 12) + 1


class YogaChartContext:
    """Precomputed lookup container for fast, deterministic yoga evaluations."""

    def __init__(
        self,
        planets: List[Any],
        ascendant_sign_idx: int,
        houses: Optional[List[Any]] = None,
        gender: str = "male",
        is_day_birth: Optional[bool] = None,
    ):
        self.lagna_sign_idx = ascendant_sign_idx
        self.gender = gender.lower()

        # Map house (1-12) to sign (1-12) under whole-sign / rashi-bhava baseline
        self.house_to_sign: Dict[int, int] = {}
        self.sign_to_house: Dict[int, int] = {}
        for h in range(1, 13):
            sign_idx = ((self.lagna_sign_idx - 1 + (h - 1)) % 12) + 1
            self.house_to_sign[h] = sign_idx
            self.sign_to_house[sign_idx] = h

        # Map house to lord
        self.house_lords: Dict[int, str] = {
            h: SIGN_LORDS[self.house_to_sign[h]] for h in range(1, 13)
        }

        # Planetary positions
        self.planet_sign: Dict[str, int] = {}
        self.planet_house: Dict[str, int] = {}
        self.planet_deg_in_sign: Dict[str, float] = {}
        self.planet_longitude: Dict[str, float] = {}
        self.planet_is_retrograde: Dict[str, bool] = {}
        self.planet_navamsa_sign: Dict[str, int] = {}
        self.house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        self.sign_occupants: Dict[int, List[str]] = {s: [] for s in range(1, 13)}

        for p in planets:
            p_name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else None)
            if not p_name:
                continue

            sign_idx = getattr(p, "sign_index", None) or (p.get("sign_index") if isinstance(p, dict) else None)
            lon = getattr(p, "longitude", None) or (p.get("longitude") if isinstance(p, dict) else None)
            deg_in_sign = getattr(p, "degree_in_sign", None) or (p.get("degree_in_sign") if isinstance(p, dict) else 0.0)
            retro = getattr(p, "is_retrograde", False) or (p.get("is_retrograde", False) if isinstance(p, dict) else False)

            if sign_idx is not None:
                house_num = self.sign_to_house.get(sign_idx, ((sign_idx - self.lagna_sign_idx) % 12) + 1)
                self.planet_sign[p_name] = sign_idx
                self.planet_house[p_name] = house_num
                self.planet_deg_in_sign[p_name] = float(deg_in_sign)
                self.planet_is_retrograde[p_name] = bool(retro)
                self.house_occupants[house_num].append(p_name)
                self.sign_occupants[sign_idx].append(p_name)

                if lon is not None:
                    self.planet_longitude[p_name] = float(lon)
                    # Boundary-safe integer milli-arcsecond Navamsa calculation (immune to IEEE 754 division truncation)
                    from app.services.varga_engine import calculate_navamsa_from_longitude
                    varga_info = calculate_navamsa_from_longitude(float(lon))
                    self.planet_navamsa_sign[p_name] = varga_info["d9_sign_index"]
                else:
                    # Approximation if longitude omitted: based on degree in sign
                    nav_in_sign = int(deg_in_sign / (30.0 / 9.0))
                    # Element start: Fire (1,5,9) starts Aries(1); Earth (2,6,10) starts Capricorn(10);
                    # Air (3,7,11) starts Libra(7); Water (4,8,12) starts Cancer(4)
                    elem_starts = {1: 1, 2: 10, 3: 7, 4: 4, 5: 1, 6: 10, 7: 7, 8: 4, 9: 1, 10: 10, 11: 7, 12: 4}
                    start_sign = elem_starts.get(sign_idx, 1)
                    self.planet_navamsa_sign[p_name] = ((start_sign - 1 + nav_in_sign) % 12) + 1

        # Day or Night birth:
        # In Vedic convention, Sun in houses 7, 8, 9, 10, 11, 12 represents daylight hours (above horizon)
        # Sun in houses 1, 2, 3, 4, 5, 6 represents night hours (below horizon)
        if is_day_birth is not None:
            self.is_day_birth = is_day_birth
        else:
            sun_house = self.planet_house.get("Sun")
            self.is_day_birth = (sun_house in {7, 8, 9, 10, 11, 12}) if sun_house else True

    def planet_aspects_house(self, planet: str, target_house: int) -> bool:
        """Check if planet casts full Parashari drishti on target_house."""
        source_house = self.planet_house.get(planet)
        if not source_house:
            return False
        diff = count_houses_inclusive(source_house, target_house)
        allowed = SPECIAL_ASPECTS.get(planet, {7})
        return diff in allowed

    def planet_aspects_planet(self, planet_a: str, planet_b: str) -> bool:
        """Check if planet_a aspects planet_b."""
        house_b = self.planet_house.get(planet_b)
        if not house_b:
            return False
        return self.planet_aspects_house(planet_a, house_b)

    def are_mutually_aspecting(self, planet_a: str, planet_b: str) -> bool:
        """Check if planet_a and planet_b mutually cast full aspects on each other."""
        return self.planet_aspects_planet(planet_a, planet_b) and self.planet_aspects_planet(planet_b, planet_a)

    def are_conjoined(self, planet_a: str, planet_b: str) -> bool:
        """Check if planet_a and planet_b share the same sign/house."""
        h_a = self.planet_house.get(planet_a)
        h_b = self.planet_house.get(planet_b)
        return bool(h_a and h_b and h_a == h_b)

    def is_exalted(self, planet: str) -> bool:
        """Check if planet is in its sign of exaltation."""
        sign = self.planet_sign.get(planet)
        return bool(sign and sign == EXALTATION_SIGNS.get(planet))

    def is_debilitated(self, planet: str) -> bool:
        """Check if planet is in its sign of debilitation."""
        sign = self.planet_sign.get(planet)
        return bool(sign and sign == DEBILITATION_SIGNS.get(planet))

    def is_in_own_sign(self, planet: str) -> bool:
        """Check if planet is in its own sign."""
        sign = self.planet_sign.get(planet)
        return bool(sign and sign in OWN_SIGNS.get(planet, set()))

    def is_in_kendra(self, planet: str) -> bool:
        """Check if planet is in a Kendra (1, 4, 7, 10) from Lagna."""
        h = self.planet_house.get(planet)
        return bool(h and h in KENDRA_HOUSES)

    def is_in_trikona(self, planet: str) -> bool:
        """Check if planet is in a Trikona (1, 5, 9) from Lagna."""
        h = self.planet_house.get(planet)
        return bool(h and h in TRIKONA_HOUSES)

    def is_in_dusthana(self, planet: str) -> bool:
        """Check if planet is in a Dusthana (6, 8, 12) from Lagna."""
        h = self.planet_house.get(planet)
        return bool(h and h in DUSTHANA_HOUSES)

    def is_combust(self, planet: str, combustion_orbs: Optional[Dict[str, float]] = None) -> bool:
        """Check if planet is combust by Sun."""
        if planet in ("Sun", "Rahu", "Ketu"):
            return False
        sun_lon = self.planet_longitude.get("Sun")
        planet_lon = self.planet_longitude.get(planet)
        if sun_lon is None or planet_lon is None:
            # Fallback to same sign
            return self.are_conjoined("Sun", planet)
        default_orbs = {
            "Moon": 12.0,
            "Mars": 17.0,
            "Mercury": 14.0,  # 12 if retrograde
            "Jupiter": 11.0,
            "Venus": 10.0,    # 8 if retrograde
            "Saturn": 15.0,
        }
        orbs = combustion_orbs or default_orbs
        orb_limit = orbs.get(planet, 12.0)
        if self.planet_is_retrograde.get(planet, False):
            if planet == "Mercury":
                orb_limit = 12.0
            elif planet == "Venus":
                orb_limit = 8.0

        diff = abs(sun_lon - planet_lon)
        if diff > 180.0:
            diff = 360.0 - diff
        return diff <= orb_limit

    def is_vargottama(self, planet: str) -> bool:
        """Check if planet is Vargottama (occupies the same zodiac sign in D1 Rasi and D9 Navamsha).

        Per Phaladeepika Ch. 3, v. 12 and BPHS Ch. 45, a planet in Vargottama acts as if in its own sign,
        substantially elevating its strength and auspiciousness.
        """
        r_sign = self.planet_sign.get(planet)
        d9_sign = self.planet_navamsa_sign.get(planet)
        return bool(r_sign and d9_sign and r_sign == d9_sign)

    def get_combustion_details(
        self, planet: str, combustion_orbs: Optional[Dict[str, float]] = None
    ) -> Tuple[bool, float, float]:
        """Return (is_combust, actual_separation_degrees, orb_limit_degrees)."""
        if planet in ("Sun", "Rahu", "Ketu"):
            return False, 999.0, 0.0
        sun_lon = self.planet_longitude.get("Sun")
        planet_lon = self.planet_longitude.get(planet)
        if sun_lon is None or planet_lon is None:
            conjoined = self.are_conjoined("Sun", planet)
            return conjoined, 0.0, 30.0

        default_orbs = {
            "Moon": 12.0,
            "Mars": 17.0,
            "Mercury": 14.0,
            "Jupiter": 11.0,
            "Venus": 10.0,
            "Saturn": 15.0,
        }
        orbs = combustion_orbs or default_orbs
        orb_limit = orbs.get(planet, 12.0)
        if self.planet_is_retrograde.get(planet, False):
            if planet == "Mercury":
                orb_limit = 12.0
            elif planet == "Venus":
                orb_limit = 8.0

        diff = abs(sun_lon - planet_lon)
        if diff > 180.0:
            diff = 360.0 - diff
        return (diff <= orb_limit), round(diff, 4), orb_limit

