"""FastAPI Router for Kuladeivam (குலதெய்வம்) Finding and Ancestral Guidance.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.schemas.kuladeivam import (
    KuladeivamRequest,
    KuladeivamPrasannaRequest,
    KuladeivamResponse,
    UniversalRefugeTemple,
)
from app.services.kuladeivam_service import (
    KuladeivamService,
    UNIVERSAL_REFUGE_TEMPLES,
    DEITY_KNOWLEDGE_BASE,
)

router = APIRouter(prefix="/api/v1/kuladeivam", tags=["Kuladeivam (Family Deity) Finder"])


@router.post(
    "/find",
    response_model=KuladeivamResponse,
    summary="Find Kuladeivam from Horoscope (5th & 9th Bhavas, D1 & D9)",
)
def find_kuladeivam_from_horoscope(request: KuladeivamRequest) -> KuladeivamResponse:
    """Calculates Kuladeivam profile, deity form, gender, temple direction, and dosha status."""
    try:
        return KuladeivamService.calculate_from_horoscope(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Kuladeivam analysis: {str(e)}",
        )


@router.post(
    "/prasanna",
    response_model=KuladeivamResponse,
    summary="Find Kuladeivam from Horary Jamakkol Prasanam",
)
def find_kuladeivam_from_prasanna(request: KuladeivamPrasannaRequest) -> KuladeivamResponse:
    """Calculates Kuladeivam status and deity indicators for querents without exact birth times."""
    try:
        return KuladeivamService.calculate_from_prasanna(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Prasanna Kuladeivam analysis: {str(e)}",
        )


@router.get(
    "/universal-temples",
    response_model=List[UniversalRefugeTemple],
    summary="Get Universal Refuge Temples for Unknown Kuladeivam",
)
def get_universal_temples():
    """Returns the four classical universal refugee shrines (Tiruchendur, Madurai, Samayapuram, Rameswaram)."""
    return UNIVERSAL_REFUGE_TEMPLES


@router.get(
    "/deity-catalog",
    summary="Get Planetary Deity Correspondences Catalog",
)
def get_deity_catalog():
    """Returns the comprehensive classical planetary deity and sacred tree correspondences."""
    return DEITY_KNOWLEDGE_BASE
