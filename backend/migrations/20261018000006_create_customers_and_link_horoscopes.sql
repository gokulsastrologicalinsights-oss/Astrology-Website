-- Gokul's Astrological Insights - Customer Management & Mandatory Phone Integration
-- Migration: 20261018000006_create_customers_and_link_horoscopes.sql
-- Description: Creates public.customers and customer_birthday_wishes tables, links saved_horoscopes, and enforces RLS policies.

-- 1. Create public.customers table
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL CHECK (char_length(trim(full_name)) > 0),
    birth_date DATE NOT NULL,
    country_code TEXT NOT NULL DEFAULT '+91',
    phone_number TEXT NULL,
    normalized_phone TEXT NULL,
    whatsapp_number TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unique constraint ensuring an authoritative customer record per astrologer/user (when phone is provided)
CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_user_normalized_phone 
ON public.customers (user_id, normalized_phone)
WHERE normalized_phone IS NOT NULL AND normalized_phone <> '';

CREATE INDEX IF NOT EXISTS idx_customers_user_id ON public.customers (user_id);
CREATE INDEX IF NOT EXISTS idx_customers_birth_date ON public.customers (birth_date);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON public.customers (created_at DESC);

-- 2. Link saved_horoscopes to public.customers
ALTER TABLE public.saved_horoscopes
ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES public.customers(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_saved_horoscopes_customer_id ON public.saved_horoscopes (customer_id);

-- 3. Create public.customer_birthday_wishes table for manual status tracking
CREATE TABLE IF NOT EXISTS public.customer_birthday_wishes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
    wish_date DATE NOT NULL,
    sent_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_customer_wish_date UNIQUE (customer_id, wish_date)
);

CREATE INDEX IF NOT EXISTS idx_customer_wishes_date ON public.customer_birthday_wishes (wish_date);

-- 4. Enable Row Level Security (RLS) on new tables
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_birthday_wishes ENABLE ROW LEVEL SECURITY;

-- Clean existing policies for idempotency
DROP POLICY IF EXISTS "customers_select_policy" ON public.customers;
DROP POLICY IF EXISTS "customers_insert_policy" ON public.customers;
DROP POLICY IF EXISTS "customers_update_policy" ON public.customers;
DROP POLICY IF EXISTS "customers_delete_policy" ON public.customers;

DROP POLICY IF EXISTS "wishes_select_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_insert_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_update_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_delete_policy" ON public.customer_birthday_wishes;

-- Policies for public.customers
CREATE POLICY "customers_select_policy" ON public.customers
FOR SELECT USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

CREATE POLICY "customers_insert_policy" ON public.customers
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND user_id = auth.uid()
);

CREATE POLICY "customers_update_policy" ON public.customers
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
) WITH CHECK (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

CREATE POLICY "customers_delete_policy" ON public.customers
FOR DELETE USING (
    (auth.role() = 'authenticated' AND user_id = auth.uid()) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- Policies for public.customer_birthday_wishes
CREATE POLICY "wishes_select_policy" ON public.customer_birthday_wishes
FOR SELECT USING (
    auth.role() = 'authenticated'
);

CREATE POLICY "wishes_insert_policy" ON public.customer_birthday_wishes
FOR INSERT WITH CHECK (
    auth.role() = 'authenticated'
);

CREATE POLICY "wishes_update_policy" ON public.customer_birthday_wishes
FOR UPDATE USING (
    auth.role() = 'authenticated'
);

CREATE POLICY "wishes_delete_policy" ON public.customer_birthday_wishes
FOR DELETE USING (
    auth.role() = 'authenticated' AND public.is_admin()
);
