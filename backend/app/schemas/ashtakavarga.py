"""Pydantic schemas for Ashtakavarga calculations."""

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


class AshtakavargaResponse(BaseModel):
    metadata: Optional[CalculationMetadata] = None
    bhinnashtakavarga: Dict[str, PlanetBavDetail] = Field(..., description="BAV grids for the 7 classical grahas")
    sarvashtakavarga: SavDetail = Field(..., description="Aggregated 7-planet Sarvashtakavarga")
    lagna_sign_index: int = Field(..., description="Ascendant sign index (1-12)")
    validation_status: str = Field("PASSED", description="Validation status against canonical 337 invariant")
    classical_reference: str = Field(
        "Brihat Parashara Hora Shastra, Chapters 66–73 (Ashtakavarga System)",
        description="Textual authority"
    )
