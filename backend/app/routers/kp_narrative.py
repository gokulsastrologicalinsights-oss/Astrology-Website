"""FastAPI Router for Feature 2: Automated KP Predictive Narrative Engine (English & Tamil)."""

from datetime import date, time as dt_time, datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool

from app.schemas.kp_narrative import (
    KpNarrativeRequest,
    KpNarrativeResponse,
    KpNarrativePdfRequest,
    SaveKpNarrativeRequest,
    SavedKpNarrativeItem,
    SavedKpNarrativeListResponse,
)
from app.services.auth_service import get_current_user
from app.services.horoscope_cache import get_cached_saved_horoscope
from app.services.kp_narrative_engine import (
    generate_kp_predictive_narrative_data,
    KpNarrativePdfGenerator,
    KpNarrativeRepository,
)

logger = logging.getLogger("gai.api.kp_narrative")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/kp-narrative", tags=["KP Predictive Narrative"])


def _validate_uuid(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: '{val}'.",
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """Optional authentication: returns user dict if valid token provided, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def _resolve_birth_parameters(
    request_data: Any,
    current_user: Optional[Dict[str, Any]],
) -> Tuple[date, dt_time, float, float, str, str, str]:
    """Resolves birth parameters from either a saved horoscope or ad-hoc birth_input."""
    saved_id_val = getattr(request_data, "saved_horoscope_id", None)
    if saved_id_val and str(saved_id_val).strip():
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required to access saved horoscopes.",
            )
        clean_id = _validate_uuid(saved_id_val)
        is_admin = current_user.get("role") == "admin"
        horoscope_row = get_cached_saved_horoscope(
            clean_id=clean_id,
            user_id=current_user["id"],
            is_admin=is_admin,
            include_calculation_result=True,
        )

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
        b_time: Optional[dt_time] = None
        if isinstance(b_time_raw, dt_time):
            b_time = b_time_raw
        elif isinstance(b_time_raw, str):
            b_time_str = b_time_raw.strip()
            try:
                b_time = dt_time.fromisoformat(b_time_str)
            except ValueError:
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
                b_time = dt_time(hour, minute, second)

        lat = float(horoscope_row["latitude"])
        lon = float(horoscope_row["longitude"])
        tz_str = horoscope_row.get("timezone") or "Asia/Kolkata"
        name = horoscope_row.get("person_name") or getattr(request_data, "person_name", None) or "Native"
        gender = horoscope_row.get("gender") or getattr(request_data, "gender", None) or "male"
        return b_date, b_time, lat, lon, tz_str, name, gender

    # Case 2: Ad-hoc birth input provided
    if getattr(request_data, "birth_input", None):
        bi = request_data.birth_input
        name = getattr(request_data, "person_name", None) or "Native"
        gender = getattr(request_data, "gender", None) or "male"
        return bi.birth_date, bi.birth_time, bi.latitude, bi.longitude, bi.timezone, name, gender

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Either 'saved_horoscope_id' or 'birth_input' must be provided.",
    )


@router.post("/generate", response_model=KpNarrativeResponse, summary="Generate automated KP predictive narrative report")
async def generate_kp_narrative_endpoint(
    request: KpNarrativeRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> KpNarrativeResponse:
    """Generates structured, plain-language predictive narrative in English and Tamil."""
    try:
        b_date, b_time, lat, lon, tz_str, name, gender = _resolve_birth_parameters(request, current_user)

        data = await run_in_threadpool(
            generate_kp_predictive_narrative_data,
            birth_date=b_date,
            birth_time=b_time,
            latitude=lat,
            longitude=lon,
            timezone_str=tz_str,
            person_name=name,
            gender=gender,
            target_date=request.target_date,
            ayanamsa_id=request.ayanamsa_id,
            language=request.language,
            months_ahead=request.months_ahead,
        )

        return KpNarrativeResponse(**data)
    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning(f"Validation error in KP narrative generation: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Calculation validation error: {str(val_err)}",
        )
    except Exception as exc:
        logger.exception(f"Error generating KP narrative: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating KP predictive narrative: {str(exc)}",
        )


@router.post("/pdf", summary="Generate downloadable KP predictive narrative PDF report")
async def generate_kp_narrative_pdf_endpoint(
    request: KpNarrativePdfRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates print-ready publication-grade PDF booklet in English or Tamil."""
    try:
        if request.precalculated_data:
            calc_data = request.precalculated_data
        else:
            b_date, b_time, lat, lon, tz_str, name, gender = _resolve_birth_parameters(request, current_user)
            calc_data = await run_in_threadpool(
                generate_kp_predictive_narrative_data,
                birth_date=b_date,
                birth_time=b_time,
                latitude=lat,
                longitude=lon,
                timezone_str=tz_str,
                person_name=name,
                gender=gender,
                target_date=request.target_date,
                ayanamsa_id=request.ayanamsa_id,
                language=request.language,
                months_ahead=request.months_ahead,
            )

        pdf_gen = KpNarrativePdfGenerator(calc_data, language=request.language)
        pdf_bytes = await run_in_threadpool(pdf_gen.generate)

        raw_name = calc_data.get("person_details", {}).get("name", "Native")
        safe_name = "".join(c for c in raw_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        bdate_str = calc_data.get("person_details", {}).get("birth_date", "Chart")
        lang_code = request.language.upper()
        filename = f"KP_Predictive_Narrative_{safe_name}_{bdate_str}_{lang_code}.pdf"

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
    except Exception as exc:
        logger.exception(f"Error generating KP narrative PDF: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating KP predictive narrative PDF: {str(exc)}",
        )


@router.post("/save", summary="Save a generated KP narrative report")
async def save_kp_narrative_endpoint(
    request: SaveKpNarrativeRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Persists a generated narrative report."""
    user_id = current_user["id"] if current_user else None
    saved_item = KpNarrativeRepository.save(
        user_id=user_id,
        title=request.title,
        person_name=request.person_name,
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        latitude=request.latitude,
        longitude=request.longitude,
        timezone_str=request.timezone,
        gender=request.gender,
        language=request.language,
        report_data=request.report_data,
        saved_horoscope_id=request.saved_horoscope_id,
    )
    return {"status": "success", "id": saved_item["id"], "message": "KP predictive narrative report saved successfully."}


@router.get("/saved", response_model=SavedKpNarrativeListResponse, summary="List saved KP narrative reports")
async def list_saved_kp_narratives_endpoint(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> SavedKpNarrativeListResponse:
    """Lists saved narrative reports for the authenticated user or all if admin."""
    user_id = current_user["id"] if current_user else None
    is_admin = current_user.get("role") == "admin" if current_user else False
    records = KpNarrativeRepository.list_all(user_id=user_id, is_admin=is_admin)
    return SavedKpNarrativeListResponse(
        total=len(records),
        items=[
            SavedKpNarrativeItem(
                id=r["id"],
                user_id=r.get("user_id"),
                title=r.get("title", "KP Narrative"),
                person_name=r.get("person_name", "Native"),
                saved_horoscope_id=r.get("saved_horoscope_id"),
                birth_date=r.get("birth_date", ""),
                birth_time=r.get("birth_time", ""),
                language=r.get("language", "ta"),
                created_at=r.get("created_at", ""),
                updated_at=r.get("updated_at", ""),
            )
            for r in records
        ],
    )


@router.get("/saved/{record_id}", summary="Get a saved KP narrative report by ID")
async def get_saved_kp_narrative_endpoint(
    record_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Retrieves full details of a saved narrative report."""
    user_id = current_user["id"] if current_user else None
    is_admin = current_user.get("role") == "admin" if current_user else False
    record = KpNarrativeRepository.get(record_id, user_id=user_id, is_admin=is_admin)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved narrative report not found.")
    return record


@router.delete("/saved/{record_id}", summary="Delete a saved KP narrative report by ID")
async def delete_saved_kp_narrative_endpoint(
    record_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Deletes a saved narrative report."""
    user_id = current_user["id"] if current_user else None
    is_admin = current_user.get("role") == "admin" if current_user else False
    success = KpNarrativeRepository.delete(record_id, user_id=user_id, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved narrative report not found or unauthorized.")
    return {"status": "success", "message": "Saved narrative report deleted successfully."}
