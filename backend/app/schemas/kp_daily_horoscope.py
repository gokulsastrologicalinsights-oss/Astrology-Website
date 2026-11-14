"""Schemas for KP Daily Horoscope & Transit Prediction Engine."""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class KpAspectPrediction(BaseModel):
    """Detailed prediction for a specific life aspect based on KP House Significations."""
    aspect_code: str = Field(..., description="Unique key: career | finance | love | health | travel")
    aspect_name: str = Field(..., description="English name: e.g. Career & Business")
    aspect_name_tamil: str = Field(..., description="Tamil name: e.g. தொழில் & வியாபாரம்")
    score: int = Field(..., ge=0, le=100, description="Normalized score 0-100")
    rating_stars: float = Field(..., ge=1.0, le=5.0, description="1 to 5 star rating")
    status: str = Field(..., description="Excellent | Favorable | Mixed | Challenging")
    signified_houses: List[int] = Field(default_factory=list, description="KP Houses activated for this aspect")
    insight_en: str = Field(..., description="Detailed prediction analysis in English")
    insight_ta: str = Field(..., description="Detailed prediction analysis in Tamil")
    key_recommendation_en: str = Field(..., description="Actionable advice in English")
    key_recommendation_ta: str = Field(..., description="Actionable advice in Tamil")


class MoonSubLordWindow(BaseModel):
    """Hourly time slot determined by the Moon's transit through KP Sub-Lords."""
    start_time: str = Field(..., description="Local start time: e.g. 08:30 AM")
    end_time: str = Field(..., description="Local end time: e.g. 10:45 AM")
    star_name: str = Field(..., description="Nakshatra name")
    star_lord: str = Field(..., description="Nakshatra lord")
    sub_lord: str = Field(..., description="KP Sub-Lord planet")
    sentiment: str = Field(..., description="golden | neutral | caution")
    activated_houses: List[int] = Field(default_factory=list, description="Houses activated for this Rashi")
    advice_en: str = Field(..., description="English advice for this time window")
    advice_ta: str = Field(..., description="Tamil advice for this time window")


class RashiDailyPrediction(BaseModel):
    """Comprehensive daily horoscope for a single Rashi with KP transit analysis."""
    rashi_id: int = Field(..., ge=1, le=12, description="1=Aries/Mesha to 12=Pisces/Meena")
    rashi_name_en: str = Field(..., description="English zodiac sign name")
    rashi_name_ta: str = Field(..., description="Tamil zodiac sign name")
    sign_lord: str = Field(..., description="Ruler of the sign")
    daily_score: int = Field(..., ge=0, le=100, description="Overall favorability score 0-100")
    daily_rating_stars: float = Field(..., ge=1.0, le=5.0, description="Overall stars 1.0 - 5.0")
    day_sentiment: str = Field(..., description="Excellent | Favorable | Mixed | Challenging")
    
    # Executive Brief Statements
    brief_statement_en: str = Field(..., description="Brief one-line statement of the day in English")
    brief_statement_ta: str = Field(..., description="Brief one-line statement of the day in Tamil")
    peak_highlight_en: str = Field(..., description="The brightest opportunity of the day in English")
    peak_highlight_ta: str = Field(..., description="The brightest opportunity of the day in Tamil")
    caution_trap_en: str = Field(..., description="Key vulnerability or caution to observe in English")
    caution_trap_ta: str = Field(..., description="Key vulnerability or caution to observe in Tamil")
    
    # Time Windows
    golden_hour_window: str = Field(..., description="Best time slot of the day")
    caution_hour_window: str = Field(..., description="Time slot requiring caution")
    
    # Lucky Attributes
    lucky_color_en: str = Field(..., description="Auspicious color in English")
    lucky_color_ta: str = Field(..., description="Auspicious color in Tamil")
    lucky_number: int = Field(..., description="Auspicious number 1-9")
    lucky_direction_en: str = Field(..., description="Auspicious direction in English")
    lucky_direction_ta: str = Field(..., description="Auspicious direction in Tamil")
    daily_remedy_en: str = Field(..., description="KP Astro guidance / affirmation in English")
    daily_remedy_ta: str = Field(..., description="KP Astro guidance / affirmation in Tamil")
    
    # Granular Breakdown
    aspects: List[KpAspectPrediction] = Field(default_factory=list, description="Predictions across all 5 core aspects")
    moon_sub_windows: List[MoonSubLordWindow] = Field(default_factory=list, description="Moon Sub-Lord hourly windows")


class KpDailyHoroscopeRequest(BaseModel):
    """Request payload for KP Daily Horoscope."""
    target_date: Optional[str] = Field(None, description="Target date in YYYY-MM-DD format (defaults to current date)")
    timezone: Optional[str] = Field("Asia/Kolkata", description="IANA timezone or offset string")
    latitude: Optional[float] = Field(13.0827, description="Latitude for local ascendant / sunrise (defaults to Chennai)")
    longitude: Optional[float] = Field(80.2707, description="Longitude for local ascendant / sunrise")
    rashi: Optional[str] = Field("all", description="Zodiac sign number (1-12), sign name (e.g. 'Aries'/'Mesha'), or 'all'")
    ayanamsa: Optional[int] = Field(1, description="Ayanamsa ID (1 = Krishnamurti KP, 0 = Lahiri)")


class KpDailyHoroscopeResponse(BaseModel):
    """Response payload containing daily KP horoscopes for requested signs."""
    date: str = Field(..., description="Calendar date (YYYY-MM-DD)")
    day_of_week: str = Field(..., description="Day name in English: e.g. Monday")
    day_of_week_ta: str = Field(..., description="Day name in Tamil: e.g. திங்கட்கிழமை")
    day_lord: str = Field(..., description="Vara lord planet")
    moon_sign_at_noon: str = Field(..., description="Moon sign at midday")
    moon_star_at_noon: str = Field(..., description="Moon star at midday")
    moon_sub_lord_at_noon: str = Field(..., description="Moon sub-lord at midday")
    ayanamsa_name: str = Field(..., description="Ayanamsa used (e.g. KP)")
    total_rashis: int = Field(..., description="Count of returned rashis")
    predictions: List[RashiDailyPrediction] = Field(..., description="Daily predictions per Rashi")
    calculated_at: str = Field(..., description="ISO calculation timestamp")


class TransitMovement(BaseModel):
    """Planetary transit details during a weekly or monthly period."""
    planet: str = Field(..., description="Planet name in English (e.g. Sun, Jupiter)")
    planet_ta: str = Field(..., description="Planet name in Tamil (e.g. சூரியன், குரு)")
    current_sign: str = Field(..., description="Zodiac sign occupied (e.g. Scorpio)")
    current_sign_ta: str = Field(..., description="Zodiac sign occupied in Tamil (e.g. விருச்சிகம்)")
    star_name: str = Field(..., description="Nakshatra name")
    star_lord: str = Field(..., description="Nakshatra ruler")
    sub_lord: str = Field(..., description="KP Sub-Lord")
    house_relative: int = Field(..., ge=1, le=12, description="House occupied relative to this Rashi (1-12)")
    is_favorable: bool = Field(..., description="True if transit is benefic according to Gochara rules")
    status: str = Field(..., description="favorable | neutral | caution")
    is_retrograde: bool = Field(default=False, description="Whether the planet is in retrograde motion")
    transit_ingress_event: Optional[str] = Field(None, description="Notable sign change event if any during this period")
    impact_summary_en: str = Field(..., description="Specific transit impact on this Rashi in English")
    impact_summary_ta: str = Field(..., description="Specific transit impact on this Rashi in Tamil")


class TransitSummaryPerRashi(BaseModel):
    """Executive synthesis of all planetary transits and their impact on a Rashi."""
    rashi_id: int = Field(..., ge=1, le=12)
    rashi_name_en: str = Field(...)
    rashi_name_ta: str = Field(...)
    planet_transits: List[TransitMovement] = Field(default_factory=list, description="All 9 planetary positions & houses")
    transit_overview_en: str = Field(..., description="Synthesized transit prediction narrative in English")
    transit_overview_ta: str = Field(..., description="Synthesized transit prediction narrative in Tamil")
    benefic_planets: List[str] = Field(default_factory=list, description="Planets delivering auspicious transit results")
    challenging_planets: List[str] = Field(default_factory=list, description="Planets requiring vigilance or remedies")
    chandrashtama_period_en: str = Field(..., description="Chandrashtama days/dates in English")
    chandrashtama_period_ta: str = Field(..., description="Chandrashtama days/dates in Tamil")
    special_yogas_en: List[str] = Field(default_factory=list, description="Special astrological formations or alerts in English")
    special_yogas_ta: List[str] = Field(default_factory=list, description="Special astrological formations or alerts in Tamil")


class RashiWeeklyPrediction(BaseModel):
    """Weekly horoscope prediction for a single Rashi with transit synthesis."""
    rashi_id: int = Field(..., ge=1, le=12)
    rashi_name_en: str = Field(...)
    rashi_name_ta: str = Field(...)
    sign_lord: str = Field(...)
    weekly_score: int = Field(..., ge=0, le=100, description="Overall favorability score 0-100")
    weekly_rating_stars: float = Field(..., ge=1.0, le=5.0, description="Overall stars 1.0 - 5.0")
    week_sentiment: str = Field(..., description="Excellent | Favorable | Mixed | Challenging")
    brief_statement_en: str = Field(..., description="Weekly executive summary in English")
    brief_statement_ta: str = Field(..., description="Weekly executive summary in Tamil")
    peak_highlight_en: str = Field(..., description="The brightest opportunity of the week in English")
    peak_highlight_ta: str = Field(..., description="The brightest opportunity of the week in Tamil")
    caution_trap_en: str = Field(..., description="Key vulnerability or warning in English")
    caution_trap_ta: str = Field(..., description="Key vulnerability or warning in Tamil")
    lucky_days_en: str = Field(..., description="Best days of the week in English")
    lucky_days_ta: str = Field(..., description="Best days of the week in Tamil")
    chandrashtama_days_en: str = Field(..., description="Days requiring caution in English")
    chandrashtama_days_ta: str = Field(..., description="Days requiring caution in Tamil")
    lucky_color_en: str = Field(...)
    lucky_color_ta: str = Field(...)
    lucky_number: int = Field(...)
    lucky_direction_en: str = Field(...)
    lucky_direction_ta: str = Field(...)
    weekly_remedy_en: str = Field(..., description="Weekly remedy and guidance in English")
    weekly_remedy_ta: str = Field(..., description="Weekly remedy and guidance in Tamil")
    aspects: List[KpAspectPrediction] = Field(default_factory=list)
    transit_summary: TransitSummaryPerRashi = Field(..., description="Transit movements & comprehensive summary")


class KpWeeklyHoroscopeRequest(BaseModel):
    """Request payload for KP Weekly Horoscope."""
    target_date: Optional[str] = Field(None, description="Any date within the target week in YYYY-MM-DD")
    timezone: Optional[str] = Field("Asia/Kolkata")
    latitude: Optional[float] = Field(13.0827)
    longitude: Optional[float] = Field(80.2707)
    rashi: Optional[str] = Field("all")
    ayanamsa: Optional[int] = Field(1)


class KpWeeklyHoroscopeResponse(BaseModel):
    """Response payload containing weekly KP horoscopes & transit summaries."""
    start_date: str = Field(..., description="Week start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Week end date (YYYY-MM-DD)")
    week_label_en: str = Field(..., description="e.g. Nov 16, 2026 - Nov 22, 2026")
    week_label_ta: str = Field(..., description="e.g. 16 நவம்பர் 2026 – 22 நவம்பர் 2026")
    ayanamsa_name: str = Field(...)
    total_rashis: int = Field(...)
    major_transits: List[TransitMovement] = Field(default_factory=list, description="Key planetary transit movements in the week")
    predictions: List[RashiWeeklyPrediction] = Field(...)
    calculated_at: str = Field(...)


class RashiMonthlyPrediction(BaseModel):
    """Monthly horoscope prediction for a single Rashi with transit synthesis."""
    rashi_id: int = Field(..., ge=1, le=12)
    rashi_name_en: str = Field(...)
    rashi_name_ta: str = Field(...)
    sign_lord: str = Field(...)
    monthly_score: int = Field(..., ge=0, le=100, description="Overall favorability score 0-100")
    monthly_rating_stars: float = Field(..., ge=1.0, le=5.0, description="Overall stars 1.0 - 5.0")
    month_sentiment: str = Field(..., description="Excellent | Favorable | Mixed | Challenging")
    brief_statement_en: str = Field(..., description="Monthly executive summary in English")
    brief_statement_ta: str = Field(..., description="Monthly executive summary in Tamil")
    peak_highlight_en: str = Field(..., description="Major breakthrough of the month in English")
    peak_highlight_ta: str = Field(..., description="Major breakthrough of the month in Tamil")
    caution_trap_en: str = Field(..., description="Key caution for the month in English")
    caution_trap_ta: str = Field(..., description="Key caution for the month in Tamil")
    auspicious_dates_en: str = Field(..., description="Auspicious dates of the month in English")
    auspicious_dates_ta: str = Field(..., description="Auspicious dates of the month in Tamil")
    chandrashtama_dates_en: str = Field(..., description="Chandrashtama dates in English")
    chandrashtama_dates_ta: str = Field(..., description="Chandrashtama dates in Tamil")
    lucky_color_en: str = Field(...)
    lucky_color_ta: str = Field(...)
    lucky_number: int = Field(...)
    lucky_direction_en: str = Field(...)
    lucky_direction_ta: str = Field(...)
    monthly_remedy_en: str = Field(..., description="Monthly remedy and guidance in English")
    monthly_remedy_ta: str = Field(..., description="Monthly remedy and guidance in Tamil")
    aspects: List[KpAspectPrediction] = Field(default_factory=list)
    transit_summary: TransitSummaryPerRashi = Field(..., description="Transit movements & comprehensive summary")


class KpMonthlyHoroscopeRequest(BaseModel):
    """Request payload for KP Monthly Horoscope."""
    year: Optional[int] = Field(None, description="Year (e.g. 2026)")
    month: Optional[int] = Field(None, description="Month (1-12)")
    target_date: Optional[str] = Field(None, description="Any date within the target month in YYYY-MM-DD")
    timezone: Optional[str] = Field("Asia/Kolkata")
    latitude: Optional[float] = Field(13.0827)
    longitude: Optional[float] = Field(80.2707)
    rashi: Optional[str] = Field("all")
    ayanamsa: Optional[int] = Field(1)


class KpMonthlyHoroscopeResponse(BaseModel):
    """Response payload containing monthly KP horoscopes & transit summaries."""
    year: int = Field(...)
    month: int = Field(...)
    start_date: str = Field(..., description="Month start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Month end date (YYYY-MM-DD)")
    month_name_en: str = Field(..., description="e.g. November 2026")
    month_name_ta: str = Field(..., description="e.g. நவம்பர் 2026")
    ayanamsa_name: str = Field(...)
    total_rashis: int = Field(...)
    major_transits: List[TransitMovement] = Field(default_factory=list, description="Key planetary transit movements in the month")
    predictions: List[RashiMonthlyPrediction] = Field(...)
    calculated_at: str = Field(...)
