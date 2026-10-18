"""Gokul's Astrological Insights - Secure Administrator Account Provisioning.

Idempotently provisions the initial administrator using trusted server-side Supabase credentials.
Never exposes credentials to the browser or logs secret keys or passwords.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("gai.bootstrap_admin")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def bootstrap_admin() -> Dict[str, Any]:
    """Idempotently bootstrap initial administrator.

    Returns:
        dict: Operation status and non-sensitive summary details.
    """
    admin_username = os.getenv("ADMIN_USERNAME", "").strip()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip()
    admin_password = os.getenv("ADMIN_INITIAL_PASSWORD", "").strip()
    supabase_url = (os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or "").strip()
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    # Check for missing configuration
    missing_vars = []
    if not admin_username:
        missing_vars.append("ADMIN_USERNAME")
    if not admin_email:
        missing_vars.append("ADMIN_EMAIL")
    if not admin_password:
        missing_vars.append("ADMIN_INITIAL_PASSWORD")
    if not supabase_url:
        missing_vars.append("SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL)")
    if not service_role_key:
        missing_vars.append("SUPABASE_SERVICE_ROLE_KEY")

    if missing_vars:
        msg = (
            f"Administrator account bootstrap skipped: Missing configuration for [{', '.join(missing_vars)}]. "
            "To provision an initial administrator, configure these in your secure environment. "
            "Refer to .env.example for required variable definitions."
        )
        logger.warning(msg)
        return {"status": "skipped", "reason": "missing_configuration", "missing": missing_vars}

    # Initialize Supabase Admin Client
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, service_role_key)
    except Exception as exc:
        logger.error(f"Failed to initialize Supabase client for admin bootstrap: {exc}")
        return {"status": "error", "error": "client_initialization_failed"}

    normalized_username = admin_username.lower().replace(" ", "_")
    display_name = admin_username

    # 1. Idempotency Check: Verify if an administrator already exists
    try:
        # Check by role
        existing_admins = (
            supabase.table("profiles")
            .select("id, username, display_name, role, must_change_password")
            .eq("role", "admin")
            .execute()
        )
        if existing_admins.data and len(existing_admins.data) > 0:
            existing_user = existing_admins.data[0]
            # Ensure display_name and username are up to date
            supabase.table("profiles").update({
                "display_name": display_name,
                "username": normalized_username,
                "must_change_password": False,
            }).eq("id", existing_user.get("id")).execute()

            logger.info(
                f"Administrator account already exists (username: {display_name}). "
                "Idempotency verified; no duplicate created."
            )
            return {
                "status": "already_exists",
                "username": display_name,
                "role": "admin",
                "must_change_password": False,
            }

        # Also check by username in profiles
        existing_profile = (
            supabase.table("profiles")
            .select("id, username, display_name, role, must_change_password")
            .or_(f"username.ilike.{normalized_username},display_name.ilike.{admin_username}")
            .execute()
        )
        if existing_profile.data and len(existing_profile.data) > 0:
            existing_user = existing_profile.data[0]
            logger.info(
                f"User profile with username '{display_name}' already exists with role '{existing_user.get('role')}'. "
                "Bootstrap completed."
            )
            return {
                "status": "already_exists",
                "username": display_name,
                "role": existing_user.get("role"),
                "must_change_password": False,
            }
    except Exception as exc:
        logger.error(f"Error querying existing profiles during bootstrap check: {exc}")
        return {"status": "error", "error": str(exc)}

    # 2. Provision initial administrator in Supabase Auth
    try:
        user_response = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True,
            "user_metadata": {
                "username": normalized_username,
                "display_name": display_name,
            },
        })

        if not user_response.user or not user_response.user.id:
            logger.error("Supabase auth admin did not return a valid user ID.")
            return {"status": "error", "error": "user_creation_failed"}

        admin_user_id = user_response.user.id

        # 3. Assign admin role and persist in profiles table
        supabase.table("profiles").upsert({
            "id": admin_user_id,
            "username": normalized_username,
            "display_name": display_name,
            "role": "admin",
            "must_change_password": False,
        }).execute()

        logger.info(
            f"Initial administrator successfully provisioned with username: {display_name}."
        )
        return {
            "status": "created",
            "username": display_name,
            "role": "admin",
            "must_change_password": False,
        }
    except Exception as exc:
        logger.error(f"Error provisioning administrator account: {exc}")
        return {"status": "error", "error": str(exc)}


if __name__ == "__main__":
    result = bootstrap_admin()
    print(f"Bootstrap result: {result.get('status')}")
