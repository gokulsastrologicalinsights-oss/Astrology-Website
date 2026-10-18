"""Pydantic schemas for Nabhasha Yoga calculations."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput, CalculationMetadata


class NabhashaYogaDetail(BaseModel):
    name: str = Field(..., description="Sanskrit name of the Nabhasha Yoga")
    category: str = Field(..., description="Classification category: Ashraya, Dala, Aakriti, or Sankhya")
    formation_rule: str = Field(..., description="Classical formation condition per BPHS")
    qualifying_houses: List[int] = Field(default_factory=list, description="Houses occupied or involved in formation")
    qualifying_signs: List[int] = Field(default_factory=list, description="Zodiac signs occupied (1-12)")
    planets_involved: List[str] = Field(default_factory=list, description="Names of the planets forming this yoga")
    description: str = Field(..., description="Traditional astrological significance and interpretation")
    is_primary: bool = Field(False, description="Whether this is the primary operative yoga under classical precedence rules")


class NabhashaDistribution(BaseModel):
    distinct_signs_count: int = Field(..., description="Number of distinct signs occupied by the 7 classical planets (1-7)")
    distinct_houses_count: int = Field(..., description="Number of distinct houses occupied (1-7)")
    planets_by_house: Dict[int, List[str]] = Field(default_factory=dict, description="Mapping of house number to planets")
    planets_by_sign: Dict[int, List[str]] = Field(default_factory=dict, description="Mapping of sign index to planets")
    kendra_planets: List[str] = Field(default_factory=list, description="Planets situated in Kendra houses (1, 4, 7, 10)")
    panaphara_planets: List[str] = Field(default_factory=list, description="Planets situated in Panaphara houses (2, 5, 8, 11)")
    apoklima_planets: List[str] = Field(default_factory=list, description="Planets situated in Apoklima houses (3, 6, 9, 12)")
    trikona_planets: List[str] = Field(default_factory=list, description="Planets situated in Trikona houses (1, 5, 9)")


class NabhashaResponse(BaseModel):
    metadata: Optional[CalculationMetadata] = None
    distribution: NabhashaDistribution
    primary_yoga: Optional[NabhashaYogaDetail] = None
    all_qualifying_yogas: List[NabhashaYogaDetail] = Field(default_factory=list)
    classical_reference: str = Field(
        "Brihat Parashara Hora Shastra, Chapter 35 (Nabhasha Yogas); Brihat Jataka, Chapter 12",
        description="Textual authority"
    )
