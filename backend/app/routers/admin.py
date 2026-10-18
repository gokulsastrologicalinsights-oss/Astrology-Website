"""FastAPI Admin Router - Privileged Administrative Operations.

Access strictly guarded by role authorization dependencies.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth_service import get_admin_user, get_supabase_client
from app.bootstrap_admin import bootstrap_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users")
def list_users(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """List all registered user profiles (administrative inspection)."""
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not configured.",
        )

    try:
        res = (
            supabase.table("profiles")
            .select("id, username, display_name, role, must_change_password, created_at, updated_at")
            .order("created_at", desc=True)
            .execute()
        )
        return {"users": res.data or []}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user records from database.",
        )


@router.post("/bootstrap")
def trigger_bootstrap():
    """Trigger server-side administrative bootstrap check idempotently."""
    result = bootstrap_admin()
    return {"status": result.get("status"), "details": result}
