"""KP Daily Horoscope Router.

Provides high-precision daily astrological forecasts for all 12 Rashis (Mesha to Meena)
or a specific Rashi, using Krishnamurti Paddhati (KP) ephemeris and transit sub-lord calculations.
"""

from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.kp_daily_horoscope import (
    KpDailyHoroscopeRequest,
    KpDailyHoroscopeResponse,
)
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/kp/daily-horoscope", tags=["KP Daily Horoscope"])
legacy_router = APIRouter(prefix="/api/kp/daily-horoscope", tags=["KP Daily Horoscope"])


@router.get("", response_model=KpDailyHoroscopeResponse, summary="Get KP daily horoscope for all or specific Rashi")
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


@router.post("", response_model=KpDailyHoroscopeResponse, summary="Post query for KP daily horoscope")
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


# Legacy / mirror routes
@legacy_router.get("", response_model=KpDailyHoroscopeResponse, include_in_schema=False)
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


@legacy_router.post("", response_model=KpDailyHoroscopeResponse, include_in_schema=False)
def post_daily_horoscope_legacy(
    request: KpDailyHoroscopeRequest,
) -> KpDailyHoroscopeResponse:
    return post_daily_horoscope_endpoint(request)
