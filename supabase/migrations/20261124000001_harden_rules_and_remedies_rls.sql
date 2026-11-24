-- Migration: 20261124000001_harden_rules_and_remedies_rls.sql
-- Description: Hardens Row-Level Security on proprietary astrological rules and remedy source references.
--              1. Revokes direct public/anon access to public.astrological_rules
--              2. Restricts public.astrological_rules SELECT strictly to administrators (public.is_admin())
--              3. Revokes direct public/anon access to public.remedy_source_references
--              4. Restricts public.remedy_source_references SELECT strictly to administrators (public.is_admin())
--              5. Grants necessary access to service_role so trusted backend execution continues seamlessly.

-- 1. Harden public.astrological_rules
ALTER TABLE public.astrological_rules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "rules_read_policy" ON public.astrological_rules;
DROP POLICY IF EXISTS "rules_admin_select_policy" ON public.astrological_rules;

CREATE POLICY "rules_admin_select_policy" ON public.astrological_rules
    FOR SELECT USING (public.is_admin());

-- Revoke dangerous anon and authenticated table-level grants
REVOKE ALL ON TABLE public.astrological_rules FROM anon;
REVOKE ALL ON TABLE public.astrological_rules FROM authenticated;

-- Ensure service_role has full access for backend server execution
GRANT ALL ON TABLE public.astrological_rules TO service_role;


-- 2. Harden public.remedy_source_references
ALTER TABLE public.remedy_source_references ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "remedy_sources_select" ON public.remedy_source_references;
DROP POLICY IF EXISTS "remedy_sources_admin_select" ON public.remedy_source_references;

CREATE POLICY "remedy_sources_admin_select" ON public.remedy_source_references
    FOR SELECT USING (public.is_admin());

-- Revoke dangerous anon and authenticated table-level grants
REVOKE ALL ON TABLE public.remedy_source_references FROM anon;
REVOKE ALL ON TABLE public.remedy_source_references FROM authenticated;

-- Ensure service_role has full access for backend server execution
GRANT ALL ON TABLE public.remedy_source_references TO service_role;
