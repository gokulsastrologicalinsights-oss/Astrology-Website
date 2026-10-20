"""PDF Horoscope Report generation router for Gokul's Astrological Insights."""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Security, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.pdf_report import HoroscopePdfReportRequest
from app.schemas.common import BirthInput
from app.services.pdf_report_engine import build_report_data, generate_horoscope_pdf_bytes
from app.services.auth_service import get_current_user, get_supabase_client

logger = logging.getLogger("gai.api.pdf_reports")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/reports/horoscope", tags=["Reports"])


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


@router.post("/pdf", summary="Generate a 9-page bilingual PDF horoscope report")
async def generate_pdf_report_endpoint(
    request: HoroscopePdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates an approximately 9-page branded English/Tamil PDF horoscope report.

    Supports:
    - Ad-hoc birth particulars via request.birth_input.
    - Saved horoscopes via request.saved_horoscope_id (requires authentication and ownership).
    """
    try:
        # Case A: Saved horoscope requested
        if request.saved_horoscope_id:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token required to access saved horoscopes.",
                )
            clean_id = _validate_uuid(request.saved_horoscope_id)
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
                logger.warning("Database error fetching saved horoscope %s: %s", clean_id, err)

            if not horoscope_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved horoscope not found or unauthorized.",
                )

            from datetime import date, time
            b_date = horoscope_row["birth_date"]
            if isinstance(b_date, str):
                b_date = date.fromisoformat(b_date)
            b_time = horoscope_row["birth_time"]
            if isinstance(b_time, str):
                parts = b_time.split(":")
                b_time = time(int(parts[0]), int(parts[1]), int(float(parts[2])) if len(parts) > 2 else 0)

            birth_input = BirthInput(
                birth_date=b_date,
                birth_time=b_time,
                timezone=horoscope_row.get("timezone", "Asia/Kolkata"),
                latitude=float(horoscope_row["latitude"]),
                longitude=float(horoscope_row["longitude"]),
            )
            native_name = request.native_name if request.native_name != "Native" else horoscope_row.get("name", "Native")

            report_data = build_report_data(
                birth_input=birth_input,
                native_name=native_name,
                gender=request.gender or horoscope_row.get("gender", "male"),
                ayanamsa_id=request.ayanamsa or horoscope_row.get("ayanamsa_id", 0),
                house_system_id=request.house_system or horoscope_row.get("house_system_id", 0),
                language=request.language,
                report_id=clean_id[:8].upper(),
                is_verified=True,
            )

        # Case B: Ad-hoc birth input
        elif request.birth_input:
            report_data = build_report_data(
                birth_input=request.birth_input,
                native_name=request.native_name,
                gender=request.gender,
                ayanamsa_id=request.ayanamsa,
                house_system_id=request.house_system,
                language=request.language,
                is_verified=True,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide either birth_input or saved_horoscope_id.",
            )

        pdf_bytes = generate_horoscope_pdf_bytes(report_data)

        filename = f"Horoscope_Report_{report_data.report_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
            },
        )

    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error("Error generating PDF horoscope report: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF report generation failed: {str(exc)}",
        )


@router.get("/pdf/{horoscope_id}", summary="Download a 9-page PDF horoscope report by saved ID")
async def download_pdf_by_id_endpoint(
    horoscope_id: str,
    language: str = "en",
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Download PDF horoscope report for a saved horoscope ID. Requires authentication and ownership."""
    req = HoroscopePdfReportRequest(
        saved_horoscope_id=horoscope_id,
        language=language,
    )
    return await generate_pdf_report_endpoint(req, current_user=current_user)
