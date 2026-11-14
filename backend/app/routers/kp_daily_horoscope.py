"""KP Daily, Weekly, and Monthly Horoscope & Transit Prediction Router.

Provides high-precision astrological forecasts for all 12 Rashis (Mesha to Meena)
or a specific Rashi, using Krishnamurti Paddhati (KP) ephemeris and Gochara transit calculations.
"""

from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.kp_daily_horoscope import (
    KpDailyHoroscopeRequest,
    KpDailyHoroscopeResponse,
    KpMonthlyHoroscopeRequest,
    KpMonthlyHoroscopeResponse,
    KpWeeklyHoroscopeRequest,
    KpWeeklyHoroscopeResponse,
)
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope
from app.services.kp_period_horoscope_service import (
    compute_kp_monthly_horoscope,
    compute_kp_weekly_horoscope,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["KP Horoscope"])
legacy_router = APIRouter(tags=["KP Horoscope"])


# ============================================================================
# 1. DAILY HOROSCOPE
# ============================================================================

@router.get("/api/v1/kp/daily-horoscope", response_model=KpDailyHoroscopeResponse, summary="Get KP daily horoscope")
def get_daily_horoscope_endpoint(
    target_date: Optional[str] = Query(None, alias="date", description="Target date in YYYY-MM-DD (defaults to today)"),
    timezone: str = Query("Asia/Kolkata", description="IANA timezone or offset string"),
    latitude: float = Query(13.0827, description="Latitude for local ascendant / sunrise"),
    longitude: float = Query(80.2707, description="Longitude for local ascendant / sunrise"),
    rashi: str = Query("all", description="Sign number (1-12), sign name ('Aries'/'Mesha'), or 'all'"),
    ayanamsa: int = Query(1, description="Ayanamsa ID (1 = Krishnamurti KP, 0 = Lahiri)"),
) -> KpDailyHoroscopeResponse:
    """Computes daily KP horoscope and executive brief statements using real-time transits."""
    try:
        return compute_kp_daily_horoscope(
            target_date=target_date,
            timezone_str=timezone,
            latitude=latitude,
            longitude=longitude,
            rashi_filter=rashi,
            ayanamsa_id=ayanamsa,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Daily Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Daily Horoscope calculation failed: {str(exc)}",
        )


@router.post("/api/v1/kp/daily-horoscope", response_model=KpDailyHoroscopeResponse, summary="Post query for KP daily horoscope")
def post_daily_horoscope_endpoint(
    request: KpDailyHoroscopeRequest,
) -> KpDailyHoroscopeResponse:
    """Computes daily KP horoscope from JSON request body."""
    try:
        return compute_kp_daily_horoscope(
            target_date=request.target_date,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude or 13.0827,
            longitude=request.longitude or 80.2707,
            rashi_filter=request.rashi or "all",
            ayanamsa_id=request.ayanamsa if request.ayanamsa is not None else 1,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Daily Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Daily Horoscope calculation failed: {str(exc)}",
        )


# ============================================================================
# 2. WEEKLY HOROSCOPE & TRANSIT PREDICTOR
# ============================================================================

@router.get("/api/v1/kp/weekly-horoscope", response_model=KpWeeklyHoroscopeResponse, summary="Get KP weekly horoscope and transit forecast")
def get_weekly_horoscope_endpoint(
    target_date: Optional[str] = Query(None, alias="date", description="Any date within the target week in YYYY-MM-DD"),
    timezone: str = Query("Asia/Kolkata", description="IANA timezone or offset string"),
    latitude: float = Query(13.0827, description="Latitude"),
    longitude: float = Query(80.2707, description="Longitude"),
    rashi: str = Query("all", description="Sign number (1-12), sign name ('Aries'/'Mesha'), or 'all'"),
    ayanamsa: int = Query(1, description="Ayanamsa ID (1 = Krishnamurti KP, 0 = Lahiri)"),
) -> KpWeeklyHoroscopeResponse:
    """Computes weekly KP horoscope, planetary transits, Chandrashtama alerts, and aspect scores."""
    try:
        return compute_kp_weekly_horoscope(
            target_date=target_date,
            timezone_str=timezone,
            latitude=latitude,
            longitude=longitude,
            rashi_filter=rashi,
            ayanamsa_id=ayanamsa,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Weekly Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Weekly Horoscope calculation failed: {str(exc)}",
        )


@router.post("/api/v1/kp/weekly-horoscope", response_model=KpWeeklyHoroscopeResponse, summary="Post query for KP weekly horoscope")
def post_weekly_horoscope_endpoint(
    request: KpWeeklyHoroscopeRequest,
) -> KpWeeklyHoroscopeResponse:
    """Computes weekly KP horoscope from JSON request body."""
    try:
        return compute_kp_weekly_horoscope(
            target_date=request.target_date,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude or 13.0827,
            longitude=request.longitude or 80.2707,
            rashi_filter=request.rashi or "all",
            ayanamsa_id=request.ayanamsa if request.ayanamsa is not None else 1,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Weekly Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Weekly Horoscope calculation failed: {str(exc)}",
        )


# ============================================================================
# 3. MONTHLY HOROSCOPE & TRANSIT PREDICTOR
# ============================================================================

@router.get("/api/v1/kp/monthly-horoscope", response_model=KpMonthlyHoroscopeResponse, summary="Get KP monthly horoscope and transit forecast")
def get_monthly_horoscope_endpoint(
    year: Optional[int] = Query(None, description="Year (e.g. 2026)"),
    month: Optional[int] = Query(None, description="Month (1-12)"),
    target_date: Optional[str] = Query(None, alias="date", description="Any date within the target month in YYYY-MM-DD"),
    timezone: str = Query("Asia/Kolkata", description="IANA timezone or offset string"),
    latitude: float = Query(13.0827, description="Latitude"),
    longitude: float = Query(80.2707, description="Longitude"),
    rashi: str = Query("all", description="Sign number (1-12), sign name ('Aries'/'Mesha'), or 'all'"),
    ayanamsa: int = Query(1, description="Ayanamsa ID (1 = Krishnamurti KP, 0 = Lahiri)"),
) -> KpMonthlyHoroscopeResponse:
    """Computes monthly KP horoscope, major Gochara movements, Chandrashtama dates, and aspect scores."""
    try:
        return compute_kp_monthly_horoscope(
            year=year,
            month=month,
            target_date=target_date,
            timezone_str=timezone,
            latitude=latitude,
            longitude=longitude,
            rashi_filter=rashi,
            ayanamsa_id=ayanamsa,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Monthly Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Monthly Horoscope calculation failed: {str(exc)}",
        )


@router.post("/api/v1/kp/monthly-horoscope", response_model=KpMonthlyHoroscopeResponse, summary="Post query for KP monthly horoscope")
def post_monthly_horoscope_endpoint(
    request: KpMonthlyHoroscopeRequest,
) -> KpMonthlyHoroscopeResponse:
    """Computes monthly KP horoscope from JSON request body."""
    try:
        return compute_kp_monthly_horoscope(
            year=request.year,
            month=request.month,
            target_date=request.target_date,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude or 13.0827,
            longitude=request.longitude or 80.2707,
            rashi_filter=request.rashi or "all",
            ayanamsa_id=request.ayanamsa if request.ayanamsa is not None else 1,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception(f"KP Monthly Horoscope calculation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Monthly Horoscope calculation failed: {str(exc)}",
        )


# ============================================================================
# LEGACY / MIRROR ROUTES
# ============================================================================

@legacy_router.get("/api/kp/daily-horoscope", response_model=KpDailyHoroscopeResponse, include_in_schema=False)
def get_daily_horoscope_legacy(
    target_date: Optional[str] = Query(None, alias="date"),
    timezone: str = Query("Asia/Kolkata"),
    latitude: float = Query(13.0827),
    longitude: float = Query(80.2707),
    rashi: str = Query("all"),
    ayanamsa: int = Query(1),
) -> KpDailyHoroscopeResponse:
    return get_daily_horoscope_endpoint(
        target_date=target_date,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        rashi=rashi,
        ayanamsa=ayanamsa,
    )


@legacy_router.post("/api/kp/daily-horoscope", response_model=KpDailyHoroscopeResponse, include_in_schema=False)
def post_daily_horoscope_legacy(
    request: KpDailyHoroscopeRequest,
) -> KpDailyHoroscopeResponse:
    return post_daily_horoscope_endpoint(request)


@legacy_router.get("/api/kp/weekly-horoscope", response_model=KpWeeklyHoroscopeResponse, include_in_schema=False)
def get_weekly_horoscope_legacy(
    target_date: Optional[str] = Query(None, alias="date"),
    timezone: str = Query("Asia/Kolkata"),
    latitude: float = Query(13.0827),
    longitude: float = Query(80.2707),
    rashi: str = Query("all"),
    ayanamsa: int = Query(1),
) -> KpWeeklyHoroscopeResponse:
    return get_weekly_horoscope_endpoint(
        target_date=target_date,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        rashi=rashi,
        ayanamsa=ayanamsa,
    )


@legacy_router.get("/api/kp/monthly-horoscope", response_model=KpMonthlyHoroscopeResponse, include_in_schema=False)
def get_monthly_horoscope_legacy(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    target_date: Optional[str] = Query(None, alias="date"),
    timezone: str = Query("Asia/Kolkata"),
    latitude: float = Query(13.0827),
    longitude: float = Query(80.2707),
    rashi: str = Query("all"),
    ayanamsa: int = Query(1),
) -> KpMonthlyHoroscopeResponse:
    return get_monthly_horoscope_endpoint(
        year=year,
        month=month,
        target_date=target_date,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        rashi=rashi,
        ayanamsa=ayanamsa,
    )
