-- ==============================================================================
-- Gokul's Astrological Insights - Consolidated Staging Migration Package
-- Target Project: pcwiopxewlxhwvddpndq (Gokuls Astrological Insights - Staging)
-- Migrations Included:
--   1. 20261018000006_create_customers_and_link_horoscopes.sql
--   2. 20261018000007_create_remedy_knowledge_base.sql
--   3. 20261018000008_make_customer_phone_optional.sql
--   4. 20261018000009_create_remedy_reports.sql
--
-- Execution Instructions:
--   Execute this script in the Supabase Dashboard SQL Editor for project:
--   pcwiopxewlxhwvddpndq
-- ==============================================================================

BEGIN;


-- PART 1: CUSTOMERS & HOROSCOPE LINKING
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


-- PART 2: REMEDY KNOWLEDGE BASE & SEEDS
-- Gokul's Astrological Insights - Remedies & Pariharam Module Database Migration
-- Migration: 20261018000007_create_remedy_knowledge_base.sql
-- Description: Establishes the clean-room Remedy Knowledge Base:
--              1. public.remedy_source_references (classical shastras, puranas, traditions)
--              2. public.remedies_problem_taxonomy (39 verified life problem categories in EN/TA)
--              3. public.remedies_catalog (verified mantras, worship, daan, fasting, and temple remedies)
--              4. public.navagraha_temples (the 9 authentic Kaveri Delta Tamil Navagraha temples)
--              Configures RLS policies, indexes, and seeds verified foundational records.

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 1. Table: public.remedy_source_references
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CREATE TABLE IF NOT EXISTS public.remedy_source_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE CHECK (char_length(trim(code)) >= 2),
    title_en TEXT NOT NULL CHECK (char_length(trim(title_en)) > 0),
    title_sa TEXT,
    author TEXT,
    tradition TEXT NOT NULL DEFAULT 'classical_jyotish' CHECK (tradition IN (
        'vedic',
        'puranic',
        'tantric',
        'classical_jyotish',
        'tamil_shaiva',
        'tamil_vaishnava',
        'regional_tradition'
    )),
    canonical_status TEXT NOT NULL DEFAULT 'primary_shastra' CHECK (canonical_status IN (
        'primary_shastra',
        'secondary_smriti',
        'purana',
        'stotra_samhita',
        'regional_tradition'
    )),
    description TEXT,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_remedy_sources_code ON public.remedy_source_references (code);
CREATE INDEX IF NOT EXISTS idx_remedy_sources_tradition ON public.remedy_source_references (tradition);

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 2. Table: public.remedies_problem_taxonomy
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CREATE TABLE IF NOT EXISTS public.remedies_problem_taxonomy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE CHECK (char_length(trim(slug)) >= 2),
    category TEXT NOT NULL CHECK (category IN (
        'career',
        'relationships_marriage',
        'health_wellness',
        'finance_wealth',
        'property_legal',
        'education_intellect',
        'spiritual_growth',
        'travel_foreign'
    )),
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT NOT NULL CHECK (char_length(trim(name_ta)) > 0),
    description_en TEXT,
    description_ta TEXT,
    primary_karakas TEXT[] NOT NULL DEFAULT '{}',
    governing_houses INT[] NOT NULL DEFAULT '{}',
    display_order INT NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    verification_status TEXT NOT NULL DEFAULT 'verified' CHECK (verification_status IN ('draft', 'under_review', 'verified')),
    reviewer_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_remedies_problem_slug ON public.remedies_problem_taxonomy (slug);
CREATE INDEX IF NOT EXISTS idx_remedies_problem_category ON public.remedies_problem_taxonomy (category);
CREATE INDEX IF NOT EXISTS idx_remedies_problem_published ON public.remedies_problem_taxonomy (is_published, verification_status);

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 3. Table: public.remedies_catalog
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CREATE TABLE IF NOT EXISTS public.remedies_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE CHECK (char_length(trim(code)) >= 2),
    graha TEXT NOT NULL CHECK (graha IN (
        'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu', 'universal'
    )),
    remedy_type TEXT NOT NULL CHECK (remedy_type IN (
        'mantra', 'worship', 'charity', 'fasting', 'temple'
    )),
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT NOT NULL CHECK (char_length(trim(name_ta)) > 0),
    description_en TEXT NOT NULL,
    description_ta TEXT NOT NULL,
    deity_en TEXT NOT NULL,
    deity_ta TEXT NOT NULL,
    sanskrit_text TEXT,
    transliteration_iast TEXT,
    transliteration_ta TEXT,
    meaning_en TEXT,
    meaning_ta TEXT,
    procedure_en TEXT NOT NULL,
    procedure_ta TEXT NOT NULL,
    japa_count INT DEFAULT 108,
    timing_recommendation_en TEXT,
    timing_recommendation_ta TEXT,
    source_reference_id UUID REFERENCES public.remedy_source_references(id) ON DELETE SET NULL,
    source_verse_or_page TEXT,
    is_pacification_only BOOLEAN NOT NULL DEFAULT FALSE,
    problem_slugs TEXT[] NOT NULL DEFAULT '{}',
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    verification_status TEXT NOT NULL DEFAULT 'verified' CHECK (verification_status IN ('draft', 'under_review', 'verified')),
    reviewer_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_remedies_catalog_graha ON public.remedies_catalog (graha);
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_type ON public.remedies_catalog (remedy_type);
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_published ON public.remedies_catalog (is_published, verification_status);
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_pacification ON public.remedies_catalog (is_pacification_only);

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 4. Table: public.navagraha_temples
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CREATE TABLE IF NOT EXISTS public.navagraha_temples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE CHECK (char_length(trim(code)) >= 2),
    graha TEXT NOT NULL CHECK (graha IN (
        'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu'
    )),
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT NOT NULL CHECK (char_length(trim(name_ta)) > 0),
    presiding_deity_en TEXT NOT NULL,
    presiding_deity_ta TEXT NOT NULL,
    graha_deity_en TEXT NOT NULL,
    graha_deity_ta TEXT NOT NULL,
    place_name_en TEXT NOT NULL,
    place_name_ta TEXT NOT NULL,
    district_en TEXT NOT NULL,
    district_ta TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Tamil Nadu',
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    visiting_day_en TEXT NOT NULL,
    visiting_day_ta TEXT NOT NULL,
    significance_en TEXT NOT NULL,
    significance_ta TEXT NOT NULL,
    remedy_offerings_en TEXT NOT NULL,
    remedy_offerings_ta TEXT NOT NULL,
    source_tradition TEXT NOT NULL DEFAULT 'Kaveri Delta Navagraha Sthalam',
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    verification_status TEXT NOT NULL DEFAULT 'verified' CHECK (verification_status IN ('draft', 'under_review', 'verified')),
    reviewer_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_navagraha_temples_graha ON public.navagraha_temples (graha);
CREATE INDEX IF NOT EXISTS idx_navagraha_temples_published ON public.navagraha_temples (is_published, verification_status);

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 5. Row Level Security (RLS) Policies
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ALTER TABLE public.remedy_source_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.remedies_problem_taxonomy ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.remedies_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.navagraha_temples ENABLE ROW LEVEL SECURITY;

-- 5.1 Sources RLS
DROP POLICY IF EXISTS "remedy_sources_select" ON public.remedy_source_references;
DROP POLICY IF EXISTS "remedy_sources_admin_modify" ON public.remedy_source_references;

CREATE POLICY "remedy_sources_select" ON public.remedy_source_references
    FOR SELECT USING (is_published = TRUE OR public.is_admin());

CREATE POLICY "remedy_sources_admin_modify" ON public.remedy_source_references
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 5.2 Taxonomy RLS
DROP POLICY IF EXISTS "remedies_taxonomy_select" ON public.remedies_problem_taxonomy;
DROP POLICY IF EXISTS "remedies_taxonomy_admin_modify" ON public.remedies_problem_taxonomy;

CREATE POLICY "remedies_taxonomy_select" ON public.remedies_problem_taxonomy
    FOR SELECT USING (is_published = TRUE OR public.is_admin());

CREATE POLICY "remedies_taxonomy_admin_modify" ON public.remedies_problem_taxonomy
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 5.3 Catalog RLS
DROP POLICY IF EXISTS "remedies_catalog_select" ON public.remedies_catalog;
DROP POLICY IF EXISTS "remedies_catalog_admin_modify" ON public.remedies_catalog;

CREATE POLICY "remedies_catalog_select" ON public.remedies_catalog
    FOR SELECT USING ((is_published = TRUE AND verification_status = 'verified') OR public.is_admin());

CREATE POLICY "remedies_catalog_admin_modify" ON public.remedies_catalog
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 5.4 Navagraha Temples RLS
DROP POLICY IF EXISTS "navagraha_temples_select" ON public.navagraha_temples;
DROP POLICY IF EXISTS "navagraha_temples_admin_modify" ON public.navagraha_temples;

CREATE POLICY "navagraha_temples_select" ON public.navagraha_temples
    FOR SELECT USING (is_published = TRUE OR public.is_admin());

CREATE POLICY "navagraha_temples_admin_modify" ON public.navagraha_temples
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());


-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 6. Grants
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
GRANT ALL ON TABLE public.remedy_source_references TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.remedies_problem_taxonomy TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.remedies_catalog TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.navagraha_temples TO anon, authenticated, service_role;

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 7. Seed: Canonical Shastra & Stotra Source References
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO public.remedy_source_references (code, title_en, title_sa, author, tradition, canonical_status, description)
VALUES
('BPHS', 'Brihat Parashara Hora Shastra', 'à¤¬à¥ƒà¤¹à¤¤à¥à¤ªà¤¾à¤°à¤¾à¤¶à¤°à¤¹à¥‹à¤°à¤¾à¤¶à¤¾à¤¸à¥à¤¤à¥à¤°à¤®à¥', 'Maharishi Parashara', 'classical_jyotish', 'primary_shastra', 'Foundational compendium of Vedic astrology detailing planetary natures, avasthas, afflictions, and classical shanti remedies.'),
('PHALADEEPIKA', 'Phaladeepika', 'à¤«à¤²à¤¦à¥€à¤ªà¤¿à¤•à¤¾', 'Mantreswara', 'classical_jyotish', 'primary_shastra', 'Classical medieval text covering planetary strengths, bhava results, yogas, and remedial pacification.'),
('NAVAGRAHA_STOTRAM', 'Sri Navagraha Stotram', 'à¤¨à¤µà¤—à¥à¤°à¤¹à¤¸à¥à¤¤à¥‹à¤¤à¥à¤°à¤®à¥', 'Sri Veda Vyasa', 'puranic', 'stotra_samhita', 'Nine sacred hymns composed by Sage Veda Vyasa in the Mahabharata / Puranic tradition to propitiate the nine celestial grahas.'),
('VALMIKI_RAMAYANA', 'Valmiki Ramayana - Aditya Hridayam', 'à¤†à¤¦à¤¿à¤¤à¥à¤¯à¤¹à¥ƒà¤¦à¤¯à¤®à¥', 'Sage Agastya / Maharishi Valmiki', 'puranic', 'stotra_samhita', 'Sacred hymn imparted by Sage Agastya to Lord Sri Rama on the battlefield (Yuddha Kanda 105) for victory, health, and dispelling inner fear.'),
('RIGVEDA', 'Rigveda Samhita - Maha Mrityunjaya', 'à¤¤à¥à¤°à¥à¤¯à¤®à¥à¤¬à¤•à¤‚ à¤¯à¤œà¤¾à¤®à¤¹à¥‡', 'Rishi Markandeya / Sage Vasistha', 'vedic', 'primary_shastra', 'The great death-conquering hymn (Rigveda 7.59.12) dedicated to Rudra for vital protection, healing, and freedom from disease and fear.'),
('MANTRA_MAHODADHI', 'Mantra Mahodadhi', 'à¤®à¤¨à¥à¤¤à¥à¤°à¤®à¤¹à¥‹à¤¦à¤§à¤¿à¤ƒ', 'Mahidhara', 'tantric', 'stotra_samhita', 'Comprehensive encyclopaedia of traditional Vedic-Tantric mantra vidhi, seed syllables (bijakshara), and japa procedures.'),
('KAVERI_DELTA_TRADITION', 'Kaveri Delta Navagraha Sthala Purana', 'à®•à®¾à®µà®¿à®°à®¿ à®Ÿà¯†à®²à¯à®Ÿà®¾ à®¨à®µà®•à®¿à®°à®• à®¸à¯à®¤à®² à®ªà¯à®°à®¾à®£à®®à¯', 'Tamil Shaiva-Vaishnava Tradition', 'tamil_shaiva', 'regional_tradition', 'Sacred temple traditions of the nine classical Navagraha sthalams located around Kumbakonam, Thanjavur, and Mayiladuthurai in Tamil Nadu.')
ON CONFLICT (code) DO UPDATE SET
    title_en = EXCLUDED.title_en,
    title_sa = EXCLUDED.title_sa,
    author = EXCLUDED.author,
    tradition = EXCLUDED.tradition,
    canonical_status = EXCLUDED.canonical_status,
    description = EXCLUDED.description,
    updated_at = NOW();

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 8. Seed: The 39 Verified Problem Taxonomy Categories
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO public.remedies_problem_taxonomy (slug, category, name_en, name_ta, description_en, description_ta, primary_karakas, governing_houses, display_order)
VALUES
-- Career (1-5)
('career_delay', 'career', 'Career Growth Delays', 'à®¤à¯Šà®´à®¿à®²à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà¯‡à®²à¯ˆ à®µà®³à®°à¯à®šà¯à®šà®¿ à®¤à®¾à®®à®¤à®®à¯', 
 'Persistent obstacles, stagnation, or delays in securing employment or career advancement.', 
 'à®µà¯‡à®²à¯ˆ à®•à®¿à®Ÿà¯ˆà®ªà¯à®ªà®¤à®¿à®²à¯ à®…à®²à¯à®²à®¤à¯ à®ªà®¤à®µà®¿ à®‰à®¯à®°à¯à®µà®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¤à¯Šà®Ÿà®°à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯‡à®•à¯à®• à®¨à®¿à®²à¯ˆ.', 
 ARRAY['saturn', 'sun', 'jupiter'], ARRAY[10, 6, 2], 1),

('job_loss_instability', 'career', 'Job Loss & Professional Instability', 'à®µà¯‡à®²à¯ˆ à®‡à®´à®ªà¯à®ªà¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®£à®¿à®¯à®¿à®Ÿ à®¨à®¿à®²à¯ˆà®¯à®±à¯à®± à®¤à®©à¯à®®à¯ˆ', 
 'Frequent layoffs, unstable job tenure, or sudden termination in career.', 
 'à®…à®Ÿà®¿à®•à¯à®•à®Ÿà®¿ à®µà¯‡à®²à¯ˆ à®®à®¾à®±à¯à®¤à®²à¯, à®µà¯‡à®²à¯ˆ à®‡à®´à®ªà¯à®ªà¯ à®…à®ªà®¾à®¯à®®à¯ à®…à®²à¯à®²à®¤à¯ à®¨à®¿à®±à¯à®µà®©à®¤à¯à®¤à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¨à®¿à®²à¯ˆà®¯à®±à¯à®± à®šà¯‚à®´à®²à¯.', 
 ARRAY['saturn', 'rahu', 'mercury'], ARRAY[10, 6, 8], 2),

('business_setbacks', 'career', 'Business Setbacks & Trade Slumps', 'à®µà®£à®¿à®•à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¨à®·à¯à®Ÿà®®à¯', 
 'Financial blockages, client loss, or unviable trade downturns in business ventures.', 
 'à®µà®¿à®¯à®¾à®ªà®¾à®°à®¤à¯à®¤à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¤à¯Šà®Ÿà®°à¯ à®ªà®¿à®©à¯à®©à®Ÿà¯ˆà®µà¯, à®µà®¾à®Ÿà®¿à®•à¯à®•à¯ˆà®¯à®¾à®³à®°à¯ à®‡à®´à®ªà¯à®ªà¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®°à¯à®¤à¯à®¤à®•à®¤à¯ à®¤à¯‡à®•à¯à®•à®®à¯.', 
 ARRAY['mercury', 'jupiter', 'venus'], ARRAY[7, 10, 11], 3),

('promotion_blocks', 'career', 'Promotion & Recognition Blocks', 'à®ªà®¤à®µà®¿ à®‰à®¯à®°à¯à®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®™à¯à®•à¯€à®•à®¾à®°à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Passed over for promotions, lack of administrative recognition despite dedicated effort.', 
 'à®•à®Ÿà®¿à®© à®‰à®´à¯ˆà®ªà¯à®ªà®¿à®±à¯à®•à¯à®°à®¿à®¯ à®…à®™à¯à®•à¯€à®•à®¾à®°à®®à¯ à®•à®¿à®Ÿà¯ˆà®•à¯à®•à®¾à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à®•à¯à®¤à®¿à®¯à®¿à®°à¯à®¨à¯à®¤à¯à®®à¯ à®ªà®¤à®µà®¿ à®‰à®¯à®°à¯à®µà¯ à®¤à®³à¯à®³à®¿à®ªà¯à®ªà¯‹à®¤à®²à¯.', 
 ARRAY['sun', 'jupiter', 'mars'], ARRAY[10, 11, 1], 4),

('workplace_conflicts', 'career', 'Workplace Politics & Authority Conflicts', 'à®ªà®£à®¿à®¯à®¿à®Ÿà®¤à¯à®¤à®¿à®²à¯ à®®à¯‡à®²à®¤à®¿à®•à®¾à®°à®¿ à®®à®±à¯à®±à¯à®®à¯ à®šà®• à®Šà®´à®¿à®¯à®°à¯ à®ªà®¿à®£à®•à¯à®•à¯à®•à®³à¯', 
 'Severe friction with superiors, organizational politics, or hostile working conditions.', 
 'à®‰à®¯à®°à¯ à®…à®¤à®¿à®•à®¾à®°à®¿à®•à®³à¯à®Ÿà®©à¯ à®•à®°à¯à®¤à¯à®¤à¯ à®®à¯‹à®¤à®²à¯à®•à®³à¯, à®…à®²à¯à®µà®²à®• à®…à®°à®šà®¿à®¯à®²à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®© à®‰à®³à¯ˆà®šà¯à®šà®²à¯.', 
 ARRAY['sun', 'mars', 'saturn'], ARRAY[10, 6, 3], 5),

-- Relationships & Marriage (6-11)
('marriage_delay', 'relationships_marriage', 'Delay in Marriage', 'à®¤à®¿à®°à¯à®®à®£à®¤à¯ à®¤à®¾à®®à®¤à®®à¯', 
 'Obstacles in finding an aligned life partner or persistent delays in finalizing marriage alliances.', 
 'à®ªà¯Šà®°à¯à®¤à¯à®¤à®®à®¾à®© à®µà®°à®©à¯ à®…à®®à¯ˆà®µà®¤à®¿à®²à¯ à®¤à®¾à®®à®¤à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à®¿à®°à¯à®®à®£à®ªà¯ à®ªà¯‡à®šà¯à®šà¯à®µà®¾à®°à¯à®¤à¯à®¤à¯ˆà®•à®³à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¤à®Ÿà¯ˆà®•à®³à¯.', 
 ARRAY['venus', 'jupiter', 'mars'], ARRAY[7, 2, 8], 6),

('marital_discord', 'relationships_marriage', 'Marital Discord & Misunderstandings', 'à®¤à®®à¯à®ªà®¤à®¿à®¯à®°à¯ à®‡à®Ÿà¯ˆà®¯à¯‡ à®•à®°à¯à®¤à¯à®¤à¯ à®µà¯‡à®±à¯à®ªà®¾à®Ÿà¯', 
 'Recurrent arguments, emotional estrangement, and lack of harmony between spouses.', 
 'à®•à®£à®µà®©à¯ à®®à®©à¯ˆà®µà®¿ à®‡à®Ÿà¯ˆà®¯à¯‡ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®ªà®°à®¸à¯à®ªà®° à®¨à®®à¯à®ªà®¿à®•à¯à®•à¯ˆà®¯à®¿à®©à¯à®®à¯ˆ, à®µà®¾à®•à¯à®•à¯à®µà®¾à®¤à®™à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®®à¯ˆà®¤à®¿à®¯à®¿à®©à¯à®®à¯ˆ.', 
 ARRAY['venus', 'mars', 'moon'], ARRAY[7, 4, 2], 7),

('separation_divorce_risk', 'relationships_marriage', 'Threat of Separation & Legal Divorce', 'à®ªà®¿à®°à®¿à®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¿à®µà®¾à®•à®°à®¤à¯à®¤à¯ à®…à®šà¯à®šà¯à®±à¯à®¤à¯à®¤à®²à¯', 
 'Impending breakdown of marriage, court litigation, or emotional rupture between partners.', 
 'à®•à¯à®Ÿà¯à®®à¯à®ªà®ªà¯ à®ªà®¿à®³à®µà¯, à®µà®¿à®µà®¾à®•à®°à®¤à¯à®¤à¯ à®µà®´à®•à¯à®•à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¨à®¿à®°à®¨à¯à®¤à®°à®ªà¯ à®ªà®¿à®°à®¿à®µà®¿à®©à¯ˆ à®…à®ªà®¾à®¯à®®à¯.', 
 ARRAY['saturn', 'rahu', 'mars'], ARRAY[7, 8, 12], 8),

('relationship_breakdown', 'relationships_marriage', 'Heartbreak & Relationship Ruptures', 'à®•à®¾à®¤à®²à¯ à®®à®±à¯à®±à¯à®®à¯ à®‰à®±à®µà¯ à®®à¯à®±à®¿à®µà¯', 
 'Emotional distress from sudden broken relationships, deceit, or emotional abandonment.', 
 'à®•à®¾à®¤à®²à¯ à®®à¯à®±à®¿à®µà¯, à®¤à¯à®°à¯‹à®•à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®‰à®£à®°à¯à®µà¯à®ªà¯‚à®°à¯à®µà®®à®¾à®© à®¤à®©à®¿à®®à¯ˆà®¤à¯ à®¤à¯à®¯à®°à®®à¯.', 
 ARRAY['venus', 'moon', 'rahu'], ARRAY[5, 7, 12], 9),

('inlaw_family_strife', 'relationships_marriage', 'In-Law & Extended Family Strife', 'à®•à¯à®Ÿà¯à®®à¯à®ª à®®à®±à¯à®±à¯à®®à¯ à®®à®¾à®®à®¿à®¯à®¾à®°à¯-à®®à®°à¯à®®à®•à®³à¯ à®šà®šà¯à®šà®°à®µà¯à®•à®³à¯', 
 'Chronic conflict between spouses and in-laws disrupting domestic harmony.', 
 'à®•à¯‚à®Ÿà¯à®Ÿà¯à®•à¯ à®•à¯à®Ÿà¯à®®à¯à®ªà®šà¯ à®šà®¿à®•à¯à®•à®²à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®‰à®±à®µà®¿à®©à®°à¯à®•à®³à®¿à®Ÿà¯ˆà®¯à¯‡ à®¨à®¿à®²à®µà¯à®®à¯ à®®à®©à®•à¯à®•à®šà®ªà¯à®ªà¯à®•à®³à¯.', 
 ARRAY['moon', 'mars', 'mercury'], ARRAY[4, 2, 9], 10),

('progeny_childbirth_delay', 'relationships_marriage', 'Delay in Progeny & Childbirth', 'à®ªà¯à®¤à¯à®¤à®¿à®° à®ªà®¾à®•à¯à®•à®¿à®¯ à®¤à®¾à®®à®¤à®®à¯', 
 'Difficulties or medical/astrological delays in conceiving and bearing healthy offspring.', 
 'à®•à¯à®´à®¨à¯à®¤à¯ˆà®ªà¯ à®ªà¯‡à®±à¯ à®ªà¯†à®±à¯à®µà®¤à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®°à¯à®¤à¯à®¤à¯à®µ/à®œà¯‹à®¤à®¿à®Ÿ à®°à¯€à®¤à®¿à®¯à®¾à®© à®¤à®¾à®®à®¤à®™à¯à®•à®³à¯.', 
 ARRAY['jupiter', 'sun', 'mars'], ARRAY[5, 9, 2], 11),

-- Health & Wellness (12-17)
('chronic_health_issues', 'health_wellness', 'Chronic Health Ailments', 'à®¨à¯€à®£à¯à®Ÿ à®•à®¾à®² à®‰à®Ÿà®²à¯ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯', 
 'Recurring illnesses, systemic weaknesses, or long-term chronic conditions.', 
 'à®¨à¯€à®£à¯à®Ÿ à®•à®¾à®²à®®à¯ à®¤à¯Šà®Ÿà®°à¯à®®à¯ à®‰à®Ÿà®²à¯ à®¨à®²à®•à¯ à®•à¯à®±à¯ˆà®ªà®¾à®Ÿà¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®•à¯à®£à®®à®Ÿà¯ˆà®¯à®¾à®¤ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯.', 
 ARRAY['sun', 'saturn', 'mars'], ARRAY[6, 8, 1], 12),

('mental_anxiety_depression', 'health_wellness', 'Anxiety, Depression & Insomnia', 'à®®à®© à®…à®´à¯à®¤à¯à®¤à®®à¯, à®ªà®¤à®±à¯à®±à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯‚à®•à¯à®•à®®à®¿à®©à¯à®®à¯ˆ', 
 'Emotional turbulence, panic, restlessness, obsessive thoughts, or inability to sleep peacefully.', 
 'à®…à®¤à®¿à®•à®ªà¯à®ªà®Ÿà®¿à®¯à®¾à®© à®®à®©à®•à¯à®•à®µà®²à¯ˆ, à®…à®®à¯ˆà®¤à®¿à®¯à®¿à®©à¯à®®à¯ˆ, à®®à®©à®šà¯à®šà¯‹à®°à¯à®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯‚à®•à¯à®•à®•à¯ à®•à¯‹à®³à®¾à®±à¯à®•à®³à¯.', 
 ARRAY['moon', 'rahu', 'mercury'], ARRAY[1, 4, 12], 13),

('eye_vision_ailments', 'health_wellness', 'Vision & Headaches', 'à®•à®£à¯ à®ªà®¾à®°à¯à®µà¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à®²à¯ˆà®µà®²à®¿ à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯', 
 'Recurring migraines, eye strain, vision problems, and nervous headaches.', 
 'à®•à®£à¯ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯, à®ªà®¾à®°à¯à®µà¯ˆ à®®à®™à¯à®•à®²à¯, à®•à®Ÿà¯à®®à¯ˆà®¯à®¾à®© à®¤à®²à¯ˆà®µà®²à®¿ à®®à®±à¯à®±à¯à®®à¯ à®’à®±à¯à®±à¯ˆà®¤à¯ à®¤à®²à¯ˆà®µà®²à®¿.', 
 ARRAY['sun', 'moon', 'mars'], ARRAY[2, 12, 1], 14),

('bone_joint_mobility', 'health_wellness', 'Bone, Joint & Vata Disorders', 'à®Žà®²à¯à®®à¯à®ªà¯, à®®à¯‚à®Ÿà¯à®Ÿà¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®¤ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯', 
 'Arthritis, joint stiffness, spinal weaknesses, or fractures related to bone density.', 
 'à®®à¯‚à®Ÿà¯à®Ÿà¯ à®µà®²à®¿, à®µà®¾à®¤à®•à¯ à®•à¯‹à®³à®¾à®±à¯à®•à®³à¯, à®®à¯à®¤à¯à®•à¯à®¤à¯à®¤à®£à¯à®Ÿà¯ à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®Žà®²à¯à®®à¯à®ªà¯ à®¤à¯‡à®¯à¯à®®à®¾à®©à®®à¯.', 
 ARRAY['saturn', 'sun', 'mars'], ARRAY[6, 8, 10], 15),

('digestive_stomach_ailments', 'health_wellness', 'Digestive & Metabolic Disturbances', 'à®šà¯†à®°à®¿à®®à®¾à®©à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¯à®¿à®±à¯ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯', 
 'Gastric disorders, liver sluggishness, or metabolic imbalances.', 
 'à®šà¯†à®°à®¿à®®à®¾à®©à®•à¯ à®•à¯‹à®³à®¾à®±à¯à®•à®³à¯, à®•à®²à¯à®²à¯€à®°à®²à¯ à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¯à®¿à®±à¯à®±à¯ à®‰à®ªà®¾à®¤à¯ˆà®•à®³à¯.', 
 ARRAY['jupiter', 'sun', 'mars'], ARRAY[5, 6, 1], 16),

('vitality_low_energy', 'health_wellness', 'Low Vitality & Chronic Fatigue', 'à®•à¯à®±à¯ˆà®¨à¯à®¤ à®†à®±à¯à®±à®²à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà¯‹à®®à¯à®ªà®²à¯', 
 'Lack of stamina, chronic lethargy, weak immunity, and diminished physical resilience.', 
 'à®‰à®Ÿà®²à¯ à®šà¯‹à®°à¯à®µà¯, à®¨à¯‹à®¯à¯ à®Žà®¤à®¿à®°à¯à®ªà¯à®ªà¯ à®šà®•à¯à®¤à®¿ à®•à¯à®±à¯ˆà®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®‰à®±à¯à®šà®¾à®•à®®à®¿à®©à¯à®®à¯ˆ.', 
 ARRAY['sun', 'mars', 'jupiter'], ARRAY[1, 3, 6], 17),

-- Finance & Wealth (18-22)
('financial_instability', 'finance_wealth', 'Income Instability & Cash Crunch', 'à®ªà®£à®ªà¯à®ªà¯à®´à®•à¯à®•à®¤à¯ à®¤à®Ÿà¯à®Ÿà¯à®ªà¯à®ªà®¾à®Ÿà¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®°à¯à®®à®¾à®©à®¤à¯ à®¤à®Ÿà¯ˆ', 
 'Unpredictable cash flows, delays in receiving payments, or insufficient regular income.', 
 'à®®à¯à®±à¯ˆà®¯à®¾à®© à®µà®°à¯à®®à®¾à®©à®®à®¿à®©à¯à®®à¯ˆ, à®µà®°à®µà¯ à®šà¯†à®²à®µà¯ à®šà®®à®¨à®¿à®²à¯ˆà®¯à®¿à®©à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®ªà®£ à®¨à¯†à®°à¯à®•à¯à®•à®Ÿà®¿.', 
 ARRAY['jupiter', 'mercury', 'venus'], ARRAY[2, 11, 9], 18),

('chronic_debt_burden', 'finance_wealth', 'Chronic Debt & Borrowing Traps', 'à®•à®Ÿà®©à¯ à®šà¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯€à®°à®¾à®¤ à®•à®Ÿà®©à¯', 
 'Inability to repay loans, accumulating interest burdens, and financial entrapment.', 
 'à®…à®¤à®¿à®•à®°à®¿à®•à¯à®•à¯à®®à¯ à®•à®Ÿà®©à¯ à®¤à¯Šà®²à¯à®²à¯ˆà®•à®³à¯, à®µà®Ÿà¯à®Ÿà®¿à®šà¯ à®šà¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®•à®Ÿà®©à¯ à®…à®Ÿà¯ˆà®ªà¯à®ªà®¤à®¿à®²à¯ à®‰à®³à¯à®³ à®šà®¿à®•à¯à®•à®²à¯à®•à®³à¯.', 
 ARRAY['mars', 'saturn', 'rahu'], ARRAY[6, 8, 12], 19),

('speculation_gambling_losses', 'finance_wealth', 'Speculative & Investment Losses', 'à®ªà®™à¯à®•à¯à®šà¯à®šà®¨à¯à®¤à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®Šà®• à®µà®£à®¿à®• à®‡à®´à®ªà¯à®ªà¯à®•à®³à¯', 
 'Severe losses in stock trading, speculative ventures, or fraudulent schemes.', 
 'à®ªà®™à¯à®•à¯ à®µà®°à¯à®¤à¯à®¤à®•à®®à¯, à®šà¯‚à®¤à®¾à®Ÿà¯à®Ÿà®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à®µà®±à®¾à®© à®®à¯à®¤à®²à¯€à®Ÿà¯à®•à®³à®¾à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®ªà¯†à®°à¯à®®à¯ à®ªà¯Šà®°à¯à®³à®¾à®¤à®¾à®° à®‡à®´à®ªà¯à®ªà¯à®•à®³à¯.', 
 ARRAY['rahu', 'mercury', 'mars'], ARRAY[5, 8, 12], 20),

('wealth_accumulation_block', 'finance_wealth', 'Obstacles in Wealth Accumulation', 'à®šà¯‡à®®à®¿à®ªà¯à®ªà¯ à®‡à®©à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à®¿à®Ÿà¯€à®°à¯ à®ªà®£ à®‡à®´à®ªà¯à®ªà¯', 
 'Money leaking through unexpected expenses, lack of sustained savings despite good earnings.', 
 'à®µà®°à¯à®®à®¾à®©à®®à¯ à®‡à®°à¯à®¨à¯à®¤à¯à®®à¯ à®šà¯‡à®®à®¿à®•à¯à®• à®®à¯à®Ÿà®¿à®¯à®¾à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®Žà®¤à®¿à®°à¯à®ªà®¾à®°à®¾à®¤ à®µà®¿à®°à®¯à®™à¯à®•à®³à¯ à®à®±à¯à®ªà®Ÿà¯à®¤à®²à¯.', 
 ARRAY['jupiter', 'venus', 'saturn'], ARRAY[2, 11, 12], 21),

('inheritance_disputes', 'finance_wealth', 'Inheritance & Ancestral Wealth Issues', 'à®ªà¯‚à®°à¯à®µà¯€à®•à®šà¯ à®šà¯Šà®¤à¯à®¤à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®°à®¿à®šà¯à®°à®¿à®®à¯ˆà®šà¯ à®šà®¿à®•à¯à®•à®²à¯à®•à®³à¯', 
 'Stalled legacy wealth, contested parental estates, and division of ancestral property.', 
 'à®ªà¯‚à®°à¯à®µà¯€à®•à®šà¯ à®šà¯Šà®¤à¯à®¤à¯ à®•à®¿à®Ÿà¯ˆà®ªà¯à®ªà®¤à®¿à®²à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®™à¯à®•à®¾à®³à®¿à®•à®³à®¿à®Ÿà¯ˆà®¯à¯‡ à®¨à®¿à®²à®µà¯à®®à¯ à®ªà®¾à®•à®ªà¯à®ªà®¿à®°à®¿à®µà®¿à®©à¯ˆ à®®à¯à®°à®£à¯à®ªà®¾à®Ÿà¯à®•à®³à¯.', 
 ARRAY['saturn', 'jupiter', 'sun'], ARRAY[8, 9, 4], 22),

-- Property & Legal (23-26)
('land_property_disputes', 'property_legal', 'Land & Real Estate Disputes', 'à®¨à®¿à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®©à¯ˆ à®¤à¯Šà®Ÿà®°à¯à®ªà®¾à®© à®¤à®•à®°à®¾à®±à¯à®•à®³à¯', 
 'Contested land titles, boundary encroachments, or fraudulent real estate transactions.', 
 'à®¨à®¿à®²à®®à¯, à®®à®©à¯ˆ à®µà®¾à®™à¯à®•à¯à®µà®¤à®¿à®²à¯ à®¤à®Ÿà¯ˆà®•à®³à¯, à®Žà®²à¯à®²à¯ˆà®¤à¯ à®¤à®•à®°à®¾à®±à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà¯Šà®¤à¯à®¤à¯ à®µà®¿à®µà®•à®¾à®°à®™à¯à®•à®³à¯.', 
 ARRAY['mars', 'saturn', 'rahu'], ARRAY[4, 6, 8], 23),

('litigation_court_cases', 'property_legal', 'Court Cases & Legal Battles', 'à®¨à¯€à®¤à®¿à®®à®©à¯à®± à®µà®´à®•à¯à®•à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà®Ÿà¯à®Ÿà®ªà¯ à®ªà¯‹à®°à®¾à®Ÿà¯à®Ÿà®™à¯à®•à®³à¯', 
 'Protracted litigation, unfair allegations, or stressful judicial proceedings.', 
 'à®¨à¯€à®¤à®¿à®®à®©à¯à®± à®µà®´à®•à¯à®•à¯à®•à®³à¯, à®…à®µà®¤à¯‚à®±à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®°à®šà¯/à®šà®Ÿà¯à®Ÿ à®°à¯€à®¤à®¿à®¯à®¾à®© à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯.', 
 ARRAY['saturn', 'mars', 'rahu'], ARRAY[6, 8, 12], 24),

('house_construction_hurdles', 'property_legal', 'House Construction Obstacles', 'à®µà¯€à®Ÿà¯ à®•à®Ÿà¯à®Ÿà¯à®®à¯ à®ªà®£à®¿à®¯à®¿à®²à¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Stalled home construction, contractor disputes, municipal hurdles, or Vastu flaws.', 
 'à®ªà¯à®¤à®¿à®¯ à®µà¯€à®Ÿà¯ à®•à®Ÿà¯à®Ÿà®¤à¯ à®¤à¯Šà®Ÿà®™à¯à®•à¯à®µà®¤à®¿à®²à¯ à®¤à®Ÿà¯ˆà®•à®³à¯, à®•à®Ÿà¯à®Ÿà¯à®®à®¾à®©à®ªà¯ à®ªà®£à®¿à®¯à®¿à®²à¯ à®¤à®¾à®®à®¤à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®¸à¯à®¤à¯ à®•à¯à®±à¯ˆà®ªà®¾à®Ÿà¯à®•à®³à¯.', 
 ARRAY['mars', 'saturn', 'jupiter'], ARRAY[4, 1, 9], 25),

('vehicle_accidents_breakdowns', 'property_legal', 'Vehicle Accidents & Frequent Breakdowns', 'à®µà®¾à®•à®© à®µà®¿à®ªà®¤à¯à®¤à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®´à¯à®¤à¯à®•à®³à¯', 
 'Repeated vehicle damages, close calls, road accidents, or mechanical failure costs.', 
 'à®…à®Ÿà®¿à®•à¯à®•à®Ÿà®¿ à®¨à®¿à®•à®´à¯à®®à¯ à®µà®¾à®•à®© à®µà®¿à®ªà®¤à¯à®¤à¯à®•à®³à¯, à®‡à®¯à®¨à¯à®¤à®¿à®°à®•à¯ à®•à¯‹à®³à®¾à®±à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®¯à®£à®ªà¯ à®ªà®¯à®®à¯.', 
 ARRAY['mars', 'rahu', 'ketu'], ARRAY[4, 8, 6], 26),

-- Education & Intellect (27-30)
('academic_focus_memory', 'education_intellect', 'Lack of Concentration & Weak Memory', 'à®•à®²à¯à®µà®¿à®¯à®¿à®²à¯ à®•à®µà®©à®•à¯à®•à¯à®±à¯ˆà®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®¨à®¿à®©à¯ˆà®µà®¾à®±à¯à®±à®²à¯ à®®à®¨à¯à®¤à®®à¯', 
 'Mental distractions, poor retention of lessons, and study restlessness in students.', 
 'à®ªà®Ÿà®¿à®ªà¯à®ªà®¿à®²à¯ à®•à®µà®©à®®à¯ à®šà¯†à®²à¯à®¤à¯à®¤ à®®à¯à®Ÿà®¿à®¯à®¾à®®à¯ˆ, à®¨à®¿à®©à¯ˆà®µà®¾à®±à¯à®±à®²à¯ à®•à¯à®±à¯ˆà®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®¨à¯à®¤ à®¨à®¿à®²à¯ˆ.', 
 ARRAY['mercury', 'moon', 'jupiter'], ARRAY[4, 5, 1], 27),

('exam_competitive_hurdles', 'education_intellect', 'Competitive Exam Hurdles', 'à®ªà¯‹à®Ÿà¯à®Ÿà®¿à®¤à¯ à®¤à¯‡à®°à¯à®µà¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¨à¯‡à®°à¯à®®à¯à®•à®¤à¯ à®¤à¯‡à®°à¯à®µà¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Falling short by small margins in government or professional competitive examinations.', 
 'à®ªà¯‹à®Ÿà¯à®Ÿà®¿à®¤à¯ à®¤à¯‡à®°à¯à®µà¯à®•à®³à¯, à®¨à¯‡à®°à¯à®®à¯à®•à®¤à¯ à®¤à¯‡à®°à¯à®µà¯à®•à®³à®¿à®²à¯ à®¤à¯Šà®Ÿà®°à¯à®¨à¯à®¤à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®®à®¯à®¿à®°à®¿à®´à¯ˆà®¤à¯ à®¤à¯‹à®²à¯à®µà®¿à®•à®³à¯.', 
 ARRAY['mercury', 'sun', 'mars'], ARRAY[5, 6, 10], 28),

('speech_communication_blocks', 'education_intellect', 'Speech Impediments & Stammering', 'à®ªà¯‡à®šà¯à®šà¯à®¤à¯ à®¤à®Ÿà¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à®¯à®•à¯à®•à®®à¯', 
 'Vocal hesitation, stammering, fear of public address, or ineffective communication.', 
 'à®ªà¯‡à®šà¯à®µà®¤à®¿à®²à¯ à®¤à®¯à®•à¯à®•à®®à¯, à®¤à®¿à®•à¯à®•à¯à®µà®¾à®¯à¯, à®ªà¯Šà®¤à¯ à®‡à®Ÿà®™à¯à®•à®³à®¿à®²à¯ à®ªà¯‡à®šà¯à®®à¯ à®ªà®¯à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà¯Šà®±à¯à®•à¯à®³à®±à¯à®ªà®Ÿà®¿à®•à®³à¯.', 
 ARRAY['mercury', 'jupiter', 'ketu'], ARRAY[2, 3, 1], 29),

('higher_education_obstacles', 'education_intellect', 'Higher Education & Research Blocks', 'à®‰à®¯à®°à¯ à®•à®²à¯à®µà®¿ à®®à®±à¯à®±à¯à®®à¯ à®†à®°à®¾à®¯à¯à®šà¯à®šà®¿à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Hurdles in securing university admission, mentor disagreements, or delayed doctoral degrees.', 
 'à®ªà®²à¯à®•à®²à¯ˆà®•à¯à®•à®´à®• à®šà¯‡à®°à¯à®•à¯à®•à¯ˆ, à®®à¯à®©à¯ˆà®µà®°à¯ à®ªà®Ÿà¯à®Ÿ à®†à®°à®¾à®¯à¯à®šà¯à®šà®¿ à®®à®±à¯à®±à¯à®®à¯ à®‰à®¯à®°à¯ à®•à®²à¯à®µà®¿à®¯à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®®à¯à®Ÿà¯à®Ÿà¯à®•à¯à®•à®Ÿà¯à®Ÿà¯ˆà®•à®³à¯.', 
 ARRAY['jupiter', 'mercury', 'sun'], ARRAY[9, 5, 4], 30),

-- Spiritual Growth & Karmic (31-35)
('spiritual_stagnation', 'spiritual_growth', 'Spiritual Stagnation & Meditation Restlessness', 'à®†à®©à¯à®®à¯€à®• à®®à¯à®©à¯à®©à¯‡à®±à¯à®±à®®à®¿à®©à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¤à®¿à®¯à®¾à®©à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Difficulty settling the wandering mind, lack of spiritual inspiration, and inner void.', 
 'à®¤à®¿à®¯à®¾à®©à®¤à¯à®¤à®¿à®²à¯ à®®à®©à®®à¯ à®’à®°à¯à®®à¯à®•à®ªà¯à®ªà®Ÿà®¾à®®à¯ˆ, à®†à®©à¯à®®à¯€à®•à®¤à¯ à®¤à¯‡à®•à¯à®• à®¨à®¿à®²à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®®à®©à®šà¯à®šà¯‹à®°à¯à®µà¯.', 
 ARRAY['ketu', 'jupiter', 'saturn'], ARRAY[12, 9, 8], 31),

('fear_negative_energies', 'spiritual_growth', 'Fear, Evil Eye & Psychological Unease', 'à®µà®¿à®³à®•à¯à®• à®®à¯à®Ÿà®¿à®¯à®¾à®¤ à®…à®šà¯à®šà®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®•à®£à¯ à®¤à®¿à®°à¯à®·à¯à®Ÿà®¿', 
 'Unexplained dread, pervasive sense of negative scrutiny, and psychic heaviness.', 
 'à®•à®£à¯ à®¤à®¿à®°à¯à®·à¯à®Ÿà®¿, à®•à®¾à®°à®£à®®à®¿à®²à¯à®²à®¾à®¤ à®ªà®¯à®®à¯, à®•à¯†à®Ÿà¯à®Ÿ à®Žà®£à¯à®£à®™à¯à®•à®³à®¿à®©à¯ à®¤à®¾à®•à¯à®•à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®Žà®¤à®¿à®°à¯à®®à®±à¯ˆ à®…à®¤à®¿à®°à¯à®µà¯à®•à®³à¯.', 
 ARRAY['rahu', 'mars', 'ketu'], ARRAY[8, 12, 6], 32),

('ancestral_karmic_blocks', 'spiritual_growth', 'Ancestral Karmic Burdens (Pitru Dosha)', 'à®ªà®¿à®¤à¯à®°à¯ à®¤à¯‹à®·à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à¯à®©à¯à®©à¯‹à®°à¯à®•à®³à®¿à®©à¯ à®†à®šà®¿à®¯à®¿à®©à¯à®®à¯ˆ', 
 'Recurrent unexplainable hardships indicating unresolved ancestral rites or karmic obligations.', 
 'à®•à¯à®Ÿà¯à®®à¯à®ªà®¤à¯à®¤à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®µà®¿à®µà®°à®¿à®•à¯à®• à®®à¯à®Ÿà®¿à®¯à®¾à®¤ à®¤à®Ÿà¯ˆà®•à®³à¯, à®µà®®à¯à®šà®¾à®µà®³à®¿ à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®¿à®¤à¯à®°à¯ à®¤à¯‹à®· à®…à®±à®¿à®•à¯à®±à®¿à®•à®³à¯.', 
 ARRAY['sun', 'rahu', 'saturn'], ARRAY[9, 5, 8], 33),

('recurrent_nightmares', 'spiritual_growth', 'Disturbed Sleep & Recurrent Nightmares', 'à®•à¯†à®Ÿà¯à®Ÿ à®•à®©à®µà¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®‡à®°à®µà®¿à®²à¯ à®ªà®¯à®®à¯', 
 'Frightening dreams, sleep paralysis, and distress upon waking during the night.', 
 'à®‡à®°à®µà®¿à®²à¯ à®¤à®¿à®Ÿà¯à®•à¯à®•à®¿à®Ÿà¯à®Ÿà¯ à®µà®¿à®´à®¿à®¤à¯à®¤à®²à¯, à®ªà®¯à®®à¯à®±à¯à®¤à¯à®¤à¯à®®à¯ à®•à¯†à®Ÿà¯à®Ÿ à®•à®©à®µà¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯‚à®•à¯à®•à®•à¯ à®•à®²à®•à¯à®•à®®à¯.', 
 ARRAY['moon', 'rahu', 'ketu'], ARRAY[12, 4, 8], 34),

('past_life_karmic_burdens', 'spiritual_growth', 'Unexplainable Karmic Hardships (Prarabdha)', 'à®•à®¾à®°à®£à®®à®±à¯à®± à®¤à¯Šà®Ÿà®°à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®¿à®°à®¾à®°à®ªà¯à®¤ à®•à®°à¯à®®à®¾', 
 'Obstacles persisting despite faultless planning, requiring surrender and spiritual propitiation.', 
 'à®…à®©à¯ˆà®¤à¯à®¤à¯ à®®à¯à®¯à®±à¯à®šà®¿à®•à®³à¯à®®à¯ à®‡à®°à¯à®¨à¯à®¤à¯à®®à¯ à®•à®¾à®°à®£à®®à®¿à®©à¯à®±à®¿ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®¤à¯‹à®²à¯à®µà®¿à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¿à®¤à®¿à®ªà¯à®ªà®¯à®©à¯ à®¤à®Ÿà¯ˆà®•à®³à¯.', 
 ARRAY['saturn', 'ketu', 'jupiter'], ARRAY[12, 8, 9], 35),

-- Travel & Foreign (36-39)
('visa_immigration_delays', 'travel_foreign', 'Visa & Immigration Delays', 'à®µà®¿à®šà®¾ à®®à®±à¯à®±à¯à®®à¯ à®µà¯†à®³à®¿à®¨à®¾à®Ÿà¯à®Ÿà¯à®ªà¯ à®ªà®¯à®£à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯', 
 'Red tape, consulate rejections, and prolonged delays in securing international travel permits.', 
 'à®µà®¿à®šà®¾ à®•à®¿à®Ÿà¯ˆà®ªà¯à®ªà®¤à®¿à®²à¯ à®•à®¾à®²à®¤à®¾à®®à®¤à®®à¯, à®¤à¯‚à®¤à®°à®• à®®à¯à®Ÿà¯à®Ÿà¯à®•à¯à®•à®Ÿà¯à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà¯†à®³à®¿à®¨à®¾à®Ÿà¯à®Ÿà¯à®ªà¯ à®ªà®¯à®£à®¤à¯ à®¤à®Ÿà¯ˆà®•à®³à¯.', 
 ARRAY['rahu', 'moon', 'jupiter'], ARRAY[9, 12, 3], 36),

('foreign_settlement_hardships', 'travel_foreign', 'Hardships in Foreign Settlement', 'à®µà¯†à®³à®¿à®¨à®¾à®Ÿà¯à®Ÿà®¿à®²à¯ à®•à¯à®Ÿà®¿à®¯à®®à®°à¯à®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®µà¯‡à®²à¯ˆà®ªà¯ à®ªà®¿à®°à®šà¯à®šà®¿à®©à¯ˆà®•à®³à¯', 
 'Struggles in finding secure employment, permanent residency, or stability abroad.', 
 'à®µà¯†à®³à®¿à®¨à®¾à®Ÿà¯à®Ÿà®¿à®²à¯ à®¨à®¿à®°à®¨à¯à®¤à®°à®•à¯ à®•à¯à®Ÿà®¿à®¯à¯à®°à®¿à®®à¯ˆ, à®¨à®²à¯à®² à®µà¯‡à®²à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®´à¯à®•à¯à®•à¯ˆ à®…à®®à¯ˆà®µà®¤à®¿à®²à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®‡à®©à¯à®©à®²à¯à®•à®³à¯.', 
 ARRAY['rahu', 'saturn', 'venus'], ARRAY[12, 9, 7], 37),

('relocation_adjustment_stress', 'travel_foreign', 'Relocation & City Change Stress', 'à®‡à®Ÿà®ªà¯à®ªà¯†à®¯à®°à¯à®µà¯ à®®à®±à¯à®±à¯à®®à¯ à®Šà®°à¯ à®®à®¾à®±à¯à®±à®¤à¯ à®¤à¯à®¯à®°à®®à¯', 
 'Disorientation, loneliness, and adaptation difficulties after shifting domestic location.', 
 'à®ªà¯à®¤à®¿à®¯ à®Šà®°à¯ à®…à®²à¯à®²à®¤à¯ à®µà¯€à®Ÿà¯à®Ÿà®¿à®±à¯à®•à¯ à®®à®¾à®±à®¿à®¯ à®ªà®¿à®©à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®‰à®Ÿà®²à¯/à®®à®© à®¨à®²à®•à¯ à®•à¯à®±à¯ˆà®ªà®¾à®Ÿà¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà®™à¯à®•à®Ÿà®™à¯à®•à®³à¯.', 
 ARRAY['moon', 'mercury', 'saturn'], ARRAY[4, 12, 3], 38),

('frequent_travel_mishaps', 'travel_foreign', 'Frequent Travel Mishaps & Delays', 'à®ªà®¯à®£à®™à¯à®•à®³à®¿à®²à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®‡à®´à®ªà¯à®ªà¯à®•à®³à¯', 
 'Lost luggage, missed connections, cancellations, and physical exhaustion during journeys.', 
 'à®ªà®¯à®£à®™à¯à®•à®³à®¿à®©à¯ à®ªà¯‹à®¤à¯ à®à®±à¯à®ªà®Ÿà¯à®®à¯ à®ªà¯Šà®°à¯à®Ÿà¯à®•à®³à¯ à®‡à®´à®ªà¯à®ªà¯, à®µà®¿à®ªà®¤à¯à®¤à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à¯Šà®Ÿà®°à¯ à®…à®²à¯ˆà®šà¯à®šà®²à¯à®•à®³à¯.', 
 ARRAY['mercury', 'moon', 'mars'], ARRAY[3, 9, 8], 39)

ON CONFLICT (slug) DO UPDATE SET
    category = EXCLUDED.category,
    name_en = EXCLUDED.name_en,
    name_ta = EXCLUDED.name_ta,
    description_en = EXCLUDED.description_en,
    description_ta = EXCLUDED.description_ta,
    primary_karakas = EXCLUDED.primary_karakas,
    governing_houses = EXCLUDED.governing_houses,
    display_order = EXCLUDED.display_order,
    updated_at = NOW();

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 9. Seed: The 9 Authentic Kaveri Delta Tamil Navagraha Temples
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO public.navagraha_temples (
    code, graha, name_en, name_ta, presiding_deity_en, presiding_deity_ta,
    graha_deity_en, graha_deity_ta, place_name_en, place_name_ta,
    district_en, district_ta, state, latitude, longitude,
    visiting_day_en, visiting_day_ta, significance_en, significance_ta,
    remedy_offerings_en, remedy_offerings_ta, source_tradition
) VALUES
('TEMPLE_SURYANAR_KOVIL', 'sun', 
 'Suryanar Kovil', 'à®šà¯‚à®°à®¿à®¯à®©à®¾à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Suryanarayana Swamy', 'à®¸à¯à®°à¯€ à®šà¯‚à®°à®¿à®¯à®¨à®¾à®°à®¾à®¯à®£ à®šà¯à®µà®¾à®®à®¿',
 'Lord Surya (Sun)', 'à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯',
 'Suryanar Kovil (near Aduthurai)', 'à®šà¯‚à®°à®¿à®¯à®©à®¾à®°à¯ à®•à¯‹à®µà®¿à®²à¯ (à®†à®Ÿà¯à®¤à¯à®±à¯ˆ à®…à®°à¯à®•à®¿à®²à¯)',
 'Thanjavur', 'à®¤à®žà¯à®šà®¾à®µà¯‚à®°à¯', 'Tamil Nadu', 11.025300, 79.489100,
 'Sunday', 'à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'The premier Sun temple in Tamil Nadu where Lord Surya is worshipped with his consorts Usha and Chhaya. Uniquely houses shrines for all other eight grahas facing Surya.',
 'à®¤à®®à®¿à®´à®•à®¤à¯à®¤à®¿à®©à¯ à®®à¯à®¤à®©à¯à®®à¯ˆ à®šà¯‚à®°à®¿à®¯ à®¤à®²à®®à¯. à®‰à®·à®¾, à®šà®¾à®¯à®¾ à®¤à¯‡à®µà®¿à®¯à®°à¯à®Ÿà®©à¯ à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯ à®…à®°à¯à®³à¯à®ªà®¾à®²à®¿à®•à¯à®•à®¿à®±à®¾à®°à¯. à®®à®±à¯à®± à®Žà®Ÿà¯à®Ÿà¯ à®•à®¿à®°à®•à®™à¯à®•à®³à¯à®®à¯ à®šà¯‚à®°à®¿à®¯à®©à¯ˆ à®¨à¯‹à®•à¯à®•à®¿à®¯à®µà®¾à®±à¯ à®¤à®©à®¿à®¤à¯à®¤à®©à®¿ à®šà®©à¯à®©à®¤à®¿à®•à®³à®¿à®²à¯ à®…à®®à¯ˆà®¨à¯à®¤à®¿à®°à¯à®ªà¯à®ªà®¤à¯ à®‡à®¤à®©à¯ à®¤à®©à®¿à®šà¯à®šà®¿à®±à®ªà¯à®ªà¯.',
 'Offering wheat, jaggery, red flowers, lighting ghee lamps, performing circumambulation (pradakshina) on Sundays at dawn.',
 'à®•à¯‹à®¤à¯à®®à¯ˆ, à®µà¯†à®²à¯à®²à®®à¯, à®šà¯†à®¨à¯à®¤à®¾à®®à®°à¯ˆ à®®à®²à®°à¯à®•à®³à¯ à®šà®®à®°à¯à®ªà¯à®ªà®¿à®¤à¯à®¤à®²à¯, à®¨à¯†à®¯à¯ à®¤à¯€à®ªà®®à¯ à®à®±à¯à®±à¯à®¤à®²à¯ à®®à®±à¯à®±à¯à®®à¯ à®žà®¾à®¯à®¿à®±à¯ à®…à®¤à®¿à®•à®¾à®²à¯ˆ à®ªà®¿à®°à®¤à®Ÿà¯à®šà®£à®®à¯ à®šà¯†à®¯à¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THINGALUR', 'moon',
 'Thingalur Kailasanathar Temple', 'à®¤à®¿à®™à¯à®•à®³à¯‚à®°à¯ à®•à¯ˆà®²à®¾à®šà®¨à®¾à®¤à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Kailasanathar and Goddess Periyanayaki', 'à®¸à¯à®°à¯€ à®•à¯ˆà®²à®¾à®šà®¨à®¾à®¤à®°à¯ - à®ªà¯†à®°à®¿à®¯à®¨à®¾à®¯à®•à®¿ à®…à®®à¯à®®à®©à¯',
 'Lord Chandra (Moon)', 'à®šà®¨à¯à®¤à®¿à®° à®ªà®•à®µà®¾à®©à¯',
 'Thingalur (near Thiruvaiyaru)', 'à®¤à®¿à®™à¯à®•à®³à¯‚à®°à¯ (à®¤à®¿à®°à¯à®µà¯ˆà®¯à®¾à®±à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Thanjavur', 'à®¤à®žà¯à®šà®¾à®µà¯‚à®°à¯', 'Tamil Nadu', 10.878900, 79.167800,
 'Monday', 'à®¤à®¿à®™à¯à®•à®Ÿà¯à®•à®¿à®´à®®à¯ˆ',
 'Classical Moon sthalam where Lord Moon worshipped Shiva to regain luminosity. Associated with relief from maternal distress, mental instability, and emotional turmoil.',
 'à®šà®¨à¯à®¤à®¿à®° à®¤à¯‹à®· à®¨à®¿à®µà®°à¯à®¤à¯à®¤à®¿ à®¤à®²à®®à¯. à®šà®¨à¯à®¤à®¿à®°à®©à¯ à®šà®¿à®µà®ªà¯†à®°à¯à®®à®¾à®©à¯ˆ à®ªà¯‚à®œà®¿à®¤à¯à®¤à¯ à®šà®¾à®ª à®µà®¿à®®à¯‹à®šà®©à®®à¯ à®ªà¯†à®±à¯à®± à®‡à®Ÿà®®à¯. à®®à®© à®…à®®à¯ˆà®¤à®¿, à®¤à®¾à®¯à®¾à®°à¯ à®¨à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®•à®²à¯à®µà®¿ à®®à¯‡à®©à¯à®®à¯ˆ à®…à®°à¯à®³à¯à®®à¯ à®¤à®²à®®à¯.',
 'Offering white raw rice, milk kheer (payasam), white cloth, white arali flowers, lighting lamps on Mondays.',
 'à®ªà®šà¯à®šà®°à®¿à®šà®¿, à®ªà®šà¯à®®à¯à®ªà®¾à®²à¯ à®ªà®¾à®¯à®¾à®šà®®à¯, à®µà¯†à®³à¯à®³à¯ˆ à®µà®¸à¯à®¤à®¿à®°à®®à¯, à®µà¯†à®³à¯à®³à¯ˆ à®…à®°à®³à®¿ à®®à®²à®°à¯à®•à®³à¯ à®šà®¾à®±à¯à®±à®¿ à®¤à®¿à®™à¯à®•à®³à¯à®•à®¿à®´à®®à¯ˆ à®µà®´à®¿à®ªà®¾à®Ÿà¯ à®šà¯†à®¯à¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_VAITHEESWARAN', 'mars',
 'Vaitheeswaran Kovil', 'à®µà¯ˆà®¤à¯à®¤à¯€à®¸à¯à®µà®°à®©à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Vaidyanatha Swamy and Goddess Thaiyalnayaki', 'à®¸à¯à®°à¯€ à®µà¯ˆà®¤à¯à®¤à®¿à®¯à®¨à®¾à®¤ à®šà¯à®µà®¾à®®à®¿ - à®¤à¯ˆà®¯à®²à¯à®¨à®¾à®¯à®•à®¿ à®…à®®à¯à®®à®©à¯',
 'Lord Sevvai / Angarakan (Mars)', 'à®…à®™à¯à®•à®¾à®°à®•à®©à¯ / à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®ªà®•à®µà®¾à®©à¯',
 'Vaitheeswaran Kovil (near Sirkazhi)', 'à®µà¯ˆà®¤à¯à®¤à¯€à®¸à¯à®µà®°à®©à¯ à®•à¯‹à®µà®¿à®²à¯ (à®šà¯€à®°à¯à®•à®¾à®´à®¿ à®…à®°à¯à®•à®¿à®²à¯)',
 'Mayiladuthurai', 'à®®à®¯à®¿à®²à®¾à®Ÿà¯à®¤à¯à®±à¯ˆ', 'Tamil Nadu', 11.202300, 79.731400,
 'Tuesday', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'World-renowned healing sthalam and supreme Mars (Angaraka) pilgrimage. Lord Shiva as the Divine Physician heals physical ailments, removes Kuja / Manglik dosha, and settles property obstacles.',
 'à®ªà¯à®•à®´à¯à®ªà¯†à®±à¯à®± à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®¸à¯à®¤à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®ªà®¿à®£à®¿ à®¤à¯€à®°à¯à®•à¯à®•à¯à®®à¯ à®¤à®²à®®à¯. à®µà¯ˆà®¤à¯à®¤à¯€à®¸à¯à®µà®°à®°à¯ à®šà®¿à®¤à¯à®¤à®¾à®®à®¿à®°à¯à®¤ à®¤à¯€à®°à¯à®¤à¯à®¤à®¤à¯à®¤à¯à®Ÿà®©à¯ à®¤à¯€à®°à®¾à®¤ à®¨à¯‹à®¯à¯à®•à®³à¯ˆà®¤à¯ à®¤à¯€à®°à¯à®¤à¯à®¤à¯, à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®¤à¯‹à®·à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®¨à®¿à®²à®®à¯ à®šà®¾à®°à¯à®¨à¯à®¤ à®¤à®Ÿà¯ˆà®•à®³à¯ˆ à®¨à¯€à®•à¯à®•à¯à®•à®¿à®±à®¾à®°à¯.',
 'Offering red lentils (thoor/masoor dal), red cloth, vilvam leaves, and lighting sesame/ghee lamps on Tuesdays.',
 'à®¤à¯à®µà®°à®®à¯à®ªà®°à¯à®ªà¯à®ªà¯, à®šà®¿à®µà®ªà¯à®ªà¯ à®µà®¸à¯à®¤à®¿à®°à®®à¯, à®šà¯†à®µà¯à®µà®°à®³à®¿ à®®à®¾à®²à¯ˆ à®šà®¾à®±à¯à®±à®¿, à®šà®¿à®¤à¯à®¤à®¾à®®à®¿à®°à¯à®¤ à®¤à¯€à®°à¯à®¤à¯à®¤à®¤à¯à®¤à®¿à®²à¯ à®¨à¯€à®°à®¾à®Ÿà®¿ à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUVENKADU', 'mercury',
 'Thiruvenkadu Swetharanyeswarar Temple', 'à®¤à®¿à®°à¯à®µà¯†à®£à¯à®•à®¾à®Ÿà¯ à®šà¯à®µà¯‡à®¤à®¾à®°à®£à¯à®¯à¯‡à®¸à¯à®µà®°à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Swetharanyeswarar and Goddess Brahmavidyambigai', 'à®¸à¯à®°à¯€ à®šà¯à®µà¯‡à®¤à®¾à®°à®£à¯à®¯à¯‡à®¸à¯à®µà®°à®°à¯ - à®ªà®¿à®°à®®à¯à®®à®µà®¿à®¤à¯à®¯à®¾à®®à¯à®ªà®¿à®•à¯ˆ',
 'Lord Budhan (Mercury)', 'à®ªà¯à®¤à®©à¯ à®ªà®•à®µà®¾à®©à¯',
 'Thiruvenkadu (near Poompuhar)', 'à®¤à®¿à®°à¯à®µà¯†à®£à¯à®•à®¾à®Ÿà¯ (à®ªà¯‚à®®à¯à®ªà¯à®•à®¾à®°à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Mayiladuthurai', 'à®®à®¯à®¿à®²à®¾à®Ÿà¯à®¤à¯à®±à¯ˆ', 'Tamil Nadu', 11.178900, 79.823400,
 'Wednesday', 'à®ªà¯à®¤à®©à¯à®•à®¿à®´à®®à¯ˆ',
 'Venerated Mercury sthalam known as the Adi Chidambaram. Famed for granting intellectual brilliance, educational excellence, musical talents, and healing nervous disorders.',
 'à®†à®¤à®¿ à®šà®¿à®¤à®®à¯à®ªà®°à®®à¯ à®Žà®©à¯à®±à¯ à®ªà¯‹à®±à¯à®±à®ªà¯à®ªà®Ÿà¯à®®à¯ à®ªà¯à®¤à®©à¯ à®¤à®²à®®à¯. à®ªà¯à®¤à®©à¯ à®ªà®•à®µà®¾à®©à¯ à®¤à®©à®¿ à®šà®©à¯à®©à®¤à®¿à®¯à®¿à®²à¯ à®…à®°à¯à®³à¯à®•à®¿à®±à®¾à®°à¯. à®•à®²à¯à®µà®¿, à®ªà¯‡à®šà¯à®šà¯à®¤à¯à®¤à®¿à®±à®©à¯, à®µà®£à®¿à®• à®®à¯‡à®©à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®¨à®°à®®à¯à®ªà¯ à®®à®£à¯à®Ÿà®² à®†à®°à¯‹à®•à¯à®•à®¿à®¯à®®à¯ à®…à®°à¯à®³à¯à®®à¯ à®¤à®²à®®à¯.',
 'Offering green gram (moong dal), green cloth, vilvam leaves, tulasi, lighting lamps on Wednesdays.',
 'à®ªà®šà¯à®šà¯ˆà®ªà¯à®ªà®¯à®±à¯, à®ªà®šà¯à®šà¯ˆ à®µà®¸à¯à®¤à®¿à®°à®®à¯, à®µà¯†à®£à¯à®•à®¾à®¨à¯à®¤à®³à¯/à®¤à¯à®³à®šà®¿ à®®à®¾à®²à¯ˆ à®šà®¾à®±à¯à®±à®¿ à®ªà¯à®¤à®©à¯à®•à®¿à®´à®®à¯ˆ à®¤à¯‹à®±à¯à®®à¯ à®¨à¯†à®¯à¯ à®¤à¯€à®ªà®®à®¿à®Ÿà¯à®Ÿà¯ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_ALANGUDI', 'jupiter',
 'Alangudi Apatsahayeswarar Temple', 'à®†à®²à®™à¯à®•à¯à®Ÿà®¿ à®†à®ªà®¤à¯à®šà®•à®¾à®¯à¯‡à®¸à¯à®µà®°à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Apatsahayeswarar and Goddess Elavarkuzhali', 'à®¸à¯à®°à¯€ à®†à®ªà®¤à¯à®šà®•à®¾à®¯à¯‡à®¸à¯à®µà®°à®°à¯ - à®à®²à®µà®¾à®°à¯à®•à¯à®´à®²à®¿ à®…à®®à¯à®®à®©à¯',
 'Lord Guru (Jupiter / Dakshinamurthy)', 'à®•à¯à®°à¯ à®ªà®•à®µà®¾à®©à¯ / à®¤à®Ÿà¯à®šà®¿à®£à®¾à®®à¯‚à®°à¯à®¤à¯à®¤à®¿',
 'Alangudi (near Valangaiman)', 'à®†à®²à®™à¯à®•à¯à®Ÿà®¿ (à®µà®²à®™à¯à®•à¯ˆà®®à®¾à®©à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Tiruvarur', 'à®¤à®¿à®°à¯à®µà®¾à®°à¯‚à®°à¯', 'Tamil Nadu', 10.825600, 79.408900,
 'Thursday', 'à®µà®¿à®¯à®¾à®´à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'Foremost Jupiter sthalam where Lord Shiva consumed poison to protect the universe. Dedicated Guru shrine worshipped for marital blessings, child boon, spiritual wisdom, and career growth.',
 'à®¤à®²à¯ˆà®šà®¿à®±à®¨à¯à®¤ à®•à¯à®°à¯ à®ªà®°à®¿à®•à®¾à®°à®¤à¯ à®¤à®²à®®à¯. à®†à®ªà®¤à¯à®šà®•à®¾à®¯à¯‡à®¸à¯à®µà®°à®°à¯ à®†à®²à®•à®¾à®² à®µà®¿à®·à®®à¯ à®‰à®£à¯à®Ÿà¯ à®¤à¯‡à®µà®°à¯à®•à®³à¯ˆà®•à¯ à®•à®¾à®¤à¯à®¤ à®‡à®Ÿà®®à¯. à®¤à®¿à®°à¯à®®à®£ à®ªà®¾à®•à¯à®•à®¿à®¯à®®à¯, à®ªà¯à®¤à¯à®¤à®¿à®° à®ªà®¾à®•à¯à®•à®¿à®¯à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®žà®¾à®©à®®à¯ à®µà¯‡à®£à¯à®Ÿà®¿ à®ªà®•à¯à®¤à®°à¯à®•à®³à¯ à®•à¯‚à®Ÿà¯à®®à¯ à®ªà¯à®£à¯à®£à®¿à®¯ à®¤à®²à®®à¯.',
 'Offering yellow split chana dal garland, yellow cloth, mullai flowers, lighting 24 ghee deepams on Thursdays.',
 'à®•à¯Šà®£à¯à®Ÿà¯ˆà®•à¯à®•à®Ÿà®²à¯ˆ à®®à®¾à®²à¯ˆ, à®®à®žà¯à®šà®³à¯ à®µà®¸à¯à®¤à®¿à®°à®®à¯, à®®à¯à®²à¯à®²à¯ˆ à®®à®²à®°à¯à®•à®³à¯ à®šà®¾à®±à¯à®±à®¿ 24 à®¨à¯†à®¯à¯ à®¤à¯€à®ªà®™à¯à®•à®³à¯ à®à®±à¯à®±à®¿ à®µà®¿à®¯à®¾à®´à®•à¯à®•à®¿à®´à®®à¯ˆ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_KANJANUR', 'venus',
 'Kanjanur Agneeswarar Temple', 'à®•à®žà¯à®šà®©à¯‚à®°à¯ à®…à®•à¯à®©à¯€à®¸à¯à®µà®°à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Agneeswarar and Goddess Karpagambal', 'à®¸à¯à®°à¯€ à®…à®•à¯à®©à¯€à®¸à¯à®µà®°à®°à¯ - à®•à®±à¯à®ªà®•à®¾à®®à¯à®ªà®¾à®³à¯',
 'Lord Sukran (Venus)', 'à®šà¯à®•à¯à®•à®¿à®° à®ªà®•à®µà®¾à®©à¯',
 'Kanjanur (near Kumbakonam)', 'à®•à®žà¯à®šà®©à¯‚à®°à¯ (à®•à¯à®®à¯à®ªà®•à¯‹à®£à®®à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Thanjavur', 'à®¤à®žà¯à®šà®¾à®µà¯‚à®°à¯', 'Tamil Nadu', 11.066700, 79.483300,
 'Friday', 'à®µà¯†à®³à¯à®³à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'Supreme Venus sthalam. Agni Bhagavan worshipped Shiva here to be cured of affliction. Lord Shiva himself reflects the radiant qualities of Sukra here, blessing devotees with prosperity and artistic flourish.',
 'à®šà¯à®•à¯à®•à®¿à®° à®ªà®•à®µà®¾à®©à¯ à®µà®´à®¿à®ªà®Ÿà¯à®Ÿ à®®à¯à®•à¯à®•à®¿à®¯ à®¤à®²à®®à¯. à®‡à®™à¯à®•à¯ à®šà®¿à®µà®ªà¯†à®°à¯à®®à®¾à®©à¯‡ à®šà¯à®•à¯à®•à®¿à®°à®©à®¿à®©à¯ à®…à®®à¯à®šà®®à®¾à®• à®…à®°à¯à®³à¯à®ªà®¾à®²à®¿à®•à¯à®•à®¿à®±à®¾à®°à¯. à®¤à®®à¯à®ªà®¤à®¿à®¯à®°à¯ à®’à®±à¯à®±à¯à®®à¯ˆ, à®šà¯†à®²à¯à®µà®®à¯, à®•à®²à¯ˆ à®žà®¾à®©à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®•à®© à®¯à¯‹à®•à®®à¯ à®¨à®²à¯à®•à¯à®®à¯ à®¤à®²à®®à¯.',
 'Offering white field beans (mochai), white silk cloth, white lotus, sweet milk dishes on Fridays.',
 'à®®à¯Šà®šà¯à®šà¯ˆà®ªà¯à®ªà®¯à®±à¯, à®µà¯†à®£à¯à®ªà®Ÿà¯à®Ÿà¯, à®µà¯†à®£à¯à®¤à®¾à®®à®°à¯ˆ à®®à®²à®°à¯à®•à®³à¯ à®šà®¾à®±à¯à®±à®¿, à®šà®°à¯à®•à¯à®•à®°à¯ˆà®ªà¯ à®ªà¯Šà®™à¯à®•à®²à¯ à®…à®²à¯à®²à®¤à¯ à®ªà®¾à®¯à®¾à®šà®®à¯ à®ªà®Ÿà¯ˆà®¤à¯à®¤à¯ à®µà¯†à®³à¯à®³à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUNALLAR', 'saturn',
 'Thirunallar Dharbaranyeswarar Temple', 'à®¤à®¿à®°à¯à®¨à®³à¯à®³à®¾à®±à¯ à®¤à®°à¯à®ªà®¾à®°à®£à¯à®¯à¯‡à®¸à¯à®µà®°à®°à¯ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Dharbaranyeswarar and Goddess Pranambigai', 'à®¸à¯à®°à¯€ à®¤à®°à¯à®ªà®¾à®°à®£à¯à®¯à¯‡à®¸à¯à®µà®°à®°à¯ - à®ªà®¿à®°à®¾à®£à®¾à®®à¯à®ªà®¿à®•à¯ˆ',
 'Lord Saneeswara (Saturn)', 'à®¸à¯à®°à¯€ à®šà®©à¯€à®¸à¯à®µà®° à®ªà®•à®µà®¾à®©à¯',
 'Thirunallar (near Karaikal)', 'à®¤à®¿à®°à¯à®¨à®³à¯à®³à®¾à®±à¯ (à®•à®¾à®°à¯ˆà®•à¯à®•à®¾à®²à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Karaikal / Puducherry-TN Border', 'à®•à®¾à®°à¯ˆà®•à¯à®•à®¾à®²à¯ / à®¤à®®à®¿à®´à®• à®Žà®²à¯à®²à¯ˆ', 'Puducherry / Tamil Nadu', 10.927200, 79.791100,
 'Saturday', 'à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'World-renowned Saturn shrine where King Nala was released from the malefic grip of Saturn after bathing in the Nala Theertham. Propitiated for Sade Sati, Ashtama Shani, and chronic hurdles.',
 'à®‰à®²à®•à®ªà¯ à®ªà¯à®•à®´à¯à®ªà¯†à®±à¯à®± à®šà®©à®¿ à®ªà®°à®¿à®•à®¾à®° à®¸à¯à®¤à®²à®®à¯. à®¨à®³ à®¤à®®à®¯à®¨à¯à®¤à®¿ à®ªà¯à®°à®¾à®£à®¤à¯à®¤à¯à®Ÿà®©à¯ à®¤à¯Šà®Ÿà®°à¯à®ªà¯à®Ÿà¯ˆà®¯à®¤à¯. à®¨à®³ à®¤à¯€à®°à¯à®¤à¯à®¤à®¤à¯à®¤à®¿à®²à¯ à®¨à¯€à®°à®¾à®Ÿà®¿ à®Žà®³à¯à®¤à¯€à®ªà®®à¯ à®à®±à¯à®±à¯à®µà®¤à®©à¯ à®®à¯‚à®²à®®à¯ à®à®´à®°à¯ˆà®šà¯ à®šà®©à®¿, à®…à®·à¯à®Ÿà®®à®šà¯ à®šà®©à®¿ à®®à®±à¯à®±à¯à®®à¯ à®µà®¾à®¤ à®¨à¯‹à®¯à¯à®•à®³à®¿à®©à¯ à®¤à®¾à®•à¯à®•à®®à¯ à®¤à®£à®¿à®•à®¿à®±à®¤à¯.',
 'Holy dip in Nala Theertham, lighting black sesame oil lamps in clay pots, donating black sesame seeds and iron items on Saturdays.',
 'à®¨à®³ à®¤à¯€à®°à¯à®¤à¯à®¤à®¤à¯à®¤à®¿à®²à¯ à®¨à¯€à®°à®¾à®Ÿà®¿, à®•à®°à¯à®ªà¯à®ªà¯ à®Žà®³à¯ à®¤à¯€à®ªà®®à¯‡à®±à¯à®±à®¿, à®¨à¯€à®² à®¨à®¿à®± à®µà®¸à¯à®¤à®¿à®°à®®à¯ à®…à®²à¯à®²à®¤à¯ à®Žà®³à¯ à®¤à®¾à®©à®®à¯ à®µà®´à®™à¯à®•à®¿ à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆà®•à®³à®¿à®²à¯ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUNAGESWARAM', 'rahu',
 'Thirunageswaram Naganathaswamy Temple', 'à®¤à®¿à®°à¯à®¨à®¾à®•à¯‡à®¸à¯à®µà®°à®®à¯ à®¨à®¾à®•à®¨à®¾à®¤à®šà¯à®µà®¾à®®à®¿ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Naganathaswamy and Goddess Pirayanindasoodi', 'à®¸à¯à®°à¯€ à®¨à®¾à®•à®¨à®¾à®¤à®šà¯à®µà®¾à®®à®¿ - à®ªà®¿à®±à¯ˆà®¯à®£à®¿à®¨à¯à®¤à®šà¯‚à®Ÿà®¿ à®…à®®à¯à®®à®©à¯',
 'Lord Rahu Bhagavan', 'à®°à®¾à®•à¯ à®ªà®•à®µà®¾à®©à¯',
 'Thirunageswaram (near Kumbakonam)', 'à®¤à®¿à®°à¯à®¨à®¾à®•à¯‡à®¸à¯à®µà®°à®®à¯ (à®•à¯à®®à¯à®ªà®•à¯‹à®£à®®à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Thanjavur', 'à®¤à®žà¯à®šà®¾à®µà¯‚à®°à¯', 'Tamil Nadu', 10.963300, 79.431700,
 'Sunday (or Rahu Kalam)', 'à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ (à®°à®¾à®•à¯ à®•à®¾à®²à®®à¯)',
 'Premier Rahu sthalam where Rahu Bhagavan worshipped Shiva. Famous for the miraculous milk abhishekam during Rahu Kalam, where milk poured on the idol visibly turns light blue.',
 'à®°à®¾à®•à¯ à®ªà®•à®µà®¾à®©à®¿à®©à¯ à®®à¯à®¤à®©à¯à®®à¯ˆà®ªà¯ à®ªà®°à®¿à®•à®¾à®°à®¤à¯ à®¤à®²à®®à¯. à®°à®¾à®•à¯ à®•à®¾à®²à®¤à¯à®¤à®¿à®²à¯ à®°à®¾à®•à¯ à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®šà¯†à®¯à¯à®¯à®ªà¯à®ªà®Ÿà¯à®®à¯ à®ªà®¾à®²à®¾à®ªà®¿à®·à¯‡à®•à®¤à¯à®¤à®¿à®©à¯ à®ªà¯‹à®¤à¯ à®ªà®¾à®²à¯ à®¨à¯€à®² à®¨à®¿à®±à®®à®¾à®• à®®à®¾à®±à¯à®®à¯ à®…à®¤à®¿à®šà®¯à®®à¯ à®¨à®¿à®•à®´à¯à®®à¯ à®ªà¯à®£à¯à®£à®¿à®¯ à®ªà¯‚à®®à®¿. à®¨à®¾à®• à®¤à¯‹à®·à®®à¯, à®•à®¾à®²à®šà®°à¯à®ªà¯à®ª à®¤à¯‹à®· à®¨à®¿à®µà®°à¯à®¤à¯à®¤à®¿ à®¤à®²à®®à¯.',
 'Milk Abhishekam during Rahu Kalam, offering urad dal, blue flowers, and lighting sesame oil lamps.',
 'à®°à®¾à®•à¯ à®•à®¾à®²à®¤à¯à®¤à®¿à®²à¯ à®ªà®¾à®²à®¾à®ªà®¿à®·à¯‡à®•à®®à¯ à®šà¯†à®¯à¯à®¤à®²à¯, à®‰à®³à¯à®¨à¯à®¤à¯ à®šà®®à®°à¯à®ªà¯à®ªà®¿à®¤à¯à®¤à®²à¯, à®¨à¯€à®² à®¨à®¿à®± à®®à®²à®°à¯à®•à®³à¯ à®šà®¾à®±à¯à®±à®¿ à®¨à®²à¯à®²à¯†à®£à¯à®£à¯†à®¯à¯ à®¤à¯€à®ªà®®à¯ à®à®±à¯à®±à¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_KEEZHPERUMPALLAM', 'ketu',
 'Keezhperumpallam Naganathaswamy Temple', 'à®•à¯€à®´à¯à®ªà¯à®ªà¯†à®°à¯à®®à¯à®ªà®³à¯à®³à®®à¯ à®¨à®¾à®•à®¨à®¾à®¤à®šà¯à®µà®¾à®®à®¿ à®•à¯‹à®µà®¿à®²à¯',
 'Sri Naganathaswamy and Goddess Soundaranayaki', 'à®¸à¯à®°à¯€ à®¨à®¾à®•à®¨à®¾à®¤à®šà¯à®µà®¾à®®à®¿ - à®šà¯Œà®¨à¯à®¤à®°à®¨à®¾à®¯à®•à®¿',
 'Lord Ketu Bhagavan', 'à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à¯',
 'Keezhperumpallam (near Poompuhar)', 'à®•à¯€à®´à¯à®ªà¯à®ªà¯†à®°à¯à®®à¯à®ªà®³à¯à®³à®®à¯ (à®ªà¯‚à®®à¯à®ªà¯à®•à®¾à®°à¯ à®…à®°à¯à®•à®¿à®²à¯)',
 'Mayiladuthurai', 'à®®à®¯à®¿à®²à®¾à®Ÿà¯à®¤à¯à®±à¯ˆ', 'Tamil Nadu', 11.143600, 79.845600,
 'Tuesday', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ',
 'Supreme Ketu sthalam where Ketu Bhagavan, having a human head and serpent body, worshipped Lord Shiva with folded hands for spiritual liberation and redemption.',
 'à®žà®¾à®©à®•à®¾à®°à®•à®©à®¾à®© à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à®¿à®©à¯ à®ªà®¿à®°à®¤à®¾à®© à®¤à®²à®®à¯. à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à¯ à®‡à®™à¯à®•à¯ à®®à®©à®¿à®¤ à®®à¯à®•à®¤à¯à®¤à¯à®Ÿà®©à¯à®®à¯ à®ªà®¾à®®à¯à®ªà¯ à®‰à®Ÿà®²à¯à®Ÿà®©à¯à®®à¯ à®šà®¿à®µà®ªà¯†à®°à¯à®®à®¾à®©à¯ˆ à®•à¯ˆà®•à¯‚à®ªà¯à®ªà®¿ à®µà®£à®™à¯à®•à¯à®®à¯ à®•à¯‹à®²à®¤à¯à®¤à®¿à®²à¯ à®…à®°à¯à®³à¯à®ªà®¾à®²à®¿à®•à¯à®•à®¿à®±à®¾à®°à¯. à®†à®©à¯à®®à¯€à®• à®®à¯‡à®©à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®®à¯‹à®Ÿà¯à®šà®®à¯ à®…à®°à¯à®³à¯à®®à¯ à®¤à®²à®®à¯.',
 'Offering horsegram (kollu), multi-coloured cloth, red/spotted flowers, and performing circumambulation on Tuesdays.',
 'à®•à¯Šà®³à¯à®³à¯ à®¤à®¾à®©à®®à¯ à®šà¯†à®¯à¯à®¤à®²à¯, à®ªà®²à®µà®£à¯à®£ à®µà®¸à¯à®¤à®¿à®°à®®à¯ à®šà®¾à®±à¯à®±à®¿, à®šà¯†à®µà¯à®µà®°à®³à®¿ à®®à®¾à®²à¯ˆ à®…à®£à®¿à®µà®¿à®¤à¯à®¤à¯ à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®¤à¯‹à®±à¯à®®à¯ à®µà®´à®¿à®ªà®Ÿà¯à®¤à®²à¯.',
 'Kaveri Delta Navagraha Sthalam')

ON CONFLICT (code) DO UPDATE SET
    name_en = EXCLUDED.name_en,
    name_ta = EXCLUDED.name_ta,
    presiding_deity_en = EXCLUDED.presiding_deity_en,
    presiding_deity_ta = EXCLUDED.presiding_deity_ta,
    graha_deity_en = EXCLUDED.graha_deity_en,
    graha_deity_ta = EXCLUDED.graha_deity_ta,
    place_name_en = EXCLUDED.place_name_en,
    place_name_ta = EXCLUDED.place_name_ta,
    district_en = EXCLUDED.district_en,
    district_ta = EXCLUDED.district_ta,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    visiting_day_en = EXCLUDED.visiting_day_en,
    visiting_day_ta = EXCLUDED.visiting_day_ta,
    significance_en = EXCLUDED.significance_en,
    significance_ta = EXCLUDED.significance_ta,
    remedy_offerings_en = EXCLUDED.remedy_offerings_en,
    remedy_offerings_ta = EXCLUDED.remedy_offerings_ta,
    updated_at = NOW();

-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
-- 10. Seed: Verified Remedies Catalog
-- â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
INSERT INTO public.remedies_catalog (
    code, graha, remedy_type, name_en, name_ta, description_en, description_ta,
    deity_en, deity_ta, sanskrit_text, transliteration_iast, transliteration_ta,
    meaning_en, meaning_ta, procedure_en, procedure_ta, japa_count,
    timing_recommendation_en, timing_recommendation_ta, is_pacification_only, problem_slugs
) VALUES
-- 1. Universal Ganesha Invocation
('REM_UNIV_GANESHA_01', 'universal', 'mantra',
 'Sri Ganesha Moola Mantra', 'à®¸à¯à®°à¯€ à®•à®£à¯‡à®š à®®à¯‚à®² à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Foundational Vedic invocation chanted before initiating any astrological remedy or noble spiritual practice to remove obstacles.',
 'à®Žà®¨à¯à®¤ à®’à®°à¯ à®œà¯‹à®¤à®¿à®Ÿà®ªà¯ à®ªà®°à®¿à®•à®¾à®°à®®à¯ à®…à®²à¯à®²à®¤à¯ à®šà¯à®ª à®•à®¾à®°à®¿à®¯à®¤à¯à®¤à¯ˆà®¤à¯ à®¤à¯Šà®Ÿà®™à¯à®•à¯à®µà®¤à®±à¯à®•à¯ à®®à¯à®©à¯ à®¤à®Ÿà¯ˆà®•à®³à¯ˆ à®¨à¯€à®•à¯à®•à®¿ à®µà¯†à®±à¯à®±à®¿ à®ªà¯†à®± à®‰à®šà¯à®šà®°à®¿à®•à¯à®• à®µà¯‡à®£à¯à®Ÿà®¿à®¯ à®®à¯à®´à¯à®®à¯à®¤à®±à¯ à®•à®Ÿà®µà¯à®³à¯ à®•à®£à®ªà®¤à®¿à®¯à®¿à®©à¯ à®®à¯‚à®² à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Ganesha', 'à®¸à¯à®°à¯€ à®µà®¿à®¨à®¾à®¯à®•à®ªà¯ à®ªà¯†à®°à¯à®®à®¾à®©à¯',
 'à¥ à¤—à¤‚ à¤—à¤£à¤ªà¤¤à¤¯à¥‡ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ gaá¹ƒ gaá¹‡apataye namaá¸¥ à¥¥', 'à®“à®®à¯ à®•à®®à¯ à®•à®£à®ªà®¤à®¯à¯‡ à®¨à®®à®¹ à¥¥',
 'Salutations to Lord Ganesha, the embodiment of wisdom, ruler of the celestial hosts, and the supreme remover of all hindrances.',
 'à®…à®©à¯ˆà®¤à¯à®¤à¯ à®•à®£à®™à¯à®•à®³à¯à®•à¯à®•à¯à®®à¯ à®¤à®²à¯ˆà®µà®°à¯à®®à¯, à®µà®¿à®•à¯à®•à®¿à®©à®™à¯à®•à®³à¯ˆà®¤à¯ à®¤à¯€à®°à¯à®ªà¯à®ªà®µà®°à¯à®®à®¾à®© à®µà®¿à®¨à®¾à®¯à®•à®ªà¯ à®ªà¯†à®°à¯à®®à®¾à®©à¯ˆà®ªà¯ à®ªà®£à®¿à®¨à¯à®¤à¯ à®µà®£à®™à¯à®•à¯à®•à®¿à®±à¯‡à®©à¯.',
 'Sit facing North or East. Cleanse hands and chant 108 times using a Rudraksha or Sandalwood mala before starting any planetary remedies.',
 'à®µà®Ÿà®•à¯à®•à¯ à®…à®²à¯à®²à®¤à¯ à®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯, à®•à¯ˆà®•à®³à¯ˆà®šà¯ à®šà¯à®¤à¯à®¤à®¿ à®šà¯†à®¯à¯à®¤à¯, à®°à¯à®¤à¯à®°à®¾à®Ÿà¯à®šà®®à¯ à®…à®²à¯à®²à®¤à¯ à®šà®¨à¯à®¤à®© à®®à®¾à®²à¯ˆà®¯à¯ˆà®•à¯ à®•à¯Šà®£à¯à®Ÿà¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Daily at dawn or before commencing any sacred endeavor', 'à®¤à®¿à®©à®®à¯à®®à¯ à®µà®¿à®Ÿà®¿à®¯à®±à¯à®•à®¾à®²à¯ˆ à®…à®²à¯à®²à®¤à¯ à®ªà¯à®¤à®¿à®¯ à®•à®¾à®°à®¿à®¯à®™à¯à®•à®³à¯ˆà®¤à¯ à®¤à¯Šà®Ÿà®™à¯à®•à¯à®®à¯ à®®à¯à®©à¯',
 FALSE, ARRAY['spiritual_stagnation', 'house_construction_hurdles', 'business_setbacks']),

-- 2. Universal Maha Mrityunjaya Healing
('REM_UNIV_MRITYUNJAYA_01', 'universal', 'mantra',
 'Maha Mrityunjaya Healing Mantra', 'à®®à®•à®¾ à®®à®¿à®°à¯à®¤à¯à®¯à¯à®žà¯à®šà®¯ à®®à®•à®¾ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Sacred Rigvedic healing prayer (Rigveda 7.59.12) dedicated to Lord Shiva as Tryambaka for freedom from severe health afflictions, accidents, and dread.',
 'à®°à®¿à®•à¯à®µà¯‡à®¤à®¤à¯à®¤à®¿à®²à¯ à®…à®°à¯à®³à®ªà¯à®ªà®Ÿà¯à®Ÿ à®šà®¿à®µà®ªà¯†à®°à¯à®®à®¾à®©à®¿à®©à¯ à®’à®ªà¯à®ªà¯à®¯à®°à¯à®µà®±à¯à®± à®®à®•à®¾ à®®à®¨à¯à®¤à®¿à®°à®®à¯. à®•à¯Šà®Ÿà®¿à®¯ à®¨à¯‹à®¯à¯à®•à®³à¯, à®µà®¿à®ªà®¤à¯à®¤à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®°à®£ à®ªà®¯à®¤à¯à®¤à¯ˆ à®¨à¯€à®•à¯à®•à®¿ à®¨à¯€à®£à¯à®Ÿ à®†à®¯à¯à®³à¯ˆà®¯à¯à®®à¯ à®¨à®²à®©à¯ˆà®¯à¯à®®à¯ à®¨à®²à¯à®•à¯à®®à¯.',
 'Lord Shiva (Tryambaka)', 'à®šà®¿à®µà®ªà¯†à®°à¯à®®à®¾à®©à¯ (à®®à¯à®•à¯à®•à®£à¯à®£à®©à¯)',
 'à¥ à¤¤à¥à¤°à¥à¤¯à¤®à¥à¤¬à¤•à¤‚ à¤¯à¤œà¤¾à¤®à¤¹à¥‡ à¤¸à¥à¤—à¤¨à¥à¤§à¤¿à¤‚ à¤ªà¥à¤·à¥à¤Ÿà¤¿à¤µà¤°à¥à¤§à¤¨à¤®à¥ à¥¤ à¤‰à¤°à¥à¤µà¤¾à¤°à¥à¤•à¤®à¤¿à¤µ à¤¬à¤¨à¥à¤§à¤¨à¤¾à¤¨à¥à¤®à¥ƒà¤¤à¥à¤¯à¥‹à¤°à¥à¤®à¥à¤•à¥à¤·à¥€à¤¯ à¤®à¤¾à¤®à¥ƒà¤¤à¤¾à¤¤à¥ à¥¥',
 'oá¹ƒ tryambakaá¹ƒ yajÄmahe sugandhiá¹ƒ puá¹£á¹­ivardhanam | urvÄrukamiva bandhanÄnmá¹›tyormuká¹£Ä«ya mÄmá¹›tÄt à¥¥',
 'à®“à®®à¯ à®¤à¯à®°à®¯à®®à¯à®ªà®•à®®à¯ à®¯à®œà®¾à®®à®¹à¯‡ à®¸à¯à®•à®¨à¯à®¤à®¿à®®à¯ à®ªà¯à®·à¯à®Ÿà®¿à®µà®°à¯à®¤à¯à®¤à®©à®®à¯ à¥¤ à®‰à®°à¯à®µà®¾à®°à¯à®•à®®à®¿à®µ à®ªà®¨à¯à®¤à®©à®¾à®©à¯à®®à¯à®°à¯à®¤à¯à®¯à¯‹à®°à¯à®®à¯à®•à¯à®·à¯€à®¯ à®®à®¾à®®à¯à®°à¯à®¤à®¾à®¤à¯ à¥¥',
 'We worship the Three-Eyed Lord Shiva, who is fragrant and nourishes all beings. May He liberate us from death and disease towards immortality, as effortlessly as a ripe gourd is freed from its creeper.',
 'à®¨à®±à¯à®®à®£à®®à¯à®®à¯, à®…à®©à¯ˆà®µà®°à¯ˆà®¯à¯à®®à¯ à®ªà¯‹à®·à®¿à®•à¯à®•à¯à®®à¯ à®†à®±à¯à®±à®²à¯à®®à¯ à®•à¯Šà®£à¯à®Ÿ à®®à¯à®•à¯à®•à®£à¯à®£à®©à®¾à®© à®šà®¿à®µà®©à¯ˆ à®µà®£à®™à¯à®•à¯à®•à®¿à®±à¯‹à®®à¯. à®µà¯†à®³à¯à®³à®°à®¿à®ªà¯ à®ªà®´à®®à¯ à®•à®¾à®®à¯à®ªà®¿à®²à®¿à®°à¯à®¨à¯à®¤à¯ à®µà®¿à®Ÿà¯à®ªà®Ÿà¯à®µà®¤à¯ à®ªà¯‹à®², à®¨à®®à¯à®®à¯ˆ à®¨à¯‹à®¯à¯à®•à®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®°à®£à®ªà¯ à®ªà®¿à®Ÿà®¿à®¯à®¿à®²à®¿à®°à¯à®¨à¯à®¤à¯ à®µà®¿à®Ÿà¯à®µà®¿à®¤à¯à®¤à¯ à®…à®®à®¿à®°à¯à®¤ à®µà®¾à®´à¯à®µà¯ˆ à®…à®°à¯à®³à¯à®ªà¯à®°à®¿à®µà®¾à®°à®¾à®•.',
 'Recite 108 times daily facing North or East, preferably after morning bath. Can be chanted alongside medical treatment for recovery.',
 'à®•à®¾à®²à¯ˆ à®¨à¯€à®°à®¾à®Ÿà®¿à®¯ à®ªà®¿à®©à¯ à®µà®Ÿà®•à¯à®•à¯ à®…à®²à¯à®²à®¤à¯ à®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ à®¤à®¿à®©à®®à¯à®®à¯ 108 à®®à¯à®±à¯ˆ à®…à®®à¯ˆà®¤à®¿à®¯à®¾à®© à®®à®©à®¤à¯à®Ÿà®©à¯ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Daily at dawn during Brahma muhurta or dusk', 'à®¤à®¿à®©à®®à¯à®®à¯ à®µà®¿à®Ÿà®¿à®¯à®±à¯à®•à®¾à®²à¯ˆ à®ªà®¿à®°à®®à¯à®® à®®à¯à®•à¯‚à®°à¯à®¤à¯à®¤à®®à¯ à®…à®²à¯à®²à®¤à¯ à®…à®¨à¯à®¤à®¿ à®®à®¾à®²à¯ˆà®¯à®¿à®²à¯',
 FALSE, ARRAY['chronic_health_issues', 'mental_anxiety_depression', 'vehicle_accidents_breakdowns', 'fear_negative_energies']),

-- 3. Sun (Surya) Namaha Mantra
('REM_SUN_MANTRA_01', 'sun', 'mantra',
 'Surya Namaha Mantra', 'à®šà¯‚à®°à®¿à®¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Classical Parashari mantra invoking Lord Surya for strengthening vitality, confidence, paternal bonds, and administrative authority.',
 'à®†à®±à¯à®±à®²à¯, à®¤à®©à¯à®©à®®à¯à®ªà®¿à®•à¯à®•à¯ˆ, à®¤à®¨à¯à®¤à¯ˆ à®µà®´à®¿ à®¨à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®°à®šà¯/à®¨à®¿à®°à¯à®µà®¾à®•à®¤à¯ à®¤à¯à®±à¯ˆ à®®à¯‡à®©à¯à®®à¯ˆà®•à¯à®•à®¾à®• à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯ˆà®ªà¯ à®ªà¯‹à®±à¯à®±à®¿ à®‰à®šà¯à®šà®°à®¿à®•à¯à®•à¯à®®à¯ à®Žà®³à®¿à®¯ à®šà®¾à®¤à¯à®µà®¿à®• à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Surya (Sun)', 'à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯',
 'à¥ à¤¸à¥‚à¤°à¥à¤¯à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ sÅ«ryÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®šà¯‚à®°à¯à®¯à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Reverence to the radiant Sun God, the supreme cosmic witness and soul of the universe.',
 'à®…à®£à¯à®Ÿ à®šà®°à®¾à®šà®°à®™à¯à®•à®³à®¿à®©à¯ à®†à®©à¯à®®à®¾à®µà®¾à®•à®µà¯à®®à¯, à®’à®³à®¿ à®µà®Ÿà®¿à®µà®¾à®•à®µà¯à®®à¯ à®µà®¿à®³à®™à¯à®•à¯à®®à¯ à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®Žà®©à®¤à¯ à®¨à®®à®¸à¯à®•à®¾à®°à®™à¯à®•à®³à¯.',
 'Offer clean water mixed with red flowers and a pinch of jaggery from a copper vessel towards the rising sun while reciting 108 times.',
 'à®šà¯†à®ªà¯à®ªà¯à®ªà¯ à®ªà®¾à®¤à¯à®¤à®¿à®°à®¤à¯à®¤à®¿à®²à¯ à®šà¯à®¤à¯à®¤à®®à®¾à®© à®¤à®£à¯à®£à¯€à®°à¯à®Ÿà®©à¯ à®šà¯†à®®à¯à®ªà®°à¯à®¤à¯à®¤à®¿ à®…à®²à¯à®²à®¤à¯ à®šà¯†à®¨à¯à®¤à®¾à®®à®°à¯ˆ à®‡à®¤à®´à¯à®•à®³à¯ à®šà¯‡à®°à¯à®¤à¯à®¤à¯, à®•à®¾à®²à¯ˆ à®šà¯‚à®°à®¿à®¯à®©à¯ˆ à®¨à¯‹à®•à¯à®•à®¿ à®¨à®¿à®©à¯à®±à®ªà®Ÿà®¿ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Sunday mornings during sunrise', 'à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®šà¯‚à®°à®¿à®¯ à®‰à®¤à®¯ à®µà¯‡à®³à¯ˆà®¯à®¿à®²à¯',
 FALSE, ARRAY['career_delay', 'promotion_blocks', 'vitality_low_energy', 'eye_vision_ailments']),

-- 4. Sun (Surya) Charity (Daan) - FOR PACIFICATION ONLY
('REM_SUN_CHARITY_01', 'sun', 'charity',
 'Surya Daan (Wheat & Copper Charity)', 'à®šà¯‚à®°à®¿à®¯ à®¤à®¾à®©à®®à¯ (à®•à¯‹à®¤à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®šà¯†à®ªà¯à®ªà¯ à®¤à®¾à®©à®®à¯)',
 'Classical charity prescribed specifically when Sun acts as a functional malefic or afflicts health bhavas. NOT to be performed if Sun is a functional Yogakaraka.',
 'à®šà¯‚à®°à®¿à®¯à®©à¯ à®…à®šà¯à®ª à®†à®¤à®¿à®ªà®¤à¯à®¤à®¿à®¯à®®à¯ à®ªà¯†à®±à¯à®±à¯ à®‰à®Ÿà®²à¯ à®¨à®²à®ªà¯ à®ªà®¾à®¤à®¿à®ªà¯à®ªà¯à®•à®³à¯ˆà®¤à¯ à®¤à®°à¯à®®à¯ à®ªà¯‹à®¤à¯ à®®à®Ÿà¯à®Ÿà¯à®®à¯ à®šà¯†à®¯à¯à®¯ à®µà¯‡à®£à¯à®Ÿà®¿à®¯ à®ªà®°à®¿à®•à®¾à®° à®¤à®¾à®©à®®à¯. à®šà¯‚à®°à®¿à®¯à®©à¯ à®¯à¯‹à®•à®•à®¾à®°à®•à®©à®¾à®• à®‡à®°à¯à®•à¯à®•à¯à®®à¯ à®ªà¯‹à®¤à¯ à®‡à®¨à¯à®¤ à®¤à®¾à®©à®¤à¯à®¤à¯ˆà®¤à¯ à®¤à®µà®¿à®°à¯à®•à¯à®• à®µà¯‡à®£à¯à®Ÿà¯à®®à¯.',
 'Lord Surya', 'à®šà¯‚à®°à®¿à®¯ à®ªà®•à®µà®¾à®©à¯',
 NULL, NULL, NULL,
 'Donating wheat grains, jaggery, or copper vessels on Sunday helps calm afflicted solar heat and dispels paternal friction.',
 'à®•à¯‹à®¤à¯à®®à¯ˆ, à®µà¯†à®²à¯à®²à®®à¯ à®…à®²à¯à®²à®¤à¯ à®šà¯†à®ªà¯à®ªà¯à®ªà¯ à®ªà®¾à®¤à¯à®¤à®¿à®°à®™à¯à®•à®³à¯ˆ à®à®´à¯ˆ à®Žà®³à®¿à®¯à®µà®°à¯à®•à®³à¯à®•à¯à®•à¯ à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®¤à®¾à®©à®®à®¾à®• à®µà®´à®™à¯à®•à¯à®µà®¤à¯ à®šà¯‚à®°à®¿à®¯à®©à®¿à®©à¯ à®‰à®•à¯à®•à®¿à®°à®¤à¯à®¤à¯ˆà®¤à¯ à®¤à®£à®¿à®•à¯à®•à¯à®®à¯.',
 'Donate 1.25 kg of whole wheat grains and jaggery wrapped in red cloth to a needy student or temple kitchen on Sunday afternoon.',
 'à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®®à®¤à®¿à®¯à®®à¯ 1.25 à®•à®¿à®²à¯‹ à®®à¯à®´à¯ à®•à¯‹à®¤à¯à®®à¯ˆ à®®à®±à¯à®±à¯à®®à¯ à®µà¯†à®²à¯à®²à®¤à¯à®¤à¯ˆ à®šà®¿à®µà®ªà¯à®ªà¯à®¤à¯ à®¤à¯à®£à®¿à®¯à®¿à®²à¯ à®µà¯ˆà®¤à¯à®¤à¯ à®à®´à¯ˆ à®®à®¾à®£à®µà®°à¯à®•à®³à¯à®•à¯à®•à¯‹ à®…à®²à¯à®²à®¤à¯ à®•à¯‹à®¯à®¿à®²à¯ à®…à®©à¯à®©à®¤à®¾à®©à®¤à¯à®¤à®¿à®±à¯à®•à¯‹ à®µà®´à®™à¯à®•à®µà¯à®®à¯.',
 NULL, 'Sunday afternoon between 12:00 PM and 1:30 PM', 'à®žà®¾à®¯à®¿à®±à¯à®±à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®¨à®£à¯à®ªà®•à®²à¯ 12:00 à®®à¯à®¤à®²à¯ 1:30 à®®à®£à®¿à®•à¯à®•à¯à®³à¯',
 TRUE, ARRAY['workplace_conflicts', 'chronic_health_issues', 'ancestral_karmic_blocks']),

-- 5. Moon (Chandra) Namaha Mantra
('REM_MOON_MANTRA_01', 'moon', 'mantra',
 'Chandra Namaha Mantra', 'à®šà®¨à¯à®¤à®¿à®° à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Traditional devotional prayer calming emotional turbulence, cooling anxiety, and healing mother-child relationships.',
 'à®®à®© à®…à®®à¯ˆà®¤à®¿, à®¨à®¿à®®à¯à®®à®¤à®¿à®¯à®¾à®© à®‰à®±à®•à¯à®•à®®à¯, à®¤à®¾à®¯à¯-à®šà¯‡à®¯à¯ à®¨à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®‰à®£à®°à¯à®šà¯à®šà®¿ à®šà®®à®¨à®¿à®²à¯ˆà®¯à¯ˆà®ªà¯ à®ªà¯†à®± à®šà®¨à¯à®¤à®¿à®° à®ªà®•à®µà®¾à®©à¯ˆà®ªà¯ à®ªà¯‹à®±à¯à®±à¯à®®à¯ à®ªà¯à®©à®¿à®¤ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Chandra (Moon)', 'à®šà®¨à¯à®¤à®¿à®° à®ªà®•à®µà®¾à®©à¯',
 'à¥ à¤¸à¥‹à¤®à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ somÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®¸à¯‹à®®à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Salutations to Lord Soma (the Moon), the reservoir of nectar and guardian of the mind and emotions.',
 'à®…à®®à®¿à®°à¯à®¤à®¤à¯à®¤à®¿à®©à¯ à®‡à®°à¯à®ªà¯à®ªà®¿à®Ÿà®®à®¾à®•à®µà¯à®®à¯, à®®à®©à¯‹à®•à®¾à®°à®•à®©à®¾à®•à®µà¯à®®à¯ à®µà®¿à®³à®™à¯à®•à¯à®®à¯ à®šà®¨à¯à®¤à®¿à®° à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®Žà®©à®¤à¯ à®µà®£à®•à¯à®•à®™à¯à®•à®³à¯.',
 'Chant 108 times on Monday evening after moonrise facing North or North-West with serene focus.',
 'à®¤à®¿à®™à¯à®•à®Ÿà¯à®•à®¿à®´à®®à¯ˆ à®®à®¾à®²à¯ˆ à®šà®¨à¯à®¤à®¿à®°à®©à¯ à®‰à®¤à®¿à®¤à¯à®¤ à®ªà®¿à®©à¯ à®µà®Ÿà®•à¯à®•à¯ à®…à®²à¯à®²à®¤à¯ à®µà®Ÿà®®à¯‡à®±à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Monday evenings after moonrise', 'à®¤à®¿à®™à¯à®•à®Ÿà¯à®•à®¿à®´à®®à¯ˆ à®®à®¾à®²à¯ˆ à®šà®¨à¯à®¤à®¿à®° à®¤à®°à®¿à®šà®©à®¤à¯à®¤à®¿à®±à¯à®•à¯à®ªà¯ à®ªà®¿à®©à¯',
 FALSE, ARRAY['mental_anxiety_depression', 'marital_discord', 'recurrent_nightmares', 'relocation_adjustment_stress']),

-- 6. Mars (Mangal) Namaha Mantra
('REM_MARS_MANTRA_01', 'mars', 'mantra',
 'Mangal Namaha Mantra', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Parashari prayer invoking Mars for courage, blood vitality, resolving land property hurdles, and mitigating Kuja dosha friction.',
 'à®¤à¯ˆà®°à®¿à®¯à®®à¯, à®¨à®¿à®²à®®à¯ à®šà®¾à®°à¯à®¨à¯à®¤ à®šà¯Šà®¤à¯à®¤à¯ à®¨à®©à¯à®®à¯ˆà®•à®³à¯, à®°à®¤à¯à®¤ à®¨à®²à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®¤à¯‹à®· à®…à®®à¯ˆà®¤à®¿à®•à¯à®•à®¾à®• à®…à®™à¯à®•à®¾à®°à®•à®©à¯ˆà®ªà¯ à®ªà¯‹à®±à¯à®±à¯à®®à¯ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Mangal (Mars / Murugan)', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®ªà®•à®µà®¾à®©à¯ / à®®à¯à®°à¯à®•à®ªà¯ à®ªà¯†à®°à¯à®®à®¾à®©à¯',
 'à¥ à¤­à¥Œà¤®à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ bhaumÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®ªà¯Œà®®à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Salutations to Mars, the son of the Earth, the granter of vigor, resilience, and victorious valor.',
 'à®ªà¯‚à®®à®¿à®¤à¯‡à®µà®¿à®¯à®¿à®©à¯ à®®à¯ˆà®¨à¯à®¤à®©à¯à®®à¯, à®…à®³à®ªà¯à®ªà®°à®¿à®¯ à®µà¯€à®°à®®à¯à®®à¯ à®ªà®²à®®à¯à®®à¯ à®…à®°à¯à®³à¯à®ªà®µà®°à¯à®®à®¾à®© à®…à®™à¯à®•à®¾à®°à®• à®ªà®•à®µà®¾à®©à¯ˆà®ªà¯ à®ªà®£à®¿à®•à®¿à®±à¯‡à®©à¯.',
 'Sit on a red mat facing South or East on Tuesday morning. Light a ghee lamp and chant 108 times.',
 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®¤à¯†à®±à¯à®•à¯ à®…à®²à¯à®²à®¤à¯ à®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®šà®¿à®µà®ªà¯à®ªà¯ à®µà®¿à®°à®¿à®ªà¯à®ªà®¿à®²à¯ à®…à®®à®°à¯à®¨à¯à®¤à¯ à®¨à¯†à®¯à¯ à®¤à¯€à®ªà®®à¯‡à®±à¯à®±à®¿ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Tuesday mornings', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®µà¯‡à®³à¯ˆà®¯à®¿à®²à¯',
 FALSE, ARRAY['land_property_disputes', 'house_construction_hurdles', 'marriage_delay', 'vitality_low_energy']),

-- 7. Mercury (Budha) Namaha Mantra
('REM_MERCURY_MANTRA_01', 'mercury', 'mantra',
 'Budha Namaha Mantra', 'à®ªà¯à®¤à®©à¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Classical prayer for intellectual acuity, commercial success, speech eloquence, and nervous balance.',
 'à®•à®²à¯à®µà®¿à®¤à¯ à®¤à¯‡à®°à¯à®šà¯à®šà®¿, à®¨à®¿à®©à¯ˆà®µà®¾à®±à¯à®±à®²à¯, à®µà®¾à®•à¯à®•à¯ à®µà®©à¯à®®à¯ˆ, à®µà®¿à®¯à®¾à®ªà®¾à®° à®µà®³à®°à¯à®šà¯à®šà®¿ à®®à®±à¯à®±à¯à®®à¯ à®ªà¯à®¤à¯à®¤à®¿ à®•à¯‚à®°à¯à®®à¯ˆà®•à¯à®•à¯à®°à®¿à®¯ à®ªà¯à®¤à®©à¯ à®ªà®•à®µà®¾à®©à¯ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Budha (Mercury / Vishnu)', 'à®ªà¯à®¤à®©à¯ à®ªà®•à®µà®¾à®©à¯ / à®µà®¿à®·à¯à®£à¯ à®ªà¯†à®°à¯à®®à®¾à®©à¯',
 'à¥ à¤¬à¥à¤§à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ budhÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®ªà¯à®¤à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Reverence to Lord Budha, the presiding lord of intelligence, discrimination, trade, and learning.',
 'à®žà®¾à®©à®®à¯, à®µà®¿à®µà¯‡à®•à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®µà®°à¯à®¤à¯à®¤à®•à®¤à¯à®¤à®¿à®©à¯ à®…à®¤à®¿à®ªà®¤à®¿à®¯à®¾à®•à®¤à¯ à®¤à®¿à®•à®´à¯à®®à¯ à®ªà¯à®¤à®©à¯ à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®Žà®©à®¤à¯ à®¨à®®à®¸à¯à®•à®¾à®°à®™à¯à®•à®³à¯.',
 'Chant 108 times on Wednesday morning facing North. Offering tulasi leaves to Lord Vishnu enhances auspicious results.',
 'à®ªà¯à®¤à®©à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®µà®Ÿà®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯. à®ªà¯†à®°à¯à®®à®¾à®³à¯à®•à¯à®•à¯à®¤à¯ à®¤à¯à®³à®šà®¿ à®šà®®à®°à¯à®ªà¯à®ªà®¿à®¤à¯à®¤à¯ à®µà®´à®¿à®ªà®Ÿà¯à®µà®¤à¯ à®•à¯‚à®Ÿà¯à®¤à®²à¯ à®¨à®±à¯à®ªà®²à®©à¯ à®¤à®°à¯à®®à¯.',
 108, 'Wednesday mornings', 'à®ªà¯à®¤à®©à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®µà¯‡à®³à¯ˆà®¯à®¿à®²à¯',
 FALSE, ARRAY['academic_focus_memory', 'business_setbacks', 'speech_communication_blocks', 'exam_competitive_hurdles']),

-- 8. Jupiter (Guru) Namaha Mantra
('REM_JUPITER_MANTRA_01', 'jupiter', 'mantra',
 'Guru Namaha Mantra', 'à®•à¯à®°à¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Sacred invocation of Brihaspati for wisdom, progeny blessings, marital happiness, and divine grace.',
 'à®žà®¾à®©à®®à¯, à®•à¯à®°à¯à®µà®°à¯à®³à¯, à®šà¯à®ª à®•à®¾à®°à®¿à®¯ à®µà¯†à®±à¯à®±à®¿, à®ªà¯à®¤à¯à®¤à®¿à®° à®ªà®¾à®•à¯à®•à®¿à®¯à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®¤à®¿à®°à¯à®®à®£ à®¯à¯‹à®•à®¤à¯à®¤à®¿à®±à¯à®•à¯à®°à®¿à®¯ à®•à¯à®°à¯ à®ªà®•à®µà®¾à®©à¯ à®ªà¯‹à®±à¯à®±à®¿.',
 'Lord Brihaspati (Jupiter / Dakshinamurthy)', 'à®•à¯à®°à¯ à®ªà®•à®µà®¾à®©à¯ / à®¤à®Ÿà¯à®šà®¿à®£à®¾à®®à¯‚à®°à¯à®¤à¯à®¤à®¿',
 'à¥ à¤¬à¥ƒà¤¹à¤¸à¥à¤ªà¤¤à¤¯à¥‡ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ bá¹›haspataye namaá¸¥ à¥¥', 'à®“à®®à¯ à®ªà®¿à®°à¯à®¹à®¸à¯à®ªà®¤à®¯à¯‡ à®¨à®®à®¹ à¥¥',
 'Salutations to Brihaspati, the preceptor of the Gods, master of Vedic scriptures, and embodiment of grace.',
 'à®¤à¯‡à®µà®°à¯à®•à®³à®¿à®©à¯ à®•à¯à®°à¯à®µà¯à®®à¯, à®šà®•à®² à®šà®¾à®¸à¯à®¤à®¿à®° à®žà®¾à®©à®™à¯à®•à®³à®¿à®©à¯ à®‡à®°à¯à®ªà¯à®ªà®¿à®Ÿà®®à¯à®®à®¾à®© à®ªà®¿à®°à®•à®¸à¯à®ªà®¤à®¿ à®ªà®•à®µà®¾à®©à¯ˆà®ªà¯ à®ªà®£à®¿à®•à®¿à®±à¯‡à®©à¯.',
 'Chant 108 times on Thursday morning wearing yellow or clean white attire facing North-East.',
 'à®µà®¿à®¯à®¾à®´à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®µà®Ÿà®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ à®®à®žà¯à®šà®³à¯ à®…à®²à¯à®²à®¤à¯ à®µà¯†à®£à¯à®£à®¿à®± à®†à®Ÿà¯ˆ à®…à®£à®¿à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Thursday mornings during sunrise', 'à®µà®¿à®¯à®¾à®´à®•à¯à®•à®¿à®´à®®à¯ˆ à®…à®¤à®¿à®•à®¾à®²à¯ˆ',
 FALSE, ARRAY['progeny_childbirth_delay', 'higher_education_obstacles', 'financial_instability', 'marriage_delay']),

-- 9. Venus (Shukra) Namaha Mantra
('REM_VENUS_MANTRA_01', 'venus', 'mantra',
 'Shukra Namaha Mantra', 'à®šà¯à®•à¯à®•à®¿à®° à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Classical prayer harmonizing relationships, attracting material comforts, artistic fulfillment, and marital joy.',
 'à®•à®³à®¤à¯à®¤à®¿à®° à®¤à¯‹à®· à®¨à®¿à®µà®°à¯à®¤à¯à®¤à®¿, à®¤à®¾à®®à¯à®ªà®¤à¯à®¤à®¿à®¯ à®…à®©à¯à®¯à¯‹à®©à¯à®¯à®®à¯, à®•à®²à¯ˆà®¤à¯ à®¤à®¿à®±à®©à¯ à®®à®±à¯à®±à¯à®®à¯ à®šà®•à®² à®à®¸à¯à®µà®°à¯à®¯à®™à¯à®•à®³à¯à®•à¯à®•à¯à®®à¯ à®‰à®°à®¿à®¯ à®šà¯à®•à¯à®•à®¿à®° à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Shukra (Venus / Mahalakshmi)', 'à®šà¯à®•à¯à®•à®¿à®° à®ªà®•à®µà®¾à®©à¯ / à®®à®•à®¾à®²à®Ÿà¯à®šà¯à®®à®¿',
 'à¥ à¤¶à¥à¤•à¥à¤°à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ Å›ukrÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®šà¯à®•à¯à®°à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Reverence to Shukracharya, the brilliant master of aesthetic beauty, harmony, and material opulence.',
 'à®šà®•à®² à®•à®²à¯ˆà®•à®³à®¿à®©à¯ à®µà®¿à®¤à¯à®¤à®•à®°à¯à®®à¯, à®‡à®©à¯à®ªà®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®´à®•à®¿à®©à¯ à®¨à®¾à®¯à®•à®°à¯à®®à®¾à®© à®šà¯à®•à¯à®•à®¿à®° à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®Žà®©à®¤à¯ à®¨à®®à®¸à¯à®•à®¾à®°à®™à¯à®•à®³à¯.',
 'Chant 108 times on Friday evening or morning facing East or South-East after a clean bath.',
 'à®µà¯†à®³à¯à®³à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®…à®²à¯à®²à®¤à¯ à®…à®¨à¯à®¤à®¿ à®®à®¾à®²à¯ˆà®¯à®¿à®²à¯ à®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ à®®à®© à®…à®®à¯ˆà®¤à®¿à®¯à¯à®Ÿà®©à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Friday mornings or twilight', 'à®µà¯†à®³à¯à®³à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®…à®²à¯à®²à®¤à¯ à®…à®¨à¯à®¤à®¿ à®®à®¾à®²à¯ˆ',
 FALSE, ARRAY['marital_discord', 'relationship_breakdown', 'wealth_accumulation_block', 'marriage_delay']),

-- 10. Saturn (Shani) Namaha Mantra
('REM_SATURN_MANTRA_01', 'saturn', 'mantra',
 'Shani Namaha Mantra', 'à®šà®©à®¿ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Vedic prayer invoking Saturn for humility, patient perseverance, relief from Sade Sati distress, and longevity.',
 'à®à®´à®°à¯ˆà®šà¯ à®šà®©à®¿, à®…à®·à¯à®Ÿà®®à®šà¯ à®šà®©à®¿ à®†à®•à®¿à®¯à®µà®±à¯à®±à®¿à®©à¯ à®ªà®¾à®¤à®¿à®ªà¯à®ªà¯à®•à®³à¯ˆà®¤à¯ à®¤à®£à®¿à®¤à¯à®¤à¯, à®ªà¯Šà®±à¯à®®à¯ˆ, à®¨à¯€à®¤à®¿ à®®à®±à¯à®±à¯à®®à¯ à®¨à¯€à®£à¯à®Ÿ à®†à®¯à¯à®³à¯ˆ à®…à®°à¯à®³à¯à®®à¯ à®šà®©à®¿ à®ªà®•à®µà®¾à®©à¯ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Shani (Saturn)', 'à®šà®©à¯€à®¸à¯à®µà®° à®ªà®•à®µà®¾à®©à¯',
 'à¥ à¤¶à¤¨à¥ˆà¤¶à¥à¤šà¤°à¤¾à¤¯ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ Å›anaiÅ›carÄya namaá¸¥ à¥¥', 'à®“à®®à¯ à®šà®©à¯ˆà®šà¯à®šà®°à®¾à®¯ à®¨à®®à®¹ à¥¥',
 'Salutations to the slow-moving Lord Shani, the dispenser of karmic justice and guardian of discipline and truth.',
 'à®¨à¯€à®¤à®¿à®¯à®¿à®©à¯ à®ªà®¾à®±à¯à®ªà®Ÿà¯à®Ÿà¯ à®•à®°à¯à®® à®µà®¿à®©à¯ˆà®•à®³à¯à®•à¯à®•à¯ à®à®±à¯à®ª à®ªà®²à®©à¯à®•à®³à¯ˆ à®…à®°à¯à®³à¯à®®à¯ à®šà®©à¯€à®¸à¯à®µà®° à®ªà®•à®µà®¾à®©à¯ˆà®ªà¯ à®ªà®£à®¿à®¨à¯à®¤à¯ à®µà®£à®™à¯à®•à¯à®•à®¿à®±à¯‡à®©à¯.',
 'Recite 108 times on Saturday evening facing West. Lighting a sesame oil lamp under a peepal tree or at home is recommended.',
 'à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®®à®¾à®²à¯ˆ à®®à¯‡à®±à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯. à®¨à®²à¯à®²à¯†à®£à¯à®£à¯†à®¯à¯ à®¤à¯€à®ªà®®à¯‡à®±à¯à®±à®¿ à®µà®´à®¿à®ªà®Ÿà¯à®µà®¤à¯ à®¨à®²à®®à¯ à®ªà®¯à®•à¯à®•à¯à®®à¯.',
 108, 'Saturday evenings after sunset', 'à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®®à®¾à®²à¯ˆ à®šà¯‚à®°à®¿à®¯ à®…à®¸à¯à®¤à®®à®©à®¤à¯à®¤à®¿à®±à¯à®•à¯à®ªà¯ à®ªà®¿à®©à¯',
 FALSE, ARRAY['career_delay', 'chronic_debt_burden', 'litigation_court_cases', 'bone_joint_mobility']),

-- 11. Saturn (Shani) Charity (Daan) - FOR PACIFICATION ONLY
('REM_SATURN_CHARITY_01', 'saturn', 'charity',
 'Shani Daan (Black Sesame & Blanket Charity)', 'à®šà®©à®¿ à®¤à®¾à®©à®®à¯ (à®•à®°à¯à®ªà¯à®ªà¯ à®Žà®³à¯ à®®à®±à¯à®±à¯à®®à¯ à®…à®©à¯à®©à®¤à®¾à®©à®®à¯)',
 'Strictly for pacifying malefic Saturn when afflicting dusthanas. Never prescribe for Taurus/Libra where Saturn is Yogakaraka.',
 'à®šà®©à®¿ à®ªà®•à®µà®¾à®©à¯ à®…à®šà¯à®ª à®†à®¤à®¿à®ªà®¤à¯à®¤à®¿à®¯à®®à¯ à®ªà¯†à®±à¯à®±à¯ à®¤à¯à®©à¯à®ªà®®à¯ à®¤à®°à¯à®®à¯ à®ªà¯‹à®¤à¯ à®®à®Ÿà¯à®Ÿà¯à®®à¯ à®šà¯†à®¯à¯à®¯ à®µà¯‡à®£à¯à®Ÿà®¿à®¯ à®ªà®°à®¿à®•à®¾à®° à®¤à®¾à®©à®®à¯. à®°à®¿à®·à®ªà®®à¯/à®¤à¯à®²à®¾à®®à¯ à®¯à¯‹à®•à®•à®¾à®°à®•à®°à¯à®•à®³à¯à®•à¯à®•à¯ à®‡à®¤à¯à®¤à®¾à®©à®®à¯ à®ªà¯Šà®°à¯à®¨à¯à®¤à®¾à®¤à¯.',
 'Lord Shani', 'à®šà®©à¯€à®¸à¯à®µà®° à®ªà®•à®µà®¾à®©à¯',
 NULL, NULL, NULL,
 'Donating black sesame seeds, mustard oil, or warm dark blankets to elderly, disabled, or needy workers on Saturday.',
 'à®•à®°à¯à®ªà¯à®ªà¯ à®Žà®³à¯, à®¨à®²à¯à®²à¯†à®£à¯à®£à¯†à®¯à¯, à®•à®°à¯à®ªà¯à®ªà¯ à®µà®¸à¯à®¤à®¿à®°à®®à¯ à®…à®²à¯à®²à®¤à¯ à®ªà¯‹à®°à¯à®µà¯ˆà®•à®³à¯ˆ à®®à¯à®¤à®¿à®¯à¯‹à®°à¯ à®®à®±à¯à®±à¯à®®à¯ à®®à®¾à®±à¯à®±à¯à®¤à¯à®¤à®¿à®±à®©à®¾à®³à®¿à®•à®³à¯à®•à¯à®•à¯ à®µà®´à®™à¯à®•à¯à®¤à®²à¯.',
 'Distribute sesame-mixed cooked rice or warm blankets to poor laborers or elderly destitute persons on Saturday afternoon.',
 'à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®®à®¤à®¿à®¯à®®à¯ à®à®´à¯ˆ à®Žà®³à®¿à®¯ à®¤à¯Šà®´à®¿à®²à®¾à®³à®°à¯à®•à®³à¯ à®…à®²à¯à®²à®¤à¯ à®®à¯à®¤à®¿à®¯à®µà®°à¯à®•à®³à¯à®•à¯à®•à¯ à®Žà®³à¯ à®•à®²à®¨à¯à®¤ à®‰à®£à®µà¯ à®…à®²à¯à®²à®¤à¯ à®ªà¯‹à®°à¯à®µà¯ˆ à®¤à®¾à®©à®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 NULL, 'Saturday afternoons', 'à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®¨à®£à¯à®ªà®•à®²à¯ à®µà¯‡à®³à¯ˆà®¯à®¿à®²à¯',
 TRUE, ARRAY['chronic_debt_burden', 'litigation_court_cases', 'past_life_karmic_burdens']),

-- 12. Rahu Namaha Mantra
('REM_RAHU_MANTRA_01', 'rahu', 'mantra',
 'Rahu Namaha Mantra', 'à®°à®¾à®•à¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Protective mantra pacifying psychological illusion, addictions, unexpected shocks, and Rahu dasha turbulence.',
 'à®®à®¾à®¯à¯ˆ, à®ªà®¿à®°à®®à¯ˆà®•à®³à¯, à®¤à®¿à®Ÿà¯€à®°à¯ à®¤à®Ÿà¯ˆà®•à®³à¯, à®µà®¿à®· à®ªà®¯à®®à¯ à®®à®±à¯à®±à¯à®®à¯ à®°à®¾à®•à¯ à®¤à®šà¯ˆ-à®ªà¯à®¤à¯à®¤à®¿à®•à®³à®¿à®©à¯ à®•à¯†à®Ÿà¯à®ªà®²à®©à¯à®•à®³à¯ˆà®¤à¯ à®¤à®£à®¿à®•à¯à®•à¯à®®à¯ à®šà®¾à®¨à¯à®¤à®¿ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Rahu (Goddess Durga)', 'à®°à®¾à®•à¯ à®ªà®•à®µà®¾à®©à¯ / à®¤à¯à®°à¯à®•à¯à®•à¯ˆ à®…à®®à¯à®®à®©à¯',
 'à¥ à¤°à¤¾à¤¹à¤µà¥‡ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ rÄhave namaá¸¥ à¥¥', 'à®“à®®à¯ à®°à®¾à®•à®µà¯‡ à®¨à®®à®¹ à¥¥',
 'Salutations to Lord Rahu, who tests the soul through worldly illusion and grants deep spiritual insight upon pacification.',
 'à®‰à®²à®•à®¿à®¯à®²à¯ à®®à®¾à®¯à¯ˆà®•à®³à¯ˆ à®µà®¿à®²à®•à¯à®•à®¿, à®¤à¯à®°à¯à®•à¯à®•à¯ˆà®¯à®¿à®©à¯ à®…à®°à¯à®³à®¾à®²à¯ à®¤à¯†à®³à®¿à®¨à¯à®¤ à®žà®¾à®©à®¤à¯à®¤à¯ˆ à®¨à®²à¯à®•à¯à®®à¯ à®°à®¾à®•à¯ à®ªà®•à®µà®¾à®©à¯ˆ à®µà®£à®™à¯à®•à¯à®•à®¿à®±à¯‡à®©à¯.',
 'Chant 108 times on Saturday or during Rahu Kalam on Tuesday/Friday facing South-West.',
 'à®šà¯†à®µà¯à®µà®¾à®¯à¯ à®…à®²à¯à®²à®¤à¯ à®µà¯†à®³à¯à®³à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®°à®¾à®•à¯ à®•à®¾à®²à®¤à¯à®¤à®¿à®²à¯ à®…à®²à¯à®²à®¤à¯ à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®®à®¾à®²à¯ˆ à®¤à¯†à®©à¯à®®à¯‡à®±à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Rahu Kalam or Saturday twilight', 'à®°à®¾à®•à¯ à®•à®¾à®²à®®à¯ à®…à®²à¯à®²à®¤à¯ à®šà®©à®¿à®•à¯à®•à®¿à®´à®®à¯ˆ à®…à®¨à¯à®¤à®¿ à®µà¯‡à®³à¯ˆ',
 FALSE, ARRAY['fear_negative_energies', 'job_loss_instability', 'speculation_gambling_losses', 'visa_immigration_delays']),

-- 13. Ketu Namaha Mantra
('REM_KETU_MANTRA_01', 'ketu', 'mantra',
 'Ketu Namaha Mantra', 'à®•à¯‡à®¤à¯ à®¨à®®à®¹ à®®à®¨à¯à®¤à®¿à®°à®®à¯',
 'Spiritual prayer invoking Ketu for detachment from past burdens, inner liberation (Moksha), and occult wisdom.',
 'à®®à¯‹à®Ÿà¯à®š à®•à®¾à®°à®•à®©à®¾à®© à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à®¿à®©à¯ à®…à®°à¯à®³à¯ˆà®ªà¯ à®ªà¯†à®±à¯à®±à¯, à®ªà¯‚à®°à¯à®µ à®œà¯†à®©à¯à®® à®µà®¿à®©à¯ˆà®•à®³à¯ˆà®¤à¯ à®¤à¯€à®°à¯à®¤à¯à®¤à¯, à®†à®©à¯à®®à¯€à®• à®žà®¾à®©à®®à¯ à®ªà¯†à®± à®‰à®¤à®µà¯à®®à¯ à®®à®¨à¯à®¤à®¿à®°à®®à¯.',
 'Lord Ketu (Lord Ganesha)', 'à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à¯ / à®µà®¿à®¨à®¾à®¯à®•à®ªà¯ à®ªà¯†à®°à¯à®®à®¾à®©à¯',
 'à¥ à¤•à¥‡à¤¤à¤µà¥‡ à¤¨à¤®à¤ƒ à¥¥', 'oá¹ƒ ketave namaá¸¥ à¥¥', 'à®“à®®à¯ à®•à¯‡à®¤à®µà¯‡ à®¨à®®à®¹ à¥¥',
 'Reverence to Lord Ketu, the flag of spiritual detachment, dispeller of illusions, and bestower of ultimate liberation.',
 'à®ªà®±à¯à®±à®±à¯à®± à®¨à®¿à®²à¯ˆà®¯à¯ˆ à®…à®°à¯à®³à®¿, à®‰à®²à®•à®ªà¯ à®ªà®¿à®£à®¿à®•à®³à®¿à®²à®¿à®°à¯à®¨à¯à®¤à¯ à®†à®©à¯à®®à®¾à®µà¯ˆ à®µà®¿à®Ÿà¯à®µà®¿à®¤à¯à®¤à¯ à®®à¯à®•à¯à®¤à®¿ à®…à®³à®¿à®•à¯à®•à¯à®®à¯ à®•à¯‡à®¤à¯ à®ªà®•à®µà®¾à®©à¯à®•à¯à®•à¯ à®¨à®®à®¸à¯à®•à®¾à®°à®™à¯à®•à®³à¯.',
 'Chant 108 times on Tuesday morning facing North-East after offering Durva grass to Lord Ganesha.',
 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®•à®¾à®²à¯ˆ à®µà®¿à®¨à®¾à®¯à®•à®°à¯à®•à¯à®•à¯ à®…à®°à¯à®•à®®à¯à®ªà¯à®²à¯ à®šà®®à®°à¯à®ªà¯à®ªà®¿à®¤à¯à®¤ à®ªà®¿à®©à¯ à®µà®Ÿà®•à®¿à®´à®•à¯à®•à¯ à®¨à¯‹à®•à¯à®•à®¿ à®…à®®à®°à¯à®¨à¯à®¤à¯ 108 à®®à¯à®±à¯ˆ à®œà®ªà®®à¯ à®šà¯†à®¯à¯à®¯à®µà¯à®®à¯.',
 108, 'Tuesday mornings at dawn', 'à®šà¯†à®µà¯à®µà®¾à®¯à¯à®•à¯à®•à®¿à®´à®®à¯ˆ à®µà®¿à®Ÿà®¿à®¯à®±à¯à®•à®¾à®²à¯ˆ',
 FALSE, ARRAY['spiritual_stagnation', 'past_life_karmic_burdens', 'recurrent_nightmares', 'ancestral_karmic_blocks'])

ON CONFLICT (code) DO UPDATE SET
    graha = EXCLUDED.graha,
    remedy_type = EXCLUDED.remedy_type,
    name_en = EXCLUDED.name_en,
    name_ta = EXCLUDED.name_ta,
    description_en = EXCLUDED.description_en,
    description_ta = EXCLUDED.description_ta,
    deity_en = EXCLUDED.deity_en,
    deity_ta = EXCLUDED.deity_ta,
    sanskrit_text = EXCLUDED.sanskrit_text,
    transliteration_iast = EXCLUDED.transliteration_iast,
    transliteration_ta = EXCLUDED.transliteration_ta,
    meaning_en = EXCLUDED.meaning_en,
    meaning_ta = EXCLUDED.meaning_ta,
    procedure_en = EXCLUDED.procedure_en,
    procedure_ta = EXCLUDED.procedure_ta,
    japa_count = EXCLUDED.japa_count,
    timing_recommendation_en = EXCLUDED.timing_recommendation_en,
    timing_recommendation_ta = EXCLUDED.timing_recommendation_ta,
    is_pacification_only = EXCLUDED.is_pacification_only,
    problem_slugs = EXCLUDED.problem_slugs,
    updated_at = NOW();


-- PART 3: RELAX CUSTOMER PHONE NULLABILITY
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


-- PART 4: REMEDY REPORTS
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



COMMIT;
-- ==============================================================================
-- End of Consolidated Staging Migration Package
-- ==============================================================================
