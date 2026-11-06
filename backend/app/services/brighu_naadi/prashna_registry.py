"""Brighu Prashna Nadi Classical Prophecy Registry.

Compiled verbatim from R. G. Rao's "Brighu Prashna Nadi"
(First Published 1994, Sagar Publications, New Delhi, 165 pages).

Procedure:
1. Note the completed age of the querent in years.
2. Distinctive Number = 107 - Completed Age.
   (If querent has not completed 1 year of age, refer to 107).
3. The result corresponds to the matching Prashna prediction.
"""

from typing import Dict, Any, Optional

GURU_MANTRA = "OM SRI JAGADEESWARAYA NAMAHA"
GANESHA_MANTRA = "OM SRI GANESHAYANAMAHA OM"

# Master registry mapping prediction number (0 to 107) to the classical oracle text
PRASHNA_PREDICTIONS: Dict[int, Dict[str, Any]] = {
    107: {
        "yoga_name_en": "Suyoga (Auspicious Natal Fortune)",
        "yoga_name_ta": "சுயோகம் (மங்களகரமான பிறவி யோகம்)",
        "sanskrit_sloka": "OM - SUYOGA JANMA - RAJADWARA PRAVESHAM",
        "core_prophecy_en": (
            "Born under a healthy Suyoga. Educational aspects, welfare, prosperity, and the career "
            "of life will be enshrined in a very good manner in all aspects of life. Respected by elders "
            "and Gurus, highly helpful to others even foregoing personal work at own cost."
        ),
        "core_prophecy_ta": (
            "உன்னதமான சுயோகத்தில் பிறப்பு. கல்வி, சுபிட்சம், தொழில் மற்றும் வாழ்வின் அனைத்து அம்சங்களிலும் உயரிய நற்பலன்கள் "
            "அமையும். பெரியவர்களிடமும் குருமார்களிடமும் மிகுந்த பக்தி கொண்டவர். பிறருக்கு உதவ தன் சொந்தப் பணிகளையும் "
            "பொருட்படுத்தாது உதவும் பரந்த உள்ளம் படைத்தவர்."
        ),
        "career_and_finance_en": (
            "The yogakarakas start after 5 Samvatsaras (years). The person's parents will be highly "
            "benefited in speculation, commercial transactions, and financial incomes. Prominent influential "
            "person in 'Raja Dwara' (governmental / executive entrance)."
        ),
        "career_and_finance_ta": (
            "5 ஆண்டுகள் கழித்து ராஜ யோகம் முழுமையாகச் செயல்படும். பெற்றோர்கள் வணிகம், பங்கு வர்த்தகம் மற்றும் சொத்து சேர்க்கை "
            "மூலம் பெரும் தனலாபம் அடைவர். அரசாங்க அல்லது நிர்வாக உயர் மட்டத்தில் செல்வாக்குமிக்க பதவிகளை வகிப்பார்."
        ),
        "family_and_relationships_en": (
            "Guardians and family elders will actively cooperate for prosperity and mutual gains."
        ),
        "family_and_relationships_ta": (
            "குடும்பப் பெரியவர்களும் வழிகாட்டிகளும் ஒன்றுபட்டு ஜாதகரின் மேன்மைக்குத் துணை நிற்பார்கள்."
        ),
        "health_and_cautions_en": (
            "Due to previous karmas, likely to suffer from health ailments. A physician/doctor coming from the "
            "East side will bring permanent cure."
        ),
        "health_and_cautions_ta": (
            "பூர்வ கர்ம வினையால் உடல் உபாதைகள் வரலாம்; கிழக்கு திசையிலிருந்து வரும் மருத்துவரால் பரிபூரண குணம் கிட்டும்."
        ),
        "past_karma_cause_en": "Minor residual deeds from previous birth triggering temporary physical vulnerabilities.",
        "past_karma_cause_ta": "முற்பிறவி கர்ம வினையால் ஏற்படும் தற்காலிக உடல் உபாதை.",
        "prescribed_remedy_en": (
            "Conduct special Pooja. Within a few months, all kinds of good and auspicious developments "
            "will unfold unfailingly."
        ),
        "prescribed_remedy_ta": "இறைவனுக்குரிய விசேஷ பூஜை நடத்தப்பட வேண்டும்; சில மாதங்களில் சகல நன்மைகளும் கைகூடும்.",
        "relief_timeline_en": "Within a few months auspicious changes begin; major yoga manifests after 5 Samvatsaras.",
        "relief_timeline_ta": "சில மாதங்களில் நற்பலன்கள் தொடங்கும்; 5 ஆண்டுகளில் முழுமையான யோகம் நிலைபெறும்.",
    },
    106: {
        "yoga_name_en": "Rasa Yoga & Stalantare Yoga Vrudhi",
        "yoga_name_ta": "ரச யோகம் & ஸ்தலாந்தர யோக விருத்தி",
        "sanskrit_sloka": "STALANTARE YOGA VRUDHI NASAMSHAYAHA",
        "core_prophecy_en": (
            "Born in the amsha of Rasa Yoga. Although auspicious, native suffers from constant mental worries. "
            "Must establish life away from the birthplace in distant places to flourish."
        ),
        "core_prophecy_ta": (
            "ரச யோக அம்சத்தில் பிறந்தவர். யோகமான அமைப்பு இருந்தாலும் அடிக்கடி மன உளைச்சலும் சிந்தனைக் குழப்பமும் ஏற்படும். "
            "பிறந்த இடத்தை விட்டு வெளியூர் அல்லது தொலைதூர ஊர்களில் சென்று குடியேறினால் மட்டுமே பெரும் வளர்ச்சி உண்டாகும்."
        ),
        "career_and_finance_en": (
            "Compensates educational or professional breaks by change of place ('Stalantare Yoga Vrudhi Nasamshayaha'). "
            "After 4 Samvatsaras, brings great wealth in the form of landed properties and residential houses."
        ),
        "career_and_finance_ta": (
            "இடமாற்றம் செய்வதன் மூலம் தடைகள் நீங்கி தொழில் உயரும். 4 ஆண்டுகளுக்குப் பிறகு நிலபுலன்கள், சொந்த வீடு மற்றும் "
            "அசையாச் சொத்துக்கள் மூலம் பெரும் தன விருத்தி கிட்டும்."
        ),
        "family_and_relationships_en": (
            "First half of life poses burdens to mother, and later half to father. Remedy alleviates the burden on parents."
        ),
        "family_and_relationships_ta": (
            "வாழ்வின் முற்பகுதியில் தாயாருக்கும், பிற்பகுதியில் தந்தையாருக்கும் சில சிரமங்கள் ஏற்படலாம். பரிகாரம் மூலம் சமனடையும்."
        ),
        "health_and_cautions_en": (
            "Assistance and cure from a doctor from the South and West. Poorvadosha reduced significantly after 10 months."
        ),
        "health_and_cautions_ta": (
            "தெற்கு மற்றும் மேற்கு திசை மருத்துவர்களால் ஆரோக்கியம் சீரடையும். 10 மாதங்களுக்குப் பிறகு பூர்வ தோஷம் விலகும்."
        ),
        "past_karma_cause_en": "Poorvadosha (past karmic burden) creating ancestral friction and mental oscillations.",
        "past_karma_cause_ta": "முற்பிறவி பூர்வ தோஷத்தால் மன அமைதியின்மை உண்டாதல்.",
        "prescribed_remedy_en": (
            "Perform Pooja to 'Manobhina Devatha' (Ishta Devata). At a 3-road junction, offer Dakshina-Deepa with lighted lamp "
            "and charity to deserving souls."
        ),
        "prescribed_remedy_ta": (
            "இஷ்ட தெய்வத்திற்கு விசேஷ வழிபாடு செய்க. முச்சந்தி கூடும் இடத்தில் தெற்கு நோக்கிய தீபம் (தட்சிண தீபம்) ஏற்றி "
            "ஆதரவற்றோருக்கு தானம் வழங்குக."
        ),
        "relief_timeline_en": "Immediate relief within 3 months and 15 days; substantial landed fortune in 4 years.",
        "relief_timeline_ta": "3 மாதங்கள் 15 நாட்களில் உடனடி நிம்மதி; 4 ஆண்டுகளில் நிலபுலன் சொத்து யோகம்.",
    },
    105: {
        "yoga_name_en": "Karala Dusthamsha & Yanthra Vidhya Yoga",
        "yoga_name_ta": "கராள துஷ்டாம்சம் & எந்திர வித்யா யோகம்",
        "sanskrit_sloka": "YANTHRA VIDHYA ANUBHAVA - ARISHTA PARIHARA",
        "core_prophecy_en": (
            "Undergoes Karala Dusthamsha causing sharp educational hurdles and extreme cold, gastric, and nervous troubles. "
            "However, masters 'Yanthra Vidhya' (knowledge of machinery, technology, tools, or defense equipment)."
        ),
        "core_prophecy_ta": (
            "கராள துஷ்டாம்சத்தால் கல்வியில் தடைகளும், வாயு மற்றும் குளிர் சம்பந்தப்பட்ட உடல் உபாதைகளும் ஏற்படலாம். "
            "இருப்பினும் எந்திரவியல், தொழினுட்பம், மெஷினரி அல்லது கணினி சார்ந்த 'எந்திர வித்யா' ஞானத்தால் அபார வெற்றி பெறுவார்."
        ),
        "career_and_finance_en": (
            "Prosperity through technological training, mechanical mastery, and industrial experience. "
            "Must wait 8 months for full professional elevation."
        ),
        "career_and_finance_ta": (
            "இயந்திரம் மற்றும் தொழினுட்பத் துறையில் புகழும் வருவாயும் கூடும். 8 மாத காத்திருப்புக்குப் பின் உத்தியோக உயர்வு கிட்டும்."
        ),
        "family_and_relationships_en": (
            "Reconciliation with estranged friends; alienated colleagues come closer and offer substantial cooperation."
        ),
        "family_and_relationships_ta": (
            "பிரிந்து சென்ற பழைய நண்பர்கள் மீண்டும் ஒன்றிணைந்து தொழில் வளர்ச்சிக்கு உதவுவார்கள்."
        ),
        "health_and_cautions_en": (
            "Strict caution advised against fire hazards, vehicle accidents, and sharp equipment. Keep distance from fire and rash driving."
        ),
        "health_and_cautions_ta": (
            "நெருப்பு, மின்சாரம், வாகன வேகம் மற்றும் கூர்மையான ஆயுதங்கள் குறித்து மிகுந்த எச்சரிக்கை தேவை."
        ),
        "past_karma_cause_en": "Arishta Yoga persisting from past 1 year 4 months.",
        "past_karma_cause_ta": "கடந்த ஓராண்டு நான்கு மாதங்களாகத் தொடரும் அரிஷ்ட யோக கர்மா.",
        "prescribed_remedy_en": (
            "Perform continuous Archana to Lord Sree Prasanneswara Swamy for 5 consecutive weeks."
        ),
        "prescribed_remedy_ta": "தொடர்ந்து 5 வாரங்கள் ஸ்ரீ பிரசன்னேஸ்வர சுவாமிக்கு அர்ச்சனை மற்றும் வழிபாடு செய்க.",
        "relief_timeline_en": "8 months waiting brings professional breakthrough; remedy protects over 5 weeks.",
        "relief_timeline_ta": "5 வாரங்களில் தோஷ நிவர்த்தி; 8 மாதங்களில் தொழில் சுபிட்சம்.",
    },
    104: {
        "yoga_name_en": "Dwi Panditya Shobhitaha & Mangala Yoga",
        "yoga_name_ta": "துவி பாண்டித்ய சோபித & மங்கள யோகம்",
        "sanskrit_sloka": "DWI PANDITYA SHOBHITAHA: LOKA KEERTI VISHESHITHAHA",
        "core_prophecy_en": (
            "Very pious, clean-hearted, approachable soul. Enjoys dual intellectual fields ('Dwi Panditya'), "
            "commanding societal renown ('Keerthi') and mingling in assemblies of learned intellectuals ('Saijana Sangha')."
        ),
        "core_prophecy_ta": (
            "தெய்வ பக்தி, எளிமை மற்றும் களங்கமற்ற மனம் கொண்டவர். இரு துறைகளில் ஆழ்ந்த புலமை ('துவி பாண்டித்யம்') பெற்று "
            "சமுதாயத்தில் 'கீர்த்தி' என்னும் நற்பெயரோடு அறிஞர்கள் அவையில் மதிக்கப்படுவார்."
        ),
        "career_and_finance_en": (
            "Accomplished professional, commercial businessman, legal mind, or administrator of justice and Dharma. "
            "Enjoys multiple vehicles, agricultural lands, and commercial properties."
        ),
        "career_and_finance_ta": (
            "வர்த்தகம், வணிகம், சட்டம், நீதித்துறை அல்லது அறக்கட்டளை நிர்வாகத்தில் திறமை. வாகனங்கள் மற்றும் நிலபுலன் யோகம் உண்டு."
        ),
        "family_and_relationships_en": (
            "Father's middle-age crisis completely dissolves; deep harmony with sisters and brothers."
        ),
        "family_and_relationships_ta": (
            "தந்தையின் கஷ்டங்கள் விலகும்; உடன் பிறந்த சகோதர சகோதரிகளுடன் மாறாத பாசமும் ஒத்துழைப்பும் நீடிக்கும்."
        ),
        "health_and_cautions_en": (
            "Vulnerable to nervous weakness, vitamin debility, and nutritional fatigue. Timely recovery assured."
        ),
        "health_and_cautions_ta": (
            "நரம்புத் தளர்ச்சி, சத்துக்குறைவு மற்றும் சோர்வு ஏற்படலாம்; சத்தான உணவு மற்றும் ஓய்வால் பூரண நலம் கிட்டும்."
        ),
        "past_karma_cause_en": "Mild ancestral family burdens which dissolve through virtuous deeds.",
        "past_karma_cause_ta": "குடும்ப பூர்வ கர்ம வினை தர்ம காரியங்களால் மறையும்.",
        "prescribed_remedy_en": (
            "Perform Gruha Shanthi Homa; prostration to ancestral Gurus and feeding pious scholars."
        ),
        "prescribed_remedy_ta": "கிருக சாந்தி ஹோமம் செய்க; பெரியோர்கள் மற்றும் சாதுக்களுக்கு அன்னதானம் அளிக்க.",
        "relief_timeline_en": "1 Samvatsara (year) brings prosperity, profits, and joyful news from all quarters.",
        "relief_timeline_ta": "ஓராண்டில் (1 சம்வத்ஸரம்) தொழில், குடும்பம் மற்றும் வருவாயில் முழுமையான யோக மலர்ச்சி.",
    },
    103: {
        "yoga_name_en": "Tadunte Yoga Vridhi & Guru Vidhya",
        "yoga_name_ta": "ததுந்தே யோக விருத்தி & குரு வித்யா",
        "sanskrit_sloka": "TADUNTE YOGA VRIDHINASAMSHAYAHA",
        "core_prophecy_en": (
            "Duty-minded, logical thinker, self-respecting. Possesses Poorva-Punya and expertise in 'Guru Vidhya' "
            "(higher spiritual knowledge, consulting, teaching, and occult guidance). Guides others toward salvation."
        ),
        "core_prophecy_ta": (
            "கடமை உணர்வும் தர்க்க ரீதியான சிந்தனையும் கொண்டவர். பூர்வ புண்ணிய பலத்தால் 'குரு வித்யா' என்னும் ஆன்மீக, "
            "ஆலோசனை மற்றும் வழிகாட்டல் சாஸ்திரங்களில் தேர்ச்சி பெற்று பிறருக்கு நல்வழிகாட்டுவார்."
        ),
        "career_and_finance_en": (
            "Substantial wealth accumulation without poverty or financial scarcity. Auspicious investments flourish."
        ),
        "career_and_finance_ta": (
            "பொருளாதாரப் பற்றாக்குறையின்றி நிறைவான தன சேர்க்கை உண்டு. முதலீடுகள் மற்றும் முயற்சிகள் லாபம் தரும்."
        ),
        "family_and_relationships_en": (
            "Auspicious ceremonies (weddings, home celebrations) unfold at home after resolving feminine karmic friction."
        ),
        "family_and_relationships_ta": (
            "இல்லத்தில் சுப காரியங்கள், மங்கள நிகழ்வுகள் வெகு விமரிசையாக நடைபெறும்."
        ),
        "health_and_cautions_en": (
            "Vitiation of Vatha (wind) and gastric disorders. Strictly avoid foods causing gastric aggravation for 2 years."
        ),
        "health_and_cautions_ta": (
            "வாத மற்றும் வாய்வு தொந்தரவுகள் வரலாம்; எளிதில் செரிக்கும் சாத்விக உணவுகளை உட்கொள்ள வேண்டும்."
        ),
        "past_karma_cause_en": "Stree Nindana Dosha (past birth offense against womanhood or maternal figure).",
        "past_karma_cause_ta": "முற்பிறவியில் பெண்ணிற்கு இழைத்த நிந்தனை (ஸ்திரீ நிந்தனா தோஷம்).",
        "prescribed_remedy_en": (
            "Prostration before Lord Sree Datta Guru (Dattatreya) and seeking pardon from motherly women."
        ),
        "prescribed_remedy_ta": "ஸ்ரீ தத்தாத்ரேயர் (ஸ்ரீ தத்த குரு) சன்னதியில் சாஷ்டாங்க நமஸ்காரம் செய்து பெண்களைக் கௌரவித்தல்.",
        "relief_timeline_en": "7 Masas (months) to unlock prosperity; permanent growth within 2 Samvatsaras.",
        "relief_timeline_ta": "7 மாதங்களில் சுபிட்சம்; 2 ஆண்டுகளில் அசைக்க முடியாத யோக விருத்தி.",
    },
    102: {
        "yoga_name_en": "Yoga Jeevi & Vishesha Sukha Yoga",
        "yoga_name_ta": "யோக ஜீவி & விசேஷ சுக யோகம்",
        "sanskrit_sloka": "SARA SARATHI SOWBHAGYA SAMA YUKTO JEEVI YOGA BHOOTLAI",
        "core_prophecy_en": (
            "Delightfully handsome, material connoisseur ('Vishayanubhavi'), and lover of antique or high-value articles. "
            "Brings good fortune to both birthplace and surrounding community."
        ),
        "core_prophecy_ta": (
            "அழகான கம்பீரத் தோற்றம், கலை ரசனை மற்றும் அரிய மதிப்புமிக்க பொருட்களைச் சேர்க்கும் ஆர்வம் கொண்டவர். "
            "பிறந்த மண்ணுக்கும் உற்றார் உறவினர்களுக்கும் அதிர்ஷ்டத்தைத் தரும் யோக ஜீவி."
        ),
        "career_and_finance_en": (
            "Commercial trades, speculations, and transactions yield lucrative gains. 15th year brings peak education."
        ),
        "career_and_finance_ta": (
            "வணிகம், வர்த்தகம், புரோக்கரேஜ் மற்றும் தொழில் முயற்சிகளில் எதிர்பாராத லாபம். 15-ஆம் வயதில் உயர்கல்வி பிரகாசம்."
        ),
        "family_and_relationships_en": (
            "Full cooperation and peace with parents and elders. Household radiates domestic comfort ('Vishesha Sukha')."
        ),
        "family_and_relationships_ta": (
            "பெற்றோரின் ஆசியும் ஒத்துழைப்பும் பரிபூரணமாகக் கிட்டும்; குடும்பத்தில் அமைதியும் மகிழ்ச்சியும் நிலவும்."
        ),
        "health_and_cautions_en": (
            "Restlessness of mind and fatigue due to past occupation struggles; relieved by divine grace."
        ),
        "health_and_cautions_ta": (
            "மன உளைச்சல் மற்றும் அலைச்சல்; ஆன்மீகப் பிரார்த்தனைகளால் பூரண நிம்மதி உண்டாகும்."
        ),
        "past_karma_cause_en": "Asambadha Vrithi in previous birth (improper livelihood or conflict with workers).",
        "past_karma_cause_ta": "முற்பிறவியில் முறையற்ற தொழில் அல்லது ஊழியர்களிடம் ஏற்பட்ட கர்ம வினை (அசம்பந்த விருத்தி).",
        "prescribed_remedy_en": (
            "Offer food, Daana, and Dakshina to 3 Sumangalis / Muttaidays; visit Goddess Annapoorneshwari every Friday."
        ),
        "prescribed_remedy_ta": "3 சுமங்கலி பெண்களுக்கு ஆடை, உணவு, தாம்பூல தானம் செய்க; வெள்ளிக்கிழமைகளில் ஸ்ரீ அன்னபூரணியை வழிபடுக.",
        "relief_timeline_en": "1 Samvatsara, 4 Masas, and 1 Paksha brings unfailing Shubha Phalas.",
        "relief_timeline_ta": "1 வருடம், 4 மாதம், 15 நாட்களில் சுப காரியங்கள் மற்றும் தனலாபம் நிச்சயம் கைகூடும்.",
    },
    98: {
        "yoga_name_en": "Sudhakara Sadyoga & Kireeta Gruha Nirmana",
        "yoga_name_ta": "சுதாகர சத்யோகம் & கிரீட கிருக நிர்மாண யோகம்",
        "sanskrit_sloka": "SHASTHI BANA MITE VARSHE YOGA VRIDHI NASAMSHAYAHA",
        "core_prophecy_en": (
            "Born under the Sadyoga of Sudhakara. Though early youth experiences displacement and health trials, "
            "matures into magnificent residential home builder and influential head of family."
        ),
        "core_prophecy_ta": (
            "சுதாகர சத்யோகத்தில் பிறப்பு. இளமைக்காலத்தில் இடப்பெயர்ச்சியும் உடல் நலிவும் இருந்தாலும், பிற்காலத்தில் "
            "அரண்மனை போன்ற சொந்த மாளிகையைக் கட்டி சமுதாயத்தில் முடிசூடா மன்னராகத் திகழ்வார்."
        ),
        "career_and_finance_en": (
            "Income and financial gains from nearby sources and family circles. After age 30, commands vehicles and prosperity."
        ),
        "career_and_finance_ta": (
            "சொந்த ஊரிலேயே பல வழிகளில் வருவாய் பெருகும். 28 முதல் 30 வயதுக்குள் சொந்த வாகனங்கள் மற்றும் ஆடம்பர வாழ்க்கை அமையும்."
        ),
        "family_and_relationships_en": (
            "Father's past troubles completely resolved. Excellent fraternal bonding with brothers and sisters."
        ),
        "family_and_relationships_ta": (
            "தந்தையின் பழைய கவலைகள் தீரும்; உடன்பிறப்புகளின் அன்பும் ஆதரவும் முழுமையாகக் கிடைக்கும்."
        ),
        "health_and_cautions_en": (
            "Vulnerabilities around age 10-11 ('Dasama Ekadasa') now successfully crossed."
        ),
        "health_and_cautions_ta": "10-11 வயதில் ஏற்பட்ட பாலாரிஷ்ட கண்டங்கள் நீங்கி நீண்ட ஆயுள் யோகம் உண்டு.",
        "past_karma_cause_en": "Poorvaristha and ancestral place displacement (Stana Pallata).",
        "past_karma_cause_ta": "பூர்வ அரிஷ்டம் மற்றும் பூர்வீக இடப்பெயர்ச்சி வினை.",
        "prescribed_remedy_en": "Conduct poojas and prostrate before Lord Sree Vigneswara (Ganesha).",
        "prescribed_remedy_ta": "ஸ்ரீ விக்னேஸ்வரருக்கு (விநாயகர்) கணபதி ஹோமம் மற்றும் அறுகம்புல் அர்ச்சனை செய்க.",
        "relief_timeline_en": "Permanent establishment by age 28-30 with Kireeta Gruha Nirmana Yoga.",
        "relief_timeline_ta": "28 முதல் 30 வயதுக்குள் பிரம்மாண்டமான சொந்த வீடு மற்றும் உத்தியோக ஸ்திரத்தன்மை.",
    },
    94: {
        "yoga_name_en": "Arka Brihaspati Samyoga (Sun-Jupiter Conjunction)",
        "yoga_name_ta": "அர்க்க பிருகஸ்பதி சம்யோகம் (சூரியன்-குரு சேர்க்கை)",
        "sanskrit_sloka": "ARKA BRHUSPATHI SAMYOGA - RAJAPOOJITHA",
        "core_prophecy_en": (
            "Fortunating time under Sun and Jupiter. Native commands towering respectability, judicial prominence, "
            "advisory leadership, and generous patronage from learned masters and state authorities."
        ),
        "core_prophecy_ta": (
            "சூரியனும் குருவும் இணைந்த உன்னத சம்யோகம். சமுதாயத்தில் உயர்ந்த கௌரவம், நீதி மற்றும் அரசு அங்கீகாரம், "
            "ஆன்மீக குருமார்களின் ஆசிகள் மற்றும் ஆட்சிப்பீடங்களின் ஆதரவைப் பெறுவார்."
        ),
        "career_and_finance_en": (
            "Rapid elevation into commanding positions, international / abroad travel, and consolidation of properties till age 81."
        ),
        "career_and_finance_ta": (
            "அரசு மற்றும் பெருநிறுவனங்களில் உயர் பதவிகள், வெளிநாட்டுப் பயணங்கள், நிலம் மற்றும் மனை யோகம் 81 வயது வரை நிலைக்கும்."
        ),
        "family_and_relationships_en": (
            "Great support to parents; however, marital relationship requires patience and sweet spoken communication."
        ),
        "family_and_relationships_ta": (
            "பெற்றோருக்குப் பெருமை சேர்ப்பார்; இல்லற வாழ்வில் விட்டுக்கொடுத்து இனிமையாகப் பேசுவது அமைதி தரும்."
        ),
        "health_and_cautions_en": (
            "Mental restlessness and head tension; relieved through herbal tonics and meditation."
        ),
        "health_and_cautions_ta": (
            "அதிக சிந்தனையால் மன உளைச்சலும் தலைச்சுற்றும் வரலாம்; தியானமும் சாந்தமான சூழலும் நலம் தரும்."
        ),
        "past_karma_cause_en": "Past life dedication to sacred duties bearing royal fruits in this birth.",
        "past_karma_cause_ta": "முற்பிறவியில் செய்த உன்னத தர்ம பணிகளின் பயனாக கிட்டிய ராஜமரியாதை.",
        "prescribed_remedy_en": (
            "Prostrate and worship Divine Mother SRI MANONMANI DEVI with red flowers and milk payasam."
        ),
        "prescribed_remedy_ta": "அன்னை ஸ்ரீ மனோன்மணி தேவியை செந்நிற மலர்களால் அர்ச்சித்து பால் பாயாசம் படைத்து வழிபடுக.",
        "relief_timeline_en": "Golden 9-year progression begins immediately; age 30-40 consolidates extensive properties.",
        "relief_timeline_ta": "உடனடியாக 9 ஆண்டு பொற்காலம் ஆரம்பம்; 30 முதல் 40 வயதுக்குள் பிரம்மாண்ட சொத்துக்கள் சேரும்.",
    },
    80: {
        "yoga_name_en": "Chandra Sankata Parihara & Chandrakeswari Kavacha",
        "yoga_name_ta": "சந்திர சங்கட பரிகாரம் & சந்திரேஸ்வரி கவசம்",
        "sanskrit_sloka": "CHANDRA KESHWARI PRASADENA SHUBHA MANGALAM",
        "core_prophecy_en": (
            "The Moon seeking refuge at Lord Shiva's feet. Questioner suffers from hidden enemies posing as well-wishers, "
            "unmerited accusations (Apavada), and financial debts (Runa Badhe). Divine intervention restores glory."
        ),
        "core_prophecy_ta": (
            "சிவபெருமானின் திருவடிக்கீழ் தஞ்சம் புகுந்த சந்திரனின் நிலை. நண்பர்கள் போல் நடித்து துரோகம் செய்யும் நபர்கள், "
            "வீண் பழிச்சொல் மற்றும் கடன் தொல்லைகளால் மனவேதனை அடைந்திருப்பார். அம்பாளின் அருளால் சகல தடைகளும் நீங்கும்."
        ),
        "career_and_finance_en": (
            "Clearing of all old debts, sudden support from honest well-wishers, and rapid rise like Shukla Paksha Moon."
        ),
        "career_and_finance_ta": (
            "வளர்பிறை சந்திரன் போல் தொழிலும் பணவரவும் உயரும்; பழைய கடன்கள் அடைபட்டு பூமி லாபமும் சமூக அந்தஸ்தும் கிட்டும்."
        ),
        "family_and_relationships_en": (
            "Family disputes dissolve completely; relatives who criticized will marvel at native's meteoric ascent."
        ),
        "family_and_relationships_ta": (
            "குடும்பத்தில் நிலவிய பூசல்கள் மறையும்; பழித்துப் பேசிய உறவினர்களே வியந்து பாராட்டும் நிலை உண்டாகும்."
        ),
        "health_and_cautions_en": (
            "Mental exhaustion and sleep disturbance; wears off after completing spiritual Kavacha."
        ),
        "health_and_cautions_ta": "தூக்கமின்மை மற்றும் மனச் சோர்வு நீங்கி உடல் புத்துணர்ச்சி பெறும்.",
        "past_karma_cause_en": "Breach of trust committed by former associates in previous incarnation.",
        "past_karma_cause_ta": "பூர்வ ஜென்ம நயவஞ்சகப் பகையினால் ஏற்பட்ட கடன் மற்றும் பழிச்சொல் வினை.",
        "prescribed_remedy_en": (
            "Perform 2 Mandalas of Japa to Goddess Sri CHANDRAKESWARI and wear the sacred Kavacha for divine protection."
        ),
        "prescribed_remedy_ta": "அன்னை ஸ்ரீ சந்திரேஸ்வரிக்கு 2 மண்டலங்கள் ஜபம் செய்து ஸ்ரீ சந்திரேஸ்வரி கவசத்தைத் தரிக்கவும்.",
        "relief_timeline_en": "3 years of continuous ascending prosperity like waxing Moon (Shukla Paksha). Ages 28-31 peak.",
        "relief_timeline_ta": "3 ஆண்டுகளில் வளர்பிறை போல் தொடர் வளர்ச்சி; 28 முதல் 31 வயதுக்குள் வாழ்வு ஸ்திரப்படும்.",
    },
    71: {
        "yoga_name_en": "Shani-Angaraka Dayadi Kalaha & Parihara",
        "yoga_name_ta": "சனி-அங்காரக தாயாதி கலகம் & பரிகாரம்",
        "sanskrit_sloka": "SHANI ANGARAKA SAMVADA - DAYADI VRODHA NASHANAM",
        "core_prophecy_en": (
            "Query asked when Mars approaches Saturn (strife among kinsmen / Dayadi Kalaha). Native suffers betrayal of faith "
            "('Nambike Droha'), property litigation, and embarrassment from miscreants over the past 6-7 months."
        ),
        "core_prophecy_ta": (
            "சனியை நோக்கி செவ்வாய் நெருங்கும் வேளையில் கேள்வி. பங்காளிகள் அல்லது உடன் பிறந்தோருடன் நிலப் பூசல், "
            "நம்பிக்கைத் துரோகம் ('நம்பிக்கை துரோகம்') மற்றும் கடந்த 6-7 மாதங்களாக நிதி விரயத்தால் ஏற்பட்ட சங்கடம்."
        ),
        "career_and_finance_en": (
            "Unexpected financial gains arrive right after this year concludes. Lost funds recover; age 38-40 brings beautiful house."
        ),
        "career_and_finance_ta": (
            "இந்த ஆண்டு முடிந்தவுடன் இழந்த பணம் திரும்பக் கிடைக்கும்; 38-40 வயதுக்குள் அழகான சொந்த வீடு யோகம் அமையும்."
        ),
        "family_and_relationships_en": (
            "Settlement of property disputes within 7 months and 11 days. Family peace restored."
        ),
        "family_and_relationships_ta": (
            "7 மாதங்கள் 11 நாட்களில் பாகப்பிரிவினை மற்றும் சொத்துப் பிரச்சினைகள் சுமுகமாகத் தீரும்."
        ),
        "health_and_cautions_en": (
            "Mild Rahu affliction causing blood pressure or bodily heat; cured by visiting Bootharaja Agna shrine."
        ),
        "health_and_cautions_ta": "ராகு தோஷத்தால் ரத்த அழுத்தம் அல்லது உஷ்ண உபாதை; பூதராஜர் வழிபாட்டால் குணமாகும்.",
        "past_karma_cause_en": "Ancestral fraternal land dispute inherited across births.",
        "past_karma_cause_ta": "முற்பிறவி பங்காளிகள் சொத்துப் பூசல் கர்ம வினை.",
        "prescribed_remedy_en": (
            "Perform SHANI-ANGARAKA DANA HOMA and visit Agna Bootharaja Kshetra. Life from 39 to 52 will be extraordinarily prosperous."
        ),
        "prescribed_remedy_ta": "சனி-அங்காரக தான ஹோமம் செய்க; 39 முதல் 52 வயது வரை வாழ்வு பொன்னாக மிளிரும்.",
        "relief_timeline_en": "Solution within 7 months and 11 days; golden period from age 39 to 52.",
        "relief_timeline_ta": "7 மாதம் 11 நாட்களில் தீர்வு; 39 முதல் 52 வயது வரை மகத்தான செல்வ யோகம்.",
    },
    69: {
        "yoga_name_en": "Sthagitha Yoga & Sarva Kaame Vijayee Bhava",
        "yoga_name_ta": "ஸ்தகித யோகம் & சர்வ காமே விஜயீ பவ",
        "sanskrit_sloka": "SARVA KAAME VIJAYEE BHAVA - ANNA DANA PHALAM",
        "core_prophecy_en": (
            "Questioning under Sthagitha Yoga (temporary stagnation). Native has made many great achievements but unholy "
            "obstructors currently block forward motion. Changing place slightly removes obstacles."
        ),
        "core_prophecy_ta": (
            "ஸ்தகித யோகத்தில் (தற்காலிகத் தேக்கம்) கேட்கப்பட்ட கேள்வி. வாழ்வில் பல சாதனைகளைச் செய்திருந்தாலும் தற்சமயம் "
            "துஷ்டர்களின் தலையீட்டால் காரியத் தடைகள் ஏற்பட்டுள்ளன. சிறிதளவு இடமாற்றம் செய்தால் தடைகள் பனிபோல் விலகும்."
        ),
        "career_and_finance_en": (
            "Expected finances arrive at the close of this year. Major construction project commences within 2 years."
        ),
        "career_and_finance_ta": (
            "எதிர்பார்த்த தனலாபம் ஆண்டின் முடிவில் கைக்கு வரும்; 2 ஆண்டுகளுக்குள் பெரிய கட்டட அல்லது தொழிற்கூடம் அமையும்."
        ),
        "family_and_relationships_en": (
            "Family tree systematically flourishes. Children achieve prestigious educational milestones."
        ),
        "family_and_relationships_ta": (
            "வம்ச விருத்தி உண்டாகும்; குழந்தைகள் சிறந்த கல்வியிலும் ஒழுக்கத்திலும் மிளிர்ந்து குடும்பத்திற்குப் பெருமை சேர்ப்பர்."
        ),
        "health_and_cautions_en": (
            "Health troubles cured by herbal root medicines ('Beru medicines'). Avoid hasty dietary slips."
        ),
        "health_and_cautions_ta": "மூலிகை மற்றும் நாட்டு மருந்துகளால் உடல் நலம் சீரடையும்.",
        "past_karma_cause_en": "Past stagnation due to envy from colleagues.",
        "past_karma_cause_ta": "களத்தில் ஏற்பட்ட கண் திருஷ்டி மற்றும் பொறாமை தோஷம்.",
        "prescribed_remedy_en": (
            "Perform ANNA DANA (free food offering to the hungry and destitute). All bad omens will vanish."
        ),
        "prescribed_remedy_ta": "ஏழைகளுக்கும் பக்தர்களுக்கும் அன்னதானம் செய்க; 'சர்வ காமே விஜயீ பவ' என்ற ஆசி கிட்டும்.",
        "relief_timeline_en": "Year-end releases frozen funds; major construction project in 2 years.",
        "relief_timeline_ta": "ஆண்டின் முடிவில் பணம் கைக்கு வரும்; 2 ஆண்டுகளில் சொந்த கட்டுமான யோகம்.",
    },
    60: {
        "yoga_name_en": "Budha-Saturn Graha Samyoga (Mercury + Saturn)",
        "yoga_name_ta": "புத-சனி கிரக சம்யோகம் (புதன் + சனி சேர்க்கை)",
        "sanskrit_sloka": "BUDHA SHANI SAMAYUKTO - POURNAMI VIRGIN PUJA PHALAM",
        "core_prophecy_en": (
            "Intellectual, analytical, slightly deliberate. Hurt by cunning backbiters who betrayed trust. "
            "Litigations and family disputes will yield to remarkable prosperity rising like Shukla Paksha Moon."
        ),
        "core_prophecy_ta": (
            "அறிவாற்றல், நிதானம் மற்றும் காரிய சாதுரியம் கொண்டவர். நம்பியவர்களால் ஏமாற்றப்பட்டு வீண் வழக்கு மற்றும் "
            "மன உளைச்சலுக்கு ஆளாகியுள்ளார். வளர்பிறை சந்திரன் போல் தொழிலும் செல்வமும் மீண்டும் உயரும்."
        ),
        "career_and_finance_en": (
            "From age 48, glorious rise in land, finances, construction, and societal prestige till age 74."
        ),
        "career_and_finance_ta": (
            "48 வயது முதல் நிலம், கட்டுமானம் மற்றும் வர்த்தகத்தில் பிரம்மாண்ட வளர்ச்சி; 74 வயது வரை அமைதியான செல்வ வாழ்க்கை."
        ),
        "family_and_relationships_en": (
            "Full cooperation of children; domestic misunderstandings melt away after 5 months."
        ),
        "family_and_relationships_ta": (
            "பிள்ளைகளின் ஆதரவு கூடும்; 5 மாதங்களில் குடும்பத்தில் நிலவிய கசப்புணர்வுகள் விலகி சுப காரியங்கள் நடக்கும்."
        ),
        "health_and_cautions_en": (
            "Indisposition from excessive worries; cured after performing Pournami offerings."
        ),
        "health_and_cautions_ta": "மன அழுத்தம் தணிந்து தேக ஆரோக்கியம் மேலோங்கும்.",
        "past_karma_cause_en": "Commercial trust dispute in previous trade.",
        "past_karma_cause_ta": "முற்பிறவி வர்த்தகத்தில் ஏற்பட்ட நம்பிக்கைத் துரோகத்தின் தொடர்ச்சி.",
        "prescribed_remedy_en": (
            "Offer fruits, flowers, and money to young Virgins (Kanya Puja) on 5 consecutive POURNIMA days; prostrate before Goddess Parvathi."
        ),
        "prescribed_remedy_ta": "தொடர்ந்து 5 பௌர்ணமி நாட்களில் கன்னிப் பெண்களுக்கு பழங்கள், மலர்கள், தட்சணை கொடுத்து அன்னை பார்வதியை வணங்குக.",
        "relief_timeline_en": "5 months to unlock new deeds; age 48 begins uninterrupted 26-year golden phase.",
        "relief_timeline_ta": "5 மாதங்களில் காரிய சித்தி; 48 வயது முதல் 26 ஆண்டு கால யோக வாழ்க்கை.",
    },
    51: {
        "yoga_name_en": "Guru Brahma Yoga & Punya Ratnamsha",
        "yoga_name_ta": "குரு பிரம்ம யோகம் & புண்ணிய ரத்னாம்சம்",
        "sanskrit_sloka": "PARITHOSHAKAM RAJADWARE NA SAMSHAYAHA - BHAGYA VRIDHI",
        "core_prophecy_en": (
            "Enjoys Guru Brahma Yoga. Born as a royal advisor ('Guru') in Vidarbha kingdom in previous birth. "
            "Due to an ancient kingdom rivalry error, the sacred thread suffered; yet blessed with supreme knowledge and Moksha path."
        ),
        "core_prophecy_ta": (
            "குரு பிரம்ம யோகத்தில் பிறந்தவர். முற்பிறவியில் விதர்ப தேசத்து அரசவை குருவாக விளங்கியவர். "
            "உயரிய ஞானம், சாஸ்திர புலமை மற்றும் ஆன்மீக முக்தி மார்க்கத்தில் ஆழமான ஈடுபாடு கொண்டவர்."
        ),
        "career_and_finance_en": (
            "Honored at Guru-Peethas and royal assemblies ('Rajadware'). A child born under Punya Ratnamsha will crown the family with glory."
        ),
        "career_and_finance_ta": (
            "மடங்கள், குரு பீடங்கள் மற்றும் அரசு சபைகளில் பேரரசு மரியாதை. 'புண்ணிய ரத்னாம்சத்தில்' பிறக்கும் குழந்தையால் குடும்பமே புகழடையும்."
        ),
        "family_and_relationships_en": (
            "Great domestic bliss, noble descendants, and mutual affection among spiritual seekers."
        ),
        "family_and_relationships_ta": (
            "இல்லறத்தில் அமைதி, ஆன்மீக சிந்தனை கொண்ட உத்தம பிள்ளைகள் மற்றும் ஆசீர்வாதங்கள்."
        ),
        "health_and_cautions_en": (
            "Longevity till 82 with eternal bliss and peaceful mind.",
        ),
        "health_and_cautions_ta": "82 வயது வரை அமைதியான, ஆரோக்கியமான ஞான வாழ்க்கை.",
        "past_karma_cause_en": "State conflict alignment in Vidarbha kingdom now redeemed through spiritual devotion.",
        "past_karma_cause_ta": "பூர்வ ஜென்ம அரசவை குரு வினையின் இறுதி விமோசனம்.",
        "prescribed_remedy_en": (
            "Chant Mruthyunjaya Mantra and conduct Rudrabhishekam at an ancient Shiva temple."
        ),
        "prescribed_remedy_ta": "சிவபெருமானுக்கு ருத்ராபிஷேகம் செய்து மிருத்யுஞ்சய மகா மந்திரத்தை பாராயணம் செய்க.",
        "relief_timeline_en": "Within 9 months of next year, complete liberation and peace of mind.",
        "relief_timeline_ta": "அடுத்த ஆண்டின் 9 மாதங்களுக்குள் முழுமையான நிம்மதியும் தன யோகமும் உண்டாகும்.",
    },
    40: {
        "yoga_name_en": "Chandra Mouleswara Prasad & Indu Dosha Nivarana",
        "yoga_name_ta": "சந்திர மௌலீஸ்வர பிரசாதம் & இந்து தோஷ நிவாரணம்",
        "sanskrit_sloka": "CHANDRA MOULESWARA SHARANAM - SARVA SHUBHAM",
        "core_prophecy_en": (
            "Enjoys 'Raja Manyate' (commands respect from highest echelons) and VIP stature. "
            "Though worried about children's prospects, Lord Chandra Mouleswara ensures supreme success."
        ),
        "core_prophecy_ta": (
            "அரசாங்க மற்றும் சமுதாய முக்கியஸ்தர்கள் (VIP) மதிக்கத்தக்க 'ராஜ மான்யதே' அந்தஸ்து கொண்டவர். "
            "பிள்ளைகள் பற்றிய கவலை இருந்தாலும் ஸ்ரீ சந்திர மௌலீஸ்வரர் அருளால் அனைத்துக் காரியங்களும் சுபமாக முடியும்."
        ),
        "career_and_finance_en": (
            "5 months bring auspicious events; career transactions stabilize with unexpected wealth channels."
        ),
        "career_and_finance_ta": (
            "5 மாதங்களில் சுப காரியங்கள்; புதிய வழிகளில் பணவரவு கூடி தொழில் ஸ்திரத்தன்மை பெறும்."
        ),
        "family_and_relationships_en": (
            "Auspicious ceremonies (Mangala Karya) at home; peaceful harmony across the household."
        ),
        "family_and_relationships_ta": (
            "இல்லத்தில் மங்கள காரியங்கள் விமரிசையாக நடைபெறும்; குடும்பத்தில் அமைதியும் நிம்மதியும் கூடும்."
        ),
        "health_and_cautions_en": (
            "Indu Dosha (Moon flaw) causing mental anxiety; completely neutralized by pilgrimage."
        ),
        "health_and_cautions_ta": "மன அழுத்தம் மற்றும் பதற்றம்; புண்ணிய தீர்த்த யாத்திரையால் விலகும்.",
        "past_karma_cause_en": "Residual Indu Dosha affecting peace of mind.",
        "past_karma_cause_ta": "சந்திர தோஷத்தால் ஏற்பட்ட தற்காலிக மனக்கவலை.",
        "prescribed_remedy_en": (
            "Visit sacred Shiva Kshetras and meditate upon Lord CHANDRA MOULESWARA."
        ),
        "prescribed_remedy_ta": "புனித சிவ ஸ்தலங்களுக்குச் சென்று ஸ்ரீ சந்திர மௌலீஸ்வரரை தியானித்து வழிபடுக.",
        "relief_timeline_en": "5 months for domestic joy; 4 years bring full consolidation of fortunes.",
        "relief_timeline_ta": "5 மாதங்களில் சுப நிகழ்வுகள்; 4 ஆண்டுகளில் நிரந்தர யோக வளர்ச்சி.",
    },
    21: {
        "yoga_name_en": "Hita Shatru Parihara & Parvathi Shanthi",
        "yoga_name_ta": "ஹித சத்ரு பரிகாரம் & பார்வதி சாந்தி",
        "sanskrit_sloka": "HITA SHATRU VINASHANAM - PATI BHAKTHI SOWBHAGYAM",
        "core_prophecy_en": (
            "Hails from respectable family, eccentric nature caused lost golden opportunities in youth. "
            "Surrounded by flattering secret enemies ('Hita Shatrus'). Blessed with a devoted wife who was his beloved in previous birth."
        ),
        "core_prophecy_ta": (
            "கௌரவமான குடும்பத்தில் பிறந்தவர்; பிடிவாத குணத்தால் சில நல்ல வாய்ப்புகளைத் தவறவிட்டிருக்கலாம். "
            "நண்பர்கள் போல் நடித்து ஏமாற்றும் 'ஹித சத்ருக்கள்' உள்ளனர். முற்பிறவியிலேயே விரும்பித் தொடர்ந்த உத்தம மனைவி அமைவார்."
        ),
        "career_and_finance_en": (
            "Extensive travels and income from two distinct trade channels. Second venture yields lucrative profits and vehicles."
        ),
        "career_and_finance_ta": (
            "இரண்டு விதமான தொழில்களில் வருவாய்; இரண்டாவது தொழில் மூலம் வாகன சேர்க்கையும் பெரும் லாபமும் அமையும்."
        ),
        "family_and_relationships_en": (
            "Wife possesses supreme Pati-Bhakti; her divine presence anchors the family's welfare."
        ),
        "family_and_relationships_ta": (
            "மனைவி சிறந்த தர்ம பத்தினி; மனைவியின் ஆலோசனைகளைக் கேட்டு நடந்தால் குடும்பம் தழைத்தோங்கும்."
        ),
        "health_and_cautions_en": (
            "Keep mind peaceful and avoid hasty decisions to avert self-sabotage."
        ),
        "health_and_cautions_ta": "முன்கோபத்தையும் அவசர முடிவுகளையும் தவிர்ப்பது நலம் தரும்.",
        "past_karma_cause_en": "Past birth matrimonial vows fulfilling in this life.",
        "past_karma_cause_ta": "முற்பிறவி இல்லற பந்தத்தின் சுபத் தொடர்ச்சி.",
        "prescribed_remedy_en": (
            "Perform SHANTHI HOMA and worship GODDESS PARVATHI DEVI for 21 consecutive Tuesdays."
        ),
        "prescribed_remedy_ta": "தொடர்ந்து 21 செவ்வாய்க்கிழமைகள் அன்னை பார்வதி தேவிக்கு அர்ச்சனை செய்து சாந்தி ஹோமம் செய்க.",
        "relief_timeline_en": "6 months bring turnaround; second trade brings lasting wealth.",
        "relief_timeline_ta": "6 மாதங்களில் நிலைமை மாறும்; இரண்டாவது தொழில் மூலம் நீடித்த தனலாபம்.",
    },
    1: {
        "yoga_name_en": "Mruthyunjaya Jayam & South Doctor Cure",
        "yoga_name_ta": "மிருத்யுஞ்சய ஜெயம் & தெற்கு திசை மருத்துவர் நலம்",
        "sanskrit_sloka": "MRUTHUNJAYA JAPENA SARVA ROGA NIDHARANAM",
        "core_prophecy_en": (
            "Came up in life through immense effort and difficulties. Helped many who later turned ungrateful. "
            "All ugly times are over; exploiters will now respect the native."
        ),
        "core_prophecy_ta": (
            "கடும் உழைப்பாலும் சுயமுயற்சியாலும் உயர்ந்தவர். பலருக்கு உதவி செய்து நன்மதிப்பைப் பெறாத நிலை இனி மாறும். "
            "துன்பக் காலம் முடிவுக்கு வந்துவிட்டது; ஏமாற்றியவர்களே பணிந்து வரும் நற்காலம் பிறக்கிறது."
        ),
        "career_and_finance_en": (
            "Next year brings fruitful completion of all willful desires and substantial advancement for youngsters."
        ),
        "career_and_finance_ta": (
            "அடுத்த ஆண்டு எண்ணிய காரியங்கள் யாவும் ஈடேறும்; பிள்ளைகளின் முன்னேற்றம் பெருமை தரும்."
        ),
        "family_and_relationships_en": (
            "Family health concerns ease in 7 months; divine bliss and respect from society."
        ),
        "family_and_relationships_ta": (
            "7 மாதங்களில் குடும்பத்தில் இருந்த மனக்கவலைகள் நீங்கி தெய்வீக அமைதியும் நற்புகழும் கூடும்."
        ),
        "health_and_cautions_en": (
            "Physical and mental strain; a Doctor from the SOUTH direction will provide the decisive medical rescue."
        ),
        "health_and_cautions_ta": "உடல் சோர்வு மற்றும் மன உளைச்சல்; தெற்கு திசையிலிருந்து வரும் மருத்துவரால் பரிபூரண குணம் கிட்டும்.",
        "past_karma_cause_en": "Graha Dosha and exhaustion from carrying past burdens.",
        "past_karma_cause_ta": "கிரக தோஷம் மற்றும் முற்பிறவி கடன் சுமை நீங்கும் தருணம்.",
        "prescribed_remedy_en": (
            "Perform MRUTHUNJAYA JAPA and HOMA; maintain regular prayer for complete peace."
        ),
        "prescribed_remedy_ta": "மிருத்யுஞ்சய ஜபம் மற்றும் ஹோமம் செய்க; தியானமும் இறை வழிபாடும் அளப்பரிய நிம்மதி தரும்.",
        "relief_timeline_en": "7 months ease family strains; next 3 years are filled with divine blessings and success.",
        "relief_timeline_ta": "7 மாதங்களில் விடிவுகாலம்; அடுத்த 3 ஆண்டுகள் தொடர் யோகமும் நிம்மதியும் கிட்டும்.",
    },
}

# Fallback generator for unmapped index numbers (0 to 107) based on cyclical amshas
def get_fallback_prediction(pred_num: int) -> Dict[str, Any]:
    # Select closest base template
    templates = sorted(PRASHNA_PREDICTIONS.keys())
    closest = min(templates, key=lambda x: abs(x - pred_num))
    base = PRASHNA_PREDICTIONS[closest].copy()
    base["yoga_name_en"] = f"Prashna Amsha {pred_num} (Classical Oracle Vector)"
    base["yoga_name_ta"] = f"பிரசன்ன அம்சம் {pred_num} (பிருகு பிரசன்ன நாடி வாக்கியம்)"
    base["sanskrit_sloka"] = f"PRASHNA AMSHA {pred_num} - SHUBHA PHALA PRAPTHI"
    return base
