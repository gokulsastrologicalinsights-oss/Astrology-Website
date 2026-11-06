"""Jamakkol Prasanam constants, tables, and foundational astrological metadata.

Codified according to classical Tamil Jamakkol Shastra (e.g. S.R. Santhanam,
Sage Romarishi traditions, and Vaidiyanathan Horary systems).
"""

from typing import Dict, Any, List, Tuple

# 12 Zodiac signs in order (1=Aries ... 12=Pisces)
ZODIAC_SIGNS: Dict[int, Dict[str, Any]] = {
    1: {
        "name_en": "Aries",
        "name_ta": "மேஷம்",
        "lord_en": "Mars",
        "lord_ta": "செவ்வாய்",
        "element": "Fire",
        "nature": "Chara",
        "nature_ta": "சரம்",
        "rising_nature": "Pristodaya",
        "rising_nature_ta": "பிருஷ்டோதய ராசி",
        "direction_en": "East",
        "direction_ta": "கிழக்கு",
        "degrees_start": 0.0,
    },
    2: {
        "name_en": "Taurus",
        "name_ta": "ரிஷபம்",
        "lord_en": "Venus",
        "lord_ta": "சுக்கிரன்",
        "element": "Earth",
        "nature": "Sthira",
        "nature_ta": "ஸ்திரம்",
        "rising_nature": "Pristodaya",
        "rising_nature_ta": "பிருஷ்டோதய ராசி",
        "direction_en": "South-East (Agni)",
        "direction_ta": "தென்கிழக்கு (ஆக்னேயம்)",
        "degrees_start": 30.0,
    },
    3: {
        "name_en": "Gemini",
        "name_ta": "மிதுனம்",
        "lord_en": "Mercury",
        "lord_ta": "புதன்",
        "element": "Air",
        "nature": "Ubhaya",
        "nature_ta": "உபயம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "South",
        "direction_ta": "தெற்கு",
        "degrees_start": 60.0,
    },
    4: {
        "name_en": "Cancer",
        "name_ta": "கடகம்",
        "lord_en": "Moon",
        "lord_ta": "சந்திரன்",
        "element": "Water",
        "nature": "Chara",
        "nature_ta": "சரம்",
        "rising_nature": "Pristodaya",
        "rising_nature_ta": "பிருஷ்டோதய ராசி",
        "direction_en": "South-West (Nirruthi)",
        "direction_ta": "தென்மேற்கு (நைருதி)",
        "degrees_start": 90.0,
    },
    5: {
        "name_en": "Leo",
        "name_ta": "சிம்மம்",
        "lord_en": "Sun",
        "lord_ta": "சூரியன்",
        "element": "Fire",
        "nature": "Sthira",
        "nature_ta": "ஸ்திரம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "West",
        "direction_ta": "மேற்கு",
        "degrees_start": 120.0,
    },
    6: {
        "name_en": "Virgo",
        "name_ta": "கன்னி",
        "lord_en": "Mercury",
        "lord_ta": "புதன்",
        "element": "Earth",
        "nature": "Ubhaya",
        "nature_ta": "உபயம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "North-West (Vayu)",
        "direction_ta": "வடமேற்கு (வாயுவியம்)",
        "degrees_start": 150.0,
    },
    7: {
        "name_en": "Libra",
        "name_ta": "துலாம்",
        "lord_en": "Venus",
        "lord_ta": "சுக்கிரன்",
        "element": "Air",
        "nature": "Chara",
        "nature_ta": "சரம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "North",
        "direction_ta": "வடக்கு",
        "degrees_start": 180.0,
    },
    8: {
        "name_en": "Scorpio",
        "name_ta": "விருச்சிகம்",
        "lord_en": "Mars",
        "lord_ta": "செவ்வாய்",
        "element": "Water",
        "nature": "Sthira",
        "nature_ta": "ஸ்திரம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "North-East (Easanya)",
        "direction_ta": "வடகிழக்கு (ஈசானியம்)",
        "degrees_start": 210.0,
    },
    9: {
        "name_en": "Sagittarius",
        "name_ta": "தனுசு",
        "lord_en": "Jupiter",
        "lord_ta": "குரு",
        "element": "Fire",
        "nature": "Ubhaya",
        "nature_ta": "உபயம்",
        "rising_nature": "Pristodaya",
        "rising_nature_ta": "பிருஷ்டோதய ராசி",
        "direction_en": "East",
        "direction_ta": "கிழக்கு",
        "degrees_start": 240.0,
    },
    10: {
        "name_en": "Capricorn",
        "name_ta": "மகரம்",
        "lord_en": "Saturn",
        "lord_ta": "சனி",
        "element": "Earth",
        "nature": "Chara",
        "nature_ta": "சரம்",
        "rising_nature": "Pristodaya",
        "rising_nature_ta": "பிருஷ்டோதய ராசி",
        "direction_en": "South",
        "direction_ta": "தெற்கு",
        "degrees_start": 270.0,
    },
    11: {
        "name_en": "Aquarius",
        "name_ta": "கும்பம்",
        "lord_en": "Saturn",
        "lord_ta": "சனி",
        "element": "Air",
        "nature": "Sthira",
        "nature_ta": "ஸ்திரம்",
        "rising_nature": "Sirosodayam",
        "rising_nature_ta": "சிரோதய ராசி",
        "direction_en": "West",
        "direction_ta": "மேற்கு",
        "degrees_start": 300.0,
    },
    12: {
        "name_en": "Pisces",
        "name_ta": "மீனம்",
        "lord_en": "Jupiter",
        "lord_ta": "குரு",
        "element": "Water",
        "nature": "Ubhaya",
        "nature_ta": "உபயம்",
        "rising_nature": "Siropristodaya",
        "rising_nature_ta": "சிரோபிருஷ்டோதய ராசி",
        "direction_en": "North",
        "direction_ta": "வடக்கு",
        "degrees_start": 330.0,
    },
}

# The 8 signs that house the 8 Jama Grahas in anti-clockwise sequence from Pisces (skipping 4 Fixed signs)
JAMA_SIGNS_ANTICLOCKWISE: List[int] = [12, 10, 9, 7, 6, 4, 3, 1]

# 8 Jamakkol Planets
JAMA_GRAHAS: List[Dict[str, Any]] = [
    {
        "id": "sun",
        "name_en": "Sun",
        "name_ta": "சூரியன்",
        "symbol": "☉",
        "classical_name_ta": "கதிர்",
        "is_benefic": False,
        "signification_en": "Father, Elder son, Heart, Right eye, Gold, Government, Status",
        "signification_ta": "தந்தை, மூத்த மகன், இதயம், வலது கண், தங்கம், அரசு விவகாரம், அந்தஸ்து",
        "color": "#F59E0B",
    },
    {
        "id": "mars",
        "name_en": "Mars",
        "name_ta": "செவ்வாய்",
        "symbol": "♂",
        "classical_name_ta": "சேய்",
        "is_benefic": False,
        "signification_en": "Brother, Land/Property, Husband, Ego, Quarrels, Fights, Skills, Sports, Surgery",
        "signification_ta": "சகோதரன், பூமி/நிலம், கணவர், அகந்தை, சண்டை, தகராறு, திறமை, விளையாட்டு, அறுவை சிகிச்சை",
        "color": "#EF4444",
    },
    {
        "id": "jupiter",
        "name_en": "Jupiter",
        "name_ta": "குரு",
        "symbol": "♃",
        "classical_name_ta": "பொன்",
        "is_benefic": True,
        "signification_en": "Children, Extreme wealth/money, Temple, Teacher, Higher education, Ancestors, Share market, Bank",
        "signification_ta": "புத்திர பாக்கியம், பெரும் செல்வம், ஆலயம், குரு/ஆசிரியர், உயர்கல்வி, முன்னோர்கள், பங்குச்சந்தை, வங்கி",
        "color": "#EAB308",
    },
    {
        "id": "mercury",
        "name_en": "Mercury",
        "name_ta": "புதன்",
        "symbol": "☿",
        "classical_name_ta": "மால்",
        "is_benefic": True,
        "signification_en": "Children, Education, Vacant land, Love affair, Agreement, Contract, Documents, Share market, Partnership",
        "signification_ta": "கல்வி, காலி மனை/நிலம், காதல், ஒப்பந்தம், பத்திரங்கள், பங்குச்சந்தை, வியாபாரக் கூட்டு",
        "color": "#10B981",
    },
    {
        "id": "venus",
        "name_en": "Venus",
        "name_ta": "சுக்கிரன்",
        "symbol": "♀",
        "classical_name_ta": "சுக்கிரன்",
        "is_benefic": True,
        "signification_en": "Wife, Love, Romance, Love marriage, Money, Female, Luxury vehicles",
        "signification_ta": "மனைவி, காதல், களத்திரம், காதல் திருமணம், பணம், பெண் விவகாரங்கள், ஆடம்பரம், வாகனம்",
        "color": "#EC4899",
    },
    {
        "id": "saturn",
        "name_en": "Saturn",
        "name_ta": "சனி",
        "symbol": "♄",
        "classical_name_ta": "சனி",
        "is_benefic": False,
        "signification_en": "Job, Profession, Longevity, Fear of death, Servants, Delay, Dilapidated building, Knees",
        "signification_ta": "வேலை, உத்தியோகம், ஆயுள், மரண பயம், வேலையாட்கள், காலதாமதம், பாழடைந்த வீடு, முழங்கால்",
        "color": "#6366F1",
    },
    {
        "id": "moon",
        "name_en": "Moon",
        "name_ta": "சந்திரன்",
        "symbol": "☽",
        "classical_name_ta": "மதி",
        "is_benefic": True,
        "signification_en": "Thoughts, Mother, Mother-in-law, Food items, Secret contacts, Event happens fast",
        "signification_ta": "மன எண்ணங்கள், தாய், மாமியார், உணவுப் பண்டங்கள், ரகசிய தொடர்புகள், காரியம் அதிவேகமாக நடக்கும்",
        "color": "#38BDF8",
    },
    {
        "id": "snake",
        "name_en": "Snake",
        "name_ta": "பாம்பு",
        "symbol": "☊",
        "classical_name_ta": "பாம்பு",
        "is_benefic": False,
        "signification_en": "Foreign contact, Pressure, Problems, Conception, Change of place, Evil spirits, Paranormal, Loans",
        "signification_ta": "வெளிநாட்டு தொடர்பு, மன அழுத்தம், சிக்கல்கள், கருத்தரித்தல், இடமாற்றம், அமானுஷ்யம், கடன் வாங்குதல்",
        "color": "#8B5CF6",
    },
]

JAMA_GRAHA_INDEX: Dict[str, int] = {g["id"]: idx for idx, g in enumerate(JAMA_GRAHAS)}

WEEKDAY_TO_DAY_LORD: Dict[int, str] = {
    6: "sun",
    0: "moon",
    1: "mars",
    2: "mercury",
    3: "jupiter",
    4: "venus",
    5: "saturn",
}

NIGHT_START_LORD: Dict[str, str] = {
    "sun": "jupiter",
    "moon": "venus",
    "mars": "saturn",
    "mercury": "sun",
    "jupiter": "moon",
    "venus": "mars",
    "saturn": "mercury",
}

SURYA_VEETHI_RULES: Dict[int, Dict[str, Any]] = {
    2: {"veethi_id": "mesha", "name_en": "Mesha Veethi", "name_ta": "மேஷ வீதி", "anchor_sign": 1},
    3: {"veethi_id": "mesha", "name_en": "Mesha Veethi", "name_ta": "மேஷ வீதி", "anchor_sign": 1},
    4: {"veethi_id": "mesha", "name_en": "Mesha Veethi", "name_ta": "மேஷ வீதி", "anchor_sign": 1},
    5: {"veethi_id": "mesha", "name_en": "Mesha Veethi", "name_ta": "மேஷ வீதி", "anchor_sign": 1},

    12: {"veethi_id": "rishabha", "name_en": "Rishabha Veethi", "name_ta": "ரிஷப வீதி", "anchor_sign": 2},
    1: {"veethi_id": "rishabha", "name_en": "Rishabha Veethi", "name_ta": "ரிஷப வீதி", "anchor_sign": 2},
    6: {"veethi_id": "rishabha", "name_en": "Rishabha Veethi", "name_ta": "ரிஷப வீதி", "anchor_sign": 2},
    7: {"veethi_id": "rishabha", "name_en": "Rishabha Veethi", "name_ta": "ரிஷப வீதி", "anchor_sign": 2},

    8: {"veethi_id": "mithuna", "name_en": "Mithuna Veethi", "name_ta": "மிதுன வீதி", "anchor_sign": 3},
    9: {"veethi_id": "mithuna", "name_en": "Mithuna Veethi", "name_ta": "மிதுன வீதி", "anchor_sign": 3},
    10: {"veethi_id": "mithuna", "name_en": "Mithuna Veethi", "name_ta": "மிதுன வீதி", "anchor_sign": 3},
    11: {"veethi_id": "mithuna", "name_en": "Mithuna Veethi", "name_ta": "மிதுன வீதி", "anchor_sign": 3},
}

DIRECTIONS_MAP: Dict[int, Dict[str, str]] = {
    1: {"en": "East", "ta": "கிழக்கு", "ruler": "Sun / Indra"},
    2: {"en": "South-East (Agni)", "ta": "தென்கிழக்கு (ஆக்னேயம்)", "ruler": "Venus / Agni"},
    3: {"en": "South", "ta": "தெற்கு", "ruler": "Mars / Yama"},
    4: {"en": "South-West (Nirruthi)", "ta": "தென்மேற்கு (நைருதி)", "ruler": "Rahu / Nirruthi"},
    5: {"en": "West", "ta": "மேற்கு", "ruler": "Saturn / Varuna"},
    6: {"en": "North-West (Vayu)", "ta": "வடமேற்கு (வாயுவியம்)", "ruler": "Moon / Vayu"},
    7: {"en": "North", "ta": "வடக்கு", "ruler": "Mercury / Kubera"},
    8: {"en": "North-East (Easanya)", "ta": "வடகிழக்கு (ஈசானியம்)", "ruler": "Jupiter / Easanya"},
    9: {"en": "East", "ta": "கிழக்கு", "ruler": "Sun / Indra"},
    10: {"en": "South", "ta": "தெற்கு", "ruler": "Mars / Yama"},
    11: {"en": "West", "ta": "மேற்கு", "ruler": "Saturn / Varuna"},
    12: {"en": "North", "ta": "வடக்கு", "ruler": "Jupiter / Kubera"},
}

PLANET_DIGNITIES: Dict[str, Dict[str, int]] = {
    "Sun": {"exalted": 1, "debilitated": 7},
    "Moon": {"exalted": 2, "debilitated": 8},
    "Mars": {"exalted": 10, "debilitated": 4},
    "Mercury": {"exalted": 6, "debilitated": 12},
    "Jupiter": {"exalted": 4, "debilitated": 10},
    "Venus": {"exalted": 12, "debilitated": 6},
    "Saturn": {"exalted": 7, "debilitated": 1},
    "Rahu": {"exalted": 2, "debilitated": 8},
    "Ketu": {"exalted": 8, "debilitated": 2},
}

SIGN_LORDS: Dict[int, str] = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}

SUBH_UDAYAM_SIGNS: List[int] = [5, 6, 7, 8, 9, 10]
SUBH_ARUDAM_SIGNS: List[int] = [11, 12, 1, 2, 3, 4]

# Relationships Karakatwas Table
RELATIONSHIP_KARAKAS: Dict[str, Dict[str, Any]] = {
    "father": {"planet": "Sun", "en": "Father / Father-in-law", "ta": "தந்தை / மாமனார்", "house": 9},
    "eldest_son": {"planet": "Sun", "en": "Eldest Son", "ta": "மூத்த மகன்", "house": 5},
    "mother": {"planet": "Moon", "en": "Mother / Mother-in-law", "ta": "தாய் / மாமியார்", "house": 4},
    "eldest_sister": {"planet": "Moon", "en": "Eldest Sister", "ta": "மூத்த சகோதரி", "house": 11},
    "brother": {"planet": "Mars", "en": "Brother / Brother-in-law", "ta": "சகோதரன் / மைத்துனன்", "house": 3},
    "husband": {"planet": "Mars", "en": "Husband", "ta": "கணவர்", "house": 7},
    "uncle": {"planet": "Mercury", "en": "Maternal Uncle", "ta": "தாய்மாமன்", "house": 6},
    "second_sibling": {"planet": "Mercury", "en": "2nd Brother / 2nd Sister", "ta": "இரண்டாம் சகோதரன்/சகோதரி", "house": 3},
    "affair": {"planet": "Mercury", "en": "Love Affair / Secret Alliance", "ta": "காதல் / ரகசிய தொடர்பு", "house": 5},
    "wife": {"planet": "Venus", "en": "Wife", "ta": "மனைவி", "house": 7},
    "daughter_in_law": {"planet": "Venus", "en": "Daughter-in-law", "ta": "மருமகள்", "house": 9},
    "aunt": {"planet": "Venus", "en": "Aunt / Younger Sister", "ta": "அத்தை / சித்தி / இளைய சகோதரி", "house": 3},
    "son_in_law": {"planet": "Jupiter", "en": "Son-in-law", "ta": "மருமகன்", "house": 11},
    "elder_brother": {"planet": "Jupiter", "en": "Father's Elder Brother / Elder Brother", "ta": "பெரியப்பா / மூத்த சகோதரன்", "house": 11},
    "children": {"planet": "Jupiter", "en": "Children (Son/Daughter)", "ta": "குழந்தைகள் / புத்திரர்கள்", "house": 5},
    "younger_uncle": {"planet": "Saturn", "en": "Father's Younger Brother", "ta": "சித்தப்பா", "house": 3},
    "servants": {"planet": "Saturn", "en": "Servants / Subordinates", "ta": "பணியாளர்கள் / வேலையாட்கள்", "house": 6},
    "grandparents": {"planet": "Snake", "en": "Grandfather / Grandmother", "ta": "தாத்தா / பாட்டி", "house": 9},
}

# Politics and Government Posts Karakas
GOVT_POLITICS_KARAKAS: Dict[str, Dict[str, Any]] = {
    "president": {"planets": ["Sun"], "en": "President of Nation", "ta": "நாட்டின் ஜனாதிபதி / முதன்மை தலைவர்"},
    "prime_minister": {"planets": ["Sun", "Jupiter"], "en": "Prime Minister", "ta": "பிரதம மந்திரி"},
    "minister_state_head": {"planets": ["Sun"], "en": "State Head / Chief Minister / Any Minister", "ta": "முதலமைச்சர் / மந்திரி"},
    "mp": {"planets": ["Jupiter"], "en": "Member of Parliament (MP)", "ta": "நாடாளுமன்ற உறுப்பினர் (MP)"},
    "mla": {"planets": ["Sun", "Mars"], "en": "Member of Legislative Assembly (MLA)", "ta": "சட்டமன்ற உறுப்பினர் (MLA)"},
    "central_cabinet": {"planets": ["Sun"], "en": "Central Cabinet Minister", "ta": "மத்திய கேபினட் அமைச்சர்"},
    "defense_dept": {"planets": ["Snake", "Mars"], "en": "Defense Department (Military / Security)", "ta": "பாதுகாப்புத் துறை / ராணுவம்"},
    "police_dept": {"planets": ["Mars"], "en": "Police Department / Law Enforcement", "ta": "காவல்துறை"},
    "teacher": {"planets": ["Jupiter", "Mercury"], "en": "Teacher / Professor / Education Head", "ta": "ஆசிரியர் / பேராசிரியர் / கல்வி அதிகாரி"},
    "auditor_ca": {"planets": ["Mercury"], "en": "Chartered Accountant (CA) / Auditor", "ta": "தணிக்கையாளர் / சி.ஏ (CA)"},
    "physician_doctor": {"planets": ["Sun", "Ketu"], "en": "Physician / Medical Doctor", "ta": "மருத்துவர்"},
    "judge": {"planets": ["Jupiter", "Ketu"], "en": "Judge / Magistrate", "ta": "நீதிபதி"},
    "lawyer": {"planets": ["Saturn", "Ketu"], "en": "Lawyer / Advocate", "ta": "வழக்கறிஞர்"},
    "bank": {"planets": ["Venus", "Jupiter"], "en": "Banker / Financial Officer", "ta": "வங்கி அதிகாரி"},
    "panchayat_election": {"planets": ["Saturn"], "en": "Panchayat Election / Local Body Head", "ta": "பஞ்சாயத்து தலைவர் / உள்ளாட்சி பதவி"},
}

# Commodities for Share Market
COMMODITY_KARAKAS: Dict[str, Dict[str, Any]] = {
    "gold": {"planet": "Sun", "en": "Gold & Sovereign Metals", "ta": "தங்கம் & விலைமதிப்பற்ற உலோகம்"},
    "silver": {"planet": "Moon", "en": "Silver, Liquid & Dairy Commodities", "ta": "வெள்ளி, திரவப் பொருட்கள் & பால்வளம்"},
    "copper_real_estate": {"planet": "Mars", "en": "Copper, Red Chillies, Real Estate, Steel", "ta": "செம்பு, மிளகாய், ரியல் எஸ்டேட், உலோகம்"},
    "grains_textiles": {"planet": "Mercury", "en": "Grains, Green Pulses, Paper & Media", "ta": "தானியங்கள், பருப்பு வகைகள், காகிதம், தகவல் தொடர்பு"},
    "turmeric_yellow_pulses": {"planet": "Jupiter", "en": "Turmeric (Haldi), Yellow Pulses, Banking", "ta": "மஞ்சள், பருப்பு வகைகள், நிதித்துறை"},
    "sugar_diamond": {"planet": "Venus", "en": "Sugar, Diamond, Luxury, Cotton, Vehicles", "ta": "சர்க்கரை, வைரம், ஆடம்பரம், பருத்தி, ஆட்டோமொபைல்"},
    "oil_iron": {"planet": "Saturn", "en": "Crude Oil, Petroleum, Iron, Coal, Heavy Industries", "ta": "கச்சா எண்ணெய், பெட்ரோலியம், இரும்பு, நிலக்கரி"},
}

PLANET_QUERY_KARAKATWAS: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "en": "Father, Elder son, Heart, Right eye, Gold, Government, Status",
        "ta": "தந்தை, மூத்த மகன், இதயம், வலது கண், தங்கம், அரசு காரியங்கள், அந்தஸ்து",
    },
    "Moon": {
        "en": "Thoughts, Mother, Mother-in-Law, Food items, Secret contacts, Event happens fast",
        "ta": "மன எண்ணங்கள், தாய், மாமியார், உணவுப் பண்டங்கள், ரகசிய தொடர்புகள் (சந்திரன் வந்தால் காரியம் மிக வேகமாக நடக்கும்)",
    },
    "Mars": {
        "en": "Brother, Land/Property, Husband, Ego, Quarrels, Fights, Skills, Sports, Surgery",
        "ta": "சகோதரன், பூமி/நிலம், கணவர், அகந்தை, சண்டை சச்சரவு, திறமை, விளையாட்டு, அறுவை சிகிச்சை",
    },
    "Mercury": {
        "en": "Children, Education, Vacant land, Love affair, Agreement, Contract, Documents, Share market, Partnership",
        "ta": "குழந்தைகள், கல்வி, காலி மனை, காதல், உடன்படிக்கை, பத்திரங்கள், பங்குச்சந்தை, வியாபார கூட்டு",
    },
    "Venus": {
        "en": "Wife, Love, Romance, Love marriage, Money, Female, Luxury assets",
        "ta": "மனைவி, காதல், அன்பு, காதல் திருமணம், பணம், பெண் விவகாரங்கள், ஆடம்பர சுகபோகம்",
    },
    "Jupiter": {
        "en": "Children, Money (extreme wealth), Temple, Teacher, Higher education, Ancestors, Share market, Bank",
        "ta": "புத்திரர்கள், பெரும் தன லாபம், கோவில், ஆசிரியர்/குரு, உயர்கல்வி, முன்னோர்கள், வங்கி",
    },
    "Saturn": {
        "en": "Job, Profession, Longevity, Fear of death, Servants, Delay, Dilapidated building, Knees",
        "ta": "உத்தியோகம், தொழில், ஆயுள், மரண பயம், வேலையாட்கள், காலதாமதம், பாழடைந்த வீடு, முழங்கால்",
    },
    "Snake": {
        "en": "Foreign contact, Pressure, Problems, Conception, Change of place, Evil spirits, Paranormal experiences, Loans",
        "ta": "வெளிநாட்டு தொடர்பு, மன அழுத்தம், சிக்கல்கள், கருவுறுதல், இடமாற்றம், அமானுஷ்யம், கடன் வாங்குதல்",
    },
    "Rahu": {
        "en": "Foreign contact, Pressure, Problems, Conception, Change of place, Evil spirits, Paranormal experiences, Loans",
        "ta": "வெளிநாட்டு தொடர்பு, மன அழுத்தம், சிக்கல்கள், கருவுறுதல், இடமாற்றம், அமானுஷ்யம், கடன் வாங்குதல்",
    },
    "Ketu": {
        "en": "Spiritual liberation, Renunciation, Medical diagnosis, Hidden obstacles, Surgery",
        "ta": "மோட்சம், ஆன்மீகம், மருத்துவம், மறைமுக தடைகள், திடீர் விலகல்",
    },
}

# Classical 12 Bhava Effects of Kavippu from Udayam
KAVIPPU_BHAVA_EFFECTS: Dict[int, Dict[str, Any]] = {
    1: {
        "en": "Sitting in 1st House (with Udayam): Answer is NEGATIVE for every question that is beneficial for querent; mental crisis and personal block.",
        "ta": "1-ல் கவிப்பு (உதயத்தில்): கேள்வியாளருக்கு நன்மை தரும் அனைத்து காரியங்களுக்கும் பதில் 'இல்லை/தோல்வி'; மன அழுத்தம், உடல் உபாதை.",
    },
    2: {
        "en": "Kavippu in 2nd House: Problems in family = YES; Money coming = NO; Eye surgery / Lie / Deceit = YES.",
        "ta": "2-ல் கவிப்பு: குடும்பத்தில் குழப்பம் = உண்டு; வரவேண்டிய பணம் வருவது = இல்லை; கண் அறுவை சிகிச்சை / பொய் / ஏமாற்றம் = உண்டு.",
    },
    3: {
        "en": "Kavippu in 3rd House: Problems from siblings = YES; Business with them = NO; Documentation blemish; Short travel = NO.",
        "ta": "3-ல் கவிப்பு: சகோதரர்களால் சிக்கல் = உண்டு; அவர்களுடன் கூட்டு = கூடாது; ஆவணங்களில் குளறுபடி; பயணங்கள் தடைபடும்.",
    },
    4: {
        "en": "Kavippu in 4th House: New home / Land purchase = NO; Mother recover from disease = NO; Agriculture / Borewell water = NO.",
        "ta": "4-ல் கவிப்பு: புதிய வீடு/மனை வாங்குதல் = தடை; தாய் நலம் பெறுவது = இல்லை; விவசாயம் / போர்வெல் தண்ணீர் கிடைப்பது = இல்லை.",
    },
    5: {
        "en": "Kavippu in 5th House: Get a child = NO; Buy shares = NO; Ancestral property = NO; Politics power = NO; Love affair success = NO.",
        "ta": "5-ல் கவிப்பு: புத்திர பாக்கியம் = இல்லை; பங்குச்சந்தை லாபம் = நஷ்டம்; பூர்வீக சொத்து / அரசியல் பதவி / காதல் வெற்றி = இல்லை.",
    },
    6: {
        "en": "Kavippu in 6th House: Problems after loan = YES; Job problem = YES; Disease recover = NO; Get servant / loan = NO.",
        "ta": "6-ல் கவிப்பு: கடன் வாங்குவது = சிக்கல்; உத்தியோக நெருக்கடி = உண்டு; நோய் குணமாவது = தாமதம்; புதிய கடன் கிடைப்பது = இல்லை.",
    },
    7: {
        "en": "Kavippu in 7th House: Wife illness = No recovery; Partnership business = NO; Court case = QUERENT WINS (Opposition defeated!).",
        "ta": "7-ல் கவிப்பு: மனைவி உடல் நலம் = சுமாரானது; வியாபார கூட்டு = கூடாது; நீதிமன்ற வழக்கில் = கேள்வியாளருக்கு வெற்றி (எதிரி தோல்வி)!",
    },
    8: {
        "en": "Kavippu in 8th House: Insurance claim = NO; Disgrace, shame, death, lost document = Will NOT be recovered.",
        "ta": "8-ல் கவிப்பு: இன்சூரன்ஸ் தொகை கிடைப்பது = இல்லை; அவமானம், கண்டம், காணாமல் போன ஆவணங்கள் கிடைப்பது = இல்லை.",
    },
    9: {
        "en": "Kavippu in 9th House: Father health cure = NO; Foreign travel = NO; Higher education = NO; Lottery/fortune = NO.",
        "ta": "9-ல் கவிப்பு: தந்தை உடல் நலம் = சுமாரானது; வெளிநாட்டுப் பயணம் = ரத்து; உயர்கல்வி / அதிர்ஷ்டம் = இல்லை.",
    },
    10: {
        "en": "Kavippu in 10th House: Job / Profession promotion = NO; New business launch = NO.",
        "ta": "10-ல் கவிப்பு: உத்தியோக உயர்வு / பதவி உயர்வு = இல்லை; புதிய தொழில் தொடங்குவது = தடை.",
    },
    11: {
        "en": "Kavippu in 11th House: Fulfilment of desire = NO; In most cases results are negative / Denial of profit.",
        "ta": "11-ல் கவிப்பு: நினைத்த காரியம் நிறைவேறுவது = இல்லை; லாபம் கிட்டுவது = முடக்கம்; பெரும்பான்மை காரியங்கள் தோல்வி.",
    },
    12: {
        "en": "Kavippu in 12th House: Foreign visa = NO; Imprisonment / Legal penalty = YES; Medical expenses & Hospitalization = YES.",
        "ta": "12-ல் கவிப்பு: வெளிநாட்டு விசா = இல்லை; தண்டனை / சிறைவாசம் = எச்சரிக்கை; மருத்துவ விரயம் & மருத்துவமனை = உண்டு.",
    },
}

# Classical 12 Bhava Effects of Udayam Lord (Querent's Inner Thoughts)
UDAYAM_LORD_THOUGHT_EFFECTS: Dict[int, Dict[str, Any]] = {
    1: {"en": "Self, physical body, personal reputation, health problems.", "ta": "சுய கௌரவம், உடல் நலம், தலைமை, சொந்த விவகாரம்."},
    2: {"en": "Income, money coming, family matters, eye issues.", "ta": "பணம், குடும்ப விவகாரம், வரவு, கண் சிகிச்சை."},
    3: {"en": "Communication, siblings, short travel, change of place, documents.", "ta": "தொடர்பு, சகோதரம், இடமாற்றம், குறுகிய பயணம், பத்திரங்கள்."},
    4: {"en": "House, mother, stolen items, vehicles, education, land.", "ta": "வீடு, தாய் நலம், வாகனம், கல்வி, திருட்டுப் பொருள், சொத்து."},
    5: {"en": "Children, love affair, speculative planning, politics, mantra.", "ta": "குழந்தைகள், காதல், பங்குச்சந்தை, அரசியல், தெய்வ வழிபாடு."},
    6: {"en": "Loan, debt, disease, court case, dispute, servants.", "ta": "கடன், நோய், வழக்கு, எதிரிகள், வேலையாட்கள்."},
    7: {"en": "Marriage, partnership, business, spouse, opponent, second child.", "ta": "திருமணம், கூட்டுத் தொழில், கணவன்/மனைவி, எதிராளி."},
    8: {"en": "Longevity, disgrace, surgery, high interest, sudden losses, insurance, will.", "ta": "ஆயுள், திடீர் இழப்பு, அறுவை சிகிச்சை, அவமானம், உயில், இன்சூரன்ஸ்."},
    9: {"en": "Father, foreign travel, higher education, guru, initiation, 2nd marriage.", "ta": "தந்தை, வெளிநாடு, உயர்கல்வி, குரு, ஆலயம், மறுமணம்."},
    10: {"en": "Job, profession, promotion, duty, higher post, business status.", "ta": "உத்தியோகம், பதவி உயர்வு, அரசு பணி, தொழில் கடமை."},
    11: {"en": "Profit and gains, fulfilment of desires, happiness, elder sibling.", "ta": "லாபம், நினைத்த காரிய வெற்றி, பேரானந்தம், மூத்த சகோதரன்."},
    12: {"en": "Extravagant expenses, losses, intangible profit, medical costs, secret plans.", "ta": "தேவையற்ற விரயம், நஷ்டம், மருத்துவ செலவு, ரகசிய திட்டம், வெளிநாடு."},
}

# Classical Planet Attributes Table: Rays, Age, Height, Places, Direction
PLANET_ATTRIBUTES: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "rays": 5,
        "age": "50 (Middle age / நடுத்தர வயது)",
        "height": "Medium (நடுத்தர உயரம்)",
        "places_en": "Forest, cattle shed, government buildings, open ground",
        "places_ta": "காடு, மாட்டுத் தொழுவம், அரசு அலுவலகங்கள், திறந்த வெளி",
        "direction_en": "East (90°)",
        "direction_ta": "கிழக்கு (90°)",
    },
    "Moon": {
        "rays": 21,
        "age": "70 (Old age / மூத்த வயது)",
        "height": "Short (குள்ளம்)",
        "places_en": "Watery places, rivers, oceans, wells, bathrooms, milk booths",
        "places_ta": "நீர்நிலைகள், ஆறு, கடல், கிணறு, குளியலறை, பால் பண்ணை",
        "direction_en": "North-West (Vayu)",
        "direction_ta": "வடமேற்கு (வாயுவியம்)",
    },
    "Mars": {
        "rays": 7,
        "age": "16 (Youth / வாலிப பருவம்)",
        "height": "Short (குள்ளம்)",
        "places_en": "Forest, fiery places, kitchen, weapons room, battleground",
        "places_ta": "காடு, நெருப்பு உள்ள இடம், சமையலறை, ஆயுதக் கூடம், போர்க்களம்",
        "direction_en": "South (180°)",
        "direction_ta": "தெற்கு (180°)",
    },
    "Mercury": {
        "rays": 9,
        "age": "20 (Young adult / இளமை)",
        "height": "Tall (உயரம்)",
        "places_en": "Town, city, where people live, schools, libraries, fertile land",
        "places_ta": "நகரம், மக்கள் வாழும் இடம், பள்ளி, நூலகம், செழிப்பான பூமி",
        "direction_en": "North (0°/360°)",
        "direction_ta": "வடக்கு (0°/360°)",
    },
    "Jupiter": {
        "rays": 10,
        "age": "30 (Mature adult / நடுத்தர வாலிபம்)",
        "height": "Tall (உயரம்)",
        "places_en": "Town, city, where people live, temples, puja rooms, banks, courts",
        "places_ta": "நகரம், மக்கள் வாழும் இடம், கோவில், பூஜை அறை, வங்கி, நீதிமன்றம்",
        "direction_en": "North-East (Easanya)",
        "direction_ta": "வடகிழக்கு (ஈசானியம்)",
    },
    "Venus": {
        "rays": 16,
        "age": "7 (Child / சிறு பெண் பருவம்)",
        "height": "Medium (நடுத்தர உயரம்)",
        "places_en": "Watery places, bedroom, entertainment halls, beauty parlours, dress shops",
        "places_ta": "நீர்நிலைகள், படுக்கையறை, கேளிக்கை கூடம், அழகு நிலையம், ஆடம்பர கடைகள்",
        "direction_en": "South-East (Agni)",
        "direction_ta": "தென்கிழக்கு (ஆக்னேயம்)",
    },
    "Saturn": {
        "rays": 4,
        "age": "Very Old Age (முதிய பருவம்)",
        "height": "Short (குள்ளம்)",
        "places_en": "Forest, waste land, dilapidated rooms, garbage bins, graveyard",
        "places_ta": "காடு, தரிசு நிலம், பாழடைந்த அறை, குப்பை மேடு, சுடுகாடு",
        "direction_en": "West (270°)",
        "direction_ta": "மேற்கு (270°)",
    },
    "Snake": {
        "rays": 4,
        "age": "Very Old Age (முதிய பருவம்)",
        "height": "Tall (உயரம்)",
        "places_en": "Bamboo bushes, dense forest, termite mounds, waste land, foreign lands",
        "places_ta": "மூங்கில் புதர், அடர்ந்த காடு, புற்று, பாழ் நிலம், வெளிநாடு",
        "direction_en": "South-West (Nirruthi)",
        "direction_ta": "தென்மேற்கு (நைருதி)",
    },
    "Rahu": {
        "rays": 4,
        "age": "Very Old Age (முதிய பருவம்)",
        "height": "Tall (உயரம்)",
        "places_en": "Bamboo bushes, dense forest, termite mounds, waste land, foreign lands",
        "places_ta": "மூங்கில் புதர், அடர்ந்த காடு, புற்று, பாழ் நிலம், வெளிநாடு",
        "direction_en": "South-West (Nirruthi)",
        "direction_ta": "தென்மேற்கு (நைருதி)",
    },
    "Ketu": {
        "rays": 4,
        "age": "Very Old Age (முதிய பருவம்)",
        "height": "Tall (உயரம்)",
        "places_en": "Hermitage, occult caves, termite mounds, medicine stores",
        "places_ta": "ஆசிரமம், குகைகள், புற்று, மருந்து கடைகள்",
        "direction_en": "North-East (Easanya)",
        "direction_ta": "வடகிழக்கு (ஈசானியம்)",
    },
}

# Jeeva Karaka Planet to Person Signification
JEEVA_KARAKA_MAP: Dict[str, Dict[str, str]] = {
    "Sun": {"en": "Father / Father-in-Law", "ta": "தந்தை / மாமனார்"},
    "Moon": {"en": "Mother / Mother-in-Law / Elder Sister", "ta": "தாய் / மாமியார் / மூத்த சகோதரி"},
    "Mars": {"en": "Husband / Brother / Brother-in-Law", "ta": "கணவர் / சகோதரன் / மைத்துனன்"},
    "Mercury": {"en": "Maternal Uncle / 2nd Sibling / Nephew", "ta": "தாய்மாமன் / 2-ம் சகோதரன் / மருமகன்"},
    "Jupiter": {"en": "Children / Elder Brother / Son-in-Law", "ta": "புத்திரர்கள் / அண்ணன் / மருமகன்"},
    "Venus": {"en": "Wife / Daughter-in-Law / Aunt / Younger Sister", "ta": "மனைவி / மருமகள் / அத்தை / தங்கை"},
    "Saturn": {"en": "Father's Younger Brother / Servants / Subordinates", "ta": "சித்தப்பா / வேலையாட்கள் / பணியாளர்கள்"},
    "Snake": {"en": "Paternal / Maternal Grandparents", "ta": "தாத்தா / பாட்டி"},
    "Rahu": {"en": "Paternal / Maternal Grandparents", "ta": "தாத்தா / பாட்டி"},
    "Ketu": {"en": "Maternal Ancestors / Ascetics", "ta": "தாய்வழி முன்னோர்கள் / சந்நியாசிகள்"},
}

# Planet with Kavippu: Nature and Profile of Person who did Black Magic
BLACK_MAGIC_SORCERER_KARAKAS: Dict[str, Dict[str, str]] = {
    "Sun": {"en": "Father figure, government authority, powerful high-status person", "ta": "தந்தை ஸ்தானத்தில் உள்ளவர், அரசு அதிகாரி, செல்வாக்குள்ள நபர்"},
    "Moon": {"en": "Motherly figure, elderly woman, food/water vendor, female neighbor", "ta": "தாய் ஸ்தானத்தில் உள்ள பெண், வயதான பெண்மணி, உணவு/பால் வழங்குபவர்"},
    "Mars": {"en": "Brother, young aggressive male, military/police person, enemy", "ta": "சகோதரன், வாலிப ஆண், சீருடை பணியாளர், பழைய விரோதி"},
    "Mercury": {"en": "Maternal uncle, close relative, merchant, young student, friend", "ta": "தாய்மாமன், நெருங்கிய உறவினர், வியாபாரி, இளைஞர், நண்பர்"},
    "Jupiter": {"en": "Priest, temple affiliate, brahmin, religious teacher, respected elder", "ta": "பூசாரி, கோவில் சார்ந்தவர், ஆன்மீக குரு, பெரியவர்"},
    "Venus": {"en": "Young woman, wife's relative, beautician, sister-in-law, female rival", "ta": "இளம் பெண், மனைவி வழி பெண் உறவினர், பெண் எதிரி"},
    "Saturn": {"en": "Servant, subordinate laborer, scavenger, elderly dark complexioned person", "ta": "வேலைக்காரர், தொழிலாளி, துப்புரவாளர், வயதான கருத்த நபர்"},
    "Snake": {"en": "Professional sorcerer, black magician, tantric outsider, foreigner", "ta": "பில்லி சூனிய மாந்திரீகர், அந்நிய நபர், தாந்திரீக வாதி"},
    "Rahu": {"en": "Professional sorcerer, black magician, tantric outsider, foreigner", "ta": "பில்லி சூனிய மாந்திரீகர், அந்நிய நபர், தாந்திரீக வாதி"},
    "Ketu": {"en": "Ascetic, hermit, occult mystic, religious mendicant", "ta": "சந்நியாசி, போலி சாமியார், மறைமுக மாந்திரீகவாதி"},
}

# Approaching Planet Muhurta Significations (Actions Favorable During This Hour)
APPROACHING_PLANET_MUHURTA_SIGNIFICATIONS: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "en": "Applying for govt jobs, meeting officials/boss/politicians, swearing-in ceremonies, talking with father/father-in-law, starting terraced house construction.",
        "ta": "அரசு வேலைக்கு விண்ணப்பித்தல், அதிகாரிகள்/தலைவர்களை சந்தித்தல், பதவி ஏற்பு, தந்தை/மாமனாருடன் பேசுதல், மாடி வீடு கட்டத் தொடங்குதல்.",
        "auspicious_for": ["Govt Jobs", "Meeting Authorities", "Father Matters", "Construction"],
    },
    "Mars": {
        "en": "Applying/joining police or defense, seeing/purchasing land/property. (DO NOT select this time for peace settlements, negotiations or delicate talks - leads to quarrels).",
        "ta": "காவல்துறை/ராணுவத்தில் சேருதல், பூமி/நிலம் வாங்குதல். (எச்சரிக்கை: சமரச பேச்சுவார்த்தைக்கோ உடன்படிக்கைக்கோ இந்நேரத்தை தேர்ந்தெடுக்க வேண்டாம் - வாக்குவாதம் மூளும்).",
        "auspicious_for": ["Police / Defense", "Land Purchase", "Physical Training"],
    },
    "Jupiter": {
        "en": "Buying gold, applying for teaching jobs, depositing cash in bank, child-related activities, performing Homam/fire rituals, temple work, appeasing god.",
        "ta": "தங்கம் வாங்குதல், ஆசிரியர் பணிக்கு விண்ணப்பித்தல், வங்கியில் பணம் செலுத்துதல், புத்திர காரியங்கள், ஹோமம் செய்தல், கோவில் திருப்பணி.",
        "auspicious_for": ["Buying Gold", "Banking", "Teaching", "Homam & Puja", "Children"],
    },
    "Mercury": {
        "en": "Drafting letters, sending emails, applying to schools/colleges, buying vacant land, signing agreements/contracts, investing in share market, resolving differences with relatives.",
        "ta": "கடிதம்/மின்னஞ்சல் அனுப்புதல், பள்ளி/கல்லூரி விண்ணப்பம், காலி மனை வாங்குதல், ஒப்பந்தம் கையெழுத்திடுதல், பங்குச்சந்தை முதலீடு, கருத்து வேறுபாடு தீர்த்தல்.",
        "auspicious_for": ["Agreements", "Education", "Share Market", "Vacant Land", "Letters/Email"],
    },
    "Venus": {
        "en": "Buying vehicles, diamonds, clothes, luxury items, silver, cows/cattle, romance, marriage proposals.",
        "ta": "வாகனம், வைரம், ஆடை ஆபரணங்கள், வெள்ளி, பசு வாங்குதல், வரன் பார்த்தல், சுப நிகழ்வுகள்.",
        "auspicious_for": ["Vehicles", "Diamond & Luxury", "Clothes", "Marriage Proposal"],
    },
    "Saturn": {
        "en": "Appointing labor/servants, buying old things, iron/scrap, fire homam for longevity, long-term durable foundation.",
        "ta": "வேலையாட்களை நியமித்தல், பழைய பொருட்கள், இரும்பு வாங்குதல், ஆயுள் ஹோமம் செய்தல்.",
        "auspicious_for": ["Appointing Servants", "Iron / Scrap", "Longevity Rituals"],
    },
    "Moon": {
        "en": "Deriving water, digging well/borewell, juice shop, hotel, restaurant, beginning travel, travel business, meeting mother/mother-in-law.",
        "ta": "கிணறு தோண்டுதல், நீர் ஊற்று காணுதல், உணவகம்/ஹோட்டல் தொடங்குதல், பயணம் தொடங்குதல், தாய்/மாமியாரை சந்தித்தல்.",
        "auspicious_for": ["Digging Well / Water", "Hotel & Restaurant", "Travel", "Mother Matters"],
    },
    "Snake": {
        "en": "Foreign travel departure, IVF / test-tube baby conception procedures. (Inauspicious for all other normal worldly initiatives).",
        "ta": "வெளிநாட்டுப் பயணம் தொடங்குதல், செயற்கை கருத்தரித்தல் (IVF / Test-tube baby). (மற்ற அனைத்து சுப காரியங்களுக்கும் விலக்கப்பட வேண்டும்).",
        "auspicious_for": ["Foreign Travel", "IVF Conception"],
    },
    "Rahu": {
        "en": "Foreign travel departure, IVF / test-tube baby conception procedures.",
        "ta": "வெளிநாட்டுப் பயணம் தொடங்குதல், செயற்கை கருத்தரித்தல் (IVF).",
        "auspicious_for": ["Foreign Travel", "IVF Conception"],
    },
    "Ketu": {
        "en": "Spiritual initiation, astrological consultation, medical diagnosis, solitary retreat.",
        "ta": "மந்திர உபதேசம், ஜோதிட ஆலோசனை, மருத்துவம் தொடங்குதல், தியானம்.",
        "auspicious_for": ["Spiritual Initiation", "Astrology", "Medical Treatment"],
    },
}


# ==============================================================================
# Islamic Legal Guidance & Shariah Ruqyah on Astrology & Witchcraft
# Source: "சூனியம் மற்றும் சோதிடம் குறித்த இஸ்லாமிய சட்ட விளக்கம்"
# Author: Grand Mufti Sheikh Abdul Aziz ibn Abdullah ibn Baz (ரஹிமஹுல்லாஹ்)
# Ministry of Islamic Affairs, Endowments, Da'wah and Guidance, Riyadh
# ==============================================================================
ISLAMIC_LEGAL_GUIDANCE_AND_RUQYAH: Dict[str, Any] = {
    "source_title_ta": "சூனியம் மற்றும் சோதிடம் குறித்த இஸ்லாமிய சட்ட விளக்கம்",
    "source_title_en": "Islamic Legal Clarification Regarding Black Magic (Sihr) and Astrology/Soothsaying (Jothidam)",
    "author_ta": "அஷ்ஷெய்க் அப்துல் அஸீஸ் இப்னு அப்தில்லாஹ் பின் பாஸ் (ரஹிமஹுல்லாஹ்) - முன்னாள் சவூதி அரேபிய தலைமை முஃப்தி",
    "author_en": "Grand Mufti Sheikh Abdul Aziz ibn Abdullah ibn Baz (Rahimahullah) - Former Grand Mufti of Saudi Arabia",
    "publisher_ta": "இஸ்லாமிய விவகாரங்கள், அவ்காப், அழைப்பு மற்றும் வழிகாட்டல் அமைச்சகம், ரியாத்",
    "publisher_en": "Ministry of Islamic Affairs, Endowments, Da'wah and Guidance, Riyadh, KSA",
    "core_verdict_ta": (
        "இஸ்லாமிய ஷரீஆவின் அடிப்படை விதிகளின்படி ஜோதிடம், குறி சொல்லுதல், மறைவானவற்றை அறிவதாக வாதிடும் மந்திரவாதிகளிடம் செல்லுதல் மற்றும் "
        "சூனியம் (செய்வினை) செய்தல் அல்லது செய்யக் கோருதல் யாவும் மாபெரும் பாவங்களாகும் (குஃப்ர் / ஷிர்க்). "
        "மறைவான ஞானம் ('இல்முல் ஃகைப்') அல்லாஹ் ஒருவனுக்கு மட்டுமே உரியது (ஸூறா அந்-நம்ல் 27:65). "
        "ஆயினும் சூனியம், கண் திருஷ்டி அல்லது துஷ்ட சக்திகளால் பாதிக்கப்பட்டோர் மார்க்க வரம்புக்குட்பட்டு "
        "அல்குர்ஆன் ஆயத்துக்கள் மற்றும் சுன்னத்தான திக்ருகள் (ருக்யா ஷரீஆ) மூலம் பூரண நிவாரணம் பெற மார்க்கத்தில் அனுமதி உண்டு."
    ),
    "core_verdict_en": (
        "Under Islamic Shariah, fortune-telling, astrology (claiming knowledge of the unseen / 'Ilm al-Ghayb), and black magic (Sihr) "
        "are categorized among the seven fatal, destructive sins (Al-Mubiqat). The unseen belongs exclusively to Allah (Surah An-Naml 27:65). "
        "However, those afflicted by witchcraft, evil eye, or demonic distress are provided authentic, Shariah-compliant spiritual healing "
        "through the Holy Quran, Prophetic supplications, and lote-leaf water treatment (Ruqyah Shariyyah)."
    ),
    "authentic_hadith_cautions": [
        {
            "arabic": "مَنْ أَتَى عَرَّافًا فَسَأَلَهُ عَنْ شَيْءٍ لَمْ تُقْبَلْ لَهُ صَلَاةٌ أَرْبَعِينَ لَيْلَةً",
            "tamil": "யார் (சோதிடன்) குறி சொல்பவனிடம் சென்று ஏதேனும் ஒன்றைப் பற்றி விசாரித்தால் அவனுடைய நாற்பது நாட்களின் தொழுகைகள் ஏற்றுக் கொள்ளப்படமாட்டாது. (ஸஹீஹ் முஸ்லிம்)",
            "english": "Whoever visits a fortune teller or astrologer and asks him about anything, his prayer will not be accepted for forty nights. (Sahih Muslim)",
            "source": "Sahih Muslim 2230",
        },
        {
            "arabic": "مَنْ أَتَى كَاهِنًا أَوْ عَرَّافًا فَصَدَّقَهُ بِمَا يَقُولُ فَقَدْ كَفَرَ بِمَا أُنْزِلَ عَلَى مُحَمَّدٍ",
            "tamil": "யார் ஒருவர் குறி சொல்பவரிடமோ அல்லது சோதிடனிடமோ சென்று அவர் கூறுவதை நம்பி உண்மைப்படுத்தினால், முஹம்மத் (ஸல்) அவர்களின் மீது இறக்கியருளப்பட்டதை நிராகரித்தவராவார். (அபூதாவூத், அஹ்மத், ஹாக்கிம்)",
            "english": "Whoever visits a soothsayer or an astrologer and believes in what he says has disbelieved in that which was revealed to Muhammad (peace be upon him). (Sunan Abu Dawud, Musnad Ahmad, Al-Hakim)",
            "source": "Abu Dawud 3904, Musnad Ahmad 9536",
        },
        {
            "arabic": "لَيْسَ مِنَّا مَنْ تَطَيَّرَ أَوْ تُطُيِّرَ لَهُ أَوْ تَكَهَّنَ أَوْ تُكُهِّنَ لَهُ أَوْ سَحَرَ أَوْ سُحِرَ لَهُ",
            "tamil": "சகுனம் பார்ப்பவரும் தனக்கு பார்க்குமாறு சொல்பவரும், சோதிடம் பார்ப்பவரும் பார்த்து விடுமாறு சொல்பவரும், சூனியம் செய்பவரும் சூனியம் செய்யுமாறு வேண்டுபவரும் எங்களைச் சார்ந்தவரல்ல. (பஸ்ஸார்)",
            "english": "He is not of us who seeks omens or has omens sought for him, or who tells fortunes or has his fortune told, or who practices sorcery or has sorcery practiced for him. (Musnad Al-Bazzar)",
            "source": "Musnad Al-Bazzar / Tabarani",
        },
    ],
    "impermissible_treatments": {
        "title_ta": "விலக்கப்பட்ட சிகிச்சை முறைகள் (நுஷ்ரா & ஷைத்தானிய பித்தலாட்டங்கள்)",
        "title_en": "Strictly Forbidden Treatments (Nushrah & Occult Practices)",
        "items_ta": [
            "சூனியத்தை அழிக்க மற்றொரு மந்திரவாதியிடம் சென்று மாய மந்திரங்கள் செய்தல் ('நுஷ்ரா' குறித்து நபியவர்களிடம் கேட்கப்பட்ட போது 'அது ஷைத்தானின் செயல்' என பதிலளித்தார்கள் - அபூதாவூத்).",
            "ஜின்களுக்கு கோழி, ஆடு போன்ற பிராணிகளை அறுத்துப் பலியிடுதல் அல்லது அல்லாஹ் அல்லாதவர்களிடம் நிவாரணம் கோருதல் (அஷ்ஷிர்குல் அக்பர் - பெரும் இணைவைப்பு).",
            "தாயத்து தகடுகளில் புரியாத எண்கள், குறியீடுகள், மந்திரக் கோடுகள் வரைந்து உடலில் கட்டுதல்.",
            "நோயாளியிடம் தாய் பெயர், உறவினர் பெயர்களைக் கேட்டு ஜின்களை வரவழைத்து சிகிச்சை செய்தல்.",
        ],
        "items_en": [
            "Consulting another sorcerer to undo magic (When asked about Nushrah, the Prophet pbuh replied: 'It is from the deeds of Satan' - Abu Dawud).",
            "Sacrificing animals to jinns or invoking unseen spirits (Ash-Shirk al-Akbar - major idolatry).",
            "Wearing amulets, talismans with occult numerical squares, demonic sigils, or knotted cords.",
            "Asking for the patient's mother's name to summon jinn or divine hidden matters.",
        ],
    },
    "sunnah_ruqyah_cure": {
        "title_ta": "ஷரீஆ அனுமதித்த 7 பச்சை இலந்தை இலை ருக்யா சிகிச்சை (அறிஞர் இப்னு பாஸ் வழிகாட்டல்)",
        "title_en": "Authentic Sunnah Ruqyah: 7 Green Sidr (Lote) Leaves Water Treatment",
        "description_ta": (
            "சூனியத்தால் பாதிக்கப்பட்டவர் அல்லது கணவன்-மனைவி தாம்பத்திய உறவில் செய்வினையால் தடைப்பட்டோருக்கு (கட்டுப்பாடு / இஸ்திஹ்லா) "
            "இப்னுல் கைய்யிம் மற்றும் அஷ்ஷெய்க் இப்னு பாஸ் பரிந்துரைத்த சுன்னத்தான அருமருந்து."
        ),
        "description_en": (
            "Classical Ruqyah endorsed by scholars including Wahb ibn Munabbih, Ibn al-Qayyim, and Sheikh Ibn Baz for nullifying black magic, "
            "the evil eye, and spells causing marital discord or impotence."
        ),
        "step_by_step_ta": [
            "1. இலந்தை மரத்தின் ஏழு பச்சை இலைகளைப் பறித்து இரு கற்களுக்கிடையே அல்லது உரலில் நன்கு அரைத்துக்கொள்ளவும்.",
            "2. ஒரு பாத்திரத்தில் குடிப்பதற்கும் குளிப்பதற்கும் போதுமான சுத்தமான நீரை ஊற்றி, அரைத்த இலந்தை விழுதை அதில் கலக்கவும்.",
            "3. அந்த நீரில் வாய் அருகமைத்து உளூவுடன் பின்வரும் அல்குர்ஆன் ஸூராக்களையும் ஆயத்துக்களையும் நபிகளாரின் துஆக்களையும் ஓதி ஊதவும்:",
            "   • ஸூறதுல் பாத்திஹா (அல்-ஹம்து ஸூரா)",
            "   • ஆயதுல் குர்ஸி (ஸூறதுல் பகரா வசனம் 255)",
            "   • ஸூறதுல் காஃபிரூன் (குல் யா அய்யுஹல் காபிரூன்)",
            "   • ஸூறதுல் இஹ்லாஸ் (குல்ஹுவல்லாஹு அஹத்) - 3 முறை",
            "   • ஸூறதுல் பலக் (குல்அஊது பிரப்பில் பலக்) - 3 முறை",
            "   • ஸூறதுந் நாஸ் (குல்அஊது பிரப்பின்னாஸ்) - 3 முறை",
            "   • ஸூறா அல்-அஃராப் (7:117-119): 'வஅவ்ஹைனா இலா மூஸா அன் அல்கி அஸாக ஃபஇஃதா ஹிய தல்ஃகஃபு மா யஃபிகூன், ஃப வகஅல்ஹக்கு வபதல மா கானூ யஃமலூன்...'",
            "   • ஸூறா யூனுஸ் (10:79-82): 'மா ஜிஃதும் பிஹிஸ்ஸிஹ்ரு இன்னல்லாஹ ஸயுப்திலுஹூ இன்னல்லாஹ லா யுஸ்லிஹு அமலல் முப்ஸிதீன்...'",
            "   • ஸூறா தாஹா (20:65-69): 'இன்னமா ஸனஊ கைது ஸாஹிரின், வலா யுஃப்லிஹுஸ் ஸாஹிரு ஹைது அதா...'",
            "   • நபிமொழி துஆ (3 முறை): 'அல்லாஹும்ம ரப்பன் நாஸி, அத்ஹிபில் பஃஸ, வஷ்ஃபி அன்தஷ் ஷாஃபி, லா ஷிஃபாஅ இல்லா ஷிஃபாஉக, ஷிஃபாஅன் லா யுஃகாதிரு ஸகமா'",
            "   • ஜிப்ரீல் (அலை) துஆ (3 முறை): 'பிஸ்மில்லாஹி அர்கீக மின் குல்லி ஷைய்இன் யுஃதீக, வமின் ஷர்ரி குல்லி நப்ஸின் அவ் அய்னின் ஹாஸிதின், அல்லாஹு யஷ்பீக, பிஸ்மில்லாஹி அர்கீக'",
            "4. ஓதிய நீரிலிருந்து மூன்று மிடர்கள் குடித்துவிட்டு, எஞ்சிய நீரைக் கொண்டு உடல் முழுவதும் குளிக்க வேண்டும்.",
            "5. நோய் குணமாகும் வரை பல நாட்கள் இதனைத் தொடரலாம்; அல்லாஹ்வின் அருளால் பூரண குணம் கிடைக்கும்.",
        ],
        "step_by_step_en": [
            "1. Pick 7 green leaves of the Sidr (Lote tree / Ziziphus) and crush them finely between stones or a pestle.",
            "2. Pour clean water sufficient for drinking and bathing into a vessel, and mix the crushed leaves.",
            "3. Bring the water close to the mouth and recite the following with ritual purity (Wudu):",
            "   • Surah Al-Fatihah",
            "   • Ayatul Kursi (Surah Al-Baqarah: 255)",
            "   • Surah Al-Kafirun (109)",
            "   • Surah Al-Ikhlas (112), Surah Al-Falaq (113), Surah An-Nas (114) - 3 times each",
            "   • Surah Al-A'raf (7:117-119): Moses' staff destroying Pharaoh's magic",
            "   • Surah Yunus (10:79-82): 'What you have brought is sorcery; indeed, Allah will make it void'",
            "   • Surah Ta-Ha (20:65-69): 'The magician will never succeed wherever he may come from'",
            "   • Prophetic Dua (3x): 'Allahumma Rabban-naas, adh-hibil-ba's, washfi Antash-Shaafee, laa shifaa'a illa shifaa'uk, shifaa'an laa yughadiru saqama'",
            "   • Jibril's Ruqyah (3x): 'Bismillahi arqeeka min kulli shay'in yu'dheeka, wa min sharri kulli nafsin aw 'aynin hasidin, Allahu yashfeeka, bismillahi arqeeka'",
            "4. Drink 3 sips of the water, then wash and bathe (ghusl) with the rest.",
            "5. Repeat daily until symptoms and afflictions disappear completely by Allah's will.",
        ],
    },
    "daily_protective_fortress": {
        "title_ta": "தினசரி தற்காப்பு அரண் (துஷ்ட சக்திகள் நெருங்காமல் இருக்க)",
        "title_en": "Daily Spiritual Shield (Protection Against Devils & Evil Eye)",
        "adhkar_ta": [
            {
                "name": "ஆயதுல் குர்ஸி (ஸூறா அல்-பகரா 255)",
                "when": "ஒவ்வொரு தொழுகைக்குப் பின்னும், இரவில் படுக்கைக்குச் செல்லும் முன்",
                "benefit": "படுக்கையில் ஓதினால் விடியும் வரை அல்லாஹ்வின் பாதுகாப்பாளர் உடனிருந்து ஷைத்தான் நெருங்காமல் பாதுகாப்பார்.",
            },
            {
                "name": "மூன்று குல் ஸூராக்கள் (இஹ்லாஸ், பலக், நாஸ்)",
                "when": "ஃபஜ்ர் மற்றும் மஃக்ரிப் தொழுகைக்குப் பின் தலா 3 முறை",
                "benefit": "அனைத்துவிதமான கெடுதிகள், கண் திருஷ்டி மற்றும் பொறாமையிலிருந்து முழுமையான பாதுகாப்பு.",
            },
            {
                "name": "ஸூறதுல் பகராவின் இறுதி இரு வசனங்கள் (2:285-286)",
                "when": "தினமும் இரவில் தூங்கும் முன்",
                "benefit": "யார் ஓரிரவில் இதனை ஓதுகிறாரோ அதுவே அவரது தற்காப்பிற்குப் போதுமானதாகும்.",
            },
            {
                "name": "பிஸ்மில்லாஹில்லதீ லா யளுர்ரு...",
                "when": "காலையிலும் மாலையிலும் 3 முறை",
                "benefit": "'வானிலும் பூமியிலும் உள்ள எப்பொருளும் எவ்விதத் தீங்கும் செய்ய முடியாது' - நபிமொழி.",
            },
            {
                "name": "அஊது பிகலிமாதில்லாஹித்தாம்மாதி...",
                "when": "வெளியில் தங்கும் போது அல்லது பயணத்தின் போது",
                "benefit": "அந்த இடத்திலிருந்து புறப்படும் வரை எந்தவொரு தீங்கும் அணுகாது.",
            },
        ],
        "adhkar_en": [
            {
                "name": "Ayatul Kursi (Surah Al-Baqarah 2:255)",
                "when": "After each fard prayer and before going to sleep",
                "benefit": "A guardian angel from Allah protects you through the night and no devil can approach until dawn.",
            },
            {
                "name": "The Three Quls (Al-Ikhlas, Al-Falaq, An-Nas)",
                "when": "3 times after Fajr and 3 times after Maghrib",
                "benefit": "Universal shield against witchcraft, envious eyes (Hasad), and unseen harms.",
            },
            {
                "name": "Last 2 Verses of Surah Al-Baqarah (2:285-286)",
                "when": "Every night before sleeping",
                "benefit": "Whoever recites them at night, they suffice him against every evil.",
            },
            {
                "name": "Bismillaahil-ladhee laa yadurru ma'as-mihi...",
                "when": "3 times every morning and evening",
                "benefit": "Nothing in the heavens or earth can cause harm when this name is invoked.",
            },
            {
                "name": "A'oodhu bi kalimaat-Illaahit-taammaati...",
                "when": "When stopping at any dwelling or traveling",
                "benefit": "Protection from all creatures and unseen harms until departure.",
            },
        ],
    },
    "disenchantment_protocol": {
        "title_ta": "செய்வினை முடிச்சுகளைக் கண்டறிந்து அழிக்கும் முறை",
        "title_en": "Locating and Dissolving Physical Charms & Knotted Cords",
        "details_ta": (
            "சூனியத்திற்கான மிகப்பயனுள்ள சிகிச்சை என்னவெனில், சூனியம் வைக்கப்பட்ட இடத்தை கண்டறிய முயற்சித்தல். "
            "அவ்வாறு முடிச்சிடப்பட்ட நூல்கள், ஆணிகள் அல்லது தாயத்துக்களை வெளியே எடுத்து முடிச்சுகளை அவிழ்த்து அழித்துவிட்டால் "
            "சூனியம் உடனடியாக முறிந்துவிடும் (நபியவர்களுக்கு லபீத் இப்னு அஃஸம் செய்த சூனியம் கிணற்றிலிருந்து எடுக்கப்பட்டு முடிச்சுகள் அவிழ்க்கப்பட்ட முறை)."
        ),
        "details_en": (
            "The most decisive cure for black magic is locating the physical talisman, knotted cords, or pinned needles, "
            "untying all knots while reciting the Mu'awwidhat, and burning or destroying them completely. "
            "This was the exact manner in which the spell cast on the Prophet (pbuh) was dismantled from the well of Dharwan."
        ),
    },
}
