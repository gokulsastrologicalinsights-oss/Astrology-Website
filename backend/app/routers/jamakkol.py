"""Jamakkol Prasanam (ஜாமக்கோள் பிரசன்னம்) API Router.

Exposes endpoints for calculating:
- Real-time 8 Day & 8 Night Jamams
- The Three Pillars: Udhayam, Aarudham, and Kavippu
- The 8 Outer Jamakkol Planets (Jama Grahas)
- Transit Planets (Vaanveethi Grahas) + Gulika/Mandi
- 12 House Placements from Udhayam
- Synthesized classical Prashna verdict, timing, direction, and remedies
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.jamakkol import JamakkolPrasanamRequest, JamakkolPrasanamResponse
from app.services.jamakkol.calculator import calculate_jamakkol_prasanam
from app.services.jamakkol.constants import (
    ZODIAC_SIGNS,
    JAMA_GRAHAS,
    JAMA_SIGNS_ANTICLOCKWISE,
    SURYA_VEETHI_RULES,
    DIRECTIONS_MAP,
)

router = APIRouter(prefix="/api/v1/jamakkol-prasanam", tags=["Jamakkol Prasanam"])


@router.get("/metadata", summary="Get Jamakkol Prasanam foundational astrological metadata")
def get_jamakkol_metadata():
    """Returns metadata for 8 Jama Grahas, 12 Signs, and Surya Veethi classifications."""
    return {
        "jama_grahas": JAMA_GRAHAS,
        "jama_signs_anticlockwise": JAMA_SIGNS_ANTICLOCKWISE,
        "surya_veethi_rules": SURYA_VEETHI_RULES,
        "zodiac_signs": ZODIAC_SIGNS,
        "directions_map": DIRECTIONS_MAP,
    }


@router.post(
    "/calculate",
    response_model=JamakkolPrasanamResponse,
    summary="Calculate Jamakkol Prasanam Horary Chart & Predictions",
)
def compute_jamakkol(request: JamakkolPrasanamRequest):
    """Calculates complete Jamakkol Horary chart, 3 Pillars, Jama Grahas, and rule-based predictions."""
    try:
        res = calculate_jamakkol_prasanam(
            query_dt_str=request.query_datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            tz_str=request.timezone,
            ayanamsa_id=request.ayanamsa_id,
            query_text=request.query_text,
            query_category=request.query_category,
            querent_seed=request.querent_seed,
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Jamakkol Prasanam: {str(e)}",
        )
