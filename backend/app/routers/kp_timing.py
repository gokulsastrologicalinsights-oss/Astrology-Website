"""KP Monthly & Period Predictive Timing Router.

Exposes endpoints for calculating guaranteed, highly favorable, and caution
monthly event predictions using Krishnamurti Paddhati (KP System) 4-pillar principles.
"""

from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.common import BirthInput
from app.schemas.kp_timing import (
    KpMonthlyPredictionRequest,
    KpMonthlyPredictionResponse,
)
from app.services.auth_service import get_current_user
from app.services.horoscope_cache import get_cached_saved_horoscope
from app.services.kp_timing_service import (
    calculate_kp_monthly_prediction,
    MONTH_NAMES_EN,
    MONTH_NAMES_TA,
)

security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/kp/timing", tags=["KP Monthly & Period Timing"])


def _validate_uuid(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns its canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid saved horoscope UUID format.",
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """Optional authentication."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


@router.get("/available-months", summary="Get candidate months for prediction")
def get_available_months():
    """Returns the current month and upcoming 6 months as selection shortcuts."""
    today = date.today()
    results = []
    
    # Generate current month and next 5 months
    cur_y = today.year
    cur_m = today.month

    for offset in range(6):
        m = (cur_m - 1 + offset) % 12 + 1
        y = cur_y + (cur_m - 1 + offset) // 12
        is_current = (offset == 0)
        is_next = (offset == 1)
        results.append({
            "year": y,
            "month": m,
            "label_en": f"{MONTH_NAMES_EN[m]} {y}",
            "label_ta": f"{MONTH_NAMES_TA[m]} {y}",
            "is_current": is_current,
            "is_next": is_next,
            "tag_ta": "நடப்பு மாதம்" if is_current else ("அடுத்த மாதம்" if is_next else ""),
        })

    return {"months": results}


@router.post("/monthly-prediction", response_model=KpMonthlyPredictionResponse, summary="Calculate KP Monthly Prediction")
async def get_kp_monthly_prediction(
    request: KpMonthlyPredictionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> KpMonthlyPredictionResponse:
    """Calculates KP 4-pillar monthly event predictions with guaranteed fructification timing."""
    birth = request.birth

    native_name = request.native_name

    # If saved_horoscope_id provided, load from cache/db
    if not birth and request.saved_horoscope_id:
        try:
            clean_id = _validate_uuid(request.saved_horoscope_id)
            user_id = str(current_user["id"]) if current_user and "id" in current_user else ""
            is_admin = bool(current_user and current_user.get("role") == "admin")
            saved = get_cached_saved_horoscope(
                clean_id=clean_id,
                user_id=user_id,
                is_admin=is_admin or (not bool(user_id)),
                include_calculation_result=False,
            )
            if not saved:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Saved horoscope {request.saved_horoscope_id} not found",
                )
            # Construct BirthInput
            b_data = saved.get("birth_data") or saved
            birth_time_raw = b_data.get("birth_time") or b_data.get("time") or "12:00:00"
            if isinstance(birth_time_raw, str) and len(birth_time_raw.split(":")) == 2:
                birth_time_raw = f"{birth_time_raw}:00"
            birth = BirthInput(
                birth_date=b_data.get("birth_date") or b_data.get("date"),
                birth_time=birth_time_raw,
                latitude=float(b_data.get("latitude", 13.0827)),
                longitude=float(b_data.get("longitude", 80.2707)),
                timezone=b_data.get("timezone", "Asia/Kolkata"),
            )
            if not native_name:
                native_name = saved.get("person_name") or saved.get("name") or b_data.get("person_name") or b_data.get("name") or "ஜாதகர்"
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to load saved horoscope: {str(e)}",
            )

    if not birth:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'birth' input or 'saved_horoscope_id' must be provided.",
        )

    try:
        response = calculate_kp_monthly_prediction(
            birth=birth,
            year=request.year,
            month=request.month,
            ayanamsa_id=request.ayanamsa_id,
            native_name=native_name or "ஜாதகர்",
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Monthly calculation error: {str(exc)}",
        )
