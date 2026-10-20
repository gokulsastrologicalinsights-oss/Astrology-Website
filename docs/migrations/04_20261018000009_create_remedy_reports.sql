-- Gokul's Astrological Insights - Remedies & Pariharam Engine Migration
-- Migration: 20261018000009_create_remedy_reports.sql
-- Description: Creates public.remedy_reports table, indexes, and RLS policies for persisting astrologer-reviewed remedy reports.

CREATE TABLE IF NOT EXISTS public.remedy_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE CASCADE,
    person_name TEXT,
    input_data_fingerprint TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (review_status IN ('draft', 'reviewed', 'approved')),
    astrologer_notes TEXT,
    selected_remedy_codes TEXT[] NOT NULL DEFAULT '{}',
    language TEXT NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'ta')),
    analysis_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_remedy_reports_user_id ON public.remedy_reports (user_id);
CREATE INDEX IF NOT EXISTS idx_remedy_reports_horoscope_id ON public.remedy_reports (horoscope_id);
CREATE INDEX IF NOT EXISTS idx_remedy_reports_fingerprint ON public.remedy_reports (input_data_fingerprint);
CREATE INDEX IF NOT EXISTS idx_remedy_reports_created_at ON public.remedy_reports (created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.remedy_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "remedy_reports_select_policy" ON public.remedy_reports;
DROP POLICY IF EXISTS "remedy_reports_insert_policy" ON public.remedy_reports;
DROP POLICY IF EXISTS "remedy_reports_update_policy" ON public.remedy_reports;
DROP POLICY IF EXISTS "remedy_reports_delete_policy" ON public.remedy_reports;

-- Select Policy: Users read their own reports; Admins read all reports
CREATE POLICY "remedy_reports_select_policy" ON public.remedy_reports
FOR SELECT USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Insert Policy: Authenticated users can insert their own reports
CREATE POLICY "remedy_reports_insert_policy" ON public.remedy_reports
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND user_id = auth.uid()
);

-- Update Policy: Users update their own reports; Admins can update any
CREATE POLICY "remedy_reports_update_policy" ON public.remedy_reports
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
) WITH CHECK (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Delete Policy: Users delete their own reports; Admins can delete any
CREATE POLICY "remedy_reports_delete_policy" ON public.remedy_reports
FOR DELETE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Grants
GRANT SELECT, INSERT, UPDATE, DELETE ON public.remedy_reports TO authenticated;
GRANT ALL ON public.remedy_reports TO service_role;
