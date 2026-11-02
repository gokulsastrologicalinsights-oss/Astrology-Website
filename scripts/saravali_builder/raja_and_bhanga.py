# scripts/saravali_builder/raja_and_bhanga.py
"""Saravali Chapter 35 (Raja Yogas) & Chapter 39 (Raja Yoga Bhanga / Obstructions).
"""

def get_raja_and_bhanga_rules():
    rules = []

    # 1. Raja Yogas (Chapter 35)
    raja_data = [
        ("RULE-SARAVALI-RAJA-PUSHKALA",
         "Pushkala Yoga (Saravali Ch. 35, v. 144-145)", "புஷ்கல யோகம் (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [1, 4, 7, 10], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "houses": [1, 4, 7, 9, 10, 11], "chart": "d1"}
         ]},
         "Saravali Ch. 35, v. 144-145 extols Pushkala Yoga: The Moon's dispositor and Lagna Lord are in Kendras or friendly signs, while benefics aspect Lagna. The native becomes a sovereign ruler, renowned, riding royal chariots, wealthy, and universally lauded.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 144-145 புஷ்கல யோகத்தைப் போற்றுகிறது: சந்திரனின் அதிபதியும் லக்னாதிபதியும் கேந்திரத்தில் அமர்ந்து, லக்னத்தைச் சுபர்கள் பார்த்தால் அரசனுக்கு நிகரான வாழ்வு, சகல வாகன யோகம் மற்றும் நீங்காத புகழ் கிட்டும்.",
         "Pushkala Sovereign Auspiciousness Principle: Complete harmonization of physical self (Lagna) and emotional soul (Moon dispositor).",
         "புஷ்கல யோக விதி: லக்னமும் சந்திர ராசி அதிபதியும் கேந்திர பலம் பெற்று சுபப் பார்வை பெறுவது அரச யோகத்தை உருவாக்கும்.",
         "Saravali, Ch. 35, Sloka 144-145", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-CHANDRADHI",
         "Chandradhi Yoga (Saravali Ch. 35, v. 20-21)", "சந்திராதி யோகம் (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_relative_house", "planet": "Jupiter", "from_planet": "Moon", "relative_houses": [6, 7, 8], "chart": "d1"},
             {"condition_type": "planet_relative_house", "planet": "Venus", "from_planet": "Moon", "relative_houses": [6, 7, 8], "chart": "d1"},
             {"condition_type": "planet_relative_house", "planet": "Mercury", "from_planet": "Moon", "relative_houses": [6, 7, 8], "chart": "d1"}
         ]},
         "Saravali Ch. 35, v. 20-21: When natural benefics (Mercury, Jupiter, Venus) occupy the 6th, 7th, and 8th from the Moon, Chandradhi Yoga is formed. The native becomes a king, prime minister, commander, long-lived, victorious over rivals, and endowed with wealth.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 20-21: சந்திரனுக்கு 6, 7, 8 ஆகிய இடங்களில் இயற்கை சுப கிரகங்களான புதன், குரு, சுக்கிரன் அமர்வது சந்திராதி யோகம் எனப்படும்; அரசன், பிரதமர் அல்லது தளபதியாகும் தகுதி, எதிரிகளை வெல்லுதல் மற்றும் நீண்ட ஆயுள் நல்கும்.",
         "Lunar Frontal Benefic Array Principle: Benefics flanking opposite houses from the Moon protect the mental core and confer supreme statehood.",
         "சந்திராதி யோக விதி: சந்திரனுக்கு எதிரே உள்ள 6, 7, 8-ல் சுபர்கள் நிற்பது மனதை பலப்படுத்தி மாபெரும் அதிகாரத்தை வழங்கும்.",
         "Saravali, Ch. 35, Sloka 20-21", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-LAGNADHI",
         "Lagnadhi Yoga (Saravali Ch. 34, v. 13)", "லக்னாதி யோகம் (சாராவளி அத்தியாயம் 34)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [6, 7, 8], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "houses": [6, 7, 8], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "houses": [6, 7, 8], "chart": "d1"}
         ]},
         "Saravali Ch. 34, v. 13: When natural benefics (Mercury, Jupiter, Venus) occupy the 6th, 7th, and 8th from Lagna without malefic conjunctions, Lagnadhi Yoga forms, bestowing scholarly leadership, virtuous character, wealth, and high office.",
         "சாராவளி அத்தியாயம் 34, சுலோகம் 13: லக்னத்திற்கு 6, 7, 8 ஆகிய இடங்களில் இயற்கை சுபர்கள் அமர்வது லக்னாதி யோகம்; அறிவார்ந்த தலைமை, நற்பண்புகள், உயர் பதவி மற்றும் செல்வம் அருளும்.",
         "Lagna Flanking Benefic Principle.",
         "லக்னாதி யோக சுப ஆளுமை விதி.",
         "Saravali, Ch. 34, Sloka 13", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-DHARMA-KARMA",
         "Dharma-Karmadhipati Yoga (Saravali Ch. 35, v. 14)", "தர்ம-கர்மாதிபதி யோகம் (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 9, "placed_in_house": 10, "chart": "d1"},
             {"condition_type": "house_lord_placement", "house": 10, "placed_in_house": 9, "chart": "d1"}
         ]},
         "Saravali Ch. 35, v. 14: Mutual reception or conjunction of 9th and 10th lords in auspicious houses forms the paramount Dharma-Karmadhipati Raja Yoga, conferring emperor-like status, righteous rule, and enduring prosperity.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 14: 9 மற்றும் 10-ஆம் அதிபதிகள் பரிவர்த்தனை பெற்றாலோ அல்லது இணைந்தாலோ தர்ம-கர்மாதிபதி ராஜயோகம் உண்டாகும்; மாபெரும் சக்கரவர்த்தி யோகம், தர்ம ஆட்சி மற்றும் அழியாத செல்வம் கிட்டும்.",
         "Highest Raja Yoga of Kendra and Kona union.",
         "கேந்திர-திரிகோண அதிபதிகளின் உன்னத ராஜயோக விதி.",
         "Saravali, Ch. 35, Sloka 14", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-EXALTED-3PLANETS",
         "Three Planets Exalted Royal Status (Saravali Ch. 35, v. 30)", "மூன்று கிரகங்கள் உச்சம் பெறும் ராஜயோகம் (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "multi_planet_dignity", "dignity": "exalted", "min_count": 3, "chart": "d1"},
         "Saravali Ch. 35, v. 30: When three planets are in their exaltation signs, even a person born in a humble family becomes a ruler or commands equal royal authority.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 30: ஜாதகத்தில் மூன்று கிரகங்கள் உச்சம் பெற்று நின்றால், எளிய குடும்பத்தில் பிறந்தவராயினும் அரசனாகவோ அல்லது அரசனுக்கு நிகரான அதிகாரியாவோ உயர்வார்.",
         "Multi-Planet Exaltation Sovereign Elevation Principle.",
         "மும்மூர்த்தி உச்ச ராஜயோக விதி: மூன்று கிரகங்கள் உச்சம் பெறுவது மாபெரும் அரச யோகத்தை உருவாக்கும்.",
         "Saravali, Ch. 35, Sloka 30", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-EXALTED-MOON-JUPITER",
         "Exalted Moon in Taurus Aspected by Jupiter (Saravali Ch. 35, v. 40)", "ரிஷபத்தில் உச்ச சந்திரன் - குரு பார்வை (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_sign", "planet": "Moon", "sign": 2, "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Jupiter", "target_type": "planet", "target_value": "Moon", "chart": "d1"}
         ]},
         "Saravali Ch. 35, v. 40: If the Moon is exalted in Taurus and aspected fully by Jupiter, the native becomes an emperor whose command is obeyed by all neighboring lands.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 40: சந்திரன் ரிஷப ராசியில் உச்சம் பெற்று தேவகுருவான குருவின் முழு பார்வையைப் பெற்றால் ஜாதகர் திசையெட்டும் ஆளும் சக்கரவர்த்தி யோகத்தைப் பெறுவார்.",
         "Highest Lunar Dignity and Divine Grace Synthesis.",
         "உச்ச சந்திரனும் குரு பார்வையும் தரும் இணையற்ற ராஜயோகம்.",
         "Saravali, Ch. 35, Sloka 40", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-RAJA-KENDRA-BENEFICS",
         "All Benefics in Kendras Free from Malefics (Saravali Ch. 35, v. 1-5)", "சுபர்கள் அனைவரும் கேந்திரத்தில் அமைந்த ராஜயோகம் (சாராவளி அத்தியாயம் 35)",
         "saravali_raja_yogas",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [1, 4, 7, 10], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "houses": [1, 4, 7, 10], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "houses": [1, 4, 7, 10], "chart": "d1"}
         ]},
         "Saravali Ch. 35, v. 1-5: If all natural benefics (Jupiter, Venus, Mercury) occupy angular houses without malefic affliction, the native attains supreme sovereignty, vast riches, and immaculate character.",
         "சாராவளி அத்தியாயம் 35, சுலோகம் 1-5: குரு, சுக்கிரன், புதன் ஆகிய மூன்று சுபர்களும் கேந்திர வீடுகளில் அமர்ந்து பாபத் தொடர்பின்றி இருந்தால், ஜாதகர் மாபெரும் அரசயோகத்தையும் நற்புகழையும் அடைவார்.",
         "Quad-Angular Benefic Dominance Principle.",
         "முழு சுப கேந்திர யோக விதி.",
         "Saravali, Ch. 35, Sloka 1-5", "SeverityLevel.FAVORABLE")
    ]

    for r_id, name_en, name_ta, subcat, c_tree, desc_en, desc_ta, princ_en, princ_ta, sloka, sev in raja_data:
        rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{r_id}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="saravali_classics",
        subcategory="{subcat}",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={c_tree},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="{princ_en}",
        astrological_principle_ta="{princ_ta}",
        source_reference="{sloka}",
        limitations_en="Obstructions to Raja Yogas (Raja Yoga Bhanga) must be checked concurrently.",
        limitations_ta="சாராவளி அத்தியாயம் 39-ல் கூறப்பட்டுள்ள ராஜயோக பங்க அமைப்புகளையும் கவனிக்க வேண்டும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    # 2. Raja Yoga Bhanga / Obstructions (Chapter 39)
    bhanga_data = [
        ("RULE-SARAVALI-BHANGA-SUN-FALL",
         "Sun in Fall (Libra 10°) Annihilating Raja Yogas (Saravali Ch. 39, v. 1)", "துலாம் 10°-ல் நீச சூரியன்: ராஜயோக பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "planet_sign", "planet": "Sun", "sign": 7, "chart": "d1"},
         "Saravali Ch. 39, v. 1: If the Sun is at deep fall in Libra (Param Neecha around 10°), it destroys hundreds of potential Raja Yogas in the nativity, rendering royal status ineffective.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 1: சூரிய பகவான் துலாம் ராசியில் பரம நீசம் பெற்றால், ஜாதகத்தில் உள்ள நூற்றுக்கணக்கான ராஜயோகங்களையும் அது அழித்துவிடும் என்று சாராவளி எச்சரிக்கிறது.",
         "Solar Debility Sovereign Nullification Principle.",
         "சூரிய நீச பங்க விதி: ஆத்மகாரகன் மற்றும் அரசாங்க காரகன் நீசமடைவது அரச யோகங்களைத் தடுக்கும்.",
         "Saravali, Ch. 39, Sloka 1", "SeverityLevel.UNFAVORABLE"),

        ("RULE-SARAVALI-BHANGA-MOON-FALL",
         "Debilitated Moon Afflicted by Malefics (Saravali Ch. 39, v. 2)", "பாபிகளால் பார்க்கப்படும் நீச சந்திரன்: ராஜயோக பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_sign", "planet": "Moon", "sign": 8, "chart": "d1"},
             {"condition_type": "compound", "operator": "OR", "conditions": [
                 {"condition_type": "planet_aspect", "aspecting_planet": "Saturn", "target_type": "planet", "target_value": "Moon", "chart": "d1"},
                 {"condition_type": "planet_aspect", "aspecting_planet": "Mars", "target_type": "planet", "target_value": "Moon", "chart": "d1"}
             ]}
         ]},
         "Saravali Ch. 39, v. 2: If the Moon is in debilitation in Scorpio and aspected by malefics without benefic relief, other royal yogas become barren and fruitless.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 2: சந்திரன் விருச்சிகத்தில் நீசமடைந்து சனி அல்லது செவ்வாயின் பார்வையைப் பெற்றால், பிற ராஜயோகங்கள் யாவும் பயனற்றுப் போகும்.",
         "Lunar Distress Yoga Collapse Principle.",
         "சந்திர நீச பீடை விதி: மனோகாரகன் பலமிழந்து பாபப் பார்வை பெறுவது உயர்நிலையைத் தடுக்கும்.",
         "Saravali, Ch. 39, Sloka 2", "SeverityLevel.UNFAVORABLE"),

        ("RULE-SARAVALI-BHANGA-THREE-FALLEN",
         "Three or More Planets in Debilitation (Saravali Ch. 39, v. 5)", "மூன்று கிரகங்கள் நீசம் பெறுதல்: ராஜயோக பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "multi_planet_dignity", "dignity": "debilitated", "min_count": 3, "chart": "d1"},
         "Saravali Ch. 39, v. 5: If three or more planets occupy debilitation signs, the native faces poverty, continuous obstacles, and loss of ancestral prestige regardless of other yogas.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 5: மூன்று அல்லது அதற்கு மேற்பட்ட கிரகங்கள் நீசமடைந்து நின்றால், பிற யோகங்கள் இருப்பினும் வறுமை, தடைகள் மற்றும் கௌரவக் குறைவு ஏற்படும்.",
         "Multi-Planet Debility Gravitational Drain Principle.",
         "மும்மூர்த்தி நீச தோஷ விதி: பல கிரகங்கள் நீசமடைவது ஜாதக பலத்தை முழுமையாகக் குறைக்கும்.",
         "Saravali, Ch. 39, Sloka 5", "SeverityLevel.UNFAVORABLE"),

        ("RULE-SARAVALI-BHANGA-BENEFICS-DUSTHANA",
         "All Benefics Relegated to Dusthanas 6, 8, 12 (Saravali Ch. 39, v. 8)", "அனைத்து சுபர்களும் 6, 8, 12-ல் மறைதல்: யோக பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [6, 8, 12], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "houses": [6, 8, 12], "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "houses": [6, 8, 12], "chart": "d1"}
         ]},
         "Saravali Ch. 39, v. 8: When all natural benefics are tucked away into Dusthana houses (6th, 8th, 12th) while malefics dominate Kendras, Raja Yogas fail to materialize.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 8: இயற்கை சுபர்களான குரு, சுக்கிரன், புதன் ஆகிய மூவரும் 6, 8, 12 ஆகிய மறைவு ஸ்தானங்களில் முடங்கிவிட்டால் ராஜயோகங்கள் செயல்படாது.",
         "Benefic Sequestration Deficit Principle.",
         "சுப கிரக மறைவு பலாபலன் இழப்பு விதி.",
         "Saravali, Ch. 39, Sloka 8", "SeverityLevel.UNFAVORABLE"),

        ("RULE-SARAVALI-BHANGA-MAL-10TH-UNASPECTED",
         "Malefics in 10th Unaspected by Benefics (Saravali Ch. 39, v. 11)", "10-ல் சுபப் பார்வையற்ற பாப கிரகங்கள்: கர்ம பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 10, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mars", "house": 10, "chart": "d1"}
         ]},
         "Saravali Ch. 39, v. 11: If solitary cruel malefics occupy the 10th house without benefic association or aspect, the native commits degraded deeds and suffers sudden downfall.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 11: சுபர்களின் தொடர்பின்றி சனி அல்லது செவ்வாய் தனியாக 10-ல் அமர்வது திடீர் சறுக்கல்களையும் கர்ம பங்கத்தையும் உண்டாக்கும்.",
         "Unmoderated Malefic Angular Occupation Principle.",
         "10-ஆம் பாவக அசுப ஆக்கிரமிப்பு விதி.",
         "Saravali, Ch. 39, Sloka 11", "SeverityLevel.MIXED"),

        ("RULE-SARAVALI-BHANGA-RAHU-LAGNA-MOON-FALL",
         "Rahu in Lagna with Moon Debilitated (Saravali Ch. 39, v. 15)", "லக்னத்தில் ராகு மற்றும் நீச சந்திரன்: யோக பங்கம் (சாராவளி அத்தியாயம் 39)",
         "saravali_raja_yoga_bhanga",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Rahu", "house": 1, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Moon", "sign": 8, "chart": "d1"}
         ]},
         "Saravali Ch. 39, v. 15: If Rahu is in Lagna while the Moon is debilitated in Scorpio, the native experiences extreme anxieties, false illusions, and nullification of auspicious yogas.",
         "சாராவளி அத்தியாயம் 39, சுலோகம் 15: லக்னத்தில் ராகு நின்று சந்திரன் விருச்சிகத்தில் நீசமடைந்தால் மன சஞ்சலங்கள் மற்றும் யோகங்களின் செயல்திறன் முடங்கும்.",
         "Lunar Eclipse Axis Lagna Disruption Principle.",
         "சர்ப்ப தோஷ சந்திர நீச பங்க விதி.",
         "Saravali, Ch. 39, Sloka 15", "SeverityLevel.UNFAVORABLE")
    ]

    for r_id, name_en, name_ta, subcat, c_tree, desc_en, desc_ta, princ_en, princ_ta, sloka, sev in bhanga_data:
        rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{r_id}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="saravali_classics",
        subcategory="{subcat}",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={c_tree},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="{princ_en}",
        astrological_principle_ta="{princ_ta}",
        source_reference="{sloka}",
        limitations_en="Neecha Bhanga Raja Yoga (cancellation of debility) can restore status.",
        limitations_ta="நீச பங்க ராஜயோகம் உண்டானால் இப்பங்கங்கள் நீங்கி சுப பலன்கள் கிடைக்கும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    return rules
