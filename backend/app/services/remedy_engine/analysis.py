"""Vedic Astrological Remedy Analysis Engine.

Consumes existing calculation outputs (without recalculating ephemeris):
1. Chart Context Extraction: Extracts Ascendant, Moon/Rasi, Nakshatra,
   planetary states (debilitation, combustion, dusthanas), and running Dasa-Bhukti.
2. Classical Diagnostic Rules:
   - Debilitated planets (with Neechabhanga checking)
   - Combust planets (within classical solar orbs)
   - Dusthana (6th, 8th, 12th) afflictions
   - Kuja Dosha (Manglik) with verified BPHS cancellation exceptions
   - Active Mahadasha & Antardasha lord afflictions
   - Rahu-Ketu karmic axis placements
3. Yogakaraka Protection Safeguard (BPHS Ch. 34): Strict prohibition of Daan/charity
   for Yogakarakas, providing safe Sattvic alternatives (Gayatri/Stotra Japa & Temples).
4. Deterministic Ranking: Scores and prioritizes remedies according to active Dasa and chart need.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple

from app.schemas.remedies import (
    ChartFactorExplanation,
    RecommendedRemedy,
    ChartContextSummary,
    RemedyAnalysisResponse,
    RemedyItem,
    NavagrahaTempleItem,
    NeechaBhangaAssessment,
)
from app.services.remedy_engine.eligibility import (
    LAGNA_PLANETARY_NATURE,
    PLANET_CANONICAL_NAMES,
    RemedyEligibilityEngine,
)
from app.services.remedy_engine.repository import (
    remedy_repository,
    VERIFIED_TEMPLES,
    VERIFIED_REMEDIES,
)
from app.services.varga_engine import calculate_navamsa_from_longitude

# Standard Zodiac Sign Numbers (1 = Aries to 12 = Pisces)
SIGN_NUMBERS: Dict[str, int] = {
    "aries": 1,
    "taurus": 2,
    "gemini": 3,
    "cancer": 4,
    "leo": 5,
    "virgo": 6,
    "libra": 7,
    "scorpio": 8,
    "sagittarius": 9,
    "capricorn": 10,
    "aquarius": 11,
    "pisces": 12,
}

SIGN_NAMES_BY_NUM: Dict[int, str] = {v: k for k, v in SIGN_NUMBERS.items()}

# Sign Lords
SIGN_LORDS: Dict[str, str] = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

# Exaltation & Debilitation Signs
EXALTATION_SIGNS: Dict[str, str] = {
    "sun": "aries",
    "moon": "taurus",
    "mars": "capricorn",
    "mercury": "virgo",
    "jupiter": "cancer",
    "venus": "pisces",
    "saturn": "libra",
    "rahu": "taurus",
    "ketu": "scorpio",
}

DEBILITATION_SIGNS: Dict[str, str] = {
    "sun": "libra",
    "moon": "scorpio",
    "mars": "cancer",
    "mercury": "pisces",
    "jupiter": "capricorn",
    "venus": "virgo",
    "saturn": "aries",
    "rahu": "scorpio",
    "ketu": "taurus",
}

# Classical Combustion Orbs from Sun (Degrees)
COMBUSTION_ORBS: Dict[str, float] = {
    "moon": 12.0,
    "mars": 17.0,
    "mercury": 14.0,  # 12.0 if retrograde
    "jupiter": 11.0,
    "venus": 10.0,    # 8.0 if retrograde
    "saturn": 15.0,
}


def _norm(name: Optional[str]) -> str:
    """Normalize sign or planet string."""
    if not name:
        return ""
    return str(name).strip().lower()


def compute_input_fingerprint(data: Any) -> str:
    """Deterministic hash of chart inputs or payload to detect staleness."""
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def evaluate_neecha_bhanga(
    deb_planet: str,
    lagna_sign: str,
    planets_dict: Dict[str, Dict[str, Any]],
    d9_signs: Dict[str, Optional[str]],
    combust_planets: Set[str],
    yogakaraka_planets: Set[str],
    running_mahadasha: Optional[str] = None,
) -> NeechaBhangaAssessment:
    """Evaluates classical Neecha Bhanga cancellation factors and distinguishes cancellation indicators
    from complete Neecha Bhanga Raja Yoga (NBRY) per Phaladeepika Ch. 6, BPHS Ch. 34 & 39, and Jataka Parijata Ch. 7.
    """
    p_canonical = PLANET_CANONICAL_NAMES.get(deb_planet, deb_planet.capitalize())
    p_info = planets_dict.get(deb_planet) or {}
    d1_sign = _norm(p_info.get("sign") or p_info.get("rasi") or DEBILITATION_SIGNS.get(deb_planet, ""))
    d1_house = p_info.get("house")
    is_d1_deb = (d1_sign == DEBILITATION_SIGNS.get(deb_planet))

    # 1. D9 Navamsa placements
    d9_sign_val = d9_signs.get(deb_planet)
    if d9_sign_val:
        d9_sign = _norm(d9_sign_val)
        d9_data_status = "verified"
        own_ex_sign = EXALTATION_SIGNS.get(deb_planet)
        is_d9_exalted = (d9_sign == own_ex_sign)
        is_d9_own_sign = (SIGN_LORDS.get(d9_sign) == deb_planet)
        is_vargottama = (d1_sign == d9_sign)
    else:
        d9_sign = None
        d9_data_status = "unavailable"
        is_d9_exalted = False
        is_d9_own_sign = False
        is_vargottama = False

    # Moon info for counting from Moon
    moon_info = planets_dict.get("moon") or {}
    moon_house = moon_info.get("house")

    def in_kendra_lagna(h: Optional[int]) -> bool:
        return h in (1, 4, 7, 10) if h is not None else False

    def in_kendra_moon(h: Optional[int], planet_name: Optional[str] = None) -> bool:
        if h is None or moon_house is None:
            return False
        # Moon cannot be in Kendra from itself; when evaluating Moon, it must be in Kendra from Lagna
        if planet_name == "moon":
            return False
        return ((h - moon_house) % 12 + 1) in (1, 4, 7, 10)

    # Dispositor of debilitated sign
    dispositor = SIGN_LORDS.get(d1_sign)
    disp_info = planets_dict.get(dispositor) or {} if dispositor else {}
    disp_house = disp_info.get("house")

    # Ruler of exaltation sign of debilitated planet
    own_ex_sign = EXALTATION_SIGNS.get(deb_planet)
    own_ex_lord = SIGN_LORDS.get(own_ex_sign) if own_ex_sign else None
    own_ex_lord_info = planets_dict.get(own_ex_lord) or {} if own_ex_lord else {}
    own_ex_lord_house = own_ex_lord_info.get("house")

    # Planet that exalts in the debilitation sign
    exalt_in_deb_sign = next((p for p, ex_s in EXALTATION_SIGNS.items() if ex_s == d1_sign), None)
    exalt_in_deb_info = planets_dict.get(exalt_in_deb_sign) or {} if exalt_in_deb_sign else {}
    exalt_in_deb_house = exalt_in_deb_info.get("house")

    qualifying_criteria: List[str] = []
    rule_identifiers: List[str] = []
    supporting_placements: Dict[str, Any] = {
        "d1_sign": d1_sign.capitalize() if d1_sign else None,
        "d1_house": d1_house,
        "d9_sign": d9_sign.capitalize() if d9_sign else None,
        "dispositor": dispositor.capitalize() if dispositor else None,
        "dispositor_house": disp_house,
        "exaltation_sign_ruler": own_ex_lord.capitalize() if own_ex_lord else None,
        "exaltation_sign_ruler_house": own_ex_lord_house,
    }

    # CRITERION D9-1: Exalted in Navamsha (Ucca Navamsha)
    if is_d9_exalted:
        qualifying_criteria.append(f"{p_canonical} is exalted in Navamsha D9 ({d9_sign.capitalize()})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 29; Jataka Parijata Ch. 7, v. 16")

    # CRITERION D9-2: Own Sign in Navamsha (Sva Navamsha)
    if is_d9_own_sign:
        qualifying_criteria.append(f"{p_canonical} occupies own sign in Navamsha D9 ({d9_sign.capitalize()})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 29; Saravali Ch. 26")

    # CRITERION D9-3: Vargottama in Debilitation Sign
    if is_vargottama:
        qualifying_criteria.append(f"{p_canonical} is Vargottama in {d1_sign.capitalize()} (identical sign in D1 and D9)")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 29; BPHS Ch. 6")

    # CRITERION D1-1: Dispositor of debilitated sign is in Kendra from Lagna or Moon
    disp_k_lagna = in_kendra_lagna(disp_house)
    disp_k_moon = in_kendra_moon(disp_house, dispositor)
    if disp_house and (disp_k_lagna or disp_k_moon):
        from_ref = "Lagna & Moon" if (disp_k_lagna and disp_k_moon) else ("Lagna" if disp_k_lagna else "Moon")
        qualifying_criteria.append(f"Dispositor {dispositor.capitalize()} in Kendra from {from_ref} (House {disp_house})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 26; BPHS Ch. 39")

    # CRITERION D1-2: Lord of exaltation sign is in Kendra from Lagna or Moon
    ex_lord_k_lagna = in_kendra_lagna(own_ex_lord_house)
    ex_lord_k_moon = in_kendra_moon(own_ex_lord_house, own_ex_lord)
    if own_ex_lord_house and (ex_lord_k_lagna or ex_lord_k_moon):
        from_ref = "Lagna & Moon" if (ex_lord_k_lagna and ex_lord_k_moon) else ("Lagna" if ex_lord_k_lagna else "Moon")
        qualifying_criteria.append(f"Exaltation sign ruler {own_ex_lord.capitalize()} in Kendra from {from_ref} (House {own_ex_lord_house})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 26; BPHS Ch. 39")

    # CRITERION D1-3: Planet exalting in debilitation sign is in Kendra from Lagna or Moon
    deb_ex_k_lagna = in_kendra_lagna(exalt_in_deb_house)
    deb_ex_k_moon = in_kendra_moon(exalt_in_deb_house, exalt_in_deb_sign)
    if exalt_in_deb_house and (deb_ex_k_lagna or deb_ex_k_moon):
        qualifying_criteria.append(f"Planet exalting in {d1_sign.capitalize()} ({exalt_in_deb_sign.capitalize()}) is in Kendra (House {exalt_in_deb_house})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 27")

    # CRITERION D1-4: Debilitated planet itself in Kendra from Lagna or Moon
    deb_k_lagna = in_kendra_lagna(d1_house)
    deb_k_moon = in_kendra_moon(d1_house, deb_planet)
    if d1_house and (deb_k_lagna or deb_k_moon):
        qualifying_criteria.append(f"{p_canonical} itself occupies a Kendra house (House {d1_house})")
        rule_identifiers.append("Phaladeepika Ch. 6, v. 27; Mansagari")

    # CRITERION D1-5: Dispositor directly aspects debilitated planet
    if disp_house and d1_house:
        aspects = False
        dist = (d1_house - disp_house) % 12
        if dist == 6:  # 7th aspect
            aspects = True
        elif dispositor == "mars" and dist in (3, 7):
            aspects = True
        elif dispositor == "jupiter" and dist in (4, 8):
            aspects = True
        elif dispositor == "saturn" and dist in (2, 9):
            aspects = True
        if aspects:
            qualifying_criteria.append(f"Dispositor {dispositor.capitalize()} (House {disp_house}) directly aspects {p_canonical} (House {d1_house})")
            rule_identifiers.append("Phaladeepika Ch. 6, v. 28")

    # Deduplicate rule identifiers
    dedup_rules = list(dict.fromkeys(rule_identifiers))
    has_indicator = len(qualifying_criteria) > 0
    is_combust = deb_planet in combust_planets
    is_yogakaraka = deb_planet in yogakaraka_planets
    is_running_dasa = (deb_planet == _norm(running_mahadasha))

    # Synthesis & Decision Engine
    if not has_indicator:
        if d9_data_status == "unavailable":
            cancellation_status = "insufficient_data"
            is_complete_nbry = False
            confidence_status = "conditional"
            unresolved = "True D9 Navamsa placements were unavailable in chart data; cancellation evaluation reflects D1 placements only."
            severity = "high" if (is_yogakaraka or is_running_dasa) else "moderate"
            reason_en = (
                f"{p_canonical} is debilitated in D1 ({d1_sign.capitalize()}). True D9 Navamsa placements were unavailable "
                "in the input data to assess Navamsa exaltation, own-sign, or Vargottama dignity. No D1 cancellation rules were met."
            )
            reason_ta = (
                f"{p_canonical} D1 ராசியில் ({d1_sign}) நீசமடைந்துள்ளார். நவாம்ச (D9) தரவு கிடைக்கப்பெறாததால் நவாம்ச பலம் மதிப்பீடு செய்யப்படவில்லை. "
                "D1 விதிகளின்படி நீச பங்கம் உறுதி செய்யப்படவில்லை; சாஸ்திர பரிகாரங்கள் தேவை."
            )
        else:
            cancellation_status = "none"
            is_complete_nbry = False
            confidence_status = "high"
            unresolved = None
            severity = "high" if (is_yogakaraka or is_running_dasa) else "moderate"
            reason_en = (
                f"{p_canonical} is debilitated in {d1_sign.capitalize()} without any classical cancellation factors satisfied in D1 or D9 Navamsa. "
                "Dedicated remedial propitiation is recommended to alleviate functional weaknesses."
            )
            reason_ta = (
                f"{p_canonical} {d1_sign} ராசியில் நீசமடைந்துள்ளார்; D1 அல்லது D9 நவாம்சத்தில் எந்த ஒரு சாஸ்திர நீச பங்க விதிகளும் பொருந்தவில்லை. "
                "பாதிப்புகளைத் தணிக்க உரிய சாஸ்திர பரிகாரங்கள் அவசியம்."
            )
    else:
        # One or more cancellation indicators are present
        if is_combust:
            cancellation_status = "nbry_neutralized_by_combustion"
            is_complete_nbry = False
            confidence_status = "high"
            unresolved = f"Solar combustion (Astangata) neutralizes the outward Raja Yoga manifestation of {p_canonical} per Phaladeepika Ch. 6."
            severity = "high" if (is_yogakaraka or is_running_dasa) else "moderate"
            criteria_str = "; ".join(qualifying_criteria)
            reason_en = (
                f"Neecha Bhanga cancellation indicator is present ({criteria_str}), but full Neecha Bhanga Raja Yoga is "
                f"neutralized by solar combustion (Astangata) per Phaladeepika Ch. 6. Remedies to propitiate Surya and {p_canonical} are recommended."
            )
            reason_ta = (
                f"நீச பங்க விதி அமைந்திருந்தாலும் ({criteria_str}), {p_canonical} சூரியனுடன் அஸ்தமனம் ஆகியுள்ளதால் ராஜ யோக பலன் தடைபடுகிறது "
                "(பலதீபிகை அத்தியாயம் 6). சூரியன் மற்றும் {p_canonical} வழிபாடுகள் தேவை."
            )
        else:
            # Check if placement qualifies for Complete NBRY
            is_well_placed = (
                (d1_house in (1, 4, 7, 10, 5, 9))
                or (disp_house in (1, 4, 7, 10, 5, 9))
                or is_d9_exalted
                or is_d9_own_sign
            )
            if is_well_placed:
                cancellation_status = "complete_nbry_qualifying"
                is_complete_nbry = True
                confidence_status = "high"
                unresolved = None
                if is_vargottama and not (is_d9_exalted or is_d9_own_sign):
                    unresolved = "Vargottama in debility confers enduring internal resilience, but causes initial psychological friction before manifesting success."

                # Documented severity decision rule:
                if is_running_dasa:
                    severity = "moderate"  # Classical rule: initial hurdles during active Dasa before success
                elif is_yogakaraka:
                    severity = "moderate"  # Yogakaraka requires attentive Sattvic strengthening
                else:
                    severity = "mild"      # Complete cancellation transforms debility into strength

                criteria_str = "; ".join(qualifying_criteria)
                reason_en = (
                    f"Full Neecha Bhanga Raja Yoga is confirmed ({criteria_str}). Initial delays or struggle are transformed into "
                    f"phenomenal resilience, authority, and eventual triumph per Phaladeepika Ch. 6 and BPHS Ch. 39."
                )
                reason_ta = (
                    f"முழுமையான நீச பங்க ராஜ யோகம் உறுதி செய்யப்பட்டுள்ளது ({criteria_str}). ஆரம்பக்கால தடைகள் நீங்கி, "
                    "அபரிமிதமான விடாமுயற்சி, கௌரவம் மற்றும் வெற்றி கிட்டும் (பலதீபிகை அத்தியாயம் 6 & பராசர ஹோரா சாஸ்திரம்)."
                )
            else:
                # In Dusthana (6, 8, 12) without Kendra dispositor
                cancellation_status = "cancellation_indicator_present"
                is_complete_nbry = False
                confidence_status = "medium"
                unresolved = f"{p_canonical} occupies Dusthana House {d1_house}, which constrains complete Raja Yoga manifestation."
                severity = "moderate"
                criteria_str = "; ".join(qualifying_criteria)
                reason_en = (
                    f"Neecha Bhanga cancellation indicator is present ({criteria_str}), but {p_canonical} is situated in "
                    f"Dusthana House {d1_house}, preventing full unhindered Raja Yoga results. Moderate remedial worship is recommended."
                )
                reason_ta = (
                    f"நீச பங்க விதி பொருந்துகிறது ({criteria_str}), ஆனால் கிரகம் மறைவு ஸ்தானமான {d1_house}-ஆம் இடத்தில் இருப்பதால் "
                    "முழுமையான ராஜ யோகமாக அமையவில்லை. மிதமான சாஸ்திர வழிபாடுகள் நலம் தரும்."
                )

    return NeechaBhangaAssessment(
        graha=deb_planet,
        d1_sign=d1_sign.capitalize() if d1_sign else "",
        d1_house=d1_house,
        is_d1_debilitated=is_d1_deb,
        d9_data_status=d9_data_status,
        d9_sign=d9_sign.capitalize() if d9_sign else None,
        d9_house=None,
        is_d9_exalted=is_d9_exalted,
        is_d9_own_sign=is_d9_own_sign,
        is_vargottama=is_vargottama,
        cancellation_status=cancellation_status,
        has_cancellation_indicator=has_indicator,
        is_complete_nbry=is_complete_nbry,
        is_combust=is_combust,
        qualifying_criteria=qualifying_criteria,
        rule_identifiers=dedup_rules,
        severity=severity,
        reason_en=reason_en,
        reason_ta=reason_ta,
        supporting_placements=supporting_placements,
        confidence_status=confidence_status,
        unresolved_interpretation=unresolved,
    )


def extract_chart_context(
    chart_data: Dict[str, Any],
    dasa_data: Optional[Dict[str, Any]] = None,
) -> ChartContextSummary:
    """Extract natal chart context without recalculating astronomical positions."""
    # 1. Ascendant / Lagna
    asc = chart_data.get("ascendant") or {}
    lagna_sign = _norm(asc.get("sign") or asc.get("rasi") or "aries")
    lagna_lord = SIGN_LORDS.get(lagna_sign)

    # 2. Functional Nature from Parashari tables
    lagna_info = LAGNA_PLANETARY_NATURE.get(lagna_sign) or {
        "yogakaraka": None,
        "benefics": set(),
        "malefics": set(),
    }
    yogakaraka = lagna_info.get("yogakaraka")
    yogakarakas = [yogakaraka] if yogakaraka else []
    functional_benefics = sorted(list(lagna_info.get("benefics") or []))
    functional_malefics = sorted(list(lagna_info.get("malefics") or []))

    # 3. Parse Planets
    planets_dict: Dict[str, Dict[str, Any]] = {}
    planets_raw = chart_data.get("planets") or []
    if isinstance(planets_raw, list):
        for p in planets_raw:
            p_name = _norm(p.get("name") or p.get("planet"))
            if p_name:
                planets_dict[p_name] = p
    elif isinstance(planets_raw, dict):
        for k, v in planets_raw.items():
            planets_dict[_norm(k)] = v

    # Extract Sun & Moon
    sun_info = planets_dict.get("sun") or {}
    moon_info = planets_dict.get("moon") or {}
    sun_sign = _norm(sun_info.get("sign") or sun_info.get("rasi") or "aries")
    moon_sign = _norm(moon_info.get("sign") or moon_info.get("rasi") or "aries")

    # Moon Nakshatra
    panchang = chart_data.get("panchang") or {}
    moon_nak = (
        moon_info.get("nakshatra")
        or panchang.get("nakshatra")
        or panchang.get("nakshatra_name")
        or "Ashwini"
    )

    # 4. Debilitation, Exaltation & Combustion
    debilitated: List[str] = []
    exalted: List[str] = []
    combust: List[str] = []
    dusthanas: Dict[str, List[str]] = {"6": [], "8": [], "12": []}

    sun_long = float(sun_info.get("longitude", 0.0))

    for p_name, p_data in planets_dict.items():
        if p_name in ("uranus", "neptune", "pluto"):
            continue

        p_sign = _norm(p_data.get("sign") or p_data.get("rasi"))
        p_house = p_data.get("house")

        # Exaltation / Debilitation
        if p_sign == DEBILITATION_SIGNS.get(p_name):
            debilitated.append(p_name)
        elif p_sign == EXALTATION_SIGNS.get(p_name):
            exalted.append(p_name)

        # Combustion (exclude Sun, Rahu, Ketu)
        if p_name not in ("sun", "rahu", "ketu") and "longitude" in p_data and "longitude" in sun_info:
            p_long = float(p_data.get("longitude", 0.0))
            diff = abs(p_long - sun_long)
            if diff > 180.0:
                diff = 360.0 - diff

            orb_limit = COMBUSTION_ORBS.get(p_name, 12.0)
            if p_data.get("is_retrograde") and p_name in ("mercury", "venus"):
                orb_limit -= 2.0  # Slightly tighter orb for retrograde inferior planets

            if diff <= orb_limit or p_data.get("is_combust"):
                combust.append(p_name)

        # Dusthana placements (6th, 8th, 12th houses from Lagna)
        if p_house in (6, 8, 12):
            dusthanas[str(p_house)].append(p_name)

    # 5. Extract or Compute D9 Navamsa placements
    d9_signs: Dict[str, Optional[str]] = {}
    vargottama_planets: List[str] = []
    has_d9_source = False

    # Priority 1: Check varga_d1_d9 in chart_data
    varga_data = chart_data.get("varga_d1_d9") or chart_data.get("varga") or {}
    varga_planets = varga_data.get("planets") or []
    if varga_planets and isinstance(varga_planets, list):
        for vp in varga_planets:
            vp_name = _norm(vp.get("name") if isinstance(vp, dict) else getattr(vp, "name", None))
            d9_s = _norm(vp.get("d9_sign_name") if isinstance(vp, dict) else getattr(vp, "d9_sign_name", None))
            if vp_name and d9_s:
                d9_signs[vp_name] = d9_s
                has_d9_source = True
                is_v = vp.get("is_vargottama") if isinstance(vp, dict) else getattr(vp, "is_vargottama", False)
                if is_v and vp_name not in vargottama_planets:
                    vargottama_planets.append(vp_name)

    # Priority 2: Check per-planet d9_sign / navamsa_sign or compute from longitude
    for p_name, p_data in planets_dict.items():
        if p_name in ("uranus", "neptune", "pluto"):
            continue
        p_d1_sign = _norm(p_data.get("sign") or p_data.get("rasi"))
        if p_name not in d9_signs:
            d9_explicit = (
                p_data.get("d9_sign")
                or p_data.get("d9_sign_name")
                or p_data.get("navamsa_sign")
                or p_data.get("navamsa")
            )
            if d9_explicit:
                d9_s = _norm(d9_explicit)
                d9_signs[p_name] = d9_s
                has_d9_source = True
                if p_d1_sign and p_d1_sign == d9_s and p_name not in vargottama_planets:
                    vargottama_planets.append(p_name)
            elif "longitude" in p_data and p_data.get("longitude") is not None:
                try:
                    p_lon = float(p_data["longitude"])
                    nav_calc = calculate_navamsa_from_longitude(p_lon)
                    d9_s = _norm(nav_calc["d9_sign_name"])
                    d9_signs[p_name] = d9_s
                    has_d9_source = True
                    if nav_calc.get("is_vargottama") and p_name not in vargottama_planets:
                        vargottama_planets.append(p_name)
                except Exception:
                    pass

    # Status of D9 data
    if has_d9_source and len(d9_signs) >= 7:
        d9_data_status = "verified"
    elif has_d9_source and len(d9_signs) > 0:
        d9_data_status = "partial"
    else:
        d9_data_status = "unavailable"

    # 6. Kuja Dosha (Manglik) Analysis with Classical Exceptions (BPHS Ch. 81)
    mars_info = planets_dict.get("mars")
    kuja_status = "none"
    kuja_details: Optional[str] = None

    if mars_info:
        mars_house = mars_info.get("house")
        mars_sign = _norm(mars_info.get("sign") or mars_info.get("rasi"))
        jupiter_info = planets_dict.get("jupiter")

        # Kuja dosha occurs when Mars is in 1st, 2nd, 4th, 7th, 8th, or 12th house
        if mars_house in (1, 2, 4, 7, 8, 12):
            cancellations = []
            if mars_sign == "aries" and mars_house == 1:
                cancellations.append("Mars in own sign (Aries) in 1st house cancels Kuja Dosha")
            elif mars_sign == "scorpio" and mars_house == 4:
                cancellations.append("Mars in own sign (Scorpio) in 4th house cancels Kuja Dosha")
            elif mars_sign == "capricorn" and mars_house in (7, 8):
                cancellations.append("Mars in exaltation sign (Capricorn) in 7th/8th house cancels Kuja Dosha")
            elif lagna_sign in ("cancer", "leo"):
                cancellations.append(f"Mars is Yogakaraka for {lagna_sign.capitalize()} Lagna, neutralizing Kuja Dosha")

            # Jupiter aspect or conjunction
            if jupiter_info:
                jup_house = jupiter_info.get("house")
                if jup_house == mars_house:
                    cancellations.append("Mars conjunct Jupiter cancels Kuja Dosha")
                elif jup_house is not None and mars_house is not None:
                    aspect_dist = (mars_house - jup_house) % 12
                    if aspect_dist in (7, 5, 9):
                        cancellations.append("Auspicious aspect of Jupiter onto Mars neutralizes Kuja Dosha")

            if cancellations:
                kuja_status = "cancelled"
                kuja_details = "; ".join(cancellations)
            else:
                kuja_status = "present"
                kuja_details = (
                    f"Mars occupies the {mars_house}th house in {mars_sign.capitalize()} from Lagna, "
                    "forming un-cancelled Kuja Dosha impacting marriage, emotional temperament, and domestic harmony."
                )

    # 7. Running Vimshottari Dasa / Bhukti
    running_mahadasha = None
    running_bhukti = None
    if dasa_data:
        active_period = (
            dasa_data.get("active_period")
            or dasa_data.get("current_period")
            or dasa_data.get("running_period")
        )
        if active_period:
            running_mahadasha = _norm(active_period.get("mahadasha") or active_period.get("lord"))
            running_bhukti = _norm(active_period.get("antardasha") or active_period.get("bhukti"))
        elif "mahadasha" in dasa_data:
            running_mahadasha = _norm(dasa_data.get("mahadasha"))
            running_bhukti = _norm(dasa_data.get("bhukti") or dasa_data.get("antardasha"))

    # 8. Evaluate Neecha Bhanga for all debilitated planets
    combust_set = set(combust)
    yogakaraka_set = set(yogakarakas)
    neecha_assessments: List[NeechaBhangaAssessment] = []
    for deb_p in debilitated:
        nb_assessment = evaluate_neecha_bhanga(
            deb_planet=deb_p,
            lagna_sign=lagna_sign,
            planets_dict=planets_dict,
            d9_signs=d9_signs,
            combust_planets=combust_set,
            yogakaraka_planets=yogakaraka_set,
            running_mahadasha=running_mahadasha,
        )
        neecha_assessments.append(nb_assessment)

    d9_clean_map = {k: v.capitalize() for k, v in d9_signs.items() if v}

    return ChartContextSummary(
        lagna_sign=lagna_sign.capitalize(),
        lagna_lord=lagna_lord.capitalize() if lagna_lord else None,
        moon_sign=moon_sign.capitalize(),
        moon_nakshatra=str(moon_nak),
        sun_sign=sun_sign.capitalize(),
        running_mahadasha=running_mahadasha.capitalize() if running_mahadasha else None,
        running_bhukti=running_bhukti.capitalize() if running_bhukti else None,
        yogakaraka_planets=yogakarakas,
        functional_benefics=functional_benefics,
        functional_malefics=functional_malefics,
        combust_planets=combust,
        debilitated_planets=debilitated,
        exalted_planets=exalted,
        dusthana_planets=dusthanas,
        kuja_dosha_status=kuja_status,
        kuja_dosha_details=kuja_details,
        d9_data_status=d9_data_status,
        d9_planetary_signs=d9_clean_map,
        vargottama_planets=[p.capitalize() for p in vargottama_planets],
        neecha_bhanga_assessments=neecha_assessments,
    )


def diagnose_chart_factors(
    context: ChartContextSummary,
    chart_data: Dict[str, Any],
) -> List[ChartFactorExplanation]:
    """Diagnose specific chart afflictions and auspicious placements with Shastra citations."""
    factors: List[ChartFactorExplanation] = []
    lagna = context.lagna_sign

    # 1. Debilitation & Neecha Bhanga Factors
    nb_by_planet = {a.graha: a for a in context.neecha_bhanga_assessments}

    for planet in context.debilitated_planets:
        p_name = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
        is_yogakaraka = planet in context.yogakaraka_planets
        nb_assessment = nb_by_planet.get(planet)

        if nb_assessment:
            is_cancelled = nb_assessment.cancellation_status in ("complete_nbry_qualifying", "cancellation_indicator_present", "nbry_neutralized_by_combustion")
            title_en = (
                f"Neecha Bhanga Raja Yoga of {p_name}"
                if nb_assessment.cancellation_status == "complete_nbry_qualifying"
                else (
                    f"Debilitation & Neecha Bhanga of {p_name}"
                    if is_cancelled
                    else f"Debilitation of {p_name} (Neecha)"
                )
            )
            title_ta = (
                f"{p_name} நீச பங்க ராஜ யோகம்"
                if nb_assessment.cancellation_status == "complete_nbry_qualifying"
                else (
                    f"{p_name} நீச பங்கம்"
                    if is_cancelled
                    else f"{p_name} நீச நிலை (நீச்ச கிரகம்)"
                )
            )

            desc_en_parts = [nb_assessment.reason_en]
            desc_ta_parts = [nb_assessment.reason_ta]
            if is_yogakaraka:
                desc_en_parts.append(
                    f"CRITICAL SAFEGUARD: {p_name} is the supreme Yogakaraka for {lagna} Lagna. "
                    "Charity (Daan) is strictly prohibited. Strengthen solely through Sattvic Gayatri Japa or temple worship."
                )
                desc_ta_parts.append(
                    f"முக்கிய சாஸ்திர விதி: {p_name} {lagna} லக்னத்திற்கு யோககாரகன் ஆவார். "
                    "தானம் செய்தல் முற்றிலும் விலக்கப்பட்டுள்ளது; காயத்ரி ஜபம் அல்லது ஆலய வழிபாடு மூலமே பலப்படுத்த வேண்டும்."
                )

            rules_str = "; ".join(nb_assessment.rule_identifiers) if nb_assessment.rule_identifiers else "Brihat Parashara Hora Shastra Ch. 34 & Phaladeepika Ch. 20"

            factors.append(ChartFactorExplanation(
                factor_type="debilitation",
                graha=planet,
                house=nb_assessment.d1_house,
                title_en=title_en,
                title_ta=title_ta,
                description_en=" ".join(desc_en_parts),
                description_ta=" ".join(desc_ta_parts),
                rule_reference=rules_str,
                is_confirmed=True,
                severity=nb_assessment.severity,
                neecha_bhanga=nb_assessment,
            ))
        else:
            factors.append(ChartFactorExplanation(
                factor_type="debilitation",
                graha=planet,
                title_en=f"Debilitation of {p_name} (Neecha)",
                title_ta=f"{p_name} நீச நிலை (நீச்ச கிரகம்)",
                description_en=f"{p_name} is in its debilitation sign.",
                description_ta=f"{p_name} நீச ராசியில் அமர்ந்துள்ளார்.",
                rule_reference="Brihat Parashara Hora Shastra Ch. 34 & Phaladeepika Ch. 20",
                is_confirmed=True,
                severity="high" if is_yogakaraka else "moderate",
            ))

    # 2. Combustion Factors
    for planet in context.combust_planets:
        p_name = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
        factors.append(ChartFactorExplanation(
            factor_type="combustion",
            graha=planet,
            title_en=f"Combustion of {p_name} (Astangata)",
            title_ta=f"{p_name} அஸ்தமனம் (அஸ்தங்கதம்)",
            description_en=(
                f"{p_name} is combust due to close proximity to the Sun. Combustion creates inner friction and "
                "obscures outward results. Propitiation of Surya and chanting the planet's Gayatri mantra is recommended."
            ),
            description_ta=(
                f"{p_name} சூரியனுடன் மிக நெருங்கி அஸ்தமனம் அடைந்துள்ளார். இதனால் கிரக காரக பலன்கள் மறைக்கப்படும்; "
                "சூரிய நமஸ்காரம் மற்றும் குறிப்பிட்ட கிரக காயத்ரி ஜபம் நலம் தரும்."
            ),
            rule_reference="Surya Siddhanta & Phaladeepika Ch. 20 Verse 31",
            is_confirmed=True,
            severity="moderate",
        ))

    # 3. Dusthana Afflictions (6th, 8th, 12th)
    for house_str, p_list in context.dusthana_planets.items():
        h_num = int(house_str)
        h_meaning = {
            6: ("Rog, Rina, Shatru (Health, Debts, Litigation)", "நோய், கடன், வழக்குகள்"),
            8: ("Randhra / Ayur (Chronic delays, unexpected obstacles)", "ஆயுள், திடீர் தடைகள்"),
            12: ("Vyaya (Expenditure, loss, sleep disturbances)", "விரயம், தூக்கமின்மை, நஷ்டம்"),
        }.get(h_num, ("Dusthana", "மறைவு ஸ்தானம்"))

        for planet in p_list:
            if planet in ("rahu", "ketu"):
                continue  # Handled in nodal axis
            p_name = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
            factors.append(ChartFactorExplanation(
                factor_type="dusthana",
                graha=planet,
                house=h_num,
                title_en=f"{p_name} in {h_num}th House ({h_meaning[0].split('(')[0].strip()})",
                title_ta=f"{p_name} {h_num}-ஆம் இடத்தில் ({h_meaning[1]})",
                description_en=(
                    f"{p_name} is located in the {h_num}th Dusthana house ({h_meaning[0]}). "
                    "Remedial pacification harmonizes its energy and mitigates vulnerability during transits."
                ),
                description_ta=(
                    f"{p_name} மறைவு ஸ்தானமான {h_num}-ஆம் இடத்தில் ({h_meaning[1]}) உள்ளார். உரிய சாஸ்திர பரிகாரங்கள் பாதிப்புகளை மட்டுப்படுத்தும்."
                ),
                rule_reference="BPHS Ch. 34 & Bhavartha Ratnakara",
                is_confirmed=True,
                severity="moderate",
            ))

    # 4. Kuja Dosha (Manglik)
    if context.kuja_dosha_status == "present":
        factors.append(ChartFactorExplanation(
            factor_type="kuja_dosha",
            graha="mars",
            title_en="Kuja Dosha (Mars Affliction / Manglik)",
            title_ta="செவ்வாய் தோஷம்",
            description_en=context.kuja_dosha_details or "Un-cancelled Mars affliction affecting marriage and relationships.",
            description_ta="விவாகம் மற்றும் தாம்பத்திய நல்லிணக்கத்தை பாதிக்கும் நிவர்த்தி அடையாத செவ்வாய் தோஷம்.",
            rule_reference="Brihat Parashara Hora Shastra Ch. 81 & Muhurta Chintamani",
            is_confirmed=True,
            severity="high",
        ))
    elif context.kuja_dosha_status == "cancelled":
        factors.append(ChartFactorExplanation(
            factor_type="kuja_dosha_cancelled",
            graha="mars",
            title_en="Kuja Dosha Neutralized (Dosha Bhanga)",
            title_ta="செவ்வாய் தோஷ நிவர்த்தி (தோஷ பங்கம்)",
            description_en=f"Mars placement triggers a classical cancellation: {context.kuja_dosha_details}. No severe dosha operates.",
            description_ta=f"செவ்வாய் அமைப்பு சாஸ்திர விதிப்படி நிவர்த்தி அடைந்துள்ளது: {context.kuja_dosha_details}.",
            rule_reference="Phaladeepika & Muhurta Chintamani Kuja Dosha Apavadas",
            is_confirmed=True,
            severity="mild",
        ))

    # 5. Running Dasa Lord
    if context.running_mahadasha:
        dasa_graha = _norm(context.running_mahadasha)
        p_name = PLANET_CANONICAL_NAMES.get(dasa_graha, dasa_graha.capitalize())
        is_malefic = dasa_graha in context.functional_malefics
        factors.append(ChartFactorExplanation(
            factor_type="running_dasa",
            graha=dasa_graha,
            title_en=f"Active Dasa Period: {p_name} Mahadasha",
            title_ta=f"தற்போதைய திசை: {p_name} மகாதிசை",
            description_en=(
                f"You are currently operating in {p_name} Mahadasha. Remedies associated with {p_name} "
                "carry paramount relevance right now because the Dasa lord is the primary arbiter of life events."
            ),
            description_ta=(
                f"தற்போது {p_name} மகாதிசை நடைபெறுகிறது. திசாநாதனின் அருளைப் பெற உரிய மந்திரம் மற்றும் வழிபாடுகள் உடனடி பலன் தரும்."
            ),
            rule_reference="Brihat Parashara Hora Shastra Ch. 46 (Vimshottari Dasa Results)",
            is_confirmed=True,
            severity="high" if is_malefic else "moderate",
        ))

    return factors


def rank_and_retrieve_remedies(
    context: ChartContextSummary,
    factors: List[ChartFactorExplanation],
    remedies_catalog: List[Dict[str, Any]],
    temples_catalog: List[Dict[str, Any]],
) -> List[RecommendedRemedy]:
    """Deterministically score, filter, and rank remedies for the chart context."""
    results: List[RecommendedRemedy] = []
    temple_by_graha = {t["graha"]: t for t in temples_catalog}

    afflicted_grahas: Set[str] = {f.graha for f in factors if f.factor_type in ("debilitation", "combustion", "dusthana", "kuja_dosha")}
    running_dasa = _norm(context.running_mahadasha)
    running_bhukti = _norm(context.running_bhukti)
    yogakarakas = set(context.yogakaraka_planets)

    for rem_raw in remedies_catalog:
        rem_item = RemedyItem(**rem_raw)
        graha = _norm(rem_item.graha)
        rem_type = _norm(rem_item.remedy_type)

        # GEMSTONE POLICY: Strictly exclude gemstones from automated personalized public recommendations
        if rem_type in ("gemstone", "ratna", "gem"):
            continue

        # Base scoring
        score = 20
        matching_factors: List[str] = []
        reason_en_parts: List[str] = []
        reason_ta_parts: List[str] = []
        yogakaraka_warning: Optional[str] = None

        # Yogakaraka Protection Check
        if graha in yogakarakas:
            if rem_type in ("charity", "daan", "donation"):
                # STRICT PROHIBITION: Omit or mark as strictly restricted
                continue
            else:
                score += 25
                matching_factors.append("Yogakaraka Planet")
                reason_en_parts.append(f"Strengthens your supreme Yogakaraka planet ({graha.capitalize()})")
                reason_ta_parts.append(f"உங்கள் யோககாரக கிரகமான {graha}-வை பலப்படுத்துகிறது")

        # Running Dasa Lord Match
        if graha == running_dasa:
            score += 40
            matching_factors.append("Active Mahadasha Lord")
            reason_en_parts.append(f"Propitiates your active Mahadasha lord ({graha.capitalize()})")
            reason_ta_parts.append(f"நடைபெறும் {graha} திசாநாதனின் அருளைப் பெறுகிறது")
        elif graha == running_bhukti:
            score += 20
            matching_factors.append("Active Antardasha Lord")
            reason_en_parts.append(f"Aligns with your running Antardasha period ({graha.capitalize()})")
            reason_ta_parts.append(f"நடைபெறும் புக்தி நாதனின் அருளைப் பெறுகிறது")

        # Affliction Match (Debilitation, Combustion, Dusthana, Kuja Dosha)
        if graha in afflicted_grahas:
            nb_assessment = next((a for a in context.neecha_bhanga_assessments if a.graha == graha), None)
            if nb_assessment and nb_assessment.cancellation_status == "complete_nbry_qualifying":
                score += 15
                matching_factors.append("Neecha Bhanga Raja Yoga")
                reason_en_parts.append(f"Supports auspicious Raja Yoga realization of {graha.capitalize()} (Neecha Bhanga)")
                reason_ta_parts.append(f"{graha} கிரகத்தின் நீச பங்க ராஜ யோக சுப பலன்களை மேம்படுத்துகிறது")
            elif nb_assessment and nb_assessment.cancellation_status == "nbry_neutralized_by_combustion":
                score += 30
                matching_factors.append("Debilitation with Combustion")
                reason_en_parts.append(f"Propitiates {graha.capitalize()} whose Raja Yoga is neutralized by solar combustion")
                reason_ta_parts.append(f"அஸ்தமனத்தால் பாதிக்கப்பட்ட {graha} கிரகத்தின் சாந்தி பரிகாரம்")
            else:
                score += 30
                matching_factors.append("Diagnosed Chart Affliction")
                reason_en_parts.append(f"Alleviates diagnosed chart affliction of {graha.capitalize()}")
                reason_ta_parts.append(f"ஜாதகத்தில் கண்டறியப்பட்ட {graha} பாதிப்பை நீக்குகிறது")

        # Universal Remedies (e.g. Gayatri, Maha Mrityunjaya)
        if graha == "universal":
            score = 50
            matching_factors.append("Universal Shanti")
            reason_en_parts.append("Universal Vedic hymn for peace, health, and dispelling inner fear")
            reason_ta_parts.append("ஆயுள் மற்றும் ஆரோக்கியம் தரும் அகில உலக வேத சாந்தி மந்திரம்")

        if not matching_factors and graha != "universal":
            # Baseline general remedy
            score = 15
            reason_en_parts.append(f"General propitiation for {graha.capitalize()}")
            reason_ta_parts.append(f"{graha} கிரகத்திற்கான பொதுவான சாஸ்திர பரிகாரம்")

        # Priority tier
        if score >= 65:
            tier = "essential"
        elif score >= 40:
            tier = "recommended"
        else:
            tier = "optional"

        # Link Kaveri Delta Temple if available
        linked_temple = None
        if graha in temple_by_graha:
            linked_temple = NavagrahaTempleItem(**temple_by_graha[graha])

        reason_en = ". ".join(reason_en_parts) + "."
        reason_ta = ". ".join(reason_ta_parts) + "."

        results.append(RecommendedRemedy(
            remedy=rem_item,
            relevance_score=min(100, score),
            priority_tier=tier,
            reason_en=reason_en,
            reason_ta=reason_ta,
            matching_factors=matching_factors,
            yogakaraka_warning=yogakaraka_warning,
            temple=linked_temple,
        ))

    # Sort descending by relevance score
    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return results


async def generate_remedy_analysis(
    chart_data: Dict[str, Any],
    horoscope_id: Optional[str] = None,
    person_name: Optional[str] = None,
    birth_date: Optional[str] = None,
    birth_time: Optional[str] = None,
    dasa_data: Optional[Dict[str, Any]] = None,
    client_inputs: Optional[Dict[str, Any]] = None,
) -> RemedyAnalysisResponse:
    """Generate complete, shastra-validated remedy analysis for a chart snapshot."""
    # Context extraction
    context = extract_chart_context(chart_data, dasa_data)

    # Diagnostics
    factors = diagnose_chart_factors(context, chart_data)

    # Knowledge retrieval
    remedies = await remedy_repository.get_all_remedies()
    temples = await remedy_repository.get_all_navagraha_temples()

    # Ranking
    recommendations = rank_and_retrieve_remedies(context, factors, remedies, temples)

    fingerprint_seed = {
        "lagna": context.lagna_sign,
        "moon": context.moon_sign,
        "nakshatra": context.moon_nakshatra,
        "sun": context.sun_sign,
        "dasa": context.running_mahadasha,
        "inputs": client_inputs or {},
    }
    input_fingerprint = compute_input_fingerprint(fingerprint_seed)

    return RemedyAnalysisResponse(
        horoscope_id=horoscope_id,
        person_name=person_name or "Birth Chart Analysis",
        birth_date=birth_date,
        birth_time=birth_time,
        calculation_timestamp=datetime.now(timezone.utc).isoformat(),
        chart_context=context,
        diagnosed_factors=factors,
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        is_stale=False,
        input_fingerprint=input_fingerprint,
        status="complete",
    )
