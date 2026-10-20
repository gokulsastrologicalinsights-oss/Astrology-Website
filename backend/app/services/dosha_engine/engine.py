"""Unified Classical Dosha Engine orchestrator.

Coordinates evaluations for Kuja Dosha, Kaal Sarp Dosha, Sadesati/Saturn transit,
and additional classical doshas (Pitru, Guru Chandal, Shrapit, Grahan).
"""

from typing import List, Optional, Any
from app.schemas.common import CalculationMetadata
from app.schemas.dosha import UnifiedDoshaResponse
from app.services.dosha_engine.models import DoshaChartContext
from app.services.dosha_engine.kuja_dosha import evaluate_kuja_dosha
from app.services.dosha_engine.kaal_sarp import evaluate_kaal_sarp_dosha
from app.services.dosha_engine.sadesati import evaluate_sadesati
from app.services.dosha_engine.additional_doshas import evaluate_additional_doshas


def calculate_unified_doshas(
    planets: List[Any],
    ascendant_sign_idx: int,
    houses: Optional[List[Any]] = None,
    include_2nd_house_in_kuja: bool = True,
    transit_date: Optional[str] = None,
    transit_time: Optional[str] = "12:00:00",
    ayanamsa_id: int = 0,
    metadata: Optional[CalculationMetadata] = None,
) -> UnifiedDoshaResponse:
    """Evaluate all classical Vedic Doshas on authoritative planetary positions.

    Parameters:
    - planets: list of planet objects or dicts (name, sign_index, longitude, degree_in_sign, is_retrograde)
    - ascendant_sign_idx: Ascendant sign index (1-12)
    - houses: optional list of house cusps
    - include_2nd_house_in_kuja: True for South Indian convention, False for North Indian convention
    - transit_date: Optional ISO date (YYYY-MM-DD) for Sadesati evaluation (defaults to current date)
    - transit_time: Optional transit time (HH:MM:SS) for Sadesati evaluation
    - ayanamsa_id: Ayanamsa identifier for XALEN transit calculation (0=Lahiri)
    - metadata: Optional CalculationMetadata
    """
    ctx = DoshaChartContext(
        planets=planets,
        ascendant_sign_idx=ascendant_sign_idx,
        houses=houses,
    )

    # 1. Kuja / Manglik Dosha
    kuja_dosha = evaluate_kuja_dosha(ctx, include_2nd_house=include_2nd_house_in_kuja)

    # 2. Kaal Sarp Dosha
    kaal_sarp_dosha = evaluate_kaal_sarp_dosha(ctx)

    # 3. Retrieve Saturn BAV bindus if Ashtakavarga engine is available
    saturn_bav_bindus = None
    try:
        from app.services.ashtakavarga_engine import calculate_ashtakavarga
        av_res = calculate_ashtakavarga(planets, ascendant_sign_idx)
        if av_res and hasattr(av_res, "bav") and "Saturn" in av_res.bav:
            saturn_bav_bindus = av_res.bav["Saturn"].sign_bindus
    except Exception:
        saturn_bav_bindus = None

    # 4. Sadesati and Saturn Transit
    sadesati = evaluate_sadesati(
        ctx=ctx,
        transit_date=transit_date,
        transit_time=transit_time,
        ayanamsa_id=ayanamsa_id,
        saturn_bav_bindus=saturn_bav_bindus,
    )

    # 5. Additional Classical Doshas (Pitru, Guru Chandal, Shrapit, Grahan Sun, Grahan Moon)
    additional_doshas = evaluate_additional_doshas(ctx)

    # 6. Build Complete Normalized 30-Dosha Catalogue
    from app.services.dosha_engine.catalogue import build_complete_dosha_catalogue
    all_doshas, summary = build_complete_dosha_catalogue(
        ctx=ctx,
        include_2nd_house_in_kuja=include_2nd_house_in_kuja,
        transit_date=transit_date,
        transit_time=transit_time,
        ayanamsa_id=ayanamsa_id,
        saturn_bav_bindus=saturn_bav_bindus,
    )

    # 7. Aggregate Summary Counters (preserved for backward compatibility)
    total_evaluated = 3 + len(additional_doshas)  # Kuja + Kaal Sarp + Sadesati + 5 additional = 8

    active_count = 0
    cancelled_count = 0

    if kuja_dosha.is_present:
        if kuja_dosha.is_cancelled:
            cancelled_count += 1
        else:
            active_count += 1

    if kaal_sarp_dosha.is_present:
        if kaal_sarp_dosha.is_cancelled:
            cancelled_count += 1
        else:
            active_count += 1

    if sadesati.is_active:
        active_count += 1

    for d in additional_doshas:
        if d.is_present:
            if d.is_cancelled:
                cancelled_count += 1
            else:
                active_count += 1

    summary_counts = {
        "total_doshas_evaluated": total_evaluated,
        "total_active_doshas": active_count,
        "total_cancelled_doshas": cancelled_count,
    }

    return UnifiedDoshaResponse(
        metadata=metadata,
        kuja_dosha=kuja_dosha,
        kaal_sarp_dosha=kaal_sarp_dosha,
        sadesati=sadesati,
        additional_doshas=additional_doshas,
        summary_counts=summary_counts,
        all_doshas=all_doshas,
        summary=summary,
    )
