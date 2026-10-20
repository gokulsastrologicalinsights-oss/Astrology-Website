"""Orchestrator and aggregation service for Traditional Tamil 10 Poruthams."""

from typing import Dict, Any, List

from app.services.marriage_engine.models import (
    MarriageChartContext,
    PoruthamResult,
    PoruthamStatus,
    PoruthamGrade,
)
from app.services.marriage_engine.porutham_rules import (
    evaluate_dina_porutham,
    evaluate_gana_porutham,
    evaluate_mahendra_porutham,
    evaluate_sthree_deergha_porutham,
    evaluate_yoni_porutham,
    evaluate_rasi_porutham,
    evaluate_rasi_adhipathi_porutham,
    evaluate_vasya_porutham,
    evaluate_rajju_porutham,
    evaluate_vedha_porutham,
)
from app.schemas.marriage import PoruthamDetailItem, TamilPoruthamSummary


def _result_to_detail_item(res: PoruthamResult) -> PoruthamDetailItem:
    """Convert an internal PoruthamResult to an API-facing PoruthamDetailItem."""
    grade_str = res.grade.value if res.grade else "Varjya" if res.status == PoruthamStatus.FAIL else "Uthama"
    return PoruthamDetailItem(
        rule_id=res.rule_id,
        name_en=res.name_en,
        name_ta=res.name_ta,
        status=res.status.value,
        grade=grade_str,
        score=res.score,
        max_score=res.max_score,
        is_favorable=res.is_favorable,
        groom_input=res.groom_input,
        bride_input=res.bride_input,
        intermediate_calculation=res.intermediate_calculation,
        counting_direction=res.counting_direction,
        applied_acceptance_criteria=res.applied_acceptance_criteria,
        source_and_version=res.source_and_version,
        description=res.explanation_en,
        description_tamil=res.explanation_ta,
        classical_reference=res.source_and_version,
        warnings=res.warnings,
    )


def evaluate_tamil_10_poruthams(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> TamilPoruthamSummary:
    """Evaluate all 10 Traditional Tamil Poruthams deterministically.

    Parameters
    ----------
    groom : MarriageChartContext
        Resolved horoscope context for the groom.
    bride : MarriageChartContext
        Resolved horoscope context for the bride.

    Returns
    -------
    TamilPoruthamSummary
        Complete breakdown of the 10 Poruthams, raw and earned scores, Rajju & Vedha status,
        and explanatory summary notes.
    """
    evaluators = [
        ("dina", evaluate_dina_porutham),
        ("gana", evaluate_gana_porutham),
        ("mahendra", evaluate_mahendra_porutham),
        ("sthree_deergha", evaluate_sthree_deergha_porutham),
        ("yoni", evaluate_yoni_porutham),
        ("rasi", evaluate_rasi_porutham),
        ("rasi_adhipathi", evaluate_rasi_adhipathi_porutham),
        ("vasya", evaluate_vasya_porutham),
        ("rajju", evaluate_rajju_porutham),
        ("vedha", evaluate_vedha_porutham),
    ]

    poruthams_dict: Dict[str, PoruthamDetailItem] = {}
    total_score = 0.0

    for key, eval_fn in evaluators:
        res: PoruthamResult = eval_fn(groom, bride)
        item = _result_to_detail_item(res)
        poruthams_dict[key] = item
        total_score += res.score

    # Status of Maha Poruthams
    rajju_item = poruthams_dict.get("rajju")
    rajju_status = rajju_item.status if rajju_item else "FAIL"

    vedha_item = poruthams_dict.get("vedha")
    vedha_status = vedha_item.status if vedha_item else "FAIL"

    # Classical Tamil Aggregate Verdict
    if total_score >= 7.0:
        aggregate_verdict = "Uthama"
    elif total_score >= 5.0:
        aggregate_verdict = "Madhyama"
    else:
        aggregate_verdict = "Adhama"

    summary_notes: List[str] = []
    if rajju_status == "FAIL":
        summary_notes.append("CRITICAL: Rajju Dosha (Rajju Thatu) is present. In classical Tamil tradition, Rajju has no cancellation.")
    if vedha_status == "FAIL":
        summary_notes.append("CRITICAL: Mutual Vedha affliction is present between the birth stars.")
    if rajju_status == "PASS" and vedha_status == "PASS":
        summary_notes.append("Foundational Maha Poruthams (Rajju and Vedha) are both satisfied.")

    summary_notes.append(
        f"Tamil 10 Porutham score: {total_score:.1f} / 10.0 (Grade: {aggregate_verdict}). "
        "Astrological compatibility analysis highlights traditional harmony indicators; it is an interpretive advisory tool rather than a fatalistic certainty."
    )

    return TamilPoruthamSummary(
        poruthams=poruthams_dict,
        total_score=round(total_score, 2),
        max_score=10.0,
        aggregate_verdict=aggregate_verdict,
        rajju_status=rajju_status,
        vedha_status=vedha_status,
        summary_notes=summary_notes,
    )
