"""Cheshta Bala — Motional Strength.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 23, Sloka 33-38.

Eight motional states (Gatis) of the Tara Grahas (Mars, Mercury, Jupiter, Venus, Saturn):
1. Vakra (Retrograde) — Maximum motional strength (60 virupas).
2. Vikala / Stationary (speed near 0, |speed| < 0.1 deg/day) — (45 virupas).
3. Chara / Direct Fast (|speed| >= average mean daily motion) — (30 virupas).
4. Manda / Direct Slow (|speed| < average mean daily motion) — (15 virupas).

Sun and Moon:
- Luminaries never exhibit retrograde motion.
- Classical BPHS prescribes fixed moderate motional strength (30 virupas) as
  their motion is governed by Solstitial (Ayana) and Lunar Phase (Paksha) balas.
"""

from __future__ import annotations

from typing import Dict
from app.services.shadbala_engine.models import PlanetCtx

# Mean daily geocentric motions (degrees per day) for the 5 tara grahas
_MEAN_DAILY_MOTION: Dict[str, float] = {
    "Mars": 0.524,
    "Mercury": 1.200,
    "Jupiter": 0.083,
    "Venus": 1.000,
    "Saturn": 0.033,
}


def calc_cheshta_bala(planet: PlanetCtx) -> float:
    """Compute Cheshta Bala in virupas (0 to 60)."""
    # Sun and Moon have fixed 30 virupas
    if planet.name in ("Sun", "Moon"):
        return 30.0

    # If retrograde: full 60 virupas per BPHS
    if planet.is_retrograde or planet.speed_deg_per_day < 0.0:
        return 60.0

    speed = abs(planet.speed_deg_per_day)

    # Stationary (speed near zero, preparing to station/retrograde)
    if speed < 0.1:
        return 45.0

    # Compare against mean daily motion
    mean_speed = _MEAN_DAILY_MOTION.get(planet.name, 0.5)
    if speed >= mean_speed:
        return 30.0
    else:
        return 15.0
