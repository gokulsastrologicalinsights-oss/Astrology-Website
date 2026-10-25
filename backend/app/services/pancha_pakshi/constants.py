"""Pancha Pakshi Shastra - Classical Constants and Tables.

Based on Sage Agastya's authentic Pancha Pakshi Shastra (அகத்தியர் பஞ்ச பட்சி சாஸ்திரம்).
Defines the five birds, their elemental correspondences, friendship/enmity matrices,
and the classical day/night activity tables across both Shukla and Krishna Pakshas.
"""

from typing import Dict, Any, List

# The Five Birds of Pancha Pakshi (பஞ்ச பட்சிகள்)
BIRDS: List[Dict[str, Any]] = [
    {
        "id": "vulture",
        "index": 0,
        "name_en": "Vulture / Falcon",
        "name_ta": "வல்லூறு",
        "element_en": "Ether / Space",
        "element_ta": "ஆகாயம்",
        "ruling_planet": "Jupiter",
        "ruling_planet_ta": "குரு",
        "lucky_direction": "North",
        "lucky_direction_ta": "வடக்கு",
        "lucky_color": "Golden Yellow",
        "lucky_color_ta": "மஞ்சள்",
        "symbol": "🦅",
        "friendly_birds": ["Owl"],
        "friendly_birds_ta": ["ஆந்தை"],
        "inimical_birds": ["Peacock"],
        "inimical_birds_ta": ["மயில்"],
        "description_en": "High-altitude vision, sharp focus, decisive executive action, and spiritual wisdom.",
        "description_ta": "உயர்ந்த நோக்கு, தீவிர கவனம், தடையற்ற ஆதிக்கம் மற்றும் ஆன்மீக ஞானம்.",
    },
    {
        "id": "owl",
        "index": 1,
        "name_en": "Owl",
        "name_ta": "ஆந்தை",
        "element_en": "Air",
        "element_ta": "காற்று",
        "ruling_planet": "Venus",
        "ruling_planet_ta": "சுக்கிரன்",
        "lucky_direction": "East",
        "lucky_direction_ta": "கிழக்கு",
        "lucky_color": "White / Pearl",
        "lucky_color_ta": "வெள்ளை",
        "symbol": "🦉",
        "friendly_birds": ["Crow"],
        "friendly_birds_ta": ["காகம்"],
        "inimical_birds": ["Cock"],
        "inimical_birds_ta": ["கோழி"],
        "description_en": "Nocturnal alertness, secret knowledge, intuitive stealth, and artistic wealth.",
        "description_ta": "இரவு விழிப்புணர்வு, மறைபொருள் அறிவு, கூரிய உள்ளுணர்வு மற்றும் கலை வளம்.",
    },
    {
        "id": "crow",
        "index": 2,
        "name_en": "Crow",
        "name_ta": "காகம்",
        "element_en": "Fire",
        "element_ta": "நெருப்பு",
        "ruling_planet": "Sun & Mars",
        "ruling_planet_ta": "செவ்வாய் / சூரியன்",
        "lucky_direction": "South",
        "lucky_direction_ta": "தெற்கு",
        "lucky_color": "Black / Dark Red",
        "lucky_color_ta": "கருப்பு / அடர் சிவப்பு",
        "symbol": "🐦‍⬛",
        "friendly_birds": ["Cock"],
        "friendly_birds_ta": ["கோழி"],
        "inimical_birds": ["Vulture"],
        "inimical_birds_ta": ["வல்லூறு"],
        "description_en": "Social cohesion, vigilance, survival tenacity, shrewd intelligence, and ancestral blessings.",
        "description_ta": "ஒற்றுமை, விழிப்புணர்வு, சூழ்நிலையை வெல்லும் தந்திரம் மற்றும் முன்னோர்களின் ஆசி.",
    },
    {
        "id": "cock",
        "index": 3,
        "name_en": "Cock / Rooster",
        "name_ta": "கோழி",
        "element_en": "Water",
        "element_ta": "நீர்",
        "ruling_planet": "Mercury & Saturn",
        "ruling_planet_ta": "புதன் / சனி",
        "lucky_direction": "West",
        "lucky_direction_ta": "மேற்கு",
        "lucky_color": "Emerald Green",
        "lucky_color_ta": "பச்சை",
        "symbol": "🐓",
        "friendly_birds": ["Peacock"],
        "friendly_birds_ta": ["மயில்"],
        "inimical_birds": ["Owl"],
        "inimical_birds_ta": ["ஆந்தை"],
        "description_en": "Dawn herald, courage, time punctuality, defensive valor, and continuous industry.",
        "description_ta": "விடியலின் தூதுவன், துணிவு, கால உணர்வு, தற்காப்பு வீரம் மற்றும் விடாமுயற்சி.",
    },
    {
        "id": "peacock",
        "index": 4,
        "name_en": "Peacock",
        "name_ta": "மயில்",
        "element_en": "Earth",
        "element_ta": "நிலம்",
        "ruling_planet": "Moon",
        "ruling_planet_ta": "சந்திரன்",
        "lucky_direction": "North-West",
        "lucky_direction_ta": "வடமேற்கு",
        "lucky_color": "Peacock Blue / Multicolor",
        "lucky_color_ta": "நீலம் / பலவண்ணம்",
        "symbol": "🦚",
        "friendly_birds": ["Vulture"],
        "friendly_birds_ta": ["வல்லூறு"],
        "inimical_birds": ["Crow"],
        "inimical_birds_ta": ["காகம்"],
        "description_en": "Beauty, grace, regal presence, spiritual elevation, and divine magnetic attraction.",
        "description_ta": "அழகு, நளினம், ராஜ கம்பீரம், ஆன்மீக மேன்மை மற்றும் வசீகரிக்கும் ஆற்றல்.",
    },
]

BIRD_MAP = {b["id"]: b for b in BIRDS}
BIRD_INDEX_MAP = {b["index"]: b for b in BIRDS}

# The Five Activities (ஐந்து தொழில்கள்)
ACTIVITIES: Dict[str, Dict[str, Any]] = {
    "ruling": {
        "id": "ruling",
        "name_en": "Ruling (Arasu)",
        "name_ta": "அரசு",
        "power_score": 100,
        "nature": "peak_auspicious",
        "color": "#10B981",  # emerald green
        "badge": "100% Peak Power",
        "description_en": "Supreme vigor. All actions undertaken succeed effortlessly. Peak authority, victory, and prosperity.",
        "description_ta": "முழுமையான ஆதிக்க நிலை. தொட்ட காரியங்கள் யாவும் தடையின்றி வெற்றி பெறும் உன்னத நேரம்.",
        "recommended_en": [
            "Signing major agreements, contracts, and deeds",
            "Starting new businesses, ventures, and investments",
            "Meeting government authorities, dignitaries, and patrons",
            "Filing lawsuits, contesting elections, and interviews",
            "Buying gold, properties, vehicles, and taking oaths",
        ],
        "recommended_ta": [
            "முக்கிய ஒப்பந்தங்கள், பத்திரங்கள் கையெழுத்திடுதல்",
            "புதிய தொழில், வியாபாரம் மற்றும் முதலீடுகள் தொடங்குதல்",
            "அரசு அதிகாரிகள், உயர் தலைவர்கள் சந்திப்பு",
            "வழக்கு தொடுத்தல், நேர்காணல் மற்றும் தேர்தல்கள்",
            "தங்கம், சொத்துக்கள், வாகனங்கள் வாங்குதல் மற்றும் பொறுப்பேற்பு",
        ],
        "avoid_en": ["Trivial arguments, idle gossip, giving up advantages"],
        "avoid_ta": ["வீண் வாக்குவாதங்கள், சோம்பல்"],
    },
    "eating": {
        "id": "eating",
        "name_en": "Eating (Oon)",
        "name_ta": "ஊண்",
        "power_score": 80,
        "nature": "highly_auspicious",
        "color": "#3B82F6",  # blue
        "badge": "80% Strong Vitality",
        "description_en": "Nourishing, joyful, and productive state. Fosters financial accumulation, happy meetings, and growth.",
        "description_ta": "ஊட்டமும் மகிழ்ச்சியும் தரும் நிலை. தன வரவு, சுப பேச்சுவார்த்தைகள் மற்றும் வளர்ச்சிக்கு உகந்தது.",
        "recommended_en": [
            "Financial transactions, banking, and receiving money",
            "Family gatherings, matchmaking talks, and dining with allies",
            "Buying clothes, domestic appliances, and fine dining",
            "Learning new knowledge, arts, and educational admissions",
            "Housewarming and moving into a new home",
        ],
        "recommended_ta": [
            "நிதி பரிவர்த்தனைகள், வங்கி நடவடிக்கைகள், வரவுகள்",
            "குடும்ப சுப பேச்சுவார்த்தைகள், விருந்து உபசாரம்",
            "ஆடை, ஆபரணங்கள் மற்றும் வீட்டு உபயோக பொருட்கள் வாங்குதல்",
            "புதிய கல்வி, கலைகள் பயில தொடங்குதல்",
            "புதுமனை புகுதல் மற்றும் சுப விழாக்கள்",
        ],
        "avoid_en": ["Lending large sums without guarantee"],
        "avoid_ta": ["பிணையின்றி பெரிய கடன் தருவது"],
    },
    "walking": {
        "id": "walking",
        "name_en": "Walking (Nadai)",
        "name_ta": "நடை",
        "power_score": 50,
        "nature": "moderate",
        "color": "#F59E0B",  # amber
        "badge": "50% Moderate Movement",
        "description_en": "Dynamic and mobile. Favorable for short journeys, commuting, dynamic communications, and routine works.",
        "description_ta": "இயக்கமும் பயணமும் நிறைந்த நிலை. குறுகிய பயணங்கள் மற்றும் அன்றாடப் பணிகளுக்கு நன்று.",
        "recommended_en": [
            "Commencing business travels, deliveries, and commutes",
            "Routine tasks, outdoor errands, and marketing visits",
            "Athletic workouts, walking, and physical training",
            "Sending proposals, emails, and follow-up communications",
        ],
        "recommended_ta": [
            "பயணங்கள் தொடங்குதல், போக்குவரத்து, வெளியூர் செல்லுதல்",
            "அன்றாட பணிகள், களப் பணிகள், வாடிக்கையாளர் விசிட்",
            "உடற்பயிற்சி, நடைப்பயிற்சி மற்றும் விளையாட்டு",
            "தகவல் தொடர்பு, மின்னஞ்சல் மற்றும் தூது செல்லுதல்",
        ],
        "avoid_en": ["Signing irreversible lifelong pledges"],
        "avoid_ta": ["ஆயுட்கால முக்கிய முடிவுகள் எடுப்பது"],
    },
    "sleeping": {
        "id": "sleeping",
        "name_en": "Sleeping (Thuyil)",
        "name_ta": "துயில்",
        "power_score": 20,
        "nature": "low_vitality",
        "color": "#8B5CF6",  # purple
        "badge": "20% Low Energy / Rest",
        "description_en": "Passive, dormant state. Best for rest, sleep, secret contemplation, meditation, and quiet studies.",
        "description_ta": "ஓய்வும் அமைதியும் தேவைப்படும் நிலை. தியானம், பிரார்த்தனை மற்றும் உறக்கத்திற்கு மட்டுமே உகந்தது.",
        "recommended_en": [
            "Rest, relaxation, sleeping, and body rejuvenation",
            "Private meditation, mantra japa, and quiet study",
            "Visiting holy shrines quietly without worldly intent",
        ],
        "recommended_ta": [
            "ஓய்வு எடுத்தல், தூங்குதல், உடல் நலம் காத்தல்",
            "ரகசிய தியானம், இறை வழிபாடு, அமைதியான வாசிப்பு",
            "கோவில் தரிசனம் அமைதியாக செய்தல்",
        ],
        "avoid_en": [
            "Starting any competitive actions, aggressive debates",
            "Signing business documents or investments",
        ],
        "avoid_ta": [
            "புதிய பணிகள் தொடங்குதல், வாக்குவாதங்கள்",
            "முக்கிய ஆவணங்களில் கையெழுத்திடுதல்",
        ],
    },
    "dying": {
        "id": "dying",
        "name_en": "Dying (Saavu / Padupakshi)",
        "name_ta": "சாவு (படுபட்சி)",
        "power_score": 0,
        "nature": "inauspicious",
        "color": "#EF4444",  # red
        "badge": "0% Critical Warning",
        "description_en": "Defeated / Padupakshi phase. Zero vital immunity. Do NOT initiate new actions, confrontations, or surgeries.",
        "description_ta": "படுபட்சி காலம். பிராண சக்தி முற்றிலும் குறைந்த நேரம். சுப காரியங்கள் முற்றிலுமாக தவிர்க்கப்பட வேண்டும்.",
        "recommended_en": [
            "Remaining patient, quiet, and introspective",
            "Chanting Kuladeivam or protective Kavacha mantras",
            "Submitting to divine will and avoiding rash decisions",
        ],
        "recommended_ta": [
            "அமைதி காத்தல், பொறுமை காத்தல்",
            "குலதெய்வ வழிபாடு மற்றும் கவச பாராயணம்",
            "முக்கியமான எந்த முடிவும் எடுக்காமல் இருத்தல்",
        ],
        "avoid_en": [
            "All auspicious beginnings: weddings, home purchases, launches",
            "Surgeries, litigation, court hearings, lending money",
            "Starting long journeys or engaging in conflicts",
        ],
        "avoid_ta": [
            "அனைத்து சுப காரியங்கள், திருமண பேச்சு, கிரயம்",
            "அறுவை சிகிச்சை, கடன் கொடுத்தல், வாக்குவாதங்கள்",
            "புதிய பயணங்கள் தொடங்குதல்",
        ],
    },
}

# 27 Nakshatras to Birth Bird Map (Janma Pakshi)
# 1: Ashwini .. 27: Revati
SHUKLA_PAKSHA_STAR_BIRD = {
    1: "vulture", 2: "vulture", 3: "vulture", 4: "vulture", 5: "vulture",       # Ashwini to Mrigashira
    6: "owl", 7: "owl", 8: "owl", 9: "owl", 10: "owl", 11: "owl",                # Ardra to P.Phalguni
    12: "crow", 13: "crow", 14: "crow", 15: "crow", 16: "crow",                  # U.Phalguni to Vishakha
    17: "cock", 18: "cock", 19: "cock", 20: "cock", 21: "cock",                  # Anuradha to U.Ashadha
    22: "peacock", 23: "peacock", 24: "peacock", 25: "peacock", 26: "peacock", 27: "peacock",  # Shravana to Revati
}

KRISHNA_PAKSHA_STAR_BIRD = {
    1: "peacock", 2: "peacock", 3: "peacock", 4: "peacock", 5: "peacock",       # Ashwini to Mrigashira
    6: "cock", 7: "cock", 8: "cock", 9: "cock", 10: "cock", 11: "cock",          # Ardra to P.Phalguni
    12: "crow", 13: "crow", 14: "crow", 15: "crow", 16: "crow",                  # U.Phalguni to Vishakha
    17: "owl", 18: "owl", 19: "owl", 20: "owl", 21: "owl",                      # Anuradha to U.Ashadha
    22: "vulture", 23: "vulture", 24: "vulture", 25: "vulture", 26: "vulture", 27: "vulture",  # Shravana to Revati
}

# Classical Agastya Activity Cyclic Order for each bird
# Order of birds: ["vulture", "owl", "crow", "cock", "peacock"]
# Order of activities: ["ruling", "eating", "walking", "sleeping", "dying"]

# Shukla Paksha Daytime Activity Matrix
# Weekday: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
# Each value is a list of 5 activity IDs for Yamams 1..5 for each of the 5 birds
SHUKLA_DAY_TABLE: Dict[int, Dict[str, List[str]]] = {
    # Sunday (6) & Tuesday (1): Vulture starts with Ruling
    6: {
        "vulture": ["ruling", "eating", "walking", "sleeping", "dying"],
        "owl": ["eating", "walking", "sleeping", "dying", "ruling"],
        "crow": ["walking", "sleeping", "dying", "ruling", "eating"],
        "cock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "peacock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    1: {
        "vulture": ["ruling", "eating", "walking", "sleeping", "dying"],
        "owl": ["eating", "walking", "sleeping", "dying", "ruling"],
        "crow": ["walking", "sleeping", "dying", "ruling", "eating"],
        "cock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "peacock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    # Monday (0) & Wednesday (2): Owl starts with Ruling
    0: {
        "owl": ["ruling", "eating", "walking", "sleeping", "dying"],
        "crow": ["eating", "walking", "sleeping", "dying", "ruling"],
        "cock": ["walking", "sleeping", "dying", "ruling", "eating"],
        "peacock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "vulture": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    2: {
        "owl": ["ruling", "eating", "walking", "sleeping", "dying"],
        "crow": ["eating", "walking", "sleeping", "dying", "ruling"],
        "cock": ["walking", "sleeping", "dying", "ruling", "eating"],
        "peacock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "vulture": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    # Thursday (3): Crow starts with Ruling
    3: {
        "crow": ["ruling", "eating", "walking", "sleeping", "dying"],
        "cock": ["eating", "walking", "sleeping", "dying", "ruling"],
        "peacock": ["walking", "sleeping", "dying", "ruling", "eating"],
        "vulture": ["sleeping", "dying", "ruling", "eating", "walking"],
        "owl": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    # Friday (4): Cock starts with Ruling
    4: {
        "cock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "peacock": ["eating", "walking", "sleeping", "dying", "ruling"],
        "vulture": ["walking", "sleeping", "dying", "ruling", "eating"],
        "owl": ["sleeping", "dying", "ruling", "eating", "walking"],
        "crow": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    # Saturday (5): Peacock starts with Ruling
    5: {
        "peacock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "vulture": ["eating", "walking", "sleeping", "dying", "ruling"],
        "owl": ["walking", "sleeping", "dying", "ruling", "eating"],
        "crow": ["sleeping", "dying", "ruling", "eating", "walking"],
        "cock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
}

# Shukla Paksha Nighttime Activity Matrix
SHUKLA_NIGHT_TABLE: Dict[int, Dict[str, List[str]]] = {
    6: {  # Sunday night
        "cock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "peacock": ["ruling", "dying", "walking", "sleeping", "eating"],
        "vulture": ["dying", "walking", "sleeping", "eating", "ruling"],
        "owl": ["walking", "sleeping", "eating", "ruling", "dying"],
        "crow": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    0: {  # Monday night
        "peacock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "vulture": ["ruling", "dying", "walking", "sleeping", "eating"],
        "owl": ["dying", "walking", "sleeping", "eating", "ruling"],
        "crow": ["walking", "sleeping", "eating", "ruling", "dying"],
        "cock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    1: {  # Tuesday night
        "vulture": ["eating", "ruling", "dying", "walking", "sleeping"],
        "owl": ["ruling", "dying", "walking", "sleeping", "eating"],
        "crow": ["dying", "walking", "sleeping", "eating", "ruling"],
        "cock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "peacock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    2: {  # Wednesday night
        "owl": ["eating", "ruling", "dying", "walking", "sleeping"],
        "crow": ["ruling", "dying", "walking", "sleeping", "eating"],
        "cock": ["dying", "walking", "sleeping", "eating", "ruling"],
        "peacock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "vulture": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    3: {  # Thursday night
        "crow": ["eating", "ruling", "dying", "walking", "sleeping"],
        "cock": ["ruling", "dying", "walking", "sleeping", "eating"],
        "peacock": ["dying", "walking", "sleeping", "eating", "ruling"],
        "vulture": ["walking", "sleeping", "eating", "ruling", "dying"],
        "owl": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    4: {  # Friday night
        "cock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "peacock": ["ruling", "dying", "walking", "sleeping", "eating"],
        "vulture": ["dying", "walking", "sleeping", "eating", "ruling"],
        "owl": ["walking", "sleeping", "eating", "ruling", "dying"],
        "crow": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    5: {  # Saturday night
        "peacock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "vulture": ["ruling", "dying", "walking", "sleeping", "eating"],
        "owl": ["dying", "walking", "sleeping", "eating", "ruling"],
        "crow": ["walking", "sleeping", "eating", "ruling", "dying"],
        "cock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
}

# Krishna Paksha Daytime Activity Matrix
KRISHNA_DAY_TABLE: Dict[int, Dict[str, List[str]]] = {
    6: {  # Sunday day: Cock rules Yamam 1
        "cock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "crow": ["eating", "walking", "sleeping", "dying", "ruling"],
        "owl": ["walking", "sleeping", "dying", "ruling", "eating"],
        "vulture": ["sleeping", "dying", "ruling", "eating", "walking"],
        "peacock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    1: {  # Tuesday day: Cock rules Yamam 1
        "cock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "crow": ["eating", "walking", "sleeping", "dying", "ruling"],
        "owl": ["walking", "sleeping", "dying", "ruling", "eating"],
        "vulture": ["sleeping", "dying", "ruling", "eating", "walking"],
        "peacock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    0: {  # Monday day: Owl rules Yamam 1
        "owl": ["ruling", "eating", "walking", "sleeping", "dying"],
        "vulture": ["eating", "walking", "sleeping", "dying", "ruling"],
        "peacock": ["walking", "sleeping", "dying", "ruling", "eating"],
        "cock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "crow": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    2: {  # Wednesday day: Vulture rules Yamam 1
        "vulture": ["ruling", "eating", "walking", "sleeping", "dying"],
        "peacock": ["eating", "walking", "sleeping", "dying", "ruling"],
        "cock": ["walking", "sleeping", "dying", "ruling", "eating"],
        "crow": ["sleeping", "dying", "ruling", "eating", "walking"],
        "owl": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    3: {  # Thursday day: Peacock rules Yamam 1
        "peacock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "cock": ["eating", "walking", "sleeping", "dying", "ruling"],
        "crow": ["walking", "sleeping", "dying", "ruling", "eating"],
        "owl": ["sleeping", "dying", "ruling", "eating", "walking"],
        "vulture": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    4: {  # Friday day: Crow rules Yamam 1
        "crow": ["ruling", "eating", "walking", "sleeping", "dying"],
        "owl": ["eating", "walking", "sleeping", "dying", "ruling"],
        "vulture": ["walking", "sleeping", "dying", "ruling", "eating"],
        "peacock": ["sleeping", "dying", "ruling", "eating", "walking"],
        "cock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
    5: {  # Saturday day: Cock rules Yamam 1
        "cock": ["ruling", "eating", "walking", "sleeping", "dying"],
        "crow": ["eating", "walking", "sleeping", "dying", "ruling"],
        "owl": ["walking", "sleeping", "dying", "ruling", "eating"],
        "vulture": ["sleeping", "dying", "ruling", "eating", "walking"],
        "peacock": ["dying", "ruling", "eating", "walking", "sleeping"],
    },
}

# Krishna Paksha Nighttime Activity Matrix
KRISHNA_NIGHT_TABLE: Dict[int, Dict[str, List[str]]] = {
    6: {  # Sunday night
        "crow": ["eating", "ruling", "dying", "walking", "sleeping"],
        "owl": ["ruling", "dying", "walking", "sleeping", "eating"],
        "vulture": ["dying", "walking", "sleeping", "eating", "ruling"],
        "peacock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "cock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    0: {  # Monday night
        "cock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "crow": ["ruling", "dying", "walking", "sleeping", "eating"],
        "owl": ["dying", "walking", "sleeping", "eating", "ruling"],
        "vulture": ["walking", "sleeping", "eating", "ruling", "dying"],
        "peacock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    1: {  # Tuesday night
        "crow": ["eating", "ruling", "dying", "walking", "sleeping"],
        "owl": ["ruling", "dying", "walking", "sleeping", "eating"],
        "vulture": ["dying", "walking", "sleeping", "eating", "ruling"],
        "peacock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "cock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    2: {  # Wednesday night
        "peacock": ["eating", "ruling", "dying", "walking", "sleeping"],
        "cock": ["ruling", "dying", "walking", "sleeping", "eating"],
        "crow": ["dying", "walking", "sleeping", "eating", "ruling"],
        "owl": ["walking", "sleeping", "eating", "ruling", "dying"],
        "vulture": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    3: {  # Thursday night
        "vulture": ["eating", "ruling", "dying", "walking", "sleeping"],
        "peacock": ["ruling", "dying", "walking", "sleeping", "eating"],
        "cock": ["dying", "walking", "sleeping", "eating", "ruling"],
        "crow": ["walking", "sleeping", "eating", "ruling", "dying"],
        "owl": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    4: {  # Friday night
        "owl": ["eating", "ruling", "dying", "walking", "sleeping"],
        "vulture": ["ruling", "dying", "walking", "sleeping", "eating"],
        "peacock": ["dying", "walking", "sleeping", "eating", "ruling"],
        "cock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "crow": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
    5: {  # Saturday night
        "crow": ["eating", "ruling", "dying", "walking", "sleeping"],
        "owl": ["ruling", "dying", "walking", "sleeping", "eating"],
        "vulture": ["dying", "walking", "sleeping", "eating", "ruling"],
        "peacock": ["walking", "sleeping", "eating", "ruling", "dying"],
        "cock": ["sleeping", "eating", "ruling", "dying", "walking"],
    },
}

# Sub-Activity Cycle Order (அந்தர வரிசை)
# Starting from the main activity of the Yamam, the 5 sub-periods cycle through:
ACTIVITY_CYCLE_ORDER = ["ruling", "eating", "walking", "sleeping", "dying"]
