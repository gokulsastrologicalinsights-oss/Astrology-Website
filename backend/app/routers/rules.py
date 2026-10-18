"""Rule-based analysis router (Cultural heuristics & canon audit)."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.rules import (
    RuleAuditNote,
    KujaDoshaStatus,
    CareerAnalysisSummary,
)
from app.schemas.horoscope import HoroscopeRequest
from app.services.ephemeris import calculate_full_horoscope
from app.services.rule_engine import (
    analyze_career_indicators,
    check_kuja_dosha_basic,
    list_documented_rules,
)

router = APIRouter(prefix="/api/v1/rules", tags=["Rule Engine"])


@router.get("/inventory", response_model=List[RuleAuditNote])
def get_rule_inventory() -> List[RuleAuditNote]:
    """List all documented astrological rules and their verification/audit status."""
    return list_documented_rules()


@router.post("/career", response_model=CareerAnalysisSummary)
def get_career_analysis(request: HoroscopeRequest) -> CareerAnalysisSummary:
    """Analyze 10th house, 10th lord, planetary aspects, and Amatyakaraka.

    Traditional Parashari & Jaimini heuristic indicators only.
    """
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
        )
        return analyze_career_indicators(horoscope)
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Career rule analysis failed: {str(exc)}",
        )

