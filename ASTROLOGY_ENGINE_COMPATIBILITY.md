# GOKUL'S ASTROLOGICAL INSIGHTS
## ASTROLOGY ENGINE COMPATIBILITY & ASTRONOMICAL PRECISION AUDIT

> **Document Version:** 1.0.0  
> **Calculation Engine:** XALEN Ephemeris 0.6.0 (Rust PyO3 Native Module)  
> **Source Verification:** `backend/app/services/ephemeris.py`, `dasa_service.py`, `kp_service.py`, `pdf_report_engine/*`  
> **Accuracy Standard:** High-precision Geocentric Sidereal coordinates validated against Swiss Ephemeris within $0.0001^\circ$ (sub-arcsecond)

---

### 1. BIRTH INPUT & GEOGRAPHIC COORDINATES SPECIFICATION

All calculation requests across Vedic, KP, Dasa, and Varga endpoints consume the standard `BirthInput` schema:

```json
{
  "birth_date": "1995-10-24",
  "birth_time": "14:30:00",
  "timezone": "Asia/Kolkata",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "ayanamsa": 0,
  "house_system": 2,
  "gender": "male"
}
```

#### 1.1 Timezone Handling
- The backend uses Python `zoneinfo` and `dateutil` in `backend/app/services/timezone_utils.py`.
- **Accepted Timezone Formats:**
  1. Standard IANA time zone identifiers (e.g., `"Asia/Kolkata"`, `"America/New_York"`, `"Europe/London"`).
  2. Fixed UTC offset strings (e.g., `"+05:30"`, `"-04:00"`, `"UTC"`).
- Automatically computes Julian Day UT1 and accounts for historical Daylight Saving Time (DST) shifts.

#### 1.2 Coordinate Precision
- Latitude: Decimal degrees from $-90.0^\circ$ to $+90.0^\circ$ (validated by Pydantic `ge=-90.0, le=90.0`).
- Longitude: Decimal degrees from $-180.0^\circ$ to $+180.0^\circ$ (positive East).

---

### 2. CORE CALCULATION ENGINES & API EXPOSURE

#### 2.1 Planetary Positions, Nakshatras & Dignities
- **Engine:** `compute_planetary_positions()` in `ephemeris.py`.
- **Planetary Bodies:** Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu (Mean/True), Ketu, Uranus, Neptune, Pluto.
- **Output Metrics:** Exact Longitude ($0^\circ - 360^\circ$), Sign Index (1 to 12), Sign Name (English & Tamil), Degree in Sign ($0.0^\circ - 30.0^\circ$), Latitude, Speed (Deg/Day), Retrograde status (`is_retrograde: bool`), Nakshatra Index (1 to 27), Nakshatra Name, Pada (1 to 4), Star Lord, Sub Lord.
- **API Status:** **Fully exposed via `POST /api/v1/horoscope/calculate`**.

#### 2.2 D1 (Rasi) and D9 (Navamsa) Charts
- **Engine:** `varga_engine.py` (Varga algorithms based on BPHS Chapter 6).
- **Mathematical Form:**
  - $D_1$ Rasi: Direct sign placement ($\lfloor \lambda / 30^\circ \rfloor + 1$).
  - $D_9$ Navamsa: Division by $3^\circ 20'$ ($200'$ arc). Signs mapped by element triplicity (Movable, Fixed, Dual).
- **API Status:** **Fully exposed via `POST /api/v1/horoscope/varga/d1-d9` and `GET /api/v1/horoscope/varga/d1-d9/{horoscope_id}`**.

#### 2.3 Bhava Chalit & House Systems
- **Engine:** XALEN House Cusp calculator (`app/services/ephemeris.py`).
- **Supported Systems:**
  - `0`: Whole Sign (Traditional Vedic standard).
  - `1`: Equal House.
  - `2`: Placidus (Semi-arc standard required for KP Astrology).
- **Output:** 12 House Cusps with degrees, signs, star lords, and sub-lords.
- **API Status:** **Fully exposed via `POST /api/v1/horoscope/calculate` and `POST /api/v1/horoscope/kp`**.

#### 2.4 Five-Level Vimshottari Dasa Engine
- **Engine:** `backend/app/services/dasa_service.py`.
- **Mathematical Formula:** 120-year cycle initiated by Moon's exact longitude within its natal Nakshatra ($13^\circ 20'$ arc):
  $$\text{Balance Ratio} = 1 - \frac{\lambda_{\text{Moon}} \pmod{13^\circ 20'}}{13^\circ 20'}$$
- **Levels Computed:**
  1. Maha Dasa (Major Period)
  2. Antar Dasa / Bhukti (Sub Period)
  3. Pratyantar Dasa (Sub-Sub Period)
  4. Sookshma Dasa (Sub-Sub-Sub Period)
  5. Prana Dasa (5th level instantaneous period)
- **API Status:** **Fully exposed via `POST /api/v1/horoscope/dasa` and `POST /api/v1/horoscope/dasa/direct`**.

#### 2.5 KP (Krishnamurti Padhdhati) Engine
- **Engine:** `backend/app/services/kp_service.py` & `backend/app/services/kp_engine/*`.
- **Features:**
  - Exact Placidus cusps with ARMC calculation.
  - KP 1-249 and 1-2193 sub-sub division tables.
  - 4-Tier Signification Matrix:
    - Grade A: Planets in the star of occupants of the Bhava.
    - Grade B: Planets occupying the Bhava.
    - Grade C: Planets in the star of the lord of the Bhava.
    - Grade D: Lord of the Bhava.
  - Ruling Planets (RP) at moment of query / birth.
  - Horary (Prashna) 1-249 calculation with Ascendant longitude assignment.
- **API Status:** **Fully exposed via `POST /api/v1/horoscope/kp`, `POST /api/v1/horoscope/kp/horary`, and `POST /api/v1/horoscope/kp/horary-predict`**.

#### 2.6 Horoscope PDF Generation Services
- **Engine:** `backend/app/services/pdf_report_engine/*`.
- **Typography & Complex Script Shaping:** ReportLab combined with `uharfbuzz` and Google Noto Sans Tamil fonts (`NotoSansTamil-Regular.ttf`, `NotoSansTamil-Bold.ttf`) for flawless Tamil vowel ligature rendering without box glyphs.
- **Reports Supported:**
  - 9-page bilingual Vedic horoscope report (Tamil & English).
  - 6-page KP Astrology report (Tamil & English).
  - 6-page traditional Tamil horoscope writing booklet (*Jathaga Kurippu*).
  - Single-page quick chart summary.
- **API Status:** **Fully exposed via `POST /api/v1/reports/horoscope/pdf`, `GET /api/v1/reports/horoscope/pdf/{id}`, and `POST /api/v1/reports/kp/pdf`**.

---

### 3. INTERNAL SERVICES VS API ACCESSIBILITY AUDIT

A critical question of this audit is whether any calculation engine is locked inside internal Python services without an accessible HTTP API:

| Engine | Internal Python Module | Exposed via FastAPI API? | Mobile Ready Status |
| :--- | :--- | :--- | :--- |
| **XALEN Ephemeris Core** | `app.services.ephemeris` | **YES** (`/api/v1/horoscope/calculate`) | Direct API reuse |
| **Vimshottari Dasa (5-levels)** | `app.services.dasa_service` | **YES** (`/api/v1/horoscope/dasa`) | Direct API reuse |
| **Shodashvarga (D1 to D60)** | `app.services.varga_engine` | **YES** (`/api/v1/horoscope/varga/shodashvarga`) | Direct API reuse |
| **Shadbala 6-fold Strength** | `app.services.shadbala_engine` | **YES** (`/api/v1/vedic/shadbala`) | Direct API reuse |
| **Ashtakavarga BAV/SAV/Kaksha**| `app.services.ashtakavarga_engine` | **YES** (`/api/v1/vedic/ashtakavarga/*`) | Direct API reuse |
| **195 BPHS Vedic Yogas** | `app.services.yoga_engine` | **YES** (`/api/v1/vedic/yogas`) | Direct API reuse |
| **Unified Dosha Engine** | `app.services.dosha_engine` | **YES** (`/api/v1/vedic/doshas`) | Direct API reuse |
| **KP Natal & Horary (1-249)** | `app.services.kp_service` | **YES** (`/api/v1/horoscope/kp*`) | Direct API reuse |
| **32 Standard KP Event Rules** | `app.services.kp_event_engine` | **YES** (`/api/v1/horoscope/kp-events/*`) | Direct API reuse |
| **Double Transit Radar** | `app.services.double_transit_engine` | **YES** (`/api/v1/vedic/double-transit`) | Direct API reuse |
| **Medical Astrology Engine** | `app.services.medical_astrology_engine` | **YES** (`/api/v1/vedic/medical-astrology`) | Direct API reuse |
| **Marriage Matching Engine** | `app.services.marriage_engine` | **YES** (`/api/marriage-compatibility/*`) | Direct API reuse |
| **Numerology Suite** | `app.services.numerology` | **YES** (`/api/v1/numerology/*`) | Direct API reuse |
| **Remedies & Pariharam DB** | `app.services.remedy_engine` | **YES** (`/api/v1/remedies/*`) | Direct API reuse |
| **Vastu Shastra Layouts** | `app.services.vastu_service` | **YES** (`/api/v1/vastu/*`) | Direct API reuse |
| **Tamil Horoscope Booklet** | `app.services.horoscope_writing` | **YES** (`/api/v1/tools/horoscope-writing/*`) | Direct API reuse |

**Result:** **100% of the astrology engines are already exposed through well-formed REST APIs in FastAPI.** There are zero calculations trapped in internal-only services.
