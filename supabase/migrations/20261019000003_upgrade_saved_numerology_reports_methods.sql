-- Gokul's Astrological Insights - Numerology Module Database Migration
-- Migration: 20261019000003_upgrade_saved_numerology_reports_methods.sql
-- Description: Idempotent and self-contained migration for public.saved_numerology_reports:
--              1. Ensures public.is_admin() helper function is defined safely with fixed search_path.
--              2. Creates table if not exists with all 12 required columns and 10 supported methods.
--              3. If table exists, safely upgrades method CHECK constraint to all 10 registered methods.
--              4. Configures advisory-locked display_number trigger for concurrency-safe ordering.
--              5. Configures Row Level Security (RLS) policies and least-privilege role grants.
-- Author: Antigravity AI Pair Programmer
-- Timestamp: 2026-10-19 18:30:00 UTC
-- Status: PREPARED (PENDING USER APPROVAL - NOT EXECUTED REMOTELY)

-- =============================================================================
-- Pre-Migration Verification Query (Run in Supabase SQL Editor to inspect current state):
-- SELECT 
--     EXISTS (
--         SELECT 1 FROM information_schema.tables 
--         WHERE table_schema = 'public' AND table_name = 'saved_numerology_reports'
--     ) AS table_exists,
--     COALESCE(
--         (SELECT pg_get_constraintdef(c.oid) 
--          FROM pg_constraint c 
--          JOIN pg_namespace n ON n.oid = c.connamespace 
--          WHERE c.conname = 'saved_numerology_reports_method_check' AND n.nspname = 'public'),
--         'NONE'
--     ) AS current_method_constraint,
--     EXISTS (
--         SELECT 1 FROM pg_proc p
--         JOIN pg_namespace n ON n.oid = p.pronamespace
--         WHERE n.nspname = 'public' AND p.proname = 'is_admin'
--     ) AS is_admin_function_exists;
-- =============================================================================

-- 1. Ensure public.is_admin() helper function exists and is hardened
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name = 'profiles'
    ) THEN
        RETURN FALSE;
    END IF;

    RETURN EXISTS (
        SELECT 1
        FROM public.profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE SET search_path = public;

GRANT EXECUTE ON FUNCTION public.is_admin() TO anon, authenticated, service_role;

-- 2. Idempotent Table Creation or Constraint Upgrade
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Branch A: Create table if not exists with all columns and upgraded 10-method constraint
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name = 'saved_numerology_reports'
    ) THEN
        CREATE TABLE public.saved_numerology_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            display_number INTEGER NOT NULL,
            person_name TEXT NOT NULL CHECK (char_length(trim(person_name)) > 0),
            birth_date DATE NOT NULL,
            method TEXT NOT NULL CONSTRAINT saved_numerology_reports_method_check CHECK (
                method IN (
                    'traditional',
                    'destiny_matrix',
                    'advanced',
                    'name_correction',
                    'business',
                    'phone',
                    'vehicle',
                    'property',
                    'marriage',
                    'family'
                )
            ),
            system_convention TEXT NOT NULL,
            calculation_data JSONB NOT NULL,
            interpretation_data JSONB NOT NULL,
            engine_version TEXT NOT NULL DEFAULT '1.0.0',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_saved_numerology_user_display UNIQUE (user_id, display_number)
        );
        RAISE NOTICE 'Table public.saved_numerology_reports created with all 10 supported methods.';
    ELSE
        -- Branch B: If table exists, safely upgrade the method CHECK constraint
        -- Drop standard named constraint if present
        ALTER TABLE public.saved_numerology_reports 
            DROP CONSTRAINT IF EXISTS saved_numerology_reports_method_check;

        -- Drop any legacy check constraint on method matching the old 3-method list or containing method_check
        FOR r IN (
            SELECT con.conname
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
            WHERE nsp.nspname = 'public'
              AND rel.relname = 'saved_numerology_reports'
              AND con.contype = 'c'
              AND (
                  pg_get_constraintdef(con.oid) ILIKE '%method%traditional%'
                  OR con.conname ILIKE '%method_check%'
              )
        ) LOOP
            EXECUTE 'ALTER TABLE public.saved_numerology_reports DROP CONSTRAINT IF EXISTS ' || quote_ident(r.conname);
        END LOOP;

        -- Add upgraded 10-method constraint
        ALTER TABLE public.saved_numerology_reports 
            ADD CONSTRAINT saved_numerology_reports_method_check 
            CHECK (method IN (
                'traditional',
                'destiny_matrix',
                'advanced',
                'name_correction',
                'business',
                'phone',
                'vehicle',
                'property',
                'marriage',
                'family'
            ));

        -- Ensure unique constraint exists on (user_id, display_number)
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
            WHERE nsp.nspname = 'public'
              AND rel.relname = 'saved_numerology_reports'
              AND con.conname = 'uq_saved_numerology_user_display'
        ) THEN
            ALTER TABLE public.saved_numerology_reports 
                ADD CONSTRAINT uq_saved_numerology_user_display UNIQUE (user_id, display_number);
        END IF;

        RAISE NOTICE 'Upgraded method CHECK constraint on existing public.saved_numerology_reports.';
    END IF;
END $$;

-- 3. Indexes for high-performance retrieval and ordering
CREATE INDEX IF NOT EXISTS idx_saved_numerology_user_id ON public.saved_numerology_reports (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_numerology_created_at ON public.saved_numerology_reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_numerology_method ON public.saved_numerology_reports (method);

-- 4. Concurrency-Safe Transactional Sequential Numbering Trigger
CREATE OR REPLACE FUNCTION public.set_saved_numerology_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        PERFORM pg_advisory_xact_lock(hashtext('saved_numerology_' || NEW.user_id::text));
        
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_numerology_reports
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_numerology_display_number ON public.saved_numerology_reports;
CREATE TRIGGER trg_set_saved_numerology_display_number
BEFORE INSERT ON public.saved_numerology_reports
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_numerology_display_number();

GRANT EXECUTE ON FUNCTION public.set_saved_numerology_display_number() TO authenticated, service_role;

-- 5. Row Level Security (RLS) Configuration
ALTER TABLE public.saved_numerology_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_numerology_select_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_insert_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_update_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_delete_policy" ON public.saved_numerology_reports;

-- Policy 1: SELECT (own reports or admin)
CREATE POLICY "saved_numerology_select_policy"
ON public.saved_numerology_reports
FOR SELECT
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- Policy 2: INSERT (own reports only)
CREATE POLICY "saved_numerology_insert_policy"
ON public.saved_numerology_reports
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
);

-- Policy 3: UPDATE (own reports only)
CREATE POLICY "saved_numerology_update_policy"
ON public.saved_numerology_reports
FOR UPDATE
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- Policy 4: DELETE (own reports or admin)
CREATE POLICY "saved_numerology_delete_policy"
ON public.saved_numerology_reports
FOR DELETE
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- 6. Role Permissions (Least-Privilege Security Design)
-- Revoke all permissions from anon to prevent unauthenticated table access
REVOKE ALL ON TABLE public.saved_numerology_reports FROM anon;

-- Grant standard CRUD only to authenticated users and service_role
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.saved_numerology_reports TO authenticated, service_role;

-- =============================================================================
-- Post-Migration Verification Query (Run in Supabase SQL Editor after execution):
-- SELECT 
--     c.conname AS constraint_name,
--     pg_get_constraintdef(c.oid) AS constraint_definition
-- FROM pg_constraint c 
-- JOIN pg_namespace n ON n.oid = c.connamespace 
-- WHERE c.conname = 'saved_numerology_reports_method_check' 
--   AND n.nspname = 'public';
--
-- Rollback Plan:
-- Option A: Revert CHECK constraint to legacy 3-method limitation
-- WARNING: This statement will FAIL if any rows with the 7 newer methods
-- ('name_correction', 'business', 'phone', 'vehicle', 'property', 'marriage', 'family')
-- exist in the table. Those rows must be backed up/archived and deleted prior to running:
-- -- DELETE FROM public.saved_numerology_reports WHERE method NOT IN ('traditional', 'destiny_matrix', 'advanced');
-- ALTER TABLE public.saved_numerology_reports DROP CONSTRAINT IF EXISTS saved_numerology_reports_method_check;
-- ALTER TABLE public.saved_numerology_reports ADD CONSTRAINT saved_numerology_reports_method_check 
--     CHECK (method IN ('traditional', 'destiny_matrix', 'advanced'));
--
-- Option B: Complete Table Drop (DESTRUCTIVE - IRREVERSIBLE DATA LOSS)
-- WARNING: Executing this will permanently delete the table and all saved user numerology reports:
-- -- DROP TABLE IF EXISTS public.saved_numerology_reports CASCADE;
-- =============================================================================
