# Technical, Astrological & Licensing Audit: KP Events & Prediction Module

**Audited Reference Repository:** [https://github.com/girishbp-wq/KP-Astrology](https://github.com/girishbp-wq/KP-Astrology)  
**Target Platform:** Gokul’s Astrological Insights  
**Auditor:** Antigravity (Google DeepMind Advanced Agentic Coding)  
**Audit Date:** October 18, 2026  
**Status:** Completed (Phase 1: Pre-Implementation Audit)  
**Deliverable Document:** `kp_events_and_prediction_integration_audit.md`  

---

## 1. Executive Summary

An exhaustive technical, astrological, algorithmic, and licensing audit of the repository `girishbp-wq/KP-Astrology` was conducted to determine how its event-timing logic, ruling-planet mechanics, and house-grouping predictions can be safely and legally integrated into **Gokul’s Astrological Insights** as a new, independent dashboard module: **KP Events & Prediction**.

### Core Verdict: CONDITIONAL GO (Strict Clean-Room Architecture Using Native XALEN Engine)

1. **Licensing Barrier (Strict Code Copy Reject):**  
   The reference repository `girishbp-wq/KP-Astrology` **contains NO open-source license file** (no MIT, Apache, GPL, or BSD license). The only license text present in the entire repository is an embedded license header for the third-party JavaScript library `astronomy-engine` by Don Cross (MIT). Under the Berne Convention and GitHub Terms of Service, code in an unfree/unlicensed public repository remains **"All Rights Reserved"** by the author (`girishbp-wq`). **Directly copying, transpiling, or bundling the author's proprietary code into this commercial website is legally prohibited.**
   
2. **Missing Repository Components in Git:**  
   Although the repository's `README.md` describes a dual architecture featuring a Python engine (`kp_engine/`), command-line tool (`kp_cli.py`), and test suite (`tests/test_validation.py`), the git repository contains **only three committed files**: `index.html` (568 KB single-page web app), `Rashis with star lords with Degrees.html` (31 KB), and `README.md`. The Python engine and validation tests were omitted during upload (`Add files via upload`). Consequently, no official Python files or test scripts can be executed directly from the reference clone.

3. **Ephemeris & Ayanamsa Preservation (XALEN Inviolability):**  
   The reference repository uses an approximate cubic polynomial fit for the KP-New (Krishnamurti) ayanamsa and relies on the client-side JavaScript `astronomy-engine`. In contrast, Gokul’s Astrological Insights runs on a high-precision, sub-arcsecond native **XALEN (Rust 0.6.0 / PyO3)** astronomical engine using the standard Chitrapaksha / Lahiri ayanamsa (`SE_SIDM_LAHIRI`, `ayanamsa_id=1`) for its customer horoscopes. **Under no circumstances should the client-side polynomial ayanamsa or a competing ephemeris replace or be mixed into the production calculation flow.**

4. **Astrological Concepts & Algorithms (Clean-Room Adapt):**  
   The reference application's astrological methodology is classical Krishnamurti Paddhati (KSK):
   - **Event Promise:** Evaluated via Cuspal Sub-Lord (CSL) of primary event houses and 4-tier significators (A, B, C, D).
   - **Dasha Gating:** Event fructification requires running Vimshottari Maha Dasha, Bhukti, and Antara lords to signify supporting houses.
   - **Event Date Scanner:** Tracks transit Moon's sign lord, star lord, and sub lord matching Ruling Planets (RP) or significators.
   - **Event Time Window Scanner:** Scans candidate dates for transit Ascendant (Lagna) sign lord, sub lord, and sub-sub lord matching Ruling Planets.
   
   These astrological principles and scanning algorithms can be implemented cleanly, robustly, and natively in Python/FastAPI using our existing XALEN calculation services and presented in Next.js 16 / React 19.

---

## 2. Complete Source & Repository Inventory

The cloned repository at `scratch/KP-Astrology` contains:

```
scratch/KP-Astrology/
├── .git/                                            # Git metadata (commit: 2c26138)
├── index.html                                       # Monolithic Single-Page App (568,905 bytes; 11,947 lines)
│   ├── Lines 1–211: HTML DOM & CSS Layout          # Responsive web UI, form inputs, tabs
│   ├── Lines 212–10020: astronomy-engine.js        # Don Cross astronomy library (MIT License)
│   ├── Line 10021: window.KP_GROUPINGS             # 110 Event Definitions (JSON array)
│   ├── Lines 10022–10589: kp_web.js (KP)           # Sub-lord theory (249 subs), Placidus cusps, Dasha
│   ├── Lines 10590–10811: kp_btr.js (KBTR)         # Geo parsing, Lagna chain, Ruling Planets, BTR
│   ├── Lines 10812–10939: kp_timing.js (KTIME)     # Transit Moon/Lagna event scanner & Dasha gating
│   └── Lines 10940–11947: kp_learn.js & UI App     # Client localStorage feedback & DOM controllers
├── Rashis with star lords with Degrees.html         # Static HTML reference table for Southern chart (31 KB)
└── README.md                                        # Documentation file (14,831 bytes)
```

### Git History Findings
- Initial commit `33eeef3` (Jul 8, 2026): Minimal README.
- Commit `eef8b7a` (Jul 8, 2026): Uploaded monolithic `index.html`.
- Commit `9b337d3` (Jul 19, 2026): Refactored progeny and love marriage logic.
- Commit `2c26138` (Jul 30, 2026): Added `Rashis with star lords with Degrees.html`.
- **Finding:** No Python source files (`kp_engine/`, `kp_cli.py`) or test files (`tests/test_validation.py`) were ever pushed to the GitHub repository.

---

## 3. Intellectual Property, Licensing & Legal Compliance

| Dimension | Reference Repository (`girishbp-wq/KP-Astrology`) | Gokul’s Astrological Insights Policy | Compliance Verdict |
| :--- | :--- | :--- | :--- |
| **Repository License** | **NONE** (No LICENSE file in root or tree) | Commercial / Proprietary platform | ❌ **PROHIBITED** to vendor or copy code |
| **Bundled Libraries** | `astronomy-engine` (Don Cross, MIT) | Not needed; native XALEN ephemeris used | ✅ Clean separation |
| **Astrological Rules** | Classical KP Sub-Lord theory, KSK writings, Placidus semi-arc trigonometry, Vimshottari Dasha | Mathematical/astrological ideas in the public domain | ✅ **PERMISSIBLE** for clean-room implementation |
| **House Groupings** | Standard 12-house KP significations for major life events | Classical Jyotish / KP literature | ✅ Clean-room schema integration |

**Legal Conclusion:** We must not copy code blocks, HTML, or JavaScript from `girishbp-wq/KP-Astrology`. All logic must be built using native Python services and TypeScript components adhering to existing project standards.

---

## 4. Astrological & Technical Verification of Timing Algorithms

### 4.1 Event Promise Evaluation (CSL & Significators)
- **KP Rule:** An event is promised if the Cuspal Sub-Lord (CSL) of the primary house is connected to supporting houses through its star lord or significations.
- **Example (Marriage):** Primary house is 7th. Supporting houses are 2 (family addition), 7 (partnership/spouse), 11 (fulfillment of desires/gain). Denying houses are 1, 6 (12th to 7th), 10.
- **Example (Job):** Primary house is 6 (service) or 10 (profession). Supporting houses are 2, 6, 10, 11. Denying houses are 1, 5 (12th to 6th), 9 (12th to 10th).
- **Example (Childbirth):** Primary house is 5. Supporting houses are 2, 5, 11. Denying houses are 1, 4 (12th to 5th), 10.
- **Promise vs Timing Distinction:** A favorable transit or ruling planet does not cause an event if the natal CSL denies the matter. The engine must explicitly evaluate and report the natal event promise before proceeding to date scanning.

### 4.2 Ruling Planets (RP) Mechanics
- Ruling planets are determined for the **moment and place of query/judgement**:
  1. Lagna Ascendant Star Lord
  2. Lagna Ascendant Rasi (Sign) Lord
  3. Moon Star Lord
  4. Moon Rasi (Sign) Lord
  5. Day Lord (Lord of the weekday from sunrise)
  6. Nodes (Rahu/Ketu) acting as agents of conjoined planets, aspecting planets, or sign lords.
- **Retrograde Filtering Rule:** In KP, an RP that occupies the star of a retrograde planet is deemed weak or rejected. This prevents false positive transit candidates.

### 4.3 Transit Event Scanning Pipeline
1. **Dasha-Bhukti-Antara (DBA) Screening:**
   - Evaluates the running or selected Dasha periods.
   - Lords of Maha Dasha, Bhukti, and Antara must signify supporting houses.
   - Periods that signify denying houses or lack supporting significations are ranked low or flagged as unsupportive.
2. **Transit Moon Scanning (Date Determination):**
   - The Moon passes through the zodiac in ~27.3 days (~13°20' per day).
   - Scans candidate dates in the user's requested date range (e.g., 30–180 days).
   - A date qualifies when transit Moon's sign lord, star lord, and sub lord are active Ruling Planets and/or significators of the event.
3. **Transit Ascendant (Lagna) Scanning (Time Window Determination):**
   - Within each qualifying Moon transit day, the Ascendant completes a 360° rotation in 24 hours.
   - Scans at fine resolution (e.g., 1–5 minutes) to identify windows when transit Lagna sign lord, sub lord, and sub-sub lord match the event significators/ruling planets.
   - This narrows the candidate event timing to specific local clock time windows.

### 4.4 Date Range, Timezone & Edge Cases
- **Timezone Offsets:** Must handle timezone differences between birth place, judgement place, and transit coordinate system.
- **Midnight Boundary:** Scanning across midnight (00:00:00) must transition dates smoothly without losing hours or double-counting days.
- **Leap Days & Daylight Saving Time (DST):** Uses Python `zoneinfo` and XALEN Julian Day conversions to ensure continuity across leap years and DST boundaries.
- **Missing Fructification:** If no candidate passes the threshold within the requested range, the engine must return a clear "No qualifying event window found within the requested range" message rather than inventing a date.

---

## 5. Ayanamsa Comparison: Reference vs Existing XALEN Engine

| Feature | Reference Repository (`index.html`) | Existing XALEN Platform | Architectural Decision |
| :--- | :--- | :--- | :--- |
| **Engine** | `astronomy-engine` JS (Meeus/JPL approximations) | Native `xalen` (Rust 0.6.0 core, C/PyO3 bindings) | **Keep XALEN:** Superior precision, thread-safe, sub-arcsecond accuracy |
| **Ayanamsa Formula** | Cubic polynomial fit (`23.76024 + 1.396888*T + ...`) | High-precision Swiss Ephemeris algorithm in Rust | **Preserve XALEN:** Never use polynomial approximations in backend |
| **Ayanamsa Mode** | KP-New fixed | Standard Chitrapaksha / Lahiri (`ayanamsa_id=1`) with KP (`ayanamsa_id=5`) option | **Preserve User/Chart Configuration:** Do not alter customer horoscope's saved ayanamsa |
| **Placidus Cusps** | Semi-arc iteration in client JS | Native `xalen.swe.houses` (exact equinox Placidus) | **Use Native XALEN Placidus:** 100% verified against validation suite |
| **Sub-Lord Table** | 249 sub-division table generated at runtime | Shared `app.services.kp_engine` 249 subdivisions | **Reuse Existing KP Subdivision Tables** |

---

## 6. Inspection of Existing Application Architecture

### 6.1 Backend Foundations
- **`backend/app/services/kp_engine/`:** Complete 249 sub-division lookup, significator generation (A, B, C, D), Placidus cusps, and Horary 1–249.
- **`backend/app/services/kp_event_engine/`:** 
  - `event_rules.py`: Centralized registry of 32 KP event definitions with supporting/denying houses, primary cusps, gain-type classifications.
  - `period_service.py`: Dasha period extraction from XALEN dasa trees.
  - `scoring_service.py`: Rule-based scoring with Green / Orange / Red grading.
  - `repository.py`: Persistence and retrieval from `public.kp_event_analyses`.
- **`backend/app/services/kp_transit_timeline.py`:** Exact planetary ingress and boundary crossings using XALEN.
- **`backend/app/routers/kp_events.py`:** Existing router handling direct analysis, saved horoscope analysis, and registry retrieval.

### 6.2 Frontend Architecture
- **Next.js 16 App Router & React 19:** Existing tools under `/tools/advanced-kp`, `/tools/transit-watch`, `/tools/horoscope`, and `/dashboard`.
- **Design System:** Consistent theme using `#102A4C` (deep navy), `#B8862B` (gold), `#FAF2DE` (warm cream), and `#E8EEF7` (soft slate). Full Tamil font localization (`font-tamil`).
- **Authentication & RLS:** Supabase JWT authentication (`Bearer` token) with Row Level Security. Users only access their own horoscopes and saved analyses; administrators have elevated access.

---

## 7. Implementation Plan

### Phase 1: Pre-Implementation Audit (COMPLETED)
- Inspect reference repository source, licensing, algorithms, and limitations.
- Document comparison with XALEN and existing modules.
- Publish `kp_events_and_prediction_integration_audit.md`.

### Phase 2: Backend Service Layer (`kp_prediction_service.py` & Schemas)
- Define Pydantic request/response models:
  - `KpPredictionRequest`: `horoscope_id` (or birth details), `event_name`, `start_date`, `end_date`, `scan_resolution_minutes`, `include_ruling_planets`.
  - `KpPredictionResponse`: Event promise evaluation, candidate Dasha periods, ranked candidate dates & time windows, transit evidence, ruling planets evidence, methodology disclaimer.
- Create transit candidate date scanner (Moon transit matching significators/RPs).
- Create Ascendant time window scanner (Lagna transit matching significators/RPs).
- Integrate Dasha-Bhukti-Antara gating.
- Implement ranking score and evidence grade (High, Moderate, Speculative).

### Phase 3: Dedicated Backend Router (`backend/app/routers/kp_prediction.py`)
- `POST /api/v1/kp-prediction/scan`: Run the full promise + Dasha + transit date & time scan.
- `GET /api/v1/kp-prediction/events`: Retrieve all supported event categories with rules.
- Register router in `backend/app/main.py`.

### Phase 4: Frontend Dedicated Module (`/tools/kp-events-prediction`)
- Create page: `frontend/src/app/tools/kp-events-prediction/page.tsx`.
- Include the 6 required UI sections:
  1. **Horoscope Selection:** Choose customer/saved horoscope or input new birth chart with coordinates and timezone validation.
  2. **Event Selection:** Dropdown of supported event categories (Marriage, Job, Promotion, Childbirth, Education, Property, Travel, etc.).
  3. **Event Promise Analysis:** Cuspal Sub-Lord (CSL) details, supporting/conflicting significations, clear astrological rule explanation.
  4. **Dasha-Based Timing:** Maha Dasha, Bhukti, Antara periods with start/end dates and period lords' significations.
  5. **Date & Time Scanner:** Configurable date range, resolution, Moon transit candidate dates, Lagna transit candidate windows.
  6. **Results & Report:** Summary card, evidence grade, transit details, calculation conventions, printable/downloadable summary.
- Add entry to `/tools` directory and dashboard quick-launch cards.
- Add English & Tamil i18n support.

### Phase 5: Automated Testing & Validation
- Unit tests for promise evaluation and significator matching.
- Unit tests for transit date and Lagna time window scanning.
- Integration tests for `/api/v1/kp-prediction/scan` with authentication and ownership verification.
- Regression tests confirming existing KP Advanced, KP Event Analysis, and KP Transit Watch remain unaffected.

---

## 8. Definition of Done Checklist

- [x] Pre-implementation audit completed and documented.
- [ ] No copyrighted/unlicensed code from `girishbp-wq/KP-Astrology` copied into production.
- [ ] XALEN native engine retained as the sole ephemeris provider.
- [ ] Event promise evaluated prior to date scanning.
- [ ] Moon transit dates and Lagna transit time windows calculated dynamically (no mock/hardcoded dates).
- [ ] Dedicated FastAPI router and service implemented with Pydantic typing.
- [ ] Dedicated Next.js 16 frontend module added to dashboard and tools directory.
- [ ] Existing modules (KP Advanced, KP Transit Watch, KP Event Analysis) operational without regression.
- [ ] Authenticated access and user data isolation verified.
- [ ] Test suite passing with 0 regressions.
