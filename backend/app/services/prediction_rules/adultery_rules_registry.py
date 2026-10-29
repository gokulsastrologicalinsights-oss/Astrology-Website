"""Classical Adultery, Extramarital Relations, and Stri Jataka Rules Register.

Contains:
1. 33 Yogas from Jataka Tatva on unconventional relations, extra-marital affairs,
   and physical intimacy combinations.
2. Stri Jataka (Brihat Jataka Ch. 20) rules on female horoscopy, marital discord,
   7th house afflictions, and Navamsa Venus-Mars Parivartana.

Ethical & Academic Note:
These classical aphorisms are preserved purely for scholarly astrological research and
comparative canon verification. Traditional texts used stark terminology; these indicators
represent astrological heuristics and must never be used to make dogmatic moral or character
judgments about an individual or their spouse.
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

JT_DISCLAIMER_EN = (
    "Classical textual heuristic from Jataka Tatva recorded for astrological research. "
    "Traditional aphorisms must be interpreted with academic objectivity, counter-balancing "
    "benefic aspects (Jupiter/Venus), and cultural context rather than definitive character judgment."
)
JT_DISCLAIMER_TA = (
    "ஜாதக தத்துவம் நூலின் பாரம்பரிய ஆய்வுக் குறிப்பு. இத்தகைய அமைப்புகள் வெறும் பொதுவான நூற் கூற்றுகளே அன்றி, "
    "குரு அல்லது சுக்கிரனின் சுபப் பார்வைகள் மூலம் மாறும்; தனிப்பட்ட ஒழுக்கம் அல்லது விசுவாசத்தை உறுதியாகத் தீர்மானிக்காது."
)

BJ_DISCLAIMER_EN = (
    "Classical rule from Varahamihira's Brihat Jataka (Stri Jataka Adhyaya). "
    "In ancient horoscopy, 7th house afflictions were framed in traditional terms. "
    "Modern evaluation requires synthesizing overall chart dignity, 9th/4th house strength, and benefic mitigations."
)
BJ_DISCLAIMER_TA = (
    "வராகமிஹிரரின் பிருஹத் ஜாதகம் (ஸ்திரீ ஜாதக அத்தியாயம்) வழியிலான பாரம்பரிய விதி. "
    "7-ஆம் பாவத்தின் பாதிப்புகள் மட்டுமே விவாகரத்து, விதவைத்தன்மை அல்லது பாலியல் நடத்தையை தீர்மானிக்காது; "
    "முழுமையான லக்ன மற்றும் குருவின் சுப பலன்களைக் கொண்டு ஆராய வேண்டும்."
)

JATAKA_TATVA_33_ADULTERY_RULES: List[AstrologicalRuleDefinition] = [
    # Yoga 1
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-01",
        name_en="Jataka Tatva Yoga 1 - Venus & Mercury in 7th, 8th, or 10th House",
        name_ta="ஜாதக தத்துவம் யோகம் 1 - 7, 8 அல்லது 10-ல் சுக்கிரன் மற்றும் புதன்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus and Mercury co-occupying the 7th, 8th, or 10th house creates heightened sensual curiosity, romantic flair, and attraction toward unconventional or extramarital intimacy.",
        interpretation_ta="சுக்கிரன் மற்றும் புதன் ஆகிய இரு கிரகங்களும் 7, 8 அல்லது 10-ஆம் வீடுகளில் அமைவது அதீத காம நாட்டம், காதல் ஈர்ப்பு மற்றும் திருமணத்திற்கு வெளியேயான உறவுகளில் நாட்டத்தை ஏற்படுத்தலாம்.",
        astrological_principle_en="Jataka Tatva, Sutra 1: 'If Venus and Mercury are in the 7th, 8th, or 10th house, the native engages in connections outside marriage.'",
        astrological_principle_ta="சுக்கிரன் மற்றும் புதன் 7, 8 அல்லது 10-ஆம் வீடுகளில் இணைவது காம வேட்கை மற்றும் மாற்று உறவு நாட்டத்தைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 1",
        severity=SeverityLevel.MIXED,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": [7, 8, 10], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Mercury", "house": [7, 8, 10], "chart": "d1"}
            ]
        }
    ),

    # Yoga 2
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-02",
        name_en="Jataka Tatva Yoga 2 - Venus in 10th & Mars in 7th (Mars Aspecting Venus)",
        name_ta="ஜாதக தத்துவம் யோகம் 2 - 10-ல் சுக்கிரன் & 7-ல் செவ்வாய் (செவ்வாய் பார்வை)",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus placed in the 10th house with Mars in the 7th house subjects the planet of passion (Venus) to Mars's 4th special aspect, firing up aggressive, uninhibited romantic pursuits outside wedlock.",
        interpretation_ta="10-ஆம் வீட்டில் சுக்கிரன் அமைந்து 7-ஆம் வீட்டில் செவ்வாய் அமைந்தால், செவ்வாயின் 4-ஆம் பார்வை சுக்கிரன் மீது விழுந்து தீவிர பாலியல் உணர்ச்சியையும் ரகசிய ஈர்ப்பையும் உருவாக்குகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 2: 'Venus in 10th and Mars in 7th with Mars casting aspect upon Venus associates with extramarital alliances.'",
        astrological_principle_ta="10-ல் சுக்கிரன், 7-ல் செவ்வாய் அமைவது செவ்வாயின் பார்வை மூலம் பாலியல் வேட்கையைத் தூண்டுகிறது.",
        source_reference="Jataka Tatva - Sutra 2",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": 10, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"}
            ]
        }
    ),

    # Yoga 3
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-03",
        name_en="Jataka Tatva Yoga 3 - Venus & Mars Connected to 4th & 10th Lords",
        name_ta="ஜாதக தத்துவம் யோகம் 3 - 4 மற்றும் 10-ஆம் அதிபதிகளுடன் சுக்கிரன்-செவ்வாய் தொடர்பு",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Connection between 4th lord (domestic peace/chastity) and 10th lord involving Venus and Mars disrupts conventional domestic satisfaction, favoring passionate external adventures.",
        interpretation_ta="4-ஆம் அதிபதியும் 10-ஆம் அதிபதியும் சுக்கிரன்-செவ்வாய் காரகத்துவத்துடன் தொடர்பு கொள்வது குடும்பத்திற்கு வெளியேயான பாலியல் நாட்டத்தை உருவாக்குகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 3: 'Lords of 4th and 10th house associated with Venus and Mars denotes intense passion beyond conventional bonds.'",
        astrological_principle_ta="4 மற்றும் 10-ஆம் அதிபதிகளுடன் சுக்கிரன்-செவ்வாய் சேர்க்கை அல்லது தொடர்பு காம நாட்டத்தைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 3",
        severity=SeverityLevel.MIXED,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Mars"], "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 4, "placed_in_house": [4, 10], "chart": "d1"}
            ]
        }
    ),

    # Yoga 4
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-04",
        name_en="Jataka Tatva Yoga 4 - Venus in 10th from Moon, Saturn in 10th from Venus",
        name_ta="ஜாதக தத்துவம் யோகம் 4 - சந்திரனிலிருந்து 10-ல் சுக்கிரன், அங்கிருந்து 10-ல் சனி",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus occupying the 10th from the Moon while Saturn occupies the 10th from Venus creates emotional coldness toward legitimate partners alongside clandestine sensual relationships.",
        interpretation_ta="சந்திரனிலிருந்து 10-ஆம் வீட்டில் சுக்கிரன் அமைந்து, அங்கிருந்து 10-ஆம் வீட்டில் சனி அமைவது கட்டுப்பாடற்ற அல்லது ரகசிய பாலியல் தொடர்புகளைக் குறிக்கிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 4: 'Venus in 10th from Moon and Saturn in 10th from Venus denotes unregulated sexual behavior.'",
        astrological_principle_ta="சந்திரனிலிருந்து 10-ல் சுக்கிரன் மற்றும் சுக்கிரனிலிருந்து 10-ல் சனி பாலியல் கட்டுப்பாடின்மையைக் குறிக்கிறது.",
        source_reference="Jataka Tatva - Sutra 4",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": [4, 10], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Saturn", "house": [1, 7], "chart": "d1"}
            ]
        }
    ),

    # Yoga 5
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-05",
        name_en="Jataka Tatva Yoga 5 - Venus, Mercury & Saturn in Venus's Sign in 7th/10th",
        name_ta="ஜாதக தத்துவம் யோகம் 5 - சுக்கிரன் ராசியில் 7 அல்லது 10-ல் சுக்கிரன், புதன், சனி",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Conjunction of Venus, Mercury, and Saturn in Taurus or Libra situated in the 7th or 10th house produces highly unconventional, pleasure-seeking lifestyle with disregard for societal norms.",
        interpretation_ta="சுக்கிரனுக்குரிய ரிஷபம் அல்லது துலாமில், 7 அல்லது 10-ஆம் இடத்தில் சுக்கிரன், புதன் மற்றும் சனி இணைந்திருப்பது கட்டுப்பாடற்ற அல்லது நெறிமீறிய உறவு நடத்தையைக் குறிக்கும்.",
        astrological_principle_en="Jataka Tatva, Sutra 5: 'Venus, Mercury, and Saturn in 7th or 10th house in a sign of Venus causes uninhibited sexual lifestyle.'",
        astrological_principle_ta="சுக்கிரனின் ராசியில் 7 அல்லது 10-ல் சுக்கிரன், புதன், சனி இணைவது ஒழுக்கக் கட்டுப்பாடற்ற நடத்தையைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 5",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": [7, 10], "chart": "d1"},
                {"condition_type": "planet_sign", "planet": "Venus", "sign": [2, 7], "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Mercury", "Saturn"], "chart": "d1"}
            ]
        }
    ),

    # Yoga 6
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-06",
        name_en="Jataka Tatva Yoga 6 - 6th Lord in Dusthana (6th, 8th, or 12th House)",
        name_ta="ஜாதக தத்துவம் யோகம் 6 - 6-ஆம் அதிபதி 6, 8 அல்லது 12-ஆம் துஷ்டானத்தில்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="6th lord placed in a Dusthana (6, 8, or 12) triggers Vipareeta Harsha Yoga, but classically associates with secret alliances, contentious infatuations, and extra-marital escapades.",
        interpretation_ta="6-ஆம் வீட்டின் அதிபதி 6, 8 அல்லது 12 போன்ற துஷ்டானங்களில் அமைவது மறைமுக அல்லது திருமணத்திற்கு வெளியேயான உறவுச் சிக்கல்களுடன் பாரம்பரியமாகத் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 6: 'Lord of the 6th house placed in any Dusthana (6th, 8th, or 12th) associates with extramarital relationships.'",
        astrological_principle_ta="6-ஆம் அதிபதி துஷ்டானத்தில் அமைவது ரகசிய உறவு நாட்டத்தை ஏற்படுத்தும்.",
        source_reference="Jataka Tatva - Sutra 6",
        severity=SeverityLevel.NEUTRAL,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 6,
            "placed_in_house": [6, 8, 12],
            "chart": "d1"
        }
    ),

    # Yoga 7
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-07",
        name_en="Jataka Tatva Yoga 7 - 2nd, 7th & 10th Lords Combined in 10th House",
        name_ta="ஜாதக தத்துவம் யோகம் 7 - 2, 7 மற்றும் 10-ஆம் அதிபதிகள் 10-ல் இணைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="When the lords of family wealth (2nd), marriage (7th), and public karma (10th) all congregate in the 10th house, professional and romantic spheres intertwine, fostering public liaisons.",
        interpretation_ta="2, 7 மற்றும் 10-ஆம் வீடுகளின் அதிபதிகள் மூவரும் 10-ஆம் வீட்டில் அமைவது திருமணத்திற்கு வெளியேயான உறவுகள் அல்லது தொழில் ரீதியான ஈர்ப்புகளுடன் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 7: 'Lords of 2nd, 7th, and 10th houses positioned together in the 10th house indicates outside relationships.'",
        astrological_principle_ta="2, 7, 10-ஆம் அதிபதிகள் பத்தாம் பாவத்தில் இணைவது திருமணத்திற்கு வெளியேயான உறவைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 7",
        severity=SeverityLevel.MIXED,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 2, "placed_in_house": 10, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 10, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 10, "placed_in_house": 10, "chart": "d1"}
            ]
        }
    ),

    # Yoga 8
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-08",
        name_en="Jataka Tatva Yoga 8 - 7th Lord with Rahu/Ketu & Malefic Affliction",
        name_ta="ஜாதக தத்துவம் யோகம் 8 - 7-ஆம் அதிபதி ராகு/கேதுவுடன் இணைந்து பாவ பார்வை பெறுதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 7th lord conjoined with the nodal axis (Rahu or Ketu) under malefic aspect distorts orthodox marital bonding, fostering obsessive extramarital entanglements.",
        interpretation_ta="7-ஆம் வீட்டின் அதிபதி ராகு அல்லது கேதுவுடன் இணைந்து, பாவ கிரகத்தின் பார்வையைப் பெறுவது கட்டுப்பாடற்ற அல்லது ரகசிய உறவுப் பழக்கத்தைக் குறிக்கும்.",
        astrological_principle_en="Jataka Tatva, Sutra 8: '7th lord combined with Rahu or Ketu and aspected by a malefic denotes uninhibited relationship patterns.'",
        astrological_principle_ta="7-ஆம் அதிபதி ராகு-கேதுவுடன் இணைந்து பாவ பார்வை பெறுவது கட்டுப்பாடற்ற உறவுப் பழக்கத்தைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 8",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Rahu"], "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Ketu"], "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": [6, 8, 12], "chart": "d1"}
            ]
        }
    ),

    # Yoga 9
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-09",
        name_en="Jataka Tatva Yoga 9 - Venus in Mars/Saturn Varga with Malefic Aspect",
        name_ta="ஜாதக தத்துவம் யோகம் 9 - செவ்வாய்/சனி வர்க்கத்தில் சுக்கிரன் & பாவ பார்வை",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus occupying a Martian (Aries/Scorpio) or Saturnian (Capricorn/Aquarius) sign/Varga while receiving aspects from Mars or Saturn intensifies carnal urges and rebellious romantic choices.",
        interpretation_ta="சுக்கிரன் செவ்வாய் அல்லது சனிக்குச் சொந்தமான ராசிகளில் அமைந்து, அவற்றின் பார்வையைப் பெறுவது பாலியல் நடத்தையில் தீவிர நாட்டத்தையும் மரபுமீறிய விருப்பங்களையும் குறிக்கும்.",
        astrological_principle_en="Jataka Tatva, Sutra 9: 'Venus situated in a Varga of Mars or Saturn and aspected by the corresponding planet denotes carnal preoccupation.'",
        astrological_principle_ta="செவ்வாய் அல்லது சனியின் ராசிகளில் சுக்கிரன் இருந்து பார்வை பெறுவது காம நாட்டத்தை அதிகரிக்கும்.",
        source_reference="Jataka Tatva - Sutra 9",
        severity=SeverityLevel.MIXED,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "planet_sign",
            "planet": "Venus",
            "sign": [1, 8, 10, 11],
            "chart": "d1"
        }
    ),

    # Yoga 10
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-10",
        name_en="Jataka Tatva Yoga 10 - Venus & Mars in 12th House / Shayana Sthana",
        name_ta="ஜாதக தத்துவம் யோகம் 10 - 12-ல் சுக்கிரன் மற்றும் செவ்வாய் சேர்க்கை",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus and Mars joining in the 12th house (Shayana Sthana - bedroom pleasures) creates insatiable romantic passion and secret romantic affairs away from the spouse.",
        interpretation_ta="12-ஆம் வீட்டில் சுக்கிரனும் செவ்வாயும் இணைந்திருப்பது சயன சுகத்தில் அதீத ஈடுபாட்டையும், ரகசிய அல்லது திருமணத்திற்கு வெளியேயான உடலுறவு நாட்டத்தையும் உருவாக்குகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 10: 'Venus and Mars in the 12th house (or 12th from Karakamsha) produces intense extramarital sensuality.'",
        astrological_principle_ta="12-ல் சுக்கிரன் மற்றும் செவ்வாய் சேர்க்கை அதீத காம நாட்டத்தைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 10",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Mars"], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Venus", "house": 12, "chart": "d1"}
            ]
        }
    ),

    # Yoga 11
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-11",
        name_en="Jataka Tatva Yoga 11 - Ketu in 9th House / Dharma Sthana",
        name_ta="ஜாதக தத்துவம் யோகம் 11 - 9-ல் கேது அமைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Ketu in the 9th house dislodges traditional religious orthodoxies and dharma, making the native disregard societal marital rules for personal or spiritual romantic exploration.",
        interpretation_ta="9-ஆம் இடத்தில் கேது அமைவது மத மற்றும் சமூக சம்பிரதாயங்களை மீறும் எண்ணத்தை உருவாக்கி, மரபுசாரா உறவு நாட்டத்தை ஏற்படுத்தலாம்.",
        astrological_principle_en="Jataka Tatva, Sutra 11: 'Ketu in the 9th house produces unconventional attitudes toward traditional relationship codes.'",
        astrological_principle_ta="9-ல் கேது பாரம்பரிய மத, ஒழுக்க கட்டுப்பாடுகளை மீறும் தன்மையைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 11",
        severity=SeverityLevel.NEUTRAL,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Ketu",
            "house": 9,
            "chart": "d1"
        }
    ),

    # Yoga 12
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-12",
        name_en="Jataka Tatva Yoga 12 - 2nd Lord Placed in 3rd or 4th House",
        name_ta="ஜாதக தத்துவம் யோகம் 12 - 2-ஆம் அதிபதி 3 அல்லது 4-ஆம் வீட்டில் அமைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="2nd lord (family lineage and fidelity) placed in the 3rd (courage/passions) or 4th (domestic dwelling) predisposes to romantic initiatives outside the primary family bond.",
        interpretation_ta="2-ஆம் வீட்டின் அதிபதி லக்னத்திலிருந்து 3 அல்லது 4-ஆம் வீட்டில் அமைவது குடும்ப எல்லைக்கு அப்பாற்பட்ட உறவு நாட்ட யோகங்களில் பாரம்பரியமாகச் சேர்க்கப்பட்டுள்ளது.",
        astrological_principle_en="Jataka Tatva, Sutra 12: 'Lord of the 2nd house placed in the 3rd or 4th house predisposes to extramarital associations.'",
        astrological_principle_ta="2-ஆம் அதிபதி 3 அல்லது 4-ல் அமைவது குடும்ப பந்தத்திற்கு வெளியேயான ஈர்ப்பைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 12",
        severity=SeverityLevel.NEUTRAL,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 2,
            "placed_in_house": [3, 4],
            "chart": "d1"
        }
    ),

    # Yoga 13
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-13",
        name_en="Jataka Tatva Yoga 13 - 7th Lord in 1st, 2nd, 7th, or 12th House",
        name_ta="ஜாதக தத்துவம் யோகம் 13 - 7-ஆம் அதிபதி 1, 2, 7 அல்லது 12-ல் அமைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 7th lord placed in the 1st (self-centric desire), 2nd (multiplicity of family ties), 7th (hyper-marital focus), or 12th (bed pleasures) brings opportunities for supplementary romantic alliances.",
        interpretation_ta="7-ஆம் வீட்டின் அதிபதி 1, 2, 7 அல்லது 12-ஆம் வீடுகளில் அமைவது திருமணத்திற்கு வெளியேயான அல்லது கூடுதல் காதல் உறவுகளுக்கான வாய்ப்புகளுடன் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 13: '7th lord in 1st or 7th, or in 2nd or 12th house denotes diversified romantic relationships.'",
        astrological_principle_ta="7-ஆம் அதிபதி 1, 2, 7 அல்லது 12-ல் அமைவது பலதரப்பட்ட உறவு வாய்ப்புகளைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 13",
        severity=SeverityLevel.NEUTRAL,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": [1, 2, 7, 12],
            "chart": "d1"
        }
    ),

    # Yoga 14
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-14",
        name_en="Jataka Tatva Yoga 14 - Venus in 7th House in Mars/Saturn Signs",
        name_ta="ஜாதக தத்துவம் யோகம் 14 - 7-ல் சுக்கிரன் செவ்வாய் அல்லது சனியின் ராசிகளில்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus occupying the 7th house in signs ruled by Mars (Aries/Scorpio) or Saturn (Capricorn/Aquarius) creates passionate marital discontent, seeking novelty outside monogamy.",
        interpretation_ta="7-ஆம் வீட்டில் சுக்கிரன் அமைந்து செவ்வாய் அல்லது சனியின் ராசிகளில் இருப்பது உறவுகளில் அதிருப்தியையும் மாற்றுத் தொடர்புகளை நாடும் எண்ணத்தையும் குறிக்கிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 14: 'Venus in 7th in Varga of Mars or Saturn or aspected by them denotes unrestrained romantic inclinations.'",
        astrological_principle_ta="7-ல் சுக்கிரன் செவ்வாய்/சனி ராசியில் இருப்பது தாம்பத்திய அதிருப்தியையும் மாற்று உறவு நாட்டத்தையும் தரும்.",
        source_reference="Jataka Tatva - Sutra 14",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": 7, "chart": "d1"},
                {"condition_type": "planet_sign", "planet": "Venus", "sign": [1, 8, 10, 11], "chart": "d1"}
            ]
        }
    ),

    # Yoga 15
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-15",
        name_en="Jataka Tatva Yoga 15 - Moon, Mars & Saturn Conjoined in 7th House",
        name_ta="ஜாதக தத்துவம் யோகம் 15 - 7-ல் சந்திரன், செவ்வாய் மற்றும் சனி சேர்க்கை",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Conjunction of Moon (mind), Mars (aggression/passion), and Saturn (secrecy/delays) in the 7th house indicates that both the native and partner may seek emotional and carnal fulfillment outside the marriage.",
        interpretation_ta="7-ஆம் வீட்டில் சந்திரன், செவ்வாய் மற்றும் சனி இணைந்திருப்பது ஜாதகரும் அவருடைய வாழ்க்கைத்துணையும் திருமணத்திற்கு வெளியேயான உறவுகளில் ஈடுபடக்கூடும் என்ற பாரம்பரியக் கூற்றைக் குறிக்கிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 15: 'Moon, Mars, and Saturn conjoined in 7th house denotes extra-marital tendencies for both partners.'",
        astrological_principle_ta="7-ல் சந்திரன்-செவ்வாய்-சனி சேர்க்கை இருவரிடமும் தாம்பத்திய விலகலையும் மாற்று உறவையும் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 15",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Moon", "Mars", "Saturn"], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Moon", "house": 7, "chart": "d1"}
            ]
        }
    ),

    # Yoga 16
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-16",
        name_en="Jataka Tatva Yoga 16 - Moon or Venus in Kendra Conjoined with Malefics",
        name_ta="ஜாதக தத்துவம் யோகம் 16 - கேந்திரத்தில் சந்திரன்/சுக்கிரன் பாவ கிரகங்களுடன்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Moon or Venus situated in a Kendra house heavily afflicted by natural malefics (Mars or Saturn) indicates extreme psychological vulnerability and taboo relationship boundaries.",
        interpretation_ta="சந்திரன் அல்லது சுக்கிரன் கேந்திர வீடுகளில் பாவ கிரகங்களுடன் (செவ்வாய் அல்லது சனி) இணைந்திருப்பது உணர்ச்சி ரீதியான தடுமாற்றத்தையும் வரம்புமீறிய பாலியல் ஈர்ப்பையும் குறிக்கும்.",
        astrological_principle_en="Jataka Tatva, Sutra 16: 'Moon or Venus in Kendra connected with malefics indicates boundary-violating relationship patterns.'",
        astrological_principle_ta="கேந்திரத்தில் சந்திரன் அல்லது சுக்கிரன் பாவ கிரகங்களுடன் இணைவது ஒழுக்க வரம்புமீறலைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 16",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Moon", "Saturn"], "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Saturn"], "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Moon", "Mars"], "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Mars"], "chart": "d1"}
            ]
        }
    ),

    # Yoga 17
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-17",
        name_en="Jataka Tatva Yoga 17 - 4th Lord Afflicted in Dusthana without Benefics",
        name_ta="ஜாதக தத்துவம் யோகம் 17 - 4-ஆம் அதிபதி சுப பார்வையின்றி துஷ்டானத்தில்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Affliction to the 4th house/lord (governing heart, mental peace, and motherly respect) by Dusthana placements without Jupiter's glance causes unusual attraction toward older or authoritative partners.",
        interpretation_ta="4-ஆம் வீட்டின் அதிபதி சுபப் பார்வையின்றி 6, 8, அல்லது 12-ல் அமைவது தாய்க்கு நிகரான அல்லது வயதில் மூத்த நபர்களிடம் முறையற்ற உறவு ஏற்படுவதாக மூல நூல் கூறுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 17: '4th lord afflicted without benefic association indicates attraction toward much older maternal figures.'",
        astrological_principle_ta="4-ஆம் அதிபதி சுப தொடர்பின்றி கெடுவது வயதில் மூத்தவர்களிடம் முறையற்ற ஈர்ப்பைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 17",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 4,
            "placed_in_house": [6, 8, 12],
            "chart": "d1"
        }
    ),

    # Yoga 18
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-18",
        name_en="Jataka Tatva Yoga 18 - 7th Lord or Saturn Afflicted in 4th House",
        name_ta="ஜாதக தத்துவம் யோகம் 18 - 4-ஆம் வீட்டில் 7-ஆம் அதிபதி அல்லது சனி",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 7th lord placed in the 4th house (bringing marital desires into the inner domestic sanctuary) or Saturn occupying the 4th house disturbs family boundaries.",
        interpretation_ta="7-ஆம் வீட்டின் அதிபதி 4-ஆம் வீட்டில் அமைவது அல்லது 4-ஆம் வீட்டில் சனி அமர்வது குடும்பத்துக்குள் முறையற்ற உறவுச் சிக்கல்களை ஏற்படுத்தும் என மூலத்தில் கூறப்பட்டுள்ளது.",
        astrological_principle_en="Jataka Tatva, Sutra 18: '7th lord in 4th with malefic or Saturn in 4th house denotes domestic taboo relationships.'",
        astrological_principle_ta="4-ல் 7-ஆம் அதிபதி அல்லது சனி அமைவது குடும்பத்திற்குள் உறவு எல்லை மீறலைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 18",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 4, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Saturn", "house": 4, "chart": "d1"}
            ]
        }
    ),

    # Yoga 19
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-19",
        name_en="Jataka Tatva Yoga 19 - Sun or Mars in 7th House (Fiery Marital Energy)",
        name_ta="ஜாதக தத்துவம் யோகம் 19 - 7-ஆம் வீட்டில் சூரியன் அல்லது செவ்வாய்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Presence of fiery planets (Sun or Mars) in the 7th house brings ego collisions, impulsive sexual encounters, and aggressive intimacy seeking unconventional outlets.",
        interpretation_ta="7-ஆம் வீட்டில் சூரியன் அல்லது செவ்வாய் அமைவது அகந்தை மோதல்களையும், அவசர பாலியல் உறவுகளையும், ஆதிக்க மனப்பான்மையையும் அளிக்கிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 19: 'Sun or Mars in the 7th house produces aggressive carnal urges and unconventional unions.'",
        astrological_principle_ta="7-ல் சூரியன் அல்லது செவ்வாய் அமைவது உக்கிரமான பாலியல் உணர்ச்சியையும் முரட்டுத்தனத்தையும் தரும்.",
        source_reference="Jataka Tatva - Sutra 19",
        severity=SeverityLevel.MIXED,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Sun", "house": 7, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"}
            ]
        }
    ),

    # Yoga 20
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-20",
        name_en="Jataka Tatva Yoga 20 - Venus or Rahu in 7th House (Illusory Passion)",
        name_ta="ஜாதக தத்துவம் யோகம் 20 - 7-ஆம் வீட்டில் சுக்கிரன் அல்லது ராகு",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Venus or Rahu in the 7th house creates intense glamour, romantic fixation, and vulnerability to taboo or unconventional partners.",
        interpretation_ta="7-ஆம் வீட்டில் சுக்கிரன் அல்லது ராகு அமைவது மாயை கலந்த காமக் கவர்ச்சியையும், தடைசெய்யப்பட்ட உறவுகளில் ஈடுபாட்டையும் உருவாக்கும் எனக் கட்டுரை கூறுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 20: 'Venus or Rahu in 7th house indicates unconventional sexual liaisons.'",
        astrological_principle_ta="7-ல் சுக்கிரன் அல்லது ராகு இருப்பது எல்லை கடந்த காமக் கவர்ச்சியையும் ரகசிய உறவையும் தரும்.",
        source_reference="Jataka Tatva - Sutra 20",
        severity=SeverityLevel.MIXED,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": 7, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Rahu", "house": 7, "chart": "d1"}
            ]
        }
    ),

    # Yoga 21
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-21",
        name_en="Jataka Tatva Yoga 21 - Moon Conjoined with Malefic in 9th House",
        name_ta="ஜாதக தத்துவம் யோகம் 21 - 9-ஆம் வீட்டில் சந்திரன் பாவ கிரகத்துடன் இணைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The Moon conjunct a natural malefic (Saturn, Mars, or Rahu) in the 9th house (preceptor/guru house) traditionally signifies attraction toward venerated mentors or mentor figures.",
        interpretation_ta="9-ஆம் வீட்டில் சந்திரன் ஒரு பாவ கிரகத்துடன் இணைந்து அமைவது குரு அல்லது மதிக்கத்தக்க நபர்களின் துணைவியிடம் ஈர்ப்பு ஏற்படும் என்று மூல நூலில் குறிப்பிடப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 21: 'Moon conjoined with a malefic in the 9th house associates with transgressions toward respected mentor figures.'",
        astrological_principle_ta="9-ல் சந்திரன் பாவ கிரகத்துடன் இணைவது குரு ஸ்தானத்தில் உள்ளவர்களிடம் முறையற்ற ஈர்ப்பைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 21",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Moon", "house": 9, "chart": "d1"},
                {
                    "condition_type": "compound",
                    "operator": "OR",
                    "conditions": [
                        {"condition_type": "planet_conjunction", "planets": ["Moon", "Saturn"], "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Moon", "Mars"], "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Moon", "Rahu"], "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Yoga 22
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-22",
        name_en="Jataka Tatva Yoga 22 - Moon Placed Alone in 9th House",
        name_ta="ஜாதக தத்துவம் யோகம் 22 - 9-ஆம் வீட்டில் சந்திரன் அமைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Moon in the 9th house bestows a philosophical mind, but classical aphorisms note emotional bonding with partners significantly older or possessing mature authority.",
        interpretation_ta="9-ஆம் வீட்டில் சந்திரன் அமைவது ஆன்மீக நாட்டத்தைத் தந்தாலும், பாரம்பரிய ஜோதிடத்தில் வயதில் மூத்த பெண்களுடன் காதல் உறவு ஏற்படும் அமைப்பாகக் குறிப்பிடப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 22: 'Moon in the 9th house denotes romantic attachments with older partners.'",
        astrological_principle_ta="9-ல் சந்திரன் அமைவது வயதில் மூத்தவர்களிடம் அன்பும் ஈர்ப்பும் கொள்ளும் அமைப்பைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 22",
        severity=SeverityLevel.NEUTRAL,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Moon",
            "house": 9,
            "chart": "d1"
        }
    ),

    # Yoga 23
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-23",
        name_en="Jataka Tatva Yoga 23 - 9th Lord Afflicted or in Dusthana",
        name_ta="ஜாதக தத்துவம் யோகம் 23 - 9-ஆம் அதிபதி நீசம் அல்லது துஷ்டானத்தில் அமைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 9th lord in debilitation or occupying a Dusthana weakens internal dharmic restraint, opening pathways to taboo affairs and disregard for religious codes.",
        interpretation_ta="9-ஆம் வீட்டின் அதிபதி நீசம் அடைவது அல்லது துஷ்டானத்தில் இருப்பது தார்மீகக் கட்டுப்பாடுகளைத் தளர்த்தி, குடும்பத்திற்குப் புறம்பான முறையற்ற உறவுகளுக்கு வழிகோலும்.",
        astrological_principle_en="Jataka Tatva, Sutra 23: 'Debilitated 9th lord indicates moral laxity in romantic relationships.'",
        astrological_principle_ta="9-ஆம் அதிபதி பலவீனமடைவது நெறிமுறைகளில் தளர்வையும் முறையற்ற உறவையும் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 23",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 9,
            "placed_in_house": [6, 8, 12],
            "chart": "d1"
        }
    ),

    # Yoga 24
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-24",
        name_en="Jataka Tatva Yoga 24 - Lagna Lord & 6th Lord Mutual Affliction",
        name_ta="ஜாதக தத்துவம் யோகம் 24 - லக்னாதிபதியும் 6-ஆம் அதிபதியும் பாவ தொடர்புடன் இணைதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Lagna lord and 6th lord conjoined with malefics draws the personality toward conflict, litigations, and contentious love affairs that disrupt social standing.",
        interpretation_ta="லக்னாதிபதியும் 6-ஆம் வீட்டின் அதிபதியும் பாவ கிரகங்களுடன் இணைவது వివాதங்கள், ரகசிய சச்சரவுகள் மற்றும் திருமணத்திற்கு வெளியேயான உறவுகளுடன் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 24: 'Lagna lord and 6th lord afflicted by malefics associates with scandalous romantic alliances.'",
        astrological_principle_ta="லக்னாதிபதி மற்றும் 6-ஆம் அதிபதி பாவ கிரக தொடர்புடன் இணைவது சர்ச்சை உறவுகளைத் தரும்.",
        source_reference="Jataka Tatva - Sutra 24",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 1, "placed_in_house": [6, 8, 12], "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 6, "placed_in_house": [1, 6, 7, 8], "chart": "d1"}
            ]
        }
    ),

    # Yoga 25
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-25",
        name_en="Jataka Tatva Yoga 25 - Waning Moon with Malefic in 7th / 8th & 9th Lords Conjoined",
        name_ta="ஜாதக தத்துவம் யோகம் 25 - 7-ல் தேய்பிறைச் சந்திரன் & பாவ கிரகம் / 8, 9 அதிபதிகள் சேர்க்கை",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Waning Moon with a malefic in the 7th house, or conjunction of 8th and 9th lords, creates disillusionment in conventional marriage and secret emotional pursuits.",
        interpretation_ta="தேய்பிறைச் சந்திரன் பாவ கிரகத்துடன் 7-ல் அமைதல் அல்லது 8 மற்றும் 9-ஆம் அதிபதிகள் ஒன்றாக இணைவது திருமண வாழ்வில் அதிருப்தியையும் ரகசிய உறவையும் குறிக்கும்.",
        astrological_principle_en="Jataka Tatva, Sutra 25: 'Waning Moon in 7th with malefic or 8th/9th lords conjoined indicates marital infidelity.'",
        astrological_principle_ta="7-ல் தேய்பிறை சந்திரன்-பாவ கிரகம் அல்லது 8-9 அதிபதிகள் சேர்க்கை மாற்று உறவு நாட்டம் தரும்.",
        source_reference="Jataka Tatva - Sutra 25",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Moon", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Moon", "Saturn"], "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "house_lord_placement", "house": 8, "placed_in_house": [8, 9], "chart": "d1"},
                        {"condition_type": "house_lord_placement", "house": 9, "placed_in_house": [8, 9], "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Yoga 26
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-26",
        name_en="Jataka Tatva Yoga 26 - Mercury in 7th or 7th Lord with Malefics in Dusthana",
        name_ta="ஜாதக தத்துவம் யோகம் 26 - 7-ல் புதன் அல்லது 7-ஆம் அதிபதி பாவ கிரகத்துடன் துஷ்டானத்தில்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Mercury in the 7th house (producing dual or fickle romantic curiosity) or 7th lord afflicted in a Dusthana produces multiple parallel partnerships.",
        interpretation_ta="புதன் 7-ஆம் வீட்டில் அமைவது அல்லது 7-ஆம் அதிபதி பாவ கிரகங்களுடன் இணைந்து துஷ்டானத்தில் இருப்பது பலதரப்பட்ட காதல் அல்லது மாற்று உறவுகளைத் தரும்.",
        astrological_principle_en="Jataka Tatva, Sutra 26: 'Mercury in 7th or afflicted 7th lord in Dusthana denotes duality in relationships.'",
        astrological_principle_ta="7-ல் புதன் அல்லது 7-ஆம் அதிபதி துஷ்டானத்தில் அமைவது இரட்டை உறவு நாட்டத்தைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 26",
        severity=SeverityLevel.MIXED,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Mercury", "house": 7, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": [6, 8, 12], "chart": "d1"}
            ]
        }
    ),

    # Yoga 27
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-27",
        name_en="Jataka Tatva Yoga 27 - Malefics Occupying Three Kendra Angles (1, 4, 7, 10)",
        name_ta="ஜாதக தத்துவம் யோகம் 27 - நான்கு கேந்திரங்களில் மூன்றில் பாவ கிரகங்கள்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Natural malefics occupying three of the four Kendras (Sarpa/Dalpa Yoga variants) causes unrestrained passions, intense rebel spirit, and defiance of domestic restrictions.",
        interpretation_ta="நான்கு கேந்திர வீடுகளில் (1, 4, 7, 10) மூன்று வீடுகளில் பாவ கிரகங்கள் அமைவது கட்டுப்பாடற்ற அல்லது மிகையான பாலியல் நடத்தையைக் குறிக்கும் என்று ஆசிரியர் குறிப்பிடுகிறார்.",
        astrological_principle_en="Jataka Tatva, Sutra 27: 'Malefics in 3 Kendras denotes hyper-sexual vitality and rejection of social conventions.'",
        astrological_principle_ta="கேந்திரங்களில் பாவ கிரகங்கள் நிறைவது அதீத காம நாட்டத்தையும் சமூக கட்டுப்பாடுகளை மீறும் தன்மையையும் தரும்.",
        source_reference="Jataka Tatva - Sutra 27",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Saturn", "house": [1, 4, 7, 10], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mars", "house": [1, 4, 7, 10], "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Rahu", "house": [1, 4, 7, 10], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Saturn", "house": [1, 4, 7, 10], "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Yoga 28
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-28",
        name_en="Jataka Tatva Yoga 28 - Strong Navamsa Dispositor of 7th Lord (Multiple Partners)",
        name_ta="ஜாதக தத்துவம் யோகம் 28 - 7-ஆம் அதிபதியின் நவாம்ச அதிபதி சுப பலம் பெறுதல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D9,
        calculation_mode="thirukanitha",
        interpretation_en="When the Navamsa dispositor of the 7th lord is exceptionally endowed with benefic strength (Parvatamsa or high Varga bala), the native attracts immense romantic popularity and multiple female partners.",
        interpretation_ta="7-ஆம் வீட்டின் அதிபதி நின்ற நவாம்ச ராசியின் அதிபதி சுப பலம் பெற்று வலிமையாக இருந்தால் பல பெண்களின் தொடர்பு அல்லது ஈர்ப்பு ஏற்படும் எனக் கூறப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 28: 'Navamsa lord of 7th lord endowed with high Varga bala indicates associations with many women.'",
        astrological_principle_ta="7-ஆம் அதிபதியின் நவாம்ச அதிபதி சுப பலம் பெறுவது பல பெண்களின் கவர்ச்சியையும் தொடர்பையும் தரும்.",
        source_reference="Jataka Tatva - Sutra 28",
        severity=SeverityLevel.MIXED,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": [1, 4, 5, 7, 9, 10, 11],
            "chart": "d9"
        }
    ),

    # Yoga 29
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-29",
        name_en="Jataka Tatva Yoga 29 - Partner Unfaithfulness & Secret Liaisons Indicators",
        name_ta="ஜாதக தத்துவம் யோகம் 29 - வாழ்க்கைத்துணையின் விசுவாசமின்மை / ரகசிய உறவு யோகம்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="8th lord in the 8th house, or Venus heavily afflicted by Mars/Saturn while malefics flank the 2nd and 12th houses (Papakarthari), classically denotes infidelity or secret parallel lives of the partner.",
        interpretation_ta="8-ஆம் வீட்டின் அதிபதி 8-லேயே அமைதல் அல்லது சுக்கிரன் செவ்வாய்-சனி-ராகுவுடன் இணைந்து 2 மற்றும் 12-ல் பாவ கிரகங்கள் இருப்பது வாழ்க்கைத்துணையின் விசுவாசமின்மையைக் குறிக்கும் என ஆசிரியர் கூறுகிறார்.",
        astrological_principle_en="Jataka Tatva, Sutra 29: '8th lord in 8th or afflicted Venus in Papakarthari associates with partner's unfaithfulness.'",
        astrological_principle_ta="8-ஆம் அதிபதி 8-ல் இருத்தல் அல்லது சுக்கிரன் பாவ கர்த்தாரி யோகத்தில் இருப்பது துணையின் ரகசிய தொடர்பைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 29",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="male",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 8, "placed_in_house": 8, "chart": "d1"},
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Venus", "house": [6, 8, 12], "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Venus", "Mars"], "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Yoga 30
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-30",
        name_en="Jataka Tatva Yoga 30 - Rahu & Saturn Conjoined in Lagna (1st House)",
        name_ta="ஜாதக தத்துவம் யோகம் 30 - லக்னத்தில் ராகு மற்றும் சனி இணைந்திருத்தல்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Rahu and Saturn combining in the Ascendant generates intense unconventionality, rebellion against marital fidelity, and secret extramarital escapades.",
        interpretation_ta="லக்னத்தில் ராகு மற்றும் சனி இணைந்திருப்பது பெண்களின் அல்லது ஆண்களின் திருமணத்திற்கு வெளியேயான ரகசிய உறவுகளுடன் பாரம்பரியமாகத் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 30: 'Rahu and Saturn in Lagna indicates unconventional relationship practices.'",
        astrological_principle_ta="லக்னத்தில் ராகு-சனி சேர்க்கை மரபு மீறிய திருமணத்திற்கு வெளியேயான உறவைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 30",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_conjunction", "planets": ["Rahu", "Saturn"], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Rahu", "house": 1, "chart": "d1"}
            ]
        }
    ),

    # Yoga 31
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-31",
        name_en="Jataka Tatva Yoga 31 - 7th Lord with Rahu in Lagna / 10th House Malefics",
        name_ta="ஜாதக தத்துவம் யோகம் 31 - லக்னத்தில் 7-ஆம் அதிபதி & ராகு / 10-ல் பாவ கிரகங்கள்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 7th lord placed with Rahu in the 1st house or malefics placed in the 10th without benefic aspect indicates extramarital births or raising children born outside traditional marriage.",
        interpretation_ta="7-ஆம் வீட்டின் அதிபதி ராகுவுடன் லக்னத்தில் அமைதல் அல்லது 10-ல் பாவ கிரகங்கள் அமைவது திருமணத்திற்கு வெளியேயான உறவின் மூலம் குழந்தை பெறுதல் போன்ற அமைப்புகளுடன் பாரம்பரிய நூலில் கூறப்பட்டுள்ளது.",
        astrological_principle_en="Jataka Tatva, Sutra 31: '7th lord with Rahu in Lagna or 10th house malefics denotes extramarital progeny.'",
        astrological_principle_ta="லக்னத்தில் 7-ஆம் அதிபதி-ராகு அல்லது 10-ல் பாவ கிரகங்கள் திருமணத்திற்கு வெளியேயான உறவு வழியிலான அமைப்பைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 31",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Rahu", "house": 1, "chart": "d1"},
                        {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 1, "chart": "d1"}
                    ]
                },
                {"condition_type": "planet_house", "planet": "Rahu", "house": 10, "chart": "d1"},
                {"condition_type": "planet_conjunction", "planets": ["Venus", "Mars"], "chart": "d1"}
            ]
        }
    ),

    # Yoga 32
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-32",
        name_en="Jataka Tatva Yoga 32 - 5th or 7th Lord Associated with 6th Lord without Benefics",
        name_ta="ஜாதக தத்துவம் யோகம் 32 - 5 அல்லது 7-ஆம் அதிபதி 6-ஆம் அதிபதியுடன் தொடர்பு",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="In female charts, the 5th (children/romance) or 7th (marriage) lord linked to the 6th lord (conflict/unconventionality) devoid of benefic aspect brings unconventional unions and external alliances.",
        interpretation_ta="பெண்களின் ஜாதகத்தில் 5 அல்லது 7-ஆம் வீட்டின் அதிபதி 6-ஆம் வீட்டின் அதிபதியுடன் தொடர்பு பெற்று சுபப் பார்வையின்றி இருப்பது திருமணத்திற்கு வெளியேயான உறவுகளுடன் பாரம்பரியமாகத் தொடர்புபடுத்தப்படுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 32: '5th or 7th lord linked to 6th lord indicates unconventional unions and extramarital offspring in female horoscopy.'",
        astrological_principle_ta="5 அல்லது 7-ஆம் அதிபதி 6-ஆம் அதிபதியுடன் இணைவது பெண் ஜாதகத்தில் எல்லை மீறிய உறவு நாட்டத்தைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 32",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="female",
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": [6, 8], "chart": "d1"},
                        {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": [6, 8], "chart": "d1"}
                    ]
                },
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 2, "chart": "d1"}
            ]
        }
    ),

    # Yoga 33
    AstrologicalRuleDefinition(
        rule_id="RULE-JT-ADULT-33",
        name_en="Jataka Tatva Yoga 33 - 6th & 8th Lords with Moon & Mars in 4th House",
        name_ta="ஜாதக தத்துவம் யோகம் 33 - 4-ல் சந்திரன் மற்றும் செவ்வாயுடன் 6, 8-ஆம் அதிபதிகள்",
        category_slug="sexuality_intimacy",
        subcategory="classical_adultery_unions",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The 6th and 8th lords combining with Moon and Mars in the 4th house (maternal house/matru sthana) or Venus-Mars in Saturn's signs reflects maternal relationship disruptions or secret domestic heritage.",
        interpretation_ta="6 மற்றும் 8-ஆம் வீட்டின் அதிபதிகள் சந்திரன் மற்றும் செவ்வாயுடன் இணைந்து 4-ஆம் வீட்டில் அமைவது தாயாரின் ரகசிய அல்லது மாற்று உறவுகளைக் குறிக்கும் என மூல நூல் குறிப்பிடுகிறது.",
        astrological_principle_en="Jataka Tatva, Sutra 33: '6th and 8th lords with Moon and Mars in 4th house indicates maternal extramarital relations.'",
        astrological_principle_ta="4-ல் சந்திரன்-செவ்வாயுடன் 6, 8-ஆம் அதிபதிகள் இணைவது தாயாரின் மாற்று உறவு அமைப்பைக் குறிக்கும்.",
        source_reference="Jataka Tatva - Sutra 33",
        severity=SeverityLevel.UNFAVORABLE,
        limitations_en=JT_DISCLAIMER_EN,
        limitations_ta=JT_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Moon", "house": 4, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mars", "house": 4, "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Venus", "sign": [10, 11], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Mars", "sign": [10, 11], "chart": "d1"}
                    ]
                }
            ]
        }
    ),
]

BRIHAT_JATAKA_STRI_RULES: List[AstrologicalRuleDefinition] = [
    # Stri Jataka Rule 1
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-01",
        name_en="Brihat Jataka Stri 1 - Multiple Malefics in 7th House (Marital Distress)",
        name_ta="பிருஹத் ஜாதகம் ஸ்திரீ 1 - 7-ஆம் வீட்டில் பல பாவ கிரகங்கள் (தாம்பத்தியப் பிரிவு)",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Multiple natural malefics (Mars, Saturn, Sun, Rahu) placed in the 7th house without Jupiter's soothing aspect indicates severe distress in early marriage, separation, or early loss of partner as cited by Varahamihira.",
        interpretation_ta="செவ்வாய், சனி போன்ற பல பாவ கிரகங்கள் 7-ஆம் வீட்டில் அமைந்தால், பெண் இளம் வயதில் கணவனை இழக்கக்கூடும் அல்லது மிகக் கடுமையான தாம்பத்தியப் பிரிவைச் சந்திக்க நேரிடும் என பிருஹத் ஜாதகம் கூறுகிறது.",
        astrological_principle_en="Brihat Jataka, Stri Jataka Adhyaya, Verse 1: 'Multiple malefics in the 7th house indicates early widowhood or severe marital disruption.'",
        astrological_principle_ta="7-ஆம் பாவத்தில் பல பாவ கிரகங்கள் அமைவது கணவனை இழத்தல் அல்லது கடுமையான தாம்பத்திய முறிவை ஏற்படுத்தும்.",
        source_reference="Brihat Jataka, Ch. 20 (Stri Jataka), Verse 1",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Saturn", "house": 7, "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Sun", "house": 7, "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Saturn", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Rahu", "house": 7, "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Stri Jataka Rule 2
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-02",
        name_en="Brihat Jataka Stri 2 - Benefic & Malefic Both Occupying 7th House (Remarriage)",
        name_ta="பிருஹத் ஜாதகம் ஸ்திரீ 2 - 7-ஆம் வீட்டில் சுப மற்றும் பாவ கிரகங்கள் இணைதல் (மறுமணம்)",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="When both a benefic (Jupiter, Venus, or Mercury) and a malefic (Mars, Saturn, or Rahu) occupy the 7th house, the first marital alliance faces breakdown, followed by a successful second marriage.",
        interpretation_ta="7-ஆம் வீட்டில் சுப மற்றும் பாவ கிரகங்கள் இணைந்து காணப்பட்டால், முதல் திருமணம் முறிந்து இரண்டாவது திருமணம் ஏற்படும் என வராகமிஹிரர் விளக்குகிறார்.",
        astrological_principle_en="Brihat Jataka, Stri Jataka Adhyaya, Verse 2: 'Mixture of benefic and malefic in the 7th house brings a second marriage.'",
        astrological_principle_ta="7-ஆம் வீட்டில் சுப-அசுப கிரகங்கள் இணைவது மறுமணம் அல்லது இரண்டாவது திருமண யோகத்தை அளிக்கும்.",
        source_reference="Brihat Jataka, Ch. 20 (Stri Jataka), Verse 2",
        severity=SeverityLevel.MIXED,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Jupiter", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Saturn", "house": 7, "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Venus", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"}
                    ]
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Mercury", "house": 7, "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"}
                    ]
                }
            ]
        }
    ),

    # Stri Jataka Rule 3
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-03",
        name_en="Brihat Jataka Stri 3 - Strong Malefic in 7th with Benefic Aspect (Separation & Self-Reliance)",
        name_ta="பிருஹத் ஜாதகம் ஸ்திரீ 3 - 7-ல் வலிமையான பாவ கிரகம் சுபப் பார்வையுடன் (பிரிவு)",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="A strong malefic occupying the 7th house that receives the aspect of a benefic indicates the husband abandoning the marriage or marital estrangement, leading the native to build an autonomous life.",
        interpretation_ta="வலிமையான பாவ கிரகம் 7-ஆம் வீட்டில் இருந்து சுப கிரகத்தின் பார்வையைப் பெற்றால், கணவன் மனைவியைப் பிரியக்கூடும் அல்லது தன்னிச்சையான தனி வாழ்க்கையை வாழ நேரிடும்.",
        astrological_principle_en="Brihat Jataka, Stri Jataka Adhyaya, Verse 3: 'Strong malefic in 7th aspected by benefic indicates separation and subsequent independent living.'",
        astrological_principle_ta="7-ல் வலிமையான பாவ கிரகம் சுப பார்வை பெறுவது பிரிவையும் பின்னர் சுயமாக வாழும் நிலையையும் தரும்.",
        source_reference="Brihat Jataka, Ch. 20 (Stri Jataka), Verse 3",
        severity=SeverityLevel.MIXED,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Saturn", "house": 7, "chart": "d1"},
                {"condition_type": "planet_aspect", "aspecting_planet": "Jupiter", "target_type": "house", "target_value": 7, "chart": "d1"}
            ]
        }
    ),

    # Stri Jataka Rule 4 (Navamsa Venus-Mars Parivartana)
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-04",
        name_en="Brihat Jataka Stri 4 - Navamsa Venus-Mars Mutual Sign Exchange (Passionate Autonomy)",
        name_ta="பிருஹத் ஜாதகம் ஸ்திரீ 4 - நவாம்சத்தில் சுக்கிரன்–செவ்வாய் பரிவர்த்தனை (தீவிர பாலியல் நாட்டம்)",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D9,
        calculation_mode="thirukanitha",
        interpretation_en="In the Navamsa chart (D9), Venus placed in a Martian sign (Aries or Scorpio) while Mars is placed in a Venusian sign (Taurus or Libra) establishes a powerful Parivartana, producing intense erotic passion and unconventional relationships.",
        interpretation_ta="நவாம்ச ஜாதகத்தில் சுக்கிரன் செவ்வாயின் நவாம்ச ராசிகளான மேஷம் அல்லது விருச்சிகத்திலும், செவ்வாய் சுக்கிரனின் நவாம்ச ராசிகளான ரிஷபம் அல்லது துலாமிலும் அமைந்து பரிவர்த்தனை பெறுவது மரபு மீறிய தீவிர பாலியல் நாட்டத்தைக் குறிக்கும்.",
        astrological_principle_en="Brihat Jataka, Stri Jataka Adhyaya, Verse 4: 'If in Navamsa Venus occupies a sign of Mars and Mars occupies a sign of Venus, the woman engages in extramarital passion.'",
        astrological_principle_ta="நவாம்சத்தில் சுக்கிரனும் செவ்வாயும் பரிவர்த்தனை பெறுவது திருமணத்திற்கு வெளியேயான தீவிர காம உறவைக் குறிக்கும்.",
        source_reference="Brihat Jataka, Ch. 20 (Stri Jataka), Verse 4",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_sign", "planet": "Venus", "sign": [1, 8], "chart": "d9"},
                {"condition_type": "planet_sign", "planet": "Mars", "sign": [2, 7], "chart": "d9"}
            ]
        }
    ),

    # Stri Jataka Rule 5
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-05",
        name_en="Brihat Jataka Stri 5 - Venus, Mars & Moon Conjunction (Commercial / Coerced Intimacy)",
        name_ta="பிருஹத் ஜாதகம் ஸ்திரீ 5 - சுக்கிரன், செவ்வாய், சந்திரன் இணைதல்",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="The triple conjunction of Venus (sensuality), Mars (physical vitality/coercion), and Moon (mind) associates with extreme erotic vulnerability, commercialized sexual labor, or marital exploitation.",
        interpretation_ta="சுக்கிரன், செவ்வாய் மற்றும் சந்திரன் ஆகிய மூன்று கிரகங்களும் இணைந்திருப்பது தீவிர உணர்ச்சி வசப்படுதலையும், பொருளாதார நெருக்கடி அல்லது குடும்பத்தினரின் வற்புறுத்தலால் பாலியல் தொழிலில் ஈடுபடும் யோகத்தையும் குறிக்கும் என மூல ஆசிரியர் கூறுகிறார்.",
        astrological_principle_en="Brihat Jataka, Stri Jataka Adhyaya, Verse 5: 'Conjunction of Venus, Mars, and Moon denotes commercial or coerced intimacy.'",
        astrological_principle_ta="சுக்கிரன், செவ்வாய், சந்திரன் சேர்க்கை பொருளாதார சூழலால் பாலியல் தொழிலில் ஈடுபடும் அமைப்பைத் தரும்.",
        source_reference="Brihat Jataka, Ch. 20 (Stri Jataka), Verse 5",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Venus", "Mars", "Moon"],
            "chart": "d1"
        }
    ),

    # Stri Jataka Rule 6 (Chart Example 2 / 4 - Moon & Mars in 7th House Separation)
    AstrologicalRuleDefinition(
        rule_id="RULE-BJ-STRI-06",
        name_en="Brihat Jataka Example Pattern - Moon & Mars in 7th House (Marital Estrangement)",
        name_ta="பிருஹத் ஜாதக உதாரணம் - 7-ல் சந்திரன் மற்றும் செவ்வாய் சேர்க்கை (பிரிவு)",
        category_slug="sexuality_intimacy",
        subcategory="stri_jataka_principles",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        interpretation_en="Chandra-Mangala yoga situated directly in the 7th house provokes domestic turbulence, early estrangement, and subsequent uninhibited pursuit of independent livelihood and relationships.",
        interpretation_ta="7-ஆம் வீட்டில் சந்திரனும் செவ்வாயும் இணைந்திருப்பது தாம்பத்தியக் கசப்புகளையும், கணவரைப் பிரிந்து சுயமாக வாழும் சூழலையும் உருவாக்கும் என்று உதாரண ஜாதக ஆய்வில் குறிப்பிடப்பட்டுள்ளது.",
        astrological_principle_en="Brihat Jataka Practical Delineation: 'Moon and Mars in 7th house in female horoscopy indicates marital estrangement and independent path.'",
        astrological_principle_ta="7-ல் சந்திரன்-செவ்வாய் சேர்க்கை தாம்பத்திய முறிவையும் தன்னிச்சையான மாற்று வாழ்க்கையையும் தரும்.",
        source_reference="Brihat Jataka Example Analysis (Stri Jataka)",
        severity=SeverityLevel.UNFAVORABLE,
        applicable_gender="female",
        limitations_en=BJ_DISCLAIMER_EN,
        limitations_ta=BJ_DISCLAIMER_TA,
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Moon", "house": 7, "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"}
            ]
        }
    ),
]
