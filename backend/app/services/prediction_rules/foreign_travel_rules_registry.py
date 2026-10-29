"""Classical Foreign Travel and Foreign Settlement Astrological Rules Registry.

Comprehensive rules derived from classical authorities (Brihat Parashara Hora Shastra,
Jataka Parijata, Phaladeepika, Saravali) and master synthesis on Foreign Travel &
Settlement (Chara/Watery signs, Rahu Mlechha Karaka, 4th House Affliction vs 12th House
Strength, Nakshatra indicators, and purpose-based travel: Higher Education, Employment,
Marriage, and Diplomacy).
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

TRAVEL_DISCLAIMER_EN = (
    "Classical heuristic from Vedic astrology for foreign travel and settlement. "
    "Permanent foreign residence requires both a strong 12th/9th house and affliction to the 4th house (homeland), "
    "validated alongside D4 (Chaturthamsa) and operating Dasha-Antardasha periods."
)
TRAVEL_DISCLAIMER_TA = (
    "வேத ஜோதிடத்தின்படி வெளிநாட்டுப் பயணம் மற்றும் குடியேற்றத்திற்கான பாரம்பரிய விதிகள். "
    "நிரந்தர வெளிநாட்டு வாழ்க்கை அமைய 12/9-ம் வீடுகளின் வலிமையும், 4-ம் வீட்டின் (தாயகம்) பாதிப்பும் "
    "டி4 (சதுர்த்தாம்சம்) மற்றும் தசா-புக்திகளோடு ஒப்பிடப்பட்டு உறுதி செய்யப்பட வேண்டும்."
)

FOREIGN_TRAVEL_RULES_CATALOGUE: List[AstrologicalRuleDefinition] = [
    # -----------------------------------------------------------------------
    # RULE-TRV-02: 4th Lord in Dusthana (Affliction to Homeland / Foreign Settlement)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-02",
        version=1,
        name_en="4th Lord in Dusthana (Displacement from Motherland & Foreign Settlement)",
        name_ta="4-ஆம் அதிபதி மறைவு ஸ்தானத்தில் (தாயகம் விட்டு வெளிநாட்டில் குடியேறுதல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 4, "placed_in_house": 6, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 4, "placed_in_house": 8, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 4, "placed_in_house": 12, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Rahu", "house": 4, "chart": "d1"},
            ]
        },
        interpretation_en="The 4th house represents one's native homeland, ancestral home, and domestic comfort. When the 4th lord is placed in a Dusthana (6th, 8th, or 12th house) or Rahu afflicts the 4th house, the emotional and residential bond to the birthplace is severed, creating prime yogas for settling abroad.",
        interpretation_ta="4-ஆம் வீடு ஒருவரின் சொந்த நாடு, பூர்வீக இல்லம் மற்றும் மன அமைதியைக் குறிக்கிறது. 4-ஆம் அதிபதி 6, 8, அல்லது 12-ஆம் மறைவு ஸ்தானங்களில் அமையும்போதோ அல்லது ராகு 4-ல் அமையும்போதோ, பிறந்த ஊருடனான பிணைப்பு குறைந்து வெளிநாட்டில் நிரந்தரமாகக் குடியேறும் யோகம் உண்டாகிறது.",
        astrological_principle_en="Affliction or displacement of the 4th bhava/lord is the prerequisite for permanent foreign settlement, detaching the native from the soil of birth.",
        astrological_principle_ta="தாயகத்தைக் குறிக்கும் 4-ஆம் பாவகம் மற்றும் அதன் அதிபதி பலவீனமடைவதே வெளிநாட்டில் நிரந்தரமாக வாழ முதன்மையான காரணியாகும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24; Phaladeepika Ch. 16",
        limitations_en="If Jupiter aspects the 4th house, strong family obligations may retain the native in their home country.",
        limitations_ta="குருவின் சுபப்பார்வை 4-ஆம் வீட்டின் மீது இருந்தால் குடும்பப் பிணைப்பு தாயகத்திலேயே தக்கவைக்கலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-03: Rahu in 12th House (Mlechha Karaka in Foreign Lands)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-03",
        version=1,
        name_en="Rahu in 12th House (Mlechha Karaka in House of Foreign Lands)",
        name_ta="12-ஆம் வீட்டில் ராகு (அன்னிய தேச காரகன் மறைவு வீட்டில் இருத்தல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Rahu",
            "house": 12,
            "chart": "d1"
        },
        interpretation_en="Rahu is the primary Mlechha Karaka (significator of foreign lands, alien cultures, and overseas journeys). Positioned in the 12th house of foreign residence, Rahu creates immense longing, opportunities, and eventual relocation to foreign soils during its periods.",
        interpretation_ta="ராகு அன்னிய நாடு மற்றும் வேற்று கலாச்சாரங்களின் முதன்மைக் காரகன். வெளிநாட்டு ஸ்தானமான 12-ஆம் வீட்டில் ராகு அமர்வது வெளிநாட்டுப் பயணம், வேலை மற்றும் வெளிநாட்டு வாழ்க்கையை வெகுவாக ஊக்குவிக்கும் யோகமாகும்.",
        astrological_principle_en="Rahu as Mlechha Karaka residing in Vyaya Bhava (12th house) directs expenditure and residence toward offshore destinations.",
        astrological_principle_ta="அன்னிய காரகனான ராகு விரய ஸ்தானமான 12-ல் அமர்ந்து வெளிநாட்டு வாசம் மற்றும் தொடர்புகளை ஏற்படுத்துகிறார்.",
        source_reference="Saravali, Ch. 30; Jataka Parijata Ch. 8",
        limitations_en="Rahu in 12th can bring initial cultural adjustments or sleep cycle disruptions overseas.",
        limitations_ta="12-ல் ராகு ஆரம்பகால வெளிநாட்டு வாழ்க்கையில் சில மன உளைச்சல்களையும் நிம்மதியின்மையையும் தரலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-04: Rahu in Lagna or 7th House (Global Horizons & Overseas Endeavors)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-04",
        version=1,
        name_en="Rahu in Lagna or 7th House (Global Horizons & Overseas Voyages)",
        name_ta="லக்னம் அல்லது 7-ஆம் வீட்டில் ராகு (வெளிநாட்டு ஈர்ப்பு மற்றும் கடல் கடந்த பயணம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Rahu", "house": 1, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Rahu", "house": 7, "chart": "d1"},
            ]
        },
        interpretation_en="The 1st-7th axis governs self-identity and interaction with the wider world. Rahu on this axis expands the native's mindset beyond cultural borders, creating frequent opportunities for overseas journeys, multinational ventures, or international trade.",
        interpretation_ta="1 மற்றும் 7-ஆம் வீடுகள் சுய ஆளுமை மற்றும் புற உலக தொடர்பைக் குறிக்கும். இந்த அச்சில் ராகு இருப்பது உலகளாவிய சிந்தனையை அளித்து வெளிநாட்டுப் பயணங்கள் மற்றும் சர்வதேச வர்த்தக வாய்ப்புகளை உருவாக்கும்.",
        astrological_principle_en="Rahu activating the Kendras 1 or 7 propels individual ambitions towards distant lands.",
        astrological_principle_ta="கேந்திர ஸ்தானங்களான 1 அல்லது 7-ல் ராகு இருப்பது ஜாதகரின் எண்ணங்களை கடல் கடந்து பயணிக்கச் செய்கிறது.",
        source_reference="Jataka Bharanam, Rahu Phala",
        limitations_en="Affliction to 7th house requires careful partnership and relationship harmony check.",
        limitations_ta="7-ஆம் பாவகம் பாதிக்கப்படும் போது திருமண அல்லது தொழில் கூட்டாண்மைகளில் கவனம் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-05: Moon in Watery Sign or Conjunct Rahu (Crossing the Seas / Samudra Gamana)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-05",
        version=1,
        name_en="Moon in Watery Signs or Conjunct Rahu (Crossing the Seas / Samudra Gamana)",
        name_ta="ஜல ராசியில் சந்திரன் அல்லது ராகு சேர்க்கை (சமுத்திர யாத்திரை / கடல் கடத்தல் யோகம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Moon", "Rahu"], "same_sign_only": True, "chart": "d1"},
                {"condition_type": "planet_sign", "planet": "Moon", "sign": "Cancer", "chart": "d1"},
                {"condition_type": "planet_sign", "planet": "Moon", "sign": "Scorpio", "chart": "d1"},
                {"condition_type": "planet_sign", "planet": "Moon", "sign": "Pisces", "chart": "d1"},
            ]
        },
        interpretation_en="Watery signs (Cancer, Scorpio, Pisces) represent the vast oceans and oceanic navigation. The Moon as ruler of water and movement, especially when conjunct Rahu, signifies crossing the seas to alien lands (Samudra Gamana Yoga).",
        interpretation_ta="கடக, விருச்சிக, மீன ராசிகள் ஜல தத்துவ ராசிகளாகும். ஜல காரகனான சந்திரன் இந்த ராசிகளிலோ அல்லது ராகுவோடு சேர்ந்தோ இருக்கும்போது பெருங்கடல் கடந்து வெளிநாடு செல்லும் யோகத்தை நல்குகிறார்.",
        astrological_principle_en="Moon and Watery Tatwa combined with shadow planet Rahu produces trans-oceanic displacement.",
        astrological_principle_ta="சந்திரனும் ஜல தத்துவமும் ராகுவோடு இணையும் போது கடல் கடந்த வெளிநாட்டுப் பயணங்கள் எளிதாகக் கைகூடும்.",
        source_reference="Brihat Jataka, Ch. 18; Saravali Ch. 23",
        limitations_en="Moon afflicted by Rahu (Grahan yoga) needs remedies for mental tranquility during transits.",
        limitations_ta="சந்திரன் ராகுவோடு இணையும் கிரகண அமைப்பில் பயணத்தின் போது மன அமைதி காக்க பரிகாரங்கள் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-06: Moon in 12th House (Foreign Living & Overseas Residence)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-06",
        version=1,
        name_en="Moon in 12th House (Foreign Living & Overseas Residence)",
        name_ta="12-ஆம் வீட்டில் சந்திரன் (வெளிநாட்டில் வாசம் செய்தல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Moon",
            "house": 12,
            "chart": "d1"
        },
        interpretation_en="The Moon is the natural karaka of mind, mother, and domestic roots (4th lord of Kaal Purusha). Its placement in the 12th house of foreign lands shifts the native's emotional home to distant territories, favoring comfortable living overseas.",
        interpretation_ta="சந்திரன் காலபுருஷனுக்கு 4-ஆம் அதிபதியாகி தாய்நாடு மற்றும் இல்லத்தைக் குறிக்கிறார். அவர் 12-ஆம் வீடான தூர தேசத்தில் அமையும்போது வெளிநாட்டிலேயே தன் வாழ்விடத்தை அமைத்துக் கொள்ளும் எண்ணமும் சூழலும் உருவாகிறது.",
        astrological_principle_en="The 4th karaka of Kalapurusha residing in the 12th house transposes domestic life to distant shores.",
        astrological_principle_ta="காலபுருஷ தத்துவப்படி 4-ஆம் அதிபதி 12-ல் இருப்பது தாயகத்தை விட்டு அகன்று வாழ்வதைக் காட்டுகிறது.",
        source_reference="Phaladeepika, Ch. 8, Sloka 6",
        limitations_en="Native may miss motherland or family during adverse Moon transits.",
        limitations_ta="சந்திரனின் சாதகமற்ற கோச்சார காலத்தில் தாயகம் மற்றும் குடும்ப நினைவுகள் ஏங்க வைக்கலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-07: Lagna Lord in 12th House (Physical Relocation to Foreign Land)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-07",
        version=1,
        name_en="Lagna Lord in 12th House (Physical Relocation to Foreign Land)",
        name_ta="லக்னாதிபதி 12-ஆம் வீட்டில் (உடலும் உயிரும் வெளிநாட்டில் தங்குதல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 1,
            "placed_in_house": 12,
            "chart": "d1"
        },
        interpretation_en="The Ascendant represents the physical body and self. When the Lagna lord sits in the 12th house (foreign territory), the native's physical presence is placed in distant lands. In movable or watery signs, this grants long-term or permanent residence abroad.",
        interpretation_ta="லக்னம் ஒருவரின் உடலையும் இயக்கத்தையும் குறிக்கிறது. லக்னாதிபதி 12-ல் அமரும் போது ஜாதகரின் நேரடி இருப்பே வெளிநாட்டில் அமைகிறது. இது சரம் அல்லது ஜல ராசியாக இருப்பின் நிரந்தர வெளிநாட்டு வாழ்வை நல்கும்.",
        astrological_principle_en="Tanubhavam (1st lord) in Vyayabhavam (12th) establishes the life path in foreign soil.",
        astrological_principle_ta="தனு பாவாதிபதி விரய ஸ்தானமான 12-ல் அமைவது ஜாதகரின் வாழ்க்கைப் பாதையை வெளிநாட்டில் நிலைநிறுத்துகிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 12",
        limitations_en="12th lord and 1st lord strengths determine financial savings capacity abroad.",
        limitations_ta="12-ஆம் அதிபதியின் பலத்தைப் பொறுத்து வெளிநாட்டு சேமிப்புத் திறன் அமையும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-08: Sun in 5th House (Diplomatic Assignments & Overseas State Service)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-08",
        version=1,
        name_en="Sun in 5th House (Diplomatic Assignments & Overseas State Service)",
        name_ta="5-ஆம் வீட்டில் சூரியன் (அரசு தூதரக பணி மற்றும் வெளிநாட்டு உயர் பொறுப்புகள்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Sun",
            "house": 5,
            "chart": "d1"
        },
        interpretation_en="The Sun represents royalty, state authority, and governance. When placed in the 5th house of counsel and intellect, it fosters dignified diplomacy, connections with overseas dignitaries, and foreign postings in government or international agencies.",
        interpretation_ta="சூரியன் அரசு அதிகாரம், அரசு தூதரகம் மற்றும் கௌரவத்தைக் குறிக்கிறார். 5-ஆம் புத்தி ஸ்தானத்தில் சூரியன் அமர்வது வெளிநாட்டுத் தூதரகப் பணிகள், பன்னாட்டு பிரதிநிதித்துவம் மற்றும் சர்வதேச பொறுப்புகளைத் தரும்.",
        astrological_principle_en="Sun in 5th combines royal authority with strategic intelligence suitable for overseas governance.",
        astrological_principle_ta="5-ல் சூரியன் அரச கௌரவத்தையும் அறிவுக்கூர்மையையும் இணைத்து சர்வதேச தூதரகப் பணிகளுக்கு வழிவகுக்கும்.",
        source_reference="Saravali, Ch. 31; Jataka Parijata Ch. 8",
        limitations_en="Sun afflicted by Saturn or Rahu requires tactful communication with foreign authorities.",
        limitations_ta="சனி அல்லது ராகுவின் சேர்க்கை இருக்கும்போது வெளிநாட்டு மேலதிகாரிகளிடம் கவனமாகப் பழக வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-09: Mercury in 4th House (Frequent Relocations & Changes of Residence)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-09",
        version=1,
        name_en="Mercury in 4th House (Frequent Relocations & Changes of Residence)",
        name_ta="4-ஆம் வீட்டில் புதன் (அடிக்கடி வீடு மாற்றம் மற்றும் சுறுசுறுப்பான பிரயாணங்கள்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Mercury",
            "house": 4,
            "chart": "d1"
        },
        interpretation_en="Mercury is quick, adaptable, and mobile. In the 4th house of domestic residence, it creates a restless domestic environment with frequent transfers, shifting of flats or cities, and mobile living, particularly when in movable or dual signs.",
        interpretation_ta="புதன் விரைவான இயக்கம் மற்றும் மாற்றத்தைக் குறிப்பவர். 4-ஆம் வீட்டில் புதன் அமைவது ஜாதகருக்கு அடிக்கடி வாழிட மாற்றம், ஊர் மாற்றம் மற்றும் பயணங்களால் நிறைந்த சுறுசுறுப்பான சூழலை உருவாக்குகிறது.",
        astrological_principle_en="Mercury's mercurial volatility in the 4th bhava induces continuous geographical flexibility.",
        astrological_principle_ta="4-ஆம் பாவகத்தில் புதனின் இயக்கம் ஜாதகருக்கு ஒரே இடத்தில் தங்கிவிடாமல் தொடர் மாற்றங்களை ஏற்படுத்துகிறது.",
        source_reference="Phaladeepika, Ch. 8, Sloka 11",
        limitations_en="Frequent relocations may occasionally cause scattered household settling.",
        limitations_ta="அடிக்கடி வீடு மாறுவதால் இல்லற அமைப்பில் சில அலைச்சல்கள் ஏற்படலாம்.",
        severity=SeverityLevel.NEUTRAL,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-10: Moon or Rahu in Travel Nakshatras (Ashwini, Bharani, Ardra, Swati, Pushya, Hasta)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-10",
        version=1,
        name_en="Moon or Rahu in Travel Nakshatras (Ashwini, Bharani, Ardra, Swati, Pushya, Hasta)",
        name_ta="பயண நட்சத்திரங்களில் சந்திரன் அல்லது ராகு (அஸ்வினி, பரணி, திருவாதிரை, சுவாதி, பூசம், அஸ்தம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Ashwini", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Bharani", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Ardra", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Swati", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Pushya", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Hasta", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Ashwini", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Bharani", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Ardra", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Swati", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Pushya", "chart": "d1"},
                {"condition_type": "planet_nakshatra", "planet": "Rahu", "nakshatra": "Hasta", "chart": "d1"},
            ]
        },
        interpretation_en="Specific lunar asterisms possess intrinsic energy for swift transit, air travel, and overseas connections. Swati (ruled by Vayu/wind) and Ardra/Ashwini/Bharani/Pushya/Hasta stimulate rapid travel and international mobility when occupied by Moon or Rahu.",
        interpretation_ta="அஸ்வினி, பரணி, திருவாதிரை, சுவாதி, பூசம், அஸ்தம் ஆகிய நட்சத்திரங்கள் அதிவேகப் பயணங்கள் மற்றும் கடல் கடத்தலைக் குறிக்கும். இதில் சந்திரன் அல்லது ராகு அமரும்போது வெளிநாடு செல்லும் வாய்ப்பு பன்மடங்கு அதிகரிக்கிறது.",
        astrological_principle_en="Chara and Vayu-influenced Nakshatras accelerate the kinetic propulsion for international journeys.",
        astrological_principle_ta="வாயு மற்றும் வேக தத்துவ நட்சத்திரங்கள் சர்வதேச பயணங்களுக்கான உந்துதலைத் தருகின்றன.",
        source_reference="Nakshatra Samhita; Hora Ratnam",
        limitations_en="Favorable dasha operates to manifest physical ticketing and visa processing.",
        limitations_ta="தசா-புக்திகள் கைகூடும் போதே விசா மற்றும் பயண ஏற்பாடுகள் தடையின்றி நடக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-11: 5th Lord in 9th or 12th House (Foreign Travel for Higher Education)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-11",
        version=1,
        name_en="5th Lord in 9th or 12th House (Foreign Travel for Higher Education)",
        name_ta="5-ஆம் அதிபதி 9 அல்லது 12-ஆம் வீட்டில் (உயர் கல்விக்காக வெளிநாடு செல்லுதல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": 9, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": 12, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 9, "placed_in_house": 5, "chart": "d1"},
            ]
        },
        interpretation_en="The 5th house represents academic learning and intellect, while the 9th signifies higher education/long distance journeys, and the 12th signifies foreign lands. When the 5th lord is situated in the 9th or 12th house, the native goes abroad for university studies and higher degrees.",
        interpretation_ta="5-ஆம் வீடு கல்வி அறிவையும், 9-ஆம் வீடு உயர்கல்வி மற்றும் தூரப் பயணத்தையும், 12-ஆம் வீடு வெளிநாட்டையும் குறிக்கும். 5-ஆம் அதிபதி 9 அல்லது 12-ல் அமைவது வெளிநாட்டு பல்கலைக்கழகங்களில் மேற்படிப்பு படிக்கும் யோகத்தை அளிக்கிறது.",
        astrological_principle_en="Mutual connection between Trikonas (5th & 9th) and Vyaya (12th) channels intellectual development into foreign academies.",
        astrological_principle_ta="5, 9 திரிகோணங்களும் 12-ஆம் வீடும் இணைவது கல்விக்கான சர்வதேச பயணத்தை உருவாக்குகிறது.",
        source_reference="Jataka Parijata, Ch. 7; Uttara Kalamrita",
        limitations_en="Check Jupiter or Mercury affliction to prevent exam interruptions overseas.",
        limitations_ta="குரு அல்லது புதனின் பலத்தை உறுதி செய்து கல்வித் தடைகளை தவிர்க்கலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-12: 7th Lord in 9th or 12th House (Foreign Relocation After Marriage)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-12",
        version=1,
        name_en="7th Lord in 9th or 12th House (Foreign Relocation After Marriage)",
        name_ta="7-ஆம் அதிபதி 9 அல்லது 12-ஆம் வீட்டில் (திருமணத்திற்குப் பின் வெளிநாடு செல்லுதல்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 9, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 12, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Venus", "house": 12, "chart": "d1"},
            ]
        },
        interpretation_en="The 7th house rules marriage and spouse. When the 7th lord sits in the 9th (fortune/long travel) or 12th house (foreign land), or Venus (Kalathrakaraka) resides in the 12th, marriage becomes the catalyst for foreign travel and settlement overseas.",
        interpretation_ta="7-ஆம் வீடு திருமணம் மற்றும் வாழ்க்கைத் துணையைக் குறிக்கும். 7-ஆம் அதிபதி 9 அல்லது 12-ல் அமையும் போதோ அல்லது களத்திரகாரகன் சுக்கிரன் 12-ல் இருக்கும் போதோ திருமணத்திற்குப் பிறகு வெளிநாடு சென்று குடியேறும் யோகம் கூடுகிறது.",
        astrological_principle_en="Kalathra bhava connected to distant houses indicates the spouse either resides abroad or facilitates overseas relocation.",
        astrological_principle_ta="களத்திர ஸ்தானம் வெளிநாட்டு ஸ்தானங்களோடு தொடர்பு கொள்வது வாழ்க்கைத் துணையால் வெளிநாட்டு யோகத்தை உருவாக்குகிறது.",
        source_reference="Phaladeepika, Ch. 12; Brihat Jataka Ch. 20",
        limitations_en="Affliction to Venus by Rahu/Mars should be analyzed for smooth matrimonial adjustment in foreign culture.",
        limitations_ta="சுக்கிரனின் நிலையை ஆராய்ந்து அந்நிய கலாச்சாரத்தில் திருமண இணக்கத்தை உறுதி செய்ய வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-13: 11th Lord in 6th House (Foreign Employment & Lucrative Earnings)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-13",
        version=1,
        name_en="11th Lord in 6th House (Foreign Employment & Lucrative Earnings Abroad)",
        name_ta="11-ஆம் அதிபதி 6-ஆம் வீட்டில் (வெளிநாட்டு உத்தியோகம் மற்றும் அதிக வருவாய்)",
        category_slug="education_travel",
        subcategory="foreign_employment",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 11,
            "placed_in_house": 6,
            "chart": "d1"
        },
        interpretation_en="The 11th house signifies financial gains and fulfillment of desires, while the 6th house represents salaried employment and competitive services. When the 11th lord is in the 6th house, the native earns substantial wealth working in foreign organizations or multinational corporate employment.",
        interpretation_ta="11-ஆம் வீடு லாப ஸ்தானம், 6-ஆம் வீடு உத்தியோக ஸ்தானம். 11-ஆம் அதிபதி 6-ல் அமர்வது பன்னாட்டு நிறுவனங்களில் சிறந்த வேலைவாய்ப்பைப் பெற்று வெளிநாட்டில் மிகப்பெரிய பண வரவையும் புகழையும் ஈட்டும் யோகமாகும்.",
        astrological_principle_en="Labhadhipati in Satrubhava/Upachaya channels lucrative financial prosperity through external overseas employment.",
        astrological_principle_ta="லாபாதிபதி உபஜெய ஸ்தானமான 6-ல் இருப்பது அந்நிய நிறுவன சேவையின் வழி பெரும் தனலாபத்தைத் தருகிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 131",
        limitations_en="Hard work and competitive vigilance are required in corporate workplace.",
        limitations_ta="கார்ப்பரேட் நிறுவனங்களில் உழைப்பும் திறமையும் தொடர்ந்து தேவைப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-14: Lagna Lord in 7th House (Constant Business Travel Abroad)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-14",
        version=1,
        name_en="Lagna Lord in 7th House (Constant Business Travel Abroad)",
        name_ta="லக்னாதிபதி 7-ஆம் வீட்டில் (தொடர் தொழில்முறை வெளிநாட்டுப் பயணங்கள்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 1,
            "placed_in_house": 7,
            "chart": "d1"
        },
        interpretation_en="The 7th house represents foreign transactions, commercial contracts, and public engagement. Lagna lord in the 7th house directly aspects the 1st house while inhabiting the trade quadrant, causing frequent domestic and overseas business trips.",
        interpretation_ta="7-ஆம் வீடு வாணிபம் மற்றும் வெளிநாட்டுத் தொடர்புகளைக் குறிக்கும். லக்னாதிபதி 7-ல் அமர்ந்து லக்னத்தையே பார்ப்பதால் தொழில் மற்றும் வர்த்தக நிமித்தமாக அடிக்கடி வெளிநாடு சென்று வரும் சூழல் உண்டாகிறது.",
        astrological_principle_en="1st lord in 7th creates a dynamic pendulum between the native self and offshore business arenas.",
        astrological_principle_ta="லக்னாதிபதி 7-ல் அமர்வது ஜாதகரை சர்வதேச வர்த்தக மற்றும் கூட்டாண்மை பயணங்களில் தொடர்ந்து ஈடுபடுத்துகிறது.",
        source_reference="Saravali, Ch. 34; Phaladeepika Ch. 16",
        limitations_en="Frequent travel may create temporary separation from domestic hearth.",
        limitations_ta="அடிக்கடி பயணம் செய்வதால் குடும்பத்தை விட்டு தற்காலிகமாகப் பிரிய நேரிடலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-15: 3rd Lord in 9th or 12th House (Propensity for Overseas Journeys)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-15",
        version=1,
        name_en="3rd Lord in 9th or 12th House (Propensity for Overseas Journeys)",
        name_ta="3-ஆம் அதிபதி 9 அல்லது 12-ஆம் வீட்டில் (தூர தேச பயணங்கள் மற்றும் வெளிநாட்டு ஆர்வம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 3, "placed_in_house": 9, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 3, "placed_in_house": 12, "chart": "d1"},
            ]
        },
        interpretation_en="The 3rd house governs movement, short travel, and courage. When the 3rd lord is situated in the 9th house (long journeys) or 12th house (foreign territory), it merges short and long travel energies, imparting a natural affinity for foreign voyages.",
        interpretation_ta="3-ஆம் வீடு பயணம் மற்றும் சுறுசுறுப்பைக் குறிக்கும். 3-ஆம் அதிபதி 9 (நீண்ட பயணம்) அல்லது 12-ல் (வெளிநாடு) அமையும்போது கடல் கடந்த பயணங்களும் வெளிநாட்டுத் தொடர்புகளும் இயல்பாகவே அமைகின்றன.",
        astrological_principle_en="3rd house kinetic energy linked to 9th/12th axis creates sustained international mobility.",
        astrological_principle_ta="3-ஆம் அதிபதி 9 அல்லது 12-ல் இருப்பது நீண்ட தூர பயணங்களுக்கான இயல்பான ஆர்வத்தையும் வாய்ப்பையும் தருகிறது.",
        source_reference="Jataka Parijata, Ch. 11, Sloka 22",
        limitations_en="Expenditure on travels should be budgeted wisely.",
        limitations_ta="பயணங்களுக்கான செலவுகளைத் திட்டமிட்டு நிர்வகிக்க வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-16: Saturn in 12th House (Enduring Foreign Residence & Solitude)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-16",
        version=1,
        name_en="Saturn in 12th House (Enduring Foreign Residence & Diligent Labor Overseas)",
        name_ta="12-ஆம் வீட்டில் சனி (நீண்டகால வெளிநாட்டு வாசம் மற்றும் விடாமுயற்சி)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Saturn",
            "house": 12,
            "chart": "d1"
        },
        interpretation_en="Saturn represents endurance, perseverance, and detachment. Its placement in the 12th house fosters long-term residence away from one's birth region, sustained career efforts abroad, and disciplined adaptation to distant lands.",
        interpretation_ta="சனி பகவான் விடாமுயற்சி மற்றும் பொறுமையைக் குறிப்பவர். 12-ஆம் வீட்டில் சனி அமைவது பிறந்த ஊரை விட்டு நீண்ட காலம் தங்கி உழைக்கும் வெளிநாட்டு வாழ்க்கையையும் பொறுப்பான உத்தியோகத்தையும் குறிக்கிறது.",
        astrological_principle_en="Saturn in 12th anchors the native in foreign geography through disciplined work and solitary perseverance.",
        astrological_principle_ta="12-ல் சனி இருப்பது வெளிநாட்டில் கடின உழைப்பின் மூலம் நிலையான வாழ்க்கையை அமைத்துக் கொள்ள வழிசெய்கிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24; Saravali Ch. 30",
        limitations_en="Native may feel isolated or miss ancestral family roots at times.",
        limitations_ta="அந்நிய தேசத்தில் சில நேரங்களில் தனிமை உணர்வு அல்லது பூர்வீக ஏக்கம் ஏற்படலாம்.",
        severity=SeverityLevel.NEUTRAL,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-17: 12th Lord in 9th, 8th, or 6th House (Classic Foreign Settlement Yoga)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-17",
        version=1,
        name_en="12th Lord in 9th, 8th, or 6th House (Classic Foreign Settlement Yoga)",
        name_ta="12-ஆம் அதிபதி 9, 8 அல்லது 6-ல் (செட்டில்மென்ட் யோகம் / வெளிநாட்டு வாழ்க்கை)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 12, "placed_in_house": 9, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 12, "placed_in_house": 8, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 12, "placed_in_house": 6, "chart": "d1"},
            ]
        },
        interpretation_en="The 12th house governs foreign settlement. When the 12th lord is placed in the 9th house (fortune abroad) or the transformation/service houses (8th/6th), it weaves foreign living directly into the fabric of native destiny and fortune.",
        interpretation_ta="12-ஆம் அதிபதி 9-ஆம் வீட்டில் (பாக்கிய ஸ்தானம்) அல்லது 8, 6-ல் அமையும்போது வெளிநாட்டிலேயே நிரந்தரமாக வாழ்ந்து தனது பாக்கியத்தை அமைத்துக் கொள்ளும் உன்னத யோகம் உண்டாகிறது.",
        astrological_principle_en="Vyayadhipati placed in Bhagya (9th) or Trik houses aligns karmic fortune with overseas soil.",
        astrological_principle_ta="12-ஆம் அதிபதி 9-ல் அமர்வது வெளிநாட்டு மண்ணிலேயே ஒருவரது பாக்கியம் மற்றும் அதிர்ஷ்டம் அமைவதைக் காட்டுகிறது.",
        source_reference="Phaladeepika, Ch. 6, Sloka 35",
        limitations_en="Maintain legal documents and visa status meticulously during 12th lord sub-periods.",
        limitations_ta="12-ஆம் அதிபதியின் புக்தி காலத்தில் சட்ட ஆவணங்கள் மற்றும் விசா நடைமுறைகளில் கவனம் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-18: 11th Lord in 12th House (Global Social Circles & Overseas Friends)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-18",
        version=1,
        name_en="11th Lord in 12th House (Global Social Circles & Overseas Friends)",
        name_ta="11-ஆம் அதிபதி 12-ஆம் வீட்டில் (வெளிநாட்டு நண்பர்கள் மற்றும் சர்வதேச வட்டாரம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 11,
            "placed_in_house": 12,
            "chart": "d1"
        },
        interpretation_en="The 11th house signifies friends, peer networks, and social alliances. Placed in the 12th house of foreign lands, it creates friendships with foreigners, multinational peer networks, and strong social connections established abroad.",
        interpretation_ta="11-ஆம் வீடு நட்பு மற்றும் சமூக வட்டாரத்தைக் குறிக்கும். 11-ஆம் அதிபதி 12-ல் இருப்பது வெளிநாட்டவர்கள் மற்றும் சர்வதேச நண்பர்களுடன் சிறந்த நட்புறவையும் ஆதரவையும் பெற்றுத் தரும் யோகமாகும்.",
        astrological_principle_en="11th lord in 12th exports friendships, social networks, and cooperative gains overseas.",
        astrological_principle_ta="11-ஆம் அதிபதி 12-ல் அமர்ந்து வெளிநாட்டு நட்பு வட்டாரத்தையும் சர்வதேச ஆதரவையும் உருவாக்குகிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 137",
        limitations_en="Expenses on friends or hospitality abroad should be monitored.",
        limitations_ta="நண்பர்களுக்கான செலவுகள் மற்றும் விருந்தோம்பலை திட்டமிட்டுச் செய்வது நல்லது.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-19: Lagna in Movable Sign (Aries, Cancer, Libra, Capricorn - High Mobility)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-19",
        version=1,
        name_en="Lagna in Movable Sign (Aries, Cancer, Libra, Capricorn - Kinetic Mobility)",
        name_ta="சர ராசி லக்னம் (மேஷம், கடகம், துலாம், மகரம் - தொடர் இயக்க யோகம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "lagna_sign", "sign": "Aries", "chart": "d1"},
                {"condition_type": "lagna_sign", "sign": "Cancer", "chart": "d1"},
                {"condition_type": "lagna_sign", "sign": "Libra", "chart": "d1"},
                {"condition_type": "lagna_sign", "sign": "Capricorn", "chart": "d1"},
            ]
        },
        interpretation_en="Chara (movable) signs possess a fundamentally dynamic and mobile disposition. When the Ascendant falls in Aries, Cancer, Libra, or Capricorn, the native possesses inherent restlessness and readiness to relocate residence or travel across continents.",
        interpretation_ta="சர ராசிகள் நிலையற்ற, சுறுசுறுப்பான இயக்கத் தத்துவத்தைக் கொண்டவை. மேஷம், கடகம், துலாம், மகரம் ஆகிய சர லக்னங்களில் பிறந்தவர்கள் ஊர் மாற்றம் மற்றும் வெளிநாட்டுப் பயணங்களை எளிதாக ஏற்கும் மனப்பான்மை கொண்டவர்கள்.",
        astrological_principle_en="Chara Rashi Lagna provides the kinetic foundation required for changing countries and residences.",
        astrological_principle_ta="சர லக்ன அமைப்பு வாழிட மாற்றம் மற்றும் நாடு மாறுவதற்கான அடிப்படையான இயக்க சக்தியைத் தருகிறது.",
        source_reference="Brihat Jataka, Ch. 1, Sloka 8; Saravali Ch. 3",
        limitations_en="Fixed planets are required to maintain stability once settled abroad.",
        limitations_ta="வெளிநாட்டில் குடியேறிய பின் நிலைத்தன்மை பெற ஸ்திர ராசி அமைப்புகள் உதவும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # RULE-TRV-20: Moon in Kendra (1, 4, 7, 10 - Extensive Domestic and Global Travel)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-20",
        version=1,
        name_en="Moon in Kendra (1, 4, 7, 10 - High Travel Frequency within and outside Country)",
        name_ta="கேந்திரத்தில் சந்திரன் (1, 4, 7, 10 - உள்நாடு மற்றும் வெளிநாட்டுப் பயண யோகம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Moon", "house": 1, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Moon", "house": 4, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Moon", "house": 7, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Moon", "house": 10, "chart": "d1"},
            ]
        },
        interpretation_en="According to classical aphorisms, when the Moon occupies a Kendra (1st, 4th, 7th, or 10th house), the individual experiences frequent travels both within their home country and across international borders, constantly in motion.",
        interpretation_ta="செவ்வியல் ஜோதிட நூல்களின்படி, சந்திரன் 1, 4, 7, 10 ஆகிய கேந்திரங்களில் அமையும்போது ஜாதகர் உள்நாட்டிலும் வெளிநாட்டிலும் தொடர்ச்சியான பயணங்களை மேற்கொண்டு சுறுசுறுப்பாக இயங்குவார்.",
        astrological_principle_en="Moon in Kendras activates angular momentum across foundational pillars of the horoscope.",
        astrological_principle_ta="கேந்திர ஸ்தானங்களில் சந்திரன் அமர்வது தொடர் இயக்கத்தையும் பயண வாய்ப்புகளையும் உருவாக்குகிறது.",
        source_reference="Saravali, Ch. 23; Phaladeepika Ch. 8",
        limitations_en="Balance between busy travel schedule and resting periods is recommended.",
        limitations_ta="தொடர் பயணங்களால் உடல் சோர்வடையாமல் ஓய்வெடுப்பது நல்லது.",
        severity=SeverityLevel.FAVORABLE,
    ),
]
