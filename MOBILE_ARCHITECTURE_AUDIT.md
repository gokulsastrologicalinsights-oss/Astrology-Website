# GOKUL'S ASTROLOGICAL INSIGHTS
## MOBILE ARCHITECTURE AUDIT & DUAL-CLIENT SYSTEM SPECIFICATION

> **Document Version:** 1.0.0  
> **Date:** November 2026  
> **Status:** Stage 0 - Architecture & Mobile Readiness Audit  
> **Target Framework:** React Native + Expo (Android) & Next.js 16 (Web)  
> **Shared Core:** Python FastAPI Backend & Supabase PostgreSQL Database

---

### 1. EXECUTIVE ARCHITECTURE OVERVIEW

Gokul's Astrological Insights (GAI) is a deterministic, rule-based Vedic and Krishnamurti Padhdhati (KP) astrology platform. The system operates strictly without LLMs or conversational AI, relying on astronomical mathematics and classical textual algorithms.

The current production system exists as a full-stack mono-repository consisting of:
1. **Frontend:** Next.js 16.4.2 (React 19.3.0, TypeScript 5, Tailwind CSS 4) hosted on Vercel.
2. **Backend:** FastAPI (Python >= 3.12 / 3.13, Pydantic 2.8+, Uvicorn) hosted on Render / Docker.
3. **Ephemeris Engine:** `xalen-ephemeris` — a native high-precision clean-room astronomical calculation engine written in Rust and compiled via Maturin/PyO3.
4. **Database & Auth:** Supabase PostgreSQL with managed GoTrue authentication, fine-grained Row-Level Security (RLS) policies, transactional sequential numbering, and storage buckets.
5. **PDF Engine:** Python ReportLab, Pillow, pypdf, pypdfium2, and uharfbuzz for high-resolution bilingual (Tamil/English) report rendering.

#### Core Mobile Strategy
The upcoming Android application will be built using **React Native + Expo** and will operate as a **first-class sibling client** alongside the existing Next.js web application. Both clients will communicate with the **same shared FastAPI backend** and **same Supabase PostgreSQL database**, sharing user accounts, customer records, saved horoscopes, calculation logic, and PDF reports without code duplication or database bifurcation.

---

### 2. EXISTING VS PROPOSED SYSTEM ARCHITECTURE

#### 2.1 Current System Topology (Web Monorepo)

```
+-------------------------------------------------------------------------+
|                              WEB CLIENT                                 |
|               Next.js 16.4.2 (React 19, Tailwind CSS 4)                 |
+------------------------------------+------------------------------------+
                                     |
                +--------------------+--------------------+
                |                                         |
     (HTTP Cookies / SSR)                       (Bearer JWT / Reverse Proxy)
                v                                         v
+-------------------------------+       +---------------------------------+
|      Next.js Route Handlers   |       |         FastAPI Backend         |
|  (/api/auth, /api/horoscopes, |       |      (Python 3.12+, Uvicorn)    |
|   /api/customers, /api/v1/*)  |       |   235 Calculation Operations    |
+---------------+---------------+       +----------------+----------------+
                |                                        |
                | (Service Role / SSR)                   | (Service Role & JWT)
                v                                        v
+-------------------------------------------------------------------------+
|                       SUPABASE CLOUD PLATFORM                           |
|  - Auth (GoTrue Identity)                                               |
|  - PostgreSQL Database (RLS Policies, Sequential Triggers)              |
|  - Storage Buckets ('horoscope-reports')                                |
+-------------------------------------------------------------------------+
```

#### 2.2 Proposed Dual-Client Shared-Backend Topology

```
+------------------------------------+   +------------------------------------+
|          NEXT.JS WEB APP           |   |       REACT NATIVE EXPO APP        |
|  Next.js 16.4.2 (Vercel / Browser) |   |    Android App (Expo SDK 52/53)    |
+-----------------+------------------+   +-----------------+------------------+
                  |                                        |
     (Cookies /   |                                        | (Bearer JWT via
      Bearer JWT) |                                        |  Expo SecureStore)
                  |                                        |
                  +-------------------+--------------------+
                                      |
                                      v
          +--------------------------------------------------------+
          |             SHARED FASTAPI BACKEND SERVER              |
          |               (Hosted on Render / Linux)               |
          |--------------------------------------------------------|
          |  * Auth Middleware: JWT Verification (auth_service.py) |
          |  * Ephemeris Engine: XALEN Rust PyO3 Core              |
          |  * 235 Calculation Endpoints (Vedic, KP, Dasa, Yogas)  |
          |  * PDF Report Generation (ReportLab + Tamil HarfBuzz)  |
          |  * In-Memory Horoscope Cache (300s TTL / 300 Max)      |
          |  * Shared Horoscope & Customer CRUD API Extension      |
          +---------------------------+----------------------------+
                                      |
                                      | (PostgREST / Service Role)
                                      v
          +--------------------------------------------------------+
          |                SUPABASE MANAGED CLOUD                  |
          |--------------------------------------------------------|
          |  1. Auth (GoTrue): Single user identity & credentials  |
          |  2. Database: PostgreSQL 15+                           |
          |     - public.profiles (roles & granular permissions)   |
          |     - public.saved_horoscopes (per-user charts)        |
          |     - public.customers (CRM phone & WhatsApp)          |
          |     - public.pinned_horoscopes (dashboard pins)        |
          |     - public.saved_kp_charts & analyses                |
          |     - public.muhurta_*, remedy_*, vastu_* tables       |
          |  3. Storage: 'horoscope-reports' bucket                |
          +--------------------------------------------------------+
```

---

### 3. COMPONENT BREAKDOWN & MOBILE READINESS

| Component | Web Implementation | Mobile (Expo) Readiness | Mobile Strategy |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js 16.4.2 (App Router) | React Native 0.76+ / Expo SDK 52+ | New standalone Expo repository or sibling package. |
| **Authentication Client** | `@supabase/ssr` (Cookie-based) | `@supabase/supabase-js` + `expo-secure-store` | Standard JWT Bearer token authentication stored in hardware-encrypted keystore. |
| **Calculations** | FastAPI `/api/v1/*` proxy | Direct HTTP calls to FastAPI Backend | 100% direct reuse of existing 235 calculation endpoints. |
| **Storage & Caching** | LocalStorage + Memory Cache | `AsyncStorage` + React Query / Zustand | Offline caching of completed horoscope results. |
| **Chart Visualizer** | React SVG South Indian Chart | `react-native-svg` South Indian Chart | Clean React Native port of existing 12-box SVG grid renderer. |
| **PDF Generation** | Server-side ReportLab | Server-side ReportLab | Mobile initiates download stream via `expo-file-system` and views via `expo-sharing`. |
| **State Management** | React Context (`auth-context.tsx`) | Zustand / React Context | Light, predictable reactive state for user session and active chart. |

---

### 4. NETWORK & CORS SPECIFICATIONS

1. **Current Backend CORS Settings (`backend/app/config.py`):**
   ```python
   allowed_origins = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "http://localhost:3001",
       "http://127.0.0.1:3001",
       "https://gai-astrology.com",
       "https://www.gai-astrology.com",
       "https://astrology-website.vercel.app",
   ]
   allowed_origin_regex = r"^https://.*\.vercel\.app$"
   ```
2. **Mobile Network Implications:**
   - Native Android applications (via `fetch` or `axios` in React Native) do **not** send an `Origin` header like a web browser; therefore, CORS restrictions do not block native mobile HTTP traffic.
   - For web preview / Expo Web development, `http://localhost:8081` (Expo default dev port) must be included in allowed origins during mobile development.
3. **Payload Limits:**
   - FastAPI enforces a 10 MB request limit (`MAX_REQUEST_BODY_BYTES = 10_485_760`).
   - Standard mobile birth input requests are < 1 KB; PDF download responses range between 150 KB and 2.5 MB, well within safe transport limits.

---

### 5. DUAL-CLIENT DATA CONSISTENCY GUARANTEE

Both frontends guarantee data consistency because:
1. **Single Source of Truth:** All horoscope computations originate exclusively from the XALEN Rust ephemeris in FastAPI.
2. **Deterministic Outputs:** Given the same birth parameters (date, time, lat, lon, ayanamsa), the mathematical output is 100% identical on Web, Android, and PDF reports.
3. **Unified Identity:** A customer registered on the Android app logs into the same account on Web with identical saved horoscopes, pinned charts, and customer profiles.
4. **Advisory Locking:** Monotonic sequential display numbers (`display_number`) are enforced at the PostgreSQL database level using transactional advisory locks (`pg_advisory_xact_lock`), completely preventing race conditions regardless of which client creates the record.
