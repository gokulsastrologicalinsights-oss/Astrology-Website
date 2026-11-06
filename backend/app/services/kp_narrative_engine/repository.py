"""Persistence Repository for Saved KP Predictive Narrative Reports.

Provides unified storage with Supabase Postgres table `saved_kp_narratives` and
high-integrity local JSON storage at `data/saved_kp_narratives.json` as reliable fallback.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from app.services.auth_service import get_supabase_client

logger = logging.getLogger("gai.kp_narrative.repository")

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
LOCAL_RECORDS_FILE = DATA_DIR / "saved_kp_narratives.json"


def _ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOCAL_RECORDS_FILE.exists():
        try:
            with open(LOCAL_RECORDS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not initialize local records file: {e}")


def _load_local_records() -> List[Dict[str, Any]]:
    _ensure_data_file()
    try:
        with open(LOCAL_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading local records file: {e}")
        return []


def _save_local_records(records: List[Dict[str, Any]]) -> None:
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
    try:
        parsed = uuid.UUID(str(val).strip())
        return str(parsed)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: '{val}'.",
        )


class KpNarrativeRepository:
    """Repository handling persistence of KP Predictive Narrative reports."""

    @staticmethod
    def save(
        user_id: Optional[str],
        title: str,
        person_name: str,
        birth_date: str,
        birth_time: str,
        latitude: float,
        longitude: float,
        timezone_str: str,
        gender: str,
        language: str,
        report_data: Dict[str, Any],
        saved_horoscope_id: Optional[str] = None,
        record_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        rec_id = _validate_uuid_string(record_id) if record_id else str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        row = {
            "id": rec_id,
            "user_id": user_id,
            "title": title,
            "person_name": person_name,
            "saved_horoscope_id": saved_horoscope_id,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
            "gender": gender,
            "language": language,
            "report_data": report_data,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        # 1. Try Supabase
        sb = get_supabase_client()
        if sb:
            try:
                sb.table("saved_kp_narratives").upsert(row).execute()
                logger.info(f"Saved KP narrative {rec_id} to Supabase")
            except Exception as e:
                logger.warning(f"Supabase persistence error: {e}. Falling back to disk.")

        # 2. Local fallback
        records = _load_local_records()
        existing_idx = next((i for i, r in enumerate(records) if r.get("id") == rec_id), None)
        if existing_idx is not None:
            row["created_at"] = records[existing_idx].get("created_at", now_iso)
            records[existing_idx] = row
        else:
            records.append(row)
        _save_local_records(records)

        return row

    @staticmethod
    def get(record_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> Optional[Dict[str, Any]]:
        clean_id = _validate_uuid_string(record_id)

        # 1. Try Supabase
        sb = get_supabase_client()
        if sb:
            try:
                query = sb.table("saved_kp_narratives").select("*").eq("id", clean_id)
                if not is_admin and user_id:
                    query = query.eq("user_id", user_id)
                res = query.execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                logger.warning(f"Supabase lookup error for {clean_id}: {e}")

        # 2. Local fallback
        records = _load_local_records()
        for r in records:
            if r.get("id") == clean_id:
                if is_admin or not user_id or r.get("user_id") == user_id:
                    return r
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to this saved KP narrative.",
                    )
        return None

    @staticmethod
    def list_all(user_id: Optional[str] = None, is_admin: bool = False) -> List[Dict[str, Any]]:
        sb = get_supabase_client()
        if sb:
            try:
                query = sb.table("saved_kp_narratives").select(
                    "id, user_id, title, person_name, saved_horoscope_id, birth_date, birth_time, language, created_at, updated_at"
                )
                if not is_admin and user_id:
                    query = query.eq("user_id", user_id)
                res = query.order("updated_at", desc=True).execute()
                if res.data is not None:
                    return res.data
            except Exception as e:
                logger.warning(f"Supabase list error: {e}")

        records = _load_local_records()
        filtered = [
            {
                "id": r["id"],
                "user_id": r.get("user_id"),
                "title": r.get("title", "KP Narrative Report"),
                "person_name": r.get("person_name", "Native"),
                "saved_horoscope_id": r.get("saved_horoscope_id"),
                "birth_date": r.get("birth_date", ""),
                "birth_time": r.get("birth_time", ""),
                "language": r.get("language", "ta"),
                "created_at": r.get("created_at", ""),
                "updated_at": r.get("updated_at", ""),
            }
            for r in records
            if is_admin or not user_id or r.get("user_id") == user_id
        ]
        filtered.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return filtered

    @staticmethod
    def delete(record_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> bool:
        clean_id = _validate_uuid_string(record_id)
        # Verify access
        existing = KpNarrativeRepository.get(clean_id, user_id, is_admin)
        if not existing:
            return False

        sb = get_supabase_client()
        if sb:
            try:
                sb.table("saved_kp_narratives").delete().eq("id", clean_id).execute()
            except Exception as e:
                logger.warning(f"Supabase delete error: {e}")

        records = _load_local_records()
        records = [r for r in records if r.get("id") != clean_id]
        _save_local_records(records)
        return True
