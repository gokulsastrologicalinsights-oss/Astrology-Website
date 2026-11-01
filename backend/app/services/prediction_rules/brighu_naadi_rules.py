"""Brighu Naadi Sangraha Classical Rules Registry.

Formulated from the classical treatise 'Brighu Naadi Sangraha: (Pearls of Brighu Naadi)'
by Dr. N. Srinivasan Shastry (Sagar Publications).

Core Principles:
1. Jeeva Karaka: Jupiter represents the native's life force, vitality, and conscious destiny.
   All 12 Bhavas are analyzed from Jupiter's natal sign position.
2. Karma Karaka: Saturn represents the native's occupation, livelihood, and worldly duty.
   All career combinations are deciphered from Saturn's planetary associations.
3. Planetary Yogas & Mutual Combinations: Sign conjunctions and trinal/quadrant
   relationships between Karaka planets trigger distinct life patterns, wealth,
   properties, education, health, and partnerships.
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

BRIGHU_NAADI_DISCLAIMER_EN = (
    "Classical Brighu Naadi interpretation according to Dr. N. Srinivasan Shastry's "
    "'Brighu Naadi Sangraha'. In Naadi principles, planetary conjunctions and karakatwas "
    "govern fate independently of conventional house cusps."
)
BRIGHU_NAADI_DISCLAIMER_TA = (
    "டாக்டர் என். சீனிவாசன் சாஸ்திரியின் 'பிருகு நாடி சங்கிரகம்' நூலின் அடிப்படையிலான பலன். "
    "நாடி ஜோதிட முறையில் லக்னத்தை விட காரக கிரகங்களின் சேர்க்கையே மனித வாழ்வின் கர்ம பலன்களை நிர்ணயிக்கிறது."
)

BRIGHU_NAADI_PREDICTION_RULES: List[AstrologicalRuleDefinition] = [
    # =======================================================================
    # 1. KARMA KARAKA (SATURN) & CAREER COMBINATIONS
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-01",
        version=1,
        name_en="Saturn-Jupiter Conjunction: Dharmakarmadhipati Yoga in Livelihood",
        name_ta="சனி - குரு சேர்க்கை: கர்மத்தில் தர்ம கர்மாதிபதி யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Jupiter"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "When Karma Karaka (Saturn) is conjoined with Jeeva Karaka (Jupiter), Brighu Naadi "
            "proclaims a noble, honorable vocation. The native engages in teaching, advisory roles, "
            "justice, consulting, management, or administrative responsibility. The career is guided "
            "by strong ethical foundations, earning wide community respect and professional stability."
        ),
        interpretation_ta=(
            "கர்ம காரகரான சனியும் ஜீவ காரகரான குருவும் ஒரே ராசியில் இணைந்திருப்பது உன்னதமான தர்ம கர்மாதிபதி யோகமாகும். "
            "ஜாதகர் ஆசிரியர் பணி, நீதித்துறை, ஆலோசனை, நிர்வாகம் அல்லது அறப்பணிகளில் ஈடுபட்டு சமுதாயத்தில் உயரிய நற்புகழையும் "
            "தொழில் ஸ்திரத்தன்மையையும் பெறுவார்."
        ),
        astrological_principle_en="Saturn (Karma) united with Jupiter (Dharma/Jeeva) transforms raw labor into righteous, respected societal duty.",
        astrological_principle_ta="சனி (கர்மம்) மற்றும் குரு (தர்மம்/ஜீவன்) சேர்க்கை உழைப்பை தர்ம நெறி கொண்ட கௌரவப் பணியாக மாற்றுகிறது.",
        source_reference="Brighu Naadi Sangraha, Ch. 'Saturn in Combination with Planets', pp. 45-48",
        limitations_en="If combust or aspected by Rahu, periods of professional dilemma may precede establishment.",
        limitations_ta="ராகுவின் சேர்க்கை அல்லது அஸ்தமனம் இருப்பின் ஆரம்ப காலங்களில் தொழிலில் குழப்பம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-02",
        version=1,
        name_en="Saturn-Sun Conjunction: Government Liaison, Paternal Friction & Delayed Authority",
        name_ta="சனி - சூரியன் சேர்க்கை: அரசுத் தொடர்பு, தந்தை வழி கருத்துவேறுபாடு மற்றும் தாமத அதிகாரம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Sun"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn conjunct Sun unites the planet of labor with the royal planet of sovereign power. "
            "The native often secures employment connected to government departments, public sectors, "
            "or political administrations. However, classical Brighu Naadi notes sharp differences "
            "with father or state superiors, and professional promotions arrive only after persistent struggle."
        ),
        interpretation_ta=(
            "சனியும் சூரியனும் சேரும்போது அரசு, பொதுத்துறை அல்லது அரசியல் தொடர்புகளுடன் கூடிய தொழில் வாய்ப்புகள் உண்டாகும். "
            "இருப்பினும் தந்தையுடனோ அல்லது உயர் அதிகாரிகளுடனோ கருத்து வேறுபாடுகள் ஏற்படும்; கடின உழைப்பிற்கு பிறகே அதிகாரப் பதவிகள் கிட்டும்."
        ),
        astrological_principle_en="Sun (Pitri/Sovereignty) conjoined with natural enemy Saturn (Karma/Labor) produces friction with authority before elevated station.",
        astrological_principle_ta="சூரியன் (அரசு/பித்ரு) மற்றும் சனி (கர்மம்) எதிரெதிர் குணங்களால் அதிகாரப் போராட்டம் மற்றும் தாமத வெற்றியைத் தரும்.",
        source_reference="Brighu Naadi Sangraha, pp. 48-50",
        limitations_en="Benefic aspects from Jupiter mitigate authority tensions.",
        limitations_ta="குருவின் சுபப் பார்வை இருப்பின் அதிகாரிகளுடனான பகை தணியும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-03",
        version=1,
        name_en="Saturn-Moon Conjunction: Wandering Livelihood, Travel, Fluctuations & Mental Restlessness",
        name_ta="சனி - சந்திரன் சேர்க்கை: அலைச்சல் மிகுந்த தொழில், இடமாற்றங்கள் மற்றும் மன உளைச்சல்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Moon"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Brighu Naadi identifies Saturn conjunct Moon as the yoga of mobile or fluctuating enterprise. "
            "The native frequently changes job locations, travels for work, or engages in liquid commerce, "
            "catering, hospitality, naval transport, or healthcare nursing. Periods of vocational anxiety "
            "and mental restlessness accompany career shifts."
        ),
        interpretation_ta=(
            "சனியும் சந்திரனும் இணைவது தொழில் ரீதியான தொடர் இடமாற்றங்கள், பிரயாணங்கள் அல்லது திரவப் பொருட்கள், "
            "உணவகம், ஏற்றுமதி மற்றும் மருத்துவ நர்சிங் துறை வாய்ப்புகளைக் குறிக்கும். மனதில் அடிக்கடி தொழிலில் சலிப்பும் அலைச்சலும் ஏற்படும்."
        ),
        astrological_principle_en="Moon represents movement, fluids, and fluctuating emotions; union with Saturn creates periodic vocational relocations.",
        astrological_principle_ta="சந்திரன் (சலனம்/மனம்) சனியுடன் சேர்வதால் பணியில் அடிக்கடி மாற்றங்களும் அலைச்சல்களும் நிகழ்கின்றன.",
        source_reference="Brighu Naadi Sangraha, pp. 51-53",
        limitations_en="Strong Jupiter aspect provides stability and transforms travel into lucrative commerce.",
        limitations_ta="குரு பார்வை பெற்றால் அலைச்சல் பிரயாணங்கள் நல்ல தன லாபமாக மாறும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-04",
        version=1,
        name_en="Saturn-Mars Conjunction: Mechanical, Technical, Engineering, Machinery & Hazard Vigilance",
        name_ta="சனி - செவ்வாய் சேர்க்கை: எந்திரவியல், பொறியியல், ஆயுதப் பணி மற்றும் காய எச்சரிக்கை",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Mars"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn (Karma) with Mars (Bhumi/Shastra/Agni) creates the quintessential technical and mechanical yoga. "
            "The native thrives in engineering, construction, electrical or mechanical machinery, metallurgy, "
            "police, military, or surgical operations. Precaution is advised regarding bodily cuts, burns, or physical injuries at work."
        ),
        interpretation_ta=(
            "சனி மற்றும் செவ்வாய் சேர்க்கை பொறியியல், கட்டுமானம், எந்திரவியல், மின்சாரம், இரும்பு-உலோக தொழில், "
            "காவல்துறை அல்லது அறுவை சிகிச்சை துறைகளில் வெற்றியைத் தரும். தொழில் செய்யும் இடங்களில் காயங்கள் மற்றும் தீக்காயங்கள் ஏற்படாமல் கவனமாக இருக்க வேண்டும்."
        ),
        astrological_principle_en="Mars represents energy, heat, and tools; coupled with Saturn, it channels labor into heavy machinery and technical trades.",
        astrological_principle_ta="செவ்வாய் (ஆயுதம்/எந்திரம்) சனியுடன் இணைவது தொழினுட்ப உழைப்பையும் உடல் காய சாத்தியங்களையும் குறிக்கும்.",
        source_reference="Brighu Naadi Sangraha, pp. 53-56",
        limitations_en="Mars exalted in Capricorn or in own sign Aries/Scorpio reduces accident risk and elevates executive command.",
        limitations_ta="செவ்வாய் ஆட்சி உச்சம் பெற்றிருப்பின் காயங்கள் இன்றி உயர் பொறியியல் மேலாண்மை கிட்டும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-05",
        version=1,
        name_en="Saturn-Mercury Conjunction: Commercial Acumen, Accounting, Trade & Agency Enterprises",
        name_ta="சனி - புதன் சேர்க்கை: வர்த்தக சாமர்த்தியம், கணக்கியல், வியாபாரம் மற்றும் ஏஜென்சி தொழில்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Mercury"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "When Saturn is conjunct Mercury (Buddhi Karaka), the native possesses sharp practical intelligence. "
            "Brighu Naadi assigns this combination to commercial business, brokerage, auditing, accountancy, "
            "publishing, journalism, and commission agencies. The native often manages two concurrent streams of income."
        ),
        interpretation_ta=(
            "சனியும் புதனும் ஒரே ராசியில் இணைந்தால் புத்திக்கூர்மையும் வர்த்தக திறமையும் உண்டாகும். "
            "கணக்குத் துறை, தணிக்கை, ஏஜென்சி, எழுத்து-பதிப்பகம், பத்திரிகை அல்லது வர்த்தக நிறுவனங்களில் சிறந்து விளங்குவர்; இரட்டைத் தொழில் வாய்ப்பும் உண்டு."
        ),
        astrological_principle_en="Mercury is the natural friend of Saturn; intellectual dexterity merges with diligent execution to foster successful enterprise.",
        astrological_principle_ta="புதன் சனியின் உற்ற நண்பன்; அறிவுத்திறனும் உழைப்பும் ஒன்றிணைந்து வெற்றிகரமான வணிகத்தை உருவாக்குகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 56-59",
        limitations_en="Affliction by Rahu can induce contractual disputes or tax audit scrutiny.",
        limitations_ta="ராகுவின் சேர்க்கை இருப்பின் ஒப்பந்தங்களில் வழக்குகளும் கணக்கு வழக்குகளில் சோதனைகளும் வரலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-06",
        version=1,
        name_en="Saturn-Venus Conjunction: Luxury Enterprises, Artistic Vocation & Wealth via Spouse",
        name_ta="சனி - சுக்கிரன் சேர்க்கை: ஆடம்பரப் பொருட்கள், கலைத்துறை மற்றும் துணை வழி தன யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Venus"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn conjoined with Venus produces a highly lucrative material yoga in Brighu Naadi. "
            "The native succeeds in financial industries, luxury commodities, vehicles, cosmetics, "
            "interior decor, entertainment, or textile enterprises. Furthermore, significant wealth and "
            "fortune typically manifest after marriage through the spouse's auspicious presence."
        ),
        interpretation_ta=(
            "சனியும் சுக்கிரனும் சேரும்போது சிறந்த தன யோகம் உருவாகிறது. அழகு சாதனங்கள், ஆடம்பர வாகனங்கள், "
            "வங்கி நிதித்துறை, ஆடை அலங்காரம் அல்லது கலை சார்ந்த தொழில்களில் பெரும் வருவாய் ஈட்டுவர்; திருமணத்திற்குப் பின் துணைவியார் மூலம் பெருஞ்செல்வம் பெருகும்."
        ),
        astrological_principle_en="Venus as Dhanakaraka and Kalatrakaraka harmonizes with friend Saturn to channel professional effort into luxury, ease, and financial security.",
        astrological_principle_ta="சுக்கிரன் (தன/களத்திர காரகன்) சனியுடன் இணையும் போது உழைப்பு பெரும் செல்வமாகவும் வாகன வசதிகளாகவும் மாறுகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 59-62",
        limitations_en="Combustion by Sun reduces the durability of marital luxury.",
        limitations_ta="சூரியனால் அஸ்தமனம் பெற்றால் இல்லற போகங்கள் தற்காலிகமாக குறையலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-07",
        version=1,
        name_en="Saturn-Rahu Conjunction: Foreign Engagements, High Technology, Chemicals & Sudden Reversals",
        name_ta="சனி - ராகு சேர்க்கை: வெளிநாட்டு பணி, உயர் தொழினுட்பம், ரசாயனம் மற்றும் எதிர்பாராத திருப்பங்கள்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Rahu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn with Rahu unites Karma with the shadowy illusionary node. Brighu Naadi associates this "
            "with non-traditional professions: computer science, software, artificial intelligence, aviation, "
            "foreign multinational corporations, photography, pharmaceuticals, and synthetic chemicals. "
            "Sudden rises are followed by unpredicted career pivots or workplace intrigue."
        ),
        interpretation_ta=(
            "சனியும் ராகுவும் இணையும் போது நவீன கணிப்பொறி தொழினுட்பம், செயற்கை நுண்ணறிவு, விமானத்துறை, "
            "மருந்து தயாரிப்பு, ரசாயனத் துறை அல்லது வெளிநாட்டு நிறுவனங்களில் உயரிய யோகம் கிட்டும். எனினும் தொழிலில் திடீர் மாற்றங்களும் மறைமுக எதிர்ப்புகளும் ஏற்படும்."
        ),
        astrological_principle_en="Rahu amplifies Saturn's scope beyond traditional boundaries, introducing unconventional, synthetic, and foreign career spheres.",
        astrological_principle_ta="ராகு சனியின் எல்லைகளை விரிவுபடுத்தி பாரம்பரியமற்ற நவீன மற்றும் அந்நிய தேசத் தொழில்களை வழங்குகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 62-65",
        limitations_en="Benefic aspect from Jupiter prevents deceptive traps and secures long-term foreign residency.",
        limitations_ta="குருவின் சுபப்பார்வை அமைந்தால் வெளிநாட்டு வேலை நிரந்தரமாகும்; ஏமாற்றங்கள் தவிர்க்கப்படும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-KARMA-08",
        version=1,
        name_en="Saturn-Ketu Conjunction: Mukti Yoga in Profession, Law, Occult, Textiles & Detachment",
        name_ta="சனி - கேது சேர்க்கை: தொழிலில் முக்தி யோகம், சட்டம், ஆன்மீகம், நெசவு மற்றும் பற்றின்மை",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Saturn", "Ketu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn conjunct Ketu is the classic 'Mukti/Renunciation' yoga in profession. The native excels in "
            "jurisprudence, legal counseling, auditing, religious trust administration, astrology, medicine, "
            "or spinning/weaving textiles. The native inwardly feels indifferent to worldly acclaim and frequently "
            "seeks quiet retreat or philanthropic service."
        ),
        interpretation_ta=(
            "சனியும் கேதுவும் சேர்வது 'தொழிலில் முக்தி யோகம்' எனப்படுகிறது. சட்டத்துறை, நீதித்துறை, ஆன்மீக அறக்கட்டளைகள், "
            "ஜோதிடம், நெசவுத் தொழில் அல்லது மருத்துவம் ஆகியவற்றில் பிரகாசிப்பர். பொருள் ஆசைகளில் பற்றற்ற மனநிலை நிலவும்."
        ),
        astrological_principle_en="Ketu cuts attachment to the material fruits of Saturn's labor, directing efforts toward truth, spiritual service, and righteous law.",
        astrological_principle_ta="கேது சனியின் கர்மத்தில் உலகியல் பற்றுகளை அறுத்து ஆன்மீக மற்றும் அறப்பணிகளில் ஈடுபடுத்துகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 65-68",
        limitations_en="May produce periods of unemployment or self-imposed professional exile if not counterbalanced by Venus.",
        limitations_ta="சுக்கிரனின் தொடர்பு இல்லாவிடில் தற்காலிக வேலை இழப்பு அல்லது ஒதுங்கி வாழும் நிலை வரலாம்.",
        severity=SeverityLevel.NEUTRAL,
    ),

    # =======================================================================
    # 2. JEEVA KARAKA (JUPITER) & PERSONAL DESTINY COMBINATIONS
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-JEEVA-01",
        version=1,
        name_en="Jupiter-Venus Conjunction: Sreemantha Yoga & Marital Splendor",
        name_ta="குரு - சுக்கிரன் சேர்க்கை: ஸ்ரீமந்த யோகம் மற்றும் இல்லற மேன்மை",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Jupiter", "Venus"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Jupiter (Deva Guru / Jeeva Karaka) conjoined with Venus (Asura Guru / Kalatra & Dhanakaraka) "
            "forms the legendary Sreemantha Yoga in Brighu Naadi. The native enjoys exceptional beauty, "
            "magnificent conveyance, palatial residence, cultured spouse, and enduring financial prosperity. "
            "Both wisdom and material luxury flourish hand in hand."
        ),
        interpretation_ta=(
            "தேவகுருவும் அசுரகுருவும் ஒரே ராசியில் இணைவது இணையற்ற 'ஸ்ரீமந்த யோகமாகும்'. "
            "அழகான மற்றும் பண்பான வாழ்க்கைத் துணை, சொகுசு வாகனங்கள், அழகிய இல்லம் மற்றும் நிறைவான தன தான்ய "
            "செல்வம் ஜாதகருக்கு இயல்பாகவே கிட்டும்."
        ),
        astrological_principle_en="The two supreme natural benefics united in one sign elevate both the conscious soul (Jupiter) and sensory fortune (Venus).",
        astrological_principle_ta="சுப கிரகங்களான குருவும் சுக்கிரனும் சேர்வது ஜீவனையும் சுக போகங்களையும் ஒருங்கே உச்ச நிலைக்கு உயர்த்துகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 22-25",
        limitations_en="Can induce mild ego clashes between partners over philosophical versus sensual preferences.",
        limitations_ta="ஆன்மீக மற்றும் உலகியல் ஆசைகளுக்கிடையே துணைவருடன் சிறு கருத்து வேறுபாடுகள் வரலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-JEEVA-02",
        version=1,
        name_en="Jupiter-Sun Conjunction: Raja Yoga, Paternal Lineage Honor & Supreme Authority",
        name_ta="குரு - சூரியன் சேர்க்கை: ராஜ யோகம், பித்ரு பெருமை மற்றும் உயர் அதிகாரம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Jupiter", "Sun"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Jupiter conjunct Sun unites Jeeva Karaka with the soul and sovereign lord Sun. "
            "The native stems from an illustrious paternal family of upright character. "
            "Social prestige, government patronization, advisory authority, and commanding "
            "leadership manifest prominently between the ages of 21 and 28."
        ),
        interpretation_ta=(
            "ஜீவ காரகரான குரு ஆத்மகாரகரான சூரியனுடன் சேர்வது உயரிய ராஜயோகமாகும். "
            "பாரம்பரிய பெருமை மிக்க குடும்பத்தில் பிறந்து, அரசு கௌரவங்கள், தலைமைப் பொறுப்புகள் மற்றும் சமுதாய மதிப்பைப் பெறுவர்; 21 முதல் 28 வயதில் பிரபலம் அடைவர்."
        ),
        astrological_principle_en="Jupiter sanctifies Sun's ego, transforming ambition into benevolent leadership and widespread social reverence.",
        astrological_principle_ta="குரு சூரியனுடன் இணைவது கர்வத்தை அடக்கி தர்ம வழியிலான அரசாட்சி மற்றும் தலைமையைத் தருகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 19-22",
        limitations_en="Combustion within tight orb (under 3 degrees) can create ego friction with authoritative figures.",
        limitations_ta="3 பாகைக்குள் அஸ்தமனம் பெற்றால் தந்தையுடனோ மேலதிகாரியுடனோ அதிகார மோதல் வரலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-JEEVA-03",
        version=1,
        name_en="Jupiter-Mars Conjunction: Guru-Mangala Yoga & Extensive Property Acquisition",
        name_ta="குரு - செவ்வாய் சேர்க்கை: குரு-மங்கள யோகம் மற்றும் நிலபுலன்கள் பாக்கியம்",
        category_slug="property_vehicles",
        subcategory="property_land",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Jupiter", "Mars"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "The conjunction of Jupiter and Mars generates the celebrated Guru-Mangala Yoga. "
            "Mars as Bhumi Karaka (land significator) blessed by Jupiter guarantees acquisition of "
            "landed estates, agricultural property, independent houses, and leadership in brotherly circles. "
            "Property milestones arrive with certainty at ages 27-28 and 40."
        ),
        interpretation_ta=(
            "குருவும் செவ்வாயும் இணைவது 'குரு-மங்கள யோகமாகும்'. பூமி காரகனான செவ்வாய் குருவின் அருள் பெறுவதால் "
            "சொந்த வீடு, விவசாய நிலங்கள், மனை யோகம் மற்றும் சகோதர வழியில் மேன்மை உண்டாகும்; 27-28 மற்றும் 40 வயதில் சொத்து யோகம் கூடும்."
        ),
        astrological_principle_en="Mars provides kinetic force and real estate ownership; Jupiter ensures righteous acquisition and value appreciation.",
        astrological_principle_ta="செவ்வாய் நிலபுலன்களையும், குரு அதன் ஸ்திரமான வளர்ச்சியையும் நல்குகின்றனர்.",
        source_reference="Brighu Naadi Sangraha, pp. 25-28",
        limitations_en="Aspect from Saturn may require legal boundary verifications before construction.",
        limitations_ta="சனியின் பார்வை இருப்பின் நிலம் வாங்கும் போது பத்திரங்களை சரிபார்த்து வாங்குவது நன்று.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-JEEVA-04",
        version=1,
        name_en="Jupiter-Mercury Conjunction: Buddhi-Jeeva Yoga & Multi-Disciplinary Erudition",
        name_ta="குரு - புதன் சேர்க்கை: புத்தி-ஜீவ யோகம் மற்றும் பன்முக கல்வி ஞானம்",
        category_slug="education_intellect",
        subcategory="higher_education",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Jupiter", "Mercury"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Brighu Naadi highlights Jupiter conjunct Mercury as the pinnacle of intellectual erudition. "
            "The native masters multiple languages, literary sciences, mathematical analytics, or legal treatise. "
            "Advisory prowess makes them valued counselors, educational leaders, and astute financial strategists."
        ),
        interpretation_ta=(
            "குருவும் புதனும் இணைந்திருப்பது அறிவாற்றலின் உச்சமான புத்தி-ஜீவ யோகமாகும். "
            "பன்மொழி புலமை, கணிதம், சட்டம் அல்லது இலக்கியத்தில் மேன்மை பெற்று சிறந்த ஆலோசகராகவும் பேராசிரியராகவும் விளங்குவர்."
        ),
        astrological_principle_en="Mercury rules intellect and dialectics; Jupiter expands it into universal wisdom and moral jurisprudence.",
        astrological_principle_ta="புதனின் புத்திக் கூர்மையும் குருவின் மெய்யறிவும் இணைந்து பரந்த ஞானத்தை உருவாக்குகின்றன.",
        source_reference="Brighu Naadi Sangraha, pp. 28-31",
        limitations_en="Over-rationalizing emotional scenarios can occasionally cause indecision.",
        limitations_ta="எல்லாவற்றையும் அளவுக்கு அதிகமாக தர்க்கரீதியாக யோசிப்பது முடிவெடுப்பதில் தயக்கத்தை ஏற்படுத்தலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-JEEVA-05",
        version=1,
        name_en="Jupiter-Ketu Conjunction: Gnana Mukti Yoga & Supreme Intuitive Wisdom",
        name_ta="குரு - கேது சேர்க்கை: ஞான முக்தி யோகம் மற்றும் உள்ளுணர்வு மெய்ஞானம்",
        category_slug="education_intellect",
        subcategory="higher_education",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Jupiter", "Ketu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "The union of Jupiter (Guru) and Ketu (Moksha Karaka) forms the sacred Gnana Yoga in Brighu Naadi. "
            "The native possesses spontaneous spiritual intuition, proficiency in occult sciences, astrology, "
            "Vedas, and timeless philosophy. Material entanglements naturally dissolve in favor of inner transcendence."
        ),
        interpretation_ta=(
            "குருவும் கேதுவும் இணைந்திருப்பது உயர் ஆன்மீக ஞான முக்தி யோகமாகும். "
            "இயல்பான உள்ளுணர்வு, ஜோதிடம், வேதம், தத்துவம் மற்றும் ஆன்மீக ஆராய்ச்சிகளில் ஆழ்ந்த ஞானம் கிட்டும்; உலகியல் பற்றுகள் விடுபடும்."
        ),
        astrological_principle_en="Ketu operates as the flag of spiritual emancipation; when united with Guru, it produces enlightenment and genuine seer insights.",
        astrological_principle_ta="கேது முக்தியையும் குரு மெய்யறிவையும் குறிப்பதால் இருவரின் சேர்க்கை ஞான திருஷ்டியை அளிக்கிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 34-37",
        limitations_en="Early youth may experience periodic social detachment or indifference to conventional career milestones.",
        limitations_ta="இளமை பருவத்தில் உலகியல் வாழ்க்கையில் பற்றின்மையும் தனிமை விருப்பமும் தோன்றலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 3. MARRIAGE & PARTNERSHIP COMBINATIONS (VENUS KARAKA)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-MARR-01",
        version=1,
        name_en="Venus-Mars Conjunction: Passionate Magnetism & Marital Temperament Harmony",
        name_ta="சுக்கிரன் - செவ்வாய் சேர்க்கை: அதீத கவர்ச்சி மற்றும் தம்பதியரிடையே முன்கோப எச்சரிக்கை",
        category_slug="marriage_relationships",
        subcategory="spouse_characteristics",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Mars"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Venus (Kalatra Karaka) conjunct Mars (Kama/Energy) produces magnetic physical attraction, "
            "early romantic attachments, and spontaneous marital vows. However, Brighu Naadi warns of "
            "temperamental impatience between partners unless grounded by mutual tolerance or Jupiter's aspect."
        ),
        interpretation_ta=(
            "சுக்கிரனும் செவ்வாயும் இணைந்திருப்பது காந்த கவர்ச்சியையும் தீவிர காதல் உணர்வுகளையும் தரும். "
            "இருப்பினும் முன்கோபம், பிடிவாதம் காரணமாக தம்பதியரிடையே வாக்குவாதங்கள் ஏற்பட வாய்ப்புள்ளதால் பரஸ்பர சகிப்புத்தன்மை அவசியம்."
        ),
        astrological_principle_en="Mars provides fire while Venus fuels desire; unbridled energy demands grounding through patience and maturity.",
        astrological_principle_ta="சுக்கிரன் ஆசையையும் செவ்வாய் வேகத்தையும் குறிப்பதால் திருமண வாழ்வில் நிதானமும் விட்டுக்கொடுத்தலும் தேவைப்படுகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 78-81",
        limitations_en="Benefic aspect from Jupiter completely pacifies temperamental frictions.",
        limitations_ta="குருவின் சுபப் பார்வை கிடைத்தால் முன்கோபம் குறைந்து அன்யோன்யம் நிறையும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-MARR-02",
        version=1,
        name_en="Venus-Ketu Conjunction: Spiritual Spouse, Marriage Timing Delay & Sacred Bond",
        name_ta="சுக்கிரன் - கேது சேர்க்கை: ஆன்மீக வாழ்க்கைத் துணை, திருமண தாமதம் மற்றும் பவித்திர பந்தம்",
        category_slug="marriage_relationships",
        subcategory="marriage_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Ketu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Venus conjoined with Ketu in Brighu Naadi indicates a deeply religious, austere, or medically "
            "inclined spouse. Marriage often materializes after the age of 27-28, with minor initial "
            "impediments. The conjugal relationship transcends mere sensual pleasure into a spiritual companionship."
        ),
        interpretation_ta=(
            "சுக்கிரனுடன் கேது இணைவது ஆன்மீக பக்தி கொண்ட, மருத்துவம் அல்லது அறப்பணி சார்ந்த வாழ்க்கைத் துணையை அளிக்கும். "
            "திருமணம் 27-28 வயதிற்கு மேல் சில தடைகளுக்குப் பின் கைகூடும்; தாம்பத்தியம் வெறும் போகமாக இல்லாமல் ஆத்மார்த்த பந்தமாக அமையும்."
        ),
        astrological_principle_en="Ketu spiritualizes Venus, curtailing frivolous romantic expectations while imparting lasting karmic depth to marriage.",
        astrological_principle_ta="கேது சுக்கிரனின் உலகியல் இச்சைகளை ஆன்மீக ஆழமாக மாற்றி பவித்திரமான இல்லறத்தை உருவாக்குகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 81-84",
        limitations_en="Can manifest temporary coldness or emotional aloofness in the first year of marital life.",
        limitations_ta="திருமணமான ஆரம்ப காலங்களில் தற்காலிக மனக்கசப்புகள் அல்லது விலகல் மனப்பான்மை ஏற்படலாம்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-MARR-03",
        version=1,
        name_en="Venus-Rahu Conjunction: Unconventional Marriage, Foreign Spouse & Grand Desires",
        name_ta="சுக்கிரன் - ராகு சேர்க்கை: வழக்கத்திற்கு மாறான திருமணம், அந்நிய துணை மற்றும் ஆடம்பர மோகம்",
        category_slug="marriage_relationships",
        subcategory="marriage_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Rahu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Venus conjunct Rahu breaks orthodox bounds in matrimonial alliances. The native may marry "
            "outside traditional community boundaries, wed a foreign or distant partner, or seek grand, "
            "glamorous romantic expressions. Caution against unrealistic expectations in conjugal life is warranted."
        ),
        interpretation_ta=(
            "சுக்கிரனும் ராகுவும் இணைந்திருப்பது மரபு வழியைத் தாண்டிய காதல் திருமணம், கலப்புத் திருமணம் அல்லது அந்நிய தேசத்து "
            "வாழ்க்கைத் துணையைக் குறிக்கும். தாம்பத்தியத்தில் அதீத கற்பனைகளும் ஆடம்பர விருப்பங்களும் காணப்படும்."
        ),
        astrological_principle_en="Rahu exaggerates Venusian sensory appetite, propelling the native across social and cultural frontiers in matrimony.",
        astrological_principle_ta="ராகு சுக்கிரனின் போக ஆசைகளை எல்லையற்றதாக மாற்றி சமுதாய வரம்புகளைக் கடந்த திருமணத்தை உருவாக்குகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 84-87",
        limitations_en="Aspect of Jupiter or Saturn stabilizes marital loyalty and domestic permanence.",
        limitations_ta="குரு அல்லது சனியின் பார்வை அமைந்தால் திருமண வாழ்க்கை நிலையானதாக மாறும்.",
        severity=SeverityLevel.MIXED,
    ),

    # =======================================================================
    # 4. KNOWLEDGE & OCCULT SCIENCES
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-EDU-01",
        version=1,
        name_en="Mercury-Ketu Conjunction: Vak-Gnana Yoga, Occult Wisdom, Mathematics & Coding",
        name_ta="புதன் - கேது சேர்க்கை: வாக்கு-ஞான யோகம், மறைபொருள் ஜோதிடம், கணிதம் மற்றும் மென்பொருள்",
        category_slug="education_intellect",
        subcategory="higher_education",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Mercury", "Ketu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Mercury (intellect, logic, trade) conjoined with Ketu (occult, algorithms, moksha) gives birth "
            "to penetrating analytical insight. The native masters intricate systems: computer code, data architecture, "
            "cryptography, mathematical research, astrology, and mystical literature. Their speech carries prophetic undertones."
        ),
        interpretation_ta=(
            "புதனும் கேதுவும் சேரும் போது நுண்ணிய பகுப்பாய்வுத் திறன் கொண்ட வாக்கு-ஞான யோகம் உண்டாகிறது. "
            "கணினி மென்பொருள் நிரலாக்கம், கணிதம், ஜோதிட ரகசியங்கள், மறைமுக தத்துவங்கள் மற்றும் நுண்கலைகளில் நிகரற்ற மேதைமை தோன்றும்."
        ),
        astrological_principle_en="Ketu sharpens Mercury's linear logic into non-linear, intuitive, cryptographic breakthroughs.",
        astrological_principle_ta="கேது புதனின் தர்க்கத்தை மீறி உள்ளுணர்வு சார்ந்த நுண் கணித மற்றும் ஜோதிட ஞானத்தை வழங்குகிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 38-41",
        limitations_en="Early schooling may witness minor speech hesitations or sporadic study breaks before mastery.",
        limitations_ta="ஆரம்ப பள்ளிப் பருவத்தில் சிறு திக்குவாய் அல்லது கல்வி இடைவேளை தோன்றி பின்னர் உச்சநிலையை அடையலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 5. HEALTH & VITALITY CAUTIONS
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNS-HLTH-01",
        version=1,
        name_en="Mars-Rahu Conjunction: High-Energy Metabolism, Blood Impurities & Hazard Vigilance",
        name_ta="செவ்வாய் - ராகு சேர்க்கை: அதீத வெப்ப உடல், ரத்த அழுத்தம் மற்றும் விபத்து எச்சரிக்கை",
        category_slug="health_vitality",
        subcategory="health_vitality",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Mars", "Rahu"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "Mars (blood, marrow, muscle) combined with toxic node Rahu generates internal bile heat, "
            "tendency toward blood pressure fluctuations, allergic reactions, or surgical interventions. "
            "Brighu Naadi advises extreme care around fast vehicles, fire, and industrial machinery, especially during Rahu or Mars cycles."
        ),
        interpretation_ta=(
            "செவ்வாயும் ராகுவும் இணைவது உடலில் அதீத பித்த வெப்பம், ரத்த அழுத்தம் அல்லது ஒவ்வாமை உபாதைகளைத் தரலாம். "
            "வாகனங்கள் ஓட்டும் போதும், தீ மற்றும் எந்திரங்களைக் கையாளும் போதும் மிகுந்த எச்சரிக்கை தேவை."
        ),
        astrological_principle_en="Rahu amplifies Mars's combustible fire, increasing inflammation and impulsive hazard risks.",
        astrological_principle_ta="ராகு செவ்வாயின் தீயை பெருக்கி ரத்த கொதிப்பு மற்றும் காயங்களை உருவாக்கும் வாய்ப்பை அதிகரிக்கிறது.",
        source_reference="Brighu Naadi Sangraha, pp. 88-91",
        limitations_en="Aspect of Jupiter transforms this combination into extraordinary technical endurance and surgical mastery.",
        limitations_ta="குரு பார்வை பெற்றால் இந்த சேர்க்கை சிறந்த அறுவை சிகிச்சை மருத்துவர் யோகமாக மாறும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 6. BHRIGU NANDI NADI ACADEMIC RESEARCH EXTENSION (R. G. RAO SYSTEM)
    # A. Jagadeesan & Dr. K. Jothimani, IJCRME Vol. 7, Issue 2, pp. 23-31, 2022
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-R03-JUP-MOON-7TH",
        version=1,
        name_en="BNN Rule 3: Moon with 7th House Jupiter - Vitality to Mother & Gains via Travel",
        name_ta="BNN விதி 3: சந்திரனுக்கு 7-ல் குரு - தாய்க்கு நல்வாழ்வு மற்றும் பிரயாண தன லாபம்",
        category_slug="life_events_domain",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_aspect",
            "planet_from": "Moon",
            "planet_to": "Jupiter",
            "house_distance": 7,
            "chart": "d1",
        },
        interpretation_en=(
            "According to Bhrigu Nandi Nadi Rule 3 (R. G. Rao system), when the Moon receives the direct 7th "
            "house polar aspect of benevolent Jupiter, the native's mother is blessed with vitality, long life, and dignity. "
            "The native accomplishes lucrative foreign travels, commercial gains through movement, and emotional contentment."
        ),
        interpretation_ta=(
            "பிருகு நந்தி நாடி விதி 3-ன் படி, சந்திரனுக்கு 7-ஆம் வீட்டில் தேவகுருவான குரு அமர்ந்து பார்த்தால் "
            "தாயாருக்கு நீண்ட ஆயுளும் யோகமும் உண்டாகும்; ஜாதகர் பிரயாணங்கள், வெளியூர் தொடர்புகள் மற்றும் வர்த்தகப் பயணங்கள் "
            "வழியாக பெரும் தன லாபத்தைப் பெறுவார்."
        ),
        astrological_principle_en="Natural benefic Jupiter opposite Moon creates powerful polar resonance, purifying the mental and maternal karakatva.",
        astrological_principle_ta="சந்திரனுக்கு நேர் 7-ல் சுப கிரகமான குரு நிற்பது மனோகாரகத்தையும் மாத்ருகாரகத்தையும் உயரிய நிலைக்கு உயர்த்துகிறது.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, Rule 3, p. 24",
        limitations_en="Aspects from Rahu or Saturn can cause temporary anxiety during travel.",
        limitations_ta="ராகுவின் சேர்க்கை இருப்பின் பிரயாணங்களில் சிறு அலைச்சல்கள் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-SAT-LIBRA",
        version=1,
        name_en="BNN Saturn in Libra: Exalted Karma Karaka - Judiciary, Law & Design Luminary",
        name_ta="BNN துலாமில் சனி: உச்ச கர்ம காரகர் - நீதித்துறை, சட்டம் மற்றும் அலங்கார யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Saturn",
            "sign": "libra",
            "chart": "d1",
        },
        interpretation_en=(
            "In Bhrigu Nandi Nadi, Saturn reaches its highest exalted dignity in Libra (Venus's sign). "
            "The native attains high judicial posts, thrives as a senior legal counsel, or commands flourishing "
            "enterprises in luxury garments, interior design, architecture, engineering, and the automotive industry."
        ),
        interpretation_ta=(
            "பிருகு நந்தி நாடி முறைப்படி துலாம் ராசியில் சனி பகவான் உச்சம் பெறுகிறார். ஜாதகர் உச்ச நீதிமன்ற/உயர் நீதிமன்ற நீதிபதி, "
            "பிரபல வழக்கறிஞர் அல்லது ஆடம்பர ஆடை அணிகலன்கள், உள் அலங்காரம், பொறியியல் துறை மற்றும் வாகனத் தொழிலில் கொடிகட்டிப் பறப்பார்."
        ),
        astrological_principle_en="Exalted Saturn in Venus's air sign balances righteous justice with refined worldly commerce.",
        astrological_principle_ta="சுக்கிரனின் காற்று ராசியில் சனி உச்சமடைவது நீதியையும் நேர்த்தியான வர்த்தகப் புகழையும் ஒருங்கே தருகிறது.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, Saturn in 12 Zodiacs, pp. 30-31",
        limitations_en="Combustion by Sun reduces initial judicial speed.",
        limitations_ta="சூரியனுடன் இணைந்தால் ஆரம்ப காலங்களில் அதிகார வளர்ச்சிக்கு கூடுதல் உழைப்பு தேவைப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-SAT-SAGITTARIUS",
        version=1,
        name_en="BNN Saturn in Sagittarius: Honorable Legal, Academic & Financial Directorship",
        name_ta="BNN தனுசில் சனி: கௌரவமிக்க சட்டம், கல்வி மற்றும் நிதித்துறை தலைமை யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Saturn",
            "sign": "sagittarius",
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn occupies friendly Jupiterian territory in Sagittarius. Bhrigu Nandi Nadi assigns this "
            "placement to distinguished, honorable vocations: professors, university deans, bank managers, "
            "government treasurers, magistrates, high accountants, and religious trust administrators."
        ),
        interpretation_ta=(
            "தனுசு ராசியில் சனி நட்பு பெறுகிறார். பிருகு நந்தி நாடி முறைப்படி ஜாதகர் பேராசிரியர், கல்வித்துறை தலைவர், "
            "வங்கி மேலாளர், அரசு கருவூலப் பொறுப்பு, நீதித்துறை வழக்கறிஞர் அல்லது பொது அறக்கட்டளை நிர்வாகியாக உயர்வார்."
        ),
        astrological_principle_en="Saturn's labor harmonized with Jupiter's dharma yields prestigious, unblemished administrative duty.",
        astrological_principle_ta="சனி குருவின் தர்ம வீட்டில் அமர்வது நேர்மையான உழைப்பால் சமூக கௌரவத்தையும் உன்னத பதவியையும் தருகிறது.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, p. 31",
        limitations_en="Aspect from Rahu may trigger bureaucratic audits.",
        limitations_ta="ராகுவின் சேர்க்கை இருப்பின் நிதித் தணிக்கைகளில் கவனம் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-SAT-AQUARIUS",
        version=1,
        name_en="BNN Saturn in Aquarius: Scientific Research, Astrology, Psychology & High Technology",
        name_ta="BNN கும்பத்தில் சனி: அறிவியல் ஆராய்ச்சி, ஜோதிடம், உளவியல் மற்றும் விண்வெளி தொழினுட்பம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Saturn",
            "sign": "aquarius",
            "chart": "d1",
        },
        interpretation_en=(
            "Saturn rules its Moolatrikona sign Aquarius. In Bhrigu Nandi Nadi, this produces eminent scientific "
            "researchers, astrologers, psychologists, executive managers, aviation/aerospace engineers, and spiritual thinkers."
        ),
        interpretation_ta=(
            "கும்பத்தில் சனி ஆட்சி பெறுகிறார். பிருகு நந்தி நாடி முறைப்படி ஜோதிடம், உளவியல், அறிவியல் கண்டுபிடிப்புகள், "
            "விண்வெளி மற்றும் விமானப் பொறியியல், நிறுவன மேலாண்மை மற்றும் தத்துவ ஆராய்ச்சிகளில் மாபெரும் மேதைமை கிட்டும்."
        ),
        astrological_principle_en="Moolatrikona Saturn in air sign Aquarius drives collective innovation, occult mastery, and intellectual leadership.",
        astrological_principle_ta="கும்பத்தில் சனி தன் மூலத்திரிகோண பலத்தால் அறிவியல், மறைபொருள் ஜோதிடம் மற்றும் சமூக முன்னேற்றத்தை நல்குகிறார்.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, p. 31",
        limitations_en="Tendency toward intellectual solitude or detachment from family frivolity.",
        limitations_ta="அறிவுசார் தனிமை விருப்பமும் குடும்ப உலகியல் பேச்சுகளில் பற்றின்மையும் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-SAT-TAURUS",
        version=1,
        name_en="BNN Saturn in Taurus: Financial Treasury, Banking, Software & Automobile Industry",
        name_ta="BNN ரிஷபத்தில் சனி: நிதித்துறை, வங்கி, கணினி மென்பொருள் மற்றும் வாகன தொழில் யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Saturn",
            "sign": "taurus",
            "chart": "d1",
        },
        interpretation_en=(
            "Taurus represents the celestial treasury ruled by friendly Venus. Bhrigu Nandi Nadi indicates "
            "career fulfillment in the banking sector, moneylending, financial institutions, the automotive industry, "
            "and modern software/computer technology."
        ),
        interpretation_ta=(
            "ரிஷபம் காலபுருஷனின் தன ஸ்தானம்; இதன் அதிபதி சனியின் நண்பரான சுக்கிரன். இங்கு சனி அமர்வது வங்கித்துறை, "
            "நிதி நிறுவனங்கள், வட்டித் தொழில், வாகன உற்பத்தி மற்றும் நவீன கணினி மென்பொருள் துறைகளில் சிறப்பான தன லாபத்தைத் தரும்."
        ),
        astrological_principle_en="Saturn in an Earth sign of Venus transforms labor into material wealth, financial instruments, and digital enterprise.",
        astrological_principle_ta="சுக்கிரனின் நில ராசியில் சனி அமர்வது உழைப்பை நிலையான நிதியாகவும் சொத்துக்களாகவும் மாற்றுகிறது.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, p. 30",
        limitations_en="If combust by Sun, delays in initial banking promotions occur.",
        limitations_ta="சூரியனால் அஸ்தமனம் அடைந்தால் ஆரம்ப கால உத்தியோக உயர்வில் சிறு தாமதம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-BNN-SAT-ARIES",
        version=1,
        name_en="BNN Saturn in Aries: Mechanical Machinery, Defense, Uniformed Personnel & Engineering",
        name_ta="BNN மேஷத்தில் சனி: எந்திரவியல், ராணுவம், காவல்துறை மற்றும் பொறியியல் உழைப்பு",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Saturn",
            "sign": "aries",
            "chart": "d1",
        },
        interpretation_en=(
            "In Aries (Mars's fire sign), Karma Karaka Saturn engages with tools, machinery, and physical grit. "
            "The native works in mechanical engineering, factory operations, military defense, police, or uniformed services. "
            "Initial career struggles transform into disciplined technical command."
        ),
        interpretation_ta=(
            "மேஷத்தில் சனி பகவான் அமர்வது எந்திரவியல், மெக்கானிக்கல் பணிகள், தொழிற்சாலைகள், ராணுவம், காவல்துறை "
            "அல்லது சீருடைப் பணிகளில் முன்னேற்றத்தைத் தரும். ஆரம்ப கால போராட்டங்களுக்குப் பின் உறுதி மிக்க தொழினுட்ப தலைமை கிட்டும்."
        ),
        astrological_principle_en="Saturn in Mars's sign channels persistent endurance into metallic machinery and security duty.",
        astrological_principle_ta="செவ்வாயின் வீட்டில் சனி அமர்வது கடுமையான உழைப்பையும் ஆயுத-எந்திரக் கட்டுப்பாட்டையும் நல்குகிறது.",
        source_reference="A. Jagadeesan & Dr. K. Jothimani, IJCRME 2022, p. 30",
        limitations_en="Precaution required regarding physical injuries at workplace during early Mars cycles.",
        limitations_ta="ஆரம்ப காலங்களில் பணியிடங்களில் சிறு காயங்கள் ஏற்படாமல் கவனமாக இருத்தல் நன்று.",
        severity=SeverityLevel.MIXED,
    ),
]
