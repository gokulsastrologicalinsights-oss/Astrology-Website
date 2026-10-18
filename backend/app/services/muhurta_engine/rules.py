"""Occasion-Specific Muhurta Rule Engine.

Evaluates candidate time intervals against configured astrological rules,
distinguishing between:
1. Mandatory rules
2. Disqualifying conditions
3. Advisories
4. Optional advanced checks (Tara Bala, Chandra Bala)

Provides transparent scoring, detailed explanations, and failure diagnostics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


TARA_NAMES = {
    1: {"name": "Janma", "nature": "Caution / Body Strain", "is_benefic": False, "status": "advisory"},
    2: {"name": "Sampat", "nature": "Wealth & Prosperity", "is_benefic": True, "status": "pass"},
    3: {"name": "Vipat", "nature": "Danger / Loss", "is_benefic": False, "status": "fail"},
    4: {"name": "Kshema", "nature": "Safety & Well-being", "is_benefic": True, "status": "pass"},
    5: {"name": "Pratyak", "nature": "Obstacles / Delay", "is_benefic": False, "status": "fail"},
    6: {"name": "Sadhana", "nature": "Achievement & Fulfilment", "is_benefic": True, "status": "pass"},
    7: {"name": "Naidhana (Vadha)", "nature": "Fatal / Severe Destruction", "is_benefic": False, "status": "fail"},
    8: {"name": "Mitra", "nature": "Friendship & Concord", "is_benefic": True, "status": "pass"},
    9: {"name": "Parama Mitra", "nature": "Supreme Beneficence", "is_benefic": True, "status": "pass"},
}

MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}


def evaluate_tara_bala(transit_nakshatra_idx: int, birth_nakshatra_idx: Optional[int]) -> Dict[str, Any]:
    """Calculates Navatara (Tara Bala) from the native's Janma Nakshatra."""
    if not birth_nakshatra_idx or birth_nakshatra_idx < 1 or birth_nakshatra_idx > 27:
        return {
            "status": "incomplete",
            "tara_number": None,
            "tara_name": None,
            "is_favorable": None,
            "passed": False,
            "details": "Birth star (Janma Nakshatra) not supplied. Tara Bala check is incomplete.",
        }

    # Count from Janma Nakshatra to transit Nakshatra inclusive
    count = ((transit_nakshatra_idx - birth_nakshatra_idx) % 27) + 1
    tara_num = ((count - 1) % 9) + 1
    tara_info = TARA_NAMES[tara_num]

    passed = tara_info["is_benefic"]
    return {
        "status": "pass" if passed else ("advisory" if tara_info["status"] == "advisory" else "fail"),
        "tara_number": tara_num,
        "tara_name": tara_info["name"],
        "nature": tara_info["nature"],
        "is_favorable": passed,
        "passed": passed,
        "details": f"Tara {tara_num} ({tara_info['name']}): {tara_info['nature']}.",
    }


def evaluate_chandra_bala(transit_moon_sign_idx: int, birth_moon_sign_idx: Optional[int]) -> Dict[str, Any]:
    """Calculates Chandra Bala from the native's Janma Rashi (1..12).
    Auspicious houses: 1, 3, 6, 7, 10, 11 (and 2, 5, 9).
    Strictly inauspicious: 8 (Ashtama Chandra) and 12.
    """
    if not birth_moon_sign_idx or birth_moon_sign_idx < 1 or birth_moon_sign_idx > 12:
        return {
            "status": "incomplete",
            "house_from_moon": None,
            "is_favorable": None,
            "passed": False,
            "details": "Birth Moon Sign (Janma Rashi) not supplied. Chandra Bala check is incomplete.",
        }

    house = ((transit_moon_sign_idx - birth_moon_sign_idx) % 12) + 1
    is_ashtama = (house == 8)
    is_good = house in {1, 3, 6, 7, 10, 11, 2, 5, 9}

    if is_ashtama:
        return {
            "status": "fail",
            "house_from_moon": house,
            "is_favorable": False,
            "passed": False,
            "is_ashtama_chandra": True,
            "details": f"Ashtama Chandra! Transit Moon is in 8th house from Janma Rashi. Strictly prohibited for auspicious ventures.",
        }

    return {
        "status": "pass" if is_good else "advisory",
        "house_from_moon": house,
        "is_favorable": is_good,
        "passed": is_good,
        "is_ashtama_chandra": False,
        "details": f"Transit Moon is in house {house} from Janma Rashi ({'Auspicious Chandra Bala' if is_good else 'Moderate/Neutral placement'}).",
    }


def check_interval_overlap(
    slot_start: datetime, slot_end: datetime, window_start_str: str, window_end_str: str
) -> bool:
    """Returns True if the slot [slot_start, slot_end] overlaps with [window_start, window_end]."""
    w_start = datetime.fromisoformat(window_start_str)
    w_end = datetime.fromisoformat(window_end_str)
    # Overlap occurs when max(start1, start2) < min(end1, end2)
    return max(slot_start, w_start) < min(slot_end, w_end)


def evaluate_muhurta_slot(
    slot_start_utc: datetime,
    slot_end_utc: datetime,
    daily_panchang: Dict[str, Any],
    lagna_planets: Dict[str, Any],
    rules: Dict[str, Any],
    birth_details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluates a candidate time window [slot_start_utc, slot_end_utc] against occasion rules.

    Returns:
        Dict containing:
        - status: 'meets_configured_rules' | 'meets_rules_with_advisories' | 'fails_mandatory_rules' | 'incomplete'
        - score: 0..100 (transparent internal rule-based score)
        - passed_rules: List[Dict]
        - failed_rules: List[Dict]
        - advisories: List[Dict]
        - incomplete_checks: List[Dict]
        - explanation: str
    """
    passed_rules: List[Dict[str, Any]] = []
    failed_rules: List[Dict[str, Any]] = []
    advisories: List[Dict[str, Any]] = []
    incomplete_checks: List[Dict[str, Any]] = []

    score = 100
    points_breakdown: Dict[str, int] = {}

    # Extract Panchang elements
    tithi_num = daily_panchang["tithi"]["number"]
    nak_num = daily_panchang["nakshatra"]["number"]
    weekday_num = daily_panchang["vara"]["weekday_number"]
    inauspicious = daily_panchang["inauspicious_periods"]
    dur_muhurtas = daily_panchang["dur_muhurtas"]
    varjyam = daily_panchang["varjyam"]
    auspicious = daily_panchang["auspicious_periods"]

    # 1. Prohibited Inauspicious Periods (Mandatory Rules)
    # Rahu Kalam
    if rules.get("prohibit_rahu_kalam", True):
        rahu = inauspicious["rahu_kalam"]
        if check_interval_overlap(slot_start_utc, slot_end_utc, rahu["start_utc"], rahu["end_utc"]):
            failed_rules.append({
                "rule": "Rahu Kalam Avoidance",
                "severity": "mandatory",
                "message": f"Time slot overlaps with Rahu Kalam ({rahu['duration_minutes']} min).",
            })
            score -= 30
        else:
            passed_rules.append({"rule": "Rahu Kalam Avoidance", "message": "Clean of Rahu Kalam."})

    # Yamagandam
    if rules.get("prohibit_yamagandam", True):
        yama = inauspicious["yamagandam"]
        if check_interval_overlap(slot_start_utc, slot_end_utc, yama["start_utc"], yama["end_utc"]):
            failed_rules.append({
                "rule": "Yamagandam Avoidance",
                "severity": "mandatory",
                "message": f"Time slot overlaps with Yamagandam ({yama['duration_minutes']} min).",
            })
            score -= 25
        else:
            passed_rules.append({"rule": "Yamagandam Avoidance", "message": "Clean of Yamagandam."})

    # Gulikai
    if rules.get("prohibit_gulikai", False):
        guli = inauspicious["gulikai"]
        if check_interval_overlap(slot_start_utc, slot_end_utc, guli["start_utc"], guli["end_utc"]):
            failed_rules.append({
                "rule": "Gulika Kalam Avoidance",
                "severity": "mandatory",
                "message": f"Time slot overlaps with Gulika Kalam ({guli['duration_minutes']} min).",
            })
            score -= 15
        else:
            passed_rules.append({"rule": "Gulika Kalam Avoidance", "message": "Clean of Gulika Kalam."})

    # Dur Muhurta
    if rules.get("prohibit_dur_muhurta", True):
        has_dur = False
        for dm in dur_muhurtas:
            if check_interval_overlap(slot_start_utc, slot_end_utc, dm["start_utc"], dm["end_utc"]):
                has_dur = True
                break
        if has_dur:
            failed_rules.append({
                "rule": "Dur Muhurta Avoidance",
                "severity": "mandatory",
                "message": "Time slot intersects with a traditional Dur Muhurta window.",
            })
            score -= 20
        else:
            passed_rules.append({"rule": "Dur Muhurta Avoidance", "message": "Clean of Dur Muhurta."})

    # Varjyam (Tyajyam)
    if rules.get("prohibit_varjyam", True):
        if check_interval_overlap(slot_start_utc, slot_end_utc, varjyam["start_utc"], varjyam["end_utc"]):
            failed_rules.append({
                "rule": "Varjyam (Tyajyam) Avoidance",
                "severity": "mandatory",
                "message": f"Time slot falls inside Nakshatra Varjyam / Tyajyam period ({varjyam['duration_minutes']} min).",
            })
            score -= 25
        else:
            passed_rules.append({"rule": "Varjyam Avoidance", "message": "Clean of Nakshatra Varjyam."})

    # 2. Tithi Suitability
    acceptable_tithis = rules.get("acceptable_tithis", [])
    if acceptable_tithis:
        if tithi_num in acceptable_tithis:
            passed_rules.append({
                "rule": "Acceptable Tithi",
                "message": f"Tithi {daily_panchang['tithi']['name']} ({daily_panchang['tithi']['paksha']} {tithi_num}) is auspicious for this occasion.",
            })
        else:
            # Check if it is a Rikta Tithi (4, 9, 14, 19, 24, 29) or Amavasya (30)
            is_rikta = tithi_num in {4, 9, 14, 19, 24, 29}
            severity = "mandatory" if (is_rikta or tithi_num == 30) else "advisory"
            failed_rules.append({
                "rule": "Acceptable Tithi",
                "severity": severity,
                "message": f"Tithi {daily_panchang['tithi']['name']} is not in the preferred list for this occasion.",
            })
            score -= (20 if severity == "mandatory" else 10)

    # 3. Nakshatra Suitability
    acceptable_nakshatras = rules.get("acceptable_nakshatras", [])
    if acceptable_nakshatras:
        if nak_num in acceptable_nakshatras:
            passed_rules.append({
                "rule": "Acceptable Nakshatra",
                "message": f"Nakshatra {daily_panchang['nakshatra']['name']} is highly favorable.",
            })
        else:
            failed_rules.append({
                "rule": "Acceptable Nakshatra",
                "severity": "advisory",
                "message": f"Nakshatra {daily_panchang['nakshatra']['name']} is not among the primary traditional stars for this event.",
            })
            score -= 15

    # 4. Weekday Suitability
    acceptable_weekdays = rules.get("acceptable_weekdays", [])
    if acceptable_weekdays:
        if weekday_num in acceptable_weekdays:
            passed_rules.append({
                "rule": "Acceptable Weekday",
                "message": f"{daily_panchang['vara']['name_en']} is an auspicious day.",
            })
        else:
            advisories.append({
                "rule": "Weekday Preference",
                "message": f"{daily_panchang['vara']['name_en']} is less preferred for this ceremony.",
            })
            score -= 10

    # 5. Lagna and Bhava Shuddhi
    asc = lagna_planets.get("ascendant", {})
    occupants = lagna_planets.get("bhava_occupants", {})

    # Allowed Lagnas
    allowed_lagnas = rules.get("allowed_lagnas", [])
    if allowed_lagnas:
        if asc.get("sign_index") in allowed_lagnas:
            passed_rules.append({
                "rule": "Favorable Lagna (Ascendant)",
                "message": f"Ascendant {asc.get('sign_name')} ({asc.get('sign_name_ta')}) matches the required sign nature.",
            })
        else:
            advisories.append({
                "rule": "Lagna Nature",
                "message": f"Ascendant {asc.get('sign_name')} is not the preferred sign category for this occasion.",
            })
            score -= 10

    # Ashtama Shuddhi (8th house must have no planets)
    if rules.get("require_ashtama_shuddhi", True):
        occupants_8th = occupants.get(8, [])
        if occupants_8th:
            failed_rules.append({
                "rule": "Ashtama Shuddhi (Clean 8th House)",
                "severity": "mandatory",
                "message": f"Ashtama Dosha: 8th house is occupied by {', '.join(occupants_8th)}.",
            })
            score -= 25
        else:
            passed_rules.append({
                "rule": "Ashtama Shuddhi",
                "message": "Pristine 8th house: Completely vacant, ensuring longevity and protection from calamity.",
            })

    # Sapthama Shuddhi (7th house free from malefics - vital for marriage)
    if rules.get("require_sapthama_shuddhi", False):
        occupants_7th = occupants.get(7, [])
        malefics_7th = [p for p in occupants_7th if p in MALEFIC_PLANETS]
        if malefics_7th:
            failed_rules.append({
                "rule": "Sapthama Shuddhi (Clean 7th House)",
                "severity": "mandatory",
                "message": f"Sapthama Dosha: 7th house occupied by malefic planet(s) {', '.join(malefics_7th)}.",
            })
            score -= 25
        else:
            passed_rules.append({
                "rule": "Sapthama Shuddhi",
                "message": "7th house is clear of malefic afflictions.",
            })

    # 6. Bonus Auspicious Periods (Abhijit, Amrita Kalam)
    # Check if slot overlaps with Abhijit
    abhijit = auspicious.get("abhijit", {})
    if abhijit and check_interval_overlap(slot_start_utc, slot_end_utc, abhijit["start_utc"], abhijit["end_utc"]):
        if not abhijit.get("is_dur_muhurta_clash"):
            passed_rules.append({
                "rule": "Abhijit Muhurta Coincidence",
                "message": "Slot coincides with the potent midday Abhijit Muhurta, which neutralizes minor doshas.",
            })
            score = min(100, score + 10)

    # Check if slot overlaps with Amrita Kalam
    amrita = auspicious.get("amrita_kalam", {})
    if amrita and check_interval_overlap(slot_start_utc, slot_end_utc, amrita["start_utc"], amrita["end_utc"]):
        passed_rules.append({
            "rule": "Amrita Kalam Alignment",
            "message": "Slot coincides with Amrita Kalam (nectar window).",
        })
        score = min(100, score + 10)

    # 7. Tara Bala & Chandra Bala (when birth details provided)
    has_groom_or_native = False
    if birth_details:
        native_nak = birth_details.get("native_nakshatra") or birth_details.get("groom_nakshatra")
        native_rashi = birth_details.get("native_rashi") or birth_details.get("groom_rashi")

        if native_nak:
            has_groom_or_native = True
            tb = evaluate_tara_bala(nak_num, native_nak)
            if tb["status"] == "pass":
                passed_rules.append({"rule": "Tara Bala", "message": tb["details"]})
            elif tb["status"] == "fail":
                failed_rules.append({"rule": "Tara Bala", "severity": "mandatory", "message": tb["details"]})
                score -= 20
            else:
                advisories.append({"rule": "Tara Bala", "message": tb["details"]})
                score -= 5

        if native_rashi:
            has_groom_or_native = True
            cb = evaluate_chandra_bala(asc.get("sign_index", 1), native_rashi)
            if cb["status"] == "pass":
                passed_rules.append({"rule": "Chandra Bala", "message": cb["details"]})
            elif cb["status"] == "fail":
                failed_rules.append({"rule": "Chandra Bala", "severity": "mandatory", "message": cb["details"]})
                score -= 20
            else:
                advisories.append({"rule": "Chandra Bala", "message": cb["details"]})
                score -= 5

        # If bride details present (for marriage)
        bride_nak = birth_details.get("bride_nakshatra")
        if bride_nak:
            tb_bride = evaluate_tara_bala(nak_num, bride_nak)
            if tb_bride["status"] == "pass":
                passed_rules.append({"rule": "Bride Tara Bala", "message": f"Bride: {tb_bride['details']}"})
            elif tb_bride["status"] == "fail":
                failed_rules.append({"rule": "Bride Tara Bala", "severity": "mandatory", "message": f"Bride: {tb_bride['details']}"})
                score -= 20

    if rules.get("require_tara_bala", False) and not has_groom_or_native:
        incomplete_checks.append({
            "check": "Tara Bala",
            "message": "Native / Bride / Groom Janma Nakshatra not provided. Tara Bala compatibility could not be computed.",
        })

    if rules.get("require_chandra_bala", False) and not has_groom_or_native:
        incomplete_checks.append({
            "check": "Chandra Bala",
            "message": "Native Janma Rashi not provided. Chandra Bala strength could not be computed.",
        })

    # Final Score & Status Clamping
    score = max(0, min(100, score))

    has_mandatory_failure = any(f.get("severity") == "mandatory" for f in failed_rules)

    if has_mandatory_failure:
        status = "fails_mandatory_rules"
        explanation = f"Fails mandatory Muhurta criteria: {failed_rules[0]['message']}"
    elif incomplete_checks:
        status = "incomplete"
        explanation = f"Meets available rules with score {score}/100, but personal birth data is missing for required checks."
    elif advisories or failed_rules:
        status = "meets_rules_with_advisories"
        explanation = f"Meets core rules with score {score}/100, with minor traditional advisories."
    else:
        status = "meets_configured_rules"
        explanation = f"Pristine auspicious window! Fully satisfies all configured rules with score {score}/100."

    return {
        "status": status,
        "score": score,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "advisories": advisories,
        "incomplete_checks": incomplete_checks,
        "explanation": explanation,
    }
