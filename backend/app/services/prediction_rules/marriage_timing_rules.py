"""Marriage Timing & Navamsa-Jaimini Composite Rules Registry.

Formulated from the classical synthesis treatise 'Marriage Timing in Astrology:
Easy Method to Predict Exact Age and Date' by Astrologer Debraj, synthesizing:
1. Brihat Parashara Hora Shastra principles (7th lord, dispositor, 2nd lord, Venus/Rahu).
2. Gayatri Devi Vasudev & Dr. B.V. Raman principles on Navamsa (D9) Dasha/Bhukti
   and the 4-8 mutual status transition (single to married).
3. Prof. K.N. Rao's Composite Method synthesizing Jaimini Darakaraka (DK),
   Chara Dasha, and Vimshottari timing.
4. Classical transit (Gochar) triggers: Double transit of Jupiter & Saturn over
   the 7th house, 7th lord, Navamsa Lagna, and Upapada Lagna (UL).
5. Love marriage (5th-7th) vs. secret attachment (5th-8th) yogas.
6. Timing impediments: Saturn and 8th lord afflictions causing delay vs. denial.
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

DEBRAJ_TIMING_DISCLAIMER_EN = (
    "Classical predictive guideline for timing marital union. Vedic astrology requires "
    "composite verification through multiple Dasha systems (Vimshottari and Chara Dasha), "
    "Navamsha (D9) confirmation, and favorable Gochara (Jupiter and Saturn transits)."
)
DEBRAJ_TIMING_DISCLAIMER_TA = (
    "திருமண கால நிர்ணயத்திற்கான பாரம்பரிய ஜோதிட விதி. விம்சோத்தரி தசா, ஜைமினி சார தசா, "
    "நவாம்ச (D9) அமைப்புகள் மற்றும் குரு, சனி கோச்சாரங்களின் ஒருங்கிணைந்த ஆய்வின் மூலம் "
    "திருமண காலத்தை துல்லியமாக நிர்ணயிக்க வேண்டும்."
)

MARRIAGE_TIMING_RULES: List[AstrologicalRuleDefinition] = [
    # -----------------------------------------------------------------------
    # Rule 1: 7th Lord Dasha / Bhukti Primary Marital Manifestation
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-01",
        version=1,
        name_en="7th Lord Dasha-Antardasha Primary Marriage Timing Window",
        name_ta="7-ஆம் அதிபதி தசா-புத்தி முதன்மை திருமணக் காலம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": [1, 2, 4, 5, 7, 9, 10, 11],
            "chart": "d1"
        },
        interpretation_en=(
            "When the 7th house lord is strong and favorably placed, its Mahadasha or Antardasha "
            "represents the primary astrological window for entering into legal marriage, solemnizing "
            "vows, and establishing long-term partnership bonds."
        ),
        interpretation_ta=(
            "7-ஆம் பாவக அதிபதி பலம் பெற்று சுப ஸ்தானங்களில் அமர்ந்திருக்கும் போது, அதன் மகா தசா அல்லது "
            "அந்தர்தசா/புத்திக் காலம் ஜாதகருக்குத் திருமணம் கைகூடும் தலையாய காலமாகும்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 1: The 7th lord from Lagna or Moon is the principal ruler of marital contract. "
            "Its operative periods naturally fructify marriageable events."
        ),
        astrological_principle_ta=(
            "லக்னம் அல்லது சந்திரனுக்கு 7-ஆம் அதிபதியின் தசா-புத்திகள் திருமண பந்தத்தை ஏற்படுத்துவதில் முதன்மையானவை."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 1; Phaladeepika Ch. 10",
        limitations_en="Combustion or severe Papa-Kartari yoga on the 7th lord may delay results until late in the period.",
        limitations_ta="7-ஆம் அதிபதி அஸ்தமனம் அல்லது பாபகர்த்தாரி யோகத்தில் இருப்பின் திருமணத்தில் தாமதம் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 2: Dispositor of the 7th Lord Timing Activation
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-02",
        version=1,
        name_en="7th Lord's Dispositor Activating Marital Fructification",
        name_ta="7-ஆம் அதிபதியின் வீட்டு அதிபதி (பரிவர்த்தனை/டிஸ்போஸிடர்) திருமண காலம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": [1, 4, 5, 7, 9, 10, 11],
            "chart": "d1"
        },
        interpretation_en=(
            "The dispositor of the 7th lord (the graha ruling the sign occupied by the 7th lord) "
            "carries delegated marital energy. Its Dasha or Antardasha frequently solemnizes wedlock "
            "when the 7th lord's own period is not operative during marriageable age."
        ),
        interpretation_ta=(
            "7-ஆம் அதிபதி அமர்ந்த வீட்டின் அதிபதி (டிஸ்போஸிடர்) திருமண காரகத்துவத்தைப் பெற்று விளங்குவார். "
            "அவரது தசா அல்லது அந்தர்தசா காலத்தில் திருமணம் வெகு விமரிசையாக நடைபெறும்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 2: The dispositor of the 7th lord acts as an active catalyst for marital fruition, "
            "channeling the energy of the partnership bhava."
        ),
        astrological_principle_ta=(
            "7-ஆம் அதிபதியின் வீட்டு அதிபதியின் காலத்திலும் திருமண பிராப்தம் முழுமையாகக் கைகூடும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 2; Jataka Parijata Ch. 14",
        limitations_en="Requires validation with current age and favorable transit support.",
        limitations_ta="திருமண வயதும் கோச்சார அனுகூலமும் இருத்தல் அவசியம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 3: 2nd Lord (Kutumba Sthana) Family Expansion Timing
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-03",
        version=1,
        name_en="2nd Lord Dasha-Antardasha (Kutumba Vriddhi & Household Union)",
        name_ta="2-ஆம் அதிபதி தசா-புத்தி (குடும்ப விருத்தி & திருமண யோகம்)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 2,
            "placed_in_house": [1, 2, 4, 5, 7, 9, 10, 11],
            "chart": "d1"
        },
        interpretation_en=(
            "Marriage connects two families and initiates Kutumba Vriddhi (family expansion). "
            "The Dasha or Antardasha of the 2nd lord brings integration into a new family circle "
            "and formalizes matrimony."
        ),
        interpretation_ta=(
            "திருமணம் என்பது இரு குடும்பங்களின் சங்கமம் மற்றும் புதிய குடும்ப உறுப்பினரின் வருகையாகும். "
            "2-ஆம் அதிபதியின் தசா-புத்தி காலத்தில் குடும்ப விருத்தியுடன் கூடிய திருமணப் பாக்கியம் உருவாகும்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 6: 2nd house governs family, mutual speech, and wealth. Its lord triggers "
            "household expansion through wedlock."
        ),
        astrological_principle_ta=(
            "2-ஆம் பாவம் குடும்ப ஸ்தானம் என்பதால், அதன் அதிபதியின் காலத்தில் இல்லற வாழ்க்கை தொடங்குகிறது."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 6; Brihat Parashara Hora Shastra",
        limitations_en="As 2nd house is also a Maraka bhava, health of elders should be safeguarded.",
        limitations_ta="2-ஆம் பாவம் மாரக ஸ்தானமாகவும் இருப்பதால் சுப ஆதிபத்தியம் கவனிக்கப்பட வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 4: Venus & Rahu Operative Periods as Marriage Catalysts
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-04",
        version=1,
        name_en="Natural Significator Venus or Catalyst Rahu Operative Window",
        name_ta="சுக்கிரன் அல்லது ராகு தசா-புத்தி திருமண உந்துதல்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Venus", "house": [1, 2, 4, 5, 7, 9, 10, 11], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Rahu", "house": [3, 6, 7, 10, 11], "chart": "d1"}
            ]
        },
        interpretation_en=(
            "Venus is the natural Karaka of romance and marriage, while Rahu acts as an unconventional, "
            "sudden relationship catalyst. Operating Dasha or Antardasha periods of Venus or Rahu during "
            "marriageable age frequently grant wedlock regardless of their chart lordship."
        ),
        interpretation_ta=(
            "சுக்கிரன் திருமணத்திற்கான நைசர்கிக காரகர்; ராகு திடீர் திருமண நிகழ்வுகளுக்கு வழிகோலும் கிரகம். "
            "திருமண வயதில் வரும் சுக்கிரன் அல்லது ராகுவின் தசா-புத்திகள் ஆதிபத்தியம் பாராமல் திருமணத்தைத் தரும்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 7: Natural significator Venus and catalyst Rahu possess inherent potency to confer "
            "marital alliances during prime youth."
        ),
        astrological_principle_ta=(
            "இயற்கை களத்திர காரகன் சுக்கிரன் மற்றும் சமூக பந்தங்களை விரிவுபடுத்தும் ராகுவின் காலத்தில் திருமணம் நடக்கும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 7; Saravali Ch. 34",
        limitations_en="Rahu Dasha may create rapid or inter-community unions; check Navamsa disposition.",
        limitations_ta="ராகு காலத்தில் நடக்கும் திருமணம் வழக்கத்திற்கு மாறானதாகவோ விரைவானதாகவோ அமையலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 5: 7th Lord from Venus (Shukra Kalatra Sthana Lord)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-05",
        version=1,
        name_en="7th Lord Reckoned from Natal Venus (Shukra Kalatra Adhipati)",
        name_ta="சுக்கிரனுக்கு 7-ஆம் அதிபதி தசா-புத்தி திருமண யோகம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Venus",
            "house": [1, 2, 4, 5, 7, 9, 10, 11],
            "chart": "d1"
        },
        interpretation_en=(
            "The 7th house reckoned from natal Venus represents the Karaka-Lagna perspective of marital destiny. "
            "The planetary ruler of this sign triggers wedding ceremonies during its Dasha or Antardasha."
        ),
        interpretation_ta=(
            "சுக்கிரன் நின்ற ராசியிலிருந்து 7-ஆம் வீட்டு அதிபதி திருமணத்திற்கான முக்கிய காரக ஆதிபத்தியம் வகிக்கிறார். "
            "இவரின் தசா-புத்திக் காலத்தில் களத்திர பாக்கியம் நனவாகும்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 8: Parashari Karaka-Lagna principle: Dasha/Antardasha of the 7th lord from Venus "
            "bestows marriage and romantic fulfillment."
        ),
        astrological_principle_ta=(
            "காரக லக்ன விதியின்படி சுக்கிரனுக்கு 7-ஆம் இடத்து அதிபதி திருமணக் காலத்தை நிர்ணயிக்கிறார்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 8; Brihat Parashara Hora Shastra",
        limitations_en="Cross-reference with Vimshottari Mahadasha balance.",
        limitations_ta="விம்சோத்தரி தசா இருப்புடன் ஒப்பிட்டுப் பார்க்க வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 6: Bhavat Bhavam (Lagna Lord / 7th from 7th) Marriage Activation
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-06",
        version=1,
        name_en="Lagna Lord (7th from 7th Bhavat Bhavam) Marriage Timing",
        name_ta="லக்னாதிபதி (பவாத் பாவம் - 7க்கு 7) திருமண பந்தம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 1,
            "placed_in_house": [1, 2, 4, 5, 7, 9, 10, 11],
            "chart": "d1"
        },
        interpretation_en=(
            "Under the Bhavat Bhavam principle, the 7th house from the 7th is the Lagna (1st house). "
            "Consequently, the Dasha or Antardasha of the Lagna lord frequently formalizes marital status, "
            "signifying a complete rebirth and personal evolution through matrimony."
        ),
        interpretation_ta=(
            "பவாத் பாவ விதியின்படி 7-ஆம் பாவத்திற்கு 7-ஆம் பாவம் லக்னம் ஆகும். எனவே லக்னாதிபதியின் தசா-புத்தி "
            "காலத்தில் ஜாதகர் புதிய இல்லற அந்தஸ்தைப் பெறுவார்."
        ),
        astrological_principle_en=(
            "Core Vedic Rule 9: The Lagna lord represents the self taking on marital responsibilities. "
            "Its period marks definitive personal transitions."
        ),
        astrological_principle_ta=(
            "லக்னாதிபதி பலம் பெற்று சுப ஸ்தானத்தில் அமர்ந்து தசா நடத்தும் போது திருமணம் நிச்சயமாகும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Rule 9; Phaladeepika",
        limitations_en="Must be evaluated alongside the 7th lord and transit Jupiter.",
        limitations_ta="7-ஆம் அதிபதி மற்றும் குரு கோச்சாரத்துடன் இணைத்து அறிய வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 7: Navamsha Lagna Lord Antardasha Activation
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-07",
        version=1,
        name_en="Navamsha Lagna Lord Antardasha Direct Marital Fructification",
        name_ta="நவாம்ச லக்னாதிபதி அந்தர்தசா திருமண யோகம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D9,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 1,
            "placed_in_house": [1, 4, 5, 7, 9, 10],
            "chart": "d9"
        },
        interpretation_en=(
            "Because Navamsha (D9) specifically governs marital karma, the rising Navamsha Lagna Lord's "
            "Antardasha carries decisive power to trigger wedlock. For example, Aries/Scorpio Navamsha Lagna "
            "triggers marriage in Mars periods; Taurus/Libra in Venus periods."
        ),
        interpretation_ta=(
            "நவாம்சம் என்பது களத்திர கர்மாவை குறிக்கும் முக்கிய வர்க்க சக்கரம். நவாம்ச லக்னாதிபதியின் புத்தி அல்லது தசா "
            "காலம் திருமணத்தை நேரடியாக நடத்தி வைக்கும் அதீத ஆற்றல் கொண்டது."
        ),
        astrological_principle_en=(
            "Navamsha Principle: The lord of the rising sign in Navamsha is the gatekeeper of marital manifestation. "
            "Its sub-period marks the solemnization of marriage."
        ),
        astrological_principle_ta=(
            "நவாம்ச லக்னாதிபதியின் அந்தர்தசா காலத்தில் திருமணம் கைகூடும் என்பது பாரம்பரிய அனுபவ விதி."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Navamsha Rules; Gayatri Devi Vasudev",
        limitations_en="Accurate birth time within 2-3 minutes is required for precise Navamsha Lagna determination.",
        limitations_ta="நவாம்ச லக்னம் சரியாக அமைய துல்லியமான பிறப்பு நேரம் அவசியமாகும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 8: Gayatri Devi Vasudev 4-8 Mutual Placement in Navamsha (Single to Married)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-08",
        version=1,
        name_en="Gayatri Devi Vasudev Principle: Navamsha 4-8 Axis Status Transition",
        name_ta="காயத்ரி தேவி வாசுதேவ் விதி: நவாம்சத்தில் 4-8 நிலை மாற்றம் (திருமண அந்தஸ்து)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D9,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": [4, 8, 10], "chart": "d9"},
                {"condition_type": "house_lord_placement", "house": 1, "placed_in_house": [4, 8], "chart": "d9"}
            ]
        },
        interpretation_en=(
            "As highlighted by renowned astrologer Gayatri Devi Vasudev (daughter of Dr. B.V. Raman), a 4-8 "
            "mutual disposition (chaturthashtaka) of Mahadasha and Antardasha lords in the Navamsha chart "
            "denotes a dramatic transformation of personal status: transitioning permanently from single to married."
        ),
        interpretation_ta=(
            "டாக்டர் பி.வி. ராமனின் புதல்வி காயத்ரி தேவி வாசுதேவ் அவர்களின் ஆய்வுப்படி, நவாம்ச சக்கரத்தில் தசாநாதன் "
            "மற்றும் புத்திநாதன் பரஸ்பரம் 4-8 (சதுர்த்தாஷ்டகம்) அமைப்பில் இருப்பது ஜாதகரின் அந்தஸ்தை பிரம்மச்சரியத்திலிருந்து "
            "இல்லற வாழ்க்கைக்கு மாற்றும் திருப்புமுனையாகும்."
        ),
        astrological_principle_en=(
            "Navamsha 4-8 Transition: The 4th house represents home and domestic comfort, while the 8th represents "
            "status alteration. Their mutual relationship in D9 shifts life from solitary to partnered living."
        ),
        astrological_principle_ta=(
            "நவாம்சத்தில் 4-8 தொடர்பு ஏற்படுவது இல்லற அமைப்பையும் வாழ்க்கைத் துணையின் பிரவேசத்தையும் உறுதிப்படுத்துகிறது."
        ),
        source_reference="Gayatri Devi Vasudev; Dr. B.V. Raman; Marriage Timing in Astrology (Debraj)",
        limitations_en="If malefic afflictions dominate, the 4-8 axis can bring sudden marital adjustments.",
        limitations_ta="பாப கிரகங்களின் சேர்க்கை இருப்பின் திருமண ஆரம்பத்தில் சில சவால்கள் வரலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 9: Jaimini Darakaraka (DK) Sign & Period (K.N. Rao Composite Technique)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-09",
        version=1,
        name_en="Jaimini Darakaraka (DK) Composite Marriage Timing (K.N. Rao System)",
        name_ta="ஜைமினி தாரகாரகன் (DK) மற்றும் கே.என். ராவ் கூட்டுத் திருமண நிர்ணயம்",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.COMBINED,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_occupancy", "house": 7, "chart": "d1", "is_empty": False},
                {"condition_type": "house_occupancy", "house": 7, "chart": "d9", "is_empty": False}
            ]
        },
        interpretation_en=(
            "In Jaimini Upadesha Sutras, the planet holding the lowest degree is the Darakaraka (DK), "
            "the prime significator of spouse. As taught by master astrologer K.N. Rao, marriage fructifies "
            "during the Chara Dasha of the sign housing DK in D1 or D9, the sign owned by DK, or even the "
            "Vimshottari Dasha-Antardasha of the Darakaraka planet itself."
        ),
        interpretation_ta=(
            "ஜைமினி ஜோதிடத்தில் குறைந்த பாகை பெற்ற கிரகம் 'தாரகாரகன்' (DK) எனப்படும். புகழ்பெற்ற ஜோதிடர் கே.என். ராவ் "
            "அவர்களின் ஒருங்கிணைந்த முறையின்படி, தாரகாரகன் நின்ற ராசி, அவரது நவாம்ச ராசி, அல்லது தாரகாரக கிரகத்தின் "
            "விம்சோத்தரி தசா-புத்தி காலத்தில் திருமணம் உறுதியாக நடந்தேறும்."
        ),
        astrological_principle_en=(
            "Jaimini & Composite Rule: Darakaraka embodies the physical arrival of the spouse. Linking Jaimini DK "
            "with Vimshottari Dasha yields the highest empirical accuracy."
        ),
        astrological_principle_ta=(
            "தாரகாரக கிரகத்தின் தசா-புத்திகள் திருமண பந்தத்தை வாழ்நாளில் கொண்டுவரும் அசைக்க முடியாத விதி."
        ),
        source_reference="Jaimini Sutras; K.N. Rao Composite Method; Marriage Timing in Astrology (Debraj)",
        limitations_en="DK must be accurately identified using lowest planetary degrees excluding Rahu/Ketu.",
        limitations_ta="ராகு, கேது தவிர்த்து 7 கிரகங்களில் குறைந்த பாகை பெற்ற கிரகத்தை சரியாக கணக்கிட வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 10: 5th-7th Connection (Love Marriage & Romantic Timing)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-10",
        version=1,
        name_en="5th & 7th Lords Connection (Love Marriage & Courtship Fructification)",
        name_ta="5 மற்றும் 7-ஆம் அதிபதிகள் தொடர்பு (காதல் திருமணம் மற்றும் மனமொத்த பந்தம்)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": 7, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 5, "chart": "d1"},
                {"condition_type": "mutual_exchange", "house_a": 5, "house_b": 7, "chart": "d1"}
            ]
        },
        interpretation_en=(
            "When the 5th house (Purva Punya, romance, courtship) connects with the 7th house (matrimony, legal union) "
            "via mutual exchange, placement, or aspect, it creates definitive yogas for Love Marriage. Marriage is solemnized "
            "during the operating periods of these interconnected lords."
        ),
        interpretation_ta=(
            "5-ஆம் அதிபதி (காதல், பூர்வ புண்ணியம்) மற்றும் 7-ஆம் அதிபதி (திருமணம்) ஆகிய இருவரும் பரிவர்த்தனை, "
            "இணைவு அல்லது பார்த்துக் கொள்ளும் போது காதல் திருமணம் கைகூடும். இவர்களின் தசா-புத்திகளில் காதல் வெற்றியாகும்."
        ),
        astrological_principle_en=(
            "5th-7th Sambandha translates personal romantic attachment into sanctified marital partnership."
        ),
        astrological_principle_ta=(
            "5 மற்றும் 7-ஆம் பாவக தொடர்புகள் காதல் பந்தத்தை சட்டப்பூர்வ இல்லறமாக மாற்றும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), House 7 & 5; Phaladeepika",
        limitations_en="If afflicted by Saturn or Rahu, courtship may require overcoming family initial reservations.",
        limitations_ta="சனி அல்லது ராகு சம்பந்தப்பட்டால் குடும்பத்தினரின் சம்மதம் பெற சற்று போராட வேண்டியிருக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 11: 5th & 8th Lords Connection (Sensual Nature & Secret Attachment Dynamics)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-11",
        version=1,
        name_en="5th & 8th Lords Connection (Sensual Intensity & Confidential Romance)",
        name_ta="5 மற்றும் 8-ஆம் அதிபதிகள் தொடர்பு (ரகசிய ஈர்ப்பு & உணர்ச்சிபூர்வ உறவு)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": 8, "chart": "d1"},
                {"condition_type": "house_lord_placement", "house": 8, "placed_in_house": 5, "chart": "d1"}
            ]
        },
        interpretation_en=(
            "When the 5th house of affection connects with the 8th house of privacy, hidden pleasures, and sensual "
            "depth, the native experiences intense emotional attachments, deep romantic privacy, or unconventional "
            "secret relationships before formalization."
        ),
        interpretation_ta=(
            "5-ஆம் அதிபதியும் 8-ஆம் அதிபதியும் இணைவது அல்லது பார்த்துக் கொள்வது அதீத உணர்ச்சிவசப்படும் தன்மை, "
            "ரகசியக் காதல் மற்றும் வெளிப்படையாகத் தெரியாத ஆழமான பந்தங்களை உருவாக்கும்."
        ),
        astrological_principle_en=(
            "5th-8th Connection: The 8th house represents privacy, shared secrets, and physical magnetism. "
            "When linked with romance (5th), relationships are characterized by deep discretion and passionate intensity."
        ),
        astrological_principle_ta=(
            "மறைவு ஸ்தானமான 8-ஆம் பாவத்துடன் காதல் ஸ்தானமான 5-ஆம் பாவம் இணைவது அந்தரங்கக் காதல் யோகமாகும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), House 8 & 5; Jataka Tatva",
        limitations_en="Discretion is advised to avoid emotional complications; benefic Jupiter mitigates secrecy.",
        limitations_ta="குருவின் சுபப் பார்வை இருப்பின் தவறான வழிகளில் செல்லாமல் ஆன்மீக பந்தமாக மாறும்.",
        severity=SeverityLevel.NEUTRAL,
    ),

    # -----------------------------------------------------------------------
    # Rule 12: Saturn Affliction on 7th House / Lord (Delayed Marriage Check)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-12",
        version=1,
        name_en="Saturn Affliction on 7th House / Lord (Mature & Delayed Marriage Verification)",
        name_ta="7-ஆம் பாவத்தில் சனி பார்வை அல்லது அமர்வு (காலதாமத மற்றும் முதிர்ந்த திருமணம்)",
        category_slug="delayed_marriage",
        subcategory="delayed_marriage",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Saturn", "house": 7, "chart": "d1"},
                {"condition_type": "planet_aspect", "aspecting_planet": "Saturn", "target_type": "house", "target_value": 7, "chart": "d1"}
            ]
        },
        interpretation_en=(
            "Before calculating timing windows, Vedic astrology requires determining whether the native has a timely "
            "or delayed marriage. Saturn influencing the 7th house or 7th lord demands emotional maturity, typically "
            "delaying marriage until after age 28 to 32, filtering out premature or unstable alliances."
        ),
        interpretation_ta=(
            "திருமண காலத்தைக் கணிக்கும் முன் காலதாமத அமைப்புகள் உள்ளதா எனப் பார்ப்பது அவசியம். 7-ஆம் வீட்டில் சனி அமர்வது "
            "அல்லது 7-ஆம் வீட்டைப் பார்ப்பது திருமணத்தை 28 முதல் 32 வயது வரை தாமதப்படுத்தி, பக்குவமான துணையை அமைக்கும்."
        ),
        astrological_principle_en=(
            "Step 2 Delay Check: Saturn's cold, deliberate nature tests marital foundations. When Saturn is involved, "
            "marriage should not be timed in early youth (under age 25)."
        ),
        astrological_principle_ta=(
            "சனி பகவானின் தாக்கம் திருமணத்தில் காலதாமதத்தைத் தந்தாலும், பிற்காலத்தில் நிலையான வாழ்வை நல்கும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Step 2 Delay Check; Brihat Parashara Hora Shastra",
        limitations_en="If Saturn is in own sign (Capricorn/Aquarius) or exalted in Libra, delay yields great stability.",
        limitations_ta="சனி ஆட்சி அல்லது உச்சம் பெற்று நின்றால் தாமதமானாலும் மிகச் சிறந்த வரன் அமையும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 13: 8th Lord Affliction on 7th House (Marital Endurance Screening)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-13",
        version=1,
        name_en="8th Lord Influence on 7th House / Lord (Marital Longevity & Timing Screener)",
        name_ta="8-ஆம் அதிபதி 7-ல் அமர்வு (மாங்கல்ய பலம் & திருமண கால நிதானம்)",
        category_slug="delayed_marriage",
        subcategory="delayed_marriage",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 8,
            "placed_in_house": 7,
            "chart": "d1"
        },
        interpretation_en=(
            "The 8th house is the 2nd from the 7th, governing marital sustenance, longevity, and shared assets. "
            "When the 8th lord occupies the 7th house, marriage timing requires careful horoscopic matching to ensure "
            "enduring stability and prevent hasty alliances."
        ),
        interpretation_ta=(
            "8-ஆம் பாவம் 7-க்கு 2-ஆம் வீடாகி மாங்கல்ய ஸ்தானமாகவும் திருமணத்தின் ஆயுளாகவும் விளங்குகிறது. 8-ஆம் அதிபதி "
            "7-ல் அமர்வது நிதானமான திருமணப் பொருத்தத்தையும், முறையான கால நிர்ணயத்தையும் கோருகிறது."
        ),
        astrological_principle_en=(
            "Step 2 Screener: 8th lord in 7th challenges initial marital ease but grants profound transformation "
            "once both partners cultivate mutual forbearance."
        ),
        astrological_principle_ta=(
            "8-ஆம் அதிபதியின் அமைப்பினால் திருமண ஏற்பாடுகளில் தடைகள் வந்து விலகும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Step 2; Phaladeepika Ch. 10",
        limitations_en="Aspect of Jupiter or Venus neutralizes hurdles completely.",
        limitations_ta="குருவின் சுபப் பார்வை இருந்தால் சகல தடைகளும் நீங்கி சுபமங்களம் உண்டாகும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 14: Jupiter Drishti on 7th House (Divine Sanction for Timely Marriage)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-14",
        version=1,
        name_en="Jupiter Divine Drishti on 7th House (Auspicious Timing Sanction)",
        name_ta="7-ஆம் பாவத்திற்கு குருவின் சுபப் பார்வை (தெய்வீக திருமண யோகம்)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_aspect",
            "aspecting_planet": "Jupiter",
            "target_type": "house",
            "target_value": 7,
            "chart": "d1"
        },
        interpretation_en=(
            "Jupiter casting its 5th, 7th, or 9th glance upon the 7th house confers supreme divine blessing, "
            "cancelling afflictions, dissolving delay yogas, and guaranteeing timely solemnization of marriage "
            "during favorable Dasha-Antardasha cycles."
        ),
        interpretation_ta=(
            "தேவகுருவான குரு பகவான் தனது 5, 7 அல்லது 9-ஆம் பார்வையால் 7-ஆம் பாவத்தைப் பார்ப்பது அனைத்து தோஷங்களையும் "
            "போக்கி, நற்குணங்கள் நிறைந்த வாழ்க்கைத் துணையுடன் குறித்த காலத்தில் திருமணத்தை நடத்தி வைக்கும்."
        ),
        astrological_principle_en=(
            "Guru Drishti is the premier classical antidote to marital delay. When Jupiter aspects the 7th house, "
            "matrimonial prospects are blessed with social honor and happiness."
        ),
        astrological_principle_ta=(
            "'குரு பார்க்க கோடி நன்மை' என்பதற்கேற்ப குருவின் பார்வை 7-ஆம் பாவத்திற்கு கிடைப்பது அரிய பாக்கியமாகும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj); Brihat Parashara Hora Shastra",
        limitations_en="Jupiter must not be afflicted by deep debilitation or Rahu conjunction.",
        limitations_ta="குரு நீசம் அல்லது ராகுவுடன் இணைந்து குரு சண்டாள யோகம் பெறாமல் இருக்க வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # -----------------------------------------------------------------------
    # Rule 15: 7th Lord in Navamsha Kendra/Trikona (D9 Sanction for Harmonious Union)
    # -----------------------------------------------------------------------
    AstrologicalRuleDefinition(
        rule_id="RULE-MARR-TIME-15",
        version=1,
        name_en="Navamsha 7th Lord in Auspicious Kendra/Trikona (D9 Marital Harmony)",
        name_ta="நவாம்ச 7-ஆம் அதிபதி கேந்திர, திரிகோணத்தில் அமர்வு (நவாம்ச திருமண உறுதிப்பாடு)",
        category_slug="marriage_timing",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D9,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "house_lord_placement",
            "house": 7,
            "placed_in_house": [1, 4, 5, 7, 9, 10],
            "chart": "d9"
        },
        interpretation_en=(
            "When the 7th lord of the Navamsha (D9) chart is situated in a Kendra (1, 4, 7, 10) or Trikona (1, 5, 9), "
            "the core marital destiny is fortified. During its operating periods, wedding ceremonies proceed smoothly "
            "with enthusiastic support from both families."
        ),
        interpretation_ta=(
            "நவாம்சத்தில் 7-ஆம் அதிபதி கேந்திர அல்லது திரிகோண வீடுகளில் சுப பலத்துடன் அமர்வது திருமண பந்தத்தை "
            "வலுவாக்கும். இவரது தசா-புத்திகளில் இரு குடும்பத்தாரின் முழு ஆசியுடன் திருமணம் கைகூடும்."
        ),
        astrological_principle_en=(
            "Navamsha Confirmation: D1 indicates the potential of marriage, while D9 confirms the fruition and "
            "dignity of the bond. A fortified D9 7th lord ensures auspicious timing."
        ),
        astrological_principle_ta=(
            "ராசி சக்கரம் மரத்தின் கிளை என்றால் நவாம்சம் அதன் வேர். நவாம்ச 7-ஆம் அதிபதியின் பலம் திருமணத்தை உறுதி செய்யும்."
        ),
        source_reference="Marriage Timing in Astrology (Debraj), Navamsha Rules; Phaladeepika",
        limitations_en="Verify absence of debilitation or planetary war in D9.",
        limitations_ta="நவாம்சத்தில் கிரகம் நீசம் அல்லது கிரக யுத்தம் அடையாமல் இருக்க வேண்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
]
