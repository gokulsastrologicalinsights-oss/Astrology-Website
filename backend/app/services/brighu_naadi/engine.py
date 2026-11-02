"""Brighu Naadi Predictive Engine.

Evaluates Jeeva Karaka (Jupiter), Karma Karaka (Saturn), Vastu/Birth Environment,
exact timing milestones, physical markers, and classical Naadi combinations based on
Dr. N. Srinivasan Shastry's "Brighu Naadi Sangraha".
"""

from typing import Dict, Any, List, Optional
from app.schemas.brighu_naadi import (
    BrighuBirthEnvironment,
    BrighuJeevaKaraka,
    BrighuKarmaKaraka,
    BrighuTimingMilestone,
    BrighuPhysicalMarker,
    BrighuNaadiRuleMatch,
    BrighuNaadiResponse,
)
from app.services.brighu_naadi.registry import (
    BRIGHU_NAADI_METADATA,
    ROAD_DIRECTION_MAP,
    DOOR_FACING_MAP,
    CITY_SECTOR_MAP,
    TEMPLE_NEAR_BIRTH_MAP,
    SPOUSE_DIRECTION_MAP,
    MARRIAGE_AGE_BY_VENUS_FROM_JUPITER,
    FAME_AGE_BY_SUN_FROM_JUPITER,
    PROPERTY_AGE_BY_JUPITER_FROM_MARS,
    FINANCE_AGE_BY_VENUS_FROM_JUPITER,
    CAREER_AGE_BY_VENUS_FROM_SATURN,
    ACCIDENT_AGE_BY_MARS_FROM_RAHU,
    INFANT_DANGER_AGE_BY_KETU_FROM_JUPITER,
    RELOCATION_AGE_BY_MOON_FROM_SATURN,
    FATHER_CRITICAL_AGE_BY_SUN_FROM_SATURN,
    MOTHER_CRITICAL_AGE_BY_MOON_FROM_SATURN,
    FEMALE_HUSBAND_CRITICAL_AGE_BY_MARS_FROM_SATURN,
    SUN_SIGN_CONSTITUTION,
    RAHU_SIGN_AFFLICTIONS,
    KETU_SIGN_DANGERS,
    BRIGHU_NAADI_RULES_DATABASE,
    BHRIGU_NANDI_NADI_RESEARCH_METADATA,
    BNN_PLANETARY_FRIENDSHIP,
    BNN_DIRECTIONS,
    BNN_20_GOLDEN_RULES,
    BNN_SATURN_SIGN_CAREERS,
    BNN_PLANETARY_INDUSTRIES,
)

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_NAMES_TA = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
    "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
    "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

JUPITER_LIFESTYLES = {
    1: {
        "en": "Pioneering, dynamic, adventurous, and courageous life with strong self-will.",
        "ta": "துணிச்சல், புதிய முயற்சிகளில் வேகம், தன்னிச்சையான சுபாவம் மற்றும் தலைமைப் பண்பு.",
    },
    2: {
        "en": "Rich, royal, and prosperous life with taste for fine food, comfort, and music.",
        "ta": "வசதியான அரச வாழ்க்கை, அறுசுவை உணவுப் பிரியம், இசை மற்றும் பொருள் சேர்க்கை.",
    },
    3: {
        "en": "Highly intellectual, versatile, trade-oriented, and communication-driven life.",
        "ta": "அபார அறிவாற்றல், வர்த்தக சிந்தனை, எழுத்து, உரையாடல் மற்றும் வியாபாரத் திறன்.",
    },
    4: {
        "en": "Exalted, noble, compassionate, and deeply protective of family and virtues.",
        "ta": "உயர்ந்த உன்னத வாழ்க்கை, தாய் பாசம், இரக்க குணம் மற்றும் நற்குணங்களின் உறைவிடம்.",
    },
    5: {
        "en": "Majestic, dignified, commanding, and righteous living with royal affiliations.",
        "ta": "கம்பீரமான ஆளுமை, நேர்மை, அரசு மற்றும் அதிகாரமிக்கவர்களுடன் நெருங்கிய தொடர்பு.",
    },
    6: {
        "en": "Deeply learned, analytical, service-minded, and possessing profound legal intellect.",
        "ta": "ஆழ்ந்த கல்வி ஞானம், நுட்பமான பகுப்பாய்வுத் திறன் மற்றும் சட்ட நுணுக்க அறிவு.",
    },
    7: {
        "en": "Balanced, diplomatic, elegant living, though challenged by jealousy from close circles.",
        "ta": "நாகரிகமான வாழ்க்கை, நேர்த்தி, சமநிலை; எனினும் உறவினர்களின் பொறாமைக்கு ஆளாகும் வாய்ப்பு.",
    },
    8: {
        "en": "Intensely ambitious, tenacious, research-oriented, and drawn to occult mysteries.",
        "ta": "அடங்காத லட்சிய வேட்கை, ஆழ்ந்த ரகசிய சாஸ்திர ஆர்வம் மற்றும் விடாமுயற்சி.",
    },
    9: {
        "en": "Forest-like detached simplicity, philosophical nobility, high wisdom, and truthfulness.",
        "ta": "வனவாசம் போன்ற எளிமை, தத்துவ ஞானம், உயர்ந்த ஆன்மீகத் தேடல் மற்றும் வாய்மை.",
    },
    10: {
        "en": "Pragmatic, industrious, duty-bound life with substantial earnings from foreign lands.",
        "ta": "கடின உழைப்பு, கடமை உணர்வு மற்றும் வெளியூர்/வெளிநாட்டுத் தொடர்புகளால் வருவாய்.",
    },
    11: {
        "en": "Visionary, philanthropic, pilgrimage-loving, and spiritually elevating life path.",
        "ta": "சமூக சிந்தனை, புண்ணிய ஸ்தல யாத்திரைகள் மற்றும் லட்சியங்களை அடையும் மன உறுதி.",
    },
    12: {
        "en": "Deeply devout, pious, contemplative, and constantly yearning for spiritual liberation.",
        "ta": "தெய்வ பக்தி, ஞானம், மோட்ச சாதனை மற்றும் உலகப் பற்றற்ற உன்னத ஆன்மீக நிலை.",
    },
}


def _diff_signs(from_sign: int, to_sign: int) -> int:
    """Calculate 1-based house difference from from_sign to to_sign (1 to 12)."""
    return ((to_sign - from_sign) % 12) + 1


def evaluate_brighu_naadi(
    planets_data: Dict[str, Dict[str, Any]],
    ascendant_sign: int,
    gender: str = "male",
) -> BrighuNaadiResponse:
    """Core evaluation function for Brighu Naadi Sangraha.

    planets_data expects a dictionary keyed by standard planet names:
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'.
    Each value contains: {'sign_index': 1-12, 'degree': float, 'is_retrograde': bool}.
    """
    # Normalize planet signs
    p_signs: Dict[str, int] = {}
    p_retro: Dict[str, bool] = {}
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        info = planets_data.get(p_name, {})
        s_idx = info.get("sign_index", 1)
        p_signs[p_name] = max(1, min(12, int(s_idx)))
        p_retro[p_name] = bool(info.get("is_retrograde", False))

    jup_sign = p_signs["Jupiter"]
    sat_sign = p_signs["Saturn"]
    rahu_sign = p_signs["Rahu"]
    ketu_sign = p_signs["Ketu"]
    sun_sign = p_signs["Sun"]
    moon_sign = p_signs["Moon"]
    mars_sign = p_signs["Mars"]
    mer_sign = p_signs["Mercury"]
    ven_sign = p_signs["Venus"]

    # 1. Birth Environment & Vastu
    road_data = ROAD_DIRECTION_MAP.get(rahu_sign, {"en": "East to West", "ta": "கிழக்கு முதல் மேற்கு வரை"})
    door_data = DOOR_FACING_MAP.get(rahu_sign, {"en": "Facing East", "ta": "கிழக்கு நோக்கிய தலைவாசல்"})
    city_data = CITY_SECTOR_MAP.get(rahu_sign, {"en": "Eastern part of the City / Town", "ta": "ஊர் / நகரத்தின் கிழக்கு பகுதி"})
    temple_data = TEMPLE_NEAR_BIRTH_MAP.get(sun_sign, {"en": "Shiva Temple", "ta": "ஸ்ரீ சிவபெருமான் ஆலயம்"})

    spouse_sign = ven_sign if gender.lower() == "male" else mars_sign
    spouse_dir_data = SPOUSE_DIRECTION_MAP.get(spouse_sign, {"en": "East", "ta": "கிழக்கு திசை"})

    birth_env = BrighuBirthEnvironment(
        road_direction_en=road_data["en"],
        road_direction_ta=road_data["ta"],
        door_facing_en=door_data["en"],
        door_facing_ta=door_data["ta"],
        city_sector_en=city_data["en"],
        city_sector_ta=city_data["ta"],
        temple_near_birth_en=temple_data["en"],
        temple_near_birth_ta=temple_data["ta"],
        spouse_direction_en=spouse_dir_data["en"],
        spouse_direction_ta=spouse_dir_data["ta"],
        rahu_sign=SIGN_NAMES_EN[rahu_sign - 1],
        ketu_sign=SIGN_NAMES_EN[ketu_sign - 1],
        sun_sign=SIGN_NAMES_EN[sun_sign - 1],
    )

    # 2. Jeeva Karaka (Jupiter) Profile
    jup_house_lagna = _diff_signs(ascendant_sign, jup_sign)
    lifestyle_info = JUPITER_LIFESTYLES.get(jup_sign, JUPITER_LIFESTYLES[1])
    is_prosperity_41 = jup_sign in [3, 9, 12]  # Gemini, Sagittarius, Pisces

    # Map planets in 12 bhavas counted from Jupiter
    bhavas_from_jup: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    for p_name, s_idx in p_signs.items():
        if p_name == "Jupiter":
            continue
        h_from_jup = _diff_signs(jup_sign, s_idx)
        bhavas_from_jup[h_from_jup].append(p_name)

    # Check 4 consecutive empty houses from Jupiter
    empty_adjacent_check = all(len(bhavas_from_jup[h]) == 0 for h in [2, 3, 4, 5])

    # Per BNN Rule (R. G. Rao): Jupiter is Jeeva Karaka for male, Venus for female
    primary_jeeva_planet = "Venus" if gender.lower() == "female" else "Jupiter"

    jeeva_karaka = BrighuJeevaKaraka(
        sign=SIGN_NAMES_EN[jup_sign - 1],
        sign_ta=SIGN_NAMES_TA[jup_sign - 1],
        house_from_lagna=jup_house_lagna,
        lifestyle_profile_en=lifestyle_info["en"],
        lifestyle_profile_ta=lifestyle_info["ta"],
        prosperity_after_41=is_prosperity_41,
        planets_in_bhavas_from_jupiter=bhavas_from_jup,
        empty_adjacent_misery_check=empty_adjacent_check,
        primary_karaka_planet=primary_jeeva_planet,
        gender_applied=gender.lower(),
    )

    # 3. Karma Karaka (Saturn) Profile & Directional Alignment
    sat_house_lagna = _diff_signs(ascendant_sign, sat_sign)

    # Direction of Saturn
    if sat_sign in [1, 5, 9]:
        sat_dir = "East (Fire)"
        sat_dir_signs = [1, 5, 9]
    elif sat_sign in [2, 6, 10]:
        sat_dir = "South (Earth)"
        sat_dir_signs = [2, 6, 10]
    elif sat_sign in [3, 7, 11]:
        sat_dir = "West (Air)"
        sat_dir_signs = [3, 7, 11]
    else:
        sat_dir = "North (Water)"
        sat_dir_signs = [4, 8, 12]

    # Rule 1 & Rule 2: Planets in the same directional trine (1, 5, 9)
    sat_same_dir = [p for p, s in p_signs.items() if s in sat_dir_signs and p != "Saturn"]

    # Rule 3: Planet in the 7th sign to Saturn
    sat_opp_sign = ((sat_sign + 6 - 1) % 12) + 1
    sat_opp_planets = [p for p, s in p_signs.items() if s == sat_opp_sign]

    # Rule 4 & 5: Flanking planets in 2nd and 12th from Saturn
    sat_2nd_sign = (sat_sign % 12) + 1
    sat_12th_sign = ((sat_sign - 2 + 12) % 12) + 1
    sat_2nd_planets = [p for p, s in p_signs.items() if s == sat_2nd_sign]
    sat_12th_planets = [p for p, s in p_signs.items() if s == sat_12th_sign]

    # Saturn in Sign vocational profile from BNN research paper
    sat_sign_info = BNN_SATURN_SIGN_CAREERS.get(sat_sign, {})
    sat_sign_career_en = sat_sign_info.get("en")
    sat_sign_career_ta = sat_sign_info.get("ta")

    # Retrograde backward influence into 12th house (Rule 14)
    sat_retro_behind_en = None
    sat_retro_behind_ta = None
    if p_retro.get("Saturn"):
        behind_sign_idx = sat_12th_sign
        behind_planets = [p for p, s in p_signs.items() if s == behind_sign_idx]
        sat_retro_behind_en = (
            f"Saturn is retrograde, casting backward energy vector toward {SIGN_NAMES_EN[behind_sign_idx - 1]} (12th from Saturn)."
            + (f" Engaging planets: {', '.join(behind_planets)}." if behind_planets else " House is unoccupied.")
        )
        sat_retro_behind_ta = (
            f"சனி பகவான் வக்ரம் பெற்று தனது 12-ஆம் வீடான {SIGN_NAMES_TA[behind_sign_idx - 1]} ராசியை நோக்கி பின்னோக்கிப் பலன் தருகிறார்."
            + (f" அங்கு உள்ள கிரகங்கள்: {', '.join(behind_planets)}." if behind_planets else " அங்கு கிரகங்கள் இல்லை.")
        )

    # Conjunctions with Saturn (same sign)
    sat_conjoined = [p for p, s in p_signs.items() if s == sat_sign and p != "Saturn"]

    career_fields_en: List[str] = []
    career_fields_ta: List[str] = []

    # Combine conjunctions and directional trines into professional fields
    career_influences = set(sat_conjoined + sat_same_dir)
    if "Sun" in career_influences or sat_sign == 5:
        career_fields_en.append("Government Employment & Civil Administration")
        career_fields_ta.append("அரசு உத்தியோகம் மற்றும் பொது நிர்வாகத் துறை")
    if "Mars" in career_influences or sat_sign in [1, 8]:
        career_fields_en.append("Machinery, Mechanical Engineering, Metallurgy & Construction")
        career_fields_ta.append("இயந்திரவியல், பொறியியல், எஃகு மற்றும் கட்டுமானத் துறை")
    if "Mercury" in career_influences or sat_sign in [3, 6]:
        career_fields_en.append("Legal Advocate, Commercial Trade, Auditing & IT/Media")
        career_fields_ta.append("வழக்கறிஞர் பணி, வர்த்தக வணிகம், ஆடிட்டிங் மற்றும் ஊடகம்")
    if "Jupiter" in career_influences or sat_sign in [9, 12]:
        career_fields_en.append("Banking, Educational Institutions, Preaching & Astrology")
        career_fields_ta.append("வங்கித் துறை, கல்வி நிறுவனங்கள், ஆன்மீகம் மற்றும் ஜோதிடம்")
    if "Venus" in career_influences or sat_sign in [2, 7]:
        career_fields_en.append("Jewelry, Bullion, Financial Concerns, Arts & Luxury Commerce")
        career_fields_ta.append("நகை வியாபாரம், நிதி நிறுவனம், நுண்கலைகள் மற்றும் ஆடம்பர வணிகம்")
    if "Rahu" in career_influences:
        career_fields_en.append("Aviation, Photography, Secret Intelligence & Foreign Tech")
        career_fields_ta.append("விமானப் போக்குவரத்து, புகைப்படம், உளவுத்துறை மற்றும் நவீன தொழில்நுட்பம்")
    if "Ketu" in career_influences:
        career_fields_en.append("Chemical Industry, Medical/Surgical Hardware & Occult/Astrology")
        career_fields_ta.append("ரசாயனத் துறை, மருத்துவக் கருவிகள் மற்றும் மறைபொருள் ஆய்வுகள்")
    if "Moon" in career_influences or sat_sign == 4:
        career_fields_en.append("Hospitality, Hotels/Restaurants, Liquid Goods & Overseas Job")
        career_fields_ta.append("ஹோட்டல், உணவு விடுதி, திரவப் பொருட்கள் மற்றும் வெளிநாட்டுப் பணி")

    # Fallback if no specific conjunction
    if not career_fields_en:
        career_fields_en.append("Independent Enterprise, Technical Services & Commercial Trade")
        career_fields_ta.append("சுயதொழில், தொழில்நுட்ப சேவை மற்றும் வர்த்தக வணிகம்")

    # Calculate career starting age using Naadi round: signs from Saturn to Rahu * 2.5 yrs
    signs_to_rahu = ((rahu_sign - sat_sign) % 12)
    if signs_to_rahu == 0:
        signs_to_rahu = 12
    career_start_age = round(signs_to_rahu * 2.5, 1)
    if career_start_age < 16.0:
        career_start_age += 30.0  # Cycle 2 if childhood

    # Check Saturn to Venus relative house
    ven_from_sat = _diff_signs(sat_sign, ven_sign)
    sat_ven_lookup = CAREER_AGE_BY_VENUS_FROM_SATURN.get(ven_from_sat)

    sat_status_en = f"Saturn is stationed in {SIGN_NAMES_EN[sat_sign - 1]} ({sat_house_lagna}th from Lagna) in {sat_dir} direction. "
    sat_status_ta = f"சனி பகவான் {SIGN_NAMES_TA[sat_sign - 1]} ராசியில் (லக்னத்திற்கு {sat_house_lagna}-ல்) {sat_dir} திசையில் அமர்ந்துள்ளார். "

    if p_retro["Saturn"]:
        sat_status_en += "Retrograde Saturn grants exceptional growth in foreign places or cities away from birth."
        sat_status_ta += "வக்கிர சனி அமைந்திருப்பதால் சொந்த ஊரை விட வெளியூர் அல்லது வெளிநாடுகளில் பெருத்த தனலாபம் கிட்டும்."
    else:
        sat_status_en += "Direct Saturn indicates disciplined, steady ascent through personal competence."
        sat_status_ta += "நேர்கதி சனி அமைந்திருப்பதால் முறைப்படியான, தொடர் உழைப்பின் மூலம் நிலையான வளர்ச்சி ஏற்படும்."

    karma_karaka = BrighuKarmaKaraka(
        sign=SIGN_NAMES_EN[sat_sign - 1],
        sign_ta=SIGN_NAMES_TA[sat_sign - 1],
        house_from_lagna=sat_house_lagna,
        career_fields_en=career_fields_en,
        career_fields_ta=career_fields_ta,
        career_start_age_approx=career_start_age,
        career_status_en=sat_status_en,
        career_status_ta=sat_status_ta,
        saturn_sign_career_en=sat_sign_career_en,
        saturn_sign_career_ta=sat_sign_career_ta,
        direction=sat_dir,
        planets_in_same_direction=sat_same_dir,
        planets_in_opposite_direction=sat_opp_planets,
        planets_in_2nd=sat_2nd_planets,
        planets_in_12th=sat_12th_planets,
        is_retrograde=p_retro.get("Saturn", False),
        retrograde_backward_house_influence_en=sat_retro_behind_en,
        retrograde_backward_house_influence_ta=sat_retro_behind_ta,
    )

    # 4. Exact Predicted Timing Milestones
    milestones: List[BrighuTimingMilestone] = []

    # A. Marriage Timing
    ven_from_jup = _diff_signs(jup_sign, ven_sign)
    marr_ages = MARRIAGE_AGE_BY_VENUS_FROM_JUPITER.get(ven_from_jup, [24, 28])
    milestones.append(
        BrighuTimingMilestone(
            category="marriage",
            age_years=marr_ages,
            event_en=f"Auspicious period for marriage union and marital alliance (Ages {', '.join(map(str, marr_ages))})",
            event_ta=f"திருமண பந்தம் மற்றும் மாங்கல்ய யோகம் கைகூடும் வயது ({', '.join(map(str, marr_ages))} ஆண்டுகள்)",
            basis_en=f"Venus posited in {ven_from_jup}th house from Jeeva Karaka Jupiter (2nd round contact)",
            basis_ta=f"ஜீவகாரகன் குருவுக்கு {ven_from_jup}-ஆம் வீட்டில் சுக்கிரன் அமர்ந்து 2-வது சுற்றில் தொடுதல்",
        )
    )

    # B. Career Initiation & Milestone
    if sat_ven_lookup:
        c_start = sat_ven_lookup["start"]
        c_change = sat_ven_lookup.get("change")
        career_ages = [c_start]
        if c_change:
            career_ages.append(c_change)
        milestones.append(
            BrighuTimingMilestone(
                category="career",
                age_years=career_ages,
                event_en=f"Entry into active profession at age {c_start}" + (f", major career transformation at age {c_change}" if c_change else ""),
                event_ta=f"{c_start} வயதில் தொழில் தொடக்கம்" + (f", {c_change} வயதில் தொழில் உயர்வு/மாறுதல்" if c_change else ""),
                basis_en=f"Venus located in {ven_from_sat}th house from Karma Karaka Saturn",
                basis_ta=f"கர்மகாரகன் சனிக்கு {ven_from_sat}-ஆம் வீட்டில் சுக்கிரன் அமர்வு",
            )
        )

    # C. Landed Property & House Construction
    jup_from_mars = _diff_signs(mars_sign, jup_sign)
    prop_ages = PROPERTY_AGE_BY_JUPITER_FROM_MARS.get(jup_from_mars, [32, 44])
    milestones.append(
        BrighuTimingMilestone(
            category="property",
            age_years=prop_ages,
            event_en=f"Acquisition of land, residential house construction, or real estate expansion (Ages {', '.join(map(str, prop_ages))})",
            event_ta=f"சொந்த வீடு கட்டுதல், பூமி வாங்குதல் அல்லது சொத்து சேர்க்கை ({', '.join(map(str, prop_ages))} வயது)",
            basis_en=f"Jupiter stationed in {jup_from_mars}th house from Mars (Jeeva Karaka touching Mars/4th lord in 4th round)",
            basis_ta=f"செவ்வாய்க்கு {jup_from_mars}-ஆம் வீட்டில் குரு அமர்ந்து 4-வது சுற்றில் பூமி காரகத்துவத்தை தூண்டுதல்",
        )
    )

    # D. Name, Fame & Government Honor
    sun_from_jup = _diff_signs(jup_sign, sun_sign)
    fame_ages = FAME_AGE_BY_SUN_FROM_JUPITER.get(sun_from_jup, [34, 46])
    milestones.append(
        BrighuTimingMilestone(
            category="fame",
            age_years=fame_ages,
            event_en=f"Attainment of public honors, promotions, and elevated social name and fame (Ages {', '.join(map(str, fame_ages))})",
            event_ta=f"சமூகப் புகழ், உத்தியோக உயர்வு மற்றும் அரசு அங்கீகாரம் பெறும் வயது ({', '.join(map(str, fame_ages))} ஆண்டுகள்)",
            basis_en=f"Sun positioned in {sun_from_jup}th house from Jeeva Karaka Jupiter",
            basis_ta=f"ஜீவகாரகன் குருவுக்கு {sun_from_jup}-ஆம் வீட்டில் சூரியன் அமர்வு",
        )
    )

    # E. Financial Prosperity Waves
    fin_ages = FINANCE_AGE_BY_VENUS_FROM_JUPITER.get(ven_from_jup, [25, 38, 50])
    milestones.append(
        BrighuTimingMilestone(
            category="finance",
            age_years=fin_ages,
            event_en=f"Major financial windfalls, business profits, and asset accumulation cycles (Ages {', '.join(map(str, fin_ages))})",
            event_ta=f"அபரிமிதமான தனலாபம், நிதி வளர்ச்சி மற்றும் செல்வம் குவியும் சுழற்சிகள் ({', '.join(map(str, fin_ages))} வயது)",
            basis_en=f"Venus situated in {ven_from_jup}th house from Jupiter",
            basis_ta=f"குருவுக்கு {ven_from_jup}-ஆம் வீட்டில் தனகாரகன் சுக்கிரன் அமர்வு",
        )
    )

    # F. Relocation / Change of Place
    moon_from_sat = _diff_signs(sat_sign, moon_sign)
    relo_ages = RELOCATION_AGE_BY_MOON_FROM_SATURN.get(moon_from_sat, [21, 37])
    milestones.append(
        BrighuTimingMilestone(
            category="travel",
            age_years=relo_ages,
            event_en=f"Geographical relocation, residence change, or overseas journey (Ages {', '.join(map(str, relo_ages))})",
            event_ta=f"ஊர் மாறுதல், இடப்பெயர்ச்சி அல்லது தூர தேச பயணம் ({', '.join(map(str, relo_ages))} வயது)",
            basis_en=f"Moon placed in {moon_from_sat}th house from Saturn",
            basis_ta=f"சனிக்கு {moon_from_sat}-ஆம் வீட்டில் சந்திரன் அமர்வு",
        )
    )

    # G. Accident / Physical Caution Milestone
    mars_from_rahu = _diff_signs(rahu_sign, mars_sign)
    acc_ages = ACCIDENT_AGE_BY_MARS_FROM_RAHU.get(mars_from_rahu, [18, 36])
    milestones.append(
        BrighuTimingMilestone(
            category="caution",
            age_years=acc_ages,
            event_en=f"Heightened physical vulnerability, accidents, or bodily injury caution (Ages {', '.join(map(str, acc_ages))})",
            event_ta=f"வாகன விபத்து, காயம் அல்லது அறுவை சிகிச்சை முன்னெச்சரிக்கை காலம் ({', '.join(map(str, acc_ages))} வயது)",
            basis_en=f"Mars located in {mars_from_rahu}th house from Rahu",
            basis_ta=f"ராகுவுக்கு {mars_from_rahu}-ஆம் வீட்டில் செவ்வாய் அமர்வு",
        )
    )

    # H. Father & Mother Critical Longevity Milestones
    sun_from_sat = _diff_signs(sat_sign, sun_sign)
    father_ages = FATHER_CRITICAL_AGE_BY_SUN_FROM_SATURN.get(sun_from_sat, [35])
    milestones.append(
        BrighuTimingMilestone(
            category="family",
            age_years=father_ages,
            event_en=f"Critical health or testing transition for father during native's age {', '.join(map(str, father_ages))}",
            event_ta=f"தந்தையின் உடல்நிலை மற்றும் ஆயுளுக்கான கண்ட காலம் (ஜாதகரின் {', '.join(map(str, father_ages))} வயது)",
            basis_en=f"Saturn having Sun in {sun_from_sat}th house (Saturn's 2nd round transit aspect)",
            basis_ta=f"சனிக்கு {sun_from_sat}-ஆம் வீட்டில் சூரியன் அமர்வு",
        )
    )

    mother_ages = MOTHER_CRITICAL_AGE_BY_MOON_FROM_SATURN.get(moon_from_sat, [32])
    milestones.append(
        BrighuTimingMilestone(
            category="family",
            age_years=mother_ages,
            event_en=f"Critical health period for mother during native's age {', '.join(map(str, mother_ages))}",
            event_ta=f"தாயாரின் உடல்நிலை மற்றும் ஆயுளுக்கான எச்சரிக்கை காலம் (ஜாதகரின் {', '.join(map(str, mother_ages))} வயது)",
            basis_en=f"Saturn having Moon in {moon_from_sat}th house",
            basis_ta=f"சனிக்கு {moon_from_sat}-ஆம் வீட்டில் சந்திரன் அமர்வு",
        )
    )

    # 5. Physical Constitution & Health Markers
    phys_markers: List[BrighuPhysicalMarker] = []

    # Sun constitution
    sun_c = SUN_SIGN_CONSTITUTION.get(sun_sign, SUN_SIGN_CONSTITUTION[1])
    phys_markers.append(
        BrighuPhysicalMarker(
            source_planet="Sun",
            sign=SIGN_NAMES_EN[sun_sign - 1],
            organ_en=sun_c["organ_en"],
            organ_ta=sun_c["organ_ta"],
            indication_en=sun_c["desc_en"],
            indication_ta=sun_c["desc_ta"],
            is_caution=False,
        )
    )

    # Rahu affliction zone
    rahu_a = RAHU_SIGN_AFFLICTIONS.get(rahu_sign, RAHU_SIGN_AFFLICTIONS[1])
    phys_markers.append(
        BrighuPhysicalMarker(
            source_planet="Rahu",
            sign=SIGN_NAMES_EN[rahu_sign - 1],
            organ_en=rahu_a["organ_en"],
            organ_ta=rahu_a["organ_ta"],
            indication_en=rahu_a["desc_en"],
            indication_ta=rahu_a["desc_ta"],
            is_caution=True,
        )
    )

    # Ketu danger mode
    ketu_d = KETU_SIGN_DANGERS.get(ketu_sign, KETU_SIGN_DANGERS[1])
    phys_markers.append(
        BrighuPhysicalMarker(
            source_planet="Ketu",
            sign=SIGN_NAMES_EN[ketu_sign - 1],
            organ_en=ketu_d["type_en"],
            organ_ta=ketu_d["type_ta"],
            indication_en=ketu_d["desc_en"],
            indication_ta=ketu_d["desc_ta"],
            is_caution=True,
        )
    )

    # 6. Classical Rule Matching from Treatise Database (R. G. Rao's Bhrigu Nandi Nadi)
    matched_rules: List[BrighuNaadiRuleMatch] = []

    def _match_pattern(pat: Dict[str, Any]) -> tuple[bool, List[str]]:
        inv: List[str] = []
        checks_performed = 0

        if "all_of" in pat:
            for sub_p in pat["all_of"]:
                ok, sub_inv = _match_pattern(sub_p)
                if not ok:
                    return False, []
                inv.extend(sub_inv)
            return True, inv

        if "gender" in pat:
            checks_performed += 1
            if str(gender).strip().lower() != str(pat["gender"]).strip().lower():
                return False, []

        if "planet" in pat and "sign" in pat:
            checks_performed += 1
            p = pat["planet"]
            s = pat["sign"]
            if p_signs.get(p) != s:
                return False, []
            inv.append(p)

        if "planet_in_sign" in pat:
            checks_performed += 1
            pis = pat["planet_in_sign"]
            p = pis["planet"]
            s = pis["sign"]
            if p_signs.get(p) != s:
                return False, []
            inv.append(p)

        if "planet_is_retrograde" in pat:
            checks_performed += 1
            p = pat["planet_is_retrograde"]
            if not p_retro.get(p, False):
                return False, []
            inv.append(p)

        if "conjunction" in pat:
            checks_performed += 1
            req = pat["conjunction"]
            if req:
                tgt = p_signs.get(req[0])
                if not all(p_signs.get(p) == tgt for p in req):
                    return False, []
                inv.extend(req)

        if "relative_house" in pat:
            checks_performed += 1
            rh = pat["relative_house"]
            p_from = rh["from"]
            p_to = rh["to"]
            exp_h = rh["house"]
            if isinstance(p_to, list):
                if not all(_diff_signs(p_signs[p_from], p_signs[p]) == exp_h for p in p_to):
                    return False, []
                inv.append(p_from)
                inv.extend(p_to)
            else:
                if _diff_signs(p_signs[p_from], p_signs[p_to]) != exp_h:
                    return False, []
                inv.extend([p_from, p_to])

        if "has_planet_in_house" in pat:
            checks_performed += 1
            hph = pat["has_planet_in_house"]
            p_from = hph["from"]
            p_to = hph["planet"]
            exp_h = hph["house"]
            if _diff_signs(p_signs[p_from], p_signs[p_to]) != exp_h:
                return False, []
            inv.extend([p_from, p_to])

        if "planet_in_any_sign" in pat:
            checks_performed += 1
            pias = pat["planet_in_any_sign"]
            p = pias["planet"]
            valid_signs = pias["signs"]
            if p_signs.get(p) not in valid_signs:
                return False, []
            inv.append(p)

        if "sign_exchange" in pat:
            checks_performed += 1
            ex = pat["sign_exchange"]
            p1, p2 = ex[0], ex[1]
            s1, s2 = p_signs.get(p1), p_signs.get(p2)
            lord1 = SIGN_LORDS.get(s1)
            lord2 = SIGN_LORDS.get(s2)
            if not (lord1 == p2 and lord2 == p1):
                return False, []
            inv.extend([p1, p2])

        if "house_empty_from" in pat:
            checks_performed += 1
            he = pat["house_empty_from"]
            p_from = he["from"]
            exp_h = he["house"]
            target_sign = (((p_signs[p_from] - 1 + exp_h - 1) % 12) + 1)
            occupied = any(s == target_sign for s in p_signs.values())
            if occupied:
                return False, []
            inv.append(p_from)

        if "aspects_house_from" in pat:
            checks_performed += 1
            ahf = pat["aspects_house_from"]
            asp_p = ahf["aspecting_planet"]
            from_p = ahf["from_planet"]
            tgt_h = ahf["target_house"]
            tgt_sign = (((p_signs[from_p] - 1 + tgt_h - 1) % 12) + 1)
            diff = _diff_signs(p_signs[asp_p], tgt_sign)
            valid = [7]
            if asp_p == "Mars":
                valid = [4, 7, 8]
            elif asp_p == "Jupiter":
                valid = [5, 7, 9]
            elif asp_p == "Saturn":
                valid = [3, 7, 10]
            if diff not in valid:
                return False, []
            inv.extend([asp_p, from_p])

        if "hemmed_between" in pat:
            checks_performed += 1
            hb = pat["hemmed_between"]
            tgt_p = hb["target_planet"]
            m1 = hb.get("malefic_1", "Saturn")
            m2 = hb.get("malefic_2", "Mars")
            t_s = p_signs.get(tgt_p)
            if not t_s:
                return False, []
            prev_s = ((t_s - 2 + 12) % 12) + 1
            next_s = (t_s % 12) + 1
            m1_s = p_signs.get(m1)
            m2_s = p_signs.get(m2)
            if not ((m1_s == prev_s and m2_s == next_s) or (m2_s == prev_s and m1_s == next_s)):
                return False, []
            inv.extend([tgt_p, m1, m2])

        if pat.get("special_encircle"):
            checks_performed += 1
            j_s = p_signs.get("Jupiter")
            v_s = p_signs.get("Venus")
            if not (j_s and v_s):
                return False, []
            inv.extend(["Jupiter", "Venus"])

        return (checks_performed > 0), inv

    for rule_def in BRIGHU_NAADI_RULES_DATABASE:
        matched, planets_involved = _match_pattern(rule_def["pattern"])
        if matched:
            matched_rules.append(
                BrighuNaadiRuleMatch(
                    rule_id=rule_def["rule_id"],
                    category=rule_def["category"],
                    title_en=rule_def["title_en"],
                    title_ta=rule_def["title_ta"],
                    interpretation_en=rule_def["interpretation_en"],
                    interpretation_ta=rule_def["interpretation_ta"],
                    planets_involved=list(set(planets_involved)),
                    source_page=rule_def["source_page"],
                )
            )

    # 6. Directional Groupings in Bhrigu Nandi Nadi (R. G. Rao System)
    bnn_directional_groups: Dict[str, List[str]] = {
        "East (Fire)": [p for p, s in p_signs.items() if s in [1, 5, 9]],
        "South (Earth)": [p for p, s in p_signs.items() if s in [2, 6, 10]],
        "West (Air)": [p for p, s in p_signs.items() if s in [3, 7, 11]],
        "North (Water)": [p for p, s in p_signs.items() if s in [4, 8, 12]],
    }

    # 7. Rule 10: Rahu-Ketu Axis Career Outside
    def _signs_between(from_s: int, to_s: int) -> List[int]:
        res = []
        curr = (from_s % 12) + 1
        while curr != to_s:
            res.append(curr)
            curr = (curr % 12) + 1
        return res

    rk_side1 = _signs_between(rahu_sign, ketu_sign)
    rk_side2 = _signs_between(ketu_sign, rahu_sign)
    rk_divides = (jup_sign in rk_side1 and sat_sign in rk_side2) or (jup_sign in rk_side2 and sat_sign in rk_side1)

    rahu_ketu_outside_obj = {
        "is_triggered": rk_divides,
        "rule_number": 10,
        "rule_title_en": "Rule 10: Rahu-Ketu Division Causing Profession Outside",
        "rule_title_ta": "விதி 10: ராகு-கேது அச்சு குருவையும் சனியையும் பிரிப்பதால் வெளியூர்/வெளிநாட்டு உத்தியோகம்",
        "explanation_en": (
            "Jeeva Karaka (Jupiter) and Karma Karaka (Saturn) reside on opposite hemispheres of the Rahu-Ketu axis. "
            "Per Bhrigu Nandi Nadi Rule 10 (R. G. Rao system), the native's career is definitively established outside their birthplace or abroad."
            if rk_divides else
            "Jupiter and Saturn reside on the same hemisphere of the Rahu-Ketu axis, anchoring primary career activities within the regional/native territory."
        ),
        "explanation_ta": (
            "ஜீவ காரகரான குருவும் கர்ம காரகரான சனியும் ராகு-கேது அச்சின் எதிரெதிர் பகுதிகளில் அமைந்துள்ளனர். "
            "பிருகு நந்தி நாடி விதி 10-ன் படி, ஜாதகரின் தொழில் பிறந்த ஊருக்கு வெளியே அல்லது வெளிநாடுகளில் அமையும் என்பது உறுதியாகிறது."
            if rk_divides else
            "குருவும் சனியும் ராகு-கேது அச்சின் ஒரே பகுதியில் இருப்பதால் உள்ளூர் அல்லது சொந்த மாநிலத்திற்குள்ளேயே தொழில் அமையும் வாய்ப்பு அதிகம்."
        ),
    }

    # 8. Evaluation of the 20 Bhrigu Nandi Nadi Golden Rules
    bnn_20_evaluations: List[Dict[str, Any]] = []
    for r in BNN_20_GOLDEN_RULES:
        r_num = r["rule_number"]
        is_active = False
        notes_en = ""
        notes_ta = ""

        if r_num == 1:
            planets_found = sat_2nd_planets + sat_12th_planets + sat_opp_planets + sat_same_dir
            if planets_found:
                is_active = True
                notes_en = f"Saturn's karakatva is actively triggered by {', '.join(set(planets_found))} situated in 2nd, 12th, 7th, or 5th/9th trines."
                notes_ta = f"சனியின் கர்ம காரகத்துவம் 2, 12, 7 மற்றும் 5, 9 திரிகோணங்களில் உள்ள {', '.join(set(planets_found))} கிரகங்களால் தீவிரமாகத் தூண்டப்படுகிறது."
        elif r_num == 2:
            if len(sat_same_dir) > 0:
                is_active = True
                notes_en = f"Planets in {sat_dir} direction ({', '.join(sat_same_dir)} + Saturn) work together to shape professional destiny."
                notes_ta = f"{sat_dir} திசையில் நிற்கும் {', '.join(sat_same_dir)} மற்றும் சனி ஒன்றிணைந்து தொழில் விதியை உருவாக்குகின்றனர்."
        elif r_num == 3:
            if sat_opp_planets:
                is_active = True
                notes_en = f"Saturn directly aspects {', '.join(sat_opp_planets)} across 7th sign, generating dynamic career interactions."
                notes_ta = f"சனி 7-ஆம் பாவத்தில் உள்ள {', '.join(sat_opp_planets)} கிரகங்களை நேரடியாகப் பார்த்து கர்மத்தில் நேரடித் தாக்கம் செலுத்துகிறார்."
        elif r_num == 4:
            if sat_2nd_planets or sat_12th_planets:
                is_active = True
                notes_en = f"Saturn is flanked by {', '.join(sat_12th_planets) or 'Empty'} in 12th and {', '.join(sat_2nd_planets) or 'Empty'} in 2nd house."
                notes_ta = f"சனிக்கு 12-ல் {', '.join(sat_12th_planets) or 'எதுவுமில்லை'} மற்றும் 2-ல் {', '.join(sat_2nd_planets) or 'எதுவுமில்லை'} கிரகங்கள் சூழ்ந்துள்ளன."
        elif r_num == 6:
            retro_in_2nd_from_sat = [p for p in sat_2nd_planets if p_retro.get(p)]
            if retro_in_2nd_from_sat:
                is_active = True
                notes_en = f"Retrograde planet {', '.join(retro_in_2nd_from_sat)} in 2nd house moves backward toward Saturn, causing career friction."
                notes_ta = f"2-ல் நிற்கும் வக்ர கிரகம் {', '.join(retro_in_2nd_from_sat)} பின்னோக்கி சனியை நோக்கி நகர்ந்து தொழிலில் இழுபறியைத் தரும்."
        elif r_num == 10:
            is_active = rk_divides
            notes_en = rahu_ketu_outside_obj["explanation_en"]
            notes_ta = rahu_ketu_outside_obj["explanation_ta"]
        elif r_num == 14:
            if p_retro.get("Saturn") or p_retro.get("Jupiter"):
                is_active = True
                notes_en = "Retrograde karaka (Saturn/Jupiter) projects energetic half-aspect backward into 12th house, neutralizing past vulnerabilities."
                notes_ta = "வக்ர காரகன் (சனி/குரு) தனது 12-ஆம் வீட்டை நோக்கி பின்னோக்கிப் பார்வை செலுத்தி முந்தைய தோஷங்களை நீக்குகிறார்."
        elif r_num == 19:
            retro_in_12th = [p for p in sat_12th_planets if p_retro.get(p)]
            if retro_in_12th:
                is_active = True
                notes_en = f"12th house planet {', '.join(retro_in_12th)} is retrograde, retreating backward away from Saturn and sparing career from obstruction."
                notes_ta = f"12-ல் உள்ள {', '.join(retro_in_12th)} வக்ரமடைந்து சனியை விட்டு பின்வாங்குவதால் தொழில் பாதிப்பு தவிர்க்கப்படுகிறது."
        elif r_num == 20:
            sat_enemies = BNN_PLANETARY_FRIENDSHIP["Saturn"]["inimical"]
            retro_enemies_in_2nd = [p for p in sat_2nd_planets if p in sat_enemies and p_retro.get(p)]
            if retro_enemies_in_2nd:
                is_active = True
                notes_en = f"Inimical planet {', '.join(retro_enemies_in_2nd)} in 2nd house is retrograde, striking backward into Saturn's vocational domain."
                notes_ta = f"2-ல் உள்ள பகை கிரகம் {', '.join(retro_enemies_in_2nd)} வக்ரமடைந்து சனியை பின்னோக்கித் தாக்கி தடைகளை உருவாக்குகிறது."

        bnn_20_evaluations.append({
            "rule_number": r_num,
            "title_en": r["title_en"],
            "title_ta": r["title_ta"],
            "is_active": is_active,
            "principle_en": r["principle_en"],
            "principle_ta": r["principle_ta"],
            "chart_evidence_en": notes_en if is_active else "Condition neutral / inactive in this natal chart.",
            "chart_evidence_ta": notes_ta if is_active else "இந்த ஜாதகத்தில் இந்த விதியின் தாக்கம் இயல்பான சமநிலையில் உள்ளது.",
            "source_ref": r["source_ref"],
        })

    return BrighuNaadiResponse(
        treatise_metadata=BRIGHU_NAADI_METADATA,
        bnn_research_metadata=BHRIGU_NANDI_NADI_RESEARCH_METADATA,
        birth_environment=birth_env,
        jeeva_karaka=jeeva_karaka,
        karma_karaka=karma_karaka,
        timing_milestones=milestones,
        physical_health_markers=phys_markers,
        matched_rules=matched_rules,
        bnn_directional_groups=bnn_directional_groups,
        bnn_20_rules_evaluations=bnn_20_evaluations,
        rahu_ketu_axis_career_outside=rahu_ketu_outside_obj,
    )
