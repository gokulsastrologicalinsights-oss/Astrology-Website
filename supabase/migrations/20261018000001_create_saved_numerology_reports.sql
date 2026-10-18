-- Gokul's Astrological Insights - Numerology Module Database Migration
-- Migration: 20261018000001_create_saved_numerology_reports.sql
-- Description: Creates public.saved_numerology_reports table, transactional advisory-locked sequential numbering, and RLS policies.

CREATE TABLE IF NOT EXISTS public.saved_numerology_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,
    person_name TEXT NOT NULL CHECK (char_length(trim(person_name)) > 0),
    birth_date DATE NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('traditional', 'destiny_matrix', 'advanced')),
    system_convention TEXT NOT NULL,
    calculation_data JSONB NOT NULL,
    interpretation_data JSONB NOT NULL,
    engine_version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_saved_numerology_user_display UNIQUE (user_id, display_number)
);

CREATE INDEX IF NOT EXISTS idx_saved_numerology_user_id ON public.saved_numerology_reports (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_numerology_created_at ON public.saved_numerology_reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_numerology_method ON public.saved_numerology_reports (method);

-- Concurrency-Safe Transactional Sequential Numbering Mechanism
-- Uses a transaction-level advisory lock scoped to the user_id to prevent numbering collisions
-- under concurrent requests, guaranteeing 1, 2, 3... per user without SELECT COUNT(*) + 1 races.
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

-- Row Level Security (RLS) Configuration
ALTER TABLE public.saved_numerology_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_numerology_select_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_insert_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_update_policy" ON public.saved_numerology_reports;
DROP POLICY IF EXISTS "saved_numerology_delete_policy" ON public.saved_numerology_reports;

-- Normal users can view only their own numerology reports; admins can inspect all
CREATE POLICY "saved_numerology_select_policy"
ON public.saved_numerology_reports
FOR SELECT
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- Normal users can insert reports only for their own account
CREATE POLICY "saved_numerology_insert_policy"
ON public.saved_numerology_reports
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can update only their own reports
CREATE POLICY "saved_numerology_update_policy"
ON public.saved_numerology_reports
FOR UPDATE
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can delete only their own reports; admins can also delete
CREATE POLICY "saved_numerology_delete_policy"
ON public.saved_numerology_reports
FOR DELETE
USING (
    auth.uid() = user_id OR public.is_admin()
);

GRANT ALL ON TABLE public.saved_numerology_reports TO anon, authenticated, service_role;
