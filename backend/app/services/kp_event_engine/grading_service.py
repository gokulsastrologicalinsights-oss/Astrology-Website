"""KP Event Prediction Engine - Grading Service.

Implements deterministic evaluation of GREEN (STRONG), ORANGE (MODERATE),
and RED (WEAK) grades, CSL arbiter caps/downgrades, and retrograde adjustments.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .event_rules import EventRule
from .scoring_service import PeriodScoringResult
from .signification_normalizer import LEVEL_WEIGHTS, normalize_planet_name


@dataclass
class GradeResult:
    event_name: str
    original_color: str   # "green", "orange", "red"
    final_color: str      # "green", "orange", "red"
    original_grade: str   # "STRONG", "MODERATE", "WEAK"
    grade: str            # "STRONG", "MODERATE", "WEAK"
    support_score: int
    denial_score: int
    coverage: float
    denied: bool
    retrograde_note: Optional[str]
    csl_adjustment: Optional[str]
    csl_details: Optional[Dict[str, Any]]
    hint: str
    supporting_houses: List[Dict[str, Any]]
    denying_houses: List[Dict[str, Any]]
    missing_supporting_houses: List[int]
    scoring_metadata: Dict[str, Any]


def grade_scored_event(
    event: EventRule,
    scored: PeriodScoringResult,
    csl_map: Optional[Dict[int, str]] = None,
    all_significations: Optional[Dict[str, Dict[int, str]]] = None,
    retrograde_status: Optional[Dict[str, bool]] = None,
    downgrade_on_antara_retrograde: bool = True,
    missing_house_l3_l4_only: bool = False,
) -> GradeResult:
    """Applies KP grading rules with explicit precedence and adjustments."""
    supp = scored.support_score
    den = scored.denial_score
    cov = scored.coverage
    has_h11 = any(h.house == 11 for h in scored.supporting_houses)
    total_supp_count = len(event.supporting_houses)
    covered_supp_count = len(scored.supporting_houses)

    # 1. Evaluate GREEN eligibility
    # Condition 1: Coverage 100%, OR all-but-one where missing house has only L3/L4 evidence
    coverage_ok_for_green = (cov >= 1.0) or (scored.all_but_one_coverage and missing_house_l3_l4_only)

    is_green = (
        coverage_ok_for_green
        and (supp > 2 * den)
        and scored.md_supports
        and scored.bd_supports
        and (not event.is_gain_type or has_h11)
    )

    # 2. Evaluate ORANGE eligibility (if not GREEN)
    is_orange = False
    if not is_green:
        is_orange = (
            (cov >= 0.60)
            and (supp > den)
            and (covered_supp_count >= 2)
        )

    # 3. Initial Base Color & Grade
    if is_green:
        base_color = "green"
        base_grade = "STRONG"
    elif is_orange:
        base_color = "orange"
        base_grade = "MODERATE"
    else:
        base_color = "red"
        base_grade = "WEAK"

    # Denied flag: denial strictly exceeds 1.5 * support
    is_denied = (den > 1.5 * supp)

    # 4. Cusp Sub-Lord (CSL) Adjustment
    csl_adjustment_note: Optional[str] = None
    csl_details: Optional[Dict[str, Any]] = None
    final_color = base_color

    primary_cusp = event.primary_cusp
    csl_planet = csl_map.get(primary_cusp) if csl_map else None

    if csl_planet and all_significations and csl_planet in all_significations:
        csl_sigs = all_significations[csl_planet]
        csl_supp = sum(LEVEL_WEIGHTS[lvl] for h, lvl in csl_sigs.items() if h in event.supporting_houses and lvl in LEVEL_WEIGHTS)
        csl_den = sum(LEVEL_WEIGHTS[lvl] for h, lvl in csl_sigs.items() if h in event.denying_houses and lvl in LEVEL_WEIGHTS)

        csl_details = {
            "primary_cusp": primary_cusp,
            "csl_planet": csl_planet,
            "csl_support_score": csl_supp,
            "csl_denial_score": csl_den,
        }

        # Clear denial: CSL signifies denying houses with NO supporting houses (csl_supp == 0 and csl_den > 0),
        # or denying score is at least double supporting score (csl_den >= 2 * csl_supp)
        csl_clearly_denies = (csl_den > 0 and csl_supp == 0) or (csl_supp > 0 and csl_den >= 2 * csl_supp)
        # Mainly denies: CSL denying score is strictly greater than supporting score (csl_den > csl_supp)
        csl_mainly_denies = (csl_den > csl_supp)

        if csl_clearly_denies:
            if final_color != "red":
                final_color = "red"
                csl_adjustment_note = f"CSL ({csl_planet}) of Cusp {primary_cusp} clearly denies event ({csl_den} vs {csl_supp}); downgraded to RED."
        elif csl_mainly_denies:
            if final_color == "green":
                final_color = "orange"
                csl_adjustment_note = f"CSL ({csl_planet}) of Cusp {primary_cusp} mainly signifies denying houses ({csl_den} vs {csl_supp}); capped at ORANGE."
        # If csl_supp >= csl_den (including tie), no downgrade applied

    # 5. Retrograde Adjustment
    retro_note: Optional[str] = None
    retro_lords: List[str] = []

    participating_lords = [scored.mahadasha_lord, scored.bhukti_lord]
    if scored.antara_lord:
        participating_lords.append(scored.antara_lord)

    if retrograde_status:
        for lord in participating_lords:
            norm_l = normalize_planet_name(lord)
            if norm_l and retrograde_status.get(norm_l, False):
                retro_lords.append(norm_l)

    if retro_lords:
        retro_note = "delay possible"
        # Determine whether retrograde lords trigger downgrade
        should_downgrade = False
        if any(l in retro_lords for l in [scored.mahadasha_lord, scored.bhukti_lord]):
            should_downgrade = True
        elif scored.antara_lord in retro_lords and downgrade_on_antara_retrograde:
            should_downgrade = True

        if should_downgrade and final_color == "green":
            final_color = "orange"

    # Map final color to grade label
    grade_label_map = {
        "green": "STRONG",
        "orange": "MODERATE",
        "red": "WEAK",
    }
    final_grade = grade_label_map[final_color]

    # Generate hint (<= 20 words)
    hint = event.get_hint(final_color)
    if retro_note and "delay possible" not in hint.lower():
        # Append delay possible note if not already mentioned
        hint = f"{hint} (Delay possible)."

    scoring_metadata = {
        "md_supports": scored.md_supports,
        "bd_supports": scored.bd_supports,
        "antara_supports": scored.antara_supports,
        "covered_supporting_count": covered_supp_count,
        "total_supporting_count": total_supp_count,
        "has_house_11": has_h11,
        "is_gain_type": event.is_gain_type,
        "retrograde_lords": retro_lords,
        "missing_supporting_houses": scored.missing_supporting_houses,
        "effective_house_weights": scored.effective_house_weights,
    }

    return GradeResult(
        event_name=event.name,
        original_color=base_color,
        final_color=final_color,
        original_grade=base_grade,
        grade=final_grade,
        support_score=supp,
        denial_score=den,
        coverage=cov,
        denied=is_denied,
        retrograde_note=retro_note,
        csl_adjustment=csl_adjustment_note,
        csl_details=csl_details,
        hint=hint,
        supporting_houses=[c.to_dict() for c in scored.supporting_houses],
        denying_houses=[c.to_dict() for c in scored.denying_houses],
        missing_supporting_houses=scored.missing_supporting_houses,
        scoring_metadata=scoring_metadata,
    )
