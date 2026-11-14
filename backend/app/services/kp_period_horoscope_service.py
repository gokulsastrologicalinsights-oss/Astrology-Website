"""KP Weekly and Monthly Horoscope & Transit Prediction Engine.

Computes comprehensive Weekly and Monthly astrological forecasts for all 12 Rashis
using Krishnamurti Paddhati (KP) sub-lord principles, Gochara (transit) mechanics,
and high-precision XALEN ephemeris.

Provides:
1. Complete planetary transit positions & ingress events (Sun, Moon, Mars, Mercury,
   Jupiter, Venus, Saturn, Rahu, Ketu)
2. Gochara house effects and transit summaries per Rashi (English & Tamil)
3. Chandrashtama warnings (exact days in week, date spans in month)
4. Special yogas (Guru Balan, Sade Sati, Ashtama Shani, Kantaka Shani)
5. 5 Granular Life Aspects (Career, Finance, Love, Health, Travel/Studies)
6. Executive Weekly/Monthly Briefs, Peak Opportunities, Caution Traps
7. Lucky days/dates, colors, numbers, directions, and period remedies
"""

from __future__ import annotations

import calendar
import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

import xalen

from app.schemas.kp_daily_horoscope import (
    KpAspectPrediction,
    KpMonthlyHoroscopeResponse,
    KpWeeklyHoroscopeResponse,
    RashiMonthlyPrediction,
    RashiWeeklyPrediction,
    TransitMovement,
    TransitSummaryPerRashi,
)
from app.services.ephemeris import AYANAMSA_NAMES
from app.services.kp_daily_horoscope_service import (
    MOON_HOUSE_INTERPRETATIONS,
    PLANET_IDS,
    RASHI_LUCKY_ATTRIBUTES,
    RASHI_METADATA,
    SIGN_TO_INDEX,
    WEEKDAY_INFO,
    _calc_house_relative,
)
from app.services.kp_engine.constants import (
    NAKSHATRAS,
    PLANET_ABBR,
    SIGN_LORDS,
    SIGNS,
    SIGNS_RULED_BY,
)
from app.services.kp_engine.vedic import normalize_longitude, point_info
from app.services.timezone_utils import resolve_birth_datetime

logger = logging.getLogger(__name__)

PLANET_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "ராகு",
    "Ketu": "கேது",
}

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

MONTHS_TA: Dict[int, str] = {
    1: "ஜனவரி", 2: "பிப்ரவரி", 3: "மார்ச்", 4: "ஏப்ரல்", 5: "மே", 6: "ஜூன்",
    7: "ஜூலை", 8: "ஆகஸ்ட்", 9: "செப்டம்பர்", 10: "அக்டோபர்", 11: "நவம்பர்", 12: "டிசம்பர்",
}

MONTHS_EN: Dict[int, str] = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}

# Gochara Benefic Houses relative to Janma / Chandra Rashi
BENEFIC_TRANSIT_HOUSES: Dict[str, Set[int]] = {
    "Sun": {3, 6, 10, 11},
    "Moon": {1, 3, 6, 7, 10, 11},
    "Mars": {3, 6, 11},
    "Mercury": {2, 4, 6, 8, 10, 11},
    "Jupiter": {2, 5, 7, 9, 11},
    "Venus": {1, 2, 3, 4, 5, 8, 9, 11, 12},  # 6, 7, 10 unfavorable
    "Saturn": {3, 6, 11},
    "Rahu": {3, 6, 10, 11},
    "Ketu": {3, 6, 11},
}

# Detailed Gochara House Interpretations for Planets (English & Tamil)
PLANET_HOUSE_TRANSIT_IMPACT: Dict[str, Dict[int, Tuple[str, str]]] = {
    "Sun": {
        1: ("Vitality fluctuations; maintain emotional calm and avoid ego in leadership.", "உடல் உஷ்ணம் மற்றும் முன்கோபத்தைத் தவிர்த்து நிதானம் காப்பது நலம்."),
        2: ("Watch tone in family dialogues; exercise budget prudence.", "குடும்பப் பேச்சில் நிதானம் தேவை; பண வரவில் பட்ஜெட் கட்டுப்பாடு அவசியம்."),
        3: ("High courage, triumph over rivals, and success in bold communications.", "தைரியமும் முயற்சியும் கூடும்; போட்டிகளில் வெற்றி மற்றும் புதிய ஒப்பந்தங்கள் கைகூடும்."),
        4: ("Focus on domestic peace and property upkeep; balance home and work.", "வீடு, வாகன பராமரிப்பில் கவனம்; குடும்ப அமைதிக்கு முன்னுரிமை கொடுங்கள்."),
        5: ("Exercise prudence in investments; guide children with patient understanding.", "அவசர ஊக வணிகத்தைத் தவிர்க்கவும்; பிள்ளைகளின் நலனில் அக்கறை தேவை."),
        6: ("Shatru Jaya: Decisive victory over competition, clearance of hurdles and debts.", "சத்ரு ஜெய காலம்: எதிர்ப்புகளும் கடன்களும் அகலும்; தொழில் போட்டிகளில் வெற்றி."),
        7: ("Diplomacy required with partners and spouse; avoid unnecessary arguments.", "வாடிக்கையாளர்கள் மற்றும் வாழ்க்கை துணையிடம் விட்டுக்கொடுத்துச் செல்லவும்."),
        8: ("Caution with superiors; avoid legal haste and defer high-risk agreements.", "அரசு விவகாரங்கள் மற்றும் அதிகாரிகளிடம் நிதானம்; புதிய ஒப்பந்தங்களில் கவனம்."),
        9: ("Spiritual elevation, blessings from father or mentors, pilgrimage support.", "தந்தை மற்றும் பெரியோர்களின் ஆசி; ஆன்மீக ஈடுபாடும் புண்ணிய காரியங்களும் சிறக்கும்."),
        10: ("Peak career momentum, leadership honor, government favor, and professional status.", "தொழிலில் மதிப்பு மரியாதை கூடும்; மேலதிகாரிகள் மற்றும் அரசின் ஆதரவு உண்டு."),
        11: ("Outstanding financial inflows, realization of cherished goals, high prestige.", "பெரிய அளவிலான பணவரவு; விருப்பங்கள் யாவும் நிறைவேறும் பொன்னான காலம்."),
        12: ("Auspicious expenditures for worthy causes; foreign and spiritual links.", "சுப காரியங்களுக்கான செலவுகள்; அமைதியான ஆன்மீக தியானம் மன நிம்மதி தரும்."),
    },
    "Jupiter": {
        1: ("Wisdom, intellectual clarity, philosophical mindset, and personal growth.", "ஞானமும் நற்சிந்தனைகளும் பெருகும்; புதிய முயற்சிகளில் நல்ல தெளிவு பிறக்கும்."),
        2: ("Dhana Guru: Excellent wealth accumulation, family harmony, financial recovery.", "தன குரு: பணப்புழக்கம் சரளமாகும்; குடும்பத்தில் சுப காரியங்கள் கூடிவரும்."),
        3: ("Courageous initiatives, rewarding short travel, supportive communications.", "சுறுசுறுப்பான முயற்சிகளுக்கு அனுகூலம்; சகோதர ஆதரவும் பேச்சுவார்த்தை வெற்றியும் உண்டு."),
        4: ("Domestic bliss, peace of mind, blessings through mother and property gains.", "குடும்பத்தில் மன நிம்மதி; தாய் வழி ஆதரவு மற்றும் வீடு வாகன யோகம் கிட்டும்."),
        5: ("Poorva Punya: Supreme intellect, child happiness, creative and academic success.", "பூர்வ புண்ணிய பலம்; பிள்ளைகளால் பெருமை, கலை மற்றும் கல்வித் துறையில் சாதனை."),
        6: ("Wisdom helps overcome obstacles; steady resolution of debts and workplace tests.", "அறிவாற்றலால் தடைகள் அகலும்; அலுவலகத்தில் பொறுமையுடன் செயல்பட்டு வெற்றி பெறலாம்."),
        7: ("Kalathra Guru: Marital harmony, auspicious alliance talks, lucrative partnerships.", "களத்திர குரு: திருமணப் பேச்சுக்கள் கைகூடும்; கூட்டாண்மை தொழிலில் நல்ல லாபம்."),
        8: ("Deep research, spiritual awakening, handling inherited or hidden assets safely.", "ஆராய்ச்சி சிந்தனை மற்றும் ஆன்மீக ஈடுபாடு; ரகசிய விவகாரங்களில் விழிப்புணர்வு."),
        9: ("Bhagya Guru: Supreme divine fortune, pilgrimage, mentor blessings, high prestige.", "பாக்கிய குரு: தெய்வ அருள் துணை நிற்கும்; தொலைதூரப் பயணங்கள் மற்றும் புகழ் ஓங்கும்."),
        10: ("Professional ethics, promotion, leadership responsibilities, community respect.", "கர்ம ஸ்தானம்: உத்தியோகத்தில் நல்ல பெயர், புதிய பொறுப்புகள் மற்றும் அங்கீகாரம்."),
        11: ("Sarva Labha: Peak multi-stream inflows, fulfillment of desires, influential ties.", "சர்வ லாபம்: எதிர்பாராத தனலாபம்; முயற்சிகள் அனைத்தும் லாபகரமாக முடியும்."),
        12: ("Subha-vyaya: Auspicious charity, spiritual inclination, foreign opportunities.", "சுப விரயங்கள்; ஆன்மீக மற்றும் தர்ம காரியங்களில் மனம் நிறைவடையும்."),
    },
    "Saturn": {
        1: ("Janma Shani: Demands patience, disciplined stamina, and attention to wellness.", "ஜன்ம சனி: பொறுமையும் கடின உழைப்பும் அவசியம்; ஆரோக்கியத்தில் கூடுதல் கவனம்."),
        2: ("Padhuka Shani: Practice mindful speech and avoid impulsive financial spending.", "வாக்குஸ்தான சனி: பேச்சில் நிதானம் தேவை; வீண் விரயங்களைத் தவிர்க்கவும்."),
        3: ("Supreme courage, steadfast perseverance brings long-lasting foundation & wins.", "தைரிய ஸ்தான சனி: விடாமுயற்சிக்கு நிலையான வெற்றி; தடைகளைத் தகர்த்து முன்னேறுவீர்கள்."),
        4: ("Ardhastama Shani: Maintain domestic harmony; avoid rushing property disputes.", "அர்த்தாஷ்டம சனி: குடும்ப விவகாரங்களில் அமைதி காக்கவும்; தாயாரின் உடல்நலன் காக்க."),
        5: ("Focus on long-term investments; maintain patient communication with children.", "ஊக வணிகத்தைத் தவிர்க்கவும்; பிள்ளைகளிடம் கனிவாகப் பேசுவது நலம்."),
        6: ("Shatru Samhara: Elimination of adversaries, relief from lingering debts, endurance.", "சத்ரு சம்ஹாரம்: எதிர்ப்புகள் முறியடிக்கப்படும்; கடன் மற்றும் ஆரோக்கிய சுமை குறையும்."),
        7: ("Kantaka Shani: Professional diplomacy and transparency in mutual partnerships.", "கண்டக சனி: கூட்டாளிகளிடம் வெளிப்படைத்தன்மை; சமரசப் போக்கு நன்மை தரும்."),
        8: ("Ashtama Shani: Cautious commuting, health vigilance, defer high-risk ventures.", "அஷ்டம சனி: அமைதியான தியானம் அவசியம்; பயணங்கள் மற்றும் முதலீடுகளில் கவனம்."),
        9: ("Ethical conduct, respect for elders and spiritual discipline yield blessings.", "பெரியோர்களை மதித்து நடக்கவும்; தர்ம நெறிகளுடன் உழைத்தால் சுப பலன் உண்டு."),
        10: ("Career stamina: Diligent work ethic brings durable leadership recognition.", "தொழில் சனி: உழைப்பிற்கான நிலையான அங்கீகாரம்; பொறுப்புகள் கூடும்."),
        11: ("Subha Shani: High durable returns, long-term wealth, influential network gains.", "லாப சனி: நிலையான நிதி ஆதாயம்; பெரிய மனிதர்களின் ஆதரவும் புதிய வாய்ப்புகளும்."),
        12: ("Viraya Shani: Strict budget discipline, introspective meditation, avoidance of haste.", "விரய சனி: பட்ஜெட் கட்டுப்பாடு தேவை; ஆன்மீக வழிபாடு அமைதி தரும்."),
    },
    "Mars": {
        1: ("High dynamic drive; avoid haste while driving and channel energy constructively.", "அதிக வேகம்; முன்கோபத்தைத் தவிர்த்து விவேகமாக உழைப்பது நற்பலன் தரும்."),
        2: ("Direct speech; weigh your words in financial discussions to prevent friction.", "பேச்சில் கடுமையைத் தவிர்க்கவும்; நிதி சார்ந்த விவகாரங்களில் நிதானம் தேவை."),
        3: ("Dynamic bravery, property negotiations advance, decisive operational wins.", "தைரிய வீரியம் கூடும்; நிலம், வீடு விவகாரங்கள் சுமுகமாக முடியும்."),
        4: ("Temperamental patience at home; ensure vehicle safety and domestic harmony.", "குடும்பத்தில் அமைதி காக்கவும்; வாகனங்களை கவனமாக இயக்குவது நலம்."),
        5: ("Avoid speculative gambles; channel passion into creative and sporty endeavors.", "முதலீடுகளில் அவசரம் வேண்டாம்; புத்தி கூர்மையுடன் செயல்படவும்."),
        6: ("Unstoppable victory over competition, energetic dispute resolution, high drive.", "போட்டிகளையும் எதிர்ப்புகளையும் துவம்சம் செய்யும் ஆற்றல்; கடன்கள் தீரும்."),
        7: ("Cooperative attitude in marital and partnership affairs; avoid confrontational stance.", "களத்திர மற்றும் கூட்டுத் தொழிலில் சகிப்புத்தன்மை அவசியம்; வாக்குவாதம் தவிர்த்தல்."),
        8: ("High vigilance required while driving and handling machinery; practice mindfulness.", "வாகனம் மற்றும் எந்திரங்களை இயக்கும் போது கூடுதல் விழிப்புணர்வு தேவை."),
        9: ("Moral courage; travel plans require clear schedules; honor father's guidance.", "தூரப் பயணங்களில் முன் தயாரிப்பு தேவை; தர்ம நெறிகளைக் கடைப்பிடிக்கவும்."),
        10: ("Kuladeepam: High administrative drive, victory in professional projects, leadership.", "உத்தியோகத்தில் அதிரடி முன்னேற்றம்; புதிய திட்டங்களை தலைமை தாங்கி முடிப்பீர்கள்."),
        11: ("Profits from real estate, machinery, technical ventures, and energetic allies.", "நிலம் மற்றும் தொழில் மூலமாக அதிக பணவரவு; நண்பர்கள் உறுதுணையாக நிற்பர்."),
        12: ("Control impulsiveness; monitor travel and medical budgets cautiously.", "தேவையற்ற அவசர செலவுகளைக் கட்டுப்படுத்தவும்; நிதானமான நடைமுறை நலம் தரும்."),
    },
    "Venus": {
        1: ("Charming personality, joy, artistic appreciation, and mutual attraction.", "முகப்பொலிவும் கவர்ச்சியும் கூடும்; கலை மற்றும் மகிழ்ச்சியான சூழல் நிலவும்."),
        2: ("Delightful family gatherings, monetary inflows, purchase of quality comforts.", "குடும்பத்தில் மகிழ்ச்சி; பணப்புழக்கம் மற்றும் ஆடை ஆபரண சேர்க்கை உண்டு."),
        3: ("Cordial relations with siblings, enjoyable short trips, engaging communication.", "இனிமையான பயணங்கள்; தகவல் தொடர்பு மற்றும் கலை பணிகளில் வெற்றி."),
        4: ("Domestic luxury, happiness, acquisition of home conveniences and vehicle comfort.", "வீட்டு வசதிகள் பெருகும்; வாகனம் வாங்கும் யோகம் மற்றும் தாய்வழி ஆதரவு."),
        5: ("Joy in romantic bonds, child happiness, creative inspiration, aesthetic pleasure.", "காதல் மற்றும் குடும்பத்தில் மகிழ்ச்சி; பிள்ளைகளால் மனநிறைவு."),
        6: ("Avoid luxury splurges; maintain hygiene and balanced nutritional intake.", "ஆடம்பரச் செலவுகளைத் தவிர்க்கவும்; உடல் ஆரோக்கியத்தில் கவனம்."),
        7: ("Harmony with spouse and social grace; fruitful discussions in mutual alliances.", "களத்திர அன்யோன்யம் கூடும்; வாடிக்கையாளர்களிடம் நல்ல வரவேற்பு."),
        8: ("Unexpected gifts or financial receivables; pleasure through discreet means.", "எதிர்பாராத பணவரவு அல்லது பரிசுகள் கிட்டும்; ரகசிய நன்மைகள் உண்டு."),
        9: ("Fortunate journeys, spiritual elegance, blessings of prosperity and charity.", "சுப பயணங்கள்; தர்ம காரியங்கள் செய்வதில் மனம் ஈடுபடும்; அதிர்ஷ்டம் கூடும்."),
        10: ("Respect in profession; artistic or service oriented businesses flourish.", "தொழிலில் நற்பெயர்; வாடிக்கையாளர்கள் மத்தியில் மதிப்பு உயரும்."),
        11: ("Multi-fold profits, pleasant friendships, realization of social wishes.", "பன்மடங்கு லாபம்; சுப நிகழ்ச்சிகளில் பங்கேற்பு மற்றும் மனமகிழ்ச்சி."),
        12: ("Auspicious comforts, joyful bedroom serenity, tasteful festive expenses.", "சுப விரயங்கள்; மன அமைதியும் சுக நித்திரையும் கிடைக்கும்."),
    },
    "Mercury": {
        1: ("Sharp intelligence, engaging wit, academic prowess, and swift communications.", "புத்தி கூர்மை மற்றும் வாக்கு சாதுரியம் கூடும்; புதிய கற்றல் ஆர்வம் பெருகும்."),
        2: ("Financial wisdom, pleasant speech, profits from trading and accounting.", "வாக்கு வன்மை; வியாபாரம் மற்றும் கணக்கு வழக்குகளில் நல்ல லாபம்."),
        3: ("Effective presentations, successful agreements, helpful sibling support.", "தகவல் பரிமாற்றம் மற்றும் பேச்சுவார்த்தைகள் வெற்றி பெறும்; குறுகிய பயணங்கள் அனுகூலம்."),
        4: ("Academic excellence, friendly domestic vibe, vehicle/property documentation.", "கல்வியில் முன்னேற்றம்; வீடு மற்றும் சொத்து ஆவணங்கள் சுமுகமாகும்."),
        5: ("Creative brilliance, speculative intelligence, joyful rapport with youngsters.", "படைப்பாற்றல் மிளிரும்; அறிவு சார்ந்த போட்டிகளில் வெற்றி கிட்டும்."),
        6: ("Analytical edge over competitors, clearance of complex audits, productive work.", "எதிர்ப்புகளை சாதுரியமாக முறியடிப்பீர்கள்; வேலைகளில் சுறுசுறுப்பு."),
        7: ("Smooth negotiations, commercial partnerships thrive, pleasant social contacts.", "வியாபார ஒப்பந்தங்கள் கைகூடும்; கூட்டாளிகளுடன் சுமுக உறவு."),
        8: ("Deep research insights, recovery of forgotten assets, discreet technical skill.", "ஆராய்ச்சி கல்வி மற்றும் தொழில் நுட்பத்தில் முன்னேற்றம்; எதிர்பாராத செய்தி வரும்."),
        9: ("Higher studies success, guidance from wise teachers, auspicious long-distance news.", "உயர் கல்வியில் வெற்றி; பெரியோர்களின் நல்வழிகாட்டுதல் கிட்டும்."),
        10: ("Professional communication success, trade expansion, clerical commendation.", "உத்தியோகத்தில் சுறுசுறுப்பு; வியாபார விரிவாக்கம் அனுகூலமாகும்."),
        11: ("Trade profits, influential intellectual circle, multiple income avenues.", "வியாபாரத்தில் புதிய வாடிக்கையாளர்கள்; புத்திசாலித்தனத்தால் நல்ல லாபம்."),
        12: ("Avoid overthinking; double-check contracts and electronic communications.", "அதிக சிந்தனையைத் தவிர்க்கவும்; ஆவணங்களை கவனமாக பரிசீலிக்கவும்."),
    },
    "Rahu": {
        3: ("Fearless enterprise, foreign tech ventures, breakthrough over old barriers.", "தைரியம் கூடும்; புதிய தொழில் நுட்பம் மற்றும் வெளிநாட்டு தொடர்புகளால் வெற்றி."),
        6: ("Shatru Jaya: Crushing competition, clearing liabilities, unyielding endurance.", "போட்டிகளில் அபார வெற்றி; பழைய பாக்கிகள் மற்றும் கடன்கள் வசூலாகும்."),
        10: ("Rapid professional elevation, fame, handling large modern projects.", "தொழிலில் திடீர் திருப்புமுனை; செல்வாக்கும் அதிகாரமும் உயரும்."),
        11: ("Sudden multi-source windfalls, network expansion, unconventional gains.", "எதிர்பாராத தனலாபம்; புதிய வட்டாரங்கள் மூலம் காரிய வெற்றி."),
    },
    "Ketu": {
        3: ("Spiritual bravery, intuitive writing, swift overcoming of minor setbacks.", "ஆன்மீக தைரியம்; உள்ளுணர்வு வழிகாட்டும்; தடைகள் அகலும்."),
        6: ("Silent victory over hidden adversaries, medical recovery, disciplined routine.", "மறைமுக எதிர்ப்புகள் விலகும்; ஆரோக்கியத்தில் நல்ல முன்னேற்றம்."),
        11: ("Spiritual elevation, unexpected debt relief, blessings from ascetic souls.", "ஆன்மீக லாபம்; எதிர்பாராத பண உதவி மற்றும் மன நிம்மதி."),
    },
}

KP_WEEKLY_REMEDIES: Dict[str, Tuple[str, str]] = {
    "Mars": (
        "Chant Subramanya Bhujangam or visit Murugan temple on Tuesday for dynamic momentum and protection.",
        "செவ்வாய்க்கிழமையன்று முருகப்பெருமானை வழிபடவும்; கந்த சஷ்டி கவசம் படிப்பது தடைகளை நீக்கி வெற்றியைத் தரும்."
    ),
    "Venus": (
        "Offer white flowers to Goddess Lakshmi on Friday; light a ghee lamp for domestic harmony and wealth.",
        "வெள்ளிக்கிழமையன்று மகாலட்சுமிக்கு நெய் தீபமேற்றி வழிபடவும்; இனிமையான பேச்சும் தூய்மையும் செல்வத்தை ஈர்க்கும்."
    ),
    "Mercury": (
        "Offer green gram (moong dal) or pray to Lord Vishnu on Wednesday to sharpen business intelligence.",
        "புதன்கிழமையன்று விஷ்ணு சஹஸ்ரநாமம் கேட்கவும் அல்லது பெருமாள் வழிபாடு செய்ய அறிவுத்திறனும் வியாபார லாபமும் கூடும்."
    ),
    "Moon": (
        "Offer milk or pray to Lord Shiva on Monday; cultivate calm mindful decisions during evening hours.",
        "திங்கட்கிழமையன்று சிவபெருமானுக்கு பால் அபிஷேகம் அல்லது வழிபாடு செய்யவும்; தாயாரின் ஆசி பெறுவது நலம்."
    ),
    "Sun": (
        "Perform Surya Namaskar and chant Aditya Hridaya Stotram on Sunday for vitality, confidence, and authority.",
        "ஞாயிற்றுக்கிழமையன்று ஆதித்ய ஹிருதய ஸ்தோத்திரம் கேட்கவும் அல்லது படிக்கவும்; தந்தை வழி நல்லுறவு நலம் தரும்."
    ),
    "Jupiter": (
        "Pray to Lord Dakshinamurthy on Thursday with yellow flowers or offer chana dal for divine wisdom and luck.",
        "வியாழக்கிழமையன்று தட்சிணாமூர்த்திக்கு கொண்டைக்கடலை மாலை சாற்றி வழிபடவும்; பெரியோர்களின் ஆசி பெறவும்."
    ),
    "Saturn": (
        "Light sesame oil lamp for Lord Shiva/Hanuman on Saturday; assist those who labor diligently.",
        "சனிக்கிழமையன்று ஆஞ்சநேயர் அல்லது சிவபெருமானை வழிபடவும்; ஏழை எளியவர்களுக்கு அன்னதானம் செய்வது சனி தோஷத்தை நீக்கும்."
    ),
}

KP_MONTHLY_REMEDIES: Dict[str, Tuple[str, str]] = {
    "Mars": (
        "Perform monthly Sashti fasting or Archana for Lord Murugan to foster property prosperity and peace.",
        "மாதாந்திர சஷ்டி விரதம் அல்லது முருகப்பெருமான் வழிபாடு செய்வது நிலம், தொழில் சார்ந்த தடைகளை நீக்கும்."
    ),
    "Venus": (
        "Perform Friday Lakshmi Puja on Sukla Paksha and donate white rice or sweets for sustained prosperity.",
        "சுக்கில பட்ச வெள்ளிக்கிழமைகளில் லட்சுமி குபேர பூஜை செய்வது மாதாந்திர தன வரவை பெருக்கும்."
    ),
    "Mercury": (
        "Engage in Vishnu Sahasranama recital on Ekadashi and support student education for mental brilliance.",
        "ஏகாதசி தோறும் விஷ்ணு வழிபாடு செய்யவும்; கல்வி பயிலும் மாணவர்களுக்கு நோட்டுப் புத்தகம் வழங்கவும்."
    ),
    "Moon": (
        "Observe Somavara Vrat or Pournami Chandradarsanam; practice meditation for emotional stability.",
        "பௌர்ணமி தோறும் அம்பாள் வழிபாடு அல்லது கிரிவலம் செல்வது மாதாந்திர மன அமைதியையும் ஆரோக்கியத்தையும் தரும்."
    ),
    "Sun": (
        "Perform monthly Sankranti Arghya and maintain respect for mentors and father for leadership victory.",
        "மாதப் பிறப்பன்று சூரிய வழிபாடு செய்து முன்னோர்களை வழிபடவும்; தலைமைப் பண்பும் அரசு மரியாதையும் கூடும்."
    ),
    "Jupiter": (
        "Offer Guru Kanikkai or support temple annadhanam on Guruvara for expansive blessings throughout the month.",
        "மாதந்தோறும் குருவாரம் அன்று அன்னதானம் செய்யவும்; ஆன்மீக பெரியோர்களின் ஆசி பெறுவது பாக்கியத்தை வளர்க்கும்."
    ),
    "Saturn": (
        "Observe Pradosham and Shani Trayodashi worship; feed crows and laborers to dissolve hurdles.",
        "மாதந்தோறும் வரும் பிரதோஷ வழிபாடு மற்றும் சனிக்கிழமை நல்லெண்ணெய் தீபம் ஏற்றுவது நீண்டகால வெற்றியைத் தரும்."
    ),
}


def _get_planet_positions_at_date(
    calc_date: date,
    tz_obj: ZoneInfo,
    ayanamsa_id: int,
) -> Dict[str, Dict[str, Any]]:
    """Calculates all 9 planet longitudes and info for a specific date at midday."""
    noon_time = time(12, 0, 0)
    _, _, noon_jd, _, _ = resolve_birth_datetime(calc_date, noon_time, str(tz_obj))

    planets_data: Dict[str, Dict[str, Any]] = {}
    for p_name, p_id in PLANET_IDS.items():
        pos = xalen.planet_position(noon_jd, p_id, True, ayanamsa_id)
        lon = pos["longitude"]
        p_info = point_info(lon)
        planets_data[p_name] = {
            "longitude": lon,
            "sign": p_info.sign,
            "sign_degree": p_info.sign_degree,
            "star_name": p_info.star,
            "star_lord": p_info.star_lord,
            "sub_lord": p_info.sub_lord,
            "is_retrograde": pos.get("is_retrograde", False),
            "speed": pos.get("lon_speed", 0.0),
        }
    return planets_data


def _detect_transit_ingresses_in_period(
    start_date: date,
    end_date: date,
    tz_obj: ZoneInfo,
    ayanamsa_id: int,
) -> List[Dict[str, Any]]:
    """Detects any planetary sign changes occurring between start_date and end_date."""
    ingresses: List[Dict[str, Any]] = []
    days_count = (end_date - start_date).days + 1

    # Check step by step (daily for slow and fast planets except Moon)
    tracked_planets = ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    # Sample day by day
    prev_positions: Optional[Dict[str, str]] = None
    curr_d = start_date
    while curr_d <= end_date:
        p_data = _get_planet_positions_at_date(curr_d, tz_obj, ayanamsa_id)
        current_signs = {p: p_data[p]["sign"] for p in tracked_planets}

        if prev_positions is not None:
            for p in tracked_planets:
                if prev_positions[p] != current_signs[p]:
                    from_s = prev_positions[p]
                    to_s = current_signs[p]
                    p_ta = PLANET_NAMES_TA.get(p, p)
                    from_ta = SIGN_NAMES_TA.get(from_s, from_s)
                    to_ta = SIGN_NAMES_TA.get(to_s, to_s)
                    d_str = curr_d.strftime("%b %d")
                    d_str_ta = f"{curr_d.day} {MONTHS_TA.get(curr_d.month, '')}"
                    ingresses.append({
                        "planet": p,
                        "planet_ta": p_ta,
                        "from_sign": from_s,
                        "from_sign_ta": from_ta,
                        "to_sign": to_s,
                        "to_sign_ta": to_ta,
                        "date": curr_d.isoformat(),
                        "event_en": f"{p} enters {to_s} on {d_str}",
                        "event_ta": f"{p_ta} பெயர்ச்சி: {from_ta} ராசியிலிருந்து {to_ta} ராசிக்கு மாறுகிறார் ({d_str_ta})",
                    })

        prev_positions = current_signs
        curr_d += timedelta(days=1)

    return ingresses


def _track_moon_and_chandrashtama(
    start_date: date,
    end_date: date,
    rashi_idx: int,
    tz_obj: ZoneInfo,
    ayanamsa_id: int,
    is_weekly: bool,
) -> Tuple[str, str, str, str]:
    """Evaluates Moon's transit across the period to pinpoint Chandrashtama and Auspicious days."""
    curr_d = start_date
    chandrashtama_days: List[Tuple[date, str, str]] = []
    auspicious_days: List[Tuple[date, str, str]] = []

    while curr_d <= end_date:
        noon_time = time(12, 0, 0)
        _, _, jd, _, _ = resolve_birth_datetime(curr_d, noon_time, str(tz_obj))
        pos = xalen.planet_position(jd, PLANET_IDS["Moon"], True, ayanamsa_id)
        m_sign_idx = int(pos["longitude"] // 30.0) + 1
        m_house = ((m_sign_idx - rashi_idx) % 12) + 1

        w_idx = curr_d.weekday()
        day_en, day_ta, _ = WEEKDAY_INFO[w_idx]

        if m_house == 8:
            chandrashtama_days.append((curr_d, day_en, day_ta))
        elif m_house in (2, 5, 9, 10, 11):
            auspicious_days.append((curr_d, day_en, day_ta))

        curr_d += timedelta(days=1)

    # Format outputs
    if is_weekly:
        if chandrashtama_days:
            # e.g. "Wednesday & Thursday"
            c_en = " & ".join(sorted(list({d[1] for d in chandrashtama_days})))
            c_ta = " & ".join(sorted(list({d[2] for d in chandrashtama_days})))
        else:
            c_en = "No Chandrashtama this week"
            c_ta = "இந்த வாரம் சந்திராஷ்டமம் இல்லை"

        if auspicious_days:
            l_en = " & ".join(sorted(list({d[1] for d in auspicious_days[:3]})))
            l_ta = " & ".join(sorted(list({d[2] for d in auspicious_days[:3]})))
        else:
            l_en = "Tuesday & Friday"
            l_ta = "செவ்வாய் & வெள்ளி"
    else:
        # Monthly formatting: date ranges
        if chandrashtama_days:
            # Group into spans
            dates_list = [d[0] for d in chandrashtama_days]
            spans: List[str] = []
            spans_ta: List[str] = []
            
            # Simple span clustering
            start_grp = dates_list[0]
            prev_grp = dates_list[0]
            for dt in dates_list[1:]:
                if (dt - prev_grp).days == 1:
                    prev_grp = dt
                else:
                    if start_grp == prev_grp:
                        spans.append(f"{start_grp.strftime('%b %d')}")
                        spans_ta.append(f"{start_grp.day} {MONTHS_TA.get(start_grp.month, '')}")
                    else:
                        spans.append(f"{start_grp.strftime('%b %d')} - {prev_grp.strftime('%b %d')}")
                        spans_ta.append(f"{start_grp.day} – {prev_grp.day} {MONTHS_TA.get(prev_grp.month, '')}")
                    start_grp = dt
                    prev_grp = dt
            if start_grp == prev_grp:
                spans.append(f"{start_grp.strftime('%b %d')}")
                spans_ta.append(f"{start_grp.day} {MONTHS_TA.get(start_grp.month, '')}")
            else:
                spans.append(f"{start_grp.strftime('%b %d')} - {prev_grp.strftime('%b %d')}")
                spans_ta.append(f"{start_grp.day} – {prev_grp.day} {MONTHS_TA.get(prev_grp.month, '')}")

            c_en = ", ".join(spans)
            c_ta = ", ".join(spans_ta)
        else:
            c_en = "No prolonged Chandrashtama"
            c_ta = "குறிப்பிடத்தக்க சந்திராஷ்டமம் இல்லை"

        if auspicious_days:
            # Pick 4 notable dates across month
            step = max(1, len(auspicious_days) // 4)
            chosen = [auspicious_days[i][0] for i in range(0, len(auspicious_days), step)][:4]
            l_en = ", ".join([f"{d.strftime('%b %d')}" for d in chosen])
            l_ta = ", ".join([f"{d.day} {MONTHS_TA.get(d.month, '')}" for d in chosen])
        else:
            l_en = "1st, 10th, 19th, 28th"
            l_ta = "1, 10, 19, 28-ம் தேதிகள்"

    return c_en, c_ta, l_en, l_ta


def _build_rashi_transit_summary(
    rashi_idx: int,
    planet_positions: Dict[str, Dict[str, Any]],
    ingresses: List[Dict[str, Any]],
    chandrashtama_en: str,
    chandrashtama_ta: str,
    is_weekly: bool,
) -> Tuple[TransitSummaryPerRashi, int, List[TransitMovement]]:
    """Builds comprehensive transit summary for a single Rashi."""
    r_en, r_ta, sign_lord = RASHI_METADATA[rashi_idx]
    movements: List[TransitMovement] = []
    benefics: List[str] = []
    challenging: List[str] = []
    special_yogas_en: List[str] = []
    special_yogas_ta: List[str] = []

    # Map of ingresses by planet
    ingress_map: Dict[str, str] = {ing["planet"]: ing["event_en"] for ing in ingresses}
    ingress_map_ta: Dict[str, str] = {ing["planet"]: ing["event_ta"] for ing in ingresses}

    transit_score_modifier = 0

    # Planets to display in order of traditional importance
    order = ["Jupiter", "Saturn", "Sun", "Mars", "Venus", "Mercury", "Rahu", "Ketu", "Moon"]

    for p in order:
        p_data = planet_positions.get(p)
        if not p_data:
            continue
        p_lon = p_data["longitude"]
        p_sign = p_data["sign"]
        p_sign_idx = int(p_lon // 30.0) + 1
        h_rel = _calc_house_relative(p_sign_idx, rashi_idx)
        p_ta = PLANET_NAMES_TA.get(p, p)
        s_ta = SIGN_NAMES_TA.get(p_sign, p_sign)

        is_fav = h_rel in BENEFIC_TRANSIT_HOUSES.get(p, set())
        if is_fav:
            status = "favorable"
            benefics.append(p)
            transit_score_modifier += 4
        elif h_rel in (6, 8, 12) and p in ("Saturn", "Mars", "Sun", "Rahu"):
            status = "caution"
            challenging.append(p)
            transit_score_modifier -= 3
        else:
            status = "neutral"

        # Impact statement
        impact_pair = PLANET_HOUSE_TRANSIT_IMPACT.get(p, {}).get(h_rel, None)
        if impact_pair:
            imp_en, imp_ta = impact_pair
        else:
            if is_fav:
                imp_en = f"{p} transits house {h_rel} ({p_sign}) bringing supportive momentum."
                imp_ta = f"{p_ta} {h_rel}-ம் வீட்டில் ({s_ta}) சஞ்சரித்து நல்ல அனுகூலங்களை வழங்குகிறார்."
            else:
                imp_en = f"{p} transits house {h_rel} ({p_sign}); maintain steady patience."
                imp_ta = f"{p_ta} {h_rel}-ம் வீட்டில் ({s_ta}) சஞ்சரிப்பதால் நிதானமாக செயல்படுவது நலம்."

        ing_event = ingress_map.get(p, None)

        # Check Special Yogas for this Rashi
        if p == "Jupiter":
            if h_rel in (2, 5, 7, 9, 11):
                special_yogas_en.append(f"Guru Balan Active: Jupiter in house {h_rel} casts auspicious aspects on your sign.")
                special_yogas_ta.append(f"குரு பலம்: குரு பகவான் {h_rel}-ம் இடத்தில் சஞ்சரித்து சுபப் பார்வைகளால் அருள் பாலிக்கிறார்.")
                transit_score_modifier += 6
        elif p == "Saturn":
            if h_rel in (12, 1, 2):
                special_yogas_en.append("Sade Sati Active: Saturn transit demands patience, steady ethics, and health care.")
                special_yogas_ta.append("ஏழரை சனி தாக்கம்: விவேகமான உழைப்பும் ஆஞ்சநேயர் வழிபாடும் அமைதியைத் தரும்.")
                transit_score_modifier -= 4
            elif h_rel == 8:
                special_yogas_en.append("Ashtama Shani: Exercise road caution, avoid heavy debt, and maintain emotional calm.")
                special_yogas_ta.append("அஷ்டம சனி: பயணங்களிலும் நிதிப் பரிவர்த்தனையிலும் கூடுதல் எச்சரிக்கை தேவை.")
                transit_score_modifier -= 5
            elif h_rel == 4:
                special_yogas_en.append("Ardhastama Shani: Focus on domestic peace and property patience.")
                special_yogas_ta.append("அர்த்தாஷ்டம சனி: குடும்ப விவகாரங்களில் பொறுமையும் தாயார் நலனில் அக்கறையும் தேவை.")
            elif h_rel in (3, 6, 11):
                special_yogas_en.append(f"Subha Shani: Saturn in Upachaya house {h_rel} provides formidable victory over hurdles.")
                special_yogas_ta.append(f"சுப சனி: {h_rel}-ம் இடத்து சனி பகவான் எதிர்ப்புகளையும் கடன் தொல்லைகளையும் தகர்த்து வெற்றி தருவார்.")
                transit_score_modifier += 5

        movements.append(TransitMovement(
            planet=p,
            planet_ta=p_ta,
            current_sign=p_sign,
            current_sign_ta=s_ta,
            star_name=p_data["star_name"],
            star_lord=p_data["star_lord"],
            sub_lord=p_data["sub_lord"],
            house_relative=h_rel,
            is_favorable=is_fav,
            status=status,
            is_retrograde=p_data["is_retrograde"],
            transit_ingress_event=ing_event,
            impact_summary_en=imp_en,
            impact_summary_ta=imp_ta,
        ))

    # Transit Overview Synthesis Narrative
    period_term_en = "week" if is_weekly else "month"
    period_term_ta = "வாரம்" if is_weekly else "மாதம்"

    benefic_names_en = ", ".join(benefics[:3]) if benefics else "benefic stars"
    benefic_names_ta = ", ".join([PLANET_NAMES_TA.get(b, b) for b in benefics[:3]]) if benefics else "சுப கிரகங்கள்"

    chal_names_en = ", ".join(challenging[:2]) if challenging else "minor aspects"
    chal_names_ta = ", ".join([PLANET_NAMES_TA.get(c, c) for c in challenging[:2]]) if challenging else "சில கிரக நிலைகள்"

    overview_en = (
        f"For {r_en}, planetary transits this {period_term_en} are predominantly anchored by {benefic_names_en} in supportive houses, "
        f"fueling progress in routine affairs and career objectives. Vigilance is advised regarding {chal_names_en} to keep expenditures and speech balanced. "
        f"During Chandrashtama ({chandrashtama_en}), refrain from initiating high-stakes deals."
    )
    overview_ta = (
        f"{r_ta} ராசிக்கு இந்த {period_term_ta} {benefic_names_ta} சாதகமான ஸ்தானங்களில் சஞ்சரிப்பதால் தொழில், உத்தியோகத்தில் நல்ல முன்னேற்றமும் "
        f"காரிய அனுகூலமும் உண்டாகும். அதே சமயம் {chal_names_ta} ஆதிக்கத்தால் வீண் வாக்குவாதங்கள் மற்றும் விரயங்களை தவிர்ப்பது நலம். "
        f"சந்திராஷ்டம தினங்களில் ({chandrashtama_ta}) புதிய ஒப்பந்தங்கள் மற்றும் பயணங்களில் கூடுதல் நிதானம் தேவை."
    )

    summary = TransitSummaryPerRashi(
        rashi_id=rashi_idx,
        rashi_name_en=r_en,
        rashi_name_ta=r_ta,
        planet_transits=movements,
        transit_overview_en=overview_en,
        transit_overview_ta=overview_ta,
        benefic_planets=benefics,
        challenging_planets=challenging,
        chandrashtama_period_en=chandrashtama_en,
        chandrashtama_period_ta=chandrashtama_ta,
        special_yogas_en=special_yogas_en,
        special_yogas_ta=special_yogas_ta,
    )

    return summary, transit_score_modifier, movements


def _build_period_aspects(
    r_en: str,
    r_ta: str,
    rashi_idx: int,
    planet_positions: Dict[str, Dict[str, Any]],
    transit_modifier: int,
    is_weekly: bool,
) -> Tuple[List[KpAspectPrediction], int]:
    """Generates 5 life aspects predictions for weekly or monthly horizon."""
    # Find key houses
    jup_pos = planet_positions.get("Jupiter", {})
    jup_sign = int(jup_pos.get("longitude", 0.0) // 30.0) + 1
    jup_house = _calc_house_relative(jup_sign, rashi_idx)

    sun_pos = planet_positions.get("Sun", {})
    sun_sign = int(sun_pos.get("longitude", 0.0) // 30.0) + 1
    sun_house = _calc_house_relative(sun_sign, rashi_idx)

    ven_pos = planet_positions.get("Venus", {})
    ven_sign = int(ven_pos.get("longitude", 0.0) // 30.0) + 1
    ven_house = _calc_house_relative(ven_sign, rashi_idx)

    sat_pos = planet_positions.get("Saturn", {})
    sat_sign = int(sat_pos.get("longitude", 0.0) // 30.0) + 1
    sat_house = _calc_house_relative(sat_sign, rashi_idx)

    p_term = "week" if is_weekly else "month"
    p_term_ta = "வாரம்" if is_weekly else "மாதம்"

    # 1. Career
    c_base = 65 + (transit_modifier // 2)
    if sun_house in (10, 11, 3, 6):
        c_base += 12
    if sat_house in (3, 6, 11):
        c_base += 10
    if jup_house in (2, 5, 9, 10, 11):
        c_base += 8
    c_score = min(96, max(38, c_base))
    c_stars = round(1.0 + (c_score / 100.0) * 4.0, 1)
    c_status = "Excellent" if c_score >= 80 else ("Favorable" if c_score >= 62 else ("Mixed" if c_score >= 48 else "Challenging"))

    if c_score >= 75:
        c_en = f"Exceptional professional momentum throughout this {p_term}. New opportunities, corporate commendation, and leadership breakthroughs unfold."
        c_ta = f"இந்த {p_term_ta} தொழில் மற்றும் உத்தியோகத்தில் மிகச் சிறந்த வளர்ச்சி உண்டு. மேலதிகாரிகளின் பாராட்டு, புதிய பொறுப்புகள் மற்றும் தொழில் முன்னேற்றம் கைகூடும்."
        c_rec_en = "Pursue ambitious presentations, business expansions, and client closures boldly."
        c_rec_ta = "புதிய திட்டங்கள் மற்றும் தொழில் விரிவாக்க முயற்சிகளில் தைரியமாக இறங்கி வெற்றி பெறலாம்."
    elif c_score >= 55:
        c_en = f"Steady progress in office assignments. Routine deliverables flow smoothly through systematic execution."
        c_ta = f"உத்தியோகத்தில் வழக்கமான பணிகள் சீராக நடக்கும். சக ஊழியர்களின் ஒத்துழைப்புடன் பணிகளை எளிதில் முடிப்பீர்கள்."
        c_rec_en = "Maintain consistency and avoid unnecessary friction with colleagues."
        c_rec_ta = "பணியிடத்தில் தேவையில்லாத விவாதங்களைத் தவிர்த்து கடமையில் கவனம் செலுத்தவும்."
    else:
        c_en = f"Patience is needed in professional dealings. Workload pressures may arise; verify agreements carefully."
        c_ta = f"தொழிலில் கூடுதல் விழிப்புணர்வும் பொறுமையும் தேவை. புதிய முயற்சிகளில் அவசரம் காட்டாமல் நிதானமாக செயல்படவும்."
        c_rec_en = "Keep official communications documented and defer high-risk career switches."
        c_rec_ta = "அலுவலக ஆவணங்களை கவனமாக கையாளவும்; அவசர முடிவுகளைத் தவிர்க்கவும்."

    career = KpAspectPrediction(
        aspect_code="career",
        aspect_name="Career & Profession",
        aspect_name_tamil="தொழில் & உத்தியோகம்",
        score=c_score,
        rating_stars=c_stars,
        status=c_status,
        signified_houses=[10, 11, 6],
        insight_en=c_en,
        insight_ta=c_ta,
        key_recommendation_en=c_rec_en,
        key_recommendation_ta=c_rec_ta,
    )

    # 2. Finance
    f_base = 62 + (transit_modifier // 2)
    if jup_house in (2, 5, 9, 11):
        f_base += 15
    if ven_house in (2, 11, 4):
        f_base += 10
    f_score = min(95, max(35, f_base))
    f_stars = round(1.0 + (f_score / 100.0) * 4.0, 1)
    f_status = "Excellent" if f_score >= 80 else ("Favorable" if f_score >= 62 else ("Mixed" if f_score >= 48 else "Challenging"))

    if f_score >= 75:
        f_en = f"Strong financial inflows and clearance of overdue payments. Lucrative avenues open up for savings and investments."
        f_ta = f"பணப்புழக்கம் திருப்திகரமாக இருக்கும்; வரவேண்டிய பழைய பாக்கிகள் வசூலாகும். புதிய வருமான வழிகள் பிறக்கும்."
        f_rec_en = "Allocate surplus capital into long-term sovereign assets and disciplined savings."
        f_rec_ta = "வரும் உபரி வருமானத்தை வீண் விரயம் செய்யாமல் பயனுள்ள சேமிப்பில் முதலீடு செய்யவும்."
    elif f_score >= 55:
        f_en = f"Balanced cash flow. Inflows match regular domestic requirements without acute bottlenecks."
        f_ta = f"வரவும் செலவும் சமநிலையில் இருக்கும். குடும்பத்தின் அத்தியாவசிய தேவைகள் தடையின்றி பூர்த்தியாகும்."
        f_rec_en = "Stick to budgeted checklists and defer impulse purchases."
        f_rec_ta = "திட்டமிட்ட வரவு செலவு கணக்கைப் பின்பற்றவும்; ஆடம்பர செலவுகளைக் குறைக்கவும்."
    else:
        f_en = f"Careful monitoring of expenditures is essential this {p_term}. Avoid speculative borrowings."
        f_ta = f"பண விவகாரங்களில் மிகுந்த எச்சரிக்கை தேவை. தேவையற்ற விரயங்களும் எதிர்பாராத செலவுகளும் வரக்கூடும்."
        f_rec_en = "Avoid lending money or guaranteeing third-party loans."
        f_rec_ta = "யாருக்கும் கடன் கொடுக்கல் வாங்கல் அல்லது ஜாமீன் போடுவதைத் தவிர்க்கவும்."

    finance = KpAspectPrediction(
        aspect_code="finance",
        aspect_name="Wealth & Finance",
        aspect_name_tamil="தனம் & பணவரவு",
        score=f_score,
        rating_stars=f_stars,
        status=f_status,
        signified_houses=[2, 11, 9],
        insight_en=f_en,
        insight_ta=f_ta,
        key_recommendation_en=f_rec_en,
        key_recommendation_ta=f_rec_ta,
    )

    # 3. Love & Family
    l_base = 66 + (transit_modifier // 3)
    if ven_house in (1, 2, 4, 5, 7, 11):
        l_base += 12
    if jup_house in (5, 7, 9):
        l_base += 10
    l_score = min(96, max(40, l_base))
    l_stars = round(1.0 + (l_score / 100.0) * 4.0, 1)
    l_status = "Excellent" if l_score >= 80 else ("Favorable" if l_score >= 62 else ("Mixed" if l_score >= 48 else "Challenging"))

    if l_score >= 75:
        l_en = f"Heartwarming domestic bliss and mutual warmth with your life partner. Auspicious family events bring joyful unity."
        l_ta = f"குடும்பத்தில் அமைதியும் மகிழ்ச்சியும் நிலவும்; தம்பதியரிடையே அன்யோன்யம் கூடும். சுப காரிய பேச்சுவார்த்தைகள் சுமுகமாகும்."
        l_rec_en = "Spend quality time with family and celebrate shared milestones together."
        c_rec_ta = "குடும்பத்தினருடன் நேரம் செலவிட்டு மகிழ்ச்சியைப் பகிர்ந்து கொள்ளவும்."
    elif l_score >= 55:
        l_en = f"Pleasant interpersonal relationships. Small differences are easily reconciled with open dialogue."
        l_ta = f"உறவினர்களிடையே சுமுகமான சூழல் நிலவும்; சிறு மனஸ்தாபங்கள் பேசித் தீர்க்கப்படும்."
        l_rec_en = "Listen with empathy and meet loved ones halfway."
        c_rec_ta = "பரஸ்பர விட்டுக்கொடுத்துச் செல்லும் மனப்பான்மை குடும்ப அமைதியைக் காக்கும்."
    else:
        l_en = f"Patience is advised in domestic matters. Avoid escalating minor misunderstandings."
        l_ta = f"குடும்பத்தில் தேவையற்ற வாக்குவாதங்களைத் தவிர்க்கவும்; விட்டுக்கொடுத்துச் செல்வது நலம்."
        l_rec_en = "Guard against stubbornness and maintain harmonious silence during arguments."
        c_rec_ta = "முன்கோபத்தைத் தவிர்த்து பெரியோர்களின் ஆலோசனையைக் கேட்டு நடக்கவும்."

    love = KpAspectPrediction(
        aspect_code="love",
        aspect_name="Love & Family",
        aspect_name_tamil="குடும்பம் & உறவுகள்",
        score=l_score,
        rating_stars=l_stars,
        status=l_status,
        signified_houses=[7, 2, 5],
        insight_en=l_en,
        insight_ta=l_ta,
        key_recommendation_en=l_rec_en,
        key_recommendation_ta=c_rec_ta,
    )

    # 4. Health & Vitality
    h_base = 65 + (transit_modifier // 3)
    if sun_house in (1, 3, 6, 10, 11):
        h_base += 10
    if sat_house in (8, 12):
        h_base -= 12
    h_score = min(94, max(38, h_base))
    h_stars = round(1.0 + (h_score / 100.0) * 4.0, 1)
    h_status = "Excellent" if h_score >= 80 else ("Favorable" if h_score >= 62 else ("Mixed" if h_score >= 48 else "Challenging"))

    if h_score >= 75:
        h_en = f"High physical stamina, mental clarity, and refreshed vitality throughout this {p_term}."
        h_ta = f"உடல் நலம் சீராக இருக்கும்; மனதில் உற்சாகமும் சுறுசுறுப்பும் பெருகும். நோயற்ற வாழ்வு உண்டு."
        h_rec_en = "Maintain regular yoga, balanced hydration, and outdoor physical exercise."
        h_rec_ta = "வழக்கமான உடற்பயிற்சி, சத்தான உணவு மற்றும் நடைப்பயிற்சி நல்ல ஆரோக்கியம் தரும்."
    elif h_score >= 55:
        h_en = f"Normal health flow. Minor seasonal fatigue can be averted with timely meals and good rest."
        h_ta = f"ஆரோக்கியம் சீராக இருக்கும்; நேரத்திற்கு சத்தான உணவு உண்பது நலம்."
        h_rec_en = "Ensure 7 hours of restorative sleep and avoid skipping breakfast."
        h_rec_ta = "நேரத்திற்கு உறங்கி நேரத்திற்கு சத்தான உணவு உட்கொள்ளவும்."
    else:
        h_en = f"Guard against exhaustion and digestive sensitivity. Avoid unhygienic foods."
        h_ta = f"அஜீரணக் கோளாறு மற்றும் தூக்கமின்மை ஏற்படலாம்; ஆரோக்கியத்தில் கவனம் தேவை."
        h_rec_en = "Consult your physician for chronic issues and take timely relaxation breaks."
        h_rec_ta = "உணவுக் கட்டுப்பாடும் தியானமும் மன அமைதியையும் உடல் நலனையும் காக்கும்."

    health = KpAspectPrediction(
        aspect_code="health",
        aspect_name="Health & Vitality",
        aspect_name_tamil="உடல்நலம் & உற்சாகம்",
        score=h_score,
        rating_stars=h_stars,
        status=h_status,
        signified_houses=[1, 11, 6],
        insight_en=h_en,
        insight_ta=h_ta,
        key_recommendation_en=h_rec_en,
        key_recommendation_ta=h_rec_ta,
    )

    # 5. Travel & Studies
    t_base = 64 + (transit_modifier // 3)
    if jup_house in (5, 9, 3, 11):
        t_base += 12
    t_score = min(95, max(40, t_base))
    t_stars = round(1.0 + (t_score / 100.0) * 4.0, 1)
    t_status = "Excellent" if t_score >= 80 else ("Favorable" if t_score >= 62 else ("Mixed" if t_score >= 48 else "Challenging"))

    if t_score >= 75:
        t_en = f"Highly rewarding long-distance travel, pilgrimage, and academic breakthroughs. Exams and certifications succeed."
        t_ta = f"பயணங்களால் எதிர்பாராத நன்மைகள் உண்டாகும்; உயர்கல்வி மற்றும் தேர்வுகளில் மாணவர்கள் சிறப்பான வெற்றி பெறுவர்."
        t_rec_en = "Embrace cross-cultural learning, competitive tests, and visionary plans."
        t_rec_ta = "கல்வி மற்றும் வெளிநாட்டு பயண முயற்சிகளில் தைரியமாக முன்னேறலாம்."
    elif t_score >= 55:
        t_en = f"Ordinary travel and educational pursuits progress systematically. Double-check tickets and timings."
        t_ta = f"வழக்கமான பயணங்களும் கல்விப் பணிகளும் சுமுகமாகும்; பயண நேரத்தை முன்கூட்டியே திட்டமிடவும்."
        t_rec_en = "Keep travel kits prepared and review study materials methodically."
        t_rec_ta = "பயணங்களின் போது ஆவணங்களை சரியாக வைத்துக்கொள்ளவும்."
    else:
        t_en = f"Commuting fatigue or minor schedule delays possible. Defer non-essential journeys."
        t_ta = f"பயணங்களில் அலைச்சலும் காலதாமதமும் ஏற்படலாம்; அவசியமான பயணங்களை மட்டும் மேற்கொள்ளவும்."
        t_rec_en = "Drive cautiously and avoid night highway travel."
        t_rec_ta = "இரவு நேரப் பயணங்களைத் தவிர்க்கவும்; கவனமாக வாகனம் ஓட்டவும்."

    travel = KpAspectPrediction(
        aspect_code="travel",
        aspect_name="Travel & Studies",
        aspect_name_tamil="பயணம் & கல்வி",
        score=t_score,
        rating_stars=t_stars,
        status=t_status,
        signified_houses=[3, 9, 11],
        insight_en=t_en,
        insight_ta=t_ta,
        key_recommendation_en=t_rec_en,
        key_recommendation_ta=t_rec_ta,
    )

    aspects = [career, finance, love, health, travel]
    overall_score = int(round((c_score * 0.3) + (f_score * 0.25) + (l_score * 0.2) + (h_score * 0.15) + (t_score * 0.1)))
    return aspects, overall_score


def compute_kp_weekly_horoscope(
    target_date: Optional[date | str] = None,
    timezone_str: str = "Asia/Kolkata",
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    rashi_filter: Optional[str] = "all",
    ayanamsa_id: int = 1,
) -> KpWeeklyHoroscopeResponse:
    """Computes high-precision KP weekly predictions for all or requested Rashis."""
    tz_clean = timezone_str.strip() if timezone_str else "Asia/Kolkata"
    try:
        tz_obj = ZoneInfo(tz_clean)
    except Exception:
        tz_obj = ZoneInfo("Asia/Kolkata")

    now_local = datetime.now(tz_obj)
    if target_date is None:
        calc_date = now_local.date()
    elif isinstance(target_date, str):
        calc_date = datetime.strptime(target_date.strip(), "%Y-%m-%d").date()
    else:
        calc_date = target_date

    # Determine Week: Monday to Sunday
    start_date = calc_date - timedelta(days=calc_date.weekday())
    end_date = start_date + timedelta(days=6)

    # Week Labels
    week_label_en = f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
    week_label_ta = f"{start_date.day} {MONTHS_TA.get(start_date.month, '')} {start_date.year} – {end_date.day} {MONTHS_TA.get(end_date.month, '')} {end_date.year}"

    # Ephemeris planetary positions at midpoint (Thursday noon)
    mid_date = start_date + timedelta(days=3)
    planet_positions = _get_planet_positions_at_date(mid_date, tz_obj, ayanamsa_id)

    # Detect all ingresses during this week
    ingresses = _detect_transit_ingresses_in_period(start_date, end_date, tz_obj, ayanamsa_id)

    aya_name = AYANAMSA_NAMES.get(ayanamsa_id, ("KP", ""))[0]

    # Resolve Rashis to evaluate
    rashis_to_calc: List[int] = []
    if not rashi_filter or str(rashi_filter).strip().lower() in ("all", "0", ""):
        rashis_to_calc = list(range(1, 13))
    elif str(rashi_filter).strip().isdigit():
        r_num = int(str(rashi_filter).strip())
        rashis_to_calc = [r_num] if 1 <= r_num <= 12 else list(range(1, 13))
    else:
        clean_name = str(rashi_filter).strip().capitalize()
        matched = SIGN_TO_INDEX.get(clean_name, None)
        rashis_to_calc = [matched] if matched else list(range(1, 13))

    predictions: List[RashiWeeklyPrediction] = []
    global_movements_recorded: List[TransitMovement] = []

    for r_idx in rashis_to_calc:
        r_en, r_ta, sign_lord = RASHI_METADATA[r_idx]

        # Chandrashtama & Auspicious days
        c_en, c_ta, l_en, l_ta = _track_moon_and_chandrashtama(start_date, end_date, r_idx, tz_obj, ayanamsa_id, is_weekly=True)

        # Transit summary
        transit_summary, transit_mod, movements = _build_rashi_transit_summary(
            r_idx, planet_positions, ingresses, c_en, c_ta, is_weekly=True
        )

        if not global_movements_recorded:
            global_movements_recorded = movements

        # Aspects & overall score
        aspect_list, weekly_score = _build_period_aspects(
            r_en, r_ta, r_idx, planet_positions, transit_mod, is_weekly=True
        )

        weekly_rating_stars = round(1.0 + (weekly_score / 100.0) * 4.0, 1)
        if weekly_score >= 76:
            week_sentiment = "Excellent"
        elif weekly_score >= 60:
            week_sentiment = "Favorable"
        elif weekly_score >= 45:
            week_sentiment = "Mixed"
        else:
            week_sentiment = "Challenging"

        # Executive brief statement
        if weekly_score >= 75:
            brief_en = f"Auspicious week powered by strong transit support. Key initiatives, contracts, and financial efforts bear fruitful rewards."
            brief_ta = f"கோச்சார கிரகங்களின் பூரண ஆதரவுடன் இந்த வாரம் தொட்ட காரியங்கள் துலங்கும்; தொழில், உத்தியோகம் மற்றும் நிதி விவகாரங்களில் சிறப்பான அனுகூலம் உண்டு."
            peak_en = "Breakthroughs in negotiations, career advancement, and unexpected financial receivables."
            peak_ta = "புதிய ஒப்பந்தங்கள் கையெழுத்தாகும்; பழைய பாக்கிகள் வசூலாகி நிதிநிலை உயரும்."
            caution_en = f"During Chandrashtama ({c_en}), defer risky speculative moves and drive patiently."
            caution_ta = f"சந்திராஷ்டம நாட்களில் ({c_ta}) புதிய முதலீடுகளைத் தவிர்த்து நிதானம் காக்கவும்."
        elif weekly_score >= 58:
            brief_en = f"Balanced and productive week. Systematic hard work yields steady gains across domestic and career fronts."
            brief_ta = f"வழக்கமான பணிகளில் முன்னேற்றம் தரும் நல்வாரம்; திட்டமிட்டு செயல்படுவதன் மூலம் எதிர்பார்த்த நற்பலன்களை அடையலாம்."
            peak_en = "Smooth resolution of pending office tasks and harmonious domestic interactions."
            peak_ta = "நிலுவைப் பணிகள் எளிதில் முடியும்; குடும்பத்தில் மகிழ்ச்சியான சூழல் நிலவும்."
            caution_en = f"Strictly avoid unnecessary verbal debates during {c_en}."
            caution_ta = f"{c_ta} தினங்களில் தேவையற்ற வாக்குவாதங்களைத் தவிர்க்கவும்."
        else:
            brief_en = f"Demands patience and strategic discipline. Focus on consolidating current routines and avoiding speculative risks."
            brief_ta = f"பொறுமையும் நிதானமும் தேவைப்படும் வாரம்; புதிய பெரிய முதலீடுகளைத் தவிர்த்து அன்றாட பணிகளில் கவனம் செலுத்தவும்."
            peak_en = "Deep focus, spiritual peace, and clearing accumulated back-office work."
            peak_ta = "அமைதியான ஆன்மீக வழிபாடு மற்றும் நிலுவை வேலைகளை சீர் செய்வதற்கு ஏற்றது."
            caution_en = f"Observe high vigilance during Chandrashtama ({c_en}); guard against impulse expense."
            caution_ta = f"சந்திராஷ்டம நாட்களில் ({c_ta}) கவனமாக வாகனம் ஓட்டவும்; கடன் வாங்குவதைத் தவிர்க்கவும்."

        lucky_attr = RASHI_LUCKY_ATTRIBUTES.get(r_idx, RASHI_LUCKY_ATTRIBUTES[1])
        remedy_pair = KP_WEEKLY_REMEDIES.get(sign_lord, KP_WEEKLY_REMEDIES["Jupiter"])

        pred = RashiWeeklyPrediction(
            rashi_id=r_idx,
            rashi_name_en=r_en,
            rashi_name_ta=r_ta,
            sign_lord=sign_lord,
            weekly_score=weekly_score,
            weekly_rating_stars=weekly_rating_stars,
            week_sentiment=week_sentiment,
            brief_statement_en=brief_en,
            brief_statement_ta=brief_ta,
            peak_highlight_en=peak_en,
            peak_highlight_ta=peak_ta,
            caution_trap_en=caution_en,
            caution_trap_ta=caution_ta,
            lucky_days_en=l_en,
            lucky_days_ta=l_ta,
            chandrashtama_days_en=c_en,
            chandrashtama_days_ta=c_ta,
            lucky_color_en=lucky_attr["color_en"],
            lucky_color_ta=lucky_attr["color_ta"],
            lucky_number=lucky_attr["num"],
            lucky_direction_en=lucky_attr["dir_en"],
            lucky_direction_ta=lucky_attr["dir_ta"],
            weekly_remedy_en=remedy_pair[0],
            weekly_remedy_ta=remedy_pair[1],
            aspects=aspect_list,
            transit_summary=transit_summary,
        )
        predictions.append(pred)

    return KpWeeklyHoroscopeResponse(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        week_label_en=week_label_en,
        week_label_ta=week_label_ta,
        ayanamsa_name=aya_name,
        total_rashis=len(predictions),
        major_transits=global_movements_recorded,
        predictions=predictions,
        calculated_at=now_local.isoformat(),
    )


def compute_kp_monthly_horoscope(
    year: Optional[int] = None,
    month: Optional[int] = None,
    target_date: Optional[date | str] = None,
    timezone_str: str = "Asia/Kolkata",
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    rashi_filter: Optional[str] = "all",
    ayanamsa_id: int = 1,
) -> KpMonthlyHoroscopeResponse:
    """Computes high-precision KP monthly predictions for all or requested Rashis."""
    tz_clean = timezone_str.strip() if timezone_str else "Asia/Kolkata"
    try:
        tz_obj = ZoneInfo(tz_clean)
    except Exception:
        tz_obj = ZoneInfo("Asia/Kolkata")

    now_local = datetime.now(tz_obj)

    if year is not None and month is not None:
        calc_year = int(year)
        calc_month = int(month)
    elif target_date is not None:
        if isinstance(target_date, str):
            dt_parsed = datetime.strptime(target_date.strip(), "%Y-%m-%d").date()
        else:
            dt_parsed = target_date
        calc_year = dt_parsed.year
        calc_month = dt_parsed.month
    else:
        calc_year = now_local.year
        calc_month = now_local.month

    # Month boundaries
    _, last_day = calendar.monthrange(calc_year, calc_month)
    start_date = date(calc_year, calc_month, 1)
    end_date = date(calc_year, calc_month, last_day)

    month_name_en = f"{MONTHS_EN.get(calc_month, '')} {calc_year}"
    month_name_ta = f"{MONTHS_TA.get(calc_month, '')} {calc_year}"

    # Ephemeris planetary positions at midpoint of the month (15th noon)
    mid_date = date(calc_year, calc_month, min(15, last_day))
    planet_positions = _get_planet_positions_at_date(mid_date, tz_obj, ayanamsa_id)

    # Detect all ingresses during this month
    ingresses = _detect_transit_ingresses_in_period(start_date, end_date, tz_obj, ayanamsa_id)

    aya_name = AYANAMSA_NAMES.get(ayanamsa_id, ("KP", ""))[0]

    # Resolve Rashis to evaluate
    rashis_to_calc: List[int] = []
    if not rashi_filter or str(rashi_filter).strip().lower() in ("all", "0", ""):
        rashis_to_calc = list(range(1, 13))
    elif str(rashi_filter).strip().isdigit():
        r_num = int(str(rashi_filter).strip())
        rashis_to_calc = [r_num] if 1 <= r_num <= 12 else list(range(1, 13))
    else:
        clean_name = str(rashi_filter).strip().capitalize()
        matched = SIGN_TO_INDEX.get(clean_name, None)
        rashis_to_calc = [matched] if matched else list(range(1, 13))

    predictions: List[RashiMonthlyPrediction] = []
    global_movements_recorded: List[TransitMovement] = []

    for r_idx in rashis_to_calc:
        r_en, r_ta, sign_lord = RASHI_METADATA[r_idx]

        # Chandrashtama date ranges & Auspicious dates across the month
        c_en, c_ta, l_en, l_ta = _track_moon_and_chandrashtama(start_date, end_date, r_idx, tz_obj, ayanamsa_id, is_weekly=False)

        # Transit summary
        transit_summary, transit_mod, movements = _build_rashi_transit_summary(
            r_idx, planet_positions, ingresses, c_en, c_ta, is_weekly=False
        )

        if not global_movements_recorded:
            global_movements_recorded = movements

        # Aspects & overall score
        aspect_list, monthly_score = _build_period_aspects(
            r_en, r_ta, r_idx, planet_positions, transit_mod, is_weekly=False
        )

        monthly_rating_stars = round(1.0 + (monthly_score / 100.0) * 4.0, 1)
        if monthly_score >= 76:
            month_sentiment = "Excellent"
        elif monthly_score >= 60:
            month_sentiment = "Favorable"
        elif monthly_score >= 45:
            month_sentiment = "Mixed"
        else:
            month_sentiment = "Challenging"

        # Executive brief statement
        if monthly_score >= 75:
            brief_en = f"A remarkably prosperous month filled with expansive opportunities. Favorable Gochara alignment empowers career growth, wealth accumulation, and family happiness."
            brief_ta = f"இந்த மாதம் கிரகங்களின் சாதகமான சஞ்சாரத்தால் பெரும் நன்மைகள் விளையும்; புதிய தொழில் வாய்ப்புகள், பணவரவு பெருக்கம் மற்றும் குடும்பத்தில் சுப காரியங்கள் கைகூடும்."
            peak_en = "Major milestone achieved in career, acquisition of coveted assets, and outstanding financial inflows."
            peak_ta = "தொழிலில் புதிய திருப்புமுனை, சொத்து சேர்க்கை மற்றும் பன்மடங்கு வருமான உயர்வு உண்டு."
            caution_en = f"Observe careful financial and travel vigilance on Chandrashtama dates ({c_en})."
            caution_ta = f"சந்திராஷ்டம தினங்களில் ({c_ta}) புதிய ஒப்பந்தங்கள், பெரிய முதலீடுகள் மற்றும் பயணங்களைத் தவிர்க்கவும்."
        elif monthly_score >= 58:
            brief_en = f"Constructive and steady month. Focused execution delivers durable progress in professional goals and domestic peace."
            brief_ta = f"உழைப்பிற்கேற்ற நற்பலன்களைத் தரும் சிறப்பான மாதம்; திட்டமிட்டு செயல்படுவதன் மூலம் பொருளாதார நிலை உயரும்."
            peak_en = "Successful clearance of long-pending tasks, recognition from superiors, and harmonious family ties."
            peak_ta = "நீண்ட நாள் நிலுவைப் பணிகள் முடிவுக்கு வரும்; மேலதிகாரிகளின் நன்மதிப்பு கிட்டும்."
            caution_en = f"Plan around Chandrashtama spans ({c_en}) and avoid taking on excessive domestic commitments."
            caution_ta = f"{c_ta} சந்திராஷ்டம நாட்களில் பொறுமை காக்கவும்; வீண் வாக்குவாதங்களைத் தவிர்க்கவும்."
        else:
            brief_en = f"Consolidation month requiring patience and methodical prudence. Prioritize health, avoid speculation, and rely on spiritual discipline."
            brief_ta = f"நிதானமும் எச்சரிக்கையும் தேவைப்படும் மாதம்; புதிய ரிஸ்க் எடுப்பதைத் தவிர்த்து, சேமிப்பிலும் ஆரோக்கியத்திலும் கவனம் செலுத்தவும்."
            peak_en = "Strengthening inner resilience, peaceful spiritual discovery, and clearing backlogs."
            peak_ta = "தியானம் மற்றும் ஆன்மீக வழிபாட்டால் மன அமைதியும் புதிய தெளிவும் பிறக்கும்."
            caution_en = f"Strict caution during Chandrashtama ({c_en}); guard against impulsive decisions and financial guarantees."
            caution_ta = f"சந்திராஷ்டம தினங்களில் ({c_ta}) கவனமாக இருக்கவும்; யாருக்கும் கடன் கொடுப்பதோ வாங்குவதோ வேண்டாம்."

        lucky_attr = RASHI_LUCKY_ATTRIBUTES.get(r_idx, RASHI_LUCKY_ATTRIBUTES[1])
        remedy_pair = KP_MONTHLY_REMEDIES.get(sign_lord, KP_MONTHLY_REMEDIES["Jupiter"])

        pred = RashiMonthlyPrediction(
            rashi_id=r_idx,
            rashi_name_en=r_en,
            rashi_name_ta=r_ta,
            sign_lord=sign_lord,
            monthly_score=monthly_score,
            monthly_rating_stars=monthly_rating_stars,
            month_sentiment=month_sentiment,
            brief_statement_en=brief_en,
            brief_statement_ta=brief_ta,
            peak_highlight_en=peak_en,
            peak_highlight_ta=peak_ta,
            caution_trap_en=caution_en,
            caution_trap_ta=caution_ta,
            auspicious_dates_en=l_en,
            auspicious_dates_ta=l_ta,
            chandrashtama_dates_en=c_en,
            chandrashtama_dates_ta=c_ta,
            lucky_color_en=lucky_attr["color_en"],
            lucky_color_ta=lucky_attr["color_ta"],
            lucky_number=lucky_attr["num"],
            lucky_direction_en=lucky_attr["dir_en"],
            lucky_direction_ta=lucky_attr["dir_ta"],
            monthly_remedy_en=remedy_pair[0],
            monthly_remedy_ta=remedy_pair[1],
            aspects=aspect_list,
            transit_summary=transit_summary,
        )
        predictions.append(pred)

    return KpMonthlyHoroscopeResponse(
        year=calc_year,
        month=calc_month,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        month_name_en=month_name_en,
        month_name_ta=month_name_ta,
        ayanamsa_name=aya_name,
        total_rashis=len(predictions),
        major_transits=global_movements_recorded,
        predictions=predictions,
        calculated_at=now_local.isoformat(),
    )
