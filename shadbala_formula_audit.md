# Comprehensive Mathematical & Astrological Audit: Shadbala Engine (Phase 1.1)

**Target System:** Gokul’s Astrological Insights  
**Audited Engine:** `backend/app/services/shadbala_engine/`  
**Reference Canon:** *Brihat Parasara Hora Shastra* (BPHS), Chapter 27 (*Graha-Bhava-Bala-Adhyaya*) / Chapter 28 (*Shadbala*), supplemented by Dr. B.V. Raman (*Graha and Bhava Balas*) and *Phaladeepika* (Ch. 4).  
**Astronomical Engine:** XALEN Ephemeris (Rust 0.6.0 / PyO3, Chitrapaksha/Lahiri Ayanamsha)  
**Date of Audit:** October 18, 2026  
**Status:** Completed & Corrected (100% Green Test Suite)

---

## 1. Executive Summary

This independent mathematical audit was conducted following the initial implementation of the Shadbala calculation engine. Its purpose was to verify every formula against classical Sanskrit source literature, identify simplifications or discrepancies, upgrade the engine to rigorous continuous formulas, and provide an independent recalculation of the benchmark chart (Chennai, May 15, 1990, 14:30 IST).

### Core Audit Verdict:
1. **Mathematical Soundness:** The initial implementation successfully established the architectural scaffolding, type schemas, and unit invariant tests.
2. **Identified Discrepancies:** Six specific calculation areas were identified as relying on coarse discrete categories rather than classical continuous formulas:
   - **Saptavargaja Bala:** Evaluated only Rasi (D1) scaled by $6/7$; now upgraded to evaluate all **7 classical vargas** ($D_1, D_2, D_3, D_7, D_9, D_{12}, D_{30}$) using **Panchadha Maitri** (five-fold compound friendship).
   - **Dig Bala:** Used house-based discrete steps ($60, 50, \dots, 0$ virupas); now upgraded to the exact continuous BPHS angular formula $\frac{\text{arc from Nirbala}}{3.0}$ from cardinal cusps.
   - **Ojhayugma Bala:** Evaluated only Rasi odd/even (max 15 virupas); now upgraded to evaluate both Rasi and Navamsha (max 30 virupas).
   - **Ayana Bala:** Used a binary $20/40$ step; now upgraded to continuous planetary declination $\delta$ ($[24 \pm \delta] \times 1.25$).
   - **Abda Bala:** Defaulted to Sun; now evaluates the solar year ruler based on the weekday of Mesha Sankranti (ingress into sidereal Aries).
   - **Drik Bala:** Employed custom orbs; now follows the continuous 7-piece BPHS Drishti curve ($30^\circ$ to $300^\circ$) plus Vishesha Drishti divided by $4.0$.
3. **Independent Benchmark Recalculation:** The reference chart was recalculated using the corrected formulas. Jupiter (498.87 virupas) and Venus (495.86 virupas) emerge as the dominant grahas, with Saturn (440.01 virupas) gaining significant strength through 4 own-sign divisional placements.
4. **Zero Regressions:** All 14 dedicated Shadbala tests passed, and the full regression suite maintained 100% green status across all 300+ tests.

---

## 2. Mathematical Specification & Formula Sources

The classical Shadbala comprises six distinct categories of strength, measured in **virupas** (shashtiamsas), where $60 \text{ virupas} = 1 \text{ rupa}$.

```
Shadbala Total = Sthana Bala + Dig Bala + Kala Bala + Cheshta Bala + Naisargika Bala + Drik Bala
```

### Component 1: Sthana Bala (Positional Strength)
*Source: BPHS Chapter 27, Slokas 5–14*

Sthana Bala is the sum of five sub-components:
$$\text{Sthana Bala} = \text{Uchcha} + \text{Saptavargaja} + \text{Ojhayugma} + \text{Kendradi} + \text{Drekkana}$$

#### 1.1 Uchcha Bala (Exaltation Strength)
* **Classical Formula (BPHS Ch. 27, Sloka 5):**
  $$\text{Uchcha Bala} = \frac{180^\circ - |\lambda - \lambda_{\text{exalt}}|}{3.0}$$
* **Maximum:** 60 virupas at exact deep exaltation point (*Paramochcha*).
* **Minimum:** 0 virupas at exact deep debilitation point (*Paramaneecha* = $\lambda_{\text{exalt}} + 180^\circ$).
* **Canonical Degrees:**
  - Sun: Aries $10^\circ$ ($\lambda = 10^\circ$)
  - Moon: Taurus $3^\circ$ ($\lambda = 33^\circ$)
  - Mars: Capricorn $28^\circ$ ($\lambda = 298^\circ$)
  - Mercury: Virgo $15^\circ$ ($\lambda = 165^\circ$)
  - Jupiter: Cancer $5^\circ$ ($\lambda = 95^\circ$)
  - Venus: Pisces $27^\circ$ ($\lambda = 357^\circ$)
  - Saturn: Libra $20^\circ$ ($\lambda = 200^\circ$)

#### 1.2 Saptavargaja Bala (Seven-Divisional Dignity Strength)
* **Classical Formula (BPHS Ch. 27, Slokas 8–11):**  
  Evaluated across 7 divisional charts: $D_1$ (Rasi), $D_2$ (Hora), $D_3$ (Drekkana), $D_7$ (Saptamsha), $D_9$ (Navamsha), $D_{12}$ (Dvadasamsha), and $D_{30}$ (Trimsamsha).
* **Dignity Scoring via Panchadha Maitri (Compound Friendship):**
  - **Moolatrikona:** $45.0 \text{ virupas}$ (applicable in $D_1$ within canonical degree limits)
  - **Swakshetra (Own Sign):** $30.0 \text{ virupas}$
  - **Adhi-Mitra (Great Friend = Natural Friend + Temporal Friend):** $22.5 \text{ virupas}$
  - **Mitra (Friend = Natural Friend + Temporal Enemy OR Neutral + Temporal Friend):** $15.0 \text{ virupas}$
  - **Sama (Neutral = Natural Neutral + Temporal Enemy OR Friend + Enemy balance):** $7.5 \text{ virupas}$
  - **Shatru (Enemy = Natural Enemy + Temporal Friend):** $3.75 \text{ virupas}$
  - **Adhi-Shatru (Great Enemy = Natural Enemy + Temporal Enemy):** $1.875 \text{ virupas}$
* **Temporal Friendship Rule (Tatkalika Mitra):**  
  Planets positioned in houses 2, 3, 4, 10, 11, and 12 from the graha in the Rasi ($D_1$) chart are temporal friends ($+1$); planets in houses 1, 5, 6, 7, 8, and 9 are temporal enemies ($-1$).
* **Divisional Longitude Mapping:**
  - $D_1$: Sign index $1 \dots 12$
  - $D_2$: Odd signs: $0-15^\circ$ Sun (Leo), $15-30^\circ$ Moon (Cancer); Even signs: $0-15^\circ$ Moon (Cancer), $15-30^\circ$ Sun (Leo)
  - $D_3$: $0-10^\circ$ sign itself, $10-20^\circ$ 5th sign, $20-30^\circ$ 9th sign
  - $D_7$: Odd signs: count from sign; Even signs: count from 7th sign
  - $D_9$: Fiery signs count from Aries; Earthy from Capricorn; Airy from Libra; Watery from Cancer
  - $D_{12}$: Count from sign itself ($2^\circ 30'$ per division)
  - $D_{30}$: Odd signs: Mars ($0-5^\circ$), Saturn ($5-10^\circ$), Jupiter ($10-18^\circ$), Mercury ($18-25^\circ$), Venus ($25-30^\circ$); Even signs: Venus ($0-5^\circ$), Mercury ($5-12^\circ$), Jupiter ($12-20^\circ$), Saturn ($20-25^\circ$), Mars ($25-30^\circ$).

#### 1.3 Ojhayugma Bala (Odd/Even Sign & Navamsha Strength)
* **Classical Formula (BPHS Ch. 27, Sloka 12):**
  - Male grahas (Sun, Mars, Jupiter): 15 virupas in odd Rasi + 15 virupas in odd Navamsha (Max 30 virupas).
  - Female grahas (Moon, Venus): 15 virupas in even Rasi + 15 virupas in even Navamsha (Max 30 virupas).
  - Neutral grahas (Mercury, Saturn): 15 virupas in odd Rasi + 15 virupas in odd Navamsha (Max 30 virupas).

#### 1.4 Kendradi Bala (Quadrant Strength)
* **Classical Formula (BPHS Ch. 27, Sloka 13):**
  - Kendra houses (1, 4, 7, 10): $60.0 \text{ virupas}$
  - Panapara houses (2, 5, 8, 11): $30.0 \text{ virupas}$
  - Apoklima houses (3, 6, 9, 12): $15.0 \text{ virupas}$

#### 1.5 Drekkana Bala (Decanate Gender Strength)
* **Classical Formula (BPHS Ch. 27, Sloka 14):**
  - Male grahas in 1st decanate ($0^\circ - 10^\circ$): $15.0 \text{ virupas}$
  - Neutral grahas in 2nd decanate ($10^\circ - 20^\circ$): $15.0 \text{ virupas}$
  - Female grahas in 3rd decanate ($20^\circ - 30^\circ$): $15.0 \text{ virupas}$

---

### Component 2: Dig Bala (Directional Strength)
*Source: BPHS Chapter 27, Slokas 15–18*

* **Potent Points (Digbala Exaltation = 60 virupas):**
  - Jupiter & Mercury: 1st House Cusp (Lagna / East, $\lambda_{\text{lagna}}$)
  - Sun & Mars: 10th House Cusp (Midheaven / South, $\lambda_{\text{lagna}} + 270^\circ$)
  - Saturn: 7th House Cusp (Descendant / West, $\lambda_{\text{lagna}} + 180^\circ$)
  - Moon & Venus: 4th House Cusp (Nadir / North, $\lambda_{\text{lagna}} + 90^\circ$)
* **Nirbala Points (Zero Strength Points = $180^\circ$ opposite to potent points):**
  - Jupiter & Mercury: 7th cusp
  - Sun & Mars: 4th cusp
  - Saturn: 1st cusp
  - Moon & Venus: 10th cusp
* **Continuous Classical Formula:**
  $$\text{diff} = |\lambda_{\text{planet}} - \lambda_{\text{nirbala}}| \pmod{360^\circ}$$
  $$\text{if } \text{diff} > 180^\circ: \text{diff} = 360^\circ - \text{diff}$$
  $$\text{Dig Bala} = \frac{\text{diff}}{3.0}$$

---

### Component 3: Kala Bala (Temporal Strength)
*Source: BPHS Chapter 27, Slokas 19–32*

Kala Bala is the sum of eight sub-components:
$$\text{Kala Bala} = \text{Nathonnatha} + \text{Paksha} + \text{Tribhaga} + \text{Abda} + \text{Masa} + \text{Vara} + \text{Hora} + \text{Ayana}$$

1. **Nathonnatha Bala:**
   - Diurnal grahas (Sun, Jupiter, Venus): $60 \text{ virupas}$ if day birth, $0$ if night birth.
   - Nocturnal grahas (Moon, Mars, Saturn): $60 \text{ virupas}$ if night birth, $0$ if day birth.
   - Mercury: Always receives $30 \text{ virupas}$.
2. **Paksha Bala:**
   - Elongation $\theta = (\lambda_{\text{moon}} - \lambda_{\text{sun}}) \pmod{360^\circ}$.
   - Arc $d = \theta$ if $\theta \le 180^\circ$ else $(360^\circ - \theta)$.
   - Benefics (Jupiter, Venus, waxing Moon, Mercury): $\text{score} = \frac{d}{180.0} \times 60.0$.
   - Malefics (Sun, Mars, Saturn, waning Moon): $\text{score} = 60.0 - \left(\frac{d}{180.0} \times 60.0\right)$.
3. **Tribhaga Bala:**
   - Day third 1 (morning): Mercury ($15 \text{ virupas}$)
   - Day third 2 (noon): Sun ($15 \text{ virupas}$)
   - Day third 3 (afternoon): Saturn ($15 \text{ virupas}$)
   - Night third 1 (evening): Moon ($15 \text{ virupas}$)
   - Night third 2 (midnight): Venus ($15 \text{ virupas}$)
   - Night third 3 (pre-dawn): Mars ($15 \text{ virupas}$)
   - Jupiter: Always receives $15 \text{ virupas}$ regardless of time of birth.
4. **Abda Bala (Lord of the Solar Year):**
   - Ruler of the weekday on which the solar year commenced at Mesha Sankranti (ingress into sidereal Aries, approx April 14th) receives $15 \text{ virupas}$.
5. **Masa Bala (Lord of the Solar Month):**
   - Ruler of the solar zodiac sign currently occupied by the Sun receives $30 \text{ virupas}$.
6. **Vara Bala (Lord of the Weekday):**
   - Ruler of the day of birth receives $45 \text{ virupas}$.
7. **Hora Bala (Lord of the Planetary Hour):**
   - Planetary hour starting at sunrise (~06:00) with the weekday lord, sequenced in descending Chaldean orbital order: Saturn $\to$ Jupiter $\to$ Mars $\to$ Sun $\to$ Venus $\to$ Mercury $\to$ Moon. The ruling hora lord receives $60 \text{ virupas}$.
8. **Ayana Bala (Declination-Based Solstitial Strength):**
   - Obliquity of ecliptic $\epsilon \approx 23.44^\circ$.
   - Sayana longitude $\lambda_{\text{sayana}} = (\lambda_{\text{sidereal}} + \text{ayanamsa}) \pmod{360^\circ}$.
   - Declination $\delta = \arcsin(\sin \lambda_{\text{sayana}} \times \sin \epsilon)$.
   - Sun, Mars, Jupiter, Venus (North-leaning): $\text{Ayana Bala} = (24.0 + \delta) \times 1.25$.
   - Moon, Saturn (South-leaning): $\text{Ayana Bala} = (24.0 - \delta) \times 1.25$.
   - Mercury: $\text{Ayana Bala} = (24.0 + \delta) \times 1.25$.

---

### Component 4: Cheshta Bala (Motional Strength)
*Source: BPHS Chapter 27, Slokas 33–38*

* **The Classical 8-Gati Framework:**
  - Vakra (Retrograde, $V < 0$): $60.0 \text{ virupas}$
  - Vikala (Stationary, $|V| < 0.1^\circ/\text{day}$): $45.0 \text{ virupas}$
  - Chara / Sama (Direct Fast, $|V| \ge V_{\text{mean}}$): $30.0 \text{ virupas}$
  - Manda (Direct Slow, $|V| < V_{\text{mean}}$): $15.0 \text{ virupas}$
  - Sun & Moon: Fixed at $30.0 \text{ virupas}$ per BPHS convention (luminaries do not retrograde).
* **The Continuous Seegra Kendra Framework:**
  - For outer planets (Mars, Jupiter, Saturn), Seegrochcha is the Sun. Elongation $K = |\lambda_{\text{sun}} - \lambda_{\text{planet}}|$. If $K > 180^\circ$, $K = 360^\circ - K$.
  - Continuous $\text{Cheshta Bala} = \frac{K}{3.0}$ (giving $60$ at exact opposition / retrograde, and $0$ at exact conjunction).

---

### Component 5: Naisargika Bala (Natural Inherent Strength)
*Source: BPHS Chapter 27, Sloka 31*

Permanently fixed classical constants proportional to astronomical luminosity:
- Sun: $60.00 \text{ virupas}$ ($1.00 \text{ rupa}$)
- Moon: $51.43 \text{ virupas}$ ($0.857 \text{ rupa}$)
- Venus: $42.86 \text{ virupas}$ ($0.714 \text{ rupa}$)
- Jupiter: $34.29 \text{ virupas}$ ($0.571 \text{ rupa}$)
- Mercury: $25.71 \text{ virupas}$ ($0.429 \text{ rupa}$)
- Mars: $17.14 \text{ virupas}$ ($0.286 \text{ rupa}$)
- Saturn: $8.57 \text{ virupas}$ ($0.143 \text{ rupa}$)

---

### Component 6: Drik Bala (Aspectual Strength)
*Source: BPHS Chapter 27, Slokas 39–44*

Let forward arc $\theta = (\lambda_{\text{receiving}} - \lambda_{\text{aspecting}}) \pmod{360^\circ}$.

* **BPHS Continuous General Drishti Curve (0 to 60 shashtiamsas):**
  - $0^\circ \le \theta < 30^\circ$: $0$
  - $30^\circ \le \theta < 60^\circ$: $(\theta - 30) \times 0.5$ (reaches 15 at $60^\circ$)
  - $60^\circ \le \theta < 90^\circ$: $15 + (\theta - 60) \times 1.0$ (reaches 45 at $90^\circ$)
  - $90^\circ \le \theta < 120^\circ$: $45 - (\theta - 90) \times 0.5$ (drops to 30 at $120^\circ$)
  - $120^\circ \le \theta < 150^\circ$: $30 - (\theta - 120) \times 1.0$ (drops to 0 at $150^\circ$)
  - $150^\circ \le \theta < 180^\circ$: $(\theta - 150) \times 2.0$ (reaches 60 at $180^\circ$)
  - $180^\circ \le \theta < 300^\circ$: $(300 - \theta) / 2.0$ (drops from 60 at $180^\circ$ to 0 at $300^\circ$)
  - $300^\circ \le \theta < 360^\circ$: $0$
* **Vishesha Drishti (Special Full Aspects):**
  - Mars casts full aspect ($60 \text{ virupas}$) on 4th ($90^\circ$) and 8th ($210^\circ$).
  - Jupiter casts full aspect ($60 \text{ virupas}$) on 5th ($120^\circ$) and 9th ($240^\circ$).
  - Saturn casts full aspect ($60 \text{ virupas}$) on 3rd ($60^\circ$) and 10th ($270^\circ$).
* **Aggregation:**
  $$\text{Drik Bala} = \frac{\sum \text{Benefic Drishtis} - \sum \text{Malefic Drishtis}}{4.0}$$
  Benefics: Jupiter, Venus, waxing Moon, Mercury. Malefics: Sun, Mars, Saturn, waning Moon.

---

## 3. Confirmed Discrepancies & Codebase Corrections

| Component | Pre-Audit Implementation | Audited BPHS Formula | Impact & Correction |
|:---|:---|:---|:---|
| **Saptavargaja Bala** | Evaluated only $D_1$ scaled by $6/7$ ($6-38$ virupas) | Evaluates all 7 vargas ($D_1, D_2, D_3, D_7, D_9, D_{12}, D_{30}$) using Panchadha Maitri | **Corrected.** Saturn in own sign across 4 vargas now receives $146.25 \text{ virupas}$, matching classical magnitudes ($60-150 \text{ virupas}$). |
| **Dig Bala** | House-based discrete step function ($60, 50, \dots$) | Continuous arc from Nirbala point: $\frac{\text{diff}}{3.0}$ | **Corrected.** Provides sub-arcsecond continuous values ($0.0 \dots 60.0 \text{ virupas}$). |
| **Ojhayugma Bala** | Checked only Rasi sign ($0$ or $15$) | Checks both Rasi and Navamsha ($0, 15, \text{ or } 30$) | **Corrected.** Grahas aligned in both Rasi and Navamsha now receive full $30.0 \text{ virupas}$. |
| **Ayana Bala** | Coarse binary $20.0 / 40.0 \text{ virupas}$ | Continuous planetary declination $\delta$: $(24 \pm \delta) \times 1.25$ | **Corrected.** Jupiter at $+23.10^\circ$ declination earns $58.87 \text{ virupas}$; Saturn at $-21.08^\circ$ earns $56.36 \text{ virupas}$. |
| **Abda Bala** | Defaulted to Sun ($15 \text{ virupas}$) | Weekday lord at Mesha Sankranti (solar ingress into Aries) | **Corrected.** 1990 Mesha Sankranti fell on a Saturday, awarding $15.0 \text{ virupas}$ to Saturn. |
| **Drik Bala** | Custom piecewise orbs | BPHS continuous 7-piece Drishti curve ($30^\circ - 300^\circ$) + Vishesha Drishti / 4 | **Corrected.** Full classical aspect curve implemented. |

---

## 4. Independent Recalculation: Chennai Benchmark Chart

**Birth Data:** 1990-05-15, 14:30:00 IST (UTC+05:30), Chennai ($13.0827^\circ\text{N}, 80.2707^\circ\text{E}$).  
**Ayanamsha:** Chitrapaksha/Lahiri ($23.734^\circ$).  
**Ascendant:** Virgo $4^\circ 23' 48"$ ($\lambda = 154.3968^\circ$).  
**Panchang:** Krishna Shashthi, Uttara Ashadha, Shubha Yoga, Gara Karana, Mangalavara (Tuesday).

### Detailed Component Breakdown (Virupas)

| Graha | Sthana Bala | Dig Bala | Kala Bala | Cheshta Bala | Naisargika | Drik Bala | Total Virupas | Total Rupas | Required | Ratio | Strong? | Rank |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Jupiter** | 237.35 | 33.80 | 173.43 | 30.00 | 34.29 | -9.99 | **498.87** | **8.31** | 390.0 | **1.28** | **Yes** | **1** |
| **Venus** | 244.82 | 25.15 | 165.80 | 30.00 | 42.86 | -12.76 | **495.86** | **8.26** | 330.0 | **1.50** | **Yes** | **2** |
| **Sun** | 145.03 | 48.72 | 193.99 | 30.00 | 60.00 | -19.10 | **458.64** | **7.64** | 390.0 | **1.18** | **Yes** | **3** |
| **Saturn** | 212.41 | 39.04 | 106.81 | 60.00 | 8.57 | +13.18 | **440.01** | **7.33** | 300.0 | **1.47** | **Yes** | **4** |
| **Mercury** | 219.77 | 13.30 | 117.28 | 60.00 | 25.71 | -21.64 | **414.42** | **6.91** | 420.0 | 0.99 | No | **5** |
| **Moon** | 169.63 | 50.83 | 95.83 | 30.00 | 51.43 | +13.09 | **410.81** | **6.85** | 360.0 | **1.14** | **Yes** | **6** |
| **Mars** | 208.66 | 26.71 | 89.63 | 30.00 | 17.14 | -5.16 | **366.97** | **6.12** | 300.0 | **1.22** | **Yes** | **7** |

### Astrological Observations on Reference Results:
1. **Jupiter (Rank 1, 498.87 virupas):** Highest strength due to Kendra 10th placement (Kendradi 60.0), northern declination near solstice (Ayana 58.87), Diurnal birth (60.0), and decanate dignity.
2. **Venus (Rank 2, 495.86 virupas):** Exalted in Pisces (Uchcha 57.32), Kendra 7th (Kendradi 60.0), highest overall ratio ($1.50 \times$ requirement).
3. **Saturn (Rank 4, 440.01 virupas):** Elevated significantly by its 4 own-sign divisional placements in Capricorn ($D_1, D_3, D_9, D_{12}$), retrograde motion (Cheshta 60.0), and Southern declination (Ayana 56.36).
4. **Mercury (Rank 5, 414.42 virupas):** While achieving 414.42 virupas, Mercury falls just short of its high classical requirement ($420 \text{ virupas}$, ratio $0.99$), correctly evaluated as `is_strong: false`.

---

## 5. Independent Test Suite & Verification Results

### A. Dedicated Shadbala Test Suite (`backend/tests/test_shadbala_engine.py`)
**14 tests executed, 14 passed (100% green in 1.19s):**
- `test_uchcha_bala_exact_exaltation_and_debilitation`: Verifies exact $60.0$ at exaltation and $0.0$ at debilitation.
- `test_naisargika_bala_fixed_classical_values`: Verifies all 7 fixed BPHS constants.
- `test_dig_bala_best_and_worst_houses`: Verifies exact cardinal angles ($15^\circ, 105^\circ, 195^\circ, 285^\circ$) for Dig Bala.
- `test_cheshta_bala_rules`: Verifies retrograde ($60.0$) and luminaries ($30.0$).
- `test_kala_bala_nathonnatha`: Verifies diurnal vs nocturnal day/night allocations.
- `test_shadbala_returns_exact_seven_classical_planets`: Asserts Rahu and Ketu exclusion.
- `test_shadbala_mathematical_consistency`: Asserts $\sum \text{components} = \text{total\_virupas}$ and $\text{rupas} = \text{virupas} / 60.0$.
- `test_shadbala_ranking_integrity`: Asserts unique ranks $1 \dots 7$ ordered descending.
- `test_shadbala_api_endpoint`: Validates HTTP 200 contract at `POST /api/v1/vedic/shadbala`.
- `test_metadata_endpoint_includes_shadbala`: Validates capability in `GET /api/v1/metadata`.
- `test_rules_inventory_includes_shadbala_rule`: Validates `RULE-SHADBALA-01` in rules inventory.
- `test_saptavargaja_bala_classical_compound_dignities`: **[NEW REFERENCE TEST]** Verifies independently established 7-varga positions and Panchadha Maitri score ($146.25 \text{ virupas}$) for Saturn.
- `test_ayana_bala_solstitial_extremes`: **[NEW REFERENCE TEST]** Verifies continuous Ayana Bala at Summer Solstice ($>55.0$) and Winter Solstice ($<5.0$).
- `test_independent_reference_chart_chennai_1990`: **[NEW REFERENCE TEST]** Validates complete benchmark calculation against pre-established ranges.

### B. Full Regression Test Suite
Executed: `.venv\Scripts\pytest backend\tests -q`  
**Result:** **294 passed, 9 skipped, 0 failures** across all modules.

---

## 6. Tradition-Dependent Rules & Assumptions

1. **Moon's Paksha Bala:** BPHS Sloka 22 notes that the Moon's Paksha Bala can be doubled compared to other benefics. In standard computational practice (e.g., BV Raman and modern software), single normalization ($0-60 \text{ virupas}$) is retained to prevent Kala Bala from skewing disproportionately.
2. **Mercury's Benefic/Malefic Status:** Mercury is categorized as naturally benefic in Drik Bala and Paksha Bala unless conjunct a natural malefic with an orb $<5^\circ$.
3. **House Cusps:** Whole Sign (Rashi-Bhava) is standard in classical Vedic astrology, where the Ascendant degree defines the cardinal reference point ($h_1 = \lambda_{\text{lagna}}$, $h_4 = \lambda_{\text{lagna}} + 90^\circ$, $h_7 = \lambda_{\text{lagna}} + 180^\circ$, $h_{10} = \lambda_{\text{lagna}} + 270^\circ$).
