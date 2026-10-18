"""Supabase Persistence and Repository Service for Muhurta.

Handles saving, listing, fetching, updating, and deleting Muhurta records
with Row-Level Security (RLS) enforcement, concurrency-safe sequential numbering,
and robust fallback in-memory/cache handling during development or tests.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.services.auth_service import get_supabase_client
from app.services.muhurta_engine.occasions import DEFAULT_OCCASIONS

# In-memory storage cache for occasions, rules, and saved muhurtas
_LOCAL_SAVED_MUHURTAS: Dict[str, Dict[str, Any]] = {}
_LOCAL_CUSTOM_OCCASIONS: Dict[str, Dict[str, Any]] = {}
_LOCAL_RULES: Dict[str, Dict[str, Any]] = {}


def save_muhurta_selection(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a candidate Muhurta interval to Supabase public.saved_muhurtas.
    The database trigger automatically assigns a collision-free sequential display_number.
    """
    supabase = get_supabase_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    row_data = {
        "user_id": user_id,
        "title": data.get("title") or f"{data.get('occasion_name', 'Muhurta')} on {data.get('event_date')}",
        "occasion_code": data.get("occasion_code", "marriage"),
        "occasion_name": data.get("occasion_name", "Marriage"),
        "event_date": data.get("event_date"),
        "start_time": data.get("start_time"),
        "end_time": data.get("end_time"),
        "local_start_time": data.get("local_start_time"),
        "local_end_time": data.get("local_end_time"),
        "duration_minutes": data.get("duration_minutes", 45),
        "location_name": data.get("location_name", "Chennai, India"),
        "latitude": data.get("latitude", 13.0827),
        "longitude": data.get("longitude", 80.2707),
        "timezone": data.get("timezone", "Asia/Kolkata"),
        "ayanamsa_id": data.get("ayanamsa_id", 0),
        "tradition": data.get("tradition", "south_indian"),
        "score": data.get("score", 85),
        "status": data.get("status", "meets_configured_rules"),
        "panchang_summary": data.get("panchang_summary", {}),
        "lagna_summary": data.get("lagna_summary", {}),
        "rule_evaluations": data.get("rule_evaluations", {}),
        "birth_details": data.get("birth_details"),
        "notes": data.get("notes"),
        "client_name": data.get("client_name"),
    }

    if supabase:
        try:
            res = supabase.table("saved_muhurtas").insert(row_data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            # Table might still be synchronizing schema cache; fallback to memory
            pass

    # Fallback storage
    record_id = str(uuid.uuid4())
    user_records = [r for r in _LOCAL_SAVED_MUHURTAS.values() if r["user_id"] == user_id]
    next_disp = len(user_records) + 1

    record = {
        "id": record_id,
        "display_number": next_disp,
        "created_at": now_iso,
        "updated_at": now_iso,
        **row_data,
    }
    _LOCAL_SAVED_MUHURTAS[record_id] = record
    return record


def list_saved_muhurtas(
    user_id: str,
    is_admin: bool = False,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve saved muhurtas for authenticated user, or all for admin."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_muhurtas").select("*")
            if not is_admin:
                query = query.eq("user_id", user_id)
            if search:
                query = query.or_(f"title.ilike.%{search}%,client_name.ilike.%{search}%")
            res = query.order("display_number", desc=True).range(offset, offset + limit - 1).execute()
            if res.data is not None:
                return res.data
        except Exception:
            pass

    # Fallback
    records = list(_LOCAL_SAVED_MUHURTAS.values())
    if not is_admin:
        records = [r for r in records if r["user_id"] == user_id]
    if search:
        s = search.lower()
        records = [
            r for r in records
            if s in r.get("title", "").lower() or s in (r.get("client_name") or "").lower()
        ]
    records.sort(key=lambda r: r.get("display_number", 0), reverse=True)
    return records[offset:offset + limit]


def get_saved_muhurta(user_id: str, record_id: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
    """Retrieve a single saved Muhurta report by UUID."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_muhurtas").select("*").eq("id", record_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    record = _LOCAL_SAVED_MUHURTAS.get(record_id)
    if record and (is_admin or record["user_id"] == user_id):
        return record
    return None


def update_saved_muhurta(
    user_id: str, record_id: str, updates: Dict[str, Any], is_admin: bool = False
) -> Optional[Dict[str, Any]]:
    """Updates client_name, notes, or title on a saved Muhurta record."""
    supabase = get_supabase_client()
    allowed_fields = {"title", "client_name", "notes"}
    data_to_update = {k: v for k, v in updates.items() if k in allowed_fields}
    data_to_update["updated_at"] = datetime.now(timezone.utc).isoformat()

    if supabase:
        try:
            query = supabase.table("saved_muhurtas").update(data_to_update).eq("id", record_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    record = _LOCAL_SAVED_MUHURTAS.get(record_id)
    if record and (is_admin or record["user_id"] == user_id):
        record.update(data_to_update)
        return record
    return None


def delete_saved_muhurta(user_id: str, record_id: str, is_admin: bool = False) -> bool:
    """Delete a saved Muhurta record."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_muhurtas").delete().eq("id", record_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return True
        except Exception:
            pass

    record = _LOCAL_SAVED_MUHURTAS.get(record_id)
    if record and (is_admin or record["user_id"] == user_id):
        del _LOCAL_SAVED_MUHURTAS[record_id]
        return True
    return False


# Occasion Management
def list_occasions(include_disabled: bool = False) -> List[Dict[str, Any]]:
    """List occasions including default system ones and any custom admin ones."""
    occasions = list(DEFAULT_OCCASIONS)
    occasions.extend(_LOCAL_CUSTOM_OCCASIONS.values())
    if not include_disabled:
        occasions = [o for o in occasions if o.get("is_enabled", True)]
    return occasions


def create_custom_occasion(admin_user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Admin-only: Create a new custom occasion type."""
    code = data["code"].lower().strip().replace(" ", "_")
    now_iso = datetime.now(timezone.utc).isoformat()
    obj = {
        "id": str(uuid.uuid4()),
        "code": code,
        "name_en": data["name_en"],
        "name_ta": data.get("name_ta") or data["name_en"],
        "category": data.get("category", "custom"),
        "description_en": data.get("description_en", ""),
        "description_ta": data.get("description_ta", ""),
        "icon": data.get("icon", "Sparkles"),
        "is_enabled": data.get("is_enabled", True),
        "is_system": False,
        "created_by": admin_user_id,
        "created_at": now_iso,
        "updated_at": now_iso,
        "rules": data.get("rules", {
            "acceptable_tithis": [2, 3, 5, 7, 10, 11, 13],
            "acceptable_nakshatras": [1, 4, 5, 7, 8, 12, 13, 15, 17, 21, 22, 26, 27],
            "acceptable_weekdays": [1, 3, 4, 5],
            "prohibit_rahu_kalam": True,
            "prohibit_yamagandam": True,
            "prohibit_gulikai": False,
            "prohibit_dur_muhurta": True,
            "prohibit_varjyam": True,
            "require_ashtama_shuddhi": True,
            "require_sapthama_shuddhi": False,
            "require_tara_bala": True,
            "require_chandra_bala": True,
            "allowed_lagnas": [],
            "min_duration_minutes": 30,
        }),
    }
    _LOCAL_CUSTOM_OCCASIONS[code] = obj
    return obj


def update_occasion(code: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Admin-only: Update or disable an occasion."""
    # Look in custom
    if code in _LOCAL_CUSTOM_OCCASIONS:
        _LOCAL_CUSTOM_OCCASIONS[code].update(updates)
        _LOCAL_CUSTOM_OCCASIONS[code]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return _LOCAL_CUSTOM_OCCASIONS[code]

    # Look in default
    for o in DEFAULT_OCCASIONS:
        if o["code"] == code:
            o.update(updates)
            return o
    return None
