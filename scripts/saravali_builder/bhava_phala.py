# scripts/saravali_builder/bhava_phala.py
"""Saravali Chapter 30: Bhava Phala Rules Builder.
Covers Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn across houses 1 to 12
plus Malefics in Dusthanas.
"""

def get_bhava_phala_rules():
    rules = []

    planets_data = {
        "Sun": {
            "name_ta": "சூரியன்",
            "sloka_base": 2,
            "houses": {
                1: {
                    "en_name": "Sun in 1st House (Lagna Bhava Phala)",
                    "ta_name": "லக்னத்தில் சூரியன் (1-ஆம் பாவக பலன்)",
                    "desc_en": "According to Saravali, if the Sun is in Lagna, the native will have sparse hair, be indolent, quick to anger, have a prominent personality, fierce eyes, and a tall, sturdy physique. If in Aries, Leo, or Sagittarius, courage and leadership are pronounced.",
                    "desc_ta": "சாராவளி படி, சூரியன் லக்னத்தில் அமர்ந்தால் ஜாதகர் கூரிய பார்வையும், கம்பீரமான உடலமைப்பும், முன்சீற்றமும், தலைமைப் பண்பும் கொண்டிருப்பார். மேஷம், சிம்மம், தனுசுவில் இருந்தால் அதிக தைரியமும் புகழும் கிட்டும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 2-4"
                },
                2: {
                    "en_name": "Sun in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் சூரியன் (தன பாவக பலன்)",
                    "desc_en": "Per Saravali, Sun in 2nd house deprives the native of modesty, causes facial or dental ailments, creates obstacles to ancestral wealth, but confers financial gains through royal or governmental patronage.",
                    "desc_ta": "2-ல் சூரியன் அமர்ந்தால் முக அல்லது கண் உபாதைகள், பூர்வீக சொத்துகளில் தடைகள் ஏற்படலாம்; ஆயினும் அரசு அல்லது அதிகார பதவிகள் மூலம் தன லாபம் உண்டாகும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 5"
                },
                3: {
                    "en_name": "Sun in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் சூரியன் (சகஜ பாவக பலன்)",
                    "desc_en": "Saravali states that Sun in the 3rd house makes the native exceptionally brave, wealthy, liberal, powerful, victorious over adversaries, and endowed with physical prowess, though friction with younger siblings is noted.",
                    "desc_ta": "3-ல் சூரியன் அமைவது ஜாதகருக்கு பேராற்றல், அஞ்சாநெஞ்சம், பரந்த உள்ளம், எதிரிகளை வெல்லும் பராக்கிரமம் மற்றும் நிறைந்த செல்வத்தை வழங்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 6"
                },
                4: {
                    "en_name": "Sun in 4th House (Sukha Bhava Phala)",
                    "ta_name": "4-ஆம் வீட்டில் சூரியன் (சுக பாவக பலன்)",
                    "desc_en": "Per Saravali, the native with Sun in 4th lacks domestic peace, experiences estrangement from ancestral lands or mother's guidance, has a troubled heart, and serves superiors, unless fortified in Leo.",
                    "desc_ta": "4-ல் சூரியன் அமர்ந்தால் சொந்த வீடு, பூமி, தாய் மற்றும் வாகன வழியில் மன அமைதிக் குறைவு ஏற்படும்; சிம்மத்தில் ஆட்சி பெற்றால் அன்றி தாய்வழி உறவில் மனக்கசப்பு வரலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 7"
                },
                5: {
                    "en_name": "Sun in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் சூரியன் (புத்திர பாவக பலன்)",
                    "desc_en": "According to Saravali, Sun in 5th renders the native sharp-minded, fond of woodlands and solitude, of short progeny, wandering disposition, and prone to digestive or cardiac heat.",
                    "desc_ta": "5-ல் சூரியன் அமைந்தால் கூரிய புத்தி, காடுகள்-இயற்கையில் விருப்பம், குறைந்த புத்திர பாக்கியம், அலைச்சல் மற்றும் பித்த சம்பந்தமான கோளாறுகள் உண்டாகலாம்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 8"
                },
                6: {
                    "en_name": "Sun in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் சூரியன் (சத்ரு பாவக பலன்)",
                    "desc_en": "Saravali proclaims that Sun in the 6th creates a triumphant warrior who destroys adversaries, possesses immense vitality, commands servants, and enjoys regal honor and vigorous health.",
                    "desc_ta": "6-ல் சூரியன் இருப்பது சத்ரு ஜெயம் எனப்படும் மாபெரும் யோகம்; எதிரிகளைப் பூண்டோடு அழிக்கும் ஆற்றல், அரசு மரியாதை, உடல் வலிமை மற்றும் செல்வாக்கு தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 9"
                },
                7: {
                    "en_name": "Sun in 7th House (Kalatra Bhava Phala)",
                    "ta_name": "7-ஆம் வீட்டில் சூரியன் (களத்திர பாவக பலன்)",
                    "desc_en": "Saravali states that Sun in the 7th causes marital discord, an arrogant or sickly partner, wanderlust, public disputes, and lack of domestic comfort.",
                    "desc_ta": "7-ல் சூரியன் நின்றால் வாழ்க்கைத் துணையுடன் கருத்து வேறுபாடுகள், மனைவியின் உடல்நிலையில் பாதிப்பு, வெளிநாட்டுப் பயணம் மற்றும் சமூகத்தில் விரோதம் ஏற்படலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 10"
                },
                8: {
                    "en_name": "Sun in 8th House (Ayur Bhava Phala)",
                    "ta_name": "8-ஆம் வீட்டில் சூரியன் (ஆயுள் பாவக பலன்)",
                    "desc_en": "Saravali notes that Sun in the 8th deprives the native of wealth and vitality, causes eye complaints, shortens familial happiness, and creates hazards from quadrupeds or government displeasure.",
                    "desc_ta": "8-ல் சூரியன் அமைவது கண் பார்வை பலவீனம், தன விரயம், அரசாங்கத்தால் தண்டனை அல்லது அபராதம் மற்றும் உடற்சோர்வை ஏற்படுத்தும் அமைப்பாகும்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 11"
                },
                9: {
                    "en_name": "Sun in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் சூரியன் (பாக்ய பாவக பலன்)",
                    "desc_en": "Per Saravali, Sun in 9th makes the person devoted to deities and preceptors, wealthy, father-oriented or self-reliant, charitable, endowed with conveyances, and honored in society.",
                    "desc_ta": "9-ல் சூரியன் வீற்றிருப்பது தெய்வ பக்தி, குரு மரியாதை, தரும சிந்தனை, வாகன யோகம் மற்றும் சமுதாயத்தில் உயர்ந்த கௌரவத்தை நல்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 12"
                },
                10: {
                    "en_name": "Sun in 10th House (Karma Bhava Phala - Digbala)",
                    "ta_name": "10-ஆம் வீட்டில் சூரியன் (கர்ம பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali extols Sun in 10th: The native attains supreme regal status, Digbala strength, vast wealth, scholarly renown, generous nature, heroic achievements, and ministerial command.",
                    "desc_ta": "10-ல் சூரியன் திக்பலம் பெற்று உச்ச பலன் தருகிறார். அரசுத் துறையில் உயர் பதவி, அரசியல் அதிகாரம், தாராள குணம், நீங்காத புகழ் மற்றும் சமூகத் தலைமை அமையும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 13"
                },
                11: {
                    "en_name": "Sun in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் சூரியன் (லாப பாவக பலன்)",
                    "desc_en": "Saravali confirms that Sun in 11th makes the native immensely affluent, possessor of vast land and conveyances, victorious over foes, served by attendants, and long-lived.",
                    "desc_ta": "11-ல் சூரியன் அமைந்தால் அளப்பரிய தன லாபம், பூமி-வாகன யோகம், எதிரிகளை அடக்கும் ஆற்றல், பணியாட்கள் சேர்க்கை மற்றும் நீண்ட ஆயுள் உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 14"
                },
                12: {
                    "en_name": "Sun in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் சூரியன் (வியய பாவக பலன்)",
                    "desc_en": "Per Saravali, Sun in 12th causes expenditure on government penalties or travels, weak left eye, conflict with paternal lineage, and fallen stature unless spiritually oriented.",
                    "desc_ta": "12-ல் சூரியன் அமர்ந்தால் தேவையற்ற விரயங்கள், இடது கண் உபாதை, தந்தையுடன் கருத்து வேறுபாடு மற்றும் வெளிநாட்டு அலைச்சல் ஏற்பட வாய்ப்புண்டு.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 15"
                }
            }
        },
        "Moon": {
            "name_ta": "சந்திரன்",
            "sloka_base": 16,
            "houses": {
                1: {
                    "en_name": "Moon in 1st House (Lagna Bhava Phala)",
                    "ta_name": "லக்னத்தில் சந்திரன் (1-ஆம் பாவக பலன்)",
                    "desc_en": "According to Saravali, Moon in Lagna makes the native handsome, wealthy, eloquent, fond of pleasures, peaceful, and popular. Waxing Moon grants vibrant health, while waning Moon causes physical debility.",
                    "desc_ta": "சாராவளி படி, லக்னத்தில் சந்திரன் நின்றால் அழகிய உருவம், நற்பண்புகள், வசீகரப் பேச்சு, மகிழ்ச்சியான வாழ்க்கை அமையும். வளர்பிறையாயின் சிறந்த ஆரோக்கியமும், தேய்பிறையாயின் உடற்பலவீனமும் ஏற்படும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 16-17"
                },
                2: {
                    "en_name": "Moon in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் சந்திரன் (தன பாவக பலன்)",
                    "desc_en": "Saravali states that Moon in 2nd renders the native wealthy, sweet-spoken, fond of delicacies, devoted to family, and possessed of charming facial features.",
                    "desc_ta": "2-ல் சந்திரன் வீற்றிருப்பது இனிய சொல், அழகிய முகம், சுவையான உணவு நாட்டம், குடும்ப அமைதி மற்றும் நிலையான செல்வத்தை அளிக்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 18"
                },
                3: {
                    "en_name": "Moon in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் சந்திரன் (சகஜ பாவக பலன்)",
                    "desc_en": "Per Saravali, Moon in 3rd makes the native valorous, happy with brothers/sisters, enthusiastic, fond of learning, scriptures, and artistic pursuits.",
                    "desc_ta": "3-ல் சந்திரன் அமைந்தால் தைரியம், உடன்பிறப்புகளின் ஆதரவு, கலை மற்றும் இலக்கியங்களில் ஈடுபாடு, உற்சாகமான மனநிலை உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 19"
                },
                4: {
                    "en_name": "Moon in 4th House (Sukha Bhava Phala - Digbala)",
                    "ta_name": "4-ஆம் வீட்டில் சந்திரன் (சுக பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali extols Moon in 4th (Digbala): Blessed with vehicles, lands, precious garments, domestic tranquility, maternal devotion, generous friends, and aristocratic comforts.",
                    "desc_ta": "4-ல் சந்திரன் திக்பலம் பெறுகிறார்; மாத்ரு சுகம், நிலம், சொகுசு வாகனங்கள், உயர்ந்த ஆடைகள், மன நிம்மதி மற்றும் உண்மையான நண்பர்களின் சேர்க்கை அருளும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 20"
                },
                5: {
                    "en_name": "Moon in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் சந்திரன் (புத்திர பாவக பலன்)",
                    "desc_en": "Saravali confirms that Moon in 5th confers virtuous and graceful children, profound intelligence, ministerial counsel, poetic gift, and devotion to spiritual mantras.",
                    "desc_ta": "5-ல் சந்திரன் அமர்வது நற்குணமுள்ள குழந்தைகள், கூரிய நுண்ணறிவு, கவிதை எழுதும் ஆற்றல், அரசு ஆலோசனை மற்றும் மந்திர சித்தியை வழங்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 21"
                },
                6: {
                    "en_name": "Moon in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் சந்திரன் (சத்ரு பாவக பலன்)",
                    "desc_en": "According to Saravali, Moon in 6th brings weak digestion, susceptibility to phlegm and water-borne ailments, hostility from maternal relations, and fluctuating vitality.",
                    "desc_ta": "6-ல் சந்திரன் அமர்வது மந்தமான ஜீரண சக்தி, சளி-கப உபாதைகள், தாயார் வழியில் மனக்கசப்பு மற்றும் மன சஞ்சலங்களை ஏற்படுத்தக்கூடும்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 22"
                },
                7: {
                    "en_name": "Moon in 7th House (Kalatra Bhava Phala)",
                    "ta_name": "7-ஆம் வீட்டில் சந்திரன் (களத்திர பாவக பலன்)",
                    "desc_en": "Per Saravali, Moon in 7th grants a beautiful, affectionate, and well-mannered spouse, successful business partnerships, fame, and diplomatic acumen.",
                    "desc_ta": "7-ல் சந்திரன் நின்றால் அழகான குணமுள்ள வாழ்க்கைத் துணை, வெற்றிகரமான கூட்டுத் தொழில், சமூகத்தில் வசீகரம் மற்றும் பிரபல்யம் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 23"
                },
                8: {
                    "en_name": "Moon in 8th House (Ayur Bhava Phala - Chandrashtama)",
                    "ta_name": "8-ஆம் வீட்டில் சந்திரன் (ஆயுள் பாவக பலன் - சந்திராஷ்டமம்)",
                    "desc_en": "Saravali warns that Moon in 8th causes intermittent ailments, mental anxiety, risk from aquatic places, and vulnerability in childhood unless protected by benefics.",
                    "desc_ta": "8-ல் சந்திரன் அமைவது மனக்குழப்பம், ஆரோக்கியக் குறைவு, நீர்நிலைகளில் கவனம் தேவைப்படும் நிலை மற்றும் பாலாரிஷ்ட அமைப்பைச் சுட்டுகிறது.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 24"
                },
                9: {
                    "en_name": "Moon in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் சந்திரன் (பாக்ய பாவக பலன்)",
                    "desc_en": "Saravali affirms that Moon in 9th makes the native highly pious, virtuous, wealthy, blessed with righteous children, respected by leaders, and successful in long voyages.",
                    "desc_ta": "9-ல் சந்திரன் வீற்றிருப்பது பூர்வ புண்ணிய பலன்; தர்ம சிந்தனை, நற்பண்புகள், கடல் கடந்த பிரயாணங்களில் வெற்றி மற்றும் சமூக மரியாதை தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 25"
                },
                10: {
                    "en_name": "Moon in 10th House (Karma Bhava Phala)",
                    "ta_name": "10-ஆம் வீட்டில் சந்திரன் (கர்ம பாவக பலன்)",
                    "desc_en": "Per Saravali, Moon in 10th brings career success in public-facing roles, administrative authority, charitable undertakings, religious pilgrimages, and popular adoration.",
                    "desc_ta": "10-ல் சந்திரன் அமைவது பொதுச்சேவை, மக்கள் தொடர்பு, நிர்வாகப் பொறுப்பு, புனித யாத்திரைகள் மற்றும் தொழில் மேன்மையை வழங்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 26"
                },
                11: {
                    "en_name": "Moon in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் சந்திரன் (லாப பாவக பலன்)",
                    "desc_en": "Saravali declares Moon in 11th extremely auspicious: The native acquires abundant riches, loyal friends, noble offspring, and continuous prosperity through trade or arts.",
                    "desc_ta": "11-ல் சந்திரன் அமர்வது அளப்பரிய லாபம், உண்மையான நண்பர்கள், கலை வழியிலான வருமானம் மற்றும் தொடர் சுப நிகழ்வுகளை அருளும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 27"
                },
                12: {
                    "en_name": "Moon in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் சந்திரன் (வியய பாவக பலன்)",
                    "desc_en": "Saravali states Moon in 12th causes secret sorrows, foreign residence, eye afflictions, expenditure on philanthropic or erratic deeds, and quiet seclusion.",
                    "desc_ta": "12-ல் சந்திரன் நின்றால் தனிமை விரும்புதல், வெளிநாட்டு வாசம், கண் உபாதைகள், சுப/அசுப விரயங்கள் மற்றும் அலைபாயும் மனநிலை ஏற்படும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 28"
                }
            }
        },
        "Mars": {
            "name_ta": "செவ்வாய்",
            "sloka_base": 29,
            "houses": {
                1: {
                    "en_name": "Mars in 1st House (Lagna Bhava Phala)",
                    "ta_name": "லக்னத்தில் செவ்வாய் (1-ஆம் பாவக பலன்)",
                    "desc_en": "According to Saravali, Mars in Lagna gives a scar on the head/face, courageous nature, rash actions, strong physical vitality, short temper, and martial mindset.",
                    "desc_ta": "சாராவளி படி, லக்னத்தில் செவ்வாய் நின்றால் முகத்தில் வடு, அதீத தைரியம், முன்கோபம், துணிச்சலான செயல்கள் மற்றும் போர்க்குணம் உண்டாகும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 29"
                },
                2: {
                    "en_name": "Mars in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் செவ்வாய் (தன பாவக பலன்)",
                    "desc_en": "Per Saravali, Mars in 2nd causes harsh speech, financial instability due to impulsiveness, eye complaints, and discord within the immediate family.",
                    "desc_ta": "2-ல் செவ்வாய் அமைந்தால் கடுமையான பேச்சு, அவசரப்பட்டு செலவு செய்தல், குடும்பத்தில் வாக்குவாதம் மற்றும் கண் உபாதைகள் ஏற்படும்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 30"
                },
                3: {
                    "en_name": "Mars in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் செவ்வாய் (சகஜ பாவக பலன்)",
                    "desc_en": "Saravali extols Mars in 3rd: Heroic valor, immense physical strength, leadership among peers, self-made wealth, though occasional tension with co-borns occurs.",
                    "desc_ta": "3-ல் செவ்வாய் அமர்வது மகா பராக்கிரம யோகம்; தன்னம்பிக்கை, தளராத உழைப்பு, சுயமுயற்சியால் செல்வம் ஈட்டுதல் மற்றும் எதிரிகளை வீழ்த்தும் வீரம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 31"
                },
                4: {
                    "en_name": "Mars in 4th House (Sukha Bhava Phala)",
                    "ta_name": "4-ஆம் வீட்டில் செவ்வாய் (சுக பாவக பலன்)",
                    "desc_en": "Saravali notes Mars in 4th denies maternal warmth, creates domestic strife, vehicular damages, loss of ancestral property, and emotional volatility.",
                    "desc_ta": "4-ல் செவ்வாய் நின்றால் தாய்வழி சுகக்குறைவு, பூமி-வாகன வழியில் தடைகள், வீட்டு அமைதியின்மை மற்றும் மன அமைதிக் குறைவு ஏற்படும்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 32"
                },
                5: {
                    "en_name": "Mars in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் செவ்வாய் (புத்திர பாவக பலன்)",
                    "desc_en": "Per Saravali, Mars in 5th causes difficulties in progeny, restless intellect, speculative losses, digestive heat, and impetuous decisions.",
                    "desc_ta": "5-ல் செவ்வாய் அமைந்தால் புத்திர பாக்கியத்தில் காலதாமதம், அவசர முடிவுகள், சூதாட்டம்/ஊக வணிகத்தில் நஷ்டம் மற்றும் வயிற்றுக் கோளாறுகள் வரலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 33"
                },
                6: {
                    "en_name": "Mars in 6th House (Satru Bhava Phala - Shatru Hanta)",
                    "ta_name": "6-ஆம் வீட்டில் செவ்வாய் (சத்ரு பாவக பலன் - சத்ரு ஹந்தா)",
                    "desc_en": "Saravali praises Mars in 6th: Shatru-Hanta Yoga, commanding respect, annihilating debts and enemies, vigorous digestive power, and governmental authority.",
                    "desc_ta": "6-ல் செவ்வாய் இருப்பது எதிரிகளை வேரறுக்கும் சத்ரு ஹந்தா யோகம்; கடன் நீங்குதல், வழக்கு வெற்றி, அபார உடல் வலிமை மற்றும் உயர் அதிகாரம் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 34"
                },
                7: {
                    "en_name": "Mars in 7th House (Kalatra Bhava Phala - Kuja Dosha)",
                    "ta_name": "7-ஆம் வீட்டில் செவ்வாய் (களத்திர பாவக பலன் - செவ்வாய் தோஷம்)",
                    "desc_en": "Saravali states Mars in 7th causes marital frictions, separation, health vulnerabilities to spouse, wanderlust, and heated partnerships (classical Kuja Dosha).",
                    "desc_ta": "7-ல் செவ்வாய் களத்திர தோஷத்தை உண்டாக்கும்; மனைவியின் ஆரோக்கியத்தில் பாதிப்பு, தம்பதியிடையே கருத்து வேறுபாடு மற்றும் பிரிவு ஏற்பட வாய்ப்புண்டு.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 35"
                },
                8: {
                    "en_name": "Mars in 8th House (Ayur Bhava Phala)",
                    "ta_name": "8-ஆம் வீட்டில் செவ்வாய் (ஆயுள் பாவக பலன்)",
                    "desc_en": "Saravali indicates Mars in 8th brings susceptibility to accidents, surgical procedures, urinary or blood ailments, and friction over inheritances.",
                    "desc_ta": "8-ல் செவ்வாய் அமைந்தால் விபத்துகள், அறுவை சிகிச்சைகள், ரத்த அல்லது சிறுநீரக பாதிப்புகள் மற்றும் பூர்வீக சொத்துச் சிக்கல்கள் நேரலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 36"
                },
                9: {
                    "en_name": "Mars in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் செவ்வாய் (பாக்ய பாவக பலன்)",
                    "desc_en": "Per Saravali, Mars in 9th causes strained relations with father or preceptors, independent fortune earned through military/engineering fields, and legal friction.",
                    "desc_ta": "9-ல் செவ்வாய் அமைந்தால் தந்தையுடன் கருத்து வேறுபாடு, சுய உழைப்பால் சொத்து சேர்க்கை, இயந்திரம்-தொழில்நுட்ப வழியில் அதிர்ஷ்டம் உண்டாகும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 37"
                },
                10: {
                    "en_name": "Mars in 10th House (Karma Bhava Phala - Digbala)",
                    "ta_name": "10-ஆம் வீட்டில் செவ்வாய் (கர்ம பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali declares Mars in 10th supreme: Attains Digbala, Kuladeepa Yoga (family illuminator), executive leadership, success in administration, land, and industry.",
                    "desc_ta": "10-ல் செவ்வாய் திக்பலம் பெற்று குலதீப யோகம் அருள்கிறார்; நிர்வாகத் தலைமை, ரியல் எஸ்டேட்-தொழிற்சாலை வெற்றி மற்றும் அரசாங்க கௌரவம் உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 38"
                },
                11: {
                    "en_name": "Mars in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் செவ்வாய் (லாப பாவக பலன்)",
                    "desc_en": "Saravali praises Mars in 11th: Continuous accumulation of wealth, ownership of vast properties, overcoming obstacles effortlessly, and high societal rank.",
                    "desc_ta": "11-ல் செவ்வாய் நின்றால் மிகப்பெரிய தன லாபம், நிலபுலன்கள் சேர்க்கை, எதிர்ப்புகளை எளிதில் முறியடிக்கும் பேராற்றல் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 39"
                },
                12: {
                    "en_name": "Mars in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் செவ்வாய் (வியய பாவக பலன்)",
                    "desc_en": "Saravali warns Mars in 12th brings heavy losses through litigation, impulsiveness, injury to left eye, bed comforts disturbance, and conflict with authority.",
                    "desc_ta": "12-ல் செவ்வாய் நின்றால் வழக்குகள் வழியே பொருள் விரயம், கண் உபாதை, சயன சுகக் குறைவு மற்றும் கோபத்தால் இழப்புகள் உண்டாகலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 40"
                }
            }
        },
        "Mercury": {
            "name_ta": "புதன்",
            "sloka_base": 41,
            "houses": {
                1: {
                    "en_name": "Mercury in 1st House (Lagna Bhava Phala - Digbala)",
                    "ta_name": "லக்னத்தில் புதன் (1-ஆம் பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali praises Mercury in Lagna (Digbala): Scholar, eloquent speaker, mathematician, youthful appearance, humorous, virtuous, and respected by the learned.",
                    "desc_ta": "லக்னத்தில் புதன் திக்பலம் பெற்று வித்வான் யோகம் அருள்கிறார்; இளமையான தோற்றம், சாதுரியப் பேச்சு, கணிதம் மற்றும் கல்வியில் நிபுணத்துவம் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 41"
                },
                2: {
                    "en_name": "Mercury in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் புதன் (தன பாவக பலன்)",
                    "desc_en": "According to Saravali, Mercury in 2nd grants sweet and witty speech, wealth acquired through intellectual skill, poetic ability, and delicious feasts.",
                    "desc_ta": "2-ல் புதன் அமைந்தால் சாதுரியமான பேச்சு, அறிவுத்திறனால் தன வரவு, கவிதை எழுதும் ஆற்றல் மற்றும் குடும்பத்தில் மகிழ்ச்சி நிறையும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 42"
                },
                3: {
                    "en_name": "Mercury in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் புதன் (சகஜ பாவக பலன்)",
                    "desc_en": "Per Saravali, Mercury in 3rd makes the native industrious, fond of writing and communications, blessed with affectionate siblings, and skilled in trading.",
                    "desc_ta": "3-ல் புதன் நின்றால் விடாமுயற்சி, எழுத்தாற்றல், உடன்பிறப்புகளுடன் நற்புறவு, வணிகத் திறன் மற்றும் புதிய வித்தைகளைக் கற்கும் ஆர்வம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 43"
                },
                4: {
                    "en_name": "Mercury in 4th House (Sukha Bhava Phala)",
                    "ta_name": "4-ஆம் வீட்டில் புதன் (சுக பாவக பலன்)",
                    "desc_en": "Saravali confirms Mercury in 4th brings excellent education, maternal happiness, comfortable houses, friends, conveyances, and intellectual acclaim.",
                    "desc_ta": "4-ல் புதன் அமைவது உயர்கல்வி யோகம், தாய்வழி ஆதரவு, அழகான வீடு, சொகுசு வாகனங்கள் மற்றும் சமூகத்தில் நற்பெயர் அருளும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 44"
                },
                5: {
                    "en_name": "Mercury in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் புதன் (புத்திர பாவக பலன்)",
                    "desc_en": "Saravali states Mercury in 5th grants brilliant intelligence, mastery in astrology and mantra shastras, worthy children, and ministerial advisory status.",
                    "desc_ta": "5-ல் புதன் கூரிய நுண்ணறிவு, ஜோதிட-மந்திர சாஸ்திர ஞானம், சிறந்த புத்திர பாக்கியம் மற்றும் அரசாங்க ஆலோசனைப் பொறுப்பைத் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 45"
                },
                6: {
                    "en_name": "Mercury in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் புதன் (சத்ரு பாவக பலன்)",
                    "desc_en": "Per Saravali, Mercury in 6th makes the native contentious, prone to nerve strain, but victorious in debates and intellectual contests.",
                    "desc_ta": "6-ல் புதன் அமர்ந்தால் வாத-விவாதங்களில் வெற்றி, எதிர்ப்புகளை புத்தியால் முறியடித்தல்; நரம்பு சம்பந்தமான பாதிப்புகள் வரலாம்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 46"
                },
                7: {
                    "en_name": "Mercury in 7th House (Kalatra Bhava Phala)",
                    "ta_name": "7-ஆம் வீட்டில் புதன் (களத்திர பாவக பலன்)",
                    "desc_en": "Saravali states Mercury in 7th brings an intelligent, articulate, and youthful spouse, successful partnerships, and widespread public goodwill.",
                    "desc_ta": "7-ல் புதன் நின்றால் புத்திசாலியான இளமையான வாழ்க்கைத் துணை, வெற்றிகரமான வணிகக் கூட்டு மற்றும் சமூகத்தில் நற்பெயர் உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 47"
                },
                8: {
                    "en_name": "Mercury in 8th House (Ayur Bhava Phala)",
                    "ta_name": "8-ஆம் வீட்டில் புதன் (ஆயுள் பாவக பலன்)",
                    "desc_en": "Saravali extols Mercury in 8th: Conferring long life, scholarly renown, inheritance, royal favor, and steadfast intellect despite life's twists.",
                    "desc_ta": "8-ல் புதன் அமைவது நீண்ட ஆயுள், பரம்பரைச் சொத்து, அரசு உதவி, சாஸ்திர ஞானம் மற்றும் புகழைத் தரும் விசேஷ அமைப்பாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 48"
                },
                9: {
                    "en_name": "Mercury in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் புதன் (பாக்ய பாவக பலன்)",
                    "desc_en": "Per Saravali, Mercury in 9th makes the native virtuous, highly educated, charitable, devoted to religion, wealthy, and endowed with fine progeny.",
                    "desc_ta": "9-ல் புதன் அமைவது தர்ம கர்மாதிபதி யோகத்திற்கு நிகரானது; ஆன்மீக நாட்டம், உயர்கல்வி, அறச்செயல்கள் மற்றும் பெரும் செல்வம் அருளும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 49"
                },
                10: {
                    "en_name": "Mercury in 10th House (Karma Bhava Phala)",
                    "ta_name": "10-ஆம் வீட்டில் புதன் (கர்ம பாவக பலன்)",
                    "desc_en": "Saravali proclaims Mercury in 10th grants fame as an author, accountant, diplomat, or statesman; prosperous, righteous, and highly honored.",
                    "desc_ta": "10-ல் புதன் இருப்பது சிறந்த உத்தியோகம், வணிக வெற்றி, கணக்கியல்-எழுத்துத்துறையில் சாதனை மற்றும் சமுதாய அந்தஸ்தை நல்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 50"
                },
                11: {
                    "en_name": "Mercury in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் புதன் (லாப பாவக பலன்)",
                    "desc_en": "Saravali praises Mercury in 11th: Multi-stream income, prosperous commerce, truthful nature, learned companions, and abundant gains.",
                    "desc_ta": "11-ல் புதன் அமைந்தால் பல வழிகளில் பண வரவு, நேர்மையான குணம், சிறந்த நண்பர்கள் மற்றும் வணிகத் துறையில் அபரிமித லாபம் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 51"
                },
                12: {
                    "en_name": "Mercury in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் புதன் (வியய பாவக பலன்)",
                    "desc_en": "Saravali notes Mercury in 12th leads to expenses on religious or educational charities, foreign travels, but occasionally wandering intellect.",
                    "desc_ta": "12-ல் புதன் நின்றால் தர்ம காரியங்கள் மற்றும் கல்விக்காகச் செலவிடுதல், வெளிநாட்டுப் பிரயாணங்கள் மற்றும் ஆன்மீகச் சிந்தனை தரும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 52"
                }
            }
        },
        "Jupiter": {
            "name_ta": "குரு",
            "sloka_base": 53,
            "houses": {
                1: {
                    "en_name": "Jupiter in 1st House (Lagna Bhava Phala - Digbala)",
                    "ta_name": "லக்னத்தில் குரு (1-ஆம் பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali hails Jupiter in Lagna (Digbala): Possessor of radiant personality, profound wisdom, longevity, high morality, royal favor, and spiritual distinction.",
                    "desc_ta": "லக்னத்தில் குரு திக்பலம் பெற்று பிரம்மாண்ட யோகம் அளிக்கிறார்; ஞானம், நீண்ட ஆயுள், களங்கமற்ற புகழ், தெய்வ அருள் மற்றும் அரச மரியாதை தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 53-54"
                },
                2: {
                    "en_name": "Jupiter in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் குரு (தன பாவக பலன்)",
                    "desc_en": "According to Saravali, Jupiter in 2nd confers abundant wealth, eloquent and truthful speech, magnetic face, family honor, and financial security.",
                    "desc_ta": "2-ல் குரு வீற்றிருப்பது சிறந்த தன யோகம்; சத்திய வாக்கு, குடும்ப மேன்மை, முக வசீகரம் மற்றும் நிரந்தரச் செல்வத்தை அளிக்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 55"
                },
                3: {
                    "en_name": "Jupiter in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் குரு (சகஜ பாவக பலன்)",
                    "desc_en": "Per Saravali, Jupiter in 3rd makes the native pious, devoted to brothers, fond of travels, philosophical writer, though sometimes cautious in enterprise.",
                    "desc_ta": "3-ல் குரு அமைந்தால் நற்குணமுள்ள சகோதரர்கள், தத்துவ ஞானம், எழுத்துப்பணி மற்றும் தர்ம சிந்தனை உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 56"
                },
                4: {
                    "en_name": "Jupiter in 4th House (Sukha Bhava Phala)",
                    "ta_name": "4-ஆம் வீட்டில் குரு (சுக பாவக பலன்)",
                    "desc_en": "Saravali affirms Jupiter in 4th confers palatial homes, conveyances, domestic serenity, high academic credentials, maternal blessing, and happiness.",
                    "desc_ta": "4-ல் குரு இருப்பது மாத்ரு பாக்கியம், அழகான மாளிகை, வாகன வசதிகள், உயர் கல்வி மற்றும் குடும்பத்தில் நிம்மதியைத் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 57"
                },
                5: {
                    "en_name": "Jupiter in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் குரு (புத்திர பாவக பலன்)",
                    "desc_en": "Saravali declares Jupiter in 5th grants brilliant intellect, noble offspring, mantra-siddhi, advisory status to rulers, and profound philosophical insights.",
                    "desc_ta": "5-ல் குரு அமைவது பூர்வ புண்ணிய விசேஷம்; அறிவார்ந்த குழந்தைகள், தெய்வ அருள், மந்திரி பதவி மற்றும் ஆன்மீக ஞானத்தை அருளும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 58"
                },
                6: {
                    "en_name": "Jupiter in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் குரு (சத்ரு பாவக பலன்)",
                    "desc_en": "Per Saravali, Jupiter in 6th subdues adversaries through diplomacy, grants medical skill or service-oriented success, though liver or fat-related issues can arise.",
                    "desc_ta": "6-ல் குரு நின்றால் சாத்வீக முறையில் எதிரிகளை வெல்லுதல், தொண்டு மனப்பான்மை மற்றும் ஆரோக்கியத்தில் சீரான பராமரிப்பு தேவைப்படும் நிலை ஏற்படும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 59"
                },
                7: {
                    "en_name": "Jupiter in 7th House (Kalatra Bhava Phala)",
                    "ta_name": "7-ஆம் வீட்டில் குரு (களத்திர பாவக பலன்)",
                    "desc_en": "Saravali praises Jupiter in 7th: Grants a noble, virtuous, educated spouse, excellent character, public respect, and prosperity after marriage.",
                    "desc_ta": "7-ல் குரு அமர்வது சிறந்த களத்திர யோகம்; குணவதியான மனைவி, திருமணத்திற்குப் பின் பெரும் பாக்கியங்கள் மற்றும் சமுதாய மதிப்பு நல்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 60"
                },
                8: {
                    "en_name": "Jupiter in 8th House (Ayur Bhava Phala)",
                    "ta_name": "8-ஆம் வீட்டில் குரு (ஆயுள் பாவக பலன்)",
                    "desc_en": "Saravali notes Jupiter in 8th confers long life, peaceful end, interest in occult and esoteric wisdom, though mundane wealth faces occasional blocks.",
                    "desc_ta": "8-ல் குரு இருப்பது நீண்ட ஆயுள், ஆன்மீக-மறைபொருள் ஆராய்ச்சி, மரண பயமின்மை மற்றும் சாத்வீக வாழ்க்கையை அமைக்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 61"
                },
                9: {
                    "en_name": "Jupiter in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் குரு (பாக்ய பாவக பலன்)",
                    "desc_en": "Saravali extols Jupiter in 9th (Karaka in Bhava): Supreme fortune, devotion to preceptors, builder of temples, vast wealth, and righteous legacy.",
                    "desc_ta": "9-ல் குரு அமைவது முழுமையான பாக்ய யோகம்; தர்ம ஸ்தாபனம், ஆலயம் அமைத்தல், குருபக்தி, அளவற்ற செல்வம் மற்றும் உயர்ந்த சமூக கௌரவம் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 62"
                },
                10: {
                    "en_name": "Jupiter in 10th House (Karma Bhava Phala)",
                    "ta_name": "10-ஆம் வீட்டில் குரு (கர்ம பாவக பலன்)",
                    "desc_en": "Saravali proclaims Jupiter in 10th brings eminent professional status, high executive office, spotless reputation, patron of scholars, and righteous deeds.",
                    "desc_ta": "10-ல் குரு வீற்றிருப்பது களங்கமற்ற தொழில் புகழ், அரசு அல்லது நீதித்துறையில் உயர் பதவி மற்றும் சமூகத்தில் பெருமதிப்பைத் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 63"
                },
                11: {
                    "en_name": "Jupiter in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் குரு (லாப பாவக பலன்)",
                    "desc_en": "Saravali declares Jupiter in 11th: Enormous wealth, fulfilment of desires, noble friends, virtuous progeny, and steady growth in all endeavors.",
                    "desc_ta": "11-ல் குரு அமர்வது மகா தன லாபம்; ஆசைகள் அனைத்தும் நிறைவேறுதல், சிறந்த நண்பர்கள், புத்திர மேன்மை மற்றும் தொடர் முன்னேற்றம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 64"
                },
                12: {
                    "en_name": "Jupiter in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் குரு (வியய பாவக பலன்)",
                    "desc_en": "Per Saravali, Jupiter in 12th directs wealth towards sacred charities, pilgrimages, ascetic practices, granting spiritual liberation (Moksha orientation).",
                    "desc_ta": "12-ல் குரு நின்றால் மோட்ச மார்க்கம், தர்ம காரியங்களுக்கு செலவிடுதல், புனித யாத்திரைகள் மற்றும் ஆன்மீக அமைதி உண்டாகும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 65"
                }
            }
        },
        "Venus": {
            "name_ta": "சுக்கிரன்",
            "sloka_base": 66,
            "houses": {
                1: {
                    "en_name": "Venus in 1st House (Lagna Bhava Phala)",
                    "ta_name": "லக்னத்தில் சுக்கிரன் (1-ஆம் பாவக பலன்)",
                    "desc_en": "According to Saravali, Venus in Lagna makes the native exceptionally handsome, charming, romantic, long-lived, wealthy, skilled in arts, and adored by all.",
                    "desc_ta": "சாராவளி படி, லக்னத்தில் சுக்கிரன் அமைந்தால் பேரழகு, வசீகரம், கலைகளில் தேர்ச்சி, நீண்ட ஆயுள், நற்புகழ் மற்றும் சகல சுகங்களும் கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 66"
                },
                2: {
                    "en_name": "Venus in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் சுக்கிரன் (தன பாவக பலன்)",
                    "desc_en": "Saravali affirms Venus in 2nd confers vast wealth, poetic and eloquent speech, jewels, sumptuous feasts, and harmonious family life.",
                    "desc_ta": "2-ல் சுக்கிரன் இருப்பது தன தான்ய யோகம்; நவரத்தினங்கள் சேர்க்கை, இனிமையான வாக்கு, கவிதை நயம் மற்றும் குடும்ப அமைதி தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 67"
                },
                3: {
                    "en_name": "Venus in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் சுக்கிரன் (சகஜ பாவக பலன்)",
                    "desc_en": "Per Saravali, Venus in 3rd makes the native artistic, fond of luxuries and perfumes, affectionate towards siblings, but sometimes indolent.",
                    "desc_ta": "3-ல் சுக்கிரன் நின்றால் கலை ஆர்வம், வாசனை திரவியங்கள் மற்றும் ஆடை ஆபரண நாட்டம், உடன்பிறப்புகளின் அன்பு உண்டாகும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 68"
                },
                4: {
                    "en_name": "Venus in 4th House (Sukha Bhava Phala - Digbala)",
                    "ta_name": "4-ஆம் வீட்டில் சுக்கிரன் (சுக பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali extols Venus in 4th (Digbala): Luxurious vehicles, magnificent residences, mother's longevity, abundant comforts, perfumes, and domestic bliss.",
                    "desc_ta": "4-ல் சுக்கிரன் திக்பலம் பெற்று வாகன யோகம், ஆடம்பர மாளிகை, தாயாரின் ஆசி, மன அமைதி மற்றும் சகல சௌபாக்கியங்களையும் அருள்கிறார்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 69"
                },
                5: {
                    "en_name": "Venus in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் சுக்கிரன் (புத்திர பாவக பலன்)",
                    "desc_en": "Saravali states Venus in 5th brings poetic talents, wealth, handsome offspring (predominantly daughters), wisdom, and ministerial advisory positions.",
                    "desc_ta": "5-ல் சுக்கிரன் அமைவது கலை ஞானம், அழகிய குழந்தைகள், கவிதை எழுதும் ஆற்றல், அரசு ஆலோசனை மற்றும் மிகுந்த செல்வம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 70"
                },
                6: {
                    "en_name": "Venus in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் சுக்கிரன் (சத்ரு பாவக பலன்)",
                    "desc_en": "Per Saravali, Venus in 6th causes adversity through women, urinary or kidney complaints, financial depletion, and vulnerability to rivals.",
                    "desc_ta": "6-ல் சுக்கிரன் அமைவது பெண்களால் விரோதம், சிறுநீரக அல்லது சர்க்கரை உபாதைகள், வீண் விரயங்கள் மற்றும் எதிர்ப்புகளை உருவாக்கலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 71"
                },
                7: {
                    "en_name": "Venus in 7th House (Kalatra Bhava Phala)",
                    "ta_name": "7-ஆம் வீட்டில் சுக்கிரன் (களத்திர பாவக பலன்)",
                    "desc_en": "Saravali notes Venus in 7th brings a very attractive partner, passion, but warns of marital friction or indulgence unless dignified.",
                    "desc_ta": "7-ல் சுக்கிரன் அழகிய மனைவியைத் தரும்; ஆயினும் காம நாட்டம், தாம்பத்தியத்தில் சலனங்கள் அல்லது மனைவியின் உடல்நிலையில் கவனம் தேவைப்படும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 72"
                },
                8: {
                    "en_name": "Venus in 8th House (Ayur Bhava Phala)",
                    "ta_name": "8-ஆம் வீட்டில் சுக்கிரன் (ஆயுள் பாவக பலன்)",
                    "desc_en": "Saravali extols Venus in 8th: Conferring long life, abundant wealth, princely status, and a peaceful, painless departure.",
                    "desc_ta": "8-ல் சுக்கிரன் இருப்பது அஷ்டம சுக்கிர யோகம் எனப்படும்; நீண்ட ஆயுள், திடீர் தன வரவு, சுகபோகம் மற்றும் அமைதியான வாழ்வு தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 73"
                },
                9: {
                    "en_name": "Venus in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் சுக்கிரன் (பாக்ய பாவக பலன்)",
                    "desc_en": "Per Saravali, Venus in 9th brings continuous good fortune, religious pilgrimages, generous charities, devotion to preceptors, and blissful marital life.",
                    "desc_ta": "9-ல் சுக்கிரன் அமைவது பூரண பாக்கியம்; தர்ம சிந்தனை, சொகுசுப் பிரயாணங்கள், குருபக்தி மற்றும் திருமணத்திற்குப் பின் பெரும் செல்வம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 74"
                },
                10: {
                    "en_name": "Venus in 10th House (Karma Bhava Phala)",
                    "ta_name": "10-ஆம் வீட்டில் சுக்கிரன் (கர்ம பாவக பலன்)",
                    "desc_en": "Saravali states Venus in 10th brings career success in arts, luxury goods, diplomacy, high public standing, and royal favor.",
                    "desc_ta": "10-ல் சுக்கிரன் அமைந்தால் கலை, ஆடை-ஆபரணம், திரைப்படம் அல்லது அழகு சாதனத் தொழில்களில் வெற்றி மற்றும் சமூக மரியாதை கிட்டும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 75"
                },
                11: {
                    "en_name": "Venus in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் சுக்கிரன் (லாப பாவக பலன்)",
                    "desc_en": "Saravali praises Venus in 11th: Immense wealth, acquisition of precious gems, luxurious conveyances, and steady profits through creative trades.",
                    "desc_ta": "11-ல் சுக்கிரன் இருப்பது அளப்பரிய தன லாபம், ஆபரணச் சேர்க்கை, வாகன சுகம் மற்றும் பெண்களின் ஆதரவால் முன்னேற்றம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 76"
                },
                12: {
                    "en_name": "Venus in 12th House (Vyaya Bhava Phala - Sayana Sukha)",
                    "ta_name": "12-ஆம் வீட்டில் சுக்கிரன் (வியய பாவக பலன் - சயன சுகம்)",
                    "desc_en": "Saravali proclaims Venus in 12th gives profound bedroom comforts (Sayana Sukha), vast wealth, lavish living, and foreign prosperity.",
                    "desc_ta": "12-ல் சுக்கிரன் அமர்வது சுகபோக யோகம்; சயன சுகம், ஆடம்பரச் செலவுகள், வெளிநாட்டு வாழ்க்கை மற்றும் பணப்புழக்கம் தடையின்றி இருக்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 77"
                }
            }
        },
        "Saturn": {
            "name_ta": "சனி",
            "sloka_base": 78,
            "houses": {
                1: {
                    "en_name": "Saturn in 1st House (Lagna Bhava Phala)",
                    "ta_name": "லக்னத்தில் சனி (1-ஆம் பாவக பலன்)",
                    "desc_en": "Per Saravali, Saturn in Lagna makes the native sorrowful, sluggish, sickly in childhood, emaciated, and wanderlust, unless in Libra, Capricorn, or Aquarius (Sasa Yoga).",
                    "desc_ta": "சாராவளி படி, லக்னத்தில் சனி அமர்ந்தால் இளமையில் ஆரோக்கியக் குறைவு, மந்த குணம், சோம்பல்; ஆனால் துலாம், மகரம், கும்பத்தில் இருந்தால் சச யோகம் மூலம் ஆட்சி அதிகாரம் கிட்டும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 78"
                },
                2: {
                    "en_name": "Saturn in 2nd House (Dhana Bhava Phala)",
                    "ta_name": "2-ஆம் வீட்டில் சனி (தன பாவக பலன்)",
                    "desc_en": "Saravali states Saturn in 2nd brings harsh speech, poverty or delayed wealth, discord with family members, and living away from birthplace.",
                    "desc_ta": "2-ல் சனி நின்றால் கடுமையான வாக்கு, தன வரவில் தாமதம், குடும்பப் பிரிவு மற்றும் பிறர் தேசத்தில் வாழும் நிலை உண்டாகலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 79"
                },
                3: {
                    "en_name": "Saturn in 3rd House (Sahaja Bhava Phala)",
                    "ta_name": "3-ஆம் வீட்டில் சனி (சகஜ பாவக பலன்)",
                    "desc_en": "Saravali praises Saturn in 3rd: Heroic disposition, destruction of rivals, immense perseverance, acquisition of wealth, though strain with siblings.",
                    "desc_ta": "3-ல் சனி வீற்றிருப்பது மாபெரும் தைரிய யோகம்; அஞ்சாநெஞ்சம், கடின உழைப்பால் வெற்றி, எதிரிகளை வீழ்த்துதல் மற்றும் நிலையான செல்வம் தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 80"
                },
                4: {
                    "en_name": "Saturn in 4th House (Sukha Bhava Phala)",
                    "ta_name": "4-ஆம் வீட்டில் சனி (சுக பாவக பலன்)",
                    "desc_en": "Per Saravali, Saturn in 4th deprives the native of maternal affection, creates heart distress, domestic worries, vehicular troubles, and gloomy surroundings.",
                    "desc_ta": "4-ல் சனி நின்றால் தாய்வழி சுகக் குறைவு, பூமி-வீடு வகையில் சிக்கல்கள், வாகனத் தொல்லை மற்றும் மன அமைதியின்மை ஏற்படலாம்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 81"
                },
                5: {
                    "en_name": "Saturn in 5th House (Putra Bhava Phala)",
                    "ta_name": "5-ஆம் வீட்டில் சனி (புத்திர பாவக பலன்)",
                    "desc_en": "Saravali notes Saturn in 5th causes delay or loss of children, melancholic mind, wandering disposition, but aptitude in ancient or technical lore.",
                    "desc_ta": "5-ல் சனி அமைந்தால் புத்திர பாக்கியத்தில் தடை-தாமதம், மன அழுத்தம்; பழமையான சாஸ்திரங்கள் மற்றும் தொழில்நுட்பக் கல்வியில் ஆர்வம் தரும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 82"
                },
                6: {
                    "en_name": "Saturn in 6th House (Satru Bhava Phala)",
                    "ta_name": "6-ஆம் வீட்டில் சனி (சத்ரு பாவக பலன்)",
                    "desc_en": "Saravali extols Saturn in 6th: Complete destruction of enemies, immense courage, voracious appetite, freedom from debts, and regal authority.",
                    "desc_ta": "6-ல் சனி அமர்வது எதிரிகளை அடியோடு அழிக்கும் மகா யோகம்; வழக்கு வெற்றி, கடன் நிவர்த்தி, பராக்கிரமம் மற்றும் அரசு ஆதரவு தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 83"
                },
                7: {
                    "en_name": "Saturn in 7th House (Kalatra Bhava Phala - Digbala)",
                    "ta_name": "7-ஆம் வீட்டில் சனி (களத்திர பாவக பலன் - திக்பலம்)",
                    "desc_en": "Saravali states Saturn in 7th (Digbala) brings a mature, sober spouse, delay in marriage, travel abroad, but marital friction if afflicted.",
                    "desc_ta": "7-ல் சனி திக்பலம் பெறுகிறார்; முதிர்ந்த பக்குவமான வாழ்க்கைத் துணை, தாமத திருமணம், வெளிநாட்டுப் பயணம் மற்றும் தொழில் கூட்டாண்மை தரும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 84"
                },
                8: {
                    "en_name": "Saturn in 8th House (Ayur Bhava Phala - Dirghayu)",
                    "ta_name": "8-ஆம் வீட்டில் சனி (ஆயுள் பாவக பலன் - தீர்க்காயுள்)",
                    "desc_en": "Saravali affirms Saturn in 8th (Ayushkaraka in Ayusthana): Grants exceptional longevity, but chronic health vulnerabilities, colic, or hard labor.",
                    "desc_ta": "8-ல் சனி அமைவது தீர்க்காயுள் யோகம்; ஆயுள் காரகன் ஆயுள் ஸ்தானத்தில் அமர்வது நீண்ட வாழ்வை நல்கும், எனினும் வாத உபாதைகள் ஏற்படலாம்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 85"
                },
                9: {
                    "en_name": "Saturn in 9th House (Bhagya Bhava Phala)",
                    "ta_name": "9-ஆம் வீட்டில் சனி (பாக்ய பாவக பலன்)",
                    "desc_en": "Per Saravali, Saturn in 9th causes ascetic inclinations, delayed fortune, philosophical bent, and building of public water tanks or religious shelters.",
                    "desc_ta": "9-ல் சனி நின்றால் துறவு நாட்டம், தாமதமான அதிர்ஷ்டம், பொது நலப்பணிகள் செய்தல் மற்றும் ஆன்மீக பக்குவத்தை வழங்கும்.",
                    "severity": "SeverityLevel.MIXED",
                    "sloka": "Saravali, Ch. 30, Sloka 86"
                },
                10: {
                    "en_name": "Saturn in 10th House (Karma Bhava Phala)",
                    "ta_name": "10-ஆம் வீட்டில் சனி (கர்ம பாவக பலன்)",
                    "desc_en": "Saravali proclaims Saturn in 10th: Rise to authority through relentless toil, leadership in civic affairs, ministerial position, or judicial command.",
                    "desc_ta": "10-ல் சனி அமர்வது அரிய உழைப்பால் உயர்வு; தொழிலாளர் தலைமை, நீதித்துறை, அரசியல் அல்லது நகராட்சி அதிகாரத்தை வழங்கும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 87"
                },
                11: {
                    "en_name": "Saturn in 11th House (Labha Bhava Phala)",
                    "ta_name": "11-ஆம் வீட்டில் சனி (லாப பாவக பலன்)",
                    "desc_en": "Saravali praises Saturn in 11th: Massive enduring wealth, longevity, political influence, conveyances, and command over large workforce.",
                    "desc_ta": "11-ல் சனி அமர்வது பூரண தன லாபம்; நீண்ட ஆயுள், அரசியல் செல்வாக்கு, நிலபுலன்கள் மற்றும் ஊழியர் தலைமை தரும்.",
                    "severity": "SeverityLevel.FAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 88"
                },
                12: {
                    "en_name": "Saturn in 12th House (Vyaya Bhava Phala)",
                    "ta_name": "12-ஆம் வீட்டில் சனி (வியய பாவக பலன்)",
                    "desc_en": "Saravali warns Saturn in 12th causes heavy expenditure on penalties or sickness, loneliness, living in distant foreign lands, and ascetic solitude.",
                    "desc_ta": "12-ல் சனி அமைந்தால் விரயங்கள், தனிமை, வெளிநாட்டு வாசம், தூக்கமின்மை மற்றும் ஆன்மீகத் தனிமை உண்டாகும்.",
                    "severity": "SeverityLevel.UNFAVORABLE",
                    "sloka": "Saravali, Ch. 30, Sloka 89"
                }
            }
        }
    }

    # Generate 84 rules
    for p_name, p_info in planets_data.items():
        p_code = p_name[:3].upper()
        for house_num, h_data in p_info["houses"].items():
            rule_id = f"RULE-SARAVALI-BHAVA-{p_code}-{house_num:02d}"
            rule_str = f'''    AstrologicalRuleDefinition(
        rule_id="{rule_id}",
        version=1,
        name_en="{h_data['en_name']}",
        name_ta="{h_data['ta_name']}",
        category_slug="saravali_classics",
        subcategory="saravali_bhava_phala",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "planet_house",
            "planet": "{p_name}",
            "house": {house_num},
            "chart": "d1"
        }},
        interpretation_en="{h_data['desc_en']}",
        interpretation_ta="{h_data['desc_ta']}",
        astrological_principle_en="Classical Bhava Phala: Placement of {p_name} in House {house_num} activates specific karakatvas as codified by Kalyana Varma in Saravali.",
        astrological_principle_ta="பாரம்பரிய பாவக பலன்: கல்யாண வர்மரின் சாராவளி நூலின்படி {p_info['name_ta']} பகவான் {house_num}-ஆம் பாவத்தில் அமர்வதால் ஏற்படும் தனித்துவமான பலாபலன்கள்.",
        source_reference="{h_data['sloka']}",
        limitations_en="Dignity (Exaltation, Moolatrikona, Debilitation) and aspects from benefics/malefics modify these baseline indications.",
        limitations_ta="கிரகத்தின் ஆட்சி, உச்சம், நீச நிலை மற்றும் பிற சுப/அசுப கிரகங்களின் பார்வைகள் இப்பலன்களில் மாற்றங்களை ஏற்படுத்தும்.",
        severity={h_data['severity']},
    ),'''
            rules.append(rule_str)

    # Rule 85: Malefics in Dusthanas (Ch. 30, v. 84)
    dusthana_rule = '''    AstrologicalRuleDefinition(
        rule_id="RULE-SARAVALI-BHAVA-MAL-DUSTHANA",
        version=1,
        name_en="Malefics Fortified in Dusthana (6, 8, 12 - Saravali Principle)",
        name_ta="மறைவு ஸ்தானங்களில் (6, 8, 12) பாப கிரகங்கள் அமர்வு (சாராவளி விதி)",
        category_slug="saravali_classics",
        subcategory="saravali_bhava_phala",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={
            "condition_type": "compound",
            "operator": "OR",
            "conditions": [
                {"condition_type": "planet_house", "planet": "Mars", "houses": [6, 8, 12], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Saturn", "houses": [6, 8, 12], "chart": "d1"},
                {"condition_type": "planet_house", "planet": "Sun", "houses": [6, 8, 12], "chart": "d1"}
            ]
        },
        interpretation_en="Saravali notes in Ch. 30, v. 84 that naturally malefic planets (Sun, Mars, Saturn) placed in Dusthana houses (6th, 8th, 12th) destroy the negative significations of those houses (suppressing enemies, debts, and fatal threats) while preserving vitality if fortified.",
        interpretation_ta="சாராவளி அத்தியாயம் 30, சுலோகம் 84-ன் படி, இயற்கை பாப கிரகங்களான சூரியன், செவ்வாய், சனி ஆகியோர் 6, 8, 12 ஆகிய மறைவு ஸ்தானங்களில் அமரும்போது கடன், நோய், எதிரிகள் மற்றும் விபத்துகளை அழித்து ஜாதகருக்கு வெற்றியைத் தருகின்றனர்.",
        astrological_principle_en="Dusthana Suppression Principle: Malefics in 3, 6, 11 destroy house distress, functioning as powerful protectors when not afflicting Lagna Lord.",
        astrological_principle_ta="மறைவு ஸ்தான பாபக் கிரக ஆளுமை விதி: 6, 8, 12-ல் பாபிகள் இருப்பது தீய பலன்களை அழித்து சுபத்துவத்தை நிலைநிறுத்தும்.",
        source_reference="Saravali, Ch. 30, Sloka 84",
        limitations_en="If combust or aspecting Lagna, physical distress or sudden surgeries may occur.",
        limitations_ta="லக்னாதிபதியைப் பார்த்தாலோ அல்லது அஸ்தமனம் பெற்றாலோ உடல்நலக் கோளாறுகள் ஏற்படலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),'''
    rules.append(dusthana_rule)

    return rules
