"""28 Nakshatras - The Real Secrets of Vedic Astrology.

Canonical reference catalog containing detailed electoral, transit, pada,
character, dosha, and remedial data for all 28 Nakshatras (27 + Abhijit).

Derived from classical Jyotish treatises and compiled teachings of:
B.V. Raman, Rama Krishna Bhatt, Kalaprakashika (Subramaniyam Iyer),
Purohit Rami Shivan, Pandit Navaratnam, Nalini Kanta Dasa,
Shyamasundara Dasa, Pandit Srinivasan, Sobhana Mataji, and Panditji Master Deepak.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PadaDetail(BaseModel):
    pada_number: int
    degree_range: str
    traits: str
    dosha_status: str
    dosha_affects: Optional[str] = None
    remedy: Optional[str] = None


class NakshatraData(BaseModel):
    id: int
    name: str
    name_tamil: str
    alternate_names: List[str] = Field(default_factory=list)
    span_zodiac: str
    degree_start: float
    degree_end: float
    functional_nature: str  # Fixed, Soft/Gentle, Light/Swift, Dreadful/Sharp, Movable/Temporary, Fierce/Cruel, Mixed
    functional_nature_tamil: str
    gender: str  # Masculine, Feminine, Hermaphrodite / Eunuch
    result_grade: str  # GOOD, OK, HARM, MISERY
    ruling_deity: str
    ruling_planet: str
    gaze_direction: str  # Forward, Upward, Downward
    gaze_direction_tamil: str
    caste: str
    motivation: str  # Dharma, Artha, Kama, Moksha / Salvation / Carnal / Material / Spiritual
    sight_quality: str  # Blind, Weak, Average, Good
    luminary_type: str  # Solar, Lunar
    kula_type: str  # Kul, Akul, Kulakul
    num_stars: int
    symbol_shape: str
    favourable_actions: List[str]
    inauspicious_for: List[str]
    ascendant_indications: str
    moon_indications: str
    rules_over: List[str]
    places: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    abstracts: List[str] = Field(default_factory=list)
    padas: List[PadaDetail]
    general_remedy: Optional[str] = None


FUNCTIONAL_NATURE_GROUPS: Dict[str, Dict[str, Any]] = {
    "FIXED": {
        "name_en": "Fixed / Steady (Sthira / Dhruva)",
        "name_ta": "ஸ்திர / நிலையான நட்சத்திரங்கள்",
        "nakshatras": ["Rohini", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada"],
        "nakshatra_ids": [4, 12, 21, 26],
        "suitable_actions_en": (
            "Laying foundations, constructing buildings, digging wells, buying land, planting trees, "
            "sowing seeds, installation of Deities (avahani), building temples, coronations, expiatory rituals, "
            "long-term careers, entering enduring relationships, and anything desirous of a lasting or permanent effect."
        ),
        "suitable_actions_ta": (
            "அடிக்கல் நாட்டுதல், கட்டட நிர்மாணம், கிணறு வெட்டுதல், நிலம் வாங்குதல், மரம் நடுதல், விதை விதைத்தல், "
            "தெய்வப் பிரதிஷ்டை, கோவில் அமைத்தல், முடிசூட்டு விழா, நீண்டகால ஒப்பந்தங்கள் மற்றும் நிலையான சுப காரியங்கள்."
        ),
        "nature_type": "steady"
    },
    "SOFT": {
        "name_en": "Soft / Gentle (Mridu)",
        "name_ta": "மிருதுவான / சாந்த நட்சத்திரங்கள்",
        "nakshatras": ["Mrigashira", "Chitra", "Anuradha", "Revati"],
        "nakshatra_ids": [5, 14, 17, 27],
        "suitable_actions_en": (
            "Fine arts, learning, making friendships, sensual pleasures, decorations, sexual union, "
            "wearing new apparel, marriage (vivaha), singing and dancing, processions, auspicious ceremonies, "
            "festivities, agricultural dealings, and short pleasant journeys."
        ),
        "suitable_actions_ta": (
            "நுண்கலைகள், கல்வி கற்றல், நட்பு பாராட்டுதல், சிற்றின்பம், ஆடை ஆபரணங்கள் அணிதல், தாம்பத்தியம், "
            "திருமணம், இசை, நடனம், ஊர்வலங்கள், மங்கள சடங்குகள், விவசாய வர்த்தகம் மற்றும் சுப பிரயாணங்கள்."
        ),
        "nature_type": "gentle"
    },
    "LIGHT": {
        "name_en": "Light / Swift (Kshipra / Laghu)",
        "name_ta": "லகு / சுறுசுறுப்பு நட்சத்திரங்கள்",
        "nakshatras": ["Ashwini", "Pushya", "Hasta"],
        "nakshatra_ids": [1, 8, 13],
        "suitable_actions_en": (
            "Sports, enjoying items of luxury, starting industries, skilled craftsmanship/labour, medical treatments, "
            "commencing education, starting journeys, meeting friends, buying and selling, performing spiritual activities, "
            "decorations, exercise, and giving or receiving loans."
        ),
        "suitable_actions_ta": (
            "விளையாட்டு, நுகர்வுப் பொருட்கள் அனுபவித்தல், தொழிற்சாலை தொடங்குதல், கைவினை நேர்த்தி, மருத்துவ சிகிச்சை, "
            "கல்வி துவக்கம், பயணம் புறப்படுதல், நண்பர்களை சந்தித்தல், வர்த்தக விற்பனை, ஆபரணம் அணிதல், கடன் கொடுத்தல்/வாங்குதல்."
        ),
        "nature_type": "swift"
    },
    "DREADFUL": {
        "name_en": "Dreadful / Sharp (Tikshna / Daruna)",
        "name_ta": "தீட்சண / கொடிய நட்சத்திரங்கள்",
        "nakshatras": ["Ardra", "Ashlesha", "Jyeshtha", "Mula"],
        "nakshatra_ids": [6, 9, 18, 19],
        "suitable_actions_en": (
            "Success in warfare, crisis resolution, invocation of spirits/elementals, tantric incantations, "
            "imprisonment, causing separation of opponents, acts of demolition/destruction, and breaking alliances with superiors."
        ),
        "suitable_actions_ta": (
            "போர் வெற்றி, ஆபத்துகளை சமாளித்தல், மாந்திரீக தந்திர காரியங்கள், எதிரிகளை முறியடித்தல், சிறை வைத்தல், "
            "பிரிவினை உண்டாக்குதல், பழையவற்றை தகர்த்தல் மற்றும் தீய சக்திகளை கட்டுப்படுத்துதல்."
        ),
        "nature_type": "sharp"
    },
    "MOVABLE": {
        "name_en": "Temporary / Movable / Quick (Chara / Chala)",
        "name_ta": "சர / விரைவு நட்சத்திரங்கள்",
        "nakshatras": ["Punarvasu", "Swati", "Shravana", "Dhanishta", "Shatabhisha"],
        "nakshatra_ids": [7, 15, 22, 23, 24],
        "suitable_actions_en": (
            "Undertaking travel, acquiring conveyances/automobiles, gardening, going on processions, visiting friends, "
            "and anything requiring mobility or temporary duration."
        ),
        "suitable_actions_ta": (
            "தூரப் பயணம், மோட்டார் வாகனங்கள் வாங்குதல், தோட்டம் அமைத்தல், ஊர்வலம் செல்லுதல், நண்பர்களை பார்த்தல், "
            "தற்காலிக மற்றும் சுழலும் தன்மை கொண்ட புதிய முயற்சிகள்."
        ),
        "nature_type": "movable"
    },
    "FIERCE": {
        "name_en": "Fierce / Cruel (Ugra)",
        "name_ta": "உக்கிர / தீவிர நட்சத்திரங்கள்",
        "nakshatras": ["Bharani", "Magha", "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"],
        "nakshatra_ids": [2, 10, 11, 20, 25],
        "suitable_actions_en": (
            "Crushing opponents, aggressive legal battles, confrontation, demolition, dealing with fire/weapons, "
            "incarceration, competitive athletics, and hazardous enterprises."
        ),
        "suitable_actions_ta": (
            "எதிரிகளை அடக்குதல், கடுமையான வழக்குகள், அக்னி மற்றும் ஆயுத விவகாரங்கள், சிறை நடவடிக்கைகள், "
            "போட்டி விளையாட்டுகள், கடினமான சவால்களை எதிர்கொள்ளுதல்."
        ),
        "nature_type": "cruel"
    },
    "MIXED": {
        "name_en": "Mixed (Mishra / Sadharana)",
        "name_ta": "மிஸ்ர / கலப்பு நட்சத்திரங்கள்",
        "nakshatras": ["Krittika", "Vishakha"],
        "nakshatra_ids": [3, 16],
        "suitable_actions_en": (
            "Routine duties, professional responsibilities, mechanical works, commercial collections, "
            "and general activities of day-to-day importance."
        ),
        "suitable_actions_ta": (
            "அன்றாட பணிகள், தொழில் கடமைகள், இயந்திர இயக்கம், வர்த்தக வசூல் மற்றும் வழக்கமான நடைமுறை அலுவல்கள்."
        ),
        "nature_type": "mixed"
    }
}


NAKSHATRAS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Ashwini",
        "name_tamil": "அஸ்வினி",
        "alternate_names": ["Aswini", "Asvini"],
        "span_zodiac": "Aries 0°00' - 13°20'",
        "degree_start": 0.0,
        "degree_end": 13.3333,
        "functional_nature": "Light / Swift",
        "functional_nature_tamil": "லகு / சுறுசுறுப்பு",
        "gender": "Masculine",
        "result_grade": "GOOD",
        "ruling_deity": "Ashwini Kumaras (Celestial Physicians)",
        "ruling_planet": "Ketu",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Vaishya",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Weak",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Horse's Head",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Education initiation (vidya rambham)",
            "Agriculture & trade",
            "Medical treatments & giving medicine",
            "Starting industries & skilled labour",
            "Sports & exercise",
            "Starting journeys & buying/selling"
        ],
        "inauspicious_for": [
            "Acts requiring extreme stealth or long-term passivity"
        ],
        "ascendant_indications": (
            "Likeable personality with lovely appearance, well-dressed and ornamented. Efficient in work, "
            "living by respectable means, and prominent member of the family. Resolute character capable of controlling "
            "eating habits, happy, carefree, and modest, though more financially successful than most."
        ),
        "moon_indications": (
            "Fond of ornaments, lovely appearance, clever, intelligent, skilled in arts, loved by all, "
            "swift in thought and deed, interested in medicine, transport, and commercial ventures."
        ),
        "rules_over": [
            "Horses, dealers, and riders",
            "Physicians and healers",
            "Merchants and traders",
            "Attractive personalities",
            "Attendants, astrologers, and military commandants"
        ],
        "places": ["Stables", "Hospitals", "Transport depots", "Trading hubs"],
        "objects": ["Chariots", "Medicines", "Golden ornaments", "Transport vehicles"],
        "abstracts": ["Light of dawn", "Swiftness", "Miraculous healing"],
        "general_remedy": "Gifts of Gold to the Deity, Vaishnavas, or learned Brahmanas.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "0°00' - 3°20' Aries (Mars / Aries Navamsa)",
                "traits": "Unsteady mind, sinful attachments, indulging in sensual pleasures, tendency to criticize others.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Not good for child or father in early infancy.",
                "remedy": "Gift of Gold to Deity or learned Vaishnavas/brahmanas."
            },
            {
                "pada_number": 2,
                "degree_range": "3°20' - 6°40' Aries (Venus / Taurus Navamsa)",
                "traits": "Scriptural knowledge, jack of all trades with many talents, handsome appearance, quick learner.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "6°40' - 10°00' Aries (Mercury / Gemini Navamsa)",
                "traits": "Mathematical talents, earning by physical labor, good teacher or advertiser; prone to piles, occasional villainous streak.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "10°00' - 13°20' Aries (Moon / Cancer Navamsa)",
                "traits": "Effeminate grace, wise, truthful, wealthy, highly liked by opposite sex, intuitive knowledge of astrology.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 2,
        "name": "Bharani",
        "name_tamil": "பரணி",
        "alternate_names": ["Barani"],
        "span_zodiac": "Aries 13°20' - 26°40'",
        "degree_start": 13.3333,
        "degree_end": 26.6667,
        "functional_nature": "Fierce / Cruel",
        "functional_nature_tamil": "உக்கிர / தீவிர",
        "gender": "Feminine",
        "result_grade": "HARM",
        "ruling_deity": "Yamaraja (Lord of Dharma & Death)",
        "ruling_planet": "Venus",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Outcast / Mlechha",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Average",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 3,
        "symbol_shape": "Womb / Female Sex Organ",
        "favourable_actions": [
            "Demolishing obstacles & crushing adversaries",
            "Entering caves, tunnels, or subterranean realms",
            "Work related to weapons, fire, and heat",
            "Distilling potent medicines & surgical extracts",
            "Enforcing discipline, warfare, and severe contest"
        ],
        "inauspicious_for": [
            "Peaceful celebrations, gentle ceremonies, delicate alliances, starting travel"
        ],
        "ascendant_indications": (
            "Fickle-minded, courageous, proud, with good longevity. Fond of kinsmen and helpful to friends, "
            "though usually having few children. Vital character easily led by others, with questionable moral moments, "
            "troubled by others' jealousy, yet capable of bearing enormous responsibilities."
        ),
        "moon_indications": (
            "Clever in work, dutiful, resilient, enduring hardships with stoicism, free from chronic disease, "
            "plain-spoken, unyielding under pressure."
        ),
        "rules_over": [
            "Men engaged in killing, torture, incarceration",
            "Those feeding off flesh and blood",
            "Cereals, seeds",
            "Workers bearing heavy physical loads",
            "Those devoid of nobility who operate in raw crisis"
        ],
        "places": ["Ponds, wells, slaughterhouses, morgues, cremation grounds, underground cellars"],
        "objects": ["Weapons, fire tools, poisons, cereals"],
        "abstracts": ["Restraint", "Concealment", "Karmic retribution"],
        "general_remedy": "Annadaanam (providing meals for learned brahmanas and the needy).",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "13°20' - 16°40' Aries (Sun / Leo Navamsa)",
                "traits": "Strong temper, reddish hair, ability to defeat enemies, broad-minded, valorous, perseverant.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "16°40' - 20°00' Aries (Mercury / Virgo Navamsa)",
                "traits": "Lazy, clever, weakness for opposite sex, scriptural knowledge, religious inclinations.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "20°00' - 23°20' Aries (Venus / Libra Navamsa)",
                "traits": "Lean and tall appearance, broad eyes, pride balanced with wisdom and even temper.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects father and mother of native in early years.",
                "remedy": "Annadaanam - provide wholesome meals for brahmanas and the destitute."
            },
            {
                "pada_number": 4,
                "degree_range": "23°20' - 26°40' Aries (Mars / Scorpio Navamsa)",
                "traits": "Courageous, obstinate, proud, keeping rough company, unsparing in conflict.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 3,
        "name": "Krittika",
        "name_tamil": "கார்த்திகை",
        "alternate_names": ["Krttika", "Karthigai"],
        "span_zodiac": "Aries 26°40' - Taurus 10°00'",
        "degree_start": 26.6667,
        "degree_end": 40.0,
        "functional_nature": "Mixed",
        "functional_nature_tamil": "மிஸ்ர / கலப்பு",
        "gender": "Masculine",
        "result_grade": "HARM",
        "ruling_deity": "Agni (God of Fire / Vahni)",
        "ruling_planet": "Sun",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Brahmana",
        "motivation": "Kama (Carnal Desires)",
        "sight_quality": "Good",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 6,
        "symbol_shape": "Dagger / Razor / Axe",
        "favourable_actions": [
            "Purification by fire & cooking feasts",
            "Routine duties & administrative responsibilities",
            "Metal casting, pottery, mining, furnace work",
            "Debates, surgical procedures, cutting away decay",
            "Sacrificial offerings & chanting sacred Vedic hymns"
        ],
        "inauspicious_for": [
            "Peaceful celebrations, gentle water journeys, delicate diplomatic compromises"
        ],
        "ascendant_indications": (
            "Proud, dignified, and honorable personality full of ambition for power. Angry but strictly truthful, "
            "with a voracious appetite and a wavering mind, possessing keen dexterity, technical skill, and many material possessions."
        ),
        "moon_indications": (
            "Brilliant appearance, well-known, large appetite, strong purpose, sharp speech, "
            "incisive intellect capable of piercing delusion."
        ),
        "rules_over": [
            "White flowers and sacrificial offerings",
            "Qualified brahmanas, grammarians, Vedic scholars",
            "Miners, barbers, potters, blacksmiths",
            "Holy ascetics and discerning astrologers"
        ],
        "places": ["Mines", "Furnaces", "Kitchens", "Sacrificial altars", "Barber shops"],
        "objects": ["Razors", "Daggers", "Swords", "Sacrificial vessels"],
        "abstracts": ["Physical/creative force", "Burning purification", "Axe of discrimination"],
        "general_remedy": "Annadaanam (providing meals for brahmanas) and lighting ghee lamps for Agni/Lord Muruga.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "26°40' Aries - 0°00' Taurus (Jupiter / Sagittarius Navamsa)",
                "traits": "Wise, well-mannered, sickly in early youth but possessing good longevity, taste for varied pleasures.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "0°00' - 3°20' Taurus (Saturn / Capricorn Navamsa)",
                "traits": "Averse to hypocritical ascetics, non-conformist, instigating actions that provoke conventional society.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "3°20' - 6°40' Taurus (Saturn / Aquarius Navamsa)",
                "traits": "Valorous and proud, indiscreet, quick-tempered, sensual desires, unconventional means of earning.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Adversely affects father and mother.",
                "remedy": "Annadaanam - provide wholesome feeding for brahmanas."
            },
            {
                "pada_number": 4,
                "degree_range": "6°40' - 10°00' Taurus (Jupiter / Pisces Navamsa)",
                "traits": "Humble yet arrogant, anxious, fluctuating wealth, susceptible to mental distress and health complaints.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 4,
        "name": "Rohini",
        "name_tamil": "ரோகிணி",
        "alternate_names": ["Rohinee"],
        "span_zodiac": "Taurus 10°00' - 23°20'",
        "degree_start": 40.0,
        "degree_end": 53.3333,
        "functional_nature": "Fixed",
        "functional_nature_tamil": "ஸ்திர / நிலையான",
        "gender": "Masculine",
        "result_grade": "GOOD",
        "ruling_deity": "Brahma (Creator of the Universe / Prajapati)",
        "ruling_planet": "Moon",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Shudra",
        "motivation": "Moksha (Salvation / Spiritual Liberation)",
        "sight_quality": "Blind",
        "luminary_type": "Solar",
        "kula_type": "Akul",
        "num_stars": 5,
        "symbol_shape": "Cart / Chariot / Temple",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Parting of hair (simontan)",
            "Constructing a house (griha rambham)",
            "Marriage (vivaha)",
            "Coronation & public appointments",
            "Buying cows, bulls, conveyances, elephants",
            "Planting trees, sowing seeds, laying foundations",
            "All enterprises desiring permanent lasting fruition"
        ],
        "inauspicious_for": [
            "Destructive acts, ending associations"
        ],
        "ascendant_indications": (
            "Sensually attractive and becomes a charismatic leader. May have early separation from parents or "
            "tension with mother. Wealthy, popular, religious, magnetic romantic allure, virile, highly productive."
        ),
        "moon_indications": (
            "Truthful, pure, sweet-tongued, of settled and composed mind, lovely appearance, fond of luxury and fine arts."
        ),
        "rules_over": [
            "Merchants, aristocracy, kings, men of authority",
            "Yogic practitioners performing austerities",
            "Cows, bulls, aquatic creatures",
            "Farmers, agricultural producers, factory magnates",
            "Mountain ranges and scenic landscapes"
        ],
        "places": ["Hills, mountains, hotels, restaurants, boarding houses, luxury resorts"],
        "objects": ["Chariots, agricultural produce, sweet perfumes, gemstones"],
        "abstracts": ["Cosmic growth", "Fertility", "Artistic enchantment"],
        "general_remedy": "Gift black Gingelly (sesame) seeds to Deity or pious learned brahmanas.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "10°00' - 13°20' Taurus (Mars / Aries Navamsa)",
                "traits": "Passionate, ambitious, sharp speech, striking physical appearance.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects mother and maternal uncle (as occurred in Sri Krishna's avatara).",
                "remedy": "Gift black Gingelly (sesame) seeds to Deity or learned brahmins."
            },
            {
                "pada_number": 2,
                "degree_range": "13°20' - 16°40' Taurus (Venus / Taurus Navamsa - Vargottama)",
                "traits": "Large expressive eyes, gentle habits, eloquent speaker, in control of senses, delicate health.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects mother and maternal uncle.",
                "remedy": "Gift black Gingelly (sesame) seeds to Deity or brahmins."
            },
            {
                "pada_number": 3,
                "degree_range": "16°40' - 20°00' Taurus (Mercury / Gemini Navamsa)",
                "traits": "Devout, praiseworthy habits, charitable, mathematically gifted, harmonious demeanor.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects maternal uncle.",
                "remedy": "Gift black Gingelly seeds to brahmins."
            },
            {
                "pada_number": 4,
                "degree_range": "20°00' - 23°20' Taurus (Moon / Cancer Navamsa)",
                "traits": "Wealthy, reads others' thoughts, prophetic intuition, strong arms, widely popular, wise.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 5,
        "name": "Mrigashira",
        "name_tamil": "மிருகசீரிடம்",
        "alternate_names": ["Mrgasira", "Mrigashirsha"],
        "span_zodiac": "Taurus 23°20' - Gemini 6°40'",
        "degree_start": 53.3333,
        "degree_end": 66.6667,
        "functional_nature": "Soft / Gentle",
        "functional_nature_tamil": "மிருதுவான / சாந்த",
        "gender": "Hermaphrodite / Eunuch",
        "result_grade": "GOOD",
        "ruling_deity": "Soma (Chandra / The Moon God)",
        "ruling_planet": "Mars",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Servants / Shudra",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Weak",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Deer's Head",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Constructing a house (griha rambham)",
            "Marriage (vivaha)",
            "Travel & research journeys",
            "Working with camels and elephants",
            "Singing, dancing, and fine arts"
        ],
        "inauspicious_for": [
            "Confrontation, heavy warfare, harsh punishment"
        ],
        "ascendant_indications": (
            "Attractive, inquisitive, passionate seeker of truth and beauty. Feminine grace, vacillating mind, "
            "vulnerable to sickness in early childhood, thin physique, talkative, devoted to mother, gifted orator or singer."
        ),
        "moon_indications": (
            "Fickle, sharp-witted, timid, eloquent, averse to direct physical combat, industrious in work, "
            "wealthy, indulgent in refined sensual pleasures."
        ),
        "rules_over": [
            "Beasts, birds, forest dwellers",
            "Flowers, fruits, fragrant articles, sea products",
            "Musicians, poets, lovers, messengers",
            "Drinkers of celestial nectar (Soma rasa)"
        ],
        "places": ["Forests, parks, music halls, taxation departments"],
        "objects": ["Platinum, diamond, rubies, corals, sandalwood powder, snuff, tobacco"],
        "abstracts": ["Searching mind", "Innocence", "Poetic longing"],
        "general_remedy": "None strictly needed; worship of Chandra and Lord Muruga brings great blessings.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "23°20' - 26°40' Taurus (Sun / Leo Navamsa)",
                "traits": "Wealthy, overcoming enemies, sturdy build, strong appetite.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "26°40' Taurus - 0°00' Gemini (Mercury / Virgo Navamsa)",
                "traits": "Handsome, truthful, cultured, full of deep knowledge, concealed inner frustration.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "0°00' - 3°20' Gemini (Venus / Libra Navamsa)",
                "traits": "Lover of travel, grateful, persuasive speaker, benevolent, keen intellect.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "3°20' - 6°40' Gemini (Mars / Scorpio Navamsa)",
                "traits": "Passionate, knowledgeable in erotics, prone to physical wounds, formidable debater.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 6,
        "name": "Ardra",
        "name_tamil": "திருவாதிரை",
        "alternate_names": ["Arudra"],
        "span_zodiac": "Gemini 6°40' - 20°00'",
        "degree_start": 66.6667,
        "degree_end": 80.0,
        "functional_nature": "Dreadful / Sharp",
        "functional_nature_tamil": "தீட்சண / கொடிய",
        "gender": "Feminine",
        "result_grade": "OK",
        "ruling_deity": "Rudra (Lord Shiva as the Storm & Destroyer)",
        "ruling_planet": "Rahu",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Detestable / Outcast",
        "motivation": "Kama (Carnal Desires)",
        "sight_quality": "Average",
        "luminary_type": "Lunar",
        "kula_type": "Kulakul",
        "num_stars": 1,
        "symbol_shape": "Teardrop / Diamond / Shining Ruby",
        "favourable_actions": [
            "Surgical operations & medical interventions",
            "Chemistry, alchemy, research labs",
            "Demolishing old structures",
            "Tantric incantations & spirit exorcism",
            "Reconcilement after severe estrangement"
        ],
        "inauspicious_for": [
            "Marriage, peaceful celebrations, inaugurations"
        ],
        "ascendant_indications": (
            "Proud, robust physique, long-lived, receiving money from government sources. Few children, "
            "cunning speech, fickle mind, athletic disposition, critical memory, prone to deceit or harsh labor."
        ),
        "moon_indications": (
            "Haughty, emotionally stormy, mischievous, highly perceptive beneath facades, capable of surviving immense trials."
        ),
        "rules_over": [
            "Hunters, animal workers, slaughterers",
            "Enchanters, sorcerers, callers of spirits",
            "Cereals, scientific chemicals",
            "Those operating in crisis and emergency"
        ],
        "places": ["Forts, battlements, chemical plants, high observation canopies"],
        "objects": ["Precious rubies, chemicals, precision surgical instruments"],
        "abstracts": ["The teardrop of suffering", "Emotional catharsis", "Storm renewal"],
        "general_remedy": "Feed the learned brahmanas and chant Sri Rudram / Shiva panchakshari.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "6°40' - 10°00' Gemini (Jupiter / Sagittarius Navamsa)",
                "traits": "Noble habits, truthful, intelligent, senses well-controlled.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "10°00' - 13°20' Gemini (Saturn / Capricorn Navamsa)",
                "traits": "Frank, outspoken, proud, prone to illness, direct to a fault.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "13°20' - 16°40' Gemini (Saturn / Aquarius Navamsa)",
                "traits": "Fiery temper, cutting speech, skeptical of dogma, rebellious.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "16°40' - 20°00' Gemini (Jupiter / Pisces Navamsa)",
                "traits": "Perverse advice, strained ties with siblings, burdened mind.",
                "dosha_status": "Dosha Present (Minor)",
                "dosha_affects": "Generates emotional strain and discord with kin.",
                "remedy": "Feed the brahmanas and recite Shiva stotras."
            }
        ]
    },
    {
        "id": 7,
        "name": "Punarvasu",
        "name_tamil": "புனர்பூசம்",
        "alternate_names": ["Purnavasu"],
        "span_zodiac": "Gemini 20°00' - Cancer 3°20'",
        "degree_start": 80.0,
        "degree_end": 93.3333,
        "functional_nature": "Temporary / Movable",
        "functional_nature_tamil": "சர / விரைவு",
        "gender": "Masculine",
        "result_grade": "OK",
        "ruling_deity": "Aditi (Mother of the Demigods / Cosmic Space)",
        "ruling_planet": "Jupiter",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Vaishya",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Good",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 4,
        "symbol_shape": "Bow & Quiver / Building",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Constructing a house (griha rambham)",
            "Changing residence / moving into new home",
            "Commencing business travels & trade deals",
            "Acquiring conveyances and vehicles"
        ],
        "inauspicious_for": [
            "Giving or taking loans (money may keep returning in cycles)"
        ],
        "ascendant_indications": (
            "Freedom-loving, cannot be tied down, frequent change of residence or partners. Charitable, intelligent, "
            "easily contented, poetic, passionate, careful in business with moderate financial success."
        ),
        "moon_indications": (
            "Self-controlled, happy, friendly, honorable, easily contented, quick to recover from setbacks."
        ),
        "rules_over": [
            "Merchants, traders, artisans",
            "The famous, truthful, generous, pure",
            "Cereals and harvested grains",
            "Travelers and those seeking spiritual renewal"
        ],
        "places": ["Granaries, ships, commercial warehouses, temporary dwellings"],
        "objects": ["Bows, quivers, arrows, woven fabrics"],
        "abstracts": ["Star of Renewal", "Return of the light", "Purification of self"],
        "general_remedy": "No special dosha remedy required; honoring Goddess Aditi and Jupiter brings joy.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "20°00' - 23°20' Gemini (Mars / Aries Navamsa)",
                "traits": "Hairy, sturdy build, wise but arrogant, quick temper, passionate.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "23°20' - 26°40' Gemini (Venus / Taurus Navamsa)",
                "traits": "Good habits, protects siblings, clever in work, religious, bilious constitution.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "26°40' Gemini - 0°00' Cancer (Mercury / Gemini Navamsa - Vargottama)",
                "traits": "Poetic, long life, clever in speech, occasionally hypocritical, dental sensitivity.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "0°00' - 3°20' Cancer (Moon / Cancer Navamsa - Pushkara & Vargottama)",
                "traits": "Handsome, admired by opposite sex, eloquent speaker, highly cherished.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 8,
        "name": "Pushya",
        "name_tamil": "பூசம்",
        "alternate_names": ["Pushyami", "Poosam"],
        "span_zodiac": "Cancer 3°20' - 16°40'",
        "degree_start": 93.3333,
        "degree_end": 106.6667,
        "functional_nature": "Light / Swift",
        "functional_nature_tamil": "லகு / சுறுசுறுப்பு",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Brihaspati (Guru / Priest of the Demigods)",
        "ruling_planet": "Saturn",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Kshatriya",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Blind",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Cow's Udder / Arrow / Flower",
        "favourable_actions": [
            "BEST of all 27 stars for auspicious ventures",
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Parting of hair (simontan)",
            "Entering new house (griha pravesham)",
            "Starting journeys & commerce",
            "Taking medicine & healing therapies",
            "All spiritual & virtuous rituals (satkriya karmanis)"
        ],
        "inauspicious_for": [
            "Marriage ceremony itself (classical exception: Pushya is forbidden for Vivaha under Sage Bharadwaja's curse)"
        ],
        "ascendant_indications": (
            "Earnest, thoughtful, religious, stubborn yet eloquent. Learned in scriptures, independent, "
            "rises to high status, nourishes relatives, plump body."
        ),
        "moon_indications": (
            "Composed mind, learned, wealthy, virtuous, universally liked, wise advisor."
        ),
        "rules_over": [
            "Wheat, rice, barley, sugarcane",
            "Ministers, advisors, high officials",
            "Virtuous priests engaged in sacrifices",
            "Forest dwellers and fishermen"
        ],
        "places": ["Forests, royal courts, hermitages, temples"],
        "objects": ["Arrows, sacred milk, grains, holy books"],
        "abstracts": ["Supreme nourishment", "Karmic flowering", "Divine wisdom"],
        "general_remedy": "Gift a piece of Sandalwood to the Deity or learned brahmins.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "3°20' - 6°40' Cancer (Sun / Leo Navamsa)",
                "traits": "Cruel temper, harbors ill will, likes solitude, prone to shooting bodily pains.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "6°40' - 10°00' Cancer (Mercury / Virgo Navamsa)",
                "traits": "Respected by many, liking everyone, moderate wealth, balanced outlook.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects father and mother.",
                "remedy": "Gift a piece of fragrant Sandalwood to the Deity or learned brahmins."
            },
            {
                "pada_number": 3,
                "degree_range": "10°00' - 13°20' Cancer (Venus / Libra Navamsa)",
                "traits": "Happy, knowledgeable, devoted, spiritual wisdom, respected by the wise, forgiving.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects father and mother.",
                "remedy": "Gift a piece of Sandalwood to the Deity or learned brahmins."
            },
            {
                "pada_number": 4,
                "degree_range": "13°20' - 16°40' Cancer (Mars / Scorpio Navamsa)",
                "traits": "Heavy build, quarrelsome tendencies, sensual passion, hard-hearted.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 9,
        "name": "Ashlesha",
        "name_tamil": "ஆயில்யம்",
        "alternate_names": ["Aslesa", "Ayilyam"],
        "span_zodiac": "Cancer 16°40' - 30°00'",
        "degree_start": 106.6667,
        "degree_end": 120.0,
        "functional_nature": "Dreadful / Sharp",
        "functional_nature_tamil": "தீட்சண / கொடிய",
        "gender": "Feminine",
        "result_grade": "MISERY",
        "ruling_deity": "Sarpas (Nagas / Divine Serpents)",
        "ruling_planet": "Mercury",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Outcast",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Weak",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 5,
        "symbol_shape": "Coiled Serpent / Wheel",
        "favourable_actions": [
            "Overcoming adversaries & secret maneuvers",
            "Handling poisons, reptiles, and dangerous chemicals",
            "Tantric rituals & serpent propitiation",
            "Commerce requiring shrewd negotiations",
            "Root medicines and surgical procedures"
        ],
        "inauspicious_for": [
            "All peaceful, gentle, domestic, or marriage beginnings"
        ],
        "ascendant_indications": (
            "Anti-social, penetrating knowledge, austere habits, tactless, cruel, fickle, few children. "
            "Capable of immense exertion, needs to develop tact and perform humanitarian service to relieve parental anxiety."
        ),
        "moon_indications": (
            "Insincere, voracious appetite, deceitful, ungrateful, sharp tongue, yet mystical and occult-oriented."
        ),
        "rules_over": [
            "Insects, reptiles, serpents, poisoners",
            "Robbers and covert agents",
            "Physicians handling potent poisons and herbs",
            "Roots, bulbs, medicinal fruits"
        ],
        "places": ["Dense snake burrows, poison labs, dense jungles, secret chambers"],
        "objects": ["Poisons, serpents, wheel shapes, chemical acids"],
        "abstracts": ["The entwiner", "Kundalini force", "Occult hypnosis"],
        "general_remedy": "Annadaanam - provide wholesome meals for 21 brahmanas and Naga puja.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "16°40' - 20°00' Cancer (Jupiter / Sagittarius Navamsa)",
                "traits": "Well-known, charitable, broad chest, long arms, wealthy, happy and wise.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Generates minor friction.",
                "remedy": "Feed the learned brahmins."
            },
            {
                "pada_number": 2,
                "degree_range": "20°00' - 23°20' Cancer (Saturn / Capricorn Navamsa)",
                "traits": "Unmotivated, prone to poor hygiene, loss of money, sickly.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Creates loss of wealth for the household.",
                "remedy": "Provide meals for 21 brahmanas."
            },
            {
                "pada_number": 3,
                "degree_range": "23°20' - 26°40' Cancer (Saturn / Aquarius Navamsa)",
                "traits": "Crooked build, fiery temper, scientific intellect, unyielding.",
                "dosha_status": "Severe Dosha",
                "dosha_affects": "Adversely affects the native's mother (Gandanta junction).",
                "remedy": "Annadaanam - provide meals for 21 brahmanas and perform Ashlesha Shanti."
            },
            {
                "pada_number": 4,
                "degree_range": "26°40' Cancer - 0°00' Leo (Jupiter / Pisces Navamsa - Gandanta)",
                "traits": "Passionate, loose attachments, frequently ailing, few children.",
                "dosha_status": "Dosha Present (Gandanta)",
                "dosha_affects": "Affects father/native directly.",
                "remedy": "Annadaanam - feed 21 brahmanas and perform Ayilya Gandanta Shanti."
            }
        ]
    },
    {
        "id": 10,
        "name": "Magha",
        "name_tamil": "மகம்",
        "alternate_names": ["Makha"],
        "span_zodiac": "Leo 0°00' - 13°20'",
        "degree_start": 120.0,
        "degree_end": 133.3333,
        "functional_nature": "Fierce / Cruel",
        "functional_nature_tamil": "உக்கிர / தீவிர",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Pitris (Ancestors / Forefathers)",
        "ruling_planet": "Ketu",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Shudra",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Average",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 5,
        "symbol_shape": "Royal Throne Room / House / Palanquin",
        "favourable_actions": [
            "Ancestral rituals & Tarpanam",
            "Coronations, assuming high office",
            "Singing, dancing, theatrical pageantry",
            "Agriculture and grain storage",
            "Military maneuvers, battling foes, setting fires to obstacles"
        ],
        "inauspicious_for": [
            "Lending money, undergoing medical therapies"
        ],
        "ascendant_indications": (
            "Servants and wealth, enjoys pleasures, devoted to God and elders, receives praise from dignitaries. "
            "Proud, dignified, royal lineage bearing, thorough executor of work."
        ),
        "moon_indications": (
            "Lives in luxury and comfort, physically strong, devoted to parents and ancestral traditions, authoritative."
        ),
        "rules_over": [
            "Aristocrats, granaries, mountaineers",
            "Those devoted to ancestors and parents",
            "Heroes, military leaders, large traders"
        ],
        "places": ["Granaries, palaces, royal courts, historical monuments"],
        "objects": ["Thrones, palanquins, family heirlooms, weapons"],
        "abstracts": ["The Mighty One", "Ancestral glory", "Lordship over masses"],
        "general_remedy": "Gift a Silver horse icon to the Deity or learned brahmanas, and perform Pitru Tarpanam.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "0°00' - 3°20' Leo (Mars / Aries Navamsa - Gandanta)",
                "traits": "Reddish appearance, large appetite, ferocious gaze, enthusiastic character.",
                "dosha_status": "Severe Dosha (Gandanta)",
                "dosha_affects": "Adversely affects the child / native in early infancy.",
                "remedy": "Gift a Silver horse icon to the Deity or learned brahmanas; perform Magha Shanti."
            },
            {
                "pada_number": 2,
                "degree_range": "3°20' - 6°40' Leo (Venus / Taurus Navamsa)",
                "traits": "Worrier, expensive tastes, ambitious, knowledgeable in unconventional subjects.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "6°40' - 10°00' Leo (Mercury / Gemini Navamsa)",
                "traits": "Flatterer, back-biter, strong constitution, susceptible to intestinal complaints.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects father and mother.",
                "remedy": "Gift a Silver horse icon or feed the brahmanas."
            },
            {
                "pada_number": 4,
                "degree_range": "10°00' - 13°20' Leo (Moon / Cancer Navamsa)",
                "traits": "Heavily passionate, sweet talker, proud, charismatic.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 11,
        "name": "Purva Phalguni",
        "name_tamil": "பூரம்",
        "alternate_names": ["Pubba", "Poorvaphalguni"],
        "span_zodiac": "Leo 13°20' - 26°40'",
        "degree_start": 133.3333,
        "degree_end": 146.6667,
        "functional_nature": "Fierce / Cruel",
        "functional_nature_tamil": "உக்கிர / தீவிர",
        "gender": "Feminine",
        "result_grade": "OK",
        "ruling_deity": "Bhaga (God of Fortune & Prosperity)",
        "ruling_planet": "Venus",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Brahmana",
        "motivation": "Kama (Carnal Desires)",
        "sight_quality": "Good",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 2,
        "symbol_shape": "Front Legs of a Bed / Scaffold / Swinging Hammock",
        "favourable_actions": [
            "Demolishing opponents & competitive sports",
            "Selling commodities, cotton, honey, salt, oils",
            "Artistic expression, acting, music, theater",
            "Dealing with weapons, fire, and heat",
            "Romance, courtship, persuasion"
        ],
        "inauspicious_for": [
            "Starting new construction or laying foundations"
        ],
        "ascendant_indications": (
            "Active, physical person always on the go, well-known, able to command others. Generous in money distribution, "
            "inclined toward natural outdoor life, excellent health, passionate love of sports."
        ),
        "moon_indications": (
            "Wanderer, intensely loyal to chosen leader or cause, liberal, bright attractive appearance, sweet-spoken."
        ),
        "rules_over": [
            "Actors, musicians, artisans, young women",
            "Commodities, cotton, salt, honey, oil",
            "Friendly and amiable personalities"
        ],
        "places": ["Theaters, museums, slaughterhouses, dance halls"],
        "objects": ["Swinging hammocks, beds, sweet oils, cotton fabrics"],
        "abstracts": ["Fruit of the tree", "Fortune (Bhagya)", "Sensual luxury"],
        "general_remedy": "None strictly needed; worshipping Goddess Lakshmi / Parvati brings good fortune.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "13°20' - 16°40' Leo (Sun / Leo Navamsa - Vargottama)",
                "traits": "Sweet speech, brave, courageous, fiery temper, occasional laziness.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "16°40' - 20°00' Leo (Mercury / Virgo Navamsa)",
                "traits": "Hardworking, clean habits, well-known, spirited, high fluid intake.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "20°00' - 23°20' Leo (Venus / Libra Navamsa)",
                "traits": "Artistic talents, passionate, devoted to family, clever imagination.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "23°20' - 26°40' Leo (Mars / Scorpio Navamsa)",
                "traits": "Ungentle, turbulent, scars on body, father of sons.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Generates restlessness and friction.",
                "remedy": "None strictly required; feeding poor youth helps."
            }
        ]
    },
    {
        "id": 12,
        "name": "Uttara Phalguni",
        "name_tamil": "உத்திரம்",
        "alternate_names": ["Uttaraphalguni", "Uthiram"],
        "span_zodiac": "Leo 26°40' - Virgo 10°00'",
        "degree_start": 146.6667,
        "degree_end": 160.0,
        "functional_nature": "Fixed",
        "functional_nature_tamil": "ஸ்திர / நிலையான",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Aryaman (God of Patronage & Divine Chivalry)",
        "ruling_planet": "Sun",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Kshatriya",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Blind",
        "luminary_type": "Solar",
        "kula_type": "Akul",
        "num_stars": 2,
        "symbol_shape": "Back Legs of a Bed / Fig Tree",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Entering new house (griha pravesham)",
            "Constructing a house (griha rambham)",
            "Coronation & political appointments",
            "Marriage (vivaha)",
            "Long-term investments, patronages, foundations"
        ],
        "inauspicious_for": [
            "Severing long-standing friendships"
        ],
        "ascendant_indications": (
            "Handsome, learned, substantial wealth, generous yet proud, intelligent, inclined to spiritual penance. "
            "Great talent in business, handicrafts, and public patronage."
        ),
        "moon_indications": (
            "Earns through intellectual mastery, widely respected, voluptuous form, happy, friendly, owns self-acquired property."
        ),
        "rules_over": [
            "Kind-hearted, pure-living souls",
            "Learned scholars, devoted leaders, monarchs",
            "Fine grains and agricultural abundance",
            "Patrons of public welfare"
        ],
        "places": ["Town halls, royal palaces, charitable endowments, healing sanctuaries"],
        "objects": ["Beds, iron, stone, loudspeakers, megaphones"],
        "abstracts": ["Star of Patronage", "Enduring charity", "Fruitful harvest"],
        "general_remedy": "Gift a bronze/brass bowl filled with black Gingelly seeds to the Deity or learned brahmanas.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "26°40' Leo - 0°00' Virgo (Jupiter / Sagittarius Navamsa)",
                "traits": "Wealthy, famous, brave, prosperous household, doer of noble deeds.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Adversely affects both parents in childhood.",
                "remedy": "Gift a bowl filled with black Gingelly seeds to the Deity."
            },
            {
                "pada_number": 2,
                "degree_range": "0°00' - 3°20' Virgo (Saturn / Capricorn Navamsa)",
                "traits": "Critical nature, ungrounded, agricultural interest, modest means.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "3°20' - 6°40' Virgo (Saturn / Aquarius Navamsa)",
                "traits": "Proud, passionate, spotless cleanliness, extensive learning.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "6°40' - 10°00' Virgo (Jupiter / Pisces Navamsa)",
                "traits": "Humorous, occasionally ungrateful, critical disposition, small progeny.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Creates minor friction with elders.",
                "remedy": "None needed; honoring Sun God helps."
            }
        ]
    },
    {
        "id": 13,
        "name": "Hasta",
        "name_tamil": "அஸ்தம்",
        "alternate_names": ["Hastha"],
        "span_zodiac": "Virgo 10°00' - 23°20'",
        "degree_start": 160.0,
        "degree_end": 173.3333,
        "functional_nature": "Light / Swift",
        "functional_nature_tamil": "லகு / சுறுசுறுப்பு",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Savitr (The Sun as the Solar Awakener)",
        "ruling_planet": "Moon",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Vaishya",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Weak",
        "luminary_type": "Solar",
        "kula_type": "Akul",
        "num_stars": 5,
        "symbol_shape": "Hand / Clenched Fist",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Constructing a house (griha rambham)",
            "Marriage (vivaha)",
            "Coronation, entering commerce, medical therapies",
            "Craftsmanship, jewelry making, tailoring, sleight of hand"
        ],
        "inauspicious_for": [
            "Inactivity, prolonged rest"
        ],
        "ascendant_indications": (
            "Likeable character, extraordinarily skilled with the hands, sociable, entertaining, fixed in purpose. "
            "Handsome, orthodox behavior, sensitive, artistic, inclined toward public service, fond of foreign travels."
        ),
        "moon_indications": (
            "Industrious, sharp dexterity, clever in humor and mimicry, passionate, resourceful."
        ),
        "rules_over": [
            "Chauffeurs, travelers in conveyances",
            "Artists, jewelers, craftsmen, Vedic scholars",
            "Traders, commodities, cereals, elephants"
        ],
        "places": ["Embassies, craft workshops, jewelry bazaars, transport hubs"],
        "objects": ["Merchandise, conveyances, ornaments, fine clothes"],
        "abstracts": ["Clenched fist of determination", "Healing touch", "Dispelling ignorance"],
        "general_remedy": "None strictly needed; Aditya Hridaya stotram recitation brings radiant grace.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "10°00' - 13°20' Virgo (Mars / Aries Navamsa)",
                "traits": "Strong, able to defeat enemies, quick temper, energetic.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "13°20' - 16°40' Virgo (Venus / Taurus Navamsa)",
                "traits": "Sweet speech, admirable qualities, lives in homeland, devoted.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "16°40' - 20°00' Virgo (Mercury / Gemini Navamsa)",
                "traits": "Deep love for music, crafty mind, prone to early separation from father.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects parents (especially father).",
                "remedy": "Annadaanam and reciting Vishnu Sahasranama."
            },
            {
                "pada_number": 4,
                "degree_range": "20°00' - 23°20' Virgo (Moon / Cancer Navamsa)",
                "traits": "Righteous conduct, strong, high status, robust appetite, aided by mother's lineage.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 14,
        "name": "Chitra",
        "name_tamil": "சித்திரை",
        "alternate_names": ["Citra", "Chithirai"],
        "span_zodiac": "Virgo 23°20' - Libra 6°40'",
        "degree_start": 173.3333,
        "degree_end": 186.6667,
        "functional_nature": "Soft / Gentle",
        "functional_nature_tamil": "மிருதுவான / சாந்த",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Tvashtar (Visvakarma / Celestial Architect)",
        "ruling_planet": "Mars",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Agriculturist / Shudra",
        "motivation": "Kama (Carnal Desires)",
        "sight_quality": "Average",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 1,
        "symbol_shape": "Bright Pearl / Shining Gem",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Entering new house (griha pravesham)",
            "Constructing a house (griha rambham)",
            "Wearing new clothes and jewelry",
            "Architecture, engineering, visual arts, painting",
            "Interior decoration, sculpture, perfumery"
        ],
        "inauspicious_for": [
            "Drab, routine, or destructive activities"
        ],
        "ascendant_indications": (
            "Wears colorful clothes and jewels, popular with opposite sex, engages in diverse pursuits, "
            "critical streak, lives away from birthplace, brilliant visual flair."
        ),
        "moon_indications": (
            "Beautifully formed body, magnetic eyes, elegant attire, refined speech, artistic intuition."
        ),
        "rules_over": [
            "Jewelers, gemologists, painters, writers",
            "Singers, perfumers, mathematicians",
            "Surgeons, weavers, architects",
            "Fine royal crops and flowers"
        ],
        "places": ["Art studios, architectural offices, jewelry vaults, perfume laboratories"],
        "objects": ["Dresses, ornaments, pearls, gemstones, colorful tapestries"],
        "abstracts": ["The Brilliant One", "Visual elegance", "Architectural perfection"],
        "general_remedy": "Vastradanam - gift beautiful new cloths to the Deity and learned Vaishnavas/brahmanas.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "23°20' - 26°40' Virgo (Sun / Leo Navamsa)",
                "traits": "Strong, arrogant, uncharitable, raised across two households, eye sensitivity.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects parents.",
                "remedy": "Vastradanam - gift nice new cloth to Deity and brahmins."
            },
            {
                "pada_number": 2,
                "degree_range": "26°40' Virgo - 0°00' Libra (Mercury / Virgo Navamsa)",
                "traits": "Sticks to word, walks briskly, performs penances, modest wealth.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects parents.",
                "remedy": "Vastradanam - gift cloth to brahmins."
            },
            {
                "pada_number": 3,
                "degree_range": "0°00' - 3°20' Libra (Venus / Libra Navamsa - Vargottama)",
                "traits": "Famous, gentle habits, brave, righteous means, highly artistic.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Minor friction.",
                "remedy": "None needed."
            },
            {
                "pada_number": 4,
                "degree_range": "3°20' - 6°40' Libra (Mars / Scorpio Navamsa)",
                "traits": "Knack for business, sweet and cunning speech, striking appearance.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Minor.",
                "remedy": "None needed."
            }
        ]
    },
    {
        "id": 15,
        "name": "Swati",
        "name_tamil": "சுவாதி",
        "alternate_names": ["Svati"],
        "span_zodiac": "Libra 6°40' - 20°00'",
        "degree_start": 186.6667,
        "degree_end": 200.0,
        "functional_nature": "Temporary / Movable",
        "functional_nature_tamil": "சர / விரைவு",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Vayu (Demigod of the Wind & Air)",
        "ruling_planet": "Rahu",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Material / Vaishya",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Good",
        "luminary_type": "Solar",
        "kula_type": "Akul",
        "num_stars": 1,
        "symbol_shape": "Shoot of Plant / Coral / Sword / Priest",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Entering new house (griha pravesham)",
            "Marriage (vivaha)",
            "Agriculture and sowing",
            "Buying vehicles and transport machines",
            "Travel, air journeys, learning theology"
        ],
        "inauspicious_for": [
            "Rigid, immovable arrangements requiring fixity"
        ],
        "ascendant_indications": (
            "Deliberate and slow in action, modest simple appearance, lives away from birthplace, "
            "independent in thought and deed (the self-going), kind, happy, engaged in religious affairs."
        ),
        "moon_indications": (
            "Righteous, clever in commerce, sweet-spoken, modest, compassionate, adaptable to any wind of change."
        ),
        "rules_over": [
            "Birds, beasts, horses, traveling traders",
            "Grains that cause wind (beans/pulses)",
            "Ascetics, theologians, connoisseurs"
        ],
        "places": ["Airports, open grasslands, windy hills, educational institutions"],
        "objects": ["Swords, rubies, light musical instruments, wind mills"],
        "abstracts": ["Self-going independence", "The priest / theologian", "Gentle flexibility"],
        "general_remedy": "No dosha remedy needed; all padas are auspicious.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "6°40' - 10°00' Libra (Jupiter / Sagittarius Navamsa)",
                "traits": "Courageous, eloquent, scientific intellect, commanding servants.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "10°00' - 13°20' Libra (Saturn / Capricorn Navamsa)",
                "traits": "Unconventional earnings, hidden passions, secretive acts, strategic.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "13°20' - 16°40' Libra (Saturn / Aquarius Navamsa)",
                "traits": "Fame, gentle demeanor, courage, company of saintly persons.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "16°40' - 20°00' Libra (Jupiter / Pisces Navamsa)",
                "traits": "Passionate, quick temper, stubborn, bold outspoken views.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 16,
        "name": "Vishakha",
        "name_tamil": "விசாகம்",
        "alternate_names": ["Visakha", "Visakam"],
        "span_zodiac": "Libra 20°00' - Scorpio 3°20'",
        "degree_start": 200.0,
        "degree_end": 213.3333,
        "functional_nature": "Mixed",
        "functional_nature_tamil": "மிஸ்ர / கலப்பு",
        "gender": "Hermaphrodite / Eunuch",
        "result_grade": "OK",
        "ruling_deity": "Indra and Agni (Lords of Lightning & Sacrificial Fire)",
        "ruling_planet": "Jupiter",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Outcast",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Blind",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 4,
        "symbol_shape": "Arched Gateway / Potter's Wheel / Branching Tree",
        "favourable_actions": [
            "Writing, dancing, singing, literary composition",
            "Mechanical engineering and technical tasks",
            "Commercial collections and corn gathering",
            "Goal-directed campaigns and relentless pursuit of targets",
            "Routine duties and professional responsibilities"
        ],
        "inauspicious_for": [
            "Soft diplomatic retreats, surrender"
        ],
        "ascendant_indications": (
            "Aggressive, impatient, wealthy, wise, devoted to worship, talkative, easily angered. "
            "Cultivates something until the fruit is ripe, success in import/export."
        ),
        "moon_indications": (
            "Quarrelsome, envious of rivals, covetous of victory, highly persuasive orator, bright presence."
        ),
        "rules_over": [
            "Trees bearing red blossoms and fruits",
            "Sesamum, green gram, black gram, cotton",
            "Those devoted to Indra and Agni, determined campaigners"
        ],
        "places": ["Arched gateways, power plants, manufacturing mills, sports arenas"],
        "objects": ["Dresses, ornaments, iron, stone, commercial items"],
        "abstracts": ["Star of Purpose", "Relentless determination", "Branching triumph"],
        "general_remedy": "Provide wholesome meals for 21 devout learned brahmanas and serve them with humility.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "20°00' - 23°20' Libra (Mars / Aries Navamsa)",
                "traits": "Envious, arrogant, ungentle; gifted in business, astrology, and mathematical calculation.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects relatives of the family.",
                "remedy": "Provide meals for 21 brahmin devotees."
            },
            {
                "pada_number": 2,
                "degree_range": "23°20' - 26°40' Libra (Venus / Taurus Navamsa)",
                "traits": "Diplomatic, clever, keen interest in science, palmistry, or astrology.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects family relatives.",
                "remedy": "Provide meals for 21 brahmin devotees."
            },
            {
                "pada_number": 3,
                "degree_range": "26°40' Libra - 0°00' Scorpio (Mercury / Gemini Navamsa)",
                "traits": "Strong, cheerful, clean-hearted, talented in mathematics, eloquent speaker.",
                "dosha_status": "Shanti Required",
                "dosha_affects": "Need to perform Shanti for family welfare.",
                "remedy": "Provide meals for 21 brahmin devotees."
            },
            {
                "pada_number": 4,
                "degree_range": "0°00' - 3°20' Scorpio (Moon / Cancer Navamsa)",
                "traits": "Eloquent, noble thoughts, wise, artistic, endowed with good fortune and righteous deeds.",
                "dosha_status": "Shanti Required",
                "dosha_affects": "Need to perform Shanti for household concord.",
                "remedy": "Provide meals for 21 brahmin devotees."
            }
        ]
    },
    {
        "id": 17,
        "name": "Anuradha",
        "name_tamil": "அனுஷம்",
        "alternate_names": ["Anushya", "Anooradha"],
        "span_zodiac": "Scorpio 3°20' - 16°40'",
        "degree_start": 213.3333,
        "degree_end": 226.6667,
        "functional_nature": "Soft / Gentle",
        "functional_nature_tamil": "மிருதுவான / சாந்த",
        "gender": "Hermaphrodite / Eunuch",
        "result_grade": "GOOD",
        "ruling_deity": "Mitra (Demigod of Friendship & Sun God Vivasvan)",
        "ruling_planet": "Saturn",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Shudra",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Weak",
        "luminary_type": "Solar",
        "kula_type": "Akul",
        "num_stars": 3,
        "symbol_shape": "Lotus Flower / Triumphal Archway / Staff",
        "favourable_actions": [
            "Entering new house (griha pravesham)",
            "Marriage (vivaha)",
            "Eight kinds of auspicious ceremonies (ashta mangala)",
            "Thread ceremony (upanayanam)",
            "Constructing a house (griha rambham)",
            "Installing Deity/idol (avahani)",
            "Forming alliances, partnerships, and organizing collective endeavors",
            "Travel, tourism, and diplomatic assemblies"
        ],
        "inauspicious_for": [
            "Harsh combat, acts of malice"
        ],
        "ascendant_indications": (
            "Wanderer, devoted to spiritual pursuits, unable to bear hunger, kind, handsome, "
            "lives away from birthplace. Fond of organizational life, corporate leadership, and devotional service."
        ),
        "moon_indications": (
            "Star of Success; brilliant organizer, affectionate, loyal friend, steadfast in spiritual devotion (follower of Radha)."
        ),
        "rules_over": [
            "Men of prowess, corporate leaders, tourists, motorists",
            "Friends of the virtuous, lovers of assemblies",
            "All honest persons, autumn crops"
        ],
        "places": ["Assembly halls, conference centers, tourist venues, temples"],
        "objects": ["Dresses, ornaments, woolen goods, hides"],
        "abstracts": ["Star of Success", "Divine friendship", "Devotional call to action"],
        "general_remedy": "None required; all 4 padas are auspicious and pure.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "3°20' - 6°40' Scorpio (Sun / Leo Navamsa)",
                "traits": "Truthful, noble deeds, legal talent, interest in ancient subjects, occasionally misdirected advice.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "6°40' - 10°00' Scorpio (Mercury / Virgo Navamsa)",
                "traits": "Kind, religious, fortunate, thrives in foreign lands, ambitious.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "10°00' - 13°20' Scorpio (Venus / Libra Navamsa)",
                "traits": "Wise, truthful, talented astrologer, humorous, ambitious.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "13°20' - 16°40' Scorpio (Mars / Scorpio Navamsa)",
                "traits": "Courageous, truthful, passionate, occasionally sharp or confrontational.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 18,
        "name": "Jyeshtha",
        "name_tamil": "கேட்டை",
        "alternate_names": ["Jyestha", "Kettai"],
        "span_zodiac": "Scorpio 16°40' - 30°00'",
        "degree_start": 226.6667,
        "degree_end": 240.0,
        "functional_nature": "Dreadful / Sharp",
        "functional_nature_tamil": "தீட்சண / கொடிய",
        "gender": "Feminine",
        "result_grade": "OK",
        "ruling_deity": "Indra (King of the Demigods / Shakra)",
        "ruling_planet": "Mercury",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Agriculturist / Shudra",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Average",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Earring / Umbrella / Round Talisman",
        "favourable_actions": [
            "Assuming executive positions & commanding subordinates",
            "Shaving (cuda karanam)",
            "Commercial negotiations & high finance",
            "Writing, mechanical tasks, music, performing arts",
            "Confronting adversaries and asserting authority"
        ],
        "inauspicious_for": [
            "Delicate, submissive, or yielding undertakings"
        ],
        "ascendant_indications": (
            "Natural leader, seniormost (The Chief), intent on objective. External polish and respectability, "
            "passionate interior, honored by dignitaries, skilled administrator."
        ),
        "moon_indications": (
            "Virtuous, contented yet quick-tempered and irritable, executive command, self-reliant."
        ),
        "rules_over": [
            "Battle heroes, corporate leaders, influential men of pedigree",
            "Kings intent on conquest, military commanders",
            "Thieves, secretive operatives, electric power workers"
        ],
        "places": ["Thermal electric stations, administrative headquarters, high towers"],
        "objects": ["Iron, stone, weapons, earrings, umbrellas"],
        "abstracts": ["The Seniormost Chief", "Executive mastery", "Protective umbrella"],
        "general_remedy": "Godaan - gift of a cow or equivalent value to the Deity or qualified learned brahmana.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "16°40' - 20°00' Scorpio (Jupiter / Sagittarius Navamsa)",
                "traits": "Humorous, proud, talented writer, living with honor.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Generates loss of happiness in family circle.",
                "remedy": "Godaan or feeding brahmanas."
            },
            {
                "pada_number": 2,
                "degree_range": "20°00' - 23°20' Scorpio (Saturn / Capricorn Navamsa)",
                "traits": "Clean, eloquent, victorious, occasional health ailments.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Can cause financial fluctuations and loss of wealth.",
                "remedy": "Godaan or equivalent charity."
            },
            {
                "pada_number": 3,
                "degree_range": "23°20' - 26°40' Scorpio (Saturn / Aquarius Navamsa)",
                "traits": "Bitterness with relatives, eye troubles, owns landed property or livestock.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Adversely affects father of the native.",
                "remedy": "Godaan - gift of cow/equivalent to learned brahmin."
            },
            {
                "pada_number": 4,
                "degree_range": "26°40' Scorpio - 0°00' Sagittarius (Jupiter / Pisces Navamsa - Gandanta)",
                "traits": "Cruel, quarrelsome, prone to physical misery or motor difficulties.",
                "dosha_status": "Severe Dosha (Gandanta)",
                "dosha_affects": "Adversely affects mother of the native.",
                "remedy": "Perform Jyeshtha Gandanta Shanti and Godaan."
            }
        ]
    },
    {
        "id": 19,
        "name": "Mula",
        "name_tamil": "மூலம்",
        "alternate_names": ["Moola"],
        "span_zodiac": "Sagittarius 0°00' - 13°20'",
        "degree_start": 240.0,
        "degree_end": 253.3333,
        "functional_nature": "Dreadful / Sharp",
        "functional_nature_tamil": "தீட்சண / கொடிய",
        "gender": "Hermaphrodite / Eunuch",
        "result_grade": "GOOD",
        "ruling_deity": "Nirriti (Goddess of Calamity & Dissolution)",
        "ruling_planet": "Ketu",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Outcast / Carnal",
        "motivation": "Kama (Carnal Desires)",
        "sight_quality": "Good",
        "luminary_type": "Solar",
        "kula_type": "Kulakul",
        "num_stars": 11,
        "symbol_shape": "Tied Bunch of Roots / Lion's Tail / Elephant's Goad",
        "favourable_actions": [
            "Root medicine extraction & herbal research",
            "Investigating origins and foundational research",
            "Demolition, uprooting obstacles, warfare",
            "Feeding on roots, bulbs, fruits",
            "Occult investigations, tantra, deep philosophy"
        ],
        "inauspicious_for": [
            "Routine financial lending, fragile beginnings"
        ],
        "ascendant_indications": (
            "Ambitious, independent, interest in politics, handsome appearance, learned but subject to mental vacillation. "
            "Deep search for origin of life, occasional marital turmoil."
        ),
        "moon_indications": (
            "Proud, fairly well-to-do, soft disposition, fixed mind, luxurious habits."
        ),
        "rules_over": [
            "Medicines, physicians, group leaders",
            "Dealers in roots, bulbs, flowers, fruits, seeds",
            "Ascetics living on wilderness roots, wealthy persons"
        ],
        "places": ["Root cellars, botanical gardens, medicinal labs, dense forests"],
        "objects": ["Iron, stone, weapons, medicinal roots"],
        "abstracts": ["The Root Origin", "Dissolution of illusions", "Uprooting darkness"],
        "general_remedy": "Gift a Buffalo or equivalent value to the Deity or a qualified learned brahmana; perform Mula Shanti.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "0°00' - 3°20' Sagittarius (Mars / Aries Navamsa - Gandanta)",
                "traits": "Knowledgeable, devoted but lethargic, sickly, arrogant, few children.",
                "dosha_status": "Severe Dosha (Gandanta)",
                "dosha_affects": "Adversely affects parents (specifically father/native).",
                "remedy": "Gift a Buffalo or equivalent cost to Deity or learned brahmin; perform Mula Shanti."
            },
            {
                "pada_number": 2,
                "degree_range": "3°20' - 6°40' Sagittarius (Venus / Taurus Navamsa)",
                "traits": "Truthful, gentle, knowledgeable; prone to heart or eye sensitivity.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects father of the native.",
                "remedy": "Perform Mula Shanti and Annadaanam."
            },
            {
                "pada_number": 3,
                "degree_range": "6°40' - 10°00' Sagittarius (Mercury / Gemini Navamsa)",
                "traits": "Passionate, handsome, contemplative nature, unconventional actions.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Loss of wealth can be expected.",
                "remedy": "Charity to brahmins and Annadaanam."
            },
            {
                "pada_number": 4,
                "degree_range": "10°00' - 13°20' Sagittarius (Moon / Cancer Navamsa)",
                "traits": "Strong, clever, gentle, wise, senses mastered, triumphs over opponents.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 20,
        "name": "Purva Ashadha",
        "name_tamil": "பூராடம்",
        "alternate_names": ["Poorvashad", "Purvasadha"],
        "span_zodiac": "Sagittarius 13°20' - 26°40'",
        "degree_start": 253.3333,
        "degree_end": 266.6667,
        "functional_nature": "Fierce / Cruel",
        "functional_nature_tamil": "உக்கிர / தீவிர",
        "gender": "Feminine",
        "result_grade": "OK",
        "ruling_deity": "Apah (Water Goddess / Cosmic Waters)",
        "ruling_planet": "Venus",
        "gaze_direction": "Downward",
        "gaze_direction_tamil": "கீழ்நோக்கு",
        "caste": "Brahmana",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Blind",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 4,
        "symbol_shape": "Elephant's Tusk / Fan / Winnowing Basket",
        "favourable_actions": [
            "Confronting adversaries, battles, assertive campaigns",
            "Maritime travel, building bridges, digging waterways",
            "Distilling medicines, working with liquids and fire",
            "Debates, litigation, unyielding defense of truth",
            "Purification rituals invoking water goddesses"
        ],
        "inauspicious_for": [
            "Timid, passive compromises"
        ],
        "ascendant_indications": (
            "The Undefeated / Unsubdued. Humble, many friends, faithful to spouse, position of high reputation, "
            "acts independently without caring for others' gossip, thrives in public administration."
        ),
        "moon_indications": (
            "Proud, steadfast in friendship and devotion, pleasant marital partner, courageous resilience."
        ),
        "rules_over": [
            "Navigators, fishermen, aquatics, bridge builders",
            "Those living near water, tender-hearted persons",
            "Aquatic flowers, fruits, pearls, maritime trade"
        ],
        "places": ["Harbors, rivers, lakes, canals, water filtration systems"],
        "objects": ["Water vessels, elephant tusks, striking weapons, fire instruments"],
        "abstracts": ["The Undefeated", "Invincible victory", "Sublime water purification"],
        "general_remedy": "Feed the learned brahmanas and offer worship to the sacred rivers / Goddess Lakshmi.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "13°20' - 16°40' Sagittarius (Sun / Leo Navamsa)",
                "traits": "Mild, brave, humble, caters to the needy, income connected with water.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "16°40' - 20°00' Sagittarius (Mercury / Virgo Navamsa)",
                "traits": "Proud, lustrous personality, quick temper, humorous, heavy perspirer.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "20°00' - 23°20' Sagittarius (Venus / Libra Navamsa)",
                "traits": "Clean, learns good qualities from others, pot-belly build.",
                "dosha_status": "Dosha Present",
                "dosha_affects": "Affects parents (specifically mother's longevity/health).",
                "remedy": "Feed the brahmanas and worship Apah / Varuna."
            },
            {
                "pada_number": 4,
                "degree_range": "23°20' - 26°40' Sagittarius (Mars / Scorpio Navamsa)",
                "traits": "Strong, benevolent, truthful, resonant deep voice, opposes rivals, skin sensitivity.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 21,
        "name": "Uttara Ashadha",
        "name_tamil": "உத்திராடம்",
        "alternate_names": ["Uttarashad", "Uttarasadha"],
        "span_zodiac": "Sagittarius 26°40' - Capricorn 10°00'",
        "degree_start": 266.6667,
        "degree_end": 280.0,
        "functional_nature": "Fixed",
        "functional_nature_tamil": "ஸ்திர / நிலையான",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Vishwadevas (Universal Divine Principles)",
        "ruling_planet": "Sun",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Kshatriya",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Weak",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 4,
        "symbol_shape": "Elephant's Tusk / Small Bed / Scaffold",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Marriage (vivaha)",
            "Coronation, assuming civic and government leadership",
            "Laying foundations, erecting lasting public monuments",
            "Planting long-lived trees, digging canals, civic works",
            "Entering into sacred vows and philanthropic missions"
        ],
        "inauspicious_for": [
            "Rapid, fleeting or illicit transactions"
        ],
        "ascendant_indications": (
            "The Universal One. Sincere, kind, excellent counselor, sharp intellect, public servant, "
            "deep reader, achieves lasting fame and widespread respect."
        ),
        "moon_indications": (
            "Well-behaved, numerous true friends, grateful, amiable, righteous, universally admired."
        ),
        "rules_over": [
            "Warriors, wrestlers, men of valour, horse riders",
            "Those devoted to God, upright rulers",
            "Immovable structures, great trees, stone monuments"
        ],
        "places": ["Monuments, civic plazas, governmental council chambers"],
        "objects": ["Dress, iron, stone, elephant gear"],
        "abstracts": ["The Universal One", "Absolute integrity", "Unwavering virtue"],
        "general_remedy": "Nothing required; all padas are exceptionally good and auspicious.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "26°40' Sagittarius - 0°00' Capricorn (Jupiter / Sagittarius Navamsa - Vargottama)",
                "traits": "Wise, broad-minded, charitable, scriptural wisdom, deeply loved by preceptors.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "0°00' - 3°20' Capricorn (Saturn / Capricorn Navamsa - Vargottama)",
                "traits": "Charitable, firm in speech, devoted, strict with unrighteousness, ambitious.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "3°20' - 6°40' Capricorn (Saturn / Aquarius Navamsa)",
                "traits": "Proud, tall and sturdy build, large eyes, formidable presence.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "6°40' - 10°00' Capricorn (Jupiter / Pisces Navamsa)",
                "traits": "Charitable, religious, wealthy, truthful, widely cherished.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 22,
        "name": "Shravana",
        "name_tamil": "திருவோணம்",
        "alternate_names": ["Sravan", "Thiruvonam"],
        "span_zodiac": "Capricorn 10°00' - 23°20'",
        "degree_start": 280.0,
        "degree_end": 293.3333,
        "functional_nature": "Temporary / Movable",
        "functional_nature_tamil": "சர / விரைவு",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Lord Vishnu (Preserver of the Universe) & Goddess Saraswati",
        "ruling_planet": "Moon",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Outcast / Mlechha",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Good",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Ear / Three Footprints (Trivikrama) / Trident",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayana)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Entering new house (griha pravesham)",
            "Taking medicine & undertaking healing courses",
            "Repairing old houses & infrastructure",
            "Listening to sacred oral traditions (Shruti)",
            "Acquiring conveyances, travel, educational enrollment"
        ],
        "inauspicious_for": [
            "Violent warfare, destruction"
        ],
        "ascendant_indications": (
            "Star of Hearing / Cosmic Learning. Lordly character, well-known, spends generously on noble causes, "
            "learned student, lives away from birthplace, does humanitarian and temple work."
        ),
        "moon_indications": (
            "Learned, wealthy, famous, blessed with a generous partner, passionate student of wisdom, eloquent."
        ),
        "rules_over": [
            "Devotees of Lord Vishnu, truth-speakers",
            "The efficient, energetic, righteous, active",
            "Jugglers, performers, communicators"
        ],
        "places": ["Universities, auditoriums, sound studios, temples of Vishnu"],
        "objects": ["Conveyances, audio recorders, sacred scriptures"],
        "abstracts": ["Star of Hearing", "Transcendental sound", "Cosmic preservation"],
        "general_remedy": "None required; all 4 padas are auspicious; worshipping Lord Venkateshwara/Vishnu brings immense prosperity.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "10°00' - 13°20' Capricorn (Mars / Aries Navamsa)",
                "traits": "Tall and sturdy, virtuous, critical of error, enthusiastic.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "13°20' - 16°40' Capricorn (Venus / Taurus Navamsa)",
                "traits": "Passionate, slender, devout, commanding assistants and servants.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "16°40' - 20°00' Capricorn (Mercury / Gemini Navamsa)",
                "traits": "Passionate, astute, business success, managing assets and debts skillfully.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "20°00' - 23°20' Capricorn (Moon / Cancer Navamsa)",
                "traits": "Charitable, religious, owns property and agricultural holdings, sun-burnt complexion.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 23,
        "name": "Dhanishta",
        "name_tamil": "அவிட்டம்",
        "alternate_names": ["Shravistha", "Avittam"],
        "span_zodiac": "Capricorn 23°20' - Aquarius 6°40'",
        "degree_start": 293.3333,
        "degree_end": 306.6667,
        "functional_nature": "Temporary / Movable",
        "functional_nature_tamil": "சர / விரைவு",
        "gender": "Feminine",
        "result_grade": "GOOD",
        "ruling_deity": "Ashta Vasus (The Eight Elemental Demigods)",
        "ruling_planet": "Mars",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Agriculturist / Shudra",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Blind",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 4,
        "symbol_shape": "Mridanga (Drum) / Flute",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Thread ceremony (upanayanam)",
            "Entering new house (griha pravesham)",
            "Taking medicine (aroghyam)",
            "Constructing a house (griha rambham)",
            "Musical performance, orchestra, singing, instrumental music",
            "Buying vehicles and movable machinery"
        ],
        "inauspicious_for": [
            "Giving loans on Saturday (Panchaka considerations)"
        ],
        "ascendant_indications": (
            "Star of Symphony. Unifying others for common causes, heroic nature, royal demeanor, charitable. "
            "Fortunes found away from home, fond of rhythmic music and poetry."
        ),
        "moon_indications": (
            "Liberal in gifts yet shrewd in material acquisition, daring, fond of music and astrology, wealthy."
        ),
        "rules_over": [
            "Men without pride, fast loyal friends",
            "Charitable, peaceful, self-controlled persons",
            "Musicians, drummers, gold merchants"
        ],
        "places": ["Monuments, music auditoriums, rhythmic dancing schools, banks"],
        "objects": ["Mridanga drums, flutes, musical instruments, gold coins"],
        "abstracts": ["Star of Symphony", "Elemental wealth (Vasus)", "Harmonic resonance"],
        "general_remedy": "Nothing required; all padas are good; worshipping Lord Muruga / Ashta Vasus brings renown.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "23°20' - 26°40' Capricorn (Sun / Leo Navamsa)",
                "traits": "Sharp chin, ambitious, passionate, resolute under pressure.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "26°40' Capricorn - 0°00' Aquarius (Mercury / Virgo Navamsa)",
                "traits": "Enthusiastic, truthful, wise, firm mind, skillful debater.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "0°00' - 3°20' Aquarius (Venus / Libra Navamsa)",
                "traits": "Proud, wealthy, well-mannered, fair complexion, takes great care of dependents.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "3°20' - 6°40' Aquarius (Mars / Scorpio Navamsa)",
                "traits": "Hairy body, bold, proud, obstinate, unsparing with rivals.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 24,
        "name": "Shatabhisha",
        "name_tamil": "சதயம்",
        "alternate_names": ["Satabhisa", "Sathayam", "Shatabhishakam"],
        "span_zodiac": "Aquarius 6°40' - 20°00'",
        "degree_start": 306.6667,
        "degree_end": 320.0,
        "functional_nature": "Temporary / Movable",
        "functional_nature_tamil": "சர / விரைவு",
        "gender": "Hermaphrodite / Eunuch",
        "result_grade": "OK",
        "ruling_deity": "Varuna (Cosmic Ocean & Sky God)",
        "ruling_planet": "Rahu",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Spiritual / Outcast",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Weak",
        "luminary_type": "Solar",
        "kula_type": "Kulakul",
        "num_stars": 100,
        "symbol_shape": "Circle / 100 Physicians / Empty Circle",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Constructing new house (griha rambham)",
            "Entering new house (griha pravesham)",
            "Thread ceremony (upanayanam)",
            "Taking medicine & advanced medical therapies (aroghyam)",
            "Horse riding, learning vehicle mechanics",
            "Shaving (cuda karanam / chaulam)",
            "Scientific research, astronomy, nuclear physics, statistics"
        ],
        "inauspicious_for": [
            "Open confession of secrets, simplistic business"
        ],
        "ascendant_indications": (
            "The Veiling Star / Hundred Physicians. Quiet, restricted in self-expression, servitude or analytical positions. "
            "Deeply interested in philosophy, mysticism, or astrology, strategic, educational travels."
        ),
        "moon_indications": (
            "Daring, able to conquer opponents, hard to convince, truthful, unfortunate in minor matters but transcendent."
        ),
        "rules_over": [
            "Aquatic products, fish dealers, ocean navigators",
            "Boar hunters, washer men, distillers, trappers",
            "Physicians, biochemists, astronomers"
        ],
        "places": ["Oceans, chemical labs, radar stations, medical dispensaries"],
        "objects": ["Aquatic silk, hessian, wool, medical elixirs"],
        "abstracts": ["The Hundred Physicians", "Occult gravitation", "Atomic theory", "Statistics"],
        "general_remedy": "Nothing required; worship of Lord Shiva / Varuna brings great peace.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "6°40' - 10°00' Aquarius (Jupiter / Sagittarius Navamsa)",
                "traits": "Happy, wealthy, benevolent, truthful, kind to scholars and animals.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "10°00' - 13°20' Aquarius (Saturn / Capricorn Navamsa)",
                "traits": "Hoarder, misanthropic streak, proud, private.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "13°20' - 16°40' Aquarius (Saturn / Aquarius Navamsa - Vargottama)",
                "traits": "Wealthy, frugal, hungry for knowledge, sensitive heart.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "16°40' - 20°00' Aquarius (Jupiter / Pisces Navamsa)",
                "traits": "Proud, happy, doing good for society, independent views.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 25,
        "name": "Purva Bhadrapada",
        "name_tamil": "பூரட்டாதி",
        "alternate_names": ["Poorvabhadrapad", "Purattadi"],
        "span_zodiac": "Aquarius 20°00' - Pisces 3°20'",
        "degree_start": 320.0,
        "degree_end": 333.3333,
        "functional_nature": "Fierce / Cruel",
        "functional_nature_tamil": "உக்கிர / தீவிர",
        "gender": "Masculine",
        "result_grade": "OK",
        "ruling_deity": "Aja Ekapada (The One-Footed Cosmic Serpent / Rudra)",
        "ruling_planet": "Jupiter",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Brahmana",
        "motivation": "Artha (Material Desires)",
        "sight_quality": "Average",
        "luminary_type": "Lunar",
        "kula_type": "Kul",
        "num_stars": 2,
        "symbol_shape": "Front of Funeral Cot / Two-Faced Man / Sword",
        "favourable_actions": [
            "Demolishing obstacles & crushing adversaries",
            "Handling poison, weapons, fire, and electricity",
            "Hydroelectric power projects, aircraft, ferries, bridges",
            "Penance, atonement for sins, spiritual austerities",
            "Aggressive litigation, single combat, high-risk undertakings"
        ],
        "inauspicious_for": [
            "Peaceful celebrations, gentle domestic ceremonies"
        ],
        "ascendant_indications": (
            "The Burning Pair. High-strung, serious about deep philosophy, unorthodox, intent in work. "
            "Changes residence often, good longevity, repentant for sins, transforms crisis into spiritual illumination."
        ),
        "moon_indications": (
            "Wealthy yet frugal, clever in executing work, intense convictions, philosopher's temperament."
        ),
        "rules_over": [
            "Hydroelectric workers, aviators, ferry operators",
            "Those clever in single combat, fierce competitors",
            "Religious institutions, ascetics of severe vows"
        ],
        "places": ["Religious institutions, hydroelectric dams, bridges, crematoriums"],
        "objects": ["Poison, weapons, airplanes, high-voltage transformers"],
        "abstracts": ["The Burning Pair", "Atonement", "Tapasya (ascetic fire)"],
        "general_remedy": "Feeding the learned brahmanas and invoking their blessings (ashirvadam).",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "20°00' - 23°20' Aquarius (Mars / Aries Navamsa)",
                "traits": "Tall, heavy build, passionate, fighter, intense worrier.",
                "dosha_status": "Good / Neutral",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "23°20' - 26°40' Aquarius (Venus / Taurus Navamsa)",
                "traits": "Receives wealth from government/authorities, liked by opposite sex, material fulfillment.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "26°40' Aquarius - 0°00' Pisces (Mercury / Gemini Navamsa)",
                "traits": "Relaxed, peaceful, jolly, elegantly dressed, honored by society.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "0°00' - 3°20' Pisces (Moon / Cancer Navamsa)",
                "traits": "Humble, frugal, good-looking, long life, occupied with personal projects.",
                "dosha_status": "Minor Dosha",
                "dosha_affects": "Minor dosha involved.",
                "remedy": "Feed the brahmanas and invoke their blessings."
            }
        ]
    },
    {
        "id": 26,
        "name": "Uttara Bhadrapada",
        "name_tamil": "உத்திரட்டாதி",
        "alternate_names": ["Uttarabhadrapad", "Uthirattathi"],
        "span_zodiac": "Pisces 3°20' - 16°40'",
        "degree_start": 333.3333,
        "degree_end": 346.6667,
        "functional_nature": "Fixed",
        "functional_nature_tamil": "ஸ்திர / நிலையான",
        "gender": "Masculine",
        "result_grade": "GOOD",
        "ruling_deity": "Ahirbudhnya (Serpent of the Ocean Depths / Shiva)",
        "ruling_planet": "Saturn",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Kshatriya",
        "motivation": "Kama (Carnal / Elevated Desires)",
        "sight_quality": "Good",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 5,
        "symbol_shape": "Back of Funeral Cot / Pair of Twins / Snake in the Deep",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Entering new house (griha pravesham)",
            "Constructing a house (griha rambham)",
            "Coronation, assuming stewardship",
            "Marriage (vivaha)",
            "Charity, penance, establishing trusts, building monasteries",
            "Work with dairy, milk products, lasting stone structures"
        ],
        "inauspicious_for": [
            "Superficial or hasty activities"
        ],
        "ascendant_indications": (
            "Power to control anger, capacity to elevate consciousness from lower to spiritual plane. "
            "Protector of people (Kshatriya star), happiness from children, interest in occult, eloquent, fond of society."
        ),
        "moon_indications": (
            "Clever speech, happy, virtuous, enjoys life with children, overcomes adversaries, likes to serve."
        ),
        "rules_over": [
            "Sacrifices, charity, penance, ascetics",
            "Monarchs, wealthy philanthropists, recluses",
            "Valuable corn, dairy products, geological engineers"
        ],
        "places": ["Nursing homes, monasteries, geological departments, steel works, religious trusts"],
        "objects": ["Dress, iron, stone, milk products"],
        "abstracts": ["Serpent of the Cosmic Deep", "Mastery over anger", "Spiritual ascent"],
        "general_remedy": "Nothing required; all padas are exceptionally good and auspicious.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "3°20' - 6°40' Pisces (Sun / Leo Navamsa)",
                "traits": "Lustrous, handsome appearance, wealthy, truthful, widely popular.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "6°40' - 10°00' Pisces (Mercury / Virgo Navamsa)",
                "traits": "Slender, gentle qualities, adheres to righteous path, vast knowledge.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "10°00' - 13°20' Pisces (Venus / Libra Navamsa)",
                "traits": "Red-haired, frank, occasionally stubborn, perseverant.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "13°20' - 16°40' Pisces (Mars / Scorpio Navamsa)",
                "traits": "Passionate, broad-minded storyteller, collects assets daily, strong leader.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    },
    {
        "id": 27,
        "name": "Revati",
        "name_tamil": "ரேவதி",
        "alternate_names": ["Revathi"],
        "span_zodiac": "Pisces 16°40' - 30°00'",
        "degree_start": 346.6667,
        "degree_end": 360.0,
        "functional_nature": "Soft / Gentle",
        "functional_nature_tamil": "மிருதுவான / சாந்த",
        "gender": "Masculine",
        "result_grade": "GOOD",
        "ruling_deity": "Pushan (Nourisher and Protector of Travelers & Flocks)",
        "ruling_planet": "Mercury",
        "gaze_direction": "Forward",
        "gaze_direction_tamil": "முன்னோக்கு",
        "caste": "Shudra",
        "motivation": "Moksha (Salvation)",
        "sight_quality": "Blind",
        "luminary_type": "Lunar",
        "kula_type": "Akul",
        "num_stars": 32,
        "symbol_shape": "Fish / Mridanga Drum / Pair of Fish",
        "favourable_actions": [
            "Installing Deity/idol (avahani)",
            "Thread ceremony (upanayanam)",
            "Parting of hair (simontan)",
            "Shaving (cuda karanam)",
            "Entering new house (griha pravesham)",
            "Marriage (vivaha)",
            "Taking medicine (arogyam) & commencing addiction recovery",
            "Legal settlements & ripe judicial agreements",
            "Maritime travel, buying gems, perfumes, dresses"
        ],
        "inauspicious_for": [
            "Aggressive warfare, cruelty"
        ],
        "ascendant_indications": (
            "The Wealthy One. Good longevity, attractive appearance, valiant, proud, self-respecting. "
            "Clean, strong body, sociable, excellent teacher, nourished by divine grace (Pushan)."
        ),
        "moon_indications": (
            "Clean, courageous, well-liked, beautifully formed physique, gentle wisdom, prosperous."
        ),
        "rules_over": [
            "Aquatic products, fruits, flowers, salt, gems, pearls",
            "Conch shells, lotus blossoms, perfumes",
            "Traders, sailors, shepherds, legal authorities"
        ],
        "places": ["Stock markets, chemical plants, legal departments, embassies, universities"],
        "objects": ["Salt, pearls, conch shells, ornaments, gems, perfumes, sound recorders"],
        "abstracts": ["The Wealthy Nourisher", "Safe passage across ocean of life", "Ripe judgement"],
        "general_remedy": "Gift of Gold to the Deity or learned brahmanas (especially for Pada 4 Gandanta).",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "16°40' - 20°00' Pisces (Jupiter / Sagittarius Navamsa)",
                "traits": "Clever, happy, learned, deep thinker, smooth skin.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "20°00' - 23°20' Pisces (Saturn / Capricorn Navamsa)",
                "traits": "Passionate, firm mind, lustrous face, managing debts successfully.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "23°20' - 26°40' Pisces (Saturn / Aquarius Navamsa)",
                "traits": "Open-hearted, unconventional, colorful manners, generous.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "26°40' Pisces - 0°00' Aries (Jupiter / Pisces Navamsa - Gandanta)",
                "traits": "Clean, courageous, truthful, brave, razor-sharp intellect.",
                "dosha_status": "Severe Dosha (Gandanta)",
                "dosha_affects": "Adversely affects the child in early infancy.",
                "remedy": "Gift of Gold to the Deity or learned brahmin; perform Revati Gandanta Shanti."
            }
        ]
    },
    {
        "id": 28,
        "name": "Abhijit",
        "name_tamil": "அபிஜித்",
        "alternate_names": ["Abhijith"],
        "span_zodiac": "Capricorn 6°40' - 10°53'20'' (Intercalary Asterism)",
        "degree_start": 276.6667,
        "degree_end": 280.8889,
        "functional_nature": "Light / Victory (Brahma Asterism)",
        "functional_nature_tamil": "விஜய / பிரம்ம நட்சத்திரம்",
        "gender": "Feminine",
        "result_grade": "OK",
        "ruling_deity": "Brahma (Supreme Creator)",
        "ruling_planet": "Sun",
        "gaze_direction": "Upward",
        "gaze_direction_tamil": "மேல்நோக்கு",
        "caste": "Brahmana",
        "motivation": "Dharma (Spiritual Duty)",
        "sight_quality": "Good",
        "luminary_type": "Solar",
        "kula_type": "Kul",
        "num_stars": 3,
        "symbol_shape": "Victory Arch / Abhijit Muhurta Midday Sun",
        "favourable_actions": [
            "All victory-oriented endeavors (Abhijit = The Victorious)",
            "Commencing sacred rituals during Abhijit Muhurta (midday)",
            "Overcoming any malefic planetary dosha in transit",
            "Inauguration of holy enterprises, coronation, oaths of office"
        ],
        "inauspicious_for": [
            "Southward journeys on Wednesday"
        ],
        "ascendant_indications": (
            "The 28th Intercalary Nakshatra of Supreme Victory. Presided over by Lord Brahma in the highest realm, "
            "endows unyielding righteousness, brilliance, and immunity to conventional astrological blemishes."
        ),
        "moon_indications": (
            "Victorious mind, invincibility in righteous contest, supreme clarity, auspiciousness."
        ),
        "rules_over": [
            "Kings, victorious generals, supreme judges",
            "Highest priests, divine architects",
            "Times of cosmic alignment"
        ],
        "places": ["Supreme courts, royal crowns, central meridian zenith"],
        "objects": ["Crowns of victory, white horses, golden scepters"],
        "abstracts": ["Invincible Victory", "Brahma's Light", "Dispeller of 100,000 doshas"],
        "general_remedy": "None required; invoking Lord Brahma or chanting Gayatri Mantra brings complete victory.",
        "padas": [
            {
                "pada_number": 1,
                "degree_range": "Intercalary 1st Quarter (Capricorn 6°40' - 7°43'20'')",
                "traits": "Victorious, dignified, scholar of the highest truth.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 2,
                "degree_range": "Intercalary 2nd Quarter (Capricorn 7°43'20'' - 8°46'40'')",
                "traits": "Supreme administrator, righteous judge, revered by leaders.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 3,
                "degree_range": "Intercalary 3rd Quarter (Capricorn 8°46'40'' - 9°50'00'')",
                "traits": "Endowed with high knowledge, protective of society, victorious over obstacles.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            },
            {
                "pada_number": 4,
                "degree_range": "Intercalary 4th Quarter (Capricorn 9°50'00'' - 10°53'20'')",
                "traits": "Radiant spiritual illumination, divine grace, lasting glory.",
                "dosha_status": "Good / Auspicious",
                "dosha_affects": None,
                "remedy": None
            }
        ]
    }
]


# Canonical 28 Nakshatras Summary Table as provided in classical source
NAKSHATRAS_SUMMARY_TABLE: List[Dict[str, Any]] = [
    {"num": 1, "name": "ASWINI", "gender": "M", "result": "GOOD", "nature": "GENTLE", "ruled_by": "ASWINIDEVATAS", "direction": "FORWARD"},
    {"num": 2, "name": "BHARANI", "gender": "F", "result": "HARM", "nature": "CRUEL", "ruled_by": "YAMARAJ", "direction": "DOWNWARD"},
    {"num": 3, "name": "KRITTIKA", "gender": "M", "result": "HARM", "nature": "MIXED", "ruled_by": "AGNI", "direction": "DOWNWARD"},
    {"num": 4, "name": "ROHINI", "gender": "M", "result": "GOOD", "nature": "STEADY", "ruled_by": "BRAHMA", "direction": "UPWARD"},
    {"num": 5, "name": "MRGASIRA", "gender": "H", "result": "GOOD", "nature": "EXCELLENT", "ruled_by": "MOON", "direction": "FORWARD"},
    {"num": 6, "name": "ARDRA", "gender": "F", "result": "OK", "nature": "HARSH", "ruled_by": "RUDRA", "direction": "UPWARD"},
    {"num": 7, "name": "PUNARVASU", "gender": "M", "result": "OK", "nature": "MOVABLE", "ruled_by": "ADITI", "direction": "FORWARD"},
    {"num": 8, "name": "PUSYAMI", "gender": "M", "result": "GOOD", "nature": "GENTLE", "ruled_by": "GURU", "direction": "UPWARD"},
    {"num": 9, "name": "ASLESHA", "gender": "F", "result": "MISERY", "nature": "HARSH", "ruled_by": "SARPA (RAHU)", "direction": "DOWNWARD"},
    {"num": 10, "name": "MAGHA", "gender": "F", "result": "GOOD", "nature": "CRUEL", "ruled_by": "PITRS", "direction": "DOWNWARD"},
    {"num": 11, "name": "PURVA.PH.", "gender": "F", "result": "OK", "nature": "CRUEL", "ruled_by": "BHAGA (SIVA)", "direction": "DOWNWARD"},
    {"num": 12, "name": "UTT.PHAL.", "gender": "F", "result": "GOOD", "nature": "STEADY", "ruled_by": "ARYAMAN", "direction": "UPWARD"},
    {"num": 13, "name": "HASTA", "gender": "M", "result": "GOOD", "nature": "GENTLE", "ruled_by": "SAVITR (SUN)", "direction": "FORWARD"},
    {"num": 14, "name": "CHITRA", "gender": "F", "result": "GOOD", "nature": "EXCELLENT", "ruled_by": "TVASTR", "direction": "FORWARD"},
    {"num": 15, "name": "SWATI", "gender": "F", "result": "GOOD", "nature": "MOVABLE", "ruled_by": "VAYU", "direction": "DOWNWARD"},
    {"num": 16, "name": "VISHAKHA", "gender": "F", "result": "OK", "nature": "MIXED", "ruled_by": "INDRA AND AGNI", "direction": "DOWNWARD"},
    {"num": 17, "name": "ANURADHA", "gender": "M", "result": "GOOD", "nature": "EXCELLENT", "ruled_by": "MITRA (SUN)", "direction": "FORWARD"},
    {"num": 18, "name": "JYESTHA", "gender": "F", "result": "OK", "nature": "MIXED", "ruled_by": "SHAKRA (INDRA)", "direction": "FORWARD"},
    {"num": 19, "name": "MULA", "gender": "H", "result": "GOOD", "nature": "CRUEL", "ruled_by": "NIRRTI", "direction": "DOWNWARD"},
    {"num": 20, "name": "P.ASADHA", "gender": "F", "result": "OK", "nature": "CRUEL", "ruled_by": "APAH (WATER)", "direction": "DOWNWARD"},
    {"num": 21, "name": "UTT.ASADHA", "gender": "F", "result": "GOOD", "nature": "STEADY", "ruled_by": "VISVADEVAS", "direction": "UPWARD"},
    {"num": 22, "name": "SRAVAN", "gender": "F", "result": "GOOD", "nature": "MOVABLE", "ruled_by": "VISNU", "direction": "UPWARD"},
    {"num": 23, "name": "DHANISTHA", "gender": "F", "result": "GOOD", "nature": "MOVABLE", "ruled_by": "VASANA (INDRA)", "direction": "UPWARD"},
    {"num": 24, "name": "SATABHISAK", "gender": "H", "result": "OK", "nature": "MOVABLE", "ruled_by": "VARUNA", "direction": "UPWARD"},
    {"num": 25, "name": "P.BHADRA", "gender": "M", "result": "OK", "nature": "CRUEL", "ruled_by": "AJA (BRAHMA)", "direction": "UPWARD"},
    {"num": 26, "name": "UTT.BHADRA", "gender": "M", "result": "GOOD", "nature": "STEADY", "ruled_by": "AHIRBUDHNYA", "direction": "UPWARD"},
    {"num": 27, "name": "REVATI", "gender": "M", "result": "GOOD", "nature": "EXCELLENT", "ruled_by": "PUSAN", "direction": "FORWARD"},
    {"num": 28, "name": "ABHIJIT", "gender": "F", "result": "OK", "nature": "BRAHMA", "ruled_by": "BRAHMA", "direction": "UPWARD"},
]


# Canonical E-Book Treatise & Esoteric Philosophy
EBOOK_TREATISE: Dict[str, Any] = {
    "title": "28 Nakshatras - The Real Secrets of Vedic Astrology (An e-book)",
    "title_tamil": "28 நட்சத்திரங்கள் - வேத ஜோதிடத்தின் உண்மை ரகசியங்கள் (மின்னூல்)",
    "subtitle": "Unlocking the 27 Lunar Mansions and the 28th Intercalary Star Abhijit",
    "subtitle_tamil": "27 சந்திர நட்சத்திரங்கள் மற்றும் 28-வது அபிஜித் நட்சத்திரத்தின் மூல ரகசியங்கள்",
    "author_tradition": "Classical Vedic Rishis, Kalaprakashika, B.V. Raman, Rama Krishna Bhatt & Master Deepak",
    "chapters": [
        {
            "id": "celestial_influences",
            "number": 1,
            "title_en": "The Key to Celestial Influences: 27 Constellations vs 12 Zodiac Signs",
            "title_ta": "விண்வெளி ஆற்றலின் திறவுகோல்: 12 ராசிகளை விட 27 நட்சத்திரங்களே முதன்மையானவை",
            "content_en": (
                "In the Vedic (Hindu) system of Astrology, known in Sanskrit as Jyotish, the 27 constellations and not the 12 "
                "star-signs are the master key to understanding celestial influences on our planet. These 27 constellations are "
                "known as the 27 Nakshatras, which reside 300 to 400 light years away from earth. Based on a person's moon "
                "Nakshatra at the time of birth, Jyotish offers the most powerful, penetrating predictive technique compared to all "
                "other astrological systems worldwide."
            ),
            "content_ta": (
                "சமஸ்கிருதத்தில் 'ஜோதிஷம்' எனப்படும் வேத ஜோதிட முறையில், பூமி மீது ஏற்படும் பிரபஞ்ச கதிர்வீச்சு தாக்கங்களை உணர்வதற்கு "
                "12 ராசிகளை விட 27 விண்மீன் மண்டலங்களே (நட்சத்திரங்கள்) தலையாய திறவுகோலாகும். பூமியிலிருந்து 300 முதல் 400 ஒளி ஆண்டுகள் "
                "தொலைவில் அமைந்துள்ள இந்த 27 நட்சத்திரங்கள், ஒரு மனிதன் பிறக்கும் போது சந்திரன் சஞ்சரிக்கும் நட்சத்திரத்தின் அடிப்படையில் "
                "உலகிலேயே மிகத் துல்லியமான எதிர்கால பலன்களை கணிக்க வழிவகுக்கின்றன."
            ),
            "key_takeaway": "The 27 Nakshatras are 300-400 light years distant and hold deeper karmic vibrations than the 12 solar signs."
        },
        {
            "id": "etymology_sky_map",
            "number": 2,
            "title_en": "Etymology: The True Meaning of 'Sky Map' and 'Star Map'",
            "title_ta": "சொல்லிலக்கணம்: 'வான வரைபடம்' மற்றும் 'நட்சத்திர வரைபடம்'",
            "content_en": (
                "The term 'Nakshatra' reveals its profound scientific purpose when broken down into its constituent Sanskrit roots. "
                "Under one dissection, 'naks' means 'sky' and 'shetra' means 'region', translating directly into 'Sky Map'. Under an "
                "alternate classical dissection, 'naksha' is 'map' and 'tara' is 'star', rendering Nakshatra as 'Star Map'. Both etymological "
                "derivations unequivocally establish that in the eyes of the ancient Vedic seers, the 27 Nakshatras—and not the 12 signs—are "
                "the true cosmic grid that maps the sky."
            ),
            "content_ta": (
                "'நட்சத்திரம்' என்ற சொல் அதன் சமஸ்கிருத வேர்ச்சொற்களை ஆராயும் போது வியத்தகு உண்மையை வெளிப்படுத்துகிறது. 'நக்ஸ்' என்றால் 'வானம்', "
                "'சேத்திரம்' என்றால் 'பிரதேசம்'—இதன் பொருள் 'வான வரைபடம்' (Sky Map). மற்றுமொரு பிரிவின்படி, 'நக்ஷா' என்றால் 'வரைபடம்', 'தாரா' "
                "என்றால் 'விண்மீன்'—ஆக நட்சத்திரம் என்பது 'விண்மீன் வரைபடம்' (Star Map). இவ்விரு விளக்கங்களும் பண்டைய வேத ரிஷிகளின் பார்வையில் "
                "வானத்தை துல்லியமாக அளவிடும் வரைபடமாக 12 ராசிகள் அல்ல, 27 நட்சத்திர மண்டலங்களே திகழ்ந்தன என்பதை நிரூபிக்கின்றன."
            ),
            "key_takeaway": "Nakshatra literally translates to 'Sky Map' (Naks-Shetra) and 'Star Map' (Naksha-Tara)."
        },
        {
            "id": "lunar_mansions",
            "number": 3,
            "title_en": "The Moon as the Ancient Cosmic Clock & 5,000+ Years Vedic Antiquity",
            "title_ta": "பண்டைய காலக் கணிப்பொறியாக சந்திரன் & 5000 ஆண்டு வேதத் தொன்மை",
            "content_en": (
                "It was the Moon that ancient seers first looked to for calculating time and connecting to the stars. 'Nakshatras' is the "
                "name given to the constellations or mansions of the Moon, as the Moon resides in each of these constellations for "
                "approximately one solar day. This constellation architecture is exceedingly ancient, dating back more than 5,000 years, "
                "as explicitly documented in the Rigveda and oldest Vedic scriptures. These 28 lunar mansions also appear in ancient "
                "Chinese and Arabic traditions, yet have been largely neglected by modern Western astrology."
            ),
            "content_ta": (
                "பண்டைய மக்கள் காலத்தைக் கணக்கிடவும் விண்மீன்களை அறியவும் முதலில் சந்திரனையே கவனித்தனர். சந்திரன் ஒவ்வொரு விண்மீன் மண்டலத்திலும் "
                "ஒரு நாள் தங்குவதால், இவை 'சந்திரனின் தங்குமிடங்கள்' (Lunar Mansions) என அழைக்கப்பெற்றன. ரிக் வேதம் உள்ளிட்ட அதிபுராதன வேத நூல்களில் "
                "குறிப்பிடப்பட்டுள்ள இந்த அமைப்பு 5,000 ஆண்டுகளுக்கும் மேலான தொன்மை வாய்ந்தது. சீன மற்றும் அரபு ஜோதிடங்களிலும் இந்த சந்திர "
                "மண்டலங்கள் பயன்படுத்தப்பட்ட போதிலும், மேலைநாட்டு ஜோதிடத்தில் இது கவனிக்கப்படாமல் போனது."
            ),
            "key_takeaway": "The Moon stays in one Nakshatra per day, forming the foundational 5,000-year-old Vedic lunar calendar."
        },
        {
            "id": "mathematical_matrix",
            "number": 4,
            "title_en": "Mathematical Architecture: 13°20' Divisions Composing the 360° Zodiac",
            "title_ta": "கணிதக் கட்டமைப்பு: 13°20' கொண்ட 27 பகுதிகள் அமைக்கும் 360° காலச்சக்கரம்",
            "content_en": (
                "Each of the 27 Nakshatras spans precisely 13 degrees and 20 minutes of celestial longitude (800 arcminutes). Multiplying "
                "13°20' by 27 equals exactly 360°00', encompassing the complete ecliptic circle. Each Nakshatra is further subdivided into "
                "four quarters known as Padas (3°20' each), totaling 108 Padas in the zodiac—the sacred Vedic number that harmonizes the "
                "9 planets with the 12 rashis (9 × 12 = 108)."
            ),
            "content_ta": (
                "ஒவ்வொரு நட்சத்திரமும் வான மண்டலத்தில் சரியாக 13 பாகை 20 கலை (13°20' = 800 கலைகள்) நீளத்தைக் கொண்டுள்ளது. 13°20' என்பதை 27 ஆல் "
                "பெருக்கினால் மொத்த ராசி மண்டலத்தின் 360° துல்லியமாக கிடைக்கிறது. மேலும் ஒவ்வொரு நட்சத்திரமும் 4 பாதங்களாக (3°20' வீதம்) "
                "பிரிக்கப்பட்டு, மொத்த காலச்சக்கரத்தில் 108 பாதங்கள் அமைகின்றன. இது 9 கிரகங்கள் மற்றும் 12 ராசிகளை இணைக்கும் புனித 108 கணித "
                "சூத்திரமாகும் (9 × 12 = 108)."
            ),
            "key_takeaway": "Each Nakshatra spans 13°20'; subdivided into 4 Padas of 3°20' each, yielding the sacred 108 Navamsa quarters."
        },
        {
            "id": "four_purusharthas",
            "number": 5,
            "title_en": "The Four Purusharthas: Classification by Primary Soul Motivation",
            "title_ta": "நான்கு புருஷார்த்தங்கள்: ஆன்மாவின் முதன்மை உந்துதல்கள்",
            "content_en": (
                "The Nakshatras are systematically classified according to the four primary Vedic soul motivations (Purusharthas): "
                "Dharma (righteous duty, living on spiritual principles), Artha (material prosperity, acquisition of wealth), "
                "Kama (sensual pleasures, artistic beauty, emotional desire), and Moksha (spiritual liberation from the cycle of birth and death). "
                "They are also categorized by gender, caste (Brahmana, Kshatriya, Vaishya, Shudra, and Outcast), species (Yoni), and presiding deities."
            ),
            "content_ta": (
                "நட்சத்திரங்கள் நான்கு புருஷார்த்தங்களின்படி வகைப்படுத்தப்பட்டுள்ளன: தர்மம் (ஆன்மீக நெறிமுறை), அர்த்தம் (பொருளாதார வளர்ச்சி), "
                "காமம் (கலை, இன்பம் மற்றும் ஆசைகள்), மற்றும் மோட்சம் (பிறவிப் பெருங்கடலிலிருந்து விடுதலை). மேலும் இவை பாலினம், வர்ணம், யோனி "
                "மற்றும் ஆளும் தெய்வங்களின் அடிப்படையில் மிக நுணுக்கமாக பிரிக்கப்பட்டுள்ளன."
            ),
            "key_takeaway": "The Nakshatras align human life directly with the four eternal goals: Dharma, Artha, Kama, and Moksha."
        },
        {
            "id": "signs_vs_nakshatras",
            "number": 6,
            "title_en": "Signs vs. Nakshatras: The Cosmic Essence vs. The Mere 'Heap'",
            "title_ta": "ராசிகள் vs நட்சத்திரங்கள்: ஆழமான கதிர்வீச்சு vs வெறும் 'குவியல்'",
            "content_en": (
                "Both the zodiac signs and the Nakshatras begin at the identical celestial coordinate: 0°00' Aries begins simultaneously with "
                "the first Nakshatra, Ashwini. However, each zodiac sign merely contains the blended composite of the Nakshatras falling "
                "within it. The Sanskrit word for sign, 'Rashi', literally translates to 'a heap, mass, or collection' of influences. "
                "Compared to the superficial signs, the Nakshatras possess a far deeper, concentrated vibratory effect that touches the soul's causal body."
            ),
            "content_ta": (
                "ராசி மண்டலமும் நட்சத்திர மண்டலமும் ஒரே புள்ளியில் தொடங்குகின்றன: மேஷ ராசியின் 0° தொடக்கமே அஸ்வினி நட்சத்திரத்தின் தொடக்கமாகும். "
                "ஆனால் ராசி என்பது அதற்குள் விழும் நட்சத்திரக் கதிர்களின் கூட்டுச் சேர்க்கையே தவிர வேறில்லை. சமஸ்கிருதத்தில் 'ராசி' என்றால் 'குவியல்' "
                "(ஒருங்கிணைந்த தொகுதி) என்று பொருள். எனவே ராசிகளை விட நட்சத்திரங்களே மனிதனின் ஆன்ம ஆழத்தில் ஊடுருவி பலன் தரும் மூல சக்தியாகும்."
            ),
            "key_takeaway": "Rashi literally means 'heap'; Nakshatras are the foundational building blocks of all zodiac signs."
        },
        {
            "id": "cosmic_cross",
            "number": 7,
            "title_en": "The Cosmic Cross of Creation: Prakriti & Purusha",
            "title_ta": "பிரபஞ்ச சிருஷ்டியின் சிலுவை: பிரகிருதி மற்றும் புருஷன்",
            "content_en": (
                "Prakriti (the primordial female creative impulse) sustains the general matrix of the zodiac, generating the fertile "
                "conditions in which the cosmic seeds sprinkled by Purusha (the male divine consciousness factor) fructify and grow. "
                "The Nakshatras and zodiac signs represent the passive, receptive creative potency—the horizontal arm of creation. "
                "The planets are the positive, generating, active forces—the vertical arm. In the cross of cosmic creation, the Nakshatras "
                "provide the material womb, while the planets act as the precipitating catalyst."
            ),
            "content_ta": (
                "பிரகிருதி (பெண் படைப்பு ஆற்றல்) பிரபஞ்சத்தின் அடித்தளத்தை நிலைநிறுத்துகிறது; இதில் புருஷன் (ஆண் விழிப்புணர்வு காரணி) தெளிக்கும் "
                "விதை முளைத்து வளர்கிறது. நட்சத்திரங்களும் ராசிகளும் உள்வாங்கும் சக்தி கொண்டவை—இவை படைப்பின் கிடைமட்டக் கையாகும் (Horizontal Arm). "
                "கிரகங்கள் நேர்மறை இயக்க ஆற்றல்கள்—இவை படைப்பின் செங்குத்துக் கையாகும் (Vertical Arm). இவ்விரு தத்துவங்களின் சங்கமமே பிரபஞ்ச சிருஷ்டி."
            ),
            "key_takeaway": "Nakshatras constitute the receptive horizontal matrix (Prakriti), while Planets are the active precipitating forces (Purusha)."
        },
        {
            "id": "storehouse_of_karma",
            "number": 8,
            "title_en": "The Abodes of Karma: The True Repository of Spiritual Labor",
            "title_ta": "கர்மக் கருவூலம்: தவம் மற்றும் ஆன்மீக உழைப்பின் சேமிப்பு கிடங்கு",
            "content_en": (
                "Ancient Indian seers declared that the Nakshatras represent the celestial abodes into which the fruits of our labor "
                "(our Karma) are transferred and preserved across lifetimes. The Nakshatras faithfully dispense the fruits of past actions, "
                "the highest and most protected of which are the fruits of worship, meditation, and spiritual labor. Hence in Vedic "
                "astrology, human personality and destiny are read primarily through the Moon Nakshatra (Janma Tara) rather than the solar sign."
            ),
            "content_ta": (
                "நாம் செய்யும் கர்ம வினைகளின் பலன்கள் சேமிக்கப்பட்டு வைக்கப்படும் தேவக் கருவூலங்களே நட்சத்திரங்கள் என்று முனிவர்கள் உரைத்தனர். "
                "முற்பிறவி கர்ம பலன்களை, குறிப்பாக நாம் செய்த தியானம், வழிபாடு மற்றும் ஆன்மீக உழைப்பின் மேலான பலன்களை நட்சத்திரங்களே உரிய காலத்தில் "
                "வழங்குகின்றன. எனவே தான் சூரிய ராசியை விட, சந்திரன் நின்ற நட்சத்திரத்தை (ஜென்ம தாரை) வைத்தே வேத ஜோதிடம் முழு வாழ்வையும் கணிக்கிறது."
            ),
            "key_takeaway": "Nakshatras store and dispense lifetime Karma, especially the fruits of meditation and spiritual devotion."
        },
        {
            "id": "vimshottari_dasha",
            "number": 9,
            "title_en": "The 120-Year Vimshottari Dasha Predictive System",
            "title_ta": "120 ஆண்டுகால விம்சோத்தரி தசா காலக் கணிப்பு முறை",
            "content_en": (
                "Vedic astrology employs the unmatched planetary period system called Dasha, anchored directly to the exact degree of the Moon "
                "in its birth Nakshatra. Foremost among these is the Vimshottari Dasha, a 120-year cycle comprising the nine Grahas "
                "(Sun 6y, Moon 10y, Mars 7y, Rahu 18y, Jupiter 16y, Saturn 19y, Mercury 17y, Ketu 7y, and Venus 20y). This deterministic "
                "timing framework allows Vedic astrologers to time life events with an accuracy unachievable in other traditions."
            ),
            "content_ta": (
                "பிறக்கும் போது சந்திரன் நின்ற நட்சத்திர பாதத்தின் அடிப்படையிலேயே 120 ஆண்டுகால விம்சோத்தரி தசா இருப்பு கணக்கிடப்படுகிறது. "
                "சூரியன் (6), சந்திரன் (10), செவ்வாய் (7), ராகு (18), குரு (16), சனி (19), புதன் (17), கேது (7), சுக்கிரன் (20) என ஒன்பது கிரகங்களுக்கும் "
                "பகிரப்படும் இக்காலக் கட்டமே வாழ்வின் திருப்பங்களை முன்கூட்டியே துல்லியமாக அறிய உதவும் தனித்துவமான வேத ஜோதிட பொக்கிஷமாகும்."
            ),
            "key_takeaway": "Vimshottari Dasha maps 120 years of planetary unfolding using the exact Moon Nakshatra degree at birth."
        },
        {
            "id": "constellational_transits",
            "number": 10,
            "title_en": "Constellational Transits & Electional (Muhurta) Science",
            "title_ta": "கோச்சார சஞ்சாரங்கள் & முகூர்த்த தேர்தல் ஜோதிட சாஸ்திரம்",
            "content_en": (
                "Whatever activity we initiate at a particular moment retains an indelible resonance with the energetic environment of that "
                "place and time. Because every moment possesses its own unique potency, inaugurating enterprises under an auspicious transit "
                "ensures longevity and success. In electional astrology (Muhurta), placing the Moon in a sympathetic constellation relative "
                "to one's Janma Tara (Birth Star) and the nature of the undertaking is paramount."
            ),
            "content_ta": (
                "ஒரு குறிப்பிட்ட முகூர்த்த வேளையில் தொடங்கப்படும் எந்தவொரு காரியமும், அந்த கணத்தின் பிரபஞ்ச ஆற்றலை தன் வாழ்நாள் முழுவதும் சுமந்து நிற்கும். "
                "எனவே தான் தொடங்கும் காரியம் வெற்றியடையவும் நிலைத்து நிற்கவும், சந்திரனின் கோச்சார சஞ்சாரத்தை ஆராய்ந்து சுப முகூர்த்தம் தேர்வு செய்வது "
                "முக்கியமானது. ஒருவரின் ஜென்ம நட்சத்திரத்திற்கு அனுகூலமான தாரை பலம் உள்ள நாளில் காரியங்களைத் தொடங்குவது சுப சித்தியை தரும்."
            ),
            "key_takeaway": "Every venture initiated absorbs the cosmic quality of that exact moment; Muhurta aligns with sympathetic Nakshatras."
        },
        {
            "id": "functional_transit_natures",
            "number": 11,
            "title_en": "The Seven Functional Transit Natures (Sthira, Mridu, Laghu, Tikshna, Chara, Ugra, Mishra)",
            "title_ta": "ஏழு இயற்கை பிரிவுகள் (ஸ்திர, மிருது, லகு, தீட்சண, சர, உக்கிர, மிஸ்ர நட்சத்திரங்கள்)",
            "content_en": (
                "The 27 Nakshatras are grouped into 7 functional transit categories that dictate what enterprises will thrive under their sway:\n"
                "1. FIXED (Sthira/Steady): Rohini, Uttaraphalguni, Uttarashadha, Uttarabhadrapada — for laying foundations, digging wells, building temples, coronations, and permanent contracts.\n"
                "2. SOFT (Mridu/Gentle): Mrigashira, Chitra, Anuradha, Revati — for fine arts, music, dance, marriage, wearing apparel, and festivities.\n"
                "3. LIGHT (Laghu/Swift): Ashwini, Pushya, Hasta — for sports, medicine, starting industries, journeys, craftsmanship, loans, and education.\n"
                "4. DREADFUL (Tikshna/Sharp): Ardra, Ashlesha, Jyeshtha, Mula — for warfare, surgery, breaking alliances, and overcoming powerful opponents.\n"
                "5. MOVABLE (Chara/Temporary): Punarvasu, Swati, Shravana, Dhanishta, Shatabhisha — for travel, conveyances, gardening, and short-term ventures.\n"
                "6. FIERCE (Ugra/Cruel): Bharani, Magha, Purvaphalguni, Purvashadha, Purvabhadrapada — for conflict, demolition, weapons, fire, and decisive combat.\n"
                "7. MIXED (Mishra/Routine): Krittika, Vishakha — for daily professional obligations, technical duties, and routine affairs."
            ),
            "content_ta": (
                "27 நட்சத்திரங்களும் 7 செயல்பாட்டு பிரிவுகளாக பிரிக்கப்பட்டு காரிய சித்திக்கான வழிகாட்டிகளாக விளங்குகின்றன:\n"
                "1. ஸ்திர (நிலையானவை): ரோகிணி, உத்திரம், உத்திராடம், உத்திரட்டாதி — அடிக்கல் நாட்ட, கிணறு வெட்ட, ஆலயம் அமைக்க, நிரந்தர பணிகளுக்கு.\n"
                "2. மிருது (சாந்தமானவை): மிருகசீரிஷம், சித்திரை, அனுஷம், ரேவதி — கலைகள், சங்கீதம், திருமணம், புத்தாடை அணிய, சுப விழாக்கள்.\n"
                "3. லகு (சுறுசுறுப்பானவை): அஸ்வினி, பூசம், ஹஸ்தம் — விளையாட்டு, மருத்துவம், தொழில் தொடக்கம், கல்வி, பிரயாணம்.\n"
                "4. தீட்சண (கடுமையானவை): திருவாதிரை, ஆயில்யம், கேட்டை, மூலம் — சத்திர சிகிச்சை, வழக்கு, எதிர்ப்புகளை முறியடிக்கும் சாகசம்.\n"
                "5. சர (இயங்கக்கூடியவை): புனர்பூசம், சுவாதி, திருவோணம், அவிட்டம், சதயம் — வாகனங்கள் வாங்க, பயணம், தற்காலிக காரியங்கள்.\n"
                "6. உக்கிர (மூர்க்கமானவை): பரணி, மகம், பூரம், பூராடம், பூரட்டாதி — எதிரிகளை வெல்ல, நெருப்பு, ஆயுதப் பிரயோகம், கடும் சண்டைகள்.\n"
                "7. மிஸ்ர (கலப்பு): கார்த்திகை, விசாகம் — அன்றாட கடமைகள், அலுவலகப் பணிகள் மற்றும் வழக்கமான தொழில் நிர்வாகம்."
            ),
            "key_takeaway": "7 functional natures govern what enterprise will succeed under which celestial transit."
        },
        {
            "id": "intercalary_abhijit",
            "number": 12,
            "title_en": "The 28th Asterism: Abhijit (The Victorious Brahma Asterism)",
            "title_ta": "28-வது அபிஜித் நட்சத்திரம்: பிரம்மனின் அருள் பெற்ற விஜய நட்சத்திரம்",
            "content_en": (
                "In classical Vedic astronomy, the 28th intercalary asterism Abhijit spans Capricorn 6°40' to 10°53'20'' (nested between "
                "Uttara Ashadha and Shravana). Presided over by Lord Brahma, Abhijit translates directly to 'The Victorious One'. "
                "Celebrated as the cosmic dispeller of 100,000 astrological doshas, the daily midday Abhijit Muhurta is honored across "
                "all classical treatises as a supreme celestial window that overcomes malefic transit afflictions and grants absolute victory."
            ),
            "content_ta": (
                "வேத கால வானியலில், உத்திராடம் மற்றும் திருவோண நட்சத்திரங்களுக்கு இடையில் மகர ராசியில் 6°40' முதல் 10°53'20'' வரை அமைந்துள்ள "
                "28-வது இடைச்செருகல் நட்சத்திரமே அபிஜித் ஆகும். பிரம்ம தேவனால் ஆளப்படும் இந்நட்சத்திரம் 'வெற்றியைத் தருபவர்' என்று பொருள்படும். "
                "தினசரி நண்பகல் வேளையில் வரும் 'அபிஜித் முகூர்த்தம்' ஒரு லட்சம் ஜோதிட தோஷங்களை அழிக்கும் அதியற்புத வரப்பிரசாதமாக சாஸ்திரங்களில் போற்றப்படுகிறது."
            ),
            "key_takeaway": "Abhijit is the 28th asterism of Lord Brahma, revered for dispelling 100,000 doshas and assuring victory."
        }
    ]
}

