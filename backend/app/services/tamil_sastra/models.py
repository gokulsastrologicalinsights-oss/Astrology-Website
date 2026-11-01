"""Pydantic schemas and models for the Tamil Astrology & Daily Dharma Sastra module.

Derived from classical treatises:
"இந்து மதமும் ஜோதிட சாஸ்திரமும் கூறும் தினசரி வாழ்வில் செய்யக்கூடாதவையும், செய்ய வேண்டியவையும்"
(What to do and what not to do in daily life according to Hindu Dharma and Astrology Sastra).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MedicalDeityItem(BaseModel):
    id: int
    disease_en: str
    disease_ta: str
    deity_en: str
    deity_ta: str
    category: str
    description_en: Optional[str] = None
    description_ta: Optional[str] = None
    mantra_or_procedure_en: Optional[str] = None
    mantra_or_procedure_ta: Optional[str] = None


class LifeWishDeityItem(BaseModel):
    id: int
    goal_en: str
    goal_ta: str
    deity_en: str
    deity_ta: str
    temple_sankalpa_en: Optional[str] = None
    temple_sankalpa_ta: Optional[str] = None
    special_notes_ta: Optional[str] = None


class RamayanaParayanamItem(BaseModel):
    id: int
    purpose_en: str
    purpose_ta: str
    kandam_en: str
    kandam_ta: str
    sarga_title_en: str
    sarga_title_ta: str
    recommended_time_en: str
    recommended_time_ta: str
    benefits_ta: Optional[str] = None


class NavagrahaCorrespondenceItem(BaseModel):
    graha_en: str
    graha_ta: str
    cloth_color_en: str
    cloth_color_ta: str
    grain_en: str
    grain_ta: str
    direction_en: str
    direction_ta: str
    gemstone_en: str
    gemstone_ta: str
    dhupam_fragrance_en: str
    dhupam_fragrance_ta: str
    adhidevata_en: str
    adhidevata_ta: str
    metal_en: str
    metal_ta: str
    flower_en: str
    flower_ta: str
    vehicle_en: str
    vehicle_ta: str


class DasaPariharamItem(BaseModel):
    graha_en: str
    graha_ta: str
    affliction_triggers_ta: str
    pariharam_procedure_ta: str
    donation_items_ta: str
    sacred_temples_ta: List[str]
    mantra_or_japa_ta: str


class VastuAwakeningTimingItem(BaseModel):
    tamil_month: str
    solar_day: int
    gregorian_approx: str
    duration_time: str
    puja_golden_window: str
    best_door_facing_ta: str
    notes_ta: str


class VastuRuleItem(BaseModel):
    rule_number: int
    category: str
    rule_ta: str
    rule_en: str
    importance: str  # Mandatory, Highly Recommended, Recommended


class SoolamDirectionItem(BaseModel):
    day_or_tithi_or_star: str
    soolam_direction_ta: str
    soolam_direction_en: str
    pariharam_item_ta: str
    pariharam_item_en: str
    instructions_ta: str


class GowriMuhurtaSlot(BaseModel):
    order: int
    name_ta: str
    name_en: str
    nature: str  # Auspicious, Inauspicious
    is_favorable: bool
    description_ta: str


class SpecialMuhurtaItem(BaseModel):
    title_ta: str
    title_en: str
    recommended_stars_ta: List[str]
    recommended_weekdays_ta: List[str]
    recommended_tithis_ta: List[str]
    avoid_ta: List[str]
    golden_rules_ta: List[str]


class DailyGuidanceRequest(BaseModel):
    date: str = Field(description="ISO date string (YYYY-MM-DD)")
    janma_nakshatra_idx: Optional[int] = Field(None, ge=1, le=27, description="Native's birth nakshatra index 1..27")
    janma_rasi_idx: Optional[int] = Field(None, ge=1, le=12, description="Native's birth moon sign index 1..12")


class DailyGuidanceResponse(BaseModel):
    date: str
    weekday_ta: str
    weekday_en: str
    naal_vizhippu_ta: str
    naal_vizhippu_category: str  # two_eyed, one_eyed, blind
    vaara_soolam_ta: str
    vaara_soolam_direction: str
    pariharam_ta: str
    gowri_panchangam_day: List[GowriMuhurtaSlot]
    auspicious_horas_ta: List[str]
    chandrashtama_warning: bool
    dos_for_today_ta: List[str]
    donts_for_today_ta: List[str]
    deepam_worship_tip_ta: str
    general_dharma_tip_ta: str
