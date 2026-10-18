"""Pydantic schemas for Vedic Yoga calculation and analysis."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import CalculationMetadata


class YogaConditionItem(BaseModel):
    condition: str = Field(..., description="Description of the rule condition")
    passed: bool = Field(..., description="Whether this specific condition was satisfied")
    detail: str = Field(..., description="Actual evaluated chart values supporting the condition status")


class YogaDetail(BaseModel):
    id: str = Field(..., description="Machine-readable unique identifier for the yoga")
    name: str = Field(..., description="Sanskrit / English name of the Yoga")
    name_tamil: str = Field(..., description="Tamil name of the Yoga")
    category: str = Field(
        ...,
        description="Category: Major Classical, Raja Yoga, Dhana Yoga, Panch Mahapurusha, Lunar/Solar, Vipareeta Raja, Parivartana, Avayoga"
    )
    status: str = Field(
        ...,
        description="Status: Qualifying, Cancelled, or Not Qualifying"
    )
    is_qualifying: bool = Field(..., description="True if the yoga is fully operative and uncancelled")
    planets_involved: List[str] = Field(default_factory=list, description="Planets forming or triggering this yoga")
    relevant_houses: List[int] = Field(default_factory=list, description="House numbers (1-12) involved")
    conditions: List[YogaConditionItem] = Field(default_factory=list, description="Detailed condition checklist")
    short_interpretation: str = Field(..., description="Concise traditional effect and life significance")
    classical_definition: str = Field(..., description="Traditional textual rule and formation criteria")
    classical_reference: str = Field(
        ...,
        description="Textual authority (e.g., BPHS, Phaladeepika, Saravali, 300 Important Combinations)"
    )
    verification_status: str = Field(
        ...,
        description="Rule verification status: Verified, Corrected from Reference, or Classical Independent Implementation"
    )
    cancellation_reason: Optional[str] = Field(
        None,
        description="Explanation if the yoga was cancelled by a classical Bhanga rule"
    )


class YogaSummary(BaseModel):
    total_evaluated: int = Field(..., description="Total number of yoga rules evaluated")
    total_qualifying: int = Field(..., description="Total number of operative qualifying yogas")
    raja_yogas_count: int = Field(..., description="Count of qualifying Raja Yogas")
    dhana_yogas_count: int = Field(..., description="Count of qualifying Dhana (wealth) Yogas")
    mahapurusha_yogas_count: int = Field(..., description="Count of qualifying Panch Mahapurusha Yogas")
    vipareeta_yogas_count: int = Field(..., description="Count of qualifying Vipareeta Raja Yogas")
    other_classical_count: int = Field(..., description="Count of other qualifying classical yogas")
    cancelled_count: int = Field(..., description="Count of yogas cancelled by classical Bhanga rules")


class VedicYogaResponse(BaseModel):
    metadata: Optional[CalculationMetadata] = None
    summary: YogaSummary
    yogas: List[YogaDetail] = Field(default_factory=list)
