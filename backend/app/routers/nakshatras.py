"""Nakshatra Shastra & Electoral Transit Router.

Provides deterministic endpoints for:
1. Canonical 28 Nakshatras catalog (27 Constellations + Abhijit)
2. Functional Nature groupings (Fixed, Soft, Swift, Sharp, Movable, Cruel, Mixed)
3. Activity and Electional transit suitability evaluation
4. Pada-level characteristics, Dosha diagnostics, and Remedial Upayas
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.nakshatra_engine import (
    get_all_nakshatras,
    get_nakshatra_by_id_or_name,
    get_functional_natures_summary,
    check_activity_suitability,
    evaluate_birth_star_pada,
    get_28_nakshatra_table,
    get_ebook_treatise,
    get_nakshatra_prediction,
)

router = APIRouter(prefix="/api/v1/nakshatras", tags=["Nakshatra Shastra"])


class ActivityCheckRequest(BaseModel):
    activity: str = Field(..., description="The planned enterprise or activity (e.g., 'laying foundations', 'marriage', 'travel')")
    nakshatra: str = Field(..., description="Nakshatra name or numeric ID (1-28)")


class PadaDoshaRequest(BaseModel):
    nakshatra: str = Field(..., description="Nakshatra name or numeric ID (1-28)")
    pada: int = Field(..., ge=1, le=4, description="Pada quarter number (1-4)")


@router.get("", response_model=List[Dict[str, Any]])
def list_nakshatras(
    nature: Optional[str] = Query(None, description="Filter by functional nature (e.g. Fixed, Soft, Swift, Sharp, Movable, Cruel, Mixed)"),
    direction: Optional[str] = Query(None, description="Filter by gaze direction (Forward, Upward, Downward)"),
    gender: Optional[str] = Query(None, description="Filter by gender (Masculine, Feminine, Hermaphrodite)"),
    result: Optional[str] = Query(None, description="Filter by result grade (GOOD, HARM, OK, MISERY)"),
    search: Optional[str] = Query(None, description="Search by name (English or Tamil), deity, symbol, or activity"),
) -> List[Dict[str, Any]]:
    """List all 28 Nakshatras with comprehensive characteristics and optional filtering."""
    return get_all_nakshatras(
        nature=nature,
        direction=direction,
        gender=gender,
        result=result,
        search=search,
    )


@router.get("/summary-table", response_model=List[Dict[str, Any]])
def get_canonical_table() -> List[Dict[str, Any]]:
    """Get the classical 28-Nakshatra master summary table (including Abhijit)."""
    return get_28_nakshatra_table()


@router.get("/functional-natures", response_model=Dict[str, Any])
def get_functional_natures() -> Dict[str, Any]:
    """Get the 7 functional constellational transit categories, their rules, and suitable activities."""
    return get_functional_natures_summary()


@router.get("/treatise", response_model=Dict[str, Any])
def get_treatise() -> Dict[str, Any]:
    """Get the full canonical 28 Nakshatras E-Book treatise and esoteric philosophy."""
    return get_ebook_treatise()


@router.get("/prediction/{identifier}", response_model=Dict[str, Any])
def get_prediction(
    identifier: str,
    pada: Optional[int] = Query(None, ge=1, le=4, description="Optional pada quarter (1-4)"),
) -> Dict[str, Any]:
    """Get complete predictive report: Moon in star, Ascendant in star, Pada traits, Dosha analysis, and Remedial Upayas."""
    result = get_nakshatra_prediction(identifier, pada=pada)
    if not result.get("valid"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", f"Nakshatra '{identifier}' not found."),
        )
    return result


@router.get("/{identifier}", response_model=Dict[str, Any])
def get_nakshatra_detail(identifier: str) -> Dict[str, Any]:
    """Get complete details, padas, ascendant & moon indications for a single nakshatra."""
    nak = get_nakshatra_by_id_or_name(identifier)
    if not nak:
        raise HTTPException(
            status_code=404,
            detail=f"Nakshatra '{identifier}' not found in canonical catalog.",
        )
    return nak


@router.post("/check-activity", response_model=Dict[str, Any])
def check_activity(req: ActivityCheckRequest) -> Dict[str, Any]:
    """Check if an intended activity or enterprise is auspicious under a given Nakshatra."""
    result = check_activity_suitability(activity=req.activity, nakshatra_name_or_id=req.nakshatra)
    if not result.get("valid"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "Invalid nakshatra query."),
        )
    return result


@router.post("/pada-dosha", response_model=Dict[str, Any])
def check_pada_dosha(req: PadaDoshaRequest) -> Dict[str, Any]:
    """Diagnose birth pada traits, family/native blemishes (Doshas), and required Remedial Upayas (Pariharam)."""
    result = evaluate_birth_star_pada(nakshatra_name_or_id=req.nakshatra, pada=req.pada)
    if not result.get("valid"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "Invalid nakshatra or pada."),
        )
    return result
