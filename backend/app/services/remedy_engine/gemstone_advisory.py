"""Astrological Gemstone (Ratna) Advisory & Classical Safety Engine.

Implements authentic Ratna Shastra based on classical canons:
- Brihat Samhita (Ch. 80-83 - Ratna Pariksha)
- Jataka Parijata (Ch. 2)
- Mani Mala (Raja Radhakanta Deb)
- Bhavartha Ratnakara
- Garuda Purana (Preta Khanda & Brahma Khanda)

Features:
- Anukula Vada (Benefic Strengthening) vs Pratikula Shanti (Malefic Pacification)
- 3 Pillars of Auspicious Gemology:
    1. Jeevan Ratna (Life Stone) - Lagna Lord (Health, Vitality, Longevity)
    2. Punya Ratna (Lucky Stone) - 5th Lord (Intellect, Education, Punya)
    3. Bhagya Ratna (Fortune Stone) - 9th Lord (Luck, Prosperity, Divine Grace)
- Secondary Support Stone: Authentic Yogakaraka (Taurus, Cancer, Leo, Libra, Capricorn, Aquarius) or Dasha Lord
- Dynamic weight calculation based on Native's Body Weight (1 Ratti per 10 kg body weight)
- Complete 9 Grahas including Rahu (Gomed) and Ketu (Vaiduryam)
- Affordable Uparatna (Semi-precious substitutes)
- Auspicious metals, wearing fingers, minimum carat & ratti weights, consecration & Gayatri mantras
- Classical Red-Flag Prohibitions (Dusthana 6th/8th/12th lords, Maraka/Badhaka)
- Enemy Gem Conflict Guard (prevents wearing adversarial stones together)
- Integrated 1-to-14 Mukhi Rudraksha compatibility matrix for safe Pratikula pacification
"""

from typing import List, Dict, Any, Optional
from app.schemas.remedies import (
    GemstoneRecommendation,
    ProhibitedGemstoneItem,
    GemstoneAdvisoryResponse,
    RudrakshaItem,
    RudrakshaRecommendationSummary,
)
from app.services.remedy_engine.rudraksha_advisory import (
    RudrakshaAdvisoryEngine,
    RUDRAKSHA_REGISTRY,
)

PLANET_GEMSTONE_DATA: Dict[str, Dict[str, Any]] = {
    "sun": {
        "graha_name_en": "Sun (Surya)",
        "graha_name_ta": "சூரியன்",
        "primary_gem_en": "Natural Ruby (Manikyam)",
        "primary_gem_ta": "இயற்கை மாணிக்கம்",
        "primary_gem_sanskrit": "माणिक्यम् (Māṇikyam)",
        "upratna_substitutes_en": ["Red Garnet", "Spinel", "Red Tourmaline (Rubellite)"],
        "upratna_substitutes_ta": ["சிவப்பு கார்னெட்", "ஸ்பைனல்", "ரூபலைட்"],
        "prescribed_metal_en": "22K Yellow Gold or Pure Copper",
        "prescribed_metal_ta": "22 காரட் தங்கம் அல்லது சுத்தமான செம்பு",
        "ideal_finger_en": "Ring Finger (Right Hand)",
        "ideal_finger_ta": "மோதிர விரல் (வலது கை)",
        "minimum_carats": 3.25,
        "minimum_rattis": 3.5,
        "energization_day_en": "Sunday morning during Shukla Paksha (Sunrise or Surya Hora)",
        "energization_day_ta": "வளர்பிறை ஞாயிற்றுக்கிழமை காலை (சூரிய உதயம் அல்லது சூரிய ஓரை)",
        "consecration_mantra_sanskrit": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः (Om Hraam Hreem Hroum Sah Sooryaaya Namah)",
        "consecration_mantra_ta": "ஓம் ஹ்ராம் ஹ்ரீம் ஹ்ரௌம் ஸஹ சூர்யாய நமஹ",
        "gayatri_mantra_sanskrit": "ॐ भास्कराय विद्महे महाद्युतिकराय धीमहि तन्नो आदित्यः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் பாஸ்கராய வித்மஹே மஹத்யுதிகராய தீமஹி தந்நோ ஆதித்யஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Immerse in Gangajal, raw cow's milk, and honey for 45 minutes; wash with fresh water and recite 108 Surya Moola Mantras.",
        "cleansing_vidhi_ta": "கங்கை நீர், பசும்பால், தேன் கலவையில் 45 நிமிடங்கள் வைத்து, தூய நீரால் கழுவி 108 முறை சூரிய மூல மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["saturn", "venus", "rahu", "ketu"],
        "incompatible_gems_warning_en": "NEVER wear Ruby with Blue Sapphire, Diamond, Hessonite (Gomed), or Cat's Eye.",
        "incompatible_gems_warning_ta": "மாணிக்கத்தை நீலம், வைரம், கோமேதகம், அல்லது வைடூரியத்துடன் சேர்த்து அணியக் கூடாது.",
    },
    "moon": {
        "graha_name_en": "Moon (Chandra)",
        "graha_name_ta": "சந்திரன்",
        "primary_gem_en": "Natural South Sea Pearl (Mukta / Moti)",
        "primary_gem_ta": "இயற்கை முத்து",
        "primary_gem_sanskrit": "मुक्ताफलम् (Muktāphalam)",
        "upratna_substitutes_en": ["Natural Moonstone", "White Coral"],
        "upratna_substitutes_ta": ["நிலாக்கற்கள் (மூன்ஸ்டோன்)", "வெள்ளை பவழம்"],
        "prescribed_metal_en": "Pure Sterling Silver (925) or White Gold",
        "prescribed_metal_ta": "சுத்தமான வெள்ளி அல்லது வெள்ளை தங்கம்",
        "ideal_finger_en": "Little Finger (Right Hand)",
        "ideal_finger_ta": "சுண்டு விரல் (வலது கை)",
        "minimum_carats": 4.5,
        "minimum_rattis": 5.0,
        "energization_day_en": "Monday evening during Shukla Paksha or Purnima (Chandra Hora)",
        "energization_day_ta": "வளர்பிறை திங்கட்கிழமை மாலை அல்லது பௌர்ணமி (சந்திர ஓரை)",
        "consecration_mantra_sanskrit": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः (Om Shraam Shreem Shroum Sah Chandramase Namah)",
        "consecration_mantra_ta": "ஓம் ச்ராம் ச்ரீம் ச்ரௌம் ஸஹ சந்திரமஸே நமஹ",
        "gayatri_mantra_sanskrit": "ॐ क्षीरपुत्राय विद्महे अमृतत्त्वाय धीमहि तन्नो चन्द्रः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் க்ஷீரபுத்ராய வித்மஹே அம்ருதத்த்வாய தீமஹி தந்நோ சந்த்ரஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Purify in raw cow's milk and Gangajal; place under direct moonlight for 1 hour; recite 108 Chandra Mantras.",
        "cleansing_vidhi_ta": "பசும்பால் மற்றும் கங்கை நீரில் தூய்மை செய்து, நிலவொளியில் 1 மணி நேரம் வைத்து 108 முறை சந்திர மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["rahu", "ketu"],
        "incompatible_gems_warning_en": "NEVER wear Pearl with Hessonite (Gomed) or Cat's Eye (Vaidooryam).",
        "incompatible_gems_warning_ta": "முத்தை கோமேதகம் அல்லது வைடூரியத்துடன் ஒருபோதும் இணைக்கக் கூடாது.",
    },
    "mars": {
        "graha_name_en": "Mars (Chevvai / Mangal)",
        "graha_name_ta": "செவ்வாய்",
        "primary_gem_en": "Natural Red Coral (Moonga / Pavazham)",
        "primary_gem_ta": "இயற்கை செம்பவழம்",
        "primary_gem_sanskrit": "प्रवालम् (Pravālam)",
        "upratna_substitutes_en": ["Red Carnelian", "Red Agate"],
        "upratna_substitutes_ta": ["சிவப்பு கார்னிலியன்", "சிவப்பு அகேட்"],
        "prescribed_metal_en": "Gold, Copper, or Panchadhatu",
        "prescribed_metal_ta": "தங்கம், செம்பு அல்லது பஞ்சலோகம்",
        "ideal_finger_en": "Ring Finger (Right Hand)",
        "ideal_finger_ta": "மோதிர விரல் (வலது கை)",
        "minimum_carats": 5.25,
        "minimum_rattis": 6.0,
        "energization_day_en": "Tuesday morning during Shukla Paksha (Mars Hora)",
        "energization_day_ta": "வளர்பிறை செவ்வாய்க்கிழமை காலை (செவ்வாய் ஓரை)",
        "consecration_mantra_sanskrit": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः (Om Kraam Kreem Kroum Sah Bhoumaaya Namah)",
        "consecration_mantra_ta": "ஓம் க்ராம் க்ரீம் க்ரௌம் ஸஹ பௌமாய நமஹ",
        "gayatri_mantra_sanskrit": "ॐ अङ्गारकाय विद्महे शक्तिहस्ताय धीमहि तन्नो भौमः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் அங்காரகாய வித்மஹே சக்திஹஸ்தாய தீமஹி தந்நோ பௌமஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Immerse in holy water mixed with kumkum and raw milk; chant 108 Angaraka Moola Mantras.",
        "cleansing_vidhi_ta": "குங்குமம் கலந்த கங்கை நீர் மற்றும் பசும்பாலில் வைத்து 108 முறை அங்காரக மூல மந்திரம் ஜெபித்து அணிதல்.",
        "enemy_planets": ["mercury", "saturn", "rahu"],
        "incompatible_gems_warning_en": "NEVER wear Red Coral with Emerald or Blue Sapphire.",
        "incompatible_gems_warning_ta": "செம்பவழத்தை மரகதம் அல்லது நீலக்கல்லுடன் ஒருபோதும் சேர்த்து அணியக் கூடாது.",
    },
    "mercury": {
        "graha_name_en": "Mercury (Budhan)",
        "graha_name_ta": "புதன்",
        "primary_gem_en": "Natural Emerald (Panna / Marakatham)",
        "primary_gem_ta": "இயற்கை மரகதம்",
        "primary_gem_sanskrit": "मरकतम् (Marakatam)",
        "upratna_substitutes_en": ["Green Tourmaline (Verdelite)", "Peridot", "Green Jade"],
        "upratna_substitutes_ta": ["பச்சை டூர்மலைன்", "பெரிடோட்", "பச்சை ஜேட்"],
        "prescribed_metal_en": "Gold or Silver",
        "prescribed_metal_ta": "தங்கம் அல்லது வெள்ளி",
        "ideal_finger_en": "Little Finger (Right Hand)",
        "ideal_finger_ta": "சுண்டு விரல் (வலது கை)",
        "minimum_carats": 3.25,
        "minimum_rattis": 3.5,
        "energization_day_en": "Wednesday morning during Shukla Paksha (Budha Hora)",
        "energization_day_ta": "வளர்பிறை புதன்கிழமை காலை (புதன் ஓரை)",
        "consecration_mantra_sanskrit": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (Om Braam Breem Broum Sah Budhaaya Namah)",
        "consecration_mantra_ta": "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ புதாய நமஹ",
        "gayatri_mantra_sanskrit": "ॐ सौम्यरूपाय विद्महे वाणेशाय धीमहि तन्नो सौम्यः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் ஸௌம்யரூபாய வித்மஹே வாணேசாய தீமஹி தந்நோ ஸௌம்யஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Wash with unboiled cow's milk and Gangajal; place on fresh tulasi leaves; chant 108 Budha Mantras.",
        "cleansing_vidhi_ta": "பசும்பால் மற்றும் கங்கை நீரால் கழுவி, துளசி இலைகள் மீது வைத்து 108 முறை புதன் மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["moon", "mars"],
        "incompatible_gems_warning_en": "NEVER wear Emerald with Pearl or Red Coral.",
        "incompatible_gems_warning_ta": "மரகதத்தை முத்து அல்லது செம்பவழத்துடன் சேர்த்து அணியக் கூடாது.",
    },
    "jupiter": {
        "graha_name_en": "Jupiter (Guru / Brihaspati)",
        "graha_name_ta": "குரு",
        "primary_gem_en": "Natural Yellow Sapphire (Pukhraj / Pushparagam)",
        "primary_gem_ta": "இயற்கை மஞ்சள் புஷ்பராகம்",
        "primary_gem_sanskrit": "पुष्परागम् (Puṣparāgam)",
        "upratna_substitutes_en": ["Natural Yellow Topaz", "Citrine (Sunela)", "Heliodor"],
        "upratna_substitutes_ta": ["மஞ்சள் டோபாஸ்", "சிட்ரின் (சுனேலா)", "ஹெலியோடார்"],
        "prescribed_metal_en": "22K Solid Yellow Gold",
        "prescribed_metal_ta": "22 காரட் சுத்தமான தங்கம்",
        "ideal_finger_en": "Index Finger (Tarjani - Right Hand)",
        "ideal_finger_ta": "ஆள்காட்டி விரல் (வலது கை)",
        "minimum_carats": 3.75,
        "minimum_rattis": 4.0,
        "energization_day_en": "Thursday morning during Shukla Paksha (Sunrise or Guru Hora)",
        "energization_day_ta": "வளர்பிறை வியாழக்கிழமை காலை (சூரிய உதயம் அல்லது குரு ஓரை)",
        "consecration_mantra_sanskrit": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (Om Graam Greem Groum Sah Gurave Namah)",
        "consecration_mantra_ta": "ஓம் க்ராம் க்ரீம் க்ரௌம் ஸஹ குரவே நமஹ",
        "gayatri_mantra_sanskrit": "ॐ गुरुदेवाय विद्महे परब्रह्माय धीमहि तन्नो गुरुः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் குருதேவாய வித்மஹே பரப்ரஹ்மாய தீமஹி தந்நோ குருஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Dip in raw cow's milk, turmeric water, and honey; offer yellow flowers; chant 108 Guru Moola Mantras.",
        "cleansing_vidhi_ta": "பசும்பால், மஞ்சள் நீர், தேனில் வைத்து, மஞ்சள் மலர்களால் அர்ச்சித்து 108 முறை குரு மூல மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["venus", "mercury"],
        "incompatible_gems_warning_en": "NEVER wear Yellow Sapphire with Diamond or Emerald.",
        "incompatible_gems_warning_ta": "புஷ்பராகத்தை வைரம் அல்லது மரகதத்துடன் ஒருபோதும் இணைக்கக் கூடாது.",
    },
    "venus": {
        "graha_name_en": "Venus (Sukran)",
        "graha_name_ta": "சுக்கிரன்",
        "primary_gem_en": "Natural Diamond (Heera / Vairam)",
        "primary_gem_ta": "இயற்கை வைரம்",
        "primary_gem_sanskrit": "वज्रम् (Vajram / Hīrakam)",
        "upratna_substitutes_en": ["White Zircon", "White Sapphire", "Goshenite"],
        "upratna_substitutes_ta": ["வெள்ளை ஜிர்கான்", "வெள்ளை புஷ்பராகம்", "கோஷனைட்"],
        "prescribed_metal_en": "Platinum, White Gold, or Silver",
        "prescribed_metal_ta": "பிளாட்டினம், வெள்ளை தங்கம் அல்லது வெள்ளி",
        "ideal_finger_en": "Middle Finger or Little Finger (Right Hand)",
        "ideal_finger_ta": "நடுவிரல் அல்லது சுண்டு விரல் (வலது கை)",
        "minimum_carats": 0.50,
        "minimum_rattis": 0.6,
        "energization_day_en": "Friday sunrise or evening during Shukla Paksha (Sukra Hora)",
        "energization_day_ta": "வளர்பிறை வெள்ளிக்கிழமை காலை அல்லது மாலை (சுக்கிர ஓரை)",
        "consecration_mantra_sanskrit": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (Om Draam Dreem Droum Sah Shukraaya Namah)",
        "consecration_mantra_ta": "ஓம் த்ராம் த்ரீம் த்ரௌம் ஸஹ சுக்ராய நமஹ",
        "gayatri_mantra_sanskrit": "ॐ भृगुपुत्राय विद्महे दिव्यदेहाय धीमहि तन्नो शुक्रः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் ப்ருகுபுத்ராய வித்மஹே திவ்யதேஹாய தீமஹி தந்நோ சுக்ரஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Immerse in Gangajal, sandalwood paste water, and raw milk; chant 108 Sukra Mantras.",
        "cleansing_vidhi_ta": "கங்கை நீர், சந்தனம் கலந்த நீர், பசும்பாலில் வைத்து 108 முறை சுக்கிர மூல மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["sun", "moon", "jupiter"],
        "incompatible_gems_warning_en": "NEVER wear Diamond with Ruby, Pearl, or Yellow Sapphire.",
        "incompatible_gems_warning_ta": "வைரத்தை மாணிக்கம், முத்து அல்லது மஞ்சள் புஷ்பராகத்துடன் சேர்த்து அணியக் கூடாது.",
    },
    "saturn": {
        "graha_name_en": "Saturn (Saneeswara)",
        "graha_name_ta": "சனி",
        "primary_gem_en": "Natural Blue Sapphire (Neelam / Indraneelam)",
        "primary_gem_ta": "இயற்கை இந்திரநீலம் (நீலக்கல்)",
        "primary_gem_sanskrit": "नीलमणिः (Nīlamaṇiḥ)",
        "upratna_substitutes_en": ["Natural Amethyst (Katela)", "Iolite (Neeli)", "Blue Topaz"],
        "upratna_substitutes_ta": ["அமேதிஸ்ட் (கத்தேலா)", "அயோலைட் (நீலி)", "ப்ளூ டோபாஸ்"],
        "prescribed_metal_en": "Sterling Silver or Panchadhatu",
        "prescribed_metal_ta": "சுத்தமான வெள்ளி அல்லது பஞ்சலோகம்",
        "ideal_finger_en": "Middle Finger (Right Hand)",
        "ideal_finger_ta": "நடுவிரல் (மத்திய விரல் - வலது கை)",
        "minimum_carats": 4.25,
        "minimum_rattis": 4.5,
        "energization_day_en": "Saturday twilight or night during Shukla Paksha (Shani Hora)",
        "energization_day_ta": "வளர்பிறை சனிக்கிழமை மாலை அல்லது இரவு (சனி ஓரை)",
        "consecration_mantra_sanskrit": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (Om Praam Preem Proum Sah Shanaishcharaaya Namah)",
        "consecration_mantra_ta": "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ சனைச்சராய நமஹ",
        "gayatri_mantra_sanskrit": "ॐ सूर्यपुत्राय विद्महे मन्दचेष्टाय धीमहि तन्नो सौरिः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் சூர்யபுத்ராய வித்மஹே மந்தசேஷ்டாய தீமஹி தந்நோ ஸௌரிஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Mandatory 3-day trial under pillow first. If safe, wash in Gangajal and raw milk with black sesame seeds; chant 108 Shani Mantras.",
        "cleansing_vidhi_ta": "3 நாட்கள் தலையணையின் கீழ் வைத்து பரிசோதனை செய்தல் கட்டாயம். பின் கங்கை நீர், பசும்பாலில் எள் சேர்த்து தூய்மை செய்து 108 முறை சனி மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["sun", "moon", "mars"],
        "incompatible_gems_warning_en": "NEVER wear Blue Sapphire with Ruby, Pearl, or Red Coral.",
        "incompatible_gems_warning_ta": "நீலக்கல்லை மாணிக்கம், முத்து அல்லது செம்பவழத்துடன் ஒருபோதும் இணைக்கக் கூடாது.",
    },
    "rahu": {
        "graha_name_en": "Rahu (North Node)",
        "graha_name_ta": "ராகு பகவான்",
        "primary_gem_en": "Natural Hessonite Garnet (Gomed / Gomedhaka)",
        "primary_gem_ta": "இயற்கை கோமேதகம்",
        "primary_gem_sanskrit": "गोमेदः (Gomedaḥ)",
        "upratna_substitutes_en": ["Orange Spessartite Garnet", "Honey Agate", "Brown Zircon"],
        "upratna_substitutes_ta": ["ஸ்பெஸ்ஸார்டைட் கார்னெட்", "தேன் அகேட்", "பழுப்பு ஜிர்கான்"],
        "prescribed_metal_en": "Sterling Silver or Ashtadhatu",
        "prescribed_metal_ta": "சுத்தமான வெள்ளி அல்லது அஷ்டதாது",
        "ideal_finger_en": "Middle Finger (Right Hand)",
        "ideal_finger_ta": "நடுவிரல் (வலது கை)",
        "minimum_carats": 4.5,
        "minimum_rattis": 5.0,
        "energization_day_en": "Saturday twilight or Wednesday night during Rahu Kaal (Shukla Paksha)",
        "energization_day_ta": "வளர்பிறை சனிக்கிழமை அந்தி வேளை அல்லது புதன்கிழமை ராகு காலம்",
        "consecration_mantra_sanskrit": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (Om Bhraam Bhreem Bhroum Sah Rahave Namah)",
        "consecration_mantra_ta": "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ ராகவே நமஹ",
        "gayatri_mantra_sanskrit": "ॐ नागाध्वजाय विद्महे पद्म हस्ताय धीमहि तन्नो राहुः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் நாகத்வஜாய வித்மஹே பத்ம ஹஸ்தாய தீமஹி தந்நோ ராகுஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Mandatory 3-day pillow test. Purify in Gangajal and raw cow milk for 45 minutes; place on blue cloth and chant 108 Rahu Mantras.",
        "cleansing_vidhi_ta": "3 நாட்கள் தலையணையின் கீழ் வைத்து பரிசோதனை செய்தல் கட்டாயம். கங்கை நீர் மற்றும் பசும்பாலில் 45 நிமிடங்கள் வைத்து 108 முறை ராகு மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["sun", "moon", "mars", "jupiter"],
        "incompatible_gems_warning_en": "NEVER wear Hessonite with Ruby, Pearl, Red Coral, or Yellow Sapphire.",
        "incompatible_gems_warning_ta": "கோமேதகத்தை மாணிக்கம், முத்து, செம்பவழம் அல்லது மஞ்சள் புஷ்பராகத்துடன் ஒருபோதும் இணைக்கக் கூடாது.",
    },
    "ketu": {
        "graha_name_en": "Ketu (South Node)",
        "graha_name_ta": "கேது பகவான்",
        "primary_gem_en": "Natural Chrysoberyl Cat's Eye (Vaiduryam / Lehsunia)",
        "primary_gem_ta": "இயற்கை வைடூரியம் (கேது ரத்தினம்)",
        "primary_gem_sanskrit": "वैदूर्यम् (Vaidūryam)",
        "upratna_substitutes_en": ["Fibrolite Cat's Eye", "Apatite Cat's Eye", "Tourmaline Cat's Eye"],
        "upratna_substitutes_ta": ["ஃபைப்ரோலைட் வைடூரியம்", "அபடைட் கேட்ஸ் ஐ", "டூர்மலைன் கேட்ஸ் ஐ"],
        "prescribed_metal_en": "Pure 22K Gold, Silver, or Panchadhatu",
        "prescribed_metal_ta": "22 காரட் தங்கம், வெள்ளி அல்லது பஞ்சலோகம்",
        "ideal_finger_en": "Middle Finger or Little Finger (Right Hand)",
        "ideal_finger_ta": "நடுவிரல் அல்லது சுண்டு விரல் (வலது கை)",
        "minimum_carats": 3.5,
        "minimum_rattis": 4.0,
        "energization_day_en": "Tuesday midnight or Thursday morning during Ketu/Mars Hora (Shukla Paksha)",
        "energization_day_ta": "வளர்பிறை செவ்வாய்க்கிழமை அல்லது வியாழக்கிழமை கேது/செவ்வாய் ஓரை",
        "consecration_mantra_sanskrit": "ॐ स्रां स्रीं स्रौं सः केतवे नमः (Om Sraam Sreem Sroum Sah Ketave Namah)",
        "consecration_mantra_ta": "ஓம் ஸ்ராம் ஸ்ரீம் ஸ்ரௌம் ஸஹ கேதவே நமஹ",
        "gayatri_mantra_sanskrit": "ॐ अश्वाध्वजाय विद्महे शूल हस्ताय धीमहि तन्नो केतुः प्रचोदयात्",
        "gayatri_mantra_ta": "ஓம் அஸ்வத்வஜாய வித்மஹே சூல ஹஸ்தாய தீமஹி தந்நோ கேதுஹ் ப்ரசோதயாத்",
        "cleansing_vidhi_en": "Purify in Gangajal and raw milk with sacred Vibhuti; chant 108 Ketu Moola Mantras.",
        "cleansing_vidhi_ta": "விபூதி கலந்த கங்கை நீர் மற்றும் பசும்பாலில் வைத்து தூய்மை செய்து 108 முறை கேது மூல மந்திரம் ஜெபித்தல்.",
        "enemy_planets": ["sun", "moon", "mars"],
        "incompatible_gems_warning_en": "NEVER wear Cat's Eye with Ruby, Pearl, or Red Coral.",
        "incompatible_gems_warning_ta": "வைடூரியத்தை மாணிக்கம், முத்து அல்லது செம்பவழத்துடன் ஒருபோதும் இணைக்கக் கூடாது.",
    },
}

# Sign lordship definitions
SIGN_LORDS: Dict[str, str] = {
    "Aries": "mars", "Taurus": "venus", "Gemini": "mercury", "Cancer": "moon",
    "Leo": "sun", "Virgo": "mercury", "Libra": "venus", "Scorpio": "mars",
    "Sagittarius": "jupiter", "Capricorn": "saturn", "Aquarius": "saturn", "Pisces": "jupiter",
}

# 12 Sign House Rulers (House 1 to 12)
SIGN_ORDER = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Classical Yogakaraka definitions (single planet ruling both a Kendra 4,7,10 and Trikona 5,9)
YOGAKARAKA_BY_LAGNA: Dict[str, Dict[str, Any]] = {
    "Taurus": {
        "graha": "saturn",
        "houses": [9, 10],
        "reason_en": "Saturn is the supreme Yogakaraka ruling the 9th Trikona (Bhagya) and 10th Kendra (Karma).",
        "reason_ta": "சனி பகவான் 9-ஆம் திரிகோணம் மற்றும் 10-ஆம் கேந்திரத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
    "Cancer": {
        "graha": "mars",
        "houses": [5, 10],
        "reason_en": "Mars is the supreme Yogakaraka ruling the 5th Trikona (Punya) and 10th Kendra (Karma).",
        "reason_ta": "செவ்வாய் பகவான் 5-ஆம் திரிகோணம் மற்றும் 10-ஆம் கேந்திரத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
    "Leo": {
        "graha": "mars",
        "houses": [4, 9],
        "reason_en": "Mars is the supreme Yogakaraka ruling the 4th Kendra (Sukha) and 9th Trikona (Bhagya).",
        "reason_ta": "செவ்வாய் பகவான் 4-ஆம் கேந்திரம் மற்றும் 9-ஆம் திரிகோணத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
    "Libra": {
        "graha": "saturn",
        "houses": [4, 5],
        "reason_en": "Saturn is the supreme Yogakaraka ruling the 4th Kendra (Sukha) and 5th Trikona (Punya).",
        "reason_ta": "சனி பகவான் 4-ஆம் கேந்திரம் மற்றும் 5-ஆம் திரிகோணத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
    "Capricorn": {
        "graha": "venus",
        "houses": [5, 10],
        "reason_en": "Venus is the supreme Yogakaraka ruling the 5th Trikona (Punya) and 10th Kendra (Karma).",
        "reason_ta": "சுக்கிர பகவான் 5-ஆம் திரிகோணம் மற்றும் 10-ஆம் கேந்திரத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
    "Aquarius": {
        "graha": "venus",
        "houses": [4, 9],
        "reason_en": "Venus is the supreme Yogakaraka ruling the 4th Kendra (Sukha) and 9th Trikona (Bhagya).",
        "reason_ta": "சுக்கிர பகவான் 4-ஆம் கேந்திரம் மற்றும் 9-ஆம் திரிகோணத்தை ஆட்சி செய்து பூரண யோககாரகனாக விளங்குகிறார்.",
    },
}


class GemstoneAdvisoryEngine:
    """Evaluates 3-pillar gemstone recommendations, secondary support, and classical prohibitions."""

    @classmethod
    def get_house_lord(cls, lagna_sign: str, house_num: int) -> str:
        """Returns the planet ruling house_num (1-12) from lagna_sign."""
        idx = SIGN_ORDER.index(lagna_sign)
        target_sign = SIGN_ORDER[(idx + house_num - 1) % 12]
        return SIGN_LORDS[target_sign]

    @classmethod
    def get_houses_ruled_by_planet(cls, lagna_sign: str, planet: str) -> List[int]:
        """Returns all houses (1-12) ruled by a planet for a given Lagna."""
        houses: List[int] = []
        for h in range(1, 13):
            if cls.get_house_lord(lagna_sign, h) == planet:
                houses.append(h)
        return houses

    @classmethod
    def evaluate_advisory(
        cls,
        lagna_sign: str,
        moon_sign: Optional[str] = None,
        running_mahadasha: Optional[str] = None,
        running_bhukti: Optional[str] = None,
        body_weight_kg: Optional[float] = None,
        debilitated_planets: Optional[List[str]] = None,
        combust_planets: Optional[List[str]] = None,
        has_kuja_dosha: bool = False,
        has_sade_sati: bool = False,
        has_kaal_sarp: bool = False,
    ) -> GemstoneAdvisoryResponse:
        """Generates the full 3-pillar gemstone prescription, secondary support, and strict prohibition matrix."""
        # 1. Determine Lords for 1st, 5th, and 9th houses
        lagna_lord = cls.get_house_lord(lagna_sign, 1)
        fifth_lord = cls.get_house_lord(lagna_sign, 5)
        ninth_lord = cls.get_house_lord(lagna_sign, 9)

        life_rec = cls._build_recommendation(
            category_code="life_stone",
            category_name_en="Life Stone (Jeevan Ratna)",
            category_name_ta="உயிர் ரத்தினம் (ஜீவன் ரத்னம்)",
            governing_purpose_en="Lagna Lord Gemstone: Enhances overall physical vitality, immune resistance, self-confidence, longevity, and aura protection.",
            governing_purpose_ta="லக்னாதிபதி ரத்தினம்: உடல் ஆரோக்கியம், நோய் எதிர்ப்பு சக்தி, தன்னம்பிக்கை, ஆயுள் பலம் மற்றும் தேஜஸை மேம்படுத்துகிறது.",
            lagna_sign=lagna_sign,
            graha=lagna_lord,
            body_weight_kg=body_weight_kg,
        )

        lucky_rec = cls._build_recommendation(
            category_code="lucky_stone",
            category_name_en="Lucky Stone (Punya Ratna)",
            category_name_ta="புண்ணிய ரத்தினம் (பூர்வ புண்ணியம்)",
            governing_purpose_en="5th Lord Gemstone: Amplifies intellect, memory, academic acumen, intuition, progeny blessings, and past karmic merit.",
            governing_purpose_ta="5-ஆம் அதிபதி ரத்தினம்: அறிவுத் திறன், நினைவாற்றல், கல்வி மேன்மை, உள்ளுணர்வு, புத்திர பாக்கியம் மற்றும் பூர்வ புண்ணிய பலன்களைத் தூண்டுகிறது.",
            lagna_sign=lagna_sign,
            graha=fifth_lord,
            body_weight_kg=body_weight_kg,
        )

        fortune_rec = cls._build_recommendation(
            category_code="fortune_stone",
            category_name_en="Fortune Stone (Bhagya Ratna)",
            category_name_ta="பாக்கிய ரத்தினம் (பாக்கிய ஸ்தானம்)",
            governing_purpose_en="9th Lord Gemstone: Magnetizes divine grace, career fortune, financial prosperity, father's well-being, and righteous luck.",
            governing_purpose_ta="9-ஆம் அதிபதி ரத்தினம்: தெய்வ அருள், தொழில் அதிர்ஷ்டம், தன வரவு, தந்தை நலம் மற்றும் பாக்கிய யோகங்களை ஈர்க்கிறது.",
            lagna_sign=lagna_sign,
            graha=ninth_lord,
            body_weight_kg=body_weight_kg,
        )

        # 2. Secondary Support Stone (Yogakaraka or Functional Benefic Dasha Lord)
        secondary_rec: Optional[GemstoneRecommendation] = None
        primary_grahas = {lagna_lord, fifth_lord, ninth_lord}

        if lagna_sign in YOGAKARAKA_BY_LAGNA:
            yk_info = YOGAKARAKA_BY_LAGNA[lagna_sign]
            yk_graha = yk_info["graha"]
            if yk_graha not in primary_grahas:
                secondary_rec = cls._build_recommendation(
                    category_code="secondary_support",
                    category_name_en="Secondary Support Stone (Yogakaraka)",
                    category_name_ta="இரண்டாம் நிலை ஆதரவு ரத்தினம் (யோககாரகன்)",
                    governing_purpose_en=f"Yogakaraka Gemstone: Simultaneously activates Kendra power and Trikona fortune. {yk_info['reason_en']}",
                    governing_purpose_ta=f"யோககாரக ரத்தினம்: கேந்திர மற்றும் திரிகோண அதிர்ஷ்டத்தை ஒருங்கே தூண்டுகிறது. {yk_info['reason_ta']}",
                    lagna_sign=lagna_sign,
                    graha=yk_graha,
                    body_weight_kg=body_weight_kg,
                )
        elif running_mahadasha:
            dasha_clean = running_mahadasha.lower()
            if dasha_clean in PLANET_GEMSTONE_DATA and dasha_clean not in primary_grahas:
                d_houses = cls.get_houses_ruled_by_planet(lagna_sign, dasha_clean)
                has_dusthana = any(h in (6, 8, 12) for h in d_houses)
                has_kendra_trikona = any(h in (1, 4, 5, 7, 9, 10) for h in d_houses)
                if has_kendra_trikona and not has_dusthana:
                    secondary_rec = cls._build_recommendation(
                        category_code="secondary_support",
                        category_name_en=f"Secondary Support Stone ({running_mahadasha} Dasha Lord)",
                        category_name_ta=f"இரண்டாம் நிலை ஆதரவு ரத்தினம் ({running_mahadasha} தசா நாதன்)",
                        governing_purpose_en=f"Empowers the running Mahadasha period to manifest optimal professional and financial fruits.",
                        governing_purpose_ta=f"தற்போது நடைபெறும் {running_mahadasha} தசையின் சுப பலன்களை முழுமையாக ஈர்க்கிறது.",
                        lagna_sign=lagna_sign,
                        graha=dasha_clean,
                        body_weight_kg=body_weight_kg,
                    )

        # 3. Determine Prohibited Gemstones (Dusthana 6, 8, 12 rulers & Functional Malefics)
        prohibited_items: List[ProhibitedGemstoneItem] = []
        auspicious_planets = {lagna_lord, fifth_lord, ninth_lord}
        if secondary_rec:
            auspicious_planets.add(secondary_rec.graha)

        for p_name, p_data in PLANET_GEMSTONE_DATA.items():
            if p_name in auspicious_planets and p_name != lagna_lord:
                continue

            ruled = cls.get_houses_ruled_by_planet(lagna_sign, p_name)
            dusthana_rules = [h for h in ruled if h in (6, 8, 12)]

            # If rules dusthana and is NOT the Lagna lord
            if dusthana_rules and p_name != lagna_lord:
                houses_str = ", ".join(f"{h}th" for h in dusthana_rules)
                prohibited_items.append(
                    ProhibitedGemstoneItem(
                        graha=p_name,
                        graha_name_en=p_data["graha_name_en"],
                        graha_name_ta=p_data["graha_name_ta"],
                        primary_gem_en=p_data["primary_gem_en"],
                        primary_gem_ta=p_data["primary_gem_ta"],
                        reason_en=(
                            f"Rules Dusthana houses ({houses_str}) for {lagna_sign} Lagna. "
                            "Wearing this gemstone directly strengthens malefic vibrations, aggravating debts, litigation, surgeries, illnesses, and financial setbacks."
                        ),
                        reason_ta=(
                            f"{lagna_sign} லக்னத்திற்கு {houses_str} போன்ற மறைவு ஸ்தானங்களின் அதிபதி. "
                            "இந்த ரத்தினத்தை அணிவது கடன், நோய், வழக்கு மற்றும் விபத்து போன்ற பாதகங்களை தீவிரப்படுத்தும்."
                        ),
                        dusthana_houses_ruled=dusthana_rules,
                        is_functional_malefic=True,
                        safe_alternative_en=f"Pacify {p_data['graha_name_en']} via Moola Mantra recitation, Rudraksha bead, Kaveri Delta temple archana, or sattvic charity.",
                        safe_alternative_ta=f"{p_data['graha_name_ta']} பகவானை மூல மந்திர ஜெபம், உகந்த ருத்ராட்சம், நவக்கிரக கோவில் அர்ச்சனை மற்றும் எளிய தானங்கள் மூலம் அமைதிப்படுத்தவும்.",
                    )
                )

        # 4. Anukula vs Pratikula Doctrine Matrix
        anukula_doctrine_en = {
            "title": "Anukula (Benefic Strengthening) vs Pratikula (Malefic Pacification)",
            "authority": "Brihat Samhita (Ch. 80), Garuda Purana, Mani Mala (Raja Radhakanta Deb)",
            "core_principle": (
                "Gemstones act as cosmic crystalline prisms that capture and transmit planetary radiation into the wearer's bio-magnetic aura. "
                "They ALWAYS magnify the planet's energy. Therefore, under classical 'Anukula Vada', gems are strictly prescribed ONLY for functional "
                "benefics (Lagna, 5th, 9th lords, and Yogakarakas). Malefic, afflicted, or Dusthana planets must NEVER be given gemstones. "
                "Instead, classical Shastras prescribe 'Pratikula Shanti': safe pacification through Rudraksha Beads, Moola Mantras, Daana (charity), and Sthala Yatra."
            ),
            "gemstones_method": "Anukula Reinforcement (Magnifies benefic light; worn on fingers)",
            "rudraksha_method": "Pratikula Pacification (Electromagnetic bio-calming; absorbs and neutralizes stress/doshas safely without radiation amplification)",
        }

        anukula_doctrine_ta = {
            "title": "அனுகூல ரத்தின முறை vs பிரதிகூல சாந்தி முறை",
            "authority": "பிருஹத் சம்ஹிதை (அத். 80), கருட புராணம், மணி மாலா",
            "core_principle": (
                "ரத்தினங்கள் என்பவை வானியல் கதிர்வீச்சை கிரகித்து உடலின் ஆரா மண்டலத்தில் பெருக்கும் காந்தக் கண்ணாடிகள் போன்றது. "
                "அவை எப்போதும் கிரகத்தின் ஆற்றலை பெருக்கவே செய்யும்; சாந்தப்படுத்தாது! ஆகவே 'அனுகூல வாத' விதிப்படி, யோககாரகர்கள் மற்றும் லக்ன/திரிகோண சுப கிரகங்களுக்கு மட்டுமே "
                "ரத்தினங்களை அணிய வேண்டும். மறைவு ஸ்தானாதிபதிகள் (6, 8, 12) மற்றும் பாப கிரகங்களுக்கு ரத்தினம் அணிந்தால் விபரீத விளைவுகள் ஏற்படும். "
                "அவற்றுக்கு 'பிரதிகூல சாந்தி' முறையில் ருத்ராட்சம், மூல மந்திர ஜெபம், தானங்கள் மற்றும் கோவில் வழிபாடுகள் மட்டுமே செய்ய வேண்டும்."
            ),
            "gemstones_method": "அனுகூல வலுவூட்டல் (சுப ஒளிக்கதிர்களை பெருக்கும்; விரல்களில் அணிதல்)",
            "rudraksha_method": "பிரதிகூல சாந்தி (மின்காந்த அதிர்வுகளை சமன் செய்து, பக்கவிளைவுகளின்றி தோஷங்களை அமைதிப்படுத்துதல்)",
        }

        # 5. Rudraksha Evaluation
        rudraksha_summary = RudrakshaAdvisoryEngine.evaluate_rudraksha(
            lagna_sign=lagna_sign,
            moon_sign=moon_sign,
            running_mahadasha=running_mahadasha,
            running_bhukti=running_bhukti,
            debilitated_planets=debilitated_planets,
            combust_planets=combust_planets,
            has_kuja_dosha=has_kuja_dosha,
            has_sade_sati=has_sade_sati,
            has_kaal_sarp=has_kaal_sarp,
        )
        rudraksha_catalog = RudrakshaAdvisoryEngine.get_all_beads()

        # 6. Conflicting combinations warnings
        conflicts_en = [
            "Rule of Mutual Incompatibility: Never wear gems of mutual planetary enemies simultaneously (e.g. Ruby + Blue Sapphire, Pearl + Hessonite/Cat's Eye, Yellow Sapphire + Diamond).",
            "Trial Period Mandatory: Blue Sapphire (Neelam) and Hessonite (Gomed) must be kept under your pillow for 3 consecutive nights to verify harmony before metal setting.",
            "Cracked or Treated Gems Warning: Never wear fractured, heavily heat-treated, synthetic, or chipped stones as classical Shastras indicate they bring sudden misfortune.",
            "Rudraksha Harmony: Rudraksha beads (unlike gemstones) can be worn harmoniously with all authentic Anukula gemstones without conflict.",
        ]
        conflicts_ta = [
            "பகை கிரக ரத்தினங்களை ஒருபோதும் ஒன்றாக அணியக் கூடாது (எ.கா: மாணிக்கம் + நீலம்; முத்து + கோமேதகம்; புஷ்பராகம் + வைரம்).",
            "சோதனை விதி: நீலக்கல் மற்றும் கோமேதகம் அணிவதற்கு முன் 3 இரவுகள் தலையணையின் கீழ் வைத்து சுப/அசுப கனவுகளை சோதித்துப் பார்க்க வேண்டும்.",
            "விரிசல், உடைசல் அல்லது செயற்கை முறையில் தயாரிக்கப்பட்ட ரத்தினங்களை அணியக்கூடாது; அவை தோஷங்களை ஏற்படுத்தும்.",
            "ருத்ராட்ச இணக்க விதி: ருத்ராட்சங்களை அனைத்து சுப ரத்தினங்களுடனும் எவ்வித முரண்பாடும் இன்றி தாராளமாக ஒன்றாக அணியலாம்.",
        ]

        rules_en = [
            "Always set gemstones with an open back so the polished pavilion directly touches the epidermal skin surface.",
            "Purify and energize the ring during the prescribed planetary hora and bright fortnight (Shukla Paksha).",
            "Re-energize the gemstone annually on the deity's sacred festival day (e.g. Guru Purnima for Yellow Sapphire).",
            "Standard Weight Rule: Wear at least 1 Ratti per 10 kg of body weight for optimal bio-energetic resonance.",
        ]
        rules_ta = [
            "ரத்தினத்தின் அடிபாகம் தோலில் படும் வகையில் மோதிரம் அமைக்கப்பட வேண்டும்.",
            "வளர்பிறை சுப தினத்தில் உரிய கிரக ஓரையில் சுத்தி செய்து அணிவது கட்டாயம்.",
            "ஆண்டுதோறும் உரிய திருநாளில் (எ.கா: குரு பூர்ணிமா) மோதிரத்தை மீண்டும் பூஜித்து புதுப்பிக்க வேண்டும்.",
            "எடை விதி: உடலின் 10 கிலோ எடைக்கு குறைந்தது 1 ரட்டி வீதம் ரத்தினம் அமைப்பது உத்தமமானது.",
        ]

        notice_en = (
            "Classical Jyotish Mandate: Gemstone prescription is a potent spiritual and bio-energetic intervention. "
            "While this automated audit enforces classical Shastra rules, in-person verification with a certified astrologer "
            "is strongly recommended to assess D9 Navamsa dignity, combustion degrees, and Maraka/Badhaka sensitivities."
        )
        notice_ta = (
            "பாரம்பரிய ஜோதிட விதி: ரத்தினங்கள் உடலின் மின்காந்த அதிர்வுகளை மாற்றும் ஆற்றல் கொண்டவை. "
            "நவாம்ச பலம், அஸ்தமனம் மற்றும் மாரக/பாதக நிலைகளை ஒரு தகுதிவாய்ந்த ஜோதிடரிடம் நேரில் காட்டி உறுதிப்படுத்திய பின்னரே ரத்தினங்களை அணிய வேண்டும்."
        )

        return GemstoneAdvisoryResponse(
            lagna_sign=lagna_sign,
            moon_sign=moon_sign,
            running_mahadasha=running_mahadasha,
            running_bhukti=running_bhukti,
            body_weight_kg=body_weight_kg,
            life_stone=life_rec,
            lucky_stone=lucky_rec,
            fortune_stone=fortune_rec,
            secondary_support_stone=secondary_rec,
            prohibited_gemstones=prohibited_items,
            anukula_vs_pratikula_doctrine_en=anukula_doctrine_en,
            anukula_vs_pratikula_doctrine_ta=anukula_doctrine_ta,
            recommended_rudraksha=rudraksha_summary,
            rudraksha_catalog=rudraksha_catalog,
            conflicting_combinations_warning_en=conflicts_en,
            conflicting_combinations_warning_ta=conflicts_ta,
            general_wearing_rules_en=rules_en,
            general_wearing_rules_ta=rules_ta,
            mandatory_review_notice_en=notice_en,
            mandatory_review_notice_ta=notice_ta,
        )

    @classmethod
    def _build_recommendation(
        cls,
        category_code: str,
        category_name_en: str,
        category_name_ta: str,
        governing_purpose_en: str,
        governing_purpose_ta: str,
        lagna_sign: str,
        graha: str,
        body_weight_kg: Optional[float] = None,
    ) -> GemstoneRecommendation:
        """Constructs an individual gemstone recommendation object with weight formulas and mantras."""
        meta = PLANET_GEMSTONE_DATA[graha]
        houses = cls.get_houses_ruled_by_planet(lagna_sign, graha)
        houses_str = ", ".join(f"{h}th" for h in houses)

        # Weight calculation: 1 Ratti per 10 kg body weight
        base_carats = meta["minimum_carats"]
        base_rattis = meta.get("minimum_rattis", round(base_carats * 1.1, 2))

        if body_weight_kg and body_weight_kg > 30:
            calc_ratti = round(body_weight_kg / 10.0, 2)
            rec_rattis = max(base_rattis, calc_ratti)
            rec_carats = round(rec_rattis * 0.91, 2)
            formula_en = f"Personalized: {body_weight_kg:.1f} kg ÷ 10 = {calc_ratti:.2f} Rattis (approx {rec_carats:.2f} Carats / {int(rec_carats*200)} mg)."
            formula_ta = f"தனிப்பயன் எடை: {body_weight_kg:.1f} கிலோ ÷ 10 = {calc_ratti:.2f} ரட்டி (தோராயமாக {rec_carats:.2f} காரட் / {int(rec_carats*200)} மி.கி)."
        else:
            rec_carats = base_carats
            rec_rattis = base_rattis
            formula_en = f"Standard Classical Threshold: Minimum {base_rattis:.1f} Rattis ({base_carats:.2f} Carats). (Formula: 1 Ratti per 10 kg body weight)."
            formula_ta = f"பாரம்பரிய குறைந்தபட்ச அளவு: குறைந்தது {base_rattis:.1f} ரட்டி ({base_carats:.2f} காரட்). (விதி: 10 கிலோ உடல் எடைக்கு 1 ரட்டி)."

        # Check if rules 6, 8, or 12
        rules_dusthana = any(h in (6, 8, 12) for h in houses)
        if category_code == "life_stone":
            safety = "auspicious"
            eligible = True
            just_en = f"As the Lagna Lord ruling the 1st house ({houses_str}) for {lagna_sign}, this stone is universally supportive of life vitality."
            just_ta = f"{lagna_sign} லக்னத்தின் லக்னாதிபதியாக விளங்குவதால் ({houses_str} வீடுகள்), இந்த ரத்தினம் உடலுக்கும் உயிருக்கும் சிறந்த பாதுகாப்பு அரணாக திகழ்கிறது."
        elif category_code == "secondary_support":
            safety = "auspicious"
            eligible = True
            just_en = f"Yogakaraka / Auspicious Dasha Lord governing house(s) ({houses_str}). Highly potent for material expansion and royal favor."
            just_ta = f"யோககாரகன் / சுப தசா நாதன் ({houses_str} வீடுகள்). தொழில் மற்றும் சமூக அந்தஸ்தை உயர்த்தும் ஆற்றல் வாய்ந்தது."
        elif rules_dusthana:
            safety = "caution_required"
            eligible = True
            just_en = f"Rules the auspicious house along with a Dusthana ({houses_str}). Must only be worn if well-placed in Kendra/Trikona and verified by an astrologer."
            just_ta = f"சுப ஸ்தானத்துடன் மறைவு ஸ்தானத்தையும் ({houses_str}) ஆட்சி செய்வதால், கேந்திர/திரிகோண பலம் பெற்றிருந்தால் மட்டுமே அணிய வேண்டும்."
        else:
            safety = "auspicious"
            eligible = True
            just_en = f"Pure functional benefic ruling the auspicious {houses_str} house(s). Highly recommended for sustained fortune and merit."
            just_ta = f"முழுமையான சுப ஸ்தானங்களை ({houses_str}) ஆட்சி செய்வதால், மேலான அதிர்ஷ்டமும் நற்பலன்களும் கிட்டும்."

        return GemstoneRecommendation(
            category_code=category_code,
            category_name_en=category_name_en,
            category_name_ta=category_name_ta,
            governing_purpose_en=governing_purpose_en,
            governing_purpose_ta=governing_purpose_ta,
            graha=graha,
            graha_name_en=meta["graha_name_en"],
            graha_name_ta=meta["graha_name_ta"],
            house_lordships=houses,
            primary_gem_en=meta["primary_gem_en"],
            primary_gem_ta=meta["primary_gem_ta"],
            primary_gem_sanskrit=meta["primary_gem_sanskrit"],
            upratna_substitutes_en=meta["upratna_substitutes_en"],
            upratna_substitutes_ta=meta["upratna_substitutes_ta"],
            prescribed_metal_en=meta["prescribed_metal_en"],
            prescribed_metal_ta=meta["prescribed_metal_ta"],
            ideal_finger_en=meta["ideal_finger_en"],
            ideal_finger_ta=meta["ideal_finger_ta"],
            minimum_carats=rec_carats,
            minimum_rattis=rec_rattis,
            weight_guideline_formula_en=formula_en,
            weight_guideline_formula_ta=formula_ta,
            energization_day_en=meta["energization_day_en"],
            energization_day_ta=meta["energization_day_ta"],
            consecration_mantra_sanskrit=meta["consecration_mantra_sanskrit"],
            consecration_mantra_ta=meta["consecration_mantra_ta"],
            gayatri_mantra_sanskrit=meta.get("gayatri_mantra_sanskrit"),
            gayatri_mantra_ta=meta.get("gayatri_mantra_ta"),
            cleansing_vidhi_en=meta["cleansing_vidhi_en"],
            cleansing_vidhi_ta=meta["cleansing_vidhi_ta"],
            safety_status=safety,
            is_eligible=eligible,
            astrological_justification_en=just_en,
            astrological_justification_ta=just_ta,
            incompatible_gems_warning_en=meta["incompatible_gems_warning_en"],
            incompatible_gems_warning_ta=meta["incompatible_gems_warning_ta"],
        )
