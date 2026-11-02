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
    analyze_saved_chart_nakshatras,
)
from app.services.auth_service import get_supabase_client
from app.services.ephemeris import calculate_full_horoscope

router = APIRouter(prefix="/api/v1/nakshatras", tags=["Nakshatra Shastra"])


class ChartAnalysisRequest(BaseModel):
    horoscope_data: Optional[Dict[str, Any]] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = "Asia/Kolkata"
    ayanamsa: Optional[int] = 0
    saved_horoscope_id: Optional[str] = None


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


@router.post("/chart-analysis", response_model=Dict[str, Any])
def analyze_chart_nakshatras_endpoint(req: ChartAnalysisRequest) -> Dict[str, Any]:
    """Perform in-depth empirical Nakshatra analysis based on Saptarishis research for a chart."""
    horo_data = req.horoscope_data
    b_date = req.birth_date

    # Case A: Saved horoscope ID provided
    if req.saved_horoscope_id:
        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("saved_horoscopes").select("*").eq("id", req.saved_horoscope_id.strip()).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    b_date = b_date or row.get("birth_date")
                    calc_res = row.get("calculation_result") or {}
                    # Check if already cached
                    if "natchathira_analysis" in calc_res and calc_res["natchathira_analysis"]:
                        return calc_res["natchathira_analysis"]
                    horo_data = calc_res.get("horoscope")
                    if not horo_data and row.get("birth_date") and row.get("birth_time"):
                        computed = calculate_full_horoscope(
                            birth_date=row["birth_date"],
                            birth_time=row["birth_time"],
                            latitude=float(row.get("latitude") or 13.0827),
                            longitude=float(row.get("longitude") or 80.2707),
                            timezone=row.get("timezone") or "Asia/Kolkata",
                            ayanamsa_id=int(row.get("ayanamsa_id") or 0),
                        )
                        horo_data = computed.model_dump()
            except Exception as e:
                print(f"[Nakshatra Analysis] Saved horoscope fetch error: {e}")

    # Case B: Ad-hoc birth parameters provided without pre-computed horoscope
    if not horo_data and req.birth_date and req.birth_time and req.latitude is not None and req.longitude is not None:
        computed = calculate_full_horoscope(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            latitude=req.latitude,
            longitude=req.longitude,
            timezone=req.timezone or "Asia/Kolkata",
            ayanamsa_id=req.ayanamsa or 0,
        )
        horo_data = computed.model_dump()

    if not horo_data:
        raise HTTPException(
            status_code=422,
            detail="Must provide either horoscope_data, saved_horoscope_id, or complete birth details.",
        )

    return analyze_saved_chart_nakshatras(horo_data, birth_date_str=b_date)


@router.get("/saved-analysis/{horoscope_id}", response_model=Dict[str, Any])
def get_saved_horoscope_nakshatra_analysis(horoscope_id: str) -> Dict[str, Any]:
    """Retrieve or compute in-depth Nakshatra analysis for any saved horoscope."""
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=503, detail="Database client unavailable.")

    clean_id = horoscope_id.strip()
    try:
        res = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=404, detail="Saved horoscope not found.")
        row = res.data[0]
        calc_res = row.get("calculation_result") or {}

        # If already stored, return it
        if "natchathira_analysis" in calc_res and calc_res["natchathira_analysis"]:
            return calc_res["natchathira_analysis"]

        horo_data = calc_res.get("horoscope")
        if not horo_data:
            computed = calculate_full_horoscope(
                birth_date=row["birth_date"],
                birth_time=row["birth_time"],
                latitude=float(row.get("latitude") or 13.0827),
                longitude=float(row.get("longitude") or 80.2707),
                timezone=row.get("timezone") or "Asia/Kolkata",
                ayanamsa_id=int(row.get("ayanamsa_id") or 0),
            )
            horo_data = computed.model_dump()

        analysis = analyze_saved_chart_nakshatras(horo_data, birth_date_str=row.get("birth_date"))
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze saved horoscope: {str(e)}")
