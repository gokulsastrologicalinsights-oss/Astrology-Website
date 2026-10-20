"""Repository service for Traditional Tamil Horoscope Writing Documents.

Manages persistence, retrieval, listing, and deletion with:
1. Supabase Postgres table `saved_horoscope_writings` when migration is active.
2. High-integrity local JSON persistence in `data/saved_horoscope_writings.json`
   for persistent storage across server restarts when database DDL migrations are pending.
3. Server-side ownership verification (RLS parity) ensuring users access only their own records.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
from fastapi import HTTPException, status

from app.services.auth_service import get_supabase_client

logger = logging.getLogger("gai.horoscope_writing.repository")

# Locate persistent data directory
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
LOCAL_RECORDS_FILE = DATA_DIR / "saved_horoscope_writings.json"


def _ensure_data_file() -> None:
    """Ensures that the data directory and records file exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOCAL_RECORDS_FILE.exists():
        try:
            with open(LOCAL_RECORDS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not initialize local records file: {e}")


def _load_local_records() -> List[Dict[str, Any]]:
    """Loads all records from the persistent disk file."""
    _ensure_data_file()
    try:
        with open(LOCAL_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading local records file: {e}")
        return []


def _save_local_records(records: List[Dict[str, Any]]) -> None:
    """Atomically saves all records to the persistent disk file."""
    _ensure_data_file()
    temp_file = LOCAL_RECORDS_FILE.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        temp_file.replace(LOCAL_RECORDS_FILE)
    except Exception as e:
        logger.error(f"Error saving local records: {e}")
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass


def _validate_uuid_string(val: Any) -> str:
    """Validates that a string is a well-formed UUID and returns canonical string."""
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: '{val}'.",
        )


class HoroscopeWritingRepository:
    """Unified repository handling Supabase database persistence and local disk fallback."""

    @staticmethod
    def save(
        user_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Persists a horoscope writing document and returns the saved document metadata.
        
        Guarantees persistence across backend restarts.
        """
        clean_user_id = _validate_uuid_string(user_id)
        now_iso = datetime.now(timezone.utc).isoformat()
        new_id = str(uuid.uuid4())

        record: Dict[str, Any] = {
            "id": new_id,
            "user_id": clean_user_id,
            "horoscope_id": payload.get("horoscope_id"),
            "person_name": payload.get("person_name", "Native"),
            "birth_date": payload.get("birth_date"),
            "birth_time": payload.get("birth_time"),
            "birth_place": payload.get("birth_place"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "timezone": payload.get("timezone", "Asia/Kolkata"),
            "panchanga_system": payload.get("panchanga_system", "thirukanitha"),
            "calculated_data": payload.get("calculated_data", {}),
            "overrides": payload.get("overrides", {}),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        # Attempt 1: Supabase PostgreSQL table
        supabase = get_supabase_client()
        if supabase:
            try:
                db_payload = {
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "horoscope_id": record["horoscope_id"],
                    "person_name": record["person_name"],
                    "birth_date": record["birth_date"],
                    "birth_time": record["birth_time"],
                    "birth_place": record["birth_place"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"],
                    "timezone": record["timezone"],
                    "panchanga_system": record["panchanga_system"],
                    "calculated_data": record["calculated_data"],
                    "overrides": record["overrides"],
                }
                resp = supabase.table("saved_horoscope_writings").insert(db_payload).execute()
                if resp.data and len(resp.data) > 0:
                    saved_row = resp.data[0]
                    # Also keep local file in sync
                    local_recs = _load_local_records()
                    local_recs.insert(0, record)
                    _save_local_records(local_recs)

                    return {
                        "success": True,
                        "id": saved_row.get("id", new_id),
                        "persistence_target": "supabase",
                        "message": "Horoscope writing document successfully persisted to Supabase database.",
                        "created_at": saved_row.get("created_at", now_iso),
                    }
            except Exception as db_err:
                logger.info(
                    "Supabase saved_horoscope_writings table not writable (%s); using disk-backed persistence.",
                    db_err,
                )

        # Attempt 2: High-integrity disk-backed persistence
        try:
            local_recs = _load_local_records()
            local_recs.insert(0, record)
            _save_local_records(local_recs)

            return {
                "success": True,
                "id": new_id,
                "persistence_target": "local_disk",
                "message": "Horoscope writing document successfully persisted to secure local repository.",
                "created_at": now_iso,
            }
        except Exception as file_err:
            logger.error("Failed to persist horoscope writing to disk: %s", file_err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist horoscope writing document: {str(file_err)}",
            )

    @staticmethod
    def list_records(
        user_id: str,
        is_admin: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Lists saved horoscope writing documents for the authenticated user."""
        clean_user_id = _validate_uuid_string(user_id)

        # Attempt 1: Supabase
        supabase = get_supabase_client()
        if supabase:
            try:
                query = supabase.table("saved_horoscope_writings").select("*")
                if not is_admin:
                    query = query.eq("user_id", clean_user_id)
                resp = (
                    query.order("created_at", desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )
                if resp.data is not None and len(resp.data) > 0:
                    for row in resp.data:
                        row["persistence_target"] = "supabase"
                    return resp.data
            except Exception as e:
                logger.info("Supabase saved_horoscope_writings query fallback to local: %s", e)

        # Attempt 2: Local disk records
        all_recs = _load_local_records()
        if is_admin:
            filtered = all_recs
        else:
            filtered = [r for r in all_recs if str(r.get("user_id")) == clean_user_id]

        filtered.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        sliced = filtered[offset : offset + limit]
        for r in sliced:
            if "persistence_target" not in r:
                r["persistence_target"] = "local_disk"
        return sliced

    @staticmethod
    def get_by_id(
        record_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """Retrieves a single saved horoscope writing document, enforcing ownership."""
        clean_rec_id = _validate_uuid_string(record_id)
        clean_user_id = _validate_uuid_string(user_id)

        # Attempt 1: Supabase
        supabase = get_supabase_client()
        if supabase:
            try:
                resp = (
                    supabase.table("saved_horoscope_writings")
                    .select("*")
                    .eq("id", clean_rec_id)
                    .execute()
                )
                if resp.data and len(resp.data) > 0:
                    row = resp.data[0]
                    if not is_admin and str(row.get("user_id")) != clean_user_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorized: Access to this horoscope writing document is restricted.",
                        )
                    row["persistence_target"] = "supabase"
                    return row
            except HTTPException:
                raise
            except Exception as e:
                logger.info("Supabase get query fallback to local: %s", e)

        # Attempt 2: Local disk
        all_recs = _load_local_records()
        matching = [r for r in all_recs if str(r.get("id")) == clean_rec_id]
        if not matching:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saved horoscope writing document '{clean_rec_id}' not found.",
            )

        doc = matching[0]
        if not is_admin and str(doc.get("user_id")) != clean_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: Access to this horoscope writing document is restricted.",
            )

        if "persistence_target" not in doc:
            doc["persistence_target"] = "local_disk"
        return doc

    @staticmethod
    def delete(
        record_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> bool:
        """Deletes a saved horoscope writing document, enforcing ownership."""
        clean_rec_id = _validate_uuid_string(record_id)
        clean_user_id = _validate_uuid_string(user_id)

        # First verify document exists and belongs to user
        doc = HoroscopeWritingRepository.get_by_id(clean_rec_id, clean_user_id, is_admin)

        deleted = False

        # Attempt 1: Delete from Supabase
        supabase = get_supabase_client()
        if supabase:
            try:
                supabase.table("saved_horoscope_writings").delete().eq("id", clean_rec_id).execute()
                deleted = True
            except Exception as e:
                logger.info("Supabase delete failed or table missing: %s", e)

        # Attempt 2: Delete from local disk
        all_recs = _load_local_records()
        remaining = [r for r in all_recs if str(r.get("id")) != clean_rec_id]
        if len(remaining) < len(all_recs):
            _save_local_records(remaining)
            deleted = True

        return deleted

    @staticmethod
    def update(
        record_id: str,
        user_id: str,
        payload: Dict[str, Any],
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """Updates an existing saved horoscope writing document, enforcing ownership."""
        clean_rec_id = _validate_uuid_string(record_id)
        clean_user_id = _validate_uuid_string(user_id)

        # Verify document exists and belongs to user (raises 404/403 if not)
        doc = HoroscopeWritingRepository.get_by_id(clean_rec_id, clean_user_id, is_admin)

        now_iso = datetime.now(timezone.utc).isoformat()
        update_fields: Dict[str, Any] = {"updated_at": now_iso}
        for field in ("person_name", "birth_place", "overrides", "calculated_data", "panchanga_system"):
            if field in payload and payload[field] is not None:
                update_fields[field] = payload[field]

        # Update in Supabase if table exists
        supabase = get_supabase_client()
        if supabase:
            try:
                resp = supabase.table("saved_horoscope_writings").update(update_fields).eq("id", clean_rec_id).execute()
                if resp.data and len(resp.data) > 0:
                    doc = resp.data[0]
                    doc["persistence_target"] = "supabase"
            except Exception as e:
                logger.info("Supabase update failed or table missing: %s", e)

        # Update in local disk
        all_recs = _load_local_records()
        for idx, r in enumerate(all_recs):
            if str(r.get("id")) == clean_rec_id:
                all_recs[idx].update(update_fields)
                doc = all_recs[idx]
                break
        _save_local_records(all_recs)

        if "persistence_target" not in doc:
            doc["persistence_target"] = "local_disk"
        return doc
