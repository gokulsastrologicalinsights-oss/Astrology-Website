"""KP (Krishnamurti Paddhati) calculation and persistence router."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.kp import (
    KpRequest,
    KpResponse,
    HoraryKpRequest,
    HoraryKpResponse,
    SaveKpChartRequest,
    SavedKpChartItem,
    SavedKpChartListResponse,
    TransitTimelineRequest,
    TransitTimelineResponse,
)
from app.schemas.kp_horary_prediction import (
    InstantHoraryPredictionRequest,
    InstantHoraryPredictionResponse,
    HoraryTopicInfo,
)
from app.schemas.pdf_report import KpPdfReportRequest
from app.schemas.btr import BtrRequest, BtrResponse
from app.services.kp_service import calculate_kp_chart, calculate_horary_chart
from app.services.kp_horary_prediction_service import (
    calculate_instant_horary_prediction,
    get_all_topics,
)
from app.services.kp_transit_timeline import compute_transit_timeline
from app.services.kp_engine.btr_engine import run_birth_time_rectification, EVENT_TEMPLATES
from app.services.auth_service import get_current_user
from app.routers.pdf_reports import get_optional_current_user
from app.services.kp_engine.kp_chart_repository import (
    save_kp_chart,
    list_kp_charts,
    get_kp_chart,
    delete_kp_chart,
)

router = APIRouter(prefix="/api/v1/horoscope", tags=["KP"])


# 1. Natal KP Chart Calculation
@router.post("/kp", response_model=KpResponse, summary="Calculate complete KP Natal chart")
def calculate_horoscope_kp(request: KpRequest) -> KpResponse:
    """Calculate KP 249 sub-division positions, cuspal sub-lords, 4-tier significators, and Dasa."""
    try:
        response = calculate_kp_chart(
            birth=request,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
        )
        return response
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KP calculation failed: {str(exc)}",
        )


# 2. Horary Prashna (1-249) Calculation
@router.post("/kp/horary", response_model=HoraryKpResponse, summary="Calculate authentic KP Horary (1-249) chart")
def calculate_horary_kp(request: HoraryKpRequest) -> HoraryKpResponse:
    """Calculate authentic KP Horary chart with ARMC inversion, Placidus cusps, and significators."""
    try:
        response = calculate_horary_chart(request)
        return response
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KP Horary calculation failed: {str(exc)}",
        )


# 2b. Instant KP Horary / Prashna (1-249) Automated Event Predictor
@router.get("/kp/horary-predict/topics", response_model=List[HoraryTopicInfo], summary="List supported KP Horary Prashna topics")
def list_horary_prediction_topics() -> List[HoraryTopicInfo]:
    """Returns all validated Horary Prashna query topics with primary cusps and supporting houses."""
    return get_all_topics()


@router.post("/kp/horary-predict", response_model=InstantHoraryPredictionResponse, summary="Instant KP Horary / Prashna Automated Event Predictor")
def predict_instant_horary_event(request: InstantHoraryPredictionRequest) -> InstantHoraryPredictionResponse:
    """Evaluates real-time Horary query (1-249) and returns immediate Verdict Card:
    - Outcome: YES (Promised) | DELAYED (With Effort) | NO (Denied)
    - Timing of Fructification: Operating Dasha + exact Moon transit window
    - Astrological Explanation: Dual-language transparent explanation in plain English and Tamil.
    """
    try:
        return calculate_instant_horary_prediction(request)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KP Horary event prediction failed: {str(exc)}",
        )


# 3. Persistence: Save KP Chart (Natal or Horary)
@router.post("/kp/charts", response_model=SavedKpChartItem, summary="Save KP Chart snapshot")
def save_chart(
    request: SaveKpChartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        record = save_kp_chart(current_user["id"], request.model_dump())
        return record
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist KP chart: {str(exc)}",
        )


# 4. Persistence: List Saved KP Charts
@router.get("/kp/charts", response_model=SavedKpChartListResponse, summary="List saved KP Charts")
def list_charts(
    chart_type: Optional[str] = Query(None, description="'natal' or 'horary'"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    all_users: bool = Query(False, description="Admin only: view all users' charts"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin" and all_users
    records = list_kp_charts(
        user_id=current_user["id"],
        chart_type=chart_type,
        limit=limit,
        offset=offset,
        is_admin=is_admin,
    )
    return {"charts": records, "total_count": len(records)}


# 5. Persistence: Get Single Saved KP Chart
@router.get("/kp/charts/{chart_id}", response_model=SavedKpChartItem, summary="Get saved KP Chart snapshot")
def get_chart(
    chart_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    record = get_kp_chart(current_user["id"], chart_id, is_admin=is_admin)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved KP chart not found or unauthorized.",
        )
    return record


# 6. Persistence: Delete Saved KP Chart
@router.delete("/kp/charts/{chart_id}", summary="Delete saved KP Chart")
def delete_chart(
    chart_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    success = delete_kp_chart(current_user["id"], chart_id, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved KP chart not found or unauthorized.",
        )
    return {"status": "success", "message": "Chart deleted successfully."}


# 7. KP Transit Ingress and Sub-Lord Timeline Calculation
@router.post(
    "/kp/transit-timeline",
    response_model=TransitTimelineResponse,
    summary="Calculate KP Transit Ingress and Sub-Lord Timeline",
    description="Calculate exact Sidereal Rashi, Nakshatra, and KP Sub-Lord boundary crossings over a 7-30 day window.",
)
def get_transit_timeline(
    request: TransitTimelineRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> TransitTimelineResponse:
    """Compute high-precision KP Transit Timeline. Requires valid authentication."""
    try:
        result = compute_transit_timeline(
            start_date=request.start_date,
            start_time=request.start_time,
            end_date=request.end_date,
            end_time=request.end_time,
            forecast_days=request.forecast_days,
            timezone_str=request.timezone,
            planets=request.planets,
            ayanamsa_id=request.ayanamsa,
            max_events=request.max_events,
        )
        return TransitTimelineResponse(**result.to_dict())
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="KP Transit Timeline calculation failed.",
        )


# 8. KP PDF Report Generation Endpoints
@router.post("/kp/pdf", summary="Generate dedicated 6-page bilingual KP Astrology PDF report")
async def generate_kp_pdf_direct(
    request: KpPdfReportRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    from app.routers.pdf_reports import generate_kp_pdf_endpoint
    return await generate_kp_pdf_endpoint(request, current_user=current_user)


@router.get("/kp/charts/{chart_id}/pdf", summary="Download a 6-page KP PDF report by saved ID")
async def download_kp_chart_pdf_direct(
    chart_id: str,
    language: str = "en",
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    from app.routers.pdf_reports import download_kp_pdf_by_id_endpoint
    return await download_kp_pdf_by_id_endpoint(chart_id, language=language, current_user=current_user)


# 9. KP Birth Time Rectification (BTR) Endpoints
@router.post("/kp/rectify", response_model=BtrResponse, summary="Perform KP Birth Time Rectification")
def rectify_birth_time(request: BtrRequest) -> BtrResponse:
    """Rectify birth time using past life events, KP Lagna Sub-Lord, and Vimshottari Dasa."""
    try:
        return run_birth_time_rectification(request)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Birth time rectification failed: {str(exc)}",
        )


@router.get("/kp/rectify/templates", summary="Get standard life event templates for BTR")
def get_btr_event_templates():
    """Returns canonical life event presets (Marriage, Career, Childbirth, Accident, etc.)."""
    return {"templates": EVENT_TEMPLATES}





# ---------------------------------------------------------------------------
# 10. KP Reader 2 (Fundamental Principles) Endpoints
# ---------------------------------------------------------------------------
from app.schemas.kp_reader2 import (
    SignClassificationSchema,
    SignSignificationSchema,
    HouseSignificationSchema,
    PlanetSignificationSchema,
    AstrologerAptitudeRequest,
    AstrologerAptitudeResponse,
    SpeechFertilityRequest,
    SpeechFertilityResponse,
    KarmaEvaluationRequest,
    KarmaEvaluationResponse,
    FortunaRequest,
    FortunaResponse,
)
from app.services.kp_engine.reader2 import (
    classify_sign,
    evaluate_astrologer_proficiency,
    evaluate_speech_and_fertility,
    evaluate_karma_category,
    calculate_kp_fortuna,
    SIGN_SIGNIFICATIONS,
    HOUSE_SIGNIFICATIONS_KP,
    PLANET_SIGNIFICATIONS_KP,
)


@router.get(
    "/kp/reader2/classifications",
    summary="Get 13-fold classification of Zodiac signs per KP Reader 2",
    description="Returns positive/negative, element, mobility, fertility, voice/mute, violent, human/bestial, and ascension characteristics.",
)
def get_sign_classifications(
    sign: Optional[str] = Query(None, description="Optional sign name (e.g. 'Aries', 'Cancer')"),
):
    if sign:
        s = sign.strip().title()
        if s not in SIGN_SIGNIFICATIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sign '{sign}' not recognized.",
            )
        return classify_sign(s)
    
    return {s: classify_sign(s) for s in SIGN_SIGNIFICATIONS}


@router.get(
    "/kp/reader2/signs",
    summary="Get comprehensive sign significations per KP Reader 2 Chapter 16",
    description="Returns physical appearance, mental tendencies, health/diseases, finance, romance, profession, places, direction, lucky stones/numbers.",
)
def get_kp_signs(
    sign: Optional[str] = Query(None, description="Optional sign name (e.g. 'Taurus')"),
):
    if sign:
        s = sign.strip().title()
        if s not in SIGN_SIGNIFICATIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sign '{sign}' not recognized.",
            )
        return SIGN_SIGNIFICATIONS[s]
    return SIGN_SIGNIFICATIONS


@router.get(
    "/kp/reader2/houses",
    summary="Get 12 Bhavas detailed significations per KP Reader 2 Chapter 17",
    description="Returns primary matters, anatomy, relatives, favorable/unfavorable connections, and Karakas for houses 1 to 12.",
)
def get_kp_houses(
    house: Optional[int] = Query(None, ge=1, le=12, description="Optional house number (1-12)"),
):
    if house:
        return HOUSE_SIGNIFICATIONS_KP[house]
    return HOUSE_SIGNIFICATIONS_KP


@router.get(
    "/kp/reader2/planets",
    summary="Get planetary significations per KP Reader 2 Chapter 18",
    description="Returns astronomy, physical features, mental qualities, pathology, professions, places, lucky stones, and KP doctrine for planets.",
)
def get_kp_planets(
    planet: Optional[str] = Query(None, description="Optional planet name (e.g. 'Mercury', 'Uranus', 'Fortuna')"),
):
    if planet:
        p = planet.strip().title()
        if p not in PLANET_SIGNIFICATIONS_KP:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planet '{planet}' not found in KP Reader 2.",
            )
        return PLANET_SIGNIFICATIONS_KP[p]
    return PLANET_SIGNIFICATIONS_KP


@router.post(
    "/kp/reader2/evaluate-astrologer",
    response_model=AstrologerAptitudeResponse,
    summary="Evaluate astrological learning aptitude per KP Reader 2 Chapter 14",
    description="Evaluates whether a chart possesses the planetary combinations to master astrology (Moon in Cancer, Mercury-Moon harmony, Saturn-Mercury depth, etc.).",
)
def evaluate_astrologer(request: AstrologerAptitudeRequest) -> AstrologerAptitudeResponse:
    res = evaluate_astrologer_proficiency(
        mercury_sign=request.mercury_sign,
        moon_sign=request.moon_sign,
        uranus_sign=request.uranus_sign,
        saturn_sign=request.saturn_sign,
        jupiter_sign=request.jupiter_sign,
        mars_sign=request.mars_sign,
        ascendant_sign=request.ascendant_sign,
        mercury_house=request.mercury_house,
        moon_house=request.moon_house,
        jupiter_house=request.jupiter_house,
        saturn_house=request.saturn_house,
        uranus_house=request.uranus_house,
        is_moon_mercury_aspect=request.is_moon_mercury_aspect,
        is_saturn_mercury_aspect=request.is_saturn_mercury_aspect,
        is_jupiter_mercury_aspect=request.is_jupiter_mercury_aspect,
        is_uranus_mercury_aspect=request.is_uranus_mercury_aspect,
    )
    return AstrologerAptitudeResponse(
        score=res.score,
        aptitude_grade=res.aptitude_grade,
        factors_present=res.factors_present,
        recommendations=res.recommendations,
        reasons=res.reasons,
    )


@router.post(
    "/kp/reader2/speech-fertility",
    response_model=SpeechFertilityResponse,
    summary="Evaluate speech defects and fertility promise per KP Reader 2 Chapter 15",
    description="Checks 2nd cusp mute/voice signs and 5th/11th cusps fruitful/barren signs per Prof. Krishnamurti.",
)
def evaluate_speech_fertility(request: SpeechFertilityRequest) -> SpeechFertilityResponse:
    res = evaluate_speech_and_fertility(
        cusp_2_sign=request.cusp_2_sign,
        cusp_5_sign=request.cusp_5_sign,
        cusp_11_sign=request.cusp_11_sign,
        mercury_sign=request.mercury_sign,
        mercury_afflicted_by_saturn_mars=request.mercury_afflicted_by_saturn_mars,
        planets_in_5th=request.planets_in_5th,
        planets_in_11th=request.planets_in_11th,
    )
    return SpeechFertilityResponse(
        speech_condition=res.speech_condition,
        speech_reasons=res.speech_reasons,
        fertility_promise=res.fertility_promise,
        fertility_reasons=res.fertility_reasons,
    )


@router.post(
    "/kp/reader2/karma",
    response_model=KarmaEvaluationResponse,
    summary="Evaluate past Karma category per KP Reader 2 Chapter 10 & 12",
    description="Classifies native's karma as Dhruda, Dhruda-Adhruda, or Adhruda based on Jupiter and 9th lord connections.",
)
def evaluate_karma(request: KarmaEvaluationRequest) -> KarmaEvaluationResponse:
    res = evaluate_karma_category(
        lagna_aspect_from_jupiter_or_9th_lord=request.lagna_aspect_from_jupiter_or_9th_lord,
        moon_aspect_from_jupiter_or_9th_lord=request.moon_aspect_from_jupiter_or_9th_lord,
        dasa_lord_aspect_from_jupiter_or_9th_lord=request.dasa_lord_aspect_from_jupiter_or_9th_lord,
        jupiter_or_9th_lord_in_lagna_or_moon=request.jupiter_or_9th_lord_in_lagna_or_moon,
    )
    return KarmaEvaluationResponse(
        karma_type=res.karma_type,
        severity_level=res.severity_level,
        mitigation_potential=res.mitigation_potential,
        chart_indications=res.chart_indications,
        philosophical_counsel=res.philosophical_counsel,
    )


@router.post(
    "/kp/reader2/fortuna",
    response_model=FortunaResponse,
    summary="Calculate KP Pars Fortunae (Fortuna) per KP Reader 2 Chapter 18 & pp. 74-75",
    description="Calculates exact longitude, sign, star, sub-lord, and transit significance for Pars Fortunae.",
)
def get_fortuna(request: FortunaRequest) -> FortunaResponse:
    res = calculate_kp_fortuna(
        ascendant_deg=request.ascendant_deg,
        moon_deg=request.moon_deg,
        sun_deg=request.sun_deg,
        is_day_birth=request.is_day_birth,
    )
    return FortunaResponse(
        longitude=res.longitude,
        sign=res.sign,
        sign_lord=res.sign_lord,
        star=res.star,
        star_lord=res.star_lord,
        sub_lord=res.sub_lord,
        is_day_birth=res.is_day_birth,
        formula_used=res.formula_used,
        signification=res.signification,
    )


# ---------------------------------------------------------------------------
# 11. KP Reader 3 (Predictive Stellar Astrology) Endpoints
# ---------------------------------------------------------------------------
from app.schemas.kp_reader3 import (
    Kp249DivisionSchema,
    Kp249TableResponse,
    CuspalSubLordItemSchema,
    CuspalSubLordsRequest,
    CuspalSubLordsResponse,
    PlanetarySubLordItemSchema,
    PlanetarySubLordsRequest,
    PlanetarySubLordsResponse,
    TwinDivergenceRequest,
    TwinDivergenceResponse,
    LagnaStarSignificationResponse,
)
from app.services.kp_engine.reader3 import (
    generate_kp_249_table,
    lookup_249_by_number,
    lookup_249_by_longitude,
    lookup_249_by_lords,
    search_249_table,
    compute_cuspal_sub_lords,
    compute_planetary_sub_lords,
    differentiate_twin_births,
    LAGNA_STAR_SIGNIFICATIONS,
)


@router.get(
    "/kp/reader3/table-249",
    response_model=Kp249TableResponse,
    summary="Get KP Reader 3 authoritative 249 sub-division table",
    description="Returns the 249 sub-divisions with exact arc-minute/arc-second boundaries, sign/star/sub lords, and medical/vocational significations.",
)
def get_kp_249_table(
    query: Optional[str] = Query(None, description="Optional search keyword for profession, disease, or anatomy"),
    sign: Optional[str] = Query(None, description="Filter by Zodiac sign (e.g. 'Aries')"),
    star: Optional[str] = Query(None, description="Filter by Nakshatra (e.g. 'Ashwini')"),
    star_lord: Optional[str] = Query(None, description="Filter by Star Lord (e.g. 'Ketu')"),
    sub_lord: Optional[str] = Query(None, description="Filter by Sub-Lord (e.g. 'Venus')"),
    limit: Optional[int] = Query(None, ge=1, le=249, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset results"),
) -> Kp249TableResponse:
    matches = search_249_table(
        query=query,
        sign=sign,
        star=star,
        star_lord=star_lord,
        sub_lord=sub_lord,
    )
    if offset:
        matches = matches[offset:]
    if limit:
        matches = matches[:limit]

    return Kp249TableResponse(
        total_divisions=len(matches),
        divisions=[
            Kp249DivisionSchema(
                number=d.number,
                sign=d.sign,
                sign_lord=d.sign_lord,
                star=d.star,
                star_lord=d.star_lord,
                sub_lord=d.sub_lord,
                start_deg=d.start_deg,
                end_deg=d.end_deg,
                sign_start_deg=d.sign_start_deg,
                sign_end_deg=d.sign_end_deg,
                start_dms=d.start_dms,
                end_dms=d.end_dms,
                sign_start_dms=d.sign_start_dms,
                sign_end_dms=d.sign_end_dms,
                span_arcmin=d.span_arcmin,
                body_parts=d.body_parts,
                diseases=d.diseases,
                mental_qualities=d.mental_qualities,
                professions=d.professions,
            )
            for d in matches
        ],
    )


@router.get(
    "/kp/reader3/table-249/{number}",
    response_model=Kp249DivisionSchema,
    summary="Get single KP 249 sub-division by number (1-249)",
    description="Returns exact degrees, lords, and Reader 3 profile for a given horary division.",
)
def get_kp_249_by_number(number: int) -> Kp249DivisionSchema:
    if not 1 <= number <= 249:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"KP division number must be between 1 and 249, got {number}",
        )
    d = lookup_249_by_number(number)
    return Kp249DivisionSchema(
        number=d.number,
        sign=d.sign,
        sign_lord=d.sign_lord,
        star=d.star,
        star_lord=d.star_lord,
        sub_lord=d.sub_lord,
        start_deg=d.start_deg,
        end_deg=d.end_deg,
        sign_start_deg=d.sign_start_deg,
        sign_end_deg=d.sign_end_deg,
        start_dms=d.start_dms,
        end_dms=d.end_dms,
        sign_start_dms=d.sign_start_dms,
        sign_end_dms=d.sign_end_dms,
        span_arcmin=d.span_arcmin,
        body_parts=d.body_parts,
        diseases=d.diseases,
        mental_qualities=d.mental_qualities,
        professions=d.professions,
    )


@router.get(
    "/kp/reader3/lookup-longitude",
    response_model=Kp249DivisionSchema,
    summary="Lookup 249 sub-division by sidereal longitude",
    description="Maps any sidereal degree (0-360°) to its exact KP Reader 3 sub-division.",
)
def lookup_by_longitude(
    longitude: float = Query(..., description="Sidereal longitude in degrees (0 to 360)"),
) -> Kp249DivisionSchema:
    d = lookup_249_by_longitude(longitude)
    return Kp249DivisionSchema(
        number=d.number,
        sign=d.sign,
        sign_lord=d.sign_lord,
        star=d.star,
        star_lord=d.star_lord,
        sub_lord=d.sub_lord,
        start_deg=d.start_deg,
        end_deg=d.end_deg,
        sign_start_deg=d.sign_start_deg,
        sign_end_deg=d.sign_end_deg,
        start_dms=d.start_dms,
        end_dms=d.end_dms,
        sign_start_dms=d.sign_start_dms,
        sign_end_dms=d.sign_end_dms,
        span_arcmin=d.span_arcmin,
        body_parts=d.body_parts,
        diseases=d.diseases,
        mental_qualities=d.mental_qualities,
        professions=d.professions,
    )


@router.post(
    "/kp/reader3/cuspal-sub-lords",
    response_model=CuspalSubLordsResponse,
    summary="Compute 12 Cuspal Sub-Lords per KP Reader 3",
    description="Evaluates all 12 Placidus house cusps, identifying their sign lord, star lord, sub-lord, sub-sub lord, 249 division, and cuspal promise.",
)
def get_cuspal_sub_lords(request: CuspalSubLordsRequest) -> CuspalSubLordsResponse:
    cusps = request.cusp_longitudes

    if not cusps and request.birth:
        from app.services.kp_service import calculate_kp_chart
        kp_res = calculate_kp_chart(
            birth=request.birth,
            ayanamsa_id=request.birth.ayanamsa if hasattr(request.birth, 'ayanamsa') else 1,
            house_system_id="P",
        )
        cusps = [c.cusp_degree for c in kp_res.cuspal_analysis]

    if not cusps or len(cusps) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 12 cusp_longitudes or valid birth input must be provided.",
        )

    computed = compute_cuspal_sub_lords(
        cusp_longitudes=cusps,
        planet_significators=request.planet_significators,
    )

    items = [
        CuspalSubLordItemSchema(
            house=c.house,
            longitude=c.longitude,
            longitude_dms=c.longitude_dms,
            sign=c.sign,
            sign_lord=c.sign_lord,
            star=c.star,
            star_lord=c.star_lord,
            sub_lord=c.sub_lord,
            sub_sub_lord=c.sub_sub_lord,
            pada=c.pada,
            division_249_number=c.division_249_number,
            division_span_dms=c.division_span_dms,
            promise=c.promise,
            favorable_houses=c.favorable_houses,
            unfavorable_houses=c.unfavorable_houses,
            reader3_ruling=c.reader3_ruling,
            sub_significations=c.sub_significations,
        )
        for c in computed
    ]

    return CuspalSubLordsResponse(
        cuspal_sub_lords=items,
        calculation_notes=(
            "As codified by Prof. K. S. Krishnamurti in KP Reader 3: The cusp position indicates the matters "
            "signified by its star lord, while the Sub-Lord is the final decisive factor that approves or denies "
            "the fructification of that house's promise."
        ),
    )


@router.post(
    "/kp/reader3/planetary-sub-lords",
    response_model=PlanetarySubLordsResponse,
    summary="Compute Planetary Sub-Lords and 3-Tier Agency per KP Reader 3",
    description="Computes planetary sub-lords and breaks down the 3-tier KP agency: Planet (Source/How), Star Lord (Nature of Result/What), Sub-Lord (Decision/Outcome).",
)
def get_planetary_sub_lords(request: PlanetarySubLordsRequest) -> PlanetarySubLordsResponse:
    positions = request.planet_positions
    cusps = request.cusp_longitudes
    lagna = request.lagna_sign

    if not positions and request.birth:
        from app.services.kp_service import calculate_kp_chart
        kp_res = calculate_kp_chart(
            birth=request.birth,
            ayanamsa_id=request.birth.ayanamsa if hasattr(request.birth, 'ayanamsa') else 1,
            house_system_id="P",
        )
        positions = {p.planet: p.longitude for p in kp_res.planetary_positions}
        cusps = [c.cusp_degree for c in kp_res.cuspal_analysis]
        lagna = kp_res.cuspal_analysis[0].sign

    if not positions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either planet_positions dictionary or valid birth input must be provided.",
        )

    computed = compute_planetary_sub_lords(
        positions=positions,
        cusps=cusps,
        lagna_sign=lagna,
    )

    items = {
        planet: PlanetarySubLordItemSchema(
            planet=p.planet,
            longitude=p.longitude,
            longitude_dms=p.longitude_dms,
            house=p.house,
            sign=p.sign,
            sign_lord=p.sign_lord,
            star=p.star,
            star_lord=p.star_lord,
            sub_lord=p.sub_lord,
            sub_sub_lord=p.sub_sub_lord,
            pada=p.pada,
            division_249_number=p.division_249_number,
            division_span_dms=p.division_span_dms,
            source_planet=p.source_planet,
            nature_star_lord=p.nature_star_lord,
            decision_sub_lord=p.decision_sub_lord,
            star_houses_for_lagna=p.star_houses_for_lagna,
            sub_significations=p.sub_significations,
            reader3_interpretation=p.reader3_interpretation,
        )
        for planet, p in computed.items()
    }

    effective_lagna = lagna or (computed["Sun"].sign if "Sun" in computed else "Aries")

    return PlanetarySubLordsResponse(
        lagna_sign=effective_lagna,
        planetary_sub_lords=items,
        three_tier_doctrine=(
            "KP Reader 3 Golden Rule: Planet = Source of light (how results manifest through nature and occupation); "
            "Star Lord = Nature of result (matters of houses owned and occupied); Sub-Lord = Decisive arbiter "
            "(whether favorable or unfavorable)."
        ),
    )


@router.post(
    "/kp/reader3/twin-divergence",
    response_model=TwinDivergenceResponse,
    summary="Demonstrate Twin Birth Differentiation via KP Sub-Lord theory",
    description="Illustrates why twins born minutes apart with identical Rasi & Navamsa diverge in profession and destiny due to Sub-Lord shifts.",
)
def evaluate_twin_divergence(request: TwinDivergenceRequest) -> TwinDivergenceResponse:
    res = differentiate_twin_births(
        lagna1_deg=request.lagna1_deg,
        lagna2_deg=request.lagna2_deg,
    )
    return TwinDivergenceResponse(
        lagna1_deg=res.lagna1_deg,
        lagna2_deg=res.lagna2_deg,
        twin1_sub_lord=res.twin1_sub_lord,
        twin2_sub_lord=res.twin2_sub_lord,
        twin1_div_number=res.twin1_div_number,
        twin2_div_number=res.twin2_div_number,
        twin1_professions=res.twin1_professions,
        twin2_professions=res.twin2_professions,
        twin1_medical=res.twin1_medical,
        twin2_medical=res.twin2_medical,
        reader3_explanation=res.reader3_explanation,
    )


@router.get(
    "/kp/reader3/lagna-star-significations",
    summary="Get Reader 3 Star House Significations for all 12 Lagnas",
    description="Returns the houses owned and operational nature of the 9 Star Lords across all 12 Lagnas per KP Reader 3.",
)
def get_lagna_star_significations(
    lagna: Optional[str] = Query(None, description="Optional Lagna sign name (e.g. 'Aries', 'Leo')"),
):
    if lagna:
        l_norm = lagna.strip().title()
        if l_norm not in LAGNA_STAR_SIGNIFICATIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lagna '{lagna}' not recognized.",
            )
        return {"lagna": l_norm, "star_significations": LAGNA_STAR_SIGNIFICATIONS[l_norm]}
    return LAGNA_STAR_SIGNIFICATIONS


# ---------------------------------------------------------------------------
# 12. KP Reader 4 (Marriage, Married Life & Children) Endpoints
# ---------------------------------------------------------------------------
from app.schemas.kp_reader4 import (
    MarsDoshaRequest,
    MarsDoshaResponse,
    MarsDoshaSourceDetailSchema,
    MarsDoshaPariharaSchema,
    PunarphooRequest,
    PunarphooResponse,
    SpouseAppearanceRequest,
    SpouseAppearanceResponse,
    CareerSpouseRequest,
    CareerSpouseResponse,
    MarriagePromiseRequest,
    MarriagePromiseResponse,
    SecondMarriageRequest,
    SecondMarriageResponse,
    ProgenyPromiseRequest,
    ProgenyPromiseResponse,
    KasyapaSeventhStarRequest,
    KasyapaSeventhStarResponse,
)
from app.services.kp_engine.reader4 import (
    evaluate_mars_dosha_reader4,
    evaluate_punarphoo_reader4,
    lookup_spouse_appearance_reader4,
    evaluate_career_spouse_reader4,
    evaluate_marriage_promise_reader4,
    evaluate_second_marriage_reader4,
    evaluate_progeny_reader4,
    evaluate_kasyapa_seventh_star,
)


@router.post(
    "/kp/reader4/mars-dosha",
    response_model=MarsDoshaResponse,
    summary="Evaluate authentic Mars Dosha & 10 Classical Pariharas per KP Reader 4",
    description="Evaluates Mars placement sign-to-sign from Lagna, Moon, and Venus across houses 1, 2, 4, 7, 8, 12, checks all 10 Classical Pariharas, and resolves with KP Cuspal Sub-Lord.",
)
def evaluate_mars_dosha(request: MarsDoshaRequest) -> MarsDoshaResponse:
    res = evaluate_mars_dosha_reader4(
        mars_sign=request.mars_sign,
        lagna_sign=request.lagna_sign,
        moon_sign=request.moon_sign,
        venus_sign=request.venus_sign,
        is_mars_conjunct_or_aspected_by_jupiter=request.is_mars_conjunct_or_aspected_by_jupiter,
        is_mars_conjunct_or_aspected_by_mercury=request.is_mars_conjunct_or_aspected_by_mercury,
        is_mars_conjunct_moon=request.is_mars_conjunct_moon,
        is_mars_conjunct_jupiter_within_8deg=request.is_mars_conjunct_jupiter_within_8deg,
        seventh_csl_signifies_6_10_12=request.seventh_csl_signifies_6_10_12,
    )
    return MarsDoshaResponse(
        raw_dosha_present=res.raw_dosha_present,
        total_score=res.total_score,
        source_details=[
            MarsDoshaSourceDetailSchema(
                reference_point=s.reference_point,
                reference_sign=s.reference_sign,
                mars_sign=s.mars_sign,
                counted_house=s.counted_house,
                has_dosha=s.has_dosha,
                dosha_weight=s.dosha_weight,
                reasons=s.reasons,
            )
            for s in res.source_details
        ],
        pariharas_applicable=[
            MarsDoshaPariharaSchema(
                rule_id=p.rule_id,
                rule_name=p.rule_name,
                description=p.description,
                applies=p.applies,
            )
            for p in res.pariharas_applicable
        ],
        is_mitigated=res.is_mitigated,
        kp_cuspal_override=res.kp_cuspal_override,
        recommendation=res.recommendation,
        shastric_verdict=res.shastric_verdict,
    )


@router.post(
    "/kp/reader4/punarphoo",
    response_model=PunarphooResponse,
    summary="Detect Punarphoo (Saturn-Moon impediment) per KP Reader 4 Chapter 22",
    description="Detects Saturn-Moon connections, predicts negotiation delays, wedding postponements, and matches against Prof. Krishnamurti's 4 historical case histories.",
)
def evaluate_punarphoo(request: PunarphooRequest) -> PunarphooResponse:
    res = evaluate_punarphoo_reader4(
        saturn_sign=request.saturn_sign,
        moon_sign=request.moon_sign,
        saturn_star=request.saturn_star,
        moon_star=request.moon_star,
        saturn_sub=request.saturn_sub,
        moon_sub=request.moon_sub,
        saturn_house=request.saturn_house,
        moon_house=request.moon_house,
        saturn_aspects_moon=request.saturn_aspects_moon,
        is_rahu_or_ketu_representing_saturn_or_moon=request.is_rahu_or_ketu_representing_saturn_or_moon,
    )
    return PunarphooResponse(
        is_punarphoo_present=res.is_punarphoo_present,
        severity=res.severity,
        connections_found=res.connections_found,
        case_study_analogy=res.case_study_analogy,
        predicted_impediments=res.predicted_impediments,
        kp_counsel=res.kp_counsel,
    )


@router.post(
    "/kp/reader4/spouse-appearance",
    response_model=SpouseAppearanceResponse,
    summary="Lookup spouse physical features & characteristics by 7th Cusp Sub-Lord per KP Reader 4 Chapter 29",
    description="Retrieves stature, facial structure, complexion, temperament, and lifestyle traits of the spouse across all 9 planets in all 12 signs.",
)
def get_spouse_appearance(request: SpouseAppearanceRequest) -> SpouseAppearanceResponse:
    res = lookup_spouse_appearance_reader4(
        csl_planet=request.csl_planet,
        csl_sign=request.csl_sign,
        node_conjunction=request.node_conjunction,
        node_aspect=request.node_aspect,
        node_star_lord=request.node_star_lord,
    )
    return SpouseAppearanceResponse(
        csl_planet=res.csl_planet,
        csl_sign=res.csl_sign,
        stature=res.stature,
        complexion_and_face=res.complexion_and_face,
        temperament=res.temperament,
        vocational_and_lifestyle_traits=res.vocational_and_lifestyle_traits,
        cautionary_notes=res.cautionary_notes,
        shastric_quote=res.shastric_quote,
    )


@router.post(
    "/kp/reader4/career-spouse",
    response_model=CareerSpouseResponse,
    summary="Evaluate Career Wife / Working Partner promise per KP Reader 4 Chapter 32",
    description="Checks whether 4th Cusp Sub-Lord signifies 4, 8, or 12 (10th, 2nd, and 6th houses of spouse).",
)
def evaluate_career_spouse(request: CareerSpouseRequest) -> CareerSpouseResponse:
    res = evaluate_career_spouse_reader4(
        fourth_csl_planet=request.fourth_csl_planet,
        fourth_csl_signifies=request.fourth_csl_signifies,
        is_mars_involved=request.is_mars_involved,
    )
    return CareerSpouseResponse(
        will_marry_career_spouse=res.will_marry_career_spouse,
        fourth_csl_planet=res.fourth_csl_planet,
        fourth_csl_signifies=res.fourth_csl_signifies,
        matching_houses=res.matching_houses,
        spouse_vocation_type=res.spouse_vocation_type,
        explanation=res.explanation,
    )


@router.post(
    "/kp/reader4/marriage-promise",
    response_model=MarriagePromiseResponse,
    summary="Evaluate Marriage Promise, Delay & Denial ('Grapes are Sour') per KP Reader 4",
    description="Checks 7th Cusp Sub-Lord for supporting houses (2, 7, 11) vs denying houses (1, 6, 10, 4) and identifies permanent denial.",
)
def evaluate_marriage_promise(request: MarriagePromiseRequest) -> MarriagePromiseResponse:
    res = evaluate_marriage_promise_reader4(
        seventh_csl_planet=request.seventh_csl_planet,
        seventh_csl_signifies=request.seventh_csl_signifies,
        is_saturn_connected=request.is_saturn_connected,
        is_saturn_in_5th=request.is_saturn_in_5th,
        is_mars_in_8th=request.is_mars_in_8th,
    )
    return MarriagePromiseResponse(
        verdict=res.verdict,
        seventh_csl_planet=res.seventh_csl_planet,
        supporting_significations=res.supporting_significations,
        denying_significations=res.denying_significations,
        is_denied=res.is_denied,
        delay_factors=res.delay_factors,
        philosophical_verdict=res.philosophical_verdict,
        detailed_reasoning=res.detailed_reasoning,
    )


@router.post(
    "/kp/reader4/second-marriage",
    response_model=SecondMarriageResponse,
    summary="Evaluate Second Marriage & Plurality per KP Reader 4 Chapters 24, 25, 52",
    description="Evaluates dual signs, Mercury on 7th CSL, 2nd CSL support, and Venus-Uranus / Moon-Venus plurality aspects.",
)
def evaluate_second_marriage(request: SecondMarriageRequest) -> SecondMarriageResponse:
    res = evaluate_second_marriage_reader4(
        seventh_csl_planet=request.seventh_csl_planet,
        seventh_csl_sign=request.seventh_csl_sign,
        seventh_csl_signifies=request.seventh_csl_signifies,
        second_csl_signifies=request.second_csl_signifies,
        is_venus_uranus_hard_aspect=request.is_venus_uranus_hard_aspect,
        is_moon_venus_hard_aspect=request.is_moon_venus_hard_aspect,
        is_rahu_in_7th=request.is_rahu_in_7th,
    )
    return SecondMarriageResponse(
        is_second_marriage_indicated=res.is_second_marriage_indicated,
        plurality_of_relationships=res.plurality_of_relationships,
        seventh_csl_in_dual_sign=res.seventh_csl_in_dual_sign,
        seventh_csl_is_mercury=res.seventh_csl_is_mercury,
        second_cusp_sub_lord_support=res.second_cusp_sub_lord_support,
        reasons=res.reasons,
        guidance=res.guidance,
    )


@router.post(
    "/kp/reader4/progeny-promise",
    response_model=ProgenyPromiseResponse,
    summary="Evaluate Progeny Promise, Fruitful vs Barren signs & Adoption per KP Reader 4",
    description="Evaluates 5th Cusp Sub-Lord for fruitful/barren signs, significations of 2, 5, 11 vs 4, 10, twins, and adoption.",
)
def evaluate_progeny(request: ProgenyPromiseRequest) -> ProgenyPromiseResponse:
    res = evaluate_progeny_reader4(
        fifth_csl_planet=request.fifth_csl_planet,
        fifth_csl_sign=request.fifth_csl_sign,
        fifth_csl_signifies=request.fifth_csl_signifies,
        is_mercury_or_jupiter_in_dual_sign=request.is_mercury_or_jupiter_in_dual_sign,
        is_saturn_connected_to_8_12=request.is_saturn_connected_to_8_12,
    )
    return ProgenyPromiseResponse(
        childbirth_promised=res.childbirth_promised,
        fertility_status=res.fertility_status,
        fifth_csl_planet=res.fifth_csl_planet,
        fifth_csl_sign=res.fifth_csl_sign,
        fifth_csl_signifies=res.fifth_csl_signifies,
        supporting_houses=res.supporting_houses,
        denying_houses=res.denying_houses,
        twin_birth_indicated=res.twin_birth_indicated,
        adoption_indicated=res.adoption_indicated,
        progeny_timing_advice=res.progeny_timing_advice,
        clive_fallacy_counsel=res.clive_fallacy_counsel,
    )


@router.post(
    "/kp/reader4/kasyapa-seventh-star",
    response_model=KasyapaSeventhStarResponse,
    summary="Evaluate Sage Kasyapa's 7th Star (Vatham) findings per KP Reader 4 Chapter 6",
    description="Evaluates empirical findings of Sage Kasyapa for 7th star pairs (Punarvasu-Hasta, Rohini-Magha, Revati-Arudra, etc.).",
)
def evaluate_kasyapa_seventh_star_endpoint(
    request: KasyapaSeventhStarRequest,
) -> KasyapaSeventhStarResponse:
    res = evaluate_kasyapa_seventh_star(
        bride_star=request.bride_star,
        groom_star=request.groom_star,
    )
    return KasyapaSeventhStarResponse(
        bride_star=res.bride_star,
        groom_star=res.groom_star,
        is_seventh_star=res.is_seventh_star,
        kasyapa_verdict=res.kasyapa_verdict,
        predicted_experience=res.predicted_experience,
        shastric_details=res.shastric_details,
    )

