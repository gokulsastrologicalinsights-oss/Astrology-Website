"""Internal dataclasses for passing chart context through the Shadbala engine.

These are NOT Pydantic models — they are lightweight Python dataclasses used
only within the calculation pipeline for performance and clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PlanetCtx:
    """Extracted context for one graha, derived from XALEN PlanetInfo."""
    name: str
    body_id: int
    longitude: float          # Sidereal longitude 0-360°
    degree_in_sign: float     # 0-30°
    sign_index: int           # 1-12 (1=Aries)
    speed_deg_per_day: float  # Negative = retrograde
    is_retrograde: bool
    nakshatra_lord: str       # Vimshottari nakshatra lord name


@dataclass
class HouseCtx:
    """Extracted context for one bhava (house)."""
    house_number: int         # 1-12
    sign_index: int           # 1-12


@dataclass
class AscendantCtx:
    """Extracted ascendant context."""
    degree: float             # 0-360° sidereal
    sign_index: int           # 1-12
    degree_in_sign: float     # 0-30°


@dataclass
class BirthCtx:
    """Birth time and location context for Kala Bala computation."""
    birth_date: str           # "YYYY-MM-DD"
    birth_time: str           # "HH:MM" or "HH:MM:SS"
    timezone_str: str         # e.g. "Asia/Kolkata"
    latitude: float
    longitude: float          # Geographic longitude (east = positive)


@dataclass
class ChartCtx:
    """Full chart context passed to every Shadbala sub-calculator."""
    planets: List[PlanetCtx]
    houses: List[HouseCtx]
    ascendant: AscendantCtx
    birth: BirthCtx
    vara_name: str            # Weekday from XALEN PanchangInfo.vara (e.g. "Ravivara")
    sun_longitude: float      # Needed for Paksha and Ayana calculations
    moon_longitude: float     # Needed for Paksha Bala
    is_day_birth: bool        # Sun in houses 7-12 (above horizon)

    # Map planet name → PlanetCtx for O(1) lookup
    planet_map: Dict[str, PlanetCtx] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.planet_map = {p.name: p for p in self.planets}
