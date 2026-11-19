# -*- coding: utf-8 -*-
"""
Planetary House Predictions for Sun (சூரியன்), Moon (சந்திரன்), and Mars (செவ்வாய்)
Based on Dr. B. V. Raman's "How to Judge a Horoscope" & Classical Saravali
"""

SUN_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (தனு பாவம் / சுய கௌரவம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Self & Dignity)",
        "core_traits_ta": [
            "அதிகமான தன்னம்பிக்கை, கம்பீரமான தோற்றம் மற்றும் தலைமை தாங்கும் குணம் கொண்டவர்.",
            "மானமரியாதை மற்றும் சுயகௌரவத்திற்கு அதிமுக்கியத்துவம் கொடுப்பவர்; தலைவணங்க விரும்பாத சுபாவம்.",
            "விரைவில் கோபமும் ஆவேசமும் வரும் முன்கோபித்தனம் உண்டு; ஆனால் கோபம் நிலைக்காது.",
            "உயர்ந்த லட்சியங்கள், நேர்மையான கொள்கைகள் மற்றும் சுதந்திரமான சிந்தனைப்போக்கு உடையவர்.",
            "பிறர் ஆதிக்கத்தையோ கட்டுப்பாட்டையோ ஒருபோதும் ஏற்க மாட்டார்."
        ],
        "core_traits_en": [
            "Strong moral nature, righteous minded, ambitious, and lover of authority and power.",
            "Places immense value on personal self-respect, honor, and dignity; refuses subservience.",
            "Quick-tempered and spirited with a fiery temperament, though anger subsides quickly.",
            "Possesses a magnetic presence, robust vitality, and natural leadership aptitude.",
            "Cherishes independence and fiercely resists being dominated by others."
        ],
        "strong_placement_ta": [
            "மேஷத்தில் உச்சம் அல்லது சிம்மத்தில் ஆட்சி பெற்றால்: அளப்பரிய அரசு கௌரவம், சமுதாயத்தில் முதன்மை அந்தஸ்து மற்றும் நீண்ட ஆயுள் உண்டாகும்.",
            "திக்பலம் அல்லது அதிக ஷட்பலத்துடன் இருப்பின்: அரசாங்க உயர்பதவி, அரசியல் செல்வாக்கு மற்றும் பிறரால் போற்றப்படும் பெருவாழ்வு அமையும்."
        ],
        "strong_placement_en": [
            "Exalted in Aries or in own sign Leo: Confers high government rank, commanding stature, robust health, and longevity.",
            "High Shadbala or Digbala: Endows executive power, magnetic charisma, and triumph in all public endeavors."
        ],
        "weak_placement_ta": [
            "துலாத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கண் உபாதைகள், தலைவலி, அதிக அலைச்சல் மற்றும் பிடிவாத குணம் உண்டாகலாம்.",
            "பகை/நீச பலம் பெற்றால்: காரணமற்ற கோபம், தற்பெருமை மற்றும் தந்தையுடன் கருத்து வேறுபாடுகள் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated in Libra or afflicted by Saturn/Rahu: Tends towards eye afflictions, chronic headaches, ego clashes, and restless wandering.",
            "Low planetary strength: Leads to unwarranted arrogance, strained relations with the father, and obstacles in public life."
        ],
        "career_wealth_ta": [
            "நிர்வாகத் துறை, அரசுப் பணிகள், மருத்துவம், அரசியல், அதிகாரப் பதவிகள் மற்றும் தலைமைப் பொறுப்புகளில் பெரும் வெற்றி.",
            "சொந்த உழைப்பாலும் கௌரவமான வழிகளாலும் செல்வமும் சமுதாய மதிப்பும் ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Success in administrative services, state leadership, governance, medicine, defense, and entrepreneurial leadership.",
            "Acquires wealth through honorable self-exertion, commanding positions, and royal or state patronage."
        ],
        "health_precautions_ta": [
            "உடலில் பித்த உஷ்ணம், கண் சம்மந்தப்பட்ட உபாதைகள், ரத்த அழுத்த மாறுபாடுகள் மற்றும் தலைவலி ஏற்பட வாய்ப்புண்டு.",
            "குளிர்ந்த நீர் அருந்துதல் மற்றும் அதிக வெயிலைத் தவிர்ப்பது நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Prone to bilious heat, febrile complaints, eye strain, and blood pressure fluctuations.",
            "Benefited by cooling foods, balanced hydration, and regular eye care."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 51) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (வாக்கு, தனம் & குடும்பம்)",
        "house_title_en": "2nd House - Dhana Bhava (Wealth, Speech & Family)",
        "core_traits_ta": [
            "பேச்சில் உறுதியும், அதிகார தோரணையும், கம்பீரமான குரல்வளமும் கொண்டவர்.",
            "தான் நினைத்ததை வெளிப்படையாகவும் அழுத்தமாகவும் பேசும் நேர்மையான குணம்.",
            "குடும்பத்தில் தலைமைப் பொறுப்பை ஏற்று நடத்தும் சுபாவம்; விட்டுக் கொடுக்காத கொள்கை.",
            "கடின உழைப்பால் மட்டுமே செல்வத்தைச் சேர்க்க வேண்டும் என்ற தளராத உறுதி கொண்டவர்."
        ],
        "core_traits_en": [
            "Possesses a firm, commanding, and authoritative tone of voice; speaks truthfully and directly.",
            "Values financial independence through industrious, hard-earned effort.",
            "Tends to assume headship of family affairs; unyielding on ethical principles.",
            "May display stubbornness in financial and domestic negotiations."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பூர்வீகச் சொத்துகள், அரசாங்கக் கொடைகள் மற்றும் நிலையான வங்கி இருப்பு அமையும்.",
            "சுபப் பார்வை இருப்பின்: வாக்கு பலிதம், இனிமையான பேச்சு மற்றும் செல்வச் செழிப்புடன் கூடிய குடும்ப நலம் கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Accumulates solid ancestral wealth, earns state subsidies, and gains high financial security.",
            "Benefic aspects: Confers influential speech, respected lineage, and abundant fiscal prosperity."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: அதிகாரிகளிடம் வாக்குவாதம் செய்து இழப்பு ஏற்படுதல், முகத்தில் வடுக்கள் உண்டாகலாம்.",
            "பண விரயங்களும், பேச்சினால் உறவினர்களிடம் மனக்கசப்புகளும் ஏற்படக்கூடும்."
        ],
        "weak_placement_en": [
            "Afflicted or debilitated: Financial losses due to friction with authorities, domestic disputes, and face/mouth ailments.",
            "Harsh speech may alienate family members and lead to sudden financial drain."
        ],
        "career_wealth_ta": [
            "வங்கிகள், நிதித்துறை, அரசு கருவூலம், நகை/தங்கம் வர்த்தகம் மற்றும் சட்ட ஆலோசனைகளில் தன லாபம்.",
            "சுயமுயற்சியால் சொத்துகளைச் சேர்ப்பார்; அரசு வழியில் ஆதாயம் உண்டு."
        ],
        "career_wealth_en": [
            "Gains through banking, government treasury, precious metals/gems, legal advocacy, and revenue administration.",
            "Builds tangible assets through resolute perseverance and disciplined money management."
        ],
        "health_precautions_ta": [
            "வலது கண் கோளாறுகள், தொண்டை அல்லது பற்கள் சம்மந்தப்பட்ட வியாதிகள், வாய் புண்கள் வரலாம்.",
            "சூடான மற்றும் அதிக காரமான உணவுப் பண்டங்களைக் குறைப்பது நல்லது."
        ],
        "health_precautions_en": [
            "Susceptibility to right-eye afflictions, facial heat eruptions, and throat irritations.",
            "Advised to moderate spicy food intake and maintain oral dental hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 99) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (தைரியம் & வீரியம்)",
        "house_title_en": "3rd House - Sahaja Bhava (Courage, Valor & Enterprise)",
        "core_traits_ta": [
            "அசாத்தியமான மனத்துணிச்சல், வீரம் மற்றும் எந்த சவாலையும் எதிர்கொள்ளும் திடமான குணம்.",
            "எதிரிகளைத் துணிச்சலாக வெல்லும் ஆற்றல்; உபசய ஸ்தானத்தில் சூரியன் அமர்வது சிறந்த அமைப்பாகும்.",
            "சுயமரியாதையும் கம்பீரமும் கொண்ட செயல்வீரர்; பிறரிடம் கையேந்தாத சுயசார்பு.",
            "இளைய சகோதரர்களிடம் சற்று கண்டிப்பும் மேலாதிக்கப் போக்கும் கொண்டிருக்கலாம்."
        ],
        "core_traits_en": [
            "Extraordinary courage, high fortitude, and undaunted valor in overcoming obstacles.",
            "Sun in the 3rd (an Upachaya house) is hailed as an auspicious placement for vanquishing adversaries.",
            "Self-reliant, highly spirited, and capable of driving ventures with fearless enterprise.",
            "May exert a firm, demanding authority over younger siblings."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடெங்கும் புகழ், மாபெரும் பராக்கிரமம் மற்றும் வெற்றிகள் குவியும்.",
            "உயர் அதிகாரிகளுடனும் முக்கியஸ்தர்களுடனும் நெருங்கிய நட்பும் அதனால் பெரும் நன்மைகளும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Strong or exalted: Confers far-reaching fame, heroic standing, and prosperous journeys.",
            "Commands respect among dignitaries, armed forces, or top-level corporate boards."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப தொடர்புகள் பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் வலி அல்லது காயங்கள் உண்டாகலாம்.",
            "அதிகமான பிடிவாதத்தால் வீண் பகைகளும் மன உளைச்சலும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Afflicted or debilitated: Friction with brothers, shoulder/arm injuries, and unyielding obstinacy.",
            "May foster unnecessary antagonisms through excessive rashness."
        ],
        "career_wealth_ta": [
            "ராணுவம், காவல் துறை, விளையாட்டு, எழுத்து, தகவல் தொடர்பு, பிரசுரத் தொழில் மற்றும் பொது நிர்வாகத்தில் உயர்வு.",
            "தைரியமான முதலீடுகள் மற்றும் குறுகிய பயணங்கள் மூலம் தன வரவு அதிகரிக்கும்."
        ],
        "career_wealth_en": [
            "Lucrative success in defense services, policing, journalism, competitive sports, publishing, and transport.",
            "Gains wealth through audacious strategic initiatives and lucrative business travels."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை அல்லது காது குடைச்சல் வரலாம்.",
            "முறையான உடற்பயிற்சியும் தோள் பட்டைக்கான ஆசனங்களும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to shoulder stiffness, upper arm injuries, and hearing or ear sensitivities.",
            "Benefited by regular shoulder exercises and balanced nervous relaxation."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 139) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (தாய், நிலம் & மன அமைதி)",
        "house_title_en": "4th House - Sukha Bhava (Mother, Property & Domestic Life)",
        "core_traits_ta": [
            "உயர்ந்த கொள்கைகளும், தத்துவ சிந்தனைகளும், பாரம்பரியத்தின் மீது தீவிர பற்றும் கொண்டவர்.",
            "வீட்டிலும் குடும்பத்திலும் தன் ஆதிக்கமும் கட்டுப்பாடும் இருக்க வேண்டும் என விரும்புவார்.",
            "மனதில் ஒருவிதமான அலைபாயும் தன்மையும், அடிக்கடி உள்ளுக்குள் கொதிக்கும் வேகமும் இருக்கலாம்.",
            "தாய் வழியில் ஒழுக்கமும் மரியாதையும் பெற்றவர்; ஆன்மீக மற்றும் ரகசிய சாஸ்திரங்களில் ஆர்வம்."
        ],
        "core_traits_en": [
            "Philosophical, dignified, and holds deep attachment to family heritage and traditional values.",
            "Desires order and authority within the domestic household; can be strict with dependents.",
            "Experiences occasional internal restlessness despite an outward poise.",
            "Inclined towards deep contemplation, ancient scriptures, and occult wisdom."
        ],
        "strong_placement_ta": [
            "சுப ஸ்தானம் அல்லது ஆட்சி/உச்சம் பெற்றால்: மாட மாளிகைகள், பூமி லாபம், ஆடம்பர வாகனங்கள் மற்றும் மன நிம்மதி கிட்டும்.",
            "தந்தையின் சொத்துகள் தடையின்றி வந்து சேரும்; தாய்வழி உறவுகளால் மரியாதை உண்டாகும்."
        ],
        "strong_placement_en": [
            "Exalted or well-aspected: Grants grand residential estates, fertile lands, conveyance luxuries, and stable peace.",
            "Inherits ancestral properties seamlessly and enjoys honorable paternal favor."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக் குறைவு, வீட்டு சூழலில் அமைதியின்மை மற்றும் சொத்து தகராறுகள் ஏற்படலாம்.",
            "வாகனங்களால் செலவுகளும், பூர்வீக வீட்டை விட்டு இடம்பெயரும் சூழ்நிலையும் உருவாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Domestic friction, mother's frail health, property litigations, and heart anxieties.",
            "Disputes over parental inheritance and frequent changes of residence."
        ],
        "career_wealth_ta": [
            "நிலம், ரியல் எஸ்டேட், சுரங்கத் தொழில், விவசாயம், கட்டிடக் கலை மற்றும் அரசு மானியங்கள் மூலம் செல்வம்.",
            "அரசு வாகன யோகம் மற்றும் கௌரவப் பதவிகள் கிட்டும்."
        ],
        "career_wealth_en": [
            "Thrives in real estate, civil engineering, mining, agriculture, automotive industries, and government quarters.",
            "Builds enduring asset portfolios in prime landed properties."
        ],
        "health_precautions_ta": [
            "இதயப் படபடப்பு, நெஞ்சு சளி, ரத்த அழுத்தம் மற்றும் மன உளைச்சலுக்கு வாய்ப்புண்டு.",
            "யோகா, பிராணாயாமம் மற்றும் எளிய உணவுகள் இதய நலனைப் பாதுகாக்கும்."
        ],
        "health_precautions_en": [
            "Vulnerable to cardiac strain, chest congestion, blood pressure surges, and mental stress.",
            "Cardiovascular checkups and deep breathing meditation are strongly advised."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 173) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (புத்தி & புத்திர பாவம்)",
        "house_title_en": "5th House - Putra & Poorvapunya Bhava (Intellect, Progeny & Merit)",
        "core_traits_ta": [
            "கூர்மையான மதிநுட்பம், ஆழமான புத்திசாலித்தனம் மற்றும் திட்டமிட்டு செயலாற்றும் திறன் கொண்டவர்.",
            "தெய்வ பக்தி, மந்திர சித்தி மற்றும் வேத சாஸ்திரங்களை எளிதில் கிரகிக்கும் ஆற்றல் உண்டு.",
            "மானமரியாதைக்கு முதலிடம் கொடுப்பதால் தன் புத்திசாலித்தனத்தைப் பிறர் குறை கூற அனுமதிக்க மாட்டார்.",
            "குழந்தைகளிடம் சற்று கண்டிப்பான அணுகுமுறையைக் கடைப்பிடிக்க வாய்ப்புண்டு."
        ],
        "core_traits_en": [
            "Sharp intellect, piercing analytical insight, and impressive strategic acumen.",
            "Deep spiritual inclination, inclination towards mantras, ethical philosophy, and higher research.",
            "Takes immense pride in intellectual superiority; hates superficiality.",
            "May exhibit an authoritative, disciplinary attitude towards children."
        ],
        "strong_placement_ta": [
            "சிம்மத்தில் ஆட்சி அல்லது மேஷத்தில் உச்சம் பெற்றால்: புகழ்பெற்ற சந்ததிகள், சமுதாயத்தில் உயரிய ஆலோசனைப் பதவிகள் மற்றும் அரச யோகம்.",
            "முற்பிறவி புண்ணிய பலத்தால் எடுத்த காரியங்கள் யாவிலும் தொடர் வெற்றி மற்றும் செல்வச் செழிப்பு."
        ],
        "strong_placement_en": [
            "Exalted or in own sign: Bestows distinguished, successful children, royal counsel status, and vast good fortune.",
            "Harvests the fruits of past-life merit (Poorvapunya) through intuitive breakthroughs and fame."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் பார்வை இருப்பின்: புத்திர பாக்கியத்தில் காலதாமதம், பிள்ளைகளுடன் கருத்து வேறுபாடு ஏற்படலாம்.",
            "ஊக வணிகம் (Speculation) அல்லது பங்குச் சந்தையில் அவசரப்பட்டு நஷ்டமடையக்கூடும்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Delays or anxieties regarding children, strained relationship with first child.",
            "Heavy losses through impulsive speculative trades or gambling tendencies."
        ],
        "career_wealth_ta": [
            "அரசியல் ஆலோசகர், பேராசிரியர், திட்ட இயக்குநர், நிதி மேலாண்மை, ஆராய்ச்சி மற்றும் கலைத் துறைகளில் சாதனை.",
            "மந்திர, ஜோதிட அல்லது ஆன்மீகத் துறைகளிலும் நல்ல வருமானம் கிட்டும்."
        ],
        "career_wealth_en": [
            "Excels as political strategist, university dean, corporate director, fund manager, and scientific researcher.",
            "Financial success through administrative advisory and intellectual creations."
        ],
        "health_precautions_ta": [
            "வயிற்றுப் பகுதியில் உஷ்ணக் கோளாறுகள், செரிமானக் குறைபாடு மற்றும் அமிலத்தன்மை (Acidity) வரலாம்.",
            "காரமான உணவுகளைத் தவிர்த்து நீர்ச்சத்து மிகுந்த காய்கறிகளை உண்பது நல்லது."
        ],
        "health_precautions_en": [
            "Prone to stomach gastric fires, indigestion, liver sluggishness, and peptic discomfort.",
            "A balanced alkaline diet with abundant fluids is recommended."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 219) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு & ரோக பாவம் (எதிரி ஜெயம் & தைரியம்)",
        "house_title_en": "6th House - Satru & Roga Bhava (Victory Over Foes & Immunity)",
        "core_traits_ta": [
            "எதிரிகளை அடியோடு முறியடிக்கும் பராக்கிரமம்; வழக்குகளிலும் போட்டிகளிலும் வெல்லும் ஆற்றல்.",
            "சூரியன் 6-ஆம் பாவத்தில் அமர்வது மிகச் சிறந்த உபசய பலனாகும்; சவால்களைத் துணிவுடன் தகர்ப்பார்.",
            "கடுமையான உழைப்பாளி; மற்றவர்களுக்குக் கீழ் வேலை செய்வதிலும் தன் ஆளுமையை நிலைநாட்டுவார்.",
            "தாய்மாமனுடன் சில சமயம் கருத்து மோதல்கள் ஏற்படலாம்."
        ],
        "core_traits_en": [
            "Unflinching valor in overcoming opposition; crushes competitors and legal adversaries.",
            "Sun in the 6th is classically celebrated as a powerful Upachaya shield that bestows heroic resilience.",
            "Indefatigable worker with high executive discipline; refuses to succumb under pressure.",
            "May encounter complex relations or boundary disputes with maternal relatives."
        ],
        "strong_placement_ta": [
            "சுப வலுவுடன் இருப்பின்: அரசாங்க உயர் பொறுப்புகள், எதிரிகள் இல்லாத நிம்மதியான வாழ்வு மற்றும் அசைக்க முடியாத சரீர பலம்.",
            "நீதித்துறை, ராணுவம் அல்லது நிர்வாகப் போட்டிகளில் எப்போதும் முதலிடம் பிடிப்பார்."
        ],
        "strong_placement_en": [
            "Strong or exalted: Ensures total conquest of all foes, debt-free prosperity, and ironclad physical immunity.",
            "Commands high authority in civil services, judiciary, military, or labor unions."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப யோகம் இருப்பின்: தீராத உஷ்ண வியாதிகள், ரத்த சோகை அல்லது கடன் தொல்லைகள் வரலாம்.",
            "வேலையாட்களால் ஏமாற்றப்படுதலும், கண் வலி அல்லது சிறுநீரக பாதிப்புகள் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Recurrent febrile conditions, chronic blood impurities, and burdensome debt litigation.",
            "Troubles through subordinates, servants, or hostile workplace rivals."
        ],
        "career_wealth_ta": [
            "மருத்துவம், சட்டம் மற்றும் நீதித்துறை, ஆயுதப் படைகள், வங்கித் துறையில் கடன் மீட்பு மற்றும் தணிக்கைத் துறை.",
            "எதிர்ப்புகளையும் தடைகளையும் தனக்குச் சாதகமாக மாற்றிப் பெரும்பொருள் ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Thrives in healthcare/surgery, corporate law, forensic auditing, defense, and debt restructuring.",
            "Turns competitive crises into lucrative career breakthroughs and steady financial power."
        ],
        "health_precautions_ta": [
            "வயிற்றுக்கடுப்பு, பித்தக் கோளாறுகள், தொடை மற்றும் இடுப்புப் பகுதியில் வலிகள் வரலாம்.",
            "உடலில் நீரிழப்பு ஏற்படாமல் பார்த்துக் கொள்வதும் சீரான உடற்பயிற்சியும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to kidney stones, hepatic irritation, lower intestinal inflammation, and skin rashes.",
            "Maintain proper hydration and avoid over-exertion under the hot sun."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 260) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (வாழ்க்கைத் துணை & கூட்டுத்தொழில்)",
        "house_title_en": "7th House - Kalathra Bhava (Spouse & Partnerships)",
        "core_traits_ta": [
            "வாழ்க்கைத் துணையிடம் ஆதிக்கமும் மேலாதிக்கப் போக்கும் செலுத்தும் குணம்; தன் சொல்லே எடுபட வேண்டும் என்ற எண்ணம்.",
            "வெளிப்படையான மற்றும் கம்பீரமான ஆளுமை; பிறரை எளிதில் ஈர்க்கும் தகைமை.",
            "திருமண வாழ்வில் ஈகோ (Ego) மோதல்கள் வராமல் கவனமாகப் பேண வேண்டியது அவசியம்.",
            "தொழில் கூட்டாளிகளுடன் ஒப்பந்தங்களில் கண்டிப்பும் வெளிப்படைத்தன்மையும் கொண்டிருப்பார்."
        ],
        "core_traits_en": [
            "Authoritative attitude towards spouse; desires to be the dominant guiding voice in matrimonial ties.",
            "Possesses a regal demeanor that naturally attracts public attention and social recognition.",
            "Requires conscious management of pride and ego to maintain harmonious marital peace.",
            "Demands absolute transparency and formal protocol in business joint ventures."
        ],
        "strong_placement_ta": [
            "சுப கிரகங்களின் சேர்க்கை அல்லது ஆட்சி/உச்சம் பெற்றால்: புகழ்பெற்ற, வசதியான குடும்பத்திலிருந்து வாழ்க்கைத் துணை அமைவார்.",
            "வெளிநாட்டு வர்த்தகங்களிலும், பொது அமைப்புகளிலும் மாபெரும் மதிப்பும் வருமானமும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Well-aspected or exalted: Partner comes from an honorable, prosperous, and high-status family background.",
            "Brings remarkable prestige and fiscal windfalls through foreign trade and diplomatic missions."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் இருப்பின்: திருமண வாழ்வில் மனக்கசப்புகள், காலதாமதமான திருமணம் அல்லது தற்காலிகப் பிரிவு.",
            "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்படுதலும் அரசுத் தடைகளும் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Afflicted or debilitated: Marital friction, domestic estrangement, delayed nuptials, or spousal health challenges.",
            "Disputes and unexpected financial losses in commercial partnerships."
        ],
        "career_wealth_ta": [
            "பொது நிர்வாகம், அரசியல் பிரதிநிதித்துவம், ஏற்றுமதி-இறக்குமதி, சட்ட ஒப்பந்தங்கள் மற்றும் வர்த்தகப் பிரதிநிதித்துவம்.",
            "வாழ்க்கைத் துணையின் வழியே கௌரவமும் அதிர்ஷ்டமும் சேர்ந்து வரக்கூடும்."
        ],
        "career_wealth_en": [
            "Success in international diplomacy, foreign commerce, contract negotiation, corporate lobbying, and public arbitration.",
            "Potential for substantial financial advancement through marriage and strategic alliances."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், அடிவயிற்று வலி, நீரிழிவு அல்லது தாம்பத்திய உறுப்புகளில் உஷ்ணம் உண்டாகலாம்.",
            "முறையான ஓய்வும் மருத்துவப் பரிசோதனைகளும் அவசியமாகும்."
        ],
        "health_precautions_en": [
            "Vulnerability to renal imbalances, urinary tract irritation, and groin area heat.",
            "Adequate hydration and periodic reproductive health monitoring are advised."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (அஷ்டம ஸ்தானம் & மறைமுக ஞானம்)",
        "house_title_en": "8th House - Ayur Bhava (Longevity, Legacies & Occult Secrets)",
        "core_traits_ta": [
            "ஆழமான மறைபொருள் ஞானம், ஆன்மீக ரகசியங்களை ஆராயும் ஆர்வம் மற்றும் கூரிய உள்ளுணர்வு கொண்டவர்.",
            "வாழ்க்கையில் திடீர் திருப்பங்களையும், எதிர்பாராத அதிர்ஷ்டங்களையும் அல்லது திடீர் சரிவுகளையும் சந்திப்பார்.",
            "தன்னம்பிக்கை குறையாமல் நெருக்கடிகளில் சாதிக்கும் மன உறுதி; தன் பலவீனங்களை வெளிக்காட்டாதவர்.",
            "அரசாங்க வழியிலோ அல்லது வரி விவகாரங்களிலோ எச்சரிக்கையுடன் இருக்க வேண்டும்."
        ],
        "core_traits_en": [
            "Deep fascination with esoteric mysteries, research, astrology, and the metaphysics of life and death.",
            "Experiences dramatic life fluctuations, sudden windfalls, or sudden structural crises.",
            "Maintains a stoic, secretive composure during turbulent storms; masks emotional vulnerabilities.",
            "Must maintain strict compliance in taxation and governmental statutory matters."
        ],
        "strong_placement_ta": [
            "சுப பலம் பெற்றால்: நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள், காப்பீடு அல்லது மனைவி வழியில் தன வரவு.",
            "அஷ்டம சனியின் தாக்கத்தைக் குறைத்து ஆன்மீக முக்தி நிலையை நோக்கிப் பயணிக்கும் ஆற்றல்."
        ],
        "strong_placement_en": [
            "Well-placed or strong: Grants long life, handsome insurance or legacy inheritances, and spousal dowry benefits.",
            "Endows deep occult mastery and ability to survive critical physical perils."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப தொடர்புகள் இருப்பின்: கண் பார்வைக் குறைபாடு, திடீர் விபத்துகள் அல்லது அரசாங்க அபராதங்கள்.",
            "தந்தைக்கு அற்பாயுள் அல்லது தந்தையுடன் நீண்ட காலப் பிரிவு ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Afflicted or debilitated: Impaired eyesight, head injuries, government tax penalties, or sudden disgrace.",
            "Paternal health complications or early estrangement from the father."
        ],
        "career_wealth_ta": [
            "புலனாய்வுத் துறை, தொல்பொருள் ஆராய்ச்சி, தடயவியல், சுரங்கத் தொழில், ஆயுள் காப்பீடு மற்றும் மெட்டபாலிசம் சார்ந்த மருத்துவம்.",
            "மறைமுக சொத்துகள் மற்றும் திடீர் நிதி ஒதுக்கீடுகள் மூலம் பண வரவு."
        ],
        "career_wealth_en": [
            "Thrives in forensic investigation, archaeology, petroleum/mining exploration, life insurance, and toxicology.",
            "Gains wealth through settlement claims, legacies, and hidden financial assets."
        ],
        "health_precautions_ta": [
            "தலைக் காயம், இருதய பலவீனம், கண் புரை அல்லது அதிக உஷ்ணக் கட்டிகள் வரலாம்.",
            "வாகனம் ஓட்டும்போது அதிக கவனம் தேவை; கண்களைப் பரிசோதித்துக் கொள்ளவும்."
        ],
        "health_precautions_en": [
            "Prone to sudden head trauma, high febrile attacks, chronic eye defects, and cardiovascular strain.",
            "Cautious driving habits and preventive ocular care are recommended."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்மம், தந்தை & குரு அருள்)",
        "house_title_en": "9th House - Bhagya Bhava (Fortune, Father, Dharma & Grace)",
        "core_traits_ta": [
            "உயரிய தர்ம சிந்தனை, நேர்மை, தெய்வ பக்தி மற்றும் பெரியோர்களை மதிக்கும் உன்னத சுபாவம்.",
            "தந்தையின் மீது அளப்பரிய மரியாதையும் அவர் வழியில் நற்பெயரைக் காக்கும் கடமையும் கொண்டவர்.",
            "ஆன்மீகத் திருத்தலப் பயணங்கள், தர்ம காரியங்கள் செய்வதில் பேரானந்தம் அடைவார்.",
            "சமுதாயத்தில் மதிப்பிற்குரிய வழிகாட்டியாகவும் ஆசானாகவும் விளங்குவார்."
        ],
        "core_traits_en": [
            "High philosophical nobility, pious disposition, unwavering ethics, and deep reverence for preceptors.",
            "Holds paternal heritage in high esteem and strives to preserve family ancestral honors.",
            "Fond of sacred pilgrimages, charitable endowments, and exploring world philosophies.",
            "Naturally rises as an esteemed moral counselor and inspiring guide in society."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பரம்பரைச் செல்வம், தந்தை நீண்ட ஆயுளுடன் உயர் பதவியில் இருத்தல், அளப்பரிய பாக்கியம்.",
            "அரசு விருதுகள், ஆன்மீக பீடாதிபதிகளின் ஆசி மற்றும் வாழ்நாள் முழுவதும் குறைவற்ற செல்வம்."
        ],
        "strong_placement_en": [
            "Exalted or own house: Bestows radiant fortune, noble and long-lived father, and royal dignities.",
            "Blessings from spiritual gurus, government honors, and perpetual financial grace."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப தாக்கங்கள் இருப்பின்: தந்தையின் உடல்நலம் பாதித்தல், தந்தையுடன் கருத்து வேறுபாடுகள்.",
            "முன்னோர்களின் புண்ணியம் குறைந்து தர்ம காரியங்களில் தடைகளும் அவப்பெயரும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health reversals, ideological clashes with father, and religious skepticism.",
            "Obstacles in higher studies and potential disappointment in legal or spiritual proceedings."
        ],
        "career_wealth_ta": [
            "நீதிபதி, வழக்கறிஞர், அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், சர்வதேசத் தூதர் மற்றும் ஆன்மீக விரிவுரையாளர்.",
            "தர்ம வழியில் சேர்க்கும் நிலையான சொத்துகள் மற்றும் வெளிநாட்டு தொடர்புகளால் ஆதாயம்."
        ],
        "career_wealth_en": [
            "Distinguished success as magistrate, legal luminary, university dean, religious trustee, or diplomat.",
            "Builds honorable wealth through ethical enterprises, foundations, and cross-border projects."
        ],
        "health_precautions_ta": [
            "தொடைப் பகுதியில் வலி, இடுப்பு நரம்புத் தளர்ச்சி (Sciatica) மற்றும் கல்லீரல் உஷ்ணம் ஏற்படலாம்.",
            "நடைப்பயிற்சியும், முறையான ஆன்மீக விரதங்களும் ஆரோக்கியத்திற்குப் பலம் சேர்க்கும்."
        ],
        "health_precautions_en": [
            "Prone to femoral fatigue, sciatica nerve sensitivity, and hepatic heat.",
            "Regular stretching, walking regimens, and sattvic diet optimize vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (திக்பலம் / அரசு அதிகாரம் & கீர்த்தி)",
        "house_title_en": "10th House - Karma Bhava (Digbala / Supreme Career, Power & Fame)",
        "core_traits_ta": [
            "சூரியன் 10-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று அமர்வது மாபெரும் ராஜயோக அமைப்பாகும்.",
            "அரசு அதிகாரம், தலைமை ஆளுமை, கம்பீரம் மற்றும் ஆயிரக்கணக்கான மக்களை வழிநடத்தும் திறன்.",
            "தொழிலில் அசைக்க முடியாத தன்னம்பிக்கை; தோல்விகளை வெற்றிகளாக மாற்றும் துணிவு.",
            "கீர்த்தி, புகழ் மற்றும் சமுதாயத்தின் உச்சாணிக் கொம்பில் அமரும் உயர்நிலை."
        ],
        "core_traits_en": [
            "Sun attains absolute Digbala (directional strength) in the 10th house, generating a supreme Raja Yoga.",
            "Natural commanding authority, visionary administrative genius, and effortless executive leadership.",
            "Unyielding confidence in professional pursuits; turns adversity into triumph.",
            "Garlands the native with widespread fame, royal favors, and premier public stature."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்று திக்பலத்துடன் திகழின்: நாட்டின் மிக உயர்ந்த ஆட்சிப் பதவிகள், ஐ.ஏ.எஸ்/ஐ.பி.எஸ் அல்லது கேபினட் அந்தஸ்து.",
            "தொழிலில் மாபெரும் சாம்ராஜ்யம் அமைத்து சரித்திரத்தில் இடம்பிடிக்கும் சாதனையாளராகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted or in own sign with Digbala: Crown administrative posts, ministerial positions, or top corporate chairmanships.",
            "Builds a monumental professional empire and earns enduring historical acclaim."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உயர் அதிகாரிகளால் வீண் தொல்லைகள், உத்தியோகத்தில் திடீர் இடமாற்றம்.",
            "அரசியல் பகைகளும் பொது வாழ்வில் நற்பெயருக்கு களங்கமும் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or heavily afflicted: Sudden political fall, conflict with government regulators, and professional demotion.",
            "Public scandals and hurdles in career advancement despite high intellectual capacity."
        ],
        "career_wealth_ta": [
            "அரசாங்கத் தலைமைப் பதவிகள், நீதித்துறைத் தலைமை, அரசியல் தலைவர்கள், பெருநிறுவன மேலாண்மை இயக்குநர்கள்.",
            "அதிகார பலத்தாலும் தொழில் மேன்மையாலும் அள்ள அள்ளக் குறையாத தன வரவும் அரச மரியாதையும்."
        ],
        "career_wealth_en": [
            "Prime minister/cabinet ranks, supreme judiciary, CEO/managing directors of conglomerates, defense chiefs.",
            "Vast financial empire generated directly from authoritative executive command."
        ],
        "health_precautions_ta": [
            "அதிக பணிச்சுமையால் ரத்த அழுத்தம், தூக்கமின்மை, மூட்டு வலி மற்றும் உஷ்ணக் கோளாறுகள்.",
            "தவறாமல் ஓய்வெடுத்தலும் தியானமும் உடல் சமநிலையைக் காக்கும்."
        ],
        "health_precautions_en": [
            "Occupational stress, hypertension, insomnia, knee strain, and metabolic heat.",
            "Daily meditation and mandatory work-life balance boundaries are essential."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் & உயர் நட்பு)",
        "house_title_en": "11th House - Labha Bhava (Abundant Gains & Influential Network)",
        "core_traits_ta": [
            "எண்ணிய எண்ணங்கள் யாவும் நிறைவேறும் அதிர்ஷ்டம்; உபசய ஸ்தானத்தில் சூரியன் அமர்வது பெரும் தன லாபத்தைத் தரும்.",
            "செல்வாக்கு மிக்க மனிதர்கள், அரசியல் பிரமுகர்கள் மற்றும் அரசாங்க உயர் அதிகாரிகளின் நட்பு கிட்டும்.",
            "தன்னம்பிக்கை, நேர்மை மற்றும் சுதந்திரமான உழைப்பால் செல்வத்தைச் சேர்க்கும் ஆர்வம்.",
            "மூத்த சகோதரர்களிடம் அன்பும் அதே சமயம் சில கருத்து வேறுபாடுகளும் ஏற்படலாம்."
        ],
        "core_traits_en": [
            "Fulfillment of cherished long-term aspirations; Sun in the 11th is a classic guarantor of steady financial growth.",
            "Builds an elite network with statesmen, industry titans, and influential administrative leaders.",
            "Self-made magnate who cherishes financial autonomy and upright business ethics.",
            "Affectionate yet independently minded relationship with elder siblings."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பல வழிகளிலிருந்து கோடிக் கணக்கில் வருமானம், அசைக்க முடியாத செல்வச் செழிப்பு.",
            "சமூகத்தில் பெரும் கௌரவப் பதவிகள், வாகனங்கள் மற்றும் ஆடம்பர வாழ்க்கை வசதிகள் அமையும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows immense multi-channel revenue streams, monumental liquid wealth, and luxury assets.",
            "Appointed to prestigious public boards and celebrated for grand philanthropic benevolence."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்படுதல், எதிர்பார்க்கும் லாபத்தில் காலதாமதம்.",
            "மூத்த சகோதரருடன் சொத்து தகராறுகள் அல்லது பிரிவுகள் ஏற்படக்கூடும்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by unreliable associates, delayed business receivables, and fiscal bottlenecks.",
            "Estrangement or legal disputes with elder siblings over ancestral partitions."
        ],
        "career_wealth_ta": [
            "பெரு நிறுவன வர்த்தகம், நிதி ஆலோசகர், அரசாங்க ஒப்பந்தங்கள், பொது நிறுவனப் பங்குகள் மற்றும் ரியல் எஸ்டேட்.",
            "குறைந்த முதலீட்டில் பெரும் லாபம் ஈட்டும் வர்த்தகச் சாதுரியம்."
        ],
        "career_wealth_en": [
            "Thrives in venture capitalism, state procurement contracts, corporate finance, equity markets, and industrial scaling.",
            "Exceptional skill in multiplying capital through high-level social leverage."
        ],
        "health_precautions_ta": [
            "இடது காது கேளாமை அல்லது வலி, கணுக்கால் வலி, ரத்த ஓட்டக் குறைபாடுகள் வரலாம்.",
            "கால் தசைகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியமும் முக்கியம்."
        ],
        "health_precautions_en": [
            "Vulnerable to left-ear infections, ankle sprains, and sluggish peripheral blood circulation.",
            "Calf stretching and routine otic checkups are beneficial."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்சம், வெளிநாட்டு வாழ்க்கை & ஆன்மீகம்)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Liberation, Foreign Lands & Expenses)",
        "core_traits_ta": [
            "தனிமையை விரும்பும் அமைதியான சுபாவம்; உலக மாயைகளிலிருந்து விடுபடும் ஆன்மீக நாட்டம்.",
            "பிறந்த ஊரை விட்டுத் தொலைதூரத்திலோ அல்லது வெளிநாடுகளிலோ வாழ்வதில் அனுகூலம்.",
            "பணத்தை தர்ம காரியங்களுக்கும் ஆன்மீக திருப்பணிகளுக்கும் தாராளமாகச் செலவிடும் மனப்பான்மை.",
            "அரசாங்க விவகாரங்களில் அல்லது அதிகாரிகளிடம் பேசும்போது அடக்கத்தைக் கடைப்பிடிப்பது நல்லது."
        ],
        "core_traits_en": [
            "Introspective temperament, loves solitude, and harbors an instinctive yearning for spiritual transcendence.",
            "Remarkable prosperity and peaceful life when settled far away from birthplace or in foreign lands.",
            "Spends generously on noble charities, temple construction, and philosophical institutions.",
            "Must practice diplomatic restraint to avoid confrontations with governmental authorities."
        ],
        "strong_placement_ta": [
            "சுப தொடர்புகளுடன் இருப்பின்: வெளிநாட்டில் மாபெரும் அரசு கௌரவம், பன்னாட்டு நிறுவனங்களில் உயர் பதவி மற்றும் மோட்ச சாதனை.",
            "சுயமரியாதையுடன் கூடிய அமைதியான வாழ்க்கை மற்றும் ஆன்மீக முதிர்ச்சி."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: High diplomatic standing abroad, executive tenure in multinational agencies, and spiritual enlightenment.",
            "Attains tranquil detachment and honorable status in far-flung territories."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: விரயச் செலவுகள், தந்தைக்கு நஷ்டம், கண் பார்வைக் குறைபாடு.",
            "அரசாங்க அபராதங்கள், வழக்குகளால் நிம்மதியின்மை அல்லது தூக்கமின்மை ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Excessive expenditure, financial drains on behalf of father, and defective left eye.",
            "Susceptible to penalties from tax authorities, confinement, or persistent sleep disorders."
        ],
        "career_wealth_ta": [
            "தூதரகப் பணிகள், வெளிநாட்டு வர்த்தகம், கப்பல் போக்குவரத்து, மருத்துவமனை நிர்வாகம், ஆன்மீக மடாலயங்கள்.",
            "அந்நிய தேசத்து கரன்சி மூலம் வருவாய் பெருகுதல்."
        ],
        "career_wealth_en": [
            "Flourishes in diplomatic consulates, international shipping, sanatorium/hospital administration, and spiritual retreats.",
            "Financial inflow derived predominantly from foreign currencies and distant shores."
        ],
        "health_precautions_ta": [
            "இடது கண் பாதிப்பு, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் உடல் சோர்வு.",
            "தூங்குவதற்கு முன் தியானம் செய்தலும் கண்களைக் குளிர்ந்த நீரால் கழுவுவதும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Left eye sensitivities, foot ailments, chronic sleeplessness, and general physical exhaustion.",
            "Nightly grounding meditation, eye relaxation, and consistent sleep hygiene are indicated."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

MOON_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (மனோ பாவம் / காந்தக் கவர்ச்சி)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Mind & Magnetic Charm)",
        "core_traits_ta": [
            "வசீகரமான தோற்றம், மென்மையான கண்கள் மற்றும் அனைவரையும் ஈர்க்கும் காந்தக் கவர்ச்சி உடையவர்.",
            "கற்பனைத் திறன், உணர்ச்சிப் பெருக்கு மற்றும் கவிதை/கலைகளில் ஆழ்ந்த ஈடுபாடு கொண்டவர்.",
            "மனநிலை அடிக்கடி மாறும் சுபாவம்; சந்திரனின் வளர்-தேய் நிலைகளைப் போல எண்ணங்களில் ஏற்ற இறக்கங்கள் இருக்கும்.",
            "பயணங்களை மிகவும் விரும்புவார்; புதிய இடங்களையும் மனிதர்களையும் சந்திப்பதில் அலாதி பிரியம்.",
            "மக்கள் செல்வாக்கு எளிதில் கிட்டும்; பொதுவாழ்வில் பெரும் ஆதரவு பெறுவார்."
        ],
        "core_traits_en": [
            "Charming physical appearance, soft luminous eyes, and an instinctively magnetic aura.",
            "High poetic imagination, artistic sensitivity, romantic idealism, and emotional depth.",
            "Fluctuating mental temperament echoing lunar waxing and waning cycles; prone to mood shifts.",
            "Passionate traveler and explorer, thriving on variety and social change.",
            "Commands widespread popularity and connects effortlessly with the masses."
        ],
        "strong_placement_ta": [
            "ரிஷபத்தில் உச்சம் அல்லது கடகத்தில் ஆட்சி பெற்று வளர்பிறை சந்திரனாக இருப்பின்: நீண்ட ஆயுள், அரச போக வாழ்க்கை மற்றும் அசைக்க முடியாத மக்கள் செல்வாக்கு.",
            "குருவின் சேர்க்கை (கஜகேசரி யோகம்) பெற்றால்: அறிவுக் களஞ்சியமாகவும், செல்வந்தராகவும் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Exalted in Taurus, in own sign Cancer, or Full Waxing Moon: Confers aristocratic lifestyle, immense public acclaim, and serene longevity.",
            "In Gajakesari Yoga with Jupiter: Becomes a renowned intellectual luminary and wealthy community leader."
        ],
        "weak_placement_ta": [
            "விருச்சிகத்தில் நீசம் அல்லது தேய்பிறைச் சந்திரன், ராகு/சனியின் சேர்க்கை பெற்றால்: மன உளைச்சல், அதீத பயம், நரம்புத் தளர்ச்சி மற்றும் சளித் தொல்லைகள்.",
            "முடிவெடுக்க முடியாமல் தடுமாறுதல் மற்றும் பிறர் சொல்லைக் கேட்டு குழம்புதல்."
        ],
        "weak_placement_en": [
            "Debilitated in Scorpio, waning, or conjunct Saturn/Rahu: Chronic anxiety, melancholia, phobias, and emotional volatility.",
            "Difficulty in firm decision-making; highly susceptible to external mental manipulation."
        ],
        "career_wealth_ta": [
            "பொதுமக்கள் தொடர்பு, திரவப் பொருட்கள், பால் பண்ணை, ஹோட்டல் துறை, நாவலாசிரியர், சினிமா மற்றும் கலைத் துறை.",
            "மக்கள் ஆதரவாலும் வர்த்தகப் பயணங்களாலும் நிலையான தன வரவு."
        ],
        "career_wealth_en": [
            "Success in public relations, maritime trade, hospitality, culinary arts, cinema, literature, and luxury retail.",
            "Accumulates wealth through popular mass appeal and consumer-facing enterprises."
        ],
        "health_precautions_ta": [
            "கபக் கோளாறுகள், ஜலதோஷம், ஆஸ்துமா, ஜீரணக் குறைபாடு மற்றும் பெண்களுக்கு மாதவிடாய் கோளாறுகள் வரலாம்.",
            "குளிர்ந்த உணவுகளையும் பனி பொழிவையும் தவிர்ப்பது நல்லது."
        ],
        "health_precautions_en": [
            "Prone to phlegmatic chills, respiratory sensitivity, water-retention, and menstrual irregularities in women.",
            "Avoid chilled foods, damp environments, and maintain respiratory warmth."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (இனிமையான வாக்கு & தனம்)",
        "house_title_en": "2nd House - Dhana Bhava (Sweet Eloquence & Prosperity)",
        "core_traits_ta": [
            "இனிமையான, கனிவான மற்றும் அனைவரையும் வசீகரிக்கும் பேச்சாற்றல் கொண்டவர்.",
            "பெரிய குடும்பம், விருந்தோம்பல் குணம் மற்றும் உறவினர்களை அரவணைத்துச் செல்லும் சுபாவம்.",
            "அழகான முகம், வசீகரமான புன்னகை மற்றும் ஒளிமயமான கண்கள் அமைந்திருக்கும்.",
            "கலைகள், சுவையான உணவுகள் மற்றும் ஆடை ஆபரணங்களின் மீது பேரார்வம் உடையவர்."
        ],
        "core_traits_en": [
            "Possesses a sweet, persuasive, and melodious voice; speaks with comforting kindness.",
            "Enjoys a large, supportive family and delights in gracious domestic hospitality.",
            "Blessed with a pleasant, handsome facial countenance and captivating eyes.",
            "Has refined taste in culinary delicacies, exquisite attire, and aesthetic gems."
        ],
        "strong_placement_ta": [
            "வளர்பிறை சந்திரன் ஆட்சி அல்லது உச்சம் பெற்றால்: பரம்பரை சொத்துகள், நவரத்தினங்கள், வெள்ளி மற்றும் வங்கி சேமிப்புகள் நிரம்பி வழியும்.",
            "வாக்கு பலிதம் உண்டாகும்; இவரது சொல்லுக்கு குடும்பத்திலும் சமுதாயத்திலும் தனி மதிப்பு இருக்கும்."
        ],
        "strong_placement_en": [
            "Waxing Moon in exaltation or own house: Vast liquid wealth, silver, pearls, heirloom jewellery, and substantial bank deposits.",
            "Words carry prophetic authority and persuasive sway in public and family deliberations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் பெற்றால்: பேச்சில் குழப்பம், குடும்பத்தில் மனஸ்தாபங்கள் மற்றும் பண விரயங்கள்.",
            "வலது கண்ணில் பார்வைக் குறைபாடு அல்லது பல் வலிகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Financial instability, domestic discord, and speech stammer or hesitations.",
            "Prone to right-eye vision impairments and dental sensitivities."
        ],
        "career_wealth_ta": [
            "வங்கி, நிதி நிறுவனம், உணவு மற்றும் பேக்கரி தொழில், நவரத்தின வர்த்தகம், பாடகர், பேச்சாளர் மற்றும் இசைக்கலைஞர்.",
            "சுமுகமான பேச்சாலும் மக்கள் ஆதரவாலும் பெரும் தன லாபம்."
        ],
        "career_wealth_en": [
            "Thrives in banking, culinary entrepreneurship, pearl/gem trading, professional singing, and voiceover arts.",
            "Attracts steady income through charming customer engagement and financial services."
        ],
        "health_precautions_ta": [
            "தொண்டை சளி, டான்சில்ஸ், பல் சொத்தை, முகம் மற்றும் கண்ணில் உஷ்ணக் கட்டிகள் வரலாம்.",
            "வெதுவெதுப்பான நீர் அருந்துதலும் தொண்டை பராமரிப்பும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to tonsillitis, oral inflammation, dental caries, and right-eye strain.",
            "Warm fluids and regular dental hygiene are strongly encouraged."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 99) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (கலைத் திறன் & சகோதர நலம்)",
        "house_title_en": "3rd House - Sahaja Bhava (Artistic Flair & Sibling Harmony)",
        "core_traits_ta": [
            "மென்மையான உள்ளமும், கலை ஆர்வமும், சிறந்த எழுத்து மற்றும் தகவல் தொடர்புத் திறனும் உடையவர்.",
            "சகோதர சகோதரிகளிடம் அதிக பாசம் வைத்திருப்பார்; குறிப்பாக பெண் சகோதரிகளால் நன்மை உண்டு.",
            "பயணங்களை மிகவும் விரும்புவார்; அடிக்கடி குறுகிய தூரப் பயணங்கள் மேற்கொள்வார்.",
            "மனதில் தைரியம் இருந்தாலும் சில நேரங்களில் அவசியமற்ற சந்தேகங்களும் தயக்கங்களும் வரலாம்."
        ],
        "core_traits_en": [
            "Artistic mindset, highly talented in creative writing, fine arts, and communicative diplomacy.",
            "Affectionate bond with siblings, with special assistance and goodwill from sisters.",
            "Fond of frequent, picturesque short travels, outings, and changing environments.",
            "Courageous yet emotionally sensitive; occasionally prone to hesitations or mild vacillation."
        ],
        "strong_placement_ta": [
            "வளர்பிறை அல்லது சுப கிரக சேர்க்கை பெற்றால்: கலைத் துறையில் சர்வதேசப் புகழ், சிறந்த எழுத்தாளராக வலம் வருதல், சகோதரர்களால் பெரும் ஆதரவு.",
            "எடுத்த முயற்சிகள் யாவும் சுமுகமாக நிறைவேறி சமுதாயத்தில் நற்பெயர் கிட்டும்."
        ],
        "strong_placement_en": [
            "Strong waxing Moon: International acclaim in literary and performing arts, supportive siblings, and triumphant initiatives.",
            "Attains great social esteem and honors through elegant diplomacy."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப பார்வை பெற்றால்: சகோதரர்களுடன் மனக்கசப்புகள், கைகளில் வலி, பயணங்களால் வீண் அலைச்சல்.",
            "தைரியக் குறைபாடும் காரணமற்ற அச்சமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
        ],
        "weak_placement_en": [
            "Afflicted or debilitated: Estrangement from siblings, fatigue from fruitless journeys, and upper limb pain.",
            "Lack of inner resolve and unnecessary anxious timidity hampering bold initiatives."
        ],
        "career_wealth_ta": [
            "பத்திரிகைத் துறை, நாவல் மற்றும் கதை எழுதுதல், விளம்பரத் துறை, பயண ஏஜென்சி, தொலைத்தொடர்பு மற்றும் இசை.",
            "எழுத்தாற்றலாலும் புதிய சிந்தனைகளாலும் தன வரவு பெருகும்."
        ],
        "career_wealth_en": [
            "Flourishes in journalism, screenplay writing, travel agency operations, telecommunications, and digital media.",
            "Gains wealth through intellectual and creative expressions."
        ],
        "health_precautions_ta": [
            "கைகளில் நரம்பு வலி, தோள்பட்டை இறுக்கம், காதுகளில் நீர் வடிதல் அல்லது ஜலதோஷம் வரலாம்.",
            "குளிர்காலத்தில் காது மற்றும் தொண்டையை மூடிப் பாதுகாப்பது நல்லது."
        ],
        "health_precautions_en": [
            "Prone to shoulder strain, ear fluid imbalances, and recurring colds.",
            "Keep chest and throat protected during cold weather spells."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - மாத்ரு & சுக பாவம் (தாயன்பு, சொத்து & மன அமைதி)",
        "house_title_en": "4th House - Matru & Sukha Bhava (Mother, Comforts & Serenity)",
        "core_traits_ta": [
            "தாயாரின் மீது அளப்பரிய அன்பும், தாயாரின் ஆசியால் வாழ்வில் சகல சௌபாக்கியங்களும் பெறுபவர்.",
            "அமைதியான இல்லற வாழ்க்கை, நற்பண்புகள், தாராள மனப்பான்மை மற்றும் இரக்க சுபாவம் கொண்டவர்.",
            "நீர்நிலைகள், தோட்டங்கள், பசுமையான இடங்கள் மற்றும் ஆடம்பர வீடுகளில் வசிப்பதில் விருப்பம்.",
            "உணர்ச்சிவசப்படும் சுபாவம் கொண்டிருப்பதால் மன நிம்மதிக்கு அதிக முக்கியத்துவம் கொடுப்பார்."
        ],
        "core_traits_en": [
            "Deep filial devotion to mother; receives bountiful maternal blessings and emotional nurturing.",
            "Gracious host, generous philanthropist, and seeks harmonious, aesthetic home sanctuaries.",
            "Loves waterbodies, lush gardens, scenic retreats, and luxurious residential spaces.",
            "Emotionally attuned; prioritizes peace of mind above raw worldly aggression."
        ],
        "strong_placement_ta": [
            "சந்திரன் கடகத்தில் ஆட்சி அல்லது ரிஷபத்தில் உச்சம் பெற்றால்: மாளிகைகள் போன்ற வீடு, சொகுசு வாகனங்கள், தாயார் நீண்ட ஆயுளுடன் இருத்தல்.",
            "மனதில் பூரண அமைதியும், சமுதாயத்தில் உயரிய மதிப்பும் பெற்று சுகவாழ்வு வாழ்வார்."
        ],
        "strong_placement_en": [
            "In Cancer or Taurus: Bestows stately palatial mansions, premium vehicular fleet, and long-lived, noble mother.",
            "Enjoys unperturbed emotional tranquility, refined comforts, and civic honors."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக்குறைவு, பூர்வீக சொத்துகளில் இழப்பு, வீட்டு சூழலில் அமைதியின்மை.",
            "நெஞ்சு சளி, மன உளைச்சல் மற்றும் அடிக்கடி வீட்டை மாற்ற வேண்டிய கட்டாயம் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Fragile health of mother, property disputes, and emotional unhappiness at home.",
            "Susceptible to chest congestion, acute melancholy, and frequent changes of residence."
        ],
        "career_wealth_ta": [
            "ரியல் எஸ்டேட், பால் மற்றும் நீர்வழி வர்த்தகம், விவசாயப் பண்ணைகள், உளவியல் ஆலோசனை மற்றும் வாகனத் தொழில்.",
            "தாய்வழிச் சொத்துகளாலும் வீட்டுமனை வர்த்தகத்தாலும் தன வரவு கொழிக்கும்."
        ],
        "career_wealth_en": [
            "Profitable avenues in residential architecture, dairy agriculture, marine logistics, psychology, and luxury hospitality.",
            "Inherits substantial maternal properties and realizes rapid appreciation on real estate."
        ],
        "health_precautions_ta": [
            "நெஞ்சு சளி, நுரையீரல் அலர்ஜி, இருமல் மற்றும் தூக்கமின்மை வரலாம்.",
            "இரவில் அதிக நேரம் விழித்திருப்பதைத் தவிர்த்து ஆழ்ந்த தூக்கம் கொள்வது நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Prone to pulmonary congestion, bronchial allergies, and water retention around heart.",
            "Ensure restful sleep patterns and avoid cold nighttime drafts."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 174) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கற்பனை வளம் & பூர்வ புண்ணியம்)",
        "house_title_en": "5th House - Putra Bhava (Creativity, Progeny & Devotion)",
        "core_traits_ta": [
            "அசாத்தியமான கற்பனை வளம், கவிதை எழுதும் ஆற்றல், கூர்மையான நினைவாற்றல் மற்றும் கலை உணர்வு.",
            "குழந்தைகளிடம் பேரன்பு செலுத்துவார்; நற்குணமும் அழகும் நிறைந்த பெண் குழந்தைகள் அமைய வாய்ப்புண்டு.",
            "தெய்வ பக்தி, தியானம் மற்றும் சாத்வீக வழிபாடுகளில் அதிக ஈடுபாடு காட்டுவார்.",
            "மனதில் தூய்மையான எண்ணங்களும், பிறருக்கு நலம் பயக்கும் ஆலோசனைகளை வழங்கும் பண்பும் உண்டு."
        ],
        "core_traits_en": [
            "Profound creative genius, poetic eloquence, stellar intuitive memory, and aesthetic flair.",
            "Deep affection for children; often blessed with charming, accomplished daughters.",
            "Pious devotional heart, drawn to meditation, mantra sadhana, and sattvic temple worship.",
            "Pure-hearted counselor whose instinctive advice brings healing and solace to others."
        ],
        "strong_placement_ta": [
            "பூர்ண சந்திரன் சுப தொடர்புடன் இருப்பின்: அறிவார்ந்த சந்ததிகள், கலை மற்றும் இலக்கியத்தில் விருதுகள், அரச யோகம்.",
            "பூர்வ புண்ணிய பலத்தால் தொட்டதெல்லாம் பொன்னாகும் யோகமும், திடீர் தன லாபங்களும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Bright waxing Moon: Celebrated, virtuous children, national honors in arts or literature, and royal fortune.",
            "Reaps past-life blessings through effortless creative triumphs and sudden speculative prosperity."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கவலைகள், குழந்தைகளின் உடல்நலம் பாதித்தல்.",
            "பங்குச் சந்தை அல்லது ஊக வணிகத்தில் உணர்ச்சிவசப்பட்டு முதலீடு செய்து நஷ்டமடைதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Emotional distress regarding children, erratic schooling for progeny.",
            "Financial setbacks through emotional, ill-calculated investments in speculative markets."
        ],
        "career_wealth_ta": [
            "சினிமா இயக்குநர், இசை அமைப்பாளர், எழுத்தாளர், கல்வியாளர், குழந்தைகள் நல மருத்துவர் மற்றும் பங்கு ஆலோசகர்.",
            "கலை படைப்புகள், அறிவுசார் சொத்துரிமை மற்றும் ஆலோசனைகள் மூலம் அபரிமிதமான செல்வம்."
        ],
        "career_wealth_en": [
            "Distinction as film director, composer, literary novelist, child educator, pediatrician, or financial analyst.",
            "Generates wealth through intellectual property, creative royalties, and intuitive advisory."
        ],
        "health_precautions_ta": [
            "செரிமானக் கோளாறுகள், வயிற்றுப் பகுதியில் நீர் கட்டிகள், பித்த நீர் சமநிலையின்மை வரலாம்.",
            "எளிதில் செரிக்கும் சத்தான உணவுகளை வேளைக்கு உண்பது ஆரோக்கியம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to gastric acidity, stomach bloating, lymphatic cysts, and sluggish digestion.",
            "Adopt easily digestible light meals and regular meal timings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - ரோக பாவம் (நோய் எதிர்ப்பு & பணிவு)",
        "house_title_en": "6th House - Satru & Roga Bhava (Health Care & Diligence)",
        "core_traits_ta": [
            "அமைதியான சுபாவம்; வாக்குவாதங்களையும் நேரடி மோதல்களையும் விரும்புவதில்லை.",
            "பிறருக்கு உதவும் தாராள உள்ளமும், சேவை மனப்பான்மையும், அர்ப்பணிப்புடன் உழைக்கும் குணமும் கொண்டவர்.",
            "மனதில் தேவையில்லாத கவலைகளையும், பயங்களையும் வளர்த்துக்கொண்டு அமைதியை இழக்கக்கூடும்.",
            "தாய்மாமன் அல்லது தாய்வழி உறவினர்களுடன் உறவில் சற்று ஏற்ற இறக்கங்கள் இருக்கலாம்."
        ],
        "core_traits_en": [
            "Gentle, conflict-averse temperament; prefers conciliation over aggressive showdowns.",
            "Compassionate humanitarian spirit, dedicated to humble service and patient diligence.",
            "Prone to psychosomatic worries and internal anxieties that affect general vitality.",
            "Experiences fluctuating dynamics with maternal uncles and domestic servants."
        ],
        "strong_placement_ta": [
            "வளர்பிறை சந்திரனாக இருந்து சுப பார்வை பெற்றால்: நோய்களை வெல்லும் மன உறுதி, கடன்கள் இல்லாத அமைதியான வாழ்க்கை.",
            "மருத்துவத் துறையிலும், சேவை நிறுவனங்களிலும் உயர் பதவிகளை வகித்து நற்பெயர் பெறுவார்."
        ],
        "strong_placement_en": [
            "Waxing Moon with benefic aspects: Robust psychological immunity against disease, debt-free living, and reliable staff.",
            "Attains respected executive standing in medical, public health, or charitable service foundations."
        ],
        "weak_placement_ta": [
            "தேய்பிறை சந்திரன் அல்லது நீசமாக இருப்பின்: தீராத சளி, வயிற்றுப் போக்கு, செரிமானக் கோளாறுகள், ரத்த சோகை.",
            "எதிரிகளால் மறைமுகத் தொல்லைகளும், வேலையாட்களால் நஷ்டமும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Waning or debilitated: Chronic bronchial catarrh, dysentery, stomach ulcers, and anemia.",
            "Subtle undermining from covert rivals and financial leakages caused by dishonest subordinates."
        ],
        "career_wealth_ta": [
            "செவிலியர் துறை, பார்மசி, சத்துணவு நிபுணர், ஹோட்டல் உணவு வழங்கல், சமூக சேவை மற்றும் கால்நடை பராமரிப்பு.",
            "உழைப்பிற்கேற்ற நியாயமான ஊதியமும், சேவையின் மூலமான நற்பெயரும் கிட்டும்."
        ],
        "career_wealth_en": [
            "Career fulfillment in nursing, pharmaceuticals, dietetics, catering, welfare agencies, and veterinary care.",
            "Earns stable income through honest, compassionate service to people in distress."
        ],
        "health_precautions_ta": [
            "ஜலதோஷம், நுரையீரல் தொற்று, அஜீரணம் மற்றும் நீர் மூலம் பரவும் நோய்கள் வரலாம்.",
            "காய்ச்சிய சுத்தமான குடிநீரை அருந்துவதும், குளிர்ச்சியான உணவுகளைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to pulmonary phlegm, bowel infections, amoebiasis, and waterborne pathogens.",
            "Drink purified boiled water and avoid refrigerated or uncooked street foods."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (அழகான துணை & பொது ஈர்ப்பு)",
        "house_title_en": "7th House - Kalathra Bhava (Charming Spouse & Public Allure)",
        "core_traits_ta": [
            "அழகான, கனிவான, கவர்ச்சிகரமான குணநலன்கள் கொண்ட வாழ்க்கைத் துணை அமையப் பெறுவார்.",
            "தாம்பத்திய வாழ்வில் ரொமான்ஸ், பரஸ்பர அன்பு மற்றும் பாசம் நிறைந்திருக்கும்.",
            "பொதுமக்கள் தொடர்பில் சிறந்தவர்; வணிக கூட்டாளிகளுடன் சுமுகமாகப் பழகி காரியம் சாதிப்பார்.",
            "அடிக்கடி கடல் கடந்த பயணங்கள் மற்றும் வியாபார நிமித்தமான பயணங்களை மேற்கொள்வார்."
        ],
        "core_traits_en": [
            "Blessed with an attractive, gentle, affectionate, and aesthetically refined spouse.",
            "Enjoys romantic warmth, mutual devotion, and harmonious conjugal bliss.",
            "Natural diplomat in public interactions; builds agreeable, trust-based business alliances.",
            "Fond of overseas voyages, maritime trade, and scenic recreational travels."
        ],
        "strong_placement_ta": [
            "பூர்ண சந்திரன் சுப கிரகங்களுடன் இருப்பின்: அதிர்ஷ்டகரமான செல்வந்த குடும்பத் துணை, திருமணத்திற்குப் பின் அபரிமிதமான வளர்ச்சி.",
            "பன்னாட்டு வர்த்தகத்தில் பெரும் லாபமும், சமூகத்தில் உயர்ந்த தம்பதிகளாகப் போற்றப்படும் நிலையும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Full Moon with benefics: Marries into an affluent, distinguished family; exponential post-marital prosperity.",
            "Reaps huge profits from transnational commerce and enjoys enviable social prestige as an ideal couple."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் இருப்பின்: துணையின் உடல்நலத்தில் அடிக்கடி பாதிப்பு, மனநிலை ஊசலாட்டங்களால் குடும்பத்தில் சலசலப்பு.",
            "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஏமாற்றப்பட்டு இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Emotional fragility or health ailments in spouse, moodiness causing marital tension.",
            "Vulnerable to deceit and capital erosion through untrustworthy business partners."
        ],
        "career_wealth_ta": [
            "சுற்றுலாத் துறை, கப்பல் போக்குவரத்து, இறக்குமதி-ஏற்றுமதி, அழகு சாதனப் பொருட்கள், ஆடை வடிவமைப்பு மற்றும் பொது உறவுகள்.",
            "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் பொதுமக்கள் செல்வாக்கினாலும் தன லாபம் பெருகும்."
        ],
        "career_wealth_en": [
            "High rewards in hospitality, luxury travel, marine logistics, cosmetics, fashion apparel, and public advocacy.",
            "Financial prosperity augmented substantially through marital fortunes and joint assets."
        ],
        "health_precautions_ta": [
            "சிறுநீரகத் தொற்று, அடிவயிறு மற்றும் பிறப்புறுப்புப் பகுதியில் நீர் வீக்கம், உஷ்ணக் கோளாறுகள்.",
            "முறையான நீர் அருந்துதலும் தனிநபர் சுகாதாரமும் நலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to renal congestion, bladder irritations, and pelvic fluid imbalances.",
            "Maintain optimal daily fluid intake and attentive personal hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (உள்ளுணர்வு & மறைபொருள் நாட்டம்)",
        "house_title_en": "8th House - Ayur Bhava (Intuition, Occult Mysteries & Legacies)",
        "core_traits_ta": [
            "அசாத்தியமான உள்ளுணர்வு (Intuition), கனவுகள் பலிக்கும் ஆற்றல் மற்றும் ஆன்மீக ரகசியங்களில் ஈடுபாடு.",
            "மனதில் ஆழமான உணர்ச்சிகளை மறைத்து வைத்திருக்கும் சுபாவம்; எதையும் வெளிப்படையாகப் பேச மாட்டார்.",
            "வாழ்க்கையில் எதிர்பாராத அதிர்ஷ்டங்களும் அல்லது திடீர் மன அழுத்தங்களும் மாறி மாறி வரலாம்.",
            "நீர்நிலைகளில் செல்லும்போது மிகுந்த எச்சரிக்கையுடன் இருக்க வேண்டும்."
        ],
        "core_traits_en": [
            "Extraordinary intuitive perception, vivid prophetic dreams, and fascination with occult mysteries.",
            "Guarded emotional core; conceals profound internal feelings beneath an enigmatic surface.",
            "Encounters sudden financial windfalls alternating with acute psychological transformations.",
            "Must exercise supreme caution around deep waterbodies and aquatic journeys."
        ],
        "strong_placement_ta": [
            "வளர்பிறை அல்லது சுப பார்வை இருப்பின்: நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள், மனைவியின் வழியில் பெரும் தன வரவு.",
            "ஆழ்ந்த ஆன்மீக ஞானமும், மறைமுக சாஸ்திரங்களில் தேர்ச்சியும் பெற்று பிறருக்கு வழிகாட்டுவார்."
        ],
        "strong_placement_en": [
            "Waxing Moon with benefics: Extended longevity, substantial unearned legacies, and prosperous dowry assets.",
            "Attains mystical enlightenment and deep psychological wisdom, guiding seekers."
        ],
        "weak_placement_ta": [
            "தேய்பிறை அல்லது விருச்சிகத்தில் நீசம் பெற்றால்: மன அழுத்தம் (Depression), நீரில் கண்டம், கண் உபாதைகள்.",
            "தாயாரின் ஆயுளுக்கு பலவீனம் அல்லது தாயை விட்டுப் பிரியும் சூழல் உருவாகலாம்."
        ],
        "weak_placement_en": [
            "Waning or debilitated in Scorpio: Acute mental depression, danger of drowning, ocular weakness.",
            "Fragile vitality for the mother or painful early maternal separation."
        ],
        "career_wealth_ta": [
            "மறைமுகப் புலனாய்வு, ஜோதிடம், ஹிப்னாட்டிசம், உளவியல் சிகிச்சை, ஆயுள் காப்பீடு மற்றும் தொல்பொருள் ஆராய்ச்சி.",
            "திடீர் தன லாபங்கள், பங்குச் சந்தை டிவிடெண்டுகள் மற்றும் உயில் சொத்துகள் மூலம் வரவு."
        ],
        "career_wealth_en": [
            "Success in psychoanalysis, astrology, hypnotherapy, insurance settlements, toxicology, and esoteric research.",
            "Financial windfalls from inherited estates, insurance payouts, and strategic private equity."
        ],
        "health_precautions_ta": [
            "மன அழுத்தம், மூளை நரம்பு பலவீனம், நாள்பட்ட சளி, சிறுநீரகக் கோளாறுகள் மற்றும் நீரிழிவு அபாயம்.",
            "தியானம், பிராணாயாமம் மற்றும் மனநல ஆலோசனைகள் புத்துணர்ச்சி தரும்."
        ],
        "health_precautions_en": [
            "Prone to melancholic depressive states, chronic sinus congestion, and endocrine imbalances.",
            "Daily meditation, breathwork, and emotional grounding practices are essential."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்மம், தீர்த்த யாத்திரை & தந்தை)",
        "house_title_en": "9th House - Bhagya Bhava (Fortune, Pilgrimage & Divine Grace)",
        "core_traits_ta": [
            "உன்னதமான தர்ம சிந்தனை, பக்தி, இரக்கம் மற்றும் அனைவராலும் போற்றப்படும் நற்குணங்கள் கொண்டவர்.",
            "புனிதத் தலங்களுக்கு யாத்திரை செல்வதிலும், திருக்குளங்களில் நீராடுவதிலும் அலாதி பிரியம்.",
            "தந்தையின் மீது பாசமும் மரியாதையும் கொண்டவர்; தந்தை வழியில் நன்மைகளும் ஆசிகளும் கிட்டும்.",
            "அதிர்ஷ்டம் நிறைந்த வாழ்வு; இக்கட்டான நேரங்களில் இறைவனின் அருள் கைகொடுத்துக் காப்பாற்றும்."
        ],
        "core_traits_en": [
            "Sublime spiritual piety, deep compassion, ethical uprightness, and universally admired virtues.",
            "Passionate love for pilgrimages to sacred river shrines, holy temples, and spiritual retreats.",
            "Cherishes deep affection for the father; reaps noble paternal heritage and divine blessings.",
            "A genuinely fortunate soul whom serendipitous grace rescues from life's toughest corners."
        ],
        "strong_placement_ta": [
            "பூர்ண சந்திரன் ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட பாக்கிய யோகம், அரசாங்க கௌரவம், வற்றாத செல்வம்.",
            "தர்ம ஸ்தாபனங்களை நிறுவுதல், சமுதாயத்தில் உயர்ந்த ஆன்மீகத் தலைவராகப் போற்றப்படுதல்."
        ],
        "strong_placement_en": [
            "Full Moon in strength: Bestows boundless Bhagya Yoga, supreme civic honors, and perennial wealth.",
            "Founding philanthropic trusts, rising as an inspiring philosophical leader across nations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக் குறைவு, மத நம்பிக்கைகளில் குழப்பம்.",
            "புனிதப் பயணங்களில் பொருள் இழப்பு அல்லது ஏமாற்றங்கள் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health trials, religious disillusionment, and ideological clashes with mentors.",
            "Loss of baggage or financial deceit during sacred pilgrimages."
        ],
        "career_wealth_ta": [
            "ஆன்மீக அறக்கட்டளைகள், பல்கலைக்கழகப் பேராசிரியர்கள், சட்ட ஆலோசகர்கள், சர்வதேச வர்த்தகம் மற்றும் நூலாசிரியர்கள்.",
            "தர்ம வழியில் ஈட்டும் செல்வமும், வெளிநாட்டு முதலீடுகளால் அபரிமிதமான வளர்ச்சியும்."
        ],
        "career_wealth_en": [
            "Thrives in philanthropic foundations, academic deanships, international jurisprudence, and spiritual literature.",
            "Amasses pure, untainted wealth through principled cross-border commerce."
        ],
        "health_precautions_ta": [
            "தொடை மற்றும் இடுப்புப் பகுதியில் நரம்பு வலி, உடல் சோர்வு மற்றும் செரிமானக் கோளாறுகள்.",
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
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (மக்கள் செல்வாக்கு & தொழில் மேன்மை)",
        "house_title_en": "10th House - Karma Bhava (Mass Popularity & Professional Glory)",
        "core_traits_ta": [
            "மக்கள் மத்தியில் அளப்பரிய செல்வாக்கும், நற்பெயரும், உயர்ந்த தொழில் நிலையும் உடையவர்.",
            "எந்தத் துறையிலும் முன்னணியில் நிற்கும் தலைமைப் பண்பும், சுறுசுறுப்பும் கொண்ட செயல்வீரர்.",
            "அரசாங்க ஆதரவு, பொதுமக்களின் ஏகோபித்த அன்பு மற்றும் கௌரவப் பதவிகள் எளிதில் கிட்டும்.",
            "தன் தொழில் மூலம் பல்லாயிரக்கணக்கான மக்களுக்கு வேலைவாய்ப்பும் நன்மையும் செய்வார்."
        ],
        "core_traits_en": [
            "Enormous public acclaim, immaculate professional repute, and elevated occupational stature.",
            "Energetic dynamism, natural flair for leadership, and decisive organizational execution.",
            "Commands governmental patronage, civic adoration, and prestigious chairmanships.",
            "Builds enterprises that provide livelihood and benevolent welfare to hundreds of families."
        ],
        "strong_placement_ta": [
            "பூர்ண சந்திரன் சுப பலத்துடன் இருப்பின்: அமைச்சரவை யோகம், பெருநிறுவனத் தலைவர் அந்தஸ்து, அழியாத புகழ்.",
            "தொழிலில் அசைக்க முடியாத சாம்ராஜ்யத்தை நிறுவி சமூகத்தின் வழிகாட்டியாகத் திகழ்வார்."
        ],
        "strong_placement_en": [
            "Bright Moon with strength: Confers ministerial portfolios, CEO status of mega-corporations, and timeless fame.",
            "Constructs an unshakeable commercial empire and serves as a celebrated icon of industry."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், பொது வாழ்வில் அவப்பெயர்.",
            "உயர் அதிகாரிகளால் நெருக்கடிகளும், வியாபாரத்தில் நிலையற்ற தன்மையும் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Occupational instability, sudden public fall from grace, and emotional burnout.",
            "Frequent erratic job switches and unmerited criticism from civic regulators."
        ],
        "career_wealth_ta": [
            "அரசியல், மக்கள் தொடர்பு, மருத்துவம், ஹோட்டல் மற்றும் சுற்றுலா, கப்பல் போக்குவரத்து, திரவப் பொருட்கள் வர்த்தகம்.",
            "மக்கள் ஆதரவாலும் தொழில் மேன்மையாலும் கோடிக் கணக்கில் செல்வம் சேரும்."
        ],
        "career_wealth_en": [
            "Stellar career in statesmanship, public administration, healthcare, maritime logistics, and hospitality.",
            "Multi-million liquid capital generated via widespread customer trust and civic goodwill."
        ],
        "health_precautions_ta": [
            "மூட்டு வலி, பணிச்சுமையால் தூக்கமின்மை, மன அழுத்தம் மற்றும் கபத் தொல்லைகள்.",
            "வேலைக்கு நடுவே தகுந்த ஓய்வும், தியானப் பயிற்சிகளும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Vulnerable to knee joint stiffness, occupational sleep deprivation, and psychosomatic tension.",
            "Pace work rhythms mindfully and engage in restful evening relaxation rituals."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அனைத்து விருப்பங்களும் நிறைவேறுதல்)",
        "house_title_en": "11th House - Labha Bhava (Abundant Gains & Wish Fulfillment)",
        "core_traits_ta": [
            "தொட்ட காரியங்களில் எல்லாம் லாபம், ஆசைகள் யாவும் நிறைவேறுதல் மற்றும் நிலையான பொருளாதார உயர்வு.",
            "உயர் அந்தஸ்து படைத்த பெண்களின் நட்பும் ஆதரவும் வாழ்வின் உயர்வுக்குப் பெரிதும் உதவும்.",
            "தாராள மனப்பான்மை, விருந்தோம்பல் குணம் மற்றும் சமூகத்தில் பல நண்பர்களைக் கொண்டிருப்பார்.",
            "மூத்த சகோதர சகோதரிகளுடன் அன்பான இணக்கமும் அவர்களால் நன்மைகளும் கிட்டும்."
        ],
        "core_traits_en": [
            "Boundless prosperity, steady streams of revenue, and smooth realization of cherished ambitions.",
            "Enjoys beneficial patronage and enduring friendship from influential, noble women.",
            "Magnanimous, hospitable, and surrounded by a vast network of loyal, supportive associates.",
            "Deeply fulfilling companionship with elder siblings who foster career elevation."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்று பூர்ண சந்திரனாக இருப்பின்: கணக்கிலடங்கா செல்வம், சொகுசு வாகனங்கள், சமூகத்தின் முதன்மை அந்தஸ்து.",
            "பல வழிகளிலிருந்து தொடர் வருமானம் வந்து வங்கி இருப்பு எப்போதும் பெருகிக் கொண்டே இருக்கும்."
        ],
        "strong_placement_en": [
            "Bright Moon in Taurus/Cancer: Tremendous wealth accumulation, fleet of luxury cars, and premier social rank.",
            "Unceasing multi-faceted financial inflows ensuring massive liquidity and asset appreciation."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் பிரிவு.",
            "லாபங்கள் கைக்கு எட்டும் நேரத்தில் நழுவிப் போதல் அல்லது பண விரயங்கள் ஏற்படுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by counterfeit friends, financial leakages, and sibling estrangement.",
            "Anticipated dividends slip away at the last moment due to bad timing or misjudgment."
        ],
        "career_wealth_ta": [
            "நிதி நிறுவனங்கள், பங்குச் சந்தை, ஏற்றுமதி வர்த்தகம், உணவு மற்றும் பானங்கள், ரத்தின வர்த்தகம், சமூக வலைப்பின்னல்கள்.",
            "குறைந்த உழைப்பில் அபரிமிதமான லாபம் ஈட்டும் வணிகத் திறமை."
        ],
        "career_wealth_en": [
            "Lucrative success in fintech, stock brokerage, food commodities, gemstone export, and media platforms.",
            "Exceptional ability to turn ideas into scalable cash cows."
        ],
        "health_precautions_ta": [
            "இடது காது வலி, கணுக்கால் வீக்கம், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் சளித் தொல்லைகள்.",
            "முறையான பாத பராமரிப்பும் உடற்பயிற்சியும் நலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear aches, ankle edema, sluggish lymphatic circulation, and colds.",
            "Leg stretching and keeping ankles warm assist lymphatic drainage."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அமைதி, அயன சயன சுகம் & வெளிநாடு)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Inner Peace, Seclusion & Foreign Lands)",
        "core_traits_ta": [
            "அமைதியான தனிமையை விரும்பும் சுபாவம்; ஆழ்ந்த தூக்கமும் ஆன்மீக சிந்தனைகளும் கொண்டவர்.",
            "பிறந்த மண்ணை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அபரிமிதமான யோகம் பெறுவார்.",
            "ஏழை எளியவர்களுக்கும், மருத்துவமனைகளுக்கும், ஆன்மீக ஸ்தலங்களுக்கும் தாராளமாக வாரி வழங்கும் வள்ளல் தன்மை.",
            "மனதில் சில நேரங்களில் காரணமற்ற தனிமை உணர்வும் விரக்தியும் எட்டிப் பார்க்கக்கூடும்."
        ],
        "core_traits_en": [
            "Loves peaceful seclusion, contemplative solitude, deep sleep, and transcendent spiritual musings.",
            "Achieves peak prosperity and renown when settled far away from natal home or in overseas territories.",
            "Benevolent philanthropist who spends liberally on hospices, ashrams, and humanitarian causes.",
            "May occasionally suffer from subjective loneliness or vague emotional isolation."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் சொத்துகள், அமைதியான இல்லற சுகம், ஆன்மீக முக்தி நிலை.",
            "அயன சயன சுகம் பூரணமாகக் கிட்டும்; மனக் குழப்பங்கள் நீங்கி ஆத்ம சாந்தி அடைவார்."
        ],
        "strong_placement_en": [
            "Strong with benefic aspects: Vast real estate holdings abroad, blissful conjugal rest, and spiritual Moksha.",
            "Enjoys sound restorative sleep, serene mental clarity, and divine tranquility."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தூக்கமின்மை, கண் பார்வைக் குறைபாடு, பண விரயங்கள்.",
            "மனக் கவலைகள், வீண் பயம் மற்றும் மருத்துவச் செலவுகளால் நிம்மதி குறையலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe insomnia, left-eye vision defects, chronic financial drain, and hospital bills.",
            "Haunted by irrational anxieties, nightmares, and heavy domestic expenditure."
        ],
        "career_wealth_ta": [
            "மருத்துவமனை நிர்வாகம், வெளிநாட்டுத் தூதரகம், சர்வதேசக் கப்பல் போக்குவரத்து, ஆன்மீக மடங்கள், உளவியல் காப்பகங்கள்.",
            "வெளிநாட்டு பண வரவாலும் ஆன்மீகப் பணிகளாலும் செல்வம் சேரும்."
        ],
        "career_wealth_en": [
            "High success in hospital administration, international diplomacy, overseas logistics, and meditative retreats.",
            "Income derived extensively in foreign currencies and specialized offshore institutions."
        ],
        "health_precautions_ta": [
            "இடது கண் உபாதை, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் சளித் தொல்லைகள்.",
            "இரவில் படுக்கும் முன் பாதங்களை வெதுவெதுப்பான நீரில் கழுவுதலும் தியானமும் அமைதி தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye strain, foot nerve pain, chronic insomnia, and recurring phlegm.",
            "Warm foot soaks and guided meditation before sleep restore equilibrium."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

MARS_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (வீரம், பராக்கிரமம் & ஆவேசம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Heroic Valor & Fiery Will)",
        "core_traits_ta": [
            "அசாத்தியமான உடல்பலம், அஞ்சாநெஞ்சம், தளராத தைரியம் மற்றும் கம்பீரமான ஆளுமை கொண்டவர்.",
            "முன்கோபமும், எதையும் உடனே செய்து முடிக்க வேண்டும் என்ற அவசரமும், துடிப்பான சுபாவமும் இருக்கும்.",
            "சுயமரியாதைக்குக் களங்கம் விளைவித்தால் ஆவேசமடைவார்; யாருக்கும் தலைவணங்காத சுதந்திரப் போக்கு.",
            "தலை அல்லது முகத்தில் சிறிய தழும்பு அல்லது காயம் இருக்க வாய்ப்புண்டு; உஷ்ண தேகம்.",
            "சவால்களையும் போட்டிகளையும் துணிவுடன் எதிர்கொண்டு வெற்றிகொள்ளும் பேராற்றல்."
        ],
        "core_traits_en": [
            "Tremendous physical vitality, indomitable bravery, iron constitution, and commanding persona.",
            "Quick to flare up with a rash, impetuous temper; eager for immediate action and dynamic breakthroughs.",
            "Fiercely protective of self-respect; scorns defeat and rejects subordination.",
            "Often carries a scar or mark on the forehead or face; hot, pitta-dominated constitution.",
            "Fearless competitor who thrives in high-stakes adversarial contests."
        ],
        "strong_placement_ta": [
            "மேஷம்/விருச்சிகத்தில் ஆட்சி அல்லது மகரத்தில் உச்சம் பெற்று ருசக யோகம் (Ruchaka Yoga) அமைந்தால்: தலைமைத் தளபதி யோகம், போலீஸ்/ராணுவ உயர்பதவி, பரந்த நிலபுலன்கள்.",
            "அசைக்க முடியாத செல்வாக்கு, ஆயிரக்கணக்கான மக்களை வழிநடத்தும் அதிகாரம் மற்றும் வீரப்புகழ்."
        ],
        "strong_placement_en": [
            "Exalted in Capricorn or in own signs Aries/Scorpio forming Ruchaka Mahapurusha Yoga: Supreme military commander, high police chief, vast landed wealth.",
            "Commands invincible influence, monumental administrative muscle, and national honors for bravery."
        ],
        "weak_placement_ta": [
            "கடகத்தில் நீசம் அல்லது ராகு/சனியின் தாக்கம் பெற்றால்: விபத்துகளில் காயங்கள், அவசர முடிவுகளால் நஷ்டம், ரத்தக் கொதிப்பு.",
            "காரணமற்ற சண்டை சச்சரவுகள், பிடிவாதம் மற்றும் திருமண வாழ்வில் குஜ தோஷத்தால் (Kuja Dosha) பாதிப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Cancer or afflicted by Rahu/Saturn: Prone to physical accidents, burns, head trauma, and hypertension.",
            "Reckless anger causes self-destructive disputes; Kuja Dosha sparks marital discords if unchecked."
        ],
        "career_wealth_ta": [
            "ராணுவம், காவல்துறை, அறுவை சிகிச்சை மருத்துவர், ரியல் எஸ்டேட், மெக்கானிக்கல் இன்ஜினியரிங், சுரங்கத் தொழில், தீயணைப்பு.",
            "துணிச்சலான முதலீடுகள், பூமி/நில வர்த்தகம் மற்றும் சொந்தத் தொழில் மூலம் அபரிமிதமான தன லாபம்."
        ],
        "career_wealth_en": [
            "Exemplary career in armed forces, IPS/defense command, trauma surgery, real estate development, mechanical engineering, and mining.",
            "Amasses great fortune through bold capital deployments and landed property acquisition."
        ],
        "health_precautions_ta": [
            "தலையில் காயங்கள், ரத்தக் கொதிப்பு, மூல நோய், உஷ்ணக் கட்டிகள் மற்றும் தீக்காயங்கள் ஏற்பட வாய்ப்புண்டு.",
            "காரமான உணவுகளைக் குறைத்து உடலை குளிர்ச்சியாக வைத்திருப்பதும், நிதானமாக வாகனம் ஓட்டுவதும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to cranial lacerations, hypertension, hemorrhoids, inflammatory boils, and burn hazards.",
            "Adopt cooling diets, avoid explosive temper tantrums, and maintain speed limits on roads."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (கூர்மையான வாக்கு & பூமி லாபம்)",
        "house_title_en": "2nd House - Dhana Bhava (Sharp Speech & Landed Wealth)",
        "core_traits_ta": [
            "வெளிப்படையான, கூர்மையான மற்றும் தயவுதாட்சண்யமற்ற பேச்சாற்றல்; பேச்சில் காரமும் உறுதியும் இருக்கும்.",
            "கடின உழைப்பாலும், விடாமுயற்சியாலும் சொத்துகளைச் சேர்க்கும் தன்னம்பிக்கை உடையவர்.",
            "குடும்பத்தில் சில சமயம் வீண் வாக்குவாதங்கள் வரலாம்; விட்டுக்கொடுத்துச் செல்வது நலம்.",
            "இரும்பு, உலோகம், இயந்திரங்கள் மற்றும் நிலம் தொடர்பான விஷயங்களில் நல்ல ஞானம் இருக்கும்."
        ],
        "core_traits_en": [
            "Blunt, incisive, and unvarnished speech; cuts straight to the core without diplomatic sugarcoating.",
            "Tenacious drive to amass tangible physical properties through hard enterprise.",
            "Prone to sudden domestic arguments within the family circle; requires tactful speech control.",
            "Innate flair for metals, weaponry, heavy machinery, and real estate evaluation."
        ],
        "strong_placement_ta": [
            "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் பலம் பெற்றால்: பல கோடி மதிப்பிலான நிலபுலன்கள், தங்கக் கட்டிகள், அசைக்க முடியாத வங்கி இருப்பு.",
            "பேச்சில் கம்பீரமும் அதிகாரமும் கூடி சமுதாயத்தில் உயர்ந்த அந்தஸ்து கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-million dollar real estate estates, bullion wealth, and robust liquidity.",
            "Voice commands respect and persuasive authority in boardroom negotiations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சினால் குடும்பத்தில் விரிசல், வழக்குகளால் தன விரயம்.",
            "வலது கண்ணில் அடிபடுதல், பல் பிடுங்குதல் அல்லது முகத்தில் தழும்புகள் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Harsh words causing broken family ties, litigation costs, and sudden fiscal erosion.",
            "Prone to right-eye trauma, severe dental issues, and facial scars."
        ],
        "career_wealth_ta": [
            "ரியல் எஸ்டேட் புரோக்கரேஜ், இரும்பு/உலோக வர்த்தகம், இயந்திர உதிரிபாகங்கள், காண்ட்ராக்டர், வெடிபொருள் தயாரிப்பு, சமையல் கலை.",
            "பூமி லாபம் மற்றும் தொழில்நுட்ப உழைப்பால் செல்வச் சேர்க்கை உண்டாகும்."
        ],
        "career_wealth_en": [
            "Lucrative earnings in real estate development, scrap metal, hardware manufacturing, defense contracting, and industrial fabrication.",
            "Substantial wealth generated via property flipping and mechanical ventures."
        ],
        "health_precautions_ta": [
            "பல் வலி, ஈறுகளில் ரத்தம் வடிதல், தொண்டை அழற்சி, முகப்பருக்கள் மற்றும் வலது கண் பார்வை பாதிப்பு.",
            "வாய் சுகாதாரத்தைப் பேணுதலும், சூடான கார உணவுகளைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to dental abscesses, bleeding gums, pharyngeal inflammation, and right-eye irritation.",
            "Strict oral dental care and moderation of heavily spiced dishes are indicated."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய வீரியம் & வெற்றி)",
        "house_title_en": "3rd House - Sahaja Bhava (Extraordinary Valour & Triumph)",
        "core_traits_ta": [
            "செவ்வாய் 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது இணையற்ற வீரத்தையும் துணிவையும் தரும் ராஜ யோகமாகும்.",
            "எந்தவிதமான ஆபத்தையும் கண்டு அஞ்சாத சிங்கம் போன்ற பராக்கிரமம்; எதிரிகளைப் புறமுதுகிடச் செய்வார்.",
            "விளையாட்டு, சாகசப் பயணங்கள், உடற்கட்டு மற்றும் போட்டிகளில் எப்போதும் முதலிடம் பிடிப்பார்.",
            "இளைய சகோதரர்களிடம் கண்டிப்பு காட்டினாலும் அவர்களுக்கு அரணாக நின்று காப்பார்."
        ],
        "core_traits_en": [
            "Mars in the 3rd (Upachaya house) is classically venerated as a formidable engine of heroic valor and victory.",
            "Lionhearted bravery in the face of imminent peril; scatters opponents with decisive boldness.",
            "Stellar athletic stamina, fond of martial arts, adventurous explorations, and physical conditioning.",
            "Acts as a fierce protector for younger siblings despite an authoritative demeanor."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடாளும் அதிகாரம், ராணுவம்/காவல்துறையில் மிக உயரிய தலைமை, சரித்திரப் புகழ்.",
            "எடுத்த காரியங்கள் அனைத்திலும் அசுர வெற்றி; தோல்வி என்பதே அறியாத சாதனையாளராக விளங்குவார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows apex command in armed forces, legendary athletic laurels, and national honors.",
            "Triumphs decisively in every competitive arena; builds a legacy of fearless excellence."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப தொடர்புகள் இருப்பின்: சகோதரர்களுடன் நிலத்தகராறு, கைகளில் முறிவு அல்லது காயங்கள்.",
            "அவசரப்பட்டு வாக்குவாதம் செய்வதால் சட்டச் சிக்கல்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Acrimonious land disputes with brothers, collarbone/arm fractures, and rash legal altercations.",
            "Impulsive, aggressive outbursts causing alienation of well-wishers."
        ],
        "career_wealth_ta": [
            "ராணுவ அதிகாரிகள், விளையாட்டு வீரர்கள், துப்பறிவாளர், அறுவை சிகிச்சை நிபுணர், கட்டுமானத் துறை, பாதுகாப்பு ஏஜென்சிகள்.",
            "தைரியமான முதலீடுகளாலும் சாதனைகளாலும் அள்ள அள்ளக் குறையாத செல்வம்."
        ],
        "career_wealth_en": [
            "Celebrated success as defense commodore, elite athlete, trauma surgeon, construction developer, and security contractor.",
            "Generates vast capital through audacious enterprise and competitive contracts."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் எலும்பு முறிவு, காது நரம்புக் கோளாறு மற்றும் ரத்த உறைவு.",
            "சாகச விளையாட்டுகளின் போது பாதுகாப்பு உபகரணங்களை தவறாமல் அணிய வேண்டும்."
        ],
        "health_precautions_en": [
            "Prone to collarbone trauma, shoulder dislocations, upper limb fractures, and auditory inflammation.",
            "Mandatory usage of protective sports gear and defensive driving habits."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (பூமி யோகம் & வீரம் நிறைந்த இல்லம்)",
        "house_title_en": "4th House - Sukha Bhava (Landed Estates & Domineering Home)",
        "core_traits_ta": [
            "சொந்தமாக நிலம், தோட்டம், வீடுகள் வாங்குவதில் அதிக ஆர்வமும் சாதனையும் படைப்பவர்.",
            "வீட்டிலும் குடும்பத்திலும் தன் கட்டுப்பாடும் அதிகாரமும் இருக்க வேண்டும் என கண்டிப்பு காட்டுவார்.",
            "மனதில் ஒருவிதமான அமைதியின்மையும், அடிக்கடி கோபம் தலைக்கேறும் வேகமும் இருக்கலாம்.",
            "தாய் வழியில் கருத்து வேறுபாடுகள் வராமல் பொறுமையைக் கடைப்பிடிப்பது நல்லது."
        ],
        "core_traits_en": [
            "Tremendous passion for acquiring vast landed estates, agricultural farms, and solid brick structures.",
            "Exercises rigid, no-nonsense control within the domestic sphere; demands strict discipline at home.",
            "Harbors internal fiery restlessness, periodically venting bursts of acute irritation.",
            "Must temper domestic interactions with patience to avoid friction with mother."
        ],
        "strong_placement_ta": [
            "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் ருசக யோகம் அமைந்தால்: ஏக்கர் கணக்கில் நிலங்கள், மாளிகைகள், சொகுசு வாகனங்கள்.",
            "அரசாங்கத்தால் வழங்கப்படும் பங்களாக்கள், கௌரவப் பதவிகள் மற்றும் நிலையான செல்வ வளம்."
        ],
        "strong_placement_en": [
            "Exalted in Capricorn forming Ruchaka Yoga: Enormous acreage of land, prime real estate complexes, and heavy vehicle fleets.",
            "Granted state residences, executive privileges, and enduring ancestral security."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாய் உடல்நலம் பாதித்தல், பூர்வீக நிலங்கள் கைவிட்டுப் போதல், வீட்டு விபத்துகள்.",
            "வாகன விபத்துகள், நிலத்தகராறுகளால் வழக்குகள் மற்றும் மன நிம்மதியின்மை ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Cancer or afflicted: Severe maternal health crises, loss of parental land to litigations, and vehicle collisions.",
            "Domestic turbulence, persistent friction with relatives, and property encumbrances."
        ],
        "career_wealth_ta": [
            "கட்டிடக் கலை, சிவில் இன்ஜினியரிங், விவசாய நில வர்த்தகம், ஆட்டோமொபைல் உதிரிபாகங்கள், சுரங்கம், செங்கல் சூளைகள்.",
            "பூமி பரிவர்த்தனைகளாலும் கட்டுமானத் தொழிலாலும் கோடிக்கணக்கில் வருமானம்."
        ],
        "career_wealth_en": [
            "Flourishes in civil engineering, commercial architecture, real estate syndication, automotive logistics, and quarrying.",
            "Massive capital accumulated through property land banking and urban development."
        ],
        "health_precautions_ta": [
            "நெஞ்சு வலி, ரத்த அழுத்த ஏற்றத்தாழ்வு, இதயப் படபடப்பு, வயிற்றில் அமிலம் மற்றும் உஷ்ண வியாதிகள்.",
            "எண்ணெயில் பொரித்த உணவுகளைத் தவிர்த்து இதய நலனைப் பரிசோதித்துக் கொள்ளவும்."
        ],
        "health_precautions_en": [
            "Prone to angina pectoris, cardiovascular strain, severe gastric reflux, and chest bruising.",
            "Avoid excessive fried foods, practice cardio exercise, and schedule routine cardiac checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 174) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கூர்மையான புத்தி & தைரியமான முதலீடு)",
        "house_title_en": "5th House - Putra Bhava (Sharp Intellect & Bold Speculation)",
        "core_traits_ta": [
            "மின்னல் போன்ற கூர்மையான புத்திசாலித்தனம், விரைவான முடிவெடுக்கும் திறன் மற்றும் தந்திரமான செயலாற்றல்.",
            "பங்குச் சந்தை, புதிய கண்டுபிடிப்புகள் மற்றும் சவாலான முதலீடுகளில் தைரியமாக இறங்குவார்.",
            "பிள்ளைகளிடம் அதிக கண்டிப்பு காட்டுவார்; இதனால் பிள்ளைகளுடன் கருத்து மோதல்கள் வர வாய்ப்புண்டு.",
            "தன் அறிவாற்றலையும் திறமையையும் சவால் விடுபவர்களை ஒருபோதும் சும்மா விட மாட்டார்."
        ],
        "core_traits_en": [
            "Lightning-fast analytical intellect, incisive tactical brilliance, and instant decision-making capacity.",
            "Audacious appetite for stock markets, venture risk, technological innovations, and strategic games.",
            "Tends to enforce military discipline with children, which can create emotional friction with them.",
            "Ferociously competitive when intellectual mastery or status is challenged."
        ],
        "strong_placement_ta": [
            "சுப ஸ்தானத்தில் ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற, தைரியமான ஆண் குழந்தைகள் பிறக்கும்; பூர்வ புண்ணியம் பலம் பெறும்.",
            "அரசாங்க உயர் ஆலோசனை குழுக்களில் இடம் பெறுதல், பெரிய அளவிலான முதலீடுகளில் அசுர லாபம் ஈட்டுதல்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Bestows bold, valiant, and accomplished sons; magnifies past-life merit.",
            "Appointed to top government defense/intelligence advisory boards; massive speculative jackpots."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் தடைகள், கருச்சிதைவு அபாயம், பிள்ளைகளால் மனக்கவலை.",
            "சூதாட்டம், தவறான பங்கு வர்த்தகத்தால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Miscarriages, painful surgeries regarding progeny, and troubled relations with offspring.",
            "Crippling financial losses incurred through rash, impulsive gambling or day-trading."
        ],
        "career_wealth_ta": [
            "மென்பொருள் பொறியியல், சிஸ்டம் ஆர்க்கிடெக்ட், பங்குச் சந்தை முதலீட்டாளர், ஆயுத வடிவமைப்பு, விளையாட்டு பயிற்சியாளர்.",
            "புத்தி சாதுரியத்தாலும் தைரியமான ரிஸ்க் எடுக்கும் குணத்தாலும் பெரும் தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Thrives in algorithms/fintech, systems engineering, proprietary stock trading, defense hardware, and athletic coaching.",
            "Attains massive wealth through calculated high-stakes entrepreneurial gambles."
        ],
        "health_precautions_ta": [
            "அஜீரணம், வயிற்றுப் புண் (Peptic Ulcer), குடல் அழற்சி, கல்லீரல் உஷ்ணம் மற்றும் குடல்வால் அழற்சி (Appendicitis).",
            "காரமான உணவுகளைக் கட்டுப்படுத்தி சரியான நேரத்தில் உணவு உட்கொள்ளுதல் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to peptic ulcers, hyperacidity, acute appendicitis, and inflammatory colitis.",
            "Strictly moderate spicy dishes, avoid skipping meals, and keep stomach lining soothed."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (அசைக்க முடியாத சத்ரு ஜெயம் / மகா பலம்)",
        "house_title_en": "6th House - Satru Bhava (Total Conquest Over Foes & Invincible Immunity)",
        "core_traits_ta": [
            "செவ்வாய் 6-ஆம் பாவத்தில் அமைவது ஜாதகத்திற்கு மாபெரும் கவசமாகும்; எதிரிகள் இவரைக் கண்டு அஞ்சுவர்.",
            "எந்தவிதமான வழக்கு, போட்டி, சதித்திட்டம் மற்றும் கடன் தொல்லைகளையும் தவிடுபொடியாக்கும் அசுர பலம்.",
            "அளப்பரிய நோய் எதிர்ப்புச் சக்தி; கடினமான உடலுழைப்பையும் தாங்கும் திடகாத்திரமான உடல்வாகு.",
            "பணியாளர்களையும் வேலைக்காரர்களையும் திறம்பட வழிநடத்தி வேலை வாங்கும் சாமர்த்தியம் உண்டு."
        ],
        "core_traits_en": [
            "Mars in the 6th is classically celebrated as an impenetrable fortress of strength; totally annihilates opposition.",
            "Crushes all litigation, hostile conspiracies, and financial liabilities with unyielding resolve.",
            "Possesses iron physical stamina, supreme immune resilience, and boundless work capacity.",
            "Commands absolute obedience and high productivity from subordinates and staff."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, நீதித்துறை/ராணுவத்தில் சர்வாதிகார அதிகாரம்.",
            "அளப்பரிய செல்வம், உடல் ஆரோக்கியம் மற்றும் போட்டிகளில் தொடர் வெற்றிகள் குவியும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows complete Shatru Samhara Yoga! Total absence of enemies, premier defense/judicial supreme command.",
            "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உடலில் உஷ்ண வியாதிகள், கொப்பளங்கள், அறுவை சிகிச்சைகள்.",
            "வேலையாட்களால் தகராறுகள், கடன் சுமைகள் அல்லது தாய்மாமனுடன் விரோதம் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Cancer or afflicted: Recurring acute inflammatory fevers, painful surgeries, and blood impurities.",
            "Troublesome labor disputes, insubordinate employees, and financial friction with maternal uncles."
        ],
        "career_wealth_ta": [
            "அறுவை சிகிச்சை மருத்துவர், குற்றவியல் வழக்கறிஞர், ராணுவத் தளபதி, வங்கி கடன் வசூலிப்பு, பாதுகாப்புத் துறை, சுங்கத்துறை.",
            "போட்டிகளையும் எதிர்ப்புகளையும் முறியடித்து அதன் வழியே அபரிமிதமான செல்வம் ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Dominates in trauma/orthopedic surgery, criminal trial law, armed forces, debt recovery, and border customs enforcement.",
            "Extracts substantial financial wealth directly from competitive conquests."
        ],
        "health_precautions_ta": [
            "அடிவயிற்று வலி, சிறுநீரகக் கற்கள், ரத்தக் கொப்பளங்கள், தீக்காயங்கள் மற்றும் அறுவை சிகிச்சைத் தழும்புகள்.",
            "அதிக நீர் அருந்துதலும், ரத்த அழுத்தப் பரிசோதனைகளும் அவசியமாகும்."
        ],
        "health_precautions_en": [
            "Vulnerable to kidney stones, acute abscesses, blood toxicities, burns, and surgical interventions.",
            "Maintain high fluid intake, monitor blood pressure, and avoid extreme heat exposure."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (குஜ தோஷம் / ஆற்றல்மிக்க துணை)",
        "house_title_en": "7th House - Kalathra Bhava (Kuja Dosha / Dynamic Spouse)",
        "core_traits_ta": [
            "துணிச்சலான, கம்பீரமான மற்றும் சுதந்திரமான சுபாவம் கொண்ட வாழ்க்கைத் துணை அமைவார்.",
            "குஜ தோஷம் (Kuja Dosha) அமைவதால் வாழ்க்கைத் துணையுடன் ஈகோ மோதல்களும் சூடான வாக்குவாதங்களும் வரலாம்.",
            "கூட்டுத் தொழிலில் பார்ட்னர்களிடம் கண்டிப்பும் வெளிப்படைத்தன்மையும் கொண்டிருப்பார்.",
            "சுயமரியாதையை விட்டுக்கொடுக்க மாட்டார்; தாம்பத்தியத்தில் சமரசமும் பொறுமையும் மிக அவசியமாகும்."
        ],
        "core_traits_en": [
            "Spouse is dynamic, spirited, courageous, fiercely independent, and possessing strong willpower.",
            "Classic Kuja Dosha (Mangal Dosha) configuration; sparks volatile ego clashes if mutual patience is lacking.",
            "Direct and strictly contractual in commercial business partnerships.",
            "Refuses to compromise on personal dignity; conscious harmony and emotional tact are essential."
        ],
        "strong_placement_ta": [
            "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப சேர்க்கை பெற்றால்: குஜ தோஷம் நிவர்த்தியாகி வசதியான, செல்வாக்கு மிக்க துணை அமைவார்.",
            "ரியல் எஸ்டேட் மற்றும் தொழில் கூட்டாண்மைகளில் பன்னாட்டு அளவில் பெரும் லாபமும் வெற்றியும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted in Capricorn or in own signs with benefics: Kuja Dosha is cancelled, granting an affluent, high-status, devoted partner.",
            "Remarkable financial windfalls through multinational corporate joint ventures and real estate syndicates."
        ],
        "weak_placement_ta": [
            "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடும் விரிசல், விவாகரத்து அல்லது பிரிவினை அபாயம்.",
            "துணைக்கு விபத்துகள், ரத்த அழுத்தம் அல்லது கூட்டுத் தொழிலில் பெரும் ஏமாற்றங்கள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Cancer or afflicted by malefics: Severe marital turbulence, threat of separation or divorce.",
            "Spouse prone to physical injuries, surgeries, or hypertension; financial betrayal by business partners."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், கட்டுமான காண்ட்ராக்ட், இயந்திர இறக்குமதி, சட்ட ஒப்பந்தங்கள், விளையாட்டு பொருட்கள் உற்பத்தி.",
            "வாழ்க்கைத் துணையின் குடும்ப வழியிலும் துணிச்சலான கூட்டு வர்த்தகத்தாலும் தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Lucrative success in international engineering trade, construction contracting, industrial imports, and sports goods.",
            "Substantial capital influx via marital alliances and strategic commercial consortiums."
        ],
        "health_precautions_ta": [
            "சிறுநீரகப் பாதை எரிச்சல், அடிவயிற்று உஷ்ணம், விரைவாதம், கருப்பை அல்லது விதைப்பை உபாதைகள்.",
            "முறையான மருத்துவப் பரிசோதனைகளும், உஷ்ணத்தைத் தணிக்கும் உணவுகளும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to urinary tract inflammation, pelvic inflammatory disease, prostatitis, and reproductive heat.",
            "Routine medical screenings and staying well-hydrated are strongly indicated."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (அஷ்டம செவ்வாய் / ஆபத்துகளிலிருந்து தப்புதல்)",
        "house_title_en": "8th House - Ayur Bhava (Survival from Peril & Secret Assets)",
        "core_traits_ta": [
            "அசாத்தியமான மன உறுதி; ஆபத்தான சூழ்நிலைகளில் கூட தற்காத்துக் கொள்ளும் துணிச்சலான உள்ளுணர்வு உடையவர்.",
            "அஷ்டமத்தில் செவ்வாய் அமர்வது மாங்கல்ய தோஷம் மற்றும் ஆயுள் பரிசோதனைகளைத் தரக்கூடிய அமைப்பாகும்.",
            "வாழ்க்கையில் திடீர் விபத்துகள், ரத்தக் காயங்கள் அல்லது அறுவை சிகிச்சைகளை சந்திக்க நேரிடலாம்.",
            "ரகசியத் திட்டங்களைத் தீட்டுவதிலும் மறைமுக எதிரிகளை எதிர்கொள்வதிலும் வல்லவர்."
        ],
        "core_traits_en": [
            "Exceptional survival instincts; possesses an uncanny reflex to extricate self from hazardous emergencies.",
            "Mars in the 8th is a critical placement for Kuja Dosha, testing marital harmony and physical safety.",
            "Prone to unexpected accidental mishaps, lacerations, or sudden surgical operations during Dasa periods.",
            "Highly adept at keeping confidential secrets and outmaneuvering covert adversaries."
        ],
        "strong_placement_ta": [
            "விருச்சிகத்தில் ஆட்சி அல்லது மகரத்தில் உச்சம் பெற்றால்: விபத்துகளிலிருந்து தப்பும் யோகம், நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள்.",
            "துணையின் வழியே மாபெரும் காப்பீட்டுத் தொகையோ அல்லது பூர்வீக சொத்துகளோ வந்து சேரும்."
        ],
        "strong_placement_en": [
            "In own sign Scorpio or exalted in Capricorn: Miraculous escapes from physical danger, sturdy longevity, vast legacies.",
            "Acquires substantial insurance claims, estates, and concealed wealth through marital ties."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீக்காயங்கள், ஆயுதங்களால் காயங்கள், வாகன விபத்துகள், மூல நோய்.",
            "திருமண வாழ்வில் துணையின் ஆயுளுக்கு கண்டம் அல்லது கடுமையான சண்டை சச்சரவுகள் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Burns, severe lacerations from metal/weapons, traffic crashes, and severe piles.",
            "Severe physical trials for the spouse, legal entanglements, and sudden wealth depletion."
        ],
        "career_wealth_ta": [
            "தடயவியல் துறை, பிரேதப் பரிசோதனை மருத்துவர், வெடிபொருள் நிபுணர், ஆயுள் காப்பீட்டு தணிக்கை, சுரங்க இன்ஜினியரிங்.",
            "திடீர் இன்சூரன்ஸ் இழப்பீடுகள், உயில் சொத்துகள் மற்றும் ரகசிய ஒப்பந்தங்கள் மூலம் தன வரவு."
        ],
        "career_wealth_en": [
            "Excels in forensic pathology, trauma surgery, demolition engineering, insurance auditing, and oil drilling.",
            "Wealth derived through settlement windfalls, unearned inheritance, and crisis management fees."
        ],
        "health_precautions_ta": [
            "மூல நோய் (Piles), ஆசனவாய் வெடிப்பு, ரத்தப் போக்கு, இடுப்பு எலும்பு முறிவு மற்றும் விபத்துக் காயங்கள்.",
            "வாகனம் ஓட்டும்போது மிகுந்த எச்சரிக்கை தேவை; நார்ச்சத்து மிகுந்த உணவுகளை உண்பது நல்லது."
        ],
        "health_precautions_en": [
            "Vulnerable to hemorrhoidal bleeding, anal fissures, acute pelvic trauma, and bone fractures.",
            "Extreme caution required when handling vehicles or machinery; maintain a high-fiber cooling diet."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம வீரம் & தந்தை நலம்)",
        "house_title_en": "9th House - Bhagya Bhava (Righteous Crusader & Paternal Fortune)",
        "core_traits_ta": [
            "நியாயத்திற்காகவும் அநீதியை எதிர்த்தும் துணிவுடன் குரல் கொடுக்கும் தர்ம வீரர்.",
            "தனக்கென தனித்துவமான கொள்கைகளை வகுத்துக்கொண்டு வாழ்வார்; பிறர் சொல்வதை அப்படியே ஏற்க மாட்டார்.",
            "தந்தையுடன் கருத்து வேறுபாடுகள் வரலாம்; ஆனால் தந்தையின் நலனில் எப்போதும் அக்கறை கொண்டிருப்பார்.",
            "நீண்ட தூர சாகசப் பயணங்கள், மலைப் பிரதேசங்கள் மற்றும் வரலாற்றுச் சிறப்புமிக்க இடங்களுக்குச் செல்வதில் விருப்பம்."
        ],
        "core_traits_en": [
            "Fierce champion of justice; ready to combat ethical wrongdoing and stand up for righteous causes.",
            "Possesses an independent philosophical worldview; refuses blind dogmatic conformism.",
            "Periodic ideological clashes with the father, yet preserves a fundamental filial loyalty.",
            "Passionate affinity for high-altitude treks, rugged adventures, and exploring ancient battlefields."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்று சுப பார்வை அமைந்தால்: தந்தையின் செல்வாக்கு உயர்தல், முன்னோர்களின் பூமி பலம், அரசு கௌரவம்.",
            "ஆன்மீகத் தலைமை, தர்ம ஸ்தாபனங்களில் நிர்வாகப் பதவி மற்றும் சமுதாயத்தில் மாபெரும் நற்பெயர்."
        ],
        "strong_placement_en": [
            "Exalted or in own house with benefics: Elevates paternal stature, inherits vast ancestral lands, and wins civic awards.",
            "Attains executive stewardship over religious or philanthropic foundations and universal respect."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், தந்தையுடன் கடுமையான விரோதம்.",
            "ஆன்மீக குருமார்களுடன் மோதல்கள், சட்டச் சிக்கல்கள் மற்றும் வெளிநாட்டுப் பயணங்களில் தடைகள்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health breakdown, bitter estrangement from father, and legal suits.",
            "Clashes with religious mentors, anti-establishment rebelliousness, and visa/immigration denials."
        ],
        "career_wealth_ta": [
            "சட்டத்துறை, உயர் நீதிமன்ற நீதிபதி, அரசியல் பேச்சாளர், சர்வதேச பாதுகாப்பு ஆலோசகர், வனத்துறை அதிகாரி.",
            "நீதி மற்றும் தர்ம வழியிலும், வெளிநாட்டுத் தொடர்புகளாலும் நிலையான சொத்துகள் சேரும்."
        ],
        "career_wealth_en": [
            "Thrives as appellate judge, constitutional attorney, geopolitical defense analyst, and forestry conservator.",
            "Builds enduring real estate assets through ethical practice and multinational contracts."
        ],
        "health_precautions_ta": [
            "தொடை எலும்பு வலி, இடுப்பு நரம்புப் பிடிப்பு (Sciatica), கல்லீரல் உஷ்ணம் மற்றும் தசைப் பிடிப்புகள்.",
            "முறையான யோகாசனப் பயிற்சிகளும், தசைப் பிடிப்புகளுக்கான மசாஜ்களும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Prone to femoral strain, sciatic nerve irritation, liver heat, and hamstring muscle tears.",
            "Regular yoga stretching and therapeutic muscular massage optimize lower limb mobility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (குலதீபக யோகம் / திக்பலம் & தலைமை)",
        "house_title_en": "10th House - Karma Bhava (Kuladipaka Yoga / Supreme Digbala & Command)",
        "core_traits_ta": [
            "செவ்வாய் 10-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று குலதீபக யோகத்தை (Kuladipaka Yoga) உருவாக்குகிறார்.",
            "தன் குலத்திற்கே விளக்காகத் திகழ்ந்து குடும்பத்தையும் தொழிலையும் மாபெரும் உச்சிக்குக் கொண்டு செல்வார்.",
            "தளராத சுறுசுறுப்பு, தலைமை தாங்கும் பேராற்றல், இரும்பு போன்ற மன உறுதி மற்றும் கம்பீரம்.",
            "சவாலான திட்டங்களை முன்னின்று நடத்தி முடிக்கும் செயல்வீரர்; எதிர்ப்புகளைத் தூள்தூளாக்குவார்."
        ],
        "core_traits_en": [
            "Mars attains maximum Digbala (directional potency) in the 10th house, generating the prestigious Kuladipaka Yoga.",
            "Acts as the radiant beacon of the lineage, elevating family name and commercial fortunes to unprecedented peaks.",
            "Unbounded dynamism, invincible leadership prowess, iron fortitude, and commanding imperial aura.",
            "Relentless executor who spearheads daunting missions and obliterates institutional stagnation."
        ],
        "strong_placement_ta": [
            "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் ருசக யோகம் பெற்றால்: நாட்டின் முதன்மை ராணுவத் தளபதி, போலீஸ் டிஜிபி, கேபினட் மந்திரி யோகம்.",
            "பல்லாயிரக்கணக்கான பணியாளர்களை வழிநடத்தும் தலைமை நிர்வாக அதிகாரி (CEO) அந்தஸ்து மற்றும் சரித்திரப் புகழ்."
        ],
        "strong_placement_en": [
            "Exalted in Capricorn or in own signs forming Ruchaka Yoga: Chief of Army Staff, Director General of Police, Cabinet Minister.",
            "Global industrialist or CEO commanding thousands of personnel; enters history books as a transformative pioneer."
        ],
        "weak_placement_ta": [
            "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: அதிகாரிகளுடன் மோதல், பதவியிறக்கம், பொது வாழ்வில் சரிவு.",
            "தொழிலில் விபத்துகள், இயந்திரச் சேதங்கள் மற்றும் திடீர் நஷ்டங்கள் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Sudden workplace fall, clashes with state regulators, demotion from high office.",
            "Severe industrial accidents, mechanical breakdowns, and catastrophic business liabilities."
        ],
        "career_wealth_ta": [
            "பாதுகாப்புப் படைகள், காவல்துறை, சிவில் இன்ஜினியரிங், அறுவை சிகிச்சை மருத்துவமனை அதிபர், பெரிய தொழிற்சாலைகள், கனரக இயந்திரங்கள்.",
            "அரசாங்க ஒப்பந்தங்கள் மற்றும் தொழில் ஆளுமை மூலம் பல கோடிகளில் சொத்துக்களும் அதிகாரமும்."
        ],
        "career_wealth_en": [
            "Dominant in military defense, police leadership, heavy civil construction, hospital chains, and steel fabrication.",
            "Multi-million dollar assets accrued through authoritative leadership and state infrastructure tenders."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் ரத்த அழுத்தம், மூட்டு வலி, தசை இறுக்கம் மற்றும் உஷ்ணக் கட்டிகள்.",
            "முறையான உடற்பயிற்சியும், ஓய்வுக்கான நேரத்தை ஒதுக்குவதும் நீண்ட ஆயுளைத் தரும்."
        ],
        "health_precautions_en": [
            "Occupational stress, hypertension, knee cartilage wear, muscle spasms, and febrile inflammation.",
            "Structured cardiovascular workouts and disciplined sleep patterns protect executive vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட பூமி லாபம் & மாபெரும் தன வரவு)",
        "house_title_en": "11th House - Labha Bhava (Massive Real Estate Gains & Wealth Accumulation)",
        "core_traits_ta": [
            "செவ்வாய் 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது அளப்பரிய செல்வத்தையும், தொடர் லாபங்களையும் தரும் யோகமாகும்.",
            "எடுத்த முதலீடுகள் யாவிலும் இரட்டிப்பு லாபம்; ஆசைகள் அனைத்தும் தன்னம்பிக்கையால் நிறைவேறும்.",
            "செல்வாக்கு மிக்க தலைவர்கள், தொழில் அதிபர்கள் மற்றும் பாதுகாப்பு அதிகாரிகளின் நட்பு கிட்டும்.",
            "மூத்த சகோதரர்களிடம் அன்பும் அதே சமயம் சில கருத்து வேறுபாடுகளும் ஏற்படலாம்."
        ],
        "core_traits_en": [
            "Mars in the 11th (an Upachaya house) is a premier harbinger of relentless wealth creation and continuous financial expansion.",
            "Multiplies capital returns on every enterprise; fulfills grand ambitions through bold self-effort.",
            "Cultivates powerful camaraderie with magnates, top bureaucrats, and military chiefs.",
            "Maintains a respectful yet occasionally combative dynamic with elder siblings."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற நிலங்கள், அடுக்குமாடிக் குடியிருப்புகள், தொழிற்சாலைகள், தங்கக் கட்டிகள் குவியும்.",
            "சமுதாயத்தில் மாபெரும் செல்வந்தராகப் போற்றப்படுதல், அரசியலில் பெரிய ஆதரவு பெறுதல்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multiple residential towers, vast agricultural acreages, factories, and gold bullion.",
            "Ranked among the elite wealthy tier of society; commands formidable political muscle."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாப சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு பெரும் இழப்பு, மூத்த சகோதரருடன் சொத்துத் தகராறு.",
            "லாபங்கள் கைநழுவுதல், கடன் சுமைகள் அல்லது தவறான முதலீடுகளால் விரயங்கள்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Heavy betrayal by deceptive associates, bitter partition lawsuits with elder brother.",
            "Sudden loss of profit margins and capital entrapment in disputed properties."
        ],
        "career_wealth_ta": [
            "ரியல் எஸ்டேட் வளர்ச்சி, நில மேம்பாடு, இரும்பு மற்றும் எஃகு ஆலைகள், கட்டுமான ஒப்பந்தங்கள், வென்ச்சர் கேபிடல்.",
            "நிலங்களின் மதிப்பு பல மடங்கு உயர்வதாலும், துணிச்சலான வணிகத்தாலும் பெரும் தன லாபம்."
        ],
        "career_wealth_en": [
            "Magnificent success in mega-real-estate syndicates, steel manufacturing, infrastructure procurement, and venture capital.",
            "Huge exponential capital appreciation realized from prime urban land parcels."
        ],
        "health_precautions_ta": [
            "இடது காது வலி, கணுக்கால் சுளுக்கு, ரத்தக் கொதிப்பு மற்றும் தசைநார் கிழிசல்.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், ரத்த அழுத்தப் பரிசோதனைகளும் நலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear inflammation, ankle sprains, arterial hypertension, and ligament tears.",
            "Calf stretching, ankle mobility drills, and routine vascular monitoring are advised."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (குஜ தோஷம் / வெளிநாட்டு வெற்றி & விரயம்)",
        "house_title_en": "12th House - Vraya Bhava (Kuja Dosha / Foreign Conquests & Heavy Expenses)",
        "core_traits_ta": [
            "சுதந்திரமான மனப்பான்மை; பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ சாதிப்பார்.",
            "செவ்வாய் 12-ஆம் பாவத்தில் அமர்வது குஜ தோஷத்தை (Kuja Dosha) உண்டாக்கும்; தாம்பத்தியத்தில் சகிப்புத்தன்மை தேவை.",
            "பணத்தை தாராளமாகச் செலவழிக்கும் சுபாவம்; திடீர் விரயங்களும் எதிர்பாராத நஷ்டங்களும் வரலாம்.",
            "ரகசிய எதிரிகளை எளிதில் அடையாளம் கண்டு அவர்களைத் துணிவுடன் முறியடிப்பார்."
        ],
        "core_traits_en": [
            "Restless independent spirit; thrives far more dramatically abroad or in distant jurisdictions than in birth city.",
            "Triggers Kuja Dosha (Mangal Dosha) from the 12th; necessitates conscious tolerance and tenderness in marital intimacy.",
            "Spends with open-handed impetuosity; prone to sudden drain of liquid funds.",
            "Possesses sharp instincts to sniff out hidden conspirators and neutralize them proactively."
        ],
        "strong_placement_ta": [
            "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப சேர்க்கை பெற்றால்: வெளிநாட்டில் மாபெரும் ரியல் எஸ்டேட் சாம்ராஜ்யம், ஆயுத ஏற்றுமதி.",
            "அரசாங்கத் தூதரகங்களில் பாதுகாப்பு அதிகாரி யோகம், எதிரிகளைத் தன் காலடியில் வீழ்த்தும் பராக்கிரமம்."
        ],
        "strong_placement_en": [
            "Exalted or well-placed: Commands massive offshore real estate holdings, defense hardware contracts, and global standing.",
            "Attains prestigious diplomatic defense attache roles; totally subjugates covert adversaries."
        ],
        "weak_placement_ta": [
            "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: இடது கண் காயம், தூக்கமின்மை, மருத்துவச் செலவுகள், சிறைவாசம் அல்லது சட்ட அபராதங்கள்.",
            "தாம்பத்திய சுகக் குறைவு, விவாகரத்து வழக்குகள் மற்றும் திடீர் நிதி திவால் அபாயம்."
        ],
        "weak_placement_en": [
            "Debilitated or heavily afflicted: Left eye ocular injury, acute insomnia, crushing surgical debts, confinement or penal fines.",
            "Marital estrangement, bedroom coldness, and risk of sudden insolvency."
        ],
        "career_wealth_ta": [
            "வெளிநாட்டு காண்ட்ராக்ட், கப்பல் படை, சிறைத்துறை நிர்வாகம், சர்வதேச உளவுத்துறை, மெட்டலர்ஜி மற்றும் ஆயுத வர்த்தகம்.",
            "வெளிநாட்டு முதலீடுகளாலும் தூரதேசப் பணிகளாலும் செல்வம் சேரும்."
        ],
        "career_wealth_en": [
            "Dominates in foreign defense contracting, naval navigation, correctional administration, international espionage, and metallurgy.",
            "Generates vast revenues in foreign currencies from remote overseas installations."
        ],
        "health_precautions_ta": [
            "இடது கண் பாதிப்பு, பாதங்களில் வெட்டுக்காயங்கள்/தீக்காயங்கள், மூல நோய் மற்றும் தூக்கமின்மை.",
            "இரவில் அமைதியான சூழலில் தூங்குவதும், பாதங்களைப் பாதுகாப்பதும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Vulnerable to left-eye lacerations, foot burns/puncture wounds, acute hemorrhoids, and insomnia.",
            "Wear sturdy footwear, secure protective eyewear, and practice sleep hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]
