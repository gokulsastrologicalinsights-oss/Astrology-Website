"""Dig Bala — Directional Strength.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 27, Sloka 15-18.

Planetary directions of maximum strength (Dig Bala = 60 virupas):
- Jupiter & Mercury: 1st house cusp (Lagna / East)  → Nirbala point = 7th house cusp (Descendant)
- Sun & Mars: 10th house cusp (Midheaven / South)   → Nirbala point = 4th house cusp (Nadir)
- Saturn: 7th house cusp (Descendant / West)        → Nirbala point = 1st house cusp (Lagna)
- Moon & Venus: 4th house cusp (Nadir / North)       → Nirbala point = 10th house cusp (Midheaven)

Formula:
The angular difference between the planet's longitude and its Nirbala point:
    diff = abs(planet_longitude - nirbala_point) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    dig_bala = diff / 3.0

At potent point (diff = 180° from Nirbala): Dig Bala = 180 / 3 = 60 virupas.
At Nirbala point (diff = 0°): Dig Bala = 0 / 3 = 0 virupas.
All intermediate longitudes receive exact continuous virupas proportional to arc distance.
"""

from __future__ import annotations

from typing import Dict
from app.services.shadbala_engine.models import ChartCtx, PlanetCtx


def calc_dig_bala(planet: PlanetCtx, ctx: ChartCtx) -> float:
    """Compute Dig Bala (Directional Strength) in virupas (0 to 60) per BPHS continuous formula."""
    asc_deg = ctx.ascendant.degree

    # Cardinal reference points (Lagna, Nadir, Descendant, Midheaven)
    h1_point = asc_deg
    h4_point = (asc_deg + 90.0) % 360.0
    h7_point = (asc_deg + 180.0) % 360.0
    h10_point = (asc_deg + 270.0) % 360.0

    nirbala_map: Dict[str, float] = {
        "Jupiter": h7_point,
        "Mercury": h7_point,
        "Sun":     h4_point,
        "Mars":    h4_point,
        "Saturn":  h1_point,
        "Moon":    h10_point,
        "Venus":   h10_point,
    }

    nirbala = nirbala_map.get(planet.name)
    if nirbala is None:
        return 0.0

    diff = abs(planet.longitude - nirbala) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff

    dig_bala = diff / 3.0
    return round(max(0.0, min(60.0, dig_bala)), 4)
