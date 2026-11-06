"""Bhrigu Nandi Nadi (BNN) Astrology Knowledge Base & Rules Registry.

Formulated from the classical compendium:
"BNN ASTROLOGY NOTES BY PANKAJJ K DUAA"

Encompassing:
- 12 Rashis & House Ownership (Char, Sthir, Upaye / Dwisvabhav)
- Planetary Exaltation & Debilitation (Vedic Pattern & Naadi House Quality Pattern)
- Nadi Planetary Friendship & Enmity Matrix
- Nadi Geometric Aspect Weights (Conjunction, Trine, 2/12, 3/11, 1/7)
- Degree Precision & Chalit Realignment Mechanics
- 12 Bhavas: Karak Tatvas & Cuspal Sub-Lord (CSL) Predictive Combinations
- Medical Astrology Diagnostic Rules & Organ Mappings
- Two-Planet Conjunction Profiles
- Specialized Yogas (Dhan, Property, Progeny, Sibling, Berozgari, Marriage, Jail, Politics)
- Comprehensive Remedial Science (Rudrakshas, Mantras, Dana, Taboos & Life Maxims)
"""

from typing import Dict, Any, List

BNN_PANKAJJ_DUAA_METADATA: Dict[str, Any] = {
    "title": "BNN Astrology Notes by Pankajj K Duaa",
    "title_ta": "பங்கஜ் கே துவா அவர்களின் பிருகு நந்தி நாடி ஜோதிட விதிகள்",
    "author": "Pankajj K Duaa",
    "traditions": ["Bhrigu Nandi Nadi (BNN)", "Krishnamurti Paddhati (KP)", "Vedic Parashari", "Lal Kitab"],
    "summary_en": (
        "Comprehensive synthesis of Pankajj K Duaa's BNN teachings combining planetary karakatwas, "
        "Naadi house qualities irrespective of signs, directional trines, degree movements, "
        "CSL event combinations, medical diagnosis by organ and gender-differentiated life significators "
        "(Jupiter for men, Venus for women), two-planet combination profiles, and specific Lal Kitab/Vedic remedies."
    ),
    "summary_ta": (
        "பங்கஜ் கே துவா அவர்களின் பிருகு நந்தி நாடி முறை: காரக தத்துவங்கள், ராசி சாரா பாவ பலன்கள், "
        "திசை திரிகோணங்கள், பாகை வினைகள், கே.பி. உப-அதிபதி விதிகள், மருத்துவ ஜோதிடம், "
        "ஆண்களுக்கு குரு மற்றும் பெண்களுக்கு சுக்கிரன் ஜீவ காரக நிர்ணயம், இரு கிரக சேர்க்கை பலன்கள் மற்றும் பரிகாரங்கள்."
    ),
}

# ---------------------------------------------------------------------------
# 1. 12 Rashis & House Ownership
# ---------------------------------------------------------------------------
BNN_RASHI_MOBILITY: Dict[int, Dict[str, Any]] = {
    1: {"name_en": "Aries", "name_hi": "Mesh", "name_ta": "மேஷம்", "mobility": "Char (Movable)", "lord": "Mars", "element": "Fire", "direction": "East"},
    2: {"name_en": "Taurus", "name_hi": "Vrishab", "name_ta": "ரிஷபம்", "mobility": "Sthir (Fixed)", "lord": "Venus", "element": "Earth", "direction": "South"},
    3: {"name_en": "Gemini", "name_hi": "Mithun", "name_ta": "மிதுனம்", "mobility": "Upaye / Dwisvabhav (Dual)", "lord": "Mercury", "element": "Air", "direction": "West"},
    4: {"name_en": "Cancer", "name_hi": "Kark", "name_ta": "கடகம்", "mobility": "Char (Movable)", "lord": "Moon", "element": "Water", "direction": "North"},
    5: {"name_en": "Leo", "name_hi": "Singh", "name_ta": "சிம்மம்", "mobility": "Sthir (Fixed)", "lord": "Sun", "element": "Fire", "direction": "East"},
    6: {"name_en": "Virgo", "name_hi": "Kanya", "name_ta": "கன்னி", "mobility": "Upaye / Dwisvabhav (Dual)", "lord": "Mercury", "element": "Earth", "direction": "South"},
    7: {"name_en": "Libra", "name_hi": "Tula", "name_ta": "துலாம்", "mobility": "Char (Movable)", "lord": "Venus", "element": "Air", "direction": "West"},
    8: {"name_en": "Scorpio", "name_hi": "Vrischik", "name_ta": "விருச்சிகம்", "mobility": "Sthir (Fixed)", "lord": "Mars", "element": "Water", "direction": "North"},
    9: {"name_en": "Sagittarius", "name_hi": "Dhanu", "name_ta": "தனுசு", "mobility": "Upaye / Dwisvabhav (Dual)", "lord": "Jupiter", "element": "Fire", "direction": "East"},
    10: {"name_en": "Capricorn", "name_hi": "Makar", "name_ta": "மகரம்", "mobility": "Char (Movable)", "lord": "Saturn", "element": "Earth", "direction": "South"},
    11: {"name_en": "Aquarius", "name_hi": "Kumbh", "name_ta": "கும்பம்", "mobility": "Sthir (Fixed)", "lord": "Saturn", "element": "Air", "direction": "West"},
    12: {"name_en": "Pisces", "name_hi": "Meen", "name_ta": "மீனம்", "mobility": "Upaye / Dwisvabhav (Dual)", "lord": "Jupiter", "element": "Water", "direction": "North"},
}

# ---------------------------------------------------------------------------
# 2. Exaltation & Debilitation (Vedic & Naadi House Quality Pattern)
# ---------------------------------------------------------------------------
BNN_VEDIC_UCCH_NEECH: Dict[str, Dict[str, Any]] = {
    "Sun": {"ucch_sign": 1, "neech_sign": 7, "ucch_name": "Aries", "neech_name": "Libra"},
    "Moon": {"ucch_sign": 2, "neech_sign": 8, "ucch_name": "Taurus", "neech_name": "Scorpio"},
    "Mars": {"ucch_sign": 10, "neech_sign": 4, "ucch_name": "Capricorn", "neech_name": "Cancer"},
    "Mercury": {"ucch_sign": 6, "neech_sign": 12, "ucch_name": "Virgo", "neech_name": "Pisces"},
    "Jupiter": {"ucch_sign": 4, "neech_sign": 10, "ucch_name": "Cancer", "neech_name": "Capricorn"},
    "Venus": {"ucch_sign": 12, "neech_sign": 6, "ucch_name": "Pisces", "neech_name": "Virgo"},
    "Saturn": {"ucch_sign": 7, "neech_sign": 1, "ucch_name": "Libra", "neech_name": "Aries"},
    "Rahu": {"ucch_sign": 3, "neech_sign": 9, "ucch_name": "Gemini", "neech_name": "Sagittarius"},
    "Ketu": {"ucch_sign": 9, "neech_sign": 3, "ucch_name": "Sagittarius", "neech_name": "Gemini"},
}

BNN_NAADI_HOUSE_QUALITY: Dict[str, Dict[str, List[int]]] = {
    "Sun": {
        "good": [1, 2, 3, 4, 5, 9, 10, 11],
        "very_bad": [7],
        "mix": [6, 8, 12],
    },
    "Moon": {
        "good": [1, 2, 3, 4, 5, 7, 9, 10, 11],
        "very_bad": [6, 8, 12],
        "mix": [],
    },
    "Mars": {
        "good": [1, 2, 5, 6, 9, 10, 11, 12],
        "very_bad": [3, 4, 8],
        "mix": [7],  # Spousal arguments
    },
    "Venus": {
        "good": [1, 2, 3, 4, 5, 7, 9, 10, 11, 12],
        "very_bad": [],
        "mix": [6, 8],
    },
    "Mercury": {
        "good": [1, 2, 5, 6, 7, 9, 10, 11],
        "very_bad": [3, 12],
        "mix": [4, 8],
    },
    "Jupiter": {
        "good": [1, 2, 3, 4, 5, 7, 9, 11, 12],
        "very_bad": [6, 8],
        "mix": [10],
    },
    "Saturn": {
        "good": [2, 3, 5, 6, 9, 10, 11],
        "very_bad": [1, 8, 9],
        "mix": [4, 7, 12],
    },
    "Rahu": {
        "good": [3, 6, 10, 11],
        "very_bad": [1, 2, 8, 9, 12],
        "mix": [4, 5, 7],
    },
    "Ketu": {
        "good": [2, 5, 9, 10, 11, 12],
        "very_bad": [3, 6, 8],
        "mix": [1, 4, 7],
    },
}

# ---------------------------------------------------------------------------
# 3. Nadi Planetary Friendship & Enmity Matrix
# ---------------------------------------------------------------------------
BNN_PANKAJJ_FRIENDSHIP: Dict[str, Dict[str, List[str]]] = {
    "Sun": {
        "friends": ["Moon", "Jupiter", "Mars", "Mercury"],
        "enemies": ["Rahu", "Ketu", "Saturn"],
        "neutral": ["Venus"],
    },
    "Moon": {
        "friends": ["Sun", "Jupiter", "Mars"],
        "enemies": ["Mercury", "Rahu", "Ketu", "Saturn", "Venus"],
        "neutral": [],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter", "Venus"],
        "enemies": ["Rahu", "Ketu", "Saturn", "Mercury"],
        "neutral": [],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars", "Saturn"],
        "enemies": ["Rahu", "Ketu"],
        "neutral": ["Mercury"],
    },
    "Mercury": {
        "friends": ["Sun", "Saturn", "Rahu", "Venus"],
        "enemies": ["Ketu", "Moon", "Mars"],
        "neutral": ["Jupiter"],
    },
    "Venus": {
        "friends": ["Mercury", "Saturn", "Jupiter", "Rahu"],
        "enemies": ["Moon", "Ketu"],
        "neutral": ["Sun", "Mars"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus", "Jupiter"],
        "enemies": ["Sun", "Rahu", "Ketu", "Moon", "Mars"],
        "neutral": [],
    },
    "Rahu": {
        "friends": ["Mercury"],  # If together, risks prison if doing illegal work
        "enemies": ["Sun", "Moon", "Mars", "Jupiter", "Venus", "Saturn", "Ketu"],
        "neutral": [],
    },
    "Ketu": {
        "friends": [],  # Ketu has no friends; all planets are considered enemies/severed
        "enemies": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"],
        "neutral": [],
    },
}

# ---------------------------------------------------------------------------
# 4. Aspect & Connection Geometry in BNN
# ---------------------------------------------------------------------------
BNN_ASPECT_WEIGHTS: Dict[str, Dict[str, Any]] = {
    "conjunction": {
        "houses": [0],
        "percentage": 100,
        "description_en": "Same house placement: 100% complete fusion of planetary karakatwas.",
        "description_ta": "ஒரே ராசியில் இணைவு: 100% முழுமையான காரக சேர்க்கை.",
    },
    "trine": {
        "houses": [1, 5, 9],
        "percentage": 75,
        "description_en": "Trinal directional harmony (1, 5, 9): 75% connection.",
        "description_ta": "திசை திரிகோண சேர்க்கை (1, 5, 9): 75% காரக தொடர்பு.",
    },
    "padosi_2_12": {
        "houses": [2, 12],
        "percentage_forward": 90,
        "percentage_backward": 25,
        "description_en": "Adjacent houses (2/12): 90% forward clockwise momentum, 25% backward reflection.",
        "description_ta": "2/12 அண்டை வீடுகள்: முன்னோக்கி 90%, பின்னோக்கி 25% காரக தாக்கம்.",
    },
    "hexagonal_3_11": {
        "houses": [3, 11],
        "percentage": 25,
        "description_en": "3/11 connection: 20% to 30% subtle auxiliary influence.",
        "description_ta": "3/11 தொடர்பு: 20% முதல் 30% வரையிலான உப பலன்.",
    },
    "opposition_1_7": {
        "houses": [7],
        "percentage": 50,
        "description_en": "Direct 1/7 mutual aspect: 50% reciprocal energetic interaction.",
        "description_ta": "நேரெதிர் 1/7 பார்வை: 50% சமசப்தம பார்வை பலன்.",
    },
}

# ---------------------------------------------------------------------------
# 5. Degree Precision & Chalit Realignment Rules
# ---------------------------------------------------------------------------
BNN_DEGREE_RULES: Dict[str, Any] = {
    "zodiac_progression": (
        "All planets move clockwise from 0 to 30 degrees across signs, except Rahu and Ketu "
        "which move strictly anticlockwise from 30 degrees to 0 degrees, entering at 30 and exiting at 0."
    ),
    "cusp_border_forward": (
        "Any direct planet (except Rahu/Ketu) situated between 27 and 30 degrees gives the complete "
        "results of the subsequent (next) house as well."
    ),
    "cusp_border_backward": (
        "Any direct planet (except Rahu/Ketu) situated between 0 and 3 degrees reflects and gives "
        "the results of the preceding (previous) house as well."
    ),
    "retrograde_mechanics": (
        "Retrograde planets (Mars, Mercury, Jupiter, Venus, Saturn) traverse in reverse; "
        "if retrograde at 27-30 degrees or 0-3 degrees, they cast their primary results into the previous house."
    ),
    "chalit_shift_mandate": (
        "Always cross-examine planet placements in Bhava Chalit; if a planet shifts houses in Chalit, "
        "apply its house results accordingly."
    ),
}

# ---------------------------------------------------------------------------
# 6. Medical Astrology Rules (Pankajj K Duaa System)
# ---------------------------------------------------------------------------
BNN_MEDICAL_ASTROLOGY_RULES: Dict[str, Any] = {
    "house_anatomical_map": {
        1: {"en": "Upper neck area, skull, and nose", "ta": "மண்டை ஓடு, மேல் கழுத்து மற்றும் மூக்கு"},
        2: {"en": "Neck, right eye, throat, oral cavity", "ta": "கழுத்து, வலது கண், தொண்டை, வாய்"},
        3: {"en": "Shoulders, hands, arms, right ear, respiratory tract", "ta": "தோள்பட்டை, கைகள், வலது காது, சுவாசக் குழாய்"},
        4: {"en": "Heart, lungs, chest, thoracic spine behind lungs", "ta": "இதயம், நுரையீரல்கள், மார்புப் பகுதி"},
        5: {"en": "Stomach, upper abdomen, navel, lumbar spine behind navel", "ta": "வயிறு, மேல் வயிறு, தொப்புள், முதுகுத் தண்டு"},
        6: {"en": "Lower abdomen, intestines, lower spine", "ta": "அடிவயிறு, குடல் பகுதிகள்"},
        7: {"en": "Private generative organs, prostate, rectum, anal fissures", "ta": "அந்தரங்க உறுப்புகள், புரோஸ்டேட், மலக்குடல்"},
        8: {"en": "External genitalia, excretory systems, testicles", "ta": "பாலியல் உறுப்புகள், விரைப்பை"},
        9: {"en": "Thighs, femoral arteries", "ta": "தொடைகள், இடுப்பு எலும்புகள்"},
        10: {"en": "Knees, patellar joints", "ta": "முழங்கால்கள்"},
        11: {"en": "Calf muscles, shins, left ear", "ta": "கால் முட்டிக்கு கீழ் தசை, இடது காது"},
        12: {"en": "Feet, ankles, left eye", "ta": "பாதங்கள், இடது கண்"},
    },
    "golden_rule_two_enemies": (
        "If two or more enemy planets occupy a single house, the physiological organ governed by that "
        "house will suffer chronic pathology, surgical trauma, or functional failure."
    ),
    "life_significator_rules": {
        "male": {
            "prime_karaka": "Jupiter",
            "principle_en": "In men, Jupiter is the prime significator of life force, breath, and vitality.",
            "principle_ta": "ஆண்களுக்கு குரு பகவானே ஜீவ காரகர் (உயிர் மற்றும் ஆரோக்கியக் காரகர்).",
            "afflictions": "Jupiter in 6th/8th house, or Jupiter conjoined with Rahu or Ketu causes recurrent health crises.",
        },
        "female": {
            "prime_karaka": "Venus",
            "secondary_karaka": "Jupiter",
            "principle_en": "In women, Venus is the prime significator of life force and vitality; Jupiter is secondary.",
            "principle_ta": "பெண்களுக்கு சுக்கிர பகவானே முதன்மை ஜீவ காரகர்; குரு இரண்டாம் நிலை காரகர்.",
            "afflictions": "Venus afflicted by Rahu, Ketu, Moon, or placed in 6th/8th house causes chronic female health disorders.",
        },
    },
    "planetary_diseases": {
        "Sun": {
            "organs": "Bones, heart, gall bladder, right eye, touchable brain cortex",
            "pathologies": "Acidity, head injury, migraine, fevers, cardiac stress",
            "triggers": "Sun with Rahu, Ketu, or Saturn; or Sun placed in 6th, 7th, or 8th house",
        },
        "Moon": {
            "organs": "Lungs, untouchable brain (subconscious mind), fluid metabolism",
            "pathologies": "Asthma, sinusitis, clinical depression, severe mental disorders, anxiety",
            "triggers": "Moon in 6th, 8th, or 12th; Moon with Rahu, Ketu, or Saturn; Moon+Lagna afflicted (sinus); Moon+4th+5th afflicted (depression)",
        },
        "Mars": {
            "organs": "Muscular tissue, blood, arterial flow, teeth, female ovaries/eggs",
            "pathologies": "Accidents, surgical operations, blood infections, high BP (Mars+Rahu), erratic BP (Mars+Ketu), PCOD, uterine bleeding",
            "triggers": "Mars in 3rd, 4th, or 8th; Mars connected with Rahu, Ketu, or Mercury",
        },
        "Jupiter": {
            "organs": "Lungs (cellular oxygenation), nasal breath, liver, thyroid gland, adipose tissue",
            "pathologies": "Breathing difficulties, asthma, obesity, fatty liver, diabetes mellitus, tumors",
            "triggers": "Jupiter in 6th or 8th; Jupiter conjoined with Rahu or Ketu",
        },
        "Venus": {
            "organs": "Renal system, kidneys, private generative organs, sperm count in males, cheeks",
            "pathologies": "Kidney stones, urinary tract disorders, childbirth complications, ovarian cysts",
            "triggers": "Venus in 6th or 8th; Venus conjoined with Rahu, Ketu, or Moon",
        },
        "Mercury": {
            "organs": "Central nervous system, skin, auditory canals, memory, sense of smell",
            "pathologies": "Depression, skin eruptions, amnesia, stuttering, suicidal tendencies (in 4th), severe depression (in 12th)",
            "triggers": "Mercury+Mars (depression), Mercury+Moon (confusion), Mercury+Ketu (brain issues), Mercury in 3, 4, 8, 12",
        },
        "Saturn": {
            "organs": "Skeletal structure, alimentary canal in stomach, spinal column, nervous system",
            "pathologies": "Chronic long-term diseases, severe acidity/GERD, leg paralysis, rheumatoid arthritis",
            "triggers": "Saturn afflicted by Sun, Mars, Rahu, or Ketu; placed in 1st, 8th, or 12th",
        },
        "Rahu": {
            "organs": "Intestines, pelvic cavity, bowels, cellular mutation",
            "pathologies": "Allergies, chronic constipation, anal fissures, piles, sleep disorders/insomnia, malignant tumors",
            "triggers": "Rahu in 7th or 8th causes private organ disorders; Rahu + Saturn connection triggers Cancer Yoga",
        },
        "Ketu": {
            "organs": "Prostate, urinary tract, sensory nerve endings, auditory canals",
            "pathologies": "Urinary blockage, prostate hypertrophy, unidentified bodily cysts, surgical scars, back and leg pains",
            "triggers": "Ketu in 3rd, 6th, 8th; or in 7th/8th (genital ailments)",
        },
    },
    "cancer_yoga": {
        "formula": "Saturn connected with Rahu in any manner (conjunction, trine, 1/7 opposition, or mutual aspect)",
        "reading_en": "Saturn-Rahu connection creates cellular mutations and predisposition to malignant tumors/Cancer.",
        "reading_ta": "சனியும் ராகுவும் எவ்வகையிலேனும் இணைந்தால் (சேர்க்கை, பார்வை, திரிகோணம்) அது புற்றுநோய் (Cancer) அபாயத்தைக் குறிக்கும்.",
    },
}

# ---------------------------------------------------------------------------
# 7. Two-Planet Combinations (Conjunction Profiles)
# ---------------------------------------------------------------------------
BNN_PLANET_PAIR_COMBINATIONS: Dict[str, Dict[str, Any]] = {
    "Sun_Moon": {
        "en": "Father is emotional, mobile, has mood swings; mother has executive temperament, anger, or government service.",
        "ta": "தந்தை உணர்ச்சிவசப்படக்கூடியவர், பயணப்பிரியர்; தாய் அதிகார சுபாவம், கோபம் அல்லது அரசுப் பணி தொடர்புடையவர்.",
    },
    "Sun_Mars": {
        "en": "Father is quarrelsome, dominant, owns landed estate; spouse or younger brother holds government/uniformed job with fierce temper.",
        "ta": "தந்தை ஆதிக்க குணம், பூமி-நிலம் உள்ளவர்; கணவன் அல்லது தம்பி அரசுப் பணி/சீருடைப் பணி மற்றும் முன்கோபம் கொண்டவர்.",
    },
    "Sun_Mercury": {
        "en": "Father is an astute merchant, landholder, teacher, or astrologer; sister or aunt holds high intelligence and government status.",
        "ta": "தந்தை புத்திசாலி வியாபாரி, நிலச்சுவாந்தார், ஆசிரியர் அல்லது ஜோதிடர்; சகோதரி அல்லது அத்தை அரசு செல்வாக்கு கொண்டவர்.",
    },
    "Sun_Jupiter": {
        "en": "Father is a respected banker, doctor, judge, or counselor with sound bank balance; native is egoistic, dignified, and enjoys state honor.",
        "ta": "தந்தை வங்கி, மருத்துவம், நீதித்துறை அல்லது கௌரவப் பதவியில் உள்ளவர்; ஜாதகர் கம்பீரமான ஆளுமை மற்றும் அரசு மரியாதை பெறுவார்.",
    },
    "Sun_Venus": {
        "en": "Father possesses wealth, luxury cars, and artistic taste; spouse is proud, egoistic, and may hold government or administrative office.",
        "ta": "தந்தை செல்வந்தர், நிலம் மற்றும் வாகன யோகம் உள்ளவர்; மனைவி கௌரவமிக்கவர், அரசுப் பணி அல்லது நிர்வாக அதிகாரம் உள்ளவர்.",
    },
    "Sun_Saturn": {
        "en": "Exclusive Government Job Yoga (never engage in private speculation); father suffers leg pains, serves in judiciary/law; elder brother is harsh.",
        "ta": "அரசுப் பணி யோகம் (தனியார் வர்த்தகம் தவிர்க்கவும்); தந்தை கால் வலி அல்லது சட்டத்துறையில் இருப்பார்; அண்ணனுடன் கருத்து வேறுபாடு.",
    },
    "Sun_Rahu": {
        "en": "Pitru Dosha; father faces intense struggles, defamation, police/court matters, or eye trouble; paternal grandfather had government ties.",
        "ta": "பித்ரு தோஷம்; தந்தை பல போராட்டங்கள், அவப்பெயர் அல்லது கண் உபாதைகளை சந்திப்பார்; பாட்டனார் அரசுத் தொடர்பு கொண்டவர்.",
    },
    "Sun_Ketu": {
        "en": "Sovereign Banner Yoga (Raja + Jhanda) ideal for apex leadership/government; father may face cardiac/gallbladder issues or spiritual detachment.",
        "ta": "அரசாங்கக் கொடி யோகம் (ராஜ யோகம்); தலைமைப் பதவிக்கு உன்னதமானது; தந்தைக்கு இதய/பித்தப்பை கோளாறுகள் அல்லது ஆன்மீக நாட்டம்.",
    },
    "Moon_Mars": {
        "en": "Mother undergoes surgeries, injuries, or owns land; spouse or younger brother faces mental restlessness and frequent relocations.",
        "ta": "தாயாருக்கு அறுவை சிகிச்சை அல்லது நில யோகம்; கணவன் அல்லது தம்பி மன அமைதியற்ற அலைச்சல் மற்றும் இடமாற்றம் காண்பார்.",
    },
    "Moon_Mercury": {
        "en": "Native prone to skin sensitivity or social gossip; mother is scholarly, business-minded, or an astrologer; female relatives bear names like 'Rani'.",
        "ta": "தோல் ஒவ்வாமை அல்லது வதந்திகள்; தாய் கல்வியறிவு, வியாபாரம் அல்லது ஜோதிட ஆர்வம் உள்ளவர்; பெண் உறவினர்கள் 'ராணி' எனப் பெயர்பெறுவர்.",
    },
    "Moon_Jupiter": {
        "en": "Gajakesari-type counselor; native is sensitive to cold, serves as an exceptional advisor; mother is righteous, pious, banker, or magistrate.",
        "ta": "உயர்ந்த ஆலோசகர்; சளி பிடிக்கும் உடல்வாகு; தாய் தர்ம சிந்தனை, பக்தி, வங்கி அல்லது ஆசிரியர் பணி தொடர்புடையவர்.",
    },
    "Moon_Venus": {
        "en": "Native takes residential property loan; discord among sisters (Moon+Venus sisters cannot harmonize); if within 3 deg, risk of female-related defamation.",
        "ta": "வீட்டுக் கடன் வாங்குவர்; சகோதரிகளுக்குள் தீவிர கருத்து வேறுபாடு (சந்திரன்-சுக்கிரன் இணைந்தால் அக்கா-தங்கைக்குள் ஒத்து வராது); அவப்பெயர் எச்சரிக்கை.",
    },
    "Moon_Saturn": {
        "en": "Visha Yoga (Poison Yoga); native suffers recurring mental anxiety; mother suffers chronic leg pain and hardships; career experiences sea tides.",
        "ta": "விஷ யோகம்; தீவிர மன உளைச்சல், தாய் வழி கருத்து வேறுபாடு; தாயாருக்கு கால் வலி மற்றும் உழைப்பு; தொழிலில் ஏற்ற இறக்கங்கள்.",
    },
    "Moon_Rahu": {
        "en": "Mother travels overseas, enters politics, or visits courts; paternal grandfather was nomadic, emotional, or engaged in water-related work.",
        "ta": "தாய் வெளிநாட்டுப் பயணம், அரசியல் அல்லது வழக்குத் தொடர்பு; தந்தை வழி பாட்டனார் உணர்ச்சிவசப்படக்கூடிய அலைச்சல் பிரியர்.",
    },
    "Moon_Ketu": {
        "en": "Deep mental isolation / depression; mother is deeply spiritual or undergoes operations (piles/fistula) or maternal estrangement.",
        "ta": "மன அழுத்தம் மற்றும் தனிமை; தாய் தீவிர ஆன்மீகவாதி அல்லது அறுவை சிகிச்சை (மூலம்/பிஸ்டுலா) சந்திப்பார் அல்லது தாயன்பு குறைவு.",
    },
    "Mars_Mercury": {
        "en": "Mercury locks Mars's courage; hesitation, education breaks; spouse/brother is an educated merchant owning land. Jupiter+Mars+Mercury = 2 lands.",
        "ta": "புதன் செவ்வாயின் தைரியத்தை பூட்டுகிறார்; கல்வித் தடை, வியாபார மந்தம்; கணவன்/தம்பி நிலம் உள்ள வியாபாரி. குரு+செவ்வாய்+புதன் = 2 நிலங்கள்.",
    },
    "Mars_Jupiter": {
        "en": "Younger brother guaranteed; spouse or brother is a righteous advisor, doctor, or magistrate; native owns landed property.",
        "ta": "நிச்சயமாக இளைய சகோதரன் உண்டு; கணவன் அல்லது தம்பி கௌரவமான மருத்துவர், நீதிபதி அல்லது ஆலோசகர்; நில யோகம்.",
    },
    "Mars_Venus": {
        "en": "Colonizer Yoga; native acquires maximal landed properties; passionate romantic marriage (unless severed by Ketu).",
        "ta": "ரியல் எஸ்டேட் காலனைசர் யோகம்; அதிக நிலபுலன்கள் சேரும்; தீவிர காதல் திருமணம் (கேதுவின் தொடர்பு இல்லாவிடில்).",
    },
    "Mars_Saturn": {
        "en": "Brotherly discord (brothers cannot harmonize); prone to physical accidents, blood pressure shifts, low hemoglobin; mechanical/civil engineer or police.",
        "ta": "சகோதர ஒற்றுமையின்மை (அண்ணன்-தம்பிக்குள் ஒத்து வராது); விபத்து, ரத்த அழுத்தம், ஹீமோகுளோபின் குறைவு; எந்திரவியல், சிவில் அல்லது காவல்துறை.",
    },
    "Mars_Rahu": {
        "en": "Spouse or younger brother faces struggles, relocates abroad, or plays domestic politics; paternal grandfather was fierce and owned land.",
        "ta": "கணவன் அல்லது தம்பியின் வாழ்வில் போராட்டங்கள், வெளிநாடு அல்லது வீட்டு அரசியல்; பாட்டனார் கோபக்கார நிலச்சுவாந்தார்.",
    },
    "Mars_Ketu": {
        "en": "Strict Prohibition: NEVER take or give monetary loans in life. Prone to blood infection, surgeries, root canals; spouse/brother in law/medicine.",
        "ta": "கடுமையான எச்சரிக்கை: ஆயுளில் கடன் வாங்கவோ கொடுக்கவோ கூடாது! ரத்தத் தொற்று, அறுவை சிகிச்சை, பல் ரூட் கெனால்; கணவன்/தம்பி சட்டம் அல்லது மருத்துவர்.",
    },
    "Mercury_Jupiter": {
        "en": "Lifelong learner; immense wisdom; native owns land, excels in commerce; prominent combination among professional astrologers.",
        "ta": "ஆயுள் முழுவதும் கற்கும் வித்தை; அபார அறிவு; நில யோகம்; வர்த்தக வெற்றி; ஜோதிட மேதைகளிடம் காணப்படும் உன்னத சேர்க்கை.",
    },
    "Mercury_Venus": {
        "en": "Vishnu-Lakshmi Yoga; native acquires one house and one piece of land; sweet persuasive voice, wealth through mercantile business.",
        "ta": "விஷ்ணு-லட்சுமி யோகம்; ஒரு வீடு மற்றும் ஒரு நிலம் நிச்சயமாக அமையும்; இனிமையான வாக்குவன்மை, வர்த்தக ரீதியான பெருஞ்செல்வம்.",
    },
    "Mercury_Saturn": {
        "en": "Slow learner in early youth, dental aches, ear sensitivity; younger sister faces marriage delay; paternal relatives are shrewd merchants.",
        "ta": "ஆரம்பக் கல்வியில் மந்தம், பல் வலி, காது வலி; தங்கை திருமணம் தாமதம்; தந்தை வழி உறவினர்கள் சாமர்த்தியமான வியாபாரிகள்.",
    },
    "Mercury_Rahu": {
        "en": "Warning: Do not engage in illegal commerce (leads to jail); IT multi-nationals, telecom, call centers, multi-lingual mimicry, multiple lands.",
        "ta": "எச்சரிக்கை: சட்டவிரோத செயல்கள் செய்தால் சிறை தண்டனை; பன்னாட்டு ஐடி நிறுவனம், தகவல் தொடர்பு, பல மொழிகள் பேசும் திறன், பல நிலங்கள்.",
    },
    "Mercury_Ketu": {
        "en": "Stuttering/speech impediments, ear pain, litigation disputes; maternal relatives in astrology, law, pharmacy, or surgery.",
        "ta": "திக்குவாய்/பேச்சுத் தடை, காது வலி, கோர்ட் கேஸ்; தாய்மாமன் ஜோதிடர், வழக்கறிஞர், மருந்து அல்லது அறுவை சிகிச்சை நிபுணர்.",
    },
    "Jupiter_Venus": {
        "en": "Crorepati Yoga; native acquires immense wealth; spouse is a banker, financier, teacher, or counselor; native owns at least one house.",
        "ta": "கோடீஸ்வர யோகம்; அபரிமிதமான செல்வச் சேர்க்கை; மனைவி வங்கி, நிதித்துறை, ஆசிரியர் அல்லது ஆலோசகர்; ஒரு வீடு சொந்தமாக அமையும்.",
    },
    "Jupiter_Saturn": {
        "en": "Elder brother guaranteed; native is lucky, clever, enjoys lifelong employment stability (Dharmakarmadhipati); paternal uncles are learned.",
        "ta": "நிச்சயமாக மூத்த சகோதரன் உண்டு; புத்திசாலி, அதிர்ஷ்டசாலி, வாழ்நாள் முழுவதும் கைநிறைய தொழில் யோகம்; பெரியப்பா/சித்தப்பா அறிஞர்கள்.",
    },
    "Jupiter_Rahu": {
        "en": "Guru Chandal Yoga; native travels abroad, handles optical/camera devices, has digestive/liver vulnerability; grandfather was a high scholar.",
        "ta": "குரு சண்டாள யோகம்; வெளிநாட்டுப் பயணம், கேமரா/தொழினுட்ப ஆர்வம், கல்லீரல்/வயிற்று உபாதை; பாட்டனார் மிக உயர்ந்த கல்வியாளர்.",
    },
    "Jupiter_Ketu": {
        "en": "If Ketu is in 12th from Jupiter, native has no elder siblings. Ascetic nature, doctor, astrologer, occultist; liver trouble or pregnancy termination.",
        "ta": "குருவுக்கு 12-ல் கேது இருந்தால் மூத்த சகோதரர் இருக்க மாட்டார்; துறவி சுபாவம், மருத்துவர், ஜோதிடர்; கல்லீரல் கோளாறு அல்லது கருச்சிதைவு.",
    },
    "Venus_Saturn": {
        "en": "Delays marriage but grants lasting stability; spouse suffers leg pain; native's house will be older construction; deep intuitive grasp of BNN.",
        "ta": "திருமணம் தாமதமாகும் ஆனால் நிலைக்கும்; மனைவிக்கு கால் வலி; பழைய பாரம்பரிய வீடு; பிருகு நந்தி நாடி சாஸ்திரத்தில் அபார தேர்ச்சி.",
    },
    "Venus_Rahu": {
        "en": "Multiple spacious properties; spousal secret reproductive ailments; money acquired through salesmanship, persuasive speech, or foreign ties.",
        "ta": "பல பிரம்மாண்ட வீடுகள் மற்றும் நிலங்கள்; மனைவிக்கு அந்தரங்க ஆரோக்கிய உபாதைகள்; சாமர்த்திய பேச்சு, மார்க்கெட்டிங் மூலம் தனலாபம்.",
    },
    "Venus_Ketu": {
        "en": "House located at corner or in street lane; STRICT WARNING: Never lend money to anyone; lifelong financial tightness easing after maturity.",
        "ta": "வீடு முட்டுச்சந்து அல்லது மூலையில் அமையும்; கடுமையான எச்சரிக்கை: யாருக்கும் கடன் கொடுக்கக் கூடாது; நடுத்தர வயதுக்கு பின்பே பண நெருக்கடி தீரும்.",
    },
    "Venus_Moon_Ketu": {
        "en": "Native takes real estate loan that proves exceedingly arduous to repay.",
        "ta": "வீடு வாங்குவதற்காக வாங்கிய கடன் திருப்பிச் செலுத்த முடியாமல் நீண்ட காலம் பெரும் சுமையாக மாறும்.",
    },
    "Saturn_Rahu": {
        "en": "Pret Atma Yoga / prone to evil eye; career stabilizes and accelerates only after age 30; suitable for aviation, photography, or investigation.",
        "ta": "பிரேத ஆத்மா யோகம் / கண் திருஷ்டி; 30 வயதுக்கு பிறகே தொழிலில் அசுர வளர்ச்சி மற்றும் வருமானம்; விமானத்துறை, துப்பறிதல் அல்லது போட்டோகிராபி.",
    },
    "Saturn_Ketu": {
        "en": "Berozgari Yoga (Unemployment Yoga); career succeeds only in Ketu professions (astrology, law, coding, medicine, theology); income surges after age 30.",
        "ta": "வேலையின்மை யோகம் (Berozgari); கேதுவின் தொழில்களை (ஜோதிடம், சட்டம், சாப்ட்வேர், மருத்துவம், ஆன்மீகம்) செய்தால் மட்டுமே 30 வயதுக்கு பின் பிரகாசிக்கும்.",
    },
}

# ---------------------------------------------------------------------------
# 8. Cuspal Sub-Lord (CSL) & Bhava Rules Catalog
# ---------------------------------------------------------------------------
BNN_CSL_EVENT_RULES: Dict[str, Dict[str, Any]] = {
    "immunity_and_vitality": {
        "favourable": [5, 11, 3, 9],
        "cure": [3, 5, 9, 11],
        "disease": [1, 4, 6, 8, 10, 12],
        "threat_to_life": [4, 10, 6, 8, 12],
        "chronic_saturn_rule": "If 1st CSL signifies 6 and 6th signifies 8, and both link to Saturn, illness is chronic and persistent.",
    },
    "victory_in_dispute": {
        "native_wins": [2, 6, 11],
        "opponent_wins": [5, 7, 8, 12],
    },
    "missing_person": {
        "water_sign": "Deceased",
        "land_sign": "Safe",
        "air_sign": "Far away",
        "fire_sign": "Injured",
        "return_home_houses": [2, 4, 11],
    },
    "wealth_accumulation": {
        "gain": [2, 6, 10, 11],
        "sudden_unearned_gain": [8],
        "loss": [5, 8, 12],
    },
    "competitive_exam": {
        "success": [3, 6, 9, 11],
        "failure": [2, 5, 8, 10, 12],
    },
    "property_ownership": {
        "purchase": [2, 4, 11],
        "with_loan": [12],
        "rental_income": [6],
        "sale": [3, 5, 10],
        "sale_profit": [11],
        "sale_loss": [8],
        "litigation_win": [2, 4, 11],
        "litigation_loss": [3, 5, 8, 10, 12],
    },
    "stock_market_csl": {
        "favourable": [2, 3, 5, 6, 8, 11],
        "unfavourable": [1, 4, 7, 9, 10, 12],
        "trading_style": {
            "intraday": ["Venus", "Mercury", "Moon"],
            "swing_5_10_days": ["Venus", "Sun", "Mars"],
            "short_term_90d_1yr": ["Jupiter"],
            "long_term_2_5yr_plus": ["Saturn"],
            "rahu_ketu_rule": "Rahu/Ketu assume nature of conjunct lord, star lord, opposite lord, or sign lord.",
        },
        "rahu_8_12_warning": "If Rahu is in 8th or 12th house, NEVER participate in share market; Rahu will ruin the native multiple times.",
    },
    "employment_and_career": {
        "job_success": [2, 6, 11],
        "promotion": [2, 6, 10, 11],
        "job_change": [5, 3, 9],
        "permanent_job": [6],
        "temporary_contractual": [3],
        "loan_clearance": [2, 6, 11],
        "retirement_job": [2, 6, 10, 11],
        "career_governor": "Nature of job must be checked from 10th House, never from 6th House alone.",
    },
    "marriage_and_divorce": {
        "marriage_promised": [2, 7, 11],
        "marriage_delayed": [4, 10],
        "marriage_channels": {
            "love": [5],
            "matrimonial_portal": [3],
            "arranged_court": [8],
            "stranger_spiritual": [9],
            "foreigner": [12],
            "elopement": [5, 8, 12],
        },
        "soul_partnership": [11],
        "barren_signs": ["Aries", "Gemini", "Leo", "Virgo"],
        "soulmate_match_rule": "Boy's 7th CSL = Girl's Moon Star Lord; or Girl's 7th CSL = Boy's Moon Star Lord (Made for each other).",
        "second_marriage_rule": "7th CSL in Duality AND 9th CSL connects to 2, 7, 9, 11 in Dual & Fruitful sign.",
        "divorce_indicators": [
            "Ketu placed between Mars and Venus",
            "Venus+Mars with Rahu between them (duniya aag laga degi)",
            "Venus+Mars with Saturn between them (grief after marriage)",
            "Two separating planets (Sun, Saturn, Rahu, Ketu) in 7th house",
            "Ketu between Sun and Moon (parents' divorce)",
            "Sun in Saturn star/sub or Saturn in Sun star/sub (Punarpoo Dosha cancellation)",
        ],
    },
    "foreign_settlement": {
        "travel": [3, 9, 12],
        "settlement": [11],
        "wealth_abroad": [2, 6, 11],
        "combinations": [
            "Rahu + Moon = Foreign travel",
            "Rahu + Saturn = Foreign settlement",
            "Saturn + Rahu + Moon = Foreign settlement (unless severed by Ketu)",
            "Guru + Rahu = Lives abroad",
            "Sun + Rahu = Settle abroad",
        ],
    },
    "jail_yoga": {
        "rules": [
            "Mercury + Rahu with Saturn in 2nd or 4th house",
            "Saturn or Rahu placed in 4th house (residence confinement)",
            "Saturn in Cancer sign (Kark Rashi)",
            "Saturn and Rahu conjoined in Cancer sign",
            "Equal number of planets flanking 2nd and 12th houses",
            "Saturn + Mercury",
        ]
    },
}

# ---------------------------------------------------------------------------
# 9. Planetary Yogas Catalog
# ---------------------------------------------------------------------------
BNN_YOGAS_CATALOG: Dict[str, Dict[str, Any]] = {
    "Dhan_Yoga": {
        "title": "BNN Mega Wealth Yoga (Dhan Yog)",
        "formula": "Jupiter (Life) + Venus (Wealth) + Saturn (Career) + Mercury (Business) connected across 1/5/9, 2/6/10, 3/7/11, 4/8/12, 2/12, 1/7, or 3/11",
        "effect_en": "Endows native with exceptional commercial prosperity, executive assets, and high social standing.",
        "effect_ta": "குரு, சுக்கிரன், சனி மற்றும் புதன் இணைந்து அல்லது திரிகோண தொடர்பில் இருப்பது மகா தன யோகத்தை தரும்.",
    },
    "Property_Acquisition_Yogas": {
        "title": "BNN Real Estate Yogas",
        "rules": [
            {"planets": ["Venus", "Jupiter"], "result_en": "Owns at least one house.", "result_ta": "ஒரு சொந்த வீடு அமையும்."},
            {"planets": ["Venus", "Saturn"], "result_en": "Owns an older/heritage house.", "result_ta": "பழைய பாரம்பரிய வீடு அமையும்."},
            {"planets": ["Venus", "Mercury"], "result_en": "Owns one house and one plot of land.", "result_ta": "ஒரு வீடும் ஒரு காலி நிலமும் அமையும்."},
            {"planets": ["Jupiter", "Mars", "Mercury"], "result_en": "Owns two distinct pieces of land.", "result_ta": "இரண்டு தனித்தனி நிலங்களுக்கு அதிபதியாவார்."},
            {"planets": ["Venus", "Rahu"], "result_en": "Multiple properties, including large mansions.", "result_ta": "பல பிரம்மாண்ட வீடுகள் மற்றும் சொத்துக்கள்."},
            {"planets": ["Venus", "Ketu"], "result_en": "Property faces legal disputes or is situated in a lane/corner.", "result_ta": "சொத்தில் வில்லங்கம் அல்லது முட்டுச்சந்து வீடு."},
            {"planets": ["Venus", "Mars"], "result_en": "Colonizer Yoga - massive real estate holdings.", "result_ta": "காலனைசர் யோகம் - மிகப்பெரிய நில அதிபர்."},
            {"planets": ["Venus", "Moon", "Ketu"], "result_en": "Heavy loan for property that is difficult to repay.", "result_ta": "கடன் வாங்கி வீடு கட்டி திருப்பிச் செலுத்த திண்டாடுவர்."},
        ],
    },
    "Santan_Affliction_Yogas": {
        "title": "BNN Progeny Vulnerabilities (Santan Badha)",
        "rules": [
            {"condition": "Saturn in 5th House", "meaning_en": "Serpent devouring children; late child, miscarriages, or sorrow from children.", "meaning_ta": "5-ல் சனி: தாமத குழந்தை, கருச்சிதைவு அல்லது பிள்ளைகளால் கவலை."},
            {"condition": "Rahu in 5th House", "meaning_en": "Inauspicious progeny results; trials persist even after abortions.", "meaning_ta": "5-ல் ராகு: கருச்சிதைவு மற்றும் பிள்ளைகளால் தொடர் மனவேதனை."},
            {"condition": "Ketu in 5th House", "meaning_en": "Child arrives via surgical operation/C-section after miscarriage; health fragility in son.", "meaning_ta": "5-ல் கேது: அறுவை சிகிச்சை மூலம் குழந்தை; ஆண் குழந்தைக்கு ஆரோக்கிய குறைபாடு."},
            {"condition": "Mercury in 8th or 12th House", "meaning_en": "Vulnerability to female child's health/longevity.", "meaning_ta": "8 அல்லது 12-ல் புதன்: பெண் குழந்தையின் ஆரோக்கியத்தில் சிக்கல்."},
            {"condition": "Sun and Venus within 3 degrees", "meaning_en": "Conception obstacles; impedes child birth.", "meaning_ta": "சூரியன் - சுக்கிரன் 3 பாகைக்குள் இணைவது குழந்தை பாக்கியத்தை தாமதப்படுத்தும்."},
            {"condition": "Moon and Venus within 3 degrees", "meaning_en": "Conception obstacles; denies easy child birth.", "meaning_ta": "சந்திரன் - சுக்கிரன் 3 பாகைக்குள் இணைவது குழந்தை பாக்கியத்தை தாமதப்படுத்தும்."},
            {"condition": "Mars + Moon Conjunction", "meaning_en": "High susceptibility to miscarriages/abortions.", "meaning_ta": "செவ்வாய் + சந்திரன் சேர்க்கை கருச்சிதைவை ஏற்படுத்தும்."},
        ],
    },
    "Sibling_Dynamics": {
        "title": "BNN Sibling Rules",
        "rules": [
            {"condition": "Jupiter connected to Mars", "result_en": "Younger brother guaranteed.", "result_ta": "நிச்சயமாக தம்பி உண்டு."},
            {"condition": "Jupiter connected to Saturn", "result_en": "Elder brother guaranteed.", "result_ta": "நிச்சயமாக அண்ணன் உண்டு."},
            {"condition": "Ketu in 12th from Jupiter", "result_en": "No elder siblings.", "result_ta": "மூத்த சகோதரர் இருக்க மாட்டார்."},
            {"condition": "Mars + Saturn", "result_en": "Discord and rivalry among brothers.", "result_ta": "சகோதர ஒற்றுமையின்மை (அண்ணன்-தம்பி சண்டை)."},
            {"condition": "Moon + Venus", "result_en": "Discord among sisters.", "result_ta": "சகோதரிகளுக்குள் தீவிர கருத்து வேறுபாடு."},
            {"condition": "Planetary Age Ranks", "result_en": "Saturn = Eldest sibling, Mars = Middle sibling, Mercury = Youngest sibling.", "result_ta": "சனி = மூத்தவர், செவ்வாய் = நடுத்தரமானவர், புதன் = இளையவர்."},
        ],
    },
    "Daridra_Berozgari_Yoga": {
        "title": "BNN Poverty & Unemployment Yogas",
        "combinations": ["Saturn + Ketu", "Venus + Ketu", "Saturn + Rahu", "Jupiter + Venus + Mercury + Saturn + Ketu"],
        "ketu_house_effects": {
            "1_4_7": "Bad; causes delays and one or two abortions before child.",
            "3_6_8": "Very bad; severe Berozgari (unemployment) unless working in Ketu domains.",
            "2_5_9_10_11_12": "Leaves native free to prosper according to karma.",
        },
        "turning_point": "Saturn+Ketu and Saturn+Rahu income surges only after age 30.",
    },
    "Serial_Marriage_Houses": {
        "title": "Multiple Marriages in Nadi / Vedic",
        "sequence": {
            "1st_and_6th_marriage": "7th House",
            "2nd_and_7th_marriage": "9th House (2nd Husband = Saturn; 2nd Wife = Mercury)",
            "3rd_and_8th_marriage": "11th House",
            "4th_marriage": "3rd House",
            "5th_marriage": "5th House",
        },
    },
    "Court_Cases_and_Litigation": {
        "title": "Court Cases & Police Station Yogas",
        "combinations": [
            "Mercury + Rahu",
            "Mercury + Ketu",
            "Saturn + Ketu",
            "Ketu + Mars + Mercury",
            "During 12th House periods or Saturn in 12th House (prolonged court case)",
        ],
    },
    "Accidents_and_Operations": {
        "title": "Surgery & Accident Yogas",
        "combinations": ["Mars + Rahu", "Mars + Ketu", "Mars + Saturn"],
    },
}

# ---------------------------------------------------------------------------
# 10. Comprehensive Planetary Remedial Science
# ---------------------------------------------------------------------------
BNN_REMEDIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "rudraksha": "1 Mukhi Rudraksha",
        "deities": ["Lord Shiva", "Lord Vishnu"],
        "mantra": "Om Hraam Hreem Hroum Suryaye Namaha",
        "specific_remedies": [
            "If Sun in 4, 6, 7, 8, 12: Lifetime dana of jaggery (gud) and copper.",
            "Touch father's feet daily and massage his legs.",
            "Offer fresh water (Arghya) to Lord Sun within 1 hour of sunrise.",
            "Offer crowns (Mukut) or peacock feathers (Mor Pankh) to Lord Vishnu.",
            "Offer Besan Ladoo to Vishnu Temple (do not bring them back).",
            "Recite Aditya Hridaya Stotram at sunrise daily.",
            "Recite Vishnu Sahasranama Stotram.",
            "Early to bed and rise early with sunrise.",
        ],
    },
    "Moon": {
        "rudraksha": "2 Mukhi Rudraksha",
        "deities": ["Lord Shiva", "Goddess Parvati"],
        "mantra": "Om Namah Shivaya / Mahamrityunjaya Mantra",
        "specific_remedies": [
            "Drink drinking water from a pure silver tumbler.",
            "Offer fresh water and unboiled milk onto a Shivling.",
            "Offer water and milk to Banyan tree root (Bargad).",
            "Observe Ekadashi fasts; offer milk/water Arghya on Purnima (Full Moon).",
            "STRICT TABOO: If Moon is in 6th or 8th house, NEVER donate milk or water to anyone (causes financial ruin).",
            "Seva of mother or elder ladies; carry mother's photograph.",
            "Take holy baths in oceans or sacred rivers on Mondays.",
        ],
    },
    "Mars": {
        "rudraksha": "3 Mukhi Rudraksha",
        "deities": ["Lord Hanuman"],
        "mantra": "Hanuman Chalisa / Sundar Kand",
        "specific_remedies": [
            "If Mars in 3, 4, 8: Donate jaggery (gud) and red lentils (masoor).",
            "Keep a solid square silver piece inside pocket or purse.",
            "Float sweet batasha or revadi in flowing river water.",
            "Offer water to Neem tree.",
            "Apply orange vermilion (sindoor) with pure jasmine oil to Hanuman Ji (for debt, job hurdles, marital discord).",
            "Recite Sundar Kand regularly (both males and females).",
            "Consume daily meals seated inside the kitchen; walk barefoot on green grass.",
            "Maintain amicable relations with younger brother.",
        ],
    },
    "Mercury": {
        "rudraksha": "4 Mukhi Rudraksha",
        "deities": ["Lord Ganesha", "Goddess Durga", "Lord Vishnu"],
        "mantra": "Om Namo Bhagavate Vasudevaya",
        "specific_remedies": [
            "If Mercury in 1st house: Strictly avoid wearing green clothing.",
            "Gift green dresses, green bangles, and sweets to young girls under 9 years of age.",
            "Soak whole green moong dal overnight and feed to birds in the morning.",
            "Feed green grass and fodder to goats.",
            "Offer clothing, green bangles, and dakshina to kinnars (transgenders) to unlock progeny and fortune.",
            "Recite Durga Saptashati and Ganesh Atharvashirsha.",
            "Recite Gopal Sahasranamam if encountering progeny obstacles.",
        ],
    },
    "Jupiter": {
        "rudraksha": "5 Mukhi Rudraksha",
        "deities": ["Lord Dattatreya", "Sai Baba", "Lord Vishnu"],
        "mantra": "Om Namo Bhagavate Vasudevaya / Guru Stotram",
        "specific_remedies": [
            "If Jupiter in 6, 8, 10: Daily apply saffron (Kesar) or turmeric tilak on forehead and navel.",
            "Wear a gold chain or sacred yellow thread around the neck.",
            "Donate 600g (if in 6th) or 800g (if in 8th) chana dal or turmeric to temple or religious trust.",
            "Donate papaya fruit to temples or orphanages.",
            "Perform selfless service (seva) in temples on Thursdays.",
            "Drink turmeric milk (Haldi doodh).",
            "Offer water to banana tree (Kele ka ped).",
            "Water and light diya at Peepal tree (omit Sundays).",
        ],
    },
    "Venus": {
        "rudraksha": "6 Mukhi Rudraksha",
        "deities": ["Goddess Lakshmi", "Mata Santoshi", "Lord Krishna"],
        "mantra": "Om Shum Shukraya Namaha / Sri Suktam / Vaibhav Lakshmi",
        "specific_remedies": [
            "If Venus in 6 or 8: Treat spouse with utmost reverence, gift perfumes and cosmetics, massage spouse's feet.",
            "STRICT TABOO: If Venus in 6 or 8, NEVER lend monetary loans to anyone (money will sink).",
            "Feed green fodder and fresh roti with jaggery to cows daily.",
            "Apply cow ghee tilak; donate pure ghee or cotton to temples.",
            "Wear Shukra Mani or Sphatik (quartz) rosary.",
            "Take curd bath (rub curd on body before bathing).",
            "Abhishek of Shivling with fresh unflavored curd.",
            "One-time remedy: Bury 21 Hakik gemstones on a Saturday near a Peepal tree.",
        ],
    },
    "Saturn": {
        "rudraksha": "7 Mukhi Rudraksha",
        "deities": ["Lord Bhairava", "Lord Shiva", "Lord Shani"],
        "mantra": "Om Sham Shanaischaraya Namaha / Mahamrityunjaya Mantra",
        "specific_remedies": [
            "If Saturn in 1, 4, 8, 12: Dana of mustard oil, whole black urad dal, water on Shivling.",
            "Feed fresh green grass/oil-smeared rotis to black buffaloes.",
            "For career breakthrough: Feed visually challenged (blind) individuals.",
            "Feed destitute beggars; respect manual laborers, housekeepers, and elder brothers.",
            "Amavasya ritual: Tie jaggery in two corners of a black piece of cloth and offer to Lord Shani.",
            "Maintain strict honesty, punctuality, and hard work in vocation.",
        ],
    },
    "Rahu": {
        "rudraksha": "8 Mukhi Rudraksha",
        "deities": ["Goddess Saraswati", "Lord Bhairava", "Lord Shiva"],
        "mantra": "Nav Nag Stotram / Saraswati Chalisa / Bhairav Mantra",
        "specific_remedies": [
            "IMMEDIATE RELIEF: Gift a bundle of bidis to municipal sweepers/sanitation workers.",
            "If Rahu in 1, 2, 4, 7, 8, 9, 12: Donate white radishes or tea leaves (omit if in 5th).",
            "Float alive Mangur fish in flowing natural river water.",
            "Feed wheat flour dough balls (Ate ki goli) to river fish.",
            "Eat daily meals seated inside the kitchen.",
            "Feed pearl millet (bajra) to wild pigeons.",
            "Clean toilet bowls and bathrooms personally using blue Lysol.",
            "Perform Rudrabhishekam; seva of paternal grandparents.",
        ],
    },
    "Ketu": {
        "rudraksha": "9 Mukhi Rudraksha",
        "deities": ["Lord Ganesha", "Lord Bhairava", "Lord Hanuman"],
        "mantra": "Ganesh Atharvashirsha / Om Kem Ketave Namaha",
        "specific_remedies": [
            "If Ketu in 1, 3, 4, 6, 7, 8: Donate 3 yellow bananas freely to temple or elderly.",
            "Donate raw garlic pods to handicapped/disabled individuals.",
            "Donate black-and-white checkered blankets to lepers or monks.",
            "Offer fresh Durva grass to Lord Ganesha with white and black sesame seeds.",
            "Feed Marie/Marigold biscuits to stray dogs (15-20 packets if heavily afflicted).",
            "Corn silk (Bhutte ke baal) ritual: Circle 4 times anticlockwise around head and bury in isolated soil.",
            "Practice meditation, Pranayama, and seva of maternal grandparents.",
        ],
    },
}

BNN_GENERAL_LIFE_REMEDIES: List[Dict[str, str]] = [
    {"rule": "Moon Afflicted", "maxim": "Ruined childhood (Bachpan Kharab) - propitiate Shiva and nurture mother."},
    {"rule": "Sun Afflicted", "maxim": "Tormented youth (Jawani Kharab) - offer water to Sun and revere father."},
    {"rule": "Saturn Afflicted", "maxim": "Suffering in old age (Bhudapa Kharab) - follow ethical conduct and feed the needy."},
    {"rule": "Bhandara Food Taboo", "maxim": "Avoid eating in public free bhandaras; doing so severely afflicts the Sun and self-esteem."},
    {"rule": "Used Articles Taboo", "maxim": "Never wear clothes, shoes, or slippers discarded by others."},
    {"rule": "Speech Purification", "maxim": "Apply saffron (Kesar) tilak to the tongue to sweeten harsh speech (Vaani Dosha)."},
    {"rule": "Evening Arrival Rule", "maxim": "Never return home with empty hands in the evening; always bring fruits or household goods."},
    {"rule": "Broken Rice Taboo", "maxim": "Do not consume broken rice grains (Tukdi Chawal represents Ketu)."},
    {"rule": "Masoor Dal Debt Remedy", "maxim": "Offer 400g red masoor dal onto Shivling while chanting: 'Om Rin Mukteshvaraya Namah Mahadevaya Namah'."},
    {"rule": "Universal S.O.S. Remedy", "maxim": "When any planet is severely afflicted, offering its corresponding metal or grain to Lord Shiva, a cow, or a beggar removes negative karma with zero side effects."},
]


def evaluate_pankajj_duaa_compendium(
    planets_data: Dict[str, Dict[str, Any]],
    ascendant_sign: int,
    gender: str = "male",
) -> Dict[str, Any]:
    """Evaluates Pankajj K Duaa's BNN predictive, medical, yoga, and remedial rules."""
    p_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    p_signs: Dict[str, int] = {}
    p_degrees: Dict[str, float] = {}
    p_retro: Dict[str, bool] = {}
    p_houses: Dict[str, int] = {}

    for p in p_names:
        info = planets_data.get(p, {})
        s_idx = max(1, min(12, int(info.get("sign_index", 1))))
        deg = float(info.get("degree", 0.0))
        ret = bool(info.get("is_retrograde", False))
        h_idx = ((s_idx - ascendant_sign) % 12) + 1
        p_signs[p] = s_idx
        p_degrees[p] = deg
        p_retro[p] = ret
        p_houses[p] = h_idx

    # 1. Rashi Mobility Classification
    char_planets, sthir_planets, upaye_planets = [], [], []
    for p, s in p_signs.items():
        mob = BNN_RASHI_MOBILITY.get(s, {}).get("mobility", "")
        if "Char" in mob:
            char_planets.append(p)
        elif "Sthir" in mob:
            sthir_planets.append(p)
        else:
            upaye_planets.append(p)

    rashi_mobility_summary = {
        "char_movable_count": len(char_planets),
        "char_planets": char_planets,
        "sthir_fixed_count": len(sthir_planets),
        "sthir_planets": sthir_planets,
        "upaye_dual_count": len(upaye_planets),
        "upaye_planets": upaye_planets,
    }

    # 2. Naadi House Quality Evaluation (Irrespective of Rashi)
    house_qualities = {}
    for p, h in p_houses.items():
        q_data = BNN_NAADI_HOUSE_QUALITY.get(p, {})
        status = "neutral"
        status_ta = "நடுத்தரம்"
        if h in q_data.get("good", []):
            status = "Good (Ucch Effect)"
            status_ta = "உச்ச பலன் / நற்பலன்"
        elif h in q_data.get("very_bad", []):
            status = "Very Bad (Neech Effect)"
            status_ta = "நீச பலன் / கடும் பாதிப்பு"
        elif h in q_data.get("mix", []):
            status = "Mixed Effect"
            status_ta = "கலப்பு பலன்"
        house_qualities[p] = {
            "house": h,
            "status": status,
            "status_ta": status_ta,
        }

    # 3. Medical Astrology Diagnostics
    # A. Life Significator
    is_female = gender.lower() == "female"
    prime_karaka = "Venus" if is_female else "Jupiter"
    prime_house = p_houses[prime_karaka]
    prime_afflicted = False
    reasons_en, reasons_ta = [], []

    if is_female:
        if prime_house in [6, 8]:
            prime_afflicted = True
            reasons_en.append(f"Venus in {prime_house}th house causes chronic gynecological or vitality weakness.")
            reasons_ta.append(f"சுக்கிரன் {prime_house}-ஆம் வீட்டில் அமர்வது பெண்மை நலம் மற்றும் ஆரோக்கிய பலவீனத்தைத் தரும்.")
        if p_signs["Venus"] in [p_signs["Rahu"], p_signs["Ketu"], p_signs["Moon"]]:
            prime_afflicted = True
            reasons_en.append("Venus is conjoined with Rahu, Ketu, or Moon.")
            reasons_ta.append("சுக்கிரன் ராகு, கேது அல்லது சந்திரனுடன் இணைந்து பலவீனமடைகிறார்.")
    else:
        if prime_house in [6, 8]:
            prime_afflicted = True
            reasons_en.append(f"Jupiter in {prime_house}th house creates vulnerability to digestive, liver, or breathing disorders.")
            reasons_ta.append(f"குரு {prime_house}-ஆம் வீட்டில் நிற்பது கல்லீரல் அல்லது சுவாச ஆரோக்கியத்தைப் பாதிக்கும்.")
        if p_signs["Jupiter"] in [p_signs["Rahu"], p_signs["Ketu"]]:
            prime_afflicted = True
            reasons_en.append("Jupiter is afflicted by nodal axis (Rahu/Ketu conjunction).")
            reasons_ta.append("குரு ராகு அல்லது கேதுவுடன் இணைந்து பலவீனமடைந்துள்ளார்.")

    life_significator_eval = {
        "prime_planet": prime_karaka,
        "is_afflicted": prime_afflicted,
        "house": prime_house,
        "evaluation_en": " ".join(reasons_en) if prime_afflicted else f"Life significator ({prime_karaka}) is dignified and safeguards vitality.",
        "evaluation_ta": " ".join(reasons_ta) if prime_afflicted else f"ஜீவ காரகரான {prime_karaka} சுப பலத்துடன் ஆரோக்கியத்தைக் காக்கிறார்.",
    }

    # B. Organ Afflictions by 2+ Enemy Planets in Single House
    organ_afflictions = []
    house_planets: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    for p, h in p_houses.items():
        house_planets[h].append(p)

    for h, occupant_planets in house_planets.items():
        if len(occupant_planets) >= 2:
            has_enemy_pair = False
            for i in range(len(occupant_planets)):
                for j in range(i + 1, len(occupant_planets)):
                    p1, p2 = occupant_planets[i], occupant_planets[j]
                    enemies_of_p1 = BNN_PANKAJJ_FRIENDSHIP.get(p1, {}).get("enemies", [])
                    if p2 in enemies_of_p1:
                        has_enemy_pair = True
                        break
                if has_enemy_pair:
                    break
            if has_enemy_pair:
                organ_info = BNN_MEDICAL_ASTROLOGY_RULES["house_anatomical_map"].get(h, {})
                organ_afflictions.append({
                    "house": h,
                    "planets": occupant_planets,
                    "organ_en": organ_info.get("en", ""),
                    "organ_ta": organ_info.get("ta", ""),
                    "warning_en": f"House {h} holds mutual enemies ({', '.join(occupant_planets)}); vulnerability to disorders in {organ_info.get('en', '')}.",
                    "warning_ta": f"{h}-ஆம் பாவத்தில் பகை கிரகங்கள் ({', '.join(occupant_planets)}) இணைவதால் {organ_info.get('ta', '')} பகுதியில் பாதிப்பு ஏற்படலாம்.",
                })

    # C. Cancer Yoga Check
    sat_s, rahu_s = p_signs["Saturn"], p_signs["Rahu"]
    cancer_diff = abs(sat_s - rahu_s)
    has_cancer_yoga = (sat_s == rahu_s) or (cancer_diff in [4, 8]) or (cancer_diff == 6)
    cancer_yoga_eval = {
        "is_active": has_cancer_yoga,
        "title_en": "Saturn-Rahu Cancer / Cellular Mutation Vulnerability",
        "title_ta": "சனி - ராகு புற்றுநோய் / கட்டி பாதிப்பு எச்சரிக்கை",
        "explanation_en": "Saturn and Rahu are interconnected (conjunction, trine, or opposition), indicating bodily vulnerability to cysts or cellular mutations." if has_cancer_yoga else "Saturn and Rahu operate in distinct unlinked sectors.",
        "explanation_ta": "சனியும் ராகுவும் சேர்க்கை, திரிகோணம் அல்லது சமசப்தம தொடர்பில் இருப்பதால் உடலில் கட்டிகள் அல்லது செல் பிறழ்வு எச்சரிக்கை தேவை." if has_cancer_yoga else "சனியும் ராகுவும் தொடர்பில்லாமல் இயல்பாக உள்ளனர்.",
    }

    # 4. Matched Planet-Pair Combinations (Conjunctions)
    matched_pairs = []
    checked_pairs = set()
    for p1 in p_names:
        for p2 in p_names:
            if p1 >= p2:
                continue
            pair_key_1 = f"{p1}_{p2}"
            pair_key_2 = f"{p2}_{p1}"
            found_key = pair_key_1 if pair_key_1 in BNN_PLANET_PAIR_COMBINATIONS else (pair_key_2 if pair_key_2 in BNN_PLANET_PAIR_COMBINATIONS else None)
            if found_key and found_key not in checked_pairs:
                # Conjunction in same sign
                if p_signs[p1] == p_signs[p2]:
                    checked_pairs.add(found_key)
                    deg_diff = abs(p_degrees[p1] - p_degrees[p2])
                    info = BNN_PLANET_PAIR_COMBINATIONS[found_key]
                    matched_pairs.append({
                        "pair": f"{p1} + {p2}",
                        "degree_difference": round(deg_diff, 2),
                        "sign": p_signs[p1],
                        "reading_en": info["en"],
                        "reading_ta": info["ta"],
                    })

    # 5. Specialized Yogas Evaluator
    matched_yogas = []

    # A. Dhan Yoga (Jupiter + Venus + Saturn + Mercury)
    # Check if Jupiter, Venus, Saturn, Mercury share same element trine or same houses
    element_map = {1: "Fire", 5: "Fire", 9: "Fire", 2: "Earth", 6: "Earth", 10: "Earth", 3: "Air", 7: "Air", 11: "Air", 4: "Water", 8: "Water", 12: "Water"}
    jup_elem = element_map[p_signs["Jupiter"]]
    ven_elem = element_map[p_signs["Venus"]]
    sat_elem = element_map[p_signs["Saturn"]]
    mer_elem = element_map[p_signs["Mercury"]]
    if jup_elem == ven_elem == sat_elem == mer_elem:
        matched_yogas.append({
            "yoga_name": "BNN Mega Wealth Yoga (Dhan Yog)",
            "yoga_name_ta": "BNN மகா தன யோகம்",
            "is_favorable": True,
            "description_en": "Jupiter (Life), Venus (Wealth), Saturn (Karma), and Mercury (Trade) unite in the same directional trine, creating immense commercial prosperity.",
            "description_ta": "குரு, சுக்கிரன், சனி மற்றும் புதன் ஒரே திசை திரிகோணத்தில் இணைந்து அரிய மகா தன யோகத்தை உண்டாக்குகின்றனர்.",
        })

    # B. Colonizer Real Estate Yoga (Venus + Mars)
    if p_signs["Venus"] == p_signs["Mars"]:
        matched_yogas.append({
            "yoga_name": "Colonizer Real Estate Yoga (Venus + Mars)",
            "yoga_name_ta": "காலனைசர் ரியல் எஸ்டேட் யோகம் (சுக்கிரன் + செவ்வாய்)",
            "is_favorable": True,
            "description_en": "Venus conjunct Mars grants extensive landed property, layout development, and modern real estate acquisition.",
            "description_ta": "சுக்கிரனும் செவ்வாயும் இணைவதால் பிரம்மாண்டமான நிலபுலன்கள், ரியல் எஸ்டேட் மற்றும் வீட்டுமனை யோகம் அமையும்.",
        })

    # C. Vishnu-Lakshmi Yoga (Venus + Mercury)
    if p_signs["Venus"] == p_signs["Mercury"]:
        matched_yogas.append({
            "yoga_name": "Vishnu-Lakshmi Property & Commerce Yoga (Venus + Mercury)",
            "yoga_name_ta": "விஷ்ணு-லட்சுமி யோகம் (சுக்கிரன் + புதன்)",
            "is_favorable": True,
            "description_en": "Venus conjunct Mercury assures ownership of one house and one piece of land, alongside sweet speech and commercial revenue.",
            "description_ta": "சுக்கிரனும் புதனும் சேர்வதால் ஒரு வீடு, ஒரு காலி நிலம் மற்றும் வர்த்தக ரீதியான தனலாபம் கிட்டும்.",
        })

    # D. Two Lands Yoga (Jupiter + Mars + Mercury)
    if (element_map[p_signs["Jupiter"]] == element_map[p_signs["Mars"]] == element_map[p_signs["Mercury"]]) or (p_signs["Jupiter"] == p_signs["Mars"] == p_signs["Mercury"]):
        matched_yogas.append({
            "yoga_name": "Two Lands Ownership Yoga (Jupiter + Mars + Mercury)",
            "yoga_name_ta": "இரு நில யோகம் (குரு + செவ்வாய் + புதன்)",
            "is_favorable": True,
            "description_en": "Jupiter (Life) + Mars (Land) + Mercury (Trade/Two) promises ownership of two separate landed properties.",
            "description_ta": "குரு, செவ்வாய் மற்றும் புதன் இணைவதால் இரண்டு தனித்தனி நிலங்களுக்கு உரிமையாளராவார்.",
        })

    # E. Berozgari Yoga (Saturn + Ketu)
    if p_signs["Saturn"] == p_signs["Ketu"]:
        matched_yogas.append({
            "yoga_name": "Berozgari (Unemployment) & Post-30 Awakening Yoga (Saturn + Ketu)",
            "yoga_name_ta": "வேலையின்மை யோகம் & 30 வயதுக்கு பின் யோகம் (சனி + கேது)",
            "is_favorable": False,
            "description_en": "Saturn with Ketu terminates ordinary corporate pursuits; native must adopt Ketu fields (astrology, coding, law, medicine); earnings surge after age 30.",
            "description_ta": "சனி கேதுவுடன் இணைவதால் வழக்கமான வேலைகளில் திருப்தியின்மை ஏற்படும்; கேதுவின் துறைகளில் மட்டுமே 30 வயதுக்கு பின் அபார வளர்ச்சி கிட்டும்.",
        })

    # F. Sister Discord (Moon + Venus)
    if p_signs["Moon"] == p_signs["Venus"]:
        matched_yogas.append({
            "yoga_name": "Sister Discord & Residential Loan Yoga (Moon + Venus)",
            "yoga_name_ta": "சகோதரிகள் ஒற்றுமையின்மை & வீட்டுக் கடன் (சந்திரன் + சுக்கிரன்)",
            "is_favorable": False,
            "description_en": "Moon conjunct Venus signifies discord among sisters and taking a heavy loan for residential shelter.",
            "description_ta": "சந்திரனும் சுக்கிரனும் இணைவதால் சகோதரிகளுக்குள் மனக்கசப்புகளும், வீட்டின் மீது கடன் சுமைகளும் உண்டாகும்.",
        })

    # G. Brother Discord (Mars + Saturn)
    if p_signs["Mars"] == p_signs["Saturn"]:
        matched_yogas.append({
            "yoga_name": "Brotherly Discord & Accident Caution (Mars + Saturn)",
            "yoga_name_ta": "சகோதர ஒற்றுமையின்மை & விபத்து எச்சரிக்கை (செவ்வாய் + சனி)",
            "is_favorable": False,
            "description_en": "Mars conjunct Saturn indicates friction among brothers, fluctuating blood pressure, and mechanical/engineering prowess.",
            "description_ta": "செவ்வாயும் சனியும் இணைவதால் சகோதர ஒற்றுமையின்மை மற்றும் எந்திரவியல் துறையில் வெற்றி உண்டாகும்.",
        })

    # H. Strict Loan Prohibition (Mars + Ketu or Venus + Ketu)
    if p_signs["Mars"] == p_signs["Ketu"]:
        matched_yogas.append({
            "yoga_name": "Strict Loan Prohibition Yoga (Mars + Ketu)",
            "yoga_name_ta": "கடன் தடை யோகம் (செவ்வாய் + கேது)",
            "is_favorable": False,
            "description_en": "Strict Pankajj Duaa Injunction: NEVER take or extend any financial loan in life. Prone to surgery or blood infection.",
            "description_ta": "கடுமையான எச்சரிக்கை: ஆயுளில் கடன் வாங்கவோ கொடுக்கவோ கூடாது. அறுவை சிகிச்சை அல்லது ரத்தத் தொற்று எச்சரிக்கை.",
        })
    if p_signs["Venus"] == p_signs["Ketu"]:
        matched_yogas.append({
            "yoga_name": "Lending Prohibition & Corner House Yoga (Venus + Ketu)",
            "yoga_name_ta": "கடன் கொடுக்கக் கூடாது & முட்டுச்சந்து வீடு (சுக்கிரன் + கேது)",
            "is_favorable": False,
            "description_en": "Strict Injunction: NEVER extend monetary loans to anyone. House will be situated in a corner or lane.",
            "description_ta": "எச்சரிக்கை: யாருக்கும் கடன் கொடுக்கக் கூடாது (பணம் திரும்பாது). வீடு முட்டுச்சந்தில் அமையும்.",
        })

    # I. Dietary Taboo (Sun in 11th House)
    if p_houses["Sun"] == 11:
        matched_yogas.append({
            "yoga_name": "Sun in 11th House: Strict Vegetarian Mandate",
            "yoga_name_ta": "11-ஆம் வீட்டில் சூரியன்: கடுமையான அசைவ உணவுத் தவிர்ப்பு",
            "is_favorable": False,
            "description_en": "Strict BNN Mandate: Native must strictly abstain from non-vegetarian food to protect progeny health and ensure prosperity.",
            "description_ta": "கடுமையான BNN விதி: பிள்ளைகளின் நல்வாழ்வுக்காக ஜாதகர் வாழ்நாள் முழுவதும் அசைவ உணவை கண்டிப்பாகத் தவிர்க்க வேண்டும்.",
        })

    # J. Progeny Warnings (Saturn / Rahu / Ketu in 5th)
    if p_houses["Saturn"] == 5:
        matched_yogas.append({
            "yoga_name": "Saturn in 5th House: Child Delay & Serpent Dosha",
            "yoga_name_ta": "5-ல் சனி: தாமத குழந்தை & கருச்சிதைவு எச்சரிக்கை",
            "is_favorable": False,
            "description_en": "Saturn in 5th Bhava acts as a devouring serpent for progeny; causes delay, abortion, or filial sorrow.",
            "description_ta": "5-ஆம் வீட்டில் சனி அமர்வது குழந்தை பாக்கியத்தை தாமதப்படுத்தும் அல்லது பிள்ளைகளால் கவலையைத் தரும்.",
        })
    if p_houses["Rahu"] == 5:
        matched_yogas.append({
            "yoga_name": "Rahu in 5th House: Obstacles in Progeny",
            "yoga_name_ta": "5-ல் ராகு: வம்ச விருத்தி தடைகள்",
            "is_favorable": False,
            "description_en": "Rahu in 5th House indicates trials regarding children and potential miscarriages.",
            "description_ta": "5-ல் ராகு இருப்பது பிள்ளைகள் விஷயத்தில் சோதனைகளையும் போராட்டங்களையும் தரும்.",
        })
    if p_houses["Ketu"] == 5:
        matched_yogas.append({
            "yoga_name": "Ketu in 5th House: Progeny via Surgery / C-Section",
            "yoga_name_ta": "5-ல் கேது: அறுவை சிகிச்சை மூலம் குழந்தை பிறப்பு",
            "is_favorable": False,
            "description_en": "Ketu in 5th Bhava promises children through surgical C-section or after initial abortion; monitor son's health.",
            "description_ta": "5-ல் கேது நிற்பதால் அறுவை சிகிச்சை மூலம் குழந்தை பிறக்கும்; ஆண் குழந்தையின் ஆரோக்கியத்தை கவனிக்க வேண்டும்.",
        })

    # 6. Degree Border Alerts
    degree_border_alerts = []
    for p, deg in p_degrees.items():
        if p in ["Rahu", "Ketu"]:
            continue
        is_ret = p_retro.get(p, False)
        if 27.0 <= deg <= 30.0:
            if is_ret:
                degree_border_alerts.append({
                    "planet": p,
                    "degree": deg,
                    "shift_en": f"{p} is retrograde at {deg:.2f}°: casts primary results into the PREVIOUS house.",
                    "shift_ta": f"{p} {deg:.2f}° பாகையில் வக்ரமடைந்துள்ளது: தனது முந்தைய வீட்டிற்குரிய பலன்களை வழங்குகிறது.",
                })
            else:
                degree_border_alerts.append({
                    "planet": p,
                    "degree": deg,
                    "shift_en": f"{p} is at {deg:.2f}° (cusp border): imparts full results to the NEXT house as well.",
                    "shift_ta": f"{p} {deg:.2f}° பாகையில் எல்லையில் உள்ளது: அடுத்த வீட்டின் பலன்களையும் முழுமையாகத் தருகிறது.",
                })
        elif 0.0 <= deg <= 3.0:
            degree_border_alerts.append({
                "planet": p,
                "degree": deg,
                "shift_en": f"{p} is at {deg:.2f}° (cusp entry): reflects lingering influence into the PREVIOUS house.",
                "shift_ta": f"{p} {deg:.2f}° தொடக்க பாகையில் உள்ளது: முந்தைய வீட்டின் பலன்களையும் பிரதிபலிக்கிறது.",
            })

    # 7. Prescribed Remedies
    prescribed_remedies = []
    # Identify planets that are in very bad houses or afflicted
    afflicted_planets = set()
    for p, q in house_qualities.items():
        if "Very Bad" in q["status"] or "Mixed" in q["status"]:
            afflicted_planets.add(p)
    if prime_afflicted:
        afflicted_planets.add(prime_karaka)
    if has_cancer_yoga:
        afflicted_planets.add("Saturn")
        afflicted_planets.add("Rahu")

    for p in sorted(list(afflicted_planets)):
        r_info = BNN_REMEDIES_REGISTRY.get(p)
        if r_info:
            prescribed_remedies.append({
                "planet": p,
                "rudraksha": r_info["rudraksha"],
                "deities": ", ".join(r_info["deities"]),
                "mantra": r_info["mantra"],
                "key_remedies": r_info["specific_remedies"][:4],
            })

    return {
        "metadata": BNN_PANKAJJ_DUAA_METADATA,
        "rashi_mobility_summary": rashi_mobility_summary,
        "naadi_house_qualities": house_qualities,
        "medical_astrology": {
            "life_significator": life_significator_eval,
            "organ_afflictions": organ_afflictions,
            "cancer_yoga": cancer_yoga_eval,
        },
        "matched_pairs": matched_pairs,
        "matched_yogas": matched_yogas,
        "degree_border_alerts": degree_border_alerts,
        "prescribed_remedies": prescribed_remedies,
        "general_life_maxims": BNN_GENERAL_LIFE_REMEDIES,
    }

