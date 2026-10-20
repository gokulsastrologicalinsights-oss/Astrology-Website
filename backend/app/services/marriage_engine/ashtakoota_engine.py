"""Orchestrator and aggregation service for the North Indian 36-Point Ashtakoota Matching."""

from typing import Dict, Any, List

from app.services.marriage_engine.models import (
    MarriageChartContext,
    KootaResult,
)
from app.services.marriage_engine.ashtakoota_rules import (
    evaluate_varna_koota,
    evaluate_vashya_koota,
    evaluate_tara_koota,
    evaluate_yoni_koota,
    evaluate_graha_maitri_koota,
    evaluate_gana_koota_ashtakoota,
    evaluate_bhakoot_koota,
    evaluate_nadi_koota,
)
from app.schemas.marriage import KootaDetailItem, AshtakootaSummary


def _koota_result_to_detail_item(res: KootaResult) -> KootaDetailItem:
    """Convert an internal KootaResult to an API-facing KootaDetailItem."""
    return KootaDetailItem(
        koota_id=res.koota_id,
        name_en=res.name_en,
        status=res.status.value,
        max_points=res.max_points,
        earned_points=res.earned_points,
        raw_calculation=res.raw_calculation,
        groom_input=res.groom_input,
        bride_input=res.bride_input,
        intermediate_calculation=res.intermediate_calculation,
        is_dosha_present=res.is_dosha_present,
        is_cancelled=res.is_cancelled,
        cancellation_reason=res.cancellation_reason,
        description=res.description,
        classical_reference=res.classical_reference,
        warnings=res.warnings,
    )


def evaluate_ashtakoota_matching(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
    minimum_threshold: float = 18.0,
) -> AshtakootaSummary:
    """Evaluate North Indian 36-Point Ashtakoota matching deterministically.

    Parameters
    ----------
    groom : MarriageChartContext
        Resolved horoscope context for the groom.
    bride : MarriageChartContext
        Resolved horoscope context for the bride.
    minimum_threshold : float, default 18.0
        Classical passing threshold out of 36.0 points.

    Returns
    -------
    AshtakootaSummary
        Complete breakdown of the 8 Kootas, total points scored out of 36.0,
        Nadi & Bhakoot Dosha statuses, and explanatory notes.
    """
    evaluators = [
        ("varna", evaluate_varna_koota),
        ("vashya", evaluate_vashya_koota),
        ("tara", evaluate_tara_koota),
        ("yoni", evaluate_yoni_koota),
        ("graha_maitri", evaluate_graha_maitri_koota),
        ("gana", evaluate_gana_koota_ashtakoota),
        ("bhakoot", evaluate_bhakoot_koota),
        ("nadi", evaluate_nadi_koota),
    ]

    kootas_dict: Dict[str, KootaDetailItem] = {}
    total_points = 0.0

    for key, eval_fn in evaluators:
        res: KootaResult = eval_fn(groom, bride)
        item = _koota_result_to_detail_item(res)
        kootas_dict[key] = item
        total_points += res.earned_points

    # Dosha checks
    nadi_item = kootas_dict.get("nadi")
    nadi_dosha_present = bool(nadi_item and nadi_item.is_dosha_present)
    nadi_dosha_cancelled = bool(nadi_item and nadi_item.is_cancelled)

    bhakoot_item = kootas_dict.get("bhakoot")
    bhakoot_dosha_present = bool(bhakoot_item and bhakoot_item.is_dosha_present)
    bhakoot_dosha_cancelled = bool(bhakoot_item and bhakoot_item.is_cancelled)

    is_threshold_met = total_points >= minimum_threshold

    summary_notes: List[str] = []

    # Explanatory notes
    summary_notes.append(
        f"Ashtakoota Aggregate: {total_points:.1f} / 36.0 points "
        f"({'Satisfies' if is_threshold_met else 'Does not satisfy'} traditional threshold of {minimum_threshold:.1f} pts)."
    )

    if nadi_dosha_present:
        if nadi_dosha_cancelled:
            summary_notes.append("Nadi Dosha detected but CANCELLED per classical Muhurta Chintamani exceptions.")
        else:
            summary_notes.append("CRITICAL: Active, uncancelled Nadi Dosha is present (0/8 pts). Traditional remediation advised.")
    else:
        summary_notes.append("Nadi Koota is clear (8/8 pts).")

    if bhakoot_dosha_present:
        if bhakoot_dosha_cancelled:
            summary_notes.append("Bhakoot Dosha detected but CANCELLED per classical sign lord exceptions.")
        else:
            summary_notes.append("CRITICAL: Active, uncancelled Bhakoot Dosha is present (0/7 pts).")
    else:
        summary_notes.append("Bhakoot Koota is clear (7/7 pts).")

    summary_notes.append(
        "Traditional note: The 36-point Ashtakoota score reflects North Indian compatibility conventions. "
        "A score >= 18 points is an indicator of alignment, not an absolute guarantee of marital outcome."
    )

    return AshtakootaSummary(
        kootas=kootas_dict,
        total_points=round(total_points, 2),
        max_points=36.0,
        minimum_threshold=minimum_threshold,
        is_threshold_met=is_threshold_met,
        nadi_dosha_present=nadi_dosha_present,
        nadi_dosha_cancelled=nadi_dosha_cancelled,
        bhakoot_dosha_present=bhakoot_dosha_present,
        bhakoot_dosha_cancelled=bhakoot_dosha_cancelled,
        summary_notes=summary_notes,
    )
