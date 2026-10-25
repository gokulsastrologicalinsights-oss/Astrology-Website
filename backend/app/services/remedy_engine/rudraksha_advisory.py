"""Classical Rudraksha Shastra & Compatibility Engine.

Based on sacred scriptures:
- Shiva Purana (Vidyeshvara Samhita & Uma Samhita)
- Padma Purana (Srishti Khanda)
- Shrimad Devi Bhagavatam (Book 11)
- Rudrakshajabala Upanishad

Features:
- Complete 1 to 14 Mukhi canonical database + Gauri Shankar & Ganesh Rudraksha
- Presiding Deities, Ruling Grahas, Chakras, Beeja Mantras (Sanskrit & Tamil)
- Classical astrological benefits, dosha mitigation (Sade Sati, Kaal Sarp, Manglik, Kemadruma, etc.)
- Chart-aware recommendation engine:
    * Primary Bead (pacifies critical afflictions or strengthens Lagna)
    * Secondary Bead (career/fortune/Dasha alignment)
    * Universal Bead (5-Mukhi Panchamukhi - universally auspicious for all humanity)
- Authentic Prana Pratishtha consecration vidhi & wearing protocols
- Pure Pratikula remedy: Rudraksha safely pacifies malefic energy without solar magnification
"""

from typing import List, Dict, Any, Optional
from app.schemas.remedies import RudrakshaItem, RudrakshaRecommendationSummary


RUDRAKSHA_REGISTRY: Dict[int, Dict[str, Any]] = {
    1: {
        "mukhi": 1,
        "name_en": "1 Mukhi Rudraksha (Eka Mukhi)",
        "name_ta": "1 முக ருத்ராட்சம் (ஏக முகி)",
        "ruling_deity_en": "Lord Shiva (Paramashiva / Supreme Consciousness)",
        "ruling_deity_ta": "சிவபெருமான் (பரமசிவன்)",
        "ruling_graha": "sun",
        "ruling_graha_en": "Sun (Surya)",
        "ruling_graha_ta": "சூரியன்",
        "chakra_en": "Sahasrara (Crown) & Ajna (Third Eye)",
        "chakra_ta": "துரியம் (சகஸ்ரார சக்கரம்) & ஆக்ஞா சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं नमः (Om Hreem Namah) / ॐ ॐ दृशां नमः",
        "beeja_mantra_en": "Om Hreem Namah / Om Om Drisham Namah",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் நமஹ / ஓம் ஓம் த்ருஷாம் நமஹ",
        "astrological_benefits_en": "Destroys all sins of past lives, cures Sun-related afflictions, enhances leadership, willpower, administrative authority, and leads to spiritual liberation (Moksha).",
        "astrological_benefits_ta": "முற்பிறவி பாவங்களை நீக்கும்; சூரிய தோஷம், பித்ரு தோஷம் நிவர்த்தியாகும்; தலைமைப் பண்பு, மன உறுதி, அரசு மரியாதை மற்றும் முக்தி அடைய வழிவகுக்கும்.",
        "doshas_mitigated_en": ["Surya Dosha (Afflicted Sun)", "Pitru Dosha", "Low Self-Confidence", "Eye and Bone Ailments"],
        "doshas_mitigated_ta": ["சூரிய தோஷம்", "பித்ரு தோஷம்", "தன்னம்பிக்கை குறைபாடு", "கண் மற்றும் எலும்பு உபாதைகள்"],
        "who_should_wear_en": "Leaders, spiritual seekers, administrators, doctors, CEOs, and those seeking detachment with worldly victory.",
        "who_should_wear_ta": "தலைவர்கள், ஆன்மீக சாதகர்கள், நிர்வாகிகள், மருத்துவர்கள் மற்றும் உயர் பதவிகளில் உள்ளவர்கள்.",
        "wearing_protocol_en": "Cap in pure 22K Gold or Sterling Silver. Wear on a Sunday morning during Shukla Paksha after reciting 108 Surya Mantras.",
        "wearing_protocol_ta": "தங்கம் அல்லது வெள்ளியில் கட்டி, வளர்பிறை ஞாயிறு காலை 108 முறை மூல மந்திரம் ஜெபித்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
    2: {
        "mukhi": 2,
        "name_en": "2 Mukhi Rudraksha (Dwi Mukhi)",
        "name_ta": "2 முக ருத்ராட்சம் (த்வி முகி)",
        "ruling_deity_en": "Ardhanarishvara (Shiva & Shakti Divine Union)",
        "ruling_deity_ta": "அர்த்தநாரீஸ்வரர் (சிவன்-சக்தி ஐக்கியம்)",
        "ruling_graha": "moon",
        "ruling_graha_en": "Moon (Chandra)",
        "ruling_graha_ta": "சந்திரன்",
        "chakra_en": "Swadhisthana (Sacral Chakra)",
        "chakra_ta": "சுவாதிஷ்டான சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ नमः (Om Namah) / ॐ खं कस्तूरी नमः",
        "beeja_mantra_en": "Om Namah / Om Kham Kastoori Namah",
        "beeja_mantra_ta": "ஓம் நமஹ / ஓம் கம் கஸ்தூரி நமஹ",
        "astrological_benefits_en": "Removes Chandra Dosha, cures Kemadruma Dosha, relieves emotional instability, anxiety, and depression. Unsurpassed for fostering marital harmony and mutual affection between partners.",
        "astrological_benefits_ta": "சந்திர தோஷம் மற்றும் கேமத்ரும தோஷத்தை போக்கும்; மன அமைதி, மன அழுத்தம் நீங்குதல், தம்பதியர் ஒற்றுமை மற்றும் குடும்ப நல்லுறவை வளர்க்கும்.",
        "doshas_mitigated_en": ["Chandra Dosha (Afflicted Moon)", "Kemadruma Dosha", "Depression & Mood Swings", "Marital Discord"],
        "doshas_mitigated_ta": ["சந்திர தோஷம்", "கேமத்ரும தோஷம்", "மன அழுத்தம் & மன ஊசலாட்டம்", "தம்பதியர் கருத்து வேறுபாடு"],
        "who_should_wear_en": "Couples facing disharmony, artists, individuals suffering from insomnia, emotional trauma, or mental restlessness.",
        "who_should_wear_ta": "தம்பதியர் ஒற்றுமை நாடுவோர், மன சஞ்சலம் மற்றும் தூக்கமின்மையால் அவதிப்படுவோர்.",
        "wearing_protocol_en": "Cap in Pure Silver and wear with white silk thread on a Monday evening after reciting 108 Chandra Mantras.",
        "wearing_protocol_ta": "வெள்ளியில் கட்டி, வெள்ளை பட்டு நூலில் வளர்பிறை திங்கட்கிழமை மாலை அணிவது சிறப்பு.",
        "is_pratikula_remedy": True,
    },
    3: {
        "mukhi": 3,
        "name_en": "3 Mukhi Rudraksha (Tri Mukhi)",
        "name_ta": "3 முக ருத்ராட்சம் (த்ரி முகி)",
        "ruling_deity_en": "Agni Deva (The Sacred Fire of Purification)",
        "ruling_deity_ta": "அக்னி தேவன் (தூய்மைப்படுத்தும் நெருப்புக் கடவுள்)",
        "ruling_graha": "mars",
        "ruling_graha_en": "Mars (Mangala / Chevvai)",
        "ruling_graha_ta": "செவ்வாய் (அங்காரகன்)",
        "chakra_en": "Manipura (Solar Plexus Chakra)",
        "chakra_ta": "மணிபூரக சக்கரம் (தொப்புள் மையம்)",
        "beeja_mantra_sanskrit": "ॐ क्लीं नमः (Om Kleem Namah)",
        "beeja_mantra_en": "Om Kleem Namah",
        "beeja_mantra_ta": "ஓம் க்லீம் நமஹ",
        "astrological_benefits_en": "Directly burns past karmic sins, pacifies severe Kuja / Manglik Dosha, dissolves inferiority complex, fear, and lethargy. Ignites dynamic energy, courage, and vitality.",
        "astrological_benefits_ta": "பாவ வினைகளை சுட்டெரிக்கும்; கடுமையான செவ்வாய் தோஷம் (மாங்கல்ய தோஷம்) நீக்கும்; தாழ்வு மனப்பான்மை, அச்சம் நீங்கி வீரியமும் சுறுசுறுப்பும் பிறக்கும்.",
        "doshas_mitigated_en": ["Manglik / Kuja Dosha", "Angarak Dosha", "Lethargy & Self-Doubt", "Digestive & Blood Impurities"],
        "doshas_mitigated_ta": ["செவ்வாய் தோஷம்", "அங்காரக தோஷம்", "சோம்பல் & பயம்", "செரிமான மற்றும் ரத்தக் கோளாறுகள்"],
        "who_should_wear_en": "Those suffering from depression, suppressed anger, Manglik delay in marriage, athletes, military/police officers, and engineers.",
        "who_should_wear_ta": "செவ்வாய் தோஷம் உள்ளவர்கள், திருமணத் தடை சந்திப்போர், விளையாட்டு வீரர்கள், காவல்/ராணுவப் பணியாளர்கள்.",
        "wearing_protocol_en": "Cap in Pure Copper or Gold, strung on red silk thread. Don on a Tuesday morning during Mars Hora.",
        "wearing_protocol_ta": "செம்பு அல்லது தங்கத்தில் கட்டி, சிவப்பு நூலில் செவ்வாய்க்கிழமை காலை செவ்வாய் ஓரையில் அணியவும்.",
        "is_pratikula_remedy": True,
    },
    4: {
        "mukhi": 4,
        "name_en": "4 Mukhi Rudraksha (Chatur Mukhi)",
        "name_ta": "4 முக ருத்ராட்சம் (சதுர் முகி)",
        "ruling_deity_en": "Lord Brahma (The Creator of the Universe)",
        "ruling_deity_ta": "பிரம்மா (படைப்புக் கடவுள்)",
        "ruling_graha": "mercury",
        "ruling_graha_en": "Mercury (Budhan)",
        "ruling_graha_ta": "புதன்",
        "chakra_en": "Vishuddha (Throat Chakra)",
        "chakra_ta": "விசுத்தி சக்கரம் (தொண்டை மையம்)",
        "beeja_mantra_sanskrit": "ॐ ह्रीं नमः (Om Hreem Namah) / ॐ वां नमः",
        "beeja_mantra_en": "Om Hreem Namah / Om Vaam Namah",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் நமஹ / ஓம் வாம் நமஹ",
        "astrological_benefits_en": "Neutralizes Mercury debility and speech impediments; stimulates immense intellect, memory retention, logical reasoning, and eloquent communication.",
        "astrological_benefits_ta": "புதன் பலவீனத்தை நீக்கும்; ஞாபக சக்தி, கூர்மையான புத்தி, நாவன்மை, வாதத் திறன் மற்றும் பேச்சாற்றலை அபரிமிதமாக உயர்த்தும்.",
        "doshas_mitigated_en": ["Budha Dosha (Debilitated Mercury)", "Speech Impediments & Stammering", "Memory Weakness", "Nervous Restlessness"],
        "doshas_mitigated_ta": ["புதன் தோஷம்", "திக்குவாய் & பேச்சுத் தடுமாற்றம்", "மறதி", "நரம்பு தளர்ச்சி"],
        "who_should_wear_en": "Students, writers, teachers, journalists, chartered accountants, software engineers, and public speakers.",
        "who_should_wear_ta": "மாணவர்கள், ஆசிரியர்கள், எழுத்தாளர்கள், வழக்கறிஞர்கள், கணக்காளர்கள் மற்றும் மேடைப் பேச்சாளர்கள்.",
        "wearing_protocol_en": "Cap in Silver or Gold, wear on a Wednesday morning after offering green gram (moong) and reciting 108 Budha Mantras.",
        "wearing_protocol_ta": "வெள்ளியில் கட்டி, புதன்கிழமை காலை பாசிப்பயறு சமர்ப்பித்து 108 முறை புதன் மந்திரம் ஜெபித்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
    5: {
        "mukhi": 5,
        "name_en": "5 Mukhi Rudraksha (Pancha Mukhi)",
        "name_ta": "5 முக ருத்ராட்சம் (பஞ்ச முகி)",
        "ruling_deity_en": "Kalagni Rudra (Lord Shiva's Time-Dissolving Aspect)",
        "ruling_deity_ta": "காலாக்னி ருத்ரன் (காலத்தை வென்ற சிவ வடிவம்)",
        "ruling_graha": "jupiter",
        "ruling_graha_en": "Jupiter (Guru / Brihaspati)",
        "ruling_graha_ta": "குரு பகவான்",
        "chakra_en": "Vishuddha & Anahata (Heart Chakra)",
        "chakra_ta": "விசுத்தி மற்றும் அனாகத சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं नमः (Om Hreem Namah) / ॐ नमः शिवाय",
        "beeja_mantra_en": "Om Hreem Namah / Om Namah Shivaya",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் நமஹ / ஓம் நம சிவாய",
        "astrological_benefits_en": "Universally auspicious for all humanity with zero negative side effects. Harmonizes blood pressure, calms the mind, neutralizes Guru Chandal Dosha, and bestows longevity and spiritual peace.",
        "astrological_benefits_ta": "அனைத்து மனிதர்களுக்கும் பொதுவானது; எவ்வித பக்கவிளைவும் அற்றது. ரத்த அழுத்தம் சீராக்கும்; குரு சண்டாள தோஷம் நீக்கும்; ஞானமும் ஆயுளும் வழங்கும்.",
        "doshas_mitigated_en": ["Guru Chandal Dosha", "Jupiter Afflictions", "High Blood Pressure", "Anxiety & Anger"],
        "doshas_mitigated_ta": ["குரு சண்டாள தோஷம்", "குரு தோஷம்", "ரத்தக் கொதிப்பு", "மன அமைதியின்மை & கோபம்"],
        "who_should_wear_en": "Universally recommended for everyone — students, householders, elders, professionals, and spiritual seekers.",
        "who_should_wear_ta": "அனைத்து ராசி, லக்னக்காரர்களும் எவ்வித கட்டுப்பாடும் இன்றி அணியலாம்.",
        "wearing_protocol_en": "Can be worn as a single bead or a 108-bead Japa Mala on yellow or red silk thread on any auspicious Thursday or Monday.",
        "wearing_protocol_ta": "மஞ்சள் அல்லது சிவப்பு நூலில் வியாழன் அல்லது திங்கட்கிழமையில் அணியலாம்.",
        "is_pratikula_remedy": True,
    },
    6: {
        "mukhi": 6,
        "name_en": "6 Mukhi Rudraksha (Shanmukhi)",
        "name_ta": "6 முக ருத்ராட்சம் (ஷண்முகி)",
        "ruling_deity_en": "Lord Kartikeya (Skanda / Murugan)",
        "ruling_deity_ta": "முருகப்பெருமான் (கந்தக் கடவுள்)",
        "ruling_graha": "venus",
        "ruling_graha_en": "Venus (Sukran) / Mars",
        "ruling_graha_ta": "சுக்கிரன் / செவ்வாய்",
        "chakra_en": "Swadhisthana (Sacral Chakra)",
        "chakra_ta": "சுவாதிஷ்டான சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं हुं नमः (Om Hreem Hoom Namah)",
        "beeja_mantra_en": "Om Hreem Hoom Namah",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் ஹூம் நமஹ",
        "astrological_benefits_en": "Bestows magnetic charm, emotional grounding, immense willpower, stamina, and victory in competitive pursuits. Pacifies Venus afflictions and reproductive imbalances.",
        "astrological_benefits_ta": "முருகனின் பரிபூரண அருள்; கவர்ச்சி, வசீகரம், அபார மனோபலம், போட்டிகளில் வெற்றி, சுக்கிர தோஷம் மற்றும் பாலியல் சமநிலையின்மையை நீக்கும்.",
        "doshas_mitigated_en": ["Shukra Dosha (Venus Afflictions)", "Lack of Willpower", "Obesity & Lethargy", "Competitive Blockages"],
        "doshas_mitigated_ta": ["சுக்கிர தோஷம்", "மன உறுதி இன்மை", "உடல் பருமன்", "போட்டிகளில் தோல்வி பயம்"],
        "who_should_wear_en": "Actors, artists, company managers, athletes, competitive exam aspirants, and Murugan devotees.",
        "who_should_wear_ta": "கலைஞர்கள், நிர்வாகிகள், விளையாட்டு வீரர்கள், அரசுத் தேர்வு எழுதுவோர் மற்றும் முருக பக்தர்கள்.",
        "wearing_protocol_en": "Cap in Silver or Copper, wear on a Friday morning or Tuesday morning on a red silk thread.",
        "wearing_protocol_ta": "வெள்ளி அல்லது செம்பில் கட்டி, வெள்ளி அல்லது செவ்வாய்க்கிழமை காலை அணியவும்.",
        "is_pratikula_remedy": True,
    },
    7: {
        "mukhi": 7,
        "name_en": "7 Mukhi Rudraksha (Sapta Mukhi)",
        "name_ta": "7 முக ருத்ராட்சம் (சப்த முகி)",
        "ruling_deity_en": "Goddess Mahalakshmi (Goddess of Wealth & Fortune)",
        "ruling_deity_ta": "மகாலட்சுமி தேவி (செல்வத்தின் அதிபதி)",
        "ruling_graha": "saturn",
        "ruling_graha_en": "Saturn (Saneeswara)",
        "ruling_graha_ta": "சனி பகவான்",
        "chakra_en": "Anahata (Heart Chakra) & Manipura",
        "chakra_ta": "அனாகத சக்கரம் (இதய மையம்)",
        "beeja_mantra_sanskrit": "ॐ हुं नमः (Om Hoom Namah) / ॐ महालक्ष्म्यै नमः",
        "beeja_mantra_en": "Om Hoom Namah / Om Mahalakshmyai Namah",
        "beeja_mantra_ta": "ஓம் ஹூம் நமஹ / ஓம் மகாலக்ஷ்ம்யை நமஹ",
        "astrological_benefits_en": "Supreme classical antidote for Sade Sati, Ashtama Shani, Kantaka Shani, and Shani Mahadasha. Dissolves severe financial distress, poverty, business debt, and opens prosperous avenues.",
        "astrological_benefits_ta": "ஏழரைச் சனி, அஷ்டமச் சனி, கண்டகச் சனி மற்றும் சனி தசா-புத்திக்கு மிகச் சிறந்த பரிகாரம். வறுமை, கடன் தொல்லை நீங்கி மகாலட்சுமியின் அருள் நிலைக்கும்.",
        "doshas_mitigated_en": ["Sade Sati (7.5 Years Saturn)", "Ashtama Shani", "Shani Dosha", "Financial Ruin & Chronic Debts"],
        "doshas_mitigated_ta": ["ஏழரைச் சனி", "அஷ்டமச் சனி", "சனி தோஷம்", "கடன் சுமை & பண நெருக்கடி"],
        "who_should_wear_en": "Anyone undergoing Sade Sati, business owners struggling with chronic cash flow deficits, professionals facing career stagnation.",
        "who_should_wear_ta": "ஏழரைச் சனி, அஷ்டமச் சனி நடப்பவர்கள், தொழிலில் நஷ்டம் சந்திப்போர், தீவிர கடன் சுமையில் உள்ளவர்கள்.",
        "wearing_protocol_en": "Cap in Silver or Panchadhatu, wear on a Saturday twilight or Friday morning on a black/red silk thread after chanting Shani and Lakshmi mantras.",
        "wearing_protocol_ta": "வெள்ளி அல்லது பஞ்சலோகத்தில் கட்டி, சனிக்கிழமை மாலை அல்லது வெள்ளிக்கிழமை காலை அணியவும்.",
        "is_pratikula_remedy": True,
    },
    8: {
        "mukhi": 8,
        "name_en": "8 Mukhi Rudraksha (Ashta Mukhi)",
        "name_ta": "8 முக ருத்ராட்சம் (அஷ்ட முகி)",
        "ruling_deity_en": "Lord Ganesha (Vighnaharta / Remover of Obstacles)",
        "ruling_deity_ta": "விநாயகப் பெருமான் (விக்னஹர்த்தா)",
        "ruling_graha": "rahu",
        "ruling_graha_en": "Rahu (North Lunar Node)",
        "ruling_graha_ta": "ராகு பகவான்",
        "chakra_en": "Muladhara (Root Chakra)",
        "chakra_ta": "மூலாதார சக்கரம் (அடிப்படை மையம்)",
        "beeja_mantra_sanskrit": "ॐ हुं नमः (Om Hoom Namah) / ॐ गं गणपतये नमः",
        "beeja_mantra_en": "Om Hoom Namah / Om Gam Ganapataye Namah",
        "beeja_mantra_ta": "ஓம் ஹூம் நமஹ / ஓம் கம் கணபதயே நமஹ",
        "astrological_benefits_en": "Directly pacifies Rahu afflictions, Kaal Sarp Dosha, and Sarpa Dosha. Eliminates sudden unforeseen hurdles, hidden enemies, illusions, night terrors, and speculative losses.",
        "astrological_benefits_ta": "ராகு தோஷம், கால சர்ப்ப தோஷம், நாக தோஷம் ஆகியவற்றை நீக்கும். திடீர் தடைகள், மறைமுக எதிரிகள், மாயை மற்றும் பயத்தை தகர்த்து வெற்றி தரும்.",
        "doshas_mitigated_en": ["Kaal Sarp Dosha", "Rahu Mahadasha / Bhukti", "Sarpa Dosha", "Sudden Obstacles & Phobias"],
        "doshas_mitigated_ta": ["கால சர்ப்ப தோஷம்", "ராகு தசை/புக்தி தோஷம்", "நாக தோஷம்", "திடீர் தடைகள் & விபத்து பயம்"],
        "who_should_wear_en": "Those running Rahu Dasha/Bhukti, individuals with Kaal Sarp Dosha, occult researchers, share traders, and entrepreneurs facing frequent sudden setbacks.",
        "who_should_wear_ta": "ராகு தசை நடப்பவர்கள், கால சர்ப்ப தோஷம் உள்ளவர்கள், புதிய தொழில் தொடங்குவோர்.",
        "wearing_protocol_en": "Cap in Silver or Ashtadhatu, wear on a Wednesday or Saturday morning after offering grass (Aruvam Pul) to Lord Ganesha.",
        "wearing_protocol_ta": "வெள்ளியில் கட்டி, புதன் அல்லது சனிக்கிழமை விநாயகருக்கு அருகம்புல் சாற்றி 108 முறை கணபதி மந்திரம் ஓதி அணியவும்.",
        "is_pratikula_remedy": True,
    },
    9: {
        "mukhi": 9,
        "name_en": "9 Mukhi Rudraksha (Nava Mukhi)",
        "name_ta": "9 முக ருத்ராட்சம் (நவ முகி)",
        "ruling_deity_en": "Goddess Durga / Navadurga (9 Divine Shakti Aspects)",
        "ruling_deity_ta": "துர்க்கா பரமேஸ்வரி (நவதுர்க்கை)",
        "ruling_graha": "ketu",
        "ruling_graha_en": "Ketu (South Lunar Node)",
        "ruling_graha_ta": "கேது பகவான்",
        "chakra_en": "Sahasrara & Ajna Chakra",
        "chakra_ta": "துரியம் & ஆக்ஞா சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं हुं नमः (Om Hreem Hoom Namah) / ॐ दुं दुर्गायै नमः",
        "beeja_mantra_en": "Om Hreem Hoom Namah / Om Doom Durgayai Namah",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் ஹூம் நமஹ / ஓம் தும்துர்காயை நமஹ",
        "astrological_benefits_en": "Neutralizes Ketu afflictions, mysterious chronic ailments, mental phobias, and occult disturbances. Imparts dynamic courage, fearlessness, maternal protection, and spiritual detachment.",
        "astrological_benefits_ta": "கேது தோஷம், இனம் புரியாத பயம், தீய சக்திகளின் தாக்கம், கண் திருஷ்டி நீக்கும். துர்க்கையின் அருளால் அதீத தைரியம், பாதுகாப்பு மற்றும் ஆன்மீக முக்தி கிட்டும்.",
        "doshas_mitigated_en": ["Ketu Mahadasha / Bhukti", "Grahan Dosha", "Occult Disturbances & Evil Eye", "Phobias & Panic Attacks"],
        "doshas_mitigated_ta": ["கேது தசை/புக்தி தோஷம்", "கிரகண தோஷம்", "கண் திருஷ்டி & செய்வினை பயம்", "மன நடுக்கம்"],
        "who_should_wear_en": "Those running Ketu Dasha, women seeking divine protection, spiritual meditators, and individuals troubled by phobias or unexplainable distress.",
        "who_should_wear_ta": "கேது தசை நடப்பவர்கள், பெண்கள், ஆன்மீக யோகிகள் மற்றும் திருஷ்டி தோஷத்தால் பாதிக்கப்பட்டவர்கள்.",
        "wearing_protocol_en": "Cap in Silver or Gold, wear on a Friday morning or Tuesday during Rahu Kaal / Durga Puja on a red silk thread.",
        "wearing_protocol_ta": "வெள்ளியில் கட்டி, செவ்வாய் அல்லது வெள்ளிக்கிழமை துர்க்கை வழிபாட்டிற்கு பின் அணியவும்.",
        "is_pratikula_remedy": True,
    },
    10: {
        "mukhi": 10,
        "name_en": "10 Mukhi Rudraksha (Dasha Mukhi)",
        "name_ta": "10 முக ருத்ராட்சம் (தச முகி)",
        "ruling_deity_en": "Lord Mahavishnu (The Supreme Preserver)",
        "ruling_deity_ta": "மகாவிஷ்ணு (காக்கும் கடவுள்)",
        "ruling_graha": "all",
        "ruling_graha_en": "All 9 Planets (Navagraha Shield)",
        "ruling_graha_ta": "நவக்கிரகங்கள் அனைத்தும்",
        "chakra_en": "Anahata & Manipura Chakra",
        "chakra_ta": "அனாகத & மணிபூரக சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं नमः (Om Hreem Namah) / ॐ नमो भगवते वासुदेवाय",
        "beeja_mantra_en": "Om Hreem Namah / Om Namo Bhagavate Vasudevaya",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் நமஹ / ஓம் நமோ பகவதே வாசுதேவாய",
        "astrological_benefits_en": "Acts as an impenetrable armor against all 9 planetary malefic vibrations, evil eye (drishti), black magic, and legal disputes. Pacifies restless ancestors and shields the family lineage.",
        "astrological_benefits_ta": "நவக்கிரக தோஷங்கள் அனைத்திற்கும் ஒரே கவசம்; எதிரிகள் பயம், வழக்குகள், பில்லி-சூனியம் மற்றும் திருஷ்டி தோஷங்களை முற்றிலுமாக அழிக்கும்.",
        "doshas_mitigated_en": ["All Navagraha Doshas Simultaneously", "Court Cases & Legal Battles", "Black Magic & Evil Eye", "Pitru Shraap"],
        "doshas_mitigated_ta": ["நவக்கிரக தோஷங்கள் யாவும்", "நீதிமன்ற வழக்குகள்", "தீய கண் திருஷ்டி", "பித்ரு சாபம்"],
        "who_should_wear_en": "Individuals facing multifaceted planetary afflictions, court cases, business sabotage, or high-risk administrative careers.",
        "who_should_wear_ta": "பல கிரக தோஷங்களால் பாதிக்கப்பட்டவர்கள், வழக்குகளில் சிக்கியவர்கள், பெரும் தொழிலதிபர்கள்.",
        "wearing_protocol_en": "Cap in Pure Gold or Silver, wear on a Thursday morning or Ekadashi on yellow silk thread after chanting Vishnu Sahasranamam or 108 Vishnu Mantras.",
        "wearing_protocol_ta": "தங்கம் அல்லது வெள்ளியில் கட்டி, வியாழன் அல்லது ஏகாதசி நன்னாளில் விஷ்ணு மந்திரம் ஜெபித்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
    11: {
        "mukhi": 11,
        "name_en": "11 Mukhi Rudraksha (Ekadasha Mukhi)",
        "name_ta": "11 முக ருத்ராட்சம் (ஏகாதச முகி)",
        "ruling_deity_en": "11 Rudras & Lord Hanuman (Mahavira)",
        "ruling_deity_ta": "ஏகாதச ருத்ரர்கள் & வீர அனுமன்",
        "ruling_graha": "mars",
        "ruling_graha_en": "Mars & Jupiter (Higher Spiritual Mastery)",
        "ruling_graha_ta": "செவ்வாய் மற்றும் குரு",
        "chakra_en": "Vishuddha & Ajna Chakra",
        "chakra_ta": "விசுத்தி & ஆக்ஞா சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ श्रीं ॐ ह्रीं हुं फट् (Om Shreem Om Hreem Hoom Phat)",
        "beeja_mantra_en": "Om Shreem Om Hreem Hoom Phat",
        "beeja_mantra_ta": "ஓம் ஸ்ரீம் ஓம் ஹ்ரீம் ஹூம் பட்",
        "astrological_benefits_en": "Shields against accidental physical trauma, enhances judgment, self-discipline, fearlessness, oratorical authority, and physical stamina. Equivalent to performing 1,000 Ashwamedha Yagnas.",
        "astrological_benefits_ta": "விபத்துகளில் இருந்து பாதுகாப்பு; அனுமனின் அருள், அபார ஞாபக சக்தி, துணிவு, யோக சாதனை மற்றும் ஆன்மீக பலம் பெருகும்.",
        "doshas_mitigated_en": ["Accidental Injuries & Surgical Risks", "Fear of Untimely Death", "Indecision & Lack of Focus", "Speech Blockages"],
        "doshas_mitigated_ta": ["விபத்து கண்டங்கள்", "அகால மரண பயம்", "குழப்பமான மனநிலை", "தைரியமின்மை"],
        "who_should_wear_en": "Athletes, travelers, yogis, yoga teachers, security personnel, and those striving for extreme self-discipline and meditation mastery.",
        "who_should_wear_ta": "விளையாட்டு வீரர்கள், ஆன்மீக சாதகர்கள், அடிக்கடி பயணம் மேற்கொள்வோர்.",
        "wearing_protocol_en": "Cap in Silver or Copper, wear on a Tuesday morning after reciting Hanuman Chalisa.",
        "wearing_protocol_ta": "வெள்ளி அல்லது செம்பில் கட்டி, செவ்வாய்க்கிழமை காலை அனுமன் சாலிசா பாராயணம் செய்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
    12: {
        "mukhi": 12,
        "name_en": "12 Mukhi Rudraksha (Dwadasha Mukhi)",
        "name_ta": "12 முக ருத்ராட்சம் (துவாதச முகி)",
        "ruling_deity_en": "12 Adityas (Dwadasa Surya / Solar Lords)",
        "ruling_deity_ta": "துவாதச ஆதித்தர்கள் (12 சூரிய வடிவங்கள்)",
        "ruling_graha": "sun",
        "ruling_graha_en": "Sun (Surya - Radiant Aspect)",
        "ruling_graha_ta": "சூரிய பகவான்",
        "chakra_en": "Manipura & Anahata Chakra",
        "chakra_ta": "மணிபூரக & அனாகத சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ क्रौं क्षौं रौं नमः (Om Kroum Kshoum Roum Namah) / ॐ सूर्याய नमः",
        "beeja_mantra_en": "Om Kroum Kshoum Roum Namah / Om Sooryaaya Namah",
        "beeja_mantra_ta": "ஓம் க்ரௌம் க்ஷௌம் ரௌம் நமஹ / ஓம் சூர்யாய நமஹ",
        "astrological_benefits_en": "Unmatched solar radiance. Eliminates debilitating Sun curses, eye/heart/bone weakness, and political friction. Radiates magnetic charisma, administrative brilliance, and elite wealth.",
        "astrological_benefits_ta": "சூரியனின் முழுமையான தேஜஸ்; இதயம், கண் மற்றும் எலும்பு பலவீனம் நீங்கும்; அரசு மரியாதை, அரசியல் செல்வாக்கு, அதிகாரப் பதவி தரும்.",
        "doshas_mitigated_en": ["Severe Sun Debility / Combustion", "Government / Tax Disputes", "Heart & Eye Weakness", "Loss of Status / Defamation"],
        "doshas_mitigated_ta": ["சூரிய நீச தோஷம்", "அரசாங்கத் தடைகள்", "இதய உபாதைகள்", "புகழ் மங்குதல்"],
        "who_should_wear_en": "Politicians, IAS/IPS officers, top executives, ministers, public figures, and doctors.",
        "who_should_wear_ta": "அரசியல் தலைவர்கள், அரசு உயர் அதிகாரிகள், தொழிலதிபர்கள் மற்றும் சமூகப் பிரமுகர்கள்.",
        "wearing_protocol_en": "Cap in Pure 22K Gold or Copper, wear on a Sunday morning at sunrise during Shukla Paksha on a red/orange thread.",
        "wearing_protocol_ta": "தங்கம் அல்லது செம்பில் கட்டி, வளர்பிறை ஞாயிறு சூரிய உதய வேளையில் அணியவும்.",
        "is_pratikula_remedy": True,
    },
    13: {
        "mukhi": 13,
        "name_en": "13 Mukhi Rudraksha (Trayodasha Mukhi)",
        "name_ta": "13 முக ருத்ராட்சம் (திரயோதச முகி)",
        "ruling_deity_en": "Lord Kamadeva & Indra Deva",
        "ruling_deity_ta": "காமதேவன் & இந்திர தேவன்",
        "ruling_graha": "venus",
        "ruling_graha_en": "Venus (Sukran) / Mercury",
        "ruling_graha_ta": "சுக்கிரன்",
        "chakra_en": "Swadhisthana Chakra",
        "chakra_ta": "சுவாதிஷ்டான சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ ह्रीं नमः (Om Hreem Namah) / ॐ कामदेवाय नमः",
        "beeja_mantra_en": "Om Hreem Namah / Om Kamadevaya Namah",
        "beeja_mantra_ta": "ஓம் ஹ்ரீம் நமஹ / ஓம் காமதேவாய நமஹ",
        "astrological_benefits_en": "Bestows mesmerizing interpersonal magnetism, artistic genius, royal luxury, and marital fulfillment. Awakens hidden talents and grants all worldly desires (Bhoga and Moksha).",
        "astrological_benefits_ta": "அபார வசீகர சக்தி, கலைஞானம், சொகுசு வாழ்க்கை, தாம்பத்திய சுகம் மற்றும் அனைத்து இகபர சுகங்களையும் நல்கும்.",
        "doshas_mitigated_en": ["Venus Afflictions in 7th/8th Houses", "Infertility & Reproductive Imbalances", "Financial Poverty", "Lack of Charm"],
        "doshas_mitigated_ta": ["சுக்கிர தோஷம்", "தாம்பத்திய திருப்தியின்மை", "கவர்ச்சியின்மை", "செல்வ வறட்சி"],
        "who_should_wear_en": "Marketing heads, actors, creative artists, researchers, traders, and those seeking magnetic social presence and romance.",
        "who_should_wear_ta": "விற்பனை மேலாளர்கள், திரைப்படக் கலைஞர்கள், தொழிலதிபர்கள்.",
        "wearing_protocol_en": "Cap in Silver or Gold, wear on a Friday morning or Shukla Paksha Trayodashi on a silk thread.",
        "wearing_protocol_ta": "வெள்ளி அல்லது தங்கத்தில் கட்டி, வளர்பிறை திரயோதசி அல்லது வெள்ளிக்கிழமை காலை அணியவும்.",
        "is_pratikula_remedy": True,
    },
    14: {
        "mukhi": 14,
        "name_en": "14 Mukhi Rudraksha (Chaturdasha Mukhi - Devamani)",
        "name_ta": "14 முக ருத்ராட்சம் (தேவமணி - சதுர்தச முகி)",
        "ruling_deity_en": "Lord Shiva (The Supreme Ajna Eye / Mahadeva)",
        "ruling_deity_ta": "சிவபெருமான் (முக்கண்ணன் - ஆக்ஞா சக்கரம்)",
        "ruling_graha": "saturn",
        "ruling_graha_en": "Saturn (Shani) & Mars (Mangala)",
        "ruling_graha_ta": "சனி மற்றும் செவ்வாய்",
        "chakra_en": "Ajna (Third Eye Chakra)",
        "chakra_ta": "ஆக்ஞா சக்கரம் (புருவ மத்தி / நெற்றிக்கண்)",
        "beeja_mantra_sanskrit": "ॐ नमः (Om Namah) / ॐ ह्रीं नमः",
        "beeja_mantra_en": "Om Namah / Om Hreem Namah",
        "beeja_mantra_ta": "ஓம் நமஹ / ஓம் ஹ்ரீம் நமஹ",
        "astrological_benefits_en": "Known classically as 'Devamani' (Gem of the Gods). Awakens divine intuition, sixth sense, and future foresight. Fully neutralizes Manglik dosha and Sade Sati together; supreme spiritual armor.",
        "astrological_benefits_ta": "சிவபெருமானின் நெற்றிக்கண்ணில் இருந்து உருவானது; 'தேவமணி' எனப்படும். உள்ளுணர்வு மற்றும் எதிர்காலத்தை கணிக்கும் ஞானம் தரும்; சனி மற்றும் செவ்வாய் தோஷங்களை அடியோடு நிவர்த்தி செய்யும்.",
        "doshas_mitigated_en": ["Combined Shani + Mangal Curses", "Sade Sati & Kantaka Shani", "Severe Manglik Dosha", "Severe Karmic Impediments"],
        "doshas_mitigated_ta": ["சனி-செவ்வாய் சேர்க்கை தோஷம்", "ஏழரைச் சனி", "தீவிர செவ்வாய் தோஷம்", "முற்பிறவி சாபங்கள்"],
        "who_should_wear_en": "Astrologers, visionaries, intuitive healers, high-stakes investors, spiritual masters, and judges.",
        "who_should_wear_ta": "ஜோதிடர்கள், நீதிபதிகள், ஆன்மீக குருமார்கள் மற்றும் பெரிய முதலீட்டாளர்கள்.",
        "wearing_protocol_en": "Cap in 22K Gold or Silver, wear on forehead or around neck on a Monday or Saturday after 108 Shiva Panchakshari Mantras.",
        "wearing_protocol_ta": "தங்கம் அல்லது வெள்ளியில் கட்டி, திங்கள் அல்லது சனிக்கிழமை சிவபூஜை செய்து நெற்றியில் தொட்டு அணியவும்.",
        "is_pratikula_remedy": True,
    },
}

SPECIAL_RUDRAKSHA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "gauri_shankar": {
        "mukhi": 0,
        "name_en": "Gauri Shankar Rudraksha",
        "name_ta": "கௌரி சங்கர் ருத்ராட்சம்",
        "ruling_deity_en": "Lord Shiva & Goddess Parvati (Unified Cosmic Couple)",
        "ruling_deity_ta": "சிவபெருமான் மற்றும் அன்னை பார்வதி",
        "ruling_graha": "moon",
        "ruling_graha_en": "Moon & Venus (Harmony & Love)",
        "ruling_graha_ta": "சந்திரன் மற்றும் சுக்கிரன்",
        "chakra_en": "Anahata (Heart Chakra)",
        "chakra_ta": "அனாகத சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ गौरीशंकराय नमः (Om Gauri Shankaraaya Namah)",
        "beeja_mantra_en": "Om Gauri Shankaraaya Namah",
        "beeja_mantra_ta": "ஓம் கௌரிசங்கராய நமஹ",
        "astrological_benefits_en": "Two naturally conjoined beads representing the absolute union of Shiva & Shakti. Supreme blessing for marital longevity, resolving divorce threats, and fertility/conception.",
        "astrological_benefits_ta": "இயற்கையாக இணைந்த இரண்டு ருத்ராட்சங்கள். தம்பதியர் மனக்கசப்பு நீங்குதல், விவாகரத்து தவிர்த்தல், குழந்தை பாக்கியம் மற்றும் குடும்ப அமைதிக்கு இணையற்றது.",
        "doshas_mitigated_en": ["Severe Marital Discord", "Delays in Marriage", "Conception Difficulties", "7th House Afflictions"],
        "doshas_mitigated_ta": ["குடும்ப சண்டை & பிரிவு", "திருமணத் தடை", "புத்திர தோஷம்", "7-ஆம் பாவ தோஷங்கள்"],
        "who_should_wear_en": "Married couples facing discord, individuals waiting for marriage, and couples wishing for righteous progeny.",
        "who_should_wear_ta": "திருமணத் தடை உள்ளவர்கள், தம்பதியர் ஒற்றுமை நாடுவோர் மற்றும் குழந்தை வரம் வேண்டுவோர்.",
        "wearing_protocol_en": "Cap in Gold or Silver, wear around neck on a Monday or Friday after offering milk to Shiva Linga.",
        "wearing_protocol_ta": "தங்கம் அல்லது வெள்ளியில் கட்டி, திங்கள் அல்லது வெள்ளிக்கிழமையில் சிவலிங்கத்திற்கு பால் அபிஷேகம் செய்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
    "ganesh": {
        "mukhi": 0,
        "name_en": "Ganesh Rudraksha",
        "name_ta": "கணேஷ் ருத்ராட்சம்",
        "ruling_deity_en": "Lord Ganesha (Vighnaharta)",
        "ruling_deity_ta": "விநாயகப் பெருமான்",
        "ruling_graha": "mercury",
        "ruling_graha_en": "Mercury & Rahu (Intellect & Obstacle Elimination)",
        "ruling_graha_ta": "புதன் மற்றும் ராகு",
        "chakra_en": "Muladhara Chakra",
        "chakra_ta": "மூலாதார சக்கரம்",
        "beeja_mantra_sanskrit": "ॐ गं गणपतये नमः (Om Gam Ganapataye Namah)",
        "beeja_mantra_en": "Om Gam Ganapataye Namah",
        "beeja_mantra_ta": "ஓம் கம் கணபதயே நமஹ",
        "astrological_benefits_en": "Features an authentic natural trunk-like protrusion. Bestows obstacle-free progress, commercial prosperity, sharp analytical wit, and academic laurels.",
        "astrological_benefits_ta": "இயற்கையான தும்பிக்கை அமைப்பை கொண்டது. தொழில் தடைகளை தகர்க்கும்; வியாபார விருத்தி, புத்தி கூர்மை மற்றும் கல்வியில் சாதனை தரும்.",
        "doshas_mitigated_en": ["Chronic Hurdles in Projects", "Educational Distractions", "Business Losses", "Ketu / Rahu Afflictions"],
        "doshas_mitigated_ta": ["காரியத் தடைகள்", "கல்வியில் கவனக்குறைவு", "தொழில் நஷ்டம்"],
        "who_should_wear_en": "Entrepreneurs, students preparing for exams, software engineers, and those launching fresh initiatives.",
        "who_should_wear_ta": "தொழில்முனைவோர், மாணவர்கள், புதிய முயற்சி தொடங்குவோர்.",
        "wearing_protocol_en": "Cap in Silver or Gold, wear on a Wednesday morning on a red/green thread after Ganesha Puja.",
        "wearing_protocol_ta": "வெள்ளியில் கட்டி, புதன்கிழமை காலை விநாயகர் வழிபாடு செய்து அணியவும்.",
        "is_pratikula_remedy": True,
    },
}


class RudrakshaAdvisoryEngine:
    """Evaluates authentic 1-to-14 Mukhi Rudraksha Shastra & personalized compatibility."""

    @classmethod
    def get_all_beads(cls) -> List[RudrakshaItem]:
        """Returns the full canonical catalogue of 1-to-14 Mukhi + special beads."""
        items: List[RudrakshaItem] = []
        for m in range(1, 15):
            items.append(RudrakshaItem(**RUDRAKSHA_REGISTRY[m]))
        for _, s_data in SPECIAL_RUDRAKSHA_REGISTRY.items():
            items.append(RudrakshaItem(**s_data))
        return items

    @classmethod
    def evaluate_rudraksha(
        cls,
        lagna_sign: str,
        moon_sign: Optional[str] = None,
        running_mahadasha: Optional[str] = None,
        running_bhukti: Optional[str] = None,
        debilitated_planets: Optional[List[str]] = None,
        combust_planets: Optional[List[str]] = None,
        has_kuja_dosha: bool = False,
        has_sade_sati: bool = False,
        has_kaal_sarp: bool = False,
    ) -> RudrakshaRecommendationSummary:
        """Determines personalized primary, secondary, and universal beads based on chart."""
        deb_set = {p.lower() for p in (debilitated_planets or [])}
        com_set = {p.lower() for p in (combust_planets or [])}
        dasha_lower = (running_mahadasha or "").lower()

        # Universal Bead is always 5-Mukhi
        universal_bead = RudrakshaItem(**RUDRAKSHA_REGISTRY[5])

        # Priority 1: Sade Sati or Saturn Debility -> 7-Mukhi (Mahalakshmi / Shani pacification)
        # Priority 2: Kaal Sarp / Rahu affliction -> 8-Mukhi (Ganesha / Rahu pacification)
        # Priority 3: Kuja Dosha / Mars affliction -> 3-Mukhi (Agni / Mangal pacification)
        # Priority 4: Ketu affliction -> 9-Mukhi (Durga / Ketu pacification)
        # Priority 5: Sun affliction / debility -> 1-Mukhi or 12-Mukhi (Surya)
        # Priority 6: Moon affliction / Kemadruma -> 2-Mukhi (Ardhanarishvara)
        # Priority 7: Mercury affliction -> 4-Mukhi (Brahma / Budhan)
        # Priority 8: Venus affliction -> 6-Mukhi (Kartikeya / Sukran)
        # Priority 9: Jupiter affliction -> 5-Mukhi or 11-Mukhi (11 Rudras)

        primary_mukhi = 5
        primary_reason_en = ""
        primary_reason_ta = ""

        if has_sade_sati or "saturn" in deb_set or dasha_lower == "saturn":
            primary_mukhi = 7
            primary_reason_en = (
                f"7 Mukhi Rudraksha (Goddess Mahalakshmi & Saturn) is prescribed because you have active "
                f"Saturn influences ({'Sade Sati' if has_sade_sati else 'Saturn Dasha/Debility'}). "
                "Unlike Blue Sapphire gemstone, 7 Mukhi safely dissolves financial hardship and delays without any risk."
            )
            primary_reason_ta = (
                f"சனி பகவானின் தாக்கம் உள்ளதால் ({'ஏழரைச் சனி' if has_sade_sati else 'சனி தசா/நீசம்'}), "
                "7 முக ருத்ராட்சம் (மகாலட்சுமி வடிவம்) பரிந்துரைக்கப்படுகிறது. நீலக்கல்லைப் போன்ற பக்கவிளைவுகள் இன்றி "
                "பணக்கஷ்டம், ஆரோக்கிய உபாதைகளை பாதுகாப்பாக போக்கும்."
            )
        elif has_kaal_sarp or "rahu" in deb_set or dasha_lower == "rahu":
            primary_mukhi = 8
            primary_reason_en = (
                f"8 Mukhi Rudraksha (Lord Ganesha & Rahu) is prescribed to neutralize "
                f"{'Kaal Sarp Dosha' if has_kaal_sarp else 'Rahu affliction'}. It grounds chaotic thoughts and dissolves sudden roadblocks."
            )
            primary_reason_ta = (
                f"{'கால சர்ப்ப தோஷம்' if has_kaal_sarp else 'ராகுவின் தாக்கம்'} உள்ளதால், 8 முக ருத்ராட்சம் (விநாயகர் வடிவம்) பரிந்துரைக்கப்படுகிறது. "
                "திடீர் தடைகள் மற்றும் மனக் குழப்பங்களை அகற்றி தெளிவு தரும்."
            )
        elif has_kuja_dosha or "mars" in deb_set or dasha_lower == "mars":
            primary_mukhi = 3
            primary_reason_en = (
                f"3 Mukhi Rudraksha (Agni Deva & Mars) is prescribed to pacify "
                f"{'Kuja / Manglik Dosha' if has_kuja_dosha else 'Mars affliction'}. It incinerates past karmic burdens and clears marriage obstacles."
            )
            primary_reason_ta = (
                f"{'செவ்வாய் தோஷம்' if has_kuja_dosha else 'செவ்வாய் பலவீனம்'} உள்ளதால், 3 முக ருத்ராட்சம் (அக்னி தேவன் வடிவம்) பரிந்துரைக்கப்படுகிறது. "
                "கர்ம வினைகளை சுட்டெரித்து திருமணத் தடைகளை நீக்கும்."
            )
        elif "ketu" in deb_set or dasha_lower == "ketu":
            primary_mukhi = 9
            primary_reason_en = "9 Mukhi Rudraksha (Goddess Durga & Ketu) is prescribed to pacify Ketu, granting maternal protection and removing fear."
            primary_reason_ta = "கேதுவின் தாக்கத்தை போக்க 9 முக ருத்ராட்சம் (துர்க்கை வடிவம்) பரிந்துரைக்கப்படுகிறது. அச்சம் நீங்கி தைரியமும் அருளும் கிட்டும்."
        elif "sun" in deb_set or dasha_lower == "sun":
            primary_mukhi = 12
            primary_reason_en = "12 Mukhi Rudraksha (12 Adityas & Sun) is prescribed to revitalize solar energy, boosting health, vitality, and authority."
            primary_reason_ta = "சூரியனின் ஆற்றலை வலுப்படுத்த 12 முக ருத்ராட்சம் (துவாதச ஆதித்தர்கள் வடிவம்) பரிந்துரைக்கப்படுகிறது. உடல்நலமும் அரசு மரியாதையும் கூடும்."
        elif "moon" in deb_set or dasha_lower == "moon":
            primary_mukhi = 2
            primary_reason_en = "2 Mukhi Rudraksha (Ardhanarishvara & Moon) is prescribed to harmonize lunar energy, emotional stability, and relationships."
            primary_reason_ta = "சந்திரனின் பலவீனத்தை நீக்கி மன அமைதி மற்றும் குடும்ப ஒற்றுமை பெற 2 முக ருத்ராட்சம் (அர்த்தநாரீஸ்வரர் வடிவம்) பரிந்துரைக்கப்படுகிறது."
        elif "mercury" in deb_set or dasha_lower == "mercury":
            primary_mukhi = 4
            primary_reason_en = "4 Mukhi Rudraksha (Lord Brahma & Mercury) is prescribed to awaken intellectual brilliance, speech fluency, and memory."
            primary_reason_ta = "புதனின் பலவீனத்தை போக்கி கூர்மையான அறிவு, நாவன்மை மற்றும் கல்வி மேன்மை பெற 4 முக ருத்ராட்சம் (பிரம்மா வடிவம்) பரிந்துரைக்கப்படுகிறது."
        elif "venus" in deb_set or dasha_lower == "venus":
            primary_mukhi = 6
            primary_reason_en = "6 Mukhi Rudraksha (Lord Kartikeya & Venus) is prescribed to strengthen willpower, physical charm, and emotional balance."
            primary_reason_ta = "சுக்கிரனின் பலவீனத்தை போக்கி முருகனின் அருளோடு மன உறுதி, கவர்ச்சி மற்றும் சுப பலன்களைப் பெற 6 முக ருத்ராட்சம் பரிந்துரைக்கப்படுகிறது."
        else:
            # Default to Lagna-based alignment
            lagna_map = {
                "Aries": 3, "Taurus": 6, "Gemini": 4, "Cancer": 2,
                "Leo": 12, "Virgo": 4, "Libra": 6, "Scorpio": 3,
                "Sagittarius": 11, "Capricorn": 7, "Aquarius": 7, "Pisces": 11
            }
            primary_mukhi = lagna_map.get(lagna_sign, 5)
            primary_reason_en = f"Selected {primary_mukhi} Mukhi Rudraksha as the optimal vibrational resonance for {lagna_sign} Lagna."
            primary_reason_ta = f"{lagna_sign} லக்னத்திற்கு உகந்த மின்காந்த அதிர்வலைகளைக் கொண்டதாக {primary_mukhi} முக ருத்ராட்சம் பரிந்துரைக்கப்படுகிறது."

        primary_bead = RudrakshaItem(**RUDRAKSHA_REGISTRY[primary_mukhi])

        # Secondary Bead: Pick a complementary bead (e.g. 10 Mukhi Navagraha shield or 11 Mukhi Hanuman bead)
        secondary_mukhi = 10 if primary_mukhi != 10 else 11
        secondary_bead = RudrakshaItem(**RUDRAKSHA_REGISTRY[secondary_mukhi])

        instructions_en = [
            "Consecrate before wearing: Immerse in raw cow's milk and Gangajal for 1 hour; apply sandalwood paste and offer fresh flowers.",
            "Recite 108 times the Shiva Panchakshari Mantra: 'Om Namah Shivaya' while holding the bead in your right hand.",
            "Wear strung in pure red, yellow, or white silk thread, capped in pure silver, gold, or copper.",
            "Remove during funeral ceremonies or intimate marital relations, and place respectfully at your home altar.",
            "Rudraksha beads have electromagnetic and bio-physical calming properties; they can be safely worn alongside prescribed Anukula gemstones.",
        ]
        instructions_ta = [
            "அணிவதற்கு முன் சுத்திகரிப்பு: பசும்பால் மற்றும் கங்கை நீரில் 1 மணி நேரம் வைத்து, சந்தனம் பூசி மலர்களால் அர்ச்சிக்கவும்.",
            "வலது கையில் ருத்ராட்சத்தை ஏந்தி 108 முறை 'ஓம் நம சிவாய' மந்திரம் ஜெபிக்கவும்.",
            "தூய வெள்ளி, தங்கம் அல்லது செம்பில் கட்டி, சிவப்பு அல்லது மஞ்சள் பட்டு நூலில் அணியவும்.",
            "மரண வீடுகள் மற்றும் தீட்டு காலங்களில் கழற்றி வீட்டு பூஜை அறையில் வைக்கவும்.",
            "ருத்ராட்சம் உடலின் மின்காந்த அலைகளை சமநிலைப்படுத்தும்; இதனை பரிந்துரைக்கப்பட்ட சுப ரத்தினங்களுடன் சேர்த்தும் அணியலாம்.",
        ]

        return RudrakshaRecommendationSummary(
            primary_bead=primary_bead,
            secondary_bead=secondary_bead,
            universal_bead=universal_bead,
            personal_alignment_reason_en=primary_reason_en,
            personal_alignment_reason_ta=primary_reason_ta,
            wearing_instructions_en=instructions_en,
            wearing_instructions_ta=instructions_ta,
        )
