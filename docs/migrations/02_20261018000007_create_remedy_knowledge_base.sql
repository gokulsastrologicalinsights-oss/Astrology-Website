-- Gokul's Astrological Insights - Remedies & Pariharam Module Database Migration
-- Migration: 20261018000007_create_remedy_knowledge_base.sql
-- Description: Establishes the clean-room Remedy Knowledge Base:
--              1. public.remedy_source_references (classical shastras, puranas, traditions)
--              2. public.remedies_problem_taxonomy (39 verified life problem categories in EN/TA)
--              3. public.remedies_catalog (verified mantras, worship, daan, fasting, and temple remedies)
--              4. public.navagraha_temples (the 9 authentic Kaveri Delta Tamil Navagraha temples)
--              Configures RLS policies, indexes, and seeds verified foundational records.

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Table: public.remedy_source_references
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Table: public.remedies_problem_taxonomy
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Table: public.remedies_catalog
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Table: public.navagraha_temples
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Row Level Security (RLS) Policies
-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Grants
-- ─────────────────────────────────────────────────────────────────────────────
GRANT ALL ON TABLE public.remedy_source_references TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.remedies_problem_taxonomy TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.remedies_catalog TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.navagraha_temples TO anon, authenticated, service_role;

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Seed: Canonical Shastra & Stotra Source References
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO public.remedy_source_references (code, title_en, title_sa, author, tradition, canonical_status, description)
VALUES
('BPHS', 'Brihat Parashara Hora Shastra', 'बृहत्पाराशरहोराशास्त्रम्', 'Maharishi Parashara', 'classical_jyotish', 'primary_shastra', 'Foundational compendium of Vedic astrology detailing planetary natures, avasthas, afflictions, and classical shanti remedies.'),
('PHALADEEPIKA', 'Phaladeepika', 'फलदीपिका', 'Mantreswara', 'classical_jyotish', 'primary_shastra', 'Classical medieval text covering planetary strengths, bhava results, yogas, and remedial pacification.'),
('NAVAGRAHA_STOTRAM', 'Sri Navagraha Stotram', 'नवग्रहस्तोत्रम्', 'Sri Veda Vyasa', 'puranic', 'stotra_samhita', 'Nine sacred hymns composed by Sage Veda Vyasa in the Mahabharata / Puranic tradition to propitiate the nine celestial grahas.'),
('VALMIKI_RAMAYANA', 'Valmiki Ramayana - Aditya Hridayam', 'आदित्यहृदयम्', 'Sage Agastya / Maharishi Valmiki', 'puranic', 'stotra_samhita', 'Sacred hymn imparted by Sage Agastya to Lord Sri Rama on the battlefield (Yuddha Kanda 105) for victory, health, and dispelling inner fear.'),
('RIGVEDA', 'Rigveda Samhita - Maha Mrityunjaya', 'त्र्यम्बकं यजामहे', 'Rishi Markandeya / Sage Vasistha', 'vedic', 'primary_shastra', 'The great death-conquering hymn (Rigveda 7.59.12) dedicated to Rudra for vital protection, healing, and freedom from disease and fear.'),
('MANTRA_MAHODADHI', 'Mantra Mahodadhi', 'मन्त्रमहोदधिः', 'Mahidhara', 'tantric', 'stotra_samhita', 'Comprehensive encyclopaedia of traditional Vedic-Tantric mantra vidhi, seed syllables (bijakshara), and japa procedures.'),
('KAVERI_DELTA_TRADITION', 'Kaveri Delta Navagraha Sthala Purana', 'காவிரி டெல்டா நவகிரக ஸ்தல புராணம்', 'Tamil Shaiva-Vaishnava Tradition', 'tamil_shaiva', 'regional_tradition', 'Sacred temple traditions of the nine classical Navagraha sthalams located around Kumbakonam, Thanjavur, and Mayiladuthurai in Tamil Nadu.')
ON CONFLICT (code) DO UPDATE SET
    title_en = EXCLUDED.title_en,
    title_sa = EXCLUDED.title_sa,
    author = EXCLUDED.author,
    tradition = EXCLUDED.tradition,
    canonical_status = EXCLUDED.canonical_status,
    description = EXCLUDED.description,
    updated_at = NOW();

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. Seed: The 39 Verified Problem Taxonomy Categories
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO public.remedies_problem_taxonomy (slug, category, name_en, name_ta, description_en, description_ta, primary_karakas, governing_houses, display_order)
VALUES
-- Career (1-5)
('career_delay', 'career', 'Career Growth Delays', 'தொழில் மற்றும் வேலை வளர்ச்சி தாமதம்', 
 'Persistent obstacles, stagnation, or delays in securing employment or career advancement.', 
 'வேலை கிடைப்பதில் அல்லது பதவி உயர்வில் ஏற்படும் தொடர் தடைகள் மற்றும் தேக்க நிலை.', 
 ARRAY['saturn', 'sun', 'jupiter'], ARRAY[10, 6, 2], 1),

('job_loss_instability', 'career', 'Job Loss & Professional Instability', 'வேலை இழப்பு மற்றும் பணியிட நிலையற்ற தன்மை', 
 'Frequent layoffs, unstable job tenure, or sudden termination in career.', 
 'அடிக்கடி வேலை மாறுதல், வேலை இழப்பு அபாயம் அல்லது நிறுவனத்தில் ஏற்படும் நிலையற்ற சூழல்.', 
 ARRAY['saturn', 'rahu', 'mercury'], ARRAY[10, 6, 8], 2),

('business_setbacks', 'career', 'Business Setbacks & Trade Slumps', 'வணிகத் தடைகள் மற்றும் நஷ்டம்', 
 'Financial blockages, client loss, or unviable trade downturns in business ventures.', 
 'வியாபாரத்தில் ஏற்படும் தொடர் பின்னடைவு, வாடிக்கையாளர் இழப்பு மற்றும் வர்த்தகத் தேக்கம்.', 
 ARRAY['mercury', 'jupiter', 'venus'], ARRAY[7, 10, 11], 3),

('promotion_blocks', 'career', 'Promotion & Recognition Blocks', 'பதவி உயர்வு மற்றும் அங்கீகாரத் தடைகள்', 
 'Passed over for promotions, lack of administrative recognition despite dedicated effort.', 
 'கடின உழைப்பிற்குரிய அங்கீகாரம் கிடைக்காமை மற்றும் தகுதியிருந்தும் பதவி உயர்வு தள்ளிப்போதல்.', 
 ARRAY['sun', 'jupiter', 'mars'], ARRAY[10, 11, 1], 4),

('workplace_conflicts', 'career', 'Workplace Politics & Authority Conflicts', 'பணியிடத்தில் மேலதிகாரி மற்றும் சக ஊழியர் பிணக்குகள்', 
 'Severe friction with superiors, organizational politics, or hostile working conditions.', 
 'உயர் அதிகாரிகளுடன் கருத்து மோதல்கள், அலுவலக அரசியல் மற்றும் மன உளைச்சல்.', 
 ARRAY['sun', 'mars', 'saturn'], ARRAY[10, 6, 3], 5),

-- Relationships & Marriage (6-11)
('marriage_delay', 'relationships_marriage', 'Delay in Marriage', 'திருமணத் தாமதம்', 
 'Obstacles in finding an aligned life partner or persistent delays in finalizing marriage alliances.', 
 'பொருத்தமான வரன் அமைவதில் தாமதம் மற்றும் திருமணப் பேச்சுவார்த்தைகளில் ஏற்படும் தடைகள்.', 
 ARRAY['venus', 'jupiter', 'mars'], ARRAY[7, 2, 8], 6),

('marital_discord', 'relationships_marriage', 'Marital Discord & Misunderstandings', 'தம்பதியர் இடையே கருத்து வேறுபாடு', 
 'Recurrent arguments, emotional estrangement, and lack of harmony between spouses.', 
 'கணவன் மனைவி இடையே ஏற்படும் பரஸ்பர நம்பிக்கையின்மை, வாக்குவாதங்கள் மற்றும் அமைதியின்மை.', 
 ARRAY['venus', 'mars', 'moon'], ARRAY[7, 4, 2], 7),

('separation_divorce_risk', 'relationships_marriage', 'Threat of Separation & Legal Divorce', 'பிரிவு மற்றும் விவாகரத்து அச்சுறுத்தல்', 
 'Impending breakdown of marriage, court litigation, or emotional rupture between partners.', 
 'குடும்பப் பிளவு, விவாகரத்து வழக்குகள் மற்றும் நிரந்தரப் பிரிவினை அபாயம்.', 
 ARRAY['saturn', 'rahu', 'mars'], ARRAY[7, 8, 12], 8),

('relationship_breakdown', 'relationships_marriage', 'Heartbreak & Relationship Ruptures', 'காதல் மற்றும் உறவு முறிவு', 
 'Emotional distress from sudden broken relationships, deceit, or emotional abandonment.', 
 'காதல் முறிவு, துரோகம் மற்றும் உணர்வுபூர்வமான தனிமைத் துயரம்.', 
 ARRAY['venus', 'moon', 'rahu'], ARRAY[5, 7, 12], 9),

('inlaw_family_strife', 'relationships_marriage', 'In-Law & Extended Family Strife', 'குடும்ப மற்றும் மாமியார்-மருமகள் சச்சரவுகள்', 
 'Chronic conflict between spouses and in-laws disrupting domestic harmony.', 
 'கூட்டுக் குடும்பச் சிக்கல்கள் மற்றும் உறவினர்களிடையே நிலவும் மனக்கசப்புகள்.', 
 ARRAY['moon', 'mars', 'mercury'], ARRAY[4, 2, 9], 10),

('progeny_childbirth_delay', 'relationships_marriage', 'Delay in Progeny & Childbirth', 'புத்திர பாக்கிய தாமதம்', 
 'Difficulties or medical/astrological delays in conceiving and bearing healthy offspring.', 
 'குழந்தைப் பேறு பெறுவதில் ஏற்படும் தடைகள் மற்றும் மருத்துவ/ஜோதிட ரீதியான தாமதங்கள்.', 
 ARRAY['jupiter', 'sun', 'mars'], ARRAY[5, 9, 2], 11),

-- Health & Wellness (12-17)
('chronic_health_issues', 'health_wellness', 'Chronic Health Ailments', 'நீண்ட கால உடல் உபாதைகள்', 
 'Recurring illnesses, systemic weaknesses, or long-term chronic conditions.', 
 'நீண்ட காலம் தொடரும் உடல் நலக் குறைபாடுகள் மற்றும் குணமடையாத உபாதைகள்.', 
 ARRAY['sun', 'saturn', 'mars'], ARRAY[6, 8, 1], 12),

('mental_anxiety_depression', 'health_wellness', 'Anxiety, Depression & Insomnia', 'மன அழுத்தம், பதற்றம் மற்றும் தூக்கமின்மை', 
 'Emotional turbulence, panic, restlessness, obsessive thoughts, or inability to sleep peacefully.', 
 'அதிகப்படியான மனக்கவலை, அமைதியின்மை, மனச்சோர்வு மற்றும் தூக்கக் கோளாறுகள்.', 
 ARRAY['moon', 'rahu', 'mercury'], ARRAY[1, 4, 12], 13),

('eye_vision_ailments', 'health_wellness', 'Vision & Headaches', 'கண் பார்வை மற்றும் தலைவலி பிரச்சினைகள்', 
 'Recurring migraines, eye strain, vision problems, and nervous headaches.', 
 'கண் உபாதைகள், பார்வை மங்கல், கடுமையான தலைவலி மற்றும் ஒற்றைத் தலைவலி.', 
 ARRAY['sun', 'moon', 'mars'], ARRAY[2, 12, 1], 14),

('bone_joint_mobility', 'health_wellness', 'Bone, Joint & Vata Disorders', 'எலும்பு, மூட்டு மற்றும் வாத உபாதைகள்', 
 'Arthritis, joint stiffness, spinal weaknesses, or fractures related to bone density.', 
 'மூட்டு வலி, வாதக் கோளாறுகள், முதுகுத்தண்டு பிரச்சினைகள் மற்றும் எலும்பு தேய்மானம்.', 
 ARRAY['saturn', 'sun', 'mars'], ARRAY[6, 8, 10], 15),

('digestive_stomach_ailments', 'health_wellness', 'Digestive & Metabolic Disturbances', 'செரிமானம் மற்றும் வயிறு உபாதைகள்', 
 'Gastric disorders, liver sluggishness, or metabolic imbalances.', 
 'செரிமானக் கோளாறுகள், கல்லீரல் பிரச்சினைகள் மற்றும் வயிற்று உபாதைகள்.', 
 ARRAY['jupiter', 'sun', 'mars'], ARRAY[5, 6, 1], 16),

('vitality_low_energy', 'health_wellness', 'Low Vitality & Chronic Fatigue', 'குறைந்த ஆற்றல் மற்றும் சோம்பல்', 
 'Lack of stamina, chronic lethargy, weak immunity, and diminished physical resilience.', 
 'உடல் சோர்வு, நோய் எதிர்ப்பு சக்தி குறைவு மற்றும் உற்சாகமின்மை.', 
 ARRAY['sun', 'mars', 'jupiter'], ARRAY[1, 3, 6], 17),

-- Finance & Wealth (18-22)
('financial_instability', 'finance_wealth', 'Income Instability & Cash Crunch', 'பணப்புழக்கத் தட்டுப்பாடு மற்றும் வருமானத் தடை', 
 'Unpredictable cash flows, delays in receiving payments, or insufficient regular income.', 
 'முறையான வருமானமின்மை, வரவு செலவு சமநிலையின்மை மற்றும் பண நெருக்கடி.', 
 ARRAY['jupiter', 'mercury', 'venus'], ARRAY[2, 11, 9], 18),

('chronic_debt_burden', 'finance_wealth', 'Chronic Debt & Borrowing Traps', 'கடன் சுமை மற்றும் தீராத கடன்', 
 'Inability to repay loans, accumulating interest burdens, and financial entrapment.', 
 'அதிகரிக்கும் கடன் தொல்லைகள், வட்டிச் சுமை மற்றும் கடன் அடைப்பதில் உள்ள சிக்கல்கள்.', 
 ARRAY['mars', 'saturn', 'rahu'], ARRAY[6, 8, 12], 19),

('speculation_gambling_losses', 'finance_wealth', 'Speculative & Investment Losses', 'பங்குச்சந்தை மற்றும் ஊக வணிக இழப்புகள்', 
 'Severe losses in stock trading, speculative ventures, or fraudulent schemes.', 
 'பங்கு வர்த்தகம், சூதாட்டம் மற்றும் தவறான முதலீடுகளால் ஏற்படும் பெரும் பொருளாதார இழப்புகள்.', 
 ARRAY['rahu', 'mercury', 'mars'], ARRAY[5, 8, 12], 20),

('wealth_accumulation_block', 'finance_wealth', 'Obstacles in Wealth Accumulation', 'சேமிப்பு இன்மை மற்றும் திடீர் பண இழப்பு', 
 'Money leaking through unexpected expenses, lack of sustained savings despite good earnings.', 
 'வருமானம் இருந்தும் சேமிக்க முடியாமை மற்றும் எதிர்பாராத விரயங்கள் ஏற்படுதல்.', 
 ARRAY['jupiter', 'venus', 'saturn'], ARRAY[2, 11, 12], 21),

('inheritance_disputes', 'finance_wealth', 'Inheritance & Ancestral Wealth Issues', 'பூர்வீகச் சொத்து மற்றும் வாரிசுரிமைச் சிக்கல்கள்', 
 'Stalled legacy wealth, contested parental estates, and division of ancestral property.', 
 'பூர்வீகச் சொத்து கிடைப்பதில் தடைகள் மற்றும் பங்காளிகளிடையே நிலவும் பாகப்பிரிவினை முரண்பாடுகள்.', 
 ARRAY['saturn', 'jupiter', 'sun'], ARRAY[8, 9, 4], 22),

-- Property & Legal (23-26)
('land_property_disputes', 'property_legal', 'Land & Real Estate Disputes', 'நிலம் மற்றும் மனை தொடர்பான தகராறுகள்', 
 'Contested land titles, boundary encroachments, or fraudulent real estate transactions.', 
 'நிலம், மனை வாங்குவதில் தடைகள், எல்லைத் தகராறுகள் மற்றும் சொத்து விவகாரங்கள்.', 
 ARRAY['mars', 'saturn', 'rahu'], ARRAY[4, 6, 8], 23),

('litigation_court_cases', 'property_legal', 'Court Cases & Legal Battles', 'நீதிமன்ற வழக்குகள் மற்றும் சட்டப் போராட்டங்கள்', 
 'Protracted litigation, unfair allegations, or stressful judicial proceedings.', 
 'நீதிமன்ற வழக்குகள், அவதூறுகள் மற்றும் அரசு/சட்ட ரீதியான பிரச்சினைகள்.', 
 ARRAY['saturn', 'mars', 'rahu'], ARRAY[6, 8, 12], 24),

('house_construction_hurdles', 'property_legal', 'House Construction Obstacles', 'வீடு கட்டும் பணியில் தடைகள்', 
 'Stalled home construction, contractor disputes, municipal hurdles, or Vastu flaws.', 
 'புதிய வீடு கட்டத் தொடங்குவதில் தடைகள், கட்டுமானப் பணியில் தாமதம் மற்றும் வாஸ்து குறைபாடுகள்.', 
 ARRAY['mars', 'saturn', 'jupiter'], ARRAY[4, 1, 9], 25),

('vehicle_accidents_breakdowns', 'property_legal', 'Vehicle Accidents & Frequent Breakdowns', 'வாகன விபத்துகள் மற்றும் பழுதுகள்', 
 'Repeated vehicle damages, close calls, road accidents, or mechanical failure costs.', 
 'அடிக்கடி நிகழும் வாகன விபத்துகள், இயந்திரக் கோளாறுகள் மற்றும் பயணப் பயம்.', 
 ARRAY['mars', 'rahu', 'ketu'], ARRAY[4, 8, 6], 26),

-- Education & Intellect (27-30)
('academic_focus_memory', 'education_intellect', 'Lack of Concentration & Weak Memory', 'கல்வியில் கவனக்குறைவு மற்றும் நினைவாற்றல் மந்தம்', 
 'Mental distractions, poor retention of lessons, and study restlessness in students.', 
 'படிப்பில் கவனம் செலுத்த முடியாமை, நினைவாற்றல் குறைவு மற்றும் மந்த நிலை.', 
 ARRAY['mercury', 'moon', 'jupiter'], ARRAY[4, 5, 1], 27),

('exam_competitive_hurdles', 'education_intellect', 'Competitive Exam Hurdles', 'போட்டித் தேர்வுகள் மற்றும் நேர்முகத் தேர்வு தடைகள்', 
 'Falling short by small margins in government or professional competitive examinations.', 
 'போட்டித் தேர்வுகள், நேர்முகத் தேர்வுகளில் தொடர்ந்து ஏற்படும் மயிரிழைத் தோல்விகள்.', 
 ARRAY['mercury', 'sun', 'mars'], ARRAY[5, 6, 10], 28),

('speech_communication_blocks', 'education_intellect', 'Speech Impediments & Stammering', 'பேச்சுத் தடை மற்றும் தயக்கம்', 
 'Vocal hesitation, stammering, fear of public address, or ineffective communication.', 
 'பேசுவதில் தயக்கம், திக்குவாய், பொது இடங்களில் பேசும் பயம் மற்றும் சொற்குளறுபடிகள்.', 
 ARRAY['mercury', 'jupiter', 'ketu'], ARRAY[2, 3, 1], 29),

('higher_education_obstacles', 'education_intellect', 'Higher Education & Research Blocks', 'உயர் கல்வி மற்றும் ஆராய்ச்சித் தடைகள்', 
 'Hurdles in securing university admission, mentor disagreements, or delayed doctoral degrees.', 
 'பல்கலைக்கழக சேர்க்கை, முனைவர் பட்ட ஆராய்ச்சி மற்றும் உயர் கல்வியில் ஏற்படும் முட்டுக்கட்டைகள்.', 
 ARRAY['jupiter', 'mercury', 'sun'], ARRAY[9, 5, 4], 30),

-- Spiritual Growth & Karmic (31-35)
('spiritual_stagnation', 'spiritual_growth', 'Spiritual Stagnation & Meditation Restlessness', 'ஆன்மீக முன்னேற்றமின்மை மற்றும் தியானத் தடைகள்', 
 'Difficulty settling the wandering mind, lack of spiritual inspiration, and inner void.', 
 'தியானத்தில் மனம் ஒருமுகப்படாமை, ஆன்மீகத் தேக்க நிலை மற்றும் மனச்சோர்வு.', 
 ARRAY['ketu', 'jupiter', 'saturn'], ARRAY[12, 9, 8], 31),

('fear_negative_energies', 'spiritual_growth', 'Fear, Evil Eye & Psychological Unease', 'விளக்க முடியாத அச்சம் மற்றும் கண் திருஷ்டி', 
 'Unexplained dread, pervasive sense of negative scrutiny, and psychic heaviness.', 
 'கண் திருஷ்டி, காரணமில்லாத பயம், கெட்ட எண்ணங்களின் தாக்கம் மற்றும் எதிர்மறை அதிர்வுகள்.', 
 ARRAY['rahu', 'mars', 'ketu'], ARRAY[8, 12, 6], 32),

('ancestral_karmic_blocks', 'spiritual_growth', 'Ancestral Karmic Burdens (Pitru Dosha)', 'பித்ரு தோஷம் மற்றும் முன்னோர்களின் ஆசியின்மை', 
 'Recurrent unexplainable hardships indicating unresolved ancestral rites or karmic obligations.', 
 'குடும்பத்தில் ஏற்படும் விவரிக்க முடியாத தடைகள், வம்சாவளி பிரச்சினைகள் மற்றும் பித்ரு தோஷ அறிகுறிகள்.', 
 ARRAY['sun', 'rahu', 'saturn'], ARRAY[9, 5, 8], 33),

('recurrent_nightmares', 'spiritual_growth', 'Disturbed Sleep & Recurrent Nightmares', 'கெட்ட கனவுகள் மற்றும் இரவில் பயம்', 
 'Frightening dreams, sleep paralysis, and distress upon waking during the night.', 
 'இரவில் திடுக்கிட்டு விழித்தல், பயமுறுத்தும் கெட்ட கனவுகள் மற்றும் தூக்கக் கலக்கம்.', 
 ARRAY['moon', 'rahu', 'ketu'], ARRAY[12, 4, 8], 34),

('past_life_karmic_burdens', 'spiritual_growth', 'Unexplainable Karmic Hardships (Prarabdha)', 'காரணமற்ற தொடர் தடைகள் மற்றும் பிராரப்த கர்மா', 
 'Obstacles persisting despite faultless planning, requiring surrender and spiritual propitiation.', 
 'அனைத்து முயற்சிகளும் இருந்தும் காரணமின்றி ஏற்படும் தோல்விகள் மற்றும் விதிப்பயன் தடைகள்.', 
 ARRAY['saturn', 'ketu', 'jupiter'], ARRAY[12, 8, 9], 35),

-- Travel & Foreign (36-39)
('visa_immigration_delays', 'travel_foreign', 'Visa & Immigration Delays', 'விசா மற்றும் வெளிநாட்டுப் பயணத் தடைகள்', 
 'Red tape, consulate rejections, and prolonged delays in securing international travel permits.', 
 'விசா கிடைப்பதில் காலதாமதம், தூதரக முட்டுக்கட்டைகள் மற்றும் வெளிநாட்டுப் பயணத் தடைகள்.', 
 ARRAY['rahu', 'moon', 'jupiter'], ARRAY[9, 12, 3], 36),

('foreign_settlement_hardships', 'travel_foreign', 'Hardships in Foreign Settlement', 'வெளிநாட்டில் குடியமர்வு மற்றும் வேலைப் பிரச்சினைகள்', 
 'Struggles in finding secure employment, permanent residency, or stability abroad.', 
 'வெளிநாட்டில் நிரந்தரக் குடியுரிமை, நல்ல வேலை மற்றும் வாழ்க்கை அமைவதில் ஏற்படும் இன்னல்கள்.', 
 ARRAY['rahu', 'saturn', 'venus'], ARRAY[12, 9, 7], 37),

('relocation_adjustment_stress', 'travel_foreign', 'Relocation & City Change Stress', 'இடப்பெயர்வு மற்றும் ஊர் மாற்றத் துயரம்', 
 'Disorientation, loneliness, and adaptation difficulties after shifting domestic location.', 
 'புதிய ஊர் அல்லது வீட்டிற்கு மாறிய பின் ஏற்படும் உடல்/மன நலக் குறைபாடுகள் மற்றும் சங்கடங்கள்.', 
 ARRAY['moon', 'mercury', 'saturn'], ARRAY[4, 12, 3], 38),

('frequent_travel_mishaps', 'travel_foreign', 'Frequent Travel Mishaps & Delays', 'பயணங்களில் தடைகள் மற்றும் இழப்புகள்', 
 'Lost luggage, missed connections, cancellations, and physical exhaustion during journeys.', 
 'பயணங்களின் போது ஏற்படும் பொருட்கள் இழப்பு, விபத்துகள் மற்றும் தொடர் அலைச்சல்கள்.', 
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. Seed: The 9 Authentic Kaveri Delta Tamil Navagraha Temples
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO public.navagraha_temples (
    code, graha, name_en, name_ta, presiding_deity_en, presiding_deity_ta,
    graha_deity_en, graha_deity_ta, place_name_en, place_name_ta,
    district_en, district_ta, state, latitude, longitude,
    visiting_day_en, visiting_day_ta, significance_en, significance_ta,
    remedy_offerings_en, remedy_offerings_ta, source_tradition
) VALUES
('TEMPLE_SURYANAR_KOVIL', 'sun', 
 'Suryanar Kovil', 'சூரியனார் கோவில்',
 'Sri Suryanarayana Swamy', 'ஸ்ரீ சூரியநாராயண சுவாமி',
 'Lord Surya (Sun)', 'சூரிய பகவான்',
 'Suryanar Kovil (near Aduthurai)', 'சூரியனார் கோவில் (ஆடுதுறை அருகில்)',
 'Thanjavur', 'தஞ்சாவூர்', 'Tamil Nadu', 11.025300, 79.489100,
 'Sunday', 'ஞாயிற்றுக்கிழமை',
 'The premier Sun temple in Tamil Nadu where Lord Surya is worshipped with his consorts Usha and Chhaya. Uniquely houses shrines for all other eight grahas facing Surya.',
 'தமிழகத்தின் முதன்மை சூரிய தலம். உஷா, சாயா தேவியருடன் சூரிய பகவான் அருள்பாலிக்கிறார். மற்ற எட்டு கிரகங்களும் சூரியனை நோக்கியவாறு தனித்தனி சன்னதிகளில் அமைந்திருப்பது இதன் தனிச்சிறப்பு.',
 'Offering wheat, jaggery, red flowers, lighting ghee lamps, performing circumambulation (pradakshina) on Sundays at dawn.',
 'கோதுமை, வெல்லம், செந்தாமரை மலர்கள் சமர்ப்பித்தல், நெய் தீபம் ஏற்றுதல் மற்றும் ஞாயிறு அதிகாலை பிரதட்சணம் செய்தல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THINGALUR', 'moon',
 'Thingalur Kailasanathar Temple', 'திங்களூர் கைலாசநாதர் கோவில்',
 'Sri Kailasanathar and Goddess Periyanayaki', 'ஸ்ரீ கைலாசநாதர் - பெரியநாயகி அம்மன்',
 'Lord Chandra (Moon)', 'சந்திர பகவான்',
 'Thingalur (near Thiruvaiyaru)', 'திங்களூர் (திருவையாறு அருகில்)',
 'Thanjavur', 'தஞ்சாவூர்', 'Tamil Nadu', 10.878900, 79.167800,
 'Monday', 'திங்கட்கிழமை',
 'Classical Moon sthalam where Lord Moon worshipped Shiva to regain luminosity. Associated with relief from maternal distress, mental instability, and emotional turmoil.',
 'சந்திர தோஷ நிவர்த்தி தலம். சந்திரன் சிவபெருமானை பூஜித்து சாப விமோசனம் பெற்ற இடம். மன அமைதி, தாயார் நலம் மற்றும் கல்வி மேன்மை அருளும் தலம்.',
 'Offering white raw rice, milk kheer (payasam), white cloth, white arali flowers, lighting lamps on Mondays.',
 'பச்சரிசி, பசும்பால் பாயாசம், வெள்ளை வஸ்திரம், வெள்ளை அரளி மலர்கள் சாற்றி திங்கள்கிழமை வழிபாடு செய்தல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_VAITHEESWARAN', 'mars',
 'Vaitheeswaran Kovil', 'வைத்தீஸ்வரன் கோவில்',
 'Sri Vaidyanatha Swamy and Goddess Thaiyalnayaki', 'ஸ்ரீ வைத்தியநாத சுவாமி - தையல்நாயகி அம்மன்',
 'Lord Sevvai / Angarakan (Mars)', 'அங்காரகன் / செவ்வாய் பகவான்',
 'Vaitheeswaran Kovil (near Sirkazhi)', 'வைத்தீஸ்வரன் கோவில் (சீர்காழி அருகில்)',
 'Mayiladuthurai', 'மயிலாடுதுறை', 'Tamil Nadu', 11.202300, 79.731400,
 'Tuesday', 'செவ்வாய்க்கிழமை',
 'World-renowned healing sthalam and supreme Mars (Angaraka) pilgrimage. Lord Shiva as the Divine Physician heals physical ailments, removes Kuja / Manglik dosha, and settles property obstacles.',
 'புகழ்பெற்ற செவ்வாய் ஸ்தலம் மற்றும் பிணி தீர்க்கும் தலம். வைத்தீஸ்வரர் சித்தாமிர்த தீர்த்தத்துடன் தீராத நோய்களைத் தீர்த்து, செவ்வாய் தோஷம் மற்றும் நிலம் சார்ந்த தடைகளை நீக்குகிறார்.',
 'Offering red lentils (thoor/masoor dal), red cloth, vilvam leaves, and lighting sesame/ghee lamps on Tuesdays.',
 'துவரம்பருப்பு, சிவப்பு வஸ்திரம், செவ்வரளி மாலை சாற்றி, சித்தாமிர்த தீர்த்தத்தில் நீராடி செவ்வாய்க்கிழமை வழிபடுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUVENKADU', 'mercury',
 'Thiruvenkadu Swetharanyeswarar Temple', 'திருவெண்காடு சுவேதாரண்யேஸ்வரர் கோவில்',
 'Sri Swetharanyeswarar and Goddess Brahmavidyambigai', 'ஸ்ரீ சுவேதாரண்யேஸ்வரர் - பிரம்மவித்யாம்பிகை',
 'Lord Budhan (Mercury)', 'புதன் பகவான்',
 'Thiruvenkadu (near Poompuhar)', 'திருவெண்காடு (பூம்புகார் அருகில்)',
 'Mayiladuthurai', 'மயிலாடுதுறை', 'Tamil Nadu', 11.178900, 79.823400,
 'Wednesday', 'புதன்கிழமை',
 'Venerated Mercury sthalam known as the Adi Chidambaram. Famed for granting intellectual brilliance, educational excellence, musical talents, and healing nervous disorders.',
 'ஆதி சிதம்பரம் என்று போற்றப்படும் புதன் தலம். புதன் பகவான் தனி சன்னதியில் அருள்கிறார். கல்வி, பேச்சுத்திறன், வணிக மேன்மை மற்றும் நரம்பு மண்டல ஆரோக்கியம் அருளும் தலம்.',
 'Offering green gram (moong dal), green cloth, vilvam leaves, tulasi, lighting lamps on Wednesdays.',
 'பச்சைப்பயறு, பச்சை வஸ்திரம், வெண்காந்தள்/துளசி மாலை சாற்றி புதன்கிழமை தோறும் நெய் தீபமிட்டு வழிபடுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_ALANGUDI', 'jupiter',
 'Alangudi Apatsahayeswarar Temple', 'ஆலங்குடி ஆபத்சகாயேஸ்வரர் கோவில்',
 'Sri Apatsahayeswarar and Goddess Elavarkuzhali', 'ஸ்ரீ ஆபத்சகாயேஸ்வரர் - ஏலவார்குழலி அம்மன்',
 'Lord Guru (Jupiter / Dakshinamurthy)', 'குரு பகவான் / தட்சிணாமூர்த்தி',
 'Alangudi (near Valangaiman)', 'ஆலங்குடி (வலங்கைமான் அருகில்)',
 'Tiruvarur', 'திருவாரூர்', 'Tamil Nadu', 10.825600, 79.408900,
 'Thursday', 'வியாழக்கிழமை',
 'Foremost Jupiter sthalam where Lord Shiva consumed poison to protect the universe. Dedicated Guru shrine worshipped for marital blessings, child boon, spiritual wisdom, and career growth.',
 'தலைசிறந்த குரு பரிகாரத் தலம். ஆபத்சகாயேஸ்வரர் ஆலகால விஷம் உண்டு தேவர்களைக் காத்த இடம். திருமண பாக்கியம், புத்திர பாக்கியம் மற்றும் ஞானம் வேண்டி பக்தர்கள் கூடும் புண்ணிய தலம்.',
 'Offering yellow split chana dal garland, yellow cloth, mullai flowers, lighting 24 ghee deepams on Thursdays.',
 'கொண்டைக்கடலை மாலை, மஞ்சள் வஸ்திரம், முல்லை மலர்கள் சாற்றி 24 நெய் தீபங்கள் ஏற்றி வியாழக்கிழமை வழிபடுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_KANJANUR', 'venus',
 'Kanjanur Agneeswarar Temple', 'கஞ்சனூர் அக்னீஸ்வரர் கோவில்',
 'Sri Agneeswarar and Goddess Karpagambal', 'ஸ்ரீ அக்னீஸ்வரர் - கற்பகாம்பாள்',
 'Lord Sukran (Venus)', 'சுக்கிர பகவான்',
 'Kanjanur (near Kumbakonam)', 'கஞ்சனூர் (கும்பகோணம் அருகில்)',
 'Thanjavur', 'தஞ்சாவூர்', 'Tamil Nadu', 11.066700, 79.483300,
 'Friday', 'வெள்ளிக்கிழமை',
 'Supreme Venus sthalam. Agni Bhagavan worshipped Shiva here to be cured of affliction. Lord Shiva himself reflects the radiant qualities of Sukra here, blessing devotees with prosperity and artistic flourish.',
 'சுக்கிர பகவான் வழிபட்ட முக்கிய தலம். இங்கு சிவபெருமானே சுக்கிரனின் அம்சமாக அருள்பாலிக்கிறார். தம்பதியர் ஒற்றுமை, செல்வம், கலை ஞானம் மற்றும் வாகன யோகம் நல்கும் தலம்.',
 'Offering white field beans (mochai), white silk cloth, white lotus, sweet milk dishes on Fridays.',
 'மொச்சைப்பயறு, வெண்பட்டு, வெண்தாமரை மலர்கள் சாற்றி, சர்க்கரைப் பொங்கல் அல்லது பாயாசம் படைத்து வெள்ளிக்கிழமை வழிபடுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUNALLAR', 'saturn',
 'Thirunallar Dharbaranyeswarar Temple', 'திருநள்ளாறு தர்பாரண்யேஸ்வரர் கோவில்',
 'Sri Dharbaranyeswarar and Goddess Pranambigai', 'ஸ்ரீ தர்பாரண்யேஸ்வரர் - பிராணாம்பிகை',
 'Lord Saneeswara (Saturn)', 'ஸ்ரீ சனீஸ்வர பகவான்',
 'Thirunallar (near Karaikal)', 'திருநள்ளாறு (காரைக்கால் அருகில்)',
 'Karaikal / Puducherry-TN Border', 'காரைக்கால் / தமிழக எல்லை', 'Puducherry / Tamil Nadu', 10.927200, 79.791100,
 'Saturday', 'சனிக்கிழமை',
 'World-renowned Saturn shrine where King Nala was released from the malefic grip of Saturn after bathing in the Nala Theertham. Propitiated for Sade Sati, Ashtama Shani, and chronic hurdles.',
 'உலகப் புகழ்பெற்ற சனி பரிகார ஸ்தலம். நள தமயந்தி புராணத்துடன் தொடர்புடையது. நள தீர்த்தத்தில் நீராடி எள்தீபம் ஏற்றுவதன் மூலம் ஏழரைச் சனி, அஷ்டமச் சனி மற்றும் வாத நோய்களின் தாக்கம் தணிகிறது.',
 'Holy dip in Nala Theertham, lighting black sesame oil lamps in clay pots, donating black sesame seeds and iron items on Saturdays.',
 'நள தீர்த்தத்தில் நீராடி, கருப்பு எள் தீபமேற்றி, நீல நிற வஸ்திரம் அல்லது எள் தானம் வழங்கி சனிக்கிழமைகளில் வழிபடுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_THIRUNAGESWARAM', 'rahu',
 'Thirunageswaram Naganathaswamy Temple', 'திருநாகேஸ்வரம் நாகநாதசுவாமி கோவில்',
 'Sri Naganathaswamy and Goddess Pirayanindasoodi', 'ஸ்ரீ நாகநாதசுவாமி - பிறையணிந்தசூடி அம்மன்',
 'Lord Rahu Bhagavan', 'ராகு பகவான்',
 'Thirunageswaram (near Kumbakonam)', 'திருநாகேஸ்வரம் (கும்பகோணம் அருகில்)',
 'Thanjavur', 'தஞ்சாவூர்', 'Tamil Nadu', 10.963300, 79.431700,
 'Sunday (or Rahu Kalam)', 'ஞாயிற்றுக்கிழமை (ராகு காலம்)',
 'Premier Rahu sthalam where Rahu Bhagavan worshipped Shiva. Famous for the miraculous milk abhishekam during Rahu Kalam, where milk poured on the idol visibly turns light blue.',
 'ராகு பகவானின் முதன்மைப் பரிகாரத் தலம். ராகு காலத்தில் ராகு பகவானுக்கு செய்யப்படும் பாலாபிஷேகத்தின் போது பால் நீல நிறமாக மாறும் அதிசயம் நிகழும் புண்ணிய பூமி. நாக தோஷம், காலசர்ப்ப தோஷ நிவர்த்தி தலம்.',
 'Milk Abhishekam during Rahu Kalam, offering urad dal, blue flowers, and lighting sesame oil lamps.',
 'ராகு காலத்தில் பாலாபிஷேகம் செய்தல், உளுந்து சமர்ப்பித்தல், நீல நிற மலர்கள் சாற்றி நல்லெண்ணெய் தீபம் ஏற்றுதல்.',
 'Kaveri Delta Navagraha Sthalam'),

('TEMPLE_KEEZHPERUMPALLAM', 'ketu',
 'Keezhperumpallam Naganathaswamy Temple', 'கீழ்ப்பெரும்பள்ளம் நாகநாதசுவாமி கோவில்',
 'Sri Naganathaswamy and Goddess Soundaranayaki', 'ஸ்ரீ நாகநாதசுவாமி - சௌந்தரநாயகி',
 'Lord Ketu Bhagavan', 'கேது பகவான்',
 'Keezhperumpallam (near Poompuhar)', 'கீழ்ப்பெரும்பள்ளம் (பூம்புகார் அருகில்)',
 'Mayiladuthurai', 'மயிலாடுதுறை', 'Tamil Nadu', 11.143600, 79.845600,
 'Tuesday', 'செவ்வாய்க்கிழமை',
 'Supreme Ketu sthalam where Ketu Bhagavan, having a human head and serpent body, worshipped Lord Shiva with folded hands for spiritual liberation and redemption.',
 'ஞானகாரகனான கேது பகவானின் பிரதான தலம். கேது பகவான் இங்கு மனித முகத்துடனும் பாம்பு உடலுடனும் சிவபெருமானை கைகூப்பி வணங்கும் கோலத்தில் அருள்பாலிக்கிறார். ஆன்மீக மேன்மை மற்றும் மோட்சம் அருளும் தலம்.',
 'Offering horsegram (kollu), multi-coloured cloth, red/spotted flowers, and performing circumambulation on Tuesdays.',
 'கொள்ளு தானம் செய்தல், பலவண்ண வஸ்திரம் சாற்றி, செவ்வரளி மாலை அணிவித்து செவ்வாய்க்கிழமை தோறும் வழிபடுதல்.',
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. Seed: Verified Remedies Catalog
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO public.remedies_catalog (
    code, graha, remedy_type, name_en, name_ta, description_en, description_ta,
    deity_en, deity_ta, sanskrit_text, transliteration_iast, transliteration_ta,
    meaning_en, meaning_ta, procedure_en, procedure_ta, japa_count,
    timing_recommendation_en, timing_recommendation_ta, is_pacification_only, problem_slugs
) VALUES
-- 1. Universal Ganesha Invocation
('REM_UNIV_GANESHA_01', 'universal', 'mantra',
 'Sri Ganesha Moola Mantra', 'ஸ்ரீ கணேச மூல மந்திரம்',
 'Foundational Vedic invocation chanted before initiating any astrological remedy or noble spiritual practice to remove obstacles.',
 'எந்த ஒரு ஜோதிடப் பரிகாரம் அல்லது சுப காரியத்தைத் தொடங்குவதற்கு முன் தடைகளை நீக்கி வெற்றி பெற உச்சரிக்க வேண்டிய முழுமுதற் கடவுள் கணபதியின் மூல மந்திரம்.',
 'Lord Ganesha', 'ஸ்ரீ விநாயகப் பெருமான்',
 'ॐ गं गणपतये नमः ॥', 'oṃ gaṃ gaṇapataye namaḥ ॥', 'ஓம் கம் கணபதயே நமஹ ॥',
 'Salutations to Lord Ganesha, the embodiment of wisdom, ruler of the celestial hosts, and the supreme remover of all hindrances.',
 'அனைத்து கணங்களுக்கும் தலைவரும், விக்கினங்களைத் தீர்ப்பவருமான விநாயகப் பெருமானைப் பணிந்து வணங்குகிறேன்.',
 'Sit facing North or East. Cleanse hands and chant 108 times using a Rudraksha or Sandalwood mala before starting any planetary remedies.',
 'வடக்கு அல்லது கிழக்கு நோக்கி அமர்ந்து, கைகளைச் சுத்தி செய்து, ருத்ராட்சம் அல்லது சந்தன மாலையைக் கொண்டு 108 முறை ஜபம் செய்யவும்.',
 108, 'Daily at dawn or before commencing any sacred endeavor', 'தினமும் விடியற்காலை அல்லது புதிய காரியங்களைத் தொடங்கும் முன்',
 FALSE, ARRAY['spiritual_stagnation', 'house_construction_hurdles', 'business_setbacks']),

-- 2. Universal Maha Mrityunjaya Healing
('REM_UNIV_MRITYUNJAYA_01', 'universal', 'mantra',
 'Maha Mrityunjaya Healing Mantra', 'மகா மிருத்யுஞ்சய மகா மந்திரம்',
 'Sacred Rigvedic healing prayer (Rigveda 7.59.12) dedicated to Lord Shiva as Tryambaka for freedom from severe health afflictions, accidents, and dread.',
 'ரிக்வேதத்தில் அருளப்பட்ட சிவபெருமானின் ஒப்புயர்வற்ற மகா மந்திரம். கொடிய நோய்கள், விபத்துகள் மற்றும் மரண பயத்தை நீக்கி நீண்ட ஆயுளையும் நலனையும் நல்கும்.',
 'Lord Shiva (Tryambaka)', 'சிவபெருமான் (முக்கண்ணன்)',
 'ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् । उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात् ॥',
 'oṃ tryambakaṃ yajāmahe sugandhiṃ puṣṭivardhanam | urvārukamiva bandhanānmṛtyormukṣīya māmṛtāt ॥',
 'ஓம் த்ரயம்பகம் யஜாமஹே ஸுகந்திம் புஷ்டிவர்த்தனம் । உர்வாருகமிவ பந்தனான்ம்ருத்யோர்முக்ஷீய மாம்ருதாத் ॥',
 'We worship the Three-Eyed Lord Shiva, who is fragrant and nourishes all beings. May He liberate us from death and disease towards immortality, as effortlessly as a ripe gourd is freed from its creeper.',
 'நறுமணமும், அனைவரையும் போஷிக்கும் ஆற்றலும் கொண்ட முக்கண்ணனான சிவனை வணங்குகிறோம். வெள்ளரிப் பழம் காம்பிலிருந்து விடுபடுவது போல, நம்மை நோய்கள் மற்றும் மரணப் பிடியிலிருந்து விடுவித்து அமிர்த வாழ்வை அருள்புரிவாராக.',
 'Recite 108 times daily facing North or East, preferably after morning bath. Can be chanted alongside medical treatment for recovery.',
 'காலை நீராடிய பின் வடக்கு அல்லது கிழக்கு நோக்கி அமர்ந்து தினமும் 108 முறை அமைதியான மனதுடன் ஜபம் செய்யவும்.',
 108, 'Daily at dawn during Brahma muhurta or dusk', 'தினமும் விடியற்காலை பிரம்ம முகூர்த்தம் அல்லது அந்தி மாலையில்',
 FALSE, ARRAY['chronic_health_issues', 'mental_anxiety_depression', 'vehicle_accidents_breakdowns', 'fear_negative_energies']),

-- 3. Sun (Surya) Namaha Mantra
('REM_SUN_MANTRA_01', 'sun', 'mantra',
 'Surya Namaha Mantra', 'சூரிய நமஹ மந்திரம்',
 'Classical Parashari mantra invoking Lord Surya for strengthening vitality, confidence, paternal bonds, and administrative authority.',
 'ஆற்றல், தன்னம்பிக்கை, தந்தை வழி நலம் மற்றும் அரசு/நிர்வாகத் துறை மேன்மைக்காக சூரிய பகவானைப் போற்றி உச்சரிக்கும் எளிய சாத்விக மந்திரம்.',
 'Lord Surya (Sun)', 'சூரிய பகவான்',
 'ॐ सूर्याय नमः ॥', 'oṃ sūryāya namaḥ ॥', 'ஓம் சூர்யாய நமஹ ॥',
 'Reverence to the radiant Sun God, the supreme cosmic witness and soul of the universe.',
 'அண்ட சராசரங்களின் ஆன்மாவாகவும், ஒளி வடிவாகவும் விளங்கும் சூரிய பகவானுக்கு எனது நமஸ்காரங்கள்.',
 'Offer clean water mixed with red flowers and a pinch of jaggery from a copper vessel towards the rising sun while reciting 108 times.',
 'செப்புப் பாத்திரத்தில் சுத்தமான தண்ணீருடன் செம்பருத்தி அல்லது செந்தாமரை இதழ்கள் சேர்த்து, காலை சூரியனை நோக்கி நின்றபடி 108 முறை ஜபம் செய்யவும்.',
 108, 'Sunday mornings during sunrise', 'ஞாயிற்றுக்கிழமை காலை சூரிய உதய வேளையில்',
 FALSE, ARRAY['career_delay', 'promotion_blocks', 'vitality_low_energy', 'eye_vision_ailments']),

-- 4. Sun (Surya) Charity (Daan) - FOR PACIFICATION ONLY
('REM_SUN_CHARITY_01', 'sun', 'charity',
 'Surya Daan (Wheat & Copper Charity)', 'சூரிய தானம் (கோதுமை மற்றும் செப்பு தானம்)',
 'Classical charity prescribed specifically when Sun acts as a functional malefic or afflicts health bhavas. NOT to be performed if Sun is a functional Yogakaraka.',
 'சூரியன் அசுப ஆதிபத்தியம் பெற்று உடல் நலப் பாதிப்புகளைத் தரும் போது மட்டும் செய்ய வேண்டிய பரிகார தானம். சூரியன் யோககாரகனாக இருக்கும் போது இந்த தானத்தைத் தவிர்க்க வேண்டும்.',
 'Lord Surya', 'சூரிய பகவான்',
 NULL, NULL, NULL,
 'Donating wheat grains, jaggery, or copper vessels on Sunday helps calm afflicted solar heat and dispels paternal friction.',
 'கோதுமை, வெல்லம் அல்லது செப்புப் பாத்திரங்களை ஏழை எளியவர்களுக்கு ஞாயிற்றுக்கிழமை தானமாக வழங்குவது சூரியனின் உக்கிரத்தைத் தணிக்கும்.',
 'Donate 1.25 kg of whole wheat grains and jaggery wrapped in red cloth to a needy student or temple kitchen on Sunday afternoon.',
 'ஞாயிற்றுக்கிழமை மதியம் 1.25 கிலோ முழு கோதுமை மற்றும் வெல்லத்தை சிவப்புத் துணியில் வைத்து ஏழை மாணவர்களுக்கோ அல்லது கோயில் அன்னதானத்திற்கோ வழங்கவும்.',
 NULL, 'Sunday afternoon between 12:00 PM and 1:30 PM', 'ஞாயிற்றுக்கிழமை நண்பகல் 12:00 முதல் 1:30 மணிக்குள்',
 TRUE, ARRAY['workplace_conflicts', 'chronic_health_issues', 'ancestral_karmic_blocks']),

-- 5. Moon (Chandra) Namaha Mantra
('REM_MOON_MANTRA_01', 'moon', 'mantra',
 'Chandra Namaha Mantra', 'சந்திர நமஹ மந்திரம்',
 'Traditional devotional prayer calming emotional turbulence, cooling anxiety, and healing mother-child relationships.',
 'மன அமைதி, நிம்மதியான உறக்கம், தாய்-சேய் நலம் மற்றும் உணர்ச்சி சமநிலையைப் பெற சந்திர பகவானைப் போற்றும் புனித மந்திரம்.',
 'Lord Chandra (Moon)', 'சந்திர பகவான்',
 'ॐ सोमाय नमः ॥', 'oṃ somāya namaḥ ॥', 'ஓம் ஸோமாய நமஹ ॥',
 'Salutations to Lord Soma (the Moon), the reservoir of nectar and guardian of the mind and emotions.',
 'அமிர்தத்தின் இருப்பிடமாகவும், மனோகாரகனாகவும் விளங்கும் சந்திர பகவானுக்கு எனது வணக்கங்கள்.',
 'Chant 108 times on Monday evening after moonrise facing North or North-West with serene focus.',
 'திங்கட்கிழமை மாலை சந்திரன் உதித்த பின் வடக்கு அல்லது வடமேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.',
 108, 'Monday evenings after moonrise', 'திங்கட்கிழமை மாலை சந்திர தரிசனத்திற்குப் பின்',
 FALSE, ARRAY['mental_anxiety_depression', 'marital_discord', 'recurrent_nightmares', 'relocation_adjustment_stress']),

-- 6. Mars (Mangal) Namaha Mantra
('REM_MARS_MANTRA_01', 'mars', 'mantra',
 'Mangal Namaha Mantra', 'செவ்வாய் நமஹ மந்திரம்',
 'Parashari prayer invoking Mars for courage, blood vitality, resolving land property hurdles, and mitigating Kuja dosha friction.',
 'தைரியம், நிலம் சார்ந்த சொத்து நன்மைகள், ரத்த நலம் மற்றும் செவ்வாய் தோஷ அமைதிக்காக அங்காரகனைப் போற்றும் மந்திரம்.',
 'Lord Mangal (Mars / Murugan)', 'செவ்வாய் பகவான் / முருகப் பெருமான்',
 'ॐ भौमाय नमः ॥', 'oṃ bhaumāya namaḥ ॥', 'ஓம் பௌமாய நமஹ ॥',
 'Salutations to Mars, the son of the Earth, the granter of vigor, resilience, and victorious valor.',
 'பூமிதேவியின் மைந்தனும், அளப்பரிய வீரமும் பலமும் அருள்பவருமான அங்காரக பகவானைப் பணிகிறேன்.',
 'Sit on a red mat facing South or East on Tuesday morning. Light a ghee lamp and chant 108 times.',
 'செவ்வாய்க்கிழமை காலை தெற்கு அல்லது கிழக்கு நோக்கி சிவப்பு விரிப்பில் அமர்ந்து நெய் தீபமேற்றி 108 முறை ஜபம் செய்யவும்.',
 108, 'Tuesday mornings', 'செவ்வாய்க்கிழமை காலை வேளையில்',
 FALSE, ARRAY['land_property_disputes', 'house_construction_hurdles', 'marriage_delay', 'vitality_low_energy']),

-- 7. Mercury (Budha) Namaha Mantra
('REM_MERCURY_MANTRA_01', 'mercury', 'mantra',
 'Budha Namaha Mantra', 'புதன் நமஹ மந்திரம்',
 'Classical prayer for intellectual acuity, commercial success, speech eloquence, and nervous balance.',
 'கல்வித் தேர்ச்சி, நினைவாற்றல், வாக்கு வன்மை, வியாபார வளர்ச்சி மற்றும் புத்தி கூர்மைக்குரிய புதன் பகவான் மந்திரம்.',
 'Lord Budha (Mercury / Vishnu)', 'புதன் பகவான் / விஷ்ணு பெருமான்',
 'ॐ बुधाय नमः ॥', 'oṃ budhāya namaḥ ॥', 'ஓம் புதாய நமஹ ॥',
 'Reverence to Lord Budha, the presiding lord of intelligence, discrimination, trade, and learning.',
 'ஞானம், விவேகம் மற்றும் வர்த்தகத்தின் அதிபதியாகத் திகழும் புதன் பகவானுக்கு எனது நமஸ்காரங்கள்.',
 'Chant 108 times on Wednesday morning facing North. Offering tulasi leaves to Lord Vishnu enhances auspicious results.',
 'புதன்கிழமை காலை வடக்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும். பெருமாளுக்குத் துளசி சமர்ப்பித்து வழிபடுவது கூடுதல் நற்பலன் தரும்.',
 108, 'Wednesday mornings', 'புதன்கிழமை காலை வேளையில்',
 FALSE, ARRAY['academic_focus_memory', 'business_setbacks', 'speech_communication_blocks', 'exam_competitive_hurdles']),

-- 8. Jupiter (Guru) Namaha Mantra
('REM_JUPITER_MANTRA_01', 'jupiter', 'mantra',
 'Guru Namaha Mantra', 'குரு நமஹ மந்திரம்',
 'Sacred invocation of Brihaspati for wisdom, progeny blessings, marital happiness, and divine grace.',
 'ஞானம், குருவருள், சுப காரிய வெற்றி, புத்திர பாக்கியம் மற்றும் திருமண யோகத்திற்குரிய குரு பகவான் போற்றி.',
 'Lord Brihaspati (Jupiter / Dakshinamurthy)', 'குரு பகவான் / தட்சிணாமூர்த்தி',
 'ॐ बृहस्पतये नमः ॥', 'oṃ bṛhaspataye namaḥ ॥', 'ஓம் பிருஹஸ்பதயே நமஹ ॥',
 'Salutations to Brihaspati, the preceptor of the Gods, master of Vedic scriptures, and embodiment of grace.',
 'தேவர்களின் குருவும், சகல சாஸ்திர ஞானங்களின் இருப்பிடமுமான பிரகஸ்பதி பகவானைப் பணிகிறேன்.',
 'Chant 108 times on Thursday morning wearing yellow or clean white attire facing North-East.',
 'வியாழக்கிழமை காலை வடகிழக்கு நோக்கி அமர்ந்து மஞ்சள் அல்லது வெண்ணிற ஆடை அணிந்து 108 முறை ஜபம் செய்யவும்.',
 108, 'Thursday mornings during sunrise', 'வியாழக்கிழமை அதிகாலை',
 FALSE, ARRAY['progeny_childbirth_delay', 'higher_education_obstacles', 'financial_instability', 'marriage_delay']),

-- 9. Venus (Shukra) Namaha Mantra
('REM_VENUS_MANTRA_01', 'venus', 'mantra',
 'Shukra Namaha Mantra', 'சுக்கிர நமஹ மந்திரம்',
 'Classical prayer harmonizing relationships, attracting material comforts, artistic fulfillment, and marital joy.',
 'களத்திர தோஷ நிவர்த்தி, தாம்பத்திய அன்யோன்யம், கலைத் திறன் மற்றும் சகல ஐஸ்வர்யங்களுக்கும் உரிய சுக்கிர மந்திரம்.',
 'Lord Shukra (Venus / Mahalakshmi)', 'சுக்கிர பகவான் / மகாலட்சுமி',
 'ॐ शुक्राय नमः ॥', 'oṃ śukrāya namaḥ ॥', 'ஓம் சுக்ராய நமஹ ॥',
 'Reverence to Shukracharya, the brilliant master of aesthetic beauty, harmony, and material opulence.',
 'சகல கலைகளின் வித்தகரும், இன்பம் மற்றும் அழகின் நாயகருமான சுக்கிர பகவானுக்கு எனது நமஸ்காரங்கள்.',
 'Chant 108 times on Friday evening or morning facing East or South-East after a clean bath.',
 'வெள்ளிக்கிழமை காலை அல்லது அந்தி மாலையில் கிழக்கு நோக்கி அமர்ந்து மன அமைதியுடன் 108 முறை ஜபம் செய்யவும்.',
 108, 'Friday mornings or twilight', 'வெள்ளிக்கிழமை காலை அல்லது அந்தி மாலை',
 FALSE, ARRAY['marital_discord', 'relationship_breakdown', 'wealth_accumulation_block', 'marriage_delay']),

-- 10. Saturn (Shani) Namaha Mantra
('REM_SATURN_MANTRA_01', 'saturn', 'mantra',
 'Shani Namaha Mantra', 'சனி நமஹ மந்திரம்',
 'Vedic prayer invoking Saturn for humility, patient perseverance, relief from Sade Sati distress, and longevity.',
 'ஏழரைச் சனி, அஷ்டமச் சனி ஆகியவற்றின் பாதிப்புகளைத் தணித்து, பொறுமை, நீதி மற்றும் நீண்ட ஆயுளை அருளும் சனி பகவான் மந்திரம்.',
 'Lord Shani (Saturn)', 'சனீஸ்வர பகவான்',
 'ॐ शनैश्चराय नमः ॥', 'oṃ śanaiścarāya namaḥ ॥', 'ஓம் சனைச்சராய நமஹ ॥',
 'Salutations to the slow-moving Lord Shani, the dispenser of karmic justice and guardian of discipline and truth.',
 'நீதியின் பாற்பட்டு கர்ம வினைகளுக்கு ஏற்ப பலன்களை அருளும் சனீஸ்வர பகவானைப் பணிந்து வணங்குகிறேன்.',
 'Recite 108 times on Saturday evening facing West. Lighting a sesame oil lamp under a peepal tree or at home is recommended.',
 'சனிக்கிழமை மாலை மேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும். நல்லெண்ணெய் தீபமேற்றி வழிபடுவது நலம் பயக்கும்.',
 108, 'Saturday evenings after sunset', 'சனிக்கிழமை மாலை சூரிய அஸ்தமனத்திற்குப் பின்',
 FALSE, ARRAY['career_delay', 'chronic_debt_burden', 'litigation_court_cases', 'bone_joint_mobility']),

-- 11. Saturn (Shani) Charity (Daan) - FOR PACIFICATION ONLY
('REM_SATURN_CHARITY_01', 'saturn', 'charity',
 'Shani Daan (Black Sesame & Blanket Charity)', 'சனி தானம் (கருப்பு எள் மற்றும் அன்னதானம்)',
 'Strictly for pacifying malefic Saturn when afflicting dusthanas. Never prescribe for Taurus/Libra where Saturn is Yogakaraka.',
 'சனி பகவான் அசுப ஆதிபத்தியம் பெற்று துன்பம் தரும் போது மட்டும் செய்ய வேண்டிய பரிகார தானம். ரிஷபம்/துலாம் யோககாரகர்களுக்கு இத்தானம் பொருந்தாது.',
 'Lord Shani', 'சனீஸ்வர பகவான்',
 NULL, NULL, NULL,
 'Donating black sesame seeds, mustard oil, or warm dark blankets to elderly, disabled, or needy workers on Saturday.',
 'கருப்பு எள், நல்லெண்ணெய், கருப்பு வஸ்திரம் அல்லது போர்வைகளை முதியோர் மற்றும் மாற்றுத்திறனாளிகளுக்கு வழங்குதல்.',
 'Distribute sesame-mixed cooked rice or warm blankets to poor laborers or elderly destitute persons on Saturday afternoon.',
 'சனிக்கிழமை மதியம் ஏழை எளிய தொழிலாளர்கள் அல்லது முதியவர்களுக்கு எள் கலந்த உணவு அல்லது போர்வை தானம் செய்யவும்.',
 NULL, 'Saturday afternoons', 'சனிக்கிழமை நண்பகல் வேளையில்',
 TRUE, ARRAY['chronic_debt_burden', 'litigation_court_cases', 'past_life_karmic_burdens']),

-- 12. Rahu Namaha Mantra
('REM_RAHU_MANTRA_01', 'rahu', 'mantra',
 'Rahu Namaha Mantra', 'ராகு நமஹ மந்திரம்',
 'Protective mantra pacifying psychological illusion, addictions, unexpected shocks, and Rahu dasha turbulence.',
 'மாயை, பிரமைகள், திடீர் தடைகள், விஷ பயம் மற்றும் ராகு தசை-புத்திகளின் கெடுபலன்களைத் தணிக்கும் சாந்தி மந்திரம்.',
 'Lord Rahu (Goddess Durga)', 'ராகு பகவான் / துர்க்கை அம்மன்',
 'ॐ राहवे नमः ॥', 'oṃ rāhave namaḥ ॥', 'ஓம் ராகவே நமஹ ॥',
 'Salutations to Lord Rahu, who tests the soul through worldly illusion and grants deep spiritual insight upon pacification.',
 'உலகியல் மாயைகளை விலக்கி, துர்க்கையின் அருளால் தெளிந்த ஞானத்தை நல்கும் ராகு பகவானை வணங்குகிறேன்.',
 'Chant 108 times on Saturday or during Rahu Kalam on Tuesday/Friday facing South-West.',
 'செவ்வாய் அல்லது வெள்ளிக்கிழமை ராகு காலத்தில் அல்லது சனிக்கிழமை மாலை தென்மேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.',
 108, 'Rahu Kalam or Saturday twilight', 'ராகு காலம் அல்லது சனிக்கிழமை அந்தி வேளை',
 FALSE, ARRAY['fear_negative_energies', 'job_loss_instability', 'speculation_gambling_losses', 'visa_immigration_delays']),

-- 13. Ketu Namaha Mantra
('REM_KETU_MANTRA_01', 'ketu', 'mantra',
 'Ketu Namaha Mantra', 'கேது நமஹ மந்திரம்',
 'Spiritual prayer invoking Ketu for detachment from past burdens, inner liberation (Moksha), and occult wisdom.',
 'மோட்ச காரகனான கேது பகவானின் அருளைப் பெற்று, பூர்வ ஜென்ம வினைகளைத் தீர்த்து, ஆன்மீக ஞானம் பெற உதவும் மந்திரம்.',
 'Lord Ketu (Lord Ganesha)', 'கேது பகவான் / விநாயகப் பெருமான்',
 'ॐ केतवे नमः ॥', 'oṃ ketave namaḥ ॥', 'ஓம் கேதவே நமஹ ॥',
 'Reverence to Lord Ketu, the flag of spiritual detachment, dispeller of illusions, and bestower of ultimate liberation.',
 'பற்றற்ற நிலையை அருளி, உலகப் பிணிகளிலிருந்து ஆன்மாவை விடுவித்து முக்தி அளிக்கும் கேது பகவானுக்கு நமஸ்காரங்கள்.',
 'Chant 108 times on Tuesday morning facing North-East after offering Durva grass to Lord Ganesha.',
 'செவ்வாய்க்கிழமை காலை விநாயகருக்கு அருகம்புல் சமர்ப்பித்த பின் வடகிழக்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.',
 108, 'Tuesday mornings at dawn', 'செவ்வாய்க்கிழமை விடியற்காலை',
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
