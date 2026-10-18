"""KP Event Prediction Engine - Scoring Service.

Computes participating lords, effective house weights, support/denial scores,
and coverage for a given period and event rule.

Deterministic rules:
1. Effective weight per house is the MAXIMUM weight across participating lords:
   L1=4, L2=3, L3=2, L4=1. Never sums the weights of the same house across lords.
2. Coverage = (count of distinct supporting houses covered) / (total supporting houses).
3. Mahadasha and Bhukti lords must both independently signify >= 1 supporting house
   to qualify for GREEN.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from .event_rules import EventRule
from .signification_normalizer import LEVEL_WEIGHTS, WEIGHT_TO_LEVEL, normalize_planet_name


@dataclass(frozen=True)
class HouseContribution:
    house: int
    level: str
    weight: int
    contributing_lord: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "house": self.house,
            "level": self.level,
            "weight": self.weight,
        }


@dataclass
class PeriodLordSignifications:
    mahadasha_lord: str
    bhukti_lord: str
    antara_lord: Optional[str] = None
    all_significations: Dict[str, Dict[int, str]] = field(default_factory=dict)


@dataclass
class PeriodScoringResult:
    event_name: str
    mahadasha_lord: str
    bhukti_lord: str
    antara_lord: Optional[str]
    effective_house_weights: Dict[int, int]
    effective_house_levels: Dict[int, str]
    support_score: int
    denial_score: int
    coverage: float
    supporting_houses: List[HouseContribution]
    denying_houses: List[HouseContribution]
    md_supports: bool
    bd_supports: bool
    antara_supports: Optional[bool]
    all_but_one_coverage: bool
    missing_supporting_houses: List[int]


def score_period_for_event(
    event: EventRule,
    md_lord: str,
    bd_lord: str,
    antara_lord: Optional[str],
    significations: Dict[str, Dict[int, str]],
) -> PeriodScoringResult:
    """Calculates deterministic support score, denial score, effective house weights,
    and coverage for an event under the participating planetary lords.
    """
    norm_md = normalize_planet_name(md_lord) or md_lord
    norm_bd = normalize_planet_name(bd_lord) or bd_lord
    norm_ad = normalize_planet_name(antara_lord) if antara_lord else None

    participating_lords = [norm_md, norm_bd]
    if norm_ad and norm_ad in significations:
        participating_lords.append(norm_ad)

    # Step 2: Calculate effective weight for each house across participating lords
    # Max weight wins; never add weights across lords for the same house
    effective_weights: Dict[int, int] = {}
    effective_levels: Dict[int, str] = {}
    lord_contributor_map: Dict[int, str] = {}

    for h in range(1, 13):
        max_wt = 0
        best_lvl = ""
        best_lord = ""
        for lord in participating_lords:
            lord_sigs = significations.get(lord, {})
            lvl = lord_sigs.get(h)
            if lvl and lvl in LEVEL_WEIGHTS:
                wt = LEVEL_WEIGHTS[lvl]
                if wt > max_wt:
                    max_wt = wt
                    best_lvl = lvl
                    best_lord = lord
        if max_wt > 0:
            effective_weights[h] = max_wt
            effective_levels[h] = best_lvl
            lord_contributor_map[h] = best_lord

    # Step 3: Compute support and denial scores
    supporting_list: List[HouseContribution] = []
    denying_list: List[HouseContribution] = []
    supp_score = 0
    den_score = 0

    for sh in event.supporting_houses:
        if sh in effective_weights:
            wt = effective_weights[sh]
            lvl = effective_levels[sh]
            supp_score += wt
            supporting_list.append(
                HouseContribution(
                    house=sh,
                    level=lvl,
                    weight=wt,
                    contributing_lord=lord_contributor_map.get(sh, ""),
                )
            )

    for dh in event.denying_houses:
        if dh in effective_weights:
            wt = effective_weights[dh]
            lvl = effective_levels[dh]
            den_score += wt
            denying_list.append(
                HouseContribution(
                    house=dh,
                    level=lvl,
                    weight=wt,
                    contributing_lord=lord_contributor_map.get(dh, ""),
                )
            )

    total_supp_houses = len(event.supporting_houses)
    covered_supp_count = len(supporting_list)
    coverage = covered_supp_count / total_supp_houses if total_supp_houses > 0 else 0.0

    missing_supp = [h for h in event.supporting_houses if h not in effective_weights]
    all_but_one = (covered_supp_count == total_supp_houses - 1) and (total_supp_houses > 1)

    # Step 4: Validate independent lord participation
    # Both Mahadasha lord and Bhukti lord must independently signify at least one supporting house
    md_sigs = significations.get(norm_md, {})
    bd_sigs = significations.get(norm_bd, {})
    ad_sigs = significations.get(norm_ad, {}) if norm_ad else {}

    md_supports = any(sh in md_sigs for sh in event.supporting_houses)
    bd_supports = any(sh in bd_sigs for sh in event.supporting_houses)
    ad_supports = any(sh in ad_sigs for sh in event.supporting_houses) if norm_ad else None

    # Sort contributions by house number
    supporting_list.sort(key=lambda c: c.house)
    denying_list.sort(key=lambda c: c.house)

    return PeriodScoringResult(
        event_name=event.name,
        mahadasha_lord=norm_md,
        bhukti_lord=norm_bd,
        antara_lord=norm_ad,
        effective_house_weights=effective_weights,
        effective_house_levels=effective_levels,
        support_score=supp_score,
        denial_score=den_score,
        coverage=coverage,
        supporting_houses=supporting_list,
        denying_houses=denying_list,
        md_supports=md_supports,
        bd_supports=bd_supports,
        antara_supports=ad_supports,
        all_but_one_coverage=all_but_one,
        missing_supporting_houses=missing_supp,
    )
