"""Structured, versioned, source-backed rule registry for Medical Astrology.

Classical References:
- Brihat Parashara Hora Shastra (BPHS), Chapter 17 (Bhavaphala Adhyaya: Effects of the 6th House / Rogaphala).
- Brihat Parashara Hora Shastra (BPHS), Chapter 11 (Arishta Bhanga Adhyaya).
- Phaladeepika of Mantreswara, Chapter 14 (Roga Vimarsa: Diseases indicated by Bhavas and Grahas).
- Saravali of Kalyana Varma, Chapters 31 & 32 (Bhava Phala of 6th & 8th houses).
- Jataka Parijata of Vaidyanatha Dikshita, Chapter 6 (Roga and Arishta Phala).
- Krishnamurti Paddhati (KP) Reader IV: Medical Astrology & CSL Significations.

STRICT SAFETY RESTRICTIONS:
All interpretations are traditional astrological observations for research and education.
No clinical diagnoses, onset predictions, or health scores are generated.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

RULE_SET_VERSION = "1.0.0"


@dataclass(frozen=True)
class ClassicalMedicalRuleDefinition:
    id: str
    name: str
    name_tamil: str
    source: str
    chapter_verse: str
    category: str  # "Vedic Birth Chart" | "Vedic House Lord" | "Vedic Conjunction/Aspect" | "Vedic Mitigation" | "KP 6th Cusp Sub-Lord" | "KP Dasha Signification"
    system: str  # "vedic" | "kp"
    required_placements: str
    mandatory_conditions: List[str]
    traditional_interpretation: str
    interpretation_tamil: str
    anatomical_system: str
    modifiers: Optional[str] = None
    conflicting_indications: Optional[str] = None
    remedy_en: Optional[str] = None
    remedy_ta: Optional[str] = None


# Master Verified Registry
MEDICAL_RULES_REGISTRY: Dict[str, ClassicalMedicalRuleDefinition] = {
    # -------------------------------------------------------------------------
    # BPHS CHAPTER 17: SINGLE-PLANET PLACEMENTS IN 6TH HOUSE
    # -------------------------------------------------------------------------
    "bphs_17_1_sun_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_1_sun_6th",
        name="Sun in 6th House (Solar Vitality & Digestive Fire)",
        name_tamil="6-ம் பாவத்தில் சூரியன் (உடற்சூடு மற்றும் ஜீரண பலம்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 1–2",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Sun occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Sun is located in the 6th bhava from Lagna",
            "Evaluate Sun's dignity and aspects",
        ],
        traditional_interpretation=(
            "Traditional texts record that the Sun in the 6th house confers vigorous constitutional resistance "
            "and digestive power (Jatharagni) to subdue ailments. If afflicted by natural malefics, heat-related "
            "or bilious (Pitta) imbalances and eye sensitivities are traditionally noted."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் சூரியன் அமைந்திருப்பது நோய்களை எதிர்க்கும் வலுவான உடலமைப்பையும், செரிமான ஆற்றலையும் "
            "(ஜடராக்னி) குறிக்கும். அசுப கிரக சேர்க்கை அல்லது பார்வை பெற்றால் பித்த உடற்சூடு, கண் தொடர்பான கவனங்கள் தேவைப்படலாம்."
        ),
        anatomical_system="Cardiovascular, Vital Energy, Digestive Fire (Pitta), Eyes",
        modifiers="Benefic aspects from Jupiter enhance vitality; combustion of other planets or debility in Libra tempers stamina.",
        conflicting_indications="Arishta Bhanga from strong benefics in Kendras fully overrides general afflictions.",
    ),
    "bphs_17_3_moon_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_3_moon_6th",
        name="Moon in 6th House (Phlegmatic & Digestive Sensitivity)",
        name_tamil="6-ம் பாவத்தில் சந்திரன் (கப தோஷம் மற்றும் செரிமான மென்மை)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 3–4",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Moon occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Moon is located in the 6th bhava from Lagna",
            "Consider Paksha Bala (waxing vs waning)",
        ],
        traditional_interpretation=(
            "The Moon in the 6th house is traditionally associated with sensitive digestion, fluid balance "
            "variations, and phlegmatic (Kapha) tendencies. A waxing, strong Moon mitigates distress, while a "
            "waning Moon afflicted by Rahu or Saturn suggests emotional stress affecting physical well-being."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் சந்திரன் அமைந்திருப்பது செரிமான உணர்திறன், நீர்ச்சத்து மாறுபாடுகள் மற்றும் கப தோஷப் "
            "போக்குகளைக் குறிப்பதாக பாரம்பரிய நூல்கள் கூறுகின்றன. வளர்பிறைச் சந்திரன் சுப பலன் தரும்; தேய்பிறைச் சந்திரன் "
            "அல்லது ராகுவின் சேர்க்கை மன அழுத்தம் சார்ந்த உடல் சோர்வை ஏற்படுத்தலாம்."
        ),
        anatomical_system="Bodily Fluids, Stomach, Lungs/Bronchial Mucosa, Mental Equilibrium",
        modifiers="Bright Moon (Shukla Paksha) or aspect of Jupiter protects against bodily weakness.",
        conflicting_indications="Jupiter in 1st, 4th, 7th, or 10th dissolves lunar weaknesses.",
    ),
    "bphs_17_5_mars_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_5_mars_6th",
        name="Mars in 6th House (Immune Defense & Inflammatory Tendencies)",
        name_tamil="6-ம் பாவத்தில் செவ்வாய் (நோய் எதிர்ப்பு ஆற்றல் மற்றும் உஷ்ணத் தன்மை)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 5–6",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Mars occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Mars is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Mars placed in an Upachaya house (6th) is celebrated in classical texts for creating formidable bodily "
            "immunity and the power to triumph over illnesses. When heavily afflicted or conjoined with Rahu/Saturn, "
            "acute inflammatory conditions, fevers, or surgical marks are traditionally cited."
        ),
        interpretation_tamil=(
            "உபசெய ஸ்தானமான 6-ம் பாவத்தில் செவ்வாய் இருப்பது அபாரமான நோய் எதிர்ப்பு ஆற்றலையும், எதிர்ப்புகளை முறியடிக்கும் "
            "தைரியத்தையும் அளிக்கும் என சாஸ்திரங்கள் பகர்கின்றன. ராகு அல்லது சனியுடன் கூடும்போது உஷ்ணக் காய்ச்சல்கள் அல்லது காயங்கள் ஏற்பட வாய்ப்புள்ளது."
        ),
        anatomical_system="Muscular System, Blood/Bone Marrow, Inflammatory Response, Head",
        modifiers="Exaltation in Capricorn produces supreme resilience; debility in Cancer increases vulnerability to cuts or blood tension.",
        conflicting_indications="Aspect of benefic Venus or Jupiter tempers excess Pitta.",
    ),
    "bphs_17_7_mercury_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_7_mercury_6th",
        name="Mercury in 6th House (Nervous & Respiratory Sensitivity)",
        name_tamil="6-ம் பாவத்தில் புதன் (நரம்பு மற்றும் சுவாச உணர்திறன்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 7–8",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Mercury occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Mercury is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Classical astrology associates Mercury in the 6th house with intellectual vigor alongside sensitive "
            "nervous, skin, and upper respiratory responses. Mental overexertion can manifest as fatigue or digestive "
            "sensitivity unless Mercury is fortified in Gemini or Virgo."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் புதன் அமர்வது அறிவுக் கூர்மையை அளித்தாலும், நரம்பு மண்டலம், தோல் மற்றும் சுவாசப் பாதையில் "
            "உணர்திறனை அளிக்கலாம். அதிக மன உழைப்பு உடற்சோர்வை ஏற்படுத்தக்கூடும்; கன்னி அல்லது மிதுனத்தில் ஆட்சி பெற்றால் தோஷம் நீங்கும்."
        ),
        anatomical_system="Nervous System, Skin, Bronchial/Respiratory Passages, Intellect",
        modifiers="Own sign Virgo or Gemini converts placement into analytical strength; combustion increases mental restlessness.",
        conflicting_indications="Benefic conjunction with Venus or aspect of Jupiter protects nervous stamina.",
    ),
    "bphs_17_9_jupiter_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_9_jupiter_6th",
        name="Jupiter in 6th House (Metabolic Balance & Hepatic Rulership)",
        name_tamil="6-ம் பாவத்தில் குரு (வளர்சிதை மாற்றம் மற்றும் கல்லீரல் ஆதிக்கம்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 9–10",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Jupiter occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Jupiter is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Jupiter in the 6th house generally protects the individual through eventual recovery and sound medical "
            "counsel. Classical texts observe a predisposition toward sluggish metabolic processing, hepatic/liver "
            "sensitivity, or adipose tissue accumulation when afflicted."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் குரு அமர்வது சிறந்த மருத்துவ வழிகாட்டுதல் மூலமும், தெய்வீக அருளாலும் விரைவான குணமடைதலைத் தரும். "
            "பாதிக்கப்பட்டிருந்தால் கல்லீரல், கொழுப்புச்சத்து அல்லது வளர்ச்சிதை மாற்றத்தில் சமநிலையின்மை ஏற்படக்கூடும்."
        ),
        anatomical_system="Liver, Pancreas, Arterial Circulation, Fat Tissue (Medas), Ears",
        modifiers="Debility in Capricorn increases dietary sensitivity; aspect on 10th and 2nd supports healing resources.",
        conflicting_indications="Jupiter aspecting 10th, 12th, or 2nd maintains recovery safeguards.",
    ),
    "bphs_17_11_venus_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_11_venus_6th",
        name="Venus in 6th House (Urogenital & Hormonal Tendencies)",
        name_tamil="6-ம் பாவத்தில் சுக்கிரன் (சிறுநீரகம் மற்றும் நாளமில்லா சுரப்பி நிலைகள்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 11–12",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Venus occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Venus is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Venus in the 6th house is traditionally associated with bodily water regulation, kidney function, and "
            "reproductive/endocrine balance. Classical authors advise moderation in diet and sensory indulgence to "
            "avoid urinary or hormonal imbalances."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் சுக்கிரன் இருப்பது நீர் சமநிலை, சிறுநீரகம் மற்றும் இனப்பெருக்க உறுப்புகளின் செயல்பாட்டைக் குறிக்கும். "
            "முறையற்ற உணவு அல்லது அதீத உடல் உழைப்பால் ஹார்மோன் சமநிலையின்மை ஏற்பட வாய்ப்புள்ளதாக சாஸ்திரங்கள் சுட்டிக்காட்டுகின்றன."
        ),
        anatomical_system="Kidneys, Pelvic Region, Reproductive System, Hormonal Balance, Throat",
        modifiers="Exaltation in Pisces or aspect of Jupiter shields the excretory-reproductive axis.",
        conflicting_indications="Strong Lagna lord in Kendra neutralizes constitutional debility.",
    ),
    "bphs_17_13_saturn_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_13_saturn_6th",
        name="Saturn in 6th House (Constitutional Endurance & Vata Tendencies)",
        name_tamil="6-ம் பாவத்தில் சனி (நீண்டகால சகிப்புத்தன்மை மற்றும் வாத ஆதிக்கம்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verses 13–14",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Saturn occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Saturn is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Saturn in the 6th house is an auspicious Upachaya placement conferring tenacity, pain tolerance, and "
            "the capacity to wear down lingering ailments. If afflicted, chronic joints, dental, or wind (Vata) "
            "sluggishness may require routine physical maintenance."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் சனி அமைந்திருப்பது நோய்களை வெல்லும் அபார சகிப்புத்தன்மையையும் நீண்ட ஆயுளையும் தரும் உன்னத உபசெய நிலையாகும். "
            "பாதிக்கப்பட்டிருந்தால் மூட்டு வலி, வாத தோஷம் அல்லது தசைப் பிடிப்பு போன்ற நீண்டகால மெதுவான உபாதைகள் ஏற்படலாம்."
        ),
        anatomical_system="Skeletal Structure, Knees, Joints, Teeth, Chronic Nervous Wind (Vata)",
        modifiers="Exalted in Libra grants immense physical stamina; debilitated in Aries requires attention to bone density.",
        conflicting_indications="Benefic aspect from Jupiter dissolves chronic Vata fatigue.",
    ),
    "bphs_17_15_rahu_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_15_rahu_6th",
        name="Rahu in 6th House (Robust Immunity Overcoming Obscure Ailments)",
        name_tamil="6-ம் பாவத்தில் ராகு (மறைமுக நோய்களை வெல்லும் எதிர்ப்பு சக்தி)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 15",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Rahu occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Rahu is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Rahu in the 6th house is lauded in classical Parashari astrology as a destroyer of enemies and ailments "
            "(Ari-Hanta). It endows an unconventional, resilient immune system, though subtle allergic sensitivities or "
            "difficult-to-categorize bodily reactions are occasionally noted."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் ராகு அமர்வது சத்ருக்களையும் நோய்களையும் வெல்லும் 'அரிஹந்தா' யோகமாகும். இது அபார எதிர்ப்பு சக்தியைத் தரும்; "
            "அதேவேளையில் ஒவ்வாமை (அலர்ஜி) அல்லது கண்டறிய கடினமான உடல் உபாதைகளில் விழிப்புணர்வு அவசியம்."
        ),
        anatomical_system="Immune Matrix, Subtle Toxins, Allergic Tendencies, Undiagnosed Strains",
        modifiers="Dispositor well-placed in Kendra/Trikona strengthens diagnostic clarity.",
        conflicting_indications="Jupiter aspect clears toxic tendencies and promotes swift recovery.",
    ),
    "bphs_17_16_ketu_6th": ClassicalMedicalRuleDefinition(
        id="bphs_17_16_ketu_6th",
        name="Ketu in 6th House (Resilience Against Microbial & Acute Strains)",
        name_tamil="6-ம் பாவத்தில் கேது (நுண்ணுயிர் பாதிப்புகளை முறியடிக்கும் எதிர்ப்பு பலம்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 16",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Ketu occupies the 6th house from natal Lagna",
        mandatory_conditions=[
            "Ketu is located in the 6th bhava from Lagna",
        ],
        traditional_interpretation=(
            "Ketu in the 6th house confers strong instinctual defense mechanisms against pathogenic strains and acute "
            "fevers. Classical authorities note a tendency toward sudden inflammatory flare-ups, localized insect bites, "
            "or skin irritations that typically resolve quickly."
        ),
        interpretation_tamil=(
            "6-ம் பாவத்தில் கேது இருப்பது வைரஸ், பாக்டீரியா போன்ற நுண்ணுயிர் தொற்றுகளை எதிர்க்கும் இயல்பான நோய் எதிர்ப்பு சக்தியைத் தரும். "
            "திடீர் உஷ்ணக் கொப்புளங்கள் அல்லது தோல் எரிச்சல் தோன்றி விரைவில் மறையும் தன்மையைக் குறிக்கும்."
        ),
        anatomical_system="Immune Defense, Microbial Resistance, Fevers, Wounds/Irritations",
        modifiers="Benefic dispositor stabilizes recovery speed.",
        conflicting_indications="Benefic aspects on 6th prevent inflammatory persistence.",
    ),

    # -------------------------------------------------------------------------
    # BPHS CHAPTER 17: HOUSE LORDS (LAGNA, 6TH, 8TH, 12TH)
    # -------------------------------------------------------------------------
    "bphs_17_17_lord6_in_1": ClassicalMedicalRuleDefinition(
        id="bphs_17_17_lord6_in_1",
        name="6th Lord in Lagna (Constitution Closely Linked to Immunity)",
        name_tamil="லக்னத்தில் 6-ம் அதிபதி (நோய் எதிர்ப்பு மற்றும் உடலமைப்பு இணைப்பு)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 17",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Lord of 6th house occupies the 1st house (Lagna)",
        mandatory_conditions=[
            "6th lord is placed in house 1",
        ],
        traditional_interpretation=(
            "When the 6th lord resides in the 1st house, the physical body is intimately engaged with building and "
            "maintaining immune defense. Childhood fevers or physical marks from activity are common in traditional "
            "texts; robust vitality emerges as adulthood progresses, provided the Lagna lord is well-dignified."
        ),
        interpretation_tamil=(
            "6-ம் அதிபதி லக்னத்தில் இருப்பது, உடல் அமைப்பு நோய் எதிர்ப்பு ஆற்றலை சுயமாகக் கட்டமைப்பதைக் குறிக்கும். "
            "இளமையில் சிறு காயங்கள் அல்லது காய்ச்சல்கள் வரலாம்; லக்னாதிபதி பலம் பெற்றிருந்தால் வயது கூடக்கூட திடகாத்திரமான ஆரோக்கியம் கிட்டும்."
        ),
        anatomical_system="Head, Physical Constitution, General Immunity",
        modifiers="If 6th lord is also Lagna lord (Aries/Scorpio or Taurus/Libra Lagna), the affliction is substantially mitigated.",
        conflicting_indications="Benefics in Kendras protect physical stamina and longevity.",
    ),
    "bphs_17_22_lord6_in_6": ClassicalMedicalRuleDefinition(
        id="bphs_17_22_lord6_in_6",
        name="6th Lord in 6th House (Harsha Yoga / Immunity Swa-kshetra)",
        name_tamil="6-ம் அதிபதி 6-ல் ஆட்சி (ஹர்ஷ யோகம் / நோய் அழிக்கும் பலம்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 22",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Lord of 6th house occupies the 6th house in own sign",
        mandatory_conditions=[
            "6th lord is placed in house 6",
            "Planet is in its own sign",
        ],
        traditional_interpretation=(
            "6th lord in the 6th house forms the auspicious Harsha Yoga (a Vipareeta formation). Parashara states "
            "that the native possesses a strong constitution, sound digestive stamina, and natural immunity capable "
            "of dispelling bodily ailments swiftly."
        ),
        interpretation_tamil=(
            "6-ம் அதிபதி தன் சொந்த வீட்டில் 6-ல் ஆட்சி பெறுவது 'ஹர்ஷ யோகம்' எனப்படும். இது நோய்களை விரைவாக அழிக்கும் "
            "இயற்கையான உடற்பலத்தையும், நோய் எதிர்ப்பு சக்தியையும், நீண்ட ஆரோக்கியத்தையும் அளிக்கும் என பராசரர் குறிப்பிடுகிறார்."
        ),
        anatomical_system="Digestive Core, Intestinal Tract, Endogenous Immune Vitality",
        modifiers="Free from malefic conjunction yields pristine constitutional stamina.",
        conflicting_indications="None; this is a classical protective formation.",
    ),
    "bphs_17_24_lord6_in_8": ClassicalMedicalRuleDefinition(
        id="bphs_17_24_lord6_in_8",
        name="6th Lord in 8th House (Vipareeta Dynamics & Deep Recuperation)",
        name_tamil="8-ம் பாவத்தில் 6-ம் அதிபதி (விபரீத தாத்பரியம் மற்றும் ஆழமான மீட்சி)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 24",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Lord of 6th house occupies the 8th house",
        mandatory_conditions=[
            "6th lord is located in house 8",
        ],
        traditional_interpretation=(
            "When the 6th lord occupies the 8th house, two Dusthana lords interact, creating Vipareeta (Sarala-Harsha) "
            "dynamics. While sudden bodily changes or acute-to-chronic transitions are traditionally monitored, "
            "unafflicted placements indicate surprising resilience and recovery from profound physical challenges."
        ),
        interpretation_tamil=(
            "6-ம் அதிபதி 8-ல் மறைவது விபரீத ராஜயோக அமைப்பாகும். கடுமையான உடல் சவால்களிலிருந்தும் வியக்கத்தக்க வகையில் "
            "மீண்டு வரும் ஆற்றலை இது தரும்; எனினும் மறைமுக உடல் உபாதைகளில் முறையான மருத்துவப் பராமரிப்பு அவசியம்."
        ),
        anatomical_system="Excretory System, Pelvic Floor, Longevity Reserves, Cellular Recovery",
        modifiers="Benefic aspects from Jupiter convert potential stress into strong regenerative vitality.",
        conflicting_indications="Arishta Bhanga formations neutralize chronic vulnerabilities.",
    ),
    "bphs_17_28_lord6_in_12": ClassicalMedicalRuleDefinition(
        id="bphs_17_28_lord6_in_12",
        name="6th Lord in 12th House (Recuperative Rest & Medical Expenditure)",
        name_tamil="12-ம் பாவத்தில் 6-ம் அதிபதி (மருத்துவச் செலவு மற்றும் ஓய்வு)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 28",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Lord of 6th house occupies the 12th house",
        mandatory_conditions=[
            "6th lord is located in house 12",
        ],
        traditional_interpretation=(
            "The 6th lord placed in the 12th house (Vipareeta Vimala interplay) indicates expenditure directed toward "
            "health and wellness, restful sleep cycles, or hospitalization during major transits. Traditional texts "
            "observe that diseases contracted away from the birthplace resolve through structured bed rest."
        ),
        interpretation_tamil=(
            "6-ம் அதிபதி 12-ல் இருப்பது விமல யோக தொடர்பைக் குறிக்கும். உடல் ஆரோக்கியத்திற்கான செலவுகள், ஆழ்ந்த தூக்கத்தின் "
            "அவசியம் மற்றும் முறையான ஓய்வு மூலம் உடல் நலம் பெறுவதை பாரம்பரிய நூல்கள் விவரிக்கின்றன."
        ),
        anatomical_system="Sleep Architecture, Feet/Lymphatics, Left Eye, Hospitalization/Confinement",
        modifiers="Benefic influence on 12th ensures swift discharge from care facilities.",
        conflicting_indications="Jupiter in Kendra shields against prolonged institutional confinement.",
    ),
    "bphs_17_29_lagna_lord_in_6": ClassicalMedicalRuleDefinition(
        id="bphs_17_29_lagna_lord_in_6",
        name="Lagna Lord in 6th House (Constitutional Fortification Required)",
        name_tamil="6-ம் பாவத்தில் லக்னாதிபதி (உடற்பராமரிப்பு மற்றும் தற்காப்புத் தேவை)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 17, Verse 29",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Lord of 1st house occupies the 6th house",
        mandatory_conditions=[
            "Lagna lord is located in house 6",
        ],
        traditional_interpretation=(
            "When the Lagna lord enters the 6th house, the physical constitution is continually tested by daily "
            "strains, requiring disciplined routines, exercise, and dietary care. If exalted or aspected by benefics, "
            "the native develops an unshakeable health discipline that conquers physical weaknesses."
        ),
        interpretation_tamil=(
            "லக்னாதிபதி 6-ல் அமர்வது உடலை ஆரோக்கியப் பழக்கவழக்கங்கள், உடற்பயிற்சி மற்றும் உணவுக்கட்டுப்பாடு மூலம் பேணிப் பாதுகாக்க "
            "வேண்டியதன் அவசியத்தை உணர்த்துகிறது. சுப பார்வை பெற்றால் எத்தகைய நோயையும் வெல்லும் ஒழுக்கமான வாழ்வு அமையும்."
        ),
        anatomical_system="Overall Vitality, Digestive Integrity, Musculoskeletal Tone",
        modifiers="Exaltation or benefic aspects (Jupiter/Venus) completely transform this into athletic discipline.",
        conflicting_indications="Strong benefics in 1st, 4th, 7th, 10th cancel physical fragility.",
    ),

    # -------------------------------------------------------------------------
    # SARAVALI & PHALADEEPIKA: CONJUNCTIONS, ASPECTS & MULTI-PLANET
    # -------------------------------------------------------------------------
    "saravali_sun_saturn": ClassicalMedicalRuleDefinition(
        id="saravali_sun_saturn",
        name="Sun–Saturn Mutual Aspect or Conjunction (Solar–Vata Tension)",
        name_tamil="சூரியன்–சனி சேர்க்கை அல்லது சமசப்தமப் பார்வை (உஷ்ண–வாத முரண்பாடு)",
        source="Saravali & Phaladeepika",
        chapter_verse="Saravali Ch. 31, v. 8; Phaladeepika Ch. 14, v. 3",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun and Saturn in conjunction (same house) or in mutual aspect (7th from each other)",
        mandatory_conditions=[
            "Sun and Saturn are conjoined or mutually aspecting",
        ],
        traditional_interpretation=(
            "The mutual interaction of fire (Sun) and cold/dry wind (Saturn) is traditionally noted for tension between "
            "vitality and skeletal-joint stamina. Classical authors recommend balanced posture, bone nutrition, and "
            "eye protection during periods governed by these grahas."
        ),
        interpretation_tamil=(
            "நெருப்புக் கிரகமான சூரியனும், குளிர்ச்சியான வாத கிரகமான சனியும் இணைவது அல்லது பார்ப்பது உஷ்ண-வாத சமநிலையின்மையை "
            "உணர்த்துகிறது. எலும்பு, மூட்டுகள், பார்வை மற்றும் ரத்த அழுத்தத்தில் கவனமும், நிதானமான ஓய்வும் பரிந்துரைக்கப்படுகிறது."
        ),
        anatomical_system="Skeletal Structure, Eye Sight, Blood Pressure, Spinal Column",
        modifiers="Mitigated if Jupiter aspects either planet or if Saturn is in Libra/Capricorn/Aquarius.",
        conflicting_indications="Jupiter aspecting Sun or Saturn dissolves harsh mutual friction.",
    ),
    "saravali_mars_saturn": ClassicalMedicalRuleDefinition(
        id="saravali_mars_saturn",
        name="Mars–Saturn Conjunction or Mutual Aspect (Pitta–Vata Friction)",
        name_tamil="செவ்வாய்–சனி சேர்க்கை அல்லது பார்வை (பித்த–வாத முரண்பாடு)",
        source="Saravali & Phaladeepika",
        chapter_verse="Saravali Ch. 31, v. 12; Phaladeepika Ch. 14, v. 5",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars and Saturn in conjunction or aspecting each other",
        mandatory_conditions=[
            "Mars and Saturn are conjoined or in mutual aspect",
        ],
        traditional_interpretation=(
            "The combination of Mars (heat, blood, muscle) and Saturn (cold, bone, contraction) is classically "
            "associated with physical stress, athletic strains, or surgical vulnerability. Regular bodywork, hydration, "
            "and caution during rapid physical movement are traditionally emphasized."
        ),
        interpretation_tamil=(
            "செவ்வாய் (ரத்தம், தசை, உஷ்ணம்) மற்றும் சனி (எலும்பு, வாதம்) இணைவது தசைப்பிடிப்பு, எலும்பு மூட்டு சோர்வு அல்லது "
            "காயங்கள் ஏற்படும் சாத்தியத்தை பாரம்பரிய சாஸ்திரங்கள் குறிப்பிடுகின்றன. எச்சரிக்கையான உடற்பயிற்சி நன்மை பயக்கும்."
        ),
        anatomical_system="Blood Circulation, Bone Marrow, Muscular Tension, Surgery/Accidents",
        modifiers="Benefic aspect of Jupiter cools the inflammatory friction.",
        conflicting_indications="Jupiter in Kendra neutralizes sudden physical perils.",
    ),
    "phaladeepika_moon_rahu": ClassicalMedicalRuleDefinition(
        id="phaladeepika_moon_rahu",
        name="Moon Afflicted by Rahu/Ketu (Eclipse Axis / Emotional Somatization)",
        name_tamil="சந்திரன் ராகு/கேது சேர்க்கை (கிரகண அச்சு / மன–உடல் உணர்திறன்)",
        source="Phaladeepika",
        chapter_verse="Chapter 14, Verse 8",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjoined with Rahu or Ketu in any house",
        mandatory_conditions=[
            "Moon is in the same sign as Rahu or Ketu",
        ],
        traditional_interpretation=(
            "Affliction of the Moon by nodal grahas is traditionally linked to emotional fluctuations somaticizing "
            "as digestive disturbance, allergic responses, or sleep irregularities. Calming routines, hydration, and "
            "grounded environments are traditionally advised to protect vitality."
        ),
        interpretation_tamil=(
            "சந்திரன் ராகு அல்லது கேதுவுடன் இணைவது மன அழுத்தத்தால் உடல் செரிமானம், ஒவ்வாமை அல்லது தூக்கமின்மை ஏற்படுவதை "
            "விளக்குகிறது. மன அமைதியைத் தரும் தியானம் மற்றும் சீரான உணவுப் பழக்கம் ஆரோக்கியத்தைப் பாதுகாக்கும்."
        ),
        anatomical_system="Nervous-Emotional Axis, Lymphatic Fluids, Sleep Quality, Digestion",
        modifiers="Jupiter aspecting the Moon stabilizes emotional-bodily harmony.",
        conflicting_indications="Strong Jupiter in Kendra or Trikona cancels psychological psychosomatic distress.",
    ),
    "bphs_three_malefics_dusthana": ClassicalMedicalRuleDefinition(
        id="bphs_three_malefics_dusthana",
        name="Sun, Mars, and Saturn in Dusthana Houses (Three-Planet Malefic Matrix)",
        name_tamil="மறைவு ஸ்தானங்களில் சூரியன், செவ்வாய், சனி (மும்மல அசுப அமைப்பு)",
        source="Phaladeepika & Saravali",
        chapter_verse="Phaladeepika Ch. 14, v. 15; Saravali Ch. 31, v. 18",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun, Mars, and Saturn all occupy 6th, 8th, or 12th houses",
        mandatory_conditions=[
            "Sun in house 6, 8, or 12",
            "Mars in house 6, 8, or 12",
            "Saturn in house 6, 8, or 12",
        ],
        traditional_interpretation=(
            "When the primary natural malefics (Sun, Mars, Saturn) concentrate in Dusthana houses, classical texts "
            "note potential constitutional fatigue and slow recuperation from acute stress. Consistent medical checkups "
            "and protective lifestyle choices are strongly emphasized in traditional literature."
        ),
        interpretation_tamil=(
            "சூரியன், செவ்வாய், சனி ஆகிய மூன்று அசுப கிரகங்களும் 6, 8, 12 ஆகிய மறைவு வீடுகளில் அமைந்தால் உடல் பலவீனங்கள் "
            "மற்றும் நீண்டகால சோர்வு ஏற்பட வாய்ப்புள்ளதாக நூல்கள் எச்சரிக்கின்றன. முறையான மருத்துவ வழிகாட்டுதல் பாதுகாப்பு தரும்."
        ),
        anatomical_system="Endurance, Chronic Inflammatory Response, Longevity Reserves",
        modifiers="Jupiter or Venus in Kendra acts as a supreme protective shield (Arishta Bhanga).",
        conflicting_indications="Benefics in Kendras completely dissolve the life-threatening impact.",
    ),

    # -------------------------------------------------------------------------
    # VEDIC MITIGATIONS / ARISHTA BHANGA
    # -------------------------------------------------------------------------
    "arishta_bhanga_jupiter_aspect": ClassicalMedicalRuleDefinition(
        id="arishta_bhanga_jupiter_aspect",
        name="Jupiter Aspecting Lagna or 6th House (Arishta Bhanga Shield)",
        name_tamil="லக்னம் அல்லது 6-ம் பாவத்திற்கு குரு பார்வை (அரிஷ்ட பங்க பாதுகாப்பு)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 11, Verse 1; Phaladeepika Ch. 13, v. 9",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Jupiter casts 5th, 7th, or 9th aspect on House 1 or House 6",
        mandatory_conditions=[
            "Jupiter is not combust",
            "Jupiter casts aspect on House 1 or House 6",
        ],
        traditional_interpretation=(
            "Parashara declares: 'Even as a lion rouses fear among thousands of deer, uncombust Jupiter aspecting "
            "the Ascendant or 6th house dissolves myriad bodily afflictions.' This configuration grants powerful "
            "recuperative resilience, timely diagnosis, and effective therapies."
        ),
        interpretation_tamil=(
            "சிங்கத்தைக் கண்டு மான்கள் அஞ்சுவது போல, லக்னத்தையோ 6-ம் வீட்டையோ பார்க்கும் அஸ்தங்கமாகாத குருவின் பார்வை "
            "ஆயிரக்கணக்கான நோய்களையும் அரிஷ்டங்களையும் அழித்துவிடும் என பராசரர் அருள்கிறார். இது அற்புதமான குணமடையும் சக்தியை அளிக்கும்."
        ),
        anatomical_system="Constitutional Immunity, Cellular Regeneration, Healing Receptivity",
        modifiers="Jupiter in own sign (Sagittarius/Pisces) or exalted (Cancer) amplifies protective power exponentially.",
        conflicting_indications="None; this is the primary classical counter-measure.",
    ),
    "arishta_bhanga_benefics_kendras": ClassicalMedicalRuleDefinition(
        id="arishta_bhanga_benefics_kendras",
        name="Natural Benefics in Kendras (Quadrants Sustaining Vital Longevity)",
        name_tamil="கேந்திரங்களில் சுப கிரகங்கள் (நீண்ட ஆயுள் மற்றும் ஆரோக்கிய அரண்)",
        source="Brihat Parashara Hora Shastra",
        chapter_verse="Chapter 11, Verse 2",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Jupiter, Venus, or Mercury occupy houses 1, 4, 7, or 10",
        mandatory_conditions=[
            "At least one natural benefic in a Kendra house",
            "Planet is free from severe affliction",
        ],
        traditional_interpretation=(
            "Natural benefics in quadrant houses (1, 4, 7, 10) form a classical citadel around constitutional vitality. "
            "Even when 6th or 8th house combinations indicate periodic health disturbances, quadrant benefics guarantee "
            "longevity, resilient organ reserves, and swift recuperation."
        ),
        interpretation_tamil=(
            "1, 4, 7, 10 ஆகிய கேந்திர ஸ்தானங்களில் குரு, சுக்கிரன் அல்லது புதன் போன்ற சுப கிரகங்கள் அமர்வது உடல் ஆரோக்கியத்திற்கு "
            "இரும்புக் கோட்டை போன்ற பாதுகாப்பைத் தரும். நோய்கள் வந்தாலும் எளிதில் குணமாகும் வரப்பிரசாதத்தை இது அளிக்கும்."
        ),
        anatomical_system="Vital Core Reserve, Long-term Constitutional Longevity",
        modifiers="Multiple benefics in Kendras eliminate pediatric and adult arishta doshas.",
        conflicting_indications="None; primary life-preservation rule.",
    ),

    # -------------------------------------------------------------------------
    # KRISHNAMURTI PADDHATI (KP) MEDICAL ASTROLOGY RULES (KP READER IV)
    # -------------------------------------------------------------------------
    "kp_rule_6csl_signifies_6": ClassicalMedicalRuleDefinition(
        id="kp_rule_6csl_signifies_6",
        name="KP Rule: 6th Cusp Sub-Lord Signifies House 6 (Acute Illness Indication)",
        name_tamil="கே.பி. விதி: 6-ம் உப அதிபதி 6-ம் பாவத்தைக் குறித்தல் (நோய் நிலை)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Disease and CSL'",
        category="KP 6th Cusp Sub-Lord",
        system="kp",
        required_placements="Sub-Lord of 6th cusp is a significator of House 6 (Levels A, B, C, or D)",
        mandatory_conditions=[
            "6th CSL or its star lord signifies house 6",
        ],
        traditional_interpretation=(
            "In KP Krishnamurti Paddhati, the 6th Cuspal Sub-Lord is the primary governor of disease. When the 6th CSL "
            "signifies house 6, the body experiences acute physical symptoms or conditions requiring medical attention "
            "during periods connected to this planet."
        ),
        interpretation_tamil=(
            "கே.பி. ஜோதிடத்தில் 6-ம் பாவத்தின் உப அதிபதி (CSL) நோயின் முதன்மை காரகர் ஆவார். இவர் 6-ம் வீட்டைத் தொடர்பு கொண்டால், "
            "அவரது தசா புத்தி காலங்களில் சிகிச்சை தேவைப்படும் உடல் உபாதைகள் ஏற்பட பாரம்பரிய விதி கூறுகிறது."
        ),
        anatomical_system="Governed by the 6th CSL planet and its Star-Lord",
        modifiers="If 6th CSL simultaneously signifies house 11, the ailment is mild and rapidly cured.",
        conflicting_indications="Signification of houses 1, 5, 11 negates chronic disease formation.",
    ),
    "kp_rule_6csl_signifies_8": ClassicalMedicalRuleDefinition(
        id="kp_rule_6csl_signifies_8",
        name="KP Rule: 6th Cusp Sub-Lord Signifies House 8 (Chronic Distress & Surgical Factor)",
        name_tamil="கே.பி. விதி: 6-ம் உப அதிபதி 8-ம் பாவத்தைக் குறித்தல் (நீண்டகால உபாதை / அறுவை சிகிச்சை)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Accidents and Surgery'",
        category="KP 6th Cusp Sub-Lord",
        system="kp",
        required_placements="Sub-Lord of 6th cusp signifies House 8",
        mandatory_conditions=[
            "6th CSL signifies house 8",
        ],
        traditional_interpretation=(
            "According to KP principles, when the 6th CSL is connected to the 8th house (pain, chronic affliction, surgery), "
            "physical challenges tend to be intense or prolonged. If Mars is also involved, surgical intervention or "
            "invasive diagnostics are classically indicated to resolve the condition."
        ),
        interpretation_tamil=(
            "6-ம் உப அதிபதி 8-ம் பாவத்தைக் குறிக்கும் போது, வலிகள், நீண்டகால உடல் சிரமங்கள் அல்லது அறுவை சிகிச்சைக்கான சாத்தியங்கள் "
            "கே.பி. முறையில் குறிப்பிடப்படுகின்றன. செவ்வாய் இணைந்திருந்தால் சிகிச்சை மூலம் நிவாரணம் கிட்டும்."
        ),
        anatomical_system="Chronic Reserves, Excretory/Genital Region, Surgical Points",
        modifiers="Connection to house 5 or 11 ensures successful outcome of any procedure.",
        conflicting_indications="Signification of 5 (12th from 6th) brings cure.",
    ),
    "kp_rule_6csl_signifies_12": ClassicalMedicalRuleDefinition(
        id="kp_rule_6csl_signifies_12",
        name="KP Rule: 6th Cusp Sub-Lord Signifies House 12 (Hospitalization & Bed Rest)",
        name_tamil="கே.பி. விதி: 6-ம் உப அதிபதி 12-ம் பாவத்தைக் குறித்தல் (மருத்துவமனை அனுமதி மற்றும் ஓய்வு)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Hospitalization'",
        category="KP 6th Cusp Sub-Lord",
        system="kp",
        required_placements="Sub-Lord of 6th cusp signifies House 12",
        mandatory_conditions=[
            "6th CSL signifies house 12",
        ],
        traditional_interpretation=(
            "KP astrology holds that the 12th house signifies confinement, clinics, hospital admission, and expenditures "
            "on cure. When the 6th CSL signifies 12, physical ailments traditionally lead to institutional care or "
            "enforced periods of recuperative bed rest."
        ),
        interpretation_tamil=(
            "கே.பி. விதிகளின்படி 6-ம் உப அதிபதி 12-ம் வீட்டைத் தொடர்பு கொண்டால், மருத்துவமனை அனுமதி, சிகிச்சைக்கான செலவுகள் "
            "அல்லது படுக்கை ஓய்வு தேவைப்படும் நிலைகளை பாரம்பரிய சாஸ்திரம் குறிப்பிடுகிறது."
        ),
        anatomical_system="Sleep, Feet, Immune Exhaustion, Institutional Recuperation",
        modifiers="If 11 is also signified (12th from 12th), discharge from care is prompt and complete.",
        conflicting_indications="House 11 signification guarantees successful discharge.",
    ),
    "kp_rule_recovery_1_5_11": ClassicalMedicalRuleDefinition(
        id="kp_rule_recovery_1_5_11",
        name="KP Rule: 6th CSL Signifies 1, 5, or 11 (Cure, Recovery & Disease Negation)",
        name_tamil="கே.பி. விதி: 6-ம் உப அதிபதி 1, 5, 11-ஐக் குறித்தல் (குணமடைதல் மற்றும் நோய் முறிவு)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Cure of Disease'",
        category="KP 6th Cusp Sub-Lord",
        system="kp",
        required_placements="6th CSL signifies houses 1, 5, or 11",
        mandatory_conditions=[
            "6th CSL signifies 1, 5, or 11",
        ],
        traditional_interpretation=(
            "In KP doctrine: House 5 is the 12th from 6th (negation/loss of disease); House 11 is the 12th from 12th "
            "(negation of hospitalization); House 1 is bodily vitality. When the 6th CSL or operating Dasha lords signify "
            "1, 5, or 11, the native experiences complete recovery and therapeutic success."
        ),
        interpretation_tamil=(
            "கே.பி. தத்துவப்படி: 5-ம் வீடு என்பது 6-க்கு 12-ம் வீடாகி நோயை அழிக்கும்; 11-ம் வீடு மருத்துவமனை வாசம் நீங்கி "
            "பூரண குணம் பெறுவதைக் குறிக்கும்; 1-ம் வீடு உடற்பலத்தைக் குறிக்கும். 6-ம் CSL 1, 5, 11-ஐக் குறித்தால் நோய் நீங்கி பூரண நலம் கிட்டும்."
        ),
        anatomical_system="Cellular Restoration, Therapeutic Responsiveness, Vitality",
        modifiers="Strong signification of 11 provides unyielding protection against chronic illness.",
        conflicting_indications="None; this is the primary recovery rule in KP.",
    ),
    "kp_rule_dasa_susceptibility": ClassicalMedicalRuleDefinition(
        id="kp_rule_dasa_susceptibility",
        name="KP Rule: Active Period Lords Signify 6, 8, or 12 (Temporal Attention Window)",
        name_tamil="கே.பி. தசா விதி: தசா-புத்தி நாதர்கள் 6, 8, 12-ஐக் குறித்தல் (கவனத்திற்குரிய காலம்)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Timing of Disease via Dasha'",
        category="KP Dasha Signification",
        system="kp",
        required_placements="Active Mahadasha or Bhukti lord signifies houses 6, 8, or 12",
        mandatory_conditions=[
            "Dasha or Bhukti lord is significator of 6, 8, or 12",
        ],
        traditional_interpretation=(
            "KP temporal timing dictates that an event occurs only when the operating Dasa, Bhukti, and Antara lords "
            "agree. When period rulers signify 6, 8, or 12, traditional texts advise mindful health maintenance "
            "pertaining to the anatomical regions of those specific planetary rulers."
        ),
        interpretation_tamil=(
            "கே.பி. காலக்கணிப்பு விதிகளின்படி, நடப்பு தசா அல்லது புத்தி நாதர்கள் 6, 8, 12 ஆகிய பாவங்களைக் குறிக்கும் காலத்தில், "
            "அக்கிரகங்களுக்குரிய உடல் உறுப்புகளில் விழிப்புணர்வும், போதிய ஓய்வும் தேவைப்படுவதாக பாரம்பரிய நூல்கள் கூறுகின்றன."
        ),
        anatomical_system="Governed by the specific active period lord",
        modifiers="If Antara lord signifies 1, 5, or 11, temporary disturbances resolve quickly.",
        conflicting_indications="Concurrently active 11th house sub-periods bring rapid relief.",
    ),
    "kp_rule_dasa_recovery": ClassicalMedicalRuleDefinition(
        id="kp_rule_dasa_recovery",
        name="KP Rule: Active Period Lords Signify 1, 5, or 11 (Temporal Recovery Window)",
        name_tamil="கே.பி. தசா விதி: தசா-புத்தி நாதர்கள் 1, 5, 11-ஐக் குறித்தல் (குணமடையும் காலம்)",
        source="KP Reader IV: Medical Astrology",
        chapter_verse="KP Reader IV, Section 'Timing of Recovery'",
        category="KP Dasha Signification",
        system="kp",
        required_placements="Active Mahadasha, Bhukti, or Antara lord signifies houses 1, 5, or 11",
        mandatory_conditions=[
            "Period lord signifies houses 1, 5, or 11",
        ],
        traditional_interpretation=(
            "When the operating Dasha, Bhukti, or Antara lord is a strong significator of houses 1, 5, or 11, "
            "the temporal astrological window supports restoration of constitutional vigor, favorable treatment "
            "responses, and discharge from medical care."
        ),
        interpretation_tamil=(
            "நடப்பு தசா, புத்தி அல்லது அந்தர நாதர்கள் 1, 5, 11 ஆகிய பாவங்களைக் குறிக்கும் போது, அது உடல் பலம் திரும்பும், "
            "மருத்துவ சிகிச்சைகள் சிறப்பான பலன் தரும் மற்றும் பூரண குணம் கிட்டும் சுப காலமாகும் என கே.பி. சாஸ்திரம் கூறுகிறது."
        ),
        anatomical_system="System-wide Vitality & Recuperation",
        modifiers="Combination with Jupiter transit over natal 1st or 11th amplifies vitality.",
        conflicting_indications="None; direct indicator of health restoration.",
    ),
}


# Kalapurusha 12-Sign Anatomical Correspondence
KALAPURUSHA_ANATOMY: Dict[int, Dict[str, Any]] = {
    1: {
        "sign_en": "Aries (Mesha)",
        "sign_ta": "மேஷம்",
        "lord": "Mars",
        "system_en": "Cerebral & Cranial Axis",
        "system_ta": "மூளை மற்றும் தலைப் பகுதி",
        "organs_en": "Head, Brain, Cranial Bones, Facial Symmetry, Pineal Gland",
        "organs_ta": "தலை, மூளை, மண்டை ஓடு, முக எலும்புகள்",
        "humor": "Pitta (Fire)",
    },
    2: {
        "sign_en": "Taurus (Vrishabha)",
        "sign_ta": "ரிஷபம்",
        "lord": "Venus",
        "system_en": "Facial & Vocal Axis",
        "system_ta": "முகம், குரல்வளை மற்றும் கழுத்துப் பகுதி",
        "organs_en": "Face, Throat, Vocal Cords, Neck, Teeth, Right Eye, Thyroid",
        "organs_ta": "முகம், தொண்டை, குரல்வளை, பற்கள், வலது கண், தைராய்டு",
        "humor": "Vata/Kapha (Earth)",
    },
    3: {
        "sign_en": "Gemini (Mithuna)",
        "sign_ta": "மிதுனம்",
        "lord": "Mercury",
        "system_en": "Respiratory & Brachial Axis",
        "system_ta": "தோள்பட்டை, கைகள் மற்றும் சுவாசப் பாதை",
        "organs_en": "Shoulders, Arms, Hands, Upper Respiratory Tract, Bronchi",
        "organs_ta": "தோள்கள், கைகள், மேல் சுவாசக் குழாய், மூச்சுக்குழல்",
        "humor": "Vata (Air)",
    },
    4: {
        "sign_en": "Cancer (Karka)",
        "sign_ta": "கடகம்",
        "lord": "Moon",
        "system_en": "Thoracic & Gastric Axis",
        "system_ta": "மார்பு, நுரையீரல் மற்றும் இரைப்பை பகுதி",
        "organs_en": "Chest, Breasts, Lower Lungs, Stomach, Epigastric Cavity",
        "organs_ta": "மார்பு, நுரையீரல் அடிப்பகுதி, இரைப்பை, செரிமானப் பை",
        "humor": "Kapha (Water)",
    },
    5: {
        "sign_en": "Leo (Simha)",
        "sign_ta": "சிம்மம்",
        "lord": "Sun",
        "system_en": "Cardiovascular & Spinal Axis",
        "system_ta": "இதயம், தண்டுவடம் மற்றும் முதுகெலும்பு",
        "organs_en": "Heart, Upper Back, Spine, Aorta, Core Vital Energy",
        "organs_ta": "இதயம், முதுகெலும்பு, தண்டுவடம், முதன்மை ரத்த நாளங்கள்",
        "humor": "Pitta (Fire)",
    },
    6: {
        "sign_en": "Virgo (Kanya)",
        "sign_ta": "கன்னி",
        "lord": "Mercury",
        "system_en": "Digestive & Intestinal Axis",
        "system_ta": "அடிவயிறு, குடல் மற்றும் செரிமான மண்டலம்",
        "organs_en": "Lower Abdomen, Small & Large Intestines, Appendix, Spleen",
        "organs_ta": "அடிவயிறு, சிறுகுடல், பெருங்குடல், குடல்வால்",
        "humor": "Vata/Pitta (Earth)",
    },
    7: {
        "sign_en": "Libra (Tula)",
        "sign_ta": "துலாம்",
        "lord": "Venus",
        "system_en": "Renal & Pelvic Axis",
        "system_ta": "சிறுநீரகம் மற்றும் இடுப்புப் பகுதி",
        "organs_en": "Kidneys, Lumbar Region, Pelvis, Internal Reproductive Vasculature",
        "organs_ta": "சிறுநீரகங்கள், இடுப்பு எலும்புப் பகுதி, கீழ்முதுகு",
        "humor": "Vata (Air)",
    },
    8: {
        "sign_en": "Scorpio (Vrishchika)",
        "sign_ta": "விருச்சிகம்",
        "lord": "Mars",
        "system_en": "Excretory & Reproductive Axis",
        "system_ta": "இனப்பெருக்கம் மற்றும் கழிவு மண்டலம்",
        "organs_en": "External Genitalia, Excretory Organs, Rectum, Bladder, Prostate",
        "organs_ta": "இனப்பெருக்க உறுப்புகள், மலக்குடல், சிறுநீர்ப்பை",
        "humor": "Kapha/Pitta (Water)",
    },
    9: {
        "sign_en": "Sagittarius (Dhanus)",
        "sign_ta": "தனுசு",
        "lord": "Jupiter",
        "system_en": "Hepato-Femoral Axis",
        "system_ta": "இடுப்பு மூட்டு மற்றும் தொடைகள்",
        "organs_en": "Hips, Thighs, Femoral Arteries, Sciatic Nerve, Hepatic System",
        "organs_ta": "இடுப்பு, தொடைகள், தொடை ரத்த நாளங்கள், இடுப்பு நரம்புகள்",
        "humor": "Pitta (Fire)",
    },
    10: {
        "sign_en": "Capricorn (Makara)",
        "sign_ta": "மகரம்",
        "lord": "Saturn",
        "system_en": "Skeletal & Articular Axis",
        "system_ta": "முழங்கால், மூட்டுகள் மற்றும் எலும்புக் கூடு",
        "organs_en": "Knees, Knee Caps, Skeletal System, Bones, Joints, Skin Barrier",
        "organs_ta": "முழங்கால்கள், எலும்புகள், மூட்டு இணைப்புகள், தோல் பாதுகாப்பு",
        "humor": "Vata (Earth)",
    },
    11: {
        "sign_en": "Aquarius (Kumbha)",
        "sign_ta": "கும்பம்",
        "lord": "Saturn",
        "system_en": "Circulatory & Crural Axis",
        "system_ta": "கணுக்கால், கெண்டைக்கால் மற்றும் ரத்த ஓட்டம்",
        "organs_en": "Calves, Shins, Ankles, Peripheral Circulation, Oxygen Transport",
        "organs_ta": "கெண்டைக் கால்கள், கணுக்கால்கள், ரத்த ஓட்ட மண்டலம்",
        "humor": "Vata (Air)",
    },
    12: {
        "sign_en": "Pisces (Meena)",
        "sign_ta": "மீனம்",
        "lord": "Jupiter",
        "system_en": "Pedal & Lymphatic Axis",
        "system_ta": "பாதங்கள் மற்றும் நிணநீர் மண்டலம்",
        "organs_en": "Feet, Toes, Lymphatic Circulation, Left Eye, Sleep Induction",
        "organs_ta": "பாதங்கள், கால்விரல்கள், நிணநீர் திரவம், இடது கண்",
        "humor": "Kapha (Water)",
    },
}


# Planetary Natural Anatomical Governance
PLANET_ANATOMY_GOVERNANCE: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "organs_en": "Heart, Bones, Vital Force, Head, Right Eye (day birth/male)",
        "organs_ta": "இதயம், எலும்புகள், உயிர்ச்சத்து, தலை, வலது கண்",
        "dosha": "Pitta (Bile / Heat)",
        "governance": "Vitality, circulation, central cardiac rhythm",
    },
    "Moon": {
        "organs_en": "Bodily Fluids, Blood Plasma, Stomach, Breasts, Left Eye",
        "organs_ta": "நீர்ச்சத்து, ரத்த பிளாஸ்மா, இரைப்பை, மார்பகம், இடது கண்",
        "dosha": "Kapha / Vata (Fluids)",
        "governance": "Emotional somaticization, hydration, lymphatic rhythm",
    },
    "Mars": {
        "organs_en": "Red Blood Cells, Bone Marrow, Muscular Tone, Cranial Base, Bile",
        "organs_ta": "சிவப்பு ரத்த அணுக்கள், எலும்பு மச்சை, தசைகள், பித்தம்",
        "dosha": "Pitta (Inflammatory)",
        "governance": "Cellular defense, inflammation, acute trauma repair",
    },
    "Mercury": {
        "organs_en": "Nervous System, Skin Epidermis, Bronchi, Vocal Organs, Intellect",
        "organs_ta": "நரம்பு மண்டலம், தோல், மூச்சுக்குழாய், குரல்வளை",
        "dosha": "Tridosha (Equi-balanced / Vata prone)",
        "governance": "Neurotransmitter signaling, skin respiration, coordination",
    },
    "Jupiter": {
        "organs_en": "Liver, Gallbladder, Pancreas, Arteries, Fat Tissue (Medas), Hearing",
        "organs_ta": "கல்லீரல், பித்தப்பை, கணையம், கொழுப்பு திசுக்கள், காதுகள்",
        "dosha": "Kapha (Nutritive)",
        "governance": "Metabolism, hepatic detoxification, cellular replenishment",
    },
    "Venus": {
        "organs_en": "Kidneys, Endocrine Hormones, Reproductive Fluids, Facial Complexion",
        "organs_ta": "சிறுநீரகம், ஹார்மோன்கள், இனப்பெருக்க திரவம், கண் பார்வை",
        "dosha": "Kapha / Vata",
        "governance": "Osmotic regulation, hormonal homeostasis, sensory ease",
    },
    "Saturn": {
        "organs_en": "Skeletal System, Joints, Teeth, Chronic Nerve Wind, Mineral Density",
        "organs_ta": "எலும்புகள், மூட்டு இணைப்புகள், பற்கள், வாத மண்டலம்",
        "dosha": "Vata (Cold / Dry / Chronic)",
        "governance": "Structural endurance, degenerative buffering, cellular aging",
    },
    "Rahu": {
        "organs_en": "Immune Paradoxes, Environmental Allergens, Subtle Toxic Strains",
        "organs_ta": "ஒவ்வாமை (அலர்ஜி), கண்டறிய கடினமான உடல் நிலைகள், நச்சுத்தன்மை",
        "dosha": "Vata / Pitta",
        "governance": "Immunological hypersensitivity, neuro-endocrine anomalies",
    },
    "Ketu": {
        "organs_en": "Microbial Resistance, Autoimmune Signatures, Inflammatory Fevers",
        "organs_ta": "நுண்ணுயிர் தொற்று எதிர்ப்பு, வைரஸ் பாதிப்பு, திடீர் உஷ்ணம்",
        "dosha": "Pitta (Intense heat)",
        "governance": "Deep cellular immunity, sudden diagnostic inflection points",
    },
}


# =============================================================================
# DR. S. KRISHNA KUMAR COMPENDIUM: MEDICAL ASTROLOGY & PROGENY TREATISE
# Reference: "A Book on Medical Astrology: Horoscope or Stethoscope - Diagnosis
# of Diseases, Problems in Progeny, Their Remedies"
# Author: Dr. S. Krishna Kumar, Chairman Bangalore Chapter of ICAS Chennai
# Publisher: Bhartiya Prachya Evam Sanatan Vigyan Sansthan, Delhi
# =============================================================================

DR_KRISHNA_KUMAR_METADATA: Dict[str, Any] = {
    "book_title": "A Book on Medical Astrology: Horoscope or Stethoscope (Diagnosis of Diseases, Problems in Progeny, Their Remedies)",
    "book_title_ta": "மருத்துவ ஜோதிடம்: ஜாதகமா அல்லது ஸ்டெதாஸ்கோப்பா (நோய் கண்டறிதல், சந்தான தோஷங்கள் மற்றும் பரிகாரங்கள்)",
    "author": "Dr. S. Krishna Kumar, Chairman Bangalore Chapter of Indian Council of Astrological Sciences (Regd.) Chennai",
    "publisher": "Bhartiya Prachya Evam Sanatan Vigyan Sansthan, Delhi (4649/21 Darya Ganj New Delhi-110002)",
    "submission": "Submitted to Open International University, Sri Lanka",
    "salient_features": [
        "Astrological Diagnosis vs. Medical Stethoscope: Pre-symptomatic detection via Karmic / Vidhi chart and Dasha periods years in advance.",
        "Prarabdha & Sanchita Karma Theory: Law of karma manifesting as physical constitution and diseases.",
        "Macrocosm & Microcosm (Pindanda & Brahmanda): Pancha Bhootas (5 Tatwas), Tanmatras, and Abhimani Devatas of organs.",
        "Navadwaras & Navagrahas: The nine body openings governed by planetary forces.",
        "Tridosha Ayurvedic Classification: Planetary constitution balancing Vata, Pitta, and Kapha.",
        "27 Nakshatras & Medical Anatomy: Governed body parts, Nakshatra Devatas, and specific disease susceptibilities for natives born in each star.",
        "Manasika & Buddhi Yogas: 11 classical combinations for intellect, memory retention, dullness, insanity (Unmada), and wavering mind.",
        "Organ-Specific & Systemic Yogas: Comprehensive diagnosis for head, eyes, ears, mouth, throat, boils, urinary tract, heart, kidneys, and leprosy.",
        "Progeny Problems & 9 Curses (Shapa): Detailed causes and precise Vedic propitiations for Sarpa, Pitru, Bhratru, Matru, Matula, Brahma, Patni, and Preta Shapa.",
        "Female Horoscopy & 10 Gestational Months: Month-by-month fetal development governed by Grahas (Kalala, Ghana, Ankura, Asthi, Charma, Angaja, Chethanatha, Adhana, Udvega, Prasava).",
        "Caesarean vs. Normal Delivery: Predictive indicators based on Mars, Moon, and Jupiter aspects.",
        "12 Classical Clinical Case Histories: Real consulting horoscopes illustrating brain tumour, blood cancer, breast cancer, vitiligo, and blindness via Dagdha Rashis.",
    ],
}

# 27 Nakshatras: Body Parts, Devatas, Disease Tendencies, and Vedic Propitiations
NAKSHATRA_27_MEDICAL_MATRIX: Dict[int, Dict[str, Any]] = {
    1: {
        "number": 1,
        "name": "Ashwini",
        "name_ta": "அஸ்வினி",
        "body_part_en": "Upper feet and toes",
        "body_part_ta": "மேல் பாதம் மற்றும் கால் விரல்கள்",
        "devata": "Ashwini Kumaras (Celestial Physicians)",
        "disease_tendency_en": "Periodical fever, sudden body temperature spikes, malaria-like fevers",
        "disease_tendency_ta": "விட்டு விட்டு வரும் காய்ச்சல், திடீர் உடல் உஷ்ண மாறுபாடுகள்",
        "propitiation_en": "Propitiation of Ashwini Devatas with herbal ghee and charity of horse gram.",
        "propitiation_ta": "அஸ்வினி குமாரர்கள் ஆராதனை, மூலிகைத் தைல வழிபாடு மற்றும் கொள்ளு தானம்.",
    },
    2: {
        "number": 2,
        "name": "Bharani",
        "name_ta": "பரணி",
        "body_part_en": "Lower feet and soles",
        "body_part_ta": "கீழ் பாதம் மற்றும் பாத அடிப் பகுதி",
        "devata": "Yama (Lord of Dharma & Mortality)",
        "disease_tendency_en": "Dysentery, acute loose bowels, lower bowel inflammation",
        "disease_tendency_ta": "வயிற்றுப்போக்கு, சீதபேதி, அடிக்குடல் அழற்சி",
        "propitiation_en": "Yama Devata pooja, Tila Homa (sesame fire ritual), and serving cool water to travelers.",
        "propitiation_ta": "யம தர்மராஜன் வழிபாடு, எள் ஹோமம் மற்றும் தாகசாந்தி தானம்.",
    },
    3: {
        "number": 3,
        "name": "Krittika",
        "name_ta": "கிருத்திகை",
        "body_part_en": "Head and cerebral crown",
        "body_part_ta": "தலை மற்றும் உச்சிப் பகுதி",
        "devata": "Agni (God of Fire)",
        "disease_tendency_en": "Intestinal disorders with alternating constipation and diarrhoea, gastric heat",
        "disease_tendency_ta": "மாறி மாறி வரும் மலச்சிக்கல் & வயிற்றுப்போக்கு, குடல் உஷ்ணம்",
        "propitiation_en": "Agni pooja with pure cow ghee oblations, feeding fasting devotees.",
        "propitiation_ta": "பசு நெய் கொண்டு அக்னி வழிபாடு மற்றும் அன்னதானம்.",
    },
    4: {
        "number": 4,
        "name": "Rohini",
        "name_ta": "ரோகிணி",
        "body_part_en": "Forehead and cranial frontal bone",
        "body_part_ta": "நெற்றி மற்றும் முன்தலை எலும்பு",
        "devata": "Brahma / Prajapati (Creator)",
        "disease_tendency_en": "Piles, haemorrhoids, and ano-rectal inflammatory disorders",
        "disease_tendency_ta": "மூல நோய், பௌத்திரம் மற்றும் ஆசனவாய் கோளாறுகள்",
        "propitiation_en": "Surya & Brahma worship, consuming coolant foods, and charity of white rice.",
        "propitiation_ta": "பிரம்மா மற்றும் சூரியன் வழிபாடு, குளிர்ச்சி உணவுகள் உட்கொள்ளுதல், பச்சரிசி தானம்.",
    },
    5: {
        "number": 5,
        "name": "Mrigashira",
        "name_ta": "மிருகசீரிஷம்",
        "body_part_en": "Eyebrows and ocular ridge",
        "body_part_ta": "புருவங்கள் மற்றும் கண் புருவ எலும்பு",
        "devata": "Moon / Soma (Nectar of Immortality)",
        "disease_tendency_en": "Chronic indigestion, sluggish digestive metabolism, bilious nausea",
        "disease_tendency_ta": "அஜீரணம், செரிமான மந்தம், பித்த குமட்டல்",
        "propitiation_en": "Chandra pooja on Mondays, offering raw milk to Shiva, consuming digestive herbs.",
        "propitiation_ta": "திங்கட்கிழமை சந்திர வழிபாடு, சிவபெருமானுக்கு பால் அபிஷேகம், சீரக நீர் அருந்துதல்.",
    },
    6: {
        "number": 6,
        "name": "Ardra",
        "name_ta": "திருவாதிரை",
        "body_part_en": "Eyes and optic pathways",
        "body_part_ta": "கண்கள் மற்றும் பார்வை நரம்புகள்",
        "devata": "Rudra (Lord of Destructive Transformation)",
        "disease_tendency_en": "Mandagni (weak gastric fire), chronic low appetite, metabolic deficiency",
        "disease_tendency_ta": "மந்தாக்னி (பசியின்மை / பலவீனமான செரிமான நெருப்பு)",
        "propitiation_en": "Rudrabhisheka with bilva leaves and recitation of Sri Rudram.",
        "propitiation_ta": "வில்வ இலைகளால் ருத்ராபிஷேகம் மற்றும் ஸ்ரீ ருத்ர பாராயணம்.",
    },
    7: {
        "number": 7,
        "name": "Punarvasu",
        "name_ta": "புனர்பூசம்",
        "body_part_en": "Nose and nasal cavities",
        "body_part_ta": "மூக்கு மற்றும் நாசித் துவாரங்கள்",
        "devata": "Aditi (Universal Cosmic Mother)",
        "disease_tendency_en": "Cholera, acute water-borne gastrointestinal infections, dehydration",
        "disease_tendency_ta": "வாந்திபேதி, நீர் தொற்று மற்றும் தீவிர நீரிழப்பு",
        "propitiation_en": "Aditi Devi worship, donating pure drinking water facilities to the public.",
        "propitiation_ta": "அதிதி தேவி வழிபாடு, பொதுமக்களுக்கு குடிநீர் வசதி ஏற்படுத்தித் தருதல்.",
    },
    8: {
        "number": 8,
        "name": "Pushya",
        "name_ta": "பூசம்",
        "body_part_en": "Face and oral structure",
        "body_part_ta": "முகம் மற்றும் வாய் அமைப்பு",
        "devata": "Brihaspati (Preceptor of Gods)",
        "disease_tendency_en": "Tastelessness (Anorexia / Aruchi), loss of palate sensation, mouth dryness",
        "disease_tendency_ta": "சுவையின்மை (அரோசகம்), நாக்கு சுவை இழப்பு, வாய் உலர்வு",
        "propitiation_en": "Brihaspati Shanti, Guru stotra recitation, donating yellow chickpeas and saffron.",
        "propitiation_ta": "பிரகஸ்பதி சாந்தி, குரு தியானம், கொண்டைக்கடலை மற்றும் குங்குமப்பூ தானம்.",
    },
    9: {
        "number": 9,
        "name": "Ashlesha",
        "name_ta": "ஆயில்யம்",
        "body_part_en": "Ears and auditory channels",
        "body_part_ta": "காதுகள் மற்றும் செவிப்பாதை",
        "devata": "Sarpa (Serpent Deity)",
        "disease_tendency_en": "Anemia (Pandu Roga), blood weakness, pale complexion, lack of stamina",
        "disease_tendency_ta": "ரத்த சோகை (பாண்டு நோய்), ரத்த அணுக்கள் குறைபாடு, உடல் சோர்வு",
        "propitiation_en": "Sarpa pooja, offering milk to Naga deities, consuming iron-rich satwik diet.",
        "propitiation_ta": "நாகர் வழிபாடு, புற்றுக்குப் பால் வார்த்தல் மற்றும் ஊட்டச்சத்து பராமரிப்பு.",
    },
    10: {
        "number": 10,
        "name": "Magha",
        "name_ta": "மகம்",
        "body_part_en": "Chin and mandibular jaw",
        "body_part_ta": "தாடை மற்றும் கீழ்த்தாடை எலும்பு",
        "devata": "Pitrus (Ancestral Forefathers)",
        "disease_tendency_en": "Breathing problems, asthma, chronic respiratory congestion",
        "disease_tendency_ta": "மூச்சுத்திணறல், ஆஸ்துமா மற்றும் நாள்பட்ட சுவாசக் கோளாறுகள்",
        "propitiation_en": "Pitru Tarpanam, Amavasya oblations, and serving food to elderly seekers.",
        "propitiation_ta": "பித்ரு தர்ப்பணம், அமாவாசை திதி வழிபாடு மற்றும் முதியோருக்கு அன்னதானம்.",
    },
    11: {
        "number": 11,
        "name": "Purva Phalguni",
        "name_ta": "பூரம்",
        "body_part_en": "Right hand and arm",
        "body_part_ta": "வலது கை மற்றும் முழங்கை",
        "devata": "Surya / Bhaga (Solar Deity)",
        "disease_tendency_en": "Chronic cough (both dry and productive bronchitis), bronchial irritation",
        "disease_tendency_ta": "வறட்டு இருமல் அல்லது சளி இருமல், மூச்சுக்குழாய் அழற்சி",
        "propitiation_en": "Surya Namaskara at dawn, Aditya Hridaya recitation, drinking warm tulsi decoctions.",
        "propitiation_ta": "சூரிய நமஸ்காரம், ஆதித்ய ஹிருதய பாராயணம் மற்றும் துளசி தீர்த்தம்.",
    },
    12: {
        "number": 12,
        "name": "Uttara Phalguni",
        "name_ta": "உத்திரம்",
        "body_part_en": "Left hand and arm",
        "body_part_ta": "இடது கை மற்றும் முழங்கை",
        "devata": "Aryama (Deity of Honorable Treaties)",
        "disease_tendency_en": "Leprosy (Kushta), persistent dermatological eruptions, fungal skin lesions",
        "disease_tendency_ta": "குஷ்டம், நாள்பட்ட தோல் நோய்கள், படர்தாமரை",
        "propitiation_en": "Aryama worship, supporting orphanages, applying sandalwood and neem preparations.",
        "propitiation_ta": "அரியமான் வழிபாடு, ஆதரவற்றோருக்கு உதவுதல், சந்தன-வேப்பிலை பயன்பாடு.",
    },
    13: {
        "number": 13,
        "name": "Hasta",
        "name_ta": "அஸ்தம்",
        "body_part_en": "Fingers and manual dexterity joints",
        "body_part_ta": "கை விரல்கள் மற்றும் கை மூட்டுகள்",
        "devata": "Savitru (Creative Solar Luminary)",
        "disease_tendency_en": "Diabetes mellitus of various types (Prameha), pancreatic weakness",
        "disease_tendency_ta": "பல்வேறு வகையான நீரிழிவு (பிரமேகம்), கணைய பலவீனம்",
        "propitiation_en": "Gayatri Japa at sunrise, donating green grams, avoiding excessive sweets.",
        "propitiation_ta": "காலை காயத்ரி ஜபம், பாசிப்பயறு தானம், சர்க்கரை உணவுகளை மட்டுப்படுத்துதல்.",
    },
    14: {
        "number": 14,
        "name": "Chitra",
        "name_ta": "சித்திரை",
        "body_part_en": "Neck and cervical vertebrae",
        "body_part_ta": "கழுத்து மற்றும் பிடரிப் பகுதி",
        "devata": "Tvashtru (Celestial Architect Vishwakarma)",
        "disease_tendency_en": "Giddiness, vertigo, cervical balance disorders, partial loss of consciousness",
        "disease_tendency_ta": "தலைச்சுற்றல், மயக்கம், கழுத்து நரம்பு அழுத்தம்",
        "propitiation_en": "Tvashtru Vishwakarma worship, donating tools or support to artisans.",
        "propitiation_ta": "துவஷ்டா வழிபாடு, கைவினைஞர்களுக்கு உதவுதல், கழுத்துக்கான எளிய யோகாசனம்.",
    },
    15: {
        "number": 15,
        "name": "Swati",
        "name_ta": "சுவாதி",
        "body_part_en": "Chest and upper thoracic cavity",
        "body_part_ta": "மார்பு மற்றும் மேல் நெஞ்சுப் பகுதி",
        "devata": "Vayu (Wind Deity / Prana Lord)",
        "disease_tendency_en": "Eye diseases, corneal irritation, blurred vision, ocular dryness",
        "disease_tendency_ta": "கண் நோய்கள், கண் வறட்சி, பார்வை மங்குதல்",
        "propitiation_en": "Vayu stotra, lighting pure camphor for Shiva, pranayama practice.",
        "propitiation_ta": "வாயு பகவான் பிரார்த்தனை, கற்பூர தீப வழிபாடு மற்றும் பிராணாயாமப் பயிற்சி.",
    },
    16: {
        "number": 16,
        "name": "Vishakha",
        "name_ta": "விசாகம்",
        "body_part_en": "Lungs and respiratory alveoli",
        "body_part_ta": "நுரையீரல் மற்றும் மூச்சு நுண்குழல்கள்",
        "devata": "Indra & Agni (Dual Rulers of Might and Fire)",
        "disease_tendency_en": "Ear diseases, auditory canal infections, tinnitus, partial hearing loss",
        "disease_tendency_ta": "காது நோய்கள், காது இரைச்சல் (டின்னிடஸ்), செவித்திறன் குறைவு",
        "propitiation_en": "Murugan / Skanda worship, lighting ghee lamps on Tuesdays, ear hygiene.",
        "propitiation_ta": "முருகப்பெருமான் வழிபாடு, செவ்வாய்க்கிழமை நெய் தீபம் ஏற்றுதல்.",
    },
    17: {
        "number": 17,
        "name": "Anuradha",
        "name_ta": "அனுஷம்",
        "body_part_en": "Stomach and epigastric zone",
        "body_part_ta": "வயிறு மற்றும் இரைப்பை மேல் பகுதி",
        "devata": "Mitra (Deity of Friendship & Universal Light)",
        "disease_tendency_en": "Diseases of the nose (Peenasa Roga), chronic catarrh, sinus blockages",
        "disease_tendency_ta": "மூக்கு நோய்கள் (பீனச ரோகம்), நாள்பட்ட சளி, சைனஸ் அடைப்பு",
        "propitiation_en": "Mitra Devata aradhana, nasal steam therapies, donating bell-metal vessels.",
        "propitiation_ta": "மித்ர தேவதை வழிபாடு, மூலிகை ஆவி பிடித்தல் மற்றும் வெண்கல பாத்திரம் தானம்.",
    },
    18: {
        "number": 18,
        "name": "Jyeshtha",
        "name_ta": "கேட்டை",
        "body_part_en": "Right portion of stomach and hepatic margin",
        "body_part_ta": "வயிற்றின் வலது பகுதி மற்றும் கல்லீரல் ஓரம்",
        "devata": "Indra / Moon (King of Devas)",
        "disease_tendency_en": "Diseases of the mouth: teeth decay, tongue sores, lip fissures, gums & throat",
        "disease_tendency_ta": "வாய் நோய்கள்: பல் சொத்தை, நாக்கு புண்கள், உதடு வெடிப்பு, தொண்டை வலி",
        "propitiation_en": "Indra worship, salt-water oral rinses, charity of fresh green vegetables.",
        "propitiation_ta": "இந்திர பகவான் வழிபாடு, மூலிகை வாய் கொப்பளிப்பு, பசும் காய்கறிகள் தானம்.",
    },
    19: {
        "number": 19,
        "name": "Mula",
        "name_ta": "மூலம்",
        "body_part_en": "Left portion of stomach and splenic zone",
        "body_part_ta": "வயிற்றின் இடது பகுதி மற்றும் மண்ணீரல்",
        "devata": "Nirriti / Rakshasa (Goddess of Calamity & Dissolution)",
        "disease_tendency_en": "Tuberculosis of any type (Kshaya Roga), deep chest and lung wasting",
        "disease_tendency_ta": "எவ்வகை காசநோயும் (க்ஷய ரோகம்), நுரையீரல் பலவீனம்",
        "propitiation_en": "Maha Mrityunjaya Japa, donating roots and tubers, worshipping Lord Hanuman.",
        "propitiation_ta": "மகா மிருத்யுஞ்சய ஜபம், கிழங்கு வகைகள் தானம் மற்றும் அனுமன் வழிபாடு.",
    },
    20: {
        "number": 20,
        "name": "Purvashada",
        "name_ta": "பூராடம்",
        "body_part_en": "Back and lumbar vertebral column",
        "body_part_ta": "முதுகு மற்றும் கீழ்முதுகு எலும்புகள்",
        "devata": "Apas / Jala Devata (Primordial Waters)",
        "disease_tendency_en": "Formation of stones in urinary tract (kidney/bladder calculi / Ashmari)",
        "disease_tendency_ta": "சிறுநீரகக் கற்கள் (அஷ்மரீ) மற்றும் சிறுநீர்ப்பை அடைப்புகள்",
        "propitiation_en": "Varuna Pooja, maintaining high fluid intake, donating tender coconuts.",
        "propitiation_ta": "வருண பகவான் பூஜை, அதிக நீர் அருந்துதல், இளநீர் தானம்.",
    },
    21: {
        "number": 21,
        "name": "Uttarashada",
        "name_ta": "உத்திராடம்",
        "body_part_en": "Waist and pelvic girdle",
        "body_part_ta": "இடுப்பு மற்றும் இடுப்பு வளைய எலும்பு",
        "devata": "Vishwadevas (Universal Divine Virtues)",
        "disease_tendency_en": "Vomiting, bilious reflux, gastric emesis, chronic nausea",
        "disease_tendency_ta": "வாந்தி, பித்த வாந்தி, அமில ஏப்பம், செரிமான எதிர்ப்போக்கு",
        "propitiation_en": "Vishwadeva worship, light alkaline diet, charity to temples.",
        "propitiation_ta": "விஸ்வே தேவர்கள் ஆராதனை, எளிமையான காரசாரமற்ற உணவு மற்றும் ஆலய வழிபாடு.",
    },
    22: {
        "number": 22,
        "name": "Shravana",
        "name_ta": "திருவோணம்",
        "body_part_en": "Upper genital region and groins",
        "body_part_ta": "மேல் பிறப்புறுப்பு மற்றும் தொடை இடுக்கு",
        "devata": "Lord Vishnu (Preserver of Cosmos)",
        "disease_tendency_en": "Tastelessness disease, neurological loss of oral sensation, digestive apathy",
        "disease_tendency_ta": "சுவை நரம்பு பலவீனம், நாக்கு மரத்துப்போதல், உணவு விருப்பமின்மை",
        "propitiation_en": "Vishnu Sahasranama recitation on Dwadashi, donating Tulasi plants and curd rice.",
        "propitiation_ta": "துவாதசி திதியில் விஷ்ணு சகஸ்ரநாமம், துளசி மாலை சாற்றுதல், தயிர்சாத தானம்.",
    },
    23: {
        "number": 23,
        "name": "Dhanishta",
        "name_ta": "அவிட்டம்",
        "body_part_en": "Generative organs and perineum",
        "body_part_ta": "பிறப்புறுப்பு மற்றும் கீழ் இடுப்பு பகுதி",
        "devata": "Ashta Vasus (Eight Cosmic Elements)",
        "disease_tendency_en": "Pains caused by Vata disorder, sprains, sciatica, severe rheumatism",
        "disease_tendency_ta": "வாத வலிகள், சுளுக்கு, மூட்டு வாதம், தசைப்பிடிப்பு",
        "propitiation_en": "Ashta Vasu worship, application of medicinal sesame oil, keeping warm.",
        "propitiation_ta": "அஷ்ட வசுக்கள் வழிபாடு, நல்லெண்ணெய் மசாஜ் மற்றும் வெந்நீர் குளியல்.",
    },
    24: {
        "number": 24,
        "name": "Shatabhisha",
        "name_ta": "சதயம்",
        "body_part_en": "Right thigh and femoral muscles",
        "body_part_ta": "வலது தொடை மற்றும் தொடை தசைகள்",
        "devata": "Varuna (Cosmic Ocean & Mystic Healer)",
        "disease_tendency_en": "Bilious diseases, liver heat, gallbladder inflammation, yellow bile excess",
        "disease_tendency_ta": "பித்த நோய்கள், கல்லீரல் உஷ்ணம், பித்தப்பை அழற்சி",
        "propitiation_en": "Varuna homa, bathing in holy rivers, consuming cooling herbal bitters.",
        "propitiation_ta": "வருண ஹோமம், புண்ணிய தீர்த்த ஸ்நானம், வேப்பிலை கஷாயம் போன்ற பித்த நிவாரணிகள்.",
    },
    25: {
        "number": 25,
        "name": "Purva Bhadrapada",
        "name_ta": "பூரட்டாதி",
        "body_part_en": "Left thigh and femoral muscles",
        "body_part_ta": "இடது தொடை மற்றும் தொடை தசைகள்",
        "devata": "Aja Ekapada / Jala (One-Footed Cosmic Serpent)",
        "disease_tendency_en": "Phlegmatic diseases (Kapha excess), severe mucus accumulation, bronchial edema",
        "disease_tendency_ta": "கப நோய்கள் (சளி மிகுதி), நுரையீரல் கோழை அடைப்பு",
        "propitiation_en": "Rudra Japa, dry herbal fomentation, consuming trikatu (dry ginger, pepper, pippali).",
        "propitiation_ta": "ருத்ர ஜபம், திரிகடுக சூரணம் உட்கொள்ளுதல், உலர் ஒத்தடம் கொடுத்தல்.",
    },
    26: {
        "number": 26,
        "name": "Uttara Bhadrapada",
        "name_ta": "உத்திரட்டாதி",
        "body_part_en": "Ankles and Achilles tendon",
        "body_part_ta": "கணுக்கால் மற்றும் குதிகால் நரம்பு",
        "devata": "Ahirbudhnya / Brahma (Serpent of the Depths)",
        "disease_tendency_en": "Diseases developed from chronic fatigue, physical exhaustion, adrenal burnout",
        "disease_tendency_ta": "அதிசோர்வு, உடல் தளர்ச்சி, நரம்பு பலவீனம் மற்றும் தளர்வு நோய்கள்",
        "propitiation_en": "Brahma aradhana, disciplined sleep schedules, nourishing rasayana tonics.",
        "propitiation_ta": "பிரம்மா ஆராதனை, முறையான ஆழ்ந்த உறக்கம், ரசாயன சத்தான உணவுகள்.",
    },
    27: {
        "number": 27,
        "name": "Revati",
        "name_ta": "ரேவதி",
        "body_part_en": "Feet and pedal digits",
        "body_part_ta": "பாதங்கள் மற்றும் கால் பெருவிரல்கள்",
        "devata": "Pushan (Solar Nourisher & Guide)",
        "disease_tendency_en": "Diseases developed from boils, carbuncles, unhealed ulcerations, and wounds",
        "disease_tendency_ta": "புண்கள், கொப்புளங்கள், ஆறாத காயங்கள் மற்றும் ரத்தக் கட்டிகள்",
        "propitiation_en": "Pushan worship, feeding cows green grass, topical antiseptic herbal care.",
        "propitiation_ta": "பூஷா வழிபாடு, பசுக்களுக்கு அகத்திக்கீரை வழங்குதல், மூலிகைப் புண் பராமரிப்பு.",
    },
}

# 10 Gestational Months: Ruling Grahas and Developmental Milestones
PREGNANCY_GESTATIONAL_MONTHS: List[Dict[str, Any]] = [
    {
        "month": 1,
        "ruling_planet": "Venus",
        "sanskrit_term": "Kalala (கலலம்)",
        "stage_en": "Fleshy Zygote / Seminal-Ovular Fluid Union",
        "stage_ta": "விந்து-சுக்கில சேர்க்கை / கருக்கோளம்",
        "description_en": "In the 1st month, the fluid union of male semen (Shukla) and female ovum (Shonitha) forms a viscous fleshy mass called Kalala, ruled by Venus. Affliction in this month risks early zygotic dissolution.",
        "description_ta": "முதல் மாதத்தில் சுக்ல-சோணித இணைப்பால் 'கலலம்' எனும் திரவக் கரு உருவாகிறது; இதற்கு சுக்கிரன் அதிபதி.",
    },
    {
        "month": 2,
        "ruling_planet": "Mars",
        "sanskrit_term": "Ghana (கனம்)",
        "stage_en": "Solidification into Kidney-Bean Mass",
        "stage_ta": "கரு திரட்சியடைந்து கெட்டிப்படுதல்",
        "description_en": "In the 2nd month, the mass undergoes solidification (Ghana) into an embryonic vesicle shaped like a kidney bean, ruled by Mars. Excessive heat or Mars affliction causes cramping.",
        "description_ta": "இரண்டாம் மாதத்தில் கரு கெட்டிப்பட்டு (கனம்) சிறுநீரக விதை வடிவம் பெறுகிறது; இதற்கு செவ்வாய் அதிபதி.",
    },
    {
        "month": 3,
        "ruling_planet": "Jupiter",
        "sanskrit_term": "Ankura (அங்குரம்)",
        "stage_en": "Sprouting of Limbs, Buds, and Organ Primordia",
        "stage_ta": "உறுப்புகளின் முளைப்பு மற்றும் கிளைத்தல்",
        "description_en": "In the 3rd month, the sprouts (Ankura) of the arms, legs, and internal organ primordia show themselves, governed by Jupiter (Karaka for expansion and growth).",
        "description_ta": "மூன்றாம் மாதத்தில் கை, கால்கள் மற்றும் உள்ளுறுப்புகளின் அரும்புகள் முளைக்கின்றன (அங்குரம்); குரு பகவான் இதற்கு அதிபதி.",
    },
    {
        "month": 4,
        "ruling_planet": "Sun",
        "sanskrit_term": "Asthi (அஸ்தி)",
        "stage_en": "Bone Formation & Skeletal Matrix",
        "stage_ta": "எலும்பு உருவாக்கம் மற்றும் மண்டை ஓடு உறுதிபெறுதல்",
        "description_en": "In the 4th month, skeletal ossification takes place; bones, vertebrae, and cranial structures harden, governed by the Sun (Karaka for Asthi/Bones). If Sun is debilitated/afflicted, developmental arrest occurs.",
        "description_ta": "நான்காம் மாதத்தில் எலும்புகள், தண்டுவடம் உறுதியாகின்றன (அஸ்தி); சூரிய பகவான் இதன் அதிபதி.",
    },
    {
        "month": 5,
        "ruling_planet": "Moon",
        "sanskrit_term": "Charma (சர்மம்)",
        "stage_en": "Skin Layers, Epidermis & Bodily Fluids",
        "stage_ta": "தோல் அடுக்குகள் மற்றும் திரவப் படலம் உருவாக்கம்",
        "description_en": "In the 5th month, the skin (Charma) develops over the muscular structure, and subcutaneous bodily fluids are regulated by the Moon.",
        "description_ta": "ஐந்தாம் மாதத்தில் தோல், தோல் நிறமிகள் மற்றும் நீர்ச்சத்து உருவாகிறது; சந்திரன் இதன் அதிபதி.",
    },
    {
        "month": 6,
        "ruling_planet": "Saturn",
        "sanskrit_term": "Angaja (அங்கஜம்)",
        "stage_en": "Nails, Hair, Body Bristles & Sensory Openings",
        "stage_ta": "முடி, நகங்கள், உடல் ரோமங்கள் மற்றும் அங்கங்கள்",
        "description_en": "In the 6th month, hairs, fingernails, and delicate peripheral structures (Angaja) take form, governed by Saturn (controller of structural maturation).",
        "description_ta": "ஆறாம் மாதத்தில் தலைமுடி, நகங்கள், ரோமங்கள் வளர்கின்றன; சனி பகவான் இதன் அதிபதி.",
    },
    {
        "month": 7,
        "ruling_planet": "Mercury",
        "sanskrit_term": "Chethanathaha (சேதனா)",
        "stage_en": "Sensory Animation, Nervous Impulses & Consciousness",
        "stage_ta": "உயிரோட்ட உணர்வு, நரம்பு இயக்கம் மற்றும் சைதன்யம்",
        "description_en": "In the 7th month, consciousness (Chethanathaha) awakens; the fetal nervous system and sensory coordination become active, ruled by Mercury.",
        "description_ta": "ஏழாம் மாதத்தில் கருவிற்குள் சைதன்யம் (உயிர் உணர்வு) மற்றும் நரம்பியல் இயக்கம் துவங்குகிறது; புதன் இதன் அதிபதி.",
    },
    {
        "month": 8,
        "ruling_planet": "Adhana Lagna Lord",
        "sanskrit_term": "Adhana / Ojas (ஆதான லக்னாதிபதி)",
        "stage_en": "Nourishment via Umbilical Cord (High Vulnerability)",
        "stage_ta": "தொப்புள் கொடி வழியே தாயின் சத்து பெறுதல் (மிக முக்கிய மாதம்)",
        "description_en": "In the 8th month, the vital fluid (Ojas) oscillates between mother and child via the umbilical cord, governed by the lord of conception time (Adhana Lagna). Ancients considered this a highly delicate month.",
        "description_ta": "எட்டாம் மாதத்தில் ஓஜஸ் சக்தி தாய்க்கும் சேய்க்கும் மாறி மாறி சுழலும்; ஆதான லக்னாதிபதி ஆளும் இந்நாட்களில் மிகுந்த கவனம் தேவை.",
    },
    {
        "month": 9,
        "ruling_planet": "Moon",
        "sanskrit_term": "Udvega (உத்வேகம்)",
        "stage_en": "Maternal Anxiety & Fetal Labour Readiness",
        "stage_ta": "பிரசவ உத்வேகம், பிரசவ வலி தயார்நிலை",
        "description_en": "In the 9th month, maternal labour anxiety (Udvega) and fetal descent begin, governed by the Moon.",
        "description_ta": "ஒன்பதாம் மாதத்தில் குழந்தை வெளிப்பட எத்தனிக்கும் உத்வேகம் உண்டாகிறது; சந்திரன் இதற்கு அதிபதி.",
    },
    {
        "month": 10,
        "ruling_planet": "Sun",
        "sanskrit_term": "Prasava (பிரசவம்)",
        "stage_en": "Delivery and Emergence into Sunlight",
        "stage_ta": "சுகப்பிரசவம் மற்றும் வெளி உலகுக்கு வருதல்",
        "description_en": "In the 10th month, birth and delivery (Prasava) take place under the governance of the Sun (bringer of life into daylight).",
        "description_ta": "பத்தாம் மாதத்தில் குழந்தை பிரசவமாகி உலகுக்கு வருகிறது; சூரிய பகவான் இதற்கு அதிபதி.",
    },
]

# 9 Severe Curses (Shapa) Causing Progeny Obstacles and Vedic Remedies
PROGENY_CURSES_AND_REMEDIES: List[Dict[str, Any]] = [
    {
        "id": "sarpa_shapa",
        "shapa_name": "Sarpa Shapa (Curse of Snake / Serpent)",
        "shapa_name_ta": "சர்ப்ப சாபம் (நாக சாபம்)",
        "afflicted_karaka": "Rahu & 5th House / Jupiter",
        "cause_en": "Harm inflicted on serpents or destroying ant-hills in previous or present births.",
        "cause_ta": "முற்பிறவியில் அல்லது இப்பிறவியில் பாம்புகளைத் துன்புறுத்துதல் அல்லது புற்று அழித்தல்.",
        "combinations": [
            "Rahu occupies the 5th house and receives the aspect of Mars, or occupies Aries/Scorpio.",
            "Saturn conjoins the 5th lord in the 5th house aspected by Moon, or conjoined with Moon & Rahu.",
            "Jupiter (Putrakaraka) conjoins Rahu and 5th lord while Lagna lord conjoins Mars.",
            "5th house falls in Aries/Scorpio with Rahu and Mercury.",
        ],
        "remedy_en": "Perform Naga Pratishtha (installing a consecrated golden or stone Naga idol), worship Nagaraja with milk, donate a milch cow (Godana), fertile land, sesame seeds (Tila), and gold.",
        "remedy_ta": "சுயகிருஹ்ய சூத்திரப்படி தங்கத்தில் நாக பிரதிஷ்டை செய்து பூஜித்தல், கோதானம், பூமிதானம், எள் மற்றும் பொன் தானம் செய்தல்.",
    },
    {
        "id": "pitru_shapa",
        "shapa_name": "Pitru Shapa (Curse of Forefathers / Departed Souls)",
        "shapa_name_ta": "பித்ரு சாபம் (முன்னோர்கள் சாபம்)",
        "afflicted_karaka": "Sun & 9th House / 9th Lord",
        "cause_en": "Neglecting father, ancestors, or failing to perform annual Shraddha ceremonies.",
        "cause_ta": "தந்தையை அவமதித்தல், பித்ரு தர்ப்பணம் மற்றும் வருடாந்திர சிரார்த்தங்களை கைவிடுதல்.",
        "combinations": [
            "Sun is debilitated in 5th house in Saturn's Navamsha and hemmed between malefics.",
            "5th lord Sun is in 5th or 9th with malefics or aspected by malefics.",
            "Jupiter is in Leo while 5th lord conjoins Sun, and malefics occupy 5th and Lagna.",
            "9th lord is in 6, 8, or 12 while Jupiter is in a malefic house.",
            "Sun in 8th, Saturn in 5th, 5th lord with Rahu, and malefics in Lagna.",
        ],
        "remedy_en": "Perform Gaya Shraddha at Gaya Kshetra for departed souls; perform Anna-dana (feeding 1,000 or 10,000 Brahmins), or perform Kanya Dana (sponsoring marriage of an underprivileged girl), and donate a cow with calf.",
        "remedy_ta": "கயா க்ஷேத்திரத்தில் கயா சிரார்த்தம் செய்தல், 10,000 பேருக்கு அன்னதானம் அல்லது கன்னிகாதானம் மற்றும் கன்றுடன் கூடிய பசு தானம்.",
    },
    {
        "id": "bhratru_shapa",
        "shapa_name": "Bhratru Shapa (Curse of Brothers)",
        "shapa_name_ta": "ப்ராத்ரு சாபம் (சகோதரர்கள் சாபம்)",
        "afflicted_karaka": "Mars & 3rd Lord",
        "cause_en": "Cheating brothers out of ancestral wealth or inheritance, driving them into distress and anguish.",
        "cause_ta": "சகோதரர்களுக்குரிய சொத்து அல்லது பணத்தை தராமல் ஏமாற்றி அவர்களின் மனவேதனைக்கு ஆளாதல்.",
        "combinations": [
            "3rd lord occupies 5th conjoined with Mars & Rahu, while 5th and Lagna lords are in 8th.",
            "Mars in Lagna, Saturn in 5th, 3rd lord in 9th, and Jupiter in 12th.",
            "5th lord debilitated in 3rd while Saturn is in 5th, and Mars in 5th or 12th.",
            "Lagna lord in 12th, Mars in 5th, and 5th lord in 8th.",
        ],
        "remedy_en": "Listen to Srimad Vishnu Purana; observe Chandrayana Vrata; bathe in the sacred Kaveri River or visit a revered Vishnu Kshetra; plant an Ashwatha tree with sacred thread and marriage rites; donate 10 cows, observe Prajapatya Vrata, and donate land with fruit trees.",
        "remedy_ta": "விஷ்ணு புராணம் கேட்டல், சந்திராயண விரதம், காவேரி ஸ்நானம், அரச மரக் கன்று நட்டு உபநயன-விவாக சடங்கு செய்தல், 10 பசுக்கள் தானம் மற்றும் பழமரங்கள் உள்ள நிலதானம்.",
    },
    {
        "id": "matru_shapa",
        "shapa_name": "Matru Shapa (Curse of Mother)",
        "shapa_name_ta": "மாத்ரு சாபம் (தாயின் சாபம்)",
        "afflicted_karaka": "Moon & 4th Lord",
        "cause_en": "Hurting, abandoning, or speaking cruelly to one's mother or maternal figures.",
        "cause_ta": "தாயை உதாசீனப்படுத்துதல், கடுமையான சொற்களால் நோகடித்தல் மற்றும் அன்னையை கைவிடுதல்.",
        "combinations": [
            "5th lord is Moon, debilitated or hemmed with malefics, with malefics in 4th and 5th.",
            "Saturn in 11th, malefics in 4th, and Moon in 5th in debilitation.",
            "5th lord in 6, 8, or 12, Lagna lord debilitated, and Moon conjoined with malefics.",
            "Moon in 5th or 9th conjoined with Saturn, Rahu, Mars, and Jupiter.",
            "Cancer Lagna with Mars & Rahu, while Moon & Saturn occupy Scorpio.",
        ],
        "remedy_en": "Perform 100,000 Gayatri Japa; donate a house or shelter; distribute milk boiled in silver vessels to scholars; serve food and perform 28,000 pradakshinas (circumambulations) around the sacred Ashwatha tree.",
        "remedy_ta": "ஒரு லட்சம் காயத்ரி ஜபம், இல்லம் தானம், வெள்ளிப் பாத்திரத்தில் பால் தானம் மற்றும் அரச மரத்தை 28,000 முறை வலம் வருதல்.",
    },
    {
        "id": "matula_shapa",
        "shapa_name": "Matula Shapa (Curse of Maternal Uncle)",
        "shapa_name_ta": "மாதுல சாபம் (தாய்மாமன் சாபம்)",
        "afflicted_karaka": "Mercury & 6th Lord",
        "cause_en": "Betraying or humiliating maternal uncles or their rightful dues.",
        "cause_ta": "தாய்மாமனை வஞ்சிப்பது அல்லது தாய்மாமனின் உரிமைகளைப் பறிப்பது.",
        "combinations": [
            "5th house occupied by Mercury and Jupiter along with Mars and Rahu, with Saturn in Lagna.",
            "Lagna lord and 5th lord in 5th along with Mercury, Mars, and Saturn.",
            "5th lord in Lagna, combust Saturn in 7th, and Lagna lord with Mercury.",
        ],
        "remedy_en": "Install a consecrated idol of Lord Vishnu; dig public drinking water wells, tanks, or reservoirs for the general public, and bathe at Rama Setu (Rameswaram).",
        "remedy_ta": "விஷ்ணு சிலை பிரதிஷ்டை செய்தல், பொதுமக்களுக்கு பயன்படும் குளம், கிணறு அல்லது குடிநீர் மையம் அமைத்தல், ராமேஸ்வர ராம சேதுவில் நீராடுதல்.",
    },
    {
        "id": "brahma_shapa",
        "shapa_name": "Brahma Shapa (Curse of Scholars / Brahmins)",
        "shapa_name_ta": "பிரம்ம சாபம் (வேத வித்தகர்கள் சாபம்)",
        "afflicted_karaka": "Jupiter & 9th Lord",
        "cause_en": "Arrogance of one's education/wealth leading to insulting, ridiculing, or deceiving pious teachers and spiritual scholars.",
        "cause_ta": "கல்வி அல்லது செல்வச் செருக்கால் பெரியோர்களையும், சாதுக்களையும் அவமதித்தல்.",
        "combinations": [
            "Rahu in Jupiter's signs (Sagittarius/Pisces), 5th house occupied by Jupiter, Mars, Saturn, and 9th lord in 8th.",
            "9th lord in 5th, while 5th lord is in 8th with Jupiter, Mars, and Rahu.",
            "Jupiter debilitated in Lagna or 5th, while 5th lord occupies 6, 8, or 12.",
            "5th lord Jupiter occupies 8th with malefics while Sun or Moon is 5th lord.",
        ],
        "remedy_en": "Observe Chandrayana Vrata and Brahma Koorcha Traya; donate cows facing south direction; donate five gems (Pancharatna) and gold; feed 1,000 to 10,000 Vedic scholars.",
        "remedy_ta": "சந்திராயண விரதம் மற்றும் பிரம்ம கூர்ச்ச த்ரயம், தெற்கு நோக்கி நின்று கோதானம் செய்தல், பஞ்சரத்னம் மற்றும் தங்கம் தானம், 10,000 பேருக்கு அன்னதானம்.",
    },
    {
        "id": "patni_shapa",
        "shapa_name": "Patni / Stree Shapa (Curse of Wife / Woman)",
        "shapa_name_ta": "பத்னி / ஸ்த்ரீ சாபம் (மனைவி அல்லது பெண்ணின் சாபம்)",
        "afflicted_karaka": "Venus & 7th Lord",
        "cause_en": "Cruelty, infidelity, abandonment, or causing severe mental anguish to a wedded wife or noble women.",
        "cause_ta": "மனைவியை கைவிடுதல், துரோகம் செய்தல் அல்லது பெண்களை கண்ணீர் வடிக்க வைத்தல்.",
        "combinations": [
            "7th lord in 5th in Saturn's Navamsha, while 5th lord occupies 8th.",
            "Venus in 5th, 7th lord in 8th, and Jupiter conjoined with malefics.",
            "7th house occupied by Saturn and Venus, 8th lord Sun in 5th, Rahu in Lagna.",
            "5th house is Venus's sign (Taurus/Libra) occupied by Rahu and Moon, with malefics in 12, 1, 2.",
        ],
        "remedy_en": "Perform Kanya Dana (sponsoring the wedding of an impoverished virtuous bride); donate decorated golden idols of Lakshmi-Narayana, along with 10 cows, clothes, bedding, and jewellery to deserving couples.",
        "remedy_ta": "கன்னிகாதானம் செய்து வைத்தல், லக்ஷ்மி-நாராயணன் விக்கிரகம், 10 பசுக்கள், புத்தாடைகள் மற்றும் படுக்கைகளை தம்பதிகளுக்கு தானம் செய்தல்.",
    },
    {
        "id": "preta_shapa",
        "shapa_name": "Preta Shapa (Curse of Unfulfilled Ancestors / Disembodied Spirits)",
        "shapa_name_ta": "ப்ரேத சாபம் (சாந்தியடையாத ஆத்மாக்களின் சாபம்)",
        "afflicted_karaka": "Saturn, Rahu & 5th House",
        "cause_en": "Failure to perform proper funeral rites (Karma Lopa) at death, leaving ancestral souls un-emancipated and lingering in Pretatva.",
        "cause_ta": "முன்னோர்களுக்குரிய ஈமச் சடங்குகளை (கர்மாக்களை) முறையாக செய்யாமல் விடுவதால் ஆன்மாக்கள் சாந்தியடையாமல் தவித்தல்.",
        "combinations": [
            "Saturn and Sun in 5th, waning Moon in 7th, Rahu in Lagna, and Jupiter in 12th.",
            "Malefics in Lagna, Sun in 12th, Saturn, Mars & Mercury in 5th, and 5th lord in 8th.",
            "Rahu in Lagna, Saturn in 5th, and Jupiter in 8th.",
            "Lagna occupied by Saturn and Mandi, Rahu in 5th, Sun in 8th.",
        ],
        "remedy_en": "Perform Vishnu Shraddha ceremony; take sacred Rudra Snana; donate an idol of Lord Brahma, milch cows, silver, and Blue Sapphire (Neela Ratna).",
        "remedy_ta": "விஷ்ணு சிரார்த்தம் செய்தல், ருத்ர ஸ்நானம், பிரம்மா விக்கிரகம், பசுக்கள், வெள்ளி மற்றும் நீலக்கல் (நீல ரத்தினம்) தானம் செய்தல்.",
    },
    {
        "id": "parashara_planetary_progeny_remedies",
        "shapa_name": "Parashara's 9 Planetary Mitigations for Progeny Obstacles",
        "shapa_name_ta": "பராசரரின் ஒன்பது கிரக சந்தான பரிகாரங்கள்",
        "afflicted_karaka": "Specific Obstacle-Causing Graha",
        "cause_en": "Specific planetary doshas obstructing progeny and family expansion.",
        "cause_ta": "குழந்தைப்பேற்றைத் தடுக்கும் குறிப்பிட்ட கிரக தோஷங்கள்.",
        "combinations": [
            "Sun obstacle: Recite Harivamsha Purana (Harivamsha Parayana).",
            "Moon obstacle: Perform Shiva / Ishwara Aradhana.",
            "Mars obstacle: Perform Rudrabhisheka with red flowers and ghee.",
            "Mercury obstacle: Donate curd rice placed in a Kansya (bronze) vessel.",
            "Jupiter obstacle: Feed guests and perform dedicated Pitru Pooja.",
            "Venus obstacle: Donate healthy cows to deserving recipients.",
            "Saturn obstacle: Perform Maha Mrityunjaya Japa.",
            "Rahu obstacle: Perform Kanya Dana (sponsoring a virtuous girl's wedding).",
            "Ketu obstacle: Donate cows to virtuous and spiritual souls.",
        ],
        "remedy_en": "Recitation of Valmiki Ramayana Bala Kanda (Payasa Paravrithi sarga - Dasharatha distributing payasam to his queens) and performing Santana Gopala Krishna Homa on Shravana star falling on Dwadashi tithi.",
        "remedy_ta": "ராமாயண பால காண்டத்தில் உள்ள பாயச தான சர்க்கத்தை பாராயணம் செய்தல் மற்றும் திருவோண நட்சத்திரம் துவாதசி திதியில் கூடும் நாளில் சந்தான கோபால கிருஷ்ண ஹோமம் செய்தல்.",
    },
]

# Pancha Bhoota Tatwas, Tanmatras, Abhimani Devatas, and Navadwaras
TATWAS_AND_NAVADWARAS: List[Dict[str, Any]] = [
    {
        "tatwa_en": "Akasha (Ether / Space)",
        "tatwa_ta": "ஆகாய தத்துவம்",
        "planet": "Jupiter",
        "sense_en": "Shabda (Sound / Hearing)",
        "sense_ta": "சப்தம் (கேட்கும் உணர்வு)",
        "body_parts_en": "Ears, speech organ, lightning pathways, intellectual expansion",
        "body_parts_ta": "காதுகள், வாக்கு, செவிப்பாதை",
        "abhimani_devata": "Dishanatha (Directional Lords)",
    },
    {
        "tatwa_en": "Vayu (Air)",
        "tatwa_ta": "வாயு தத்துவம்",
        "planet": "Saturn",
        "sense_en": "Sparsha (Touch)",
        "sense_ta": "ஸ்பரிசம் (தொடு உணர்வு)",
        "body_parts_en": "Skin, nervous transmission, hands, bodily motions and joints",
        "body_parts_ta": "தோல், தொடு உணர்வு, நரம்புகள், மூட்டு அசைவுகள்",
        "abhimani_devata": "Vayu & Mitra",
    },
    {
        "tatwa_en": "Agni (Fire)",
        "tatwa_ta": "தேயு / அக்னி தத்துவம்",
        "planet": "Sun & Mars",
        "sense_en": "Roopa (Sight / Form)",
        "sense_ta": "ரூபம் (பார்வை உணர்வு)",
        "body_parts_en": "Eyes, face, body heat, digestive fire (Jatharagni), blood",
        "body_parts_ta": "கண்கள், முகம், உடற்சூடு, ஜடராக்னி",
        "abhimani_devata": "Agni & Surya",
    },
    {
        "tatwa_en": "Aapa / Jala (Water)",
        "tatwa_ta": "அப்பு / ஜல தத்துவம்",
        "planet": "Moon & Venus",
        "sense_en": "Rasa (Taste)",
        "sense_ta": "ரசம் (சுவை உணர்வு)",
        "body_parts_en": "Tongue, palate, all bodily juices, plasma, urine, mucus, semen",
        "body_parts_ta": "நாக்கு, ரத்த பிளாஸ்மா, சிறுநீர், சுக்ல-சோணிதம், கபம்",
        "abhimani_devata": "Varuna & Chandra",
    },
    {
        "tatwa_en": "Prithvi (Earth)",
        "tatwa_ta": "பிருத்வி / நில தத்துவம்",
        "planet": "Mercury",
        "sense_en": "Gandha (Smell)",
        "sense_ta": "கந்தம் (நுகரும் உணர்வு)",
        "body_parts_en": "Nose, smelling power, muscular tissue, nervous system (Naramandala)",
        "body_parts_ta": "மூக்கு, நுகர்வு ஆற்றல், தசை மண்டலம், நரம்பு மண்டலம்",
        "abhimani_devata": "Vishnu & Prajapati",
    },
]

# 12 Documented Classical Case Studies from Chapters 6 & 7
CLASSICAL_CASE_STUDIES: List[Dict[str, Any]] = [
    {
        "id": "case_1_mental_aberration_liver",
        "title_en": "Case 1: Mental Aberration & Liver Disorder",
        "title_ta": "வழக்கு 1: திடீர் மனக்குழப்பம் & கல்லீரல் பாதிப்பு",
        "patient_profile": "Female, Born 12-10-1972 at 11:50 AM (Sagittarius Lagna)",
        "disease_diagnosed": "Acute Mental Aberration & Hepatic Dysregulation",
        "astrological_indicators": [
            "Ascendant lord Jupiter afflicted by conjunction with Rahu in Lagna.",
            "Mind significator Moon debilitated in Scorpio aspected by Saturn.",
            "In Navamsha, Moon is further conjoined with Rahu.",
            "Liver significator Jupiter under shadow of Rahu.",
        ],
        "dasha_timing": "Venus Mahadasha (6th lord of disease) and Moon Bhukti (debilitated mind significator).",
        "key_takeaway": "When the 6th lord dasha runs concurrently with an afflicted Moon sub-period and Jupiter is shadowed by Rahu, psychological disorientation and hepatic vulnerability manifest simultaneously.",
    },
    {
        "id": "case_2_blood_cancer",
        "title_en": "Case 2: Blood Cancer (Leukemia)",
        "title_ta": "வழக்கு 2: ரத்தப் புற்றுநோய் (Blood Cancer)",
        "patient_profile": "Male, Born 15-11-1937 at 16:09 Bangalore (Aries Lagna)",
        "disease_diagnosed": "Leukemia / Blood Cancer",
        "astrological_indicators": [
            "Aries Lagna: 8th lord Mars (Swadeha Maraka) exalted in Capricorn with 12th lord Jupiter (expansion).",
            "8th house occupied by Rahu and Mercury, disposited by blood significator Mars.",
            "Mercury and Rahu occupy the asterism of Saturn, which aspects the 6th house.",
        ],
        "dasha_timing": "Fag end of Mars Mahadasha at the Kuja-Rahu Sandhi transition point.",
        "key_takeaway": "Exalted Mars with expansive 12th lord Jupiter combined with Rahu in 8th in Saturn's star produced expansive blood cellular proliferation precisely at Kuja-Rahu Sandhi.",
    },
    {
        "id": "case_3_mental_depression",
        "title_en": "Case 3: Chronic Mental Depression & Retardation",
        "title_ta": "வழக்கு 3: நாள்பட்ட மன அழுத்தம் & மூளை பலவீனம்",
        "patient_profile": "Male, Born 03-10-1981 at 01:15 Medak (Cancer Lagna)",
        "disease_diagnosed": "Chronic Mental Depression & Imbalance",
        "astrological_indicators": [
            "Lagna lord Moon debilitated in Scorpio receiving aspect of 8th lord Saturn.",
            "Lagna (Shiro Bhava) occupied by Mars and Rahu in Ashlesha star (12th lord).",
            "Intellect significator Mercury placed in the star of Rahu.",
            "4th lord Venus posited in the star of 6th lord Jupiter.",
        ],
        "dasha_timing": "Perpetual psychological strain during Dasha of stars ruled by Rahu and Saturn.",
        "key_takeaway": "Debilitated Moon aspected by Saturn with Mars and Rahu directly in the head zone creates an enduring mental cloudiness (opacity) that defies standard therapy.",
    },
    {
        "id": "case_4_cervical_spondylitis",
        "title_en": "Case 4: Cervical Spondylitis",
        "title_ta": "வழக்கு 4: கழுத்து எலும்புத் தேய்மானம் (Cervical Spondylitis)",
        "patient_profile": "Native with severe cervical spine degeneration",
        "disease_diagnosed": "Cervical Spondylitis & Nerve Compression",
        "astrological_indicators": [
            "3rd house (neck and cervical zone) receives combined aspects of Saturn and Mars.",
            "Lagna lord is conjoined with 8th lord Mercury (ruler of nerves and spinal signals).",
            "Jupiter aspects 3rd house, preventing complete structural paralysis.",
        ],
        "dasha_timing": "Onset during operating periods of 3rd lord and aspecting Mars.",
        "key_takeaway": "Malefic aspects of Mars (inflammation) and Saturn (degeneration) on the 3rd house coupled with afflicted Mercury pinpoint spinal cervical spondylitis.",
    },
    {
        "id": "case_5_bronchial_asthma",
        "title_en": "Case 5: Chronic Bronchial Asthma",
        "title_ta": "வழக்கு 5: நாள்பட்ட ஆஸ்துமா (Bronchial Asthma)",
        "patient_profile": "Native, Born 07-04-1991 at 14:35 Bangalore (Cancer Lagna)",
        "disease_diagnosed": "Bronchial Asthma & Mucous Obstruction",
        "astrological_indicators": [
            "6th lord Jupiter is retrograde and exalted in Cancer (watery sign).",
            "Ascendant lord Moon occupies the 6th house (Deha Kashta Yoga).",
            "Saturn (chronic illness) aspects both Lagna and 6th lord Jupiter.",
        ],
        "dasha_timing": "Active Dasha periods of Jupiter and Saturn.",
        "key_takeaway": "Retrograde 6th lord exalted in a watery sign with Moon in 6th and Saturn's cold aspect creates chronic phlegmatic airway constriction.",
    },
    {
        "id": "case_6_gynaecological_uterus_removal",
        "title_en": "Case 6: Gynaecological Complications & Uterus Removal",
        "title_ta": "வழக்கு 6: கருப்பை அறுவைசிகிச்சை (Hysterectomy)",
        "patient_profile": "Female native with severe uterine pathology",
        "disease_diagnosed": "Uterine Fibroids & Surgical Hysterectomy",
        "astrological_indicators": [
            "5th lord Venus (womb) debilitated in Virgo in the star of 8th lord Sun.",
            "Rahu occupies the 5th house.",
            "6th lord Mercury exalted in Virgo with Venus, aspected by surgical Mars and chronic Saturn.",
            "Venus hemmed in Papa Kartari Yoga between Sun, waning Moon, Ketu, and Saturn.",
        ],
        "dasha_timing": "Mercury Mahadasha and Mercury Bhukti (6th lord of disease in Uccha Vargottama).",
        "key_takeaway": "Affliction to 5th house by Mars and Saturn while 5th lord is debilitated and conjoined with 6th lord compels surgical excision of the uterus.",
    },
    {
        "id": "case_7_caesarean_delivery",
        "title_en": "Case 7: Urgent Caesarean Operation",
        "title_ta": "வழக்கு 7: அவசர சிசேரியன் அறுவைசிகிச்சை",
        "patient_profile": "Female, Capricorn Lagna with obstructed labour",
        "disease_diagnosed": "Obstructed Labour & Surgical Delivery",
        "astrological_indicators": [
            "7th house (abdominal zone) occupied by Moon and aspected by surgical planet Mars.",
            "No protective aspect of Jupiter on the 7th house or on Moon.",
            "Moon (governor of natural labour pains) afflicted by Mars and Saturn.",
            "Putrakaraka Jupiter conjoined with Ketu (which acts like Mars) in 6th house.",
        ],
        "dasha_timing": "Mercury Mahadasha with Mars transit triggering the 7th house.",
        "key_takeaway": "When Mars aspects the Moon in the 7th without Jupiter's intervention, natural labour pains fail to manifest, necessitating urgent surgical intervention.",
    },
    {
        "id": "case_8_normal_delivery",
        "title_en": "Case 8: Normal Child Delivery without Surgery",
        "title_ta": "வழக்கு 8: அறுவைசிகிச்சையற்ற சுகப்பிரசவம்",
        "patient_profile": "Female, Born 11-12-1954 at 03:30 AM",
        "disease_diagnosed": "Successful Natural Delivery",
        "astrological_indicators": [
            "7th house (abdomen) occupied by its own lord Venus and exalted Saturn without Mars aspect.",
            "Moon (labour pains) is completely free from the aspect of Mars.",
            "Exalted Jupiter in 4th casts full aspect on 5th lord Sun.",
        ],
        "dasha_timing": "Mercury Mahadasha under Jupiter's protective transit.",
        "key_takeaway": "Even with badhakadhipati Saturn present, the complete absence of Mars's aspect on Moon and 7th plus Jupiter's exaltation aspect guarantees a safe natural delivery.",
    },
    {
        "id": "case_9_brain_tumour_cross_chart",
        "title_en": "Case 9: Brain Tumour & Cross-Diagnosis via Husband's Chart",
        "title_ta": "வழக்கு 9: மூளைக் கட்டி & கணவர் ஜாதக வழி கண்டறிதல்",
        "patient_profile": "Wife Born 07-09-1958 at 17:46; Husband born in Sagittarius Lagna",
        "disease_diagnosed": "Brain Tumour (Meningioma) & Successful Surgery",
        "astrological_indicators": [
            "Wife: Lagna lord Moon (head) in 11th (badhaka sthana) with Mars (boils/tumours) in Mars star.",
            "Husband's Chart: 7th house (wife) is Gemini, ruled by Mercury; Mercury conjoins Mars and Ketu in 8th from Lagna.",
            "Wife's tumour detected during husband's Jupiter dasha (Jupiter in star of 7th lord Mercury).",
        ],
        "dasha_timing": "End of Jupiter Mahadasha (Rogadhipati dasha for wife).",
        "key_takeaway": "Astrology allows precise disease cross-diagnosis: the husband's 7th house derivative (Gemini with Mercury, Mars, Ketu) accurately mirrored his wife's brain surgery.",
    },
    {
        "id": "case_10_leucoderma",
        "title_en": "Case 10: Leucoderma (Vitiligo) with Multi-Coloured Patches",
        "title_ta": "வழக்கு 10: வெண்புள்ளி நோய் (Leucoderma / Vitiligo)",
        "patient_profile": "Male, Born 15/16-07-1915 (Taurus Lagna)",
        "disease_diagnosed": "Leucoderma / Vitiligo",
        "astrological_indicators": [
            "Saturn aspects Venus (Lagna lord and Karaka for bodily radiance/beauty), creating ugliness.",
            "Mercury (ruler of skin) is conjoined with Ketu.",
            "Ketu rules 'Chitra Varna' (multi-coloured substances / depigmented white patches).",
        ],
        "dasha_timing": "Saturn Mahadasha at the Saturnine age of 60 years.",
        "key_takeaway": "Affliction of Venus by Saturn combined with Mercury and Ketu produces multi-coloured skin depigmentation known classically as Shvitra.",
    },
    {
        "id": "case_11_breast_cancer",
        "title_en": "Case 11: Breast Cancer & Mastectomy",
        "title_ta": "வழக்கு 11: மார்பகப் புற்றுநோய் & அறுவைசிகிச்சை",
        "patient_profile": "Female, Born 03-04-1972 (Aries Lagna)",
        "disease_diagnosed": "Malignant Breast Tumour & Mastectomy",
        "astrological_indicators": [
            "4th house (breasts) occupied by Ketu.",
            "4th lord Moon is debilitated in 8th (Scorpio) and receives combined aspects of Mars and badhakadhipati Saturn.",
            "Lagna lord Mars is conjoined with badhakadhipati Saturn in the 2nd house.",
        ],
        "dasha_timing": "Mercury Mahadasha (6th lord of disease and surgery).",
        "key_takeaway": "Affliction to the 4th house and 4th lord Moon by Saturn, Mars, and Ketu indicates tumours in the breast region, with surgery removing the organ.",
    },
    {
        "id": "case_12_blindness_dagdha_rashis",
        "title_en": "Case 12: Blindness via Burnt Signs (Dagdha Rashis)",
        "title_ta": "வழக்கு 12: தக்த ராசிகள் மூலம் கண் பார்வை இழப்பு",
        "patient_profile": "Female, Born 12/13-07-1984 on Chaturdashi Tithi (Aries Lagna)",
        "disease_diagnosed": "Congenital / Juvenile Blindness",
        "astrological_indicators": [
            "Born on Chaturdashi Tithi, where Gemini, Virgo, Sagittarius, and Pisces become Dagdha (Burnt) Rashis.",
            "Both eye karakas, Sun and Moon, occupy Dagdha Rashis (Gemini and Sagittarius).",
            "2nd house occupied by Rahu; 12th lord Jupiter aspected by badhakadhipati Saturn.",
            "2nd lord Venus conjoined with 6th lord Mercury and aspected by exalted Saturn.",
        ],
        "dasha_timing": "Early childhood dasha of afflicted 2nd and 12th lords.",
        "key_takeaway": "When both natural eye karakas (Sun and Moon) are trapped in Tithi Dagdha (Burnt) Rashis while 2nd and 12th houses are afflicted, irreversible loss of eyesight occurs.",
    },
]

# Dr. S. Krishna Kumar Specific Rules Registry (Yogas from Chapters 1, 2, 4)
DR_KRISHNA_KUMAR_RULES_REGISTRY: Dict[str, ClassicalMedicalRuleDefinition] = {
    "kk_theevra_buddhi": ClassicalMedicalRuleDefinition(
        id="kk_theevra_buddhi",
        name="Theevra Buddhi Yoga (Profound & Penetrating Intellect)",
        name_tamil="தீவிர புத்தி யோகம் (அசாத்திய நுண்ணறிவு)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-III",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="5th lord exalted in Navamsha and aspected by benefics, or 5th house hemmed between benefics",
        mandatory_conditions=[
            "5th lord exalted in Navamsha with benefic aspect, or 5th house in Shubha Kartari",
        ],
        traditional_interpretation=(
            "According to Dr. S. Krishna Kumar, when the lord of intelligence (5th lord) attains exaltation "
            "in Navamsha and receives benefic aspects, or the 5th bhava is hemmed between benefics, the native "
            "possesses exceptional intellectual acuity, deep analytical power, and sharp cognitive stamina."
        ),
        interpretation_tamil=(
            "டாக்டர் எஸ். கிருஷ்ண குமாரின் கூற்றுப்படி, 5-ம் அதிபதி நவாம்சத்தில் உச்சம் பெற்று சுப பார்வை பெற்றாலோ "
            "அல்லது 5-ம் வீடு சுபகர்த்தாரி யோகம் பெற்றாலோ, ஜாதகர் அசாத்திய நுண்ணறிவும், ஆழ்ந்த பகுப்பாய்வுத் திறனும் பெறுவார்."
        ),
        anatomical_system="Cerebral Cortex, Higher Mental Plane, Buddhi",
        modifiers="Jupiter or Mercury aspecting Lagna strengthens retention.",
        conflicting_indications="Combustion of 5th lord tempers cognitive endurance.",
    ),
    "kk_parengita_gnana": ClassicalMedicalRuleDefinition(
        id="kk_parengita_gnana",
        name="Parengita Gnana Yoga (Intuitive Insight into Others' Minds)",
        name_tamil="பரேங்கித ஞான யோகம் (பிறர் மனதை அறியும் நுட்பம்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-I",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="Navamshadhipati of Jupiter in Kendra/Trikona aspected by Jupiter in Rashi",
        mandatory_conditions=[
            "Dispositor of Jupiter in Navamsha occupies Kendra or Trikona and receives aspect from Jupiter",
        ],
        traditional_interpretation=(
            "The native understands the hidden aspirations and thoughts occurring within others' minds. "
            "This placement creates extraordinary psychological discernment and telepathic empathy."
        ),
        interpretation_tamil=(
            "குருவின் நவாம்ச நாதர் கேந்திர திரிகோணங்களில் அமர்ந்து ராசியில் குருவின் பார்வையைப் பெற்றால், "
            "பிறரின் மனதில் நடப்பதை முன்கூட்டியே உணரும் அரிய உளவியல் ஞானமும் உள்ளுணர்வும் உண்டாகும்."
        ),
        anatomical_system="Intuitive Neural Pathways, Empathy Centers, Pineal Axis",
        modifiers="Association with Mercury grants articulate counseling skills.",
        conflicting_indications="Rahu affliction introduces misinterpretation.",
    ),
    "kk_buddhida_yoga": ClassicalMedicalRuleDefinition(
        id="kk_buddhida_yoga",
        name="Buddhida Yoga (Psychological Advisor & Counselor Intellect)",
        name_tamil="புத்தித யோகம் (உளவியல் ஆலோசகர் திறன்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-II",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="Benefics occupy 5th house aspected by Jupiter and Venus, and 5th lord aspected by both",
        mandatory_conditions=[
            "Benefics in 5th house aspected by Jupiter and Venus",
            "5th lord receives aspect of Jupiter and Venus",
        ],
        traditional_interpretation=(
            "Traditional texts record that natives with this yoga possess the balanced temperament, patience, "
            "and discernment required to counsel, guide, and heal troubled minds as psychiatric advisors."
        ),
        interpretation_tamil=(
            "5-ம் பாவத்தில் சுபர்கள் அமர்ந்து குரு, சுக்கிரனின் பார்வையைப் பெற்று, 5-ம் அதிபதியும் இவ்விரு கிரக பார்வை பெற்றால் "
            "ஜாதகர் சிறந்த ஆலோசகராகவும், பிறர் மனக்குறைகளைத் தீர்க்கும் உளவியல் நிபுணராகவும் விளங்குவார்."
        ),
        anatomical_system="Emotional Homeostasis, Cognitive Equilibrium",
        modifiers="Exalted Venus adds compassion; exalted Jupiter adds wisdom.",
        conflicting_indications="None.",
    ),
    "kk_dharanadhi_samartha": ClassicalMedicalRuleDefinition(
        id="kk_dharanadhi_samartha",
        name="Dharanadhi Samartha Buddhi Yoga (Prodigious Memory Retention)",
        name_tamil="தாரணாதி சமர்த்த புத்தி யோகம் (மறக்க முடியாத நினைவாற்றல்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-IV",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="Navamsha lord of Jupiter in Kendra/Trikona aspected by 5th house lord",
        mandatory_conditions=[
            "Navamsha lord of Jupiter placed in Kendra or Trikona and aspected by 5th lord",
        ],
        traditional_interpretation=(
            "Confers flawless information retention, retentive memory, and rapid cognitive retrieval. "
            "The native absorbs scriptures and complex sciences without forgetting."
        ),
        interpretation_tamil=(
            "குருவின் நவாம்ச நாதர் கேந்திர அல்லது திரிகோணத்தில் இருந்து 5-ம் அதிபதியால் பார்க்கப்பட்டால், "
            "ஒருமுறை கேட்டதை மறக்காத அபார நினைவாற்றலும் (தாரணா சக்தி) விவேகமும் அமையும்."
        ),
        anatomical_system="Hippocampus, Memory Storage Centers, Synaptic Plasticity",
        modifiers="Strong Mercury adds verbal recall speed.",
        conflicting_indications="Affliction by Mandi or Gulika introduces sporadic absentmindedness.",
    ),
    "kk_buddhi_nasha": ClassicalMedicalRuleDefinition(
        id="kk_buddhi_nasha",
        name="Buddhi Nasha Yoga (Cognitive Vulnerability & Loss of Clarity)",
        name_tamil="புத்தி நாச யோகம் (புத்தி மந்தம் & தெளிவின்மை)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-V",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="5th house occupied by malefics, 5th lord with malefic in Krura Shashtyamsha, or 5th lord combust/debilitated",
        mandatory_conditions=[
            "5th house occupied by malefics and 5th lord conjoined with malefics in Krura Shashtyamsha",
        ],
        traditional_interpretation=(
            "Indicates periods of clouded judgment, cognitive exhaustion, or vulnerability to misdirection. "
            "Classical texts recommend regular Gayatri recitation and satwik routine."
        ),
        interpretation_tamil=(
            "5-ம் வீட்டில் அசுபர்கள் இருந்து, 5-ம் அதிபதியும் அசுப சேர்க்கை பெற்று குரூர ஷஷ்டியாம்சத்தில் இருந்தால், "
            "சரியான முடிவுகளை எடுக்க முடியாமல் புத்தி தடுமாறும் நிலை ஏற்படலாம்."
        ),
        anatomical_system="Cognitive Processing, Executive Function",
        modifiers="Benefic aspect from Jupiter in Kendra dissolves the afflicted condition.",
        conflicting_indications="Arishta Bhanga from Jupiter in Lagna fully cancels.",
    ),
    "kk_unmada_yoga": ClassicalMedicalRuleDefinition(
        id="kk_unmada_yoga",
        name="Unmada Yoga (Extreme Emotional Surge & High Blood Pressure)",
        name_tamil="உன்மாத யோகம் (அதி தீவிர உணர்ச்சி & ரத்த அழுத்தப் போக்கு)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-VIII",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="Jupiter in Lagna and Mars in 7th, or Saturn + 2nd lord + Mars conjoined",
        mandatory_conditions=[
            "Jupiter in Janma Lagna and Mars in 7th house, or Saturn conjoining Mars and 2nd lord",
        ],
        traditional_interpretation=(
            "Traditional texts record that Mars in the 7th opposite Jupiter in Lagna produces excessive "
            "emotional heat, intense passion, and predisposition to blood pressure or bilious (Pitta) agitation."
        ),
        interpretation_tamil=(
            "லக்னத்தில் குருவும் 7-ல் செவ்வாயும் அமைந்தாலோ, அல்லது 2-ம் அதிபதியுடன் சனி-செவ்வாய் கூடினாலோ "
            "அதி தீவிர உணர்ச்சிவசப்படுதல், பித்த உஷ்ணம் மற்றும் ரத்த அழுத்த மாற்றங்கள் ஏற்பட வாய்ப்புள்ளது."
        ),
        anatomical_system="Neuro-Vascular Axis, Blood Pressure, Amygdala Reactivity",
        modifiers="Benefic Moon in Kendra calms emotional surges.",
        conflicting_indications="Jupiter's strong dignity promotes eventual self-mastery.",
    ),
    "kk_mati_bhramana": ClassicalMedicalRuleDefinition(
        id="kk_mati_bhramana",
        name="Mati Bhramana Yoga (Mental Disorientation / Wavering State)",
        name_tamil="மதி பிரமண யோகம் (மனக் குழப்பம் & தெளிவற்ற சிந்தனை)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-X",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="Krishna Paksha Moon conjoined with Saturn in 12th house",
        mandatory_conditions=[
            "Waning Moon (Krishna Paksha) conjoins Saturn in the 12th house",
        ],
        traditional_interpretation=(
            "Waning Moon conjoined with Saturn in the 12th house (Vyaya Bhava) scatters mental focus and "
            "creates melancholic moods, sensory disorientation, or sleep disturbances."
        ),
        interpretation_tamil=(
            "தேய்பிறைச் சந்திரன் 12-ம் வீட்டில் சனியுடன் இணையும் போது மனக்குழப்பம், தூக்கமின்மை, தனிமை விரும்புதல் "
            "மற்றும் தெளிவற்ற சிந்தனைப் போக்குகள் ஏற்படும் என டாக்டர் கிருஷ்ண குமார் விளக்குகிறார்."
        ),
        anatomical_system="Subconscious Processing, Circadian Rhythm, Neuro-transmitter Balance",
        modifiers="Aspect of Jupiter or Venus provides emotional stability.",
        conflicting_indications="Benefic placements in 4th house anchor the psyche.",
    ),
    "kk_krodha_yoga": ClassicalMedicalRuleDefinition(
        id="kk_krodha_yoga",
        name="Krodha Yoga (Volatile Temperament & Reactive Anger)",
        name_tamil="குரோத யோகம் (தீவிர கோப உணர்ச்சி & உணர்ச்சி வேகம்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 18-XI",
        category="Manasika & Buddhi Yogas",
        system="vedic",
        required_placements="2nd lord malefic conjoined with Gulika or in debilitated / inimical Navamsha",
        mandatory_conditions=[
            "2nd lord is a natural malefic conjoined with Gulika or in Papakartari / Neecha Navamsha",
        ],
        traditional_interpretation=(
            "Affliction to the 2nd house of speech and facial expression by malefic combinations produces a fiery, "
            "harsh, and reactive temper that elevates vascular tension."
        ),
        interpretation_tamil=(
            "2-ம் அதிபதி அசுபராகி குளிகனுடன் கூடினாலோ அல்லது நீச நவாம்சத்தில் இருந்தாலோ கடும் கோபமும், உணர்ச்சி வேகமும் "
            "வெளிப்படும்; இதனால் ரத்த நாளங்களில் உஷ்ணம் ஏறும்."
        ),
        anatomical_system="Vocal Expression, Sympathetic Nervous Surge, Facial Vasculature",
        modifiers="Benefic Jupiter aspect softens speech and cools temperament.",
        conflicting_indications="None.",
    ),
    "kk_shiro_vyadhi": ClassicalMedicalRuleDefinition(
        id="kk_shiro_vyadhi",
        name="Shiro Vyadhi Yoga (Cranial & Head Region Vulnerability)",
        name_tamil="சிரோ வியாதி யோகம் (தலை மற்றும் மண்டை ஓட்டுப் பகுதி கவனம்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-A",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Lagna lord and 6th lord conjoined with Rahu or Ketu",
        mandatory_conditions=[
            "Lagna lord and 6th lord conjoin Rahu or Ketu",
        ],
        traditional_interpretation=(
            "When the Lagna lord and 6th lord combine with nodal shadow planets (Rahu/Ketu), the cranial "
            "area is sensitive to headaches, neural tension, or subtle Vata-related disturbances."
        ),
        interpretation_tamil=(
            "லக்னாதிபதியும் 6-ம் அதிபதியும் ராகு அல்லது கேதுவுடன் இணையும் போது தலைவலி, மண்டை ஓட்டு நரம்பு அழுத்தம் "
            "அல்லது வாதக் கோளாறுகள் ஏற்பட வாய்ப்புள்ளது."
        ),
        anatomical_system="Cranial Cavity, Brain Vasculature, Head Nerves",
        modifiers="Jupiter's aspect on Lagna shields the brain.",
        conflicting_indications="Sun exalted in 1st overrides head afflictions.",
    ),
    "kk_nethra_roga": ClassicalMedicalRuleDefinition(
        id="kk_nethra_roga",
        name="Nethra Roga Yoga (Ocular Sensitivity & Vision Care)",
        name_tamil="நேத்ர ரோக யோகம் (கண் பார்வை & விழித்திரை உணர்திறன்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-B",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="2nd lord conjoins Saturn, Mars, and Mandi, or Sun/Moon in 6/8/12",
        mandatory_conditions=[
            "2nd lord conjoined with Saturn, Mars, or Mandi, or eye karakas Sun/Moon in Dusthanas",
        ],
        traditional_interpretation=(
            "Traditional medical astrology links the 2nd and 12th houses with the right and left eyes. "
            "Affliction by Saturn, Mars, or Mandi necessitates routine ocular care and glare protection."
        ),
        interpretation_tamil=(
            "2-ம் அதிபதி சனி, செவ்வாய், மாந்தியுடன் கூடினாலோ அல்லது சூரியன்/சந்திரன் மறைவு ஸ்தானங்களில் இருந்தாலோ "
            "கண் பார்வை உணர்திறன், ஒளி மங்குதல் போன்றவைகளில் கூடுதல் கவனிப்பு தேவை."
        ),
        anatomical_system="Ocular System, Retina, Optic Nerves (Right & Left Eyes)",
        modifiers="Venus or Jupiter in friendly houses preserves vision.",
        conflicting_indications="Benefic aspects on 2nd and 12th houses mitigate eye strain.",
    ),
    "kk_badhira_yoga": ClassicalMedicalRuleDefinition(
        id="kk_badhira_yoga",
        name="Badhira Yoga (Auditory System & Ear Sensitivity)",
        name_tamil="பதிர யோகம் (செவித்திறன் & காது நரம்புகள் கவனம்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-D",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="3rd house occupied/aspected by malefics, or Mercury and 6th lord aspected by malefics",
        mandatory_conditions=[
            "3rd house conjoined or aspected by malefics, or 3rd lord in Krura Shashtyamsha",
        ],
        traditional_interpretation=(
            "The 3rd and 11th houses govern the right and left ears. Affliction to the 3rd house or Mercury "
            "(ruler of communication organs) suggests susceptibility to ear infections or auditory sensitivity."
        ),
        interpretation_tamil=(
            "3-ம் பாவத்தில் அசுபர்கள் இருந்தாலோ அல்லது புதனும் 6-ம் அதிபதியும் அசுப பார்வை பெற்றாலோ செவிப்பாதை, "
            "காது நரம்புகளில் கூடுதல் கவனம் செலுத்துவது நலம்."
        ),
        anatomical_system="Auditory Canals, Tympanic Membrane, Cochlear Nerves",
        modifiers="Jupiter (Karaka for hearing) in Kendra preserves auditory sharpness.",
        conflicting_indications="Benefic aspect on 3rd house protects ears.",
    ),
    "kk_dantha_roga": ClassicalMedicalRuleDefinition(
        id="kk_dantha_roga",
        name="Dantha Roga Yoga (Dental Integrity & Oral Care)",
        name_tamil="தந்த ரோக யோகம் (பற்கள் ஆரோக்கியம் & ஈறுகள் பராமரிப்பு)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-H",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="2nd lord with Rahu in 6th, or Rahu/Ketu in 2nd/6th, or Moon+Saturn+Sun in 7th",
        mandatory_conditions=[
            "2nd lord conjoins Rahu in 6th, or Rahu/Ketu in 6th, or 2nd house afflicted by malefics",
        ],
        traditional_interpretation=(
            "The 2nd house and Saturn govern bones, teeth, and gums. Nodal contact with the 2nd lord or 6th house "
            "advises proactive dental hygiene and enamel protection against decay."
        ),
        interpretation_tamil=(
            "2-ம் அதிபதி ராகுவுடன் 6-ல் இருந்தாலோ அல்லது ராகு/கேது 6-ல் நின்றாலோ பற்கள் சொத்தை, ஈறு கோளாறுகள் "
            "ஏற்படக்கூடும் என்பதால் தொடர் பல் பராமரிப்பு நல்லது."
        ),
        anatomical_system="Dentition, Enamel, Periodontal Tissue, Gums",
        modifiers="Benefic aspect on 2nd house ensures strong teeth.",
        conflicting_indications="Jupiter in 2nd gives radiant, aligned teeth.",
    ),
    "kk_gala_roga": ClassicalMedicalRuleDefinition(
        id="kk_gala_roga",
        name="Gala Roga Yoga (Throat & Vocal Axis Sensitivity)",
        name_tamil="கள ரோக யோகம் (தொண்டை & குரல்வளை உணர்திறன்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-G",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="3rd lord conjoined with Rahu and Mercury",
        mandatory_conditions=[
            "3rd lord conjoined with Rahu and Mercury",
        ],
        traditional_interpretation=(
            "The 3rd house and Mercury rule the neck, vocal cords, and larynx. Rahu's conjunction with the 3rd "
            "lord and Mercury indicates sensitivity to throat irritation, pharyngitis, or voice strain."
        ),
        interpretation_tamil=(
            "3-ம் அதிபதி ராகு மற்றும் புதனுடன் கூடினால் தொண்டை அழற்சி, குரல்வளை சோர்வு மற்றும் சளித் தொந்தரவுகள் "
            "ஏற்படலாம் என மூல நூல்கள் கூறுகின்றன."
        ),
        anatomical_system="Throat, Larynx, Vocal Cords, Pharynx",
        modifiers="Warm herbal drinks and voice rest support the vocal axis.",
        conflicting_indications="Venus in 2nd in own sign protects voice quality.",
    ),
    "kk_hridaya_roga": ClassicalMedicalRuleDefinition(
        id="kk_hridaya_roga",
        name="Hridaya Roga Yoga (Cardiovascular & Heart Sensitivity)",
        name_tamil="ஹிருதய ரோக யோகம் (இதயம் மற்றும் மார்புப் பகுதி கவனம்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-Y",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="4th lord in Dusthana, Sun and Moon weak aspected by malefics",
        mandatory_conditions=[
            "4th lord occupies 6, 8, or 12, with Sun and Moon afflicted by Saturn or Mars",
        ],
        traditional_interpretation=(
            "Dr. Krishna Kumar highlights that the 4th house and Sun rule the heart. Mars aspect brings acute "
            "or sudden inflammatory strain, while Saturn aspect causes chronic gradual weakening that requires "
            "paced lifestyle management."
        ),
        interpretation_tamil=(
            "4-ம் அதிபதி மறைவிடத்தில் இருந்து, சூரியன் மற்றும் சந்திரன் சனி-செவ்வாய் பார்வை பெற்றால் இதயம் "
            "மற்றும் ரத்த ஓட்டத்தில் கூடுதல் கவனம் செலுத்தி மிதமான வாழ்க்கை முறையைப் பின்பற்ற வேண்டும்."
        ),
        anatomical_system="Cardiovascular System, Heart Muscle, Aorta, Thoracic Circulation",
        modifiers="Jupiter in 4th or aspecting 4th lord acts as supreme cardiac protection.",
        conflicting_indications="Strong Sun in Lagna or 10th strengthens cardiac vitality.",
    ),
    "kk_mutra_krichra": ClassicalMedicalRuleDefinition(
        id="kk_mutra_krichra",
        name="Mutra Krichra Yoga (Urinary Tract & Renal Fluid Regulation)",
        name_tamil="மூத்திரக் கிருச்சிர யோகம் (சிறுநீரக மண்டலம் & நீர் சமநிலை)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-K",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Moon in watery sign, Moon's dispositor in 6th watery sign aspected by Mercury",
        mandatory_conditions=[
            "Moon in watery sign (Cancer, Scorpio, Pisces) and its dispositor in 6th in watery sign with Mercury aspect",
        ],
        traditional_interpretation=(
            "Watery sign influences on the 6th house with lunar involvement point toward fluid retention, "
            "urinary tract sensitivity, or predisposition to urinary stone formation (Ashmari)."
        ),
        interpretation_tamil=(
            "சந்திரன் நீர் ராசியில் இருந்து அதன் அதிபதி 6-ல் நீர் ராசியில் புதனின் பார்வை பெற்றால், சிறுநீரகப் பாதை "
            "மற்றும் நீர்ச்சத்து சமநிலையில் கூடுதல் விழிப்புணர்வு தேவை."
        ),
        anatomical_system="Renal Excretory Tract, Kidneys, Bladder, Fluid Osmosis",
        modifiers="High hydration and tender coconut water mitigate urinary heat.",
        conflicting_indications="Venus well-placed in Kendra protects kidney function.",
    ),
    "kk_arsha_roga": ClassicalMedicalRuleDefinition(
        id="kk_arsha_roga",
        name="Arsha Roga Yoga (Ano-Rectal & Haemorrhoidal Care)",
        name_tamil="அர்ச ரோக யோகம் (மூலம் மற்றும் மலக்குடல் பராமரிப்பு)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-X",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Saturn in Lagna and Mars in 7th, or 8th lord malefic in 7th without benefic aspect",
        mandatory_conditions=[
            "Saturn in Lagna and Mars in 7th, or 8th lord malefic placed in 7th without benefic aspect",
        ],
        traditional_interpretation=(
            "The 8th house governs excretory and ano-rectal organs. When Saturn and Mars interact across the 1st "
            "and 7th or afflict the 8th lord, classical texts highlight dietary fibre and cooling habits to avoid piles."
        ),
        interpretation_tamil=(
            "லக்னத்தில் சனியும் 7-ல் செவ்வாயும் நின்றாலோ அல்லது 8-ம் அதிபதி அசுபராகி 7-ல் நின்றாலோ மூல நோய் மற்றும் "
            "மலச்சிக்கல் ஏற்படாமல் இருக்க நார்ச்சத்து மிக்க உணவும், நீர்ச்சத்தும் அவசியம்."
        ),
        anatomical_system="Ano-Rectal Canal, Haemorrhoidal Veins, Lower Bowel",
        modifiers="Cooling buttermilk and satwik diet prevent rectal irritation.",
        conflicting_indications="Jupiter aspect on 8th house dissolves chronic distress.",
    ),
    "kk_deha_sthoulya": ClassicalMedicalRuleDefinition(
        id="kk_deha_sthoulya",
        name="Deha Sthoulya Yoga (Predisposition to Heavy / Corpulent Physique)",
        name_tamil="தேக ஸ்தௌல்ய யோகம் (உடற்பருமன் & கொழுப்பு திசு அதிகரிப்பு)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 19-R",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Lagna in watery sign occupied by benefics, or Jupiter in watery sign aspecting Lagna",
        mandatory_conditions=[
            "Ascendant in a watery sign (Cancer, Scorpio, Pisces) with benefics, or Jupiter posited in watery Lagna",
        ],
        traditional_interpretation=(
            "Benefics, especially Jupiter, occupying or aspecting watery ascendants expand adipose tissue (Medas) "
            "and bodily fluids, creating a large, well-nourished, or corpulent physical frame."
        ),
        interpretation_tamil=(
            "நீர் ராசி லக்னமாகி அங்கு சுபர்கள் இருந்தாலோ, அல்லது குரு நீர் ராசியில் இருந்து லக்னத்தைப் பார்த்தாலோ "
            "உடலில் கொழுப்பு திசுக்கள் (மேதஸ்) கூடி பருமனான உடலமைப்பு அமையும்."
        ),
        anatomical_system="Adipose Tissue (Medas), Endocrine Metabolism, Lymphatic Volume",
        modifiers="Active physical exertion and light diet balance bodily bulk.",
        conflicting_indications="Saturn in Lagna produces a lean, slim frame (Krishathwa).",
    ),
    "kk_mrityunjaya_resuscitation": ClassicalMedicalRuleDefinition(
        id="kk_mrityunjaya_resuscitation",
        name="Mrityunjaya Resuscitation Yoga (Overcoming Critical Health Crises)",
        name_tamil="மிருத்யுஞ்சய மீட்சி யோகம் (தீவிர உடல் ஆபத்துகளிலிருந்து மீண்டு வருதல்)",
        source="A Book on Medical Astrology (Dr. S. Krishna Kumar)",
        chapter_verse="Chapter 1, Section 20-ii",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="8th lord occupies Kendra along with Saturn",
        mandatory_conditions=[
            "8th lord occupies a Kendra (1st, 4th, 7th, 10th) conjoined with Saturn",
        ],
        traditional_interpretation=(
            "Dr. Krishna Kumar highlights a miraculous formula: 'Having given up hopes the native overcomes "
            "the acute seriousness and comes back to life.' When the 8th lord is in Kendra with Saturn, "
            "formidable longevity reserves allow recovery even from near-fatal conditions."
        ),
        interpretation_tamil=(
            "டாக்டர் கிருஷ்ண குமார் ஒரு அரிய சூத்திரத்தை சுட்டிக்காட்டுகிறார்: 8-ம் அதிபதி சனியுடன் கூடி கேந்திரத்தில் "
            "அமைந்தால், மருத்துவ ரீதியாக நம்பிக்கையற்ற நிலையிலும் கூட ஜாதகர் அபாயத்தை வென்று மீண்டு வந்து நீண்ட ஆயுள் பெறுவார்."
        ),
        anatomical_system="Autonomic Life Reserves, Cellular Vitality, Longevity Axis",
        modifiers="Jupiter's trinal aspect guarantees prompt recuperation.",
        conflicting_indications="None; celebrated life-restoring combination.",
    ),
}


# ===========================================================================
# Dr. S. S. Chatterjee "Advance Medical Astrology" Specific Research Rules
# ===========================================================================

DR_CHATTERJEE_GOLDEN_RULES_REGISTRY: Dict[str, ClassicalMedicalRuleDefinition] = {
    "chatterjee_death_point_saturn": ClassicalMedicalRuleDefinition(
        id="chatterjee_death_point_saturn",
        name="Dr. Chatterjee's Death Point Triggered by Saturn Aspect",
        name_tamil="டாக்டர் சட்டர்ஜியின் மிருத்யு புள்ளி மீது சனியின் பார்வை",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Timing Diseases & Cosmic Influences (1989)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Transit Saturn casting aspect (0°, 60°, 180°, 270°) on Death Point (Asc+Sun+Moon+Jup mod 360°)",
        mandatory_conditions=[
            "Calculate Death Point: (Ascendant + Sun + Moon + Jupiter) % 360",
            "Transit Saturn aspects this zodiac degree within orb",
        ],
        traditional_interpretation=(
            "Dr. S. S. Chatterjee discovered in 1989 that the mathematical Death Point (Ascendant + Sun + Moon + Jupiter) "
            "acts as the primary chidra-sensitive degree of the zodiac. When Saturn in transit casts its 1st, 3rd, 7th, "
            "or 10th aspect upon this sensitive degree, the native undergoes critical constitutional crises or serious health debacles."
        ),
        interpretation_tamil=(
            "டாக்டர் எஸ். எஸ். சட்டர்ஜி கண்டறிந்த சூத்திரப்படி, (லக்னம் + சூரியன் + சந்திரன் + குரு) பாகைகளின் கூட்டுத்தொகை "
            "மிருத்யு புள்ளியாகும். கோச்சார சனி பகவான் தனது பார்வை (1, 3, 7, 10-ஆம் பார்வைகள்) மூலம் இந்த புள்ளியைத் தொடும் போது "
            "உடலில் தீவிர உடல்நலக் குறைவும் ஆரோக்கியப் போராட்டங்களும் ஏற்படுவதாக நிறுவப்பட்டுள்ளது."
        ),
        anatomical_system="Systemic Vital Force, Longevity Axis, Cellular Immunity",
        modifiers="Transit Jupiter casting trine or conjunction to Death Point neutralizes acute crises.",
        conflicting_indications="Strong Parijata Yoga or benefic Kendra dominance offers formidable resistance.",
    ),
    "chatterjee_parijata_longevity": ClassicalMedicalRuleDefinition(
        id="chatterjee_parijata_longevity",
        name="Parijata Yoga & Kendra-Benefic Longevity Shield",
        name_tamil="பாரிஜாத யோகம் & கேந்திர சுபர்கள் அருளும் தீர்க்காயுள்",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapters 1 & 4, Longevity Principles (Exp. Prof. Galgali & Dr. Khorana)",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Lagna lord dispositor in Kendra/Trikona, benefics in Kendras, malefics relegated to 3rd or 11th",
        mandatory_conditions=[
            "Benefics occupy angles (1, 4, 7, 10) or trines (1, 5, 9)",
            "Malefics occupy 3rd or 11th houses",
        ],
        traditional_interpretation=(
            "Dr. Chatterjee emphasizes that those who possess natural benefics (Jupiter, Venus, Mercury, waxing Moon) in "
            "Kendras/Trikonas while malefics (Rahu, Ketu, Mars, Saturn, Sun) occupy either the 3rd or 11th house enjoy "
            "remarkable stamina, freedom from hospitalizations, and live an active, disease-free life past 80 years."
        ),
        interpretation_tamil=(
            "கேந்திர மற்றும் திரிகோணங்களில் சுபக் கிரகங்களும், 3 அல்லது 11-ஆம் வீடுகளில் அசுபக் கிரகங்களும் அமைந்தால், "
            "ஜாதகர் அசாத்திய நோய் எதிர்ப்பு சக்தியும், 80 ஆண்டுகளைத் தாண்டி ஆரோக்கியமாக வாழும் தீர்க்காயுள் யோகத்தையும் பெறுவார்."
        ),
        anatomical_system="Full Constitutional Immunity, Autonomic Homeostasis, Ageless Living",
        modifiers="Exaltation of Lagnesha elevates vitality to sovereign levels.",
        conflicting_indications="None; celebrated protective shield against disease.",
    ),
    "chatterjee_diabetes_mellitus": ClassicalMedicalRuleDefinition(
        id="chatterjee_diabetes_mellitus",
        name="Diabetes Mellitus (Madhumeha) Pancreatic-Glycemic Imbalance",
        name_tamil="மதுமேகம் / நீரிழிவு நோய் (கணைய-சர்க்கரை சமநிலையின்மை)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Mechanisms of Diabetes Mellitus (Exp. 1 & 4)",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Venus afflicted by malefics; Virgo (6th sign) afflicted; 6/12 axis strained by Mars/Saturn; Jupiter weak",
        mandatory_conditions=[
            "Venus (endocrine regulator) or 6th house/Virgo afflicted by Saturn, Mars, or Nodes",
            "Jupiter (glycogen regulator) weak or in enemy camp",
        ],
        traditional_interpretation=(
            "Venus rules all glandular and endocrine functions, while Jupiter rules liver glycogen storage and systemic recovery. "
            "Virgo is the 6th sign representing the pancreas and intestines. When Venus, Virgo, and the 6th house are afflicted by "
            "Saturn, Mars, or Rahu while Jupiter is weakened, the body struggles to maintain blood glucose balance."
        ),
        interpretation_tamil=(
            "சுக்கிரன் நாளமில்லா சுரப்பிகளையும், குரு கல்லீரலின் சர்க்கரை சேமிப்பையும், கன்னி ராசி கணையத்தையும் குறிக்கின்றன. "
            "இவை சனி, செவ்வாய், ராகுவின் தாக்கத்தால் பலவீனமடையும் போது சர்க்கரை சமநிலையின்மை மற்றும் நீரிழிவு பாதிப்பு ஏற்படலாம்."
        ),
        anatomical_system="Pancreatic Islets of Langerhans, Insulin Regulation, Renal Glycemic Excretion",
        modifiers="Dietary intake of germinated grams, neem leaves, and karela juice balances pitta-kapha metabolism.",
        conflicting_indications="Jupiter aspecting Lagna or 6th house provides strong metabolic stabilization.",
    ),
    "chatterjee_rahu_5th_gastro": ClassicalMedicalRuleDefinition(
        id="chatterjee_rahu_5th_gastro",
        name="Rahu in 5th House (Vata Abdominal Spasms & Gastroenteritis)",
        name_tamil="5-ஆம் பாவத்தில் ராகு (வாயுத் தொல்லை & தீவிர குடல் அழற்சி)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 1",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Rahu occupies the 5th house from Lagna",
        mandatory_conditions=["Rahu in 5th house"],
        traditional_interpretation=(
            "As Rahu is the supreme Karaka for Vata (wind) and the 5th house governs the belly, epigastrium, "
            "and digestive enzymatic organs, Rahu in the 5th causes severe windy diseases, flatulence, and acute gastroenteritis."
        ),
        interpretation_tamil=(
            "ராகு வாயுவின் காரகனாகவும், 5-ம் பாவம் வயிற்றுப் பகுதியை ஆளுவதாலும், 5-ல் ராகு அமர்வது வயிற்றுப் பொருமல், வாயுத் தொல்லை "
            "மற்றும் தீவிர இரைப்பை குடல் அழற்சியைத் தரும்."
        ),
        anatomical_system="Abdominal Cavity, Epigastrium, Gastric Mucosa, Vata Balance",
        modifiers="Aspect of Jupiter calms gastrointestinal turbulence.",
        conflicting_indications="5th lord strong in Kendra prevents severe inflammation.",
    ),
    "chatterjee_saturn_5th_dyspepsia": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_5th_dyspepsia",
        name="Saturn in 5th House (Vata-Kapha Dyspepsia & Sluggish Agni)",
        name_tamil="5-ஆம் பாவத்தில் சனி (செரிமான மந்தம் & அஜீரணக் கோளாறு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 2",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Saturn occupies the 5th house from Lagna",
        mandatory_conditions=["Saturn in 5th house"],
        traditional_interpretation=(
            "As Saturn is the significator of cold Kapha and dry Vata, its placement in the 5th house chills "
            "the digestive fire (Mandagni), predisposing the native to chronic dyspepsia, sluggish metabolism, and abdominal bloating."
        ),
        interpretation_tamil=(
            "சனி குளிர்ச்சியான கப மற்றும் வறண்ட வாயு காரகனாக இருப்பதால், 5-ல் அமைவது ஜடராக்னியை மந்தமாக்கி, நீண்டகால செரிமானக் குறைபாட்டையும் "
            "அஜீரணத்தையும் ஏற்படுத்தும்."
        ),
        anatomical_system="Gastric Fire (Jatharagni), Stomach, Duodenal Digestion",
        modifiers="Mars aspect introduces bilious heat into cold digestion.",
        conflicting_indications="Saturn in own sign Capricorn/Aquarius or exalted in Libra acts favorably.",
    ),
    "chatterjee_sun_rahu_4th_skin": ClassicalMedicalRuleDefinition(
        id="chatterjee_sun_rahu_4th_skin",
        name="Sun and Rahu in 4th House (Atrophic Skin & Tissue Degeneration)",
        name_tamil="4-ஆம் பாவத்தில் சூரியன்-ராகு (தோல் வறட்சி & சுருக்கங்கள்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 12",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun and Rahu conjoined in the 4th house from Lagna",
        mandatory_conditions=["Sun and Rahu in 4th house"],
        traditional_interpretation=(
            "The combination of the scorching Sun with eclipse-causing Rahu in the 4th house causes atrophic conditions "
            "of the skin, wherein the dermal layers become prematurely dry, inelastic, wrinkled, and sensitive to environmental toxins."
        ),
        interpretation_tamil=(
            "4-ஆம் பாவத்தில் சூரியனும் ராகுவும் இணைவது தோலின் ஈரப்பதத்தை வற்றச் செய்து, முன்கூட்டியே சுருக்கங்கள், வறட்சி "
            "மற்றும் தோல் மெலிந்து போதல் போன்ற குறைபாடுகளை ஏற்படுத்தும்."
        ),
        anatomical_system="Dermal Elasticity, Subcutaneous Tissue, Thoracic Blood Vessel Tone",
        modifiers="Benefic aspect from Venus or Moon restores dermal moisture.",
        conflicting_indications="Jupiter in Kendra protects cellular vitality.",
    ),
    "chatterjee_venus_saturn_8th_chronic": ClassicalMedicalRuleDefinition(
        id="chatterjee_venus_saturn_8th_chronic",
        name="Venus and Saturn in 8th House (Protracted Chronic Ailments & Costly Recovery)",
        name_tamil="8-ஆம் பாவத்தில் சுக்கிரன்-சனி (நீண்டகால உபாதைகள் & தாமத மீட்சி)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 13",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Venus and Saturn conjoined in the 8th house from Lagna",
        mandatory_conditions=["Venus and Saturn in 8th house"],
        traditional_interpretation=(
            "In case of illness or injury, recovery is exceptionally slow and involves substantial financial outlay. "
            "The 8th house represents longevity reserves and cellular immunity; Saturn-Venus here causes lingering chronic tendencies."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் சுக்கிரனும் சனியும் இணைவது நோய் அல்லது காயங்களிலிருந்து மீண்டு வர நீண்ட கால அவகாசத்தையும், "
            "அதிக மருத்துவச் செலவுகளையும் ஏற்படுத்தும் அமைப்பாகும்."
        ),
        anatomical_system="Deep Tissue Immunity, Excretory Tract, Venous Circulation",
        modifiers="Saturn in Libra (exaltation) preserves longevity despite slow recuperation.",
        conflicting_indications="Benefic aspects from Jupiter hasten recovery time.",
    ),
    "chatterjee_mars_venus_8th_urogenital": ClassicalMedicalRuleDefinition(
        id="chatterjee_mars_venus_8th_urogenital",
        name="Mars and Venus in 8th House (Urogenital & Reproductive Vulnerability)",
        name_tamil="8-ஆம் பாவத்தில் செவ்வாய்-சுக்கிரன் (இனப்பெருக்க மற்றும் சிறுநீரக உணர்திறன்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 14",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars and Venus conjoined in the 8th house from Lagna",
        mandatory_conditions=["Mars and Venus in 8th house"],
        traditional_interpretation=(
            "Mars represents heat, blood, and inflammation, while Venus rules reproductive organs and bodily fluids. "
            "Their union in the 8th house indicates urogenital inflammatory conditions, sexually transmitted vulnerabilities, or surgical needs."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் செவ்வாயும் சுக்கிரனும் இணைவது பிறப்புறுப்பு மற்றும் சிறுநீரகப் பாதைகளில் அழற்சி, சூடு சார்ந்த தொந்தரவுகள் "
            "மற்றும் அறுவை சிகிச்சைக்கான சாத்தியங்களைக் குறிக்கும்."
        ),
        anatomical_system="Reproductive Vasculature, Gonads, Urogenital Mucosa",
        modifiers="Cooling diet and hydration mitigate Pitta-Shukra flare-ups.",
        conflicting_indications="Jupiter aspecting 8th house neutralizes infectious tendencies.",
    ),
    "chatterjee_mars_saturn_8th_digestive": ClassicalMedicalRuleDefinition(
        id="chatterjee_mars_saturn_8th_digestive",
        name="Mars and Saturn in 8th House (Digestive Turmoil, Waist Adiposity & Fracture Risk)",
        name_tamil="8-ஆம் பாவத்தில் செவ்வாய்-சனி (செரிமானக் கோளாறு, இடுப்புச் சதை & எலும்பு முறிவு அபாயம்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 15",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars and Saturn conjoined in the 8th house from Lagna",
        mandatory_conditions=["Mars and Saturn in 8th house"],
        traditional_interpretation=(
            "Dr. Chatterjee highlights that natives with Mars and Saturn in the 8th house are vulnerable to severely disturbed "
            "digestive systems, abnormal accumulation of fat around the waist and belly, and risk of bone fractures from sudden falls."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் செவ்வாயும் சனியும் இணைவது சீரற்ற செரிமான மண்டலம், இடுப்பு மற்றும் வயிற்றில் கொழுப்பு சேருதல், "
            "மற்றும் எதிர்பாராத வீழ்ச்சிகளால் எலும்பு முறிவு ஏற்படும் அபாயத்தைக் குறிக்கும்."
        ),
        anatomical_system="Lower Abdomen, Waist Adipose Tissue, Pelvic Skeletal Structure",
        modifiers="Careful gait and core exercises strengthen bone-ligament stability.",
        conflicting_indications="Strong Lagna lord in Kendra eliminates catastrophic falls.",
    ),
    "chatterjee_saturn_rahu_8th_obesity": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_rahu_8th_obesity",
        name="Saturn and Rahu in 8th House (Lower Body Adiposity & Sluggish Recuperation)",
        name_tamil="8-ஆம் பாவத்தில் சனி-ராகு (கீழுடல் பருமன் & மந்தமான நோய் எதிர்ப்பு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 17",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn and Rahu conjoined in the 8th house from Lagna",
        mandatory_conditions=["Saturn and Rahu in 8th house"],
        traditional_interpretation=(
            "The 8th house rules systemic immunity and cellular resistance. Saturn and Rahu together in the 8th cause the lower body "
            "(hips, thighs, pelvic basin) to become disproportionately overweight, accompanied by sluggish immune recovery."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் சனியும் ராகுவும் கூடி நிற்பது கீழ் உடலில் அதிக சதை சேருவதையும், நோய் தாக்குதலுக்குப் பிறகு உடலின் "
            "மீட்சித் திறன் மிக மந்தமாக இருப்பதையும் குறிக்கும்."
        ),
        anatomical_system="Pelvic Basin, Lower Extremity Lymphatics, Cellular Immunity",
        modifiers="Daily aerobic exercise and avoidance of stale foods stimulates metabolism.",
        conflicting_indications="Aspect of benefic Jupiter provides vital resilience.",
    ),
    "chatterjee_saturn_ketu_8th_gangrene": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_ketu_8th_gangrene",
        name="Saturn and Ketu in 8th House (Septic Complications & Delayed Healing)",
        name_tamil="8-ஆம் பாவத்தில் சனி-கேது (சீழ் பிடித்தல் & மெதுவான காயம் ஆறுதல்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 18",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn and Ketu conjoined in the 8th house from Lagna",
        mandatory_conditions=["Saturn and Ketu in 8th house"],
        traditional_interpretation=(
            "Saturn and Ketu in the 8th house predispose open wounds or tissue traumas to become septic or heal very slowly. "
            "Compared to Rahu, Ketu-Saturn requires extraordinary hygiene and protracted antibiotic/antiseptic care."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் சனியும் கேதுவும் இணைந்தால் காயங்கள் சீழ் பிடிக்கும் அபாயமும், திசுக்கள் ஆறுவதில் மிகுந்த காலதாமதமும் "
            "ஏற்படலாம்; கூடுதல் கிருமி நாசினி விழிப்புணர்வு தேவை."
        ),
        anatomical_system="Deep Tissue Granulation, Wound Healing, Immune White Blood Cells",
        modifiers="Immediate sterile cleansing of minor abrasions prevents complications.",
        conflicting_indications="Mars well-placed accelerates wound coagulation and healing.",
    ),
    "chatterjee_sun_mars_8th_pitta_burn": ClassicalMedicalRuleDefinition(
        id="chatterjee_sun_mars_8th_pitta_burn",
        name="Sun and Mars in 8th House (Acute Pitta Flare-Ups & Thermal Hazards)",
        name_tamil="8-ஆம் பாவத்தில் சூரியன்-செவ்வாய் (அதி உஷ்ணம், ரத்த அழுத்தம் & தீக்காய அபாயம்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 19",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun and Mars conjoined in the 8th house from Lagna",
        mandatory_conditions=["Sun and Mars in 8th house"],
        traditional_interpretation=(
            "Sun and Mars are prime fiery planets. In the 8th house, they cause extreme Pitta vitiation, acute fevers, inflammatory "
            "ulcers, blood pressure fluctuations, excessive bleeding, and vulnerability to accidents from fire, heat, or electricity."
        ),
        interpretation_tamil=(
            "சூரியனும் செவ்வாயும் மிகை வெப்பக் கிரகங்களாகும். 8-ல் அவை இணைவது ரத்தக் கொதிப்பு, அதிக ரத்தப்போக்கு, அல்சர் புண்கள் "
            "மற்றும் தீ, மின்சாரம் சார்ந்த விபத்துக்களுக்கு ஆளாகும் சாத்தியத்தைத் தரும்."
        ),
        anatomical_system="Arterial Blood Pressure, Vascular Integrity, Heat Regulation",
        modifiers="Regular monitoring of blood pressure and satwik cooling diet preserves vascular health.",
        conflicting_indications="Benefic aspects from Moon or Jupiter calm arterial tension.",
    ),
    "chatterjee_moon_saturn_8th_injury": ClassicalMedicalRuleDefinition(
        id="chatterjee_moon_saturn_8th_injury",
        name="Moon and Saturn in 8th House (Limb & Locomotor Sensitivity)",
        name_tamil="8-ஆம் பாவத்தில் சந்திரன்-சனி (மூட்டுகள் & கால்களில் காயம்/நடை குறைபாடு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 20",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon and Saturn conjoined in the 8th house from Lagna",
        mandatory_conditions=["Moon and Saturn in 8th house"],
        traditional_interpretation=(
            "When Moon and Saturn occupy the 8th house, accidental injuries to limbs are indicated during Saturn transits. "
            "If located in Taurus, Scorpio, Leo, or Pisces, the injury may leave a persistent limp or walking sensitivity."
        ),
        interpretation_tamil=(
            "8-ஆம் பாவத்தில் சந்திரனும் சனியும் இணைவது கால்களில் அடிபடுதல், மூட்டு வாதம் அல்லது நடைபயிற்சியில் தற்காலிக சுளுக்கு, "
            "நடை மாற்றங்களை உருவாக்கலாம்."
        ),
        anatomical_system="Locomotor System, Ligaments, Synovial Fluid, Lower Limbs",
        modifiers="Joint-strengthening exercises and calcium-vitamin D optimization protect bones.",
        conflicting_indications="Venus in Kendra protects graceful physical locomotion.",
    ),
    "chatterjee_saturn_mercury_respiratory": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_mercury_respiratory",
        name="Conjunction of Saturn and Mercury (Respiratory & Bronchial Sensitivity)",
        name_tamil="சனி-புதன் சேர்க்கை (சுவாசக் குழாய் & ஆஸ்துமா போன்ற மூச்சுத் திணறல்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 28",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn and Mercury conjoined in any house (unless in exaltation or own sign)",
        mandatory_conditions=[
            "Saturn and Mercury in the same house",
            "Neither planet is in its own sign or exaltation sign",
        ],
        traditional_interpretation=(
            "A mere conjunction of Saturn and Mercury (except when one of them is exalted or in own sign) is a sure classical signal "
            "for breathing troubles, bronchial spasms, or chronic respiratory allergies."
        ),
        interpretation_tamil=(
            "சனி மற்றும் புதன் ஒரே வீட்டில் இணைந்திருப்பது (அவற்றில் ஒன்று ஆட்சி அல்லது உச்சம் பெறாத நிலையில்) சுவாசக் குழாய் அழற்சி, "
            "ஆஸ்துமா அல்லது மூச்சுத் திணறல் தொடர்பான கவனத்தைக் கோரும்."
        ),
        anatomical_system="Bronchial Tree, Respiratory Mucosa, Alveolar Gas Exchange",
        modifiers="Pranayama and deep breathing exercises expand vital lung capacity.",
        conflicting_indications="Jupiter aspecting the combination dilutes bronchial constriction.",
    ),
    "chatterjee_sun_mars_lagna_bp": ClassicalMedicalRuleDefinition(
        id="chatterjee_sun_mars_lagna_bp",
        name="Sun and Mars in Lagna (Arterial Tension & Pitta Blood Pressure Surges)",
        name_tamil="லக்னத்தில் சூரியன்-செவ்வாய் (அதிக ரத்த அழுத்தம் & தலைப் பகுதியில் உடற்சூடு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 29",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun and Mars conjoined in the 1st house (Ascendant)",
        mandatory_conditions=["Sun and Mars in 1st house"],
        traditional_interpretation=(
            "Conjunction of Mars and Sun in Lagna creates an extremely fiery constitution. Traditional texts note high arterial tension, "
            "hyper-acidity, frequent headaches, and sudden blood pressure spikes due to Pitta aggravation."
        ),
        interpretation_tamil=(
            "லக்னத்தில் சூரியனும் செவ்வாயும் இணைவது அதீத பித்த உடலமைப்பைத் தரும். இது ரத்தக் கொதிப்பு, தலைவலி, கோபம் மற்றும் "
            "உடற்சூடு அதிகரிப்பை இயல்பாக உண்டாக்குகிறது."
        ),
        anatomical_system="Cardiovascular Outflow, Cranial Vasculature, Arterial Blood Pressure",
        modifiers="Consuming copper-charged water and reducing salt intake stabilizes arterial pressure.",
        conflicting_indications="Cooling aspect of Moon or Jupiter balances the fiery surge.",
    ),
    "chatterjee_blood_4th_mars_moon": ClassicalMedicalRuleDefinition(
        id="chatterjee_blood_4th_mars_moon",
        name="Affliction of 4th House, Moon and Mars (Hematological Vulnerability)",
        name_tamil="4-ஆம் பாவம், சந்திரன், செவ்வாய் பாதிப்பு (ரத்த சோகை & ரத்த நாளக் குறைபாடுகள்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 31",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="4th house afflicted while both Moon and Mars are associated with malefics",
        mandatory_conditions=[
            "4th house contains a malefic or 4th lord in Dusthana",
            "Moon or Mars is afflicted by Saturn, Rahu, or Ketu",
        ],
        traditional_interpretation=(
            "Blood circulation is governed by the 4th house, while the Moon and Mars are the natural karakas for blood volume and hemoglobin. "
            "When the 4th house, Moon, and Mars are simultaneously afflicted, hematological disorders, anemia, or circulation defects manifest."
        ),
        interpretation_tamil=(
            "ரத்த ஓட்டம் 4-ஆம் பாவத்தாலும், ரத்த சிவப்பணுக்கள் சந்திரன் மற்றும் செவ்வாயாலும் ஆளப்படுகின்றன. இவை மூன்றும் அசுப கிரகங்களால் "
            "பாதிக்கப்படும் போது ரத்த சோகை, ரத்த அழுக்கு அல்லது ரத்த நாளக் குறைபாடுகள் உண்டாகலாம்."
        ),
        anatomical_system="Hematological System, Hemoglobin Synthesis, Cardiac Blood Circulation",
        modifiers="Iron-charged water and green leafy vegetables restore iron reserves.",
        conflicting_indications="Unafflicted Jupiter aspecting the 4th house cleanses blood chemistry.",
    ),
    "chatterjee_mercury_6th_saturn_aspect_ear": ClassicalMedicalRuleDefinition(
        id="chatterjee_mercury_6th_saturn_aspect_ear",
        name="Mercury in 6th Aspected by Saturn (Auditory & Ear Sensitivity)",
        name_tamil="6-ல் புதன் மீது சனியின் பார்வை (காது கேளாமை & செவி நரம்பு குறைபாடு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 34",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mercury in the 6th house receiving full aspect from Saturn",
        mandatory_conditions=[
            "Mercury occupies the 6th house",
            "Saturn casts aspect on Mercury",
        ],
        traditional_interpretation=(
            "Mercury rules the auditory pathways, nerves, and communicative senses. In the 6th house receiving Saturn's cold, constricting "
            "drishti, classical texts record vulnerability to hearing loss, tinnitus, or chronic middle ear infections."
        ),
        interpretation_tamil=(
            "செவிப்புலன் மற்றும் நரம்புகளின் காரகனான புதன் 6-ல் நின்று சனியின் பார்வையைப் பெற்றால், காது கேளாமை, நரம்பு பலவீனம் "
            "அல்லது காதுகளில் சீழ் வடிதல் போன்ற தொந்தரவுகள் நேரலாம்."
        ),
        anatomical_system="Auditory Nerve, Middle Ear Cavity, Eustachian Tube",
        modifiers="Early ENT evaluation and avoidance of loud acoustic trauma protects auditory health.",
        conflicting_indications="Jupiter in 3rd or aspecting Mercury preserves clear hearing.",
    ),
    "chatterjee_lagna_papa_kartari": ClassicalMedicalRuleDefinition(
        id="chatterjee_lagna_papa_kartari",
        name="Ascendant Hemmed Between Saturn and Mars (Papa-Kartari Deha Peeda)",
        name_tamil="லக்னம் சனி-செவ்வாய் இடையே பாபகர்த்தாரி (உடல் நலிவு & ஆரோக்கியப் போராட்டங்கள்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 44",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="12th house and 2nd house occupied by Saturn and Mars (or vice versa)",
        mandatory_conditions=[
            "Saturn in 12th/2nd and Mars in 2nd/12th hem the Ascendant",
        ],
        traditional_interpretation=(
            "When the Ascendant is flanked by harsh malefics Saturn and Mars on either side (in 12th and 2nd houses), the physical body "
            "is squeezed in Papa-Kartari Yoga. Dr. Chatterjee notes recurring bodily debilities, low vital stamina, and multiple health hurdles."
        ),
        interpretation_tamil=(
            "லக்னத்திற்கு 12 மற்றும் 2-ஆம் வீடுகளில் சனியும் செவ்வாயும் நின்று லக்னத்தை கத்திரி போல நெரித்தால் (பாபகர்த்தாரி யோகம்), "
            "உடலில் பலவீனம், தொடர் ஆரோக்கியப் பின்னடைவுகள் ஏற்படலாம்."
        ),
        anatomical_system="Physical Vitality, Cranial Symmetry, Whole Body Constitution",
        modifiers="Benefic planets in 1st house or trines alleviate constitutional distress.",
        conflicting_indications="Jupiter casting aspect onto Lagna shatters the malefic scissors.",
    ),
    "chatterjee_jupiter_mars_stomach": ClassicalMedicalRuleDefinition(
        id="chatterjee_jupiter_mars_stomach",
        name="Jupiter Afflicted by Mars or 8th Lord (Gastric Inflammation & Hepatic Strain)",
        name_tamil="குரு மீது செவ்வாய்/8-ஆம் அதிபதியின் பார்வை (வயிற்று அழற்சி & கல்லீரல் வீக்கம்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 51",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Jupiter receiving full aspect from Mars or the 8th house lord",
        mandatory_conditions=[
            "Jupiter is aspected by Mars or by 8th lord",
        ],
        traditional_interpretation=(
            "Jupiter rules the liver, digestive enzymes, and systemic fat metabolism. When Jupiter is aspected by aggressive Mars, "
            "it induces gastric wall inflammation. When aspected by the 8th lord, hepatomegaly or liver/spleen enlargement is indicated."
        ),
        interpretation_tamil=(
            "செரிமான நொதிகள் மற்றும் கல்லீரலின் அதிபதியான குருவை செவ்வாய் பார்த்தால் வயிற்று அழற்சியும், 8-ஆம் அதிபதி பார்த்தால் "
            "கல்லீரல் அல்லது மண்ணீரல் வீக்கமும் உண்டாகலாம்."
        ),
        anatomical_system="Hepatic Parenchyma, Gastric Mucosa, Bile Secretion, Liver Enzymes",
        modifiers="Avoidance of saturated fats and inclusion of turmeric (curcumin) cools the liver.",
        conflicting_indications="Jupiter in own sign Sagittarius/Pisces or exalted in Cancer protects hepatic tissue.",
    ),
    "chatterjee_kidney_7th_taurus_libra": ClassicalMedicalRuleDefinition(
        id="chatterjee_kidney_7th_taurus_libra",
        name="Affliction of 7th House, 7th Lord, Venus & Libra (Renal & Kidney Disorders)",
        name_tamil="7-ஆம் பாவம், சுக்கிரன், துலாம் ராசி பாதிப்பு (சிறுநீரகம் & சிறுநீர்ப்பைக் கற்கள்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 54",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="7th house or 7th lord afflicted by 6th lord while Venus, Taurus, or Libra is afflicted",
        mandatory_conditions=[
            "7th house contains or is aspected by 6th lord",
            "Venus is combust, debilitated, or with malefic in chart",
        ],
        traditional_interpretation=(
            "The 7th house and sign Libra govern the kidneys and renal filtration units, while Venus is the ruler of urogenital tissues. "
            "Affliction of the 7th house/lord by the 6th lord alongside afflicted Venus indicates renal calculi (kidney stones) or nephritis."
        ),
        interpretation_tamil=(
            "7-ஆம் பாவமும் துலாம் ராசியும் சிறுநீரகங்களை ஆள்கின்றன. 6-ஆம் அதிபதியின் தாக்குதலோடு சுக்கிரனும் பலவீனமடைந்தால், "
            "சிறுநீரகக் கற்கள் மற்றும் சிறுநீரக வடிகட்டுதல் குறைபாடுகள் ஏற்படலாம்."
        ),
        anatomical_system="Renal Glomeruli, Kidneys, Ureters, Urinary Osmosis",
        modifiers="High daily water intake (3-4 litres) and barley water prevent renal stone precipitation.",
        conflicting_indications="Strong Jupiter aspect on 7th house maintains smooth renal function.",
    ),
    "chatterjee_lagna_lord_shubha_kartari": ClassicalMedicalRuleDefinition(
        id="chatterjee_lagna_lord_shubha_kartari",
        name="Lagna Lord Hemmed Between Benefics (Shubha-Kartari Immunity & Longevity)",
        name_tamil="லக்னாதிபதி சுபர்கள் இடையே சுபகர்த்தாரி (நோயற்ற வாழ்வு & நீண்ட ஆயுள்)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 57",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Lord of the Ascendant hemmed between unafflicted Mercury, Venus, or Jupiter",
        mandatory_conditions=[
            "Lagna lord has natural benefics on both adjacent sides without intervening malefics",
        ],
        traditional_interpretation=(
            "Longevity and sovereign freedom from chronic diseases are assured when the lord of the Ascendant is placed between "
            "any two unafflicted benefics (Mercury, Venus, Jupiter). This Shubha-Kartari Yoga forms an impenetrable biological shield."
        ),
        interpretation_tamil=(
            "லக்னாதிபதி சுப கிரகங்களான புதன், சுக்கிரன், குரு ஆகியோரின் நடுவே சுபகர்த்தாரி யோகம் பெற்று அமர்ந்தால், "
            "ஜாதகர் எத்தகைய கொடிய நோய்களிலிருந்தும் எளிதில் மீண்டு பூரண ஆயுளும் ஆரோக்கியமும் பெறுவார்."
        ),
        anatomical_system="Autonomic Resilience, Deep Cellular Longevity, Constitutional Immunity",
        modifiers="Lagna lord in Kendra/Trikona further enhances vitality.",
        conflicting_indications="None; celebrated classical health-protecting combination.",
    ),
    "chatterjee_urinary_sun_venus_saturn_5th": ClassicalMedicalRuleDefinition(
        id="chatterjee_urinary_sun_venus_saturn_5th",
        name="Sun, Venus, and Saturn in 5th House (Pancreatic-Glycemic Stress & Urinary Tract)",
        name_tamil="5-ஆம் பாவத்தில் சூரியன்-சுக்கிரன்-சனி (கணைய சர்க்கரை அழுத்தம் & சிறுநீரகப் பாதை)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 60",
        category="Organ-Specific Yogas",
        system="vedic",
        required_placements="Sun, Venus, and Saturn co-present in the 5th house",
        mandatory_conditions=["Sun, Venus, and Saturn in 5th house"],
        traditional_interpretation=(
            "The mutual friction of the scorching Sun, cold Saturn, and fluid-ruler Venus in the 5th house impairs both glandular "
            "insulin secretions and fluid filtration, predisposing to urinary disorders, gleet, and juvenile/adult diabetes mellitus."
        ),
        interpretation_tamil=(
            "5-ஆம் பாவத்தில் சூரியன், சுக்கிரன், சனி ஒன்று கூடினால் கணையத்தின் இன்சுலின் சுரப்பும் சிறுநீரக நீர் வடிகட்டுதலும் "
            "பாதிக்கப்பட்டு, நீரிழிவு மற்றும் சிறுநீரக உபாதைகள் உண்டாகலாம்."
        ),
        anatomical_system="Endocrine Pancreas, Urinary Bladder, Glycemic Fluid Balance",
        modifiers="Low glycemic index diet and fenugreek (methi) powder stabilize sugar balance.",
        conflicting_indications="Jupiter trinal aspect neutralizes glandular degeneration.",
    ),
    "chatterjee_mars_4th_moon_blood": ClassicalMedicalRuleDefinition(
        id="chatterjee_mars_4th_moon_blood",
        name="Mars in 4th Aspecting Moon (Blood Circulation Friction & Pressure Surges)",
        name_tamil="4-ல் செவ்வாய் சந்திரனைப் பார்த்தல் (ரத்த ஓட்ட உராய்வு & ரத்தக் கொதிப்பு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 76",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars in 4th house casting aspect on Moon or Moon in 4th aspected by Mars",
        mandatory_conditions=[
            "Mars in 4th house and aspects Moon, or mutual 4th/10th aspect between Mars and Moon",
        ],
        traditional_interpretation=(
            "Mars in the 4th house (heart/chest cavity) in aspect to the Moon (fluids and emotions) creates friction between Pitta "
            "heat and Kapha fluid, producing blood impurities, erratic circulatory pressure, and menstrual/arterial turbulence."
        ),
        interpretation_tamil=(
            "மார்பு ஸ்தானமான 4-ல் செவ்வாய் நின்று சந்திரனைப் பார்ப்பது உடலின் ரத்த ஓட்டத்தில் அழுத்தத்தையும், உஷ்ண மாறுபாடுகளையும், "
            "ரத்தக் கொதிப்புப் போக்குகளையும் ஏற்படுத்தும்."
        ),
        anatomical_system="Cardio-Thoracic Vasculature, Blood Volume, Arterial Pressure",
        modifiers="Hydration and silver-charged water cool systemic vascular friction.",
        conflicting_indications="Jupiter aspect restores cardiac and vascular peace.",
    ),
    "chatterjee_insomnia_sun_12th": ClassicalMedicalRuleDefinition(
        id="chatterjee_insomnia_sun_12th",
        name="Sun / 12th House Affliction (Circadian Rhythm Disruption & Insomnia)",
        name_tamil="சூரியன் / 12-ஆம் பாவம் பாதிப்பு (தூக்கமின்மை & சிர்காடியன் சுழற்சி சீர்குலைவு)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 114",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="12th house from Lagna or Sun occupied by malefics (Saturn, Mars, Rahu, Ketu)",
        mandatory_conditions=[
            "Malefic occupying 12th house or 12th from Sun",
        ],
        traditional_interpretation=(
            "The Sun is the solar clock governing the natural sleep-wake cycle; when the Sun sets, all living beings sleep. "
            "Dr. Chatterjee emphasizes that malefics (Saturn, Mars, Rahu, Ketu) in the 12th from Sun or Lagna cause chronic insomnia, "
            "disturbed sleep patterns, and autonomic nervous restlessness."
        ),
        interpretation_tamil=(
            "சூரியன் இயற்கை உயிரியல் கடிகாரத்தின் அதிபதியாவார். லக்னத்திற்கு அல்லது சூரியனுக்கு 12-ல் அசுப கிரகங்கள் நின்றால், "
            "ஆழ்ந்த தூக்கமின்மை, அமைதியற்ற இரவுப் பொழுதுகள் மற்றும் நரம்பு சோர்வு ஏற்படலாம்."
        ),
        anatomical_system="Pineal Melatonin Axis, Sleep Induction, Hypothalamic Circadian Clock",
        modifiers="Sleeping in dark room, avoiding evening screen time, and taking warm milk restores circadian rhythm.",
        conflicting_indications="Waxing Moon in 12th or benefic aspect from Venus guarantees peaceful rest.",
    ),
    "chatterjee_saturn_mars_vata_rakta": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_mars_vata_rakta",
        name="Saturn in 1st/6th/8th Aspected by Mars (Vata-Rakta / Gout & Joint Inflammation)",
        name_tamil="1, 6, 8-ல் சனி மீது செவ்வாயின் பார்வை (வாத-ரக்தம், கவுட் & மூட்டு அழற்சி)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 120",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn in 1st, 6th, or 8th house receiving full aspect from Mars",
        mandatory_conditions=[
            "Saturn is in house 1, 6, or 8",
            "Mars casts aspect on Saturn",
        ],
        traditional_interpretation=(
            "Saturn rules Vata (wind, bones, joints) while Mars rules Rakta (blood, inflammatory heat). When Saturn in 1st, 6th, "
            "or 8th is aspected by Mars, classical Ayurvedic pathology defines this as Vata-Rakta (gout, arthritis, joint swelling)."
        ),
        interpretation_tamil=(
            "சனி வாதத்தையும் எலும்புகளையும், செவ்வாய் ரத்தத்தையும் ஆள்கின்றன. 1, 6, அல்லது 8-ல் உள்ள சனியை செவ்வாய் பார்த்தால் "
            "வாத-ரக்தம் (மூட்டு வலி, கவுட், மூட்டுகளில் யூரிக் அமிலம் சேருதல்) ஏற்படலாம்."
        ),
        anatomical_system="Synovial Joints, Cartilage, Uric Acid Metabolism, Bone Articulations",
        modifiers="Copper-charged water and low purine diet alleviate joint stiffness.",
        conflicting_indications="Jupiter aspect mitigates joint inflammation.",
    ),
    "chatterjee_moon_6_12_saturn_lagna_asthma": ClassicalMedicalRuleDefinition(
        id="chatterjee_moon_6_12_saturn_lagna_asthma",
        name="Moon in 6th/12th with Saturn in Lagna (Bronchial Obstruction & Asthmatic Tendency)",
        name_tamil="லக்னத்தில் சனி & 6/12-ல் சந்திரன் (சுவாசத் தடை & ஆஸ்துமா சளித் தொல்லை)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 138",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn in Lagna while Moon occupies the 6th or 12th house",
        mandatory_conditions=[
            "Saturn is in 1st house",
            "Moon is in 6th or 12th house",
        ],
        traditional_interpretation=(
            "Saturn in the Ascendant restricts thoracic expansion, while Moon in 6th or 12th weakens phlegmatic (Kapha) immunity. "
            "This configuration classically leads to chronic bronchial congestion, nocturnal coughing, and asthmatic breathing difficulties."
        ),
        interpretation_tamil=(
            "லக்னத்தில் சனி நின்று சந்திரன் 6 அல்லது 12-ல் அமைந்தால், மார்புப் பகுதியில் சளி அடைப்பு, மூச்சுத் திணறல் மற்றும் "
            "ஆஸ்துமா உபாதைகள் தோன்றும் சாத்தியமுண்டு."
        ),
        anatomical_system="Thoracic Cavity, Bronchial Tree, Pulmonary Kapha Drainage",
        modifiers="Steam inhalation, dry warm climate, and pranayama clear airways.",
        conflicting_indications="Sun strong in Kendra burns excess phlegm.",
    ),
    "chatterjee_saturn_rahu_2nd_constipation": ClassicalMedicalRuleDefinition(
        id="chatterjee_saturn_rahu_2nd_constipation",
        name="Saturn and Rahu in 2nd House (Chronic Constipation - Grandmother of Diseases)",
        name_tamil="2-ஆம் பாவத்தில் சனி-ராகு (நீண்டகால மலச்சிக்கல் & செரிமான வறட்சி)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 139",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Saturn and Rahu conjoined in the 2nd house from Lagna",
        mandatory_conditions=["Saturn and Rahu in 2nd house"],
        traditional_interpretation=(
            "Dr. Chatterjee emphasizes that constipation is the 'grandmother of all diseases'. Saturn and Rahu together in the 2nd house "
            "(diet, food habits, and oral intake) cause dry dietary habits, irregular meals, and chronic colon sluggishness."
        ),
        interpretation_tamil=(
            "டாக்டர் சட்டர்ஜி 'மலச்சிக்கலே அனைத்து நோய்களின் தாய்' என்று எச்சரிக்கிறார். 2-ல் சனியும் ராகுவும் கூடினால் முறையற்ற உணவுப் பழக்கம், "
            "குடலில் வறட்சி மற்றும் கடுமையான மலச்சிக்கல் உண்டாகலாம்."
        ),
        anatomical_system="Large Intestine, Colonic Peristalsis, Dietary Assimilation",
        modifiers="High dietary fibre, papaya, curd, and salt-free days eliminate bowel stagnation.",
        conflicting_indications="Benefic Jupiter aspecting 2nd house promotes healthy digestion.",
    ),
    "chatterjee_disease_free_benefic_6th": ClassicalMedicalRuleDefinition(
        id="chatterjee_disease_free_benefic_6th",
        name="Unaffiliated Benefic in 6th with 6th Lord in Kendra (Arogya Immunity Yoga)",
        name_tamil="6-ல் தனித்த சுபர் & கேந்திரத்தில் 6-ஆம் அதிபதி (ஆரோக்கிய யோகம் / இயற்கை எதிர்ப்புச் சக்தி)",
        source="Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse="Chapter 2, Golden Rule 227",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Unafflicted natural benefic (Jupiter, Venus, or Mercury) in 6th while 6th lord is in Kendra (1, 4, 7, 10)",
        mandatory_conditions=[
            "Natural benefic occupies 6th house without malefic conjunction",
            "6th lord occupies Kendra (1, 4, 7, 10)",
        ],
        traditional_interpretation=(
            "If the 6th house is occupied by an unaffiliated natural benefic while the lord of the 6th house is anchored in an angle (Kendra) "
            "from the Ascendant, the subject enjoys exceptional natural immunity and rarely incurs severe illnesses."
        ),
        interpretation_tamil=(
            "6-ஆம் பாவத்தில் தனித்த சுபக் கிரகம் (குரு, சுக்கிரன், புதன்) அமர்ந்து, 6-ஆம் அதிபதி கேந்திரத்தில் நின்றால், "
            "ஜாதகர் வியக்கத்தக்க இயற்கை நோய் எதிர்ப்பு சக்தி பெற்று பெரும் நோய்களின்றி நலமுடன் வாழ்வார்."
        ),
        anatomical_system="Host Immune Defense, Lymphocyte Resilience, Arogya Balance",
        modifiers="Benefic in own sign further magnifies health.",
        conflicting_indications="None; praised classical arogya combination.",
    ),
}

# Clinical Case Studies from Dr. S. S. Chatterjee's Research Diary
CHATTERJEE_CASE_STUDIES: List[Dict[str, Any]] = [
    {
        "case_id": "chatterjee_case_1_diabetes",
        "case_title": "Example 1: Story of a Diabetic Patient",
        "case_title_ta": "உதாரணம் 1: நீரிழிவு நோயாளி ஒருவரின் வாழ்க்கை வரலாறு",
        "patient_profile": "Male, Born 16-04-1968 at 15:30 IST, Kolkata (Pisces Lagna)",
        "disease_diagnosed": "Juvenile Diabetes Mellitus with Coma and Early Demise",
        "astrological_indicators": [
            "Pisces Lagna with 5 planets conjoined: Sun, Venus, Ketu, Mercury, Saturn with Rahu aspecting.",
            "Lagna lord Jupiter posited in the 6th house (Leo), making all 5 planets in Lagna functionally weak.",
            "Exchange of 1st and 8th lords generating Dainya Yoga (misery, diseases, enemies).",
            "Saturn-Rahu-Sun conjunction in Lagna with Venus afflicted by malefics generated severe diabetes at a very young age.",
        ],
        "dasha_timing": "Demise during Saturn-Jupiter chidra-dasa (Saturn ruling 11th/12th, Jupiter in 6th).",
        "key_takeaway": "When 6th/8th/12th lords conjoin in Lagna with Rahu-Ketu while Lagnesha lands in 6th and Venus is combust/afflicted, acute diabetes manifests early in life.",
    },
    {
        "case_id": "chatterjee_case_2_robust_health",
        "case_title": "Example 2: Prof. R. J. Galgali - Example of Robust Health",
        "case_title_ta": "உதாரணம் 2: பேராசிரியர் ஆர். ஜே. கல்கலி - பரிபூரண ஆரோக்கியத்தின் உதாரணம்",
        "patient_profile": "Male, Born 05-03-1927 at 23:30 IST, Belgaon (Scorpio Lagna)",
        "disease_diagnosed": "Ageless Living - Completely Free from Diseases past Age 80",
        "astrological_indicators": [
            "Maha Yoga (exchange between 1st lord Mars in 7th and 7th lord Venus in 5th with Lagnesha aspecting Lagna).",
            "Union of three benefics (Venus, Moon, Mercury) in the 5th house forming Parijata Yoga.",
            "Strong 4th house and 4th lord Sun with Jupiter; no evil conjunctions in Dusthanas.",
            'Robust 100 kg physique, 6\'2" height, illustrious university dean, completely disease-free and vice-free.',
        ],
        "dasha_timing": "Flourished through all major periods without any serious medical crises.",
        "key_takeaway": "Strong Lagnesha aspecting Lagna, 1st/4th lord Maha Yoga, and three benefics in 5th completely eliminate the negative traits of Mars-Saturn oppositions, conferring a disease-free life.",
    },
    {
        "case_id": "chatterjee_case_3_deaf_mute_child",
        "case_title": "Example 3: Congenital Motor, Speech, and Hearing Impairment",
        "case_title_ta": "உதாரணம் 3: பிறவியிலேயே பேச, கேட்க, நடக்க இயலாத குழந்தையின் ஜாதகம்",
        "patient_profile": "Male, Born 11-08-1992 at 23:30 IST, Ghaziabad (Aries Lagna)",
        "disease_diagnosed": "Deaf, Dumb, Crippled Locomotor Disorder from Birth",
        "astrological_indicators": [
            "Aries Lagna; Sun and retrograde 6th lord Mercury in Cancer receiving direct aspect of Saturn from Capricorn.",
            "Mutual Moon-Sun affliction across Kendra axis forming Adhama Yoga.",
            "Deha Rasi (Cancer) occupied by retrograde 6th lord Mercury and aspected by Saturn.",
            "Jeeva Rasi lord Jupiter aspected by 8th lord Mars; 3rd house (ears/arms) occupied by Ketu.",
        ],
        "dasha_timing": "Commenced life with Deha Rasi Cancer dasha, severely afflicted by Saturn and Mars.",
        "key_takeaway": "When both Deha and Jeeva signs are occupied by malefics or afflicted by 6th/8th lords, and Sun-Moon mutual affliction occurs, profound congenital sensory and locomotor handicaps result.",
    },
    {
        "case_id": "chatterjee_case_4_diabetic_lady",
        "case_title": "Example 4: Lifelong Suffering from Diabetes Mellitus",
        "case_title_ta": "உதாரணம் 4: வாழ்நாள் முழுவதும் நீரிழிவு நோயால் போராடிய பெண்மணியின் ஜாதகம்",
        "patient_profile": "Female, Born 04-03-1977 at 18:45 IST, Ludhiana (Leo Lagna)",
        "disease_diagnosed": "Severe Diabetes Mellitus from Age 12, Diabetic Coma",
        "astrological_indicators": [
            "Leo Lagna; 6th/12th axis heavily afflicted by Mars in Capricorn and Saturn in Cancer.",
            "Virgo (pancreas/6th zodiac sign) afflicted by Saturn's 3rd aspect.",
            "Moon afflicted by Sun and Ketu; Sun afflicted by Rahu across 1/7 axis.",
            "Venus hemmed between malefics in 8th house (Pisces); 8th lord Jupiter in 10th enemy camp.",
        ],
        "dasha_timing": "Trapped by diabetes from age 12; entered diabetic coma in March 2006 during Sun-Ketu dasha.",
        "key_takeaway": "Affliction of Virgo, 6/12 axis strained by Mars-Saturn, Venus hemmed in 8th, and weak Jupiter destroy glycemic homeostasis, triggering severe diabetes.",
    },
    {
        "case_id": "chatterjee_case_5_chronic_ailments",
        "case_title": "Example 5: Married Lady with Lifelong Chronic Health Problems",
        "case_title_ta": "உதாரணம் 5: வாழ்நாள் முழுவதும் தீராத தலைவலி, கண், தொண்டை உபாதைகள் கொண்ட பெண்",
        "patient_profile": "Female, Born 17-08-1968 at 05:03 IST, Amritsar (Cancer Lagna)",
        "disease_diagnosed": "Lifelong Headache, Poor Eyesight, Throat Irritation, Sinusitis, Auditory Weakness",
        "astrological_indicators": [
            "Cancer Lagna occupied by debilitated Mars; 10th house occupied by debilitated and retrograde Saturn.",
            "4th house spoiled by the joint violent aspects of Saturn and Mars.",
            "3rd house occupied by Ketu; 3rd lord Mercury combust and afflicted by 6th lord Jupiter in 2nd.",
            "Sun and Venus hemmed between malefics in Leo, impairing ocular and cranial health.",
        ],
        "dasha_timing": "Suffering persisted uninterruptedly through education, marriage, and adulthood.",
        "key_takeaway": "Joint aspects of Mars and Saturn concentrating on the 4th house and Lagna, with 3rd lord combust and afflicted by 6th lord, produce chronic head, eye, and respiratory ailments.",
    },
    {
        "case_id": "chatterjee_case_6_khorana_nobel",
        "case_title": "Example 6: Dr. Hargobind Khorana - Nobel Laureate Longevity & Intellect",
        "case_title_ta": "உதாரணம் 6: டாக்டர் ஹர்கோவிந்த் கொரானா - நோபல் பரிசு மற்றும் தீர்க்காயுள் யோகம்",
        "patient_profile": "Male, Born 09-01-1922 at 15:30 IST, Rajpur Punjab (Taurus Lagna)",
        "disease_diagnosed": "Robust Longevity, Genetic Synthesis Pioneer, Nobel Prize in Medicine (1968)",
        "astrological_indicators": [
            "Taurus Lagna; Lagna lord Venus placed in 8th house; its dispositor Jupiter in 5th; its dispositor Mercury in 9th, forming legendary Parijata Yoga.",
            "Yoga Karaka Saturn in 5th with Jupiter and Rahu, catalyzing profound chemical and metallurgical research.",
            "8th lord in presence of Rahu helped him in revolutionary gene synthesis discoveries (DNA/RNA).",
        ],
        "dasha_timing": "Received Nobel Prize during Jupiter-Ketu dasha; Parijata Yoga planets yielded supreme glory.",
        "key_takeaway": "Parijata Yoga converts even the 8th lord and Rahu into instruments of world-renowned scientific achievement and grants sustained vital endurance.",
    },
]


# ===========================================================================
# Jane Ridder-Patrick: A Handbook of Medical Astrology (2nd Edition)
# CrabApple Press, Edinburgh - Compendium Data & Rule Registry
# ===========================================================================

JANE_RIDDER_PATRICK_METADATA: Dict[str, Any] = {
    "book_title": "A Handbook of Medical Astrology (Second Edition, Revised and Enlarged)",
    "book_title_ta": "மருத்துவ ஜோதிட கையேடு (இரண்டாம் பதிப்பு - ஜேன் ரிடர்-பேட்ரிக்)",
    "author": "Jane Ridder-Patrick, Ph.D., N.D., M.N.I.M.H.",
    "author_credentials": "Practising Pharmacist, Medical Herbalist, Naturopath, and Astrologer (Edinburgh, Scotland)",
    "publisher": "CrabApple Press, Edinburgh (ISBN 978 0 9551989 0 8)",
    "foreword_by": "Charles Harvey, Past President of the Astrological Association of Great Britain",
    "philosophical_motto": "Let it be stated here once and for all that we are not dealing with symbols but activities, are not instituting metaphorical allusions but commenting upon urgent forces, quite capable of practical demonstration. — Heinrich Daath",
    "alphabet_framework": {
        "Planets": "WHAT is happening — action, physiological processes in the body (the verbs)",
        "Signs": "WHERE these processes take place — location, structure, anatomy (the adjectives/adverbs)",
        "Aspects": "HOW planets modify the physiological processes of other planets",
        "Houses": "WHICH external and environmental factors affect health",
        "Transits_Progressions": "WHEN — timing of onset, crisis, remission, and recurrence of health problems",
    },
    "three_factors_of_disease": {
        "1_disease_potential": "Natal chart vulnerability: without natal significators, a disease will never manifest.",
        "2_conducive_conditions": "Physical, emotional, mental hygiene and the presence/absence of internal/external toxins.",
        "3_triggers": "Transits and progressions activating chart potential at 3 levels: Inner Mind, Outer Events, or Physical Body."
    }
}

CULPEPER_7_RULES: List[Dict[str, str]] = [
    {
        "rule_number": "1",
        "rule_en": "Fortify the body with herbs of the nature of the Lord of the Ascendant, 'tis no matter whether he be a Fortune or Infortune in this case.",
        "rule_ta": "லக்னாதிபதியின் தன்மை கொண்ட மூலிகைகளால் உடலை வலுப்படுத்த வேண்டும்; அவர் சுபரோ அல்லது அசுபரோ என்பது இங்கு முக்கியமல்ல.",
        "application": "Reinforces native constitution and vitality through Ascendant lord's botanical affinities."
    },
    {
        "rule_number": "2",
        "rule_en": "Let your medicine be something antipathetical to the Lord of the Sixth.",
        "rule_ta": "உங்கள் மருந்து 6-ஆம் அதிபதியின் தன்மைக்கு எதிர்நிலையானதாக (முரண்பட்டதாக) இருக்க வேண்டும்.",
        "application": "Doctrine of contraries: opposes the pathogenic influence generating the ailment."
    },
    {
        "rule_number": "3",
        "rule_en": "Let your medicine be something of the nature of the sign ascending.",
        "rule_ta": "உங்கள் மருந்து உதயமாகும் லக்ன ராசியின் இயல்புக்கு ஒத்ததாக இருக்க வேண்டும்.",
        "application": "Nourishes the physical form and elemental temperament of the rising sign."
    },
    {
        "rule_number": "4",
        "rule_en": "If the Lord of the Tenth be strong make use of his medicines.",
        "rule_ta": "10-ஆம் அதிபதி வலுவாக இருப்பின், அவரது ஆதிக்கத்திற்குரிய மருந்துகளைப் பயன்படுத்தவும்.",
        "application": "The 10th house is the house of the physician and medicine; its strong lord guarantees therapeutic efficacy."
    },
    {
        "rule_number": "5",
        "rule_en": "If this cannot well be make use of the medicines of the Light of Time [Sun by day, Moon by night].",
        "rule_ta": "இது சாத்தியமில்லை எனில், காலத்தின் ஒளியான கிரகத்தின் (பகலில் சூரியன், இரவில் சந்திரன்) மருந்துகளைப் பயன்படுத்தவும்.",
        "application": "Draws upon diurnal solar vitality or nocturnal lunar fluid nourishment."
    },
    {
        "rule_number": "6",
        "rule_en": "Be sure always to fortify the grieved part of the body by sympathetical remedies.",
        "rule_ta": "பாதிக்கப்பட்ட உடல் உறுப்பை அதற்குரிய ஒத்த சுபாவமுள்ள (அனுதாப) மருந்துகளால் எப்போதும் தேற்ற வேண்டும்.",
        "application": "Sympathetic remedies support and nourish the specific organ in distress."
    },
    {
        "rule_number": "7",
        "rule_en": "Regard the heart, keep that upon the wheels, because the Sun is the foundation of life, and therefore universal remedies cure all diseases by fortifying the heart.",
        "rule_ta": "இதயத்தை கண்ணும் கருத்துமாகப் பாதுகாக்கவும்; ஏனெனில் சூரியனே உயிரின் ஆதாரம், இதயத்தை வலுப்படுத்துவதே அனைத்து பிணிகளையும் தீர்க்கும்.",
        "application": "Protecting the solar pump ensures oxygen and vital prana reach every tissue cell."
    }
]

JANE_THREE_CROSSES: List[Dict[str, Any]] = [
    {
        "cross": "Cardinal Cross",
        "cross_ta": "சர ராசிகள் (மேஷம், கடகம், துலாம், மகரம்)",
        "theme": "Regulation, Structure and Protection",
        "systems": "Skin, Skeletal, Endocrine and Immune systems",
        "reflex_dynamics": "Aries (Adrenals) -> Libra (Kidneys/Blood sugar/Sodium balance) -> Cancer (Body water/Mucous membranes) -> Capricorn (Anterior Pituitary/Bones/Skin). Disorders in one sign reflexly trigger symptoms across the cross.",
        "therapeutic_focus": "Endocrine harmony, fluid homeostasis, skeletal density, and pituitary-adrenal balance."
    },
    {
        "cross": "Fixed Cross",
        "cross_ta": "ஸ்திர ராசிகள் (ரிஷபம், சிம்மம், விருச்சிகம், கும்பம்)",
        "theme": "Vital Functions & Accumulation",
        "systems": "Cardiovascular, Reproductive, Excretory systems & Reptilian Brain",
        "reflex_dynamics": "Taurus (Throat/Thyroid) <-> Scorpio (Colon/Reproductive organs); Leo (Heart/Spine) <-> Aquarius (Calf venous pump/Corticospinal tract). Tends toward cellular proliferation, stones, and tissue engorgement.",
        "therapeutic_focus": "Cardiovascular circulation, metabolic detox, lower bowel regularity, and anti-engorgement."
    },
    {
        "cross": "Mutable Cross",
        "cross_ta": "உபய ராசிகள் (மிதுனம், கன்னி, தனுசு, மீனம்)",
        "theme": "Metabolic Cross: Change and Exchange",
        "systems": "Respiratory, Digestive, and Nervous systems (Least robust, body mediators)",
        "reflex_dynamics": "Gemini (Tubes, lungs, peripheral nerves) <-> Sagittarius (Locomotion, cerebral cortex, higher integration); Virgo (Enteric belly brain, digestion, enzymes) <-> Pisces (Lymphatic, pineal, immune boundary dissolution).",
        "therapeutic_focus": "Nervous regulation, digestive enzyme support (naturopathy), and emotional boundary consolidation."
    }
]

JANE_CELL_SALTS: List[Dict[str, Any]] = [
    {"sign": "Aries", "sign_ta": "மேஷம்", "cell_salt": "Potassium phosphate", "abbreviation": "Kali. phos.", "action_en": "Brain and nerve nutrient, relieves mental exhaustion, tension headaches.", "action_ta": "மூளை மற்றும் நரம்பு ஊட்டச்சத்து, மன உளைச்சல் தலைவலியைப் போக்கும்."},
    {"sign": "Taurus", "sign_ta": "ரிஷபம்", "cell_salt": "Sodium sulphate", "abbreviation": "Nat. sulph.", "action_en": "Liver and water eliminator, supports bile flow, relieves biliousness.", "action_ta": "கல்லீரல் மற்றும் நீர் கழிவு நீக்கி, பித்த ஓட்டத்தை சீராக்கும்."},
    {"sign": "Gemini", "sign_ta": "மிதுனம்", "cell_salt": "Potassium chloride", "abbreviation": "Kali. mur.", "action_en": "Respiratory and glandular decongestant, clears bronchial phlegm and fibrinous exudates.", "action_ta": "சுவாச மற்றும் நிணநீர் சளி நீக்கி, மூச்சுக்குழாய் அடைப்பை அகற்றும்."},
    {"sign": "Cancer", "sign_ta": "கடகம்", "cell_salt": "Calcium fluoride", "abbreviation": "Calc. fluor.", "action_en": "Elastic tissue and vascular toner, maintains stomach elasticity, prevents vein laxity.", "action_ta": "திசு நெகிழ்ச்சி மற்றும் இரத்தக்குழாய் வலுவூட்டி, வீங்கி பருத்த நரம்புகளைத் தடுக்கும்."},
    {"sign": "Leo", "sign_ta": "சிம்மம்", "cell_salt": "Magnesium phosphate", "abbreviation": "Mag. phos.", "action_en": "Muscular and antispasmodic salt, relieves cardiac tension, muscle spasms and cramps.", "action_ta": "தசை பிடிப்பு நிவாரணி, இதய தசை மற்றும் நரம்பு இறுக்கத்தைத் தளர்த்தும்."},
    {"sign": "Virgo", "sign_ta": "கன்னி", "cell_salt": "Potassium sulphate", "abbreviation": "Kali. sulph.", "action_en": "Skin and mucous membrane oxygen carrier, supports enteric digestion and enzyme balance.", "action_ta": "தோல் மற்றும் சளிச்சவ்வு பிராணவாயு கடத்தி, செரிமான என்சைம்களை சீராக்கும்."},
    {"sign": "Libra", "sign_ta": "துலாம்", "cell_salt": "Sodium phosphate", "abbreviation": "Nat. phos.", "action_en": "Acid-base neutralizer, prevents lactic and uric acid accumulation, supports kidneys.", "action_ta": "அமில-கார சமநிலைப்படுத்தி, யூரிக் அமில தேக்கத்தைத் தடுத்து சிறுநீரகத்தை காக்கும்."},
    {"sign": "Scorpio", "sign_ta": "விருச்சிகம்", "cell_salt": "Calcium sulphate", "abbreviation": "Calc. sulph.", "action_en": "Cellular cleanser and purifier, heals suppurating wounds, boils, and clears colon wastes.", "action_ta": "உயிரணு கழிவகற்றி, சீழ் பிடித்த கட்டிகளை குணமாக்கி குடல் நச்சுக்களை நீக்கும்."},
    {"sign": "Sagittarius", "sign_ta": "தனுசு", "cell_salt": "Silicon oxide", "abbreviation": "Silica", "action_en": "Connective tissue cleanser and strengthener, gives tensile strength to joints and nerve sheaths.", "action_ta": "இணைப்பு திசு வலுவூட்டி, மூட்டுகள் மற்றும் நரம்பு உறைகளுக்கு நெகிழ்வுத்தன்மை தரும்."},
    {"sign": "Capricorn", "sign_ta": "மகரம்", "cell_salt": "Calcium phosphate", "abbreviation": "Calc. phos.", "action_en": "Bone and skeletal builder, essential for tooth dentine, joint repair, and convalescence.", "action_ta": "எலும்பு மற்றும் எலும்புக்கூடு கட்டமைப்பாளர், பற்கள் மற்றும் மூட்டு தேய்மானத்தை சீராக்கும்."},
    {"sign": "Aquarius", "sign_ta": "கும்பம்", "cell_salt": "Sodium chloride", "abbreviation": "Nat. mur.", "action_en": "Osmotic fluid distributor, regulates hydration of cells and blood circulation in lower limbs.", "action_ta": "செல்லுலார் நீர் சமநிலைப் படுத்தி, கால் நரம்புகள் மற்றும் ரத்த ஓட்டத்தை சீராக்கும்."},
    {"sign": "Pisces", "sign_ta": "மீனம்", "cell_salt": "Iron phosphate", "abbreviation": "Ferr. phos.", "action_en": "Oxygen carrier and anti-inflammatory, relieves early stages of fever, congestion and chills.", "action_ta": "ஆக்சிஜன் கடத்தி மற்றும் அழற்சி எதிர்ப்பு உப்பு, காய்ச்சல் மற்றும் சளி தொற்றை நீக்கும்."}
]

JANE_BACH_FLOWERS: List[Dict[str, Any]] = [
    {"sign": "Aries", "sign_ta": "மேஷம்", "flower": "Impatiens", "action_en": "For impatience, tension, irritability, and driving body beyond limits.", "action_ta": "பொறுமையின்மை, எரிச்சல் மற்றும் உடலை வருத்தும் அவசர நிலையைத் தணிக்கும்."},
    {"sign": "Taurus", "sign_ta": "ரிஷபம்", "flower": "Gentian", "action_en": "For discouragement, despondency, and resistance to unexpected bodily changes.", "action_ta": "மனச்சோர்வு, நம்பிக்கை இழப்பு மற்றும் மாற்றங்களை ஏற்க மறுக்கும் மனதை மாற்றும்."},
    {"sign": "Gemini", "sign_ta": "மிதுனம்", "flower": "Cerato", "action_en": "For doubting one's inner voice, mental vacillation, and sensory distraction.", "action_ta": "தன் சுய உள்ளுணர்வை நம்பாமை மற்றும் சிதறும் கவனத்தை ஒருமுகப்படுத்தும்."},
    {"sign": "Cancer", "sign_ta": "கடகம்", "flower": "Clematis", "action_en": "For ungrounded daydreaming, withdrawal into shell, and fluid sluggishness.", "action_ta": "கனவுலகில் வாழ்தல், நிஜத்தை எதிர்கொள்ள தயங்குதல் மற்றும் மந்தநிலையை அகற்றும்."},
    {"sign": "Leo", "sign_ta": "சிம்மம்", "flower": "Vervain", "action_en": "For over-enthusiasm, stress from over-exertion, and driving the heart too hard.", "action_ta": "அளவுக்கு மிஞ்சிய வைராக்கியம், இதயத்தை வருத்தும் அதீத உழைப்பை சமநிலைப்படுத்தும்."},
    {"sign": "Virgo", "sign_ta": "கன்னி", "flower": "Centaury", "action_en": "For inability to say 'no', anxious over-service, and psychosomatic gut strain.", "action_ta": "'முடியாது' என மறுக்க முடியாமல் பிறருக்கு உழைத்து குடல் சோர்வு அடைவதைத் தடுக்கும்."},
    {"sign": "Libra", "sign_ta": "துலாம்", "flower": "Scleranthus", "action_en": "For indecision, emotional mood swings, and erratic fluctuating kidney/hormone tone.", "action_ta": "முடிவெடுக்க இயலாமை, ஊசலாடும் மனநிலை மற்றும் ஹார்மோன் சமநிலையின்மையை சீராக்கும்."},
    {"sign": "Scorpio", "sign_ta": "விருச்சிகம்", "flower": "Chicory", "action_en": "For possessiveness, holding on to old resentments, and colon congestion.", "action_ta": "பற்றுதல், பழைய கோபங்களை அடக்கி வைத்தல் மற்றும் கழிவுத் தேக்கத்தை போக்கும்."},
    {"sign": "Sagittarius", "sign_ta": "தனுசு", "flower": "Agrimony", "action_en": "For hiding inner pain behind a cheerful face, restlessness, and reckless stress.", "action_ta": "மனக்கவலையை சிரித்த முகத்திற்குள் மறைத்தல் மற்றும் அமைதியின்மையை போக்கும்."},
    {"sign": "Capricorn", "sign_ta": "மகரம்", "flower": "Mimulus", "action_en": "For fear of worldly failure, chronic anxiety, joint stiffness, and cold depression.", "action_ta": "தோல்வி பயம், வாழ்வியல் அச்சம், மூட்டு விறைப்பு மற்றும் மன அழுத்தத்தை நீக்கும்."},
    {"sign": "Aquarius", "sign_ta": "கும்பம்", "flower": "Water Violet", "action_en": "For proud aloofness, nervous tension, feeling disconnected from human warmth.", "action_ta": "தனிமை விரும்புதல், நரம்பு அதிர்வு மற்றும் சமூக பற்றுதலற்ற இறுக்கத்தை தளர்த்தும்."},
    {"sign": "Pisces", "sign_ta": "மீனம்", "flower": "Rock Rose", "action_en": "For acute panic, terror, psychic over-sensitivity, and immune collapse.", "action_ta": "திடீர் பீதி, பயம், அதிகப்படியான உணர்திறன் மற்றும் நோய் எதிர்ப்பு தளர்ச்சியை நீக்கும்."}
]

JANE_ACUPUNCTURE_MERIDIANS: List[Dict[str, Any]] = [
    {"sign": "Aries", "sign_ta": "மேஷம்", "meridian": "Kidney Meridian", "meridian_ta": "சிறுநீரக மெரிடியன்"},
    {"sign": "Taurus", "sign_ta": "ரிஷபம்", "meridian": "Triple Warmer Meridian", "meridian_ta": "மூவெப்ப கட்டுப்பாட்டு மெரிடியன்"},
    {"sign": "Gemini", "sign_ta": "மிதுனம்", "meridian": "Liver Meridian", "meridian_ta": "கல்லீரல் மெரிடியன்"},
    {"sign": "Cancer", "sign_ta": "கடகம்", "meridian": "Stomach Meridian", "meridian_ta": "இரைப்பை மெரிடியன்"},
    {"sign": "Leo", "sign_ta": "சிம்மம்", "meridian": "Heart Meridian", "meridian_ta": "இதய மெரிடியன்"},
    {"sign": "Virgo", "sign_ta": "கன்னி", "meridian": "Large Intestine Meridian", "meridian_ta": "பெருங்குடல் மெரிடியன்"},
    {"sign": "Libra", "sign_ta": "துலாம்", "meridian": "Circulation-Sexuality (Pericardium) Meridian", "meridian_ta": "இதய உறை / பாலியல் மெரிடியன்"},
    {"sign": "Scorpio", "sign_ta": "விருச்சிகம்", "meridian": "Bladder Meridian", "meridian_ta": "சிறுநீர்ப்பை மெரிடியன்"},
    {"sign": "Sagittarius", "sign_ta": "தனுசு", "meridian": "Pancreas-Spleen Meridian", "meridian_ta": "கணையம்-மண்ணீரல் மெரிடியன்"},
    {"sign": "Capricorn", "sign_ta": "மகரம்", "meridian": "Gall Bladder Meridian", "meridian_ta": "பித்தப்பை மெரிடியன்"},
    {"sign": "Aquarius", "sign_ta": "கும்பம்", "meridian": "Lung Meridian", "meridian_ta": "நுரையீரல் மெரிடியன்"},
    {"sign": "Pisces", "sign_ta": "மீனம்", "meridian": "Small Intestine Meridian", "meridian_ta": "சிறுகுடல் மெரிடியன்"}
]

JANE_ELEMENTAL_BALANCING: Dict[str, Any] = {
    "Excess Air": {
        "qualities": "Light, dry, and cold (Ayurvedic Vata - 'what blows')",
        "symptoms": "Lean dry skin, rapid aging, low blood sugar, flatulence, constipation, shooting pains, creaking joints, insomnia (2am-6am), racing anxious mind.",
        "balancing_diet": "Heavy, moist, and hot foods. Dairy products (yoghurt), cooked rice, oats, warm oily vegetables, generous salad dressings, digestive warming spices.",
        "avoid": "Raw food, yeast, mushrooms, refined sugars, dry beans, excess cabbage family.",
        "indicated_herbs": "Digestive stimulants, nervine sedatives, demulcents, bulk laxatives (valerian, liquorice, marshmallow, psyllium)."
    },
    "Low Air": {
        "qualities": "Deficiency of circulation, flexibility, and nervous responsiveness",
        "symptoms": "Sluggish reflex action, poor peripheral circulation, rigid mental patterns.",
        "balancing_diet": "Light, dry, stimulating foods. Raw foods, raw vegetable juices, sprouted grains and seeds, low oil intake, small infrequent meals.",
        "avoid": "Heavy dense greasy foods.",
        "indicated_herbs": "Circulatory stimulants, nerve stimulants, bitter tonics (peppermint, tea, rosemary, gentian)."
    },
    "Excess Fire": {
        "qualities": "Hot, light, and dry (Ayurvedic Pitta - 'what cooks')",
        "symptoms": "High body temperature, reddish complexion, greasy skin, acne, voracious appetite, hyperacidity, diarrhea, irritability, aggressive drive.",
        "balancing_diet": "Cold, moist, heavy foods. Bland foods, steamed vegetables, sweet fruits, fresh milk (minimizing sour yoghurt), sweet grains.",
        "avoid": "Hot chilies, mustard, vinegar, alcohol, excessive meat, deep-fried foods.",
        "indicated_herbs": "Bitter tonics, alteratives, demulcents, cooling sedatives (burdock, dandelion root, chamomile, yarrow)."
    },
    "Low Fire": {
        "qualities": "Deficiency of digestive fire (Agni), vitality, and enthusiasm",
        "symptoms": "Cold pale skin, poor sluggish digestion, food fermentation, gas, depression, low self-esteem, weak immunity against pathogens.",
        "balancing_diet": "Hot, dry, aromatic foods. Warm whole grains cooked with oil and warming spices, ginger, garlic, onions, rock salt, frequent small meals.",
        "avoid": "Cold iced drinks, heavy dairy, raw chilled salads, refined sugar.",
        "indicated_herbs": "Digestive and circulatory stimulants (ginger, cinnamon, cayenne pepper, angelica)."
    },
    "Excess Water": {
        "qualities": "Cold, wet, and heavy (Ayurvedic Kapha - 'what sticks')",
        "symptoms": "Plump soft body, fluid retention, oedema, excess mucous in stomach/lungs, asthma, slow monotone speech, clinginess, possessiveness.",
        "balancing_diet": "Hot, dry, and light foods. Lightly cooked vegetables, beans, pungent spices, light grains (millet, barley).",
        "avoid": "Heavy oily foods, dairy, sweet foods, refined wheat, salt (which retains water), large quantities of melons.",
        "indicated_herbs": "Diaphoretics, diuretics, bitter tonics, expectorants (yarrow, cleavers, couchgrass, elderflowers)."
    },
    "Low Water": {
        "qualities": "Dehydration, stiffness, dry mucous membranes, lack of softness",
        "symptoms": "Dry brittle tissues, lack of emotional buffering, poor joint lubrication, insomnia.",
        "balancing_diet": "Juicy fruits and vegetables, judicious salt, wheat, oats, seaweed, milk, natural honey.",
        "avoid": "Strong diuretics, dry crackers, astringent unlubricated foods.",
        "indicated_herbs": "Demulcents, soothing mucilaginous herbs (liquorice, marshmallow, comfrey, slippery elm)."
    },
    "Excess Earth": {
        "qualities": "Dense, heavy, cold, and slow",
        "symptoms": "Leathery thickened skin, tissue sclerosis, calcium deposits, sluggish elimination, extreme rigidity.",
        "balancing_diet": "Light freshly cooked foods, sprouts, steamed greens, stimulating spices, no desserts.",
        "avoid": "Heavy dairy, dense meats, rich pastries, excess potatoes.",
        "indicated_herbs": "Bitter tonics, digestive and mental stimulants, purgatives (senna, aloes, gentian)."
    },
    "Low Earth": {
        "qualities": "Lack of physical stamina, grounding, and structural minerals",
        "symptoms": "Fragile bones, weak teeth, poor convalescent rebuilding, ungroundedness.",
        "balancing_diet": "Heavy, nutritious, grounding foods. Potatoes, unrefined whole grains, dairy, butter, oils, root vegetables with garlic and onions.",
        "avoid": "Extreme fasting, skipped meals, raw insubstantial snacks.",
        "indicated_herbs": "Nourishing tonics, minerals, seaweeds, bone restoratives (comfrey, horsetail, nettles)."
    }
}

JANE_CASE_STUDIES: List[Dict[str, Any]] = [
    {
        "case_id": "jrp_case_1_tom",
        "case_title": "Case Study 1: Tom — Academic Decumbiture Analysis",
        "case_title_ta": "வழக்கு ஆய்வு 1: டாம் — பேராசிரியரின் நோய்விவர ஜோதிட ஆய்வு",
        "patient_profile": "Male, 43 years, Academic returning from abroad with chronic right-sided abdominal pain and recurrent malaria-like fevers for 10 years.",
        "astrological_indicators": [
            "Ascendant Virgo, Ascendant Lord Mercury exalted in 9th house (unafflicted, shows patient attempting to bear illness bravely alone).",
            "6th house cusp Pisces; 6th lord Jupiter in Taurus in 8th house, square Mars in 5th.",
            "Moon in Gemini in 9th house applying to trine Venus, separating from Mars (corrupted blood, fever, bile).",
            "Right side indication: Jupiter above earth in masculine/nocturnal sign points to right posterior hepatic lobe.",
            "Planetary Hour: Moon ruler of hour sextiles Venus (radicality confirmed)."
        ],
        "outcome_and_remedies": "Mercury herbs indicated immediately (Valerian, hot in 1st, dry in 2nd). Blood and liver cleanse with Jupiterian herbs (Dandelion root, Yellow dock). Gallbladder cooling with small quantities of Gentian and Barberry bark."
    },
    {
        "case_id": "jrp_case_2_angela",
        "case_title": "Case Study 2: Angela — Pituitary Adenoma & Acromegaly",
        "case_title_ta": "வழக்கு ஆய்வு 2: ஏஞ்சலா — பிட்யூட்டரி கட்டி மற்றும் அக்ரோமேகலி",
        "patient_profile": "Female with Aries Sun, Scorpio Moon conjunct Neptune, Mars in Pisces opposite Pluto, and Jupiter in Capricorn.",
        "astrological_indicators": [
            "Pituitary Gland ruled by Capricorn (Anterior Pituitary) and Jupiter (growth/expansion) placed in Capricorn.",
            "Jupiter in Capricorn = Stifled growth postponed until emotional maturity; manifested as Growth Hormone secreting adenoma.",
            "Moon conjunct Neptune in Scorpio = Severe porous psychic boundaries, infant colic, idiopathic oedema, food/silver allergies.",
            "Mars in Pisces opposite Pluto = Repressed assertiveness, digestive sensitivity, surgery for adenoma when Moon was in Aries."
        ],
        "outcome_and_remedies": "Successful transsphenoidal surgical removal in 1994. Upgraded through 3 'M's: Mastication (thorough chewing), Massage (claiming physical boundaries), and Meditation (centering awareness). Assertiveness training and digestive enzymes restored health."
    }
]


# ---------------------------------------------------------------------------
# JANE RIDDER-PATRICK CLASSICAL & CLINICAL MEDICAL ASTROLOGY RULES REGISTRY
# Source: A Handbook of Medical Astrology (2nd Edition), Jane Ridder-Patrick
# ---------------------------------------------------------------------------
JANE_RIDDER_PATRICK_RULES_REGISTRY: Dict[str, ClassicalMedicalRuleDefinition] = {
    "jrp_sun_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_sun_saturn",
        name="Sun–Saturn Tension: Slowed Metabolism & Arteriosclerosis",
        name_tamil="சூரியன்–சனி பார்வை/சேர்க்கை: மெதுவான வளர்சிதை மாற்றம் & தமனி தடிப்பு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Sun–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Sun forms hard aspect (0°, 90°, or 180°) with Saturn",
            "Evaluate constitutional temperature and cardiovascular tone",
        ],
        traditional_interpretation=(
            "According to Jane Ridder-Patrick, Saturn slows down the vital fire of the Sun. Subjects tend to be cool to the touch "
            "yet tolerate cold well. A hallmark is the accumulation of mineral deposits causing tissues to harden, thicken, and lose flexibility, "
            "predisposing to rheumatic stiffness and arteriosclerosis. Later in life, repeated onslaughts on solar vitality produce chronic conditions."
        ),
        interpretation_tamil=(
            "ஜேன் ரிடர்-பேட்ரிக் கூற்றுப்படி, சனி பகவான் சூரியனின் பிராண அக்னியை மட்டுப்படுத்துகிறார். இதனால் உடல் குளிர்ந்து காணப்படும்; "
            "தாது உப்புகள் தேங்கி திசுக்கள் தடித்து நெகிழ்வுத்தன்மை குறையலாம். தமனி தடிப்பு (Arteriosclerosis) மற்றும் மூட்டு விறைப்பு "
            "ஏற்பட வாய்ப்புள்ளது. முதிய வயதில் தீராத நோய்கள் எழாமல் இருக்க முன் எச்சரிக்கை தேவை."
        ),
        anatomical_system="Arterial System, Bone Structure, Basal Metabolism, Connective Tissue",
        modifiers="Benefic aspect from Jupiter softens arterial stiffness; fire sign placements improve warmth.",
        conflicting_indications="Sun exalted in Aries or strong Mars counters hypothermia and circulatory stagnation.",
        remedy_en="Daily morning cold shower or cold water hydrotherapy to stimulate vitality; structured regular exercise; Calcium phosphate (Calc. phos.) tissue salt; Mimulus Bach flower; warm nourishing unrefined diet.",
        remedy_ta="அதிகாலை குளிர்ந்த நீர் குளியல் மூலம் நரம்புகளைத் தூண்டுதல்; முறையான உடற்பயிற்சி; கால்சியம் பாஸ்பேட் (Calc phos) தாது உப்பு; மிமுலஸ் மலர் மருந்து; சத்தான கதகதப்பான உணவு.",
    ),
    "jrp_sun_mars": ClassicalMedicalRuleDefinition(
        id="jrp_sun_mars",
        name="Sun–Mars Dynamic: High Metabolic Fire, Fevers & Acidosis",
        name_tamil="சூரியன்–செவ்வாய் உக்கிரம்: அதீத வளர்சிதை மாற்றம், காய்ச்சல் & அமிலத்தன்மை",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Sun–Mars)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun conjunct, square, or opposite Mars in natal chart",
        mandatory_conditions=[
            "Sun forms hard aspect (0°, 90°, or 180°) with Mars",
            "Examine inflammatory tendencies and basal heat production",
        ],
        traditional_interpretation=(
            "Ridder-Patrick records that Mars in hard aspect to Sun produces an accelerated basal metabolic rate. Individuals emit copious heat "
            "yet subjectively feel chills. There is a strong tendency toward systemic acidosis, rapid waste accumulation, acute high fevers, "
            "and inflammatory conditions. Eliminative organs must function optimally to expel metabolic wastes promptly."
        ),
        interpretation_tamil=(
            "சூரியன்–செவ்வாய் தீவிர சேர்க்கை அல்லது பார்வை உடலில் அதீத உஷ்ணத்தையும், விரைவான வளர்சிதை மாற்றத்தையும் உருவாக்கும். "
            "உடலில் அமிலத்தன்மை (Acidosis) அதிகரித்தல், திடீர் அதிகக் காய்ச்சல், அழற்சி மற்றும் தீக்காயப் பாதிப்புகள் ஏற்படலாம். "
            "கழிவகற்றும் உறுப்புகள் முறையாகச் செயல்படுவது இன்றியமையாதது."
        ),
        anatomical_system="Immune Inflammatory Response, Muscular Heat Production, Adrenal Medulla, Blood Fibrinogen",
        modifiers="Cooling signs (Taurus, Cancer, Pisces) mitigate febrile spikes; Jupiter aspect protects blood purity.",
        conflicting_indications="Saturn aspect cools inflammation, though it may turn acute states into stiffness.",
        remedy_en="Alkaline, cooling diet with frequent light meals to compensate for energy expenditure; fresh chamomile and eyebright tea; Potassium phosphate (Kali phos); Impatiens Bach flower; avoiding violent stimulants.",
        remedy_ta="காரத்தன்மை கொண்ட குளிர்ச்சியான உணவு முறை; சிறிய அளவிலான அடிக்கடி உணவு; சீமைச்சாமந்தி (Chamomile) தேநீர்; காலி பாஸ் (Kali phos) உப்பு; இம்பேஷன்ஸ் மலர் மருந்து; அதிக காரம் மற்றும் துரித உணவுகளைத் தவிர்த்தல்.",
    ),
    "jrp_sun_neptune": ClassicalMedicalRuleDefinition(
        id="jrp_sun_neptune",
        name="Sun–Neptune Sensitivity: Compromised Vitality & Porous Boundaries",
        name_tamil="சூரியன்–நெப்டியூன் பலவீனம்: பிராண பலவீனம் & எல்லை மயக்கம்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Sun–Neptune)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun conjunct, square, or opposite Neptune in natal chart",
        mandatory_conditions=[
            "Sun forms hard aspect with Neptune",
            "Assess immune boundary resilience and subtle fatigue",
        ],
        traditional_interpretation=(
            "Neptune breaks down boundaries and renders tissues permeable. Sun–Neptune contacts compromise vitality and immune resistance, "
            "often leading to subtle anaemia, fatigue, and breaks in clear waking consciousness. Individuals are highly susceptible to "
            "reality-altering addictions (alcohol, refined sugars) that act as slow physical self-sabotage, as well as focus-related eye disorders."
        ),
        interpretation_tamil=(
            "நெப்டியூன் உடல் மற்றும் மன எல்லைகளைக் கரைக்கும் தன்மை கொண்டது. சூரியனுடன் தொடர்பு கொள்ளும்போது நோய் எதிர்ப்பு சக்தி மற்றும் "
            "பிராண பலம் குறையலாம். சோகை (Anaemia), தெளிவின்மை, போதை அல்லது சர்க்கரைப் பழக்கங்களுக்கு அடிமையாதல் மற்றும் கண் பார்வைக் "
            "கவனம் தேவைப்படலாம்."
        ),
        anatomical_system="Cellular Membrane Permeability, Pineal Gland, Retinal Focus, Vital Aura",
        modifiers="Strong Mars or Sun in fire signs supplies physical grit; Saturn lends solid protective boundaries.",
        conflicting_indications="Exalted Sun in Aries resists debility.",
        remedy_en="Creative visualization and meditation; strict abstinence from alcohol and reality-dulling substances; Angelica and Rosemary tonics; Rock Rose Bach flower; yellow sunlight therapy to charge the pineal gland.",
        remedy_ta="ஆக்கப்பூர்வமான மனக்காட்சி தியானம்; மது, அதிக சர்க்கரை மற்றும் புகையிலை தவிர்த்தல்; ரோஸ்மேரி மற்றும் ஏஞ்சலிகா மூலிகைகள்; ராக் ரோஸ் மலர் மருந்து; அதிகாலை சூரிய ஒளி குளியல்.",
    ),
    "jrp_sun_uranus": ClassicalMedicalRuleDefinition(
        id="jrp_sun_uranus",
        name="Sun–Uranus Disruption: Cardiac Arrhythmia & Neuro-Circulatory Asthenia",
        name_tamil="சூரியன்–யுரேனஸ் அதிர்வு: இதயத் துடிப்பு ஒழுங்கின்மை & நரம்பு சோர்வு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Sun–Uranus)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun conjunct, square, or opposite Uranus in natal chart",
        mandatory_conditions=[
            "Sun in hard aspect (0°, 90°, 180°) to Uranus",
            "Evaluate biological rhythms (heartbeat, pulse, respiration)",
        ],
        traditional_interpretation=(
            "Sun–Uranus governs the rhythmic pulsations of the organism. Difficult aspects manifest as disrupted cardiac rhythm, atrial fibrillation, "
            "or neuro-circulatory asthenia (effort syndrome / anxiety neurosis mimicking functional autonomic disorders). The body's electrical pacing "
            "becomes erratic, requiring conscious low-stimulus relaxation."
        ),
        interpretation_tamil=(
            "சூரியன்–யுரேனஸ் தொடர்பு உடலின் சீரான தாள லயங்களை (இதயத் துடிப்பு, நாடி, சுவாசம்) குறிக்கிறது. கடுமையான பார்வைகள் "
            "இதயத் துடிப்பு தாறுமாறாதல் (Arrhythmia), நரம்பு வழி இதய பதற்றம் (NCA) மற்றும் பதற்ற நரம்புத் தளர்ச்சியைத் தூண்டலாம்."
        ),
        anatomical_system="Cardiac Pacemaker, Autonomic Nervous System, Membrane Electrical Potential, Pyramidal Tract",
        modifiers="Fixed signs (Leo, Aquarius) concentrate voltage in heart; airy signs agitate nervous impulses.",
        conflicting_indications="Harmonious aspects of Jupiter or Venus restore emotional stability.",
        remedy_en="Low-stimulus downtime; conscious somatic grounding; magnesium-rich diet; Magnesium phosphate (Mag. phos.); Water Violet Bach flower; steady rhythmic pranayama breathing.",
        remedy_ta="அமைதியான சூழலில் ஓய்வு; நரம்பு மண்டலத்தை சாந்தப்படுத்தும் தியானம்; மெக்னீசியம் பாஸ்பேட் (Mag phos) உப்பு; வாட்டர் வயலட் மலர் மருந்து; சீரான பிராணாயாம மூச்சுப் பயிற்சி.",
    ),
    "jrp_sun_pluto": ClassicalMedicalRuleDefinition(
        id="jrp_sun_pluto",
        name="Sun–Pluto Stress: Cellular Transformation & Radical Endurance",
        name_tamil="சூரியன்–புளூட்டோ அழுத்தம்: உயிரணு மாற்றம் & தீவிர சகிப்புத்தன்மை",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Sun–Pluto)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun conjunct, square, or opposite Pluto in natal chart",
        mandatory_conditions=[
            "Sun forms hard aspect with Pluto",
            "Particularly scrutinized if placed in Fixed signs (Taurus, Leo, Scorpio, Aquarius)",
        ],
        traditional_interpretation=(
            "Sun–Pluto grants tremendous stamina and resilience, yet when subjected to prolonged stress beyond the breaking point, "
            "it can lead to dramatic physical breakdowns. Davidson noted that Pluto in a fixed sign afflicting a fixed sign Sun predisposes "
            "to sarcoma (connective tissue malignancy) or deep abscess formation. Regeneration requires addressing psychological survival drives."
        ),
        interpretation_tamil=(
            "சூரியன்–புளூட்டோ சேர்க்கை அபரிமிதமான உடல் சகிப்புத்தன்மையை அளிக்கும்; ஆனால் எல்லையை மீறிய தொடர் மன அழுத்தத்தில் திசுக்கள் "
            "அடிமட்டத்தில் பாதிக்கப்பட்டு கட்டிகள், தீவிர அழற்சி அல்லது ஸ்திர ராசிகளில் இதய பாதிப்புகளை ஏற்படுத்தலாம். ஆழ்ந்த நச்சு நீக்கம் தேவை."
        ),
        anatomical_system="Cell Nucleus, DNA Blueprint, Connective Tissue Integrity, Deep Cellular Elimination",
        modifiers="Sextiles and trines provide peerless recuperation and tissue rebuilding.",
        conflicting_indications="Strong benefic placement in Kendra prevents malign tissue degeneration.",
        remedy_en="Gerson therapy nutritional principles; deep psychological shadow release; radical honesty; Bloodstone or Almandine grounding; Calcium sulphate (Calc. sulph.) cell salt.",
        remedy_ta="கெர்சன் ஊட்டச்சத்து நச்சு நீக்கம்; ஆழ்ந்த உளவியல் ஆலோசனைகள்; கால்சியம் சல்பேட் (Calc sulph) உப்பு; பிளட்ஸ்டோன் ரத்தின சிகிச்சை; தற்காப்புக் கலை அல்லது கடின உடற்பயிற்சி மூலம் தீவிர ஆற்றலை வெளிப்படுத்துதல்.",
    ),
    "jrp_moon_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_moon_saturn",
        name="Moon–Saturn Chill: Water Balance, Mucosa Defects & Depressive Tone",
        name_tamil="சந்திரன்–சனி சேர்க்கை: நீர்ச்சத்து குறைபாடு, சளிச்சவ்வு பலவீனம் & மனச்சோர்வு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Moon–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Moon in hard aspect to Saturn",
            "Assess fluid balance, emotional constriction, and digestive motility",
        ],
        traditional_interpretation=(
            "Saturn constricts the fluid, responsive nature of the Moon. This combination produces slowed emotional responses, restrictive "
            "eating habits, chronic disturbances in the body water balance, defective mucous membranes, and bladder weakness. In women, "
            "it frequently correlates with delayed puberty, dysmenorrhoea, or scanty menses accompanied by depressive tendencies."
        ),
        interpretation_tamil=(
            "சனி சந்திரனின் இயல்பான நீர் ஓட்டத்தை சுருக்குகிறது. இதனால் உடலின் நீர் சமநிலைக் கோளாறுகள், சளிச்சவ்வு வறட்சி, சிறுநீர்ப்பை மென்மை, "
            "பசியின்மை மற்றும் மன உளைச்சல் ஏற்படலாம். பெண்களுக்கு மாதவிடாய் தாமதம் அல்லது வலியைத் தரலாம்."
        ),
        anatomical_system="Body Fluids, Mucous Membranes, Bladder Tone, Limbic Emotional Response, Menstrual Rhythm",
        modifiers="Waxing Moon or Jupiter aspect softens depressive chilling.",
        conflicting_indications="Moon in Taurus or Cancer exhibits innate constitutional moisture.",
        remedy_en="Warm, moist, grounding diet; emotional counseling; White willow and chickweed remedies; Sodium sulphate (Nat. sulph.); Mimulus / Gentian Bach flowers; warm baths with essential oils.",
        remedy_ta="சூடான, சத்தான திரவ உணவுகள்; உளவியல் ஆற்றுப்படுத்துதல்; வெள்ளை வில்லோ மூலிகை; நேட் சல்ப் (Nat sulph) உப்பு; மிமுலஸ் மலர் மருந்து; வெதுவெதுப்பான எண்ணெய் தேய்த்துக் குளித்தல்.",
    ),
    "jrp_moon_neptune": ClassicalMedicalRuleDefinition(
        id="jrp_moon_neptune",
        name="Moon–Neptune Fluidity: Idiopathic Oedema, Allergies & Psychic Porosity",
        name_tamil="சந்திரன்–நெப்டியூன் இணைப்பு: திரவத் தேக்கம், ஒவ்வாமை & அதீத உணர்திறன்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Moon–Neptune)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjunct, square, trine, or opposite Neptune in natal chart",
        mandatory_conditions=[
            "Moon in major aspect to Neptune (including trines which strongly link to sensitivities)",
            "Scrutinize fluid retention, osmotic pressure shifts, and food/metal allergies",
        ],
        traditional_interpretation=(
            "Jane Ridder-Patrick emphasizes that Moon–Neptune erodes emotional and cellular boundaries. Highly impressionable individuals suffer from "
            "osmotic shifts, premenstrual bloating, or full-blown idiopathic oedema where weight fluctuates drastically. Moon–Neptune trines, even more "
            "than hard aspects, correlate with food sensitivities (dairy, wheat, sugar), candida overgrowth, asthma, and metal allergies (especially silver, the metal of Moon)."
        ),
        interpretation_tamil=(
            "சந்திரன்–நெப்டியூன் இணைப்பு உடல் திரவங்கள் மற்றும் உணர்வு எல்லைகளை எளிதில் ஊடுருவச் செய்கிறது. இடியோபாடிக் எடிமா (காரணமற்ற நீர் வீக்கம்), "
            "உணவு ஒவ்வாமை (பால், கோதுமை, சர்க்கரை), ஆஸ்துமா மற்றும் வெள்ளி ஆபரண ஒவ்வாமை ஏற்படலாம். சூழல் உணர்வுகளைத் தன்னுள் உறிஞ்சும் மனநிலை தோன்றும்."
        ),
        anatomical_system="Lymphatic Drainage, Osmotic Pressure, Intracellular Fluid, Immune Boundary Recognition",
        modifiers="Presence in water signs (Cancer, Scorpio, Pisces) magnifies fluid swelling.",
        conflicting_indications="Saturn aspect imposes firm boundary limits and dispels psychic fog.",
        remedy_en="Practice the 3 'M's: Mastication (thorough chewing of food & experience), Massage (claiming physical skin boundaries), and Meditation (centering awareness); avoid pasteurized dairy; Clematis / Rock Rose Bach flowers; Natrum muriaticum.",
        remedy_ta="மூன்று 'M' பயிற்சி: மென்று உண்ணுதல் (Mastication), தைல மசாஜ் (Massage - தோல் எல்லையை உணர்தல்), தியானம் (Meditation); பதப்படுத்தப்பட்ட பால் பொருட்களைத் தவிர்த்தல்; கிளிமேடிஸ் மலர் மருந்து; நேட் மியூர் உப்பு.",
    ),
    "jrp_moon_mars": ClassicalMedicalRuleDefinition(
        id="jrp_moon_mars",
        name="Moon–Mars Friction: Repressed Anger, Bilious Nausea & Hyperthyroidism",
        name_tamil="சந்திரன்–செவ்வாய் முரண்பாடு: அடக்கிய கோபம், பித்த குமட்டல் & தைராய்டு பாதிப்பு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Moon–Mars)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjunct, square, or opposite Mars in natal chart",
        mandatory_conditions=[
            "Moon forms hard aspect with Mars",
            "Examine emotional assertiveness, bile secretion, and thyroid status",
        ],
        traditional_interpretation=(
            "Conflict between the need to nurture (Moon) and the drive to fight (Mars). Carter and Ridder-Patrick state that when emotional "
            "anger does not find an external constructive outlet, it turns inward, undermining health. Clinically manifests as copious menses, "
            "bilious nausea, reddish skin eruptions, and involuntary muscle twitches. Reinhold Ebertin linked it directly with Graves' disease (hyperthyroidism)."
        ),
        interpretation_tamil=(
            "பராமரிக்கும் குணம் (சந்திரன்) மற்றும் மோதும் குணம் (செவ்வாய்) இடையேயான முரண்பாடு. அடக்கப்பட்ட கோபம் உள்ளுறுப்புகளை தாக்கி, "
            "அதிக ரத்தப்போக்கு, பித்த குமட்டல், சிவப்பு தடிப்புகள் மற்றும் தைராய்டு அதீத சுரப்பு (கிரேவ்ஸ் நோய்) ஏற்பட வழிவகுக்கும்."
        ),
        anatomical_system="Thyroid Gland, Gastric Motility, Bilious Secretions, Involuntary Muscular Action, Menstruation",
        modifiers="Benefic aspects from Jupiter convert martial friction into righteous vitality.",
        conflicting_indications="Venus in good dignity soothes emotional temper.",
        remedy_en="Assertiveness training; active physical sports or martial arts; cooling bitter tonics (gentian, barberry); Potassium phosphate (Kali phos); Impatiens Bach flower; avoiding overheated emotional confrontations.",
        remedy_ta="சுய உரிமையை வெளிப்படுத்தும் பயிற்சி; யோகா மற்றும் உடற்பயிற்சி; கசப்புச் சுவை கொண்ட மூலிகைகள் (Dandelion, Barberry); காலி பாஸ் உப்பு; இம்பேஷன்ஸ் மலர் மருந்து; வீண் வாக்குவாதங்களைத் தவிர்த்தல்.",
    ),
    "jrp_moon_uranus": ClassicalMedicalRuleDefinition(
        id="jrp_moon_uranus",
        name="Moon–Uranus Tension: Visceral Colic, Neuro-Glandular Spasms & Bulimia",
        name_tamil="சந்திரன்–யுரேனஸ் அதிர்வு: உள்ளுறுப்பு வலி, நரம்பு பிடிப்பு & உணவு முறை ஒழுங்கின்மை",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Moon–Uranus)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjunct, square, or opposite Uranus in natal chart",
        mandatory_conditions=[
            "Moon forms hard aspect with Uranus",
            "Examine visceral smooth muscle spasms and autonomic stability",
        ],
        traditional_interpretation=(
            "Psychologically manifests as unpredictable emotional electricity and lack of felt safety. Pathologically, Uranus induces "
            "spasmodic colic in fluid-containing or fluid-excreting organs (bladder, colon, gall bladder, prostate) and blood pressure instability. "
            "Sufferers frequently override bodily rhythms (delaying menses at will, ignoring prompts to eat or sleep, or developing bulimic gorge-and-purge cycles)."
        ),
        interpretation_tamil=(
            "உணர்ச்சித் தளத்தில் மின்னல் போன்ற திடீர் மாற்றங்கள் தோன்றும். சிறுநீர்ப்பை, குடல், பித்தப்பை போன்ற உள்ளுறுப்புகளில் திடீர் பிடிப்பு வலிகள் "
            "(Colic), ரத்த அழுத்த மாறுபாடுகள், மற்றும் உடலின் பசி, தூக்க சுழற்சிகளை மீறி நடக்கும் போக்குகள் (Bulimia) ஏற்படலாம்."
        ),
        anatomical_system="Visceral Smooth Muscle, Bladder & Colon Sphincters, Neuro-Hormonal Rhythms, Blood Pressure",
        modifiers="Earth sign placements anchor electrical surges.",
        conflicting_indications="Saturn trine stabilizes autonomic periodicity.",
        remedy_en="Strict routine for meals and sleep; low-stimulus relaxation; Magnesium phosphate (Mag. phos.); Water Violet Bach flower; grounding breathing exercises.",
        remedy_ta="சீரான உணவு மற்றும் தூக்க அட்டவணை; அமைதியான சூழல்; மெக்னீசியம் பாஸ்பேட் (Mag phos) தாது உப்பு; வாட்டர் வயலட் மலர் மருந்து; நரம்புகளை அமைதிப்படுத்தும் பயிற்சிகள்.",
    ),
    "jrp_moon_pluto": ClassicalMedicalRuleDefinition(
        id="jrp_moon_pluto",
        name="Moon–Pluto Holding: Endometriosis, Fibroids & Deep Visceral Cleansing",
        name_tamil="சந்திரன்–புளூட்டோ தேக்கம்: எண்டோமெட்ரியோசிஸ், கருப்பை கட்டிகள் & குடல் கழிவு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Moon–Pluto)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Moon conjunct, square, or opposite Pluto in natal chart",
        mandatory_conditions=[
            "Moon forms hard aspect with Pluto",
            "Examine reproductive and lower bowel eliminative integrity",
        ],
        traditional_interpretation=(
            "Pluto intensifies lunar reproductive and eliminative processes. Women with Moon–Pluto aspects frequently experience "
            "fibroids, endometriosis, severe menorrhagia, intense childbirth crises, or disturbances of bowel function requiring surgical "
            "intervention. Deep holding patterns represent fear of emotional vulnerability; healing occurs when intuitive power and bodily ripening are embraced."
        ),
        interpretation_tamil=(
            "புளூட்டோ சந்திரனின் இனப்பெருக்க மற்றும் கழிவகற்றும் உறுப்புகளில் தீவிர தாக்கத்தை ஏற்படுத்துகிறது. பெண்களுக்கு கருப்பை நார்த்திசுக்கட்டிகள் "
            "(Fibroids), எண்டோமெட்ரியோசிஸ், அதிக உதிரப்போக்கு அல்லது பெருங்குடல் கழிவுத் தேக்கப் பிரச்சினைகள் ஏற்படலாம். அடிவயிற்று நச்சு நீக்கம் அவசியம்."
        ),
        anatomical_system="Uterus, Endometrium, Ovarian Follicles, Sigmoid Colon, Pelvic Lymphatics",
        modifiers="Benefic aspect from Jupiter eases pelvic stagnation.",
        conflicting_indications="Venus in Taurus or Libra provides natural hormonal balance.",
        remedy_en="Pelvic castor oil packs; colon detox; psychological acceptance of emotional boundaries; Calcium sulphate (Calc. sulph.); Chicory Bach flower; radical nutritional cleansing.",
        remedy_ta="அடிவயிற்று விளக்கெண்ணெய் ஒத்தடம்; குடல் நச்சு நீக்கம்; உணர்ச்சி வடிகால் பயிற்சிகள்; கால்கேரியா சல்பேட் (Calc sulph) உப்பு; சிக்கரி மலர் மருந்து; நார்ச்சத்து நிறைந்த உணவுகள்.",
    ),
    "jrp_mars_neptune": ClassicalMedicalRuleDefinition(
        id="jrp_mars_neptune",
        name="Mars–Neptune: The Classical Pathological Aspect (Autoimmune & Low Resistance)",
        name_tamil="செவ்வாய்–நெப்டியூன் இணைப்பு: 'நோயியல் அம்சம்' — தன்னுடல் தாக்குதல் & குறைந்த எதிர்ப்பு சக்தி",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Mars–Neptune)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars conjunct, square, or opposite Neptune in natal chart",
        mandatory_conditions=[
            "Mars forms hard aspect with Neptune",
            "Evaluate white blood cell defense, autoimmune markers, and insidious infections",
        ],
        traditional_interpretation=(
            "Jane Ridder-Patrick titles this 'the pathological aspect' because Mars, the warrior of bodily defense, is confused and undermined "
            "by Neptune's diffuseness. The body does not know whether to attack or surrender, leading to autoimmune disorders where immune cells "
            "turn upon the host's own tissues, as well as chronic pus discharges and low-grade elusive infections. Transmuted through altruistic causes."
        ),
        interpretation_tamil=(
            "மருத்துவ ஜோதிடத்தில் இது 'நோயியல் சேர்க்கை' என அழைக்கப்படுகிறது. உடலின் பாதுகாப்பு வீரனான செவ்வாய், நெப்டியூனின் எல்லையற்ற "
            "மயக்கத்தால் குழம்பி, உடலின் சொந்த திசுக்களையே தாக்கும் 'தன்னுடல் தாக்குதல்' (Autoimmune) நோய்களையும், நாள்பட்ட மர்மமான தொற்றுகளையும் உருவாக்கலாம்."
        ),
        anatomical_system="White Blood Cells, Lymphocyte Recognition, Muscular Tone, Pus Elimination",
        modifiers="Mars in Capricorn (exalted) maintains structural resistance despite Neptunian mist.",
        conflicting_indications="Sun in fiery signs fortifies the core vitality.",
        remedy_en="Dedication of physical energy to a noble altruistic cause; alterative immune-modulating herbs (burdock, yellow dock, sarsaparilla); Ferrum phosphate (Ferr. phos.); Rock Rose Bach flower; avoiding martyrdom dynamics.",
        remedy_ta="சுயநலமற்ற அறப்பணிகளில் உடலுழைப்பை செலுத்துதல்; இரத்தத்தை சுத்தி செய்யும் மூலிகைகள் (Burdock, Sarsaparilla); பெர்ரம் பாஸ்பேட் (Ferr phos) உப்பு; ராக் ரோஸ் மலர் மருந்து; மருத்துவ நிபுணரின் வழிகாட்டல்.",
    ),
    "jrp_mars_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_mars_saturn",
        name="Mars–Saturn Tension: Joint Inflammation, Arthritis & Gallstones",
        name_tamil="செவ்வாய்–சனி முரண்பாடு: மூட்டு அழற்சி, வாத நோய் & பித்தப்பை கற்கள்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Mars–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mars conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Mars forms hard aspect with Saturn",
            "Examine bone formation, red blood cells, joint synovial fluid, and bile concentration",
        ],
        traditional_interpretation=(
            "Mars (inflammatory heat) collides with Saturn (cold contraction and crystallization). The classic manifestation is joint inflammation "
            "alternating with chronic stiffness, as seen in arthritis, bone malformations, and pathological fractures. It also governs gallstone formation "
            "from crystallized bile salts and impaired red cell maturation in the bone marrow."
        ),
        interpretation_tamil=(
            "செவ்வாயின் அக்னி வெப்பமும் சனியின் குளிர்ந்த இறுகும் தன்மையும் மோதும் போது மூட்டு அழற்சி (Arthritis), எலும்பு தேய்மானம், "
            "மற்றும் பித்தப்பையில் கற்கள் (Gallstones) உருவாகும் சூழல் ஏற்படுகிறது. ஒழுங்கமைக்கப்பட்ட உடற்பயிற்சி மூலம் இதனை சமநிலைப்படுத்தலாம்."
        ),
        anatomical_system="Articular Joints, Bone Marrow, Red Blood Cell Synthesis, Gall Bladder Bile Concentration",
        modifiers="Mars in Capricorn reconciles both planetary energies; benefic Jupiter aspect alleviates joint pain.",
        conflicting_indications="Strong Venus maintains synovial fluid lubrication.",
        remedy_en="Disciplined martial arts or structured physiotherapy (karate, resistance training); antirheumatic herbs (celery seed, angelica, bogbean); Calcium phosphate (Calc. phos.); Centaury / Mimulus Bach flowers.",
        remedy_ta="கராத்தே அல்லது சீரான தசைப் பயிற்சி; வாதம் தணிக்கும் மூலிகைகள் (Celery seed, Angelica); கால்கேரியா பாஸ்பேட் உப்பு; செண்டாரி மலர் மருந்து; மூட்டுகளுக்கு வெதுவெதுப்பான ஒத்தடம்.",
    ),
    "jrp_mercury_mars": ClassicalMedicalRuleDefinition(
        id="jrp_mercury_mars",
        name="Mercury–Mars Irritability: Motor Nerve Tension, Tics & Spasticity",
        name_tamil="புதன்–செவ்வாய் உக்கிரம்: நரம்பு எரிச்சல், துடிப்பு & தசை பிடிப்பு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Mercury–Mars)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mercury conjunct, square, or opposite Mars in natal chart",
        mandatory_conditions=[
            "Mercury forms hard aspect with Mars",
            "Assess motor nerve conduction, reflex excitability, and speech velocity",
        ],
        traditional_interpretation=(
            "Mercury represents neural pathways; Mars introduces violent heat and speed. Hard aspects create motor nerve irritability, "
            "involuntary twitchings, tics, nervous tissue inflammation, and spastic tremors. When anxiety surges, it frequently triggers "
            "bilious diarrhea accompanied by intense thirst."
        ),
        interpretation_tamil=(
            "புதன் நரம்பு மண்டலத்தையும், செவ்வாய் உஷ்ண வேகத்தையும் குறிக்கின்றன. இச்சேர்க்கை மோட்டார் நரம்புகளில் அதீத தூண்டுதலை உண்டாக்கி, "
            "கண் அல்லது தசை துடிப்பு (Tics), நரம்பு அழற்சி மற்றும் பதற்றத்தால் ஏற்படும் பித்த வயிற்றுப்போக்கை உருவாக்கலாம்."
        ),
        anatomical_system="Motor Efferent Nerves, Neuromuscular Junction, Enteric Nerve Motility, Speech Articulation",
        modifiers="Placement in Gemini or Virgo speeds up nervous impulse; Jupiter aspect broadens patience.",
        conflicting_indications="Saturn aspect slows down neural firing, transforming tics into stiffness.",
        remedy_en="Nervine tonics to soothe nerve sheath (valerian, skullcap, passionflower); eliminating caffeine and energy drinks; Potassium phosphate (Kali phos); Impatiens Bach flower; conscious breath pacing.",
        remedy_ta="நரம்புகளை சாந்தப்படுத்தும் மூலிகைத் தேநீர் (Valerian, Passionflower); காபி, தேநீர் மற்றும் செயற்கை குளிர்பானங்களைத் தவிர்த்தல்; காலி பாஸ் உப்பு; இம்பேஷன்ஸ் மலர் மருந்து.",
    ),
    "jrp_mercury_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_mercury_saturn",
        name="Mercury–Saturn Retardation: Auditory Ossicle Stiffness & Dyslexia",
        name_tamil="புதன்–சனி மந்தம்: காது எலும்பு இறுக்கம், பேச்சுக் குறைபாடு & மூட்டு வலி",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Mercury–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mercury conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Mercury forms hard aspect with Saturn",
            "Assess auditory nerve & middle ear bones, speech fluency, and cognitive processing speed",
        ],
        traditional_interpretation=(
            "Saturn restrains and cools Mercury's nervous communication. Clinically correlates with under-functioning of the nervous system, "
            "specifically the auditory nerve and tiny middle ear bones (ruled by Saturn), predisposing to hearing impairment and tinnitus. "
            "Commonly found in cases of developmental dyslexia, delayed speech articulation, and deep dull pain in the joints."
        ),
        interpretation_tamil=(
            "சனி புதனின் நரம்புத் தொடர்பை மட்டுப்படுத்துகிறது. இதனால் நடுச்செவி சிற்றெலும்புகள் (Middle ear bones) மற்றும் செவி நரம்புகளில் "
            "மந்தம் ஏற்பட்டு கேட்கும் திறன் குறைபாடு, டின்னிடஸ் (Tinnitus), பேச்சில் தயக்கம் அல்லது மூட்டுகளில் மந்தமான வலி ஏற்படலாம்."
        ),
        anatomical_system="Auditory Nerve, Middle Ear Ossicles, Speech Centers (Broca's area), Joint Nerve Supply",
        modifiers="Air signs mitigate speech delay; earth signs intensify acoustic stiffness.",
        conflicting_indications="Sun conjunct Mercury (Cazimi) preserves sharp mental clarity.",
        remedy_en="Vocal articulation and singing exercises; ear warmth therapy; warm nervine spices (fennel, dill, liquorice); Silicon oxide (Silica); Mimulus Bach flower; warm ear oil drops (Karna Poorana).",
        remedy_ta="குரல் பயிற்சி மற்றும் மந்திர உச்சரிப்பு; காதுகளுக்கு கதகதப்பான நல்லெண்ணெய் சிகிச்சை; பெருஞ்சீரகம், அதிமதுரம் உட்கொள்ளுதல்; சிலிக்கா தாது உப்பு; மிமுலஸ் மலர் மருந்து.",
    ),
    "jrp_venus_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_venus_saturn",
        name="Venus–Saturn Stasis: Endocrine Hypofunction, Renal Sclerosis & Varicose Veins",
        name_tamil="சுக்கிரன்–சனி தேக்கம்: நாளமில்லா சுரப்பி மந்தம், சிறுநீரக இறுக்கம் & நரம்பு சுருளல்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Venus–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Venus conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Venus in hard aspect to Saturn",
            "Scrutinize venous return, hormonal output, and renal tubule elasticity",
        ],
        traditional_interpretation=(
            "Venus rules balance, venous return, and hormonal feedback; Saturn introduces sclerosis and atrophy. Hard aspects lead to under-functioning "
            "of endocrine glands (compensatory enlargement such as goitre), emphysema of pulmonary alveoli, hardening of kidney tubules, "
            "and venous stasis. Venus conjunct Saturn in Aquarius is particularly documented for varicose veins in the lower extremities."
        ),
        interpretation_tamil=(
            "சுக்கிரன் ஹார்மோன் சமநிலையையும், சனி சுருங்குதலையும் குறிக்கின்றன. இதனால் தைராய்டு சுரப்புக் குறைவு (Goitre), சிறுநீரகக் குழாய்கள் "
            "தடித்தல் மற்றும் கால்களில் நரம்பு சுருண்டு வீங்குதல் (Varicose veins - குறிப்பாக கும்பத்தில் இவ்விருவர் இணையும் போது) ஏற்படலாம்."
        ),
        anatomical_system="Venous Circulation, Endocrine Regulatory Feedback, Kidney Glomeruli, Pulmonary Alveoli",
        modifiers="Benefic aspect from Jupiter eases venous pressure; fire signs stimulate glandular secretion.",
        conflicting_indications="Venus in own signs (Taurus, Libra) retains homeostatic resilience.",
        remedy_en="Leg elevation; daily brisk walking to activate calf muscle venous pumps; Burdock and Lady's mantle; Calcium fluoride (Calc. fluor.); Scleranthus Bach flower; emerald / copper vibrational balancing.",
        remedy_ta="கால்களை உயர்த்தி வைத்து ஓய்வெடுத்தல்; தினமும் நடைப்பயிற்சி மூலம் கால் நரம்பு ஓட்டத்தை சீராக்குதல்; பரங்கிப்பட்டை, லேடிஸ் மேண்டில் மூலிகைகள்; கால்கேரியா புளோர் (Calc fluor) உப்பு; ஸ்கிளராந்தஸ் மலர் மருந்து.",
    ),
    "jrp_jupiter_saturn": ClassicalMedicalRuleDefinition(
        id="jrp_jupiter_saturn",
        name="Jupiter–Saturn Tension: Sluggish Liver Metabolism & Arterial Rigidity",
        name_tamil="குரு–சனி முரண்பாடு: மந்தமான கல்லீரல் செயல்பாடு & தமனி இறுக்கம்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Jupiter–Saturn)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Jupiter conjunct, square, or opposite Saturn in natal chart",
        mandatory_conditions=[
            "Jupiter in hard aspect to Saturn",
            "Assess liver size and detoxification, arterial elasticity, and mood fluctuation",
        ],
        traditional_interpretation=(
            "Jupiter governs liver synthesis and arterial expansion; Saturn restricts and hardens. Hard aspects produce an under-functioning, "
            "often small or congested liver, sluggish bile emulsification of fats, gall bladder colic, and arterial hardening associated with high "
            "blood pressure. Psychologically leads to seesawing between exuberant optimism and deep pessimism."
        ),
        interpretation_tamil=(
            "குரு கல்லீரல் கொழுப்பு செரிமானத்தையும், சனி சுருங்குதலையும் ஆள்கின்றனர். இவ்விருவர் முரண்பாடு கல்லீரல் மந்தம், பித்தப்பைக் கோளாறுகள், "
            "மற்றும் தமனி தடிப்பினால் உண்டாகும் ரத்த அழுத்தத்தை (Hypertension) உருவாக்கலாம். மனநிலையில் அதீத நம்பிக்கையும் சோர்வும் மாறி மாறி வரும்."
        ),
        anatomical_system="Hepatic Lobes, Gall Bladder Bile Synthesis, Arterial Walls, Fat Emulsification",
        modifiers="Jupiter in Cancer (exalted) shields liver parenchyma; Sun aspect boosts arterial vitality.",
        conflicting_indications="Benefic Mars aspect stimulates active circulation.",
        remedy_en="Liver decongestant tonics (dandelion root, yellow dock, agrimony); low saturated-fat diet; Sodium sulphate (Nat. sulph.); Agrimony Bach flower; steady disciplined physical routine.",
        remedy_ta="கல்லீரல் சுத்தி மூலிகைகள் (Dandelion root, Agrimony); குறைந்த கொழுப்புள்ள சமச்சீர் உணவு; சோடியம் சல்பேட் (Nat sulph) உப்பு; அக்ரிமனி மலர் மருந்து; சீரான உடற்பயிற்சி.",
    ),
    "jrp_jupiter_neptune": ClassicalMedicalRuleDefinition(
        id="jrp_jupiter_neptune",
        name="Jupiter–Neptune Permeability: Waterlogged Tissues & Gas Fermentation",
        name_tamil="குரு–நெப்டியூன் பலவீனம்: திசுக்களில் நீர் கசிவு & குடல் வாயு உப்புசம்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 3: The Planets and Aspects (Jupiter–Neptune)",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Jupiter conjunct, square, or opposite Neptune in natal chart",
        mandatory_conditions=[
            "Jupiter in hard aspect to Neptune",
            "Evaluate small arterial permeability, liver enzyme potency, and intestinal gas",
        ],
        traditional_interpretation=(
            "Neptune renders small arterial walls abnormally permeable, allowing fluid leakage into interstitial tissues (waterlogged boggy tissues). "
            "Hepatic enzyme metabolism becomes deficient, leaving food particles incompletely digested; this results in excessive intestinal fermentation, "
            "severe gas bloating, and floating fatty or clay-coloured stools. Misdiagnoses are extremely frequent."
        ),
        interpretation_tamil=(
            "நெப்டியூன் தமனிகளின் சுவர்களை அதீத கசிவுத்தன்மை கொண்டதாக மாற்றுகிறது; இதனால் திசுக்களில் நீர் தேங்கி உடல் பருமன் போலத் தோன்றும். "
            "செரிமான என்சைம்கள் குறைந்து குடலில் வாயு உற்பத்தியாகி வயிறு உப்பும்; மிதக்கும் கொழுப்பு கலந்த கழிவுகள் வெளியேறலாம்."
        ),
        anatomical_system="Arterial Capillaries, Liver Detoxification Enzymes, Intestinal Gas Balance, Stool Consistency",
        modifiers="Virgo emphasis demands strict food hygiene; fire signs help burn off swampy dampness.",
        conflicting_indications="Saturn aspect dries up excessive mucosal leakage.",
        remedy_en="Digestive enzymes; bitter digestive stimulants (gentian, barberry); avoiding rich creamy foods and excess alcohol; Potassium sulphate (Kali. sulph.); Scleranthus Bach flower.",
        remedy_ta="இயற்கை செரிமான என்சைம்கள்; கசப்பு மூலிகைகள் (ஜென்சியன், பார்மெர்ரி); அதிக கொழுப்பு, மது மற்றும் பால் உணவுகளைத் தவிர்த்தல்; பொட்டாசியம் சல்பேட் உப்பு; ஸ்கிளராந்தஸ் மலர் மருந்து.",
    ),
    "jrp_cardinal_cross_reflex": ClassicalMedicalRuleDefinition(
        id="jrp_cardinal_cross_reflex",
        name="Cardinal Cross Reflex Axis: Regulation, Structure & Endocrine Interplay",
        name_tamil="சர ராசி முரண் அச்சு: கட்டுப்பாடு, கட்டமைப்பு & நாளமில்லா சுரப்பி ஒருங்கிணைப்பு",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 4: The Signs and Houses (The Cardinal Cross)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Two or more planets in hard aspect across Cardinal signs (Aries, Cancer, Libra, Capricorn)",
        mandatory_conditions=[
            "Multiple planets situated in Cardinal quadruplicity signs",
            "Examine reflex organ axes: Adrenals <-> Kidneys <-> Water mucosa <-> Pituitary/Skeleton",
        ],
        traditional_interpretation=(
            "The Cardinal Cross is the cross of Regulation, Structure, and Protection. The four signs act in an intimately linked reflex loop: "
            "Aries rules the adrenals (blood pressure and fight-or-flight); Libra rules the kidneys (blood filtration, sugar balance, sodium retention); "
            "Cancer rules body water and protective mucous membranes; Capricorn rules the anterior pituitary (master regulator of adrenals and bones). "
            "Affliction in one sign reflexly disturbs the entire protective endocrine chain."
        ),
        interpretation_tamil=(
            "சர ராசிகளான மேஷம் (அட்ரினல்), கடகம் (உடல் நீர், சளிச்சவ்வு), துலாம் (சிறுநீரகம், சர்க்கரை சமநிலை), மகரம் (பிட்யூட்டரி, எலும்பு) "
            "ஆகிய நான்கும் உடலின் கட்டுப்பாட்டு சங்கிலியாகும். ஒன்றில் ஏற்படும் அழுத்தம் மற்ற உறுப்புகளில் எதிரொலித்து (Reflex action) "
            "நீர் தேக்கம், தலைவலி, சர்க்கரை மற்றும் ரத்த அழுத்த மாற்றங்களை உண்டாக்கும்."
        ),
        anatomical_system="Pituitary–Adrenal–Renal Axis, Mucous Membranes, Skeleton and Bone Density",
        modifiers="Benefics in Cardinal angles preserve homeostatic equilibrium.",
        conflicting_indications="Lagna lord strong in Kendra minimizes reflex systemic spread.",
        remedy_en="Balancing water and sodium intake; kidney flushing herbal infusions (cleavers, couchgrass); endocrine-soothing foods; Calc. fluor. and Nat. phos. cell salts; maintaining strict sleep rhythm for the pituitary.",
        remedy_ta="உப்பு மற்றும் நீர் உட்கொள்ளலை சமநிலையில் வைத்தல்; சிறுநீரக கழிவகற்றும் மூலிகை நீர்; பிட்யூட்டரி சுரப்பியை பாதுகாக்க சரியான தூக்க முறை; கால்கேரியா புளோர் மற்றும் நேட் பாஸ் உப்புகள்.",
    ),
    "jrp_fixed_cross_reflex": ClassicalMedicalRuleDefinition(
        id="jrp_fixed_cross_reflex",
        name="Fixed Cross Reflex Axis: Vital Functions, Organ Engorgement & Cellular Proliferation",
        name_tamil="ஸ்திர ராசி முரண் அச்சு: பிராண இயக்கங்கள், இரத்த ஓட்டம் & உயிரணு பெருக்கம்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 4: The Signs and Houses (The Fixed Cross)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Two or more planets in hard aspect across Fixed signs (Taurus, Leo, Scorpio, Aquarius)",
        mandatory_conditions=[
            "Multiple planets situated in Fixed quadruplicity signs",
            "Examine reflex links: Thyroid <-> Colon/Reproductive; Heart <-> Calf Venous Circulation",
        ],
        traditional_interpretation=(
            "The Fixed Cross governs the Vital Functions: cardiovascular, reproductive, excretory, and reptilian brain instincts. "
            "Fixed signs are aggregative, tending to hold fast, accumulate toxic wastes, and proliferate cellular overgrowth (cysts, benign tumours, stones). "
            "Classic reflex pairs: Taurus (neck/thyroid) reflexes into Scorpio (pelvic organs/colon); Leo (heart/spine) reflexes into Aquarius (calf muscle venous pump and spinal motor tracts)."
        ),
        interpretation_tamil=(
            "ஸ்திர ராசிகளான ரிஷபம் (தொண்டை/தைராய்டு), சிம்மம் (இதயம்/முதுகுத்தண்டு), விருச்சிகம் (பெருங்குடல்/பாலியல் உறுப்புகள்), "
            "கும்பம் (கால் நரம்புகள்/சுழற்சி) ஆகியவை உடலின் அடிப்படை வாழ்வாதாரத்தை ஆள்கின்றன. இவை கழிவுகளை அடக்கி வைத்து கட்டிகள், "
            "கற்கள் அல்லது நரம்பு வீக்கத்தை உருவாக்கலாம். தீவிர உடற்பயிற்சி மற்றும் மலக்குடல் சுத்தி அவசியம்."
        ),
        anatomical_system="Cardiovascular System, Endocrine Thyroid, Pelvic Reproductive Organs, Venous Return, Deep Colon",
        modifiers="Harmonious aspects of Sun prevent cardiovascular stagnation.",
        conflicting_indications="Strong Mars provides dynamic centrifugal cleansing.",
        remedy_en="Cardiovascular walking and swimming; colon cleansing high-fiber diet; thyroid nutritional support (kelp, seaweeds); Mag. phos. and Calc. sulph. cell salts; avoiding rich aggregative foods.",
        remedy_ta="தினமும் நடைப்பயிற்சி மற்றும் நீச்சல்; குடல் கழிவகற்றும் நார்ச்சத்து உணவுகள்; தைராய்டு ஊட்டச்சத்து (கடல் பாசி); மெக் பாஸ் மற்றும் கால்கேரியா சல்பேட் உப்புகள்; அதிக கொழுப்பு உணவுகளைத் தவிர்த்தல்.",
    ),
    "jrp_mutable_cross_reflex": ClassicalMedicalRuleDefinition(
        id="jrp_mutable_cross_reflex",
        name="Mutable Cross Reflex Axis: Metabolism, Enteric Belly-Brain & Psychosomatics",
        name_tamil="உபய ராசி முரண் அச்சு: வளர்சிதை மாற்றம், வயிற்று மூளை (ENS) & மனோதத்துவ பாதிப்புகள்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 4: The Signs and Houses (The Mutable Cross)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Two or more planets in hard aspect across Mutable signs (Gemini, Virgo, Sagittarius, Pisces)",
        mandatory_conditions=[
            "Multiple planets situated in Mutable quadruplicity signs",
            "Examine reflex linkages: Gemini (Lungs/Nerves) <-> Sagittarius (Locomotion/Brain); Virgo (Enteric ENS) <-> Pisces (Immune/Pineal)",
        ],
        traditional_interpretation=(
            "The Mutable Cross is the Metabolic Cross (Greek 'metabole' = change and exchange), governing respiratory, digestive, and nervous mediators. "
            "Mutable signs are the least robust due to high sensitivity. Virgo rules the enteric nervous system ('belly brain') and digestive enzymes, "
            "which reflex directly into Pisces (lymphatic and immune dissolution, psychosomatic somatization). When external stress strikes, "
            "the vagus nerve discharges shock into the intestines, causing IBS, diarrhea, or ulcers."
        ),
        interpretation_tamil=(
            "உபய ராசிகளான மிதுனம் (சுவாசம்/நரம்புகள்), கன்னி (குடல் நரம்பு/செரிமானம்), தனுசு (இயக்கம்/பெருமூளை), மீனம் (நிணநீர்/உள்ளுணர்வு) "
            "ஆகியவை உடலின் வளர்சிதை மாற்ற தூதுவர்கள் ஆகும். மன அழுத்தம் ஏற்படும் போது, குடல் நரம்பு மண்டலம் (Belly Brain) பாதிக்கப்பட்டு "
            "IBS, அஜீரணம் அல்லது ஆஸ்துமா போன்ற மனோதத்துவ (Psychosomatic) உடல் உபாதைகள் தோன்றலாம்."
        ),
        anatomical_system="Enteric Nervous System (ENS), Bronchial Airways, Pancreatic Enzymes, Lymphatic Immune Boundary",
        modifiers="Earth placement grounds flighty nervous excitability; water placement soothes gut mucosa.",
        conflicting_indications="Well-placed Mercury or Jupiter strengthens mental-digestive resilience.",
        remedy_en="Virgo Naturopathic approach: pure, unadulterated, whole foods; mindful eating with thorough chewing (Mastication); soothing nervine teas (chamomile, peppermint); Kali. sulph. and Ferr. phos.; Centaury / Cerato Bach flowers.",
        remedy_ta="கன்னி ராசி இயற்கை மருத்துவ முறை: தூய்மையான இயற்கை உணவுகள்; உணவை நன்றாக மென்று உண்ணுதல்; சீமைச்சாமந்தி, புதினா தேநீர்; காலி சல்ப் மற்றும் பெர்ரம் பாஸ் உப்புகள்; செண்டாரி மலர் மருந்து.",
    ),
    "jrp_decumbiture_early_late_asc": ClassicalMedicalRuleDefinition(
        id="jrp_decumbiture_early_late_asc",
        name="Decumbiture Stricture: Premature (<3°) or Protracted (>27°) Ascendant",
        name_tamil="நோய்விவர ஜோதிட எச்சரிக்கை: ஆரம்ப நிலை (<3°) அல்லது தாமதமான (>27°) லக்னம்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 6: The Decumbiture Chart (Strictures on Judgement)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Decumbiture or consultation chart Ascendant is less than 3° or greater than 27° in any sign",
        mandatory_conditions=[
            "Ascendant longitude in sign is < 3.0° or > 27.0°",
            "Cross-verify with patient age or exact moment of confinement to bed",
        ],
        traditional_interpretation=(
            "William Lilly and Jane Ridder-Patrick instruct that if the Ascendant is less than 3 degrees (especially in signs of short ascension), "
            "the ailment is in its embryonic inception—premature for definitive astrological judgment. If 27 degrees or more, the illness is "
            "already deeply ingrained, past its crisis turning point, or the matter has slipped out of the practitioner's direct control."
        ),
        interpretation_tamil=(
            "வில்லியம் லில்லி மற்றும் ஜேன் ரிடர்-பேட்ரிக் கூற்றுப்படி, ஒரு நோய்விவர அல்லது பிரசன்ன லக்னம் 3 பாகைக்குள் இருந்தால், நோய் இன்னும் "
            "முழுமையாக வெளிப்படவில்லை (ஆரம்ப நிலை); 27 பாகைக்கு மேல் இருந்தால், நோய் முற்றிவிட்டது அல்லது முக்கிய திருப்புமுனையைத் தாண்டிவிட்டது "
            "என்பதைக் குறிக்கும். மருத்துவர் மிகுந்த எச்சரிக்கையுடன் அணுக வேண்டும்."
        ),
        anatomical_system="Diagnostic Timing, Disease Chronicity, Crisis Turning Point",
        modifiers="If native is very young or facial marks match Ascendant sign, judgement is permissible.",
        conflicting_indications="Chart taken at exact second patient took to bed overrides stricture.",
        remedy_en="Patient observation; postpone invasive interventions until symptoms consolidate; monitor critical Moon days (45°, 90°, 135°, 180°); support natural vital forces.",
        remedy_ta="நோயாளிக்கு உடனடியாக தீவிர சிகிச்சைகள் செய்யாமல் கவனிப்பில் வைத்தல்; சந்திரனின் முக்கிய திருப்புமுனை நாட்களைக் (Critical Days) கண்காணித்தல்; உடலின் இயற்கை குணமளிக்கும் ஆற்றலை ஆதரித்தல்.",
    ),
    "jrp_decumbiture_via_combusta": ClassicalMedicalRuleDefinition(
        id="jrp_decumbiture_via_combusta",
        name="Decumbiture Stricture: Moon in Via Combusta (15° Libra – 15° Scorpio)",
        name_tamil="நோய்விவர ஜோதிட எச்சரிக்கை: எரிந்த பாதையில் சந்திரன் (15° துலாம் – 15° விருச்சிகம்)",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 6: The Decumbiture Chart (Strictures on Judgement)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Natal or Decumbiture Moon between 195°00' and 225°00' (15° Libra to 15° Scorpio)",
        mandatory_conditions=[
            "Moon is situated in the fiery, turbulent zone of Via Combusta",
            "Scrutinize extreme subjective fear, toxic exacerbations, and emotional turbulence",
        ],
        traditional_interpretation=(
            "The Moon in the Via Combusta ('the fiery way' from 15° Libra to 15° Scorpio) signifies a state of severe internal toxic "
            "agitation, heightened subjective distress, and unpredictable vital flow. Traditional masters warn that remedies may produce paradoxical "
            "reactions or that the patient is panicking beyond objective symptom severity."
        ),
        interpretation_tamil=(
            "சந்திரன் 'எரிந்த பாதையில்' (15° துலாம் முதல் 15° விருச்சிகம் வரை) இருக்கும் போது, உடலின் பிராண ஓட்டம் அமைதியிழந்து, நச்சுத் தேக்கம் "
            "மற்றும் தீவிர மனப்பயத்தை உண்டாக்கும். மருந்துகள் எதிர்பாராத விளைவுகளைத் தரலாம்; நோயாளியின் பயத்தை ஆற்றுப்படுத்துவதே முதல் தேவையாகும்."
        ),
        anatomical_system="Emotional Limbic Axis, Autonomic Fear Response, Toxic Elimination",
        modifiers="Spica conjunction at 24° Libra softens distress.",
        conflicting_indications="Native having natal Ascendant in this degree range tolerates this transit naturally.",
        remedy_en="Cooling demulcent remedies; quiet emotional grounding; calming silver-charged water; Rock Rose Bach flower for panic; avoiding sudden aggressive medical changes.",
        remedy_ta="குளிர்ச்சியான சாந்தப்படுத்தும் மருந்துகள்; மன அமைதி தியானம்; வெள்ளி நாணயம் இட்டு காய்ச்சிய நீர்; பீதி நீங்க ராக் ரோஸ் மலர் மருந்து; அவசர அறுவை சிகிச்சைகளை தவிர்த்தல்.",
    ),
    "jrp_decumbiture_void_moon": ClassicalMedicalRuleDefinition(
        id="jrp_decumbiture_void_moon",
        name="Decumbiture Condition: Void of Course Moon (No Acute Organic Progression)",
        name_tamil="நோய்விவர நிலை: தொடர்பற்ற சந்திரன் (Void of Course Moon)",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 6: The Decumbiture Chart (The Moon's Aspects)",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Moon makes no further major applying aspect before leaving its current sign",
        mandatory_conditions=[
            "Moon is Void of Course",
            "Examine whether immediate health panic will dissolve without structural organic harm",
        ],
        traditional_interpretation=(
            "When the Moon is Void of Course, traditional horary and medical rules judge that 'nothing will come of the matter'. "
            "While remedies may act sluggishly, the acute crisis will not advance into fatal organic destruction. It advises against elective surgery "
            "during this period as procedures may fail to accomplish their desired objective or require repeat intervention."
        ),
        interpretation_tamil=(
            "சந்திரன் ஒரு ராசியைக் கடக்கும் முன் எவ்வித கிரக பார்வையோ சேர்க்கையோ பெறாமல் (Void of Course) இருக்கும் போது, அப்போதைய நோய் "
            "அச்சுறுத்தல் பெரும் ஆபத்தாக மாறாது. எனினும், இக்காலத்தில் திட்டமிடப்பட்ட அறுவை சிகிச்சைகளைத் தவிர்ப்பது நல்லது; ஏனெனில் சிகிச்சை முழு பலன் தராமல் போகலாம்."
        ),
        anatomical_system="Autonomic Stabilization, Post-Surgical Healing Tone, Visceral Recovery",
        modifiers="Void Moon in Taurus, Cancer, Sagittarius, or Pisces is less vulnerable.",
        conflicting_indications="Strong Ascendant lord guarantees smooth recuperation.",
        remedy_en="Rest and recuperation; postponing non-emergency surgery until Moon enters a fruitful sign and makes benefic applying aspects; Clematis Bach flower; gentle supportive fluids.",
        remedy_ta="முழுமையான ஓய்வு; அவசரமில்லாத அறுவை சிகிச்சைகளை சந்திரன் சுப கிரக பார்வை பெறும் வரை ஒத்திவைத்தல்; கிளிமேடிஸ் மலர் மருந்து; எளிய திரவ உணவுகள் உட்கொள்ளுதல்.",
    ),
    "jrp_culpeper_ascendant_fortification": ClassicalMedicalRuleDefinition(
        id="jrp_culpeper_ascendant_fortification",
        name="Culpeper's Golden Injunction: Fortification of the Ascendant Lord",
        name_tamil="கல்பேப்பரின் முதன்மை விதி: லக்னாதிபதியை பலப்படுத்துதல்",
        source="A Handbook of Medical Astrology (Jane Ridder-Patrick)",
        chapter_verse="Chapter 6: The Decumbiture Chart & Chapter 9: Materia Medica",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Evaluates natal Ascendant sign and its governing planetary ruler",
        mandatory_conditions=[
            "Identify the lord of the Ascendant and its elemental temperament",
            "Apply Culpeper's 1st Rule of Astro-Medicine to fortify bodily integrity",
        ],
        traditional_interpretation=(
            "Nicholas Culpeper's foundational rule, highlighted by Jane Ridder-Patrick: 'Fortify the body with herbs of the nature of the "
            "Lord of the Ascendant, 'tis no matter whether he be a Fortune or Infortune in this case.' Strengthening the Lagna lord reinforces "
            "the vital conductor of prana, ensuring the host constitution resists and expels all pathogenic incursions."
        ),
        interpretation_tamil=(
            "17-ஆம் நூற்றாண்டு மாமேதை நிக்கோலஸ் கல்பேப்பர் மற்றும் ஜேன் ரிடர்-பேட்ரிக் வலியுறுத்தும் முதன்மை விதி: லக்னாதிபதி சுபரோ "
            "அசுபரோ, அவரது தன்மைக்குரிய மூலிகைகள் மற்றும் உணவுகளால் உடலின் உயிர் சக்தியை பலப்படுத்த வேண்டும். லக்னாதிபதி வலுப்பெற்றால் உடல் எத்தகைய நோயையும் எதிர்த்து வெல்லும்."
        ),
        anatomical_system="Vital Host Constitution, Pranic Conductivity, Cellular Rebuilding",
        modifiers="Exaltation or own-sign placement of Lagna lord provides inherent constitutional invulnerability.",
        conflicting_indications="Combustion of Lagna lord demands extra gentle non-heating remedies.",
        remedy_en="Consume botanicals, whole foods, and cell salts ruled by your Ascendant lord; wear the corresponding harmonizing metal or gemstone; practice targeted breathing aligned with your rising element.",
        remedy_ta="உங்கள் லக்னாதிபதிக்குரிய மூலிகைகள், முழு தானியங்கள் மற்றும் தாது உப்புகளை உட்கொள்ளுதல்; லக்னாதிபதிக்குரிய ரத்தினம் அல்லது உலோகத்தை அணிதல்; லக்ன பூத தத்துவத்திற்குரிய மூச்சுப் பயிற்சி செய்தல்.",
    ),
}
