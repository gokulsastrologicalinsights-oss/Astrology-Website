-- Gokul's Astrological Insights - Muhurta Module Database Migration
-- Migration: 20261018000002_create_muhurta_tables.sql
-- Description: Creates public.muhurta_occasions, public.muhurta_occasion_rules, and public.saved_muhurtas
--              with concurrency-safe advisory-locked sequential numbering and Row-Level Security (RLS).

-- 1. Create public.muhurta_occasions table
CREATE TABLE IF NOT EXISTS public.muhurta_occasions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE CHECK (char_length(trim(code)) >= 2),
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT NOT NULL CHECK (char_length(trim(name_ta)) > 0),
    category TEXT NOT NULL CHECK (category IN (
        'marriage_relationships',
        'family_ceremonies',
        'home_property',
        'business_professional',
        'travel_vehicles',
        'education_spiritual',
        'custom'
    )),
    description_en TEXT,
    description_ta TEXT,
    icon TEXT NOT NULL DEFAULT 'Sparkles',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_muhurta_occasions_category ON public.muhurta_occasions (category);
CREATE INDEX IF NOT EXISTS idx_muhurta_occasions_is_enabled ON public.muhurta_occasions (is_enabled);

-- 2. Create public.muhurta_occasion_rules table
CREATE TABLE IF NOT EXISTS public.muhurta_occasion_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occasion_code TEXT NOT NULL REFERENCES public.muhurta_occasions(code) ON DELETE CASCADE,
    tradition TEXT NOT NULL DEFAULT 'south_indian' CHECK (tradition IN ('south_indian', 'north_indian', 'tamil_panchangam')),
    acceptable_tithis INT[] NOT NULL DEFAULT '{}',
    acceptable_nakshatras INT[] NOT NULL DEFAULT '{}',
    acceptable_weekdays INT[] NOT NULL DEFAULT '{}',
    prohibit_rahu_kalam BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_yamagandam BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_gulikai BOOLEAN NOT NULL DEFAULT FALSE,
    prohibit_dur_muhurta BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_varjyam BOOLEAN NOT NULL DEFAULT TRUE,
    require_ashtama_shuddhi BOOLEAN NOT NULL DEFAULT TRUE,
    require_sapthama_shuddhi BOOLEAN NOT NULL DEFAULT FALSE,
    require_tara_bala BOOLEAN NOT NULL DEFAULT FALSE,
    require_chandra_bala BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_lagnas INT[] NOT NULL DEFAULT '{}',
    min_duration_minutes INT NOT NULL DEFAULT 30,
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_muhurta_rule_occasion_tradition UNIQUE (occasion_code, tradition)
);

CREATE INDEX IF NOT EXISTS idx_muhurta_rules_occasion ON public.muhurta_occasion_rules (occasion_code);

-- 3. Create public.saved_muhurtas table
CREATE TABLE IF NOT EXISTS public.saved_muhurtas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (char_length(trim(title)) > 0),
    occasion_code TEXT NOT NULL,
    occasion_name TEXT NOT NULL,
    event_date DATE NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    local_start_time TEXT NOT NULL,
    local_end_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    location_name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    timezone TEXT NOT NULL,
    ayanamsa_id INTEGER NOT NULL DEFAULT 0,
    tradition TEXT NOT NULL DEFAULT 'south_indian',
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    status TEXT NOT NULL CHECK (status IN (
        'meets_configured_rules',
        'meets_rules_with_advisories',
        'fails_mandatory_rules',
        'incomplete'
    )),
    panchang_summary JSONB NOT NULL,
    lagna_summary JSONB NOT NULL,
    rule_evaluations JSONB NOT NULL,
    birth_details JSONB,
    notes TEXT,
    client_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_saved_muhurtas_user_display UNIQUE (user_id, display_number)
);

CREATE INDEX IF NOT EXISTS idx_saved_muhurtas_user_id ON public.saved_muhurtas (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_muhurtas_event_date ON public.saved_muhurtas (event_date);
CREATE INDEX IF NOT EXISTS idx_saved_muhurtas_created_at ON public.saved_muhurtas (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_muhurtas_occasion_code ON public.saved_muhurtas (occasion_code);

-- 4. Concurrency-Safe Transactional Sequential Numbering Trigger for saved_muhurtas
CREATE OR REPLACE FUNCTION public.set_saved_muhurta_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        PERFORM pg_advisory_xact_lock(hashtext('saved_muhurtas_' || NEW.user_id::text));
        
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_muhurtas
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_muhurta_display_number ON public.saved_muhurtas;
CREATE TRIGGER trg_set_saved_muhurta_display_number
BEFORE INSERT ON public.saved_muhurtas
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_muhurta_display_number();

-- 5. Row-Level Security (RLS) Policies
ALTER TABLE public.muhurta_occasions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.muhurta_occasion_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_muhurtas ENABLE ROW LEVEL SECURITY;

-- Occasions RLS: Everyone (authenticated or anon) can read enabled occasions; admins can manage all
DROP POLICY IF EXISTS "muhurta_occasions_select_policy" ON public.muhurta_occasions;
DROP POLICY IF EXISTS "muhurta_occasions_admin_insert" ON public.muhurta_occasions;
DROP POLICY IF EXISTS "muhurta_occasions_admin_update" ON public.muhurta_occasions;
DROP POLICY IF EXISTS "muhurta_occasions_admin_delete" ON public.muhurta_occasions;

CREATE POLICY "muhurta_occasions_select_policy"
ON public.muhurta_occasions FOR SELECT
USING (is_enabled = TRUE OR public.is_admin());

CREATE POLICY "muhurta_occasions_admin_insert"
ON public.muhurta_occasions FOR INSERT
WITH CHECK (public.is_admin());

CREATE POLICY "muhurta_occasions_admin_update"
ON public.muhurta_occasions FOR UPDATE
USING (public.is_admin())
WITH CHECK (public.is_admin());

CREATE POLICY "muhurta_occasions_admin_delete"
ON public.muhurta_occasions FOR DELETE
USING (public.is_admin());

-- Rules RLS: Authenticated and anon can read rules; admins can modify
DROP POLICY IF EXISTS "muhurta_rules_select_policy" ON public.muhurta_occasion_rules;
DROP POLICY IF EXISTS "muhurta_rules_admin_insert" ON public.muhurta_occasion_rules;
DROP POLICY IF EXISTS "muhurta_rules_admin_update" ON public.muhurta_occasion_rules;
DROP POLICY IF EXISTS "muhurta_rules_admin_delete" ON public.muhurta_occasion_rules;

CREATE POLICY "muhurta_rules_select_policy"
ON public.muhurta_occasion_rules FOR SELECT
USING (TRUE);

CREATE POLICY "muhurta_rules_admin_insert"
ON public.muhurta_occasion_rules FOR INSERT
WITH CHECK (public.is_admin());

CREATE POLICY "muhurta_rules_admin_update"
ON public.muhurta_occasion_rules FOR UPDATE
USING (public.is_admin())
WITH CHECK (public.is_admin());

CREATE POLICY "muhurta_rules_admin_delete"
ON public.muhurta_occasion_rules FOR DELETE
USING (public.is_admin());

-- Saved Muhurtas RLS: Normal users see their own; Admins see all
DROP POLICY IF EXISTS "saved_muhurtas_select_policy" ON public.saved_muhurtas;
DROP POLICY IF EXISTS "saved_muhurtas_insert_policy" ON public.saved_muhurtas;
DROP POLICY IF EXISTS "saved_muhurtas_update_policy" ON public.saved_muhurtas;
DROP POLICY IF EXISTS "saved_muhurtas_delete_policy" ON public.saved_muhurtas;

CREATE POLICY "saved_muhurtas_select_policy"
ON public.saved_muhurtas FOR SELECT
USING (auth.uid() = user_id OR public.is_admin());

CREATE POLICY "saved_muhurtas_insert_policy"
ON public.saved_muhurtas FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_muhurtas_update_policy"
ON public.saved_muhurtas FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "saved_muhurtas_delete_policy"
ON public.saved_muhurtas FOR DELETE
USING (auth.uid() = user_id OR public.is_admin());

GRANT ALL ON TABLE public.muhurta_occasions TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.muhurta_occasion_rules TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.saved_muhurtas TO anon, authenticated, service_role;
