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


class SpouseOriginProfile(BaseModel):
    """Details regarding the direction and introduction pathway of the spouse (2-3 concise points)."""
    direction_en: str = Field(..., description="Geographical direction of the spouse, e.g., 'East / North-East'")
    direction_ta: str = Field(..., description="துணைவர் வரும் திசை, எ.கா. 'கிழக்கு / வடகிழக்கு'")
    distance_type_en: str = Field(..., description="Estimated distance category: nearby, moderate, or distant/relocated")
    distance_type_ta: str = Field(..., description="தொலைவு மதிப்பீடு: உள்ளூர், நடுத்தர தூரம் அல்லது வெளிவட்டம்/இடம் பெயர்ந்தவர்")
    source_channel_en: str = Field(..., description="Primary meeting sphere: workplace, education, travel, mutual friends, or family network")
    source_channel_ta: str = Field(..., description="அறிமுக களம்: தொழில், கல்விக்கூடம், நண்பர்கள் வட்டம் அல்லது குடும்பத்தினர்")
    points_en: List[str] = Field(default_factory=list, description="2 to 3 concise bullet points detailing how the bride/groom comes from")
    points_ta: List[str] = Field(default_factory=list, description="துணைவர் வரும் வழிமுறை பற்றிய 2 முதல் 3 முக்கிய குறிப்புகள்")


class LifePartnerProfile(BaseModel):
    """Astrological portrait of who the life partner will be."""
    nature_temperament_en: str = Field(..., description="Personality traits, emotional temperament, and core disposition")
    nature_temperament_ta: str = Field(..., description="குணநலன்கள் மற்றும் சுபாவம்")
    physical_features_en: str = Field(..., description="Physical stature, appearance, and demeanor")
    physical_features_ta: str = Field(..., description="தோற்றம் மற்றும் உடல்வாகு")
    career_background_en: str = Field(..., description="Professional inclination or vocational background")
    career_background_ta: str = Field(..., description="கல்வி மற்றும் தொழில் பின்னணி")
    summary_en: str = Field(..., description="Comprehensive spousal identity summary in English")
    summary_ta: str = Field(..., description="வாழ்க்கைத் துணைவர் பற்றிய விரிவான தமிழ் விளக்கம்")


class LoveInitiationTiming(BaseModel):
    """Timing and astrological circumstances when love or courtship started/blossomed."""
    estimated_age_range: str = Field(..., description="E.g., '20 – 23 years' or '22 – 25 years'")
    approximate_period: str = Field(..., description="E.g., '2016 – 2019' or running calendar period")
    trigger_dasha_en: str = Field(..., description="Planetary dasha/antardasha triggering romantic ignition")
    trigger_dasha_ta: str = Field(..., description="காதல் ஈர்ப்பை தூண்டிய தசா/புத்தி காலம்")
    context_en: str = Field(..., description="Life context and circumstances during courtship genesis")
    context_ta: str = Field(..., description="காதல் மலர்ந்த வாழ்க்கை சூழல் மற்றும் அறிமுக பின்னணி")


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

    # 3 Specialized In-Depth Predictors requested by users
    spouse_origin: Optional[SpouseOriginProfile] = Field(
        None, description="2 to 3 concise points detailing the direction and introduction pathway of the bride/groom"
    )
    life_partner: Optional[LifePartnerProfile] = Field(
        None, description="Astrological portrait of who the life partner will be"
    )
    love_timing: Optional[LoveInitiationTiming] = Field(
        None, description="Estimated age window and astrological timing when love started or blossoms"
    )

    # Technical Details for Astrologers / Curious Users
    fifth_house_summary: str
    seventh_house_summary: str
    kp_sublord_summary: Optional[str] = None
    venus_summary: str

    calculated_at: str
