"""FastAPI Router for Tamil Astrology and Daily Dharma Sastra endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status

from app.services.tamil_sastra.service import TamilSastraService
from app.services.tamil_sastra.models import (
    MedicalDeityItem,
    LifeWishDeityItem,
    RamayanaParayanamItem,
    NavagrahaCorrespondenceItem,
    DasaPariharamItem,
    VastuAwakeningTimingItem,
    VastuRuleItem,
    GowriMuhurtaSlot,
    DailyGuidanceRequest,
    DailyGuidanceResponse,
)

router = APIRouter(prefix="/api/v1/tamil-sastra", tags=["Tamil Astrology & Daily Dharma Sastra"])


@router.get("/medical-deities", response_model=List[MedicalDeityItem], summary="Get 22 disease-healing deity mappings")
def get_medical_deities(
    query: Optional[str] = Query(None, description="Search by disease or deity name (EN or TA)"),
    category: Optional[str] = Query(None, description="Filter by body system / disease category"),
):
    """Returns canonical disease-to-deity propitiations from the Tamil Shastra canon."""
    try:
        return TamilSastraService.get_medical_deities(query=query, category=category)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/life-wishes", response_model=List[LifeWishDeityItem], summary="Get deity worship guidelines for 20 life wishes")
def get_life_wishes(
    query: Optional[str] = Query(None, description="Search by life goal or deity (EN or TA)"),
):
    """Returns deity propitiation procedures for 20 life goals (wealth, marriage, education, etc.)."""
    try:
        return TamilSastraService.get_life_wishes(query=query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ramayana-parayanam", response_model=List[RamayanaParayanamItem], summary="Get Valmiki Ramayana Parayanam Sargas")
def get_ramayana_parayanam(
    kandam: Optional[str] = Query(None, description="Filter by Ramayana Kanda"),
    query: Optional[str] = Query(None, description="Search by purpose or chapter name"),
):
    """Returns 19 specific Valmiki Ramayana chapters and sargas for fulfillment of specific desires."""
    try:
        return TamilSastraService.get_ramayana_parayanam(kandam=kandam, query=query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/navagraha-catalog", response_model=List[NavagrahaCorrespondenceItem], summary="Get complete Navagraha attributes")
def get_navagraha_catalog():
    """Returns planetary color, grain, direction, gemstone, incense, deity, metal, flower, and vehicle."""
    try:
        return TamilSastraService.get_navagraha_catalog()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dasa-pariharams", response_model=List[DasaPariharamItem], summary="Get 9 planetary Dasa-Bhukti Pariharams & Temples")
def get_dasa_pariharams():
    """Returns Dasa remedies, charity items, and sacred Tamil Nadu Navagraha sthalams."""
    try:
        return TamilSastraService.get_dasa_pariharams()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/vastu-timings", response_model=List[VastuAwakeningTimingItem], summary="Get 8 annual Vastu Purusha awakening dates & times")
def get_vastu_timings():
    """Returns the 8 specific Tamil solar dates, duration windows, and 36-minute puja timings."""
    try:
        return TamilSastraService.get_vastu_timings()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/vastu-rules", response_model=List[VastuRuleItem], summary="Get 51 classical Vastu Shastra rules")
def get_vastu_rules(category: Optional[str] = Query(None, description="Filter by category (rooms, water, layout, trees, etc.)")):
    """Returns practical Vastu rules for residential harmony and wealth retention."""
    try:
        return TamilSastraService.get_vastu_rules(category=category)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/soolam-pariharam", summary="Get Vaara, Tithi, and Nakshatra Soolam with remedies")
def get_soolam_pariharam():
    """Returns directional travel prohibitions and traditional antidotes."""
    try:
        return TamilSastraService.get_soolam_data()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/gowri-panchangam", response_model=List[GowriMuhurtaSlot], summary="Get Gowri Panchangam slots for weekday")
def get_gowri_panchangam(
    weekday: int = Query(..., ge=0, le=6, description="0=Monday, 1=Tuesday, ..., 6=Sunday")
):
    """Returns the 8 daytime Gowri Muhurta slots (Uthi, Amirtham, Rogam, Labham, Dhanam, Sugam, Visham, Soram)."""
    try:
        return TamilSastraService.get_gowri_panchangam(weekday)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/special-muhurtas", summary="Get special muhurta rules (Debt clearance, Pudhu Kanakku, Deepam wicks)")
def get_special_muhurtas():
    """Returns specialized rules for debt clearance, ledger opening, deepam wicks, and temple pradakshinas."""
    try:
        return TamilSastraService.get_special_muhurtas()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/numerology", summary="Get traditional Tamil numerology for birth dates 1..9")
def get_tamil_numerology(
    birth_number: Optional[int] = Query(None, ge=1, le=9, description="Birth date root number (1..9)")
):
    """Returns lucky/unlucky numbers, colors, and gemstones from classical Tamil numerology."""
    try:
        return TamilSastraService.get_tamil_numerology(birth_number)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/daily-guidance", response_model=DailyGuidanceResponse, summary="Compute comprehensive daily Dharma guidance")
def compute_daily_guidance(request: DailyGuidanceRequest):
    """Computes personalized daily do's and don'ts, Soolam pariharam, Naal Vizhippu, and Gowri slots."""
    try:
        return TamilSastraService.compute_daily_guidance(
            date_str=request.date,
            janma_nakshatra_idx=request.janma_nakshatra_idx,
            janma_rasi_idx=request.janma_rasi_idx,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
