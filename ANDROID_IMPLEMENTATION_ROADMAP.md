# GOKUL'S ASTROLOGICAL INSIGHTS
## REACT NATIVE + EXPO ANDROID IMPLEMENTATION ROADMAP

> **Document Version:** 1.0.0  
> **Target Framework:** React Native 0.76+ / Expo SDK 52+ (Managed Workflow)  
> **Language:** TypeScript 5+  
> **Styling:** NativeWind (Tailwind CSS for React Native)  
> **Icons:** Lucide React Native  
> **Estimated Project Timeline:** 6 to 8 Weeks (Across 4 Stages)

---

### 1. TECHNICAL STACK & DEPENDENCY INVENTORY

The following verified libraries are recommended for the Android application to match the web design system while maximizing native performance:

```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "expo-router": "~4.0.0",
    "react-native": "0.76.x",
    "react": "18.3.1",
    "@supabase/supabase-js": "^2.48.0",
    "expo-secure-store": "~14.0.0",
    "expo-file-system": "~18.0.0",
    "expo-sharing": "~13.0.0",
    "expo-status-bar": "~2.0.0",
    "react-native-svg": "15.8.0",
    "lucide-react-native": "^0.475.0",
    "nativewind": "^4.1.23",
    "tailwindcss": "^3.4.17",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.60.0",
    "@react-native-community/datetimepicker": "8.2.0"
  }
}
```

---

### 2. PHASED EXECUTION ROADMAP

```
+-------------------------------------------------------------------------+
| STAGE 1: FOUNDATION & NETWORK (Week 1 - 2)                              |
| - Expo project setup, TypeScript configuration, NativeWind              |
| - Supabase Client + Expo SecureStore hardware authentication adapter   |
| - Typed FastAPI HTTP API Client (sharing schemas with web)              |
| - Navigation hierarchy (Expo Router file-based tabs & stacks)           |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| STAGE 2: MVP CORE ENGINES (Week 3 - 4)                                  |
| - Feature 1: Login & Account Profile management                         |
| - Feature 2: Astrologer Dashboard (Panchang & Live Transits)            |
| - Feature 3: Birth Details Input Form (Date/Time Picker, Coordinates)   |
| - Feature 4: Interactive South Indian Chart Visualizer (D1 & D9 SVG)    |
| - Feature 5: Saved Horoscopes Directory (Search, Pagination, Pinning)   |
| - Feature 6: Bilingual PDF Report Generator (Download & Share Sheet)    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| STAGE 3: PHASE 2 MODULES (Week 5 - 6)                                   |
| - Feature 7: KP Astrology (Natal Cusps, Horary 1-249, 32 KP Events)     |
| - Feature 8: Transit Analysis & Jupiter-Saturn Double Transit Radar     |
| - Feature 9: Marriage Compatibility (Porutham, Papasamya, Dasha Sandhi) |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| STAGE 4: PHASE 3 MODULES & PRODUCTION RELEASE (Week 7 - 8)              |
| - Feature 10: Complete Numerology Suite (Lo Shu Grid & Name Correction) |
| - Feature 11: Remedies, Navagraha Temples & Gemstones                   |
| - Feature 12: Shadbala Strengths & Ashtakavarga Matrices                |
| - Feature 13: Shodashvarga 16 Divisional Charts (D1 - D60)              |
| - Performance profiling, APK/AAB build via EAS, Play Store deployment   |
+-------------------------------------------------------------------------+
```

---

### 3. DETAILED STAGE BREAKDOWN & DELIVERABLES

#### Stage 1: Foundation, Auth & Navigation (Week 1 – 2)
1. **Repository Setup:**
   - Initialize clean Expo project using Expo Router.
   - Configure path aliases (`@/*`) matching web structure.
2. **Authentication Integration:**
   - Implement `ExpoSecureStoreAdapter` for `@supabase/supabase-js`.
   - Create `AuthContext` / `useAuthStore` using Zustand.
   - Wire auto-token refresh and protected route guards.
3. **Shared API Client:**
   - Create `src/lib/api.ts` ported from the web client, attaching `Authorization: Bearer <token>` on every call.
   - Connect to FastAPI backend endpoint base URL (configurable via `EXPO_PUBLIC_API_BASE_URL`).
4. **Design System & Typography:**
   - Configure Tailwind / NativeWind color tokens matching web dark/gold palette.
   - Ensure Tamil Unicode font rendering on Android devices.

#### Stage 2: MVP Core Implementation (Week 3 – 4)
1. **Horoscope Form (`CreateHoroscopeScreen`):**
   - Native Android Date & Time Pickers.
   - Quick city lookup with pre-filled coordinates.
   - Client-side validation for latitude/longitude boundaries.
2. **South Indian Chart Renderer (`SouthIndianChart.tsx`):**
   - High-performance declarative SVG chart using `react-native-svg`.
   - 12-box traditional diamond/square grid layout.
   - Planetary glyphs, degrees, retrogradation flags, and Tamil/English toggle.
3. **Dasa Tree Viewer (`DasaViewer.tsx`):**
   - Accordion tree structure displaying Maha Dasa, Bhukti, and Pratyantar Dasa with start and end dates.
4. **Saved Horoscopes (`SavedHoroscopesScreen.tsx`):**
   - Virtualized `FlatList` with pagination and debounced search.
   - Pin / unpin action updating `public.pinned_horoscopes`.
5. **PDF Report Downloader:**
   - Streaming download via `expo-file-system`.
   - Native Android Share Sheet invocation via `expo-sharing`.

#### Stage 3: Phase 2 Engines (Week 5 – 6)
1. **KP Astrology Screen:**
   - Display 12 house cusps with exact star lord, sub-lord, and sub-sub-lord.
   - Horary number selector (1 to 249) with instant query execution.
   - 4-tier significators matrix.
2. **Transit Analysis:**
   - Real-time transit radar visualizer comparing natal vs transit planetary degrees.
3. **Marriage Compatibility:**
   - Dual birth details input.
   - 10 Porutham scorecard, Papasamya points calculation, and Dasha Sandhi check.

#### Stage 4: Phase 3 Engines & Play Store Launch (Week 7 – 8)
1. **Numerology Module:**
   - Interactive 3x3 Lo Shu Grid visualizer.
   - Name correction score calculator (Chaldean & Pythagorean).
2. **Remedies & Temples:**
   - Navagraha temples directory with map links.
   - Gemstone & Rudraksha advisory.
3. **Shadbala & Shodashvarga:**
   - Visual strength comparison charts.
   - 16 Divisional charts tab navigator.
4. **Build & Release:**
   - Configure `app.json` with permissions (`INTERNET`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`).
   - Run EAS Build to generate release AAB (Android App Bundle).
   - Sign with release keystore for Google Play Store submission.

---

### 4. ESTIMATED EFFORT & RESOURCE ALLOCATION

| Phase | Scope | Dedicated Hours | Sprints (2 Weeks) |
| :--- | :--- | :--- | :--- |
| **Stage 1: Foundation** | Project setup, Auth, API Client, Navigation | 60 Hours | Sprint 1 |
| **Stage 2: MVP Core** | Dashboard, Form, SVG Chart, Saved List, PDF | 90 Hours | Sprint 2 |
| **Stage 3: Phase 2** | KP Engine, Transits, Marriage Matching | 80 Hours | Sprint 3 |
| **Stage 4: Phase 3** | Numerology, Remedies, Shadbala, Vargas, EAS Build | 90 Hours | Sprint 4 |
| **TOTAL** | **Full Feature-Parity Android App** | **320 Hours** | **4 Sprints (8 Weeks)** |

---

### 5. RECOMMENDED NEXT IMPLEMENTATION STAGE

Upon explicit client approval of this Stage 0 Audit:
- **Proceed to Stage 1:** Initialize the React Native + Expo managed repository, set up Supabase Auth with Expo SecureStore, connect to the existing FastAPI backend, and verify end-to-end token validation with the live backend.
