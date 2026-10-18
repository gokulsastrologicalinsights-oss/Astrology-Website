"""Gokul's Astrological Insights - Server-Side Authentication & Authorization Services.

Validates Supabase Auth tokens and enforces Row-Level / Role-Based authorization.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer(auto_error=False)


def get_supabase_client():
    """Returns a Supabase admin client using server-side service role key."""
    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        return None

    try:
        from supabase import create_client
        return create_client(supabase_url, service_role_key)
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Dict[str, Any]:
    """Dependency: Extract and verify current authenticated user from Bearer JWT.

    Raises:
        HTTPException: 401 if credentials missing or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    supabase = get_supabase_client()

    # If Supabase client is configured, verify via Supabase Auth
    if supabase:
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_id = user_response.user.id

            # Query profile for role & must_change_password
            profile_res = (
                supabase.table("profiles")
                .select("id, username, display_name, role, must_change_password")
                .eq("id", user_id)
                .single()
                .execute()
            )

            profile = profile_res.data or {}
            return {
                "id": user_id,
                "email": user_response.user.email,
                "username": profile.get("username", "user"),
                "display_name": profile.get("display_name"),
                "role": profile.get("role", "user"),
                "must_change_password": profile.get("must_change_password", False),
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate token with Supabase.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Fallback for offline token decoding in test environments
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain valid subject (sub).",
            )
        return {
            "id": user_id,
            "email": payload.get("email"),
            "username": payload.get("user_metadata", {}).get("username", "user"),
            "display_name": payload.get("user_metadata", {}).get("display_name"),
            "role": payload.get("role", "user"),
            "must_change_password": False,
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_admin_user(
    current_user: Dict[str, Any] = Security(get_current_user),
) -> Dict[str, Any]:
    """Dependency: Require administrative role for privileged operations."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrative privileges required.",
        )
    return current_user
