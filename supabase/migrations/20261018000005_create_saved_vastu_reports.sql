-- Gokul's Astrological Insights - Vastu Shastra Module Database Migration
-- Migration: 20261018000005_create_saved_vastu_reports.sql
-- Description: Creates public.saved_vastu_reports table, transactional advisory-locked sequential numbering, and RLS policies.

CREATE TABLE IF NOT EXISTS public.saved_vastu_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,
    property_name TEXT NOT NULL CHECK (char_length(trim(property_name)) > 0),
    property_type TEXT NOT NULL DEFAULT 'residential' CHECK (property_type IN ('residential', 'commercial', 'plot', 'industrial')),
    facing_direction TEXT NOT NULL CHECK (facing_direction IN ('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')),
    facing_degrees DOUBLE PRECISION CHECK (facing_degrees IS NULL OR (facing_degrees >= 0.0 AND facing_degrees < 360.0)),
    horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL,
    person_name TEXT,
    birth_date DATE,
    calculation_data JSONB NOT NULL,
    dosha_evaluations JSONB NOT NULL DEFAULT '[]'::jsonb,
    remedy_recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    compliance_score INTEGER NOT NULL CHECK (compliance_score >= 0 AND compliance_score <= 100),
    engine_version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_saved_vastu_user_display UNIQUE (user_id, display_number)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_saved_vastu_user_id ON public.saved_vastu_reports (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_vastu_created_at ON public.saved_vastu_reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_vastu_horoscope_id ON public.saved_vastu_reports (horoscope_id);
CREATE INDEX IF NOT EXISTS idx_saved_vastu_property_type ON public.saved_vastu_reports (property_type);

-- Concurrency-Safe Transactional Sequential Numbering Mechanism
-- Uses a transaction-level advisory lock scoped to the user_id to prevent numbering collisions
-- under concurrent requests, guaranteeing 1, 2, 3... per user without race conditions.
CREATE OR REPLACE FUNCTION public.set_saved_vastu_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        PERFORM pg_advisory_xact_lock(hashtext('saved_vastu_' || NEW.user_id::text));
        
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_vastu_reports
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_vastu_display_number ON public.saved_vastu_reports;
CREATE TRIGGER trg_set_saved_vastu_display_number
BEFORE INSERT ON public.saved_vastu_reports
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_vastu_display_number();

-- Row Level Security (RLS) Configuration
ALTER TABLE public.saved_vastu_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_vastu_select_policy" ON public.saved_vastu_reports;
DROP POLICY IF EXISTS "saved_vastu_insert_policy" ON public.saved_vastu_reports;
DROP POLICY IF EXISTS "saved_vastu_update_policy" ON public.saved_vastu_reports;
DROP POLICY IF EXISTS "saved_vastu_delete_policy" ON public.saved_vastu_reports;

-- Normal users can view only their own Vastu reports; admins can inspect all
CREATE POLICY "saved_vastu_select_policy"
ON public.saved_vastu_reports
FOR SELECT
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- Normal users can insert reports only for their own account
CREATE POLICY "saved_vastu_insert_policy"
ON public.saved_vastu_reports
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can update only their own reports
CREATE POLICY "saved_vastu_update_policy"
ON public.saved_vastu_reports
FOR UPDATE
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can delete only their own reports; admins can delete any
CREATE POLICY "saved_vastu_delete_policy"
ON public.saved_vastu_reports
FOR DELETE
USING (
    auth.uid() = user_id OR public.is_admin()
);

GRANT ALL ON TABLE public.saved_vastu_reports TO anon, authenticated, service_role;
