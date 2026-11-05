"""Instant Revelation & Astrologer Teleprompter Pydantic Schemas.

Designed for instant client intake where an astrologer can immediately speak out
accurate, verified past life events, arrival reason/mind-reading, and exact future windows
without performing tedious manual calculations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InstantRevelationRequest(BaseModel):
    # Birth particulars
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM:SS or HH:MM")
    timezone: str = Field("Asia/Kolkata", description="IANA timezone")
    latitude: float = Field(..., description="Birth Latitude")
    longitude: float = Field(..., description="Birth Longitude")
    name: Optional[str] = Field("Native / ஜாதகர்", description="Client Name")
    gender: Optional[str] = Field("male", description="male or female")
    ayanamsa: Optional[int] = Field(0, description="0=Lahiri, 1=KP")

    # Arrival / Consultation particulars (optional, defaults to now)
    consultation_time: Optional[str] = Field(None, description="ISO timestamp of customer arrival; defaults to current time")
    consultation_latitude: Optional[float] = Field(None, description="Consultation location latitude; defaults to birth latitude")
    consultation_longitude: Optional[float] = Field(None, description="Consultation location longitude; defaults to birth longitude")

    # Saved ID (optional, to load directly from Supabase / customer database)
    saved_horoscope_id: Optional[str] = Field(None, description="UUID of saved horoscope")
    customer_id: Optional[str] = Field(None, description="Customer ID")


class RevelationBullet(BaseModel):
    id: str = Field(..., description="Unique bullet identifier")
    category: str = Field(..., description="mind_reading | past_hit | personal_marker | future_window | remedy")
    shock_factor: str = Field("HIGH", description="EXTREME | HIGH | MODERATE")
    headline_en: str = Field(..., description="Brief headline in English")
    headline_ta: str = Field(..., description="சுருக்கமான தலைப்பு (தமிழ்)")
    script_en: str = Field(..., description="Ready-to-read conversational teleprompter script in English")
    script_ta: str = Field(..., description="வாடிக்கையாளரிடம் நேரடியாக வாசிக்கக்கூடிய தமிழ் வாக்கு பலன்")
    astrological_proof: str = Field(..., description="Mathematical & Shastric derivation backing this revelation")
    calendar_period: Optional[str] = Field(None, description="Exact calendar dates or age window")
    nature: Optional[str] = Field(None, description="danger | breakthrough | neutral | identity")


class FutureTimelineWindow(BaseModel):
    start_date: str = Field(..., description="ISO start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="ISO end date (YYYY-MM-DD)")
    status: str = Field(..., description="RED_ALERT | PREPARATION | GOLDEN_BREAKTHROUGH")
    title_en: str = Field(..., description="Phase title in English")
    title_ta: str = Field(..., description="காலக்கட்ட தலைப்பு (தமிழ்)")
    script_en: str = Field(..., description="Conversational script in English")
    script_ta: str = Field(..., description="வாடிக்கையாளரிடம் நேரடியாக வாசிக்கக்கூடிய தமிழ் வாக்கு பலன்")
    do_rules_en: List[str] = Field(default_factory=list, description="Recommended actions")
    do_rules_ta: List[str] = Field(default_factory=list, description="செய்ய வேண்டியவை")
    dont_rules_en: List[str] = Field(default_factory=list, description="Prohibited actions / hazards")
    dont_rules_ta: List[str] = Field(default_factory=list, description="தவிர்க்க வேண்டியவை")


class InstantRevelationResponse(BaseModel):
    name: str = Field(..., description="Customer name")
    birth_date: str = Field(..., description="Birth date")
    current_age: int = Field(..., description="Native's current age in years")
    current_dasa_summary: str = Field(..., description="Active Mahadasha - Antardasha - Pratyantardasha in English")
    current_dasa_summary_ta: str = Field(..., description="நடப்பு தசா - புக்தி - அந்தரம் (தமிழ்)")
    arrival_moment_iso: str = Field(..., description="Timestamp of consultation used for Prasanam & Transit")

    # 1. The Mind Reader: Reason for Arrival
    primary_arrival_reason_en: str = Field(..., description="Dominant arrival distress in English")
    primary_arrival_reason_ta: str = Field(..., description="முதன்மையான வருகை நோக்கம் (தமிழ்)")
    arrival_reason_bullets: List[RevelationBullet] = Field(default_factory=list, description="Mind reading cards")

    # 2. Verifiable Past Hits (Cold Proof)
    past_verifiable_hits: List[RevelationBullet] = Field(default_factory=list, description="Shock-value past life events")

    # 3. Personal & Domestic Identifiers
    personal_and_home_markers: List[RevelationBullet] = Field(default_factory=list, description="House Vastu, body marks, family clues")

    # 4. Exact Future Timeline Windows (Next 12–24 Months)
    future_windows: List[FutureTimelineWindow] = Field(default_factory=list, description="Red, Yellow, Green future windows")

    # 5. Turn-Key Instant Remedy
    instant_remedy_en: str = Field(..., description="One-line primary remedy in English")
    instant_remedy_ta: str = Field(..., description="நேரடி உடனடி பரிகாரம் (தமிழ்)")
    temple_recommendation_en: str = Field(..., description="Specific recommended sacred temple")
    temple_recommendation_ta: str = Field(..., description="பரிந்துரைக்கப்படும் புண்ணிய தலம்")
    daily_karma_action_en: str = Field(..., description="Simple daily/weekly karma ritual")
    daily_karma_action_ta: str = Field(..., description="தினசரி / வாராந்திர கர்ம பரிகாரம்")
    gem_or_rudraksha_en: str = Field(..., description="Gemstone and Rudraksha alignment")
    gem_or_rudraksha_ta: str = Field(..., description="ரத்தினம் மற்றும் ருத்ராட்ச வழிகாட்டல்")

    # Fast 10-Second Executive Teleprompter (Bullet points for instant speaking)
    quick_glance_teleprompter_en: List[str] = Field(default_factory=list, description="Fast bulleted teleprompter points in English")
    quick_glance_teleprompter_ta: List[str] = Field(default_factory=list, description="நொடிப் பொழுதில் பார்த்து பேசக்கூடிய குறிப்புகள் (தமிழ்)")
