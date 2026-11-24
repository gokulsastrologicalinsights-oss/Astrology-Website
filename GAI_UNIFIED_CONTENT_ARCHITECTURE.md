# Gokul's Astrological Insights (GAI)
## Unified Content Architecture Specification (Phase 2 Deliverable)

**Date:** November 24, 2026  
**Status:** Approved & Formally Codified  
**Objective:** Transform GAI into an authoritative, customer-facing proprietary astrology platform by unifying fragmented author-wise and book-wise presentations into consistent, professional service categories while preserving internal algorithmic integrity.

---

### Architectural Core Principle: Strict Separation of Concerns

```mermaid
graph TD
    subgraph A[A. Internal Proprietary Knowledge Vault (Server-Side Only)]
        A1[Classical Sanskrit Treatises: BPHS, Saravali, Phaladeepika, Jataka Parijata]
        A2[Modern Empirical Astrological Research: K.N. Rao, Marc Boney, Dr. S. Krishna Kumar]
        A3[Ephemeris & Mathematical Mechanics: Rust xalen-ephemeris, Meeus, ELP2000, IAU 2006]
        A4[Internal Rule Identifiers: RULE-BPHS-*, RULE-SARA-*, RULE-BNS-*, RULE-DK-*]
        A5[Licensing & Legal Compliance: Apache 2.0 NOTICE, MIT LICENSE, BSD 3-Clause]
    end

    subgraph B[Transformation & Presentation Engine]
        B1[Prediction Synthesizer]
        B2[Unified Terminology Registry: unified-astrology-terminology.ts]
        B3[Server-Side Sanitizer: Strips raw slokas, authors, and internal file paths]
    end

    subgraph C[B. Customer-Facing Unified Platform (Customer UI / Reports)]
        C1[Major Life Milestones & Timing Analysis]
        C2[Career & Financial Trajectory Analysis]
        C3[Ayurvedic Constitution & Vitality Assessment]
        C4[Dual Planetary Transit Alignment (Jupiter & Saturn)]
        C5[Planetary Pathology & Physical Susceptibility]
        C6[Planetary Connectivity & Destiny Significations]
        C7[Comprehensive Matrimonial Compatibility & 36 Ashta Kuta]
        C8[Spouse Characteristics & Directional Analysis]
        C9[Six-Fold Planetary Strength Analysis (Shadbala)]
        C10[Traditional Remedial Guidance & Sanctification Directives]
    end

    A --> B
    B --> C
```

---

### Universal Terminology Mapping Matrix

The following standard terminology is enforced across all web pages, tabs, cards, modals, tooltips, and PDF reports:

| Legacy Disclosed Label | Standardized Customer-Facing Unified Title | Tamil Unified Title (தமிழ்) | Customer-Facing Subtitle / Guidance |
| :--- | :--- | :--- | :--- |
| **Marc Boney & K.N. Rao Major Life Milestones** | **Major Life Milestones & Planetary Timing Analysis** | **முக்கிய வாழ்க்கை மைல்கற்கள் & கால கணிப்பு** | Composite timing synthesis combining periodic dasha cycles, divisional charts, and major transit alignments. |
| **K.N. Rao Double Transit Axiom** | **Dual Planetary Transit Alignment (Jupiter & Saturn)** | **குரு-சனி இரட்டை பெயர்ச்சி கால கணிப்பு** | Evaluates the concurrent catalytic aspect of Jupiter and Saturn confirming the manifestation of major life events. |
| **K.N. Rao Research Canon** | **Career & Financial Trajectory Analysis** | **தொழில், அந்தஸ்து & நிதி வளர்ச்சி ஆய்வு** | Empirically validated classical models analyzing profession, executive status, business vs service, and wealth accumulation. |
| **Dr. S. Krishna Kumar Medical Treatise** | **Ayurvedic Constitution & Vitality Assessment** | **உடல்நலக் கூறுகள் & ஆயுர்வேத திரிகோண ஆய்வு** | Synthesized classical Ayurvedic Tridosha balance (Vata, Pitta, Kapha) and organ governance mapped to planetary longitudes. |
| **Heinrich Däath Classical Compendium** | **Planetary Pathology & Physical Susceptibility Analysis** | **கிரக பாதிப்புகள் & உடல்நல எச்சரிக்கைகள்** | Critical astronomical indications for anatomical susceptibility, periodic vulnerability, and preventative wellness safeguards. |
| **Brighu Naadi Treatise (R.G. Rao & Vels Univ)** | **Planetary Connectivity & Destiny Significations** | **கிரக இணைப்புகள் & விதி பலன்கள்** | Foundational planetary mutual aspects, directional trines, and sign connectivity revealing innate life purpose. |
| **Comprehensive Kundli Matching per BPHS** | **Comprehensive Matrimonial Compatibility & 36 Ashta Kuta** | **திருமணப் பொருத்தங்கள் & 36 அஷ்டகூட ஆய்வு** | Classical 36-point Kuta analysis, planetary friendship, Kuja Dosha evaluation, and mutual dasha synchronicity. |
| **Spouse Sivadasan Ravi KP Rule Card** | **Spouse Characteristics & Directional Analysis** | **வாழ்க்கைத் துணைவர் குணாதிசயங்கள் & திசை கணிப்பு** | Astrological indications of spouse's temperament, physical constitution, profession, and directional orientation. |
| **Shadbala Engine per BPHS Ch. 23** | **Six-Fold Planetary Strength Analysis (Shadbala)** | **அறுவகை கிரக பலம் (ஷட்பலம்)** | Classical quantitative planetary strength evaluation across positional, directional, temporal, motional, natural, and aspectual balas. |
| **Planetary House Placement (B.V. Raman & Saravali)** | **Planetary House Placement Predictions** | **பாவக கிரக நிலைகள் & பொதுப் பலன்கள்** | Detailed life effects of planetary occupants and rulers across the twelve houses of the birth horoscope. |
| **Sannu Ahmed Karma Diagnostic & Picatrix Rituals** | **Traditional Remedial Guidance & Sanctification Directives** | **பாரம்பரிய பரிகாரங்கள் & வழிபாட்டு நெறிமுறைகள்** | Sanctified Vedic mantras, temple pilgrimages, charity, and gemstone weight formulas harmonizing challenging planetary karmas. |
| **GK Transit Matching Card** | **Current Planetary Transit Alignments** | **தற்போதைய கிரகப் பெயர்ச்சி பலன்கள்** | Real-time astronomical ephemeris transit positions overlaying the native's natal chart and active dasha period. |
| **XALEN Ephemeris Engine / Swiss Ephemeris 2.10** | **Certified High-Precision Astronomical Calculations** | **அங்கீகரிக்கப்பட்ட துல்லிய வானியல் கணித முறை** | Deterministic, sub-arcsecond sidereal ephemeris algorithms computing planetary longitudes and unequal cuspal sub-divisions. |

---

### Internal Metadata Preservation Guidelines

1. **Rule Identifiers:**  
   Internal rule IDs (`RULE-BPHS-*`, `RULE-SARA-*`, `RULE-BNS-*`, `RULE-DK-*`) remain unchanged in Python registries, unit tests, and database tables. They serve as immutable internal keys.
2. **Treatise Bibliographic Records:**  
   Internal bibliographic metadata (`source_book`, `chapter`, `sloka`, `author`) remains stored in server-side registries. It is utilized by internal researchers and developers for canonical verification.
3. **Customer Presentation Layer:**  
   When generating client JSON responses or rendering frontend components, the presentation layer consumes the unified labels from `unified-astrology-terminology.ts` and renders clean predictions, evidence points, and remedial guidance without printing raw bibliographic source strings.
4. **Zero Fabrication:**  
   Astrological results are never falsely attributed to GAI or invented authors. They are presented as standard, authoritative astrological analysis (e.g., "Major Life Milestones Analysis", "Planetary Strength Analysis").

---

### Implementation Status

- Centralized mapping module created: `frontend/src/lib/unified-astrology-terminology.ts`.
- Priority 1 (Unified Content Architecture) is officially ratified.
- Proceeding to **Priority 2: Customer UI Sanitization**.
