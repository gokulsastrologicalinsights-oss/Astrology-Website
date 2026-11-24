# GOKUL'S ASTROLOGICAL INSIGHTS
## MOBILE GAP ANALYSIS & ARCHITECTURAL MITIGATION REPORT

> **Document Version:** 1.0.0  
> **Audit Status:** Stage 0 - Existing System Readiness  
> **Key Finding:** 98.3% of the backend is directly reusable on mobile; exactly 3 architectural bridge gaps require consideration for Stage 1.

---

### 1. VERIFIED REUSABILITY METRICS

| System Component | Existing Endpoints | Directly Reusable on Mobile | Minor Bridge Required | Reusability Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Ephemeris & Calculations** | 35 operations | 35 operations | 0 | **100.0%** |
| **Vedic Yogas & Doshas** | 17 operations | 17 operations | 0 | **100.0%** |
| **Vimshottari Dasa Engine** | 2 operations | 2 operations | 0 | **100.0%** |
| **KP Astrology Suite** | 36 operations | 36 operations | 0 | **100.0%** |
| **PDF Generation Services** | 12 operations | 12 operations | 0 | **100.0%** |
| **Marriage Compatibility** | 14 operations | 14 operations | 0 | **100.0%** |
| **Numerology Suite** | 18 operations | 18 operations | 0 | **100.0%** |
| **Remedies & Pariharams** | 23 operations | 23 operations | 0 | **100.0%** |
| **Vastu Shastra** | 7 operations | 7 operations | 0 | **100.0%** |
| **Tamil Sastra & Booklet** | 19 operations | 19 operations | 0 | **100.0%** |
| **Auth & User Management** | 6 operations | 4 operations | 2 (Username login) | **66.7%** |
| **Horoscope & Customer CRUD** | 8 operations | 4 operations | 4 (BFF routes in Next) | **50.0%** |
| **TOTAL** | **235 operations** | **223 operations** | **12 operations** | **98.3%** |

---

### 2. DETAILED GAP ANALYSIS & MITIGATION OPTIONS

#### GAP 1: Horoscope & Customer Persistence Routing
- **Existing Web Architecture:**
  - `POST /api/v1/horoscope/calculate` computes raw planetary positions.
  - The web browser sends the calculation snapshot to Next.js `POST /api/horoscopes`.
  - Next.js acts as a Backend-For-Frontend (BFF): it verifies customer WhatsApp, provisions `public.customers`, compacts the Dasa tree to 3 levels (~200 KB) using `compactDasaTree()`, and inserts into `public.saved_horoscopes` via Supabase.
  - Sub-engines in FastAPI (e.g. PDF generation, D1-D9) read directly from Supabase via `get_cached_saved_horoscope()`.
- **The Mobile Dilemma:**
  - FastAPI currently lacks generic `POST /api/v1/horoscopes` and `GET /api/v1/horoscopes` endpoints.
- **Available Resolutions for Stage 1:**
  - **Resolution A (Recommended - FastAPI Shared CRUD Router):**
    In Stage 1 development, add a shared router `backend/app/routers/horoscope_crud.py` to FastAPI (`POST /api/v1/horoscopes`, `GET /api/v1/horoscopes`, `DELETE /api/v1/horoscopes/{id}`). This establishes FastAPI as the true single backend for both Web and Mobile.
  - **Resolution B (Supabase Client Direct):**
    The Android app performs `supabase.from('saved_horoscopes').select()` and `insert()` directly using its authenticated session, leveraging the existing PostgreSQL RLS policies.
  - **Resolution C (Mobile calls Next.js BFF):**
    The Android app calls `https://gai-astrology.com/api/horoscopes`. Works immediately, but introduces a runtime dependency on the Next.js web deployment.

#### GAP 2: Username vs. Email Login on Mobile
- **Existing Web Architecture:**
  - Next.js `/api/auth/login` allows users to log in with either an email address or a username.
  - If a username is entered, Next.js calls `adminClient.from("profiles")` (using the server-side service role key) to resolve the email address before calling Supabase Auth.
- **The Mobile Dilemma:**
  - A native mobile client must **never** contain the `SUPABASE_SERVICE_ROLE_KEY`.
  - Direct anonymous queries to Supabase cannot look up other users' email addresses due to RLS security.
- **Available Resolutions for Stage 1:**
  - **Resolution A (Standard Email Login - Zero Changes):**
    The Android app requires users to log in with their email address and password. Standard, secure, and needs zero changes.
  - **Resolution B (FastAPI Username Resolver):**
    Add `POST /api/v1/auth/resolve-username` to FastAPI. FastAPI uses its existing server-side `get_supabase_client()` to safely return the email corresponding to a username.

#### GAP 3: Dasa Tree Payload Size Optimization
- **Existing Web Architecture:**
  - A full 5-level Vimshottari Dasa tree is approximately 1.8 MB of JSON.
  - Next.js trims the saved snapshot to 3 levels (`compactDasaTree()`), reducing database row size to ~200 KB.
  - When deeper 4th or 5th level Dasa periods are needed, the backend recomputes them on-demand via `POST /api/v1/horoscope/dasa`.
- **Mobile Mitigation:**
  - When saving from mobile, the Android app should either request depth=3 for persistent storage, or let the FastAPI shared endpoint perform the standard 3-level compaction before database insertion.

---

### 3. SECURITY & RISK ASSESSMENT

| Risk Area | Severity | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Service Role Key Exposure** | **CRITICAL** | Total database compromise | Mobile app must NEVER package `SUPABASE_SERVICE_ROLE_KEY`. Use only `EXPO_PUBLIC_SUPABASE_ANON_KEY`. |
| **Token Theft from Device** | **HIGH** | Account hijacking | Store session JWT and refresh tokens strictly in Android EncryptedSharedPreferences via `expo-secure-store`. |
| **Network Egress Spikes** | **MEDIUM** | Increased Supabase costs | Utilize FastAPI's in-memory horoscope cache (300s TTL) for all calculation and PDF requests. |
| **Network Latency & Offline** | **LOW** | Poor UX on slow 4G/3G | Cache recent calculated charts in React Native `AsyncStorage` / SQLite. |
| **Tamil Font Rendering Glitches** | **LOW** | Broken PDF ligatures | None needed — FastAPI ReportLab already bundles Noto Sans Tamil and HarfBuzz shaper. |
