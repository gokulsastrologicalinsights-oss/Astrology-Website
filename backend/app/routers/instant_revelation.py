"""Instant Revelation Router.

Provides instantaneous client intake predictions and an astrologer cold-reading teleprompter.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.instant_revelation import (
    InstantRevelationRequest,
    InstantRevelationResponse,
)
from app.services.instant_revelation.engine import InstantRevelationEngine

router = APIRouter(prefix="/api/v1/instant-revelation", tags=["Instant Revelation"])


@router.post(
    "/analyze",
    response_model=InstantRevelationResponse,
    summary="Generate instant customer intake revelation dossier",
)
def analyze_instant_revelation(request: InstantRevelationRequest) -> InstantRevelationResponse:
    """Instantly synthesizes:

    1. The Mind Reader: Reason for customer arrival (Jamakkol Aarudham/Udhayam + Transit Moon)
    2. Shock Proof: 3 Verifiable past life milestones with calculated calendar years
    3. Personal & Domestic Identifiers: House Vastu, door facing, body scars/moles, family traits
    4. Exact Future Timeline Windows: Red-alert vs golden breakthrough periods for the next 12-24 months
    5. Turn-Key Instant Remedy: Direct temple, weekly karma act, and gemstone/rudraksha
    """
    try:
        return InstantRevelationEngine.analyze(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating instant revelation dossier: {str(exc)}",
        )
