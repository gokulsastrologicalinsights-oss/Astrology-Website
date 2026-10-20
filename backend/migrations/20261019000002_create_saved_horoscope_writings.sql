-- Gokul's Astrological Insights - Traditional Tamil Horoscope Writing Module Database Migration
-- Migration: 20261019000002_create_saved_horoscope_writings.sql
-- Description: Creates public.saved_horoscope_writings table, indexes, and RLS policies.

CREATE TABLE IF NOT EXISTS public.saved_horoscope_writings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE SET NULL,
    person_name TEXT NOT NULL CHECK (char_length(trim(person_name)) > 0),
    birth_date DATE NOT NULL,
    birth_time TEXT NOT NULL CHECK (char_length(trim(birth_time)) > 0),
    birth_place TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    panchanga_system TEXT NOT NULL DEFAULT 'thirukanitha',
    calculated_data JSONB NOT NULL,
    overrides JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_saved_horoscope_writings_user_id ON public.saved_horoscope_writings (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_horoscope_writings_horoscope_id ON public.saved_horoscope_writings (horoscope_id);
CREATE INDEX IF NOT EXISTS idx_saved_horoscope_writings_created_at ON public.saved_horoscope_writings (created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.saved_horoscope_writings ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view own documents or admin can inspect all
DROP POLICY IF EXISTS "saved_horoscope_writings_select_policy" ON public.saved_horoscope_writings;
CREATE POLICY "saved_horoscope_writings_select_policy"
ON public.saved_horoscope_writings
FOR SELECT
USING (auth.uid() = user_id OR public.is_admin());

-- RLS Policy: Users can insert their own documents
DROP POLICY IF EXISTS "saved_horoscope_writings_insert_policy" ON public.saved_horoscope_writings;
CREATE POLICY "saved_horoscope_writings_insert_policy"
ON public.saved_horoscope_writings
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can update their own documents
DROP POLICY IF EXISTS "saved_horoscope_writings_update_policy" ON public.saved_horoscope_writings;
CREATE POLICY "saved_horoscope_writings_update_policy"
ON public.saved_horoscope_writings
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can delete their own documents or admin can delete any
DROP POLICY IF EXISTS "saved_horoscope_writings_delete_policy" ON public.saved_horoscope_writings;
CREATE POLICY "saved_horoscope_writings_delete_policy"
ON public.saved_horoscope_writings
FOR DELETE
USING (auth.uid() = user_id OR public.is_admin());

-- Grants
GRANT ALL ON TABLE public.saved_horoscope_writings TO anon, authenticated, service_role;
