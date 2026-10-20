"""Utility script to safely synchronize existing local Horoscope Writing records to Supabase.

Ensures:
1. No records are deleted or discarded during migration.
2. An automatic JSON backup is created before syncing.
3. Records are checked for pre-existence in Supabase to avoid duplicate key conflicts.
4. Preserves all original timestamps, UUIDs, calculation results, and overrides.
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Load environment
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

LOCAL_DATA_FILE = repo_dir / "data" / "saved_horoscope_writings.json"


def sync_local_to_supabase():
    print("=" * 70)
    print("SYNC LOCAL HOROSCOPE WRITING RECORDS TO SUPABASE")
    print("=" * 70)

    if not LOCAL_DATA_FILE.exists():
        print(f"[INFO] No local records file found at: {LOCAL_DATA_FILE}")
        return

    with open(LOCAL_DATA_FILE, "r", encoding="utf-8") as f:
        try:
            local_records = json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not parse local records: {e}")
            return

    if not local_records:
        print("[INFO] Local records file is empty. No records to sync.")
        return

    print(f"[INFO] Found {len(local_records)} local records to inspect.")

    supabase = get_supabase_client()
    if not supabase:
        print("[ERROR] Could not initialize Supabase client.")
        return

    # Check remote table existence
    try:
        supabase.table("saved_horoscope_writings").select("id").limit(1).execute()
    except Exception as e:
        print(f"[BLOCKED] Remote table 'saved_horoscope_writings' is not available in Supabase: {e}")
        print("Please apply the migration first before running sync.")
        return

    # Create local backup before performing any sync operations
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = repo_dir / "data" / f"saved_horoscope_writings.backup_{timestamp_str}.json"
    shutil.copy2(LOCAL_DATA_FILE, backup_file)
    print(f"[BACKUP] Safe local backup created at: {backup_file.name}")

    synced_count = 0
    skipped_count = 0

    for rec in local_records:
        rec_id = rec.get("id")
        if not rec_id:
            continue

        # Check if record already exists remotely
        try:
            existing = supabase.table("saved_horoscope_writings").select("id").eq("id", rec_id).execute()
            if existing.data and len(existing.data) > 0:
                print(f"  - Record {rec_id} ({rec.get('person_name')}) already exists in Supabase. Skipping.")
                skipped_count += 1
                continue
        except Exception as err:
            print(f"  [WARN] Error checking existing record {rec_id}: {err}")

        # Insert record into Supabase
        db_payload = {
            "id": rec["id"],
            "user_id": rec["user_id"],
            "horoscope_id": rec.get("horoscope_id"),
            "person_name": rec.get("person_name", "Native"),
            "birth_date": rec.get("birth_date"),
            "birth_time": rec.get("birth_time"),
            "birth_place": rec.get("birth_place"),
            "latitude": rec.get("latitude"),
            "longitude": rec.get("longitude"),
            "timezone": rec.get("timezone", "Asia/Kolkata"),
            "panchanga_system": rec.get("panchanga_system", "thirukanitha"),
            "calculated_data": rec.get("calculated_data", {}),
            "overrides": rec.get("overrides", {}),
            "created_at": rec.get("created_at"),
            "updated_at": rec.get("updated_at"),
        }

        try:
            resp = supabase.table("saved_horoscope_writings").insert(db_payload).execute()
            if resp.data and len(resp.data) > 0:
                print(f"  + Record {rec_id} ({rec.get('person_name')}) successfully synced to Supabase!")
                synced_count += 1
            else:
                print(f"  [WARN] Insert for record {rec_id} did not return data.")
        except Exception as err:
            print(f"  [ERROR] Failed to insert record {rec_id} into Supabase: {err}")

    print("\n" + "=" * 70)
    print(f"SYNC SUMMARY: {synced_count} records migrated, {skipped_count} records already present.")
    print(f"Original local data preserved at: {LOCAL_DATA_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    sync_local_to_supabase()
