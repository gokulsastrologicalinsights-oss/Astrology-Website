"""Supabase Persistence Service for Numerology Reports.

Handles saving, listing, fetching, and deleting numerology reports with
Row-Level Security (RLS) enforcement and concurrency-safe sequential numbering.
"""

from typing import List, Dict, Any, Optional
from app.services.auth_service import get_supabase_client
from app.schemas.numerology import SaveNumerologyReportRequest


ENGINE_VERSION = "1.0.0"


def save_numerology_report(user_id: str, request: SaveNumerologyReportRequest) -> Dict[str, Any]:
    """Persists a generated numerology report to Supabase public.saved_numerology_reports.
    The database trigger automatically assigns a collision-free sequential display_number.
    """
    supabase = get_supabase_client()
    if not supabase:
        # Fallback offline simulation when database is disconnected in tests/dev
        import uuid
        from datetime import datetime, timezone
        return {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "display_number": 1,
            "person_name": request.person_name,
            "birth_date": request.birth_date,
            "method": request.method,
            "system_convention": request.system_convention,
            "calculation_data": request.calculation_data,
            "interpretation_data": request.interpretation_data,
            "engine_version": ENGINE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    data = {
        "user_id": user_id,
        "person_name": request.person_name.strip(),
        "birth_date": request.birth_date.strip(),
        "method": request.method.strip(),
        "system_convention": request.system_convention.strip(),
        "calculation_data": request.calculation_data,
        "interpretation_data": request.interpretation_data,
        "engine_version": ENGINE_VERSION,
    }

    res = (
        supabase.table("saved_numerology_reports")
        .insert(data)
        .execute()
    )

    if not res.data:
        raise RuntimeError("Failed to insert numerology report into database.")

    return res.data[0]


def list_numerology_reports(
    user_id: str, is_admin: bool = False, limit: int = 50, offset: int = 0
) -> List[Dict[str, Any]]:
    """Retrieve saved numerology reports for the authenticated user, or all for admins."""
    supabase = get_supabase_client()
    if not supabase:
        return []

    query = supabase.table("saved_numerology_reports").select("*")
    if not is_admin:
        query = query.eq("user_id", user_id)

    res = query.order("display_number", desc=True).range(offset, offset + limit - 1).execute()
    return res.data or []


def get_numerology_report(user_id: str, report_id: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
    """Retrieve a single saved numerology report by UUID, checking user ownership or admin privileges."""
    supabase = get_supabase_client()
    if not supabase:
        return None

    query = supabase.table("saved_numerology_reports").select("*").eq("id", report_id)
    if not is_admin:
        query = query.eq("user_id", user_id)

    res = query.execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None


def delete_numerology_report(user_id: str, report_id: str, is_admin: bool = False) -> bool:
    """Delete a saved numerology report by UUID."""
    supabase = get_supabase_client()
    if not supabase:
        return False

    query = supabase.table("saved_numerology_reports").delete().eq("id", report_id)
    if not is_admin:
        query = query.eq("user_id", user_id)

    res = query.execute()
    return bool(res.data and len(res.data) > 0)
