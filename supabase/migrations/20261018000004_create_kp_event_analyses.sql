-- Gokul's Astrological Insights - KP Event Prediction Module Database Migration
-- Migration: 20261018000004_create_kp_event_analyses.sql
-- Description: Creates public.kp_event_analyses table, indexes, and RLS policies for KP Dasha-Bhukti event predictions.

CREATE TABLE IF NOT EXISTS public.kp_event_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE CASCADE,
    rule_set_version TEXT NOT NULL DEFAULT '1.0.0',
    input_data_fingerprint TEXT NOT NULL,
    calculation_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unique index to guarantee one active analysis record per horoscope per user
CREATE UNIQUE INDEX IF NOT EXISTS uq_kp_event_analyses_user_horoscope
ON public.kp_event_analyses (user_id, horoscope_id)
WHERE horoscope_id IS NOT NULL;

-- Secondary lookup indexes
CREATE INDEX IF NOT EXISTS idx_kp_event_analyses_user_id ON public.kp_event_analyses (user_id);
CREATE INDEX IF NOT EXISTS idx_kp_event_analyses_horoscope_id ON public.kp_event_analyses (horoscope_id);
CREATE INDEX IF NOT EXISTS idx_kp_event_analyses_fingerprint ON public.kp_event_analyses (input_data_fingerprint);
CREATE INDEX IF NOT EXISTS idx_kp_event_analyses_created_at ON public.kp_event_analyses (created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.kp_event_analyses ENABLE ROW LEVEL SECURITY;

-- Clean existing policies for idempotency
DROP POLICY IF EXISTS "kp_event_analyses_select_policy" ON public.kp_event_analyses;
DROP POLICY IF EXISTS "kp_event_analyses_insert_policy" ON public.kp_event_analyses;
DROP POLICY IF EXISTS "kp_event_analyses_update_policy" ON public.kp_event_analyses;
DROP POLICY IF EXISTS "kp_event_analyses_delete_policy" ON public.kp_event_analyses;

-- Select Policy: Users read only their own analyses; Administrators read all
CREATE POLICY "kp_event_analyses_select_policy" ON public.kp_event_analyses
FOR SELECT USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Insert Policy: Authenticated users can insert their own analyses
CREATE POLICY "kp_event_analyses_insert_policy" ON public.kp_event_analyses
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND user_id = auth.uid()
);

-- Update Policy: Users update their own analyses; Administrators update any
CREATE POLICY "kp_event_analyses_update_policy" ON public.kp_event_analyses
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
) WITH CHECK (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Delete Policy: Users delete their own analyses; Administrators delete any
CREATE POLICY "kp_event_analyses_delete_policy" ON public.kp_event_analyses
FOR DELETE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);
