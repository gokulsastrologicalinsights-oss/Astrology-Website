"""KP Event Prediction Engine - Persistence and Repository Service.

Handles persisting and retrieving event analysis records to/from Supabase
public.kp_event_analyses with Row-Level Security (RLS) enforcement and
robust fallback in-memory cache for dev/offline/testing modes.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

from app.services.auth_service import get_supabase_client
from .event_rules import RULE_SET_VERSION

logger = logging.getLogger(__name__)

# In-memory fallback cache for development, testing, and offline modes
_LOCAL_KP_EVENT_ANALYSES: Dict[str, Dict[str, Any]] = {}


def compute_input_fingerprint(data: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 fingerprint from relevant horoscope input fields."""
    normalized_keys = {
        "rule_set_version": RULE_SET_VERSION,
        "lagna": data.get("lagna"),
        "periods": data.get("periods"),
        "significations": data.get("significations"),
        "csl_significations": data.get("csl_significations"),
        "retrograde_status": data.get("retrograde_status"),
    }
    raw_str = json.dumps(normalized_keys, sort_keys=True, default=str)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def save_kp_event_analysis(
    user_id: str,
    horoscope_id: Optional[str],
    analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Persists KP event analysis record to Supabase public.kp_event_analyses or local cache."""
    supabase = get_supabase_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    fingerprint = compute_input_fingerprint(analysis_data)
    record_id = str(uuid.uuid4())

    summary_payload = dict(analysis_data.get("overall_summary", {}))
    if "human_readable_report" in analysis_data:
        summary_payload["human_readable_report"] = analysis_data["human_readable_report"]

    row_data = {
        "id": record_id,
        "user_id": user_id,
        "horoscope_id": horoscope_id,
        "rule_set_version": RULE_SET_VERSION,
        "input_data_fingerprint": fingerprint,
        "calculation_timestamp": now_iso,
        "summary": summary_payload,
        "results": analysis_data.get("periods", []),
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    if supabase:
        try:
            # Check if record for this horoscope_id already exists; update if so
            if horoscope_id:
                existing = (
                    supabase.table("kp_event_analyses")
                    .select("id")
                    .eq("user_id", user_id)
                    .eq("horoscope_id", horoscope_id)
                    .execute()
                )
                if existing.data and len(existing.data) > 0:
                    update_data = {
                        "rule_set_version": RULE_SET_VERSION,
                        "input_data_fingerprint": fingerprint,
                        "calculation_timestamp": now_iso,
                        "summary": summary_payload,
                        "results": analysis_data.get("periods", []),
                        "updated_at": now_iso,
                    }
                    res = (
                        supabase.table("kp_event_analyses")
                        .update(update_data)
                        .eq("id", existing.data[0]["id"])
                        .execute()
                    )
                    if res.data and len(res.data) > 0:
                        out = dict(res.data[0])
                        out["persistence_status"] = "database"
                        return out

            res = supabase.table("kp_event_analyses").insert(row_data).execute()
            if res.data and len(res.data) > 0:
                out = dict(res.data[0])
                out["persistence_status"] = "database"
                return out
        except Exception as exc:
            logger.warning(
                "Database persistence to public.kp_event_analyses was unavailable (%s); falling back to ephemeral in-memory cache.",
                exc,
            )

    # Fallback to local cache with explicit operational warning
    warning_msg = (
        "Warning: Analysis saved to temporary in-memory cache because database table "
        "public.kp_event_analyses is not provisioned or unreachable. Results will not "
        "persist across server restarts or multiple backend workers."
    )
    row_data["persistence_status"] = "in_memory_ephemeral"
    row_data["persistence_warning"] = warning_msg

    # If horoscope_id provided, replace existing entry for same horoscope
    if horoscope_id:
        for k, v in list(_LOCAL_KP_EVENT_ANALYSES.items()):
            if v.get("user_id") == user_id and v.get("horoscope_id") == horoscope_id:
                del _LOCAL_KP_EVENT_ANALYSES[k]

    _LOCAL_KP_EVENT_ANALYSES[record_id] = row_data
    return row_data


def get_kp_event_analysis(
    user_id: str,
    horoscope_id: str,
    is_admin: bool = False,
) -> Optional[Dict[str, Any]]:
    """Retrieves an existing analysis by horoscope_id."""
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("kp_event_analyses").select("*").eq("horoscope_id", horoscope_id)
            res = query.order("created_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                if is_admin or str(row.get("user_id")) == str(user_id):
                    out = dict(row)
                    out["persistence_status"] = "database"
                    return out
        except Exception:
            pass

    # Search local cache
    for record in _LOCAL_KP_EVENT_ANALYSES.values():
        if record.get("horoscope_id") == horoscope_id and (is_admin or record.get("user_id") == user_id):
            out = dict(record)
            out["persistence_status"] = "in_memory_ephemeral"
            out["persistence_warning"] = (
                "Warning: Retrieved from temporary in-memory cache; not yet committed to durable database."
            )
            return out
    return None


def delete_kp_event_analysis(
    user_id: str,
    analysis_id: str,
    is_admin: bool = False,
) -> bool:
    """Deletes an analysis record."""
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("kp_event_analyses").delete().eq("id", analysis_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data:
                return True
        except Exception:
            pass

    if analysis_id in _LOCAL_KP_EVENT_ANALYSES:
        rec = _LOCAL_KP_EVENT_ANALYSES[analysis_id]
        if is_admin or rec.get("user_id") == user_id:
            del _LOCAL_KP_EVENT_ANALYSES[analysis_id]
            return True
    return False


def list_kp_event_analyses(
    user_id: str,
    is_admin: bool = False,
    limit: int = 10,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieves a paginated list of analysis records for the user (or all if admin)
    with related horoscope metadata safely attached.
    """
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    supabase = get_supabase_client()

    if supabase:
        try:
            # Query kp_event_analyses with exact total count
            query = supabase.table("kp_event_analyses").select("*", count="exact")
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = (
                query.order("updated_at", desc=True)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            total_count = res.count if res.count is not None else len(res.data or [])
            rows = res.data or []

            # Collect horoscope_ids to safely enrich with horoscope metadata
            horoscope_ids = [r["horoscope_id"] for r in rows if r.get("horoscope_id")]
            horo_meta_map: Dict[str, Dict[str, Any]] = {}

            if horoscope_ids:
                try:
                    # Enforce application-level user authorization on horoscope metadata
                    h_query = (
                        supabase.table("saved_horoscopes")
                        .select("id, user_id, person_name, birth_date, display_number, calculation_result")
                        .in_("id", list(set(horoscope_ids)))
                    )
                    if not is_admin:
                        h_query = h_query.eq("user_id", user_id)
                    h_res = h_query.execute()
                    for h in (h_res.data or []):
                        asc_sign = None
                        calc = h.get("calculation_result") or {}
                        if isinstance(calc, dict):
                            asc_sign = calc.get("horoscope", {}).get("ascendant", {}).get("sign_name")
                        horo_meta_map[str(h["id"])] = {
                            "person_name": h.get("person_name"),
                            "birth_date": str(h.get("birth_date")),
                            "display_number": h.get("display_number"),
                            "lagna": asc_sign,
                        }
                except Exception as meta_exc:
                    logger.warning("Could not fetch related horoscope metadata: %s", meta_exc)

            summaries = []
            for r in rows:
                summary = r.get("summary") or {}
                hid = str(r.get("horoscope_id")) if r.get("horoscope_id") else None
                meta = horo_meta_map.get(hid, {}) if hid else {}

                summaries.append({
                    "id": str(r["id"]),
                    "user_id": str(r["user_id"]),
                    "horoscope_id": hid,
                    "rule_set_version": r.get("rule_set_version", "1.0.0"),
                    "calculation_timestamp": str(r.get("calculation_timestamp") or r.get("created_at")),
                    "created_at": str(r.get("created_at")),
                    "updated_at": str(r.get("updated_at")),
                    "running_period": summary.get("running_period"),
                    "total_periods": summary.get("total_periods", 0),
                    "green_count": summary.get("green_count", 0),
                    "orange_count": summary.get("orange_count", 0),
                    "red_count": summary.get("red_count", 0),
                    "persistence_status": "database",
                    "person_name": meta.get("person_name"),
                    "birth_date": meta.get("birth_date"),
                    "display_number": meta.get("display_number"),
                    "lagna": meta.get("lagna"),
                })

            return summaries, total_count
        except Exception as exc:
            logger.warning("Database list_kp_event_analyses failed (%s); checking local cache.", exc)

    # Fallback to local cache for offline/testing modes
    filtered = [
        rec for rec in _LOCAL_KP_EVENT_ANALYSES.values()
        if is_admin or rec.get("user_id") == user_id
    ]
    # Sort deterministically by updated_at desc, created_at desc
    filtered.sort(key=lambda x: (x.get("updated_at", ""), x.get("created_at", "")), reverse=True)
    total_count = len(filtered)
    paged = filtered[offset: offset + limit]

    summaries = []
    for r in paged:
        summary = r.get("summary") or {}
        summaries.append({
            "id": str(r.get("id")),
            "user_id": str(r.get("user_id")),
            "horoscope_id": str(r.get("horoscope_id")) if r.get("horoscope_id") else None,
            "rule_set_version": r.get("rule_set_version", "1.0.0"),
            "calculation_timestamp": str(r.get("calculation_timestamp") or r.get("created_at")),
            "created_at": str(r.get("created_at")),
            "updated_at": str(r.get("updated_at")),
            "running_period": summary.get("running_period"),
            "total_periods": summary.get("total_periods", 0),
            "green_count": summary.get("green_count", 0),
            "orange_count": summary.get("orange_count", 0),
            "red_count": summary.get("red_count", 0),
            "persistence_status": "in_memory_ephemeral",
            "person_name": None,
            "birth_date": None,
            "display_number": None,
            "lagna": None,
        })
    return summaries, total_count

