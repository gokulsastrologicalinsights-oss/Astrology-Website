# Comprehensive Read-Only Audit & Architectural Blueprint
## Feature: Comprehensive Vedic + KP Marriage Compatibility Engine
**Project:** Gokul's Astrological Insights  
**Audit Date:** October 19, 2026  
**Auditor:** Antigravity (Google DeepMind Advanced Agentic Coding)  
**Status:** PHASE 0 COMPLETED — PENDING APPROVAL TO PROCEED TO PHASE 1  
**Target Repository:** `E:\GAI\Astrology Website`

---

## 1. Executive Summary

This read-only audit establishes the foundational baseline, verified dependencies, reusable components, and architectural boundaries for the proposed **Comprehensive Vedic + KP Marriage Compatibility Engine** within **Gokul's Astrological Insights**.

In accordance with strict project mandates:
- **No code, database schemas, configuration files, or dependencies were altered during this audit.**
- **Zero AGPLv3 or proprietary third-party code contamination:** The implementation will remain 100% clean-room developed using primary classical Sanskrit and Tamil astrological scriptures (*Brihat Parashara Hora Shastra*, *Phaladeepika*, *Muhurta Chintamani*, *Kalaprakasika*, *Kumaraswamiyam*, *Jathaka Alankaram*, *Brihat Samhita*, and K.S. Krishnamurti's *KP Readers*).
- **Core Engine Inviolability:** The native **XALEN 0.6.0 (Rust/PyO3)** ephemeris, Chitrapaksha/Lahiri Ayanamsa, and Placidus/Whole Sign house systems will be reused without modification.
- **KP Engine Inviolability:** The existing KP Events & Prediction module (`app.services.kp_event_engine`), candidate-window selection, and event-scoring mechanisms will remain completely untouched.
- **Baseline Test Verification:** All 417 existing active backend tests passed, 258 validation-suite tests passed, and all 66 frontend test assertions passed with zero regressions.

---

## 2. Baseline Test Execution Results

The entire test suite was executed to record immutable baseline integrity:

### A. Backend Pytest Suite (`backend/tests`)
```
Command: .venv\Scripts\pytest -q
Results: 417 passed, 9 skipped, 128 warnings in 136.71s (100% passing across active tests)
Coverage:
  - Ephemeris & Horoscope calculations: PASS
  - Vimshottari Dasa (5 levels & calendar age): PASS
  - KP Astrology & 249 sub-lord boundaries: PASS
  - KP Event Prediction engine (32 events): PASS
  - KP Transit timeline scanner: PASS
  - D1 Rasi & D9 Navamsa (integer mas precision): PASS
  - Complete 16-chart Shodashvarga engine: PASS
  - Classical Shadbala engine (6 balas): PASS
  - Vedic Yoga engine & cancellation rules: PASS
  - Unified Classical Dosha engine (30 doshas): PASS
  - Vastu Shastra 16-zone Devata mandala: PASS
  - Daily Panchangam & Muhurta finder: PASS
  - Numerology (Traditional & Destiny Matrix): PASS
  - PDF Horoscope report generator (9 pages): PASS
  - Auth, RBAC, and Supabase RLS security: PASS
```

### B. Validation Suite (`validation_suite`)
```
Command: .venv\Scripts\pytest validation_suite -q
Results: 258 passed in 0.84s (100% passing)
Coverage:
  - Sub-arcsecond planetary longitude validation vs Swiss Ephemeris JPL DE431: PASS
  - Lahiri ayanamsa precision (< 1.0" residual): PASS
  - Placidus houses & Ascendant sub-tenth-arcsecond agreement: PASS
  - XALEN Rust-to-Python bindings fidelity: PASS
```

### C. Frontend Automated Suites (`frontend/scripts`)
```
Command: npm --prefix frontend test
Results: 66 passed, 0 failed across 7 automated test suites:
  - Deterministic Chart Correctness (South & North Indian grids): 8 passed
  - Five-Level Dasa & Calendar Age: 10 passed
  - Auth & Security logic: 7 passed
  - Destiny Card Canvas generation: 12 passed
  - Transit Watch UI integration: 15 passed
  - D1 Rasi & D9 Navamsa frontend contracts: 6 passed
  - Vedic Dosha Analysis UI & bilingual dictionary: 8 passed
```

### D. TypeScript Static Verification
```
Command: npm --prefix frontend run type-check
Results: tsc --noEmit exited 0 (Zero TypeScript errors)
```

---

## 3. Existing Architecture and Data Flow

```
                                  +------------------------------------+
                                  |    Next.js 16 + React 19 Frontend  |
                                  |      (Tailwind CSS v4 + i18n)      |
                                  +-----------------+------------------+
                                                    | HTTP REST (JSON)
                                                    v
                                  +------------------------------------+
                                  |        FastAPI Backend Engine      |
                                  |         (app/routers/...)          |
                                  +--------+------------------+--------+
                                           |                  |
                   +-----------------------+                  +-----------------------+
                   v                                                                  v
+--------------------------------------+                           +--------------------------------------+
|       XALEN 0.6.0 Astronomy Engine   |                           |    Supabase PostgreSQL Database      |
|    (Rust Core via PyO3 C-Extension)  |                           |  (Profiles, Horoscopes, RLS, Locks)  |
|  - VSOP87 / ELP2000 Ephemeris        |                           +--------------------------------------+
|  - Chitrapaksha Lahiri Ayanamsa      |
|  - Sub-tenth-arcsecond Houses        |
|  - 27 Nakshatras & 108 Padas         |
|  - 1-249 KP Sub-Divisions            |
|  - Vimshottari 120-Year Dasa Cycle   |
+--------------------------------------+
```

### Existing Data Flow & Authentication
1. **Ad-Hoc Calculation Flow:** Client sends unauthenticated or authenticated birth inputs (`birth_date`, `birth_time`, `timezone`, `latitude`, `longitude`, `ayanamsa_id`, `house_system_id`) to `/api/v1/horoscope/calculate`.
2. **Date & Time Resolution:** `app.services.timezone_utils.resolve_birth_datetime` converts local birth parameters into UTC, evaluates the exact Julian Day (`jd_ut1`), and computes fractional timezone offsets.
3. **Planetary & House Geometry:** `app.services.ephemeris` queries XALEN for geocentric apparent coordinates and generates Placidus/Whole Sign cusps.
4. **Vedic Divisional Extensions:** Coordinates are dispatched to `app.services.varga_engine` where integer milli-arcsecond (mas) arithmetic computes exact D1, D9 Navamsa, and Shodashvarga divisions without IEEE-754 precision drift.
5. **Doshas & Afflictions:** Coordinates are evaluated by `app.services.dosha_engine` (Kuja, Kaal Sarp, Sadesati, Pitru, Guru Chandal, Shrapit, Grahan).
6. **Authentication & Persistence:** When authenticated via Supabase Bearer JWT tokens (`app.services.auth_service`), reports are saved in `saved_horoscopes` with transactional advisory locks (`pg_advisory_xact_lock`) ensuring strict sequential display numbering per user.

---

## 4. Verified Reusable XALEN APIs

All verified XALEN functions reside in the installed `xalen` C-extension compiled from `xalen-ephemeris`:

| Capability | Verified API / Function | Source Location | Input / Output Schema | Calculation Convention | Reusability Status |
|---|---|---|---|---|---|
| **Sidereal Planetary Longitudes** | `xalen.planet_position` | `crates/xalen-python/src/lib.rs` (wrapped in `app/services/ephemeris.py`) | `(jd: f64, body_id: u8, sidereal: bool, ayanamsa: u8) -> dict` | Apparent geocentric sidereal. Returns longitude, latitude, distance, daily speed, retrograde flag. | **Fully Reusable** |
| **Lahiri Ayanamsa** | `xalen.ayanamsa` | `crates/xalen-python/src/lib.rs` | `(jd: f64, system: u8) -> f64` | Chitrapaksha Lahiri (`system=0`). Anchored to Spica at 180°. Sub-arcsecond precision. | **Fully Reusable** |
| **Houses & Ascendant** | `xalen.swe.houses_ex` | `crates/xalen-python/src/swe_compat.rs` | `(jd: f64, lat: f64, lon: f64, hsys: bytes, flags: i32) -> (cusps, ascmc)` | True equinox of date, true obliquity. Supports Whole Sign (`b'W'`), Equal (`b'E'`), Placidus (`b'P'`). | **Fully Reusable** |
| **Nakshatra & Pada** | `xalen.nakshatra` | `crates/xalen-python/src/lib.rs` | `(moon_sidereal_deg: f64) -> dict` | 27 nakshatras, 108 padas (13°20' per nakshatra, 3°20' per pada). Returns index (0-26), name, pada (1-4), lord, deity. | **Fully Reusable** |
| **Moon Sign (Rashi)** | `xalen.rashi` & `get_sign_info` | `xalen-python` & `app/services/ephemeris.py` | `(sidereal_deg: f64) -> (sign_idx 1-12, name_en, name_ta, deg_in_sign)` | 30° per sign starting at 0° Aries. | **Fully Reusable** |
| **D1 & D9 Navamsa** | `calculate_varga_d1_d9` | `app/services/varga_engine.py` | `(planets, ascendant, metadata) -> VargaD1D9Response` | Integer milli-arcsecond (mas) arithmetic. Zero floating-point boundary errors. Evaluates Vargottama, Pushkara Navamsa, Navamsa lords. | **Fully Reusable** |
| **Vimshottari Dasa** | `xalen.vimshottari_dasha` | `crates/xalen-python/src/lib.rs` (wrapped in `app/services/dasa_service.py`) | `(moon_lon: f64, birth_jd: f64, depth: int) -> list[dict]` | 120-year cycle, 365.25-day year convention. Supports up to 5 levels (Maha, Antar, Pratyantar, Sookshma, Prana) with exact calendar age. | **Fully Reusable** |
| **KP Sub-Lords (1-249)** | `xalen.kp_position` | `crates/xalen-python/src/lib.rs` | `(sidereal_deg: f64) -> dict` | Computes sign lord, star lord, sub lord, sub-sub lord, and canonical 1-249 KP number with sign-boundary splits. | **Fully Reusable** |
| **KP Cuspal Analysis** | `xalen.kp_cuspal_analysis` | `crates/xalen-python/src/lib.rs` | `(cusps: list[f64], planets: dict\|list) -> list[dict]` | Evaluates 12 Placidus cusps with sign, star, sub, and sub-sub lords. | **Fully Reusable** |
| **KP Significators** | `xalen.kp_significators` | `crates/xalen-python/src/lib.rs` | `(cusps: list[f64], planets: dict\|list) -> list[dict]` | 4-tier KP strength hierarchy (Grade A: Star of Occupant, Grade B: Occupant, Grade C: Star of Owner, Grade D: Owner, Grade E: Aspecting). | **Fully Reusable** |
| **Shadbala Strengths** | `app.services.shadbala_engine` | `app/services/shadbala_engine/calculator.py` | `(planets, ascendant, houses, panchang, ...) -> ShadbalaResponse` | Full 6 balas (Sthana, Dig, Kala, Cheshta, Naisargika, Drik) for 7 classical grahas with virupas, rupas, and thresholds. | **Fully Reusable** |
| **Parashari Aspects** | `DoshaChartContext` / `YogaChartContext` | `app/services/dosha_engine/models.py` & `yoga_engine` | `(graha_1, graha_2) -> bool` | Mars (4, 7, 8), Jupiter (5, 7, 9), Saturn (3, 7, 10), Sun/Moon/Merc/Venus (7), Rahu/Ketu (5, 7, 9). | **Fully Reusable** |

---

## 5. Verified Reusable KP APIs

The repository contains two mature KP implementations that provide verified APIs:

### 1. Dedicated Python KP Engine (`app/services/kp_service.py` & `app/services/kp_engine/`)
- `calculate_kp_chart(birth, ayanamsa_id=1, house_system_id=2)`:
  - Returns complete 9-planet KP positions (with Star Lord, Sub Lord, Sub-Sub Lord, and KP division 1-249).
  - Returns 12 Placidus cusps with Cuspal Sub-Lord (CSL) and Cuspal Promise classification.
  - Implements 4-tier significators (A, B, C, D) per K.S. Krishnamurti's *KP Reader II*.
  - Implements Ruling Planets (Day Lord, Moon Sign Lord, Moon Star Lord, Lagna Sign Lord, Lagna Star Lord).
  - **Reusability:** Provides exact 7th house Cuspal Sub-Lord and marriage significators for both groom and bride.

### 2. KP Event Prediction Engine (`app/services/kp_event_engine/`)
- In `event_rules.py`, the 32 standard KP events are formally cataloged:
  - **Marriage:** Supporting houses = `[2, 7, 11]`, Denying houses = `[1, 6, 10]`, Primary cusp = `7`.
  - **Divorce / Separation:** Supporting houses = `[1, 6, 10, 12]`, Denying houses = `[2, 7, 11]`, Primary cusp = `6`.
  - **Second Marriage:** Supporting houses = `[2, 7, 9, 11]`, Denying houses = `[1, 6, 8, 10]`, Primary cusp = `9`.
- **Constraint Compliance:** We will **not** modify or fork `kp_event_engine`. Instead, the Marriage Compatibility Engine will consume `event_rules.py` and the existing KP significator calculations via a read-only adapter to evaluate whether the groom's and bride's 7th house Cuspal Sub-Lords and active Dasa periods activate houses 2, 7, 11 or 1, 6, 10.

---

## 6. Existing Compatibility-Related Code & Limitations

The repository contains partial or preliminary references to compatibility, which must be carefully audited to avoid regressions:

### A. Rust Compatibility Module (`xalen-ephemeris/crates/xalen-vedic/src/compatibility.rs`)
- Implements an internal 8-factor Ashtakoota function: `ashtakoota_match(boy_moon_nak, girl_moon_nak, boy_rashi, girl_rashi) -> GunaMatch`.
- **Limitations:**
  1. It is **NOT** exposed to Python in `crates/xalen-python/src/lib.rs` (it cannot be called by FastAPI without modifying XALEN, which is forbidden).
  2. Yoni scoring is simplified to only 3 values (4, 2, 0) instead of the classical 14x14 matrix.
  3. Varna is Nakshatra-based rather than North Indian Rasi-based.
  4. Tara calculates boy-to-girl forward difference rather than girl-to-boy.
  5. Lacks Bhakoot exceptions (same lord, friendly lords).
  6. Lacks Nadi exceptions (same sign different nakshatra, same nakshatra different pada).
  7. Has **zero** Tamil 10 Porutham support.
  8. Has **zero** cross-chart Vedic synastry support.
- **Architectural Decision:** We will **not** modify XALEN Rust code. Instead, we will implement complete, verified, and testable Tamil 10 Porutham and Ashtakoota evaluators in the dedicated Python `marriage_engine` module.

### B. Single-Chart Dosha Engine (`app/services/dosha_engine/catalogue.py`)
- In `catalogue.py` (lines 1900–1935), 4 compatibility doshas are cataloged:
  - 24: `nadi_dosha`
  - 25: `bhakoot_dosha`
  - 26: `gana_dosha`
  - 27: `yoni_dosha`
- In single-chart mode, these return `status="indeterminate"` with `missing_prerequisites="Requires partner horoscope for synastry evaluation"`.
- A baseline regression test (`backend/tests/test_dosha_catalogue_comprehensive.py::test_marriage_compatibility_doshas_indeterminate`) explicitly asserts:
  `assert data["summary"]["total_indeterminate"] == 4`
- **Architectural Safeguard:** We will **NOT** alter the single-chart behavior of `catalogue.py`. The single horoscope endpoint must continue to return 4 indeterminate doshas when evaluated on a solitary chart. The new Marriage Compatibility Engine will be an independent two-chart synastry engine.

### C. Single-Chart Kuja Dosha (`app/services/dosha_engine/kuja_dosha.py`)
- Thoroughly evaluates Kuja Dosha from Lagna (100%), Moon (75%), and Venus (50%) with 8 classical cancellations (BPHS Ch. 81, Muhurta Chintamani).
- **Limitation:** It only evaluates a single chart. It does not evaluate mutual Kuja Dosha balancing between two partners, nor does it calculate Papasamya point differentials.
- **Reusability:** The single-chart Kuja evaluation logic will be reused as a component of the groom's and bride's individual chart evaluations.

### D. Cultural Heuristics Rule Inventory (`app/services/rule_engine.py`)
- Contains draft entries:
  - `RULE-MARR-01`: "Basic Kuja Dosha House Identification" (`status="Draft"`).
  - `RULE-MARR-02`: "Ashtakuta / 10-Porutham Matching" (`status="Requires Verification"`).
- We will update the documentation inventory during implementation to reflect the newly verified, authoritative engine.

### E. Frontend UI Status
- In `frontend/src/app/tools/page.tsx`, the card for "Porutham & Match" ("திருமணப் பொருத்தம்") currently links to `/tools/horoscope`. No dedicated marriage matching interface exists yet.

---

## 7. Missing Functionality Summary

| Required Capability | Current Repository Status | Action Required |
|---|---|---|
| **Dedicated Marriage Engine Namespace** | Absent | Create `app/services/marriage_engine/` |
| **Tamil 10 Poruthams** | Absent | Implement all 10 independent Poruthams with exact counting rules, exception scopes, and Tamil/English explanations. |
| **North Indian Ashtakoota (36 Pts)** | Absent in Python (Rust draft unexposed & incomplete) | Implement complete 8-koota engine with full 14x14 Yoni matrix, raw calculations, intermediate values, and source-backed exceptions. |
| **Vedic Marriage Analysis (D1 & D9)** | Building blocks present, but synastry synthesis absent | Implement 7th house/lord, 2nd/4th/8th/12th houses, Venus & Jupiter analysis, and D9 Navamsa cross-validation. |
| **Kuja Dosha Mutual Balancing** | Single chart present; mutual pair matching absent | Implement cross-chart Kuja Dosha intensity balancing and cancellation. |
| **Papasamya (Malefic Balance)** | Absent | Implement South Indian traditional Papasamya point system for Sun, Mars, Saturn, Rahu, and Ketu. |
| **Nadi & Bhakoot Exceptions** | Absent | Implement documented classical exceptions with rule versions and citations. |
| **Rajju & Vedha Evaluation** | Absent | Implement 5-Rajju classification, Shiro/Kantha/Udara/Kati/Pada, and 12-pair Nakshatra Vedha lookup. |
| **Bidirectional Synastry** | Absent | Implement Groom-to-Bride and Bride-to-Groom overlays. |
| **KP Marriage Analysis Adapter** | KP primitives present; marriage adapter absent | Implement read-only adapter evaluating 7th CSL (2,7,11 vs 1,6,10) and Dasa-Bhukti alignment. |
| **Deterministic Final Assessment** | Absent | Implement explicit, source-backed decision table producing one top-level verdict from documented taxonomy. |
| **API Endpoints** | Absent | Implement `/api/v1/marriage-compatibility/calculate`, `/rules`, `/save`, `/saved`. |
| **Supabase Persistence** | Absent | Add migration `create_saved_marriage_compatibility.sql` with user RLS. |
| **User Interface** | Absent | Build `/tools/marriage-compatibility` with dual birth inputs, bilingual Porutham/Ashtakoota tabs, and saved history. |
| **Automated Test Suite** | Absent | Create comprehensive unit, integration, and regression test suites. |

---

## 8. Calculation & Licensing Integrity

### A. Clean-Room Provenance & Zero AGPL Contamination
- Under no circumstances will any file, algorithm, YAML rule, or structure from `scratch/daiv-ai/` (AGPL-3.0) or any other copyleft repository be imported, copied, or utilized.
- All formulas and astrological tables will be transcribed directly from verified public-domain classical Sanskrit and Tamil texts:
  - *Brihat Parashara Hora Shastra* (BPHS)
  - *Muhurta Chintamani* by Daivajna Ramadayalu
  - *Kalaprakasika* (Canonical South Indian Muhurta & Porutham text)
  - *Kumaraswamiyam* & *Jathaka Alankaram* (Tamil astrological treatises)
  - *Phaladeepika* by Mantreswara
  - *Brihat Samhita* by Varahamihira
  - *KP Readers I, II, III* by Prof. K.S. Krishnamurti

### B. Astronomy Engine Fidelity
- All celestial coordinates, planetary speeds, Julian dates, house cusps, and Dasa hierarchies are derived exclusively from **XALEN 0.6.0** via `app.services.ephemeris`.
- No secondary or unvalidated astronomical library will be introduced.
- Floating-point divisions near cusp boundaries will use the exact integer milli-arcsecond conventions established in `app.services.varga_engine`.

---

## 9. Proposed New Module Boundaries

The implementation will follow the repository's established service architecture:

```
backend/app/services/marriage_engine/
├── __init__.py                     # Package export & versioning
├── models.py                       # Internal dataclasses & enums
├── adapters.py                     # Horoscope-to-synastry context adapter
├── porutham.py                     # Tamil 10 Porutham evaluators
├── ashtakoota.py                   # North Indian 36-point Ashtakoota evaluators
├── papasamya.py                    # South Indian Papasamya malefic point balancer
├── dosha_evaluators.py             # Kuja, Nadi, Bhakoot, Rajju, Vedha exception engine
├── vedic_analysis.py               # D1/D9 houses, lords, Venus/Jupiter significations
├── kp_adapter.py                   # Read-only KP 7th CSL & significator adapter
├── timing.py                       # Dasa-Bhukti marriage timing evaluator
├── assessment.py                   # Deterministic decision matrix & explanation generator
├── repository.py                   # Supabase persistence adapter
└── orchestrator.py                 # Master calculation orchestrator
```

### Supporting Files:
- **Schemas:** `backend/app/schemas/marriage.py` (Pydantic v2 models for requests, intermediate results, and full responses).
- **Router:** `backend/app/routers/marriage.py` (API endpoints).
- **Frontend Page:** `frontend/src/app/tools/marriage-compatibility/page.tsx`.
- **Frontend Components:** `frontend/src/components/marriage/` (Dual birth forms, Porutham grid, Ashtakoota table, Dosha breakdown, Vedic/KP synastry, Final verdict badge).

---

## 10. Proposed API and Data Contracts

### A. Calculate Endpoint
`POST /api/v1/marriage-compatibility/calculate`

```typescript
// Request Schema (supports ad-hoc birth input or saved horoscope references)
interface MarriageCompatibilityRequest {
  groom: {
    saved_horoscope_id?: string;
    birth_input?: BirthInput;
  };
  bride: {
    saved_horoscope_id?: string;
    birth_input?: BirthInput;
  };
  rule_system?: "all" | "tamil_porutham" | "ashtakoota" | "vedic_kp"; // Default: "all"
  ayanamsa_id?: number;       // Default: 0 (Lahiri)
  house_system_id?: number;   // Default: 0 (Whole Sign) or 2 (Placidus)
  include_timing?: boolean;   // Default: true
  include_kp?: boolean;       // Default: true
}
```

```typescript
// Response Schema
interface MarriageCompatibilityResponse {
  metadata: CalculationMetadata;
  groom_summary: PersonChartSummary;
  bride_summary: PersonChartSummary;
  tamil_porutham: {
    individual_poruthams: Record<string, PoruthamResult>; // Dina, Gana, Mahendra, etc.
    total_score: number;       // Earned matches (e.g. 7.5 / 10)
    aggregate_verdict: "Uthama" | "Madhyama" | "Adhama";
    rajju_status: "PASS" | "FAIL";
    vedha_status: "PASS" | "FAIL";
  };
  ashtakoota: {
    kootas: Record<string, KootaResult>; // Varna (1), Vashya (2), Tara (3), Yoni (4), etc.
    total_points: number;      // Earned points (e.g. 24.5)
    max_points: 36;
    nadi_dosha_present: boolean;
    nadi_dosha_cancelled: boolean;
    bhakoot_dosha_present: boolean;
    bhakoot_dosha_cancelled: boolean;
  };
  dosha_analysis: {
    groom_kuja: KujaDoshaResult;
    bride_kuja: KujaDoshaResult;
    mutual_kuja_balance: "BALANCED" | "GROOM_EXCESS" | "BRIDE_EXCESS" | "NEITHER_AFFLICTED";
    groom_papasamya: PapasamyaResult;
    bride_papasamya: PapasamyaResult;
    papasamya_verdict: "FAVORABLE" | "TOLERABLE" | "UNFAVORABLE";
    active_doshas_with_exceptions: DoshaExceptionItem[];
  };
  vedic_analysis: {
    groom_marriage_houses: HouseAfflictionSummary;
    bride_marriage_houses: HouseAfflictionSummary;
    d9_navamsa_synthesis: NavamsaCrossCheck;
    venus_jupiter_disposition: SignificatorRelationship;
  };
  cross_chart_synastry: {
    moon_distance_groom_to_bride: number;
    moon_distance_bride_to_groom: number;
    ascendant_relationship: string;
    venus_mars_interaction: string;
  };
  kp_analysis?: {
    groom_7th_csl: KpCslPromise;
    bride_7th_csl: KpCslPromise;
    significators_agreement: string;
  };
  timing_analysis?: {
    groom_active_dasa: DasaPeriodSummary;
    bride_active_dasa: DasaPeriodSummary;
    conducive_marriage_window: string;
  };
  final_assessment: {
    verdict: "FAVOURABLE_UNDER_SELECTED_RULES" | "MIXED_OR_CONDITIONAL" | "UNFAVOURABLE_UNDER_SELECTED_RULES" | "INDETERMINATE";
    decision_path: string[];
    key_strengths: string[];
    primary_challenges: string[];
    reproducibility_fingerprint: string;
  };
}
```

### B. Rule Inventory Endpoint
`GET /api/v1/marriage-compatibility/rules`
Returns the versioned, auditable Rule Source Register and classical citations.

---

## 11. Database Schema & Migration Conventions

In strict accordance with the existing Supabase migrations:
- New migration file: `supabase/migrations/20261018000010_create_saved_marriage_compatibility.sql`.
- Follows the identical pattern as `saved_horoscopes`, `saved_numerology_reports`, `saved_muhurta_calculations`, `saved_kp_charts`, `kp_event_analyses`, `saved_vastu_reports`, and `saved_remedy_reports`.
- Uses UUID primary keys, user foreign key with `ON DELETE CASCADE`, advisory transactional locks for sequential display numbering (`1, 2, 3...` per user), JSONB calculation snapshot, and strict Row Level Security (RLS) restricting access to the record owner or administrator (`public.is_admin()`).
- Completely additive and reversible (`DROP TABLE IF EXISTS`). Zero modification of existing database tables.

---

## 12. Test Coverage Gaps & Plan

### Existing Gaps Identified:
1. No tests currently evaluate two-horoscope relationships simultaneously.
2. No tests exist for Tamil 10 Porutham calculations or Nakshatra counting.
3. No tests exist in Python for Ashtakoota 36-point calculations.
4. No tests evaluate mutual Kuja Dosha pairing or Papasamya.
5. No tests evaluate cross-chart D1-to-D9 synastry.

### Proposed Test Strategy (Phase 10):
- **Unit Tests (`test_marriage_porutham.py`):**
  - Test all 10 Poruthams with positive, negative, and boundary Nakshatra combinations (e.g. Ashwini to Bharani, Rohini to Mrigashira, identical nakshatras, 27th nakshatra wrap).
  - Test all 5 Rajju categories (Shiro, Kantha, Udara, Kati, Pada) and negative Rajju clashes.
  - Test all 12 Vedha star pairs (e.g. Ashwini vs Jyeshtha).
- **Unit Tests (`test_marriage_ashtakoota.py`):**
  - Test all 8 Kootas individually.
  - Test complete 14x14 Yoni matrix.
  - Test Bhakoot Dosha and all classical cancellation exceptions (same lord, friendly lords).
  - Test Nadi Dosha and exceptions (same nakshatra different pada/rasi).
- **Unit Tests (`test_marriage_doshas_and_papasamya.py`):**
  - Test mutual Kuja Dosha balancing (both afflicted = balanced, only one afflicted = active dosha).
  - Test South Indian Papasamya point allocations across Lagna, Moon, and Venus.
- **Integration Tests (`test_marriage_api_and_persistence.py`):**
  - Test `/api/v1/marriage-compatibility/calculate` with ad-hoc inputs and saved horoscopes.
  - Test deterministic repeat calculations.
  - Test Supabase RLS and multi-user isolation.
  - Verify baseline tests remain 100% green.

---

## 13. Risks & Backward-Compatibility Safeguards

| Risk Identified | Impact | Architectural Safeguard |
|---|---|---|
| **Altering single-chart Dosha engine** | Could break `test_dosha_catalogue_comprehensive.py` line 371 | Keep `app.services.dosha_engine` completely untouched. In single-chart mode, the 4 compatibility doshas remain strictly `indeterminate`. |
| **Mixing Tamil and North Indian scores** | Incompatible astrological systems; creates invalid aggregate scores | Strict separation: Tamil 10 Porutham returned as fractional score (e.g. `7.5 / 10`), Ashtakoota returned as points (e.g. `28 / 36`). They are never added or converted into a single merged point score. |
| **Silent cancellation of Doshas** | High risk of false-positive matchmaking | Every exception must evaluate explicit conditions; cancellation reasons are recorded with classical source citation. If conditions are unmet, dosha remains `DETECTED`. |
| **Database disruption** | Data loss or schema conflicts | Additive migration only. No alterations to existing tables. |
| **KP Event Prediction disruption** | Regressions in existing prediction features | Zero code changes to `app.services.kp_event_engine`. Read-only consumption via dedicated adapter. |

---

## 14. Ordered Implementation Sequence (Phases 1–11)

Upon review and approval of this Phase 0 audit:

- **PHASE 1:** Engine Foundation (`app/services/marriage_engine/`, models, schemas, and XALEN chart context adapters).
- **PHASE 2:** Traditional Tamil 10 Porutham Engine (Dina, Gana, Mahendra, Sthree Deergha, Yoni, Rasi, Rasi Athipathi, Vasya, Rajju, Vedha).
- **PHASE 3:** North Indian 36-Point Ashtakoota Engine (Varna, Vashya, Tara, Yoni 14x14 matrix, Graha Maitri, Gana, Bhakoot + exceptions, Nadi + exceptions).
- **PHASE 4:** Comprehensive Vedic Marriage Analysis (D1 & D9 7th house/lords, 2nd, 4th, 8th, 12th houses, Venus & Jupiter dispositions, Pushkara Navamsa).
- **PHASE 5:** Dosha Rules, Exceptions, Mutual Kuja Balancing, and South Indian Papasamya Engine.
- **PHASE 6:** Bidirectional Cross-Chart Synastry (Groom-to-Bride & Bride-to-Groom overlays).
- **PHASE 7:** KP Marriage Analysis Adapter (Read-only 7th CSL promise and Dasa-Bhukti timing alignment).
- **PHASE 8:** Deterministic Final Assessment (Rule-based decision table and bilingual explanations).
- **PHASE 9:** API Router, Supabase Migration (`20261018000010_create_saved_marriage_compatibility.sql`), and Next.js Frontend (`/tools/marriage-compatibility`).
- **PHASE 10:** Automated Unit, Integration, and Regression Testing (preserving all 417 baseline tests).
- **PHASE 11:** Final Documentation, Verification Report, and Acceptance Demonstration.
