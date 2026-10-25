"""Astrological Rules Registry & Classical Catalogue.

Provides initial verified rules across Marriage, Career, Lagna, Nakshatra,
Sexuality & Intimacy, Wealth, Children, and Education, along with database loading.
"""

from typing import List, Dict, Any, Optional
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

# ---------------------------------------------------------------------------
# Initial Verified Classical Rule Library
# ---------------------------------------------------------------------------

INITIAL_RULES_CATALOGUE: List[AstrologicalRuleDefinition] = [
    # -----------------------------------------------------------------------
    # A. Marriage & Relationships
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-01",
        version=1,
        name_en="7th Lord in 7th House (Swakshetra Sthana-Bala)",
        name_ta="7-ஆம் அதிபதி 7-ல் ஆட்சி பெறுதல்",
        category_slug="marriage_prospects",
        subcategory="first_marriage",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": 7,
            "chart": "d1"
        },
        interpretation_en="When the 7th house lord occupies its own 7th house, classical texts indicate a steady, supportive marital partnership, cultural affinity between partners, and strong relationship foundations.",
        interpretation_ta="7-ஆம் அதிபதி தனது சொந்த வீட்டில் (7-ஆம் பாவம்) ஆட்சி பெற்று அமர்வது நிலையான மற்றும் இணக்கமான திருமண வாழ்க்கையையும், சிறந்த வாழ்க்கைத் துணையையும் தரும் அமைப்பாகும்.",
        astrological_principle_en="Bhavat Bhava and Sthana-Bala principle: A lord occupying its own bhava shields that house from debility, fostering domestic stability and mutual fidelity.",
        astrological_principle_ta="பவாத் பாவ மற்றும் ஸ்தான பல விதி: ஒரு பாவத்தின் அதிபதி அதே பாவத்தில் ஆட்சி பெறும்போது அந்த பாவக காரகத்துவங்கள் பலமடைகின்றன.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 70",
        limitations_en="Aspects from combust or functional malefics can modify the expression of this placement.",
        limitations_ta="பாப கிரகங்களின் பார்வை அல்லது சேர்க்கை இருப்பின் பலன்களில் மாறுதல் ஏற்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-02",
        version=1,
        name_en="Jupiter in 7th House (Guru in Kalatra Sthana)",
        name_ta="7-ஆம் வீட்டில் குரு பகவான் அமர்வு",
        category_slug="marriage_prospects",
        subcategory="spouse_characteristics",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Jupiter",
            "house": 7,
            "chart": "d1"
        },
        interpretation_en="Jupiter in the 7th house indicates a virtuous, educated, and dignified spouse with strong ethical bearings. Jupiter aspects Lagna (1st house) by 7th Drishti, blessing physical vitality and wisdom.",
        interpretation_ta="7-ஆம் வீட்டில் தேவகுருவான குரு பகவான் வீற்றிருப்பது பண்பான, கற்றறிந்த, நற்குணங்கள் கொண்ட வாழ்க்கைத் துணையை அருளும். மேலும் 1-ஆம் பாவத்தை குரு பார்ப்பதால் ஜாதகருக்கு நீண்ட ஆயுளும் நற்புகழும் கிட்டும்.",
        astrological_principle_en="Natural benefic occupying Kendra with full aspect on Lagna confers dignity and social honor through wedlock (Karakobhava Nashaya caution applies when afflicted).",
        astrological_principle_ta="சுப கிரகமான குரு கேந்திரத்தில் அமர்ந்து லக்னத்தைப் பார்ப்பது இல்லற வாழ்வில் மரியாதையையும் சமூக அந்தஸ்தையும் நல்கும்.",
        source_reference="Phaladeepika, Ch. 8, Sloka 19",
        limitations_en="If Jupiter is combust or rules dusthanas (6/8/12), traditional texts note potential for partner rigidity.",
        limitations_ta="குரு மறைவு ஸ்தான அதிபதியாகி அஸ்தமனம் பெற்றிருந்தால் குணத்தில் பிடிவாதம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-03",
        version=1,
        name_en="Saturn in 7th House (Delayed / Mature Marriage Timing)",
        name_ta="7-ஆம் பாவத்தில் சனி பகவான் அமர்வு (காலதாமதத் திருமணம்)",
        category_slug="delayed_marriage",
        subcategory="delayed_marriage",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Saturn",
            "house": 7,
            "chart": "d1"
        },
        interpretation_en="Saturn in the 7th house traditionally signifies mature or delayed timing of marriage (often after age 28-30). It fosters a realistic, duty-conscious partnership requiring patience and emotional maturity.",
        interpretation_ta="7-ஆம் பாவத்தில் சனி பகவான் அமர்வது பொறுமை, கடமை உணர்வு மற்றும் பக்குவமான திருமண பந்தத்தை குறிக்கிறது. பொதுவாக 28-30 வயதுக்கு மேல் திருமணம் அமைவது நற்பலனைத் தரும்.",
        astrological_principle_en="Saturn slows and structures karma related to the house it occupies, demanding steady commitment over hasty infatuation.",
        astrological_principle_ta="சனி பகவான் நின்ற பாவத்தின் காரகத்துவங்களை தாமதப்படுத்தி, பக்குவத்தையும் ஸ்திரத்தன்மையையும் வழங்குகிறார்.",
        source_reference="Brihat Jataka, Ch. 20, Sloka 8",
        limitations_en="If Saturn is in own sign (Capricorn/Aquarius) or exalted (Libra), it forms Sasa Yoga rather than destructive delay.",
        limitations_ta="சனி துலாம், மகரம், கும்பத்தில் இருக்கும் போது சச யோகம் உண்டாகி சுப பலன்கள் அதிகரிக்கும்.",
        severity=SeverityLevel.NEUTRAL,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-04",
        version=1,
        name_en="Second Marriage / Dual Sign Influence on 7th House",
        name_ta="7-ஆம் பாவகத்தில் உபய ராசி மற்றும் புதன் தாக்கம்",
        category_slug="second_marriage",
        subcategory="second_marriage",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [3, 6, 9, 12],  # Gemini, Virgo, Sagittarius, Pisces Lagna (makes 7th a dual sign)
                    "chart": "d1"
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mercury",
                    "house": [7, 2, 11],
                    "chart": "d1"
                }
            ]
        },
        interpretation_en="When a dual sign rises on the 7th cusp alongside Mercury's influence on 7th or 2nd houses, classical canons observe multiplicity of partnerships or significant phases in domestic life.",
        interpretation_ta="7-ஆம் பாவம் உபய ராசியாகி (மிதுனம், கன்னி, தனுசு, மீனம்), புதனின் தொடர்பும் அமையும் போது வாழ்க்கையில் ஒன்றுக்கு மேற்பட்ட திருமண அல்லது கூட்டு ஒப்பந்த வாய்ப்புகள் அமையும் சாத்தியக்கூறுகளை பாரம்பரிய நூல்கள் கூறுகின்றன.",
        astrological_principle_en="Dvisvabhava (dual/mutable) signs inherently signify adaptability and recurrence of experiences under qualifying planetary dasas.",
        astrological_principle_ta="உபய ராசிகள் இயற்கையிலேயே மாற்றங்களையும் தொடர் நிகழ்வுகளையும் குறிக்கும் தன்மை கொண்டவை.",
        source_reference="Saravali, Ch. 35, Sloka 42",
        limitations_en="Strong benefic aspects from Jupiter or single strong 7th lord can preserve a singular lifelong marriage.",
        limitations_ta="குருவின் சுபப் பார்வை வலுவாக அமைந்தால் ஒரே திருமண பந்தம் நிலைத்து நிற்கும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-05",
        version=1,
        name_en="Mars-Venus Mutual Parashari Drishti (Passionate Dynamics)",
        name_ta="செவ்வாய் - சுக்கிரன் பரஸ்பர பார்வை யோகம்",
        category_slug="relationship_compatibility",
        subcategory="attraction_interpretations",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_aspect",
            "aspecting_planet": "Mars",
            "target_type": "planet",
            "target_value": "Venus",
            "aspect_type": "any",
            "chart": "d1"
        },
        interpretation_en="When Mars aspects Venus, traditional Jyotish highlights strong interpersonal magnetism, expressive romantic enthusiasm, and passionate creative energy.",
        interpretation_ta="செவ்வாய் பகவான் சுக்கிரனைப் பார்க்கும் போது தீவிரமான அன்பும் ஈர்ப்பும், உணர்ச்சிமிக்க கலை மற்றும் தாம்பத்திய நாட்டமும் உண்டாகும்.",
        astrological_principle_en="Mars (pitta/fire, initiative) energizes Venus (water/aesthetics, desire), producing dynamic attraction and vivid emotional expression.",
        astrological_principle_ta="செவ்வாயின் நெருப்பும் சுக்கிரனின் அழகியலும் இணையும் போது கவர்ச்சியும் உணர்ச்சிப் பெருக்கும் இயல்பாக வெளிப்படும்.",
        source_reference="Jataka Parijata, Ch. 14, Sloka 28",
        limitations_en="Requires calm communication to prevent impulsive reactions during Mars or Venus sub-periods.",
        limitations_ta="செவ்வாய் அல்லது சுக்கிரன் தசா-புக்திகளில் உணர்ச்சிவசப்பட்டு முடிவெடுப்பதைத் தவிர்ப்பது நலம்.",
        severity=SeverityLevel.NEUTRAL,
    ),

    # -----------------------------------------------------------------------
    # B. Career & Profession
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-CAR-01",
        version=1,
        name_en="Sun in 10th House with Directional Strength (Digbala)",
        name_ta="10-ஆம் வீட்டில் திக்பலம் பெற்ற சூரியன் (அரசு மற்றும் தலைமைப் பதவி)",
        category_slug="career_profession",
        subcategory="government_employment",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Sun",
            "house": 10,
            "chart": "d1"
        },
        interpretation_en="The Sun attains maximum directional strength (Digbala) in the 10th house (Zenith/Karma Sthana). This confers innate executive authority, leadership potential, administrative capability, and respect from government or institutional hierarchies.",
        interpretation_ta="10-ஆம் வீட்டில் சூரியன் திக்பலம் பெற்று உச்ச பலம் அடைகிறார். இதனால் அரசுப் பணி, தலைமைப் பொறுப்பு, நிர்வாகத் திறன் மற்றும் சமூகத்தில் உயரிய கௌரவம் கிட்டும்.",
        astrological_principle_en="Digbala doctrine: Sun at zenith radiates maximum light and executive sovereignty in the house of worldly action (Karmasthana).",
        astrological_principle_ta="திக்பல விதி: நடுப்பகல் சூரியன் 10-ஆம் பாவத்தில் ஆளுகை செலுத்துவது தொழில் மேன்மையையும் தலைமைத்துவத்தையும் வழங்கும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 28, Sloka 12",
        limitations_en="Combustion of other planets or affliction by Rahu (Eclipse axis) can trigger political friction.",
        limitations_ta="ராகு-கேது சேர்க்கை அல்லது கிரகணம் ஏற்பட்டால் அதிகாரிகளுடன் கருத்து வேறுபாடு தோன்றும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-CAR-02",
        version=1,
        name_en="10th Lord in 1st House (Self-Determined Professional Success)",
        name_ta="10-ஆம் அதிபதி லக்னத்தில் அமர்வு",
        category_slug="career_profession",
        subcategory="business_entrepreneurship",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 10,
            "placed_in_house": 1,
            "chart": "d1"
        },
        interpretation_en="The 10th lord occupying Lagna signifies a self-made professional identity, independent entrepreneurship, personal brand recognition, and initiative-driven success.",
        interpretation_ta="10-ஆம் அதிபதி லக்னத்தில் அமர்வது சுயதொழில் ஆர்வம், சுயமாக முன்னேறும் ஆற்றல், சொந்த முயற்சியால் கிட்டும் புகழ் மற்றும் தொழில் மேன்மையை குறிக்கும்.",
        astrological_principle_en="Kendra lord placed in Trikona/Lagna unites action (Karma) with personal identity (Tanu), producing strong agency.",
        astrological_principle_ta="கன்ம ஸ்தானாதிபதி லக்னத்தில் அமர்வது சுய முயற்சியால் வாழ்க்கையில் உயர்ந்த நிலையை அடைய உதவும்.",
        source_reference="Phaladeepika, Ch. 16, Sloka 22",
        limitations_en="Benefic placement of Lagna lord itself is necessary to sustain physical stamina under heavy workload.",
        limitations_ta="லக்னாதிபதியும் பலம் பெற்றிருந்தால் மட்டுமே பணிச்சுமையை சமாளித்து வெற்றி பெற இயலும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-CAR-03",
        version=1,
        name_en="Saturn in 10th House (Steady Rise to Authority)",
        name_ta="10-ஆம் வீட்டில் சனி பகவான் (படிப்படியான தொழில் உயர்வு)",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Saturn",
            "house": 10,
            "chart": "d1"
        },
        interpretation_en="Saturn in the 10th house indicates dedication to hard work, organizational discipline, and gradual yet enduring ascent in career. Maturity brings considerable institutional authority.",
        interpretation_ta="10-ஆம் வீட்டில் சனி பகவான் அமர்வது கடின உழைப்பு, விடாமுயற்சி, பொறுப்புணர்வை வளர்த்து, முற்பகுதியில் போராட்டங்களையும் பிற்பகுதியில் மிக உயர்ந்த அந்தஸ்தையும் தரும்.",
        astrological_principle_en="Saturn governs persistence and mass organizations; in the 10th house it builds durable structures that withstand adversity.",
        astrological_principle_ta="கர்மகாரகன் சனி 10-ல் இருப்பது நிலையான, வீழ்ச்சியடையாத தொழில் வளர்ச்சியை காலம் கடந்து அருளும்.",
        source_reference="Saravali, Ch. 30, Sloka 77",
        limitations_en="Early career may involve strenuous effort and humble beginnings before recognition solidifies.",
        limitations_ta="தொடக்க காலத்தில் அதிக உழைப்பும் அதற்கேற்ற பலன் தாமதமும் ஏற்படலாம்.",
        severity=SeverityLevel.NEUTRAL,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-CAR-04",
        version=1,
        name_en="Mercury in 10th House (Commercial & Analytical Intellect)",
        name_ta="10-ஆம் வீட்டில் புதன் பகவான் (வணிகம் மற்றும் அறிவுசார் தொழில்)",
        category_slug="career_profession",
        subcategory="business_entrepreneurship",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Mercury",
            "house": 10,
            "chart": "d1"
        },
        interpretation_en="Mercury in the 10th house fosters sharp commercial acumen, communication mastery, analytical consulting prowess, accounting expertise, or success in media and publishing.",
        interpretation_ta="10-ஆம் பாவத்தில் புதன் அமர்வது எழுத்து, ஊடகம், கணக்கியல், வர்த்தகம், தகவல் தொழில்நுட்பம் மற்றும் ஆலோசனைத் துறைகளில் சிறந்து விளங்க உதவும்.",
        astrological_principle_en="Budha in Karmasthana confers agility of mind, eloquence in negotiations, and multi-disciplinary career flexibility.",
        astrological_principle_ta="புத்தி காரகனான புதன் 10-ல் அமர்ந்து தொழில் திறமை மற்றும் பேச்சாற்றலால் வருமானத்தை பெருக்குகிறார்.",
        source_reference="Brihat Jataka, Ch. 20, Sloka 5",
        limitations_en="Retrograde Mercury may produce periodic changes in business focus or contracts.",
        limitations_ta="புதன் வக்கிரமாக இருந்தால் தொழில் ஒப்பந்தங்களில் கவனம் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # C. Personality & Birth Characteristics
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-PERS-01",
        version=1,
        name_en="Aries Ascendant (Mesha Lagna - Pioneering Initiative)",
        name_ta="மேஷ லக்னம் (முன்னோடி மற்றும் வீரம்)",
        category_slug="personality_birth",
        subcategory="lagna_characteristics",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "lagna_sign",
            "sign": 1,
            "chart": "d1"
        },
        interpretation_en="Aries Lagna individuals exhibit innate courage, entrepreneurial drive, directness, and spontaneous leadership. Governed by Mars, they thrive in challenging competitive environments.",
        interpretation_ta="மேஷ லக்னத்தில் பிறந்தவர்கள் அஞ்சா நெஞ்சம், தலைமைத் திறன், சுறுசுறுப்பு மற்றும் நேர்மையான சுபாவம் கொண்டவர்கள். செவ்வாயின் ஆதிக்கத்தால் சவால்களை எதிர்கொண்டு வெல்லும் ஆற்றல் படைத்தவர்கள்.",
        astrological_principle_en="Movable Fire sign ruled by Mars: Primal spark of creation granting boldness, rapid recuperation, and intolerance of sluggishness.",
        astrological_principle_ta="சர அக்னி ராசி: செவ்வாயின் ஆதிக்கம் காரிய வீரியத்தையும் வேகம் கலந்த துணிவையும் தருகிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 4, Sloka 6",
        limitations_en="Patience and sustained follow-through must be cultivated to complement rapid beginnings.",
        limitations_ta="பொறுமையுடன் கூடிய திட்டமிடல் இருந்தால் முழுமையான வெற்றியை அடையலாம்.",
        severity=SeverityLevel.INFO,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-PERS-02",
        version=1,
        name_en="Taurus Ascendant (Vrishabha Lagna - Grounded Steadfastness)",
        name_ta="ரிஷப லக்னம் (நிலைத்தன்மை மற்றும் கலை நாட்டம்)",
        category_slug="personality_birth",
        subcategory="lagna_characteristics",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "lagna_sign",
            "sign": 2,
            "chart": "d1"
        },
        interpretation_en="Taurus Lagna natives possess tremendous perseverance, aesthetic refinement, financial prudence, and loyalty. Ruled by Venus, they seek material comfort and serene environments.",
        interpretation_ta="ரிஷப லக்னத்தில் பிறந்தவர்கள் விடாமுயற்சி, பொறுமை, கலை ஆர்வம், நிதி நிர்வாகத் திறன் மற்றும் விசுவாசம் நிறைந்தவர்கள். சுக்கிரனின் ஆதிக்கத்தால் நளினமும் வசதியான வாழ்வும் விரும்புவர்.",
        astrological_principle_en="Fixed Earth sign ruled by Shukra: Unyielding determination, sensory appreciation, and capacity to accumulate tangible wealth.",
        astrological_principle_ta="ஸ்திர பூமி ராசி: சுக்கிரனின் அருள் செல்வ சேமிப்பையும் அழகியல் நாட்டத்தையும் வழங்குகிறது.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 4, Sloka 7",
        limitations_en="Reluctance to embrace swift transitions or change established routines.",
        limitations_ta="திடீர் மாற்றங்களை ஏற்கத் தயங்குதல் மற்றும் பிடிவாதக் குணம் தவிர்க்கப்பட வேண்டும்.",
        severity=SeverityLevel.INFO,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-PERS-03",
        version=1,
        name_en="Moon in Rohini Nakshatra (Charm & Emotional Magnetism)",
        name_ta="ரோகிணி நட்சத்திரத்தில் சந்திரன் (கவர்ச்சி மற்றும் கலை உணர்வு)",
        category_slug="personality_birth",
        subcategory="nakshatra_characteristics",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_nakshatra",
            "planet": "Moon",
            "nakshatra": "Rohini"
        },
        interpretation_en="Moon in Rohini (its favorite Nakshatra) bestows physical grace, artistic sensibilities, persuasive speech, emotional warmth, and love for nature and luxury.",
        interpretation_ta="சந்திரன் தனக்கு மிகவும் பிரியமான ரோகிணி நட்சத்திரத்தில் சஞ்சரிப்பது எழிலான தோற்றம், இனிமையான பேச்சு, வசீகரக் குணம் மற்றும் கலைகளில் ஈடுபாட்டை அருளும்.",
        astrological_principle_en="Rohini is ruled by Moon in Taurus (exaltation sign of Moon), presided over by Prajapati, signifying fertility, beauty, and creative abundance.",
        astrological_principle_ta="ரிஷபத்தில் உச்சம் பெறும் ரோகிணியில் சந்திரன் அமர்வது மன அமைதியையும் கவர்ச்சிகரமான ஆளுமையையும் தரும்.",
        source_reference="Brihat Samhita, Ch. 15, Sloka 5",
        limitations_en="Tendency toward indulgence in luxury or emotional sensitivity to criticism.",
        limitations_ta="ஆடம்பரத்தில் அதீத ஆர்வம் மற்றும் உணர்ச்சிவசப்படுதல் ஏற்பட வாய்ப்புண்டு.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-PERS-04",
        version=1,
        name_en="Jupiter Exalted in Cancer (Hamsa Mahapurusha Dignity)",
        name_ta="கடகத்தில் உச்சம் பெற்ற குரு (ஹம்ச யோகம்)",
        category_slug="personality_birth",
        subcategory="planetary_strengths",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Jupiter",
            "dignity": "exalted",
            "chart": "d1"
        },
        interpretation_en="Jupiter reaches its deep exaltation in Cancer (Katakam). This bestows expansive philosophical wisdom, high ethical standards, benevolent generosity, and profound respect from society.",
        interpretation_ta="கடக ராசியில் குரு பகவான் உச்சம் பெறுவது ஆன்மீக ஞானம், அறநெறி வழுவாத வாழ்க்கை, பரந்த மனப்பான்மை மற்றும் சமுதாயத்தில் மிக உயர்ந்த மரியாதையை நல்கும்.",
        astrological_principle_en="Uccha Guru elevates Sattva guna to its highest state, shielding the native's character and supporting ethical pursuits.",
        astrological_principle_ta="குருவின் உச்ச நிலை சத்துவ குணத்தை வளர்த்து, தெய்வீக அருளையும் குடும்ப மேன்மையையும் உறுதி செய்கிறது.",
        source_reference="Saravali, Ch. 27, Sloka 8",
        limitations_en="Requires practical grounding to avoid overly idealistic or trusting decisions.",
        limitations_ta="அளவுக்கு மிஞ்சிய நம்பிக்கையால் ஏமாறாமல் நடைமுறைக்கு உகந்த முடிவுகளை எடுக்க வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # D. Sexuality & Intimacy (Nuanced, Classical, Non-stigmatizing)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-SEXI-01",
        version=1,
        name_en="Venus-Rahu Close Conjunction in Passionate Signs (Traditional Jyotish Heuristic)",
        name_ta="சுக்கிரன் - ராகு நெருக்கமான சேர்க்கை (பாரம்பரிய ஜோதிட அணுகுமுறை)",
        category_slug="sexuality_intimacy",
        subcategory="attraction_interpretations",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_conjunction",
                    "planets": ["Venus", "Rahu"],
                    "same_sign_only": True,
                    "orb_degrees": 8.0,
                    "chart": "d1"
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Venus",
                    "sign": [1, 2, 7, 8, 12],  # Aries, Taurus, Libra, Scorpio, Pisces
                    "chart": "d1"
                }
            ]
        },
        interpretation_en="In classical Jyotish tradition, a close conjunction of Venus and Rahu within an 8-degree orb in Venus- or Mars-influenced signs is symbolically interpreted as magnifying romantic imagination, attraction toward unconventional beauty, and intense sensory enthusiasm. This traditional heuristic reflects creative curiosity and emotional depth rather than a deterministic psychological diagnosis.",
        interpretation_ta="பாரம்பரிய ஜோதிட சாஸ்திரத்தில் சுக்கிரனும் ராகுவும் 8 பாகைக்குள் நெருங்கி சுக்கிர/செவ்வாய் ராசிகளில் இணைவது அதீத கற்பனை வளம், புதிய அழகியல் மீதான நாட்டம் மற்றும் உணர்ச்சிமிக்க கலை ஆர்வத்தை குறிக்கும். இது நல்வழியில் வழிநடத்தப்பட வேண்டிய மனோசக்தி.",
        astrological_principle_en="Rahu amplifies the significations of the planet it closely conjoins; uniting with Shukra (sensory beauty and desire), it encourages boundary-expanding aesthetic and romantic exploration.",
        astrological_principle_ta="ராகு தான் இணையும் கிரகத்தின் காரகத்துவங்களை பன்மடங்கு பெருக்குவதால், சுக்கிரனோடு சேரும் போது காதல் மற்றும் கலை ஆர்வத்தை விரிவுபடுத்துகிறது.",
        source_reference="Jataka Parijata, Ch. 8, Sloka 34; Phaladeepika, Ch. 18",
        limitations_en="Deterministic assumptions about private behavior or morality must never be drawn. Jupiter's aspect or functional benefic dignity channels this configuration into stellar creative and artistic achievement.",
        limitations_ta="குருவின் சுபப் பார்வை இருப்பின் இந்நிலை மிகச் சிறந்த திரைக்கலை, நாடகம் மற்றும் உலகளாவிய கலைத் துறை வெற்றியாக உருமாறும்.",
        severity=SeverityLevel.MIXED,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-SEXI-02",
        version=1,
        name_en="Venus in 12th House (Shayana Sukha - Bedroom Comfort & Aesthetics)",
        name_ta="12-ஆம் வீட்டில் சுக்கிரன் (சயன சுகம் மற்றும் அமைதி)",
        category_slug="sexuality_intimacy",
        subcategory="intimacy_themes",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Venus",
            "house": 12,
            "chart": "d1"
        },
        interpretation_en="Classical Vedic texts note that Venus uniquely prospers in the 12th house (traditionally known as Shayana Sukha or bedroom comfort). It fosters appreciation for sensory luxuries, restful sanctuary, and affectionate private intimacy.",
        interpretation_ta="ஜோதிட சாஸ்திரப்படி 12-ஆம் வீட்டில் சுக்கிரன் அமர்வது சயன சுகம், நிம்மதியான உறக்கம், ஆடம்பரமான வாழ்க்கைச் சூழல் மற்றும் தாம்பத்திய அன்யோன்யத்தை நல்கும் சிறப்பு அமைப்பாகும்.",
        astrological_principle_en="Shukra is the only natural benefic considered intrinsically happy in the 12th house (house of surrender and sensory relaxation).",
        astrological_principle_ta="மறைவு ஸ்தானமான 12-ல் சுக்கிரன் இருப்பது மட்டுமே சுப பலன்களை தந்து சுகபோகங்களை வளர்க்கும் விதிவிலக்கு பெற்ற அமைப்பாகும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 28, Sloka 14",
        limitations_en="Prudent financial tracking is recommended to regulate lavish expenditures on luxuries.",
        limitations_ta="ஆடம்பரச் செலவுகளைக் கட்டுப்படுத்தி சேமிப்பில் கவனம் செலுத்த வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # E. Money & Assets
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-WLTH-01",
        version=1,
        name_en="11th Lord in 2nd House (Dhana-Labha Interlocking Yoga)",
        name_ta="11-ஆம் அதிபதி 2-ஆம் வீட்டில் அமர்வு (தன-லாப யோகம்)",
        category_slug="money_assets",
        subcategory="wealth_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 11,
            "placed_in_house": 2,
            "chart": "d1"
        },
        interpretation_en="When the 11th lord (gains, aspirations) resides in the 2nd house (accumulated wealth, financial assets), classical texts establish a prominent Dhana Yoga. Income flows naturally into tangible savings and family prosperity.",
        interpretation_ta="11-ஆம் அதிபதி (லாபம்) 2-ஆம் வீட்டில் (தன ஸ்தானம்) அமர்வது மிகச் சிறந்த தன யோகமாகும். வருமானம் சேமிப்பாக மாறி சொத்துக்கள் பெருகும்.",
        astrological_principle_en="Direct linkage between Labhasthana (11th) and Dhanasthana (2nd) converts professional revenues into long-term liquid and real capital.",
        astrological_principle_ta="லாபமும் தனமும் ஒன்றுடன் ஒன்று தொடர்பு கொள்வது வாழ்நாள் முழுவதும் பணப்புழக்கத்தை உறுதி செய்யும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 41, Sloka 3",
        limitations_en="Combustion or dusthana aspects to 2nd house require systematic investment discipline.",
        limitations_ta="2-ஆம் பாவம் பாப கிரகங்களால் பாதிக்கப்பட்டால் பண விரயங்களைத் தவிர்க்க திட்டமிடுதல் அவசியம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-WLTH-02",
        version=1,
        name_en="Jupiter Aspecting 2nd House (Dhanakaraka Aspect)",
        name_ta="2-ஆம் பாவத்தை பார்க்கும் குரு பகவான் (தன காரகப் பார்வை)",
        category_slug="money_assets",
        subcategory="savings_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_aspect",
            "aspecting_planet": "Jupiter",
            "target_type": "house",
            "target_value": 2,
            "aspect_type": "any",
            "chart": "d1"
        },
        interpretation_en="Jupiter's benefic aspect on the 2nd house protects financial solvency, encourages ethical earnings, sweetens family discourse, and promotes sustainable wealth accumulation.",
        interpretation_ta="குருவின் சுபப் பார்வை 2-ஆம் பாவத்தின் மீது விழுவது தன பலத்தை கூட்டி, குடும்பத்தில் சுபகாரியங்களை நிகழ்த்தி, நேர்மையான வழிகளில் செல்வம் சேர வழிவகுக்கும்.",
        astrological_principle_en="Guru is Dhanakaraka (significator of wealth) and Kutumbakaraka; its aspect cleanses and expands the affairs of the 2nd bhava.",
        astrological_principle_ta="தனகாரகனான குருவின் பார்வை குடும்ப அமைதியையும் பொருளாதார ஸ்திரத்தன்மையையும் நிலைநாட்டும்.",
        source_reference="Phaladeepika, Ch. 15, Sloka 8",
        limitations_en="Jupiter ruling 6th or 8th house may introduce occasional expenses on welfare or pilgrimage.",
        limitations_ta="குரு மறைவு ஸ்தான அதிபதியாக இருப்பின் சுபச் செலவுகள் அதிகரிக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-WLTH-03",
        version=1,
        name_en="Mars in 4th House in Fixed Sign (Landed Property Yoga)",
        name_ta="4-ஆம் பாவத்தில் பூமி காரகன் செவ்வாய் (நிலம், பூமி யோகம்)",
        category_slug="money_assets",
        subcategory="property_land",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "house": 4,
                    "chart": "d1"
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Mars",
                    "sign": [1, 2, 8, 10],  # Aries, Taurus, Scorpio, Capricorn
                    "chart": "d1"
                }
            ]
        },
        interpretation_en="Mars as Bhoomi Karaka (significator of land) in the 4th house (Matru & Griha Sthana) in its own or exaltation sign bestows substantial real estate holdings, land ownership, and permanent residences.",
        interpretation_ta="பூமி காரகனான செவ்வாய் 4-ஆம் வீட்டில் ஆட்சி அல்லது உச்சம் பெற்று அமைவது சொந்த வீடு, விவசாய நிலம் மற்றும் ரியல் எஸ்டேட் சொத்துக்கள் சேரும் பாக்கியத்தை தரும்.",
        astrological_principle_en="Kendra placement of Bhoomi Karaka in Sukhastana produces tangible immoveable property assets (Ruchaka yoga when in Kendra in own/exalted sign).",
        astrological_principle_ta="ருசக யோக அமைப்புடன் செவ்வாய் 4-ல் அமைவது சொந்த மனை, அடுக்குமாடி இல்லங்களை நல்கும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 40",
        limitations_en="Kuja Dosha considerations apply regarding domestic adjustments.",
        limitations_ta="செவ்வாய் தோஷ அம்சங்கள் இருப்பதால் குடும்பத்தில் விட்டுக் கொடுத்துச் செல்வது நலம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # F. Family & Children
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-FAM-01",
        version=1,
        name_en="5th Lord in 5th House (Santan Prapti / Putrabhava Strength)",
        name_ta="5-ஆம் அதிபதி 5-ல் ஆட்சி (புத்திர பாக்கிய யோகம்)",
        category_slug="family_children",
        subcategory="children_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 5,
            "placed_in_house": 5,
            "chart": "d1"
        },
        interpretation_en="The 5th lord placed in its own 5th house strongly confirms progeny blessing, cultured and accomplished children, deep intellect, and past-life meritorious karma (Purva Punya).",
        interpretation_ta="5-ஆம் அதிபதி 5-ஆம் பாவத்திலேயே ஆட்சி பெறுவது சிறந்த புத்திர பாக்கியத்தையும், நற்குணங்கள் நிறைந்த பிள்ளைகளையும், பூர்வ புண்ணிய பலன்களையும் உறுதி செய்யும்.",
        astrological_principle_en="Sthana-Bala of Purva Punya lord protects lineage, creative progeny, and intuitive intelligence.",
        astrological_principle_ta="பூர்வ புண்ணிய ஸ்தானாதிபதி பலம் பெறுவது வம்ச விருத்தியையும் மன நிம்மதியையும் வழங்கும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 50",
        limitations_en="Node conjunction (Rahu/Ketu) on 5th house can require traditional pacification.",
        limitations_ta="ராகு-கேது சேர்க்கை இருப்பின் குழந்தை பிறப்பில் சற்று தாமதம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # G. Education & Travel
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-EDU-01",
        version=1,
        name_en="Mercury & Jupiter Favorable Association (High Learning & Wisdom)",
        name_ta="புதன் - குரு சுப சேர்க்கை அல்லது பார்வை (உயர் கல்வி யோகம்)",
        category_slug="education_travel",
        subcategory="higher_education",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "planet_conjunction",
                    "planets": ["Mercury", "Jupiter"],
                    "same_sign_only": True,
                    "chart": "d1"
                },
                {
                    "condition_type": "planet_aspect",
                    "aspecting_planet": "Jupiter",
                    "target_type": "planet",
                    "target_value": "Mercury",
                    "aspect_type": "any",
                    "chart": "d1"
                }
            ]
        },
        interpretation_en="The harmonious combination of Mercury (analytical intellect) and Jupiter (philosophical wisdom) produces stellar academic credentials, teaching capability, scholarly reputation, and aptitude for advisory roles.",
        interpretation_ta="புத்தியின் நாயகன் புதனும் ஞானத்தின் நாயகன் குருவும் இணைவது அல்லது பார்ப்பது சரஸ்வதி யோகத்தை உண்டாக்கி, உயர்கல்வி, ஆராய்ச்சி, பேராசிரியர் பணி மற்றும் மேன்மையான அறிவாற்றலைத் தரும்.",
        astrological_principle_en="Synthesis of Vidyakaraka (Jupiter) and Buddhirkaraka (Mercury) unifies critical logic with expansive dharmic understanding.",
        astrological_principle_ta="வித்யா காரகன் குருவும் புத்தி காரகன் புதனும் இணைவது கல்வித் துறையில் சாதனை படைக்க வழிவகுக்கும்.",
        source_reference="Jataka Parijata, Ch. 7, Sloka 18",
        limitations_en="Combustion of Mercury by close Sun proximity should be checked for exam anxiety.",
        limitations_ta="புதன் சூரியனுடன் மிக நெருங்கி அஸ்தமனம் அடைந்திருந்தால் தேர்வு சமயங்களில் பதற்றம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-TRV-01",
        version=1,
        name_en="9th Lord in 12th House (Foreign Residence & Long Voyages)",
        name_ta="9-ஆம் அதிபதி 12-ல் அமைதல் (வெளிநாட்டுப் பயணம் மற்றும் குடியேற்றம்)",
        category_slug="education_travel",
        subcategory="foreign_travel",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 9,
            "placed_in_house": 12,
            "chart": "d1"
        },
        interpretation_en="Placement of the 9th lord (long journeys, higher fortune) in the 12th house (foreign lands, distant realms) strongly indicates living, studying, or establishing residence abroad.",
        interpretation_ta="பாக்யாதிபதியான 9-ஆம் அதிபதி 12-ஆம் வீட்டில் (வெளிநாடு) அமர்வது கடல் கடந்த பயணம், வெளிநாட்டில் கல்வி பயிலுதல் அல்லது நீண்ட காலம் வசிக்கும் யோகத்தை அருளும்.",
        astrological_principle_en="Bhagya (9th) operating in the house of foreign soils (12th) activates prosperity through distant migrations.",
        astrological_principle_ta="பாக்ய ஸ்தானாதிபதி விரய ஸ்தானத்தில் அமர்வது அந்நிய தேசத்தில் மேன்மையையும் அதிர்ஷ்டத்தையும் தரும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka 92",
        limitations_en="Periodic home visits are advised to maintain domestic roots and ancestral connections.",
        limitations_ta="தாய்நாட்டின் தொடர்பைத் தக்கவைத்துக் கொள்வது மன அமைதியைத் தரும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # H. Cross-Chart (D1 + D9) & KP Rules
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-VARGA-01",
        version=1,
        name_en="Jupiter Vargottama Dignity (D1 Rasi and D9 Navamsa Concordance)",
        name_ta="வர்கோத்தமம் பெற்ற குரு பகவான் (D1 மற்றும் D9 சமநிலை)",
        category_slug="personality_birth",
        subcategory="planetary_strengths",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.BOTH,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Jupiter",
            "dignity": "vargottama",
            "chart": "both"
        },
        interpretation_en="When Jupiter occupies the same zodiac sign in both Rasi (D1) and Navamsa (D9), it attains Vargottama dignity. Classical canons equate Vargottama strength to own-sign rulership, conferring unwavering moral judgment, noble character, and lasting divine grace.",
        interpretation_ta="ராசி சக்கரம் (D1) மற்றும் நவாம்சம் (D9) ஆகிய இரண்டிலும் குரு பகவான் ஒரே ராசியில் அமர்வது வர்கோத்தம பலமாகும். இது சுய ஆட்சிக்கு சமமான வலிமையை தந்து அறநெறி, வாக்கு பலிதம் மற்றும் தொடர் நற்பலன்களை உறுதி செய்யும்.",
        astrological_principle_en="Vargottama bridges the physical reality (D1) with internal spiritual resilience (D9), making the planet's auspicious promises unshakeable.",
        astrological_principle_ta="வர்கோத்தம விதி: இரு முக்கிய சக்கரங்களிலும் ஒரே ராசியில் இருப்பது கிரகத்தின் முழுமையான சுபத்துவத்தை வெளிப்படுத்தும்.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 6, Sloka 31",
        limitations_en="Combustion by Sun reduces outer material display while retaining inner spiritual integrity.",
        limitations_ta="சூரியனுடன் அஸ்தமனம் பெற்றிருந்தால் புற உலக நன்மைகளை விட அகத்தூய்மை அதிகமாகும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-KP-01",
        version=1,
        name_en="KP 7th Cusp Sub-Lord Signifies 2, 7, 11 (Marital Promise)",
        name_ta="கே.பி 7-ஆம் பாவ உப அதிபதி 2, 7, 11 தொடர்புகள் (திருமண உறுதி)",
        category_slug="marriage_relationships",
        subcategory="marriage_prospects",
        astrology_system=AstrologySystem.KP,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "kp_sub_lord",
            "cusp": 7,
            "sub_lord": ["Venus", "Jupiter", "Mercury", "Moon"]
        },
        interpretation_en="Under Krishnamurti Paddhati (KP), when the 7th cuspal sub-lord is a benefic planet (Venus, Jupiter, Mercury, Moon) and positively signifies houses 2 (family), 7 (union), or 11 (fulfillment), the natal promise of fruitful marriage is strongly validated.",
        interpretation_ta="கே.பி ஜோதிட முறைப்படி 7-ஆம் பாவத்தின் உப-அதிபதி சுப கிரகமாக அமைந்து 2 (குடும்பம்), 7 (களத்திரம்), 11 (லாபம்) பாவங்களை தொடர்பு கொள்ளும் போது இனிமையான திருமண வாழ்க்கை உறுதியாகிறது.",
        astrological_principle_en="KP Cuspal Sub-Lord doctrine: The sub-lord of the cusp decides whether the matters of that house will fruitfully materialize.",
        astrological_principle_ta="கே.பி பாவ உப அதிபதி விதி: ஒரு பாவத்தின் ஆரம்ப முனையின் உப அதிபதியே அந்த பாவக பலன் நிறைவேறுமா என்பதை தீர்மானிக்கிறது.",
        source_reference="K.S. Krishnamurti, KP Reader II: Fundamental Principles",
        limitations_en="Sub-lord placed in constellation of 6 or 12 house lord creates pre-marital negotiation delays.",
        limitations_ta="உப அதிபதி 6 அல்லது 12-ஆம் அதிபதியின் நட்சத்திரத்தில் நின்றால் திருமண பேச்சுகளில் தாமதம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),
]


class RulesRegistry:
    """In-memory and database-backed rule repository."""

    _rules: Dict[str, AstrologicalRuleDefinition] = {r.rule_id: r for r in INITIAL_RULES_CATALOGUE}

    @classmethod
    def get_all_rules(cls) -> List[AstrologicalRuleDefinition]:
        return list(cls._rules.values())

    @classmethod
    def get_rule_by_id(cls, rule_id: str) -> Optional[AstrologicalRuleDefinition]:
        return cls._rules.get(rule_id)

    @classmethod
    def get_rules_for_category(cls, category_slug: str, subcategory: Optional[str] = None) -> List[AstrologicalRuleDefinition]:
        res = []
        for r in cls._rules.values():
            if not r.is_enabled:
                continue
            if r.category_slug == category_slug:
                if subcategory and r.subcategory and r.subcategory != subcategory:
                    continue
                res.append(r)
        return res

    @classmethod
    def register_rule(cls, rule: AstrologicalRuleDefinition) -> None:
        cls._rules[rule.rule_id] = rule

    @classmethod
    def count(cls) -> int:
        return len(cls._rules)
