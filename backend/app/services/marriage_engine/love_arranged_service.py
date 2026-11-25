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

try:
    import xalen.swe as xswe
except ImportError:
    import swisseph as xswe
from app.schemas.common import BirthInput
from app.schemas.love_marriage import (
    LoveOrArrangedFactor,
    LoveOrArrangedRequest,
    LoveOrArrangedResponse,
    SpouseOriginProfile,
    LifePartnerProfile,
    LoveInitiationTiming,
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

        # Determine 3 Specialized In-Depth Predictors
        spouse_origin = cls._determine_spouse_origin(
            gender=gender,
            sign_7=sign_7,
            lord_7=lord_7,
            house_signs=house_signs,
            planet_house=planet_house,
            planet_sign=planet_sign,
        )

        life_partner = cls._determine_life_partner_profile(
            gender=gender,
            sign_7=sign_7,
            lord_7=lord_7,
            planet_house=planet_house,
            planet_sign=planet_sign,
        )

        love_timing = cls._determine_love_timing(
            birth_date=birth.birth_date,
            lord_5=lord_5,
            lord_7=lord_7,
            love_pct=love_pct,
            kp_chart=kp_chart,
        )

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
            spouse_origin=spouse_origin,
            life_partner=life_partner,
            love_timing=love_timing,
            fifth_house_summary=fifth_info,
            seventh_house_summary=seventh_info,
            kp_sublord_summary=kp_sublord_summary_text,
            venus_summary=venus_info,
            calculated_at=datetime.now(dt_timezone.utc).isoformat(),
        )

    @classmethod
    def _determine_spouse_origin(
        cls,
        gender: str,
        sign_7: int,
        lord_7: str,
        house_signs: Dict[int, int],
        planet_house: Dict[str, int],
        planet_sign: Dict[str, int],
    ) -> SpouseOriginProfile:
        """Determines the origin direction, distance, and 2-3 points on how the bride/groom arrives."""
        def sign_dir(s: int) -> Tuple[str, str]:
            if s in (1, 5, 9):
                return "East", "கிழக்கு"
            elif s in (2, 6, 10):
                return "South", "தெற்கு"
            elif s in (3, 7, 11):
                return "West", "மேற்கு"
            else:
                return "North", "வடக்கு"

        d7_en, d7_ta = sign_dir(sign_7)
        pos_lord_7 = planet_sign.get(lord_7, sign_7)
        dlord_en, dlord_ta = sign_dir(pos_lord_7)

        # Compound direction
        if d7_en == dlord_en:
            dir_en = d7_en
            dir_ta = d7_ta
        elif (d7_en == "East" and dlord_en == "North") or (d7_en == "North" and dlord_en == "East"):
            dir_en = "North-East (Ishanya)"
            dir_ta = "வடகிழக்கு (ஈசான்யம்)"
        elif (d7_en == "East" and dlord_en == "South") or (d7_en == "South" and dlord_en == "East"):
            dir_en = "South-East (Agneya)"
            dir_ta = "தென்கிழக்கு (ஆக்னேயம்)"
        elif (d7_en == "West" and dlord_en == "North") or (d7_en == "North" and dlord_en == "West"):
            dir_en = "North-West (Vayavya)"
            dir_ta = "வடமேற்கு (வாயுவியம்)"
        elif (d7_en == "West" and dlord_en == "South") or (d7_en == "South" and dlord_en == "West"):
            dir_en = "South-West (Nairrutya)"
            dir_ta = "தென்மேற்கு (நைருதி)"
        else:
            dir_en = f"{d7_en} / {dlord_en}"
            dir_ta = f"{d7_ta} / {dlord_ta}"

        # Distance category by sign quality (Chara, Sthira, Dwisvabhava)
        if sign_7 in (1, 4, 7, 10):
            dist_en = "Distant location / outside native birthplace or relocated partner"
            dist_ta = "தொலைதூர பகுதி / வெளி மாவட்டம் அல்லது இடம் பெயர்ந்த வாழ்க்கைத்துணை"
        elif sign_7 in (2, 5, 8, 11):
            dist_en = "Nearby vicinity / same hometown or closely connected native circle"
            dist_ta = "உள்ளூர் / சொந்த ஊர் அல்லது மிக அருகிலுள்ள வட்டாரம்"
        else:
            dist_en = "Moderate distance / neighboring town or adjacent district"
            dist_ta = "நடுத்தர தூரம் / அருகிலுள்ள நகரம் அல்லது பக்கத்து மாவட்டம்"

        # Sphere of meeting / channel
        h_7 = planet_house.get(lord_7, 7)
        if h_7 in (6, 10):
            channel_en = "Professional workplace, corporate organization, or career networking"
            channel_ta = "பணியிடம், கார்ப்பரேட் நிறுவனம் அல்லது தொழில் சார்ந்த பொதுவான களம்"
            point2_en = "The primary introduction takes place through a professional workspace, corporate organization, or shared career project where daily interactions foster mutual rapport."
            point2_ta = "பணியிடம், தொழில்முறை நிறுவனம் அல்லது உத்தியோகப்பூர்வ சந்திப்புகள் வழியாக இருவருக்குள்ளும் பரஸ்பர அறிமுகமும் நட்பும் இயல்பாக உருவாகிறது."
        elif h_7 in (3, 11):
            channel_en = "Social gathering, mutual friend circle, or digital / community media"
            channel_ta = "நண்பர்கள் வட்டம், சமூகக் கூடல் அல்லது தகவல் தொடர்பு / இணைய தளம்"
            point2_en = "Connection is initiated through mutual close friends, social celebratory gatherings, or modern digital/community communication platforms."
            point2_ta = "பொதுவான நண்பர்கள் வட்டம், குடும்ப விசேஷங்கள் அல்லது நவீன தகவல் தொடர்பு சாதனங்கள் வாயிலாக முதல் அறிமுகம் மலர்கிறது."
        elif h_7 in (2, 9):
            channel_en = "Family elders, relatives, or traditional matrimonial alliance network"
            channel_ta = "குடும்பப் பெரியோர்கள், உறவினர்கள் அல்லது பாரம்பரிய வரன் முறை"
            point2_en = "The alliance arrives through respected family elders, maternal/paternal relatives, or established traditional matrimonial introductions."
            point2_ta = "குடும்பப் பெரியோர்கள், நெருங்கிய உறவினர்கள் அல்லது பாரம்பரிய வரன் பார்க்கும் முறை வாயிலாக இரு குடும்பங்களும் இணைகின்றன."
        elif h_7 in (4, 5):
            channel_en = "Educational campus, college / university circle, or creative events"
            channel_ta = "கல்லூரி / கல்விக்கூடம் அல்லது பொதுவான கலை மற்றும் கலைநிகழ்ச்சி களம்"
            point2_en = "The bond sparks during educational pursuits, college/university campus life, or shared recreational/artistic interests."
            point2_ta = "கல்லூரி அல்லது உயர்கல்வி பயிலும் காலம், அல்லது பொதுவான கலை மற்றும் விருப்பங்கள் சார்ந்த நிகழ்வுகளில் முதல் சந்திப்பு ஏற்படுகிறது."
        elif h_7 in (1, 7):
            channel_en = "Direct personal encounter, neighborhood acquaintance, or travel encounter"
            channel_ta = "நேரடி அறிமுகம், பக்கத்து பகுதி அல்லது பயணத்தின்போது ஏற்பட்ட சந்திப்பு"
            point2_en = "The meeting unfolds through direct personal encounter, neighborhood acquaintance, or a serendipitous interaction."
            point2_ta = "முன்பே தெரிந்த பழக்கம், அருகிலுள்ள வட்டாரத் தொடர்பு அல்லது எதிர்பாராத நேரடி சந்திப்பின் மூலம் அன்பு உருவாகிறது."
        else:
            channel_en = "Distant origin, transit / travel connection, or cross-cultural alliance"
            channel_ta = "தூரத்து அறிமுகம், தொலைதூரப் பயணம் அல்லது கலாச்சார எல்லை கடந்த வரன்"
            point2_en = "The partner hails from a distinct geographical or cultural background, met during travel, relocation, or overseas assignments."
            point2_ta = "தொலைதூரப் பயணம், பணியிட இடமாற்றம் அல்லது வேறுபட்ட கலாச்சாரப் பின்னணியில் எதிர்பாராத விதமாக சந்திப்பு அமைகிறது."

        # Point 1: Direction & Distance
        point1_en = f"The life partner originates from the {dir_en} direction relative to the native's birthplace, hailing from a {dist_en.lower()}."
        point1_ta = f"வாழ்க்கைத் துணைவர் ஜாதகரின் பிறந்த இடத்திலிருந்து {dir_ta} திசையிலிருந்து அமைகிறார் ({dist_ta})."

        # Point 3: Locality & Family Environment
        if sign_7 in (4, 8, 12):
            point3_en = "The spouse's family belongs to a fertile, coastal, or scenic green locality with strong emotional and cultural rootedness."
            point3_ta = "துணைவரின் பூர்வீகம் நீர்நிலைகள், பசுமையான சூழல் அல்லது நதிக்கரை/கடற்கரை சார்ந்த வளமான நிலப்பரப்பில் அமைந்திருக்கும்."
        elif sign_7 in (2, 6, 10):
            point3_en = "The partner comes from an industrious, hardworking, and commercially established family background with ancestral values."
            point3_ta = "துணைவர் கடுமையான உழைப்பு, வியாபாரம் அல்லது பாரம்பரிய சொத்துக்கள் மற்றும் குடும்ப விழுமியங்கள் கொண்ட வம்சத்தைச் சேர்ந்தவர்."
        elif sign_7 in (3, 7, 11):
            point3_en = "The partner hails from a prominent urban metropolis, educational center, or commercially vibrant technological hub."
            point3_ta = "துணைவர் தகவல் தொடர்பு, கல்வி நிறுவனங்கள் அல்லது வணிக வளம் நிறைந்த நவீன நகரப்பகுதியை பூர்வீகமாகக் கொண்டவர்."
        else:
            point3_en = "The partner's family holds respected social standing, characterized by principled leadership, energy, and administrative reputation."
            point3_ta = "துணைவரின் குடும்பம் சமுதாயத்தில் நன்மதிப்பும், நிர்வாக திறமையும், கௌரவமான பாரம்பரியமும் கொண்டதாக விளங்கும்."

        points_en = [point1_en, point2_en, point3_en]
        points_ta = [point1_ta, point2_ta, point3_ta]

        return SpouseOriginProfile(
            direction_en=dir_en,
            direction_ta=dir_ta,
            distance_type_en=dist_en,
            distance_type_ta=dist_ta,
            source_channel_en=channel_en,
            source_channel_ta=channel_ta,
            points_en=points_en,
            points_ta=points_ta,
        )

    @classmethod
    def _determine_life_partner_profile(
        cls,
        gender: str,
        sign_7: int,
        lord_7: str,
        planet_house: Dict[str, int],
        planet_sign: Dict[str, int],
    ) -> LifePartnerProfile:
        """Determines the traits, appearance, and career profile of who the life partner will be."""
        planets_in_7 = [p for p, h in planet_house.items() if h == 7]
        dominant_planet = planets_in_7[0] if planets_in_7 else lord_7

        is_groom = (gender == "female")
        partner_label_en = "Groom / Husband" if is_groom else "Bride / Wife"
        partner_label_ta = "கணவர் (மணமகன்)" if is_groom else "மனைவி (மணமகள்)"

        profiles = {
            "Sun": {
                "nature_en": "Noble, dignified, self-respecting, authoritative, and principled with natural leadership charisma.",
                "nature_ta": "சுயமரியாதை, கம்பீரம், கொள்கைப்பிடிப்பு, தலைமைப் பண்பு மற்றும் கௌரவத்தை பெரிதும் மதிக்கும் நேர்மையான குணம்.",
                "features_en": "Imposing posture, commanding presence, bright facial aura, medium to tall height, and proud demeanor.",
                "features_ta": "கம்பீரமான நடை, பிரகாசமான முகம், நடுத்தர அல்லது நல்ல உயரமான உடல்வாகு மற்றும் எடுப்பான தோற்றம்.",
                "career_en": "Government administration, executive leadership, public enterprise, management, or established family enterprise.",
                "career_ta": "அரசுத்துறை, நிர்வாகப் பணி, தலைமைப் பொறுப்பு, மேலாண்மை அல்லது பரம்பரை தொழில்.",
            },
            "Moon": {
                "nature_en": "Gentle, compassionate, deeply intuitive, family-oriented, fond of comfort, and emotionally supportive.",
                "nature_ta": "அன்பும் பாசமும் நிறைந்த மென்மையான சுபாவம், உணர்ச்சிவசப்படும் குணம், குடும்பப் பற்று மற்றும் இரக்க சுபாவம்.",
                "features_en": "Round or soft attractive facial features, glowing fair complexion, soothing eyes, and graceful charming demeanor.",
                "features_ta": "அழகான வட்ட முகம், தெளிவான கண்கள், நளினமான உடல்வாகு மற்றும் வசீகரமான புன்னகை.",
                "career_en": "Healthcare, hospitality, arts, public relations, finance, education, or creative enterprises.",
                "career_ta": "மருத்துவம், மக்கள் தொடர்பு, உணவகம்/விருந்தோம்பல், கலைத்துறை, கல்வி அல்லது நிதி நிர்வாகம்.",
            },
            "Mars": {
                "nature_en": "Energetic, courageous, assertive, fiercely loyal, active, protective of family, and decisive in action.",
                "nature_ta": "சுறுசுறுப்பு, தைரியம், எதையும் நேருக்கு நேர் பேசும் குணம், துணையை பாதுகாக்கும் உறுதி மற்றும் விரைவான முடிவெடுக்கும் ஆற்றல்.",
                "features_en": "Athletic build, sharp radiant eyes, firm step, confident expression, and youthful physical vigor.",
                "features_ta": "உறுதியான கட்டுக்கோப்பான உடல்வாகு, கூர்மையான பார்வை, சுறுசுறுப்பான நடை மற்றும் இளமையான தோற்றம்.",
                "career_en": "Engineering, technology, defense/uniformed services, real estate, construction, surgery, or entrepreneurship.",
                "career_ta": "பொறியியல், தகவல் தொழில்நுட்பம், பாதுகாப்புத்துறை, கட்டுமானத்துறை, அறுவை சிகிச்சை அல்லது சொந்த தொழில்.",
            },
            "Mercury": {
                "nature_en": "Sharp-witted, articulate communicator, humorous, adaptable, intellectually curious, and cheerful in companionship.",
                "nature_ta": "அறிவுக் கூர்மை, கனிவான பேச்சுத்திறன், நகைச்சுவை உணர்வு, விரைந்து கற்கும் ஆர்வம் மற்றும் கலகலப்பான சுபாவம்.",
                "features_en": "Youthful countenance, expressive lively eyes, slender to medium stature, and energetic posture.",
                "features_ta": "எப்போதும் இளமையான தோற்றம், ஒளி பொருந்திய கண்கள், நடுத்தர உடல்வாகு மற்றும் சுறுசுறுப்பான இயல்பு.",
                "career_en": "Software engineering, data analytics, banking, journalism, publishing, accounting, commerce, or trade.",
                "career_ta": "மென்பொருள் பொறியியல், தரவு பகுப்பாய்வு, வங்கிப்பணி, எழுத்து, ஆடிட்டிங், வர்த்தகம் அல்லது வணிக மேலாண்மை.",
            },
            "Jupiter": {
                "nature_en": "Wise, cultured, spiritually inclined, dignified, ethical, generous, and devoted to family honour and traditions.",
                "nature_ta": "ஞானம், நற்பண்புகள், ஆன்மீக பற்று, பெரியோரை மதிக்கும் அடக்கம், நேர்மை மற்றும் குடும்ப தர்மத்தை காக்கும் மாண்பு.",
                "features_en": "Stately and commanding build, warm compassionate gaze, pleasant magnetic smile, and respectable aura.",
                "features_ta": "அமைதியான கனிவான பார்வை, எடுப்பான கம்பீரமான தோற்றம், அழகான புன்னகை மற்றும் மரியாதைக்குரிய ஆளுமை.",
                "career_en": "Higher education, advisory, law, banking, professorship, management consulting, or corporate strategy.",
                "career_ta": "உயர்கல்வி, பேராசிரியர் பணி, சட்டம், வங்கி நிர்வாகம், நிதி ஆலோசனை அல்லது வழிகாட்டுதல்.",
            },
            "Venus": {
                "nature_en": "Charming, artistic, romantic, peace-loving, socially refined, affectionate, and deeply invested in marital joy.",
                "nature_ta": "வசீகரமான குணம், கலையார்வம், ரொமான்டிக் சுபாவம், அமைதி விரும்பி, பாசமிக்கவர் மற்றும் இல்லற இன்பத்தை போற்றுபவர்.",
                "features_en": "Highly attractive facial features, captivating eyes, pleasing smile, stylish dressing sense, and graceful poise.",
                "features_ta": "மிகவும் வசீகரமான முகம், கவர்ச்சியான கண்கள், அழகான புன்னகை, நேர்த்தியான ஆடை தேர்வு மற்றும் நளினமான நடை.",
                "career_en": "Creative media, fashion, luxury goods, IT/design, cinema, music, architecture, interior design, or hospitality.",
                "career_ta": "கலைத்துறை, ஃபேஷன், டிசைனிங், மென்பொருள் வடிவமைப்பு, சினிமா, இசை, ஆர்க்கிடெக்ட் அல்லது அழகுக்கலை.",
            },
            "Saturn": {
                "nature_en": "Mature, patient, duty-bound, disciplined, practical, dependable, and possessing deep endurance.",
                "nature_ta": "முதிர்ந்த எண்ணங்கள், அளவற்ற பொறுமை, கடமை உணர்வு, உழைப்பாளி, எளிமை மற்றும் வாழ்நாள் முழுவதும் துணையாக நிற்கும் விசுவாசம்.",
                "features_en": "Lean to tall stature, thoughtful composed face, serious gaze, mature demeanor, and grounded posture.",
                "features_ta": "ஒல்லியான அல்லது உயரமான தோற்றம், அமைதியான சிந்தனை முகம், முதிர்ச்சியான நடை மற்றும் எளிமையான பாங்கு.",
                "career_en": "Core engineering, manufacturing, operations, law, governance, civil services, agriculture, or research.",
                "career_ta": "கோர் இன்ஜினியரிங், உற்பத்தித்துறை, செயல்பாட்டு மேலாண்மை, சட்டம், ஆய்வுத்துறை அல்லது விவசாயம்.",
            },
            "Rahu": {
                "nature_en": "Progressive, unconventional, ambitious, magnetic, quick-witted, and possessing broad international outlook.",
                "nature_ta": "முற்போக்கு சிந்தனை, புதுமை விரும்புபவர், அபரிமிதமான லட்சியம், தனித்துவமான ஈர்ப்பு மற்றும் நவீன உலகப் பார்வை.",
                "features_en": "Distinctive striking looks, expressive deep eyes, modern styling, and captivating presence.",
                "features_ta": "தனித்துவமான தோற்றம், வசீகரமான கண்கள், நவீன நாகரீக உடை மற்றும் மற்றவர்களை ஈர்க்கும் உடல்வாகு.",
                "career_en": "Cutting-edge tech, global MNCs, digital marketing, aviation, foreign commerce, media, or innovative start-ups.",
                "career_ta": "நவீன தொழில்நுட்பம், பன்னாட்டு நிறுவனம், டிஜிட்டல் மார்க்கெட்டிங், விமானத்துறை, வெளிநாட்டு வர்த்தகம் அல்லது ஸ்டார்ட்-அப்.",
            },
            "Ketu": {
                "nature_en": "Spiritual, introspective, sincere, humble, selfless, intuitive, and placing contentment above materialism.",
                "nature_ta": "ஆன்மீக நாட்டம், எளிமை, அமைதியான சிந்தனை, உண்மையான அன்பு, சுயநலமற்ற மனம் மற்றும் ஆழ்ந்த உள்ளுணர்வு.",
                "features_en": "Simple graceful countenance, calm serene gaze, modest demeanor, and gentle posture.",
                "features_ta": "எளிமையான முக அமைதி, சாந்தமான பார்வை, ஆடம்பரமற்ற பாங்கு மற்றும் மென்மையான உடல்வாகு.",
                "career_en": "Software development, research, psychology, healthcare, spirituality, analytics, or consulting.",
                "career_ta": "மென்பொருள் உருவாக்கம், ஆராய்ச்சி, உளவியல், மருத்துவம், ஆன்மீகம் அல்லது தகவல் பகுப்பாய்வு.",
            },
        }

        p = profiles.get(dominant_planet, profiles["Venus"])

        summary_en = (
            f"Your {partner_label_en.lower()} is governed primarily by {dominant_planet}'s astrological influence in the 7th house realm. "
            f"This planetary configuration promises an enduring, mutually supportive partnership with shared values and domestic harmony."
        )

        summary_ta = (
            f"உங்கள் {partner_label_ta} 7-ஆம் பாவகத்தில் {PLANET_NAMES_TA.get(dominant_planet, dominant_planet)} கிரகத்தின் ஆதிக்கத்தில் அமைகிறார். "
            f"இக்கிரக அமைப்பு இல்லறத்தில் மனமொத்த புரிதல், பரஸ்பர மரியாதை மற்றும் நீடித்த மகிழ்ச்சியை அருளும் உன்னத சுபயோகமாகும்."
        )

        return LifePartnerProfile(
            nature_temperament_en=p["nature_en"],
            nature_temperament_ta=p["nature_ta"],
            physical_features_en=p["features_en"],
            physical_features_ta=p["features_ta"],
            career_background_en=p["career_en"],
            career_background_ta=p["career_ta"],
            summary_en=summary_en,
            summary_ta=summary_ta,
        )

    @classmethod
    def _determine_love_timing(
        cls,
        birth_date: Any,
        lord_5: str,
        lord_7: str,
        love_pct: int,
        kp_chart: Any,
    ) -> LoveInitiationTiming:
        """Estimates when romantic attraction ignited or blooms based on 5th house/lord dasha triggers."""
        if hasattr(birth_date, "year"):
            b_year = birth_date.year
        else:
            try:
                b_year = int(str(birth_date)[:4])
            except Exception:
                b_year = 1995

        trigger_lord = "Venus" if lord_5 in ("Venus", "Mercury", "Mars", "Moon") else lord_5
        if trigger_lord not in ("Venus", "Rahu", "Mercury", "Mars"):
            trigger_lord = "Venus"

        found_md = None
        if kp_chart and hasattr(kp_chart, "dasa_hierarchy") and kp_chart.dasa_hierarchy:
            mds = getattr(kp_chart.dasa_hierarchy, "mahadashas", [])
            for md in mds:
                try:
                    s_yr = int(md.start_date[:4])
                    e_yr = int(md.end_date[:4])
                    age_at_start = s_yr - b_year
                    if 16 <= age_at_start <= 30 or (s_yr <= b_year + 22 <= e_yr):
                        found_md = md.lord
                        break
                except Exception:
                    pass

        active_timing_lord = found_md or trigger_lord

        if love_pct >= 60:
            age_start = 20
            age_end = 23
            context_en = (
                "Romance ignited during college/higher education or initial corporate career transition. "
                "Mutual attraction deepened through frequent intellectual exchanges, shared aspirations, and heartfelt emotional bonding."
            )
            context_ta = (
                "கல்லூரி / உயர்கல்வி பயிலும் காலத்திலோ அல்லது பணியிடத்தின் ஆரம்ப கட்டத்திலோ இந்த காதல் ஈர்ப்பு தொடங்கியது. "
                "இருவருக்கும் இடையே உருவான புரிதல், தொடர் உரையாடல் மற்றும் பரஸ்பர அன்பின் மூலம் இக்காதல் வேரூன்றியது."
            )
        elif love_pct >= 40:
            age_start = 22
            age_end = 25
            context_en = (
                "Romantic rapport developed during early career years or formal pre-wedding interaction. "
                "Friendship naturally evolved into affectionate attachment with growing mutual trust and familial approval."
            )
            context_ta = (
                "பணியில் இணைந்த ஆரம்ப ஆண்டுகள் அல்லது வரன் பார்க்கும் முன்பாக ஏற்பட்ட அறிமுகத்தில் காதல் உணர்வுகள் மலர்ந்தன. "
                "நல்ல நட்பாகத் தொடங்கி நாளடைவில் ஆழ்ந்த காதலாகவும், இருவர் விருப்பத்திலான பந்தமாகவும் உருப்பெற்றது."
            )
        else:
            age_start = 23
            age_end = 26
            context_en = (
                "Emotional readiness and marital love blossoms during the matrimonial selection and engagement period. "
                "Affection deepens smoothly following elders' matchmaking and reciprocal family alignment."
            )
            context_ta = (
                "திருமணத்திற்குரிய வரன் பார்க்கும் பருவம் மற்றும் நிச்சயதார்த்த காலகட்டத்தில் காதல் மற்றும் ஈர்ப்பு மலர்கிறது. "
                "பெரியோர்கள் ஏற்பாடு செய்த வரன் என்றாலும், இருவருக்கும் இடையே மனமொத்த அன்பும் பாசமும் விரைவாக உண்டாகும்."
            )

        year_start = b_year + age_start
        year_end = b_year + age_end

        trigger_dasha_en = f"{active_timing_lord} Mahadasha / {lord_5} Antardasha with Venus transit activation"
        trigger_dasha_ta = f"{PLANET_NAMES_TA.get(active_timing_lord, active_timing_lord)} தசை / {PLANET_NAMES_TA.get(lord_5, lord_5)} புக்தி மற்றும் சுக்கிரனின் கோச்சார அனுகூல காலம்"

        return LoveInitiationTiming(
            estimated_age_range=f"{age_start} – {age_end} years",
            approximate_period=f"{year_start} – {year_end}",
            trigger_dasha_en=trigger_dasha_en,
            trigger_dasha_ta=trigger_dasha_ta,
            context_en=context_en,
            context_ta=context_ta,
        )
