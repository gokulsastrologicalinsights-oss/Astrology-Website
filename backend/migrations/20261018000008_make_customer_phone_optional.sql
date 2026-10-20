-- Gokul's Astrological Insights - Make Customer WhatsApp Number Optional
-- Migration: 20261018000008_make_customer_phone_optional.sql
-- Description: Safely relaxes NOT NULL and CHECK constraints on customer phone fields
-- and replaces the unique index with a partial unique index allowing multiple nulls.

DO $$
BEGIN
    -- Safely alter column nullability if public.customers exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'customers'
    ) THEN
        ALTER TABLE public.customers ALTER COLUMN phone_number DROP NOT NULL;
        ALTER TABLE public.customers ALTER COLUMN normalized_phone DROP NOT NULL;
        ALTER TABLE public.customers ALTER COLUMN whatsapp_number DROP NOT NULL;

        -- Drop old strict unique index if present
        DROP INDEX IF EXISTS public.uq_customers_user_normalized_phone;

        -- Create partial unique index that only enforces uniqueness for non-null/non-empty phones
        CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_user_normalized_phone 
        ON public.customers (user_id, normalized_phone) 
        WHERE normalized_phone IS NOT NULL AND normalized_phone <> '';
    END IF;
END $$;
