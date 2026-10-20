"""Sthana Bala — Positional Strength.

Five classical sub-components (BPHS Ch. 27, Slokas 5-22):
1. Uchcha Bala        — Exaltation strength (0-60 virupas).
2. Saptavargaja Bala  — Seven-divisional (D1, D2, D3, D7, D9, D12, D30) placement strength (Panchadha Maitri).
3. Ojhayugma Bala     — Odd/even sign and Navamsha placement strength (0-30 virupas).
4. Kendradi Bala      — House quadrant/succedent/cadent strength (15, 30, or 60 virupas).
5. Drekkana Bala      — Decanate gender-based strength (0 or 15 virupas).

All strengths are expressed in virupas (shashtiamsas). 60 virupas = 1 rupa.
"""

from __future__ import annotations

from typing import Dict, Tuple

from app.services.shadbala_engine.models import ChartCtx, PlanetCtx
from app.schemas.shadbala import SthanaBalaSub


# ---------------------------------------------------------------------------
# 1. UCHCHA BALA — Exaltation Strength
# ---------------------------------------------------------------------------
# Classical Exaltation deep degrees (BPHS Ch. 3 / Ch. 27):
# Sun: Aries 10°, Moon: Taurus 3°, Mars: Capricorn 28°, Mercury: Virgo 15°,
# Jupiter: Cancer 5°, Venus: Pisces 27°, Saturn: Libra 20°
_EXALTATION_LON: Dict[str, float] = {
    "Sun":     10.0,   # 10° Aries
    "Moon":    33.0,   # 3° Taurus
    "Mars":    298.0,  # 28° Capricorn
    "Mercury": 165.0,  # 15° Virgo
    "Jupiter": 95.0,   # 5° Cancer
    "Venus":   357.0,  # 27° Pisces
    "Saturn":  200.0,  # 20° Libra
}


def _angular_distance(lon_a: float, lon_b: float) -> float:
    """Shortest circular distance between two ecliptic longitudes (0-180°)."""
    diff = abs(lon_a - lon_b) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def calc_uchcha_bala(planet: PlanetCtx) -> float:
    """Return Uchcha Bala in virupas (0-60).

    Formula (BPHS Ch. 27, Sloka 5):
        uchcha_bala = (180 - angular_distance(λ, λ_exalt)) / 3.0
    """
    if planet.name not in _EXALTATION_LON:
        return 0.0
    dist = _angular_distance(planet.longitude, _EXALTATION_LON[planet.name])
    return max(0.0, min(60.0, (180.0 - dist) / 3.0))


# ---------------------------------------------------------------------------
# 2. SAPTAVARGAJA BALA — Seven-Divisional Dignity Strength
# ---------------------------------------------------------------------------
# Evaluated across D1, D2, D3, D7, D9, D12, D30 using Panchadha Maitri
# (Five-fold Compound Friendship = Naisargika + Tatkalika) per BPHS Ch. 27, Slokas 8-11:
# - Moolatrikona: 45.0 virupas
# - Swakshetra (Own sign): 30.0 virupas
# - Adhi-Mitra (Great Friend): 22.5 virupas
# - Mitra (Friend): 15.0 virupas
# - Sama (Neutral): 7.5 virupas
# - Shatru (Enemy): 3.75 virupas
# - Adhi-Shatru (Great Enemy): 1.875 virupas

SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

MOOLATRIKONA_SIGNS: Dict[str, int] = {
    "Sun": 5, "Moon": 2, "Mars": 1, "Mercury": 6,
    "Jupiter": 9, "Venus": 7, "Saturn": 11,
}

MOOLATRIKONA_RANGES: Dict[str, Tuple[float, float]] = {
    "Sun": (0.0, 20.0), "Moon": (4.0, 30.0), "Mars": (0.0, 12.0),
    "Mercury": (16.0, 20.0), "Jupiter": (0.0, 10.0),
    "Venus": (0.0, 15.0), "Saturn": (0.0, 20.0),
}

PERMANENT_FRIENDS: Dict[str, frozenset] = {
    "Sun":     frozenset(["Moon", "Mars", "Jupiter"]),
    "Moon":    frozenset(["Sun", "Mercury"]),
    "Mars":    frozenset(["Sun", "Moon", "Jupiter"]),
    "Mercury": frozenset(["Sun", "Venus"]),
    "Jupiter": frozenset(["Sun", "Moon", "Mars"]),
    "Venus":   frozenset(["Mercury", "Saturn"]),
    "Saturn":  frozenset(["Mercury", "Venus"]),
}

PERMANENT_ENEMIES: Dict[str, frozenset] = {
    "Sun":     frozenset(["Venus", "Saturn"]),
    "Moon":    frozenset([]),
    "Mars":    frozenset(["Mercury"]),
    "Mercury": frozenset(["Moon"]),
    "Jupiter": frozenset(["Mercury", "Venus"]),
    "Venus":   frozenset(["Sun", "Moon"]),
    "Saturn":  frozenset(["Sun", "Moon", "Mars"]),
}


def _get_divisional_signs(longitude: float) -> Dict[str, int]:
    """Compute the 1-indexed zodiac sign (1-12) in all seven classical vargas."""
    s = int(longitude // 30.0) + 1
    deg = longitude % 30.0
    is_odd = (s % 2) == 1

    # 1. D1 Rasi
    d1 = s

    # 2. D2 Hora (BPHS: Odd signs: 0-15° Sun (Leo=5), 15-30° Moon (Cancer=4); Even signs: 0-15° Moon (4), 15-30° Sun (5))
    if is_odd:
        d2 = 5 if deg < 15.0 else 4
    else:
        d2 = 4 if deg < 15.0 else 5

    # 3. D3 Drekkana (0-10° same, 10-20° 5th, 20-30° 9th)
    if deg < 10.0:
        d3 = s
    elif deg < 20.0:
        d3 = ((s - 1 + 4) % 12) + 1
    else:
        d3 = ((s - 1 + 8) % 12) + 1

    # 4. D7 Saptamsha (Odd signs: from same sign; Even signs: from 7th sign)
    s_idx = int(deg // (30.0 / 7.0))
    d7 = ((s - 1 + s_idx) % 12) + 1 if is_odd else ((s - 1 + 6 + s_idx) % 12) + 1

    # 5. D9 Navamsha (Fiery from 1, Earthy from 10, Airy from 7, Watery from 4)
    nav_idx = int(deg // (30.0 / 9.0))
    element_start = {1: 1, 5: 1, 9: 1, 2: 10, 6: 10, 10: 10, 3: 7, 7: 7, 11: 7, 4: 4, 8: 4, 12: 4}
    d9 = ((element_start[s] - 1 + nav_idx) % 12) + 1

    # 6. D12 Dvadasamsha (Count 2°30' divisions from same sign)
    d12_idx = int(deg // 2.5)
    d12 = ((s - 1 + d12_idx) % 12) + 1

    # 7. D30 Trimsamsha (BPHS rules: Odd: 0-5 Mars/1, 5-10 Sat/11, 10-18 Jup/9, 18-25 Merc/3, 25-30 Ven/7;
    #                   Even: 0-5 Ven/2, 5-12 Merc/6, 12-20 Jup/12, 20-25 Sat/10, 25-30 Mars/8)
    if is_odd:
        if deg < 5.0: d30 = 1
        elif deg < 10.0: d30 = 11
        elif deg < 18.0: d30 = 9
        elif deg < 25.0: d30 = 3
        else: d30 = 7
    else:
        if deg < 5.0: d30 = 2
        elif deg < 12.0: d30 = 6
        elif deg < 20.0: d30 = 12
        elif deg < 25.0: d30 = 10
        else: d30 = 8

    return {"D1": d1, "D2": d2, "D3": d3, "D7": d7, "D9": d9, "D12": d12, "D30": d30}


def _evaluate_panchadha_dignity(
    planet_name: str,
    target_sign: int,
    rasi_positions: Dict[str, int],
    is_d1: bool = False,
    deg_in_sign: float = 0.0,
) -> float:
    """Evaluate Panchadha Maitri dignity score (virupas) for a planet in a divisional sign."""
    lord = SIGN_LORDS[target_sign]

    # Own sign / Moolatrikona
    if lord == planet_name:
        if is_d1 and target_sign == MOOLATRIKONA_SIGNS.get(planet_name):
            lo, hi = MOOLATRIKONA_RANGES.get(planet_name, (0.0, 30.0))
            if lo <= deg_in_sign <= hi:
                return 45.0  # Moolatrikona
        return 30.0  # Swakshetra

    # 1. Natural friendship (Naisargika)
    if lord in PERMANENT_FRIENDS.get(planet_name, frozenset()):
        nat = 1
    elif lord in PERMANENT_ENEMIES.get(planet_name, frozenset()):
        nat = -1
    else:
        nat = 0

    # 2. Temporal friendship (Tatkalika) based on Rasi chart placement:
    # Planets in 2, 3, 4, 10, 11, 12 from planet are temporal friends (+1); others are enemies (-1).
    p_sign = rasi_positions.get(planet_name, 1)
    l_sign = rasi_positions.get(lord, 1)
    diff = (l_sign - p_sign) % 12
    temp = 1 if diff in (1, 2, 3, 9, 10, 11) else -1

    # 3. Compound Panchadha Maitri
    combo = nat + temp
    if combo == 2:
        return 22.5   # Adhi-Mitra (Great Friend)
    elif combo == 1:
        return 15.0   # Mitra (Friend)
    elif combo == 0:
        return 7.5    # Sama (Neutral)
    elif combo == -1:
        return 3.75   # Shatru (Enemy)
    else:
        return 1.875  # Adhi-Shatru (Great Enemy)


def calc_saptavargaja_bala(planet: PlanetCtx, ctx: ChartCtx | None = None) -> float:
    """Compute Saptavargaja Bala across all 7 classical vargas using Panchadha Maitri."""
    rasi_positions = {p.name: p.sign_index for p in ctx.planets} if ctx else {planet.name: planet.sign_index}
    vargas = _get_divisional_signs(planet.longitude)

    total_virupas = 0.0
    for v_name, sign_idx in vargas.items():
        score = _evaluate_panchadha_dignity(
            planet_name=planet.name,
            target_sign=sign_idx,
            rasi_positions=rasi_positions,
            is_d1=(v_name == "D1"),
            deg_in_sign=planet.degree_in_sign,
        )
        total_virupas += score

    return round(total_virupas, 4)


# ---------------------------------------------------------------------------
# 3. OJHAYUGMA BALA — Odd/Even Sign & Navamsha Placement Strength
# ---------------------------------------------------------------------------
# BPHS Ch. 27, Sloka 12:
# Male planets (Sun, Mars, Jupiter) in odd sign: 15 virupas; in odd Navamsha: 15 virupas (max 30).
# Female planets (Moon, Venus) in even sign: 15 virupas; in even Navamsha: 15 virupas (max 30).
# Neutral planets (Mercury, Saturn) in odd sign: 15 virupas; in odd Navamsha: 15 virupas (max 30).

_MALE_GRAHAS = frozenset(["Sun", "Mars", "Jupiter"])
_FEMALE_GRAHAS = frozenset(["Moon", "Venus"])


def calc_ojhayugma_bala(planet: PlanetCtx) -> float:
    """Return Ojhayugma Bala in virupas (0, 15, or 30)."""
    # 1. Rasi odd/even
    is_odd_rasi = (planet.sign_index % 2) == 1

    # 2. Navamsha odd/even
    nav_idx = int(planet.degree_in_sign // (30.0 / 9.0))
    element_start = {1: 1, 5: 1, 9: 1, 2: 10, 6: 10, 10: 10, 3: 7, 7: 7, 11: 7, 4: 4, 8: 4, 12: 4}
    d9_sign = ((element_start[planet.sign_index] - 1 + nav_idx) % 12) + 1
    is_odd_nav = (d9_sign % 2) == 1

    score = 0.0
    if planet.name in _MALE_GRAHAS:
        if is_odd_rasi: score += 15.0
        if is_odd_nav:  score += 15.0
    elif planet.name in _FEMALE_GRAHAS:
        if not is_odd_rasi: score += 15.0
        if not is_odd_nav:  score += 15.0
    else:  # Mercury, Saturn
        if is_odd_rasi: score += 15.0
        if is_odd_nav:  score += 15.0

    return score


# ---------------------------------------------------------------------------
# 4. KENDRADI BALA — House Quadrant/Succedent/Cadent Strength
# ---------------------------------------------------------------------------
# BPHS Ch. 27, Sloka 13:
# Kendra (1, 4, 7, 10) = 60 virupas.
# Panapara (2, 5, 8, 11) = 30 virupas.
# Apoklima (3, 6, 9, 12) = 15 virupas.

def _planet_house_number(planet: PlanetCtx, houses: list) -> int:
    sign_to_house: Dict[int, int] = {h.sign_index: h.house_number for h in houses}
    return sign_to_house.get(planet.sign_index, 1)


def calc_kendradi_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """Return Kendradi Bala in virupas (15, 30, or 60)."""
    house_num = _planet_house_number(planet, ctx.houses)
    if house_num in (1, 4, 7, 10):
        return 60.0
    if house_num in (2, 5, 8, 11):
        return 30.0
    return 15.0


# ---------------------------------------------------------------------------
# 5. DREKKANA BALA — Decanate Gender Strength
# ---------------------------------------------------------------------------
# BPHS Ch. 27, Sloka 14:
# Male planets (Sun, Mars, Jupiter) in 1st decanate (0-10°) = 15 virupas.
# Neutral planets (Mercury, Saturn) in 2nd decanate (10-20°) = 15 virupas.
# Female planets (Moon, Venus) in 3rd decanate (20-30°) = 15 virupas.

def calc_drekkana_bala(planet: PlanetCtx) -> float:
    """Return Drekkana Bala in virupas (0 or 15)."""
    deg = planet.degree_in_sign
    if planet.name in _MALE_GRAHAS:
        return 15.0 if deg < 10.0 else 0.0
    if planet.name in _FEMALE_GRAHAS:
        return 15.0 if deg >= 20.0 else 0.0
    return 15.0 if 10.0 <= deg < 20.0 else 0.0


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def calc_sthana_bala(planet: PlanetCtx, ctx: ChartCtx) -> SthanaBalaSub:
    """Compute all five Sthana Bala sub-components and return the aggregate."""
    uchcha = calc_uchcha_bala(planet)
    sapta = calc_saptavargaja_bala(planet, ctx)
    ojha = calc_ojhayugma_bala(planet)
    kendradi = calc_kendradi_bala(planet, ctx)
    drekkana = calc_drekkana_bala(planet)
    total = uchcha + sapta + ojha + kendradi + drekkana
    return SthanaBalaSub(
        uchcha_bala=round(uchcha, 4),
        saptavargaja_bala=round(sapta, 4),
        ojhayugma_bala=round(ojha, 4),
        kendradi_bala=round(kendradi, 4),
        drekkana_bala=round(drekkana, 4),
        total=round(total, 4),
    )
