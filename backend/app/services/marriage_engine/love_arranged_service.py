"""Service for Love vs Arranged Marriage Prediction.

Analyzes an individual horoscope using:
1. Classical Vedic Astrological Principles (Parashara, Phaladeepika, BPHS 5th-7th lord connections).
2. Krishnamurti Padhdhati (KP) Cuspal Sub-Lord (CSL) rules for 5th (courtship) & 7th (wedlock) cusps.
3. Siddhayogi Sivadasan Ravi Nadi Mercury-Ketu and Karaka configurations.
4. Parental & Family Consent indicators (Jupiter / 9th Lord aspects).
"""

from __future__ import annotations
from datetime import datetime, timezone as dt_timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

import swisseph as xswe
from app.schemas.common import BirthInput
from app.schemas.love_marriage import (
    LoveOrArrangedFactor,
    LoveOrArrangedRequest,
    LoveOrArrangedResponse,
)
from app.services.timezone_utils import resolve_birth_datetime
from app.services.ephemeris import (
    compute_planetary_positions,
    get_sign_info,
)
from app.services.kp_service import calculate_kp_chart

logger = logging.getLogger("gai.marriage.love_arranged")

SIGN_NAMES_EN = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}

SIGN_NAMES_TA = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்",
}

PLANET_NAMES_TA = {
    "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்",
    "Mercury": "புதன்", "Jupiter": "குரு", "Venus": "சுக்கிரன்",
    "Saturn": "சனி", "Rahu": "ராகு", "Ketu": "கேது",
}

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}


def check_parashari_aspect(planet_name: str, planet_sign: int, target_sign: int) -> bool:
    """Check if planet casts a Parashari aspect on target sign."""
    offset = ((target_sign - planet_sign) % 12) + 1
    if offset == 7:
        return True
    if planet_name == "Mars" and offset in (4, 8):
        return True
    if planet_name == "Jupiter" and offset in (5, 9):
        return True
    if planet_name == "Saturn" and offset in (3, 10):
        return True
    return False


class LoveArrangedService:
    """Evaluates whether entered horoscope indicates love or arranged marriage."""

    @classmethod
    def evaluate(cls, request: LoveOrArrangedRequest) -> LoveOrArrangedResponse:
        birth = request.birth
        gender = (request.gender or "male").lower()
        native_name = request.name or ("Native" if gender != "female" else "Native")

        # 1. Ephemeris & Astronomical Calculation
        local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
            birth.birth_date,
            birth.birth_time,
            birth.timezone,
        )

        vedic_planets = compute_planetary_positions(birth_jd, ayanamsa_id=0, include_outer=False)
        planet_by_name = {p.name: p for p in vedic_planets}

        # Ascendant
        xswe.set_sid_mode(xswe.SIDM_LAHIRI, 0, 0)
        cusps_raw, ascmc_raw = xswe.houses_ex(birth_jd, birth.latitude, birth.longitude, b"W", xswe.FLG_SIDEREAL)
        asc_deg = ascmc_raw[0] % 360.0
        asc_sign_idx, asc_sign_name, asc_sign_tamil, _ = get_sign_info(asc_deg)

        # Whole-sign house indices (1 to 12)
        house_signs: Dict[int, int] = {}
        for h in range(1, 13):
            house_signs[h] = ((asc_sign_idx + h - 2) % 12) + 1

        house_lords: Dict[int, str] = {h: SIGN_LORDS[house_signs[h]] for h in range(1, 13)}

        # Planet placements
        planet_sign: Dict[str, int] = {}
        planet_house: Dict[str, int] = {}
        for p in vedic_planets:
            p_sign = p.sign_index
            h = ((p_sign - asc_sign_idx) % 12) + 1
            planet_sign[p.name] = p_sign
            planet_house[p.name] = h

        # 2. KP Chart Calculation
        kp_chart = None
        csl_5 = None
        csl_7 = None
        sig_5_houses: List[int] = []
        sig_7_houses: List[int] = []
        try:
            kp_chart = calculate_kp_chart(birth=birth)
            if kp_chart and kp_chart.cuspal_analysis and len(kp_chart.cuspal_analysis) >= 7:
                c5 = kp_chart.cuspal_analysis[4]
                c7 = kp_chart.cuspal_analysis[6]
                csl_5 = c5.sub_lord.title()
                csl_7 = c7.sub_lord.title()

                for h_entry in kp_chart.house_significators:
                    if csl_5 in h_entry.all_significators:
                        sig_5_houses.append(h_entry.house)
                    if csl_7 in h_entry.all_significators:
                        sig_7_houses.append(h_entry.house)
        except Exception as kp_err:
            logger.warning(f"KP calculation error: {kp_err}")

        # 3. Factor Analysis
        factors: List[LoveOrArrangedFactor] = []
        love_score = 15.0  # Base neutral baseline
        arranged_score = 15.0

        lord_1 = house_lords[1]
        lord_5 = house_lords[5]
        lord_7 = house_lords[7]
        lord_9 = house_lords[9]
        lord_2 = house_lords[2]

        sign_5 = house_signs[5]
        sign_7 = house_signs[7]

        pos_lord_5 = planet_sign.get(lord_5, 1)
        pos_lord_7 = planet_sign.get(lord_7, 7)
        pos_lord_1 = planet_sign.get(lord_1, 1)

        # -------------------------------------------------------------
        # Factor A: 5th Lord & 7th Lord Relationship (Core Vedic Rule)
        # -------------------------------------------------------------
        if pos_lord_5 == pos_lord_7:
            love_score += 28
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en=f"5th Lord ({lord_5}) & 7th Lord ({lord_7}) in Conjunction",
                    title_ta=f"5-ஆம் அதிபதி ({PLANET_NAMES_TA.get(lord_5)}) & 7-ஆம் அதிபதி ({PLANET_NAMES_TA.get(lord_7)}) ஒரே ராசியில் சேர்க்கை",
                    influence="LOVE",
                    description_en=f"The lord of romance ({lord_5}) is conjoined with the lord of marriage ({lord_7}) in {SIGN_NAMES_EN[pos_lord_5]}. This is the quintessential classical indicator of romantic courtship leading to wedlock.",
                    description_ta=f"காதல் ஸ்தானாதிபதி {PLANET_NAMES_TA.get(lord_5)} மற்றும் களத்திர ஸ்தானாதிபதி {PLANET_NAMES_TA.get(lord_7)} இருவரும் {SIGN_NAMES_TA[pos_lord_5]} ராசியில் ஒன்றாக இணைந்துள்ளனர். இது காதல் திருமணத்தை உறுதிப்படுத்தும் முதன்மையான சாஸ்திர யோகமாகும்.",
                    weight=5,
                )
            )
        elif pos_lord_5 == sign_7 and pos_lord_7 == sign_5:
            love_score += 30
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en=f"Parivartana (Sign Exchange) between 5th Lord and 7th Lord",
                    title_ta=f"5-ஆம் அதிபதி மற்றும் 7-ஆம் அதிபதி இடையே பரிவர்த்தனை யோகம்",
                    influence="LOVE",
                    description_en=f"5th lord {lord_5} sits in the 7th house ({SIGN_NAMES_EN[sign_7]}) while 7th lord {lord_7} sits in the 5th house ({SIGN_NAMES_EN[sign_5]}). This mutual exchange binds romantic affection with official marriage.",
                    description_ta=f"5-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_5)} 7-ஆம் வீட்டிலும், 7-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_7)} 5-ஆம் வீட்டிலும் அமர்ந்து உன்னதமான பரிவர்த்தனை பெற்றுள்ளனர். இதனால் காதல் நிச்சயம் திருமணத்தில் முடியும்.",
                    weight=5,
                )
            )
        elif pos_lord_5 == sign_7:
            love_score += 22
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en=f"5th Lord ({lord_5}) placed directly in 7th House",
                    title_ta=f"5-ஆம் அதிபதி ({PLANET_NAMES_TA.get(lord_5)}) நேரடியாக 7-ஆம் வீட்டில் அமர்வு",
                    influence="LOVE",
                    description_en=f"The planet governing romance and heartfelt attraction sits directly in the house of marriage ({SIGN_NAMES_EN[sign_7]}), steering personal romantic desires into holy matrimony.",
                    description_ta=f"காதலை குறிக்கும் 5-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_5)} களத்திர வீடான 7-ஆம் வீட்டில் அமர்ந்துள்ளதால் சொந்த விருப்பத்தின் பேரிலான காதல் திருமணம் அமைய அதிக வாய்ப்புள்ளது.",
                    weight=4,
                )
            )
        elif pos_lord_7 == sign_5:
            love_score += 22
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en=f"7th Lord ({lord_7}) placed in 5th House of Romance",
                    title_ta=f"7-ஆம் அதிபதி ({PLANET_NAMES_TA.get(lord_7)}) காதல் வீடான 5-ஆம் பாவத்தில் அமர்வு",
                    influence="LOVE",
                    description_en=f"The lord of partnership ({lord_7}) resides in the house of love and courtship ({SIGN_NAMES_EN[sign_5]}), strongly inclining the native toward choosing their own life partner.",
                    description_ta=f"திருமணத்திற்குரிய 7-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_7)} காதல் ஸ்தானமான 5-ஆம் வீட்டில் நிற்பதால் வாழ்க்கைத்துணையை ஜாதகரே விரும்பித் தேர்ந்தெடுப்பார்.",
                    weight=4,
                )
            )
        elif check_parashari_aspect(lord_5, pos_lord_5, pos_lord_7) or check_parashari_aspect(lord_7, pos_lord_7, pos_lord_5):
            love_score += 18
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en=f"Mutual Aspect between 5th Lord ({lord_5}) and 7th Lord ({lord_7})",
                    title_ta=f"5-ஆம் அதிபதி & 7-ஆம் அதிபதி இடையே சமசப்தம / விசேஷ பார்வை தொடர்பு",
                    influence="LOVE",
                    description_en=f"The 5th lord {lord_5} and 7th lord {lord_7} behold each other through Parashari drishti, creating mutual magnetic attraction culminating in marriage.",
                    description_ta=f"5-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_5)} மற்றும் 7-ஆம் அதிபதி {PLANET_NAMES_TA.get(lord_7)} ஒருவரையொருவர் பார்வை செய்வதால் இரு மனங்கள் ஒன்றிணைந்து திருமண பந்தம் உருவாகும்.",
                    weight=4,
                )
            )
        else:
            arranged_score += 15
            factors.append(
                LoveOrArrangedFactor(
                    category="5th & 7th Lord Relationship",
                    title_en="Independent 5th and 7th Lords (No Direct Link)",
                    title_ta="5 மற்றும் 7-ஆம் அதிபதிகளுக்கு இடையே நேரடி தொடர்பின்மை",
                    influence="ARRANGED",
                    description_en="The lords of the 5th and 7th houses operate independently without conjunction, exchange, or mutual aspect, favoring traditional family-arranged marriage.",
                    description_ta="காதலுக்குரிய 5-ஆம் அதிபதியும் திருமணத்திற்குரிய 7-ஆம் அதிபதியும் தங்களுக்குள் நேரடி சேர்க்கையோ பார்வைகளோ பெறவில்லை. இது மரபு வழி திருமணத்திற்கு சாதகமாகும்.",
                    weight=3,
                )
            )

        # -------------------------------------------------------------
        # Factor B: Venus & Planetary Chemistry (Mars / Rahu / Moon)
        # -------------------------------------------------------------
        pos_ven = planet_sign.get("Venus", 1)
        pos_mars = planet_sign.get("Mars", 1)
        pos_rahu = planet_sign.get("Rahu", 1)
        pos_jup = planet_sign.get("Jupiter", 1)
        pos_sat = planet_sign.get("Saturn", 1)

        # Venus-Mars
        if pos_ven == pos_mars or check_parashari_aspect("Mars", pos_mars, pos_ven) or check_parashari_aspect("Venus", pos_ven, pos_mars):
            love_score += 16
            factors.append(
                LoveOrArrangedFactor(
                    category="Planetary Attraction",
                    title_en="Venus-Mars Passion Synergy",
                    title_ta="சுக்கிரன் - செவ்வாய் சேர்க்கை / பார்வை (தீவிர ஈர்ப்பு யோகம்)",
                    influence="LOVE",
                    description_en="Venus (Karaka of love) joins or aspects Mars (Karaka of physical vitality and passion), imparting strong romantic magnetism and emotional initiative.",
                    description_ta="காதல் காரகன் சுக்கிரனும், உணர்ச்சி காரகன் செவ்வாயும் தொடர்பு கொள்வது ஜாதகருக்குள் தீவிர காதல் ஈர்ப்பையும் வசீகரத்தையும் உருவாக்கும்.",
                    weight=4,
                )
            )

        # Venus-Rahu or Rahu in 7th
        if pos_ven == pos_rahu or planet_house.get("Rahu") == 7 or check_parashari_aspect("Rahu", pos_rahu, pos_ven):
            love_score += 18
            factors.append(
                LoveOrArrangedFactor(
                    category="Planetary Attraction",
                    title_en="Venus-Rahu / Rahu in 7th (Unconventional Romance)",
                    title_ta="சுக்கிரன்-ராகு தொடர்பு அல்லது 7-ல் ராகு (கலாச்சார எல்லை கடந்த ஈர்ப்பு)",
                    influence="LOVE",
                    description_en="Rahu's influence on Venus or the 7th house encourages unconventional, modern alliances often crossing traditional caste, community, or geographic boundaries.",
                    description_ta="சுக்கிரனுடன் ராகு இணைய அல்லது 7-ஆம் வீட்டில் ராகு அமைய, ஜாதகர் மரபு வழி பழக்கங்களை தாண்டி சொந்த விருப்பத்தில் புதுமையான காதல் திருமணத்தை நாடுவார்.",
                    weight=4,
                )
            )

        # -------------------------------------------------------------
        # Factor C: Jupiter (Dharma, Tradition, Elders' Blessing)
        # -------------------------------------------------------------
        jup_aspects_7th = check_parashari_aspect("Jupiter", pos_jup, sign_7)
        jup_aspects_7th_lord = check_parashari_aspect("Jupiter", pos_jup, pos_lord_7)
        jup_in_7th = planet_house.get("Jupiter") == 7
        jup_in_2nd = planet_house.get("Jupiter") == 2
        jup_in_9th = planet_house.get("Jupiter") == 9

        if jup_aspects_7th or jup_aspects_7th_lord or jup_in_7th or jup_in_2nd or jup_in_9th:
            arranged_score += 24
            factors.append(
                LoveOrArrangedFactor(
                    category="Family & Elders Blessing",
                    title_en="Benefic Jupiter Safeguarding Marriage / Family Realm",
                    title_ta="குருவின் சுபப் பார்வை / இருப்பு (சாஸ்திர தர்மம் மற்றும் பெரியோர் ஆசி)",
                    influence="ARRANGED",
                    description_en="Jupiter's divine ray protects the 7th house or family houses (2nd/9th), conferring parental approval, ethical honor, and strong support for traditional matrimony.",
                    description_ta="தேவகுருவின் சுபப் பார்வை 7-ஆம் பாவம் அல்லது குடும்ப பாவங்களில் பதிவதால், திருமணத்தில் பெரியோர்களின் முழு ஆசியும், சாஸ்திர தர்மப்படி குடும்பத்தார் நடத்தும் சுபயோகமும் உண்டாகும்.",
                    weight=4,
                )
            )

        # -------------------------------------------------------------
        # Factor D: 2nd, 7th & 9th House Linkage (Traditional Alliances)
        # -------------------------------------------------------------
        pos_lord_9 = planet_sign.get(lord_9, 1)
        pos_lord_2 = planet_sign.get(lord_2, 1)

        if pos_lord_7 == house_signs[9] or pos_lord_9 == sign_7:
            arranged_score += 18
            factors.append(
                LoveOrArrangedFactor(
                    category="Traditional Alliance Signatures",
                    title_en="7th & 9th Lord Sambandha (Father & Elders' Direction)",
                    title_ta="7 மற்றும் 9-ஆம் அதிபதிகள் தொடர்பு (பெற்றோர் வழிகாட்டுதல்)",
                    influence="ARRANGED",
                    description_en="The 7th lord aligns with the 9th house of father, pitrus, and dharma, indicating the matrimonial match is brought through respected elders or family network.",
                    description_ta="7-ஆம் அதிபதி தந்தை மற்றும் குரு ஸ்தானமான 9-ஆம் வீட்டுடன் தொடர்பு கொள்வதால் பெற்றோர் பார்த்து முடிவு செய்யும் திருமண பந்தம் கைகூடும்.",
                    weight=4,
                )
            )

        if pos_lord_7 == house_signs[2] or pos_lord_2 == sign_7:
            arranged_score += 14
            factors.append(
                LoveOrArrangedFactor(
                    category="Traditional Alliance Signatures",
                    title_en="7th & 2nd House Family Linkage",
                    title_ta="7 மற்றும் 2-ஆம் பாவக குடும்ப சேர்க்கை",
                    influence="ARRANGED",
                    description_en="Direct connection between 2nd house of family lineage and 7th house indicates marriage expands family bonds via traditional match-making.",
                    description_ta="குடும்ப ஸ்தானமான 2-ஆம் பாவமும் களத்திர 7-ஆம் பாவமும் இணைவதால், குடும்பத்தினர் விரும்பும் வரன் நிச்சயமாகி திருமணம் இனிதே நடைபெறும்.",
                    weight=3,
                )
            )

        # Saturn adherence to traditions
        if planet_house.get("Saturn") == 7 and pos_rahu != pos_sat:
            arranged_score += 12
            factors.append(
                LoveOrArrangedFactor(
                    category="Traditional Alliance Signatures",
                    title_en="Saturn in 7th House (Orthodox & Methodical Pathway)",
                    title_ta="7-ல் சனி பகவான் அமர்வு (மரபு வழி பழமை விரும்புதல்)",
                    influence="ARRANGED",
                    description_en="Saturn in 7th enforces mature, orthodox criteria and patient alignment with family elders' consent before solemnizing the wedding.",
                    description_ta="7-ஆம் வீட்டில் சனி அமர்ந்துள்ளதால் எதிலும் அவசரப்படாமல் மரபு வழி குடும்ப நியதிகளைப் பின்பற்றி திருமணம் நடைபெறும்.",
                    weight=3,
                )
            )

        # -------------------------------------------------------------
        # Factor E: KP Cuspal Sub-Lord (CSL) Analysis (Prof. K.S.K.)
        # -------------------------------------------------------------
        kp_sublord_summary_text = None
        if csl_5 and csl_7:
            kp_csl_5_love = (5 in sig_5_houses and 11 in sig_5_houses) or (7 in sig_5_houses)
            kp_csl_7_love = (5 in sig_7_houses) or (csl_7 in ["Venus", "Mars", "Rahu"] and 5 in sig_7_houses)
            kp_csl_7_arranged = (2 in sig_7_houses or 7 in sig_7_houses or 11 in sig_7_houses) and (5 not in sig_7_houses)

            if kp_csl_5_love or kp_csl_7_love:
                love_score += 24
                factors.append(
                    LoveOrArrangedFactor(
                        category="KP Cuspal Sub-Lord Alignment",
                        title_en=f"KP 5th CSL ({csl_5}) / 7th CSL ({csl_7}) Signifies Romance",
                        title_ta=f"கே.பி 5-ஆம் CSL ({PLANET_NAMES_TA.get(csl_5, csl_5)}) / 7-ஆம் CSL ({PLANET_NAMES_TA.get(csl_7, csl_7)}) காதல் பாவங்களை குறிக்கிறது",
                        influence="LOVE",
                        description_en=f"Under KP system, 5th CSL signifies houses {sig_5_houses or [5, 11]} and 7th CSL signifies {sig_7_houses or [7]}. Connection to 5th (romance) and 11th (desire fulfillment) validates personal courtship.",
                        description_ta=f"கே.பி ஜோதிட முறைப்படி 5-ஆம் உப அதிபதி {sig_5_houses or [5, 11]} பாவங்களையும், 7-ஆம் உப அதிபதி {sig_7_houses or [7]} பாவங்களையும் குறிப்பதால் காதல் உறவு மலர்ந்து திருமணத்தில் இணைய சாதகமாக உள்ளது.",
                        weight=5,
                    )
                )
                kp_sublord_summary_text = f"KP 5th CSL {csl_5} & 7th CSL {csl_7} actively signify romantic houses (5, 7, 11)."
            elif kp_csl_7_arranged:
                arranged_score += 20
                factors.append(
                    LoveOrArrangedFactor(
                        category="KP Cuspal Sub-Lord Alignment",
                        title_en=f"KP 7th CSL ({csl_7}) Signifies Pure Matrimony (Houses 2, 7, 11)",
                        title_ta=f"கே.பி 7-ஆம் உப அதிபதி ({PLANET_NAMES_TA.get(csl_7, csl_7)}) மரபு வழி திருமண பாவங்களை குறிக்கிறது",
                        influence="ARRANGED",
                        description_en=f"Under KP rules, 7th CSL {csl_7} signifies houses {sig_7_houses or [2, 7, 11]} without involvement of 5th house of romance, confirming a traditional arranged alliance.",
                        description_ta=f"கே.பி முறைப்படி 7-ஆம் உப அதிபதி {csl_7} காதல் பாவமான 5-ஆம் தொடர்பு இன்றி 2, 7, 11 பாவங்களை மட்டும் குறிப்பது நிச்சயிக்கப்பட்ட திருமணத்தை உறுதி செய்கிறது.",
                        weight=4,
                    )
                )
                kp_sublord_summary_text = f"KP 7th CSL {csl_7} signifies traditional matrimonial houses (2, 7, 11) without romantic entanglement."

        # -------------------------------------------------------------
        # Factor F: Siddhayogi Sivadasan Ravi Nadi Rule
        # -------------------------------------------------------------
        budha_sign = planet_sign.get("Mercury", 1)
        ketu_sign = planet_sign.get("Ketu", 7)
        dist_bk = ((ketu_sign - budha_sign) % 12) + 1
        is_love_trigger = dist_bk in {1, 5, 9, 2}
        benefic_aspect = (((pos_jup - budha_sign) % 12) + 1 in {1, 5, 7, 9}) or (((pos_ven - budha_sign) % 12) + 1 in {1, 7})

        if is_love_trigger:
            love_score += 15
            factors.append(
                LoveOrArrangedFactor(
                    category="Nadi Principles",
                    title_en="Siddhayogi Sivadasan Ravi Mercury-Ketu Romantic Impulse",
                    title_ta="சித்தயோகி சிவதாசன் ரவி புதன்-கேது காதல் ஈர்ப்பு விதி",
                    influence="LOVE",
                    description_en="Mercury-Ketu sambandha in trines or 2nd house activates deep romantic inclination and heartfelt attachment.",
                    description_ta="புதன்-கேது சேர்க்கை அல்லது 1, 5, 9, 2 திரிகோண தொடர்பு ஆழ்ந்த காதல் ஈர்ப்பையும் விருப்பத்தையும் ஏற்படுத்தும்.",
                    weight=3,
                )
            )

        # -------------------------------------------------------------
        # Score Normalization & Percentages
        # -------------------------------------------------------------
        total = love_score + arranged_score
        love_pct = int(round((love_score / total) * 100))
        # Keep bounds sane
        love_pct = max(10, min(90, love_pct))
        arranged_pct = 100 - love_pct

        # -------------------------------------------------------------
        # Family Support Determination
        # -------------------------------------------------------------
        has_jup_support = jup_aspects_7th or jup_aspects_7th_lord or jup_in_7th or jup_in_9th
        if love_pct >= 60:
            if has_jup_support:
                family_support = "High Parental Support & Blessings"
                family_support_ta = "பெற்றோர் மற்றும் குடும்பத்தினரின் முழு சம்மதம் கிடைக்கும்"
            elif pos_rahu == pos_ven or planet_house.get("Rahu") == 7:
                family_support = "Family Persuasion Needed"
                family_support_ta = "ஆரம்பத்தில் பெரியவர்களை பேசி சம்மதிக்க வைக்க வேண்டியிருக்கும்"
            else:
                family_support = "Moderate Family Support"
                family_support_ta = "பெரியவர்களின் நல் ஆதரவுடன் சுபமாக முடியும்"
        elif love_pct >= 40:
            family_support = "Both Family and Self-Choice Blend Harmoniously"
            family_support_ta = "பெற்றோர் பார்க்கும் வரன் அல்லது உங்கள் விருப்பம் இருதரப்பும் மனமொத்து நடக்கும்"
        else:
            family_support = "Traditional Family Initiative"
            family_support_ta = "குடும்பத்தினர் மற்றும் பெரியோர்களின் முழு ஆதரவுடன் சிறப்பாக நடைபெறும்"

        # -------------------------------------------------------------
        # Final Verdict Formulation
        # -------------------------------------------------------------
        if love_pct >= 60:
            if has_jup_support:
                verdict = "Love Marriage with Family Blessings"
                verdict_ta = "பெற்றோர் சம்மதத்துடன் காதல் திருமணம் (Love-cum-Arranged)"
                verdict_badge = "LOVE_ARRANGED"
                summary_en = f"This horoscope shows strong romantic indicators ({love_pct}%) guided by planetary goodwill. Your love affair is blessed with family consent and culminates in a happy, respectable marriage."
                summary_ta = f"இந்த ஜாதகத்தில் காதல் திருமணத்திற்கான சாத்தியக்கூறுகள் மிக வலுவாக ({love_pct}%) உள்ளன. குரு மற்றும் சுப கிரகங்களின் அனுகூலத்தால் பெரியவர்களின் சம்மதத்துடன் காதல் திருமணம் இனிதே கைகூடும்."
            else:
                verdict = "Love Marriage"
                verdict_ta = "காதல் திருமணம் (Love Marriage)"
                verdict_badge = "LOVE"
                summary_en = f"Planetary alignments strongly indicate a self-chosen romantic marriage ({love_pct}%). You will choose your life partner based on personal affection and mutual understanding."
                summary_ta = f"கிரக அமைப்புகள் ஜாதகரே விரும்பித் தேர்ந்தெடுக்கும் காதல் திருமணத்தை ({love_pct}%) சுட்டிக்காட்டுகின்றன. பரஸ்பர அன்பும் ஈர்ப்பும் கொண்ட வாழ்க்கைத் துணை அமைவார்."
        elif love_pct >= 40:
            verdict = "Love-cum-Arranged Marriage"
            verdict_ta = "பெற்றோர் சம்மதத்துடன் காதல் திருமணம் (இருவர் மனமொத்து நடக்கும்)"
            verdict_badge = "LOVE_ARRANGED"
            summary_en = f"A harmonious balance of romantic attraction ({love_pct}%) and traditional family consent ({arranged_pct}%). Even if arranged by elders, deep mutual love will blossom before wedding."
            summary_ta = f"காதல் உணர்வுகளும் ({love_pct}%) குடும்பத்தாரின் சம்மதமும் ({arranged_pct}%) சம பலத்துடன் உள்ளன. பெரியவர்கள் பார்த்து நடத்தினாலும் இருவர் மனமும் விரும்பி ஏற்கும் காதல் கலந்த சுப திருமணமாக அமையும்."
        else:
            verdict = "Arranged Marriage"
            verdict_ta = "பெற்றோரால் நிச்சயிக்கப்பட்ட திருமணம் (Arranged Marriage)"
            verdict_badge = "ARRANGED"
            summary_en = f"Traditional matrimonial pathway favored ({arranged_pct}%). Your marriage will be arranged by family elders through proper matching and societal customs, conferring enduring peace."
            summary_ta = f"சாஸ்திர சம்பிரதாய முறைப்படி பெற்றோர் மற்றும் குடும்பப் பெரியோர்களால் நிச்சயிக்கப்பட்ட சுப திருமணம் ({arranged_pct}%) சிறப்பாக நடைபெறும். இல்லறம் அமைதியாகவும் சீராகவும் அமையும்."

        # Technical Summaries
        fifth_info = f"5th House in {SIGN_NAMES_EN[sign_5]} (Lord: {lord_5} in {SIGN_NAMES_EN[pos_lord_5]}, House {planet_house.get(lord_5, 1)})"
        seventh_info = f"7th House in {SIGN_NAMES_EN[sign_7]} (Lord: {lord_7} in {SIGN_NAMES_EN[pos_lord_7]}, House {planet_house.get(lord_7, 7)})"
        venus_info = f"Venus in {SIGN_NAMES_EN[pos_ven]} (House {planet_house.get('Venus', 1)})"

        # Birth summary
        b_sum = f"{birth.birth_date.strftime('%d %b %Y')}, {birth.birth_time.strftime('%I:%M %p')} ({birth.timezone})"

        return LoveOrArrangedResponse(
            native_name=native_name,
            native_gender=gender,
            birth_summary=b_sum,
            verdict=verdict,
            verdict_ta=verdict_ta,
            verdict_badge=verdict_badge,
            love_percentage=love_pct,
            arranged_percentage=arranged_pct,
            summary_en=summary_en,
            summary_ta=summary_ta,
            family_support=family_support,
            family_support_ta=family_support_ta,
            key_factors=factors,
            fifth_house_summary=fifth_info,
            seventh_house_summary=seventh_info,
            kp_sublord_summary=kp_sublord_summary_text,
            venus_summary=venus_info,
            calculated_at=datetime.now(dt_timezone.utc).isoformat(),
        )
