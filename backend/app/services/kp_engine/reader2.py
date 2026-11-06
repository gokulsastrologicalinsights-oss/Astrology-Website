"""Krishnamurti Paddhati (KP) Reader 2: Fundamental Principles of Astrology.

Codified directly from Prof. K. S. Krishnamurti's monumental work:
'KP Reader II: Fundamental Principles of Astrology (Hindu - Western & Stellar)'.

Contains:
1. 13-fold classification of the twelve Zodiac signs.
2. Complete significations for all 12 signs (Aries through Pisces).
3. Complete significations for all 12 Bhavas/Houses.
4. Complete significations for planets (Sun through Ketu, Uranus, Neptune, Fortuna).
5. Foundational astrological evaluators:
   - Astrologer proficiency combinations (Chapter 14)
   - Speech defect indications (Mute signs & afflicted Mercury)
   - Childbearing / fertility promise (Fruitful vs Barren signs)
   - Karma classification (Dhruda, Dhruda-Adhruda, Adhruda)
   - Pars Fortunae (Fortuna) calculation and transit signification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# 1. 13-FOLD CLASSIFICATION OF THE TWELVE SIGNS (Chapter 15)
# ---------------------------------------------------------------------------

#: Positive (Masculine / Day) and Negative (Feminine / Night)
POSITIVE_SIGNS: Tuple[str, ...] = (
    "Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius",
)
NEGATIVE_SIGNS: Tuple[str, ...] = (
    "Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces",
)

#: Northern and Southern signs (Celestial Equator boundary)
NORTHERN_SIGNS: Tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
)
SOUTHERN_SIGNS: Tuple[str, ...] = (
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

#: Equinoctial and Tropical signs
EQUINOCTIAL_SIGNS: Tuple[str, ...] = ("Aries", "Libra")
TROPICAL_SIGNS: Tuple[str, ...] = ("Cancer", "Capricorn")

#: Four Elements (Quadruplicities / Tatvas)
FIERY_SIGNS: Tuple[str, ...] = ("Aries", "Leo", "Sagittarius")
EARTHY_SIGNS: Tuple[str, ...] = ("Taurus", "Virgo", "Capricorn")
AIRY_SIGNS: Tuple[str, ...] = ("Gemini", "Libra", "Aquarius")
WATERY_SIGNS: Tuple[str, ...] = ("Cancer", "Scorpio", "Pisces")

#: Mobility / Qualities (Triplicities & Gunas)
MOVABLE_SIGNS: Tuple[str, ...] = ("Aries", "Cancer", "Libra", "Capricorn")  # Rajas
FIXED_SIGNS: Tuple[str, ...] = ("Taurus", "Leo", "Scorpio", "Aquarius")     # Tamas
COMMON_SIGNS: Tuple[str, ...] = ("Gemini", "Virgo", "Sagittarius", "Pisces")  # Sattva (Dual / Mutable)

#: Fertility / Progeny capacity
FRUITFUL_SIGNS: Tuple[str, ...] = ("Cancer", "Scorpio", "Pisces")
SEMI_FRUITFUL_SIGNS: Tuple[str, ...] = ("Taurus", "Libra", "Sagittarius", "Capricorn")
BARREN_SIGNS: Tuple[str, ...] = ("Aries", "Gemini", "Leo", "Virgo")

#: Speech & Voice characteristics
MUTE_SIGNS: Tuple[str, ...] = ("Cancer", "Scorpio", "Pisces")
VOICE_SIGNS: Tuple[str, ...] = ("Gemini", "Libra", "Aquarius")  # Airy medium

#: Violent signs (courage, daring, combative)
VIOLENT_SIGNS: Tuple[str, ...] = ("Aries", "Scorpio")

#: Human / Humane vs Bestial / Four-legged signs
HUMAN_SIGNS: Tuple[str, ...] = ("Gemini", "Virgo", "Libra", "Aquarius", "Sagittarius")  # 1st half Dhanus
BESTIAL_SIGNS: Tuple[str, ...] = ("Aries", "Taurus", "Leo", "Capricorn", "Sagittarius")  # 2nd half Dhanus

#: Dual and Bicorporal (Double-bodied) signs
DUAL_SIGNS: Tuple[str, ...] = ("Gemini", "Sagittarius", "Pisces")
BICORPORAL_SIGNS: Tuple[str, ...] = ("Gemini", "Sagittarius", "Pisces")

#: Ascension speed (Northern Hemisphere; reversed in Southern Hemisphere)
SHORT_ASCENSION_SIGNS_NORTH: Tuple[str, ...] = (
    "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini",
)
LONG_ASCENSION_SIGNS_NORTH: Tuple[str, ...] = (
    "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
)


@dataclass(frozen=True)
class SignClassification:
    """Complete 13-dimension classification of a Zodiac sign according to Reader 2."""
    sign: str
    polarity: str           # "Positive" or "Negative"
    gender: str             # "Masculine" or "Feminine"
    hemisphere: str         # "Northern" or "Southern"
    cardinality_type: str   # "Equinoctial", "Tropical", or "General"
    element: str            # "Fiery", "Earthy", "Airy", or "Watery"
    mobility: str           # "Movable", "Fixed", or "Common"
    guna: str               # "Rajas", "Tamas", or "Sattva"
    fertility: str          # "Fruitful", "Semi-fruitful", or "Barren"
    speech_type: str        # "Mute", "Voice/Musical", or "Moderate"
    is_violent: bool
    is_human: bool
    is_bestial: bool
    is_dual: bool
    is_bicorporal: bool
    ascension_north: str    # "Short" or "Long"
    ascension_south: str    # "Short" or "Long"


def classify_sign(sign: str) -> SignClassification:
    """Return the structured 13-fold classification for any Zodiac sign name."""
    s = sign.strip().title()
    polarity = "Positive" if s in POSITIVE_SIGNS else "Negative"
    gender = "Masculine" if s in POSITIVE_SIGNS else "Feminine"
    hemi = "Northern" if s in NORTHERN_SIGNS else "Southern"
    
    if s in EQUINOCTIAL_SIGNS:
        card = "Equinoctial"
    elif s in TROPICAL_SIGNS:
        card = "Tropical"
    else:
        card = "General"

    if s in FIERY_SIGNS:
        elem = "Fiery"
    elif s in EARTHY_SIGNS:
        elem = "Earthy"
    elif s in AIRY_SIGNS:
        elem = "Airy"
    else:
        elem = "Watery"

    if s in MOVABLE_SIGNS:
        mob, guna = "Movable", "Rajas"
    elif s in FIXED_SIGNS:
        mob, guna = "Fixed", "Tamas"
    else:
        mob, guna = "Common", "Sattva"

    if s in FRUITFUL_SIGNS:
        fert = "Fruitful"
    elif s in BARREN_SIGNS:
        fert = "Barren"
    else:
        fert = "Semi-fruitful"

    if s in MUTE_SIGNS:
        speech = "Mute"
    elif s in VOICE_SIGNS:
        speech = "Voice/Musical"
    else:
        speech = "Moderate"

    asc_n = "Short" if s in SHORT_ASCENSION_SIGNS_NORTH else "Long"
    asc_s = "Long" if asc_n == "Short" else "Short"

    return SignClassification(
        sign=s,
        polarity=polarity,
        gender=gender,
        hemisphere=hemi,
        cardinality_type=card,
        element=elem,
        mobility=mob,
        guna=guna,
        fertility=fert,
        speech_type=speech,
        is_violent=(s in VIOLENT_SIGNS),
        is_human=(s in HUMAN_SIGNS),
        is_bestial=(s in BESTIAL_SIGNS),
        is_dual=(s in DUAL_SIGNS),
        is_bicorporal=(s in BICORPORAL_SIGNS),
        ascension_north=asc_n,
        ascension_south=asc_s,
    )


# ---------------------------------------------------------------------------
# 2. SIGN SIGNIFICATIONS (Chapter 16 - Aries through Pisces)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SignSignification:
    """Detailed astrological and mundane significations of a sign from KP Reader 2."""
    sign_name: str
    sanskrit_name: str
    symbol: str
    start_degree: float
    end_degree: float
    ruling_planet: str
    exaltation_planet: Optional[str]
    debilitation_planet: Optional[str]
    detriment_planet: Optional[str]
    constellations_included: List[str]
    physical_appearance: str
    mental_tendencies: str
    characteristics: str
    health_and_diseases: List[str]
    body_parts: List[str]
    finance_and_fortune: str
    romance_and_marriage: str
    ideal_partner_signs: List[str]
    domestic_environments: str
    professions: List[str]
    places: List[str]
    direction: str
    products: List[str]
    countries_and_cities: List[str]
    handwriting: str
    lucky_days: List[str]
    lucky_numbers: List[int]
    lucky_stones: List[str]
    lucky_colors: List[str]


SIGN_SIGNIFICATIONS: Dict[str, SignSignification] = {
    "Aries": SignSignification(
        sign_name="Aries",
        sanskrit_name="Mesha",
        symbol="Ram",
        start_degree=0.0,
        end_degree=30.0,
        ruling_planet="Mars",
        exaltation_planet="Sun",
        debilitation_planet="Saturn",
        detriment_planet="Venus",
        constellations_included=["Ashwini (1-4)", "Bharani (1-4)", "Krittika (Pada 1)"],
        physical_appearance="Middle stature, lean and muscular body, neither stout nor thick; ruddy complexion; fairly long neck and face; broad temples, narrow chin; bushy eyebrows, sharp eyesight; wiry dark to sandy hair.",
        mental_tendencies="Ever active, ambitious, bold, impulsive, highly confident, courageous, independent, hates subordination and seeks to be at the head of all affairs.",
        characteristics="Enterprising, quick to act with executive force; creates opportunities rather than waiting; frank, open, generous; if afflicted: rash, quarrelsome, over-optimistic, egoistic.",
        health_and_diseases=[
            "Headaches", "Burns", "Neuralgia", "High fever", "Colic pains",
            "Insomnia", "Apoplexy", "Migraine", "Brain inflammatory affections",
        ],
        body_parts=["Head", "Brain", "Face", "Skull bones", "Carotid arteries"],
        finance_and_fortune="Desire to earn much and spend lavishly; impulsive purchases and rash investments; tends not to balance budget without conscious planning; needs to think before acting.",
        romance_and_marriage="Extremely frank, ardent, and romantic; charming to opposite sex; wives witty and independent, proud of home; husbands generous providers but impulsive.",
        ideal_partner_signs=["Leo", "Sagittarius", "Libra"],
        domestic_environments="Loves home and family; keeps residence clean and organized; excellent host who welcomes cheerful company.",
        professions=[
            "Army Officers", "Defense Personnel", "Surgeons", "Police", "Detectives",
            "Engineers", "Mechanics", "Iron and Steel workers", "Chemists", "Firefighters",
            "Sportsmen", "Butchers", "Barbers", "Kiln workers",
        ],
        places=[
            "Pastures for cattle", "Sandy soils", "Hilly grounds", "Plateaus",
            "Ceilings and roofs", "Iron foundries", "Furnaces",
        ],
        direction="East",
        products=[
            "Iron and Steel", "Machinery", "Motors", "Tractors", "Heavy acids",
            "Sports goods", "Weapons", "Firearms",
        ],
        countries_and_cities=[
            "Britain", "Germany", "Denmark", "Palestine", "Syria", "Burgundy",
            "Naples", "Marseilles", "Florence", "Verona", "Madras (Chennai)",
        ],
        handwriting="Stiff and rigid with sharp angles and narrow hooks; lines slanting to the right; words connected in groups of three and four; thick strokes with a bold underline.",
        lucky_days=["Tuesday", "Saturday", "Friday"],
        lucky_numbers=[9, 8, 6],
        lucky_stones=["Red Coral", "Blue Sapphire"],
        lucky_colors=["Red", "Yellow", "Copper"],
    ),
    "Taurus": SignSignification(
        sign_name="Taurus",
        sanskrit_name="Rishaba",
        symbol="Bull",
        start_degree=30.0,
        end_degree=60.0,
        ruling_planet="Venus",
        exaltation_planet="Moon",
        debilitation_planet=None,
        detriment_planet="Mars",
        constellations_included=["Krittika (Padas 2-4)", "Rohini (1-4)", "Mrigashira (Padas 1-2)"],
        physical_appearance="Middle stature, plump body, broad forehead, thick and stout neck, bright eyes, dark hair, solidly built stocky frame with strong shoulders.",
        mental_tendencies="Patient, enduring, slow and steady, determined, plodding, persevering, conservative, conservative in finances, faithful in affection.",
        characteristics="Great power of endurance; slow to anger, but when provoked, wild and unrelenting like an earthquake; superb long-term planner; appreciates music, art, and fine food.",
        health_and_diseases=[
            "Throat afflictions", "Tonsillitis", "Diphtheria", "Goitre",
            "Apoplexy", "Mumps", "Laryngeal disorders",
        ],
        body_parts=["Throat", "Neck", "Vocal cords", "Thyroid gland", "Pharynx"],
        finance_and_fortune="Sharp eye on money and worldly possessions; accumulates estates, jewelry, and gems; handles finances with utmost prudence; patient accumulator.",
        romance_and_marriage="Deeply loyal, steady, and affectionate; devoted domestic partner; loves domestic comforts, aesthetic home decor, and harmony.",
        ideal_partner_signs=["Virgo", "Capricorn", "Scorpio"],
        domestic_environments="Comfortable, harmonious, and decorated with taste; surrounded by gardens, orchards, and peaceful rural surroundings.",
        professions=[
            "Finance and Banking", "Agriculture", "Horticulture", "Jewelry trade",
            "Music and Arts", "Luxury Goods", "Cosmetics", "Architecture", "Hotels and Catering",
        ],
        places=[
            "Meadows", "Pastures", "Agricultural lands", "Gardens", "Banks",
            "Dining rooms", "Wardrobes", "Stables",
        ],
        direction="South",
        products=[
            "Wheat", "Barley", "Rice", "Sugar", "Silk", "Perfumes",
            "Jewelry", "Dairy products", "Flowers",
        ],
        countries_and_cities=[
            "Ireland", "Persia", "Poland", "Asia Minor", "Rhodes",
            "Dublin", "Leipzig", "St. Louis",
        ],
        handwriting="Round, graceful, even letters with well-defined curved hooks; calm and steady rhythm; rarely blots or erases.",
        lucky_days=["Friday", "Wednesday", "Saturday"],
        lucky_numbers=[6, 5, 8],
        lucky_stones=["Diamond", "White Sapphire", "Emerald"],
        lucky_colors=["White", "Pink", "Green"],
    ),
    "Gemini": SignSignification(
        sign_name="Gemini",
        sanskrit_name="Mithuna",
        symbol="Twins",
        start_degree=60.0,
        end_degree=90.0,
        ruling_planet="Mercury",
        exaltation_planet=None,
        debilitation_planet=None,
        detriment_planet="Jupiter",
        constellations_included=["Mrigashira (Padas 3-4)", "Ardra (1-4)", "Punarvasu (Padas 1-3)"],
        physical_appearance="Tall, upright, slender stature; long arms and fingers; thin features, sharp dark eyes, quick active gait, vivacious expression.",
        mental_tendencies="Inquisitive, intellectual, versatile, quick-witted, literary-minded, adaptable, fond of travel, conversation, and exchange of ideas.",
        characteristics="Dual nature; capable of managing multiple projects simultaneously; gifted speaker and writer; restless and easily bored if tied to routine.",
        health_and_diseases=[
            "Bronchitis", "Asthma", "Pleurisy", "Pneumonia", "Nervous disorders",
            "Respiratory catarrh", "Fractures of collar bone and arms",
        ],
        body_parts=["Shoulders", "Arms", "Hands", "Lungs", "Respiratory tract", "Nervous system"],
        finance_and_fortune="Fluctuating income; gains through intellectual activities, journalism, trade, brokerage, and multiple streams of work.",
        romance_and_marriage="Charming and intellectually stimulating companion; needs mental camaraderie; avoids possessive or overly emotional partners.",
        ideal_partner_signs=["Libra", "Aquarius", "Sagittarius"],
        domestic_environments="Lively, full of books, magazines, telephones, radios, and gadgets; frequently hosting friends and intellectual visitors.",
        professions=[
            "Journalists", "Authors", "Accountants", "Secretaries", "Translators",
            "Post and Telegraph workers", "Brokers", "Commercial Travelers", "Teachers", "Publishers",
        ],
        places=[
            "Libraries", "Bookshops", "Schools", "Railway stations", "Airports",
            "Post offices", "Print shops",
        ],
        direction="West",
        products=[
            "Paper", "Books", "Stationery", "Communication instruments",
            "Scientific apparatus", "Light transport vehicles",
        ],
        countries_and_cities=[
            "United States", "Belgium", "Wales", "Tripoli",
            "London", "Melbourne", "San Francisco", "Nuremberg",
        ],
        handwriting="Rapid, thin, upright or slightly slanting; connected words with light pressure; dots and crosses swiftly completed.",
        lucky_days=["Wednesday", "Friday", "Thursday"],
        lucky_numbers=[5, 6, 3],
        lucky_stones=["Emerald", "Green Agate"],
        lucky_colors=["Green", "Yellow", "Light Blue"],
    ),
    "Cancer": SignSignification(
        sign_name="Cancer",
        sanskrit_name="Kataka",
        symbol="Crab",
        start_degree=90.0,
        end_degree=120.0,
        ruling_planet="Moon",
        exaltation_planet="Jupiter",
        debilitation_planet="Mars",
        detriment_planet="Saturn",
        constellations_included=["Punarvasu (Pada 4)", "Pushya (1-4)", "Ashlesha (1-4)"],
        physical_appearance="Moderate stature, round face, pale complexion, stout upper body, prominent chest, full cheeks, expressive emotional eyes, walking with a rolling gait.",
        mental_tendencies="Emotional, sensitive, sympathetic, imaginative, protective, domestic, retentive memory, patriotic, prudent, cautious.",
        characteristics="Deep love for home and mother; moody and receptive to surroundings; tenacity like the crab's claw; excellent financial instinct and prudence.",
        health_and_diseases=[
            "Stomach disorders", "Indigestion", "Dropsy", "Pleurisy",
            "Gastric ulcers", "Digestive catarrh", "Gallstones",
        ],
        body_parts=["Chest", "Breasts", "Stomach", "Digestive organs", "Epigastric region"],
        finance_and_fortune="Careful and thrifty; amasses wealth through cautious savings, real estate, liquid assets, and ancestral connections.",
        romance_and_marriage="Deeply devoted and protective partner; craves emotional security and affection; devoted parent.",
        ideal_partner_signs=["Scorpio", "Pisces", "Capricorn"],
        domestic_environments="Warm, welcoming, centered around family and culinary comfort; prefers living near lakes, rivers, or the sea.",
        professions=[
            "Sailors", "Marine Engineers", "Fishermen", "Liquid Refreshment dealers",
            "Dairy farmers", "Nurses", "Caterers", "Hotel Keepers", "Historians", "Antiquarians",
        ],
        places=[
            "Rivers", "Seashores", "Lakes", "Wells", "Cisterns",
            "Kitchens", "Dining rooms", "Historical monuments",
        ],
        direction="North",
        products=[
            "Water", "Milk", "Dairy products", "Liquids", "Seafood",
            "Pearls", "Silver", "Fabrics",
        ],
        countries_and_cities=[
            "Scotland", "Holland", "New Zealand", "Paraguay",
            "Amsterdam", "New York", "Manchester", "Stockholm",
        ],
        handwriting="Curved, rounded letters with full loops in lower zones; gentle pressure; legible, emotional, and rhythmic.",
        lucky_days=["Monday", "Tuesday", "Thursday"],
        lucky_numbers=[2, 7, 9],
        lucky_stones=["Pearl", "Moonstone"],
        lucky_colors=["White", "Silver", "Sea Green"],
    ),
    "Leo": SignSignification(
        sign_name="Leo",
        sanskrit_name="Simha",
        symbol="Lion",
        start_degree=120.0,
        end_degree=150.0,
        ruling_planet="Sun",
        exaltation_planet=None,
        debilitation_planet=None,
        detriment_planet="Saturn",
        constellations_included=["Magha (1-4)", "Purva Phalguni (1-4)", "Uttara Phalguni (Pada 1)"],
        physical_appearance="Broad shoulders, commanding posture, prominent chest, majestic gait, bright eyes, light brown or golden wavy hair, dignified regal countenance.",
        mental_tendencies="Magnanimous, ambitious, noble, generous, authoritative, dignified, courageous, loyal, open-hearted, hates pettiness and deceit.",
        characteristics="Natural leader; commands respect without exertion; loves pomp, ceremony, and luxury; fiercely defends honor; susceptible to flattery.",
        health_and_diseases=[
            "Heart diseases", "Palpitation", "Spinal disorders", "High blood pressure",
            "Sunstroke", "Giddiness", "Fevers",
        ],
        body_parts=["Heart", "Spinal column", "Back", "Aorta", "Cardiac circulation"],
        finance_and_fortune="High earning potential coupled with lavish expenditure; liberal spender; gains through high governmental posts, executive positions, and leadership.",
        romance_and_marriage="Passionate, romantic, and faithful lover; treats partner with royal respect; expects admiration and loyalty in return.",
        ideal_partner_signs=["Aries", "Sagittarius", "Aquarius"],
        domestic_environments="Palatial, luxurious, tastefully decorated with gold, rich fabrics, and majestic furnishings; generous entertainer.",
        professions=[
            "King", "Ministers", "High Government Officials", "Executives",
            "Judges", "Goldsmiths", "Directors", "Theatrical Managers", "Military Commanders",
        ],
        places=[
            "Royal palaces", "Castles", "Government buildings", "Forests",
            "Deserts", "High hills", "Theaters",
        ],
        direction="East",
        products=[
            "Gold", "Precious stones", "Medicines", "Aromatic herbs",
            "Luxurious garments", "Brass",
        ],
        countries_and_cities=[
            "France", "Italy", "Bohemia", "Sicily",
            "Rome", "Bristol", "Damascus", "Philadelphia",
        ],
        handwriting="Large, bold, open, upright letters; dramatic capitals; steady and authoritative strokes; grand signature.",
        lucky_days=["Sunday", "Tuesday", "Thursday"],
        lucky_numbers=[1, 4, 9],
        lucky_stones=["Ruby", "Amber"],
        lucky_colors=["Orange", "Gold", "Bright Red"],
    ),
    "Virgo": SignSignification(
        sign_name="Virgo",
        sanskrit_name="Kanni",
        symbol="Virgin",
        start_degree=150.0,
        end_degree=180.0,
        ruling_planet="Mercury",
        exaltation_planet="Mercury",
        debilitation_planet="Venus",
        detriment_planet="Jupiter",
        constellations_included=["Uttara Phalguni (Padas 2-4)", "Hasta (1-4)", "Chitra (Padas 1-2)"],
        physical_appearance="Middle stature, slender and well-knit body, dark neat hair, active walk, sharp and analytical eyes, neat and modest appearance.",
        mental_tendencies="Analytical, methodical, critical, industrious, hygienic, intellectual, observant, diplomatic, precise, practical.",
        characteristics="Fastidious eye for detail; perfectionist; excels in organization, editing, and medical analysis; prone to worry over trivial matters.",
        health_and_diseases=[
            "Intestinal complaints", "Appendicitis", "Dysentery", "Typhoid",
            "Colic", "Constipation", "Malnutrition", "Nervous debility",
        ],
        body_parts=["Abdomen", "Bowels", "Intestines", "Digestive tract", "Spleen"],
        finance_and_fortune="Prudent financial management; earns steadily through service, commerce, auditing, scientific, and technical professions.",
        romance_and_marriage="Thoughtful, caring, and loyal partner; expresses affection through practical service and consideration; cautious in entering relationships.",
        ideal_partner_signs=["Taurus", "Capricorn", "Pisces"],
        domestic_environments="Spotlessly clean, orderly, hygienic, and equipped with practical tools and reference books.",
        professions=[
            "Doctors", "Pharmacists", "Auditors", "Accountants", "Statisticians",
            "Inspectors", "Proofreaders", "Secretaries", "Librarians", "Chemists", "Dietitians",
        ],
        places=[
            "Libraries", "Laboratories", "Pharmacies", "Offices",
            "Clinics", "Granaries", "Fields of grain",
        ],
        direction="South",
        products=[
            "Medicines", "Chemicals", "Grains", "Paper",
            "Surgical instruments", "Calculators", "Sanitary appliances",
        ],
        countries_and_cities=[
            "Turkey", "Switzerland", "West Indies", "Mesopotamia",
            "Paris", "Lyon", "Heidelberg", "Boston",
        ],
        handwriting="Small, neat, regular, precise, legible; small letters cleanly formed; margins strictly observed.",
        lucky_days=["Wednesday", "Friday"],
        lucky_numbers=[5, 6],
        lucky_stones=["Emerald", "Jade", "Green Tourmaline"],
        lucky_colors=["Green", "Grey", "Navy Blue"],
    ),
    "Libra": SignSignification(
        sign_name="Libra",
        sanskrit_name="Thulam",
        symbol="Scales / Balance",
        start_degree=180.0,
        end_degree=210.0,
        ruling_planet="Venus",
        exaltation_planet="Saturn",
        debilitation_planet="Sun",
        detriment_planet="Mars",
        constellations_included=["Chitra (Padas 3-4)", "Swati (1-4)", "Vishakha (Padas 1-3)"],
        physical_appearance="Tall and slender, well-proportioned body, graceful features, charming smile, fair complexion, dimpled cheeks or chin, pleasing and attractive appearance.",
        mental_tendencies="Just, sympathetic, peace-loving, diplomatic, aesthetic, refined, sociable, balanced, cooperative, fond of partnership and harmony.",
        characteristics="Strong sense of justice and fair play; natural arbitrator; hates discord and violence; artistic temperament; can be indecisive when weighing options.",
        health_and_diseases=[
            "Kidney disorders", "Bright's disease", "Lumbago", "Urinary infections",
            "Diabetes", "Eczema", "Suppression of urine",
        ],
        body_parts=["Kidneys", "Loins", "Spine lumbar region", "Adrenal glands", "Pelvis"],
        finance_and_fortune="Gains through partnership, legal profession, diplomacy, cosmetic arts, public trade, and joint enterprises.",
        romance_and_marriage="Marriage is central to happiness; deeply affectionate, romantic, and charming partner; desires mental harmony and equality.",
        ideal_partner_signs=["Gemini", "Aquarius", "Aries"],
        domestic_environments="Artistic, elegant, beautifully balanced, adorned with flowers, artwork, mirrors, and pleasing soft lighting.",
        professions=[
            "Judges", "Lawyers", "Diplomats", "Arbitrators", "Artists",
            "Musicians", "Interior Decorators", "Perfumers", "Cosmeticians", "Partnership Merchants",
        ],
        places=[
            "Courts of justice", "Art galleries", "Music rooms", "Ballrooms",
            "Boutiques", "High-class clubs", "Windmills",
        ],
        direction="West",
        products=[
            "Cosmetics", "Perfumes", "Art objects", "Musical instruments",
            "Silks", "Confectionery", "Jewelry",
        ],
        countries_and_cities=[
            "Austria", "Argentina", "Japan", "Burma",
            "Vienna", "Lisbon", "Copenhagen", "Frankfurt",
        ],
        handwriting="Graceful, flowing, artistic, elegant spacing; curved letters with aesthetic flair; balanced margins.",
        lucky_days=["Friday", "Saturday", "Wednesday"],
        lucky_numbers=[6, 8, 5],
        lucky_stones=["Diamond", "White Sapphire"],
        lucky_colors=["Light Blue", "Pink", "White"],
    ),
    "Scorpio": SignSignification(
        sign_name="Scorpio",
        sanskrit_name="Vrischika",
        symbol="Scorpion",
        start_degree=210.0,
        end_degree=240.0,
        ruling_planet="Mars",
        exaltation_planet="Uranus",
        debilitation_planet="Moon",
        detriment_planet="Venus",
        constellations_included=["Vishakha (Pada 4)", "Anuradha (1-4)", "Jyeshtha (1-4)"],
        physical_appearance="Middle stature, robust, sturdy and muscular body, broad face, thick curling dark hair, penetrating and hypnotic eyes, prominent nose.",
        mental_tendencies="Intense, secretive, determined, resourceful, investigative, occult-minded, passionate, courageous, unrelenting, unyielding.",
        characteristics="Unmatched willpower; can endure extreme hardship; penetrates to the core of mysteries; passionate in loyalty and formidable in enmity; sharp tongue.",
        health_and_diseases=[
            "Genital and urinary infections", "Piles", "Fistula", "Ulcers",
            "Venereal complaints", "Nasal catarrh", "Prostate enlargement",
        ],
        body_parts=["Generative organs", "Excretory organs", "Prostate", "Bladder", "Pelvic colon"],
        finance_and_fortune="Gains through inheritance, insurance, wills, research, surgery, mining, and joint finances; strategic and shrewd accumulator.",
        romance_and_marriage="Deeply passionate, magnetic, and fiercely loyal; demands total commitment; prone to intense jealousy if provoked.",
        ideal_partner_signs=["Cancer", "Pisces", "Taurus"],
        domestic_environments="Private, secure, quiet retreat where the native can relax undisturbed away from prying public eyes.",
        professions=[
            "Surgeons", "Detectives", "Chemists", "Research Scientists", "Occultists",
            "Miners", "Naval Officers", "Insurance Investigators", "Butchers", "Psychiatrists",
        ],
        places=[
            "Laboratories", "Mines", "Operating theaters", "Cemeteries",
            "Swamps", "Hidden chambers", "Chemical factories",
        ],
        direction="North",
        products=[
            "Poisons", "Chemicals", "Oils", "Petroleum",
            "Surgical blades", "Metals extracted from earth", "Wine",
        ],
        countries_and_cities=[
            "Norway", "Algeria", "Morocco", "Transvaal",
            "Liverpool", "Washington", "Dover", "Messina",
        ],
        handwriting="Firm, sharp, angular strokes with heavy downward pressure; condensed letters with hidden flourishes.",
        lucky_days=["Tuesday", "Thursday", "Sunday"],
        lucky_numbers=[9, 3, 1],
        lucky_stones=["Yellow Topaz", "Red Coral"],
        lucky_colors=["Dark Red", "Maroon", "Black"],
    ),
    "Sagittarius": SignSignification(
        sign_name="Sagittarius",
        sanskrit_name="Dhanus",
        symbol="Centaur / Archer",
        start_degree=240.0,
        end_degree=270.0,
        ruling_planet="Jupiter",
        exaltation_planet=None,
        debilitation_planet=None,
        detriment_planet="Mercury",
        constellations_included=["Mula (1-4)", "Purva Ashadha (1-4)", "Uttara Ashadha (Pada 1)"],
        physical_appearance="Tall, well-formed athletic figure, high forehead, clear open frank eyes, cheerful expression, reddish brown hair, long nose, dignified bearing.",
        mental_tendencies="Philosophical, optimistic, religious, generous, freedom-loving, frank, truth-seeking, prophetic, athletic, aspiring.",
        characteristics="Broad-minded visionary; loves open air, sports, philosophy, and long travel; highly moral and philanthropic; occasionally tactless due to excessive bluntness.",
        health_and_diseases=[
            "Sciatica", "Hip and thigh injuries", "Rheumatism", "Arterial disorders",
            "Gout", "Liver congestion", "Accidents from horses and sports",
        ],
        body_parts=["Hips", "Thighs", "Arterial system", "Femur", "Sacral region"],
        finance_and_fortune="Fortunate through higher education, publishing, law, foreign commerce, religious institutions, and wise investments; generous benefactor.",
        romance_and_marriage="Honest, jovial, and open partner; values mutual freedom and philosophical resonance; companionable marriage.",
        ideal_partner_signs=["Aries", "Leo", "Gemini"],
        domestic_environments="Spacious, open, well-ventilated, decorated with trophies, sports equipment, travel souvenirs, and spiritual texts.",
        professions=[
            "Judges", "Philosophers", "Professors", "Publishers", "Clergy / Priests",
            "Horse Trainers", "Sportsmen", "Explorers", "Foreign Ambassadors", "Philanthropists",
        ],
        places=[
            "Temples", "Churches", "Universities", "Courts",
            "Race courses", "Open pastures", "Stables", "Forests",
        ],
        direction="East",
        products=[
            "Horses", "Sports goods", "Philosophical books", "Silks",
            "Gold", "Medicinal barks", "Spices",
        ],
        countries_and_cities=[
            "Spain", "Hungary", "Australia", "Arabia",
            "Cologne", "Sheffield", "Toronto", "Toledo",
        ],
        handwriting="Free-flowing, bold, ascending lines; large looping letters with wide spacing; open and optimistic signature.",
        lucky_days=["Thursday", "Sunday", "Tuesday"],
        lucky_numbers=[3, 1, 9],
        lucky_stones=["Yellow Sapphire", "Golden Topaz"],
        lucky_colors=["Yellow", "Purple", "Golden Orange"],
    ),
    "Capricorn": SignSignification(
        sign_name="Capricorn",
        sanskrit_name="Makara",
        symbol="Goat / Crocodile",
        start_degree=270.0,
        end_degree=300.0,
        ruling_planet="Saturn",
        exaltation_planet="Mars",
        debilitation_planet="Jupiter",
        detriment_planet="Moon",
        constellations_included=["Uttara Ashadha (Padas 2-4)", "Shravana (1-4)", "Dhanishta (Padas 1-2)"],
        physical_appearance="Short to middle stature, slender, bony frame, prominent chin and cheekbones, dark wiry hair, deep-set thoughtful eyes, careful deliberate gait.",
        mental_tendencies="Prudent, ambitious, methodical, disciplined, economical, persevering, patient, practical, cautious, persistent.",
        characteristics="Master of perseverance; climbs steadily to summit of career against heavy odds; respects tradition and authority; cautious in trust; disciplined work ethic.",
        health_and_diseases=[
            "Rheumatism", "Knee complaints", "Skin diseases", "Eczema",
            "Dislocation of bones", "Digestive sluggishness", "Melancholy",
        ],
        body_parts=["Knees", "Bones", "Joints", "Skeletal system", "Skin", "Teeth"],
        finance_and_fortune="Slow, steady accumulation of wealth through hard work, government contracts, mining, real estate, and conservative investments.",
        romance_and_marriage="Faithful, reliable, and duty-bound partner; takes marriage vows seriously; offers solid domestic stability and security.",
        ideal_partner_signs=["Taurus", "Virgo", "Cancer"],
        domestic_environments="Durable, orderly, traditional, practical, located in mountainous or quiet solid masonry surroundings.",
        professions=[
            "Administrators", "Government Officers", "Builders", "Contractors",
            "Mining Engineers", "Geologists", "Farmers", "Antiques dealers", "Managers",
        ],
        places=[
            "Mountains", "Rocky places", "Mines", "Quarries",
            "Old buildings", "Government secretariats", "Cemeteries",
        ],
        direction="South",
        products=[
            "Iron", "Lead", "Coal", "Minerals", "Cement",
            "Building materials", "Leather", "Hides",
        ],
        countries_and_cities=[
            "India", "Bulgaria", "Mexico", "Greece",
            "Oxford", "Brussels", "Delhi", "Port Said",
        ],
        handwriting="Compact, small, vertical, stiff, carefully aligned; regular spacing with minimal ornamentation; neat and economical.",
        lucky_days=["Saturday", "Wednesday", "Friday"],
        lucky_numbers=[8, 5, 6],
        lucky_stones=["Blue Sapphire", "Lapis Lazuli"],
        lucky_colors=["Blue", "Black", "Dark Brown"],
    ),
    "Aquarius": SignSignification(
        sign_name="Aquarius",
        sanskrit_name="Kumbha",
        symbol="Water Bearer",
        start_degree=300.0,
        end_degree=330.0,
        ruling_planet="Saturn",
        exaltation_planet=None,
        debilitation_planet=None,
        detriment_planet="Sun",
        constellations_included=["Dhanishta (Padas 3-4)", "Shatabhisha (1-4)", "Purva Bhadrapada (Padas 1-3)"],
        physical_appearance="Middle stature, robust, well-formed body, clear complexion, kind and broad forehead, intelligent eyes, gentle and friendly expression.",
        mental_tendencies="Humanitarian, inventive, progressive, intellectual, scientific, intuitive, altruistic, broad-minded, independent, original.",
        characteristics="Pioneer in research and reform; produces exceptional astrologers, scientists, and social reformers; champions universal brotherhood; unconventional.",
        health_and_diseases=[
            "Ankle sprains and fractures", "Varicose veins", "Circulatory sluggishness",
            "Heart weaknesses (via Leo opposition)", "Nervous exhaustion", "Spasms",
        ],
        body_parts=["Ankles", "Calves", "Circulatory system", "Blood flow", "Tibia and Fibula"],
        finance_and_fortune="Earnings through scientific inventions, research, aviation, electricity, astrology, cooperative societies, and social welfare.",
        romance_and_marriage="Seeks intellectual equality, camaraderie, and mutual respect; faithful partner who grants and expects individual freedom.",
        ideal_partner_signs=["Gemini", "Libra", "Leo"],
        domestic_environments="Modern, innovative, equipped with modern technology and gadgets, welcoming to reformers, researchers, and diverse friends.",
        professions=[
            "Astrologers", "Scientists", "Researchers", "Electricians", "Aviators",
            "Social Reformers", "Inventors", "Philosophers", "Radio Engineers", "Telecommunication experts",
        ],
        places=[
            "Observatories", "Laboratories", "Aviation grounds", "Broadcasting stations",
            "Electrical works", "Assembly halls", "Societies",
        ],
        direction="West",
        products=[
            "Electrical appliances", "Radio and TV equipment", "Airplanes",
            "Scientific apparatus", "Aluminium", "Rare gases",
        ],
        countries_and_cities=[
            "Russia", "Sweden", "Poland", "Abyssinia",
            "Brighton", "Salzburg", "Hamburg", "Bremen",
        ],
        handwriting="Unconventional, legible, original flourishes; even pressure with scientific clarity; spontaneous and clear.",
        lucky_days=["Saturday", "Tuesday", "Thursday"],
        lucky_numbers=[8, 9, 3],
        lucky_stones=["Blue Sapphire", "Amethyst"],
        lucky_colors=["Electric Blue", "Ultramarine", "Grey"],
    ),
    "Pisces": SignSignification(
        sign_name="Pisces",
        sanskrit_name="Meena",
        symbol="Two Fishes tied with a cord",
        start_degree=330.0,
        end_degree=360.0,
        ruling_planet="Jupiter",
        exaltation_planet="Venus",
        debilitation_planet="Mercury",
        detriment_planet="Mercury",
        constellations_included=["Purva Bhadrapada (Pada 4)", "Uttara Bhadrapada (1-4)", "Revati (1-4)"],
        physical_appearance="Short to middle stature, fleshy body, pale complexion, prominent soft eyes, full lips, small hands and feet, quiet and gentle demeanor.",
        mental_tendencies="Intuitive, sympathetic, compassionate, spiritual, imaginative, psychic, peaceful, self-sacrificing, contemplative, modest.",
        characteristics="Deeply receptive and mystical; easily affected by the sorrows of others; gifted in music, poetry, and occult arts; tendency to daydream or drift.",
        health_and_diseases=[
            "Foot disorders", "Corns", "Bunions", "Dropsy", "Lymphatic congestion",
            "Intestinal catarrh", "Mucous complaints", "Drug sensitivities",
        ],
        body_parts=["Feet", "Toes", "Lymphatic system", "Tarsus bones", "Mucous membranes"],
        finance_and_fortune="Earnings through oceanic shipping, charities, pharmaceuticals, spiritual institutions, fiction, music, and liquids.",
        romance_and_marriage="Deeply romantic, sensitive, and devoted partner; craves emotional and spiritual soulmate connection; extraordinarily forgiving.",
        ideal_partner_signs=["Cancer", "Scorpio", "Virgo"],
        domestic_environments="Peaceful, quiet sanctuary near water, decorated with artistic and mystical themes, aquarium, and tranquil music.",
        professions=[
            "Naval Officers", "Sailors", "Chemists", "Nurses", "Hospital Workers",
            "Clergy", "Spiritual Teachers", "Poets", "Fiction Writers", "Musicians", "Charity Organizers",
        ],
        places=[
            "Oceans", "Seas", "Docks", "Monasteries", "Hospitals",
            "Asylums", "Fish ponds", "Hermitages",
        ],
        direction="North",
        products=[
            "Fish", "Pearls", "Sea products", "Liquids", "Medicines",
            "Spiritual books", "Beverages", "Chemicals",
        ],
        countries_and_cities=[
            "Portugal", "Normandy", "Calabria", "Egypt",
            "Seville", "Warsaw", "Alexandria", "Lancaster",
        ],
        handwriting="Soft, flowing, rounded, gentle strokes; letters leaning slightly to the right with graceful curves.",
        lucky_days=["Thursday", "Monday", "Tuesday"],
        lucky_numbers=[3, 2, 7, 9],
        lucky_stones=["Yellow Sapphire", "Cat's Eye", "Aquamarine"],
        lucky_colors=["Sea Green", "Yellow", "Lavender"],
    ),
}


# ---------------------------------------------------------------------------
# 3. TWELVE HOUSES SIGNIFICANCE (Chapter 17)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HouseSignificationKP:
    """Complete significations of a Bhava/House according to KP Reader 2 Chapter 17."""
    house: int
    sanskrit_name: str
    primary_matters: List[str]
    anatomical_parts: List[str]
    relatives_signified: List[str]
    favorable_conjunctions: List[str]
    unfavorable_conjunctions: List[str]
    karakas: List[str]
    detailed_signification: str


HOUSE_SIGNIFICATIONS_KP: Dict[int, HouseSignificationKP] = {
    1: HouseSignificationKP(
        house=1,
        sanskrit_name="Tanu Bhava (Lagna)",
        primary_matters=[
            "Physical body", "Complexion", "Constitution", "General health",
            "Longevity", "Vitality", "Character and temperament", "Self-expression",
            "Fame and reputation", "Head and brain",
        ],
        anatomical_parts=["Head", "Brain", "Cranial bones", "Facial structure"],
        relatives_signified=["Native himself / herself", "Grandmother (4th from 10th)"],
        favorable_conjunctions=["1", "2", "3", "10", "11"],
        unfavorable_conjunctions=["6", "8", "12"],
        karakas=["Sun"],
        detailed_signification="Represents the native's personality, physical appearance, mental disposition, general health, life force, and the overall course of destiny. As the pivotal cusp, its sub-lord dictates the native's vitality and life achievements.",
    ),
    2: HouseSignificationKP(
        house=2,
        sanskrit_name="Dhana Bhava",
        primary_matters=[
            "Wealth and money", "Liquid assets", "Speech", "Vision / Right eye",
            "Family", "Food and diet", "Moveable property", "Jewelry and precious metals",
            "Primary education", "Maraka (Death-inflicting) power",
        ],
        anatomical_parts=["Face", "Right eye", "Teeth", "Tongue", "Vocal organs", "Chin", "Throat"],
        relatives_signified=["Immediate family members", "Second wife / partner"],
        favorable_conjunctions=["2", "6", "10", "11"],
        unfavorable_conjunctions=["1", "8", "12"],
        karakas=["Jupiter"],
        detailed_signification="Rules accumulated wealth, money in hand, domestic harmony, power of speech, eloquence, eating habits, and the right eye. In KP, it is also a primary house of material fructification (2, 6, 11) and a Maraka sthana.",
    ),
    3: HouseSignificationKP(
        house=3,
        sanskrit_name="Sahaja / Bhratru Bhava",
        primary_matters=[
            "Younger coborns (brothers and sisters)", "Courage and valor", "Short journeys",
            "Communication", "Letters and correspondence", "Writing and signing documents",
            "Agreements and contracts", "Neighbours and cousins", "Hands and arms",
        ],
        anatomical_parts=["Hands", "Arms", "Shoulders", "Collar bones", "Respiratory canal", "Right ear"],
        relatives_signified=["Younger brothers", "Younger sisters", "Cousins", "Neighbours"],
        favorable_conjunctions=["3", "5", "11"],
        unfavorable_conjunctions=["2", "8", "12"],
        karakas=["Mars"],
        detailed_signification="Signifies courage, initiatives, communicative prowess, publications, short-distance travels, junior co-borns, and intellectual agility. Vital for sales, negotiation, and journalism.",
    ),
    4: HouseSignificationKP(
        house=4,
        sanskrit_name="Sukha / Mathru Bhava",
        primary_matters=[
            "Mother", "Immovable property", "Lands and buildings", "Vehicles / conveyances",
            "Academic education", "Domestic happiness", "Underground treasures and mines",
            "End of life conditions", "Chest and lungs",
        ],
        anatomical_parts=["Chest", "Breasts", "Lungs", "Ribs", "Heart (emotional aspects)"],
        relatives_signified=["Mother", "Maternal ancestors"],
        favorable_conjunctions=["4", "11", "12"],
        unfavorable_conjunctions=["3", "8"],
        karakas=["Moon", "Venus", "Mars (for land)"],
        detailed_signification="Denotes the mother's longevity and health, ancestral property, residential comforts, academic diplomas, vehicles, and the native's domestic sanctuary and emotional contentment.",
    ),
    5: HouseSignificationKP(
        house=5,
        sanskrit_name="Putra Bhava",
        primary_matters=[
            "Children / Progeny", "Intelligence and intellect", "Creative talents",
            "Romance and love affairs", "Speculation / Lottery / Shares",
            "Past merit (Purva Punya)", "Spiritual mantras and rituals", "Sports and entertainment",
        ],
        anatomical_parts=["Heart", "Stomach", "Upper abdomen", "Liver", "Spleen"],
        relatives_signified=["Children", "Paternal grandfather (9th from 9th)"],
        favorable_conjunctions=["2", "5", "11"],
        unfavorable_conjunctions=["1", "4", "8", "12"],
        karakas=["Jupiter"],
        detailed_signification="Primary cusp for childbirth, speculative ventures, romantic unions, artistic ingenuity, and spiritual discipleship. Its connection with houses 2 and 11 guarantees children and speculative success.",
    ),
    6: HouseSignificationKP(
        house=6,
        sanskrit_name="Ripu / Roga Bhava",
        primary_matters=[
            "Disease and ailments", "Debts and loans", "Litigation and lawsuits",
            "Enemies and rivals", "Service and employment", "Subordinates and servants",
            "Maternal uncle", "Competitive examinations", "Pet animals",
        ],
        anatomical_parts=["Intestines", "Digestive system", "Abdominal region", "Kidneys (part)"],
        relatives_signified=["Maternal uncle", "Employees", "Tenants"],
        favorable_conjunctions=["6", "10", "11"],
        unfavorable_conjunctions=["5", "12"],
        karakas=["Mars", "Saturn"],
        detailed_signification="Governs illnesses, litigations, banking debts, daily labor, competitive exams, and professional employment. In KP, House 6 is an Upachaya sthana providing gains through employment and victory over competitors.",
    ),
    7: HouseSignificationKP(
        house=7,
        sanskrit_name="Kalatra Bhava",
        primary_matters=[
            "Spouse / Marriage partner", "Business partners", "Legal contracts",
            "Open enemies and competitors", "Public relations and trade", "Foreign travels / residency",
            "Second child (3rd from 5th)", "Maraka (Death-inflicting) cusp",
        ],
        anatomical_parts=["Kidneys", "Internal generative organs", "Bladder", "Pelvic region"],
        relatives_signified=["Spouse (Husband/Wife)", "Business Partner"],
        favorable_conjunctions=["2", "7", "11"],
        unfavorable_conjunctions=["1", "6", "12"],
        karakas=["Venus"],
        detailed_signification="The pivotal house for matrimony, partnerships, legal ties, and commercial transactions. Its cuspal sub-lord is the definitive arbiter of whether marriage is promised and whether it thrives or dissolves.",
    ),
    8: HouseSignificationKP(
        house=8,
        sanskrit_name="Ayur / Randhra Bhava",
        primary_matters=[
            "Longevity and span of life", "Mode of death", "Accidents and sudden danger",
            "Unearned wealth / Inheritance", "Insurance policies and wills",
            "Gifts and dowry", "Humiliation and mental distress", "Occult sciences and research",
        ],
        anatomical_parts=["External generative organs", "Excretory organs", "Anus", "Perineum"],
        relatives_signified=["In-laws", "Deceased ancestors"],
        favorable_conjunctions=["8", "11", "2"],
        unfavorable_conjunctions=["1", "7", "12"],
        karakas=["Saturn"],
        detailed_signification="The house of longevity, sudden transformations, hidden perils, surgical operations, legacy, insurance, and deep occult penetration. Connected with 2 and 11, it yields sudden legacy; with 1 and 6, severe distress.",
    ),
    9: HouseSignificationKP(
        house=9,
        sanskrit_name="Bhagya / Dharma Bhava",
        primary_matters=[
            "Father", "Fortune and divine grace", "Higher education and research",
            "Religion and spiritual philosophy", "Pilgrimages and long journeys",
            "Guru / Preceptor", "Law and judiciary", "Publishing",
        ],
        anatomical_parts=["Hips", "Thighs", "Femoral arteries"],
        relatives_signified=["Father", "Preceptor / Guru", "Grandchildren (5th from 5th)"],
        favorable_conjunctions=["9", "11", "1"],
        unfavorable_conjunctions=["8", "12"],
        karakas=["Jupiter", "Sun (for father)"],
        detailed_signification="House of righteousness (Dharma), ancestral blessings, supreme fortune, overseas travels, higher wisdom, publishing, and spiritual awakening.",
    ),
    10: HouseSignificationKP(
        house=10,
        sanskrit_name="Karma / Rajya Bhava",
        primary_matters=[
            "Profession and career", "Honor and dignity", "Public status and fame",
            "Government favor and authority", "Promotion and rank", "Ambition",
            "Knees and joints",
        ],
        anatomical_parts=["Knees", "Patella", "Joints", "Skeletal frame"],
        relatives_signified=["Mother-in-law (4th from 7th)", "Employer / Sovereign"],
        favorable_conjunctions=["2", "6", "10", "11"],
        unfavorable_conjunctions=["5", "9", "12"],
        karakas=["Sun", "Saturn", "Mercury", "Jupiter"],
        detailed_signification="The pinnacle of the chart (Midheaven). Governs one's profession, livelihood, corporate or political standing, reputation, and public recognition.",
    ),
    11: HouseSignificationKP(
        house=11,
        sanskrit_name="Labha Bhava",
        primary_matters=[
            "Gains and profit", "Realization of hopes and wishes", "Elder coborns",
            "Friends and benefactors", "Societies and clubs", "Pleasant celebrations",
            "Left ear",
        ],
        anatomical_parts=["Left ear", "Ankles", "Calves", "Left hand"],
        relatives_signified=["Elder brothers", "Elder sisters", "Son-in-law / Daughter-in-law"],
        favorable_conjunctions=["1", "2", "11"],
        unfavorable_conjunctions=["8", "12"],
        karakas=["Jupiter"],
        detailed_signification="The paramount house of fulfillment of desires in KP astrology. Any event whose significator connects with House 11 terminates in joyous success, prosperity, and permanent gain.",
    ),
    12: HouseSignificationKP(
        house=12,
        sanskrit_name="Vyaya / Moksha Bhava",
        primary_matters=[
            "Expenses and losses", "Foreign settlements / travels", "Confinement / Hospitalization / Imprisonment",
            "Bed pleasures and sleep", "Secret enemies and intrigues", "Donations and charity",
            "Moksha (Final liberation)", "Feet and toes",
        ],
        anatomical_parts=["Feet", "Toes", "Left eye", "Lymphatic system"],
        relatives_signified=["Paternal uncle (3rd from 10th)", "Secret adversaries"],
        favorable_conjunctions=["2", "6", "11", "12"],
        unfavorable_conjunctions=["8"],
        karakas=["Saturn", "Ketu"],
        detailed_signification="Signifies expenditures, financial outflow, separation from birthplace, foreign residence, subconscious realms, hospitals, and ultimate spiritual liberation.",
    ),
}


# ---------------------------------------------------------------------------
# 4. PLANETARY SIGNIFICATIONS (Chapter 18)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlanetSignificationKP:
    """Detailed planetary significations according to KP Reader 2 Chapter 18."""
    planet: str
    sanskrit_name: str
    nature: str
    gender: str
    governs_body_parts: List[str]
    pathology_and_diseases: List[str]
    mental_qualities: List[str]
    professions: List[str]
    places: List[str]
    products_and_minerals: List[str]
    lucky_day: str
    lucky_numbers: List[int]
    lucky_stone: str
    lucky_color: str
    kp_special_doctrine: str


PLANET_SIGNIFICATIONS_KP: Dict[str, PlanetSignificationKP] = {
    "Sun": PlanetSignificationKP(
        planet="Sun",
        sanskrit_name="Surya",
        nature="Benefic / Royal / Hot / Dry",
        gender="Masculine",
        governs_body_parts=["Heart", "Spine", "Right eye in males", "Left eye in females", "Bones", "Brain vitality"],
        pathology_and_diseases=["Heart trouble", "High fever", "Eye affections", "Sunstroke", "Blood circulation disorders"],
        mental_qualities=["Authority", "Dignity", "Willpower", "Leadership", "Generosity", "Honor", "Ambition"],
        professions=["Kings", "Ministers", "High Government Officials", "Judges", "Physicians", "Bankers", "Jewelers"],
        places=["Palaces", "Government buildings", "Open squares", "Castles", "Capitols"],
        products_and_minerals=["Gold", "Ruby", "Wheat", "Medicinal herbs", "Aromatic wood"],
        lucky_day="Sunday",
        lucky_numbers=[1, 4],
        lucky_stone="Ruby",
        lucky_color="Golden Yellow / Orange",
        kp_special_doctrine="Natural significator for father, government, and vital soul force. Rules Leo and delivers results of its star-lord with authority.",
    ),
    "Moon": PlanetSignificationKP(
        planet="Moon",
        sanskrit_name="Chandra",
        nature="Benefic / Cold / Moist / Feminine",
        gender="Feminine",
        governs_body_parts=["Stomach", "Breasts", "Uterus", "Left eye in males", "Right eye in females", "Body fluids", "Lymph"],
        pathology_and_diseases=["Stomach disorders", "Dropsy", "Mental ailments", "Eye weaknesses", "Dysentery", "Cold/Catarrh"],
        mental_qualities=["Mind (Manas)", "Imagination", "Intuition", "Memory", "Sympathy", "Changeability", "Maternal instinct"],
        professions=["Sailors", "Marine officers", "Liquid refreshment dealers", "Nurses", "Midwives", "Historians", "Dairy farmers"],
        places=["Seas", "Rivers", "Lakes", "Fountains", "Wells", "Public markets"],
        products_and_minerals=["Silver", "Pearls", "Milk", "Liquids", "Salt", "White goods"],
        lucky_day="Monday",
        lucky_numbers=[2, 7],
        lucky_stone="Pearl / Moonstone",
        lucky_color="White / Silver",
        kp_special_doctrine="Chief governor of mind, public opinion, and fast transits. Star and sub of the Moon at birth or query moment provide critical timing cues.",
    ),
    "Mars": PlanetSignificationKP(
        planet="Mars",
        sanskrit_name="Mangal / Kuja",
        nature="Malefic / Fiery / Dry / Dynamic",
        gender="Masculine",
        governs_body_parts=["Muscles", "Head", "Bone marrow", "Genitals", "Blood", "Bile", "Motor nerves"],
        pathology_and_diseases=["Burns", "Fevers", "Inflammations", "Wounds", "Surgical operations", "Fractures", "Hemorrhages"],
        mental_qualities=["Courage", "Valor", "Aggressiveness", "Enthusiasm", "Leadership in battle", "Sharp wit", "Impatience"],
        professions=["Army Officers", "Surgeons", "Police", "Engineers", "Mechanics", "Ironworkers", "Firefighters", "Sportsmen"],
        places=["Battlefields", "Iron foundries", "Furnaces", "Operating rooms", "Kilns", "Butcher shops"],
        products_and_minerals=["Iron", "Steel", "Red coral", "Heavy chemicals", "Arms and ammunition"],
        lucky_day="Tuesday",
        lucky_numbers=[9],
        lucky_stone="Red Coral",
        lucky_color="Bright Red / Scarlet",
        kp_special_doctrine="Significator of land, brothers, machinery, and surgery. When connected with 8 or 12, prompts accidents or acute surgeries.",
    ),
    "Mercury": PlanetSignificationKP(
        planet="Mercury",
        sanskrit_name="Budha",
        nature="Neutral / Adaptable / Dual / Intellectual",
        gender="Neutral / Dual",
        governs_body_parts=["Central nervous system", "Brain", "Tongue", "Speech organs", "Hands", "Skin", "Lungs"],
        pathology_and_diseases=["Speech defects (stammering)", "Nervous breakdowns", "Respiratory catarrh", "Asthma", "Skin diseases"],
        mental_qualities=["Supreme intelligence", "Quick grasp", "Analytical acumen", "Linguistic fluency", "Memory", "Calculative power"],
        professions=["Accountants", "Auditors", "Journalists", "Authors", "Astrologers", "Teachers", "Brokers", "Translators"],
        places=["Libraries", "Schools", "Post offices", "Print presses", "Bookshops", "Commercial exchanges"],
        products_and_minerals=["Paper", "Stationery", "Books", "Emerald", "Brass", "Communication equipment"],
        lucky_day="Wednesday",
        lucky_numbers=[5],
        lucky_stone="Emerald",
        lucky_color="Green",
        kp_special_doctrine="Primary planet of astrology and intellect. Good aspect between Moon and Mercury gives photographic memory, intuition, and astrological mastery.",
    ),
    "Jupiter": PlanetSignificationKP(
        planet="Jupiter",
        sanskrit_name="Guru / Brihaspati",
        nature="Great Benefic / Warm / Moist / Divine",
        gender="Masculine",
        governs_body_parts=["Liver", "Arterial blood", "Thighs", "Fat / Adipose tissue", "Right ear", "Pancreas"],
        pathology_and_diseases=["Liver disorders", "Diabetes", "Obesity", "Arteriosclerosis", "Apoplexy", "Blood impurities"],
        mental_qualities=["Wisdom", "Devotion", "Justice", "Optimism", "Philanthropy", "Truthfulness", "Dignity"],
        professions=["Judges", "Lawyers", "Bankers", "Professors", "Clergy / Priests", "Philosophers", "Financial advisers"],
        places=["Courts of law", "Temples", "Churches", "Universities", "Colleges", "Treasuries", "Charitable trusts"],
        products_and_minerals=["Gold", "Yellow Sapphire", "Topaz", "Wheat", "Barley", "Sweet fruits"],
        lucky_day="Thursday",
        lucky_numbers=[3],
        lucky_stone="Yellow Sapphire",
        lucky_color="Yellow / Golden",
        kp_special_doctrine="Supreme benefic representing divine grace and past virtuous deeds (9th lord connection). Mitigates affliction and shields against evil.",
    ),
    "Venus": PlanetSignificationKP(
        planet="Venus",
        sanskrit_name="Sukra",
        nature="Benefic / Harmonious / Artistic / Feminine",
        gender="Feminine",
        governs_body_parts=["Throat", "Kidneys", "Generative organs", "Semen", "Complexion", "Pelvis", "Eyes (beauty)"],
        pathology_and_diseases=["Urinary and kidney diseases", "Venereal complaints", "Diabetes", "Throat infections", "Skin eruptions"],
        mental_qualities=["Aesthetic taste", "Romance", "Love of harmony", "Sociability", "Charming speech", "Artistic creativity"],
        professions=["Artists", "Musicians", "Actors", "Perfumers", "Cosmeticians", "Jewelers", "Cinema directors", "Silk traders"],
        places=["Theaters", "Art studios", "Boudoirs", "Music halls", "Boutiques", "High-class restaurants"],
        products_and_minerals=["Diamonds", "Silks", "Perfumes", "Cosmetics", "Musical instruments", "Confectionery"],
        lucky_day="Friday",
        lucky_numbers=[6],
        lucky_stone="Diamond / White Sapphire",
        lucky_color="White / Pink / Variegated",
        kp_special_doctrine="Chief governor of matrimony, conveyance (Vahana), and refined comforts. Key significator for marriage and partnership.",
    ),
    "Saturn": PlanetSignificationKP(
        planet="Saturn",
        sanskrit_name="Sani",
        nature="Great Malefic / Cold / Dry / Plodding",
        gender="Neutral / Feminine",
        governs_body_parts=["Bones", "Teeth", "Knees", "Joints", "Spleen", "Auditory nerve", "Skin"],
        pathology_and_diseases=["Chronic rheumatism", "Paralysis", "Gout", "Bone fractures", "Deafness", "Melancholia", "Consumption"],
        mental_qualities=["Perseverance", "Patience", "Discipline", "Economy", "Methodical research", "Caution", "Endurance"],
        professions=["Miners", "Geologists", "Builders", "Tannery workers", "Laborers", "Agriculturalists", "Antiques dealers"],
        places=["Mines", "Cemeteries", "Ruins", "Old buildings", "Dungeons", "Isolated dark corners"],
        products_and_minerals=["Iron", "Lead", "Coal", "Blue Sapphire", "Leather", "Kerosene", "Cement"],
        lucky_day="Saturday",
        lucky_numbers=[8],
        lucky_stone="Blue Sapphire / Amethyst",
        lucky_color="Dark Blue / Black",
        kp_special_doctrine="The planet of delay, obstacle, and sustained labor. When harmonious, grants unshakeable concentration and mathematical precision.",
    ),
    "Rahu": PlanetSignificationKP(
        planet="Rahu",
        sanskrit_name="Rahu (Dragon's Head)",
        nature="Shadowy Malefic / Smoky / Mysterious",
        gender="Feminine / Neutral",
        governs_body_parts=["Skin", "Breathing passages", "Legs", "Nervous network", "Intestinal parasites"],
        pathology_and_diseases=["Undiagnosed diseases", "Poisoning", "Leprosy", "Epidemics", "Hiccups", "Sudden hysteria"],
        mental_qualities=["Ambition", "Diplomacy", "Unconventional ideas", "Occult interests", "Worldly shrewdness", "Secretiveness"],
        professions=["Aviators", "Radio operators", "Chemical researchers", "Smugglers", "Diplomats", "Speculators", "Detectives"],
        places=["Radio stations", "Airports", "Underground caves", "Dense jungles", "Foreign lands"],
        products_and_minerals=["Gomedha (Hessonite)", "Lead", "Agate", "Petroleum", "Poisonous chemicals"],
        lucky_day="Saturday",
        lucky_numbers=[4],
        lucky_stone="Hessonite (Gomed)",
        lucky_color="Dark Smoky / Brown",
        kp_special_doctrine="In KP, Rahu acts as the representative agent of: (1) its sign lord, (2) planets aspecting/conjoining it, and (3) its star-lord. It is stronger than other grahas.",
    ),
    "Ketu": PlanetSignificationKP(
        planet="Ketu",
        sanskrit_name="Ketu (Dragon's Tail)",
        nature="Shadowy Fiery / Spiritual / Terminating",
        gender="Neutral",
        governs_body_parts=["Nervous system", "Spine", "Belly", "Feet", "Hair"],
        pathology_and_diseases=["Epidemics", "Skin eruptive sores", "Intestinal worms", "Boils", "Wasp and snake bites", "Surgery"],
        mental_qualities=["Spiritual detachment", "Moksha aspiration", "Intuition", "Self-sacrifice", "Asceticism", "Occult insight"],
        professions=["Spiritual ascetics", "Astrologers", "Occult practitioners", "Herbal doctors", "Watchmakers", "Monks"],
        places=["Hermitages", "Ashrams", "Solitary huts", "Surgical wards", "Cremation grounds"],
        products_and_minerals=["Cat's Eye (Vaidurya)", "Medicinal roots", "Earthen pots", "Copper"],
        lucky_day="Tuesday",
        lucky_numbers=[7],
        lucky_stone="Cat's Eye",
        lucky_color="Smoky Grey / Multi-colored",
        kp_special_doctrine="Agent representing its sign lord, star lord, and aspecting grahas. Chief karaka for spiritual enlightenment, intuition, and occult sciences.",
    ),
    "Uranus": PlanetSignificationKP(
        planet="Uranus",
        sanskrit_name="Herschel / Prajapati",
        nature="Eccentric / Electric / Radical / Occult",
        gender="Neutral",
        governs_body_parts=["Nervous system", "Aura", "Brain synapses", "Motor reflexes"],
        pathology_and_diseases=["Sudden nervous shocks", "Spasms", "Cramps", "Incurable neuroses", "Unexpected heart failure"],
        mental_qualities=["Originality", "Invention", "Astrological genius", "Radical reform", "Independence", "Eccentricity"],
        professions=["Astrologers", "Inventors", "Aviation experts", "Atomic researchers", "Electricians", "Radiologists"],
        places=["Observatories", "Power grids", "Aviation hangars", "Radio broadcast stations"],
        products_and_minerals=["Uranium", "Radium", "Electricity", "Zircon", "Modern electronics"],
        lucky_day="Wednesday / Saturday",
        lucky_numbers=[4],
        lucky_stone="Zircon / Aquamarine",
        lucky_color="Electric Blue / Fluorescent",
        kp_special_doctrine="Foremost modern planet for astrology and research. Harmonious aspect with Mercury, Moon, and Jupiter confers astrological mastery and intuition.",
    ),
    "Neptune": PlanetSignificationKP(
        planet="Neptune",
        sanskrit_name="Varuna",
        nature="Mystical / Subtle / Psychic / Liquid",
        gender="Feminine",
        governs_body_parts=["Pineal gland", "Spinal fluid", "Lymph", "Psychic sensory centers"],
        pathology_and_diseases=["Drug intoxication", "Coma", "Delusions", "Waterborne diseases", "Food poisoning", "Insanity"],
        mental_qualities=["Psychic perception", "Clairvoyance", "Mystical visions", "Musical genius", "Poetic idealism", "Dreaminess"],
        professions=["Mystics", "Clairvoyants", "Fiction writers", "Spiritual healers", "Musicians", "Film artists", "Naval sailors"],
        places=["Oceans", "Spiritual retreats", "Sanatoriums", "Film studios", "Chemical research centers"],
        products_and_minerals=["Anesthetics", "Liquids", "Oils", "Platinum", "Coral", "Artificial silks"],
        lucky_day="Monday / Thursday",
        lucky_numbers=[7],
        lucky_stone="Amethyst / Moonstone",
        lucky_color="Sea Green / Lavender / Opaline",
        kp_special_doctrine="Governs mystical states and deceptive appearances. Afflictions cause projects to start in a flash and end in a crash.",
    ),
    "Fortuna": PlanetSignificationKP(
        planet="Fortuna",
        sanskrit_name="Pars Fortunae / Athrishta",
        nature="Benefic / Material Harvest / Providential",
        gender="Neutral",
        governs_body_parts=["Physical well-being", "Vital stamina"],
        pathology_and_diseases=["None (Point of prosperity)"],
        mental_qualities=["Contentment", "Confidence", "Optimism"],
        professions=["Speculation", "Lottery winners", "Treasure seekers", "Beneficiaries of fortune"],
        places=["Treasuries", "Safe deposit vaults", "Stock exchanges"],
        products_and_minerals=["Unearned wealth", "Prizes", "Windfalls", "Precious gems"],
        lucky_day="Day of birth",
        lucky_numbers=[1, 6],
        lucky_stone="Yellow Sapphire / Diamond",
        lucky_color="Golden / Bright White",
        kp_special_doctrine="Sensitive point representing worldly prosperity and sudden unearned gains. Calculated as Ascendant + Moon - Sun (day) or Ascendant + Sun - Moon (night). Transits over Fortuna trigger material windfalls.",
    ),
}


# ---------------------------------------------------------------------------
# 5. FOUNDATIONAL KP EVALUATORS (Reader 2 Chapters 10, 12, 14, 15, 18)
# ---------------------------------------------------------------------------

@dataclass
class AstrologerAptitudeResult:
    """Evaluation score and factors for learning astrology (Reader 2 Chapter 14)."""
    score: int                     # Out of 100
    aptitude_grade: str            # "Excellent", "Good", "Moderate", "Unfavorable"
    factors_present: List[str]
    recommendations: List[str]
    reasons: List[str]


def evaluate_astrologer_proficiency(
    mercury_sign: str,
    moon_sign: str,
    uranus_sign: Optional[str] = None,
    saturn_sign: Optional[str] = None,
    jupiter_sign: Optional[str] = None,
    mars_sign: Optional[str] = None,
    ascendant_sign: Optional[str] = None,
    mercury_house: Optional[int] = None,
    moon_house: Optional[int] = None,
    jupiter_house: Optional[int] = None,
    saturn_house: Optional[int] = None,
    uranus_house: Optional[int] = None,
    is_moon_mercury_aspect: bool = False,
    is_saturn_mercury_aspect: bool = False,
    is_jupiter_mercury_aspect: bool = False,
    is_uranus_mercury_aspect: bool = False,
) -> AstrologerAptitudeResult:
    """Evaluates the native's chart for proficiency in learning and predicting astrology.
    
    Directly codifies the conditions given by Prof. K. S. Krishnamurti in Reader 2,
    pp. 86-95 ("Who can learn Astrology").
    """
    score = 20  # Base curiosity score
    factors: List[str] = []
    reasons: List[str] = []

    # 1. Moon in Cancer (Horasara rule cited by Krishnamurti)
    if moon_sign.strip().title() == "Cancer":
        score += 15
        factors.append("Moon in Cancer (Horasara citation)")
        reasons.append("Moon in Cancer grants natural receptivity, photographic memory, and intuitive astrological interest.")

    # 2. Moon and Mercury harmonious relationship
    if is_moon_mercury_aspect:
        score += 20
        factors.append("Harmonious Moon-Mercury aspect")
        reasons.append("Moon (mind mirror) and Mercury (intellect lens) in harmony provide clear exposition, good vocabulary, and intuitive perception.")

    # 3. Saturn and Mercury good connection
    if is_saturn_mercury_aspect:
        score += 15
        factors.append("Saturn-Mercury good connection")
        reasons.append("Saturn and Mercury grant concentration, depth of thought, persistence, and mathematical competence essential for KP.")

    # 4. Jupiter and Mercury connection
    if is_jupiter_mercury_aspect:
        score += 15
        factors.append("Jupiter-Mercury harmonious aspect")
        reasons.append("Jupiter gives wisdom, broad vision, command of language, and divine guidance in judging horoscopes.")

    # 5. Uranus involvement (Modern KP research planet)
    if is_uranus_mercury_aspect or (uranus_house and uranus_house in {1, 3, 9, 10}):
        score += 15
        factors.append("Uranus prominent in intellectual houses/aspects")
        reasons.append("Uranus governs original research, scientific deduction, and radical stellar astrology.")

    # 6. Mercury house placement (1, 4, 5, 7, 9, 10, 11 per Jataka Tatva)
    if mercury_house and mercury_house in {1, 4, 5, 7, 9, 10, 11}:
        score += 10
        factors.append(f"Mercury well-placed in House {mercury_house}")
        reasons.append(f"Mercury in House {mercury_house} promotes analytical reasoning and dedication to learning.")

    # 7. Gemini Ascendant with exalted Jupiter (Reader 2 rule 13)
    if ascendant_sign and ascendant_sign.strip().title() == "Gemini" and jupiter_sign and jupiter_sign.strip().title() == "Cancer":
        score += 20
        factors.append("Gemini Ascendant with Exalted Jupiter in Cancer")
        reasons.append("Classic stellar combination for an eminent scholar and teacher of astrology.")

    # 8. Saturn/Moon in 1, 3, 9, or 10th houses (Reader 2 rule 1)
    if (saturn_house and saturn_house in {1, 3, 9, 10}) or (moon_house and moon_house in {1, 3, 9, 10}):
        score += 10
        factors.append("Saturn/Moon in key houses (1, 3, 9, 10)")
        reasons.append("Gives immense appetite to learn astrology, plodding patience, and persevering research attitude.")

    final_score = min(score, 100)
    if final_score >= 80:
        grade = "Excellent"
        recs = [
            "Highly qualified for professional astrological practice and research.",
            "Possesses keen intuition, mathematical precision, and gift of truthful prophecy.",
        ]
    elif final_score >= 60:
        grade = "Good"
        recs = [
            "Capable of mastering stellar astrology and guiding clients accurately.",
            "Cultivate meditation and systematic ephemeris study to strengthen intuition.",
        ]
    elif final_score >= 40:
        grade = "Moderate"
        recs = [
            "Can learn astrology as an engaging hobby and for personal guidance.",
            "Verify calculations carefully and avoid over-confident predictions without corroboration.",
        ]
    else:
        grade = "Unfavorable"
        recs = [
            "May struggle with contradictory indications or lose patience during intricate calculations.",
            "Focus on foundational principles before attempting predictive consultancy.",
        ]

    return AstrologerAptitudeResult(
        score=final_score,
        aptitude_grade=grade,
        factors_present=factors,
        recommendations=recs,
        reasons=reasons,
    )


@dataclass
class SpeechAndFertilityPromise:
    """Evaluation of speech defects and childbearing fertility from Reader 2 Chapter 15."""
    speech_condition: str          # "Normal", "Vocal Gift", "Impediment Risk"
    speech_reasons: List[str]
    fertility_promise: str         # "Promised", "Delayed / Mixed", "Challenging / Barren"
    fertility_reasons: List[str]


def evaluate_speech_and_fertility(
    cusp_2_sign: str,
    cusp_5_sign: str,
    cusp_11_sign: str,
    mercury_sign: Optional[str] = None,
    mercury_afflicted_by_saturn_mars: bool = False,
    planets_in_5th: Optional[List[str]] = None,
    planets_in_11th: Optional[List[str]] = None,
) -> SpeechAndFertilityPromise:
    """Evaluates speech promise and childbearing fertility according to Reader 2 principles."""
    c2 = cusp_2_sign.strip().title()
    c5 = cusp_5_sign.strip().title()
    c11 = cusp_11_sign.strip().title()

    speech_cond = "Normal"
    speech_reasons: List[str] = []

    # Speech rules (Reader 2 pp. 114)
    if c2 in VOICE_SIGNS:
        speech_cond = "Vocal Gift"
        speech_reasons.append(f"Cusp 2 falls in Voice/Musical sign '{c2}', favoring eloquence and vocal expression.")
    elif c2 in MUTE_SIGNS:
        if mercury_afflicted_by_saturn_mars:
            speech_cond = "Impediment Risk"
            speech_reasons.append(f"Cusp 2 in Mute sign '{c2}' with Mercury afflicted by Saturn/Mars indicates stammer or vocal defect.")
        else:
            speech_reasons.append(f"Cusp 2 in Mute sign '{c2}' suggests reserved, cautious speech.")

    # Fertility rules (Reader 2 pp. 113)
    fertility_reasons: List[str] = []
    is_5_fruitful = c5 in FRUITFUL_SIGNS
    is_11_fruitful = c11 in FRUITFUL_SIGNS
    is_5_barren = c5 in BARREN_SIGNS
    is_11_barren = c11 in BARREN_SIGNS

    if is_5_fruitful and is_11_fruitful:
        fert_promise = "Promised"
        fertility_reasons.append(f"Both 5th ({c5}) and 11th ({c11}) cusps fall in Fruitful watery signs, promising progeny.")
    elif is_5_barren and is_11_barren:
        fert_promise = "Challenging / Barren"
        fertility_reasons.append(f"Both 5th ({c5}) and 11th ({c11}) cusps occupy Barren signs, indicating delays or medical assistance needed.")
    else:
        fert_promise = "Delayed / Mixed"
        fertility_reasons.append(f"5th cusp in '{c5}' and 11th cusp in '{c11}' present semi-fruitful or mixed indications; progeny fructifies through favorable Dasa.")

    if planets_in_5th:
        fertility_reasons.append(f"Planets in 5th house: {', '.join(planets_in_5th)}.")
    if planets_in_11th:
        fertility_reasons.append(f"Planets in 11th house: {', '.join(planets_in_11th)}.")

    return SpeechAndFertilityPromise(
        speech_condition=speech_cond,
        speech_reasons=speech_reasons,
        fertility_promise=fert_promise,
        fertility_reasons=fertility_reasons,
    )


@dataclass
class KarmaEvaluationResult:
    """Categorization of past Karma based on Reader 2 Chapter 10 & 12."""
    karma_type: str                # "Dhruda Karma", "Dhruda-Adhruda Karma", "Adhruda Karma"
    severity_level: str            # "Inexorable / Rigid", "Excusable / Relievable", "Mild / Naturally Blessed"
    mitigation_potential: str      # "Negligible", "High via Shanti / Virtue", "Immediate / Effortless"
    chart_indications: List[str]
    philosophical_counsel: str


def evaluate_karma_category(
    lagna_aspect_from_jupiter_or_9th_lord: bool,
    moon_aspect_from_jupiter_or_9th_lord: bool,
    dasa_lord_aspect_from_jupiter_or_9th_lord: bool,
    jupiter_or_9th_lord_in_lagna_or_moon: bool = False,
) -> KarmaEvaluationResult:
    """Categorizes the operative Karma of the native per Prof. Krishnamurti's doctrine.
    
    Chapter 12:
    - Dhruda Karma: Severe unpardonable past actions. Lacks Jupiter/9th lord benefic aspect.
    - Dhruda-Adhruda Karma: Excusable past actions. Receives Jupiter or 9th lord aspects; prayers/charity mitigate.
    - Adhruda Karma: Thought-only past errors. Jupiter/9th lord in Lagna or with Moon; naturally blessed.
    """
    if jupiter_or_9th_lord_in_lagna_or_moon:
        return KarmaEvaluationResult(
            karma_type="Adhruda Karma",
            severity_level="Mild / Naturally Blessed",
            mitigation_potential="Immediate / Effortless",
            chart_indications=[
                "Jupiter or 9th house lord posited directly in Lagna or conjoined with natal Moon.",
                "Denotes noble deeds in past incarnation leaving negligible negative karmic debt.",
            ],
            philosophical_counsel="The native enjoys peace and fortune with minimal impediments; charitable acts amplify prosperity effortlessly.",
        )
    elif (
        lagna_aspect_from_jupiter_or_9th_lord
        or moon_aspect_from_jupiter_or_9th_lord
        or dasa_lord_aspect_from_jupiter_or_9th_lord
    ):
        return KarmaEvaluationResult(
            karma_type="Dhruda-Adhruda Karma",
            severity_level="Excusable / Relievable",
            mitigation_potential="High via Shanti / Virtue",
            chart_indications=[
                "Lagna, Moon, or Dasa-lord receives benefic aspect from Jupiter or the 9th lord.",
                "Pardonable karmic debts that respond effectively to prayers, medical treatment, and philanthropic service.",
            ],
            philosophical_counsel="Performance of sincere remedial measures (Shanti), selfless charity, and medical care removes suffering and grants peace of mind.",
        )
    else:
        return KarmaEvaluationResult(
            karma_type="Dhruda Karma",
            severity_level="Inexorable / Rigid",
            mitigation_potential="Negligible",
            chart_indications=[
                "Lagna, Moon, and Dasa/Bhukti lords are devoid of protective aspects from Jupiter and 9th lord.",
                "Inexorable past Karma (Avasyam Anubhokthavyam) that must be endured with fortitude.",
            ],
            philosophical_counsel="Patient endurance and spiritual surrender are indicated. While physical circumstances cannot be completely avoided, mental fortitude overcomes distress.",
        )


@dataclass
class FortunaCalculationResult:
    """KP Pars Fortunae calculation and significations (Reader 2 pp. 74-75, 488)."""
    longitude: float               # 0.0 .. 360.0
    sign: str
    sign_lord: str
    star: str
    star_lord: str
    sub_lord: str
    is_day_birth: bool
    formula_used: str
    signification: str


def calculate_kp_fortuna(
    ascendant_deg: float,
    moon_deg: float,
    sun_deg: float,
    is_day_birth: bool,
) -> FortunaCalculationResult:
    """Calculates KP Pars Fortunae (Fortuna) following Prof. Krishnamurti's exact rule.
    
    - Day birth (Sun above horizon / in houses 7-12): Ascendant + Moon - Sun
    - Night birth (Sun below horizon / in houses 1-6): Ascendant + Sun - Moon
    (all normalized to 0..360°)
    """
    from app.services.kp_engine.vedic import point_info

    asc = ascendant_deg % 360.0
    mo = moon_deg % 360.0
    su = sun_deg % 360.0

    if is_day_birth:
        fort_lon = (asc + mo - su) % 360.0
        formula = "Ascendant + Moon - Sun"
    else:
        fort_lon = (asc + su - mo) % 360.0
        formula = "Ascendant + Sun - Moon"

    pinfo = point_info(fort_lon)

    return FortunaCalculationResult(
        longitude=round(fort_lon, 4),
        sign=pinfo.sign,
        sign_lord=pinfo.sign_lord,
        star=pinfo.star,
        star_lord=pinfo.star_lord,
        sub_lord=pinfo.sub_lord,
        is_day_birth=is_day_birth,
        formula_used=formula,
        signification="Pars Fortunae indicates the focal point of material prosperity, sudden gains, and unearned wealth. Transits across this point trigger timely windfalls.",
    )
