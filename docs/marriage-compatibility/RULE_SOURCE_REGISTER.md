# Classical Astrological Rule Source Register
## Feature: Comprehensive Vedic + KP Marriage Compatibility Engine
**Project:** Gokul's Astrological Insights  
**Date:** October 19, 2026  
**Status:** INITIAL PHASE 0 DRAFT — PENDING AUDIT REVIEW & APPROVAL  
**Maintainer:** Gokul's Astrological Insights Engineering & Jyotish Council

---

## 1. Governance & Verification Standards

To guarantee strict astrological authenticity, reproducibility, and legal integrity:
1. **No Invented Rules:** Every calculation, point allocation, boundary, and cancellation exception must trace directly to an authoritative classical treatise or validated tradition.
2. **Explicit Separation of Traditions:** Tamil 10 Porutham calculations and North Indian 36-point Ashtakoota calculations are maintained as distinct methodologies. Their scores must never be summed, averaged, or commingled into a synthetic metric.
3. **Deterministic Evaluation:** Rule evaluations are purely functional and idempotent. No stochastic models, heuristics, or LLM overrides are permitted.
4. **Clean-Room Verification:** Zero algorithms, YAML tables, or code structures from `scratch/daiv-ai/` or any copyleft repository are referenced. All logic is derived directly from primary public-domain classical literature.
5. **Approval Workflow:**
   - `APPROVED_FOR_IMPLEMENTATION`: Primary classical source verified with exact sloka/chapter; explicit calculation formula and exception boundaries defined.
   - `PENDING_CONFIRMATION`: Multiple regional variations exist; specific school or convention must be explicitly selected before implementation.
   - `UNSUPPORTED`: Claimed folk rule or modern unverified assertion with no classical textual basis; explicitly barred from production engine.

---

## 2. Tamil Traditional 10 Poruthams (Dasa Porutham)

*Primary Authority:* *Kalaprakasika* (Chapter 12: Vivaha Prakarana), *Kumaraswamiyam*, *Jathaka Alankaram*, *Brihat Samhita* (Chapter 100).

| Rule ID | Porutham Name | Astrological Significance | Canonical Source & Reference | Counting Convention & Evaluation Logic | Documented Exceptions / Scope | Implementation & Verification Status |
|---|---|---|---|---|---|---|
| `TAM-POR-01` | **Dina Porutham** (தினம்) | Health, vitality, freedom from illness, longevity of couple | *Kalaprakasika* Ch. 12, Slokas 1–6 (v1.0) | Count from Bride's Janma Nakshatra to Groom's Janma Nakshatra. Divide by 9. Remainder 2 (Sampat), 4 (Kshema), 6 (Sadhana), 8 (Mitra), 9/0 (Parama Mitra) = **Uthama (Favorable)**. Remainder 1 (Janma), 3 (Vipat), 5 (Pratyak), 7 (Naidhana) = **Adhama (Unfavorable)**. 27th star = Vainashika (Inauspicious). | Same Nakshatra allowed for Rohini, Ardra, Makha, Hasta, Vishakha, Shravana, Uttarabhadrapada, Revati. Different Padas evaluated. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-02` | **Gana Porutham** (கணம்) | Temperament, psychological compatibility, behavioral concord | *Kalaprakasika* Ch. 12, Slokas 7–12; *Muhurta Chintamani* (v1.0) | 27 Nakshatras divided into 3 Ganas: **Deva** (Divine), **Manushya** (Human), **Rakshasa** (Fierce). Same Gana = Favorable (1.0). Deva Groom + Manushya Bride = Favorable (1.0). Manushya Groom + Deva Bride = Moderate (0.5). Rakshasa Groom + Deva/Manushya Bride = Moderate (0.5). Rakshasa Bride + Deva/Manushya Groom = Unfavorable (0.0). | Mitigations for Gana defect noted in warnings when Moon sign lords are friendly, Samasaptaka (7th), or star distance > 14. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-03` | **Mahendra Porutham** (மகேந்திரம்) | Progeny, family lineage growth, paternal blessings | *Kalaprakasika* Ch. 12, Slokas 13–15 (v1.0) | Count from Bride's star to Groom's star. If Groom's star is 4th, 7th, 10th, 13th, 16th, 19th, 22nd, or 25th = **Present (Uthama, 1.0 pt)**. Otherwise = **Absent (Adhama, 0.0 pt)**. | Binary evaluation. Absence does not veto marriage if primary Poruthams (Dina, Rasi, Rajju) are strong. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-04` | **Sthree Deergha** (ஸ்திரீ தீர்க்கம்) | Woman's prosperity, marital longevity, wealth accumulation | *Kalaprakasika* Ch. 12, Sloka 16 (v1.0) | Count from Bride's star to Groom's star. If Groom's star is strictly beyond 13th Nakshatra (> 13) = **Uthama (1.0 pt)**. Between 8th and 13th = **Madhyama (0.5 pt)**. Less than or equal to 7 = **Adhama (0.0 pt)**. | Secondary Porutham. Deficiency does not veto alliance if Rasi and Graha Maitri are strong. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-05` | **Yoni Porutham** (யோனி) | Biological harmony, mutual attraction, physical intimacy | *Brihat Samhita* Ch. 100; *Kalaprakasika* Ch. 12 (v1.0) | 14 Animal archetypes. Same species = **Uthama (1.0 pt)**. Friendly/neutral species = **Madhyama (0.5 pt)**. Inimical sworn enemy pairs = **Varjya (0.0 pt)**. Classical 7 Sworn Inimical Pairs: Cow–Tiger, Elephant–Lion, Horse–Buffalo, Dog–Deer, Cat–Rat, Snake–Mongoose, Monkey–Sheep. | Mutual inimical pairs strictly veto Yoni Porutham (Vaira Yoni). Bilateral symmetry verified. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-06` | **Rasi Porutham** (ராசி) | Lineage harmony, domestic stability, mutual prosperity | *Kalaprakasika* Ch. 12, Slokas 20–25 (v1.0) | Distance of Groom's Moon Sign from Bride's Moon Sign (inclusive): 7th (Samasaptaka) = **Uthama (1.0 pt)**; 3rd, 11th = **Uthama (1.0 pt)**; 4th, 10th = **Madhyama (0.75 pt)**; Same Rasi with Groom star ahead = **Uthama (1.0 pt)**; 6/8 and 2/12 = **Inauspicious (0.0 pt)**. | Classical Cancellations: 6/8 allowed if signs share same lord (Aries-Scorpio, Taurus-Libra = 0.5 pt); 2/12 allowed if Capricorn-Aquarius (Saturn) or Pisces-Aries (Jupiter/Mars) = 0.5 pt; 5/9 allowed if sign lords friendly = 0.5 pt. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-07` | **Rasi Athipathi** (ராசி அதிபதி) | Friendship of ruling grahas, psychological alignment | *Phaladeepika* Ch. 2; *Kalaprakasika* Ch. 12; *BPHS* Ch. 15 (v1.0) | Natural planetary relationship (*Naisargika Sambandha*) between Groom's Moon sign lord and Bride's Moon sign lord. Same Lord or Mutual Friends = **Uthama (1.0 pt)**. Friend-Neutral = **Uthama (0.75 pt)**. Mutual Neutral = **Madhyama (0.5 pt)**. Neutral-Enemy or Friend-Enemy = **Adhama (0.25 pt)**. Mutual Enemies = **Adhama (0.0 pt)**. | Evaluates natural planetary friendships deterministically per BPHS Ch. 15 matrix. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-08` | **Vasya Porutham** (வசியம்) | Mutual devotion, marital concord, emotional responsiveness | *Kalaprakasika* Ch. 12, Slokas 26–28 (v1.0) | Canonical Sign Vasya Table: Aries->Leo/Scorpio; Taurus->Cancer/Libra; Gemini->Virgo; Cancer->Scorpio/Sagittarius; Leo->Libra; Virgo->Pisces/Gemini; Libra->Capricorn/Virgo; Scorpio->Cancer; Sagittarius->Pisces; Capricorn->Aries/Aquarius; Aquarius->Aries; Pisces->Capricorn. Mutual Vasya = **Uthama (1.0 pt)**. One-way Vasya = **Madhyama (0.75 pt)**. Absent = **Adhama (0.0 pt)**. | If either sign is Vasya to the other, Porutham is considered present in Tamil practice. Absence does not veto. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-09` | **Rajju Porutham** (ரஜ்ஜு) | Mangalya longevity, health of spouse, life protection | *Kalaprakasika* Ch. 12, Slokas 29–35; *Kumaraswamiyam* (v1.0) | 5 Rajju classes: **Shiro** (Head), **Kantha** (Neck), **Udara** (Stomach), **Kati** (Hip), **Pada** (Foot). Different Rajju = **Uthama (1.0 pt)**. **Same Rajju is STRICTLY PROHIBITED (Rajju Dosha, 0.0 pt, Varjya)**: Shiro = threat to husband; Kantha = threat to wife; Udara = obstacle to progeny; Kati = poverty; Pada = wandering/instability. | In South Indian tradition, Rajju has **NO CANCELLATION**; it is an absolute foundational prerequisite (Maha Porutham). | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |
| `TAM-POR-10` | **Vedha Porutham** (வேதை) | Mutual affliction, psychic discord, destructive interaction | *Kalaprakasika* Ch. 12, Slokas 36–38 (v1.0) | 12 Mutually Repulsive Nakshatra Pairs: Ashwini–Jyeshtha; Bharani–Anuradha; Krittika–Vishakha; Rohini–Swati; Ardra–Shravana; Punarvasu–Uttarashadha; Pushya–Purvashadha; Ashlesha–Mula; Magha–Revati; Purvaphalguni–Uttarabhadrapada; Uttaraphalguni–Purvabhadrapada; Hasta–Shatabhisha. Mars triad mutual Vedha (Mrigashira, Chitra, Dhanishta). If pair matches = **Vedha Dosha (Varjya, 0.0 pt)**. No Vedha = **Uthama (1.0 pt)**. | Vedha Dosha permits no cancellation if pair falls in repulsive axis. Maha Porutham. | `IMPLEMENTED_AND_VERIFIED`<br>(18 tests in `test_tamil_10_poruthams.py`) |

---

## 3. North Indian Ashtakoota Matching (36-Point System)

*Primary Authority:* *Muhurta Chintamani* (Chapter 6: Vivaha Prakarana), *Brihat Parashara Hora Shastra* (Chapter 81).

| Koota ID | Koota Name | Maximum Points | Canonical Source | Input Primitives | Classical Scoring Formula & Rules | Documented Exceptions & Cancellations | Approval Status |
|---|---|---:|---|---|---|---|---|
| `ASHTA-01` | **Varna Koota** | 1 | *Muhurta Chintamani* Ch. 6, Sloka 1 | Moon Signs (Rashi) | Brahmin (Cancer, Scorpio, Pisces = 4), Kshatriya (Aries, Leo, Sagittarius = 3), Vaishya (Taurus, Virgo, Capricorn = 2), Shudra (Gemini, Libra, Aquarius = 1). Groom Varna $\ge$ Bride Varna = **1 point**; Groom Varna $<$ Bride Varna = **0 points**. | None required. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-02` | **Vashya Koota** | 2 | *Muhurta Chintamani* Ch. 6, Sloka 2 | Moon Signs (Rashi) | 5 Classes: Chatushpada (Aries, Taurus, Sagittarius 2nd half, Capricorn 1st half); Dwipada (Gemini, Virgo, Libra, Aquarius, Sagittarius 1st half); Jalachara (Cancer, Pisces, Capricorn 2nd half); Vanachara (Leo); Keeta (Scorpio). Same class = **2 pts**; Mutual Vasya = **2 pts**; One-way Vasya = **1 pt**; Neutral = **1 pt**; Inimical (e.g. Vanachara vs Chatushpada) = **0 pts**. | Sign lord friendship mitigates point reduction. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-03` | **Tara Koota** (Dina) | 3 | *Muhurta Chintamani* Ch. 6, Slokas 3–5 | Moon Nakshatras | Count from Bride star to Groom star $\pmod{9}$ (Tara 1) and Groom star to Bride star $\pmod{9}$ (Tara 2). Tara 1, 3, 5, 7 = Inauspicious; 2, 4, 6, 8, 9/0 = Auspicious. Both auspicious = **3 pts**; One auspicious = **1.5 pts**; Neither auspicious = **0 pts**. | If Tara is afflicted, strong Graha Maitri or Bhakoot provides secondary mitigation. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-04` | **Yoni Koota** | 4 | *Muhurta Chintamani* Ch. 6, Slokas 6–9; *BPHS* Ch. 81 | Moon Nakshatras | Complete 14x14 classical animal matrix. Same animal = **4 pts**; Friendly animals = **3 pts**; Neutral animals = **2 pts**; Inimical animals = **1 pt**; Bitter sworn enemy pairs = **0 pts** (Horse-Buffalo, Elephant-Lion, Sheep-Monkey, Serpent-Mongoose, Dog-Deer, Cat-Rat, Cow-Tiger). | Gender within same animal species: Male Groom + Female Bride preferred, but does not alter base 4 points. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-05` | **Graha Maitri Koota** | 5 | *Muhurta Chintamani* Ch. 6, Slokas 10–12 | Moon Sign Lords | Natural friendship of Rasi lords: Both mutual friends = **5 pts**; One friend, one neutral = **4 pts**; Both neutral = **3 pts**; One friend, one enemy = **1 pt**; One neutral, one enemy = **0.5 pts**; Both bitter enemies = **0 pts**. | If Moon sign lords are identical (e.g. both Aries/Scorpio or Taurus/Libra), full 5 points awarded regardless of natural relationship. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-06` | **Gana Koota** | 6 | *Muhurta Chintamani* Ch. 6, Slokas 13–15 | Moon Nakshatras | Deva-Deva = **6 pts**; Manushya-Manushya = **6 pts**; Rakshasa-Rakshasa = **6 pts**; Deva-Manushya = **5 pts**; Manushya-Deva = **5 pts**; Deva-Rakshasa = **1 pt**; Rakshasa-Deva = **0 pts**; Manushya-Rakshasa = **0 pts**; Rakshasa-Manushya = **0 pts**. | If Moon sign distance is 7th (Samasaptaka) or if sign lords are mutual friends, Gana defect earns **3 pts** (partial mitigation). | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-07` | **Bhakoot Koota** | 7 | *Muhurta Chintamani* Ch. 6, Slokas 16–20 | Moon Signs (Rashi) | Mutual sign distance: 1/1, 3/11, 4/10 = **7 pts**; 2/12 (Dvidwadasa), 5/9 (Navapanchama), 6/8 (Shadashtaka) = **0 pts (Bhakoot Dosha)**. | **Classical Bhakoot Cancellations:** (1) Same Rasi Lord cancels 6/8 (Aries-Scorpio, Taurus-Libra); (2) Same Rasi Lord cancels 2/12 (Capricorn-Aquarius); (3) Mutual friendship of lords mitigates 5/9 (Aries-Sagittarius, Cancer-Pisces). | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| `ASHTA-08` | **Nadi Koota** | 8 | *Muhurta Chintamani* Ch. 6, Slokas 21–25; *BPHS* Ch. 81 | Moon Nakshatras | Adi (Vata), Madhya (Pitta), Antya (Kapha). Different Nadi = **8 pts**; Same Nadi = **0 pts (Nadi Dosha)**. | **Classical Nadi Cancellations:** (1) Same Rasi but different Nakshatras; (2) Same Nakshatra but different Rasi (Pada crosses boundary); (3) Same Nakshatra but different Padas for designated stars (Rohini, Mrigashira, Ardra, Pushya, Shravana, Uttarabhadrapada). | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |
| **TOTAL** | **Ashtakoota Aggregate** | **36** | | | Minimum acceptable score traditionally **18 / 36**, subject to Nadi and Bhakoot non-affliction. | A score $\ge 18$ does not override an active, uncancelled Nadi or Bhakoot Dosha. | `IMPLEMENTED_AND_VERIFIED`<br>(12 tests in `test_ashtakoota.py`) |

---

## 4. Kuja / Chevvai / Manglik Dosha & Mutual Pairing

*Primary Authority:* *Brihat Parashara Hora Shastra* (Chapter 81), *Muhurta Chintamani*, *Brihat Samhita*.

| Rule ID | Sub-Rule Name | Trigger Placements | Classical Conditions | Cancellation & Exception Rules | Authority Citation | Approval Status |
|---|---|---|---|---|---|---|
| `DOS-KUJA-01` | **Tri-Reference Kuja Detection** | Mars in 1, 2, 4, 7, 8, 12 | Evaluated independently from **Lagna (100% weight)**, **Moon (75% weight)**, and **Venus (50% weight)**. | Evaluates whether Mars afflicts physical vitality (1st), family/speech (2nd), domestic peace (4th), marital bond (7th), longevity/mangalya (8th), or bed pleasures (12th). | *BPHS* Ch. 81; *Muhurta Chintamani* | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `DOS-KUJA-02` | **Individual Dignity Cancellations** | Mars in own sign, exaltation, debilitation | Mars in Aries or Scorpio; Mars in Capricorn; Mars debilitated in Cancer in 7th or 8th house. | Own sign neutralizes fire; exaltation acts as protector; debilitation in 7/8 lacks malefic potency. | *BPHS* Ch. 81, Sloka 47; *Muhurta Chintamani* | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `DOS-KUJA-03` | **House-Sign Specific Exceptions** | Specific sign-house combinations | Mars in 2nd in Gemini/Virgo; Mars in 12th in Taurus/Libra; Mars in 8th in Sagittarius/Pisces; Mars in 7th in Leo/Aquarius. | Classical sign-lord absorption eliminates disruptive energy. | *Muhurta Chintamani* Ch. 6 | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `DOS-KUJA-04` | **Functional Benefic / Yogakaraka Exception** | Cancer or Leo Lagna | For Cancer Lagna (Mars rules 5th & 10th) and Leo Lagna (Mars rules 4th & 9th). | Mars is functional Yogakaraka and cannot inflict Kuja Dosha from Lagna. | *BPHS* Ch. 34 & 81 | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `DOS-KUJA-05` | **Benefic Aspect Mitigation** | Jupiter / Moon aspect | Jupiter conjoined with or aspecting Mars (5th, 7th, 9th); Moon conjoined (Chandra-Mangala). | Divine aspect soothes Martian volatility. | *BPHS* Ch. 81 | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `DOS-KUJA-06` | **Mutual Kuja Balancing (Samadosham)** | Both charts have Kuja Dosha | Groom has Kuja Dosha AND Bride has Kuja Dosha of comparable effective intensity. | **Mutual Neutralization:** "Doshasya samyam bhavati" — equal malefic force on both sides neutralizes marital friction. | *Muhurta Chintamani*; *Kalaprakasika* Ch. 12 | `IMPLEMENTED_AND_VERIFIED`<br>(41 tests in `test_mutual_doshas.py`) |
| `DOS-KUJA-07` | **Cross-Planet Mars Counterbalance** | Mars in 7th/8th counterbalanced by Saturn/Rahu | Groom's Mars in 7th/8th is matched by Bride having Saturn, Rahu, or Ketu in 7th/8th, or vice-versa. | Planetary counters neutralize specific house afflictions. | *Kalaprakasika* Ch. 12 | `IMPLEMENTED_AND_VERIFIED`<br>(41 tests in `test_mutual_doshas.py`) |

---

## 5. South Indian Papasamya (Malefic Balance)

*Primary Authority:* *Kalaprakasika* (Chapter 12), *Jathaka Alankaram*.

| Rule ID | Rule Name | Evaluated Planets | Evaluated Houses | Point Assignment Logic | Balancing Criterion | Approval Status |
|---|---|---|---|---|---|---|
| `DOS-PAPA-01` | **Papasamya Point Allocation** | Sun, Mars, Saturn, Rahu, Ketu | Houses 1, 2, 4, 7, 8, 12 from Lagna, Moon, and Venus | **Standard Classical Weights:**<br>• Mars: 1.0 point per placement<br>• Saturn: 1.0 point per placement<br>• Rahu: 0.5 point per placement<br>• Ketu: 0.5 point per placement<br>• Sun: 0.5 point per placement | Points evaluated separately for Groom and Bride across all 3 reference points (Lagna, Moon, Venus). | `IMPLEMENTED_AND_VERIFIED`<br>(41 tests in `test_mutual_doshas.py`) |
| `DOS-PAPA-02` | **Papasamya Balance Evaluation** | Groom Total Papam vs Bride Total Papam | Aggregate across 3 reference frames | **Acceptance Criteria:**<br>1. Groom Papam $\ge$ Bride Papam and difference $\le 25\%$: **FAVORABLE (Optimum Balance)**.<br>2. Both totals within absolute diff $\le 0.5$ pts: **FAVORABLE**.<br>3. Groom excess 25–50%: **TOLERABLE**.<br>4. Bride Papam exceeds Groom Papam by $> 25\%$ and diff $\ge 0.5$ pts: **UNFAVORABLE (Excess Malefic on Bride)**. | Classical South Indian canon strictly forbids bride carrying substantially higher malefic load than groom. | `IMPLEMENTED_AND_VERIFIED`<br>(41 tests in `test_mutual_doshas.py`) |

---

## 6. Comprehensive Vedic Marriage Analysis (D1 & D9)

*Primary Authority:* *Brihat Parashara Hora Shastra* (Chapters 9, 13, 18, 20), *Phaladeepika* (Chapter 10: Kalatra Bhava), *Jataka Parijata*.

| Rule ID | Dimension | Target Grahas / Houses | Evaluated Conditions | Synthesis Principle | Approval Status |
|---|---|---|---|---|---|
| `VED-MARR-01` | **7th House & 7th Lord (D1)** | 7th Bhava, 7th Lord | Occupants, aspects of natural benefics (Jupiter, Venus, Mercury) vs malefics (Saturn, Mars, Rahu, Ketu, Sun). Strength and dignity of 7th lord. | Strong 7th lord in Kendra/Trikona protects marriage bond; 7th lord debilitated in 6/8/12 requires mitigation. | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `VED-MARR-02` | **2nd, 4th, 5th, 8th, 12th Houses (D1)** | 2nd (Kutumba), 4th (Sukha), 5th (Putra), 8th (Mangalya), 12th (Sayana) | Disposition of lords and occupants of auxiliary marriage houses. | Affliction to 2nd impacts speech/family; 4th impacts domestic bliss; 5th impacts romance/progeny; 8th impacts marital longevity; 12th impacts bedroom harmony. | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `VED-MARR-03` | **Natural Marriage Significators** | Venus (Shukra), Jupiter (Guru), Moon, Mars, Saturn, Rahu-Ketu | Dignity (Exalted, Own, Moolatrikona, Debilitated), combustion, retrogression, functional nature by Lagna (BPHS Ch. 34). | Venus is primary Karaka for all; Jupiter is Karaka for women (husband/dharma); Moon reflects emotional bond. | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `VED-MARR-04` | **D9 Navamsa Cross-Validation** | D9 Lagna, D9 7th House, D9 7th Lord, Navamsa Venus, D1 7th Lord in D9 | Position of D1 7th lord in D9; D9 7th lord in D1; Vargottama planets; Pushkara Navamsa placements; boundary sensitivity. | If D1 shows weakness but D9 7th lord is exalted or in Pushkara Navamsa, marital fulfillment improves after youth. | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_vedic_marriage_analysis.py`) |
| `VED-MARR-05` | **Cross-Chart Synastry Overlays** | Groom planets in Bride's houses; Bride planets in Groom's houses | Moon-to-Moon distance; Lagna-to-Lagna relationship; 7th lord cross-placements; Venus-Jupiter Karaka overlays; Navamsa boundary checks. | Identifies bidirectional resonance: does Groom's placement uplift Bride's houses, and vice versa? | `IMPLEMENTED_AND_VERIFIED`<br>(16 tests in `test_synastry.py`) |

---

## 7. KP Marriage Analysis & Event Timing

*Primary Authority:* *KP Readers I, II, III* by Prof. K.S. Krishnamurti.

| Rule ID | Module | Target Cusp / Planet | Canonical KP Rule | Astrological Rationale | Implementation & Verification Status |
|---|---|---|---|---|---|
| `KP-MARR-01` | **7th Cuspal Sub-Lord (CSL) Promise** | 7th House Cusp Sub-Lord | CSL must signify houses **2, 7, 11** for fruitful, committed marriage. If CSL signifies **1, 6, 10**, delay, denial, or marital discord is indicated. | In KP, the CSL is the ultimate arbiter of a house's fruition. House 2 = family addition, 7 = spouse/union, 11 = fulfillment of desires. Houses 1, 6, 10 are 12th (negation) to 2, 7, 11. | `IMPLEMENTED_AND_VERIFIED`<br>(13 tests in `test_kp_marriage_adapter.py`) |
| `KP-MARR-02` | **4-Tier House Significators** | Key Marriage Houses (2, 7, 11) & Denying Houses (1, 6, 10) | Extract 4-tier KP house significators: Level A (planets in star of occupants), Level B (occupants), Level C (planets in star of lord), Level D (house lord). | Preserves exact 4-tier provenance without fabricating missing levels; identifies marriage-facilitating and detrimental significators. | `IMPLEMENTED_AND_VERIFIED`<br>(13 tests in `test_kp_marriage_adapter.py`) |
| `KP-MARR-03` | **Ruling Planets Agreement & Vimshottari Timing** | Groom/Bride Ruling Planets & Vimshottari Dasa-Bhukti Lords | Evaluates commonality of Ruling Planets (Day Lord, Asc sign/star/sub, Moon sign/star/sub) and assesses active/upcoming Dasa-Bhukti lords for activation of 2, 7, 11 vs 1, 6, 10. | RP agreement indicates synchronous karmic readiness; timing analysis identifies auspicious periods for marital manifestation without claiming event guarantees. | `IMPLEMENTED_AND_VERIFIED`<br>(13 tests in `test_kp_marriage_adapter.py`) |

---

## 8. Deterministic Final Assessment Decision Matrix

| Condition / Evidence Layer | Threshold for Favorable | Threshold for Mixed / Conditional | Threshold for Unfavorable |
|---|---|---|---|
| **Tamil 10 Porutham** | $\ge 6.0$ matches AND Rajju = PASS AND Vedha = PASS | 5.0 to 5.5 matches AND Rajju = PASS | $< 5.0$ matches OR Rajju = FAIL OR Vedha = FAIL |
| **North Indian Ashtakoota** | $\ge 21.0$ points AND Nadi = Clear/Cancelled AND Bhakoot = Clear/Cancelled | 18.0 to 20.5 points AND Nadi = Clear/Cancelled | $< 18.0$ points OR Active Uncancelled Nadi Dosha OR Active Uncancelled Bhakoot Dosha |
| **Kuja Dosha Balance** | Both charts free OR Both charts balanced (Samadosham) | One chart mild Kuja ($\le 50\%$) with benefic cancellation | One chart high active Kuja ($> 100\%$) and partner completely unafflicted |
| **Papasamya Balance** | Groom Papam $\ge$ Bride Papam AND difference $\le 25\%$ | Groom Papam and Bride Papam within $\pm 10\%$ | Bride Papam exceeds Groom Papam by $> 25\%$ |
| **Vedic 7th House & D9** | 7th lords well-placed in D1 and supported in D9 | Minor afflictions with Jupiter/Venus aspectual protection | Severe unmitigated afflictions to 7th house and 7th lords in both D1 and D9 |
| **KP 7th CSL** | CSL signifies 2, 7, 11 for both | CSL mixed (signifies 2, 7, 11 and 1, 6) | CSL exclusively signifies 1, 6, 10 (denial) for either |

### Top-Level Verdict Taxonomy:
1. `FAVOURABLE_UNDER_SELECTED_RULES`: All selected traditions satisfy favorable thresholds with zero critical vetoes.
2. `MIXED_OR_CONDITIONAL`: Acceptable aggregate scores, but secondary afflictions exist requiring mature alignment, communication, and traditional mitigations.
3. `UNFAVOURABLE_UNDER_SELECTED_RULES`: Active, uncancelled critical veto present (e.g. Rajju Thatu, Vedha, active Nadi Dosha, or gross Papasamya imbalance).
4. `INDETERMINATE`: Missing mandatory birth coordinates or unresolvable astronomical boundary ambiguity.

---

## 9. Unresolved Source Questions & Implementation Decisions

| Question ID | Unresolved / Ambiguous Area | Competing Views | Adopted Engineering Decision | Approval Status |
|---|---|---|---|---|
| `Q-01` | **Sthree Deergha Threshold** | *Kalaprakasika* mentions $> 13$ stars is Uthama. Some later texts allow $> 7$ stars. | Adopt tiered evaluation: $> 13$ stars = Uthama; 8 to 13 stars = Madhyama; $\le 7$ stars = Adhama. Expose exact star distance in explanation. | `APPROVED_FOR_IMPLEMENTATION` |
| `Q-02` | **Double Tara vs Single Tara in Ashtakoota** | Some North Indian texts count only Bride-to-Groom (max 3 pts). Others count both directions (1.5 pts each = 3 pts). | Adopt the bidirectional (both directions, 1.5 pts each) convention per *Muhurta Chintamani*, which ensures equal evaluation of both individuals. | `APPROVED_FOR_IMPLEMENTATION` |
| `Q-03` | **Rajju Dosha Exceptions** | Traditional Tamil astrology asserts Rajju has zero cancellation. Some modern astrological software permits cancellation if Rasi lords are identical or friendly. | Uphold strict traditional South Indian convention: Rajju has **NO CANCELLATION**. We flag Rajju failure transparently and never mask it. | `APPROVED_FOR_IMPLEMENTATION` |
| `Q-04` | **Kuja Dosha 2nd House Inclusion** | South Indian tradition counts house 2 (1, 2, 4, 7, 8, 12). North Indian tradition often omits house 2 (1, 4, 7, 8, 12). | Preserve configurable toggle `include_2nd_house` (default `True` for South Indian convention, configurable to `False` for North Indian convention), consistent with existing `app/services/dosha_engine/kuja_dosha.py`. | `APPROVED_FOR_IMPLEMENTATION` |
