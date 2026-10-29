"""Pydantic schemas for Pancha Pakshi Shastra endpoints."""

from typing import List, Dict, Any, Optional
from datetime import date as dt_date, datetime
from pydantic import BaseModel, Field, field_validator


class PanchaPakshiRequest(BaseModel):
    target_date: dt_date = Field(..., description="Target date in YYYY-MM-DD")
    latitude: float = Field(default=13.0827, ge=-90.0, le=90.0)
    longitude: float = Field(default=80.2707, ge=-180.0, le=180.0)
    timezone: str = Field(default="Asia/Kolkata")
    birth_nakshatra: int = Field(..., ge=1, le=27, description="Birth star index 1..27 (Ashwini=1, Revati=27)")
    birth_paksha: str = Field(default="shukla", description="'shukla' (waxing) or 'krishna' (waning)")

    @field_validator("target_date", mode="before")
    @classmethod
    def parse_target_date(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean_str = v.strip().split("T")[0].split(" ")[0]
            try:
                return dt_date.fromisoformat(clean_str)
            except Exception:
                pass
        elif isinstance(v, datetime):
            return v.date()
        return v

    @field_validator("birth_nakshatra", mode="before")
    @classmethod
    def parse_birth_nakshatra(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return int(v.strip())
            except Exception:
                pass
        return v

    @field_validator("birth_paksha", mode="before")
    @classmethod
    def parse_birth_paksha(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().lower()
            if "krishna" in clean or "தேய்" in clean or "thei" in clean or "waning" in clean:
                return "krishna"
            return "shukla"
        return v


class AntaraSlot(BaseModel):
    sub_index: int
    global_sub_index: int
    period_type: str
    major_activity: str
    major_activity_en: str
    major_activity_ta: str
    sub_activity: str
    sub_activity_en: str
    sub_activity_ta: str
    power_score: int
    rating: str
    rating_label_en: str
    rating_label_ta: str
    color: str
    start_time_utc: str
    end_time_utc: str
    start_time_local: str
    end_time_local: str
    duration_minutes: float
    recommended_en: List[str]
    recommended_ta: List[str]
    avoid_en: List[str]
    avoid_ta: List[str]


class YamamSlot(BaseModel):
    yamam_index: int
    period_type: str
    name_en: str
    name_ta: str
    native_activity: str
    native_activity_en: str
    native_activity_ta: str
    power_score: int
    nature: str
    color: str
    ruling_bird: str
    ruling_bird_ta: str
    start_time_utc: str
    end_time_utc: str
    start_time_local: str
    end_time_local: str
    duration_minutes: float
    sub_periods: List[AntaraSlot]
    all_birds_state: Dict[str, str]


class PanchaPakshiResponse(BaseModel):
    target_date: str
    location: Dict[str, Any]
    astronomical: Dict[str, Any]
    birth_details: Dict[str, Any]
    birth_bird: Dict[str, Any]
    day_yamam_duration_minutes: float
    night_yamam_duration_minutes: float
    sub_period_duration_minutes: float
    day_yamams: List[YamamSlot]
    night_yamams: List[YamamSlot]
    all_antaras: List[AntaraSlot]
    golden_windows: List[AntaraSlot]
    padupakshi_windows: List[AntaraSlot]
    total_golden_windows: int
    total_padupakshi_windows: int
