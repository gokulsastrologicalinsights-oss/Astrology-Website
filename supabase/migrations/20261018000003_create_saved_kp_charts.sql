-- Gokul's Astrological Insights - Advanced KP Module Database Migration
-- Migration: 20261018000003_create_saved_kp_charts.sql
-- Description: Creates public.saved_kp_charts table, transactional advisory-locked sequential numbering, and RLS policies for Advanced KP and Horary Prashna.

CREATE TABLE IF NOT EXISTS public.saved_kp_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,
    chart_type TEXT NOT NULL CHECK (chart_type IN ('natal', 'horary')),
    title TEXT NOT NULL CHECK (char_length(trim(title)) > 0),

    -- Natal specifics (nullable for horary)
    birth_date DATE,
    birth_time TEXT,

    -- Horary specifics (nullable for natal)
    horary_number INTEGER CHECK (horary_number IS NULL OR (horary_number >= 1 AND horary_number <= 249)),
    question_text TEXT,
    question_date DATE,
    question_time TEXT,

    -- Shared location and ephemeris configuration
    location_name TEXT NOT NULL CHECK (char_length(trim(location_name)) > 0),
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    timezone TEXT NOT NULL CHECK (char_length(trim(timezone)) > 0),
    ayanamsa_id INTEGER NOT NULL DEFAULT 1,
    house_system_id INTEGER NOT NULL DEFAULT 2,

    -- Engine metadata & structured calculation snapshot
    engine_version TEXT NOT NULL DEFAULT '1.0.0',
    calculation_result JSONB NOT NULL,

    -- Optional foreign key linking to an existing saved horoscope
    saved_horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_saved_kp_charts_user_display UNIQUE (user_id, display_number)
);

CREATE INDEX IF NOT EXISTS idx_saved_kp_charts_user_id ON public.saved_kp_charts (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_kp_charts_created_at ON public.saved_kp_charts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_kp_charts_chart_type ON public.saved_kp_charts (chart_type);

-- Concurrency-Safe Transactional Sequential Numbering Mechanism
-- Uses a transaction-level advisory lock scoped to the user_id to prevent numbering collisions
-- under concurrent requests, guaranteeing 1, 2, 3... per user without SELECT COUNT(*) + 1 races.
CREATE OR REPLACE FUNCTION public.set_saved_kp_chart_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        PERFORM pg_advisory_xact_lock(hashtext('saved_kp_charts_' || NEW.user_id::text));

        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_kp_charts
        WHERE user_id = NEW.user_id;

        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_kp_chart_display_number ON public.saved_kp_charts;
CREATE TRIGGER trg_set_saved_kp_chart_display_number
BEFORE INSERT ON public.saved_kp_charts
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_kp_chart_display_number();

-- Row Level Security (RLS) Configuration
ALTER TABLE public.saved_kp_charts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_kp_charts_select_policy" ON public.saved_kp_charts;
DROP POLICY IF EXISTS "saved_kp_charts_insert_policy" ON public.saved_kp_charts;
DROP POLICY IF EXISTS "saved_kp_charts_update_policy" ON public.saved_kp_charts;
DROP POLICY IF EXISTS "saved_kp_charts_delete_policy" ON public.saved_kp_charts;

-- Select Policy: Users read their own records; Administrators read all records
CREATE POLICY "saved_kp_charts_select_policy" ON public.saved_kp_charts
FOR SELECT USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Insert Policy: Authenticated users can insert their own records
CREATE POLICY "saved_kp_charts_insert_policy" ON public.saved_kp_charts
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND user_id = auth.uid()
);

-- Update Policy: Users update their own records; Administrators can update any
CREATE POLICY "saved_kp_charts_update_policy" ON public.saved_kp_charts
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
) WITH CHECK (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Delete Policy: Users delete their own records; Administrators can delete any
CREATE POLICY "saved_kp_charts_delete_policy" ON public.saved_kp_charts
FOR DELETE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);
