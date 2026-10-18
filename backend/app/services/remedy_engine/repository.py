"""Remedy Knowledge Base Repository and Data Access Layer.

Handles data access for Problem Taxonomy, Remedy Catalog, Source References,
and Tamil Navagraha Temples. Implements seamless dual-tier access: attempts
Supabase REST queries via Service Role client first, gracefully falling back
to verified, canonical in-memory registries for development, testing, and offline modes.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.services.auth_service import get_supabase_client
from app.services.remedy_engine.taxonomy import VERIFIED_PROBLEM_TAXONOMY, TAXONOMY_BY_SLUG

logger = logging.getLogger(__name__)

# ─── Canonical Classical Source References ────────────────────────────────────
VERIFIED_SOURCES: List[Dict[str, Any]] = [
    {
        "code": "BPHS",
        "title_en": "Brihat Parashara Hora Shastra",
        "title_sa": "बृहत्पाराशरहोराशास्त्रम्",
        "author": "Maharishi Parashara",
        "tradition": "classical_jyotish",
        "canonical_status": "primary_shastra",
        "description": "Foundational compendium of Vedic astrology detailing planetary natures, avasthas, afflictions, and classical shanti remedies.",
        "is_published": True,
    },
    {
        "code": "PHALADEEPIKA",
        "title_en": "Phaladeepika",
        "title_sa": "फलदीपिका",
        "author": "Mantreswara",
        "tradition": "classical_jyotish",
        "canonical_status": "primary_shastra",
        "description": "Classical medieval text covering planetary strengths, bhava results, yogas, and remedial pacification.",
        "is_published": True,
    },
    {
        "code": "NAVAGRAHA_STOTRAM",
        "title_en": "Sri Navagraha Stotram",
        "title_sa": "नवग्रहस्तोत्रम्",
        "author": "Sri Veda Vyasa",
        "tradition": "puranic",
        "canonical_status": "stotra_samhita",
        "description": "Nine sacred hymns composed by Sage Veda Vyasa in the Mahabharata / Puranic tradition to propitiate the nine celestial grahas.",
        "is_published": True,
    },
    {
        "code": "VALMIKI_RAMAYANA",
        "title_en": "Valmiki Ramayana - Aditya Hridayam",
        "title_sa": "आदित्यहृदयम्",
        "author": "Sage Agastya / Maharishi Valmiki",
        "tradition": "puranic",
        "canonical_status": "stotra_samhita",
        "description": "Sacred hymn imparted by Sage Agastya to Lord Sri Rama on the battlefield (Yuddha Kanda 105) for victory, health, and dispelling inner fear.",
        "is_published": True,
    },
    {
        "code": "RIGVEDA",
        "title_en": "Rigveda Samhita - Maha Mrityunjaya",
        "title_sa": "त्र्यम्बकं यजामहे",
        "author": "Rishi Markandeya / Sage Vasistha",
        "tradition": "vedic",
        "canonical_status": "primary_shastra",
        "description": "The great death-conquering hymn (Rigveda 7.59.12) dedicated to Rudra for vital protection, healing, and freedom from disease and fear.",
        "is_published": True,
    },
    {
        "code": "MANTRA_MAHODADHI",
        "title_en": "Mantra Mahodadhi",
        "title_sa": "मन्त्रमहोदधिः",
        "author": "Mahidhara",
        "tradition": "tantric",
        "canonical_status": "stotra_samhita",
        "description": "Comprehensive encyclopaedia of traditional Vedic-Tantric mantra vidhi, seed syllables (bijakshara), and japa procedures.",
        "is_published": True,
    },
    {
        "code": "KAVERI_DELTA_TRADITION",
        "title_en": "Kaveri Delta Navagraha Sthala Purana",
        "title_sa": "காவிரி டெல்டா நவகிரக ஸ்தல புராணம்",
        "author": "Tamil Shaiva-Vaishnava Tradition",
        "tradition": "tamil_shaiva",
        "canonical_status": "regional_tradition",
        "description": "Sacred temple traditions of the nine classical Navagraha sthalams located around Kumbakonam, Thanjavur, and Mayiladuthurai in Tamil Nadu.",
        "is_published": True,
    },
]

# ─── Authentic Kaveri Delta Tamil Navagraha Temples ──────────────────────────
VERIFIED_TEMPLES: List[Dict[str, Any]] = [
    {
        "code": "TEMPLE_SURYANAR_KOVIL",
        "graha": "sun",
        "name_en": "Suryanar Kovil",
        "name_ta": "சூரியனார் கோவில்",
        "presiding_deity_en": "Sri Suryanarayana Swamy",
        "presiding_deity_ta": "ஸ்ரீ சூரியநாராயண சுவாமி",
        "graha_deity_en": "Lord Surya (Sun)",
        "graha_deity_ta": "சூரிய பகவான்",
        "place_name_en": "Suryanar Kovil (near Aduthurai)",
        "place_name_ta": "சூரியனார் கோவில் (ஆடுதுறை அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "state": "Tamil Nadu",
        "latitude": 11.0253,
        "longitude": 79.4891,
        "visiting_day_en": "Sunday",
        "visiting_day_ta": "ஞாயிற்றுக்கிழமை",
        "significance_en": "The premier Sun temple in Tamil Nadu where Lord Surya is worshipped with his consorts Usha and Chhaya. Uniquely houses shrines for all other eight grahas facing Surya.",
        "significance_ta": "தமிழகத்தின் முதன்மை சூரிய தலம். உஷா, சாயா தேவியருடன் சூரிய பகவான் அருள்பாலிக்கிறார். மற்ற எட்டு கிரகங்களும் சூரியனை நோக்கியவாறு தனித்தனி சன்னதிகளில் அமைந்திருப்பது இதன் தனிச்சிறப்பு.",
        "remedy_offerings_en": "Offering wheat, jaggery, red flowers, lighting ghee lamps, performing circumambulation (pradakshina) on Sundays at dawn.",
        "remedy_offerings_ta": "கோதுமை, வெல்லம், செந்தாமரை மலர்கள் சமர்ப்பித்தல், நெய் தீபம் ஏற்றுதல் மற்றும் ஞாயிறு அதிகாலை பிரதட்சணம் செய்தல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_THINGALUR",
        "graha": "moon",
        "name_en": "Thingalur Kailasanathar Temple",
        "name_ta": "திங்களூர் கைலாசநாதர் கோவில்",
        "presiding_deity_en": "Sri Kailasanathar and Goddess Periyanayaki",
        "presiding_deity_ta": "ஸ்ரீ கைலாசநாதர் - பெரியநாயகி அம்மன்",
        "graha_deity_en": "Lord Chandra (Moon)",
        "graha_deity_ta": "சந்திர பகவான்",
        "place_name_en": "Thingalur (near Thiruvaiyaru)",
        "place_name_ta": "திங்களூர் (திருவையாறு அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "state": "Tamil Nadu",
        "latitude": 10.8789,
        "longitude": 79.1678,
        "visiting_day_en": "Monday",
        "visiting_day_ta": "திங்கட்கிழமை",
        "significance_en": "Classical Moon sthalam where Lord Moon worshipped Shiva to regain luminosity. Associated with relief from maternal distress, mental instability, and emotional turmoil.",
        "significance_ta": "சந்திர தோஷ நிவர்த்தி தலம். சந்திரன் சிவபெருமானை பூஜித்து சாப விமோசனம் பெற்ற இடம். மன அமைதி, தாயார் நலம் மற்றும் கல்வி மேன்மை அருளும் தலம்.",
        "remedy_offerings_en": "Offering white raw rice, milk kheer (payasam), white cloth, white arali flowers, lighting lamps on Mondays.",
        "remedy_offerings_ta": "பச்சரிசி, பசும்பால் பாயாசம், வெள்ளை வஸ்திரம், வெள்ளை அரளி மலர்கள் சாற்றி திங்கள்கிழமை வழிபாடு செய்தல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_VAITHEESWARAN",
        "graha": "mars",
        "name_en": "Vaitheeswaran Kovil",
        "name_ta": "வைத்தீஸ்வரன் கோவில்",
        "presiding_deity_en": "Sri Vaidyanatha Swamy and Goddess Thaiyalnayaki",
        "presiding_deity_ta": "ஸ்ரீ வைத்தியநாத சுவாமி - தையல்நாயகி அம்மன்",
        "graha_deity_en": "Lord Sevvai / Angarakan (Mars)",
        "graha_deity_ta": "அங்காரகன் / செவ்வாய் பகவான்",
        "place_name_en": "Vaitheeswaran Kovil (near Sirkazhi)",
        "place_name_ta": "வைத்தீஸ்வரன் கோவில் (சீர்காழி அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "state": "Tamil Nadu",
        "latitude": 11.2023,
        "longitude": 79.7314,
        "visiting_day_en": "Tuesday",
        "visiting_day_ta": "செவ்வாய்க்கிழமை",
        "significance_en": "World-renowned healing sthalam and supreme Mars (Angaraka) pilgrimage. Lord Shiva as the Divine Physician heals physical ailments, removes Kuja / Manglik dosha, and settles property obstacles.",
        "significance_ta": "புகழ்பெற்ற செவ்வாய் ஸ்தலம் மற்றும் பிணி தீர்க்கும் தலம். வைத்தீஸ்வரர் சித்தாமிர்த தீர்த்தத்துடன் தீராத நோய்களைத் தீர்த்து, செவ்வாய் தோஷம் மற்றும் நிலம் சார்ந்த தடைகளை நீக்குகிறார்.",
        "remedy_offerings_en": "Offering red lentils (thoor/masoor dal), red cloth, vilvam leaves, and lighting sesame/ghee lamps on Tuesdays.",
        "remedy_offerings_ta": "துவரம்பருப்பு, சிவப்பு வஸ்திரம், செவ்வரளி மாலை சாற்றி, சித்தாமிர்த தீர்த்தத்தில் நீராடி செவ்வாய்க்கிழமை வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_THIRUVENKADU",
        "graha": "mercury",
        "name_en": "Thiruvenkadu Swetharanyeswarar Temple",
        "name_ta": "திருவெண்காடு சுவேதாரண்யேஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Swetharanyeswarar and Goddess Brahmavidyambigai",
        "presiding_deity_ta": "ஸ்ரீ சுவேதாரண்யேஸ்வரர் - பிரம்மவித்யாம்பிகை",
        "graha_deity_en": "Lord Budhan (Mercury)",
        "graha_deity_ta": "புதன் பகவான்",
        "place_name_en": "Thiruvenkadu (near Poompuhar)",
        "place_name_ta": "திருவெண்காடு (பூம்புகார் அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "state": "Tamil Nadu",
        "latitude": 11.1789,
        "longitude": 79.8234,
        "visiting_day_en": "Wednesday",
        "visiting_day_ta": "புதன்கிழமை",
        "significance_en": "Venerated Mercury sthalam known as the Adi Chidambaram. Famed for granting intellectual brilliance, educational excellence, musical talents, and healing nervous disorders.",
        "significance_ta": "ஆதி சிதம்பரம் என்று போற்றப்படும் புதன் தலம். புதன் பகவான் தனி சன்னதியில் அருள்கிறார். கல்வி, பேச்சுத்திறன், வணிக மேன்மை மற்றும் நரம்பு மண்டல ஆரோக்கியம் அருளும் தலம்.",
        "remedy_offerings_en": "Offering green gram (moong dal), green cloth, vilvam leaves, tulasi, lighting lamps on Wednesdays.",
        "remedy_offerings_ta": "பச்சைப்பயறு, பச்சை வஸ்திரம், வெண்காந்தள்/துளசி மாலை சாற்றி புதன்கிழமை தோறும் நெய் தீபமிட்டு வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_ALANGUDI",
        "graha": "jupiter",
        "name_en": "Alangudi Apatsahayeswarar Temple",
        "name_ta": "ஆலங்குடி ஆபத்சகாயேஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Apatsahayeswarar and Goddess Elavarkuzhali",
        "presiding_deity_ta": "ஸ்ரீ ஆபத்சகாயேஸ்வரர் - ஏலவார்குழலி அம்மன்",
        "graha_deity_en": "Lord Guru (Jupiter / Dakshinamurthy)",
        "graha_deity_ta": "குரு பகவான் / தட்சிணாமூர்த்தி",
        "place_name_en": "Alangudi (near Valangaiman)",
        "place_name_ta": "ஆலங்குடி (வலங்கைமான் அருகில்)",
        "district_en": "Tiruvarur",
        "district_ta": "திருவாரூர்",
        "state": "Tamil Nadu",
        "latitude": 10.8256,
        "longitude": 79.4089,
        "visiting_day_en": "Thursday",
        "visiting_day_ta": "வியாழக்கிழமை",
        "significance_en": "Foremost Jupiter sthalam where Lord Shiva consumed poison to protect the universe. Dedicated Guru shrine worshipped for marital blessings, child boon, spiritual wisdom, and career growth.",
        "significance_ta": "தலைசிறந்த குரு பரிகாரத் தலம். ஆபத்சகாயேஸ்வரர் ஆலகால விஷம் உண்டு தேவர்களைக் காத்த இடம். திருமண பாக்கியம், புத்திர பாக்கியம் மற்றும் ஞானம் வேண்டி பக்தர்கள் கூடும் புண்ணிய தலம்.",
        "remedy_offerings_en": "Offering yellow split chana dal garland, yellow cloth, mullai flowers, lighting 24 ghee deepams on Thursdays.",
        "remedy_offerings_ta": "கொண்டைக்கடலை மாலை, மஞ்சள் வஸ்திரம், முல்லை மலர்கள் சாற்றி 24 நெய் தீபங்கள் ஏற்றி வியாழக்கிழமை வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_KANJANUR",
        "graha": "venus",
        "name_en": "Kanjanur Agneeswarar Temple",
        "name_ta": "கஞ்சனூர் அக்னீஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Agneeswarar and Goddess Karpagambal",
        "presiding_deity_ta": "ஸ்ரீ அக்னீஸ்வரர் - கற்பகாம்பாள்",
        "graha_deity_en": "Lord Sukran (Venus)",
        "graha_deity_ta": "சுக்கிர பகவான்",
        "place_name_en": "Kanjanur (near Kumbakonam)",
        "place_name_ta": "கஞ்சனூர் (கும்பகோணம் அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "state": "Tamil Nadu",
        "latitude": 11.0667,
        "longitude": 79.4833,
        "visiting_day_en": "Friday",
        "visiting_day_ta": "வெள்ளிக்கிழமை",
        "significance_en": "Supreme Venus sthalam. Agni Bhagavan worshipped Shiva here to be cured of affliction. Lord Shiva himself reflects the radiant qualities of Sukra here, blessing devotees with prosperity and artistic flourish.",
        "significance_ta": "சுக்கிர பகவான் வழிபட்ட முக்கிய தலம். இங்கு சிவபெருமானே சுக்கிரனின் அம்சமாக அருள்பாலிக்கிறார். தம்பதியர் ஒற்றுமை, செல்வம், கலை ஞானம் மற்றும் வாகன யோகம் நல்கும் தலம்.",
        "remedy_offerings_en": "Offering white field beans (mochai), white silk cloth, white lotus, sweet milk dishes on Fridays.",
        "remedy_offerings_ta": "மொச்சைப்பயறு, வெண்பட்டு, வெண்தாமரை மலர்கள் சாற்றி, சர்க்கரைப் பொங்கல் அல்லது பாயாசம் படைத்து வெள்ளிக்கிழமை வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_THIRUNALLAR",
        "graha": "saturn",
        "name_en": "Thirunallar Dharbaranyeswarar Temple",
        "name_ta": "திருநள்ளாறு தர்பாரண்யேஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Dharbaranyeswarar and Goddess Pranambigai",
        "presiding_deity_ta": "ஸ்ரீ தர்பாரண்யேஸ்வரர் - பிராணாம்பிகை",
        "graha_deity_en": "Lord Saneeswara (Saturn)",
        "graha_deity_ta": "ஸ்ரீ சனீஸ்வர பகவான்",
        "place_name_en": "Thirunallar (near Karaikal)",
        "place_name_ta": "திருநள்ளாறு (காரைக்கால் அருகில்)",
        "district_en": "Karaikal / Puducherry-TN Border",
        "district_ta": "காரைக்கால் / தமிழக எல்லை",
        "state": "Puducherry / Tamil Nadu",
        "latitude": 10.9272,
        "longitude": 79.7911,
        "visiting_day_en": "Saturday",
        "visiting_day_ta": "சனிக்கிழமை",
        "significance_en": "World-renowned Saturn shrine where King Nala was released from the malefic grip of Saturn after bathing in the Nala Theertham. Propitiated for Sade Sati, Ashtama Shani, and chronic hurdles.",
        "significance_ta": "உலகப் புகழ்பெற்ற சனி பரிகார ஸ்தலம். நள தமயந்தி புராணத்துடன் தொடர்புடையது. நள தீர்த்தத்தில் நீராடி எள்தீபம் ஏற்றுவதன் மூலம் ஏழரைச் சனி, அஷ்டமச் சனி மற்றும் வாத நோய்களின் தாக்கம் தணிகிறது.",
        "remedy_offerings_en": "Holy dip in Nala Theertham, lighting black sesame oil lamps in clay pots, donating black sesame seeds and iron items on Saturdays.",
        "remedy_offerings_ta": "நள தீர்த்தத்தில் நீராடி, கருப்பு எள் தீபமேற்றி, நீல நிற வஸ்திரம் அல்லது எள் தானம் வழங்கி சனிக்கிழமைகளில் வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_THIRUNAGESWARAM",
        "graha": "rahu",
        "name_en": "Thirunageswaram Naganathaswamy Temple",
        "name_ta": "திருநாகேஸ்வரம் நாகநாதசுவாமி கோவில்",
        "presiding_deity_en": "Sri Naganathaswamy and Goddess Pirayanindasoodi",
        "presiding_deity_ta": "ஸ்ரீ நாகநாதசுவாமி - பிறையணிந்தசூடி அம்மன்",
        "graha_deity_en": "Lord Rahu Bhagavan",
        "graha_deity_ta": "ராகு பகவான்",
        "place_name_en": "Thirunageswaram (near Kumbakonam)",
        "place_name_ta": "திருநாகேஸ்வரம் (கும்பகோணம் அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "state": "Tamil Nadu",
        "latitude": 10.9633,
        "longitude": 79.4317,
        "visiting_day_en": "Sunday (or Rahu Kalam)",
        "visiting_day_ta": "ஞாயிற்றுக்கிழமை (ராகு காலம்)",
        "significance_en": "Premier Rahu sthalam where Rahu Bhagavan worshipped Shiva. Famous for the miraculous milk abhishekam during Rahu Kalam, where milk poured on the idol visibly turns light blue.",
        "significance_ta": "ராகு பகவானின் முதன்மைப் பரிகாரத் தலம். ராகு காலத்தில் ராகு பகவானுக்கு செய்யப்படும் பாலாபிஷேகத்தின் போது பால் நீல நிறமாக மாறும் அதிசயம் நிகழும் புண்ணிய பூமி. நாக தோஷம், காலசர்ப்ப தோஷ நிவர்த்தி தலம்.",
        "remedy_offerings_en": "Milk Abhishekam during Rahu Kalam, offering urad dal, blue flowers, and lighting sesame oil lamps.",
        "remedy_offerings_ta": "ராகு காலத்தில் பாலாபிஷேகம் செய்தல், உளுந்து சமர்ப்பித்தல், நீல நிற மலர்கள் சாற்றி நல்லெண்ணெய் தீபம் ஏற்றுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "TEMPLE_KEEZHPERUMPALLAM",
        "graha": "ketu",
        "name_en": "Keezhperumpallam Naganathaswamy Temple",
        "name_ta": "கீழ்ப்பெரும்பள்ளம் நாகநாதசுவாமி கோவில்",
        "presiding_deity_en": "Sri Naganathaswamy and Goddess Soundaranayaki",
        "presiding_deity_ta": "ஸ்ரீ நாகநாதசுவாமி - சௌந்தரநாயகி",
        "graha_deity_en": "Lord Ketu Bhagavan",
        "graha_deity_ta": "கேது பகவான்",
        "place_name_en": "Keezhperumpallam (near Poompuhar)",
        "place_name_ta": "கீழ்ப்பெரும்பள்ளம் (பூம்புகார் அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "state": "Tamil Nadu",
        "latitude": 11.1436,
        "longitude": 79.8456,
        "visiting_day_en": "Tuesday",
        "visiting_day_ta": "செவ்வாய்க்கிழமை",
        "significance_en": "Supreme Ketu sthalam where Ketu Bhagavan, having a human head and serpent body, worshipped Lord Shiva with folded hands for spiritual liberation and redemption.",
        "significance_ta": "ஞானகாரகனான கேது பகவானின் பிரதான தலம். கேது பகவான் இங்கு மனித முகத்துடனும் பாம்பு உடலுடனும் சிவபெருமானை கைகூப்பி வணங்கும் கோலத்தில் அருள்பாலிக்கிறார். ஆன்மீக மேன்மை மற்றும் மோட்சம் அருளும் தலம்.",
        "remedy_offerings_en": "Offering horsegram (kollu), multi-coloured cloth, red/spotted flowers, and performing circumambulation on Tuesdays.",
        "remedy_offerings_ta": "கொள்ளு தானம் செய்தல், பலவண்ண வஸ்திரம் சாற்றி, செவ்வரளி மாலை அணிவித்து செவ்வாய்க்கிழமை தோறும் வழிபடுதல்.",
        "source_tradition": "Kaveri Delta Navagraha Sthalam",
        "is_published": True,
        "verification_status": "verified",
    },
]

# ─── Verified Foundational Remedies Catalog ──────────────────────────────────
VERIFIED_REMEDIES: List[Dict[str, Any]] = [
    {
        "code": "REM_UNIV_GANESHA_01",
        "graha": "universal",
        "remedy_type": "mantra",
        "name_en": "Sri Ganesha Moola Mantra",
        "name_ta": "ஸ்ரீ கணேச மூல மந்திரம்",
        "description_en": "Foundational Vedic invocation chanted before initiating any astrological remedy or noble spiritual practice to remove obstacles.",
        "description_ta": "எந்த ஒரு ஜோதிடப் பரிகாரம் அல்லது சுப காரியத்தைத் தொடங்குவதற்கு முன் தடைகளை நீக்கி வெற்றி பெற உச்சரிக்க வேண்டிய முழுமுதற் கடவுள் கணபதியின் மூல மந்திரம்.",
        "deity_en": "Lord Ganesha",
        "deity_ta": "ஸ்ரீ விநாயகப் பெருமான்",
        "sanskrit_text": "ॐ गं गणपतये नमः ॥",
        "transliteration_iast": "oṃ gaṃ gaṇapataye namaḥ ॥",
        "transliteration_ta": "ஓம் கம் கணபதயே நமஹ ॥",
        "meaning_en": "Salutations to Lord Ganesha, the embodiment of wisdom, ruler of the celestial hosts, and the supreme remover of all hindrances.",
        "meaning_ta": "அனைத்து கணங்களுக்கும் தலைவரும், விக்கினங்களைத் தீர்ப்பவருமான விநாயகப் பெருமானைப் பணிந்து வணங்குகிறேன்.",
        "procedure_en": "Sit facing North or East. Cleanse hands and chant 108 times using a Rudraksha or Sandalwood mala before starting any planetary remedies.",
        "procedure_ta": "வடக்கு அல்லது கிழக்கு நோக்கி அமர்ந்து, கைகளைச் சுத்தி செய்து, ருத்ராட்சம் அல்லது சந்தன மாலையைக் கொண்டு 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Daily at dawn or before commencing any sacred endeavor",
        "timing_recommendation_ta": "தினமும் விடியற்காலை அல்லது புதிய காரியங்களைத் தொடங்கும் முன்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["spiritual_stagnation", "house_construction_hurdles", "business_setbacks"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_UNIV_MRITYUNJAYA_01",
        "graha": "universal",
        "remedy_type": "mantra",
        "name_en": "Maha Mrityunjaya Healing Mantra",
        "name_ta": "மகா மிருத்யுஞ்சய மகா மந்திரம்",
        "description_en": "Sacred Rigvedic healing prayer (Rigveda 7.59.12) dedicated to Lord Shiva as Tryambaka for freedom from severe health afflictions, accidents, and dread.",
        "description_ta": "ரிக்வேதத்தில் அருளப்பட்ட சிவபெருமானின் ஒப்புயர்வற்ற மகா மந்திரம். கொடிய நோய்கள், விபத்துகள் மற்றும் மரண பயத்தை நீக்கி நீண்ட ஆயுளையும் நலனையும் நல்கும்.",
        "deity_en": "Lord Shiva (Tryambaka)",
        "deity_ta": "சிவபெருமான் (முக்கண்ணன்)",
        "sanskrit_text": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् । उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात् ॥",
        "transliteration_iast": "oṃ tryambakaṃ yajāmahe sugandhiṃ puṣṭivardhanam | urvārukamiva bandhanānmṛtyormukṣīya māmṛtāt ॥",
        "transliteration_ta": "ஓம் த்ரயம்பகம் யஜாமஹே ஸுகந்திம் புஷ்டிவர்த்தனம் । உர்வாருகமிவ பந்தனான்ம்ருத்யோர்முக்ஷீய மாம்ருதாத் ॥",
        "meaning_en": "We worship the Three-Eyed Lord Shiva, who is fragrant and nourishes all beings. May He liberate us from death and disease towards immortality, as effortlessly as a ripe gourd is freed from its creeper.",
        "meaning_ta": "நறுமணமும், அனைவரையும் போஷிக்கும் ஆற்றலும் கொண்ட முக்கண்ணனான சிவனை வணங்குகிறோம். வெள்ளரிப் பழம் காம்பிலிருந்து விடுபடுவது போல, நம்மை நோய்கள் மற்றும் மரணப் பிடியிலிருந்து விடுவித்து அமிர்த வாழ்வை அருள்புரிவாராக.",
        "procedure_en": "Recite 108 times daily facing North or East, preferably after morning bath. Can be chanted alongside medical treatment for recovery.",
        "procedure_ta": "காலை நீராடிய பின் வடக்கு அல்லது கிழக்கு நோக்கி அமர்ந்து தினமும் 108 முறை அமைதியான மனதுடன் ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Daily at dawn during Brahma muhurta or dusk",
        "timing_recommendation_ta": "தினமும் விடியற்காலை பிரம்ம முகூர்த்தம் அல்லது அந்தி மாலையில்",
        "source_code": "RIGVEDA",
        "source_verse_or_page": "Mandala 7, Sukta 59, Mantra 12",
        "is_pacification_only": False,
        "problem_slugs": ["chronic_health_issues", "mental_anxiety_depression", "vehicle_accidents_breakdowns", "fear_negative_energies"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SUN_MANTRA_01",
        "graha": "sun",
        "remedy_type": "mantra",
        "name_en": "Surya Namaha Mantra",
        "name_ta": "சூரிய நமஹ மந்திரம்",
        "description_en": "Classical Parashari mantra invoking Lord Surya for strengthening vitality, confidence, paternal bonds, and administrative authority.",
        "description_ta": "ஆற்றல், தன்னம்பிக்கை, தந்தை வழி நலம் மற்றும் அரசு/நிர்வாகத் துறை மேன்மைக்காக சூரிய பகவானைப் போற்றி உச்சரிக்கும் எளிய சாத்விக மந்திரம்.",
        "deity_en": "Lord Surya (Sun)",
        "deity_ta": "சூரிய பகவான்",
        "sanskrit_text": "ॐ सूर्याय नमः ॥",
        "transliteration_iast": "oṃ sūryāya namaḥ ॥",
        "transliteration_ta": "ஓம் சூர்யாய நமஹ ॥",
        "meaning_en": "Reverence to the radiant Sun God, the supreme cosmic witness and soul of the universe.",
        "meaning_ta": "அண்ட சராசரங்களின் ஆன்மாவாகவும், ஒளி வடிவாகவும் விளங்கும் சூரிய பகவானுக்கு எனது நமஸ்காரங்கள்.",
        "procedure_en": "Offer clean water mixed with red flowers and a pinch of jaggery from a copper vessel towards the rising sun while reciting 108 times.",
        "procedure_ta": "செப்புப் பாத்திரத்தில் சுத்தமான தண்ணீருடன் செம்பருத்தி அல்லது செந்தாமரை இதழ்கள் சேர்த்து, காலை சூரியனை நோக்கி நின்றபடி 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Sunday mornings during sunrise",
        "timing_recommendation_ta": "ஞாயிற்றுக்கிழமை காலை சூரிய உதய வேளையில்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["career_delay", "promotion_blocks", "vitality_low_energy", "eye_vision_ailments"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SUN_CHARITY_01",
        "graha": "sun",
        "remedy_type": "charity",
        "name_en": "Surya Daan (Wheat & Copper Charity)",
        "name_ta": "சூரிய தானம் (கோதுமை மற்றும் செப்பு தானம்)",
        "description_en": "Classical charity prescribed specifically when Sun acts as a functional malefic or afflicts health bhavas. NOT to be performed if Sun is a functional Yogakaraka.",
        "description_ta": "சூரியன் அசுப ஆதிபத்தியம் பெற்று உடல் நலப் பாதிப்புகளைத் தரும் போது மட்டும் செய்ய வேண்டிய பரிகார தானம். சூரியன் யோககாரகனாக இருக்கும் போது இந்த தானத்தைத் தவிர்க்க வேண்டும்.",
        "deity_en": "Lord Surya",
        "deity_ta": "சூரிய பகவான்",
        "sanskrit_text": None,
        "transliteration_iast": None,
        "transliteration_ta": None,
        "meaning_en": "Donating wheat grains, jaggery, or copper vessels on Sunday helps calm afflicted solar heat and dispels paternal friction.",
        "meaning_ta": "கோதுமை, வெல்லம் அல்லது செப்புப் பாத்திரங்களை ஏழை எளியவர்களுக்கு ஞாயிற்றுக்கிழமை தானமாக வழங்குவது சூரியனின் உக்கிரத்தைத் தணிக்கும்.",
        "procedure_en": "Donate 1.25 kg of whole wheat grains and jaggery wrapped in red cloth to a needy student or temple kitchen on Sunday afternoon.",
        "procedure_ta": "ஞாயிற்றுக்கிழமை மதியம் 1.25 கிலோ முழு கோதுமை மற்றும் வெல்லத்தை சிவப்புத் துணியில் வைத்து ஏழை மாணவர்களுக்கோ அல்லது கோயில் அன்னதானத்திற்கோ வழங்கவும்.",
        "japa_count": None,
        "timing_recommendation_en": "Sunday afternoon between 12:00 PM and 1:30 PM",
        "timing_recommendation_ta": "ஞாயிற்றுக்கிழமை நண்பகல் 12:00 முதல் 1:30 மணிக்குள்",
        "source_code": "PHALADEEPIKA",
        "is_pacification_only": True,
        "problem_slugs": ["workplace_conflicts", "chronic_health_issues", "ancestral_karmic_blocks"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_MOON_MANTRA_01",
        "graha": "moon",
        "remedy_type": "mantra",
        "name_en": "Chandra Namaha Mantra",
        "name_ta": "சந்திர நமஹ மந்திரம்",
        "description_en": "Traditional devotional prayer calming emotional turbulence, cooling anxiety, and healing mother-child relationships.",
        "description_ta": "மன அமைதி, நிம்மதியான உறக்கம், தாய்-சேய் நலம் மற்றும் உணர்ச்சி சமநிலையைப் பெற சந்திர பகவானைப் போற்றும் புனித மந்திரம்.",
        "deity_en": "Lord Chandra (Moon)",
        "deity_ta": "சந்திர பகவான்",
        "sanskrit_text": "ॐ सोमाय नमः ॥",
        "transliteration_iast": "oṃ somāya namaḥ ॥",
        "transliteration_ta": "ஓம் ஸோமாய நமஹ ॥",
        "meaning_en": "Salutations to Lord Soma (the Moon), the reservoir of nectar and guardian of the mind and emotions.",
        "meaning_ta": "அமிர்தத்தின் இருப்பிடமாகவும், மனோகாரகனாகவும் விளங்கும் சந்திர பகவானுக்கு எனது வணக்கங்கள்.",
        "procedure_en": "Chant 108 times on Monday evening after moonrise facing North or North-West with serene focus.",
        "procedure_ta": "திங்கட்கிழமை மாலை சந்திரன் உதித்த பின் வடக்கு அல்லது வடமேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Monday evenings after moonrise",
        "timing_recommendation_ta": "திங்கட்கிழமை மாலை சந்திர தரிசனத்திற்குப் பின்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["mental_anxiety_depression", "marital_discord", "recurrent_nightmares", "relocation_adjustment_stress"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_MARS_MANTRA_01",
        "graha": "mars",
        "remedy_type": "mantra",
        "name_en": "Mangal Namaha Mantra",
        "name_ta": "செவ்வாய் நமஹ மந்திரம்",
        "description_en": "Parashari prayer invoking Mars for courage, blood vitality, resolving land property hurdles, and mitigating Kuja dosha friction.",
        "description_ta": "தைரியம், நிலம் சார்ந்த சொத்து நன்மைகள், ரத்த நலம் மற்றும் செவ்வாய் தோஷ அமைதிக்காக அங்காரகனைப் போற்றும் மந்திரம்.",
        "deity_en": "Lord Mangal (Mars / Murugan)",
        "deity_ta": "செவ்வாய் பகவான் / முருகப் பெருமான்",
        "sanskrit_text": "ॐ भौमाय नमः ॥",
        "transliteration_iast": "oṃ bhaumāya namaḥ ॥",
        "transliteration_ta": "ஓம் பௌமாய நமஹ ॥",
        "meaning_en": "Salutations to Mars, the son of the Earth, the granter of vigor, resilience, and victorious valor.",
        "meaning_ta": "பூமிதேவியின் மைந்தனும், அளப்பரிய வீரமும் பலமும் அருள்பவருமான அங்காரக பகவானைப் பணிகிறேன்.",
        "procedure_en": "Sit on a red mat facing South or East on Tuesday morning. Light a ghee lamp and chant 108 times.",
        "procedure_ta": "செவ்வாய்க்கிழமை காலை தெற்கு அல்லது கிழக்கு நோக்கி சிவப்பு விரிப்பில் அமர்ந்து நெய் தீபமேற்றி 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Tuesday mornings",
        "timing_recommendation_ta": "செவ்வாய்க்கிழமை காலை வேளையில்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["land_property_disputes", "house_construction_hurdles", "marriage_delay", "vitality_low_energy"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_MERCURY_MANTRA_01",
        "graha": "mercury",
        "remedy_type": "mantra",
        "name_en": "Budha Namaha Mantra",
        "name_ta": "புதன் நமஹ மந்திரம்",
        "description_en": "Classical prayer for intellectual acuity, commercial success, speech eloquence, and nervous balance.",
        "description_ta": "கல்வித் தேர்ச்சி, நினைவாற்றல், வாக்கு வன்மை, வியாபார வளர்ச்சி மற்றும் புத்தி கூர்மைக்குரிய புதன் பகவான் மந்திரம்.",
        "deity_en": "Lord Budha (Mercury / Vishnu)",
        "deity_ta": "புதன் பகவான் / விஷ்ணு பெருமான்",
        "sanskrit_text": "ॐ बुधाय नमः ॥",
        "transliteration_iast": "oṃ budhāya namaḥ ॥",
        "transliteration_ta": "ஓம் புதாய நமஹ ॥",
        "meaning_en": "Reverence to Lord Budha, the presiding lord of intelligence, discrimination, trade, and learning.",
        "meaning_ta": "ஞானம், விவேகம் மற்றும் வர்த்தகத்தின் அதிபதியாகத் திகழும் புதன் பகவானுக்கு எனது நமஸ்காரங்கள்.",
        "procedure_en": "Chant 108 times on Wednesday morning facing North. Offering tulasi leaves to Lord Vishnu enhances auspicious results.",
        "procedure_ta": "புதன்கிழமை காலை வடக்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும். பெருமாளுக்குத் துளசி சமர்ப்பித்து வழிபடுவது கூடுதல் நற்பலன் தரும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Wednesday mornings",
        "timing_recommendation_ta": "புதன்கிழமை காலை வேளையில்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["academic_focus_memory", "business_setbacks", "speech_communication_blocks", "exam_competitive_hurdles"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_JUPITER_MANTRA_01",
        "graha": "jupiter",
        "remedy_type": "mantra",
        "name_en": "Guru Namaha Mantra",
        "name_ta": "குரு நமஹ மந்திரம்",
        "description_en": "Sacred invocation of Brihaspati for wisdom, progeny blessings, marital happiness, and divine grace.",
        "description_ta": "ஞானம், குருவருள், சுப காரிய வெற்றி, புத்திர பாக்கியம் மற்றும் திருமண யோகத்திற்குரிய குரு பகவான் போற்றி.",
        "deity_en": "Lord Brihaspati (Jupiter / Dakshinamurthy)",
        "deity_ta": "குரு பகவான் / தட்சிணாமூர்த்தி",
        "sanskrit_text": "ॐ बृहस्पतये नमः ॥",
        "transliteration_iast": "oṃ bṛhaspataye namaḥ ॥",
        "transliteration_ta": "ஓம் பிருஹஸ்பதயே நமஹ ॥",
        "meaning_en": "Salutations to Brihaspati, the preceptor of the Gods, master of Vedic scriptures, and embodiment of grace.",
        "meaning_ta": "தேவர்களின் குருவும், சகல சாஸ்திர ஞானங்களின் இருப்பிடமுமான பிரகஸ்பதி பகவானைப் பணிகிறேன்.",
        "procedure_en": "Chant 108 times on Thursday morning wearing yellow or clean white attire facing North-East.",
        "procedure_ta": "வியாழக்கிழமை காலை வடகிழக்கு நோக்கி அமர்ந்து மஞ்சள் அல்லது வெண்ணிற ஆடை அணிந்து 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Thursday mornings during sunrise",
        "timing_recommendation_ta": "வியாழக்கிழமை அதிகாலை",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["progeny_childbirth_delay", "higher_education_obstacles", "financial_instability", "marriage_delay"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_VENUS_MANTRA_01",
        "graha": "venus",
        "remedy_type": "mantra",
        "name_en": "Shukra Namaha Mantra",
        "name_ta": "சுக்கிர நமஹ மந்திரம்",
        "description_en": "Classical prayer harmonizing relationships, attracting material comforts, artistic fulfillment, and marital joy.",
        "description_ta": "களத்திர தோஷ நிவர்த்தி, தாம்பத்திய அன்யோன்யம், கலைத் திறன் மற்றும் சகல ஐஸ்வர்யங்களுக்கும் உரிய சுக்கிர மந்திரம்.",
        "deity_en": "Lord Shukra (Venus / Mahalakshmi)",
        "deity_ta": "சுக்கிர பகவான் / மகாலட்சுமி",
        "sanskrit_text": "ॐ शुक्राय नमः ॥",
        "transliteration_iast": "oṃ śukrāya namaḥ ॥",
        "transliteration_ta": "ஓம் சுக்ராய நமஹ ॥",
        "meaning_en": "Reverence to Shukracharya, the brilliant master of aesthetic beauty, harmony, and material opulence.",
        "meaning_ta": "சகல கலைகளின் வித்தகரும், இன்பம் மற்றும் அழகின் நாயகருமான சுக்கிர பகவானுக்கு எனது நமஸ்காரங்கள்.",
        "procedure_en": "Chant 108 times on Friday evening or morning facing East or South-East after a clean bath.",
        "procedure_ta": "வெள்ளிக்கிழமை காலை அல்லது அந்தி மாலையில் கிழக்கு நோக்கி அமர்ந்து மன அமைதியுடன் 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Friday mornings or twilight",
        "timing_recommendation_ta": "வெள்ளிக்கிழமை காலை அல்லது அந்தி மாலை",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["marital_discord", "relationship_breakdown", "wealth_accumulation_block", "marriage_delay"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SATURN_MANTRA_01",
        "graha": "saturn",
        "remedy_type": "mantra",
        "name_en": "Shani Namaha Mantra",
        "name_ta": "சனி நமஹ மந்திரம்",
        "description_en": "Vedic prayer invoking Saturn for humility, patient perseverance, relief from Sade Sati distress, and longevity.",
        "description_ta": "ஏழரைச் சனி, அஷ்டமச் சனி ஆகியவற்றின் பாதிப்புகளைத் தணித்து, பொறுமை, நீதி மற்றும் நீண்ட ஆயுளை அருளும் சனி பகவான் மந்திரம்.",
        "deity_en": "Lord Shani (Saturn)",
        "deity_ta": "சனீஸ்வர பகவான்",
        "sanskrit_text": "ॐ शनैश्चराय नमः ॥",
        "transliteration_iast": "oṃ śanaiścarāya namaḥ ॥",
        "transliteration_ta": "ஓம் சனைச்சராய நமஹ ॥",
        "meaning_en": "Salutations to the slow-moving Lord Shani, the dispenser of karmic justice and guardian of discipline and truth.",
        "meaning_ta": "நீதியின் பாற்பட்டு கர்ம வினைகளுக்கு ஏற்ப பலன்களை அருளும் சனீஸ்வர பகவானைப் பணிந்து வணங்குகிறேன்.",
        "procedure_en": "Recite 108 times on Saturday evening facing West. Lighting a sesame oil lamp under a peepal tree or at home is recommended.",
        "procedure_ta": "சனிக்கிழமை மாலை மேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும். நல்லெண்ணெய் தீபமேற்றி வழிபடுவது நலம் பயக்கும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Saturday evenings after sunset",
        "timing_recommendation_ta": "சனிக்கிழமை மாலை சூரிய அஸ்தமனத்திற்குப் பின்",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["career_delay", "chronic_debt_burden", "litigation_court_cases", "bone_joint_mobility"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SATURN_CHARITY_01",
        "graha": "saturn",
        "remedy_type": "charity",
        "name_en": "Shani Daan (Black Sesame & Blanket Charity)",
        "name_ta": "சனி தானம் (கருப்பு எள் மற்றும் அன்னதானம்)",
        "description_en": "Strictly for pacifying malefic Saturn when afflicting dusthanas. Never prescribe for Taurus/Libra where Saturn is Yogakaraka.",
        "description_ta": "சனி பகவான் அசுப ஆதிபத்தியம் பெற்று துன்பம் தரும் போது மட்டும் செய்ய வேண்டிய பரிகார தானம். ரிஷபம்/துலாம் யோககாரகர்களுக்கு இத்தானம் பொருந்தாது.",
        "deity_en": "Lord Shani",
        "deity_ta": "சனீஸ்வர பகவான்",
        "sanskrit_text": None,
        "transliteration_iast": None,
        "transliteration_ta": None,
        "meaning_en": "Donating black sesame seeds, mustard oil, or warm dark blankets to elderly, disabled, or needy workers on Saturday.",
        "meaning_ta": "கருப்பு எள், நல்லெண்ணெய், கருப்பு வஸ்திரம் அல்லது போர்வைகளை முதியோர் மற்றும் மாற்றுத்திறனாளிகளுக்கு வழங்குதல்.",
        "procedure_en": "Distribute sesame-mixed cooked rice or warm blankets to poor laborers or elderly destitute persons on Saturday afternoon.",
        "procedure_ta": "சனிக்கிழமை மதியம் ஏழை எளிய தொழிலாளர்கள் அல்லது முதியவர்களுக்கு எள் கலந்த உணவு அல்லது போர்வை தானம் செய்யவும்.",
        "japa_count": None,
        "timing_recommendation_en": "Saturday afternoons",
        "timing_recommendation_ta": "சனிக்கிழமை நண்பகல் வேளையில்",
        "source_code": "PHALADEEPIKA",
        "is_pacification_only": True,
        "problem_slugs": ["chronic_debt_burden", "litigation_court_cases", "past_life_karmic_burdens"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_RAHU_MANTRA_01",
        "graha": "rahu",
        "remedy_type": "mantra",
        "name_en": "Rahu Namaha Mantra",
        "name_ta": "ராகு நமஹ மந்திரம்",
        "description_en": "Protective mantra pacifying psychological illusion, addictions, unexpected shocks, and Rahu dasha turbulence.",
        "description_ta": "மாயை, பிரமைகள், திடீர் தடைகள், விஷ பயம் மற்றும் ராகு தசை-புத்திகளின் கெடுபலன்களைத் தணிக்கும் சாந்தி மந்திரம்.",
        "deity_en": "Lord Rahu (Goddess Durga)",
        "deity_ta": "ராகு பகவான் / துர்க்கை அம்மன்",
        "sanskrit_text": "ॐ राहवे नमः ॥",
        "transliteration_iast": "oṃ rāhave namaḥ ॥",
        "transliteration_ta": "ஓம் ராகவே நமஹ ॥",
        "meaning_en": "Salutations to Lord Rahu, who tests the soul through worldly illusion and grants deep spiritual insight upon pacification.",
        "meaning_ta": "உலகியல் மாயைகளை விலக்கி, துர்க்கையின் அருளால் தெளிந்த ஞானத்தை நல்கும் ராகு பகவானை வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times on Saturday or during Rahu Kalam on Tuesday/Friday facing South-West.",
        "procedure_ta": "செவ்வாய் அல்லது வெள்ளிக்கிழமை ராகு காலத்தில் அல்லது சனிக்கிழமை மாலை தென்மேற்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Rahu Kalam or Saturday twilight",
        "timing_recommendation_ta": "ராகு காலம் அல்லது சனிக்கிழமை அந்தி வேளை",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["fear_negative_energies", "job_loss_instability", "speculation_gambling_losses", "visa_immigration_delays"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_KETU_MANTRA_01",
        "graha": "ketu",
        "remedy_type": "mantra",
        "name_en": "Ketu Namaha Mantra",
        "name_ta": "கேது நமஹ மந்திரம்",
        "description_en": "Spiritual prayer invoking Ketu for detachment from past burdens, inner liberation (Moksha), and occult wisdom.",
        "description_ta": "மோட்ச காரகனான கேது பகவானின் அருளைப் பெற்று, பூர்வ ஜென்ம வினைகளைத் தீர்த்து, ஆன்மீக ஞானம் பெற உதவும் மந்திரம்.",
        "deity_en": "Lord Ketu (Lord Ganesha)",
        "deity_ta": "கேது பகவான் / விநாயகப் பெருமான்",
        "sanskrit_text": "ॐ केतवे नमः ॥",
        "transliteration_iast": "oṃ ketave namaḥ ॥",
        "transliteration_ta": "ஓம் கேதவே நமஹ ॥",
        "meaning_en": "Reverence to Lord Ketu, the flag of spiritual detachment, dispeller of illusions, and bestower of ultimate liberation.",
        "meaning_ta": "பற்றற்ற நிலையை அருளி, உலகப் பிணிகளிலிருந்து ஆன்மாவை விடுவித்து முக்தி அளிக்கும் கேது பகவானுக்கு நமஸ்காரங்கள்.",
        "procedure_en": "Chant 108 times on Tuesday morning facing North-East after offering Durva grass to Lord Ganesha.",
        "procedure_ta": "செவ்வாய்க்கிழமை காலை விநாயகருக்கு அருகம்புல் சமர்ப்பித்த பின் வடகிழக்கு நோக்கி அமர்ந்து 108 முறை ஜபம் செய்யவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Tuesday mornings at dawn",
        "timing_recommendation_ta": "செவ்வாய்க்கிழமை விடியற்காலை",
        "source_code": "BPHS",
        "is_pacification_only": False,
        "problem_slugs": ["spiritual_stagnation", "past_life_karmic_burdens", "recurrent_nightmares", "ancestral_karmic_blocks"],
        "is_published": True,
        "verification_status": "verified",
    },
]


# ─── Repository Functions ───────────────────────────────────────────────────

def list_problem_taxonomy(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List problem taxonomy items with dual-mode Supabase and in-memory fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("remedies_problem_taxonomy").select("*")
            if category:
                query = query.eq("category", category)
            res = query.order("display_order").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    # Fallback to local verified taxonomy
    items = VERIFIED_PROBLEM_TAXONOMY
    if category:
        items = [p for p in items if p["category"] == category]
    return sorted(items, key=lambda x: x.get("display_order", 0))


def get_problem_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Fetch single problem taxonomy item by slug."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedies_problem_taxonomy").select("*").eq("slug", slug).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    return TAXONOMY_BY_SLUG.get(slug)


def list_remedies(
    graha: Optional[str] = None,
    remedy_type: Optional[str] = None,
    problem_slug: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List remedies with optional filters."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("remedies_catalog").select("*").eq("is_published", True)
            if graha:
                query = query.eq("graha", graha)
            if remedy_type:
                query = query.eq("remedy_type", remedy_type)
            if problem_slug:
                query = query.contains("problem_slugs", [problem_slug])
            res = query.order("code").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    # Fallback to local verified catalog
    results = VERIFIED_REMEDIES
    if graha:
        results = [r for r in results if r["graha"] == graha]
    if remedy_type:
        results = [r for r in results if r["remedy_type"] == remedy_type]
    if problem_slug:
        results = [r for r in results if problem_slug in r.get("problem_slugs", [])]

    return results


def get_remedy_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Fetch single remedy by unique code."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedies_catalog").select("*").eq("code", code).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    for r in VERIFIED_REMEDIES:
        if r["code"] == code:
            return r
    return None


def list_navagraha_temples(graha: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Tamil Navagraha temples."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("navagraha_temples").select("*").eq("is_published", True)
            if graha:
                query = query.eq("graha", graha)
            res = query.order("code").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    results = VERIFIED_TEMPLES
    if graha:
        results = [t for t in results if t["graha"] == graha]
    return results


def get_temple_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Fetch single temple by code."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("navagraha_temples").select("*").eq("code", code).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    for t in VERIFIED_TEMPLES:
        if t["code"] == code:
            return t
    return None


def list_source_references() -> List[Dict[str, Any]]:
    """List canonical classical sources."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedy_source_references").select("*").eq("is_published", True).execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    return VERIFIED_SOURCES


# ─── In-Memory Store for Remedy Reports (Fallback / Testing) ─────────────────
IN_MEMORY_REMEDY_REPORTS: Dict[str, Dict[str, Any]] = {}


def save_report_record(
    user_id: str,
    horoscope_id: str,
    input_data_fingerprint: str,
    analysis_snapshot: Dict[str, Any],
    review_status: str = "draft",
    astrologer_notes: Optional[str] = None,
    selected_remedy_codes: Optional[List[str]] = None,
    language: str = "en",
    person_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist an astrologer-reviewed remedy report to Supabase or fallback store."""
    import uuid
    report_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    record = {
        "id": report_id,
        "user_id": str(user_id),
        "horoscope_id": str(horoscope_id),
        "person_name": person_name,
        "input_data_fingerprint": input_data_fingerprint,
        "review_status": review_status,
        "astrologer_notes": astrologer_notes,
        "selected_remedy_codes": selected_remedy_codes or [],
        "language": language,
        "analysis_snapshot": analysis_snapshot,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedy_reports").insert(record).execute()
            if res.data and len(res.data) > 0:
                saved = res.data[0]
                IN_MEMORY_REMEDY_REPORTS[saved["id"]] = saved
                return saved
        except Exception as err:
            logger.warning(
                "Supabase insert into 'remedy_reports' failed (%s); storing in fallback in-memory registry.",
                err,
            )

    logger.info("Persisted remedy report %s into in-memory fallback store.", report_id)
    IN_MEMORY_REMEDY_REPORTS[report_id] = record
    return record


def get_report_record(
    report_id: str,
    user_id: str,
    is_admin: bool = False,
) -> Optional[Dict[str, Any]]:
    """Retrieve single remedy report ensuring strict server-side ownership verification."""
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedy_reports").select("*").eq("id", report_id).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                if is_admin or str(row.get("user_id")) == str(user_id):
                    return row
                return None
        except Exception as err:
            logger.warning(
                "Supabase query for 'remedy_reports' (id=%s) failed (%s); checking in-memory fallback store.",
                report_id,
                err,
            )

    # Check local fallback
    row = IN_MEMORY_REMEDY_REPORTS.get(report_id)
    if row:
        if is_admin or str(row.get("user_id")) == str(user_id):
            return row
    return None


def list_report_records(
    user_id: str,
    horoscope_id: Optional[str] = None,
    is_admin: bool = False,
) -> List[Dict[str, Any]]:
    """List remedy reports for user or specific horoscope."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("remedy_reports").select("*")
            if not is_admin:
                query = query.eq("user_id", str(user_id))
            if horoscope_id:
                query = query.eq("horoscope_id", str(horoscope_id))
            res = query.order("created_at", desc=True).execute()
            if res.data is not None:
                return res.data
        except Exception as err:
            logger.warning(
                "Supabase list query for 'remedy_reports' failed (%s); listing from in-memory fallback store.",
                err,
            )

    # Fallback to in-memory records
    results = []
    for r in IN_MEMORY_REMEDY_REPORTS.values():
        if not is_admin and str(r.get("user_id")) != str(user_id):
            continue
        if horoscope_id and str(r.get("horoscope_id")) != str(horoscope_id):
            continue
        results.append(r)
    return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)


class RemedyRepository:
    """Repository interface for remedy knowledge base data access."""

    async def get_all_problem_taxonomies(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return list_problem_taxonomy(category)

    async def get_problem_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        return get_problem_by_slug(slug)

    async def get_all_remedies(
        self,
        graha: Optional[str] = None,
        remedy_type: Optional[str] = None,
        problem_slug: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return list_remedies(graha=graha, remedy_type=remedy_type, problem_slug=problem_slug)

    async def get_remedy_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return get_remedy_by_code(code)

    async def get_all_navagraha_temples(self, graha: Optional[str] = None) -> List[Dict[str, Any]]:
        return list_navagraha_temples(graha)

    async def get_temple_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return get_temple_by_code(code)

    async def get_all_source_references(self) -> List[Dict[str, Any]]:
        return list_source_references()

    async def save_report(
        self,
        user_id: str,
        horoscope_id: str,
        input_data_fingerprint: str,
        analysis_snapshot: Dict[str, Any],
        review_status: str = "draft",
        astrologer_notes: Optional[str] = None,
        selected_remedy_codes: Optional[List[str]] = None,
        language: str = "en",
        person_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return save_report_record(
            user_id=user_id,
            horoscope_id=horoscope_id,
            input_data_fingerprint=input_data_fingerprint,
            analysis_snapshot=analysis_snapshot,
            review_status=review_status,
            astrologer_notes=astrologer_notes,
            selected_remedy_codes=selected_remedy_codes,
            language=language,
            person_name=person_name,
        )

    async def get_report_by_id(
        self,
        report_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> Optional[Dict[str, Any]]:
        return get_report_record(report_id, user_id, is_admin)

    async def list_reports(
        self,
        user_id: str,
        horoscope_id: Optional[str] = None,
        is_admin: bool = False,
    ) -> List[Dict[str, Any]]:
        return list_report_records(user_id, horoscope_id, is_admin)


remedy_repository = RemedyRepository()


