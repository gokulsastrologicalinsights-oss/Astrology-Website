"""Deva Keralam (Chandra Kala Nadi) — Volume 3 Classical Rules Registry.

Authoritative codification of classical astrological rules from the sacred
treatise 'Deva Keralam (Chandra Kala Nadi)' compiled by Sage Venkatesa and
translated by R. Santhanam (Book III, Slokas 1998 to 5774).

Includes:
- Sage Garga's Kali Yuga Exaltation-Debilitation Balance Rule (Slokas 2187-2188)
- Grand Sovereign Yogas: Koorma, Matsya, Akhanda Samrajya, Rudrasana, Chamara
- Volume II Part I Classical Codifications: Mathanga, Malavya Cancellation, Bhikshu & Neechabhanga,
  Chhatra, Mani Pravada, Maha Pandita, Parijata, Nityanitya Karaka, Khanda Nirnaya,
  Aquarius Champakamsa, Gemini Indramsa, Ksheera Kumbha & Parashu Durga Remedies
- Divine Wisdom Yogas: Hari Hara Brahma, Avatara, Kubera, Lagnadhi, Kusuma
- Martial & Prosperity Yogas: Bheri, Sankha, Kahala, Cancer-Kubera Mars Exaltation
- Lunar Kriya & Avastha Manifestations: Susthira & Kampita Avasthas (Slokas 2592-2608)
- Ascendant Nadiamsa Aphorisms: Leo Kutila, Scorpio Sama, Taurus Arudha Kemadruma
- Progeny Karma-Vipaka Diagnostic & Remedial Science (Slokas 2073-2083)
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

DEVA_KERALAM_RULES: List[AstrologicalRuleDefinition] = [
    # =======================================================================
    # 1. SAGE GARGA'S KALI YUGA EXALTATION-DEBILITATION BALANCE RULE
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-GARGA-KALI-YUGA-01",
        version=1,
        name_en="Deva Keralam Sage Garga Kali Yuga Rule: Exalted Planets Ineffective Without Simultaneous Debility",
        name_ta="தேவ கேரளம் கார்க்கிய முனிவர் கலியுக விதி: சமகால நீச கிரகம் இன்றி உச்ச கிரகங்களின் ராஜயோக பலனின்மை",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_dignity",
                    "planet": "Sun",
                    "dignity": "exalted",
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Sun",
                    "chart": "d9",
                    "signs": [7],  # Debilitated in Navamsa (Libra)
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2187-2188 & 2170-2171) Revelation according to Sage Garga: In the Kali Yuga, even if "
            "a native possesses multiple exalted planets, Raja Yoga will NOT fructify unless there is a simultaneous "
            "debilitated planet or balancing downward dignity. Exalted Sun falling into Libra Navamsa cancels a hundred "
            "ordinary Raja Yogas and induces hardship and poverty unless balanced by religious devotion, holy Ganga baths, "
            "and worship of Lord Siva."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2187-2188, 2170-2171) கார்க்கிய முனிவரின் கலியுக ரகசிய விதி: கலியுகத்தில் ஒருவருக்கு "
            "மூன்று கிரகங்கள் உச்சம் பெற்றிருந்தாலும், மற்றொரு கிரகம் சமகாலத்தில் நீசம் பெறாவிடில் ராஜயோகம் பலன் தராது. "
            "இராசியில் உச்சம் பெற்ற சூரியன் நவாம்சத்தில் நீசம் (துலாம்) அடைந்தால் நூறு ராஜயோகங்களும் செயலற்று போய் வறுமை "
            "உண்டாகும். இதற்கு பரிகாரமாக கங்கா ஸ்நானமும் சிவ வழிபாடும் கட்டாயம் செய்ய வேண்டும்."
        ),
        astrological_principle_en="Sage Garga's Kali Yuga Law: Perfect polar balance between Uccha (exaltation) and Neecha (debilitation) is mandatory for sustainable material elevation.",
        astrological_principle_ta="கலியுகத்தில் உச்சத்தின் ஆணவமும் கர்மமும் நீசத்தின் பணிவு மற்றும் சமநிலையோடு இணையும் போதே நிலைத்த யோகம் உண்டாகும்.",
        source_reference="Deva Keralam Book III, Slokas 2170-2171 & 2187-2188 (Sage Garga & Achyuta of Kerala)",
        limitations_en="Mitigated when another planet is debilitated in D1 or when native engages in sacred pilgrimage and Siva worship.",
        limitations_ta="இராசிச் சக்கரத்தில் ஏதேனும் ஒரு கிரகம் நீசம் பெற்றிருந்தாலோ அல்லது சிவபக்தி பூண்டிருந்தாலோ தோஷம் நிவர்த்தியாகும்.",
        severity=SeverityLevel.MIXED,
    ),

    # =======================================================================
    # 2. KOORMA YOGA (TYPE A & TYPE B)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KOORMA-YOGA-01",
        version=1,
        name_en="Deva Keralam Koorma Yoga Type A: Sovereign Immobility, Unshakeable Prosperity & Renown",
        name_ta="தேவ கேரளம் கூர்ம யோகம் (வகை A): அசைக்க முடியாத ஆட்சி அதிகாரம், நிலையான பெருஞ்செல்வம் & நற்புகழ்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [3, 11],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [9, 12],  # Sagittarius or Pisces (own sign)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5518-5524) Sovereign Koorma Yoga: When Jupiter occupies his own sign in the 3rd or 11th "
            "house while the Lagna lord (or Venus for Libra ascendants) is dignified in the 11th house, the sacred Koorma "
            "(Tortoise Avatar) Yoga is formed. The native commands immovable sovereignty, immense patience, boundless "
            "philanthropy, and fame that withstands the tests of time like the cosmic tortoise supporting Mount Mandara."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5518-5524) கூர்ம யோகம்: குரு பகவான் தனது சொந்த வீடான தனுசு அல்லது மீனத்தில் 3 அல்லது 11-ஆம் "
            "இடத்திலும், லக்னாதிபதி (அல்லது சுக்கிரன்) 11-ஆம் இடத்திலும் அமர்வது மகா கூர்ம யோகமாகும். மந்தார மலையைத் தாங்கிய "
            "கூர்ம அவதாரம் போல் ஜாதகர் அசைக்க முடியாத சாம்ராஜ்ய பலம், எல்லையற்ற பொறுமை, தர்ம சிந்தனை மற்றும் அழியாத உலகப் "
            "புகழைப் பெறுவார்."
        ),
        astrological_principle_en="Jupiter's swakshetra dignity in Upachayas combined with 11th house gains produces unshakeable structural endurance.",
        astrological_principle_ta="உபசய ஸ்தானங்களில் ஆட்சி பெற்ற குருவும் 11-ல் நின்ற சுப லக்னாதிபதியும் பாறை போன்ற நிலைத்த வெற்றியையும் நீடித்த செல்வத்தையும் அளிக்கின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 5518-5519 & 5520-5524",
        limitations_en="Must not be afflicted by Rahu-Ketu axis across the 5th/11th houses.",
        limitations_ta="5/11 அச்சில் ராகு-கேதுவின் கடுமையான சேர்க்கை இல்லாத போது யோகம் பூரணமாக வெளிப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KOORMA-YOGA-02",
        version=1,
        name_en="Deva Keralam Koorma Yoga Type B: Movable Lagna with Fixed Ascendant Lord Blessed by Benefics",
        name_ta="தேவ கேரளம் கூர்ம யோகம் (வகை B): சர லக்ன அதிபதி ஸ்திர ராசி-நவாம்சம் பெற்று சுக்கிர-குரு தொடர்பு",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [1, 4, 7, 10],  # Movable ascendants
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5518-5520) Classical Koorma Yoga Type B: When a movable sign (Aries, Cancer, Libra, Capricorn) "
            "ascends while Jupiter and Venus prominently occupy angular houses (Kendras), the dynamic initiative of the movable "
            "ascendant becomes anchored with tortoise-like resilience. The native achieves lifelong administrative authority, "
            "high societal patronage, and peaceful legacy."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5518-5520) கூர்ம யோகம் (வகை B): சர லக்னங்கள் (மேஷம், கடகம், துலாம், மகரம்) அமைந்து, "
            "கேந்திரங்களில் சுக்கிரனும் குருவும் வலிமையுடன் நிற்பது சர ராசியின் வேகத்திற்கு கூர்மத்தைப் போன்ற திடமான ஆதாரத்தை "
            "அளிக்கிறது. இதனால் ஜாதகர் நீடித்த அரசு பதவி, பெருஞ்செல்வம் மற்றும் சமூக மதிப்பைப் பெறுவார்."
        ),
        astrological_principle_en="Movable dynamic energy grounded by dual natural benefics in Kendras produces enduring stability.",
        astrological_principle_ta="சர லக்னத்தின் இயங்கு சக்தி கேந்திரத்து குரு-சுக்கிர சுப பலத்தால் உறுதிப்பட்டு நீடித்த புகழைத் தருகிறது.",
        source_reference="Deva Keralam Book III, Slokas 5518-5520",
        limitations_en="Combustion of Venus or retrogression of both planets reduces temporal velocity of results.",
        limitations_ta="சுக்கிரன் அஸ்தமனம் ஆகாமல் இருக்கும் போது பலன்கள் விரைவாக வந்தடையும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 3. MATSYA YOGA (OCEANIC WISDOM & SPIRITUAL RENOWN)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MATSYA-YOGA-01",
        version=1,
        name_en="Deva Keralam Matsya Yoga: Oceanic Intellect, Sacred Intuition & Religious Preeminence",
        name_ta="தேவ கேரளம் மச்ச யோகம்: கடல் போன்ற மெய்யறிவு, ஆன்மீக ஞானம் & மதபீட தலைமைத்துவம்",
        category_slug="spiritual_life",
        subcategory="spiritual_growth",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [5, 9],  # Trikonas
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Ketu",
                    "houses": [1, 9],  # Spiritual anchor
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5460-5470) Sacred Matsya Yoga: Benefic planets radiating from the trinal houses (5th and 9th) "
            "in harmony with Ketu generates the divine Matsya (Fish Incarnation) Yoga. The native plunges into the deepest oceans "
            "of wisdom, recovers ancient scriptural knowledge, possesses exceptional occult intuition, and lives a life of sacred "
            "purity and spotless moral character."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5460-5470) மச்ச யோகம்: திரிகோணங்களில் (5 மற்றும் 9) குரு போன்ற சுப கிரகங்கள் அமைந்து "
            "கேதுவின் ஆன்மீகத் தொடர்பு ஏற்படுவது மகா விஷ்ணுவின் மச்ச அவதார யோகமாகும். கடல் போன்ற ஆழமான சாஸ்திர ஞானம், மறைபொருள் "
            "நுண்ணறிவு, தெய்வ கடாட்சம் மற்றும் களங்கமற்ற தர்ம வாழ்வு இவருக்கு அமையும்."
        ),
        astrological_principle_en="Trikona benefics combined with Ketu's moksha karakatwa synthesize worldly intellect with transcendental insight.",
        astrological_principle_ta="திரிகோண சுப கிரகங்களும் மோட்ச காரகன் கேதுவும் இணைந்து உலகியல் அறிவையும் ஆன்ம ஞானத்தையும் ஒன்றிணைக்கின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 5460-5465 & 5470",
        limitations_en="Native may detach from worldly vanity; material greed is antithetical to this yoga's activation.",
        limitations_ta="உலகியல் பேராசைகளைத் தவிர்த்து தர்ம வழியில் நடக்கும் போது யோகம் பலமடங்கு பிரகாசிக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 4. AKHANDA SAMRAJYA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-AKHANDA-SAMRAJYA-01",
        version=1,
        name_en="Deva Keralam Akhanda Samrajya Yoga: Unbroken Imperial Eminence & Monumental Treasury",
        name_ta="தேவ கேரளம் அகண்ட சாம்ராஜ்ய யோகம்: தடையற்ற தலைமை ஆளுமை, மாபெரும் தன யோகம் & ஆதிக்க பலம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [2, 5, 11],  # Wealth houses
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [1, 4, 7, 10],  # Moon in Kendra
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5495-5505) Imperial Akhanda Samrajya Yoga: When Jupiter lords or occupies prime wealth houses "
            "(2nd, 5th, 11th) while the Moon is strongly placed in a Kendra, the native commands unbroken imperial fortune, "
            "widespread industrial or institutional lordship, and uninterrupted cash flow across their lifespan."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5495-5505) அகண்ட சாம்ராஜ்ய யோகம்: 2, 5, 11 ஆகிய தன ஸ்தானங்களில் வியாழன் வலுப்பெற்று, "
            "சந்திரன் கேந்திர ஸ்தானங்களில் அமர்வது அகண்ட சாம்ராஜ்ய யோகத்தை உண்டாக்குகிறது. ஜாதகர் தடையற்ற பெருஞ்செல்வம், "
            "உயர் அதிகார பதவி மற்றும் வாழ்நாள் முழுவதும் குறையாத தன லாபத்தை அனுபவிப்பார்."
        ),
        astrological_principle_en="Luminaries in angular positions supported by Jupiter's treasury lordship grant unbroken socio-economic dominion.",
        astrological_principle_ta="கேந்திரத்து சந்திரன் மற்றும் தன ஸ்தானத்து குருவின் யோகச் சேர்க்கை தடையற்ற செல்வ சாம்ராஜ்யத்தை உருவாக்குகிறது.",
        source_reference="Deva Keralam Book III, Slokas 5495-5505",
        limitations_en="Must not coincide with Kemadruma Yoga of the Moon without cancellation.",
        limitations_ta="சந்திரனுக்கு கேமத்துரும தோஷம் இல்லாத போது அல்லது பங்கமடைந்த போது இந்த யோகம் முழுமையாகச் செயல்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 5. RUDRASANA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-RUDRASANA-YOGA-01",
        version=1,
        name_en="Deva Keralam Rudrasana Yoga: Fierce Administrative Power & Karmic Crucible",
        name_ta="தேவ கேரளம் ருத்ராசன யோகம்: கடுமையான அதிகார ஆளுமை & தீவிர கர்ம சோதனைகளை வெல்லும் வீரியம்",
        category_slug="career_profession",
        subcategory="job_prospects",
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
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "houses": [1, 10],  # Lagna or 10th
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5475-5480 & 5530) Rudrasana Yoga: Venus conjoined Rahu while Mars dominates the Ascendant "
            "or 10th house creates the formidable Rudrasana (Seat of Rudra) Yoga. The native commands aggressive authority, "
            "confronts extreme institutional trials, survives fierce political or corporate conflicts, and attains commanding "
            "eminence through unyielding courage."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5475-5480, 5530) ருத்ராசன யோகம்: சுக்கிரனும் ராகுவும் இணைய, செவ்வாய் லக்னத்திலோ அல்லது "
            "10-ஆம் வீட்டிலோ அமர்வது ருத்ராசன யோகத்தை உருவாக்குகிறது. ஜாதகர் கடுமையான நிர்வாக அதிகாரம், எதற்கும் அஞ்சாத நெஞ்சம் "
            "மற்றும் தீவிர அரசியல் அல்லது தொழில் போராட்டங்களை வென்று உச்ச நிலையை அடைவார்."
        ),
        astrological_principle_en="Venus-Rahu desire ambition propelled by Mars's angular martial vigor triggers intense karmic tests leading to commanding authority.",
        astrological_principle_ta="சுக்கிரன்-ராகுவின் அதீத பேரார்வமும் செவ்வாயின் போர்க்குணமும் இணைந்து சோதனைகளைத் தாண்டிய பெரும் ஆளுமையை அளிக்கின்றன.",
        source_reference="Deva Keralam Book III, Slokas 5475-5480 & 5530",
        limitations_en="Marital turbulence and sudden controversies require worship of Lord Shiva / Rudrabhishekam.",
        limitations_ta="குடும்ப வாழ்வில் அமைதிக்கும் சர்ச்சைகள் நீங்கவும் ருத்ராபிஷேகமும் சிவ வழிபாடும் அவசியம்.",
        severity=SeverityLevel.MIXED,
    ),

    # =======================================================================
    # 6. HARI HARA BRAHMA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-HARI-HARA-BRAHMA-01",
        version=1,
        name_en="Deva Keralam Hari Hara Brahma Yoga: Divine Trinity Blessing, Vedic Mastery & Spotless Fame",
        name_ta="தேவ கேரளம் ஹரி ஹர பிரம்ம யோகம்: மும்மூர்த்திகளின் திருவருள், வேத ஞானம் & களங்கமற்ற உலகப் புகழ்",
        category_slug="spiritual_life",
        subcategory="spiritual_growth",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 2, 4, 5, 7, 9, 10, 11],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mercury",
                    "houses": [2, 12],  # Flanking houses
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5420-5425) Trinity Yoga: Benefic planets (Jupiter, Venus, Mercury) harmoniously positioned "
            "in angular, trinal, and flanking positions from the Lagna generate Hari Hara Brahma Yoga. The native is endowed "
            "with Vedic erudition, truthful speech, spotless philanthropy, and enjoys the continuous grace of the cosmic preservers."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5420-5425) ஹரி ஹர பிரம்ம யோகம்: குரு, சுக்கிரன், புதன் ஆகிய இயற்கை சுப கிரகங்கள் லக்னத்திற்கும் "
            "கேந்திர-திரிகோணங்களுக்கும் சுப அமைப்பில் நிற்பது மும்மூர்த்திகளின் ஆசி பெற்ற உன்னத யோகமாகும். ஜாதகர் சத்திய வாக்கு, "
            "வேத சாஸ்திர தேர்ச்சி, அறநெறி வாழ்வு மற்றும் சகல நன்மைகளையும் பெறுவார்."
        ),
        astrological_principle_en="Triple natural benefics enveloping key pivot houses form an impenetrable karmic shield of sattvic grace.",
        astrological_principle_ta="முப்பெரும் சுப கிரகங்கள் கேந்திரங்களிலும் தன ஸ்தானங்களிலும் அமர்ந்து தெய்வீக பாதுகாப்பையும் நற்புகழையும் அருள்கின்றன.",
        source_reference="Deva Keralam Book III, Slokas 5420-5425",
        limitations_en="Native must strictly uphold truthfulness to preserve the yogic potency.",
        limitations_ta="சத்திய வாக்கை எப்போதும் கடைப்பிடிப்பது இந்த யோகத்தின் முழு ஆற்றலைத் தக்கவைக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 7. AVATARA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-AVATARA-YOGA-01",
        version=1,
        name_en="Deva Keralam Avatara Yoga: Divine Aura, Mass Resonance & Philosophical Renown",
        name_ta="தேவ கேரளம் அவதார யோகம்: தெய்வீக ஒளி, மக்கள் செல்வாக்கு & சமூகத்தை மாற்றியமைக்கும் தத்துவ ஆளுமை",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_dignity",
                    "planet": "Saturn",
                    "dignity": "exalted",  # Libra Saturn
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5415-5419) Avatara Yoga: Jupiter and Venus occupying Kendras while Saturn is exalted (in Libra) "
            "creates the rare Avatara (Divine Incarnation) Yoga. The subject is revered by the masses, radiates philosophical "
            "authority, transforms societal paradigms, and leaves an indelible mark on history."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5415-5419) அவதார யோகம்: கேந்திரங்களில் குருவும் சுக்கிரனும் சுபமாக அமைய, சனி பகவான் துலாமில் "
            "உச்சம் பெற்று அமர்வது மகா அவதார யோகமாகும். ஜாதகர் தெய்வீக வசீகரமும், மக்கள் கூட்டத்தை வழிநடத்தும் ஆளுமையும், "
            "சமூக மாற்றத்தை உருவாக்கும் தத்துவ வலிமையும் கொண்டு விளங்குவார்."
        ),
        astrological_principle_en="Exalted Saturn (righteous karma/justice) harnessed by dual preceptor benefics (Jupiter-Venus) produces epoch-defining leadership.",
        astrological_principle_ta="நீதி தேவனான சனியின் உச்ச பலமும் இரு குருமார்களின் (வியாழன்-சுக்கிரன்) கேந்திர சுபமும் இணைந்து மகத்தான வழிகாட்டியை உருவாக்குகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 5415-5419",
        limitations_en="Requires strict discipline; egoism destroys the spiritual vibration of this placement.",
        limitations_ta="ஆணவமின்றி மக்கள் சேவையில் ஈடுபடும் போது இந்த யோகம் உலகப் புகழைத் தரும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 8. KUBERA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KUBERA-YOGA-01",
        version=1,
        name_en="Deva Keralam Kubera Yoga: Boundless Realized Riches Matching the Lord of Wealth",
        name_ta="தேவ கேரளம் குபேர யோகம்: அளப்பரிய தன திரட்சி & குபேர சம்பத்து போன்ற நிதி நிலைத்தன்மை",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [11],  # 11th house of gains
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [2],  # 2nd house of treasury
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5430-5435 & 2175-2180) Sacred Kubera Yoga: Jupiter occupying the 11th house of boundless gains "
            "while Venus guards the 2nd house of accumulated treasury forms Kubera Yoga. The native enjoys vast vaults of wealth, "
            "flawless financial liquidity, and blessings of Goddess Mahalakshmi throughout life."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5430-5435, 2175-2180) குபேர யோகம்: லாப ஸ்தானமான 11-ல் குருவும், தன ஸ்தானமான 2-ல் சுக்கிரனும் "
            "அமர்வது மகா குபேர யோகமாகும். ஜாதகர் தர்ம வழியிலான பெருஞ்செல்வம், தங்க-வைர ஆபரணங்கள், அசையா சொத்துக்கள் மற்றும் "
            "குபேரனைப் போன்ற நிதி ஆதிக்கத்தை அனுபவிப்பார்."
        ),
        astrological_principle_en="Direct polar resonance between 2nd house (Dhankara Venus) and 11th house (Labhakara Jupiter) produces maximum monetary accumulation.",
        astrological_principle_ta="2-ஆம் இடத்து சுக்கிரனும் 11-ஆம் இடத்து குருவும் ஒருவருக்கொருவர் எதிர்கொண்டு நிலையான தன விருத்தியை உருவாக்குகின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 5430-5435",
        limitations_en="A portion of income must be dedicated to public charities (Anna Dana / water tanks).",
        limitations_ta="வருவாயில் ஒரு பகுதியை அன்னதானத்திற்கும் நீர்நிலைப் பராமரிப்பிற்கும் தானம் செய்வது செல்வத்தை பன்மடங்காக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 9. LAGNADHI YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-LAGNADHI-YOGA-01",
        version=1,
        name_en="Deva Keralam Lagnadhi Yoga: Ministership, Pure Temperament & Victory Over Adversaries",
        name_ta="தேவ கேரளம் லக்னாதி யோகம்: அமைச்சரவை பதவி, களங்கமற்ற குணம் & எதிரிகளை வெல்லும் ஆளுமை",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [6, 7, 8],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [6, 7, 8],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2157-2158, 2210-2212, 4178-4182) Classical Lagnadhi Yoga: When prime natural benefics "
            "(Jupiter, Venus, and Mercury) occupy the 6th, 7th, and 8th houses from the Ascendant free from malefic combustion, "
            "Lagnadhi Yoga is activated. The native attains high ministerial advisory positions, commands respect from the sovereign, "
            "vanquishes all enemies without physical violence, and lives with pristine moral integrity."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2157-2158, 4178-4182) லக்னாதி யோகம்: லக்னத்திற்கு 6, 7, 8 ஆகிய இடங்களில் சுப கிரகங்களான குருவும் "
            "சுக்கிரனும் அமர்வது லக்னாதி யோகமாகும். ஜாதகர் உயர் அரசாங்க ஆலோசகர் அல்லது அமைச்சர் அந்தஸ்து, பழி பாவமற்ற நல்லொழுக்கம், "
            "எதிரிகளை வன்முறையின்றி வெல்லும் ராஜதந்திரம் மற்றும் தீர்க்காயுளைப் பெறுவார்."
        ),
        astrological_principle_en="Benefics subduing 6th (enemies) and 8th (vulnerabilities) from Lagna insulate the native from all existential hazards.",
        astrological_principle_ta="6 மற்றும் 8-ஆம் வீடுகளை சுப கிரகங்கள் ஆக்கிரமிக்கும் போது எதிரிகளும் நோய்களும் தாமாகவே அடங்கி விடுகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 2157-2158 & 4178-4182",
        limitations_en="Benefics should not be retrograde and conjoined with Mars or Rahu.",
        limitations_ta="சுப கிரகங்கள் ராகு-செவ்வாய் சேர்க்கையின்றி தனித்து நிற்கும் போது யோகம் மிகச் சிறந்த பலனைத் தரும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 10. KUSUMA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KUSUMA-YOGA-01",
        version=1,
        name_en="Deva Keralam Kusuma Yoga: Radiant Charm, Universal Belovedness & Regal Elevation",
        name_ta="தேவ கேரளம் குசும யோகம்: மலர் போன்ற வசீகரம், மக்கள் அன்பு & அரண்மனை போன்ற வாழ்க்கை வசதிகள்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Venus",
                    "signs": [2, 5, 8, 11],  # Fixed sign
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Saturn",
                    "houses": [10],  # Saturn in 10th
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2216-2220) Kusuma (Flower) Yoga: Venus posited in a fixed sign while Saturn firmly occupies "
            "the 10th house produces Kusuma Yoga. The native blossoms like a fragrant flower in society, enjoys magnetic personal "
            "charm, acquires royal conveyances, and attains respected authority in civic affairs."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2216-2220) குசும யோகம்: சுக்கிரன் ஸ்திர ராசிகளில் (ரிஷபம், சிம்மம், விருச்சிகம், கும்பம்) அமைய, "
            "சனி பகவான் 10-ஆம் வீட்டில் ஆட்சி அல்லது பலத்துடன் அமர்வது குசும யோகமாகும். மலர் போன்ற வசீகரம், சமூகத்தில் எல்லாராலும் "
            "விரும்பப்படும் குணம், சொகுசு வாகனங்கள் மற்றும் உயரிய நிர்வாக அந்தஸ்து கிட்டும்."
        ),
        astrological_principle_en="Fixed Venusian grace aligned with 10th house Saturnian civic duty creates universally cherished public authority.",
        astrological_principle_ta="ஸ்திர சுக்கிரனின் அழகுணர்ச்சியும் 10-ஆம் இடத்து சனியின் உழைப்பும் இணைந்து நன்மதிப்புமிக்க தலைமையை உருவாக்குகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 2216-2220",
        limitations_en="Affliction to Venus by Mars produces domestic restlessness.",
        limitations_ta="செவ்வாயின் அசுப சேர்க்கை இல்லாத போது இல்லறமும் தொழிலும் ஒருசேர சிறக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 11. BHERI YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-BHERI-YOGA-01",
        version=1,
        name_en="Deva Keralam Bheri Yoga: Resounding War Trumpet Renown, Courage & Long Life",
        name_ta="தேவ கேரளம் பேரி யோகம்: முரசு கொட்டும் பெரும்புகழ், அஞ்சா நெஞ்சம் & தீர்க்காயுள்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [9, 10, 11],  # 9th lord / strong Sun
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5440-5445) Bheri Yoga: When Jupiter and Venus command the angles (Kendras) while the 9th lord "
            "or Sun is powerfully placed in Upachaya/Dharma houses, Bheri (War Drum) Yoga resounds. The native's name echo like "
            "royal victory drums across far-off territories; they possess unshakeable courage, robust vitality, and a celebrated lineage."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5440-5445) பேரி யோகம்: கேந்திரங்களில் குருவும் சுக்கிரனும் பலம் பெற, பாக்கியாதிபதி அல்லது சூரியன் "
            "9, 10, 11 ஆகிய வீடுகளில் சுபமாக அமர்வது பேரி யோகமாகும். வெற்றி முரசு போல ஜாதகரின் புகழ் எங்கும் எதிரொலிக்கும். "
            "அஞ்சாத தைரியம், பூரண ஆயுள் மற்றும் பெருமைமிக்க வம்சம் அமையும்."
        ),
        astrological_principle_en="Kendra benefics combined with Dharma strength herald triumphant public renown.",
        astrological_principle_ta="கேந்திர சுபர்களும் பாக்கிய பலமும் இணைந்து வெற்றியை பறைசாற்றும் முரசு யோகத்தை அளிக்கின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 5440-5445",
        limitations_en="Pride must be bridled; respect towards preceptors is essential.",
        limitations_ta="பெரியவர்களையும் ஆசிரியர்களையும் மதித்து நடப்பது யோகத்தின் நற்பலனை நிலைநிறுத்தும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 12. SANKHA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-SANKHA-YOGA-01",
        version=1,
        name_en="Deva Keralam Sankha Yoga: Righteousness, Shastric Scholarship & Expansive Real Estate",
        name_ta="தேவ கேரளம் சங்க யோகம்: தர்ம சிந்தனை, சாஸ்திர ஞானம் & பரந்த நிலபுலன்கள்",
        category_slug="property_assets",
        subcategory="real_estate",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [5, 6],  # 5th or 6th lord
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],  # Kendra
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5438-5440) Sankha Yoga: When the lords of the 5th and 6th houses are in mutual Kendras with a "
            "dignified Lagna lord, sacred Sankha (Conch) Yoga is realized. The native is deeply devoted to righteous deeds, highly "
            "learned in sacred sciences, endowed with expansive real estate, and blessed with auspicious longevity."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5438-5440) சங்க யோகம்: 5 மற்றும் 6-ஆம் அதிபதிகள் பரஸ்பர கேந்திரங்களில் அமைய, சுக்கிரன் கேந்திரத்தில் "
            "வலுப்பெறுவது சங்க யோகமாகும். மகா விஷ்ணுவின் பாஞ்சசன்னிய சங்கம் போல் தூய்மையான தர்ம நெறி, சாஸ்திர பாண்டித்தியம், "
            "விவசாய மற்றும் குடியிருப்பு நிலங்களின் சேர்க்கை, மற்றும் நல்வாழ்வு உண்டாகும்."
        ),
        astrological_principle_en="Righteous integration of 5th house intellect with 6th house effort yields clean land assets and peace.",
        astrological_principle_ta="5-ஆம் இடத்து புண்ணியமும் 6-ஆம் இடத்து உழைப்பும் இணைந்து உன்னதமான பூமி யோகத்தை நல்குகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 5438-5440",
        limitations_en="Clean title deeds and ethical land transactions maintain the sacred sanctity of this yoga.",
        limitations_ta="நில ஆவணங்களை முறையாகவும் நேர்மையாகவும் பராமரிப்பது யோகத்தை வளர்க்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 13. KAHALA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KAHALA-YOGA-01",
        version=1,
        name_en="Deva Keralam Kahala Yoga: Large Enterprise Command, Noble Tenacity & Transport Fleet",
        name_ta="தேவ கேரளம் காஹள யோகம்: பெருநிறுவன தலைமைத்துவம், தளராத உறுதி & வாகன யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [4, 9],  # 4th and 9th resonance
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "houses": [1, 4, 7, 10],  # Kendra strength
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5436-5438) Kahala Yoga: When the lords of the 4th (vehicles/masses) and 9th (fortune/dharma) "
            "form mutual Kendra relationships while the Lagna lord is fortified, Kahala Yoga manifests. The native becomes the "
            "resolute commander of an army, enterprise, or corporate empire, endowed with fleets of conveyances and enduring wealth."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5436-5438) காஹள யோகம்: 4-ஆம் அதிபதியும் 9-ஆம் அதிபதியும் கேந்திரங்களில் பலம் பெற்று செவ்வாய் "
            "கேந்திரத்தில் நிற்பது காஹள யோகமாகும். ஜாதகர் அசைக்க முடியாத மன உறுதி, பெரும் படை அல்லது வர்த்தக சாம்ராஜ்ய தலைமை, "
            "வாகனங்களின் அணிவகுப்பு மற்றும் சமூக கௌரவத்தைப் பெறுவார்."
        ),
        astrological_principle_en="Conjunction of 4th house popular infrastructure with 9th house divine fortune creates corporate and military leadership.",
        astrological_principle_ta="4-ஆம் இடத்து மக்கள் பலமும் 9-ஆம் இடத்து பாக்கியமும் இணைந்து பெருநிறுவன ஆளுமையை உருவாக்குகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 5436-5438",
        limitations_en="Native must temper obstinacy with compassionate counsel.",
        limitations_ta="பிடிவாதத்தைக் குறைத்து மற்றவர்களின் நல்ல ஆலோசனைகளை ஏற்பது வெற்றியைத் தரும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 14. CHAMARA YOGA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-CHAMARA-YOGA-01",
        version=1,
        name_en="Deva Keralam Chamara Yoga: Royal Whisks of Honor, Aristocratic Brilliance & Kingly Rank",
        name_ta="தேவ கேரளம் சாமர யோகம்: சாமரம் வீசப்படும் அரச கௌரவம், பேரறிஞர் சிறப்பு & தலைமைப் பதவி",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 7, 9, 10],  # Aspecting or occupying
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_dignity",
                    "planet": "Sun",
                    "dignity": "exalted",  # Aries Sun in Kendra/Trikona
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 5505-5510) Chamara Yoga: When the exalted Ascendant lord (or Sun) occupies an angular house "
            "in direct harmonious aspect or conjunction with Jupiter, Chamara (Royal Whisk) Yoga unfolds. The native is attended "
            "by symbols of state honor, master of numerous disciplines, eloquent orator, and celebrated as an advisor to rulers."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 5505-5510) சாமர யோகம்: உச்சம் பெற்ற லக்னாதிபதி (அல்லது சூரியன்) கேந்திரத்தில் அமைய, "
            "குரு பகவானின் சுபப் பார்வை பெறுவது சாமர யோகமாகும். அரசவையில் சாமரம் வீசி கௌரவிக்கப்படும் அரச போகம், பன்மொழி "
            "புலமை, வசீகரமான மேடைப் பேச்சு மற்றும் உயரிய தலைமைப் பதவி கிட்டும்."
        ),
        astrological_principle_en="Exalted royal karaka aspected by Devaguru Jupiter grants ceremonial state honors.",
        astrological_principle_ta="உச்சம் பெற்ற சூரியனை தேவகுருவான வியாழன் பார்க்கும் போது சாமர யோகம் என்ற அரச கௌரவம் உண்டாகிறது.",
        source_reference="Deva Keralam Book III, Slokas 5505-5510",
        limitations_en="Must not be afflicted by combust Mercury or Gulika in the 10th house.",
        limitations_ta="10-ஆம் இடத்தில் குளிகன் சேர்க்கையின்றி இருக்கும் போது யோகம் தடையின்றி இயங்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 15. KEMADRUMA YOGA CANCELLATION VIA EXALTED TAURUS MOON IN ARUDHA LAGNA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KEMADRUMA-AL-TAURUS-01",
        version=1,
        name_en="Deva Keralam Kemadruma Cancellation: Exalted Taurus Moon in Arudha Lagna Yielding Monumental Wealth",
        name_ta="தேவ கேரளம் கேமத்துரும பங்கம்: ஆருட லக்னத்தில் உச்ச சந்திரன் - பெருஞ்செல்வம் & வாகன யோகம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Moon",
                    "signs": [2],  # Exalted in Taurus
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [8],  # 8th from Taurus (Sagittarius)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2166-2169) Sacred Reversal Principle: While Moon conjoined or aspected by Rahu with malefics "
            "in 8th from Arudha Lagna normally triggers penury, if the Arudha Lagna falls in Taurus with the exalted Moon and "
            "Jupiter simultaneously occupies Sagittarius (8th from AL / own sign), the Kemadruma curse is totally inverted into "
            "monumental riches, vast landed estates, royal robes, and luxury carriages."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2166-2169) கேமத்துரும விசேஷ நிவர்த்தி விதி: ஆருட லக்னம் ரிஷபமாகி அங்கு சந்திரன் உச்சம் பெற, "
            "குரு பகவான் தனுசில் (ஆருடத்திற்கு 8-ல் ஆட்சி) நிற்பது கேமத்துரும தோஷத்தை அடியோடு நீக்குகிறது. இதனால் தரித்திரம் நீங்கி "
            "அரசாங்க கௌரவம், பட்டாடைகள், குதிரை-யானை போன்ற சொகுசு வாகனங்கள் மற்றும் மாபெரும் நில உடைமைகள் சேரும்."
        ),
        astrological_principle_en="Exalted Moon anchoring Arudha Lagna with Jupiter swakshetra in 8th converts adversity into hidden reserves of liquid prosperity.",
        astrological_principle_ta="ஆருடத்தில் உச்சம் பெற்ற சந்திரனும் தனுசு ஆட்சி குருவும் இணைந்து வறுமை தோஷத்தை பெருஞ்செல்வமாக மாற்றுகின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 2166-2169",
        limitations_en="Native must not hoard wealth unethically; charity preserves this rare inversion.",
        limitations_ta="தான தர்மங்களை தவறாமல் செய்து வந்தால் செல்வம் பல தலைமுறைகளுக்கு நிலைத்து நிற்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 16. CHANDRA KRIYA: SUSTHIRA AVASTHA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-CHANDRA-SUSTHIRA-01",
        version=1,
        name_en="Deva Keralam Chandra Susthira Avastha: Unshakeable Enterprise & Guaranteed Success",
        name_ta="தேவ கேரளம் சந்திர சுஸ்திர அவஸ்தை: அசைக்க முடியாத ஸ்திரத்தன்மை & காரிய சித்தி",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Moon",
                    "signs": [2, 5, 8, 11],  # Fixed signs
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 7, 10],  # Kendra aspect
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2593 & 2605) Chandra Susthira Avastha: When the Moon occupies a fixed sign (Taurus, Leo, "
            "Scorpio, Aquarius) in mutual relationship with the Lagna lord and receiving benefic aspects, the Moon enters the "
            "Susthira (Rock-Firm) State. In all queries, business initiatives, and life undertakings, sure triumph and enduring "
            "stability are granted."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2593, 2605) சந்திர சுஸ்திர அவஸ்தை: சந்திரன் ஸ்திர ராசிகளில் (ரிஷபம், சிம்மம், விருச்சிகம், கும்பம்) "
            "அமர்ந்து குருவின் சுபப் பார்வை பெறுவது சுஸ்திர அவஸ்தையாகும். தொட்ட காரியங்கள் யாவும் தடையின்றி வெற்றி பெறும். "
            "தொழிலில் அசைக்க முடியாத நிலைத்தன்மையும் வாழ்நாள் வெற்றியும் உண்டாகும்."
        ),
        astrological_principle_en="Fixed lunar foundation aspected by natural benefics creates an immovable psychological and material bedrock.",
        astrological_principle_ta="ஸ்திர ராசி சந்திரனும் குருவின் பார்வையும் இணைந்து எத்தகைய புயலிலும் அசையாத மனோபலத்தையும் காரிய வெற்றியையும் தருகின்றன.",
        source_reference="Deva Keralam Book III, Slokas 2593 & 2605",
        limitations_en="Must not be afflicted by Mars conjunction without benefic relief.",
        limitations_ta="செவ்வாயின் தீய சேர்க்கை இல்லாத போது இந்த காரிய சித்தி யோகம் முழுமையாக வெளிப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 17. CHANDRA KRIYA: KAMPITA AVASTHA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-CHANDRA-KAMPITA-01",
        version=1,
        name_en="Deva Keralam Chandra Kampita Avastha: Mental Agitation, Trembling & Captivity Fears",
        name_ta="தேவ கேரளம் சந்திர கம்பిత அவஸ்தை: மன நடுக்கம், அச்ச உணர்வு & காரியத் தடைகள்",
        category_slug="health_vitality",
        subcategory="chronic_diseases",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Moon",
                    "signs": [5],  # Leo (Sun's sign)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_conjunction",
                    "planets": ["Saturn", "Mars"],
                    "same_sign_only": True,
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Sloka 2594) Chandra Kampita Avastha: If Saturn conjoins Mars while the Moon is in the Sun's sign (Leo), "
            "the Moon enters the Kampita (Trembling/Panic) state. The native suffers from chronic anxiety, sudden panic attacks, "
            "irrational fears of confinement, and mental restraint. Propitiation of the Moon-God with silver vessel dana and "
            "recitation of Mrityunjaya Japa destroys this malefic terror."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகம் 2594) சந்திர கம்பిత அவஸ்தை: சூரியனின் வீடான சிம்மத்தில் சந்திரன் நிற்க, சனியும் செவ்வாயும் இணைவது "
            "சந்திரனை கம்பித (நடுக்கம்) அவஸ்தைக்கு உள்ளாக்குகிறது. ஜாதகர் தேவையற்ற பயம், மன உளைச்சல், சிறை பயம் மற்றும் பதற்றத்திற்கு "
            "ஆளாவார். இதற்கு பரிகாரமாக சந்திர பகவானுக்கு வெள்ளி தானமும் மகா மிருத்யுஞ்சய ஜபமும் செய்ய வேண்டும்."
        ),
        astrological_principle_en="Solar sign heat combined with Saturn-Mars malefic pincer compresses lunar emotional equilibrium into trembling panic.",
        astrological_principle_ta="சூரியனின் உஷ்ண ராசியில் சனியும் செவ்வாயும் சந்திரனைப் பாதிக்கும் போது மனோகாரகன் நிலை குலைந்து நடுக்கத்தை உருவாக்குகிறார்.",
        source_reference="Deva Keralam Book III, Sloka 2594",
        limitations_en="Mitigated when Jupiter casts its soothing trinal aspect onto the Moon.",
        limitations_ta="குருவின் 5 அல்லது 9-ஆம் பார்வை சந்திரனுக்கு கிடைத்தால் இந்த நடுக்கம் பெருமளவு குறையும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 18. LEO ASCENDANT: KUTILA NADIAMSA SOLAR RADIANCE
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-LEO-KUTILA-01",
        version=1,
        name_en="Deva Keralam Leo Lagna Kutila Nadiamsa: Sattvic Eloquence & Royal Paternal Inheritance",
        name_ta="தேவ கேரளம் சிம்ம லக்னம் குடில நாடியம்சம்: சாத்வீக வாக்குவன்மை & தந்தை வழி பூர்வீக சொத்து யோகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [5],  # Leo Lagna
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [1, 9, 10],  # Strong Sun
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 5, 9],  # Benefic aspect
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 1999-2012) Leo Kutila Nadiamsa: In Leo ascendant with Sun exalted or situated in Kendra/Trikona "
            "aspected by Jupiter, the native becomes pure Sattvic in temperament, remarkably eloquent in their mother tongue, "
            "skilful in learning and literature, and inherits substantial paternal prosperity."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 1999-2012) சிம்ம லக்னம் குடில நாடியம்சம்: சிம்ம லக்னத்தில் பிறந்து சூரியன் கேந்திர-திரிகோணங்களில் "
            "குருவின் பார்வையைப் பெறுவது ஜாதகருக்கு சாத்வீக குணத்தையும், தாய்மொழியில் சிறந்த கவிதை மற்றும் புலமையையும், "
            "தந்தையின் பூர்வீக சொத்துக்களையும் தடையின்றி அளிக்கும்."
        ),
        astrological_principle_en="Leo's royal fire tempered by Jupiter's sattvic glance transforms autocratic pride into benevolent wisdom and paternal fortune.",
        astrological_principle_ta="சிம்மத்து சூரியனை குரு பார்ப்பது ஆணவத்தை நீக்கி சாத்வீக அறிவையும் தந்தை வழி ஆசியையும் நல்குகிறது.",
        source_reference="Deva Keralam Book III, Slokas 1999-2012",
        limitations_en="If Mars aspects Sun without Jupiter, temperament becomes sharp and irascible.",
        limitations_ta="செவ்வாயின் பார்வை மட்டும் இருந்தால் முன் கோபமும் பிடிவாதமும் அதிகரிக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 19. SCORPIO ASCENDANT: SAMA NADIAMSA MASTER ASTROLOGER
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-SCORPIO-SAMA-ASTROLOGY-01",
        version=1,
        name_en="Deva Keralam Scorpio Lagna Sama Nadiamsa: Master Astrologer & Devotee of Lord Siva",
        name_ta="தேவ கேரளம் விருச்சிக லக்னம் சம நாடியம்சம்: ஜோதிட மேதை, சிவபக்தி & தீர்க்கமான வாக்குப்பலிதம்",
        category_slug="education_intellect",
        subcategory="higher_education",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [8],  # Scorpio Lagna
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [5],  # 5th in Pisces (exalted)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Saturn",
                    "houses": [5],  # Saturn in 5th with Venus
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2154-2156 & 2145-2148) Sama Nadiamsa Revelation: In Scorpio ascendant, when the 4th lord "
            "Saturn conjoins exalted Venus in the 5th house (Pisces), the native becomes an extraordinarily skilful astrologer "
            "and horoscopist. Blessed by Lord Siva through Panchakshari Mantra, they possess infallible prophetic intuition, "
            "philosophical depth, and holy speech."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2154-2156) விருச்சிக லக்னம் சம நாடியம்சம்: விருச்சிக லக்னத்திற்கு 4-ஆம் அதிபதி சனி 5-ஆம் வீடான "
            "மீனத்தில் உச்ச சுக்கிரனுடன் இணைவது ஜாதகரை இணையற்ற ஜோதிட மேதையாக மாற்றும். சிவபெருமானின் பஞ்சாட்சர மந்திர சித்தி, "
            "துல்லியமான பலன் கூறும் வாக்குப்பலிதம், மற்றும் உலகளாவிய நற்புகழ் இவருக்கு உண்டாகும்."
        ),
        astrological_principle_en="Exalted Venus (intuitive arts) conjoined Saturn (deep patience/ancient techniques) in the 5th house of intellect unlocks prophetic vision.",
        astrological_principle_ta="5-ஆம் இடத்து உச்ச சுக்கிரனும் சனியும் இணைந்து ஜோதிட சாஸ்திரத்தின் மிக நுண்ணிய ரகசியங்களை எளிதில் கணிக்கும் ஞானத்தை அளிக்கின்றனர்.",
        source_reference="Deva Keralam Book III, Slokas 2154-2156 & 2210-2214",
        limitations_en="Must maintain ritual cleanliness and practice daily Shiva Panchakshari recitation.",
        limitations_ta="தினமும் 'ஓம் நமச்சிவாய' பஞ்சாட்சர ஜெபம் செய்வது வாக்குப்பலிதத்தை மேலும் கூர்மையாக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 20. CANCER ASCENDANT: KUBERA NADIAMSA MARS EXALTATION
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-CANCER-KUBERA-MARS-01",
        version=1,
        name_en="Deva Keralam Cancer Lagna Kubera Nadiamsa: Exalted Mars in 7th Bestowing Royal Opulence",
        name_ta="தேவ கேரளம் கடக லக்னம் குபேர நாடியம்சம்: 7-ல் உச்ச செவ்வாய் அருளும் பெரும் தன வர்த்தக யோகம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [4],  # Cancer Lagna
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "houses": [7],  # Exalted in Capricorn in 7th
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Mars",
                    "signs": [10],  # Capricorn
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2275-2285 & Chandra Nadi) Kubera Nadiamsa: For Cancer ascendant, Mars (Yogakaraka lording "
            "5th and 10th) exalted in the 7th house (Capricorn) produces Kubera Nadiamsa Raja Yoga. The native ascends to "
            "monumental trade prosperity, royal state recognition, boundless assets in real estate and gold, and enjoys unbroken "
            "opulence."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2275-2285) கடக லக்னம் குபேர நாடியம்சம்: கடக லக்னத்திற்கு 5 மற்றும் 10-ஆம் அதிபதியான யோககாரகன் "
            "செவ்வாய் 7-ஆம் வீட்டில் மகரத்தில் உச்சம் பெறுவது குபேர நாடியம்ச ராஜயோகமாகும். ஜாதகர் சர்வதேச வர்த்தக வெற்றி, அரசாங்க ஆதரவு, "
            "அசையா சொத்துக்களின் குவியல் மற்றும் குபேரனைப் போன்ற அழியாத செல்வத்தை அடைவார்."
        ),
        astrological_principle_en="Cancer Yogakaraka Mars exalted in Kendrastana forms Ruchaka Mahapurusha Yoga intersecting Kubera Nadiamsa.",
        astrological_principle_ta="கடகத்திற்கு யோககாரகனான செவ்வாய் கேந்திரத்தில் உச்சம் பெற்று ருசக மகாபுருஷ யோகத்துடன் குபேர தன சம்பத்தை வழங்குகிறார்.",
        source_reference="Deva Keralam Book III, Slokas 2275-2285",
        limitations_en="Marital partnership requires understanding due to high-voltage martial energy in the 7th house.",
        limitations_ta="7-ஆம் இடத்து தீவிர செவ்வாய் ஆற்றலால் தம்பதியரிடையே பரஸ்பர விட்டுக்கொடுத்தல் அமைதி தரும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 21. PROGENY CURSE & SACRED REMEDIAL SCIENCE
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-PROGENY-CURSE-REMEDY-01",
        version=1,
        name_en="Deva Keralam Progeny Curse Diagnosis: Past-Life Brahmin Curse & Setu Snana / Harivamsa Remedy",
        name_ta="தேவ கேரளம் புத்திர சாப விதி: முற்பிறவி பிரம்ம சாபமும் சேது ஸ்நானம் / ஹரிவம்ச பரிகாரமும்",
        category_slug="children_family",
        subcategory="progeny_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [7],  # Libra Jupiter
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [12],  # Pisces Navamsa
                    "chart": "d9",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2073-2083) Sacred Karma-Vipaka Diagnosis: When Jupiter occupies Libra in D1 while begetting "
            "Pisces Navamsa in D9, the native carries the curse of a Brahmin from a previous life, causing severe delay or "
            "mortality of progeny. Remedial Injunction: Sacred dips at Setu (Rameswaram) for 21 days or 3 months, recitation "
            "or listening to the sacred Harivamsa Purana, and Pradosha Siva worship for 96 days totally neutralizes this blemish "
            "and blesses the native with virtuous sons."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2073-2083) புத்திர சாப கர்மவிபாக விதி: குரு பகவான் இராசியில் துலாமிலும் நவாம்சத்தில் மீனத்திலும் "
            "அமர்வது முற்பிறவி பிரம்ம சாபத்தை உணர்த்துகிறது. இதனால் வம்சவிருத்தியில் தீவிர தடைகளும் குழந்தை பிறப்பில் தாமதமும் "
            "உண்டாகும். பரிகாரம்: ராமேஸ்வரம் சேது கடலில் 21 நாட்கள் அல்லது 3 மாதங்கள் நீராடுதல், ஸ்ரீ ஹரிவம்ச புராணம் படித்தல்/கேட்டல், "
            "மற்றும் 96 நாட்கள் பிரதோஷ சிவ வழிபாடு ஆகியவை இந்த சாபத்தை நீக்கி நற்புத்திரர்களை அருளும்."
        ),
        astrological_principle_en="Jupiter's affliction in Venusian sign across D1-D9 mirrors ancestral spiritual debts requiring sacred water pilgrimage.",
        astrological_principle_ta="சுக்கிரனின் வீட்டில் நின்ற குரு நவாம்சத்தில் புஷ்கர அமைப்பில் இருந்தாலும் கர்ம வினையைத் தீர்க்க புனித தீர்த்த ஸ்நானம் அவசியமாகிறது.",
        source_reference="Deva Keralam Book III, Slokas 2073-2083",
        limitations_en="In the absence of these prescribed remedies, first wife may give birth only to female issues or face obstacles.",
        limitations_ta="பரிகாரங்களை முறைப்படி செய்யும் போது ஆண் குழந்தை பாக்கியமும் வம்ச விருத்தியும் தடையின்றி கிட்டும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 22. MERCURY IN HARINA NADIAMSA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MERCURY-HARINA-01",
        version=1,
        name_en="Deva Keralam Fixed Ascendant Harina Nadiamsa: Public Water Works, Temple Building & Sacred Charity",
        name_ta="தேவ கேரளம் ஸ்திர லக்னம் ஹரிண நாடியம்சம்: புதன் அமைப்பும் பொது நீர்நிலை, கோவில் திருப்பணி & தர்ம காரியங்கள்",
        category_slug="spiritual_life",
        subcategory="karmic_remedies",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [2, 5, 8, 11],  # Fixed ascendants
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mercury",
                    "houses": [1, 5, 9, 10, 11],  # Dignified Mercury
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [2],  # Moon in 2nd
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam (Slokas 2330-2354) Harina Nadiamsa Principle: In a fixed ascendant (Taurus, Leo, Scorpio, Aquarius), "
            "when Mercury is dignified in Kendra/Trikona while the Moon occupies the 2nd house, the native devotes extensive wealth "
            "to public welfare: excavating drinking water tanks, planting sacred public parks, donating lands to temples, and "
            "patronizing Vedic scholars."
        ),
        interpretation_ta=(
            "தேவ கேரளம் (ஸ்லோகங்கள் 2330-2354) ஹரிண நாடியம்சம்: ஸ்திர லக்னங்களில் (ரிஷபம், சிம்மம், விருச்சிகம், கும்பம்) புதன் "
            "கேந்திர-திரிகோணங்களில் அமைய, சந்திரன் 2-ல் அமர்வது ஜாதகரை பெரும் தர்ம சீலராக்கும். பொது மக்களின் பயன்பாட்டிற்கு குளங்கள் "
            "வெட்டுதல், நந்தவனங்கள் அமைத்தல், கோவில்களுக்கு நிலங்களை தானம் செய்தல் போன்ற உன்னத தர்ம காரியங்களில் ஈடுபடுவார்."
        ),
        astrological_principle_en="Fixed earth/water ascendant combined with Mercury's philanthropic intellect creates permanent community infrastructure.",
        astrological_principle_ta="ஸ்திர லக்னத்தின் நிலைத்தன்மையும் புதனின் நுண்ணறிவும் இணைந்து சமுதாயத்திற்குப் பயன்படும் நிலையான நீர்நிலைப் பணிகளைச் செய்விக்கின்றன.",
        source_reference="Deva Keralam Book III, Slokas 2330-2354",
        limitations_en="Native may face minor friction with siblings concerning ancestral property distribution.",
        limitations_ta="பூர்வீக சொத்து விவகாரங்களில் சகோதரர்களிடம் அமைதி காப்பது நலம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # VOLUME II PART I CLASSICAL RULES (SLOKAS 1 TO 579+)
    # =======================================================================

    # =======================================================================
    # 23. MATHANGA YOGA (IMPERIAL EMINENCE & CHARIOT-ELEPHANT ARMIES)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MATHANGA-YOGA-01",
        version=1,
        name_en="Deva Keralam Mathanga Yoga: Imperial Eminence, Chariot & Elephant Armies, Resounding Drum Fame",
        name_ta="தேவ கேரளம் மாதங்க யோகம்: சாம்ராஜ்ய அதிகாரம், யானை குதிரை வாகனங்கள் & முரசு கொட்டும் பெரும்புகழ்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 5, 7, 9, 10],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 9, 10, 11],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [1, 9, 10, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 22-25) Sovereign Mathanga Yoga: When lords of Kendras and Trikonas occupy the 10th, 7th, "
            "or mutual Kendras/Trikonas while natural benefics (Jupiter and Venus) and regal karakas are powerfully situated, Mathanga Yoga "
            "is produced. The sound of royal kettle-drums (Bheri) and trumpets echoes daily before the native's gates. The native commands "
            "royal conveyances (chariots, elephant escorts, and modern luxury fleets), broad territorial influence, and unshakeable prosperity."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 22-25) மாதங்க யோகம்: கேந்திர-திரிகோணாதிபதிகள் 10 அல்லது 7-ஆம் இடத்திலோ, "
            "அல்லது பரஸ்பர கேந்திர திரிகோணங்களிலோ நின்று லக்னாதிபதி பலம் பெற மாதங்க யோகம் உருவாகிறது. ஜாதகரின் வாசல் முன் பேரிகை "
            "முழக்கங்களும் மங்கள வாத்தியங்களும் சதா முழங்கும். யானைப்படை, குதிரைப்படை, ராஜ ரதங்கள் போன்ற சொகுசு வாகனங்கள், நிலபுலன்கள், "
            "அரச அந்தஸ்து மற்றும் நாடெங்கும் பரவும் பெரும் புகழை அடைவார்."
        ),
        astrological_principle_en="Harmonious linkage between 10th (Kha), 7th (Madana), and 9th/1st lords produces imperial governance and regal pomp.",
        astrological_principle_ta="10 மற்றும் 7-ஆம் அதிபதிகளுடன் 9-ஆம் அதிபதியும் லக்னாதிபதியும் கேந்திர திரிகோணங்களில் இணையும் போது சாம்ராஜ்ய யோகமும் ராஜ மரியாதையும் உண்டாகிறது.",
        source_reference="Deva Keralam Book II Part I, Slokas 22-25 (Sage Venkatesa)",
        limitations_en="Affliction by Rahu in the 10th house may introduce political scandals before final victory.",
        limitations_ta="10-ல் ராகுவின் கடுமையான தொடர்பு இருந்தால் அரசியலில் சவால்களை எதிர்கொண்ட பிறகே வெற்றி கிட்டும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 24. MALAVYA YOGA CANCELLATION NUANCE
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MALAVYA-CANCELLATION-01",
        version=1,
        name_en="Deva Keralam Malavya Yoga Cancellation Nuance: Obstruction & Delayed Fruits via Saturn or Jupiter Contact",
        name_ta="தேவ கேரளம் மாளவ்ய யோக பங்க விதி: சனி அல்லது குருவின் சேர்க்கையால் ஏற்படும் தடை, காலதாமதம் மற்றும் போராட்டம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Venus",
                    "signs": [2, 7, 12],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 7, 10],
                    "chart": "d1",
                },
                {
                    "condition_type": "compound",
                    "operator": "OR",
                    "conditions": [
                        {
                            "condition_type": "planet_conjunction",
                            "planets": ["Venus", "Saturn"],
                            "same_sign_only": True,
                            "chart": "d1",
                        },
                        {
                            "condition_type": "planet_conjunction",
                            "planets": ["Venus", "Jupiter"],
                            "same_sign_only": True,
                            "chart": "d1",
                        },
                    ],
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 26-27) Malavya Yoga Obstruction Rule: While Venus placed in Kendra in Taurus, Libra, "
            "or Pisces creates the exalted Pancha Mahapurusha Malavya Yoga, Sage Venkatesa reveals that conjunction or direct aspect with "
            "Saturn or Jupiter causes 'Malavya Yoga Bhanga'. The native will not receive instant effortless royalty; rather, immense struggle, "
            "delays, and friction will precede any fortune, and prosperity arrives only after overcoming prolonged hardships."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 26-27) மாளவ்ய யோக பங்க விதி: சுக்கிரன் கேந்திரத்தில் ஆட்சி/உச்சம் பெற்று "
            "பஞ்ச மகாபுருஷ யோகங்களில் ஒன்றான மாளவ்ய யோகத்தை உருவாக்கினாலும், அவருடன் சனியோ அல்லது குருவோ கூடினாலோ அல்லது பார்த்தாலோ "
            "யோகம் பங்கமடையும் (மாலவீயோக பங்கவான்). ராஜபோகங்கள் எளிதில் கிட்டாமல், கடும் போராட்டங்கள், தாமதங்கள் மற்றும் தடைகளைக் "
            "கடந்தே தாமதமாக செல்வம் சேரும்."
        ),
        astrological_principle_en="Saturn's restriction or Jupiter's philosophical detachment restricts Venusian luxury, requiring karmic endurance.",
        astrological_principle_ta="சுக்கிரனின் உலகியல் போகத்தை சனியின் கர்மக் கட்டுப்பாடோ அல்லது குருவின் விரக்தியோ மட்டுப்படுத்தி கடின உழைப்புக்கு பிறகே பலனைத் தரும்.",
        source_reference="Deva Keralam Book II Part I, Slokas 26-27",
        limitations_en="Fruits are achieved late in life (after age 36) through disciplined patience and persistent effort.",
        limitations_ta="36 வயதிற்குப் பிறகு பொறுமையும் விடாமுயற்சியும் கொண்டு செயல்பட்டால் தாமதமாக யோகம் நிலைக்கும்.",
        severity=SeverityLevel.MIXED,
    ),

    # =======================================================================
    # 25. BHIKSHU-DIGAMBARA REVERSAL
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-BHIKSHU-DIGAMBARA-01",
        version=1,
        name_en="Deva Keralam Bhikshu-Digambara Fall: Exaltation in D1 Dissolved by Debility in Navamsa",
        name_ta="தேவ கேரளம் பிக்ஷு யோகம்: ராசியில் உச்சம் பெற்ற கிரகம் நவாம்சத்தில் நீசம் அடைவதால் உண்டாகும் திடீர் வீழ்ச்சி",
        category_slug="wealth_finances",
        subcategory="financial_loss",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.BOTH,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Jupiter", "signs": [4], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Jupiter", "signs": [10], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Sun", "signs": [1], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Sun", "signs": [7], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Mars", "signs": [10], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Mars", "signs": [4], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Saturn", "signs": [7], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Saturn", "signs": [1], "chart": "d9"},
                    ],
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 28-29) Bhikshu-Digambara Fall: Even if born a royal prince or heir to immense fortune "
            "(Mahi-shatru-putro'pi), if key exalted planets in the Rasi chart (D1) occupy their debilitation sign in Navamsa (D9), the native "
            "faces sudden downward mobility, living like a mendicant or Digambara ascetic. Surface glory disappears during their dasa-bhukti periods."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 28-29) பிக்ஷு / திகாம்பர யோகம்: ராசிச் சக்கரத்தில் (D1) கிரகம் உச்சம் பெற்றிருந்தாலும் "
            "நவாம்சத்தில் (D9) நீசமடைந்தால், அவன் அரசனின் மகனாகப் பிறந்தாலும் ஆண்டியாக, பிச்சைக்காரனாக அல்லது நாடோடித் துறவியாக வறுமையில் வீழ்வான். "
            "அந்த கிரகத்தின் தசா புத்தி காலங்களில் வெளிப்படையான பெருமைகள் மறைந்து சோதனைகள் பெருகும்."
        ),
        astrological_principle_en="The Navamsa is the ultimate fruitional reality of the soul; D9 debility dissolves D1 surface exaltation.",
        astrological_principle_ta="நவாம்சம் என்பது கர்மாவின் உண்மைப் பலன்; நவாம்ச நீசம் ராசியின் உச்ச பலனைக் கரைத்து வறுமையை உண்டாக்கும்.",
        source_reference="Deva Keralam Book II Part I, Slokas 28-29",
        limitations_en="Neutralized if the dispositor of the Navamsa sign is strongly placed in Kendra in D1 or D9.",
        limitations_ta="நவாம்ச அதிபதி கேந்திரத்தில் பலம் பெற்றிருந்தால் இந்த தோஷத்தின் தீவிரம் பெருமளவு மட்டுப்படும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 26. NEECHABHANGA SOVEREIGN ASCENT
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-NEECHABHANGA-SOVEREIGN-01",
        version=1,
        name_en="Deva Keralam Neechabhanga Sovereign Ascent: D1 Debility Rising to Navamsa Exaltation",
        name_ta="தேவ கேரளம் நீசபங்க உன்னத யோகம்: ராசியில் நீசம் பெற்ற கிரகம் நவாம்சத்தில் உச்சம் பெற்று தரும் சாம்ராஜ்ய யோகம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.BOTH,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Jupiter", "signs": [10], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Jupiter", "signs": [4], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Sun", "signs": [7], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Sun", "signs": [1], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Mars", "signs": [4], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Mars", "signs": [10], "chart": "d9"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Saturn", "signs": [1], "chart": "d1"},
                        {"condition_type": "planet_sign", "planet": "Saturn", "signs": [7], "chart": "d9"},
                    ],
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 28-29) Sovereign Neechabhanga Ascent: When a planet debilitated in the Rasi chart (D1) "
            "attains exaltation in the Navamsa chart (D9), the sacred reversal of fortune takes place. Even if born in an impoverished home, "
            "the native rises with formidable determination to sovereign stature, widespread authority, and magnificent wealth."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 28-29) நீசபங்க உன்னத யோகம்: ராசிச் சக்கரத்தில் (D1) நீசம் பெற்ற கிரகம் "
            "நவாம்சத்தில் (D9) உச்சம் பெறும் போது விசேஷ யோகம் உண்டாகிறது. எளிய குடிலில் பிறந்தாலும் ஜாதகர் தளராத உழைப்பாலும் "
            "தெய்வ அனுகூலத்தாலும் உயர்ந்து அரசர் போன்ற அதிகாரத்தையும் பெருஞ்செல்வத்தையும் அடைவார்."
        ),
        astrological_principle_en="Navamsa exaltation completely cancels and transmutes Rasi debility into resilient enduring strength.",
        astrological_principle_ta="நவாம்ச உச்சமானது ராசியின் நீசக் கறையை முழுமையாகப் போக்கி நிலைத்த பெரும் யோகமாக மாற்றுகிறது.",
        source_reference="Deva Keralam Book II Part I, Slokas 28-29",
        limitations_en="Rise occurs primarily in the second half of life (after age 28-32).",
        limitations_ta="இந்த யோகத்தின் வளர்ச்சி 28-32 வயதிற்குப் பிறகே தீவிரமாக வெளிப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 27. CHHATRA YOGA (ROYAL CANOPY OF PROTECTION)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-CHHATRA-YOGA-01",
        version=1,
        name_en="Deva Keralam Chhatra Yoga: Royal Canopy of Protection, Oratorical Brilliance & Ministerial Stature",
        name_ta="தேவ கேரளம் சத்ர யோகம்: அரச பாதுகாப்புக் குடை (வெண்கொற்றக்குடை), மந்திரி ஆளுமை & சிவபக்தி",
        category_slug="career_profession",
        subcategory="leadership",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [2],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [9],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 5, 7, 9, 10],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 89-91) Sovereign Chhatra Yoga: When the Moon occupies the 2nd house, Venus is positioned "
            "in the 9th house (Bhagya), and Jupiter fortifies Kendras or Trikonas, Chhatra (Royal Parasol) Yoga is formed. The native is endowed "
            "with supreme oratorical prowess, noble lineage, aristocratic protection, and ministerial authority. Devoted to Lord Shiva in the "
            "second half of life, the native commands boundless vehicular comforts, land grants, and immense public respect."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 89-91) சத்ர யோகம் (வெண்கொற்றக்குடை யோகம்): 2-ல் சந்திரன் அமர, 9-ல் சுக்கிரன் அமைய, "
            "கேந்திர திரிகோணங்களில் குரு நின்றால் சத்ர யோகம் உண்டாகிறது. ஜாதகர் அரச பாதுகாப்புக் குடை நிழலில் வாழ்வது போல பாதுகாப்பும், "
            "விசேஷ வாக்கு வன்மையும், மந்திரி அந்தஸ்தும் பெறுவார். 40 வயதிற்கு மேல் சிவபாத பூஜை செய்து சகல ஐஸ்வர்யங்களையும் அடைவார்."
        ),
        astrological_principle_en="2nd house lunar sweetness coupled with 9th house Venusian fortune creates an unassailable aura of regal favor.",
        astrological_principle_ta="2-ல் நின்ற சந்திரனின் வாக்கும் 9-ல் நின்ற சுக்கிரனின் பாக்கியமும் இணைந்து அரச மரியாதையையும் பாதுகாப்பையும் தருகின்றன.",
        source_reference="Deva Keralam Book II Part I, Slokas 89-91",
        limitations_en="6th house Rahu may cause secret detractors who fail to penetrate the native's protective canopy.",
        limitations_ta="மறைமுக எதிர்ப்புகள் வந்தாலும் அரச ஆதரவு மற்றும் சிவ கடாட்சத்தால் அவை விலகிவிடும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 28. MANI PRAVADA YOGA (PEARL & CORAL GARLAND OF FORTUNE)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MANI-PRAVADA-01",
        version=1,
        name_en="Deva Keralam Mani Pravada Yoga: Pearl & Coral Garland of Alternating Benefics & Enemy-Quelling Strength",
        name_ta="தேவ கேரளம் மணி பிரவாள யோகம்: முத்து-பவள மாலை போன்ற தொடர் சுப நிலை, அரசு தலைமை & அஷ்ட ஐஸ்வர்யம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [2, 4, 5],
                    "chart": "d1",
                },
                {
                    "condition_type": "compound",
                    "operator": "OR",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Mars", "houses": [3], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Saturn", "houses": [3], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Sun", "houses": [3], "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [4, 5, 9],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 126-127) Mani Pravada Yoga: When Jupiter or natural benefics occupy the 2nd house, a malefic "
            "(Mars, Saturn, Sun) occupies the 3rd house (destroying competitors and providing unyielding bravery), and Venus graces the 4th, 5th, "
            "or 9th houses, the auspicious Mani Pravada (Gem-Coral Garland) Yoga is formed. The native enjoys unbroken prosperity, high governmental "
            "advisory power, and profound family happiness."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 126-127) மணி பிரவாள யோகம்: 2-ல் குரு போன்ற சுப கிரகம் நிற்க, 3-ல் செவ்வாய், சனி, சூரியன் "
            "போன்ற பாப கிரகம் நின்று எதிரிகளை வேரறுக்க, 4, 5 அல்லது 9-ஆம் வீடுகளில் சுக்கிரன் அமைய மணி பிரவாள யோகம் உண்டாகிறது. முத்துக்களும் "
            "பவளங்களும் கோர்த்த மாலை போல ஜாதகரின் வாழ்க்கை அலங்கரிக்கப்படும்; வறுமையின்றி தொடர் அரசு செல்வாக்கு கிட்டும்."
        ),
        astrological_principle_en="Upachaya 3rd house malefic suppression combined with 2nd, 4th, 5th benefic grace creates seamless prosperity.",
        astrological_principle_ta="3-ல் நின்ற பாபி எதிரிகளை அழிக்க, 2, 4, 5-ல் நின்ற சுபர்கள் அஷ்ட ஐஸ்வர்யங்களையும் கல்வி-வாகன சுகங்களையும் வழங்குகின்றனர்.",
        source_reference="Deva Keralam Book II Part I, Slokas 126-127",
        limitations_en="Combustion of 2nd house lord may cause minor dental or throat ailments in late life.",
        limitations_ta="2-ஆம் அதிபதி அஸ்தமனம் அடையாத போது யோகத்தின் முழு வீச்சு தடையின்றி வெளிப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 29. MAHA PANDITA YOGA (POLYMATHIC WISDOM & SOVEREIGN ADVISOR)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-MAHA-PANDITA-01",
        version=1,
        name_en="Deva Keralam Maha Pandita Yoga: Polymathic Intellect, Shastric Erudition & Sovereign Advisory Eminence",
        name_ta="தேவ கேரளம் மகா பண்டித யோகம்: சர்வ சாஸ்திர பாண்டித்யம், அரச ஆலோசகர் & தர்ம ஞானம்",
        category_slug="education_intellect",
        subcategory="intellect",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1],
                    "chart": "d1",
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Sun", "houses": [1, 5], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mercury", "houses": [1, 5], "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Sun", "Mercury"], "same_sign_only": True, "chart": "d1"},
                    ],
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 70-72) Maha Pandita Yoga: When Jupiter is placed in the Lagna, or Sun and Mercury are closely "
            "conjoined in the 1st or 5th house free from malefic aspect, Maha Pandita Yoga is produced. The native becomes an ocean of wisdom, "
            "revered by scholars and monarchs alike, celebrated for poetic genius, Vedic knowledge, and righteous judgment."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 70-72) மகா பண்டித யோகம்: குரு பகவான் லக்னத்தில் அமர்ந்தாலோ, அல்லது சூரியனும் "
            "புதனும் லக்னம் அல்லது 5-ஆம் வீட்டில் இணைந்து சுப பார்வை பெற்றாலோ மகா பண்டித யோகம் உண்டாகிறது. ஜாதகர் சகல சாஸ்திரங்களையும் உணர்ந்த "
            "பேரறிஞராகவும், அரசர்களால் போற்றப்படும் ஆலோசகராகவும், தர்ம நெறி தவறாத மேதையாகவும் விளங்குவார்."
        ),
        astrological_principle_en="Ascendant-fortified Jupiter or Budhaditya combines intellect (Buddhi) with divine consciousness (Guru).",
        astrological_principle_ta="லக்னத்தில் திகழும் குருவும் புதாதித்ய யோகமும் ஒரு மனிதனை உலகப் புகழ் பெற்ற அறிஞனாகவும் ஞானியாகவும் உயர்த்துகின்றன.",
        source_reference="Deva Keralam Book II Part I, Slokas 70-72",
        limitations_en="Native may exhibit unyielding intellectual pride if not balanced by devotional humility.",
        limitations_ta="ஆன்மீகப் பணிவும் குரு பக்தியும் பூண்டிருக்கும் போது ஞானம் முழுமையாகப் பிரகாசிக்கும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 30. PARIJATA YOGA (WISH-FULFILLING CELESTIAL TREE)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-PARIJATA-YOGA-01",
        version=1,
        name_en="Deva Keralam Parijata Yoga: Wish-Fulfilling Celestial Tree of Regal Fortune & Generational Wealth",
        name_ta="தேவ கேரளம் பாரிஜாத யோகம்: கற்பக விருட்சம் போன்ற ராஜயோகம், தூய சிந்தனை & தொடர் தன தான்ய லாபம்",
        category_slug="wealth_finances",
        subcategory="wealth_accumulation",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 5, 7, 9, 10],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 5, 7, 9, 10],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mercury",
                    "houses": [5, 9, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 314-315) Parijata Yoga: When the 5th house is graced by benefics, Venus and Jupiter occupy "
            "Kendras or Trikonas, and Mercury supports the trikonas or 11th house, the celestial Parijata Yoga is realized. Like the divine "
            "wish-granting Parijata tree, the native experiences spontaneous fulfillment of noble desires, virtuous progeny, royal favor, "
            "and generational wealth."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 314-315) பாரிஜாத யோகம்: 5-ஆம் வீட்டில் சுப கிரகம் நிற்க, சுக்கிரனும் குருவும் "
            "கேந்திர-திரிகோணங்களில் அமைய, புதன் பலம் பெற்றால் பாரிஜாத யோகம் உண்டாகிறது. தேவலோகத்துக் கற்பக விருட்சம் கேட்டதையெல்லாம் தருவது "
            "போல, ஜாதகர் நற்குழந்தைகள், தர்ம நெறி, அரச கௌரவம் மற்றும் தலைமுறை தலைமுறையாய் நிலைக்கும் செல்வத்தைப் பெறுவார்."
        ),
        astrological_principle_en="Trikona benefics conjoined with Venusian aesthetic grace produces inexhaustible auspicious karma.",
        astrological_principle_ta="பூர்வ புண்ணிய ஸ்தானமும் (5) பாக்கிய ஸ்தானமும் (9) சுக்கிரனுடன் இணையும் போது கேட்டதையெல்லாம் அருளும் உன்னத யோகம் மலர்கிறது.",
        source_reference="Deva Keralam Book II Part I, Slokas 314-315",
        limitations_en="Native should avoid speculative gambling to preserve the pristine nature of this sacred yoga.",
        limitations_ta="சூதாட்டம் மற்றும் முறையற்ற ஊக வர்த்தகங்களைத் தவிர்ப்பது யோகத்தை நிலைநிறுத்தும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 31. NITYANITYA KARAKA DOCTRINE
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-NITYANITYA-KARAKA-01",
        version=1,
        name_en="Deva Keralam Nityanitya Karaka Doctrine: Natural Karaka in Swakshetra Refutes Karako Bhava Nasaya",
        name_ta="தேவ கேரளம் நித்ய-அநித்ய காரக பாவ கோட்பாடு: காரகோ பாவ நாசாய விதியின் நிவர்த்தியும் சுப விருத்தியும்",
        category_slug="overall_nature",
        subcategory="temperament",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Jupiter", "signs": [9, 12], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Jupiter", "houses": [5, 9], "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Venus", "signs": [2, 7], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Venus", "houses": [7], "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Sun", "signs": [5], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Sun", "houses": [9, 10], "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "compound",
                    "operator": "AND",
                    "conditions": [
                        {"condition_type": "planet_sign", "planet": "Mars", "signs": [1, 8], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Mars", "houses": [3], "chart": "d1"},
                    ],
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 319-324) Nityanitya Karaka Shastric Revelation: Sage Venkatesa clarifies the ancient adage "
            "'Karako Bhava Nasaya' (a karaka in its own bhava destroys the bhava). When a natural significator (Nitya Karaka) occupies its own "
            "sign (Swakshetra) or exaltation sign within that bhava, it does NOT destroy the bhava; rather, it elevates that bhava to supreme strength "
            "and lasting flourishing (Swakshetre samsthite vriddhih syat)."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 319-324) நித்ய-அநித்ய காரக பாவ கோட்பாடு: 'காரகோ பாவ நாசாய' (காரகன் காரக வீட்டில் "
            "நின்றால் பாவம் அழியும்) என்ற பொது விதியை வேங்கடேச பண்டிதர் மறுபரிசீலனை செய்து விளக்குகிறார். ஒரு நித்ய காரக கிரகம் தனது சொந்த வீட்டிலோ "
            "அல்லது உச்ச வீட்டிலோ அந்த பாவகத்தில் அமையும் போது, பாவம் அழிவதற்குப் பதிலாக பன்மடங்கு சுப விருத்தியையே தரும் (ஸ்வக்ஷேத்ரே சம்ஸ்திதே விருத்திஹி)."
        ),
        astrological_principle_en="Swakshetra and exaltation dignities overpower natural bhava karakatwa friction, guaranteeing bhava prosperity.",
        astrological_principle_ta="ஆட்சி மற்றும் உச்ச பலம் பெற்ற காரக கிரகம் காரக பாவத்தை அழிக்காமல், மாறாக அந்த பாவத்தின் பலனை நிலைபெறச் செய்யும்.",
        source_reference="Deva Keralam Book II Part I, Slokas 319-324",
        limitations_en="Direct aspect of Rahu or debilitated malefic can reintroduce minor friction in the significator's portfolio.",
        limitations_ta="ராகுவின் கடுமையான பார்வை இல்லாத போது இந்த சுப விருத்தி பூரணமாக வெளிப்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 32. KHANDA NIRNAYA (LIFESPAN QUADRANT TIMING)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KHANDA-NIRNAYA-01",
        version=1,
        name_en="Deva Keralam Khanda Nirnaya: Dvitiya Khanda Prime Middle-Age Regal Elevation",
        name_ta="தேவ கேரளம் கண்ட நிர்ணய விதி: துவிதீய கண்டத்தில் (5 முதல் 8-ஆம் வீடுகள்) சுப கிரகங்களால் ஏற்படும் நடுப்பருவ ராஜ்யாபிஷேகம்",
        category_slug="career_profession",
        subcategory="job_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [5, 7, 9],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [5, 7, 9, 10, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Sloka 22, Khanda Nirnaya Section): Human life is partitioned into three 4-house quadrants: "
            "Prathama Khanda (Houses 1-4, youth), Dvitiya Khanda (Houses 5-8, middle age / 25-50), and Tritiya Khanda (Houses 9-12, elder years / 50+). "
            "When exalted or benefic planets fortify the Dvitiya Khanda, the native experiences supreme Rajyabhisheka (executive crowning, major career "
            "breakthroughs, and massive wealth) during the prime middle phase of life."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகம் 22) கண்ட நிர்ணய விதி: மனித ஆயுள் 4 வீடுகள் கொண்ட 3 கண்டங்களாகப் பிரிக்கப்படுகிறது: "
            "1 முதல் 4-ஆம் வீடுகள் இளமைப் பருவம் (பிரதம கண்டம்), 5 முதல் 8-ஆம் வீடுகள் நடுப்பருவம் (துவிதீய கண்டம் / 25-50 வயது), 9 முதல் 12-ஆம் வீடுகள் "
            "முதுமைப் பருவம் (திருதியை கண்டம்). 5 முதல் 8-ஆம் வீடுகளில் சுப மற்றும் உச்ச கிரகங்கள் அமையப் பெற்றால், ஜாதகருக்கு நடுப்பருவத்தில் "
            "ராஜ்யாபிஷேகம், பதவி உயர்வு மற்றும் பெருஞ்செல்வம் உண்டாகும்."
        ),
        astrological_principle_en="Planetary concentrations across 4-house quadrants dictate the exact seasonal flowering of human destiny.",
        astrological_principle_ta="ராசிச் சக்கரத்தின் நான்கு பாவப் பிரிவுகள் ஒரு மனிதனின் தலைவிதி எந்தக் காலகட்டத்தில் மலரும் என்பதைத் துல்லியமாக நிர்ணயிக்கின்றன.",
        source_reference="Deva Keralam Book II Part I, Sloka 22 (Khanda Nirnaya)",
        limitations_en="Youth may be quiet or ordinary prior to the dramatic turning point between ages 28 and 32.",
        limitations_ta="28 முதல் 32 வயதிற்கு இடைப்பட்ட திருப்புமுனைக்குப் பிறகே இந்த ராஜ யோகம் முழு வீச்சுடன் செயல்படும்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 33. AQUARIUS LAGNA CHAMPAKAMSA / JALAMSA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-AQUARIUS-CHAMPAKA-01",
        version=1,
        name_en="Deva Keralam Aquarius Lagna Champaka Nadiamsa: Watery Jupiter & Affluent Mercantile Fortune",
        name_ta="தேவ கேரளம் கும்ப லக்னம் சம்பகா/ஜலாம்சம்: ஜல ராசி குருவால் தூர தேச வர்த்தகம் & விசேஷ களத்திர யோகம்",
        category_slug="wealth_finances",
        subcategory="business_growth",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [11],
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [4, 8, 12],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 4, 5, 7, 9, 10, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 498-515) Aquarius Ascendant Champakamsa / Jalamsa: For an Aquarius native, when Jupiter occupies "
            "a watery sign or watery Navamsa while Venus is dignified, the native flourishes through long-distance maritime or foreign commerce, gems, "
            "and textiles. The native is blessed with a beautiful, virtuous spouse and experiences a tremendous surge in wealth after the 32nd year."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 498-515) கும்ப லக்னம் சம்பகாம்சம் / ஜலாம்சம்: கும்ப லக்னத்தில் பிறந்து, குரு பகவான் ஜல "
            "ராசிகளிலோ (கடகம், விருச்சிகம், மீனம்) அல்லது ஜலாம்சத்திலோ நிற்க, சுக்கிரன் பலமுடன் அமைந்தால் ஜாதகர் கடல் கடந்த வியாபாரம், நவரத்தின வர்த்தகம், "
            "மற்றும் ஆடை தொழிலில் கொடிகட்டிப் பறப்பார். அழகான குணவதி மனைவியும், 32 வயதிற்கு மேல் பெரும் செல்வமும் உண்டாகும்."
        ),
        astrological_principle_en="Aquarius airy intellect channeled through Jupiter's watery dispositor unlocks global maritime wealth.",
        astrological_principle_ta="கும்பத்தின் வாயுத் தத்துவமும் குருவின் ஜல தத்துவமும் இணைந்து தூர தேச வர்த்தகத்தில் அபரிமிதமான செல்வத்தை ஈட்டித் தருகின்றன.",
        source_reference="Deva Keralam Book II Part I, Slokas 498-515",
        limitations_en="Native must manage respiratory health and maintain digestive balance during long travels.",
        limitations_ta="தூர பயணங்களின் போது சளி மற்றும் செரிமான உபாதைகளில் கவனம் தேவை.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 34. GEMINI LAGNA INDRAMSA
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-GEMINI-INDRAMSA-01",
        version=1,
        name_en="Deva Keralam Gemini Lagna Indramsa: Mercantile Fleet Command, Maritime Contracts & Persuasive Eloquence",
        name_ta="தேவ கேரளம் மிதுன லக்னம் இந்திராம்சம்: கடல் கடந்த வாணிபம், சொல்வன்மை & அரசு கௌரவம்",
        category_slug="wealth_finances",
        subcategory="business_growth",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [3],
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mercury",
                    "houses": [1, 4, 5, 7, 9, 10],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 4, 5, 7, 9, 10, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 241, 506-529) Gemini Ascendant Indramsa: For a Gemini native, when Mercury is dignified in Kendra "
            "or Trikona and supported by the Moon or Jupiter, the native rises to prominence in intellectual and commercial ventures. Possessing "
            "persuasive eloquence and mathematical acumen, the native commands fleet operations, foreign contracts, and extensive landed estates."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 241, 506-529) மிதுன லக்னம் இந்திராம்சம்: மிதுன லக்னத்தில் பிறந்து புதன் கேந்திர-திரிகோணங்களில் "
            "பலம் பெற்று, சந்திரன் அல்லது குருவின் சுப பார்வை பெற்றால் ஜாதகர் வர்த்தகத்திலும் கல்வியிலும் முதன்மை பெறுவார். விசேஷ சொல்வன்மை, கணினி/கணித "
            "ஞானம், மற்றும் தூர தேச ஒப்பந்தங்கள் மூலம் பெரும் நிலபுலன்களையும் வாகன யோகத்தையும் அடைவார்."
        ),
        astrological_principle_en="Gemini's analytical mercantile lordship empowered by Jupiterian wisdom produces transnational business success.",
        astrological_principle_ta="மிதுன புதனின் வியாபாரத் திறமையும் குருவின் வழிகாட்டலும் சர்வதேச வர்த்தக வெற்றியை நல்குகின்றன.",
        source_reference="Deva Keralam Book II Part I, Slokas 241 & 506-529",
        limitations_en="Occasional nervous tension during intense contractual negotiations.",
        limitations_ta="முக்கிய ஒப்பந்தங்களின் போது பதற்றத்தைத் தவிர்த்து நிதானத்தைக் கையாள்வது நலம்.",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 35. KSHEERA KUMBHA REMEDY (SACRED MILK-POT PROPITIATION)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-KSHEERA-KUMBHA-REMEDY-01",
        version=1,
        name_en="Deva Keralam Ksheera Kumbha Remedy: Sacred Milk-Pot Danam for Chronic Fevers & Paternal Lineage Curses",
        name_ta="தேவ கேரளம் க்ஷீர கும்ப தான பரிகாரம்: பித்ரு சாபம், தொடர் சுரம் & பித்த உபாதைகளுக்கான பாற்குட தானம்",
        category_slug="spiritual_life",
        subcategory="karmic_remedies",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "OR",
                    "conditions": [
                        {"condition_type": "planet_conjunction", "planets": ["Sun", "Saturn"], "same_sign_only": True, "chart": "d1"},
                        {"condition_type": "planet_conjunction", "planets": ["Sun", "Rahu"], "same_sign_only": True, "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [1, 6, 8, 9, 12],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 182-185) Ksheera Kumbha Shastric Remedy: When the Sun or Lagna is afflicted by Saturn or Rahu, "
            "giving rise to burning fevers, bile imbalances (Pitta-Vata), and persistent paternal lineage curses, Sage Venkatesa prescribes the sacred "
            "Ksheera Kumbha Danam. A silver or bronze vessel filled with pure cow's milk is offered to Lord Maheswara with the mantra 'Maheshadevadvesha "
            "Mahakashtanivaraka', instantly terminating the karmic affliction."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 182-185) க்ஷீர கும்ப தான பரிகாரம்: சூரியனோ அல்லது லக்னமோ சனி, ராகுவால் பீடிக்கப்பட்டு "
            "தொடர் காய்ச்சல், பித்த ரோகம் மற்றும் பித்ரு தோஷங்களால் துன்பப்படும் போது, மகேஸ்வர பெருமானை ஆவாஹனம் செய்து வெள்ளி அல்லது வெண்கலக் குடத்தில் "
            "பசும்பால் நிரப்பி 'மகேஶதேவதேவேஶ மஹாகஷ்டநிவாரக' என்ற மந்திரத்தை உச்சரித்து தானம் செய்ய வேண்டும். இதனால் சகல ரோகங்களும் பித்ரு தோஷங்களும் "
            "உடனடியாக நீங்கும்."
        ),
        astrological_principle_en="Lunar-milky offering to Shiva cools the fiery solar-martian-saturnine affliction of the 1st/9th houses.",
        astrological_principle_ta="சிவபெருமானுக்குச் செய்யப்படும் பாற்குட தானம் சூரிய-சனி சேர்க்கையால் ஏற்படும் பித்ரு தோஷத்தையும் உஷ்ண பிணியையும் போக்குகிறது.",
        source_reference="Deva Keralam Book II Part I, Slokas 182-185",
        limitations_en="Should be performed on a Monday or Pradosham during waxing lunar fortnight for maximum potency.",
        limitations_ta="வளர்பிறை திங்கட்கிழமை அல்லது பிரதோஷ நாளில் செய்வது உன்னத பலனைத் தரும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 36. PARASHU DURGA REMEDY (SACRED WEAPON PROPITIATION)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-PARASHU-DURGA-REMEDY-01",
        version=1,
        name_en="Deva Keralam Parashu Durga Remedy: Sacred Axe Offering to Vana Durga for Quelling Dire Adversaries & Litigation",
        name_ta="தேவ கேரளம் பரசு துர்கா மகா பரிகாரம்: சத்ரு நாசம், அரச பயம் & வழக்கு வெற்றிக்கான மழு தானம்",
        category_slug="spiritual_life",
        subcategory="karmic_remedies",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "compound",
                    "operator": "OR",
                    "conditions": [
                        {"condition_type": "planet_house", "planet": "Mars", "houses": [6, 8], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Saturn", "houses": [6, 8], "chart": "d1"},
                        {"condition_type": "planet_house", "planet": "Rahu", "houses": [6, 8], "chart": "d1"},
                    ],
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [6, 8, 10, 12],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book II Part I (Slokas 573-575) Parashu Vana Durga Shastric Remedy: When malefic transit or dasa of the 6th/8th lords triggers "
            "fierce enmity, legal litigation, and government harassment, the native must perform the Parashu (Axe) Danam to Vana Durga with the sacred "
            "slokas: 'Shatrubeejakulocchede Kulasreshtha Prasadaya... Mayarpitamidam Natha Kutharam Pradadamyaham'. The fierce weapon offering "
            "uproots all enemy conspiracies and grants supreme victory."
        ),
        interpretation_ta=(
            "தேவ கேரளம் 2-ஆம் பாகம் 1-ஆம் தொகுதி (ஸ்லோகங்கள் 573-575) பரசு துர்கா மகா பரிகாரம்: 6 அல்லது 8-ஆம் அதிபதிகளின் தசா காலத்திலோ அல்லது "
            "கோச்சாரத்திலோ கொடிய எதிர்ப்புகள், நீதிமன்ற வழக்குகள், மற்றும் அரசாங்க குரோதங்கள் ஏற்படும் போது, வனதுர்க்கா தேவிக்கு 'ஶத்ருபீஜகுலோச்சேதே "
            "குலஶ்ரேஷ்ட ப்ரஸாதய... மயார்பிதமிதம் நாத குடாரம் ப்ரததாம்யஹம்' என்ற மூல மந்திரத்தை ஓதி மழு (கோடாரி) விக்கிரகம் தானம் செய்ய வேண்டும். "
            "இதனால் சகல சத்ரு சதிகளும் வேரறுந்து வெற்றி கிட்டும்."
        ),
        astrological_principle_en="Offering the martial axe (Parashu) to Durga transmutes 6th-house inimical aggression into sovereign protection.",
        astrological_principle_ta="துர்க்கைக்கு மழுவை அர்ப்பணிக்கும் பரிகாரம் 6-ஆம் பாவத்து சத்ருக்களின் கொடிய சதியை அழித்து பரிபூரண பாதுகாப்பை வழங்குகிறது.",
        source_reference="Deva Keralam Book II Part I, Slokas 573-575",
        limitations_en="Must be preceded by fasting and strictly observed non-violent righteous living.",
        limitations_ta="விரதமிருந்து அஹிம்சை நெறியுடன் கூடிய தர்ம வாழ்வைக் கடைப்பிடித்து இத்தானத்தைச் செய்ய வேண்டும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 23. DEVA KERALAM BOOK 1: MATANGA YOGA (SLOKAS 1-2)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-MATANGA-YOGA-01",
        version=1,
        name_en="Deva Keralam Matanga Yoga: Exalted Jupiter with Venus and Moon in Cancer Vargottama",
        name_ta="தேவ கேரளம் மாதங்க யோகம்: கடகத்தில் உச்ச குரு-சுக்கிர சேர்க்கை மற்றும் சந்திரன் வர்கோத்தம ராஜயோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_raja_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [4],  # Cancer (Exalted)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Venus",
                    "signs": [4],  # Cancer
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Moon",
                    "signs": [4],  # Cancer (Own sign & Vargottama potential)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 1-2) Matanga Yoga: When Jupiter occupies Cancer (especially the final Pisces Navamsa) "
            "conjoined Venus, and the Moon is situated in her own sign Cancer and Vargottama in Cancer Navamsa, the supreme "
            "Maatanga Yoga is generated. The native possesses an auspicious blood-red radiant complexion, magnetic aristocratic "
            "countenance, commanding executive presence, unshakeable virtue, and lifelong regal honors."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 1-2) மாதங்க யோகம்: கடக ராசியில் மீன நவாம்சத்தில் குரு பகவான் சுக்கிரனுடன் கூடி நிற்க, "
            "சந்திரன் தனது சொந்த வீடான கடகத்தில் நவாம்சத்திலும் கடகத்தில் (வர்கோத்தமம்) அமைந்தால் 'மாதங்க யோகம்' உண்டாகிறது. "
            "இதனால் ஜாதகர் செவ்வந்த நிறமும், வசீகர கம்பீர முகமும், அரச கௌரவமும், நிர்வாக ஆளுமையும், உயர்ந்த நற்குணங்களும் பெற்று "
            "நீண்ட ஆயுளுடன் சிறப்புற்று வாழ்வார்."
        ),
        astrological_principle_en="Exalted Jupiter conjoining beneficial Venus in maternal Cancer while Moon is Vargottama produces sublime royal dignity.",
        astrological_principle_ta="கடகத்தில் உச்ச குரு சுக்கிரனுடன் இணைந்து சந்திரன் வர்கோத்தமம் பெறுவது உன்னதமான அரச பதவியையும் வசீகர கம்பீரத்தையும் தருகிறது.",
        source_reference="Deva Keralam Book I, Slokas 1-2",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 24. DEVA KERALAM BOOK 1: KOORMA YOGA (SLOKAS 41-46)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-KOORMA-YOGA-01",
        version=1,
        name_en="Deva Keralam Koorma Yoga: Auspicious Planets in 1st, 3rd, and 11th Bestowing 5th Dasha Riches",
        name_ta="தேவ கேரளம் கூர்ம யோகம்: லக்னம், 3 மற்றும் 11-ஆம் இடங்களில் கிரகங்கள் அமைய 5-ஆம் தசாவில் பெரும் தனயோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_raja_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1, 3, 11],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Venus",
                    "houses": [1, 3, 11],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 41-46) Koorma Yoga: When auspicious and strong planets occupy the 1st, 3rd, and 11th "
            "houses, Koorma Yoga is formed. The second half of life and particularly the 5th Dasha from birth (Pratyak Dasa) "
            "brings monumental financial expansion, commercial mastery across multiple enterprises, and royal luxuries mediated "
            "by the ascendant lord."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 41-46) கூர்ம யோகம்: லக்னம், 3-ஆம் இடம் மற்றும் 11-ஆம் இடங்களில் சுப மற்றும் யோக கிரகங்கள் "
            "அமர்ந்து பலம் பெறும்போது 'கூர்ம யோகம்' உண்டாகிறது. ஜாதகர் தனது 5-ஆம் தசாவில் (பிரத்யக் தசா) பல வகை வணிகத் துறைகளில் பெரும் "
            "அனுபவமும் தேர்ச்சியும் பெற்று, நாளுக்கு நாள் அபரிமிதமான தன லாபங்களையும், லக்னாதிபதியின் அனுகூலத்தால் அரச சுகங்களையும் அடைவார்."
        ),
        astrological_principle_en="Triangular anchor in 1st (self), 3rd (initiative), and 11th (gains) establishes resilient tortoise-like enduring prosperity.",
        astrological_principle_ta="லக்னம், 3 மற்றும் 11-ஆம் இடங்களின் தொடர்பு கூர்மம் (ஆமை) போன்ற அசைக்க முடியாத நிலையான செல்வத்தையும் வணிக வெற்றியையும் உருவாக்குகிறது.",
        source_reference="Deva Keralam Book I, Slokas 41-46",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 25. DEVA KERALAM BOOK 1: TAURUS ABALA NADIAMSA (SLOKAS 54-62)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-TAURUS-ABALA-01",
        version=1,
        name_en="Deva Keralam Taurus Lagna Abala Nadiamsa: Sister's Spouse Patronage & Sacred River Fortune",
        name_ta="தேவ கேரளம் ரிஷப லக்னம் அபலா நாடியம்சம்: மைத்துனர் ஆதரவு மற்றும் புண்ணிய நதிக்கரை பாக்கியம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_nadiamsas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [2],  # Taurus Ascendant
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [1, 3, 5, 9, 10, 11],  # Dignified 3rd lord / Moon
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 54-62) Taurus Abala Nadiamsa: A native rising in Taurus ascendant within Abala (Prabha) "
            "Nadiamsa (26°48' to 27°00') possesses a slender frame, deep devotion to elder siblings, and gentle intellect. Through "
            "the influential sponsorship of his brother-in-law (sister's husband), he migrates to sacred river confluences or pilgrim "
            "centers like Gokarna, overcoming initial hardships to attain distinguished fortune."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 54-62) ரிஷப லக்னம் அபலா நாடியம்சம்: ரிஷப லக்னத்தில் அபலா (பிரபா) நாடியம்சத்தில் பிறந்த ஜாதகர் "
            "மெலிந்த தேகமும், மூத்த சகோதரரிடம் மிகுந்த அன்பும் கொண்டிருப்பார். சகோதரியின் கணவர் (மைத்துனர்) மூலமாக வழிகாட்டப்பட்டு மேற்கு "
            "நதிக்கரை அல்லது கோகர்ணம் போன்ற புண்ணிய க்ஷேத்திரங்களுக்குச் சென்று வாழ்ந்து, ஆரம்ப கால வறுமையைக் கடந்து பெரும் யோகங்களை அடைவார்."
        ),
        astrological_principle_en="Taurus fixed earth Lagna with beneficial 3rd/9th links activates foreign pilgrim prosperity through in-laws.",
        astrological_principle_ta="ரிஷப லக்னத்திற்கு 3-ஆம் அதிபதியின் பலம் மைத்துனர் வழி ஆதரவையும் புண்ணிய ஸ்தலங்களில் தங்கி தனம் ஈட்டும் பாக்கியத்தையும் தரும்.",
        source_reference="Deva Keralam Book I, Slokas 54-62",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 26. DEVA KERALAM BOOK 1: PROGENY CURSE & SETU REMEDY (SLOKAS 70-75)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-PROGENY-BRAHMA-SHAPA-01",
        version=1,
        name_en="Deva Keralam Taurus Lagna Progeny Blemish: 8th Lord Jupiter in 5th with Malefic Aspects & Setu Snanam",
        name_ta="தேவ கேரளம் ரிஷப லக்ன புத்திர தோஷ பிரம்ம சாப விதி: 5-ல் குருவுக்கு பாபர் பார்வை & சேது-நாகேஸ்வர பரிகாரம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_karma_remedies",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [2],  # Taurus
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [5],  # 8th lord in 5th house (Virgo)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_aspect",
                    "aspecting_planet": "Saturn",
                    "target_type": "planet",
                    "target_value": "Jupiter",
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 70-75) Progeny Karma-Vipaka: When Jupiter, owning the 8th house for Taurus ascendant, "
            "is posited in the 5th house and afflicted by the aspect of Saturn or Mars, past-life offenses against holy men "
            "(Brahmana Shapa) cause severe hurdles in begetting progeny. Sage Achyuta prescribes holy bath at Setu (Rameswaram), "
            "worship of Lord Nageswara Siva on Pradosha, and Monday charities to grant healthy children in mature age."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 70-75) புத்திர சாப கர்ம விபாகம்: ரிஷப லக்னத்திற்கு 8-ஆம் அதிபதியான குரு 5-ஆம் இடமான கன்னியில் "
            "அமர்ந்து சனியின் பார்வையைப் பெற்றால், முற்பிறவியில் சான்றோரை அவமதித்த பிரம்ம சாபத்தால் புத்திர பாக்கியத் தடைகள் உண்டாகும். "
            "இதற்கு தென்திசை ராமேஸ்வரம் சேது கடலில் புனித நீராடுதல், சோமவார பிரதோஷ விரதமிருந்து நாகேஸ்வர சிவலிங்க வழிபாடு செய்தல் "
            "மூலம் தோஷம் நீங்கி நீண்ட ஆயுளுள்ள குழந்தைகள் பிறக்கும்."
        ),
        astrological_principle_en="8th lord occupying 5th under Saturnine gaze manifests past-life karmic childlessness requiring pilgrim atonement.",
        astrological_principle_ta="ரிஷபத்திற்கு 8-ஆம் அதிபதி குரு 5-ல் அமர்ந்து சனி பார்வை பெறுவது பூர்வ கர்ம புத்திர தடையைக் குறிக்கிறது; சேது ஸ்நானம் இதற்கு நிவர்த்தி.",
        remedy_en="Holy bath at Rameswaram Setu waters, worship of Lord Nageswara Siva on Pradosha days, and fasting on Mondays with charitable gifts.",
        remedy_ta="ராமேஸ்வரம் சேது கடலில் புனித நீராடுதல், பிரதோஷ தினங்களில் நாகேஸ்வர சிவலிங்க அர்ச்சனை, மற்றும் திங்கட்கிழமைகளில் விரதமிருந்து சோமவார தானம் செய்தல்.",
        source_reference="Deva Keralam Book I, Slokas 70-75",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 27. DEVA KERALAM BOOK 1: AQUARIUS NIRMALA VEDANTA SCHOLAR (SLOKAS 88-92)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-AQUARIUS-NIRMALA-VEDANTA-01",
        version=1,
        name_en="Deva Keralam Aquarius Lagna Nirmala Nadiamsa: Moon in 6th and 10th Lord Strong Vedanta Mastery",
        name_ta="தேவ கேரளம் கும்ப லக்னம் நிர்மலா நாடியம்சம்: 6-ல் சந்திரன் மற்றும் 10-ல் செவ்வாய் வேதாந்த ஞான யோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_nadiamsas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [11],  # Aquarius
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [6],  # Cancer (6th house)
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "houses": [10, 12, 1, 3],  # 10th lord Mars strong (own Scorpio or exalted Capricorn)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 88-92) Aquarius Vedanta Yoga: When the 6th lord Moon is posited in Cancer in Nirmala "
            "Nadiamsa while the 10th lord Mars is dignified in own sign or Navamsa, the native attains supreme realization in "
            "Vedanta, the Upanishads, and the 24 sacred Tatwas. He is impeccably virtuous, eloquent, devout to both Vishnu and Siva, "
            "and experiences ascending fortunes in the 3rd and 4th Dashas."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 88-92) கும்ப லக்ன வேதாந்த யோகம்: கும்ப லக்னத்திற்கு 6-ஆம் அதிபதியான சந்திரன் கடகத்தில் "
            "நிர்மலா நாடியம்சத்தில் அமர்ந்து, 10-ஆம் அதிபதியான செவ்வாய் ஆட்சி அல்லது உச்ச பலம் பெற்றால், ஜாதகர் வேதாந்த சாஸ்திரங்களிலும் "
            "உபநிடத தத்துவங்களிலும் மகா ஞானியாகத் திகழ்வார். சொல்வன்மை, தர்ம சிந்தனை, சிவ-விஷ்ணு பக்தி பூண்டு 3 மற்றும் 4-ஆம் தசைகளில் "
            "அளப்பரிய தன லாபங்களையும் கௌரவத்தையும் அடைவார்."
        ),
        astrological_principle_en="6th house Moon in psychic Cancer integrated with strong 10th lord channels spiritual service into scriptural brilliance.",
        astrological_principle_ta="கும்பத்திற்கு 6-ல் சந்திரன் கடகத்திலும் 10-ஆம் அதிபதி செவ்வாய் ஆட்சி/உச்சத்திலும் அமைவது வேதாந்த ஞானத்தையும் ஆன்மீகப் புகழையும் தரும்.",
        source_reference="Deva Keralam Book I, Slokas 88-92",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 28. DEVA KERALAM BOOK 1: AQUARIUS VISWAMBHARA MASTER AUTHOR (SLOKAS 97-103)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-AQUARIUS-VISWAMBHARA-WRITER-01",
        version=1,
        name_en="Deva Keralam Aquarius Lagna Viswambhara Nadiamsa: Jupiter in Scorpio Master Author & Scriptural Commentator",
        name_ta="தேவ கேரளம் கும்ப லக்னம் விஸ்வம்பரா நாடியம்சம்: விருச்சிக குரு கன்னி நவாம்சத்தில் கிரந்தகர்த்தா யோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_nadiamsas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [11],  # Aquarius
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Jupiter",
                    "signs": [8],  # Scorpio (10th house)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 97-103) Viswambhara Grantha-Karta Yoga: In Aquarius ascendant, Jupiter placed in Scorpio "
            "(10th house) within Viswambhara Nadiamsa (falling into Virgo Navamsa) endows the native with supreme intellectual acumen, "
            "unwavering truthfulness, intuitive mastery over the minds of others, and extraordinary literary authorship. The native "
            "becomes a renowned compiler of holy shastras (Grantha-Karta) and receives sovereign patronage."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 97-103) விஸ்வம்பரா கிரந்தகர்த்தா யோகம்: கும்ப லக்னத்திற்கு 10-ஆம் இடமான விருச்சிகத்தில் "
            "குரு பகவான் விஸ்வம்பரா நாடியம்சத்தில் (கன்னி நவாம்சத்தில்) அமையப் பெற்றால், ஜாதகர் பிறர் மனதை அறியும் கூரிய நுண்ணறிவும், "
            "சாஸ்திர ஞானமும், இணையற்ற எழுத்தாற்றலும் பெற்று உலகப் புகழ்பெற்ற நூலாசிரியராகவும் (கிரந்தகர்த்தா) சாஸ்திர உரையாசிரியராகவும் "
            "திகழ்ந்து அரச கௌரவம் அடைவார்."
        ),
        astrological_principle_en="Jupiter in 10th Scorpio combined with Mercurial analytical Navamsa manifests authoritative literary scholarship.",
        astrological_principle_ta="கும்பத்திற்கு 10-ல் குரு விருச்சிகத்தில் அமர்ந்து புதனின் நவாம்சம் பெறுவது சிறந்த எழுத்தாற்றலையும் நூலாசிரியர் யோகத்தையும் நல்கும்.",
        source_reference="Deva Keralam Book I, Slokas 97-103",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 29. DEVA KERALAM BOOK 1: STEP-BROTHER PROGENY SANTANA GOPALA (SLOKAS 115-118)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-STEP-BROTHER-SANTANA-GOPALA-01",
        version=1,
        name_en="Deva Keralam Agada Nadiamsa: Sun with Ketu in 10th Progeny Affliction & Santana Gopala Gift Remedy",
        name_ta="தேவ கேரளம் அகதா நாடியம்சம்: 10-ல் சூரியன்+கேது மாற்றாந்தாய் சகோதர புத்திர தோஷம் & சந்தான கோபால விக்கிரக தானம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_karma_remedies",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Sun",
                    "houses": [10],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Ketu",
                    "houses": [10],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 115-118 & 151-153): When the Sun conjoins Ketu in the 10th house devoid of benefic aspect, "
            "the native's step-brother suffers from severe childlessness or loss of issues due to purva-janma karmas. Sage Vyasa ordains "
            "the gift of a consecrated Santana Gopala Krishna idol, observing Shashti Vrata, and bathing in the sea on Tula Sankranti "
            "to dissolve the affliction and obtain surviving progeny."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 115-118 & 151-153): லக்னத்திற்கு 10-ஆம் இடத்தில் சூரியன் கேதுவுடன் கூடி சுபரின் பார்வையின்றி "
            "நின்றால், ஒன்றுவிட்ட மாற்றாந்தாய் சகோதரருக்கு முற்பிறவி வினையால் புத்திர தோஷம் உண்டாகும். மகரிஷி வியாசரின் உபதேசப்படி, "
            "ராமேஸ்வர சேது ஸ்நானம் செய்து, சஷ்டி விரதமிருந்து, சந்தான கோபால கிருஷ்ணரின் விக்கிரகத்தை ஆசாரியருக்கு தானம் அளித்தால் "
            "புத்திர தோஷம் நிவர்த்தியாகி தீர்க்காயுள் உள்ள குழந்தைகள் பிறப்பர்."
        ),
        astrological_principle_en="Ketu conjoining Sun in 10th afflicts paternal lineage continuity requiring Krishna-Gopala remedial worship.",
        astrological_principle_ta="10-ல் சூரியனும் கேதுவும் இணைவது பிதுர்வழி வம்ச விருத்தி தடையைத் தரும்; சந்தான கோபால தானம் இதற்கு சாஸ்திரப் பரிகாரம்.",
        remedy_en="Gift of a Santana Gopala Krishna idol to a pious scholar, observance of Shashti Vrata, and holy dip at Rameswaram Setu.",
        remedy_ta="சந்தான கோபால கிருஷ்ணர் விக்கிரக தானம் அளித்தல், சஷ்டி விரதம் இருத்தல், மற்றும் ராமேஸ்வரம் சேது கடலில் புனித நீராடுதல்.",
        source_reference="Deva Keralam Book I, Slokas 115-118",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 30. DEVA KERALAM BOOK 1: SAGITTARIUS VARUNA ROYAL YOGA (SLOKAS 201-204)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-SAGITTARIUS-VARUNA-ROYAL-01",
        version=1,
        name_en="Deva Keralam Sagittarius Lagna Varuna Nadiamsa Grand Royal Yoga: 1st, 3rd, 4th, and 6th Planetary Array",
        name_ta="தேவ கேரளம் தனுசு லக்னம் வருண நாடியம்சம் மகா ராஜயோகம்: லக்னத்தில் குரு+சந்திரன், 3-ல் ஆட்சி சனி, 4-ல் உச்சத்து சுக்கிரன்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_raja_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [9],  # Sagittarius
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Jupiter",
                    "houses": [1],  # Jupiter in Lagna
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [1],  # Moon in Lagna
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Saturn",
                    "houses": [3],  # Saturn in Aquarius (Moolatrikona)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 201-204) Grand Varuna Royal Yoga: When Jupiter and Moon conjoin in Sagittarius Lagna within "
            "Varuna Nadiamsa while Saturn holds his Moolatrikona 3rd house in Aquarius and Venus is exalted in the 4th with Ketu, "
            "the native rises to supreme ministerial or royal stature. Endowed with palanquins, state honors, and formidable wealth "
            "manifesting in the 2nd and 5th Dashas, the native enjoys king-like supremacy."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 201-204) வருண நாடியம்ச மகா ராஜயோகம்: தனுசு லக்னத்தில் குருவும் சந்திரனும் இணைந்து நிற்க, "
            "3-ஆம் வீட்டில் சனி மூலதிரிகோண பலத்துடனும், 4-ஆம் வீட்டில் சுக்கிரன் உச்ச பலத்துடனும் அமைந்தால், ஜாதகர் அரசருக்கு இணையான "
            "உயர் பதவியையும், பல்லக்கு வாகனங்களையும், அரச மரியாதைகளையும் பெற்று வாழ்வார். 16, 20, 32 வயதுகளுக்குப் பிறகும், 2 மற்றும் "
            "5-ஆம் தசைகளிலும் அளப்பரிய தன விருத்தியை அடைவார்."
        ),
        astrological_principle_en="Lagna lord Jupiter conjoined Moon aspecting 5th & 9th combined with Moolatrikona Saturn in 3rd guarantees kingly status.",
        astrological_principle_ta="தனுசு லக்னத்தில் லக்னாதிபதி குரு சந்திரனுடன் கூடி 3-ல் சனி ஆட்சி பெறுவது அரசுக்கு நிகரான பெரும் செல்வாக்கையும் பதவியையும் தரும்.",
        source_reference="Deva Keralam Book I, Slokas 201-204",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 31. DEVA KERALAM BOOK 1: 10TH HOUSE RAHU GANGA & SETU YATRA (SLOKAS 255-256)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-RAHU-10TH-GANGA-SETU-01",
        version=1,
        name_en="Deva Keralam 10th House Rahu: Sacred Bath in Mother Ganga or 3-Week Southern Setu Pilgrimage",
        name_ta="தேவ கேரளம் பத்தாம் இட ராகு: கங்கா ஸ்நான புண்ணியம் மற்றும் 3 வார சேது யாத்ரா யோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_bhava_phala",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "planet_house",
            "planet": "Rahu",
            "houses": [10],  # Rahu in 10th house
            "chart": "d1",
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 255-256) Pilgrim Rahu Rule: Rahu situated in the 10th house from the ascendant brings "
            "elevated spiritual merit through a holy dip in the sacred river Ganga. Alternatively, the native embarks on a revered "
            "three-week pilgrimage to the southern ocean sanctuary of Setu (Rameswaram). When 9th and 10th lords connect, the native "
            "donates lands, institutes schools, and builds agrahara settlements."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 255-256) பத்தாம் இட ராகு யாத்ரா யோகம்: லக்னத்திற்கு 10-ஆம் இடத்தில் ராகு பகவான் அமர்ந்திருந்தால், "
            "ஜாதகர் புனித கங்கை நதியில் நீராடும் மகா புண்ணியத்தையோ அல்லது தென்திசையின் சேது (ராமேஸ்வரம்) தீர்த்தத்தில் மூன்று வார யாத்திரை "
            "மேற்கொண்டு கடலில் நீராடும் பாக்கியத்தையோ பெறுவார். 9 மற்றும் 10-ஆம் அதிபதிகளின் தொடர்பு உண்டானால் அக்ரஹார பூமி தானங்களையும் "
            "அன்னதான சத்திரங்களையும் நிறுவி அழியாப் புகழ் பெறுவார்."
        ),
        astrological_principle_en="10th house Rahu breaks orthodox boundaries by compelling sacred transformative pilgrimages to the supreme waters.",
        astrological_principle_ta="10-ல் ராகு அமைவது கங்கையில் நீராடுதல் அல்லது சேது யாத்திரை போன்ற புண்ணிய தீர்த்த ஸ்நானங்களை உண்டாக்கும்.",
        source_reference="Deva Keralam Book I, Slokas 255-256",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 32. DEVA KERALAM BOOK 1: SAGITTARIUS SUN IN SCORPIO KUMARA (SLOKAS 265-267)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-SAGITTARIUS-SCORPIO-SUN-KUMARA-01",
        version=1,
        name_en="Deva Keralam Sagittarius Lagna Sun in Scorpio Kumara Nadiamsa: Vedic Devotion to Vishnu and Siva",
        name_ta="தேவ கேரளம் தனுசு லக்னம் விருச்சிக சூரியன் குமார நாடியம்சம்: சிவ-விஷ்ணு சமபக்தி மற்றும் வைதீக நெறி",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_nadiamsas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [9],  # Sagittarius
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Sun",
                    "signs": [8],  # Scorpio (12th house)
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 265-267): For Sagittarius ascendant, when the 9th lord Sun is posited in Scorpio in Kumara "
            "Nadiamsa, the native is a staunch practitioner of Vedic dharma and an exemplary devotee of both Lord Vishnu and Lord Siva. "
            "He honors his father's righteous lineage, protects ancestral heritage, and enjoys profound inner peace and scholarly "
            "renown among his peers."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 265-267): தனுசு லக்னத்திற்கு 9-ஆம் அதிபதியான சூரியன் 12-ஆம் இடமான விருச்சிகத்தில் குமார "
            "நாடியம்சத்தில் அமையப் பெற்றால், ஜாதகர் சிவபெருமானையும் மகாவிஷ்ணுவையும் சமமாகப் போற்றி வழிபடும் உத்தம பக்தராக விளங்குவார். "
            "வைதீக நெறிகளைப் பின்பற்றி, தந்தையின் தர்ம வழியில் நின்று முன்னோர்களின் கௌரவத்தைக் காத்து நன்மதிப்பைப் பெறுவார்."
        ),
        astrological_principle_en="9th lord Sun in mystical Scorpio directs regal solar energy into non-dual spiritual devotion to Hari and Hara.",
        astrological_principle_ta="தனுசுக்கு 9-ஆம் அதிபதி சூரியன் விருச்சிகத்தில் அமைவது வேத தர்ம நெறியையும் சிவ-விஷ்ணு சமபக்தியையும் நல்கும்.",
        source_reference="Deva Keralam Book I, Slokas 265-267",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 33. DEVA KERALAM BOOK 1: SATURN TRANSIT OVER NAVAMSA DISPOSITOR (SLOKAS 285-286)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-SATURN-TRANSIT-NAVAMSA-DISPOSITOR-01",
        version=1,
        name_en="Deva Keralam Transit Science: Saturn Transiting Navamsa Dispositor of 2nd Lord Causing Financial Reversal",
        name_ta="தேவ கேரளம் நவாம்ச கோசார விதி: 2-ஆம் அதிபதியின் நவாம்ச ராசி மீது சனி கோசாரம் & தன நஷ்டம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_gochara_navamsa",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Saturn",
                    "houses": [2, 6, 8, 12],  # Afflicted Saturn / Dhana house
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 285-286 & 354) Navamsa Gochara Principle: Whenever transit Saturn crosses the Rasi identical "
            "with the natal Navamsa occupied by the 2nd lord (or 8th lord) or its trines, the native suffers sudden depletion of accrued "
            "wealth, fiscal distress, and family discord. Propitiation through Siva Abhisheka and sesame oil lamp offerings is indicated."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 285-286 & 354) நவாம்ச கோசார ரகசியம்: 2-ஆம் அதிபதி (அல்லது 8-ஆம் அதிபதி) நவாம்சத்தில் நின்ற "
            "ராசிக்கோ அல்லது அதன் திரிகோண ராசிக்கோ கோசார சனி சஞ்சரிக்கும் காலத்தில், ஜாதகருக்குத் திடீர் தன நஷ்டமும், வியாபாரப் பின்னடைவும், "
            "குடும்பத்தில் மனக்கலக்கமும் உண்டாகும். இதற்கு சிவலிங்கத்திற்கு நல்லெண்ணெய் தீபமேற்றி வழிபடுவதும் ருத்ராபிஷேகம் செய்வதும் நற்பலன் தரும்."
        ),
        astrological_principle_en="Transit of malefic Saturn through the Navamsa dispositor of wealth/death triggers acute karmic auditing.",
        astrological_principle_ta="தன/அஷ்டமாதிபதியின் நவாம்ச ராசியில் கோசார சனி செல்லும்போது கர்ம வினையால் தன நஷ்டம் உண்டாகும்; சிவாலயம் செல்லல் பரிகாரம்.",
        remedy_en="Lighting sesame oil lamps for Lord Siva on Saturdays and chanting Sri Rudram to mitigate sudden financial loss.",
        remedy_ta="சனிக்கிழமைகளில் சிவாலயத்தில் நல்லெண்ணெய் தீபம் ஏற்றுதல் மற்றும் ஸ்ரீ ருத்ர பாராயணம் செய்து தன நஷ்டங்களைத் தவிர்த்தல்.",
        source_reference="Deva Keralam Book I, Slokas 285-286",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 34. DEVA KERALAM BOOK 1: AQUARIUS RAHU-SUN IN VENUS NAVAMSA (SLOKAS 357-359)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-AQUARIUS-RAHU-SUN-VENUS-NAVAMSA-01",
        version=1,
        name_en="Deva Keralam Rahu and Sun in Aquarius: Venus Navamsa Bestowing Marital Felicity and Robust Health",
        name_ta="தேவ கேரளம் கும்பத்தில் ராகு-சூரியன் சுக்கிர நவாம்சம்: தாம்பத்ய சுகம், ஆரோக்கியம் மற்றும் தன பாக்கியம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_bhava_phala",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_sign",
                    "planet": "Sun",
                    "signs": [11],  # Aquarius
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_sign",
                    "planet": "Rahu",
                    "signs": [11],  # Aquarius
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 357-359): When Rahu and the Sun conjoin in Aquarius, they normally cause moral and urinary "
            "ailments if falling into Mercury's Navamsa; however, if they attain a Navamsa of Venus (Taurus or Libra), the defect is "
            "completely nullified. The native enjoys exceptional longevity, glowing vitality, a devoted and noble spouse, and abundant "
            "material fortunes."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 357-359): கும்ப ராசியில் ராகுவும் சூரியனும் இணைந்து நின்று புதனின் நவாம்சம் பெற்றால் "
            "சிறுநீரக நோய்களையும் ஒழுக்கக் கேடுகளையும் தரும்; ஆனால் அவர்களே சுக்கிரனின் நவாம்சமான ரிஷபம் அல்லது துலாம் நவாம்சம் பெற்றால் "
            "அத்தோஷங்கள் முற்றிலும் நீங்கிவிடும். ஜாதகருக்குத் தீர்க்காயுளும், ஆரோக்கியமும், அன்பான குணவதி மனைவியும், நிலைத்த தன தான்ய சம்பத்துகளும் "
            "அமைந்து இனிதே வாழ்வார்."
        ),
        astrological_principle_en="Venusian harmonious Navamsa sub-influence elevates the Eclipse-forming Sun-Rahu conjunction in Aquarius.",
        astrological_principle_ta="கும்பத்தில் சூரியன்-ராகு சேர்க்கை சுக்கிர நவாம்சம் பெறும்போது கிரகண தோஷம் நீங்கி தாம்பத்ய சுகமும் ஆரோக்கியமும் பெருகும்.",
        source_reference="Deva Keralam Book I, Slokas 357-359",
        severity=SeverityLevel.FAVORABLE,
    ),

    # =======================================================================
    # 35. DEVA KERALAM BOOK 1: KALA CHAKRA DASA DEHA/JEEVA AILMENTS (SLOKAS 329-330)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-KALA-CHAKRA-DEHA-JEEVA-01",
        version=1,
        name_en="Deva Keralam Kala Chakra Dasa Principle: Malefics in Deha or Jeeva Rasi Causing Severe Ailments",
        name_ta="தேவ கேரளம் காலச்சக்கர தசா விதி: தேக அல்லது ஜீவ ராசியில் பாப கிரகங்கள் அமைவதால் உடல் உபாதைகள்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_bhava_phala",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "planet_house",
                    "planet": "Saturn",
                    "houses": [6, 8, 12],
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Mars",
                    "houses": [6, 8, 12],
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 329-330) Kala Chakra Dasa Deha-Jeeva Vulnerability: If either the Deha Rasi (physical sheath) "
            "or the Jeeva Rasi (vital life-force) in the Kala Chakra Dasa framework contains natural malefics (Saturn/Mars), the native "
            "experiences intense physical tribulations and surgical risks during the operation of those Rasi periods. Gifting an image "
            "of the Zodiac wheel (Chakra Yantra) is prescribed to nullify untimely demise."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 329-330) காலச்சக்கர தசா தேக-ஜீவ ரகசியம்: காலச்சக்கர தசா முறையில் உடலைக் குறிக்கும் 'தேக ராசி' "
            "அல்லது உயிரைக் குறிக்கும் 'ஜீவ ராசி'களில் பாப கிரகங்களான சனி அல்லது செவ்வாய் அமைந்திருந்தால், அந்த ராசி தசைகள் நடக்கும்போது "
            "கடுமையான சரீர உபாதைகளும் அறுவை சிகிச்சை கண்டங்களும் உண்டாகும். இதற்கு சோதிடருக்கு சக்ர யந்திர தானம் அளிப்பதும் மிருத்யுஞ்சய சாந்தியும் பரிகாரமாகும்."
        ),
        astrological_principle_en="Malefics residing in the Deha or Jeeva sensitive points of the Kala Chakra wheel afflict physical embodiment.",
        astrological_principle_ta="காலச்சக்கர தசையின் தேக அல்லது ஜீவ ராசிகளில் பாப கிரகங்கள் அமர்வது சரீர ஆரோக்கியத்திற்குச் சோதனையைத் தரும்; சக்ர யந்திர தானம் பரிகாரம்.",
        remedy_en="Donation of a silver Chakra Yantra to a pious astrologer and recitation of Mahamrityunjaya Mantra.",
        remedy_ta="சோதிட அறிஞருக்கு வெள்ளி சக்ர யந்திர தானம் அளித்தல் மற்றும் மகா மிருத்யுஞ்சய மந்திரம் ஜபித்து சாந்தி செய்தல்.",
        source_reference="Deva Keralam Book I, Slokas 329-330",
        severity=SeverityLevel.UNFAVORABLE,
    ),

    # =======================================================================
    # 36. DEVA KERALAM BOOK 1: CHANDRA NADI KUTILA MOON MATERNAL LONGEVITY (SLOKAS 132-135)
    # =======================================================================
    AstrologicalRuleDefinition(
        rule_id="RULE-DK-B1-CHANDRA-NADI-KUTILA-MOON-01",
        version=1,
        name_en="Deva Keralam Chandra Nadi Citation: 6th Lord Moon in Kutila Nadiamsa with Mercury Maternal Longevity",
        name_ta="தேவ கேரளம் சந்திர நாடி மேற்கோள்: 6-ஆம் அதிபதி சந்திரன் குடில நாடியம்சத்தில் புதன் பார்வை தாய்வழி ஆயுள் யோகம்",
        category_slug="deva_keralam_classics",
        subcategory="deva_keralam_nadiamsas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "AND",
            "conditions": [
                {
                    "condition_type": "lagna_sign",
                    "sign": [11],  # Aquarius
                },
                {
                    "condition_type": "planet_house",
                    "planet": "Moon",
                    "houses": [6],  # 6th house Moon
                    "chart": "d1",
                },
                {
                    "condition_type": "planet_aspect",
                    "aspecting_planet": "Mercury",
                    "target_type": "planet",
                    "target_value": "Moon",
                    "chart": "d1",
                },
            ],
        },
        interpretation_en=(
            "Deva Keralam Book 1 (Slokas 132-135) Chandra Nadi Citation: According to the venerable Chandra Nadi, for an Aquarius native, "
            "when the 6th lord Moon occupies Kutila Nadiamsa in aspect to Mercury, maternal relatives enjoy long spans of life. The native "
            "inherits ancestral maternal wealth, and the mother prospers through her middle progeny."
        ),
        interpretation_ta=(
            "தேவ கேரளம் முதல் பாகம் (சுலோகங்கள் 132-135) சந்திர நாடி மேற்கோள்: பழம்பெரும் சந்திர நாடி நூலை மேற்கோள் காட்டி மகரிஷி அச்சுதர் "
            "அருளியபடி, கும்ப லக்னத்திற்கு 6-ஆம் அதிபதியான சந்திரன் குடில நாடியம்சத்தில் அமர்ந்து புதனால் பார்க்கப்பட்டால், தாய்வழி உறவினர்கள் "
            "நீண்ட ஆயுளுடன் வாழ்வர்; ஜாதகரின் தாயார் நன்மைகளை அடைவார்; தாய்வழிப் பூர்வீக சொத்துக்கள் ஜாதகருக்கு வந்து சேரும்."
        ),
        astrological_principle_en="6th lord Moon aspected by intellectual Mercury preserves maternal longevity and secures maternal patrimony.",
        astrological_principle_ta="கும்பத்திற்கு 6-ஆம் அதிபதி சந்திரனைப் புதன் பார்ப்பது தாய்வழி உறவினர்களின் ஆயுளையும் தாய்வழிச் சொத்துக்களையும் காக்கும்.",
        source_reference="Deva Keralam Book I, Slokas 132-135",
        severity=SeverityLevel.FAVORABLE,
    ),
]
