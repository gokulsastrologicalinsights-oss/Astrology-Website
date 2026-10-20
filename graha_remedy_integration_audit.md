# Technical & Licensing Integration Audit: Graha Remedy

**Audited Repository:** [https://github.com/git-pranesh/graha-remedy](https://github.com/git-pranesh/graha-remedy)  
**Target Platform:** Gokul’s Astrological Insights  
**Auditor:** Antigravity (Google DeepMind Advanced Agentic Coding)  
**Audit Date:** October 18, 2026  
**Status:** Completed (Phase 1: Read-Only Audit)  
**Deliverable Path:** `graha_remedy_integration_audit.md`  

---

## 1. Executive Summary

An exhaustive technical, astrological, algorithmic, and licensing audit of the repository `git-pranesh/graha-remedy` was conducted to determine whether its remedy knowledge base, problem-to-remedy mappings, and recommendation rules can safely, authentically, and legally be integrated into **Gokul’s Astrological Insights**.

### Core Verdict: CONDITIONAL GO (Strict Clean-Room Re-implementation Only)

1. **Strict Code REJECT (AGPL-3.0 Copyleft Barrier):**  
   The entire repository is explicitly licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**, with core calculation modules tightly coupled to `@swisseph/node` (Swiss Ephemeris AGPL option). Direct copying or transpiling of any TypeScript, JavaScript, or Express/Next.js code from `graha-remedy` into Gokul’s proprietary codebase would trigger viral copyleft obligations under AGPL Section 13 (Remote Network Interaction), compelling Gokul's Astrological Insights to open-source its entire backend, frontend, proprietary XALEN ephemeris bridges, and Supabase integration.

2. **Calculation Engine REJECT (XALEN Engine Inviolability):**  
   Graha Remedy relies on `@swisseph/node` for planetary calculations. In accordance with platform safeguards, **under no circumstances will XALEN or the existing KP calculation engine be replaced, modified, or wrapped by Swiss Ephemeris / AGPL software**. Gokul's Astrological Insights already possesses a superior, high-precision native astronomical engine.

3. **Knowledge Base & Conceptual Diagnostic ADAPT:**  
   The repository contains a valuable, structured taxonomy of **39 real-world problem categories**, planetary correspondences (ruling elements, body parts, afflictions), and a diagnostic scoring concept (weighting house lords +20, natural karakas +15, active Mahadasha +25, Antardasha +15, afflictions +15, and Neecha Bhanga cancellation). However, the existing data files suffer from **corrupted mantra transliterations** (e.g., garbled Gayatri and Katyayani mantras), **missing classical scriptural citations**, **fatal astrological bugs** (e.g., flagging individual charts with "Nadi Dosha", calculating Sade Sati from natal Saturn), and **zero authentic Tamil Navagraha temple data**.

4. **Integration Path:**  
   All valid problem concepts and planetary remedy associations must be **clean-room re-engineered** as native Python Pydantic models and FastAPI services in `backend/app/services/remedy_engine/`, backed by dedicated tables in Supabase. All remedies must be verified against classical Jyotish canons (Brihat Parashara Hora Shastra, Mantra Mahodadhi, Phaladeepika) and fully localized into Tamil with Kaveri Delta Navagraha temple records.

---

## 2. Repository Structure & Technical Architecture

### 2.1 Directory Structure & File Inventory

The repository is organized as a monorepo containing a legacy Node.js/Express backend, a modern Next.js 15 App Router frontend, a file-backed JSON data layer, and utility scripts:

```
scratch/graha-remedy/
├── .freebuff/
│   └── run.md                               # Dev launch scripts & ports (3001 backend, 5173 frontend)
├── backend/                                 # Legacy Node.js + Express + TypeScript service
│   ├── src/
│   │   ├── index.ts                         # Express server entry point (port 3001)
│   │   ├── utils.ts                         # File I/O helpers (readJsonData)
│   │   ├── routes/
│   │   │   ├── auth.ts                      # File-backed cookie JWT authentication
│   │   │   ├── chart.ts                     # Chart calculation endpoint
│   │   │   ├── personalized.ts              # Personalized remedies endpoint
│   │   │   ├── planets.ts                   # Planetary metadata endpoint
│   │   │   ├── remedies.ts                  # Raw remedy catalog endpoint
│   │   │   ├── remedyRules.ts               # Problem-to-remedy lookup endpoint
│   │   │   ├── reports.ts                   # Report saving & retrieval
│   │   │   └── universal.ts                 # Universal remedy categories endpoint
│   │   └── services/
│   │       ├── astro-engine.ts              # @swisseph/node planetary engine (Lahiri)
│   │       ├── chart.ts                     # Geocoding + birth chart orchestration
│   │       ├── chart-cache.ts               # In-memory/file chart caching
│   │       ├── dosha.ts                     # [UNPATCHED] Dosha evaluation (Manglik, Sade Sati, Nadi)
│   │       ├── geocoder.ts                  # OSM Nominatim client (rate-limited 1 req/sec)
│   │       ├── json-store.ts                # Atomic JSON file storage (users.json, reports.json)
│   │       ├── overpass-temples.ts          # Overpass OSM API query client
│   │       ├── rules-engine.ts              # Affliction scoring & diagnostic engine (32 KB)
│   │       └── temple-matcher.ts            # Temple matcher (OSM Overpass + static fallback)
│   ├── tests/
│   │   └── rules-engine.test.ts             # Vitest test suite (mock chart scenarios)
│   ├── package.json                         # AGPL-3.0-or-later, @swisseph/node ^1.3.1
│   └── test-chart.mts                       # Standalone CLI chart calculation verification
├── data/                                    # File-based JSON Knowledge Base
│   ├── planets/
│   │   └── planets.json                     # 9 Grahas: Sanskrit, elements, body parts, karakatwas (5 KB)
│   ├── remedies/
│   │   ├── remedies.json                    # Planetary remedies: mantras, fasting, daan, puja (17 KB)
│   │   └── universal.json                   # Universal remedies: Ganesha, health, finance, etc. (11 KB)
│   ├── remedies_by_problem/
│   │   └── remedies_by_problem.json         # 39 problem keys mapped to planet arrays (2 KB)
│   ├── temples/
│   │   └── temples.json                     # 46 general temples from rishabhmodi03/hindu-temples (8.6 KB)
│   ├── seo_pages/                           # 34 JSON articles (15 duplicated pairs with - and _)
│   ├── seo_research/                        # SEO keyword matrices, SERP data, Koala briefs
│   ├── koala_content_instructions.txt       # AI writer prompting directives
│   └── koala_banned_words.txt               # Negative constraint prompts for AI generator
├── frontend/                                # Next.js 15.5.2 (React 19, TypeScript) App Router
│   ├── app/
│   │   ├── api/                             # Serverless API routes (remedies, panchang, chart, auth)
│   │   ├── calculators/                     # Standalone Vedic calculators (Lagna, Nakshatra, Dasha)
│   │   ├── choghadiya/                      # Daily Choghadiya tables for 82 cities
│   │   ├── panchang/                        # Daily Panchang tables for 82 cities
│   │   ├── remedies/                        # Dynamic remedy landing pages ([slug])
│   │   ├── ta/                              # Tamil panchangam and calendar routes ([city], [year])
│   │   ├── te/                              # Telugu panchangam and calendar routes
│   │   └── hi/                              # Hindi festival, panchang, and choghadiya routes
│   ├── src/
│   │   ├── components/                      # React UI components (GowriTable, NallaNeramPage, etc.)
│   │   ├── data/
│   │   │   └── places.json                  # GeoNames offline cities dataset (5.78 MB, CC BY 4.0)
│   │   ├── lib/
│   │   │   ├── gowri.ts                     # Gowri Panchangam weekday tables (with bug on Saturday)
│   │   │   └── i18n-south.ts                # Tamil & Telugu Panchang translation keys
│   │   └── services/
│   │       ├── astro-engine.ts              # Duplicate of backend astro-engine with @swisseph/node
│   │       ├── dosha.ts                     # [PATCHED in 4e70a78] Fixed Nadi & transiting Sade Sati
│   │       ├── panchang.ts                  # Swiss Ephemeris daily almanac engine
│   │       ├── rules-engine.ts              # Duplicate of backend rules engine
│   │       └── transits.ts                  # Saturn transit span calculator (Julian Day)
│   └── package.json                         # AGPL-3.0-or-later, @swisseph/node ^1.3.1, Next 15.5.2
├── scripts/                                 # Content generation & automation scripts
│   ├── generate-sample-gemini.js            # Calls OpenRouter (google/gemini-3.8-flash) to write articles
│   ├── generate-cluster-a-mantras.js        # Automated bulk AI generation of mantra pages
│   ├── generate-clusters-b-c-d.js           # Automated bulk AI generation of beej mantra pages
│   ├── research-seo-keywords.js             # DataForSEO / SERP analysis
│   └── build-places.py                      # GeoNames data parser
├── LICENSE                                  # Full GNU Affero General Public License v3.0 text
├── package.json                             # Root workspace runner (concurrently backend + frontend)
├── vercel.json                              # Production Vercel deployment config (bom1 region)
└── README.md                                # Public documentation & claims
```

### 2.2 Technical Stack & Architecture

1. **Dual-Architecture Drift:**
   The repository originated as an Express.js backend (`backend/src/index.ts` on port 3001) paired with a frontend client. Later, the project migrated calculation services directly into Next.js App Router API routes (`frontend/app/api/`) for single-deployment on Vercel. 
   **Critical Defect:** When bug fixes were made in commit `4e70a78` (fixing transit-based Sade Sati and Ashtakoota Nadi), they were applied **only to `frontend/src/services/dosha.ts`**. The `backend/src/services/dosha.ts` file was abandoned with known erroneous logic.

2. **Calculation Flow:**
   ```
   [User Input: Date, Time, Place, Problems]
                    │
                    ▼
     [Geocoding: Places.json / Nominatim]
                    │
                    ▼
   [Astro Engine: @swisseph/node (Lahiri Ayanamsa)]
                    │
                    ▼
       [Chart: Positions, Bhavas, Dashas]
                    │
                    ▼
        [Dosha Service: Manglik, Sade Sati]
                    │
                    ▼
   [Rules Engine: diagnoseResponsiblePlanets()]
   - House Lord (+20)
   - Karaka (+15)
   - Mahadasha (+25) / Antardasha (+15)
   - Chart Afflictions (+15, Neecha Bhanga checks)
                    │
                    ▼
   [Remedies Catalog: JSON Lookup (Mantras, Vrat, Daan)]
   ```

3. **External Network Calls:**
   - **OpenStreetMap Nominatim (`geocoder.ts`):** `https://nominatim.openstreetmap.org/search` (rate limited to 1.1s).
   - **OpenStreetMap Overpass API (`overpass-temples.ts`):** `https://overpass-api.de/api/interpreter` querying `amenity=place_of_worship, religion=hindu` within 25 km radius. Note: In `personalized.ts` (lines 49-51), Overpass execution was disabled and stubbed out with `templeMatches = {}`.
   - **OpenRouter API (`scripts/generate-sample-gemini.js`):** `https://openrouter.ai/api/v1/chat/completions` using model `google/gemini-3.8-flash`.

---

## 3. Remedy Dataset Inventory

| Dataset File | File Size | Record Count | Structure & Key Attributes | Usability Assessment |
| :--- | :--- | :--- | :--- | :--- |
| [`data/planets/planets.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/planets/planets.json) | 5,093 B | 9 Grahas | `id`, `name`, `sanskrit`, `element`, `nature`, `day`, `color`, `gemstone`, `bodyParts`, `governs`, `weaknessCauses` | **Usable conceptually**. Factual astronomical/Jyotish correspondences. Public domain facts. |
| [`data/remedies/remedies.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies/remedies.json) | 16,966 B | 9 Grahas (461 lines) | Per planet: `mantras` (namaha, beej, stotram), `fasting`, `donations`, `pujaSteps`, `temples`, `deity`, `deityDescription` | **Flawed**. Contains corrupt transliterations, missing scripture verses, zero Tamil records. |
| [`data/remedies/universal.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies/universal.json) | 10,880 B | 7 Categories (253 lines) | `foundation` (Ganesha), `categories` (health, finance, career, relationships, mental_peace, litigation), `general` | **Partially usable**. Contains severe Sanskrit textual errors (Gayatri, Katyayani). |
| [`data/remedies_by_problem/remedies_by_problem.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies_by_problem/remedies_by_problem.json) | 1,953 B | 39 Problem mappings | Key = problem string (e.g. `career_delay`), Value = array of 2-4 planet IDs (`["saturn", "sun", "jupiter"]`) | **High conceptual value**. Clean taxonomy of user life concerns, but requires chart evaluation. |
| [`data/temples/temples.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/temples/temples.json) | 8,627 B | 46 Temples | `id`, `name`, `city`, `state`, `deity`, `lat`, `lon`, `famous` (source: `rishabhmodi03/hindu-temples`, MIT) | **REJECT**. Only 46 general North/West Indian temples. Contains **zero** Tamil Navagraha temples. |
| [`data/seo_pages/*.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/seo_pages/) | ~380 KB total | 34 Files (17 unique) | `seo_title`, `meta_desc`, `content_html` | **REJECT**. AI-generated marketing copy produced via OpenRouter/Gemini. 15 duplicate file pairs. |
| [`frontend/src/data/places.json`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/frontend/src/data/places.json) | 5.78 MB | Thousands of cities | GeoNames dataset (name, lat, lon, timezone, country) | **REJECT copy**. Gokul's platform already has city lookup and native timezone services. |

---

## 4. Rule and Content Quality Assessment

### 4.1 Mantra Text and Transliteration Inaccuracies

A granular review of Sanskrit mantras in `remedies.json` and `universal.json` revealed severe textual errors, garbled transliterations, and invented verses:

1. **Gayatri Mantra Corruption ([`universal.json#L184`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies/universal.json#L184)):**
   - *Graha Remedy text:* `Om Bhur Bhu-vaḥ Su-vah Ta-tsa-vi-tur Va-reṇyam Bha-go-va-sy Dhi-ma-hi Dhi-yo Yo Naḥ Pra-cho-dayaat`
   - *Error:* `Bha-go-va-sy Dhi-ma-hi` is phonetically and grammatically corrupted.
   - *Classical Standard (Rigveda 3.62.10):* `ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात् ॥` (`Bhargo Devasya Dhimahi`). Chanting corrupted syllables contradicts Vedic tradition (*Mantra Bhrashta*).

2. **Surya Gayatri Mantra Inaccuracy ([`remedies.json#L20-L24`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies/remedies.json#L20-L24)):**
   - *Graha Remedy text:* `"Surya Gayatri Mantra"`, transliteration: `"Om Bhaaskaraaya Namaha | Om Jap Suryaya Sahasraanaam"`
   - *Error:* This is not the Gayatri meter at all. It is a fragmented mixture of a Namaha chant and a japa instruction.
   - *Classical Standard (Mahanarayana Upanishad / Vedic canon):*  
     `ॐ भास्कराय विद्महे दिवाकराय धीमहि तन्नः सूर्यः प्रचोदयात् ॥`  
     (`Om Bhaskaraya Vidmahe Divakaraya Dhimahi Tanno Suryah Prachodayat`).

3. **Katyayani Mantra Distortion ([`universal.json#L154`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/data/remedies/universal.json#L154)):**
   - *Graha Remedy text:* `Om Ka-tya-ya-nyai Vi-dma-he Ka-n-ka-ta-ya Dhi-ma-hi Tha-n-no Da-rghi Pra-cho-dayaat`
   - *Error:* The words `Ka-n-ka-ta-ya` and `Da-rghi` are nonsensical distortions.
   - *Classical Standard:*  
     `ॐ कात्यायन्यै च विद्महे कन्याकुमार्यै धीमहि तन्नோ துர்கி: ப்ரசோதயாத் ॥`  
     (`Om Katyayanyai Cha Vidmahe Kanyakumaryai Dhimahi Tanno Durgih Prachodayat`) or the classical marriage prayer from Srimad Bhagavatam (10.22.4):  
     `कात्यायनि महामाये महायोगिन्यधीश्वरि । नन्दगोपसुतं देवि पतिं मे कुरु ते नमः ॥`

4. **Transliteration Missing for Major Stotrams:**
   In `remedies.json` and `universal.json`, major stotrams such as *Aditya Hridayam*, *Durga Saptashati*, *Vishnu Sahasranamam*, *Sudarshana Ashtakam*, and *Kanakadhara Stotram* provide zero Sanskrit text or transliteration, giving only descriptions like `"(15 verses from the Rigveda)"` or `"(8 verses dedicated to Lord Sudarshana)"`.

### 4.2 Astrological Errors and Unverified Claims

1. **The Single-Chart "Nadi Dosha" Fallacy ([`backend/src/services/dosha.ts#L247-L261`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/backend/src/services/dosha.ts#L247-L261)):**
   - In `backend/src/services/dosha.ts`, the engine checks whether a person's Moon nakshatra belongs to *Aadi Nadi*. If yes, it sets `nadi: true` and flags the chart with **"Nadi Dosha"**.
   - **Astrological Verdict:** Complete fabrication. In classical Jyotish (BPHS Chapter 44, Muhurta Chintamani), *Nadi Dosha* is strictly an **Ashta Kuta synastry (compatibility) metric** between two birth charts (bride and groom). An individual natal chart **never has Nadi Dosha**. Flagging a single person with Nadi Dosha causes unwarranted distress and violates classical principles.
   - *Note:* While `frontend/src/services/dosha.ts` partially commented this out in commit `4e70a78`, `backend/src/services/dosha.ts` still actively runs this flawed logic.

2. **Corrupted Nakshatra Nadi Table in Backend ([`backend/src/services/dosha.ts#L40-L68`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/backend/src/services/dosha.ts#L40-L68)):**
   - The classical Nadi allocation across 27 nakshatras follows an exact 9/9/9 tripartite distribution (1-2-3-3-2-1 snake progression).
   - In `backend/src/services/dosha.ts`, line 37 states: `// Antya Naid: — none typically listed, but we use the remaining ones`. The table assigns:
     - 12 Nakshatras to Aadi (including Bharani and Krittika, which are Madhya and Antya!)
     - 8 Nakshatras to Madhya
     - 7 Nakshatras to Antya
   - This table is mathematically and astrologically invalid.

3. **Natal Sade Sati Bug ([`backend/src/services/dosha.ts#L170-L192`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/backend/src/services/dosha.ts#L170-L192)):**
   - In `backend/src/services/dosha.ts`, `computeSadeSati` calculates distance between **natal Moon** and **natal Saturn**.
   - If a person is born with Saturn in the 12th, 1st, or 2nd from natal Moon, the backend permanently flags them as undergoing Sade Sati for their entire life!
   - Sade Sati is strictly a **planetary transit (Gochar)** event occurring when *transiting* Saturn moves through the 12th, 1st, and 2nd houses from natal Moon.

4. **Sun in 9th House Labeled as "Pitra Dosha" ([`backend/src/services/dosha.ts#L222`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/backend/src/services/dosha.ts#L222)):**
   - The engine automatically triggers *Pitra Dosha* simply if `sun.house === 9`.
   - In Parashari astrology, Sun is the *Karaka* of the 9th house (Dharma/Father/Fortune). While some later schools debate *Karako Bhava Nashaya*, Sun in the 9th forms powerful Raja Yogas (e.g., for Aries, Sagittarius, Scorpio Lagna). Blanket categorization as Pitra Dosha without Rahu/Ketu/Saturn affliction is misleading.

5. **Gowri Panchangam Table Typo ([`frontend/src/lib/gowri.ts#L7`](file:///e:/GAI/Astrology%20Website/scratch/graha-remedy/frontend/src/lib/gowri.ts#L7)):**
   - In `GOWRI_NIGHT` for Saturday (index 6):  
     `["Laabam", "Dhanam", "Sugam", "Soram", "Uthi", "Visham", "Amirdha", "Soram"]`
   - `Soram` appears twice (at slots 4 and 8), while `Rogam` (the traditional malefic slot) is completely omitted.

6. **Dangerous Problem-to-Remedy Omission: Yogakaraka Blindness:**
   - In `data/remedies_by_problem/remedies_by_problem.json` and `backend/src/routes/remedyRules.ts`, if a user selects `career_delay`, the endpoint recommends remedies for Saturn, Sun, and Jupiter.
   - The system recommends **Daan (donation)** and pacification rituals for those planets **without checking whether the planet is a functional benefic or Yogakaraka**!
   - In classical Jyotish (BPHS, Mantreswara’s Phaladeepika):
     > *A functional benefic or Yogakaraka planet (such as Saturn for Taurus/Libra Lagna, or Mars for Cancer/Leo Lagna) must NEVER be propitiated via Daan (donation of its significations), as giving away its items disperses its auspicious strength.*
   - Recommending black sesame / iron donation to a Taurus Lagna native because of "career delay" actively damages their 9th/10th Yogakaraka.

7. **Duplication and Artificial SEO Generation:**
   - The repository claims: *"All results are calculated with the Swiss Ephemeris; no AI-written readings."* (README line 3).
   - In reality, `data/seo_pages/` contains **34 JSON articles** generated by `scripts/generate-sample-gemini.js`, `generate-cluster-a-mantras.js`, and `generate-clusters-b-c-d.js` calling OpenRouter (`google/gemini-3.8-flash`).
   - 15 files are exact duplicates created by inconsistent script naming (hyphen vs underscore):
     - `chandra-mantra.json` == `chandra_mantra.json`
     - `evil-eye-remedies.json` == `evil_eye_remedies.json`
     - `ketu-mantra.json` == `ketu_mantra.json`
     - `ketu-remedy.json` == `ketu_remedy.json`
     - `mangal-mantra.json` == `mangal_mantra.json`
     - `mercury-planet-remedies.json` == `mercury_planet_remedies.json`
     - `moon-remedies.json` == `moon_remedies.json`
     - `rahu-mantra.json` == `rahu_mantra.json`
     - `rahu-remedies.json` == `rahu_remedies.json`
     - `shani-beej-mantra.json` == `shani_beej_mantra.json`
     - `shani-mantra.json` == `shani_mantra.json`
     - `shukra-beej-mantra.json` == `shukra_beej_mantra.json`
     - `shukra-mantra.json` == `shukra_mantra.json`
     - `surya-mantra.json` == `surya_mantra.json`
     - `vedic-astrology-remedies.json` == `vedic_astrology_remedies.json`

---

## 5. Licence and Dependency Risks

### 5.1 AGPL-3.0-or-Later Legal Obligations

The repository root `LICENSE`, `package.json`, `backend/package.json`, and `frontend/package.json` are governed by the **GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**.

```
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
Section 13: Remote Network Interaction
"Notwithstanding any other provision of this License, if you modify the Program, 
your modified version must prominently offer all users interacting with it remotely 
through a computer network... an opportunity to receive the Corresponding Source 
of your version by providing access to the Corresponding Source from a network 
server at no charge, through some standard or customary means of facilitating 
copying of software."
```

#### Legal Impact on Gokul's Astrological Insights:
1. **Viral Incompatibility with Proprietary Code:**  
   If any TypeScript, Python, or JavaScript code from `graha-remedy` is copied, adapted, or linked into Gokul's Astrological Insights, the AGPL copyleft clause extends to the **entire combined work**. Gokul's platform would be legally obligated to release the complete source code of its FastAPI backend, Next.js frontend, Supabase schemas, and proprietary calculation wrappers under AGPL-3.0.
2. **Strict Clean-Room Requirement:**  
   To prevent copyleft contamination, **not a single line of source code from `graha-remedy` may be copied, imported, or adapted**. Only non-copyrightable astrological concepts, public-domain shastra rules, and problem taxonomies may be re-implemented independently.

### 5.2 Swiss Ephemeris Dual-Licence Risk

- Graha Remedy uses `@swisseph/node` under the AGPL option of Swiss Ephemeris (Astrodienst AG).
- Swiss Ephemeris is dual-licensed:
  1. **GNU AGPL-3.0:** Free of charge, but forces the calling application to be 100% AGPL-3.0.
  2. **Commercial License:** Requires purchasing a paid license from Astrodienst AG for closed-source or commercial use.
- **Platform Safeguard Compliance:**  
  Gokul’s Astrological Insights uses its own native `XALEN ephemeris` engine. Rejecting `@swisseph/node` and retaining XALEN completely avoids both AGPL contamination and commercial licensing fees.

### 5.3 Third-Party Dependency Licences

| Dependency / Component | Upstream Licence | Commercial Compatibility | Platform Risk |
| :--- | :--- | :--- | :--- |
| `git-pranesh/graha-remedy` Code | **AGPL-3.0-or-later** | ❌ Incompatible with closed-source | **Extreme (Viral Copyleft)** |
| `@swisseph/node` | **AGPL-3.0 / Commercial** | ❌ Requires commercial license if not AGPL | **High (Redundant with XALEN)** |
| `rishabhmodi03/hindu-temples` | MIT | ✅ Fully Compatible | Low (Dataset inadequate anyway) |
| `GeoNames` (`places.json`) | CC BY 4.0 | ✅ Permitted with attribution | Low (Gokul already has geo services) |
| OpenStreetMap Overpass & Nominatim | ODbL / Acceptable Use Policy | ⚠️ Fragile (Rate limits, IP bans) | **Medium (Violates zero external API rule)** |
| OpenRouter / Gemini 3.8 Flash | Commercial API Terms | ❌ Paid third-party API | **High (Violates zero paid API rule)** |

---

## 6. REUSE / ADAPT / REJECT Decision Matrix

| Component / File Path | Upstream Status | Quality / Accuracy | Verdict | Rationale & Remediation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Astronomical Engine** (`backend/src/services/astro-engine.ts`, `frontend/src/services/astro-engine.ts`) | AGPL-3.0, `@swisseph/node` | Functionally accurate Lahiri, but uses Swiss Ephemeris | **REJECT** | **Do not touch.** Gokul’s platform already has the native XALEN ephemeris engine. Importing `@swisseph/node` would violate safeguards and trigger AGPL obligations. |
| **Backend Dosha Service** (`backend/src/services/dosha.ts`) | AGPL-3.0 | ❌ Unpatched, fatal errors (natal Sade Sati, single-chart Nadi dosha, corrupted Nadi table) | **REJECT** | Inaccurate, misleading, and legally encumbered. |
| **Frontend Dosha Service** (`frontend/src/services/dosha.ts`, `transits.ts`) | AGPL-3.0 | Partially corrected transit Sade Sati, correct Ashtakoota table | **REJECT (Code) / ADAPT (Logic)** | Do not copy code. Transit-based Sade Sati is standard classical Gochar; implement cleanly in Python using XALEN ephemeris. |
| **Rules Engine** (`backend/src/services/rules-engine.ts`) | AGPL-3.0 | Good diagnostic weighting model (+20 lord, +15 karaka, +25 dasha, Neecha Bhanga) | **REJECT (Code) / ADAPT (Logic)** | Re-implement the diagnostic weighting algorithm from scratch in Python (`remedy_engine/scoring.py`), adding Yogakaraka protections and combustion checks. |
| **Planetary Attributes** (`data/planets/planets.json`) | Public domain facts | Factual classical correspondences (body parts, colors, days, gemstones) | **ADAPT** | Cleanse factual correspondences into Python constants or Supabase lookup table. Do not copy JSON file directly. |
| **Remedy Catalog** (`data/remedies/remedies.json`) | Cultural canon / AGPL container | Mantras incomplete, missing verses, zero Tamil records | **ADAPT** | Re-curate mantras and rituals against classical texts (BPHS, Mantra Mahodadhi). Add Devanagari, English IAST, and Tamil script. |
| **Universal Remedies** (`data/remedies/universal.json`) | Cultural canon / AGPL container | Corrupt transliterations (Gayatri, Katyayani) | **ADAPT** | Fix corrupted transliterations against Rigveda and Srimad Bhagavatam; integrate into Supabase remedy catalog. |
| **Problem Taxonomy** (`data/remedies_by_problem/remedies_by_problem.json`) | Factual mapping | 39 practical life problems | **ADAPT** | Use the 39 problem keys as the UX taxonomy for Gokul’s frontend problem selector, but map through the full chart diagnostic engine. |
| **Temples Dataset** (`data/temples/temples.json`) | MIT (`hindu-temples`) | ❌ 46 temples only; **0** Tamil Navagraha temples | **REJECT** | Curate an authentic dataset of the 9 Kaveri Delta Navagraha Temples (Suryanar Kovil, Thingalur, etc.) with Tamil names and sthala purana. |
| **OSM Overpass Client** (`overpass-temples.ts`, `geocoder.ts`) | AGPL-3.0, ODbL | Dependent on external HTTP calls, fragile, rate-limited | **REJECT** | Violates platform safeguard against introducing external API dependencies. Use curated database instead. |
| **SEO Content & AI Scripts** (`data/seo_pages/`, `scripts/*.js`) | Generated via OpenRouter Gemini 3.8 Flash | Contains 15 duplicate file pairs; generic SEO copy | **REJECT** | Violates platform safeguard against AI/LLM generation and external APIs. |
| **Authentication & Store** (`backend/src/routes/auth.ts`, `json-store.ts`) | File-based JSON (`users.json`, `reports.json`) | ❌ Insecure file storage | **REJECT** | Gokul's platform already utilizes Supabase PostgreSQL authentication, JWT, and RLS policies. |
| **Gowri Panchangam** (`frontend/src/lib/gowri.ts`) | Cultural formula | Saturday night typo (duplicate `Soram`, missing `Rogam`) | **ADAPT** | Correct Saturday night table and implement natively in Gokul’s Muhurta engine in Python. |
| **South Indian I18n** (`frontend/src/lib/i18n-south.ts`) | Factual translations | Good Tamil/Telugu panchang terminology | **ADAPT** | Incorporate Tamil terminology for Tithi, Nakshatra, Yoga, and Karana into Gokul's frontend dictionary. |

---

## 7. Proposed Integration Architecture

To maintain the architectural integrity of Gokul’s Astrological Insights, preserve the inviolability of XALEN, and respect AGPL-3.0 boundaries, the integration must follow a **Clean-Room Design Pattern**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND: Next.js (TypeScript)                    │
│  - Problem Selector UI (39 curated concerns in English & Tamil)        │
│  - Remedy Card Component (Mantra, Vrat, Daan, Temple, Why Prescribed)  │
│  - Tamil / English Dual Script Display & Audio Transliteration Guide   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP POST /api/v1/remedies/diagnose
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      BACKEND: FastAPI (Python)                         │
│  app/routers/remedies.py                                               │
│  app/services/remedy_engine/                                           │
│  ├── diagnostics.py   <── Evaluates chart afflictions + dasha timing   │
│  ├── protections.py   <── Safeguards Yogakarakas & functional benefics │
│  ├── matching.py      <── Matches afflicted lords to remedies          │
│  └── models.py        <── Pydantic request/response schemas            │
└──────────────┬──────────────────────────────────────────┬──────────────┘
               │ Calls                                    │ Queries
               ▼                                          ▼
┌───────────────────────────────┐     ┌──────────────────────────────────┐
│     NATIVE XALEN ENGINE       │     │        SUPABASE DATABASE         │
│  - calculate_full_horoscope() │     │  - remedies_catalog              │
│  - Planet positions & houses  │     │  - remedies_problem_map          │
│  - Vimshottari Dasa / Antar   │     │  - navagraha_temples (Tamil Nadu)│
│  - Classical Drishti & Yogas  │     │  - user_remedy_reports (RLS)     │
└───────────────────────────────┘     └──────────────────────────────────┘
```

### 7.1 Database Schema (Supabase PostgreSQL)

Clean-room schema design to store verified remedies without any dependency on external JSON files:

```sql
-- 1. Master remedies catalog
CREATE TABLE public.remedies_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graha VARCHAR(20) NOT NULL, -- 'sun', 'moon', 'mars', etc.
    remedy_type VARCHAR(30) NOT NULL, -- 'mantra_namaha', 'mantra_beej', 'stotram', 'vrat', 'daan', 'puja', 'temple'
    title_en TEXT NOT NULL,
    title_ta TEXT NOT NULL,
    deity_en TEXT NOT NULL,
    deity_ta TEXT NOT NULL,
    sanskrit_devanagari TEXT,
    transliteration_iast TEXT,
    transliteration_ta TEXT,
    practice_instructions_en TEXT NOT NULL,
    practice_instructions_ta TEXT NOT NULL,
    recommended_count INT DEFAULT 108,
    classical_source TEXT, -- e.g., 'Brihat Parashara Hora Shastra 58.12-14'
    is_pacification_only BOOLEAN DEFAULT FALSE, -- TRUE = Daan / Kavach for afflicted malefics
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Problem-to-Graha Karakatwa mapping
CREATE TABLE public.remedies_problem_taxonomy (
    problem_key VARCHAR(50) PRIMARY KEY, -- 'career_delay', 'marriage_delay', etc.
    category VARCHAR(30) NOT NULL, -- 'career', 'relationships', 'health', 'finance', 'spiritual'
    label_en TEXT NOT NULL,
    label_ta TEXT NOT NULL,
    primary_karakas TEXT[] NOT NULL, -- ARRAY['sun', 'saturn', 'jupiter']
    governing_houses INT[] NOT NULL -- ARRAY[10, 6, 2]
);

-- 3. Curated Tamil Navagraha Temples
CREATE TABLE public.navagraha_temples (
    id VARCHAR(30) PRIMARY KEY, -- 'suryanar_kovil', 'thingalur', etc.
    graha VARCHAR(20) NOT NULL,
    temple_name_en TEXT NOT NULL,
    temple_name_ta TEXT NOT NULL,
    presiding_deity_en TEXT NOT NULL,
    presiding_deity_ta TEXT NOT NULL,
    location_place TEXT NOT NULL,
    district TEXT NOT NULL DEFAULT 'Thanjavur/Mayiladuthurai',
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    speciality_en TEXT NOT NULL,
    speciality_ta TEXT NOT NULL,
    visiting_day VARCHAR(20) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_remedies_graha ON public.remedies_catalog(graha);
CREATE INDEX idx_remedies_type ON public.remedies_catalog(remedy_type);
CREATE INDEX idx_navagraha_graha ON public.navagraha_temples(graha);
```

### 7.2 Backend Python Service Architecture

Create `backend/app/services/remedy_engine/`:

1. **`diagnostics.py`:**
   - Evaluates natal planet strength using XALEN ephemeris data.
   - Calculates debilitation and verifies classical **Neecha Bhanga** rules (Lord in Kendra from Lagna/Moon, exaltation lord in Kendra, etc.).
   - Computes combust planets (*Astangata*) within standard classical combustion orbs from Sun (Mars 17°, Mercury 14°, Jupiter 11°, Venus 10°, Saturn 15°).
   - Evaluates dusthana lordships (6th, 8th, 12th) based on Lagna.
   - Detects active Mahadasha and Antardasha lords from `dasa_service.py`.

2. **`protections.py` (Crucial Vedic Safeguard):**
   - Implements **Yogakaraka Protection Logic**:
     ```python
     YOGAKARAKAS = {
         "Taurus": "saturn",       # 9th & 10th lord
         "Cancer": "mars",         # 5th & 10th lord
         "Leo": "mars",            # 4th & 9th lord
         "Libra": "saturn",        # 4th & 5th lord
         "Capricorn": "venus",     # 5th & 10th lord
         "Aquarius": "venus",      # 4th & 9th lord
     }
     ```
   - **Rule:** If a planet is a Yogakaraka or functional benefic, **never prescribe Daan (donation)**. Instead, prescribe stotras, temple worship, or Sattvic strengthening remedies.

3. **`scoring.py`:**
   - Deterministic diagnostic score:
     - House Lord of affected life domain: `+20`
     - Natural Karaka of problem: `+15`
     - Running Mahadasha: `+25`
     - Running Antardasha: `+15`
     - Chart Affliction (Dusthana, Debilitated without Neecha Bhanga, Combust): `+15`
     - Severe affliction (multiple malefic aspects): `+10`
   - Selects the top 1 or 2 planets genuinely responsible for the concern in *this native's specific chart*.

4. **`FastAPI Router` (`app/routers/remedies.py`):**
   - `POST /api/v1/remedies/diagnose`: Accepts birth parameters and selected problem keys, runs XALEN horoscope, diagnoses afflictions, and returns tailored remedies with full classical rationale.

---

## 8. Missing Tamil Content & Verification Requirements

Graha Remedy is substantially deficient in South Indian and Tamil astrological traditions:

### 8.1 The 9 Kaveri Delta Navagraha Temples (Completely Missing)

In Tamil Nadu astrology, remedies for planetary afflictions are fundamentally linked to the **Navagraha Sthalams** in the Kaveri Delta region (Thanjavur, Kumbakonam, and Mayiladuthurai districts). None of these are present in `graha-remedy`:

| Graha (Planet) | Tamil Name | Classical Navagraha Sthalam | Presiding Deity | District / Location | Key Remedial Worship |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sun** | சூரியன் (Sooriyan) | **Suryanar Kovil** (சூரியனார் கோவில்) | Sri Suryanarayana Swamy | Aduthurai, Thanjavur | Sun worship with wheat, red lotus, Sunday parikrama |
| **Moon** | சந்திரன் (Chandran) | **Thingalur** (திங்களூர்) | Sri Kailasanathar | Thingalur, Thanjavur | White flower puja, raw rice/milk offering on Mondays |
| **Mars** | செவ்வாய் / அங்காரகன் | **Vaitheeswaran Kovil** (வைத்தீஸ்வரன் கோவில்) | Sri Vaidyanatha Swamy / Sevvai | Mayiladuthurai | Angaraka parikrama, red lentil daan, curing ailments |
| **Mercury** | புதன் (Budhan) | **Thiruvenkadu** (திருவெண்காடு) | Sri Swetharanyeswarar / Budhan | Sirkazhi, Mayiladuthurai | Green gram offering, Saraswati/Vidya blessings |
| **Jupiter** | குரு / பிரகஸ்பதி | **Alangudi** (ஆலங்குடி) | Sri Apatsahayeswarar / Dakshinamurthy | Valangaiman, Tiruvarur | Yellow chana dal mala, Thursday ghee deepam |
| **Venus** | சுக்கிரன் (Sukran) | **Kanjanur** (கஞ்சனூர்) | Sri Agneeswarar / Sukran | Kumbakonam, Thanjavur | White cloth, mochai payaru offering on Fridays |
| **Saturn** | சனி / சனீஸ்வரன் | **Thirunallar** (திருநள்ளாறு) | Sri Dharbaranyeswarar / Saneeswara | Karaikal, Puducherry/TN | Nala Theertham holy dip, sesame oil deepam on Saturdays |
| **Rahu** | ராகு (Rahu) | **Thirunageswaram** (திருநாகேஸ்வரம்) | Sri Naganathaswamy / Rahu | Kumbakonam, Thanjavur | Pal Abhishekam during Rahu Kalam (milk turns blue) |
| **Ketu** | கேது (Ketu) | **Keezhperumpallam** (கீழ்ப்பெரும்பள்ளம்) | Sri Naganathaswamy / Ketu | Poompuhar, Mayiladuthurai | Kollu (horsegram) offering, Moksha blessings |

### 8.2 Missing Tamil Linguistic Assets
1. **Tamil Mantra Transliteration:**  
   Vedic mantras in `graha-remedy` exist only in English Romanization (often misspelled). Tamil users require authentic Tamil script with accurate phonetic markers (e.g., `ஓம் சூர்யாய நமஹ`, `ஓம் நமச்சிவாய`, `காயத்ரி மந்திரம்`).
2. **Tamil Remedy Descriptions:**  
   Fasting (விரதம் - Viratham), Charity (தானம் - Daanam), and Worship (பூஜை விதிமுறைகள் - Puja Vidhi) must be presented in fluent, respectful literary Tamil.
3. **South Indian Panchang Corrections:**  
   Fix the Saturday night error in `Gowri Panchangam` (`frontend/src/lib/gowri.ts`), restoring `Rogam` (ரோகம்) to its proper sequence.

---

## 9. Test Plan & Regression Safeguards

To ensure that integrating the remedy module does not affect any existing systems, the following regression and validation safeguards are mandated:

### 9.1 Mathematical Engine Safeguards (Zero-Deviation Rule)
- Run the full existing test suite for the native XALEN ephemeris and KP engine:
  ```powershell
  .\.venv\Scripts\pytest backend/tests/ -v
  ```
- Compare outputs before and after to ensure **0.000000° variation** in planetary longitudes, bhava cusps, and Dasa dates.
- Confirm zero imports of `@swisseph/node` or Swiss Ephemeris C binaries.

### 9.2 Remedy Engine Unit Tests (`backend/tests/test_remedy_engine.py`)
1. **Yogakaraka Protection Test:**  
   Verify that for Taurus Lagna, Saturn (Yogakaraka) is never assigned a Daan/pacification remedy, even if `career_delay` is passed as a problem.
2. **Neecha Bhanga Cancellation Test:**  
   Verify that a debilitated planet (e.g., Sun in Libra) with Venus in a Kendra from Lagna is recognized as having Neecha Bhanga, suppressing severe negative affliction flags.
3. **Combustion Verification Test:**  
   Verify that a planet within combustion distance of the Sun is correctly tagged as *Combust (Astangata)* and assigned appropriate Kavach or prayer remedies.
4. **Active Dasha Weighting Test:**  
   Verify that when two planets are equally afflicted, the running Mahadasha/Antardasha lord receives priority scoring (+25/+15 weight).
5. **Mantra Text Fidelity Test:**  
   Verify that all Devanagari and Tamil mantra strings match authentic Vedic text with 100% character precision (confirming absence of corrupted strings like `Bha-go-va-sy`).

### 9.3 Supabase & Database Safeguards
- Verify that existing tables (`user_profiles`, `analyses`, `birth_details`, etc.) and Row Level Security (RLS) policies are untouched.
- All new remedy tables must reside in independent DDL migrations with full rollback scripts.

---

## 10. Final Verdict & Actionable Roadmap

### Final Verdict: CONDITIONAL GO

```
┌────────────────────────────────────────────────────────────────────────┐
│                              AUDIT VERDICT                             │
│                                                                        │
│   [❌] AGPL-3.0 Repository Source Code              --> REJECT         │
│   [❌] @swisseph/node Astronomical Library         --> REJECT         │
│   [❌] Existing Backend Dosha Service (Flawed)     --> REJECT         │
│   [❌] Static Temples Dataset (Missing Navagraha)  --> REJECT         │
│   [❌] AI-Generated SEO Content & OpenRouter       --> REJECT         │
│                                                                        │
│   [✅] 39-Problem Life Taxonomy                    --> ADAPT          │
│   [✅] Diagnostic Scoring & Weighting Formula      --> ADAPT          │
│   [✅] Planetary Correspondences (Public Domain)   --> ADAPT          │
│   [✅] Clean-Room Python Backend on XALEN Engine   --> IMPLEMENT      │
│   [✅] Curated Tamil Navagraha Temples & Mantras   --> IMPLEMENT      │
│                                                                        │
│                  OVERALL VERDICT: CONDITIONAL GO                       │
│    (Proceed ONLY with Clean-Room Re-engineering in Python/FastAPI)     │
└────────────────────────────────────────────────────────────────────────┘
```

### Actionable Implementation Roadmap (Phase 2 — Pending User Approval)

1. **Step 1: Clean-Room Data Preparation (No Code Copying):**
   - Curate a clean, verified JSON dataset of authentic classical mantras, fasting rules, and daan recommendations based on BPHS and Mantra Mahodadhi.
   - Compile the 9 Kaveri Delta Tamil Navagraha Temples with coordinates, sthala purana, and Tamil script.
   - Formulate the 39-problem taxonomy with primary/secondary karakas and governing bhavas.

2. **Step 2: Supabase Migration:**
   - Create migrations for `remedies_catalog`, `remedies_problem_taxonomy`, and `navagraha_temples`.
   - Seed the verified data.

3. **Step 3: FastAPI Backend Implementation:**
   - Create `backend/app/services/remedy_engine/` containing:
     - `diagnostics.py` (chart afflictions, Neecha Bhanga, combustion using native XALEN)
     - `protections.py` (Yogakaraka and functional benefic protections)
     - `scoring.py` (diagnostic ranking with dasha weighting)
   - Add router `app/routers/remedies.py` exposing `POST /api/v1/remedies/diagnose`.

4. **Step 4: Next.js Frontend Integration:**
   - Create a clean, elegant Remedy Finder interface in `frontend/src/` with bilingual (English/Tamil) tabs.
   - Display recommended remedies categorized by Mantra, Vrat, Daan, and Temple, clearly presenting the astrological reason why each is prescribed.

---
*Audit completed under strict read-only safeguards. No production files, schemas, or calculation engines have been modified. Implementation awaits user approval.*
