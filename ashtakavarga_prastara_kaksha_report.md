# Feature 2 Report — Ashtakavarga Prastara & Kaksha Extensions

**Author:** Antigravity AI  
**Date:** 2026-10-18  
**Roadmap Track:** Daiv AI Feature Extraction — Phase 3 (Feature 2 of 6)  
**Status:** COMPLETE & INDEPENDENTLY VALIDATED  
**Baseline Test Result:** 310 passed, 9 skipped, 0 failed  

---

## 1. Executive Summary

As part of the approved roadmap for feature extraction from `master12coder/daiv-ai`, **Feature 2: Ashtakavarga Prastara and Kaksha Extensions** has been independently designed, implemented, and mathematically verified.

The existing Ashtakavarga service already provided Bhinnashtakavarga (BAV), Sarvashtakavarga (SAV), and BPHS Shodhana reductions (Trikona, Ekadhipatya, Shodhya Pinda). Feature 2 extends this architecture with:
1. **Prastarashtakavarga (Spread-out Matrix):** An 8-donor $\times$ 12-sign binary contribution grid for all 7 classical planets, structured in the canonical Kaksha speed sequence.
2. **Kaksha Vibhaga (Sign Octants):** Full 96-division transit grids ($12 \text{ signs} \times 8 \text{ divisions of } 3^\circ 45'$), mapping each $3.75^\circ$ segment to its planetary/Lagna lord.
3. **Kaksha Transit Evaluator:** An evaluation engine that scores whether a transiting planet's exact degree falls into a benefic (bindu $= 1$) or malefic/obstructive (rekha $= 0$) Kaksha according to the natal Prastara matrix.
4. **Dedicated REST API Endpoints:** Clean endpoints for Prastara matrices, Kaksha grids, and real-time transit evaluations, plus optional inclusion in the master `/api/v1/vedic/ashtakavarga` response.

All implementations strictly adhere to clean-room engineering standards: zero lines of code or assets were copied from AGPLv3 sources. The XALEN ephemeris and dedicated KP engine remain 100% untouched.

---

## 2. Classical Canon & Mathematical Formulas

### 2.1 Classical References
- **Brihat Parashara Hora Shastra (BPHS)**:
  - Chapter 66: *Ashtakavarga Vidhana* (Rules of beneficial points from 8 donors).
  - Chapter 67: *Kaksha Vibhaga* (Subdivisions and transit fruition).
- **Dr. B.V. Raman**: *Ashtakavarga System of Direction*, Chapters 5 (*Prastara Ashtakavarga*) and 6 (*Gocharaphala / Transits*).

### 2.2 Canonical 8-Donor Sequence (Kaksha Order)
In classical astrology, the eight donors are ordered strictly by descending geocentric orbital speed (from the slowest planetary motion to the fastest, terminating with the Ascendant/Lagna):

$$\text{Donor Sequence} = [\text{Saturn}, \text{Jupiter}, \text{Mars}, \text{Sun}, \text{Venus}, \text{Mercury}, \text{Moon}, \text{Lagna}]$$

| Kaksha # | Lord | Span in Sign | Degree Range (Dec) |
|---|---|---|---|
| 1 | **Saturn** | $00^\circ 00' - 03^\circ 45'$ | $0.0000^\circ - 3.7500^\circ$ |
| 2 | **Jupiter** | $03^\circ 45' - 07^\circ 30'$ | $3.7500^\circ - 7.5000^\circ$ |
| 3 | **Mars** | $07^\circ 30' - 11^\circ 15'$ | $7.5000^\circ - 11.2500^\circ$ |
| 4 | **Sun** | $11^\circ 15' - 15^\circ 00'$ | $11.2500^\circ - 15.0000^\circ$ |
| 5 | **Venus** | $15^\circ 00' - 18^\circ 45'$ | $15.0000^\circ - 18.7500^\circ$ |
| 6 | **Mercury** | $18^\circ 45' - 22^\circ 30'$ | $18.7500^\circ - 22.5000^\circ$ |
| 7 | **Moon** | $22^\circ 30' - 26^\circ 15'$ | $22.5000^\circ - 26.2500^\circ$ |
| 8 | **Lagna** | $26^\circ 15' - 30^\circ 00'$ | $26.2500^\circ - 30.0000^\circ$ |

### 2.3 Mathematical Invariants & Reconciliations
For each target planet $P \in \{\text{Sun}, \text{Moon}, \text{Mars}, \text{Mercury}, \text{Jupiter}, \text{Venus}, \text{Saturn}\}$:

1. **Column Total Invariant (Prastara $\leftrightarrow$ BAV):**  
   For any zodiac sign index $s \in \{1 \dots 12\}$, the sum across all 8 donors in the Prastara matrix must equal the BAV bindus for sign $s$:
   $$\sum_{d \in \text{Donors}} \text{Prastara}[P][d][s] = \text{BAV}[P][s]$$

2. **Row Total Invariant (Donor Rule Reconciliation):**  
   For any donor $d$, the sum across all 12 signs equals the exact number of auspicious houses prescribed for donor $d$ in *BPHS*:
   $$\sum_{s=1}^{12} \text{Prastara}[P][d][s] = |\text{BeneficHouses}(P, d)|$$

3. **Matrix Total Invariant:**  
   $$\sum_{s=1}^{12} \sum_{d \in \text{Donors}} \text{Prastara}[P][d][s] = \text{ExpectedTotal}[P]$$
   - Sun: 48, Moon: 49, Mars: 39, Mercury: 54, Jupiter: 56, Venus: 52, Saturn: 39.

4. **Grand Total Invariant:**  
   $$\sum_{P \in \text{Planets}_7} \text{TotalBindus}(\text{Prastara}[P]) = 337$$

### 2.4 Kaksha Transit Evaluation Rule
When planet $P$ transits sign $S$ at degree $D \in [0^\circ, 30^\circ)$:
1. Active Kaksha index $k = \lfloor D / 3.75^\circ \rfloor$. Kaksha number $K = k + 1 \in \{1 \dots 8\}$.
2. Kaksha ruler $L = \text{KAKSHA\_CONTRIBUTOR\_ORDER}[k]$.
3. Query natal Prastara: $\text{has\_bindu} = (\text{Prastara}[P][L][S] == 1)$.
4. If $\text{has\_bindu} == \text{True}$: Transit is **Auspicious** (favorable fruits, obstruction-free period).
5. If $\text{has\_bindu} == \text{False}$: Transit is **Inauspicious** (delays, obstacles, diminished benefic results).

---

## 3. Architecture & Implementation Details

### 3.1 Schema Layer (`backend/app/schemas/ashtakavarga.py` & `horoscope.py`)
- `PrastaraRow`: Contains `contributor: str`, `sign_bindus: Dict[int, int]` (0 or 1), and `total_contributions: int`.
- `PrastaraDetail`: Full matrix with 8 rows ordered in Kaksha sequence, column `sign_totals`, and `total_bindus`.
- `PrastaraResponse`: API response containing `prastara: Dict[str, PrastaraDetail]`, `grand_total_bindus: 337`, and `validation_status: "PASSED"`.
- `KakshaDivisionInfo`: Individual $3^\circ 45'$ span with `kaksha_number`, `lord`, `start_degree`, `end_degree`, `range_display`, and `has_bindu`.
- `PlanetKakshaSignDetail`: 8 divisions per sign, sign name, and `total_bindus` matching BAV.
- `KakshaTransitQuery` & `KakshaTransitResult`: Query and result models for evaluating any transit position.
- `KakshaTransitEvaluationRequest`: Extends `HoroscopeRequest` with a `transit: KakshaTransitQuery` field.
- `KakshaResponse`: Complete 96-division breakdown for all 7 grahas.
- `AshtakavargaResponse`: Extended with optional `prastara` and `kaksha_grids` fields.

### 3.2 Calculation Engines
- **`backend/app/services/ashtakavarga_engine/prastara.py`**:
  - `compute_planet_prastara(target_planet, contributor_signs)`: Generates the 8-donor $\times$ 12-sign matrix, verifying individual row totals and column totals.
  - `compute_all_prastara_matrices(contributor_signs)`: Generates Prastara for all 7 classical grahas.
- **`backend/app/services/ashtakavarga_engine/kaksha.py`**:
  - `get_kaksha_division_for_degree(degree_in_sign)`: Constant-time boundary determination and formatting.
  - `build_planet_kaksha_grid(planet_name, prastara_detail)`: Maps Prastara matrices into 96 structured Kaksha divisions.
  - `build_all_kaksha_grids(prastara_dict)`: Builds Kaksha grids for all 7 planets.
  - `evaluate_kaksha_transit(...)`: Resolves absolute longitude or sign+degree and computes auspiciousness against natal Prastara.
- **`backend/app/services/ashtakavarga_engine/calculator.py`**:
  - Enhanced `calculate_ashtakavarga()` with `include_prastara=True, include_kaksha=True` parameters, maintaining backward compatibility while enriching default responses.

### 3.3 API Endpoints (`backend/app/routers/vedic_extensions.py`)
1. `POST /api/v1/vedic/ashtakavarga`: Returns BAV, SAV, Shodhana, and enriched with `prastara` and `kaksha_grids`.
2. `POST /api/v1/vedic/ashtakavarga/prastara`: Dedicated endpoint returning complete 8 $\times$ 12 Prastara matrices for all 7 planets.
3. `POST /api/v1/vedic/ashtakavarga/kaksha`: Dedicated endpoint returning full 96-division Kaksha breakdown.
4. `POST /api/v1/vedic/ashtakavarga/kaksha/transit`: Dedicated endpoint evaluating transiting planet degree/sign against natal Kaksha bindus.

---

## 4. Verification & Test Outcomes

### 4.1 Test Suites Executed

| Suite | File | Tests Run | Result |
|---|---|---|---|
| **Ashtakavarga Core** | `backend/tests/test_ashtakavarga_engine.py` | 5 | **5 PASSED** |
| **Prastara & Kaksha Tests** | `backend/tests/test_ashtakavarga_prastara_kaksha.py` | 7 | **7 PASSED** |
| **Shadbala Regression Check** | `backend/tests/test_shadbala_engine.py` | 14 | **14 PASSED** |
| **Full Regression Suite** | `backend/tests/` (entire suite) | 319 | **310 PASSED, 9 SKIPPED, 0 FAILED** |

### 4.2 Test Coverage Highlights
- **Reconciliation with BAV:** Checked all $7 \times 12 = 84$ sign columns across all 7 planets; column sum verified identical to BAV sign bindus in every case.
- **337 Grand Total Invariant:** Grand sum across all 7 Prastara matrices verified to equal 337.
- **Kaksha Boundary Tests:** Checked boundaries at $0.0^\circ$, $3.7499^\circ$, $3.7500^\circ$, $7.4999^\circ$, $7.5000^\circ$, $11.25^\circ$, $15.00^\circ$, $18.75^\circ$, $22.50^\circ$, $26.25^\circ$, $29.9999^\circ$, and $30.0^\circ$.
- **Transit Auspiciousness:** Tested transit evaluation for Sun, Jupiter, and others across all 8 Kakshas, confirming correct mapping to `Auspicious` (bindu 1) and `Inauspicious` (rekha 0).
- **API Acceptance:** Tested `/prastara`, `/kaksha`, and `/kaksha/transit` using FastAPI `TestClient`.

---

## 5. Changed and Added Files

| File | Change Type | Description |
|---|---|---|
| `backend/app/schemas/ashtakavarga.py` | Modified | Added `PrastaraRow`, `PrastaraDetail`, `PrastaraResponse`, `KakshaDivisionInfo`, `PlanetKakshaSignDetail`, `KakshaTransitQuery`, `KakshaTransitResult`, `KakshaResponse`, and updated `AshtakavargaResponse`. |
| `backend/app/schemas/horoscope.py` | Modified | Added `KakshaTransitEvaluationRequest`. |
| `backend/app/services/ashtakavarga_engine/prastara.py` | **New** | Clean-room implementation of 8-donor $\times$ 12-sign Prastara matrix and 337-invariant validation. |
| `backend/app/services/ashtakavarga_engine/kaksha.py` | **New** | Clean-room implementation of 96-Kaksha division grids and transit auspiciousness evaluation. |
| `backend/app/services/ashtakavarga_engine/calculator.py` | Modified | Integrated `include_prastara` and `include_kaksha` options into `calculate_ashtakavarga()`. |
| `backend/app/services/ashtakavarga_engine/__init__.py` | Modified | Exported Prastara and Kaksha public interfaces. |
| `backend/app/routers/vedic_extensions.py` | Modified | Added `/ashtakavarga/prastara`, `/ashtakavarga/kaksha`, and `/ashtakavarga/kaksha/transit` endpoints. |
| `backend/tests/test_ashtakavarga_prastara_kaksha.py` | **New** | 7 comprehensive mathematical and API verification tests. |
| `ashtakavarga_prastara_kaksha_report.md` | **New** | Feature documentation and verification deliverable. |

---

## 6. Constraints & Safety Adherence Check

- [x] **XALEN Preserved:** XALEN ephemeris remains the sole planetary-position engine.
- [x] **KP Engine Preserved:** Dedicated KP engine, transit timeline, and prediction services untouched.
- [x] **Existing BAV/SAV/Shodhana Preserved:** All 5 pre-existing Ashtakavarga tests pass without modification.
- [x] **Clean-Room Logic:** 100% independent formulas derived directly from *BPHS* and B.V. Raman; zero code or assets copied from AGPLv3 `daiv-ai`.
- [x] **Test Baseline Maintained & Extended:** Clean pass on 310 tests (9 skipped, 0 failures), strictly up from 303.
- [x] **Zero Database / Schema Mutations:** No Supabase migration or tables altered.

---

## 7. Next Feature in Roadmap

**Phase 3, Feature 3: Yoga Detection and Cancellation Enhancements**
(Awaiting user review and approval before proceeding).
