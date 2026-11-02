# scripts/saravali_builder/angles_and_worldly.py
"""Saravali Chapter 31 (Two Planets in Angles) & Chapters 32-34 (Worldly Affairs).
20 rules for Two Planets in Kendras (Ch. 31)
18 rules for 9th, 10th, 2nd, 11th houses (Ch. 32-34)
"""

def get_angles_and_worldly_rules():
    rules = []

    # 1. Chapter 31: 20 combinations of Two Planets in Angles (1, 4, 7, 10)
    angle_pairs = [
        ("Sun", "Moon", "RULE-SARAVALI-KENDRA-SUN-MOO",
         "Sun and Moon Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் சந்திரன் (சாராவளி பலன்)",
         "According to Saravali Ch. 31, v. 2, if Sun and Moon are both in Kendras (1st, 4th, 7th, or 10th), the native is courageous, skilled in royal service, renowned, but experiences domestic emotional shifts.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 2: சூரியனும் சந்திரனும் கேந்திரங்களில் (1, 4, 7, 10) அமைந்தால் வீர பராக்கிரமம், அரச பணி, புகழ் மற்றும் சமூகத்தில் உயர்ந்த அந்தஸ்து கிட்டும்.",
         "Saravali, Ch. 31, Sloka 2", "SeverityLevel.FAVORABLE"),

        ("Sun", "Mars", "RULE-SARAVALI-KENDRA-SUN-MAR",
         "Sun and Mars Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் செவ்வாய் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 3: Sun and Mars in Kendras grant supreme martial authority, fearless demeanor, success in armed forces or governance, though prone to high blood pressure or fiery disputes.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 3: கேந்திரங்களில் சூரியனும் செவ்வாயும் அமைவது ராணுவ அல்லது காவல் தலைமை, நிர்வாக அதிகாரம், அஞ்சாநெஞ்சம் மற்றும் மாபெரும் தைரியத்தை நல்கும்.",
         "Saravali, Ch. 31, Sloka 3", "SeverityLevel.FAVORABLE"),

        ("Sun", "Mercury", "RULE-SARAVALI-KENDRA-SUN-MER",
         "Sun and Mercury Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் புதன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 4: Intellectually brilliant, eloquent orator, trusted minister or scribe to authorities, endowed with conveyances, and respected in learned assemblies.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 4: கேந்திரங்களில் சூரியனும் புதனும் அமைவது சிறந்த கல்வி, நாவன்மை, அரசாங்க ஆலோசகர் பதவி, வாகன யோகம் மற்றும் அறிஞர் சபையில் கௌரவத்தை அளிக்கும்.",
         "Saravali, Ch. 31, Sloka 4", "SeverityLevel.FAVORABLE"),

        ("Sun", "Jupiter", "RULE-SARAVALI-KENDRA-SUN-JUP",
         "Sun and Jupiter Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் குரு (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 5: Eminent advisor, highly ethical, wealthy, beloved by rulers, builder of public institutions, and radiant with spiritual and material dignity.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 5: கேந்திரங்களில் சூரியனும் குருவும் அமைவது தர்மவானாகத் திகழ்தல், அரச தலைமை ஆலோசகர் அந்தஸ்து, அழியாத புகழ் மற்றும் பெரும் செல்வத்தை வழங்கும்.",
         "Saravali, Ch. 31, Sloka 5", "SeverityLevel.FAVORABLE"),

        ("Sun", "Venus", "RULE-SARAVALI-KENDRA-SUN-VEN",
         "Sun and Venus Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் சுக்கிரன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 6: Accomplished in the fine arts, wealthy, fond of perfumes and ornaments, possessing handsome vehicles, though requiring balance in relationships.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 6: கேந்திரங்களில் சூரியனும் சுக்கிரனும் அமைவது நுண்கலைகளில் தேர்ச்சி, ஆடை-ஆபரணச் சேர்க்கை, வசீகரத் தோற்றம் மற்றும் சுகபோக வாழ்வை அருளும்.",
         "Saravali, Ch. 31, Sloka 6", "SeverityLevel.FAVORABLE"),

        ("Sun", "Saturn", "RULE-SARAVALI-KENDRA-SUN-SAT",
         "Sun and Saturn Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சூரியன் மற்றும் சனி (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 7: Enduring perseverance, leader of workers or commoners, overcoming intense early struggles, victorious in long litigation.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 7: கேந்திரங்களில் சூரியனும் சனியும் அமைவது கடுமையான உழைப்பால் உயர்வு, தொழிலாளர் தலைமை, வழக்கு வெற்றி மற்றும் மன உறுதி தரும்.",
         "Saravali, Ch. 31, Sloka 7", "SeverityLevel.MIXED"),

        ("Moon", "Mars", "RULE-SARAVALI-KENDRA-MOO-MAR",
         "Moon and Mars Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சந்திரன் மற்றும் செவ்வாய் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 8: Energetic merchant, wealthy through lands and minerals, fearless, assertive, endowed with dynamic vitality and commercial triumphs.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 8: கேந்திரங்களில் சந்திரனும் செவ்வாயும் அமைவது மகா தன யோகம்; நிலம், ரியல் எஸ்டேட் வணிகத்தில் வெற்றி மற்றும் அஞ்சாநெஞ்சம் தரும்.",
         "Saravali, Ch. 31, Sloka 8", "SeverityLevel.FAVORABLE"),

        ("Moon", "Mercury", "RULE-SARAVALI-KENDRA-MOO-MER",
         "Moon and Mercury Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சந்திரன் மற்றும் புதன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 9: Sweet-spoken, poet, interpreter of sacred texts, loved by peers, endowed with artistic and mathematical acumen.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 9: கேந்திரங்களில் சந்திரனும் புதனும் அமைவது சாதுரியமான பேச்சு, கவிதை நயம், சாஸ்திர ஞானம், நற்புகழ் மற்றும் கலை வெற்றி தரும்.",
         "Saravali, Ch. 31, Sloka 9", "SeverityLevel.FAVORABLE"),

        ("Moon", "Jupiter", "RULE-SARAVALI-KENDRA-MOO-JUP",
         "Moon and Jupiter Stationed in Angles (Kendra Gaja Kesari)", "கேந்திரங்களில் சந்திரன் மற்றும் குரு (கேந்திர கஜ கேசரி)",
         "Saravali Ch. 31, v. 10: Supreme Gaja Kesari placement: Righteous sovereign, deeply affluent, respected by learned councils, blessed with noble sons and lifelong honor.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 10: கேந்திர கஜ கேசரி யோகம்; சமுதாய தலைமை, அளப்பரிய தனம், களங்கமற்ற புகழ், உன்னத புத்திர பாக்கியம் மற்றும் சகல நன்மைகளையும் நல்கும்.",
         "Saravali, Ch. 31, Sloka 10", "SeverityLevel.FAVORABLE"),

        ("Moon", "Venus", "RULE-SARAVALI-KENDRA-MOO-VEN",
         "Moon and Venus Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சந்திரன் மற்றும் சுக்கிரன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 11: Endowed with luxurious residences, jewels, conveyances, graceful manners, deep domestic contentment, and commercial success.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 11: கேந்திரங்களில் சந்திரனும் சுக்கிரனும் அமைவது மாளிகை வீடு, சொகுசு வாகனங்கள், வசீகர குணம் மற்றும் குடும்ப அமைதியை அருளும்.",
         "Saravali, Ch. 31, Sloka 11", "SeverityLevel.FAVORABLE"),

        ("Moon", "Saturn", "RULE-SARAVALI-KENDRA-MOO-SAT",
         "Moon and Saturn Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் சந்திரன் மற்றும் சனி (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 12: Serious and contemplative mind, success in construction and agrarian sectors, patient demeanor, enduring legacy through perseverance.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 12: கேந்திரங்களில் சந்திரனும் சனியும் அமைவது ஆழமான சிந்தனை, விவசாயம்-கட்டுமானத் துறையில் வெற்றி மற்றும் விடாமுயற்சி தரும்.",
         "Saravali, Ch. 31, Sloka 12", "SeverityLevel.MIXED"),

        ("Mars", "Mercury", "RULE-SARAVALI-KENDRA-MAR-MER",
         "Mars and Mercury Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் செவ்வாய் மற்றும் புதன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 13: Expert in metallurgy, surgical arts, trading, analytical engineering, energetic debater, and successful in competitive trials.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 13: கேந்திரங்களில் செவ்வாயும் புதனும் அமைவது பொறியியல், மருத்துவம், கணிதம் மற்றும் போட்டித் தேர்வுகளில் மகத்தான வெற்றி தரும்.",
         "Saravali, Ch. 31, Sloka 13", "SeverityLevel.FAVORABLE"),

        ("Mars", "Jupiter", "RULE-SARAVALI-KENDRA-MAR-JUP",
         "Mars and Jupiter Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் செவ்வாய் மற்றும் குரு (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 14: Virtuous commander, master of city or state planning, renowned for courage tempered by righteousness, vastly prosperous.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 14: கேந்திரங்களில் செவ்வாயும் குருவும் அமைவது தர்ம சிந்தனையுடன் கூடிய வீரம், உயர்மட்ட நிர்வாகப் பதவி மற்றும் பூரண செல்வத்தை வழங்கும்.",
         "Saravali, Ch. 31, Sloka 14", "SeverityLevel.FAVORABLE"),

        ("Mars", "Venus", "RULE-SARAVALI-KENDRA-MAR-VEN",
         "Mars and Venus Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் செவ்வாய் மற்றும் சுக்கிரன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 15: Passionate, charismatic, magnetic personality, talented in fine arts or athletics, affluent, commanding social admiration.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 15: கேந்திரங்களில் செவ்வாயும் சுக்கிரனும் அமைவது வசீகரமான ஆளுமை, விளையாட்டு-கலைத் தேர்ச்சி மற்றும் உலகியல் செல்வாக்கை அருளும்.",
         "Saravali, Ch. 31, Sloka 15", "SeverityLevel.FAVORABLE"),

        ("Mars", "Saturn", "RULE-SARAVALI-KENDRA-MAR-SAT",
         "Mars and Saturn Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் செவ்வாய் மற்றும் சனி (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 16: Iron constitution, master of heavy industry or defense projects, fearless in danger, unyielding in execution.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 16: கேந்திரங்களில் செவ்வாயும் சனியும் அமைவது இரும்பு போன்ற உடல் பலம், பாதுகாப்பு-தொழிற்சாலை தலைமை மற்றும் அஞ்சாநெஞ்சம் தரும்.",
         "Saravali, Ch. 31, Sloka 16", "SeverityLevel.MIXED"),

        ("Mercury", "Jupiter", "RULE-SARAVALI-KENDRA-MER-JUP",
         "Mercury and Jupiter Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் புதன் மற்றும் குரு (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 17: Supreme intellectual configuration: Renowned author, legal authority, university scholar, truthful, affluent, and universally venerated.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 17: கேந்திரங்களில் புதனும் குருவும் அமைவது பேரறிஞர் யோகம்; நீதித்துறை, பல்கலைக்கழக தலைமை, நூலாசிரியர் புகழ் மற்றும் சமுதாய மரியாதை தரும்.",
         "Saravali, Ch. 31, Sloka 17", "SeverityLevel.FAVORABLE"),

        ("Mercury", "Venus", "RULE-SARAVALI-KENDRA-MER-VEN",
         "Mercury and Venus Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் புதன் மற்றும் சுக்கிரன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 18: Refined aesthetic genius, witty conversation, melodious voice, dramatic success, prosperous lifestyle, and popular love.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 18: கேந்திரங்களில் புதனும் சுக்கிரனும் அமைவது கலை ஞானம், சாதுரியப் பேச்சு, வசீகர தோற்றம், திரைப்பட-இசைத்துறை வெற்றி மற்றும் செல்வத்தை நல்கும்.",
         "Saravali, Ch. 31, Sloka 18", "SeverityLevel.FAVORABLE"),

        ("Mercury", "Saturn", "RULE-SARAVALI-KENDRA-MER-SAT",
         "Mercury and Saturn Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் புதன் மற்றும் சனி (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 19: Expert statistician, analyst, methodical writer, disciplined student of complex codes, reliable in execution.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 19: கேந்திரங்களில் புதனும் சனியும் அமைவது கணக்கியல், புள்ளிவிவர ஆய்வு, துல்லியமான எழுத்துப்பணி மற்றும் நேர்மையான வாழ்வை அமைக்கும்.",
         "Saravali, Ch. 31, Sloka 19", "SeverityLevel.FAVORABLE"),

        ("Jupiter", "Venus", "RULE-SARAVALI-KENDRA-JUP-VEN",
         "Jupiter and Venus Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் குரு மற்றும் சுக்கிரன் (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 20: Both supreme preceptors in angles: Princely wealth, magnificent intellect, unblemished prestige, luxurious living, and philanthropic legacy.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 20: இரு பெரும் குருமார்கள் கேந்திரத்தில் அமைவது மகா பாக்கியம்; அரசனுக்கு நிகரான வாழ்வு, சகல சுகபோகம் மற்றும் தர்ம ஸ்தாபனம் செய்யும் தகுதி தரும்.",
         "Saravali, Ch. 31, Sloka 20", "SeverityLevel.FAVORABLE"),

        ("Jupiter", "Saturn", "RULE-SARAVALI-KENDRA-JUP-SAT",
         "Jupiter and Saturn Stationed in Angles (Saravali Kendra Phala)", "கேந்திரங்களில் குரு மற்றும் சனி (சாராவளி பலன்)",
         "Saravali Ch. 31, v. 21: Majestic civic leader, patron of temples and educational funds, sober wisdom, enduring financial stability, and lasting historical impact.",
         "சாராவளி அத்தியாயம் 31, சுலோகம் 21: கேந்திரங்களில் குருவும் சனியும் அமைவது சமுதாயத் தலைவராக உயர்தல், அறக்கட்டளை அமைத்தல், நிதானமான ஞானம் மற்றும் நீடித்த செல்வாக்கு தரும்.",
         "Saravali, Ch. 31, Sloka 21", "SeverityLevel.FAVORABLE")
    ]

    for p1, p2, r_id, name_en, name_ta, desc_en, desc_ta, sloka, sev in angle_pairs:
        rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{r_id}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="saravali_classics",
        subcategory="saravali_graha_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {{"condition_type": "planet_house", "planet": "{p1}", "houses": [1, 4, 7, 10], "chart": "d1"}},
                {{"condition_type": "planet_house", "planet": "{p2}", "houses": [1, 4, 7, 10], "chart": "d1"}}
            ]
        }},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="Kendra Angular Power Principle: Planets stationed in Kendras (1, 4, 7, 10) operate at maximum structural strength, directly determining worldly success per Saravali Ch. 31.",
        astrological_principle_ta="கேந்திர ஆளுமை விதி: 1, 4, 7, 10 ஆகிய கேந்திர ஸ்தானங்களில் அமரும் கிரகங்கள் முழுமையான ஆற்றலுடன் உலகியல் வெற்றிகளை உருவாக்குகின்றன.",
        source_reference="{sloka}",
        limitations_en="Check exact house occupation (1st vs 4th vs 7th vs 10th) and mutual aspects.",
        limitations_ta="நின்ற குறிப்பிட்ட கேந்திர வீடு மற்றும் பரஸ்பர பார்வைகளைக் கொண்டு தீவிரத்தை அறிய வேண்டும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    # 2. Worldly Affairs: Chapters 32, 33, 34
    worldly_rules_data = [
        ("RULE-SARAVALI-BHAGYA-OWN-LAND",
         "9th House Fortune in Native Country (Saravali Ch. 32)", "சொந்த நாட்டில் பாக்ய யோகம் (சாராவளி அத்தியாயம் 32)",
         "saravali_worldly_affairs",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 9, "placed_in_house": 9, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [1, 4, 7, 9, 10], "chart": "d1"}
         ]},
         "Saravali Ch. 32, v. 23 states that if the 9th lord is in the 9th itself and supported by Jupiter, the native achieves great fortune, ancestral wealth, and high renown in their native homeland.",
         "சாராவளி அத்தியாயம் 32, சுலோகம் 23: 9-ஆம் அதிபதி 9-லேயே ஆட்சி பெற்று குருவின் ஆதரவு பெற்றால் ஜாதகர் சொந்த நாட்டிலேயே அளப்பரிய தனம், பூர்வீக சொத்து மற்றும் அழியாத புகழைப் பெறுவார்.",
         "Swakshetra Bhagya: The fortune house energized in its own locus fosters deep rooted prosperity.",
         "சுய ஸ்தான பாக்ய யோகம்: சொந்த மண்ணிலேயே நிலைத்து நின்று பெரும் பாக்கியங்களை அடையும் அமைப்பு.",
         "Saravali, Ch. 32, Sloka 23", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-BHAGYA-FOREIGN-LAND",
         "Fortune in Distant / Foreign Lands (Saravali Ch. 32)", "வெளிநாட்டில் பாக்ய மேன்மை (சாராவளி அத்தியாயம் 32)",
         "saravali_worldly_affairs",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 9, "placed_in_house": 12, "chart": "d1"}
         ]},
         "According to Saravali Ch. 32, v. 25-26, when the 9th lord occupies the 12th house (or moveable watery sign), fortune blossoms primarily in foreign territories and across oceans.",
         "சாராவளி அத்தியாயம் 32, சுலோகம் 25-26: 9-ஆம் அதிபதி 12-ஆம் வீட்டில் அமரும்போது ஜாதகருக்கு கடல் கடந்த வெளிநாடுகளில் அளப்பரிய முன்னேற்றமும் செல்வமும் உண்டாகும்.",
         "Bhagya-Vyaya Trans-Oceanic Link: 9th lord in 12th directs luck to international horizons.",
         "பாக்ய-வியய யோகம்: வெளிநாட்டு வாழ்வின் மூலம் வாழ்க்கையின் அதிர்ஷ்டம் பிரகாசிக்கும் அமைப்பு.",
         "Saravali, Ch. 32, Sloka 25-26", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-SUN-MOON",
         "10th Livelihood Guided by Sun from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் சூரியன்: உத்தியோக மேன்மை (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Sun", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 2: When Sun occupies the 10th from the Moon, the native's livelihood arises through royal patronage, government leadership, gold, medicines, and administration.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 2: சந்திரனுக்கு 10-ஆம் இடத்தில் சூரியன் நின்றால் அரசுப் பணி, அரசியல் தலைமை, தங்கம், மருந்து மற்றும் நிர்வாகத் துறைகளில் வாழ்வாதாரம் அமையும்.",
         "Chandra-Karmadhipa Solar Vector: Profession indicated by planetary occupation relative to Moon.",
         "சந்திர லக்ன கர்ம விதி: சந்திரனுக்கு 10-ல் உள்ள கிரகத்தின் காரகத்துவம் தொழிலைத் தீர்மானிக்கும்.",
         "Saravali, Ch. 33, Sloka 2", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-MARS-MOON",
         "10th Livelihood Guided by Mars from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் செவ்வாய்: தொழில் யோகம் (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Mars", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 3: When Mars is in the 10th from the Moon, livelihood stems from defense, fire, weapons, engineering, minerals, real estate, and surgery.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 3: சந்திரனுக்கு 10-ல் செவ்வாய் அமர்ந்தால் பாதுகாப்புத் துறை, பொறியியல், ரியல் எஸ்டேட், தீ-மின்சாரம் மற்றும் அறுவை சிகிச்சைத் துறைகளில் வருமானம் வரும்.",
         "Martial Professional Catalyst from Moon.",
         "சந்திரனுக்கு 10-ல் செவ்வாய் தரும் தொழில் மேன்மை.",
         "Saravali, Ch. 33, Sloka 3", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-MERCURY-MOON",
         "10th Livelihood Guided by Mercury from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் புதன்: அறிவுசார் தொழில் (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Mercury", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 4: Mercury in the 10th from Moon grants profession through writing, accountancy, mathematics, commerce, communications, and publishing.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 4: சந்திரனுக்கு 10-ல் புதன் நின்றால் எழுத்து, கணக்கியல், கணிதம், வர்த்தகம், ஊடகம் மற்றும் வெளியீட்டுத் துறைகளில் தொழில் வெற்றி தரும்.",
         "Mercurial Intellectual Commerce from Lunar Ascendant.",
         "சந்திரனுக்கு 10-ல் புதன் தரும் அறிவுசார் வணிக யோகம்.",
         "Saravali, Ch. 33, Sloka 4", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-JUPITER-MOON",
         "10th Livelihood Guided by Jupiter from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் குரு: தர்ம உத்தியோகம் (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Jupiter", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 5: Jupiter in the 10th from Moon yields income through education, judiciary, religious guidance, treasury, counseling, and royal honors.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 5: சந்திரனுக்கு 10-ல் குரு அமைந்தால் கல்வி, நீதித்துறை, ஆன்மீகம், வங்கி-நிதித்துறை மற்றும் அரசு ஆலோசனையில் பெரும் வருமானம் ஈட்டுவார்.",
         "Jupiterian Preceptorial Livelihood from Moon.",
         "சந்திரனுக்கு 10-ல் குரு தரும் உன்னத தலைமை மற்றும் கல்விப் பணி.",
         "Saravali, Ch. 33, Sloka 5", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-VENUS-MOON",
         "10th Livelihood Guided by Venus from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் சுக்கிரன்: கலை-ஆடம்பரத் தொழில் (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Venus", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 6: Venus in the 10th from Moon confers profession in cinema, textiles, jewels, perfumes, hospitality, and luxury commodities.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 6: சந்திரனுக்கு 10-ல் சுக்கிரன் அமர்ந்தால் சினிமா, ஆடை, நவரத்தினங்கள், வாசனை திரவியங்கள் மற்றும் ஆடம்பரப் பொருட்களால் தன லாபம்.",
         "Venusian Aesthetic Commerce from Moon.",
         "சந்திரனுக்கு 10-ல் சுக்கிரன் அருளும் கலை-வணிக வெற்றி.",
         "Saravali, Ch. 33, Sloka 6", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-KARMA-SATURN-MOON",
         "10th Livelihood Guided by Saturn from Moon (Saravali Ch. 33)", "சந்திரனுக்கு 10-ல் சனி: உழைப்பால் உயர்வு (சாராவளி அத்தியாயம் 33)",
         "saravali_worldly_affairs",
         {"condition_type": "planet_relative_house", "planet": "Saturn", "from_planet": "Moon", "relative_house": 10, "chart": "d1"},
         "Saravali Ch. 33, v. 7: Saturn in the 10th from Moon brings profession through labor, agriculture, mining, heavy transport, machinery, and petroleum.",
         "சாராவளி அத்தியாயம் 33, சுலோகம் 7: சந்திரனுக்கு 10-ல் சனி அமைந்தால் விவசாயம், சுரங்கம், கனரக போக்குவரத்து, தொழிற்சாலை மற்றும் பெட்ரோலியத் துறையில் வளர்ச்சி.",
         "Saturnian Industrial Enterprise from Moon.",
         "சந்திரனுக்கு 10-ல் சனி அருளும் தொழில்துறை சாதனை.",
         "Saravali, Ch. 33, Sloka 7", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-DHANA-CONSERVATION",
         "2nd House Enduring Wealth Accumulation (Saravali Ch. 34)", "2-ஆம் பாவக நிலையான தன யோகம் (சாராவளி அத்தியாயம் 34)",
         "saravali_worldly_affairs",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 2, "placed_in_house": 2, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Jupiter", "houses": [1, 2, 4, 7, 9, 10, 11], "chart": "d1"}
         ]},
         "Saravali Ch. 34, v. 2: When the 2nd lord is in the 2nd house supported by Jupiter, the native gathers unbroken riches, inherits vast family treasures, and speaks truthfully.",
         "சாராவளி அத்தியாயம் 34, சுலோகம் 2: 2-ஆம் அதிபதி 2-ஆம் பாவத்திலேயே ஆட்சி பெற்று குருவால் பார்க்கப்பட்டால் ஜாதகர் அழியாத பெரும் செல்வத்தையும் பூர்வீகப் புதையலையும் பெறுவார்.",
         "Sustained Treasury Principle (Dhana Sthana Sthairya).",
         "தன ஸ்தான ஸ்திர விதி: 2-ல் 2-ஆம் அதிபதி குருவின் தொடர்புடன் நிற்பது நிரந்தரச் செல்வத்தை அளிக்கும்.",
         "Saravali, Ch. 34, Sloka 2", "SeverityLevel.FAVORABLE"),

        ("RULE-SARAVALI-DHANA-DESTRUCTION",
         "2nd House Dissipation of Wealth (Saravali Ch. 34)", "2-ஆம் பாவக தன விரய அமைப்பு (சாராவளி அத்தியாயம் 34)",
         "saravali_worldly_affairs",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 2, "placed_in_house": 12, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Saturn", "house": 2, "chart": "d1"}
         ]},
         "Saravali Ch. 34, v. 9: If the 2nd lord is placed in the 12th house while Saturn occupies the 2nd house without benefic aspects, ancestral wealth dissipates rapidly.",
         "சாராவளி அத்தியாயம் 34, சுலோகம் 9: 2-ஆம் அதிபதி 12-ல் மறைந்து, 2-ஆம் பாவத்தில் சனி நின்றால் பூர்வீக சொத்துகள் விரயமாகி பொருளாதார நெருக்கடி உண்டாகலாம்.",
         "Dhana Karaka and Bhava Affliction Principle.",
         "தன பாவ விரய விதி: 2-ஆம் அதிபதி 12-ல் மறைந்து சனி 2-ல் நிற்பது தன இழப்பைத் தரும்.",
         "Saravali, Ch. 34, Sloka 9", "SeverityLevel.UNFAVORABLE"),

        ("RULE-SARAVALI-LABHA-MULTIPLE-GAINS",
         "11th House Multi-Stream Wealth Flow (Saravali Ch. 34)", "11-ஆம் பாவக பலவழி தன லாபம் (சாராவளி அத்தியாயம் 34)",
         "saravali_worldly_affairs",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 11, "placed_in_house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "houses": [1, 2, 5, 9, 10, 11], "chart": "d1"}
         ]},
         "Saravali Ch. 34, v. 62: The 11th lord in the 11th supported by Mercury ensures wealth pouring in from multiple trade streams, commercial enterprises, and supportive elder brothers.",
         "சாராவளி அத்தியாயம் 34, சுலோகம் 62: 11-ஆம் அதிபதி 11-ல் ஆட்சி பெற்று புதனின் தொடர்பு பெற்றால் பல்வேறு வணிக வழிகளிலிருந்து இடைவிடாத தன லாபம் குவியும்.",
         "Labha Sthana Multiplicity Principle.",
         "லாப ஸ்தான பலவழி வருமான விதி.",
         "Saravali, Ch. 34, Sloka 62", "SeverityLevel.FAVORABLE")
    ]

    for r_id, name_en, name_ta, subcat, c_tree, desc_en, desc_ta, princ_en, princ_ta, sloka, sev in worldly_rules_data:
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
        limitations_en="Dasa timing and planetary strength modify manifestation periods.",
        limitations_ta="தசா புக்தி காலங்கள் மற்றும் கிரக பலத்தைப் பொருத்து பலன்கள் நடைபெறும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    return rules
