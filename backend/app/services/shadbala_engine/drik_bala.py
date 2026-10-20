"""Drik Bala — Aspectual Strength.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 27, Sloka 39-44.

Drik Bala represents the cumulative aspectual influence (Drishti Pinda)
received by a graha from all other classical grahas:
- Aspects from natural benefics (Jupiter, Venus, Mercury) increase strength (+).
- Aspects from natural malefics (Sun, Mars, Saturn) reduce strength (-).
- Moon is treated as benefic if waxing (Paksha elongation <= 180°), or malefic if waning.

Continuous Drishti curve across 30° to 300° (BPHS Ch. 27, Slokas 39-42):
- 0° to 30°: Aspect = 0
- 30° to 60°: Aspect = (θ - 30) * 0.5 (reaches 15 shashtiamsas at 60°)
- 60° to 90°: Aspect = 15 + (θ - 60) * 1.0 (reaches 45 shashtiamsas at 90°)
- 90° to 120°: Aspect = 45 - (θ - 90) * 0.5 (drops to 30 shashtiamsas at 120°)
- 120° to 150°: Aspect = 30 - (θ - 120) * 1.0 (drops to 0 shashtiamsas at 150°)
- 150° to 180°: Aspect = (θ - 150) * 2.0 (reaches 60 shashtiamsas / full aspect at 180°)
- 180° to 300°: Aspect = (300 - θ) / 2.0 (drops from 60 shashtiamsas at 180° to 0 at 300°)
- 300° to 360°: Aspect = 0

Vishesha Drishti (Special full aspects):
- Mars: 4th (90°) and 8th (210°) houses.
- Jupiter: 5th (120°) and 9th (240°) houses.
- Saturn: 3rd (60°) and 10th (270°) houses.

Per BPHS:
    Drik Bala = (Benefic Aspect Total - Malefic Aspect Total) / 4.0
"""

from __future__ import annotations

from typing import Dict
from app.services.shadbala_engine.models import ChartCtx, PlanetCtx

_NATURAL_BENEFICS = frozenset(["Jupiter", "Venus", "Mercury"])
_NATURAL_MALEFICS = frozenset(["Sun", "Mars", "Saturn"])


def _calculate_general_drishti(diff_deg: float) -> float:
    """Calculate BPHS continuous general Drishti (0 to 60 shashtiamsas)."""
    diff = diff_deg % 360.0

    if diff < 30.0 or diff >= 300.0:
        return 0.0
    elif 30.0 <= diff < 60.0:
        return (diff - 30.0) * 0.5
    elif 60.0 <= diff < 90.0:
        return 15.0 + (diff - 60.0) * 1.0
    elif 90.0 <= diff < 120.0:
        return 45.0 - (diff - 90.0) * 0.5
    elif 120.0 <= diff < 150.0:
        return 30.0 - (diff - 120.0) * 1.0
    elif 150.0 <= diff < 180.0:
        return (diff - 150.0) * 2.0
    else:  # 180.0 <= diff < 300.0
        return (300.0 - diff) / 2.0


def _calculate_special_drishti(aspecting_name: str, diff_deg: float) -> float:
    """Calculate special full aspect (Vishesha Drishti) cast by Mars, Jupiter, or Saturn."""
    diff = diff_deg % 360.0

    if aspecting_name == "Mars":
        # 4th house (90°) and 8th house (210°) within ±15° orb
        if 75.0 <= diff <= 105.0:
            return 60.0 * (1.0 - abs(diff - 90.0) / 15.0)
        if 195.0 <= diff <= 225.0:
            return 60.0 * (1.0 - abs(diff - 210.0) / 15.0)

    elif aspecting_name == "Jupiter":
        # 5th house (120°) and 9th house (240°) within ±15° orb
        if 105.0 <= diff <= 135.0:
            return 60.0 * (1.0 - abs(diff - 120.0) / 15.0)
        if 225.0 <= diff <= 255.0:
            return 60.0 * (1.0 - abs(diff - 240.0) / 15.0)

    elif aspecting_name == "Saturn":
        # 3rd house (60°) and 10th house (270°) within ±15° orb
        if 45.0 <= diff <= 75.0:
            return 60.0 * (1.0 - abs(diff - 60.0) / 15.0)
        if 255.0 <= diff <= 285.0:
            return 60.0 * (1.0 - abs(diff - 270.0) / 15.0)

    return 0.0


def calc_drik_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """Compute Drik Bala (Aspectual Strength) in virupas.

    Iterates through all 6 other classical grahas, computes aspects cast upon
    `planet`, and returns (benefic_aspects - malefic_aspects) / 4.0.
    """
    benefic_sum = 0.0
    malefic_sum = 0.0

    # Determine Moon's benefic status (waxing = benefic, waning = malefic)
    moon_is_benefic = True
    if ctx.moon_longitude is not None and ctx.sun_longitude is not None:
        elongation = (ctx.moon_longitude - ctx.sun_longitude) % 360.0
        moon_is_benefic = elongation <= 180.0

    for other in ctx.planets:
        if other.name == planet.name:
            continue
        if other.name not in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            continue

        # Forward arc from other (aspecting) to planet (receiving)
        forward_diff = (planet.longitude - other.longitude) % 360.0

        general = _calculate_general_drishti(forward_diff)
        special = _calculate_special_drishti(other.name, forward_diff)
        aspect_val = max(general, special)

        # Categorize benefic vs malefic
        is_benefic = False
        if other.name in _NATURAL_BENEFICS:
            is_benefic = True
        elif other.name == "Moon":
            is_benefic = moon_is_benefic
        elif other.name in _NATURAL_MALEFICS:
            is_benefic = False

        if is_benefic:
            benefic_sum += aspect_val
        else:
            malefic_sum += aspect_val

    # BPHS formula: Net Drik Bala = (Benefic Drishti - Malefic Drishti) / 4.0
    net_drik = (benefic_sum - malefic_sum) / 4.0
    return round(net_drik, 4)
