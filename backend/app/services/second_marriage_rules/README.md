# Isolated KP Second-Marriage Rules Module

Deterministic, read-only implementation of the three extracted Krishnamurti Paddhati (KP) second-marriage rules.

## 1. Overview & Provenance

This module provides a standalone, side-effect-free evaluator for the three classical KP rules governing second-marriage indications. It integrates with existing canonical KP chart calculations via a read-only adapter without mutating chart context or altering production databases.

### Classical Citations & Extracted Texts

| Rule | Classical Identifier | Exact Extracted Text |
|---|---|---|
| **Rule 1** | `KP-SM-RULE-1` | *"The 7th cusp sub-lord is deposited in Gemini, Virgo, or Pisces, OR the 7th cusp sub-lord is Mercury or Jupiter; AND the 7th cusp sub-lord signifies house 2 or house 11, or both."* |
| **Rule 2** | `KP-SM-RULE-2` | *"The 2nd cusp sub-lord signifies house 7 or house 11."* |
| **Rule 3** | `KP-SM-RULE-3` | *"The 9th cusp sub-lord signifies house 2, house 9, or house 11."* |

---

## 2. Rule Specifications & Classical Assumptions

### Rule 1 — 7th Cusp Sub-Lord
Evaluates the 7th cuspal sub-lord (CSL) under an exact two-part boolean condition:
- **Condition A (Planet or Sign):**
  - The CSL planet is `Mercury` or `Jupiter`, **OR**
  - The CSL planet is deposited in zodiac sign `Gemini`, `Virgo`, or `Pisces`.
  - *Strict Fidelity Note:* Sagittarius is intentionally **excluded** from the sign list to adhere strictly to the extracted source text.
- **Condition B (Significations):**
  - The CSL planet signifies house 2 (addition to family) or house 11 (fulfillment of partnership desires).
- **Resolution:**
  - Passes if and only if **Condition A is True AND Condition B is True**.
  - If required input data (sub-lord, deposited sign, or significators) is missing, evaluates to `INDETERMINATE`.

### Rule 2 — 2nd Cusp Sub-Lord
- **Condition:** 2nd CSL signifies house 7 (partner/spouse) or house 11 (fulfillment).
- **Assumption:** House 2 represents *Kutumbasthana* (expansion of family). Connection to the primary partnership house (7) or permanent union house (11) signals another marital bond.

### Rule 3 — 9th Cusp Sub-Lord
- **Condition:** 9th CSL signifies house 2, 9, or 11.
- **Classical Assumption:** Under classical *Bhavat Bhava* doctrine, the 9th house serves as the primary significator of the second spouse because the second spouse is traditionally conceived in the context of the first spouse's younger sibling (3rd house counted from the 7th house = 9th house).

---

## 3. Architecture & Safety Guarantees

1. **Non-Destructive Read-Only Adapter (`adapt_kp_chart_data`):**
   - Ingests `KpResponse` instances or chart dictionaries (`calculation_result.kp`).
   - Normalizes cusps (2, 7, 9), planetary positions, and 4-tier ABCD significators.
   - Operates strictly on copies without modifying input objects or database records.

2. **Independence:**
   - Does not alter `kp_prediction_service.py`, `kp_event_engine/event_rules.py`, or `kp_engine/significators.py`.
   - Results are isolated under the `backend/app/services/second_marriage_rules/` namespace.

3. **Combined Interpretation Policy (`RULES_SUMMARY_ONLY`):**
   - Rules are evaluated independently. No arbitrary composite formula is imposed.
   - The summary verdict is explicitly typed as `RULES_SUMMARY_ONLY`.

4. **Event Engine Comparison Helper (`compare_with_existing_event_engine`):**
   - Documents divergence between this classical 3-rule module and the project's existing event engine (`EVENT_REGISTRY["Second marriage"]`).
   - *Key differences:* The existing event engine checks only Cusp 9, includes House 7 in its supporting set, and applies separating house penalties (`1, 6, 8, 10`).

---

## 4. Epistemological Notice

Passing or failing a software test confirms that the chart data meets or fails the specific astrological criteria encoded from the classical source. It does **not** constitute an empirical or scientific prediction of real-world marital history.
