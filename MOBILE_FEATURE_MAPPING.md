# GOKUL'S ASTROLOGICAL INSIGHTS
## ANDROID APP FEATURE-TO-BACKEND MAPPING SPECIFICATION

> **Document Version:** 1.0.0  
> **Target Platform:** React Native + Expo (Android)  
> **Architecture Principle:** 100% Shared Backend & Database

---

### 1. MVP FEATURE MAPPING (PHASE 1)

#### Feature 1: Login and Account
- **Objective:** Secure user authentication, session persistence, role determination, and profile management.
- **Backend Service:** Supabase Auth (GoTrue).
- **Database Table:** `public.profiles`.
- **API Endpoints:**
  - `POST https://<supabase-url>/auth/v1/token?grant_type=password` (Login)
  - `POST https://<supabase-url>/auth/v1/signup` (Registration)
  - `GET /rest/v1/profiles?id=eq.<user_id>` (Profile metadata)
- **Mobile Storage:** `expo-secure-store` (Tokens: `access_token`, `refresh_token`).
- **UI Screen:** `LoginScreen.tsx` (Email/Password, validation, error banner), `AccountScreen.tsx`.

#### Feature 2: Dashboard
- **Objective:** Astrologer command center displaying quick Panchang, today's planetary transits, pinned charts, and recent saved horoscopes.
- **Backend Service:** FastAPI + Supabase PostgREST.
- **Database Tables:** `public.pinned_horoscopes`, `public.saved_horoscopes`.
- **API Endpoints:**
  - `GET /api/v1/horoscope/live-transits` (Real-time planetary positions)
  - `POST /api/v1/muhurta/panchang` (Today's Tithi, Nakshatra, Yoga, Karana, Vara)
  - `GET /rest/v1/pinned_horoscopes?select=horoscope_id,saved_horoscopes(*)`
  - `GET /rest/v1/saved_horoscopes?select=id,display_number,person_name,birth_date&limit=5&order=created_at.desc`
- **UI Screen:** `DashboardScreen.tsx` with pull-to-refresh and horizontal scrollable pinned charts.

#### Feature 3: Horoscope Creation
- **Objective:** Fast, validated birth data entry form calculating astronomical chart data.
- **Backend Service:** FastAPI Ephemeris (`ephemeris.py`).
- **API Endpoint:**
  - `POST /api/v1/horoscope/calculate`
  - `POST /api/v1/horoscope/dasa` (depth=3)
- **Request Schema:** `HoroscopeRequest` (`birth_date`, `birth_time`, `timezone`, `latitude`, `longitude`, `ayanamsa: 0`, `house_system: 2`).
- **Response Schema:** `HoroscopeResponse` (Planetary coordinates, house cusps, panchang, yogas).
- **Persistence Path:** Writes completed record to `public.saved_horoscopes` via Supabase client or shared FastAPI endpoint.
- **UI Screen:** `CreateHoroscopeScreen.tsx` (Date picker, 12-hour/24-hour time picker, location geocoding lookup).

#### Feature 4: Horoscope Details & Chart Visualizer
- **Objective:** Interactive South Indian chart viewer showing D1 Rasi, D9 Navamsa, planetary tables, dignities, and Dasa periods.
- **Backend Service:** FastAPI (`varga_engine.py`, `dasa_service.py`).
- **API Endpoints:**
  - `POST /api/v1/horoscope/varga/d1-d9` (or retrieved from saved record)
  - `POST /api/v1/vedic/doshas` (Mangal, Rahu-Ketu, Kalasarpa)
- **UI Components:**
  - `SouthIndianChart.tsx` (SVG rendered via `react-native-svg` showing 12 houses: Mesha to Meena, Retrograde indicator `(R)`, Ascendant `Asc/ல`).
  - `PlanetaryTable.tsx` (Planetary degrees, Nakshatra, Pada, Dignity badges).
  - `DasaTreeViewer.tsx` (Expandable accordion for Maha Dasa and Bhuktis).

#### Feature 5: Saved Horoscopes Directory
- **Objective:** Searchable, paginated directory of client horoscopes with customer details and pinning support.
- **Backend Service:** Supabase PostgREST / Shared FastAPI Endpoint.
- **Database Tables:** `public.saved_horoscopes`, `public.pinned_horoscopes`, `public.customers`.
- **API Operations:**
  - Listing with search filter (`person_name.ilike.%query%`).
  - Pagination (`range(offset, offset + limit - 1)`).
  - Toggle Pin (`insert` / `delete` on `pinned_horoscopes`).
  - Delete chart (`delete().eq('id', horoscope_id)`).
- **UI Screen:** `SavedHoroscopesScreen.tsx` with instant search bar, badge indicators, and swipe-to-delete.

#### Feature 6: Tamil & English PDF Reports
- **Objective:** One-click download, offline saving, and WhatsApp sharing of official 9-page bilingual horoscope reports.
- **Backend Service:** FastAPI ReportLab Engine (`pdf_report_engine/*`).
- **API Endpoints:**
  - `POST /api/v1/reports/horoscope/pdf` (or `GET /api/v1/reports/horoscope/pdf/{horoscope_id}?language=ta|en`)
  - `POST /api/v1/reports/horoscope/single-page-pdf`
- **Mobile Integration:**
  1. `expo-file-system`: Downloads binary stream to `${FileSystem.documentDirectory}Horoscope_<name>.pdf`.
  2. `expo-sharing`: Opens Android native system share sheet (WhatsApp, Gmail, Bluetooth) or native PDF viewer.
- **UI Component:** `PdfDownloadButton.tsx` with progress indicator and language selector (`தமிழ்` / `English`).

---

### 2. PHASE 2 FEATURE MAPPING

#### Feature 7: KP Astrology (Krishnamurti Padhdhati)
- **Backend Service:** FastAPI KP Engine (`kp_service.py`, `kp_event_engine`).
- **Database Table:** `public.saved_kp_charts`, `public.kp_event_analyses`.
- **API Endpoints:**
  - `POST /api/v1/horoscope/kp` (Natal cuspal sub-lords & 4-tier significators)
  - `POST /api/v1/horoscope/kp/horary` (1-249 Horary calculation)
  - `POST /api/v1/horoscope/kp/horary-predict` (Automated topic prediction)
  - `POST /api/v1/horoscope/kp-events/analyze` (32 standard event predictions)
  - `POST /api/v1/reports/kp/pdf` (6-page KP PDF report)
- **UI Screen:** `KpAstrologyScreen.tsx` (Cusp table, planet significators, Prashna 1-249 selector).

#### Feature 8: Transit Analysis & Double Transit Radar
- **Backend Service:** FastAPI (`double_transit_engine.py`, `ephemeris.py`).
- **API Endpoints:**
  - `GET /api/v1/horoscope/live-transits`
  - `POST /api/v1/vedic/double-transit` (Jupiter + Saturn simultaneous aspect radar)
  - `POST /api/v1/vedic/ashtakavarga/kaksha/transit`
- **UI Screen:** `TransitRadarScreen.tsx` (Live sky transit wheel + event timing radar).

#### Feature 9: Marriage Compatibility (Porutham)
- **Backend Service:** FastAPI Marriage Engine (`marriage_engine/*`).
- **Database Table:** `public.saved_marriage_compatibility_reports`.
- **API Endpoints:**
  - `POST /api/marriage-compatibility/analyze` (10/12 Poruthams, Papasamya, Dasha Sandhi)
  - `POST /api/v1/reports/marriage-compatibility/pdf`
- **UI Screen:** `MarriageMatchingScreen.tsx` (Boy/Girl dual input form, Porutham scorecard, Rajju/Stree Dheerkha alerts).

---

### 3. PHASE 3 FEATURE MAPPING

#### Feature 10: Complete Numerology Suite
- **Backend Service:** FastAPI Numerology (`app/services/numerology/*`).
- **Database Table:** `public.saved_numerology_reports`.
- **API Endpoints:**
  - `POST /api/v1/numerology/traditional` (Life path, Destiny, Soul urge)
  - `POST /api/v1/numerology/destiny-matrix` (Lo Shu Grid)
  - `POST /api/v1/numerology/name-analysis` & `name-correction`
  - `POST /api/v1/numerology/export-pdf`
- **UI Screen:** `NumerologyScreen.tsx` (Lo Shu 3x3 interactive grid, Chaldean name analyzer).

#### Feature 11: Advanced Remedies & Temple Pariharams
- **Backend Service:** FastAPI Remedy Engine (`app/services/remedy_engine/*`).
- **Database Table:** `public.remedy_knowledge_base`, `public.remedy_reports`.
- **API Endpoints:**
  - `POST /api/v1/remedies/analyze` (Lal Kitab, Graha Pariharams)
  - `GET /api/v1/remedies/temples` (Navagraha sthalams in Tamil Nadu)
  - `POST /api/v1/remedies/gemstones`, `POST /api/v1/remedies/rudraksha`
  - `POST /api/v1/reports/gemstone-rudraksha/pdf`
- **UI Screen:** `RemediesScreen.tsx` (Categorized tabs: Temples, Gemstones, Mantras, Charity).

#### Feature 12: Shadbala & Ashtakavarga
- **Backend Service:** FastAPI Shadbala & Ashtakavarga Engines.
- **API Endpoints:**
  - `POST /api/v1/vedic/shadbala` (Sthana, Dig, Kala, Chesta, Naisargika, Drik bala)
  - `POST /api/v1/vedic/ashtakavarga` (BAV / SAV tables)
  - `POST /api/v1/vedic/ashtakavarga/prastara`
- **UI Screen:** `StrengthsScreen.tsx` (Shadbala horizontal bar charts, Ashtakavarga score grids).

#### Feature 13: Advanced Divisional Charts (Shodashvarga D1-D60)
- **Backend Service:** FastAPI Varga Engine (`varga_engine.py`).
- **API Endpoints:**
  - `POST /api/v1/horoscope/varga/shodashvarga`
  - `GET /api/v1/horoscope/varga/shodashvarga/{horoscope_id}`
  - `POST /api/v1/reports/shodashvarga/pdf`
- **UI Screen:** `DivisionalChartsScreen.tsx` (Tabs for D2 Hora, D3 Drekkana, D4 Chaturthamsha, D7 Saptamsha, D10 Dashamsha career, D12 Dwadashamsha, D60 Shashtiamsha).
