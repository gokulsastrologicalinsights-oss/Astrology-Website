-- Gokul's Astrological Insights - Customer Dasa-Bhukti Caution Alerts Tracking
-- Migration: 20261029000002_create_customer_dasa_caution_alerts.sql
-- Description: Creates customer_dasa_caution_alerts table for tracking astrologer notifications for adverse Dasa-Bhukti periods.

CREATE TABLE IF NOT EXISTS public.customer_dasa_caution_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE,
    horoscope_id UUID REFERENCES public.saved_horoscopes(id) ON DELETE CASCADE,
    dasa_lord TEXT NOT NULL,
    bhukti_lord TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT,
    severity TEXT NOT NULL DEFAULT 'high',
    sent_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for speedy lookups
CREATE INDEX IF NOT EXISTS idx_caution_alerts_customer_id ON public.customer_dasa_caution_alerts (customer_id);
CREATE INDEX IF NOT EXISTS idx_caution_alerts_horoscope_id ON public.customer_dasa_caution_alerts (horoscope_id);
CREATE INDEX IF NOT EXISTS idx_caution_alerts_sent_at ON public.customer_dasa_caution_alerts (sent_at DESC);

-- Unique index to prevent duplicate alerts for the same horoscope and period
CREATE UNIQUE INDEX IF NOT EXISTS uq_customer_caution_horo_period 
ON public.customer_dasa_caution_alerts (horoscope_id, dasa_lord, bhukti_lord, period_start);

-- Enable Row Level Security (RLS)
ALTER TABLE public.customer_dasa_caution_alerts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "caution_alerts_select_policy" ON public.customer_dasa_caution_alerts;
DROP POLICY IF EXISTS "caution_alerts_insert_policy" ON public.customer_dasa_caution_alerts;
DROP POLICY IF EXISTS "caution_alerts_update_policy" ON public.customer_dasa_caution_alerts;
DROP POLICY IF EXISTS "caution_alerts_delete_policy" ON public.customer_dasa_caution_alerts;

CREATE POLICY "caution_alerts_select_policy" ON public.customer_dasa_caution_alerts
FOR SELECT USING (
    (auth.role() = 'authenticated' AND (sent_by = auth.uid() OR sent_by IS NULL)) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

CREATE POLICY "caution_alerts_insert_policy" ON public.customer_dasa_caution_alerts
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated'
);

CREATE POLICY "caution_alerts_update_policy" ON public.customer_dasa_caution_alerts
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND sent_by = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

CREATE POLICY "caution_alerts_delete_policy" ON public.customer_dasa_caution_alerts
FOR DELETE USING (
    (auth.role() = 'authenticated' AND public.is_admin())
);
