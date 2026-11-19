# -*- coding: utf-8 -*-
"""
Planetary House Predictions for Mercury (புதன்), Jupiter (குரு), and Venus (சுக்கிரன்)
Based on Dr. B. V. Raman's "How to Judge a Horoscope" & Classical Saravali
"""

MERCURY_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (திக்பலம் / மகா புத்தி & வித்யா யோகம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Digbala / Intellect & Wit)",
        "core_traits_ta": [
            "புதன் லக்னத்தில் திக்பலம் (Digbala) பெற்று அமர்வது மாபெரும் வித்யா யோகத்தையும் கூர்மையான புத்திக்கூர்மையையும் தரும்.",
            "கவர்ச்சிகரமான இளமைத் தோற்றம், நகைச்சுவை உணர்வு, வசீகரமான பேச்சாற்றல் மற்றும் விரைந்து கற்கும் திறன்.",
            "கணிதம், ஜோதிடம், கணக்கியல், தர்க்க சாஸ்திரம் மற்றும் பல மொழிகளில் புலமை பெறும் ஆற்றல் உண்டு.",
            "விவேகமான முடிவுகள், சாதுரியமான அணுகுமுறை மற்றும் எந்தச் சூழ்நிலையிலும் நயமாகப் பேசி காரியம் சாதிக்கும் சாமர்த்தியம்.",
            "மானமரியாதைக்கு முக்கியத்துவம் கொடுப்பார்; தன் அறிவை யாரேனும் குறைத்து மதிப்பிடுவதை விரும்ப மாட்டார்."
        ],
        "core_traits_en": [
            "Mercury attains supreme Digbala (directional potency) in the 1st house, generating extraordinary intellectual brilliance.",
            "Youthful countenance, delightful wit, magnetic eloquence, and an agile, lightning-fast learning capacity.",
            "Natural genius in mathematics, astrology, accountancy, logic, linguistics, and literature.",
            "Diplomatic acumen; navigates convoluted interpersonal scenarios with polished grace and persuasive tact.",
            "Treasures intellectual self-respect; disdains superficiality and arrogance in peers."
        ],
        "strong_placement_ta": [
            "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் (Bhadra Yoga) அமைந்தால்: உலகப் புகழ் பெற்ற அறிஞர், அரசாங்க முதன்மை ஆலோசகர்.",
            "நூற்றுக்கணக்கான நூல்களை இயற்றும் ஆற்றல், சர்வதேச விருதுகள் மற்றும் மாபெரும் தொழில் சாம்ராஜ்யம்."
        ],
        "strong_placement_en": [
            "Exalted in Virgo or own sign Gemini forming Bhadra Mahapurusha Yoga: Globally acclaimed scholar, chief ministerial advisor.",
            "Prolific author of masterworks, recipient of international scholastic laurels, and creator of successful commercial conglomerates."
        ],
        "weak_placement_ta": [
            "மீனத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நரம்புத் தளர்ச்சி, முடிவெடுப்பதில் குழப்பம், பேச்சில் தடுமாற்றம்.",
            "அதிக சிந்தனையால் மன உளைச்சல் மற்றும் சூதாட்டம் அல்லது தவறான கணக்குகளால் நஷ்டம்."
        ],
        "weak_placement_en": [
            "Debilitated in Pisces or afflicted: Nervous debility, mental indecision, stammering, and erratic memory lapses.",
            "Overthinking inducing chronic mental exhaustion and fiscal losses due to fraudulent book-keeping."
        ],
        "career_wealth_ta": [
            "தகவல் தொழில்நுட்பம் (IT), மென்பொருள் உருவாக்கம், தணிக்கையாளர் (CA), பத்திரிகையாளர், எழுத்தாளர், பங்கு வர்த்தகம், கல்வித்துறை.",
            "அறிவுசார் சொத்துரிமை, வர்த்தக சாதுரியம் மற்றும் தரகு/கமிஷன் மூலம் அபரிமிதமான செல்வம்."
        ],
        "career_wealth_en": [
            "Eminent success in information technology, software architecture, chartered accountancy, journalism, equity trading, and publishing.",
            "Generates vast wealth through intellectual property, syndication royalties, and commercial brokerage."
        ],
        "health_precautions_ta": [
            "நரம்பு மண்டல பலவீனம், தோல் அலர்ஜி, ஆஸ்துமா, தலைவலி மற்றும் கைகளில் நடுக்கம்.",
            "தியானம், பிராணாயாமம் மற்றும் கீரை வகைகளை உணவில் சேர்ப்பது நரம்புகளைப் பலப்படுத்தும்."
        ],
        "health_precautions_en": [
            "Prone to nervous breakdown, skin dermatosis, bronchial asthma, vertigo, and hand tremors.",
            "Deep yogic breathing, nervous relaxation therapies, and green leafy nutrition preserve equilibrium."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (சாதுரிய வாக்கு & வணிகச் செல்வம்)",
        "house_title_en": "2nd House - Dhana Bhava (Eloquent Speech & Commercial Wealth)",
        "core_traits_ta": [
            "நயமான, இனிமையான மற்றும் எந்தக் கூட்டத்தையும் தன் பேச்சால் மயக்கும் அபார பேச்சாற்றல்.",
            "வணிக நுணுக்கங்கள், கணக்கு வழக்குகளில் துல்லியம் மற்றும் பணத்தைச் சுழற்றிப் பெருக்கும் சாதுரியம்.",
            "குடும்பத்தில் மகிழ்ச்சியான சூழல்; உறவினர்களுடன் கலகலப்பாகப் பழகும் சுபாவம்.",
            "நகைச்சுவை ததும்பப் பேசி அனைவரையும் சிரிக்க வைக்கும் கலை உணர்வு கொண்டவர்."
        ],
        "core_traits_en": [
            "Exceptional eloquence; enchants audiences with persuasive, humorous, and lucid expression.",
            "Acute mercantile instincts, flawless mathematical ledgering, and masterly financial acumen.",
            "Fosters a joyful, lively, and intellectually stimulating domestic atmosphere.",
            "Spontaneous sense of humor and quick repartee that endears him across social circles."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: கோடிக்கணக்கான திரவ சேமிப்பு, வைர-வைடூரியங்கள், வாக்கு பலிதம்.",
            "பேச்சையே மூலதனமாக வைத்துப் பெரும் பணம் ஈட்டும் வித்தாக விளங்குவார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows massive liquid banking reserves, precious gems, and prophetic speech accuracy.",
            "Monetizes communicative intellect into an inexhaustible goldmine of wealth."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் பொய்மை, வாக்கு தவறுகை, தவறான முதலீடுகளால் நஷ்டம்.",
            "பற்களில் சொத்தை, வாய் புண்கள் அல்லது வலது கண்ணில் பார்வை மங்குதல் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Deceptive speech, breach of financial trusts, and heavy trading losses.",
            "Prone to dental decay, oral ulcerations, and right-eye vision impairments."
        ],
        "career_wealth_ta": [
            "வங்கி மேலாளர், தணிக்கையாளர், முதலீட்டு ஆலோசகர், தொலைக்காட்சி நிகழ்ச்சித் தொகுப்பாளர், பேராசிரியர், பதிப்பகத் தொழில்.",
            "பேச்சாற்றல், எழுத்து மற்றும் வர்த்தக பரிவர்த்தனைகள் மூலம் வற்றாத தன வரவு."
        ],
        "career_wealth_en": [
            "Thrives in banking management, forensic auditing, investment brokerage, media broadcasting, and publishing.",
            "Continuous revenue streams flowing directly from intellectual and rhetorical services."
        ],
        "health_precautions_ta": [
            "தொண்டை எரிச்சல், வாய் துர்நாற்றம், பற்கள் ஆடுதல், நாக்கில் வெடிப்பு மற்றும் நரம்புத் தளர்ச்சி.",
            "வாய் சுகாதாரத்தைப் பேணுதலும் சத்தான காய்கறிகளை உண்பதும் நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to pharyngeal irritation, halitosis, periodontal disease, and lingual sensitivity.",
            "Strict oral hygiene and antioxidant-rich organic nutrition prevent flare-ups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (படைப்பாற்றல் & தகவல் தொடர்பு)",
        "house_title_en": "3rd House - Sahaja Bhava (Literary Creativity & Media Enterprise)",
        "core_traits_ta": [
            "அசாத்தியமான எழுத்தாற்றல், பத்திரிகைத் துறையில் மேன்மை மற்றும் புதிய யோசனைகளை உருவாக்கும் திறன்.",
            "சகோதர சகோதரிகளுடன் நல்ல தோழமையும், அவர்களுடன் இணைந்து புதிய முயற்சிகளைத் தொடங்கும் ஆர்வமும் இருக்கும்.",
            "சுறுசுறுப்பான செயல்பாடுகள், குறுகிய வணிகப் பயணங்கள் மற்றும் நண்பர்களின் விரிவான வட்டாரம்.",
            "கைகளால் செய்யும் நுணுக்கமான வேலைகள், சித்திரங்கள், சிற்பங்கள் அல்லது கணினி தட்டச்சில் அசாத்திய வேகம்."
        ],
        "core_traits_en": [
            "Prolific literary ability, journalistic finesse, and brilliant creative conceptualization.",
            "Fraternal warmth; collaborates with siblings on pioneering media or technological ventures.",
            "Agile, restless energy; thrives on frequent short commercial trips and diverse social networking.",
            "Deft manual dexterity; excels in fine draftsmanship, calligraphy, digital programming, and instrumental music."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற நாவலாசிரியர், ஊடக சாம்ராஜ்யத்தின் அதிபர், சர்வதேசப் புகழ்.",
            "தொலைத்தொடர்பு மற்றும் பதிப்பகத் துறையில் பெரும் முதலீடுகளும் வெற்றிகளும் குவியும்."
        ],
        "strong_placement_en": [
            "Strong or exalted: Becomes a celebrated literary novelist, media mogul, and recipient of international acclaim.",
            "Builds lucrative empires across digital communications, satellite broadcasting, and publishing."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
            "எழுதிய எழுத்துகளால் வீண் வழக்குகள் அல்லது பத்திரிகை விவகாரங்களில் அவப்பெயர் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Bitter sibling misunderstandings, writer's block, and carpal tunnel syndrome.",
            "Defamation lawsuits or copyright controversies arising from rash publications."
        ],
        "career_wealth_ta": [
            "பத்திரிகை ஆசிரியர், நாவலாசிரியர், டிஜிட்டல் மார்க்கெட்டிங், விளம்பர ஏஜென்சி, தபால் மற்றும் பார்சல் சர்வீஸ், திரைக்கதை ஆசிரியர்.",
            "எழுத்தாற்றலாலும் தகவல் தொடர்பு நெட்வொர்க்குகளாலும் அபரிமிதமான செல்வம் சேரும்."
        ],
        "career_wealth_en": [
            "High rewards in editor-in-chief roles, digital marketing, screenplay creation, logistics syndicates, and advertising.",
            "Wealth surges through syndicate content, book royalties, and high-velocity digital networks."
        ],
        "health_precautions_ta": [
            "கைகளில் நரம்புப் பிடிப்பு, தோள்பட்டை வலி, காதுகளில் இரைச்சல் (Tinnitus) மற்றும் விரல் நடுக்கம்.",
            "கணினியில் வேலை செய்வோர் விரல்களுக்கும் கண்களுக்கும் குறிப்பிட்ட இடைவெளியில் ஓய்வு கொடுக்க வேண்டும்."
        ],
        "health_precautions_en": [
            "Prone to carpal tunnel syndrome, shoulder tension, tinnitus, and finger muscular fatigue.",
            "Ergonomic computer posture and periodic typing breaks protect musculoskeletal agility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (உயர்கல்வி, சொத்து & மகிழ்ச்சியான இல்லம்)",
        "house_title_en": "4th House - Sukha Bhava (Higher Education, Property & Joyful Home)",
        "core_traits_ta": [
            "ஆழ்ந்த கல்வி ஞானம், பல பட்டங்களைப் பெறும் யோகம் மற்றும் ஆராய்ச்சிகளில் ஆர்வம் கொண்டவர்.",
            "தாய் வழியில் அன்பும் ஆதரவும் பரிபூரணமாகக் கிட்டும்; தாயார் அறிவார்ந்த பெண்ணாக இருப்பார்.",
            "அழகிய நூலகம் கொண்ட சொகுசு வீடு, நவீன வாகனங்கள் மற்றும் பசுமையான சூழலில் வாழும் யோகம்.",
            "மனதில் நிம்மதியும், நண்பர்களை இன்முகத்துடன் வரவேற்று உபசரிக்கும் பண்பும் இருக்கும்."
        ],
        "core_traits_en": [
            "Scholastic brilliance, multiple advanced academic degrees, and relentless scientific curiosity.",
            "Cherished bond with an erudite, accomplished mother who acts as primary intellectual guide.",
            "Resides in a tastefully decorated home with an extensive personal library and modern vehicles.",
            "Radiates domestic serenity, refined manners, and delightful intellectual hospitality."
        ],
        "strong_placement_ta": [
            "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் அமைந்தால்: பல்கலைக்கழக துணைவேந்தர், பெரும் நூலாசிரியர்.",
            "அரசாங்கத்தால் வழங்கப்படும் உயரிய கௌரவங்கள், நவீன பங்களாக்கள் மற்றும் பூமி லாபம்."
        ],
        "strong_placement_en": [
            "Exalted or own house forming Bhadra Yoga: University Vice-Chancellor, premier scholar-statesman.",
            "Honored with state residences, luxurious fleet of conveyances, and flourishing estates."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: படிப்பில் தடைகள், தாயாரின் நரம்பு மண்டலம் பாதித்தல்.",
            "வீடு மற்றும் வாகனப் பராமரிப்புக்காக அதிக விரயங்கள், சொத்து ஆவணங்களில் மோசடிகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Disruptions in higher education, mother's nervous exhaustion, and forged property deeds.",
            "Repeated vehicle repair expenses, domestic anxiety, and insecure residential titles."
        ],
        "career_wealth_ta": [
            "கல்வி நிறுவனங்கள், மென்பொருள் பயிற்சி மையங்கள், வாகன உற்பத்தி மற்றும் விற்பனை, ரியல் எஸ்டேட் ஆவண ஆலோசகர், நூலகத் துறை.",
            "கல்வி சேவைகளாலும் நில ஆவண தரகு மூலமும் அளப்பரிய வருமானம்."
        ],
        "career_wealth_en": [
            "Flourishes in university administration, ed-tech startups, automotive dealership, title deed conveyancing, and libraries.",
            "Generates solid long-term equity through educational assets and commercial realty."
        ],
        "health_precautions_ta": [
            "நெஞ்சு சளி, இருதய நரம்பு பலவீனம், ஆஸ்துமா மற்றும் மன அமைதியின்மை.",
            "பிராணாயாமம், சுத்தமான காற்று மற்றும் எளிதில் செரிக்கும் காய்கறிகள் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to pulmonary spasms, intercostal neuralgia, bronchial asthma, and hyperactive anxiety.",
            "Breath control exercises and dwelling in well-ventilated, green environments promote longevity."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (மகா மேதை / மந்திர சித்தி & புத்தி)",
        "house_title_en": "5th House - Putra Bhava (Genius Intellect, Mantra Siddhi & Speculation)",
        "core_traits_ta": [
            "அசாத்தியமான புத்திக்கூர்மை, நுட்பமான தர்க்க அறிவு மற்றும் எதிர்காலத்தைக் கணிக்கும் உள்ளுணர்வு.",
            "அறிவார்ந்த, கலை உணர்வுள்ள மற்றும் நல்லொழுக்கம் நிறைந்த குழந்தைகள் அமைவார்கள்.",
            "மந்திர சாஸ்திரங்கள், வேதங்கள், சமஸ்கிருதம் மற்றும் நவீன அறிவியல் ஆய்வுகளில் தேர்ச்சி.",
            "பங்குச் சந்தை, கணித மாதிரிகள் மற்றும் திட்டமிடல் மூலம் துல்லியமாக கணித்துச் சாதிக்கும் ஆற்றல்."
        ],
        "core_traits_en": [
            "Genius-level deductive intellect, deep mathematical modeling skills, and prophetic foresight.",
            "Blessed with witty, intellectually accomplished, and morally upright children.",
            "Mastery over sacred mantras, esoteric scriptures, linguistics, and cutting-edge data science.",
            "Exceptional forecasting ability in financial markets, options algorithms, and strategic gaming."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் ஆட்சி அல்லது உச்சம் பெற்றால்: அமைச்சர்களுக்கு முதன்மை ஆலோசகர், நோபல் பரிசு அளவிலான சாதனைகள்.",
            "பூர்வ புண்ணிய பலத்தால் எடுத்த முயற்சிகள் யாவும் பல்கிப் பெருகி கோடிக்கணக்கில் தன லாபம் தரும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Chief cabinet strategist, internationally decorated academic pioneer.",
            "Past-life merits unlock frictionless intellectual breakthroughs and colossal financial windfalls."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: குழந்தைகளின் நரம்பு மண்டலம் பாதித்தல், கல்வியில் மந்த நிலை.",
            "பங்கு வர்த்தகத்தில் தவறான கணக்குகளால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Cognitive fatigue in children, learning disabilities in offspring.",
            "Disastrous financial bleedings caused by erratic speculative gambling and flawed algorithms."
        ],
        "career_wealth_ta": [
            "டேட்டா சயின்டிஸ்ட், செயற்கை நுண்ணறிவு (AI) ஆய்வாளர், பங்குச் சந்தை ஃபண்ட் மேனேஜர், நாடக ஆசிரியர், ஜோதிட ஆராய்ச்சியாளர்.",
            "அறிவுசார் படைப்புகளாலும் துல்லியமான முதலீடுகளாலும் கோடீஸ்வர யோகம்."
        ],
        "career_wealth_en": [
            "Distinction as quantitative fund manager, AI algorithm architect, playwright, data scientist, and astrological scholar.",
            "Reaps monumental fortunes through proprietary patents, copyrights, and algorithmic trading."
        ],
        "health_precautions_ta": [
            "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் நரம்பு பலவீனம் மற்றும் தலைவலி.",
            "சரியான நேரத்திற்கு எளிமையான உணவை உண்பதும், அதிக மன உளைச்சலைத் தவிர்ப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to nervous dyspepsia, gastrointestinal bloating, irritable bowel syndrome, and tension headaches.",
            "Maintain timely meals, avoid intellectual burnout, and consume gut-soothing herbal teas."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (சாதுரியத்தால் எதிரிகளை வெல்லுதல்)",
        "house_title_en": "6th House - Satru Bhava (Defeating Adversaries Through Wit)",
        "core_traits_ta": [
            "புத்தி சாதுரியத்தாலும், பேச்சுத் திறனாலும் எதிரிகளையும் போட்டியாளர்களையும் எளிதில் வீழ்த்துவார்.",
            "வழக்குகளிலும் சட்டப் போராட்டங்களிலும் தர்க்க வாதங்களை முன்வைத்து வெற்றி வாகை சூடுவார்.",
            "கடுமையான உழைப்பாளி; கணக்கு வழக்குகளையும் அலுவலகப் பணிகளையும் துல்லியமாக நிர்வகிப்பார்.",
            "தாய்மாமனுடன் நல்ல நட்பும் வணிகத் தொடர்புகளும் கொண்டிருப்பார்."
        ],
        "core_traits_en": [
            "Subdues competitors and legal adversaries through tactical intellectual maneuver rather than blunt force.",
            "Triumphs decisively in complex litigations and arbitration through razor-sharp analytical arguments.",
            "Meticulous, tireless worker with unmatched precision in administrative ledgering.",
            "Enjoys fruitful commercial collaborations and mutual goodwill with maternal relatives."
        ],
        "strong_placement_ta": [
            "கன்னியில் உச்சம் பெற்று சுப பலத்துடன் இருப்பின்: எதிரிகள் இல்லாத பெருவாழ்வு, நிதி மோசடிகளைக் கண்டறியும் உயர் பதவி.",
            "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் சமூகத்தில் உயர்ந்த மரியாதை."
        ],
        "strong_placement_en": [
            "Exalted in Virgo with benefics: Total eradication of adversaries; heads anti-corruption/forensic regulatory agencies.",
            "Vast accumulated capital, completely debt-free living, and unassailable civic respect."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தோல் அலர்ஜி, நரம்புத் தளர்ச்சி, கடன்களால் மன உளைச்சல்.",
            "வேலையாட்களால் கணக்குத் தில்லுமுல்லுகள் மற்றும் தாய்மாமனுடன் கருத்து மோதல்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Chronic dermatological rashes, nervous twitching, and anxiety over unsettled debts.",
            "Embezzlement by untrustworthy accountants or clerks; disputes with maternal uncles."
        ],
        "career_wealth_ta": [
            "சட்டத்துறை, தணிக்கை மற்றும் வரி ஆலோசகர் (Tax Consultant), மருத்துவப் பரிசோதனையாளர், வங்கியாளர், பொது நிர்வாகம்.",
            "போட்டிகளைத் தனக்குச் சாதகமாக மாற்றி வணிக லாபங்களை ஈட்டுவார்."
        ],
        "career_wealth_en": [
            "Excels in corporate taxation, forensic accounting, clinical pathology, banking risk management, and labor arbitration.",
            "Turns competitor blunders into handsome commercial windfalls."
        ],
        "health_precautions_ta": [
            "குடல் அழற்சி, நரம்புத் தளர்ச்சி, சரும நோய்கள், ஆஸ்துமா மற்றும் மலச்சிக்கல்.",
            "நார்ச்சத்து மிகுந்த காய்கறிகளையும் பழங்களையும் உண்பதும், தோலை சுத்தமாகப் பராமரிப்பதும் நலம் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to colitis, nervous exhaustion, eczema, bronchial allergies, and chronic constipation.",
            "High-fiber dietary regimen, probiotics, and dermatological care are essential."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (அறிவார்ந்த துணை & வர்த்தகக் கூட்டாண்மை)",
        "house_title_en": "7th House - Kalathra Bhava (Erudite Spouse & Commercial Alliances)",
        "core_traits_ta": [
            "அழகான, அறிவார்ந்த, பேச்சாற்றலும் வணிக ஞானமும் நிறைந்த வாழ்க்கைத் துணை அமைவார்.",
            "தம்பதியரிடையே அறிவுசார் உரையாடல்களும், நகைச்சுவையும், பரஸ்பர மரியாதையும் நிறைந்திருக்கும்.",
            "கூட்டு வர்த்தகத்தில் (Partnership) அளப்பரிய வெற்றி; ஒப்பந்தங்களை நேர்த்தியாக முடிக்கும் சாதுரியம்.",
            "பொதுமக்கள் தொடர்பிலும் தூதரகப் பணிகளிலும் சிறந்த நற்பெயரையும் செல்வாக்கையும் பெறுவார்."
        ],
        "core_traits_en": [
            "Blessed with a charming, intellectually brilliant, articulate, and commercially astute spouse.",
            "Marital life sparkles with witty repartee, shared literary pursuits, and deep intellectual companionship.",
            "Sensational success in commercial partnerships; negotiates joint contracts with masterly finesse.",
            "Natural diplomat in public interactions, arbitration boards, and overseas commercial consortia."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற செல்வந்த குடும்பத்திலிருந்து அறிவுக்களஞ்சியமான துணை அமைவார்.",
            "பன்னாட்டு வர்த்தகத்தில் பெரும் லாபமும், சமூகத்தில் சிறந்த தம்பதியராகப் போற்றப்படும் நிலையும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted or own house: Marries into a prominent, scholarly, and affluent dynasty; partner contributes directly to business expansion.",
            "Reaps huge fortunes from transnational trade agreements and commands widespread civic respect."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமணத்தில் காலதாமதம், துணையுடன் வாக்குவாதங்கள்.",
            "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஒப்பந்த மீறல்கள் மற்றும் பண இழப்புகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Delay in marital union, intellectual disputes causing domestic estrangement.",
            "Breach of contract by commercial partners resulting in arbitration costs and capital loss."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், ஏற்றுமதி-இறக்குமதி, மக்கள் தொடர்பு மேலாண்மை, சட்ட ஒப்பந்தங்கள், விநியோகஸ்தர் ஏஜென்சி.",
            "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் கூட்டுத் தொழிலாலும் தன வரவு பலமடங்கு உயரும்."
        ],
        "career_wealth_en": [
            "Dominant in cross-border trade, import-export logistics, public relations, corporate contract law, and retail distribution.",
            "Vast wealth multiplication achieved via spousal counsel and well-structured joint ventures."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், நரம்புத் தளர்ச்சி, அடிவயிற்றில் வலி மற்றும் தோல் அரிப்பு.",
            "முறையான நீர் அருந்துதலும், நரம்புகளைத் தளர்வாக்கும் பயிற்சிகளும் ஆரோக்கியத்திற்கு உதவும்."
        ],
        "health_precautions_en": [
            "Vulnerable to renal sensitivity, pelvic nervous strain, urinary irritation, and skin rashes.",
            "Abundant hydration and routine pelvic floor relaxation maintain health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (தீர்க்காயுள் / மறைமுக ஞானம் & உயில் தனம்)",
        "house_title_en": "8th House - Ayur Bhava (Long Longevity, Occult Lore & Legacies)",
        "core_traits_ta": [
            "புதன் 8-ஆம் பாவத்தில் அமர்வது நீண்ட ஆயுளையும், எதிர்பாராத அதிர்ஷ்டங்களையும் தரும் அமைப்பாகும்.",
            "ரகசிய சாஸ்திரங்கள், ஜோதிடம், குறியீட்டு முறைகள் (Cryptography) மற்றும் மறைமுக உண்மைகளை ஆராய்வதில் வல்லவர்.",
            "ஆபத்தான சூழ்நிலைகளிலும் தன் சாதுரியமான பேச்சால் தப்பிக்கும் விவேகம் கொண்டவர்.",
            "அரசாங்கத் தணிக்கைகள் அல்லது ஒப்பந்த ஆவணங்களில் மிகுந்த எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
        ],
        "core_traits_en": [
            "Mercury in the 8th is a classical guarantor of extended longevity and sudden unexpected windfalls.",
            "Profound mastery over esoteric symbology, cryptographic coding, astrology, and forensic research.",
            "Escapes precarious dangers using razor-sharp presence of mind and persuasive diplomacy.",
            "Must maintain impeccable transparency in statutory filings and signed contractual documentation."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: மாபெரும் உயில் சொத்துகள், காப்பீட்டுத் தொகைகள், பூரண தீர்க்காயுள்.",
            "மறைமுகத் தொழில் மூலம் கோடிக்கணக்கில் வருமானம் மற்றும் உலகப் புகழ் பெற்ற ஆராய்ச்சியாளராகத் திகழுதல்."
        ],
        "strong_placement_en": [
            "Strong or exalted: Bestows massive ancestral bequests, life insurance endowments, and robust long life.",
            "Monetizes proprietary data analytics and covert algorithms into immense confidential wealth."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நரம்புத் தளர்ச்சி, மூளை சோர்வு, கண் உபாதைகள்.",
            "பங்கு வர்த்தகத்தில் திடீர் சரிவுகள், ஏமாற்றங்கள் மற்றும் உயில் விவகாரங்களில் வழக்குகள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Nervous exhaustion, brain fog, chronic insomnia, and speech stammers under pressure.",
            "Sudden market crashes eroding speculative gains; protracted probate litigations."
        ],
        "career_wealth_ta": [
            "தடயவியல் கணக்காளர், சைபர் செக்யூரிட்டி நிபுணர், உளவுத்துறை பகுப்பாய்வாளர், இன்சூரன்ஸ் தணிக்கையாளர், காப்புரிமை வழக்கறிஞர்.",
            "உயில் சொத்துகள், திடீர் டிவிடெண்டுகள் மற்றும் மறைமுக ஒப்பந்தங்கள் மூலம் தன வரவு."
        ],
        "career_wealth_en": [
            "Eminence in forensic audit, cybersecurity encryption, intelligence analytics, insurance claims, and patent law.",
            "Gains unearned wealth through inheritances, court settlements, and confidential contracts."
        ],
        "health_precautions_ta": [
            "நரம்புத் தளர்ச்சி, மன அழுத்தம், பக்கவாதம் அபாயம், செரிமானக் கோளாறுகள் மற்றும் மலச்சிக்கல்.",
            "தியானம், நல்ல தூக்கம் மற்றும் நரம்புகளை அமைதிப்படுத்தும் ஊட்டச்சத்துகள் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to nervous breakdown, peripheral neuropathy, cognitive burnout, and sluggish bowels.",
            "Requires calming meditation, sound sleep hygiene, and B-complex vitamin supplementation."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம சிந்தனை, உயர்கல்வி & குருவருள்)",
        "house_title_en": "9th House - Bhagya Bhava (Righteous Wisdom, Higher Learning & Guru's Grace)",
        "core_traits_ta": [
            "உன்னதமான தர்ம சிந்தனை, தத்துவ ஞானம், பக்தி மற்றும் பெரியோர்களை மதிக்கும் நற்பண்புகள்.",
            "தந்தையின் மீது பாசமும், தந்தை வழியில் சிறந்த அறிவுரைகளும் வழிகாட்டல்களும் கிட்டும்.",
            "வெளிநாட்டுப் பல்கலைக்கழகங்களில் கல்வி பயிலும் யோகம் மற்றும் பன்னாட்டு ஆய்வுகளில் வெற்றி.",
            "மத நல்லிணக்கம், ஆன்மீக நூல்களை எழுதுதல் மற்றும் சமுதாயத்திற்கு நல்ல கருத்துகளைப் போதிக்கும் ஆற்றல்."
        ],
        "core_traits_en": [
            "Sublime ethical nobility, deep philosophical learning, pious devotion, and reverent mentorship.",
            "Harmonious, inspiring relationship with an intellectual father whose counsel guides life choices.",
            "High fortune in gaining admission to premier global universities and spearheading cross-border studies.",
            "Promotes interfaith harmony, publishes spiritual treatises, and inspires seekers through lucid discourse."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட பாக்கிய யோகம், அரசாங்க சர்வதேசத் தூதர், உலகளாவிய கௌரவம்.",
            "நிறுவனங்களைத் தோற்றுவித்து சர்வதேச அளவில் பல்லாயிரக்கணக்கான மாணவர்களுக்குக் கல்வி புகட்டும் சாதனை."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows supreme Bhagya Yoga; appointed as international ambassador or cultural delegate.",
            "Founds global academic institutions and chairs worldwide philanthropic educational endowments."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உயர்கல்வியில் தடைகள், தந்தையின் நரம்பு ஆரோக்கியம் பாதித்தல்.",
            "மத விஷயங்களில் வீண் வாதங்கள், வெளிநாட்டுப் பயணங்களில் ஆவணக் குறைபாடுகளால் இழப்புகள்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Academic disruptions in postgraduate studies, paternal nervous frailty.",
            "Futile ideological arguments and costly visa or documentation delays during international travel."
        ],
        "career_wealth_ta": [
            "பல்கலைக்கழகப் பேராசிரியர், சர்வதேசச் சட்ட ஆலோசகர், மத அறக்கட்டளைத் தலைவர், பதிப்பக அதிபர், ஆன்மீக எழுத்தாளர்.",
            "கல்வி, தர்ம வழிகள் மற்றும் பன்னாட்டு அறிவுசார் பரிமாற்றங்கள் மூலம் கோடீஸ்வர யோகம்."
        ],
        "career_wealth_en": [
            "Distinguished as university chair professor, international legal jurist, publishing conglomerate executive, and author.",
            "Amasses pure, untainted wealth through educational licensing and intellectual cross-border initiatives."
        ],
        "health_precautions_ta": [
            "தொடை நரம்பு வலி (Sciatica), இடுப்புப் பிடிப்பு, கல்லீரல் மந்தம் மற்றும் உடல் சோர்வு.",
            "முறையான நடைப்பயிற்சியும், உடலை வளைக்கும் ஆசனங்களும் ஆரோக்கியம் தரும்."
        ],
        "health_precautions_en": [
            "Susceptible to femoral neuropathy, sciatica sensitivity, sluggish hepatic bile, and fatigue.",
            "Daily stretching routines and brisk walking optimize lower extremity nerve vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (வர்த்தக சாம்ராஜ்யம் & தொழில் வெற்றி)",
        "house_title_en": "10th House - Karma Bhava (Commercial Empire & Professional Glory)",
        "core_traits_ta": [
            "வணிகத்தில் அசுர வேகம், தொழில் மேலாண்மை மற்றும் பல துறைகளில் ஒரே நேரத்தில் வெற்றிபெறும் ஆற்றல்.",
            "அரசாங்க உயர் அதிகாரிகளுடனும் தொழில் அதிபர்களுடனும் சுமுகமான நட்பும் செல்வாக்கும்.",
            "நேர்மையான நிர்வாகம், புதுமையான தொழில் யுக்திகள் மற்றும் பல்லாயிரக்கணக்கானோரை வழிநடத்தும் திறன்.",
            "சமூகத்தில் பெரும் புகழும், கௌரவப் பட்டங்களும், அழியாத தொழில் முத்திரையும் பெறுவார்."
        ],
        "core_traits_en": [
            "Dynamic commercial acumen, masterly enterprise leadership, and effortless multitasking across diverse ventures.",
            "Commands high respect and lucrative patronage among top governmental regulators and industrialists.",
            "Ethical administrative governance combined with cutting-edge innovations; natural corporate leader.",
            "Crowns life with enduring public renown, honorary academic doctorates, and celebrated institutional status."
        ],
        "strong_placement_ta": [
            "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் அமைந்தால்: நாட்டின் முன்னணி வர்த்தக சாம்ராஜ்ய அதிபர், நிதி மந்திரி யோகம்.",
            "பன்னாட்டு மென்பொருள் மற்றும் ஊடக நிறுவனங்களின் தலைவர் அந்தஸ்து மற்றும் அரச கௌரவம்."
        ],
        "strong_placement_en": [
            "Exalted or own house with Bhadra Yoga: Titan of national commerce, finance minister or central bank governor.",
            "Chairman of multinational software conglomerates and recipient of peak civic decorations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், தவறான கணக்கு வழக்குகளால் தணிக்கைச் சிக்கல்கள்.",
            "உயர் அதிகாரிகளால் நெருக்கடிகளும், வியாபாரத்தில் வாடிக்கையாளர் நம்பிக்கையை இழத்தலும்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Frequent erratic job switches, accounting discrepancies leading to tax audits.",
            "Regulatory sanctions, sudden commercial setbacks, and erosion of consumer brand trust."
        ],
        "career_wealth_ta": [
            "தகவல் தொழில்நுட்பம், வங்கித் தலைமை, ஊடக நிறுவனம், பங்குச் சந்தை தரகு நிறுவனம், ஆடிட்டிங் நிறுவனம், ஆட்டோமொபைல் மார்க்கெட்டிங்.",
            "தொழில் சாதுரியத்தாலும் வர்த்தக விரிவாக்கத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Dominant in IT software services, investment banking, media networks, audit practices, and global marketing.",
            "Multi-million dollar liquid fortunes accumulated through scalable high-margin commercial expansion."
        ],
        "health_precautions_ta": [
            "மூட்டு வலி, பணிச்சுமையால் நரம்புத் தளர்ச்சி, தூக்கமின்மை மற்றும் தோள்பட்டை இறுக்கம்.",
            "வேலைக்கு நடுவே ஓய்வும், முறையான தூக்கமும் உடல்நலனைப் பாதுகாக்கும்."
        ],
        "health_precautions_en": [
            "Vulnerable to knee osteoarthritis, occupational nervous exhaustion, insomnia, and neck spasms.",
            "Disciplined work-life boundaries and structured sleep schedules preserve vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் & அறிவுசார் வருவாய்)",
        "house_title_en": "11th House - Labha Bhava (Massive Liquid Gains & Intellectual Inflows)",
        "core_traits_ta": [
            "புதன் 11-ஆம் பாவத்தில் அமைவது தொட்டதெல்லாம் பொன்னாகும் தன லாபத்தைத் தரும் மிகச் சிறந்த யோகமாகும்.",
            "குறைந்த முதலீட்டில் பல மடங்கு லாபம் ஈட்டும் வணிகச் சாதுரியம்; ஆசைகள் அனைத்தும் எளிதில் நிறைவேறும்.",
            "அறிவார்ந்த நண்பர்கள், எழுத்தாளர்கள், தொழில் அதிபர்களின் விரிவான நட்பு வட்டம் அமையும்.",
            "மூத்த சகோதரர்களிடம் நல்ல தோழமையும், அவர்களுடன் இணைந்து வணிகம் செய்து முன்னேறும் யோகமும் உண்டு."
        ],
        "core_traits_en": [
            "Mercury in the 11th is a peerless generator of exponential financial profit and compounding wealth.",
            "Extraordinary skill in multiplying capital with lean overheads; swift realization of long-term aspirations.",
            "Surrounded by a stellar network of erudite friends, venture capitalists, authors, and industry pioneers.",
            "Harmonious camaraderie with elder siblings, often partnering with them on lucrative intellectual enterprises."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், நவீன பங்களாக்கள், ஆடம்பர வாழ்க்கை.",
            "பங்கு வர்த்தகம், தகவல் தொழில்நுட்பம் மற்றும் முதலீட்டு நிறுவனங்களில் மாபெரும் முதலீட்டாளராக உயருதல்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows unceasing multichannel cash flows, premier residential estates, and luxury assets.",
            "Rises as a celebrated venture angel investor in tech unicorns, equities, and media companies."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்படுதல், எதிர்பார்க்கும் தரகுத் தொகைகள் கைநழுவுதல்.",
            "மூத்த சகோதரருடன் சொத்துத் தகராறுகள் அல்லது பிரிவுகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by counterfeit associates, delayed commissions, and unpaid invoices.",
            "Estrangement or legal disputes with elder brother over commercial division of assets."
        ],
        "career_wealth_ta": [
            "வென்ச்சர் கேபிடல், பங்குச் சந்தை அல்காரிதம், கமிஷன் ஏஜென்சி, ஈ-காமர்ஸ், டிஜிட்டல் தளங்கள், மென்பொருள் உரிமங்கள்.",
            "புத்தி சாதுரியத்தாலும் முதலீட்டுப் பெருக்கத்தாலும் கோடீஸ்வர அந்தஸ்து."
        ],
        "career_wealth_en": [
            "Lucrative success in venture funds, algorithmic equity trading, e-commerce networks, and software licensing.",
            "Vast fortune generated from automated royalties and digital asset platforms."
        ],
        "health_precautions_ta": [
            "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், கைகளில் நடுக்கம் மற்றும் தோல் அரிப்பு.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear ache, ankle ligament stiffness, hand tremors, and skin itching.",
            "Daily ankle mobility drills and preventive otic hygiene keep limbs supple."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அயன சயனம், வெளிநாட்டு யோகம் & ஆன்மீகம்)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Foreign Success, Solitude & Deep Research)",
        "core_traits_ta": [
            "தனிமையில் அமர்ந்து ஆழ்ந்த ஆராய்ச்சி செய்வதிலும், எழுதுவதிலும், தியானிப்பதிலும் பேரானந்தம் அடைவார்.",
            "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அபரிமிதமான வெற்றியும் புகழும் கிட்டும்.",
            "பணத்தை கல்வி நிறுவனங்கள், புத்தகங்கள் மற்றும் தர்ம காரியங்களுக்காக தாராளமாகச் செலவிடுவார்.",
            "அரசாங்க வரி விவகாரங்களிலும் சட்ட ஆவணங்களிலும் எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
        ],
        "core_traits_en": [
            "Finds profound creative joy in tranquil solitude, deep scholarly research, philosophical writing, and meditation.",
            "Realizes spectacular career elevation and wealth when operating in distant overseas lands.",
            "Spends generously on educational charities, esoteric books, philanthropic trusts, and scholastic scholarships.",
            "Must practice diligence in tax compliance, offshore accounting, and signed statutory filings."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் கல்வி சாம்ராஜ்யம், சர்வதேச தூதரகம், மோட்ச சாதனை.",
            "அயன சயன சுகம், நல்ல தூக்கம் மற்றும் வெளிநாட்டு நாணயங்கள் மூலம் அளப்பரிய தன வரவு."
        ],
        "strong_placement_en": [
            "Well-placed with benefics: Vast academic or IT operations abroad, international diplomacy, and spiritual illumination.",
            "Enjoys restorative sleep, psychic balance, and tremendous income denominated in strong foreign currencies."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தூக்கமின்மை, நரம்புத் தளர்ச்சி, தவறான ஆவணங்களால் அபராதங்கள்.",
            "இடது கண் பார்வைக் குறைபாடு, மனக் குழப்பம் மற்றும் வீண் மருத்துவச் செலவுகள்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe insomnia, nervous anxiety, and penalties incurred from forged or flawed papers.",
            "Left eye vision defects, mental disorientation, and burdensome clinical expenses."
        ],
        "career_wealth_ta": [
            "சர்வதேச மென்பொருள் ஏற்றுமதி, வெளிநாட்டுத் தூதரகங்கள், சர்வதேச கப்பல் மற்றும் வான்வழி சரக்கு, மொழிபெயர்ப்பாளர், ஆன்மீக நூலகங்கள்.",
            "அந்நிய முதலீடுகளாலும் பன்னாட்டு நிறுவனங்களின் மூலமும் தொடர் தன வரவு."
        ],
        "career_wealth_en": [
            "Thrives in cross-border software export, consular services, aviation cargo, technical translation, and overseas research.",
            "Accumulates substantial wealth through foreign currency reserves and offshore contracts."
        ],
        "health_precautions_ta": [
            "இடது கண் பார்வை பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை மற்றும் தோல் வியாதிகள்.",
            "படுக்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், தியானமும் மன அமைதியைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye refractive strain, peripheral foot neuropathy, insomnia, and dermatological rashes.",
            "Nightly ocular cold-compresses and grounding meditation induce deep restorative sleep."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

JUPITER_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (திக்பலம் / ஹம்ச யோகம் / மகா ஞானம்)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Digbala / Hamsa Yoga / Supreme Wisdom)",
        "core_traits_ta": [
            "குரு லக்னத்தில் திக்பலம் (Digbala) பெற்று அமர்வது கோடி நன்மைகளைத் தரும் மகா புண்ணிய அமைப்பாகும்.",
            "கம்பீரமான, வசீகரமான, தங்க நிற மேனி, பரந்த நெற்றி மற்றும் தெய்வீகக் களை பொருந்திய அழகிய முகம்.",
            "அசைக்க முடியாத தன்னம்பிக்கை, நேர்மை, உயர்ந்த ஒழுக்கம் மற்றும் சுயமரியாதைக்கு முதலிடம் தரும் சுபாவம்.",
            "ஆன்மீகம், வேதம், சட்டம் மற்றும் மெய்யியலில் ஆழ்ந்த ஞானம்; சமுதாயத்தின் உன்னத வழிகாட்டியாகத் திகழ்வார்.",
            "எந்தப் பாப தோஷங்களையும் போக்கும் ஆற்றல்; ஒரு லட்சம் தோஷங்களை நிவர்த்தி செய்யும் தேவ குருவின் நேரடி பார்வை."
        ],
        "core_traits_en": [
            "Jupiter achieves supreme Digbala (directional potency) in the 1st house; celebrated as canceling a hundred thousand chart flaws.",
            "Noble, majestic, and commanding physical presence; golden aura, broad forehead, and radiant countenance.",
            "Unshakeable self-confidence, uncompromising righteousness, spotless moral integrity, and high personal dignity.",
            "Mastery of theology, jurisprudence, statecraft, and higher philosophy; natural statesman and preceptor.",
            "Radiates benign spiritual protection, uplifting everyone who comes into his orbit."
        ],
        "strong_placement_ta": [
            "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் (Hamsa Yoga) அமைந்தால்: நாட்டின் தலைமை நீதிபதி, ஜனாதிபதி, ஜகத்குரு யோகம்.",
            "வாழ்நாள் முழுவதும் குறைவற்ற செல்வம், உலகெங்கும் சீடர்கள் மற்றும் சரித்திரத்தில் அழியாத பொற்பெயர்."
        ],
        "strong_placement_en": [
            "Exalted in Cancer or in own signs Sagittarius/Pisces forming Hamsa Mahapurusha Yoga: Chief Justice, Prime Minister, World Spiritual Preceptor.",
            "Enduring multi-generational wealth, millions of devoted followers, and golden historical immortality."
        ],
        "weak_placement_ta": [
            "மகரத்தில் நீசம் அல்லது ராகுவின் சேர்க்கை (குரு சண்டாள யோகம்) பெற்றால்: உடல் பருமன், கல்லீரல் பாதிப்பு, மத நம்பிக்கைகளில் குழப்பம்.",
            "அளவுக்கு மீறிய நம்பிக்கை வைத்து ஏமாறுதல் அல்லது கௌரவக் குறைவுகள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Capricorn or conjunct Rahu (Guru Chandala Yoga): Severe obesity, hepatic imbalances, and doctrinal disillusionment.",
            "Vulnerability to exploitation through naive credulity; occasional setbacks to public prestige."
        ],
        "career_wealth_ta": [
            "தலைமை நீதிபதி, சட்ட வல்லுநர், பல்கலைக்கழக வேந்தர், மத்திய மந்திரி, சர்வதேச நிதி ஆலோசகர், ஆன்மீக பீடாதிபதி.",
            "அரசாங்க விருதுகள், கௌரவப் பதவிகள் மற்றும் தர்ம வழியில் கோடிக்கணக்கான சொத்துச் சேர்க்கை."
        ],
        "career_wealth_en": [
            "Peerless career as supreme appellate judge, constitutional luminary, university chancellor, cabinet minister, and pontiff.",
            "Amasses vast, clean wealth through state patronage, high consultancy, and ethical leadership."
        ],
        "health_precautions_ta": [
            "உடல் பருமன் (Obesity), கல்லீரல் கொழுப்பு (Fatty Liver), நீரிழிவு நோய் (Diabetes) மற்றும் ரத்தக் கொதிப்பு.",
            "மிதமான சாத்வீக உணவுகளும், சர்க்கரையைக் கட்டுப்படுத்துவதும், தினசரி நடைப்பயிற்சியும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to metabolic obesity, hepatic steatosis (fatty liver), diabetes mellitus, and high triglycerides.",
            "Adhere to a low-glycemic sattvic diet, eliminate refined sugars, and maintain daily brisk walking."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (வாக்கு பலிதம், அகண்ட தனம் & குடும்ப நலம்)",
        "house_title_en": "2nd House - Dhana Bhava (Prophetic Speech & Boundless Wealth)",
        "core_traits_ta": [
            "குரு 2-ஆம் பாவத்தில் அமர்வது வாக்கு பலிதம், சிறந்த கல்வியறிவு மற்றும் அளப்பரிய குடும்ப மகிழ்ச்சியைத் தரும்.",
            "கனிவான, கம்பீரமான மற்றும் கேட்போரை மெய்சிலிர்க்க வைக்கும் தெய்வீகப் பேச்சாற்றல்.",
            "பணத்தை தர்ம வழியில் ஈட்டி பல மடங்காகப் பெருக்கும் பொருளாதாரச் சாதுரியம்.",
            "பெரிய குடும்பம், நற்குணமுள்ள உறவினர்கள் மற்றும் அனைவராலும் மதிக்கப்படும் குடும்பப் பாரம்பரியம்."
        ],
        "core_traits_en": [
            "Jupiter in the 2nd is an illustrious harbinger of prophetic truth in speech, vast learning, and domestic felicity.",
            "Commands a majestic, resonant, and inspiring tone that commands instant silence and reverence.",
            "Accumulates abundant capital through righteous channels and multiplies assets through ethical investment.",
            "Enjoys a large, harmonious family circle rooted in prestigious ancestral lineage."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: குபேர யோகம்! வற்றாத தங்கக் கையிருப்பு, பல நூறு கோடி சொத்துகள், வாக்கு பலிதம்.",
            "குடும்பத்தில் அனைவரும் கல்வியாளர்களாகவும் செல்வந்தர்களாகவும் திகழ்ந்து குலப் பெருமையைக் காப்பார்கள்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows Kubera Yoga! Immense reserves of gold bullion, multi-million dollar liquidity, and infallible speech.",
            "Family lineage thrives with generational scholars, philanthropists, and dignified community leaders."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தவறான முதலீடுகளால் தன இழப்பு, குடும்பத்தில் முரண்பாடுகள்.",
            "பற்களில் நோய், வாய் துர்நாற்றம் அல்லது தொண்டையில் கட்டிகள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Financial hemorrhaging through misplaced altruism, domestic disputes, and speech harshness.",
            "Susceptible to dental caries, oral lesions, and chronic thyroid/throat inflammations."
        ],
        "career_wealth_ta": [
            "வங்கி அதிபர், நிதி அமைச்சகம், நீதித்துறை, பெரிய கல்வி நிறுவனங்கள், தங்க/நகை வர்த்தகம், அறக்கட்டளைகள்.",
            "வாக்கு பலிதத்தாலும் நிதி மேலாண்மையாலும் தலைமுறை தலைமுறைக்கும் அழியாத செல்வம்."
        ],
        "career_wealth_en": [
            "Superlative success in banking chairmanships, ministry of finance, judiciary, university trusts, and bullion commerce.",
            "Creates generational wealth through visionary stewardship and prudent asset preservation."
        ],
        "health_precautions_ta": [
            "தொண்டை சதை வளர்ச்சி, தைராய்டு கோளாறுகள், நாக்கில் புண்கள் மற்றும் பல் வியாதிகள்.",
            "உப்பு கலந்த வெதுவெதுப்பான நீரால் தொண்டையை கொப்பளிப்பதும், இனிப்புகளைக் குறைப்பதும் நல்லது."
        ],
        "health_precautions_en": [
            "Vulnerable to thyroid dysfunctions, tonsillar hypertrophy, oral ulcers, and dental decay.",
            "Warm saline gargling, minimal processed sugar intake, and annual dental checkups are advised."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (தர்ம தைரியம் & சகோதர ஆசி)",
        "house_title_en": "3rd House - Sahaja Bhava (Righteous Fortitude & Sibling Goodwill)",
        "core_traits_ta": [
            "அமைதியான, உறுதியான மனத்துணிச்சல்; அநீதிக்கு எதிராக தர்ம வழியில் போராடும் குணம்.",
            "சகோதர சகோதரிகளிடம் அதிக அன்பும், அவர்களுக்குத் தேவையான அறிவுரைகளையும் உதவிகளையும் செய்யும் வழிகாட்டியாகத் திகழ்வார்.",
            "உன்னதமான எழுத்தாற்றல், ஆன்மீக தத்துவங்களை எளிய நடையில் விளக்கும் சொல்வளம்.",
            "தீர்த்த யாத்திரைகள், ஆன்மீகப் பயணங்கள் மற்றும் புனித நதிகளில் நீராடுவதில் மிகுந்த ஈடுபாடு உண்டு."
        ],
        "core_traits_en": [
            "Calm, steadfast fortitude; champions righteousness through intellectual conviction and moral authority.",
            "Devoted guardian and mentor to siblings, extending paternal guidance and material support.",
            "Distinguished literary prose; translates complex metaphysical treatises into lucid, inspiring literature.",
            "Deep affinity for pilgrimages, visiting ancient hermits, and bathing in sanctified river confluences."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ்பெற்ற ஆன்மீக எழுத்தாளர், தத்துவ மாமேதை, சகோதரர்களால் பெரும் மேன்மை.",
            "எடுத்த காரியங்கள் அனைத்திலும் தெய்வீக வெற்றி; எந்த முயற்சியிலும் தோல்வியைத் தழுவாத நிலை."
        ],
        "strong_placement_en": [
            "Strong or exalted: Internationally celebrated metaphysical author, philosophical savant, and proud brothers.",
            "Divine grace crowns all initiatives with triumphant fruition; shielded against worldly failure."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் வலி.",
            "முயற்சிகளில் காலதாமதம் மற்றும் தேவையில்லாத சந்தேகங்களால் மன சோர்வு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Strained relations with brothers, fatigue in arms, and lack of decisive enterprise.",
            "Pessimistic procrastination hindering literary and commercial achievements."
        ],
        "career_wealth_ta": [
            "ஆன்மீக வெளியீட்டாளர், மத விரிவுரையாளர், உயர்நிலை தகவல் தொடர்பு, தத்துவ நூலாசிரியர், தொண்டு நிறுவனங்கள்.",
            "எழுத்து, அறிவுரை மற்றும் தர்ம காரியங்கள் மூலம் கௌரவமான செல்வச் சேர்க்கை."
        ],
        "career_wealth_en": [
            "Flourishes in spiritual publishing, ethical telecommunications, motivational lecturing, and charitable trusts.",
            "Honorable wealth gained through intellectual consulting, royalties, and philanthropic syndicates."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புப் பிடிப்பு, காதுகளில் மந்தம் மற்றும் தசை இறுக்கம்.",
            "முறையான யோகாசனங்களும், உடற்பயிற்சியும் உடலை ஆரோக்கியமாக வைத்திருக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to shoulder stiffness, upper arm neuralgia, auditory dullness, and muscular tension.",
            "Yogic asanas and gentle arm stretching optimize upper quadrant vitality."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (ஹம்ச யோகம் / பூரண சுகம், மாளிகைகள் & தாயன்பு)",
        "house_title_en": "4th House - Sukha Bhava (Hamsa Yoga / Mansions, Inner Peace & Mother's Grace)",
        "core_traits_ta": [
            "குரு 4-ஆம் பாவத்தில் அமர்வது அளவில்லாத மன நிம்மதி, குடும்ப சுகம் மற்றும் உயர் கல்வி யோகத்தைத் தரும்.",
            "தாய் வழியில் அளப்பரிய ஆசியும், தாயார் உன்னத ஆன்மீகப் பெண்ணாக விளங்கி நல்வழிகாட்டுவார்.",
            "பரந்த மாளிகைகள் போன்ற வீடு, நிலபுலன்கள், சொகுசு வாகனங்கள் மற்றும் அமைதியான இல்லற வாழ்க்கை.",
            "வீட்டில் எப்போதும் ஆன்மீகச் சூழல் நிலவும்; விருந்தினர்களுக்கு அன்னதானம் செய்வதில் பேரானந்தம் அடைவார்."
        ],
        "core_traits_en": [
            "Jupiter in the 4th generates profound inner tranquility, supreme domestic contentment, and scholastic distinction.",
            "Blessed by an exceptionally noble, virtuous mother who provides unconditional spiritual nurturing.",
            "Commands palatial residential estates, vast fertile lands, luxury conveyances, and serene domestic bliss.",
            "Home serves as a sanctuary for spiritual discourse, hospitable banquets, and continuous charitable feeding."
        ],
        "strong_placement_ta": [
            "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: அரண்மனை போன்ற வாழ்க்கை, பல்கலைக்கழகத் தலைமை.",
            "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, சமுதாயத்தில் மிக உயர்ந்த ஆன்மீகத் தலைவராகப் போற்றப்படுவார்."
        ],
        "strong_placement_en": [
            "Exalted in Cancer or own sign forming Hamsa Yoga: Princely residential compounds, university chancellor status.",
            "Garlanded with sovereign state honors, commanding reverence as a beacon of cultural wisdom."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் கல்லீரல் அல்லது உடல்நலம் பாதித்தல், பூர்வீக வீட்டை விட்டுப் பிரிதல்.",
            "வாகனங்களால் செலவுகள் மற்றும் சொத்து ஆவணங்களில் வில்லங்கங்கள் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Capricorn or afflicted: Maternal hepatic or cardiac ailments, estrangement from ancestral manor.",
            "Heavy financial drains on vehicular repairs and encumbrances on real estate titles."
        ],
        "career_wealth_ta": [
            "பல்கலைக்கழகங்கள், பெரிய கல்லூரிகள், விவசாயப் பண்ணைகள், ரியல் எஸ்டேட் வளர்ச்சி, ஆன்மீக மடங்கள், அரசு வாகனத் துறை.",
            "சொத்துகளின் மதிப்பு அபரிமிதமாக உயர்வதாலும் கல்விச் சேவைகளாலும் கோடிக்கணக்கில் தன வரவு."
        ],
        "career_wealth_en": [
            "Distinguished in university ownership, sprawling agro-farms, residential township development, and sacred ashrams.",
            "Colossal capital growth realized via real estate appreciation and educational foundations."
        ],
        "health_precautions_ta": [
            "இதயப் பகுதியில் கொழுப்பு படிதல், ரத்த அழுத்தம், கல்லீரல் வீக்கம் மற்றும் ஆஸ்துமா.",
            "கொழுப்புச் சத்துள்ள உணவுகளைக் குறைத்து, காய்கறிகளையும் பழங்களையும் அதிகமாக உண்பது நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Prone to coronary lipid plaque, hypertension, hepatic enlargement, and bronchial congestion.",
            "Adopt a strictly low-fat plant-based diet, schedule cardiovascular diagnostics, and avoid sedentary inertia."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (புத்திர பாக்கியம் / பிரம்ம ஞானம் & அதிர்ஷ்டம்)",
        "house_title_en": "5th House - Putra Bhava (Divine Progeny, Higher Wisdom & Serendipity)",
        "core_traits_ta": [
            "குரு 5-ஆம் பாவத்தில் (காரகோ பாவக நாஸ்தி விதிக்கு உட்படாமல் சுப பலத்துடன் இருந்தால்) மாபெரும் பூர்வ புண்ணிய யோகத்தைத் தரும்.",
            "அசாத்தியமான ஆன்மீக ஞானம், மந்திர சித்தி, தெய்வ கடாட்சம் மற்றும் கூர்மையான தொலைநோக்குப் பார்வை.",
            "சமுதாயத்தில் மிக உயர்ந்த அந்தஸ்தை அடையும் உன்னதமான, நல்லொழுக்கம் நிறைந்த புத்திரர்கள் அமைவார்கள்.",
            "எடுத்த காரியங்கள் அனைத்திலும் இறைவனின் கருணையால் எதிர்பாராத அதிர்ஷ்டங்களும் வெற்றிகளும் குவியும்."
        ],
        "core_traits_en": [
            "Jupiter in the 5th (unafflicted) unlocks past-life spiritual merit (Poorvapunya), higher gnosis, and divine benediction.",
            "Exceptional intuitive foresight, mastery of mantra sciences, and sublime theological insight.",
            "Blessed with virtuous, brilliant, and highly accomplished progeny who elevate the family dynasty.",
            "Serendipitous breakthroughs manifest effortlessly throughout life as if guided by an unseen guardian angel."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: நாட்டின் மிக உயர்ந்த அரசியல் ஆலோசகர், வேத வித்வான், பல்லாயிரம் கோடீஸ்வர யோகம்.",
            "பிள்ளைகள் உலகப் புகழ் பெறுவார்கள்; முன்னோர்களின் புண்ணியத்தால் வாழ்நாள் முழுவதும் யோக வாழ்வு."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Premier state counselor, Vedic preceptor, multi-millionaire through past-life grace.",
            "Progeny achieve world renown in science, statecraft, or arts; unending streams of good fortune."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் காலதாமதம் அல்லது பிள்ளைகளின் ஆரோக்கியத்தில் கவலை.",
            "பங்குச் சந்தையில் குருட்டுத்தனமாக முதலீடு செய்து நஷ்டமடைதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Delays or emotional anxieties regarding children; frail constitution in firstborn.",
            "Heavy financial setbacks from ill-considered speculative ventures and ideological rigidity."
        ],
        "career_wealth_ta": [
            "முதலீட்டு நிதி மேலாண்மை (Hedge Fund), அரசாங்க உயர் ஆலோசனைக் குழு, வேதாந்தப் பேராசிரியர், ஜோதிட ஆராய்ச்சி, நீதித்துறை.",
            "அறிவுசார் திட்டமிடலாலும் திடீர் அதிர்ஷ்ட வாய்ப்புகளாலும் அள்ள அள்ளக் குறையாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Stellar career in hedge fund strategy, governmental think-tanks, philosophy deanships, and judicial advisory.",
            "Monumental wealth generated through prescient investments and intellectual endowments."
        ],
        "health_precautions_ta": [
            "வயிற்றுப் பகுதியில் கொழுப்பு, கணையக் கோளாறுகள் (Pancreas), நீரிழிவு மற்றும் கல்லீரல் உஷ்ணம்.",
            "இனிப்புப் பண்டங்களைத் தவிர்த்து சத்தான நார்ச்சத்துள்ள உணவுகளை உண்பது அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to abdominal adiposity, pancreatic enzymes imbalance, type-2 diabetes, and liver congestion.",
            "Strict glycemic regulation, elimination of processed confectionery, and routine insulin checks."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (பகைவர்களை நல்வழிப்படுத்துதல் & கடன் தீர்த்தல்)",
        "house_title_en": "6th House - Satru Bhava (Reconciling Enemies & Discharging Debts)",
        "core_traits_ta": [
            "எதிரிகளையும் தன் கருணையாலும், விவேகத்தாலும், சாந்த குணத்தாலும் நண்பர்களாக மாற்றும் மாண்புடையவர்.",
            "நேரடி மோதல்களைத் தவிர்த்து அமைதியான சமரசப் பேச்சுவார்த்தைகள் மூலம் வழக்குகளை முடித்து வைப்பார்.",
            "பிறருக்கு உதவும் தாராள உள்ளமும், தொண்டு நிறுவனங்கள் மற்றும் மருத்துவமனைகளுக்கு உதவும் அறப்பண்பும் உண்டு.",
            "தாய்மாமனுடன் சுமுகமான உறவும், அவரது வழிகாட்டலால் நன்மைகளும் கிட்டும்."
        ],
        "core_traits_en": [
            "Converts bitter adversaries into allies through magnanimity, supreme patience, and moral suasion.",
            "Avoids toxic confrontations, settling litigations and commercial disputes via high-minded mediation.",
            "Deep humanitarian compassion; donates liberally to hospices, free clinics, and orphanages.",
            "Maintains affectionate bonds with maternal uncles, deriving spiritual and ethical advice from them."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: கடன்கள் இல்லாத பூரண வாழ்க்கை, வழக்குகளில் சுமுக வெற்றி, அசைக்க முடியாத உடல் ஆரோக்கியம்.",
            "மருத்துவத் துறையிலும், சமூக நல்லிணக்க அமைப்புகளிலும் உயர்ந்த தலைமைப் பதவிகளை வகிப்பார்."
        ],
        "strong_placement_en": [
            "Strong with benefic aspects: Completely debt-free existence, triumphant out-of-court settlements, and robust health.",
            "Appointed to presidential boards of health, medical ethics commissions, and humanitarian councils."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கல்லீரல் நோய்கள், நீரிழிவு, கடன் தொல்லைகளால் மன உளைச்சல்.",
            "வேலையாட்களால் பண இழப்புகளும், காரணமற்ற அவப்பெயரும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe hepatic cirrhosis, uncontrolled diabetes, and anxiety over unpaid liabilities.",
            "Financial leakages through unscrupulous subordinates and unmerited public criticism."
        ],
        "career_wealth_ta": [
            "மருத்துவமனை இயக்குநர், சர்வதேச சமரச தீர்ப்பாயம் (Arbitration), பொது சுகாதாரம், வங்கி கடன் மேலாண்மை, தொண்டு நிறுவனங்கள்.",
            "நேர்மையான உழைப்பாலும் சேவைகளாலும் நிலையான தன வரவு."
        ],
        "career_wealth_en": [
            "Flourishes as hospital director, international ombudsman, public health executive, and charitable trustee.",
            "Steady, secure income built upon principled public service and administrative competence."
        ],
        "health_precautions_ta": [
            "கல்லீரல் வீக்கம், செரிமானக் கோளாறுகள், பித்தப்பை கற்கள், நீரிழிவு மற்றும் குடல் புண்கள்.",
            "கொழுப்பு மற்றும் எண்ணெய் உணவுகளைக் குறைத்து, எளிய சமைத்த உணவுகளை உட்கொள்ளுதல் நலம்."
        ],
        "health_precautions_en": [
            "Vulnerable to hepatomegaly, biliary colic, gallstones, insulin resistance, and intestinal ulcers.",
            "Low-fat nutrition, zero alcohol consumption, and periodic liver function blood panels."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (ஹம்ச யோகம் / உன்னத துணை & கூட்டு வெற்றி)",
        "house_title_en": "7th House - Kalathra Bhava (Hamsa Yoga / Noble Spouse & Blessed Alliances)",
        "core_traits_ta": [
            "குரு 7-ஆம் பாவத்தில் அமைவது பூரண தாம்பத்திய சுகம், தெய்வ பக்திமிக்க வாழ்க்கைத் துணை மற்றும் லக்னத்திற்கு 100% சுப பார்வையைத் தரும்.",
            "அழகான, உயர்ந்த பண்புகள் நிறைந்த, செல்வந்த குடும்பத்தில் பிறந்த உன்னதமான வாழ்க்கைத் துணை அமைவார்.",
            "திருமணத்திற்குப் பின் ஜாதகருக்கு ராஜயோகம் செயல்படத் தொடங்கும்; சமூக அந்தஸ்து பலமடங்கு உயரும்.",
            "வணிக கூட்டாண்மைகளில் நேர்மையும் பரஸ்பர நம்பிக்கையும் நிலவி பல கோடி ரூபாயில் வர்த்தகம் பெருகும்."
        ],
        "core_traits_en": [
            "Jupiter in the 7th is a sublime blessing for conjugal harmony, bestowing a pious, noble partner and casting a golden aspect on Lagna.",
            "Blessed with an exquisitely virtuous, educated, prosperous, and devoted spouse.",
            "Marriage acts as the supreme catalyst for Raja Yoga, catapulting the native into high societal prominence.",
            "Commercial partnerships thrive upon ironclad mutual trust, ethical contracts, and massive turnover."
        ],
        "strong_placement_ta": [
            "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: நாட்டின் மிக உயர்ந்த குடும்பத்துடன் திருமண பந்தம், அரசு கௌரவங்கள்.",
            "சர்வதேச வர்த்தகத்தில் வெற்றி, இல்லறத்தில் சகல சௌபாக்கியங்களும் நிறைந்து தேவதம்பதிகளாக வாழ்வர்."
        ],
        "strong_placement_en": [
            "Exalted or own house forming Hamsa Yoga: Marries into royal or national leadership dynasties; shower of civic honors.",
            "Triumphs in international commerce, embodying the archetype of an ideal, prosperous divine couple."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமணத்தில் காலதாமதம், துணையின் ஆரோக்கியத்தில் குறைபாடுகள்.",
            "கூட்டுத் தொழிலில் பங்குதாரர்களை அளவுக்கு அதிகமாக நம்பி ஏமாறுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Protracted delays in solemnizing marriage; partner prone to metabolic health frailties.",
            "Loss of capital through naive over-trust in opportunistic business associates."
        ],
        "career_wealth_ta": [
            "சர்வதேச வர்த்தகம், தூதரக சேவைகள், சட்ட ஒப்பந்தங்கள், பெரிய வணிகக் கூட்டாண்மை, ஆலோசனை நிறுவனங்கள்.",
            "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் நேர்மையான கூட்டாண்மையாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
        ],
        "career_wealth_en": [
            "Dominant in international jurisprudence, consular missions, luxury trade syndicates, and corporate arbitration.",
            "Magnificent fortune accumulated through spousal providence and lucrative consortiums."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், நீரிழிவு, அடிவயிற்று உஷ்ணம் மற்றும் கொழுப்பு படிதல்.",
            "முறையான குடிநீர் அருந்துதலும், சர்க்கரை அளவைக் கட்டுப்பாட்டில் வைத்திருப்பதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to renal fat accumulation, glycosuria, diabetic complications, and pelvic sluggishness.",
            "Consistent daily hydration, low-glycemic meal planning, and annual urological screenings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (பூரண தீர்க்காயுள், மறைபொருள் ஞானம் & உயில் சொத்து)",
        "house_title_en": "8th House - Ayur Bhava (Immaculate Longevity, Esoteric Wisdom & Inheritances)",
        "core_traits_ta": [
            "குரு 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு நோயற்ற பூரண தீர்க்காயுளை (80+ வயது) வழங்கும் உன்னத அமைப்பாகும்.",
            "மறைமுக சாஸ்திரங்கள், வேதாந்தம், மரணத்திற்குப் பின் உள்ள நிலை மற்றும் பிரபஞ்ச ரகசியங்களை உணரும் ஞானம்.",
            "வாழ்க்கையில் நெருக்கடிகள் வரும்போதெல்லாம் கண்ணுக்குத் தெரியாத இறைவனின் அருள் இவரைக் காக்கும்.",
            "மனைவி வழியில் எதிர்பாராத பெரும் உயில் சொத்துகள், காப்பீடுகள் மற்றும் பரம்பரைச் செல்வங்கள் வந்து சேரும்."
        ],
        "core_traits_en": [
            "Jupiter in the 8th is classically celebrated as an invincible guarantor of long, dignified longevity (80+ years).",
            "Profound metaphysical comprehension of afterlife realms, Vedic esotericism, and cosmic quantum laws.",
            "Divine grace serves as an invisible shield, miraculously pulling the native out of life-threatening crises.",
            "Reaps unexpected testamentary windfalls, insurance estates, and unearned ancestral inheritances through marriage."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சதாபிஷேகம் (80 வயது நிறைவு) காணும் யோகம், பல்லாயிரம் கோடி உயில் சொத்துகள், ஆன்மீக முக்தி.",
            "சமுதாயத்தில் உன்னத ஆன்மீக வழிகாட்டியாகத் திகழ்ந்து அமைதியான சமாதி நிலை எய்துவார்."
        ],
        "strong_placement_en": [
            "Exalted or in own sign: Attains auspicious Centenarian age, colossal legacy inheritances, and serene Moksha.",
            "Revered as an enlightened saintly counselor, transitioning peacefully in exalted conscious meditation."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கல்லீரல் கோளாறுகள், மஞ்சள் காமாலை, உயில் சொத்துகளில் தகராறுகள்.",
            "அரசாங்க வரி ஏய்ப்பு அல்லது அபராதங்களால் மன உளைச்சல் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Chronic hepatitis, severe jaundice, and litigious partition battles over inheritances.",
            "Anxieties over estate taxes and legal probate encumbrances."
        ],
        "career_wealth_ta": [
            "ஆயுள் காப்பீட்டுத் தலைவர், தொல்பொருள் ஆராய்ச்சி, வேதாந்த ஆராய்ச்சி, டிரஸ்டி, உயில் நிர்வாகி, ரகசிய நிதி ஆலோசகர்.",
            "உயில் சொத்துகள், பரம்பரை அறக்கட்டளைகள் மற்றும் காப்பீட்டு முதிர்வுகள் மூலம் பெருஞ்செல்வம்."
        ],
        "career_wealth_en": [
            "Distinguished as life insurance commissioner, archaeological research fellow, trust executor, and private wealth manager.",
            "Vast windfalls realized through family legacies, estate settlements, and offshore annuities."
        ],
        "health_precautions_ta": [
            "மஞ்சள் காமாலை, கல்லீரல் கொழுப்பு, நீரிழிவு மற்றும் குடல் நோய்கள்.",
            "மது, கொழுப்பு உணவுகளை முற்றிலும் தவிர்த்து கல்லீரலைப் பாதுகாப்பது மிக அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to jaundice, non-alcoholic fatty liver, diabetic neuropathy, and sluggish bowels.",
            "Strictly avoid alcohol, eliminate saturated fats, and undergo bi-annual hepatic ultrasound scans."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (காரகோ பாவக நாஸ்திக்கு அப்பாற்பட்ட பரம பாக்கியம் & தர்மம்)",
        "house_title_en": "9th House - Bhagya Bhava (Supreme Fortune, Pious Father & Divine Grace)",
        "core_traits_ta": [
            "குரு 9-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் ஆகச்சிறந்த பாக்கிய அமைப்பாகும்; தர்மத்தின் உருவமாகத் திகழ்வார்.",
            "தந்தையின் மீது எல்லை இல்லாத பக்தி; தந்தை உயர்ந்த ஆன்மீகவாதியாகவும் செல்வந்தராகவும் விளங்குவார்.",
            "புனிதத் தலங்களுக்கு யாத்திரை செல்லுதல், திருவிழாக்களை முன்னின்று நடத்துதல், வேத பாடசாலைகளை உருவாக்குதல்.",
            "எடுத்த காரியங்கள் யாவும் வெற்றி பெறும்; வாழ்க்கையில் வறுமை என்பது இவரை எட்டிக்கூடப் பார்க்காது."
        ],
        "core_traits_en": [
            "Jupiter in the 9th is hailed as one of the most sublime placements in Vedic astrology; embodies living Dharma.",
            "Boundless devotion to the father, who is typically an esteemed, spiritual, and affluent patriarch.",
            "Passionate sponsor of pilgrimages, temple consecrations, Vedic academies, and Vedic chanting schools.",
            "Every enterprise is crowned with divine fruition; poverty and misery are utterly alien to his destiny."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட ராஜயோகம்! நாட்டின் மாபெரும் மத பீடாதிபதி அல்லது ஜனாதிபதி அந்தஸ்து.",
            "கோடிக்கணக்கான மக்களின் நல்வழிகாட்டி, உலகெங்கும் ஆசிரமங்கள், அரச குடும்பங்களின் ராஜகுருவாகத் திகழ்தல்."
        ],
        "strong_placement_en": [
            "Exalted or in own sign: Supreme Raja Yoga! Revered as Jagadguru, National President, or Royal Preceptor.",
            "Inspires millions of souls globally; founds international philanthropic ashrams with royal patronage."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, ஆன்மீக குருக்களுடன் முரண்பாடுகள்.",
            "வெளிநாட்டுப் பயணங்களில் தடைகள் மற்றும் தர்ம காரியங்களில் அவப்பெயர்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health setbacks, philosophical disillusionment with institutional priesthood.",
            "Delays in foreign travel and unmerited scandals regarding charitable funds."
        ],
        "career_wealth_ta": [
            "மத அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், உச்ச நீதிமன்றத் தலைமை நீதிபதி, சர்வதேச தூதர், நூலாசிரியர்.",
            "தர்ம வழியில் சேர்க்கும் வற்றாத செல்வமும், பரம்பரைச் சொத்துகளும் தலைமுறைக்கும் நிலைத்து நிற்கும்."
        ],
        "career_wealth_en": [
            "Commands top status as religious trust president, supreme court justice, ambassador, and theological author.",
            "Multi-generational noble wealth preserved intact through institutional trusts and endowments."
        ],
        "health_precautions_ta": [
            "தொடைப் பகுதியில் கொழுப்பு படிதல், இடுப்பு வாதம், கல்லீரல் உஷ்ணம் மற்றும் சர்க்கரை நோய்.",
            "நடைப்பயிற்சியும், எளிய சாத்வீக உணவு முறையும் உடல் ஆரோக்கியத்தை நீண்ட காலத்திற்குப் பாதுகாக்கும்."
        ],
        "health_precautions_en": [
            "Prone to femoral adiposity, sciatica flares, hepatic sluggishness, and late-onset hyperglycemia.",
            "Brisk morning walking and a clean sattvic lifestyle safeguard vitality into advanced age."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (ஹம்ச யோகம் / உயர் அதிகாரம், அரசு கௌரவம் & தர்ம தொழில்)",
        "house_title_en": "10th House - Karma Bhava (Hamsa Yoga / High Executive Power & Dharmic Career)",
        "core_traits_ta": [
            "குரு 10-ஆம் பாவத்தில் அமைவது உன்னதமான தர்ம நெறி தவறாத தொழில் மேன்மையையும், ஆட்சி அதிகாரத்தையும் தரும்.",
            "நேர்மையான நிர்வாகி; எந்தச் சூழ்நிலையிலும் லஞ்சம், ஊழல் மற்றும் அதர்ம வழிகளுக்கு ஒருபோதும் தலைவணங்க மாட்டார்.",
            "சமுதாயத்தில் மக்கள் போற்றும் உயர்ந்த கௌரவப் பதவிகள், பல்லாயிரக்கணக்கான பணியாளர்களை வழிநடத்தும் தலைமைப் பண்பு.",
            "தொழிலில் அசைக்க முடியாத நற்பெயர்; சரித்திரத்தில் போற்றப்படும் நல்லாசிரியராகவும் வழிகாட்டியாகவும் திகழ்வார்."
        ],
        "core_traits_en": [
            "Jupiter in the 10th confers stellar professional elevation anchored in unbending ethical righteousness.",
            "Impeccable administrator; steadfastly refuses corruption, deceit, or underhanded shortcuts.",
            "Commands high public acclaim, sovereign ministerial portfolios, and paternal leadership over thousands.",
            "Builds an unblemished professional reputation, immortalized as a visionary statesman and moral mentor."
        ],
        "strong_placement_ta": [
            "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: தலைமை நீதிபதி, கவர்னர், கேபினட் மந்திரி அந்தஸ்து.",
            "நாட்டின் முதன்மை பல்கலைக்கழகங்களின் வேந்தராகவோ அல்லது பெரிய அறக்கட்டளைகளின் தலைவராகவோ முடிசூடுவார்."
        ],
        "strong_placement_en": [
            "Exalted or own house forming Hamsa Yoga: State Governor, Supreme Court Chief Justice, Cabinet Minister.",
            "Presides as Chancellor of premier universities or Governor of the Central Reserve Bank."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உத்தியோகத்தில் உயர் அதிகாரிகளுடன் கருத்து மோதல்கள், திடீர் இடமாற்றம்.",
            "தொழிலில் நேர்மையாக இருந்தும் அவப்பெயர் உண்டாக வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Friction with autocratic superiors, sudden political transfers, and bureaucratic disillusionment.",
            "Unmerited public scrutiny despite transparently honest intentions."
        ],
        "career_wealth_ta": [
            "நீதித்துறை, உயர் கல்வித்துறை, நிதி அமைச்சகம், சர்வதேச வங்கிகள், அறக்கட்டளை நிர்வாகம், அரசு ஆலோசகர்.",
            "அரசாங்க கௌரவ ஊதியங்களாலும், தொழில் மேன்மையாலும் கோடிக்கணக்கில் சொத்துகள் சேரும்."
        ],
        "career_wealth_en": [
            "Flourishes in the judiciary, higher education, treasury leadership, sovereign wealth funds, and policy think-tanks.",
            "Commanding multi-million dollar asset accumulation through state pensions, consultancy, and board directorships."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் உடல் பருமன், மூட்டு தேய்மானம், ரத்த அழுத்தம் மற்றும் நீரிழிவு.",
            "வேலைக்கு நடுவே தியானமும், உடற்பயிற்சியும் செய்வது நீண்ட ஆயுளைத் தரும்."
        ],
        "health_precautions_en": [
            "Occupational stress, metabolic syndrome, knee osteoarthritis, and fluctuating blood pressure.",
            "Structured meditation, daily exercise, and portion control maintain executive health."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / குபேர யோகம் & உயர் நட்பு)",
        "house_title_en": "11th House - Labha Bhava (Abundant Gains, Kubera Yoga & Saintly Network)",
        "core_traits_ta": [
            "குரு 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடீஸ்வர யோகத்தையும், எண்ணிய ஆசைகள் அனைத்தையும் நிறைவேற்றும் வரப்பிரசாதமாகும்.",
            "தொட்டதெல்லாம் பொன்னாகும் தன யோகம்; பல துறைகளிலிருந்து வற்றாத நிதி வரவு வந்துகொண்டே இருக்கும்.",
            "அரசியல் தலைவர்கள், நீதிபதிகள், ஆன்மீக மகான்கள் மற்றும் பெரும் செல்வந்தர்களின் உயர்ந்த நட்பு வட்டம்.",
            "மூத்த சகோதரர்களிடம் அளப்பரிய அன்பும் பாசமும் நிலவும்; அவர்களால் பெரும் நன்மைகள் கிட்டும்."
        ],
        "core_traits_en": [
            "Jupiter in the 11th (an Upachaya house) is one of the most magnificent placements for compounding wealth and wish-fulfillment.",
            "Midas touch in financial undertakings; unceasing multi-channel cash streams flood his banking reserves.",
            "Surrounded by an elite network of statesmen, appellate judges, spiritual luminaries, and philanthropists.",
            "Cherished, profoundly harmonious bond with elder siblings, who facilitate monumental career breakthroughs."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான சொத்துகள், சொகுசு வாகனங்கள், சமூகத்தின் முதன்மை அந்தஸ்து.",
            "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு அன்னதானமும் கல்விக் கொடையும் வழங்கும் வள்ளல் யோகம்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-billion dollar asset portfolios, private air fleet, and premier social stature.",
            "Acts as a legendary philanthropist, establishing university scholarships, hospitals, and heritage restorations."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு நிதி இழப்பு, மூத்த சகோதரருடன் பிரிவு.",
            "லாபங்கள் கைநழுவிப் போதல் அல்லது எதிர்பாராத விரயங்கள் ஏற்படுதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by unscrupulous cronies, capital erosion, and sibling estrangement.",
            "Anticipated revenues delayed by bureaucratic entanglements."
        ],
        "career_wealth_ta": [
            "பெருநிறுவன முதலீடுகள், வென்ச்சர் கேபிடல், வங்கி மேலாண்மை, கல்வி நிறுவனங்கள், ஏற்றுமதி-இறக்குமதி, தொண்டு அறக்கட்டளைகள்.",
            "முதலீடுகளின் அபரிமிதமான வளர்ச்சியால் சமுதாயத்தின் பெரும் பணக்காரராக உயருதல்."
        ],
        "career_wealth_en": [
            "Unrivaled success in mega-venture capital, corporate investment banking, educational syndicates, and global philanthropy.",
            "Extraordinary capital multiplication placing the native in the billionaire tier."
        ],
        "health_precautions_ta": [
            "இடது காது கேளாமை, கணுக்கால் வீக்கம், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் சர்க்கரை நோய்.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear dullness, peripheral ankle edema, circulatory sluggishness, and diabetes.",
            "Regular ankle mobility stretching, compression socks for long flights, and otic checkups."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்ச காரகன் / ஆன்மீக முக்தி & தர்ம விரயம்)",
        "house_title_en": "12th House - Vraya & Moksha Bhava (Spiritual Liberation, Sacred Solitude & Foreign Renown)",
        "core_traits_ta": [
            "குரு 12-ஆம் பாவத்தில் அமர்வது பிறவிப் பெருங்கடலை நீந்தி முக்தி அடையும் உன்னதமான ஆன்மீக யோகமாகும்.",
            "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், கோவில் திருப்பணிகள், தர்ம ஸ்தாபனங்கள் மற்றும் ஆன்மீக காரியங்களுக்குச் செலவிடுவார்.",
            "பிறந்த மண்ணை விட வெளிநாடுகளிலோ அல்லது தொலைதூரத் தீவுகளிலோ அளப்பரிய நற்பெயரும் யோகமும் பெறுவார்.",
            "தனிமையை விரும்பும் அமைதியான முனிவர் போன்ற சுபாவம்; ஆழ்ந்த தூக்கமும் மன அமைதியும் நிறைந்திருக்கும்."
        ],
        "core_traits_en": [
            "Jupiter in the 12th is the classic harbinger of spiritual Moksha (emancipation from the cycle of rebirth).",
            "Directs worldly wealth away from frivolous vanity towards magnificent temple restorations and humanitarian endowments.",
            "Achieves peak spiritual honors, peaceful existence, and immense respect when residing in foreign lands.",
            "Contemplative, monastic inner disposition; blessed with serene restorative sleep and profound detachment."
        ],
        "strong_placement_ta": [
            "கடகத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் ஆன்மீக ஆசிரமங்கள், சர்வதேச அங்கீகாரம்.",
            "அயன சயன சுகம் பூரணமாகக் கிட்டும்; ஜீவன் முக்தி அடைந்து ஆன்மீக வரலாற்றில் இடம்பெறுவார்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Founds renowned international spiritual retreats abroad; revered as an enlightened sage.",
            "Attains effortless Samadhi, blissful restorative sleep, and transcendental liberation (Jivanmukti)."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மதத்தின் பெயரால் ஏமாற்றப்படுதல், வீண் விரயங்கள், தூக்கமின்மை.",
            "இடது கண் பார்வை மங்குதல் மற்றும் குடும்பச் சொத்துகளில் இழப்பு ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by bogus spiritual cults, fruitless financial drainage, and insomnia.",
            "Left eye vision defects and wasteful dissipation of family patrimony."
        ],
        "career_wealth_ta": [
            "சர்வதேச ஆன்மீக ஆசிரமங்கள், வெளிநாட்டுத் தூதரகங்கள், உலகளாவிய தொண்டு நிறுவனங்கள், மருத்துவமனை அறக்கட்டளைகள், தத்துவ ஆராய்ச்சி.",
            "வெளிநாட்டு நாணயங்களாலும் ஆன்மீக கொடைகளாலும் நிறைவான செல்வம்."
        ],
        "career_wealth_en": [
            "Stellar leadership in international ashrams, consular diplomacy, global humanitarian agencies, and theological institutes.",
            "Wealth sustained through generous foreign donations, international royalties, and endowment funds."
        ],
        "health_precautions_ta": [
            "இடது கண் பாதிப்பு, பாதங்களில் நீர் வீக்கம், தூக்கமின்மை மற்றும் கல்லீரல் பலவீனம்.",
            "இரவில் அமைதியான தியானமும், பாதங்களை மசாஜ் செய்வதும் ஆழ்ந்த தூக்கத்தைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye ocular strain, lymphatic foot edema, insomnia, and sluggish hepatic drainage.",
            "Nightly grounding meditation, warm foot massages, and calming chamomile infusions promote tranquility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]

VENUS_DATA = [
    {
        "house": 1,
        "bhava_category": "kendra",
        "house_title_ta": "1-ஆம் பாவம் - லக்னம் (மாளவ்ய யோகம் / பேரழகு, காந்தக் கவர்ச்சி & கலை மேதை)",
        "house_title_en": "1st House - Ascendant / Tanu Bhava (Malavya Yoga / Peerless Beauty & Artistic Genius)",
        "core_traits_ta": [
            "அழகிய காந்தக் கண்கள், பிரகாசமான வசீகர முகம், நளினமான உடல்வாகு மற்றும் அனைவரையும் கவரும் பேரழகு உடையவர்.",
            "கலை, இசை, சினிமா, இலக்கியம், ஆடை வடிவமைப்பு மற்றும் நவரத்தினங்களில் ஆழ்ந்த ரசனை கொண்டவர்.",
            "இனிமையான சுபாவம், கனிவான பேச்சு, தாராள மனப்பான்மை மற்றும் அனைவரையும் நேசிக்கும் அன்பு உள்ளம்.",
            "சொகுசு வாழ்க்கை, வாசனைத் திரவியங்கள், ஆடம்பர வாகனங்கள் மற்றும் சுகபோகங்களை முழுமையாக அனுபவிப்பார்.",
            "சுயமரியாதையை அழகாகவும் நயமாகவும் நிலைநாட்டுவார்; எவரிடமும் முரட்டுத்தனமாக நடக்க மாட்டார்."
        ],
        "core_traits_en": [
            "Dazzling magnetic physical allure, luminous eyes, proportionate facial symmetry, and graceful posture.",
            "Refined connoisseur of fine arts, classical music, cinema, literature, haute couture, and precious gems.",
            "Sweet, charming temperament; radiates effortless courtesy, generosity, and charismatic warmth.",
            "Innate destiny for luxurious living, aromatic scents, premium sports cars, and sensory delights.",
            "Preserves self-respect through exquisite diplomacy; utterly disdains vulgarity and coarse aggression."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் (Malavya Yoga) அமைந்தால்: உலகப் புகழ் பெற்ற சினிமா நட்சத்திரம், அரச போகம்.",
            "அரண்மனை போன்ற பங்களாக்கள், எண்ணற்ற சொகுசு கார்கள், உலகின் தலைசிறந்த கலைஞராகப் போற்றப்படுதல்."
        ],
        "strong_placement_en": [
            "Exalted in Pisces or in own signs Taurus/Libra forming Malavya Mahapurusha Yoga: Iconic superstar of screen and stage, princely luxuries.",
            "Commands palatial residential villas, fleets of exotic vehicles, and international adulation as an artistic legend."
        ],
        "weak_placement_ta": [
            "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்திய சுகக் குறைவு, பாலியல் நோய்கள், அழகில் வாட்டம்.",
            "ஆடம்பரச் செலவுகளால் நிதி நெருக்கடி, தவறான நட்புகளால் அவப்பெயர் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Virgo or afflicted: Marital dissatisfaction, reproductive/urological ailments, and premature loss of physical charm.",
            "Financial ruin through profligate hedonism and scandalous entanglements with unreliable companions."
        ],
        "career_wealth_ta": [
            "சினிமா, தொலைக்காட்சி, இசை, ஆடை வடிவமைப்பு (Fashion Design), அழகு சாதனங்கள், நவரத்தின வர்த்தகம், சொகுசு ஹோட்டல்கள்.",
            "கலை படைப்புகளாலும் மக்கள் செல்வாக்கினாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Superstar acclaim in entertainment, high fashion, luxury cosmetics, jewelry design, and five-star hospitality.",
            "Multi-million dollar revenues flowing from brand endorsements, creative royalties, and luxury enterprises."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், நீரிழிவு நோய் (Diabetes), பாலியல் உறுப்புகளில் உஷ்ணம், முகம் மற்றும் சரும நோய்கள்.",
            "அதிக இனிப்புகளையும், கொழுப்பு உணவுகளையும் தவிர்த்து உடற்பயிற்சி செய்வது ஆரோக்கியம் தரும்."
        ],
        "health_precautions_en": [
            "Vulnerable to renal dysfunctions, diabetes mellitus, reproductive tract inflammation, and facial acne.",
            "Moderate refined sugar and dairy fat consumption, hydrate generously, and maintain active lifestyle."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
    },
    {
        "house": 2,
        "bhava_category": "panaphara",
        "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (கவிதை வாக்கு, குபேர தனம் & ஆபரணச் சேர்க்கை)",
        "house_title_en": "2nd House - Dhana Bhava (Poetic Eloquence, Boundless Luxury & Fine Jewels)",
        "core_traits_ta": [
            "சுக்கிரன் 2-ஆம் பாவத்தில் அமைவது தேன் போன்ற இனிமையான பேச்சையும், கவிதை நயத்தையும், அகண்ட தன லாபத்தையும் தரும்.",
            "வசீகரமான புன்னகை, ஒளிமயமான முகத்தோற்றம் மற்றும் அறுசுவை உணவுகளை ரசித்து உண்ணும் பழக்கம்.",
            "நவரத்தினங்கள், தங்கம், வெள்ளி, வைர நகைகள் மற்றும் விலையுயர்ந்த ஆடைகளைச் சேர்ப்பதில் ஆர்வம்.",
            "குடும்பத்தில் மகிழ்ச்சி, அன்பு மற்றும் கணவன்-மனைவி இடையே அன்யோன்யம் நிறைந்திருக்கும்."
        ],
        "core_traits_en": [
            "Venus in the 2nd endows honeyed poetic speech, mesmerizing vocal timbre, and immense fiscal opulence.",
            "Irresistible charming smile, radiant facial glow, and an epicurean appreciation for gourmet cuisine.",
            "Avid collector of fine diamond jewelry, gold bullion, silver artifacts, and designer apparel.",
            "Fosters a joyful, harmonious, and affectionate domestic household overflowing with luxury."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது சொந்த வீட்டில் பலம் பெற்றால்: பல நூறு கோடி திரவ சேமிப்பு, வைர மாலைகள், வாக்கு பலிதம்.",
            "பேச்சையே முதலீடாக வைத்து சினிமா, பாட்டு மற்றும் வர்த்தகத்தில் உலகளவில் பெரும் புகழ் பெறுவார்."
        ],
        "strong_placement_en": [
            "Exalted in Pisces or in own house: Bestows colossal liquid capital, legendary diamond heirlooms, and prophetic vocal charisma.",
            "Monetizes speech and singing into a multi-million dollar global entertainment and business empire."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் அதீத கற்பனை, ஆடம்பர விரயங்களால் கடன்கள்.",
            "பற்களில் கோளாறுகள், வாய் புண்கள் அல்லது வலது கண்ணில் பார்வை மங்குதல் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Pretentious speech, profligate debt incurred on luxury ostentation, and family disputes.",
            "Prone to periodontal decay, oral ulcerations, and right-eye vision impairments."
        ],
        "career_wealth_ta": [
            "பாடகர், இசை அமைப்பாளர், பின்னணிக் குரல் கலைஞர், வைர வர்த்தகம், அழகு நிலையம், உணவு விடுதிகள், வங்கித் துறை.",
            "வசீகரப் பேச்சாலும் கலைத் திறனாலும் கோடிக்கணக்கில் செல்வம் குவியும்."
        ],
        "career_wealth_en": [
            "Eminence as playback singer, composer, voice actor, diamond trader, luxury salon founder, and restaurateur.",
            "Vast fortune generated directly through vocal gifts, culinary mastery, and aesthetic commerce."
        ],
        "health_precautions_ta": [
            "தொண்டை அழற்சி, நாக்கில் புண்கள், பற்கள் ஆடுதல், கண் பலவீனம் மற்றும் தைராய்டு குறைபாடுகள்.",
            "குளிர்ந்த பானங்களைத் தவிர்த்து, தொண்டையையும் பற்களையும் சுத்தமாகப் பராமரிக்கவும்."
        ],
        "health_precautions_en": [
            "Susceptible to vocal cord nodules, pharyngitis, tooth decay, ocular strain, and thyroid sluggishness.",
            "Avoid iced beverages, practice vocal warmups, and adhere to strict oral dental hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 101) & Saravali Ch. 30"
    },
    {
        "house": 3,
        "bhava_category": "upachaya",
        "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (கலை வீரியம் & சகோதரிகளின் அன்பு)",
        "house_title_en": "3rd House - Sahaja Bhava (Artistic Enterprise & Sisters' Goodwill)",
        "core_traits_ta": [
            "நளினமான செயல்பாடுகள், நாடக மற்றும் கலை உணர்வு, புதிய கலை வடிவங்களை உருவாக்கும் கற்பனைத் திறன்.",
            "சகோதர சகோதரிகளிடம் அளப்பரிய பாசம்; குறிப்பாக பெண் சகோதரிகளால் வாழ்வில் அளப்பரிய அதிர்ஷ்டமும் நன்மைகளும் கிட்டும்.",
            "அடிக்கடி பொழுதுபோக்கு உல்லாசப் பயணங்கள், படகு சவாரிகள் மற்றும் இயற்கை எழில் கொஞ்சும் இடங்களுக்குச் செல்லுதல்.",
            "இசைக் கருவிகளை வாசிப்பதிலும், நடனம், புகைப்படம் எடுப்பதிலும் அசாத்திய திறமை படைத்திருப்பார்."
        ],
        "core_traits_en": [
            "Graceful coordination, flair for dramatic performing arts, and inventive aesthetic imagination.",
            "Cherished, deeply loving bond with sisters, who bring immense good fortune and social elevation.",
            "Fond of romantic holidays, scenic yachting voyages, and weekend retreats in luxury resorts.",
            "Innate talent for mastering musical instruments, choreography, fine art photography, and design."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற இசைக் கலைஞர், ஆடை வடிவமைப்பாளர், சகோதரிகளால் பெரும் செல்வம்.",
            "கலை முயற்சிகள் யாவும் அமோக வெற்றி பெற்று நாடெங்கும் விருதுகளும் கௌரவங்களும் குவியும்."
        ],
        "strong_placement_en": [
            "Strong or exalted: World-renowned virtuoso musician, celebrity couturier, and immense wealth via sisters.",
            "Artistic projects achieve international box-office and critical acclaim; showered with golden awards."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரிகளுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
            "சிற்றின்பங்களில் அதிக நாட்டம் கொண்டு ஆற்றலை வீணடித்தல் அல்லது கலை முயற்சிகளில் தோல்வி."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Bitter sibling misunderstandings, wrist nerve fatigue, and dissipated artistic potential.",
            "Indolence, hedonistic lethargy, and commercial failures in creative ventures."
        ],
        "career_wealth_ta": [
            "இசைக் கச்சேரிகள், சினிமா இயக்கம், விளம்பர வடிவமைப்பு, கலைக்கூடங்கள் (Art Galleries), புகைப்படத் துறை, பொழுதுபோக்கு பூங்காக்கள்.",
            "கலைத் துறையாலும் பெண்களின் பேராதரவாலும் அபரிமிதமான தன சேர்க்கை."
        ],
        "career_wealth_en": [
            "Dominant in concert performance, cinema production, creative direction, luxury art galleries, and digital visual media.",
            "Tremendous financial harvest reaped through artistic syndication and female demographic appeal."
        ],
        "health_precautions_ta": [
            "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காதுகளில் நீர் வடிதல் மற்றும் சரும வறட்சி.",
            "முறையான கைகளுக்கான ஆசனங்களும், சருமத்திற்கு நல்ல ஈரப்பதமும் தருவது நலம் பயக்கும்."
        ],
        "health_precautions_en": [
            "Prone to shoulder bursitis, upper limb neuralgia, otic fluid accumulation, and skin dehydration.",
            "Gentle yoga stretches and regular skin hydration preserve physical flexibility."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
    },
    {
        "house": 4,
        "bhava_category": "kendra",
        "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (மாளவ்ய யோகம் / சொகுசு மாளிகைகள், வாகன யோகம் & சுகபோகம்)",
        "house_title_en": "4th House - Sukha Bhava (Malavya Yoga / Luxury Mansions, Exotic Cars & Pure Bliss)",
        "core_traits_ta": [
            "சுக்கிரன் 4-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று மாளவ்ய யோகத்தை (Malavya Yoga) உண்டாக்குகிறார்.",
            "அரண்மனை போன்ற ஆடம்பர பங்களா, சொகுசு கார்கள், நீச்சல் குளம், மலர்த் தோட்டங்கள் அமைந்த அழகிய இல்லம்.",
            "தாயாரின் மீது அளப்பரிய பாசம்; தாயார் மிகுந்த வசீகரமும் கலை உணர்வும் கொண்ட பெண்ணாக விளங்குவார்.",
            "வாழ்க்கையில் சகல சௌபாக்கியங்களும் குறைவின்றி அனுபவிக்கும் பூரண சுகபோக யோகம் உண்டு.",
            "இசை, நறுமணம், மென்மையான படுக்கைகள் மற்றும் அழகியல் சூழலில் வாழ்வதில் பேரானந்தம் அடைவார்."
        ],
        "core_traits_en": [
            "Venus attains peak directional potency (Digbala) in the 4th, establishing the celestial Malavya Mahapurusha Yoga.",
            "Destined for magnificent architectural mansions featuring botanical gardens, swimming pools, and imported supercars.",
            "Profound emotional bond with a refined, graceful, and affectionate mother who bestows vast material fortunes.",
            "Enjoys unalloyed domestic tranquility, sensory delight, and luxurious opulence without toil.",
            "Surrounded by ambient melodies, rare fragrances, plush furnishings, and an aesthetic sanctuary."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: நாட்டின் முன்னணி சொகுசு ரியல் எஸ்டேட் அதிபர், அரச மாளிகைகள்.",
            "எண்ணற்ற சொகுசு கார்களின் அணிவகுப்பு, பூரண மன அமைதி மற்றும் உலகளாவிய கௌரவம்."
        ],
        "strong_placement_en": [
            "Exalted or own house with Malavya Yoga: Premier luxury real estate tycoon, owner of celebrated heritage palaces.",
            "Commands a prestigious garage of exotic supercars, serene bliss, and universal civic honors."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் சிறுநீரக ஆரோக்கியம் பாதித்தல், சொகுசுப் பொருட்களால் கடன்கள்.",
            "வாகன விபத்துகள், வீட்டு அலங்காரங்களில் வீண் விரயங்கள் மற்றும் குடும்பத்தில் சலசலப்பு."
        ],
        "weak_placement_en": [
            "Debilitated in Virgo or afflicted: Maternal renal ailments, financial distress from reckless luxury spending.",
            "Vehicle breakdowns, litigations over residential estates, and domestic discontent."
        ],
        "career_wealth_ta": [
            "சொகுசு ரியல் எஸ்டேட், இன்டீரியர் டிசைனிங், ஆட்டோமொபைல் ஷோரூம்கள், வாசனைத் திரவிய தயாரிப்பு, நட்சத்திர விடுதிகள்.",
            "சொத்துகளின் மதிப்பு பல மடங்கு உயர்வதாலும் அழகியல் தொழில்களாலும் பல நூறு கோடி செல்வம்."
        ],
        "career_wealth_en": [
            "Superlative success in luxury architectural realty, interior aesthetics, exotic automobile dealerships, and resorts.",
            "Vast generational capital accrued through real estate appreciation and hospitality empires."
        ],
        "health_precautions_ta": [
            "இதயத்தில் கொழுப்பு, நெஞ்சு சளி, நீரிழிவு, சுவாசப் பாதையில் ஒவ்வாமை மற்றும் சிறுநீரக மந்தம்.",
            "கொழுப்பு மற்றும் பால் சார்ந்த இனிப்புகளைக் குறைத்து இதய ஆரோக்கியத்தைப் பேண வேண்டும்."
        ],
        "health_precautions_en": [
            "Susceptible to coronary lipid build-up, bronchial asthma, hyperglycemia, and sluggish renal drainage.",
            "Avoid heavy dairy confectionery, engage in cardiovascular fitness, and monitor lipid ratios."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
    },
    {
        "house": 5,
        "bhava_category": "trikona",
        "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கலை ஞானம், காதல் யோகம் & அழகான சந்ததிகள்)",
        "house_title_en": "5th House - Putra Bhava (Artistic Intellect, Romantic Bliss & Beautiful Progeny)",
        "core_traits_ta": [
            "கவிதை, நாடகம், சினிமா மற்றும் நுண்கலைகளில் அசாத்தியமான கற்பனைத் திறனும் புத்திசாலித்தனமும் கொண்டவர்.",
            "அழகான, குணவதியான மற்றும் கலைத் துறையில் சாதனை படைக்கும் பெண் குழந்தைகள் அமைய வாய்ப்புண்டு.",
            "வாழ்க்கையில் காதல், ரொமான்ஸ் மற்றும் கவர்ச்சிகரமான நட்பு வட்டாரம் நிறைந்து காணப்படும்.",
            "பூர்வ புண்ணிய பலத்தால் தொட்ட கலை முயற்சிகள் யாவும் வெற்றி பெற்று சமூகத்தில் பெரும் வரவேற்பைப் பெறும்."
        ],
        "core_traits_en": [
            "Sublime creative intellect; master of poetic romance, cinematic dramaturgy, and visual aesthetics.",
            "Blessed with beautiful, graceful, and artistically gifted children (often charming daughters).",
            "Romantic, passionate heart; experiences fulfilling love affairs and magnetic social associations.",
            "Past-life merit (Poorvapunya) fuels frictionless breakthroughs in entertainment, fashion, and speculative investments."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற திரைப்பட இயக்குநர், கலை வித்தகர், பன்னாட்டு விருதுகள், கோடீஸ்வர யோகம்.",
            "குழந்தைகள் உலகப் புகழ் பெறுவார்கள்; மகிழ்ச்சி நிறைந்த குடும்பமும், முதலீடுகளில் அபரிமிதமான லாபமும் கிட்டும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Celebrated film director, artistic luminary, international trophy winner, and multi-millionaire.",
            "Progeny become globally renowned icons; abundant financial returns from creative investments."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: காதலில் ஏமாற்றங்கள், புத்திர பாக்கியத்தில் காலதாமதம்.",
            "சினிமா அல்லது கலை முதலீடுகளில் பெரும் நிதி இழப்புகள் மற்றும் பெண்களால் அவப்பெயர்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Bitter heartbreaks, delayed childbearing, and anxieties regarding daughters.",
            "Crippling financial losses incurred through failed creative speculations and romantic scandals."
        ],
        "career_wealth_ta": [
            "திரைப்படத் தயாரிப்பாளர், ஆடை வடிவமைப்பாளர், நாவலாசிரியர், பங்குச் சந்தை முதலீட்டாளர், கலைக்கூடம், ஒப்பனைக் கலை.",
            "கலை படைப்புகளின் உரிமங்கள், சினிமா மற்றும் முதலீடுகள் மூலம் கோடிக்கணக்கில் வருவாய்."
        ],
        "career_wealth_en": [
            "Eminence as cinema producer, fashion designer, novelist, venture capital partner, and artistic curator.",
            "Immense royalties and investment jackpots derived from intellectual entertainment properties."
        ],
        "health_precautions_ta": [
            "செரிமானக் கோளாறுகள், வயிற்றுப் பகுதியில் கொழுப்பு, கருப்பை/விதைப்பை உபாதைகள் மற்றும் நீரிழிவு.",
            "சரியான நேரத்திற்கு சத்தான உணவை உட்கொள்ளுதலும், இனிப்புகளைக் கட்டுப்படுத்துவதும் அவசியம்."
        ],
        "health_precautions_en": [
            "Prone to gastric dysbiosis, abdominal adiposity, ovarian/testicular hormonal imbalances, and hyperglycemia.",
            "Maintain clean dietary habits, moderate dessert consumption, and undergo routine endocrine tests."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
    },
    {
        "house": 6,
        "bhava_category": "dusthana",
        "house_title_ta": "6-ஆம் பாவம் - சத்ru பாவம் (எதிரிகள் இல்லாமை & ஆரோக்கியப் பராமரிப்பு)",
        "house_title_en": "6th House - Satru Bhava (Harmonizing Foes & Urological Care)",
        "core_traits_ta": [
            "அமைதியான சுபாவம்; யாரிடமும் விரோதம் பாராட்டாமல் தன் கவர்ச்சியாலும் இன்முகத்தாலும் அனைவரையும் வசீகரிப்பார்.",
            "நேரடி மோதல்களைத் தவிர்த்து நயமாகப் பேசி பிரச்சினைகளைத் தீர்த்து வைக்கும் ராஜதந்திர குணம்.",
            "சுக்கிரன் 6-ஆம் பாவத்தில் இருப்பது மறைவு ஸ்தானம் என்பதால் ஆரோக்கியத்தில் அதிக கவனம் செலுத்த வேண்டும்.",
            "வேலையாட்களிடம் அன்பாகவும் பெருந்தன்மையாகவும் நடந்து கொண்டு வேலை வாங்குவார்."
        ],
        "core_traits_en": [
            "Gentle, peace-loving temperament; charms potential adversaries with disarming courtesy and warmth.",
            "Resolves conflicts through refined diplomatic tact rather than harsh adversarial clashes.",
            "Venus in the 6th occupies a dusthana; calls for conscious discipline regarding sensual excesses and health.",
            "Treats employees and domestic staff with kindness and generous consideration."
        ],
        "strong_placement_ta": [
            "சுப பலத்துடன் இருப்பின்: எதிரிகள் தானாகவே விலகிப் போதல், கடன் இல்லாத வாழ்க்கை, ஆரோக்கியத்தில் முன்னேற்றம்.",
            "அழகு சாதனங்கள், பெண்கள் நலம் மற்றும் மருத்துவத் துறைகளில் நற்பெயர் பெறுவார்."
        ],
        "strong_placement_en": [
            "Strong with benefic aspects: Complete dissolution of hostilities, debt-free living, and restored vitality.",
            "Achieves respected standing in aesthetic medicine, cosmetics dermatology, and female healthcare."
        ],
        "weak_placement_ta": [
            "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நீரிழிவு நோய் (Diabetes), சிறுநீரகக் கற்கள், பாலியல் வியாதிகள்.",
            "பெண்களால் வழக்குகளும், வீண் விரயங்களும், வேலையாட்களால் ஏமாற்றங்களும் ஏற்படலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Virgo or afflicted: Chronic diabetes, kidney stones, reproductive tract infections, and low vitality.",
            "Litigations with female acquaintances, heavy expenses on treatments, and deceit by subordinates."
        ],
        "career_wealth_ta": [
            "காஸ்மெட்டிக் அறுவை சிகிச்சை, தோல் மருத்துவம், பெண்களுக்கான ஆடைகள், அழகு நிலையங்கள், ஹோட்டல் உணவு நிர்வாகம்.",
            "வாடிக்கையாளர் சேவைகளாலும் நேர்மையான உழைப்பாலும் நிலையான வருமானம்."
        ],
        "career_wealth_en": [
            "Thrives in cosmetic surgery, dermatology, female couture, luxury spa management, and dietetics.",
            "Earns stable revenues by serving high-end clientele with personalized aesthetic solutions."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கற்கள், நீரிழிவு நோய், பாலியல் உறுப்புகளில் தொற்று, கண் பார்வைக் கோளாறு மற்றும் அதிக சோர்வு.",
            "தினமும் அதிகளவு சுத்தமான தண்ணீர் குடிப்பதும், சர்க்கரை அளவை தவறாமல் பரிசோதிப்பதும் மிக அவசியம்."
        ],
        "health_precautions_en": [
            "High susceptibility to nephrolithiasis (kidney stones), glycosuria, urinary tract infections, and chronic fatigue.",
            "Drink 3-4 liters of purified water daily, eliminate refined sugars, and schedule regular renal ultrasound scans."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
    },
    {
        "house": 7,
        "bhava_category": "kendra",
        "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (மாளவ்ய யோகம் / பேரழகான துணை & தாம்பத்திய சுகம்)",
        "house_title_en": "7th House - Kalathra Bhava (Malavya Yoga / Exceptionally Beautiful Spouse & Conjugal Bliss)",
        "core_traits_ta": [
            "சுக்கிரன் 7-ஆம் பாவத்தில் (காரகோ பாவக நாஸ்தி விதிக்கு உட்படாமல் சுப பலத்துடன் இருந்தால்) பேரழகான, காந்தக் கவர்ச்சிமிக்க வாழ்க்கைத் துணையைத் தருவார்.",
            "வாழ்க்கைத் துணை கலை உணர்வும், நற்குணமும், செல்வச் செழிப்பும் பொருந்திய குடும்பத்திலிருந்து வருவார்.",
            "தம்பதியரிடையே அளப்பரிய ரொமான்ஸ், பரஸ்பர கவர்ச்சி, தாம்பத்திய சுகம் மற்றும் ஆடம்பர வாழ்க்கை அமையும்.",
            "கூட்டு வர்த்தகத்தில் பெண்களின் ஆதரவாலும், அழகியல் தொழில்களாலும் அளப்பரிய தன லாபம் கிட்டும்."
        ],
        "core_traits_en": [
            "Venus in the 7th (unafflicted) gifts an extraordinarily gorgeous, graceful, and aesthetically refined spouse.",
            "Partner hails from a distinguished, wealthy, and cultured family; embodies charm and emotional tenderness.",
            "Marital union radiates romance, mutual adoration, sensual fulfillment, and aristocratic luxury.",
            "Commercial partnerships thrive spectacularly through female demographic engagement and aesthetic ventures."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: உலகப் பேரழகி/அழகன் போன்ற துணை, அரச யோகம்.",
            "பன்னாட்டு வர்த்தகத்தில் மாபெரும் வெற்றி, தம்பதிகள் இருவரும் சமுதாயத்தில் உன்னத நட்சத்திரங்களாகப் போற்றப்படுவர்."
        ],
        "strong_placement_en": [
            "Exalted in Pisces or in own signs forming Malavya Yoga: Marries a breathtakingly attractive partner of aristocratic lineage.",
            "Triumphs in international fashion and luxury trade, celebrated universally as an enchanting power couple."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்தியத்தில் அதிருப்தி, பல பெண்களின்/ஆண்களின் தொடர்புகளால் குடும்ப விரிசல்.",
            "விவாகரத்து வழக்குகள், துணையின் ஆரோக்கியக் குறைவு மற்றும் கூட்டாளிகளால் ஏமாற்றப்பட்டு இழப்பு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Severe conjugal friction, infidelity scandals eroding marital trust, and bitter divorces.",
            "Spouse suffers from chronic reproductive ailments; heavy losses through deceitful business partners."
        ],
        "career_wealth_ta": [
            "சர்வதேச ஆடை வர்த்தகம், அழகு சாதன ஏற்றுமதி, சினிமா-நாடகக் கூட்டாண்மை, சொகுசு விடுதிகள், திருமண நிகழ்வு மேலாண்மை (Wedding Planning).",
            "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் சர்வதேச வர்த்தகத்தாலும் கோடிக்கணக்கில் சொத்துகள் சேரும்."
        ],
        "career_wealth_en": [
            "Dominant in luxury bridal couture, cosmetics export, cinema consortiums, resort hospitality, and celebrity event management.",
            "Vast wealth multiplication generated via spousal fortunes and joint commercial syndicates."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், பாலியல் உறுப்பு அழற்சி, விரைவாதம், நீரிழிவு மற்றும் அடிவயிற்று உஷ்ணம்.",
            "முறையான மருத்துவப் பரிசோதனைகளும், உஷ்ணத்தைத் தணிக்கும் உணவுகளும் மிகவும் அவசியம்."
        ],
        "health_precautions_en": [
            "Susceptible to renal congestion, reproductive tract inflammation, prostatitis, diabetes, and pelvic heat.",
            "Strict personal hygiene, ample hydration, and periodic urogenital examinations are mandatory."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 8,
        "bhava_category": "dusthana",
        "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (தீர்க்காயுள், எதிர்பாராத தன வரவு & மறைமுக சுகம்)",
        "house_title_en": "8th House - Ayur Bhava (Long Longevity, Hidden Riches & Sudden Legacies)",
        "core_traits_ta": [
            "சுக்கிரன் 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு நீண்ட ஆயுளையும், எதிர்பாராத திடீர் தன யோகத்தையும் தரும்.",
            "மனைவி/கணவன் வழியில் பெரும் சொத்துகள், காப்பீட்டுத் தொகைகள் மற்றும் உயில் சொத்துகள் தடையின்றி வந்து சேரும்.",
            "மறைமுக இன்பங்களை அனுபவிப்பதில் ஆர்வம்; ரகசிய உறவுகள் அல்லது சாகசங்களில் ஈடுபாடு ஏற்படலாம்.",
            "ஆபத்தான சூழ்நிலைகளிலும் தன் வசீகரத்தாலும் சாதுரியத்தாலும் தப்பிக்கும் விவேகம் கொண்டிருப்பார்."
        ],
        "core_traits_en": [
            "Venus in the 8th is classically celebrated for bestowing smooth, peaceful longevity and sudden financial windfalls.",
            "Reaps substantial unearned wealth, life insurance settlements, and rich legacy inheritances through marriage.",
            "Fascinated by clandestine pleasures, private luxuries, and the hidden psychological dynamics of relationships.",
            "Survives perilous crises effortlessly through personal charm, diplomacy, and unexpected goodwill."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: அமைதியான பூரண தீர்க்காயுள், பல நூறு கோடி உயில் சொத்துகள், நவரத்தினங்கள்.",
            "துணையின் குடும்பத்திலிருந்து மாபெரும் வரதட்சணை மற்றும் அசையா சொத்துகள் வந்து குவியும்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Serene long life, multi-million dollar testamentary estates, and ancestral gems.",
            "Acquires massive dowry assets, prime real estate, and financial trusts through marital ties."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பாலியல் நோய்கள், சிறுநீரகக் கோளாறுகள், துணையின் ஆரோக்கியம் பாதித்தல்.",
            "பெண்களால் வழக்குகளும், ரகசிய உறவுகளால் சமுதாயத்தில் மானபங்கமும் ஏற்பட வாய்ப்புண்டு."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Veneral/urological infections, severe kidney disease, and spousal ill-health.",
            "Blackmail or defamation litigations arising from illicit affairs; sudden dissipation of inherited wealth."
        ],
        "career_wealth_ta": [
            "ஆயுள் காப்பீட்டு நிறுவனம், தொல்பொருள் நகை மதிப்பீட்டாளர், ரகசிய நிதி ஆலோசகர், நச்சுயியல் மருத்துவர், அழகியல் துறை.",
            "உயில் சொத்துகள், இன்சூரன்ஸ் முதிர்வுகள் மற்றும் திடீர் தன வரவால் பெரும் பணக்கார யோகம்."
        ],
        "career_wealth_en": [
            "Flourishes in insurance syndicates, antique gem valuation, private family office advisory, and aesthetic toxicology.",
            "Enormous fortune derived from testamentary inheritances, structured settlements, and windfall trusts."
        ],
        "health_precautions_ta": [
            "சிறுநீரகக் கோளாறுகள், நீரிழிவு, சிறுநீர்ப் பாதை தொற்று, பாலியல் பலவீனம் மற்றும் மூல நோய்.",
            "அதிக தண்ணீர் அருந்துவதும், சர்க்கரை மற்றும் கொழுப்பைக் கட்டுப்படுத்துவதும் மிக அவசியம்."
        ],
        "health_precautions_en": [
            "Vulnerable to renal lithiasis, diabetic nephropathy, chronic urinary tract infections, and hemorrhoids.",
            "Maintain high fluid intake, strictly regulate glycemic index, and practice defensive sexual hygiene."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 9,
        "bhava_category": "trikona",
        "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (பரம பாக்கியம், தர்ம செல்வம் & கலை யாத்திரை)",
        "house_title_en": "9th House - Bhagya Bhava (Sublime Fortune, Righteous Wealth & Cultural Travel)",
        "core_traits_ta": [
            "சுக்கிரன் 9-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் சகல சுகங்களையும் அனுபவிக்கும் மகா பாக்கிய அமைப்பாகும்.",
            "தந்தையின் மீது அளப்பரிய பாசமும் மரியாதையும்; தந்தை கலை உணர்வும் செல்வமும் பொருந்தியவராக இருப்பார்.",
            "அழகிய கோவில்கள், கலாச்சார மையங்கள் மற்றும் வெளிநாடுகளுக்கு உல்லாசப் பயணங்கள் செல்வதில் பேரானந்தம்.",
            "மனைவி வந்த பிறகு வாழ்க்கை பொற்காலமாக மாறும்; தர்ம சிந்தனையும், வறியவர்களுக்கு உதவும் வள்ளல் தன்மையும் உண்டு."
        ],
        "core_traits_en": [
            "Venus in the 9th is one of the most radiant placements for continuous worldly bliss, elegance, and good fortune.",
            "Deep affection for a cultivated, prosperous, and artistically refined father who acts as a loving patron.",
            "Delights in cultural tours, exploring architectural wonders, visiting ornate temples, and world journeys.",
            "Marriage ushers in a golden epoch of prosperity; generous philanthropist supporting artistic and cultural trusts."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: லக்ஷ்மி யோகம்! கோடானுகோடி சொத்துகள், சர்வதேச கௌரவங்கள், அரச போகம்.",
            "கலை கலாச்சார அறக்கட்டளைகளை நிறுவி உலகளாவிய நற்பெயரையும், வற்றாத செல்வத்தையும் பெறுவார்."
        ],
        "strong_placement_en": [
            "Exalted or own house: Bestows supreme Lakshmi Yoga! Multi-million dollar patrimony, global honors, and aristocratic bliss.",
            "Founds monumental cultural endowments, recognized internationally as an icon of cultural sophistication."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், மத சடங்குகளில் ஈடுபாடின்மை.",
            "வெளிநாட்டுப் பயணங்களில் பண விரயங்கள் மற்றும் காதல் விவகாரங்களால் குடும்பத்தில் கசப்புகள்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Paternal health difficulties, cynicism towards spiritual traditions, and wasted travel funds.",
            "Disruptions in overseas journeys and familial tensions caused by controversial romantic liaisons."
        ],
        "career_wealth_ta": [
            "கலாச்சாரத் தூதர், சர்வதேச சுற்றுலா அதிபர், கலைப் பல்கலைக்கழக அறங்காவலர், உயர் ஆடை ஏற்றுமதி, திரைப்பட விநியோகம்.",
            "தர்ம வழியிலும், வெளிநாட்டுத் தொடர்புகளாலும் பல தலைமுறைகளுக்கு நிலைக்கும் மாபெரும் செல்வம்."
        ],
        "career_wealth_en": [
            "Distinction as cultural ambassador, international tourism magnate, trustee of arts academies, and cinema distributor.",
            "Generates pure, enduring generational fortunes through principled cultural and creative enterprises."
        ],
        "health_precautions_ta": [
            "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம், நீரிழிவு மற்றும் கல்லீரல் கொழுப்பு.",
            "முறையான உடற்பயிற்சியும், சமச்சீரான உணவு முறையும் உடல் வனப்பை நீண்ட காலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to femoral neuropathy, sciatica sensitivity, hyperglycemia, and mild hepatic steatosis.",
            "Daily stretching, moderate low-sugar nutrition, and active recreational walking preserve bodily grace."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 10,
        "bhava_category": "kendra",
        "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (மாளவ்ய யோகம் / கலை சாம்ராஜ்யம் & மக்கள் செல்வாக்கு)",
        "house_title_en": "10th House - Karma Bhava (Malavya Yoga / Entertainment Empire & Celebrity Acclaim)",
        "core_traits_ta": [
            "சுக்கிரன் 10-ஆம் பாவத்தில் அமர்வது கலை, சினிமா, அழகு சாதனங்கள் மற்றும் பெண்களுக்கான வர்த்தகத்தில் மாபெரும் சாம்ராஜ்யத்தை உருவாக்கும்.",
            "கவர்ச்சிகரமான ஆளுமை; உயர் அதிகாரிகளுடனும் மக்கள் மத்தியிலும் அளப்பரிய அன்பும் ஆதரவும் பெறுவார்.",
            "தொழிலில் புதுமையான அழகியல் யுக்திகளைக் கையாண்டு லட்சக்கணக்கான வாடிக்கையாளர்களை ஈர்க்கும் சாமர்த்தியம்.",
            "சமூகத்தில் பெரும் புகழும், பன்னாட்டு விருதுகளும், ஆடம்பரமான வாழ்க்கை முறையும் பெறுவார்."
        ],
        "core_traits_en": [
            "Venus in the 10th builds towering commercial empires across entertainment, cosmetics, cinema, and luxury lifestyle.",
            "Irresistible executive charisma; wins unstinting affection and patronage from civic dignitaries and the public.",
            "Infuses commerce with creative elegance, captivating millions of devoted consumers worldwide.",
            "Celebrated with stellar public fame, international industry awards, and an enviable, glamorous lifestyle."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: உலக சினிமா சூப்பர் ஸ்டார், ஃபேஷன் சாம்ராஜ்ய அதிபர்.",
            "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, சமுதாயத்தின் முதன்மை நட்சத்திரமாக முடிசூடுவார்."
        ],
        "strong_placement_en": [
            "Exalted in Pisces or in own signs forming Malavya Yoga: International cinema icon, chairman of global luxury fashion conglomerates.",
            "Conferred premier cultural awards by heads of state; reigns as the undisputed monarch of style."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் வீழ்ச்சி, பெண்களால் அவப்பெயர் மற்றும் வழக்குகளால் நஷ்டம்.",
            "வாடிக்கையாளர் நம்பிக்கையை இழத்தலும், உத்தியோகத்தில் நிலையற்ற தன்மையும் உண்டாகலாம்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Sudden downfall in public prestige, controversies with female associates, and litigation losses.",
            "Erosion of brand equity, workplace scandals, and volatile employment trajectory."
        ],
        "career_wealth_ta": [
            "திரைப்படத்துறை, தொலைக்காட்சி, ஃபேஷன் டிசைனிங், அழகு நிலையங்கள், வைர வர்த்தகம், ஐந்து நட்சத்திர விடுதிகள், வாசனைத் திரவியங்கள்.",
            "கலை படைப்புகளாலும் பிராண்ட் அம்பாசிடர் ஒப்பந்தங்களாலும் பல நூறு கோடி செல்வம் குவியும்."
        ],
        "career_wealth_en": [
            "Dominant in film production, digital entertainment, haute couture, diamond retail, luxury hospitality, and perfumery.",
            "Accumulates colossal multi-million dollar capital via commercial royalties, equity stakes, and global brand endorsements."
        ],
        "health_precautions_ta": [
            "பணிச்சுமையால் நீரிழிவு, மூட்டு வலி, ரத்த அழுத்தம் மற்றும் தூக்கமின்மை.",
            "ஆடம்பர விருந்துகளையும், மது-கொழுப்பு உணவுகளையும் தவிர்த்து உடலை ஆரோக்கியமாகப் பேண வேண்டும்."
        ],
        "health_precautions_en": [
            "Prone to metabolic syndrome, knee cartilage wear, hypertension, and occupational insomnia.",
            "Avoid lavish late-night banquets, eliminate alcohol and trans-fats, and prioritize deep restorative rest."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 11,
        "bhava_category": "upachaya",
        "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / பெண்களின் பேராதரவு & குபேர யோகம்)",
        "house_title_en": "11th House - Labha Bhava (Massive Liquid Wealth, Women's Patronage & Wish Fulfillment)",
        "core_traits_ta": [
            "சுக்கிரன் 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது அளவில்லாத செல்வச் செழிப்பையும், அனைத்து ஆசைகளும் உடனே நிறைவேறுதலையும் தரும்.",
            "செல்வாக்கு மிக்க பெண்களின் நட்பும், ஆதரவும் கிடைத்து வாழ்வில் அடுத்தடுத்து மாபெரும் உயர்வுகளை அடைவார்.",
            "சொகுசு கார்கள், வைர நகைகள், பட்டு ஆடைகள் மற்றும் உயர்ரக வசதிகள் எப்போதும் நிறைந்து காணப்படும்.",
            "மூத்த சகோதர சகோதரிகளிடம் அளப்பரிய பாசம் நிலவும்; அவர்களால் பல கோடி ரூபாய் தன லாபம் கிட்டும்."
        ],
        "core_traits_en": [
            "Venus in the 11th (an Upachaya house) is a golden engine for compounding luxury wealth and effortless wish-fulfillment.",
            "Enjoys decisive patronage, funding, and mentorship from highly placed, affluent women across sectors.",
            "Surrounded by premium sports cars, diamond jewellery, bespoke designer wardrobes, and effortless luxury.",
            "Cherishes deep fraternal devotion with elder siblings, who facilitate lucrative investments and social prominence."
        ],
        "strong_placement_ta": [
            "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், சொகுசு மாளிகைகள், குபேர யோகம்.",
            "திரைப்படம், அழகு சாதனங்கள் மற்றும் கலை வர்த்தகத்தில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
        ],
        "strong_placement_en": [
            "Exalted or in own house: Bestows multi-billion dollar liquid holdings, luxury estates, and supreme Kubera Yoga.",
            "Ranks among the foremost wealthy magnates in entertainment, cosmetics, and luxury consumer goods."
        ],
        "weak_placement_ta": [
            "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், பெண்களால் வீண் விரயங்கள்.",
            "லாபங்கள் கைநழுவிப் போதல் அல்லது ஆடம்பரச் செலவுகளால் வங்கி இருப்பு குறைதல்."
        ],
        "weak_placement_en": [
            "Debilitated or afflicted: Exploitation by counterfeit socialite companions, financial bleedings through indiscreet liaisons.",
            "Anticipated dividends vanish through profligate party expenditures and unhedged investments."
        ],
        "career_wealth_ta": [
            "சினிமா நிதி முதலீடு, சொகுசு கார்கள் வர்த்தகம், வைர நகைக் கடைகள், பெண்களுக்கான ஆடைகள், நட்சத்திர ஹோட்டல்கள், வென்ச்சர் கேபிடல்.",
            "முதலீடுகளின் அதிவேக வளர்ச்சியாலும் பெண்கள் ஆதரவாலும் கோடீஸ்வர யோகம்."
        ],
        "career_wealth_en": [
            "Lucrative success in film finance syndication, exotic car imports, diamond retail chains, luxury apparel, and venture capital.",
            "Extraordinary capital multiplication placing the native in the elite billionaire tier."
        ],
        "health_precautions_ta": [
            "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், நீரிழிவு மற்றும் சரும அலர்ஜி.",
            "கால் நரம்புகளுக்கான உடற்பயிற்சியும், ரத்த சர்க்கரை பரிசோதனைகளும் நலம் காக்கும்."
        ],
        "health_precautions_en": [
            "Susceptible to left-ear ache, ankle ligament stiffness, hyperglycemia, and skin dermatosis.",
            "Daily ankle mobility drills, compression wear during flights, and strict glycemic monitoring."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    },
    {
        "house": 12,
        "bhava_category": "dusthana",
        "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அயன சயன சுகம் / சொகுசு வெளிநாட்டு வாழ்க்கை & ஆன்மீக கலை)",
        "house_title_en": "12th House - Vraya Bhava (Supreme Bedroom Pleasures, Luxurious Foreign Living & Spiritual Art)",
        "core_traits_ta": [
            "சுக்கிரன் 12-ஆம் பாவத்தில் அமர்வது காரகோ பாவக நாஸ்தி இல்லாத மிகச்சிறந்த அயன சயன சுகத்தைத் தரும் ராஜ யோகமாகும்.",
            "மஞ்சத்தில் பூரண சுகம், அழகான தாம்பத்திய வாழ்க்கை, நறுமணம் வீசும் ஆடம்பர படுக்கையறைகள் மற்றும் ஆழ்ந்த தூக்கம்.",
            "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அளப்பரிய செல்வமும், சொகுசு வாழ்க்கையும் கிட்டும்.",
            "பணத்தை ஆடம்பரப் பொருட்கள், கலைப் படைப்புகள் மற்றும் தர்ம காரியங்களுக்காக தாராளமாக வாரி வழங்குவார்."
        ],
        "core_traits_en": [
            "Venus in the 12th is classically hailed as an extraordinary exception: bestows unmatched sensory pleasure and bedroom bliss (Ayana Sayana Sukha).",
            "Exquisite marital intimacy, aromatic bedrooms furnished in plush silks, and deeply restorative, peaceful sleep.",
            "Achieves peak wealth, glamorous status, and aristocratic comforts when settled in foreign or overseas territories.",
            "Spends with magnificent liberality on bespoke luxuries, world art treasures, and noble philanthropic donations."
        ],
        "strong_placement_ta": [
            "மீனத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் அரண்மனை போன்ற மாளிகை, பன்னாட்டுச் செல்வம்.",
            "அயன சயன சுகம் பூரணமாகக் கிட்டும்; சமுதாயத்தில் பெரும் மதிப்பும், ஆன்மீக முக்தியும் பெறுவார்."
        ],
        "strong_placement_en": [
            "Exalted in Pisces or in own house: Commands fairy-tale estates in prime overseas locales; vast foreign exchange wealth.",
            "Unblemished conjugal ecstasy, blissful peace of mind, and sublime spiritual liberation (Moksha)."
        ],
        "weak_placement_ta": [
            "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்திய சுகக் குறைவு, பாலியல் வியாதிகள், தூக்கமின்மை.",
            "இடது கண் பாதிப்பு, ஆடம்பரப் பழக்கங்களால் கடன் மற்றும் வெளிநாட்டில் சட்டச் சிக்கல்கள் வரலாம்."
        ],
        "weak_placement_en": [
            "Debilitated in Virgo or afflicted: Bedroom coldness, urogenital infections, acute insomnia, and left eye vision defects.",
            "Heavy debts incurred through reckless nocturnal dissipation; legal disputes with foreign authorities."
        ],
        "career_wealth_ta": [
            "சர்வதேச சொகுசு விடுதிகள், கப்பல் போக்குவரத்து, வெளிநாட்டுத் தூதரகங்கள், வாசனைத் திரவிய ஏற்றுமதி, உலகளாவிய ஆடை வர்த்தகம்.",
            "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
        ],
        "career_wealth_en": [
            "Dominates in international luxury hospitality, cruise liners, consular diplomacy, perfume export, and global fashion.",
            "Colossal income denominated in hard foreign currencies flowing from overseas holdings."
        ],
        "health_precautions_ta": [
            "இடது கண் பார்வைக் கோளாறு, பாதங்களில் வலி, நீரிழிவு, சிறுநீரகக் கோளாறுகள் மற்றும் தூக்கமின்மை.",
            "தூங்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், பாதங்களை மசாஜ் செய்வதும் நல்ல தூக்கத்தைத் தரும்."
        ],
        "health_precautions_en": [
            "Prone to left-eye refractive strain, peripheral foot neuralgia, diabetes, renal weakness, and insomnia.",
            "Nightly cold eye-compresses, gentle foot reflexology, and regular renal health screenings."
        ],
        "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
    }
]
