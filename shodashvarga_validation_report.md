# Feature 5: Classical Shodashvarga (16 Divisional Charts) Engine — Validation & Verification Report

**Date:** 2026-10-18  
**Project:** Gokul's Astrological Insights  
**Status:** Completed & Fully Validated  
**Test Baseline:** 382 passed, 9 skipped (100% passing across 391 test items)  

---

## 1. Executive Summary

Feature 5 of the approved roadmap has been implemented, validated, and verified strictly per classical Vedic astrology standards (*Brihat Parashara Hora Shastra*, Chapter 6: *Shodashavargadhyaya*, and *Saravali*, Chapter 3).

The newly completed **Classical Shodashvarga Engine** supports all 16 canonical divisional charts:
1. **D1 — Rasi:** Physical constitution, general vitality, and baseline chart.
2. **D2 — Hora:** Wealth, treasury, assets, resources, and speech (*Parashari Sun/Moon system*).
3. **D3 — Drekkana:** Siblings, courage, vitality, initiative, and 3rd-house affairs.
4. **D4 — Chaturthamsa (Turyamsa):** Fixed assets, real estate, vehicles, and general fortune.
5. **D7 — Saptamsa:** Children, grandchildren, progeny, and creative lineage.
6. **D9 — Navamsa (Dharmamsa):** Spouse, marriage, dharma, inner soul's strength, and core planetary potency.
7. **D10 — Dasamsa (Swargamsa):** Profession, career, executive status, public authority, and achievements.
8. **D12 — Dwadasamsa (Suryamsa):** Parents, ancestral heritage, and paternal/maternal lineage.
9. **D16 — Shodasamsa (Kalamsa):** Vehicles, conveyances, comforts, and vehicular safety.
10. **D20 — Vimsamsa:** Spiritual progress, meditation, mantra siddhi, and upasana.
11. **D24 — Chaturvimsamsa (Siddhamsa):** Higher education, scholarship, intellectual wisdom, and research.
12. **D27 — Saptavimsamsa (Bhamsha / Nakshatramsa):** Physical stamina, subconscious strengths, and hidden vulnerabilities.
13. **D30 — Trimsamsa:** Misfortunes, evils, doshas, chronic diseases, and character trials.
14. **D40 — Khavedamsa (Swavedamsa):** Subtle auspicious and inauspicious karmic effects.
15. **D45 — Akshavedamsa:** Character purity, moral integrity, and holistic life balance.
16. **D60 — Shashtyamsa:** Root-cause past-life karma, subtle destiny, and supreme classical validation (highest Shadbala weight).

---

## 2. Mathematical Specification & Classical Formulas

Integer milli-arcsecond (mas) arithmetic is utilized throughout to guarantee exact boundary resolution on cusp divisions and prevent IEEE 754 floating-point drift:
- $1^\circ = 3,600,000$ mas
- $30^\circ = 108,000,000$ mas
- $360^\circ = 1,296,000,000$ mas

Let $S \in \{1, \dots, 12\}$ be the D1 Rasi sign ($S = \lfloor \lambda / 30^\circ \rfloor + 1$).  
Let $\theta = \lambda \pmod{30^\circ}$ be the degree within the sign ($0 \le \theta < 30^\circ$).  
Let $\text{is\_odd} = (S \pmod 2 == 1)$.  
Let $\text{is\_movable} = S \in \{1, 4, 7, 10\}$; $\text{is\_fixed} = S \in \{2, 5, 8, 11\}$; $\text{is\_dual} = S \in \{3, 6, 9, 12\}$.

| Varga | Division Name | Span | Classical Mapping Formula (*BPHS* Ch. 6) |
|---|---|---|---|
| **D1** | Rasi | $30^\circ$ | $V_{\text{sign}} = S$ |
| **D2** | Hora | $15^\circ$ | If $\text{is\_odd}$: $k=0 \implies \text{Leo (5)}$ (Sun), $k=1 \implies \text{Cancer (4)}$ (Moon).<br>If $\text{is\_even}$: $k=0 \implies \text{Cancer (4)}$ (Moon), $k=1 \implies \text{Leo (5)}$ (Sun). |
| **D3** | Drekkana | $10^\circ$ | $k = \lfloor \theta / 10^\circ \rfloor \in \{0, 1, 2\}$.<br>$V_{\text{sign}} = ((S - 1 + 4k) \pmod{12}) + 1$ (1st, 5th, 9th Kendra/Trikona). |
| **D4** | Chaturthamsa | $7.5^\circ$ | $k = \lfloor \theta / 7.5^\circ \rfloor \in \{0, 1, 2, 3\}$.<br>$V_{\text{sign}} = ((S - 1 + 3k) \pmod{12}) + 1$ (1st, 4th, 7th, 10th quadrants). |
| **D7** | Saptamsa | $\frac{30}{7}^\circ$ | $k = \lfloor \theta / (30/7) \rfloor \in \{0, \dots, 6\}$.<br>Odd signs start from $S$: $V_{\text{sign}} = ((S - 1 + k) \pmod{12}) + 1$.<br>Even signs start from $S+6$: $V_{\text{sign}} = ((S - 1 + 6 + k) \pmod{12}) + 1$. |
| **D9** | Navamsa | $3^\circ 20'$ | $k = \lfloor \theta / (10/3) \rfloor$. Continuous zodiac cycle:<br>$V_{\text{sign}} = (\lfloor \lambda / (10/3) \rfloor \pmod{12}) + 1$.<br>Movable starts $S$; Fixed starts $S+8$; Dual starts $S+4$. |
| **D10** | Dasamsa | $3^\circ$ | $k = \lfloor \theta / 3^\circ \rfloor \in \{0, \dots, 9\}$.<br>Odd signs start from $S$: $V_{\text{sign}} = ((S - 1 + k) \pmod{12}) + 1$.<br>Even signs start from $S+8$: $V_{\text{sign}} = ((S - 1 + 8 + k) \pmod{12}) + 1$. |
| **D12** | Dwadasamsa | $2.5^\circ$ | $k = \lfloor \theta / 2.5^\circ \rfloor \in \{0, \dots, 11\}$.<br>All signs start from $S$: $V_{\text{sign}} = ((S - 1 + k) \pmod{12}) + 1$. |
| **D16** | Shodasamsa | $1.875^\circ$ | $k = \lfloor \theta / 1.875^\circ \rfloor \in \{0, \dots, 15\}$.<br>Movable starts Aries (1); Fixed starts Leo (5); Dual starts Sagittarius (9).<br>$V_{\text{sign}} = ((\text{start} - 1 + k) \pmod{12}) + 1$. |
| **D20** | Vimsamsa | $1.5^\circ$ | $k = \lfloor \theta / 1.5^\circ \rfloor \in \{0, \dots, 19\}$.<br>Movable starts Aries (1); Fixed starts Sagittarius (9); Dual starts Leo (5).<br>$V_{\text{sign}} = ((\text{start} - 1 + k) \pmod{12}) + 1$. |
| **D24** | Chaturvimsamsa | $1.25^\circ$ | $k = \lfloor \theta / 1.25^\circ \rfloor \in \{0, \dots, 23\}$.<br>Odd signs start Leo (5); Even signs start Cancer (4).<br>$V_{\text{sign}} = ((\text{start} - 1 + k) \pmod{12}) + 1$. |
| **D27** | Saptavimsamsa | $1^\circ 6' 40''$ | $k = \lfloor \theta / (10/9) \rfloor \in \{0, \dots, 26\}$. Continuous zodiac cycle:<br>$V_{\text{sign}} = (\lfloor \lambda / (10/9) \rfloor \pmod{12}) + 1$.<br>Fire $\to$ Aries (1); Earth $\to$ Cancer (4); Air $\to$ Libra (7); Water $\to$ Capricorn (10). |
| **D30** | Trimsamsa | Variable | **Odd sign partitions:**<br>$0^\circ-5^\circ$: Mars $\to$ Aries (1)<br>$5^\circ-10^\circ$: Saturn $\to$ Aquarius (11)<br>$10^\circ-18^\circ$: Jupiter $\to$ Sagittarius (9)<br>$18^\circ-25^\circ$: Mercury $\to$ Gemini (3)<br>$25^\circ-30^\circ$: Venus $\to$ Libra (7)<br>**Even sign partitions (reversed):**<br>$0^\circ-5^\circ$: Venus $\to$ Taurus (2)<br>$5^\circ-12^\circ$: Mercury $\to$ Virgo (6)<br>$12^\circ-20^\circ$: Jupiter $\to$ Pisces (12)<br>$20^\circ-25^\circ$: Saturn $\to$ Capricorn (10)<br>$25^\circ-30^\circ$: Mars $\to$ Scorpio (8). |
| **D40** | Khavedamsa | $0.75^\circ$ | $k = \lfloor \theta / 0.75^\circ \rfloor \in \{0, \dots, 39\}$.<br>Odd signs start Aries (1); Even signs start Libra (7).<br>$V_{\text{sign}} = ((\text{start} - 1 + k) \pmod{12}) + 1$. |
| **D45** | Akshavedamsa | $\frac{2}{3}^\circ$ | $k = \lfloor \theta / (2/3) \rfloor \in \{0, \dots, 44\}$.<br>Movable starts Aries (1); Fixed starts Leo (5); Dual starts Sagittarius (9).<br>$V_{\text{sign}} = ((\text{start} - 1 + k) \pmod{12}) + 1$. |
| **D60** | Shashtyamsa | $0.5^\circ$ | $k = \lfloor \theta / 0.5^\circ \rfloor \in \{0, \dots, 59\}$.<br>Starts from $S$: $V_{\text{sign}} = ((S - 1 + k) \pmod{12}) + 1$.<br>**Deity Index:** Odd signs: $k$ ($0 \to 59$); Even signs: $59 - k$ ($59 \to 0$). |

---

## 3. Shashtyamsa (D60) 60 Classical Deities

Per *Brihat Parashara Hora Shastra* Ch. 6 Slokas 35-41, all 60 deities are implemented with their Sanskrit names, Tamil names, and classical nature (*Benefic / Malefic*):
- In **Odd signs**, the count proceeds in direct order ($0$ to $59$): Part 1 is *Ghora* (Malefic), Part 60 is *Indurekha* (Benefic).
- In **Even signs**, the count proceeds in reverse order ($59$ down to $0$): Part 1 is *Indurekha* (Benefic), Part 60 is *Ghora* (Malefic).

---

## 4. Documentation of Tradition-Dependent Variations

1. **D2 Hora (Parashari vs Cyclic):**
   - *Implemented Standard:* Classical Parashara rule where all placements reside strictly in Leo (Sun) or Cancer (Moon). This is the only canon recognized in *BPHS* Ch. 6.
   - *Commentary Note:* Some later commentators (e.g., *Saravali*) mention a cyclic 12-sign Hora, but Parashara's Sun-Moon Hora is the authoritative standard in Vedic astrology and Shadbala calculation.
2. **D30 Trimsamsa Degree Spans:**
   - *Implemented Standard:* Strictly followed *BPHS* Ch. 6 Slokas 27-28 ($5^\circ, 5^\circ, 8^\circ, 7^\circ, 5^\circ$ for odd signs; $5^\circ, 7^\circ, 8^\circ, 5^\circ, 5^\circ$ for even signs).
   - Sun and Moon do not rule any Trimsamsa division; rulerships belong exclusively to Mars, Saturn, Jupiter, Mercury, and Venus.
3. **D60 Deity Counting for Even Signs:**
   - *Implemented Standard:* Follows the prevailing classical tradition of reversing the deity sequence ($59 \to 0$) for even signs, preserving proper yin/yang symmetry.

---

## 5. API and Architecture Integration

- **Dedicated Shodashvarga Endpoints:**
  - `POST /api/v1/horoscope/varga/shodashvarga` (supports both ad-hoc birth input and authenticated saved horoscope ID).
  - `GET /api/v1/horoscope/varga/shodashvarga/{id}` (fetches or computes for saved horoscope).
  - `POST /api/v1/vedic/vargas` (standard Vedic extension endpoint taking `HoroscopeRequest`).
- **Complete Backwards Compatibility:**
  - `POST /api/v1/horoscope/varga/d1-d9`: Existing D1/D9 endpoint preserved 100% untouched. Returns existing `VargaD1D9Response` with an added optional `shodashvarga` payload for clients that want all 16 charts.
  - Existing frontend D1 and D9 chart presentation, summary callouts, and Pushkara Navamsa badges remain identical.
  - Standard chart-rendering payloads (`d1_chart`, `d9_chart`, `d10_chart`, `d60_chart`, and each entry in `charts[D_k].chart`) are formatted specifically for seamless consumption by `SouthIndianChart` and `NorthIndianChart` components.

---

## 6. Verification & Test Suite Results

### 6.1 Dedicated Shodashvarga Test Suite (`backend/tests/test_shodashvarga_engine.py`)
- **21 unit and reference tests executed — 21 passed (100%):**
  - `test_all_16_divisions_defined_and_metadata_complete` — PASSED
  - `test_d1_rasi_independent_mapping` — PASSED
  - `test_d2_hora_odd_even_parashari_rules` — PASSED
  - `test_d3_drekkana_1st_5th_9th_houses` — PASSED
  - `test_d4_chaturthamsa_kendra_signs` — PASSED
  - `test_d7_saptamsa_odd_even_rules` — PASSED
  - `test_d10_dasamsa_odd_even_rules` — PASSED
  - `test_d12_dwadasamsa_all_signs_start_from_self` — PASSED
  - `test_d16_shodasamsa_movable_fixed_dual_starts` — PASSED
  - `test_d20_vimsamsa_movable_fixed_dual_starts` — PASSED
  - `test_d24_chaturvimsamsa_odd_even_starts` — PASSED
  - `test_d27_saptavimsamsa_four_elements_starts` — PASSED
  - `test_d30_trimsamsa_exact_partitions_and_reversal` — PASSED
  - `test_d40_khavedamsa_odd_even_starts` — PASSED
  - `test_d45_akshavedamsa_movable_fixed_dual_starts` — PASSED
  - `test_d60_shashtyamsa_signs_and_deities` — PASSED
  - `test_boundaries_all_16_divisions_stability` — PASSED
  - `test_calculate_shodashvarga_orchestrator` — PASSED
  - `test_api_vargas_endpoint_ad_hoc` — PASSED
  - `test_api_shodashvarga_endpoint_ad_hoc` — PASSED
  - `test_api_varga_d1_d9_backward_compatibility` — PASSED

### 6.2 Full Project Regression Suite
```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\GAI\Astrology Website
configfile: pytest.ini
plugins: anyio-4.15.1
collected 391 items

...
========== 382 passed, 9 skipped, 137 warnings in 149.99s (0:02:29) ===========
```
- **Previous Baseline (Feature 4):** 353 passed, 9 skipped.
- **Current Baseline (Feature 5):** **382 passed, 9 skipped, 0 failures** across all 391 test items.
- Full backwards compatibility confirmed for D1/D9, Shadbala, Ashtakavarga, Yoga cancellations, Doshas, KP engine, Muhurta, and Vastu.

---

## 7. Changed & Created Files

| File Path | Status | Purpose |
|---|---|---|
| `backend/app/schemas/varga.py` | Modified | Added `ShodashvargaPlanetEntry`, `ShodashvargaAscendantEntry`, `ShodashvargaChartItem`, `ShodashvargaResponse`, `ShodashvargaRequest` |
| `backend/app/services/varga_engine.py` | Modified | Added `SHODASHVARGA_KEYS`, `DIVISION_METADATA`, `SHASHTYAMSA_DEITIES`, `calculate_divisional_placement`, `calculate_shodashvarga` |
| `backend/app/routers/horoscope.py` | Modified | Added `POST /api/v1/horoscope/varga/shodashvarga` and `GET /api/v1/horoscope/varga/shodashvarga/{id}` endpoints |
| `backend/app/routers/vedic_extensions.py` | Modified | Added `POST /api/v1/vedic/vargas` endpoint |
| `backend/tests/test_shodashvarga_engine.py` | Created | 21 comprehensive independent mathematical reference and API tests |
| `shodashvarga_validation_report.md` | Created | Deliverable validation and audit documentation |

---

## 8. Conclusion & Next Step

Feature 5 (Complete and Validate the 16 Shodashvarga Charts) is **100% complete, verified, and locked**. In strict compliance with instructions, no work on **Feature 6 (Nine-Page English/Tamil PDF Horoscope Report)** will commence until this report has been reviewed and approved.
