"""Remedy Knowledge Base Repository and Data Access Layer.

Handles data access for Problem Taxonomy, Remedy Catalog, Source References,
and Tamil Navagraha Temples. Implements seamless dual-tier access: attempts
Supabase REST queries via Service Role client first, gracefully falling back
to verified, canonical in-memory registries for development, testing, and offline modes.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple

_REMEDY_CACHE: Dict[str, Tuple[float, Any]] = {}
_REMEDY_CACHE_TTL = 300.0  # 5 minutes in-memory cache
from datetime import datetime, timezone
from app.services.auth_service import get_supabase_client
from app.services.remedy_engine.taxonomy import VERIFIED_PROBLEM_TAXONOMY, TAXONOMY_BY_SLUG

logger = logging.getLogger(__name__)

# ─── Canonical Classical Source References ────────────────────────────────────
VERIFIED_SOURCES: List[Dict[str, Any]] = [
    {
        "code": "IBN_BAZ_FATWA_RUQYAH",
        "title_en": "Islamic Legal Rulings on Magic and Astrology (Sooniyam & Jothidam)",
        "title_sa": "சூனியம் மற்றும் சோதிடம் குறித்த இஸ்லாமிய சட்ட விளக்கம்",
        "author": "Grand Mufti Sheikh Abdul Aziz ibn Abdullah ibn Baz (ரஹிமஹுல்லாஹ்)",
        "tradition": "islamic_shariah_ruqyah",
        "canonical_status": "authoritative_fatwa",
        "description": "Authoritative Islamic legal treatise and Sunnah Ruqyah guidance by former Grand Mufti of Saudi Arabia on protection and curative healing from sorcery (Sihr), evil eye, and astrology.",
        "is_published": True,
    },
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
    {
        "code": "SANNU_AHMED_RITUALS",
        "title_en": "Vedic Astrology Rituals & Remedies: Powerful Rituals & Remedies for a Fulfilling Life",
        "title_sa": "वैदिकज्योतिषसद्कर्मप्रायश्चित्तविधिः",
        "author": "Sannu Ahmed (Jyotish Sadhak)",
        "tradition": "vedic_tantric_syncretic",
        "canonical_status": "modern_shastra_commentary",
        "description": "Comprehensive spiritual compendium synthesizing BPHS, Jaimini Sutras, Shams al-Ma'arif, Picatrix, and Tantra on threefold karma, nakshatra doshas, and sacred geometry.",
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
    # ─── Sannu Ahmed Rituals & Remedies: Vedic Beeja Shanti Mantras ───────────
    {
        "code": "REM_SANNU_SUN_BEEJA",
        "graha": "sun",
        "remedy_type": "mantra",
        "name_en": "Surya Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "சூரிய வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Potent vibrational code from Sannu Ahmed's Vedic Astrology Rituals & Remedies to calm ego distortions and heal paternal/leadership karma.",
        "description_ta": "அகந்தையை அடக்கி, தந்தை வழி கர்ம வினைகளைத் தீர்த்து ஆன்ம பலம் அருளும் வேத பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Surya (Aditya)",
        "deity_ta": "சூரிய பகவான்",
        "sanskrit_text": "ॐ घृणिः सूर्याय नमः ॥",
        "transliteration_iast": "oṃ ghṛṇiḥ sūryāya namaḥ ॥",
        "transliteration_ta": "ஓம் கிருணிஃ சூர்யாய நமஹ ॥",
        "meaning_en": "Salutations to the luminous Lord Surya, the supreme soul of the cosmos who illuminates truth and burns away karmic ego.",
        "meaning_ta": "பிரபஞ்சத்திற்கு ஒளியூட்டி அகந்தையை அழிக்கும் சூரிய பகவானை வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times at sunrise during Sun hora facing East. Multiplied 100x when chanted on Sunday or Krittika/Uttaraphalguni/Uttarashadha days.",
        "procedure_ta": "ஞாயிற்றுக்கிழமை சூரிய ஓரையில் கிழக்கு நோக்கி அமர்ந்து 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Sunday sunrise during Sun Hora",
        "timing_recommendation_ta": "ஞாயிறு விடியற்காலை சூரிய ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["career_delay", "workplace_conflicts", "spiritual_stagnation"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_MOON_BEEJA",
        "graha": "moon",
        "remedy_type": "mantra",
        "name_en": "Chandra Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "சந்திர வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Lunar frequency code from Sannu Ahmed's manual to pacify emotional volatility, sleep disorders, and ancestral maternal karmas.",
        "description_ta": "மன அமைதியின்மை, தூக்கமின்மை மற்றும் தாயார் வழி கர்ம வினைகளைத் தணிக்கும் சந்திர பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Chandra (Soma)",
        "deity_ta": "சந்திர பகவான் / சோமதேவன்",
        "sanskrit_text": "ॐ सोमाय नमः ॥",
        "transliteration_iast": "oṃ somāya namaḥ ॥",
        "transliteration_ta": "ஓம் சோமாய நமஹ ॥",
        "meaning_en": "Salutations to Lord Soma, the divine ruler of the mind and provider of cooling cosmic nectar.",
        "meaning_ta": "மனதிற்கு அமைதியும் அமிர்தமும் தரும் சந்திர பகவானைப் பணிகிறேன்.",
        "procedure_en": "Chant 108 times at moonrise on Mondays, offering raw milk and white lotus petals in a silver bowl.",
        "procedure_ta": "திங்கட்கிழமை சந்திரன் உதிக்கும் வேளையில் வெள்ளிப் பாத்திரத்தில் பசும்பால் வைத்து 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Monday evening at Moonrise or Purnima",
        "timing_recommendation_ta": "திங்கள் அந்தி வேளை அல்லது பௌர்ணமி",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["marital_discord", "spiritual_stagnation"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_MARS_BEEJA",
        "graha": "mars",
        "remedy_type": "mantra",
        "name_en": "Mangala Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "செவ்வாய் வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Neutralizes blood karma, inward rage, land litigation, and marital friction per Sannu Ahmed's Tantric-Vedic system.",
        "description_ta": "கோபம், விபத்து பயம், நிலத் தகராறுகள் மற்றும் செவ்வாய் தோஷத்தைத் தணிக்கும் மந்திரம்.",
        "deity_en": "Lord Bhauma (Mangala)",
        "deity_ta": "செவ்வாய் பகவான்",
        "sanskrit_text": "ॐ कुं भौमाय नमः ॥",
        "transliteration_iast": "oṃ kuṃ bhaumāya namaḥ ॥",
        "transliteration_ta": "ஓம் கும் பௌமாய நமஹ ॥",
        "meaning_en": "Salutations to Lord Bhauma, the fiery celestial warrior; may his fierce energy be transmuted into righteous discipline.",
        "meaning_ta": "உக்கிரமான வீரத்தை நற்பண்பாக மாற்றும் செவ்வாய் பகவானை வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times on Tuesday facing South with a copper lamp filled with sesame oil.",
        "procedure_ta": "செவ்வாய்க்கிழமை தெற்கு நோக்கி செம்பு விளக்கில் நல்லெண்ணெய் தீபமேற்றி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Tuesday during Mars Hora",
        "timing_recommendation_ta": "செவ்வாய் ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["marital_discord", "property_disputes", "litigation_court_cases"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_MERCURY_BEEJA",
        "graha": "mercury",
        "remedy_type": "mantra",
        "name_en": "Budha Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "புதன் வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Corrects fractured speech, deceitful speech karma, nervous agitation, and commercial stagnation.",
        "description_ta": "பேச்சுத்திறன், கல்வி வளர்ச்சி மற்றும் வணிகத் தடைகளை நீக்கும் புதன் பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Budha",
        "deity_ta": "புதன் பகவான்",
        "sanskrit_text": "ॐ बुधाय नमः ॥",
        "transliteration_iast": "oṃ budhāya namaḥ ॥",
        "transliteration_ta": "ஓம் புதாய நமஹ ॥",
        "meaning_en": "Reverence to Lord Budha, the god of intellect, logic, and eloquent speech.",
        "meaning_ta": "மதிநுட்பமும் நாவன்மையும் அருளும் புதன் பகவானைப் போற்றுகிறேன்.",
        "procedure_en": "Chant 108 times on Wednesday morning facing North after offering green moong dal to cows.",
        "procedure_ta": "புதன்கிழமை காலை பசுவிற்கு பச்சைப் பயறு வழங்கி வடக்கு நோக்கி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Wednesday during Mercury Hora",
        "timing_recommendation_ta": "புதன் ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["business_setbacks", "promotion_blocks"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_JUPITER_BEEJA",
        "graha": "jupiter",
        "remedy_type": "mantra",
        "name_en": "Brihaspati Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "குரு வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Heals broken guru lineage, spiritual disorientation, and financial blockages per Sannu Ahmed's remedial almanac.",
        "description_ta": "குரு சாப நிவர்த்தி, தர்ம சிந்தனை மற்றும் பொருளாதார சுபிட்சம் தரும் பிரகஸ்பதி பீஜ மந்திரம்.",
        "deity_en": "Lord Brihaspati (Guru)",
        "deity_ta": "பிருஹஸ்பதி / குரு பகவான்",
        "sanskrit_text": "ॐ बृहस्पतये नमः ॥",
        "transliteration_iast": "oṃ bṛhaspataye namaḥ ॥",
        "transliteration_ta": "ஓம் பிருஹஸ்பதயே நமஹ ॥",
        "meaning_en": "Salutations to Brihaspati, supreme guru of the gods, embodiment of sattvic wisdom and divine law.",
        "meaning_ta": "தேவர்களின் குருவாகிய பிருஹஸ்பதி பகவானை அடிபணிந்து வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times on Thursday morning facing North-East with yellow flowers and a ghee lamp.",
        "procedure_ta": "வியாழக்கிழமை காலை வடகிழக்கு நோக்கி மஞ்சள் மலர்கள் சாற்றி நெய் தீபமேற்றி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Thursday at dawn (Guru Hora)",
        "timing_recommendation_ta": "வியாழன் விடியற்காலை குரு ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["spiritual_stagnation", "business_setbacks", "marriage_delay"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_VENUS_BEEJA",
        "graha": "venus",
        "remedy_type": "mantra",
        "name_en": "Shukra Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "சுக்கிர வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Purifies toxic desire patterns, sensual addictions, and resolves unfinished romantic contracts (Rinanubandha).",
        "description_ta": "காதல் ஏமாற்றங்கள், தாம்பத்திய விரிசல் மற்றும் தவறான ஆசைகளை நீக்கும் சுக்கிர பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Shukra (Bhargava)",
        "deity_ta": "சுக்கிர பகவான்",
        "sanskrit_text": "ॐ शुक्राय नमः ॥",
        "transliteration_iast": "oṃ śukrāya namaḥ ॥",
        "transliteration_ta": "ஓம் சுக்ராய நமஹ ॥",
        "meaning_en": "Salutations to Lord Shukracarya, the master of esoteric wisdom, beauty, and refined life force.",
        "meaning_ta": "அழகும் கலை ஞானமும் அருளும் சுக்கிராச்சாரியாரை வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times on Friday morning facing East with white flowers, white cloth, and pure cow ghee.",
        "procedure_ta": "வெள்ளிக்கிழமை காலை கிழக்கு நோக்கி வெண்மலர் சாற்றி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Friday sunrise during Venus Hora",
        "timing_recommendation_ta": "வெள்ளி விடியற்காலை சுக்கிர ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["marriage_delay", "marital_discord"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_SATURN_BEEJA",
        "graha": "saturn",
        "remedy_type": "mantra",
        "name_en": "Shani Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "சனி வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Expiates long-due karmic debts, chronic poverty, delays, and labor suffering under Saturn's purifying chisel.",
        "description_ta": "ஏழரைச் சனி, அஷ்டமச் சனி மற்றும் தொடர் கர்ம தடைகளைத் தணிக்கும் சனி பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Shani (Sanaischara)",
        "deity_ta": "சனீஸ்வர பகவான்",
        "sanskrit_text": "ॐ शं शनैश्चराय नमः ॥",
        "transliteration_iast": "oṃ śaṃ śanaiścarāya namaḥ ॥",
        "transliteration_ta": "ஓம் சம் சனைச்சராய நமஹ ॥",
        "meaning_en": "Reverence to Lord Sanaiscara, the slow-moving lord of time and divine justice who refines the soul through discipline.",
        "meaning_ta": "நீதி வழுவாமல் காலத்தின் நாயகனாக விளங்கும் சனீஸ்வர பகவானைப் பணிகிறேன்.",
        "procedure_en": "Chant 108 times on Saturday evening facing West after lighting a black sesame oil lamp.",
        "procedure_ta": "சனிக்கிழமை மாலை மேற்கு நோக்கி எள் தீபமேற்றி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Saturday twilight or Saturn Hora",
        "timing_recommendation_ta": "சனி அந்தி வேளை அல்லது சனி ஓரை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["career_delay", "chronic_debt_burden", "past_life_karmic_burdens"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_RAHU_BEEJA",
        "graha": "rahu",
        "remedy_type": "mantra",
        "name_en": "Rahu Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "ராகு வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Breaks worldly illusions, cravings, addictions, and dissolves ancestral serpent curses (Sarpa Dosha).",
        "description_ta": "மாயை, பிரமைகள் மற்றும் நாக தோஷங்களை நீக்கும் ராகு பீஜ சாந்தி மந்திரம்.",
        "deity_en": "Lord Rahu",
        "deity_ta": "ராகு பகவான்",
        "sanskrit_text": "ॐ रां राहवे नमः ॥",
        "transliteration_iast": "oṃ rāṃ rāhave namaḥ ॥",
        "transliteration_ta": "ஓம் ராம் ராகவே நமஹ ॥",
        "meaning_en": "Salutations to Lord Rahu, the cosmic shadow that drives desires and awakens the soul through disillusionment.",
        "meaning_ta": "மாயையை அகற்றி ஞானத்தை அருளும் ராகு பகவானை வணங்குகிறேன்.",
        "procedure_en": "Chant 108 times during Rahu Kalam on Tuesday/Friday or Saturday facing South-West.",
        "procedure_ta": "ராகு காலத்தில் தென்மேற்கு நோக்கி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Rahu Kalam or Saturday twilight",
        "timing_recommendation_ta": "ராகு காலம்",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["fear_negative_energies", "job_loss_instability"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_SANNU_KETU_BEEJA",
        "graha": "ketu",
        "remedy_type": "mantra",
        "name_en": "Ketu Vedic Beeja Shanti Mantra (Sannu Ahmed Tradition)",
        "name_ta": "கேது வேத பீஜ சாந்தி மந்திரம்",
        "description_en": "Cleanses past spiritual guilt, mysterious phantom pains, isolation, and awakens genuine Moksha aspiration.",
        "description_ta": "ஆன்மீகத் தெளிவு, விவரிக்க முடியாத பயங்களை நீக்கி மோட்ச மார்க்கம் காட்டும் கேது பீஜ மந்திரம்.",
        "deity_en": "Lord Ketu",
        "deity_ta": "கேது பகவான்",
        "sanskrit_text": "ॐ कें केतवे नमः ॥",
        "transliteration_iast": "oṃ keṃ ketave namaḥ ॥",
        "transliteration_ta": "ஓம் கேம் கேதவே நமஹ ॥",
        "meaning_en": "Salutations to Lord Ketu, who severs material bondage and opens the third eye of transcendent release.",
        "meaning_ta": "பந்தங்களை அறுத்து முக்தி அருளும் கேது பகவானைப் போற்றுகிறேன்.",
        "procedure_en": "Chant 108 times on Tuesday at dawn facing North-East after offering Durva grass to Ganesha.",
        "procedure_ta": "செவ்வாய்க்கிழமை காலை வடகிழக்கு நோக்கி 108 முறை ஜபிக்கவும்.",
        "japa_count": 108,
        "timing_recommendation_en": "Tuesday at dawn",
        "timing_recommendation_ta": "செவ்வாய் விடியற்காலை",
        "source_code": "SANNU_AHMED_RITUALS",
        "is_pacification_only": True,
        "problem_slugs": ["spiritual_stagnation", "past_life_karmic_burdens"],
        "is_published": True,
        "verification_status": "verified",
    },

    # ─── BPHS Chapter 83 & 84 Canonical Vedic Remedies & Shanti ─────────────
    {
        "code": "REM_BPHS_GRAHA_SHANTI_HOMAM",
        "graha": "universal",
        "remedy_type": "ritual",
        "name_en": "Maharishi Parashara Canonical Navagraha Shanti Homam",
        "name_ta": "மகரிஷி பராசர நவகிரக சாந்தி ஹோமம்",
        "description_en": "Canonical Vedic Graha Shanti per BPHS Ch. 84 utilizing dedicated sacrificial woods (Samidhas) and exact scriptural mantra counts for planetary pacification.",
        "description_ta": "பிருஹத் பராசர ஹோரா சாஸ்திரம் அத்தியாயம் 84-ன்படி நவகிரகங்களின் தோஷம் நீங்க குறிப்பிட்ட சமித்து மரங்கள் மற்றும் சாஸ்திரோக்த ஜப எண்ணிக்கையுடன் செய்யப்படும் மகா சாந்தி ஹோமம்.",
        "deity_en": "Navagraha Mandala (Adhidevata & Pratyadhidevata)",
        "deity_ta": "நவகிரக மண்டலம்",
        "sanskrit_text": "ॐ ब्रह्मा मुरारिस्त्रिपुरान्तकारी भानुः शशी भूमिसुतो बुधश्च । गुरुश्च शुक्रः शनिराहुकेतवः सर्वे ग्रहाः शान्तिकरा भवन्तु ॥",
        "transliteration_iast": "oṃ brahmā murāristripurāntakārī bhānuḥ śaśī bhūmisuto budhaśca | guruśca śukraḥ śanirāhuketavaḥ sarve grahāḥ śāntikarā bhavantu ||",
        "transliteration_ta": "ஓம் பிரம்மா முராரிஸ்திரிபுராந்தகாரீ பானு: சசி பூமிசுதோ புதஸ்ச | குருஸ்ச சுக்ர: சனி ராகு கேதவ: சர்வே கிரஹா: சாந்திகரா பவந்து ||",
        "meaning_en": "May Brahma, Vishnu, Shiva, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu grant auspicious peace and dispelling of all afflictions.",
        "meaning_ta": "மும்மூர்த்திகளும் நவகிரகங்களும் ஒன்றிணைந்து ஜாதகரின் அனைத்து தோஷங்களையும் போக்கி நல்வாழ்வையும் அமைதியையும் அருளட்டும்.",
        "procedure_en": "Perform homam using canonical woods: Arka (Sun: 7000 japas), Palasha (Moon: 11000), Khadira (Mars: 11000), Apamarga (Mercury: 9000), Ashwattha (Jupiter: 19000), Udumbara (Venus: 16000), Shami (Saturn: 23000), Durva (Rahu: 18000), and Kusha (Ketu: 17000).",
        "procedure_ta": "சூரியனுக்கு எருக்கு (7000 ஜபம்), சந்திரனுக்கு புரசு (11000), செவ்வாய்க்கு கருங்காலி (11000), புதனுக்கு நாயுருவி (9000), குருவுக்கு அரசு (19000), சுக்கிரனுக்கு அத்தி (16000), சனிக்கு வன்னி (23000), ராகுவுக்கு அருகம்புல் (18000), கேதுவுக்கு தர்ப்பை (17000) சமித்துகளுடன் முறைப்படி ஹோமம் செய்யவும்.",
        "japa_count": 122000,
        "timing_recommendation_en": "Auspicious Shukla Paksha muhurta or during planetary dasha transitions",
        "timing_recommendation_ta": "சுப சுக்கில பட்ச முகூர்த்தம் அல்லது தசா-புக்தி சந்தி காலங்களில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["past_life_karmic_burdens", "chronic_health_issues", "fear_negative_energies", "litigation_court_cases"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_SARPA",
        "graha": "rahu",
        "remedy_type": "ritual",
        "name_en": "Sarpa Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "சர்ப்ப சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Classical prayaschitta for past-life serpent curse afflicting 5th house and progeny per BPHS Ch. 83 Slokas 13-17.",
        "description_ta": "பிருஹத் பராசர ஹோரா சாஸ்திரம் அத்தியாயம் 83-ன்படி முற்பிறவி நாக தோஷத்தால் புத்திர பாக்கிய தடை ஏற்பட்டால் செய்ய வேண்டிய சாஸ்திர பரிகாரம்.",
        "deity_en": "Lord Nagaraja & Lord Subrahmanya",
        "deity_ta": "நாகராஜர் & சுப்பிரமணிய சுவாமி",
        "sanskrit_text": "ॐ नमोऽस्तु सर्पेभ्यो ये के च पृथिवीमनु । ये अन्तरिक्षे ये दिवि तेभ्यः सर्पेभ्यो नमः ॥",
        "transliteration_iast": "oṃ namo'stu sarpebhyo ye ke ca pṛthivīmanu | ye antarikṣe ye divi tebhyaḥ sarpebhyo namaḥ ||",
        "transliteration_ta": "ஓம் நமோஸ்து சர்ப்பேப்யோ யே கே ச பிருதிவீமனு | யே அந்தரிக்ஷே யே திவி தேப்ய: சர்ப்பேப்யோ நம: ||",
        "meaning_en": "Salutations to all divine serpents residing in earth, the atmospheric space, and the heavens.",
        "meaning_ta": "பூமி, அந்தரிக்ஷம், சுவர்க்கம் எங்கும் உறையும் நாக தேவதைகளுக்கு எனது மனமார்ந்த நமஸ்காரங்கள்.",
        "procedure_en": "Donate a golden serpent idol (Naga Pratima) with a cow and land/grains to a righteous priest; perform Setu Snana at Rameshwaram and Naga Prathishta.",
        "procedure_ta": "தங்க நாக பிரதிமை செய்து முறைப்படி பூஜித்து பசு தானம் செய்தல், ராமேஸ்வரம் சேது ஸ்நானம் செய்து நாக பிரதிஷ்டை செய்தல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Nag Panchami, Shravana Shukla Panchami, or Rohini/Ashlesha Nakshatra",
        "timing_recommendation_ta": "நாக பஞ்சமி அல்லது ரோகிணி/ஆயில்ய நட்சத்திர தினங்களில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "fear_negative_energies"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_PITRU",
        "graha": "sun",
        "remedy_type": "ritual",
        "name_en": "Pitru Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "பித்ரு சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Canonical prayaschitta for paternal ancestry curse causing childlessness and career setbacks per BPHS Ch. 83 Slokas 24-28.",
        "description_ta": "முற்பிறவியில் தந்தை வழி பித்ருக்களை புறக்கணித்ததால் ஏற்படும் சாபத்திற்கு பராசரர் அருளிய விமோசன பரிகாரம்.",
        "deity_en": "Pitru Devatas & Lord Rudra",
        "deity_ta": "பித்ரு தேவதைகள் & ருத்ர பெருமான்",
        "sanskrit_text": "ॐ पितृभ्यः स्वधायिभ्यः स्वधा नमः पितामहेभ्यः स्वधायिभ्यः स्वधा नमः ॥",
        "transliteration_iast": "oṃ pitṛbhyaḥ svadhāyibhyaḥ svadhā namaḥ pitāmahebhyaḥ svadhāyibhyaḥ svadhā namaḥ ||",
        "transliteration_ta": "ஓம் பித்ருப்ய: ஸ்வதாயிப்ய: ஸ்வதா நம: பிதாமஹேப்ய: ஸ்வதாயிப்ய: ஸ்வதா நம: ||",
        "meaning_en": "Reverence to the ancestors and forefathers who accept the sacred offering of Svadha.",
        "meaning_ta": "நமது பித்ருக்களுக்கும் முப்பாட்டனார்களுக்கும் இந்த சிரார்த்த தர்ப்பண நமஸ்காரங்கள் சேரட்டும்.",
        "procedure_en": "Perform Pinda Daan and Shraddha rites at Gaya or sacred pilgrimage ghats, sponsor Rudrabhisheka, and donate a milch cow with calf.",
        "procedure_ta": "கயாவில் அல்லது புண்ணிய நதிக்கரையில் பிண்ட தான சிரார்த்தம் செய்தல், ருத்ராபிஷேகம் மற்றும் கன்றுடன் கூடிய பசு தானம் வழங்குதல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Amavasya, Mahalaya Paksha, or Father's shraddha thithi",
        "timing_recommendation_ta": "அமாவாசை, மகாளய பட்சம் அல்லது தந்தையின் திதி நாளில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "career_delay"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_MATRU",
        "graha": "moon",
        "remedy_type": "ritual",
        "name_en": "Matru Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "மாத்ரு சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Canonical remedy for mother's curse affecting family peace and progeny per BPHS Ch. 83 Slokas 35-39.",
        "description_ta": "தாயாரை அவமதித்ததால் வரும் மாத்ரு சாபத்தை நீக்க பராசர முனிவர் வகுத்த சேது ஸ்நான மற்றும் வெள்ளிப் பசு தான பரிகாரம்.",
        "deity_en": "Mother Goddess & Lord Shiva",
        "deity_ta": "அன்னை பராசக்தி & சிவபெருமான்",
        "sanskrit_text": "ॐ मातृभ्यो नमः । मातॄणां पावनं तीर्थं सर्वपापप्रणाशनम् ॥",
        "transliteration_iast": "oṃ mātṛbhyo namaḥ | mātṝṇāṃ pāvanaṃ tīrthaṃ sarvapāpapraṇāśanam ||",
        "transliteration_ta": "ஓம் மாத்ருப்யோ நம: | மாத்ரூணாம் பாவனம் தீர்த்தம் சர்வபாபப்ரணாசனம் ||",
        "meaning_en": "Reverence to mothers whose maternal love is the holiest waters cleansing all sins.",
        "meaning_ta": "அனைத்துப் பாவங்களையும் போக்கும் புனித தீர்த்தமாகிய தாய்மார்களுக்கு எனது வணக்கங்கள்.",
        "procedure_en": "Take sacred bath at Rameshwaram Setu, donate a silver cow vessel filled with pure milk to worthy scholars, and serve elderly mothers.",
        "procedure_ta": "ராமேஸ்வரத்தில் சேது ஸ்நானம் செய்து, பால் நிரப்பிய வெள்ளிப் பசு உருவத்தை தானம் செய்தல் மற்றும் முதிய தாய்மார்களுக்கு உணவளித்தல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Pournami (Full Moon) or Somavara (Monday)",
        "timing_recommendation_ta": "பௌர்ணமி அல்லது திங்கட்கிழமைகளில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "mental_anxiety_depression"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_BHRATRI",
        "graha": "mars",
        "remedy_type": "ritual",
        "name_en": "Bhratri Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "ப்ராத்ரு (சகோதர) சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Prescribed atonement for past-life enmity with brothers afflicting Mars and 3rd/5th houses per BPHS Ch. 83 Slokas 45-48.",
        "description_ta": "முற்பிறவியில் உடன் பிறந்த சகோதரர்களுக்கு இழைத்த துரோகத்தினால் ஏற்படும் தோஷத்தை நீக்கும் ஸ்ரீ ஹரிவம்ச புராண பாராயண பரிகாரம்.",
        "deity_en": "Lord Sri Krishna & Lord Lakshmana",
        "deity_ta": "ஸ்ரீ கிருஷ்ணர் & லட்சுமண சுவாமி",
        "sanskrit_text": "ॐ नमो भगवते वासुदेवाय ॥",
        "transliteration_iast": "oṃ namo bhagavate vāsudevāya ||",
        "transliteration_ta": "ஓம் நமோ பகவதே வாசுதேவாய ||",
        "meaning_en": "Reverence to Lord Vasudeva Krishna, the protector of siblings and reconciler of all kin.",
        "meaning_ta": "சகோதர ஒற்றுமையை அருளும் பகவான் வாசுதேவ கிருஷ்ணருக்கு நமஸ்காரங்கள்.",
        "procedure_en": "Listen to the recitation of sacred Harivamsa Purana, plant fruitful trees, and distribute food and gifts to young boys and brothers on Tuesdays.",
        "procedure_ta": "ஹரிவம்ச புராணத்தை சிரவணம் செய்தல், செவ்வாய்க்கிழமை தான தர்மங்கள் செய்தல் மற்றும் மரக்கன்றுகள் நடுதல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Tuesday or Krishna Janmashtami / Vishnu Jayanti",
        "timing_recommendation_ta": "செவ்வாய்க்கிழமை அல்லது கிருஷ்ண ஜெயந்தி தினத்தில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "property_litigation_land_disputes"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_BRAHMANA",
        "graha": "jupiter",
        "remedy_type": "ritual",
        "name_en": "Brahmana / Guru Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "பிரம்ம சாப / குரு சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Canonical prayaschitta for disrespecting preceptors, priests, or spiritual teachers per BPHS Ch. 83 Slokas 62-67.",
        "description_ta": "முற்பிறவியில் குரு, ஆன்மீக அறிஞர்களை நிந்தித்ததால் வரும் பிரம்ம சாபத்தை நீக்க பராசரர் அருளிய காயத்ரி அநுஷ்டானம்.",
        "deity_en": "Lord Dakshinamurthy & Lord Brihaspati",
        "deity_ta": "ஸ்ரீ தட்சிணாமூர்த்தி & குரு பகவான்",
        "sanskrit_text": "ॐ गुरवे नमः । ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात् ॥",
        "transliteration_iast": "oṃ gurave namaḥ | oṃ bhūrbhuvaḥ svaḥ tatsaviturvareṇyaṃ bhargo devasya dhīmahi dhiyo yo naḥ pracodayāt ||",
        "transliteration_ta": "ஓம் குரவே நம: | ஓம் பூர்புவஸ்வ: தத்ஸவிதுர்வரேண்யம் பர்கோ தேவஸ்ய தீமஹி தியோ யோ ந: ப்ரசோதயாத் ||",
        "meaning_en": "Salutations to the Supreme Guru; may the radiant cosmic sun illuminate our higher intellect.",
        "meaning_ta": "ஜகத்குருவாகிய தட்சிணாமூர்த்தியை வணங்குகிறேன்; காயத்ரி மகா மந்திரம் நமது புத்தியை நல்வழிப்படுத்தட்டும்.",
        "procedure_en": "Undertake Chandrayana vrata or 10,000 Gayatri japas; donate gold, books, and yellow garments, and feed learned Vedic scholars.",
        "procedure_ta": "காயத்ரி மகா மந்திரத்தை 10,000 முறை ஜபித்தல், தட்சிணாமூர்த்திக்கு மஞ்சள் வஸ்திரம் சாற்றுதல் மற்றும் ஆன்மீக ஆசிரியர்களுக்கு பாதபூஜை செய்து தானம் வழங்குதல்.",
        "japa_count": 10000,
        "timing_recommendation_en": "Guruvara (Thursday) or Guru Purnima",
        "timing_recommendation_ta": "வியாழக்கிழமை அல்லது குரு பூர்ணிமா தினத்தில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "spiritual_stagnation"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_PATNI",
        "graha": "venus",
        "remedy_type": "ritual",
        "name_en": "Patni Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "பத்னி (மனைவி) சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Classical atonement for forsaking or tormenting an innocent chaste spouse in past lives per BPHS Ch. 83 Slokas 74-77.",
        "description_ta": "முற்பிறவியில் மனைவியை கைவிட்டதால் அல்லது துன்புறுத்தியதால் ஏற்படும் பத்னி சாபத்தை நீக்க லட்சுமி-நாராயண பூஜை மற்றும் கன்யாதான பரிகாரம்.",
        "deity_en": "Goddess Lakshmi & Lord Narayana",
        "deity_ta": "ஸ்ரீ லக்ஷ்மி நாராயணர்",
        "sanskrit_text": "ॐ श्रीं ह्रीं क्लीं श्री महालक्ष्म्यै नमः ॥",
        "transliteration_iast": "oṃ śrīṃ hrīṃ klīṃ śrī mahālakṣmyai namaḥ ||",
        "transliteration_ta": "ஓம் ஸ்ரீம் ஹ்ரீம் க்லீம் ஸ்ரீ மஹாலக்ஷ்ம்யை நம: ||",
        "meaning_en": "Reverence to Supreme Mother Mahalakshmi, the source of marital grace, domestic harmony, and auspicious fortune.",
        "meaning_ta": "தாம்பத்திய ஒற்றுமையையும் இல்லற மகிழ்ச்சியையும் அருளும் ஸ்ரீ மஹாலக்ஷ்மி தாயாருக்கு நமஸ்காரங்கள்.",
        "procedure_en": "Sponsor or assist in a poor girl's marriage (Kanyadaan), donate an idol of Lakshmi-Narayana with silk garments and silver ornaments, and honor women in the household.",
        "procedure_ta": "ஏழைப் பெண்ணின் திருமணத்திற்கு மாங்கல்யம் அல்லது சீர்வரிசை உதவி செய்தல் (கன்யாதான புண்ணியம்), லக்ஷ்மி நாராயணர் சிலை தானம் செய்தல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Shukravara (Friday) or Akshaya Tritiya",
        "timing_recommendation_ta": "வெள்ளிக்கிழமை அல்லது அட்சய திருதியை தினத்தில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "marital_friction_frequent_quarrels", "past_life_karmic_burdens"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_BPHS_SHAPA_PRETHA",
        "graha": "saturn",
        "remedy_type": "ritual",
        "name_en": "Pretha Shapa Prayaschitta (BPHS Ch. 83)",
        "name_ta": "ப்ரேத சாப சாந்தி பரிகாரம் (அத். 83)",
        "description_en": "Prescribed rites for curses stemming from unperformed funeral ceremonies of neglected departed souls per BPHS Ch. 83 Slokas 82-87.",
        "description_ta": "மரணமடைந்த உறவினர்களுக்கு அந்திமக் கிரியைகள் செய்யாமல் விட்டதால் ஏற்படும் பிரேத தோஷத்திற்கு பராசரர் அருளிய ஸ்ரீமத் பாகவத சப்தாஹ பரிகாரம்.",
        "deity_en": "Lord Narayana & Lord Yama Dharmaraja",
        "deity_ta": "ஸ்ரீ நாராயணர் & எம தர்மராஜர்",
        "sanskrit_text": "ॐ नमो भगवते महापुरुषाय सर्वगुणसङ्ख्यानायाऽनन्तायाव्यक्ताय नमः ॥",
        "transliteration_iast": "oṃ namo bhagavate mahāpuruṣāya sarvaguṇasaṅkhyānāyā'nantāyāvyaktāya namaḥ ||",
        "transliteration_ta": "ஓம் நமோ பகவதே மகாபுருஷாய சர்வகுணஸங்க்யானாயாநந்தாயாவ்யக்தாய நம: ||",
        "meaning_en": "Salutations to the infinite supreme Being who liberates all trapped souls into eternal peace.",
        "meaning_ta": "அனைத்து ஆன்மாக்களுக்கும் முக்தியையும் அமைதியையும் அருளும் மகாபுருஷனாகிய பரம்பொருளை வணங்குகிறேன்.",
        "procedure_en": "Organize or participate in Srimad Bhagavata Saptaha recitation, perform Gaya Shraddha, feed crows and orphan children, and donate a black cow or land.",
        "procedure_ta": "ஸ்ரீமத் பாகவத சப்தாஹ பாராயணம் நடத்துதல், கயா பிண்ட தானம், காக்கைகளுக்கும் ஆதரவற்றோருக்கும் உணவளித்தல்.",
        "japa_count": 1008,
        "timing_recommendation_en": "Mahalaya Amavasya or Saturday",
        "timing_recommendation_ta": "மகாளய அமாவாசை அல்லது சனிக்கிழமைகளில்",
        "source_code": "BPHS",
        "is_pacification_only": True,
        "problem_slugs": ["childbirth_delay", "past_life_karmic_burdens", "fear_negative_energies"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_ISLAM_RUQYAH_SIDR_01",
        "graha": "universal",
        "remedy_type": "ruqyah",
        "name_en": "Sunnah Ruqyah with 7 Green Sidr (Lote) Leaves Water Treatment",
        "name_ta": "7 பச்சை இலந்தை இலை ஷரீஆ ருக்யா சிகிச்சை (சூனியம் & செய்வினை நீங்க)",
        "description_en": "Authoritative Prophetic Ruqyah prescribed by classical scholars and Grand Mufti Sheikh Ibn Baz for breaking black magic, witchcraft, and severe evil eye using 7 crushed green Sidr (lote) leaves in water with Quranic recitations.",
        "description_ta": "அஷ்ஷெய்க் இப்னு பாஸ் (ரஹ்) மற்றும் முன்னோர்களான ஸலபுஸ்ஸாலிஹீன்கள் வழிகாட்டலில் 7 பச்சை இலந்தை இலைகளை அரைத்து நீரில் கலந்து அல்குர்ஆன் வசனங்களை ஓதி அருந்திக் குளிக்கும் சுன்னத்தான ஷரீஆ ருக்யா நிவாரண முறை.",
        "deity_en": "Allah Subhanahu Wa Ta'ala (Seeking refuge with the Lord of Mankind)",
        "deity_ta": "அல்லாஹ் (அகிலங்களை படைத்து பரிபாலிக்கும் ஏகன்)",
        "sanskrit_text": "وَأَوْحَيْنَا إِلَىٰ مُوسَىٰ أَنْ أَلْقِ عَصَاكَ ۖ فَإِذَا هِيَ تَلْقَفُ مَا يَأْفِكُونَ ۝ فَوَقَعَ الْحَقُّ وَبَطَلَ مَا كَانُوا يَعْمَلُونَ ۝ فَغُلِبُوا هُنَالِكَ وَانقَلَبُوا صَاغِرِينَ",
        "transliteration_iast": "Wa awhayna ila Musa an alqi 'asaka fa-idha hiya talqafu ma ya'fikoon. Fa-waqa'a al-haqqu wa batala ma kanoo ya'maloon. Fa-ghuliboo hunalika wanqalaboo saghireen.",
        "transliteration_ta": "வஅவ்ஹைனா இலா மூஸா அன் அல்கி அஸாக ஃபஇஃதா ஹிய தல்ஃகஃபு மா யஃபிகூன், ஃப வகஅல்ஹக்கு வபதல மா கானூ யஃமலூன், ஃபஃகுலிபூ ஹுனாலிக வன் கலபூ ஸாஃகிரீன்.",
        "meaning_en": "And We inspired to Moses: 'Throw your staff,' and at once it devoured what they were falsifying. So the truth was established, and that which they were doing was made void. And they were vanquished there and were made small. (Surah Al-A'raf 7:117-119)",
        "meaning_ta": "'உமது கைத்தடியை போடும்' என மூஸாவுக்கு நாம் வஹி அறிவித்தோம். அவர் அதனைக் கீழே போட்டதும் அது அவர்கள் பாம்பாக கற்பனை செய்தவற்றை விழுங்கிவிட்டது. உண்மை தெளிவாகிவிட்டது! அவர்கள் செய்தவை வீணாகிவிட்டன. அவர்கள் அங்கே தோற்கடிக்கப்பட்டு சிறுமையடைந்தார்கள்.",
        "procedure_en": "1. Take 7 green leaves of the Sidr (lote tree / Ziziphus) and crush them finely between stones. 2. Put into clean water sufficient for drinking and bathing. 3. Recite into the water with ritual purity (Wudu): Surah Al-Fatihah, Ayatul Kursi (2:255), Surah Al-Kafirun, Surah Al-Ikhlas (3x), Surah Al-Falaq (3x), Surah An-Nas (3x), the Moses magic verses (Al-A'raf 7:117-119, Yunus 10:79-82, Ta-Ha 20:65-69), and Prophetic duas ('Allahumma Rabban-naas adhhibil-ba's...' & 'Bismillahi arqeeka...'). 4. Drink 3 sips and bathe (ghusl) with the rest. Repeat daily until full cure is attained.",
        "procedure_ta": "1. ஏழு பச்சை இலந்தை இலைகளை எடுத்து நன்கு அரைத்து ஒரு பாத்திரத்தில் குளிப்பதற்கும் குடிப்பதற்கும் போதுமான நீரில் இடவும். 2. அந்த நீரில் அல்-ஃபாத்திஹா, ஆயதுல் குர்ஸி, அல்-காஃபிரூன், அல்-இஹ்லாஸ் (3 முறை), அல்-ஃபலக் (3 முறை), அந்-நாஸ் (3 முறை) மற்றும் ஸூறா அல்-அஃராப் (117-119), ஸூறா யூனுஸ் (79-82), ஸூறா தாஹா (65-69) ஆகிய சூனியம் முறிக்கும் வசனங்களையும் நபியவர்களின் துஆக்களையும் ஓதவும். 3. அதில் மூன்று மிடர்கள் அருந்திவிட்டு மீதி நீரால் குளிக்கவும். நோய் குணமாகும் வரை பல நாட்கள் செய்யலாம்.",
        "japa_count": 3,
        "timing_recommendation_en": "Morning after Fajr or after Asr prayer, performed in ritual purity (Wudu)",
        "timing_recommendation_ta": "உளூவுடன் சுத்தமாக இருந்து ஃபஜ்ர் அல்லது அஸர் தொழுகைக்குப் பின் ஓதி சிகிச்சை செய்தல் சிறந்தது",
        "source_code": "IBN_BAZ_FATWA_RUQYAH",
        "is_pacification_only": False,
        "problem_slugs": ["fear_negative_energies", "recurrent_nightmares", "past_life_karmic_burdens", "chronic_health_issues"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_ISLAM_DAILY_ADHKAR_02",
        "graha": "universal",
        "remedy_type": "prayer",
        "name_en": "Prophetic Fortress of Daily Protective Adhkar (Ayatul Kursi & Mu'awwidhat)",
        "name_ta": "தினசரி தற்காப்பு அரண் - ஆயதுல் குர்ஸி & முஅவ்விததைன் திக்ருகள்",
        "description_en": "Daily protective shield from the authentic Sunnah: Ayatul Kursi after obligatory prayers and at bedtime, the 3 Quls (Ikhlas, Falaq, Nas) 3 times morning & evening, and the Prophetic shield against all harms.",
        "description_ta": "ஒவ்வொரு தொழுகைக்குப் பிறகும், தூங்கும் போதும் ஆயதுல் குர்ஸி ஓதுதல், காலை மற்றும் மாலையில் குல்ஹுவல்லாஹு அஹத், குல்அவூது பிரப்பில் பலக், குல்அவூது பிரப்பிந்நாஸ் ஆகிய மூன்று ஸூராக்களை தலா 3 முறை ஓதி வருதல்.",
        "deity_en": "Allah (Al-Hafidh - The Supreme Protector)",
        "deity_ta": "அல்லாஹ் (அல்-ஹஃபீழ் - யாவற்றையும் பாதுகாப்பவன்)",
        "sanskrit_text": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
        "transliteration_iast": "Allahu la ilaha illa Huwa, Al-Hayyul-Qayyoom. La ta'khudhuhu sinatuw-wa la nawm. Lahu ma fis-samawati wa ma fil-ard...",
        "transliteration_ta": "அல்லாஹூ லாஇலாஹ இல்லா ஹுவல் ஹய்யுல் கய்யூம் லா தஃஹுதுஹு ஸினத்துவ்வலா நவம் லஹு மாபிஃஸ் ஸமாவாதி வமாபில் அர்ழி...",
        "meaning_en": "Allah! There is no deity except Him, the Ever-Living, the Sustainer of all existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. (Ayatul Kursi 2:255)",
        "meaning_ta": "அல்லாஹ்வைத் தவிர வணக்கத்திற்குரியவன் வேறு யாருமில்லை. அவன் என்றென்றும் உயிருடன் நிலைத்திருப்பவன். சிறுதூக்கமோ, உறக்கமோ அவனை ஆட்கொள்ளாது...",
        "procedure_en": "1. Recite Ayatul Kursi after each of the 5 daily obligatory prayers. 2. Recite Ayatul Kursi before going to sleep; an angel will guard you from Allah and no devil will approach until morning. 3. Recite Surahs Ikhlas, Falaq, and Nas 3 times after Fajr and 3 times after Maghrib. 4. Recite 3 times morning and evening: 'Bismillaahil-ladhee laa yadurru ma'asmihi shay'un fil-ardi wa laa fis-samaa'i wa huwas-Samee'ul-'Aleem'.",
        "procedure_ta": "1. கடமையான 5 நேரத் தொழுகைக்குப் பின் ஆயதுல் குர்ஸியை ஓதவும். 2. தூங்கும் போது ஆயதுல் குர்ஸியை ஓதினால் காலை வரை வானவர் பாதுகாப்பார்; ஷைத்தான் நெருங்க மாட்டான். 3. ஃபஜ்ர் மற்றும் மஃக்ரிப் தொழுகைக்குப் பின் 3 குல் ஸூராக்களை தலா 3 முறை ஓதவும். 4. காலையிலும் மாலையிலும் 3 முறை 'பிஸ்மில்லாஹில்லதீ லா யளுர்ரு மஅஸ்மிஹி ஷைஉன் ஃபில் அர்ழி வலா ஃபிஸ் ஸமாஇ வஹுவஸ் ஸமீஉல் அலீம்' ஓதி வரவும்.",
        "japa_count": 3,
        "timing_recommendation_en": "Morning after Fajr, Evening after Maghrib, and before bedtime",
        "timing_recommendation_ta": "தினமும் காலை ஃபஜ்ருக்குப் பின், மாலை மஃக்ரிபுக்கு பின், மற்றும் இரவில் படுக்கைக்குச் செல்லும் முன்",
        "source_code": "IBN_BAZ_FATWA_RUQYAH",
        "is_pacification_only": False,
        "problem_slugs": ["fear_negative_energies", "recurrent_nightmares", "mental_anxiety_depression"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_ISLAM_MARITAL_RUQYAH_03",
        "graha": "universal",
        "remedy_type": "ruqyah",
        "name_en": "Islamic Ruqyah for Marital Discord & Separation Sorcery (Sihr At-Tafreeq)",
        "name_ta": "கணவன்-மனைவி பிரிவினை & தாம்பத்திய சூனிய முறிவு ருக்யா",
        "description_en": "Specialized Shariah Ruqyah for couples afflicted by sudden marital repulsion, impotence caused by sorcery, or separation spells referenced in Surah Al-Baqarah (2:102), endorsed by Sheikh Ibn Baz.",
        "description_ta": "கணவன்-மனைவிக்கிடையே காரணமின்றி ஏற்படும் பிரிவு, வெறுப்பு, தாம்பத்திய உறவில் ஏற்படும் செய்வினைத் தடைகளை நீக்க அல்குர்ஆன் மற்றும் ஸுன்னாஹ் வழியிலான விசேஷ ருக்யா சிகிச்சை.",
        "deity_en": "Allah (Al-Wadood - The Source of All Love and Harmony)",
        "deity_ta": "அல்லாஹ் (அல்-வதூத் - அன்பையும் நல்லிணக்கத்தையும் பொழிபவன்)",
        "sanskrit_text": "فَيَتَعَلَّمُونَ مِنْهُمَا مَا يُفَرِّقُونَ بِهِ بَيْنَ الْمَرْءِ وَزَوْجِهِ ۚ وَمَا هُم بِضَارِّينَ بِهِ مِنْ أَحَدٍ إِلَّا بِإِذْنِ اللَّهِ",
        "transliteration_iast": "Fa-yata'allamoona minhuma ma yufarriqoona bihi baynal-mar'i wa zawjih. Wa ma hum bi-daarreena bihi min ahadin illa bi-idhnillah.",
        "transliteration_ta": "ஃபயதஅல்லமூன மின்ஹுமா மா யுஃபர்ரிகூன பிஹீ பைனல் மர்இ வ ஸவ்ஜிஹீ, வமா ஹும் பிளார்ரீன பிஹீ மின் அஹதின் இல்லா பிஇத்னில்லாஹ்.",
        "meaning_en": "They learned from them that by which they cause separation between a man and his wife. But they could not harm anyone through it except by permission of Allah. (Surah Al-Baqarah 2:102)",
        "meaning_ta": "கணவனுக்கும் மனைவிக்குமிடையில் எதைக்கொண்டு பிரிப்பார்களோ, அதை அவ்விருவரிடமிருந்து கற்றுக் கொண்டார்கள்; மேலும் அல்லாஹ்வின் அனுமதியின்றி அதைக்கொண்டு அவர்கள் ஒருவருக்குமே தீங்கிழைக்கக் கூடியவர்களாக இல்லை.",
        "procedure_en": "Prepare the 7 Sidr leaves water with Quranic recitations (Surah Al-Baqarah 102 & 255, Surah Yunus 81, Surah Ta-Ha 69, Surah Al-Falaq, Surah An-Nas). Both husband and wife drink 3 sips and bathe with the water. Recite Surah Al-Baqarah in the home continuously. Sincerely seek forgiveness (Tawbah) and avoid consulting occultists or soothsayers.",
        "procedure_ta": "7 பச்சை இலந்தை இலைகளை அரைத்து நீரில் இட்டு சூனிய முறிவு வசனங்களை ஓதி கணவனும் மனைவியும் 3 மிடர் பருகி மீதி நீரால் குளிக்கவும். வீட்டில் தொடர்ந்து ஸூறா அல்-பகரா ஓதவும். பாவமன்னிப்பு கோரி (தவ்பா) செய்து அல்லாஹ்விடம் இருவருடைய உள்ளங்களில் அன்பை ஏற்படுத்த துஆ செய்யவும்.",
        "japa_count": 3,
        "timing_recommendation_en": "Fridays or evenings after Maghrib, continued for 7 to 14 days",
        "timing_recommendation_ta": "வெள்ளிக்கிழமை அல்லது மாலையில் தொடங்கி தொடர்ந்து 7 முதல் 14 நாட்கள் செய்தல் உத்தமம்",
        "source_code": "IBN_BAZ_FATWA_RUQYAH",
        "is_pacification_only": False,
        "problem_slugs": ["marital_friction_frequent_quarrels", "marriage_delay_recurrent", "fear_negative_energies"],
        "is_published": True,
        "verification_status": "verified",
    },
    {
        "code": "REM_ISLAM_JINN_AFFLICTION_04",
        "graha": "universal",
        "remedy_type": "ruqyah",
        "name_en": "Quranic Protection from Jinn Affliction, Sleep Paralysis & Night Terrors",
        "name_ta": "ஜின் தீண்டுதல், தூக்கக் கலக்கம் & கெட்ட கனவுகளுக்கான குர்ஆன் பாதுகாப்பு",
        "description_en": "Classical Islamic healing protocol for jinn possession, psychic disturbances, night terrors, and sleep paralysis outlined in Sheikh Ibn Baz's commentary on Surah Al-Baqarah 275 and authentic Hadiths.",
        "description_ta": "மனித உடலில் ஜின் புகுந்து ஏற்படுத்தும் சோர்வு, பயம், கெட்ட கனவுகள் மற்றும் மனக்குழப்பங்களை நீக்க அல்குர்ஆன் ஆயத்துக்களை ஓதி ஊதும் சுன்னத்தான முறை.",
        "deity_en": "Allah (Al-Qaahir - The Irresistible Omnipotent)",
        "deity_ta": "அல்லாஹ் (அல்-காஹிர் - எவரையும் ஆட்கொள்ளும் மகா வல்லமையாளன்)",
        "sanskrit_text": "أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ غَضَبِهِ وَعِقَابِهِ وَشَرِّ عِبَادِهِ وَمِنْ هَمَزَاتِ الشَّيَاطِينِ وَأَنْ يَحْضُرُونِ",
        "transliteration_iast": "A'oodhu bi kalimaat-Illaahit-taammaati min ghadabihi wa 'iqaabihi wa sharri 'ibaadihi wa min hamazaatish-shayaateeni wa an yahduroon.",
        "transliteration_ta": "அஊது பிகலிமாதில்லாஹித்தாம்மாதி மின் கதபிஹீ வ இகாபிஹீ வ ஷர்ரி இபாதிஹீ வ மின் ஹமஸாதிஷ் ஷயாதீனி வ அன் யஹ்ளுரூன்.",
        "meaning_en": "I seek refuge in the perfect words of Allah from His anger, His punishment, the evil of His slaves, and from the whisperings of the devils and their presence.",
        "meaning_ta": "அல்லாஹ்வின் கோபம், தண்டனை, அவனது படைப்புகளின் தீங்குகள் மற்றும் ஷைத்தான்களின் ஊசலாட்டங்கள், அவை என்னை அணுகுவதை விட்டும் அல்லாஹ்வின் பரிபூரண வார்த்தைகளைக் கொண்டு பாதுகாவல் தேடுகிறேன்.",
        "procedure_en": "Perform ablution (Wudu) before bed. Dust the bed 3 times reciting Bismillah. Cup the hands together, blow into them while reciting Surah Al-Ikhlas, Surah Al-Falaq, and Surah An-Nas, and wipe over the face and whole body 3 times as the Prophet (pbuh) did. Recite the last 2 verses of Surah Al-Baqarah and Ayatul Kursi.",
        "procedure_ta": "படுக்கைக்குச் செல்லும் முன் உளூ செய்து கொள்ளவும். படுக்கையை 3 முறை தட்டிவிட்டு பிஸ்மில்லாஹ் கூறவும். கைகளை குவித்து அதில் அல்-இஹ்லாஸ், அல்-ஃபலக், அந்-நாஸ் ஓதி ஊதி முகம் மற்றும் உடலின் முன்பகுதி முழுவதும் 3 முறை தடவிக்கொள்ளவும். ஸூறா பகராவின் கடைசி 2 வசனங்களையும் ஆயதுல் குர்ஸியையும் ஓதவும்.",
        "japa_count": 3,
        "timing_recommendation_en": "Every night before sleeping",
        "timing_recommendation_ta": "தினமும் இரவில் உறங்கச் செல்வதற்கு முன்",
        "source_code": "IBN_BAZ_FATWA_RUQYAH",
        "is_pacification_only": False,
        "problem_slugs": ["recurrent_nightmares", "fear_negative_energies", "mental_anxiety_depression"],
        "is_published": True,
        "verification_status": "verified",
    },
]

REMEDIES_BY_CODE: Dict[str, Dict[str, Any]] = {r["code"]: r for r in VERIFIED_REMEDIES}


# ─── Repository Functions ───────────────────────────────────────────────────

def list_problem_taxonomy(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List problem taxonomy items with dual-mode Supabase and in-memory fallback."""
    cache_key = f"taxonomy_{category or 'all'}"
    now = time.time()
    if cache_key in _REMEDY_CACHE:
        c_time, c_data = _REMEDY_CACHE[cache_key]
        if now - c_time < _REMEDY_CACHE_TTL:
            return c_data
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("remedies_problem_taxonomy").select("*")
            if category:
                query = query.eq("category", category)
            res = query.order("display_order").execute()
            if res.data and len(res.data) > 0:
                _REMEDY_CACHE[cache_key] = (now, res.data)
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
    cache_key = f"problem_slug_{slug}"
    now = time.time()
    if cache_key in _REMEDY_CACHE:
        c_time, c_data = _REMEDY_CACHE[cache_key]
        if now - c_time < _REMEDY_CACHE_TTL:
            return c_data
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("remedies_problem_taxonomy").select("*").eq("slug", slug).execute()
            if res.data and len(res.data) > 0:
                _REMEDY_CACHE[cache_key] = (now, res.data[0])
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
    cache_key = f"remedies_{graha}_{remedy_type}_{problem_slug}"
    now = time.time()
    if cache_key in _REMEDY_CACHE:
        c_time, c_data = _REMEDY_CACHE[cache_key]
        if now - c_time < _REMEDY_CACHE_TTL:
            return c_data
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
                remote_codes = set()
                for row in res.data:
                    local = REMEDIES_BY_CODE.get(row.get("code"))
                    if local:
                        for k, v in local.items():
                            if row.get(k) is None:
                                row[k] = v
                    remote_codes.add(row.get("code"))
                extras = [r for r in VERIFIED_REMEDIES if r["code"] not in remote_codes]
                if graha:
                    extras = [r for r in extras if r.get("graha") == graha]
                if remedy_type:
                    extras = [r for r in extras if r.get("remedy_type") == remedy_type]
                if problem_slug:
                    extras = [r for r in extras if problem_slug in r.get("problem_slugs", [])]
                return res.data + extras
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
                row = res.data[0]
                local = REMEDIES_BY_CODE.get(row.get("code"))
                if local:
                    for k, v in local.items():
                        if row.get(k) is None:
                            row[k] = v
                return row
        except Exception:
            pass

    for r in VERIFIED_REMEDIES:
        if r["code"] == code:
            return r
    return None


def list_navagraha_temples(graha: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Tamil Navagraha temples."""
    cache_key = f"temples_{graha or 'all'}"
    now = time.time()
    if cache_key in _REMEDY_CACHE:
        c_time, c_data = _REMEDY_CACHE[cache_key]
        if now - c_time < _REMEDY_CACHE_TTL:
            return c_data
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("navagraha_temples").select("*").eq("is_published", True)
            if graha:
                query = query.eq("graha", graha)
            res = query.order("code").execute()
            if res.data and len(res.data) > 0:
                _REMEDY_CACHE[cache_key] = (now, res.data)
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
                _REMEDY_CACHE[cache_key] = (now, res.data)
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
                remote_codes = {r.get("code") for r in res.data}
                extras = [s for s in VERIFIED_SOURCES if s["code"] not in remote_codes]
                return res.data + extras
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
    """List remedy reports for user or specific horoscope with fallback store merging."""
    combined_reports: Dict[str, Dict[str, Any]] = dict(IN_MEMORY_REMEDY_REPORTS)
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("remedy_reports").select("*")
            if not is_admin:
                query = query.eq("user_id", str(user_id))
            if horoscope_id:
                query = query.eq("horoscope_id", str(horoscope_id))
            res = query.order("created_at", desc=True).execute()
            if res.data:
                for row in res.data:
                    combined_reports[row["id"]] = row
        except Exception as err:
            logger.warning(
                "Supabase list query for 'remedy_reports' failed (%s); listing from in-memory fallback store.",
                err,
            )

    # Filter and sort matching records
    results = []
    for r in combined_reports.values():
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


