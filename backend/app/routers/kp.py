"""KP (Krishnamurti Paddhati) calculation and persistence router."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.kp import (
    KpRequest,
    KpResponse,
    HoraryKpRequest,
    HoraryKpResponse,
    SaveKpChartRequest,
    SavedKpChartItem,
    SavedKpChartListResponse,
)
from app.services.kp_service import calculate_kp_chart, calculate_horary_chart
from app.services.auth_service import get_current_user
from app.services.kp_engine.kp_chart_repository import (
    save_kp_chart,
    list_kp_charts,
    get_kp_chart,
    delete_kp_chart,
)

router = APIRouter(prefix="/api/v1/horoscope", tags=["KP"])


# 1. Natal KP Chart Calculation
@router.post("/kp", response_model=KpResponse, summary="Calculate complete KP Natal chart")
def calculate_horoscope_kp(request: KpRequest) -> KpResponse:
    """Calculate KP 249 sub-division positions, cuspal sub-lords, 4-tier significators, and Dasa."""
    try:
        response = calculate_kp_chart(
            birth=request,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
        )
        return response
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KP calculation failed: {str(exc)}",
        )


# 2. Horary Prashna (1-249) Calculation
@router.post("/kp/horary", response_model=HoraryKpResponse, summary="Calculate authentic KP Horary (1-249) chart")
def calculate_horary_kp(request: HoraryKpRequest) -> HoraryKpResponse:
    """Calculate authentic KP Horary chart with ARMC inversion, Placidus cusps, and significators."""
    try:
        response = calculate_horary_chart(request)
        return response
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KP Horary calculation failed: {str(exc)}",
        )


# 3. Persistence: Save KP Chart (Natal or Horary)
@router.post("/kp/charts", response_model=SavedKpChartItem, summary="Save KP Chart snapshot")
def save_chart(
    request: SaveKpChartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        record = save_kp_chart(current_user["id"], request.model_dump())
        return record
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist KP chart: {str(exc)}",
        )


# 4. Persistence: List Saved KP Charts
@router.get("/kp/charts", response_model=SavedKpChartListResponse, summary="List saved KP Charts")
def list_charts(
    chart_type: Optional[str] = Query(None, description="'natal' or 'horary'"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    all_users: bool = Query(False, description="Admin only: view all users' charts"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin" and all_users
    records = list_kp_charts(
        user_id=current_user["id"],
        chart_type=chart_type,
        limit=limit,
        offset=offset,
        is_admin=is_admin,
    )
    return {"charts": records, "total_count": len(records)}


# 5. Persistence: Get Single Saved KP Chart
@router.get("/kp/charts/{chart_id}", response_model=SavedKpChartItem, summary="Get saved KP Chart snapshot")
def get_chart(
    chart_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    record = get_kp_chart(current_user["id"], chart_id, is_admin=is_admin)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved KP chart not found or unauthorized.",
        )
    return record


# 6. Persistence: Delete Saved KP Chart
@router.delete("/kp/charts/{chart_id}", summary="Delete saved KP Chart")
def delete_chart(
    chart_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    success = delete_kp_chart(current_user["id"], chart_id, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved KP chart not found or unauthorized.",
        )
    return {"status": "success", "message": "Chart deleted successfully."}
