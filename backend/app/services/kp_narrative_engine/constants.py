"""Constants and astrological mapping dictionaries for KP Predictive Narrative Engine."""

from typing import Dict, List, Set, Any

# Planet Names in English and Tamil
PLANET_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு (வியாழன்)",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி பகவான்",
    "Rahu": "ராகு",
    "Ketu": "கேது",
}

# Zodiac Signs in English and Tamil
SIGN_NAMES_TA: Dict[str, str] = {
    "Aries": "மேஷம்",
    "Taurus": "ரிஷபம்",
    "Gemini": "மிதுனம்",
    "Cancer": "கடகம்",
    "Leo": "சிம்மம்",
    "Virgo": "கன்னி",
    "Libra": "துலாம்",
    "Scorpio": "விருச்சிகம்",
    "Sagittarius": "தனுசு",
    "Capricorn": "மகரம்",
    "Aquarius": "கும்பம்",
    "Pisces": "மீனம்",
}

# 27 Nakshatras in Tamil
NAKSHATRA_NAMES_TA: Dict[str, str] = {
    "Ashwini": "அசுவினி",
    "Bharani": "பரணி",
    "Krittika": "கார்த்திகை",
    "Rohini": "ரோகிணி",
    "Mrigashira": "மிருகசீரிஷம்",
    "Ardra": "திருவாதிரை",
    "Punarvasu": "புனர்பூசம்",
    "Pushya": "பூசம்",
    "Ashlesha": "ஆயில்யம்",
    "Magha": "மகம்",
    "Purva Phalguni": "பூரம்",
    "Uttara Phalguni": "உத்திரம்",
    "Hasta": "அஸ்தம்",
    "Chitra": "சித்திரை",
    "Svati": "சுவாதி",
    "Vishakha": "விசாகம்",
    "Anuradha": "அனுஷம்",
    "Jyeshtha": "கேட்டை",
    "Mula": "மூலம்",
    "Purva Ashadha": "பூராடம்",
    "Uttara Ashadha": "உத்திராடம்",
    "Shravana": "திருவோணம்",
    "Dhanishta": "அவிட்டம்",
    "Shatabhisha": "சதயம்",
    "Purva Bhadrapada": "பூரட்டாதி",
    "Uttara Bhadrapada": "உத்திரட்டாதி",
    "Revati": "ரேவதி",
}

# The 6 Primary Cusps for Natal Event Promise per user specification:
# 1st, 2nd, 5th, 7th, 10th, 11th
PRIMARY_PROMISE_CUSPS = [1, 2, 5, 7, 10, 11]

CUSP_DOMAINS: Dict[int, Dict[str, str]] = {
    1: {
        "domain_en": "Physical Constitution, Vitality & Self-Elevation",
        "domain_ta": "உடல் நலம், ஆயுள் பலம் & சுய ஆளுமை",
        "short_en": "Life Vitality & Constitution",
        "short_ta": "ஆயுள் & தேக ஆரோக்கியம்",
    },
    2: {
        "domain_en": "Wealth Accumulation, Liquidity & Family Harmony",
        "domain_ta": "தன சேர்க்கை, பணப்புழக்கம் & குடும்ப நலம்",
        "short_en": "Wealth & Finances",
        "short_ta": "தன வரவு & சேமிப்பு",
    },
    5: {
        "domain_en": "Children, Creative Intellect & Speculative Fortune",
        "domain_ta": "புத்திர பாக்கியம், அறிவு & படைப்பாற்றல்",
        "short_en": "Children & Creative Intellect",
        "short_ta": "குழந்தை பாக்கியம் & கலை அறிவு",
    },
    7: {
        "domain_en": "Matrimony, Life Partner & Partnerships",
        "domain_ta": "திருமண பந்தம், வாழ்க்கை துணை & கூட்டாண்மை",
        "short_en": "Marriage & Relationships",
        "short_ta": "திருமணம் & தாம்பத்தியம்",
    },
    10: {
        "domain_en": "Career Trajectory, Status & Professional Leadership",
        "domain_ta": "தொழில் மேன்மை, பதவி உயர்வு & சமூக அந்தஸ்து",
        "short_en": "Career & Reputation",
        "short_ta": "தொழில் & உத்தியோகம்",
    },
    11: {
        "domain_en": "Fulfillment of Aspirations, Windfalls & Desires",
        "domain_ta": "ஆசைகள் நிறைவேறுதல், லாபங்கள் & நல்வாய்ப்புகள்",
        "short_en": "Gains & Desires Fulfillment",
        "short_ta": "லாபம் & விருப்ப ஈடேற்றம்",
    },
}

# KP Supportive and Challenging Houses for the 6 primary cusps
CUSP_SUPPORTIVE_HOUSES: Dict[int, Set[int]] = {
    1: {1, 2, 3, 10, 11},       # Long life, strong vitality, status
    2: {2, 6, 10, 11},          # Wealth accumulation, bank balance
    5: {2, 5, 11},              # Progeny, speculative success, high intelligence
    7: {2, 7, 11},              # Happy marriage, union, stability
    10: {2, 6, 10, 11},         # Solid career, promotion, respect
    11: {1, 2, 3, 6, 10, 11},   # Success in all ventures, realization of goals
}

CUSP_CHALLENGING_HOUSES: Dict[int, Set[int]] = {
    1: {6, 8, 12},              # Illness, anxiety, accidents, hospitalization
    2: {5, 8, 12},              # Sudden expenses, loss of savings, disputes
    5: {1, 4, 10, 6, 8, 12},    # Obstacles to progeny (4th is 12th to 5th), speculative drops
    7: {1, 6, 10, 12},          # Discord, separation (6th is 12th to 7th, 1st & 10th negation)
    10: {5, 8, 9, 12},          # Loss of status, sudden retirement (5th is 8th to 10th, 9th is 12th to 10th)
    11: {8, 12},                # Frustration of hopes, unexpected deficits
}

# Planetary Deities, Charities, Colors, and Days
PLANETARY_REMEDIES: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "deity_en": "Lord Shiva or Surya Bhagavan (Gayatri Mantra meditation)",
        "deity_ta": "சிவபெருமான் அல்லது ஸ்ரீ சூரிய பகவான் (ஆதித்ய ஹிருதய ஸ்தோத்திரம் / காயத்ரி)",
        "charity_en": "Donate whole wheat, copper vessels, or provide breakfast/food at sunrise to the needy.",
        "charity_ta": "கோதுமை, செம்பு பாத்திரங்கள் அல்லது காலையில் ஏழைகளுக்கு அன்னதானம் செய்தல்.",
        "lucky_days_en": "Sunday",
        "lucky_days_ta": "ஞாயிற்றுக்கிழமை",
        "lucky_color_en": "Ruby red, saffron, orange, bright gold",
        "lucky_color_ta": "செந்நிறம், காவி, ஆரஞ்சு, தங்க நிறம்",
        "habit_en": "Wake up before sunrise, maintain absolute transparency and respect for father and superiors.",
        "habit_ta": "சூரிய உதயத்திற்கு முன் எழுதல், தந்தையிடமும் மேலதிகாரிகளிடமும் மதிப்புடன் நடத்தல்.",
    },
    "Moon": {
        "deity_en": "Goddess Parvati or Lord Venkateswara / Chandra Bhagavan",
        "deity_ta": "அன்னை ஸ்ரீ பார்வதி அல்லது ஸ்ரீ சந்திர பகவான் (சந்திர காயத்ரி)",
        "charity_en": "Donate milk, raw rice, silver coins, or drinking water facilities to public or elderly women.",
        "charity_ta": "பால், பச்சரிசி அல்லது தாகம் தணிக்கும் குடிநீர் வசதியை ஏழை எளியோர்க்கு வழங்குதல்.",
        "lucky_days_en": "Monday",
        "lucky_days_ta": "திங்கட்கிழமை",
        "lucky_color_en": "Pearl white, silver, cream",
        "lucky_color_ta": "முத்து வெள்ளை, வெள்ளி, சந்தன நிறம்",
        "habit_en": "Keep evening hours calm, avoid overthinking before sleep, cherish relationship with mother.",
        "habit_ta": "இரவில் அதிக யோசனைகளை தவிர்த்தல், தாயாருக்கு பணிவிடை செய்து ஆசி பெறுதல்.",
    },
    "Mars": {
        "deity_en": "Lord Muruga (Kartikeya) or Lord Subramanya / Angaraka",
        "deity_ta": "முழுமுதற் கடவுள் ஸ்ரீ முருகப் பெருமான் (கந்த சஷ்டி கவசம் / சுப்பிரமணியர்)",
        "charity_en": "Donate red lentils (tuvar dal / masoor dal), blood donation, or tools to workers.",
        "charity_ta": "துவரம்பருப்பு, சிவப்பு வஸ்திரம் அல்லது குருதிக்கொடை (Blood Donation) செய்தல்.",
        "lucky_days_en": "Tuesday",
        "lucky_days_ta": "செவ்வாய்க்கிழமை",
        "lucky_color_en": "Coral red, deep vermilion, brick red",
        "lucky_color_ta": "பவள சிவப்பு, இரத்த சிவப்பு",
        "habit_en": "Channel anger into constructive workouts, avoid road rage and rushed decisions.",
        "habit_ta": "கோபத்தை உடற்பயிற்சியாக மாற்றுதல், அவசர முடிவுகள் மற்றும் வாகனப் பயணத்தில் நிதானம்.",
    },
    "Mercury": {
        "deity_en": "Lord Maha Vishnu or Sri Hayagriva (Vishnu Sahasranamam)",
        "deity_ta": "ஸ்ரீ மகாவிஷ்ணு அல்லது ஸ்ரீ ஹயக்ரீவர் (விஷ்ணு சஹஸ்ரநாமம்)",
        "charity_en": "Donate educational books, stationery, or green moong dal to impoverished students.",
        "charity_ta": "பச்சைப்பயறு, ஏழை மாணவர்களுக்கு கல்வி உபகரணங்கள் மற்றும் நோட்டுப் புத்தகங்கள் வழங்குதல்.",
        "lucky_days_en": "Wednesday",
        "lucky_days_ta": "புதன்கிழமை",
        "lucky_color_en": "Emerald green, light mint green",
        "lucky_color_ta": "மரகத பச்சை, கிளிப்பச்சை",
        "habit_en": "Read thoroughly before signing documents; maintain polite, objective email communication.",
        "habit_ta": "ஆவணங்களில் கையெழுத்திடும் முன் சரிபார்த்தல், நிதானமான மற்றும் தெளிவான பேச்சு.",
    },
    "Jupiter": {
        "deity_en": "Lord Dakshinamurthy or Guru Brihaspati / Sri Raghavendra",
        "deity_ta": "ஸ்ரீ மேதா தட்சிணாமூர்த்தி அல்லது ஸ்ரீ குரு பகவான் / ஸ்ரீ ராகவேந்திரர்",
        "charity_en": "Donate yellow chickpeas (chana dal), turmeric, yellow flowers, or support spiritual teachers.",
        "charity_ta": "கொண்டைக்கடலை, மஞ்சள், மஞ்சள் நிற வஸ்திரம் அல்லது ஆன்மீக ஆசான்களுக்கு உதவுதல்.",
        "lucky_days_en": "Thursday",
        "lucky_days_ta": "வியாழக்கிழமை",
        "lucky_color_en": "Golden yellow, canary yellow, amber",
        "lucky_color_ta": "தங்க மஞ்சள், குரு மஞ்சள்",
        "habit_en": "Engage in continuous learning, mentor juniors with kindness, practice ethical financial stewardship.",
        "habit_ta": "பெரியோர்களை மதித்தல், நற்பண்புகளுடன் கூடிய நேர்மையான நிதி மேலாண்மை கடைப்பிடித்தல்.",
    },
    "Venus": {
        "deity_en": "Goddess Mahalakshmi or Sri Ranganatha (Sri Suktam)",
        "deity_ta": "அன்னை ஸ்ரீ மகாலட்சுமி அல்லது ஸ்ரீ ரங்கநாதர் (ஸ்ரீ சூக்தம்)",
        "charity_en": "Donate white silk, clarified butter (ghee), sweets, or provide support to artists / brides.",
        "charity_ta": "வெள்ளை பட்டு, நெய், இனிப்பு அல்லது எளிய குடும்பத்து திருமணங்களுக்கு சீர்வரிசை வழங்குதல்.",
        "lucky_days_en": "Friday",
        "lucky_days_ta": "வெள்ளிக்கிழமை",
        "lucky_color_en": "Silk white, pastel pink, soft cream",
        "lucky_color_ta": "பட்டு வெள்ளை, ரோஜா நிறம், வெளிர் இளஞ்சிவப்பு",
        "habit_en": "Maintain neat personal grooming, foster loving patience in domestic life, appreciate beauty.",
        "habit_ta": "சுத்தமும் நேர்த்தியும் பேணுதல், வாழ்க்கைத் துணையிடம் அன்பும் மரியாதையும் காட்டுதல்.",
    },
    "Saturn": {
        "deity_en": "Lord Shani Bhagavan, Lord Sastha (Ayyappa), or Lord Hanuman",
        "deity_ta": "ஸ்ரீ சனீஸ்வர பகவான், ஸ்ரீ தர்ம சாஸ்தா (ஐயப்பன்) அல்லது ஸ்ரீ ஆஞ்சநேயர்",
        "charity_en": "Donate black sesame seeds, sesame oil, dark blankets, or footwear to elderly laborers.",
        "charity_ta": "கருப்பு எள், நல்லெண்ணெய் தீபம், கம்பளி ஆடைகள் அல்லது முதிய தொழிலாளர்களுக்கு செருப்பு வழங்குதல்.",
        "lucky_days_en": "Saturday",
        "lucky_days_ta": "சனிக்கிழமை",
        "lucky_color_en": "Midnight blue, charcoal navy, dark slate",
        "lucky_color_ta": "கருநீலம், அடர் நீலம்",
        "habit_en": "Practice disciplined punctuality, never humiliate service workers, persevere without complaining.",
        "habit_ta": "காலந்தவறாமை, உழைப்பாளிகளை மரியாதையுடன் நடத்துதல், பொறுமையுடன் கடமையைச் செய்தல்.",
    },
    "Rahu": {
        "deity_en": "Goddess Durga or Sri Nagaraja / Rahu Bhagavan (Durga Ashtakam)",
        "deity_ta": "அன்னை ஸ்ரீ துர்க்கை அல்லது ஸ்ரீ நாகராஜர் (ராகு கால துர்க்கை பூஜை)",
        "charity_en": "Donate black urad dal, mustard seeds, or support orphanages / medical relief for chronic patients.",
        "charity_ta": "உளுந்து, எலுமிச்சை மாலை, அல்லது ஆதரவற்றோர் இல்லங்களுக்கு மருத்துவ உதவி செய்தல்.",
        "lucky_days_en": "Tuesday / Friday (Rahu Kalam)",
        "lucky_days_ta": "செவ்வாய் / வெள்ளி (ராகு காலம்)",
        "lucky_color_en": "Smoky blue, violet, iridescent dark blue",
        "lucky_color_ta": "புகை நீலம், கருநீலம்",
        "habit_en": "Avoid sudden get-rich-quick gambles; verify credentials online; keep mental focus grounded.",
        "habit_ta": "குறுக்கு வழி பேராசைகளை தவிர்த்தல், போலி முதலீடுகளில் விழிப்புடன் இருத்தல்.",
    },
    "Ketu": {
        "deity_en": "Lord Ganesha (Vinayagar) or Lord Chitragupta (Ganesha Atharvashirsha)",
        "deity_ta": "முழுமுதற் கடவுள் ஸ்ரீ கணபதி (விநாயகர் அகவல் / சங்கடஹர சதுர்த்தி)",
        "charity_en": "Donate horse gram (kollu), multi-colored blankets, or feed stray dogs.",
        "charity_ta": "கொள்ளு, பலவண்ண கம்பளி அல்லது ஆதரவற்ற நாய்களுக்கு உணவு வழங்குதல்.",
        "lucky_days_en": "Tuesday / Thursday",
        "lucky_days_ta": "செவ்வாய் / வியாழக்கிழமை",
        "lucky_color_en": "Smoky grey, saffron-brown, terracotta",
        "lucky_color_ta": "சாம்பல் நிறம், காவி-பழுப்பு",
        "habit_en": "Practice deep meditation, study philosophy, release past grievances, practice detachment.",
        "habit_ta": "தினசரி தியானம், மனக்கசப்புகளை மறந்து மன்னித்தல், ஆன்மீக நூல்களைப் படித்தல்.",
    },
}
