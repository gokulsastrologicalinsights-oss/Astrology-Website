"""Unified Marriage & Life Partner Prediction Router.

Dedicated FastAPI router providing endpoints for:
1. Unified KP + Vedic marriage event prediction and timing windows.
2. Classical 4-step Life Partner / Spouse Nature, Character & Type prediction.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import get_current_user
from app.services.unified_prediction.models import (
    UnifiedMarriageRequest,
    UnifiedMarriageResponse,
)
from app.services.unified_prediction.engine import (
    UnifiedMarriagePredictionService,
)
from app.schemas.spouse_prediction import (
    SpousePredictionRequest,
    SpousePredictionResponse,
)
from app.services.spouse_prediction_engine import (
    SpousePredictionService,
)

logger = logging.getLogger("gai.api.predictions")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """Optional authentication: returns user dict if valid Bearer token provided, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


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
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> UnifiedMarriageResponse:
    """Execute unified marriage prediction pipeline."""
    try:
        response = UnifiedMarriagePredictionService.predict_marriage_event(request)
        return response
    except Exception as exc:
        logger.exception("Unified marriage prediction calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during marriage prediction calculation.",
        ) from None


@router.post(
    "/spouse",
    response_model=SpousePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Life Partner & Spouse Nature, Character & Archetype",
    description=(
        "Classical 4-step Vedic spouse astrology evaluating 7th House occupants, 7th Lord elemental "
        "nature (Fire, Earth, Air, Water), Karakas (Venus, Jupiter, Mars), Navamsa D9 soul profile, "
        "Mind's Desire vs Reality (Moon 7th vs Lagna 7th), quantitative trait scores, and remedies."
    ),
)
async def predict_spouse(
    request: SpousePredictionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> SpousePredictionResponse:
    """Execute life partner and spouse prediction pipeline."""
    try:
        response = SpousePredictionService.predict_spouse(request)
        return response
    except Exception as exc:
        logger.exception("Spouse prediction calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during spouse prediction: {str(exc)}",
        ) from None
