"""Nakshatra Transit & Electional Suitability Evaluator.

Provides deterministic evaluations of:
1. Functional Nature classifications (Fixed, Soft, Swift, Sharp, Movable, Cruel, Mixed)
2. Activity suitability checks for electional (Muhurta) decision making
3. Pada-specific character and blemish (Dosha) diagnostics with Shastric Upayas
4. Filtering, search, and canonical 28-Nakshatra lookups
"""

from typing import List, Dict, Any, Optional, Union
from app.services.nakshatra_engine.nakshatra_catalog import (
    NAKSHATRAS_CATALOG,
    FUNCTIONAL_NATURE_GROUPS,
    NAKSHATRAS_SUMMARY_TABLE,
    EBOOK_TREATISE,
    NakshatraData,
)


def get_all_nakshatras(
    nature: Optional[str] = None,
    direction: Optional[str] = None,
    gender: Optional[str] = None,
    result: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all nakshatras matching optional criteria."""
    results = []
    for item in NAKSHATRAS_CATALOG:
        if nature:
            nature_low = nature.lower()
            if nature_low not in item["functional_nature"].lower():
                continue
        if direction:
            if direction.lower() != item["gaze_direction"].lower():
                continue
        if gender:
            if gender.lower() not in item["gender"].lower():
                continue
        if result:
            if result.upper() != item["result_grade"].upper():
                continue
        if search:
            query = search.lower()
            matched = (
                query in item["name"].lower()
                or query in item["name_tamil"].lower()
                or query in item["ruling_deity"].lower()
                or query in item["functional_nature"].lower()
                or any(query in action.lower() for action in item["favourable_actions"])
                or any(query in alt.lower() for alt in item["alternate_names"])
            )
            if not matched:
                continue
        results.append(item)
    return results


def get_nakshatra_by_id_or_name(identifier: Union[int, str]) -> Optional[Dict[str, Any]]:
    """Lookup a single nakshatra by numeric ID (1-28) or name."""
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        target_id = int(identifier)
        for item in NAKSHATRAS_CATALOG:
            if item["id"] == target_id:
                return item
        return None

    target_name = str(identifier).strip().lower()
    for item in NAKSHATRAS_CATALOG:
        if (
            item["name"].lower() == target_name
            or item["name_tamil"].lower() == target_name
            or any(alt.lower() == target_name for alt in item["alternate_names"])
            or target_name in item["name"].lower()
        ):
            return item
    return None


def get_functional_natures_summary() -> Dict[str, Any]:
    """Retrieve the 7 functional transit categories with their rules and suitable activities."""
    return FUNCTIONAL_NATURE_GROUPS


def check_activity_suitability(
    activity: str,
    nakshatra_name_or_id: Union[int, str],
) -> Dict[str, Any]:
    """Evaluates whether an intended activity is auspicious or discouraged in a specific nakshatra."""
    nak = get_nakshatra_by_id_or_name(nakshatra_name_or_id)
    if not nak:
        return {
            "valid": False,
            "error": f"Nakshatra '{nakshatra_name_or_id}' not found in canonical catalog.",
        }

    act_low = activity.lower().strip()
    favourable_list = nak["favourable_actions"]
    inauspicious_list = nak["inauspicious_for"]

    matched_fav = [f for f in favourable_list if act_low in f.lower() or any(w in f.lower() for w in act_low.split())]
    matched_inausp = [ina for ina in inauspicious_list if act_low in ina.lower() or any(w in ina.lower() for w in act_low.split())]

    # Nature-level check
    nature_key = None
    fn_low = nak["functional_nature"].lower()
    for key, group in FUNCTIONAL_NATURE_GROUPS.items():
        if nak["name"] in group["nakshatras"]:
            nature_key = key
            break

    is_suitable = bool(matched_fav) or (not matched_inausp and nak["result_grade"] in ("GOOD", "OK"))
    recommendation = "RECOMMENDED" if matched_fav else ("AVOID" if matched_inausp or nak["result_grade"] == "HARM" else "NEUTRAL_ACCEPTABLE")

    return {
        "valid": True,
        "nakshatra_id": nak["id"],
        "nakshatra_name": nak["name"],
        "nakshatra_name_tamil": nak["name_tamil"],
        "activity_queried": activity,
        "functional_nature": nak["functional_nature"],
        "result_grade": nak["result_grade"],
        "is_suitable": is_suitable,
        "recommendation": recommendation,
        "matched_favourable_points": matched_fav,
        "matched_inauspicious_points": matched_inausp,
        "nature_guidance": FUNCTIONAL_NATURE_GROUPS[nature_key]["suitable_actions_en"] if nature_key else "",
    }


def evaluate_birth_star_pada(
    nakshatra_name_or_id: Union[int, str],
    pada: int,
) -> Dict[str, Any]:
    """Diagnoses the specific birth pada traits, doshas/blemishes, and remedial upaya."""
    nak = get_nakshatra_by_id_or_name(nakshatra_name_or_id)
    if not nak:
        return {
            "valid": False,
            "error": f"Nakshatra '{nakshatra_name_or_id}' not found.",
        }

    if pada < 1 or pada > 4:
        return {
            "valid": False,
            "error": f"Pada number must be between 1 and 4, got {pada}.",
        }

    target_pada = None
    for p in nak["padas"]:
        if p["pada_number"] == pada:
            target_pada = p
            break

    if not target_pada:
        return {
            "valid": False,
            "error": f"Pada {pada} not found for {nak['name']}.",
        }

    has_dosha = "Dosha" in target_pada["dosha_status"] or "Shanti" in target_pada["dosha_status"]
    is_severe = "Severe" in target_pada["dosha_status"] or "Gandanta" in target_pada["dosha_status"]

    return {
        "valid": True,
        "nakshatra_id": nak["id"],
        "nakshatra_name": nak["name"],
        "nakshatra_name_tamil": nak["name_tamil"],
        "pada": pada,
        "degree_range": target_pada["degree_range"],
        "traits": target_pada["traits"],
        "dosha_status": target_pada["dosha_status"],
        "has_dosha": has_dosha,
        "is_severe_gandanta": is_severe,
        "dosha_affects": target_pada["dosha_affects"],
        "remedial_upaya": target_pada["remedy"] or nak.get("general_remedy"),
        "ruling_deity": nak["ruling_deity"],
        "gaze_direction": nak["gaze_direction"],
    }


def get_28_nakshatra_table() -> List[Dict[str, Any]]:
    """Return the 28-Nakshatra canonical master summary table."""
    return NAKSHATRAS_SUMMARY_TABLE


def get_ebook_treatise() -> Dict[str, Any]:
    """Return the complete canonical E-Book treatise on 28 Nakshatras."""
    return EBOOK_TREATISE


def get_nakshatra_prediction(
    identifier: Union[int, str],
    pada: Optional[int] = None,
) -> Dict[str, Any]:
    """Generates a complete predictive report for Moon, Ascendant, Padas, and Doshas for a Nakshatra."""
    nak = get_nakshatra_by_id_or_name(identifier)
    if not nak:
        return {
            "valid": False,
            "error": f"Nakshatra '{identifier}' not found in canonical catalog.",
        }

    pada_detail = None
    if pada is not None and 1 <= pada <= 4:
        for p in nak.get("padas", []):
            if p["pada_number"] == pada:
                pada_detail = p
                break

    return {
        "valid": True,
        "nakshatra_id": nak["id"],
        "name": nak["name"],
        "name_tamil": nak["name_tamil"],
        "alternate_names": nak.get("alternate_names", []),
        "span_zodiac": nak["span_zodiac"],
        "functional_nature": nak["functional_nature"],
        "functional_nature_tamil": nak["functional_nature_tamil"],
        "gender": nak["gender"],
        "result_grade": nak["result_grade"],
        "ruling_deity": nak["ruling_deity"],
        "ruling_planet": nak["ruling_planet"],
        "gaze_direction": nak["gaze_direction"],
        "gaze_direction_tamil": nak["gaze_direction_tamil"],
        "caste": nak["caste"],
        "motivation": nak["motivation"],
        "sight_quality": nak["sight_quality"],
        "luminary_type": nak["luminary_type"],
        "kula_type": nak["kula_type"],
        "num_stars": nak["num_stars"],
        "symbol_shape": nak["symbol_shape"],
        "moon_prediction": nak["moon_indications"],
        "ascendant_prediction": nak["ascendant_indications"],
        "rules_over": nak.get("rules_over", []),
        "places": nak.get("places", []),
        "objects": nak.get("objects", []),
        "abstracts": nak.get("abstracts", []),
        "favourable_actions": nak.get("favourable_actions", []),
        "inauspicious_for": nak.get("inauspicious_for", []),
        "general_remedy": nak.get("general_remedy"),
        "selected_pada": pada,
        "selected_pada_detail": pada_detail,
        "all_padas": nak.get("padas", []),
    }

