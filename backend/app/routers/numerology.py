"""Numerology Calculation & Reports Router.

Deterministic endpoints for Traditional Numerology, Destiny Matrix,
Advanced Analysis (Lo Shu / Pinnacles), and Supabase Report Management.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.numerology import (
    TraditionalNumerologyRequest,
    TraditionalNumerologyResponse,
    TraditionalNumberDetail,
    DestinyMatrixRequest,
    DestinyMatrixResponse,
    AdvancedAnalysisRequest,
    AdvancedAnalysisResponse,
    SaveNumerologyReportRequest,
    SavedNumerologyReportResponse,
    NumerologyMetadataResponse,
)
from app.services.auth_service import get_current_user
from app.services.numerology import (
    calculate_life_path,
    calculate_birthday_number,
    calculate_attitude_number,
    calculate_personal_year,
    calculate_name_numbers,
    calculate_maturity_number,
    get_interpretation_for_number,
    generate_synthesized_reports,
    calculate_destiny_matrix,
    calculate_compatibility,
    calculate_advanced_analysis,
    save_numerology_report,
    list_numerology_reports,
    get_numerology_report,
    delete_numerology_report,
    ENGINE_VERSION,
)

router = APIRouter(prefix="/api/v1/numerology", tags=["Numerology"])


# ------------------------------------------------------------------------------
# 1. Traditional Numerology
# ------------------------------------------------------------------------------

@router.post("/traditional", response_model=TraditionalNumerologyResponse)
def compute_traditional_numerology(request: TraditionalNumerologyRequest) -> TraditionalNumerologyResponse:
    """Calculate core numbers, master numbers, and interpretations for Traditional Numerology."""
    try:
        lang = request.language
        conv = request.system_convention

        # 1. Birthdate derivations
        lp, lp_method = calculate_life_path(request.birth_date)
        b_num, b_method = calculate_birthday_number(request.birth_date)
        att, att_method = calculate_attitude_number(request.birth_date)
        py, py_method = calculate_personal_year(request.birth_date, target_year=2026)

        # 2. Name derivations
        name_res = calculate_name_numbers(request.full_name, convention=conv)
        expr = name_res["expression"]
        soul = name_res["soul_urge"]
        pers = name_res["personality"]

        # 3. Maturity number
        mat, mat_method = calculate_maturity_number(lp, expr)

        # 4. Interpretations
        def build_detail(name: str, val: int, method: str) -> TraditionalNumberDetail:
            interp = get_interpretation_for_number("life_path", val, lang=lang)
            return TraditionalNumberDetail(
                number_name=name,
                number_value=val,
                calculation_method=method,
                is_master=val in (11, 22, 33),
                short_interpretation=interp["short"],
                detailed_interpretation=interp["detailed"],
                key_attributes=interp["attributes"],
            )

        lp_detail = build_detail("Life Path Number", lp, lp_method)
        expr_detail = build_detail("Expression / Destiny Number", expr, name_res["expression_method"])
        soul_detail = build_detail("Soul Urge Number", soul, name_res["soul_urge_method"])
        pers_detail = build_detail("Personality Number", pers, name_res["personality_method"])
        bday_detail = build_detail("Birthday Number", b_num, b_method)
        att_detail = build_detail("Attitude Number", att, att_method)
        mat_detail = build_detail("Maturity / Divine Purpose Number", mat, mat_method)
        py_detail = build_detail("Personal Year Number (2026)", py, py_method)

        # 5. Synthesized themes
        synth = generate_synthesized_reports(lp, expr, soul, pers, conv, lang=lang)

        return TraditionalNumerologyResponse(
            person_name=request.full_name.strip(),
            birth_date=request.birth_date,
            system_convention=conv,
            engine_version=ENGINE_VERSION,
            life_path=lp_detail,
            expression_destiny=expr_detail,
            soul_urge=soul_detail,
            personality=pers_detail,
            birthday_number=bday_detail,
            attitude_number=att_detail,
            maturity_number=mat_detail,
            personal_year=py_detail,
            karmic_lessons=name_res["karmic_lessons"],
            hidden_passion=name_res["hidden_passion"],
            strengths=synth["strengths"],
            challenges=synth["challenges"],
            career_tendencies=synth["career_tendencies"],
            financial_tendencies=synth["financial_tendencies"],
            love_themes=synth["love_themes"],
            overall_synthesis=synth["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Traditional Numerology calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 2. Destiny Matrix
# ------------------------------------------------------------------------------

@router.post("/destiny-matrix", response_model=DestinyMatrixResponse)
def compute_destiny_matrix(request: DestinyMatrixRequest) -> DestinyMatrixResponse:
    """Calculate 22-Arcana Destiny Matrix octagram, karmic tail, purpose, and age timeline."""
    try:
        matrix = calculate_destiny_matrix(request.birth_date, lang=request.language)

        compatibility = None
        if request.partner_birth_date:
            compatibility = calculate_compatibility(
                request.birth_date,
                request.partner_birth_date,
                name1=request.person_name or "Partner 1",
                name2=request.partner_name or "Partner 2",
                lang=request.language,
            )

        return DestinyMatrixResponse(
            birth_date=request.birth_date,
            person_name=request.person_name,
            engine_version=ENGINE_VERSION,
            day_arcana=matrix["day_arcana"],
            month_arcana=matrix["month_arcana"],
            year_arcana=matrix["year_arcana"],
            karmic_tail_base=matrix["karmic_tail_base"],
            karmic_tail_triad=matrix["karmic_tail_triad"],
            comfort_zone=matrix["comfort_zone"],
            father_spirit=matrix["father_spirit"],
            mother_spirit=matrix["mother_spirit"],
            father_matter=matrix["father_matter"],
            mother_matter=matrix["mother_matter"],
            love_line=matrix["love_line"],
            money_line=matrix["money_line"],
            purpose=matrix["purpose"],
            age_timeline=matrix["age_timeline"],
            compatibility=compatibility,
            strengths=matrix["strengths"],
            challenges=matrix["challenges"],
            career_tendencies=matrix["career_tendencies"],
            financial_tendencies=matrix["financial_tendencies"],
            love_themes=matrix["love_themes"],
            overall_synthesis=matrix["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Destiny Matrix calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 3. Advanced Analysis (Lo Shu, Pinnacles, Yuan Integration)
# ------------------------------------------------------------------------------

@router.post("/advanced", response_model=AdvancedAnalysisResponse)
def compute_advanced_analysis(request: AdvancedAnalysisRequest) -> AdvancedAnalysisResponse:
    """Execute Advanced Analysis: Lo Shu 3x3 Magic Square, Arrows of Pythagoras, Pinnacles & Challenges."""
    try:
        res = calculate_advanced_analysis(request.full_name, request.birth_date, lang=request.language)
        return AdvancedAnalysisResponse(
            full_name=request.full_name.strip(),
            birth_date=request.birth_date,
            engine_version=ENGINE_VERSION,
            unicode_derived_name_number=res["unicode_derived_name_number"],
            lo_shu=res["lo_shu"],
            pinnacles_challenges=res["pinnacles_challenges"],
            karmic_debts=res["karmic_debts"],
            karmic_lessons=res["karmic_lessons"],
            dominant_vibrations=res["dominant_vibrations"],
            strengths=res["strengths"],
            challenges=res["challenges"],
            career_tendencies=res["career_tendencies"],
            financial_tendencies=res["financial_tendencies"],
            love_themes=res["love_themes"],
            overall_synthesis=res["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced Analysis calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 4. Engine Metadata & Diagnostics
# ------------------------------------------------------------------------------

@router.get("/metadata", response_model=NumerologyMetadataResponse)
def get_numerology_metadata() -> NumerologyMetadataResponse:
    """Return calculation engine versions, available conventions, and operational status."""
    return NumerologyMetadataResponse(
        service="Gokul's Astrological Insights - Numerology Engine",
        engine_version=ENGINE_VERSION,
        methods=[
            {
                "id": "traditional",
                "name": "Traditional Numerology",
                "description": "Calculates Life Path, Expression, Soul Urge, Personality, Attitude, and Maturity numbers with Master Number (11, 22, 33) preservation.",
            },
            {
                "id": "destiny_matrix",
                "name": "Destiny Matrix (22 Arcana)",
                "description": "22 Major Arcana reduction octagram mapping, ancestral lines, karmic tail, love/money entrance, age cycles (0-80), and couples compatibility.",
            },
            {
                "id": "advanced",
                "name": "Advanced Analysis & Yuan Integration",
                "description": "Yuan-compatible Unicode code-point name reduction, 3x3 Lo Shu magic square, 8 arrows of Pythagoras, 4 Life Pinnacles, and 4 Life Challenges.",
            },
        ],
        conventions=[
            {"id": "pythagorean", "name": "Pythagorean (Western Standard 1-9)", "default": True},
            {"id": "chaldean", "name": "Chaldean (Ancient Esoteric 1-8)", "default": False},
        ],
        supported_languages=["en", "ta"],
        disclaimer=(
            "Numerological calculations and interpretations are for self-reflection, personal exploration, "
            "and philosophical enrichment. They are not deterministic scientific predictions or guaranteed outcomes."
        ),
    )


# ------------------------------------------------------------------------------
# 5. Saved Reports Persistence Endpoints
# ------------------------------------------------------------------------------

@router.post("/reports", response_model=SavedNumerologyReportResponse)
def create_report(
    payload: SaveNumerologyReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedNumerologyReportResponse:
    """Persist generated report to Supabase with transactional advisory-lock sequential display numbering."""
    try:
        report = save_numerology_report(current_user["id"], payload)
        return SavedNumerologyReportResponse(
            id=str(report["id"]),
            user_id=str(report["user_id"]),
            display_number=report["display_number"],
            person_name=report["person_name"],
            birth_date=str(report["birth_date"]),
            method=report["method"],
            system_convention=report["system_convention"],
            calculation_data=report["calculation_data"],
            interpretation_data=report["interpretation_data"],
            engine_version=report["engine_version"],
            created_at=str(report["created_at"]),
            updated_at=str(report["updated_at"]),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist numerology report: {str(exc)}",
        )


@router.get("/reports")
def list_reports(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve saved numerology reports for the authenticated user, or all for admins."""
    is_admin = current_user.get("role") == "admin"
    reports = list_numerology_reports(current_user["id"], is_admin=is_admin, limit=limit, offset=offset)
    return {"reports": reports, "count": len(reports)}


@router.get("/reports/{report_id}")
def get_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve specific saved report, enforcing user ownership or admin privilege."""
    is_admin = current_user.get("role") == "admin"
    report = get_numerology_report(current_user["id"], report_id, is_admin=is_admin)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Numerology report not found or unauthorized.",
        )
    return report


@router.delete("/reports/{report_id}")
def delete_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a saved report, enforcing user ownership or admin privilege."""
    is_admin = current_user.get("role") == "admin"
    success = delete_numerology_report(current_user["id"], report_id, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or delete unauthorized.",
        )
    return {"success": True, "message": "Numerology report removed successfully."}
