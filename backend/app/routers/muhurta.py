"""Muhurta and Panchanga API Router.

Exposes endpoints for:
- Occasion catalog retrieval and administrative management
- Location-specific astronomical daily Panchangam calculation
- Multi-day Muhurta candidate finding and rule-based ranking
- Supabase persistence of selected Muhurtas with RLS enforcement
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.muhurta import (
    PanchangRequest,
    FindMuhurtaRequest,
    FindMuhurtaResponse,
    SaveMuhurtaRequest,
    UpdateSavedMuhurtaRequest,
    SavedMuhurtaItem,
    SavedMuhurtaListResponse,
    CustomOccasionRequest,
)
from app.services.auth_service import get_current_user
from app.services.muhurta_engine.astronomy import calculate_daily_panchangam
from app.services.muhurta_engine.finder import find_candidate_muhurtas
from app.services.muhurta_repository import (
    list_occasions,
    create_custom_occasion,
    update_occasion,
    save_muhurta_selection,
    list_saved_muhurtas,
    get_saved_muhurta,
    update_saved_muhurta,
    delete_saved_muhurta,
)

router = APIRouter(prefix="/api/v1/muhurta", tags=["Muhurta"])


# 1. Occasions Catalog
@router.get("/occasions", summary="List all supported Muhurta occasions")
def get_occasions(include_disabled: bool = Query(False)):
    return {"occasions": list_occasions(include_disabled=include_disabled)}


@router.post("/occasions", summary="Admin: Create custom occasion")
def add_custom_occasion(
    request: CustomOccasionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to add custom occasions.",
        )
    res = create_custom_occasion(current_user["id"], request.model_dump())
    return {"status": "success", "occasion": res}


@router.put("/occasions/{code}", summary="Admin: Update occasion rules or configuration")
def edit_occasion(
    code: str,
    updates: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to modify occasion rules.",
        )
    res = update_occasion(code, updates)
    if not res:
        raise HTTPException(status_code=404, detail="Occasion not found.")
    return {"status": "success", "occasion": res}


# 2. Daily Panchangam
@router.post("/panchang", summary="Calculate comprehensive daily Panchangam")
def compute_daily_panchang(request: PanchangRequest):
    try:
        res = calculate_daily_panchangam(
            event_date=request.date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone,
            ayanamsa_id=request.ayanamsa_id,
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Panchangam: {str(e)}",
        )


# 3. Candidate Finding and Ranking
@router.post("/find", response_model=FindMuhurtaResponse, summary="Find and rank auspicious Muhurta intervals")
def search_muhurtas(request: FindMuhurtaRequest):
    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date.",
        )

    # Max search window: 60 days
    if (request.end_date - request.start_date).days > 60:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Date search span cannot exceed 60 days per query.",
        )

    try:
        res = find_candidate_muhurtas(
            occasion_code=request.occasion_code,
            start_date=request.start_date,
            end_date=request.end_date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone,
            preferred_time_range=request.preferred_time_range,
            ayanamsa_id=request.ayanamsa_id,
            custom_rules=request.custom_rules,
            birth_details=request.birth_details,
            limit=request.limit,
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding candidate Muhurtas: {str(e)}",
        )


# 4. Persistence / Saved Muhurtas
@router.get("/saved", summary="List saved Muhurtas for authenticated user")
def list_user_saved_muhurtas(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    all_users: bool = Query(False),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    if all_users and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to inspect all users' records.",
        )

    records = list_saved_muhurtas(
        user_id=current_user["id"],
        is_admin=is_admin and all_users,
        limit=limit,
        offset=offset,
        search=search,
    )
    return {"count": len(records), "items": records}


@router.post("/saved", summary="Save a selected Muhurta candidate to Supabase")
def save_muhurta(
    request: SaveMuhurtaRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        res = save_muhurta_selection(current_user["id"], request.model_dump())
        return {"status": "success", "record": res}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist Muhurta selection: {str(e)}",
        )


@router.get("/saved/{record_id}", summary="Get saved Muhurta report details")
def get_saved_muhurta_by_id(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    record = get_saved_muhurta(current_user["id"], record_id, is_admin=is_admin)
    if not record:
        raise HTTPException(status_code=404, detail="Saved Muhurta record not found.")
    return record


@router.put("/saved/{record_id}", summary="Update notes or client name on saved Muhurta")
def update_saved_muhurta_by_id(
    record_id: str,
    request: UpdateSavedMuhurtaRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    record = update_saved_muhurta(
        current_user["id"],
        record_id,
        request.model_dump(exclude_unset=True),
        is_admin=is_admin,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Saved Muhurta record not found.")
    return {"status": "success", "record": record}


@router.delete("/saved/{record_id}", summary="Delete saved Muhurta record")
def delete_saved_muhurta_by_id(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    success = delete_saved_muhurta(current_user["id"], record_id, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=404, detail="Saved Muhurta record not found or already deleted.")
    return {"status": "success", "message": "Record successfully deleted."}
