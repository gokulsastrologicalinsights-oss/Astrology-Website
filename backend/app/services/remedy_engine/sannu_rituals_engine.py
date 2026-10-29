"""Sannu Ahmed Vedic Astrology Rituals & Remedies Knowledge Engine.

Comprehensive implementation of the sacred knowledge, rules, and remedial protocols
from "Vedic Astrology Rituals & Remedies: Powerful Rituals & Remedies for a Fulfilling Life"
by Sannu Ahmed (Jyotish Sadhak / Seeker of Light).

Covers:
1. Threefold Karma Architecture: Sanchita, Prarabdha (Acharaniya vs Vasaniya), Kriyamana (Agami).
2. The Soul-Body-Energy Circuit: Atma, Prana (72,000 nadis, pancha prana), Sharira (koshas), Breath bridge.
3. Propitiation (Shanti) vs. Empowerment (Siddhi/Shakti) Doctrine & Strict Safeguards.
4. Classical Gemstone Prescriptions, Finger, Metal, Eclipse Safeguards (Shams al-Ma'arif).
5. Weak Planets & Karmic Roots: Avasthas, Shadbala threshold, Afflictions, Combustion, Debilitation.
6. Psychological & Karmic Symptom Atlas for all 9 Grahas.
7. House-by-House (1st to 12th) manifestation of planetary weakness.
8. Nakshatras - The Soul's Hidden Code: Moon Nakshatra as Karmic Container, Pada divisions.
9. Nakshatra Doshas: Gandanta (Water-Fire knots), Abhukta Mula (Nirriti), Vishaghati, Sarpa Dosha.
10. Complete 27 Nakshatras Encyclopedia & Rituals: Sound (Beeja), Sacred Geometry (Rekha), Dravya (Offerings), Deity, Animal (Yoni), Element (Tattva).
11. Sacred Timing & Karmic Routine Planner: Planetary Horas, Transits (Gochar), Dasha timing, Eclipses, Pushya Nakshatra.
"""

from typing import Dict, List, Any, Optional, Set
from pydantic import BaseModel, Field

# ─── 1. Canonical Source Reference Metadata ──────────────────────────────────
SANNU_AHMED_SOURCE: Dict[str, Any] = {
    "code": "SANNU_AHMED_RITUALS",
    "title_en": "Vedic Astrology Rituals & Remedies: Powerful Rituals & Remedies for a Fulfilling Life",
    "title_sa": "वैदिकज्योतिषसद्कर्मप्रायश्चित्तविधिः",
    "author": "Sannu Ahmed (Jyotish Sadhak)",
    "tradition": "vedic_tantric_syncretic",
    "canonical_status": "modern_shastra_commentary",
    "description": (
        "Groundbreaking spiritual almanac synthesizing Brihat Parashara Hora Shastra, Jaimini Sutras, "
        "Yajurveda, Atharvaveda, Shams al-Ma'arif, Picatrix, and Tantric-Ayurvedic esoteric wisdom. "
        "Decodes the threefold karmic matrix, sacred geometry of yantras, nakshatra doshas, "
        "and the soul-body-energy circuit."
    ),
    "is_published": True,
}

# ─── 2. Threefold Karma Architecture ─────────────────────────────────────────
KARMA_ARCHITECTURE: Dict[str, Any] = {
    "sanchita": {
        "title_en": "Sanchita Karma (The Reservoir of Past Impressions)",
        "title_ta": "சஞ்சித கர்மா (சேமிக்கப்பட்ட பூர்வ புண்ணிய-பாவ கர்ம வினைகள்)",
        "nature": "Dormant, vast cosmic warehouse of all accumulated actions across countless lifetimes.",
        "planetary_reflection": "Cumulative strength or deep debility of planets across chart layers.",
        "immutable_level": "Latent; requires cumulative spiritual fire (tapas, jnana, Atma Vichara) to dissolve.",
        "remedial_strategy_en": "Deep purification through prolonged sadhana, pilgrimages (Teertha Yatra), Nishkama Karma Yoga, scriptural contemplation, and charity to 108 needy souls.",
        "remedial_strategy_ta": "தொடர் தவப்பயிற்சி, தீர்த்த யாத்திரை, பலனை எதிர்பாராத நிஷ்காம கர்ம யோகம் மற்றும் வேதாந்த சிந்தனை மூலம் படிந்த கர்ம வினைகளைக் கரைத்தல்.",
    },
    "prarabdha": {
        "title_en": "Prarabdha Karma (The Arrow Already Released)",
        "title_ta": "பிராரப்த கர்மா (இந்த ஜென்மத்தில் அனுபவிக்கத் தொடங்கிய கர்ம பலன்கள்)",
        "nature": "That portion of Sanchita brought into manifestation for this current incarnation. Irreversible in course, but mitigatable in impact.",
        "subdivisions": {
            "acharaniya": {
                "name_en": "Acharaniya Prarabdha (Immutable Core)",
                "name_ta": "அசரணிய பிராரப்தம் (மாற்ற முடியாதவை)",
                "description_en": "Fixed bodily parameters, biological parents, date of birth, genetic endowment, unalterable milestones.",
                "description_ta": "பிறப்பு சூழல், பெற்றோர், பிறந்த தேதி மற்றும் மரபணு சார்ந்த அசைக்க முடியாத கர்மா.",
            },
            "vasaniya": {
                "name_en": "Vasaniya Prarabdha (Modifiable Tendencies)",
                "name_ta": "வாசனிய பிராரப்தம் (சாந்தியால் தணிக்கக் கூடியவை)",
                "description_en": "Propensity toward certain ailments, mental distress, financial fluctuation; softened by accurate Graha Shanti.",
                "description_ta": "மன உளைச்சல், நோய்த் தாக்கம் மற்றும் தொழில் தடைகள்; உரிய சாந்தி பரிகாரங்களால் வேகம் தணிக்கப்படக் கூடியவை.",
            },
        },
        "planetary_reflection": "Saturn (limitations/justice), Rahu/Ketu (karmic axis), running Dasha lords, and malefic transits (e.g. Sade Sati).",
        "remedial_strategy_en": "Immediate alleviation through Graha Shanti: targeted beeja mantras, consecrated yantras, sacred gemstones, planetary homas, and protective Rudraksha beads (cushioning the blow like a cloth over a burning coal).",
        "remedial_strategy_ta": "உடனடி சாந்தி பரிகாரங்கள்: பீஜ மந்திர ஜபம், யந்திரப் பிரதிஷ்டை, தர்ம தானங்கள், ஹோமங்கள் மற்றும் ருத்ராட்ச தாரணம் மூலம் பாதிப்பின் தீவிரத்தைக் குறைத்தல்.",
    },
    "kriyamana": {
        "title_en": "Kriyamana / Agami Karma (The Seeds We Sow Now)",
        "title_ta": "கிரியாமாண / ஆகாமி கர்மா (தற்போது விதைக்கப்படும் புதிய கர்ம வினைகள்)",
        "nature": "Fresh impressions generated through present volitional thoughts, speech (vak), and deeds. Completely within conscious human agency.",
        "types": {
            "punya": "Meritorious seeds from selfless service, truthful speech, feeding the hungry, honoring ancestors.",
            "papa": "Sinful seeds accrued from greed, anger, harm to beings, deceit, or sensual exploitation.",
        },
        "planetary_reflection": "Governed by Rahu's forward desire and active choices of Lagna and 3rd house willpower.",
        "remedial_strategy_en": "Future prevention through daily Japa-mala discipline, mindful living (satya-sadhana), planetary fasting (Upavasa), consecrated Guru mantras, and offering fruits of action to Ishvara (Nishkama Karma).",
        "remedial_strategy_ta": "தினசரி மந்திர ஜபம், விரத அனுஷ்டானங்கள், குரு உபதேசம் மற்றும் தர்ம நெறியிலான விழிப்புணர்வு வாழ்க்கை மூலம் எதிர்கால வினைகளைத் தடுத்தல்.",
    },
}

# ─── 3. The Soul-Body-Energy Circuit ─────────────────────────────────────────
SOUL_BODY_CIRCUIT: Dict[str, Any] = {
    "atma": {
        "title_en": "Atma (Soul - The Pure Witness)",
        "title_ta": "ஆத்மா (சாட்சி உணர்வு)",
        "description_en": "Untouched like the Sun, but reflects distortions through the mind and subtle body.",
    },
    "prana": {
        "title_en": "Prana (Vital Energy - The Karma Conduit)",
        "title_ta": "பிராணன் (கர்ம ஆற்றல் கடத்தி)",
        "description_en": "Flows through 72,000 nadis carrying karmic scent from past lives. Blockages manifest as chronic disease and distress.",
        "bridge": "Conscious breath (Pranayama / Chandra Bhedana) directly recalibrates pranic conduits.",
    },
    "sharira": {
        "title_en": "Sharira (Physical & Subtle Bodies - Karma Storage)",
        "title_ta": "சரீரம் (கர்ம சேமிப்பு களம்)",
        "description_en": "Annamaya kosha (physical body) solidifies genetics and diseases; Manomaya and Vijnanamaya koshas store karmic vasanas.",
    },
    "remedial_mechanics": [
        {"tool": "Mantra", "action": "Vibrational cleanser targeting subtle nadi blocks to dissolve karmic density."},
        {"tool": "Homa / Agni", "action": "Subtle body reprogramming; bioenergetic offerings carried into akashic realms to melt Prarabdha."},
        {"tool": "Gemstone", "action": "Radiant frequency condenser feeding specific planetary light into the nadi circuit."},
        {"tool": "Yantra", "action": "Electro-geometric stabilizer resetting aura resonance fields."},
        {"tool": "Fasting & Dana", "action": "Pranic liberation and intentional energetic transference with cosmic law."},
    ],
    "golden_prerequisites": [
        "Shraddha (Unwavering authentic faith)",
        "Niyama (Purity of conduct and timing discipline)",
        "Adhikara (Ethical eligibility and reverence)",
    ],
}

# ─── 4. Propitiation (Shanti) vs. Empowerment (Shakti) Doctrine ───────────────
PROPITIATION_VS_EMPOWERMENT: Dict[str, Any] = {
    "core_law": (
        "When the planet is auspicious and placed in strength, empowering it will bring siddhi; "
        "but when afflicted, empowering it invites ruin. (Picatrix Book II)"
    ),
    "shanti_karmas": {
        "definition_en": "Propitiation / Dosha Nivarana: Pacifying afflicted, debilitated, combust, enemy-placed, or Paap Kartari planets.",
        "definition_ta": "சாந்தி கர்மா / தோஷ நிவர்த்தி: நீசம், அஸ்தமனம், பகை அல்லது பாபகர்த்தாரி யோகத்தில் சிக்கிய கிரகங்களை சாந்தப்படுத்துதல்.",
        "golden_rule": "NEVER energize or amplify an afflicted planet! Pacify it first with Vedic Beeja Mantras, Dana, Fasting, and Shanti Homas.",
        "beeja_mantras": {
            "sun": {"mantra": "ॐ घृणिः सूर्याय नमः", "iast": "oṃ ghṛṇiḥ sūryāya namaḥ", "ta": "ஓம் கிருணிஃ சூர்யாய நமஹ", "effect": "Calms ego, heals father karma"},
            "moon": {"mantra": "ॐ सोमाय नमः", "iast": "oṃ somāya namaḥ", "ta": "ஓம் சோமாய நமஹ", "effect": "Soothes emotional volatility and mental anxiety"},
            "mars": {"mantra": "ॐ कुं भौमाय नमः", "iast": "oṃ kuṃ bhaumāya namaḥ", "ta": "ஓம் கும் பௌமாய நமஹ", "effect": "Neutralizes aggression, blood karma, and property friction"},
            "mercury": {"mantra": "ॐ बुधाय नमः", "iast": "oṃ budhāya namaḥ", "ta": "ஓம் புதாய நமஹ", "effect": "Corrects speech flaws, mental confusion, and commercial setbacks"},
            "jupiter": {"mantra": "ॐ बृहस्पतये नमः", "iast": "oṃ bṛhaspataye namaḥ", "ta": "ஓம் பிருஹஸ்பதயே நமஹ", "effect": "Heals broken guru lineage and restores divine wisdom"},
            "venus": {"mantra": "ॐ शुक्राय नमः", "iast": "oṃ śukrāya namaḥ", "ta": "ஓம் சுக்ராய நமஹ", "effect": "Cleanses toxic desires and heals marital strife"},
            "saturn": {"mantra": "ॐ शं शनैश्चराय नमः", "iast": "oṃ śaṃ śanaiścarāya namaḥ", "ta": "ஓம் சம் சனைச்சராய நமஹ", "effect": "Releases ancestral debts, delays, and chronic labor karma"},
            "rahu": {"mantra": "ॐ रां राहवे नमः", "iast": "oṃ rāṃ rāhave namaḥ", "ta": "ஓம் ராம் ராகவே நமஹ", "effect": "Dispels illusions, addictions, and ancestral serpent curses"},
            "ketu": {"mantra": "ॐ कें केतवे नमः", "iast": "oṃ keṃ ketave namaḥ", "ta": "ஓம் கேம் கேதவே நமஹ", "effect": "Pacifies spiritual confusion, phantom fears, and isolation"},
        },
        "charity_items": {
            "sun": {"items": "Wheat, ruby, jaggery, copper", "spiritual_reason": "Ego dissolution & solar vitality alignment"},
            "moon": {"items": "Rice, raw milk, white pearls, silver", "spiritual_reason": "Emotional purification & mental stability"},
            "mars": {"items": "Red lentils (masoor), red coral, copper", "spiritual_reason": "Blood karma cleansing & anger pacification"},
            "mercury": {"items": "Green gram (moong dal), emerald, green cloth", "spiritual_reason": "Intellectual purification & speech healing"},
            "jupiter": {"items": "Yellow split gram (chana dal), turmeric, gold, yellow cloth", "spiritual_reason": "Guru debt settlement & dharmic balance"},
            "venus": {"items": "White clothes, pure cow ghee, white field beans, diamonds", "spiritual_reason": "Desire purification & relationship harmony"},
            "saturn": {"items": "Black sesame, mustard oil, leather shoes, iron vessels", "spiritual_reason": "Labor karma and chronic suffering expiation"},
            "rahu": {"items": "Mustard oil, blue/smoky cloth, urad dal, lead items", "spiritual_reason": "Illusion-breaking & karmic shadow dispersal"},
            "ketu": {"items": "Ash (vibhuti), blankets, horsegram (kollu), sesame seeds", "spiritual_reason": "Ego detachment & spiritual liberation"},
        },
    },
    "empowerment_karmas": {
        "definition_en": "Siddhi / Shakti Karmas: Amplifying favorable, unafflicted, Yogakaraka, or Lagna benefic planets.",
        "definition_ta": "சித்தி / சக்தி கர்மா: சுப ஸ்தானத்தில் உள்ள யோககாரக அல்லது லக்ன சுப கிரகங்களின் தெய்வீக ஆற்றலை அதிகரித்தல்.",
        "methods": [
            "Tattva & Yantra Activation: Triangle (Fire - Mars/Sun), Square (Earth - Mercury/Saturn), Circle (Water/Spirit - Moon/Venus/Jupiter)",
            "Consecrated Gemstone Dharana (Strictly restricted to Yogakaraka & functional benefics)",
            "Mantra Siddhi via prolonged japa counts: 1,000 (minor), 10,000 (protection), 100,000 (siddhi/grace), 1,000,000 (divine union)",
        ],
        "gemstone_rules_and_cautions": {
            "sun": {"gem": "Ruby", "metal": "Gold", "finger": "Ring", "caution": "Do NOT wear if Sun is lord of 6th, 8th, or 12th house."},
            "moon": {"gem": "Pearl", "metal": "Silver", "finger": "Little", "caution": "Avoid if Moon is waning (Krishna Paksha) and afflicted by Saturn/Rahu."},
            "mars": {"gem": "Red Coral", "metal": "Copper/Gold", "finger": "Ring", "caution": "Strictly avoid in Mars-Ketu or Mars-Rahu volatile conjunctions."},
            "mercury": {"gem": "Emerald", "metal": "Bronze/Gold", "finger": "Little", "caution": "Prescribed solely for naturally weak, unafflicted Mercury."},
            "jupiter": {"gem": "Yellow Sapphire", "metal": "Gold", "finger": "Index", "caution": "Avoid if Jupiter rules 6th or 8th Dusthana houses."},
            "venus": {"gem": "Diamond", "metal": "Silver/Platinum", "finger": "Middle", "caution": "Do NOT use in Rahu-Venus conjunction (triggers toxic attachments)."},
            "saturn": {"gem": "Blue Sapphire", "metal": "Iron/Silver", "finger": "Middle", "caution": "MANDATORY 3-day pillow test before wearing; can cause instant upheaval if misaligned."},
            "rahu": {"gem": "Hessonite (Gomed)", "metal": "Silver", "finger": "Middle", "caution": "NEVER wear during Ketu Dasha or in 8th/12th house placements without guidance."},
            "ketu": {"gem": "Cat's Eye (Vaidurya)", "metal": "Silver", "finger": "Little", "caution": "Highly unstable and electrifying; wear only under realized guru's direction."},
        },
        "lunar_eclipse_warning": (
            "SHAMS AL-MA'ARIF SAFEGUARD: Never wear or consecrate any gemstone within 3 days of a Solar or Lunar Eclipse. "
            "Eclipses are cosmic karma portals where astral doorways open; wearing gems during eclipses attracts psychic turbulence."
        ),
    },
}

# ─── 5. Weak Planets: Psychological & Karmic Symptom Atlas ────────────────────
PLANETARY_WEAKNESS_ATLAS: Dict[str, Dict[str, Any]] = {
    "sun": {
        "title_en": "Weak Sun (Surya)",
        "title_ta": "பலவீனமான சூரியன்",
        "theme": "Collapse of Selfhood, Confidence, and Soul Integrity (Ahamkara / Atma-Bindu)",
        "psychological_symptoms": [
            "Low self-esteem, chronic identity confusion, feeling invisible or directionless",
            "Craves external approval yet dreads visibility and public leadership",
            "Emotional collapse or paralyzing shame when criticized",
            "Martyr complex: over-gives to purchase validation",
        ],
        "karmic_symptoms": [
            "Dishonor from authority figures, governmental bodies, or estranged father",
            "Lack of social recognition despite immense merit and dedication",
            "Physical manifestations: chronic fatigue, cardiac strain, optic/eyesight degradation",
        ],
        "tantric_insight": "The Sun represents the Atma-Bindu (Soul particle). Weakness causes pranic core misplacement, resulting in profound inner hollow.",
    },
    "moon": {
        "title_en": "Weak Moon (Chandra)",
        "title_ta": "பலவீனமான சந்திரன்",
        "theme": "Distorted Mind, Emotional Instability, and Past-Life Amnesia (Manas / Chitta)",
        "psychological_symptoms": [
            "Chronic mood swings, acute abandonment anxiety, panic disorders",
            "Sleep disturbances, haunting nightmares, emotional hypersensitivity",
            "Irrational phobias, clinging attachment to past grievances, mother-complex",
        ],
        "karmic_symptoms": [
            "Severe friction or traumatic separation from mother or maternal lineage",
            "Extreme financial liquidity volatility (money slips through fingers)",
            "Psychosomatic ailments and repeated emotional heartbreaks",
        ],
        "tantric_insight": "The Moon mirrors karmic memory of all births. When fractured, it projects chaotic phantom patterns onto present reality.",
    },
    "mars": {
        "title_en": "Weak Mars (Mangala)",
        "title_ta": "பலவீனமான செவ்வாய்",
        "theme": "Inhibited Will, Inward Rage, Energy Collapse (Bhuta Agni)",
        "psychological_symptoms": [
            "Passive-aggression, suppressed rage, bitter resentment",
            "Paralyzing fear of confrontation, procrastination on vital decisions",
            "Self-sabotage, feelings of physical/sexual inadequacy, masculine energy collapse",
        ],
        "karmic_symptoms": [
            "Accidents, cuts, burns, blood disorders, surgical interventions",
            "Perpetual land disputes, property loss, or bitter enmity with brothers",
            "Unresolved battlefield or violence karma from past incarnations",
        ],
        "tantric_insight": "Mars governs Bhuta Agni (elemental fire). When depressed, internal fire turns inward, becoming autoimmune self-harm.",
    },
    "mercury": {
        "title_en": "Weak Mercury (Budha)",
        "title_ta": "பலவீனமான புதன்",
        "theme": "Fractured Intellect, Deceptive Speech Karma, Nervous Chaos (Buddhi / Vak)",
        "psychological_symptoms": [
            "Scattered thinking, severe ADHD-like distraction, inability to finish tasks",
            "Compulsive lying, malicious sarcasm, gossiping tendencies",
            "Rapid speech paired with comprehension failure, anxiety-driven overthinking",
        ],
        "karmic_symptoms": [
            "Academic interruptions, memory lapses, disastrous commercial contracts",
            "Speech impediments, chronic misunderstandings, legal paperwork disasters",
            "Nervous breakdowns, skin allergies, respiratory allergies",
        ],
        "tantric_insight": "Reflects past-life intellectual manipulation, breach of written trust, or misuse of sacred esoteric texts.",
    },
    "jupiter": {
        "title_en": "Weak Jupiter (Guru)",
        "title_ta": "பலவீனமான குரு",
        "theme": "Lost Dharma, Dogmatic Blindness, Spiritual Bankruptcy (Guru Tattva)",
        "psychological_symptoms": [
            "Loss of faith, cynical nihilism alternating with naive gullibility",
            "Blind fanatical attachment to false teachers without moral discernment",
            "Compromising core ethical values for fleeting material comfort",
        ],
        "karmic_symptoms": [
            "Loss of ancestral wealth, delays in childbirth or grief through children",
            "Severe friction in marriage (for women, Jupiter is Pati-karaka)",
            "Disputes with universities, judges, priests, or spiritual mentors",
        ],
        "tantric_insight": "Shows spiritual dislocation: the soul broke sacred vows in past lifetimes and now wanders in dharmic fog.",
    },
    "venus": {
        "title_en": "Weak Venus (Shukra)",
        "title_ta": "பலவீனமான சுக்கிரன்",
        "theme": "Emotional Dependence, Sensual Addiction, Rinanubandha (Shukra Dhatu)",
        "psychological_symptoms": [
            "Feeling fundamentally unworthy of love, desperate need for romantic validation",
            "Vulnerability to toxic, abusive, or emotionally exploitative partners",
            "Sensual escapism (food, shopping, lust) to soothe inner emotional famine",
        ],
        "karmic_symptoms": [
            "Infidelity, bitter divorces, heavy financial debts through luxuries",
            "Reproductive disorders, hormonal imbalances, urinary/kidney issues",
            "Unfinished romantic contracts (Rinanubandha) causing cyclical heartbreak",
        ],
        "tantric_insight": "Venus holds Shukra Dhatu (creative ojas). Damage indicates misuse of romantic charm, betrayal, or sexual exploitation in prior births.",
    },
    "saturn": {
        "title_en": "Weak Saturn (Shani)",
        "title_ta": "பலவீனமான சனி",
        "theme": "Depression, Victim Mentality, Resistance to Karmic Pruning (Nyaya / Kala)",
        "psychological_symptoms": [
            "Chronic clinical depression, existential hopelessness, crippling inertia",
            "Deep aversion to responsibility, bitter victimhood mindset",
            "Cold, aloof withdrawal from human empathy, premature cynicism",
        ],
        "karmic_symptoms": [
            "Grinding poverty, chronic degenerative diseases, paralysis/bone issues",
            "Unrecognized servitude: laboring endlessly while others reap the credit",
            "Social isolation, abandonment by family, endless administrative delays",
        ],
        "tantric_insight": "Saturn is the Supreme Karmic Executioner. Resisting his purifying chisel turns inevitable maturation into bitter suffering.",
    },
    "rahu": {
        "title_en": "Weak Rahu (North Node)",
        "title_ta": "பலவீனமான ராகு",
        "theme": "Uncontrolled Worldly Cravings, Delusion, Ancestral Shadow (Maya)",
        "psychological_symptoms": [
            "Obsessive cravings, substance addictions, paranoia, manic highs and lows",
            "Disconnection from ethics, fascination with taboos and illicit shortcuts",
        ],
        "karmic_symptoms": [
            "Sudden scandalous downfalls, ancestral serpent curses (Sarpa Dosha)",
            "Vulnerability to negative psychic influences or astral entity attachments",
        ],
        "tantric_insight": "Rahu wounds by granting what one is spiritually unready to bear, drowning the ego in its own desires.",
    },
    "ketu": {
        "title_en": "Weak Ketu (South Node)",
        "title_ta": "பலவீனமான கேது",
        "theme": "Dissociation, Spiritual Bypassing, Aimless Wandering (Moksha)",
        "psychological_symptoms": [
            "Apathy, emotional numbness, ungrounded mystical escapism",
            "Fear of intimate connection, acute sense of alien detachment from humanity",
        ],
        "karmic_symptoms": [
            "Phantom physical pains that evade medical diagnosis",
            "Sudden abrupt separations without closure, spiritual delusion",
        ],
        "tantric_insight": "Ketu wounds by stripping away what one never truly owned, forcing the soul into the void of surrender.",
    },
}

# ─── 6. House-by-House Weakness Manifestation ────────────────────────────────
HOUSE_WEAKNESS_MANIFESTATION: Dict[int, Dict[str, str]] = {
    1: {
        "bhava_name": "Lagna Bhava (Self & Vitality)",
        "impact_en": "Distorts identity, causes autoimmune disorders, identity crises, chronic fatigue, and early childhood survival hurdles.",
        "impact_ta": "லக்னத்தில் பலவீனமான கிரகம் சுய அடையாளத்தை பாதிக்கும்; நாள்பட்ட உடல் சோர்வு மற்றும் உயிர் ஆற்றல் இழப்பை ஏற்படுத்தும்.",
        "tantric_key": "Kundalini base prana-shakti remains ungrounded; soul feels disconnected from physical vessel.",
    },
    2: {
        "bhava_name": "Dhana & Vak Bhava (Wealth & Speech)",
        "impact_en": "Disrupts speech (vak-shakti), invites harsh or deceitful speech karma, chronic money dissipation, and food/alcohol toxins.",
        "impact_ta": "வாக்கு மற்றும் தன ஸ்தானம்; வார்த்தைகளில் தடுமாற்றம், பொய் அல்லது கோபப் பேச்சு, குடும்பத்தில் விரிசல் மற்றும் நிதி இழப்பு.",
        "tantric_key": "Vak-shakti corrupted; creates negative speech karma that boomerangs across generations.",
    },
    3: {
        "bhava_name": "Sahaja & Parakrama Bhava (Courage & Siblings)",
        "impact_en": "Paralyzes initiative and courage, creates procrastination, bitter sibling friction, and communication failures.",
        "impact_ta": "தைரியம் மற்றும் இளைய சகோதரர் ஸ்தானம்; முடிவெடுப்பதில் தயக்கம், மன பயம் மற்றும் சகோதரர்களுடன் விரோதம்.",
        "tantric_key": "Suppresses Kama Shakti (desire impulse); fear of asserting truth in worldly arenas.",
    },
    4: {
        "bhava_name": "Sukha & Matru Bhava (Heart & Mother)",
        "impact_en": "Unsettles the heart sanctuary (Anahata chakra), induces chronic home instability, mother trauma, and real estate setbacks.",
        "impact_ta": "சுக மற்றும் மாத்ரு ஸ்தானம்; மன அமைதியின்மை, தாயாருக்கு உடல்நலக் குறைவு மற்றும் பூமி, வீடு அமைவதில் தடைகள்.",
        "tantric_key": "Anahata chakra blocked; unable to feel at home anywhere in the cosmos.",
    },
    5: {
        "bhava_name": "Putra & Purva Punya Bhava (Intelligence & Children)",
        "impact_en": "Clouds intellect (buddhi), blocks creative flow, causes painful romantic rejection, and delays/denies child blessings.",
        "impact_ta": "பூர்வ புண்ணியம் மற்றும் புத்திர ஸ்தானம்; புத்தி மந்தம், காதல் தோல்வி, புத்திர பாக்கியத் தாமதம் மற்றும் முற்பிறவி சாபங்கள்.",
        "tantric_key": "Manas Mandala fractured; soul suffers from amnesia of spiritual wisdom mastered in past births.",
    },
    6: {
        "bhava_name": "Ripu & Roga Bhava (Debts, Enemies, Disease)",
        "impact_en": "Flares up the Shadripus (inner 6 enemies: lust, anger, greed, ego, delusion, envy); creates chronic debts, litigation, workplace servitude.",
        "impact_ta": "ருண, ரோக, சத்ரு ஸ்தானம்; தீராத கடன், தொடர் மருத்துவச் செலவுகள், மறைமுக எதிரிகள் மற்றும் அலுவலகத்தில் அவமானம்.",
        "tantric_key": "Inner enemies conquer conscious will; planet bleeds energy through routine daily friction.",
    },
    7: {
        "bhava_name": "Kalatra & Jaya Bhava (Partnership & Marriage)",
        "impact_en": "Ruptures marital harmony, brings codependency, sexual dysfunctions, betrayal in business partnerships, and partner's suffering.",
        "impact_ta": "களத்திர ஸ்தானம்; தாம்பத்தியத்தில் விரிசல், தவறான உறவுகள், விவாகரத்து பயம் மற்றும் கூட்டுத் தொழிலில் ஏமாற்றம்.",
        "tantric_key": "Maya & Shakti mirror cracked; reflects past-life exploitation of love or beauty.",
    },
    8: {
        "bhava_name": "Randhra & Ayur Bhava (Occult, Trauma, Death-Rebirth)",
        "impact_en": "Triggers sudden catastrophic losses, unearned scandals, deep psychic paranoia, suicidal ideation, and blocked inheritance.",
        "impact_ta": "ஆயுள் மற்றும் அஷ்டம ஸ்தானம்; திடீர் விபத்துகள், அவமானம், தீராத பயம், பரம்பரை சொத்து இழப்பு மற்றும் அமானுஷ்ய தொல்லைகள்.",
        "tantric_key": "Kula Kundalini cave disturbed; karmic gates seal tight, trapping spiritual energy in dark caverns.",
    },
    9: {
        "bhava_name": "Dharma & Bhagya Bhava (Fortune, Guru, Father)",
        "impact_en": "Extinguishes the sacred flame of dharma; induces cynical atheism, bitter conflict with gurus/father, and wandering without purpose.",
        "impact_ta": "பாக்கிய மற்றும் தர்ம ஸ்தானம்; தெய்வ பக்தி இழப்பு, தந்தையுடன் மனக்கசப்பு, குரு துரோக தோஷம் மற்றும் அதிர்ஷ்டமின்மை.",
        "tantric_key": "Agya chakra guidance blinded; spiritual disobedience cuts the thread of ancestral grace.",
    },
    10: {
        "bhava_name": "Karma Bhava (Career & Public Life)",
        "impact_en": "Corrupts public duty, creates sudden workplace disgrace, friction with bosses, and chronic inability to find professional purpose.",
        "impact_ta": "தொழில் மற்றும் கர்ம ஸ்தானம்; பணியிடத்தில் அவப்பெயர், வேலையின்மை, அதிகாரிகளுடன் மோதல் மற்றும் லட்சியமின்மை.",
        "tantric_key": "Rajasic creative fire corrupted; past-life abuse of authority causes public karmic demotion.",
    },
    11: {
        "bhava_name": "Labha Bhava (Gains, Desires, Network)",
        "impact_en": "Frustrates material fulfillment; creates recurring near-success failures, deceitful friends, and feeling like an eternal outsider.",
        "impact_ta": "லாப ஸ்தானம்; தொட்டதெல்லாம் நஷ்டம், கையில் காசு தங்காமை, போலி நண்பர்களின் துரோகம் மற்றும் ஆசைகள் நிறைவேறாமை.",
        "tantric_key": "Kama Siddhi corrupted; past fulfillment of desires through harmful means now attracts energetic resistance.",
    },
    12: {
        "bhava_name": "Vyaya & Moksha Bhava (Loss, Sleep, Liberation)",
        "impact_en": "Causes aimless financial drain, debilitating sleep disorders, dark nightmares, spiritual escapism, and painful isolation.",
        "impact_ta": "விரய மற்றும் மோட்ச ஸ்தானம்; வீண் விரயங்கள், தூக்கமின்மை, கெட்ட கனவுகள் மற்றும் தனிமையில் வாடும் நிலை.",
        "tantric_key": "Portal to subtle dimensions unshielded; native flees worldly duties instead of evolving into true moksha.",
    },
}

# ─── 7. Nakshatra Doshas: Critical Karmic Junctions ──────────────────────────
NAKSHATRA_DOSHAS: Dict[str, Any] = {
    "gandanta": {
        "title_en": "Gandanta Dosha (The Karmic Knots Between Water and Fire)",
        "title_ta": "கண்டாந்த தோஷம் (நீர் - நெருப்பு சந்திப்பு முடிச்சுகள்)",
        "junctions": [
            {
                "water_nakshatra": "Revati",
                "water_sign": "Pisces (Meena)",
                "fire_nakshatra": "Ashwini",
                "fire_sign": "Aries (Mesha)",
                "span": "26°40' Pisces to 03°20' Aries",
                "shanti_deity": "Ashwini Kumaras & Lord Vishnu",
                "remedy": "Recite Ashwini Kumar mantra, offer white rice to river, serve physicians and healers.",
            },
            {
                "water_nakshatra": "Ashlesha",
                "water_sign": "Cancer (Kataka)",
                "fire_nakshatra": "Magha",
                "fire_sign": "Leo (Simha)",
                "span": "26°40' Cancer to 03°20' Leo",
                "shanti_deity": "Nagas & Pitris (Ancestors)",
                "remedy": "Perform Sarpa Shanti, offer milk and turmeric to Naga shrines, chant Ketu beeja, perform Pitru Tarpana.",
            },
            {
                "water_nakshatra": "Jyeshtha",
                "water_sign": "Scorpio (Vrischika)",
                "fire_nakshatra": "Mula",
                "fire_sign": "Sagittarius (Dhanus)",
                "span": "26°40' Scorpio to 03°20' Sagittarius",
                "shanti_deity": "Lord Indra, Nirriti & Goddess Kali",
                "remedy": "Light sesame oil lamps for Kali, feed street dogs on Saturdays, perform Mula Shanti homa.",
            },
        ],
        "symptoms": [
            "Severe birth trauma or life-threatening infancy",
            "Rootless feeling, deep irrational phobias of water, fire, or serpents",
            "Cyclical resets in career and relationships: forced to start from scratch repeatedly",
            "Soul stands at an evolutionary precipice where old emotional karma burns in spiritual fire",
        ],
    },
    "abhukta_mula": {
        "title_en": "Abhukta Mula Dosha (The Untouched Karmic Fire of Nirriti)",
        "title_ta": "அபுக்த மூல தோஷம் (நிர்ருதி தேவியின் மூல நட்சத்திர தோஷம்)",
        "span": "First 00°00' to 13°20' of Mula Nakshatra (Sagittarius)",
        "deity": "Nirriti (Goddess of Dissolution and Root Destruction)",
        "symptoms": [
            "Heavy ancestral burden causing generational misfortunes",
            "Childhood health fragility; estrangement from mother or paternal lineage",
            "Sudden root-level upheaval and loss of inheritances",
        ],
        "mandatory_shanti": [
            "Delay the formal child naming ceremony (Namakaran) until the 25th or 27th day.",
            "Perform Abhukta Mula Shanti Homa on the 27th day when Moon returns to Mula.",
            "Chant 'Om Nirrittaye Namah' with a black sesame oil lamp under a Neem tree.",
            "Feed seven women and one cow on Saturday during waning moon phase.",
        ],
    },
    "vishaghati": {
        "title_en": "Vishaghati Nakshatras (Poisoned Astral Channels)",
        "title_ta": "விஷகடி நட்சத்திரங்கள் (நச்சுத்தன்மை கொண்ட கர்ம அலைவரிசைகள்)",
        "vulnerable_nakshatras": ["Ashlesha", "Mula", "Ardra", "Jyeshtha", "Purvabhadra"],
        "nature": "Zones where lunar nadis are acutely susceptible to ancestral curses, psychic contamination, and past betrayal.",
        "shanti_procedure": "Perform Naga Bali, Kala Sarpa Shanti, chant Rudram / Chamakam, and recite Nakshatra beeja mantras during lunar transit.",
    },
}

# ─── 8. Complete 27 Nakshatras Encyclopedia & Sacred Rituals ─────────────────
# Incorporates all attributes: Deity, Animal (Yoni), Tattva (Element), Symbol,
# Esoteric Decoding, Sacred Geometry (Rekha), Sound Mantra (Shabda), and Dravya (Offerings).
NAKSHATRA_RITUALS_ENCYCLOPEDIA: List[Dict[str, Any]] = [
    {
        "number": 1,
        "name": "Ashwini",
        "name_ta": "அசுவினி",
        "ruling_planet": "ketu",
        "ruling_deity": "Ashwini Kumaras (Celestial Twin Physicians)",
        "ruling_deity_ta": "அஸ்வினி குமாரர்கள்",
        "karmic_theme": "Past misuse of speed or healing powers; current quest for instantaneous recovery and self-initiation.",
        "animal_yoni": "Male Horse (Ashva)",
        "yoni_instinct": "Speed, independence, impatience with partnerships.",
        "tattva": "Earth (Prithvi)",
        "symbol": "Horse Head",
        "esoteric_symbol_meaning": "Vehicle of intention travelling between etheric realms; pranic surge of the cosmos.",
        "sacred_geometry": "Double Spiral / Twin Serpent Coil converging at center inside a circle.",
        "sound_mantra": "ॐ अश्विनिकुमाराय नमः",
        "sound_mantra_bija": "ॐ ऐं ह्रीं क्लीं अश्विन्यै नमः",
        "sound_mantra_ta": "ஓம் அஸ்வினிகுமாராய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Boiled milk with Ashwagandha root offered to twin flames; white lotus; twin ghee lamps in silver bowls on Tuesdays.",
        "ritual_procedure": "Draw double spiral on copper plate at sunrise, anoint with sandalwood oil, chant 108 times while focusing on rhythmic breath.",
        "sacred_tree": "Strychnos nux-vomica (Etti / Poison Nut)",
    },
    {
        "number": 2,
        "name": "Bharani",
        "name_ta": "பரணி",
        "ruling_planet": "venus",
        "ruling_deity": "Yama (Lord of Dharma & Sacred Death)",
        "ruling_deity_ta": "எமதர்ம ராஜன்",
        "karmic_theme": "Abuse of sensuality or moral restraint in past lives; current struggle between carnal passion and spiritual purity.",
        "animal_yoni": "Male Elephant (Gaja)",
        "yoni_instinct": "Sensual majesty, obstinate persistence, territorial protectiveness.",
        "tattva": "Earth (Prithvi)",
        "symbol": "Yoni (Sacred Womb) / Burial Pot",
        "esoteric_symbol_meaning": "The interdimensional portal where karma gestates and karmic contracts dissolve.",
        "sacred_geometry": "Downward-pointing Inverted Triangle inside a Circle with vertical axis.",
        "sound_mantra": "ॐ यमाय धर्महस्ताय नमः",
        "sound_mantra_bija": "ॐ ह्रीं यं धरणीधराय फट्",
        "sound_mantra_ta": "ஓம் யமாய தர்மஹஸ்தாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Red hibiscus offered to Goddess Kali; black sesame and mustard oil to Shani shrine; coconut and tamarind buried in earth on Friday.",
        "ritual_procedure": "Carve inverted triangle on copper plate, place under a Peepal tree on Friday night, pour rosewater and chant.",
        "sacred_tree": "Phyllanthus emblica (Nelli / Amla)",
    },
    {
        "number": 3,
        "name": "Krittika",
        "name_ta": "கிருத்திகை",
        "ruling_planet": "sun",
        "ruling_deity": "Agni (God of Sacred Fire)",
        "ruling_deity_ta": "அக்னி பகவான்",
        "karmic_theme": "Misuse of authority or fiery wrath; current trial by fire demanding purification of impure speech and ego.",
        "animal_yoni": "Female Sheep (Mesha)",
        "yoni_instinct": "Headstrong confrontation, communal loyalty.",
        "tattva": "Fire (Agni)",
        "symbol": "Razor, Flame, or Cutting Knife",
        "esoteric_symbol_meaning": "Sword of discernment (logos) cutting etheric cords and severing illusory attachments.",
        "sacred_geometry": "Upward Pointing Triangle (Agni Yantra) or Six-Pointed Hexagram.",
        "sound_mantra": "ॐ अग्नये स्वाहा",
        "sound_mantra_bija": "ॐ रां रामाय नमः",
        "sound_mantra_ta": "ஓம் அக்னயே ஸ்வாஹா",
        "japa_count": 108,
        "offerings_dravya": "Cow ghee, camphor, and uncooked rice offered to sacred Homa fire; red cloth and lentils on Tuesdays.",
        "ritual_procedure": "Draw flaming knife inside upward triangle on dried banyan leaf; burn with camphor at sunrise while chanting.",
        "sacred_tree": "Ficus glomerata (Athi / Cluster Fig)",
    },
    {
        "number": 4,
        "name": "Rohini",
        "name_ta": "ரோகிணி",
        "ruling_planet": "moon",
        "ruling_deity": "Prajapati / Brahma (Cosmic Creator)",
        "ruling_deity_ta": "பிரம்ம தேவன்",
        "karmic_theme": "Excessive vanity, romantic obsession, emotional manipulation; current lesson of unconditional nurturing.",
        "animal_yoni": "Male Serpent (Sarpa)",
        "yoni_instinct": "Hypnotic charm, secretiveness, intense attachment.",
        "tattva": "Earth (Prithvi)",
        "symbol": "Ox Cart or Chariot",
        "esoteric_symbol_meaning": "Vehicle of will moving toward physical manifestation; four wheels representing the four Purusharthas.",
        "sacred_geometry": "Square with Four Lotuses at Corners or Circle inside a Four-Petaled Lotus.",
        "sound_mantra": "ॐ प्रजापतये नमः",
        "sound_mantra_bija": "ॐ ह्रीं रोहिण्यै नमः",
        "sound_mantra_ta": "ஓம் பிரஜாபதயே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Raw cow's milk, white lotus petals, rosewater offered to Moon; white rice kheer offered to cows on Mondays.",
        "ritual_procedure": "Draw full moon mandala with white chalk, place milk bowl under moonlight, chant 108 times for emotional stabilization.",
        "sacred_tree": "Eugenia jambolana (Naval / Jamun)",
    },
    {
        "number": 5,
        "name": "Mrigashira",
        "name_ta": "மிருகசீரிஷம்",
        "ruling_planet": "mars",
        "ruling_deity": "Soma / Chandra (Nectar of Immortality)",
        "ruling_deity_ta": "சோம பகவான் / சந்திரன்",
        "karmic_theme": "Fickle wandering of the senses, perpetual romantic discontent; current quest for authentic spiritual nectar.",
        "animal_yoni": "Female Serpent (Sarpa)",
        "yoni_instinct": "Hypnotic search, sensory hunger, restless wandering.",
        "tattva": "Earth (Prithvi)",
        "symbol": "Deer's Head",
        "esoteric_symbol_meaning": "Fragile soul seeking rest in the cosmic forest; astral body seeking its eternal spring.",
        "sacred_geometry": "Crescent Moon cradling a Central Dot (Bindu) within a Circle.",
        "sound_mantra": "ॐ सोमाय चन्द्रमसे नमः",
        "sound_mantra_bija": "ॐ सां सोमाय नमः",
        "sound_mantra_ta": "ஓம் சோமாய சந்திரமஸே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "White sandalwood paste, white kheer, silver cup filled with water charged under moonlight.",
        "ritual_procedure": "Inscribe deer horns encircling a crescent moon on silver or sandalwood; recite under waxing moon at midnight.",
        "sacred_tree": "Acacia catechu (Karungali / Black Cutch)",
    },
    {
        "number": 6,
        "name": "Ardra",
        "name_ta": "திருவாதிரை",
        "ruling_planet": "rahu",
        "ruling_deity": "Rudra (Storm God / Destructive Aspect of Shiva)",
        "ruling_deity_ta": "ருத்ர பெருமான்",
        "karmic_theme": "Emotional violence, karmic betrayals, sudden storms of destiny; current baptism through sacred tears.",
        "animal_yoni": "Female Dog (Shvan)",
        "yoni_instinct": "Unconditional loyalty mixed with defensive aggression, trauma vigilance.",
        "tattva": "Water (Apas)",
        "symbol": "Teardrop or Diamond",
        "esoteric_symbol_meaning": "Crystallized karmic grief transforming into third-eye diamond brilliance.",
        "sacred_geometry": "Lightning Bolt with Trident Base cutting through a Circle.",
        "sound_mantra": "ॐ नमः शिवाय",
        "sound_mantra_bija": "ॐ रां रां रुद्राय फट्",
        "sound_mantra_ta": "ஓம் ருத்ராய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Sacred ash (vibhuti), bilva leaves, red chillies floated in water, feeding street dogs at dusk.",
        "ritual_procedure": "Etch lightning bolt on black stone, apply vibhuti, chant Rudram or Mahamrityunjaya during twilight storms.",
        "sacred_tree": "Aquilaria agallocha (Agarwood / Chenchandanam)",
    },
    {
        "number": 7,
        "name": "Punarvasu",
        "name_ta": "புனர்பூசம்",
        "ruling_planet": "jupiter",
        "ruling_deity": "Aditi (Cosmic Mother of the Devas)",
        "ruling_deity_ta": "அதிதி தேவி",
        "karmic_theme": "Loss of spiritual home, repeated aborted beginnings; current blessing of cosmic renewal and redemption.",
        "animal_yoni": "Female Cat (Marjara)",
        "yoni_instinct": "Autonomous grace, domestic independence, protective maternal energy.",
        "tattva": "Water (Apas)",
        "symbol": "Quiver of Arrows",
        "esoteric_symbol_meaning": "Divine readiness; inexhaustible arrows of karmic timelines returning to the sacred bow.",
        "sacred_geometry": "Infinity Loop (Lemniscate) or Two Interlinked Golden Circles.",
        "sound_mantra": "ॐ अदितये नमः",
        "sound_mantra_bija": "ॐ ह्रीं पुनर्वसवे नमः",
        "sound_mantra_ta": "ஓம் அதிதயே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Yellow split moong dal cooked with pure cow ghee; turmeric, tulasi leaves, donations to maternity shelters.",
        "ritual_procedure": "Draw twin golden circles in turmeric paste at Brahma Muhurta on Thursday, meditate on maternal restoration.",
        "sacred_tree": "Bambusa arundinacea (Moongil / Bamboo)",
    },
    {
        "number": 8,
        "name": "Pushya",
        "name_ta": "பூசம்",
        "ruling_planet": "saturn",
        "ruling_deity": "Brihaspati (Supreme Preceptor of the Gods)",
        "ruling_deity_ta": "பிருஹஸ்பதி / குரு பகவான்",
        "karmic_theme": "Spiritual pride, disrespect to gurus in past lives; current role as the cosmic nourisher and protector of dharma.",
        "animal_yoni": "Male Goat / Ram (Aja)",
        "yoni_instinct": "Patient grazing, steadfast climbing, selfless devotion.",
        "tattva": "Water (Apas)",
        "symbol": "Cow's Udder or Blossoming Lotus",
        "esoteric_symbol_meaning": "The milk of the cosmos pouring seventh-ray divine healing into human hearts.",
        "sacred_geometry": "Hexagon with Central Dot (Guru Mandala) encased in an Octagon.",
        "sound_mantra": "ॐ गुरवे नमः",
        "sound_mantra_bija": "ॐ पुष्याय बृहस्पतये नमः",
        "sound_mantra_ta": "ஓம் குரவே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Saffron-infused cow ghee lamps, yellow sweets, chana dal, donating to Vedic teachers and schools.",
        "ritual_procedure": "Draw Guru Mandala on banana leaf during Guru Hora on Thursday, light saffron ghee lamp, chant 108 times.",
        "sacred_tree": "Ficus religiosa (Arasamaram / Sacred Peepal)",
    },
    {
        "number": 9,
        "name": "Ashlesha",
        "name_ta": "ஆயில்யம்",
        "ruling_planet": "mercury",
        "ruling_deity": "Nagas (Divine Serpent Kings)",
        "ruling_deity_ta": "நாக தேவதைகள்",
        "karmic_theme": "Occult entanglements, manipulative secrecy, poisoning of speech; current transmutation of poison into wisdom.",
        "animal_yoni": "Male Cat (Marjara)",
        "yoni_instinct": "Silent stalking, territorial possession, hypnotic stare.",
        "tattva": "Water (Apas)",
        "symbol": "Coiled Serpent",
        "esoteric_symbol_meaning": "Kundalini shakti in deep latency; guarding the treasure of astral memories.",
        "sacred_geometry": "Coiled Spiral around a Vertical Axis inside an Inverted Triangle.",
        "sound_mantra": "ॐ நमो भगवते वासुकि नागाय",
        "sound_mantra_bija": "ॐ ह्रीं आश्लेषायै फट्",
        "sound_mantra_ta": "ஓம் வாசுகி நாகாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Raw milk and turmeric poured over Naga idols under Peepal trees; vetiver and cedarwood incense.",
        "ritual_procedure": "Draw spiral serpent on black stone with charcoal, offer sesame oil on Amavasya, meditate on ascending kundalini.",
        "sacred_tree": "Calophyllum inophyllum (Punnai / Alexandrian Laurel)",
    },
    {
        "number": 10,
        "name": "Magha",
        "name_ta": "மகம்",
        "ruling_planet": "ketu",
        "ruling_deity": "Pitris (Ancestral Spirits & Forefathers)",
        "ruling_deity_ta": "பித்ரு தேவதைகள்",
        "karmic_theme": "Royal arrogance, neglect of ancestral duties; current burden to heal and elevate the lineage.",
        "animal_yoni": "Male Rat (Mushika)",
        "yoni_instinct": "Gathering underground resources, survival persistence, family hoarding.",
        "tattva": "Water (Apas)",
        "symbol": "Royal Throne / Palanquin",
        "esoteric_symbol_meaning": "Ancestral throne crystallized as both power and karmic debt passed across generations.",
        "sacred_geometry": "Upside-Down Triangle with Eternal Flame at Center beneath a Crown.",
        "sound_mantra": "ॐ नमो भगवते पितृभ्यो स्वाहा",
        "sound_mantra_bija": "ॐ ह्रीं मघायै नमः",
        "sound_mantra_ta": "ஓம் பித்ருப்யோ நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Tarpana with black sesame and kusha grass; cooked rice offered to crows; sesame oil lamp under Peepal on Saturdays.",
        "ritual_procedure": "Inscribe lineage name inside clay throne, offer black sesame, chant at Amavasya or Pitru Paksha.",
        "sacred_tree": "Ficus benghalensis (Aalamaram / Banyan)",
    },
    {
        "number": 11,
        "name": "Purva Phalguni",
        "name_ta": "பூரம்",
        "ruling_planet": "venus",
        "ruling_deity": "Bhaga (God of Fortune & Prosperity)",
        "ruling_deity_ta": "பக தேவன்",
        "karmic_theme": "Hedonistic excess, misuse of wealth or partners; current lesson of sanctifying pleasure into bliss.",
        "animal_yoni": "Female Rat (Mushika)",
        "yoni_instinct": "Nest building, creative comfort, hoarding pleasures.",
        "tattva": "Fire (Agni)",
        "symbol": "Hammock, Swinging Couch, or Front Legs of a Bed",
        "esoteric_symbol_meaning": "Creative rest where life renews; initiation of sensual desire in divine alignment.",
        "sacred_geometry": "Circle with Five Radiating Petals (Panchakoshas of Bliss).",
        "sound_mantra": "ॐ भग देवाय नमः",
        "sound_mantra_bija": "ॐ ह्रीं फल्गुन्यै नमः",
        "sound_mantra_ta": "ஓம் பக தேவாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Jasmine flowers to Goddess Mahalakshmi; rosewater milk bath; donating silk cloth and sugar to women.",
        "ritual_procedure": "Etch five-petaled bliss circle on copper with rosewater, chant during Shukra Hora on Friday.",
        "sacred_tree": "Butea monosperma (Palasa / Flame of the Forest)",
    },
    {
        "number": 12,
        "name": "Uttara Phalguni",
        "name_ta": "உத்திரம்",
        "ruling_planet": "sun",
        "ruling_deity": "Aryaman (God of Sacred Contracts & Friendship)",
        "ruling_deity_ta": "அர்யமான்",
        "karmic_theme": "Broken oaths, disloyalty to companions; current duty to maintain sacred vows and dharmic covenants.",
        "animal_yoni": "Male Bull / Cow (Go)",
        "yoni_instinct": "Steady labor, steadfast commitment, protecting the herd.",
        "tattva": "Fire (Agni)",
        "symbol": "Four Legs of a Bed (Altar of Stability)",
        "esoteric_symbol_meaning": "The four ashramas of human life resting upon the four pillars of dharma.",
        "sacred_geometry": "Square Divided into Four Equal Quadrants (Altar of Balance).",
        "sound_mantra": "ॐ अर्यम्णे नमः",
        "sound_mantra_bija": "ॐ ह्रीं उत्तरफल्गुन्यै नमः",
        "sound_mantra_ta": "ஓம் அர்யம்ணே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Yellow flowers, whole wheat grains offered to Surya; feeding students, donating educational supplies.",
        "ritual_procedure": "Draw four quadrants in saffron ink on white cloth, place ghee lamps at each corner on Sunday sunrise.",
        "sacred_tree": "Ficus microcarpa (Ichi / Chinese Banyan)",
    },
    {
        "number": 13,
        "name": "Hasta",
        "name_ta": "அஸ்தம்",
        "ruling_planet": "moon",
        "ruling_deity": "Savitar (The Inspiring Solar God)",
        "ruling_deity_ta": "சவிதா / சூரிய பகவான்",
        "karmic_theme": "Past deceit, sleight of hand, thievery; current requirement to bless and heal through skilled hands.",
        "animal_yoni": "Female Buffalo (Mahisha)",
        "yoni_instinct": "Silent diligence, resilience in hardship, grounding patience.",
        "tattva": "Fire (Agni)",
        "symbol": "Open Palm / Hand",
        "esoteric_symbol_meaning": "Mudra Shakti: the divine hand shaping destiny and projecting cosmic grace.",
        "sacred_geometry": "Five-Pointed Star (Pentagram) Inside a Radiant Sun Circle.",
        "sound_mantra": "ॐ सवित्रे नमः",
        "sound_mantra_bija": "ॐ ह्रीं हस्ताय नमः",
        "sound_mantra_ta": "ஓம் சவித்ரே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Handmade offerings, feeding beggars with own hands, offering turmeric rice to Surya.",
        "ritual_procedure": "Trace open palm in turmeric on white cloth, place unbroken rice in center, chant at sunrise facing East.",
        "sacred_tree": "Sesbania grandiflora (Agathi / Hummingbird Tree)",
    },
    {
        "number": 14,
        "name": "Chitra",
        "name_ta": "சித்திரை",
        "ruling_planet": "mars",
        "ruling_deity": "Tvashtar / Vishwakarma (Divine Cosmic Architect)",
        "ruling_deity_ta": "விஸ்வகர்மா",
        "karmic_theme": "Pride in external appearance, superficial vanity; current duty to craft structural beauty from spiritual struggle.",
        "animal_yoni": "Female Tiger (Vyaghra)",
        "yoni_instinct": "Fierce artistic instinct, solitary elegance, hunting perfection.",
        "tattva": "Fire (Agni)",
        "symbol": "Bright Pearl or Polished Gem",
        "esoteric_symbol_meaning": "Soul refined through immense pressure; tear of suffering transmuted into eternal jewel.",
        "sacred_geometry": "Hexagram (Star of Creation) inside a Square.",
        "sound_mantra": "ॐ विश्वकर्मणे नमः",
        "sound_mantra_bija": "ॐ ह्रीं चित्रायै नमः",
        "sound_mantra_ta": "ஓம் விஸ்வகர்மணே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Kumkum and red sandalwood on Shiva Lingam; donating building tools or metal instruments to artisans.",
        "ritual_procedure": "Place white crystal in silver bowl reflecting moonlight; recite during Mars hora for structural manifestation.",
        "sacred_tree": "Aegle marmelos (Vilvam / Bael)",
    },
    {
        "number": 15,
        "name": "Swati",
        "name_ta": "சுவாதி",
        "ruling_planet": "rahu",
        "ruling_deity": "Vayu (God of Cosmic Wind & Breath)",
        "ruling_deity_ta": "வாயு பகவான்",
        "karmic_theme": "Restless rootlessness, unanchored rebellion; current task of bending like a reed in the cosmic wind.",
        "animal_yoni": "Male Buffalo (Mahisha)",
        "yoni_instinct": "Endurance, stubborn will, slow evolutionary movement.",
        "tattva": "Fire (Agni)",
        "symbol": "Young Green Sprout in the Wind or Red Coral",
        "esoteric_symbol_meaning": "Humility before cosmic breath; growth through gentle yielding rather than rigid resistance.",
        "sacred_geometry": "Sine Wave Passing Through a Spiral Circle (Breath Cycle Pattern).",
        "sound_mantra": "ॐ वायवे नमः",
        "sound_mantra_bija": "ॐ ह्रीं स्वातये नमः",
        "sound_mantra_ta": "ஓம் வாயவே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Tying white thread around Banyan tree; offering incense to wind at sunrise; pranayama sadhana.",
        "ritual_procedure": "Draw spiral breeze symbol with blue-dyed rice on open rooftop, practice 15 min conscious breath, chant.",
        "sacred_tree": "Terminalia arjuna (Marudhamaram / Arjuna Tree)",
    },
    {
        "number": 16,
        "name": "Vishakha",
        "name_ta": "விசாகம்",
        "ruling_planet": "jupiter",
        "ruling_deity": "Indra-Agni (Dual Gods of Sovereignty & Sacred Fire)",
        "ruling_deity_ta": "இந்திரா அக்னி",
        "karmic_theme": "Destructive competition, obsession with triumphant goals; current challenge to unify divided inner wills.",
        "animal_yoni": "Male Tiger (Vyaghra)",
        "yoni_instinct": "Single-pointed ambush, insatiable territorial hunger.",
        "tattva": "Fire (Agni)",
        "symbol": "Triumphal Archway or Forked Branch",
        "esoteric_symbol_meaning": "Threshold of initiation where dual forces must merge to pass through the eye of dharma.",
        "sacred_geometry": "Vertical Trident with Central Fire Triangle.",
        "sound_mantra": "ॐ इन्द्राग्निभ्यां नमः",
        "sound_mantra_bija": "ॐ ह्रीं विशाखायै नमः",
        "sound_mantra_ta": "ஓம் இந்திராக்னிப்யாம் நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Red sandalwood chips, cloves, and sugar in fire rituals; two ghee lamps lit under a Banyan tree.",
        "ritual_procedure": "Create archway of sacred leaves, walk beneath after lighting dual flames, chant 108 times for inner unification.",
        "sacred_tree": "Limonia acidissima (Vilathi / Wood Apple)",
    },
    {
        "number": 17,
        "name": "Anuradha",
        "name_ta": "அனுஷம்",
        "ruling_planet": "saturn",
        "ruling_deity": "Mitra (God of Divine Friendship & Alliances)",
        "ruling_deity_ta": "மித்ரன்",
        "karmic_theme": "Past betrayal of comrades or painful isolation; current flowering of the heart through devoted discipleship.",
        "animal_yoni": "Female Deer (Mriga)",
        "yoni_instinct": "Gentle grace, alert sensitivity, longing for herd community.",
        "tattva": "Fire (Agni)",
        "symbol": "Lotus Flower or Ascetic's Staff",
        "esoteric_symbol_meaning": "Heart blossoming out of the mud of Saturnian trials; ascetic staff of discipline.",
        "sacred_geometry": "Concentric Circles with Central Dot within a 12-Petaled Lotus.",
        "sound_mantra": "ॐ मित्राय नमः",
        "sound_mantra_bija": "ॐ ह्रीं अनुराधायै नमः",
        "sound_mantra_ta": "ஓம் மித்ராய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Curd and honey shared with children; donating shoes and umbrellas to wanderers; group Vishnu Sahasranama.",
        "ritual_procedure": "Engrave concentric circles on silver foil, offer honey, chant on Saturday evenings for reconciliation.",
        "sacred_tree": "Mimusops elengi (Magizhamaram / Spanish Cherry)",
    },
    {
        "number": 18,
        "name": "Jyeshtha",
        "name_ta": "கேட்டை",
        "ruling_planet": "mercury",
        "ruling_deity": "Indra (King of the Gods / Chief Sovereign)",
        "ruling_deity_ta": "இந்திர பகவான்",
        "karmic_theme": "Abuse of elder status, jealousy of younger peers; current burden of solitary leadership and occult responsibility.",
        "animal_yoni": "Male Deer (Mriga)",
        "yoni_instinct": "Proud vigilance, guarding the territory, sensitivity to betrayal.",
        "tattva": "Air (Vayu)",
        "symbol": "Circular Amulet, Talisman, or Earring",
        "esoteric_symbol_meaning": "Talismanic container of occult power; mirror of the unseen binding and releasing subtle forces.",
        "sacred_geometry": "Rhombus (Diamond) Inside a Circle with Piercing Central Staff.",
        "sound_mantra": "ॐ इन्द्राय नमः",
        "sound_mantra_bija": "ॐ ह्रीं ज्येष्ठायै नमः",
        "sound_mantra_ta": "ஓம் இந்திராய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Turmeric, betel leaves, pomegranate offered to Goddess Durga; silent service to one elderly soul on Thursdays.",
        "ritual_procedure": "Wear silver circular amulet engraved with nakshatra syllable on left arm; chant facing sunrise for psychic protection.",
        "sacred_tree": "Bombax ceiba (Ilanvamaram / Silk Cotton Tree)",
    },
    {
        "number": 19,
        "name": "Mula",
        "name_ta": "மூலம்",
        "ruling_planet": "ketu",
        "ruling_deity": "Nirriti (Goddess of Dissolution & Underground Roots)",
        "ruling_deity_ta": "நிர்ருதி தேவி",
        "karmic_theme": "Involvement in destructive black arts or violent past-life endings; current soul surgery uprooting illusions.",
        "animal_yoni": "Male Dog (Shvan)",
        "yoni_instinct": "Underworld guardianship, intense loyalty, protective biting.",
        "tattva": "Air (Vayu)",
        "symbol": "Tied Roots / Uprooted Stems",
        "esoteric_symbol_meaning": "Pre-birth contracts uncoiling; knot of black ether unraveling into liberation.",
        "sacred_geometry": "Inverted Black Triangle with Dot (Bindu) at Base (Root Portal).",
        "sound_mantra": "ॐ निर्ऋतये नमः",
        "sound_mantra_bija": "ॐ ह्रीं मूलायै नमः",
        "sound_mantra_ta": "ஓம் நிர்ருதயே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Red hibiscus, black sesame seeds, and mustard oil offered to Kali or Nirriti; vetiver root bundle tied in red thread.",
        "ritual_procedure": "Burn vetiver root bundle slowly with camphor during Krishna Paksha while chanting for ancestral curse dissolution.",
        "sacred_tree": "Mangifera indica (Maamaram / Mango Tree)",
    },
    {
        "number": 20,
        "name": "Purva Ashadha",
        "name_ta": "பூராடம்",
        "ruling_planet": "venus",
        "ruling_deity": "Apas (Cosmic Deified Waters)",
        "ruling_deity_ta": "அபாஸ் / ஜல தேவதைகள்",
        "karmic_theme": "Spiritual arrogance through premature victory; current purification of intention through sacred surrender.",
        "animal_yoni": "Male Monkey (Vanara)",
        "yoni_instinct": "Restless curiosity, playful leaps, social bonding.",
        "tattva": "Air (Vayu)",
        "symbol": "Winnowing Basket or Fan",
        "esoteric_symbol_meaning": "Separation of pure grain from illusory chaff; purification through divine emotional waters.",
        "sacred_geometry": "Crescent Moon over Intersecting Wavy Lines with Central Seed.",
        "sound_mantra": "ॐ अपोवित्र आपः स्वाहा",
        "sound_mantra_bija": "ॐ ह्रीं पूर्वाषाढायै नमः",
        "sound_mantra_ta": "ஓம் அபாம் பதயே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Coconut water and lotus petals floated in flowing river; saffron-soaked rice offered to Lakshmi on Fridays.",
        "ritual_procedure": "Place 9 grains in small bamboo sieve, blow gently while chanting, then float coconut water in river.",
        "sacred_tree": "Saraca asoca (Asokamaram / Ashoka Tree)",
    },
    {
        "number": 21,
        "name": "Uttara Ashadha",
        "name_ta": "உத்திராடம்",
        "ruling_planet": "sun",
        "ruling_deity": "Vishwadevas (Ten Universal Principles of Cosmic Law)",
        "ruling_deity_ta": "விஸ்வேதேவர்கள்",
        "karmic_theme": "Rigid legalism, stubborn moral pride; current alignment with invincible, compassionate universal law.",
        "animal_yoni": "Male Mongoose (Nakula)",
        "yoni_instinct": "Fearless combat with venomous forces, agile defense of righteousness.",
        "tattva": "Air (Vayu)",
        "symbol": "Elephant Tusk or Small Bed",
        "esoteric_symbol_meaning": "Bone of wisdom; single-pointed tusk of dharma piercing through the veil of ignorance.",
        "sacred_geometry": "Ten-Pointed Starburst (Ten Principles of Dharma) Rising Between Mountain Peaks.",
        "sound_mantra": "ॐ विश्वेदेवाय नमः",
        "sound_mantra_bija": "ॐ ह्रीं उत्तराषाढायै नमः",
        "sound_mantra_ta": "ஓம் விஸ்வேதேவாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Ghee lamps on hilltops facing sunrise; saffron robes donated to ascetics; practicing Surya Mudra.",
        "ritual_procedure": "Draw ten-pointed star in turmeric on banana leaf, meditate facing East at sunrise with Surya Mudra.",
        "sacred_tree": "Artocarpus heterophyllus (Palamaram / Jackfruit Tree)",
    },
    {
        "number": 22,
        "name": "Shravana",
        "name_ta": "திருவோணம்",
        "ruling_planet": "moon",
        "ruling_deity": "Vishnu (Supreme Preserver & Cosmic Listener)",
        "ruling_deity_ta": "மகாவிஷ்ணு",
        "karmic_theme": "Misuse of speech, spreading gossip, refusing to hear truth; current elevation through sacred listening (shravanam).",
        "animal_yoni": "Female Monkey (Vanara)",
        "yoni_instinct": "Imitative learning, vocal agility, attentive listening.",
        "tattva": "Air (Vayu)",
        "symbol": "Ear or Three Footprints of Vamana",
        "esoteric_symbol_meaning": "Organ of astral reception; listening as an act of divine obedience and soul recalibration.",
        "sacred_geometry": "Spiral Inside an Upward Triangle with Three Concentric Circles.",
        "sound_mantra": "ॐ नमो नारायणाय",
        "sound_mantra_bija": "ॐ ह्रीं श्रवणायै नमः",
        "sound_mantra_ta": "ஓம் நமோ நாராயணாய",
        "japa_count": 108,
        "offerings_dravya": "Tulasi leaves dipped in honey offered to Vishnu; donating warm blankets in winter; practicing silence (Mauna).",
        "ritual_procedure": "Write personal name on betel leaf, chant mantra aloud, close eyes and listen to echo in quiet meditation.",
        "sacred_tree": "Calotropis gigantea (Erukku / Crown Flower)",
    },
    {
        "number": 23,
        "name": "Dhanishta",
        "name_ta": "அவிட்டம்",
        "ruling_planet": "mars",
        "ruling_deity": "Ashta Vasus (Eight Elemental Devas of Prosperity)",
        "ruling_deity_ta": "அஷ்ட வசுக்கள்",
        "karmic_theme": "Greed for material hoard, exploitation of music/arts; current synchronization with cosmic rhythm.",
        "animal_yoni": "Female Lion (Simha)",
        "yoni_instinct": "Majestic territorial command, rhythmic coordination, fierce pride.",
        "tattva": "Ether (Akasha)",
        "symbol": "Mridanga (Drum) or Flute",
        "esoteric_symbol_meaning": "Heartbeat of time; rhythmic vibration calling planetary intelligences into harmony.",
        "sacred_geometry": "Square with Eight Petals Around (Octagram of Wealth and Sound).",
        "sound_mantra": "ॐ वसुभ्यो नमः",
        "sound_mantra_bija": "ॐ ह्रीं धनिष्ठायै नमः",
        "sound_mantra_ta": "ஓம் வசுப்யோ நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Milk poured on temple bronze bell; playing damaru or singing kirtan; donating brass vessels on Tuesdays.",
        "ritual_procedure": "Tap metal bowl rhythmically at sunrise, align incoming and outgoing breath with the beats, chant.",
        "sacred_tree": "Prosopis cineraria (Vannimaram / Shami Tree)",
    },
    {
        "number": 24,
        "name": "Shatabhisha",
        "name_ta": "சதயம்",
        "ruling_planet": "rahu",
        "ruling_deity": "Varuna (Guardian of Cosmic Law & Celestial Waters)",
        "ruling_deity_ta": "வருண பகவான்",
        "karmic_theme": "Secret misdeeds, occult transgressions; current burden of karmic illness seeking the 100 hidden healers.",
        "animal_yoni": "Female Horse (Ashva)",
        "yoni_instinct": "Solitary gallop, aloof independence, emotional veil.",
        "tattva": "Ether (Akasha)",
        "symbol": "Empty Circle or Hundred Healers",
        "esoteric_symbol_meaning": "Sigil of concealment and psychic containment; meeting one's shadow to birth the true cure.",
        "sacred_geometry": "Thousand-Petaled Chakra Encircling a Central Deep Blue Dot.",
        "sound_mantra": "ॐ वरुणाय नमः",
        "sound_mantra_bija": "ॐ ह्रीं शतभिषायै नमः",
        "sound_mantra_ta": "ஓம் வருணாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Black gram and cow ghee on Shiva Lingam; observed water fast on Amavasya; donating medicines to indigent patients.",
        "ritual_procedure": "Draw black circle with white ash, place mirror at center, sit within facing North and chant during Rahu Kaal.",
        "sacred_tree": "Nauclea cadamba (Kadambamaram / Burflower Tree)",
    },
    {
        "number": 25,
        "name": "Purva Bhadrapada",
        "name_ta": "பூரட்டாதி",
        "ruling_planet": "jupiter",
        "ruling_deity": "Aja Ekapada (The One-Footed Cosmic Fire Serpent)",
        "ruling_deity_ta": "அஜைகபாதர்",
        "karmic_theme": "Occult destruction, black tantric misuse, inner hypocrisy; current crucible of intense spiritual fire.",
        "animal_yoni": "Male Lion (Simha)",
        "yoni_instinct": "Ferocious solitary power, sovereign detachment.",
        "tattva": "Ether (Akasha)",
        "symbol": "Sword, Two-Faced Man, or Front Legs of a Funeral Cot",
        "esoteric_symbol_meaning": "Sacred lightning bolt incinerating false masks; crossing the veil between life and death.",
        "sacred_geometry": "Single Thunderbolt Piercing Two Opposing Horizontal Lines.",
        "sound_mantra": "ॐ अजैकपदाय नमः",
        "sound_mantra_bija": "ॐ ह्रीं पूर्वभाद्रपदायै नमः",
        "sound_mantra_ta": "ஓம் அஜைகபாதாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Black sesame and mustard oil offered to Bhairava; protecting and feeding stray dogs; complete abstention from deceit.",
        "ritual_procedure": "Place iron rod between two black stones on Thursday midnight, chant 108 times to sever demonic ego attachments.",
        "sacred_tree": "Azadirachta indica (Veppamaram / Neem)",
    },
    {
        "number": 26,
        "name": "Uttara Bhadrapada",
        "name_ta": "உத்திரட்டாதி",
        "ruling_planet": "saturn",
        "ruling_deity": "Ahirbudhnya (The Serpent of the Deepest Waters)",
        "ruling_deity_ta": "அஹிர்புத்னியன்",
        "karmic_theme": "Spiritual sloth, avoidance of reality; current awakening of the deep dormant ocean of kundalini.",
        "animal_yoni": "Female Cow (Go)",
        "yoni_instinct": "Patient endurance, silent ocean of milk, gentle steadiness.",
        "tattva": "Ether (Akasha)",
        "symbol": "Twin Back Legs of a Funeral Cot or Serpent in Deep Water",
        "esoteric_symbol_meaning": "Restful dormancy of kundalini at the base; subaqueous peace before resurrection.",
        "sacred_geometry": "Coiled Serpent Resting in a Spiral Flame within Water.",
        "sound_mantra": "ॐ अहिर्बुध्न्याय नमः",
        "sound_mantra_bija": "ॐ ह्रीं उत्तरभाद्रपदायै नमः",
        "sound_mantra_ta": "ஓம் அஹிர்புத்னியாய நமஹ",
        "japa_count": 108,
        "offerings_dravya": "Cow ghee offered to sacred fire in Agni homa; sea salt and turmeric bath; donating sleeping mats or sandals.",
        "ritual_procedure": "Place consecrated silver serpent in a vessel of sacred water on Saturday at Brahma Muhurta, chant 108 times.",
        "sacred_tree": "Azadirachta indica / Melia dubia (Malai Veppam / Malabar Neem)",
    },
    {
        "number": 27,
        "name": "Revati",
        "name_ta": "ரேவதி",
        "ruling_planet": "mercury",
        "ruling_deity": "Pushan (Guide of the Souls to the Far Shore)",
        "ruling_deity_ta": "பூஷா பகவான்",
        "karmic_theme": "Lack of direction, over-dependence on travelers; current completion of the wheel of rebirth.",
        "animal_yoni": "Female Elephant (Gaja)",
        "yoni_instinct": "Protective matriarchal guide, gentle wisdom, soul memory.",
        "tattva": "Ether (Akasha)",
        "symbol": "Pair of Fish Swimming in Circle or Mridanga Drum",
        "esoteric_symbol_meaning": "Souls navigating divine currents; safe astral journey across the waters of samsara into moksha.",
        "sacred_geometry": "Spiral Star Guiding a Boat across Waters.",
        "sound_mantra": "ॐ पूष्णे नमः",
        "sound_mantra_bija": "ॐ ह्रीं रेவत्यै नमः",
        "sound_mantra_ta": "ஓம் பூஷ்ணே நமஹ",
        "japa_count": 108,
        "offerings_dravya": "White rice, green cardamom, and cow ghee offered at Vishnu temple; donating footwear or travel fare for pilgrims.",
        "ritual_procedure": "Craft two rice fish figures on banana leaf, float on river at dusk while chanting for final karmic closure.",
        "sacred_tree": "Madhuca longifolia (Iluppaimaram / Mahua)",
    },
]

# Quick lookup by name
NAKSHATRA_BY_NAME: Dict[str, Dict[str, Any]] = {
    n["name"].lower(): n for n in NAKSHATRA_RITUALS_ENCYCLOPEDIA
}

# ─── 9. Sacred Timing & Karmic Routine Planner ───────────────────────────────
SACRED_TIMING_RULES: Dict[str, Any] = {
    "pushya_nakshatra": {
        "title_en": "Pushya Nakshatra (The King of Constellations)",
        "title_ta": "பூச நட்சத்திர மகா முகூர்த்தம்",
        "significance": "Ruled by Brihaspati; considered the most auspicious day for initiating all spiritual sadhanas, yantras, gold purchase, and higher remedies (except marriage).",
        "special_yogas": {
            "guru_pushya": "When Pushya falls on a Thursday: Supreme Yoga for invoking wisdom, wealth, and spiritual empowerment.",
            "shani_pushya": "When Pushya falls on a Saturday: Supreme Yoga for dissolving chronic delays, real estate blockages, and Saturnian curses.",
        },
    },
    "lunar_tithis": {
        "purnima": "Full Moon: Maximum pranic expansion. Best for Moon/Venus propitiation, Sri Vidya puja, water libations, and white donations.",
        "amavasya": "New Moon: Deepest subconscious access. Best for Pitru Tarpana, ancestral healing, Rahu/Ketu pacification, and shadow work.",
        "ekadashi": "11th Lunar Day: Complete or partial fasting burns Prarabdha and cleanses bodily toxemia (Ama).",
    },
    "eclipses": {
        "title_en": "Eclipses: Cosmic Karma Portals",
        "title_ta": "கிரகண கால கர்ம திறவு வாயில்கள்",
        "rules": [
            "Mantra repetition count during eclipses yields 1,000x to 100,000x regular potency.",
            "STRICT PROHIBITION: Never wear or buy gemstones within 3 days of an eclipse.",
            "Take ritual purificatory bath immediately after eclipse release.",
            "Donate raw grains and sesame seeds to release blocked ancestral shadows.",
        ],
    },
}


# ─── 10. Sannu Ahmed Rituals & Remedies Engine Class ─────────────────────────
class SannuRitualsEngine:
    """Core computational and diagnostic engine for Sannu Ahmed's Vedic Astrology Rituals & Remedies."""

    @staticmethod
    def get_all_nakshatra_rituals() -> List[Dict[str, Any]]:
        """Returns the complete 27 Nakshatras sacred rituals encyclopedia."""
        return NAKSHATRA_RITUALS_ENCYCLOPEDIA

    @staticmethod
    def get_nakshatra_ritual_by_name(name: str) -> Optional[Dict[str, Any]]:
        """Lookup nakshatra ritual by name (case-insensitive)."""
        clean_name = str(name).strip().lower().replace("_", "").replace("-", "").replace(" ", "")
        for n in NAKSHATRA_RITUALS_ENCYCLOPEDIA:
            n_clean = n["name"].lower().replace("_", "").replace("-", "").replace(" ", "")
            if n_clean == clean_name or clean_name in n_clean:
                return n
        return None

    @staticmethod
    def get_knowledge_overview() -> Dict[str, Any]:
        """Returns the high-level philosophical and practical knowledge overview."""
        return {
            "source": SANNU_AHMED_SOURCE,
            "karma_architecture": KARMA_ARCHITECTURE,
            "soul_body_circuit": SOUL_BODY_CIRCUIT,
            "propitiation_vs_empowerment": PROPITIATION_VS_EMPOWERMENT,
            "planetary_weakness_atlas": PLANETARY_WEAKNESS_ATLAS,
            "house_weakness_manifestation": {str(k): v for k, v in HOUSE_WEAKNESS_MANIFESTATION.items()},
            "nakshatra_doshas": NAKSHATRA_DOSHAS,
            "sacred_timing_rules": SACRED_TIMING_RULES,
        }

    @staticmethod
    def diagnose_chart_karma_and_rituals(
        lagna_sign: str,
        moon_sign: str,
        moon_nakshatra: str,
        planets_dict: Dict[str, Dict[str, Any]],
        running_mahadasha: Optional[str] = None,
        running_bhukti: Optional[str] = None,
        yogakaraka_planets: Optional[List[str]] = None,
        functional_benefics: Optional[List[str]] = None,
        functional_malefics: Optional[List[str]] = None,
        combust_planets: Optional[List[str]] = None,
        debilitated_planets: Optional[List[str]] = None,
        dusthana_planets: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Comprehensive Sannu Ahmed diagnostic:
        - Moon Nakshatra sacred geometry, deity, yoni, tattva, sound mantra, dravya.
        - Nakshatra Doshas (Gandanta, Abhukta Mula, Vishaghati, Sarpa Dosha).
        - 3-Fold Karma Blueprint (Sanchita, Prarabdha, Kriyamana).
        - Weak Planet Psychological & Karmic Symptom atlas.
        - Propitiation vs Empowerment classifications with Picatrix safeguards.
        - Sacred Timing & Routine Planner.
        """
        lagna_clean = lagna_sign.strip().lower() if lagna_sign else "aries"
        moon_nak_clean = str(moon_nakshatra).strip().lower()
        yogakarakas = set([p.lower() for p in (yogakaraka_planets or [])])
        benefics = set([p.lower() for p in (functional_benefics or [])])
        malefics = set([p.lower() for p in (functional_malefics or [])])
        combust = set([p.lower() for p in (combust_planets or [])])
        debilitated = set([p.lower() for p in (debilitated_planets or [])])
        running_md = running_mahadasha.strip().lower() if running_mahadasha else None
        running_bk = running_bhukti.strip().lower() if running_bhukti else None

        # 1. Moon Nakshatra Sacred Profile
        nak_profile = SannuRitualsEngine.get_nakshatra_ritual_by_name(moon_nak_clean)
        if not nak_profile and NAKSHATRA_RITUALS_ENCYCLOPEDIA:
            nak_profile = NAKSHATRA_RITUALS_ENCYCLOPEDIA[0]

        # 2. Nakshatra Doshas Evaluation
        detected_doshas: List[Dict[str, Any]] = []
        nak_name = nak_profile["name"].lower() if nak_profile else ""

        # A. Gandanta Check (Revati-Ashwini, Ashlesha-Magha, Jyeshtha-Mula)
        gandanta_junctions = {
            "revati": {"type": "Revati-Ashwini", "zone": "Pisces-Aries Knot", "water_star": "Revati", "fire_star": "Ashwini", "deity": "Ashwini Kumaras & Vishnu"},
            "ashwini": {"type": "Revati-Ashwini", "zone": "Pisces-Aries Knot", "water_star": "Revati", "fire_star": "Ashwini", "deity": "Ashwini Kumaras & Vishnu"},
            "ashlesha": {"type": "Ashlesha-Magha", "zone": "Cancer-Leo Knot", "water_star": "Ashlesha", "fire_star": "Magha", "deity": "Nagas & Pitris"},
            "magha": {"type": "Ashlesha-Magha", "zone": "Cancer-Leo Knot", "water_star": "Ashlesha", "fire_star": "Magha", "deity": "Nagas & Pitris"},
            "jyeshtha": {"type": "Jyeshtha-Mula", "zone": "Scorpio-Sagittarius Knot", "water_star": "Jyeshtha", "fire_star": "Mula", "deity": "Lord Indra, Nirriti & Kali"},
            "mula": {"type": "Jyeshtha-Mula", "zone": "Scorpio-Sagittarius Knot", "water_star": "Jyeshtha", "fire_star": "Mula", "deity": "Lord Indra, Nirriti & Kali"},
        }
        if nak_name in gandanta_junctions:
            j_info = gandanta_junctions[nak_name]
            detected_doshas.append({
                "dosha_type": "gandanta_dosha",
                "severity": "high",
                "title_en": f"Gandanta Dosha ({j_info['type']} Junction)",
                "title_ta": f"கண்டாந்த தோஷம் ({j_info['zone']})",
                "description_en": (
                    f"Moon is placed in {nak_profile['name']}, located at the delicate {j_info['zone']} karmic knot. "
                    "This threshold marks the death and spiritual rebirth of past emotional karma colliding with future fire. "
                    "May manifest as childhood vulnerabilities, identity crises, and cyclical restarts in life."
                ),
                "description_ta": (
                    f"சந்திரன் {nak_profile['name']} நட்சத்திரத்தில் கண்டாந்த சந்திப்பில் அமர்ந்துள்ளார். "
                    "இது நீர் மற்றும் நெருப்பு தத்துவங்களின் சந்திப்பு முடிச்சாகும்; பூர்வ கர்ம வினைகள் கரைந்து புதிய ஆன்மீகப் பிறப்பு எடுக்கும் புண்ணிய நிலை."
                ),
                "shanti_procedure_en": f"Perform Gandanta Shanti. Worship {j_info['deity']}. Offer white flowers, milk, and perform Nakshatra Beeja Japa.",
                "shanti_procedure_ta": f"கண்டாந்த சாந்தி ஹோமம் செய்தல், {j_info['deity']} வழிபாடு மற்றும் பீஜ மந்திர ஜபம் செய்தல் நலம் தரும்.",
            })

        # B. Abhukta Mula Check
        if nak_name == "mula":
            detected_doshas.append({
                "dosha_type": "abhukta_mula_dosha",
                "severity": "critical",
                "title_en": "Abhukta Mula Dosha (The Untouched Karmic Fire of Nirriti)",
                "title_ta": "அபுக்த மூல தோஷம் (நிர்ருதி தேவியின் உக்கிர கர்ம அலை)",
                "description_en": (
                    "Birth in Mula Nakshatra carries the direct impact of Goddess Nirriti (Dissolution). "
                    "Governs heavy ancestral debts, root-level transformation, and testing of family fortunes."
                ),
                "description_ta": (
                    "மூல நட்சத்திர ஜனனம் நிர்ருதி தேவியின் ஆதிக்கத்திற்கு உட்பட்டது. பரம்பரை கர்ம வினைகள் மற்றும் வேர்நிலை மாற்றங்களைக் குறிக்கும்."
                ),
                "shanti_procedure_en": (
                    "Perform formal Mula Shanti Homa on the 27th day when Moon transits Mula. "
                    "Chant 'Om Nirrittaye Namah' with a black sesame oil lamp under a Neem tree. Feed 7 women and 1 cow on Saturday."
                ),
                "shanti_procedure_ta": (
                    "27-ஆம் நாள் மூல சாந்தி செய்தல், வேப்பமரத்தடியில் நல்லெண்ணெய் தீபமேற்றி 'ஓம் நிர்ருதயே நமஹ' ஜபித்தல் மற்றும் பசுவிற்கு உணவளித்தல்."
                ),
            })

        # C. Vishaghati Nakshatra Check
        if nak_name in ("ashlesha", "mula", "ardra", "jyeshtha", "purvabhadra"):
            detected_doshas.append({
                "dosha_type": "vishaghati_nakshatra",
                "severity": "moderate",
                "title_en": f"Vishaghati Karmic Channel ({nak_profile['name']})",
                "title_ta": f"விஷகடி நட்சத்திர அமைப்பு ({nak_profile['name']})",
                "description_en": (
                    f"{nak_profile['name']} is classically classified as a Vishaghati star, "
                    "where lunar nadis are sensitive to ancestral distress, psychic turbulence, and hidden karmic vulnerabilities."
                ),
                "description_ta": (
                    f"{nak_profile['name']} விஷகடி நட்சத்திரமாகும். மறைமுக கர்ம வினைகள் மற்றும் மன உளைச்சல்களைத் தணிக்க சாந்தி வழிபாடு அவசியம்."
                ),
                "shanti_procedure_en": "Perform Naga Bali or Kala Sarpa Shanti; chant Nakshatra Beeja mantra during Moon's transit through this star.",
                "shanti_procedure_ta": "நாக சாந்தி அல்லது ருத்ர ஜபம் செய்தல் மற்றும் சந்திரன் இந்நட்சத்திரத்தில் சஞ்சரிக்கும் போது விரதமிருந்து வழிபடுதல்.",
            })

        # 3. Threefold Karma Breakdown for the Native
        # Sanchita: deep past-life debilities
        sanchita_markers: List[Dict[str, Any]] = []
        for p in debilitated:
            sanchita_markers.append({
                "graha": p,
                "factor": f"Debilitation of {p.capitalize()}",
                "lesson_en": f"Deep ancestral backlog regarding {p.capitalize()}'s natural karakas awaiting redemption.",
                "lesson_ta": f"{p} கிரக காரகத்துவம் சார்ந்த முற்பிறவி கர்ம வினைகள் நீச அமைப்பால் வெளிப்படுகின்றன.",
            })
        for h_str, p_list in (dusthana_planets or {}).items():
            if int(h_str) in (8, 12):
                for p in p_list:
                    if p not in ("rahu", "ketu"):
                        sanchita_markers.append({
                            "graha": p,
                            "factor": f"{p.capitalize()} in {h_str}th House",
                            "lesson_en": f"Latent karmic debt requiring spiritual surrender (Moksha/Randhra).",
                            "lesson_ta": f"{h_str}-ஆம் மறைவு ஸ்தானத்தில் உள்ள {p} ஆன்மீக சரணாகதியை கோருகிறது.",
                        })

        # Prarabdha: currently active ripe karmas
        prarabdha_markers: List[Dict[str, Any]] = []
        if running_md:
            prarabdha_markers.append({
                "graha": running_md,
                "factor": f"Active Mahadasha of {running_md.capitalize()}",
                "impact_en": "Primary karmic arbiter delivering present-life circumstances with clockwork precision.",
                "impact_ta": "தற்போது கர்ம பலன்களை நேரடியாக வழங்கும் பிரதான திசாநாதன்.",
            })
        if running_bk:
            prarabdha_markers.append({
                "graha": running_bk,
                "factor": f"Active Antardasha of {running_bk.capitalize()}",
                "impact_en": "Sub-period trigger activating specific prarabdha events.",
                "impact_ta": "நடைபெறும் புக்தி நாதன்; உடனடி சம்பவங்களைத் தூண்டும் கர்ம அலை.",
            })
        for p in combust:
            prarabdha_markers.append({
                "graha": p,
                "factor": f"Solar Combustion of {p.capitalize()} (Astangata)",
                "impact_en": f"Inner friction and ego-purification in {p.capitalize()}'s domain requiring solar pacification.",
                "impact_ta": f"{p} சூரியனால் அஸ்தமனம் அடைந்துள்ளதால் தன் முனைப்பைக் கைவிட்டு பணிவை மேற்கொள்ள வேண்டும்.",
            })

        # Kriyamana: Actionable Daily / Weekly Protocol
        kriyamana_protocol: List[Dict[str, Any]] = [
            {
                "practice": "Satya-Sadhana Awareness Journal",
                "cadence": "Daily before sleep",
                "objective_en": "Witness emotional triggers and reactions to prevent accumulating fresh papa (sinful) impressions.",
                "objective_ta": "தினசரி நிகழ்வுகளை விழிப்புணர்வுடன் கவனித்து புதிய கர்ம பதிவுகள் ஏற்படுவதைத் தடுத்தல்.",
            },
            {
                "practice": f"Daily Nakshatra Beeja Japa: {nak_profile.get('sound_mantra_bija') or nak_profile.get('sound_mantra')}",
                "cadence": "Daily at sunrise (108 counts)",
                "objective_en": "Cleanses the 72,000 nadis and aligns the soul with its cosmic archetype.",
                "objective_ta": "72,000 நாடிகளையும் தூய்மைப்படுத்தி உயிர் ஆற்றலை சீரமைக்கும் பிரதான ஜபம்.",
            },
            {
                "practice": "Planetary Day Fasting (Upavasa)",
                "cadence": f"Weekly on running Dasha weekday ({running_md.capitalize() if running_md else 'Monday'})",
                "objective_en": "Frees vital prana from heavy digestion to incinerate latent Prarabdha seeds.",
                "objective_ta": "செரிமான ஆற்றலை ஆன்மீக ஆற்றலாக மாற்றி கர்ம பாரத்தை எளிதாக்கும் விரதம்.",
            },
        ]

        # 4. Psychological & Karmic Diagnostics for Afflicted Planets
        psychological_diagnostics: List[Dict[str, Any]] = []
        all_afflicted = debilitated.union(combust)
        for h_str, p_list in (dusthana_planets or {}).items():
            all_afflicted = all_afflicted.union(set([p.lower() for p in p_list]))

        for p in sorted(list(all_afflicted)):
            if p in PLANETARY_WEAKNESS_ATLAS:
                atlas = PLANETARY_WEAKNESS_ATLAS[p]
                # find which house it occupies if available
                p_house = (planets_dict.get(p) or {}).get("house")
                house_impact = HOUSE_WEAKNESS_MANIFESTATION.get(p_house) if p_house else None

                psychological_diagnostics.append({
                    "graha": p,
                    "title_en": atlas["title_en"],
                    "title_ta": atlas["title_ta"],
                    "karmic_theme": atlas["theme"],
                    "house_occupied": p_house,
                    "house_manifestation": house_impact,
                    "psychological_symptoms": atlas["psychological_symptoms"],
                    "karmic_symptoms": atlas["karmic_symptoms"],
                    "tantric_insight": atlas["tantric_insight"],
                })

        # 5. Propitiation vs. Empowerment Classification for Chart Planets
        propitiation_vs_empowerment_status: List[Dict[str, Any]] = []
        all_chart_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

        for p in all_chart_planets:
            is_yogak = p in yogakarakas
            is_benefic = p in benefics
            is_malefic = p in malefics
            is_deb = p in debilitated
            is_comb = p in combust

            # Decision logic:
            # If afflicted (debilitated, combust, malefic) -> PROPITIATION ONLY
            # If unafflicted Yogakaraka or strong benefic -> EMPOWERMENT ALLOWED
            if is_deb or is_comb or is_malefic:
                action_type = "propitiation_only"
                badge_en = "Propitiation Required (Shanti Karma)"
                badge_ta = "சாந்தி பரிகாரம் மட்டும் (ஆற்றல் பெருக்குதல் கூடாது)"
                justification_en = (
                    f"{p.capitalize()} is under karmic affliction ({'debilitated' if is_deb else ''}{'combust' if is_comb else ''}{'functional malefic' if is_malefic else ''}). "
                    "Per Picatrix & BPHS, NEVER empower an afflicted planet with gemstones or amplifier rituals; pacify it first!"
                )
                justification_ta = (
                    f"{p} பாதிப்படைந்துள்ளதால் ரத்தினங்கள் அணிந்து ஆற்றலை அதிகரிக்கக் கூடாது; "
                    "சாந்தி மந்திரங்கள் மற்றும் தானங்கள் மூலமே தணிக்க வேண்டும்."
                )
                recommended_mantra = PROPITIATION_VS_EMPOWERMENT["shanti_karmas"]["beeja_mantras"].get(p)
                recommended_donation = PROPITIATION_VS_EMPOWERMENT["shanti_karmas"]["charity_items"].get(p)
            else:
                action_type = "empowerment_allowed"
                badge_en = "Empowerment Eligible (Shakti Karma)"
                badge_ta = "ஆற்றல் பெருக்கலாம் (சக்தி கர்மா)"
                justification_en = (
                    f"{p.capitalize()} is an auspicious, unafflicted {'Yogakaraka' if is_yogak else 'Lagna Benefic'}. "
                    "Empowering it with yantras, consecrated gemstones, and stotras brings siddhi and status."
                )
                justification_ta = (
                    f"{p} யோககாரக அல்லது சுப கிரகமாக உள்ளதால் யந்திரம் மற்றும் வழிபாடுகள் மூலம் இதன் சுப ஆற்றலை அதிகரிக்கலாம்."
                )
                recommended_mantra = PROPITIATION_VS_EMPOWERMENT["shanti_karmas"]["beeja_mantras"].get(p)
                recommended_donation = None

            gem_rules = PROPITIATION_VS_EMPOWERMENT["empowerment_karmas"]["gemstone_rules_and_cautions"].get(p)

            propitiation_vs_empowerment_status.append({
                "graha": p,
                "action_type": action_type,
                "badge_en": badge_en,
                "badge_ta": badge_ta,
                "justification_en": justification_en,
                "justification_ta": justification_ta,
                "beeja_mantra": recommended_mantra,
                "charity_prescribed": recommended_donation,
                "gemstone_rules": gem_rules,
            })

        return {
            "moon_nakshatra_ritual": nak_profile,
            "detected_nakshatra_doshas": detected_doshas,
            "threefold_karma_blueprint": {
                "sanchita": {
                    "summary_en": "Dormant reservoir of cumulative soul debts.",
                    "summary_ta": "முற்பிறவி கர்ம வினைகளின் சேமிப்புக் கிடங்கு.",
                    "markers": sanchita_markers,
                    "dissolution_path": KARMA_ARCHITECTURE["sanchita"]["remedial_strategy_en"],
                },
                "prarabdha": {
                    "summary_en": "The active arrow in flight shaping present challenges.",
                    "summary_ta": "தற்போது வெளிப்பட்டு இயங்கிக் கொண்டிருக்கும் கர்ம அலைகள்.",
                    "markers": prarabdha_markers,
                    "alleviation_path": KARMA_ARCHITECTURE["prarabdha"]["remedial_strategy_en"],
                },
                "kriyamana": {
                    "summary_en": "Daily and weekly conscious choices to avoid new karmic debts.",
                    "summary_ta": "புதிய கர்ம வினைகளைத் தடுக்கும் தினசரி ஆன்மீக நெறிமுறை.",
                    "protocol": kriyamana_protocol,
                },
            },
            "psychological_and_karmic_diagnostics": psychological_diagnostics,
            "propitiation_vs_empowerment_status": propitiation_vs_empowerment_status,
            "sacred_timing_and_routine": {
                "pushya_nakshatra_guidelines": SACRED_TIMING_RULES["pushya_nakshatra"],
                "lunar_tithi_observances": SACRED_TIMING_RULES["lunar_tithis"],
                "eclipse_safeguards": SACRED_TIMING_RULES["eclipses"],
                "active_dasha_hora_tip": (
                    f"Prioritize your spiritual rituals during {running_md.capitalize() if running_md else 'Sun'} Hora on its planetary weekday for 100x karmic resonance."
                ),
            },
        }

