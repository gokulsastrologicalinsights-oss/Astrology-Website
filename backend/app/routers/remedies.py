"""Remedies & Pariharam Router.

Clean-room, Shastra-validated endpoints for:
- 39 Classical Problem Taxonomy categories (Bilingual English/Tamil)
- Authentic Remedy Catalog (Devanagari Sanskrit mantras, Tamil transliteration, Daan, Fasting)
- 9 Kaveri Delta Navagraha Sthalams (Geographic coordinates, deities, offerings)
- Canonical Shastra citations (BPHS, Phaladeepika, Lal Kitab)
- Content validation and Unicode fidelity auditing
- Vedic Astrological Eligibility safeguards (Yogakaraka protection, Daan restrictions)
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.remedies import (
    ProblemTaxonomyListResponse,
    ProblemTaxonomyItem,
    RemedyListResponse,
    RemedyItem,
    NavagrahaTempleListResponse,
    NavagrahaTempleItem,
    SourceReferenceResponse,
    ContentValidationReport,
    RemedyEligibilityRequest,
    RemedyEligibilityResponse,
    RemedyAnalysisResponse,
    LiveRemedyAnalysisRequest,
    SaveRemedyReportRequest,
    SavedRemedyReportResponse,
    SavedRemedyReportsListResponse,
    PilgrimageCircuitResponse,
    PersonalizedPilgrimageRequest,
    GemstoneAdvisoryResponse,
    GemstoneAdvisoryRequest,
    RudrakshaCatalogResponse,
    RudrakshaRecommendationRequest,
    RudrakshaRecommendationSummary,
)
from app.services.remedy_engine.repository import remedy_repository
from app.services.remedy_engine.validation import RemedyValidator
from app.services.remedy_engine.eligibility import RemedyEligibilityEngine
from app.services.remedy_engine.analysis import generate_remedy_analysis
from app.services.remedy_engine.pilgrimage import PilgrimageCircuitEngine
from app.services.remedy_engine.gemstone_advisory import GemstoneAdvisoryEngine
from app.services.remedy_engine.rudraksha_advisory import RudrakshaAdvisoryEngine
from datetime import date
from app.services.auth_service import get_current_user, get_supabase_client
from app.services.ephemeris import calculate_full_horoscope
from app.services.dasa_service import calculate_dasa
from app.schemas.common import BirthInput

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/remedies", tags=["Remedies & Pariharam"])


def _validate_uuid(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns its canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format.",
        )


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



# ------------------------------------------------------------------------------
# 1. Problem Taxonomy Endpoints
# ------------------------------------------------------------------------------

@router.get("/taxonomy", response_model=ProblemTaxonomyListResponse, summary="Get Verified Problem Taxonomy")
async def get_problem_taxonomy(
    category: Optional[str] = Query(None, description="Filter by problem category, e.g. 'career', 'health_wellness'")
) -> ProblemTaxonomyListResponse:
    """Returns verified problem taxonomy entries with primary karakas, governing houses, and bilingual descriptions."""
    items = await remedy_repository.get_all_problem_taxonomies(category=category)
    categories = sorted(list({item["category"] for item in items}))
    return ProblemTaxonomyListResponse(
        total_count=len(items),
        categories=categories,
        items=[ProblemTaxonomyItem(**item) for item in items],
    )


# ------------------------------------------------------------------------------
# 2. Remedy Catalog Endpoints
# ------------------------------------------------------------------------------

@router.get("/catalog", response_model=RemedyListResponse, summary="Get Filtered Remedy Catalog")
async def get_remedy_catalog(
    graha: Optional[str] = Query(None, description="Filter by Navagraha: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu, universal"),
    remedy_type: Optional[str] = Query(None, description="Filter by remedy type: mantra, worship, charity, fasting, temple"),
    problem_slug: Optional[str] = Query(None, description="Filter by associated problem slug, e.g. 'career_delay'"),
) -> RemedyListResponse:
    """Returns verified remedies filtered by graha, type, or problem category."""
    items = await remedy_repository.get_all_remedies(
        graha=graha,
        remedy_type=remedy_type,
        problem_slug=problem_slug,
    )
    return RemedyListResponse(
        total_count=len(items),
        items=[RemedyItem(**item) for item in items],
    )


@router.get("/catalog/{code}", response_model=RemedyItem, summary="Get Remedy Detail by Code")
async def get_remedy_detail(code: str) -> RemedyItem:
    """Returns a single remedy by its unique code."""
    remedy = await remedy_repository.get_remedy_by_code(code)
    if not remedy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remedy with code '{code}' not found.",
        )
    return RemedyItem(**remedy)


# ------------------------------------------------------------------------------
# 3. Navagraha Temples Endpoints
# ------------------------------------------------------------------------------

@router.get("/temples", response_model=NavagrahaTempleListResponse, summary="Get Tamil Navagraha Temples")
async def get_navagraha_temples(
    graha: Optional[str] = Query(None, description="Filter by Navagraha planet: sun, moon, mars, etc.")
) -> NavagrahaTempleListResponse:
    """Returns authentic Kaveri Delta Navagraha Temples with coordinates, deities, and offerings."""
    temples = await remedy_repository.get_all_navagraha_temples(graha=graha)
    return NavagrahaTempleListResponse(
        total_count=len(temples),
        items=[NavagrahaTempleItem(**t) for t in temples],
    )


@router.get("/temples/{code}", response_model=NavagrahaTempleItem, summary="Get Navagraha Temple Detail")
async def get_temple_detail(code: str) -> NavagrahaTempleItem:
    """Returns a single Navagraha temple by its unique code."""
    temple = await remedy_repository.get_temple_by_code(code)
    if not temple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Temple with code '{code}' not found.",
        )
    return NavagrahaTempleItem(**temple)


# ------------------------------------------------------------------------------
# 4. Canonical Sources Endpoint
# ------------------------------------------------------------------------------

@router.get("/sources", response_model=List[SourceReferenceResponse], summary="Get Classical Shastra Sources")
async def get_classical_sources() -> List[SourceReferenceResponse]:
    """Returns canonical reference texts cited across the remedies module."""
    sources = await remedy_repository.get_all_source_references()
    return [SourceReferenceResponse(**s) for s in sources]


# ------------------------------------------------------------------------------
# 5. Content Validation & Audit Endpoint
# ------------------------------------------------------------------------------

@router.post("/validate-content", response_model=ContentValidationReport, summary="Audit Remedy Knowledge Base")
async def audit_content() -> ContentValidationReport:
    """Audits the remedy knowledge base for bilingual completeness, Devanagari Sanskrit fidelity, and Shastra citations."""
    return await RemedyValidator.audit_knowledge_base()


# ------------------------------------------------------------------------------
# 6. Vedic Astrological Eligibility Safeguard Endpoint
# ------------------------------------------------------------------------------

@router.post("/eligibility-check", response_model=RemedyEligibilityResponse, summary="Check Astrological Remedy Eligibility")
async def check_remedy_eligibility(request: RemedyEligibilityRequest) -> RemedyEligibilityResponse:
    """Evaluates remedy suitability against classical BPHS rules (e.g. Yogakaraka protection against Daan/charity)."""
    return RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign=request.ascendant_sign,
        graha=request.graha,
        remedy_type=request.remedy_type,
    )


# ------------------------------------------------------------------------------
# 7. Chart Analysis Endpoints (Saved & Live)
# ------------------------------------------------------------------------------

@router.get(
    "/analysis/saved/{horoscope_id}",
    response_model=RemedyAnalysisResponse,
    summary="Get Personalized Remedies for Saved Horoscope",
)
async def get_saved_horoscope_remedy_analysis(
    horoscope_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RemedyAnalysisResponse:
    """Consumes saved horoscope calculation output and performs rule-based diagnostic analysis without recalculating positions."""
    clean_id = _validate_uuid(horoscope_id)
    is_admin = current_user.get("role") == "admin"
    supabase = get_supabase_client()

    horoscope_row: Optional[Dict[str, Any]] = None
    if supabase:
        try:
            resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
            if resp.data and len(resp.data) > 0:
                row = resp.data[0]
                if is_admin or str(row.get("user_id")) == str(current_user["id"]):
                    horoscope_row = row
        except Exception as err:
            logger.warning(f"Database error fetching saved horoscope {clean_id}: {err}")

    if not horoscope_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved horoscope not found or unauthorized.",
        )

    calc_result = horoscope_row.get("calculation_result") or {}
    chart_data = calc_result.get("horoscope")

    # If chart_data is not in snapshot, recompute using existing engine
    if not chart_data or not isinstance(chart_data, dict):
        computed = calculate_full_horoscope(
            birth_date=horoscope_row["birth_date"],
            birth_time=horoscope_row["birth_time"],
            timezone_str=horoscope_row["timezone"],
            latitude=horoscope_row["latitude"],
            longitude=horoscope_row["longitude"],
            ayanamsa_id=horoscope_row.get("ayanamsa_id", 0),
            house_system_id=horoscope_row.get("house_system_id", 0),
        )
        chart_data = computed.model_dump()

    # Dasa data
    dasa_data = calc_result.get("dasa")
    if not dasa_data or not isinstance(dasa_data, dict):
        try:
            b_in = BirthInput(
                birth_date=horoscope_row["birth_date"],
                birth_time=horoscope_row["birth_time"],
                timezone=horoscope_row["timezone"],
                latitude=horoscope_row["latitude"],
                longitude=horoscope_row["longitude"],
            )
            computed_dasa = calculate_dasa(b_in, target_date=date.today())
            dasa_data = computed_dasa.model_dump()
        except Exception:
            dasa_data = None

    client_inputs = {
        "birth_date": horoscope_row.get("birth_date"),
        "birth_time": horoscope_row.get("birth_time"),
        "timezone": horoscope_row.get("timezone"),
        "latitude": horoscope_row.get("latitude"),
        "longitude": horoscope_row.get("longitude"),
        "ayanamsa_id": horoscope_row.get("ayanamsa_id"),
    }

    return await generate_remedy_analysis(
        chart_data=chart_data,
        horoscope_id=clean_id,
        person_name=horoscope_row.get("person_name") or "Saved Horoscope",
        birth_date=horoscope_row.get("birth_date"),
        birth_time=horoscope_row.get("birth_time"),
        dasa_data=dasa_data,
        client_inputs=client_inputs,
    )


@router.post(
    "/analysis/live",
    response_model=RemedyAnalysisResponse,
    summary="Get Personalized Remedies for Live/Ad-hoc Chart",
)
async def get_live_remedy_analysis(
    request: LiveRemedyAnalysisRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> RemedyAnalysisResponse:
    """Generates remedy analysis for active live birth inputs or existing calculation snapshot."""
    chart_data: Optional[Dict[str, Any]] = None
    dasa_data: Optional[Dict[str, Any]] = None
    client_inputs: Dict[str, Any] = {}

    if request.chart_snapshot:
        chart_data = request.chart_snapshot.get("horoscope") or request.chart_snapshot
        dasa_data = request.chart_snapshot.get("dasa")
        client_inputs = request.chart_snapshot.get("clientInputs") or {}
    elif request.birth_date and request.birth_time and request.latitude is not None and request.longitude is not None:
        computed = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa or 0,
        )
        chart_data = computed.model_dump()
        try:
            b_in = BirthInput(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                timezone=request.timezone or "Asia/Kolkata",
                latitude=request.latitude,
                longitude=request.longitude,
            )
            computed_dasa = calculate_dasa(b_in, target_date=date.today())
            dasa_data = computed_dasa.model_dump()
        except Exception:
            dasa_data = None
        client_inputs = {
            "birth_date": request.birth_date,
            "birth_time": request.birth_time,
            "timezone": request.timezone,
            "latitude": request.latitude,
            "longitude": request.longitude,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either valid chart_snapshot or complete birth coordinates are required.",
        )

    return await generate_remedy_analysis(
        chart_data=chart_data,
        horoscope_id=None,
        person_name="Live Birth Chart",
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        dasa_data=dasa_data,
        client_inputs=client_inputs,
    )


# ------------------------------------------------------------------------------
# 8. Astrologer-Reviewed Reports Endpoints
# ------------------------------------------------------------------------------

@router.post(
    "/reports",
    response_model=SavedRemedyReportResponse,
    summary="Save Astrologer-Reviewed Remedy Report",
)
async def save_remedy_report_endpoint(
    payload: SaveRemedyReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedRemedyReportResponse:
    """Persists an astrologer-reviewed remedy report with strict ownership validation."""
    clean_horoscope_id = _validate_uuid(payload.horoscope_id)
    user_id = str(current_user["id"])
    is_admin = current_user.get("role") == "admin"

    # Verify ownership of target horoscope
    supabase = get_supabase_client()
    if supabase:
        try:
            resp = supabase.table("saved_horoscopes").select("user_id, person_name").eq("id", clean_horoscope_id).execute()
            if resp.data and len(resp.data) > 0:
                horo_owner = str(resp.data[0].get("user_id"))
                if not is_admin and horo_owner != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have permission to attach remedy reports to this horoscope.",
                    )
        except HTTPException:
            raise
        except Exception as err:
            logger.warning(f"Error checking horoscope ownership: {err}")

    record = await remedy_repository.save_report(
        user_id=user_id,
        horoscope_id=clean_horoscope_id,
        input_data_fingerprint=payload.input_data_fingerprint,
        analysis_snapshot=payload.analysis_snapshot.model_dump(),
        review_status=payload.review_status,
        astrologer_notes=payload.astrologer_notes,
        selected_remedy_codes=payload.selected_remedy_codes,
        language=payload.language,
        person_name=payload.person_name,
    )

    return SavedRemedyReportResponse(**record)


@router.get(
    "/reports/{report_id}",
    response_model=SavedRemedyReportResponse,
    summary="Get Saved Remedy Report by ID",
)
async def get_remedy_report_endpoint(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedRemedyReportResponse:
    """Retrieves a saved remedy report with server-side ownership enforcement."""
    clean_id = _validate_uuid(report_id)
    is_admin = current_user.get("role") == "admin"
    user_id = str(current_user["id"])

    report = await remedy_repository.get_report_by_id(clean_id, user_id=user_id, is_admin=is_admin)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remedy report not found or unauthorized.",
        )
    return SavedRemedyReportResponse(**report)


@router.get(
    "/reports/by-horoscope/{horoscope_id}",
    response_model=SavedRemedyReportsListResponse,
    summary="List Saved Remedy Reports for Horoscope",
)
async def list_reports_for_horoscope(
    horoscope_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedRemedyReportsListResponse:
    """Lists all saved remedy reports attached to a specific horoscope."""
    clean_id = _validate_uuid(horoscope_id)
    is_admin = current_user.get("role") == "admin"
    user_id = str(current_user["id"])

    # Verify target horoscope exists and belongs to current user (or user is admin)
    supabase = get_supabase_client()
    if supabase and not is_admin:
        try:
            resp = supabase.table("saved_horoscopes").select("user_id").eq("id", clean_id).execute()
            if resp.data and len(resp.data) > 0:
                horo_owner = str(resp.data[0].get("user_id"))
                if horo_owner != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Saved horoscope not found or unauthorized.",
                    )
        except HTTPException:
            raise
        except Exception as err:
            logger.warning(f"Error checking horoscope ownership in list_reports: {err}")

    reports = await remedy_repository.list_reports(user_id=user_id, horoscope_id=clean_id, is_admin=is_admin)
    return SavedRemedyReportsListResponse(
        total_count=len(reports),
        reports=[SavedRemedyReportResponse(**r) for r in reports],
    )


# ------------------------------------------------------------------------------
# 8. Kaveri Delta Navagraha Pilgrimage Circuit Endpoints
# ------------------------------------------------------------------------------

@router.get(
    "/pilgrimage/circuits",
    response_model=List[PilgrimageCircuitResponse],
    summary="Get Standard Navagraha Pilgrimage Circuits",
)
async def get_pilgrimage_circuits() -> List[PilgrimageCircuitResponse]:
    """Returns classical 1-Day Express and 2-Day Comprehensive Navagraha pilgrimage circuits."""
    return PilgrimageCircuitEngine.get_standard_circuits()


@router.post(
    "/pilgrimage/personalized",
    response_model=PilgrimageCircuitResponse,
    summary="Get Chart-Aware Prioritized Pilgrimage Circuit",
)
async def get_personalized_pilgrimage_circuit(
    request: PersonalizedPilgrimageRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> PilgrimageCircuitResponse:
    """Evaluates native's chart afflictions, Dasha periods, and Doshas to prioritize specific sthalams."""
    chart_context: Dict[str, Any] = {}

    # Case 1: Provided snapshot
    if request.chart_snapshot and isinstance(request.chart_snapshot, dict):
        chart_data = request.chart_snapshot.get("horoscope") or request.chart_snapshot
        chart_context["running_mahadasha"] = request.chart_snapshot.get("running_mahadasha")
        chart_context["running_bhukti"] = request.chart_snapshot.get("running_bhukti")
    # Case 2: Saved horoscope ID
    elif request.horoscope_id:
        clean_id = _validate_uuid(request.horoscope_id)
        supabase = get_supabase_client()
        row = None
        if supabase:
            try:
                resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
                if resp.data:
                    row = resp.data[0]
            except Exception as err:
                logger.warning(f"Error fetching horoscope {clean_id}: {err}")
        if row:
            calc_res = row.get("calculation_result") or {}
            chart_data = calc_res.get("horoscope")
            dasa_res = calc_res.get("dasa") or {}
            if dasa_res.get("current_dasa"):
                chart_context["running_mahadasha"] = dasa_res["current_dasa"].get("lord")
                chart_context["running_bhukti"] = dasa_res["current_dasa"].get("bhukti_lord")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Horoscope {clean_id} not found.",
            )
    # Case 3: Live birth inputs
    elif request.birth_date and request.birth_time and request.latitude is not None and request.longitude is not None:
        computed = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa or 0,
        )
        chart_data = computed.model_dump()
        try:
            b_in = BirthInput(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                timezone=request.timezone or "Asia/Kolkata",
                latitude=request.latitude,
                longitude=request.longitude,
            )
            d_res = calculate_dasa(b_in, target_date=date.today())
            d_dict = d_res.model_dump()
            if d_dict.get("current_dasa"):
                chart_context["running_mahadasha"] = d_dict["current_dasa"].get("lord")
                chart_context["running_bhukti"] = d_dict["current_dasa"].get("bhukti_lord")
        except Exception:
            pass
    else:
        # Fall back to standard circuit without chart priorities
        return (
            PilgrimageCircuitEngine.build_1_day_express_circuit()
            if request.circuit_type == "1_day_express"
            else PilgrimageCircuitEngine.build_2_day_comprehensive_circuit()
        )

    # Extract planets context for priority resolution
    planets_list = chart_data.get("planets", [])
    debilitated = []
    combust = []
    for p in planets_list:
        p_name = (p.get("name") or "").lower()
        if p.get("is_debilitated"):
            debilitated.append(p_name)
        if p.get("is_combust"):
            combust.append(p_name)
    chart_context["debilitated_planets"] = debilitated
    chart_context["combust_planets"] = combust

    # Kuja Dosha
    doshas = chart_data.get("doshas") or {}
    if doshas.get("manglik") or doshas.get("kuja_dosha"):
        chart_context["kuja_dosha_status"] = "present"

    return PilgrimageCircuitEngine.generate_personalized_circuit(
        chart_context=chart_context,
        circuit_type=request.circuit_type,
    )


# ------------------------------------------------------------------------------
# 9. Astrological Gemstone (Ratna) Advisory & Safety Endpoints
# ------------------------------------------------------------------------------

@router.post(
    "/gemstones/advisory",
    response_model=GemstoneAdvisoryResponse,
    summary="Get Astrological Gemstone Prescription & Safety Audit",
)
async def get_gemstone_advisory(
    request: GemstoneAdvisoryRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> GemstoneAdvisoryResponse:
    """Evaluates 3-pillar gemstone recommendations (Life, Lucky, Fortune), secondary support, and classical Dusthana prohibitions."""
    lagna_sign = request.ascendant_sign
    moon_sign: Optional[str] = None
    mahadasha: Optional[str] = None
    bhukti: Optional[str] = None
    debilitated: List[str] = []
    combust: List[str] = []
    has_kuja = False
    has_sade = False
    has_kaal = False

    if not lagna_sign and request.horoscope_id:
        clean_id = _validate_uuid(request.horoscope_id)
        supabase = get_supabase_client()
        row = None
        if supabase:
            try:
                resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
                if resp.data:
                    row = resp.data[0]
            except Exception as err:
                logger.warning(f"Error fetching horoscope {clean_id}: {err}")
        if row:
            calc_res = row.get("calculation_result") or {}
            horo = calc_res.get("horoscope") or {}
            asc_info = horo.get("ascendant", {})
            lagna_sign = asc_info.get("sign") or row.get("ascendant_sign")
            moon_info = next((p for p in horo.get("planets", []) if p.get("name") == "Moon"), {})
            moon_sign = moon_info.get("sign")
            dasa_res = calc_res.get("dasa") or {}
            if dasa_res.get("current_dasa"):
                mahadasha = dasa_res["current_dasa"].get("lord")
                bhukti = dasa_res["current_dasa"].get("bhukti_lord")
            for p in horo.get("planets", []):
                p_n = (p.get("name") or "").lower()
                if p.get("is_debilitated"):
                    debilitated.append(p_n)
                if p.get("is_combust"):
                    combust.append(p_n)
            doshas = horo.get("doshas") or {}
            if doshas.get("manglik") or doshas.get("kuja_dosha"):
                has_kuja = True
            if doshas.get("kaal_sarp") or doshas.get("kala_sarpa"):
                has_kaal = True
            if doshas.get("sade_sati"):
                has_sade = True
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Horoscope {clean_id} not found.",
            )

    if not lagna_sign and request.birth_date and request.birth_time and request.latitude is not None and request.longitude is not None:
        computed = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone or "Asia/Kolkata",
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa or 0,
        )
        lagna_sign = computed.ascendant.sign_name
        moon_obj = next((p for p in computed.planets if p.name == "Moon"), None)
        moon_sign = moon_obj.sign_name if moon_obj else None
        for p in computed.planets:
            p_n = (p.name or "").lower()
            if getattr(p, "is_debilitated", False):
                debilitated.append(p_n)
            if getattr(p, "is_combust", False):
                combust.append(p_n)
        try:
            b_in = BirthInput(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                timezone=request.timezone or "Asia/Kolkata",
                latitude=request.latitude,
                longitude=request.longitude,
            )
            d_res = calculate_dasa(b_in, target_date=date.today())
            d_dict = d_res.model_dump()
            if d_dict.get("current_dasa"):
                mahadasha = d_dict["current_dasa"].get("lord")
                bhukti = d_dict["current_dasa"].get("bhukti_lord")
        except Exception:
            pass

    if not lagna_sign:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ascendant sign (Lagna) is required to calculate gemstone advisory.",
        )

    # Normalize lagna sign
    lagna_clean = lagna_sign.strip().capitalize()
    valid_lagnas = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    if lagna_clean not in valid_lagnas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ascendant sign: '{lagna_sign}'. Must be one of Aries through Pisces.",
        )

    return GemstoneAdvisoryEngine.evaluate_advisory(
        lagna_sign=lagna_clean,
        moon_sign=moon_sign,
        running_mahadasha=mahadasha,
        running_bhukti=bhukti,
        body_weight_kg=request.body_weight_kg,
        debilitated_planets=debilitated,
        combust_planets=combust,
        has_kuja_dosha=has_kuja,
        has_sade_sati=has_sade,
        has_kaal_sarp=has_kaal,
    )


# ------------------------------------------------------------------------------
# 10. Rudraksha Shastra & Compatibility Endpoints
# ------------------------------------------------------------------------------

@router.get(
    "/rudraksha/matrix",
    response_model=RudrakshaCatalogResponse,
    summary="Get 1-to-14 Mukhi Rudraksha Catalogue",
)
async def get_rudraksha_matrix() -> RudrakshaCatalogResponse:
    """Returns the complete classical 1-to-14 Mukhi Rudraksha catalogue along with Gauri Shankar and Ganesh beads."""
    beads = RudrakshaAdvisoryEngine.get_all_beads()
    return RudrakshaCatalogResponse(
        total_beads=len(beads),
        items=beads,
    )


@router.post(
    "/rudraksha/recommendation",
    response_model=RudrakshaRecommendationSummary,
    summary="Get Personalized Rudraksha Prescription",
)
async def get_rudraksha_recommendation(
    request: RudrakshaRecommendationRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> RudrakshaRecommendationSummary:
    """Evaluates planetary afflictions, Dasha periods, and Lagna to prescribe primary, secondary, and universal beads."""
    lagna_sign = request.ascendant_sign or "Aries"
    lagna_clean = lagna_sign.strip().capitalize()

    return RudrakshaAdvisoryEngine.evaluate_rudraksha(
        lagna_sign=lagna_clean,
        moon_sign=request.moon_sign,
        running_mahadasha=request.running_mahadasha,
        running_bhukti=request.running_bhukti,
        debilitated_planets=request.debilitated_planets,
        combust_planets=request.combust_planets,
        has_kuja_dosha=request.has_kuja_dosha,
        has_sade_sati=request.has_sade_sati,
        has_kaal_sarp=request.has_kaal_sarp,
    )



