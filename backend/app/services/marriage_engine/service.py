"""Marriage Compatibility Orchestration Service.

Orchestrates the complete deterministic evaluation of groom and bride horoscopes:
1. Resolves input data (direct birth particulars or authenticated saved horoscope).
2. Generates validated MarriageChartContext instances via XALEN ephemeris adapters.
3. Invokes Phase 1 to Phase 7 evaluators in strict topological order:
   - Phase 2: Tamil 10 Poruthams (porutham_engine)
   - Phase 3: North Indian Ashtakoota (ashtakoota_engine)
   - Phase 4: Dual Vedic Marriage Analysis (vedic_analysis)
   - Phase 5: Mutual Doshas & Papasamya (mutual_doshas)
   - Phase 6: Bidirectional Synastry (synastry)
   - Phase 7: KP 7th CSL & Timing Adapter (kp_adapter)
4. Invokes Phase 8 Composite Marriage Compatibility Assessment (composite_assessment).
5. Assembles strongly typed MarriageCompatibilityResponse with zero scale mixing,
   independent scores preserved, cross-tradition conflict detection, and non-deterministic disclaimers.
"""

from __future__ import annotations
import dataclasses
import hashlib
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.marriage import (
    MarriagePartnerInput,
    MarriageCompatibilityRequest,
    MarriageCompatibilityResponse,
    PersonProfileSummary,
    CategoryVerdictModel,
    ConflictFindingModel,
    CompositeAssessmentSummary,
    FinalAssessmentSummary,
)
from app.services.auth_service import get_supabase_client
from app.services.ephemeris import calculate_full_horoscope
from app.services.marriage_engine.adapters import (
    build_chart_context_from_birth_input,
    build_chart_context_from_horoscope_response,
)
from app.services.marriage_engine.models import (
    Gender,
    MarriageChartContext,
    SIGN_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    ConflictFinding,
    ConflictType,
)
from app.services.marriage_engine.porutham_engine import evaluate_tamil_10_poruthams
from app.services.marriage_engine.ashtakoota_engine import evaluate_ashtakoota_matching
from app.services.marriage_engine.vedic_analysis import evaluate_dual_vedic_marriage_analysis
from app.services.marriage_engine.mutual_doshas import evaluate_mutual_dosha_analysis
from app.services.marriage_engine.synastry import evaluate_bidirectional_synastry
from app.services.marriage_engine.kp_adapter import evaluate_kp_marriage_analysis
from app.services.marriage_engine.composite_assessment import (
    evaluate_composite_marriage_assessment,
    COMPOSITE_DISCLAIMER_EN,
    COMPOSITE_DISCLAIMER_TA,
)

logger = logging.getLogger("gai.marriage_service")


def _validate_uuid_string(val: str) -> str:
    """Validates that a string is a well-formed UUID."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid saved horoscope UUID format: '{val}'.",
        )


def _resolve_partner_chart(
    partner_input: MarriagePartnerInput,
    default_gender: str,
    person_id: str,
    ayanamsa_id: int,
    house_system_id: int,
    current_user: Optional[Dict[str, Any]],
) -> Tuple[MarriageChartContext, bool]:
    """Resolve a MarriagePartnerInput into a validated MarriageChartContext.

    Supports:
    1. Authenticated saved horoscope retrieval with strict user ownership validation.
    2. Transient ad-hoc birth input without requiring database persistence.

    Returns:
        Tuple of (MarriageChartContext, is_birth_time_approximate)
    """
    is_approximate = bool(partner_input.is_birth_time_approximate)
    resolved_name = (partner_input.name or person_id).strip()
    resolved_gender_str = (partner_input.gender or default_gender).strip().lower()
    gender_enum = Gender.FEMALE if "female" in resolved_gender_str else Gender.MALE

    # Case A: Saved horoscope requested
    if partner_input.saved_horoscope_id:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required to access saved horoscopes.",
            )

        clean_id = _validate_uuid_string(partner_input.saved_horoscope_id)
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable. Database configuration missing.",
            )

        is_admin = current_user.get("role") == "admin"
        horoscope_row: Optional[Dict[str, Any]] = None
        try:
            resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
            if resp.data and len(resp.data) > 0:
                row = resp.data[0]
                if is_admin or str(row.get("user_id")) == str(current_user["id"]):
                    horoscope_row = row
        except Exception as err:
            logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

        if not horoscope_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saved horoscope '{clean_id}' not found or unauthorized.",
            )

        calc_result = horoscope_row.get("calculation_result") or {}
        horo_part = calc_result.get("horoscope")

        if horo_part and isinstance(horo_part, dict):
            chart_ctx = build_chart_context_from_horoscope_response(
                horoscope=horo_part,
                person_id=person_id,
                person_name=resolved_name,
                gender=gender_enum,
                birth_date_iso=str(horoscope_row.get("birth_date", "")),
                birth_time_iso=str(horoscope_row.get("birth_time", "")),
                timezone_str=str(horoscope_row.get("timezone", "Asia/Kolkata")),
                latitude=float(horoscope_row.get("latitude", 13.0827)),
                longitude=float(horoscope_row.get("longitude", 80.2707)),
            )
            return chart_ctx, is_approximate

        # If cached horoscope snapshot is missing, recompute from stored coordinates
        computed = calculate_full_horoscope(
            birth_date=horoscope_row["birth_date"],
            birth_time=horoscope_row["birth_time"],
            timezone_str=horoscope_row["timezone"],
            latitude=horoscope_row["latitude"],
            longitude=horoscope_row["longitude"],
            ayanamsa_id=horoscope_row.get("ayanamsa_id", ayanamsa_id),
            house_system_id=horoscope_row.get("house_system_id", house_system_id),
            include_varga=True,
            include_panchang=True,
        )
        chart_ctx = build_chart_context_from_horoscope_response(
            horoscope=computed,
            person_id=person_id,
            person_name=resolved_name,
            gender=gender_enum,
            birth_date_iso=str(horoscope_row["birth_date"]),
            birth_time_iso=str(horoscope_row["birth_time"]),
            timezone_str=str(horoscope_row["timezone"]),
            latitude=float(horoscope_row["latitude"]),
            longitude=float(horoscope_row["longitude"]),
        )
        return chart_ctx, is_approximate

    # Case B: Direct transient birth parameters
    if (
        not partner_input.birth_date
        or not partner_input.birth_time
        or not partner_input.timezone
        or partner_input.latitude is None
        or partner_input.longitude is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing mandatory birth parameters for {person_id} ({resolved_name}).",
        )

    birth = BirthInput(
        birth_date=partner_input.birth_date,
        birth_time=partner_input.birth_time,
        timezone=partner_input.timezone,
        latitude=partner_input.latitude,
        longitude=partner_input.longitude,
    )

    chart_ctx = build_chart_context_from_birth_input(
        birth=birth,
        person_id=person_id,
        person_name=resolved_name,
        gender=gender_enum,
        ayanamsa_id=ayanamsa_id,
        house_system_id=house_system_id,
    )
    return chart_ctx, is_approximate


def _build_profile_summary(ctx: MarriageChartContext) -> PersonProfileSummary:
    """Extract strongly typed profile summary from MarriageChartContext."""
    nak_idx = ctx.moon_nakshatra_idx
    nak_ta = NAKSHATRA_NAMES_TA[nak_idx - 1] if 1 <= nak_idx <= 27 else ""

    venus_sign = ctx.grahas["Venus"].sign_name if "Venus" in ctx.grahas else ""
    mars_sign = ctx.grahas["Mars"].sign_name if "Mars" in ctx.grahas else ""
    jupiter_sign = ctx.grahas["Jupiter"].sign_name if "Jupiter" in ctx.grahas else ""

    return PersonProfileSummary(
        name=ctx.person_name,
        gender=ctx.gender.value,
        birth_date=ctx.birth_date_iso,
        birth_time=ctx.birth_time_iso,
        timezone=ctx.timezone,
        latitude=ctx.latitude,
        longitude=ctx.longitude,
        ascendant_sign=ctx.ascendant_sign_name,
        ascendant_sign_tamil=ctx.ascendant_sign_name_tamil,
        ascendant_degree=round(ctx.ascendant_degree, 4),
        ascendant_nakshatra=ctx.ascendant_nakshatra_name,
        ascendant_pada=ctx.ascendant_nakshatra_pada,
        ascendant_navamsa_sign=SIGN_NAMES_EN.get(ctx.ascendant_navamsa_sign_idx, ""),
        moon_sign=ctx.moon_sign_name,
        moon_sign_tamil=ctx.moon_sign_name_tamil,
        moon_degree=round(ctx.moon_degree, 4),
        moon_nakshatra=ctx.moon_nakshatra_name,
        moon_nakshatra_tamil=nak_ta,
        moon_pada=ctx.moon_nakshatra_pada,
        moon_navamsa_sign=SIGN_NAMES_EN.get(ctx.moon_navamsa_sign_idx, ""),
        venus_sign=venus_sign,
        mars_sign=mars_sign,
        jupiter_sign=jupiter_sign,
    )


def run_marriage_compatibility_analysis(
    request: MarriageCompatibilityRequest,
    current_user: Optional[Dict[str, Any]] = None,
) -> MarriageCompatibilityResponse:
    """Execute complete deterministic marriage compatibility analysis pipeline.

    1. Resolves groom and bride charts safely.
    2. Runs Phases 1–7 evaluators deterministically.
    3. Runs Phase 8 composite assessment.
    4. Formulates explainable, non-guarantee response.
    """
    # 1. Resolve Charts
    groom_chart, groom_approx = _resolve_partner_chart(
        partner_input=request.groom,
        default_gender="male",
        person_id="groom",
        ayanamsa_id=request.ayanamsa_id,
        house_system_id=request.house_system_id,
        current_user=current_user,
    )

    bride_chart, bride_approx = _resolve_partner_chart(
        partner_input=request.bride,
        default_gender="female",
        person_id="bride",
        ayanamsa_id=request.ayanamsa_id,
        house_system_id=request.house_system_id,
        current_user=current_user,
    )

    # 2. Execute Phase 2: Tamil 10 Poruthams
    tamil_porutham = evaluate_tamil_10_poruthams(groom_chart, bride_chart)

    # 3. Execute Phase 3: North Indian Ashtakoota
    ashtakoota = evaluate_ashtakoota_matching(groom_chart, bride_chart)

    # 4. Execute Phase 4: Vedic Marriage Analysis (D1 & D9)
    dual_vedic = evaluate_dual_vedic_marriage_analysis(groom_chart, bride_chart)

    # Ensure 7th house has is_afflicted attribute for Phase 8 compatibility
    for anal in (dual_vedic.groom_analysis, dual_vedic.bride_analysis):
        for h_num, h_finding in anal.houses_analysis.items():
            if not hasattr(h_finding, "is_afflicted"):
                h_finding.is_afflicted = len(getattr(h_finding, "conflicting_influences", [])) > 0

    # 5. Execute Phase 5: Mutual Doshas & Papasamya
    mutual_doshas = evaluate_mutual_dosha_analysis(groom_chart, bride_chart)

    # 6. Execute Phase 6: Bidirectional Synastry
    synastry = evaluate_bidirectional_synastry(groom_chart, bride_chart)

    # 7. Execute Phase 7: KP 7th CSL & Timing Adapter
    kp_marriage = None
    if request.include_kp:
        try:
            kp_marriage = evaluate_kp_marriage_analysis(groom_chart, bride_chart)
        except Exception as exc:
            logger.warning(f"KP marriage evaluation skipped or failed: {exc}")

    # 8. Execute Phase 8: Composite Marriage Assessment
    composite_res = evaluate_composite_marriage_assessment(
        groom_chart=groom_chart,
        bride_chart=bride_chart,
        tamil_porutham=tamil_porutham,
        ashtakoota=ashtakoota,
        groom_vedic=dual_vedic.groom_analysis,
        bride_vedic=dual_vedic.bride_analysis,
        mutual_doshas=mutual_doshas,
        synastry=synastry,
        kp_marriage=kp_marriage,
    )

    # 9. Handle Approximate Birth Time Uncertainty
    if groom_approx or bride_approx:
        approx_targets = []
        if groom_approx:
            approx_targets.append(f"Groom ({groom_chart.person_name})")
        if bride_approx:
            approx_targets.append(f"Bride ({bride_chart.person_name})")
        joined_targets = " and ".join(approx_targets)

        uncertainty_msg = (
            f"Approximate birth time provided for {joined_targets}; divisional charts (D9 Navamsa) "
            "and KP cuspal sub-lords carry elevated boundary sensitivity. Professional rectification advised."
        )
        uncertainty_msg_ta = (
            f"{joined_targets} பிறப்பு நேரம் தோராயமானது என குறிப்பிடப்பட்டுள்ளது; நவாம்சம் (D9) "
            "மற்றும் கே.பி உப அதிபதிகள் கூடுதல் உணர்திறன் கொண்டவை. நேர உறுதிப்படுத்தல் பரிந்துரைக்கப்படுகிறது."
        )

        composite_res.missing_or_uncertain_evidence.append(uncertainty_msg)
        composite_res.warnings.append(uncertainty_msg)

        has_boundary_conflict = any(
            c.conflict_type == ConflictType.BIRTH_TIME_BOUNDARY_SENSITIVITY
            for c in composite_res.conflicting_findings
        )
        if not has_boundary_conflict:
            composite_res.conflicting_findings.append(
                ConflictFinding(
                    conflict_type=ConflictType.BIRTH_TIME_BOUNDARY_SENSITIVITY,
                    title_en="Approximate Birth-Time Uncertainty",
                    title_ta="தோராயமான பிறப்பு நேர நிச்சயமற்ற தன்மை",
                    finding_a=f"User flagged approximate birth time for {joined_targets}.",
                    finding_b="Divisional ascendants and cuspal sub-lords can shift across 2-4 minute windows.",
                    resolution_principle="Preserve uncertainty transparently; emphasize Rasi/Moon matching over sensitive cuspal divisions.",
                    explanation_en=uncertainty_msg,
                    explanation_ta=uncertainty_msg_ta,
                    rule_sources=["VED-MARR-04", "RULE-MATRIX-08"],
                )
            )

    # 10. Assemble Response Models
    cat_models = {
        k: CategoryVerdictModel(
            category_id=v.category_id,
            category_name_en=v.category_name_en,
            category_name_ta=v.category_name_ta,
            status=v.status,
            tradition=v.tradition,
            score_summary=v.score_summary,
            key_factors=v.key_factors,
            vetoes_applied=v.vetoes_applied,
        )
        for k, v in composite_res.category_verdicts.items()
    }

    if not request.include_kp:
        cat_models["kp_promise"] = CategoryVerdictModel(
            category_id="kp_promise",
            category_name_en="KP 7th Cuspal Sub-Lord Promise",
            category_name_ta="கே.பி 7-ம் பாவ உப அதிபதி வாக்குறுதி",
            status="INDETERMINATE",
            tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
            score_summary="Data Unavailable (include_kp=False)",
            key_factors=["KP evaluation bypassed by request setting."],
        )
        cat_models["kp_timing"] = CategoryVerdictModel(
            category_id="kp_timing",
            category_name_en="KP Vimshottari Timing Window",
            category_name_ta="கே.பி தசா-புக்தி கால அமைவு",
            status="INDETERMINATE",
            tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
            score_summary="Data Unavailable (include_kp=False)",
            key_factors=["KP timing bypassed by request setting."],
        )

    conflict_models = [
        ConflictFindingModel(
            conflict_type=c.conflict_type.value if hasattr(c.conflict_type, "value") else str(c.conflict_type),
            title_en=c.title_en,
            title_ta=c.title_ta,
            finding_a=c.finding_a,
            finding_b=c.finding_b,
            resolution_principle=c.resolution_principle,
            explanation_en=c.explanation_en,
            explanation_ta=c.explanation_ta,
            rule_sources=c.rule_sources,
        )
        for c in composite_res.conflicting_findings
    ]

    outcome_str = composite_res.overall_outcome.value if hasattr(composite_res.overall_outcome, "value") else str(composite_res.overall_outcome)
    label_en_map = {
        "FAVOURABLE_UNDER_SELECTED_RULES": "Favourable Under Selected Rules",
        "MIXED_OR_CONDITIONAL": "Mixed or Conditional Compatibility",
        "UNFAVOURABLE_UNDER_SELECTED_RULES": "Unfavourable Under Selected Rules",
        "INDETERMINATE": "Indeterminate Compatibility",
    }
    label_ta_map = {
        "FAVOURABLE_UNDER_SELECTED_RULES": "தேர்ந்தெடுக்கப்பட்ட விதிகளின்படி சாதகமானது",
        "MIXED_OR_CONDITIONAL": "மிதமான அல்லது நிபந்தனைக்குட்பட்ட பொருத்தம்",
        "UNFAVOURABLE_UNDER_SELECTED_RULES": "தேர்ந்தெடுக்கப்பட்ட விதிகளின்படி பொருத்தமற்றது",
        "INDETERMINATE": "நிர்ணயிக்க முடியாத நிலை",
    }

    comp_summary = CompositeAssessmentSummary(
        overall_outcome=outcome_str,
        overall_outcome_label_en=label_en_map.get(outcome_str, outcome_str.replace("_", " ").title()),
        overall_outcome_label_ta=label_ta_map.get(outcome_str, "பொருத்த நிலை"),
        category_verdicts=cat_models,
        major_supportive_indicators=composite_res.major_supportive_indicators,
        major_challenging_indicators=composite_res.major_challenging_indicators,
        conflicting_findings=conflict_models,
        missing_or_uncertain_evidence=composite_res.missing_or_uncertain_evidence,
        recommended_astrologer_review=composite_res.recommended_astrologer_review,
        decision_path=composite_res.decision_path,
        disclaimers=composite_res.disclaimers or [COMPOSITE_DISCLAIMER_EN, COMPOSITE_DISCLAIMER_TA],
        rule_sources=composite_res.rule_sources,
        warnings=composite_res.warnings,
        explanation_en=composite_res.explanation_en,
        explanation_ta=composite_res.explanation_ta,
    )

    groom_prof = _build_profile_summary(groom_chart)
    bride_prof = _build_profile_summary(bride_chart)

    # Deterministic fingerprint
    fp_raw = f"{groom_chart.person_id}:{groom_chart.birth_date_iso}:{groom_chart.moon_degree:.4f}_{bride_chart.person_id}:{bride_chart.birth_date_iso}:{bride_chart.moon_degree:.4f}"
    reproducibility_fp = "SHA256:" + hashlib.sha256(fp_raw.encode("utf-8")).hexdigest()[:16]

    meta = CalculationMetadata(
        engine="XALEN 0.6.0 (Rust) + GAI Marriage Compatibility Engine 1.0.0",
        birth_utc_iso=f"{groom_chart.birth_date_iso}T{groom_chart.birth_time_iso}Z",
        julian_day_ut1=2450000.0,
        local_timezone=groom_chart.timezone,
        ayanamsa_id=request.ayanamsa_id,
        ayanamsa_name="Lahiri (Chitrapaksha)" if request.ayanamsa_id == 0 else "KP (Krishnamurti)",
        house_system_id=request.house_system_id,
        house_system_name="Whole Sign" if request.house_system_id == 0 else "Placidus",
        calculation_frame="Geocentric Sidereal",
        notes=[
            "Purely deterministic calculation.",
            "Tamil 10 Porutham (10.0 scale) and Ashtakoota (36.0 scale) preserved as independent metrics.",
            "Cross-tradition conflict detection active.",
        ],
    )

    fin_legacy = FinalAssessmentSummary(
        verdict=outcome_str,
        verdict_label_en=comp_summary.overall_outcome_label_en,
        verdict_label_ta=comp_summary.overall_outcome_label_ta,
        primary_strengths=composite_res.major_supportive_indicators[:3],
        primary_concerns=composite_res.major_challenging_indicators[:3],
        decision_path=composite_res.decision_path,
        scientific_disclaimer=COMPOSITE_DISCLAIMER_EN,
        reproducibility_fingerprint=reproducibility_fp,
    )

    return MarriageCompatibilityResponse(
        metadata=meta,
        groom_profile=groom_prof,
        bride_profile=bride_prof,
        composite_assessment=comp_summary,
        tamil_porutham=tamil_porutham,
        ashtakoota=ashtakoota,
        dosha_analysis=dataclasses.asdict(mutual_doshas),
        synastry=dataclasses.asdict(synastry),
        kp_marriage=dataclasses.asdict(kp_marriage) if kp_marriage else None,
        groom_vedic=dataclasses.asdict(dual_vedic.groom_analysis),
        bride_vedic=dataclasses.asdict(dual_vedic.bride_analysis),
        final_assessment=fin_legacy,
    )
