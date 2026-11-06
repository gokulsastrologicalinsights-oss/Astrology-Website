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
    checklist: List[str] = Field(default_factory=list, description="Multi-tiered Shastric verification checks (திரிவித சாஸ்திர சரிபார்ப்பு முறை)")


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

    # The 5 Accuracy & Shock Amplifiers
    # 1. Career & Industry Calling
    career_calling_en: str = Field(..., description="Exact professional calling & industry description in English")
    career_calling_ta: str = Field(..., description="துல்லியமான தொழில் காரகம் மற்றும் துறை விளக்கம் (தமிழ்)")
    career_fields: List[str] = Field(default_factory=list, description="Indicated professional sectors")

    # 2. Sibling Order & Family Secret
    family_birth_order_en: str = Field(..., description="Birth order & maternal lineage clues in English")
    family_birth_order_ta: str = Field(..., description="பிறப்பு வரிசை மற்றும் குடும்ப ரகசியக் குறிப்புகள் (தமிழ்)")

    # 3. Gochara Sledgehammer: Active Shani & Guru Transits
    gochara_saturn_phase: str = Field(..., description="Active Saturn transit phase (Sade Sati, Ashtama Shani, Kantaka Shani, etc.)")
    gochara_saturn_verdict_en: str = Field(..., description="Saturn transit script in English")
    gochara_saturn_verdict_ta: str = Field(..., description="சனிப் பெயர்ச்சி நேரடி வாக்கு பலன் (தமிழ்)")
    gochara_jupiter_verdict_en: str = Field(..., description="Jupiter transit script in English")
    gochara_jupiter_verdict_ta: str = Field(..., description="குருப் பெயர்ச்சி நேரடி வாக்கு பலன் (தமிழ்)")

    # 4. Dasa Chidra Alert (Dasa Sandhi)
    dasa_chidra_active: bool = Field(False, description="True if native is in the final 12 months of Mahadasha")
    dasa_chidra_warning_en: Optional[str] = Field(None, description="Dasa Chidra explanation in English")
    dasa_chidra_warning_ta: Optional[str] = Field(None, description="தசா சந்தி முடக்க எச்சரிக்கை (தமிழ்)")
    dasa_chidra_end_date: Optional[str] = Field(None, description="Date when current Mahadasha terminates")

    # 5. Specific Anatomical & Organ Vulnerability
    medical_organ_vulnerability_en: str = Field(..., description="Vulnerable organ & bodily affliction in English")
    medical_organ_vulnerability_ta: str = Field(..., description="உடல்நலக் கோளாறு & பலவீனமான உறுப்பு எச்சரிக்கை (தமிழ்)")
    vulnerable_organs: List[str] = Field(default_factory=list, description="Specific anatomical organs at risk")

    # The 4 Ultra-Precision Nadi Shockers (Option B)
    # 1. Spouse & In-Laws Secrets
    spouse_secrets_en: str = Field(..., description="Spouse origin, complexion, and in-laws clues in English")
    spouse_secrets_ta: str = Field(..., description="களத்திரம், திசை, மாமனார் வழி ரகசியக் குறிப்புகள் (தமிழ்)")

    # 2. Vehicle & Conveyance Marker
    vehicle_marker_en: str = Field(..., description="Preferred vehicle color and scratch/defect markers in English")
    vehicle_marker_ta: str = Field(..., description="வாகன நிறம், பழுது மற்றும் கீறல் அடையாளம் (தமிழ்)")

    # 3. Ancestral Property & Paternal Land Rift
    ancestral_land_rift_en: str = Field(..., description="Ancestral property, agricultural land, and well dispute clues in English")
    ancestral_land_rift_ta: str = Field(..., description="பூர்வீக சொத்து, விவசாய நிலம், கிணறு மற்றும் தந்தை வழி சிக்கல் (தமிழ்)")

    # 4. Childhood Balarishta Escape
    childhood_balarishta_en: str = Field(..., description="Childhood critical illness or high fever escape in English")
    childhood_balarishta_ta: str = Field(..., description="பாலாரிஷ்டம் - சிறுவயதில் தப்பிய கண்டம் மற்றும் தீவிர காய்ச்சல் (தமிழ்)")

    # Deva Keralam (Chandra Kala Nadi) 150 Nadiamsas & Longevity Engine
    lagna_nadiamsa_number: int = Field(1, description="Lagna Nadiamsa index 1-150")
    lagna_nadiamsa_name: str = Field(..., description="Nadiamsa name in English")
    lagna_nadiamsa_name_ta: str = Field(..., description="நாடியம்சம் பெயர் (தமிழ்)")
    lagna_nadiamsa_half: str = Field(..., description="Purvardha or Uttarardha in English")
    lagna_nadiamsa_half_ta: str = Field(..., description="பூர்வார்த்தம் அல்லது உத்தரார்த்தம் (தமிழ்)")
    lagna_nadiamsa_script_en: str = Field(..., description="Deva Keralam Nadiamsa delineation in English")
    lagna_nadiamsa_script_ta: str = Field(..., description="தேவ கேரளம் நாடியம்ச வாக்கு பலன் (தமிழ்)")
    khanda_nirnaya_longevity_en: str = Field(..., description="Khanda Nirnaya and longevity classification in English")
    khanda_nirnaya_longevity_ta: str = Field(..., description="கண்ட நிர்ணயம் மற்றும் ஆயுள் கணிதம் (தமிழ்)")
    father_critical_degree: str = Field(..., description="Father critical crisis transit degree (Deva Keralam)")
    mother_critical_degree: str = Field(..., description="Mother critical crisis transit degree (Deva Keralam)")

    # 101% Guaranteed Chart Shockers (BNN & Deva Keralam Condition-Verified)
    guaranteed_chart_shockers: List[RevelationBullet] = Field(default_factory=list, description="Strictly verified 101% matched shockers")
    remedial_taboos_en: List[str] = Field(default_factory=list, description="Strict Shastric Taboos and Behavioral Directives in English")
    remedial_taboos_ta: List[str] = Field(default_factory=list, description="சாஸ்திர கடுமையான விலக்குகள் மற்றும் உணவு விதிமுறைகள் (தமிழ்)")

    # Fast 10-Second Executive Teleprompter (Bullet points for instant speaking)
    quick_glance_teleprompter_en: List[str] = Field(default_factory=list, description="Fast bulleted teleprompter points in English")
    quick_glance_teleprompter_ta: List[str] = Field(default_factory=list, description="நொடிப் பொழுதில் பார்த்து பேசக்கூடிய குறிப்புகள் (தமிழ்)")
