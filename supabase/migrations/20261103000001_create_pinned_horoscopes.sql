-- Gokul's Astrological Insights - Pinned Horoscopes
-- Migration: 20261103000001_create_pinned_horoscopes.sql
-- Description: Creates pinned_horoscopes table for pinning preferred charts to the top of dashboard and open saved charts.

CREATE TABLE IF NOT EXISTS public.pinned_horoscopes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    horoscope_id UUID NOT NULL REFERENCES public.saved_horoscopes(id) ON DELETE CASCADE,
    pinned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pinned_horoscopes_user_horoscope UNIQUE (user_id, horoscope_id)
);

CREATE INDEX IF NOT EXISTS idx_pinned_horoscopes_user_id ON public.pinned_horoscopes (user_id);
CREATE INDEX IF NOT EXISTS idx_pinned_horoscopes_pinned_at ON public.pinned_horoscopes (pinned_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.pinned_horoscopes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "pinned_horoscopes_select_policy" ON public.pinned_horoscopes;
DROP POLICY IF EXISTS "pinned_horoscopes_insert_policy" ON public.pinned_horoscopes;
DROP POLICY IF EXISTS "pinned_horoscopes_delete_policy" ON public.pinned_horoscopes;

CREATE POLICY "pinned_horoscopes_select_policy" ON public.pinned_horoscopes
FOR SELECT USING (
    (auth.role() = 'authenticated' AND (user_id = auth.uid() OR public.is_admin()))
);

CREATE POLICY "pinned_horoscopes_insert_policy" ON public.pinned_horoscopes
FOR INSERT WITH CHECK (
    (auth.role() = 'authenticated' AND user_id = auth.uid())
);

CREATE POLICY "pinned_horoscopes_delete_policy" ON public.pinned_horoscopes
FOR DELETE USING (
    (auth.role() = 'authenticated' AND (user_id = auth.uid() OR public.is_admin()))
);
