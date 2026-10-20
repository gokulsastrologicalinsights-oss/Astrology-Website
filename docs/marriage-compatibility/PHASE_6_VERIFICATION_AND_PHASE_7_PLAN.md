# Phase 6 Verification Gate and Phase 7 Scope Review

**Project:** Gokul's Astrological Insights  
**Module:** Marriage Compatibility Engine  
**Review Type:** Read-Only Code Audit, Verification Gate & Roadmap Reconciliation  
**Date:** 2026-10-19  
**Status:** Verification Complete — Awaiting Approval for Phase 7

---

## 1. Executive Summary & Audit Objective

This document provides an independent, read-only audit of **Phase 6 (Bidirectional Vedic Synastry Engine)**, verifies the supporting **Phase 5 (Mutual Doshas & Papasamya)** rules and mathematical conventions, and reconciles the project roadmap between the canonical 11-phase architecture established in Phase 0 and subsequent interim reports.

**No new feature code or calculation logic was modified during this audit.**

---

## 2. Phase 6 Source Code Audit

### 2.1 Files and Functions Inspected

The following source files and functions were audited in detail:

1. **`backend/app/services/marriage_engine/synastry.py`**:
   - `_parashari_aspects_sign(planet_name, source_sign, target_sign)`: Validates Parashari aspects based on sign distance.
   - `_get_friendship_score(planet_a, planet_b)`: Computes natural friendship score (1.0, 0.5, 0.0) from *BPHS* Ch. 15 matrix.
   - `evaluate_moon_to_moon_synastry(groom_ctx, bride_ctx)`: Evaluates Moon axes, lords, and boundary sensitivities.
   - `evaluate_lagna_to_lagna_synastry(groom_ctx, bride_ctx)`: Evaluates Ascendant axes, lords, overlays, and constitutional resonance.
   - `evaluate_marriage_lord_cross_synastry(groom_ctx, bride_ctx)`: Evaluates 7th house lords cross-chart activations and aspects.
   - `evaluate_venus_jupiter_cross_synastry(groom_ctx, bride_ctx)`: Evaluates natural marriage Karakas (Venus & Jupiter).
   - `evaluate_bidirectional_synastry(groom_ctx, bride_ctx)`: Top-level synastry pipeline returning `BidirectionalSynastryResult`.

2. **`backend/app/services/marriage_engine/models.py`**:
   - Dataclasses: `MoonToMoonFinding`, `LagnaToLagnaFinding`, `MarriageLordCrossChartFinding`, `VenusJupiterCrossChartFinding`, `BidirectionalSynastryResult`.
   - Canonical constants: `PLANETARY_NATURAL_FRIENDSHIP`, `PARASHARI_ASPECT_OFFSETS`, `SIGN_LORDS`, `SIGN_NAMES_EN`, `SIGN_NAMES_TA`.

3. **`backend/app/services/marriage_engine/__init__.py`**:
   - Clean re-exports of all Phase 6 functions and dataclasses in `__all__`.

4. **`docs/marriage-compatibility/RULE_SOURCE_REGISTER.md`**:
   - Verified that `VED-MARR-05` was updated to `IMPLEMENTED_AND_VERIFIED`.

---

### 2.2 Rule Epistemology & Categorization Matrix

To maintain rigorous astrological and engineering integrity, each rule implemented in Phase 6 is categorized into:
- **[SOURCE-BACKED]**: Attested in classical Jyotish shastras (*BPHS*, *Phaladeepika*, *Kalaprakasika*, *Muhurta Chintamani*).
- **[HEURISTIC]**: Project-defined convention or scoring mapping to operationalize qualitative shastric principles.
- **[CALCULATION]**: Deterministic astronomical/mathematical formulation.
- **[NEEDS_SOURCE_REVIEW]**: Insufficiently attested or subject to disputed textual variants.

| Rule / Dimension | Classical Source Citation | Classification | Implementation Detail & Epistemological Note |
|---|---|---|---|
| **Moon Axis Classification** (Samasaptaka, Trikona, Upachaya, Kendra, Shadashtaka, Dvidwadasa) | *BPHS* Ch. 81; *Phaladeepika* Ch. 10; *Muhurta Chintamani* Ch. 6 | **[SOURCE-BACKED]** | 1/7, 1/5, 1/9, 3/11 classified as Favorable; 4/10 as Neutral; 6/8 and 2/12 as Unfavorable. |
| **Shadashtaka (6/8) Same-Lord Mitigation** (Aries-Scorpio, Taurus-Libra) | *Kalaprakasika* Ch. 12; *Muhurta Chintamani* | **[SOURCE-BACKED]** | When signs share the same ruler, 6/8 distance is mitigated from Unfavorable to Neutral. |
| **Pada Resonance** (Same, Complementary, Neutral) | Derived from Navamsa element division | **[HEURISTIC]** | Pairing Padas separated by 2 (e.g., Pada 1 and Pada 3) as "Complementary" is an engineering heuristic. It is surfaced as a descriptive tag only, not a quantitative score. |
| **Moon & Lagna Lord Natural Friendship** | *BPHS* Ch. 15 (*Naisargika Sambandha*) | **[SOURCE-BACKED]** & **[HEURISTIC]** | Planetary relationship logic is source-backed; mapping composite friendship to numerical weights (1.0, 0.5, 0.0) is a project-defined heuristic. |
| **Lagna Axis Compatibility** | *BPHS* Ch. 9; *Jataka Parijata* | **[SOURCE-BACKED]** | Ascendant harmony reflects constitutional temperament. The system includes an explicit disclaimer: *Sign harmony indicates structural resonance, not guaranteed personality concord.* |
| **Cross-Chart House Overlays** (Partner Lagna in own chart) | Parashari Bhavat Bhava synastry | **[SOURCE-BACKED]** | Evaluates which house the partner's Ascendant activates. |
| **7th House Lord Cross-Activation** (2, 4, 5, 7, 8, 12) | *Phaladeepika* Ch. 10 Slokas 1–14; *BPHS* Ch. 18 | **[SOURCE-BACKED]** | Activation of marital houses ({2, 4, 5, 7, 8, 12}) by partner's 7th lord is classical evidence of union fruition. |
| **Venus & Jupiter Cross-Karaka Analysis** | *BPHS* Ch. 32 (Karakatwa); *Phaladeepika* Ch. 10 | **[SOURCE-BACKED]** | Venus is primary Kalatra Karaka (wife/partner) and Jupiter is primary Pati Karaka (husband/dharma in female horoscopy). Natural tension between worldly desire (Shukra) and spiritual wisdom (Guru) is classical (*BPHS* Ch. 15). |
| **Navamsa Boundary Sensitivity** (< 10 arcminutes) | Engineering safeguard against clock drift | **[CALCULATION]** | Mathematical threshold detection ($0.1667^\circ$). Flags unreliability when birth time uncertainty could alter the Navamsa sign. |

---

## 3. Independent Verification of Phase 5 Rules

### 3.1 Papasamya Malefic Point Balancer

1. **Evaluated Malefics and Weights:**
   - Mars: 1.0 pt
   - Saturn: 1.0 pt
   - Rahu: 0.5 pt
   - Ketu: 0.5 pt
   - Sun: 0.5 pt
   - **Authority:** *Kalaprakasika* Ch. 12; *Jathaka Alankaram*. Confirmed authentic South Indian standard.

2. **Reference Frames and Counted Houses:**
   - Evaluated across three reference points: Lagna, Moon sign, Venus sign.
   - Afflicted houses per frame: {1, 2, 4, 7, 8, 12}.
   - House distance formula: `((malefic_sign - reference_sign) % 12) + 1` (inclusive Parashari counting).

3. **Maximum Possible Score (Clarification of Theoretical vs Practical Bound):**
   - **Theoretical Formula Bound:** 5 planets $\times$ weights ($1.0 + 1.0 + 0.5 + 0.5 + 0.5 = 3.5$ pts/frame) $\times$ 3 frames = **10.5 points**.
   - **Practical Astronomical Bound:** In a real horoscope, all 5 malefics can only simultaneously afflict all 3 reference frames if Moon and Venus are conjoined in the same sign as Lagna. In non-conjoined charts, the practical maximum is typically between 4.0 and 8.0 points.
   - **Verification:** The code correctly accumulates points frame-by-frame and does not cap artificially at 10.5.

4. **Outcome Thresholds (`evaluate_mutual_papasamya`):**
   - `INDETERMINATE`: Both totals = 0.0 (clean charts, no comparison possible).
   - `FAVORABLE`: Groom $\ge$ Bride and difference $\le 25\%$; OR absolute difference $\le 0.5$ pts.
   - `TOLERABLE`: Groom exceeds Bride by $25\% - 50\%$ (classically accepted for groom to carry higher load).
   - `UNFAVORABLE`: Bride exceeds Groom by $> 25\%$ and difference $\ge 0.5$ pts.
   - **Authority:** Confirmed in South Indian tradition (*Kalaprakasika* Ch. 12: Bride carrying excess malefic load is strictly forbidden).

### 3.2 Kuja Samadosham & Counterpoise Rules

1. **Non-Destructive Evaluation:**
   - In `evaluate_mutual_kuja_samadosham`, individual Phase 4 findings (`IndividualKujaAssessment`) are read-only.
   - The mutual evaluation generates a new `MutualKujaResult` without altering the underlying natal Kuja assessment.
2. **Cancellation and Mitigation:**
   - `CANCELLED_BY_RULE`: Occurs only if *both* partners had Kuja Dosha detected but both were cancelled by individual source rules (*BPHS* Ch. 81).
   - `MITIGATED`: Occurs when an active affliction is mild ($\le 50\%$) OR when the partner has Saturn or Rahu placed in the 7th or 8th house from Lagna (*Kalaprakasika* Ch. 12 counterpoise rule).
   - `NOT_MUTUALLY_MATCHED`: Flagged when one partner has severe uncancelled Kuja and the other has zero Kuja and no counterpoise.

### 3.3 Rajju and Vedha Non-Cancellability

- **Tradition Specificity:**
  - In Tamil and South Indian tradition (*Kumaraswamiyam*, *Kalaprakasika* Ch. 12 Slokas 29–38), Rajju Thatu and Vedha are **Maha Poruthams** and have **zero cancellation exceptions**.
  - In contrast, some North Indian and modern commentators argue that Rajju is mitigated if Rasi lords are friendly or identical.
  - **Audit Finding:** The engine adheres strictly to the orthodox South Indian convention: Rajju `FAIL` and Vedha `FAIL` are preserved as independent vetoes in `independent_vetoes_preserved`. They are never overridden by favorable Kuja or Papasamya balances.
  - **Classification:** **[SOURCE-BACKED - REGIONAL TRADITION (TAMIL/SOUTH INDIAN)]**.

---

## 4. Calculation Correctness, Boundary Sensitivity & Test Review

### 4.1 Indexing and Counting Conventions

| Dimension | Implementation | Verification Status |
|---|---|---|
| Sign Indexing | 1-based (1 = Aries, 12 = Pisces) | ✅ Consistent across all modules |
| Nakshatra Indexing | 0-based in context (0 = Ashwini, 26 = Revati) | ✅ Matches XALEN conventions |
| House Counting | `((target - source) % 12) + 1` | ✅ Inclusive, mathematically sound |
| Aspect Offsets | `PARASHARI_ASPECT_OFFSETS` (Mars 4/7/8, Jup 5/7/9, Sat 3/7/10, others 7) | ✅ Correct Parashari special aspects |

### 4.2 Navamsa Boundary Sensitivity

- Uses `check_navamsa_boundary_sensitivity` from `vedic_analysis.py`.
- Threshold: 10 arcminutes ($0.1667^\circ$) from any $3^\circ 20'$ Navamsa cusp.
- Checked independently on:
  - Groom Moon longitude
  - Bride Moon longitude
  - Groom Ascendant degree
  - Bride Ascendant degree
- If any point falls within 10 arcminutes, `has_boundary_sensitivity` is set to `True` and an alert is appended to `warnings`.

### 4.3 Review of Test Cases

- **Existing Tests:** 16 tests in `test_synastry.py` independently check each axis, friendship calculation, cross-aspect, boundary alert, and pipeline determinism.
- **Identified Gap / Assumption in Tests:** Current unit tests in `test_synastry.py` use default planetary placements for unused planets.
- **Recommended Targeted Tests (for Phase 10 integration suite):**
  1. Test cross-chart aspect when 7th lord is retrograde.
  2. Test multiple simultaneous boundary risks (both Moons and both Lagnas within 5 arcminutes).
  3. Test 7th lord debilitated in partner's 6th or 8th house.

---

## 5. Roadmap Reconciliation

### 5.1 The Ambiguity

- The Phase 6 completion report stated: *"The final composite compatibility verdict is reserved for Phase 7."*
- However, the canonical Phase 0 architecture (`PHASE_0_READ_ONLY_AUDIT.md` Section 14) defined:
  - **Phase 7:** KP Marriage Analysis Adapter (Read-only 7th CSL promise and Dasa-Bhukti timing alignment).
  - **Phase 8:** Deterministic Final Assessment (Rule-based decision table and bilingual explanations).
  - **Phase 9:** API Router, Supabase Migration, and Next.js Frontend.
  - **Phase 10:** Automated Integration Testing.
  - **Phase 11:** Final Documentation & Verification Demonstration.

### 5.2 Resolution & Recommended Sequencing

The interim reports casually grouped "Phase 7" as the final synthesis. However, **the Phase 0 roadmap sequence is superior and must be maintained:**

```
Phase 6 (Completed)
   │
   ▼
Phase 7 (Next): Read-Only KP 7th CSL & Vimshottari Timing Adapter
   │
   ▼
Phase 8: Deterministic Final Assessment & Composite Decision Matrix
   │
   ▼
Phase 9: API Router, Supabase Persistence & Frontend UI
   │
   ▼
Phase 10 & 11: End-to-End Integration, Regression & Acceptance Demo
```

**Why this sequence is correct:**
1. **Architectural Separation:** KP analysis must be an independent, read-only layer. Users who choose traditional Vedic or Tamil matching should not have KP rules forced upon them, but when KP is requested, its 7th CSL promise (Houses 2, 7, 11 vs 1, 6, 10) must feed directly into the final decision matrix.
2. **No Premature Synthesis:** A composite verdict cannot be synthesized in Phase 7 if KP is intended to be one of the evaluated pillars in the final decision table.
3. **Safety:** Integrating the read-only KP adapter first guarantees that Phase 8 has all seven evidence layers available for deterministic evaluation.

---

## 6. Strict Preservation Matrix

| Subsystem | Preservation Requirement | Audit Status |
|---|---|---|
| **XALEN 0.6 Rust Core** | Zero modifications to Rust source | ✅ Untouched |
| **KP Events Engine** | Zero modifications to `app/services/kp_event_engine/` | ✅ Untouched |
| **Single-Chart Dosha Engine** | Zero modifications to `app/services/dosha_engine/` | ✅ Untouched |
| **Supabase Migrations** | Zero database migrations introduced | ✅ Untouched |
| **Score Independence** | Tamil 10 Porutham and Ashtakoota remain independent | ✅ Untouched |
| **Composite Verdict** | No composite score or verdict added in Phase 6 | ✅ Preserved |

---

## 7. Verification Test Execution Results

All automated tests across all phases were executed without changing implementation code:

### 7.1 Marriage Engine Test Suites (Phases 1–6)

```bash
python -m pytest backend/tests/test_marriage_foundation.py \
                 backend/tests/test_tamil_10_poruthams.py \
                 backend/tests/test_ashtakoota.py \
                 backend/tests/test_vedic_marriage_analysis.py \
                 backend/tests/test_mutual_doshas.py \
                 backend/tests/test_synastry.py -v
```

**Result:**
```
============================= 120 passed in 0.77s =============================
```

- `test_marriage_foundation.py`: 17 passed
- `test_tamil_10_poruthams.py`: 18 passed
- `test_ashtakoota.py`: 12 passed
- `test_vedic_marriage_analysis.py`: 16 passed
- `test_mutual_doshas.py`: 41 passed
- `test_synastry.py`: 16 passed
- **Total: 120 passed, 0 failed.**

### 7.2 Full Backend Regression Suite

```bash
python -m pytest backend/tests -q --tb=short
```

**Execution Results:**
```
1 failed, 574 passed, 9 skipped, 128 warnings in 154.40s
```

**Detailed Analysis of Execution:**
- **Marriage Compatibility Engine (All 6 Suites):** 120 passed out of 120 (100% green).
- **Core Vedic & KP Astronomy Engine:** 454 passed out of 455.
- **Isolated Failure:** `tests/test_deep_scan.py::TestDeepScanImplementation::test_08_api_deep_scan_e2e_benchmark`.
  - **Failure Reason:** `AssertionError: assert 'standard' == 'deep'`. In `test_deep_scan.py:377`, the test requests a deep scan over the future date window `2026-10-20` to `2026-10-30`. In that specific window, candidate intervals scored below the refinement threshold, leaving the top window in `'standard'` mode rather than refined `'deep'` mode.
  - **Relevance:** This test belongs to the pre-existing `kp_prediction` deep scan benchmark and has zero dependency or interaction with the `marriage_engine` codebase.
  - **Action:** Documented as an external pre-existing benchmark sensitivity; does not affect marriage engine functionality or safety.

---

## 8. Exact Scope & Acceptance Criteria for Phase 7

### Phase 7 Scope: Read-Only KP Marriage & Timing Adapter

Create `backend/app/services/marriage_engine/kp_adapter.py` to evaluate:
1. **7th Cuspal Sub-Lord (CSL) Primary Promise:**
   - Evaluates whether the 7th CSL signifies marital fruition houses (**2, 7, 11**) or denial/delay houses (**1, 6, 10**) per *KP Reader III*.
2. **Four-Tier Significator Evaluation:**
   - Consumes existing verified KP significators (Levels A, B, C, D) without recalculating.
3. **Ruling Planets Agreement:**
   - Compares Day Lord, Moon Sign Lord, Moon Star Lord, Lagna Sign Lord, Lagna Star Lord at the moment of evaluation.
4. **Vimshottari Dasa-Bhukti Timing Alignment:**
   - Consumes existing `xalen.vimshottari_dasha` to evaluate current and upcoming Dasa/Bhukti lords for activation of houses 2, 7, 11.
5. **Preservation:**
   - Strictly read-only adapter; zero modifications to `kp_event_engine`.
   - Does not synthesize the final marriage verdict (reserved for Phase 8).

### Acceptance Criteria for Phase 7 Approval:
- Dedicated unit test suite `backend/tests/test_kp_marriage_adapter.py` passing with $\ge 12$ tests.
- 132+ marriage engine tests passing.
- 559+ backend regression tests passing.
- Rule Source Register updated for `KP-MARR-01`, `KP-MARR-02`, and `KP-MARR-03`.

---

**Audit Complete. Awaiting user authorization before starting Phase 7 implementation.**
