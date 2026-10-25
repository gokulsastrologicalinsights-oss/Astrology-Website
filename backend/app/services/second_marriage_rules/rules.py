"""Deterministic implementation of the three extracted KP Second-Marriage Rules.

Contains pure, side-effect-free evaluation functions and explicit classical provenance
metadata for Rule 1 (7th CSL), Rule 2 (2nd CSL), and Rule 3 (9th CSL).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from app.services.second_marriage_rules.models import (
    RuleConditionResult,
    RuleEvaluationStatus,
    SecondMarriageRuleResult,
)

# ---------------------------------------------------------------------------
# Classical Canonical Constants & Provenance
# ---------------------------------------------------------------------------

RULE_1_ID = "KP-SM-RULE-1"
RULE_1_NAME = "7th Cusp Sub-Lord Second-Marriage Rule"
RULE_1_SOURCE_ID = "KP Reader IV / Extracted Classical KP Rule 1"
RULE_1_SOURCE_TEXT = (
    "The 7th cusp sub-lord is deposited in Gemini, Virgo, or Pisces, OR the 7th cusp sub-lord "
    "is Mercury or Jupiter; AND the 7th cusp sub-lord signifies house 2 or house 11, or both."
)
RULE_1_ASSUMPTIONS = [
    "Dual/mutable signs (Mercury/Jupiter rulership) signify multiplicity, adaptability, and repetition in partnerships.",
    "Strict source fidelity: Only Gemini, Virgo, and Pisces are specified by the source rule. "
    "Sagittarius is intentionally NOT added to the sign condition to avoid silent rule drift.",
    "Houses 2 (kutumbasthana/family addition) and 11 (labhasthana/fulfillment of partnership desires) "
    "provide the necessary fructifying linkage.",
]
RULE_1_ALLOWED_PLANETS: Set[str] = {"Mercury", "Jupiter"}
RULE_1_ALLOWED_SIGNS: Set[str] = {"Gemini", "Virgo", "Pisces"}
RULE_1_SUPPORTIVE_HOUSES: Set[int] = {2, 11}


RULE_2_ID = "KP-SM-RULE-2"
RULE_2_NAME = "2nd Cusp Sub-Lord Second-Marriage Rule"
RULE_2_SOURCE_ID = "KP Reader IV / Extracted Classical KP Rule 2"
RULE_2_SOURCE_TEXT = "The 2nd cusp sub-lord signifies house 7 or house 11."
RULE_2_ASSUMPTIONS = [
    "House 2 governs the physical addition of a family member (Kutumba Vriddhi).",
    "Connection to House 7 (Kalathrasthana/spouse) or House 11 (fulfillment/friendship/partnership tie) "
    "fructifies the secondary matrimonial union.",
]
RULE_2_SUPPORTIVE_HOUSES: Set[int] = {7, 11}


RULE_3_ID = "KP-SM-RULE-3"
RULE_3_NAME = "9th Cusp Sub-Lord Second-Marriage Rule"
RULE_3_SOURCE_ID = "KP Reader IV / Extracted Classical KP Rule 3"
RULE_3_SOURCE_TEXT = "The 9th cusp sub-lord signifies house 2, house 9, or house 11."
RULE_3_ASSUMPTIONS = [
    "The 9th house is evaluated as the primary significator for the second spouse under the classical "
    "Bhavat Bhava doctrine: the second spouse is conceived in the context of the first spouse's younger sibling "
    "(3rd house counted from the 7th house = 9th house).",
    "Signification of House 2 (family addition), House 9 (second partner's ascendant), or House 11 (fulfillment) "
    "provides the requisite promise.",
]
RULE_3_SUPPORTIVE_HOUSES: Set[int] = {2, 9, 11}

VALID_PLANET_NAMES: Set[str] = {
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
}

VALID_ZODIAC_SIGNS: Set[str] = {
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
}


# ---------------------------------------------------------------------------
# Normalization Utilities
# ---------------------------------------------------------------------------

def normalize_planet_name(planet: Optional[str]) -> Optional[str]:
    """Normalizes planet name string to standard title case."""
    if not planet or not isinstance(planet, str):
        return None
    cleaned = planet.strip().title()
    return cleaned if cleaned in VALID_PLANET_NAMES else None


def normalize_sign_name(sign: Optional[str]) -> Optional[str]:
    """Normalizes zodiac sign name string to standard title case."""
    if not sign or not isinstance(sign, str):
        return None
    cleaned = sign.strip().title()
    return cleaned if cleaned in VALID_ZODIAC_SIGNS else None


def normalize_house_numbers(houses: Optional[List[Any]]) -> Optional[List[int]]:
    """Normalizes a list of house numbers to sorted unique integers in 1..12.
    
    Returns None if houses is None (indicating missing calculation data).
    Returns [] if houses is an empty list (indicating evaluated zero significations).
    """
    if houses is None:
        return None
    valid: Set[int] = set()
    for h in houses:
        try:
            h_int = int(h)
            if 1 <= h_int <= 12:
                valid.add(h_int)
        except (ValueError, TypeError):
            continue
    return sorted(list(valid))


# ---------------------------------------------------------------------------
# Pure Rule Evaluation Functions
# ---------------------------------------------------------------------------

def evaluate_rule_1(
    sub_lord: Optional[str],
    deposited_sign: Optional[str],
    significations: Optional[List[int]],
) -> SecondMarriageRuleResult:
    """Evaluates Rule 1: 7th cusp sub-lord conditions.
    
    Condition A: CSL is Mercury/Jupiter OR deposited in Gemini/Virgo/Pisces.
    Condition B: CSL signifies house 2 or 11.
    Rule passes iff Condition A AND Condition B pass.
    """
    norm_sl = normalize_planet_name(sub_lord)
    norm_sign = normalize_sign_name(deposited_sign)
    norm_sigs = normalize_house_numbers(significations)

    conditions: List[RuleConditionResult] = []

    # 1. Condition A Evaluation
    cond_a_status = RuleEvaluationStatus.FAIL
    cond_a_bool: Optional[bool] = False
    cond_a_evidence: Dict[str, Any] = {
        "sub_lord": norm_sl,
        "is_mercury_or_jupiter": False,
        "deposited_sign": norm_sign,
        "is_gem_vir_pis": False,
    }

    if not norm_sl:
        cond_a_status = RuleEvaluationStatus.INDETERMINATE
        cond_a_bool = None
        cond_a_exp = "Missing or invalid 7th cusp sub-lord identifier."
    elif norm_sl in RULE_1_ALLOWED_PLANETS:
        cond_a_evidence["is_mercury_or_jupiter"] = True
        cond_a_status = RuleEvaluationStatus.PASS
        cond_a_bool = True
        cond_a_exp = f"7th CSL ({norm_sl}) satisfies Condition A directly as Mercury/Jupiter."
    else:
        # Planet is not Mercury/Jupiter; must evaluate deposited sign
        if not norm_sign:
            cond_a_status = RuleEvaluationStatus.INDETERMINATE
            cond_a_bool = None
            cond_a_exp = f"7th CSL ({norm_sl}) is not Mercury/Jupiter and deposited sign is missing/invalid."
        elif norm_sign in RULE_1_ALLOWED_SIGNS:
            cond_a_evidence["is_gem_vir_pis"] = True
            cond_a_status = RuleEvaluationStatus.PASS
            cond_a_bool = True
            cond_a_exp = f"7th CSL ({norm_sl}) is deposited in {norm_sign} (one of Gemini, Virgo, Pisces)."
        else:
            cond_a_status = RuleEvaluationStatus.FAIL
            cond_a_bool = False
            cond_a_exp = (
                f"7th CSL ({norm_sl}) is neither Mercury/Jupiter nor deposited in Gemini, Virgo, or Pisces "
                f"(deposited in {norm_sign})."
            )

    conditions.append(
        RuleConditionResult(
            condition_id="R1_COND_A",
            condition_name="CSL Planet (Mercury/Jupiter) or Deposited Sign (Gemini/Virgo/Pisces)",
            status=cond_a_status,
            evaluated_bool=cond_a_bool,
            evidence=cond_a_evidence,
            explanation=cond_a_exp,
        )
    )

    # 2. Condition B Evaluation
    cond_b_status = RuleEvaluationStatus.FAIL
    cond_b_bool: Optional[bool] = False
    hits: List[int] = []

    if norm_sigs is None or not norm_sl:
        cond_b_status = RuleEvaluationStatus.INDETERMINATE
        cond_b_bool = None
        cond_b_exp = f"Signification data is missing or incomplete for 7th CSL ({norm_sl or 'Unknown'})."
    else:
        hits = sorted(list(set(norm_sigs).intersection(RULE_1_SUPPORTIVE_HOUSES)))
        if hits:
            cond_b_status = RuleEvaluationStatus.PASS
            cond_b_bool = True
            cond_b_exp = f"7th CSL ({norm_sl}) signifies supportive house(s) {hits} (subset of {{2, 11}})."
        else:
            cond_b_status = RuleEvaluationStatus.FAIL
            cond_b_bool = False
            cond_b_exp = f"7th CSL ({norm_sl}) signifies {norm_sigs}, lacking supportive houses 2 or 11."

    conditions.append(
        RuleConditionResult(
            condition_id="R1_COND_B",
            condition_name="CSL Signification of House 2 or 11",
            status=cond_b_status,
            evaluated_bool=cond_b_bool,
            evidence={"significations": norm_sigs or [], "hits": hits},
            explanation=cond_b_exp,
        )
    )

    # 3. Overall Rule 1 Resolution (AND logic)
    if cond_a_status == RuleEvaluationStatus.INDETERMINATE or cond_b_status == RuleEvaluationStatus.INDETERMINATE:
        overall_status = RuleEvaluationStatus.INDETERMINATE
        overall_exp = (
            f"Rule 1 evaluation is INDETERMINATE due to missing calculation inputs: "
            f"Condition A is {cond_a_status.value}; Condition B is {cond_b_status.value}."
        )
    elif cond_a_bool is True and cond_b_bool is True:
        overall_status = RuleEvaluationStatus.PASS
        overall_exp = (
            f"Rule 1 PASSES: 7th CSL ({norm_sl}) satisfies Condition A ({cond_a_exp}) "
            f"AND Condition B ({cond_b_exp})."
        )
    else:
        overall_status = RuleEvaluationStatus.FAIL
        failures = []
        if not cond_a_bool:
            failures.append("Condition A (Planet/Sign)")
        if not cond_b_bool:
            failures.append("Condition B (Houses 2/11)")
        overall_exp = f"Rule 1 FAILS: Unmet condition(s): {', '.join(failures)}."

    return SecondMarriageRuleResult(
        rule_id=RULE_1_ID,
        rule_name=RULE_1_NAME,
        source_identifier=RULE_1_SOURCE_ID,
        source_text=RULE_1_SOURCE_TEXT,
        assumptions=RULE_1_ASSUMPTIONS,
        status=overall_status,
        cusp_number=7,
        cusp_sub_lord=norm_sl,
        deposited_sign=norm_sign,
        significations_used=norm_sigs or [],
        conditions=conditions,
        explanation=overall_exp,
    )


def evaluate_rule_2(
    sub_lord: Optional[str],
    significations: Optional[List[int]],
) -> SecondMarriageRuleResult:
    """Evaluates Rule 2: 2nd cusp sub-lord signifies house 7 or 11."""
    norm_sl = normalize_planet_name(sub_lord)
    norm_sigs = normalize_house_numbers(significations)

    if not norm_sl or norm_sigs is None:
        status = RuleEvaluationStatus.INDETERMINATE
        ev_bool: Optional[bool] = None
        exp = f"Missing sub-lord or signification data for 2nd cusp (sub_lord={norm_sl or 'Missing'})."
        hits: List[int] = []
    else:
        hits = sorted(list(set(norm_sigs).intersection(RULE_2_SUPPORTIVE_HOUSES)))
        if hits:
            status = RuleEvaluationStatus.PASS
            ev_bool = True
            exp = f"2nd CSL ({norm_sl}) signifies supportive house(s) {hits} (subset of {{7, 11}})."
        else:
            status = RuleEvaluationStatus.FAIL
            ev_bool = False
            exp = f"2nd CSL ({norm_sl}) signifies {norm_sigs}, lacking supportive house 7 or 11."

    cond = RuleConditionResult(
        condition_id="R2_PRIMARY",
        condition_name="2nd CSL Signifies House 7 or 11",
        status=status,
        evaluated_bool=ev_bool,
        evidence={"sub_lord": norm_sl, "significations": norm_sigs or [], "hits": hits},
        explanation=exp,
    )

    return SecondMarriageRuleResult(
        rule_id=RULE_2_ID,
        rule_name=RULE_2_NAME,
        source_identifier=RULE_2_SOURCE_ID,
        source_text=RULE_2_SOURCE_TEXT,
        assumptions=RULE_2_ASSUMPTIONS,
        status=status,
        cusp_number=2,
        cusp_sub_lord=norm_sl,
        deposited_sign=None,
        significations_used=norm_sigs or [],
        conditions=[cond],
        explanation=f"Rule 2 {status.value}: {exp}",
    )


def evaluate_rule_3(
    sub_lord: Optional[str],
    significations: Optional[List[int]],
) -> SecondMarriageRuleResult:
    """Evaluates Rule 3: 9th cusp sub-lord signifies house 2, 9, or 11."""
    norm_sl = normalize_planet_name(sub_lord)
    norm_sigs = normalize_house_numbers(significations)

    if not norm_sl or norm_sigs is None:
        status = RuleEvaluationStatus.INDETERMINATE
        ev_bool: Optional[bool] = None
        exp = f"Missing sub-lord or signification data for 9th cusp (sub_lord={norm_sl or 'Missing'})."
        hits: List[int] = []
    else:
        hits = sorted(list(set(norm_sigs).intersection(RULE_3_SUPPORTIVE_HOUSES)))
        if hits:
            status = RuleEvaluationStatus.PASS
            ev_bool = True
            exp = f"9th CSL ({norm_sl}) signifies supportive house(s) {hits} (subset of {{2, 9, 11}})."
        else:
            status = RuleEvaluationStatus.FAIL
            ev_bool = False
            exp = f"9th CSL ({norm_sl}) signifies {norm_sigs}, lacking supportive houses 2, 9, or 11."

    cond = RuleConditionResult(
        condition_id="R3_PRIMARY",
        condition_name="9th CSL Signifies House 2, 9, or 11",
        status=status,
        evaluated_bool=ev_bool,
        evidence={"sub_lord": norm_sl, "significations": norm_sigs or [], "hits": hits},
        explanation=exp,
    )

    return SecondMarriageRuleResult(
        rule_id=RULE_3_ID,
        rule_name=RULE_3_NAME,
        source_identifier=RULE_3_SOURCE_ID,
        source_text=RULE_3_SOURCE_TEXT,
        assumptions=RULE_3_ASSUMPTIONS,
        status=status,
        cusp_number=9,
        cusp_sub_lord=norm_sl,
        deposited_sign=None,
        significations_used=norm_sigs or [],
        conditions=[cond],
        explanation=f"Rule 3 {status.value}: {exp}",
    )
