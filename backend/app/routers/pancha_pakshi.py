"""Pancha Pakshi Shastra API Router.

Exposes endpoints for calculating:
- Native's Janma Pakshi (Birth Bird)
- 5 Major Yamams & 25 Antara sub-periods for any date and location
- Golden action windows (peak ruling & eating activities)
- Padupakshi caution windows
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.pancha_pakshi import PanchaPakshiRequest, PanchaPakshiResponse
from app.services.pancha_pakshi.calculator import calculate_pancha_pakshi_bio_rhythms
from app.services.pancha_pakshi.constants import BIRDS, ACTIVITIES

router = APIRouter(prefix="/api/v1/pancha-pakshi", tags=["Pancha Pakshi Shastra"])


@router.get("/birds", summary="Get metadata of all five sacred birds and their attributes")
def get_birds_metadata():
    """Returns attributes, directions, colors, and friendship matrices of the 5 birds."""
    return {
        "birds": BIRDS,
        "activities": ACTIVITIES,
    }


@router.post("/calculate", response_model=PanchaPakshiResponse, summary="Calculate daily Pancha Pakshi bio-rhythms")
def compute_pancha_pakshi(request: PanchaPakshiRequest):
    """Calculates 5-Yamam and 25-Antara bio-rhythms for native's birth bird."""
    try:
        res = calculate_pancha_pakshi_bio_rhythms(
            target_date=request.target_date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone,
            birth_nakshatra_idx=request.birth_nakshatra,
            birth_paksha=request.birth_paksha,
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Pancha Pakshi bio-rhythms: {str(e)}",
        )
