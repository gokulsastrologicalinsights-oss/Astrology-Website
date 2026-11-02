"""Natchathira Deep Analysis Engine.

Based on empirical astrological research from classical treatises and
'Predicting Through Nakshatras - Part 1' (Saptarishis Publications).

Provides in-depth analysis for:
1. Ashwini (00°00' - 13°20' Aries)
2. Bharani (13°20' - 26°40' Aries)
3. Krittika (26°40' Aries - 10°00' Taurus)
4. Rohini (10°00' - 23°20' Taurus)
5. Mrigashira (23°20' Taurus - 06°40' Gemini)
6. Ardra (06°40' - 20°00' Gemini)
7. Punarvasu (20°00' Gemini - 03°20' Cancer)
8. Pushya (03°20' - 16°40' Cancer)
9. Ashlesha (16°40' - 30°00' Cancer)

Evaluates:
- Precise Nakshatra & Pada placements
- House rulerships (1st to 12th lords)
- Bhava placements
- Conjunctions & Classical Drik Aspects
- Sarvatobhadra Chakra (SBC) Nakshatra Aspects
- Afflictions (Malefic associations, Dusthanas, Retrograde status)
- Key Life Age Milestones (Ages 18-20, 27, 38-50, 65-75)
- Vastu directional conditions (North-East corner)
- Specific bodily vulnerabilities (Lower feet / ankles)
- Specialized Remedial Upayas (Narayana Kavach, Zero-Gossip Vow, etc.)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


# 12 Zodiac signs in order (0-indexed)
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Standard Vedic Sign Rulers
SIGN_RULERS = {
    0: "Mars",      # Aries
    1: "Venus",     # Taurus
    2: "Mercury",   # Gemini
    3: "Moon",      # Cancer
    4: "Sun",       # Leo
    5: "Mercury",   # Virgo
    6: "Venus",     # Libra
    7: "Mars",      # Scorpio (Co-ruled by Ketu)
    8: "Jupiter",   # Sagittarius
    9: "Saturn",    # Capricorn
    10: "Saturn",   # Aquarius (Co-ruled by Rahu)
    11: "Jupiter",  # Pisces
}

NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}

# SBC Cross-Aspects on specific Nakshatras as documented in Saptarishis research:
# e.g., Jyeshtha -> Ashwini; Rohini -> Ashwini; Purva Phalguni -> Ashwini; Mula -> Punarvasu
SBC_ASPECT_MAP = {
    "Ashwini": ["Rohini", "Jyeshtha", "Purva Phalguni", "Swati"],
    "Bharani": ["Krittika", "Anuradha", "Uttara Phalguni", "Vishakha"],
    "Krittika": ["Rohini", "Vishakha", "Hasta"],
    "Rohini": ["Mrigashira", "Chitra", "Swati"],
    "Mrigashira": ["Ardra", "Chitra", "Dhanishta"],
    "Ardra": ["Punarvasu", "Shatabhisha", "Shravana"],
    "Punarvasu": ["Pushya", "Mula", "Uttara Ashadha"],
    "Pushya": ["Ashlesha", "Purva Ashadha", "Abhijit"],
    "Ashlesha": ["Magha", "Mula", "Shravana"],
}


def _clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _get_sign_index(sign_name: str) -> int:
    s = sign_name.lower().strip()
    for idx, name in enumerate(ZODIAC_SIGNS):
        if name.lower() == s:
            return idx
    # Check abbreviations
    abbr_map = {
        "ar": 0, "ta": 1, "ge": 2, "cn": 3, "ca": 3,
        "le": 4, "vi": 5, "li": 6, "sc": 7,
        "sg": 8, "sa": 8, "cp": 9, "cap": 9, "aq": 10, "pi": 11
    }
    return abbr_map.get(s[:2], 0)


def extract_chart_contexts(horoscope_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts normalized Lagna, planets, houses, and lordships from horoscope data."""
    h = horoscope_data.get("horoscope") or horoscope_data

    # 1. Ascendant
    asc_raw = h.get("ascendant") or {}
    lagna_sign_name = _clean_str(asc_raw.get("sign_name") or asc_raw.get("sign") or "Aries")
    lagna_sign_idx = _get_sign_index(lagna_sign_name)
    lagna_deg = float(asc_raw.get("degree_in_sign") or 0.0)
    lagna_nak = asc_raw.get("nakshatra") or {}
    lagna_nak_name = _clean_str(lagna_nak.get("name") or "")
    lagna_pada = int(lagna_nak.get("pada") or 1)

    # 2. House Lordships from Lagna
    # house 1..12: which sign index, and who rules it
    house_to_sign = {}
    sign_to_house = {}
    planet_lordships: Dict[str, List[int]] = {
        "Sun": [], "Moon": [], "Mars": [], "Mercury": [],
        "Jupiter": [], "Venus": [], "Saturn": [], "Rahu": [], "Ketu": []
    }

    for h_num in range(1, 13):
        s_idx = (lagna_sign_idx + (h_num - 1)) % 12
        house_to_sign[h_num] = s_idx
        sign_to_house[s_idx] = h_num
        primary_ruler = SIGN_RULERS[s_idx]
        if primary_ruler in planet_lordships:
            planet_lordships[primary_ruler].append(h_num)
        if s_idx == 7 and "Ketu" in planet_lordships:  # Scorpio co-ruler Ketu
            planet_lordships["Ketu"].append(h_num)
        if s_idx == 10 and "Rahu" in planet_lordships:  # Aquarius co-ruler Rahu
            planet_lordships["Rahu"].append(h_num)

    # 3. Normalized Planets
    raw_planets = h.get("planets") or []
    planets_by_name: Dict[str, Dict[str, Any]] = {}

    for p in raw_planets:
        p_name = _clean_str(p.get("name"))
        if not p_name:
            continue
        p_sign_name = _clean_str(p.get("sign_name") or p.get("sign") or "")
        p_sign_idx = _get_sign_index(p_sign_name)
        p_deg = float(p.get("degree_in_sign") or 0.0)
        p_nak = p.get("nakshatra") or {}
        p_nak_name = _clean_str(p_nak.get("name") or "")
        p_pada = int(p_nak.get("pada") or 1)
        p_house = sign_to_house.get(p_sign_idx, 1)
        is_retro = bool(p.get("is_retrograde", False))

        planets_by_name[p_name] = {
            "name": p_name,
            "sign_name": ZODIAC_SIGNS[p_sign_idx],
            "sign_idx": p_sign_idx,
            "degree": p_deg,
            "house": p_house,
            "nakshatra_name": p_nak_name,
            "pada": p_pada,
            "is_retrograde": is_retro,
            "houses_owned": planet_lordships.get(p_name, []),
        }

    # Add Lagna as a special entity for Nakshatra evaluation
    planets_by_name["Ascendant"] = {
        "name": "Ascendant",
        "sign_name": ZODIAC_SIGNS[lagna_sign_idx],
        "sign_idx": lagna_sign_idx,
        "degree": lagna_deg,
        "house": 1,
        "nakshatra_name": lagna_nak_name,
        "pada": lagna_pada,
        "is_retrograde": False,
        "houses_owned": [1],
    }

    # 4. Planetary Aspects (Drik Sambandha)
    # Mapping which planets aspect each sign / house
    aspects_on_house: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    aspects_on_sign: Dict[int, List[str]] = {i: [] for i in range(12)}

    for p_name, p_data in planets_by_name.items():
        if p_name in ("Ascendant", "Uranus", "Neptune", "Pluto"):
            continue
        curr_house = p_data["house"]
        curr_sign = p_data["sign_idx"]

        # Universal 7th aspect (180 deg)
        opp_house = ((curr_house + 5) % 12) + 1
        opp_sign = (curr_sign + 6) % 12
        aspects_on_house[opp_house].append(p_name)
        aspects_on_sign[opp_sign].append(p_name)

        # Special aspects
        if p_name == "Mars":
            # 4th and 8th aspects
            h4 = ((curr_house + 2) % 12) + 1
            h8 = ((curr_house + 6) % 12) + 1
            s4 = (curr_sign + 3) % 12
            s8 = (curr_sign + 7) % 12
            aspects_on_house[h4].append(p_name)
            aspects_on_house[h8].append(p_name)
            aspects_on_sign[s4].append(p_name)
            aspects_on_sign[s8].append(p_name)
        elif p_name == "Jupiter":
            # 5th and 9th aspects
            h5 = ((curr_house + 3) % 12) + 1
            h9 = ((curr_house + 7) % 12) + 1
            s5 = (curr_sign + 4) % 12
            s9 = (curr_sign + 8) % 12
            aspects_on_house[h5].append(p_name)
            aspects_on_house[h9].append(p_name)
            aspects_on_sign[s5].append(p_name)
            aspects_on_sign[s9].append(p_name)
        elif p_name == "Saturn":
            # 3rd and 10th aspects
            h3 = ((curr_house + 1) % 12) + 1
            h10 = ((curr_house + 8) % 12) + 1
            s3 = (curr_sign + 2) % 12
            s10 = (curr_sign + 9) % 12
            aspects_on_house[h3].append(p_name)
            aspects_on_house[h10].append(p_name)
            aspects_on_sign[s3].append(p_name)
            aspects_on_sign[s10].append(p_name)
        elif p_name in ("Rahu", "Ketu"):
            # 5th and 9th trine aspects
            h5 = ((curr_house + 3) % 12) + 1
            h9 = ((curr_house + 7) % 12) + 1
            s5 = (curr_sign + 4) % 12
            s9 = (curr_sign + 8) % 12
            aspects_on_house[h5].append(p_name)
            aspects_on_house[h9].append(p_name)
            aspects_on_sign[s5].append(p_name)
            aspects_on_sign[s9].append(p_name)

    return {
        "lagna_sign_name": lagna_sign_name,
        "lagna_sign_idx": lagna_sign_idx,
        "lagna_nak_name": lagna_nak_name,
        "lagna_pada": lagna_pada,
        "planets": planets_by_name,
        "planet_lordships": planet_lordships,
        "aspects_on_house": aspects_on_house,
        "aspects_on_sign": aspects_on_sign,
        "sign_to_house": sign_to_house,
    }


def analyze_saved_chart_nakshatras(
    horoscope_data: Dict[str, Any],
    birth_date_str: Optional[str] = None
) -> Dict[str, Any]:
    """Main analyzer implementing Saptarishis empirical nakshatra techniques."""
    ctx = extract_chart_contexts(horoscope_data)
    planets = ctx["planets"]
    lordships = ctx["planet_lordships"]
    aspects_on_house = ctx["aspects_on_house"]
    aspects_on_sign = ctx["aspects_on_sign"]

    # Calculate current age if birth_date provided
    native_age = None
    if birth_date_str:
        try:
            b_dt = datetime.strptime(birth_date_str[:10], "%Y-%m-%d")
            today = datetime.now()
            native_age = today.year - b_dt.year - ((today.month, today.day) < (b_dt.month, b_dt.day))
        except Exception:
            pass

    # Helper: get planets in a given nakshatra
    def get_in_nak(nak_name: str) -> List[Dict[str, Any]]:
        target = nak_name.lower().strip()
        matched = []
        for name, p in planets.items():
            if target in p["nakshatra_name"].lower():
                matched.append(p)
        return matched

    # Helper: check who aspects a target nakshatra (both Drik and SBC)
    def get_aspectors_on_nak(nak_name: str) -> List[str]:
        aspectors = set()
        in_target = get_in_nak(nak_name)
        # 1. Drik aspect on the houses where this nakshatra falls
        for p in in_target:
            h = p["house"]
            for asp in aspects_on_house.get(h, []):
                aspectors.add(asp)

        # 2. SBC aspects from planets in specific SBC stars
        sbc_source_stars = SBC_ASPECT_MAP.get(nak_name, [])
        for src_star in sbc_source_stars:
            for p in get_in_nak(src_star):
                aspectors.add(p["name"])

        return list(aspectors)

    # Helper: check if a nakshatra is afflicted in this chart
    def is_nak_afflicted(nak_name: str) -> Dict[str, Any]:
        in_star = get_in_nak(nak_name)
        if not in_star:
            return {"afflicted": False, "reasons": []}

        reasons = []
        # Check malefics inside star
        for p in in_star:
            if p["name"] in NATURAL_MALEFICS:
                reasons.append(f"Natural malefic {p['name']} placed in {nak_name}")
            if p["house"] in (6, 8, 12):
                reasons.append(f"{p['name']} in dusthana {p['house']}th house")
            if p["is_retrograde"]:
                reasons.append(f"{p['name']} is retrograde")

        # Check malefic aspects
        aspectors = get_aspectors_on_nak(nak_name)
        malefic_aspectors = [a for a in aspectors if a in NATURAL_MALEFICS]
        if malefic_aspectors:
            reasons.append(f"Aspect from natural malefics: {', '.join(malefic_aspectors)}")

        return {
            "afflicted": len(reasons) >= 1,
            "reasons": reasons,
            "malefic_aspectors": malefic_aspectors,
        }

    matched_rules: List[Dict[str, Any]] = []
    age_milestones: List[Dict[str, Any]] = []
    vastu_advisories: List[Dict[str, Any]] = []
    body_part_alerts: List[Dict[str, Any]] = []
    active_nakshatras_summary: List[Dict[str, Any]] = []

    # =========================================================================
    # 1. ASHWINI (அசுவினி)
    # =========================================================================
    ashwini_planets = get_in_nak("Ashwini")
    ashwini_aspectors = get_aspectors_on_nak("Ashwini")
    ashwini_affliction = is_nak_afflicted("Ashwini")

    if ashwini_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Ashwini",
            "name_ta": "அசுவினி",
            "lord": "Ketu",
            "deity": "Ashwini Kumars",
            "symbol": "Horse's Head",
            "grahas": [p["name"] for p in ashwini_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in ashwini_planets]
        })

        # Technique 1: Travel & Movement
        for p in ashwini_planets:
            p_name = p["name"]
            h_owned = p["houses_owned"]
            h_pos = p["house"]

            # 5th or 7th lord: love interest while travelling
            if 5 in h_owned or 7 in h_owned:
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_ROMANCE_TRAVEL",
                    "category": "TRAVEL_RELATIONSHIPS",
                    "title_en": f"{p_name} rules 5th/7th House in Ashwini: Romantic Affair or Meeting Spouse While Travelling",
                    "title_ta": f"அசுவினியில் 5/7-ம் அதிபதி {p_name}: பிரயாணத்தில் அல்லது போக்குவரத்தில் காதல்/துணை சந்திப்பு",
                    "severity": "POSITIVE_TALENT",
                    "trigger_grahas": [p_name],
                    "details_en": f"{p_name} (ruling houses {h_owned}) sits in Ashwini Nakshatra in House {h_pos}. Classical research shows romance, infatuation, or meeting future life partner during journeys, flights, or transport vehicles.",
                    "details_ta": f"{p_name} (வீடுகள்: {h_owned}) அசுவினி நட்சத்திரத்தில் ஸ்தானம் பெற்றுள்ளது. பயணங்கள், விமானம், ரயில் அல்லது வாகனப் போக்குவரத்தின் போது காதல் அமையவோ அல்லது வருங்காலத் துணையை முதன்முதலில் சந்திக்கவோ அதிக வாய்ப்புண்டு.",
                    "case_study": "Saptarishis Example 7: Native flew out on Easter break to Bombay, met his future wife during travel, leading to immediate engagement.",
                    "remedy_en": "Be mindful of decisions made in fast transit; verify commitments with clarity.",
                    "remedy_ta": "பயணக் காலங்களில் எடுக்கும் அவசர முடிவுகளை நிதானமாக யோசித்து முடிவெடுக்கவும்."
                })

            # 8th or 12th lord in Ashwini: deep affairs abroad / if afflicted caution
            if 8 in h_owned or 12 in h_owned:
                is_crit = ashwini_affliction["afflicted"]
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_SEXUAL_TRAVEL",
                    "category": "TRAVEL_SECRETS",
                    "title_en": f"{p_name} rules 8th/12th House in Ashwini: Passionate Foreign Affairs & Travel Prudence",
                    "title_ta": f"அசுவினியில் 8/12-ம் அதிபதி {p_name}: வெளிநாட்டு பிரயாணங்களில் அந்தரங்க உறவுகள் மற்றும் பாதுகாப்பு",
                    "severity": "CRITICAL_CAUTION" if is_crit else "IMPORTANT_MILESTONE",
                    "trigger_grahas": [p_name],
                    "details_en": f"{p_name} ruling secret/foreign houses ({h_owned}) in swift Ashwini in House {h_pos}. Shows intense liaisons in distant cities or overseas. {'AFFLICTION WARNING: Malefic connections necessitate extreme caution against isolated places or nocturnal travel risks.' if is_crit else 'Brings deep karmic romantic journeys abroad.'}",
                    "details_ta": f"மறைவு/மோட்ச ஸ்தானாதிபதியான {p_name} அசுவினியில் இருப்பது வெளிநாட்டுப் பயணங்களின் போது எதிர்பாராத ரகசிய உறவுகளை உருவாக்கும். {'பாதிப்பு உள்ளதால்: இரவு நேரங்களில் தெரியாத தனிமையான இடங்களில் பயணிப்பதை தவிர்க்க வேண்டும்.' if is_crit else 'பயணங்களில் ஆன்மீக அல்லது ஆத்மார்த்த உறவுகளைத் தரும்.'}",
                    "case_study": "Saptarishis Examples: Elizabeth Ashley (8L afflicted in Ashwini), Martin Luther King (12L Jupiter in Ashwini in Lagna).",
                    "remedy_en": "Recite Maha Mrityunjaya Mantra before night-time long-distance travel.",
                    "remedy_ta": "இரவு நேர நீண்ட தூர பயணங்களுக்கு முன் மகா மிருத்யுஞ்சய மந்திரம் பாராயணம் செய்யவும்."
                })

            # Mars in Ashwini: Real estate travel
            if p_name == "Mars":
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_MARS_LAND",
                    "category": "PROPERTY_CAREER",
                    "title_en": "Mars in Ashwini: Travelling for Land & Real Estate Acquisitions",
                    "title_ta": "அசுவினியில் செவ்வாய்: நிலம், வீடு மற்றும் சொத்துக்கள் வாங்குவதற்காக பிரயாணங்கள்",
                    "severity": "POSITIVE_TALENT",
                    "trigger_grahas": ["Mars"],
                    "details_en": "Mars (Bhumi Karaka) in Aries-Ashwini drives active travels across regions specifically for inspecting, acquiring, and trading properties, plots, and buildings.",
                    "details_ta": "பூமி காரகனான செவ்வாய் அசுவினியில் இருப்பதால், புதிய நிலங்கள், சொத்துக்கள் வாங்குதல் மற்றும் விற்பனைக்காக பல்வேறு ஊர்களுக்குத் தொடர்ந்து பயணம் செய்வீர்கள்.",
                    "case_study": "Documented dictum in Saptarishis Nakshatra Treatise.",
                    "remedy_en": "Ensure boundary and document verifications before making hasty token payments on land.",
                    "remedy_ta": "சொத்து ஒப்பந்தங்களில் அவசரப்படாமல் ஆவணங்களை இருமுறை சரிபார்க்கவும்."
                })

            # Sun in Ashwini: Father / Salesman
            if p_name == "Sun":
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_SUN_SALES",
                    "category": "CAREER_FATHER",
                    "title_en": "Sun in Ashwini: Travelling Profession / Mobile Career for Native or Father",
                    "title_ta": "அசுவினியில் சூரியன்: தந்தை அல்லது ஜாதகருக்கு பிரயாணம் சார்ந்த தொழில்",
                    "severity": "BEHAVIORAL_TRAIT",
                    "trigger_grahas": ["Sun"],
                    "details_en": "Exalted or situated Sun in Ashwini indicates that the native's father had an active roaming/travelling job (sales, marketing, inspections), and native too thrives in dynamic, field-oriented career paths.",
                    "details_ta": "அசுவினியில் சூரியன் அமைவது தந்தையாரின் பணி அடிக்கடி வெளியூர் செல்லும் களப்பணியாக (Sales/Field duty) இருப்பதைக் காட்டும். ஜாதகருக்கும் ஓரிடத்தில் அமராமல் இயங்கும் தொழில் அமையும்.",
                    "case_study": "Saptarishis Example 8: Native was a travelling salesman who made a living on the move.",
                    "remedy_en": "Surya Namaskar at sunrise strengthens core vitality and professional stamina.",
                    "remedy_ta": "சூரிய நமஸ்காரம் செய்வது தொழில் மேன்மைக்கும் ஆரோக்கியத்திற்கும் சிறந்தது."
                })

            # Mercury in Ashwini: Fast-changing communications (Mark Zuckerberg pattern)
            if p_name == "Mercury":
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_MERCURY_FAST_TECH",
                    "category": "INTELLIGENCE_TECH",
                    "title_en": "Mercury in Ashwini: Swift Dynamic Communication & Evolving Networks",
                    "title_ta": "அசுவினியில் புதன்: வேகமான தகவல் தொடர்பு, சமூக ஊடக மேதைமை மற்றும் புதுமை",
                    "severity": "POSITIVE_TALENT",
                    "trigger_grahas": ["Mercury"],
                    "details_en": "Mercury (Karaka of speech, media, networks) in swift Ashwini grants restless mental agility, fast messaging, and success in dynamic online or communications ventures.",
                    "details_ta": "தகவல் தொடர்புக்குரிய புதன் அசுவினியில் இருப்பது மின்னல் வேக சிந்திக்கும் திறன் மற்றும் ஆன்லைன், டிஜிட்டல் ஊடகங்களில் பெரும் சாதனைகளை உருவாக்கும்.",
                    "case_study": "Mark Zuckerberg has Mercury in Ashwini as Lagna & 4th Lord: Facebook's lightning-fast evolving platform.",
                    "remedy_en": "Practice mindfulness to avoid mental scatter and impulsive communications.",
                    "remedy_ta": "சிந்தனையில் நிதானத்தைக் கடைப்பிடிப்பது கூடுதல் வெற்றியைத் தரும்."
                })

            # Moon in Ashwini: Higher studies / Education journeys
            if p_name == "Moon":
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": "ASHWINI_T1_MOON_STUDIES_TRAVEL",
                    "category": "EDUCATION_TRAVEL",
                    "title_en": "Moon in Ashwini: Long Journeys for Higher Studies, Internships & Degrees",
                    "title_ta": "அசுவினியில் சந்திரன்: உயர்கல்வி மற்றும் பயிற்சிகளுக்காக தொலைதூர/வெளிநாட்டு பிரயாணம்",
                    "severity": "POSITIVE_TALENT",
                    "trigger_grahas": ["Moon"],
                    "details_en": "Moon in Ashwini in 9th/other houses prompts journeys to different cities or countries for academic degrees, prestigious internships, and intellectual expansions.",
                    "details_ta": "மனோகாரகன் சந்திரன் அசுவினியில் அமைவது உயர்கல்வி, வெளிநாட்டுப் படிப்பு, பட்ட மேற்படிப்பு மற்றும் புதிய பயிற்சிகளுக்காகப் பல முறை ஊர் மாறச் செய்யும்.",
                    "case_study": "Saptarishis Example 3: Native travelled for higher education and internships 6 times across different countries.",
                    "remedy_en": "Offer prayers to Lord Ganesha on Sankashti Chaturthi for seamless academic success.",
                    "remedy_ta": "சங்கடஹர சதுர்த்தியன்று விநாயகரை வழிபட கல்வித்தடைகள் நீங்கும்."
                })

        # Technique 3 & 4: Affliction & Vehicle Accident Risk (3-Person Dynamic)
        if ashwini_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Ashwini",
                "technique_id": "ASHWINI_T3_T4_VEHICLE_CAUTION",
                "category": "ACCIDENT_CAUTION",
                "title_en": "Ashwini Affliction: High-Speed Vehicle Vigilance & Multi-Party Road Caution",
                "title_ta": "அசுவினி தோஷம்: வாகன பாதுகாப்பு எச்சரிக்கை & விபத்து தவிர்ப்பு விதி",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [p["name"] for p in ashwini_planets] + ashwini_affliction["malefic_aspectors"],
                "details_en": f"Ashwini is afflicted by: {'; '.join(ashwini_affliction['reasons'])}. Saptarishis research confirms a heightened tendency for vehicle scrapes or road collisions, often involving a 3-person dynamic (multiple passengers or pedestrian crossover). Vulnerable at shuttered late-night spots or wet road conditions.",
                "details_ta": f"அசுவினி நட்சத்திரத்தில் கிரக பாதிப்புகள் கண்டறியப்பட்டுள்ளன: {'; '.join(ashwini_affliction['reasons'])}. வாகனப் பிரயாணங்களில் அதிவேகத்தைத் தவிர்ப்பதும், இரவு நேரங்களில் கவனமாக இருப்பதும் அவசியம். விபத்து நடந்தால் 3 நபர்கள் தொடர்புடையதாக இருக்கும் அமைப்பு.",
                "case_study": "Saptarishis Examples 1-9: Multiple road accident case studies, John Nash automobile accident, Urmila Revankar cases.",
                "remedy_en": "Keep Hanuman Chalisa in your vehicle; install a small silver horseshoe or safety yantra; avoid overtaking rashly.",
                "remedy_ta": "வாகனத்தில் ஆஞ்சநேயர் படம் அல்லது வேல் வைக்கவும்; இரவு நேர அதிவேக பயணங்களை தவிர்க்கவும்."
            })

        # Technique 5: Punctuality Paradox
        if ashwini_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Ashwini",
                "technique_id": "ASHWINI_T5_PUNCTUALITY_PARADOX",
                "category": "BEHAVIORAL_TIMING",
                "title_en": "Ashwini Affliction: The Punctuality Paradox (Delays or Miraculous Delayed Starts)",
                "title_ta": "அசுவினி தோஷம்: காலதாமத முரண்பாடு (தாமதமாகச் சென்றாலும் காரியம் நடக்கும் விநோதம்)",
                "severity": "BEHAVIORAL_TRAIT",
                "trigger_grahas": [p["name"] for p in ashwini_planets],
                "details_en": "Classical dictum notes difficulty reaching scheduled destinations on time, or missing flights/trains minimum 3 times; conversely, when running late, events/meetings miraculously get delayed so the native never misses the start.",
                "details_ta": "நேரத்திற்கு கிளம்ப நினைத்தாலும் காலதாமதம் ஏற்படும் அமைப்பு. விமானம், ரயில் தவறவிடும் நிலை மூன்று முறை நிகழலாம். அல்லது விநோதமாக ஜாதகர் தாமதமாகச் சென்றாலும் அங்கு நிகழ்வு தாமதமாகவே தொடங்கும்.",
                "case_study": "Marilyn Monroe chronic lateness; Girish Ramakrishnan paradoxical timing luck.",
                "remedy_en": "Always build a mandatory 30-minute buffer into travel itineraries.",
                "remedy_ta": "எந்த பயணத்திற்கும் 30 நிமிடங்கள் முன்னதாகவே புறப்படும் பழக்கத்தை ஏற்படுத்தவும்."
            })

    # Technique 2: Any planet aspecting Ashwini = Master a Soul Lesson
    for asp_p in ashwini_aspectors:
        if asp_p not in [p["name"] for p in ashwini_planets]:
            lesson_map = {
                "Saturn": ("Master Selflessness, Discipline & Punctuality", "சுயநலமற்ற சேவை, காலந்தவறாமை மற்றும் ஒழுக்கத்தைக் கடைப்பிடித்தல்", "Mahatma Gandhi (Saturn in Jyeshtha aspecting Ashwini), Amitabh Bachchan."),
                "Mars": ("Master Physical Fitness & Control of Wrath/Ego", "உடற்பயிற்சி, ஆத்திரம் மற்றும் முன்விருப்பத்தைக் கட்டுப்படுத்துதல்", "Muhammad Ali boxing world champion; mastered fighting discipline."),
                "Moon": ("Master Compassion, Emotional Calm & Inner Serenity", "கருணை, அமைதியான மனம் மற்றும் தாய்மைப் பண்பை வளர்த்தல்", "John F. Kennedy (Moon in Purva Phalguni aspecting Ashwini)."),
                "Venus": ("Master Refinement without Sensual Over-Indulgence", "சிற்றின்ப அடிமைத்தனத்தைத் தவிர்த்து கலையுணர்வை வளர்த்தல்", "Saptarishis Classical Dictum."),
                "Sun": ("Master Dignified Leadership without Arrogance", "ஆணவமற்ற நல்வழிகாட்டுதல் மற்றும் தன்னலமற்ற தலைமைப் பண்பு", "JFK leadership mastery."),
                "Jupiter": ("Master Religious Tolerance & Righteous Guidance", "அனைத்து மதங்களையும் மதிக்கும் ஆழமான ஆன்மீக ஞானம்", "Muhammad Ali religious conversion to Islam."),
                "Mercury": ("Master Prudent Speech & Intellectual Discrimination", "புத்திசாலித்தனமான பேச்சு, வாக்குச் சுத்தம் மற்றும் நேர்மை", "Mark Zuckerberg & communicator cases."),
                "Rahu": ("Master Unorthodox Innovations & Cross-Cultural Wisdom", "பாரம்பரிய வழக்கங்களுக்கு அப்பால் நவீன புதுமைகளை ஏற்குதல்", "Muhammad Ali unorthodox fighting style."),
            }
            if asp_p in lesson_map:
                en_title, ta_title, cs = lesson_map[asp_p]
                matched_rules.append({
                    "nakshatra": "Ashwini",
                    "technique_id": f"ASHWINI_T2_LESSON_{asp_p.upper()}",
                    "category": "SOUL_LESSON",
                    "title_en": f"{asp_p} Aspects Ashwini: Soul Lesson to {en_title}",
                    "title_ta": f"அசுவினியை நோக்கும் {asp_p}: ஆன்ம பரிணாமப் பாடம் - {ta_title}",
                    "severity": "LIFE_LESSON",
                    "trigger_grahas": [asp_p],
                    "details_en": f"In Sarvatobhadra Chakra and Vedic Drik Shastra, {asp_p} casts a powerful aspect on Ashwini Nakshatra. This demands conscious mastery of {asp_p}'s highest virtues.",
                    "details_ta": f"சர்வோதோபத்ர சக்கரம் மற்றும் வேத பார்வையின்படி {asp_p} அசுவினி நட்சத்திரத்தை நோக்குகிறது. இது உங்கள் வாழ்க்கையில் {asp_p}-ன் உயர் பண்புகளை சுயமாக வளர்த்துக்கொள்ளக் கோருகிறது.",
                    "case_study": cs,
                    "remedy_en": f"Chant the seed mantra of {asp_p} to align its vibrational lessons.",
                    "remedy_ta": f"{asp_p} பகவானின் மூல மந்திரத்தை தினமும் 11 முறை ஜபிக்கவும்."
                })

    # =========================================================================
    # 2. BHARANI (பரணி)
    # =========================================================================
    bharani_planets = get_in_nak("Bharani")
    bharani_affliction = is_nak_afflicted("Bharani")

    if bharani_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Bharani",
            "name_ta": "பரணி",
            "lord": "Venus",
            "deity": "Yama",
            "symbol": "Yoni / Boat",
            "grahas": [p["name"] for p in bharani_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in bharani_planets]
        })

        # Technique 1: Feet / Ankles Bodily Vulnerability
        for p in bharani_planets:
            p_name = p["name"]
            h_owned = p["houses_owned"]
            h_pos = p["house"]

            rel_text_en = "Self (Native)"
            rel_text_ta = "ஜாதகர் (சுய உடல்)"
            if 4 in h_owned:
                rel_text_en = "Mother (4th Lord)"
                rel_text_ta = "தாய் (4-ம் அதிபதி)"
            elif 7 in h_owned or p_name == "Venus":
                rel_text_en = "Spouse / Partner (7th Lord / Venus)"
                rel_text_ta = "வாழ்க்கைத் துணை (7-ம் அதிபதி/சுக்கிரன்)"
            elif 9 in h_owned or p_name == "Sun":
                rel_text_en = "Father (9th Lord / Sun)"
                rel_text_ta = "தந்தை (9-ம் அதிபதி/சூரியன்)"
            elif 3 in h_owned:
                rel_text_en = "Younger Sibling (3rd Lord)"
                rel_text_ta = "இளைய சகோதரன்/சகோதரி"
            elif 11 in h_owned or h_pos == 11:
                rel_text_en = "Native's Left Wrist & Left Ankle (11th House)"
                rel_text_ta = "இடது கை மணிக்கட்டு மற்றும் இடது கணுக்கால்"
            elif p_name == "Mercury":
                rel_text_en = "Maternal Uncle (Mercury Karakatwa)"
                rel_text_ta = "தாய்மாமன்"

            body_part_alerts.append({
                "nakshatra": "Bharani",
                "graha": p_name,
                "relative_en": rel_text_en,
                "relative_ta": rel_text_ta,
                "organ": "Lower part of feet, heels, and ankles (or left wrist in 11H)",
            })

            matched_rules.append({
                "nakshatra": "Bharani",
                "technique_id": f"BHARANI_T1_FEET_ANKLE_{p_name.upper()}",
                "category": "MEDICAL_VULNERABILITY",
                "title_en": f"{p_name} in Bharani: Lower Feet & Ankle Vulnerability for {rel_text_en}",
                "title_ta": f"பரணியில் {p_name}: {rel_text_ta}-க்கு கணுக்கால் மற்றும் பாத பாதிப்பு எச்சரிக்கை",
                "severity": "CRITICAL_CAUTION" if bharani_affliction["afflicted"] else "IMPORTANT_MILESTONE",
                "trigger_grahas": [p_name],
                "details_en": f"Bharani rules the lower part of the feet and ankles. As per Saptarishis research, {p_name} placed here brings susceptibility to sprains, gout, fractures, or persistent scar marks on the feet for {rel_text_en}.",
                "details_ta": f"பரணி நட்சத்திரம் பாதங்களின் கீழ் பகுதி மற்றும் கணுக்காலைக் குறிக்கும். {p_name} இங்கு அமர்ந்திருப்பது {rel_text_ta}-க்கு கணுக்கால் வலி, தசைப்பிடிப்பு, கீல்வாதம் அல்லது விபத்துக் காயங்களை ஏற்படுத்தலாம்.",
                "case_study": "Naomi Campbell (Saturn in Bharani: cane/wheelchair), Jessica Alba (swollen ankles), Madonna (foot/ankle injury).",
                "remedy_en": "Wear comfortable orthopedic footwear; apply sesame oil on feet on Saturdays; practice grounded yoga.",
                "remedy_ta": "பாதங்களை எப்போதும் சுத்தமாகப் பராமரித்து, நல்ல மென்மையான காலணிகளை அணியவும்; சனிக்கிழமைகளில் நல்லெண்ணெய் தேய்க்கலாம்."
            })

            # Technique 5: Sudden Results
            matched_rules.append({
                "nakshatra": "Bharani",
                "technique_id": f"BHARANI_T5_SUDDEN_{p_name.upper()}",
                "category": "SUDDEN_EVENTS",
                "title_en": f"{p_name} in Bharani: Sudden Unforeseen Transformations in House {h_pos} Portfolios",
                "title_ta": f"பரணியில் {p_name}: {h_pos}-ம் பாவ விவகாரங்களில் திடீர் திருப்புமுனை",
                "severity": "IMPORTANT_MILESTONE",
                "trigger_grahas": [p_name],
                "details_en": f"Bharani signifies suddenness. Whatever house {p_name} rules ({h_owned}) or occupies (House {h_pos}) experiences abrupt changes with zero advance notice.",
                "details_ta": f"பரணி என்றாலே திடீர் நிகழ்வு என்று பொருள். {p_name} ஆளும் பாவங்கள் ({h_owned}) மற்றும் அமர்ந்த {h_pos}-ம் பாவம் சார்ந்த விஷயங்களில் எதிர்பாராத திடீர் திருப்பங்கள் உண்டாகும்.",
                "case_study": "Saptarishis Technique 5 real life examples: Sudden marriage, sudden career rises/falls.",
                "remedy_en": "Cultivate adaptable readiness; avoid making rigid long-term speculations without backup.",
                "remedy_ta": "திடீர் மாற்றங்களுக்கு எப்போதும் மனதளவில் தயாராக இருக்கவும்."
            })

            # Technique 7: Yama's Justice & Reversal
            if 1 in h_owned or 10 in h_owned or p_name == "Venus":
                matched_rules.append({
                    "nakshatra": "Bharani",
                    "technique_id": f"BHARANI_T7_YAMA_JUSTICE_{p_name.upper()}",
                    "category": "KARMIC_AUDIT",
                    "title_en": f"{p_name} in Bharani: Yama's Justice & Radical Karmic Transformation",
                    "title_ta": f"பரணியில் {p_name}: தர்மராஜன் எமனின் நியாயத் தீர்ப்பு & பெருவாழ்வு திருப்பங்கள்",
                    "severity": "LIFE_LESSON",
                    "trigger_grahas": [p_name],
                    "details_en": f"Governed by Lord Yama, Bharani subjects {p_name} (House {h_pos}, ruling {h_owned}) to a rigorous test of integrity and ethics. Crests and troughs in social status test spiritual principles.",
                    "details_ta": f"எமதர்மன் அதிபதியாக விளங்குவதால், ஜாதகர் தனது ஒழுக்கத்திலும் சத்தியத்திலும் உறுதியாக இருக்க வேண்டும். பெரும் புகழும், அதைத் தொடர்ந்து நியாயத் தீர்ப்புகளும் வாழ்வின் திருப்புமுனையாக அமையும்.",
                    "case_study": "Adolf Hitler (Lagna Lord Venus in Bharani), Cher, Gayatri Devi.",
                    "remedy_en": "Practice transparent truthfulness in business and relationships; feed the destitute on Tuesdays/Fridays.",
                    "remedy_ta": "எப்போதும் தர்ம வழியில் நடக்கவும்; ஏழை எளியவர்களுக்கு அன்னதானம் செய்யவும்."
                })

        # Technique 4: Sensual Burnout (if connected with 7, 8, 12)
        sensual_grahas = [p for p in bharani_planets if p["name"] in ("Mercury", "Rahu", "Moon", "Venus", "Mars")]
        for p in sensual_grahas:
            p_name = p["name"]
            h_owned = p["houses_owned"]
            h_pos = p["house"]
            if any(h in (7, 8, 12) for h in h_owned) or h_pos in (7, 8, 12):
                matched_rules.append({
                    "nakshatra": "Bharani",
                    "technique_id": f"BHARANI_T4_SENSUAL_BURNOUT_{p_name.upper()}",
                    "category": "RELATIONSHIP_WARNING",
                    "title_en": f"{p_name} in Bharani linked to 7/8/12th Houses: Intense Sensuality & Burnout Caution",
                    "title_ta": f"பரணியில் 7, 8, 12-ம் தொடர்புற்ற {p_name}: தீவிர உணர்ச்சி வேகம் மற்றும் சலிப்புத் தடுப்பு",
                    "severity": "CRITICAL_CAUTION",
                    "trigger_grahas": [p_name],
                    "details_en": f"{p_name} in Bharani connects with sexual/secret houses. Classical research warns that romantic affairs ignite with volcanic passion but risk burning out just as abruptly, leading to boredom or unwise impulse choices.",
                    "details_ta": f"{p_name} பரணியில் காம/மறைவு ஸ்தானங்களுடன் தொடர்பு பெற்றுள்ளது. ஆரம்பத்தில் அதீத ஈர்ப்புடனும், பின்னர் விரைவிலேயே சலிப்பு தட்டவும் வாய்ப்புள்ளது. உறவுகளில் விவேகமும் பொறுமையும் அவசியம்.",
                    "case_study": "Monica Lewinsky (Moon in Bharani in 7H), Demi Moore.",
                    "remedy_en": "Build relationships on shared intellectual values and mutual spiritual respect rather than transient physical chemistry.",
                    "remedy_ta": "வெறும் தோற்ற ஈர்ப்பை மட்டும் நம்பாமல், குணநலன்களைப் பார்த்து உறவுகளை உறுதி செய்யவும்."
                })

        # Technique 6: The Transforming Woman
        matched_rules.append({
            "nakshatra": "Bharani",
            "technique_id": "BHARANI_T6_TRANSFORMING_WOMAN",
            "category": "KEY_PEOPLE",
            "title_en": "Key Graha in Bharani: A Catalyst Woman Will Revolutionize Your Worldview",
            "title_ta": "பரணி சிறப்பு விதி: ஒரு பெண் உங்கள் வாழ்க்கைப் பார்வையை புரட்டிப் போடும் அமைப்பு",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in bharani_planets],
            "details_en": "Saptarishis Technique 6: A significant female figure (partner, strict employee, associate, or mentor) enters your life. Her uncompromising, tough, or unorthodox demeanor shakes you out of naivety and makes you street-smart.",
            "details_ta": "உங்கள் வாழ்க்கையில் ஒரு பெண் (அவர் காதலியாக இருக்க வேண்டிய அவசியமில்லை; சக ஊழியர், வழிகாட்டி அல்லது பங்குதாரராக இருக்கலாம்) வந்து உங்கள் அப்பாவித்தனத்தை நீக்கி, நடைமுறை உலகுக்கு ஏற்ற விவேகியான நபராக மாற்றுவார்.",
            "case_study": "Saptarishis Examples 1-3: Transforming ex-girlfriend, junior employee transforming boss's perspective.",
            "remedy_en": "Respect tough feedback from capable women around you; view criticism as a catalyst for maturity.",
            "remedy_ta": "திறமையான பெண்களின் கடுமையான ஆலோசனைகளையும் உங்களை செதுக்கும் நல்வாய்ப்பாக ஏற்கவும்."
        })

    # =========================================================================
    # 3. KRITTIKA (கிருத்திகை)
    # =========================================================================
    krittika_planets = get_in_nak("Krittika")
    krittika_affliction = is_nak_afflicted("Krittika")

    if krittika_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Krittika",
            "name_ta": "கிருத்திகை",
            "lord": "Sun",
            "deity": "Agni",
            "symbol": "Knife / Razor / Blade",
            "grahas": [p["name"] for p in krittika_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in krittika_planets]
        })

        # Technique 1: The "Split Into Two" Razor/Blade Principle
        for p in krittika_planets:
            p_name = p["name"]
            h_owned = p["houses_owned"]
            h_pos = p["house"]

            split_scope_en = "Affairs of house"
            split_scope_ta = "பாவ விவகாரங்கள்"
            if 2 in h_owned:
                split_scope_en = "Family & Joint Wealth (2nd Lord): Family property partition or bifurcation into separate branches"
                split_scope_ta = "குடும்பம் & பூர்வீக சொத்து (2-ம் அதிபதி): குடும்பம் இரண்டாகப் பிரிதல் அல்லது பாகப்பிரிவினை"
            elif 3 in h_owned:
                split_scope_en = "Siblings & Ears (3rd Lord): Differences and partition with siblings; potential ear surgery (surgical blade incision)"
                split_scope_ta = "சகோதரர் & காது (3-ம் அதிபதி): உடன்பிறப்புகளுடன் கருத்து வேறுபாடு/பிரிவு; காது சிகிச்சை/அறுவை சிகிச்சை"
            elif 4 in h_owned or p_name == "Ascendant":
                split_scope_en = "Motherland & Real Estate (4th Lord / Lagna): Splitting of ancestral territory or property walls"
                split_scope_ta = "தாய்மண் & நிலம் (4-ம் அதிபதி/லக்னம்): பூர்வீக நிலம்/வீடு பாகப்பிரிவினை அல்லது எல்லைச் சுவர் அமைத்தல்"
            elif 9 in h_owned:
                split_scope_en = "Father or Guru (9th Lord): Father or mentor faces health condition requiring surgical operation with blade/knife"
                split_scope_ta = "தந்தை அல்லது குரு (9-ம் அதிபதி): தந்தை அல்லது குருவுக்கு அறுவை சிகிச்சை (ஆபரேஷன்) நிகழும் அமைப்பு"

            matched_rules.append({
                "nakshatra": "Krittika",
                "technique_id": f"KRITTIKA_T1_SPLIT_{p_name.upper()}",
                "category": "BIFURCATION_SURGERY",
                "title_en": f"{p_name} in Krittika: The Sharp Knife/Blade Bifurcation — {split_scope_en}",
                "title_ta": f"கிருத்திகையில் {p_name}: அக்னி/கத்தி போன்று இரண்டாகப் பிளக்கும் விதி — {split_scope_ta}",
                "severity": "IMPORTANT_MILESTONE",
                "trigger_grahas": [p_name],
                "details_en": f"Krittika is ruled by Agni and symbolized by a razor/spear. Any planet here divides or cuts into two parts: {split_scope_en}.",
                "details_ta": f"அக்னி பகவானின் ஆதிக்கமும், கத்தி/சவரக்கத்தி சின்னமும் கொண்ட கிருத்திகையில் உள்ள கிரகம் இரண்டாகப் பிளக்கும் தன்மையைத் தரும்: {split_scope_ta}.",
                "case_study": "Walter Ulbricht (4L Jupiter in Krittika: Berlin Wall divided Germany), India Independence chart (Lagna/Rahu in Krittika: Partition), Louis Pasteur (Jupiter+Moon in Krittika: splitting polarized light).",
                "remedy_en": "Worship Lord Muruga (Karthikeya) on Sashti with ghee lamp to resolve sharp conflicts peacefully.",
                "remedy_ta": "சஷ்டி திதிகளில் முருகப்பெருமானுக்கு நெய் தீபமேற்றி வழிபட பிளவுகள் நீங்கி நன்மை உண்டாகும்."
            })

            # Technique 2: Rejection Heartburn
            if any(h in (5, 7, 8) for h in h_owned) or p_name in ("Venus", "Moon", "Ascendant"):
                matched_rules.append({
                    "nakshatra": "Krittika",
                    "technique_id": f"KRITTIKA_T2_REJECTION_HEARTBURN_{p_name.upper()}",
                    "category": "ROMANTIC_REJECTION",
                    "title_en": f"{p_name} in Krittika: Romantic Rejection & Emotional Metamorphosis",
                    "title_ta": f"கிருத்திகையில் {p_name}: காதல் நிராகரிப்பு மற்றும் அதிலிருந்து எழும் பெரும் உத்வேகம்",
                    "severity": "LIFE_LESSON",
                    "trigger_grahas": [p_name],
                    "details_en": "Key planets in Krittika indicate an experience of painful romantic rejection that initially burns deeply into the native's pride, but ultimately spurs a colossal evolutionary and material leap.",
                    "details_ta": "காதலில் அல்லது திருமணப் பேச்சுவார்த்தையில் ஏற்படும் எதிர்பாராத நிராகரிப்பு பெரும் மனவேதனையைத் தரும். ஆனால் அதே நிராகரிப்பு உங்களை வாழ்க்கையில் சாதிக்கத் தூண்டும் பெரும் சக்தியாக மாறும்.",
                    "case_study": "Saptarishis Example 1: Native rejected by partner, which triggered total positive life transformation.",
                    "remedy_en": "Chant Gayatri Mantra daily to purify emotional agitation and elevate consciousness.",
                    "remedy_ta": "தினமும் காயத்ரி மந்திரம் கூறி வர மன உளைச்சல் நீங்கி தெளிவு பிறக்கும்."
                })

            # Technique 3: Age 27 Milestone
            if p_name in ("Sun", "Moon", "Ascendant") or 1 in h_owned:
                is_past = native_age is not None and native_age > 27
                is_current = native_age == 27
                age_milestones.append({
                    "age": 27,
                    "nakshatra": "Krittika",
                    "graha": p_name,
                    "status": "PAST" if is_past else ("CURRENT" if is_current else "UPCOMING"),
                    "event_en": "Pivotal career leap, resignation, starting own business, overseas relocation, or qualifying milestone",
                    "event_ta": "தொழில் புதிய தொடக்கம், வேலையை விட்டு சொந்த தொழில் தொடங்குதல், வெளிநாட்டுப் பயணம் அல்லது முக்கிய வெற்றி",
                })
                matched_rules.append({
                    "nakshatra": "Krittika",
                    "technique_id": "KRITTIKA_T3_AGE_27_MILESTONE",
                    "category": "AGE_TRIGGER",
                    "title_en": f"Key Graha {p_name} in Krittika: Life-Defining Milestone at Age 27",
                    "title_ta": f"கிருத்திகையில் முக்கிய கிரகம் {p_name}: 27-வது வயதில் வாழ்க்கையை மாற்றும் பெரும் நிகழ்வு",
                    "severity": "IMPORTANT_MILESTONE",
                    "trigger_grahas": [p_name],
                    "details_en": f"Having {p_name} in Krittika triggers a significant, destiny-defining event around the 27th year of life (major relocation, career shift, starting business, or qualifying exams). Current status: {'Already experienced in 27th year' if is_past else ('ACTIVATED RIGHT NOW AT AGE 27!' if is_current else f'Will activate at age 27 (in {27 - (native_age or 0)} years)')}.",
                    "details_ta": f"கிருத்திகையில் உள்ள {p_name} 27-வது வயதில் வாழ்க்கையின் போக்கையே மாற்றும் திருப்புமுனை நிகழ்வைத் தரும் (வேலை மாற்றம், சொந்த தொழில், முக்கிய படிப்பு அல்லது திருமணம்).",
                    "case_study": "Saptarishis Examples 1-5: Resigning military to start business, unexpected CFA graduation, major relocation.",
                    "remedy_en": "Perform a special archana to Lord Kartikeya during your 27th year.",
                    "remedy_ta": "27-வது வயதில் முருகப் பெருமானுக்கு விசேஷ அர்ச்சனை செய்து வர நன்மைகள் கூடும்."
                })

            # Technique 4: Father-Son Karmic Payback
            if 9 in h_owned or 5 in h_owned or p_name in ("Sun", "Jupiter"):
                matched_rules.append({
                    "nakshatra": "Krittika",
                    "technique_id": "KRITTIKA_T4_FATHER_SON_KARMA",
                    "category": "FAMILY_KARMA",
                    "title_en": f"{p_name} in Krittika: Karmic Payback & Mutual Debts Between Father and Son",
                    "title_ta": f"கிருத்திகையில் {p_name}: தந்தை மற்றும் மகன் இடையேயான பூர்வ புண்ணியக் கடன் தீர்ப்பு",
                    "severity": "LIFE_LESSON",
                    "trigger_grahas": [p_name],
                    "details_en": "Dictum dictates that the native and their father/child share a deep karmic obligation where one must bail out, financially support, or spiritually rescue the other during a critical life juncture.",
                    "details_ta": "தந்தை மற்றும் மகன் இடையில் ஆழ்ந்த கர்மப் பிணைப்பு உண்டு. ஒருவர் மற்றவருக்கு இக்கட்டான காலகட்டத்தில் பெரும் உதவி செய்து கடனைத் தீர்க்கும் நிலை உருவாகும்.",
                    "case_study": "Sunil Dutt & Sanjay Dutt (9L Moon in Krittika): father rescuing son from catastrophic crises.",
                    "remedy_en": "Honor father and ancestors on Amavasya days with tarpanam and sesame water offering.",
                    "remedy_ta": "அமாவாசை தோறும் முன்னோர்களுக்கும் தந்தைக்கும் மரியாதை செலுத்தி எள் தர்பணம் செய்யவும்."
                })

    # =========================================================================
    # 4. ROHINI (ரோகிணி)
    # =========================================================================
    rohini_planets = get_in_nak("Rohini")
    rohini_affliction = is_nak_afflicted("Rohini")

    if rohini_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Rohini",
            "name_ta": "ரோகிணி",
            "lord": "Moon",
            "deity": "Brahma / Prajapati",
            "symbol": "Cart / Temple / Banyan Tree",
            "grahas": [p["name"] for p in rohini_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in rohini_planets]
        })

        # Technique 1: False Accusations / Blamed for an Uncommitted Act
        matched_rules.append({
            "nakshatra": "Rohini",
            "technique_id": "ROHINI_T1_FALSE_ACCUSATION",
            "category": "LEGAL_SCANDAL",
            "title_en": "Key Graha in Rohini: Blamed for an Act Never Committed (False Accusation Risk)",
            "title_ta": "ரோகிணியில் கிரகம்: செய்யாத தவறுக்கு பழி சுமக்கும் யோகம் & அபாண்ட அபாயம்",
            "severity": "CRITICAL_CAUTION" if rohini_affliction["afflicted"] else "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in rohini_planets],
            "details_en": f"Planets in Rohini ({', '.join([p['name'] for p in rohini_planets])}) {'under affliction' if rohini_affliction['afflicted'] else ''} indicate that at least once in their lifetime, the native will be unfairly blamed, suspected, or falsely accused of something they never committed.",
            "details_ta": f"ரோகிணி நட்சத்திரத்தில் கிரகங்கள் அமர்வது, வாழ்க்கையில் ஒரு முறையாவது செய்யாத தவறுக்காக வீண் பழி, அவப்பெயர் அல்லது அலுவலக/குடும்பத்தில் தவறாக சந்தேகிக்கப்படும் சூழ்நிலையை உருவாக்கும்.",
            "case_study": "Robert Netter (blood scandal acquittal), Marc Machin (judicial error jailed for double murder he did not commit), Paula Abdul.",
            "remedy_en": "Maintain strict written paper trails and digital receipts for sensitive actions; recite Durga Kavacham.",
            "remedy_ta": "அனைத்து முக்கிய விவகாரங்களிலும் எழுத்துப்பூர்வ ஆதாரங்களை வைத்திருக்கவும்; துர்க்கை கவசம் பாராயணம் செய்யவும்."
        })

        # Technique 3: Comparison of Spouse
        matched_rules.append({
            "nakshatra": "Rohini",
            "technique_id": "ROHINI_T3_COMPARE_SPOUSE",
            "category": "MARITAL_HABITS",
            "title_en": "Graha in Rohini: Habitual Comparison of Spouse with Past Standards or Mother",
            "title_ta": "ரோகிணியில் கிரகம்: வாழ்க்கைத்துணையை மற்றவருடன் ஒப்பிட்டுப் பார்க்கும் சுபாவம்",
            "severity": "BEHAVIORAL_TRAIT",
            "trigger_grahas": [p["name"] for p in rohini_planets],
            "details_en": "Native has a subtle sub-conscious tendency to compare spouse's cooking, habits, or looks with mother, previous partners, or siblings' spouses, risking avoidable domestic irritation.",
            "details_ta": "வாழ்க்கைத் துணையின் சமையல், பழக்கவழக்கங்கள் அல்லது குணங்களை தனது தாய் அல்லது முந்தைய உறவுகளுடன் ஒப்பிட்டுப் பேசும் மனோபாவம் இருக்கும். இதை தவிர்ப்பது குடும்ப அமைதிக்கு நல்லது.",
            "case_study": "Saptarishis Example 1: Female native constantly compares husband's behavior with sister's husband.",
            "remedy_en": "Accept and celebrate your partner's unique individuality; avoid verbal comparisons.",
            "remedy_ta": "துணையின் தனித்துவத்தை மதித்து, அவரை பிறருடன் ஒப்பிடுவதை முற்றிலும் தவிர்க்கவும்."
        })

        # Technique 4: Incest / Family Boundary Caution
        if rohini_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Rohini",
                "technique_id": "ROHINI_T4_BOUNDARY_CAUTION",
                "category": "FAMILY_BOUNDARIES",
                "title_en": "Afflicted Rohini: Family Boundary Vigilance & Relative Complexities",
                "title_ta": "பாதிக்கப்பட்ட ரோகிணி: குடும்ப எல்லைகள் மற்றும் உறவினர் விவகாரங்களில் எச்சரிக்கை",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [p["name"] for p in rohini_planets],
                "details_en": "Afflicted planets in Rohini require maintaining healthy, protective boundaries regarding extended family, in-laws, or unscrupulous relatives.",
                "details_ta": "ரோகிணியில் கிரகப் பாதிப்பு இருக்கும்போது தூரத்து உறவினர்கள் மற்றும் குடும்பத்தினரிடம் தகுந்த இடைவெளியையும் பாதுகாப்பான எல்லைகளையும் கடைப்பிடிப்பது அவசியமாகும்.",
                "case_study": "Virginia Woolf, Maryse Audouit, Carol Hemingway case studies.",
                "remedy_en": "Uphold clear personal autonomy; recite Sri Narasimha Kavacham for fierce aura protection.",
                "remedy_ta": "ஸ்ரீ நரசிம்மர் கவசம் பாராயணம் செய்து வர குடும்ப விவகாரங்களில் பாதுகாப்பு கிட்டும்."
            })

        # Technique 5: Plagiarism, Forgery, Copyright Issues
        matched_rules.append({
            "nakshatra": "Rohini",
            "technique_id": "ROHINI_T5_PLAGIARISM_IP",
            "category": "INTELLECTUAL_PROPERTY",
            "title_en": "Key Graha in Rohini: Plagiarism, Forgery & Copyright Infringement Caution",
            "title_ta": "ரோகிணியில் கிரகம்: காப்புரிமை திருட்டு, கையெழுத்து மோசடி மற்றும் ஆவண பாதுகாப்பு",
            "severity": "CRITICAL_CAUTION" if rohini_affliction["afflicted"] else "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in rohini_planets],
            "details_en": "Key planets in Rohini create high exposure to intellectual property matters: work getting stolen without credit, dealing with forged documents/signatures, or accusations of copyright infringement.",
            "details_ta": "ரோகிணி நட்சத்திரத்தில் கிரகம் அமைந்தால், உங்கள் ஆக்கங்கள் பிறரால் திருடப்படவோ அல்லது கையெழுத்துப் போலி, போலி ஆவணங்கள், காப்புரிமை (Copyright) சர்ச்சைகள் ஏற்படவோ வாய்ப்புண்டு.",
            "case_study": "Jillian Norris (student stole tarot book), Gilles Bernheim (ghostwriter scandal), Joe Biden (1987 speech plagiarism controversies), Amitabh Bachchan (copyright on voice).",
            "remedy_en": "Copyright and timestamp all original creative work; never sign blank registers or documents for others.",
            "remedy_ta": "உங்கள் படைப்புகளுக்கு உரிய காப்புரிமை பெறவும்; பிறருக்காக வெற்றுத் தாள்களில் அல்லது பதிவேடுகளில் கையெழுத்திட வேண்டாம்."
        })

    # Technique 2: Pluto or Neptune in Rohini
    for outer_p in ("Pluto", "Neptune"):
        if outer_p in planets and "rohini" in planets[outer_p]["nakshatra_name"].lower():
            p_pada = planets[outer_p]["pada"]
            age_milestones.append({
                "age": "38-50 or 65-75",
                "nakshatra": "Rohini",
                "graha": outer_p,
                "status": "VULNERABILITY_WINDOW",
                "event_en": f"{outer_p} in Rohini: Heightened water hazard, drowning risk, or critical medical crisis",
                "event_ta": f"ரோகிணியில் {outer_p}: நீர்நிலைகளில் ஆபத்து அல்லது உடல்நல நெருக்கடி காலகட்டம்",
            })
            matched_rules.append({
                "nakshatra": "Rohini",
                "technique_id": f"ROHINI_T2_OUTER_PLANET_{outer_p.upper()}",
                "category": "WATER_MORTALITY_ALERT",
                "title_en": f"{outer_p} in Rohini Pada {p_pada}: Water Hazard & Critical Health Period (Ages 38-50 or 65-75)",
                "title_ta": f"ரோகிணியில் {outer_p}: நீர் சார்ந்த ஆபத்துகள் & முக்கிய உடல்நல எச்சரிக்கை வயதுகள்",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [outer_p],
                "details_en": f"Having {outer_p} in Rohini points to vulnerable crisis periods between ages 38-50 or 65-75 involving deep water hazards, pulmonary complications, or sudden critical illness.",
                "details_ta": f"ரோகிணியில் {outer_p} அமைந்திருப்பதால், 38-50 அல்லது 65-75 வயதுகளில் ஆழமான நீர்நிலைகளில் இறங்குவதைத் தவிர்ப்பதும், ஆரோக்கியத்தில் மிகுந்த கவனம் செலுத்துவதும் அவசியமாகும்.",
                "case_study": "Jawaharlal Nehru (Neptune & Pluto in Rohini), Alfonsina Storni (drowned at 47), Paramahansa Yogananda.",
                "remedy_en": "Avoid deep water excursions and swimming alone; perform Mrityunjaya Homa during milestone years.",
                "remedy_ta": "ஆழமான நீர்நிலைகளில் நீராடுவதைத் தவிர்க்கவும்; ஆயுஷ் ஹோமம் செய்து வழிபடவும்."
            })

    # =========================================================================
    # 5. MRIGASHIRA (மிருகசீரிஷம்)
    # =========================================================================
    mrigashira_planets = get_in_nak("Mrigashira")
    mrigashira_affliction = is_nak_afflicted("Mrigashira")

    if mrigashira_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Mrigashira",
            "name_ta": "மிருகசீரிஷம்",
            "lord": "Mars",
            "deity": "Soma / Chandra",
            "symbol": "Deer's Head",
            "grahas": [p["name"] for p in mrigashira_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in mrigashira_planets]
        })

        # Technique 1 & 2: Children Late Fortune & Upbringing Friction
        matched_rules.append({
            "nakshatra": "Mrigashira",
            "technique_id": "MRIGASHIRA_T1_T2_CHILDREN_TRAITS",
            "category": "CHILDREN_PARENTING",
            "title_en": "Key Graha in Mrigashira: Children's Late Fortune & Strict Upbringing Dynamics",
            "title_ta": "மிருகசீரிஷத்தில் கிரகம்: குழந்தைகளுக்கு தாமத யோகம் & வளர்ப்பில் கண்டிப்பு",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in mrigashira_planets],
            "details_en": "Children of natives with key planets in Mrigashira often settle and attain fortune later in life (typically after age 40). Upbringing may involve frequent scolding, strict discipline, or early physical separation due to career/schooling.",
            "details_ta": "மிருகசீரிஷத்தில் கிரகங்கள் இருப்பவர்களின் குழந்தைகளுக்கு 40 வயதுக்குப் பிறகே நிலையான யோகமும் செல்வமும் அமையும். குழந்தைகள் வளர்ப்பில் அதிக கண்டிப்பும் அல்லது படிப்பு காரணமாக தற்காலிகப் பிரிவும் ஏற்படலாம்.",
            "case_study": "Saptarishis Examples 1-4: Late fortune after 40 for offspring, strict paternal scolding.",
            "remedy_en": "Nurture children with gentle warmth rather than sharp perfectionism; chant Santana Gopala Stotram.",
            "remedy_ta": "குழந்தைகளிடம் கண்டிப்பை குறைத்து அன்பை வெளிப்படுத்தவும்; சந்தான கோபால மந்திரம் ஜபிக்கவும்."
        })

        # Technique 3: Sports (Chasing Opponent / Running)
        matched_rules.append({
            "nakshatra": "Mrigashira",
            "technique_id": "MRIGASHIRA_T3_RUNNING_SPORTS",
            "category": "SPORTS_PHYSICAL",
            "title_en": "Mrigashira Talent: Running Sports & Chasing Opponents (Football, Sprinting, Athletics)",
            "title_ta": "மிருகசீரிஷ ஆற்றல்: ஓடுதல், பந்தயம் மற்றும் எதிராளியைத் துரத்தும் விளையாட்டு ஆர்வம்",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in mrigashira_planets],
            "details_en": "Symbolized by the swift searching deer, Mrigashira bestows high agility and athletic prowess, especially in sports that require chasing an opponent or racing (soccer, football, boxing, golf, sprinting).",
            "details_ta": "மான் தலை சின்னத்தைக் கொண்ட மிருகசீரிஷம் வேகமான ஓட்டம், சுறுசுறுப்பு மற்றும் எதிராளியைத் துரத்தும் விளையாட்டுக்களில் (கால்பந்து, குத்துச்சண்டை, தடகளம்) சிறந்து விளங்கும் ஆற்றலைத் தரும்.",
            "case_study": "David Beckham (Lagna Lord Venus in Mrigashira), Tiger Woods (Mars in Mrigashira), Jean-Michel Larque, Alan Hansen.",
            "remedy_en": "Channel natural restlessness into regular cardiovascular running or team sports.",
            "remedy_ta": "தினசரி ஓட்டப்பயிற்சி அல்லது விளையாட்டுகளில் ஈடுபடுவது மன அமைதியைத் தரும்."
        })

        # Technique 4: Leftover / Junk Food Connection
        has_6h_link = any(p["house"] == 6 or 6 in p["houses_owned"] for p in mrigashira_planets)
        if has_6h_link or "Moon" in [p["name"] for p in mrigashira_planets] or "Ascendant" in [p["name"] for p in mrigashira_planets]:
            matched_rules.append({
                "nakshatra": "Mrigashira",
                "technique_id": "MRIGASHIRA_T4_LEFTOVER_JUNK_FOOD",
                "category": "DIET_HABITS",
                "title_en": "Mrigashira 6th House Connection: Habitual Leftover Food or Craving for Re-fried Fast Foods",
                "title_ta": "மிருகசீரிஷம் 6-ம் பாவ தொடர்பு: பழைய உணவு உண்ணும் பழக்கம் & துரித உணவு ஈர்ப்பு",
                "severity": "BEHAVIORAL_TRAIT",
                "trigger_grahas": [p["name"] for p in mrigashira_planets],
                "details_en": "Connection between Mrigashira and the 6th house/lord creates a daily domestic pattern of preparing excess food and consuming leftovers the next day, or a strong penchant for re-fried junk foods (samosas, spicy snacks).",
                "details_ta": "மிருகசீரிஷத்திற்கு 6-ம் பாவ தொடர்பு ஏற்படுகையில், வீட்டில் அதிக உணவு சமைத்து அடுத்த நாளும் பழைய உணவை உண்ணும் பழக்கமோ, அல்லது எண்ணெய் பலகாரங்கள் மற்றும் பாஸ்ட் புட் உணவுகளில் அதீத ஈர்ப்போ இருக்கும்.",
                "case_study": "Saptarishis Examples 1-7: Rosie O'Donnell, Jennifer Lawrence, domestic leftover food cases.",
                "remedy_en": "Prioritize freshly prepared warm meals; reduce reheated fried foods to protect digestive agni.",
                "remedy_ta": "எப்போதும் புதிதாக சமைத்த சூடான உணவை உண்ண பழகவும்; பழைய உணவுகளைத் தவிர்க்கவும்."
            })

        # Technique 5: Maps & Direction Genius (if unafflicted)
        if not mrigashira_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Mrigashira",
                "technique_id": "MRIGASHIRA_T5_MAP_NAVIGATION",
                "category": "SPATIAL_GENIUS",
                "title_en": "Unafflicted Mrigashira: Exceptional Spatial Navigation, Maps & Directional Sense",
                "title_ta": "சுப மிருகசீரிஷம்: சிறந்த திசையறியும் திறன், வரைபட மேதைமை & வழிநடத்துதல்",
                "severity": "POSITIVE_TALENT",
                "trigger_grahas": [p["name"] for p in mrigashira_planets],
                "details_en": "Natural searcher and pathfinder; native (or signified partner/father) possesses an uncanny internal GPS, easily reading maps and never losing direction in unfamiliar terrain.",
                "details_ta": "மிருகசீரிஷம் தேடுதலின் நட்சத்திரம். வரைபடங்களைப் புரிந்துகொள்வதிலும், புதிய ஊர்களில் வழி தவறாமல் மிகச்சரியான திசையை அறிவதிலும் இயல்பான ஞானம் இருக்கும்.",
                "case_study": "Dr. Frederick Cook (Polar explorer), Laurent Bourgnon (famed ocean navigator).",
                "remedy_en": "Use this intuitive spatial gift in project architecture, travel logistics, and real estate layout.",
                "remedy_ta": "இந்த திசையறியும் ஆற்றலை தொழில் மேலாண்மை மற்றும் திட்டமிடலுக்கு பயன்படுத்தலாம்."
            })
        else:
            matched_rules.append({
                "nakshatra": "Mrigashira",
                "technique_id": "MRIGASHIRA_T5_DIRECTION_FLAW",
                "category": "SPATIAL_CAUTION",
                "title_en": "Afflicted Mrigashira: Flawed Blueprints or Disorientation in Transit",
                "title_ta": "அசுப மிருகசீரிஷம்: வழி தவறிப் போதல் அல்லது வீட்டின் வரைபடத்தில் குறைபாடுகள்",
                "severity": "BEHAVIORAL_TRAIT",
                "trigger_grahas": [p["name"] for p in mrigashira_planets],
                "details_en": "Under affliction, native often loses their way during transit or encounters flawed house blueprints, deed boundaries, or registration paper anomalies.",
                "details_ta": "மிருகசீரிஷத்தில் அசுப தொடர்பு உள்ளதால், பயணங்களின் போது வழி மாறுதல் அல்லது வீட்டு மனை வரைபடங்களில் தவறான எல்லைக் குறிகள் அமைய வாய்ப்புள்ளது.",
                "case_study": "Saptarishis Technique 5 caveat on afflicted charts.",
                "remedy_en": "Thoroughly double-check GPS routes and civil engineer structural blueprints.",
                "remedy_ta": "வீட்டுப் பத்திர வரைபடங்களை பொறியாளர் கொண்டு துல்லியமாக மறுஆய்வு செய்யவும்."
            })

        # Technique 6: 5th Lord in Mrigashira -> Property Division Dispute
        for p in mrigashira_planets:
            if 5 in p["houses_owned"]:
                matched_rules.append({
                    "nakshatra": "Mrigashira",
                    "technique_id": "MRIGASHIRA_T6_PROPERTY_DISPUTE",
                    "category": "INHERITANCE_DISPUTES",
                    "title_en": "5th Lord in Mrigashira: Offspring Grievances During Property/Inheritance Division",
                    "title_ta": "மிருகசீரிஷத்தில் 5-ம் அதிபதி: சொத்துப் பிரிவினையின் போது பிள்ளைகளிடையே அதிருப்தி",
                    "severity": "CRITICAL_CAUTION",
                    "trigger_grahas": [p["name"]],
                    "details_en": "Even with perfectly equal 33% divisions, children will harbour grudges regarding which side, facing direction, or corner of the ancestral property they received.",
                    "details_ta": "சொத்துக்களை பிள்ளைகளுக்கு சமமாகப் பிரித்துக் கொடுத்தாலும், ஒரு பிள்ளை தனக்கு ஒதுக்கப்பட்ட திசை அல்லது பகுதியைக் குறித்து மனக்கசப்பு அடைவார்.",
                    "case_study": "Saptarishis Technique 6 explicit dictum.",
                    "remedy_en": "Establish transparent, legally registered family settlement deeds with mutual consensus.",
                    "remedy_ta": "குடும்ப பாகப்பிரிவினையை அனைவரின் முழு சம்மதத்துடன் சட்டப்பூர்வமாக பதிவு செய்யவும்."
                })

        # Technique 7: Vastu Ishanya (North-East) Defect
        mars_afflicted = is_nak_afflicted(planets.get("Mars", {}).get("nakshatra_name", ""))["afflicted"]
        if mrigashira_affliction["afflicted"] or mars_afflicted:
            vastu_advisories.append({
                "direction": "North-East (Ishanya)",
                "defect_risk": "Toilet, septic tank, cut corner, entrance blemish, or broken wall in North-East",
                "remedy": "Place a brass Gangajal vessel or Sri Yantra in NE; keep area impeccably light and clean",
            })
            matched_rules.append({
                "nakshatra": "Mrigashira",
                "technique_id": "MRIGASHIRA_T7_VASTU_NE_DEFECT",
                "category": "VASTU_REMEDY",
                "title_en": "Afflicted Mrigashira / Mars: Vastu Blemish in North-East (Ishanya) Corner",
                "title_ta": "மிருகசீரிஷம்/செவ்வாய் பாதிப்பு: வீட்டின் வடகிழக்கு (ஈசானியம்) வாஸ்து குறைபாடு",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [p["name"] for p in mrigashira_planets] + ["Mars"],
                "details_en": "Empirical Vastu research proves that when planets in Mrigashira or Mars are afflicted, the native's residence will feature an afflicted North-East corner (toilet in NE, cut corner, septic tank underneath, or heavy load).",
                "details_ta": "மிருகசீரிஷம் அல்லது செவ்வாய் பாதிப்படையும் போது, ஜாதகர் வசிக்கும் வீட்டின் வடகிழக்கு மூலையில் (ஈசானிய மூலை) கழிவறை, செப்டிக் டேங்க், வெட்டுப்பட்ட பகுதி அல்லது வாஸ்து குறைபாடு இருக்கும்.",
                "case_study": "Saptarishis Examples 1-3: Toilet in NE, septic tank below bathroom, cut Ishanya entrance.",
                "remedy_en": "Keep the North-East zone extremely clean and clutter-free; place a bowl of sea salt or consecrated copper pyramid in the NE corner.",
                "remedy_ta": "வடகிழக்கு மூலையில் கனமான பொருட்களை வைக்காமல் தூய்மையாக வைத்து, அங்கு ஒரு செம்பு பாத்திரத்தில் கங்கை நீர் வைக்கவும்."
            })

    # =========================================================================
    # 6. ARDRA (திருவாதிரை)
    # =========================================================================
    ardra_planets = get_in_nak("Ardra")
    ardra_affliction = is_nak_afflicted("Ardra")

    if ardra_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Ardra",
            "name_ta": "திருவாதிரை",
            "lord": "Rahu",
            "deity": "Rudra",
            "symbol": "Teardrop / Human Head / Diamond",
            "grahas": [p["name"] for p in ardra_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in ardra_planets]
        })

        # Technique 1: Affinity / Stories with Animals
        matched_rules.append({
            "nakshatra": "Ardra",
            "technique_id": "ARDRA_T1_ANIMALS_CONNECTION",
            "category": "ANIMAL_BOND",
            "title_en": "Graha in Ardra: Karmic Bond with Animals (Pet Passion, Animal NGO, or Bite Story)",
            "title_ta": "திருவாதிரையில் கிரகம்: பிராணிகளுடன் ஆழமான பிணைப்பு & விலங்குகள் மீதான அன்பு/காயம்",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in ardra_planets],
            "details_en": "Ardra governs intense relationships with the animal kingdom: active animal welfare activism (PETA/NGOs), deeply beloved dogs/cows, or a memorable animal encounter/bite story.",
            "details_ta": "திருவாதிரை நட்சத்திரத்தில் கிரகங்கள் அமைவது பிராணிகள் மீது அளவுகடந்த அன்பையோ (நாய், பசு, விலங்கு நல அமைப்புகள்) அல்லது ஏதேனும் ஒரு மிருகத்தால் மறக்க முடியாத நிகழ்வையோ தரும்.",
            "case_study": "Pamela Anderson (PETA activist), Franklin D. Roosevelt (famous presidential dog Fala), Louise Weber (circus animal trainer).",
            "remedy_en": "Feed stray dogs on Saturdays and offer green grass/bananas to cows on Wednesdays.",
            "remedy_ta": "தெரு நாய்களுக்கு உணவளிப்பதும், பசுக்களுக்கு அகத்திக்கீரை தருவதும் மிகுந்த புண்ணியத்தை தரும்."
        })

        # Technique 2: Supreme Self-Sacrifice Theme
        matched_rules.append({
            "nakshatra": "Ardra",
            "technique_id": "ARDRA_T2_SACRIFICE_THEME",
            "category": "SOUL_SACRIFICE",
            "title_en": "Key Graha in Ardra: The Archetype of Supreme Self-Sacrifice for Others",
            "title_ta": "திருவாதிரையில் கிரகம்: பிறருக்காக தனது நலனையோ பதவியையோ தியாகம் செய்யும் மேன்மை",
            "severity": "LIFE_LESSON",
            "trigger_grahas": [p["name"] for p in ardra_planets],
            "details_en": "Ardra natives are called upon to make significant sacrifices: relinquishing power, prized jobs, or personal ambitions for the protection and well-being of family, siblings, or colleagues.",
            "details_ta": "தனக்கு கிடைக்க வேண்டிய உயர் பதவி, வேலை அல்லது வசதிகளை உடன் பிறந்தவர்களுக்காகவோ அல்லது பிறர் நன்மைக்காகவோ மனமுவந்து தியாகம் செய்யும் உன்னத குணம் வெளிப்படும்.",
            "case_study": "Sonia Gandhi (declining Prime Ministership in 2004), Lawrence Oates (Antarctic sacrifice), Pierre Brossolette.",
            "remedy_en": "Ensure healthy self-care boundaries so legitimate sacrifices do not turn into silent martyrdom.",
            "remedy_ta": "தியாகம் செய்வதோடு மட்டுமல்லாமல், உங்களின் நியாயமான உரிமைகளையும் பாதுகாத்துக் கொள்ளுங்கள்."
        })

        # Technique 3: Storms & Whistleblowers
        matched_rules.append({
            "nakshatra": "Ardra",
            "technique_id": "ARDRA_T3_STORMS_WHISTLEBLOWING",
            "category": "STORMS_EXPOSURE",
            "title_en": "Rudra's Gale: Weathering High-Profile Storms, Controversies & Whistleblowing",
            "title_ta": "ருத்ரனின் புயல்: பெரும் அரசியல்/சமூக புயல்களை எதிர்கொள்ளுதல் & உண்மைகளை வெளிக்கொணர்தல்",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in ardra_planets],
            "details_en": "Ruled by Rudra (Storm God), Ardra thrusts natives into dramatic upheavals, whistleblower roles, leaking classified truths, or surviving explosive controversies.",
            "details_ta": "ருத்ரனின் ஆதிக்கத்தால், வாழ்வில் எதிர்பாராத பெரும் புயல்கள், விவாதங்கள் மற்றும் ரகசியங்களை வெளிக்கொண்டு வந்து சமூகத்தில் அலைகளை உருவாக்கும் ஆற்றல் இருக்கும்.",
            "case_study": "Gandhi family ('Aandhi' storm motif), Julian Assange (WikiLeaks), Daniel Ellsberg, Helmut Zilk.",
            "remedy_en": "Recite Sri Rudram or Maha Rudra Japam to transform destructive turbulent energies into divine protection.",
            "remedy_ta": "ஸ்ரீ ருத்ரம் பாராயணம் செய்வது அல்லது கேட்பது சகல புயல்களிலிருந்தும் பாதுகாப்பு தரும்."
        })

    # =========================================================================
    # 7. PUNARVASU (புனர்பூசம்)
    # =========================================================================
    punarvasu_planets = get_in_nak("Punarvasu")
    punarvasu_affliction = is_nak_afflicted("Punarvasu")

    if punarvasu_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Punarvasu",
            "name_ta": "புனர்பூசம்",
            "lord": "Jupiter",
            "deity": "Aditi",
            "symbol": "Bow and Quiver of Arrows",
            "grahas": [p["name"] for p in punarvasu_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in punarvasu_planets]
        })

        # Technique 1: Fascination with Technology & Gadgets
        matched_rules.append({
            "nakshatra": "Punarvasu",
            "technique_id": "PUNARVASU_T1_TECH_FASCINATION",
            "category": "TECH_GADGETS",
            "title_en": "Punarvasu Talent: Craze for Cutting-Edge Technology, Phones & High Configurations",
            "title_ta": "புனர்பூச மேதைமை: நவீன தொழில்நுட்பம், லேட்டஸ்ட் போன்கள் மற்றும் கேஜெட்டுகள் மீதான மோகம்",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in punarvasu_planets],
            "details_en": "Deep fascination with electronic innovations, continuous smartphone/gadget upgrades, high-spec computers, and high aptitude for IT, software, or digital engineering.",
            "details_ta": "அடிக்கடி செல்போன் மாற்றுதல், லேட்டஸ்ட் தொழில்நுட்ப கேஜெட்டுகள் வாங்குதல் மற்றும் ஐ.டி, கம்ப்யூட்டர் துறைகளில் அபாரமான ஞானம் இருக்கும் அமைப்பு.",
            "case_study": "Steve Jobs (Jupiter in Punarvasu: Apple CEO/pioneer), Queen Elizabeth II (pioneered royal TV, 3D broadcast, email, podcasts).",
            "remedy_en": "Channel tech spending into productive professional tools rather than impulsive commercial upgrades.",
            "remedy_ta": "கேஜெட்டுகளின் மீது செய்யும் செலவுகளை பயனுள்ள தொழில் முன்னேற்றத்திற்கு பயன்படுத்துங்கள்."
        })

        # Technique 2: Fortune and Stability After a Lot of Searching
        matched_rules.append({
            "nakshatra": "Punarvasu",
            "technique_id": "PUNARVASU_T2_FORTUNE_AFTER_SEARCH",
            "category": "PERSISTENT_FORTUNE",
            "title_en": "Punarvasu Karma: Fortune & Settled Stability Attained After Repeated Searching",
            "title_ta": "புனர்பூச கர்ம விதி: பலமுறை தேடுதலுக்குப் பிறகே நிலையான யோகமும் வெற்றியும் கிட்டும்",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in punarvasu_planets],
            "details_en": "Punarvasu means 'return of the light' or repetition. Success rarely arrives on the first trial; it demands repeated iterations, retries, and persistence before crowning the native with enduring stability.",
            "details_ta": "புனர்பூசம் என்றால் 'மீண்டும் ஒளி பெருகுதல்' என்று பொருள். எந்த ஒரு காரியமும் முதல் முயற்சியில் அமையாமல், பலமுறை தேடி அலைந்த பிறகே அபார வெற்றியுடன் நிலைக்கும்.",
            "case_study": "Saptarishis Examples 1-3: Multiple iterations required for every project before sudden grand breakthrough.",
            "remedy_en": "Never lose heart after early setbacks; maintain cheerful optimism through the repetition cycle.",
            "remedy_ta": "ஆரம்ப தோல்விகளால் மனம் தளராமல் மீண்டும் மீண்டும் முயற்சி செய்யவும்; வெற்றி நிச்சயம்."
        })

        # Technique 3: Fitness-to-Junk Food Oscillation
        matched_rules.append({
            "nakshatra": "Punarvasu",
            "technique_id": "PUNARVASU_T3_FITNESS_JUNK_CYCLE",
            "category": "DIET_HEALTH",
            "title_en": "Punarvasu Habit: Strict Fitness Guru Phase Alternating with Voracious Junk Indulgence",
            "title_ta": "புனர்பூச உணவு சுபாவம்: தீவிர உடற்பயிற்சி/டயட் மற்றும் திடீர் ஜங்க் ஃபுட் வேட்டை",
            "severity": "BEHAVIORAL_TRAIT",
            "trigger_grahas": [p["name"] for p in punarvasu_planets],
            "details_en": "Erratic dietary rhythm: Native acts like a strict fitness freak or diet guru, highly selective of calories, but later abruptly breaks all rules to indulge voraciously in spicy street foods, fried snacks, or meat.",
            "details_ta": "டயட், ஜிம் என்று தீவிரமாக கட்டுப்பாடோடு இருந்துவிட்டு, திடீரென அனைத்து விதிகளையும் உடைத்து காரசாரமான ஜங்க் உணவுகளை விருப்பத்துடன் உண்ணும் சுபாவம் இருக்கும்.",
            "case_study": "Saptarishis Example 1 (Harsha Anapindi), Example 2 (Praveen Jain).",
            "remedy_en": "Adopt a sustainable, moderate diet rather than cycling between extreme asceticism and bingeing.",
            "remedy_ta": "கடுமையான விரதங்களுக்குப் பதில் நிதானமான சத்தான உணவை வழக்கமாக்கிக் கொள்ளவும்."
        })

        # Technique 4: The Protective Parental Figure Archetype
        matched_rules.append({
            "nakshatra": "Punarvasu",
            "technique_id": "PUNARVASU_T4_PARENT_FIGURE",
            "category": "NURTURING_ARCHETYPE",
            "title_en": "Aditi's Grace: Naturally Assuming the Mother/Father Caring Anchor Role",
            "title_ta": "அதிதியின் கருணை: குடும்பத்திற்கு தாய்/தந்தை போன்று அரவணைத்து காக்கும் தூணாக இருத்தல்",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in punarvasu_planets],
            "details_en": "Deity Aditi is the cosmic mother of gods. Natives naturally step up as the overarching maternal or paternal caretaker, fostering dependants, adopting children, and being the family's ultimate pillar of strength.",
            "details_ta": "தேவர்களின் தாயான அதிதி தேவியின் அருளால், குடும்பத்தில் இளையவராக இருந்தாலும் அனைவரையும் பெற்ற தாய்/தந்தை போன்று அரவணைத்து காக்கும் பெரும் பொறுப்பு உங்களிடம் இருக்கும்.",
            "case_study": "Angelina Jolie (Venus in Punarvasu/Pushya), Saptarishis Example 1 (caring family pillar).",
            "remedy_en": "Support orphanages or help foster children to harmonize Aditi's benevolent cosmic energy.",
            "remedy_ta": "அனாதை இல்லங்களில் உள்ள குழந்தைகளுக்கு கல்வி உதவி செய்வது பெருமகிழ்ச்சியைத் தரும்."
        })

    # =========================================================================
    # 8. PUSHYA (பூசம்)
    # =========================================================================
    pushya_planets = get_in_nak("Pushya")
    pushya_affliction = is_nak_afflicted("Pushya")

    if pushya_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Pushya",
            "name_ta": "பூசம்",
            "lord": "Saturn",
            "deity": "Brihaspati",
            "symbol": "Cow's Udder / Lotus / Arrow & Circle",
            "grahas": [p["name"] for p in pushya_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in pushya_planets]
        })

        # Technique 1: Occult, Tantra, Spells & Evil Eye Protection
        matched_rules.append({
            "nakshatra": "Pushya",
            "technique_id": "PUSHYA_T1_OCCULT_EVIL_EYE",
            "category": "OCCULT_PROTECTION",
            "title_en": "Key Graha in Pushya: Exposure to Esoteric Occult, Spells & Nazar/Evil-Eye Sensitivity",
            "title_ta": "பூசத்தில் கிரகம்: மாந்த்ரீகம், கண்ணூறு (திஷ்டி) உணர்தல் & ஆன்மீக பாதுகாப்பு தேவை",
            "severity": "CRITICAL_CAUTION" if pushya_affliction["afflicted"] else "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in pushya_planets],
            "details_en": "Connected with Brihaspati and Atharvaveda Abhicara lineage. Native may encounter occult/tantric matters, or suffer unexplained fatigue from severe evil eye (nazar) and psychic envy from associates.",
            "details_ta": "பிரகஸ்பதியின் அதர்வண வேத ஆதிக்கத்தால், எளிதில் கண் திருஷ்டி அல்லது மறைமுக எதிர்மறை அதிர்வுகளால் சோர்வடையும் நிலை உண்டாகும். திருஷ்டி கழித்தவுடன் உடல்நலம் தெளிவடையும் விநோதம் நிகழும்.",
            "case_study": "Raymond Buckland (Museum of Witchcraft), Diane Luciferia, Saptarishis Example 5.",
            "remedy_en": "Perform regular salt/lemon nazar remedies on Tuesdays; light a sesame oil lamp to Lord Bhairava.",
            "remedy_ta": "செவ்வாய்க்கிழமைகளில் திருஷ்டி கழிக்கவும்; பைரவருக்கு நல்லெண்ணெய் தீபமேற்றி வழிபடவும்."
        })

        # Technique 2: Narayana Kavacham as Master Remedy
        matched_rules.append({
            "nakshatra": "Pushya",
            "technique_id": "PUSHYA_T2_NARAYANA_KAVACH_REMEDY",
            "category": "SUPREME_REMEDY",
            "title_en": "Pushya Master Upaya: Narayana Kavacham Recitation as the Supreme Infallible Shield",
            "title_ta": "பூசத்தின் முதன்மை பரிகாரம்: ஸ்ரீ நாராயண கவசம் பாராயணம் — சர்வ ரக்ஷை & வெற்றி",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in pushya_planets],
            "details_en": "Classical and Saptarishis consensus: The single most potent, life-transforming remedy for anyone with focal planets in Pushya is daily or weekly recitation of Sri Narayana Kavacham, unlocking instant career breakthrough and impenetrable protection.",
            "details_ta": "பூசத்தில் கிரகம் உள்ளவர்களுக்கு மிகச்சிறந்த பரிகாரம் ஸ்ரீ நாராயண கவசம் ஆகும். இதை தினமும் அல்லது வியாழக்கிழமைகளில் பாராயணம் செய்ய வேலைவாய்ப்பு, தொழில் மேன்மை மற்றும் சகல பாதுகாப்பும் உடனடியாகக் கிட்டும்.",
            "case_study": "Saptarishis Example 1 (Samixa Saini): Started reciting Narayana Kavach in April 2016, landed job in July 2016.",
            "remedy_en": "Chant or listen to Sri Narayana Kavacham every Thursday morning.",
            "remedy_ta": "வியாழக்கிழமை தோறும் காலையில் ஸ்ரீ நாராயண கவசம் பாராயணம் செய்யவும்."
        })

        # Technique 3: Power Games & Workplace Politics
        matched_rules.append({
            "nakshatra": "Pushya",
            "technique_id": "PUSHYA_T3_POLITICS_MANIPULATION",
            "category": "WORKPLACE_POLITICS",
            "title_en": "Pushya Caution: Navigating Political Games, Corporate Manipulation & Envy",
            "title_ta": "பூச எச்சரிக்கை: அலுவலக அரசியல், சூழ்ச்சிகள் மற்றும் பிறரின் சூழ்ச்சிகளை வெல்லுதல்",
            "severity": "CRITICAL_CAUTION",
            "trigger_grahas": [p["name"] for p in pushya_planets],
            "details_en": "High susceptibility to being caught in corporate/political power struggles, demotions driven by administrative rivalry, or having to master diplomacy to protect one's hard-earned position.",
            "details_ta": "பணியிடத்தில் ஏற்படும் சூழ்ச்சிகள், மறைமுக அரசியல் மற்றும் பொறாமைகளை மிகவும் கவனமாகக் கையாள வேண்டும். இல்லையெனில் உங்கள் நற்பெயருக்குக் களங்கம் ஏற்படுத்த பிறர் முயற்சிப்பர்.",
            "case_study": "Dana Giacchetto, V.K. Krishna Menon, Sadie Delany, Saptarishis Example 6 demotion case.",
            "remedy_en": "Maintain meticulous official records; never disclose strategic personal moves prematurely.",
            "remedy_ta": "அலுவலகத்தில் உங்களின் அடுத்த கட்ட நகர்வுகளை முன்கூட்டியே யாரிடமும் பகிர வேண்டாம்."
        })

        # Technique 4: Foster Parenting & Adoption Themes
        matched_rules.append({
            "nakshatra": "Pushya",
            "technique_id": "PUSHYA_T4_FOSTER_PARENTING",
            "category": "FOSTER_PARENTING",
            "title_en": "Brihaspati's Lineage: Foster Parenting, Adoption & Being Nurtured by Others",
            "title_ta": "பிரகஸ்பதியின் மரபு: தத்து எடுத்தல், வளர்ப்புத் தாய்/தந்தை அல்லது பிறரால் வளர்க்கப்படுதல்",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in pushya_planets],
            "details_en": "Rooted in Brihaspati accepting Tara's child (Budha) from Moon: themes of adopting children, step-parents, raising others' children, or being brought up by affectionate non-biological guardians.",
            "details_ta": "பிரகஸ்பதி புதனை தனது மகனாக ஏற்று வளர்த்த புராண மரபின்படி, தத்துப்பிள்ளை எடுத்தல், வளர்ப்புத் தாய் அல்லது பிறர் குழந்தைகளை அன்புடன் ஆதரிக்கும் உன்னத அமைப்பு.",
            "case_study": "Madonna (raised by stepmother; built 10 schools for 4000 children), Angelina Jolie (adopted 3 children).",
            "remedy_en": "Extend patronage and scholarships to needy students and orphans.",
            "remedy_ta": "ஆதரவற்ற குழந்தைகளுக்கு கல்வி உதவித்தொகை வழங்குவது பெரும் புண்ணியத்தை சேர்க்கும்."
        })

    # =========================================================================
    # 9. ASHLESHA (ஆயில்யம்)
    # =========================================================================
    ashlesha_planets = get_in_nak("Ashlesha")
    ashlesha_affliction = is_nak_afflicted("Ashlesha")

    if ashlesha_planets:
        active_nakshatras_summary.append({
            "nakshatra": "Ashlesha",
            "name_ta": "ஆயில்யம்",
            "lord": "Mercury",
            "deity": "Sarpas / Nagas",
            "symbol": "Coiled Serpent",
            "grahas": [p["name"] for p in ashlesha_planets],
            "padas": [f"{p['name']} (P{p['pada']})" for p in ashlesha_planets]
        })

        # Technique 1: Any Planet in Ashlesha Gives Results Between Age 18 and 20
        is_past_18_20 = native_age is not None and native_age > 20
        is_cur_18_20 = native_age is not None and (18 <= native_age <= 20)
        age_milestones.append({
            "age": "18 - 20",
            "nakshatra": "Ashlesha",
            "graha": ", ".join([p["name"] for p in ashlesha_planets]),
            "status": "PAST" if is_past_18_20 else ("CURRENT" if is_cur_18_20 else "UPCOMING"),
            "event_en": "Critical destiny pivot: exams, moving away from home, first earnings, early marriage, or life direction change",
            "event_ta": "முக்கிய திருப்புமுனை: தேர்வுகள், வீட்டை விட்டு வெளியேறுதல், முதல் வருமானம் அல்லது வாழ்க்கைப் பாதை மாற்றம்",
        })

        matched_rules.append({
            "nakshatra": "Ashlesha",
            "technique_id": "ASHLESHA_T1_AGE_18_20_PIVOT",
            "category": "AGE_TRIGGER",
            "title_en": f"Any Graha in Ashlesha: Critical Life-Changing Results Between Ages 18 and 20",
            "title_ta": f"ஆயில்யத்தில் கிரகம்: 18 முதல் 20 வயதுக்குள் வாழ்க்கையின் மாபெரும் திருப்புமுனை",
            "severity": "IMPORTANT_MILESTONE",
            "trigger_grahas": [p["name"] for p in ashlesha_planets],
            "details_en": f"Empirical dictum: ANY planet placed in Ashlesha ({', '.join([p['name'] for p in ashlesha_planets])}) unfailingly produces life-defining results between ages 18 and 20 (academic shifts, leaving home, first career recognition, or radical lifestyle turns). Status: {'Already triggered during ages 18-20' if is_past_18_20 else ('CURRENTLY ACTIVE AT AGE 18-20!' if is_cur_18_20 else f'Upcoming at age 18-20 (in {18 - (native_age or 0)} years)')}.",
            "details_ta": f"ஆயில்யத்தில் உள்ள எந்தவொரு கிரகமும் 18 முதல் 20 வயதுக்குள் மிக முக்கியமான வாழ்க்கைத் திருப்புமுனையை (படிப்பு மாற்றம், வெளியூர் செல்லுதல், முதல் வருமானம் அல்லது புதிய உறவு) கட்டாயம் நிகழ்த்தும்.",
            "case_study": "Cameron Diaz (cover of Seventeen at 18), Marilyn Monroe (discovered at 18-19), Madonna (moved to NYC at 19-20), Sonia Gandhi (met Rajiv Gandhi at 18), Queen Elizabeth II (Counsellor of State at 18), Jawaharlal Nehru (Cambridge honours).",
            "remedy_en": "Channel the high serpent kundalini energy with focused meditation and academic discipline.",
            "remedy_ta": "யோகா மற்றும் தியானம் மூலம் மனதை ஒருமுகப்படுத்தி நல்வழியில் செலுத்தவும்."
        })

        # Technique 2: Gandanta Poison & The Zero-Gossip Vow
        matched_rules.append({
            "nakshatra": "Ashlesha",
            "technique_id": "ASHLESHA_T2_ZERO_GOSSIP_VOW",
            "category": "SOUL_VOW",
            "title_en": "Gandanta Sarpas Energy: The Absolute Imperative to NEVER Gossip or Speak Ill of Anyone",
            "title_ta": "ஆயில்ய சர்ப்ப தோஷம்: யாரையும் புறம்பேசக் கூடாது என்ற வாழ்நாள் விரதம்",
            "severity": "CRITICAL_CAUTION",
            "trigger_grahas": [p["name"] for p in ashlesha_planets],
            "details_en": "Sitting at the Cancer Gandanta, Ashlesha embodies intense serpent energy. The paramount soul law for anyone with planets in Ashlesha is NEVER EVER TO BITCH, GOSSIP, OR DEFAME OTHERS. Negative speech backfires a thousand times harsher upon the native, wrecking career and peace of mind.",
            "details_ta": "ஆயில்யம் கடக ராசியின் கந்தாந்தத்தில் சர்ப்பங்களின் ஆதிக்கத்தில் உள்ளது. இதன் மிக முக்கியமான ஆன்ம விதி: யாரைப் பற்றியும் புறம்பேசுவதோ, வீண் வம்பு பேசுவதோ கூடாது. புறம்பேசினால் அது ஆயிரம் மடங்கு வேகமாகத் திரும்பி ஜாதகரின் சொந்த நிம்மதியையும் தொழிலையும் நாசமாக்கும்.",
            "case_study": "Mahatma Gandhi conquered this energy; Saptarishis Example 3 (Choudhary Mallika: life flourished once gossip stopped), Example 4 (catastrophic downfall from backbiting).",
            "remedy_en": "Take a strict conscious vow of Mouna (sacred silence) regarding other people's faults; speak only truth with kindness.",
            "remedy_ta": "பிறரின் குறைகளைப் பேசாமல் அமைதி காக்கும் மௌன விரதத்தைக் கடைப்பிடிக்கவும்."
        })

        # Technique 3: Psychic Experiences & Spirit Encounters
        matched_rules.append({
            "nakshatra": "Ashlesha",
            "technique_id": "ASHLESHA_T3_PSYCHIC_INTUITION",
            "category": "PSYCHIC_GIFTS",
            "title_en": "Naga Mysticism: Powerful Sixth Sense, Spirit Encounters & Prophetic Intuition",
            "title_ta": "நாக ஞானம்: அபாரமான உள்ளுணர்வு, முன்னறிவிப்புக் கனவுகள் & ஆன்ம அனுபவங்கள்",
            "severity": "POSITIVE_TALENT",
            "trigger_grahas": [p["name"] for p in ashlesha_planets],
            "details_en": "Deep occult perception: Highly tuned intuition, telepathic instincts, seeing events in dreams before they occur, and sensing the presence of unseen spirits or ancestral energies.",
            "details_ta": "ஆயில்யம் ஆழமான மாய வித்தைகள் மற்றும் உள்ளுணர்வின் இருப்பிடம். நடப்பதை முன்கூட்டியே உணரும் ஆறாம் அறிவு, தெய்வீகக் கனவுகள் மற்றும் சூட்சும சக்திகளை உணரும் திறன் இருக்கும்.",
            "case_study": "The Amazing Kreskin (famed mentalist), Saptarishis Examples 1-5 (psychic visions, spirit awareness).",
            "remedy_en": "Worship Lord Shiva (Nagaraja) with milk abhishekam on Mondays or Nag Panchami.",
            "remedy_ta": "திங்கட்கிழமைகளில் சிவபெருமானுக்கும் நாகராஜருக்கும் பால் அபிஷேகம் செய்து வழிபடவும்."
        })

        # Technique 4: Reputational Warfare (if afflicted)
        if ashlesha_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Ashlesha",
                "technique_id": "ASHLESHA_T4_REPUTATION_WARFARE",
                "category": "REPUTATION_RISK",
                "title_en": "Afflicted Ashlesha: Reputational Warfare & Defamation Combat",
                "title_ta": "பாதிக்கப்பட்ட ஆயில்யம்: நற்பெயருக்கு ஆபத்து & எதிரிகளை வீழ்த்தும் வீரியம்",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [p["name"] for p in ashlesha_planets],
                "details_en": "Under affliction, the native will either cause the downfall of their rivals' reputations or find themselves the target of vicious character assassination and smear campaigns.",
                "details_ta": "ஆயில்யத்தில் அசுப கிரகங்கள் இணையும்போது, எதிரிகளின் நற்பெயரை தகர்க்கும் அல்லது பிறரால் தங்கள் நற்பெயருக்கு வீண் களங்கம் ஏற்படும் சவால்கள் உருவாகும்.",
                "case_study": "Julian Assange (leaking emails ruining rivals' careers), Saptarishis Example 5.",
                "remedy_en": "Refrain from seeking personal vengeance; allow natural cosmic justice (Karmic law) to handle detractors.",
                "remedy_ta": "பழிவாங்கும் எண்ணத்தைக் கைவிட்டு தர்மத்தின் வழியில் காரியங்களை மேற்கொள்ளவும்."
            })

        # Technique 5: Plastic Surgery Metamorphosis
        for p in ashlesha_planets:
            p_name = p["name"]
            h_owned = p["houses_owned"]
            h_pos = p["house"]
            matched_rules.append({
                "nakshatra": "Ashlesha",
                "technique_id": f"ASHLESHA_T5_PLASTIC_SURGERY_{p_name.upper()}",
                "category": "METAMORPHOSIS",
                "title_en": f"Ashlesha 'Plastic Surgery': Radical Transformation in House {h_pos} Portfolios ({p_name})",
                "title_ta": f"ஆயில்யத்தின் 'பிளாஸ்டிக் சர்ஜரி': {h_pos}-ம் பாவகத்தில் முந்தைய அடையாளம் தெரியாத பெரும் மாற்றம்",
                "severity": "IMPORTANT_MILESTONE",
                "trigger_grahas": [p_name],
                "details_en": f"Known as the 'Plastic Surgery of Nakshatras', Ashlesha produces a total metamorphosis in the house where {p_name} sits (House {h_pos}) or rules ({h_owned}): health, career, or lifestyle changes so radically from good to bad or bad to good that previous patterns become unrecognizable.",
                "details_ta": f"ஆயில்யம் 'ஜோதிட பிளாஸ்டிக் சர்ஜரி' என்று அழைக்கப்படுகிறது. {p_name} அமர்ந்த {h_pos}-ம் பாவகமும் அதன் காரகங்களும் முற்றிலுமாக உருமாறும். முந்தைய அடையாளமே தெரியாத அளவிற்கு புதிய பரிணாமம் உண்டாகும்.",
                "case_study": "Sanjay Rath (Sun in Ashlesha 6L: resigned govt post to revolutionize Jyotish), Saptarishis Examples 1-8.",
                "remedy_en": "Embrace life shedding like a serpent shedding old skin; surrender to spiritual rebirth.",
                "remedy_ta": "பாம்பு தனது சட்டையைக் கழற்றுவது போல பழைய பழக்கங்களை விட்டு புதிய மனிதராக உருவெடுக்கவும்."
            })

        # Technique 6: Sexual Imbalance Warnings (Venus / Mars in Ashlesha)
        sexual_grahas = [p for p in ashlesha_planets if p["name"] in ("Venus", "Mars")]
        if sexual_grahas and ashlesha_affliction["afflicted"]:
            matched_rules.append({
                "nakshatra": "Ashlesha",
                "technique_id": "ASHLESHA_T6_SEXUAL_BALANCE",
                "category": "RELATIONSHIP_CAUTION",
                "title_en": f"Afflicted {', '.join([p['name'] for p in sexual_grahas])} in Ashlesha: Sensual Restraint & Relationship Sanctity",
                "title_ta": f"ஆயில்யத்தில் பாதிக்கப்பட்ட {', '.join([p['name'] for p in sexual_grahas])}: காம உணர்வுகளில் நிதானம்",
                "severity": "CRITICAL_CAUTION",
                "trigger_grahas": [p["name"] for p in sexual_grahas],
                "details_en": "Venus or Mars afflicted in Ashlesha can destabilize sensual balance, prompting reckless desires, bed pleasure controversies, or scandalous relationships.",
                "details_ta": "ஆயில்யத்தில் சுக்கிரன் அல்லது செவ்வாய் பாதிப்படைந்தால், உணர்ச்சி வேகங்கள் கட்டுக்கடங்காமல் போகவோ அல்லது ஒழுக்கக் குறைபாடுகளால் அவப்பெயர் ஏற்படவோ வாய்ப்புண்டு. சுய ஒழுக்கம் மிக அவசியம்.",
                "case_study": "Michael Jackson (Venus in Ashlesha 6H aspected by Mars), Marilyn Monroe, Indira Gandhi affairs.",
                "remedy_en": "Channel high passionate prana into creative arts, athletics, or spiritual devotion; maintain spotless fidelity.",
                "remedy_ta": "காம சக்தியை கலை, உடற்பயிற்சி அல்லது இறை வழிபாட்டில் திருப்பி ஆத்ம பலம் பெறவும்."
            })

    # Summary synthesis
    crit_count = sum(1 for r in matched_rules if r["severity"] == "CRITICAL_CAUTION")
    milestone_count = sum(1 for r in matched_rules if r["severity"] == "IMPORTANT_MILESTONE")
    lesson_count = sum(1 for r in matched_rules if r["severity"] == "LIFE_LESSON")

    summary_en = (
        f"In-depth Nakshatra Shastra analysis detected {len(matched_rules)} active empirical rules across your chart. "
        f"Highlights include {crit_count} vital safety/conduct cautions, {milestone_count} significant age and career milestones, "
        f"and {lesson_count} foundational soul lessons derived from Saptarishis research."
    )
    summary_ta = (
        f"உங்கள் ஜாதகத்தில் {len(matched_rules)} முக்கிய நட்சத்திர விதிகள் கண்டறியப்பட்டுள்ளன. "
        f"அதில் {crit_count} விசேஷ எச்சரிக்கைகள், {milestone_count} வயது மற்றும் தொழில் திருப்புமுனைகள், "
        f"மற்றும் {lesson_count} ஆன்ம பரிணாமப் பாடங்கள் உள்ளன."
    )

    return {
        "valid": True,
        "analyzed_at": datetime.now().isoformat(),
        "native_age": native_age,
        "active_nakshatras_summary": active_nakshatras_summary,
        "total_rules_matched": len(matched_rules),
        "critical_cautions_count": crit_count,
        "milestones_count": milestone_count,
        "soul_lessons_count": lesson_count,
        "summary_en": summary_en,
        "summary_ta": summary_ta,
        "matched_rules": matched_rules,
        "age_milestones": age_milestones,
        "vastu_advisories": vastu_advisories,
        "body_part_alerts": body_part_alerts,
    }
