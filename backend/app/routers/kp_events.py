"""KP Event Prediction Engine - API Router.

Exposes endpoints for calculating rule-based KP event predictions across
Dasha-Bhukti periods, analyzing saved horoscopes, and retrieving event definitions.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.kp_events import (
    KpEventAnalysisRequest,
    KpEventAnalysisResponse,
    SavedHoroscopeAnalysisRequest,
)
from app.schemas.common import BirthInput
from app.schemas.horoscope import HoroscopeRequest
from app.services.auth_service import get_current_user, get_supabase_client
from app.services.kp_service import calculate_kp_chart
from app.services.ephemeris import calculate_full_horoscope
from app.services.dasa_service import _convert_node
from app.services.timezone_utils import resolve_birth_datetime
import xalen

from app.services.kp_event_engine import (
    run_kp_event_analysis,
    extract_periods_from_dasa_response,
    list_all_events,
    get_event_rule,
    save_kp_event_analysis,
    get_kp_event_analysis,
    delete_kp_event_analysis,
    derive_cusp_sub_lords_from_chart,
    extract_retrograde_status_from_chart,
    derive_planet_house_significations,
    RULE_SET_VERSION,
)

security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/horoscope/kp-events", tags=["KP Event Analysis"])


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


# 1. Direct Analysis Endpoint (conforms strictly to Section 4 & 10)
@router.post("/analyze", response_model=KpEventAnalysisResponse, summary="Analyze KP events for given periods & significations")
def analyze_kp_events(
    request: KpEventAnalysisRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> KpEventAnalysisResponse:
    """Evaluates periods against 32 KP event rules and returns color-coded predictions."""
    try:
        raw_periods = [p.model_dump() for p in request.periods]
        res = run_kp_event_analysis(
            lagna=request.lagna,
            periods=raw_periods,
            significations=request.significations,
            csl_significations=request.csl_significations,
            retrograde_status=request.retrograde_status,
            current_date=request.current_date,
            timezone_str=request.timezone or "Asia/Kolkata",
            filter_category=request.filter_category,
            filter_grade=request.filter_grade,
            filter_event=request.filter_event,
            running_only=bool(request.running_only),
        )

        # If user is authenticated and save_horoscope_id is provided, persist analysis
        if current_user and request.save_horoscope_id:
            save_kp_event_analysis(
                user_id=current_user["id"],
                horoscope_id=request.save_horoscope_id,
                analysis_data=res,
            )

        return KpEventAnalysisResponse(**res)
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"KP event analysis failed: {str(exc)}",
        )


# 2. Workflow A: Analyze Saved Horoscope
@router.post("/from-saved/{saved_horoscope_id}", response_model=KpEventAnalysisResponse, summary="Workflow A: Analyze a saved horoscope")
def analyze_saved_horoscope(
    saved_horoscope_id: str,
    filter_params: SavedHoroscopeAnalysisRequest = SavedHoroscopeAnalysisRequest(),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> KpEventAnalysisResponse:
    """Retrieves saved horoscope, computes KP significations & Dasha schedule, and calculates event predictions."""
    user_id = current_user["id"]
    is_admin = current_user.get("role") == "admin"
    supabase = get_supabase_client()

    horoscope_row: Optional[Dict[str, Any]] = None
    if supabase:
        try:
            q = supabase.table("saved_horoscopes").select("*").eq("id", saved_horoscope_id)
            if not is_admin:
                q = q.eq("user_id", user_id)
            resp = q.execute()
            if resp.data and len(resp.data) > 0:
                horoscope_row = resp.data[0]
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Database query error: {str(err)}")

    if not horoscope_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved horoscope not found or unauthorized.",
        )

    # Check if analysis was previously calculated and user did not request regeneration
    if not filter_params.regenerate:
        existing = get_kp_event_analysis(user_id, saved_horoscope_id, is_admin=is_admin)
        if existing and existing.get("results"):
            # Invalidation Check 1: Invalidate if rule-set version changed
            version_match = (existing.get("rule_set_version") == RULE_SET_VERSION)

            # Invalidation Check 2: Invalidate if saved horoscope was updated after the analysis
            horo_updated = horoscope_row.get("updated_at")
            calc_time = existing.get("calculation_timestamp") or existing.get("created_at")
            data_fresh = True
            if horo_updated and calc_time:
                try:
                    data_fresh = (str(horo_updated) <= str(calc_time))
                except Exception:
                    data_fresh = True

            # Invalidation Check 3: If user passed active filters, recompute or filter so results match
            has_active_filters = bool(
                filter_params.filter_category
                or filter_params.filter_grade
                or filter_params.filter_event
                or filter_params.running_only
            )

            if version_match and data_fresh and not has_active_filters:
                summary = existing.get("summary", {})
                periods = existing.get("results", [])
                report = summary.get("human_readable_report") or "Retrieved from saved analysis."
                return KpEventAnalysisResponse(
                    rule_set_version=existing.get("rule_set_version", RULE_SET_VERSION),
                    lagna=horoscope_row.get("calculation_result", {}).get("horoscope", {}).get("ascendant", {}).get("sign_name"),
                    current_date=existing.get("calculation_timestamp", "").split("T")[0] if existing.get("calculation_timestamp") else "2026-10-18",
                    timezone=horoscope_row.get("timezone", "Asia/Kolkata"),
                    overall_summary={
                        "rule_set_version": existing.get("rule_set_version", RULE_SET_VERSION),
                        "total_periods": len(periods),
                        "running_period": summary.get("running_period"),
                        "green_count": summary.get("green_count", 0),
                        "orange_count": summary.get("orange_count", 0),
                        "red_count": summary.get("red_count", 0),
                    },
                    periods=periods,
                    human_readable_report=report,
                )

    calc_result = horoscope_row.get("calculation_result") or {}
    horo_part = calc_result.get("horoscope")
    kp_part = calc_result.get("kp")
    dasa_part = calc_result.get("dasa")

    # If KP or Dasa calculation is missing from snapshot, recompute using existing engine
    b_date = horoscope_row["birth_date"]
    b_time = horoscope_row["birth_time"]
    tz_str = horoscope_row["timezone"]
    lat = horoscope_row["latitude"]
    lon = horoscope_row["longitude"]
    ayan_id = horoscope_row.get("ayanamsa_id", 1)
    hsys_id = horoscope_row.get("house_system_id", 2)

    birth_input = BirthInput(
        birth_date=b_date,
        birth_time=b_time,
        timezone=tz_str,
        latitude=lat,
        longitude=lon,
    )

    if not kp_part:
        kp_res = calculate_kp_chart(birth_input, ayanamsa_id=ayan_id, house_system_id=hsys_id)
        kp_part = kp_res.model_dump()

    if not horo_part:
        horo_res = calculate_full_horoscope(
            birth_date=b_date,
            birth_time=b_time,
            timezone_str=tz_str,
            latitude=lat,
            longitude=lon,
            ayanamsa_id=ayan_id,
            house_system_id=hsys_id,
        )
        horo_part = horo_res.model_dump()

    # Extract Dasha periods
    periods_list: List[Dict[str, Any]] = []
    if dasa_part and dasa_part.get("dasa_tree"):
        periods_list = extract_periods_from_dasa_response(dasa_part)
    elif kp_part and kp_part.get("dasa_hierarchy"):
        dh = kp_part["dasa_hierarchy"]
        # If mahadashas timeline available in KP
        mds = dh.get("mahadashas") or []
        for md in mds:
            periods_list.append({
                "mahadasha_lord": md.get("lord"),
                "bhukti_lord": md.get("lord"),
                "start_date": md.get("start_date"),
                "end_date": md.get("end_date"),
            })

    # If still no periods, calculate full dasa tree
    if not periods_list:
        from datetime import date as dt_date, time as dt_time
        bd_obj = dt_date.fromisoformat(str(b_date).strip()) if isinstance(b_date, str) else b_date
        bt_obj = dt_time.fromisoformat(str(b_time).strip()) if isinstance(b_time, str) else b_time
        local_dt, utc_dt, jd, _, offset_hours = resolve_birth_datetime(bd_obj, bt_obj, tz_str)
        moon_pos = xalen.planet_position(jd, 1, True, ayan_id)
        raw_tree = xalen.vimshottari_dasha(moon_pos["longitude"], jd, 2)
        dasa_tree = [_convert_node(node, birth_date=local_dt.date(), utc_offset_hours=offset_hours) for node in raw_tree]
        periods_list = extract_periods_from_dasa_response({"dasa_tree": dasa_tree})

    # Extract Lagna, Significators, CSL, Retrograde
    lagna_name = None
    if horo_part and horo_part.get("ascendant"):
        lagna_name = horo_part["ascendant"].get("sign_name")

    significations = kp_part.get("house_significators") or {}
    csl_map = derive_cusp_sub_lords_from_chart(kp_part)
    retro_map = extract_retrograde_status_from_chart(horo_part, kp_part)

    # Run analysis
    analysis_res = run_kp_event_analysis(
        lagna=lagna_name,
        periods=periods_list,
        significations=significations,
        csl_significations=csl_map,
        retrograde_status=retro_map,
        current_date=None,
        timezone_str=tz_str,
        filter_category=filter_params.filter_category,
        filter_grade=filter_params.filter_grade,
        filter_event=filter_params.filter_event,
        running_only=bool(filter_params.running_only),
    )

    # Persist analysis to database
    save_res = save_kp_event_analysis(
        user_id=user_id,
        horoscope_id=saved_horoscope_id,
        analysis_data=analysis_res,
    )

    if save_res:
        p_status = save_res.get("persistence_status", "database")
        p_warning = save_res.get("persistence_warning")
        analysis_res["persistence_status"] = p_status
        analysis_res["persistence_warning"] = p_warning
        if "overall_summary" in analysis_res:
            analysis_res["overall_summary"]["persistence_status"] = p_status
            analysis_res["overall_summary"]["persistence_warning"] = p_warning

    return KpEventAnalysisResponse(**analysis_res)


# 3. Retrieve Persisted Analysis
@router.get("/analyses/{saved_horoscope_id}", response_model=KpEventAnalysisResponse, summary="Get stored KP event analysis")
def get_saved_analysis(
    saved_horoscope_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> KpEventAnalysisResponse:
    """Retrieves saved analysis record if previously calculated."""
    user_id = current_user["id"]
    is_admin = current_user.get("role") == "admin"
    supabase = get_supabase_client()

    if supabase:
        try:
            q = supabase.table("saved_horoscopes").select("id, user_id").eq("id", saved_horoscope_id)
            if not is_admin:
                q = q.eq("user_id", user_id)
            res = q.execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved horoscope not found or unauthorized.",
                )
        except HTTPException:
            raise
        except Exception:
            pass

    record = get_kp_event_analysis(user_id, saved_horoscope_id, is_admin=is_admin)

    if not record or not record.get("results"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No saved KP event analysis found for this horoscope. Run analysis first.",
        )

    summary = record.get("summary", {})
    periods = record.get("results", [])
    report = summary.get("human_readable_report") or "Retrieved from saved analysis."
    p_status = record.get("persistence_status", "database")
    p_warning = record.get("persistence_warning")
    return KpEventAnalysisResponse(
        rule_set_version=record.get("rule_set_version", RULE_SET_VERSION),
        lagna=None,
        current_date=record.get("calculation_timestamp", "").split("T")[0] if record.get("calculation_timestamp") else "2026-10-18",
        timezone="Asia/Kolkata",
        overall_summary={
            "rule_set_version": record.get("rule_set_version", RULE_SET_VERSION),
            "total_periods": len(periods),
            "running_period": summary.get("running_period"),
            "green_count": summary.get("green_count", 0),
            "orange_count": summary.get("orange_count", 0),
            "red_count": summary.get("red_count", 0),
            "persistence_status": p_status,
            "persistence_warning": p_warning,
        },
        periods=periods,
        human_readable_report=report,
        persistence_status=p_status,
        persistence_warning=p_warning,
    )


# 4. Centralized Event Definitions Registry
@router.get("/registry", summary="List all 32 KP event definitions")
def get_event_registry() -> Dict[str, Any]:
    """Returns all 32 configured KP event definitions with supporting & denying houses."""
    events = list_all_events()
    return {
        "rule_set_version": RULE_SET_VERSION,
        "total_events": len(events),
        "events": [
            {
                "name": e.name,
                "category": e.category,
                "supporting_houses": e.supporting_houses,
                "denying_houses": e.denying_houses,
                "primary_cusp": e.primary_cusp,
                "is_gain_type": e.is_gain_type,
                "description": e.description,
            }
            for e in events
        ],
    }
