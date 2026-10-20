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
