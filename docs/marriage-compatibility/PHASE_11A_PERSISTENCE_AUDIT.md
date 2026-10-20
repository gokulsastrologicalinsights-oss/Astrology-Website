# Gokul's Astrological Insights — Phase 11A.2: Final Persistence Design Gate for Saved Marriage Compatibility Reports

**Project Root:** `E:\GAI\Astrology Website`  
**Phase:** 11A.2 — Final Persistence Design Gate & Architecture Specification  
**Date:** 2026-10-19  
**Execution Boundary:** Strictly Read-Only Architecture Review & Specification. **Zero database migrations applied. Zero database tables altered. Zero application code modified.**

---

## Executive Summary

This document represents the definitive, sign-off architecture gate for persisting Saved Marriage Compatibility Reports in Gokul's Astrological Insights (GAI). Building upon the Phase 11A initial audit and Phase 11A.1 review, this Phase 11A.2 final design gate resolves all operational, concurrency, data integrity, and lifecycle questions prior to Phase 11B implementation:

1. **Display-Number Guarantees:** Establishes the exact mathematical and operational semantics of the advisory-locked sequential numbering mechanism, explicitly distinguishing concurrency safety from deletion reuse behavior.
2. **Snapshot & Calculation-Result Integrity:** Categorizes every column into immutable calculation snapshots vs. mutable user metadata, backed by a database-level trigger enforcing strict immutability.
3. **Timestamp & Deletion Lifecycle:** Defines the cascading semantics of account deletion (`auth.users(id) ON DELETE CASCADE`), individual report deletion, and foreign-key decoupling (`saved_horoscopes(id) ON DELETE SET NULL`).
4. **Migration-Readiness Blueprint:** Provides the complete SQL migration definition, rollback procedure, pre-migration verification checklist, and test matrix aligned with existing repository migrations (`20261017000001` through `20261018000009`).

---

## 1. Display-Number Guarantees & Concurrency Analysis

### 1.1 Existing Mechanism Inspection
In GAI's existing architecture (`saved_horoscopes`, `saved_kp_charts`, `saved_numerology_reports`, and `saved_vastu_reports`), per-user sequential numbering is implemented via a `BEFORE INSERT` trigger utilizing PostgreSQL transaction-level advisory locks:

```sql
CREATE OR REPLACE FUNCTION public.set_saved_marriage_compat_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        -- Acquire transaction-level exclusive advisory lock scoped to this specific user
        PERFORM pg_advisory_xact_lock(hashtext('saved_marriage_compat_' || NEW.user_id::text));
        
        -- Compute maximum display number for this user
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_marriage_compatibility_reports
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 1.2 Multi-Request Concurrency Safety
- **Lock Scope:** `pg_advisory_xact_lock` creates an exclusive lock identified by `hashtext('saved_marriage_compat_' || user_id::text)`. Because the key incorporates the `user_id`, operations for distinct users proceed fully in parallel with zero lock contention.
- **Race Condition Immunity:** When a user initiates two or more simultaneous save requests (e.g. rapid double-clicks or parallel automated requests), Transaction 2 blocks until Transaction 1 commits (or rolls back). Upon acquiring the lock, Transaction 2 evaluates `MAX(display_number)` against the newly committed row from Transaction 1.
- **Unique Constraint:** The composite constraint `UNIQUE (user_id, display_number)` provides guaranteed safety against duplicate numbering errors.

### 1.3 Deletion Behavior & Monotonicity (Honest Guarantees)
It is critical to document the exact mathematical guarantee provided by `COALESCE(MAX(display_number), 0) + 1` without exaggeration:

1. **Interior Hole Behavior (Non-Reuse):**
   - If a user has reports #1, #2, #3, and deletes report #2:
   - `MAX(display_number)` remains 3.
   - The next inserted report will be assigned #4.
   - **Interior holes are never backfilled or reused.**
2. **Tail Deletion Behavior (Reuse of Highest Number):**
   - If a user has reports #1, #2, #3, and deletes report #3 (the highest number):
   - `MAX(display_number)` drops to 2.
   - The next inserted report will be assigned #3.
   - **Deleting the highest display number permits reuse of that highest number.**
3. **Architectural Evaluation:**
   - *Option A (Repository-Standard MAX + 1 with Advisory Lock):* Matches all existing saved tables in GAI (`saved_horoscopes`, `saved_numerology_reports`, etc.). Does not require supplementary counter tables or sequence cleanup.
   - *Option B (Dedicated Counter Table `user_report_counters`):* Guarantees strict monotonicity across all deletions by maintaining an independent incrementing counter.
   - **Design Decision:** In alignment with all existing GAI modules and user expectations for personal dashboard item numbers, **Option A is adopted**. The honest contract is documented: *Display numbers are collision-free and sequential under concurrency; internal gaps are preserved; tail deletions allow the highest number to be recycled.*

---

## 2. Snapshot & Calculation-Result Integrity

### 2.1 Column Categorization: Immutable vs. Mutable

To maintain astrological integrity and legal compliance, the persisted record strictly separates calculation artifacts from user metadata:

| Column | Data Type | Mutability | Justification |
| :--- | :--- | :---: | :--- |
| `id` | `UUID` | **Immutable** | Primary key. |
| `user_id` | `UUID` | **Immutable** | Tenant boundary; transfer of report ownership is prohibited. |
| `display_number` | `INTEGER` | **Immutable** | Assigned sequentially on creation; cannot be altered. |
| `rule_system` | `TEXT` | **Immutable** | Calculation input defining evaluation engine rules. |
| `ayanamsa_id` | `INTEGER` | **Immutable** | Calculation parameter (e.g. Lahiri / KP). |
| `house_system_id` | `INTEGER` | **Immutable** | Calculation parameter (e.g. Placidus). |
| `include_kp` | `BOOLEAN` | **Immutable** | Calculation parameter for Sub-Lord analysis. |
| `include_timing` | `BOOLEAN` | **Immutable** | Calculation parameter for Dasa-Bhukti timing. |
| `overall_outcome` | `TEXT` | **Immutable** | Synthesized compatibility verdict. |
| `porutham_score` | `DOUBLE PRECISION` | **Immutable** | Calculated Tamil 10 Poruthams score. |
| `ashtakoota_points` | `DOUBLE PRECISION` | **Immutable** | Calculated North Indian Ashtakoota score. |
| `samadosham_status` | `TEXT` | **Immutable** | Calculated Kuja Dosha balance status. |
| `papasamya_verdict` | `TEXT` | **Immutable** | Calculated Papasamya dosha balance verdict. |
| `ruling_planets_agreement` | `TEXT` | **Immutable** | Calculated KP Ruling Planets agreement. |
| `report_data` | `JSONB` | **Immutable** | Complete, comprehensive calculation snapshot. |
| `engine_version` | `TEXT` | **Immutable** | Audit version of calculation engine. |
| `report_schema_version` | `TEXT` | **Immutable** | Audit version of JSON payload structure. |
| `groom_birth_date` | `DATE` | **Immutable** | Core birth record used in calculation. |
| `bride_birth_date` | `DATE` | **Immutable** | Core birth record used in calculation. |
| `groom_is_approximate` | `BOOLEAN` | **Immutable** | Sensitivity flag set at calculation time. |
| `bride_is_approximate` | `BOOLEAN` | **Immutable** | Sensitivity flag set at calculation time. |
| `created_at` | `TIMESTAMPTZ` | **Immutable** | Audit timestamp of report generation. |
| `title` | `TEXT` | **MUTABLE** | User-customizable label (e.g. "Arun & Priya Compatibility"). |
| `groom_name` | `TEXT` | **MUTABLE** | Display name formatting correction. |
| `bride_name` | `TEXT` | **MUTABLE** | Display name formatting correction. |
| `groom_saved_horoscope_id` | `UUID` | **MUTABLE** | Optional link; can be cleared or re-linked to an owned chart. |
| `bride_saved_horoscope_id` | `UUID` | **MUTABLE** | Optional link; can be cleared or re-linked to an owned chart. |
| `updated_at` | `TIMESTAMPTZ` | **AUTOMATIC** | Automatically updated to `NOW()` on permitted metadata edits. |

### 2.2 Database Trigger Protection Guard
To guarantee that calculation-derived columns cannot be altered under any circumstance (via API tampering, direct SQL update, or client-side manipulation), a dedicated `BEFORE UPDATE` trigger is enforced:

```sql
CREATE OR REPLACE FUNCTION public.protect_marriage_report_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    -- 1. Disallow transferring report ownership or changing display number
    IF NEW.user_id <> OLD.user_id THEN
        RAISE EXCEPTION 'Report ownership cannot be transferred.';
    END IF;
    IF NEW.display_number <> OLD.display_number THEN
        RAISE EXCEPTION 'Report display number cannot be modified.';
    END IF;
    IF NEW.created_at <> OLD.created_at THEN
        RAISE EXCEPTION 'Creation timestamp is immutable.';
    END IF;

    -- 2. Disallow modifying calculation parameters
    IF NEW.rule_system <> OLD.rule_system OR
       NEW.ayanamsa_id <> OLD.ayanamsa_id OR
       NEW.house_system_id <> OLD.house_system_id OR
       NEW.include_kp <> OLD.include_kp OR
       NEW.include_timing <> OLD.include_timing THEN
        RAISE EXCEPTION 'Calculation parameters are immutable once saved.';
    END IF;

    -- 3. Disallow modifying birth dates or approximate flags
    IF NEW.groom_birth_date <> OLD.groom_birth_date OR
       NEW.bride_birth_date <> OLD.bride_birth_date OR
       NEW.groom_is_approximate <> OLD.groom_is_approximate OR
       NEW.bride_is_approximate <> OLD.bride_is_approximate THEN
        RAISE EXCEPTION 'Birth particulars associated with a calculation are immutable.';
    END IF;

    -- 4. Disallow modifying calculation outcomes, scores, or engine snapshot
    IF NEW.overall_outcome <> OLD.overall_outcome OR
       NEW.porutham_score IS DISTINCT FROM OLD.porutham_score OR
       NEW.ashtakoota_points IS DISTINCT FROM OLD.ashtakoota_points OR
       NEW.samadosham_status IS DISTINCT FROM OLD.samadosham_status OR
       NEW.papasamya_verdict IS DISTINCT FROM OLD.papasamya_verdict OR
       NEW.ruling_planets_agreement IS DISTINCT FROM OLD.ruling_planets_agreement OR
       NEW.report_data <> OLD.report_data OR
       NEW.engine_version <> OLD.engine_version OR
       NEW.report_schema_version <> OLD.report_schema_version THEN
        RAISE EXCEPTION 'Calculation snapshots and outcome scores are immutable and cannot be edited.';
    END IF;

    -- 5. Automatically touch updated_at timestamp on permitted edits
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2.3 Linked Horoscope References & Integrity
- **Decoupled Lifecycle:** The foreign keys `groom_saved_horoscope_id` and `bride_saved_horoscope_id` reference `public.saved_horoscopes(id) ON DELETE SET NULL`.
- **Integrity Guarantee:** The compatibility report does not depend on dynamic joins with `saved_horoscopes` to render its evaluation. The complete birth profile and astrological coordinates are snapshotted in `report_data`. If the referenced natal chart is deleted by the user, PostgreSQL automatically sets the foreign key to `NULL`, leaving the report, its scores, and all diagnostic breakdowns 100% intact.
- **Re-linking:** Users may update the foreign key to link or unlink natal charts in their library, guarded by the ownership check trigger described in Section 3.

---

## 3. Security, Authorization & Ownership Validation

### 3.1 Dual-Layer Ownership Validation
To prevent cross-user horoscope reference injection (where User A supplies a valid UUID belonging to User B's saved horoscopes), ownership validation is enforced at both the API layer and the database layer:

1. **API / Service Layer:**
   Prior to insertion, if `groom_saved_horoscope_id` or `bride_saved_horoscope_id` is supplied:
   ```python
   # Verify ownership in public.saved_horoscopes
   candidate_ids = [gid for gid in [groom_id, bride_id] if gid]
   if candidate_ids:
       resp = supabase.table("saved_horoscopes").select("id, user_id").in_("id", candidate_ids).execute()
       for row in resp.data:
           if str(row["user_id"]) != str(current_user["id"]) and current_user.get("role") != "admin":
               raise HTTPException(status_code=403, detail="Forbidden: Cannot link a horoscope belonging to another user.")
   ```
2. **Database Trigger Guard (`trg_check_marriage_horoscope_ownership`):**
   ```sql
   CREATE OR REPLACE FUNCTION public.check_marriage_horoscope_ownership()
   RETURNS TRIGGER AS $$
   BEGIN
       IF NEW.groom_saved_horoscope_id IS NOT NULL THEN
           IF NOT EXISTS (
               SELECT 1 FROM public.saved_horoscopes 
               WHERE id = NEW.groom_saved_horoscope_id AND user_id = NEW.user_id
           ) THEN
               RAISE EXCEPTION 'Unauthorized: groom_saved_horoscope_id does not belong to the authenticated user.';
           END IF;
       END IF;

       IF NEW.bride_saved_horoscope_id IS NOT NULL THEN
           IF NOT EXISTS (
               SELECT 1 FROM public.saved_horoscopes 
               WHERE id = NEW.bride_saved_horoscope_id AND user_id = NEW.user_id
           ) THEN
               RAISE EXCEPTION 'Unauthorized: bride_saved_horoscope_id does not belong to the authenticated user.';
           END IF;
       END IF;

       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

### 3.2 Row Level Security (RLS) Policies
RLS is enabled on `public.saved_marriage_compatibility_reports`:
- **SELECT:** `auth.uid() = user_id OR public.is_admin()` (Users view only their own records; administrators may audit for support).
- **INSERT:** `auth.uid() = user_id` (Users may only create reports bound to their own authenticated ID).
- **UPDATE:** `auth.uid() = user_id` (Users may only modify metadata of their own reports, constrained by the immutability trigger).
- **DELETE:** `auth.uid() = user_id OR public.is_admin()` (Users may delete their own reports; administrators may delete any).

---

## 4. Lifecycle & Deletion Architecture

### 4.1 Account Deletion (Cascade)
- `user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE`.
- When a user profile is deleted via Supabase Auth or admin GDPR erasure, PostgreSQL automatically cascades and deletes all associated compatibility reports.

### 4.2 Report Deletion
- Deleting a saved report permanently purges the relational row and its embedded JSONB snapshot.
- Due to the advisory lock mechanism, deleting an interior report creates a permanent hole, while deleting the highest report resets the maximum display number.

### 4.3 Referenced Natal Chart Deletion
- When a referenced horoscope in `public.saved_horoscopes` is deleted, `ON DELETE SET NULL` executes cleanly without cascading to the marriage report.

---

## 5. Support for Single-Tradition & Partial Evaluations

### 5.1 Real-World Request Modes
The Phase 8 engine and Phase 9 API support flexible evaluation combinations:
1. `rule_system = "tamil_porutham"`: Evaluates only Tamil 10 Poruthams. Ashtakoota is `None` / `null`.
2. `rule_system = "ashtakoota"`: Evaluates only North Indian Ashtakoota. Tamil Porutham is `None` / `null`.
3. `include_kp = false`: KP 7th CSL evaluation is skipped. `kp_marriage` is `None` / `null`.
4. Approximate time: Sub-Lord or Navamsa timing may be marked `INDETERMINATE`.

### 5.2 Nullable Score Constraints
To prevent schema failures on partial evaluations, score and verdict columns must remain nullable, with valid range checks applied when non-null:

```sql
porutham_score DOUBLE PRECISION NULL CHECK (
    porutham_score IS NULL OR (porutham_score >= 0.0 AND porutham_score <= 10.0)
),
ashtakoota_points DOUBLE PRECISION NULL CHECK (
    ashtakoota_points IS NULL OR (ashtakoota_points >= 0.0 AND ashtakoota_points <= 36.0)
),
samadosham_status TEXT NULL,
papasamya_verdict TEXT NULL,
ruling_planets_agreement TEXT NULL
```
- No artificial default scores (e.g. 0.0) are injected when a tradition is skipped. The column stores SQL `NULL`.

---

## 6. Migration Blueprint & Rollback Plan

### 6.1 Proposed Migration Script
**Target Migration:** `backend/migrations/20261019000001_create_saved_marriage_compatibility_reports.sql` and `supabase/migrations/20261019000001_create_saved_marriage_compatibility_reports.sql`

```sql
-- Gokul's Astrological Insights - Saved Marriage Compatibility Reports
-- Migration: 20261019000001_create_saved_marriage_compatibility_reports.sql
-- Description: Creates public.saved_marriage_compatibility_reports table, transactional advisory-locked sequential numbering, ownership triggers, immutability protection, and RLS policies.

CREATE TABLE IF NOT EXISTS public.saved_marriage_compatibility_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,

    -- User-Facing Metadata
    title TEXT NOT NULL CHECK (char_length(trim(title)) > 0),
    groom_name TEXT NOT NULL CHECK (char_length(trim(groom_name)) > 0),
    bride_name TEXT NOT NULL CHECK (char_length(trim(bride_name)) > 0),
    groom_birth_date DATE NOT NULL,
    bride_birth_date DATE NOT NULL,
    groom_is_approximate BOOLEAN NOT NULL DEFAULT FALSE,
    bride_is_approximate BOOLEAN NOT NULL DEFAULT FALSE,

    -- Optional Horoscope Linkage (Foreign key with cascade protection)
    groom_saved_horoscope_id UUID NULL REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL,
    bride_saved_horoscope_id UUID NULL REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL,

    -- Calculation Parameters
    rule_system TEXT NOT NULL DEFAULT 'all',
    ayanamsa_id INTEGER NOT NULL DEFAULT 0,
    house_system_id INTEGER NOT NULL DEFAULT 0,
    include_kp BOOLEAN NOT NULL DEFAULT TRUE,
    include_timing BOOLEAN NOT NULL DEFAULT TRUE,

    -- High-Level Outcomes (Nullable to support partial/single-tradition evaluation)
    overall_outcome TEXT NOT NULL CHECK (
        overall_outcome IN (
            'FAVOURABLE_UNDER_SELECTED_RULES',
            'MIXED_OR_CONDITIONAL',
            'UNFAVOURABLE_UNDER_SELECTED_RULES',
            'INDETERMINATE'
        )
    ),
    porutham_score DOUBLE PRECISION NULL CHECK (
        porutham_score IS NULL OR (porutham_score >= 0.0 AND porutham_score <= 10.0)
    ),
    ashtakoota_points DOUBLE PRECISION NULL CHECK (
        ashtakoota_points IS NULL OR (ashtakoota_points >= 0.0 AND ashtakoota_points <= 36.0)
    ),
    samadosham_status TEXT NULL,
    papasamya_verdict TEXT NULL,
    ruling_planets_agreement TEXT NULL,

    -- Immutable Detailed Snapshot
    report_data JSONB NOT NULL,
    engine_version TEXT NOT NULL DEFAULT '1.0.0',
    report_schema_version TEXT NOT NULL DEFAULT '1.0.0',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_saved_marriage_compat_user_display UNIQUE (user_id, display_number)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_saved_marriage_compat_user_id 
    ON public.saved_marriage_compatibility_reports (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_marriage_compat_user_created 
    ON public.saved_marriage_compatibility_reports (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_marriage_compat_outcome 
    ON public.saved_marriage_compatibility_reports (overall_outcome);
CREATE INDEX IF NOT EXISTS idx_saved_marriage_compat_groom_saved_id 
    ON public.saved_marriage_compatibility_reports (groom_saved_horoscope_id);
CREATE INDEX IF NOT EXISTS idx_saved_marriage_compat_bride_saved_id 
    ON public.saved_marriage_compatibility_reports (bride_saved_horoscope_id);

-- Concurrency-Safe Transactional Sequential Numbering Trigger
CREATE OR REPLACE FUNCTION public.set_saved_marriage_compat_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        PERFORM pg_advisory_xact_lock(hashtext('saved_marriage_compat_' || NEW.user_id::text));
        
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_marriage_compatibility_reports
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_marriage_compat_display_number ON public.saved_marriage_compatibility_reports;
CREATE TRIGGER trg_set_saved_marriage_compat_display_number
BEFORE INSERT ON public.saved_marriage_compatibility_reports
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_marriage_compat_display_number();

-- Cross-User Horoscope Ownership Trigger Guard
CREATE OR REPLACE FUNCTION public.check_marriage_horoscope_ownership()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.groom_saved_horoscope_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM public.saved_horoscopes 
            WHERE id = NEW.groom_saved_horoscope_id AND user_id = NEW.user_id
        ) THEN
            RAISE EXCEPTION 'Unauthorized: groom_saved_horoscope_id does not belong to the authenticated user.';
        END IF;
    END IF;

    IF NEW.bride_saved_horoscope_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM public.saved_horoscopes 
            WHERE id = NEW.bride_saved_horoscope_id AND user_id = NEW.user_id
        ) THEN
            RAISE EXCEPTION 'Unauthorized: bride_saved_horoscope_id does not belong to the authenticated user.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_marriage_horoscope_ownership ON public.saved_marriage_compatibility_reports;
CREATE TRIGGER trg_check_marriage_horoscope_ownership
BEFORE INSERT OR UPDATE ON public.saved_marriage_compatibility_reports
FOR EACH ROW
EXECUTE FUNCTION public.check_marriage_horoscope_ownership();

-- Immutable Snapshot Protection Trigger
CREATE OR REPLACE FUNCTION public.protect_marriage_report_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id <> OLD.user_id THEN
        RAISE EXCEPTION 'Report ownership cannot be transferred.';
    END IF;
    IF NEW.display_number <> OLD.display_number THEN
        RAISE EXCEPTION 'Report display number cannot be modified.';
    END IF;
    IF NEW.created_at <> OLD.created_at THEN
        RAISE EXCEPTION 'Creation timestamp is immutable.';
    END IF;

    IF NEW.rule_system <> OLD.rule_system OR
       NEW.ayanamsa_id <> OLD.ayanamsa_id OR
       NEW.house_system_id <> OLD.house_system_id OR
       NEW.include_kp <> OLD.include_kp OR
       NEW.include_timing <> OLD.include_timing THEN
        RAISE EXCEPTION 'Calculation parameters are immutable once saved.';
    END IF;

    IF NEW.groom_birth_date <> OLD.groom_birth_date OR
       NEW.bride_birth_date <> OLD.bride_birth_date OR
       NEW.groom_is_approximate <> OLD.groom_is_approximate OR
       NEW.bride_is_approximate <> OLD.bride_is_approximate THEN
        RAISE EXCEPTION 'Birth particulars associated with a calculation are immutable.';
    END IF;

    IF NEW.overall_outcome <> OLD.overall_outcome OR
       NEW.porutham_score IS DISTINCT FROM OLD.porutham_score OR
       NEW.ashtakoota_points IS DISTINCT FROM OLD.ashtakoota_points OR
       NEW.samadosham_status IS DISTINCT FROM OLD.samadosham_status OR
       NEW.papasamya_verdict IS DISTINCT FROM OLD.papasamya_verdict OR
       NEW.ruling_planets_agreement IS DISTINCT FROM OLD.ruling_planets_agreement OR
       NEW.report_data <> OLD.report_data OR
       NEW.engine_version <> OLD.engine_version OR
       NEW.report_schema_version <> OLD.report_schema_version THEN
        RAISE EXCEPTION 'Calculation snapshots and outcome scores are immutable and cannot be edited.';
    END IF;

    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_protect_marriage_report_snapshot ON public.saved_marriage_compatibility_reports;
CREATE TRIGGER trg_protect_marriage_report_snapshot
BEFORE UPDATE ON public.saved_marriage_compatibility_reports
FOR EACH ROW
EXECUTE FUNCTION public.protect_marriage_report_snapshot();

-- Row Level Security (RLS) Policies
ALTER TABLE public.saved_marriage_compatibility_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_marriage_compat_select_policy" ON public.saved_marriage_compatibility_reports;
CREATE POLICY "saved_marriage_compat_select_policy"
ON public.saved_marriage_compatibility_reports
FOR SELECT
USING (auth.uid() = user_id OR public.is_admin());

DROP POLICY IF EXISTS "saved_marriage_compat_insert_policy" ON public.saved_marriage_compatibility_reports;
CREATE POLICY "saved_marriage_compat_insert_policy"
ON public.saved_marriage_compatibility_reports
FOR INSERT
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "saved_marriage_compat_update_policy" ON public.saved_marriage_compatibility_reports;
CREATE POLICY "saved_marriage_compat_update_policy"
ON public.saved_marriage_compatibility_reports
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "saved_marriage_compat_delete_policy" ON public.saved_marriage_compatibility_reports;
CREATE POLICY "saved_marriage_compat_delete_policy"
ON public.saved_marriage_compatibility_reports
FOR DELETE
USING (auth.uid() = user_id OR public.is_admin());

GRANT ALL ON TABLE public.saved_marriage_compatibility_reports TO anon, authenticated, service_role;
```

### 6.2 Rollback Procedure
If rollback is ever required:
```sql
DROP TABLE IF EXISTS public.saved_marriage_compatibility_reports CASCADE;
DROP FUNCTION IF EXISTS public.set_saved_marriage_compat_display_number();
DROP FUNCTION IF EXISTS public.check_marriage_horoscope_ownership();
DROP FUNCTION IF EXISTS public.protect_marriage_report_snapshot();
```

---

## 7. Phase 11B Acceptance Test Matrix

Upon receiving authorization to implement Phase 11B, the implementation will be verified against the following comprehensive test suite:

| Test ID | Test Scenario | Expected Outcome |
| :--- | :--- | :--- |
| **TC-11B-01** | Save full compatibility report (`rule_system = "all"`) | HTTP 201 Created; sequential `display_number = 1`; all summary scores populated. |
| **TC-11B-02** | Save single-tradition report (`rule_system = "tamil_porutham"`) | HTTP 201 Created; `porutham_score` populated; `ashtakoota_points` stored as `NULL`. |
| **TC-11B-03** | Save single-tradition report (`rule_system = "ashtakoota"`) | HTTP 201 Created; `ashtakoota_points` populated; `porutham_score` stored as `NULL`. |
| **TC-11B-04** | Save report with `include_kp = false` | HTTP 201 Created; `ruling_planets_agreement` stored as `NULL`. |
| **TC-11B-05** | Unauthorized access (unauthenticated user) | HTTP 401 Unauthorized. |
| **TC-11B-06** | Cross-tenant isolation (User B attempts to fetch User A's report) | HTTP 404 or 403 Forbidden. |
| **TC-11B-07** | Cross-tenant deletion (User B attempts to delete User A's report) | HTTP 403 Forbidden; User A's report untouched. |
| **TC-11B-08** | Cross-user horoscope linking attempt (User A references User B's horoscope) | HTTP 403 Forbidden / trigger exception raised. |
| **TC-11B-09** | Update permitted metadata (Update `title`) | HTTP 200 OK; `title` updated; `updated_at` updated to `NOW()`. |
| **TC-11B-10** | Attempt to modify immutable calculation data (`porutham_score` or `report_data`) | HTTP 400/409/500 trigger exception: *Calculation snapshots and outcome scores are immutable*. |
| **TC-11B-11** | Referenced horoscope deletion | Referenced natal chart deleted in `saved_horoscopes`; foreign key becomes `NULL`; compatibility report remains fully intact. |
| **TC-11B-12** | Concurrent saves for identical user | Both requests succeed sequentially; display numbers assigned as `N` and `N+1` without race collision. |

---

## 8. Final Design Gate Status

- **Database State:** Unmodified.
- **Backend Application Code:** Unmodified.
- **Frontend Code:** Unmodified.
- **Migrations Applied:** None.
- **Status:** **Phase 11A.2 Design Gate Completed & Ready for Phase 11B Authorization.**
