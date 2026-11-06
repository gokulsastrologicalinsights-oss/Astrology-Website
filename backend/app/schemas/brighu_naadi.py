"""Brighu Naadi Pydantic Schemas.

Based on Sage Brighu's Naadi principles compiled by Dr. N. Srinivasan Shastry in
"Brighu Naadi Sangraha: (Pearls of Brighu Naadi)" (Sagar Publications).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BrighuNaadiRequest(BaseModel):
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM:SS")
    timezone: str = Field("Asia/Kolkata", description="IANA timezone")
    latitude: float = Field(..., description="Latitude of birth")
    longitude: float = Field(..., description="Longitude of birth")
    gender: Optional[str] = Field("male", description="male or female")
    ayanamsa: Optional[int] = Field(0, description="Ayanamsa ID (0=Lahiri, 1=KP)")


class BrighuBirthEnvironment(BaseModel):
    road_direction_en: str = Field(..., description="Road direction in front of birth house (East to West / South to North)")
    road_direction_ta: str = Field(..., description="பிறந்த வீட்டின் முன் செல்லும் சாலையின் திசை (கிழக்கு-மேற்கு / தெற்கு-வடக்கு)")
    door_facing_en: str = Field(..., description="Main entrance door facing (East / South / West / North)")
    door_facing_ta: str = Field(..., description="பிறந்த வீட்டின் பிரதான தலைவாசல் நோக்கிய திசை")
    city_sector_en: str = Field(..., description="Part of city/town/village where native was born")
    city_sector_ta: str = Field(..., description="பிறந்த ஊரின் பகுதி (கிழக்கு/தெற்கு/மேற்கு/வடக்கு)")
    temple_near_birth_en: str = Field(..., description="Temple or sacred site near birth place")
    temple_near_birth_ta: str = Field(..., description="பிறந்த இடத்தின் அருகில் அமைந்த ஆலயம் / தெய்வம்")
    spouse_direction_en: str = Field(..., description="Direction from which spouse will arrive (Venus for male, Mars for female)")
    spouse_direction_ta: str = Field(..., description="வாழ்க்கைத் துணை அமையும் திசை (சுக்கிரன் / செவ்வாய் நிலைப்படி)")
    rahu_sign: str = Field(..., description="Rahu sign name")
    ketu_sign: str = Field(..., description="Ketu sign name")
    sun_sign: str = Field(..., description="Sun sign name")


class BrighuJeevaKaraka(BaseModel):
    sign: str = Field(..., description="Jupiter sign (or Venus in female chart per BNN)")
    sign_ta: str = Field(..., description="குரு/சுக்கிரன் அமர்ந்த ராசி")
    house_from_lagna: int = Field(..., description="House of Jeeva Karaka from Lagna (1-12)")
    lifestyle_profile_en: str = Field(..., description="General lifestyle indication based on Jeeva Karaka sign")
    lifestyle_profile_ta: str = Field(..., description="ஜீவ காரக ராசி வழி வாழ்க்கை முறை மற்றும் சுபாவம்")
    prosperity_after_41: bool = Field(False, description="True if Jupiter is in Gemini, Sagittarius, or Pisces")
    planets_in_bhavas_from_jupiter: Dict[int, List[str]] = Field(default_factory=dict, description="Planets situated in 1st to 12th bhavas counted from Jupiter")
    empty_adjacent_misery_check: bool = Field(False, description="True if no planets in 4 consecutive houses from Jupiter")
    primary_karaka_planet: str = Field("Jupiter", description="Jupiter for male, Venus for female per Bhrigu Nandi Nadi")
    gender_applied: str = Field("male", description="male or female")


class BrighuKarmaKaraka(BaseModel):
    sign: str = Field(..., description="Saturn sign (Karma Karaka)")
    sign_ta: str = Field(..., description="சனி அமர்ந்த ராசி")
    house_from_lagna: int = Field(..., description="House of Saturn from Lagna (1-12)")
    career_fields_en: List[str] = Field(default_factory=list, description="Indicated professional fields based on Saturn combinations")
    career_fields_ta: List[str] = Field(default_factory=list, description="சனி சேர்க்கை வழி சுட்டிக்காட்டப்படும் தொழில் துறைகள்")
    career_start_age_approx: Optional[float] = Field(None, description="Age of profession commencement (signs to Rahu/Venus * 2.5 yrs)")
    career_status_en: str = Field(..., description="Status summary of professional growth and obstacles")
    career_status_ta: str = Field(..., description="தொழில் வளர்ச்சி மற்றும் தடைகள் பற்றிய விளக்கம்")
    saturn_sign_career_en: Optional[str] = Field(None, description="Saturn in sign career reading from BNN paper")
    saturn_sign_career_ta: Optional[str] = Field(None, description="சனி நின்ற ராசிக்குரிய தொழில் பலன் (BNN ஆய்வு)")
    direction: Optional[str] = Field(None, description="Fire/East, Earth/South, Air/West, Water/North")
    planets_in_same_direction: List[str] = Field(default_factory=list, description="Planets in 1, 5, 9 from Saturn")
    planets_in_opposite_direction: List[str] = Field(default_factory=list, description="Planets in 7th from Saturn")
    planets_in_2nd: List[str] = Field(default_factory=list, description="Planets in 2nd from Saturn")
    planets_in_12th: List[str] = Field(default_factory=list, description="Planets in 12th from Saturn")
    is_retrograde: bool = Field(False, description="True if Saturn is retrograde")
    retrograde_backward_house_influence_en: Optional[str] = Field(None, description="Influence of house behind Saturn when retrograde")
    retrograde_backward_house_influence_ta: Optional[str] = Field(None, description="சனி வக்ரமடைந்தால் பின் வீட்டு கிரகங்களின் தாக்கம்")


class BrighuTimingMilestone(BaseModel):
    category: str = Field(..., description="marriage, career, property, fame, finance, caution, travel, family")
    age_years: List[int] = Field(default_factory=list, description="Specific ages of event fulfillment")
    event_en: str = Field(..., description="Milestone prediction in English")
    event_ta: str = Field(..., description="நிகழ்வு காலக் கணிப்பு (தமிழ்)")
    basis_en: str = Field(..., description="Planetary configuration basis (e.g. Jupiter-Venus 2nd round)")
    basis_ta: str = Field(..., description="ஜோதிட விதி ஆதாரம்")


class BrighuPhysicalMarker(BaseModel):
    source_planet: str = Field(..., description="Sun, Rahu, Ketu, Mars, Saturn")
    sign: str = Field(..., description="Zodiac sign")
    organ_en: str = Field(..., description="Anatomical organ or bodily feature")
    organ_ta: str = Field(..., description="உடல் உறுப்பு / ஆரோக்கிய குறியீடு")
    indication_en: str = Field(..., description="Physical constitution or health alert")
    indication_ta: str = Field(..., description="ஆரோக்கிய பலன் (தமிழ்)")
    is_caution: bool = Field(False, description="True if this is a health/accident vulnerability")


class BrighuNaadiRuleMatch(BaseModel):
    rule_id: str = Field(..., description="Unique ID of classical rule")
    category: str = Field(..., description="life_force, profession, marriage, wealth, property, education, family, health")
    title_en: str = Field(..., description="Rule name in English")
    title_ta: str = Field(..., description="விதியின் பெயர் (தமிழ்)")
    interpretation_en: str = Field(..., description="Predictive reading from Brighu Naadi Sangraha")
    interpretation_ta: str = Field(..., description="பிருகு நாடி சங்கிரகம் கணிப்பு உரை")
    planets_involved: List[str] = Field(default_factory=list, description="Planets forming the combination")
    source_page: str = Field(..., description="Page in Brighu Naadi Sangraha")


class BrighuNaadiResponse(BaseModel):
    treatise_metadata: Dict[str, Any] = Field(..., description="Book title, author, publisher, and core Naadi philosophy")
    bnn_research_metadata: Optional[Dict[str, Any]] = Field(None, description="Academic research citation: A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022")
    birth_environment: BrighuBirthEnvironment = Field(..., description="Vastu, road, door, town quadrant, and local deity")
    jeeva_karaka: BrighuJeevaKaraka = Field(..., description="Jeeva Karaka profile (Jupiter for male, Venus for female) and 12 bhavas")
    karma_karaka: BrighuKarmaKaraka = Field(..., description="Saturn karma profile, career start age, and trade indicators")
    timing_milestones: List[BrighuTimingMilestone] = Field(default_factory=list, description="Exact predicted milestone ages across life areas")
    physical_health_markers: List[BrighuPhysicalMarker] = Field(default_factory=list, description="Physical constitution, appearance, and Ketu/Rahu health alerts")
    matched_rules: List[BrighuNaadiRuleMatch] = Field(default_factory=list, description="Matched classical combinations from the treatise")
    bnn_directional_groups: Optional[Dict[str, List[str]]] = Field(None, description="Planetary distributions across East (Fire), South (Earth), West (Air), North (Water)")
    bnn_20_rules_evaluations: List[Dict[str, Any]] = Field(default_factory=list, description="Evaluation of the 20 Bhrigu Nandi Nadi golden rules")
    rahu_ketu_axis_career_outside: Optional[Dict[str, Any]] = Field(None, description="Rule 10 evaluation: whether Rahu-Ketu axis divides Jupiter and Saturn")
    pankajj_duaa_compendium: Optional[Dict[str, Any]] = Field(None, description="BNN diagnostic rules, medical astrology, yogas, and remedies from Pankajj K Duaa compendium")



class BrighuPrashnaRequest(BaseModel):
    birth_date: Optional[str] = Field(None, description="YYYY-MM-DD of querent")
    completed_age: Optional[int] = Field(None, description="Completed age in years (0 to 107)")
    query_date: Optional[str] = Field(None, description="Date of query (YYYY-MM-DD, defaults to current date)")
    query_category: Optional[str] = Field("general", description="general, business, career, education, marriage, health")
    querent_order: Optional[int] = Field(1, description="1 for primary querent, 2 for second questioning person")


class BrighuPrashnaResponse(BaseModel):
    book_title: str = Field("Brighu Prashna Nadi", description="Treatise title")
    author: str = Field("R. G. Rao (Sagar Publications)", description="Author & Publisher")
    completed_age: int = Field(..., description="Completed years of age at query time")
    formula_applied: str = Field(..., description="Calculation step: 107 - Completed Age = Remainder")
    prediction_number: int = Field(..., description="Distinctive prediction number (0 to 107)")
    sub_category_key: Optional[str] = Field(None, description="Sub-prediction variant key if applicable (e.g. 87&86(3) business)")
    guru_mantra: str = Field("OM SRI JAGADEESWARAYA NAMAHA", description="Sanctified Guru Mantra recited prior to revelation")
    sanskrit_sloka: Optional[str] = Field(None, description="Classical Sanskrit aphorism from the palm leaf")
    yoga_name_en: str = Field(..., description="Governing Yoga / Amsha name in English")
    yoga_name_ta: str = Field(..., description="இயங்கும் யோகம் / அம்சம் (தமிழ்)")
    core_prophecy_en: str = Field(..., description="Central oracle prophecy")
    core_prophecy_ta: str = Field(..., description="முதன்மைக் கணிப்பு உரை (தமிழ்)")
    career_and_finance_en: str = Field(..., description="Career, profession, trade, and financial outlook")
    career_and_finance_ta: str = Field(..., description="தொழில், உத்தியோகம் மற்றும் நிதி நிலை")
    family_and_relationships_en: str = Field(..., description="Parents, spouse, children, and domestic peace")
    family_and_relationships_ta: str = Field(..., description="குடும்பம், வாழ்க்கைத்துணை, வாரிசு மற்றும் உறவுகள்")
    health_and_cautions_en: str = Field(..., description="Health status, physical vulnerabilities, and cautions")
    health_and_cautions_ta: str = Field(..., description="உடல் நலம், நோய்த்தன்மை மற்றும் எச்சரிக்கைகள்")
    past_karma_cause_en: Optional[str] = Field(None, description="Poorva Karma / Sanchita Karma cause in previous birth")
    past_karma_cause_ta: Optional[str] = Field(None, description="முற்பிறவி கர்ம வினை மற்றும் காரணங்கள்")
    prescribed_remedy_en: str = Field(..., description="Specific Pooja, deity, temple darshan, or Dana prescribed")
    prescribed_remedy_ta: str = Field(..., description="பரிகார தெய்வம், பூஜை, யாத்திரை மற்றும் தானம்")
    relief_timeline_en: str = Field(..., description="Exact duration until relief manifests (months, pakshas, samvatsaras)")
    relief_timeline_ta: str = Field(..., description="துன்பங்கள் நீங்கி சுப பலன்கள் தொடங்கும் காலம்")

    pankajj_duaa_compendium: Optional[Dict[str, Any]] = Field(None, description="BNN diagnostic rules, medical astrology, yogas, and remedies from Pankajj K Duaa compendium")

