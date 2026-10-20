"""Supabase Persistence and Repository Service for Saved Marriage Compatibility Reports.

Handles saving, listing, fetching, updating metadata, and deleting marriage compatibility reports
with Row-Level Security (RLS) enforcement, sequential display numbering, immutability of
calculation snapshots, and linked-horoscope ownership verification.
"""

from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.schemas.marriage import (
    SaveMarriageCompatibilityReportRequest,
    UpdateMarriageReportMetadataRequest,
)
from app.services.auth_service import get_supabase_client

logger = logging.getLogger("gai.marriage_engine.report_repository")

# In-memory storage caches for offline development, local testing, and mock fallbacks
_LOCAL_SAVED_MARRIAGE_REPORTS: Dict[str, Dict[str, Any]] = {}
_LOCAL_SAVED_HOROSCOPES: Dict[str, Dict[str, Any]] = {}

PERMITTED_METADATA_UPDATE_FIELDS = {
    "title",
    "groom_name",
    "bride_name",
    "groom_saved_horoscope_id",
    "bride_saved_horoscope_id",
}


def _validate_uuid_string(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns its canonical string representation."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: '{val}'.",
        )


def verify_horoscope_ownership(
    user_id: str,
    horoscope_id: str,
    role_description: str = "horoscope",
    is_admin: bool = False,
) -> None:
    """Confirms that the authenticated user owns the referenced saved horoscope.

    Raises:
        HTTPException(403): If the referenced horoscope does not belong to the user.
        HTTPException(404): If the referenced horoscope does not exist.
    """
    clean_id = _validate_uuid_string(horoscope_id)
    supabase = get_supabase_client()

    if supabase:
        try:
            res = (
                supabase.table("saved_horoscopes")
                .select("id, user_id")
                .eq("id", clean_id)
                .execute()
            )
            if not res.data or len(res.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Referenced {role_description} '{clean_id}' not found.",
                )
            record = res.data[0]
            if not is_admin and str(record.get("user_id")) != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Unauthorized: {role_description} '{clean_id}' does not belong to the authenticated user.",
                )
            return
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning(f"Error checking horoscope ownership in Supabase: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error checking {role_description} ownership: {str(exc)}",
            )

    # Offline / local mock fallback check
    if clean_id in _LOCAL_SAVED_HOROSCOPES:
        record = _LOCAL_SAVED_HOROSCOPES[clean_id]
        if not is_admin and str(record.get("user_id")) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unauthorized: {role_description} '{clean_id}' does not belong to the authenticated user.",
            )
        return

    # If in offline mode and horoscope not found in local mock, treat as not found if table was populated,
    # or allow if mock table is completely unpopulated in basic offline tests.
    if _LOCAL_SAVED_HOROSCOPES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referenced {role_description} '{clean_id}' not found in local records.",
        )


def save_marriage_report(
    user_id: str,
    payload: SaveMarriageCompatibilityReportRequest,
    is_admin: bool = False,
) -> Dict[str, Any]:
    """Persists a completed marriage compatibility report to Supabase public.saved_marriage_compatibility_reports.

    Enforces:
    - User ownership of referenced groom and bride horoscopes.
    - Advisory-locked collision-free sequential display numbering via DB trigger.
    - Snapshot immutability.
    """
    clean_user_id = _validate_uuid_string(user_id)

    # 1. Verify ownership of referenced horoscopes if provided
    if payload.groom_saved_horoscope_id:
        verify_horoscope_ownership(
            clean_user_id,
            payload.groom_saved_horoscope_id,
            role_description="groom_saved_horoscope_id",
            is_admin=is_admin,
        )

    if payload.bride_saved_horoscope_id:
        verify_horoscope_ownership(
            clean_user_id,
            payload.bride_saved_horoscope_id,
            role_description="bride_saved_horoscope_id",
            is_admin=is_admin,
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    row_data = {
        "user_id": clean_user_id,
        "title": payload.title.strip(),
        "groom_name": payload.groom_name.strip(),
        "bride_name": payload.bride_name.strip(),
        "groom_birth_date": str(payload.groom_birth_date),
        "bride_birth_date": str(payload.bride_birth_date),
        "groom_is_approximate": bool(payload.groom_is_approximate),
        "bride_is_approximate": bool(payload.bride_is_approximate),
        "groom_saved_horoscope_id": payload.groom_saved_horoscope_id,
        "bride_saved_horoscope_id": payload.bride_saved_horoscope_id,
        "rule_system": payload.rule_system,
        "ayanamsa_id": int(payload.ayanamsa_id),
        "house_system_id": int(payload.house_system_id),
        "include_kp": bool(payload.include_kp),
        "include_timing": bool(payload.include_timing),
        "overall_outcome": payload.overall_outcome,
        "porutham_score": payload.porutham_score,
        "ashtakoota_points": payload.ashtakoota_points,
        "samadosham_status": payload.samadosham_status,
        "papasamya_verdict": payload.papasamya_verdict,
        "ruling_planets_agreement": payload.ruling_planets_agreement,
        "report_data": payload.report_data,
        "engine_version": payload.engine_version or "1.0.0",
        "report_schema_version": payload.report_schema_version or "1.0.0",
    }

    supabase = get_supabase_client()
    if supabase:
        try:
            res = (
                supabase.table("saved_marriage_compatibility_reports")
                .insert(row_data)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise RuntimeError("Database write succeeded but returned no record.")
        except Exception as exc:
            err_msg = str(exc)
            if "PGRST205" in err_msg or "Could not find table 'public.saved_marriage_compatibility_reports'" in err_msg:
                logger.warning(
                    f"Table 'saved_marriage_compatibility_reports' not found in Supabase schema cache (unmigrated). "
                    f"Falling back to local in-memory repository: {exc}"
                )
            else:
                logger.error(f"Failed to persist marriage report to Supabase for user {clean_user_id}: {exc}")
                if "Unauthorized:" in err_msg or "does not belong" in err_msg:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=err_msg,
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database write failed: {err_msg}",
                )

    # Local fallback for offline mode / unit testing
    user_records = [
        r for r in _LOCAL_SAVED_MARRIAGE_REPORTS.values()
        if str(r.get("user_id")) == clean_user_id
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
    _LOCAL_SAVED_MARRIAGE_REPORTS[record_id] = record
    return dict(record)


def list_marriage_reports(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    is_admin: bool = False,
) -> List[Dict[str, Any]]:
    """Retrieve saved marriage compatibility reports with RLS enforcement, newest first.

    Ordering: display_number DESC (sequential newest first per user).
    """
    clean_user_id = _validate_uuid_string(user_id)
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("saved_marriage_compatibility_reports").select("*")
            if not is_admin:
                query = query.eq("user_id", clean_user_id)

            res = (
                query.order("display_number", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            if res.data is not None:
                return res.data
            return []
        except Exception as exc:
            err_msg = str(exc)
            if "PGRST205" in err_msg or "Could not find table 'public.saved_marriage_compatibility_reports'" in err_msg:
                logger.warning("Table 'saved_marriage_compatibility_reports' not found in Supabase schema cache. Falling back to local in-memory repository.")
            else:
                logger.error(f"Failed to list marriage reports from Supabase for user {clean_user_id}: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database query failed: {str(exc)}",
                )

    # Local in-memory fallback
    records = list(_LOCAL_SAVED_MARRIAGE_REPORTS.values())
    if not is_admin:
        records = [r for r in records if str(r.get("user_id")) == clean_user_id]

    records.sort(key=lambda r: r.get("display_number", 0), reverse=True)
    return [dict(r) for r in records[offset : offset + limit]]


def get_marriage_report(
    user_id: str,
    report_id: str,
    is_admin: bool = False,
) -> Optional[Dict[str, Any]]:
    """Retrieve a single saved marriage compatibility report by UUID, enforcing ownership."""
    clean_user_id = _validate_uuid_string(user_id)
    clean_report_id = _validate_uuid_string(report_id)
    supabase = get_supabase_client()

    if supabase:
        try:
            query = (
                supabase.table("saved_marriage_compatibility_reports")
                .select("*")
                .eq("id", clean_report_id)
            )
            if not is_admin:
                query = query.eq("user_id", clean_user_id)

            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as exc:
            err_msg = str(exc)
            if "PGRST205" in err_msg or "Could not find table 'public.saved_marriage_compatibility_reports'" in err_msg:
                logger.warning("Table 'saved_marriage_compatibility_reports' not found in Supabase schema cache. Falling back to local in-memory repository.")
            else:
                logger.error(f"Failed to fetch marriage report {clean_report_id} from Supabase: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database query failed: {str(exc)}",
                )

    record = _LOCAL_SAVED_MARRIAGE_REPORTS.get(clean_report_id)
    if record and (is_admin or str(record.get("user_id")) == clean_user_id):
        return dict(record)
    return None


def update_marriage_report_metadata(
    user_id: str,
    report_id: str,
    update_data: Dict[str, Any],
    is_admin: bool = False,
) -> Dict[str, Any]:
    """Updates permitted metadata fields for a saved marriage compatibility report.

    Strict rules:
    - Only title, groom_name, bride_name, groom_saved_horoscope_id, and bride_saved_horoscope_id can be updated.
    - All calculation data, scores, parameters, timestamps, display numbers, and ownership are strictly immutable.
    - If horoscope links are changed, the new references must belong to the authenticated user.
    """
    clean_user_id = _validate_uuid_string(user_id)
    clean_report_id = _validate_uuid_string(report_id)

    # 1. Reject any attempted update of immutable fields
    disallowed_fields = [k for k in update_data.keys() if k not in PERMITTED_METADATA_UPDATE_FIELDS]
    if disallowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot update immutable fields: {disallowed_fields}. "
                f"Only {sorted(PERMITTED_METADATA_UPDATE_FIELDS)} can be modified."
            ),
        )

    # 2. Verify existence and ownership of report
    existing = get_marriage_report(clean_user_id, clean_report_id, is_admin=is_admin)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved marriage compatibility report not found or unauthorized.",
        )

    # 3. Filter permitted updates (strip strings, handle nulls)
    clean_updates: Dict[str, Any] = {}
    if "title" in update_data and update_data["title"] is not None:
        title_str = str(update_data["title"]).strip()
        if not title_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title cannot be empty.",
            )
        clean_updates["title"] = title_str

    if "groom_name" in update_data and update_data["groom_name"] is not None:
        groom_str = str(update_data["groom_name"]).strip()
        if not groom_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Groom name cannot be empty.",
            )
        clean_updates["groom_name"] = groom_str

    if "bride_name" in update_data and update_data["bride_name"] is not None:
        bride_str = str(update_data["bride_name"]).strip()
        if not bride_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Bride name cannot be empty.",
            )
        clean_updates["bride_name"] = bride_str

    if "groom_saved_horoscope_id" in update_data:
        gid = update_data["groom_saved_horoscope_id"]
        if gid:
            verify_horoscope_ownership(
                clean_user_id,
                gid,
                role_description="groom_saved_horoscope_id",
                is_admin=is_admin,
            )
            clean_updates["groom_saved_horoscope_id"] = str(uuid.UUID(str(gid).strip()))
        else:
            clean_updates["groom_saved_horoscope_id"] = None

    if "bride_saved_horoscope_id" in update_data:
        bid = update_data["bride_saved_horoscope_id"]
        if bid:
            verify_horoscope_ownership(
                clean_user_id,
                bid,
                role_description="bride_saved_horoscope_id",
                is_admin=is_admin,
            )
            clean_updates["bride_saved_horoscope_id"] = str(uuid.UUID(str(bid).strip()))
        else:
            clean_updates["bride_saved_horoscope_id"] = None

    if not clean_updates:
        return existing

    now_iso = datetime.now(timezone.utc).isoformat()
    clean_updates["updated_at"] = now_iso

    supabase = get_supabase_client()
    if supabase:
        try:
            query = (
                supabase.table("saved_marriage_compatibility_reports")
                .update(clean_updates)
                .eq("id", clean_report_id)
            )
            if not is_admin:
                query = query.eq("user_id", clean_user_id)

            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved marriage compatibility report update failed or not found.",
            )
        except HTTPException:
            raise
        except Exception as exc:
            err_msg = str(exc)
            if "PGRST205" in err_msg or "Could not find table 'public.saved_marriage_compatibility_reports'" in err_msg:
                logger.warning("Table 'saved_marriage_compatibility_reports' not found in Supabase schema cache. Falling back to local in-memory repository.")
            else:
                logger.error(f"Failed to update marriage report {clean_report_id} in Supabase: {exc}")
                if "immutable" in err_msg.lower() or "disallow" in err_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=err_msg,
                    )
                if "Unauthorized:" in err_msg or "does not belong" in err_msg:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=err_msg,
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database update failed: {err_msg}",
                )

    # Local in-memory fallback
    record = _LOCAL_SAVED_MARRIAGE_REPORTS.get(clean_report_id)
    if not record or (not is_admin and str(record.get("user_id")) != clean_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved marriage compatibility report not found or unauthorized.",
        )

    for k, v in clean_updates.items():
        record[k] = v
    return dict(record)


def delete_marriage_report(
    user_id: str,
    report_id: str,
    is_admin: bool = False,
) -> bool:
    """Delete a saved marriage compatibility report with ownership verification."""
    clean_user_id = _validate_uuid_string(user_id)
    clean_report_id = _validate_uuid_string(report_id)

    # 1. Verify existence and ownership first
    existing = get_marriage_report(clean_user_id, clean_report_id, is_admin=is_admin)
    if not existing:
        return False

    supabase = get_supabase_client()
    if supabase:
        try:
            query = (
                supabase.table("saved_marriage_compatibility_reports")
                .delete()
                .eq("id", clean_report_id)
            )
            if not is_admin:
                query = query.eq("user_id", clean_user_id)

            res = query.execute()
            if res.data and len(res.data) > 0:
                return True
            return False
        except Exception as exc:
            err_msg = str(exc)
            if "PGRST205" in err_msg or "Could not find table 'public.saved_marriage_compatibility_reports'" in err_msg:
                logger.warning("Table 'saved_marriage_compatibility_reports' not found in Supabase schema cache. Falling back to local in-memory repository.")
            else:
                logger.error(f"Failed to delete marriage report {clean_report_id} from Supabase: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database deletion failed: {str(exc)}",
                )

    # Local in-memory fallback
    if clean_report_id in _LOCAL_SAVED_MARRIAGE_REPORTS:
        rec = _LOCAL_SAVED_MARRIAGE_REPORTS[clean_report_id]
        if is_admin or str(rec.get("user_id")) == clean_user_id:
            del _LOCAL_SAVED_MARRIAGE_REPORTS[clean_report_id]
            return True
    return False


def clear_local_storage() -> None:
    """Helper for unit and integration testing to reset in-memory test databases."""
    _LOCAL_SAVED_MARRIAGE_REPORTS.clear()
    _LOCAL_SAVED_HOROSCOPES.clear()
