"""KP Events & Prediction Router.

Dedicated FastAPI router providing endpoints for evaluating KP event promise,
identifying supporting Dasha periods, scanning candidate transit windows,
and retrieving supported event categories.
"""

from __future__ import annotations
import logging
import uuid
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import xalen
from app.schemas.common import BirthInput
from app.schemas.kp_prediction import (
    KpPredictionRequest,
    KpPredictionResponse,
    KpEventPromiseResult,
    RulingPlanetsInfo,
)
from app.services.auth_service import get_current_user, get_supabase_client
from app.services.dasa_service import _convert_node
from app.services.ephemeris import calculate_full_horoscope
from app.services.kp_service import calculate_kp_chart
from app.services.kp_prediction_service import (
    _get_event_rule,
    get_supported_events_list,
    evaluate_event_promise,
    calculate_ruling_planets,
    evaluate_dasha_periods,
    scan_candidate_event_windows,
    generate_kp_prediction_report_markdown,
    DEFAULT_AYANAMSA_ID,
)
from app.services.timezone_utils import resolve_birth_datetime

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1/kp-prediction", tags=["KP Events & Prediction"])


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """Returns authenticated user dict if valid Bearer token provided, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def _validate_uuid(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns its canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid saved horoscope UUID format.",
        )


@router.get("/events", summary="List supported KP prediction event categories")
def list_events() -> Dict[str, Any]:
    """Returns all validated KP event categories with their supporting and denying houses."""
    events = get_supported_events_list()
    return {
        "status": "success",
        "total_events": len(events),
        "events": events,
    }


@router.post("/scan", response_model=KpPredictionResponse, summary="Scan KP event promise & candidate transit windows")
def scan_kp_prediction(
    req: KpPredictionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> KpPredictionResponse:
    """Evaluates natal promise, supporting Dasha periods, and scans Moon & Ascendant transit windows."""
    # 1. Validate event name
    try:
        event_rule = _get_event_rule(req.event_name)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

    # 2. Resolve birth details and chart data
    birth_date_str: Optional[str] = req.birth_date
    birth_time_str: Optional[str] = req.birth_time
    tz_str: Optional[str] = req.timezone or "Asia/Kolkata"
    lat: Optional[float] = req.latitude
    lon: Optional[float] = req.longitude
    place_name: Optional[str] = req.place_name or "Birth Place"
    customer_name: Optional[str] = req.customer_name
    horoscope_row: Optional[Dict[str, Any]] = None
    saved_chart_ayanamsa = DEFAULT_AYANAMSA_ID

    # If horoscope_id provided, retrieve from database with ownership verification
    if req.horoscope_id:
        clean_hid = _validate_uuid(req.horoscope_id)
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable to fetch saved horoscope.",
            )

        try:
            resp = supabase.table("saved_horoscopes").select("*").eq("id", clean_hid).execute()
            if resp.data and len(resp.data) > 0:
                row = resp.data[0]
                # Enforce ownership check
                is_admin = current_user and current_user.get("role") == "admin"
                if current_user and not is_admin and str(row.get("user_id")) != str(current_user["id"]):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Saved horoscope not found or unauthorized.",
                    )
                horoscope_row = row
                birth_date_str = str(row["birth_date"])
                birth_time_str = str(row["birth_time"])
                tz_str = str(row.get("timezone", "Asia/Kolkata"))
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                place_name = str(row.get("birthplace", "Birth Place"))
                customer_name = str(row.get("person_name", "Native"))
                saved_chart_ayanamsa = int(row.get("ayanamsa_id", DEFAULT_AYANAMSA_ID))
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error reading saved horoscope {clean_hid}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved horoscope not found or unauthorized.",
            )

    # Validate essential birth fields
    if not birth_date_str or not birth_time_str or lat is None or lon is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Birth date, birth time, latitude, and longitude must be supplied or linked to a saved horoscope.",
        )

    # Validate timezone
    try:
        ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, ValueError):
        tz_str = "Asia/Kolkata"

    # 3. Calculate or unpack natal KP chart and Dasha tree
    kp_data: Optional[Dict[str, Any]] = None
    dasa_tree: Optional[List[Dict[str, Any]]] = None

    if horoscope_row and horoscope_row.get("calculation_result"):
        calc_res = horoscope_row["calculation_result"]
        if "kp" in calc_res and isinstance(calc_res["kp"], dict):
            kp_data = calc_res["kp"]
        if "dasa" in calc_res and isinstance(calc_res["dasa"], dict) and "dasa_tree" in calc_res["dasa"]:
            dasa_tree = calc_res["dasa"]["dasa_tree"]

    # Recompute KP chart if missing from snapshot
    if not kp_data:
        b_input = BirthInput(
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            timezone=tz_str,
            latitude=lat,
            longitude=lon,
        )
        kp_res = calculate_kp_chart(b_input, ayanamsa_id=saved_chart_ayanamsa)
        kp_data = kp_res.model_dump()

    # Recompute Dasha tree if missing
    if not dasa_tree:
        try:
            bd_obj = date.fromisoformat(birth_date_str.strip())
            # Parse time
            t_parts = [int(p) for p in birth_time_str.strip().split(":")[:3]]
            bt_obj = time(*t_parts)
            local_dt, utc_dt, jd_birth, _, offset_hours = resolve_birth_datetime(bd_obj, bt_obj, tz_str)
            moon_pos = xalen.planet_position(jd_birth, 1, True, saved_chart_ayanamsa)
            raw_tree = xalen.vimshottari_dasha(moon_pos["longitude"], jd_birth, 3)
            dasa_tree = [
                _convert_node(node, birth_date=local_dt.date(), utc_offset_hours=offset_hours).model_dump()
                for node in raw_tree
            ]
        except Exception as exc:
            logger.error(f"Error computing Dasha tree: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dasha calculation failed: {exc}",
            )

    # 4. Evaluate Natal Event Promise
    promise_res = evaluate_event_promise(kp_data, event_rule)

    # 5. Evaluate Ruling Planets if requested
    rp_info: Optional[RulingPlanetsInfo] = None
    active_rp_set: Set[str] = set()

    if req.include_ruling_planets:
        j_dt: datetime
        if req.judgement_datetime:
            try:
                j_dt = datetime.fromisoformat(req.judgement_datetime)
            except ValueError:
                j_dt = datetime.now(ZoneInfo(tz_str))
        else:
            j_dt = datetime.now(ZoneInfo(tz_str))

        j_lat = req.judgement_latitude if req.judgement_latitude is not None else lat
        j_lon = req.judgement_longitude if req.judgement_longitude is not None else lon

        rp_info = calculate_ruling_planets(j_dt, j_lat, j_lon, ayanamsa_id=saved_chart_ayanamsa)
        active_rp_set = set(rp_info.active_ruling_planets)

    # 6. Parse and clamp scan date range
    today = date.today()
    scan_start: date = today
    if req.start_date:
        try:
            scan_start = date.fromisoformat(req.start_date.strip())
        except ValueError:
            scan_start = today

    scan_end: date = scan_start + timedelta(days=60)
    if req.end_date:
        try:
            scan_end = date.fromisoformat(req.end_date.strip())
        except ValueError:
            scan_end = scan_start + timedelta(days=60)

    # Enforce sensible bounds (minimum 1 day, maximum 180 days)
    if scan_end < scan_start:
        scan_end = scan_start + timedelta(days=30)
    if (scan_end - scan_start).days > 180:
        scan_end = scan_start + timedelta(days=180)

    # 7. Evaluate Dasha periods within the scan range
    # Build planet significations map from kp_data
    house_sigs = kp_data.get("house_significators") or {}
    p_sigs: Dict[str, List[int]] = {}
    if isinstance(house_sigs, dict):
        for h_str, sig_d in house_sigs.items():
            try:
                h_int = int(h_str)
            except (ValueError, TypeError):
                continue
            all_planets = sig_d.get("level_a", []) + sig_d.get("level_b", []) + sig_d.get("level_c", []) + sig_d.get("level_d", [])
            for p in all_planets:
                if p not in p_sigs:
                    p_sigs[p] = []
                if h_int not in p_sigs[p]:
                    p_sigs[p].append(h_int)
    elif isinstance(house_sigs, list):
        for sig_d in house_sigs:
            if isinstance(sig_d, dict):
                h_int = int(sig_d.get("house", 0))
                all_planets = sig_d.get("level_a", []) + sig_d.get("level_b", []) + sig_d.get("level_c", []) + sig_d.get("level_d", [])
                for p in all_planets:
                    if p not in p_sigs:
                        p_sigs[p] = []
                    if h_int not in p_sigs[p]:
                        p_sigs[p].append(h_int)

    if not p_sigs and "significators" in kp_data and isinstance(kp_data["significators"], list):
        for s in kp_data["significators"]:
            if isinstance(s, dict):
                p_sigs[s.get("planet")] = s.get("signified_houses", [])

    dasha_period_results = evaluate_dasha_periods(
        dasa_tree=dasa_tree,
        planet_significations=p_sigs,
        event_rule=event_rule,
        scan_start=scan_start,
        scan_end=scan_end,
    )

    # 8. Run Date & Time Scanner (Moon & Lagna transits)
    scan_res = scan_candidate_event_windows(
        kp_chart=kp_data,
        event_rule=event_rule,
        dasa_tree=dasa_tree,
        scan_start=scan_start,
        scan_end=scan_end,
        transit_lat=lat,
        transit_lon=lon,
        transit_tz_str=tz_str,
        ruling_planets=active_rp_set,
        max_candidates=req.max_candidates,
        scan_res_min=req.scan_resolution_minutes,
        ayanamsa_id=saved_chart_ayanamsa,
        scan_mode=req.scan_mode or "standard",
        deep_refinement_target=req.deep_refinement_target or "sub_lord",
        deep_max_intervals_to_refine=req.deep_max_intervals_to_refine or 15,
        return_benchmark_metrics=True,
    )
    candidate_windows, benchmark_metrics = scan_res

    # 9. Assemble response payload
    convention_str = (
        "XALEN 0.6.0 (Rust) / Swiss Ephemeris Native Engine (Chitrapaksha Lahiri, Placidus Cusps, KP 249 Sub-Lords)"
        if saved_chart_ayanamsa == 1
        else "XALEN 0.6.0 (Rust) / Swiss Ephemeris Native Engine (KP Krishnamurti, Placidus Cusps, KP 249 Sub-Lords)"
    )

    accuracy_warning = (
        "KP Cuspal Sub-Lord calculations are highly sensitive to birth-time accuracy. "
        "A difference of 2 to 4 minutes can shift the Cuspal Sub-Lord or Sub-Sub-Lord. "
        "Verify birth-time precision with verifiable past life events before relying on candidate timing windows."
    )

    disclaimer_str = (
        "Calculated transit windows reflect favorable astrological alignments and planetary resonance according to "
        "classical Krishnamurti Paddhati principles. They are intended for guidance and decision support, not deterministic "
        "or guaranteed real-world event dates."
    )

    response_obj = KpPredictionResponse(
        horoscope_id=req.horoscope_id,
        customer_name=customer_name or "Native",
        birth_details={
            "birth_date": birth_date_str,
            "birth_time": birth_time_str,
            "timezone": tz_str,
            "latitude": lat,
            "longitude": lon,
            "birth_place": place_name,
        },
        calculation_convention=convention_str,
        birth_time_accuracy_warning=accuracy_warning,
        event_promise=promise_res,
        ruling_planets=rp_info,
        candidate_dasha_periods=dasha_period_results,
        candidate_windows=candidate_windows,
        total_windows_found=len(candidate_windows),
        scan_parameters={
            "start_date": scan_start.isoformat(),
            "end_date": scan_end.isoformat(),
            "scan_resolution_minutes": req.scan_resolution_minutes,
            "max_candidates": req.max_candidates,
            "include_ruling_planets": req.include_ruling_planets,
            "scan_mode": req.scan_mode or "standard",
            "deep_refinement_target": req.deep_refinement_target or "sub_lord",
            "deep_max_intervals_to_refine": req.deep_max_intervals_to_refine or 15,
            "benchmark_metrics": benchmark_metrics,
        },
        limitations_disclaimer=disclaimer_str,
        report_markdown="",  # filled below
    )

    # 10. Generate complete report markdown
    response_obj.report_markdown = generate_kp_prediction_report_markdown(response_obj)

    return response_obj
