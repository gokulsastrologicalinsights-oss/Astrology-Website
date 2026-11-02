"""K.N. Rao Advanced Astrological Research Prediction Rules Registry.

Formulated from the research compilation treatise:
'Advanced Techniques of Astrological Predictions'
(Vedic Astrology Series, B.P.E.S.V. Sansthan / Bharatiya Vidya Bhavan, New Delhi).

Key Papers & Authors:
1. S.N. Kapoor: Service vs Self-Employment thumb rules
2. R.C. Sharma: Technical vs Non-Technical 4-fold scoring
3. Col. A.K. Gour: Authors and Journalists literary enquiry
4. Shunny Nigam: Marital Discord 4 Main + 2 Supplementary Rules
5. Supriya Jagdish: Darakaraka in Vimshottari
6. Kusum Vashishtha: Successful Women in Leadership
7. Z Ansari: Advanced Kaal Sarpa Yoga & Ashta-Lakshmi Yoga
8. Dr. K.S. Charak: Medical Astrology, Mrityu Bhaga & Recovery Prognosis
9. P.C. Verma & Dr. R.K. Aggarwal: Ashtakavarga Kakshya & 8-Part Timing
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

KN_RAO_DISCLAIMER_EN = (
    "Empirically validated astrological research rule from 'Advanced Techniques of "
    "Astrological Predictions', edited by K.N. Rao (Bharatiya Vidya Bhavan, New Delhi)."
)
KN_RAO_DISCLAIMER_TA = (
    "கே.என். ராவ் தொகுத்த 'Advanced Techniques of Astrological Predictions' (பாரதிய வித்யா பவன், "
    "புது தில்லி) ஆய்வுக் கட்டுரைகளின் அடிப்படையில் சோதித்து உறுதிசெய்யப்பட்ட பாரம்பரிய பலன்."
)

KN_RAO_ADVANCED_RULES: List[AstrologicalRuleDefinition] = [
    # =======================================================================
    # 1. SERVICE VS SELF-EMPLOYMENT (S.N. KAPOOR)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-SE-01",
        version=1,
        name_en="Poorna Parmatmansha Dominance: Independent Business & Authority",
        name_ta="பூர்ண பரமாத்மாம்ச கிரக ஆதிக்கம்: சுயதொழில் மற்றும் தலைமை",
        category_slug="career_profession",
        subcategory="business_vs_job",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Sun",
            "houses": [10, 11, 1],
            "chart": "d1",
        },
        interpretation_en=(
            "According to S.N. Kapoor's research, Poorna Parmatmansha planets (Sun, Moon, Mars, Rahu) "
            "possess an inherent divine impulse for autonomy and self-directed creation. When Sun or "
            "Mars occupy the executive 10th or 11th houses, the native shows strong aversion to "
            "subordination, gravitating towards independent entrepreneurship, proprietary enterprise, "
            "or apex leadership with decisive authority."
        ),
        interpretation_ta=(
            "எஸ்.என். கபூரின் ஆய்வின்படி, பூர்ண பரமாத்மாம்ச கிரகங்கள் (சூரியன், சந்திரன், செவ்வாய், ராகு) "
            "மனிதருக்கு தன்னாட்சி மற்றும் சுயாதீன தொழில் செய்யும் உந்துதலைத் தருகின்றன. சூரியன் அல்லது செவ்வாய் "
            "10 அல்லது 11-ம் வீட்டில் அமையும்போது, பிறருக்கு அடிபணியாமல் சொந்த தொழில், வணிகம் அல்லது "
            "உயர் நிர்வாகப் பொறுப்புகளில் தனித்து இயங்கும் ஆற்றல் உண்டாகும்."
        ),
        astrological_principle_en="Poorna Parmatmansha planets in the visible half (7th-12th) or executive axis (10th-3rd) favor autonomous enterprise.",
        astrological_principle_ta="பூர்ண பரமாத்மாம்ச கிரகங்கள் பத்தாம் வீட்டில் அல்லது நிர்வாக ஸ்தானங்களில் பலம்பெறுவது சுயதொழில் ஆதிக்கத்தைத் தரும்.",
        source_reference="Advanced Techniques of Astrological Predictions, S.N. Kapoor, pp. 32-54",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Channel entrepreneurial energy through ethical leadership and fair treatment of employees.",
        remedy_ta="பணியாளர்களை நியாயமாக நடத்தி தர்ம நெறிகளுடன் கூடிய தொழில் முயற்சியில் ஈடுபடவும்.",
        sources=["Advanced Techniques of Astrological Predictions - S.N. Kapoor (pp. 32-54)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-SE-02",
        version=1,
        name_en="Subordination Zone Cluster: Corporate & Civil Service Propensity",
        name_ta="4, 5, 6-ம் வீடுகளில் கிரகக் குவியல்: உத்தியோக ஈடுபாடு",
        category_slug="career_profession",
        subcategory="business_vs_job",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Saturn",
            "houses": [6],
            "chart": "d1",
        },
        interpretation_en=(
            "S.N. Kapoor's thumb rules reveal that when Saturn or multiple planets occupy the 6th house "
            "(the core house of service and routine duties), the native thrives in structured corporate "
            "employment, civil services, or salaried professional roles. The 6th house orientation instills "
            "dependability, discipline in hierarchy, and mastery over routine administrative challenges."
        ),
        interpretation_ta=(
            "எஸ்.என். கபூரின் விதிப்படி, சேவை மற்றும் கடமைகளின் ஸ்தானமான 6-ம் வீட்டில் சனி அல்லது பல கிரகங்கள் "
            "அமைந்தால், ஜாதகர் அரசு பணி, பெருநிறுவன வேலை அல்லது மாத சம்பள உத்தியோகத்தில் சிறப்பாக விளங்குவார். "
            "அலுவலக விதிகளுக்குக் கட்டுப்பட்டு கடினமாக உழைக்கும் திறன் மற்றும் ஒழுக்கம் மேலோங்கும்."
        ),
        astrological_principle_en="Planets clustered in houses 4 to 6 (subordination zone) promote structured salaried employment over business.",
        astrological_principle_ta="4 முதல் 6 வரையிலான வீடுகளில் கிரகங்கள் அமைவது மாத சம்பள உத்தியோகத்திற்கு வழிவகுக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, S.N. Kapoor, pp. 35-42",
        severity=SeverityLevel.NEUTRAL,
        remedy_en="Maintain patience and continuous upskilling to secure steady corporate promotions.",
        remedy_ta="பொறுமையுடன் பணிபுரிந்து தொடர்ந்து புதிய திறன்களைக் கற்று பதவி உயர்வு பெறவும்.",
        sources=["Advanced Techniques of Astrological Predictions - S.N. Kapoor (pp. 35-42)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-SE-03",
        version=1,
        name_en="Saturn Gocharastha on Career: Commercial Enterprise & Industrial Expansion",
        name_ta="சுப ஸ்தான சனி பார்வை: சுய வணிகம் மற்றும் தொழில்துறை விரிவாக்கம்",
        category_slug="career_profession",
        subcategory="business_vs_job",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Saturn",
            "dignities": ["exalted", "own"],
            "chart": "d1",
        },
        interpretation_en=(
            "When Saturn is in dignified Gocharastha status (exalted in Libra, or in own signs Capricorn/Aquarius) "
            "and aspects or occupies career houses, Kapoor's research proves a decisive shift towards self-employment. "
            "Rather than subservience, the native builds scalable systems, manufacturing enterprises, logistics, "
            "real estate ventures, or long-term independent business assets."
        ),
        interpretation_ta=(
            "சனி பகவான் ஆட்சி (மகரம்/கும்பம்) அல்லது உச்சம் (துலாம்) பெற்று சுப பலத்துடன் தொழில் ஸ்தானத்தை "
            "நோக்கினால், ஜாதகர் பிறரிடம் அடிபணிந்து வேலை செய்யாமல் சொந்த உற்பத்தி, ரியல் எஸ்டேட், தொழில் துறை "
            "அல்லது வர்த்தக சாம்ராஜ்யத்தை கட்டமைத்து சுயதொழிலில் கொடிகட்டிப் பறப்பார்."
        ),
        astrological_principle_en="Dignified Saturn (Gocharastha) directing influence onto 10th or Lagna empowers proprietary enterprise.",
        astrological_principle_ta="ஆட்சி உச்சம் பெற்ற சனி பகவானின் பார்வை தொழில் ஸ்தானத்தில் பதிவது பெரிய அளவிலான சுயதொழில் வெற்றியைத் தரும்.",
        source_reference="Advanced Techniques of Astrological Predictions, S.N. Kapoor, pp. 43-48",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Support manual laborers and maintain ethical accounting practices in business.",
        remedy_ta="தொழிலாளர்களுக்கு உரிய ஊதியத்தை வழங்கி, நேர்மையான கணக்கு வழக்குகளைப் பேணவும்.",
        sources=["Advanced Techniques of Astrological Predictions - S.N. Kapoor (pp. 43-48)"],
    ),

    # =======================================================================
    # 2. TECHNICAL VS NON-TECHNICAL (R.C. SHARMA)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-TECH-01",
        version=1,
        name_en="Rahu Influencing 10th House: High-Tech, Electronics & Software Engineering",
        name_ta="10-ம் வீட்டில் ராகு: நவீன கணினி, மின்னணுவியல் மற்றும் மென்பொருள் துறை",
        category_slug="career_profession",
        subcategory="career_field",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Rahu",
            "houses": [10],
            "chart": "d1",
        },
        interpretation_en=(
            "R.C. Sharma's comprehensive 4-fold scoring model establishes that Rahu in the 10th house "
            "is the primary signature of cutting-edge technology. It guides the native towards electronics, "
            "telecommunications, computer engineering, aviation, artificial intelligence, and non-conventional "
            "high-tech industries, yielding significant technical mastery and global professional exposure."
        ),
        interpretation_ta=(
            "ஆர்.சி. சர்மாவின் கணித மாதிரிப்படி, 10-ம் வீட்டில் ராகு அமைவது அதிநவீன தொழில்நுட்பத்தின் "
            "முதன்மை குறியீடாகும். இது மின்னணுவியல், தகவல் தொழில்நுட்பம் (IT), மென்பொருள், வான்வெளித் துறை, "
            "மற்றும் செயற்கை நுண்ணறிவு சார்ந்த நவீன பொறியியல் துறைகளில் மாபெரும் வெற்றியைத் தரும்."
        ),
        astrological_principle_en="Rahu's dominance on the 10th house marks futuristic engineering and computing vocations.",
        astrological_principle_ta="10-ம் வீட்டில் ராகுவின் ஆதிக்கம் நவீன கணினி மற்றும் மின்னணு பொறியியல் துறையைக் குறிக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, R.C. Sharma, pp. 50-72",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Engage in continuous technical certifications and maintain focus amidst technological shifts.",
        remedy_ta="தொழில்நுட்பத் திறன்களைத் தொடர்ந்து மேம்படுத்தி சர்வதேச திட்டங்களில் கவனம் செலுத்தவும்.",
        sources=["Advanced Techniques of Astrological Predictions - R.C. Sharma (pp. 50-72)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-TECH-02",
        version=1,
        name_en="Mars-Saturn Influence on 10th: Core Mechanical, Civil & Industrial Engineering",
        name_ta="10-ம் வீட்டில் செவ்வாய்-சனி தொடர்பு: இயந்திர, கட்டுமான மற்றும் தொழிற்சாலை பொறியியல்",
        category_slug="career_profession",
        subcategory="career_field",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Mars",
            "houses": [10],
            "chart": "d1",
        },
        interpretation_en=(
            "In R.C. Sharma's empirical model, Mars in the 10th house produces Kuladipaka Yoga while scoring "
            "heavily as a technical planet (-2 score). When coupled with Saturnian aspect or nakshatras, it "
            "directs the native into core engineering disciplines: mechanical, civil construction, mining, "
            "defense technology, electrical grids, and industrial machinery."
        ),
        interpretation_ta=(
            "ஆர்.சி. சர்மாவின் ஆய்வில், 10-ம் வீட்டில் செவ்வாய் குலதீபக யோகத்தை உருவாக்குவதுடன் தீவிர தொழில்நுட்ப "
            "ஆற்றலைத் தருகிறது. சனியின் தொடர்பும் சேரும்போது இயந்திரவியல், சிவில் கட்டுமானம், சுரங்கம், "
            "பாதுகாப்புத் துறை மற்றும் கனரக தொழில்துறை பொறியியலில் ஜாதகர் புகழ்பெறுவார்."
        ),
        astrological_principle_en="Mars and Saturn in association with 10th house score decisively for core engineering professions.",
        astrological_principle_ta="செவ்வாய் மற்றும் சனி 10-ம் வீட்டில் இணைவது கனரக இயந்திரவியல் மற்றும் சிவில் பொறியியலைக் குறிக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, R.C. Sharma, pp. 56-65",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Prioritize industrial safety protocols and harness physical stamina in constructive projects.",
        remedy_ta="பணிபுரியும் இடங்களில் பாதுகாப்பு விதிகளை முறையாகப் பின்பற்றி உற்பத்தியைப் பெருக்கவும்.",
        sources=["Advanced Techniques of Astrological Predictions - R.C. Sharma (pp. 56-65)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-TECH-03",
        version=1,
        name_en="Jupiter-Venus Dominance on 10th: Humanities, Finance, Law & Administration",
        name_ta="10-ம் வீட்டில் குரு-சுக்கிர ஆதிக்கம்: நிதி, சட்டம், மனிதவளம் மற்றும் நிர்வாகம்",
        category_slug="career_profession",
        subcategory="career_field",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Jupiter",
            "houses": [10],
            "chart": "d1",
        },
        interpretation_en=(
            "Under R.C. Sharma's scoring system, Jupiter contributes a positive score (+2), pulling the career "
            "trajectory decisively into non-technical spheres. The native excels in jurisprudence, banking, "
            "corporate finance, education, advisory consulting, diplomacy, public policy, or creative humanities."
        ),
        interpretation_ta=(
            "ஆர்.சி. சர்மாவின் விதிப்படி, 10-ம் வீட்டில் குரு அமைவது தொழில்நுட்பம் சாராத உயர் துறைகளைக் குறிக்கும். "
            "நீதித்துறை, வங்கி மற்றும் நிதி மேலாண்மை, கல்வி, தணிக்கை, மனிதவள மேம்பாடு மற்றும் அரசு ஆலோசகர் "
            "போன்ற கெளரவமிக்க துறைகளில் சாதனை படைக்க வழிவகுக்கும்."
        ),
        astrological_principle_en="Jupiter on 10th yields a positive score (+2), directing the intellect toward finance, law, and education.",
        astrological_principle_ta="10-ம் வீட்டில் குரு அமைவது நிதி, சட்டம் மற்றும் கல்வித் துறைகளில் மேன்மையை உருவாக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, R.C. Sharma, pp. 66-72",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Cultivate wisdom-based mentorship and uphold supreme ethics in financial advisory.",
        remedy_ta="நீதி மற்றும் தர்ம நெறிகளைப் பின்பற்றி பிறருக்கு வழிகாட்டும் ஆலோசனைகளை வழங்கவும்.",
        sources=["Advanced Techniques of Astrological Predictions - R.C. Sharma (pp. 66-72)"],
    ),

    # =======================================================================
    # 3. AUTHORS AND JOURNALISTS (COL. A.K. GOUR)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-AUTH-01",
        version=1,
        name_en="PAC Bond of 3rd and 5th with Mercury: Literary Genius & Authorship",
        name_ta="3, 5-ம் அதிபதிகளுடன் புதன் தொடர்பு: சிறந்த இலக்கிய மற்றும் எழுத்தாற்றல்",
        category_slug="education_intellect",
        subcategory="literary_creative",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Mercury",
            "houses": [3, 5],
            "chart": "d1",
        },
        interpretation_en=(
            "Col. A.K. Gour's research demonstrates that Position-Aspect-Conjunction (PAC) bonding involving "
            "the 3rd house (arms/writing/expression), 5th house (creative intellect), and Mercury generates "
            "distinguished literary talent. The native possesses eloquence, expressive clarity, and authorial "
            "instincts, capable of writing bestselling books, research monographs, or columns."
        ),
        interpretation_ta=(
            "கர்னல் ஏ.கே. கெளரின் ஆய்வின்படி, 3-ம் வீடு (எழுத்து, கைகள்), 5-ம் வீடு (புத்தி கூர்மை) மற்றும் புதன் "
            "இணைவு அல்லது பார்வை பெறும்போது உயரிய இலக்கிய ஆற்றல் மலர்கிறது. ஜாதகர் சிறந்த எழுத்தாளராக, "
            "ஆராய்ச்சிக் கட்டுரைகள் மற்றும் புத்தகங்கள் படைப்பவராக சமூகத்தில் தனி முத்திரை பதிப்பார்."
        ),
        astrological_principle_en="PAC bonding between 3rd house, 5th house, and Mercury awakens prolific literary authorship.",
        astrological_principle_ta="3-ம் வீடு, 5-ம் வீடு மற்றும் புதனின் தொடர்பு சிறந்த படைப்பாற்றலையும் நூலாசிரியர் யோகத்தையும் தரும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Col. A.K. Gour, pp. 80-94",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Dedicate daily hours to structured writing and honor Saraswati through sharing knowledge.",
        remedy_ta="சரஸ்வதி தேவியை வணங்கி தினசரி எழுத்துப் பணியைத் தொய்வின்றித் தொடரவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Col. A.K. Gour (pp. 80-94)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-AUTH-02",
        version=1,
        name_en="Mars-Mercury Dynamic Link: Investigative Journalism & Critical Analysis",
        name_ta="செவ்வாய் - புதன் சேர்க்கை: புலனாய்வு இதழியல் மற்றும் கூர்மையான விமர்சனம்",
        category_slug="career_profession",
        subcategory="journalism_media",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_conjunction",
            "planets": ["Mars", "Mercury"],
            "same_sign_only": True,
            "chart": "d1",
        },
        interpretation_en=(
            "In Col. A.K. Gour's treatise, Mars represents ink and fiery assertion, while Mercury governs "
            "paper, newsprint, and communication. Their conjunction or mutual aspect produces rapid-fire "
            "journalistic flair, fearlessness in reporting, investigative rigor, sharp satire, and an ability "
            "to expose hidden truths through media and press publications."
        ),
        interpretation_ta=(
            "கர்னல் ஏ.கே. கெளரின் விதிப்படி, செவ்வாய் (மை, வீரியம்) மற்றும் புதன் (காகிதம், செய்தி) இணையும்போது "
            "அஞ்சாமை மிக்க புலனாய்வு இதழியல் யோகம் உருவாகிறது. அச்சு ஊடகம், தொலைக்காட்சி மற்றும் டிஜிட்டல் "
            "ஊடகங்களில் சமூக அநீதிகளைத் தட்டிக்கேட்கும் கூர்மையான விமர்சகராக விளங்குவர்."
        ),
        astrological_principle_en="Mars (ink) combined with Mercury (paper) activates vigorous journalistic and investigative publication.",
        astrological_principle_ta="செவ்வாயும் புதனும் இணைவது துணிச்சலான பத்திரிகை மற்றும் புலனாய்வு ஊடக யோகத்தைத் தரும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Col. A.K. Gour, pp. 86-91",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Verify facts meticulously and avoid haste or vitriolic polemics in public commentary.",
        remedy_ta="உண்மைகளை தீர விசாரித்து நேர்மையுடன் கூடிய சமநிலையான செய்திகளை வெளியிடவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Col. A.K. Gour (pp. 86-91)"],
    ),

    # =======================================================================
    # 4. MARITAL DISCORD & UPAPADA (SHUNNY NIGAM & SHIV RAJ SHARMA)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-MARR-01",
        version=1,
        name_en="Rule A (96% Empirical): Malefic Affliction on 2nd House from Upapada Lagna",
        name_ta="விதி A (96% உறுதி): உபபத லக்னத்திற்கு 2-ல் பாபக் கிரகங்கள் - தாம்பத்திய சிக்கல்",
        category_slug="marriage_relationships",
        subcategory="marital_harmony",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Saturn",
            "houses": [2],
            "chart": "d1",
        },
        interpretation_en=(
            "Shunny Nigam's landmark research across hundreds of documented charts demonstrated a 96% "
            "correlation between marital discord and malefic presence (Sun, Mars, Saturn, Rahu, Ketu) in or "
            "aspecting the 2nd house from Upapada Lagna (UL). This placement directly strikes at the sustenance "
            "of marriage, producing temperamental rifts, in-law conflict, or emotional estrangement unless "
            "counterbalanced by potent Jupiterian Grace."
        ),
        interpretation_ta=(
            "ஷன்னி நிகாமின் விரிவான கள ஆய்வில் 96% துல்லியமாக நிரூபிக்கப்பட்ட விதி: உபபத லக்னத்திற்கு (UL) "
            "2-ம் வீட்டில் சூரியன், செவ்வாய், சனி, ராகு அல்லது கேது அமைந்தாலோ அல்லது ஜெமினி பார்வை செலுத்தினாலோ "
            "தாம்பத்தியத்தில் கடுமையான கருத்து வேறுபாடுகள், குடும்ப அமைதியின்மை மற்றும் பிரிவினை சூழல் உருவாகலாம்."
        ),
        astrological_principle_en="Affliction to the 2nd house from Upapada Lagna impairs marital sustenance and durability.",
        astrological_principle_ta="உபபத லக்னத்திற்கு 2-ம் வீட்டில் பாபக் கிரகங்கள் அமைவது இல்லற வாழ்வின் நீடித்த அமைதியைப் பாதிக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Shunny Nigam, pp. 110-136",
        severity=SeverityLevel.UNFAVORABLE,
        remedy_en="Observe Upapada fasting on the day ruled by Upapada Lagna lord and worship Lakshmi-Narayana.",
        remedy_ta="உபபத லக்னாதிபதிக்குரிய கிழமைகளில் விரதமிருந்து லக்ஷ்மி நாராயணரை முறைப்படி வழிபடவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Shunny Nigam (pp. 110-136)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-MARR-02",
        version=1,
        name_en="Rule D (84% Empirical): Dusthana Lords Connected to 7th House or 7th Lord",
        name_ta="விதி D (84% உறுதி): 6, 8, 12-ம் அதிபதிகள் 7-ம் இடத்துடன் தொடர்பு - திருமண சவால்கள்",
        category_slug="marriage_relationships",
        subcategory="marital_harmony",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Mars",
            "houses": [7],
            "chart": "d1",
        },
        interpretation_en=(
            "In Shunny Nigam's empirical analysis, 84% of afflicted charts exhibited a strong nexus between "
            "dusthana lords (6th of litigation/disease, 8th of trauma/vulnerability, 12th of separation) and "
            "the 7th house or 7th lord. This configuration indicates marital turbulence, legal intervention, "
            "spousal health crises, or physical separation during corresponding dasha periods."
        ),
        interpretation_ta=(
            "ஷன்னி நிகாமின் ஆய்வில் 84% வழக்குகளில் காணப்பட்ட விதி: 6 (வழக்கு, கடன்), 8 (கண்டம், அவமானம்), "
            "12 (பிரிவு) ஆகிய மறைவு ஸ்தான அதிபதிகள் 7-ம் வீடு அல்லது 7-ம் அதிபதியுடன் இணையும்போது தாம்பத்தியத்தில் "
            "சட்டச் சிக்கல்கள், தற்காலிகப் பிரிவுகள் அல்லது வாழ்க்கைத்துணைக்கு ஆரோக்கியக் குறைவுகள் ஏற்படலாம்."
        ),
        astrological_principle_en="Association of 6th, 8th, or 12th lords with 7th house/lord introduces disputes and relational crises.",
        astrological_principle_ta="6, 8, 12-ம் அதிபதிகள் 7-ம் இடத்துடன் தொடர்பு கொள்வது தாம்பத்தியத்தில் பிரிவினைகளையும் வழக்குகளையும் உருவாக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Shunny Nigam, pp. 115-125",
        severity=SeverityLevel.UNFAVORABLE,
        remedy_en="Perform planetary shanti for dusthana lords and practice mutual empathy and conscious communication.",
        remedy_ta="மறைவு ஸ்தான அதிபதிகளுக்குப் பரிகாரம் செய்து, தம்பதியரிடையே விட்டுக்கொடுத்து வாழும் மனப்பக்குவத்தை வளர்க்கவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Shunny Nigam (pp. 115-125)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-MARR-03",
        version=1,
        name_en="Rule C (64% Empirical): Venus Afflicted in Rashi Chart",
        name_ta="விதி C (64% உறுதி): ராசிக் கட்டத்தில் சுக்கிரன் பீடிக்கப்படுதல் - களத்திர தோஷம்",
        category_slug="marriage_relationships",
        subcategory="marital_harmony",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Venus",
            "dignities": ["debilitated"],
            "chart": "d1",
        },
        interpretation_en=(
            "When Kalatrakaraka Venus is debilitated in Virgo, combust by the Sun, or hemmed in Papakartari "
            "Yoga by flanking malefics, Shunny Nigam observed a 64% incidence of domestic discord. The native "
            "experiences emotional dissatisfaction, delayed romance, or friction with their partner's expectations."
        ),
        interpretation_ta=(
            "களத்திரகாரகன் சுக்கிரன் கன்னியில் நீசம் பெற்றாலோ, சூரியனால் அஸ்தமனம் அடைந்தாலோ அல்லது இருபுறமும் "
            "பாபக் கிரகங்களால் சூழப்பட்டு பாபகர்த்தாரி யோகத்தில் சிக்கினாலோ 64% தாம்பத்திய மகிழ்ச்சி குறைகிறது. "
            "மனப்பொருத்தம் குறைதல் மற்றும் இல்லற வாழ்வில் அதிருப்தி ஏற்படக்கூடும்."
        ),
        astrological_principle_en="Debilitation or severe affliction to Kalatrakaraka Venus curtails conjugal contentment.",
        astrological_principle_ta="சுக்கிரன் நீசம் அல்லது பாபகர்த்தாரியில் அமைவது களத்திர சுகத்தைக் குறைக்கும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Shunny Nigam, pp. 120-130",
        severity=SeverityLevel.UNFAVORABLE,
        remedy_en="Recite Shukra Gayatri Mantra on Fridays and offer white fragrant flowers to Goddess Mahalakshmi.",
        remedy_ta="வெள்ளிக்கிழமைகளில் சுக்கிர காயத்ரி மந்திரம் ஜெபித்து ஸ்ரீ மகாலட்சுமிக்கு மல்லிகைப் பூ சாற்றி வழிபடவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Shunny Nigam (pp. 120-130)"],
    ),

    # =======================================================================
    # 5. DARAKARAKA TIMING (SUPRIYA JAGDISH)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-DK-01",
        version=1,
        name_en="Darakaraka Dasha: Pivotal Marriage Fruition & Relational Destiny",
        name_ta="தாரகாரகன் தசா காலம்: திருமண பிராப்தி மற்றும் உறவின் உச்சக்கட்டம்",
        category_slug="marriage_relationships",
        subcategory="marriage_timing",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Venus",
            "houses": [7],
            "chart": "d1",
        },
        interpretation_en=(
            "Supriya Jagdish's specialized research on Jaimini Darakaraka (planet with lowest longitude) "
            "reveals that its Vimshottari Mahadasha or Antardasha acts as a powerful catalyst for marriage. "
            "When Darakaraka is associated with benefics, the native enters wedlock with great joy; if afflicted, "
            "the same period triggers tests and pivotal marital decisions."
        ),
        interpretation_ta=(
            "சுப்ரியா ஜெகதீஷின் ஆய்வின்படி, மிகக் குறைந்த பாகை பெற்ற தாரகாரகன் (DK) கிரகத்தின் விம்சோத்தரி "
            "மகாதிசை அல்லது அந்தர்திசை நடைபெறும் காலத்தில் திருமண நிகழ்வுகள் மிக விரைவாக கைகூடுகின்றன. "
            "சுப பார்வையில் இருக்கும்போது இனிமையான இல்லறமும், பாப சேர்க்கையில் சோதனைகளும் ஏற்படும்."
        ),
        astrological_principle_en="Vimshottari periods of the Jaimini Darakaraka planet trigger critical marriage milestones.",
        astrological_principle_ta="ஜெமினி தாரகாரக கிரகத்தின் தசா-புத்திகள் திருமண பந்தத்தை உருவாக்குவதில் முதன்மை பங்கு வகிக்கின்றன.",
        source_reference="Advanced Techniques of Astrological Predictions, Supriya Jagdish, pp. 156-174",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Strengthen Darakaraka planetary vibrations through charitable deeds aligned with its nature.",
        remedy_ta="தாரகாரக கிரகத்திற்குரிய தானங்களைச் செய்து தாம்பத்திய ஒற்றுமையை பலப்படுத்தவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Supriya Jagdish (pp. 156-174)"],
    ),

    # =======================================================================
    # 6. SUCCESSFUL WOMEN IN LEADERSHIP (KUSUM VASHISHTHA)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-WOMEN-01",
        version=1,
        name_en="Sun & Mars Command in Female Charts: Political & Executive Power",
        name_ta="பெண்கள் ஜாதகத்தில் சூரியன் - செவ்வாய் ஆதிக்கம்: அரசியல் மற்றும் தலைமை அதிகாரம்",
        category_slug="career_profession",
        subcategory="leadership_fame",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_dignity",
            "planet": "Sun",
            "dignities": ["exalted", "own"],
            "chart": "d1",
        },
        interpretation_en=(
            "Kusum Vashishtha's historical research on high-achieving women (including prime ministers and corporate titans) "
            "proves that strong solar and martial dignity in Kendras or Trikonas bestows supreme administrative charisma, "
            "breakthrough leadership, resilience against societal bias, and commanding executive authority."
        ),
        interpretation_ta=(
            "குசும் வசிஷ்டாவின் வரலாற்று ஆய்வின்படி, பெண் ஜாதகங்களில் சூரியனும் செவ்வாயும் ஆட்சி, உச்சம் அல்லது "
            "கேந்திர-திரிகோணங்களில் பலம் பெற்றால், அவர்கள் நாடாளும் அரசியல் அதிகாரம், கார்ப்பரேட் தலைமைப் பதவிகள் "
            "மற்றும் சமூகத் தடைகளைத் தகர்த்து சரித்திரம் படைக்கும் ஆற்றலைப் பெறுவர்."
        ),
        astrological_principle_en="Exalted or strong Sun/Mars in female charts elevates native to high sovereign or administrative power.",
        astrological_principle_ta="பெண் ஜாதகத்தில் ஆட்சி உச்சம் பெற்ற சூரியன் செவ்வாய் உயரிய தலைமை மற்றும் ஆட்சி அதிகாரத்தை அருளும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Kusum Vashishtha, pp. 90-108",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Perform Surya Namaskar and cultivate compassionate assertiveness in decision-making.",
        remedy_ta="தினமும் சூரிய நமஸ்காரம் செய்து தலைமைப் பொறுப்புகளில் தீர்க்கமான முடிவுகளை எடுக்கவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Kusum Vashishtha (pp. 90-108)"],
    ),

    # =======================================================================
    # 7. ADVANCED KAAL SARPA & ASHTA-LAKSHMI (Z ANSARI)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-KAS-01",
        version=1,
        name_en="Savya Kaal Sarpa Yoga: Early Struggle Yielding Monumental Mid-Life Triumph",
        name_ta="ஸவ்ய கால சர்ப்ப யோகம்: ஆரம்ப காலப் போராட்டங்களுக்குப் பின் மாபெரும் உச்சம்",
        category_slug="special_yogas",
        subcategory="kaal_sarpa",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Rahu",
            "houses": [1],
            "chart": "d1",
        },
        interpretation_en=(
            "Z Ansari's nuanced paper on Kaal Sarpa Yoga establishes that in Savya configurations (planets hemmed "
            "moving towards Rahu's mouth), the early life up to age 28-32 is fraught with intense obstacles and "
            "psychological trials. However, once past this crucible, the native achieves unprecedented stature, "
            "unmatched fame, and enduring public distinction."
        ),
        interpretation_ta=(
            "இசட் அன்சாரியின் ஆய்வுப்படி, ஸவ்ய கால சர்ப்ப அமைப்பில் (கிரகங்கள் ராகுவின் முகத்தை நோக்கி நகர்தல்) "
            "32 வயது வரை தீவிர போராட்டங்களும் தடைகளும் ஏற்படும். ஆனால் அந்த காலகட்டத்தைக் கடந்தவுடன், "
            "ஜாதகர் எவராலும் எட்ட முடியாத புகழையும், மாபெரும் சமூக அந்தஸ்தையும் அடைந்து சாதனையாளராக விளங்குவார்."
        ),
        astrological_principle_en="Savya Kaal Sarpa Yoga imposes early trials that forge monumental resilience and later worldly conquest.",
        astrological_principle_ta="ஸவ்ய கால சர்ப்ப யோகம் இளமையில் போராட்டங்களையும், நடுத்தர வயதிற்குப் பின் அழியாத புகழையும் தரும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Z Ansari, pp. 1-28",
        severity=SeverityLevel.NEUTRAL,
        remedy_en="Worship Lord Shiva with Mahamrityunjaya Japa and maintain perseverance during early hurdles.",
        remedy_ta="சிவபெருமானை மகா மிருத்யுஞ்சய மந்திரத்தால் பூஜித்து விடாமுயற்சியுடன் உழைக்கவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Z Ansari (pp. 1-28)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-KAS-02",
        version=1,
        name_en="Ashta-Lakshmi Yoga: Rahu in 6th with Jupiter in Kendra: Supreme Wealth & Conquest",
        name_ta="அஷ்டலக்ஷ்மி யோகம்: 6-ல் ராகுவும் கேந்திரத்தில் குருவும் - எதிரிகளை வெல்லும் பெரும் செல்வம்",
        category_slug="wealth_finances",
        subcategory="dhan_yoga",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Rahu",
            "houses": [6],
            "chart": "d1",
        },
        interpretation_en=(
            "Z Ansari highlights this classical mitigation: when Rahu is placed in the Upachaya 6th house "
            "while Jupiter is seated in a Kendra, the dreaded Kaal Sarpa is completely converted into "
            "Ashta-Lakshmi Yoga. The native crushes all competitors, clears massive debts, and accumulates "
            "immense wealth, social honors, and perpetual prosperity."
        ),
        interpretation_ta=(
            "இசட் அன்சாரி விவரிக்கும் அரிய விதி: ராகு 6-ம் வீட்டில் அமைந்திருக்க, குரு கேந்திரத்தில் (1, 4, 7, 10) "
            "அமர்ந்தால் கால சர்ப்ப தோஷம் விலகி 'அஷ்டலக்ஷ்மி யோகமாக' மாறுகிறது. ஜாதகர் தனது அனைத்து எதிரிகளையும் "
            "வென்று, கடன்களை அடைத்து, அஷ்ட ஐஸ்வர்யங்களையும் பெற்று சமூகத்தில் சீமானாக வாழ்வார்."
        ),
        astrological_principle_en="Rahu in 6th with Jupiter in a Kendra dissolves Kaal Sarpa and transforms it into triumphant Ashta-Lakshmi Yoga.",
        astrological_principle_ta="6-ல் ராகுவும் கேந்திரத்தில் குருவும் அமைவது கால சர்ப்பத்தை நீக்கி அஷ்டலக்ஷ்மி யோகமாக மாற்றும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Z Ansari, pp. 18-24",
        severity=SeverityLevel.FAVORABLE,
        remedy_en="Express gratitude through annadhanam (food charity) and support underprivileged students.",
        remedy_ta="ஏழை எளியோருக்கு அன்னதானம் வழங்கி குருவின் பூரண அருளைப் பெறவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Z Ansari (pp. 18-24)"],
    ),

    # =======================================================================
    # 8. MEDICAL ASTROLOGY & MRITYU BHAGA (DR. K.S. CHARAK)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-MED-01",
        version=1,
        name_en="Mrityu Bhaga Degree Placement: Sudden Health Vulnerability & Caution",
        name_ta="மிருத்யு பாகை நிலை: திடீர் உடல்நலப் பாதிப்புகள் மற்றும் முன்னெச்சரிக்கை",
        category_slug="health_longevity",
        subcategory="disease_vulnerability",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Moon",
            "houses": [8],
            "chart": "d1",
        },
        interpretation_en=(
            "Dr. K.S. Charak's medical astrology research emphasizes that planets occupying their specific "
            "Mrityu Bhaga (fatal degree) in any sign represent dormant physiological flashpoints. During "
            "the dasha or adverse transits of that planet, sudden illness, accidents, or acute health "
            "emergencies manifest, requiring proactive diagnostic vigilance and spiritual protection."
        ),
        interpretation_ta=(
            "டாக்டர் கே.எஸ். சரக்கின் மருத்துவ ஜோதிட ஆய்வின்படி, ஒரு கிரகம் தனக்குரிய மிருத்யு பாகை பாகையில் "
            "அமையும்போது அந்த உறுப்பு சார்ந்த தீவிர உடல் உபாதைகள் ஏற்படலாம். அக்கிரகத்தின் தசா-புத்திகளில் திடீர் விபத்து "
            "அல்லது தீவிர நோய்கள் தலைதூக்க வாய்ப்புள்ளதால் முறையான மருத்துவ பரிசோதனைகளும் வழிபாடுகளும் அவசியம்."
        ),
        astrological_principle_en="Planetary occupation of exact Mrityu Bhaga degrees signals acute physiological vulnerability during dasha transitions.",
        astrological_principle_ta="மிருத்யு பாகை பாகையில் அமையும் கிரகம் தனது தசா காலத்தில் திடீர் உடல்நல பாதிப்புகளை ஏற்படுத்தும்.",
        source_reference="Advanced Techniques of Astrological Predictions, Dr. K.S. Charak, pp. 208-232",
        severity=SeverityLevel.UNFAVORABLE,
        remedy_en="Recite Dhanvantari Stotram daily, maintain routine health check-ups, and avoid risky physical ventures.",
        remedy_ta="தன்வந்திரி ஸ்தோத்திரம் ஜெபித்து, முறையான மருத்துவ ஆலோசனைகளையும் சீரான உணவு முறையையும் பின்பற்றவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Dr. K.S. Charak (pp. 208-232)"],
    ),

    AstrologicalRuleDefinition(
        rule_id="RULE-KNRAO-MED-02",
        version=1,
        name_en="Retrograde Benefic in Kendra: Delayed Cure & Healing Complications",
        name_ta="கேந்திரத்தில் வக்ர சுப கிரகம்: நோய் குணமாக தாமதம் மற்றும் மருத்துவ சிக்கல்கள்",
        category_slug="health_longevity",
        subcategory="recovery_prognosis",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house_placement",
            "planet": "Jupiter",
            "houses": [1, 4, 7, 10],
            "chart": "d1",
        },
        interpretation_en=(
            "Dr. K.S. Charak discovered that natural benefics (Jupiter, Venus) when retrograde in Kendras "
            "often fail to exercise their normal protective shield during acute illnesses. Instead, they can "
            "cause misdiagnosis, protracted convalescence, or atypical symptoms, requiring multiple medical opinions "
            "before finding effective remedies."
        ),
        interpretation_ta=(
            "டாக்டர் கே.எஸ். சரக்கின் விசேஷக் கண்டுபிடிப்பு: குரு அல்லது சுக்கிரன் கேந்திரங்களில் வக்ரம் பெற்றிருந்தால், "
            "அவை வழக்கமாக வழங்கும் ஆரோக்கிய பாதுகாப்பை உடனே வழங்க முடியாமல் போகலாம். தவறான மருத்துவ கணிப்புகள் "
            "அல்லது நோய் குணமாக நீண்ட காலம் பிடிப்பது போன்ற சூழல்கள் ஏற்படலாம்; இரண்டாவது மருத்துவ ஆலோசனை பெறுவது நல்லது."
        ),
        astrological_principle_en="Retrograde benefics in kendras fail to extend normal medical immunity during severe pathological onset.",
        astrological_principle_ta="கேந்திரங்களில் வக்ரம் பெற்ற சுப கிரகங்கள் நோய் காலத்தில் உடனடி ஆரோக்கிய பாதுகாப்பை வழங்கத் தயங்கலாம்.",
        source_reference="Advanced Techniques of Astrological Predictions, Dr. K.S. Charak, pp. 215-224",
        severity=SeverityLevel.NEUTRAL,
        remedy_en="Seek second medical opinions from experienced specialists and maintain therapeutic consistency.",
        remedy_ta="முக்கிய மருத்துவ முடிவுகளில் ஒன்றுக்கு மேற்பட்ட நிபுணர்களின் ஆலோசனையைப் பெறவும்.",
        sources=["Advanced Techniques of Astrological Predictions - Dr. K.S. Charak (pp. 215-224)"],
    ),
]
