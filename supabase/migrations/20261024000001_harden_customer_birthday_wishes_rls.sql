-- Gokul's Astrological Insights - Database Security Hardening
-- Migration: 20261024000001_harden_customer_birthday_wishes_rls.sql
-- Description: Strengthens customer_birthday_wishes Row-Level Security (RLS) to enforce strict tenant isolation via customer ownership.

-- 1. Drop overly broad authenticated-only policies
DROP POLICY IF EXISTS "wishes_select_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_insert_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_update_policy" ON public.customer_birthday_wishes;
DROP POLICY IF EXISTS "wishes_delete_policy" ON public.customer_birthday_wishes;

-- 2. Create customer-ownership verified RLS policies
-- SELECT: Users can only view birthday wishes for customers they own (or admins)
CREATE POLICY "wishes_select_policy" ON public.customer_birthday_wishes
FOR SELECT USING (
    (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM public.customers c WHERE c.id = customer_id AND c.user_id = auth.uid()
    )) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- INSERT: Users can only record birthday wishes for customers they own (or admins)
CREATE POLICY "wishes_insert_policy" ON public.customer_birthday_wishes
FOR INSERT WITH CHECK (
    (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM public.customers c WHERE c.id = customer_id AND c.user_id = auth.uid()
    )) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- UPDATE: Users can only update birthday wishes for customers they own (or admins)
CREATE POLICY "wishes_update_policy" ON public.customer_birthday_wishes
FOR UPDATE USING (
    (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM public.customers c WHERE c.id = customer_id AND c.user_id = auth.uid()
    )) OR
    (auth.role() = 'authenticated' AND public.is_admin())
) WITH CHECK (
    (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM public.customers c WHERE c.id = customer_id AND c.user_id = auth.uid()
    )) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);

-- DELETE: Users can only delete birthday wishes for customers they own (or admins)
CREATE POLICY "wishes_delete_policy" ON public.customer_birthday_wishes
FOR DELETE USING (
    (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM public.customers c WHERE c.id = customer_id AND c.user_id = auth.uid()
    )) OR
    (auth.role() = 'authenticated' AND public.is_admin())
);
