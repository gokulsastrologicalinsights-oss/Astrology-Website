-- Gokul's Astrological Insights - Astrological Conditions & Predictions Engine
-- Migration: 20261021000001_create_astrological_rules_engine.sql
-- Description: Creates prediction categories, rules library, and rule audit versions tables with RLS and seed data.

-- 1. Table: public.prediction_categories
CREATE TABLE IF NOT EXISTS public.prediction_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE CHECK (char_length(trim(slug)) >= 2),
    group_code TEXT NOT NULL,
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT NOT NULL CHECK (char_length(trim(name_ta)) > 0),
    description_en TEXT,
    description_ta TEXT,
    display_order INT NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prediction_categories_slug ON public.prediction_categories (slug);
CREATE INDEX IF NOT EXISTS idx_prediction_categories_group ON public.prediction_categories (group_code);
CREATE INDEX IF NOT EXISTS idx_prediction_categories_order ON public.prediction_categories (display_order);

-- 2. Table: public.astrological_rules
CREATE TABLE IF NOT EXISTS public.astrological_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id TEXT NOT NULL UNIQUE CHECK (char_length(trim(rule_id)) >= 3),
    version INT NOT NULL DEFAULT 1 CHECK (version >= 1),
    name_en TEXT NOT NULL CHECK (char_length(trim(name_en)) > 0),
    name_ta TEXT,
    category_slug TEXT NOT NULL REFERENCES public.prediction_categories(slug) ON DELETE CASCADE,
    subcategory TEXT,
    astrology_system TEXT NOT NULL DEFAULT 'vedic' CHECK (astrology_system IN ('vedic', 'kp', 'combined')),
    chart_scope TEXT NOT NULL DEFAULT 'd1' CHECK (chart_scope IN ('d1', 'd9', 'both')),
    calculation_mode TEXT NOT NULL DEFAULT 'thirukanitha',
    condition_tree JSONB NOT NULL,
    interpretation_en TEXT NOT NULL,
    interpretation_ta TEXT,
    astrological_principle_en TEXT NOT NULL,
    astrological_principle_ta TEXT,
    evidence_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_reference TEXT,
    limitations_en TEXT,
    limitations_ta TEXT,
    severity TEXT NOT NULL DEFAULT 'neutral' CHECK (severity IN ('info', 'favorable', 'unfavorable', 'neutral', 'mixed')),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_astrological_rules_rule_id ON public.astrological_rules (rule_id);
CREATE INDEX IF NOT EXISTS idx_astrological_rules_cat ON public.astrological_rules (category_slug, subcategory);
CREATE INDEX IF NOT EXISTS idx_astrological_rules_status ON public.astrological_rules (is_enabled, is_draft);

-- 3. Table: public.astrological_rule_versions (Audit History)
CREATE TABLE IF NOT EXISTS public.astrological_rule_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id TEXT NOT NULL,
    version INT NOT NULL,
    rule_snapshot JSONB NOT NULL,
    changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    change_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rule_versions_rule_ver ON public.astrological_rule_versions (rule_id, version DESC);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.prediction_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrological_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrological_rule_versions ENABLE ROW LEVEL SECURITY;

-- 4.1 Policies for prediction_categories
DROP POLICY IF EXISTS "categories_read_policy" ON public.prediction_categories;
CREATE POLICY "categories_read_policy" ON public.prediction_categories
    FOR SELECT USING (is_published = TRUE OR public.is_admin());

DROP POLICY IF EXISTS "categories_admin_modify_policy" ON public.prediction_categories;
CREATE POLICY "categories_admin_modify_policy" ON public.prediction_categories
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 4.2 Policies for astrological_rules
DROP POLICY IF EXISTS "rules_read_policy" ON public.astrological_rules;
CREATE POLICY "rules_read_policy" ON public.astrological_rules
    FOR SELECT USING ((is_enabled = TRUE AND is_draft = FALSE) OR public.is_admin());

DROP POLICY IF EXISTS "rules_admin_modify_policy" ON public.astrological_rules;
CREATE POLICY "rules_admin_modify_policy" ON public.astrological_rules
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 4.3 Policies for astrological_rule_versions
DROP POLICY IF EXISTS "rule_versions_admin_policy" ON public.astrological_rule_versions;
CREATE POLICY "rule_versions_admin_policy" ON public.astrological_rule_versions
    FOR ALL USING (public.is_admin()) WITH CHECK (public.is_admin());

-- 5. Seed Core Prediction Categories
INSERT INTO public.prediction_categories (slug, group_code, name_en, name_ta, description_en, description_ta, display_order)
VALUES
('marriage_prospects', 'marriage_relationships', 'Marriage Prospects', 'திருமண வாய்ப்புகள்', 'General promise and nature of marriage.', 'ஜாதகத்தில் திருமண பாக்கியம் மற்றும் அமைவு பற்றிய பொதுவான விதிகள்.', 1),
('marriage_timing', 'marriage_relationships', 'Marriage Timing', 'திருமண கால நிர்ணயம்', 'Timing indicators and Dasa-Bhukti influences.', 'திருமணம் கைகூடும் காலம் மற்றும் தசா-புக்தி அமைப்புகள்.', 2),
('first_marriage', 'marriage_relationships', 'First Marriage', 'முதல் திருமணம்', 'Specific indicators governing first marriage.', 'முதல் திருமண பந்தம் மற்றும் அதன் இயல்புகள்.', 3),
('second_marriage', 'marriage_relationships', 'Second Marriage', 'இரண்டாம் திருமணம்', 'Indicators of multiple unions or remarriage.', 'இரண்டாம் திருமணம் மற்றும் மறுமணத்திற்கான பாரம்பரிய ஜோதிட விதிகள்.', 4),
('delayed_marriage', 'marriage_relationships', 'Delayed Marriage', 'திருமணத் தடை மற்றும் காலதாமதம்', 'Saturn, Sun, or nodal delay influences.', 'சனி, சூரியன், ராகு-கேது தாக்கங்களால் ஏற்படும் தாமத திருமண யோகங்கள்.', 5),
('love_marriage', 'marriage_relationships', 'Love Marriage', 'காதல் திருமணம்', '5th and 7th house lord connections.', '5 மற்றும் 7-ஆம் அதிபதிகள் தொடர்பு, சுக்கிரன்-செவ்வாய், ராகு சேர்க்கைகள்.', 6),
('arranged_marriage', 'marriage_relationships', 'Arranged Marriage', 'பெரியோர்களால் நிச்சயிக்கப்பட்ட திருமணம்', 'Traditional arranged marriage alignments.', 'குடும்பத்தினரால் பேசி முடிக்கப்படும் திருமணத்திற்கான கிரக நிலைகள்.', 7),
('spouse_characteristics', 'marriage_relationships', 'Spouse Characteristics', 'வாழ்க்கைத் துணையின் குணநலன்கள்', '7th house and Venus indicators of spouse.', '7-ஆம் பாவம், நவாம்ச லக்னம் மூலம் துணையின் குணம் மற்றும் தோற்றம்.', 8),
('relationship_compatibility', 'marriage_relationships', 'Relationship Compatibility', 'உறவுப் பொருத்தம்', 'Interplanetary harmony and mutual trines.', 'தம்பதியர் இடையே பரஸ்பர இணக்கம் மற்றும் பொருத்தம்.', 9),
('career_profession', 'career_profession', 'Career & Profession', 'தொழில் மற்றும் உத்தியோகம்', 'General employment and career indicators.', 'உத்தியோக யோகம் மற்றும் வேலை வாய்ப்புகள்.', 10),
('government_employment', 'career_profession', 'Government Employment', 'அரசுப் பணி யோகம்', 'Sun, Mars, and 10th lord authority.', 'சூரியன், செவ்வாய் பலம் மற்றும் அரசு உத்தியோக யோகங்கள்.', 11),
('business_entrepreneurship', 'career_profession', 'Business & Entrepreneurship', 'சுயதொழில் மற்றும் வணிகம்', 'Commercial acumen and entrepreneurship.', 'வியாபாரம், சுயதொழில் மற்றும் வர்த்தகத் துறை அமைப்புகள்.', 12),
('personality_birth', 'personality_birth', 'Personality & Birth Characteristics', 'சுய ஆளுமை மற்றும் பிறப்புக் குணங்கள்', 'Temperament, Nakshatra, and Lagna traits.', 'சுய ஆளுமை, நட்சத்திரம் மற்றும் லக்ன இயல்புகள்.', 13),
('lagna_characteristics', 'personality_birth', 'Lagna Characteristics', 'லக்ன குணநலன்கள்', 'Ascendant sign traits and outlook.', 'பிறந்த லக்னத்தின் இயல்புகள், உடல் அமைப்பு மற்றும் பொது நடத்தை.', 14),
('nakshatra_characteristics', 'personality_birth', 'Nakshatra Characteristics', 'நட்சத்திர குணநலன்கள்', 'Core temperament governed by birth star.', 'ஜென்ம நட்சத்திரத்தின் அடிப்படை குணாதிசயங்கள்.', 15),
('planetary_strengths', 'personality_birth', 'Planetary Strengths', 'கிரகங்களின் பலம் மற்றும் வீரியம்', 'Exaltation and Vargottama dignities.', 'ஷட்பல பலம், உச்சம், வர்கோத்தம அமைப்புகளின் தாக்கங்கள்.', 16),
('sexuality_intimacy', 'sexuality_intimacy', 'Sexuality & Intimacy', 'ஈர்ப்பு மற்றும் தாம்பத்திய அந்தரங்கம்', 'Traditional classical interpretations of attraction.', 'ஈர்ப்பு மற்றும் தாம்பத்திய அந்தரங்கம் சார்ந்த பாரம்பரிய ஜோதிட விதிகள்.', 17),
('attraction_interpretations', 'sexuality_intimacy', 'Traditional Attraction Interpretations', 'பாரம்பரிய ஈர்ப்பு விளக்கங்கள்', 'Classical principles of magnetism and desire.', 'கவர்ச்சி மற்றும் ஈர்ப்பு தொடர்பான பாரம்பரிய ஜோதிட விதிகள்.', 18),
('intimacy_themes', 'sexuality_intimacy', 'Intimacy-Related Themes', 'தாம்பத்திய நெருக்கக் கூறுகள்', '12th house Shayana Sukha comfort.', '8 மற்றும் 12-ஆம் பாவங்கள் வழி அமையும் சயன சுகம் மற்றும் ரகசிய ஈடுபாடு.', 19),
('money_assets', 'money_assets', 'Money & Assets', 'தனம் மற்றும் சொத்துக்கள்', 'Wealth accumulation and Dhana yogas.', '1, 2, 5, 9, 11-ஆம் அதிபதிகளால் ஏற்படும் லட்சுமி மற்றும் தன யோகங்கள்.', 20),
('wealth_yogas', 'money_assets', 'Wealth & Dhana Yogas', 'தன யோகங்கள் மற்றும் செல்வம்', 'Classical Dhana combinations.', 'தன யோகங்கள் மற்றும் செல்வம் பெருகும் அமைப்புகள்.', 21),
('savings_accumulation', 'money_assets', 'Savings & Accumulation', 'சேமிப்பு மற்றும் தன இருப்பு', '2nd house and Jupiter protection.', '2-ஆம் பாவம் மற்றும் தனகாரகன் குருவின் பார்வையால் சேரும் நிதி.', 22),
('property_land', 'money_assets', 'Property & Real Estate', 'நிலம் மற்றும் பூமி யோகம்', '4th house and Mars real estate yogas.', '4-ஆம் பாவம், செவ்வாய் பலம் தரும் பூமி, நிலம், வீடு யோகங்கள்.', 23),
('family_children', 'family_children', 'Family & Children', 'குடும்பம் மற்றும் குழந்தைகள்', 'Children prospects and lineage blessings.', '5-ஆம் பாவம், புத்திரகாரகன் குரு மற்றும் நற்புத்திர யோகங்கள்.', 24),
('children_prospects', 'family_children', 'Children Prospects', 'புத்திர பாக்கியம்', '5th house progeny blessing.', 'புத்திர பாக்கியம் மற்றும் பிள்ளைகளின் வளர்ச்சி.', 25),
('education_travel', 'education_travel', 'Education & Travel', 'கல்வி மற்றும் பயணங்கள்', 'Higher education and long journeys.', 'உயர் கல்வி மற்றும் வெளிநாட்டுப் பயணங்கள்.', 26),
('higher_education', 'education_travel', 'Higher Education & Degrees', 'உயர்கல்வி மற்றும் பட்டப் படிப்பு', 'Scholarly degrees and specialization.', '5 மற்றும் 9-ஆம் அதிபதிகள் தரும் உயர்கல்வி, கல்லூரிப் படிப்பு யோகம்.', 27),
('foreign_travel', 'education_travel', 'Foreign Travel & Journeys', 'வெளிநாட்டுப் பயணம்', '9th and 12th house foreign travels.', '9, 12-ஆம் பாவங்கள் மற்றும் சர ராசிகளால் உருவாகும் தூர தேசப் பயணம்.', 28)
ON CONFLICT (slug) DO UPDATE SET
    name_en = EXCLUDED.name_en,
    name_ta = EXCLUDED.name_ta,
    description_en = EXCLUDED.description_en,
    description_ta = EXCLUDED.description_ta,
    display_order = EXCLUDED.display_order,
    updated_at = NOW();
