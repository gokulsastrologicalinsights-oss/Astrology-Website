"""Dedicated API endpoints for classical Vedic extensions: Nabhasha Yogas and Ashtakavarga."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.common import BirthInput
from app.schemas.horoscope import HoroscopeRequest
from app.schemas.nabhasha import NabhashaResponse
from app.schemas.ashtakavarga import AshtakavargaResponse
from app.schemas.yoga import VedicYogaResponse
from app.services.ephemeris import calculate_full_horoscope
from app.services.nabhasha_engine import detect_nabhasha_yogas
from app.services.ashtakavarga_engine import calculate_ashtakavarga
from app.services.yoga_engine import calculate_vedic_yogas

router = APIRouter(prefix="/api/v1/vedic", tags=["Vedic Extensions"])


@router.post("/yogas", response_model=VedicYogaResponse)
def calculate_vedic_yogas_endpoint(request: HoroscopeRequest) -> VedicYogaResponse:
    """Evaluate comprehensive classical Vedic Yogas (Gajakesari, Raja, Dhana, Mahapurusha, etc.)."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=True,
            gender=request.gender or "male",
        )
        if not horoscope.vedic_yogas:
            raise HTTPException(status_code=500, detail="Vedic yoga calculation returned empty response")
        horoscope.vedic_yogas.metadata = horoscope.metadata
        return horoscope.vedic_yogas
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vedic yoga calculation failed: {str(exc)}")


@router.post("/nabhasha", response_model=NabhashaResponse)
def calculate_nabhasha_endpoint(request: HoroscopeRequest) -> NabhashaResponse:
    """Detect and return classical Nabhasha Yogas for the given birth data."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=True,
            include_ashtakavarga=False,
        )
        if not horoscope.nabhasha_yogas:
            raise HTTPException(status_code=500, detail="Nabhasha calculation returned empty response")
        horoscope.nabhasha_yogas.metadata = horoscope.metadata
        return horoscope.nabhasha_yogas
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Nabhasha calculation failed: {str(exc)}")


@router.post("/ashtakavarga", response_model=AshtakavargaResponse)
def calculate_ashtakavarga_endpoint(request: HoroscopeRequest) -> AshtakavargaResponse:
    """Compute Bhinnashtakavarga (BAV), Sarvashtakavarga (SAV), and Shodhana reductions."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=True,
        )
        if not horoscope.ashtakavarga:
            raise HTTPException(status_code=500, detail="Ashtakavarga calculation returned empty response")
        horoscope.ashtakavarga.metadata = horoscope.metadata
        return horoscope.ashtakavarga
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ashtakavarga calculation failed: {str(exc)}")
