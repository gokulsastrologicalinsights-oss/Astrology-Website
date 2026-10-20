-- ==============================================================================
-- Gokul's Astrological Insights - Staging Post-Migration Verification Suite
-- Target Project: pcwiopxewlxhwvddpndq
-- Description: Read-only verification queries to validate schema objects, seed data,
--              RLS policies, indexes, and existing data integrity.
-- ==============================================================================

-- 1. Verify Presence of All Seven Required Tables
SELECT 
    table_name,
    CASE 
        WHEN table_name IN (
            'customers', 'customer_birthday_wishes', 'remedy_source_references',
            'remedies_problem_taxonomy', 'remedies_catalog', 'navagraha_temples', 'remedy_reports'
        ) THEN 'VERIFIED'
        ELSE 'OTHER'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'customers', 'customer_birthday_wishes', 'remedy_source_references',
    'remedies_problem_taxonomy', 'remedies_catalog', 'navagraha_temples', 'remedy_reports'
  )
ORDER BY table_name;
-- EXPECTED: 7 rows returned with status 'VERIFIED'.

-- 2. Verify Knowledge Base Seed Row Counts
SELECT 'remedy_source_references' AS table_name, count(*) AS actual_count, 7 AS expected_count FROM public.remedy_source_references
UNION ALL
SELECT 'remedies_problem_taxonomy', count(*), 39 FROM public.remedies_problem_taxonomy
UNION ALL
SELECT 'navagraha_temples', count(*), 9 FROM public.navagraha_temples
UNION ALL
SELECT 'remedies_catalog', count(*), 31 FROM public.remedies_catalog;
-- EXPECTED:
-- remedy_source_references: 7
-- remedies_problem_taxonomy: 39
-- navagraha_temples: 9
-- remedies_catalog: 31 (>= 30 verified classical remedies)

-- 3. Verify Row-Level Security (RLS) is Enabled on All 7 Tables
SELECT 
    c.relname AS table_name,
    c.relrowsecurity AS rls_enabled,
    c.relforcerowsecurity AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN (
    'customers', 'customer_birthday_wishes', 'remedy_source_references',
    'remedies_problem_taxonomy', 'remedies_catalog', 'navagraha_temples', 'remedy_reports'
  )
ORDER BY c.relname;
-- EXPECTED: 7 rows, all with rls_enabled = true.

-- 4. Verify RLS Policies are Defined
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN (
    'customers', 'customer_birthday_wishes', 'remedy_source_references',
    'remedies_problem_taxonomy', 'remedies_catalog', 'navagraha_temples', 'remedy_reports'
  )
ORDER BY tablename, policyname;
-- EXPECTED: Active policies for SELECT, INSERT, UPDATE, DELETE matching tenant isolation boundaries.

-- 5. Verify Customer Phone Column Nullability (Optional Phone Feature)
SELECT 
    column_name,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'customers'
  AND column_name IN ('phone_number', 'normalized_phone', 'whatsapp_number');
-- EXPECTED: All 3 columns return is_nullable = 'YES'.

-- 6. Verify Customer Partial Unique Index
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'customers'
  AND indexname = 'uq_customers_user_normalized_phone';
-- EXPECTED: Contains WHERE normalized_phone IS NOT NULL AND normalized_phone <> ''.

-- 7. Verify Saved Horoscopes Linking Column & Data Preservation
SELECT 
    count(*) AS total_saved_horoscopes,
    count(customer_id) AS horoscopes_with_customer_link
FROM public.saved_horoscopes;
-- EXPECTED: total_saved_horoscopes >= 12 (existing horoscopes untouched; 0 data lost).

-- 8. Verify Foreign Key Constraints
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND tc.table_name IN ('customers', 'customer_birthday_wishes', 'remedies_catalog', 'remedy_reports', 'saved_horoscopes')
ORDER BY tc.table_name;
