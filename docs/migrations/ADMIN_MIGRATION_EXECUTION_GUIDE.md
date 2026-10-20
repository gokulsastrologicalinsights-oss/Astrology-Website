# Staging Database Migration Execution Guide

**Project:** Gokul's Astrological Insights  
**Supabase Staging Project Reference:** `pcwiopxewlxhwvddpndq`  
**Direct Dashboard URL:** [https://supabase.com/dashboard/project/pcwiopxewlxhwvddpndq/sql/new](https://supabase.com/dashboard/project/pcwiopxewlxhwvddpndq/sql/new)  
**Authoritative Migration Files Directory:** `docs/migrations/`  

---

## 1. Safety Pre-Flight Verification

Before executing any SQL statements, the project administrator must verify:

1. **Target Project Identity:**
   - Confirm the Supabase project ID in your browser address bar is exactly: `pcwiopxewlxhwvddpndq`.
   - Never run this package against production (`release/d1-d9`) or unrelated projects.
2. **Current Schema State:**
   - Execute the following query in the SQL editor:
     ```sql
     SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
     ```
   - Current tables should be: `kp_event_analyses`, `profiles`, `saved_horoscopes`.
   - Verify existing saved horoscopes are intact:
     ```sql
     SELECT count(*) FROM public.saved_horoscopes;
     ```
3. **Execution Role:**
   - The Supabase Dashboard SQL Editor runs queries as the `postgres` superuser/database owner role, which has full DDL privileges.

---

## 2. Migration Execution Sequence

You may apply the migration package using either **Option A** (Consolidated Single Script) or **Option B** (Step-by-Step). Both options are 100% idempotent.

### Option A — Recommended: Single Consolidated Script
1. Open the Supabase Dashboard SQL Editor for `pcwiopxewlxhwvddpndq`.
2. Open [`docs/migrations/consolidated_staging_migration_package.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/consolidated_staging_migration_package.sql).
3. Copy the entire file content into the SQL Editor.
4. Click **Run**.
5. Ensure the result pane outputs `Success. No rows returned` or indicates transaction completion.

---

### Option B — Step-by-Step Individual Migrations

If preferred or if staged audit logs are required, execute the scripts sequentially:

| Step | Script File | Target Objects | Idempotency |
| :---: | :--- | :--- | :--- |
| **1** | [`01_20261018000006_create_customers_and_link_horoscopes.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/01_20261018000006_create_customers_and_link_horoscopes.sql) | `public.customers`, `public.customer_birthday_wishes`, `saved_horoscopes.customer_id` | `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS` |
| **2** | [`02_20261018000007_create_remedy_knowledge_base.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/02_20261018000007_create_remedy_knowledge_base.sql) | `remedy_source_references`, `remedies_problem_taxonomy`, `remedies_catalog`, `navagraha_temples` + Seeds | `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO UPDATE` |
| **3** | [`03_20261018000008_make_customer_phone_optional.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/03_20261018000008_make_customer_phone_optional.sql) | Drops `NOT NULL` on customer phone fields; installs partial unique index | `DO $$ BEGIN ... END $$` with `IF EXISTS` |
| **4** | [`04_20261018000009_create_remedy_reports.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/04_20261018000009_create_remedy_reports.sql) | `public.remedy_reports`, RLS policies & indexes | `CREATE TABLE IF NOT EXISTS`, `DROP POLICY IF EXISTS` |

> [!IMPORTANT]
> **Strict Halt Condition:** If any step produces a SQL syntax or constraint error, **STOP IMMEDIATELY**. Do not proceed to subsequent migrations. Report the exact error message and line number.

---

## 3. Post-Migration Verification

Immediately after execution, run the verification suite to confirm database state:

### Step 1: Execute SQL Verification Script
Copy and execute [`docs/migrations/POST_MIGRATION_VERIFICATION.sql`](file:///e:/GAI/Astrology%20Website/docs/migrations/POST_MIGRATION_VERIFICATION.sql) in the Supabase Dashboard SQL Editor.

Confirm the following criteria:
1. **Table Count:** Exactly 7 rows returned for new remedy and customer tables.
2. **Seed Counts:**
   - `remedy_source_references`: 7
   - `remedies_problem_taxonomy`: 39
   - `navagraha_temples`: 9
   - `remedies_catalog`: 31 (>= 30)
3. **RLS Enabled:** All 7 tables show `rls_enabled = true`.
4. **Phone Nullability:** Columns `phone_number`, `normalized_phone`, `whatsapp_number` all show `is_nullable = YES`.
5. **Data Preservation:** `saved_horoscopes` count is unchanged (no rows deleted).

---

### Step 2: Run Automated Application Persistence Test
From the project workspace terminal, run the automated verification script:
```powershell
.venv\Scripts\python.exe scripts/verify_remote_remedy_persistence.py
```
This script validates:
- Real round-trip `INSERT` into `public.remedy_reports`.
- Independent `SELECT` from a new HTTP session.
- Row-Level Security tenant isolation (unauthenticated 401, cross-user denial).
- Clean disposal of test records.

---

## 4. Rollback & Disaster Recovery Procedures

All four migrations are designed with non-destructive, non-breaking forward compatibility. If a rollback is explicitly required:

```sql
BEGIN;

-- Drop dependent remedy reports
DROP TABLE IF EXISTS public.remedy_reports CASCADE;

-- Drop knowledge base catalog and reference tables
DROP TABLE IF EXISTS public.remedies_catalog CASCADE;
DROP TABLE IF EXISTS public.remedies_problem_taxonomy CASCADE;
DROP TABLE IF EXISTS public.navagraha_temples CASCADE;
DROP TABLE IF EXISTS public.remedy_source_references CASCADE;

-- Drop birthday wishes
DROP TABLE IF EXISTS public.customer_birthday_wishes CASCADE;

-- Remove customer_id from saved_horoscopes without touching horoscope data
ALTER TABLE public.saved_horoscopes DROP COLUMN IF EXISTS customer_id;

-- Drop customers table
DROP TABLE IF EXISTS public.customers CASCADE;

COMMIT;
```
