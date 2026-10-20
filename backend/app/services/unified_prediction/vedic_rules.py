"""Isolated Vedic Marriage Rulebook and Decision Logic.

This module evaluates the Vedic natal marriage promise across D1 Rasi and D9
Navamsa charts, evaluating the 7th house, 7th lord, Venus (Kalatrakaraka), and
Kuja Dosha with classical cancellations.

Classical Citations & Provenance:
- 7th house & lord effects: Brihat Parashara Hora Shastra (BPHS), Ch. 18. [SOURCE_VERIFIED]
- Venus Kalatrakaraka dignity: Phaladeepika, Ch. 10. [SOURCE_VERIFIED]
- Planetary combustion (asta): BPHS, Ch. 3, slokas 49-54. [SOURCE_VERIFIED]
- Navamsa (D9) verification: Jataka Parijata, Ch. 14. [SOURCE_VERIFIED]
- Kuja Dosha & cancellations: Muhurta Chintamani, Vivaha Prakarana. [SOURCE_VERIFIED]
- Compound Categorical Denial Gate: [PROJECT_ENGINEERING_POLICY]
"""

from __future__ import annotations

import math
from typing import Dict, Any, List, Optional
from app.services.varga_engine import (
    calculate_navamsa_from_longitude,
    SIGN_LORDS,
    SIGN_NAMES_EN,
)
from app.services.unified_prediction.models import (
    VedicPromiseDetail,
    VedicInternalModifier,
    PromiseVerdict,
    RuleProvenanceTag,
)


# Natural benefics and malefics
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}

# Combustion limits in degrees from Sun (BPHS Ch. 3)
COMBUSTION_LIMIT_VENUS_DIRECT = 8.0
COMBUSTION_LIMIT_VENUS_RETRO = 10.0


def calculate_house_from_lagna(planet_sign_idx: int, lagna_sign_idx: int) -> int:
    """Calculate 1-indexed house from Lagna using Vedic Whole Sign system."""
    return ((planet_sign_idx - lagna_sign_idx) % 12) + 1


def is_combust(
    planet_lon: float,
    sun_lon: float,
    limit_deg: float,
) -> bool:
    """Check if planet is combust within limit_deg from Sun."""
    diff = abs((planet_lon - sun_lon + 180.0) % 360.0 - 180.0)
    return diff <= limit_deg


def evaluate_vedic_marriage_promise(
    planets: Dict[str, Dict[str, Any]],
    ascendant_degree: float,
) -> VedicPromiseDetail:
    """Evaluate Vedic natal marriage promise deterministically.
    
    Parameters
    ----------
    planets : dict
        Dict mapping planet name to dict containing:
        - "longitude": float (0-360)
        - "sign_index": int (1-12)
        - "is_retrograde": bool (optional, defaults to False)
    ascendant_degree : float
        Sidereal Ascendant degree (0-360).
    """
    lagna_sign_idx = int((ascendant_degree % 360.0) // 30.0) + 1
    
    # 7th House D1
    seventh_house_sign_idx = ((lagna_sign_idx + 6 - 1) % 12) + 1
    seventh_house_sign_name = SIGN_NAMES_EN[seventh_house_sign_idx]
    seventh_lord = SIGN_LORDS[seventh_house_sign_idx]
    
    # 7th Lord Placement
    seventh_lord_pos = planets.get(seventh_lord)
    if seventh_lord_pos is None:
        return VedicPromiseDetail(
            verdict=PromiseVerdict.INDETERMINATE,
            internal_modifier=VedicInternalModifier.INDETERMINATE_DATA,
            seventh_lord_d1=seventh_lord,
            seventh_house_sign_d1=seventh_house_sign_name,
            seventh_lord_house_d1=0,
            venus_combustion=False,
            venus_debilitation=False,
            venus_dusthana=False,
            kuja_dosha_present=False,
            kuja_dosha_cancelled=False,
            d9_seventh_sign="",
            d9_seventh_lord="",
            d9_venus_sign="",
            d9_afflicted=False,
            compound_denial_gates_met=0,
            rule_id="VED-MARR-ERR-001",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation=f"Calculation missing data for 7th lord {seventh_lord}.",
        )
        
    seventh_lord_sign_idx = seventh_lord_pos["sign_index"]
    seventh_lord_house = calculate_house_from_lagna(seventh_lord_sign_idx, lagna_sign_idx)
    is_seventh_lord_in_dusthana = seventh_lord_house in (6, 8, 12)
    
    # Venus Evaluation
    venus_pos = planets.get("Venus")
    sun_pos = planets.get("Sun")
    
    venus_combust = False
    venus_debilitated = False
    venus_in_dusthana = False
    
    if venus_pos is not None:
        v_lon = venus_pos["longitude"]
        v_sign = venus_pos["sign_index"]
        v_house = calculate_house_from_lagna(v_sign, lagna_sign_idx)
        venus_debilitated = (v_sign == 6)  # Virgo is debilitation sign
        venus_in_dusthana = (v_house in (6, 8, 12))
        
        if sun_pos is not None:
            s_lon = sun_pos["longitude"]
            is_retro = venus_pos.get("is_retrograde", False)
            limit = COMBUSTION_LIMIT_VENUS_RETRO if is_retro else COMBUSTION_LIMIT_VENUS_DIRECT
            venus_combust = is_combust(v_lon, s_lon, limit)

    # Kuja Dosha Evaluation
    mars_pos = planets.get("Mars")
    kuja_present = False
    kuja_cancelled = False
    if mars_pos is not None:
        m_sign = mars_pos["sign_index"]
        m_house = calculate_house_from_lagna(m_sign, lagna_sign_idx)
        # Mars in 1, 2, 4, 7, 8, 12 from Lagna
        if m_house in (1, 2, 4, 7, 8, 12):
            kuja_present = True
            # Classical cancellations (Muhurta Chintamani)
            # 1. Mars in own sign (Aries/Scorpio) or exaltation (Capricorn)
            if m_sign in (1, 8, 10):
                kuja_cancelled = True
            # 2. Jupiter aspect or conjunction
            jup_pos = planets.get("Jupiter")
            if jup_pos is not None:
                j_sign = jup_pos["sign_index"]
                j_house_from_mars = calculate_house_from_lagna(j_sign, m_sign)
                # Jupiter aspects 5th, 7th, 9th from its sign (and 1st = conjunction)
                if j_house_from_mars in (1, 5, 7, 9):
                    kuja_cancelled = True

    # Navamsa D9 Evaluation
    d9_asc = calculate_navamsa_from_longitude(ascendant_degree)
    d9_lagna_sign_idx = d9_asc["d9_sign_index"]
    d9_seventh_sign_idx = ((d9_lagna_sign_idx + 6 - 1) % 12) + 1
    d9_seventh_sign_name = SIGN_NAMES_EN[d9_seventh_sign_idx]
    d9_seventh_lord = SIGN_LORDS[d9_seventh_sign_idx]
    
    d9_venus_sign_name = ""
    d9_venus_sign_idx = 0
    if venus_pos is not None:
        d9_venus = calculate_navamsa_from_longitude(venus_pos["longitude"])
        d9_venus_sign_idx = d9_venus["d9_sign_index"]
        d9_venus_sign_name = d9_venus["d9_sign_name"]
        
    d9_7th_lord_pos = planets.get(d9_seventh_lord)
    d9_7th_lord_in_dusthana = False
    if d9_7th_lord_pos is not None:
        d9_7th_lord_varga = calculate_navamsa_from_longitude(d9_7th_lord_pos["longitude"])
        d9_7th_lord_sign = d9_7th_lord_varga["d9_sign_index"]
        d9_house = calculate_house_from_lagna(d9_7th_lord_sign, d9_lagna_sign_idx)
        d9_7th_lord_in_dusthana = d9_house in (6, 8, 12)

    d9_afflicted = d9_7th_lord_in_dusthana or (d9_venus_sign_idx == 6)  # D9 7th lord dusthana or Venus debilitated in D9

    # -----------------------------------------------------------------------
    # Compound Categorical Denial Gate (VED-MARR-PROM-006)
    # [PROJECT_ENGINEERING_POLICY]
    # Requires 3 concurrent severe failures so no single affliction denies
    # -----------------------------------------------------------------------
    gate_1 = is_seventh_lord_in_dusthana
    gate_2 = venus_combust and (venus_debilitated or venus_in_dusthana)
    gate_3 = d9_afflicted
    gates_met = sum([gate_1, gate_2, gate_3])

    if gates_met == 3:
        # Full compound categorical denial
        return VedicPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=VedicInternalModifier.DENIED_COMPOUND,
            seventh_lord_d1=seventh_lord,
            seventh_house_sign_d1=seventh_house_sign_name,
            seventh_lord_house_d1=seventh_lord_house,
            venus_combustion=venus_combust,
            venus_debilitation=venus_debilitated,
            venus_dusthana=venus_in_dusthana,
            kuja_dosha_present=kuja_present,
            kuja_dosha_cancelled=kuja_cancelled,
            d9_seventh_sign=d9_seventh_sign_name,
            d9_seventh_lord=d9_seventh_lord,
            d9_venus_sign=d9_venus_sign_name,
            d9_afflicted=d9_afflicted,
            compound_denial_gates_met=gates_met,
            rule_id="VED-MARR-PROM-006",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation=(
                f"Severe concurrent compound affliction across 3 independent factors: "
                f"7th lord ({seventh_lord}) in dusthana ({seventh_lord_house}), "
                "Venus combust and debilitated/dusthana, and D9 Navamsa afflicted. "
                "Categorical denial indicated under Vedic compound gate."
            ),
        )

    has_any_affliction = (
        gates_met > 0
        or venus_combust
        or venus_debilitated
        or venus_in_dusthana
        or is_seventh_lord_in_dusthana
        or (kuja_present and not kuja_cancelled)
        or d9_afflicted
    )

    if has_any_affliction:
        # Afflictions present but do not meet triple compound denial gate -> Promised with obstacles
        affliction_notes = []
        if gate_1:
            affliction_notes.append(f"7th lord in {seventh_lord_house}th house")
        if venus_combust:
            affliction_notes.append("Venus combust")
        if venus_debilitated:
            affliction_notes.append("Venus debilitated")
        if venus_in_dusthana:
            affliction_notes.append("Venus in dusthana")
        if kuja_present and not kuja_cancelled:
            affliction_notes.append("Uncancelled Kuja Dosha")
        if d9_afflicted:
            affliction_notes.append("Navamsa D9 7th/Venus afflicted")

        return VedicPromiseDetail(
            verdict=PromiseVerdict.PROMISED,
            internal_modifier=VedicInternalModifier.PROMISED_WITH_OBSTACLES,
            seventh_lord_d1=seventh_lord,
            seventh_house_sign_d1=seventh_house_sign_name,
            seventh_lord_house_d1=seventh_lord_house,
            venus_combustion=venus_combust,
            venus_debilitation=venus_debilitated,
            venus_dusthana=venus_in_dusthana,
            kuja_dosha_present=kuja_present,
            kuja_dosha_cancelled=kuja_cancelled,
            d9_seventh_sign=d9_seventh_sign_name,
            d9_seventh_lord=d9_seventh_lord,
            d9_venus_sign=d9_venus_sign_name,
            d9_afflicted=d9_afflicted,
            compound_denial_gates_met=gates_met,
            rule_id="VED-MARR-PROM-002",
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
            explanation=(
                "Marriage is promised with delay or obstacles. Classical afflictions observed: "
                + ", ".join(affliction_notes)
                + ". Afflictions do not satisfy the compound denial criteria."
            ),
        )

    # Clean favorable promise
    return VedicPromiseDetail(
        verdict=PromiseVerdict.PROMISED,
        internal_modifier=VedicInternalModifier.PROMISED_FAVORABLE,
        seventh_lord_d1=seventh_lord,
        seventh_house_sign_d1=seventh_house_sign_name,
        seventh_lord_house_d1=seventh_lord_house,
        venus_combustion=venus_combust,
        venus_debilitation=venus_debilitated,
        venus_dusthana=venus_in_dusthana,
        kuja_dosha_present=kuja_present,
        kuja_dosha_cancelled=kuja_cancelled,
        d9_seventh_sign=d9_seventh_sign_name,
        d9_seventh_lord=d9_seventh_lord,
        d9_venus_sign=d9_venus_sign_name,
        d9_afflicted=d9_afflicted,
        compound_denial_gates_met=gates_met,
        rule_id="VED-MARR-PROM-001",
        rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
        explanation=(
            f"Favorable marriage promise: 7th lord {seventh_lord} placed in auspicious "
            f"{seventh_lord_house}th house, Venus uncombust and dignified, and D9 Navamsa clear."
        ),
    )
