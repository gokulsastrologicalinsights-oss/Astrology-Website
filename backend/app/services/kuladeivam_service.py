"""Kuladeivam (குலதெய்வம்) Astrological Engine & Service.

Classical Tamil & Vedic Jyotish analysis of the 5th and 9th Bhavas,
D1 (Rasi) & D9 (Navamsha) divisional charts, planetary karakatwas,
deity gender, Grama vs Agamic category, temple direction,
and unknown Kuladeivam discovery rituals.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, time
import logging

from app.schemas.kuladeivam import (
    KuladeivamRequest,
    KuladeivamPrasannaRequest,
    DeityIndicator,
    TempleLandscape,
    KuladeivamDoshaAnalysis,
    UnknownDeityDiscoveryProtocol,
    HouseAnalysisDetails,
    KuladeivamResponse,
    UniversalRefugeTemple,
)
from app.services.ephemeris import calculate_full_horoscope
from app.services.jamakkol.calculator import calculate_jamakkol_prasanam
from app.services.varga_engine import calculate_varga_from_horoscope_dict

logger = logging.getLogger(__name__)

# Canonical Zodiac Signs (1-indexed)
ZODIAC_NAMES_TA = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்",
}

ZODIAC_NAMES_EN = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

GRAHA_NAMES_TA = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "இராகு",
    "Ketu": "கேது",
}

SIGN_TATTVA = {
    1: ("Agni (Fire)", "நெருப்பு (அக்னி தத்துவம்)"),
    2: ("Prithvi (Earth)", "நிலம் (பிருத்வி தத்துவம்)"),
    3: ("Vayu (Air)", "காற்று (வாயு தத்துவம்)"),
    4: ("Jala (Water)", "நீர் (ஜல தத்துவம்)"),
    5: ("Agni (Fire)", "நெருப்பு (அக்னி தத்துவம்)"),
    6: ("Prithvi (Earth)", "நிலம் (பிருத்வி தத்துவம்)"),
    7: ("Vayu (Air)", "காற்று (வாயு தத்துவம்)"),
    8: ("Jala (Water)", "நீர் (ஜல தத்துவம்)"),
    9: ("Agni (Fire)", "நெருப்பு (அக்னி தத்துவம்)"),
    10: ("Prithvi (Earth)", "நிலம் (பிருத்வி தத்துவம்)"),
    11: ("Vayu (Air)", "காற்று (வாயு தத்துவம்)"),
    12: ("Jala (Water)", "நீர் (ஜல தத்துவம்)"),
}

SIGN_GENDER = {
    1: ("Male", "ஆண் ராசி"),
    2: ("Female", "பெண் ராசி"),
    3: ("Male", "ஆண் ராசி"),
    4: ("Female", "பெண் ராசி"),
    5: ("Male", "ஆண் ராசி"),
    6: ("Female", "பெண் ராசி"),
    7: ("Male", "ஆண் ராசி"),
    8: ("Female", "பெண் ராசி"),
    9: ("Male", "ஆண் ராசி"),
    10: ("Female", "பெண் ராசி"),
    11: ("Male", "ஆண் ராசி"),
    12: ("Female", "பெண் ராசி"),
}

PLANET_DIRECTIONS = {
    "Sun": ("East", "கிழக்கு"),
    "Venus": ("South-East", "தென்கிழக்கு (அக்னி மூலை)"),
    "Mars": ("South", "தெற்கு"),
    "Rahu": ("South-West", "தென்மேற்கு (நிருதி மூலை)"),
    "Saturn": ("West", "மேற்கு"),
    "Moon": ("North-West", "வடமேற்கு (வாயு மூலை)"),
    "Mercury": ("North", "வடக்கு"),
    "Jupiter": ("North-East", "வடகிழக்கு (ஈசான்ய மூலை)"),
    "Ketu": ("North-East / Center", "வடகிழக்கு அல்லது மையப் பகுதி"),
}

DEITY_KNOWLEDGE_BASE = {
    "Sun": {
        "deity_name_ta": "ஸ்ரீ சிவபெருமான் / ருத்ரன் / வீரபத்திரர்",
        "deity_name_en": "Lord Shiva / Rudra / Veerabhadra / Surya Narayana",
        "category_ta": "ஆகம முறைப் பெருங்கோவில் தெய்வம்",
        "category_en": "Agamic / Vedic Temple Deity",
        "gender_ta": "ஆண் தெய்வம்",
        "gender_en": "Male Deity",
        "forms_ta": ["ஸ்ரீ காசி விஸ்வநாதர்", "ஸ்ரீ நடராஜ பெருமான்", "ஸ்ரீ வீரபத்திர சுவாமி", "ஸ்ரீ சூரிய நாராயணர்"],
        "forms_en": ["Kasi Viswanathar", "Nataraja Peruman", "Veerabhadra Swamy", "Surya Narayana"],
        "trees_ta": "வில்வ மரம், எருக்கு, வன்னி மரம்",
        "trees_en": "Vilvam (Bilva), Calotropis (Erukku), Vanni",
        "landscape_ta": "கிழக்கு நோக்கி அமைந்த தலம், மேட்டுப்பாங்கான வெட்டவெளி அல்லது பிரகாரமுடைய சிவன் கோவில்",
        "landscape_en": "East-facing temple, elevated terrain, or traditional Shiva sanctum",
        "desc_ta": "சூரியனின் ஆதிக்கத்தில் வரும் குலதெய்வம் சிவ அம்சம் பொருந்தியதாகும். சிவபெருமான், வீரபத்திரர் அல்லது சூரியனார் கோவில் வழிபாட்டு மரபு உங்கள் முன்னோர்களால் வழிவழியாகப் பின்பற்றப்பட்டுள்ளது.",
        "desc_en": "The Sun indicates a Solar-Shaivite ancestral lineage deity, such as Lord Shiva, Veerabhadra, or Surya Narayana with radiant, righteous protective grace.",
    },
    "Moon": {
        "deity_name_ta": "ஸ்ரீ மாரியம்மன் / பகவதி / ராஜராஜேஸ்வரி",
        "deity_name_en": "Sri Mariamman / Bhagavathi / Sri Raja Rajeshwari",
        "category_ta": "நாட்டுப்புற தாய் தெய்வம் / அம்மன் தலம்",
        "category_en": "Mother Goddess / Amman Shrine",
        "gender_ta": "பெண் தெய்வம் (அம்மன்)",
        "gender_en": "Female Deity (Amman / Devi)",
        "forms_ta": ["சமயபுரம் மாரியம்மன்", "பகவதி அம்மன்", "ஆற்றுப்படை அம்மன்", "கங்கா பரமேஸ்வரி", "பத்ரகாளி (சாந்த வடிவம்)"],
        "forms_en": ["Samayapuram Mariamman", "Bhagavathi Amman", "Riverside Amman", "Ganga Parameswari", "Bhadrakali (Sowmya)"],
        "trees_ta": "வேப்பமரம், மருத மரம், வில்வம்",
        "trees_en": "Neem tree (Vembu), Marudham, Vilvam",
        "landscape_ta": "ஆற்றங்கரை, குளத்தங்கரை, ஏரி அல்லது நீர்நிலை ஓரத்தில் வேப்பமர நிழலில் உள்ள தலம்",
        "landscape_en": "Near a waterbody (riverbank, pond, irrigation tank) under sacred neem trees",
        "desc_ta": "சந்திரனின் காரகத்துவத்தில் வரும் குலதெய்வம் கருணை மிகுந்த தாய் தெய்வமாகும். ஆற்றுப்படுக்கை, குளக்கரை அல்லது ஏரிக்கரையில் வேப்பமர நிழலில் குடிகொண்டுள்ள அம்மன் உங்கள் வம்சத்தைக் காக்கும் தெய்வம்.",
        "desc_en": "The Moon signifies a benevolent Mother Goddess (Amman / Bhagavathi) residing near water reservoirs, canals, or rivers under a sacred neem tree.",
    },
    "Mars": {
        "deity_name_ta": "ஸ்ரீ முருகப்பெருமான் / கருப்பசாமி / வீரபத்திரர்",
        "deity_name_en": "Lord Murugan / Subrahmanya / Karuppasamy / Bhairava",
        "category_ta": "வீரக்காவல் / மலைக்கோவில் தெய்வம்",
        "category_en": "Warrior Guardian / Hilltop Deity",
        "gender_ta": "ஆண் தெய்வம் (வீர வடிவம்)",
        "gender_en": "Male Deity (Warrior Protector)",
        "forms_ta": ["திருச்செந்தூர் முருகன்", "பழனி தண்டாயுதபாணி", "பதினெட்டாம்படி கருப்பசாமி", "சங்கலி கருப்பர்", "வைரவர்"],
        "forms_en": ["Tiruchendur Murugan", "Palani Dandayudhapani", "Pathinettampadi Karuppasamy", "Sangili Karuppar", "Bhairavar"],
        "trees_ta": "செண்பக மரம், மருத மரம், கருவேலம், கடம்ப மரம்",
        "trees_en": "Shenbagam, Kadamba, Marudham",
        "landscape_ta": "மலை, குன்று அல்லது தெற்கு திசையில் செம்மண் பூமியில் வாளேந்திய தோரணையில் அமைந்த தலம்",
        "landscape_en": "Hillock, elevated red-soil mound, or South-facing sword-bearing guardian shrine",
        "desc_ta": "செவ்வாயின் ஆதிக்கத்தில் வரும் குலதெய்வம் வீரமும் தீய சக்திகளை அழிக்கும் ஆற்றலும் கொண்டதாகும். முருகப்பெருமான் அல்லது காவல் தெய்வமான கருப்பசாமி உங்கள் வம்சத்தின் குலதெய்வமாக விளங்குகிறது.",
        "desc_en": "Mars indicates a powerful, fiery lineage deity: Lord Murugan/Kartikeya or Karuppasamy/Veerabhadra who destroys obstacles and fiercely protects the family line.",
    },
    "Mercury": {
        "deity_name_ta": "ஸ்ரீ மகாவிஷ்ணு / பெருமாள் / கிருஷ்ணன்",
        "deity_name_en": "Lord Maha Vishnu / Perumal / Venkatachalapathi / Krishna",
        "category_ta": "ஆகம முறை வைணவப் பெருங்கோவில்",
        "category_en": "Agamic Vaishnavite Temple Deity",
        "gender_ta": "ஆண் தெய்வம்",
        "gender_en": "Male Deity",
        "forms_ta": ["ஸ்ரீ வெங்கடாசலபதி", "ஸ்ரீ பார்த்தசாரதி", "ஸ்ரீ அரங்கநாதர்", "ஸ்ரீ வரதராஜப் பெருமாள்", "கண்ணபிரான்"],
        "forms_en": ["Tirupati Venkatachalapathi", "Parthasarathy", "Ranganatha Perumal", "Varadaraja Perumal", "Krishna"],
        "trees_ta": "துளசி மாடம், அரச மரம், நெல்லி மரம்",
        "trees_en": "Tulasi shrine, Sacred Fig (Arasa Maram), Amla (Nelli)",
        "landscape_ta": "பசுமையான வயல்வெளிகள் அல்லது ஊரின் நடுவே வடக்கு நோக்கி அமைந்த வைணவத் தலம்",
        "landscape_en": "Lush green agricultural plains or town center North-facing Vaishnava sanctum",
        "desc_ta": "புதனின் காரகத்தில் வரும் குலதெய்வம் சாத்வீக குணமும் வித்யா-செல்வ வரமும் அருளும் மகாவிஷ்ணு அல்லது பெருமாள் அம்சம். துளசி பரிமளிக்கும் வைணவ பாரம்பரியக் கோவில் உங்கள் முன்னோர்களால் வழிபடப்பட்டது.",
        "desc_en": "Mercury signifies Lord Maha Vishnu / Srinivasa Perumal, bringing intellectual wisdom, trade prosperity, and tranquil preservation to the lineage.",
    },
    "Jupiter": {
        "deity_name_ta": "ஸ்ரீ தட்சிணாமூர்த்தி / சிவபெருமான் / குரு பீடம்",
        "deity_name_en": "Lord Dakshinamurthy / Supreme Shiva / Kula Guru Peetham",
        "category_ta": "ஆகம சாஸ்திர ஞானத் தெய்வம்",
        "category_en": "Classical Vedic Knowledge Deity",
        "gender_ta": "ஆண் தெய்வம்",
        "gender_en": "Male Deity",
        "forms_ta": ["மேதாதட்சிணாமூர்த்தி", "அண்ணாமலையார்", "ஸ்ரீ ராகவேந்திரர்", "சதாசிவ பிரமேந்திரர்", "குல ஆச்சார்ய தலம்"],
        "forms_en": ["Dakshinamurthy", "Annamalaiyar", "Sri Raghavendra", "Sadashiva Brahmendra", "Ancestral Acharya Peetham"],
        "trees_ta": "ஆலமரம், வில்வ மரம், சந்தன மரம்",
        "trees_en": "Banyan Tree (Aala Maram), Vilvam, Sandalwood",
        "landscape_ta": "வடகிழக்கு (ஈசான்ய) மூலையில் பழமையான ஆலமரத்தடியில் அமைந்த ஞானத் தலம்",
        "landscape_en": "North-East (Ishanya) direction under ancient banyan trees or sacred grove",
        "desc_ta": "குருவின் அம்சத்தில் அமைந்த குலதெய்வம் பரம குருவான தட்சிணாமூர்த்தி, சிவபெருமான் அல்லது குடும்ப குருபரம்பரை ஆகும். இது குடும்பத்தில் தர்மத்தையும் சந்ததி விருத்தியையும் தழைக்கச் செய்யும்.",
        "desc_en": "Jupiter represents Lord Dakshinamurthy, Lord Shiva, or ancestral Guru Peethams that confer righteousness, offspring blessings, and spiritual elevation.",
    },
    "Venus": {
        "deity_name_ta": "ஸ்ரீ மகாலட்சுமி / காமாட்சி / அன்னபூரணி",
        "deity_name_en": "Goddess Mahalakshmi / Kamakshi Amman / Annapoornani",
        "category_ta": "மங்கல சௌபாக்ய தாய் தெய்வம்",
        "category_en": "Auspicious Mother Goddess / Sri Vidya",
        "gender_ta": "பெண் தெய்வம் (அம்மன்)",
        "gender_en": "Female Deity (Goddess of Prosperity)",
        "forms_ta": ["காஞ்சி காமாட்சி அம்மன்", "மதுரை மீனாட்சி அம்மன்", "ஸ்ரீ மகாலட்சுமி", "அன்னபூரணி", "ஸ்ரீ வித்யா லலிதாம்பிகை"],
        "forms_en": ["Kanchi Kamakshi", "Madurai Meenakshi", "Sri Mahalakshmi", "Annapoornani", "Lalithambika"],
        "trees_ta": "நந்தவன மலர்கள், நெல்லி மரம், மல்லிகை, பவளமல்லி",
        "trees_en": "Sacred flowering garden, Parijata, Nelli, Jasmine",
        "landscape_ta": "தென்கிழக்கு திசையில் மலர் நந்தவனம் அல்லது நீர்நிலைக்கு அருகாமையில் அமைந்த எழில்மிகு கோவில்",
        "landscape_en": "South-East direction near flowering groves or picturesque riverbanks",
        "desc_ta": "சுக்கிரனின் காரகத்துவத்தில் வரும் தெய்வம் சர்வ மங்கலங்களையும் அஷ்டலட்சுமி கடாட்சத்தையும் அருளும் ஸ்ரீ காமாட்சி, மீனாட்சி அல்லது மகாலட்சுமி வடிவம். பெண்களின் தாலி பாக்கியமும் குடும்ப செழிப்பும் இதனால் ஓங்கும்.",
        "desc_en": "Venus represents the auspicious Divine Mother (Kamakshi, Meenakshi, or Mahalakshmi), safeguarding marital bliss, family abundance, and domestic peace.",
    },
    "Saturn": {
        "deity_name_ta": "ஸ்ரீ அய்யனார் / தர்ம சாஸ்தா / முனீஸ்வரன்",
        "deity_name_en": "Lord Sastha / Ayyanar / Muneeswaran / Madurai Veeran",
        "category_ta": "பாரம்பரிய எல்லைக் காவல் / கிராம தேவதை",
        "category_en": "Village Boundary & Lineage Guardian",
        "gender_ta": "ஆண் தெய்வம் (காவல் தெய்வம்)",
        "gender_en": "Male Guardian Deity",
        "forms_ta": ["குல சாஸ்தா", "அடைக்கலம் காத்த அய்யனார்", "பாண்டி முனீஸ்வரன்", "மதுரை வீரன்", "சுடலை மாடன்"],
        "forms_en": ["Kula Sastha", "Adaikkalam Katha Ayyanar", "Pandi Muneeswaran", "Madurai Veeran", "Sudalai Madan"],
        "trees_ta": "ஆலமரம், புளிய மரம், வன்னி மரம், எட்டி மரம்",
        "trees_en": "Banyan Tree, Tamarind Tree (Puliya Maram), Vanni",
        "landscape_ta": "ஊர் எல்லை, பெரிய புளியமரம் அல்லது ஆலமரத்தடியில் திறந்தவெளியில் குதிரை வாகனத்துடன் கூடிய தலம்",
        "landscape_en": "Village boundary or open grove under banyan/tamarind trees with terracotta horse vahanas",
        "desc_ta": "சனியின் ஆதிக்கத்தில் வரும் குலதெய்வம் பரம்பரை காவல் தெய்வமான சாஸ்தா, அய்யனார், முனீஸ்வரன் அல்லது மதுரை வீரன் ஆகும். ஊர் எல்லையிலோ காட்டின் ஓரத்திலோ குதிரை மற்றும் பரிவார தெய்வங்களுடன் அருள்பாலிக்கும்.",
        "desc_en": "Saturn signifies classical ancestral guardian deities: Dharma Sastha, Ayyanar, Muneeswaran, or Madurai Veeran positioned at village frontiers with terracotta steed vahanas.",
    },
    "Rahu": {
        "deity_name_ta": "ஸ்ரீ நாகாத்தம்மன் / துர்க்கை / அங்காளம்மன்",
        "deity_name_en": "Sri Nagathamman / Goddess Durga / Angalamman / Kali",
        "category_ta": "நாக சக்தி / உக்கிர காளியம்மன் தலம்",
        "category_en": "Serpent Divinity / Fierce Mother Protector",
        "gender_ta": "பெண் தெய்வம்",
        "gender_en": "Female Deity",
        "forms_ta": ["புற்றடி நாகாத்தம்மன்", "அங்காள பரமேஸ்வரி", "தில்லை காளி", "கொற்றவை", "வடகாளியம்மன்"],
        "forms_en": ["Putru Nagathamman", "Angala Parameswari", "Thillai Kali", "Kotravai", "Vadakali"],
        "trees_ta": "புற்று உள்ள வேப்பமரம், நாகலிங்க மரம்",
        "trees_en": "Neem with sacred anthill, Nagalingam tree",
        "landscape_ta": "தென்மேற்கு திசையில் இயற்கை புற்று அல்லது மரத்தடியில் வேலுடன் கூடிய திறந்தவெளி அம்மன் பீடம்",
        "landscape_en": "South-West direction near natural anthill or open sanctum with Trishula/Vel",
        "desc_ta": "இராகுவின் ஆதிக்கத்தில் வரும் தெய்வம் நாக சக்தி பொருந்திய புற்றடி அம்மன், துர்க்கை அல்லது அங்காள பரமேஸ்வரி. குடும்பத்தில் உள்ள நாக தோஷங்களை நீக்கி வம்சத்தைக் கண் இமை போலக் காக்கும்.",
        "desc_en": "Rahu signifies powerful serpent protector divinities (Nagathamman, Angalamman, or Mother Durga), dissolving generational afflictions and granting invincibility.",
    },
    "Ketu": {
        "deity_name_ta": "ஸ்ரீ விநாயகர் / வீர ஆஞ்சநேயர் / பைரவர்",
        "deity_name_en": "Lord Vinayagar (Ganesha) / Veera Anjaneyar / Bhairava",
        "category_ta": "முழுமுதற் கடவுள் / சங்கட நிவாரண தலம்",
        "category_en": "Primordial Ganesha / Anjaneya Shrine",
        "gender_ta": "ஆண் தெய்வம்",
        "gender_en": "Male Deity",
        "forms_ta": ["வரசித்தி விநாயகர்", "உச்சிப் பிள்ளையார்", "வீர ஆஞ்சநேயர்", "சொர்ணாகர்ஷண பைரவர்"],
        "forms_en": ["Varasiddhi Vinayagar", "Uchi Pillaiyar", "Veera Anjaneyar", "Swarna Akarshana Bhairava"],
        "trees_ta": "அரச மரம், எருக்கு, அருகம்புல் படர்ந்த பீடம்",
        "trees_en": "Sacred Fig (Arasu), Calotropis, Arugampul",
        "landscape_ta": "ஆற்றங்கரை அரசமரத்தடி, மூன்று வழிகள் கூடும் சந்திப்பு அல்லது பாறையின் மேல் உள்ள தலம்",
        "landscape_en": "Under sacred fig trees by water reservoirs or elevated rocky perches",
        "desc_ta": "கேதுவின் ஆதிக்கத்தில் வரும் குலதெய்வம் விக்னங்களை வேரறுக்கும் விநாயகப் பெருமான் அல்லது ஆஞ்சநேயர். தொடங்கும் அனைத்து செயல்களிலும் வெற்றியைத் தந்து முக்தி வழியைக் காட்டும்.",
        "desc_en": "Ketu indicates primordial obstacle-clearing deities: Lord Ganesha under sacred fig trees or Veera Anjaneya conferring protection and spiritual release.",
    },
}

UNIVERSAL_REFUGE_TEMPLES: List[UniversalRefugeTemple] = [
    UniversalRefugeTemple(
        temple_name_ta="அருள்மிகு சுப்பிரமணிய சுவாமி திருக்கோவில்",
        temple_name_en="Arulmigu Subramaniaswamy Temple",
        location_ta="திருச்செந்தூர், தூத்துக்குடி மாவட்டம்",
        location_en="Tiruchendur, Thoothukudi District, Tamil Nadu",
        spiritual_significance_ta="தமிழ் மண்ணின் பொதுக் குலதெய்வமாகத் திகழும் கடற்கரைத் தலம். குலதெய்வம் தெரியாத எவரும் இங்கு வந்து கடலில் நீராடி விரதமிருந்து வழிபடக் குலசாபம் நீங்கி அருள் பெருகும்.",
        spiritual_significance_en="Universal Kuladeivam refuge of Tamilakam on the sea coast. Anyone unaware of their family deity can take holy sea dip and surrender to Lord Murugan to dissolve lineage blocks.",
    ),
    UniversalRefugeTemple(
        temple_name_ta="அருள்மிகு மீனாட்சி சுந்தரேஸ்வரர் திருக்கோவில்",
        temple_name_en="Arulmigu Meenakshi Sundareswarar Temple",
        location_ta="மதுரை திருத்தலம்",
        location_en="Madurai, Tamil Nadu",
        spiritual_significance_ta="அனைத்து உயிர்களுக்கும் தாய் தந்தையாய் விளங்கும் அன்னை மீனாட்சியும் சொக்கநாதரும் வீற்றிருக்கும் புண்ணிய பூமி. வம்ச தர்மம் தழைக்க இங்கு வேண்டலாம்.",
        spiritual_significance_en="Universal Mother and Father of all created beings. Praying here restores generational blessings and protects children.",
    ),
    UniversalRefugeTemple(
        temple_name_ta="அருள்மிகு சமயபுரம் மாரியம்மன் திருக்கோவில்",
        temple_name_en="Arulmigu Samayapuram Mariamman Temple",
        location_ta="சமயபுரம், திருச்சிராப்பள்ளி மாவட்டம்",
        location_en="Samayapuram, Tiruchirappalli District, Tamil Nadu",
        spiritual_significance_ta="அனைத்து கிராம அம்மன் தெய்வங்களின் மூலத் தாயாக விளங்குபவள். குலதெய்வம் அம்மன் என்று மட்டும் தெரிந்து பெயர் அறியாத குடும்பங்கள் சரணடையும் மகா சக்தி பீடம்.",
        spiritual_significance_en="Primordial Mother of all rural Amman manifestations. The greatest sanctuary for families knowing their deity is a Goddess but lacking the exact temple village.",
    ),
    UniversalRefugeTemple(
        temple_name_ta="அருள்மிகு ராமநாதசுவாமி திருக்கோவில்",
        temple_name_en="Arulmigu Ramanathaswamy Temple",
        location_ta="ராமேஸ்வரம், ராமநாதபுரம் மாவட்டம்",
        location_en="Rameswaram, Ramanathapuram District, Tamil Nadu",
        spiritual_significance_ta="முன்னோர்களின் ஆசியையும் பித்ரு தோஷ நிவர்த்தியையும் வழங்கும் முதன்மை தலம். 22 தீர்த்தங்களில் நீராடி முன்னோரை வழிபடக் குலதெய்வ வழிகாட்டுதல் கிட்டும்.",
        spiritual_significance_en="Premier ancestral pilgrimage shrine. Bathing in the 22 holy theerthams dispels Pitru obstacles, prompting intuitive dreams and elders' clues regarding the lost shrine.",
    ),
]


def _get_navamsha_sign(lon_deg: float) -> int:
    """Computes exact Navamsha (D9) sign index (1-12) for a given sidereal longitude."""
    norm = lon_deg % 360.0
    rasi_idx = int(norm // 30.0) + 1
    deg_in_rasi = norm % 30.0
    pada = int(deg_in_rasi // (30.0 / 9.0))  # 0 to 8

    # Movable (1, 4, 7, 10) starts from rasi itself
    # Fixed (2, 5, 8, 11) starts from 9th from rasi
    # Dual (3, 6, 9, 12) starts from 5th from rasi
    if rasi_idx in (1, 4, 7, 10):
        start_sign = rasi_idx
    elif rasi_idx in (2, 5, 8, 11):
        start_sign = ((rasi_idx - 1 + 8) % 12) + 1
    else:
        start_sign = ((rasi_idx - 1 + 4) % 12) + 1

    return ((start_sign - 1 + pada) % 12) + 1


def _check_aspects(planet_sign: int, target_sign: int, planet_name: str) -> bool:
    """Checks if a planet aspects a target sign under Vedic rules."""
    diff = (target_sign - planet_sign) % 12
    # 7th house aspect (diff == 6) applies to all planets
    if diff == 6:
        return True
    if planet_name == "Mars" and diff in (3, 7):  # 4th and 8th aspect
        return True
    if planet_name == "Jupiter" and diff in (4, 8):  # 5th and 9th aspect
        return True
    if planet_name == "Saturn" and diff in (2, 9):  # 3rd and 10th aspect
        return True
    if planet_name in ("Rahu", "Ketu") and diff in (4, 8):  # 5th and 9th aspect
        return True
    return False


class KuladeivamService:
    """Comprehensive service for Kuladeivam determination and spiritual guidance."""

    @classmethod
    def calculate_from_horoscope(cls, req: KuladeivamRequest) -> KuladeivamResponse:
        """Derives Kuladeivam profiles from birth chart 5th/9th houses and D9 Navamsha."""
        # 1. Compute astronomical positions
        horoscope_data = calculate_full_horoscope(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            timezone_str=req.timezone,
            latitude=req.latitude,
            longitude=req.longitude,
            ayanamsa_id=req.ayanamsa,
            house_system_id=req.house_system,
            include_panchang=True,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            include_varga=True,
            include_doshas=False,
            gender=req.gender or "male",
        )

        lagna_sign_idx = horoscope_data.ascendant.sign_index
        planets = horoscope_data.planets

        # Map planet positions
        planet_by_name = {p.name: p for p in planets}
        planets_in_signs: Dict[int, List[str]] = {s: [] for s in range(1, 13)}
        for p in planets:
            planets_in_signs[p.sign_index].append(p.name)

        # 5th & 9th House indices from Lagna
        fifth_house_sign = ((lagna_sign_idx - 1 + 4) % 12) + 1
        ninth_house_sign = ((lagna_sign_idx - 1 + 8) % 12) + 1

        fifth_lord = SIGN_LORDS[fifth_house_sign]
        ninth_lord = SIGN_LORDS[ninth_house_sign]

        # Navamsha positions
        fifth_lord_planet = planet_by_name.get(fifth_lord)
        fifth_lord_navamsha_sign = _get_navamsha_sign(fifth_lord_planet.longitude) if fifth_lord_planet else fifth_house_sign
        fifth_navamsha_lord = SIGN_LORDS[fifth_lord_navamsha_sign]

        ninth_lord_planet = planet_by_name.get(ninth_lord)
        ninth_lord_navamsha_sign = _get_navamsha_sign(ninth_lord_planet.longitude) if ninth_lord_planet else ninth_house_sign
        ninth_navamsha_lord = SIGN_LORDS[ninth_lord_navamsha_sign]

        # Aspects on 5th and 9th
        fifth_aspects = [p.name for p in planets if _check_aspects(p.sign_index, fifth_house_sign, p.name)]
        ninth_aspects = [p.name for p in planets if _check_aspects(p.sign_index, ninth_house_sign, p.name)]

        fifth_occupants = planets_in_signs[fifth_house_sign]
        ninth_occupants = planets_in_signs[ninth_house_sign]

        # Build House Analysis Objects
        fifth_house_obj = HouseAnalysisDetails(
            house_num=5,
            sign_name_ta=ZODIAC_NAMES_TA[fifth_house_sign],
            sign_name_en=ZODIAC_NAMES_EN[fifth_house_sign],
            sign_lord_ta=GRAHA_NAMES_TA.get(fifth_lord, fifth_lord),
            sign_lord_en=fifth_lord,
            sign_tattva_ta=SIGN_TATTVA[fifth_house_sign][1],
            sign_tattva_en=SIGN_TATTVA[fifth_house_sign][0],
            sign_gender_ta=SIGN_GENDER[fifth_house_sign][1],
            sign_gender_en=SIGN_GENDER[fifth_house_sign][0],
            occupants_ta=[GRAHA_NAMES_TA.get(p, p) for p in fifth_occupants],
            occupants_en=fifth_occupants,
            aspecting_grahas_ta=[GRAHA_NAMES_TA.get(p, p) for p in fifth_aspects],
            aspecting_grahas_en=fifth_aspects,
            navamsha_sign_ta=ZODIAC_NAMES_TA[fifth_lord_navamsha_sign],
            navamsha_sign_en=ZODIAC_NAMES_EN[fifth_lord_navamsha_sign],
            navamsha_lord_ta=GRAHA_NAMES_TA.get(fifth_navamsha_lord, fifth_navamsha_lord),
            navamsha_lord_en=fifth_navamsha_lord,
        )

        ninth_house_obj = HouseAnalysisDetails(
            house_num=9,
            sign_name_ta=ZODIAC_NAMES_TA[ninth_house_sign],
            sign_name_en=ZODIAC_NAMES_EN[ninth_house_sign],
            sign_lord_ta=GRAHA_NAMES_TA.get(ninth_lord, ninth_lord),
            sign_lord_en=ninth_lord,
            sign_tattva_ta=SIGN_TATTVA[ninth_house_sign][1],
            sign_tattva_en=SIGN_TATTVA[ninth_house_sign][0],
            sign_gender_ta=SIGN_GENDER[ninth_house_sign][1],
            sign_gender_en=SIGN_GENDER[ninth_house_sign][0],
            occupants_ta=[GRAHA_NAMES_TA.get(p, p) for p in ninth_occupants],
            occupants_en=ninth_occupants,
            aspecting_grahas_ta=[GRAHA_NAMES_TA.get(p, p) for p in ninth_aspects],
            aspecting_grahas_en=ninth_aspects,
            navamsha_sign_ta=ZODIAC_NAMES_TA[ninth_lord_navamsha_sign],
            navamsha_sign_en=ZODIAC_NAMES_EN[ninth_lord_navamsha_sign],
            navamsha_lord_ta=GRAHA_NAMES_TA.get(ninth_navamsha_lord, ninth_navamsha_lord),
            navamsha_lord_en=ninth_navamsha_lord,
        )

        # Primary Planet Determinant:
        # In Tamil lineage tradition: 9th house is Pitru Kula Sthana (primary ancestral line),
        # 5th house is Poorva Punya / Ishta Devata.
        # Strongest planet influencing 9th or 5th is picked.
        primary_graha = ninth_occupants[0] if ninth_occupants else ninth_lord
        secondary_graha = fifth_occupants[0] if fifth_occupants else fifth_lord

        # Fallback if both evaluate to same planet
        if secondary_graha == primary_graha:
            secondary_graha = ninth_navamsha_lord if ninth_navamsha_lord != primary_graha else fifth_navamsha_lord

        primary_kb = DEITY_KNOWLEDGE_BASE.get(primary_graha, DEITY_KNOWLEDGE_BASE["Mars"])
        secondary_kb = DEITY_KNOWLEDGE_BASE.get(secondary_graha, DEITY_KNOWLEDGE_BASE["Moon"])

        # Determine direction and landscape from 9th house & primary graha
        prim_dir_en, prim_dir_ta = PLANET_DIRECTIONS.get(primary_graha, ("East", "கிழக்கு"))
        sec_dir_en, sec_dir_ta = PLANET_DIRECTIONS.get(secondary_graha, ("North-East", "வடகிழக்கு"))

        landscape = TempleLandscape(
            primary_direction_ta=prim_dir_ta,
            primary_direction_en=prim_dir_en,
            alternate_direction_ta=sec_dir_ta,
            alternate_direction_en=sec_dir_en,
            landscape_nature_ta=primary_kb["landscape_ta"],
            landscape_nature_en=primary_kb["landscape_en"],
            temple_setting_ta=f"{primary_kb['landscape_ta']} பகுதியில் {primary_kb['trees_ta']} நிழலில் அமைந்த பழமையான ஆலயம்.",
            temple_setting_en=f"Ancient shrine situated in {primary_kb['landscape_en']} sheltered by {primary_kb['trees_en']}.",
            associated_sacred_tree_ta=primary_kb["trees_ta"],
            associated_sacred_tree_en=primary_kb["trees_en"],
            distance_indication_ta="பூர்வீக ஊரிலிருந்து அல்லது பிறந்த இடத்திலிருந்து சுமார் 15 முதல் 65 கி.மீ தொலைவு வட்டத்திற்குள் அமைய வாய்ப்புள்ளது.",
            distance_indication_en="Typically located within a 15 to 65 km radius from the ancestral homeland or birthplace.",
        )

        # Build Deity Indicators
        primary_indicator = DeityIndicator(
            deity_name_ta=primary_kb["deity_name_ta"],
            deity_name_en=primary_kb["deity_name_en"],
            deity_category_ta=primary_kb["category_ta"],
            deity_category_en=primary_kb["category_en"],
            gender_ta=primary_kb["gender_ta"],
            gender_en=primary_kb["gender_en"],
            governing_planet_ta=GRAHA_NAMES_TA.get(primary_graha, primary_graha),
            governing_planet_en=primary_graha,
            governing_house_ta="9-ஆம் பாக்கிய/பித்ரு ஸ்தானம் (முதன்மைக் குலதெய்வம்)",
            governing_house_en="9th Pitru/Bhagya House (Primary Ancestral Deity)",
            sign_name_ta=ZODIAC_NAMES_TA[ninth_house_sign],
            sign_name_en=ZODIAC_NAMES_EN[ninth_house_sign],
            sign_tattva_ta=SIGN_TATTVA[ninth_house_sign][1],
            sign_tattva_en=SIGN_TATTVA[ninth_house_sign][0],
            prominence_score=92,
            traditional_forms_ta=primary_kb["forms_ta"],
            traditional_forms_en=primary_kb["forms_en"],
            description_ta=primary_kb["desc_ta"],
            description_en=primary_kb["desc_en"],
        )

        secondary_indicator = DeityIndicator(
            deity_name_ta=secondary_kb["deity_name_ta"],
            deity_name_en=secondary_kb["deity_name_en"],
            deity_category_ta=secondary_kb["category_ta"],
            deity_category_en=secondary_kb["category_en"],
            gender_ta=secondary_kb["gender_ta"],
            gender_en=secondary_kb["gender_en"],
            governing_planet_ta=GRAHA_NAMES_TA.get(secondary_graha, secondary_graha),
            governing_planet_en=secondary_graha,
            governing_house_ta="5-ஆம் பூர்வ புண்ணிய ஸ்தானம் (இஷ்ட/துணைக் குலதெய்வம்)",
            governing_house_en="5th Purva Punya House (Ishta / Lineage Protector)",
            sign_name_ta=ZODIAC_NAMES_TA[fifth_house_sign],
            sign_name_en=ZODIAC_NAMES_EN[fifth_house_sign],
            sign_tattva_ta=SIGN_TATTVA[fifth_house_sign][1],
            sign_tattva_en=SIGN_TATTVA[fifth_house_sign][0],
            prominence_score=85,
            traditional_forms_ta=secondary_kb["forms_ta"],
            traditional_forms_en=secondary_kb["forms_en"],
            description_ta=secondary_kb["desc_ta"],
            description_en=secondary_kb["desc_en"],
        )

        # Dosha / Affliction Analysis
        afflictions_ta = []
        afflictions_en = []
        is_afflicted = False

        # Check if 9th or 5th lord in Dusthana (6, 8, 12)
        if ninth_lord_planet:
            ninth_lord_house = ((ninth_lord_planet.sign_index - lagna_sign_idx) % 12) + 1
            if ninth_lord_house in (6, 8, 12):
                is_afflicted = True
                afflictions_ta.append(f"9-ஆம் அதிபதி {GRAHA_NAMES_TA.get(ninth_lord, ninth_lord)} மறைவு ஸ்தானமான {ninth_lord_house}-இல் அமர்ந்துள்ளது.")
                afflictions_en.append(f"9th Lord {ninth_lord} is placed in Dusthana house {ninth_lord_house}.")

        # Check Rahu/Ketu presence in 5th or 9th
        if "Rahu" in ninth_occupants or "Ketu" in ninth_occupants:
            is_afflicted = True
            afflictions_ta.append("9-ஆம் வீடான பித்ரு ஸ்தானத்தில் ராகு அல்லது கேது நிழல் கிரகம் அமர்ந்துள்ளது (குலதெய்வ வழிபாடு விடுபட்டதற்கான அறிகுறி).")
            afflictions_en.append("Rahu or Ketu occupies the 9th house (indicator of interrupted ancestral worship).")

        if "Rahu" in fifth_occupants or "Ketu" in fifth_occupants:
            is_afflicted = True
            afflictions_ta.append("5-ஆம் வீட்டில் நாக தோஷ கிரகங்கள் அமர்ந்துள்ளதால் குலதெய்வ அருள் தடைகள் ஏற்பட வாய்ப்புள்ளது.")
            afflictions_en.append("Nodes in the 5th house suggest potential ancestral worship interruptions or forgotten vows.")

        if is_afflicted:
            dosha_status = KuladeivamDoshaAnalysis(
                status_ta="குலதெய்வ வழிபாட்டில் குறை அல்லது தடை நிலை (பரிகாரம் தேவை)",
                status_en="Ancestral Worship Affliction / Pending Vow Detected",
                is_afflicted=True,
                affliction_factors_ta=afflictions_ta,
                affliction_factors_en=afflictions_en,
                explanation_ta="ஜாதகத்தில் 9-ஆம் அல்லது 5-ஆம் அதிபதிகளுக்கு மறைவு அல்லது ராகு-கேது சம்பந்தம் ஏற்பட்டுள்ளது. இது முன்னோர்கள் வேண்டிய நேர்த்திக்கடன் விடுபட்டதையோ அல்லது குலதெய்வக் கோவிலுக்குச் செல்வதில் ஏற்படும் தாமதத்தையோ குறிக்கிறது.",
                explanation_en="Planetary positions indicate forgotten family vows (Nerthikadan) or discontinued annual ancestral visits that momentarily veil the deity's complete grace.",
                traditional_symptoms_ta=[
                    "குடும்பத்தில் சுபகாரியங்கள் காரணமின்றி தடைபடுதல் அல்லது தாமதமாதல்.",
                    "குழந்தை பாக்கியம் அல்லது திருமணம் தள்ளிப்போதல்.",
                    "பொருளாதாரத்தில் வரவு இருந்தும் சேமிப்பு தங்காமல் விரயமாதல்.",
                    "மன அமைதியின்மை மற்றும் கனவில் பாம்பு அல்லது பாழடைந்த கோவில் தெரிதல்.",
                ],
                traditional_symptoms_en=[
                    "Unexplained delays in auspicious family events and celebrations.",
                    "Delays in marriage or childbirth across close cousins.",
                    "Wealth dissipation despite steady income.",
                    "Restlessness and repetitive dreams of abandoned shrines or snakes.",
                ],
                mitigation_steps_ta=[
                    "வீட்டில் வெள்ளிக்கிழமை அல்லது அமாவாசை தோறும் பசு நெய் தீபமிட்டு முன்னோர்களை வழிபடவும்.",
                    "மஞ்சள் துணியில் 5 ரூபாய் நாணயம் வைத்து முடிந்து குலதெய்வ காணிக்கையாகப் பூசை அறையில் வைக்கவும்.",
                    "திருச்செந்தூர் அல்லது சமயபுரம் திருத்தலத்திற்குச் சென்று குடும்பத்தோடு வழிபாடு செய்து வரவும்.",
                ],
                mitigation_steps_en=[
                    "Light pure cow's ghee lamps every Friday or Amavasya with ancestral prayers.",
                    "Tie a sanctified coin in yellow cloth as a pending offering kept in the puja altar.",
                    "Visit universal refuge centers like Tiruchendur or Samayapuram with family.",
                ],
            )
        else:
            dosha_status = KuladeivamDoshaAnalysis(
                status_ta="பரிபூரண குலதெய்வ அருள் நிலை (சுப யோகம்)",
                status_en="Blessed & Active Ancestral Deity Shield",
                is_afflicted=False,
                affliction_factors_ta=["எந்தவித கடுமையான மறைவு அல்லது சாப தோஷங்களும் இல்லை."],
                affliction_factors_en=["No adverse Dusthana or nodal afflictions on lineage bhavas."],
                explanation_ta="உங்கள் ஜாதகத்தில் 5 மற்றும் 9-ஆம் அதிபதிகள் சுப பலத்துடன் அமைந்திருப்பதால் முன்னோர்களின் தவமும் குலதெய்வத்தின் அருட்காவலும் உங்கள் குடும்பத்திற்கு பலமான கவசமாக விளங்குகின்றது.",
                explanation_en="Auspicious strength of the 5th and 9th lords confirms the benevolent protection of your ancestral deity continuously shielding your family lineage.",
                traditional_symptoms_ta=[
                    "இக்கட்டான சூழ்நிலைகளில் கூட திடீர் நல்ல வழிகாட்டுதல் கிட்டுதல்.",
                    "குடும்பத்தில் மங்கல காரியங்கள் சுபமாக நிறைவேறுதல்.",
                    "சந்ததி நலம் மற்றும் ஆரோக்கிய விருத்தி.",
                ],
                traditional_symptoms_en=[
                    "Timely breakthroughs and unseen protection during life crises.",
                    "Smooth realization of family functions and milestones.",
                    "Generational health and prosperity.",
                ],
                mitigation_steps_ta=[
                    "வருடத்திற்கு ஒருமுறையாவது குடும்பத்தோடு குலதெய்வ சன்னதிக்குச் சென்று பொங்கலிட்டு வழிபடவும்.",
                    "வீட்டுப் பூஜையில் முதலிடம் குலதெய்வத்திற்கு வழங்கி வழிபடவும்.",
                ],
                mitigation_steps_en=[
                    "Maintain the annual family pilgrimage with sweet pongal offerings.",
                    "Accord the primary seat to the Kuladeivam during domestic festivals.",
                ],
            )

        # Discovery Protocol for Unknown Kuladeivam
        discovery_protocol = UnknownDeityDiscoveryProtocol(
            title_ta="குலதெய்வம் அறியாதோர் கண்டறியும் பாரம்பரிய வழிபாட்டு முறை",
            title_en="Classical Procedure to Discover an Unknown Family Deity",
            overview_ta="பல தலைமுறைகளாக இடம் பெயர்ந்து குலதெய்வம் எதுவென்று அறியாமல் தவிக்கும் குடும்பங்கள், தங்கள் வீட்டிலேயே முறையாகச் செய்து தெய்வீக வழிகாட்டுதலைப் பெறும் சாஸ்திர முறை.",
            overview_en="Venerable Tamil Shastra protocol for families who have lost trace of their ancestral deity through generational migrations.",
            steps_ta=[
                "1. அமாவாசை அல்லது தமிழ் மாதப் பிறப்பன்று அதிகாலை நீராடி வீட்டைச் சுத்தம் செய்யவும்.",
                "2. பூசை அறையில் ஒரு மரப்பலகை மீது பச்சரிசி பரப்பி, அதன் மீது பித்தளை அல்லது வெண்கல காமாட்சி தீபம் வைக்கவும்.",
                "3. தீபத்தில் சுத்தமான பசு நெய் அல்லது நல்லெண்ணெய் ஊற்றி, பஞ்சு திரி இட்டு கிழக்கு நோக்கி ஏற்றவும்.",
                "4. மனமுருகி: 'எங்கள் வம்சத்தை வாழ வைக்கும் புண்ணிய குலதெய்வமே! நாங்கள் அறியாமல் விட்ட குறையை மன்னித்து உனது அடையாளத்தை வெளிப்படுத்து' என்று சங்கல்பம் செய்யவும்.",
                "5. குடும்பத்தில் உள்ள மூத்த பெரியவர்கள், சொந்த ஊரில் உள்ள பங்காளி அல்லது தாயாதி உறவுகளிடம் பூர்வீக கிராமப் பெயரைக் கேட்டு விசாரிக்கவும்.",
                "6. தொடர்ந்து 48 நாட்கள் (ஒரு மண்டலம்) அல்லது 9 வெள்ளிக்கிழமைகள் மாலை 6 மணிக்கு தீபமேற்றி வர, கனவிலோ அல்லது உறவினர்கள் மூலமாகவோ குலதெய்வ அடையாளம் துல்லியமாக வெளிப்படும்.",
            ],
            steps_en=[
                "1. Clean the home altar early morning on an Amavasya or the first day of a Tamil solar month.",
                "2. Spread raw rice on a clean wooden plank and place a brass Kamakshi deepam upon it.",
                "3. Fill the lamp with pure cow's ghee or sesame oil with cotton wick facing East.",
                "4. Pray whole-heartedly: 'O Benevolent Lineage Deity, forgive our inadvertent ignorance and unveil your sacred shrine to our family'.",
                "5. Inquire with elder relatives or ancestral village pangalis about old clan migrations.",
                "6. Maintain the evening lamp lighting for 48 consecutive days (one mandala) or 9 consecutive Fridays; revelation inevitably surfaces through dreams or ancestral elder contacts.",
            ],
            deepam_procedure_ta="மாவிளக்கு தீபம்: பச்சரிசி மாவில் வெல்லம், ஏலக்காய் மற்றும் பசு நெய் கலந்து உருண்டையாக்கி, அதன் நடுவில் குழி செய்து நெய் ஊற்றி திரி இட்டு ஏற்றுவது மிகுந்த சக்தி வாய்ந்த பரிகாரமாகும்.",
            deepam_procedure_en="Maa-Vilakku Deepam: A sacred dough lamp prepared from soaked raw rice flour, jaggery, cardamom, and pure ghee. Lighting this lamp dissolves generational karmic obscurations.",
            pongal_offering_ta="பச்சரிசி, பாசிப்பருப்பு, வெல்லம் மற்றும் பசும்பால் கொண்டு புது மண்பானையில் பொங்கல் வைத்து, தலைவாழை இலையில் படைத்து குடும்பத்தோடு வழிபட வேண்டும்.",
            pongal_offering_en="Prepare traditional sweet pongal in an earthen pot with newly harvested raw rice, jaggery, and cow's milk, offering it on a plantain leaf.",
            coin_knot_ritual_ta="மஞ்சள் துணி முடிப்பு: ஒரு புதிய மஞ்சள் துணியில் ஒரு வெள்ளி நாணயம் அல்லது 5 ரூபாய் நாணயத்தை வைத்து, அதில் சிறிது பச்சரிசி மற்றும் மஞ்சள் பொடி சேர்த்து முடிந்து, 'குலதெய்வ காணிக்கை' என்று பூசை அறையில் வைத்து வணங்கவும். ஆலயம் தெரிந்ததும் அதை அங்கு சமர்ப்பிக்க வேண்டும்.",
            coin_knot_ritual_en="Yellow Cloth Coin Knot: Place a sanctified coin with unbroken raw rice in a yellow cloth, tie it securely as a dedicated pledge, and keep it in the puja room until you visit the ancestral shrine.",
            universal_refuge_temples=UNIVERSAL_REFUGE_TEMPLES,
        )

        lineage_insights_ta = [
            f"உங்கள் லக்னத்திற்கு 9-ஆம் வீடான பாக்கிய ஸ்தானம் {ZODIAC_NAMES_TA[ninth_house_sign]} ({SIGN_TATTVA[ninth_house_sign][1]}). இது தந்தை வழி பரம்பரை குலதெய்வத்தைக் குறிக்கிறது.",
            f"5-ஆம் வீடான பூர்வ புண்ணிய ஸ்தானம் {ZODIAC_NAMES_TA[fifth_house_sign]} ({SIGN_GENDER[fifth_house_sign][1]}). இது முன்னோர்களின் புண்ணிய பலத்தையும் இஷ்ட தெய்வத்தையும் குறிக்கிறது.",
            f"முதன்மைக் குலதெய்வம் {primary_indicator.deity_name_ta} ({primary_indicator.deity_category_ta}) வடிவில் அமைந்திருக்கும் சாத்தியக்கூறு மிக அதிகம்.",
            f"ஆலயத்தின் அமைவிடம் பூர்வீக ஊரின் {prim_dir_ta} திசையில் நீர்நிலை அல்லது வேப்பமரம்/ஆலமர சூழலில் அமைந்திருக்க வாய்ப்புள்ளது.",
        ]

        lineage_insights_en = [
            f"Your 9th House of Ancestry is {ZODIAC_NAMES_EN[ninth_house_sign]} ({SIGN_TATTVA[ninth_house_sign][0]}), signifying paternal hereditary lineage protection.",
            f"Your 5th House of Past Merits is {ZODIAC_NAMES_EN[fifth_house_sign]} ({SIGN_GENDER[fifth_house_sign][0]}), reflecting the accumulated spiritual merit of forefathers.",
            f"The primary lineage deity is strongly indicated as {primary_indicator.deity_name_en} ({primary_indicator.deity_category_en}).",
            f"Temple geography points towards the {prim_dir_en} direction from the ancestral hometown, associated with waterbodies or sacred trees.",
        ]

        classical_references = [
            "Brihat Parasara Hora Sastra (BPHS), Ch. 11 & Ch. 32: Bhava Karakatwas of 5th (Purva Punya) and 9th (Dharma/Pitru).",
            "Jataka Parijata, Adhyaya 15: Deities governed by Planetary lords and Navamsha dispositions.",
            "Prasna Marga, Ch. 15: Deva Prasna, identifying clan deities, pending vows, and ancestral curses.",
            "Tamil Jothida Sastra Sangraham: Grama Devata, Ayyanar, Karuppasamy, and Amman Kaval determinants.",
        ]

        return KuladeivamResponse(
            analysis_mode="horoscope",
            native_summary={
                "birth_date": str(req.birth_date),
                "birth_time": str(req.birth_time),
                "lagna_sign_ta": ZODIAC_NAMES_TA[lagna_sign_idx],
                "lagna_sign_en": ZODIAC_NAMES_EN[lagna_sign_idx],
                "moon_sign_ta": horoscope_data.planets[1].sign_name_tamil if len(horoscope_data.planets) > 1 else "",
                "moon_sign_en": horoscope_data.planets[1].sign_name if len(horoscope_data.planets) > 1 else "",
                "nakshatra": horoscope_data.planets[1].nakshatra.name if len(horoscope_data.planets) > 1 else "",
                "ancestral_district": req.ancestral_district or "Tamil Nadu Ancestral Origin",
            },
            fifth_house=fifth_house_obj,
            ninth_house=ninth_house_obj,
            primary_deity=primary_indicator,
            secondary_deity=secondary_indicator,
            temple_landscape=landscape,
            dosha_analysis=dosha_status,
            discovery_protocol=discovery_protocol,
            lineage_insights_ta=lineage_insights_ta,
            lineage_insights_en=lineage_insights_en,
            classical_references=classical_references,
        )

    @classmethod
    def calculate_from_prasanna(cls, req: KuladeivamPrasannaRequest) -> KuladeivamResponse:
        """Derives Kuladeivam guidance using horary Jamakkol Prasanam at the instant of query."""
        res = calculate_jamakkol_prasanam(
            query_dt_str=req.query_datetime,
            latitude=req.latitude,
            longitude=req.longitude,
            tz_str=req.timezone,
            ayanamsa_id=req.ayanamsa_id,
            query_text="Finding Unknown Kuladeivam (குலதெய்வம் கண்டறிதல்)",
            query_category="spiritual",
            querent_seed=req.querent_seed,
        )

        three_pillars = res.get("three_pillars", {})
        udhayam_data = three_pillars.get("udhayam", {})
        aarudham_data = three_pillars.get("aarudham", {})
        kavippu_data = three_pillars.get("kavippu", {})

        udhayam_sign = udhayam_data.get("sign_index", 1)
        aarudham_sign = aarudham_data.get("sign_index", 1)
        kavippu_sign = kavippu_data.get("sign_index", 1)

        # In Jamakkol Prasanam for Deity:
        # Aarudham indicates the heart of the matter and ancestral protector.
        # 9th from Aarudham indicates the Kula Devata.
        ninth_from_aarudham = ((aarudham_sign - 1 + 8) % 12) + 1
        fifth_from_aarudham = ((aarudham_sign - 1 + 4) % 12) + 1

        ninth_lord = SIGN_LORDS[ninth_from_aarudham]
        fifth_lord = SIGN_LORDS[fifth_from_aarudham]

        # Check Jama graha in 9th or Aarudham
        jama_grahas = res.get("jama_grahas", [])
        jama_in_9th = [jg.get("name_en") for jg in jama_grahas if jg.get("sign_index") == ninth_from_aarudham and jg.get("name_en")]
        prim_graha = jama_in_9th[0] if (jama_in_9th and jama_in_9th[0] in DEITY_KNOWLEDGE_BASE) else ninth_lord
        if not prim_graha or prim_graha not in DEITY_KNOWLEDGE_BASE:
            prim_graha = "Mars"

        sec_graha = fifth_lord if (fifth_lord and fifth_lord != prim_graha and fifth_lord in DEITY_KNOWLEDGE_BASE) else "Moon"
        if not sec_graha or sec_graha not in DEITY_KNOWLEDGE_BASE:
            sec_graha = "Moon"

        prim_kb = DEITY_KNOWLEDGE_BASE.get(prim_graha, DEITY_KNOWLEDGE_BASE["Mars"])
        sec_kb = DEITY_KNOWLEDGE_BASE.get(sec_graha, DEITY_KNOWLEDGE_BASE["Moon"])

        prim_dir_en, prim_dir_ta = PLANET_DIRECTIONS.get(prim_graha, ("East", "கிழக்கு"))
        sec_dir_en, sec_dir_ta = PLANET_DIRECTIONS.get(sec_graha, ("North", "வடக்கு"))

        landscape = TempleLandscape(
            primary_direction_ta=prim_dir_ta,
            primary_direction_en=prim_dir_en,
            alternate_direction_ta=sec_dir_ta,
            alternate_direction_en=sec_dir_en,
            landscape_nature_ta=prim_kb["landscape_ta"],
            landscape_nature_en=prim_kb["landscape_en"],
            temple_setting_ta=f"பிரசன்ன ஆருடப்படி {prim_dir_ta} திசையில் {prim_kb['trees_ta']} நிழலில் அமைந்துள்ள ஆலயம்.",
            temple_setting_en=f"Per Horary Prasna, located in the {prim_dir_en} direction sheltered by {prim_kb['trees_en']}.",
            associated_sacred_tree_ta=prim_kb["trees_ta"],
            associated_sacred_tree_en=prim_kb["trees_en"],
            distance_indication_ta="கேள்வி கேட்ட இடத்திலிருந்து அல்லது பூர்வீகத்திலிருந்து சுமார் 10 முதல் 45 கி.மீ தொலைவு.",
            distance_indication_en="Approximately 10 to 45 km from current query location or ancestral roots.",
        )

        primary_indicator = DeityIndicator(
            deity_name_ta=prim_kb["deity_name_ta"],
            deity_name_en=prim_kb["deity_name_en"],
            deity_category_ta=prim_kb["category_ta"],
            deity_category_en=prim_kb["category_en"],
            gender_ta=prim_kb["gender_ta"],
            gender_en=prim_kb["gender_en"],
            governing_planet_ta=GRAHA_NAMES_TA.get(prim_graha, prim_graha),
            governing_planet_en=prim_graha,
            governing_house_ta="பிரசன்ன ஆருடத்திற்கு 9-ஆம் பித்ரு ஸ்தானம்",
            governing_house_en="9th Pitru House from Horary Aarudham",
            sign_name_ta=ZODIAC_NAMES_TA[ninth_from_aarudham],
            sign_name_en=ZODIAC_NAMES_EN[ninth_from_aarudham],
            sign_tattva_ta=SIGN_TATTVA[ninth_from_aarudham][1],
            sign_tattva_en=SIGN_TATTVA[ninth_from_aarudham][0],
            prominence_score=95,
            traditional_forms_ta=prim_kb["forms_ta"],
            traditional_forms_en=prim_kb["forms_en"],
            description_ta=prim_kb["desc_ta"],
            description_en=prim_kb["desc_en"],
        )

        secondary_indicator = DeityIndicator(
            deity_name_ta=sec_kb["deity_name_ta"],
            deity_name_en=sec_kb["deity_name_en"],
            deity_category_ta=sec_kb["category_ta"],
            deity_category_en=sec_kb["category_en"],
            gender_ta=sec_kb["gender_ta"],
            gender_en=sec_kb["gender_en"],
            governing_planet_ta=GRAHA_NAMES_TA.get(sec_graha, sec_graha),
            governing_planet_en=sec_graha,
            governing_house_ta="பிரசன்ன ஆருடத்திற்கு 5-ஆம் பூர்வ புண்ணியம்",
            governing_house_en="5th Purva Punya from Horary Aarudham",
            sign_name_ta=ZODIAC_NAMES_TA[fifth_from_aarudham],
            sign_name_en=ZODIAC_NAMES_EN[fifth_from_aarudham],
            sign_tattva_ta=SIGN_TATTVA[fifth_from_aarudham][1],
            sign_tattva_en=SIGN_TATTVA[fifth_from_aarudham][0],
            prominence_score=88,
            traditional_forms_ta=sec_kb["forms_ta"],
            traditional_forms_en=sec_kb["forms_en"],
            description_ta=sec_kb["desc_ta"],
            description_en=sec_kb["desc_en"],
        )

        # Check Kavippu affliction in Jamakkol
        is_kavippu_afflicted = kavippu_sign in (aarudham_sign, ninth_from_aarudham, fifth_from_aarudham)
        if is_kavippu_afflicted:
            dosha_status = KuladeivamDoshaAnalysis(
                status_ta="கவிப்பு தோஷம் - குலதெய்வக் கோவில் தடை நிலை",
                status_en="Kavippu Obscuration Detected on Deity House",
                is_afflicted=True,
                affliction_factors_ta=[f"பிரசன்ன கவிப்பு புள்ளி {ZODIAC_NAMES_TA[kavippu_sign]} ராசியில் விழுந்துள்ளது."],
                affliction_factors_en=[f"Jamakkol Kavippu point falls in {ZODIAC_NAMES_EN[kavippu_sign]} sign."],
                explanation_ta="பிரசன்ன சக்கரத்தில் கவிப்பு விழுந்திருப்பதால், குலதெய்வ வழிபாடு விடுபட்டதற்கான அல்லது ஆலயம் புனரமைப்பு பெறாமல் இருப்பதற்கான வாய்ப்புள்ளது.",
                explanation_en="Kavippu indicates past vows neglected or the ancestral temple requiring maintenance/revival.",
                traditional_symptoms_ta=[
                    "குலதெய்வம் பற்றிய தகவல் கிடைப்பதில் தடைகள் ஏற்படுதல்.",
                    "குடும்பத்தில் மனக்கசப்புகள் மற்றும் காரிய தாமதங்கள்.",
                ],
                traditional_symptoms_en=[
                    "Delays in uncovering exact temple details.",
                    "Intermittent familial misunderstandings and obstacles.",
                ],
                mitigation_steps_ta=[
                    "உடனடியாக மஞ்சள் துணியில் நாணயம் முடிந்து காணிக்கை சங்கல்பம் செய்யவும்.",
                    "திருச்செந்தூர் சென்று முருகப்பெருமானை வேண்டி கடலில் நீராடி வரவும்.",
                ],
                mitigation_steps_en=[
                    "Tie a sanctified coin in yellow cloth as a pledge in your puja room.",
                    "Visit Tiruchendur sea-shore temple to dissolve generational obstacles.",
                ],
            )
        else:
            dosha_status = KuladeivamDoshaAnalysis(
                status_ta="பிரசன்ன சுப நிலை - குலதெய்வ அருள் வெளிப்படும் காலம்",
                status_en="Auspicious Horary Indication - Imminent Revelation",
                is_afflicted=False,
                affliction_factors_ta=["கவிப்பு தோஷம் இல்லை; ஆருடம் மற்றும் உதயம் சுப பலத்துடன் உள்ளன."],
                affliction_factors_en=["No Kavippu affliction on primary lineage houses."],
                explanation_ta="நீங்கள் கேள்வி கேட்ட இந்த சுப நேரத்தில் குலதெய்வம் தன்னை வெளிப்படுத்த திருவுளம் கொண்டுள்ளது. உறவினர்கள் மூலமாகவோ அல்லது கனவு மூலமாகவோ விரைவில் அடையாளம் புலப்படும்.",
                explanation_en="The auspicious query moment reveals the deity is ready to reconnect with your family line through elders or intuitive dreams.",
                traditional_symptoms_ta=["விரைவில் நற்செய்தி கிட்டுதல் மற்றும் தடைகள் அகலுதல்."],
                traditional_symptoms_en=["Imminent breakthroughs and ancestral revelations."],
                mitigation_steps_ta=["அமாவாசை தோறும் வீட்டில் மாவிளக்கு தீபம் ஏற்றி வழிபடவும்."],
                mitigation_steps_en=["Maintain cow's ghee lamps every Friday or Amavasya."],
            )

        discovery_protocol = UnknownDeityDiscoveryProtocol(
            title_ta="குலதெய்வம் அறியாதோர் கண்டறியும் பாரம்பரிய வழிபாட்டு முறை",
            title_en="Classical Procedure to Discover an Unknown Family Deity",
            overview_ta="பல தலைமுறைகளாக இடம் பெயர்ந்து குலதெய்வம் எதுவென்று அறியாமல் தவிக்கும் குடும்பங்கள், தங்கள் வீட்டிலேயே முறையாகச் செய்து தெய்வீக வழிகாட்டுதலைப் பெறும் சாஸ்திர முறை.",
            overview_en="Venerable Tamil Shastra protocol for families who have lost trace of their ancestral deity through generational migrations.",
            steps_ta=[
                "1. அமாவாசை அல்லது தமிழ் மாதப் பிறப்பன்று அதிகாலை நீராடி வீட்டைச் சுத்தம் செய்யவும்.",
                "2. பூசை அறையில் ஒரு மரப்பலகை மீது பச்சரிசி பரப்பி, அதன் மீது பித்தளை அல்லது வெண்கல காமாட்சி தீபம் வைக்கவும்.",
                "3. தீபத்தில் சுத்தமான பசு நெய் அல்லது நல்லெண்ணெய் ஊற்றி, பஞ்சு திரி இட்டு கிழக்கு நோக்கி ஏற்றவும்.",
                "4. மனமுருகி: 'எங்கள் வம்சத்தை வாழ வைக்கும் புண்ணிய குலதெய்வமே! நாங்கள் அறியாமல் விட்ட குறையை மன்னித்து உனது அடையாளத்தை வெளிப்படுத்து' என்று சங்கல்பம் செய்யவும்.",
                "5. குடும்பத்தில் உள்ள மூத்த பெரியவர்கள், சொந்த ஊரில் உள்ள பங்காளி அல்லது தாயாதி உறவுகளிடம் பூர்வீக கிராமப் பெயரைக் கேட்டு விசாரிக்கவும்.",
                "6. தொடர்ந்து 48 நாட்கள் (ஒரு மண்டலம்) அல்லது 9 வெள்ளிக்கிழமைகள் மாலை 6 மணிக்கு தீபமேற்றி வர, கனவிலோ அல்லது உறவினர்கள் மூலமாகவோ குலதெய்வ அடையாளம் துல்லியமாக வெளிப்படும்.",
            ],
            steps_en=[
                "1. Clean the home altar early morning on an Amavasya or the first day of a Tamil solar month.",
                "2. Spread raw rice on a clean wooden plank and place a brass Kamakshi deepam upon it.",
                "3. Fill the lamp with pure cow's ghee or sesame oil with cotton wick facing East.",
                "4. Pray whole-heartedly: 'O Benevolent Lineage Deity, forgive our inadvertent ignorance and unveil your sacred shrine to our family'.",
                "5. Inquire with elder relatives or ancestral village pangalis about old clan migrations.",
                "6. Maintain the evening lamp lighting for 48 consecutive days (one mandala) or 9 consecutive Fridays; revelation inevitably surfaces through dreams or ancestral elder contacts.",
            ],
            deepam_procedure_ta="மாவிளக்கு தீபம்: பச்சரிசி மாவில் வெல்லம், ஏலக்காய் மற்றும் பசு நெய் கலந்து உருண்டையாக்கி, அதன் நடுவில் குழி செய்து நெய் ஊற்றி திரி இட்டு ஏற்றுவது மிகுந்த சக்தி வாய்ந்த பரிகாரமாகும்.",
            deepam_procedure_en="Maa-Vilakku Deepam: A sacred dough lamp prepared from soaked raw rice flour, jaggery, cardamom, and pure ghee. Lighting this lamp dissolves generational karmic obscurations.",
            pongal_offering_ta="பச்சரிசி, பாசிப்பருப்பு, வெல்லம் மற்றும் பசும்பால் கொண்டு புது மண்பானையில் பொங்கல் வைத்து, தலைவாழை இலையில் படைத்து குடும்பத்தோடு வழிபட வேண்டும்.",
            pongal_offering_en="Prepare traditional sweet pongal in an earthen pot with newly harvested raw rice, jaggery, and cow's milk, offering it on a plantain leaf.",
            coin_knot_ritual_ta="மஞ்சள் துணி முடிப்பு: ஒரு புதிய மஞ்சள் துணியில் ஒரு வெள்ளி நாணயம் அல்லது 5 ரூபாய் நாணயத்தை வைத்து, அதில் சிறிது பச்சரிசி மற்றும் மஞ்சள் பொடி சேர்த்து முடிந்து, 'குலதெய்வ காணிக்கை' என்று பூசை அறையில் வைத்து வணங்கவும். ஆலயம் தெரிந்ததும் அதை அங்கு சமர்ப்பிக்க வேண்டும்.",
            coin_knot_ritual_en="Yellow Cloth Coin Knot: Place a sanctified coin with unbroken raw rice in a yellow cloth, tie it securely as a dedicated pledge, and keep it in the puja room until you visit the ancestral shrine.",
            universal_refuge_temples=UNIVERSAL_REFUGE_TEMPLES,
        )

        fifth_house_obj = HouseAnalysisDetails(
            house_num=5,
            sign_name_ta=ZODIAC_NAMES_TA[fifth_from_aarudham],
            sign_name_en=ZODIAC_NAMES_EN[fifth_from_aarudham],
            sign_lord_ta=GRAHA_NAMES_TA.get(fifth_lord, fifth_lord),
            sign_lord_en=fifth_lord,
            sign_tattva_ta=SIGN_TATTVA[fifth_from_aarudham][1],
            sign_tattva_en=SIGN_TATTVA[fifth_from_aarudham][0],
            sign_gender_ta=SIGN_GENDER[fifth_from_aarudham][1],
            sign_gender_en=SIGN_GENDER[fifth_from_aarudham][0],
            occupants_ta=[],
            occupants_en=[],
            aspecting_grahas_ta=[],
            aspecting_grahas_en=[],
            navamsha_sign_ta=ZODIAC_NAMES_TA[fifth_from_aarudham],
            navamsha_sign_en=ZODIAC_NAMES_EN[fifth_from_aarudham],
            navamsha_lord_ta=GRAHA_NAMES_TA.get(fifth_lord, fifth_lord),
            navamsha_lord_en=fifth_lord,
        )

        ninth_house_obj = HouseAnalysisDetails(
            house_num=9,
            sign_name_ta=ZODIAC_NAMES_TA[ninth_from_aarudham],
            sign_name_en=ZODIAC_NAMES_EN[ninth_from_aarudham],
            sign_lord_ta=GRAHA_NAMES_TA.get(ninth_lord, ninth_lord),
            sign_lord_en=ninth_lord,
            sign_tattva_ta=SIGN_TATTVA[ninth_from_aarudham][1],
            sign_tattva_en=SIGN_TATTVA[ninth_from_aarudham][0],
            sign_gender_ta=SIGN_GENDER[ninth_from_aarudham][1],
            sign_gender_en=SIGN_GENDER[ninth_from_aarudham][0],
            occupants_ta=[],
            occupants_en=[],
            aspecting_grahas_ta=[],
            aspecting_grahas_en=[],
            navamsha_sign_ta=ZODIAC_NAMES_TA[ninth_from_aarudham],
            navamsha_sign_en=ZODIAC_NAMES_EN[ninth_from_aarudham],
            navamsha_lord_ta=GRAHA_NAMES_TA.get(ninth_lord, ninth_lord),
            navamsha_lord_en=ninth_lord,
        )

        lineage_insights_ta = [
            f"பிரசன்ன ஆருட ராசி: {ZODIAC_NAMES_TA[aarudham_sign]}. உதயம்: {ZODIAC_NAMES_TA[udhayam_sign]}.",
            f"ஆருடத்திற்கு 9-ஆம் பித்ரு குலதெய்வ ஸ்தானம்: {ZODIAC_NAMES_TA[ninth_from_aarudham]} ({SIGN_TATTVA[ninth_from_aarudham][1]}).",
            f"முதன்மைக் குலதெய்வம்: {primary_indicator.deity_name_ta}.",
            f"ஆலயத் திசை: {prim_dir_ta}.",
        ]

        lineage_insights_en = [
            f"Prasna Aarudham: {ZODIAC_NAMES_EN[aarudham_sign]}, Udhayam: {ZODIAC_NAMES_EN[udhayam_sign]}.",
            f"9th House of Ancestry from Aarudham: {ZODIAC_NAMES_EN[ninth_from_aarudham]} ({SIGN_TATTVA[ninth_from_aarudham][0]}).",
            f"Primary Deity: {primary_indicator.deity_name_en}.",
            f"Temple Direction: {prim_dir_en}.",
        ]

        classical_references = [
            "Jamakkol Prasanam Arudha Sastra: Lineage indicators from Aarudham & Udhayam.",
            "Prasna Marga: Deva Prasna Chapter 15 (Clan Deities & Ancestral worship).",
        ]

        return KuladeivamResponse(
            analysis_mode="prasanna",
            native_summary={
                "query_datetime": req.query_datetime,
                "udhayam_ta": ZODIAC_NAMES_TA[udhayam_sign],
                "udhayam_en": ZODIAC_NAMES_EN[udhayam_sign],
                "aarudham_ta": ZODIAC_NAMES_TA[aarudham_sign],
                "aarudham_en": ZODIAC_NAMES_EN[aarudham_sign],
                "kavippu_ta": ZODIAC_NAMES_TA[kavippu_sign],
                "kavippu_en": ZODIAC_NAMES_EN[kavippu_sign],
                "ancestral_district": req.ancestral_district or "Tamil Nadu Ancestral Roots",
            },
            fifth_house=fifth_house_obj,
            ninth_house=ninth_house_obj,
            primary_deity=primary_indicator,
            secondary_deity=secondary_indicator,
            temple_landscape=landscape,
            dosha_analysis=dosha_status,
            discovery_protocol=discovery_protocol,
            lineage_insights_ta=lineage_insights_ta,
            lineage_insights_en=lineage_insights_en,
            classical_references=classical_references,
        )
