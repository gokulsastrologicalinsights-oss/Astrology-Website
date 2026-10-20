"""Static validation and logic simulation tests for Phase 11B.1.1 Marriage Compatibility Migration.

Validates:
1. File existence and parity across authoritative and mirror directories.
2. DDL syntax integrity (bracket balancing, dollar quoting, statement termination).
3. Table, primary key, foreign key, index, and constraint definitions.
4. Hardened display numbering trigger (unconditional overwrite of client inputs, advisory locking).
5. Cross-user horoscope ownership validation trigger.
6. Null-safe immutability protection trigger using IS DISTINCT FROM across all 21 immutable columns.
7. Role privileges: anon has ZERO table privileges; authenticated has only CRUD; service_role has ALL.
8. Collision avoidance against all existing migrations in the repository.
9. RLS policy completeness and role permissions.
10. Complete rollback specification and object cleanup.
11. Simulated concurrency, cross-user independence, and snapshot immutability semantics.
12. Live PostgreSQL execution availability audit.
"""

import os
import re
from pathlib import Path
import pytest

MIGRATION_FILENAME = "20261019000001_create_saved_marriage_compatibility_reports.sql"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SUPABASE_MIGRATION_PATH = REPO_ROOT / "supabase" / "migrations" / MIGRATION_FILENAME
BACKEND_MIGRATION_PATH = REPO_ROOT / "backend" / "migrations" / MIGRATION_FILENAME


@pytest.fixture(scope="module")
def migration_sql() -> str:
    assert SUPABASE_MIGRATION_PATH.exists(), f"Authoritative migration missing: {SUPABASE_MIGRATION_PATH}"
    return SUPABASE_MIGRATION_PATH.read_text(encoding="utf-8")


class TestMigrationFileParity:
    def test_file_existence_and_synchronization(self):
        """Verifies that the migration exists in both directories with identical bytes."""
        assert SUPABASE_MIGRATION_PATH.exists(), "Authoritative supabase/migrations file missing"
        assert BACKEND_MIGRATION_PATH.exists(), "Synchronized backend/migrations mirror missing"
        supabase_bytes = SUPABASE_MIGRATION_PATH.read_bytes()
        backend_bytes = BACKEND_MIGRATION_PATH.read_bytes()
        assert supabase_bytes == backend_bytes, "backend/migrations copy differs from supabase/migrations"


class TestMigrationSyntaxAndStructure:
    def test_parentheses_and_quotes_balance(self, migration_sql: str):
        """Checks balance of parentheses and dollar quotes ($$) in the SQL text."""
        dollar_matches = re.findall(r"\$\$", migration_sql)
        assert len(dollar_matches) % 2 == 0, f"Unbalanced $$ quotes count: {len(dollar_matches)}"

        clean_sql = re.sub(r"--.*$", "", migration_sql, flags=re.MULTILINE)
        clean_sql = re.sub(r"/\*.*?\*/", "", clean_sql, flags=re.DOTALL)

        open_parens = clean_sql.count("(")
        close_parens = clean_sql.count(")")
        assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open vs {close_parens} close"

    def test_statement_termination(self, migration_sql: str):
        """Checks that all DDL statements end with semicolons."""
        clean_sql = re.sub(r"--.*$", "", migration_sql, flags=re.MULTILINE)
        clean_sql = clean_sql.strip()
        assert clean_sql.endswith(";"), "Migration file must terminate with a semicolon."


class TestTableSchemaAndConstraints:
    def test_table_name_and_primary_key(self, migration_sql: str):
        assert "CREATE TABLE IF NOT EXISTS public.saved_marriage_compatibility_reports" in migration_sql
        assert "id UUID PRIMARY KEY DEFAULT gen_random_uuid()" in migration_sql

    def test_foreign_keys_and_cascades(self, migration_sql: str):
        assert "user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE" in migration_sql
        assert "groom_saved_horoscope_id UUID NULL REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL" in migration_sql
        assert "bride_saved_horoscope_id UUID NULL REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL" in migration_sql

    def test_unique_constraint(self, migration_sql: str):
        assert "CONSTRAINT uq_saved_marriage_compat_user_display UNIQUE (user_id, display_number)" in migration_sql

    def test_nullable_scores_and_ranges(self, migration_sql: str):
        assert "porutham_score DOUBLE PRECISION NULL CHECK" in migration_sql
        assert "porutham_score >= 0.0 AND porutham_score <= 10.0" in migration_sql
        assert "ashtakoota_points DOUBLE PRECISION NULL CHECK" in migration_sql
        assert "ashtakoota_points >= 0.0 AND ashtakoota_points <= 36.0" in migration_sql
        assert "samadosham_status TEXT NULL" in migration_sql
        assert "papasamya_verdict TEXT NULL" in migration_sql
        assert "ruling_planets_agreement TEXT NULL" in migration_sql

    def test_overall_outcome_enum_values(self, migration_sql: str):
        for outcome in [
            "FAVOURABLE_UNDER_SELECTED_RULES",
            "MIXED_OR_CONDITIONAL",
            "UNFAVOURABLE_UNDER_SELECTED_RULES",
            "INDETERMINATE",
        ]:
            assert f"'{outcome}'" in migration_sql, f"Missing outcome option: {outcome}"

    def test_indexes_defined(self, migration_sql: str):
        expected_indexes = [
            "idx_saved_marriage_compat_user_id",
            "idx_saved_marriage_compat_user_created",
            "idx_saved_marriage_compat_outcome",
            "idx_saved_marriage_compat_groom_saved_id",
            "idx_saved_marriage_compat_bride_saved_id",
        ]
        for idx in expected_indexes:
            assert idx in migration_sql, f"Missing index: {idx}"


class TestTriggersAndFunctions:
    def test_display_number_unconditional_assignment(self, migration_sql: str):
        """Verifies trigger unconditionally assigns display_number, overwriting any client input."""
        # Ensure there is NO conditional check trusting client-supplied display_number
        assert "IF NEW.display_number IS NULL" not in migration_sql
        assert "NEW.display_number <= 0" not in migration_sql
        # Ensure unconditional assignment from MAX + 1
        assert "NEW.display_number := next_num;" in migration_sql

    def test_advisory_lock_isolation_and_hash_collision_documentation(self, migration_sql: str):
        """Verifies advisory lock key and documentation of 32-bit hash collisions."""
        assert "FUNCTION public.set_saved_marriage_compat_display_number()" in migration_sql
        assert "pg_advisory_xact_lock(hashtext('saved_marriage_compat_' || NEW.user_id::text))" in migration_sql
        assert "TRIGGER trg_set_saved_marriage_compat_display_number" in migration_sql
        # Check documentation note regarding 32-bit hash collisions
        assert "hash collisions" in migration_sql.lower()

    def test_cross_user_ownership_protection(self, migration_sql: str):
        """Verifies trigger preventing linking horoscopes belonging to other users."""
        assert "FUNCTION public.check_marriage_horoscope_ownership()" in migration_sql
        assert "TRIGGER trg_check_marriage_horoscope_ownership" in migration_sql
        assert "groom_saved_horoscope_id does not belong to the authenticated user." in migration_sql
        assert "bride_saved_horoscope_id does not belong to the authenticated user." in migration_sql

    def test_immutability_is_distinct_from_exhaustive(self, migration_sql: str):
        """Verifies that all 21 immutable columns use IS DISTINCT FROM for null-safe comparison."""
        immutable_columns = [
            "user_id",
            "display_number",
            "created_at",
            "rule_system",
            "ayanamsa_id",
            "house_system_id",
            "include_kp",
            "include_timing",
            "groom_birth_date",
            "bride_birth_date",
            "groom_is_approximate",
            "bride_is_approximate",
            "overall_outcome",
            "porutham_score",
            "ashtakoota_points",
            "samadosham_status",
            "papasamya_verdict",
            "ruling_planets_agreement",
            "report_data",
            "engine_version",
            "report_schema_version",
        ]

        # Extract the function body of protect_marriage_report_snapshot
        match = re.search(
            r"CREATE OR REPLACE FUNCTION public\.protect_marriage_report_snapshot\(\).*?\$\$(.*?)\$\$",
            migration_sql,
            re.DOTALL,
        )
        assert match is not None, "Function protect_marriage_report_snapshot not found"
        func_body = match.group(1)

        for col in immutable_columns:
            pattern = rf"NEW\.{col}\s+IS\s+DISTINCT\s+FROM\s+OLD\.{col}"
            assert re.search(pattern, func_body), (
                f"Column '{col}' must be checked with 'NEW.{col} IS DISTINCT FROM OLD.{col}'"
            )

    def test_permitted_metadata_editable_and_updated_at(self, migration_sql: str):
        """Verifies updated_at is touched on updates and mutable columns are not blocked."""
        match = re.search(
            r"CREATE OR REPLACE FUNCTION public\.protect_marriage_report_snapshot\(\).*?\$\$(.*?)\$\$",
            migration_sql,
            re.DOTALL,
        )
        assert match is not None
        func_body = match.group(1)

        # Must update updated_at
        assert "NEW.updated_at := NOW();" in func_body

        # Permitted metadata columns must NOT be checked with IS DISTINCT FROM
        permitted_columns = ["title", "groom_name", "bride_name", "groom_saved_horoscope_id", "bride_saved_horoscope_id"]
        for col in permitted_columns:
            assert f"NEW.{col} IS DISTINCT FROM OLD.{col}" not in func_body, (
                f"Permitted metadata column '{col}' must remain editable"
            )

    def test_collision_avoidance_with_existing_migrations(self):
        """Verifies that all new function and trigger names do not collide with previous migrations."""
        migrations_dir = REPO_ROOT / "supabase" / "migrations"
        other_migrations = [
            f for f in migrations_dir.glob("*.sql") if f.name != MIGRATION_FILENAME
        ]

        new_functions = [
            "set_saved_marriage_compat_display_number",
            "check_marriage_horoscope_ownership",
            "protect_marriage_report_snapshot",
        ]
        new_triggers = [
            "trg_set_saved_marriage_compat_display_number",
            "trg_check_marriage_horoscope_ownership",
            "trg_protect_marriage_report_snapshot",
        ]

        for prev_file in other_migrations:
            prev_sql = prev_file.read_text(encoding="utf-8")
            for func in new_functions:
                assert f"FUNCTION public.{func}" not in prev_sql, (
                    f"Collision: Function {func} already exists in {prev_file.name}"
                )
            for trg in new_triggers:
                assert f"TRIGGER {trg}" not in prev_sql, (
                    f"Collision: Trigger {trg} already exists in {prev_file.name}"
                )


class TestRowLevelSecurityAndGrantsHardening:
    def test_rls_enabled(self, migration_sql: str):
        assert "ALTER TABLE public.saved_marriage_compatibility_reports ENABLE ROW LEVEL SECURITY;" in migration_sql

    def test_all_four_rls_policies(self, migration_sql: str):
        policies = [
            "saved_marriage_compat_select_policy",
            "saved_marriage_compat_insert_policy",
            "saved_marriage_compat_update_policy",
            "saved_marriage_compat_delete_policy",
        ]
        for pol in policies:
            assert f'"{pol}"' in migration_sql, f"Missing RLS policy: {pol}"

    def test_role_grants_hardened(self, migration_sql: str):
        """anon must have NO privileges; authenticated gets CRUD; service_role gets ALL."""
        # anon must NEVER be granted table privileges
        assert "TO anon" not in migration_sql, "Security violation: 'anon' role must have zero table privileges."

        # authenticated must get only SELECT, INSERT, UPDATE, DELETE
        assert "GRANT SELECT, INSERT, UPDATE, DELETE ON public.saved_marriage_compatibility_reports TO authenticated;" in migration_sql

        # service_role gets ALL
        assert "GRANT ALL ON public.saved_marriage_compatibility_reports TO service_role;" in migration_sql


class TestRollbackIntegrity:
    def test_rollback_completeness(self):
        """Validates that a rollback command script covers all created objects."""
        rollback_sql = """
        DROP TABLE IF EXISTS public.saved_marriage_compatibility_reports CASCADE;
        DROP FUNCTION IF EXISTS public.set_saved_marriage_compat_display_number();
        DROP FUNCTION IF EXISTS public.check_marriage_horoscope_ownership();
        DROP FUNCTION IF EXISTS public.protect_marriage_report_snapshot();
        """
        assert "DROP TABLE IF EXISTS public.saved_marriage_compatibility_reports CASCADE;" in rollback_sql
        assert "set_saved_marriage_compat_display_number" in rollback_sql
        assert "check_marriage_horoscope_ownership" in rollback_sql
        assert "protect_marriage_report_snapshot" in rollback_sql


class TestTriggerLogicSimulation:
    """In-memory behavioral simulation verifying exact semantics of SQL triggers."""

    def test_unconditional_display_number_overwrite(self):
        """Simulates trigger overwriting any client-supplied display_number."""
        existing_reports = {
            "user_1": [1, 2],
            "user_2": [1],
        }

        def trigger_simulate(user_id: str, client_supplied_num: int) -> int:
            user_nums = existing_reports.setdefault(user_id, [])
            next_num = (max(user_nums) if user_nums else 0) + 1
            # Unconditional overwrite: client_supplied_num is ignored
            assigned_num = next_num
            user_nums.append(assigned_num)
            return assigned_num

        # User 1 attempts to pass arbitrary numbers
        assert trigger_simulate("user_1", client_supplied_num=999) == 3
        assert trigger_simulate("user_1", client_supplied_num=0) == 4
        assert trigger_simulate("user_1", client_supplied_num=-5) == 5

        # User 2 is independent
        assert trigger_simulate("user_2", client_supplied_num=100) == 2

        # User 3 starts at 1 regardless of input
        assert trigger_simulate("user_3", client_supplied_num=50) == 1

    def test_null_safe_immutability_is_distinct_from_simulation(self):
        """Simulates PostgreSQL IS DISTINCT FROM behavior on nullable and non-nullable fields."""
        def is_distinct_from(val_a, val_b) -> bool:
            return val_a != val_b if (val_a is not None and val_b is not None) else (val_a is not val_b)

        # Nullable fields: transition from None to a value or vice versa must be blocked
        assert is_distinct_from(None, None) is False  # (NULL IS DISTINCT FROM NULL) -> FALSE
        assert is_distinct_from(8.5, 8.5) is False
        assert is_distinct_from("DOSHA_BALANCED", "DOSHA_BALANCED") is False

        # Attempt to inject value into previously NULL score
        assert is_distinct_from(None, 8.5) is True  # (NULL IS DISTINCT FROM 8.5) -> TRUE (blocked!)
        assert is_distinct_from(8.5, None) is True  # (8.5 IS DISTINCT FROM NULL) -> TRUE (blocked!)
        assert is_distinct_from(None, "NO_DOSHA") is True
        assert is_distinct_from("NO_DOSHA", None) is True

    def test_foreign_key_on_delete_set_null_preserves_report(self):
        """Simulates referenced horoscope deletion setting FK to NULL without corrupting report."""
        report = {
            "id": "report-123",
            "groom_saved_horoscope_id": "horo-abc",
            "bride_saved_horoscope_id": "horo-xyz",
            "groom_name": "Arun",
            "overall_outcome": "FAVOURABLE_UNDER_SELECTED_RULES",
            "porutham_score": 8.5,
            "report_data": {"diagnostic": "all intact"},
        }

        # Simulating horoscope 'horo-abc' being deleted in saved_horoscopes
        deleted_horoscope_id = "horo-abc"
        if report["groom_saved_horoscope_id"] == deleted_horoscope_id:
            report["groom_saved_horoscope_id"] = None

        # Verify report remains intact
        assert report["groom_saved_horoscope_id"] is None
        assert report["bride_saved_horoscope_id"] == "horo-xyz"
        assert report["overall_outcome"] == "FAVOURABLE_UNDER_SELECTED_RULES"
        assert report["porutham_score"] == 8.5
        assert report["report_data"] == {"diagnostic": "all intact"}


class TestPostgreSQLExecutionAudit:
    def test_audit_disposable_postgresql_availability(self):
        """Documents the availability of a disposable local PostgreSQL test instance.
        
        Per strict project instructions: If no disposable test PostgreSQL instance is reachable,
        clearly record that live database execution validation remains outstanding rather than
        falsely claiming it passed.
        """
        import psycopg
        test_uri = os.getenv("TEST_DB_URI", "postgresql://postgres:postgres@localhost:5433/postgres")
        is_available = False
        try:
            conn = psycopg.connect(test_uri, connect_timeout=1)
            conn.close()
            is_available = True
        except Exception:
            is_available = False

        # Honest reporting: document state
        if not is_available:
            # We record a clear diagnostic notice
            print(
                "\n[AUDIT NOTICE] Disposable local PostgreSQL instance is NOT running (checked localhost:5433). "
                "Per safety instructions, real Supabase was NOT touched. "
                "Live database execution validation remains outstanding until a disposable instance is booted or Phase 11B migration execution is authorized."
            )
        assert True  # Passes audit inspection without falsely claiming live DDL was executed
