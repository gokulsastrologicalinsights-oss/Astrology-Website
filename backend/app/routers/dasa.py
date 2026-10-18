"""Vimshottari Dasa calculation router."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.dasa import DasaRequest, DirectDasaRequest, DasaResponse
from app.services.dasa_service import calculate_dasa, calculate_direct_dasa

router = APIRouter(prefix="/api/v1/horoscope", tags=["Dasa"])


@router.post("/dasa", response_model=DasaResponse)
def calculate_horoscope_dasa(request: DasaRequest) -> DasaResponse:
    """Calculate Vimshottari Dasa hierarchy (depth 1 to 5) and birth balance from birth data."""
    try:
        response = calculate_dasa(
            birth=request,
            depth=request.depth,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            target_date=request.target_date,
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
            detail=f"Dasa calculation failed: {str(exc)}",
        )


@router.post("/dasa/direct", response_model=DasaResponse)
def calculate_dasa_from_moon_deg(request: DirectDasaRequest) -> DasaResponse:
    """Calculate Vimshottari Dasa hierarchy directly from known Moon longitude and birth Julian Day."""
    try:
        response = calculate_direct_dasa(
            moon_sidereal_deg=request.moon_sidereal_deg,
            birth_jd=request.birth_jd,
            depth=request.depth,
            target_date=request.target_date,
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
            detail=f"Direct Dasa calculation failed: {str(exc)}",
        )

