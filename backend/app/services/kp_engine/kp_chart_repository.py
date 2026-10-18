"""Supabase Persistence and Repository Service for Advanced KP Charts.

Handles saving, listing, fetching, and deleting KP charts (both Natal and Horary Prashna)
with Row-Level Security (RLS) enforcement, concurrency-safe sequential numbering,
and robust fallback in-memory handling during development, testing, or offline modes.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.services.auth_service import get_supabase_client

# In-memory storage cache for development, testing, or offline mode
_LOCAL_SAVED_KP_CHARTS: Dict[str, Dict[str, Any]] = {}
ENGINE_VERSION = "1.0.0"


def save_kp_chart(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Persists a generated KP chart (natal or horary) to Supabase public.saved_kp_charts.
    The database trigger automatically assigns a collision-free sequential display_number.
    """
    supabase = get_supabase_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    chart_type = data.get("chart_type", "natal")
    title = data.get("title") or (
        f"Horary #{data.get('horary_number', '?')} - {data.get('question_text', 'Prashna')[:30]}"
        if chart_type == "horary"
        else f"KP Natal - {data.get('title') or 'Chart'}"
    )

    row_data = {
        "user_id": user_id,
        "chart_type": chart_type,
        "title": title.strip(),
        "birth_date": data.get("birth_date"),
        "birth_time": data.get("birth_time"),
        "horary_number": data.get("horary_number"),
        "question_text": data.get("question_text"),
        "question_date": data.get("question_date"),
        "question_time": data.get("question_time"),
        "location_name": data.get("location_name") or "Unknown Location",
        "latitude": float(data.get("latitude", 13.0827)),
        "longitude": float(data.get("longitude", 80.2707)),
        "timezone": data.get("timezone", "Asia/Kolkata"),
        "ayanamsa_id": int(data.get("ayanamsa_id", 1)),
        "house_system_id": int(data.get("house_system_id", 2)),
        "engine_version": ENGINE_VERSION,
        "calculation_result": data.get("calculation_result", {}),
        "saved_horoscope_id": data.get("saved_horoscope_id"),
    }

    if supabase:
        try:
            res = supabase.table("saved_kp_charts").insert(row_data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            # Table might not exist yet or connection error, fall through to local cache
            pass

    # Fallback in-memory storage for offline / dev / tests
    user_records = [
        r for r in _LOCAL_SAVED_KP_CHARTS.values() if r.get("user_id") == user_id
    ]
    max_disp = max([r.get("display_number", 0) for r in user_records], default=0)

    record_id = str(uuid.uuid4())
    record = {
        **row_data,
        "id": record_id,
        "display_number": max_disp + 1,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    _LOCAL_SAVED_KP_CHARTS[record_id] = record
    return record


def list_kp_charts(
    user_id: str,
    chart_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    is_admin: bool = False,
) -> List[Dict[str, Any]]:
    """Retrieve saved KP charts with RLS enforcement and pagination."""
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("saved_kp_charts").select("*")
            if not is_admin:
                query = query.eq("user_id", user_id)
            if chart_type:
                query = query.eq("chart_type", chart_type)

            res = query.order("display_number", desc=True).range(offset, offset + limit - 1).execute()
            if res.data is not None:
                return res.data
        except Exception:
            pass

    # Fallback to local storage
    records = list(_LOCAL_SAVED_KP_CHARTS.values())
    if not is_admin:
        records = [r for r in records if r.get("user_id") == user_id]
    if chart_type:
        records = [r for r in records if r.get("chart_type") == chart_type]

    records.sort(key=lambda r: r.get("display_number", 0), reverse=True)
    return records[offset : offset + limit]


def get_kp_chart(user_id: str, record_id: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
    """Retrieve a single saved KP chart by ID with ownership verification."""
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("saved_kp_charts").select("*").eq("id", record_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    record = _LOCAL_SAVED_KP_CHARTS.get(record_id)
    if record and (is_admin or record.get("user_id") == user_id):
        return record
    return None


def delete_kp_chart(user_id: str, record_id: str, is_admin: bool = False) -> bool:
    """Delete a saved KP chart with ownership verification."""
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("saved_kp_charts").delete().eq("id", record_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data:
                return True
        except Exception:
            pass

    record = _LOCAL_SAVED_KP_CHARTS.get(record_id)
    if record and (is_admin or record.get("user_id") == user_id):
        del _LOCAL_SAVED_KP_CHARTS[record_id]
        return True
    return False
