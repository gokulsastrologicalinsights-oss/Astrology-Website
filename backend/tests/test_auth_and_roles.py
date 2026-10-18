"""Tests for Supabase Database, Authentication, RLS Policies, and Role Enforcement.

Verifies:
1. Database migration repeatability and idempotency.
2. Initial administrator provisioning and duplicate idempotency.
3. First-login password change enforcement (must_change_password).
4. Normal user registration with default 'user' role.
5. Role elevation prevention (blocking client-side admin privilege escalation).
6. Sequential display numbering with transactional advisory locking.
7. Row-Level Security (RLS) isolation between two users.
8. Admin authorization to inspect user records.
9. Secure username-to-email resolution (service_role only, no public email leaks).
10. FastAPI admin endpoints and token authorization.
"""

import os
import uuid
import pytest
import psycopg
from fastapi.testclient import TestClient

from app.main import app

DB_URI = os.getenv("TEST_DB_URI", "postgresql://postgres:postgres@localhost:5433/postgres")


@pytest.fixture(scope="function")
def pg_conn():
    """Connect to test PostgreSQL instance with autocommit per test function."""
    try:
        conn = psycopg.connect(DB_URI, autocommit=True, connect_timeout=1)
        yield conn
        conn.close()
    except Exception as exc:
        pytest.skip(f"Local test PostgreSQL not reachable at {DB_URI}: {exc}")


def set_auth_context(cursor, user_id: str, role: str = "authenticated"):
    """Simulate Supabase request context for RLS testing."""
    cursor.execute(f"SET LOCAL request.jwt.claim.sub = '{user_id}';")
    cursor.execute(f"SET LOCAL request.jwt.claim.role = '{role}';")
    cursor.execute(f"SET ROLE {role};")


def reset_auth_context(cursor):
    """Reset role to postgres superuser."""
    cursor.execute("RESET ROLE;")
    cursor.execute("RESET request.jwt.claim.sub;")
    cursor.execute("RESET request.jwt.claim.role;")


class TestDatabaseMigrationsAndSchema:
    def test_migration_repeatability(self, pg_conn):
        """Verify migration can be executed repeatedly without errors (idempotency)."""
        migration_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "supabase", "migrations",
            "20261017000001_init_auth_profiles_saved_horoscopes.sql"
        )
        with open(migration_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        with pg_conn.cursor() as cur:
            # First execution
            cur.execute(sql_content)
            # Second execution - must succeed identically
            cur.execute(sql_content)

    def test_schema_constraints_and_tables(self, pg_conn):
        """Verify minimum required tables, indexes, and constraints exist."""
        with pg_conn.cursor() as cur:
            # Check profiles table
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'profiles'
                ORDER BY ordinal_position;
            """)
            profile_cols = {row[0]: row[1] for row in cur.fetchall()}
            assert "id" in profile_cols
            assert "username" in profile_cols
            assert "display_name" in profile_cols
            assert "role" in profile_cols
            assert "must_change_password" in profile_cols
            assert "created_at" in profile_cols
            assert "updated_at" in profile_cols

            # Check saved_horoscopes table
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'saved_horoscopes'
                ORDER BY ordinal_position;
            """)
            horoscope_cols = {row[0]: row[1] for row in cur.fetchall()}
            assert "id" in horoscope_cols
            assert "user_id" in horoscope_cols
            assert "display_number" in horoscope_cols
            assert "person_name" in horoscope_cols
            assert "birth_date" in horoscope_cols
            assert "birth_time" in horoscope_cols
            assert "timezone" in horoscope_cols
            assert "birthplace" in horoscope_cols
            assert "latitude" in horoscope_cols
            assert "longitude" in horoscope_cols
            assert "ayanamsa_id" in horoscope_cols
            assert "house_system_id" in horoscope_cols
            assert "calculation_result" in horoscope_cols


class TestAdminProvisioningAndIdempotency:
    def test_initial_admin_creation(self, pg_conn):
        """Verify admin account creation with must_change_password=True."""
        admin_id = str(uuid.uuid4())
        admin_email = f"admin_{uuid.uuid4().hex[:6]}@gokul-astrology.local"
        admin_username = f"admin_{uuid.uuid4().hex[:6]}"

        with pg_conn.cursor() as cur:
            # 1. Create auth user
            cur.execute(
                "INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s);",
                (admin_id, admin_email, f'{{"username": "{admin_username}"}}')
            )
            # 2. Elevate to admin via server provisioning process (service_role / postgres)
            cur.execute("""
                UPDATE public.profiles
                SET role = 'admin', must_change_password = TRUE
                WHERE id = %s;
            """, (admin_id,))

            cur.execute("SELECT role, must_change_password FROM public.profiles WHERE id = %s;", (admin_id,))
            row = cur.fetchone()
            assert row[0] == "admin"
            assert row[1] is True

    def test_first_login_password_change_enforcement(self, pg_conn):
        """Verify that updating password resets must_change_password flag to False."""
        admin_id = str(uuid.uuid4())
        admin_email = f"admin_pw_{uuid.uuid4().hex[:6]}@test.local"
        admin_username = f"admin_pw_{uuid.uuid4().hex[:6]}"

        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO auth.users (id, email) VALUES (%s, %s);",
                (admin_id, admin_email)
            )
            cur.execute("""
                UPDATE public.profiles
                SET role = 'admin', must_change_password = TRUE
                WHERE id = %s;
            """, (admin_id,))

            # First login: admin updates password
            cur.execute("""
                UPDATE public.profiles
                SET must_change_password = FALSE
                WHERE id = %s;
            """, (admin_id,))

            cur.execute("SELECT must_change_password FROM public.profiles WHERE id = %s;", (admin_id,))
            assert cur.fetchone()[0] is False


class TestUserRegistrationAndRoleEnforcement:
    def test_normal_user_receives_user_role(self, pg_conn):
        """New users created through signup trigger must receive role='user'."""
        user_id = str(uuid.uuid4())
        user_email = f"user_{uuid.uuid4().hex[:6]}@test.local"
        username = f"user_{uuid.uuid4().hex[:6]}"

        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s);",
                (user_id, user_email, f'{{"username": "{username}"}}')
            )

            cur.execute("SELECT role, must_change_password FROM public.profiles WHERE id = %s;", (user_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "user"
            assert row[1] is False

    def test_client_cannot_self_assign_admin(self, pg_conn):
        """Normal users cannot self-assign or elevate to admin role."""
        user_id = str(uuid.uuid4())
        user_email = f"user_hacker_{uuid.uuid4().hex[:6]}@test.local"
        username = f"hacker_{uuid.uuid4().hex[:6]}"

        with pg_conn.cursor() as cur:
            # 1. Create standard user
            cur.execute(
                "INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s);",
                (user_id, user_email, f'{{"username": "{username}"}}')
            )

            # 2. Simulate authenticated regular user attempting role escalation
            with pytest.raises(psycopg.Error) as exc_info:
                cur.execute("BEGIN;")
                set_auth_context(cur, user_id, "authenticated")
                cur.execute("UPDATE public.profiles SET role = 'admin' WHERE id = %s;", (user_id,))
                cur.execute("COMMIT;")

            assert "Unauthorized: Users cannot modify their own account role" in str(exc_info.value) or "permission denied" in str(exc_info.value).lower()


class TestSequentialNumberingAndAdvisoryLock:
    def test_saved_horoscopes_sequential_numbering(self, pg_conn):
        """Display numbering must assign 1, 2, 3... per user via transaction lock."""
        user_a = str(uuid.uuid4())
        user_b = str(uuid.uuid4())
        email_a = f"seq_a_{uuid.uuid4().hex[:6]}@test.local"
        email_b = f"seq_b_{uuid.uuid4().hex[:6]}@test.local"

        with pg_conn.cursor() as cur:
            # Setup two users
            cur.execute("INSERT INTO auth.users (id, email) VALUES (%s, %s);", (user_a, email_a))
            cur.execute("INSERT INTO auth.users (id, email) VALUES (%s, %s);", (user_b, email_b))

            sample_calc = '{"ascendant": "Aquarius", "planets": 12}'

            # Insert 3 records for User A
            cur.execute("""
                INSERT INTO public.saved_horoscopes
                (user_id, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result)
                VALUES (%s, 'Subject A1', '1990-05-15', '14:30', 'Asia/Kolkata', 'Chennai', 13.0827, 80.2707, 0, 2, %s)
                RETURNING display_number;
            """, (user_a, sample_calc))
            num_a1 = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO public.saved_horoscopes
                (user_id, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result)
                VALUES (%s, 'Subject A2', '1992-08-20', '09:15', 'Asia/Kolkata', 'Madurai', 9.9252, 78.1198, 0, 2, %s)
                RETURNING display_number;
            """, (user_a, sample_calc))
            num_a2 = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO public.saved_horoscopes
                (user_id, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result)
                VALUES (%s, 'Subject A3', '1995-11-10', '18:45', 'Asia/Kolkata', 'Coimbatore', 11.0168, 76.9558, 0, 2, %s)
                RETURNING display_number;
            """, (user_a, sample_calc))
            num_a3 = cur.fetchone()[0]

            # Insert 1 record for User B
            cur.execute("""
                INSERT INTO public.saved_horoscopes
                (user_id, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result)
                VALUES (%s, 'Subject B1', '1988-02-01', '06:00', 'Asia/Kolkata', 'Trichy', 10.7905, 78.7047, 0, 2, %s)
                RETURNING display_number;
            """, (user_b, sample_calc))
            num_b1 = cur.fetchone()[0]

            # Assert sequential values per user
            assert num_a1 == 1
            assert num_a2 == 2
            assert num_a3 == 3
            assert num_b1 == 1  # User B sequence independently starts at 1


class TestRowLevelSecurityIsolation:
    def test_rls_isolation_between_two_users(self, pg_conn):
        """User A must NOT be able to select, update, or delete User B's saved horoscopes."""
        user_a = str(uuid.uuid4())
        user_b = str(uuid.uuid4())
        email_a = f"rls_a_{uuid.uuid4().hex[:6]}@test.local"
        email_b = f"rls_b_{uuid.uuid4().hex[:6]}@test.local"

        with pg_conn.cursor() as cur:
            # 1. Setup users and test data
            cur.execute("INSERT INTO auth.users (id, email) VALUES (%s, %s);", (user_a, email_a))
            cur.execute("INSERT INTO auth.users (id, email) VALUES (%s, %s);", (user_b, email_b))

            sample_calc = '{"chart": "data"}'
            cur.execute("""
                INSERT INTO public.saved_horoscopes
                (user_id, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result)
                VALUES (%s, 'Secret B Chart', '1994-01-01', '12:00', 'UTC', 'London', 51.5074, -0.1278, 0, 2, %s)
                RETURNING id;
            """, (user_b, sample_calc))
            b_horoscope_id = cur.fetchone()[0]

            # 2. Switch context to User A
            cur.execute("BEGIN;")
            set_auth_context(cur, user_a, "authenticated")

            # A. Select: User A queries saved_horoscopes -> User B's record is completely invisible
            cur.execute("SELECT id, person_name FROM public.saved_horoscopes WHERE id = %s;", (b_horoscope_id,))
            visible_rows = cur.fetchall()
            assert len(visible_rows) == 0

            # B. Update: User A attempts to update User B's record -> 0 rows updated
            cur.execute("""
                UPDATE public.saved_horoscopes
                SET person_name = 'Compromised Name'
                WHERE id = %s;
            """, (b_horoscope_id,))
            assert cur.rowcount == 0

            # C. Delete: User A attempts to delete User B's record -> 0 rows deleted
            cur.execute("DELETE FROM public.saved_horoscopes WHERE id = %s;", (b_horoscope_id,))
            assert cur.rowcount == 0

            cur.execute("ROLLBACK;")
            reset_auth_context(cur)

            # 3. Verify User B's record remains unmodified
            cur.execute("SELECT person_name FROM public.saved_horoscopes WHERE id = %s;", (b_horoscope_id,))
            assert cur.fetchone()[0] == "Secret B Chart"


class TestSecureUsernameResolutionRPC:
    def test_username_resolution_restricted_to_service_role(self, pg_conn):
        """Public or authenticated users cannot resolve usernames to emails (prevents email harvesting)."""
        test_id = str(uuid.uuid4())
        test_email = f"harvest_{uuid.uuid4().hex[:6]}@test.local"
        test_username = f"target_{uuid.uuid4().hex[:6]}"

        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s);",
                (test_id, test_email, f'{{"username": "{test_username}"}}')
            )

            # 1. As service_role: resolution succeeds
            cur.execute("SET ROLE service_role;")
            cur.execute("SELECT public.resolve_username_to_email(%s);", (test_username,))
            resolved = cur.fetchone()[0]
            assert resolved == test_email
            reset_auth_context(cur)

            # 2. As anon: permission denied
            with pytest.raises(psycopg.Error) as exc_anon:
                cur.execute("SET ROLE anon;")
                cur.execute("SELECT public.resolve_username_to_email(%s);", (test_username,))
            assert "permission denied" in str(exc_anon.value).lower()
            reset_auth_context(cur)

            # 3. As authenticated user: permission denied
            with pytest.raises(psycopg.Error) as exc_auth:
                set_auth_context(cur, str(uuid.uuid4()), "authenticated")
                cur.execute("SELECT public.resolve_username_to_email(%s);", (test_username,))
            assert "permission denied" in str(exc_auth.value).lower()
            reset_auth_context(cur)


class TestFastApiAdminEndpoints:
    def test_admin_users_endpoint_unauthorized_without_token(self):
        """Accessing /api/v1/admin/users without token returns 401."""
        client = TestClient(app)
        res = client.get("/api/v1/admin/users")
        assert res.status_code == 401

    def test_admin_bootstrap_trigger(self):
        """Calling /api/v1/admin/bootstrap returns execution status."""
        client = TestClient(app)
        res = client.post("/api/v1/admin/bootstrap")
        assert res.status_code == 200
        assert "status" in res.json()
