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
from typing import Dict, Any, Optional, List

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
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.order("created_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                out = dict(res.data[0])
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
