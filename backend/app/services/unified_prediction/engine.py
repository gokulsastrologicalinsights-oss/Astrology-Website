"""Master Orchestrator for Unified KP + Vedic Marriage Prediction Engine.

This module coordinates:
1. Astronomical computation via XALEN.
2. Continuous Placidus cusp adaptive subdivision sensitivity scanning.
3. Isolated KP natal marriage promise evaluation (K1–K9).
4. Isolated Vedic natal marriage promise evaluation (D1, D9, Venus, Compound Gate).
5. Conservative Master Reconciliation (M1–M11).
6. Vimshottari Dasha and supporting Double Transit timing evaluation.

Classical Citations & Provenance:
- Master Reconciliation Policy: [PROJECT_ENGINEERING_POLICY]
"""

from __future__ import annotations

from typing import Dict, List, Set, Any, Optional
from datetime import datetime

import xalen
import xalen.swe as xswe
from app.schemas.common import CalculationMetadata
from app.services.timezone_utils import resolve_birth_datetime
from app.services.ephemeris import (
    compute_planetary_positions,
    get_sign_info,
)
from app.services.kp_engine.vedic import (
    sub_lord,
    star_lord,
)
from app.services.unified_prediction.models import (
    EventVerdict,
    TimingStatus,
    PromiseVerdict,
    KPInternalModifier,
    VedicInternalModifier,
    UnifiedMarriageRequest,
    UnifiedMarriageResponse,
    RuleProvenanceTag,
    ScanStatus,
    KPPromiseDetail,
    VedicPromiseDetail,
    BirthTimeSensitivityReport,
    SensitivityToleranceGuarantee,
)
from app.services.unified_prediction.kp_rules import (
    compute_abcd_significations,
    evaluate_kp_marriage_promise,
    calculate_house_of_longitude,
)
from app.services.unified_prediction.vedic_rules import (
    evaluate_vedic_marriage_promise,
)
from app.services.unified_prediction.sensitivity import (
    scan_cusp_sensitivity,
    calculate_placidus_cusp_7,
)
from app.services.unified_prediction.dasa_transit import (
    find_marriage_timing_windows,
)


class UnifiedMarriagePredictionService:
    """Production service for unified KP + Vedic marriage event prediction."""

    @classmethod
    def predict_marriage_event(
        cls,
        request: UnifiedMarriageRequest,
    ) -> UnifiedMarriageResponse:
        """Execute deterministic marriage prediction pipeline."""
        birth = request.birth
        uncertainty_sec = request.birth_time_uncertainty_seconds

        # 1. Resolve Local and Julian Datetime
        local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
            birth.birth_date,
            birth.birth_time,
            birth.timezone,
        )

        # 2. Compute Planetary Positions (KP ayanamsa = 1, Vedic ayanamsa = 0)
        # We compute sidereal positions with KP Ayanamsa for KP and Lahiri for Vedic
        kp_planets = compute_planetary_positions(birth_jd, ayanamsa_id=1, include_outer=False)
        kp_planet_positions = {p.name: p.longitude for p in kp_planets}
        kp_retrogrades = {p.name: p.is_retrograde for p in kp_planets}

        vedic_planets = compute_planetary_positions(birth_jd, ayanamsa_id=0, include_outer=False)
        vedic_planet_dict = {
            p.name: {
                "longitude": p.longitude,
                "sign_index": p.sign_index,
                "is_retrograde": p.is_retrograde,
            }
            for p in vedic_planets
        }

        # 3. Compute KP Placidus Cusps (b'P', Krishnamurti Ayanamsa)
        xswe.set_sid_mode(xswe.SIDM_KRISHNAMURTI, 0, 0)
        try:
            cusps_raw, ascmc_raw = xswe.houses_ex(birth_jd, birth.latitude, birth.longitude, b"P", xswe.FLG_SIDEREAL)
            cusps = [c % 360.0 for c in cusps_raw]
            asc_degree_kp = ascmc_raw[0] % 360.0
            cusp_7_degree = cusps[6]
        except Exception as e:
            # Polar latitude or ephemeris failure
            kp_ayan_val = round(float(xalen.ayanamsa(birth_jd, 1)), 6) if 'birth_jd' in locals() else 0.0
            vedic_ayan_val = round(float(xalen.ayanamsa(birth_jd, 0)), 6) if 'birth_jd' in locals() else 0.0
            metadata = CalculationMetadata(
                engine="XALEN 0.6.0 (Rust) + Unified Prediction Engine",
                birth_utc_iso=utc_dt.isoformat() if 'utc_dt' in locals() else "",
                julian_day_ut1=birth_jd if 'birth_jd' in locals() else 0.0,
                local_timezone=tz_name if 'tz_name' in locals() else "",
                utc_offset_hours=offset_hours if 'offset_hours' in locals() else 0.0,
                coordinates={"latitude": birth.latitude, "longitude": birth.longitude},
                ayanamsa_id=1,
                ayanamsa_name="Krishnamurti (KP) + Chitrapaksha Lahiri (Vedic)",
                ayanamsa_deg=kp_ayan_val,
                house_system_id=2,
                house_system_name="Placidus (KP)",
                notes=[
                    f"House calculation error: {str(e)}",
                    f"KP Krishnamurti ayanamsa: {kp_ayan_val}° (ID: 1)",
                    f"Vedic Chitrapaksha Lahiri ayanamsa: {vedic_ayan_val}° (ID: 0)",
                ],
            )
            # Fail safely to INDETERMINATE
            return UnifiedMarriageResponse(
                final_verdict=EventVerdict.INDETERMINATE,
                timing_status=TimingStatus.NOT_EVALUATED,
                kp_promise=KPPromiseDetail(
                    verdict=PromiseVerdict.INDETERMINATE,
                    internal_modifier=KPInternalModifier.INDETERMINATE_DATA,
                    cuspal_sub_lord_7="Unknown",
                    star_lord_of_csl="Unknown",
                    star_lord_significations=[],
                    sub_lord_significations=[],
                    rule_id="KP-MARR-ERR-001",
                    rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
                    explanation=f"Placidus house calculation failed: {str(e)}",
                ),
                vedic_promise=VedicPromiseDetail(
                    verdict=PromiseVerdict.INDETERMINATE,
                    internal_modifier=VedicInternalModifier.INDETERMINATE_DATA,
                    seventh_lord_d1="Unknown",
                    seventh_house_sign_d1="Unknown",
                    seventh_lord_house_d1=0,
                    venus_combustion=False,
                    venus_debilitation=False,
                    venus_dusthana=False,
                    kuja_dosha_present=False,
                    kuja_dosha_cancelled=False,
                    d9_seventh_sign="Unknown",
                    d9_seventh_lord="Unknown",
                    d9_venus_sign="Unknown",
                    d9_afflicted=False,
                    compound_denial_gates_met=0,
                    rule_id="VED-MARR-ERR-001",
                    rule_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
                    explanation="Ephemeris error prevented Vedic evaluation.",
                ),
                birth_time_sensitivity=BirthTimeSensitivityReport(
                    is_sensitive=True,
                    uncertainty_seconds=request.birth_time_uncertainty_seconds,
                    scan_status=ScanStatus.SCAN_FAILED_OR_INCOMPLETE,
                    nominal_sub_lord="Unknown",
                    nominal_cusp_degree=0.0,
                    crossings=[],
                    tolerance_guarantee=SensitivityToleranceGuarantee(),
                    error_detail=str(e),
                ),
                metadata=metadata,
            )

        # 4. Compute Non-Destructive ABCD Significators
        abcd_sigs = compute_abcd_significations(kp_planet_positions, cusps)

        # Nominal 7th CSL & Star-Lord
        nominal_csl = sub_lord(cusp_7_degree)
        nominal_star_lord = star_lord(kp_planet_positions.get(nominal_csl, 0.0))

        # Helper evaluator for arbitrary sub-lord (used by sensitivity scanner)
        def evaluate_csl_verdict(sub_candidate: str) -> PromiseVerdict:
            if sub_candidate not in kp_planet_positions:
                return PromiseVerdict.INDETERMINATE
            s_lord = star_lord(kp_planet_positions[sub_candidate])
            sl_sigs = abcd_sigs.get(s_lord, {}).get("all", set())
            sub_sigs = abcd_sigs.get(sub_candidate, {}).get("all", set())
            detail = evaluate_kp_marriage_promise(
                cuspal_sub_lord_7=sub_candidate,
                star_lord_of_csl=s_lord,
                star_lord_sigs=sl_sigs,
                sub_lord_sigs=sub_sigs,
                is_csl_retro=kp_retrogrades.get(sub_candidate, False),
                is_star_retro=kp_retrogrades.get(s_lord, False),
            )
            return detail.verdict

        # 5. Continuous Placidus Cusp Sensitivity Scan
        sensitivity_report = scan_cusp_sensitivity(
            nominal_dt=local_dt,
            nominal_jd=birth_jd,
            lat=birth.latitude,
            lon=birth.longitude,
            uncertainty_seconds=uncertainty_sec,
            nominal_csl=nominal_csl,
            kp_evaluator=evaluate_csl_verdict,
        )

        # 6. Evaluate KP Promise
        sl_sigs = abcd_sigs.get(nominal_star_lord, {}).get("all", set())
        sub_sigs = abcd_sigs.get(nominal_csl, {}).get("all", set())
        kp_promise = evaluate_kp_marriage_promise(
            cuspal_sub_lord_7=nominal_csl,
            star_lord_of_csl=nominal_star_lord,
            star_lord_sigs=sl_sigs,
            sub_lord_sigs=sub_sigs,
            is_csl_retro=kp_retrogrades.get(nominal_csl, False),
            is_star_retro=kp_retrogrades.get(nominal_star_lord, False),
        )

        # Guard: If sensitivity scan detected a verdict flip or failed, override KP promise to INDETERMINATE
        if sensitivity_report.is_sensitive:
            kp_promise = kp_promise.model_copy(
                update={
                    "verdict": PromiseVerdict.INDETERMINATE,
                    "internal_modifier": KPInternalModifier.INDETERMINATE_DATA,
                    "explanation": (
                        f"Birth-time sensitivity: 7th CSL transitions within +/-{uncertainty_sec}s "
                        "uncertainty window and causes a verdict flip or scan failure."
                    ),
                }
            )

        # 7. Evaluate Vedic Promise (Whole Sign, Lahiri)
        xswe.set_sid_mode(xswe.SIDM_LAHIRI, 0, 0)
        _, ascmc_vedic = xswe.houses_ex(birth_jd, birth.latitude, birth.longitude, b"W", xswe.FLG_SIDEREAL)
        asc_degree_vedic = ascmc_vedic[0] % 360.0

        vedic_promise = evaluate_vedic_marriage_promise(
            planets=vedic_planet_dict,
            ascendant_degree=asc_degree_vedic,
        )

        # 8. Master Reconciliation Matrix (M1–M11)
        final_verdict = EventVerdict.INDETERMINATE
        timing_status = TimingStatus.NOT_EVALUATED
        timing_report: Optional[Any] = None

        concordant_support = (kp_promise.verdict == PromiseVerdict.PROMISED and vedic_promise.verdict == PromiseVerdict.PROMISED)
        concordant_denial = (kp_promise.verdict == PromiseVerdict.DENIED and vedic_promise.verdict == PromiseVerdict.DENIED)
        should_evaluate_timing = concordant_support or (request.force_timing_scan and not concordant_denial)

        if should_evaluate_timing:
            # Evaluate Timing (Concordant support or explicitly requested exploratory scan)
            search_start = request.start_year or (birth.birth_date.year + 18)
            search_end = request.end_year or (search_start + 10)

            # Build significator sets for timing
            kp_marriage_sigs = {
                p for p, data in abcd_sigs.items()
                if bool(data["all"] & {2, 7, 11})
            }

            # Vedic significators: 7th lord, lagna lord, 2nd lord, 11th lord, Venus
            lagna_sign_vedic = int((asc_degree_vedic % 360.0) // 30.0) + 1
            seventh_sign_vedic = ((lagna_sign_vedic + 6 - 1) % 12) + 1
            second_sign_vedic = ((lagna_sign_vedic + 1 - 1) % 12) + 1
            eleventh_sign_vedic = ((lagna_sign_vedic + 10 - 1) % 12) + 1

            from app.services.varga_engine import SIGN_LORDS as VEDIC_SIGN_LORDS
            vedic_marriage_sigs = {
                VEDIC_SIGN_LORDS[seventh_sign_vedic],
                VEDIC_SIGN_LORDS[lagna_sign_vedic],
                VEDIC_SIGN_LORDS[second_sign_vedic],
                VEDIC_SIGN_LORDS[eleventh_sign_vedic],
                "Venus",
            }

            moon_pos_vedic = vedic_planet_dict.get("Moon", {}).get("longitude", 0.0)
            seventh_lord_name = VEDIC_SIGN_LORDS[seventh_sign_vedic]
            lagna_lord_name = VEDIC_SIGN_LORDS[lagna_sign_vedic]

            seventh_lord_sign = vedic_planet_dict.get(seventh_lord_name, {}).get("sign_index", seventh_sign_vedic)
            lagna_lord_sign = vedic_planet_dict.get(lagna_lord_name, {}).get("sign_index", lagna_sign_vedic)

            status, report = find_marriage_timing_windows(
                moon_lon=moon_pos_vedic,
                birth_jd=birth_jd,
                birth_year=birth.birth_date.year,
                search_start_year=search_start,
                search_end_year=search_end,
                lagna_sign=lagna_sign_vedic,
                seventh_house_sign=seventh_sign_vedic,
                lagna_lord_sign=lagna_lord_sign,
                seventh_lord_sign=seventh_lord_sign,
                kp_marriage_significators=kp_marriage_sigs,
                vedic_marriage_significators=vedic_marriage_sigs,
                utc_offset_hours=offset_hours,
            )

            if concordant_support:
                final_verdict = EventVerdict.EVENT_INDICATED
            else:
                final_verdict = EventVerdict.INDETERMINATE

            timing_status = status
            timing_report = report

        elif concordant_denial:
            # Concordant Denial
            final_verdict = EventVerdict.EVENT_NOT_INDICATED
            timing_status = TimingStatus.NOT_EVALUATED

        else:
            # Inter-tradition conflict or Indeterminate
            final_verdict = EventVerdict.INDETERMINATE
            timing_status = TimingStatus.NOT_EVALUATED

        kp_ayanamsa_deg = round(float(xalen.ayanamsa(birth_jd, 1)), 6)
        vedic_ayanamsa_deg = round(float(xalen.ayanamsa(birth_jd, 0)), 6)

        metadata = CalculationMetadata(
            engine="XALEN 0.6.0 (Rust) + Unified Prediction Engine",
            birth_utc_iso=utc_dt.isoformat(),
            julian_day_ut1=birth_jd,
            local_timezone=tz_name,
            utc_offset_hours=offset_hours,
            coordinates={"latitude": birth.latitude, "longitude": birth.longitude},
            ayanamsa_id=1,
            ayanamsa_name="Krishnamurti (KP) + Chitrapaksha Lahiri (Vedic)",
            ayanamsa_deg=kp_ayanamsa_deg,
            house_system_id=2,
            house_system_name="Placidus (KP) + Whole Sign (Vedic)",
            notes=[
                "Deterministic Unified KP + Vedic Marriage Prediction Engine",
                f"KP Krishnamurti ayanamsa: {kp_ayanamsa_deg}° (ID: 1)",
                f"Vedic Chitrapaksha Lahiri ayanamsa: {vedic_ayanamsa_deg}° (ID: 0)",
            ],
        )

        return UnifiedMarriageResponse(
            final_verdict=final_verdict,
            timing_status=timing_status,
            kp_promise=kp_promise,
            vedic_promise=vedic_promise,
            birth_time_sensitivity=sensitivity_report,
            timing=timing_report,
            reconciliation_rule_id="UNI-MARR-REC-001",
            reconciliation_provenance=RuleProvenanceTag.PROJECT_ENGINEERING_POLICY,
            metadata=metadata,
        )
