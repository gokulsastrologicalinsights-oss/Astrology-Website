"""Kala Bala — Temporal Strength.

Eight classical sub-components (BPHS Ch. 27, Slokas 19-32):
1. Nathonnatha Bala (Day/Night strength)
2. Paksha Bala (Lunar fortnight strength)
3. Tribhaga Bala (Three-part-of-day/night strength)
4. Abda Bala (Solar year lord strength)
5. Masa Bala (Solar month lord strength)
6. Vara Bala (Weekday lord strength)
7. Hora Bala (Planetary hour lord strength)
8. Ayana Bala (Equinoctial/Solstitial strength based on planetary declination)

Classical References:
- BPHS Ch. 27: Kala Bala calculation rules.
- Phaladeepika Ch. 4: Kala Bala principles.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Dict, List
from app.services.shadbala_engine.models import ChartCtx, PlanetCtx
from app.schemas.shadbala import KalaBalaSub

# Diurnal and nocturnal groups for Kala Bala
_DIURNAL_GRAHAS = frozenset(["Sun", "Jupiter", "Venus"])
_NOCTURNAL_GRAHAS = frozenset(["Moon", "Mars", "Saturn"])

# Chaldean planetary hour sequence (descending geocentric orbital speed)
_CHALDEAN_ORDER: List[str] = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Sign lord mapping for Solar Month (Masa Bala)
_SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

# Weekday lord mapping for Vara Bala
_VARA_LORDS: Dict[str, str] = {
    "sunday": "Sun",
    "ravivara": "Sun",
    "ravi": "Sun",
    "monday": "Moon",
    "somavara": "Moon",
    "soma": "Moon",
    "tuesday": "Mars",
    "mangalavara": "Mars",
    "mangala": "Mars",
    "wednesday": "Mercury",
    "budhavara": "Mercury",
    "budha": "Mercury",
    "thursday": "Jupiter",
    "guruvara": "Jupiter",
    "guru": "Jupiter",
    "brihaspativara": "Jupiter",
    "friday": "Venus",
    "shukravara": "Venus",
    "shukra": "Venus",
    "saturday": "Saturn",
    "shanivara": "Saturn",
    "shani": "Saturn",
}

_WEEKDAY_INDEX_MAP: Dict[int, str] = {
    0: "Moon",     # Monday
    1: "Mars",     # Tuesday
    2: "Mercury",  # Wednesday
    3: "Jupiter",  # Thursday
    4: "Venus",    # Friday
    5: "Saturn",   # Saturday
    6: "Sun",      # Sunday
}


def _parse_birth_hour(birth_time_str: str) -> float:
    """Parse HH:MM or HH:MM:SS into decimal hours (0.0 to 23.999)."""
    try:
        parts = birth_time_str.strip().split(":")
        h = float(parts[0])
        m = float(parts[1]) if len(parts) > 1 else 0.0
        s = float(parts[2]) if len(parts) > 2 else 0.0
        return h + m / 60.0 + s / 3600.0
    except Exception:
        return 12.0


def _get_weekday_lord(ctx: ChartCtx) -> str:
    """Determine weekday lord from ctx.vara_name or birth_date."""
    raw = ctx.vara_name.strip().lower()
    for key, lord in _VARA_LORDS.items():
        if key in raw:
            return lord
    try:
        dt = datetime.strptime(ctx.birth.birth_date, "%Y-%m-%d")
        return _WEEKDAY_INDEX_MAP.get(dt.weekday(), "Sun")
    except Exception:
        return "Sun"


def calc_nathonnatha_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """1. Nathonnatha Bala — Day/Night strength (0, 30, or 60 virupas).

    Diurnal planets (Sun, Jupiter, Venus) receive 60 during day birth, 0 at night.
    Nocturnal planets (Moon, Mars, Saturn) receive 60 during night birth, 0 during day.
    Mercury always receives 30 virupas.
    """
    if planet.name == "Mercury":
        return 30.0

    if ctx.is_day_birth:
        return 60.0 if planet.name in _DIURNAL_GRAHAS else 0.0
    else:
        return 60.0 if planet.name in _NOCTURNAL_GRAHAS else 0.0


def calc_paksha_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """2. Paksha Bala — Lunar fortnight strength (0 to 60 virupas).

    Benefics (Jupiter, Venus, Moon, Mercury) gain strength with lunar illumination.
    Malefics (Sun, Mars, Saturn) gain strength in darkness (New Moon).
    """
    elongation = (ctx.moon_longitude - ctx.sun_longitude) % 360.0
    arc = elongation if elongation <= 180.0 else (360.0 - elongation)
    paksha_fraction = arc / 180.0
    paksha_strong = 60.0 * paksha_fraction

    benefics = frozenset(["Jupiter", "Venus", "Moon", "Mercury"])
    if planet.name in benefics:
        return round(paksha_strong, 4)
    else:
        return round(60.0 - paksha_strong, 4)


def calc_tribhaga_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """3. Tribhaga Bala — Three-part-of-day/night strength (0 or 15 virupas).

    Jupiter always receives 15 virupas per BPHS.
    Day: Part 1 = Mercury, Part 2 = Sun, Part 3 = Saturn.
    Night: Part 1 = Moon, Part 2 = Venus, Part 3 = Mars.
    """
    if planet.name == "Jupiter":
        return 15.0

    hour = _parse_birth_hour(ctx.birth.birth_time)
    if ctx.is_day_birth:
        if hour < 10.0:
            return 15.0 if planet.name == "Mercury" else 0.0
        elif hour < 14.0:
            return 15.0 if planet.name == "Sun" else 0.0
        else:
            return 15.0 if planet.name == "Saturn" else 0.0
    else:
        if 18.0 <= hour < 22.0:
            return 15.0 if planet.name == "Moon" else 0.0
        elif hour >= 22.0 or hour < 2.0:
            return 15.0 if planet.name == "Venus" else 0.0
        else:
            return 15.0 if planet.name == "Mars" else 0.0


def calc_abda_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """4. Abda Bala — Solar year lord strength (0 or 15 virupas).

    Per BPHS, the Lord of the Year (Abhadhipati) is the ruler of the weekday
    when the solar year commenced at Mesha Sankranti (approx April 14th).
    """
    try:
        dt = datetime.strptime(ctx.birth.birth_date, "%Y-%m-%d")
        year = dt.year
        # If born before April 14, the solar year began on April 14 of the preceding calendar year
        if (dt.month, dt.day) < (4, 14):
            year -= 1
        sankranti_date = datetime(year, 4, 14)
        year_lord = _WEEKDAY_INDEX_MAP.get(sankranti_date.weekday(), "Sun")
        return 15.0 if planet.name == year_lord else 0.0
    except Exception:
        return 15.0 if planet.name == "Sun" else 0.0


def calc_masa_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """5. Masa Bala — Solar month lord strength (0 or 30 virupas).

    The ruler of the solar zodiac sign currently occupied by the Sun receives 30 virupas.
    """
    sun_sign = int(ctx.sun_longitude // 30.0) + 1
    month_lord = _SIGN_LORDS.get(sun_sign, "Sun")
    return 30.0 if planet.name == month_lord else 0.0


def calc_vara_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """6. Vara Bala — Weekday lord strength (0 or 45 virupas).

    The lord of the birth day receives 45 virupas.
    """
    day_lord = _get_weekday_lord(ctx)
    return 45.0 if planet.name == day_lord else 0.0


def calc_hora_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """7. Hora Bala — Planetary hour lord strength (0 or 60 virupas).

    The planetary hour starts at sunrise (~06:00) with the weekday lord,
    proceeding in Chaldean descending order. The hora lord receives 60 virupas.
    """
    day_lord = _get_weekday_lord(ctx)
    hour = _parse_birth_hour(ctx.birth.birth_time)
    hours_since_sunrise = int((hour - 6.0) % 24)

    start_idx = _CHALDEAN_ORDER.index(day_lord) if day_lord in _CHALDEAN_ORDER else 0
    current_hora_lord = _CHALDEAN_ORDER[(start_idx + hours_since_sunrise) % 7]

    return 60.0 if planet.name == current_hora_lord else 0.0


def calc_ayana_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """8. Ayana Bala — Continuous Equinoctial/Solstitial strength (0 to 60 virupas).

    Classical formula (BPHS Ch. 27, Slokas 26-29 & BV Raman):
    - Obliquity of ecliptic: ε ≈ 23.44°
    - Sayana (tropical) longitude = (sidereal_lon + ayanamsa) % 360
    - Declination δ (Kranti): sin(δ) = sin(sayana_lon) * sin(ε)
    - For Sun, Mars, Jupiter, Venus (strengthened by Northern declination):
        Ayana Bala = (24.0 + δ) * 1.25
    - For Moon, Saturn (strengthened by Southern declination):
        Ayana Bala = (24.0 - δ) * 1.25
    - For Mercury:
        Ayana Bala = (24.0 + δ) * 1.25 (or normalized centered at 30 virupas)
    """
    # Estimate Chitrapaksha/Lahiri ayanamsa based on birth year
    try:
        birth_year = datetime.strptime(ctx.birth.birth_date, "%Y-%m-%d").year
    except Exception:
        birth_year = 2000
    # Lahiri ayanamsa is 23.85° at 2000.0, rate of precession ~50.29"/year ≈ 0.01397°/year
    ayanamsa_est = 23.85 + (birth_year - 2000) * 0.01397

    sayana_lon = (planet.longitude + ayanamsa_est) % 360.0
    eps_rad = math.radians(23.44)
    sin_delta = math.sin(math.radians(sayana_lon)) * math.sin(eps_rad)
    delta_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_delta))))

    if planet.name in ("Sun", "Mars", "Jupiter", "Venus"):
        ayana = (24.0 + delta_deg) * 1.25
    elif planet.name in ("Moon", "Saturn"):
        ayana = (24.0 - delta_deg) * 1.25
    else:  # Mercury
        ayana = (24.0 + delta_deg) * 1.25

    return round(max(0.0, min(60.0, ayana)), 4)


def calc_kala_bala(planet: PlanetCtx, ctx: ChartCtx) -> KalaBalaSub:
    """Compute all eight sub-components of Kala Bala and return aggregate."""
    nathonnatha = calc_nathonnatha_bala(planet, ctx)
    paksha = calc_paksha_bala(planet, ctx)
    tribhaga = calc_tribhaga_bala(planet, ctx)
    abda = calc_abda_bala(planet, ctx)
    masa = calc_masa_bala(planet, ctx)
    vara = calc_vara_bala(planet, ctx)
    hora = calc_hora_bala(planet, ctx)
    ayana = calc_ayana_bala(planet, ctx)

    total = nathonnatha + paksha + tribhaga + abda + masa + vara + hora + ayana
    return KalaBalaSub(
        nathonnatha_bala=round(nathonnatha, 4),
        paksha_bala=round(paksha, 4),
        tribhaga_bala=round(tribhaga, 4),
        abda_bala=round(abda, 4),
        masa_bala=round(masa, 4),
        vara_bala=round(vara, 4),
        hora_bala=round(hora, 4),
        ayana_bala=round(ayana, 4),
        total=round(total, 4),
    )
