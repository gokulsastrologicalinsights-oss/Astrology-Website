"""Pydantic schemas for the Shadbala (Six-fold Planetary Strength) engine.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 23: Shadbala and Bhava Bala.
- Units: virupas (base unit), rupas (= virupas / 60).
- Seven grahas evaluated: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
  Rahu and Ketu are excluded — they are shadow planets (chaya grahas) and
  BPHS does not prescribe Shadbala for them.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import CalculationMetadata


# ---------------------------------------------------------------------------
# Minimum required Shadbala strengths (virupas) per BPHS Ch. 23, Sloka 2-4.
# ---------------------------------------------------------------------------
SHADBALA_REQUIRED_VIRUPAS: Dict[str, float] = {
    "Sun":     390.0,
    "Moon":    360.0,
    "Mars":    300.0,
    "Mercury": 420.0,
    "Jupiter": 390.0,
    "Venus":   330.0,
    "Saturn":  300.0,
}


class SthanaBalaSub(BaseModel):
    """Sub-components of Sthana Bala (Positional Strength)."""
    uchcha_bala: float = Field(..., description="Exaltation strength (0-60 virupas)")
    saptavargaja_bala: float = Field(..., description="Seven-divisional chart strength (0-45 virupas)")
    ojhayugma_bala: float = Field(..., description="Odd/Even sign placement strength (0-30 virupas)")
    kendradi_bala: float = Field(..., description="Quadrant/Succedent/Cadent house strength (15/30/60 virupas)")
    drekkana_bala: float = Field(..., description="Decanate gender strength (0 or 15 virupas)")
    total: float = Field(..., description="Sum of all Sthana Bala sub-components (virupas)")


class KalaBalaSub(BaseModel):
    """Sub-components of Kala Bala (Temporal Strength)."""
    nathonnatha_bala: float = Field(..., description="Day/Night rulership strength (0-60 virupas)")
    paksha_bala: float = Field(..., description="Lunar fortnight strength (0-60 virupas)")
    tribhaga_bala: float = Field(..., description="Three-part-of-day strength (0 or 15 virupas)")
    abda_bala: float = Field(..., description="Solar year lord strength (0 or 15 virupas)")
    masa_bala: float = Field(..., description="Solar month lord strength (0 or 30 virupas)")
    vara_bala: float = Field(..., description="Weekday lord strength (0 or 45 virupas)")
    hora_bala: float = Field(..., description="Planetary hour lord strength (0 or 60 virupas)")
    ayana_bala: float = Field(..., description="Solstice-based strength (20/30/40 virupas)")
    total: float = Field(..., description="Sum of all Kala Bala sub-components (virupas)")


class PlanetShadbalaDetail(BaseModel):
    """Full Shadbala breakdown for one graha."""
    planet: str = Field(..., description="Graha name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)")

    # --- Six Balas ---
    sthana_bala: SthanaBalaSub = Field(..., description="1. Positional strength and its sub-components")
    dig_bala: float = Field(..., description="2. Directional strength (0-60 virupas)")
    kala_bala: KalaBalaSub = Field(..., description="3. Temporal strength and its sub-components")
    cheshta_bala: float = Field(..., description="4. Motional/Aspectual strength (0-60 virupas)")
    naisargika_bala: float = Field(..., description="5. Natural/Inherent strength (fixed per BPHS)")
    drik_bala: float = Field(..., description="6. Aspectual strength (variable, can be negative)")

    # --- Totals ---
    total_virupas: float = Field(..., description="Sum of all six Balas in virupas")
    total_rupas: float = Field(..., description="total_virupas / 60")
    required_virupas: float = Field(..., description="Minimum required Shadbala per BPHS Ch. 23")
    ratio: float = Field(..., description="total_virupas / required_virupas; ≥ 1.0 means planet is strong")
    is_strong: bool = Field(..., description="True if ratio ≥ 1.0")
    rank: int = Field(..., description="Strength rank 1 (strongest) through 7 (weakest)")


class ShadbalaResponse(BaseModel):
    """Complete Shadbala response for all seven classical grahas."""
    metadata: Optional[CalculationMetadata] = None
    planets: List[PlanetShadbalaDetail] = Field(
        ...,
        description="Shadbala details for the seven classical grahas, sorted by rank (strongest first)",
    )
    strongest_planet: str = Field(..., description="Graha with rank 1 (highest total virupas)")
    weakest_planet: str = Field(..., description="Graha with rank 7 (lowest total virupas)")
    calculation_notes: List[str] = Field(
        default_factory=list,
        description="Methodological notes, simplifications, and known limitations",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "strongest_planet": "Sun",
                "weakest_planet": "Saturn",
            }
        }
    }
