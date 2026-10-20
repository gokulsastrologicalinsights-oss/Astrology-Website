"""Isolated KP Marriage Rulebook and Decision Logic.

This module implements the deterministic KP natal marriage promise evaluation
following the exhaustive K1–K9 truth table and the classical ABCD significator
hierarchy without data loss.

Classical Citations & Provenance:
- Core sub-lord doctrine: K.S. Krishnamurti, KP Reader III (1971), pp. 84-92. [SOURCE_VERIFIED]
- 7th cuspal sub-lord marriage rule: KP Reader IV (1971), pp. 15-20. [SOURCE_VERIFIED]
- ABCD Significator hierarchy: KP Reader III (1971), pp. 112-118. [SOURCE_VERIFIED]
- Retrograde motion delay: KP Reader III (1971), pp. 84-86. [SOURCE_VERIFIED]
- K5/K6 precedence formalization: [PROJECT_ENGINEERING_POLICY]
- Denial house set {1, 6, 10}: [PROJECT_ENGINEERING_POLICY]
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple, Optional
from app.services.kp_engine.constants import SIGN_LORDS, SIGNS
from app.services.kp_engine.vedic import sign_index, star_lord, sub_lord
from app.services.unified_prediction.models import (
    KPPromiseDetail,
    KPInternalModifier,
    PromiseVerdict,
    RuleProvenanceTag,
)

# ---------------------------------------------------------------------------
# House Definitions (Unified Engine V1 Standard)
# ---------------------------------------------------------------------------
SUPPORTIVE_HOUSES: Set[int] = {2, 7, 11}
DENYING_HOUSES: Set[int] = {1, 6, 10}
NEUTRAL_HOUSES: Set[int] = {3, 4, 5, 8, 9, 12}


# ---------------------------------------------------------------------------
# Classical ABCD Significator Hierarchy (Non-destructive)
# ---------------------------------------------------------------------------

def calculate_house_of_longitude(lon: float, cusps: List[float]) -> int:
    """Determine house 1-12 containing a longitude under 12 Placidus cusps."""
    if not cusps or len(cusps) < 12:
        return 1
    lon_norm = lon % 360.0
    c0 = cusps[0] % 360.0
    lon_rel = (lon_norm - c0) % 360.0

    for i in range(12):
        c_rel = (cusps[i] - c0) % 360.0
        nxt_rel = (cusps[i + 1] - c0) % 360.0 if i < 11 else 360.0
        if c_rel <= lon_rel < nxt_rel:
            return i + 1
    return 12


def compute_abcd_significations(
    planet_positions: Dict[str, float],
    cusps: List[float],
) -> Dict[str, Dict[str, Set[int]]]:
    """Compute classical 4-tier ABCD significators for all planets across 12 houses.
    
    Level A: Planet in the star of an occupant of the house (Strongest)
    Level B: Occupant of the house
    Level C: Planet in the star of the cuspal lord of the house
    Level D: Cuspal lord of the house (Weakest)
    
    Returns
    -------
    dict: planet -> {"A": set(houses), "B": set(houses), "C": set(houses), "D": set(houses), "all": set(houses)}
    """
    # 1. Star-lords of all planets
    star_lords = {p: star_lord(lon) for p, lon in planet_positions.items()}
    
    # 2. Cuspal sign lords (1-indexed house -> planet)
    cuspal_lords = {i + 1: SIGN_LORDS[SIGNS[sign_index(cusps[i])]] for i in range(12)}
    
    # 3. Occupants per house (1-indexed house -> list of planets)
    occupants: Dict[int, List[str]] = {i + 1: [] for i in range(12)}
    for p, lon in planet_positions.items():
        h = calculate_house_of_longitude(lon, cusps)
        occupants[h].append(p)
        
    result: Dict[str, Dict[str, Set[int]]] = {
        p: {"A": set(), "B": set(), "C": set(), "D": set(), "all": set()}
        for p in planet_positions
    }
    
    for h in range(1, 13):
        # Level B: Occupants of house h
        for occ in occupants[h]:
            if occ in result:
                result[occ]["B"].add(h)
                result[occ]["all"].add(h)
                
        # Level A: Planets in star of an occupant of house h
        for occ in occupants[h]:
            for p, s_lord in star_lords.items():
                if s_lord == occ and p in result:
                    result[p]["A"].add(h)
                    result[p]["all"].add(h)
                    
        # Level D: Cuspal lord of house h
        c_lord = cuspal_lords[h]
        if c_lord in result:
            result[c_lord]["D"].add(h)
            result[c_lord]["all"].add(h)
            
        # Level C: Planets in star of cuspal lord of house h
        for p, s_lord in star_lords.items():
            if s_lord == c_lord and p in result:
                result[p]["C"].add(h)
                result[p]["all"].add(h)
                
    return result


# ---------------------------------------------------------------------------
# Exhaustive KP Promise Decision Engine (Cases K1–K9)
# ---------------------------------------------------------------------------

def evaluate_kp_marriage_promise(
    cuspal_sub_lord_7: str,
    star_lord_of_csl: str,
    star_lord_sigs: Set[int],
    sub_lord_sigs: Set[int],
    is_csl_retro: bool = False,
    is_star_retro: bool = False,
) -> KPPromiseDetail:
    """Evaluate KP natal marriage promise deterministically under K1–K9.
    
    Parameters
    ----------
    cuspal_sub_lord_7 : str
        The sub-lord planet of the 7th cusp.
    star_lord_of_csl : str
        The star-lord of the 7th cuspal sub-lord.
    star_lord_sigs : set of int
        All houses signified by star_lord across ABCD tiers.
    sub_lord_sigs : set of int
        All houses signified by cuspal_sub_lord_7 across ABCD tiers.
    is_csl_retro : bool
        Whether cuspal sub-lord is retrograde.
    is_star_retro : bool
        Whether star-lord is retrograde.
    """
    sl_has_sup = bool(star_lord_sigs & SUPPORTIVE_HOUSES)
    sl_has_den = bool(star_lord_sigs & DENYING_HOUSES)
    sub_has_sup = bool(sub_lord_sigs & SUPPORTIVE_HOUSES)
    sub_has_den = bool(sub_lord_sigs & DENYING_HOUSES)
    
    sl_sigs_sorted = sorted(list(star_lord_sigs))
    sub_sigs_sorted = sorted(list(sub_lord_sigs))

    # K1: Pure Support in both Star-Lord and Sub-Lord
    if sl_has_sup and not sl_has_den and sub_has_sup and not sub_has_den:
        return KPPromiseDetail(
            verdict=PromiseVerdict.PROMISED,
            internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-001",
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
            explanation=(
                f"7th CSL ({cuspal_sub_lord_7}) and its Star-Lord ({star_lord_of_csl}) "
                f"unanimously signify supportive houses {sl_sigs_sorted} and {sub_sigs_sorted} "
                "with zero denial significations. Marriage is strongly promised."
            ),
        )

    # K2: Star-Lord mixed, Sub-Lord pure support
    if sl_has_sup and sl_has_den and sub_has_sup and not sub_has_den:
        return KPPromiseDetail(
            verdict=PromiseVerdict.PROMISED,
            internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-001",
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
            explanation=(
                f"Star-Lord ({star_lord_of_csl}) has mixed significations {sl_sigs_sorted}, "
                f"but Sub-Lord ({cuspal_sub_lord_7}) provides pure support {sub_sigs_sorted}, "
                "clearing obstacles for fruition."
            ),
        )

    # K3: Star-Lord supports, Sub-Lord has mixed (supportive + denying) significations
    if sl_has_sup and sub_has_sup and sub_has_den:
        return KPPromiseDetail(
            verdict=PromiseVerdict.PROMISED,
            internal_modifier=KPInternalModifier.PROMISED_WITH_OBSTACLES,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-002",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation=(
                f"Star-Lord ({star_lord_of_csl}) supports marriage, but Sub-Lord ({cuspal_sub_lord_7}) "
                f"signifies both supportive and denying houses {sub_sigs_sorted}. "
                "Event fructifies after delays, disputes, or preliminary obstacles."
            ),
        )

    # K4: Star-Lord supports, Sub-Lord is purely neutral (neither supportive nor denying)
    if sl_has_sup and not sub_has_sup and not sub_has_den:
        return KPPromiseDetail(
            verdict=PromiseVerdict.PROMISED,
            internal_modifier=KPInternalModifier.PROMISED_DELAYED,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-002",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation=(
                f"Star-Lord ({star_lord_of_csl}) supports marriage, while Sub-Lord ({cuspal_sub_lord_7}) "
                f"is neutral ({sub_sigs_sorted}). Fruition is unimpeded by denial but delayed until strong Dasha periods."
            ),
        )

    # K5: Star-Lord has NO supportive houses, Sub-Lord has supportive houses
    # Engineering Policy Precedence: Sub-Lord cannot fructify what Star-Lord does not initiate
    if not sl_has_sup and sub_has_sup:
        return KPPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=KPInternalModifier.DENIED_AT_ROOT,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PREC-001",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation=(
                f"Star-Lord ({star_lord_of_csl}) signifies {sl_sigs_sorted} lacking houses 2, 7, 11. "
                "Matter is uninitiated at root; Sub-Lord cannot fructify what the Star-Lord does not offer."
            ),
        )

    # K6: Star-Lord supports, Sub-Lord signifies EXCLUSIVELY denying houses
    if sl_has_sup and not sub_has_sup and sub_has_den:
        return KPPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=KPInternalModifier.DENIED_AT_FRUITION,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-004",
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
            explanation=(
                f"Star-Lord ({star_lord_of_csl}) signifies supportive houses, but Sub-Lord ({cuspal_sub_lord_7}) "
                f"signifies exclusively denying houses {sub_sigs_sorted}. Fruition is blocked at the gate."
            ),
        )

    # K7 & K8: Star-Lord has NO supportive houses AND Sub-Lord has NO supportive houses
    if not sl_has_sup and not sub_has_sup:
        return KPPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=KPInternalModifier.DENIED_AT_ROOT,
            cuspal_sub_lord_7=cuspal_sub_lord_7,
            star_lord_of_csl=star_lord_of_csl,
            star_lord_significations=sl_sigs_sorted,
            sub_lord_significations=sub_sigs_sorted,
            is_csl_retrograde=is_csl_retro,
            is_star_lord_retrograde=is_star_retro,
            rule_id="KP-MARR-PROM-003",
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
            explanation=(
                f"Neither Star-Lord ({star_lord_of_csl}: {sl_sigs_sorted}) nor Sub-Lord ({cuspal_sub_lord_7}: {sub_sigs_sorted}) "
                "signifies supportive houses 2, 7, or 11. Marriage promise is absent."
            ),
        )

    # K9: Fallthrough / Defensive Indeterminate
    return KPPromiseDetail(
        verdict=PromiseVerdict.INDETERMINATE,
        internal_modifier=KPInternalModifier.INDETERMINATE_DATA,
        cuspal_sub_lord_7=cuspal_sub_lord_7,
        star_lord_of_csl=star_lord_of_csl,
        star_lord_significations=sl_sigs_sorted,
        sub_lord_significations=sub_sigs_sorted,
        is_csl_retrograde=is_csl_retro,
        is_star_lord_retrograde=is_star_retro,
        rule_id="KP-MARR-PROM-005",
        rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
        explanation="Signification patterns or input boundaries prevent a defensible KP promise determination.",
    )
