"""Schemas for Love vs Arranged Marriage Predictor.

Evaluates whether a horoscope indicates Love Marriage, Arranged Marriage,
or Love-cum-Arranged (love marriage with parental blessing) using classical
Vedic signatures, KP Cuspal Sub-Lord (CSL) rules, and Siddhayogi Sivadasan Ravi Nadi principles.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import BirthInput


class LoveOrArrangedRequest(BaseModel):
    """Input payload for Love vs Arranged Marriage determination."""
    birth: BirthInput
    name: Optional[str] = Field(None, description="Native's name for report header")
    gender: Optional[str] = Field("male", description="'male', 'female', or 'other'")
    chart_id: Optional[str] = Field(None, description="Optional UUID of a saved horoscope")


class LoveOrArrangedFactor(BaseModel):
    """Detailed astrological factor contributing to the love vs arranged verdict."""
    category: str = Field(..., description="E.g., '5th & 7th House Link', 'Planetary Attraction', 'KP Sub-Lord Rule', 'Family & Elders Blessing'")
    title_en: str
    title_ta: str
    influence: str = Field(..., description="'LOVE', 'ARRANGED', or 'NEUTRAL'")
    description_en: str
    description_ta: str
    weight: int = Field(..., ge=1, le=5, description="Significance weight from 1 to 5")


class LoveOrArrangedResponse(BaseModel):
    """Simplified, definitive output indicating Love vs Arranged Marriage alone."""
    native_name: Optional[str] = None
    native_gender: str
    birth_summary: str

    # Primary Clean Verdict
    verdict: str = Field(..., description="'Love Marriage', 'Arranged Marriage', or 'Love-cum-Arranged Marriage'")
    verdict_ta: str = Field(..., description="'காதல் திருமணம்', 'பெற்றோரால் நிச்சயிக்கப்பட்ட திருமணம்', or 'பெற்றோர் சம்மதத்துடன் காதல் திருமணம்'")
    verdict_badge: str = Field(..., description="'LOVE', 'ARRANGED', or 'LOVE_ARRANGED'")

    # Percentage Probability (Sums to 100)
    love_percentage: int = Field(..., ge=0, le=100)
    arranged_percentage: int = Field(..., ge=0, le=100)

    # Simple 1-2 sentence high-level summary
    summary_en: str
    summary_ta: str

    # Family Support / Elders' blessing status
    family_support: str
    family_support_ta: str

    # Key Astrological Drivers
    key_factors: List[LoveOrArrangedFactor] = Field(default_factory=list)

    # Technical Details for Astrologers / Curious Users
    fifth_house_summary: str
    seventh_house_summary: str
    kp_sublord_summary: Optional[str] = None
    venus_summary: str

    calculated_at: str
