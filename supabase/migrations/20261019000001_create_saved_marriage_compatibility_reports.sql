-- Gokul's Astrological Insights - Saved Marriage Compatibility Reports
-- Migration: 20261019000001_create_saved_marriage_compatibility_reports.sql
-- Description: Creates public.saved_marriage_compatibility_reports table, transactional advisory-locked sequential numbering, ownership triggers, immutability protection, and RLS policies.

-- 1. Table Definition
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

    -- Optional Horoscope Linkage (Foreign keys with cascade protection)
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

-- 2. Performance Indexes
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

-- 3. Concurrency-Safe Transactional Sequential Numbering Trigger
-- Uses a per-user advisory lock to serialize concurrent insertions by the same user.
-- Note: hashtext produces a 32-bit signed integer, so rare hash collisions between
-- unrelated users can cause benign temporary serialization, but never numbering errors.
CREATE OR REPLACE FUNCTION public.set_saved_marriage_compat_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    -- Acquire transaction-level advisory lock scoped to user_id
    PERFORM pg_advisory_xact_lock(hashtext('saved_marriage_compat_' || NEW.user_id::text));
    
    -- Always compute and assign the next sequential display number,
    -- unconditionally overwriting any client-supplied value.
    SELECT COALESCE(MAX(display_number), 0) + 1
    INTO next_num
    FROM public.saved_marriage_compatibility_reports
    WHERE user_id = NEW.user_id;
    
    NEW.display_number := next_num;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_marriage_compat_display_number ON public.saved_marriage_compatibility_reports;
CREATE TRIGGER trg_set_saved_marriage_compat_display_number
BEFORE INSERT ON public.saved_marriage_compatibility_reports
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_marriage_compat_display_number();

-- 4. Cross-User Horoscope Ownership Trigger Guard
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

-- 5. Immutable Snapshot Protection Trigger
CREATE OR REPLACE FUNCTION public.protect_marriage_report_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    -- Disallow changing ownership, display number, or creation timestamp
    IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
        RAISE EXCEPTION 'Report ownership cannot be transferred.';
    END IF;
    IF NEW.display_number IS DISTINCT FROM OLD.display_number THEN
        RAISE EXCEPTION 'Report display number cannot be modified.';
    END IF;
    IF NEW.created_at IS DISTINCT FROM OLD.created_at THEN
        RAISE EXCEPTION 'Creation timestamp is immutable.';
    END IF;

    -- Disallow modifying calculation parameters
    IF NEW.rule_system IS DISTINCT FROM OLD.rule_system OR
       NEW.ayanamsa_id IS DISTINCT FROM OLD.ayanamsa_id OR
       NEW.house_system_id IS DISTINCT FROM OLD.house_system_id OR
       NEW.include_kp IS DISTINCT FROM OLD.include_kp OR
       NEW.include_timing IS DISTINCT FROM OLD.include_timing THEN
        RAISE EXCEPTION 'Calculation parameters are immutable once saved.';
    END IF;

    -- Disallow modifying calculation birth records
    IF NEW.groom_birth_date IS DISTINCT FROM OLD.groom_birth_date OR
       NEW.bride_birth_date IS DISTINCT FROM OLD.bride_birth_date OR
       NEW.groom_is_approximate IS DISTINCT FROM OLD.groom_is_approximate OR
       NEW.bride_is_approximate IS DISTINCT FROM OLD.bride_is_approximate THEN
        RAISE EXCEPTION 'Birth particulars associated with a calculation are immutable.';
    END IF;

    -- Disallow modifying calculation scores, outcomes, or snapshot
    -- Null-safe comparison using IS DISTINCT FROM ensures nullable fields
    -- (porutham_score, ashtakoota_points, samadosham_status, papasamya_verdict,
    -- ruling_planets_agreement) cannot transition between NULL and any value.
    IF NEW.overall_outcome IS DISTINCT FROM OLD.overall_outcome OR
       NEW.porutham_score IS DISTINCT FROM OLD.porutham_score OR
       NEW.ashtakoota_points IS DISTINCT FROM OLD.ashtakoota_points OR
       NEW.samadosham_status IS DISTINCT FROM OLD.samadosham_status OR
       NEW.papasamya_verdict IS DISTINCT FROM OLD.papasamya_verdict OR
       NEW.ruling_planets_agreement IS DISTINCT FROM OLD.ruling_planets_agreement OR
       NEW.report_data IS DISTINCT FROM OLD.report_data OR
       NEW.engine_version IS DISTINCT FROM OLD.engine_version OR
       NEW.report_schema_version IS DISTINCT FROM OLD.report_schema_version THEN
        RAISE EXCEPTION 'Calculation snapshots, parameters, and outcome scores are immutable and cannot be edited.';
    END IF;

    -- Automatically update updated_at on permitted metadata edits
    -- (permitted fields: title, groom_name, bride_name, groom_saved_horoscope_id, bride_saved_horoscope_id)
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_protect_marriage_report_snapshot ON public.saved_marriage_compatibility_reports;
CREATE TRIGGER trg_protect_marriage_report_snapshot
BEFORE UPDATE ON public.saved_marriage_compatibility_reports
FOR EACH ROW
EXECUTE FUNCTION public.protect_marriage_report_snapshot();

-- 6. Row Level Security (RLS) Configuration
ALTER TABLE public.saved_marriage_compatibility_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_marriage_compat_select_policy" ON public.saved_marriage_compatibility_reports;
DROP POLICY IF EXISTS "saved_marriage_compat_insert_policy" ON public.saved_marriage_compatibility_reports;
DROP POLICY IF EXISTS "saved_marriage_compat_update_policy" ON public.saved_marriage_compatibility_reports;
DROP POLICY IF EXISTS "saved_marriage_compat_delete_policy" ON public.saved_marriage_compatibility_reports;

-- Select Policy: Users read their own reports; Admins read all reports
CREATE POLICY "saved_marriage_compat_select_policy"
ON public.saved_marriage_compatibility_reports
FOR SELECT
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- Insert Policy: Users insert reports only under their own authenticated user_id
CREATE POLICY "saved_marriage_compat_insert_policy"
ON public.saved_marriage_compatibility_reports
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
);

-- Update Policy: Users update their own reports (permitted metadata only, guarded by trigger)
CREATE POLICY "saved_marriage_compat_update_policy"
ON public.saved_marriage_compatibility_reports
FOR UPDATE
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- Delete Policy: Users delete their own reports; Admins can delete any report
CREATE POLICY "saved_marriage_compat_delete_policy"
ON public.saved_marriage_compatibility_reports
FOR DELETE
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- 7. Permissions & Grants
-- anon: Zero privileges. Anonymous visitors cannot read or write private compatibility reports.
-- authenticated: SELECT, INSERT, UPDATE, DELETE for user operations governed by RLS.
-- service_role: ALL privileges for administrative tasks, system migrations, and backend workers.
GRANT SELECT, INSERT, UPDATE, DELETE ON public.saved_marriage_compatibility_reports TO authenticated;
GRANT ALL ON public.saved_marriage_compatibility_reports TO service_role;
