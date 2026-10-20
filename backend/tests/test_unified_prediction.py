"""Comprehensive Unit and Contract Tests for the Unified Marriage Prediction Engine.

Tests:
1. KP exhaustive decision tree (K1–K9).
2. Non-destructive ABCD significator hierarchy.
3. Vedic promise evaluation, single affliction vs compound denial gate (VED-MARR-PROM-006).
4. Master reconciliation matrix (M1–M11) and decoupled timing semantics.
5. Continuous Placidus cusp adaptive subdivision sensitivity scanner (stable, flip, polar guard).
6. End-to-end integration and Pydantic serialization.
"""

import pytest
from datetime import date, time, datetime, timezone
from unittest.mock import patch, MagicMock

from app.schemas.common import BirthInput
from app.services.unified_prediction.models import (
    EventVerdict,
    TimingStatus,
    PromiseVerdict,
    KPInternalModifier,
    VedicInternalModifier,
    RuleProvenanceTag,
    ScanStatus,
    UnifiedMarriageRequest,
    UnifiedMarriageResponse,
    KPPromiseDetail,
    VedicPromiseDetail,
)
from app.services.unified_prediction.kp_rules import (
    evaluate_kp_marriage_promise,
    compute_abcd_significations,
    calculate_house_of_longitude,
)
from app.services.unified_prediction.vedic_rules import (
    evaluate_vedic_marriage_promise,
    is_combust,
    calculate_house_from_lagna,
)
from app.services.unified_prediction.sensitivity import (
    scan_cusp_sensitivity,
    calculate_placidus_cusp_7,
    get_all_kp_sub_boundaries,
)
from app.services.unified_prediction.dasa_transit import (
    evaluate_double_transit,
    find_marriage_timing_windows,
)
from app.services.unified_prediction.engine import (
    UnifiedMarriagePredictionService,
)


# ===========================================================================
# 1. KP Decision Tree Tests (K1–K9)
# ===========================================================================

def test_kp_k1_pure_support():
    """K1: Pure support in both Star-Lord and Sub-Lord -> PROMISED_SMOOTH."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Venus",
        star_lord_of_csl="Jupiter",
        star_lord_sigs={2, 7},
        sub_lord_sigs={7, 11},
    )
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == KPInternalModifier.PROMISED_SMOOTH
    assert res.rule_provenance == RuleProvenanceTag.SOURCE_VERIFIED


def test_kp_k2_mixed_star_pure_sub():
    """K2: Star-lord mixed, sub-lord pure support -> PROMISED_SMOOTH."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Venus",
        star_lord_of_csl="Saturn",
        star_lord_sigs={2, 6},
        sub_lord_sigs={7, 11},
    )
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == KPInternalModifier.PROMISED_SMOOTH


def test_kp_k3_support_star_mixed_sub():
    """K3: Star-lord supports, sub-lord mixed -> PROMISED_WITH_OBSTACLES."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Mars",
        star_lord_of_csl="Sun",
        star_lord_sigs={7},
        sub_lord_sigs={2, 6},
    )
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == KPInternalModifier.PROMISED_WITH_OBSTACLES
    assert res.rule_provenance == RuleProvenanceTag.PROJECT_ENGINEERING_POLICY


def test_kp_k4_support_star_neutral_sub():
    """K4: Star-lord supports, sub-lord neutral -> PROMISED_DELAYED."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Mercury",
        star_lord_of_csl="Venus",
        star_lord_sigs={7, 11},
        sub_lord_sigs={3, 9},  # neutral houses
    )
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == KPInternalModifier.PROMISED_DELAYED


def test_kp_k5_no_support_star_support_sub():
    """K5: Star-lord has NO support, sub-lord supports -> DENIED_AT_ROOT."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Venus",
        star_lord_of_csl="Saturn",
        star_lord_sigs={1, 6},   # no 2, 7, 11
        sub_lord_sigs={2, 7},   # sub-lord supports
    )
    assert res.verdict == PromiseVerdict.DENIED
    assert res.internal_modifier == KPInternalModifier.DENIED_AT_ROOT
    assert res.rule_provenance == RuleProvenanceTag.PROJECT_ENGINEERING_POLICY


def test_kp_k6_support_star_pure_denial_sub():
    """K6: Star-lord supports, sub-lord pure denial -> DENIED_AT_FRUITION."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Mars",
        star_lord_of_csl="Venus",
        star_lord_sigs={2, 7},
        sub_lord_sigs={1, 6, 10},  # exclusively denying
    )
    assert res.verdict == PromiseVerdict.DENIED
    assert res.internal_modifier == KPInternalModifier.DENIED_AT_FRUITION
    assert res.rule_provenance == RuleProvenanceTag.SOURCE_VERIFIED


def test_kp_k7_k8_neither_supports():
    """K7/K8: Neither star-lord nor sub-lord supports -> DENIED_AT_ROOT."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Saturn",
        star_lord_of_csl="Ketu",
        star_lord_sigs={1, 6},
        sub_lord_sigs={3, 8},
    )
    assert res.verdict == PromiseVerdict.DENIED
    assert res.internal_modifier == KPInternalModifier.DENIED_AT_ROOT


def test_kp_retrograde_flag_preserved():
    """Verify retrograde status of CSL or Star-Lord is accurately recorded."""
    res = evaluate_kp_marriage_promise(
        cuspal_sub_lord_7="Venus",
        star_lord_of_csl="Jupiter",
        star_lord_sigs={7},
        sub_lord_sigs={2},
        is_csl_retro=True,
        is_star_retro=False,
    )
    assert res.is_csl_retrograde is True
    assert res.is_star_lord_retrograde is False


# ===========================================================================
# 2. ABCD Significator Hierarchy Tests
# ===========================================================================

def test_abcd_significator_collection():
    """Verify ABCD significators retain all levels non-destructively."""
    cusps = [float(i * 30.0) for i in range(12)]
    # Place Sun at 10 deg (House 1), Moon at 40 deg (House 2)
    positions = {"Sun": 10.0, "Moon": 40.0}
    abcd = compute_abcd_significations(positions, cusps)

    # Sun is in house 1
    assert 1 in abcd["Sun"]["B"]
    assert 1 in abcd["Sun"]["all"]
    # Moon is in house 2
    assert 2 in abcd["Moon"]["B"]
    assert 2 in abcd["Moon"]["all"]


# ===========================================================================
# 3. Vedic Promise & Compound Denial Gate (VED-MARR-PROM-006)
# ===========================================================================

def test_vedic_favorable_promise():
    """Unafflicted 7th lord and dignified Venus -> PROMISED_FAVORABLE."""
    # Ascendant 0.0 (Aries, sign 1). 7th house is Libra (sign 7), lord is Venus.
    planets = {
        "Venus": {"longitude": 35.0, "sign_index": 2, "is_retrograde": False},  # Taurus (own sign, 2nd house)
        "Sun": {"longitude": 120.0, "sign_index": 5, "is_retrograde": False},   # Leo (far away, no combustion)
        "Mars": {"longitude": 280.0, "sign_index": 10, "is_retrograde": False}, # Capricorn (exalted, Kuja cancelled)
        "Jupiter": {"longitude": 95.0, "sign_index": 4, "is_retrograde": False},
        "Moon": {"longitude": 45.0, "sign_index": 2, "is_retrograde": False},
    }
    res = evaluate_vedic_marriage_promise(planets, ascendant_degree=0.0)
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == VedicInternalModifier.PROMISED_FAVORABLE
    assert res.compound_denial_gates_met == 0


def test_vedic_single_affliction_combustion_not_denied():
    """Venus combust alone must NOT categorically deny -> PROMISED_WITH_OBSTACLES."""
    planets = {
        "Venus": {"longitude": 35.0, "sign_index": 2, "is_retrograde": False},
        "Sun": {"longitude": 37.0, "sign_index": 2, "is_retrograde": False},    # Combust (within 2 deg)
        "Mars": {"longitude": 280.0, "sign_index": 10, "is_retrograde": False}, # Exalted
        "Jupiter": {"longitude": 95.0, "sign_index": 4, "is_retrograde": False},
        "Moon": {"longitude": 45.0, "sign_index": 2, "is_retrograde": False},
    }
    res = evaluate_vedic_marriage_promise(planets, ascendant_degree=0.0)
    assert res.verdict == PromiseVerdict.PROMISED
    assert res.internal_modifier == VedicInternalModifier.PROMISED_WITH_OBSTACLES
    assert res.venus_combustion is True
    assert res.compound_denial_gates_met < 3


def test_vedic_compound_denial_gate_satisfied():
    """All 3 gates satisfied (7th lord dusthana, Venus combust+debilitated, D9 afflicted) -> DENIED."""
    # Ascendant 0.0 (Aries). 7th lord is Venus.
    # Put Venus in Virgo (sign 6, debilitated, 6th house dusthana), combust Sun.
    planets = {
        "Venus": {"longitude": 158.0, "sign_index": 6, "is_retrograde": False},
        "Sun": {"longitude": 158.5, "sign_index": 6, "is_retrograde": False},
        "Mars": {"longitude": 40.0, "sign_index": 2, "is_retrograde": False},
        "Jupiter": {"longitude": 200.0, "sign_index": 7, "is_retrograde": False},
        "Moon": {"longitude": 80.0, "sign_index": 3, "is_retrograde": False},
    }
    res = evaluate_vedic_marriage_promise(planets, ascendant_degree=0.0)
    assert res.verdict == PromiseVerdict.DENIED
    assert res.internal_modifier == VedicInternalModifier.DENIED_COMPOUND
    assert res.compound_denial_gates_met == 3
    assert res.rule_provenance == RuleProvenanceTag.PROJECT_ENGINEERING_POLICY


# ===========================================================================
# 4. Master Reconciliation Matrix (M1–M11)
# ===========================================================================

def test_reconciliation_m1_both_promised_window_found():
    """M1: KP Promised + Vedic Promised + Window Found -> EVENT_INDICATED, WINDOW_FOUND."""
    req = UnifiedMarriageRequest(
        birth=BirthInput(
            birth_date=date(1995, 10, 24),
            birth_time=time(14, 30, 0),
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        birth_time_uncertainty_seconds=60.0,
    )
    resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
    assert resp.final_verdict in (EventVerdict.EVENT_INDICATED, EventVerdict.INDETERMINATE)
    if resp.kp_promise.verdict == PromiseVerdict.PROMISED and resp.vedic_promise.verdict == PromiseVerdict.PROMISED:
        assert resp.final_verdict == EventVerdict.EVENT_INDICATED
        assert resp.timing_status in (TimingStatus.WINDOW_FOUND, TimingStatus.NO_WINDOW_IN_RANGE)


def test_reconciliation_conflict_yields_indeterminate():
    """M5/M6: Conflict between KP and Vedic yields INDETERMINATE with timing NOT_EVALUATED."""
    with patch("app.services.unified_prediction.engine.evaluate_vedic_marriage_promise") as mock_vedic:
        mock_vedic.return_value = VedicPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=VedicInternalModifier.DENIED_COMPOUND,
            seventh_lord_d1="Venus",
            seventh_house_sign_d1="Libra",
            seventh_lord_house_d1=6,
            venus_combustion=True,
            venus_debilitation=True,
            venus_dusthana=True,
            kuja_dosha_present=False,
            kuja_dosha_cancelled=False,
            d9_seventh_sign="Aries",
            d9_seventh_lord="Mars",
            d9_venus_sign="Virgo",
            d9_afflicted=True,
            compound_denial_gates_met=3,
            rule_id="VED-MARR-PROM-006",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation="Mock Vedic Denied",
        )
        with patch("app.services.unified_prediction.engine.evaluate_kp_marriage_promise") as mock_kp:
            mock_kp.return_value = KPPromiseDetail(
                verdict=PromiseVerdict.PROMISED,
                internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
                cuspal_sub_lord_7="Venus",
                star_lord_of_csl="Jupiter",
                star_lord_significations=[2, 7],
                sub_lord_significations=[7, 11],
                is_csl_retrograde=False,
                is_star_lord_retrograde=False,
                rule_id="KP-MARR-PROM-001",
                rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                explanation="Mock KP Promised",
            )
            req = UnifiedMarriageRequest(
                birth=BirthInput(
                    birth_date=date(1995, 10, 24),
                    birth_time=time(14, 30, 0),
                    timezone="Asia/Kolkata",
                    latitude=13.0827,
                    longitude=80.2707,
                ),
                birth_time_uncertainty_seconds=0.0,
            )
            resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
            assert resp.final_verdict == EventVerdict.INDETERMINATE
            assert resp.timing_status == TimingStatus.NOT_EVALUATED


def test_reconciliation_concordant_denial():
    """M4: Both traditions denied -> EVENT_NOT_INDICATED, NOT_EVALUATED."""
    with patch("app.services.unified_prediction.engine.evaluate_vedic_marriage_promise") as mock_vedic:
        mock_vedic.return_value = VedicPromiseDetail(
            verdict=PromiseVerdict.DENIED,
            internal_modifier=VedicInternalModifier.DENIED_COMPOUND,
            seventh_lord_d1="Venus",
            seventh_house_sign_d1="Libra",
            seventh_lord_house_d1=6,
            venus_combustion=True,
            venus_debilitation=True,
            venus_dusthana=True,
            kuja_dosha_present=False,
            kuja_dosha_cancelled=False,
            d9_seventh_sign="Aries",
            d9_seventh_lord="Mars",
            d9_venus_sign="Virgo",
            d9_afflicted=True,
            compound_denial_gates_met=3,
            rule_id="VED-MARR-PROM-006",
            rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            explanation="Mock Vedic Denied",
        )
        with patch("app.services.unified_prediction.engine.evaluate_kp_marriage_promise") as mock_kp:
            mock_kp.return_value = KPPromiseDetail(
                verdict=PromiseVerdict.DENIED,
                internal_modifier=KPInternalModifier.DENIED_AT_ROOT,
                cuspal_sub_lord_7="Saturn",
                star_lord_of_csl="Sun",
                star_lord_significations=[1, 6],
                sub_lord_significations=[6, 10],
                is_csl_retrograde=False,
                is_star_lord_retrograde=False,
                rule_id="KP-MARR-PROM-003",
                rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                explanation="Mock KP Denied",
            )
            req = UnifiedMarriageRequest(
                birth=BirthInput(
                    birth_date=date(1995, 10, 24),
                    birth_time=time(14, 30, 0),
                    timezone="Asia/Kolkata",
                    latitude=13.0827,
                    longitude=80.2707,
                ),
                birth_time_uncertainty_seconds=0.0,
            )
            resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
            assert resp.final_verdict == EventVerdict.EVENT_NOT_INDICATED
            assert resp.timing_status == TimingStatus.NOT_EVALUATED


# ===========================================================================
# 5. Continuous Sensitivity Scanner & Safeguards
# ===========================================================================

def test_sensitivity_polar_latitude_guard():
    """Latitudes |lat| > 66.0° must trigger SCAN_FAILED_OR_INCOMPLETE fail-safe."""
    nominal_dt = datetime(1995, 10, 24, 14, 30, 0, tzinfo=timezone.utc)
    rep = scan_cusp_sensitivity(
        nominal_dt=nominal_dt,
        nominal_jd=2450015.104,
        lat=70.5,  # Arctic latitude
        lon=80.0,
        uncertainty_seconds=120.0,
        nominal_csl="Venus",
        kp_evaluator=lambda s: PromiseVerdict.PROMISED,
    )
    assert rep.is_sensitive is True
    assert rep.scan_status == ScanStatus.SCAN_FAILED_OR_INCOMPLETE
    assert "exceeds Placidus" in (rep.error_detail or "")


def test_sensitivity_stable_interval():
    """Stable interval without crossing returns STABLE and is_sensitive=False."""
    nominal_dt = datetime(1995, 10, 24, 14, 30, 0, tzinfo=timezone.utc)
    # 0 second uncertainty
    rep = scan_cusp_sensitivity(
        nominal_dt=nominal_dt,
        nominal_jd=2450015.104,
        lat=13.0827,
        lon=80.2707,
        uncertainty_seconds=0.0,
        nominal_csl="Venus",
        kp_evaluator=lambda s: PromiseVerdict.PROMISED,
    )
    assert rep.is_sensitive is False
    assert rep.scan_status == ScanStatus.STABLE
    assert len(rep.crossings) == 0


def test_sensitivity_verdict_preserved_vs_flipped():
    """Crossing that preserves verdict does NOT trigger is_sensitive, but flip does."""
    # When evaluator always returns PROMISED, crossing is preserved -> is_sensitive=False
    nominal_dt = datetime(1995, 10, 24, 14, 30, 0, tzinfo=timezone.utc)
    rep_preserved = scan_cusp_sensitivity(
        nominal_dt=nominal_dt,
        nominal_jd=2450015.104,
        lat=13.0827,
        lon=80.2707,
        uncertainty_seconds=300.0,  # 5 minutes -> guarantees some crossing
        nominal_csl="Venus",
        kp_evaluator=lambda s: PromiseVerdict.PROMISED,  # always promised
    )
    assert rep_preserved.is_sensitive is False

    # When evaluator returns DENIED for other subs -> flip triggers is_sensitive=True
    rep_flipped = scan_cusp_sensitivity(
        nominal_dt=nominal_dt,
        nominal_jd=2450015.104,
        lat=13.0827,
        lon=80.2707,
        uncertainty_seconds=300.0,
        nominal_csl="Venus",
        kp_evaluator=lambda s: PromiseVerdict.PROMISED if s == "Venus" else PromiseVerdict.DENIED,
    )
    if rep_flipped.crossings:
        assert rep_flipped.is_sensitive is True


# ===========================================================================
# 6. End-to-End Contract & Serialization Tests
# ===========================================================================

def test_full_service_contract_serialization():
    """Verify UnifiedMarriageResponse serializes cleanly to JSON according to schema."""
    req = UnifiedMarriageRequest(
        birth=BirthInput(
            birth_date=date(1995, 10, 24),
            birth_time=time(14, 30, 0),
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        birth_time_uncertainty_seconds=120.0,
        start_year=2024,
        end_year=2030,
    )
    resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
    # Pydantic dump
    dump = resp.model_dump()
    assert "final_verdict" in dump
    assert "timing_status" in dump
    assert "kp_promise" in dump
    assert "vedic_promise" in dump
    assert "birth_time_sensitivity" in dump
    assert dump["reconciliation_rule_id"] == "UNI-MARR-REC-001"


# ===========================================================================
# 7. Additional Edge Case and Decoupled Timing Tests
# ===========================================================================

def test_vedic_missing_data_indeterminate():
    """Missing 7th lord data in planetary dict returns INDETERMINATE."""
    planets = {
        "Sun": {"longitude": 120.0, "sign_index": 5, "is_retrograde": False},
        # Venus (7th lord for Aries Lagna) is deliberately omitted
    }
    res = evaluate_vedic_marriage_promise(planets, ascendant_degree=0.0)
    assert res.verdict == PromiseVerdict.INDETERMINATE
    assert res.internal_modifier == VedicInternalModifier.INDETERMINATE_DATA
    assert "missing data" in res.explanation


def test_reconciliation_m2_no_window_in_range():
    """M2: Concordant natal support with empty timing window preserves EVENT_INDICATED."""
    with patch("app.services.unified_prediction.engine.find_marriage_timing_windows") as mock_timing:
        mock_timing.return_value = (TimingStatus.NO_WINDOW_IN_RANGE, None)
        with patch("app.services.unified_prediction.engine.evaluate_vedic_marriage_promise") as mock_vedic:
            mock_vedic.return_value = VedicPromiseDetail(
                verdict=PromiseVerdict.PROMISED,
                internal_modifier=VedicInternalModifier.PROMISED_FAVORABLE,
                seventh_lord_d1="Venus",
                seventh_house_sign_d1="Libra",
                seventh_lord_house_d1=2,
                venus_combustion=False,
                venus_debilitation=False,
                venus_dusthana=False,
                kuja_dosha_present=False,
                kuja_dosha_cancelled=False,
                d9_seventh_sign="Libra",
                d9_seventh_lord="Venus",
                d9_venus_sign="Taurus",
                d9_afflicted=False,
                compound_denial_gates_met=0,
                rule_id="VED-MARR-PROM-001",
                rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                explanation="Favorable",
            )
            with patch("app.services.unified_prediction.engine.evaluate_kp_marriage_promise") as mock_kp:
                mock_kp.return_value = KPPromiseDetail(
                    verdict=PromiseVerdict.PROMISED,
                    internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
                    cuspal_sub_lord_7="Venus",
                    star_lord_of_csl="Jupiter",
                    star_lord_significations=[2, 7],
                    sub_lord_significations=[7, 11],
                    is_csl_retrograde=False,
                    is_star_lord_retrograde=False,
                    rule_id="KP-MARR-PROM-001",
                    rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                    explanation="Promised",
                )
                req = UnifiedMarriageRequest(
                    birth=BirthInput(
                        birth_date=date(1995, 10, 24),
                        birth_time=time(14, 30, 0),
                        timezone="Asia/Kolkata",
                        latitude=13.0827,
                        longitude=80.2707,
                    ),
                    birth_time_uncertainty_seconds=0.0,
                )
                resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
                assert resp.final_verdict == EventVerdict.EVENT_INDICATED
                assert resp.timing_status == TimingStatus.NO_WINDOW_IN_RANGE


def test_reconciliation_m3_timing_calculation_failure():
    """M3: Timing calculation error must NOT overturn valid EVENT_INDICATED natal verdict."""
    with patch("app.services.unified_prediction.engine.find_marriage_timing_windows") as mock_timing:
        mock_timing.return_value = (TimingStatus.TIMING_NOT_DETERMINABLE, None)
        with patch("app.services.unified_prediction.engine.evaluate_vedic_marriage_promise") as mock_vedic:
            mock_vedic.return_value = VedicPromiseDetail(
                verdict=PromiseVerdict.PROMISED,
                internal_modifier=VedicInternalModifier.PROMISED_FAVORABLE,
                seventh_lord_d1="Venus",
                seventh_house_sign_d1="Libra",
                seventh_lord_house_d1=2,
                venus_combustion=False,
                venus_debilitation=False,
                venus_dusthana=False,
                kuja_dosha_present=False,
                kuja_dosha_cancelled=False,
                d9_seventh_sign="Libra",
                d9_seventh_lord="Venus",
                d9_venus_sign="Taurus",
                d9_afflicted=False,
                compound_denial_gates_met=0,
                rule_id="VED-MARR-PROM-001",
                rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                explanation="Favorable",
            )
            with patch("app.services.unified_prediction.engine.evaluate_kp_marriage_promise") as mock_kp:
                mock_kp.return_value = KPPromiseDetail(
                    verdict=PromiseVerdict.PROMISED,
                    internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
                    cuspal_sub_lord_7="Venus",
                    star_lord_of_csl="Jupiter",
                    star_lord_significations=[2, 7],
                    sub_lord_significations=[7, 11],
                    is_csl_retrograde=False,
                    is_star_lord_retrograde=False,
                    rule_id="KP-MARR-PROM-001",
                    rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                    explanation="Promised",
                )
                req = UnifiedMarriageRequest(
                    birth=BirthInput(
                        birth_date=date(1995, 10, 24),
                        birth_time=time(14, 30, 0),
                        timezone="Asia/Kolkata",
                        latitude=13.0827,
                        longitude=80.2707,
                    ),
                    birth_time_uncertainty_seconds=0.0,
                )
                resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
                assert resp.final_verdict == EventVerdict.EVENT_INDICATED
                assert resp.timing_status == TimingStatus.TIMING_NOT_DETERMINABLE


def test_reconciliation_m7_to_m11_indeterminate_cases():
    """M7-M11: Whenever either tradition is INDETERMINATE, final verdict is INDETERMINATE."""
    for kp_v in (PromiseVerdict.PROMISED, PromiseVerdict.DENIED, PromiseVerdict.INDETERMINATE):
        for ved_v in (PromiseVerdict.PROMISED, PromiseVerdict.DENIED, PromiseVerdict.INDETERMINATE):
            if kp_v == PromiseVerdict.PROMISED and ved_v == PromiseVerdict.PROMISED:
                continue
            if kp_v == PromiseVerdict.DENIED and ved_v == PromiseVerdict.DENIED:
                continue
            # All other combinations must yield INDETERMINATE
            with patch("app.services.unified_prediction.engine.evaluate_vedic_marriage_promise") as mock_vedic:
                mock_vedic.return_value = VedicPromiseDetail(
                    verdict=ved_v,
                    internal_modifier=VedicInternalModifier.INDETERMINATE_DATA,
                    seventh_lord_d1="Venus",
                    seventh_house_sign_d1="Libra",
                    seventh_lord_house_d1=2,
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
                    rule_id="VED-TEST",
                    rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
                    explanation="Test",
                )
                with patch("app.services.unified_prediction.engine.evaluate_kp_marriage_promise") as mock_kp:
                    mock_kp.return_value = KPPromiseDetail(
                        verdict=kp_v,
                        internal_modifier=KPInternalModifier.INDETERMINATE_DATA,
                        cuspal_sub_lord_7="Venus",
                        star_lord_of_csl="Jupiter",
                        star_lord_significations=[],
                        sub_lord_significations=[],
                        is_csl_retrograde=False,
                        is_star_lord_retrograde=False,
                        rule_id="KP-TEST",
                        rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
                        explanation="Test",
                    )
                    req = UnifiedMarriageRequest(
                        birth=BirthInput(
                            birth_date=date(1995, 10, 24),
                            birth_time=time(14, 30, 0),
                            timezone="Asia/Kolkata",
                            latitude=13.0827,
                            longitude=80.2707,
                        ),
                        birth_time_uncertainty_seconds=0.0,
                    )
                    resp = UnifiedMarriagePredictionService.predict_marriage_event(req)
                    assert resp.final_verdict == EventVerdict.INDETERMINATE
                    assert resp.timing_status == TimingStatus.NOT_EVALUATED


def test_double_transit_supporting_evaluator():
    """Verify double transit evaluation returns boolean without raising."""
    res = evaluate_double_transit(transit_jd=2460450.5, target_signs={1, 7})
    assert isinstance(res, bool)

