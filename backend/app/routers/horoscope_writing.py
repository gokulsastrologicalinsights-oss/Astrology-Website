"""FastAPI router for Traditional Tamil Horoscope Writing Module."""

import uuid
import logging
from datetime import date, time, datetime
from typing import Optional, Dict, Any, List, Tuple
from fastapi import APIRouter, HTTPException, Depends, Security, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.horoscope_writing import (
    HoroscopeWritingRequest,
    HoroscopeWritingResponse,
    HoroscopeWritingPdfRequest,
    HoroscopeWritingSaveRequest,
    HoroscopeWritingSaveResponse,
    SavedHoroscopeWritingItem,
    SavedHoroscopeWritingListResponse,
    HoroscopeWritingUpdateRequest,
)
from app.schemas.common import BirthInput
from app.services.horoscope_writing import (
    calculate_traditional_horoscope_writing_data,
    TraditionalHoroscopePdfGenerator,
)
from app.services.horoscope_writing.repository import HoroscopeWritingRepository
from app.services.auth_service import get_current_user, get_supabase_client

logger = logging.getLogger("gai.api.horoscope_writing")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/tools/horoscope-writing", tags=["Horoscope Writing"])


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
    """Optional authentication: returns user dict if valid Bearer token provided, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def _resolve_birth_parameters(
    request_data: Any,
    current_user: Optional[Dict[str, Any]],
) -> Tuple[date, time, float, float, str, str, str]:
    """Resolves birth parameters from either a saved horoscope or ad-hoc birth_input."""
    saved_id_val = getattr(request_data, "saved_horoscope_id", None)
    if saved_id_val and str(saved_id_val).strip():
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required to access saved horoscopes.",
            )
        clean_id = _validate_uuid(saved_id_val)
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable.",
            )

        is_admin = current_user.get("role") == "admin"
        horoscope_row = None
        try:
            resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
            if resp.data and len(resp.data) > 0:
                row = resp.data[0]
                if is_admin or str(row.get("user_id")) == str(current_user["id"]):
                    horoscope_row = row
        except Exception as err:
            logger.warning("Database error fetching saved horoscope %s: %s", clean_id, err)

        if not horoscope_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved horoscope not found or unauthorized.",
            )

        b_date = horoscope_row.get("birth_date")
        if not b_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Saved horoscope is missing 'birth_date'.",
            )
        if isinstance(b_date, str):
            try:
                b_date = date.fromisoformat(b_date.strip())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid 'birth_date' format in saved horoscope: {b_date}",
                )

        b_time_raw = horoscope_row.get("birth_time")
        if not b_time_raw:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Saved horoscope is missing 'birth_time'.",
            )
        b_time: Optional[time] = None
        if isinstance(b_time_raw, time):
            b_time = b_time_raw
        elif isinstance(b_time_raw, str):
            b_time_str = b_time_raw.strip()
            try:
                b_time = time.fromisoformat(b_time_str)
            except ValueError:
                try:
                    import re
                    is_pm = "pm" in b_time_str.lower()
                    is_am = "am" in b_time_str.lower()
                    clean_time = re.sub(r"[^\d:]", "", b_time_str)
                    parts = clean_time.split(":")
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    second = int(float(parts[2])) if len(parts) > 2 else 0
                    if is_pm and hour < 12:
                        hour += 12
                    elif is_am and hour == 12:
                        hour = 0
                    b_time = time(hour, minute, second)
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid 'birth_time' format in saved horoscope: {b_time_raw}",
                    )

        try:
            lat = float(horoscope_row["latitude"])
            lon = float(horoscope_row["longitude"])
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                raise ValueError("Coordinates out of valid range [-90..90, -180..180]")
        except (ValueError, TypeError, KeyError) as coord_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid coordinates in saved horoscope: {coord_err}",
            )

        tz_str = horoscope_row.get("timezone") or "Asia/Kolkata"
        name = horoscope_row.get("person_name") or request_data.person_name or "Native"
        gender = horoscope_row.get("gender") or request_data.gender or "male"
        return b_date, b_time, lat, lon, tz_str, name, gender

    # Case 2: Ad-hoc birth input provided
    if getattr(request_data, "birth_input", None):
        bi = request_data.birth_input
        name = request_data.person_name or "Native"
        gender = request_data.gender or "male"
        return bi.birth_date, bi.birth_time, bi.latitude, bi.longitude, bi.timezone, name, gender

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Either 'saved_horoscope_id' or 'birth_input' must be provided.",
    )


@router.post("/calculate", response_model=HoroscopeWritingResponse, summary="Calculate traditional Tamil horoscope writing data")
async def calculate_horoscope_writing_endpoint(
    request: HoroscopeWritingRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> HoroscopeWritingResponse:
    """Computes all 6 pages of traditional Tamil horoscope writing dynamically."""
    try:
        b_date, b_time, lat, lon, tz_str, name, gender = _resolve_birth_parameters(request, current_user)

        data = calculate_traditional_horoscope_writing_data(
            birth_date=b_date,
            birth_time=b_time,
            latitude=lat,
            longitude=lon,
            timezone_str=tz_str,
            ayanamsa_id=request.ayanamsa_id,
            house_system_id=request.house_system_id,
            panchanga_system=request.panchanga_system,
            person_name=name,
            gender=gender,
            entrance_direction_basis=request.entrance_direction_basis,
            overrides=request.overrides,
        )

        return HoroscopeWritingResponse(**data)
    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning("Validation error in traditional horoscope calculation: %s", val_err)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Calculation validation error: {str(val_err)}",
        )
    except Exception as exc:
        logger.exception("Error calculating traditional horoscope writing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating traditional horoscope writing: {str(exc)}",
        )


@router.post("/pdf", summary="Generate six-page traditional Tamil horoscope booklet PDF")
async def generate_horoscope_writing_pdf_endpoint(
    request: HoroscopeWritingPdfRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates the six-page traditional Tamil booklet PDF."""
    try:
        if request.precalculated_data:
            calc_data = request.precalculated_data
        else:
            b_date, b_time, lat, lon, tz_str, name, gender = _resolve_birth_parameters(request, current_user)
            calc_data = calculate_traditional_horoscope_writing_data(
                birth_date=b_date,
                birth_time=b_time,
                latitude=lat,
                longitude=lon,
                timezone_str=tz_str,
                ayanamsa_id=request.ayanamsa_id,
                house_system_id=request.house_system_id,
                panchanga_system=request.panchanga_system,
                person_name=name,
                gender=gender,
                entrance_direction_basis=request.entrance_direction_basis,
                overrides=request.overrides,
            )

        pdf_generator = TraditionalHoroscopePdfGenerator(calc_data)
        pdf_bytes = pdf_generator.generate()

        safe_name = "".join(c for c in (calc_data.get("person_details", {}).get("name", "Native")) if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        bdate_str = calc_data.get("person_details", {}).get("birth_date", "Chart")
        filename = f"Tamil_Horoscope_Writing_{safe_name}_{bdate_str}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning("Validation error generating traditional horoscope writing PDF: %s", val_err)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"PDF generation validation error: {str(val_err)}",
        )
    except Exception as exc:
        logger.exception("Error generating traditional horoscope writing PDF: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating traditional horoscope writing PDF: {str(exc)}",
        )


@router.post("/save", response_model=HoroscopeWritingSaveResponse, summary="Persist generated horoscope writing document")
async def save_horoscope_writing_endpoint(
    request: HoroscopeWritingSaveRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> HoroscopeWritingSaveResponse:
    """Saves the generated horoscope writing document with guaranteed persistent storage."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to save horoscope writing document.",
        )

    clean_horoscope_id = None
    if request.horoscope_id and str(request.horoscope_id).strip():
        try:
            clean_horoscope_id = _validate_uuid(request.horoscope_id)
        except HTTPException:
            clean_horoscope_id = None

    payload = {
        "horoscope_id": clean_horoscope_id,
        "person_name": request.person_name,
        "birth_date": request.birth_date,
        "birth_time": request.birth_time,
        "birth_place": request.birth_place,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "timezone": request.timezone,
        "panchanga_system": request.panchanga_system,
        "calculated_data": request.calculated_data,
        "overrides": request.overrides or {},
    }

    result = HoroscopeWritingRepository.save(
        user_id=current_user["id"],
        payload=payload,
    )
    return HoroscopeWritingSaveResponse(**result)


@router.get("/saved", response_model=SavedHoroscopeWritingListResponse, summary="List saved horoscope writing documents")
async def list_saved_horoscope_writings_endpoint(
    limit: int = 50,
    offset: int = 0,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> SavedHoroscopeWritingListResponse:
    """Lists saved horoscope writing documents for the authenticated user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view saved horoscope writing documents.",
        )

    is_admin = current_user.get("role") == "admin"
    records = HoroscopeWritingRepository.list_records(
        user_id=current_user["id"],
        is_admin=is_admin,
        limit=limit,
        offset=offset,
    )
    return SavedHoroscopeWritingListResponse(
        success=True,
        count=len(records),
        items=[SavedHoroscopeWritingItem(**r) for r in records],
    )


@router.get("/saved/{id}", response_model=SavedHoroscopeWritingItem, summary="Get saved horoscope writing document by ID")
async def get_saved_horoscope_writing_endpoint(
    id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> SavedHoroscopeWritingItem:
    """Retrieves a single saved horoscope writing document by ID, enforcing user ownership."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to retrieve saved horoscope writing document.",
        )

    is_admin = current_user.get("role") == "admin"
    record = HoroscopeWritingRepository.get_by_id(
        record_id=id,
        user_id=current_user["id"],
        is_admin=is_admin,
    )
    return SavedHoroscopeWritingItem(**record)


@router.delete("/saved/{id}", summary="Delete saved horoscope writing document by ID")
async def delete_saved_horoscope_writing_endpoint(
    id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Deletes a saved horoscope writing document by ID, enforcing user ownership."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to delete saved horoscope writing document.",
        )

    is_admin = current_user.get("role") == "admin"
    deleted = HoroscopeWritingRepository.delete(
        record_id=id,
        user_id=current_user["id"],
        is_admin=is_admin,
    )
    return {
        "success": deleted,
        "message": "Horoscope writing document deleted successfully." if deleted else "Document not found.",
    }


@router.put("/saved/{id}", response_model=SavedHoroscopeWritingItem, summary="Update saved horoscope writing document by ID")
async def update_saved_horoscope_writing_endpoint(
    id: str,
    request: HoroscopeWritingUpdateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> SavedHoroscopeWritingItem:
    """Updates a saved horoscope writing document by ID, enforcing user ownership."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to update saved horoscope writing document.",
        )

    is_admin = current_user.get("role") == "admin"
    payload = request.model_dump(exclude_unset=True)
    updated = HoroscopeWritingRepository.update(
        record_id=id,
        user_id=current_user["id"],
        payload=payload,
        is_admin=is_admin,
    )
    return SavedHoroscopeWritingItem(**updated)
