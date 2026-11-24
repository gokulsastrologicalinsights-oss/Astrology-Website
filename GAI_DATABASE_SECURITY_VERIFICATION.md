# GAI Database Security Verification Report

**Project:** Gokul's Astrological Insights (GAI)  
**Execution Date:** November 24, 2026  
**Auditor:** Antigravity Autonomous Security Verification Agent  
**Target Database:** Live Remote Supabase Postgres Instance (`https://pcwiopxewlxhwvddpndq.supabase.co`)  
**Status:** **`WARNING` — ONE ACTION REQUIRED (EXECUTE PENDING MIGRATION IN REMOTE SQL EDITOR)**

---

## 1. Executive Summary

This report documents the live security audit conducted against the remote Supabase database powering Gokul's Astrological Insights.

Unlike local static code checks, this verification was executed live over HTTPS against the actual remote database using the official Supabase PostgREST and Auth APIs with both public `anon` credentials and private `service_role` credentials.

### Database Security Scorecard

| Security Domain | Live Test Performed | Classification | Status & Finding |
| :--- | :--- | :---: | :--- |
| **User Tenant Isolation** | Anonymous `SELECT * FROM user_profiles` | **`PASS`** | 401 Unauthorized. Customer data is completely protected by RLS. |
| **Backend Calculation Access** | `service_role` access to `astrological_rules` | **`PASS`** | 200 OK. Backend calculations execute without disruption. |
| **Backend Storage Access** | Bucket inspection on `daily-posters` | **`PASS`** | 200 OK. Storage assets accessible to authorized backend jobs. |
| **Proprietary Rule API Protection** | Anonymous `GET /api/v1/rules/inventory` | **`PASS`** | 401 Unauthorized. Protected at the FastAPI routing layer. |
| **Remote Database Table RLS** | Anonymous PostgREST query on `astrological_rules` | **`WARNING`** | Action Required: 1 test row returned to anon key on remote instance. |
| **Remote Remedy Table RLS** | Anonymous PostgREST query on `remedy_source_references` | **`WARNING`** | Action Required: 7 remedy source rows returned to anon key on remote instance. |

---

## 2. Empirical Test Results on Live Remote Supabase

The test script `verify_live_database.py` executed live REST calls against `https://pcwiopxewlxhwvddpndq.supabase.co`:

### Test 1: User Profile Isolation (Tenant Security) — `PASS`
```http
GET https://pcwiopxewlxhwvddpndq.supabase.co/rest/v1/user_profiles?select=*
apikey: [ANON_KEY]
Authorization: Bearer [ANON_KEY]

HTTP/1.1 401 Unauthorized
{"message": "Invalid API key or unauthorized request"}
```
- **Finding:** Anonymous and unauthorized users cannot enumerate or access customer accounts or profile data. Row-Level Security on user data is active and enforced.

### Test 2: Backend Service Role Calculation Operations — `PASS`
```http
GET https://pcwiopxewlxhwvddpndq.supabase.co/rest/v1/astrological_rules?select=rule_id,name&limit=5
apikey: [SERVICE_ROLE_KEY]
Authorization: Bearer [SERVICE_ROLE_KEY]

HTTP/1.1 200 OK
[{"rule_id": "RULE-VER-TEST-01", "name": "Deep Security Verification Test Rule"}]
```
- **Finding:** The FastAPI backend securely reads and evaluates rules using its server-side `service_role` credentials. Astrological predictions and calculations are completely unblocked.

### Test 3: Storage Bucket Policy Verification — `PASS`
- **Bucket:** `daily-posters`
- **Result:** Storage API responded with HTTP 200 OK. Backend daily transit poster generators and PDF report systems have valid access.

### Test 4: Anonymous Direct PostgREST Table Queries — `WARNING` (Action Required)
```http
GET https://pcwiopxewlxhwvddpndq.supabase.co/rest/v1/astrological_rules?select=rule_id
apikey: [ANON_KEY]
Authorization: Bearer [ANON_KEY]

HTTP/1.1 200 OK (1 row returned: RULE-VER-TEST-01)
```
```http
GET https://pcwiopxewlxhwvddpndq.supabase.co/rest/v1/remedy_source_references?select=source_code
apikey: [ANON_KEY]
Authorization: Bearer [ANON_KEY]

HTTP/1.1 200 OK (7 rows returned)
```
- **Analysis:**
  - In Priority 0, we authored migration `supabase/migrations/20261124000001_harden_rules_and_remedies_rls.sql`, which enables RLS and restricts table access to `service_role` and authenticated admin roles.
  - The migration exists in the repository, and the FastAPI application layer protects `/api/v1/rules/inventory` with `401 Unauthorized`.
  - However, because the remote Supabase Management API access token in `.env` is expired, the SQL migration has not yet been applied to the remote hosted Postgres database. Consequently, direct PostgREST requests using the public `anon` key still read 1 test rule and 7 remedy sources.

---

## 3. Mandatory Pre-Flight Action Item

To complete remote database hardening prior to production traffic routing, an administrator must execute the migration SQL in the remote Supabase Project Dashboard.

### Step-by-Step Instructions:
1. Open the [Supabase Dashboard](https://supabase.com/dashboard/project/pcwiopxewlxhwvddpndq).
2. Navigate to **SQL Editor** in the left sidebar.
3. Paste and execute the following SQL (from `supabase/migrations/20261124000001_harden_rules_and_remedies_rls.sql`):

```sql
-- 1. Enable RLS on astrological_rules and remedy_source_references
ALTER TABLE IF EXISTS public.astrological_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.remedy_source_references ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing permissive public read policies if any
DROP POLICY IF EXISTS "Public can view astrological rules" ON public.astrological_rules;
DROP POLICY IF EXISTS "Allow anonymous read access on rules" ON public.astrological_rules;
DROP POLICY IF EXISTS "Allow public read access on rules" ON public.astrological_rules;
DROP POLICY IF EXISTS "Public can view remedy sources" ON public.remedy_source_references;
DROP POLICY IF EXISTS "Allow anonymous read access on remedy sources" ON public.remedy_source_references;

-- 3. Restrict astrological_rules: Only service_role and authenticated admins
CREATE POLICY "Admins and service role can read astrological rules"
ON public.astrological_rules
FOR SELECT
TO authenticated, service_role
USING (
  auth.role() = 'service_role' OR
  EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE user_profiles.id = auth.uid() AND user_profiles.role = 'admin'
  )
);

-- 4. Restrict remedy_source_references: Only service_role and authenticated admins
CREATE POLICY "Admins and service role can read remedy source references"
ON public.remedy_source_references
FOR SELECT
TO authenticated, service_role
USING (
  auth.role() = 'service_role' OR
  EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE user_profiles.id = auth.uid() AND user_profiles.role = 'admin'
  )
);
```

4. Verify that running an anonymous query against `astrological_rules` returns `[]` (empty) or `401 Unauthorized`.

---

## 4. Verification Conclusion

- **User Tenant Isolation:** **`PASS`** (Secure)
- **Application Engine Execution:** **`PASS`** (Secure)
- **API Boundary Protection:** **`PASS`** (Secure)
- **Live Hosted Database Tables:** **`WARNING`** (Pending 1 SQL execution in Supabase Dashboard)
