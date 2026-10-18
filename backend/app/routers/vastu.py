"""Vastu Calculation & Report Management Router.

Deterministic, rule-based endpoints for Vastu directions, layout evaluations,
classical Dosha analysis, and Supabase persistence.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.vastu import (
    VastuDirectionsResponse,
    VastuEvaluationRequest,
    VastuEvaluationResponse,
    SaveVastuReportRequest,
    SavedVastuReportResponse,
    SavedVastuReportsListResponse,
)
from app.services.auth_service import get_current_user
from app.services.vastu_service import (
    get_all_directions_metadata,
    evaluate_vastu_layout,
    save_vastu_report,
    list_vastu_reports,
    get_vastu_report,
    update_vastu_report,
    delete_vastu_report,
)

router = APIRouter(prefix="/api/v1/vastu", tags=["Vastu Shastra"])


# ------------------------------------------------------------------------------
# 1. Direction & Metadata Endpoints (Public / Informational)
# ------------------------------------------------------------------------------

@router.get("/directions", response_model=VastuDirectionsResponse, summary="Get Vastu Directions & 32 Padas Metadata")
def get_vastu_directions() -> VastuDirectionsResponse:
    """Returns 8 and 16 standardized directions with azimuth spans and 32 outer deity padas."""
    try:
        return get_all_directions_metadata()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load Vastu direction metadata: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 2. Layout Evaluation Endpoint (Calculations)
# ------------------------------------------------------------------------------

@router.post("/evaluate", response_model=VastuEvaluationResponse, summary="Evaluate Property Vastu Layout")
def evaluate_property_layout(request: VastuEvaluationRequest) -> VastuEvaluationResponse:
    """Evaluates property room placements against classical Vastu Shastra rules.
    Normalizes scores strictly across assessable factors without penalizing missing data.
    """
    try:
        return evaluate_vastu_layout(request)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vastu evaluation failed: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 3. Report Persistence Endpoints (Authenticated)
# ------------------------------------------------------------------------------

@router.post("/reports", response_model=SavedVastuReportResponse, status_code=status.HTTP_201_CREATED, summary="Save Vastu Assessment")
def save_report(
    request: SaveVastuReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedVastuReportResponse:
    """Saves a completed Vastu evaluation to the user's account in Supabase.
    Automatically assigns a concurrency-safe sequential display number.
    """
    try:
        res = save_vastu_report(user_id=current_user["id"], request=request)
        return SavedVastuReportResponse(**res)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save Vastu report: {str(exc)}",
        )


@router.get("/reports", response_model=SavedVastuReportsListResponse, summary="List User's Saved Vastu Assessments")
def list_reports(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedVastuReportsListResponse:
    """Retrieves paginated saved Vastu assessments belonging to the authenticated user."""
    try:
        is_admin = current_user.get("role") == "admin"
        reports_raw, total_count = list_vastu_reports(
            user_id=current_user["id"], is_admin=is_admin, limit=limit, offset=offset
        )
        reports = [SavedVastuReportResponse(**r) for r in reports_raw]
        return SavedVastuReportsListResponse(
            reports=reports,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Vastu reports: {str(exc)}",
        )


@router.get("/reports/{report_id}", response_model=SavedVastuReportResponse, summary="Get Single Vastu Assessment")
def get_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedVastuReportResponse:
    """Fetches a saved Vastu report by UUID, enforcing ownership verification."""
    try:
        is_admin = current_user.get("role") == "admin"
        report = get_vastu_report(user_id=current_user["id"], report_id=report_id, is_admin=is_admin)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vastu report '{report_id}' not found or unauthorized.",
            )
        return SavedVastuReportResponse(**report)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Vastu report: {str(exc)}",
        )


@router.put("/reports/{report_id}", response_model=SavedVastuReportResponse, summary="Update Saved Vastu Assessment")
def update_report(
    report_id: str,
    request: SaveVastuReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedVastuReportResponse:
    """Updates an existing saved Vastu report, strictly verifying user ownership."""
    try:
        is_admin = current_user.get("role") == "admin"
        updated = update_vastu_report(
            user_id=current_user["id"], report_id=report_id, request=request, is_admin=is_admin
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vastu report '{report_id}' not found or unauthorized.",
            )
        return SavedVastuReportResponse(**updated)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Vastu report: {str(exc)}",
        )


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Saved Vastu Assessment")
def delete_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Deletes a saved Vastu report by UUID, strictly enforcing ownership."""
    try:
        is_admin = current_user.get("role") == "admin"
        success = delete_vastu_report(user_id=current_user["id"], report_id=report_id, is_admin=is_admin)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vastu report '{report_id}' not found or unauthorized.",
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Vastu report: {str(exc)}",
        )
