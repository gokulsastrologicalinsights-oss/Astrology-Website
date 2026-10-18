"""Horoscope calculation router."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.horoscope import HoroscopeRequest, HoroscopeResponse
from app.services.ephemeris import calculate_full_horoscope

router = APIRouter(prefix="/api/v1/horoscope", tags=["Horoscope"])


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

