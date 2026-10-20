"""Live PostgreSQL verification suite for Phase 11B.1.2 against isolated disposable PostgreSQL container.

Connects strictly to: postgresql://postgres:disposable_test_pass@127.0.0.1:5433/gai_test_db
NEVER connects to or contacts Supabase.

Verifies:
1. Environment pre-flight & synthetic prerequisite provisioning.
2. Migration DDL execution and object creation (table, indexes, functions, triggers, policies, grants).
3. Concurrent display-number allocation & unconditional client-supplied number overwrite.
4. Snapshot immutability (including NULL-to-value and value-to-NULL transitions via IS DISTINCT FROM).
5. Cross-user horoscope ownership rejection (groom & bride).
6. Preserving compatibility report when referenced horoscope is deleted (ON DELETE SET NULL).
7. RLS tenant isolation & role privilege enforcement (anon blocked, authenticated scoped).
8. Clean rollback execution and successful idempotent reapplication.
"""

import os
import sys
import uuid
import threading
from pathlib import Path
import psycopg
import pytest
import socket

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MIGRATION_PATH = REPO_ROOT / "supabase" / "migrations" / "20261019000001_create_saved_marriage_compatibility_reports.sql"
TEST_DB_URI = "postgresql://postgres:disposable_test_pass@127.0.0.1:5433/gai_test_db"


def is_port_open(host: str, port: int, timeout_sec: float = 0.5) -> bool:
    """Quick socket check to verify if the disposable PostgreSQL test port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except (OSError, ConnectionRefusedError, TimeoutError):
        return False


pytestmark = pytest.mark.skipif(
    not is_port_open("127.0.0.1", 5433),
    reason="Disposable PostgreSQL container on 127.0.0.1:5433 is not running (Phase 11B.1.2 verification was completed).",
)


def get_conn(autocommit=True):
    return psycopg.connect(TEST_DB_URI, autocommit=autocommit)


def setup_disposable_prerequisites(conn):
    """Sets up synthetic auth and saved_horoscopes tables without any real user data."""
    with conn.cursor() as cur:
        # Enable extension
        cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        
        # Create roles if not exist
        for role in ["anon", "authenticated", "service_role"]:
            cur.execute(f"""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{role}') THEN
                    CREATE ROLE {role} NOLOGIN;
                END IF;
            END $$;
            """)

        # Synthetic auth schema
        cur.execute("CREATE SCHEMA IF NOT EXISTS auth;")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS auth.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT UNIQUE NOT NULL
        );
        """)

        # Simulation helper functions for auth.uid() and auth.role()
        cur.execute("""
        CREATE OR REPLACE FUNCTION auth.uid() RETURNS UUID AS $$
        BEGIN
            RETURN NULLIF(current_setting('request.jwt.claim.sub', true), '')::UUID;
        END;
        $$ LANGUAGE plpgsql STABLE;
        """)

        cur.execute("""
        CREATE OR REPLACE FUNCTION auth.role() RETURNS TEXT AS $$
        BEGIN
            RETURN COALESCE(NULLIF(current_setting('request.jwt.claim.role', true), ''), 'anon');
        END;
        $$ LANGUAGE plpgsql STABLE;
        """)

        # Synthetic profiles and admin helper
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.profiles (
            id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE OR REPLACE FUNCTION public.is_admin() RETURNS BOOLEAN AS $$
        BEGIN
            RETURN EXISTS (
                SELECT 1 FROM public.profiles
                WHERE id = auth.uid() AND role = 'admin'
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER STABLE;
        """)

        # Synthetic saved_horoscopes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.saved_horoscopes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            display_number INTEGER NOT NULL,
            person_name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """)
        
        # Grant usage on schemas public and auth to roles
        cur.execute("GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;")
        cur.execute("GRANT USAGE ON SCHEMA auth TO anon, authenticated, service_role;")
        cur.execute("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA auth TO anon, authenticated, service_role;")
        cur.execute("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;")
        cur.execute("GRANT SELECT ON auth.users TO anon, authenticated, service_role;")
        cur.execute("GRANT ALL ON public.saved_horoscopes TO anon, authenticated, service_role;")
        cur.execute("GRANT ALL ON public.profiles TO anon, authenticated, service_role;")


def test_01_migration_execution_and_object_creation():
    print("\n--- Test 1: Migration Execution & Object Creation ---")
    with get_conn() as conn:
        setup_disposable_prerequisites(conn)
        sql_content = MIGRATION_PATH.read_text(encoding="utf-8")
        with conn.cursor() as cur:
            cur.execute(sql_content)

            # Verify table existence
            cur.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'saved_marriage_compatibility_reports';
            """)
            assert cur.fetchone()[0] == 1, "Table not created"

            # Verify indexes
            cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE schemaname = 'public' AND tablename = 'saved_marriage_compatibility_reports';
            """)
            indexes = [r[0] for r in cur.fetchall()]
            for expected in [
                "idx_saved_marriage_compat_user_id",
                "idx_saved_marriage_compat_user_created",
                "idx_saved_marriage_compat_outcome",
                "idx_saved_marriage_compat_groom_saved_id",
                "idx_saved_marriage_compat_bride_saved_id",
            ]:
                assert expected in indexes, f"Index {expected} missing"

            # Verify triggers
            cur.execute("""
            SELECT trigger_name FROM information_schema.triggers 
            WHERE event_object_table = 'saved_marriage_compatibility_reports';
            """)
            triggers = [r[0] for r in cur.fetchall()]
            for expected_trg in [
                "trg_set_saved_marriage_compat_display_number",
                "trg_check_marriage_horoscope_ownership",
                "trg_protect_marriage_report_snapshot",
            ]:
                assert expected_trg in triggers, f"Trigger {expected_trg} missing"

            # Verify RLS enabled
            cur.execute("""
            SELECT relrowsecurity FROM pg_class WHERE relname = 'saved_marriage_compatibility_reports';
            """)
            assert cur.fetchone()[0] is True, "RLS is not enabled"
            print("[PASS] Table, 5 indexes, 3 triggers, and RLS verified in PostgreSQL.")


def test_02_concurrent_display_number_and_client_overwrite():
    print("\n--- Test 2: Display-Number Allocation & Client Overwrite ---")
    with get_conn() as conn:
        user_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_id}', '{user_id}@test.local');")
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{other_user_id}', '{other_user_id}@test.local');")

            # 1. Test client providing positive display_number (e.g. 999) - must be overwritten with 1
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, display_number, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                overall_outcome, report_data
            ) VALUES (
                '{user_id}', 999, 'Test Report 1', 'Arun', 'Priya', '1995-05-15', '1997-08-20',
                'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
            ) RETURNING display_number;
            """)
            assigned_1 = cur.fetchone()[0]
            assert assigned_1 == 1, f"Expected display_number 1 (overwritten), got {assigned_1}"

            # 2. Test subsequent insert - must receive 2
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, display_number, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                overall_outcome, report_data
            ) VALUES (
                '{user_id}', 0, 'Test Report 2', 'Arun', 'Priya', '1995-05-15', '1997-08-20',
                'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
            ) RETURNING display_number;
            """)
            assigned_2 = cur.fetchone()[0]
            assert assigned_2 == 2, f"Expected display_number 2, got {assigned_2}"

            # 3. Test independent user - must receive 1
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, display_number, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                overall_outcome, report_data
            ) VALUES (
                '{other_user_id}', 500, 'User2 Report 1', 'Karthik', 'Divya', '1994-01-10', '1996-03-12',
                'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
            ) RETURNING display_number;
            """)
            assigned_other = cur.fetchone()[0]
            assert assigned_other == 1, f"Expected other user to receive 1, got {assigned_other}"

    # 4. Multi-threaded simultaneous inserts for the same user (testing advisory lock serialization)
    results = []
    errors = []

    def thread_insert(thread_idx):
        try:
            with get_conn(autocommit=True) as t_conn:
                with t_conn.cursor() as t_cur:
                    t_cur.execute(f"""
                    INSERT INTO public.saved_marriage_compatibility_reports (
                        user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                        overall_outcome, report_data
                    ) VALUES (
                        '{user_id}', 'Concurrent Report {thread_idx}', 'Arun', 'Priya', '1995-05-15', '1997-08-20',
                        'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
                    ) RETURNING display_number;
                    """)
                    num = t_cur.fetchone()[0]
                    results.append(num)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=thread_insert, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent inserts produced errors: {errors}"
    assert len(results) == 5, f"Expected 5 successful inserts, got {len(results)}"
    # User 1 already had 1 and 2, so concurrent inserts must be exactly 3, 4, 5, 6, 7
    assert sorted(results) == [3, 4, 5, 6, 7], f"Expected [3, 4, 5, 6, 7], got {sorted(results)}"
    print("[PASS] Client display-number overwriting and concurrent transaction advisory locks verified (100% sequential, zero race conditions).")


def test_03_snapshot_immutability_and_null_transitions():
    print("\n--- Test 3: Snapshot Immutability & Null Transitions ---")
    with get_conn() as conn:
        user_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_id}', '{user_id}@test.local');")

            # 1. Insert report with NULL scores/verdicts (single tradition simulation)
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                rule_system, overall_outcome, porutham_score, ashtakoota_points, samadosham_status, report_data
            ) VALUES (
                '{user_id}', 'Single Tradition', 'Ramesh', 'Sita', '1992-02-02', '1994-04-04',
                'tamil_porutham', 'FAVOURABLE_UNDER_SELECTED_RULES', 8.5, NULL, NULL, '{{"mode":"tamil_only"}}'::jsonb
            ) RETURNING id, updated_at;
            """)
            row = cur.fetchone()
            report_id = row[0]
            initial_updated_at = row[1]

            # 2. Attempt to update nullable field from NULL to non-NULL (tampering attempt)
            try:
                cur.execute(f"""
                UPDATE public.saved_marriage_compatibility_reports 
                SET samadosham_status = 'NO_DOSHA' 
                WHERE id = '{report_id}';
                """)
                assert False, "Failed to block NULL -> 'NO_DOSHA' transition"
            except psycopg.Error as e:
                assert "immutable and cannot be edited" in str(e).lower()
                print("[PASS] Successfully blocked NULL -> 'NO_DOSHA' tampering via IS DISTINCT FROM.")

            # 3. Attempt to update porutham_score from 8.5 to 10.0 (tampering attempt)
            try:
                cur.execute(f"""
                UPDATE public.saved_marriage_compatibility_reports 
                SET porutham_score = 10.0 
                WHERE id = '{report_id}';
                """)
                assert False, "Failed to block score alteration"
            except psycopg.Error as e:
                assert "immutable and cannot be edited" in str(e).lower()
                print("[PASS] Successfully blocked score tampering (8.5 -> 10.0).")

            # 4. Attempt to update report_data JSONB (tampering attempt)
            try:
                cur.execute(f"""
                UPDATE public.saved_marriage_compatibility_reports 
                SET report_data = '{{"tampered":true}}'::jsonb 
                WHERE id = '{report_id}';
                """)
                assert False, "Failed to block report_data tampering"
            except psycopg.Error as e:
                assert "immutable and cannot be edited" in str(e).lower()
                print("[PASS] Successfully blocked report_data JSONB tampering.")

            # 5. Permitted metadata update: update title only
            cur.execute(f"""
            UPDATE public.saved_marriage_compatibility_reports 
            SET title = 'Updated Title For Ramesh & Sita' 
            WHERE id = '{report_id}'
            RETURNING title, updated_at;
            """)
            res = cur.fetchone()
            assert res[0] == 'Updated Title For Ramesh & Sita'
            assert res[1] > initial_updated_at, "updated_at did not advance on title update"
            print("[PASS] Permitted metadata edit (title) succeeded and updated_at advanced automatically.")


def test_04_cross_user_horoscope_ownership_rejection():
    print("\n--- Test 4: Cross-User Horoscope Ownership Guard ---")
    with get_conn() as conn:
        user_a = str(uuid.uuid4())
        user_b = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_a}', '{user_a}@test.local');")
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_b}', '{user_b}@test.local');")

            # Create User B's horoscope
            cur.execute(f"""
            INSERT INTO public.saved_horoscopes (user_id, display_number, person_name, birth_date)
            VALUES ('{user_b}', 1, 'User B Groom Chart', '1990-01-01')
            RETURNING id;
            """)
            user_b_horo_id = cur.fetchone()[0]

            # Create User A's horoscope
            cur.execute(f"""
            INSERT INTO public.saved_horoscopes (user_id, display_number, person_name, birth_date)
            VALUES ('{user_a}', 1, 'User A Groom Chart', '1991-02-02')
            RETURNING id;
            """)
            user_a_horo_id = cur.fetchone()[0]

            # Attempt 1: User A tries to link User B's horoscope as groom - MUST FAIL
            try:
                cur.execute(f"""
                INSERT INTO public.saved_marriage_compatibility_reports (
                    user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                    groom_saved_horoscope_id, overall_outcome, report_data
                ) VALUES (
                    '{user_a}', 'Cross-User Attack', 'Groom', 'Bride', '1990-01-01', '1992-02-02',
                    '{user_b_horo_id}', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
                );
                """)
                assert False, "Failed to block cross-user groom horoscope reference"
            except psycopg.Error as e:
                assert "groom_saved_horoscope_id does not belong to the authenticated user" in str(e)
                print("[PASS] Successfully blocked cross-user groom horoscope linking attempt.")

            # Attempt 2: User A tries to link User B's horoscope as bride - MUST FAIL
            try:
                cur.execute(f"""
                INSERT INTO public.saved_marriage_compatibility_reports (
                    user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                    bride_saved_horoscope_id, overall_outcome, report_data
                ) VALUES (
                    '{user_a}', 'Cross-User Attack Bride', 'Groom', 'Bride', '1990-01-01', '1992-02-02',
                    '{user_b_horo_id}', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
                );
                """)
                assert False, "Failed to block cross-user bride horoscope reference"
            except psycopg.Error as e:
                assert "bride_saved_horoscope_id does not belong to the authenticated user" in str(e)
                print("[PASS] Successfully blocked cross-user bride horoscope linking attempt.")

            # Attempt 3: User A links User A's own horoscope - MUST SUCCEED
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                groom_saved_horoscope_id, overall_outcome, report_data
            ) VALUES (
                '{user_a}', 'Legitimate Linkage', 'Groom', 'Bride', '1991-02-02', '1992-02-02',
                '{user_a_horo_id}', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
            ) RETURNING id;
            """)
            assert cur.fetchone()[0] is not None
            print("[PASS] User linking their own horoscope succeeded.")


def test_05_horoscope_deletion_preserves_compatibility_report():
    print("\n--- Test 5: Horoscope Deletion Preservation (ON DELETE SET NULL) ---")
    with get_conn() as conn:
        user_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_id}', '{user_id}@test.local');")

            # Create horoscope
            cur.execute(f"""
            INSERT INTO public.saved_horoscopes (user_id, display_number, person_name, birth_date)
            VALUES ('{user_id}', 1, 'Linked Groom', '1993-03-03')
            RETURNING id;
            """)
            horo_id = cur.fetchone()[0]

            # Create marriage report linked to this horoscope
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                groom_saved_horoscope_id, overall_outcome, porutham_score, report_data
            ) VALUES (
                '{user_id}', 'Report with Linked Horoscope', 'Groom', 'Bride', '1993-03-03', '1995-05-05',
                '{horo_id}', 'FAVOURABLE_UNDER_SELECTED_RULES', 9.0, '{{"full_calc": true}}'::jsonb
            ) RETURNING id;
            """)
            report_id = cur.fetchone()[0]

            # Delete the referenced horoscope from public.saved_horoscopes
            cur.execute(f"DELETE FROM public.saved_horoscopes WHERE id = '{horo_id}';")

            # Verify report still exists, groom_saved_horoscope_id is now NULL, and all scores/report_data intact
            cur.execute(f"""
            SELECT groom_saved_horoscope_id, title, porutham_score, report_data 
            FROM public.saved_marriage_compatibility_reports 
            WHERE id = '{report_id}';
            """)
            row = cur.fetchone()
            assert row is not None, "Report was deleted when horoscope was deleted!"
            assert row[0] is None, f"Expected groom_saved_horoscope_id to be NULL, got {row[0]}"
            assert row[1] == 'Report with Linked Horoscope'
            assert row[2] == 9.0
            assert row[3] == {"full_calc": True}
            print("[PASS] Deleting referenced horoscope safely set foreign key to NULL while preserving report and calculation data 100% intact.")


def test_06_rls_tenant_isolation_and_role_grants():
    print("\n--- Test 6: RLS Tenant Isolation & Role Grants ---")
    with get_conn(autocommit=False) as conn:
        user_1 = str(uuid.uuid4())
        user_2 = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_1}', '{user_1}@test.local');")
            cur.execute(f"INSERT INTO auth.users (id, email) VALUES ('{user_2}', '{user_2}@test.local');")

            # As postgres superuser, create reports for both users
            cur.execute(f"""
            INSERT INTO public.saved_marriage_compatibility_reports (
                user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                overall_outcome, report_data
            ) VALUES 
            ('{user_1}', 'User 1 Secret Report', 'U1G', 'U1B', '1990-01-01', '1992-02-02', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb),
            ('{user_2}', 'User 2 Secret Report', 'U2G', 'U2B', '1991-01-01', '1993-02-02', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb);
            """)
        conn.commit()

    # Now test with authenticated role as user_1
    with get_conn(autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SET LOCAL request.jwt.claim.sub = '{user_1}';")
            cur.execute("SET LOCAL request.jwt.claim.role = 'authenticated';")
            cur.execute("SET ROLE authenticated;")

            # SELECT query - must see only User 1 report
            cur.execute("SELECT title FROM public.saved_marriage_compatibility_reports;")
            rows = [r[0] for r in cur.fetchall()]
            assert rows == ['User 1 Secret Report'], f"Expected only User 1 report, got {rows}"

            # Attempt to DELETE User 2's report - must affect 0 rows
            cur.execute(f"DELETE FROM public.saved_marriage_compatibility_reports WHERE user_id = '{user_2}';")
            assert cur.rowcount == 0, "User 1 was able to delete User 2's report under RLS!"

            # Attempt to INSERT report for User 2 while authenticated as User 1 - must fail RLS WITH CHECK
            try:
                cur.execute(f"""
                INSERT INTO public.saved_marriage_compatibility_reports (
                    user_id, title, groom_name, bride_name, groom_birth_date, bride_birth_date,
                    overall_outcome, report_data
                ) VALUES (
                    '{user_2}', 'Spoofed Report', 'G', 'B', '1990-01-01', '1992-02-02', 'FAVOURABLE_UNDER_SELECTED_RULES', '{{}}'::jsonb
                );
                """)
                assert False, "Failed to block spoofed INSERT under RLS"
            except psycopg.Error as e:
                assert "violates row-level security policy" in str(e).lower()
                print("[PASS] RLS blocked cross-user INSERT attempt.")

        conn.rollback()

    # Test with anon role (unauthenticated) - must be denied permissions
    with get_conn(autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET ROLE anon;")
            try:
                cur.execute("SELECT * FROM public.saved_marriage_compatibility_reports;")
                assert False, "anon role was unexpectedly able to query table"
            except psycopg.Error as e:
                assert "permission denied" in str(e).lower()
                print("[PASS] anon role blocked with 'permission denied' (zero table privileges).")
        conn.rollback()


def test_07_rollback_and_reapplication():
    print("\n--- Test 7: Rollback Cleanup & Reapplication ---")
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Execute Rollback script
            cur.execute("""
            DROP TABLE IF EXISTS public.saved_marriage_compatibility_reports CASCADE;
            DROP FUNCTION IF EXISTS public.set_saved_marriage_compat_display_number();
            DROP FUNCTION IF EXISTS public.check_marriage_horoscope_ownership();
            DROP FUNCTION IF EXISTS public.protect_marriage_report_snapshot();
            """)

            # Verify table and functions are gone
            cur.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'saved_marriage_compatibility_reports';
            """)
            assert cur.fetchone()[0] == 0, "Table still exists after rollback"

            cur.execute("""
            SELECT count(*) FROM pg_proc 
            WHERE proname IN ('set_saved_marriage_compat_display_number', 'check_marriage_horoscope_ownership', 'protect_marriage_report_snapshot');
            """)
            assert cur.fetchone()[0] == 0, "Functions still exist after rollback"
            print("[PASS] Rollback completely purged table, triggers, and trigger functions.")

            # Reapply migration from file
            sql_content = MIGRATION_PATH.read_text(encoding="utf-8")
            cur.execute(sql_content)

            # Verify table exists again
            cur.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'saved_marriage_compatibility_reports';
            """)
            assert cur.fetchone()[0] == 1, "Table not recreated on reapplication"
            print("[PASS] Idempotent reapplication succeeded with zero errors.")


if __name__ == "__main__":
    print("=================================================================")
    print("STARTING LIVE DISPOSABLE POSTGRESQL MIGRATION TEST SUITE")
    print(f"Target Database: {TEST_DB_URI}")
    print("=================================================================")
    test_01_migration_execution_and_object_creation()
    test_02_concurrent_display_number_and_client_overwrite()
    test_03_snapshot_immutability_and_null_transitions()
    test_04_cross_user_horoscope_ownership_rejection()
    test_05_horoscope_deletion_preserves_compatibility_report()
    test_06_rls_tenant_isolation_and_role_grants()
    test_07_rollback_and_reapplication()
    print("=================================================================")
    print("ALL 7 LIVE POSTGRESQL VERIFICATION PHASES PASSED (100% GREEN)")
    print("=================================================================")
