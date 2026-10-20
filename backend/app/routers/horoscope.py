"""Horoscope calculation router."""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from datetime import datetime, timezone
import zoneinfo

from app.schemas.horoscope import (
    HoroscopeRequest,
    HoroscopeResponse,
    LiveTransitsRequest,
    LiveTransitsResponse,
)
from app.schemas.varga import (
    VargaD1D9Request,
    VargaD1D9Response,
    ShodashvargaRequest,
    ShodashvargaResponse,
)
from app.services.ephemeris import (
    calculate_full_horoscope,
    compute_planetary_positions,
    AYANAMSA_NAMES,
)
from app.services.timezone_utils import resolve_birth_datetime
from app.services.varga_engine import (
    calculate_varga_from_horoscope_dict,
    calculate_shodashvarga,
    calculate_shodashvarga_from_horoscope_dict,
)
from app.services.auth_service import get_current_user, get_supabase_client

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/horoscope", tags=["Horoscope"])


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


@router.post("/calculate", response_model=HoroscopeResponse)
def calculate_horoscope(request: HoroscopeRequest) -> HoroscopeResponse:
    """Calculate Vedic horoscope: planetary positions, houses, ascendant, and panchang."""
    try:
        response = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=request.include_panchang,
            include_outer_planets=request.include_outer_planets,
            include_nabhasha=request.include_nabhasha,
            include_ashtakavarga=request.include_ashtakavarga,
            include_vedic_yogas=request.include_vedic_yogas,
            include_varga=request.include_varga,
            include_doshas=request.include_doshas,
            gender=request.gender or "male",
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
            detail=f"Horoscope calculation failed: {str(exc)}",
        )


@router.post("/varga/d1-d9", response_model=VargaD1D9Response, summary="Calculate D1 Rasi & D9 Navamsa charts")
async def calculate_varga_d1_d9_endpoint(
    request: VargaD1D9Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> VargaD1D9Response:
    """Computes D1 Rasi and D9 Navamsa charts either from ad-hoc birth input or a saved horoscope."""
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
                logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

            if not horoscope_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved horoscope not found or unauthorized.",
                )

            calc_result = horoscope_row.get("calculation_result") or {}
            horo_part = calc_result.get("horoscope")

            if horo_part and isinstance(horo_part, dict):
                varga_cached = horo_part.get("varga_d1_d9")
                if varga_cached and isinstance(varga_cached, dict):
                    return VargaD1D9Response(**varga_cached)
                return calculate_varga_from_horoscope_dict(horo_part)

            # Recompute if snapshot is missing
            computed = calculate_full_horoscope(
                birth_date=horoscope_row["birth_date"],
                birth_time=horoscope_row["birth_time"],
                timezone_str=horoscope_row["timezone"],
                latitude=horoscope_row["latitude"],
                longitude=horoscope_row["longitude"],
                ayanamsa_id=horoscope_row.get("ayanamsa_id", 0),
                house_system_id=horoscope_row.get("house_system_id", 0),
                include_varga=True,
            )
            if computed.varga_d1_d9:
                return computed.varga_d1_d9
            return calculate_varga_from_horoscope_dict(computed.model_dump())

        # Case B: Ad-hoc birth input
        if (
            not request.birth_date
            or not request.birth_time
            or request.latitude is None
            or request.longitude is None
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing required birth parameters (birth_date, birth_time, latitude, longitude) or saved_horoscope_id.",
            )

        computed = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_varga=True,
        )
        if computed.varga_d1_d9:
            return computed.varga_d1_d9
        return calculate_varga_from_horoscope_dict(computed.model_dump())

    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        logger.exception("Varga calculation error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"D1/D9 calculation failed: {str(exc)}",
        )


@router.get("/varga/d1-d9/{horoscope_id}", response_model=VargaD1D9Response, summary="Retrieve D1 Rasi & D9 Navamsa for a saved horoscope")
async def get_saved_horoscope_varga_d1_d9(
    horoscope_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> VargaD1D9Response:
    """Retrieves D1 Rasi and D9 Navamsa charts for a specific saved horoscope."""
    clean_id = _validate_uuid(horoscope_id)
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
        logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

    if not horoscope_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved horoscope not found or unauthorized.",
        )

    calc_result = horoscope_row.get("calculation_result") or {}
    horo_part = calc_result.get("horoscope")

    if horo_part and isinstance(horo_part, dict):
        varga_cached = horo_part.get("varga_d1_d9")
        if varga_cached and isinstance(varga_cached, dict):
            return VargaD1D9Response(**varga_cached)
        return calculate_varga_from_horoscope_dict(horo_part)

    # Recompute if snapshot is missing
    computed = calculate_full_horoscope(
        birth_date=horoscope_row["birth_date"],
        birth_time=horoscope_row["birth_time"],
        timezone_str=horoscope_row["timezone"],
        latitude=horoscope_row["latitude"],
        longitude=horoscope_row["longitude"],
        ayanamsa_id=horoscope_row.get("ayanamsa_id", 0),
        house_system_id=horoscope_row.get("house_system_id", 0),
        include_varga=True,
    )
    if computed.varga_d1_d9:
        return computed.varga_d1_d9
    return calculate_varga_from_horoscope_dict(computed.model_dump())


@router.post("/varga/shodashvarga", response_model=ShodashvargaResponse, summary="Calculate complete 16 Shodashvarga charts")
async def calculate_shodashvarga_endpoint(
    request: ShodashvargaRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> ShodashvargaResponse:
    """Computes all 16 classical Shodashvarga charts (D1 to D60) per BPHS Ch. 6 from ad-hoc input or saved horoscope."""
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
                logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

            if not horoscope_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved horoscope not found or unauthorized.",
                )

            calc_result = horoscope_row.get("calculation_result") or {}
            horo_part = calc_result.get("horoscope")

            if horo_part and isinstance(horo_part, dict):
                return calculate_shodashvarga_from_horoscope_dict(horo_part)

            # Recompute if snapshot is missing
            computed = calculate_full_horoscope(
                birth_date=horoscope_row["birth_date"],
                birth_time=horoscope_row["birth_time"],
                timezone_str=horoscope_row["timezone"],
                latitude=horoscope_row["latitude"],
                longitude=horoscope_row["longitude"],
                ayanamsa_id=horoscope_row.get("ayanamsa_id", 0),
                house_system_id=horoscope_row.get("house_system_id", 0),
                include_varga=True,
            )
            return calculate_shodashvarga_from_horoscope_dict(computed.model_dump())

        # Case B: Ad-hoc birth input
        if (
            not request.birth_date
            or not request.birth_time
            or request.latitude is None
            or request.longitude is None
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide either a saved_horoscope_id or complete birth details (birth_date, birth_time, latitude, longitude).",
            )

        computed = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_varga=True,
        )
        return calculate_shodashvarga_from_horoscope_dict(computed.model_dump())
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        logger.error(f"Shodashvarga calculation error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shodashvarga calculation failed: {str(exc)}",
        )


@router.get("/varga/shodashvarga/{horoscope_id}", response_model=ShodashvargaResponse, summary="Get 16 Shodashvarga charts for saved horoscope")
async def get_saved_horoscope_shodashvarga_endpoint(
    horoscope_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ShodashvargaResponse:
    """Fetch or compute all 16 Shodashvarga charts for an authenticated saved horoscope."""
    clean_id = _validate_uuid(horoscope_id)
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
        logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

    if not horoscope_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved horoscope not found or unauthorized.",
        )

    calc_result = horoscope_row.get("calculation_result") or {}
    horo_part = calc_result.get("horoscope")

    if horo_part and isinstance(horo_part, dict):
        return calculate_shodashvarga_from_horoscope_dict(horo_part)

    computed = calculate_full_horoscope(
        birth_date=horoscope_row["birth_date"],
        birth_time=horoscope_row["birth_time"],
        timezone_str=horoscope_row["timezone"],
        latitude=horoscope_row["latitude"],
        longitude=horoscope_row["longitude"],
        ayanamsa_id=horoscope_row.get("ayanamsa_id", 0),
        house_system_id=horoscope_row.get("house_system_id", 0),
        include_varga=True,
    )
    return calculate_shodashvarga_from_horoscope_dict(computed.model_dump())


def compute_live_transits_data(
    timezone_str: str = "Asia/Kolkata",
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    ayanamsa_id: int = 0,
    target_datetime_str: Optional[str] = None,
) -> LiveTransitsResponse:
    """Core calculation engine for real-time live transits using XALEN ephemeris."""
    if target_datetime_str:
        try:
            dt = datetime.fromisoformat(target_datetime_str)
        except Exception:
            raise HTTPException(status_code=422, detail=f"Invalid target_datetime format: {target_datetime_str}")
    else:
        now_utc = datetime.now(timezone.utc)
        tz_clean = (timezone_str or "Asia/Kolkata").strip()
        if tz_clean.upper() in ("UTC", "Z", "+00:00", "-00:00", "+00", "-00"):
            tz_obj = timezone.utc
        elif tz_clean.startswith(("+", "-")):
            try:
                from app.services.timezone_utils import parse_offset_to_timedelta
                offset_td = parse_offset_to_timedelta(tz_clean)
                tz_obj = timezone(offset_td)
            except Exception:
                tz_obj = timezone.utc
        else:
            try:
                tz_obj = zoneinfo.ZoneInfo(tz_clean)
            except Exception:
                tz_obj = zoneinfo.ZoneInfo("Asia/Kolkata")
        dt = now_utc.astimezone(tz_obj)

    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(
        dt.date(),
        dt.time(),
        timezone_str,
    )

    planets = compute_planetary_positions(
        jd=jd,
        ayanamsa_id=ayanamsa_id,
        include_outer=True,
    )

    aya_name = AYANAMSA_NAMES.get(ayanamsa_id, ("Lahiri", ""))[0]

    return LiveTransitsResponse(
        calculated_at=dt.isoformat(),
        timezone=tz_name,
        ayanamsa_id=ayanamsa_id,
        ayanamsa_name=aya_name,
        julian_day_ut1=jd,
        planets=planets,
    )



@router.get("/live-transits", response_model=LiveTransitsResponse, summary="Get live real-time planetary transits")
def get_live_transits_endpoint(
    timezone: str = "Asia/Kolkata",
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    ayanamsa: int = 0,
    target_datetime: Optional[str] = None,
) -> LiveTransitsResponse:
    """Computes live geocentric sidereal planetary transits using validated XALEN ephemeris."""
    try:
        return compute_live_transits_data(
            timezone_str=timezone,
            latitude=latitude,
            longitude=longitude,
            ayanamsa_id=ayanamsa,
            target_datetime_str=target_datetime,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Live transit calculation error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Live transit calculation failed: {str(exc)}",
        )


@router.post("/live-transits", response_model=LiveTransitsResponse, summary="Post query for live real-time planetary transits")
def post_live_transits_endpoint(
    request: LiveTransitsRequest,
) -> LiveTransitsResponse:
    """Computes live geocentric sidereal planetary transits from request payload."""
    try:
        return compute_live_transits_data(
            timezone_str=request.timezone,
            latitude=request.latitude or 13.0827,
            longitude=request.longitude or 80.2707,
            ayanamsa_id=request.ayanamsa,
            target_datetime_str=request.target_datetime,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Live transit calculation error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Live transit calculation failed: {str(exc)}",
        )




