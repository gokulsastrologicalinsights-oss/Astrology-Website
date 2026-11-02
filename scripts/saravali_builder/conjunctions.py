# scripts/saravali_builder/conjunctions.py
"""Saravali Chapters 15 & 16: Two-Planet and Three-Planet Conjunctions.
21 Two-Planet combinations (Ch. 15, v. 2-22)
19 Three-Planet combinations (Ch. 16, v. 1-38)
"""

def get_conjunction_rules():
    rules = []

    # 1. Chapter 15: 21 Two-Planet Conjunctions
    two_planet_data = [
        ("Sun", "Moon", "RULE-SARAVALI-CONJ-SUN-MOO",
         "Sun and Moon Conjunction (Ravi-Chandra Yoga)", "சூரியன் மற்றும் சந்திரன் சேர்க்கை (ரவி-சந்திர யோகம்)",
         "According to Saravali Ch. 15, v. 2, the conjunction of Sun and Moon makes the native skilled in machinery, stone or masonry work, fond of water and submissive to women, but physically laborious.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 2-ன் படி சூரியன் - சந்திரன் சேர்க்கை உள்ளவர் இயந்திரப்பணி, கட்டிடக்கலை அல்லது சிற்ப வேலையில் தேர்ச்சியும், கடின உழைப்பும் கொண்டிருப்பார்.",
         "Amavasya Conjunction: Sun and Moon in the same sign combine royal authority with emotional subtlety.",
         "அமாவாசை யோகம்: சூரியனும் சந்திரனும் ஒரே ராசியில் இணைவது மனோபலம் மற்றும் காரிய உறுதியை இணைக்கும் அமைப்பாகும்.",
         "Saravali, Ch. 15, Sloka 2", "SeverityLevel.MIXED"),

        ("Sun", "Mars", "RULE-SARAVALI-CONJ-SUN-MAR",
         "Sun and Mars Conjunction (Ravi-Kuja Yoga)", "சூரியன் மற்றும் செவ்வாய் சேர்க்கை (ரவி-குஜ யோகம்)",
         "Per Saravali Ch. 15, v. 3, Sun and Mars conjunct make the native immensely valorous, skilled in weapons, sharp, heroic, harsh in speech, prone to wounds and fiery temperament.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 3-ன் படி சூரியன் - செவ்வாய் சேர்க்கை ஜாதகருக்கு மகா வீரம், அஞ்சாநெஞ்சம், போர்த்திறன், ஆயுத கையாளுமை மற்றும் முன்சீற்றத்தைத் தரும்.",
         "Agni Graha Conjunction: Double fire element confers martial and executive leadership.",
         "அக்னி கிரகங்களின் சேர்க்கை: அதிகாரம், ராணுவம் மற்றும் தலைமைத் தாங்கும் ஆற்றலை நல்கும்.",
         "Saravali, Ch. 15, Sloka 3", "SeverityLevel.FAVORABLE"),

        ("Sun", "Mercury", "RULE-SARAVALI-CONJ-SUN-MER",
         "Sun and Mercury Conjunction (Budhaditya Yoga)", "சூரியன் மற்றும் புதன் சேர்க்கை (புதாதித்ய யோகம்)",
         "Saravali Ch. 15, v. 4 extols Sun and Mercury: The native is learned, eloquent, sharp-witted, wealthy, famous, favored by kings, and accomplished in all sciences.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 4 புதாதித்ய யோகத்தைப் புகழ்கிறது: பேரறிஞர், நாவன்மை, கணிதம்-சாஸ்திரங்களில் புலமை, அரசு கௌரவம் மற்றும் செல்வந்தராகத் திகழ்வார்.",
         "Budhaditya Yoga: Conjunction of wisdom (Mercury) and soul/vitality (Sun) produces supreme intellect.",
         "புதாதித்ய யோகம்: அறிவின் காரகன் புதனும் ஆத்மகாரகன் சூரியனும் இணைவது உச்சபட்ச புத்தி கூர்மையை அருளும்.",
         "Saravali, Ch. 15, Sloka 4", "SeverityLevel.FAVORABLE"),

        ("Sun", "Jupiter", "RULE-SARAVALI-CONJ-SUN-JUP",
         "Sun and Jupiter Conjunction (Guru-Aditya Yoga)", "சூரியன் மற்றும் குரு சேர்க்கை (குரு-ஆதித்ய யோகம்)",
         "According to Saravali Ch. 15, v. 5, Sun and Jupiter conjunct makes one a minister or trusted counselor, endowed with deep spiritual wisdom, righteous, wealthy, and universally respected.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 5-ன் படி சூரியன் - குரு சேர்க்கை ஒருவரை அரச ஆலோசகர் அல்லது மந்திரியாக்கும்; ஆன்மீக ஞானம், தர்ம குணம் மற்றும் அழியாத புகழ் தரும்.",
         "Guru-Aditya Yoga: Union of divine wisdom and sovereign authority yields virtuous governance.",
         "குரு-ஆதித்ய யோகம்: ஞானமும் அதிகாரமும் இணைந்து சிறந்த தலைவரையும் தர்மவானையும் உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 5", "SeverityLevel.FAVORABLE"),

        ("Sun", "Venus", "RULE-SARAVALI-CONJ-SUN-VEN",
         "Sun and Venus Conjunction (Ravi-Sukra Yoga)", "சூரியன் மற்றும் சுக்கிரன் சேர்க்கை (ரவி-சுக்கிர யோகம்)",
         "Per Saravali Ch. 15, v. 6, Sun and Venus together make the native fond of drama, stage arts, music, skilled in weapons, attractive, but prone to eye ailments or relationship friction.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 6-ன் படி சூரியன் - சுக்கிரன் சேர்க்கை நாடகம், இசை, கலைகளில் ஆர்வம், வசீகரத் தோற்றம்; எனினும் கண் உபாதை அல்லது இல்லறத்தில் சலனம் தரலாம்.",
         "Kala-Aditya Yoga: Solar illumination over Venusian artistic expressions.",
         "கலை-ஆதித்ய யோகம்: சுக்கிரனின் கலைத்திறனும் சூரியனின் வெளிச்சமும் இணையும் வடிவம்.",
         "Saravali, Ch. 15, Sloka 6", "SeverityLevel.MIXED"),

        ("Sun", "Saturn", "RULE-SARAVALI-CONJ-SUN-SAT",
         "Sun and Saturn Conjunction (Ravi-Sani Yoga)", "சூரியன் மற்றும் சனி சேர்க்கை (ரவி-சனி யோகம்)",
         "Saravali Ch. 15, v. 7 indicates Sun and Saturn conjunction causes conflict with authority/father, proficiency in metallurgy and minerals, laborious rise, and somber endurance.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 7-ன் படி சூரியன் - சனி சேர்க்கை தந்தையுடன் முரண்பாடு, உலோகம்-சுரங்கத் தொழிலில் நிபுணத்துவம் மற்றும் கடுமையான உழைப்பால் வெற்றியைத் தரும்.",
         "Pithru-Putra Sangama: Natural adversaries produce tenacity and discipline through struggle.",
         "பித்ரு-புத்திர யோகம்: இரு பெரும் முரண்பட்ட கிரகங்களின் சேர்க்கை வாழ்வின் ஆரம்பப் போராட்டத்தையும் முடிவில் முதிர்ச்சியையும் தரும்.",
         "Saravali, Ch. 15, Sloka 7", "SeverityLevel.MIXED"),

        ("Moon", "Mars", "RULE-SARAVALI-CONJ-MOO-MAR",
         "Moon and Mars Conjunction (Chandra-Mangala Yoga)", "சந்திரன் மற்றும் செவ்வாய் சேர்க்கை (சந்திர-மங்கள யோகம்)",
         "Saravali Ch. 15, v. 8 extols Moon and Mars: The native is a wealthy merchant, dealer in pottery, leather, or metals, bold, valorous, self-reliant, and fiercely ambitious.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 8 சந்திர-மங்கள யோகத்தை விவரிக்கிறது: அபரிமித தன யோகம், வணிகத் திறன், நிலம்-கனிம வர்த்தகம், அஞ்சாமை மற்றும் தலைமைப் பண்பு.",
         "Chandra-Mangala Wealth Configuration: Mind (Moon) propelled by action (Mars) yields financial prosperity.",
         "சந்திர-மங்கள யோகம்: மனமும் வேகமும் இணைந்து தொழில் மற்றும் பொருளாதார மேன்மையை உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 8", "SeverityLevel.FAVORABLE"),

        ("Moon", "Mercury", "RULE-SARAVALI-CONJ-MOO-MER",
         "Moon and Mercury Conjunction (Chandra-Budha Yoga)", "சந்திரன் மற்றும் புதன் சேர்க்கை (சந்திர-புத யோகம்)",
         "Per Saravali Ch. 15, v. 9, Moon and Mercury conjunct make the person polite, sweet-spoken, poet, interpreter of classical treatises, wealthy, famous, and gentle-natured.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 9-ன் படி சந்திரன் - புதன் சேர்க்கை இனிமையான பேச்சு, கவிதை நயம், சாஸ்திர விளக்கம் அளிக்கும் புலமை, அடக்கம் மற்றும் பெரும் புகழைத் தரும்.",
         "Budha-Chandra Saraswati Yoga: Blend of emotional perception and analytical intellect.",
         "புத-சந்திர சரஸ்வதி யோகம்: உணர்வும் பகுத்தறிவும் இணைந்து கலை-இலக்கிய மேதமையை உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 9", "SeverityLevel.FAVORABLE"),

        ("Moon", "Jupiter", "RULE-SARAVALI-CONJ-MOO-JUP",
         "Moon and Jupiter Conjunction (Gaja Kesari Conjunction)", "சந்திரன் மற்றும் குரு சேர்க்கை (கஜ கேசரி சேர்க்கை யோகம்)",
         "Saravali Ch. 15, v. 10 proclaims Moon and Jupiter: The native is righteous, wealthy, universally respected, blessed with noble sons, serene, famous, and steadfast in character.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 10 சந்திரன் - குரு சேர்க்கையைப் போற்றுகிறது: களங்கமற்ற ஒழுக்கம், பரந்த புகழ், நற்குணமுள்ள மக்கள் செல்வம், அழியாத தனம் மற்றும் சமூக ஆளுமை.",
         "Gaja Kesari Conjunction: Direct co-presence of Jupiter and Moon bestows royal dignity.",
         "கஜ கேசரி யோக சேர்க்கை: குருவும் சந்திரனும் இணைவது யானை மீதமர்ந்த சிங்கத்தைப் போல தலைமைத் தன்மையை அருளும்.",
         "Saravali, Ch. 15, Sloka 10", "SeverityLevel.FAVORABLE"),

        ("Moon", "Venus", "RULE-SARAVALI-CONJ-MOO-VEN",
         "Moon and Venus Conjunction (Chandra-Sukra Yoga)", "சந்திரன் மற்றும் சுக்கிரன் சேர்க்கை (சந்திர-சுக்கிர யோகம்)",
         "According to Saravali Ch. 15, v. 11, Moon and Venus together make the native skilled in textiles, cosmetics, gems, highly charming, loving, affluent, and surrounded by comforts.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 11-ன் படி சந்திரன் - சுக்கிரன் சேர்க்கை ஆடை, ஆபரணம், நவரத்தின வர்த்தகம், பேரழகு, சகல வசதிகள் மற்றும் சுகபோக வாழ்வை நல்கும்.",
         "Soumya Shukra-Chandra: Double benefic water-element pairing gives aesthetic brilliance.",
         "சுப சந்திர-சுக்கிர யோகம்: இரட்டை சுப கிரகங்களின் சேர்க்கை கலை, அழகு மற்றும் வசீகரத்தை அள்ளித் தரும்.",
         "Saravali, Ch. 15, Sloka 11", "SeverityLevel.FAVORABLE"),

        ("Moon", "Saturn", "RULE-SARAVALI-CONJ-MOO-SAT",
         "Moon and Saturn Conjunction (Punarphoo / Shani-Chandra)", "சந்திரன் மற்றும் சனி சேர்க்கை (புனர்பூ / சனி-சந்திர யோகம்)",
         "Saravali Ch. 15, v. 12 states Moon and Saturn conjunct makes one sober, patient, keeper of vehicles/horses, serious thinker, disciplined, but prone to bouts of melancholia.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 12-ன் படி சந்திரன் - சனி சேர்க்கை தீவிர சிந்தனை, பொறுமை, வாகனப் பராமரிப்பு, ஒழுக்கம் தரும்; மன அமைதியில் சலனம் ஏற்படலாம்.",
         "Punarphoo Yoga: Saturn's sobering touch on the lunar mind creates deep contemplation.",
         "புனர்பூ யோகம்: சந்திரனின் மனோபாவத்தில் சனியின் கட்டுப்பாடு ஆழமான ஆன்மீக-தத்துவ ஞானத்தை உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 12", "SeverityLevel.MIXED"),

        ("Mars", "Mercury", "RULE-SARAVALI-CONJ-MAR-MER",
         "Mars and Mercury Conjunction (Kuja-Budha Yoga)", "செவ்வாய் மற்றும் புதன் சேர்க்கை (குஜ-புத யோகம்)",
         "Per Saravali Ch. 15, v. 13, Mars and Mercury together make the native skilled in trade, wrestling, medicine, metallurgy, sharp debater, and successful in practical engineering.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 13-ன் படி செவ்வாய் - புதன் சேர்க்கை வர்த்தகம், விளையாட்டு, மருத்துவம், பொறியியல் மற்றும் வாதத் திறமையில் பெரும் சாதனைகளைத் தரும்.",
         "Techno-Martial Synthesis: Fusion of analytical skill (Mercury) and mechanical force (Mars).",
         "தொழில்நுட்ப வீரிய யோகம்: புதனின் அறிவும் செவ்வாயின் வேகமும் இணைந்து தொழில்நுட்ப வெற்றியைத் தரும்.",
         "Saravali, Ch. 15, Sloka 13", "SeverityLevel.FAVORABLE"),

        ("Mars", "Jupiter", "RULE-SARAVALI-CONJ-MAR-JUP",
         "Mars and Jupiter Conjunction (Guru-Mangala Yoga)", "செவ்வாய் மற்றும் குரு சேர்க்கை (குரு-மங்கள யோகம்)",
         "Saravali Ch. 15, v. 14 praises Mars and Jupiter: Leader of a city or army, learned, wealthy, truthful, expert architect or administrator, honored by kings.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 14 குரு-மங்கள யோகத்தைப் போற்றுகிறது: படைத்தளபதி அல்லது நகரத் தலைவர், கட்டிடக்கலை நிபுணர், தர்மவான், அரச மரியாதை மற்றும் சிறந்த செல்வாக்கு.",
         "Guru-Mangala Yoga: Divine wisdom guiding courageous action creates an upright leader.",
         "குரு-மங்கள யோகம்: தர்ம நெறியுடன் கூடிய வீரம் மாபெரும் சமூகத் தலைவரையும் நிர்வாகியையும் உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 14", "SeverityLevel.FAVORABLE"),

        ("Mars", "Venus", "RULE-SARAVALI-CONJ-MAR-VEN",
         "Mars and Venus Conjunction (Bhrigu-Mangala Yoga)", "செவ்வாய் மற்றும் சுக்கிரன் சேர்க்கை (பிருகு-மங்கள யோகம்)",
         "According to Saravali Ch. 15, v. 15, Mars and Venus conjunct make the native passionate, handsome, skilled in crafts, fond of luxury, charismatic, and active in sports or entertainment.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 15-ன் படி செவ்வாய் - சுக்கிரன் சேர்க்கை அதீத கவர்ச்சி, கலைகளில் ஈடுபாடு, வசீகரமான ஆளுமை, விளையாட்டு மற்றும் சுகபோக நாட்டத்தை அளிக்கும்.",
         "Kama-Kuja Configuration: Union of passion and physical magnetism.",
         "காம-குஜ அமைப்பு: காதலும் கவர்ச்சியும் இணைந்து கலை மற்றும் உலகியல் ஈர்ப்பை அதிகரிக்கும்.",
         "Saravali, Ch. 15, Sloka 15", "SeverityLevel.MIXED"),

        ("Mars", "Saturn", "RULE-SARAVALI-CONJ-MAR-SAT",
         "Mars and Saturn Conjunction (Kuja-Sani Yoga)", "செவ்வாய் மற்றும் சனி சேர்க்கை (குஜ-சனி யோகம்)",
         "Saravali Ch. 15, v. 16 notes Mars and Saturn together produce exceptional technical mastery, handling of heavy metals/machinery, perseverance, but potential friction with peers.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 16-ன் படி செவ்வாய் - சனி சேர்க்கை கடின உழைப்பு, கனரக இயந்திரங்கள்-தொழில்நுட்பத்தில் தேர்ச்சி மற்றும் விடாமுயற்சியால் சாதனைகளைத் தரும்.",
         "Yama-Kuja Combination: Hard martial discipline and tireless industrial execution.",
         "எம-குஜ யோகம்: கடுமையான உழைப்பும் எஃகு போன்ற மன உறுதியும் தொழில்துறை சாதனைகளை உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 16", "SeverityLevel.MIXED"),

        ("Mercury", "Jupiter", "RULE-SARAVALI-CONJ-MER-JUP",
         "Mercury and Jupiter Conjunction (Budha-Guru Yoga)", "புதன் மற்றும் குரு சேர்க்கை (புத-குரு யோகம்)",
         "Saravali Ch. 15, v. 17 proclaims Mercury and Jupiter: Exceptional scholar, master of sacred scriptures, eloquent advisor, esteemed writer, wealthy, and universally revered.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 17 புத-குரு சேர்க்கையை மகா வித்வான் யோகமாகப் புகழ்கிறது: வேத-சாஸ்திர விற்பன்னர், தலைசிறந்த எழுத்தாளர், நீதிமான் மற்றும் சமுதாய குரு.",
         "Brahma-Budha Saraswati Yoga: Pure intellectual and spiritual enlightenment.",
         "பிரம்ம-புத சரஸ்வதி யோகம்: அறிவுத் திறனும் ஆன்மீக ஞானமும் இணைந்து பெரும் மேதமையை அருளும்.",
         "Saravali, Ch. 15, Sloka 17", "SeverityLevel.FAVORABLE"),

        ("Mercury", "Venus", "RULE-SARAVALI-CONJ-MER-VEN",
         "Mercury and Venus Conjunction (Budha-Sukra Yoga)", "புதன் மற்றும் சுக்கிரன் சேர்க்கை (புத-சுக்கிர யோகம்)",
         "Per Saravali Ch. 15, v. 18, Mercury and Venus conjunct make the native eloquent, poet, attractive, proficient in arts and music, wealthy, humorous, and beloved by society.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 18-ன் படி புதன் - சுக்கிரன் சேர்க்கை இனிமையான பேச்சு, நயமான கவிதை, இசை-நாட்டியத் தேர்ச்சி, நகைச்சுவை உணர்வு மற்றும் பெரும் செல்வத்தைத் தரும்.",
         "Gandharva Yoga: Aesthetic brilliance, refined artistic taste, and magnetic eloquence.",
         "காந்தர்வ யோகம்: கலை ஞானமும் நாவன்மையும் இணைந்து சமூகத்தில் இணையற்ற வசீகரத்தை நல்கும்.",
         "Saravali, Ch. 15, Sloka 18", "SeverityLevel.FAVORABLE"),

        ("Mercury", "Saturn", "RULE-SARAVALI-CONJ-MER-SAT",
         "Mercury and Saturn Conjunction (Budha-Sani Yoga)", "புதன் மற்றும் சனி சேர்க்கை (புத-சனி யோகம்)",
         "Saravali Ch. 15, v. 19 states Mercury and Saturn together make one skilled in accounts, calligraphy, detailed craftsmanship, patient student of shastras, and cautious manager of assets.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 19-ன் படி புதன் - சனி சேர்க்கை கணக்கியல், சிற்பக்கலை, ஆவணப் பராமரிப்பு, பொறுமையான ஆய்வு மற்றும் சொத்துகளைப் பாதுகாக்கும் நிதானத்தை அருளும்.",
         "Analytical Endurance: Sharp logic grounded by Saturnian prudence.",
         "ஆய்வு ஒழுக்க யோகம்: கூரிய அறிவும் சனியின் நிதானமும் இணைந்து கணக்கு மற்றும் ஆராய்ச்சித் திறனை வளர்க்கும்.",
         "Saravali, Ch. 15, Sloka 19", "SeverityLevel.FAVORABLE"),

        ("Jupiter", "Venus", "RULE-SARAVALI-CONJ-JUP-VEN",
         "Jupiter and Venus Conjunction (Guru-Sukra Yoga)", "குரு மற்றும் சுக்கிரன் சேர்க்கை (குரு-சுக்கிர யோகம்)",
         "Saravali Ch. 15, v. 20 extols Jupiter and Venus: Extremely learned, endowed with high virtue, noble preceptor, possessor of abundant wealth, conveyances, and unshakeable dignity.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 20 இரு பெரும் சுபர்களின் சேர்க்கையை போற்றுகிறது: உன்னதமான பண்புகள், பேராசிரியராகும் தகுதி, நவரத்தினங்கள், வாகன யோகம் மற்றும் அழியாத செல்வாக்கு.",
         "Ubhaya-Guru Yoga: Union of Deva-Guru (Jupiter) and Asura-Guru (Venus) confers complete mastery.",
         "உபய-குரு யோகம்: தேவ குருவும் அசுர குருவும் இணைந்து அனைத்து சாஸ்திரங்களிலும் முழுமையான மேலாண்மையை அளிப்பர்.",
         "Saravali, Ch. 15, Sloka 20", "SeverityLevel.FAVORABLE"),

        ("Jupiter", "Saturn", "RULE-SARAVALI-CONJ-JUP-SAT",
         "Jupiter and Saturn Conjunction (Guru-Sani Yoga)", "குரு மற்றும் சனி சேர்க்கை (குரு-சனி யோகம்)",
         "According to Saravali Ch. 15, v. 21, Jupiter and Saturn conjunct make the native founder of temples or charitable trusts, renowned civic leader, wealthy, patient, and honored by the state.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 21-ன் படி குரு - சனி சேர்க்கை திருக்கோயில்கள் மற்றும் தர்ம அறக்கட்டளைகளை நிறுவுபவர், முதிர்ந்த நிர்வாகி, அரச கௌரவம் மற்றும் நிலைத்த செல்வம் கொண்டவர்.",
         "Brahma-Shani Sovereign Stability: Spiritual righteousness married to grounded realism.",
         "பிரம்ம-சனி யோகம்: ஆன்மீக தர்மமும் எதார்த்த உழைப்பும் இணைந்து நீடித்த சமூக அமைப்புகளையும் புகழையும் உருவாக்கும்.",
         "Saravali, Ch. 15, Sloka 21", "SeverityLevel.FAVORABLE"),

        ("Venus", "Saturn", "RULE-SARAVALI-CONJ-VEN-SAT",
         "Venus and Saturn Conjunction (Sukra-Sani Yoga)", "சுக்கிரன் மற்றும் சனி சேர்க்கை (சுக்கிர-சனி யோகம்)",
         "Saravali Ch. 15, v. 22 states Venus and Saturn together make the native skilled in painting, sculpture, handicrafts, steadfast in relationships, wealthy, and successful in international trade.",
         "சாராவளி அத்தியாயம் 15, சுலோகம் 22-ன் படி சுக்கிரன் - சனி சேர்க்கை ஓவியம், சிற்பக்கலை, கைவினைத் தொழிலில் நிபுணத்துவம், உண்மையான பற்று மற்றும் வெளிநாட்டு வணிக வெற்றியைக் கொடுக்கும்.",
         "Shilpi Yoga: Artistic imagination crystallized through disciplined craftsmanship.",
         "சிற்பி யோகம்: கலை உணர்வும் கடின உழைப்பும் இணைந்து சிறந்த படைப்புகளையும் நிலையான வருமானத்தையும் தரும்.",
         "Saravali, Ch. 15, Sloka 22", "SeverityLevel.FAVORABLE")
    ]

    for p1, p2, r_id, name_en, name_ta, desc_en, desc_ta, princ_en, princ_ta, sloka, sev in two_planet_data:
        rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{r_id}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="saravali_classics",
        subcategory="saravali_graha_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "planet_conjunction",
            "planets": ["{p1}", "{p2}"],
            "chart": "d1"
        }},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="{princ_en}",
        astrological_principle_ta="{princ_ta}",
        source_reference="{sloka}",
        limitations_en="Combustion, sign dignity, and aspects from malefic or benefic planets modify the tangible manifestation.",
        limitations_ta="அஸ்தமனம், நின்ற ராசியின் நட்பு/பகை மற்றும் பிற கிரகப் பார்வைகள் பலன்களின் தீவிரத்தை மாற்றியமைக்கும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    # 2. Chapter 16: Three-Planet Conjunctions
    three_planet_data = [
        (["Sun", "Moon", "Mars"], "RULE-SARAVALI-TRI-SUN-MOO-MAR",
         "Sun, Moon, and Mars Conjunction (Saravali Tri-Graha)", "சூரியன், சந்திரன் மற்றும் செவ்வாய் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 2: The native is fearless, warlike, energetic, skilled in mechanical or metal works, and victorious over rivals.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 2: அஞ்சாமை, போர்க்குணம், இயந்திரத் துறையில் நிபுணத்துவம் மற்றும் எதிரிகளை அடக்கும் ஆற்றல்.",
         "Saravali, Ch. 16, Sloka 2", "SeverityLevel.MIXED"),

        (["Sun", "Moon", "Mercury"], "RULE-SARAVALI-TRI-SUN-MOO-MER",
         "Sun, Moon, and Mercury Conjunction (Saravali Tri-Graha)", "சூரியன், சந்திரன் மற்றும் புதன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 3: Scholar, eloquent writer, handsome, respected by kings, possessing noble intellect and administrative tact.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 3: பேரறிஞர், நயமான எழுத்தாளர், அரச கௌரவம், கூரிய புத்தி மற்றும் நிர்வாகத் திறன்.",
         "Saravali, Ch. 16, Sloka 3", "SeverityLevel.FAVORABLE"),

        (["Sun", "Moon", "Jupiter"], "RULE-SARAVALI-TRI-SUN-MOO-JUP",
         "Sun, Moon, and Jupiter Conjunction (Saravali Tri-Graha)", "சூரியன், சந்திரன் மற்றும் குரு சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 4: Highly pious, wealthy, respected preceptor, spotless reputation, blessed with devoted family and royal favor.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 4: உயர்ந்த தர்ம சிந்தனை, பெரும் செல்வம், களங்கமற்ற புகழ் மற்றும் தெய்வ அருள் நிறைந்த வாழ்க்கை.",
         "Saravali, Ch. 16, Sloka 4", "SeverityLevel.FAVORABLE"),

        (["Sun", "Moon", "Venus"], "RULE-SARAVALI-TRI-SUN-MOO-VEN",
         "Sun, Moon, and Venus Conjunction (Saravali Tri-Graha)", "சூரியன், சந்திரன் மற்றும் சுக்கிரன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 5: Skilled in arts, attractive, fond of luxuries and perfumes, wealthy, charismatic in social circles.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 5: கலைகளில் தேர்ச்சி, பேரழகு, சுகபோக வசதிகள், நவரத்தினங்கள் மற்றும் சமூக வசீகரம்.",
         "Saravali, Ch. 16, Sloka 5", "SeverityLevel.FAVORABLE"),

        (["Sun", "Moon", "Saturn"], "RULE-SARAVALI-TRI-SUN-MOO-SAT",
         "Sun, Moon, and Saturn Conjunction (Saravali Tri-Graha)", "சூரியன், சந்திரன் மற்றும் சனி சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 6: Self-reliant, hardworking, enduring hardships, skilled in minerals and mines, philosophical disposition.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 6: சுய உழைப்பு, சோதனைகளைத் தாங்கும் மன உறுதி, தத்துவ நாட்டம் மற்றும் கனிம-சுரங்கத் தொழில் வெற்றி.",
         "Saravali, Ch. 16, Sloka 6", "SeverityLevel.MIXED"),

        (["Sun", "Mars", "Mercury"], "RULE-SARAVALI-TRI-SUN-MAR-MER",
         "Sun, Mars, and Mercury Conjunction (Saravali Tri-Graha)", "சூரியன், செவ்வாய் மற்றும் புதன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 7: Great warrior, analytical tactician, courageous commander, skilled in technical arts and litigation.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 7: தீரமிக்க படைத்தலைவர், சாதுரியமான வியூகங்கள் அமைப்பவர், தொழில்நுட்பம் மற்றும் வழக்குகளில் வெற்றி.",
         "Saravali, Ch. 16, Sloka 7", "SeverityLevel.FAVORABLE"),

        (["Sun", "Mars", "Jupiter"], "RULE-SARAVALI-TRI-SUN-MAR-JUP",
         "Sun, Mars, and Jupiter Conjunction (Saravali Tri-Graha)", "சூரியன், செவ்வாய் மற்றும் குரு சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 8: Minister of state, commanding general, righteous leader, exceedingly wealthy, famous, and victorious.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 8: அரசாங்க மந்திரி, தளபதி, தர்ம நெறி தவறாத தலைவர், அளப்பரிய தனம் மற்றும் மாபெரும் புகழ்.",
         "Saravali, Ch. 16, Sloka 8", "SeverityLevel.FAVORABLE"),

        (["Sun", "Mars", "Venus"], "RULE-SARAVALI-TRI-SUN-MAR-VEN",
         "Sun, Mars, and Venus Conjunction (Saravali Tri-Graha)", "சூரியன், செவ்வாய் மற்றும் சுக்கிரன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 9: Highly passionate, handsome, athletic, dramatic flair, charismatic, but requires marital discretion.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 9: வசீகரத் தோற்றம், கலை-விளையாட்டுத் திறன், காம நாட்டம் மற்றும் சமூகத்தில் கவர்ச்சியான ஆளுமை.",
         "Saravali, Ch. 16, Sloka 9", "SeverityLevel.MIXED"),

        (["Sun", "Mars", "Saturn"], "RULE-SARAVALI-TRI-SUN-MAR-SAT",
         "Three Malefics Conjunction: Sun, Mars, and Saturn (Saravali Tri-Graha)", "மூன்று பாப கிரகங்கள் சேர்க்கை: சூரியன், செவ்வாய், சனி (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 10 warns: Extreme physical grit, iron endurance, fearless in combat, but prone to injuries and heavy challenges.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 10: இரும்பு போன்ற மன உறுதி, போரில் அஞ்சாமை, விபத்துகள் அல்லது காயங்கள் மற்றும் தீவிர வாழ்க்கைச் சவால்கள்.",
         "Saravali, Ch. 16, Sloka 10", "SeverityLevel.MIXED"),

        (["Sun", "Mercury", "Jupiter"], "RULE-SARAVALI-TRI-SUN-MER-JUP",
         "Sun, Mercury, and Jupiter Conjunction (Saravali Tri-Graha)", "சூரியன், புதன் மற்றும் குரு சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 11: Supreme wisdom, Vedic scholar, presidential counselor, endowed with wealth, eloquence, and lasting renown.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 11: வேத சாஸ்திர ஞானம், தலைமை ஆலோசகர், நாவன்மை, அளப்பரிய செல்வம் மற்றும் நீங்காத நற்புகழ்.",
         "Saravali, Ch. 16, Sloka 11", "SeverityLevel.FAVORABLE"),

        (["Sun", "Mercury", "Venus"], "RULE-SARAVALI-TRI-SUN-MER-VEN",
         "Sun, Mercury, and Venus Conjunction (Saravali Tri-Graha)", "சூரியன், புதன் மற்றும் சுக்கிரன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 12: Eloquent poet, dramatist, attractive, honored by sovereigns, possessing vehicles, gems, and aristocratic status.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 12: அரசவைக் கவிஞர், நாடக ஆசிரியர், நவரத்தினங்கள் மற்றும் வாகன யோகம் கொண்ட சுகபோக வாழ்வு.",
         "Saravali, Ch. 16, Sloka 12", "SeverityLevel.FAVORABLE"),

        (["Sun", "Mercury", "Saturn"], "RULE-SARAVALI-TRI-SUN-MER-SAT",
         "Sun, Mercury, and Saturn Conjunction (Saravali Tri-Graha)", "சூரியன், புதன் மற்றும் சனி சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 13: Technical researcher, scribe, accountant, disciplined student of complex arts, steady rise through labor.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 13: தொழில்நுட்ப ஆராய்ச்சியாளர், கணக்காளர், கடினமான கலைகளைக் கற்கும் ஆர்வம் மற்றும் உழைப்பால் உயர்வு.",
         "Saravali, Ch. 16, Sloka 13", "SeverityLevel.FAVORABLE"),

        (["Sun", "Jupiter", "Venus"], "RULE-SARAVALI-TRI-SUN-JUP-VEN",
         "Sun, Jupiter, and Venus Conjunction (Saravali Tri-Graha)", "சூரியன், குரு மற்றும் சுக்கிரன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 14: Teacher of high rank, esteemed by royalty, opulent lifestyle, virtuous mind, and master of sacred ceremonies.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 14: அரசகுரு அந்தஸ்து, மங்களகரமான வாழ்க்கை, நற்பண்புகள் மற்றும் சகல சாஸ்திரங்களிலும் மேன்மை.",
         "Saravali, Ch. 16, Sloka 14", "SeverityLevel.FAVORABLE"),

        (["Sun", "Jupiter", "Saturn"], "RULE-SARAVALI-TRI-SUN-JUP-SAT",
         "Sun, Jupiter, and Saturn Conjunction (Saravali Tri-Graha)", "சூரியன், குரு மற்றும் சனி சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 15: Revered community elder, founder of public institutions, dignified, wealthy, and authoritative.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 15: சமுதாயத் தலைவர், பொது அறப்பணிகளை நிறுவுபவர், கம்பீரமான அதிகாரம் மற்றும் நீடித்த செல்வம்.",
         "Saravali, Ch. 16, Sloka 15", "SeverityLevel.FAVORABLE"),

        (["Moon", "Mars", "Jupiter"], "RULE-SARAVALI-TRI-MOO-MAR-JUP",
         "Moon, Mars, and Jupiter Conjunction (Saravali Tri-Graha)", "சந்திரன், செவ்வாய் மற்றும் குரு சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 19: Master of warfare and diplomacy, exceptionally prosperous, high moral stature, and honored commander.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 19: ராஜதந்திரமும் போர்த்திறனும் கொண்டவர், அபரிமித தனம், உயர்ந்த நற்பண்பு மற்றும் அரசு மரியாதை.",
         "Saravali, Ch. 16, Sloka 19", "SeverityLevel.FAVORABLE"),

        (["Moon", "Mercury", "Jupiter"], "RULE-SARAVALI-TRI-MOO-MER-JUP",
         "Moon, Mercury, and Jupiter Conjunction (Saravali Tri-Graha)", "சந்திரன், புதன் மற்றும் குரு சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 23: Pure intellect, profound writer, virtuous, blessed with exemplary children, and admired for wisdom.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 23: களங்கமற்ற ஞானம், சிறந்த எழுத்தாளர், புண்ணியவான், அறிவுள்ள மக்கள் செல்வம் மற்றும் மக்கள் அபிமானம்.",
         "Saravali, Ch. 16, Sloka 23", "SeverityLevel.FAVORABLE"),

        (["Moon", "Jupiter", "Venus"], "RULE-SARAVALI-TRI-MOO-JUP-VEN",
         "Moon, Jupiter, and Venus Conjunction (Saravali Tri-Graha)", "சந்திரன், குரு மற்றும் சுக்கிரன் சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 25: Exceedingly wealthy, graceful, beloved by all, endowed with conveyances, gems, and spiritual peace.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 25: அளப்பரிய செல்வம், பேரழகு, சகல ஜன வசியம், சொகுசு வாகனங்கள் மற்றும் மன அமைதி.",
         "Saravali, Ch. 16, Sloka 25", "SeverityLevel.FAVORABLE"),

        (["Mercury", "Jupiter", "Venus"], "RULE-SARAVALI-TRI-MER-JUP-VEN",
         "Three Benefics Conjunction: Mercury, Jupiter, and Venus (Saravali Tri-Graha)", "மூன்று சுப கிரகங்கள் சேர்க்கை: புதன், குரு, சுக்கிரன் (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 34: Supreme Saravali Benefic Conjunction: Renowned author, unmatched wisdom, royal advisor, great wealth, and unblemished character.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 34: மகா சுப யோகம்; இணையற்ற அறிவு, தலைமை ஆலோசகர், அரச கௌரவம், களங்கமற்ற நற்பண்பு மற்றும் பெரும் பாக்கியம்.",
         "Saravali, Ch. 16, Sloka 34", "SeverityLevel.FAVORABLE"),

        (["Mars", "Jupiter", "Saturn"], "RULE-SARAVALI-TRI-MAR-JUP-SAT",
         "Mars, Jupiter, and Saturn Conjunction (Saravali Tri-Graha)", "செவ்வாய், குரு மற்றும் சனி சேர்க்கை (திரிகிரக யோகம்)",
         "Saravali Ch. 16, v. 30: Executive administrator, leader in engineering, judicial or municipal authority, dignified and wealthy.",
         "சாராவளி அத்தியாயம் 16, சுலோகம் 30: உயர்மட்ட நிர்வாகி, நீதித்துறை அல்லது நகர நிர்வாகத்தில் தலைமைப் பதவி மற்றும் உறுதியான தன லாபம்.",
         "Saravali, Ch. 16, Sloka 30", "SeverityLevel.FAVORABLE")
    ]

    for planets, r_id, name_en, name_ta, desc_en, desc_ta, sloka, sev in three_planet_data:
        rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{r_id}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="saravali_classics",
        subcategory="saravali_graha_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "planet_conjunction",
            "planets": {planets},
            "chart": "d1"
        }},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="Tri-Graha Yoga Principle: Three planets uniting in a single rasi produce specialized multi-faceted life trajectories codified in Saravali Ch. 16.",
        astrological_principle_ta="திரிகிரக யோக விதி: மூன்று கிரகங்கள் ஒரே ராசியில் இணைவது வாழ்க்கையில் சிறப்பு வாய்ந்த திருப்பங்களையும் பலாபலன்களையும் நல்கும்.",
        source_reference="{sloka}",
        limitations_en="Combustion and mutual planetary warfare (Graha Yuddha) must be evaluated.",
        limitations_ta="அஸ்தமனம் மற்றும் கிரக யுத்தம் இருப்பின் பலன்களின் அளவைக் கணிக்க வேண்டும்.",
        severity={sev},
    ),'''
        rules.append(rule_str)

    return rules
