"""PDF Report generation routers for Gokul's Astrological Insights.

Supports:
1. 9-page bilingual Vedic horoscope reports (/api/v1/reports/horoscope/pdf)
2. Dedicated 6-page bilingual KP astrology reports (/api/v1/reports/kp/pdf)
"""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Security, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.pdf_report import HoroscopePdfReportRequest, KpPdfReportRequest
from app.schemas.common import BirthInput
from app.services.pdf_report_engine import (
    build_report_data,
    generate_horoscope_pdf_bytes,
    build_kp_report_data,
    generate_kp_pdf_bytes,
)
from app.services.auth_service import get_current_user, get_supabase_client
from app.services.kp_engine.kp_chart_repository import get_kp_chart

logger = logging.getLogger("gai.api.pdf_reports")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/reports/horoscope", tags=["Reports"])
kp_router = APIRouter(prefix="/api/v1/reports/kp", tags=["KP Reports"])


def _validate_uuid(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns its canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format.",
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


# -----------------------------------------------------------------------------
# 1. Vedic Horoscope PDF Endpoints
# -----------------------------------------------------------------------------
@router.post("/pdf", summary="Generate a 9-page bilingual PDF horoscope report")
async def generate_pdf_report_endpoint(
    request: HoroscopePdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates an approximately 9-page branded English/Tamil PDF horoscope report."""
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


# -----------------------------------------------------------------------------
# 2. Dedicated KP Astrology PDF Endpoints
# -----------------------------------------------------------------------------
@kp_router.post("/pdf", summary="Generate dedicated 6-page bilingual KP Astrology PDF report")
async def generate_kp_pdf_endpoint(
    request: KpPdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates a dedicated 6-page branded English/Tamil KP PDF report.

    Supports:
    - Ad-hoc natal KP chart via request.birth_input.
    - Ad-hoc horary prashna (1-249) via request.horary_input.
    - Saved KP chart via request.saved_chart_id (requires authentication and ownership).
    """
    try:
        # Case A: Saved KP Chart
        if request.saved_chart_id:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token required to access saved KP charts.",
                )
            clean_id = _validate_uuid(request.saved_chart_id)
            is_admin = current_user.get("role") == "admin"
            saved_chart = get_kp_chart(user_id=current_user["id"], record_id=clean_id, is_admin=is_admin)

            if not saved_chart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved KP chart not found or unauthorized.",
                )

            report_data = build_kp_report_data(
                saved_chart_dict=saved_chart,
                native_name=request.native_name if request.native_name != "Native" else saved_chart.get("title", "Querent"),
                gender=request.gender or "male",
                language=request.language,
                report_id=clean_id[:8].upper(),
                is_verified=True,
            )

        # Case B: Ad-hoc Horary Query (1-249)
        elif request.horary_input or request.chart_type == "horary":
            if not request.horary_input:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="horary_input details required for horary KP PDF report.",
                )
            report_data = build_kp_report_data(
                horary_input=request.horary_input,
                native_name=request.native_name,
                gender=request.gender,
                language=request.language,
                ayanamsa_id=request.ayanamsa,
                house_system_id=request.house_system,
                is_verified=True,
            )

        # Case C: Ad-hoc Natal KP Chart
        elif request.birth_input:
            report_data = build_kp_report_data(
                birth_input=request.birth_input,
                native_name=request.native_name,
                gender=request.gender,
                language=request.language,
                ayanamsa_id=request.ayanamsa,
                house_system_id=request.house_system,
                is_verified=True,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide birth_input, horary_input, or saved_chart_id.",
            )

        pdf_bytes = generate_kp_pdf_bytes(report_data)

        chart_label = "Horary" if report_data.chart_type == "horary" else "Natal"
        filename = f"KP_{chart_label}_Report_{report_data.report_id}.pdf"
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
        logger.error("Error generating KP PDF report: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP PDF report generation failed: {str(exc)}",
        )


@kp_router.get("/pdf/{chart_id}", summary="Download a 6-page KP PDF report by saved ID")
async def download_kp_pdf_by_id_endpoint(
    chart_id: str,
    language: str = "en",
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Download KP PDF report for a saved chart ID. Requires authentication and ownership."""
    req = KpPdfReportRequest(
        saved_chart_id=chart_id,
        language=language,
    )
    return await generate_kp_pdf_endpoint(req, current_user=current_user)
