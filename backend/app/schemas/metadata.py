"""Metadata schemas for GET /api/v1/metadata."""

from typing import List, Dict
from pydantic import BaseModel, Field


class AyanamsaOption(BaseModel):
    id: int
    name: str
    description: str
    is_default: bool = False


class HouseSystemOption(BaseModel):
    id: int
    name: str
    description: str
    is_default: bool = False


class LanguageOption(BaseModel):
    code: str
    name: str
    native_name: str


class ChartCapability(BaseModel):
    id: str
    name: str
    description: str


class MetadataResponse(BaseModel):
    engine: str = "XALEN Ephemeris & Vedic Astrological Engine"
    version: str = "1.0.0"
    verified_phases: List[str] = Field(default_factory=lambda: ["Phase A", "Phase B", "Phase C", "Phase D"])
    dasa_year_convention: str = "Julian Year (365.25 Days / 120 Years = 43,830 Days)"
    kp_sub_divisions: int = 249
    supported_ayanamsas: List[AyanamsaOption]
    supported_house_systems: List[HouseSystemOption]
    supported_languages: List[LanguageOption]
    chart_capabilities: List[ChartCapability]
    limitations: List[str]
