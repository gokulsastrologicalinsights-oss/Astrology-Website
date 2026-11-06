"""Pydantic schemas for Feature 2: Automated KP Predictive Narrative Engine (English & Tamil)."""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import BirthInput


class CuspalPromiseItem(BaseModel):
    """Evaluation of a single primary cuspal sub-lord in plain language."""
    cusp: int = Field(..., description="Cusp number: 1, 2, 5, 7, 10, or 11")
    domain_en: str = Field(..., description="Domain title in English")
    domain_ta: str = Field(..., description="Domain title in Tamil")
    cusp_sub_lord: str = Field(..., description="Cuspal Sub-Lord planet name")
    star_lord: str = Field(..., description="Star Lord of the CSL")
    sub_sub_lord: str = Field(..., description="Sub-Sub Lord of the CSL")
    signified_houses: List[int] = Field(default_factory=list, description="All houses signified by CSL")
    supporting_houses: List[int] = Field(default_factory=list, description="Supportive houses for this cusp")
    challenging_houses: List[int] = Field(default_factory=list, description="Denying / challenging houses")
    verdict: str = Field(..., description="'strongly_promised' | 'delayed_fruition' | 'denied_or_caution'")
    verdict_label_en: str = Field(..., description="Verdict label in English")
    verdict_label_ta: str = Field(..., description="Verdict label in Tamil")
    summary_en: str = Field(..., description="Plain-language 1-line executive summary in English")
    summary_ta: str = Field(..., description="Plain-language 1-line executive summary in Tamil")
    plain_narrative_en: str = Field(..., description="Comprehensive jargon-free predictive narrative in English")
    plain_narrative_ta: str = Field(..., description="Comprehensive jargon-free predictive narrative in Tamil")
    practical_takeaway_en: str = Field(..., description="Everyday life advice in English")
    practical_takeaway_ta: str = Field(..., description="Everyday life advice in Tamil")


class NatalPromiseSection(BaseModel):
    """Collection of all 6 evaluated primary cuspal sub-lords plus overall synthesis."""
    overall_synthesis_en: str = Field(..., description="Life promise executive summary in English")
    overall_synthesis_ta: str = Field(..., description="Life promise executive summary in Tamil")
    items: List[CuspalPromiseItem] = Field(..., description="Evaluated cuspal sub-lords (1, 2, 5, 7, 10, 11)")
    strong_promises_count: int = Field(0, description="Count of strongly promised life events")
    delayed_count: int = Field(0, description="Count of delayed life events")
    caution_count: int = Field(0, description="Count of caution / denied life areas")


class DashaPeriodDetail(BaseModel):
    """Detailed planetary breakdown of a running dasha period."""
    level: int = Field(..., description="1=Mahadasha, 2=Bhukti, 3=Antara")
    level_name_en: str = Field(..., description="Mahadasha / Bhukti / Antara")
    level_name_ta: str = Field(..., description="மகா திசை / புக்தி / அந்தரம்")
    lord: str = Field(..., description="Lord planet name in English")
    lord_ta: str = Field(..., description="Lord planet name in Tamil")
    star_lord: str = Field(..., description="Star lord of this planet")
    star_lord_ta: str = Field(..., description="Star lord in Tamil")
    sub_lord: str = Field(..., description="Sub lord of this planet")
    sub_lord_ta: str = Field(..., description="Sub lord in Tamil")
    start_date: str = Field(..., description="ISO start date")
    end_date: str = Field(..., description="ISO end date")
    duration_formatted: str = Field(..., description="Formatted duration e.g. '2y 4m 12d'")
    signified_houses: List[int] = Field(default_factory=list, description="Houses signified by this lord")


class RunningDashaImpactSection(BaseModel):
    """Running Dasha-Bhukti-Antara real-world impact across 4 dimensions."""
    mahadasha: DashaPeriodDetail
    bhukti: DashaPeriodDetail
    antara: DashaPeriodDetail
    phase_title_en: str = Field(..., description="Current planetary phase title in English")
    phase_title_ta: str = Field(..., description="Current planetary phase title in Tamil")
    phase_theme_en: str = Field(..., description="Core life theme of this running period in English")
    phase_theme_ta: str = Field(..., description="Core life theme of this running period in Tamil")
    career_impact_en: str = Field(..., description="Plain-language work and career impact in English")
    career_impact_ta: str = Field(..., description="Plain-language work and career impact in Tamil")
    finance_impact_en: str = Field(..., description="Plain-language financial liquidity impact in English")
    finance_impact_ta: str = Field(..., description="Plain-language financial liquidity impact in Tamil")
    relationship_impact_en: str = Field(..., description="Plain-language relationships & family impact in English")
    relationship_impact_ta: str = Field(..., description="Plain-language relationships & family impact in Tamil")
    health_impact_en: str = Field(..., description="Plain-language health & vitality impact in English")
    health_impact_ta: str = Field(..., description="Plain-language health & vitality impact in Tamil")
    favorable_score: int = Field(..., ge=0, le=100, description="Overall favorability index 0-100")


class MilestoneWindowItem(BaseModel):
    """Specific 12–24 month milestone window for career, wealth, or marriage."""
    id: str = Field(..., description="Unique window identifier")
    domain: str = Field(..., description="'career' | 'finance' | 'matrimony'")
    domain_label_en: str = Field(..., description="Domain label in English")
    domain_label_ta: str = Field(..., description="Domain label in Tamil")
    window_title_en: str = Field(..., description="Window range e.g. 'Nov 2026 – Feb 2027'")
    window_title_ta: str = Field(..., description="Window range in Tamil e.g. 'நவம்பர் 2026 – பிப்ரவரி 2027'")
    start_date: str = Field(..., description="ISO start date")
    end_date: str = Field(..., description="ISO end date")
    active_dba: str = Field(..., description="Active Dasha-Bhukti-Antara combo")
    status: str = Field(..., description="'Golden Opportunity' | 'Favorable Window' | 'Caution Period'")
    status_ta: str = Field(..., description="Status label in Tamil")
    headline_en: str = Field(..., description="Executive headline in English")
    headline_ta: str = Field(..., description="Executive headline in Tamil")
    plain_narrative_en: str = Field(..., description="Plain-language narrative explanation in English")
    plain_narrative_ta: str = Field(..., description="Plain-language narrative explanation in Tamil")
    action_plan_en: List[str] = Field(default_factory=list, description="Step-by-step practical action steps in English")
    action_plan_ta: List[str] = Field(default_factory=list, description="Step-by-step practical action steps in Tamil")


class RemedialAdviceSection(BaseModel):
    """Tailored Do's, Don'ts and practical remedial advice based on active sub-lords."""
    dos_en: List[str] = Field(default_factory=list, description="Actionable things to do in English")
    dos_ta: List[str] = Field(default_factory=list, description="Actionable things to do in Tamil")
    donts_en: List[str] = Field(default_factory=list, description="Actionable things to avoid in English")
    donts_ta: List[str] = Field(default_factory=list, description="Actionable things to avoid in Tamil")
    deity_prayer_en: str = Field(..., description="Recommended deity/mantra meditation in English")
    deity_prayer_ta: str = Field(..., description="Recommended deity/mantra meditation in Tamil")
    charity_action_en: str = Field(..., description="Constructive charitable action in English")
    charity_action_ta: str = Field(..., description="Constructive charitable action in Tamil")
    lifestyle_guidance_en: str = Field(..., description="Practical lifestyle adjustments in English")
    lifestyle_guidance_ta: str = Field(..., description="Practical lifestyle adjustments in Tamil")
    lucky_day_color_en: str = Field(..., description="Favorable days and colors in English")
    lucky_day_color_ta: str = Field(..., description="Favorable days and colors in Tamil")


class PersonDetails(BaseModel):
    """Native's foundational birth particulars."""
    name: str = Field("Native", description="Native's name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD")
    birth_time: str = Field(..., description="Birth time in HH:MM:SS")
    place: str = Field("Chennai, India", description="Birth place")
    latitude: float = Field(..., description="Birth latitude")
    longitude: float = Field(..., description="Birth longitude")
    timezone: str = Field("Asia/Kolkata", description="Timezone name")
    gender: str = Field("male", description="Gender")
    lagna: str = Field(..., description="Ascendant sign in English")
    lagna_ta: str = Field(..., description="Ascendant sign in Tamil")
    moon_sign: str = Field(..., description="Moon sign in English")
    moon_sign_ta: str = Field(..., description="Moon sign in Tamil")
    nakshatra: str = Field(..., description="Birth nakshatra in English")
    nakshatra_ta: str = Field(..., description="Birth nakshatra in Tamil")
    current_age: str = Field(..., description="Current age in years and months")


class KpNarrativeResponse(BaseModel):
    """Complete response payload for Automated KP Predictive Narrative Engine."""
    report_id: str = Field(..., description="Unique generated report ID")
    generated_at: str = Field(..., description="ISO generation timestamp")
    target_date: str = Field(..., description="Target reference date for Dasha analysis")
    person_details: PersonDetails
    natal_promise: NatalPromiseSection
    running_dasha: RunningDashaImpactSection
    milestone_windows: List[MilestoneWindowItem]
    remedies: RemedialAdviceSection
    disclaimer_en: str = Field(
        "This predictive narrative report is computed strictly via classical Krishnamurti Paddhati (KP) stellar rules. "
        "It serves as a reflective life blueprint and does not replace professional legal, financial, or medical counsel.",
        description="Standard ethical astrological disclaimer in English",
    )
    disclaimer_ta: str = Field(
        "இந்தக் கணிப்பு அறிக்கை பாரம்பரிய கிருஷ்ணமூர்த்தி பத்ததி (கே.பி.) உன்னத விதிகளின் அடிப்படையில் கணிதவியல் முறையில் உருவாக்கப்பட்டது. "
        "இது வாழ்க்கைப் பயணத்திற்கான வழிகாட்டுதலே அன்றி, சட்ட, நிதி அல்லது மருத்துவ ஆலோசனைகளுக்கு மாற்றாகாது.",
        description="Standard ethical astrological disclaimer in Tamil",
    )


class KpNarrativeRequest(BaseModel):
    """Input request for generating automated KP predictive narrative."""
    birth_input: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    person_name: Optional[str] = "Native"
    gender: Optional[str] = "male"
    target_date: Optional[date] = None
    ayanamsa_id: int = Field(1, description="0=Lahiri, 1=KP (Krishnamurti)")
    language: str = Field("en", description="'en' | 'ta' | 'bilingual'")
    months_ahead: int = Field(24, ge=12, le=36, description="Scan window span in months (12 to 36)")


class KpNarrativePdfRequest(BaseModel):
    """Input request for generating KP predictive narrative PDF booklet."""
    birth_input: Optional[BirthInput] = None
    saved_horoscope_id: Optional[str] = None
    person_name: Optional[str] = "Native"
    gender: Optional[str] = "male"
    target_date: Optional[date] = None
    ayanamsa_id: int = Field(1, description="0=Lahiri, 1=KP (Krishnamurti)")
    language: str = Field("ta", description="'en' | 'ta' | 'bilingual'")
    months_ahead: int = Field(24, ge=12, le=36)
    precalculated_data: Optional[Dict[str, Any]] = None


class SaveKpNarrativeRequest(BaseModel):
    """Payload to persist a generated KP predictive narrative report."""
    title: str = Field(..., description="Descriptive title for the saved report")
    person_name: str = Field(..., description="Native's name")
    saved_horoscope_id: Optional[str] = None
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM:SS")
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"
    gender: str = "male"
    language: str = "ta"
    report_data: Dict[str, Any] = Field(..., description="Full calculated KpNarrativeResponse dictionary")


class SavedKpNarrativeItem(BaseModel):
    """Saved narrative summary item for list views."""
    id: str
    user_id: Optional[str] = None
    title: str
    person_name: str
    saved_horoscope_id: Optional[str] = None
    birth_date: str
    birth_time: str
    language: str
    created_at: str
    updated_at: str


class SavedKpNarrativeListResponse(BaseModel):
    """List of all saved KP predictive narrative reports."""
    total: int
    items: List[SavedKpNarrativeItem]
