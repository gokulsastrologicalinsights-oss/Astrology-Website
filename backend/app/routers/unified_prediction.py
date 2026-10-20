"""Unified Marriage Prediction Router.

Dedicated FastAPI router providing authenticated endpoints for unified KP + Vedic
marriage event prediction, deterministic reconciliation, birth-time sensitivity
diagnostics, and decoupled timing evaluation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth_service import get_current_user
from app.services.unified_prediction.models import (
    UnifiedMarriageRequest,
    UnifiedMarriageResponse,
)
from app.services.unified_prediction.engine import (
    UnifiedMarriagePredictionService,
)

logger = logging.getLogger("gai.api.predictions")

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


@router.post(
    "/marriage",
    response_model=UnifiedMarriageResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Marriage Event (Unified KP + Vedic)",
    description=(
        "Evaluates natal marriage promise under KP and Vedic astrology with continuous "
        "Placidus birth-time sensitivity analysis, decoupled Vimshottari timing windows, "
        "and deterministic reconciliation (M1–M11)."
    ),
)
async def predict_marriage(
    request: UnifiedMarriageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UnifiedMarriageResponse:
    """Execute unified marriage prediction pipeline for authenticated user."""
    try:
        response = UnifiedMarriagePredictionService.predict_marriage_event(request)
        return response
    except Exception as exc:
        logger.exception("Unified marriage prediction calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during marriage prediction calculation.",
        ) from None
