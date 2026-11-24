# GOKUL'S ASTROLOGICAL INSIGHTS
## EXISTING API INVENTORY & MOBILE COMPATIBILITY MATRIX

> **Document Version:** 1.0.0  
> **Source Verification:** FastAPI OpenAPI Inspection (`backend/data/openapi_dump.json`) & Next.js App Router  
> **Total FastAPI Endpoints:** 210 Paths / 235 HTTP Operations  
> **Authenticated Operations:** 90  
> **Public Operations:** 145  

---

### 1. SUMMARY OF API ARCHITECTURE

All astrology calculations are serviced by the Python FastAPI backend (`/api/v1/*`). In the current production deployment:
- **Calculation Services:** 100% accessible via FastAPI.
- **PDF Report Generation:** 100% accessible via FastAPI.
- **Specialized Astrology Engines (KP, Remedies, Numerology, Vastu):** 100% accessible via FastAPI.
- **Horoscope Persistence & Listing:** Currently routed through Next.js Route Handlers (`/api/horoscopes`) before hitting Supabase, with sub-engine endpoints in FastAPI reading directly from Supabase via `get_cached_saved_horoscope`.

---

### 2. CORE ENDPOINT INVENTORY

#### 2.1 Authentication & Profile Endpoints

| HTTP Method | Route | Auth Req | Request Schema | Response Schema | Mobile Compatibility | Reusability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/v1/token?grant_type=password` (Supabase GoTrue) | None | `{ email, password }` | `{ access_token, refresh_token, user }` | **100% Mobile Ready** | Direct reuse via `@supabase/supabase-js` |
| `POST` | `/api/auth/login` (Next.js Route) | None | `{ identifier, password }` | `{ success, user, redirect }` | Web SSR / Needs HTTP client | Can be called by mobile or bypassed |
| `GET` | `/api/auth/me` (Next.js Route) | Supabase Cookie / Bearer | None | `{ authenticated, user }` | Web SSR | Replaced on mobile by Supabase client + profile fetch |
| `POST` | `/api/auth/logout` (Next.js Route) | Session | None | `{ success }` | Web SSR | Direct reuse via `supabase.auth.signOut()` |
| `GET` | `/api/v1/admin/users` (FastAPI) | Bearer JWT (`admin`) | Query params: `page, limit` | `List[AdminUserItem]` | **100% Mobile Ready** | Direct reuse |
| `POST` | `/api/v1/admin/bootstrap` (FastAPI) | None / Service Secret | None | `{ status, message }` | **100% Mobile Ready** | Internal admin operation |

#### 2.2 Vedic Horoscope Calculation & Sub-Engine Endpoints

| HTTP Method | Route | Auth Req | Request Schema | Response Schema | Mobile Compatibility | Reusability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/horoscope/calculate` | Optional | `HoroscopeRequest` (`BirthInput` + flags) | `HoroscopeResponse` (Planets, Houses, Panchang, Yogas) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/dasa` | Optional | `DasaRequest` (`BirthInput`, `depth: 1..5`) | `DasaResponse` (`dasa_tree`, `current_dasa`, `balance`) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/dasa/direct` | None | `DirectDasaRequest` (`moon_sidereal_deg`, `birth_jd`, `depth`) | `DasaResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/varga/d1-d9` | Optional | `VargaD1D9Request` (`BirthInput` OR `saved_horoscope_id`) | `VargaD1D9Response` (D1 Rasi & D9 Navamsa 12-sign mapping) | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/varga/d1-d9/{horoscope_id}` | Bearer JWT | URL Param: `horoscope_id: UUID` | `VargaD1D9Response` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/varga/shodashvarga` | Optional | `ShodashvargaRequest` (`BirthInput` OR `saved_horoscope_id`) | `ShodashvargaResponse` (All 16 charts D1 to D60) | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/varga/shodashvarga/{horoscope_id}` | Bearer JWT | URL Param: `horoscope_id: UUID` | `ShodashvargaResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/live-transits` | None | Query: `timezone, latitude, longitude, ayanamsa` | `LiveTransitsResponse` (Current planetary longitudes) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/live-transits` | None | `LiveTransitsRequest` | `LiveTransitsResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/yogas` | None | `HoroscopeRequest` | `VedicYogaResponse` (195 BPHS Yogas) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/doshas` | None | `HoroscopeRequest` | `UnifiedDoshaResponse` (Mangal, Rahu-Ketu, Kalasarpa, Pitru) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/shadbala` | None | `HoroscopeRequest` | `ShadbalaResponse` (6-fold strength + rank) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/ashtakavarga` | None | `HoroscopeRequest` | `AshtakavargaResponse` (BAV, SAV, Shodhana) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/ashtakavarga/prastara` | None | `HoroscopeRequest` | `PrastaraResponse` (Detailed bindu matrix) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/ashtakavarga/kaksha` | None | `HoroscopeRequest` | `KakshaResponse` (8 kaksha division) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/double-transit` | None | `DoubleTransitRequest` (Lagna, Rasi, domain) | `DoubleTransitResponse` (Guru-Shani Radar) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/vedic/medical-astrology` | None | `MedicalAstrologyRequest` (Birth details or saved ID) | `MedicalAstrologyResponse` | **100% Mobile Ready** | **Direct reuse without changes** |

#### 2.3 KP Astrology Endpoints

| HTTP Method | Route | Auth Req | Request Schema | Response Schema | Mobile Compatibility | Reusability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/horoscope/kp` | None | `KpRequest` (`BirthInput`, `ayanamsa: 1`) | `KpResponse` (249 Cusps, Planets, 4-tier Sig, Ruling Planets) | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/kp/horary` | None | `HoraryKpRequest` (`horary_number: 1..249`) | `HoraryKpResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/kp/horary-predict` | None | `InstantHoraryPredictionRequest` | `InstantHoraryPredictionResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/kp/horary-predict/topics` | None | None | `List[HoraryTopicInfo]` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/kp/charts` | Bearer JWT | `SaveKpChartRequest` | `SavedKpChartItem` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/kp/charts` | Bearer JWT | Query: `page, limit` | `SavedKpChartListResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/kp/charts/{chart_id}` | Bearer JWT | URL Param: `chart_id: UUID` | `SavedKpChartItem` | **100% Mobile Ready** | **Direct reuse without changes** |
| `DELETE` | `/api/v1/horoscope/kp/charts/{chart_id}` | Bearer JWT | URL Param: `chart_id: UUID` | `{ success: true }` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/kp/reader3/table-249` | None | None | `List[Table249Row]` | **100% Mobile Ready** | **Direct reuse without changes** |
| `POST` | `/api/v1/horoscope/kp-events/analyze` | Bearer JWT | `KpEventAnalysisRequest` | `KpEventAnalysisResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/horoscope/kp-events/registry` | None | None | `List[KpEventDefinition]` (32 Standard Events) | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/kp/daily-horoscope` | None | Query: `rasi, date` | `KpDailyHoroscopeResponse` | **100% Mobile Ready** | **Direct reuse without changes** |
| `GET` | `/api/v1/kp/monthly-horoscope` | None | Query: `rasi, month, year` | `KpMonthlyHoroscopeResponse` | **100% Mobile Ready** | **Direct reuse without changes** |

#### 2.4 PDF Generation Services

| HTTP Method | Route | Auth Req | Request Schema | Response Content-Type | Mobile Compatibility | Reusability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/reports/horoscope/pdf` | Optional | `HoroscopePdfReportRequest` (`saved_id` OR `birth_input`, `language: 'ta'\|'en'`) | `application/pdf` (Binary Stream, 9 pages) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `GET` | `/api/v1/reports/horoscope/pdf/{horoscope_id}` | Bearer JWT | Query: `language: 'ta'\|'en'` | `application/pdf` (Binary Stream, 9 pages) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `POST` | `/api/v1/reports/horoscope/single-page-pdf` | Optional | `SinglePageHoroscopePdfRequest` | `application/pdf` (1 page) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `POST` | `/api/v1/reports/kp/pdf` | Bearer JWT | `KpPdfReportRequest` | `application/pdf` (6 pages) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `GET` | `/api/v1/reports/kp/pdf/{chart_id}` | Bearer JWT | Query: `language: 'ta'\|'en'` | `application/pdf` (6 pages) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `POST` | `/api/v1/tools/horoscope-writing/pdf` | Bearer JWT | `HoroscopeWritingPdfRequest` | `application/pdf` (Traditional 6-page Tamil Booklet) | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `POST` | `/api/v1/reports/marriage-compatibility/pdf` | Bearer JWT | `MarriagePdfRequest` | `application/pdf` | **100% Mobile Ready** | Direct streaming to `expo-file-system` |
| `POST` | `/api/v1/reports/shodashvarga/pdf` | Bearer JWT | `ShodashvargaPdfRequest` | `application/pdf` | **100% Mobile Ready** | Direct streaming to `expo-file-system` |

#### 2.5 Horoscope CRUD Operations

| Operation | Current Web Location | Request Payload | Security / Isolation | Mobile Direct Strategy | Recommended Shared Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Save Horoscope** | Next.js `POST /api/horoscopes` | `SaveHoroscopePayload` (Birth details + calculation snapshot) | Authenticated user session; validates customer and packs 3-level Dasa | Supabase direct `insert()` OR shared FastAPI endpoint | Implement `POST /api/v1/horoscopes` in FastAPI |
| **List Horoscopes** | Next.js `GET /api/horoscopes` | Query: `page, limit, search, all` | RLS: `user_id = auth.uid()`; pinned chart priority | Supabase direct `select()` OR shared FastAPI endpoint | Implement `GET /api/v1/horoscopes` in FastAPI |
| **Get Horoscope** | Next.js `GET /api/horoscopes/[id]` | URL Param: `id: UUID` | RLS: `user_id = auth.uid()` | Supabase direct `select().eq('id', id)` | Implement `GET /api/v1/horoscopes/{id}` in FastAPI |
| **Update Horoscope** | Next.js `PUT /api/horoscopes/[id]` | `{ person_name, customer_phone, ... }` | RLS: `user_id = auth.uid()` | Supabase direct `update()` | Implement `PUT /api/v1/horoscopes/{id}` in FastAPI |
| **Delete Horoscope** | Next.js `DELETE /api/horoscopes/[id]` | URL Param: `id: UUID` | RLS: `user_id = auth.uid()` | Supabase direct `delete()` | Implement `DELETE /api/v1/horoscopes/{id}` in FastAPI |
| **Pin / Unpin Chart** | Next.js API / Supabase table | `{ horoscope_id }` | RLS: `user_id = auth.uid()` on `pinned_horoscopes` | Supabase direct `insert()` / `delete()` | Standard Supabase table access |

---

### 3. API REUSE PERCENTAGE BREAKDOWN

```
Total Verified Endpoints in System: 235
- 100% Directly Reusable on Mobile (FastAPI Calculations & PDFs): 223 endpoints (94.9%)
- Reusable via Supabase Client Direct / RLS (Customer & Horoscope Data): 8 endpoints (3.4%)
- Web-Specific BFF Proxies (Require Shared Endpoint in FastAPI): 4 endpoints (1.7%)

OVERALL REUSABILITY INDEX: 98.3%
```
