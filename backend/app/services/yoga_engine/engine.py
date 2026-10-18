"""Vedic Yoga Engine: Main orchestrator coordinating all classical yoga evaluations."""

from typing import List, Optional, Any
from app.schemas.yoga import (
    YogaDetail,
    YogaSummary,
    VedicYogaResponse,
)
from app.services.yoga_engine.models import YogaChartContext
from app.services.yoga_engine.evaluators.classical import evaluate_classical_yogas
from app.services.yoga_engine.evaluators.raja_yogas import evaluate_raja_yogas
from app.services.yoga_engine.evaluators.dhana_yogas import evaluate_dhana_yogas
from app.services.yoga_engine.evaluators.lunar_solar import evaluate_lunar_solar_yogas
from app.services.yoga_engine.evaluators.parivartana import evaluate_parivartana_yogas


def calculate_vedic_yogas(
    planets: List[Any],
    ascendant_sign_idx: int,
    houses: Optional[List[Any]] = None,
    gender: str = "male",
    is_day_birth: Optional[bool] = None,
) -> VedicYogaResponse:
    """Evaluate comprehensive classical Vedic Yogas on authoritative horoscope positions.

    Parameters:
    - planets: list of planet objects or dicts with name, sign_index, longitude, degree_in_sign
    - ascendant_sign_idx: Ascendant sign index (1-12)
    - houses: optional list of house objects
    - gender: 'male' or 'female' (defaults to 'male')
    - is_day_birth: optional bool (if None, derived from Sun's house placement)
    """
    ctx = YogaChartContext(
        planets=planets,
        ascendant_sign_idx=ascendant_sign_idx,
        houses=houses,
        gender=gender,
        is_day_birth=is_day_birth,
    )

    all_yogas: List[YogaDetail] = []

    # Run modular evaluators
    all_yogas.extend(evaluate_classical_yogas(ctx))
    all_yogas.extend(evaluate_raja_yogas(ctx))
    all_yogas.extend(evaluate_dhana_yogas(ctx))
    all_yogas.extend(evaluate_lunar_solar_yogas(ctx))
    all_yogas.extend(evaluate_parivartana_yogas(ctx))

    # Compute summary counts
    total_evaluated = len(all_yogas)
    qualifying_yogas = [y for y in all_yogas if y.is_qualifying]
    cancelled_yogas = [y for y in all_yogas if y.status == "Cancelled"]

    raja_count = len([y for y in qualifying_yogas if y.category == "Raja Yoga"])
    dhana_count = len([y for y in qualifying_yogas if y.category == "Dhana Yoga"])
    mahapurusha_count = len([y for y in qualifying_yogas if y.category == "Panch Mahapurusha"])
    vipareeta_count = len([y for y in qualifying_yogas if y.category == "Vipareeta Raja"])
    other_classical_count = len([
        y for y in qualifying_yogas
        if y.category in {"Major Classical", "Lunar/Solar", "Parivartana"}
    ])

    summary = YogaSummary(
        total_evaluated=total_evaluated,
        total_qualifying=len(qualifying_yogas),
        raja_yogas_count=raja_count,
        dhana_yogas_count=dhana_count,
        mahapurusha_yogas_count=mahapurusha_count,
        vipareeta_yogas_count=vipareeta_count,
        other_classical_count=other_classical_count,
        cancelled_count=len(cancelled_yogas),
    )

    return VedicYogaResponse(
        summary=summary,
        yogas=all_yogas,
    )
