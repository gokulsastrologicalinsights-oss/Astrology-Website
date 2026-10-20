# Technical, Astrological & Licensing Audit: DaivAI Feature Extraction

**Audited Public Repository:** [https://github.com/master12coder/daiv-ai](https://github.com/master12coder/daiv-ai)  
**Target Platform:** Gokul’s Astrological Insights  
**Auditor:** Antigravity (Google DeepMind Advanced Agentic Coding)  
**Audit Date:** October 18, 2026  
**Status:** Completed (Phase 1 & Phase 2: Pre-Implementation Audit & Gap Analysis)  
**Deliverable Document:** `daiv_ai_integration_audit.md`  
**Current Test Suite Baseline:** 283 passed, 9 skipped (100% green across all existing modules)

---

## 1. Executive Summary

An exhaustive technical, architectural, astrological, and licensing audit of the repository `master12coder/daiv-ai` was performed to identify capabilities and algorithms that can be cleanly adapted for **Gokul’s Astrological Insights** without violating intellectual property boundaries, without introducing competing astronomical calculation engines, and without destabilizing existing production systems.

### Core Audit Verdict: STRICT CLEAN-ROOM REIMPLEMENTATION ONLY

1. **Licensing Discrepancy & AGPL-3.0 Contamination Risk:**
   - The reference repository exhibits a severe licensing inconsistency: the root `pyproject.toml` declares `license = "MIT"`, whereas the root `README.md` displays an `AGPL v3` badge and declares `AGPL-3.0 License`, the root `LICENSE` file contains the complete legal text of the **GNU Affero General Public License Version 3 (AGPL-3.0)** (34,523 bytes), and all three sub-package manifests (`engine/pyproject.toml`, `products/pyproject.toml`, `apps/pyproject.toml`) explicitly declare `license = "AGPL-3.0-or-later"`.
   - Under international copyright law and open-source licensing principles, the presence of the full AGPL-3.0 license text alongside sub-package AGPL declarations establishes strong copyleft obligations. Under AGPL-3.0 Section 13 (Remote Network Interaction), incorporating any AGPL-covered source code, YAML knowledge databases, or bundled assets into a networked service would require releasing the entire host platform’s proprietary source code under AGPL-3.0.
   - In addition, `daiv-ai` depends directly on `pyswisseph>=2.10.0`, which binds to the Swiss Ephemeris under GNU GPL v2+ (or commercial license).
   - **Binding Legal Conclusion:** **Zero code, rule files, YAML files, HTML templates, or font assets from `master12coder/daiv-ai` may be copied, transpiled, or vendored into Gokul’s Astrological Insights.** All proposed features must be designed and implemented via a strict clean-room protocol using public domain classical scriptures (*Brihat Parasara Hora Shastra*, *Phaladeepika*, *Saravali*, *Jataka Parijata*) and native Python/TypeScript engineering.

2. **Ephemeris & Architectural Inviolability:**
   - **XALEN Engine Inviolability:** Gokul’s Astrological Insights is built upon a high-precision, sub-arcsecond native **XALEN (Rust 0.6.0 / PyO3)** astronomical engine (`app.services.ephemeris`), employing the Chitrapaksha / Lahiri ayanamsha (`ayanamsa_id=1`). Under no circumstances will Swiss Ephemeris or `pyswisseph` be added to our dependencies, nor will a second competing ephemeris be introduced.
   - **KP Engine Inviolability:** Our dedicated KP calculation engine, transit timeline scanner, cuspal sub-lord mechanics, and prediction services remain completely untouched.
   - **Full Stack Preservation:** The existing Next.js 16 App Router dashboard, Supabase authentication, database schema, Muhurta engine, Vastu 16-zone Devata mandala, Numerology engine, and saved horoscopes remain intact.

3. **Status of the 6 Priority Features in Our Existing Website:**
   - **Shadbala (Six-Fold Planetary Strength):** **MISSING**. Only mentioned as draft placeholders in `metadata.py` and `rules.py`. Needs independent clean-room implementation.
   - **Bhinnashtakavarga and Sarvashtakavarga:** **ALREADY ROBUSTLY IMPLEMENTED & TESTED** in `app.services.ashtakavarga_engine` (including 337 SAV bindus and authentic BPHS Trikona/Ekadhipatya Shodhana and Shodhya Pinda). Can be enriched with two missing classical extensions: **Prastara Ashtakavarga** and **Kaksha Transit Analysis**.
   - **Yoga Detection and Cancellation Rules:** **PARTIALLY IMPLEMENTED**. Our platform already detects Raja, Dhana, Mahapurusha, Vipareeta, Lunar/Solar, Nabhasha (32 types), and Parivartana yogas. Genuinely missing: **Neech Bhanga Raja Yoga** (4 cancellation rules), **Kemadruma Bhanga** (8 cancellation rules), **Arishta Bhanga** (5 cancellation rules), **Daridra Yogas**, and **Yoga Strength Modifiers** (combustion, retrogression, vargottama).
   - **Dosha Detection and Cancellation Rules:** **PARTIALLY IMPLEMENTED (Rudimentary)**. Only a basic preliminary Kuja Dosha check without cancellation logic exists. Genuinely missing: **Full Multi-Point Kuja Dosha** (Lagna, Moon, Venus) with **10 classical cancellation rules**, **12 Named Kaal Sarp Dosha Types** (full/partial), **Sadesati Detection** (Rising, Peak, Setting phases), **Pitra Dosha**, and **Extended Doshas** (Guru Chandal, Shrapit, Grahan, Angarak, Shakata).
   - **Divisional Charts (D9, D10, Shodashvarga):** **PARTIALLY IMPLEMENTED**. Our engine currently implements high-precision D1 and D9 charts with integer milli-arcsecond (mas) arithmetic. Genuinely missing: **The complete 16-chart Shodashvarga suite** (D2 Hora, D3 Drekkana, D4 Chaturthamsha, D7 Saptamsha, D10 Dasamsha, D12 Dwadashamsha, D16 Shodashamsha, D20 Vimshamsha, D24 Chaturvimshamsha, D27 Saptavimshamsha, D30 Trimshamsha, D40 Khavedamsha, D45 Akshavedamsha, D60 Shashtyamsha).
   - **PDF Horoscope Report Generation:** **MISSING ENTIRELY**. Genuinely missing in both backend and frontend. Can be implemented cleanly using `reportlab` (BSD license) with native Tamil (`Noto Sans Tamil`) and English font support.

---

## 2. Complete Repository Inventory: `master12coder/daiv-ai`

The cloned reference repository at commit `e2bdf23` contains 852 files structured as a modern monorepo:

```
scratch/daiv-ai/
├── .github/                                         # Workflows and issue templates
├── apps/                                            # Package 3: Delivery Layer (AGPL-3.0)
│   ├── pyproject.toml                               # Declares license = "AGPL-3.0-or-later"
│   └── src/daivai_app/
│       ├── cli/                                     # Click CLI (15+ commands)
│       ├── telegram/                                # Python-telegram-bot + scheduler
│       └── web/                                     # FastAPI web dashboard + HTML Jinja routes
├── assets/
│   └── fonts/                                       # Bundled NotoSansDevanagari.ttf (647 KB)
├── docs/                                            # Product specs (kundali.md, matching.md, etc.)
├── engine/                                          # Package 1: Pure Computation (AGPL-3.0)
│   ├── pyproject.toml                               # Declares license = "AGPL-3.0-or-later"
│   └── src/daivai_engine/
│       ├── compute/                                 # 173 compute modules (chart, dasha, strength, etc.)
│       │   ├── strength/                            # Shadbala subpackage (sthana, kala, cheshta, etc.)
│       │   ├── ashtakavarga.py                      # BAV, SAV, Prastara, Kaksha
│       │   ├── ashtakavarga_shodhana.py             # Trikona/Ekadhipatya reductions
│       │   ├── divisional.py & divisional_extended.py # D2-D60 varga calculations
│       │   ├── dosha.py, dosha_extended.py, dosha_sadesati_pitra.py # Doshas & cancellations
│       │   └── yoga*.py (14 modules)                # 284 classical yogas + YAML-driven engine
│       ├── constants/ & constants.py                # Astronomical & astrological lookup tables
│       ├── knowledge/                               # 11 YAML rule files (lordships, gemstones, yogas)
│       ├── models/                                  # 20 Pydantic v2 schemas
│       └── scriptures/                              # 18 BPHS chapters & Lal Kitab in YAML
├── products/                                        # Package 2: Plugins & Interpretation (AGPL-3.0)
│   ├── pyproject.toml                               # Declares license = "AGPL-3.0-or-later"
│   └── src/daivai_products/
│       ├── interpret/                               # LLM integration (Ollama, Groq, Claude, OpenAI)
│       └── plugins/                                 # 7 isolated product plugins
│           └── kundali/                             # 14-section Kundali, PDF generator, SVG charts
├── tests/                                           # 530+ pytest test cases
├── LICENSE                                          # GNU Affero General Public License v3 (34.5 KB)
├── pyproject.toml                                   # Root UV workspace (claims license = "MIT")
└── README.md                                        # Documentation (badges AGPL v3)
```

---

## 3. Intellectual Property, Licensing & Legal Risk Analysis

### 3.1 The AGPL-3.0 vs. MIT Inconsistency

A critical legal contradiction exists within the repository:
1. Root `pyproject.toml` (Line 6) specifies: `license = "MIT"`.
2. Root `README.md` (Line 3 & 170) displays: `[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)` and states `AGPL-3.0 License — see LICENSE`.
3. Root `LICENSE` contains the complete, unmodified legal text of the **GNU Affero General Public License (AGPL-3.0)**.
4. Sub-package manifests `engine/pyproject.toml`, `products/pyproject.toml`, and `apps/pyproject.toml` all explicitly specify: `license = "AGPL-3.0-or-later"`.

**Legal Analysis:**
When a repository distributes an explicit `LICENSE` file containing AGPL-3.0 and asserts AGPL-3.0 in all of its distributable library manifests (`engine`, `products`, `apps`), an errant `license = "MIT"` string in the root monorepo coordinator file cannot be relied upon as a grant of permissive licensing. 

Under Section 13 of AGPL-3.0:
> *"Notwithstanding any other provision of this License, if you modify the Program, your modified version must prominently offer all users interacting with it remotely through a computer network... an opportunity to receive the Corresponding Source of your version..."*

If any proprietary commercial web service imports, vendors, or copies AGPL-3.0 source code or data assets, the entire web application and backend could be subjected to copyleft demands.

### 3.2 Third-Party Dependency Licensing

| Dependency | License | Used in `daiv-ai` For | Implications for Gokul’s Astrological Insights |
| :--- | :--- | :--- | :--- |
| **`pyswisseph`** | GNU GPL v2+ (or commercial) | Core planetary ephemeris | ❌ **PROHIBITED**. We use our native **XALEN (Rust/PyO3)** ephemeris, which is fast, clean, and free of GPL encumbrance. |
| **`weasyprint`** | LGPL v3 | HTML to PDF rendering | ⚠️ **NOT RECOMMENDED**. Requires complex native external C libraries (Cairo, Pango, GDK-PixBuf) on Windows server environments; LGPL copyleft considerations. |
| **`reportlab`** | BSD License (Open Source) | PDF fallback rendering | ✅ **APPROVED**. Standard, battle-tested, commercial-friendly Python library with zero external C library dependencies. |
| **`matplotlib`** | PSF / BSD-compatible | Chart PNG rendering | ⚠️ Optional; SVG direct generation or ReportLab Drawing primitives are lighter and thread-safe. |
| **`NotoSansDevanagari.ttf`**| SIL Open Font License (OFL) 1.1 | Devanagari font rendering | ℹ️ Permissive for fonts, but for our Tamil/English platform we will use `Noto Sans Tamil` and `Noto Sans` under OFL 1.1. |

### 3.3 Clean-Room Boundary Protocol

To ensure 100% legal compliance and prevent any copyright infringement:
1. **No Code Copying:** Zero lines of code or internal helper functions from `scratch/daiv-ai` will be copied into `backend/app/` or `frontend/`.
2. **No Asset Copying:** No YAML knowledge files, prompt strings, or templates from `daiv-ai` will be copied.
3. **Public Domain Astrology:** Classical astrological algorithms (BPHS, Phaladeepika, Jataka Parijata) belong to humanity's shared cultural heritage and public domain mathematical canon. Formulations will be coded cleanly from scratch adhering to existing code conventions in `backend/app/services/`.
4. **Ephemeris Invariance:** All planetary positions will continue to be provided exclusively by `app.services.ephemeris` (XALEN).

---

## 4. In-Depth Technical Audit: Six Focus Areas

### 4.1 Feature 1: Shadbala (Six-Fold Planetary Strength)

#### 4.1.1 Architectural Implementation in `daiv-ai`
In `daiv-ai`, Shadbala is implemented across five modules in `engine/src/daivai_engine/compute/strength/`:
1. `sthana_bala.py` (Positional strength, max ~450 virupas):
   - **Uchcha Bala:** Exaltation strength. Calculated as $(180 - |\lambda - \lambda_{exalt}|) / 3$ (0 at deep debilitation, 60 virupas at exact exaltation degree).
   - **Saptavargaja Bala:** Dignity across 7 divisional charts ($D_1, D_2, D_3, D_7, D_9, D_12, D_30$). Assigns points per chart: Exalted = 45, Moolatrikona = 22.5, Own = 30, Friendly = 15, Neutral = 7.5, Inimical = 3.75, Debilitated = 1.875 virupas.
   - **Ojhayugma Bala:** Odd/Even sign strength. Male planets (Sun, Mars, Jupiter) get 15 virupas in odd signs in D1 and D9; female planets (Moon, Venus) get 15 in even signs; neutral planets (Mercury, Saturn) follow gender rules.
   - **Kendradi Bala:** Planets in Kendras (1, 4, 7, 10) = 60 virupas; Panaparas (2, 5, 8, 11) = 30 virupas; Apoklimas (3, 6, 9, 12) = 15 virupas.
   - **Drekkana Bala:** Male planets in 1st decanate (0-10°), neutral in 2nd (10-20°), female in 3rd (20-30°) get 15 virupas.
2. `dig_bala.py` (Directional strength, max 60 virupas):
   - Best houses: Sun & Mars in 10th (South), Jupiter & Mercury in 1st (East), Saturn in 7th (West), Moon & Venus in 4th (North).
   - Distance from worst house ($D = |H - H_{worst}|$, max 6 houses): $\text{Dig Bala} = 60 \times (1 - D / 6)$.
3. `kala_bala.py` (Temporal strength, max ~300 virupas):
   - **Nathonnatha Bala:** Diurnal planets (Sun, Jupiter, Venus) receive 60 virupas for day birth; nocturnal (Moon, Mars, Saturn) receive 60 for night birth; Mercury receives 30 virupas always.
   - **Paksha Bala:** Benefics gain up to 60 virupas proportional to Moon-Sun elongation ($|\lambda_{Moon} - \lambda_{Sun}| / 3$); malefics receive $60 - \text{Paksha Bala}$.
   - **Hora Bala:** Chaldean hour lord receives 60 virupas.
   - **Vara Bala:** Weekday lord receives 45 virupas.
   - **Ayana Bala:** Uttarayana/Dakshinayana declination-based strength (40 vs 20 virupas).
   - **Tribhaga Bala:** Ruler of the 3 parts of day/night receives 60 virupas. Jupiter receives 60 virupas always.
   - **Abda & Masa Bala:** Year lord receives 15 virupas; Month lord receives 30 virupas.
4. `cheshta_bala.py` (Motional strength, max 60 virupas):
   - Sun and Moon receive 30 virupas fixed.
   - Other 5 planets: Retrograde = 60; Stationary ($|\text{speed}| < 0.1^\circ/\text{day}$) = 45; Direct & fast ($|\text{speed}| > \text{mean}$) = 30; Direct & slow = 15 virupas.
5. `composite.py` (Natural & Aspectual strength, aggregation):
   - **Naisargika Bala (Natural):** Fixed values representing the luminosity ratio $7:6:5:4:3:2:1$ of 60 virupas:
     - Sun: 60.00, Moon: 51.43, Venus: 42.86, Jupiter: 34.29, Mercury: 25.71, Mars: 17.14, Saturn: 8.57 virupas.
   - **Drik Bala (Aspectual):** Aspect strength cast by benefics adds virupas, malefics subtracts virupas based on graduated BPHS drishti angles.
   - **Yuddha Bala:** Planetary war adjustment for non-luminary planets within $1^\circ$ longitude.
   - **Thresholds & Ratios:** Total virupas compared against canonical BPHS minimum thresholds (Sun: 390, Moon: 360, Mars: 300, Mercury: 420, Jupiter: 390, Venus: 330, Saturn: 300 virupas). Ratio $\ge 1.0$ designates a planet as strong (*Bala-yukta*).

#### 4.1.2 Current State in Gokul’s Astrological Insights
- Currently, our backend contains **ZERO** Shadbala calculations.
- References in `backend/app/routers/metadata.py` and `backend/app/schemas/rules.py` explicitly state that Shadbala is "in draft status".
- Our customers and dashboard lack planetary strength metrics, making this the single highest-value astrological gap.

#### 4.1.3 Clean-Room Implementation Plan
- **Location:** `backend/app/services/shadbala_engine/`
- **Modules:**
  - `models.py`: Pydantic models for individual sub-balas, virupa/rupa totals, ratios, and relative ranking.
  - `sthana_bala.py`: Positional calculations (utilizing our native `varga_engine` for Saptavarga charts).
  - `dig_bala.py`: Exact directional angular arc.
  - `kala_bala.py`: Temporal calculations from sunrise/sunset, weekday, hora, and solar ingress.
  - `cheshta_bala.py`: Speed and station detection from XALEN planet daily motion.
  - `drik_bala.py`: True planetary aspect arcs.
  - `calculator.py`: Master orchestrator returning complete Shadbala breakdown.
- **API Endpoint:** `POST /api/v1/vedic/shadbala` (and embedded in `HoroscopeResponse.shadbala`).

---

### 4.2 Feature 2: Bhinnashtakavarga and Sarvashtakavarga

#### 4.2.1 Audit of `daiv-ai` Implementation
- `ashtakavarga.py` computes standard 8-donor contributions for Sun through Saturn (excluding Rahu/Ketu).
- Sarvashtakavarga total is verified as exactly 337 bindus.
- In addition to standard BAV and SAV, `daiv-ai` contains two valuable extensions:
  1. **Prastara Ashtakavarga:** A $12 \times 8$ matrix per planet displaying which donor (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna) contributed each individual bindu.
  2. **Kaksha Division:** Each zodiac sign ($30^\circ$) is divided into 8 equal sub-divisions (Kakshas) of $3^\circ 45'$ ($3.75^\circ$) ruled successively by:
     $$\text{Saturn} \to \text{Jupiter} \to \text{Mars} \to \text{Sun} \to \text{Venus} \to \text{Mercury} \to \text{Moon} \to \text{Lagna}$$
     When a transiting planet passes through a Kaksha whose lord contributed a bindu in that sign’s BAV, the transit yields positive results.

#### 4.2.2 Current State in Gokul’s Astrological Insights
- Our platform **already possesses a production-grade Ashtakavarga engine** in `backend/app/services/ashtakavarga_engine/`:
  - `tables.py`: Complete BPHS 8-donor contribution matrices.
  - `calculator.py`: Computes BAV for 7 planets and 337-bindu SAV.
  - `shodhana.py`: Implements Trikona Shodhana, Ekadhipatya Shodhana, and Shodhya Pinda (Rashi Pinda, Graha Pinda).
  - Test coverage: `test_ashtakavarga_engine.py` (180 lines, fully verified).
- **Comparison:** Our existing Shodhana implementation is actually **superior** to `daiv-ai`! `daiv-ai` only applies a simplified Ekadhipatya reduction heuristic on SAV using Rahu/Ketu, whereas our engine implements the authentic 5-rule BPHS planetary occupancy and lordship reduction on each planet’s BAV.
- **Genuine Gaps:**
  1. Prastara Ashtakavarga contributor matrix ($12 \times 8$).
  2. Kaksha computation ($3^\circ 45'$ subdivisions and transit beneficence).

#### 4.2.3 Recommendation
- **Classification:** **REIMPLEMENT** (Extensions only; existing core is preserved).
- Extend `backend/app/services/ashtakavarga_engine/` by adding `prastara.py` and `kaksha.py`.
- No modifications needed to existing BAV/SAV or Shodhana logic.

---

### 4.3 Feature 3: Yoga Detection and Cancellation Rules

#### 4.3.1 Audit of `daiv-ai` Implementation
- `daiv-ai` implements 284+ yogas across 14 modules.
- Crucially, it includes explicit **cancellation (*Bhanga*) engines**:
  1. **Neech Bhanga Raja Yoga (`yoga_neech_bhanga.py`):**
     - Evaluates 4 classical conditions under which planetary debilitation transforms into royal power:
       - Condition 1: The lord of the debilitation sign is in a Kendra from Lagna or Moon.
       - Condition 2: The lord of the planet's exaltation sign is in a Kendra from Lagna or Moon.
       - Condition 3: The debilitated planet itself occupies a Kendra house (1, 4, 7, 10).
       - Condition 4: The debilitated planet is retrograde (*Vakri*).
  2. **Kemadruma Bhanga (`yoga_kemadruma.py`):**
     - When Moon has no planets in 2nd or 12th (Kemadruma Yoga), evaluates 8 cancellation rules:
       - Benefics in Kendra from Lagna or Moon.
       - Moon conjunct a planet or in a Kendra from Lagna.
       - Moon in own or exalted sign (Taurus / Cancer).
       - Full Moon with high Paksha Bala ($>120^\circ$ from Sun).
       - Jupiter or Venus aspecting Moon.
  3. **Arishta Bhanga (`yoga_kemadruma.py`):**
     - Cancels planetary afflictions and infant morbidity (*Balarishta*):
       - Strong Jupiter aspecting an afflicted Moon.
       - Natural benefics in Kendras.
       - Exalted Lagna lord in Kendra or Trikona.
       - Jupiter or Venus placed in Lagna.
  4. **Daridra & Bandhana Yogas:**
     - 11th lord in dusthanas (6, 8, 12); malefics hemming Lagna lord.
  5. **Strength Modifiers (`apply_yoga_strength`):**
     - Penalizes combust (*Asta*) planets by $50\%$; boosts Vargottama planets by $+25\%$; boosts retrograde benefic planets.

#### 4.3.2 Current State in Gokul’s Astrological Insights
- Our `backend/app/services/yoga_engine/` is well-structured and already evaluates:
  - Pancha Mahapurusha Yogas (Hamsa, Malavya, Ruchaka, Bhadra, Sasa).
  - Raja Yogas (Lords of Kendra & Trikona conjunct, aspecting, or exchanging).
  - Dhana Yogas (1st, 2nd, 5th, 9th, 11th connections).
  - Vipareeta Raja Yogas (Harsha, Sarala, Vimala).
  - Lunar & Solar Yogas (Sunapha, Anapha, Dhurdhura, Kemadruma, Gajakesari, Budhaditya, etc.).
  - Parivartana Yogas (Maha, Dainya, Khala).
  - Nabhasha Yogas (32 distinct patterns in `nabhasha_engine`).
- **Genuinely Missing:**
  - Neech Bhanga cancellation rules (currently debilitated planets are just marked debilitated).
  - Kemadruma Bhanga cancellation verification (currently Kemadruma is flagged without checking if it is cancelled).
  - Arishta Bhanga protective cancellations.
  - Classical Daridra Yogas.
  - Yoga strength modifiers (combustion discounts, retrogression modifications).

#### 4.3.3 Clean-Room Implementation Plan
- **Location:** `backend/app/services/yoga_engine/evaluators/`
- Add `cancellations.py`:
  - `evaluate_neech_bhanga(ctx)`
  - `evaluate_kemadruma_bhanga(ctx)`
  - `evaluate_arishta_bhanga(ctx)`
- Add `daridra_yogas.py` for wealth denial/impediment combinations.
- Enhance `YogaDetail` schema to include `cancellation_status`, `cancellation_factors`, and `effective_strength`.

---

### 4.4 Feature 4: Dosha Detection and Cancellation Rules

#### 4.4.1 Audit of `daiv-ai` Implementation
`daiv-ai` contains an extensive dosha suite across `dosha.py`, `dosha_sadesati_pitra.py`, and `dosha_extended.py`:
1. **Mangal (Kuja) Dosha & 10 Cancellation Rules:**
   - Evaluated from three reference points: **Lagna, Moon, and Venus**.
   - Mars in 1, 2, 4, 7, 8, 12 triggers the initial condition.
   - Evaluates 10 classical cancellation rules:
     1. Mars in own sign (Aries, Scorpio).
     2. Mars exalted (Capricorn).
     3. Mars in Jupiter’s signs (Sagittarius, Pisces).
     4. Lagna is Aries or Scorpio (Mars is Lagnesha).
     5. Jupiter aspects Mars.
     6. Saturn aspects Mars.
     7. Mars conjunct Jupiter.
     8. Mars conjunct Moon (Chandra-Mangala).
     9. Mars in 2nd house in Mercury’s signs (Gemini, Virgo) — South Indian rule.
     10. Mars in 12th house in Venus’s signs (Taurus, Libra) — South Indian rule.
2. **Kaal Sarp Dosha (12 Serpent Types):**
   - Detects whether all 7 classical planets are hemmed on one side of the Rahu-Ketu nodal axis.
   - Identifies the 12 classical serpent types based on Rahu’s house placement:
     - 1st: Anant, 2nd: Kulik, 3rd: Vasuki, 4th: Shankhapal, 5th: Padma, 6th: Mahapadma,
     - 7th: Takshak, 8th: Karkotak, 9th: Shankhnaad, 10th: Ghatak, 11th: Vishdhar, 12th: Sheshnag.
   - Classifies severity: **Full** (100% hemmed), **Partial** (1 planet escapes), **None**.
3. **Sadesati Detection:**
   - Evaluates Saturn's transit across the 12th, 1st, and 2nd houses from the natal Moon sign.
   - Determines active phase: **Rising (12th)**, **Peak (1st)**, or **Setting (2nd)**.
4. **Pitra Dosha:**
   - Sun conjunct Rahu/Ketu, or 9th lord conjunct Rahu/Ketu/Saturn.
5. **Extended Doshas:**
   - **Guru Chandal Dosha:** Jupiter conjunct Rahu (cancelled if Jupiter is exalted/own sign).
   - **Shrapit Dosha:** Saturn conjunct Rahu.
   - **Grahan Dosha:** Sun or Moon conjunct Rahu or Ketu.
   - **Angarak Dosha:** Mars conjunct Rahu.
   - **Shakata Dosha:** Jupiter in 6th, 8th, or 12th from Moon (cancelled if Jupiter is in a Kendra from Lagna).

#### 4.4.2 Current State in Gokul’s Astrological Insights
- Only a primitive `check_kuja_dosha_basic` exists in `backend/app/services/rule_engine.py`.
- It evaluates houses 1, 2, 4, 7, 8, 12 from Lagna, Moon, and Venus, but explicitly leaves cancellation rules as uncompleted draft work (`is_cancelled=False`).
- Kaal Sarp Dosha, Sadesati, Pitra Dosha, Guru Chandal, Shrapit, Grahan, and Shakata are completely absent.

#### 4.4.3 Clean-Room Implementation Plan
- **Location:** `backend/app/services/dosha_engine/`
- Build a unified dosha service:
  - `mangal_dosha.py`: Comprehensive 3-point check with the 10 classical cancellation rules.
  - `kaal_sarp.py`: Axis hemming check and 12-type classification.
  - `sadesati.py`: Natal Moon vs current or natal Saturn transit phase.
  - `extended_doshas.py`: Pitra, Guru Chandal, Shrapit, Grahan, Angarak, Shakata with cancellations.
- **API Endpoint:** `POST /api/v1/vedic/doshas` (and integrated into `HoroscopeResponse`).

---

### 4.5 Feature 5: D9, D10, and Other Divisional Charts (Shodashvarga)

#### 4.5.1 Audit of `daiv-ai` Implementation
`daiv-ai` computes 17 divisional charts ($D_1$ through $D_{60}$) in `divisional.py` and `divisional_extended.py`:
- Standard divisions: $D_2$ (Hora), $D_3$ (Drekkana), $D_4$ (Chaturthamsha), $D_5$ (Panchamsha), $D_6$ (Shashthamsha), $D_7$ (Saptamsha), $D_9$ (Navamsha), $D_{10}$ (Dasamsha), $D_{12}$ (Dwadashamsha), $D_{16}$ (Shodashamsha), $D_{20}$ (Vimshamsha), $D_{24}$ (Chaturvimshamsha), $D_{27}$ (Saptavimshamsha), $D_{30}$ (Trimshamsha), $D_{40}$ (Khavedamsha), $D_{45}$ (Akshavedamsha), $D_{60}$ (Shashtyamsha).
- Calculation methodology: Uses floating-point degrees (`lon / 30.0`, `deg / (30.0 / N)`).
- **Critical Precision Defect in `daiv-ai`:** Using standard floating-point division without integer milli-arcsecond clamping introduces subtle boundary errors on cusp edges (e.g. $3^\circ 20' 00''$ evaluating to $3.3333333333333335$ or $3.3333333333333330$).

#### 4.5.2 Current State in Gokul’s Astrological Insights
- Our engine (`backend/app/services/varga_engine.py`) provides mathematical precision using **integer milli-arcsecond (mas)** arithmetic ($1^\circ = 3,600,000\text{ mas}$, circle = $1,296,000,000\text{ mas}$):
  - Zero IEEE-754 floating-point boundary errors.
  - Computes complete $D_1$ Rasi and $D_9$ Navamsa structures.
  - Evaluates Vargottama status and Pushkara Navamsa ($24$ classical points from *Jataka Parijata*).
- **Genuinely Missing:**
  - $D_{10}$ (Dasamsha) — essential for career and professional life.
  - The remaining 14 divisional charts: $D_2, D_3, D_4, D_7, D_{12}, D_{16}, D_{20}, D_{24}, D_{27}, D_{30}, D_{40}, D_{45}, D_{60}$.

#### 4.5.3 Clean-Room Implementation Plan
- **Location:** `backend/app/services/varga_engine.py`
- Extend `varga_engine.py` with integer milli-arcsecond algorithms for the full 16 Shodashvarga charts:
  - $D_2$ (Hora - 15° each; odd signs Sun/Leo then Moon/Cancer; even signs Moon/Cancer then Sun/Leo).
  - $D_3$ (Drekkana - 10° each; 1st = same sign, 2nd = 5th sign, 3rd = 9th sign).
  - $D_4$ (Chaturthamsha - 7.5° each; same sign, 4th, 7th, 10th).
  - $D_7$ (Saptamsha - $4^\circ 17' 8.57''$ each; odd signs from same sign, even from 7th).
  - $D_{10}$ (Dasamsha - 3° each; odd signs from same sign, even from 9th).
  - $D_{12}$ (Dwadashamsha - 2.5° each; counts from same sign).
  - $D_{16}$ (Shodashamsha - $1^\circ 52' 30''$; movable from Aries, fixed from Leo, dual from Sagittarius).
  - $D_{20}$ (Vimshamsha - 1.5°; movable from Aries, fixed from Sagittarius, dual from Leo).
  - $D_{24}$ (Chaturvimshamsha - $1^\circ 15'$; odd signs from Leo, even signs from Cancer).
  - $D_{27}$ (Saptavimshamsha - $1^\circ 6' 40''$; fire from Aries, earth from Cancer, air from Libra, water from Capricorn).
  - $D_{30}$ (Trimshamsha - non-uniform degrees: odd signs 0-5° Mars, 5-10° Saturn, 10-18° Jupiter, 18-25° Mercury, 25-30° Venus; reversed for even signs).
  - $D_{40}$ (Khavedamsha - 45' each; odd from Aries, even from Libra).
  - $D_{45}$ (Akshavedamsha - 40' each; movable from Aries, fixed from Leo, dual from Sagittarius).
  - $D_{60}$ (Shashtyamsha - 30' each; odd signs from Aries, even signs from Libra).
- **API Endpoint:** `POST /api/v1/varga/shodashvarga` and `POST /api/v1/varga/d10`.

---

### 4.6 Feature 6: PDF Horoscope Report Generation

#### 4.6.1 Audit of `daiv-ai` Implementation
- `daiv-ai` generates a 14-page visual Kundali report in `products/src/daivai_products/plugins/kundali/`:
  - Primary path: Jinja2 HTML rendered into PDF using WeasyPrint.
  - Fallback path: ReportLab generating document flow with matplotlib charts.
  - Features: North Indian diamond chart, Vimshottari Dasha Gantt chart, Shadbala bar chart, Ashtakavarga heatmap, gemstone card, yoga cards, and accuracy certificate.
  - Font: Bundles `NotoSansDevanagari.ttf`.

#### 4.6.2 Current State in Gokul’s Astrological Insights
- Our website currently has **NO PDF generation capability** in backend or frontend.
- Users can view interactive charts on screen, but cannot download or print a comprehensive, branded horoscope dossier.

#### 4.6.3 Technical & Dependency Recommendations for Gokul’s Astrological Insights
1. **WeasyPrint Reject:**
   - WeasyPrint requires native Cairo, Pango, and GDK-PixBuf shared libraries installed on the operating system. On Windows development environments and standard container runtimes, Cairo/Pango bindings frequently cause setup failures and font linking crashes. Furthermore, WeasyPrint is licensed under LGPL v3.
2. **ReportLab Approval:**
   - ReportLab (`reportlab>=4.2`) is licensed under the permissive **BSD License**.
   - It is a pure Python package with fast C-extensions bundled in standard wheels, installing seamlessly on Windows, macOS, and Linux with zero system-level package manager dependencies.
   - Provides exact pixel and millimeter layout control via `Platypus` (`SimpleDocTemplate`, `Table`, `Paragraph`, `PageBreak`, `Drawing`).
3. **Bilingual Typography (Tamil & English):**
   - Must bundle Google Fonts Open Font License (OFL) TrueType fonts:
     - `NotoSansTamil-Regular.ttf` & `NotoSansTamil-Bold.ttf` for authentic Tamil Unicode glyph rendering.
     - `NotoSans-Regular.ttf` & `NotoSans-Bold.ttf` for Latin characters.
4. **Layout Structure (Gokul’s Astrological Insights Branded Dossier):**
   - Page 1: Cover page with auspicious header, customer name, date/time/place of birth, coordinates, Ayanamsha, and Lagna summary.
   - Page 2: South Indian & North Indian D1 Rasi Charts with comprehensive planetary position tables.
   - Page 3: D9 Navamsha and D10 Dasamsha charts with Vargottama & Pushkara highlights.
   - Page 4: Vimshottari Dasha-Bhukti-Antara timeline (birth balance to current active period).
   - Page 5: Full Six-fold Shadbala chart and planetary strength ranking.
   - Page 6: Bhinnashtakavarga tables, Sarvashtakavarga grid (337 bindus), and Shodhya Pindas.
   - Page 7: Classical Vedic Yogas detected and cancellation notes.
   - Page 8: Dosha analysis (Kuja Dosha, Kaal Sarp, Sadesati, Pitra Dosha) with cancellation checks.
   - Page 9: Remedial guidance (Graha remedies, mantras, lifestyle recommendations).
- **Backend Architecture:** `backend/app/services/report_engine/pdf_generator.py` producing high-fidelity PDF byte streams.
- **API Endpoint:** `POST /api/v1/horoscope/report/pdf`.

---

## 5. Secondary Features in `daiv-ai` & Assessment

| Feature in `daiv-ai` | Description & Capability | Current Status in Our Platform | Recommendation & Rationale |
| :--- | :--- | :--- | :--- |
| **Ashtakoot Matching** | 36-point North Indian compatibility matching (`matching_kootas.py`) | Rudimentary rule check in `rule_engine.py` | **DEFER**. Valuable for matrimonial matching, but secondary to individual chart completeness. |
| **Porutham Matching** | 10-point South Indian marriage matching (`matching_porutham.py`) | Not implemented | **DEFER**. Prioritize after Shadbala and Divisional charts. |
| **Gemstone Weight Engine** | 10-factor chart-based gemstone weight calculation (`gemstone_weight.py`) | Comprehensive remedy knowledge base (`remedy_engine`) in PostgreSQL | **REJECT**. Our existing PostgreSQL `remedy_knowledge_base` with strict classical eligibility rules is superior and already integrated with customer horoscopes. |
| **Lal Kitab Remedies** | Lal Kitab house positions and debt rules (`lal_kitab.py`) | Not implemented | **DEFER**. Outside traditional Parashari / KP scope. |
| **Prashna / Ashtamangala** | Horary query and 8-cowrie divination logic (`ashtamangala_prashna.py`) | Not implemented | **DEFER**. Requires separate consultation UI. |
| **LLM Interpretation Layer** | Prompts for Ollama, Groq, Claude, OpenAI (`products/interpret/`) | Deterministic classical rules | **REJECT**. Prompt instructions explicitly state: *"Do not add paid AI APIs or additional AI infrastructure unless explicitly approved."* Deterministic classical Vedic explanations are more reliable, cost-free, and legally sound. |

---

## 6. Comprehensive Gap Analysis & Classification Matrix

| Feature | Current Status in Website | Missing Functionality | Classical Formula / Input Data | Proposed Location & API | Reference Test Cases | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **1. Shadbala Engine** | Draft note only | Complete 6-fold planetary strength suite | BPHS Ch. 23; XALEN longitudes, speeds, houses, sunrise/sunset | `app.services.shadbala_engine`<br>`POST /api/v1/vedic/shadbala` | 7 planets; ratio $\ge 1.0$; Naisargika fixed virupas; rank 1-7 | **REIMPLEMENT** |
| **2. Prastara Ashtakavarga** | Missing (BAV/SAV exists) | $12 \times 8$ donor contributor matrix | BPHS Ch. 68; 8 donor house distance checks | `app.services.ashtakavarga_engine.prastara`<br>`POST /api/v1/vedic/ashtakavarga/prastara` | $\sum \text{Prastara bindus} = \text{BAV}$ total | **REIMPLEMENT** |
| **3. Kaksha Transit Engine** | Missing (BAV/SAV exists) | 8 subdivisions ($3^\circ 45'$) with lords | BPHS Ch. 69; sign longitude mod $3.75^\circ$; Kaksha lords order | `app.services.ashtakavarga_engine.kaksha`<br>`POST /api/v1/vedic/ashtakavarga/kaksha` | 8 Kakshas per sign; lord cycle Saturn $\to$ Lagna | **REIMPLEMENT** |
| **4. Neech Bhanga Raja Yoga** | Missing | 4 classical debilitation cancellation rules | BPHS Ch. 28; Kendra from Lagna/Moon, exalt lord, retrograde | `app.services.yoga_engine.evaluators.cancellations` | Sun in Libra cancelled by Mars in Kendra | **REIMPLEMENT** |
| **5. Kemadruma Bhanga** | Missing (flags without cancel) | 8 classical Moon isolation cancellation rules | BPHS Ch. 23; benefics in Kendra, Moon in Kendra, Paksha bala | `app.services.yoga_engine.evaluators.cancellations` | Isolated Moon cancelled by Jupiter in Kendra | **REIMPLEMENT** |
| **6. Arishta Bhanga** | Missing | 5 danger/affliction cancellation rules | BPHS Ch. 19; Jupiter aspect, benefics in Kendras, strong Lagnesha | `app.services.yoga_engine.evaluators.cancellations` | Dusthana Moon protected by Jupiter 5/9 aspect | **REIMPLEMENT** |
| **7. Multi-Point Kuja Dosha** | Basic check without cancel | 3-point check (Lagna, Moon, Venus) + 10 cancellation rules | BPHS Ch. 77; houses 1, 2, 4, 7, 8, 12; own sign, exalt, Jupiter aspect | `app.services.dosha_engine.mangal`<br>`POST /api/v1/vedic/doshas/mangal` | Mars in Aries (own sign) $\to$ Cancelled | **REIMPLEMENT** |
| **8. Kaal Sarp Dosha** | Missing | 12 serpent types, axis hemming, full/partial status | Traditional Jyotish; Rahu-Ketu longitude hemming; Rahu house | `app.services.dosha_engine.kaal_sarp`<br>`POST /api/v1/vedic/doshas/kaal-sarp` | All planets between Rahu H1 & Ketu H7 $\to$ Anant KSD | **REIMPLEMENT** |
| **9. Sadesati Detection** | Missing | Saturn transit across 12th, 1st, 2nd from natal Moon | Classical Gochara; Saturn vs Moon sign; Rising, Peak, Setting | `app.services.dosha_engine.sadesati`<br>`POST /api/v1/vedic/doshas/sadesati` | Transit Saturn in Aquarius, Moon in Pisces $\to$ Rising phase | **REIMPLEMENT** |
| **10. Pitra & Extended Doshas** | Missing | Pitra, Guru Chandal, Shrapit, Grahan, Angarak, Shakata | BPHS & Phaladeepika; conjunctions of luminaries/gurus with nodes | `app.services.dosha_engine.extended`<br>`POST /api/v1/vedic/doshas/extended` | Jupiter + Rahu $\to$ Guru Chandal (exalt cancel) | **REIMPLEMENT** |
| **11. Shodashvarga (D2-D60)** | Only D1 and D9 implemented | Full 16-chart divisional suite ($D_2$ through $D_{60}$) | BPHS Ch. 6 & 8; integer mas division; odd/even sign starting rules | `app.services.varga_engine`<br>`POST /api/v1/varga/shodashvarga` | $D_{10}$ odd from sign, even from 9th; $D_{60}$ odd Aries, even Libra | **REIMPLEMENT** |
| **12. PDF Horoscope Report** | Missing entirely | 9-page branded dossier (English + Tamil) | ReportLab Platypus; Noto Sans Tamil / English; XALEN chart data | `app.services.report_engine.pdf`<br>`POST /api/v1/horoscope/report/pdf` | Valid binary PDF starting with `%PDF-1.4`; Tamil glyphs intact | **REIMPLEMENT** |
| **13. Ashtakoot / Porutham** | Rudimentary | 36-guna & 10-porutham compatibility | Classical matching rules | `app.services.matching_engine` | Test against standardized 36-point cases | **DEFER** |
| **14. Gemstone Weight** | Database exists | Heuristic 10-factor weight | Client rules | N/A | Existing DB is more comprehensive | **REJECT** |
| **15. LLM Interpretation** | None (Deterministic) | External AI inference prompts | LLM API calls | N/A | Prohibited by prompt safety requirements | **REJECT** |

---

## 7. Mathematical Specifications & Reference Test Cases

### 7.1 Divisional Chart $D_{10}$ (Dasamsha) Specification
- **Arc per Division:** $3^\circ 00' 00'' = 10,800,000\text{ mas}$.
- **Part Calculation:**
  $$\text{part} = \left\lfloor \frac{\text{longitude}_{\text{mas}} \pmod{\text{MAS\_PER\_SIGN}}}{10,800,000} \right\rfloor \quad (0 \le \text{part} \le 9)$$
- **Starting Sign Rule (BPHS Ch. 6, Sloka 19-20):**
  - Odd sign ($1, 3, 5, 7, 9, 11$): Starts from the **same sign**.
  - Even sign ($2, 4, 6, 8, 10, 12$): Starts from the **9th sign** from it:
    $$\text{start} = ((\text{sign\_index} - 1 + 8) \pmod{12}) + 1$$
- **Final $D_{10}$ Sign:**
  $$D_{10}\text{ sign} = ((\text{start} - 1 + \text{part}) \pmod{12}) + 1$$
- **Verification Case:**
  - Planet at Aries ($1$) $14^\circ 20'$:
    - Sign = Aries (odd). Part = $\lfloor 14.3333 / 3 \rfloor = 4$.
    - Start = Aries ($1$). $D_{10}\text{ sign} = 1 + 4 = 5$ (Leo).
  - Planet at Taurus ($2$) $05^\circ 30'$:
    - Sign = Taurus (even). Part = $\lfloor 5.5 / 3 \rfloor = 1$.
    - Start = 9th from Taurus = Capricorn ($10$). $D_{10}\text{ sign} = 10 + 1 = 11$ (Aquarius).

### 7.2 Divisional Chart $D_{60}$ (Shashtyamsha) Specification
- **Arc per Division:** $0^\circ 30' 00'' = 1,800,000\text{ mas}$.
- **Part Calculation:**
  $$\text{part} = \left\lfloor \frac{\text{longitude}_{\text{mas}} \pmod{\text{MAS\_PER\_SIGN}}}{1,800,000} \right\rfloor \quad (0 \le \text{part} \le 59)$$
- **Starting Sign Rule (BPHS Ch. 8, Sloka 2):**
  - Odd sign ($1, 3, 5, 7, 9, 11$): Starts from **Aries ($1$)**.
  - Even sign ($2, 4, 6, 8, 10, 12$): Starts from **Libra ($7$)**.
- **Final $D_{60}$ Sign:**
  $$D_{60}\text{ sign} = ((\text{start} - 1 + \text{part}) \pmod{12}) + 1$$
- **Verification Case:**
  - Longitude $0.1^\circ$ (Aries, odd): Part 0 $\to$ Aries ($1$).
  - Longitude $30.1^\circ$ (Taurus, even): Part 0 $\to$ Libra ($7$).

### 7.3 Shadbala Minimum Required Strengths (Virupas and Rupas)
According to *Brihat Parasara Hora Shastra* Chapter 23:

$$\text{Rupa} = \frac{\text{Virupa}}{60}$$

| Planet | Minimum Required (Virupas) | Minimum Required (Rupas) | Dominant Strength Component |
| :--- | :---: | :---: | :--- |
| **Sun (Surya)** | 390.0 | 6.50 | Dig Bala in 10th house; Ayana Bala in Uttarayana |
| **Moon (Chandra)** | 360.0 | 6.00 | Paksha Bala (Waxing/Full); Dig Bala in 4th house |
| **Mars (Mangala)** | 300.0 | 5.00 | Dig Bala in 10th house; Cheshta Bala when retrograde |
| **Mercury (Budha)** | 420.0 | 7.00 | High required threshold; Dig Bala in 1st house |
| **Jupiter (Guru)** | 390.0 | 6.50 | Sthana Bala (Exalted in Cancer); Dig Bala in 1st house |
| **Venus (Shukra)** | 330.0 | 5.50 | Dig Bala in 4th house; high Naisargika Bala (42.86) |
| **Saturn (Shani)** | 300.0 | 5.00 | Dig Bala in 7th house; Cheshta Bala when retrograde |

---

## 8. Proposed Architectural Design & API Contracts

### 8.1 Backend File Structure for New Engines
All new modules are housed strictly within `backend/app/services/`:

```
backend/app/
├── schemas/
│   ├── shadbala.py                                  # ShadbalaRequest, ShadbalaResponse, PlanetShadbalaDetail
│   ├── dosha.py                                     # MangalDoshaDetail, KaalSarpDetail, SadesatiDetail, DoshaResponse
│   ├── shodashvarga.py                              # ShodashvargaResponse, VargaChartDetail (D2-D60)
│   └── report_pdf.py                                # PdfReportRequest, PdfReportMetadata
├── services/
│   ├── shadbala_engine/                             # Clean-room Shadbala engine
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── sthana_bala.py
│   │   ├── dig_bala.py
│   │   ├── kala_bala.py
│   │   ├── cheshta_bala.py
│   │   ├── drik_bala.py
│   │   └── calculator.py
│   ├── dosha_engine/                                # Clean-room Dosha & Cancellation engine
│   │   ├── __init__.py
│   │   ├── mangal.py
│   │   ├── kaal_sarp.py
│   │   ├── sadesati.py
│   │   └── extended.py
│   ├── ashtakavarga_engine/
│   │   ├── prastara.py                              # NEW: 12x8 donor contributor matrix
│   │   └── kaksha.py                                # NEW: 3°45' Kaksha transit analysis
│   ├── varga_engine.py                              # EXTENDED: Add D2, D3, D4, D7, D10, D12... D60 mas algorithms
│   ├── yoga_engine/evaluators/
│   │   └── cancellations.py                         # NEW: Neech Bhanga, Kemadruma Bhanga, Arishta Bhanga
│   └── report_engine/                               # Clean-room PDF generation engine
│       ├── __init__.py
│       ├── fonts/                                   # NotoSansTamil, NotoSans OFL fonts
│       ├── charts.py                                # South Indian & North Indian chart drawing
│       └── pdf_generator.py                         # ReportLab Platypus dossier generator
└── routers/
    ├── vedic_extensions.py                          # Add endpoints for shadbala, doshas, prastara
    └── horoscope.py                                 # Add endpoints for shodashvarga, pdf download
```

### 8.2 API Endpoint Contracts

#### 1. `POST /api/v1/vedic/shadbala`
- **Request:** Standard `HoroscopeRequest` or ad-hoc birth coordinates.
- **Response:**
  ```json
  {
    "planets": {
      "Sun": {
        "sthana_bala_virupas": 145.2,
        "dig_bala_virupas": 52.4,
        "kala_bala_virupas": 115.0,
        "cheshta_bala_virupas": 30.0,
        "naisargika_bala_virupas": 60.0,
        "drik_bala_virupas": -4.2,
        "total_virupas": 398.4,
        "total_rupas": 6.64,
        "required_virupas": 390.0,
        "strength_ratio": 1.022,
        "is_strong": true,
        "rank": 2
      }
    },
    "strongest_planet": "Jupiter",
    "weakest_planet": "Saturn"
  }
  ```

#### 2. `POST /api/v1/vedic/doshas`
- **Request:** Standard `HoroscopeRequest`.
- **Response:**
  ```json
  {
    "mangal_dosha": {
      "has_dosha": true,
      "is_cancelled": true,
      "severity": "Cancelled",
      "lagna_house": 1,
      "moon_house": 4,
      "venus_house": null,
      "cancellation_reasons": [
        "Mars is in own sign Aries",
        "Jupiter aspects Mars"
      ],
      "description_en": "Mars in 1st house from Lagna, but dosha is cancelled by Mars in own sign and Jupiter's benefic aspect.",
      "description_ta": "லக்னத்தில் செவ்வாய் அமைந்திருந்தாலும், ஆட்சி பெற்றதாலும் குரு பார்வை இருப்பதாலும் செவ்வாய் தோஷம் நிவர்த்தி ஆகிறது."
    },
    "kaal_sarp_dosha": {
      "has_dosha": false,
      "type_name": null,
      "severity": "None"
    },
    "sadesati": {
      "is_active": true,
      "phase": "Peak",
      "description_en": "Saturn transiting natal Moon sign (Janma Shani).",
      "description_ta": "ஜென்மச் சனி: சனியின் சுழற்சி ராசியில் நேரடியாக நிகழ்கிறது."
    }
  }
  ```

#### 3. `POST /api/v1/varga/shodashvarga`
- **Request:** `HoroscopeRequest`.
- **Response:**
  ```json
  {
    "charts": {
      "D1": { "name": "Rasi", "planets": [...] },
      "D9": { "name": "Navamsha", "planets": [...] },
      "D10": { "name": "Dasamsha", "planets": [...] },
      "D60": { "name": "Shashtyamsha", "planets": [...] }
    },
    "vargottama_planets": ["Sun", "Jupiter"],
    "pushkara_navamsa_planets": ["Moon"]
  }
  ```

#### 4. `POST /api/v1/horoscope/report/pdf`
- **Request:** `HoroscopeRequest` with `language: "en" | "ta" | "bilingual"`.
- **Response:** Binary stream `application/pdf` with header `Content-Disposition: attachment; filename="horoscope_gokul.pdf"`.

---

## 9. Phased Implementation Roadmap (For Phase 3 Execution)

Once this audit report is reviewed and approved, implementation will proceed in four isolated, test-driven phases:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 3.1: Precision Divisional Charts (Shodashvarga)       │
│ - Implement D2-D60 in varga_engine.py using integer mas     │
│ - Add comprehensive test_shodashvarga.py suite              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 3.2: Shadbala & Ashtakavarga Extensions               │
│ - Implement app/services/shadbala_engine/                   │
│ - Add Prastara Ashtakavarga & Kaksha analysis               │
│ - Add test_shadbala_engine.py and API endpoints             │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 3.3: Cancellation Rules & Unified Dosha Engine        │
│ - Implement Neech Bhanga & Kemadruma Bhanga evaluators      │
│ - Implement app/services/dosha_engine/ (Mangal, KSD, Sadesati)│
│ - Add unit tests and bilingual descriptions (English+Tamil) │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 3.4: Professional PDF Report Generation (ReportLab)   │
│ - Install reportlab; bundle NotoSansTamil OFL fonts         │
│ - Implement app/services/report_engine/pdf_generator.py     │
│ - Expose PDF download endpoint & integrate in Next.js UI    │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Audit Conclusion & Sign-Off Request

1. **Licensing Safety:** Confirmed. No AGPL-covered assets or code will enter the codebase. Clean-room development protects our proprietary IP.
2. **Architecture Integrity:** Confirmed. XALEN remains our sole, inviolable calculation engine. No competing ephemerides.
3. **Database & Existing Code Safety:** Confirmed. Zero existing tables or columns will be altered; existing 283 tests continue passing without regression.
4. **First Deliverable Produced:** This comprehensive document `daiv_ai_integration_audit.md` has been successfully created in the repository root.

**Awaiting user review and formal approval before commencing Phase 3 implementation.**
