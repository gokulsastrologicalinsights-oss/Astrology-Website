"""Read-only adapter and evaluator for KP Second-Marriage Rules.

Consumes validated canonical KP chart outputs (KpResponse, dict, or existing adapters)
without mutating input objects or modifying any database records.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from app.schemas.kp import KpResponse
from app.services.second_marriage_rules.models import (
    EventEngineComparisonResult,
    RuleEvaluationStatus,
    SecondMarriageAnalysisResult,
    SecondMarriageRuleResult,
    SecondMarriageSummary,
    SummaryVerdict,
)
from app.services.second_marriage_rules.rules import (
    RULE_1_ID,
    RULE_2_ID,
    RULE_3_ID,
    evaluate_rule_1,
    evaluate_rule_2,
    evaluate_rule_3,
    normalize_planet_name,
)


# ---------------------------------------------------------------------------
# Read-Only Chart Adapter
# ---------------------------------------------------------------------------

class AdaptedKpChartData:
    """Normalized, immutable snapshot of cusp, planet, and significator data."""

    def __init__(
        self,
        cusp_sub_lords: Dict[int, str],
        planet_signs: Dict[str, str],
        planet_significations: Dict[str, List[int]],
        metadata: Dict[str, Any],
    ) -> None:
        self.cusp_sub_lords = cusp_sub_lords
        self.planet_signs = planet_signs
        self.planet_significations = planet_significations
        self.metadata = metadata


def adapt_kp_chart_data(
    chart_input: Union[KpResponse, Dict[str, Any]],
) -> AdaptedKpChartData:
    """Extracts cusps, planetary positions, and 4-tier significators from KP chart data.
    
    Operates in pure read-only mode without mutating the input argument.
    """
    if chart_input is None:
        raise ValueError("Cannot adapt None: KP chart input is required.")

    # 1. Normalize dictionary or Pydantic model
    if isinstance(chart_input, KpResponse):
        raw: Dict[str, Any] = chart_input.model_dump()
    elif isinstance(chart_input, dict):
        # Work on a shallow copy of the dict to guarantee non-mutation
        raw = dict(chart_input)
    else:
        raise TypeError(f"Unsupported KP chart input type: {type(chart_input).__name__}")

    # If wrapped in calculation_result or nested kp
    if "calculation_result" in raw and isinstance(raw["calculation_result"], dict):
        raw = raw["calculation_result"].get("kp", raw)
    elif "kp" in raw and isinstance(raw["kp"], dict):
        raw = raw["kp"]

    # 2. Extract Cuspal Sub-Lords (1..12)
    cusp_sub_lords: Dict[int, str] = {}
    cusps_list = raw.get("cuspal_analysis") or raw.get("cusps") or []
    if isinstance(cusps_list, list):
        for c in cusps_list:
            if isinstance(c, dict):
                h = c.get("house")
                sl = c.get("sub_lord")
                if h is not None and sl:
                    try:
                        cusp_sub_lords[int(h)] = str(sl).strip().title()
                    except (ValueError, TypeError):
                        continue

    # 3. Extract Planetary Deposited Signs
    planet_signs: Dict[str, str] = {}
    planets_data = raw.get("planetary_positions") or raw.get("planets") or []
    if isinstance(planets_data, list):
        for p in planets_data:
            if isinstance(p, dict):
                p_name = p.get("planet")
                sign = p.get("sign_name") or p.get("sign")
                if p_name and sign:
                    planet_signs[str(p_name).strip().title()] = str(sign).strip().title()
    elif isinstance(planets_data, dict):
        for p_name, p_info in planets_data.items():
            if isinstance(p_info, dict):
                sign = p_info.get("sign_name") or p_info.get("sign")
                if sign:
                    planet_signs[str(p_name).strip().title()] = str(sign).strip().title()

    # 4. Extract Planet House Significations (ABCD Union)
    planet_significations: Dict[str, List[int]] = {}

    # 4a. Check significators list
    sigs_list = raw.get("significators")
    if isinstance(sigs_list, list):
        for item in sigs_list:
            if isinstance(item, dict):
                p_name = item.get("planet")
                houses = item.get("signified_houses")
                if p_name and isinstance(houses, list):
                    p_norm = str(p_name).strip().title()
                    valid_h = sorted(list({int(h) for h in houses if str(h).isdigit() and 1 <= int(h) <= 12}))
                    planet_significations[p_norm] = valid_h

    # 4b. Check house_significators 4-tier aggregation if significators was empty
    if not planet_significations and "house_significators" in raw:
        hs_data = raw.get("house_significators")
        accum: Dict[str, Set[int]] = {}
        if isinstance(hs_data, list):
            for h_entry in hs_data:
                if isinstance(h_entry, dict):
                    h_num = h_entry.get("house")
                    if h_num is not None:
                        all_p = (
                            h_entry.get("level_a", [])
                            + h_entry.get("level_b", [])
                            + h_entry.get("level_c", [])
                            + h_entry.get("level_d", [])
                        )
                        for p in all_p:
                            p_norm = str(p).strip().title()
                            accum.setdefault(p_norm, set()).add(int(h_num))
        elif isinstance(hs_data, dict):
            for h_str, h_entry in hs_data.items():
                if isinstance(h_entry, dict) and str(h_str).isdigit():
                    h_num = int(h_str)
                    all_p = (
                        h_entry.get("level_a", [])
                        + h_entry.get("level_b", [])
                        + h_entry.get("level_c", [])
                        + h_entry.get("level_d", [])
                    )
                    for p in all_p:
                        p_norm = str(p).strip().title()
                        accum.setdefault(p_norm, set()).add(h_num)

        if accum:
            planet_significations = {p: sorted(list(hs)) for p, hs in accum.items()}

    # 4c. Fallback to direct planet_significations dict
    if not planet_significations and "planet_significations" in raw:
        ps_dict = raw.get("planet_significations")
        if isinstance(ps_dict, dict):
            for p, hs in ps_dict.items():
                if isinstance(hs, (list, set)):
                    planet_significations[str(p).strip().title()] = sorted(list({int(h) for h in hs if str(h).isdigit()}))

    # 5. Extract safe metadata without sensitive personal information
    meta_raw = raw.get("metadata") or {}
    metadata: Dict[str, Any] = {
        "ayanamsa_name": meta_raw.get("ayanamsa_name", "KP"),
        "ayanamsa_id": meta_raw.get("ayanamsa_id", 1),
        "house_system_name": meta_raw.get("house_system_name", "Placidus"),
        "engine": meta_raw.get("engine", "kpastro (Swiss Ephemeris / KP)"),
    }

    return AdaptedKpChartData(
        cusp_sub_lords=cusp_sub_lords,
        planet_signs=planet_signs,
        planet_significations=planet_significations,
        metadata=metadata,
    )


# ---------------------------------------------------------------------------
# Evaluator Pipeline
# ---------------------------------------------------------------------------

def evaluate_second_marriage_rules(
    chart_input: Union[KpResponse, Dict[str, Any]],
) -> SecondMarriageAnalysisResult:
    """Evaluates the three isolated KP second-marriage rules against a KP chart.
    
    Deterministic, side-effect-free, and non-mutating.
    """
    adapted = adapt_kp_chart_data(chart_input)

    # 1. Rule 1: 7th Cusp Sub-Lord
    csl_7 = adapted.cusp_sub_lords.get(7)
    deposited_sign_7 = adapted.planet_signs.get(csl_7) if csl_7 else None
    sigs_7 = adapted.planet_significations.get(csl_7) if (csl_7 and csl_7 in adapted.planet_significations) else None
    res_1 = evaluate_rule_1(
        sub_lord=csl_7,
        deposited_sign=deposited_sign_7,
        significations=sigs_7,
    )

    # 2. Rule 2: 2nd Cusp Sub-Lord
    csl_2 = adapted.cusp_sub_lords.get(2)
    sigs_2 = adapted.planet_significations.get(csl_2) if (csl_2 and csl_2 in adapted.planet_significations) else None
    res_2 = evaluate_rule_2(
        sub_lord=csl_2,
        significations=sigs_2,
    )

    # 3. Rule 3: 9th Cusp Sub-Lord
    csl_9 = adapted.cusp_sub_lords.get(9)
    sigs_9 = adapted.planet_significations.get(csl_9) if (csl_9 and csl_9 in adapted.planet_significations) else None
    res_3 = evaluate_rule_3(
        sub_lord=csl_9,
        significations=sigs_9,
    )

    # 4. Rules Summary Aggregation
    rules_map = {
        "rule_1": res_1,
        "rule_2": res_2,
        "rule_3": res_3,
    }

    passed = [r.rule_id for r in rules_map.values() if r.status == RuleEvaluationStatus.PASS]
    failed = [r.rule_id for r in rules_map.values() if r.status == RuleEvaluationStatus.FAIL]
    indet = [r.rule_id for r in rules_map.values() if r.status == RuleEvaluationStatus.INDETERMINATE]

    summary_text = (
        f"Evaluated 3 isolated KP second-marriage rules: "
        f"{len(passed)} passed ({', '.join(passed) or 'none'}), "
        f"{len(failed)} failed ({', '.join(failed) or 'none'}), "
        f"{len(indet)} indeterminate ({', '.join(indet) or 'none'})."
    )

    summary = SecondMarriageSummary(
        verdict_label=SummaryVerdict.RULES_SUMMARY_ONLY,
        passed_rules=passed,
        failed_rules=failed,
        indeterminate_rules=indet,
        summary_text=summary_text,
    )

    return SecondMarriageAnalysisResult(
        rules=rules_map,
        summary=summary,
        chart_metadata=adapted.metadata,
    )


# ---------------------------------------------------------------------------
# Existing Event Engine Comparison Helper
# ---------------------------------------------------------------------------

def compare_with_existing_event_engine(
    analysis_result: SecondMarriageAnalysisResult,
    chart_input: Union[KpResponse, Dict[str, Any]],
) -> EventEngineComparisonResult:
    """Compares the isolated 3-rule outcomes with the existing event engine's verdict.
    
    Calls `evaluate_event_promise` in read-only mode if available, and documents
    the architectural causes for any divergence in verdicts.
    """
    raw_dict: Dict[str, Any] = (
        chart_input.model_dump() if isinstance(chart_input, KpResponse) else dict(chart_input)
    )
    if "calculation_result" in raw_dict and isinstance(raw_dict["calculation_result"], dict):
        raw_dict = raw_dict["calculation_result"].get("kp", raw_dict)
    elif "kp" in raw_dict and isinstance(raw_dict["kp"], dict):
        raw_dict = raw_dict["kp"]

    # Normalize chart format for evaluate_event_promise
    chart_for_engine = {
        "cusps": raw_dict.get("cuspal_analysis") or raw_dict.get("cusps") or [],
        "planets": raw_dict.get("planetary_positions") or raw_dict.get("planets") or [],
        "house_significators": raw_dict.get("house_significators") or [],
        "significators": raw_dict.get("significators") or [],
    }

    event_verdict: Optional[str] = None
    supporting_hits: List[int] = []
    denying_hits: List[int] = []

    try:
        from app.services.kp_prediction_service import _get_event_rule, evaluate_event_promise
        rule = _get_event_rule("Second marriage")
        promise = evaluate_event_promise(chart_for_engine, rule)
        event_verdict = promise.promise_status
        supporting_hits = promise.supporting_hits
        denying_hits = promise.denying_hits
    except Exception as exc:
        event_verdict = f"Event engine comparison unavailable: {str(exc)}"

    divergence_reasons = [
        "Cuspal Scope: The existing event engine evaluates solely Cusp 9 (primary_cusp=9), ignoring Cusp 7 (Rule 1) and Cusp 2 (Rule 2).",
        "Supporting House Expansion: The existing event engine defines supportive houses as [2, 7, 9, 11] (including house 7), whereas Rule 3 tests strictly [2, 9, 11].",
        "Separating House Penalty: The existing event engine subtracts or downgrades promises when denying houses [1, 6, 8, 10] are signified, whereas the classical isolated rules check positive signification presence.",
    ]

    r_verdicts = {k: v.status for k, v in analysis_result.rules.items()}

    summary = (
        f"Isolated Rules verdicts: Rule 1 ({r_verdicts.get('rule_1')}), "
        f"Rule 2 ({r_verdicts.get('rule_2')}), Rule 3 ({r_verdicts.get('rule_3')}). "
        f"Existing Event Engine verdict: '{event_verdict}' (hits={supporting_hits}, denying={denying_hits}). "
        f"Divergence is expected due to differing cuspal scope, house definitions, and threshold scoring."
    )

    return EventEngineComparisonResult(
        isolated_rules_verdicts=r_verdicts,
        event_engine_event_name="Second marriage",
        event_engine_primary_cusp=9,
        event_engine_verdict=event_verdict,
        event_engine_supporting_hits=supporting_hits,
        event_engine_denying_hits=denying_hits,
        divergence_reasons=divergence_reasons,
        comparison_summary=summary,
    )
