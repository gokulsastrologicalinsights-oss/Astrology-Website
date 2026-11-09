"""PDF Report generation routers for Gokul's Astrological Insights.

Supports:
1. 9-page bilingual Vedic horoscope reports (/api/v1/reports/horoscope/pdf)
2. Dedicated 6-page bilingual KP astrology reports (/api/v1/reports/kp/pdf)
"""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Security, Response, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.concurrency import run_in_threadpool

from app.schemas.pdf_report import (
    SinglePageHoroscopePdfRequest,
    HoroscopePdfReportRequest,
    KpPdfReportRequest,
    ShodashvargaPdfReportRequest,
    MuhurtaCertificatePdfRequest,
    PanchaPakshiPdfReportRequest,
    GemstoneRudrakshaPlaybookPdfRequest,
    MarriageCompatibilityPdfReportRequest,
)
from app.schemas.common import BirthInput
from app.services.pdf_report_engine import (
    generate_single_page_horoscope_pdf_bytes,
    build_report_data,
    generate_horoscope_pdf_bytes,
    build_kp_report_data,
    generate_kp_pdf_bytes,
    generate_shodashvarga_pdf_bytes,
    generate_muhurta_certificate_pdf_bytes,
    generate_pancha_pakshi_pdf_bytes,
    generate_gemstone_rudraksha_playbook_pdf_bytes,
    generate_marriage_compatibility_pdf_bytes,
)
from app.services.auth_service import get_current_user, get_supabase_client
from app.services.horoscope_cache import get_cached_saved_horoscope
from app.services.kp_engine.kp_chart_repository import get_kp_chart
from app.services.pdf_storage import (
    generate_pdf_cache_key,
    get_cached_pdf,
    store_cached_pdf,
    upload_pdf_to_supabase_storage,
    get_supabase_storage_signed_url,
)

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
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates an approximately 9-page branded English/Tamil PDF horoscope report.
    Offloaded to worker threadpool and cached to prevent event loop blocking under concurrency.
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
            is_admin = current_user.get("role") == "admin"
            horoscope_row = get_cached_saved_horoscope(
                clean_id=clean_id,
                user_id=current_user["id"],
                is_admin=is_admin,
                include_calculation_result=False,
            )

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
            disp_num = horoscope_row.get("display_number")
            if disp_num is not None:
                formatted_num = f"{disp_num:02d}" if isinstance(disp_num, int) and disp_num < 10 else str(disp_num)
                saved_report_id = f"#{formatted_num}"
            else:
                saved_report_id = clean_id[:8].upper()

            native_name = request.native_name if request.native_name != "Native" else (horoscope_row.get("person_name") or horoscope_row.get("name", "Native"))

            report_data = build_report_data(
                birth_input=birth_input,
                native_name=native_name,
                gender=request.gender or horoscope_row.get("gender", "male"),
                ayanamsa_id=request.ayanamsa or horoscope_row.get("ayanamsa_id", 0),
                house_system_id=request.house_system or horoscope_row.get("house_system_id", 0),
                language=request.language,
                report_id=saved_report_id,
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

        # High-concurrency caching & threadpool execution
        cache_id = request.saved_horoscope_id or f"{report_data.birth_date}_{report_data.birth_time}_{report_data.latitude}_{report_data.longitude}"
        cache_key = generate_pdf_cache_key(
            "horoscope_9p",
            cache_id,
            report_data.language,
            f"{report_data.ayanamsa_name}:{report_data.house_system_name}:{report_data.native_name}",
        )
        filename = f"Horoscope_Report_{report_data.report_id}.pdf"

        cached_entry = get_cached_pdf(cache_key)
        if cached_entry:
            pdf_bytes, filename = cached_entry
        else:
            pdf_bytes = await run_in_threadpool(generate_horoscope_pdf_bytes, report_data)
            store_cached_pdf(cache_key, pdf_bytes, filename)
            if background_tasks:
                background_tasks.add_task(
                    upload_pdf_to_supabase_storage,
                    file_path=f"horoscope/{report_data.language}/{filename}",
                    pdf_bytes=pdf_bytes,
                )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
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
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Download PDF horoscope report for a saved horoscope ID. Requires authentication and ownership."""
    req = HoroscopePdfReportRequest(
        saved_horoscope_id=horoscope_id,
        language=language,
    )
    return await generate_pdf_report_endpoint(req, background_tasks=background_tasks, current_user=current_user)


@router.post("/single-page-pdf", summary="Generate authentic 1-page traditional Tamil horoscope PDF")
async def generate_single_page_pdf_endpoint(
    request: SinglePageHoroscopePdfRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates a pixel-perfect 1-page traditional Tamil horoscope PDF conforming to Gokul's Astrological Insights layout."""
    try:
        birth_input: Optional[BirthInput] = None
        native_name = request.native_name or "Native"
        gender = request.gender or "male"
        clean_id = "001"

        if request.saved_horoscope_id:
            clean_id = _validate_uuid(request.saved_horoscope_id)
            is_admin = current_user.get("role") == "admin" if current_user else False
            user_id = current_user.get("id") if current_user else ""
            row = get_cached_saved_horoscope(
                clean_id=clean_id,
                user_id=user_id,
                is_admin=is_admin,
                include_calculation_result=False,
            )
            if not row:
                raise HTTPException(status_code=404, detail="Saved horoscope not found or unauthorized.")

            from datetime import date as d_cls, time as t_cls
            b_date = row["birth_date"]
            if isinstance(b_date, str):
                b_date = d_cls.fromisoformat(b_date)
            b_time = row["birth_time"]
            if isinstance(b_time, str):
                parts = b_time.split(":")
                b_time = t_cls(int(parts[0]), int(parts[1]), int(float(parts[2])) if len(parts) > 2 else 0)

            birth_input = BirthInput(
                birth_date=b_date,
                birth_time=b_time,
                timezone=row.get("timezone", "Asia/Kolkata"),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
            )
            if request.native_name in ("Native", "", None):
                native_name = row.get("person_name") or row.get("name") or "Native"
            else:
                native_name = request.native_name

            gender = row.get("gender") or gender
            birth_place = request.birth_place or row.get("birthplace") or "Chennai, Tamil Nadu"

            # Resolve saved horoscope display number
            disp_num = row.get("display_number")
            if disp_num is not None:
                formatted_num = f"{disp_num:02d}" if isinstance(disp_num, int) and disp_num < 10 else str(disp_num)
                saved_native_id = f"#{formatted_num}"
            else:
                saved_native_id = f"#{clean_id[:4]}"

        elif request.birth_input:
            birth_input = request.birth_input
            saved_native_id = "#001"
            birth_place = request.birth_place or "Chennai, Tamil Nadu"
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide either birth_input or saved_horoscope_id.",
            )

        # Determine native_id: prioritize real display_number / saved_native_id over raw uuid slices or placeholders
        if request.saved_horoscope_id:
            if request.native_id and request.native_id not in ("#001", "") and not request.native_id.startswith(f"#{clean_id[:3]}"):
                final_native_id = request.native_id
            else:
                final_native_id = saved_native_id
        else:
            final_native_id = request.native_id or saved_native_id

        pdf_bytes = await run_in_threadpool(
            generate_single_page_horoscope_pdf_bytes,
            birth_input=birth_input,
            native_name=native_name,
            father_name=request.father_name,
            mother_name=request.mother_name,
            gender=gender,
            birth_place=birth_place,
            native_id=final_native_id,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            language=request.language,
            font_family=request.font_family,
        )

        safe_name = native_name.replace(" ", "_").strip() or "Horoscope"
        filename = f"Single_Page_Horoscope_{safe_name}.pdf"
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
    except Exception as exc:
        logger.error("Error generating single page PDF horoscope report: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Single-page PDF generation failed: {str(exc)}",
        )


@router.get("/single-page-pdf/{horoscope_id}", summary="Download 1-page traditional Tamil horoscope PDF by saved ID")
async def download_single_page_pdf_by_id_endpoint(
    horoscope_id: str,
    language: str = "ta",
    font_family: str = "auto",
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Download 1-page PDF report for a saved horoscope ID."""
    req = SinglePageHoroscopePdfRequest(
        saved_horoscope_id=horoscope_id,
        language=language,
        font_family=font_family,
    )
    return await generate_single_page_pdf_endpoint(req, current_user=current_user)



# -----------------------------------------------------------------------------
# 2. Dedicated KP Astrology PDF Endpoints
# -----------------------------------------------------------------------------
@kp_router.post("/pdf", summary="Generate dedicated 6-page bilingual KP Astrology PDF report")
async def generate_kp_pdf_endpoint(
    request: KpPdfReportRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates a dedicated 6-page branded English/Tamil KP PDF report.
    Offloaded to worker threadpool and cached to prevent event loop blocking under concurrency.

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

        # Cache check & threadpool offload
        cache_id = request.saved_chart_id or f"{report_data.birth_date}_{report_data.birth_time}_{report_data.latitude}_{report_data.longitude}"
        cache_key = generate_pdf_cache_key(
            "kp_6p",
            cache_id,
            report_data.language,
            f"{report_data.chart_type}:{report_data.horary_number}:{report_data.native_name}",
        )
        chart_label = "Horary" if report_data.chart_type == "horary" else "Natal"
        filename = f"KP_{chart_label}_Report_{report_data.report_id}.pdf"

        cached_entry = get_cached_pdf(cache_key)
        if cached_entry:
            pdf_bytes, filename = cached_entry
        else:
            pdf_bytes = await run_in_threadpool(generate_kp_pdf_bytes, report_data)
            store_cached_pdf(cache_key, pdf_bytes, filename)
            if background_tasks:
                background_tasks.add_task(
                    upload_pdf_to_supabase_storage,
                    file_path=f"kp/{report_data.language}/{filename}",
                    pdf_bytes=pdf_bytes,
                )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
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
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Download KP PDF report for a saved chart ID. Requires authentication and ownership."""
    req = KpPdfReportRequest(
        saved_chart_id=chart_id,
        language=language,
    )
    return await generate_kp_pdf_endpoint(req, background_tasks=background_tasks, current_user=current_user)


# -----------------------------------------------------------------------------
# 3. Specialized Client-Facing PDF Reports Endpoints
# -----------------------------------------------------------------------------
studio_router = APIRouter(prefix="/api/v1/reports", tags=["Specialized PDF Reports"])


@studio_router.post("/shodashvarga/pdf", summary="Generate a 7-page Shodashvarga 16-Divisional Chart Book PDF")
async def generate_shodashvarga_pdf_endpoint(
    request: ShodashvargaPdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Compiles a complete 16-divisional Shodashvarga Chart Book (D1 through D60) with Ashtakavarga and Dasha calendar."""
    try:
        birth_input: Optional[BirthInput] = None
        if request.saved_horoscope_id:
            clean_id = _validate_uuid(request.saved_horoscope_id)
            is_admin = current_user.get("role") == "admin" if current_user else False
            user_id = current_user.get("id") if current_user else ""
            row = get_cached_saved_horoscope(
                clean_id=clean_id,
                user_id=user_id,
                is_admin=is_admin,
                include_calculation_result=False,
            )
            if not row:
                raise HTTPException(status_code=404, detail="Saved horoscope not found.")
            from datetime import date as d_cls, time as t_cls
            b_date = d_cls.fromisoformat(row["birth_date"]) if isinstance(row["birth_date"], str) else row["birth_date"]
            parts = row["birth_time"].split(":")
            b_time = t_cls(int(parts[0]), int(parts[1]))
            birth_input = BirthInput(
                birth_date=b_date,
                birth_time=b_time,
                timezone=row.get("timezone", "Asia/Kolkata"),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
            )
        elif request.birth_input:
            birth_input = request.birth_input
        else:
            raise HTTPException(status_code=422, detail="Either birth_input or saved_horoscope_id required.")

        pdf_bytes = await run_in_threadpool(generate_shodashvarga_pdf_bytes, request, birth_input)
        filename = f"Shodashvarga_Book_{request.native_name.replace(' ', '_')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error generating Shodashvarga PDF: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Shodashvarga PDF generation failed: {str(exc)}")


@studio_router.post("/muhurta-certificate/pdf", summary="Generate a ceremonial Auspicious Muhurta Selection Certificate PDF")
async def generate_muhurta_certificate_pdf_endpoint(
    request: MuhurtaCertificatePdfRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Generates an auspicious ceremonial gold-bordered Muhurta Selection Certificate."""
    try:
        pdf_bytes = await run_in_threadpool(generate_muhurta_certificate_pdf_bytes, request)
        occ_name = request.occasion.replace(" ", "_")
        filename = f"Muhurta_Certificate_{occ_name}_{request.event_date}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as exc:
        logger.error("Error generating Muhurta certificate PDF: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Muhurta certificate PDF generation failed: {str(exc)}")


@studio_router.post("/pancha-pakshi/pdf", summary="Generate an Agastya Pancha Pakshi 24-Hour Bio-Rhythm Chart PDF")
async def generate_pancha_pakshi_pdf_endpoint(
    request: PanchaPakshiPdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Compiles an Agastya Pancha Pakshi 24-Hour Bio-Rhythm dossier detailing all 50 Antara windows and Golden/Padupakshi hours."""
    try:
        pdf_bytes = await run_in_threadpool(generate_pancha_pakshi_pdf_bytes, request)
        filename = f"Pancha_Pakshi_24Hr_{request.nakshatra}_{request.target_date}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as exc:
        logger.error("Error generating Pancha Pakshi PDF: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pancha Pakshi PDF generation failed: {str(exc)}")


@studio_router.post("/gemstone-rudraksha/pdf", summary="Generate Remedial Gemstone & Rudraksha Sanctification Playbook PDF")
async def generate_gemstone_rudraksha_pdf_endpoint(
    request: GemstoneRudrakshaPlaybookPdfRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Compiles a personalized Gemstone & Rudraksha Sanctification Playbook with weight formulas and mantras."""
    try:
        pdf_bytes = await run_in_threadpool(generate_gemstone_rudraksha_playbook_pdf_bytes, request)
        filename = f"Gemstone_Rudraksha_Playbook_{request.ascendant_sign}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as exc:
        logger.error("Error generating Gemstone & Rudraksha Playbook PDF: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gemstone & Rudraksha PDF generation failed: {str(exc)}")


@studio_router.post("/marriage-compatibility/pdf", summary="Generate Marriage Compatibility & 36 Ashta Kuta PDF Report")
async def generate_marriage_compatibility_pdf_endpoint(
    request: MarriageCompatibilityPdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> Response:
    """Compiles a comprehensive bilingual Kundli Matching & 36 Ashta Kuta Compatibility Report PDF."""
    try:
        report_data = request.report_data
        if not report_data and request.saved_report_id:
            clean_id = _validate_uuid(request.saved_report_id)
            supabase = get_supabase_client()
            if not supabase:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database service unavailable. Database configuration missing.",
                )
            resp = supabase.table("saved_marriage_reports").select("id, report_data").eq("id", clean_id).execute()
            if resp.data and len(resp.data) > 0:
                row = resp.data[0]
                report_data = row.get("report_data")
            else:
                raise HTTPException(status_code=404, detail="Saved marriage compatibility report not found.")

        if isinstance(report_data, str):
            try:
                report_data = json.loads(report_data)
            except Exception as parse_err:
                logger.error("Failed to parse report_data JSON string: %s", parse_err)
                raise HTTPException(status_code=422, detail="Invalid JSON in report_data.")
        elif hasattr(report_data, "model_dump"):
            report_data = report_data.model_dump(mode="json")
        elif hasattr(report_data, "dict"):
            report_data = report_data.dict()

        if not report_data or not isinstance(report_data, dict):
            raise HTTPException(status_code=422, detail="Either valid report_data dictionary or saved_report_id required.")

        groom_p = report_data.get("groom_profile")
        groom_p = groom_p if isinstance(groom_p, dict) else {}
        bride_p = report_data.get("bride_profile")
        bride_p = bride_p if isinstance(bride_p, dict) else {}
        groom_name = (groom_p.get("name") or "Groom").replace(" ", "_")
        bride_name = (bride_p.get("name") or "Bride").replace(" ", "_")
        lang = request.language or "en"
        filename = f"Marriage_Compatibility_{groom_name}_{bride_name}_{lang}.pdf"

        pdf_bytes = await run_in_threadpool(
            generate_marriage_compatibility_pdf_bytes, report_data, language=lang
        )
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
    except Exception as exc:
        logger.error("Error generating Marriage Compatibility PDF: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Marriage Compatibility PDF generation failed: {str(exc)}")


