-- Gokul's Astrological Insights - Subscription & Selected Access Migration
-- Migration: 20261029000001_add_subscription_and_permissions_to_profiles.sql
-- Description: Adds subscription tiers, validity timestamps, account status, and granular module permissions to public.profiles.

-- 1. Add subscription columns to public.profiles
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS subscription_tier TEXT NOT NULL DEFAULT 'basic'
    CHECK (subscription_tier IN ('trial', 'basic', 'pro', 'enterprise', 'custom')),
ADD COLUMN IF NOT EXISTS subscription_status TEXT NOT NULL DEFAULT 'active'
    CHECK (subscription_status IN ('active', 'suspended', 'expired', 'pending')),
ADD COLUMN IF NOT EXISTS valid_until TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS max_pdf_monthly INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS permissions JSONB NOT NULL DEFAULT '{
    "vedic": true,
    "tamil_horoscope": false,
    "kp_astrology": false,
    "marriage_matching": true,
    "panchang_muhurta": true,
    "numerology": false,
    "vastu": false,
    "remedies": true,
    "crm": false,
    "pdf_export": true
}'::jsonb;

-- 2. Index for filtering active vs expired accounts
CREATE INDEX IF NOT EXISTS idx_profiles_subscription_status ON public.profiles (subscription_status);
CREATE INDEX IF NOT EXISTS idx_profiles_valid_until ON public.profiles (valid_until);

-- 3. Automatic admin override: Admins always have lifetime active status and all permissions
UPDATE public.profiles
SET 
    subscription_tier = 'enterprise',
    subscription_status = 'active',
    valid_until = NULL,
    max_pdf_monthly = 999999,
    permissions = '{
        "vedic": true,
        "tamil_horoscope": true,
        "kp_astrology": true,
        "marriage_matching": true,
        "panchang_muhurta": true,
        "numerology": true,
        "vastu": true,
        "remedies": true,
        "crm": true,
        "pdf_export": true
    }'::jsonb
WHERE role = 'admin';
