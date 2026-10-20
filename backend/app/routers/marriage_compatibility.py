"""Marriage Compatibility FastAPI Router.

Provides deterministic endpoints for dual-horoscope marriage compatibility analysis
synthesizing:
- Traditional Tamil 10 Poruthams
- North Indian 36-Point Ashtakoota
- Comprehensive Vedic D1 & D9 Navamsa Marriage Analysis
- Mutual Kuja Dosha & South Indian Papasamya Balancing
- Bidirectional Cross-Chart Synastry Overlays
- Read-Only KP 7th Cuspal Sub-Lord & Timing Adapter
- Phase 8 Master Composite Compatibility Assessment
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.marriage import (
    MarriageCompatibilityRequest,
    MarriageCompatibilityResponse,
    MarriageCompatibilityError,
    RuleRegisterItem,
    RuleRegisterResponse,
    SaveMarriageCompatibilityReportRequest,
    UpdateMarriageReportMetadataRequest,
    SavedMarriageReportSummaryResponse,
    SavedMarriageReportDetailResponse,
    SavedMarriageReportListResponse,
)
from app.services.auth_service import get_current_user
from app.services.marriage_engine.service import run_marriage_compatibility_analysis
from app.services.marriage_engine.report_repository import (
    save_marriage_report,
    list_marriage_reports,
    get_marriage_report,
    update_marriage_report_metadata,
    delete_marriage_report,
)

logger = logging.getLogger("gai.api.marriage_compatibility")
security = HTTPBearer(auto_error=False)

router = APIRouter(tags=["Marriage Compatibility"])


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """Optional authentication: returns user dict if valid Bearer token provided, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


@router.post(
    "/analyze",
    response_model=MarriageCompatibilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Marriage Compatibility",
    description=(
        "Evaluates comprehensive marriage compatibility for a groom and bride using "
        "deterministic Vedic and KP astrology. Synthesizes Tamil 10 Poruthams, North Indian "
        "36-point Ashtakoota, Vedic D1/D9 houses and Karakas, mutual Kuja and Papasamya doshas, "
        "bidirectional synastry, and KP 7th Cuspal Sub-Lord promise. Supports direct birth "
        "particulars or authenticated saved horoscope UUIDs."
    ),
    responses={
        200: {
            "model": MarriageCompatibilityResponse,
            "description": "Deterministic marriage compatibility assessment completed successfully.",
        },
        400: {
            "model": MarriageCompatibilityError,
            "description": "Invalid saved horoscope UUID or malformed request parameters.",
        },
        401: {
            "model": MarriageCompatibilityError,
            "description": "Authentication token required to access saved horoscopes.",
        },
        404: {
            "model": MarriageCompatibilityError,
            "description": "Saved horoscope not found or unauthorized.",
        },
        422: {
            "model": MarriageCompatibilityError,
            "description": "Validation error: invalid coordinates, missing required birth parameters, or out-of-range dates.",
        },
        500: {
            "model": MarriageCompatibilityError,
            "description": "Calculation error during astronomical or astrological evaluation.",
        },
    },
)
async def analyze_marriage_compatibility(
    request: MarriageCompatibilityRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> MarriageCompatibilityResponse:
    """Execute complete deterministic marriage compatibility pipeline."""
    try:
        response = run_marriage_compatibility_analysis(
            request=request,
            current_user=current_user,
        )
        return response
    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning(f"Validation error in marriage compatibility: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        ) from None
    except Exception as exc:
        logger.exception("Unexpected error in marriage compatibility analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected calculation error occurred: {str(exc)}",
        ) from None


@router.get(
    "/rules",
    response_model=RuleRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Marriage Compatibility Rule Register",
    description="Returns the inventory of approved, source-backed astrological rules evaluated by the engine.",
)
async def get_marriage_compatibility_rules() -> RuleRegisterResponse:
    """Return approved astrological ruleset register."""
    approved_rules = [
        RuleRegisterItem(
            rule_id="POR-01",
            name="Dina Porutham",
            tradition="Tamil Traditional",
            classical_source="Kalaprakasika Ch. 12",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Evaluates health, longevity, and day-to-day prosperity through Moon nakshatra distance.",
        ),
        RuleRegisterItem(
            rule_id="POR-02",
            name="Gana Porutham",
            tradition="Tamil Traditional",
            classical_source="Kalaprakasika Ch. 12",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Evaluates temperament, instinctive wavelength, and lifestyle compatibility (Deva, Manushya, Rakshasa).",
        ),
        RuleRegisterItem(
            rule_id="POR-09",
            name="Rajju Porutham",
            tradition="Tamil Traditional",
            classical_source="Kalaprakasika Ch. 12",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Critical traditional vitality factor. Identical Rajju (Rajju Thatu) is a non-negotiable classical veto with zero cancellation.",
        ),
        RuleRegisterItem(
            rule_id="POR-10",
            name="Vedha Porutham",
            tradition="Tamil Traditional",
            classical_source="Kalaprakasika Ch. 12",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Astrological repulsion factor between incompatible nakshatras; veto under South Indian canon.",
        ),
        RuleRegisterItem(
            rule_id="KOT-08",
            name="Nadi Koota",
            tradition="North Indian Ashtakoota",
            classical_source="Muhurta Chintamani",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Physiological and genetic compatibility factor (8.0 points); uncancelled identical Nadi is a primary veto.",
        ),
        RuleRegisterItem(
            rule_id="DOS-KUJA-01",
            name="Kuja / Manglik Dosha",
            tradition="Parashari & South Indian",
            classical_source="Brihat Parashara Hora Shastra Ch. 81",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Mars placement in houses 1, 2, 4, 7, 8, 12 from Lagna, Moon, and Venus with 8 classical cancellation exceptions.",
        ),
        RuleRegisterItem(
            rule_id="DOS-PAPA-01",
            name="Papasamya Malefic Balancing",
            tradition="South Indian Traditional",
            classical_source="Jataka Alankara & Phaladeepika",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Comparative malefic point balance ensuring groom carries equal or higher protective malefic load than bride.",
        ),
        RuleRegisterItem(
            rule_id="VED-MARR-01",
            name="7th House & 7th Lord (D1 & D9)",
            tradition="Vedic Parashari",
            classical_source="BPHS Ch. 18, Phaladeepika Ch. 10",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Disposition and aspectual influences on the 7th house and its lord in Rasi and Navamsa.",
        ),
        RuleRegisterItem(
            rule_id="KP-MARR-01",
            name="KP 7th Cuspal Sub-Lord Promise",
            tradition="Krishnamurti Paddhati",
            classical_source="KP Reader II & III",
            approval_status="IMPLEMENTED_AND_VERIFIED",
            description="Evaluates 7th cusp sub-lord signification of supporting houses (2, 7, 11) vs denying houses (1, 6, 10).",
        ),
    ]
    return RuleRegisterResponse(
        engine_name="Gokul's Astrological Insights - Marriage Compatibility Engine",
        ruleset_version="1.0.0",
        rules=approved_rules,
    )


# ===========================================================================
# Phase 11C: Saved Reports Persistence Endpoints
# ===========================================================================

@router.post(
    "/saved",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save Marriage Compatibility Report",
    description=(
        "Persists a completed marriage compatibility report as an immutable calculation snapshot. "
        "Enforces ownership verification on any linked horoscopes and automatically allocates a "
        "collision-free sequential display number for the authenticated user."
    ),
)
@router.post(
    "/reports",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_saved_marriage_compatibility_report(
    payload: SaveMarriageCompatibilityReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedMarriageReportDetailResponse:
    """Save a completed compatibility report to database."""
    is_admin = current_user.get("role") == "admin"
    record = save_marriage_report(
        user_id=str(current_user["id"]),
        payload=payload,
        is_admin=is_admin,
    )
    return SavedMarriageReportDetailResponse(**record)


@router.get(
    "/saved",
    response_model=SavedMarriageReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Saved Marriage Compatibility Reports",
    description="Retrieves saved marriage compatibility reports for the authenticated user, newest first.",
)
@router.get(
    "/reports",
    response_model=SavedMarriageReportListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_saved_marriage_compatibility_reports(
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    all_users: bool = Query(False, description="Admin only: list reports across all users"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedMarriageReportListResponse:
    """List saved marriage compatibility reports with pagination."""
    is_admin = (current_user.get("role") == "admin") and all_users
    records = list_marriage_reports(
        user_id=str(current_user["id"]),
        limit=limit,
        offset=offset,
        is_admin=is_admin,
    )
    summaries = [SavedMarriageReportSummaryResponse(**r) for r in records]
    return SavedMarriageReportListResponse(
        reports=summaries,
        total_count=len(summaries),
        limit=limit,
        offset=offset,
    )


@router.get(
    "/saved/{report_id}",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Saved Marriage Compatibility Report by ID",
    description="Retrieves a full saved report and calculation snapshot by UUID, enforcing ownership.",
)
@router.get(
    "/reports/{report_id}",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_saved_marriage_compatibility_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedMarriageReportDetailResponse:
    """Retrieve single saved report by UUID."""
    is_admin = current_user.get("role") == "admin"
    record = get_marriage_report(
        user_id=str(current_user["id"]),
        report_id=report_id,
        is_admin=is_admin,
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved marriage compatibility report not found or unauthorized.",
        )
    return SavedMarriageReportDetailResponse(**record)


@router.patch(
    "/saved/{report_id}",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Saved Marriage Compatibility Report Metadata",
    description=(
        "Updates only permitted metadata: title, groom_name, bride_name, groom_saved_horoscope_id, "
        "and bride_saved_horoscope_id. All calculation snapshots, scores, parameters, and display numbers "
        "are strictly immutable and changes will be rejected."
    ),
)
@router.patch(
    "/reports/{report_id}",
    response_model=SavedMarriageReportDetailResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def update_saved_marriage_compatibility_report_metadata(
    report_id: str,
    payload: UpdateMarriageReportMetadataRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedMarriageReportDetailResponse:
    """Update permitted metadata of a saved marriage compatibility report."""
    is_admin = current_user.get("role") == "admin"
    update_dict = payload.model_dump(exclude_unset=True)
    updated = update_marriage_report_metadata(
        user_id=str(current_user["id"]),
        report_id=report_id,
        update_data=update_dict,
        is_admin=is_admin,
    )
    return SavedMarriageReportDetailResponse(**updated)


@router.delete(
    "/saved/{report_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Saved Marriage Compatibility Report",
    description="Deletes a saved marriage compatibility report, enforcing user ownership.",
)
@router.delete(
    "/reports/{report_id}",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def delete_saved_marriage_compatibility_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Delete a saved marriage compatibility report."""
    is_admin = current_user.get("role") == "admin"
    success = delete_marriage_report(
        user_id=str(current_user["id"]),
        report_id=report_id,
        is_admin=is_admin,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved marriage compatibility report not found or delete unauthorized.",
        )
    return {
        "success": True,
        "message": "Saved marriage compatibility report deleted successfully.",
    }
