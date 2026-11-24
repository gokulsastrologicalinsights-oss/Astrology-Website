# GOKUL'S ASTROLOGICAL INSIGHTS
## MOBILE TESTING STRATEGY & ASTROLOGICAL REGRESSION SUITE

> **Document Version:** 1.0.0  
> **Target Platform:** Android (React Native + Expo)  
> **Key Quality Gate:** Astrological outputs on Android must match Web and FastAPI backend to 4 decimal places ($0.0001^\circ$)

---

### 1. MULTI-TIER TESTING PYRAMID

```
                       / \
                      /   \
                     / E2E \       Maestro / Detox UI Flow Automation
                    /-------\
                   / Integr. \     API & Supabase Auth Integration (MSW / Live)
                  /-----------\
                 /  Component  \   React Native Testing Library (RNTL)
                /---------------\
               /   Unit Tests    \ Jest (Formatters, Timezones, State Stores)
              /-------------------\
```

---

### 2. TIER 1: UNIT TESTING (JEST)

- **Execution Engine:** Jest + `ts-jest` / Babel.
- **Coverage Target:** $> 85\%$ for utility functions, state reducers, and date math.
- **Key Test Suites:**
  1. **Date & Time Formatter Tests:**
     - Validate conversions between user input (`DD/MM/YYYY`, 12-hour AM/PM) and ISO (`YYYY-MM-DD`, `HH:MM:SS`).
     - Leap year edge cases (Feb 29) and month boundaries.
  2. **Coordinate & Geolocation Validation:**
     - Reject latitudes $> 90^\circ$ or $< -90^\circ$.
     - Reject longitudes $> 180^\circ$ or $< -180^\circ$.
  3. **Timezone Offset Parsing:**
     - Validate IANA names (`Asia/Kolkata`, `America/New_York`) and raw offsets (`+05:30`, `-04:00`).
  4. **Zustand State Stores:**
     - `useAuthStore`: Verify state transitions on login, token refresh, and logout.
     - `useChartStore`: Verify active chart caching and selection.

---

### 3. TIER 2: COMPONENT TESTING (REACT NATIVE TESTING LIBRARY)

- **Target:** UI component rendering, user interactions, and visual accessibility.
- **Key Component Suites:**
  1. **`SouthIndianChart.tsx`:**
     - Verify all 12 Rasi boxes render correctly.
     - Verify Ascendant (`ல` / `Asc`) glyph renders in correct zodiac sign box.
     - Verify retrograded planets display `(R)` indicator.
     - Verify multi-planet occupancy in a single house wraps cleanly without SVG clipping.
  2. **`DasaTreeViewer.tsx`:**
     - Verify expanding a Maha Dasa displays all 9 Antar Dasas (Bhuktis).
     - Verify active current Dasa is visually highlighted with the "Current" badge.
  3. **`PdfDownloadButton.tsx`:**
     - Verify loading spinner shows during network stream.
     - Verify error toast displays if network fails.

---

### 4. TIER 3: BACKEND INTEGRATION & AUTHENTICATION TESTING

- **Target:** Contract verification between Android client, Supabase, and FastAPI.
- **Key Test Suites:**
  1. **Supabase SecureStore Auth Cycle:**
     - Authenticate test account via `supabase.auth.signInWithPassword`.
     - Verify tokens persist in mocked `expo-secure-store`.
     - Verify token auto-refresh triggers correctly before expiration.
  2. **FastAPI Calculation Contracts:**
     - Call `POST /api/v1/horoscope/calculate` with standard payload.
     - Validate response adheres to `HoroscopeResponse` schema.
  3. **PDF Stream Handling:**
     - Call `POST /api/v1/reports/horoscope/pdf`.
     - Validate `Content-Type: application/pdf` and verify file saves to `FileSystem.documentDirectory` with byte size $> 100\text{ KB}$.

---

### 5. TIER 4: ASTROLOGICAL REGRESSION & MATHEMATICAL VERIFICATION

Astrological accuracy is the core value proposition of Gokul's Astrological Insights. The Android app must produce results identical to the web platform.

#### 5.1 Benchmark Canonical Chart
The test suite executes regression runs against the verified standard benchmark chart:
- **Birth Date:** 1995-10-24
- **Birth Time:** 14:30:00 (IST)
- **Location:** Chennai, Tamil Nadu, India ($13.0827^\circ\text{ N}, 80.2707^\circ\text{ E}$)
- **Ayanamsa:** Lahiri (Chitrapaksha, ID: 0)
- **House System:** Placidus (ID: 2)

#### 5.2 Verification Assertion Criteria
| Parameter | Expected Mathematical Value | Max Allowed Android Discrepancy |
| :--- | :--- | :--- |
| **Ascendant (Lagna)** | Makara (Capricorn) $\approx 287.4^\circ$ | **$0.0000^\circ$ (Exact)** |
| **Sun Longitude** | Thula (Libra) $\approx 186.8^\circ$ | **$0.0000^\circ$ (Exact)** |
| **Moon Longitude** | Thula (Libra), Swati Nakshatra | **$0.0000^\circ$ (Exact)** |
| **Balance of Dasa at Birth** | Rahu Dasa: $\approx 11\text{ Years}, 4\text{ Months}$ | **$0\text{ Days}$ (Exact Day)** |
| **KP Sub-Lord of Cusp 1** | Verified against KP Reader 3 | **Identical Sub-Lord** |
| **D9 Navamsa Sign of Moon** | Dhanus (Sagittarius) | **Identical Sign** |

---

### 6. TIER 5: END-TO-END (E2E) AUTOMATION (MAESTRO)

Maestro is selected for Android E2E testing due to its stability on React Native and zero-flake UI flows.

#### Primary E2E Test Flow (`e2e/mvp-flow.yaml`):
```yaml
appId: com.gokul.astrologicalinsights
---
- launchApp
- assertVisible: "Gokul's Astrological Insights"
# 1. Login Flow
- tapOn: "Email"
- inputText: "test@gai-astrology.com"
- tapOn: "Password"
- inputText: "TestPass123!"
- tapOn: "Sign In"
- assertVisible: "Dashboard"

# 2. Horoscope Creation Flow
- tapOn: "New Horoscope"
- inputText:
    id: "person-name-input"
    text: "Maestro Test Person"
- tapOn: "Date of Birth"
- tapOn: "Confirm"
- tapOn: "Calculate Horoscope"

# 3. Chart Verification Flow
- assertVisible: "D1 Rasi Chart"
- assertVisible: "Planetary Positions"
- tapOn: "D9 Navamsa"
- assertVisible: "D9 Navamsa Chart"

# 4. PDF Download Flow
- tapOn: "Download Tamil PDF"
- assertVisible: "Preparing Report..."
- assertVisible: "Share"
```

---

### 7. DEVICE MATRIX & PRODUCTION RELEASE AUDIT

- **Target OS Range:** Android 10 (API Level 29) through Android 15 (API Level 35).
- **Target Architecture:** `arm64-v8a` (Primary), `armeabi-v7a`, `x86_64` (Emulator).
- **Screen Formats:**
  - Standard Smartphones (5.5" to 6.8", 1080x2400).
  - Small budget devices (720x1600).
  - Android Tablets (7" to 11", split-pane layout).
- **Performance Thresholds:**
  - Chart render time: $< 16\text{ ms}$ (steady 60 FPS).
  - App cold startup time: $< 2.0\text{ seconds}$.
  - Release APK / AAB download size: $< 25\text{ MB}$.
