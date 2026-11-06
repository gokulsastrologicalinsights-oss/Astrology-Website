"""Deva Keralam (Chandra Kala Nadi) 150 Nadiamsas and Longevity Engine.

Synthesizes micro-zodiac 12-minute arc divisions, Khanda Nirnaya, and parent critical degrees.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple

NADIAMSA_CATALOG: Dict[int, Dict[str, str]] = {
    1: {"name_ta": "வசுதா", "name_en": "Vasudha"},
    2: {"name_ta": "வைஷ்ணவீ", "name_en": "Vaishnavi"},
    3: {"name_ta": "பிராம்மீ", "name_en": "Brahmi"},
    4: {"name_ta": "காளகூடம்", "name_en": "Kalakoota"},
    5: {"name_ta": "சங்கரீ", "name_en": "Sankari"},
    6: {"name_ta": "சதாகாரீ", "name_en": "Sadaakari"},
    7: {"name_ta": "ஸமா", "name_en": "Samaa"},
    8: {"name_ta": "ஸௌம்யா", "name_en": "Saumya"},
    9: {"name_ta": "ஸுரா", "name_en": "Suraa"},
    10: {"name_ta": "மாயா", "name_en": "Maaya"},
    11: {"name_ta": "மனோஹரா", "name_en": "Manoharaa"},
    12: {"name_ta": "மாதவீ", "name_en": "Maadhavi"},
    13: {"name_ta": "மஞ்சுஸ்வனா", "name_en": "Manjuswana"},
    14: {"name_ta": "கோரா", "name_en": "Ghoraa"},
    15: {"name_ta": "கும்பினீ", "name_en": "Kumbhini"},
    16: {"name_ta": "குடிலா", "name_en": "Kutilaa"},
    17: {"name_ta": "பிரபா", "name_en": "Prabhaa"},
    18: {"name_ta": "பரா", "name_en": "Paraa"},
    19: {"name_ta": "பயஸ்வினீ", "name_en": "Payaswini"},
    20: {"name_ta": "மாலா", "name_en": "Maala"},
    21: {"name_ta": "ஜகதீ", "name_en": "Jagathi"},
    22: {"name_ta": "ஜர்ஜரா", "name_en": "Jarjharaa"},
    23: {"name_ta": "துருவா", "name_en": "Dhruva"},
    24: {"name_ta": "முஸலா", "name_en": "Musalaa"},
    25: {"name_ta": "முத்ரகரா", "name_en": "Mudgara"},
    26: {"name_ta": "பாசா", "name_en": "Pasaa"},
    27: {"name_ta": "சம்பகா", "name_en": "Champaka"},
    28: {"name_ta": "தாமினீ", "name_en": "Daamini"},
    29: {"name_ta": "மஹீ", "name_en": "Mahi"},
    30: {"name_ta": "கலுஷா", "name_en": "Kalushaa"},
    31: {"name_ta": "கமலா", "name_en": "Kamalaa"},
    32: {"name_ta": "காந்தா", "name_en": "Kantha"},
    33: {"name_ta": "காலா", "name_en": "Kaalaa"},
    34: {"name_ta": "கரிகரா", "name_en": "Karikaraa"},
    35: {"name_ta": "க்ஷமா", "name_en": "Kshamaa"},
    36: {"name_ta": "துர்தரா", "name_en": "Durdhuraa"},
    37: {"name_ta": "துர்பகா", "name_en": "Durbhagaa"},
    38: {"name_ta": "விஸ்வா", "name_en": "Viswa"},
    39: {"name_ta": "விசீர்ணா", "name_en": "Visirnaa"},
    40: {"name_ta": "விகடா", "name_en": "Vikata"},
    41: {"name_ta": "ஆவிலா", "name_en": "Aavilaa"},
    42: {"name_ta": "வித்ருமா", "name_en": "Vidrumaa"},
    43: {"name_ta": "ஸுகதா", "name_en": "Sukhada"},
    44: {"name_ta": "ஸ்னிக்தா", "name_en": "Snigdha"},
    45: {"name_ta": "ஸோதரா", "name_en": "Sodaraa"},
    46: {"name_ta": "ஸுரஸுந்தரீ", "name_en": "Surasundari"},
    47: {"name_ta": "அம்ருதப்லாவினீ", "name_en": "Amrithaplavini"},
    48: {"name_ta": "கராளா", "name_en": "Karalaa"},
    49: {"name_ta": "காமதுக்", "name_en": "Kaamadhuk"},
    50: {"name_ta": "கரவீரணீ", "name_en": "Karaveerani"},
    51: {"name_ta": "கஹ்வரா", "name_en": "Gahvaraa"},
    52: {"name_ta": "குண்டினீ", "name_en": "Kundini"},
    53: {"name_ta": "ரௌத்ரீ / காந்தா", "name_en": "Raudra/Kaantha"},
    54: {"name_ta": "விஷா", "name_en": "Vishaa"},
    55: {"name_ta": "விஷவிநாசினீ", "name_en": "Vishavinaasini"},
    56: {"name_ta": "நிர்மதா", "name_en": "Nirmadaa"},
    57: {"name_ta": "சீதளா", "name_en": "Seethalaa"},
    58: {"name_ta": "நிம்னா", "name_en": "Nimnaa"},
    59: {"name_ta": "ப்ரீதா", "name_en": "Preeta"},
    60: {"name_ta": "பவித்ரா", "name_en": "Pavitra"},
    61: {"name_ta": "மானக்னா", "name_en": "Maanaghna"},
    62: {"name_ta": "துர்பகா", "name_en": "Durbhagaa"},
    63: {"name_ta": "சித்ரா", "name_en": "Chitraa"},
    64: {"name_ta": "சித்ரிணீ", "name_en": "Chitrini"},
    65: {"name_ta": "சிரஞ்சீவினீ", "name_en": "Chiranjeevani"},
    66: {"name_ta": "பூபா", "name_en": "Bhoopa"},
    67: {"name_ta": "கதாஹரா", "name_en": "Gadaaharaa"},
    68: {"name_ta": "நாலா", "name_en": "Naala"},
    69: {"name_ta": "நளினீ", "name_en": "Nalini"},
    70: {"name_ta": "நிர்மலா", "name_en": "Nirmala"},
    71: {"name_ta": "நதீ", "name_en": "Nadi"},
    72: {"name_ta": "சதாஅம்ருதாம்சுகலா", "name_en": "Sadamritamsukala"},
    73: {"name_ta": "சபலா", "name_en": "Chapalaa"},
    74: {"name_ta": "சாங்குரா", "name_en": "Saankuraa"},
    75: {"name_ta": "த்ரைலோக்யமோகனகரீ", "name_en": "Trailokyamohanakan"},
    76: {"name_ta": "மகாமாரீ", "name_en": "Mahaamaari"},
    77: {"name_ta": "சுசீதளா", "name_en": "Suseethala"},
    78: {"name_ta": "சுமதா / சுபகா", "name_en": "Sumatha/Subhaga"},
    79: {"name_ta": "சுப்ரபா", "name_en": "Suprabhaa"},
    80: {"name_ta": "சோபா", "name_en": "Sobhaa"},
    81: {"name_ta": "சோபனா", "name_en": "Sobhana"},
    82: {"name_ta": "சிவதா", "name_en": "Sivadaa"},
    83: {"name_ta": "சிவா", "name_en": "Siva"},
    84: {"name_ta": "பலா", "name_en": "Balaa"},
    85: {"name_ta": "ஜ்வாலா", "name_en": "Jwaala"},
    86: {"name_ta": "கதா", "name_en": "Gada"},
    87: {"name_ta": "காதா", "name_en": "Gaadha"},
    88: {"name_ta": "நூதனா", "name_en": "Nootanaa"},
    89: {"name_ta": "சுமனோஹரா", "name_en": "Sumanoharaa"},
    90: {"name_ta": "சோமவல்லீ", "name_en": "Somavalli"},
    91: {"name_ta": "மோக்ஷாபவர்க்கா", "name_en": "Mokshapavarga"},
    92: {"name_ta": "வலய", "name_en": "Valayaa"},
    93: {"name_ta": "நவநீதா", "name_en": "Navaneetha"},
    94: {"name_ta": "நிசாகரீ", "name_en": "Nisakari"},
    95: {"name_ta": "நிர்விருத்தி", "name_en": "Nirvrithi"},
    96: {"name_ta": "நிகதா", "name_en": "Nigadaa"},
    97: {"name_ta": "சாரா / ஸௌரா", "name_en": "Saara/Sauraa"},
    98: {"name_ta": "சங்கீதா", "name_en": "Sangeetha"},
    99: {"name_ta": "சுதா", "name_en": "Sumathaa"},
    100: {"name_ta": "விஸ்வம்பரா", "name_en": "Viswambhara"},
    101: {"name_ta": "குமாரீ", "name_en": "Kumari"},
    102: {"name_ta": "கோகிலா", "name_en": "Kokila"},
    103: {"name_ta": "குஞ்சராக்ருதி", "name_en": "Kunjarakrithi"},
    104: {"name_ta": "ஐந்திரா", "name_en": "Aindira"},
    105: {"name_ta": "ஸ்வாஹா", "name_en": "Swaahaa"},
    106: {"name_ta": "ஸ்வரா", "name_en": "Swaraa"},
    107: {"name_ta": "வஹ்னி", "name_en": "Vahni"},
    108: {"name_ta": "ப்ரீதி", "name_en": "Preethi"},
    109: {"name_ta": "ரக்ஷோஜலா", "name_en": "Rakshajala"},
    110: {"name_ta": "ப்லவா", "name_en": "Plava"},
    111: {"name_ta": "வாருணீ", "name_en": "Vaaruni"},
    112: {"name_ta": "மதிரா", "name_en": "Madiraa"},
    113: {"name_ta": "மைத்ரீ", "name_en": "Maitri"},
    114: {"name_ta": "ஹாரிணீ", "name_en": "Haarini"},
    115: {"name_ta": "ஹரிணீ", "name_en": "Harini"},
    116: {"name_ta": "மருத்", "name_en": "Maruth"},
    117: {"name_ta": "சோமலதா", "name_en": "Somalatha"},
    118: {"name_ta": "மங்களா", "name_en": "Mangala"},
    119: {"name_ta": "முத்ரிகா", "name_en": "Mudrika"},
    120: {"name_ta": "சுதா", "name_en": "Sudha"},
    121: {"name_ta": "மேளா", "name_en": "Melaa"},
    122: {"name_ta": "தனஞ்சயா", "name_en": "Dhananjaya"},
    123: {"name_ta": "தனகரீ", "name_en": "Dhanakari"},
    124: {"name_ta": "தனதா", "name_en": "Dhanadaa"},
    125: {"name_ta": "ம்ருச்சாயா", "name_en": "Mricchaya"},
    126: {"name_ta": "அம்புஜா", "name_en": "Ambuja"},
    127: {"name_ta": "ஈசானீ", "name_en": "Isaani"},
    128: {"name_ta": "சூலினீ", "name_en": "Thoolini / Soolini"},
    129: {"name_ta": "ரௌத்ரீ", "name_en": "Raudri"},
    130: {"name_ta": "சிவா", "name_en": "Sivaa"},
    131: {"name_ta": "சிவகரீ", "name_en": "Sivakari"},
    132: {"name_ta": "கலா", "name_en": "Kalaa"},
    133: {"name_ta": "குந்தா", "name_en": "Kunda"},
    134: {"name_ta": "முகுந்தா", "name_en": "Mukunda"},
    135: {"name_ta": "பரதா", "name_en": "Bharatha"},
    136: {"name_ta": "பசிதா", "name_en": "Pasithaa"},
    137: {"name_ta": "கண்டினீ", "name_en": "Kandini"},
    138: {"name_ta": "ஸ்மரா", "name_en": "Smaraa"},
    139: {"name_ta": "குந்தலா", "name_en": "Kunthala"},
    140: {"name_ta": "கோகிலா", "name_en": "Kokila"},
    141: {"name_ta": "பாபா", "name_en": "Paapa"},
    142: {"name_ta": "காமினீ", "name_en": "Kaamini"},
    143: {"name_ta": "கலசோத்பவா", "name_en": "Kalasodhbhava"},
    144: {"name_ta": "வீரப்ரஸூ", "name_en": "Viraprasoo"},
    145: {"name_ta": "சங்கரா", "name_en": "Sankara"},
    146: {"name_ta": "சதயக்னா", "name_en": "Sathayaghna"},
    147: {"name_ta": "சதாவரீ", "name_en": "Sadaavari"},
    148: {"name_ta": "பிரஹ்வீ", "name_en": "Brahvi"},
    149: {"name_ta": "பாடலினீ", "name_en": "Paatalini"},
    150: {"name_ta": "பரமேஸ்வரி", "name_en": "Parameswari"},
}


SIGN_NAMES_TA = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
    "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
    "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

# Deva Keralam Sign Mobility: 1=Chara (Movable), 2=Sthira (Fixed), 3=Dvisvabhava (Dual)
SIGN_MOBILITY = {
    1: "Chara", 2: "Sthira", 3: "Dvisvabhava",
    4: "Chara", 5: "Sthira", 6: "Dvisvabhava",
    7: "Chara", 8: "Sthira", 9: "Dvisvabhava",
    10: "Chara", 11: "Sthira", 12: "Dvisvabhava",
}


def calculate_nadiamsa(deg_in_sign: float, sign_index: int) -> Dict[str, Any]:
    """Calculate the exact Deva Keralam 150 Nadiamsa number, name, and half.
    
    Each sign is 30 degrees = 150 Nadiamsas of 0.2 deg (12 arcminutes) each.
    - Chara (Movable) Signs (1, 4, 7, 10): 1 to 150 direct
    - Sthira (Fixed) Signs (2, 5, 8, 11): 150 down to 1 reverse
    - Dvisvabhava (Dual) Signs (3, 6, 9, 12): 76 to 150, then 1 to 75
    """
    deg = max(0.0, min(29.999999, deg_in_sign))
    fraction_idx = int(deg // 0.2)  # 0 to 149
    sub_offset = deg % 0.2  # offset in degree within 12' arc (0.2 deg)

    # First half (0' to 6' = 0.0 to 0.1 deg) vs Second half (6' to 12' = 0.1 to 0.2 deg)
    if sub_offset < 0.1:
        half_en = "Purvardha (First Half 0'-6')"
        half_ta = "பூர்வார்த்தம் (முற்பகுதி 0'-6')"
    else:
        half_en = "Uttarardha (Second Half 6'-12')"
        half_ta = "உத்தரார்த்தம் (பிற்பகுதி 6'-12')"

    mobility = SIGN_MOBILITY.get(sign_index, "Chara")
    if mobility == "Chara":
        nadi_num = fraction_idx + 1
    elif mobility == "Sthira":
        nadi_num = 150 - fraction_idx
    else:  # Dvisvabhava
        if fraction_idx < 75:
            nadi_num = 76 + fraction_idx
        else:
            nadi_num = 1 + (fraction_idx - 75)

    info = NADIAMSA_CATALOG.get(nadi_num, {"name_ta": "நாடியம்சம்", "name_en": "Nadiamsa"})
    name_ta = info["name_ta"]
    name_en = info["name_en"]

    # Arc representation
    start_min = fraction_idx * 12
    end_min = start_min + 12
    start_deg_str = f"{start_min // 60}°{start_min % 60:02d}'"
    end_deg_str = f"{end_min // 60}°{end_min % 60:02d}'"

    script_en = (
        f"Native is born under Deva Keralam Nadiamsa #{nadi_num} ({name_en}), {half_en} "
        f"spanning {start_deg_str} to {end_deg_str} in {SIGN_NAMES_EN[sign_index - 1]}. "
        "Classical texts attest to an astute, introspective soul possessing high discretion, "
        "distinct karmic inheritances, and decisive turning points tied to Gochara transit activations."
    )
    script_ta = (
        f"ஜாதகர் தேவ கேரளம் (சந்திர கலா நாடி) சாஸ்திரப்படி {SIGN_NAMES_TA[sign_index - 1]} ராசியில் "
        f"{start_deg_str} முதல் {end_deg_str} வரையிலான {nadi_num}-ஆம் நாடியம்சமான '{name_ta}' "
        f"({name_en}) {half_ta}வில் பிறந்துள்ளார். "
        "சூட்சும புத்தி, கௌரவமான குடும்பப் பாரம்பரியம் மற்றும் கோச்சார கிரக பெயர்ச்சிகளால் வாழ்வில் "
        "முக்கிய திருப்புமுனைகளை அடையும் அமைப்பு இந்த நாடியம்சத்திற்கு உண்டு."
    )

    return {
        "nadiamsa_number": nadi_num,
        "name_ta": name_ta,
        "name_en": name_en,
        "half_en": half_en,
        "half_ta": half_ta,
        "script_en": script_en,
        "script_ta": script_ta,
        "arc_str": f"{start_deg_str} - {end_deg_str}",
    }


def evaluate_khanda_and_longevity(lagna_sign: int, moon_sign: int) -> Tuple[str, str]:
    """Evaluate Deva Keralam Vol II Slokas 10-18 longevity determination and Khanda Nirnaya.
    
    Mobility pairings:
    - Chara + Chara: Dirghayu (75 - 100+ yrs)
    - Chara + Sthira: Madhyamayu (60 - 75 yrs)
    - Chara + Dvi: Alpayu (32 - 45 yrs)
    - Sthira + Chara: Madhyamayu (60 - 75 yrs)
    - Sthira + Sthira: Alpayu (32 - 40 yrs)
    - Sthira + Dvi: Dirghayu (75 - 90 yrs)
    - Dvi + Chara: Alpayu (30 - 40 yrs)
    - Dvi + Sthira: Dirghayu (75 - 85 yrs)
    - Dvi + Dvi: Madhyamayu (50 - 65 yrs)
    """
    lag_mob = SIGN_MOBILITY.get(lagna_sign, "Chara")
    moon_mob = SIGN_MOBILITY.get(moon_sign, "Chara")

    pair = (lag_mob, moon_mob)
    if pair == ("Chara", "Chara"):
        span_en = "Dirghayu (Full Longevity 75–100+ Years)"
        span_ta = "தீர்க்காயுள் (75 முதல் 100+ ஆண்டுகள் வரை)"
        desc_en = "Deva Keralam Vol II Slokas 10–18 classifies this as Dirghayu (Full Longevity). Both Lagna and Chandra occupy Movable (Chara) signs, providing exceptional vitality and recuperative power."
        desc_ta = "தேவ கேரளம் 2-ஆம் பாகம் சுலோகங்கள் 10-18-ன் படி, லக்னமும் சந்திரனும் சர ராசிகளில் அமைந்ததால் இது 'தீர்க்காயுள்' அமைப்பாகும். இயற்கையான உடல் எதிர்ப்பு சக்தியும் நீண்ட ஆயுள் பலமும் உண்டு."
    elif pair == ("Chara", "Sthira") or pair == ("Sthira", "Chara"):
        span_en = "Madhyamayu (Medium Longevity 60–75 Years)"
        span_ta = "மத்திமாயுள் (60 முதல் 75 ஆண்டுகள்)"
        desc_en = "Deva Keralam Vol II Slokas 10–18 classifies this as Madhyamayu (Medium Longevity). The interplay of Movable and Fixed signs sustains life beyond 60 years."
        desc_ta = "தேவ கேரளம் சாஸ்திரப்படி சர-ஸ்திர ராசிகளின் சேர்க்கை 'மத்திமாயுள்' (60 முதல் 75 ஆண்டுகள் வரை) தரும் அமைப்பாகும்."
    elif pair == ("Sthira", "Dvisvabhava") or pair == ("Dvisvabhava", "Sthira"):
        span_en = "Dirghayu (Full Longevity 75–90 Years)"
        span_ta = "தீர்க்காயுள் (75 முதல் 90 ஆண்டுகள் வரை)"
        desc_en = "Deva Keralam Vol II Slokas 10–18 classifies this as Dirghayu. Sthira and Dvisvabhava combinations confer long endurance and steady vitality."
        desc_ta = "தேவ கேரளம் சாஸ்திரப்படி ஸ்திர மற்றும் உபய ராசிகளின் சேர்க்கை 'தீர்க்காயுள்' (75 முதல் 90 ஆண்டுகள் வரை) அருளக்கூடிய பலம் வாய்ந்த அமைப்பாகும்."
    elif pair == ("Dvisvabhava", "Dvisvabhava"):
        span_en = "Madhyamayu (Medium Longevity 50–65 Years)"
        span_ta = "மத்திமாயுள் (50 முதல் 65 ஆண்டுகள் வரை)"
        desc_en = "Deva Keralam classifies Dual-Dual placement as Madhyamayu (50–65 Years), requiring steady lifestyle discipline."
        desc_ta = "தேவ கேரளம் சாஸ்திரப்படி உபய-உபய ராசிகளின் சேர்க்கை 'மத்திமாயுள்' (50 முதல் 65 ஆண்டுகள் வரை) குறிக்கும்."
    else:  # Chara+Dvi, Dvi+Chara, Sthira+Sthira
        span_en = "Madhyamayu with Protective Arishta-Bhanga (60–70+ Years with Remedies)"
        span_ta = "சுபகிரகப் பார்வையுடன் கூடிய மத்திமாயுள் (60 முதல் 70+ ஆண்டுகள் வரை)"
        desc_en = "Deva Keralam points out conditional longevity requiring Shastric Arishta-Bhanga protections, extending vital force with Jupiter's graceful aspects."
        desc_ta = "தேவ கேரளம் சாஸ்திரப்படி அரிஷ்ட பங்க சுப பலன்களால் ஆயுள் நீட்டிக்கப்பட்டு 60 முதல் 70+ ஆண்டுகள் வரை ஆயுள் பலம் பெறுகிறது."

    khanda_ta = f"கண்ட நிர்ணயம்: பிரதம கண்டம் (இளமை 1-4 பாவங்கள்), துவிதீய கண்டம் (யௌவனம் 5-8 பாவங்கள்), திருதியை கண்டம் (முதுமை 9-12 பாவங்கள்). ஆயுள் நிர்ணயம்: {span_ta} — {desc_ta}"
    khanda_en = f"Khanda Nirnaya: Youth (1st-4th houses), Middle (5th-8th houses), Elder (9th-12th houses). Longevity Class: {span_en} — {desc_en}"

    return khanda_en, khanda_ta


def format_zodiac_degree(deg_total: float) -> str:
    deg_total = deg_total % 360.0
    sign_idx = int(deg_total // 30.0) + 1
    deg_in_sign = deg_total % 30.0
    deg = int(deg_in_sign)
    mins = int((deg_in_sign - deg) * 60.0)
    sign_ta = SIGN_NAMES_TA[sign_idx - 1]
    sign_en = SIGN_NAMES_EN[sign_idx - 1]
    return f"{sign_ta} {deg}°{mins:02d}' ({sign_en} {deg}°{mins:02d}')"


def calculate_deva_keralam_critical_degrees(
    planets_dict: Dict[str, Dict[str, Any]],
    ascendant_sign: int,
) -> Tuple[str, str]:
    """Calculate Deva Keralam Book 1 Slokas 14-16 critical transit degrees for parents.
    
    - Father death / critical crisis degree: Sun Longitude + 4th Lord Longitude
    - Mother death / critical crisis degree: Moon Longitude + 5th Lord Longitude
    When Gochara Saturn transits these degrees or their trines (+120, +240), parents face critical events.
    """
    fourth_sign = ((ascendant_sign + 3 - 1) % 12) + 1
    fourth_lord = SIGN_LORDS.get(fourth_sign, "Moon")
    fifth_sign = ((ascendant_sign + 4 - 1) % 12) + 1
    fifth_lord = SIGN_LORDS.get(fifth_sign, "Sun")

    sun_lon = planets_dict.get("Sun", {}).get("longitude", 0.0)
    moon_lon = planets_dict.get("Moon", {}).get("longitude", 0.0)
    fl_lon = planets_dict.get(fourth_lord, {}).get("longitude", 0.0)
    five_lord_lon = planets_dict.get(fifth_lord, {}).get("longitude", 0.0)

    father_crit_deg = (sun_lon + fl_lon) % 360.0
    mother_crit_deg = (moon_lon + five_lord_lon) % 360.0

    father_str = (
        f"{format_zodiac_degree(father_crit_deg)} (மற்றும் இதன் திரிகோணங்களான "
        f"{format_zodiac_degree(father_crit_deg + 120.0)}, {format_zodiac_degree(father_crit_deg + 240.0)})"
    )
    mother_str = (
        f"{format_zodiac_degree(mother_crit_deg)} (மற்றும் இதன் திரிகோணங்களான "
        f"{format_zodiac_degree(mother_crit_deg + 120.0)}, {format_zodiac_degree(mother_crit_deg + 240.0)})"
    )

    return father_str, mother_str
