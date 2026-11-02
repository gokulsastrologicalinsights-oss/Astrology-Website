"""Career Evaluation Module: Service vs Self-Employment, Technical Scoring, and Writing Talents.

Based on empirical researches:
1. S.N. Kapoor: 'Service or Self-employment? Test the Thumb Rules' (pp. 32-54)
2. R.C. Sharma: 'Profession and Planetary Influences' (pp. 50-72)
3. Col. A.K. Gour: 'Authors and Journalists: An Astrological Enquiry' (pp. 80-94)
4. Kusum Vashishtha: 'Successful Indian Women in Different Fields' (pp. 90-108)
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from app.services.kn_rao_engine.models import (
    ServiceVsSelfEmploymentResult,
    TechnicalProfessionResult,
    AuthorJournalistResult,
)

SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

SIGN_NAMES_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

SIGN_NAMES_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

# Tattwas (Elements)
# Agni (Fire): 1, 5, 9
# Prithvi (Earth): 2, 6, 10
# Vayu (Air): 3, 7, 11
# Jala (Water): 4, 8, 12
TATTWA_MAPPING: Dict[int, str] = {
    1: "Agni", 5: "Agni", 9: "Agni",
    2: "Prithvi", 6: "Prithvi", 10: "Prithvi",
    3: "Vayu", 7: "Vayu", 11: "Vayu",
    4: "Jala", 8: "Jala", 12: "Jala",
}

# Poorna Parmatmansha Planets (BPHS Ch. 2, S.N. Kapoor p. 38)
POORNA_PARMATMANSHA_PLANETS: Set[str] = {"Sun", "Moon", "Mars", "Rahu"}
JEEVAMS_PLANETS: Set[str] = {"Mercury", "Jupiter", "Venus", "Saturn", "Ketu"}

# Parmatmansha Nakshatras (12 Nakshatras ruled by Sun, Moon, Mars, Rahu)
# Sun: Krittika (3), U.Phalguni (12), U.Ashadha (21)
# Moon: Rohini (4), Hasta (13), Shravana (22)
# Mars: Mrigashira (5), Chitra (14), Dhanishta (23)
# Rahu: Ardra (6), Swati (15), Shatabhisha (24)
PARMATMANSHA_NAKSHATRAS: Set[str] = {
    "krittika", "uttara phalguni", "uttara ashadha",
    "rohini", "hasta", "shravana",
    "mrigashira", "chitra", "dhanishta",
    "ardra", "swati", "shatabhisha", "satabhisha"
}

EXALTATION_SIGNS: Dict[str, int] = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7, "Rahu": 2, "Ketu": 8
}

DEBILITATION_SIGNS: Dict[str, int] = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
    "Jupiter": 10, "Venus": 6, "Saturn": 1, "Rahu": 8, "Ketu": 2
}

OWN_SIGNS: Dict[str, Set[int]] = {
    "Sun": {5}, "Moon": {4}, "Mars": {1, 8}, "Mercury": {3, 6},
    "Jupiter": {9, 12}, "Venus": {2, 7}, "Saturn": {10, 11},
    "Rahu": {11}, "Ketu": {8}
}

TECHNICAL_PLANETS: Set[str] = {"Saturn", "Mars", "Rahu", "Ketu"}
NON_TECHNICAL_PLANETS: Set[str] = {"Sun", "Moon", "Mercury", "Jupiter", "Venus"}


# ---------------------------------------------------------------------------
# Jaimini Karaka & Aspect Utilities
# ---------------------------------------------------------------------------

def calculate_jaimini_7_karakas(planets_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Calculate 7 Jaimini Chara Karakas by sorting planets by degree_in_sign descending.
    Excludes Rahu and Ketu according to classical 7-karaka scheme (BPHS / K.N. Rao).
    """
    candidates = []
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if p in planets_data:
            candidates.append((p, planets_data[p].get("degree_in_sign", 0.0)))
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    roles = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    karaka_map = {}
    for i, role in enumerate(roles):
        if i < len(candidates):
            karaka_map[role] = candidates[i][0]
            karaka_map[candidates[i][0]] = role
    return karaka_map


def get_jaimini_aspects_for_sign(sign_idx: int) -> Set[int]:
    """Compute signs aspected by sign_idx using Jaimini Rashi Drishti rules.
    - Movable (1, 4, 7, 10) aspects all Fixed signs (2, 5, 8, 11) except adjacent.
    - Fixed (2, 5, 8, 11) aspects all Movable signs (1, 4, 7, 10) except adjacent.
    - Dual (3, 6, 9, 12) aspects all other Dual signs.
    """
    movable = {1, 4, 7, 10}
    fixed = {2, 5, 8, 11}
    dual = {3, 6, 9, 12}

    if sign_idx in movable:
        # all fixed except adjacent sign
        adjacent = ((sign_idx) % 12) + 1
        return {s for s in fixed if s != adjacent}
    elif sign_idx in fixed:
        # all movable except adjacent previous sign
        adjacent = ((sign_idx - 2) % 12) + 1
        return {s for s in movable if s != adjacent}
    elif sign_idx in dual:
        return {s for s in dual if s != sign_idx}
    return set()


def calculate_karakamsha_sign(
    planets_data: Dict[str, Dict[str, Any]],
    d9_planets: Dict[str, Dict[str, Any]]
) -> Tuple[int, str]:
    """Calculate Karakamsha (Navamsha sign of Atmakaraka)."""
    karakas = calculate_jaimini_7_karakas(planets_data)
    ak_planet = karakas.get("AK", "Sun")
    
    if ak_planet in d9_planets:
        sign_idx = d9_planets[ak_planet]["sign_index"]
        return sign_idx, SIGN_NAMES_EN[sign_idx]
    
    # Fallback to D1 sign if D9 missing
    sign_idx = planets_data.get(ak_planet, {}).get("sign_index", 1)
    return sign_idx, SIGN_NAMES_EN[sign_idx]


def check_parashari_aspect(aspecting_sign: int, aspecting_planet: str, target_sign: int) -> bool:
    """Check if aspecting_planet in aspecting_sign casts a classical Parashari aspect on target_sign."""
    dist = ((target_sign - aspecting_sign) % 12) + 1
    if dist == 7:
        return True
    if aspecting_planet == "Mars" and dist in (4, 8):
        return True
    if aspecting_planet == "Jupiter" and dist in (5, 9):
        return True
    if aspecting_planet == "Saturn" and dist in (3, 10):
        return True
    return False


def get_parashari_aspects_for_planet(planet: str, planet_sign: int) -> Set[int]:
    """Get all signs aspected by a planet in planet_sign using classical Parashari Drishti."""
    aspected = set()
    for s in range(1, 13):
        if s != planet_sign and check_parashari_aspect(planet_sign, planet, s):
            aspected.add(s)
    return aspected


# ---------------------------------------------------------------------------
# 1. S.N. Kapoor: Service vs Self-Employment Evaluator
# ---------------------------------------------------------------------------

def evaluate_service_vs_self_employment(
    d1_planets: Dict[str, Dict[str, Any]],
    lagna_sign: int,
) -> ServiceVsSelfEmploymentResult:
    """Evaluate propensity of Self-Employment vs Service using S.N. Kapoor's thumb rules."""
    # 1. House distributions
    in_7_to_12 = 0
    in_10_to_3 = 0
    in_4_to_6 = 0

    poorna_parmatmansha_count = 0
    parmatmansha_nakshatras_count = 0

    tattwas: Dict[str, int] = {"Agni": 0, "Prithvi": 0, "Vayu": 0, "Jala": 0}
    # Add Lagna's tattwa
    lagna_tattwa = TATTWA_MAPPING.get(lagna_sign, "Agni")
    tattwas[lagna_tattwa] += 1

    sun_info = d1_planets.get("Sun")
    moon_info = d1_planets.get("Moon")
    saturn_info = d1_planets.get("Saturn")

    # 10th lord and Lagna lord
    lagna_lord = SIGN_LORDS[lagna_sign]
    tenth_sign = ((lagna_sign - 1 + 9) % 12) + 1
    tenth_lord = SIGN_LORDS[tenth_sign]

    for p_name, p_data in d1_planets.items():
        if p_name in ("Ascendant", "Lagna"):
            continue
        h = p_data.get("house", 1)
        s_idx = p_data.get("sign_index", 1)

        # Count in zones
        if 7 <= h <= 12:
            in_7_to_12 += 1
        if h in (10, 11, 12, 1, 2, 3):
            in_10_to_3 += 1
        if 4 <= h <= 6:
            in_4_to_6 += 1

        # Parmatmansha planets
        if p_name in POORNA_PARMATMANSHA_PLANETS:
            if 7 <= h <= 12 or h in (10, 11, 12, 1, 2, 3):
                poorna_parmatmansha_count += 1

        # Parmatmansha nakshatra check
        nak_name = str(p_data.get("nakshatra_name", "")).lower()
        if any(pn in nak_name for pn in PARMATMANSHA_NAKSHATRAS):
            parmatmansha_nakshatras_count += 1

        # Tattwa
        elem = TATTWA_MAPPING.get(s_idx, "Agni")
        tattwas[elem] += 1

    agni_vayu = tattwas["Agni"] + tattwas["Vayu"]
    prithvi_jala = tattwas["Prithvi"] + tattwas["Jala"]

    # Day / Night birth from Sun
    is_day_birth = False
    is_sunset_to_midnight = False
    if sun_info:
        sun_h = sun_info.get("house", 1)
        is_day_birth = (7 <= sun_h <= 12)
        is_sunset_to_midnight = (sun_h in (4, 5, 6))

    # Saturn Gocharastha vs Agocharastha
    saturn_status = "Neutral"
    saturn_aspects_career = False
    if saturn_info:
        sat_sign = saturn_info.get("sign_index", 1)
        sat_house = saturn_info.get("house", 1)
        is_exalted = (sat_sign == EXALTATION_SIGNS.get("Saturn"))
        is_own = (sat_sign in OWN_SIGNS.get("Saturn", set()))
        is_moolatrikona = (sat_sign == 11)
        is_debilitated = (sat_sign == DEBILITATION_SIGNS.get("Saturn"))
        in_dusthana = (sat_house in (6, 8, 12))

        if is_exalted or is_moolatrikona or (is_own and not in_dusthana):
            saturn_status = "Gocharastha (Favorable/Strong)"
        elif is_debilitated or in_dusthana:
            saturn_status = "Agocharastha (Adverse/Weak)"

        # Check if Saturn aspects Moon, 10th house, 10th lord, or Lagna
        moon_sign = moon_info.get("sign_index", 1) if moon_info else 1
        tenth_lord_sign = d1_planets.get(tenth_lord, {}).get("sign_index", 1)
        lagna_lord_sign = d1_planets.get(lagna_lord, {}).get("sign_index", 1)

        aspects_moon = check_parashari_aspect(sat_sign, "Saturn", moon_sign)
        aspects_tenth_house = check_parashari_aspect(sat_sign, "Saturn", tenth_sign) or (sat_house == 10)
        aspects_tenth_lord = check_parashari_aspect(sat_sign, "Saturn", tenth_lord_sign) or (tenth_lord == "Saturn")
        aspects_lagna = check_parashari_aspect(sat_sign, "Saturn", lagna_sign) or (sat_house == 1)
        aspects_lagna_lord = check_parashari_aspect(sat_sign, "Saturn", lagna_lord_sign) or (lagna_lord == "Saturn")

        if aspects_moon or aspects_tenth_house or aspects_tenth_lord or aspects_lagna or aspects_lagna_lord:
            saturn_aspects_career = True

    # Planetary Avasthas
    def get_avastha(planet_name: str) -> str:
        p = d1_planets.get(planet_name)
        if not p:
            return "Neutral"
        s = p.get("sign_index", 1)
        if s == EXALTATION_SIGNS.get(planet_name):
            return "Exalted (Uchcha)"
        if s == DEBILITATION_SIGNS.get(planet_name):
            return "Debilitated (Neecha)"
        if s in OWN_SIGNS.get(planet_name, set()):
            return "Own Sign (Swakshetra)"
        return "Normal"

    ll_avastha = get_avastha(lagna_lord)
    tl_avastha = get_avastha(tenth_lord)

    # -----------------------------------------------------------------------
    # Score Accumulation based on S.N. Kapoor Rules (p. 44)
    # -----------------------------------------------------------------------
    self_emp_points = 0
    service_points = 0
    factors_en: List[str] = []
    factors_ta: List[str] = []

    # Factor (a): 5 or more planets in 7th to 12th OR 10th to 3rd
    if in_7_to_12 >= 5 or in_10_to_3 >= 5:
        self_emp_points += 30
        factors_en.append(f"Concentration of planets in visible/executive houses ({max(in_7_to_12, in_10_to_3)} planets in 7th-12th or 10th-3rd) strongly promotes self-employment.")
        factors_ta.append(f"7 முதல் 12 அல்லது 10 முதல் 3 பாவங்களில் அதிக கிரகங்கள் ({max(in_7_to_12, in_10_to_3)} கிரகங்கள்) அமைந்திருப்பது சுயதொழில்/வணிக யோகத்தை வலுவாக உருவாக்குகிறது.")
    elif in_4_to_6 >= 3:
        service_points += 20
        factors_en.append(f"Planets concentrated in subordination houses 4th to 6th ({in_4_to_6} planets) incline towards structured employment/service.")
        factors_ta.append(f"4 முதல் 6 ஆம் பாவங்களில் கிரகங்கள் ({in_4_to_6} கிரகங்கள்) அமைந்திருப்பது உத்தியோக ஈடுபாட்டை அதிகரிக்கிறது.")

    # Factor (b): Saturn role
    if "Gocharastha" in saturn_status and saturn_aspects_career:
        self_emp_points += 20
        factors_en.append("Gocharastha (exalted/own/strong) Saturn influencing career anchors authoritative self-employment or large-scale enterprise.")
        factors_ta.append("பலம் பெற்ற கோச்சரஸ்த சனி பத்தாம் பாவம் அல்லது சந்திரனைத் தொடர்பு கொண்டு சுயதொழில் தலைமைத்துவத்தை அருளுகிறார்.")
    elif "Agocharastha" in saturn_status and saturn_aspects_career:
        service_points += 25
        factors_en.append("Agocharastha / functional malefic Saturn influencing Moon or 10th house/lord is the classic signature of professional service.")
        factors_ta.append("அகோச்சரஸ்த சனி சந்திரன் அல்லது பத்தாம் பாவத்தைப் பார்ப்பது உத்தியோகத்தில் பணிபுரிவதற்கான முக்கிய விதியாகும்.")

    # Factor (c): Poorna Parmatmansha planets in upper houses
    if poorna_parmatmansha_count >= 3:
        self_emp_points += 25
        factors_en.append(f"At least 3 Poorna Parmatmansha planets ({poorna_parmatmansha_count} planets: Sun/Moon/Mars/Rahu) occupy 7th-12th or 10th-3rd, conferring independent authority.")
        factors_ta.append(f"பூரண பரமாத்மாம்ச கிரகங்கள் ({poorna_parmatmansha_count} கிரகங்கள்: சூரியன்/சந்திரன்/செவ்வாய்/ராகு) 7-12ல் அமர்ந்து தன்னாட்சி அதிகாரத்தை அளிக்கின்றன.")

    # Factor (d): Lagna Lord / 10th Lord avastha
    if "Exalted" in ll_avastha or "Exalted" in tl_avastha:
        self_emp_points += 15
        factors_en.append("Lagna Lord or 10th Lord is exalted, bestowing self-driven enterprise and high standing.")
        factors_ta.append("லக்னாதிபதி அல்லது 10-ஆம் அதிபதி உச்சம் பெற்று சுயமாக இயங்கும் வலிமையை அளிக்கிறார்.")
    elif "Debilitated" in ll_avastha or "Debilitated" in tl_avastha:
        service_points += 20
        factors_en.append("Lagna Lord or 10th Lord in debility inclines the native towards organizational service and corporate employment.")
        factors_ta.append("லக்னாதிபதி அல்லது பத்தாம் அதிபதி நீசம் பெற்று பிறரிடம் பணிபுரியும் உத்தியோக அமைப்பைத் தருகிறார்.")

    # Factor (e): Tattwa distribution & Parmatmansha Nakshatras
    if agni_vayu >= 6 or tattwas["Vayu"] >= 3:
        self_emp_points += 15
        factors_en.append(f"Dominance of Agni & Vayu elements ({agni_vayu} planets) provides dynamic vision, enterprise, and commercial initiative.")
        factors_ta.append(f"நெருப்பு மற்றும் காற்று தத்துவங்கள் ({agni_vayu} கிரகங்கள்) தொழில் முனைவு மற்றும் வணிக உத்வேகத்தை உருவாக்குகின்றன.")
    elif prithvi_jala >= 6 or tattwas["Prithvi"] >= 3:
        service_points += 15
        factors_en.append(f"Dominance of Prithvi & Jala elements ({prithvi_jala} planets) promotes grounded dependability, routine stability, and institutional service.")
        factors_ta.append(f"நிலம் மற்றும் நீர் தத்துவங்கள் ({prithvi_jala} கிரகங்கள்) நிறுவனங்களில் நிலையான உத்தியோகப் பணியைத் தருகின்றன.")

    if parmatmansha_nakshatras_count >= 5:
        self_emp_points += 10
        factors_en.append(f"Five or more planets ({parmatmansha_nakshatras_count}) in Parmatmansha nakshatras enhance independent status.")
        factors_ta.append(f"பரமாத்மாம்ச நட்சத்திரங்களில் 5-க்கும் மேற்பட்ட கிரகங்கள் ({parmatmansha_nakshatras_count}) அமர்ந்து சுயமரியாதையை உயர்த்துகின்றன.")
    elif parmatmansha_nakshatras_count <= 3:
        service_points += 10
        factors_en.append("Fewer planets in Parmatmansha nakshatras favor structured service.")
        factors_ta.append("குறைவான பரமாத்மாம்ச நட்சத்திர இருப்பு நிறுவன வேலைவாய்ப்பை ஆதரிக்கிறது.")

    # Factor (f): Day vs Night birth
    if is_day_birth:
        self_emp_points += 10
        factors_en.append("Day birth (Sun in bright half) classically elevates self-employment propensity (3:2 ratio).")
        factors_ta.append("பகல் பிறப்பு (சூரியன் 7-12ல்) சுயதொழில் வாய்ப்பை உயர்த்துகிறது.")
    elif is_sunset_to_midnight:
        service_points += 15
        factors_en.append("Birth between sunset and midnight (Sun in 4th, 5th, or 6th) indicates service inclination (66% probability).")
        factors_ta.append("சூரிய அஸ்தமனம் முதல் நள்ளிரவு வரையிலான பிறப்பு (சூரியன் 4, 5, 6-ல்) உத்தியோக வாய்ப்பை 66% உறுதி செய்கிறது.")

    # Calculate final percentages
    total_raw = self_emp_points + service_points
    if total_raw == 0:
        self_emp_pct = 50.0
        service_pct = 50.0
    else:
        self_emp_pct = round((self_emp_points / total_raw) * 100.0, 1)
        service_pct = round((service_points / total_raw) * 100.0, 1)

    if self_emp_pct >= 60.0:
        verdict = "Self-Employment / Business / Independent Practice"
        verdict_ta = "சுயதொழில் / வணிகம் / சுதந்திர தொழில்முறை"
    elif service_pct >= 60.0:
        verdict = "Service / Employment in Public or Private Organization"
        verdict_ta = "அரசு அல்லது தனியார் நிறுவன உத்தியோகம்"
    else:
        verdict = "Mixed / Early Service Transitioning to Business"
        verdict_ta = "ஆரம்ப கால உத்தியோகம் பின் சுயதொழில் வாய்ப்பு"

    return ServiceVsSelfEmploymentResult(
        planets_in_7_to_12=in_7_to_12,
        planets_in_10_to_3=in_10_to_3,
        planets_in_4_to_6=in_4_to_6,
        poorna_parmatmansha_count=poorna_parmatmansha_count,
        parmatmansha_nakshatras_count=parmatmansha_nakshatras_count,
        tattwa_distribution=tattwas,
        agni_vayu_count=agni_vayu,
        prithvi_jala_count=prithvi_jala,
        is_day_birth=is_day_birth,
        is_sunset_to_midnight=is_sunset_to_midnight,
        saturn_status=saturn_status,
        saturn_aspects_career=saturn_aspects_career,
        lagna_lord_avastha=ll_avastha,
        tenth_lord_avastha=tl_avastha,
        self_employment_probability=self_emp_pct,
        service_probability=service_pct,
        primary_verdict=verdict,
        verdict_tamil=verdict_ta,
        rule_score_breakdown={
            "self_employment_points": self_emp_points,
            "service_points": service_points,
        },
        contributing_factors=factors_en,
        contributing_factors_tamil=factors_ta,
    )


# ---------------------------------------------------------------------------
# 2. R.C. Sharma: Technical vs Non-Technical Career Evaluator
# ---------------------------------------------------------------------------

def evaluate_technical_profession(
    d1_planets: Dict[str, Dict[str, Any]],
    d9_planets: Dict[str, Dict[str, Any]],
    lagna_sign: int,
) -> TechnicalProfessionResult:
    """Evaluate Technical vs Non-Technical career using R.C. Sharma's 4-fold mathematical scoring model.
    Non-technical planets (Sun, Moon, Mercury, Jupiter, Venus) = +1
    Technical planets (Saturn, Mars, Rahu, Ketu) = -1
    Evaluated across:
    1. Karakamsha (10th house & 10th lord)
    2. Janma Lagna (10th house & 10th lord)
    3. Chandra Lagna (10th house & 10th lord)
    4. Nakshatras of 10th house and 10th lord
    """
    karakamsha_sign_idx, karakamsha_sign_name = calculate_karakamsha_sign(d1_planets, d9_planets)
    
    # Sign index of Moon
    moon_info = d1_planets.get("Moon")
    moon_sign_idx = moon_info.get("sign_index", 1) if moon_info else 1

    # 1. Karakamsha 10th
    kk_10th_sign = ((karakamsha_sign_idx - 1 + 9) % 12) + 1
    kk_10th_lord = SIGN_LORDS[kk_10th_sign]
    score_karakamsha = 0

    # Planets influencing Karakamsha 10th via Jaimini aspects or placement
    kk_aspected_signs = get_jaimini_aspects_for_sign(kk_10th_sign)
    for p_name, p_data in d1_planets.items():
        if p_name in ("Ascendant", "Lagna"):
            continue
        p_sign = p_data.get("sign_index", 1)
        # Posited in 10th from Karakamsha or aspecting it via Jaimini aspect
        if p_sign == kk_10th_sign or p_sign in kk_aspected_signs:
            score_karakamsha += (-1 if p_name in TECHNICAL_PLANETS else +1)
        # Influencing 10th lord from Karakamsha
        if p_name == kk_10th_lord:
            score_karakamsha += (-1 if p_name in TECHNICAL_PLANETS else +1)

    # 2. Janma Lagna 10th
    lagna_10th_sign = ((lagna_sign - 1 + 9) % 12) + 1
    lagna_10th_lord = SIGN_LORDS[lagna_10th_sign]
    score_lagna = 0
    lagna_10th_lord_sign = d1_planets.get(lagna_10th_lord, {}).get("sign_index", 1)

    for p_name, p_data in d1_planets.items():
        if p_name in ("Ascendant", "Lagna"):
            continue
        p_sign = p_data.get("sign_index", 1)
        p_house = p_data.get("house", 1)
        is_posited_10th = (p_house == 10)
        is_aspected_10th = check_parashari_aspect(p_sign, p_name, lagna_10th_sign)
        is_conjunct_lord = (p_sign == lagna_10th_lord_sign and p_name != lagna_10th_lord)
        is_aspecting_lord = check_parashari_aspect(p_sign, p_name, lagna_10th_lord_sign)

        if is_posited_10th or is_aspected_10th or is_conjunct_lord or is_aspecting_lord:
            score_lagna += (-1 if p_name in TECHNICAL_PLANETS else +1)

    if lagna_10th_lord in TECHNICAL_PLANETS:
        score_lagna -= 1
    else:
        score_lagna += 1

    # 3. Chandra Lagna 10th
    moon_10th_sign = ((moon_sign_idx - 1 + 9) % 12) + 1
    moon_10th_lord = SIGN_LORDS[moon_10th_sign]
    score_moon = 0
    moon_10th_lord_sign = d1_planets.get(moon_10th_lord, {}).get("sign_index", 1)

    for p_name, p_data in d1_planets.items():
        if p_name in ("Ascendant", "Lagna"):
            continue
        p_sign = p_data.get("sign_index", 1)
        p_dist_from_moon = ((p_sign - moon_sign_idx) % 12) + 1
        is_posited_10th = (p_dist_from_moon == 10)
        is_aspected_10th = check_parashari_aspect(p_sign, p_name, moon_10th_sign)
        is_conjunct_lord = (p_sign == moon_10th_lord_sign and p_name != moon_10th_lord)
        is_aspecting_lord = check_parashari_aspect(p_sign, p_name, moon_10th_lord_sign)

        if is_posited_10th or is_aspected_10th or is_conjunct_lord or is_aspecting_lord:
            score_moon += (-1 if p_name in TECHNICAL_PLANETS else +1)

    if moon_10th_lord in TECHNICAL_PLANETS:
        score_moon -= 1
    else:
        score_moon += 1

    # 4. Nakshatra dispositor influence
    score_nak = 0
    tenth_lord_info = d1_planets.get(lagna_10th_lord)
    if tenth_lord_info:
        star_lord = tenth_lord_info.get("star_lord", "")
        if star_lord in TECHNICAL_PLANETS:
            score_nak -= 1
        elif star_lord in NON_TECHNICAL_PLANETS:
            score_nak += 1

    # Check Rahu's specific connection to engineering (R.C. Sharma finding, p. 51)
    rahu_info = d1_planets.get("Rahu")
    rahu_engineering = False
    if rahu_info:
        rahu_h = rahu_info.get("house", 1)
        rahu_sign = rahu_info.get("sign_index", 1)
        if rahu_h in (10, 1) or rahu_sign in (lagna_10th_sign, kk_10th_sign, moon_10th_sign):
            rahu_engineering = True
        elif check_parashari_aspect(rahu_sign, "Rahu", lagna_10th_sign):
            rahu_engineering = True

    total_score = score_karakamsha + score_lagna + score_moon + score_nak

    tech_influences = [p for p in TECHNICAL_PLANETS if p in d1_planets and d1_planets[p].get("house") in (1, 10)]
    non_tech_influences = [p for p in NON_TECHNICAL_PLANETS if p in d1_planets and d1_planets[p].get("house") in (1, 10)]

    if total_score <= -2:
        cat = "Technical (Engineering / IT / Electronics / Telecommunications)"
        cat_ta = "தொழில்நுட்பம் (பொறியியல் / தகவல் தொழில்நுட்பம் / மென்பொருள் / மின்னணுவியல்)"
        interp = (
            f"The 4-fold career scoring model shows a decisively negative score ({total_score}), "
            "indicating heavy influence of technical planets (Saturn, Mars, Rahu, Ketu) on the 10th houses "
            "from Lagna, Moon, and Karakamsha. Native thrives in engineering, software development, "
            "hardware, machinery, or technical sciences."
        )
        interp_ta = (
            f"நான்கு முனை தொழில் ஆய்வு மாதிரி எதிர்மறை மதிப்பெண்ணை ({total_score}) காட்டுகிறது. "
            "லக்னம், சந்திரன் மற்றும் காரகாம்சத்திலிருந்து 10-ஆம் பாவகங்களில் சனி, செவ்வாய், ராகு ஆகிய தொழில்நுட்ப "
            "கிரகங்களின் ஆதிக்கம் நிறைந்துள்ளதால் பொறியியல், தகவல் தொழில்நுட்பம் மற்றும் தொழில்நுட்ப துறைகளில் சிறந்து விளங்குவர்."
        )
    elif total_score >= 2:
        cat = "Non-Technical (Administration / Audit / Languages / Arts / Humanities)"
        cat_ta = "தொழில்நுட்பம் அல்லாத (நிர்வாகம் / தணிக்கை / மொழிகள் / கலைகள் / மேலாண்மை)"
        interp = (
            f"The 4-fold career scoring model yields a positive score (+{total_score}), "
            "dominated by non-technical benefic planets (Sun, Moon, Mercury, Jupiter, Venus). "
            "Native excels in general administration, audit, financial management, creative arts, "
            "teaching, diplomacy, or languages."
        )
        interp_ta = (
            f"நான்கு முனை ஆய்வு நேர்மறை மதிப்பெண்ணை (+{total_score}) காட்டுகிறது. "
            "குரு, சுக்கிரன், புதன், சூரியன், சந்திரன் போன்ற சுப கிரகங்களின் ஆதிக்கம் இருப்பதால் "
            "நிர்வாகம், நிதி தணிக்கை, மொழிகள், இலக்கியம் மற்றும் கலைத் துறைகளில் தலைமைப் பொறுப்பு கிட்டும்."
        )
    else:
        cat = "Semi-Technical (Technical Management / Techno-Commercial / Applied Operations)"
        cat_ta = "அரை-தொழில்நுட்பம் (தொழில்நுட்ப மேலாண்மை / செயல்பாடுகள்)"
        interp = (
            f"Balanced score ({total_score}). The chart harmonizes technical systems with managerial, "
            "analytical, or administrative duties (e.g., technocrat, project manager, or applied operations)."
        )
        interp_ta = (
            f"சமநிலை மதிப்பெண் ({total_score}). தொழில்நுட்ப அறிவுடன் நிர்வாக மேலாண்மை மற்றும் திட்டங்களை இயக்கும் ஆற்றல் உண்டாகும்."
        )

    if rahu_engineering:
        interp += " Notable Rahu prominence on the 10th axis strongly indicates software engineering, high-tech computation, or telecommunications."
        interp_ta += " பத்தாம் பாவத்தில் ராகுவின் விசேஷ தாக்கம் கணினி மென்பொருள், தொலைத்தொடர்பு மற்றும் உயர் தொழில்நுட்ப பொறியியல் வாய்ப்பை உறுதி செய்கிறது."

    return TechnicalProfessionResult(
        karakamsha_sign=karakamsha_sign_name,
        score_karakamsha_10th=score_karakamsha,
        score_lagna_10th=score_lagna,
        score_moon_10th=score_moon,
        score_nakshatra_10th=score_nak,
        total_score=total_score,
        category=cat,
        category_tamil=cat_ta,
        rahu_engineering_prominence=rahu_engineering,
        technical_planets_influencing=tech_influences,
        non_technical_planets_influencing=non_tech_influences,
        detailed_breakdown={
            "karakamsha_10th_sign": SIGN_NAMES_EN[kk_10th_sign],
            "lagna_10th_sign": SIGN_NAMES_EN[lagna_10th_sign],
            "moon_10th_sign": SIGN_NAMES_EN[moon_10th_sign],
            "score_karakamsha": score_karakamsha,
            "score_lagna": score_lagna,
            "score_moon": score_moon,
            "score_nakshatra": score_nak,
        },
        interpretation=interp,
        interpretation_tamil=interp_ta,
    )


# ---------------------------------------------------------------------------
# 3. Col. A.K. Gour: Authors and Journalists Evaluator
# ---------------------------------------------------------------------------

def evaluate_author_journalist(
    d1_planets: Dict[str, Dict[str, Any]],
    d9_planets: Dict[str, Dict[str, Any]],
    lagna_sign: int,
) -> AuthorJournalistResult:
    """Evaluate Author vs Journalist literary talents using Col. A.K. Gour's 4 principles:
    1. PAC bonding of 3rd, 5th, 10th lords, Mercury, and Jupiter
    2. Mars-Mercury bond (Ink & Paper)
    3. Jaimini 2nd, 3rd, 5th lords, Mercury, and Jupiter in Jaimini aspects
    4. Karakamsha 2nd, 3rd, 5th planetary influences
    """
    third_sign = ((lagna_sign - 1 + 2) % 12) + 1
    fifth_sign = ((lagna_sign - 1 + 4) % 12) + 1
    tenth_sign = ((lagna_sign - 1 + 9) % 12) + 1

    third_lord = SIGN_LORDS[third_sign]
    fifth_lord = SIGN_LORDS[fifth_sign]
    tenth_lord = SIGN_LORDS[tenth_sign]

    # 1. PAC Bonding
    writing_lords = {third_lord, fifth_lord, tenth_lord, "Mercury", "Jupiter"}
    pac_links = 0
    jupiter_connected = False
    mercury_connected = False

    mercury_sign = d1_planets.get("Mercury", {}).get("sign_index", 0)
    jupiter_sign = d1_planets.get("Jupiter", {}).get("sign_index", 0)
    mars_sign = d1_planets.get("Mars", {}).get("sign_index", 0)

    # Check relationships between 3, 5, 10 lords
    for l1 in [third_lord, fifth_lord, tenth_lord]:
        p1 = d1_planets.get(l1)
        if not p1:
            continue
        s1 = p1.get("sign_index", 1)
        # Check aspect or conjunction with Mercury
        if s1 == mercury_sign or check_parashari_aspect(s1, l1, mercury_sign) or check_parashari_aspect(mercury_sign, "Mercury", s1):
            pac_links += 1
            mercury_connected = True
        # Check aspect or conjunction with Jupiter
        if s1 == jupiter_sign or check_parashari_aspect(s1, l1, jupiter_sign) or check_parashari_aspect(jupiter_sign, "Jupiter", s1):
            pac_links += 1
            jupiter_connected = True

    pac_bond_present = (pac_links >= 2)

    # 2. Mars-Mercury Bond (Ink & Paper)
    mars_mercury_bond = False
    mm_details = "No direct Mars-Mercury bond detected."
    if mars_sign and mercury_sign:
        if mars_sign == mercury_sign:
            mars_mercury_bond = True
            mm_details = f"Mars and Mercury are conjoined in {SIGN_NAMES_EN[mars_sign]} (direct fusion of ink and paper)."
        elif check_parashari_aspect(mars_sign, "Mars", mercury_sign) or check_parashari_aspect(mercury_sign, "Mercury", mars_sign):
            mars_mercury_bond = True
            mm_details = f"Mars in {SIGN_NAMES_EN[mars_sign]} and Mercury in {SIGN_NAMES_EN[mercury_sign]} are in mutual Parashari aspect."
        elif mars_sign in (3, 6) or mercury_sign in (1, 8):
            mars_mercury_bond = True
            mm_details = f"Sign exchange / mutual dispositorship (Mars in Mercury sign or Mercury in Mars sign)."
        else:
            # Check D9 Navamsha link
            d9_mars_sign = d9_planets.get("Mars", {}).get("sign_index", 0)
            d9_merc_sign = d9_planets.get("Mercury", {}).get("sign_index", 0)
            if d9_mars_sign == d9_merc_sign:
                mars_mercury_bond = True
                mm_details = f"Mars and Mercury conjoined in Navamsha D9 ({SIGN_NAMES_EN.get(d9_mars_sign, '')})."

    # 3. Jaimini Aspects between 2, 3, 5 lords + Mercury + Jupiter
    second_sign = ((lagna_sign - 1 + 1) % 12) + 1
    second_lord = SIGN_LORDS[second_sign]
    jaimini_writing_planets = {second_lord, third_lord, fifth_lord, "Mercury", "Jupiter"}
    jaimini_aspect_count = 0
    for p1 in jaimini_writing_planets:
        s1 = d1_planets.get(p1, {}).get("sign_index", 0)
        if not s1:
            continue
        aspected = get_jaimini_aspects_for_sign(s1)
        for p2 in jaimini_writing_planets:
            if p1 == p2:
                continue
            s2 = d1_planets.get(p2, {}).get("sign_index", 0)
            if s2 in aspected:
                jaimini_aspect_count += 1
    jaimini_writing = (jaimini_aspect_count >= 2)

    # 4. Karakamsha 2nd, 3rd, 5th
    kk_sign_idx, _ = calculate_karakamsha_sign(d1_planets, d9_planets)
    kk_2nd = ((kk_sign_idx - 1 + 1) % 12) + 1
    kk_3rd = ((kk_sign_idx - 1 + 2) % 12) + 1
    kk_5th = ((kk_sign_idx - 1 + 4) % 12) + 1
    target_kk_signs = {kk_sign_idx, kk_2nd, kk_3rd, kk_5th}

    kk_influences = []
    for p_name, p_data in d1_planets.items():
        if p_name in ("Ascendant", "Lagna"):
            continue
        ps = p_data.get("sign_index", 1)
        if ps in target_kk_signs:
            kk_influences.append(f"{p_name} in {SIGN_NAMES_EN[ps]}")

    # Synthesize Profile
    if pac_bond_present and jupiter_connected and mercury_connected and mars_mercury_bond:
        profile = "Author-cum-Journalist (Mastery in both Books and Media)"
        profile_ta = "எழுத்தாளர் மற்றும் பத்திரிகையாளர் (நூல்கள் மற்றும் ஊடக ஆளுமை)"
        syn = (
            "Exceptional literary yoga formed by harmonious bonding of 3rd, 5th, 10th lords with both "
            "Jupiter (author of enduring books) and Mercury (journalist), reinforced by the Mars-Mercury "
            f"ink-and-paper bond ({mm_details})."
        )
        syn_ta = (
            "3, 5, 10-ஆம் அதிபதிகள் குரு (ஆழ்ந்த நூலாசிரியர்) மற்றும் புதன் (பத்திரிகையாளர்) இருவருடனும் "
            f"இணைந்து, செவ்வாய்-புதன் மை-தாள் பந்தத்தால் ({mm_details}) சிறந்த எழுத்தாளர் மற்றும் பத்திரிகை ஆளுமையை உருவாக்குகின்றன."
        )
    elif pac_bond_present and jupiter_connected and not mars_mercury_bond:
        profile = "Author (Books, Philosophy, Scholarly Granths)"
        profile_ta = "ஆழ்ந்த நூலாசிரியர் / தத்துவ எழுத்தாளர்"
        syn = (
            "Strong Jupiterian dominance on 3rd, 5th, and 10th houses. Native excels as a contemplative, "
            "authoritative author of books, research monographs, and substantial treatises."
        )
        syn_ta = (
            "3, 5, 10-ஆம் பாவங்களில் குருவின் ஆதிக்கம் நிறைந்துள்ளதால் ஆழ்ந்த தத்துவம், ஆன்மீகம் மற்றும் ஆராய்ச்சி நூல்களை இயற்றும் ஆற்றல் கிட்டும்."
        )
    elif (pac_bond_present or jaimini_writing) and (mercury_connected or mars_mercury_bond):
        profile = "Journalist (Print Media, Periodicals, Digital News)"
        profile_ta = "பத்திரிகையாளர் / செய்தி ஊடகவியலாளர்"
        syn = (
            "Strong Mercurial energy coupled with Mars-Mercury synergy. Native possesses a sharp, "
            f"investigative intellect suited for fast-paced journalism, reporting, and editorial roles. {mm_details}"
        )
        syn_ta = (
            f"புதன் மற்றும் செவ்வாய் தொடர்பால் ({mm_details}) துரிதமான செய்தி எழுதும் திறன், பத்திரிகை ஆசிரியர் மற்றும் புலனாய்வு இதழியல் யோகம் உண்டாகும்."
        )
    elif jaimini_writing or len(kk_influences) >= 2:
        profile = "Creative Literary & Communication Talent"
        profile_ta = "படைப்பிலக்கிய மற்றும் தொடர்பாடல் திறன்"
        syn = f"Jaimini aspects and Karakamsha placements ({', '.join(kk_influences)}) indicate marked communication and creative writing instincts."
        syn_ta = f"காரகாம்ச அமைப்புகள் ({', '.join(kk_influences)}) படைப்பாற்றல், கவிதை மற்றும் சிறந்த எழுத்துத் திறனைக் குறிக்கின்றன."
    else:
        profile = "Non-Literary Vocational Focus"
        profile_ta = "இலக்கியம் அல்லாத பொதுத் தொழில் துறை"
        syn = "No specialized author or journalist bonding is activated in the chart."
        syn_ta = "எழுத்தாளர் அல்லது பத்திரிகையாளர் யோக அமைப்புகள் தீவிரமாக அமையவில்லை."

    return AuthorJournalistResult(
        pac_bond_present=pac_bond_present,
        jupiter_prominence=jupiter_connected,
        mercury_prominence=mercury_connected,
        mars_mercury_bond=mars_mercury_bond,
        mars_mercury_bond_details=mm_details,
        jaimini_writing_aspects=jaimini_writing,
        karakamsha_influences=kk_influences,
        writing_profile=profile,
        writing_profile_tamil=profile_ta,
        synthesis=syn,
        synthesis_tamil=syn_ta,
    )
