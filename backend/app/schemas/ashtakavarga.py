"""Pydantic schemas for Ashtakavarga, Prastara, and Kaksha calculations."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.common import CalculationMetadata


class PlanetBavDetail(BaseModel):
    planet: str = Field(..., description="Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)")
    sign_bindus: Dict[int, int] = Field(..., description="Bindu count per zodiac sign index (1=Aries .. 12=Pisces)")
    house_bindus: Dict[int, int] = Field(..., description="Bindu count per house from Lagna (1..12)")
    total_bindus: int = Field(..., description="Sum of bindus across all 12 signs")
    expected_total: int = Field(..., description="Classical invariant total per BPHS")
    trikona_reduced: Optional[Dict[int, int]] = Field(None, description="Bindus after Trikona Shodhana")
    ekadhipatya_reduced: Optional[Dict[int, int]] = Field(None, description="Bindus after Ekadhipatya Shodhana")
    rashi_pinda: Optional[int] = Field(None, description="Rashi Pinda (sign multiplier sum)")
    graha_pinda: Optional[int] = Field(None, description="Graha Pinda (planet multiplier sum)")
    shodhya_pinda: Optional[int] = Field(None, description="Total Shodhya Pinda (Rashi Pinda + Graha Pinda)")


class SavDetail(BaseModel):
    sign_bindus: Dict[int, int] = Field(..., description="Aggregated Sarvashtakavarga bindus per sign (1-12)")
    house_bindus: Dict[int, int] = Field(..., description="Aggregated Sarvashtakavarga bindus per house from Lagna (1-12)")
    total_bindus: int = Field(337, description="Grand total across 12 signs (invariant 337)")
    average_per_sign: float = Field(28.08, description="Mathematical average bindus per sign (337/12)")
    auspicious_signs: List[int] = Field(default_factory=list, description="Signs with bindus >= 28")
    inauspicious_signs: List[int] = Field(default_factory=list, description="Signs with bindus < 28")


# ---------------------------------------------------------------------------
# Prastara Ashtakavarga Schemas
# ---------------------------------------------------------------------------

class PrastaraRow(BaseModel):
    """Row in Prastara matrix representing one donor's contributions across 12 signs."""
    contributor: str = Field(..., description="Donor name: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna")
    sign_bindus: Dict[int, int] = Field(..., description="0 or 1 for each sign (1=Aries .. 12=Pisces)")
    total_contributions: int = Field(..., description="Total bindus contributed across 12 signs by this donor")


class PrastaraDetail(BaseModel):
    """Complete 8-donor by 12-sign Prastara matrix for one target graha."""
    planet: str = Field(..., description="Target graha name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)")
    rows: List[PrastaraRow] = Field(..., description="8 rows ordered by classical Kaksha speed sequence")
    sign_totals: Dict[int, int] = Field(..., description="Column totals per sign (1-12), exactly matching BAV bindus")
    total_bindus: int = Field(..., description="Grand sum of all bindus in this matrix (matches BAV expected total)")


class PrastaraResponse(BaseModel):
    """API response model for complete Prastarashtakavarga of all 7 classical planets."""
    metadata: Optional[CalculationMetadata] = None
    prastara: Dict[str, PrastaraDetail] = Field(..., description="Prastara matrices keyed by target graha")
    grand_total_bindus: int = Field(337, description="Sum of bindus across all 7 matrices (invariant 337)")
    validation_status: str = Field("PASSED", description="Validation status against BAV totals and 337 invariant")


# ---------------------------------------------------------------------------
# Kaksha Transit Schemas
# ---------------------------------------------------------------------------

class KakshaDivisionInfo(BaseModel):
    """One 3°45' Kaksha division within a zodiac sign."""
    kaksha_number: int = Field(..., description="1-indexed Kaksha position within sign (1 to 8)")
    lord: str = Field(..., description="Kaksha ruler: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna")
    start_degree: float = Field(..., description="Starting degree in sign (0.0 to 26.25)")
    end_degree: float = Field(..., description="Ending degree in sign (3.75 to 30.0)")
    range_display: str = Field(..., description="Formatted degree span, e.g. '00°00′ – 03°45′'")
    has_bindu: bool = Field(..., description="True if donor contributed a bindu (1) in target planet's Prastara")
    auspicious: bool = Field(..., description="True if has_bindu is True (favorable transit window)")


class PlanetKakshaSignDetail(BaseModel):
    """Eight Kaksha divisions for a specific zodiac sign and planet."""
    sign_index: int = Field(..., description="Zodiac sign index (1=Aries .. 12=Pisces)")
    sign_name: str = Field(..., description="Sign name in English")
    divisions: List[KakshaDivisionInfo] = Field(..., description="All 8 Kaksha divisions in this sign")
    total_bindus: int = Field(..., description="Sum of auspicious Kakshas in this sign (matches BAV sign bindus)")


class KakshaTransitQuery(BaseModel):
    """Query model for evaluating Kaksha transit at a specific zodiac position."""
    transiting_planet: str = Field(..., description="Transiting graha name (e.g. Jupiter, Saturn, Mars)")
    transit_longitude: Optional[float] = Field(None, description="Sidereal transit longitude (0.0 to 360.0°)")
    transit_sign_index: Optional[int] = Field(None, description="Transit sign index (1-12) if longitude not given")
    transit_degree_in_sign: Optional[float] = Field(None, description="Degree in sign (0.0 to 30.0°) if longitude not given")


class KakshaTransitResult(BaseModel):
    """Detailed Kaksha evaluation for a transiting planet."""
    transiting_planet: str = Field(..., description="Name of the transiting graha")
    sign_index: int = Field(..., description="Sign index (1-12) occupied by transit")
    sign_name: str = Field(..., description="Sign name occupied by transit")
    degree_in_sign: float = Field(..., description="Degree within sign (0.0 to 30.0°)")
    kaksha_number: int = Field(..., description="Kaksha division (1 to 8)")
    kaksha_lord: str = Field(..., description="Ruler of the active Kaksha division")
    kaksha_range: str = Field(..., description="Formatted degree span of the Kaksha")
    has_bindu: bool = Field(..., description="True if natal Prastara contains a bindu (1) in this Kaksha")
    effect: str = Field(..., description="'Auspicious' if has_bindu else 'Inauspicious'")
    interpretation: str = Field(..., description="Concise classical transit interpretation")


class KakshaResponse(BaseModel):
    """Full 96-Kaksha grid (12 signs × 8 Kakshas) for all 7 classical grahas."""
    metadata: Optional[CalculationMetadata] = None
    kaksha_grids: Dict[str, List[PlanetKakshaSignDetail]] = Field(
        ...,
        description="Kaksha breakdowns for the 7 classical grahas across all 12 signs",
    )


# ---------------------------------------------------------------------------
# Master Ashtakavarga Combined Response
# ---------------------------------------------------------------------------

class AshtakavargaResponse(BaseModel):
    metadata: Optional[CalculationMetadata] = None
    bhinnashtakavarga: Dict[str, PlanetBavDetail] = Field(..., description="BAV grids for the 7 classical grahas")
    sarvashtakavarga: SavDetail = Field(..., description="Aggregated 7-planet Sarvashtakavarga")
    lagna_sign_index: int = Field(..., description="Ascendant sign index (1-12)")
    validation_status: str = Field("PASSED", description="Validation status against canonical 337 invariant")
    classical_reference: str = Field(
        "Brihat Parashara Hora Shastra, Chapters 66–73 (Ashtakavarga System)",
        description="Textual authority",
    )
    prastara: Optional[Dict[str, PrastaraDetail]] = Field(
        None,
        description="Complete 8-donor by 12-sign Prastara matrices for all 7 grahas",
    )
    kaksha_grids: Optional[Dict[str, List[PlanetKakshaSignDetail]]] = Field(
        None,
        description="Complete 96-Kaksha grids for all 7 grahas across all 12 signs",
    )
