# -*- coding: utf-8 -*-
"""
Planetary House Predictions for Saturn (சனி), Rahu (ராகு), and Ketu (கேது)
Based on Dr. B. V. Raman's "How to Judge a Horoscope" & Classical Saravali
"""

SATURN_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (சச யோகம் / இரும்பு போன்ற மன உறுதி & உழைப்பு)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Sasa Yoga / Iron Will & Enduring Discipline)",
        "core_traits_ta": [
            "ஆழ்ந்த சிந்தனை, பக்குவமான முதிர்ச்சி, அடக்கம் மற்றும் இரும்பு போன்ற விடாமுயற்சி கொண்டவர்.",
            "இளமைக் காலத்தில் போராட்டங்களையும் தடைகளையும் சந்தித்தாலும், தனது சுய உழைப்பால் பிற்காலத்தில் மாபெரும் உச்சியை அடைவார்.",
            "மானமரியாதைக்கு முதலிடம் கொடுப்பவர்; எவரிடமும் வீணாகக் கையேந்தாத சுயசார்பு குணம் உடையவர்.",
            "அமைதியான முகம், சில சமயம் சோர்வான தோற்றம் அல்லது மெலிந்த உடல்வாகு அமைந்திருக்கலாம்; காற்று/வாத தேகம்.",
            "பொறுமையும் விவேகமும் இவரின் மாபெரும் பலமாகும்; காலத்தின் அருமையை உணர்ந்து காரியம் சாதிப்பார்."
        ],
        "core_traits_en": [
            "Profound gravity, mature wisdom, stoic endurance, and unyielding perseverance.",
            "Encounters early hardships and uphill struggles, yet ascends steadily through self-exertion to peak worldly eminence.",
            "Fiercely guarded self-respect and integrity; refuses unearned charity or degrading compromises.",
            "Lean, spare physique with contemplative, serious eyes; melancholic or vata-dominated constitution.",
            "Supreme patience and discipline are his greatest weapons; triumphs through the inexorable compound power of time."
        ],
        "strong_placement_ta": [
            "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் (Sasa Yoga) அமைந்தால்: லட்சக்கணக்கான உழைப்பாளர்களை வழிநடத்தும் மக்கள் தலைவர், தொழில் அதிபர்.",
            "நீண்ட ஆயுள், பரந்த நிலபுலன்கள், சுரங்கங்கள் மற்றும் சமுதாயத்தில் அழியாத செல்வாக்கு கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted in Libra or in own signs Capricorn/Aquarius forming Sasa Mahapurusha Yoga: Legendary mass leader of the working class, industrial baron.",
            "Exceptional longevity, vast landed estates, mining concessions, and enduring civic authority."
        ],
        "weak_placement_ta": [
            "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மந்த நிலை, சோம்பல், மூட்டு வலி மற்றும் நரம்புத் தளர்ச்சி.",
            "காரணமற்ற அவநம்பிக்கை, தனிமை பயம் மற்றும் முயற்சிகளில் தொடர்ந்து தடைகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Chronic lethargy, articular rheumatism, spinal curvature, and melancholy.",
            "Persistent self-doubt, morbidity, social withdrawal, and frustrating career bottlenecks."
        ],
        "career_wealth_ta": [
            "தொழிலாளர் நலத்துறை, சுரங்கத் தொழில், இரும்பு மற்றும் எஃகு உற்பத்தி, நீதித்துறை, தொல்பொருள் ஆராய்ச்சி, விவசாயம்.",
            "சொந்த உழைப்பாலும் கடினமான பணிகளாலும் நிலையான, நீண்ட காலச் சொத்துகள் சேரும்."
        ],
        "career_wealth_en": [
            "Thrives in labor union leadership, mining exploration, metallurgy, criminal judiciary, archaeology, and heavy civil construction.",
            "Builds indestructible long-term capital assets through disciplined sweat and patient compounding."
        ],
        "health_precautions_ta": [
            "மூட்டு வலி, வாதக் கோளாறுகள் (Arthritis), எலும்பு பலவீனம், மலச்சிக்கல் மற்றும் தோல் வறட்சி.",
            "எண்ணெய் தேய்த்துக் குளிப்பதும், உடற்பயிற்சியும், சூடான புதிய உணவுகளை உண்பதும் வாதத்தைத் தணிக்கும்."
        ],
        "health_precautions_en": [
            "Prone to rheumatoid arthritis, bone density loss, chronic constipation, and dry eczema.",
            "Weekly warm sesame oil self-massages, mobility drills, and warm grounding meals subdue vata."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (சிக்கனம், உழைப்பால் தனம் & நிதான வாக்கு)",
        "house_title_en": "2nd House - Dhana Bhava (Frugality, Self-Earned Riches & Measured Speech)",
        "core_traits_ta": [
            "பேச்சில் நிதானம், ஆழ்ந்த அர்த்தம் மற்றும் குறைத்துப் பேசும் சுபாவம்; வீண் பேச்சுகளைத் தவிர்ப்பார்.",
            "பணத்தின் அருமையை உணர்ந்து சிக்கனமாகச் செலவு செய்வார்; ஒரு காசையும் வீணாக்க மாட்டார்.",
            "குடும்பத்தில் பொறுப்புமிக்க மனிதராக இருந்து அனைவருக்கும் வழிகாட்டுவார்.",
            "நிலம், பழைய பொருட்கள், இரும்பு மற்றும் பூமி சார்ந்த தொழில்களில் தன லாபம் ஈட்டுவார்."
        ],
        "core_traits_en": [
            "Measured, deliberate, and laconic speech; prefers meaningful silence over superficial chatter.",
            "Acute financial discipline and frugality; abhors wasteful indulgence and safeguards every penny.",
            "Acts as the responsible, dependable pillar of the family through trials.",
            "Innate commercial instincts for scrap recycling, heavy hardware, commodities, and agricultural lands."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான நிலங்கள், இரும்பு ஆலைகள், பரம்பரைச் சொத்துகள் குவியும்.",
            "அரசாங்கத் கருவூலங்கள் மற்றும் நிதி நிறுவனங்களில் உயர் பொறுப்புகள் வகித்து நற்பெயர் பெறுவார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows colossal real estate holdings, steel foundries, and robust generational liquidity.",
            "Entrusted with sovereign treasuries and premier fiscal directorships."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான பேச்சு, குடும்பத்தில் விரிசல், பண நெருக்கடிகள்.",
            "வலது கண்ணில் பார்வைக் குறைபாடு அல்லது பற்களில் சொத்தை வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Harsh, biting speech causing broken family ties; protracted financial insolvency.",
            "Prone to right-eye cataracts, periodontal degeneration, and severe dental cavities."
        ],
        "career_wealth_ta": [
            "பழைய இரும்பு வர்த்தகம், நிலக்கரி, பெட்ரோலியம், கனரக வாகன உதிரிபாகங்கள், தோல் தொழில், தணிக்கை.",
            "விடாமுயற்சியாலும் சிறுகச் சிறுகச் சேமிப்பதாலும் பெருஞ்செல்வந்தராக உயருவார்."
        ],
        "career_wealth_en": [
            "High returns in metal scrap recycling, coal/oil extraction, heavy equipment salvage, and forensic auditing.",
            "Rises to profound wealth through patient compounding and frugal asset conservation."
        ],
        "health_precautions_ta": [
            "பல் வலி, ஈறுகளில் ரத்தம் வடிதல், தொண்டை வறட்சி, வலது கண் பார்வை மங்குதல் மற்றும் முகத்தில் கரும் புள்ளிகள்.",
            "பல் ஆரோக்கியத்தையும், கண்களுக்கான வைட்டமின் உணவுகளையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
        ],
        "health_precautions_en": [
            "Susceptible to periodontal disease, vocal dryness, right-eye optic strain, and facial blemishes.",
            "Routine dental checkups and ocular vitamin A & lutein supplementation are essential."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 101) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசைக்க முடியாத வீரம் & வெற்றி)",
        "house_title_en": "3rd House - Sahaja Bhava (Invincible Fortitude & Upachaya Triumph)",
        "core_traits_ta": [
            "சனி 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், தளராத மன உறுதியையும் தரும் சிறந்த யோகமாகும்.",
            "எந்தவிதமான சோதனைகளையும் துணிவுடன் தாங்கி வெல்லும் ஆற்றல்; எதிரிகளைத் தன் அமைதியாலும் வியூகத்தாலும் வீழ்த்துவார்.",
            "செயல்வீரர்; வார்த்தைகளை விட தன் கடுமையான உழைப்பால் வெற்றிகளை நிரூபித்துக் காட்டுவார்.",
            "இளைய சகோதரர்களிடம் சற்று கண்டிப்பு காட்டினாலும் அவர்களுக்கு அரணாக நிற்பார்."
        ],
        "core_traits_en": [
            "Saturn in the 3rd (an Upachaya house) is classically venerated as a formidable engine of heroic resilience and steady victory.",
            "Possesses titanic endurance to absorb life's shocks; outmaneuvers adversaries through strategic patience.",
            "Man of solid action rather than boastful words; proves worth through undeniable accomplishments.",
            "Demanding yet fiercely protective guardian to younger siblings."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடெங்கும் புகழ், ராணுவம்/காவல்துறையில் மிக உயரிய தலைமை, மாபெரும் சாதனைகள்.",
            "எடுத்த முயற்சிகள் யாவும் தாமதமானாலும் அசுர வெற்றியடைந்து சரித்திரத்தில் இடம்பிடிக்கும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Confers far-reaching fame, top command in police or armed forces, and heroic stature.",
            "All ventures culminate in monumental success; builds an enduring legacy of gritty triumph."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் நிலத்தகராறு, கைகளில் நரம்பு வலி.",
            "காரணமற்ற பயமும் தயக்கமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Acrimonious sibling disputes over inheritances, upper arm numbness, and chronic fatigue.",
            "Paralyzing indecision and pessimistic hesitation sabotaging key commercial openings."
        ],
        "career_wealth_ta": [
            "காவல்துறை, ராணுவ தளவாடங்கள், போக்குவரத்து கழகங்கள், ரயில்வே, அச்சு மற்றும் கூரியர் தொழில், விளையாட்டு.",
            "கடின உழைப்பாலும் மூலோபாய திட்டங்களாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Superlative success in policing, defense logistics, railway syndicates, courier networks, and athletics.",
            "Amasses substantial capital through strategic resilience and industrial transport contracts."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை மற்றும் எலும்பு முறிவுகள்.",
            "முறையான கைகளுக்கான உடற்பயிற்சிகளும், எலும்புகளுக்கு கால்சியம் சத்தும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to shoulder frozen syndrome, brachial neuralgia, auditory nerve dullness, and bone fractures.",
            "Upper body mobility routines and dietary calcium-vitamin D3 optimization maintain structural strength."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (சச யோகம் / பூமி லாபம், பழைய சொத்துகள் & ஆழமான அமைதி)",
        "house_title_en": "4th House - Sukha Bhava (Sasa Yoga / Landed Acquisitions & Deep Contemplation)",
        "core_traits_ta": [
            "பழமையான வீடுகள், பாரம்பரிய நிலங்கள், தோட்டங்கள் மற்றும் விவசாயப் பண்ணைகளை வாங்குவதில் ஆர்வம்.",
            "வீட்டிலும் குடும்பத்திலும் ஒழுக்கமும் கட்டுப்பாடும் நிலவ வேண்டும் என கண்டிப்பாக இருப்பார்.",
            "மனதில் ஆழ்ந்த அமைதியும் தத்துவ சிந்தனைகளும் இருக்கும்; சில சமயம் காரணமற்ற தனிமை உணர்வு எட்டிப்பார்க்கும்.",
            "தாயாரின் நலனில் மிகுந்த அக்கறை காட்ட வேண்டும்; தாய்வழியில் பக்குவமும் ஆசியும் கிட்டும்."
        ],
        "core_traits_en": [
            "Passion for acquiring ancient heritage properties, agricultural acreage, sprawling orchards, and rustic estates.",
            "Enforces strict Spartan discipline and order within the domestic household.",
            "Possesses a deeply contemplative, philosophical inner life, punctuated by periodic monastic solitude.",
            "Requires attentive care for mother's health; absorbs profound maternal stoicism and wisdom."
        ],
        "strong_placement_ta": [
            "துலாத்தில் உச்சம் அல்லது சொந்த வீட்டில் சச யோகம் அமைந்தால்: பல ஏக்கர் நிலங்கள், பண்ணை மாளிகைகள், கௌரவப் பதவிகள்.",
            "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, விவசாயம் மற்றும் சுரங்கத் துறையில் பெரும் செல்வந்தராக வாழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted in Libra or own signs forming Sasa Yoga: Vast acreage of prime lands, rustic country palaces, and civic honors.",
            "Amasses profound wealth in agrarian conglomerates and mineral extraction."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் வாதக் கோளாறுகள், பூர்வீக சொத்துகளில் இழப்பு, வீட்டு விபத்துகள்.",
            "வாகனங்களால் செலவுகளும், பூர்வீக வீட்டை விட்டுப் பிரியும் சூழ்நிலையும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Maternal rheumatoid ailments, loss of ancestral manor to debts, and vehicular accidents.",
            "Chronic domestic gloom, dilapidated home conditions, and forced relocation."
        ],
        "career_wealth_ta": [
            "விவசாயப் பண்ணைகள், சுரங்கத் தொழில், நிலக்கரி, செங்கல் சூளைகள், பழைய வாகன வர்த்தகம், ரியல் எஸ்டேட்.",
            "பூமி பரிவர்த்தனைகளாலும் விவசாயத்தாலும் தலைமுறைக்கு நிலைக்கும் சொத்துகள் சேரும்."
        ],
        "career_wealth_en": [
            "Thrives in commercial farming, quarrying, coal energy, brick kilns, salvage automotive yards, and realty.",
            "Builds immense generational equity anchored in tangible land parcels."
        ],
        "health_precautions_ta": [
            "நெஞ்சு சளி, இருதய பலவீனம், ஆஸ்துமா, மூட்டு வலி மற்றும் மன அழுத்தம்.",
            "சூடான மூலிகைக் குடிநீரும், பிராணாயாமப் பயிற்சிகளும் நுரையீரல் நலனைக் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to bronchial asthma, coronary sclerosis, articular stiffness, and melancholic depression.",
            "Warm herbal decoctions, breathwork pranayama, and avoiding damp basements preserve vigor."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (ஆழ்ந்த ஆராய்ச்சி / தத்துவ புத்தி & பிற்கால யோகம்)",
        "house_title_en": "5th House - Putra Bhava (Deep Analytical Intellect & Eventual Progeny Triumph)",
        "core_traits_ta": [
            "ஆழ்ந்த சிந்தனை, ஆராய்ச்சி மனப்பான்மை, வரலாற்றுப் பற்று மற்றும் எதையும் எளிதில் நம்பாத விவேகமான புத்தி.",
            "புத்திர பாக்கியம் சற்று காலதாமதமாக அமைந்தாலும், பிற்காலத்தில் குழந்தைகள் பெரும் சாதனையாளர்களாகத் திகழ்வார்கள்.",
            "பூர்வ புண்ணியத்தில் ஆரம்பத்தில் சோதனைகள் இருந்தாலும், 36 வயதுக்குப் பிறகு அசைக்க முடியாத யோகம் செயல்படும்.",
            "பங்குச் சந்தை போன்ற சூதாட்டங்களைத் தவிர்த்து, நீண்ட கால நிலையான முதலீடுகளில் மட்டுமே ஈடுபடுவார்."
        ],
        "core_traits_en": [
            "Profound analytical intellect, deep historical interest, scientific skepticism, and rigorous logical discipline.",
            "Childbearing may experience delays, yet progeny mature into exceptionally responsible, accomplished pillars of society.",
            "Past-life karma demands early trials, unlocking magnificent unshakeable fortune after age 36.",
            "Shuns speculative day-trading, anchoring wealth exclusively in disciplined long-term compounding."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: உலகப் புகழ் பெற்ற தத்துவ அறிஞர், விஞ்ஞானி, பிற்காலத்தில் மாபெரும் கோடீஸ்வர யோகம்.",
            "குழந்தைகள் உயர் அரசுப் பதவிகளை அடைவார்கள்; குடும்பத்திற்கு அழியாத புகழையும் பெருமையையும் சேர்ப்பார்கள்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Renowned scientific philosopher, master investigator, and multi-millionaire through patient compounding.",
            "Progeny attain apex judicial or administrative ranks, elevating lineage honors."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கடும் தடைகள், பிள்ளைகளுடன் கருத்து மோதல்கள்.",
            "தவறான நிதித் திட்டங்களால் சேமிப்பு விரயமாதல் மற்றும் மன அமைதியின்மை."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe delay or heartache regarding children; ideological alienation from firstborn.",
            "Heavy financial erosion from rigid, outdated investment schemes."
        ],
        "career_wealth_ta": [
            "ஆராய்ச்சி விஞ்ஞானி, வரலாற்றுப் பேராசிரியர், தத்துவ ஆசிரியர், நில அளவையாளர், சுரங்கப் பொறியாளர், தொல்பொருள் துறை.",
            "நீண்ட கால முதலீடுகளாலும் அறிவுசார் ஆய்வுகளாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Distinction as research scientist, history dean, philosopher, geodesic surveyor, petroleum engineer, and archaeologist.",
            "Vast capital accumulated via long-horizon equity value-investing and research grants."
        ],
        "health_precautions_ta": [
            "அஜீரணம், மலச்சிக்கல், குடல் வாதம், கல்லீரல் மந்தம் மற்றும் மன அழுத்தம்.",
            "நார்ச்சத்து மிகுந்த உணவுகளையும், வெதுவெதுப்பான நீரையும் அருந்துவது செரிமானத்திற்கு உதவும்."
        ],
        "health_precautions_en": [
            "Prone to sluggish peristalsis, chronic constipation, irritable bowel spasms, and hepatic torpor.",
            "High-fiber dietary intake, abundant warm water, and physical movement keep gut healthy."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (அசைக்க முடியாத சத்ரு ஜெயம் / மகா உபசய யோகம்)",
        "house_title_en": "6th House - Satru Bhava (Unassailable Conquest of Enemies & Grand Upachaya Power)",
        "core_traits_ta": [
            "சனி 6-ஆம் பாவத்தில் அமைவது ஜாதகத்திற்கு மாபெரும் கவசமாகும்; எதிரிகள் தானாகவே அடிபணிவர்.",
            "எந்தவிதமான வழக்குகள், போட்டிகள் மற்றும் கடன் தொல்லைகளையும் தன் விடாமுயற்சியால் அடியோடு தீர்த்து வைப்பார்.",
            "இரும்பு போன்ற நோய் எதிர்ப்புச் சக்தி; கடுமையான உழைப்பையும் தாங்கும் திடகாத்திரமான உடல்வாகு.",
            "பணியாளர்களையும் தொழிலாளர்களையும் அன்பாலும் ஒழுக்கத்தாலும் தன் கட்டுப்பாட்டில் வைத்திருப்பார்."
        ],
        "core_traits_en": [
            "Saturn in the 6th is classically celebrated as an invincible fortress; crushes all adversaries and hostility.",
            "Eliminates litigations, legal disputes, and financial debts through relentless, unyielding stamina.",
            "Possesses iron physical stamina, supreme immune resilience, and boundless work capacity.",
            "Commands total loyalty and high productivity from manual laborers and subordinates."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, நீதித்துறை/தொழிலாளர் நலத்துறையில் சர்வாதிகார அதிகாரம்.",
            "அளப்பரிய செல்வம், கடன் இல்லாத வாழ்க்கை மற்றும் போட்டிகளில் தொடர் வெற்றிகள் குவியும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows complete Shatru Samhara Yoga! Total eradication of foes, supreme judicial/labor command.",
            "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீராத வாத நோய்கள், மூட்டு வலி, கடன் சுமைகளால் மன உளைச்சல்.",
            "வேலையாட்களால் வழக்குகள், திருட்டு அல்லது தாய்மாமனுடன் கடுமையான விரோதம் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Chronic rheumatologic disorders, gout, and anxiety over unpaid liabilities.",
            "Troublesome labor strikes, employee embezzlement, and bitter feuds with maternal uncles."
        ],
        "career_wealth_ta": [
            "தொழிலாளர் தீர்ப்பாயம், குற்றவியல் சட்டம், சுரங்க நிர்வாகம், கனரக இயந்திர பராமரிப்பு, பொது சுகாதாரம், சிறைத்துறை.",
            "போட்டிகளையும் சவால்களையும் தனக்குச் சாதகமாக மாற்றி கோடிக்கணக்கில் வருவாய் ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Dominates in labor tribunal arbitration, criminal trial law, mining logistics, correctional administration, and sanitation.",
            "Extracts substantial financial wealth directly from crisis management and competitive victories."
        ],
        "health_precautions_ta": [
            "மூட்டு வலி (Rheumatism), இடுப்பு வாதம், குடல் புண்கள், ஆசனவாய் வெடிப்பு மற்றும் தோல் நோய்கள்.",
            "உடலில் வாதத்தைக் குறைக்கும் எளிய சமைத்த உணவுகளும், வெந்நீர் ஒத்தடமும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to articular rheumatism, lumbar sciatica, peptic ulcers, anal fissures, and eczema.",
            "Adopt an anti-inflammatory vata-pacifying diet, warm baths, and avoid cold drafts."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (சச யோகம் / பக்குவமான துணை & காலதாமத திருமணம்)",
        "house_title_en": "7th House - Kalathra Bhava (Sasa Yoga / Mature Spouse & Delayed Nuptials)",
        "core_traits_ta": [
            "சனி 7-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று சச யோகத்தை (Sasa Yoga) உருவாக்குகிறார்.",
            "திருமணம் சற்று காலதாமதமாக அமைவது நல்லது; வாழ்க்கைத் துணை மிகுந்த பக்குவமும், பொறுப்பும், அடக்கமும் கொண்டவராக இருப்பார்.",
            "வாழ்க்கைத் துணையுடன் நிலையான, பிரிக்க முடியாத ஆழமான பந்தம் இருக்கும்; விட்டுக் கொடுத்துச் செல்வது அமைதி தரும்.",
            "கூட்டு வர்த்தகத்தில் நேர்மையும், நம்பகத்தன்மையும் கொண்டவர்களுடன் மட்டுமே ஒப்பந்தம் செய்து சாதிப்பார்."
        ],
        "core_traits_en": [
            "Saturn attains supreme Digbala (directional potency) in the 7th, generating the prestigious Sasa Mahapurusha Yoga.",
            "Marriage is typically solemnized later in life; spouse is mature, highly responsible, prudent, and stoic.",
            "Marital bond is cemented by enduring loyalty and shared duties rather than fleeting frivolity.",
            "Conducts commercial partnerships exclusively with seasoned, trustworthy, and battle-tested veterans."
        ],
        "strong_placement_ta": [
            "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் அமைந்தால்: நாட்டின் முன்னணி தொழில் சாம்ராஜ்ய அதிபர், பன்னாட்டு ஒப்பந்தங்கள்.",
            "வாழ்க்கைத் துணையால் மாபெரும் சொத்துகளும் கௌரவங்களும் வந்து சேரும்; இல்லறத்தில் பூரண அமைதி நிலவும்."
        ],
        "strong_placement_en": [
            "Exalted in Libra or own signs with Sasa Yoga: Industrial titan, commands multinational syndicates and supreme civic prestige.",
            "Spouse brings vast ancestral estates and stability; union is universally respected for steadfast dignity."
        ],
        "weak_placement_ta": [
            "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடுமையான விரிசல், துணையின் ஆரோக்கியம் பாதித்தல்.",
            "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்பட்டு பெரும் நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Cold, acrimonious marital friction; spouse suffers from chronic rheumatologic ailments.",
            "Heavy financial loss through unscrupulous business partners and protracted arbitration."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், கனரக இயந்திர ஏற்றுமதி, தொழிலாளர் சங்கம், சட்ட ஒப்பந்தங்கள், ரியல் எஸ்டேட் கூட்டாண்மை.",
            "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் விடாமுயற்சியாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Thrives in international mineral export, heavy hardware trade, collective bargaining mediation, and commercial realty.",
            "Substantial capital accumulation achieved through joint commercial endurance and steady expansion."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கற்கள், வாதக் கோளாறுகள், அடிவயிற்றில் வலி மற்றும் பாலியல் பலவீனம்.",
            "முறையான குடிநீர் அருந்துதலும், உடலை சூடாக வைத்திருப்பதும் ஆரோக்கியத்திற்கு உதவும்."
        ],
        "health_precautions_en": [
            "Susceptible to renal calculi, pelvic sciatica, chronic urinary sluggishness, and reproductive fatigue.",
            "Ample warm hydration, keeping lumbar region warm, and periodic urological screenings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (பூரண தீர்க்காயுள் / ஆயுள்காரகன் அஷ்டமத்தில் அமர்தல்)",
        "house_title_en": "8th House - Ayur Bhava (Impregnable Longevity / Ayushkaraka in 8th)",
        "core_traits_ta": [
            "ஆயுள்காரகனான சனி 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு இரும்பு போன்ற பூரண தீர்க்காயுளை (85+ வயது) வழங்கும் மகா அமைப்பாகும்.",
            "எந்தவிதமான விபத்துகள், ஆபத்துகள் மற்றும் கொடிய நோய்களிலிருந்தும் தப்பித்து நீண்ட காலம் வாழும் யோகம் உண்டு.",
            "வாழ்க்கையில் பல ஏற்ற இறக்கங்களையும், சோதனைகளையும் தாண்டி முதிர்ந்த ஞானமும் பக்குவமும் அடைவார்.",
            "மனைவி வழியில் பழைய நிலங்கள், உயில் சொத்துகள் மற்றும் காப்பீடுகள் தாமதமாக வந்து சேரும்."
        ],
        "core_traits_en": [
            "Ayushkaraka Saturn in the 8th is classically celebrated as the supreme guarantor of monumental longevity (85+ years).",
            "Miraculously survives fatal catastrophes, acute epidemics, and dangerous accidents unscathed.",
            "Weathers dramatic life tempests with unshakeable stoicism, evolving into a revered elder sage.",
            "Eventually inherits ancient landholdings, insurance payouts, and testamentary bequests through marriage."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சதாபிஷேகம் கண்டு நூற்றாண்டு வாழும் யோகம், பல்லாயிரம் கோடி உயில் சொத்துகள், ஆன்மீக முக்தி.",
            "எதிர்பாராத தன வரவுகள் வந்து சேரும்; சமுதாயத்தில் மூத்த வழிகாட்டியாகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows Centenarian longevity, vast testamentary ancestral properties, and serene Moksha.",
            "Revered as an unshakeable patriarch; commands universal veneration across generations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீராத வாத நோய்கள், பக்கவாதம், கண் பார்வை மங்குதல், ஏழ்மை.",
            "உயில் விவகாரங்களில் வழக்குகளும், அரசாங்க அபராதங்களால் மன உளைச்சலும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Chronic paralysis, osteoarthritis, severe visual degeneration, and financial distress.",
            "Protracted court litigations over disputed wills and crippling probate penalties."
        ],
        "career_wealth_ta": [
            "ஆயுள் காப்பீட்டுத் தலைவர், தொல்பொருள் ஆராய்ச்சி, நிலக்கரி மற்றும் கனிம வளங்கள், மரண சான்றிதழ் நிர்வாகம், கழிவு மேலாண்மை.",
            "உயில் சொத்துகள், பழைய முதலீடுகளின் முதிர்வு மற்றும் திடீர் தன வரவால் பெருஞ்செல்வம்."
        ],
        "career_wealth_en": [
            "Distinguished in life insurance underwriting, palaeontology, petroleum extraction, mortuary science, and waste recycling.",
            "Vast windfalls realized from mature pension funds, inherited estates, and mineral leases."
        ],
        "health_precautions_ta": [
            "மூல நோய் (Piles), ஆசனவாய் வெடிப்பு, மூட்டு வாதம், பக்கவாதம் மற்றும் கால் எலும்பு முறிவு.",
            "நார்ச்சத்து மிகுந்த உணவுகளையும், எண்ணெய் மசாஜ்களையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
        ],
        "health_precautions_en": [
            "Vulnerable to chronic hemorrhoids, anal fissures, severe rheumatoid arthritis, and femoral neck fractures.",
            "High-fiber diet, routine warm oil therapeutic massages, and falls-prevention care in old age."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம நீதி, பிற்கால பாக்கியம் & தத்துவ ஞானம்)",
        "house_title_en": "9th House - Bhagya Bhava (Righteous Morality, Delayed Fortune & Philosophical Depth)",
        "core_traits_ta": [
            "ஆழ்ந்த தர்ம சிந்தனை, நேர்மை, வேதாந்த தத்துவங்களில் பற்று மற்றும் உழைப்பையே தெய்வமாக மதிக்கும் சுபாவம்.",
            "தந்தையுடன் ஆரம்பத்தில் கருத்து வேறுபாடுகள் இருந்தாலும், பிற்காலத்தில் தந்தையின் பெருமையைக் காப்பார்.",
            "வாழ்க்கையின் பிற்பகுதியில் (36 வயதுக்கு மேல்) பாக்கியங்கள் பூரணமாகச் செயல்பட்டு பெரும் செல்வந்தராக மாற்றுவார்.",
            "பழமையான புண்ணியத் தலங்களுக்கும், மலைக் குகைகளுக்கும் சென்று அமைதியான தியானம் செய்வதில் விருப்பம்."
        ],
        "core_traits_en": [
            "Profound ethical conviction, rigorous honesty, devotion to Vedanta, and regards hard honest toil as sacred worship.",
            "Initial ideological distance from father dissolves into deep filial reverence and preservation of family heritage.",
            "Fortune compounds steadily, manifesting monumental prosperity and universal acclaim after age 36.",
            "Drawn to ancient stone shrines, remote Himalayan hermitages, and austere meditative disciplines."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட தர்ம யோகம், உச்ச நீதிமன்றத் தலைமை நீதிபதி, சர்வதேச தத்துவ மேதை.",
            "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு வாழ்வளிக்கும் மகா வள்ளலாகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted or own house: Supreme Dharma Yoga! Appellate chief justice, globally acclaimed constitutional jurist.",
            "Establishes monumental philanthropic foundations, uplifting countless destitute lives with dignity."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், மத சடங்குகளில் வெறுப்பு.",
            "வெளிநாட்டுப் பயணங்களில் தடைகள் மற்றும் தர்ம காரியங்களில் வீண் அவப்பெயர்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe paternal health reversals, bitter cynicism towards religion, and travel delays.",
            "Misappropriation of trust funds by relatives causing unmerited scandal."
        ],
        "career_wealth_ta": [
            "நீதிபதி, வழக்கறிஞர், தத்துவப் பேராசிரியர், தொண்டு நிறுவனத் தலைவர், சுரங்க ஏற்றுமதி, சர்வதேச வர்த்தகம்.",
            "நேர்மையான தர்ம வழியிலும், பழைய சொத்துகளாலும் கோடிக்கணக்கில் வற்றாத தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Exemplary career as constitutional magistrate, jurist, philosophy professor, mineral exporter, and foundation trustee.",
            "Generational wealth accumulated through unblemished professional ethics and prime real estate."
        ],
        "health_precautions_ta": [
            "தொடை எலும்பு வலி, இடுப்பு வாதம் (Sciatica), மூட்டுத் தேய்மானம் மற்றும் கால் வீக்கம்.",
            "முறையான நடைப்பயிற்சியும், வெதுவெதுப்பான எண்ணெய் மசாஜ்களும் மூட்டுகளுக்குப் பலம் தரும்."
        ],
        "health_precautions_en": [
            "Prone to femoral osteoporosis, chronic sciatica, hip joint degeneration, and lower leg edema.",
            "Gentle walking outdoors and regular warm herbal oil joint applications safeguard mobility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (சச யோகம் / சமுதாயத் தலைமை & தொழில் சாம்ராஜ்யம்)",
        "house_title_en": "10th House - Karma Bhava (Sasa Yoga / Mass Leadership & Industrial Hegemony)",
        "core_traits_ta": [
            "சனி 10-ஆம் பாவத்தில் அமர்வது உழைப்பாளர் வர்க்கத்தின் மாபெரும் தலைவராக உயர்த்தும் மிகச் சிறந்த ராஜ யோகமாகும்.",
            "சுய உழைப்பால் அடிமட்டத்திலிருந்து படிப்படியாக முன்னேறி நாட்டின் உச்ச பதவியை அடையும் விடாமுயற்சி.",
            "நேர்மையான நிர்வாகம், இரும்பு போன்ற ஒழுக்கம் மற்றும் பல்லாயிரக்கணக்கான தொழிலாளர்களை வழிநடத்தும் தலைமைப் பண்பு.",
            "அரசாங்க உயர் விருதுகள், கௌரவப் பட்டங்கள் மற்றும் சமுதாயத்தில் அழிக்க முடியாத சரித்திரப் புகழ்."
        ],
        "core_traits_en": [
            "Saturn in the 10th is a legendary hallmark of self-made titans who rise from humble origins to sovereign heights.",
            "Rises step-by-step through grueling industry and indomitable fortitude to apex positions of national statecraft.",
            "Uncompromising administrative integrity, Spartan discipline, and paternal authority over millions of working people.",
            "Garlanded with sovereign decorations, lifelong chairmanships, and timeless historical veneration."
        ],
        "strong_placement_ta": [
            "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் அமைந்தால்: நாட்டின் பிரதமர், தொழிலாளர் நலத்துறை மந்திரி, தொழில் சக்கரவர்த்தி.",
            "நாட்டின் முதன்மை இரும்பு ஆலைகள், சுரங்கங்கள் மற்றும் உள்கட்டமைப்பு சாம்ராஜ்யத்தை வழிநடத்துவார்."
        ],
        "strong_placement_en": [
            "Exalted in Libra or own signs with Sasa Yoga: Prime Minister, Minister of Labor, Titan of heavy national industry.",
            "Chairs monumental state infrastructure conglomerates, steel mills, and mineral resources."
        ],
        "weak_placement_ta": [
            "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் சரிவு, அதிகாரிகளால் தண்டனைகள், பொது வாழ்வில் சறுக்கல்.",
            "வேலையாட்களால் வேலைநிறுத்தங்களும், தொழிலில் பெரும் நஷ்டமும் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Catastrophic political fall, penal sanctions from regulators, and sudden public disgrace.",
            "Calamitous labor strikes, industrial sabotage, and severe commercial insolvency."
        ],
        "career_wealth_ta": [
            "அரசியல் தலைவர், பொது நிர்வாகம், இரும்பு மற்றும் எஃகு உற்பத்தி, சுரங்கத் துறை, ரயில்வே, உள்கட்டமைப்பு பொறியியல்.",
            "அரசாங்க கௌரவப் பதவிகளாலும் தொழில் ஆளுமையாலும் பல நூறு கோடி செல்வம் குவியும்."
        ],
        "career_wealth_en": [
            "Dominant in political governance, public sector administration, metallurgical manufacturing, railways, and civil infrastructure.",
            "Accumulates multi-million dollar equity holdings through transformative industrial leadership."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் மூட்டு வலி, ரத்த அழுத்தம், தூக்கமின்மை மற்றும் வாதக் கோளாறுகள்.",
            "வேலைக்கு நடுவே ஓய்வும், தியானப் பயிற்சிகளும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Occupational physical exhaustion, severe knee osteoarthritis, hypertension, and insomnia.",
            "Strict pacing of executive workload, daily meditation, and restorative orthopedic care."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட நில லாபம் / குபேர யோகம் & வற்றாத தன வரவு)",
        "house_title_en": "11th House - Labha Bhava (Massive Landed Wealth, Compounding Fortune & Wish Fulfillment)",
        "core_traits_ta": [
            "சனி 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடி கோடியாய் குவியும் தன யோகத்தையும், நீடித்த செல்வத்தையும் தரும்.",
            "வயது ஏற ஏற வருமானமும், சொத்துகளின் மதிப்பும் பல மடங்கு உயர்ந்து கொண்டே போகும்.",
            "செல்வாக்கு மிக்க தொழிலதிபர்கள், அரசியல்வாதிகள் மற்றும் முதியோர்களின் உயர்ந்த நட்பு வட்டம்.",
            "மூத்த சகோதரர்களிடம் நல்ல தோழமையும், அவர்களுடன் இணைந்து தொழில் செய்து முன்னேறும் யோகமும் உண்டு."
        ],
        "core_traits_en": [
            "Saturn in the 11th (an Upachaya house) is one of the grandest placements for inexorable, compounding wealth creation.",
            "Financial net worth and real estate valuations escalate exponentially with age, cresting into majestic abundance.",
            "Surrounded by seasoned industrial barons, elder statesmen, and powerful community patriarchs.",
            "Solid, enduring partnership with elder siblings who assist in expanding commercial enterprises."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற நிலங்கள், அடுக்குமாடி கட்டிடங்கள், ஆலைகள், குபேர யோகம்.",
            "அரசாங்க ஒப்பந்தங்கள் மற்றும் கனரகத் தொழில்களில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-billion dollar real estate complexes, heavy industrial plants, and supreme Kubera Yoga.",
            "Ranks among the foremost infrastructure magnates commanding prime governmental contracts."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் சொத்துத் தகராறு.",
            "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் கடன்கள் ஏற்படுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by unscrupulous associates, litigious partitions with elder brother.",
            "Delayed cash flows and capital trapped in non-performing assets."
        ],
        "career_wealth_ta": [
            "ரியல் எஸ்டேட் முதலீடுகள், சுரங்க காண்ட்ராக்ட், கனரக போக்குவரத்து, உள்கட்டமைப்பு நிதி, விவசாய நில மேம்பாடு.",
            "முதலீடுகளின் அசுர வளர்ச்சியாலும் சொத்து வாடகைகளாலும் கோடீஸ்வர யோகம்."
        ],
        "career_wealth_en": [
            "Lucrative success in commercial realty syndication, mineral concessions, fleet logistics, and infrastructure private equity.",
            "Immense compounding rental yields and long-term capital gains."
        ],
        "health_precautions_ta": [
            "இடது காது கேளாமை, கணுக்கால் வாதம், தசை இறுக்கம் மற்றும் ரத்த ஓட்டக் குறைபாடுகள்.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear auditory nerve dullness, ankle joint stiffness, and sluggish peripheral circulation.",
            "Daily ankle mobility drills, compression stockings, and regular otic checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (வைராக்கியம் / மோட்ச சாதனை & வெளிநாட்டு வாழ்க்கை)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Austere Renunciation, Foreign Settlement & Spiritual Release)",
        "core_traits_ta": [
            "உலக மாயைகளிலிருந்து விடுபடும் வைராக்கியம், ஆன்மீக பற்றற்ற நிலை மற்றும் தனிமையை விரும்பும் சுபாவம்.",
            "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது தொலைதூரத் தனிமையான இடங்களிலோ அனுகூலமும் வெற்றியும் கிட்டும்.",
            "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், அனாதை இல்லங்கள், முதியோர் காப்பகங்கள் மற்றும் தொண்டு நிறுவனங்களுக்குச் செலவிடுவார்.",
            "அரசாங்க வரி விவகாரங்களிலும் சட்ட விதிகளிலும் மிகுந்த எச்சரிக்கையுடன் செயல்பட வேண்டும்."
        ],
        "core_traits_en": [
            "Profound ascetic detachment, indifference to worldly superficiality, and deep love of meditative seclusion.",
            "Realizes superior peace of mind, high career standing, and prosperity when residing in foreign lands.",
            "Directs financial resources towards hospices, geriatric care sanitariums, and destitute relief charities.",
            "Must maintain strict compliance in statutory audits and cross-border regulatory reporting."
        ],
        "strong_placement_ta": [
            "துலாத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் தொழில் நிறுவனங்கள், சர்வதேச அங்கீகாரம்.",
            "அயன சயன சுகம், அமைதியான ஆத்ம சாந்தி மற்றும் பிறவிப் பெருங்கடலை நீந்தி மோட்சம் அடைதல்."
        ],
        "strong_placement_en": [
            "Exalted in Libra or own signs with benefics: Vast industrial conglomerates headquartered abroad; international acclaim.",
            "Attains peaceful inner serenity, unbroken restorative rest, and transcendent spiritual liberation (Moksha)."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, இடது கண் பார்வை மங்குதல், சிறைவாசம் அல்லது அபராதங்கள்.",
            "வீண் மருத்துவச் செலவுகள், ஏமாற்றங்கள் மற்றும் மன உளைச்சலால் அமைதியின்மை."
        ],
        "weak_placement_en": [
            "Debilitated in Aries or afflicted: Chronic severe insomnia, left-eye blindness risk, confinement or legal penalties.",
            "Crushing hospital debts, isolation, and persistent melancholic anxiety."
        ],
        "career_wealth_ta": [
            "சர்வதேச கப்பல் போக்குவரத்து, வெளிநாட்டு கட்டுமான ஒப்பந்தங்கள், சிறைத்துறை நிர்வாகம், முதியோர் இல்லங்கள், ஆன்மீக மடங்கள்.",
            "வெளிநாட்டு நாணயங்களாலும் தூரதேசப் பணிகளாலும் நிலையான தன வரவு."
        ],
        "career_wealth_en": [
            "Flourishes in international maritime freight, overseas civil contracting, correctional governance, and hospice administration.",
            "Substantial foreign currency reserves earned through operations in remote territories."
        ],
        "health_precautions_ta": [
            "இடது கண் பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை (Insomnia) மற்றும் வாத நோய்கள்.",
            "இரவில் அமைதியான தியானமும், பாதங்களை வெதுவெதுப்பான நீரால் கழுவுதலும் நல்ல தூக்கத்தைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye ocular degeneration, severe plantar fasciitis, chronic insomnia, and systemic vata disorders.",
            "Warm foot reflexology baths, calming bedtime rituals, and avoiding late-night digital screens promote rest."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

RAHU_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (தீவிர லட்சியம், காந்த ஆளுமை & உலகளாவிய ஆதிக்கம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Fierce Ambition, Magnetic Persona & Unconventional Rise)",
        "core_traits_ta": [
            "அபாரமான தன்னம்பிக்கை, தீவிரமான லட்சிய வெறி, காந்தக் கவர்ச்சி மற்றும் அனைவரையும் ஈர்க்கும் வசீகர ஆளுமை.",
            "பாரம்பரிய முறைகளை உடைத்து புதிய வழிகளில் சிந்தித்து வெற்றிபெறும் நவீன சிந்தனைப்போக்கு.",
            "சுயமரியாதைக்கு முதலிடம் கொடுப்பவர்; எவருக்கும் எளிதில் அடிபணியாத தன்னாட்சி சுபாவம்.",
            "வெளிநாட்டினர், வேற்று மதத்தினர் மற்றும் பலதரப்பட்ட மக்களுடன் எளிதில் பழகி காரியம் சாதிக்கும் சாமர்த்தியம்.",
            "மனதில் சில சமயம் காரணமற்ற பயமும், அதீத கற்பனைகளும், மாய எண்ணங்களும் எட்டிப்பார்க்கக்கூடும்."
        ],
        "core_traits_en": [
            "Inordinate worldly ambition, magnetic personal presence, and an unconventional trailblazing temperament.",
            "Breaks rigid orthodox taboos, deploying disruptive strategies to conquer contemporary frontiers.",
            "Fiercely protective of self-respect; scorns servitude and demands autonomous leadership.",
            "Effortlessly interacts with foreign cultures, diverse ethnicities, and global networks.",
            "Periodic psychological bouts of unexplained anxiety, vivid phobias, or restless hallucinations."
        ],
        "strong_placement_ta": [
            "ரிஷபம்/மிதுனத்தில் பலம் பெற்று சுப சேர்க்கை அமைந்தால்: உலகப் புகழ் பெற்ற தலைவர், சினிமா சூப்பர் ஸ்டார், பன்னாட்டு தொழில் அதிபர்.",
            "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, உலகளவில் பெரும் செல்வாக்குடன் முடிசூடுவார்."
        ],
        "strong_placement_en": [
            "Exalted in Taurus/Gemini with benefic aspects: Internationally celebrated mass hero, cinema icon, or billionaire tycoon.",
            "Garlanded with state honors, wielding global geopolitical and commercial influence."
        ],
        "weak_placement_ta": [
            "விருச்சிகம்/தனுசில் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மன பிரமை, போதை பழக்கங்கள், நரம்புத் தளர்ச்சி, தலை காயங்கள்.",
            "தவறான நபர்களின் தொடர்பால் அவப்பெயரும், சமுதாயத்தில் வீண் சர்ச்சைகளும் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Acute paranoia, substance addictions, severe nervous breakdown, and head trauma.",
            "Disrepute through shady associations and explosive public controversies."
        ],
        "career_wealth_ta": [
            "செயற்கை நுண்ணறிவு (AI), சைபர் செக்யூரிட்டி, விண்வெளி ஆராய்ச்சி, சினிமா, அரசியல், பன்னாட்டு ஏற்றுமதி-இறக்குமதி, பங்குச் சந்தை.",
            "துணிச்சலான நவீன முதலீடுகளாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Phenomenal success in artificial intelligence, cybersecurity, aerospace, cinema, politics, cross-border import-export, and equities.",
            "Amasses colossal fortunes through disruptive technological patents and foreign currency inflows."
        ],
        "health_precautions_ta": [
            "தலையில் காயங்கள், நரம்பு மண்டல பாதிப்பு, ஒவ்வாமை (Allergies), விஷக்கடி அபாயம் மற்றும் தூக்கமின்மை.",
            "தியானம், பிராணாயாமம் மற்றும் எளிய இயற்கை உணவுகள் மன அமைதியைத் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to cranial trauma, neurological tremors, sudden systemic allergies, venomous stings, and insomnia.",
            "Daily grounding meditation, breathwork, and clean organic nutrition stabilize the nervous system."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 54) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (மந்திர வாக்கு, திடீர் தன வரவு & அந்நிய மொழி ஞானம்)",
        "house_title_en": "2nd House - Dhana Bhava (Mesmerizing Speech, Sudden Windfalls & Polyglot Intellect)",
        "core_traits_ta": [
            "பேச்சில் அசாத்தியமான வசீகரமும், கேட்போரை வசியப்படுத்தும் தந்திரமும் கொண்ட பேச்சாற்றல்.",
            "பல மொழிகளை எளிதில் கற்கும் ஆர்வம்; அந்நிய மொழிகளில் சரளமாகப் பேசும் திறன்.",
            "எதிர்பாராத வழிகளில் திடீரென கோடிக்கணக்கில் தன வரவு வந்து சேரும் அதிர்ஷ்ட யோகம்.",
            "குடும்பத்தில் சில சமயம் ரகசியங்களும், கருத்து முரண்பாடுகளும் வரலாம்; விட்டுக்கொடுத்துச் செல்வது நல்லது."
        ],
        "core_traits_en": [
            "Mesmerizing, hypnotic verbal eloquence; sways audiences through uncanny rhetoric and persuasive craft.",
            "Natural polyglot aptitude; learns foreign languages and international idioms with effortless fluency.",
            "Subject to sudden financial windfalls and unconventional revenue streams from unexpected quarters.",
            "Experiences domestic secrets or ideological friction within the family circle; requires diplomatic candor."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமையும் போது: குபேர தன யோகம்! அந்நிய தேசத்து கரன்சி, கிரிப்டோகரன்சி, நவரத்தினங்கள் குவியும்.",
            "பேச்சையே மூலதனமாக வைத்து பன்னாட்டு அளவில் மாபெரும் கோடீஸ்வரராக உயருவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Vast Kubera wealth! Foreign exchange reserves, digital assets/crypto, and fine gems.",
            "Monetizes rhetorical and negotiating wizardry into a global multi-million dollar fortune."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் பொய்மை, வாக்கு தவறுகை, தவறான முதலீடுகளால் திடீர் திவால்.",
            "வலது கண்ணில் பார்வைக் குறைபாடு, பல் வியாதிகள் அல்லது முகத்தில் வடுக்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Deceptive promises, breach of financial contracts, and sudden fiscal ruin.",
            "Prone to right-eye vision loss, severe dental abscesses, and facial scars."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், அந்நிய செலாவணி வர்த்தகம் (Forex), மொழிபெயர்ப்பாளர், கிரிப்டோகரன்சி, ரசாயனம், தொலைக்காட்சி தொகுப்பாளர்.",
            "அந்நிய முதலீடுகளாலும் துணிச்சலான நிதி பரிவர்த்தனைகளாலும் பெரும் தன வரவு."
        ],
        "career_wealth_en": [
            "Thrives in foreign exchange markets, crypto syndicates, diplomatic translation, petrochemicals, and broadcasting.",
            "Vast capital multiplication achieved through international currency arbitrage."
        ],
        "health_precautions_ta": [
            "தொண்டை எரிச்சல், நாக்கில் புண்கள், பற்கள் ஆடுதல், வாய் துர்நாற்றம் மற்றும் வலது கண் பார்வை பாதிப்பு.",
            "வாய் சுகாதாரத்தைப் பேணுதலும், சூடான கார உணவுகளைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to pharyngeal ulceration, lingual fissures, dental cavities, and right-eye optic strain.",
            "Strict oral dental hygiene and avoidance of heavily spiced or toxic foods."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 102) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய தைரியம், வெற்றி & சர்வதேச தொடர்பு)",
        "house_title_en": "3rd House - Sahaja Bhava (Audacious Bravery, Upachaya Triumph & Global Media)",
        "core_traits_ta": [
            "ராகு 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு இமாலய வீரத்தையும், தீராத புகழையும் தரும் சிறந்த அமைப்பாகும்.",
            "எந்தவிதமான ஆபத்தையும் கண்டு அஞ்சாத சிங்கம் போன்ற பராக்கிரமம்; எதிரிகளைத் தன் சாதுரியத்தால் தவிடுபொடியாக்குவார்.",
            "நவீன தொழில்நுட்பங்கள், டிஜிட்டல் மீடியா மற்றும் சமூக வலைத்தளங்களில் அசாத்திய ஆதிக்கம் செலுத்துவார்.",
            "இளைய சகோதரர்களிடம் சற்று இடைவெளி இருக்கலாம்; ஆனால் பிற மனிதர்களை எளிதில் வழிநடத்துவார்."
        ],
        "core_traits_en": [
            "Rahu in the 3rd (an Upachaya house) is classically praised as an unstoppable engine of audacious valor and triumph.",
            "Lionhearted courage in perilous crises; shatters adversaries through technological and tactical ingenuity.",
            "Dominates modern digital communications, viral media, and cutting-edge electronic platforms.",
            "Independent dynamic with younger siblings; effortlessly commands large social crowds."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற ஊடக சாம்ராஜ்ய அதிபர், அரசியல் செல்வாக்கு, நாடெங்கும் வெற்றி.",
            "எடுத்த புதிய முயற்சிகள் யாவும் பல்கிப் பெருகி சரித்திரத்தில் அழியாத பொற்பெயர் பெறும்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Globally celebrated media baron, political mastermind, and conqueror of international markets.",
            "Pioneering digital enterprises achieve viral exponential scaling and enduring acclaim."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
            "சமூக வலைத்தளங்களில் வீண் சர்ச்சைகள் மற்றும் சட்டச் சிக்கல்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Estrangement from siblings, brachial nerve inflammation, and upper limb trauma.",
            "Explosive online defamation controversies and cyber litigation entanglements."
        ],
        "career_wealth_ta": [
            "டிஜிட்டல் மார்க்கெட்டிங், ஊடக நிறுவனம், விண்வெளி மற்றும் வான்வழிப் போக்குவரத்து, விளம்பர ஏஜென்சி, தொலைத்தொடர்பு.",
            "புதிய தொழில்நுட்பங்களாலும் சர்வதேச ஒப்பந்தங்களாலும் கோடிக்கணக்கில் செல்வம் குவியும்."
        ],
        "career_wealth_en": [
            "Dominant in digital marketing networks, electronic media, aviation logistics, cyber advertising, and satellite communications.",
            "Enormous wealth generated via scalable technological patents and viral internet infrastructure."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காதுகளில் இரைச்சல் மற்றும் விரல் நடுக்கம்.",
            "கணினியில் வேலை செய்வோர் உடற்பயிற்சியும் ஓய்வும் எடுப்பது அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to shoulder strain, brachial plexus neuropathy, tinnitus, and carpal tunnel syndrome.",
            "Ergonomic computer practices and routine upper body mobility stretching are recommended."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 142) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (நவீன மாளிகைகள், வெளிநாட்டு வாழ்க்கை & தீவிர மன ஓட்டம்)",
        "house_title_en": "4th House - Sukha Bhava (Ultra-Modern Mansions, Foreign Residence & Restless Mind)",
        "core_traits_ta": [
            "அல்ட்ரா-மாடர்ன் சொகுசு வீடுகள், அதிநவீன மின்னணு உபகரணங்கள் மற்றும் ஆடம்பர கார்களில் வாழ்வதில் ஆர்வம்.",
            "பிறந்த மண்ணை விட்டு வெளிநாடுகளிலோ அல்லது பெருநகரங்களிலோ வாழ்வதில் அபரிமிதமான வளர்ச்சி பெறுவார்.",
            "மனதில் எப்போதும் புதிய யோசனைகளும், அடங்காத தீவிர எண்ணங்களும் அலைபாய்ந்து கொண்டிருக்கும்.",
            "தாயாரின் உடல்நலத்தில் அதிக கவனம் செலுத்த வேண்டும்; தாய் வழியில் சில கருத்து முரண்பாடுகள் வரலாம்."
        ],
        "core_traits_en": [
            "Affinity for ultra-modern smart homes, cutting-edge automated electronics, and high-tech automotive fleet.",
            "Achieves exponential material elevation when settled far away from natal home or in futuristic global metropolises.",
            "Mind surges with relentless conceptual ambition and futuristic vision, occasionally verging on chronic restlessness.",
            "Requires tender vigilance regarding mother's health; periodic emotional misunderstandings in maternal lineage."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் பல நூறு கோடி மதிப்பிலான சொகுசு பங்களாக்கள், ஆடம்பர வாகனங்கள்.",
            "பன்னாட்டு நிறுவனங்களில் உயர் தலைமைப் பதவிகள் மற்றும் நவீன சொத்துகளால் மாபெரும் யோகம்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Multi-million dollar prime luxury estates abroad, exotic supercar fleet, and executive fame.",
            "Heads multinational infrastructure corporations with immense sovereign prestige."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் நரம்பு ஆரோக்கியம் பாதித்தல், பூர்வீக சொத்துகளில் தகராறுகள்.",
            "வீடு மற்றும் வாகனங்களால் எதிர்பாராத நஷ்டங்கள், விபத்துகள் மற்றும் மன அமைதியின்மை."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Maternal nervous fragility, litigations over ancestral home, and sudden domestic turbulence.",
            "Heavy financial losses through flawed property deals, vehicular collisions, and acute insomnia."
        ],
        "career_wealth_ta": [
            "ஸ்மார்ட் சிட்டி ரியல் எஸ்டேட், ஆட்டோமோட்டிவ் டெக்னாலஜி, ஏவியேஷன், எலக்ட்ரானிக்ஸ் தயாரிப்பு, இன்டீரியர் ஆட்டோமேஷன்.",
            "நவீன சொத்து பரிவர்த்தனைகளாலும் வெளிநாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் செல்வம் சேரும்."
        ],
        "career_wealth_en": [
            "Flourishes in smart city development, automotive electrification, aviation logistics, microelectronics, and home automation.",
            "Massive capital accumulated through international property syndication and tech-enabled assets."
        ],
        "health_precautions_ta": [
            "நெஞ்சு சளி, இருதய படபடப்பு, ஆஸ்துமா, ஒவ்வாமை மற்றும் மன அழுத்தம்.",
            "சுத்தமான காற்றோட்டமான சூழலில் வாழ்வதும், சுவாசப் பயிற்சிகளும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to pulmonary spasms, cardiac palpitations, bronchial allergies, and psychosomatic anxiety.",
            "Dwelling in unpolluted, well-ventilated environments and daily pranayama protect cardiovascular health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கூர்மையான தந்திர புத்தி, பங்குச் சந்தை & புதிய கண்டுபிடிப்புகள்)",
        "house_title_en": "5th House - Putra Bhava (Tactical Cunning, Speculative Windfalls & Disruptive Inventions)",
        "core_traits_ta": [
            "மின்னல் போன்ற கூர்மையான புத்திசாலித்தனம், புதுமையான தொழில் யுக்திகள் மற்றும் தந்திரமான திட்டமிடல்.",
            "பங்குச் சந்தை, கிரிப்டோகரன்சி, ஊக வணிகம் மற்றும் நவீன ஸ்டார்ட்-அப்களில் துணிச்சலாக இறங்கிச் சாதிப்பார்.",
            "புத்திர பாக்கியத்தில் ஆரம்பத்தில் சில மருத்துவக் கவனங்கள் தேவைப்படலாம்; குழந்தைகள் நவீன துறைகளில் சிறந்து விளங்குவர்.",
            "மந்திரங்கள், ஆன்மீக ரகசியங்கள் மற்றும் மாய சாஸ்திரங்களில் ஆழமான ஈடுபாடு கொண்டிருப்பார்."
        ],
        "core_traits_en": [
            "Razor-sharp tactical brilliance, avant-garde inventive ingenuity, and masterly unconventional planning.",
            "Audacious appetite for stock markets, crypto-derivatives, venture startups, and algorithmic trading.",
            "Progeny may require initial prenatal care; children excel in cutting-edge technological or artistic disciplines.",
            "Deep fascination with esoteric occult lore, hypnotic psychology, and mystical symbology."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமையும் போது: பங்குச் சந்தையில் பல நூறு கோடி ஜாக்பாட் லாபம், சர்வதேச புதிய கண்டுபிடிப்பாளர்.",
            "அரசாங்க உயர் ஆலோசனை குழுக்களில் இடம் பெறுதல், உலகளாவிய ஸ்டார்ட்-அப் நிறுவனங்களின் அதிபர்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Massive speculative jackpots in financial derivatives, celebrated tech inventor.",
            "Founder of global unicorn tech startups and advisor to state technological commissions."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் காலதாமதம், கருச்சிதைவு அபாயம்.",
            "சூதாட்டம் அல்லது தவறான ஊக வணிகத்தால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Miscarriages, complications in childbearing, and acute anxieties regarding progeny.",
            "Crippling financial bankruptcies incurred through reckless, impulsive speculative gambling."
        ],
        "career_wealth_ta": [
            "பங்குச் சந்தை அல்காரிதம், கிரிப்டோ டிரேடிங், கேமிங் தொழில், செயற்கை நுண்ணறிவு, சினிமா இயக்கம், மருந்து ஆராய்ச்சி.",
            "அறிவுசார் படைப்புகளாலும் துணிச்சலான நவீன முதலீடுகளாலும் அள்ள அள்ளக் குறையாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Dominant in algorithmic trading, crypto asset management, video game engineering, AI research, and biotechnology.",
            "Generates vast fortunes through proprietary algorithms, tech patents, and venture exits."
        ],
        "health_precautions_ta": [
            "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் புண்கள், அமிலத்தன்மை மற்றும் உணவு ஒவ்வாமை.",
            "இயற்கையான சத்தான உணவுகளை உட்கொள்ளுதலும், நச்சு உணவுகளைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to nervous dyspepsia, gastrointestinal gas, peptic ulcerations, hyperacidity, and severe food allergies.",
            "Consume pure, preservative-free organic foods and avoid unhygienic processed foods."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 222) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (எதிரிகளைத் தவிடுபொடியாக்குதல் / மகா உபசய பலம்)",
        "house_title_en": "6th House - Satru Bhava (Annihilation of Adversaries & Supreme Upachaya Might)",
        "core_traits_ta": [
            "ராகு 6-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், அசைக்க முடியாத சத்ரு ஜெயத்தையும் தரும்.",
            "எதிரிகள், வழக்குகள், சதித்திட்டங்கள் மற்றும் போட்டிகளைத் தன் சாதுரியத்தாலும் பலத்தாலும் தூள்தூளாக்குவார்.",
            "அளப்பரிய நோய் எதிர்ப்புச் சக்தி; கொடிய ஆபத்துகளிலிருந்தும் நோய்களிலிருந்தும் எளிதில் மீண்டு வருவார்.",
            "பணியாளர்களையும், பல்வேறு மொழி பேசும் உழைப்பாளர்களையும் தன் கட்டுப்பாட்டில் வைத்து வேலை வாங்குவார்."
        ],
        "core_traits_en": [
            "Rahu in the 6th (an Upachaya house) is a classically celebrated powerhouse of victory and invincible immunity.",
            "Totally demolishes adversaries, political conspiracies, hostile litigations, and commercial competitors.",
            "Possesses astonishing physiological immunity and rapid recuperative power from physical perils.",
            "Commands absolute obedience and high productivity from diverse, multicultural labor forces."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லாத பெருவாழ்வு, சர்வதேசப் புலனாய்வுத் தலைமை.",
            "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் அனைத்துப் போட்டிகளிலும் தொடர் வெற்றி."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Bestows complete Shatru Samhara Yoga! Total elimination of foes, heads intelligence agencies.",
            "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புரியாத மர்ம நோய்கள், ரத்தத்தில் நச்சுத்தன்மை, தோல் வியாதிகள்.",
            "வேலையாட்களால் ஏமாற்றப்படுதலும், கடன் சுமைகளால் மன உளைச்சலும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Baffling undiagnosable illnesses, systemic blood toxicities, and severe dermatosis.",
            "Embezzlement by treacherous employees and anxiety over mounting unpaid debts."
        ],
        "career_wealth_ta": [
            "சைபர் கிரைம் புலனாய்வு, குற்றவியல் சட்டம், மருந்து உற்பத்தி, சர்வதேச கடத்தல் தடுப்புப் பிரிவு, சுங்கத்துறை, பொது சுகாதாரம்.",
            "சவால்களையும் போட்டிகளையும் தனக்குச் சாதகமாக மாற்றி கோடிக்கணக்கில் வருவாய் ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Excels in cyber-crime forensics, criminal trial jurisprudence, pharmaceutical synthesis, customs enforcement, and epidemiology.",
            "Extracts substantial financial wealth directly from crisis management and competitive conquests."
        ],
        "health_precautions_ta": [
            "ஒவ்வாமை (Allergies), ரத்தத்தில் நச்சுத்தன்மை, பூச்சிக்கடி, குடல் தொற்று மற்றும் தோல் அரிப்பு.",
            "சுத்தமான உணவையும் நீரையும் உட்கொள்ளுதலும், நச்சுப் பொருட்களைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to sudden systemic anaphylaxis, blood impurities, venomous bites, intestinal parasites, and eczema.",
            "Strict water purification, allergen avoidance, and periodic lymphatic detox regimens are indicated."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (வேற்றுமொழி/கலாச்சாரத் துணை & பன்னாட்டு வர்த்தகம்)",
        "house_title_en": "7th House - Kalathra Bhava (Cross-Cultural Spouse & Transnational Alliances)",
        "core_traits_ta": [
            "வேற்று மதம், வேற்று மொழி அல்லது முற்றிலும் மாறுபட்ட கலாச்சாரப் பின்னணியிலிருந்து கவர்ச்சிகரமான வாழ்க்கைத் துணை அமைவார்.",
            "வாழ்க்கைத் துணையிடம் சுதந்திர மனப்பான்மையும், நவீன வாழ்க்கை முறையும் நிறைந்திருக்கும்.",
            "தாம்பத்தியத்தில் ஈகோ மோதல்கள் வராமல் பரஸ்பர புரிதலுடன் நடந்து கொள்வது மிக அவசியம்.",
            "கூட்டு வர்த்தகத்தில் வெளிநாட்டினருடனும், பன்னாட்டு நிறுவனங்களுடனும் ஒப்பந்தங்கள் செய்து வெற்றிபெறுவார்."
        ],
        "core_traits_en": [
            "Spouse hails from a diverse ethnic, foreign, or unconventional cultural background; highly charismatic and modern.",
            "Partner possesses an independent, dynamic mindset with a forward-looking lifestyle.",
            "Requires conscious emotional maturity and open communication to prevent volatile misunderstandings.",
            "Sensational success in transnational joint ventures, forging alliances with foreign conglomerates."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: பன்னாட்டு செல்வந்த குடும்பத் துணை, வெளிநாட்டில் மாபெரும் ராஜயோக வாழ்க்கை.",
            "சர்வதேச வர்த்தகத்தில் பல நூறு கோடி லாபமும், சமூகத்தில் கவர்ச்சிகரமான தம்பதியராகப் போற்றப்படும் நிலையும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Marries into an affluent international dynasty; lavish global lifestyle abroad.",
            "Multi-million dollar windfalls from global trade pacts; celebrated as an influential cosmopolitan couple."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடும் விரிசல், ரகசிய உறவுகளால் குடும்பப் பிரிவு.",
            "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்பட்டு சர்வதேச அளவில் வழக்குகளும் நஷ்டங்களும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Bitter matrimonial strife, scandalous clandestine affairs causing separation or divorce.",
            "Catastrophic financial betrayal by foreign business partners leading to international arbitration."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், ஏற்றுமதி-இறக்குமதி, வெளிநாட்டுத் தூதரகங்கள், பன்னாட்டு மக்கள் தொடர்பு, சர்வதேச விமானப் போக்குவரத்து.",
            "வாழ்க்கைத் துணையின் வழியிலும், வெளிநாட்டு கூட்டாண்மையாலும் கோடிக்கணக்கில் தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Dominant in cross-border commerce, global export-import, consular representation, international PR, and aviation.",
            "Substantial capital influx via multinational partnerships and foreign spousal assets."
        ],
        "health_precautions_ta": [
            "சிறுநீரகப் பாதை அழற்சி, பாலியல் உறுப்புகளில் தொற்று, அடிவயிற்று உஷ்ணம் மற்றும் ஒவ்வாமை.",
            "முறையான மருத்துவப் பரிசோதனைகளும், தனிநபர் சுகாதாரமும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to urinary tract infections, urogenital inflammation, reproductive heat, and systemic allergies.",
            "Strict personal hygiene, ample hydration, and periodic reproductive health screenings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (ரகசிய ஞானம், திடீர் யோகம் & ஆபத்துகளிலிருந்து தப்புதல்)",
        "house_title_en": "8th House - Ayur Bhava (Occult Mastery, Sudden Windfalls & Miraculous Survival)",
        "core_traits_ta": [
            "ஆழ்ந்த மறைபொருள் ஞானம், ஜோதிடம், தாந்திரீகம், உளவியல் மற்றும் பிரபஞ்ச ரகசியங்களை ஆராயும் பேரார்வம்.",
            "வாழ்க்கையில் திடீரென ஏற்படும் இமாலய அதிர்ஷ்டங்களும், அதே சமயம் எதிர்பாராத சரிவுகளும் மாறி மாறி வரும்.",
            "ஆபத்தான விபத்துகள் மற்றும் நெருக்கடிகளிலிருந்து மயிரிழையில் உயிர் தப்பிக்கும் விசித்திர யோகம் உண்டு.",
            "அரசாங்க வரி விவகாரங்களிலும் சட்ட விதிகளிலும் மிகுந்த விழிப்புணர்வுடன் இருக்க வேண்டும்."
        ],
        "core_traits_en": [
            "Profound fascination with occult metaphysics, astrology, esoteric tantra, and clandestine psychology.",
            "Experiences dramatic roller-coaster fluctuations: sudden stratospheric windfalls alternating with abrupt crises.",
            "Possesses an uncanny knack for surviving life-threatening disasters by a hair's breadth.",
            "Must maintain impeccable transparency in taxation, offshore finances, and legal compliance."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: வெளிநாட்டிலிருந்து திடீர் உயில் சொத்துகள், கிரிப்டோ முதலீடுகளில் மாபெரும் லாபம், நீண்ட ஆயுள்.",
            "ரகசியத் திட்டங்கள் மூலம் பல நூறு கோடி ஈட்டி சமுதாயத்தில் செல்வாக்குடன் வாழ்வார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Massive foreign legacy windfalls, phenomenal crypto investment yields, and long life.",
            "Monetizes proprietary confidential research into vast multi-million dollar liquidity."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மர்ம நோய்கள், விஷக்கடி, அரசு வழக்குகளால் அபராதங்கள்.",
            "துணையின் ஆரோக்கியத்தில் பின்னடைவுகள் மற்றும் திடீர் நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Baffling chronic ailments, toxic envenomation, punitive tax penalties, and sudden disgrace.",
            "Severe health trials for spouse and rapid dissipation of inherited assets."
        ],
        "career_wealth_ta": [
            "சைபர் செக்யூரிட்டி ஹேக்கிங், தடயவியல் துறை, சர்வதேச உளவுத்துறை, நச்சுயியல், காப்பீட்டுத் தணிக்கை, கிரிப்டோகரன்சி.",
            "திடீர் இன்சூரன்ஸ் இழப்பீடுகள், உயில் சொத்துகள் மற்றும் ரகசிய ஒப்பந்தங்கள் மூலம் தன வரவு."
        ],
        "career_wealth_en": [
            "Excels in cybersecurity penetration testing, forensic pathology, international espionage, toxicology, and crypto assets.",
            "Wealth derived through settlement windfalls, unearned inheritance, and crisis advisory."
        ],
        "health_precautions_ta": [
            "மூல நோய், ஆசனவாய் புண்கள், மர்மமான நரம்பு வலிகள், விஷக்கடி மற்றும் தூக்கமின்மை.",
            "சுத்தமான உணவை உண்பதும், நச்சுப் பொருட்களைத் தவிர்ப்பதும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to hemorrhoidal bleeding, anal fissures, idiopathic nerve pain, toxic stings, and insomnia.",
            "Strict dietary hygiene, avoidance of chemical toxins, and grounding meditative rest."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (நவீன தத்துவம், சர்வதேசப் பயணம் & புதுமை யோகம்)",
        "house_title_en": "9th House - Bhagya Bhava (Unconventional Philosophy, Global Odysseys & Breakthrough Fortune)",
        "core_traits_ta": [
            "பாரம்பரிய மதச் சடங்குகளைத் தாண்டி, நவீன உலகளாவிய ஆன்மீக சிந்தனைகளை விரும்பும் முற்போக்குவாதி.",
            "வெளிநாடுகளுக்கு அடிக்கடி பயணம் செய்தல்; பன்னாட்டுப் பல்கலைக்கழகங்களில் ஆராய்ச்சி செய்தல்.",
            "தந்தையுடன் கருத்து வேறுபாடுகள் வரலாம்; ஆனால் தந்தையின் நலனில் அக்கறை கொண்டிருப்பார்.",
            "வாழ்க்கையில் வழக்கத்திற்கு மாறான வழிகளில் அபரிமிதமான அதிர்ஷ்டங்களும் வெற்றிகளும் தேடி வரும்."
        ],
        "core_traits_en": [
            "Transcends rigid orthodoxy, championing universal spiritual humanism and progressive philosophical outlooks.",
            "Passionate world traveler; pursues cutting-edge research in premier global universities.",
            "Periodic ideological friction with father, yet strives to establish independent worldly laurels.",
            "Fortune arrives through non-traditional, innovative pathways and foreign patronages."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: சர்வதேச அங்கீகாரம், பன்னாட்டு அமைப்புகளில் உயரிய பதவி, வெளிநாட்டு யோகம்.",
            "உலகளாவிய நிறுவனங்களைத் தோற்றுவித்து சர்வதேச அளவில் புகழ்பெற்ற தலைவராக உயருவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: International cultural acclaim, executive directorships in global multilateral bodies.",
            "Founds multinational innovation hubs and commands widespread international respect."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, மத நம்பிக்கைகளில் குழப்பம்.",
            "வெளிநாட்டு விசா மற்றும் குடியுரிமை விவகாரங்களில் சட்டச் சிக்கல்கள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health complications, acute spiritual disillusionment, and ideological alienation.",
            "Visa denials, immigration litigation, and document hassles during international relocations."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகப் பிரதிநிதி, ஏவியேஷன் நிர்வாகம், சர்வதேசச் சட்டம், வெளிநாட்டுப் பல்கலைக்கழகப் பேராசிரியர், புதுமைத் தொழில்.",
            "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டுத் தொடர்புகளாலும் பல கோடிகளில் சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Distinguished as transnational trade commissioner, aviation executive, international jurist, and foreign professor.",
            "Generates vast wealth through offshore royalties, foreign exchange earnings, and cross-border consulting."
        ],
        "health_precautions_ta": [
            "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம் (Sciatica), ஒவ்வாமை மற்றும் தசைப் பிடிப்புகள்.",
            "நீண்ட விமானப் பயணங்களின் போது உடற்பயிற்சியும், போதுமான நீர் அருந்துதலும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to femoral neuropathy, sciatica sensitivity, travel-induced deep vein thrombosis, and allergies.",
            "Hydrate generously during long flights, wear compression socks, and maintain regular lower body mobility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (அதிவேக வளர்ச்சி, சர்வதேச அதிகாரம் & அரசியல் செல்வாக்கு)",
        "house_title_en": "10th House - Karma Bhava (Meteoric Rise, Global Authority & Political Stature)",
        "core_traits_ta": [
            "ராகு 10-ஆம் பாவத்தில் அமைவது தொழிலில் மின்னல் வேக வளர்ச்சியையும், சர்வதேச செல்வாக்கையும் தரும் மாபெரும் யோகமாகும்.",
            "சாதாரண நிலையிலிருந்து தொடங்கி குறுகிய காலத்தில் சமுதாயத்தின் உச்சாணிக் கொம்பில் அமரும் அசுர வேகம்.",
            "அரசியல், சினிமா, ஊடகம் மற்றும் பன்னாட்டு வர்த்தகத்தில் ஆயிரக்கணக்கான மக்களை வசீகரிக்கும் தலைமை ஆளுமை.",
            "எதிர்ப்புகளையும் விமர்சனங்களையும் தனக்குச் சாதகமான விளம்பரமாக மாற்றி வெற்றிபெறும் வித்தைக்காரர்."
        ],
        "core_traits_en": [
            "Rahu in the 10th is a celebrated catalyst for meteoric, sensational career elevation and international prominence.",
            "Ascends from total obscurity to supreme public heights with astonishing velocity and daring audacity.",
            "Commands magnetic authority across politics, cinema, media conglomerates, and multinational commerce.",
            "Master of public relations; turns hostile controversies into free publicity and stepping stones to power."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: நாட்டின் முதன்மை மந்திரி, சர்வதேச பெருநிறுவனத் தலைவர் (CEO), சரித்திரப் புகழ்.",
            "பல்லாயிரம் கோடி மதிப்பிலான தொழில் சாம்ராஜ்யத்தை நிறுவி உலகளவில் தலைசிறந்த மனிதராகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Sovereign minister, global CEO of Fortune 50 mega-corporation, and iconic historical figure.",
            "Builds a multi-billion dollar industrial and media empire, celebrated globally as a visionary trailblazer."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் வீழ்ச்சி, பொது வாழ்வில் ஊழல் குற்றச்சாட்டுகள்.",
            "அரசியல் சதிகளாலும் தவறான ஆலோசகர்களாலும் நற்பெயருக்குக் களங்கம் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Sudden catastrophic fall from power, corruption scandals, and public opprobrium.",
            "Victim of political conspiracies and toxic advice from manipulative retainers."
        ],
        "career_wealth_ta": [
            "அரசியல் தலைமை, சினிமா தயாரிப்பு, தகவல் தொழில்நுட்பத் தலைமை, வான்வழி மற்றும் விண்வெளித் துறை, சர்வதேச எண்ணெய் வர்த்தகம்.",
            "அரசாங்க செல்வாக்காலும் தொழில் மேன்மையாலும் பல நூறு கோடி செல்வம் குவியும்."
        ],
        "career_wealth_en": [
            "Dominant in political statecraft, major film production, big-tech executive suites, aerospace, and energy syndicates.",
            "Accumulates immense wealth through high-level state influence, equity shares, and multinational ventures."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் ரத்த அழுத்தம், தூக்கமின்மை, நரம்புத் தளர்ச்சி மற்றும் மர்மமான தலைவலிகள்.",
            "வேலைக்கு நடுவே அமைதியான தியானமும், முறையான ஓய்வும் எடுப்பது ஆரோக்கியத்தைப் பாதுகாக்கும்."
        ],
        "health_precautions_en": [
            "Prone to executive burnout, hypertension, chronic insomnia, nervous exhaustion, and idiopathic migraines.",
            "Daily transcendental meditation and structured relaxation intervals preserve executive stamina."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / குபேர யோகம் & வெளிநாட்டு வருவாய்)",
        "house_title_en": "11th House - Labha Bhava (Massive Multi-Channel Gains, Kubera Wealth & Global Network)",
        "core_traits_ta": [
            "ராகு 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடானுகோடி தன லாபத்தைத் தரும் மிக உன்னதமான யோகமாகும்.",
            "எண்ணிய ஆசைகள் அனைத்தும் எளிதில் நிறைவேறும்; பல வழிகளிலிருந்து பணம் வந்து கொண்டே இருக்கும்.",
            "அரசியல்வாதிகள், தொழில் அதிபர்கள் மற்றும் செல்வாக்கு மிக்க வெளிநாட்டினரின் விரிவான நட்பு வட்டம்.",
            "மூத்த சகோதரர்களிடம் சற்று சுதந்திரமான அணுகுமுறை இருக்கும்; ஆனால் அவர்களால் தன ஆதாயம் கிட்டும்."
        ],
        "core_traits_en": [
            "Rahu in the 11th (an Upachaya house) is one of the most prolific engines of boundless multi-stream wealth and ambition.",
            "Rapid, frictionless fulfillment of grand aspirations; money pours in through unconventional channels.",
            "Surrounded by a high-powered global network of politicians, venture capitalists, and foreign magnates.",
            "Maintains an independent yet profitable dynamic with elder siblings, benefiting materially through them."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், சொகுசு மாளிகைகள், குபேர யோகம்.",
            "கிரிப்டோ, பங்குச் சந்தை மற்றும் பன்னாட்டு வர்த்தகத்தில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-billion dollar liquid holdings, luxury estates, and supreme Kubera Yoga.",
            "Ranks among the foremost wealthy magnates in tech startups, speculative markets, and global commerce."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், சட்டவிரோத முதலீடுகளால் இழப்பு.",
            "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் அரசு அபராதங்கள் ஏற்படுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Heavy betrayal by counterfeit associates, catastrophic losses in dubious unregulated schemes.",
            "Capital frozen by regulatory authorities and punitive fines."
        ],
        "career_wealth_ta": [
            "வென்ச்சர் கேபிடல், கிரிப்டோகரன்சி, பங்கு வர்த்தகம், ஈ-காமர்ஸ், டிஜிட்டல் ஊடகம், சர்வதேச ஏற்றுமதி.",
            "முதலீடுகளின் அதிவேக வளர்ச்சியாலும் பன்னாட்டு தொடர்புகளாலும் கோடீஸ்வர யோகம்."
        ],
        "career_wealth_en": [
            "Lucrative success in venture capital funds, crypto networks, high-frequency trading, e-commerce, and global import-export.",
            "Extraordinary capital multiplication placing the native in the elite billionaire tier."
        ],
        "health_precautions_ta": [
            "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் ஒவ்வாமை.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear ache, ankle ligament stiffness, sluggish peripheral circulation, and systemic allergies.",
            "Daily ankle mobility drills, compression wear during flights, and regular otic checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (வெளிநாட்டு குடியுரிமை, ரகசிய முதலீடுகள் & அயன சயனம்)",
        "house_title_en": "12th House - Vraya Bhava (Permanent Foreign Settlement, Secret Offshores & Restless Sleep)",
        "core_traits_ta": [
            "பிறந்த மண்ணை விட்டு வெளிநாடுகளில் நிரந்தரமாகக் குடியேறும் பிராப்தி; அந்நிய தேசத்தில் மாபெரும் யோகம்.",
            "பணத்தை ரகசியமாக முதலீடு செய்வதிலும், வெளிநாட்டு வங்கிகளில் சொத்துகளைச் சேர்ப்பதிலும் ஆர்வம்.",
            "தனிமையை விரும்புவார்; இரவு நேரங்களில் அதிக விழிப்புடனும் படைப்பாற்றலுடனும் செயல்படுவார்.",
            "அரசாங்க சட்ட விதிகளிலும் வரி விவகாரங்களிலும் மிகுந்த எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
        ],
        "core_traits_en": [
            "Destiny for permanent foreign residency or citizenship; thrives incomparably better abroad than in birth land.",
            "Acute acumen for managing confidential offshore investments, private trusts, and international bank holdings.",
            "Loves solitary night hours; nocturnal bursts of creative and strategic genius.",
            "Must maintain strict compliance in immigration filings, international taxation, and signed cross-border declarations."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் தொழில் சாம்ராஜ்யம், சர்வதேசக் குடியுரிமை, பன்னாட்டுச் செல்வம்.",
            "அயன சயன சுகம், அமைதியான ஆத்ம சாந்தி மற்றும் வெளிநாட்டு நாணயங்கள் மூலம் அளப்பரிய தன வரவு."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Commands vast commercial conglomerates abroad; dual citizenship in premier nations.",
            "Substantial foreign currency reserves and profound peace of mind in exotic overseas retreats."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, கண் பார்வை பாதிப்பு, வெளிநாட்டில் சிறைவாசம் அல்லது நாடு கடத்தல்.",
            "வீண் விரயங்கள், சட்டவிரோத பழக்கங்களால் அபராதங்கள் மற்றும் மன உளைச்சல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe insomnia, left-eye vision defects, visa deportation, or foreign confinement.",
            "Heavy financial dissipation through reckless nocturnal habits and regulatory penalties."
        ],
        "career_wealth_ta": [
            "சர்வதேச கப்பல் போக்குவரத்து, வெளிநாட்டுத் தூதரகங்கள், சர்வதேச நிதி ஆலோசகர், விமானப் போக்குவரத்து, ரசாயன ஏற்றுமதி.",
            "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Thrives in international maritime logistics, consular diplomacy, offshore finance, aviation, and petrochemical export.",
            "Colossal income denominated in hard foreign currencies flowing from overseas holdings."
        ],
        "health_precautions_ta": [
            "இடது கண் பார்வைக் கோளாறு, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் மர்ம நோய்கள்.",
            "இரவில் படுக்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், தியானமும் நல்ல தூக்கத்தைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye refractive strain, peripheral foot neuropathy, chronic insomnia, and psychosomatic ailments.",
            "Nightly cold eye-compresses, gentle foot reflexology, and regular renal health screenings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

KETU_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (ஞான காரகன் / உள்ளுணர்வு, பற்றற்ற நிலை & ஆன்மீக முகம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Mokshakaraka / Gnostic Intuition & Ascetic Persona)",
        "core_traits_ta": [
            "ஆழ்ந்த ஆன்மீக நாட்டம், கூர்மையான உள்ளுணர்வு (Intuition), எதையும் ஊடுருவிப் பார்க்கும் ஞானப் பார்வை.",
            "உலகியல் மாயைகளில் எளிதில் மயங்காத பற்றற்ற சுபாவம்; அமைதியான, முனிவர் போன்ற முகத்தோற்றம்.",
            "சுயமரியாதைக்கு முக்கியத்துவம் கொடுப்பார்; ஆடம்பரங்களை விட எளிமையான வாழ்வையே விரும்புவார்.",
            "மருத்துவம், ஜோதிடம், யோகா மற்றும் ரகசிய சாஸ்திரங்களை இயல்பாகவே உணரும் தெய்வீக ஆற்றல் உண்டு.",
            "மனதில் சில சமயம் காரணமற்ற தனிமை உணர்வும், உலகப் பற்றுகளிலிருந்து விலகும் எண்ணமும் வரலாம்."
        ],
        "core_traits_en": [
            "Profound spiritual orientation, piercing intuitive foresight, and an uncanny ability to perceive hidden motives.",
            "Natural detachment from shallow material vanity; carries an enigmatic, ascetic countenance.",
            "Quietly guarded self-respect; prefers austere, unpretentious simplicity over gaudy ostentation.",
            "Innate flair for healing arts, Vedic astrology, yogic metaphysics, and occult diagnostics.",
            "Periodic bouts of subjective isolation, yearning to transcend worldly attachments."
        ],
        "strong_placement_ta": [
            "விருச்சிகம்/தனுசில் பலம் பெற்று சுப சேர்க்கை அமைந்தால்: உலகப் புகழ் பெற்ற ஆன்மீக குரு, சித்த மருத்துவர், ஞான யோகி.",
            "அரசாங்கத்தால் போற்றப்படும் மாபெரும் மெய்யியலாளராகத் திகழ்ந்து சரித்திரத்தில் இடம்பிடிப்பார்."
        ],
        "strong_placement_en": [
            "Exalted in Scorpio/Sagittarius with benefic aspects: Internationally revered spiritual preceptor, master naturopath, or gnostic sage.",
            "Conferred premier civic honors as an iconic philosopher, leaving an immortal legacy of wisdom."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தலைவலி, கண் பார்வைக் குறைபாடு, நரம்புத் தளர்ச்சி, சரும நோய்கள்.",
            "தன்னம்பிக்கைக் குறைவு, முடிவெடுப்பதில் குழப்பம் மற்றும் சமுதாயத்திலிருந்து விலகி வாழும் எண்ணம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Chronic cranial pain, ocular defects, nervous debility, and stubborn eczema.",
            "Erosion of self-confidence, vacillating indecision, and neurotic social alienation."
        ],
        "career_wealth_ta": [
            "ஆன்மீக ஆசிரமங்கள், யோகா மற்றும் இயற்கை மருத்துவம், ஜோதிட ஆராய்ச்சி, உளவியல் ஆலோசனை, ஹோமியோபதி.",
            "அறிவுசார் வழிகாட்டலாலும் ஆன்மீக சேவைகளாலும் கௌரவமான செல்வச் சேர்க்கை."
        ],
        "career_wealth_en": [
            "Distinction as spiritual ashram director, naturopathic physician, master astrologer, psychologist, and homeopath.",
            "Honorable wealth accrued through institutional donations, consulting honorariums, and literary treatises."
        ],
        "health_precautions_ta": [
            "தலையில் காயங்கள், ஒவ்வாமை (Allergies), தோல் வறட்சி, நரம்புத் தளர்ச்சி மற்றும் தூக்கமின்மை.",
            "தியானம், பிராணாயாமம் மற்றும் எளிய இயற்கை உணவுகள் மன அமைதியையும் ஆரோக்கியத்தையும் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to head lacerations, mysterious allergies, dry skin eruptions, nervous exhaustion, and insomnia.",
            "Daily transcendental meditation, breathwork, and clean organic nutrition stabilize the nervous system."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 54) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (மௌன வாக்கு, வேதாந்தப் பேச்சு & திடீர் விரயம்)",
        "house_title_en": "2nd House - Dhana Bhava (Laconic Truth, Vedantic Speech & Detached Wealth)",
        "core_traits_ta": [
            "குறைத்துப் பேசும் சுபாவம்; ஆனால் பேசும் வார்த்தைகளில் ஆழமான உண்மையும், வேதாந்த தத்துவமும் நிறைந்திருக்கும்.",
            "பணத்தின் மீது அளவுகடந்த ஆசை இல்லாத பற்றற்ற மனப்பான்மை; தேவைக்கேற்ற செல்வத்தை மட்டுமே நாடுவார்.",
            "குடும்பத்தில் சில சமயம் முரண்பாடுகளும், அமைதியின்மையும் வரலாம்; பொறுமை காப்பது நலம்.",
            "பழைய நூல்கள், ரகசிய சாஸ்திரங்கள் மற்றும் ஆன்மீக விஷயங்களை கற்பதில் ஆர்வம் காட்டுவார்."
        ],
        "core_traits_en": [
            "Laconic, minimalist speech; speaks with piercing, unvarnished metaphysical truth and philosophical gravity.",
            "Philosophical detachment from money; views material capital as mere transient energy.",
            "Experiences domestic turbulence or emotional distance from family; requires conscious patience.",
            "Avid student of ancient manuscripts, scriptural commentaries, and esoteric metaphysics."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமையும் போது: ஆன்மீக அறக்கட்டளைகளின் சொத்துகள், திடீர் பூமி தன யோகம், வாக்கு பலிதம்.",
            "பேச்சையே தர்ம வழியில் பயன்படுத்தி பல்லாயிரக்கணக்கான மக்களின் வாழ்வை நல்வழிப்படுத்துவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Stewardship over sacred trust estates, unexpected legacy landholdings, and prophetic speech.",
            "Deploys speech to illuminate and counsel thousands onto the path of righteousness."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் கடுமை, வாக்கு தவறுகை, தவறான முதலீடுகளால் திடீர் இழப்பு.",
            "வலது கண்ணில் பார்வைக் குறைபாடு, பல் வியாதிகள் அல்லது நாக்கில் புண்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Biting, harsh speech; broken financial commitments, and sudden capital erosion.",
            "Prone to right-eye vision impairments, dental decay, and lingual ulcerations."
        ],
        "career_wealth_ta": [
            "ஆன்மீகப் பேச்சாளர், மத தத்துவ நூலாசிரியர், தொல்பொருள் ஆய்வாளர், இயற்கை மூலிகை வர்த்தகம், ஜோதிடர்.",
            "நேர்மையான ஆலோசனைகளாலும் ஆன்மீகப் பணிகளாலும் நிலையான வருவாய்."
        ],
        "career_wealth_en": [
            "Thrives as philosophical lecturer, scriptural author, epigraphist, herbal medicines trader, and astrologer.",
            "Steady livelihood derived from scholarly consultancy and ethical services."
        ],
        "health_precautions_ta": [
            "தொண்டை வறட்சி, நாக்கில் புண்கள், பற்கள் ஆடுதல், வலது கண் பார்வை மங்குதல் மற்றும் வாய் துர்நாற்றம்.",
            "வாய் சுகாதாரத்தைப் பேணுதலும், மிதமான மூலிகைக் குடிநீர் அருந்துவதும் நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to pharyngeal dryness, oral ulcers, dental cavities, and right-eye optic strain.",
            "Strict oral hygiene, saline gargling, and organic herbal teas promote throat comfort."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 102) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய ஆன்மீக தைரியம், வெற்றி & ஞான வீரியம்)",
        "house_title_en": "3rd House - Sahaja Bhava (Spiritual Valour, Upachaya Triumph & Mystical Enterprise)",
        "core_traits_ta": [
            "கேது 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு இமாலய ஆன்மீக தைரியத்தையும், வெற்றிகளையும் தரும் சிறந்த அமைப்பாகும்.",
            "எந்தவிதமான சோதனைகளையும் துணிவுடன் தாங்கி வெல்லும் ஆற்றல்; எதிரிகளைத் தன் அமைதியாலும் ஞானத்தாலும் வீழ்த்துவார்.",
            "எழுத்தாற்றல், ஆன்மீகக் கட்டுரைகள் மற்றும் தத்துவ நூல்களை இயற்றுவதில் அசாத்திய திறமை படைத்திருப்பார்.",
            "இளைய சகோதரர்களிடம் சற்று பற்றற்ற உறவு இருக்கலாம்; ஆனால் அவர்களுக்குத் தேவையான நன்மைகளைச் செய்வார்."
        ],
        "core_traits_en": [
            "Ketu in the 3rd (an Upachaya house) is classically venerated as a powerhouse of fearless spiritual fortitude and triumph.",
            "Possesses indomitable resilience in the face of worldly crises; disarms adversaries through serene detachment.",
            "Exceptional literary talent for penning profound metaphysical treatises, esoteric essays, and poetry.",
            "Maintains an emotionally detached yet supportive dynamic with younger siblings."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற ஆன்மீக எழுத்தாளர், தத்துவ மாமேதை, நாடெங்கும் வெற்றி.",
            "எடுத்த ஆன்மீக முயற்சிகள் யாவும் அமோக வெற்றி பெற்று சரித்திரத்தில் அழியாத பொற்பெயர் பெறும்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Internationally acclaimed spiritual author, philosophical savant, and conqueror of inner faculties.",
            "Pioneering metaphysical works achieve global recognition and timeless literary honors."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
            "காரணமற்ற பயமும் தயக்கமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Bitter sibling misunderstandings, brachial nerve inflammation, and upper limb numbness.",
            "Paralyzing self-doubt and pessimistic procrastination sabotaging creative initiatives."
        ],
        "career_wealth_ta": [
            "ஆன்மீக வெளியீட்டாளர், தத்துவ ஆசிரியர், யோகா பயிற்சியாளர், சர்வதேச தொண்டு நிறுவனம், ஆயுர்வேத மருத்துவம்.",
            "எழுத்து, அறிவுரை மற்றும் தர்ம காரியங்கள் மூலம் கௌரவமான செல்வச் சேர்க்கை."
        ],
        "career_wealth_en": [
            "Dominant in spiritual publishing, philosophical pedagogy, yoga instruction, humanitarian trusts, and Ayurvedic medicine.",
            "Substantial capital accumulated through intellectual consulting, royalties, and philanthropic syndicates."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை மற்றும் விரல் நடுக்கம்.",
            "முறையான யோகாசனங்களும், உடற்பயிற்சியும் உடலை ஆரோக்கியமாக வைத்திருக்கும்."
        ],
        "health_precautions_en": [
            "Prone to shoulder stiffness, brachial plexus neuralgia, auditory dullness, and finger muscular tremors.",
            "Yogic asanas and upper quadrant stretching optimize neuromuscular flexibility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 142) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (ஆன்மீக இல்லம், தாயன்பில் பக்குவம் & ஆத்ம சாந்தி)",
        "house_title_en": "4th House - Sukha Bhava (Spiritual Home, Maternal Stoicism & Inner Solace)",
        "core_traits_ta": [
            "வீட்டில் எப்போதும் ஆன்மீகச் சூழல், அமைதி, தியான அறை மற்றும் பூஜைகள் நிறைந்திருக்கும்.",
            "தாயாரின் மீது ஆழ்ந்த பக்தி; தாயார் பக்குவமான ஆன்மீகப் பெண்ணாக விளங்கி நல்வழிகாட்டுவார்.",
            "ஆடம்பர மாளிகைகளை விட இயற்கை எழில் கொஞ்சும் அமைதியான கிராமப்புறங்களில் வசிப்பதில் விருப்பம்.",
            "மனதில் பூரண ஆத்ம சாந்தியும், உலக இன்பங்களை விட ஆன்மீக விடுதலையை நோக்கிய தீவிர பயணமும் இருக்கும்."
        ],
        "core_traits_en": [
            "Transforms the domestic home into a tranquil spiritual sanctuary, complete with meditation rooms and daily worship.",
            "Deep devotion to a stoic, spiritually enlightened mother who serves as primary moral guide.",
            "Prefers rustic country homes, hermitage retreats, and nature sanctuaries over ostentatious city mansions.",
            "Harbors deep inner solace, prioritizing spiritual emancipation (Moksha) above transient sensory pleasures."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: ஆன்மீக ஆசிரமங்கள், தியான மையங்கள், அமைதியான இல்லற சுகம்.",
            "பூர்வீகச் சொத்துகள் தடையின்றி வந்து சேரும்; சமுதாயத்தில் உன்னத ஞானியாகப் போற்றப்படுவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Founds renowned spiritual ashrams and meditation sanctuaries; deep domestic harmony.",
            "Smoothly inherits ancestral heritage properties; universally revered as an enlightened householder-sage."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக்குறைவு, பூர்வீக சொத்துகளில் தகராறுகள்.",
            "வீடு மற்றும் வாகனங்களால் எதிர்பாராத நஷ்டங்கள் மற்றும் மன அமைதியின்மை ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Maternal health frailties, disputes over ancestral lands, and domestic discontent.",
            "Financial drain from recurring property maintenance and vehicles; persistent heart palpitations."
        ],
        "career_wealth_ta": [
            "ஆன்மீக ஆசிரம நிர்வாகம், இயற்கை விவசாயம், மூலிகைப் பண்ணைகள், நில அளவையாளர், ஆயுர்வேத மருந்து தயாரிப்பு.",
            "பூமி பரிவர்த்தனைகளாலும் ஆன்மீக சேவைகளாலும் நிலையான சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Flourishes in ashram administration, organic permaculture, medicinal herbal farming, land survey, and Ayurveda.",
            "Steady capital accumulation through real estate preservation and holistic institutional assets."
        ],
        "health_precautions_ta": [
            "நெஞ்சு சளி, இருதய பலவீனம், ஆஸ்துமா, மூட்டு வலி மற்றும் மன அழுத்தம்.",
            "சூடான மூலிகைக் குடிநீரும், பிராணாயாமப் பயிற்சிகளும் நுரையீரல் நலனைக் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to bronchial asthma, cardiac rhythm irregularities, joint stiffness, and melancholic anxiety.",
            "Warm herbal decoctions, breathwork pranayama, and dwelling in clean rural air preserve health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (மகா ஞானம், மந்திர சித்தி & ஆன்மீக சந்ததிகள்)",
        "house_title_en": "5th House - Putra Bhava (Supreme Gnosis, Mantra Siddhi & Spiritual Progeny)",
        "core_traits_ta": [
            "கேது 5-ஆம் பாவத்தில் அமர்வது முற்பிறவி புண்ணியத்தின் வெளிப்பாடாகும்; அசாத்தியமான ஆன்மீக ஞானம் கிட்டும்.",
            "மந்திர சாஸ்திரங்கள், தியானம், காயத்ரி ஜபம் மற்றும் வேதங்களை எளிதில் கிரகிக்கும் ஆற்றல் உண்டு.",
            "புத்திர பாக்கியத்தில் ஆரம்பத்தில் சில காலதாமதம் இருந்தாலும், பிற்காலத்தில் குழந்தைகள் சிறந்த ஆன்மீகவாதிகளாகத் திகழ்வர்.",
            "பங்குச் சந்தை போன்ற ஊக வணிகங்களைத் தவிர்த்து, தர்ம காரியங்களில் மட்டுமே ஈடுபடுவார்."
        ],
        "core_traits_en": [
            "Ketu in the 5th signifies ripe fruits of past-life spiritual merit (Poorvapunya); unlocks transcendent gnosis.",
            "Effortless mastery of sacred mantras, esoteric meditation, Gayatri japa, and scriptural comprehension.",
            "Progeny may experience initial delays; children mature into highly moral, spiritually elevated souls.",
            "Completely shuns speculative gambling, dedicating mental energy to intellectual and charitable causes."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமையும் போது: மந்திர சித்தி பெற்ற மகா ஞானி, வேதாந்தப் பேராசிரியர், சர்வதேச விருதுகள்.",
            "குழந்தைகள் ஆன்மீகத்திலும் கல்வியிலும் உலகப் புகழ் பெறுவார்கள்; முன்னோர்களின் புண்ணியத்தால் யோக வாழ்வு."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Realizes authentic Mantra Siddhi, celebrated professor of philosophy and Vedanta.",
            "Progeny attain global renown for intellectual and spiritual purity; lives under the protection of divine grace."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கடும் தடைகள், கருச்சிதைவு அபாயம்.",
            "தவறான நிதித் திட்டங்களால் சேமிப்பு விரயமாதல் மற்றும் மன அமைதியின்மை."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Acute delays in childbearing, miscarriages, and persistent worry regarding progeny.",
            "Financial drain from ill-considered schemes and dogmatic philosophical rigidity."
        ],
        "career_wealth_ta": [
            "வேதாந்த ஆசிரியர், ஜோதிட ஆராய்ச்சியாளர், சமஸ்கிருதப் பேராசிரியர், அறக்கட்டளை நிர்வாகி, இயற்கை மருத்துவர்.",
            "அறிவுசார் படைப்புகளாலும் ஆன்மீக ஆலோசனைகளாலும் கௌரவமான செல்வச் சேர்க்கை."
        ],
        "career_wealth_en": [
            "Distinction as Vedanta professor, astrological research director, Sanskrit scholar, trust manager, and naturopath.",
            "Generates honorable wealth via book royalties, educational endowments, and institutional consultancy."
        ],
        "health_precautions_ta": [
            "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் புண்கள், அமிலத்தன்மை மற்றும் உணவு ஒவ்வாமை.",
            "இயற்கையான சத்தான உணவுகளை உட்கொள்ளுதலும், நச்சு உணவுகளைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to nervous dyspepsia, gastrointestinal bloating, peptic ulcers, and food sensitivities.",
            "Adopt simple, easily digestible sattvic foods and avoid irregular meal schedules."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 222) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (பகைவர்களை வெல்லுதல் / மகா உபசய பலம் & சேவை)",
        "house_title_en": "6th House - Satru Bhava (Vanquishing Opposition, Upachaya Strength & Selfless Service)",
        "core_traits_ta": [
            "கேது 6-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், அசைக்க முடியாத சத்ரு ஜெயத்தையும் தரும்.",
            "எதிரிகள், வழக்குகள் மற்றும் கடன் தொல்லைகளைத் தன் பற்றற்ற தன்மையாலும் விவேகத்தாலும் எளிதில் முறியடிப்பார்.",
            "இரும்பு போன்ற நோய் எதிர்ப்புச் சக்தி; எந்தவிதமான நோய்களிலிருந்தும் இயற்கை மருத்துவத்தால் மீண்டு வருவார்.",
            "எளிய மக்களுக்கும், ஆதரவற்றோருக்கும் சேவை செய்வதில் பேரானந்தம் அடைவார்."
        ],
        "core_traits_en": [
            "Ketu in the 6th (an Upachaya house) is classically celebrated as an invincible fortress of resilience and triumph.",
            "Overcomes all adversaries, litigations, and debts through fearless equanimity and intellectual detachment.",
            "Possesses robust physiological immunity, recovering swiftly from illness via holistic therapies.",
            "Derives profound personal fulfillment from humble, selfless service to marginalized and suffering souls."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, மருத்துவத் துறையில் உயர் அதிகாரம்.",
            "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் அனைத்துப் போட்டிகளிலும் தொடர் வெற்றி."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Bestows complete Shatru Samhara Yoga! Total elimination of foes, heads healthcare commissions.",
            "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மர்ம நோய்கள், தோல் அலர்ஜி, பூச்சிக்கடி, கடன் தொல்லைகள்.",
            "வேலையாட்களால் ஏமாற்றப்படுதலும், தாய்மாமனுடன் கருத்து மோதல்களும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Baffling immune disorders, chronic dermatitis, insect venom reactions, and debt worries.",
            "Deceit by domestic servants and strained relations with maternal relatives."
        ],
        "career_wealth_ta": [
            "இயற்கை மருத்துவம், ஆயுர்வேத கிளினிக், தொண்டு நிறுவனங்கள், குற்றவியல் வழக்கறிஞர், பொது சுகாதாரம், கால்நடை மருத்துவர்.",
            "சேவை மனப்பான்மையாலும் நேர்மையான உழைப்பாலும் நிலையான வருமானம்."
        ],
        "career_wealth_en": [
            "Thrives in naturopathy, Ayurvedic hospital ownership, philanthropic relief agencies, public health, and veterinary medicine.",
            "Earns stable revenues by serving community health and institutional welfare."
        ],
        "health_precautions_ta": [
            "குடல் அழற்சி, நரம்புத் தளர்ச்சி, சரும நோய்கள், ஆஸ்துமா மற்றும் மலச்சிக்கல்.",
            "நார்ச்சத்து மிகுந்த காய்கறிகளையும் பழங்களையும் உண்பதும், தோலை சுத்தமாகப் பராமரிப்பதும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to colitis, nervous exhaustion, eczema, bronchial allergies, and chronic constipation.",
            "High-fiber dietary regimen, probiotics, and dermatological care are essential."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (பக்குவமான ஆன்மீகத் துணை & பற்றற்ற தாம்பத்தியம்)",
        "house_title_en": "7th House - Kalathra Bhava (Ascetic Spiritual Spouse & Detached Matrimony)",
        "core_traits_ta": [
            "ஆன்மீக நாட்டம், பக்குவம், அமைதி மற்றும் எளிய வாழ்க்கை முறையைக் கொண்ட வாழ்க்கைத் துணை அமைவார்.",
            "தாம்பத்தியத்தில் உடல் கவர்ச்சியை விட மனரீதியான புரிதலும், ஆன்மீக நட்பும் மேலோங்கி நிற்கும்.",
            "திருமண வாழ்வில் ஈகோ மோதல்கள் வராமல் பரஸ்பர மரியாதையுடன் நடந்து கொள்வது அமைதி தரும்.",
            "கூட்டு வர்த்தகத்தில் யாரையும் அளவுக்கு அதிகமாக நம்பாமல் வெளிப்படைத்தன்மையுடன் இருப்பது நல்லது."
        ],
        "core_traits_en": [
            "Blessed with a deeply spiritual, stoic, modest, and philosophically inclined spouse.",
            "Matrimonial bond is anchored in soul communion and mutual respect rather than sensory indulgence.",
            "Requires conscious avoidance of emotional coldness to nurture warmth in domestic companionship.",
            "Must practice formal contractual diligence and avoid naive credulity in commercial partnerships."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: உன்னத ஆன்மீகக் குடும்பத் துணை, இல்லறத்தில் பூரண அமைதி, தெய்வீக தம்பதிகள்.",
            "பன்னாட்டு அமைப்புகளிலும், ஆன்மீக அறக்கட்டளைகளிலும் மாபெரும் நற்பெயரும் யோகமும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Partner hails from an esteemed spiritual family; sublime peace in domestic life.",
            "Attains high honors in international charitable foundations, celebrated as an exemplary divine couple."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கருத்து வேறுபாடுகள், தற்காலிகப் பிரிவு, துணையின் ஆரோக்கியக் குறைவு.",
            "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஏமாற்றப்பட்டு நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Marital estrangement, emotional distance causing trial separation, spousal health trials.",
            "Heavy financial losses through unprincipled business partners and breach of trust."
        ],
        "career_wealth_ta": [
            "ஆன்மீக ஆசிரமங்கள், மாற்று மருத்துவம், தொண்டு நிறுவனங்கள், சட்ட சமரசம், புத்தக வெளியீடு.",
            "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் ஆன்மீகப் பணிகளாலும் கௌரவமான தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Dominant in spiritual ashrams, alternative medicine, philanthropic trusts, legal mediation, and publishing.",
            "Steady livelihood augmented through spousal frugality and ethical institutional assets."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், அடிவயிற்று வலி, பாலியல் பலவீனம் மற்றும் ஒவ்வாமை.",
            "முறையான நீர் அருந்துதலும், தனிநபர் சுகாதாரமும் நலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to renal sluggishness, pelvic aching, reproductive fatigue, and systemic allergies.",
            "Abundant warm hydration, strict personal hygiene, and periodic urological checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (ரகசிய சித்திகள் / உள்ளுணர்வு & எதிர்பாராத ஆன்மீக யோகம்)",
        "house_title_en": "8th House - Ayur Bhava (Mystical Siddhis, Piercing Intuition & Sudden Spiritual Awakening)",
        "core_traits_ta": [
            "கேது 8-ஆம் பாவத்தில் அமைவது அசாத்தியமான உள்ளுணர்வையும், மறைபொருள் சித்திகளையும் தரும் அமைப்பாகும்.",
            "கனவுகள் பலிக்கும் ஆற்றல், எதிர்காலத்தை முன்கூட்டியே உணரும் நுண்ணறிவு, மந்திர-தந்திர சாஸ்திரங்களில் தேர்ச்சி.",
            "ஆபத்தான விபத்துகள் மற்றும் நெருக்கடிகளிலிருந்து கண்ணுக்குத் தெரியாத தெய்வ சக்தியால் காப்பாற்றப்படுவார்.",
            "மனைவி வழியில் பழைய நிலங்கள், உயில் சொத்துகள் அல்லது காப்பீட்டுத் தொகைகள் வந்து சேரும்."
        ],
        "core_traits_en": [
            "Ketu in the 8th endows extraordinary intuitive perception, prophetic dream visions, and esoteric occult mastery.",
            "Prophetic premonitions; pierces through illusions to discern future trajectories with uncanny precision.",
            "Miraculously safeguarded from catastrophic accidents and physical perils by unseen divine forces.",
            "Inherits unearned ancestral lands, insurance annuities, and testamentary estates through marital ties."
        ],
        "strong_placement_ta": [
            "விருச்சிகத்தில் ஆட்சி அல்லது தனுசில் பலம் பெற்றால்: குண்டலினி யோக சித்தி, ஆன்மீக முக்தி, பல நூறு கோடி உயில் சொத்துகள்.",
            "மறைமுக சாஸ்திரங்களில் மாமேதையாகத் திகழ்ந்து சமுதாயத்தில் உயர்ந்த வழிகாட்டியாக வாழ்வார்."
        ],
        "strong_placement_en": [
            "In own sign Scorpio or exalted in Sagittarius: Awakened Kundalini Siddhis, profound Moksha, and vast legacies.",
            "Revered as an enlightened master of occult metaphysics, guiding advanced spiritual aspirants."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மூல நோய், ஆசனவாய் வெடிப்பு, தீராத வாத நோய்கள், விபத்துகள்.",
            "உயில் விவகாரங்களில் வழக்குகளும், அரசாங்க அபராதங்களால் மன உளைச்சலும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe hemorrhoids, anal fissures, chronic rheumatoid disorders, and accidental injuries.",
            "Protracted probate disputes over contested inheritances and government tax scrutiny."
        ],
        "career_wealth_ta": [
            "ஜோதிட ஆராய்ச்சி, சித்த மருத்துவம், தொல்பொருள் ஆராய்ச்சி, தடயவியல், ஆயுள் காப்பீடு, ரகசிய நிதி ஆலோசகர்.",
            "உயில் சொத்துகள், காப்பீட்டு முதிர்வுகள் மற்றும் திடீர் தன வரவால் பெருஞ்செல்வம்."
        ],
        "career_wealth_en": [
            "Distinguished in astrological research, Siddha pharmacology, archaeology, forensic pathology, and private wealth office.",
            "Substantial capital influx via testamentary bequests, insurance settlements, and confidential contracts."
        ],
        "health_precautions_ta": [
            "மூல நோய் (Piles), ஆசனவாய் புண்கள், நரம்பு வலி, விஷக்கடி மற்றும் தூக்கமின்மை.",
            "நார்ச்சத்து மிகுந்த உணவுகளையும், எண்ணெய் மசாஜ்களையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
        ],
        "health_precautions_en": [
            "Vulnerable to hemorrhoidal inflammation, anal fissures, peripheral neuropathy, toxic stings, and insomnia.",
            "High-fiber cooling diet, warm sitz baths, and avoiding sedentary stagnation protect health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம ஞானம், பரம பக்தி & ஆன்மீக யாத்திரை)",
        "house_title_en": "9th House - Bhagya Bhava (Dharmic Gnosis, Sublime Devotion & Sacred Pilgrimages)",
        "core_traits_ta": [
            "கேது 9-ஆம் பாவத்தில் அமைவது உன்னதமான தர்ம சிந்தனையையும், இறைவனின் மீது எல்லை இல்லாத பக்தியையும் தரும்.",
            "புனிதத் தலங்களுக்கு யாத்திரை செல்வதிலும், மலைக் குகைகளில் தியானம் செய்வதிலும் பேரானந்தம் அடைவார்.",
            "தந்தையின் மீது பக்தி; தந்தையிடமிருந்து ஆன்மீக நற்குணங்களையும் தர்ம வழிகளையும் கற்றுத் தேர்ந்திருப்பார்.",
            "வாழ்க்கையில் உலக ஆசைகளைக் கடந்து ஆத்ம ஞானத்தை அடைவதே இவரின் தலையாய லட்சியமாக இருக்கும்."
        ],
        "core_traits_en": [
            "Ketu in the 9th inspires pristine ethical nobility, deep scriptural piety, and boundless devotional love.",
            "Passionate love for pilgrimages to sacred mountain hermitages, remote river confluences, and ancient temples.",
            "Reverent bond with a noble, spiritually awakened father whose ethical legacy guides life decisions.",
            "Prioritizes the realization of Self-knowledge (Atma Jnana) above all ephemeral worldly accolades."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: அகண்ட தர்ம யோகம், சர்வதேச ஆன்மீக பீடாதிபதி, அரச குடும்பங்களின் கௌரவம்.",
            "வேத பாடசாலைகளையும், ஆசிரமங்களையும் நிறுவி உலகெங்கும் லட்சக்கணக்கான மக்களுக்கு வழிகாட்டுவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Supreme Dharma Yoga! Revered as an international pontiff and saintly advisor to statesmen.",
            "Founds monumental Vedic academies and ashrams, guiding hundreds of thousands onto the path of liberation."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, மத நம்பிக்கைகளில் முரண்பாடுகள்.",
            "புனிதப் பயணங்களில் பொருள் இழப்பு அல்லது ஏமாற்றங்கள் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health difficulties, cynicism towards institutional priesthood, and travel hassles.",
            "Loss of baggage or financial disappointment during sacred pilgrimages."
        ],
        "career_wealth_ta": [
            "மத அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், ஆன்மீக நூலாசிரியர், தொண்டு நிறுவனங்கள், இயற்கை மருத்துவம்.",
            "தர்ம வழியில் சேர்க்கும் வற்றாத செல்வமும், பரம்பரைச் சொத்துகளும் நிலைத்து நிற்கும்."
        ],
        "career_wealth_en": [
            "Commands high status as religious trust president, university chancellor, spiritual author, and humanitarian trustee.",
            "Pure, untainted wealth accrued through principled educational licensing and ethical donations."
        ],
        "health_precautions_ta": [
            "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம் (Sciatica), உடல் சோர்வு மற்றும் செரிமானக் கோளாறுகள்.",
            "மிதமான நடைப்பயிற்சியும் சாத்வீக உணவு முறையும் உடல்நலனைப் பேணும்."
        ],
        "health_precautions_en": [
            "Susceptible to hip stiffness, sciatica sensitivity, and intermittent physical fatigue.",
            "Gentle walking outdoors and a nourishing sattvic diet preserve long-term vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (தர்ம தொழில், ஆன்மீக தலைமை & பற்றற்ற சாதனை)",
        "house_title_en": "10th House - Karma Bhava (Dharmic Career, Spiritual Leadership & Selfless Achievement)",
        "core_traits_ta": [
            "தொழிலில் நேர்மை, தர்ம நெறி தவறாமை, லஞ்ச-ஊழலை அடியோடு வெறுக்கும் உன்னதமான சுபாவம்.",
            "பதவி, அதிகாரம் ஆகியவற்றை விட சமுதாயத்திற்கு நல்ல சேவை செய்வதையே தன் கடமையாகக் கருதுவார்.",
            "அரசாங்க உயர் அதிகாரிகளுடனும் மக்கள் மத்தியிலும் சிறந்த நற்பெயரும், மரியாதையும் பெறுவார்.",
            "தொழிலில் சில சமயம் எதிர்பாராத மாற்றங்களும், ஆன்மீகத்தை நோக்கித் திரும்பும் சூழலும் உருவாகலாம்."
        ],
        "core_traits_en": [
            "Impeccable occupational integrity; steadfastly rejects corruption, deceit, or underhanded shortcuts.",
            "Views professional career as a sacred service (Seva) to society rather than a vehicle for selfish aggrandizement.",
            "Commands profound respect and moral authority among civic regulators, peers, and the public.",
            "May experience sudden vocational transitions, redirecting professional acumen towards spiritual or humanitarian frontiers."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் அமைந்தால்: தலைமை நீதிபதி, ஆன்மீக நிறுவனங்களின் தலைவர், அரசாங்க கௌரவப் பதவிகள்.",
            "நாட்டின் முதன்மை அறக்கட்டளைகள் மற்றும் தொண்டு சாம்ராஜ்யத்தை வழிநடத்தி அழியாத புகழ் பெறுவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Supreme Court justice, director of premier spiritual foundations, or cabinet counselor.",
            "Presides over monumental philanthropic trusts, immortalized as an unblemished public servant."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், உயர் அதிகாரிகளுடன் கருத்து மோதல்கள்.",
            "தொழிலில் நேர்மையாக இருந்தும் அவப்பெயர் உண்டாக வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Frequent erratic job switches, friction with autocratic superiors, and professional disillusionment.",
            "Unmerited public scrutiny despite transparently honest intentions."
        ],
        "career_wealth_ta": [
            "நீதித்துறை, இயற்கை மருத்துவம், தொண்டு நிறுவனங்கள், தொல்பொருள் ஆராய்ச்சி, ஆன்மீக மடங்கள், சமூக சேவை.",
            "நேர்மையான உழைப்பாலும் சேவைகளாலும் நிலையான தன வரவு."
        ],
        "career_wealth_en": [
            "Flourishes in the judiciary, naturopathic healthcare, philanthropic trusts, epigraphy, and community welfare.",
            "Steady, secure income built upon principled public service and administrative competence."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் மூட்டு வலி, ரத்த அழுத்தம், தூக்கமின்மை மற்றும் வாதக் கோளாறுகள்.",
            "வேலைக்கு நடுவே தியானமும், ஓய்வும் எடுப்பது ஆரோக்கியத்தைப் பாதுகாக்கும்."
        ],
        "health_precautions_en": [
            "Occupational stress, knee joint stiffness, hypertension, and sleep deprivation.",
            "Structured meditation, daily exercise, and portion control maintain executive health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / பற்றற்ற வருவாய் & ஆன்மீக நட்பு)",
        "house_title_en": "11th House - Labha Bhava (Massive Inflows, Wish Fulfillment & Ascetic Allies)",
        "core_traits_ta": [
            "கேது 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு அளப்பரிய செல்வத்தையும், தொடர் லாபங்களையும் தரும் மிகச்சிறந்த யோகமாகும்.",
            "எடுத்த காரியங்கள் யாவும் எளிதில் நிறைவேறும்; பல வழிகளிலிருந்து வற்றாத நிதி வரவு வந்துகொண்டே இருக்கும்.",
            "ஆன்மீக மகான்கள், சித்தர்கள், தத்துவ ஞானிகள் மற்றும் செல்வந்தர்களின் உயர்ந்த நட்பு வட்டம் அமையும்.",
            "மூத்த சகோதரர்களிடம் அன்பான உறவும், அதே சமயம் சுதந்திரமான மனப்பான்மையும் நிலவும்."
        ],
        "core_traits_en": [
            "Ketu in the 11th (an Upachaya house) is one of the most prolific placements for effortless financial accumulation.",
            "Frictionless fulfillment of cherished goals; unceasing multi-channel cash streams flood his accounts.",
            "Surrounded by a high-minded circle of enlightened yogis, philosophers, philanthropists, and magnates.",
            "Harmonious camaraderie with elder siblings combined with mutual intellectual independence."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான சொத்துகள், அறக்கட்டளைகள், குபேர யோகம்.",
            "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு வாழ்வளிக்கும் மகா வள்ளலாகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-million dollar asset portfolios, charitable foundations, and supreme Kubera Yoga.",
            "Acts as a legendary philanthropist, establishing university scholarships, hospitals, and heritage restorations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் பிரிவு.",
            "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் கடன்கள் ஏற்படுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by counterfeit associates, capital erosion, and sibling estrangement.",
            "Anticipated dividends vanish through unexpected bureaucratic bottlenecks."
        ],
        "career_wealth_ta": [
            "ஆன்மீக அறக்கட்டளைகள், இயற்கை மூலிகை ஏற்றுமதி, தொண்டு நிறுவன முதலீடுகள், புத்தக பதிப்பகம், மாற்று மருத்துவம்.",
            "முதலீடுகளின் அபரிமிதமான வளர்ச்சியால் சமுதாயத்தின் பெரும் பணக்காரராக உயருதல்."
        ],
        "career_wealth_en": [
            "Lucrative success in spiritual foundations, organic herbal export, philanthropic endowments, and alternative medicine.",
            "Extraordinary capital multiplication placing the native in the elite wealthy tier."
        ],
        "health_precautions_ta": [
            "இடது காது கேளாமை, கணுக்கால் வாதம், தசை இறுக்கம் மற்றும் ரத்த ஓட்டக் குறைபாடுகள்.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear dullness, ankle joint stiffness, and sluggish peripheral circulation.",
            "Daily ankle mobility drills, compression socks for long flights, and otic checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்ச காரகன் தன் சொந்த ஸ்தானத்தில் / பூரண ஜீவன் முக்தி)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Mokshakaraka in Prime House / Sublime Spiritual Liberation)",
        "core_traits_ta": [
            "மோட்ச காரகனான கேது 12-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் மிக உன்னதமான மோட்ச யோகமாகும் (Kaivalya Moksha).",
            "பிறவிப் பெருங்கடலை நீந்தி இறைவனின் திருவடிகளில் ஐக்கியமாகும் ஜீவன் முக்தி நிலை.",
            "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், கோவில் திருப்பணிகள், தியான மையங்கள் மற்றும் ஆன்மீக காரியங்களுக்குச் செலவிடுவார்.",
            "தனிமையில் தியானம் செய்வதில் பேரானந்தம் அடைவார்; ஆழ்ந்த தூக்கமும், அமைதியான மன நிலையும் நிறைந்திருக்கும்."
        ],
        "core_traits_en": [
            "Mokshakaraka Ketu in the 12th is celebrated as the absolute zenith of spiritual evolution: bestows Kaivalya Moksha.",
            "Attains definitive transcendence from the wheel of samsaric reincarnation, merging into the Divine Light.",
            "Directs worldly wealth exclusively towards temple renovations, secluded hermitages, and spiritual feeding.",
            "Delights in contemplative silence, experiencing ecstatic Samadhi and unperturbed restorative rest."
        ],
        "strong_placement_ta": [
            "விருச்சிகம்/தனுசில் சுப பலத்துடன் இருப்பின்: உலகப் புகழ் பெற்ற ஜீவன் முக்தர், சர்வதேச ஆன்மீக ஆசிரமங்கள், மோட்ச சாதனை.",
            "அயன சயன சுகம் பூரணமாகக் கிட்டும்; சமுதாயத்தில் பெரும் ஞானியாகப் போற்றப்பட்டு சமாதி நிலை எய்துவார்."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Revered as an authentic Jivanmukta (liberated soul), founding international ashrams.",
            "Enjoys divine peace, celestial dreams, and effortless conscious transition into Supreme Nirvana."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, இடது கண் பார்வை மங்குதல், ஏமாற்றங்கள்.",
            "வீண் விரயங்கள், போலி ஆன்மீகவாதிகளால் பண இழப்பு மற்றும் மன அமைதியின்மை."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe insomnia, left-eye vision defects, and financial deceit by bogus gurus.",
            "Fruitless financial drainage, loneliness, and persistent melancholic restlessness."
        ],
        "career_wealth_ta": [
            "ஆன்மீக ஆசிரமங்கள், தியான பீடங்கள், யோகா கல்வி நிறுவனங்கள், இயற்கை மருத்துவமனைகள், தொண்டு நிறுவனங்கள்.",
            "வெளிநாட்டு ஆன்மீகக் கொடைகளாலும் அறக்கட்டளைகளாலும் நிறைவான செல்வம்."
        ],
        "career_wealth_en": [
            "Stellar leadership in contemplative monasteries, meditation retreats, yogic universities, and holistic hospices.",
            "Sustained through generous spiritual endowments, book royalties, and international trust funds."
        ],
        "health_precautions_ta": [
            "இடது கண் பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை (Insomnia) மற்றும் வாத நோய்கள்.",
            "இரவில் அமைதியான தியானமும், பாதங்களை வெதுவெதுப்பான நீரால் கழுவுதலும் நல்ல தூக்கத்தைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye ocular strain, peripheral foot neuralgia, insomnia, and systemic vata disorders.",
            "Nightly grounding meditation, warm foot reflexology baths, and tranquil sleep hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]
