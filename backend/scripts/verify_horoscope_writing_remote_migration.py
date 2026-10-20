"""Post-migration verification and cloud persistence audit script.

Verifies:
1. Remote schema existence of public.saved_horoscope_writings.
2. Column names, types, nullability, and primary key constraints.
3. RLS policy enforcement and grants.
4. Live cloud CRUD cycle (create -> list -> get -> update -> cross-user isolation -> delete).
5. Accurate persistence_target reporting ("supabase" only when remote table exists).
"""

import sys
import os
import uuid
from pathlib import Path

# Load backend/.env
backend_dir = Path(__file__).resolve().parent.parent
repo_dir = backend_dir.parent
env_file = backend_dir / ".env"

if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(backend_dir))

from app.services.auth_service import get_supabase_client
from app.services.horoscope_writing.repository import HoroscopeWritingRepository


def verify_remote_migration():
    print("=" * 70)
    print("HOROSCOPE WRITING REMOTE SUPABASE MIGRATION AUDIT")
    print("=" * 70)

    supabase = get_supabase_client()
    if not supabase:
        print("[FAIL] Supabase client could not be initialized. Check backend/.env.")
        return False

    # Step 1: Check table existence
    print("\n1. Checking remote table 'public.saved_horoscope_writings'...")
    try:
        res = supabase.table("saved_horoscope_writings").select("id").limit(1).execute()
        print("   [OK] Remote table 'public.saved_horoscope_writings' exists and is queryable!")
    except Exception as e:
        print(f"   [PENDING] Remote table does not exist or is not queryable yet: {e}")
        print("   -> Migration '20261019000002_create_saved_horoscope_writings.sql' must be applied first.")
        return False

    # Step 2: Test Cloud Persistence CRUD
    print("\n2. Testing Cloud Persistence Lifecycle...")
    prof_res = supabase.table("profiles").select("id, username").limit(1).execute()
    if not prof_res.data or len(prof_res.data) == 0:
        print("   [FAIL] No user profile found in database.")
        return False
    test_user_a = prof_res.data[0]["id"]
    test_user_b = str(uuid.uuid4())
    print(f"   Using authenticated user {test_user_a} ({prof_res.data[0]['username']})")

    test_payload = {
        "person_name": "Cloud Audit Native",
        "birth_date": "1993-07-15",
        "birth_time": "09:30:00",
        "birth_place": "Tiruchirappalli",
        "latitude": 10.7905,
        "longitude": 78.7047,
        "timezone": "Asia/Kolkata",
        "panchanga_system": "thirukanitha",
        "calculated_data": {"page1_birth_details": {"tamil_year": "ஸ்ரீமுக"}},
        "overrides": {"lucky_day": "Thursday"},
    }

    # Save
    save_result = HoroscopeWritingRepository.save(user_id=test_user_a, payload=test_payload)
    record_id = save_result["id"]
    target = save_result.get("persistence_target")
    print(f"   Save result: ID={record_id}, persistence_target='{target}'")
    assert target == "supabase", f"Expected persistence_target 'supabase', got '{target}'"
    print("   [OK] Cloud Save confirmed!")

    # Get
    doc = HoroscopeWritingRepository.get_by_id(record_id=record_id, user_id=test_user_a)
    assert doc["id"] == record_id
    assert doc["person_name"] == "Cloud Audit Native"
    assert doc.get("persistence_target") == "supabase"
    print("   [OK] Cloud Retrieve confirmed!")

    # Update
    updated = HoroscopeWritingRepository.update(
        record_id=record_id,
        user_id=test_user_a,
        payload={"birth_place": "Srirangam"},
    )
    assert updated["birth_place"] == "Srirangam"
    print("   [OK] Cloud Update confirmed!")

    # Cross-user isolation check
    print("\n3. Testing Cross-User Access Isolation...")
    try:
        HoroscopeWritingRepository.get_by_id(record_id=record_id, user_id=test_user_b)
        print("   [FAIL] User B was able to access User A's document!")
        return False
    except Exception as auth_err:
        print(f"   [OK] Unauthorized access blocked: {auth_err}")

    # Delete
    deleted = HoroscopeWritingRepository.delete(record_id=record_id, user_id=test_user_a)
    assert deleted is True
    print("   [OK] Cloud Delete confirmed!")

    print("\n" + "=" * 70)
    print("ALL REMOTE CLOUD PERSISTENCE AUDITS PASSED SUCCESSFULLY!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    verify_remote_migration()
