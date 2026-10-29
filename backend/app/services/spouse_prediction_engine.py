"""Spouse & Life Partner Prediction Engine.

Implements classical 4-step Vedic Spouse Astrology:
1. 7th House & Planets Situated in the 7th House (from Lagna).
2. 7th Lord Placement, Dignity, and Elemental Nature (Fire, Earth, Air, Water).
3. Key Significators (Karakas):
   - Venus (Shukra): Natural significator of wife, love, and conjugal elegance for men.
   - Jupiter (Guru) & Mars (Kuja): Significators of husband and passion for women.
   - Mars-Venus synergy for mutual romance and attraction.
4. Navamsa (D9) Chart 7th House & Lord (Spouse's inner soul nature & long-term marriage).
5. "Mind's Desire vs Worldly Reality" (7th from Moon vs 7th from Lagna).
6. Quantitative Scores for Romantic Nature, Loyalty, Intelligence, and Physical Charm.
7. Remedial Prescriptions: Gemstones (e.g. White Zircon), Fasting Days, Colors, and Mantras.

Fully bilingual (English & Tamil).
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
import math
from datetime import datetime

import xalen
import xalen.swe as xswe

from app.schemas.common import BirthInput, CalculationMetadata
from app.schemas.spouse_prediction import (
    SpousePlanetInfluence,
    SeventhLordElementalAnalysis,
    SpouseSignAnalysis,
    DesireVsRealityAnalysis,
    SpouseKarakasAnalysis,
    NavamsaD9SpouseProfile,
    SpouseTraitScores,
    SpouseRemedies,
    SpousePredictionRequest,
    SpousePredictionResponse,
)
from app.services.timezone_utils import resolve_birth_datetime
from app.services.ephemeris import (
    compute_planetary_positions,
    get_sign_info,
    ZODIAC_SIGNS,
)
from app.services.varga_engine import calculate_navamsa_from_longitude

# ---------------------------------------------------------------------------
# Classical Reference Constants
# ---------------------------------------------------------------------------

SIGN_NAMES_EN = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

SIGN_NAMES_TA = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

PLANET_NAMES_TA = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு (வியாழன்)",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "இராகு",
    "Ketu": "கேது",
}

ELEMENT_BY_SIGN = {
    1: ("Fire", "நெருப்பு தத்துவம்"),
    2: ("Earth", "நில தத்துவம்"),
    3: ("Air", "காற்று தத்துவம்"),
    4: ("Water", "நீர் தத்துவம்"),
    5: ("Fire", "நெருப்பு தத்துவம்"),
    6: ("Earth", "நில தத்துவம்"),
    7: ("Air", "காற்று தத்துவம்"),
    8: ("Water", "நீர் தத்துவம்"),
    9: ("Fire", "நெருப்பு தத்துவம்"),
    10: ("Earth", "நில தத்துவம்"),
    11: ("Air", "காற்று தத்துவம்"),
    12: ("Water", "நீர் தத்துவம்"),
}

EXALTATION_SIGNS = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7, "Rahu": 2, "Ketu": 8
}

DEBILITATION_SIGNS = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
    "Jupiter": 10, "Venus": 6, "Saturn": 1, "Rahu": 8, "Ketu": 2
}

OWN_SIGNS = {
    "Sun": {5}, "Moon": {4}, "Mars": {1, 8}, "Mercury": {3, 6},
    "Jupiter": {9, 12}, "Venus": {2, 7}, "Saturn": {10, 11}
}

MOOLATRIKONA_SIGNS = {
    "Sun": 5, "Moon": 2, "Mars": 1, "Mercury": 6,
    "Jupiter": 9, "Venus": 7, "Saturn": 11
}

# ---------------------------------------------------------------------------
# Detailed Interpretive Content for 7th House Planets
# ---------------------------------------------------------------------------

PLANET_7TH_INTERPRETATIONS = {
    "Sun": {
        "spouse_type_en": "Dignified, Authoritative & Prominent Life Partner",
        "spouse_type_ta": "கண்ணியமான, தலைமைத்துவ குணம் மற்றும் செல்வாக்கு மிக்க துணை",
        "characteristics_en": [
            "Hails from a respectable, honorable family with good lineage.",
            "Possesses a regal presence, ambitious mindset, and high self-esteem.",
            "Generous and magnanimous in social dealings, though firm in decisions.",
            "Can occasionally be commanding or proud; values mutual respect above all."
        ],
        "characteristics_ta": [
            "மரியாதைக்குரிய, கௌரவமிக்க குடும்பப் பின்னணியில் இருந்து வருபவர்.",
            "தலைமைப் பண்பும், கம்பீரமான தோற்றமும், உயர்ந்த லட்சியமும் கொண்டவர்.",
            "சமூகத்தில் தாராள மனப்பான்மையுடன் நடந்துகொள்வார்; தன்மானத்திற்கு முதலிடம் அளிப்பார்.",
            "சில நேரங்களில் ஆதிக்கம் அல்லது கர்வம் வெளிப்படலாம்; மரியாதையை அதிகம் எதிர்பார்ப்பார்."
        ],
        "positives_en": ["High social standing", "Generosity", "Steadfast loyalty", "Leadership capability"],
        "positives_ta": ["உயர் சமூக அந்தஸ்து", "தாராள குணம்", "உறுதியான உண்மைத்தன்மை", "தலைமைத்துவ ஆற்றல்"],
        "watchouts_en": ["Ego clashes if boundaries are disrespected", "Occasional short-tempered nature"],
        "watchouts_ta": ["தன்மானம் சீண்டப்படும்போது வாக்குவாதம்", "அவ்வப்போது கோப உணர்ச்சி"],
    },
    "Moon": {
        "spouse_type_en": "Gentle, Nurturing & Emotionally Deep Life Partner",
        "spouse_type_ta": "அன்பான, குடும்பப் பாசமும் உணர்வுபூர்வமான மனமும் கொண்ட துணை",
        "characteristics_en": [
            "Deeply empathetic, tender-hearted, and family-oriented.",
            "Loves home comforts and creates a cozy, affectionate domestic environment.",
            "Intuitive and highly responsive to emotional nuances and partner's moods.",
            "Prone to emotional fluctuations, echoing the waxing and waning cycles of the Moon."
        ],
        "characteristics_ta": [
            "மிகவும் இரக்க குணம், மென்மையான இதயம் மற்றும் குடும்ப பற்று கொண்டவர்.",
            "வீட்டு சூழலை பாசத்துடனும் அழகிய அமைதியுடனும் வைத்திருப்பார்.",
            "உணர்வுகளை மிக எளிதில் புரிந்துகொள்ளும் நுண்ணறிவு கொண்டவர்.",
            "சந்திரனின் பிறை மாற்றங்களை போல அவ்வப்போது மனநிலையில் ஏற்ற இறக்கங்கள் (Mood swings) ஏற்படலாம்."
        ],
        "positives_en": ["Caring & nurturing", "Gentle demeanor", "Deep domestic devotion", "Empathetic listening"],
        "positives_ta": ["அக்கறையுடன் கூடிய அரவணைப்பு", "மென்மையான அணுகுமுறை", "குடும்பத்தில் முழு ஈடுபாடு", "உணர்வுபூர்வ ஆதரவு"],
        "watchouts_en": ["Over-sensitivity to casual remarks", "Periodic mood swings"],
        "watchouts_ta": ["சிறு வார்த்தைகளுக்கும் மனவருத்தம் அடைதல்", "அடிக்கடி மாறும் மனநிலை"],
    },
    "Mars": {
        "spouse_type_en": "Dynamic, High-Energy & Courageous Life Partner",
        "spouse_type_ta": "துணிச்சல், அபரிமிதமான சுறுசுறுப்பு மற்றும் கவர்ச்சிகரமான துணை",
        "characteristics_en": [
            "Energetic, athletic, and action-oriented with a drive to achieve results.",
            "Straightforward and transparent in speech; dislikes pretense or ambiguity.",
            "Brings strong passion, physical vitality, and enthusiasm to marital life.",
            "Can be quick-tempered, headstrong, or argumentative when stressed."
        ],
        "characteristics_ta": [
            "சுறுசுறுப்பான, தைரியமான மற்றும் செயல்பாடுகளில் வேகம் காட்டும் குணம் கொண்டவர்.",
            "நேரடியான பேச்சு, ஒளிவுமறைவற்ற அணுகுமுறை கொண்டவர்; பாசாங்குகளை விரும்பமாட்டார்.",
            "தாம்பத்திய வாழ்க்கையில் தீவிர ஈடுபாடும், உடல் ரீதியான ஆற்றலும் நிறைந்தவர்.",
            "கோபமும் பிடிவாதமும் விரைவாக எழலாம்; பொறுமை காப்பது மிக அவசியம்."
        ],
        "positives_en": ["Courageous protector", "Industrious & hardworking", "Passionate romantic bond", "Decisive action"],
        "positives_ta": ["பாதுகாப்பு அரணாக இருத்தல்", "கடின உழைப்பாளி", "தீவிர காதல் மற்றும் ஈர்ப்பு", "துணிச்சலான முடிவெடுத்தல்"],
        "watchouts_en": ["Impatience & hasty temper", "Requires conscious conflict de-escalation"],
        "watchouts_ta": ["பொறுமையின்மை மற்றும் அவசரக் கோபம்", "வாக்குவாதங்களை தவிர்க்க நிதானம் தேவை"],
    },
    "Mercury": {
        "spouse_type_en": "Witty, Intelligent & Youthful Life Partner",
        "spouse_type_ta": "புத்திசாலி, நகைச்சுவை உணர்வும் இளமைத் தோற்றமும் கொண்ட துணை",
        "characteristics_en": [
            "Sharp intellect, excellent conversationalist, and quick-witted humor.",
            "Youthful appearance, cheerful demeanor, and playful communication style.",
            "Skilled at commercial negotiations, multitasking, and practical problem-solving.",
            "Keeps the relationship lively, intellectually stimulating, and socially active."
        ],
        "characteristics_ta": [
            "கூரிய மதிநுட்பம், அருமையான உரையாடல் திறன் மற்றும் நகைச்சுவை சுபாவம்.",
            "இளமையான தோற்றம், சுறுசுறுப்பான நடத்தை மற்றும் கலகலப்பான அணுகுமுறை.",
            "வர்த்தகம், கணக்கு வழக்கு மற்றும் பல வேலைகளை ஒரே நேரத்தில் செய்யும் சாமர்த்தியம்.",
            "தாம்பத்திய பந்தத்தை சலிப்படையாமல் எப்போதும் உற்சாகமாக வைத்திருப்பார்."
        ],
        "positives_en": ["Brilliant communication", "Youthful radiance", "Analytical intellect", "Jovial companion"],
        "positives_ta": ["சிறந்த தகவல் தொடர்பு", "எப்போதும் இளமையான வசீகரம்", "ஆராய்ச்சி புத்தி", "மகிழ்ச்சியான நட்பு"],
        "watchouts_en": ["Restlessness or nervousness", "Over-intellectualizing emotional moments"],
        "watchouts_ta": ["அமைதியற்ற படபடப்பு", "உணர்வுகளை கூட தர்க்கரீதியாக பகுப்பாய்வு செய்தல்"],
    },
    "Jupiter": {
        "spouse_type_en": "Wise, Highly Educated & Morally Noble Life Partner",
        "spouse_type_ta": "ஞானம், உயர்கல்வி மற்றும் தெய்வீக நற்குணங்கள் நிறைந்த துணை",
        "characteristics_en": [
            "Spiritual, morally upright, and respected for noble virtues and integrity.",
            "Well-educated, scholarly, and guided by philosophical and ethical principles.",
            "Deeply supportive, encouraging personal growth, spiritual progress, and family prosperity.",
            "Brings divine grace into marital life, acting as a wise counselor and faithful companion."
        ],
        "characteristics_ta": [
            "ஆன்மீக பற்று, உயர்ந்த ஒழுக்கம் மற்றும் நற்பண்புகளால் சமூகத்தில் மதிக்கப்படுபவர்.",
            "சிறந்த படிப்பு, பரந்த அறிவு மற்றும் சாஸ்திர தர்மங்களின் மீது நம்பிக்கை உடையவர்.",
            "குடும்பத்தின் மேன்மைக்கும், ஆன்மீக முன்னேற்றத்திற்கும் உறுதுணையாக இருப்பார்.",
            "தெய்வ அருள் நிறைந்த வழிகாட்டியாகவும், உன்னதமான வாழ்க்கைத்துணையாகவும் விளங்குவார்."
        ],
        "positives_en": ["Exceptional moral loyalty", "Scholarly wisdom", "Spiritual devotion", "Prosperous presence"],
        "positives_ta": ["உயர்ந்த உண்மைத்தன்மை", "சான்றோர்க்குரிய அறிவு", "இறையன்பு", "சுப யோக நல்வாழ்வு"],
        "watchouts_en": ["Can be overly idealistic", "Occasional preachy or critical attitude"],
        "watchouts_ta": ["அதிகப்படியான நீதிபோதனை குணம்", "சிறு தவறுகளையும் கண்டிக்கும் சுபாவம்"],
    },
    "Venus": {
        "spouse_type_en": "Charming, Highly Attractive & Refined Romantic Life Partner",
        "spouse_type_ta": "பேரழகு, வசீகரம் மற்றும் கலை ரசனையுடன் கூடிய காதல் துணை",
        "characteristics_en": [
            "Remarkable physical beauty, grace, and an aesthetically refined persona.",
            "Deeply romantic, affectionate, soft-spoken, and appreciative of poetry, music, and art.",
            "Loves elegance, luxury, neatness, and cultivating a peaceful, harmonious home.",
            "Considered one of the most auspicious classical placements for marital happiness and bliss."
        ],
        "characteristics_ta": [
            "கண்களைக் கவரும் உடல் அழகு, நளினம் மற்றும் கவர்ச்சிகரமான ஆளுமை.",
            "ஆழ்ந்த காதல் குணம், மென்மையான பேச்சு, கலை, இசை மற்றும் அழகியல் ரசனை.",
            "சுகபோகம், வசதியான வாழ்க்கை மற்றும் இல்லறத்தில் அமைதியை விரும்புவார்.",
            "வேத ஜோதிடத்தில் மகிழ்ச்சியான தாம்பத்தியத்திற்கு இது மிகச் சிறந்த சுப யோகமாகும்."
        ],
        "positives_en": ["Great beauty & charm", "Romantic sweetness", "Artistic sophistication", "Harmonious companionship"],
        "positives_ta": ["அழகிய வசீகர தோற்றம்", "அன்பான பாசம்", "கலைநயம்", "இனிமையான தாம்பத்தியம்"],
        "watchouts_en": ["High expectation of material comforts", "May avoid harsh practical realities"],
        "watchouts_ta": ["ஆடம்பர வசதிகளில் அதிக நாட்டம்", "கடினமான எதார்த்தங்களை எதிர்கொள்ள தயங்குதல்"],
    },
    "Saturn": {
        "spouse_type_en": "Mature, Dutiful, Hardworking & Rock-Solid Life Partner",
        "spouse_type_ta": "முதிர்ச்சி, கடமை உணர்வு, உழைப்பாளி மற்றும் அசைக்க முடியாத உண்மைத் துணை",
        "characteristics_en": [
            "Responsible, pragmatic, and serious with an unwavering sense of duty.",
            "Exceptionally steadfast and faithful; once committed, stays through every challenge.",
            "Spouse is often older in age or possesses an old-soul maturity and sober outlook.",
            "May initially seem reserved or unromantic, but proves to be an enduring lifelong anchor."
        ],
        "characteristics_ta": [
            "கடமை தவறாத மனப்பான்மை, பொறுப்புணர்வு மற்றும் கடுமையான உழைப்பாளி.",
            "அசைக்க முடியாத உண்மைத்தன்மை; எந்த சூழ்நிலையிலும் துணையை கைவிடாத விசுவாசம்.",
            "வயதில் மூத்தவராகவோ அல்லது முதிர்ந்த சிந்தனை கொண்டவராகவோ அமைவார்.",
            "ஆரம்பத்தில் வெளிப்படையான காதல் குறைவாகத் தோன்றினாலும், வாழ்நாள் முழுவதும் பாறையைப் போன்ற பாதுகாப்பு."
        ],
        "positives_en": ["Unshakeable loyalty", "Practical stability", "Enduring longevity of bond", "Financial prudence"],
        "positives_ta": ["உறுதியான நம்பகத்தன்மை", "நடைமுறை வாழ்க்கை ஸ்திரத்தன்மை", "நீண்ட ஆயுள் பலம்", "சிக்கனமான நிதி மேலாண்மை"],
        "watchouts_en": ["May be emotionally reserved", "Can induce delay or soberness in romantic expressions"],
        "watchouts_ta": ["உணர்வுகளை வெளிப்படுத்துவதில் தயக்கம்", "காதல் வெளிப்பாடுகளில் தாமதமும் மிதமிஞ்சிய கட்டுப்பாடும்"],
    },
    "Rahu": {
        "spouse_type_en": "Unconventional, Progressive & Sharply Intelligent Life Partner",
        "spouse_type_ta": "புதுமை விரும்பி, நவீன சிந்தனை மற்றும் அதிபுத்திசாலி துணை",
        "characteristics_en": [
            "Modern, unconventional mindset that questions orthodox societal boundaries.",
            "Sharp intellect, ambitious drives, and fascination with progressive ideas or technology.",
            "Frequently indicates a spouse from a different cultural, foreign, or inter-community background.",
            "Charismatic and out-of-the-box thinker who brings unique experiences into the union."
        ],
        "characteristics_ta": [
            "மரபுவழி கட்டுப்பாடுகளைத் தாண்டி சிந்திக்கும் முற்போக்கான நவீன மனம்.",
            "கூரிய புத்தி, பெரிய லட்சியங்கள் மற்றும் நவீன தொழில்நுட்பங்களில் ஆர்வம்.",
            "வேற்று மொழி, வெளிநாடு அல்லது கலப்பு கலாச்சார பின்னணியில் இருந்து வர வாய்ப்பு உண்டு.",
            "தனித்துவமான ஆளுமை மற்றும் வசீகரம் கொண்டு வாழ்க்கையில் புதுமை சேர்ப்பார்."
        ],
        "positives_en": ["Dynamic innovator", "Culturally expansive", "Broad-minded worldview", "Intensely ambitious"],
        "positives_ta": ["புதுமையான சிந்தனை", "பரந்த கலாச்சார பார்வை", "தடைகளை உடைக்கும் ஆற்றல்", "உயர்ந்த லட்சிய வேட்கை"],
        "watchouts_en": ["Impulsive tendencies", "Unpredictable shifts in domestic routines"],
        "watchouts_ta": ["முன்கூட்டியே திட்டமிடாத அவசர முடிவுகள்", "திடீர் மனநிலை மற்றும் எதிர்பார்ப்புகள்"],
    },
    "Ketu": {
        "spouse_type_en": "Spiritual, Introverted & Philosophically Inclined Life Partner",
        "spouse_type_ta": "ஆன்மீக நாட்டம், அமைதியான இயல்பு மற்றும் தத்துவ ஞானம் கொண்ட துணை",
        "characteristics_en": [
            "Deeply spiritual, introspective, and relatively detached from materialistic vanity.",
            "Gifted in esoteric, mathematical, computational, or research-oriented disciplines.",
            "Quiet and contemplative; may express love through silence and subtle devotion rather than words.",
            "A serene soul who encourages spiritual liberation and inner peace in the household."
        ],
        "characteristics_ta": [
            "ஆழ்ந்த ஆன்மீக ஈடுபாடு, உள்முக சிந்தனை மற்றும் ஆடம்பரங்களில் பற்றற்ற இயல்பு.",
            "கணிதம், கணினி, அறிவியல் ஆராய்ச்சி அல்லது மறைபொருள் துறைகளில் அபார திறமை.",
            "அமைதியான சுபாவம்; வார்த்தைகளை விட உள்ளுணர்வால் அன்பை வெளிப்படுத்துவார்.",
            "இல்லறத்தில் அமைதியையும், ஆன்மீக விடுதலையையும் வளர்க்கும் பக்குவம் கொண்டவர்."
        ],
        "positives_en": ["Deep spiritual maturity", "Intellectual depth", "Freedom from greed", "Subtle profound loyalty"],
        "positives_ta": ["ஆன்மீக முதிர்ச்சி", "ஆழ்ந்த அறிவுத்திறன்", "ஆடம்பரமற்ற எளிமை", "அமைதியான உண்மைப்பற்று"],
        "watchouts_en": ["Difficulty expressing romantic feelings verbally", "Tendency toward seclusion"],
        "watchouts_ta": ["காதலை வெளிப்படையாக பேசத் தயங்குதல்", "தனிமையை நாடும் சுபாவம்"],
    },
}

# ---------------------------------------------------------------------------
# 7th House Sign Temperaments
# ---------------------------------------------------------------------------

SIGN_TEMPERAMENTS = {
    1: {
        "temperament_en": "Courageous, active, bold, and dynamic spouse with athletic vitality.",
        "temperament_ta": "தைரியம், சுறுசுறுப்பு, துணிச்சல் மற்றும் விளையாட்டுத் திறன் கொண்ட துணை.",
        "traits_en": ["Courageous & direct", "Action-oriented", "Passionate lover", "Competitive spirit"],
        "traits_ta": ["தைரியமான நேர்பேச்சு", "சுறுசுறுப்பான செயல்", "தீவிர காதல்", "முன்னேறும் துடிப்பு"]
    },
    2: {
        "temperament_en": "Practical, grounded, beauty-loving, and financially prudent spouse.",
        "temperament_ta": "நிதானமான, கலை ரசனை, நிதி ஸ்திரத்தன்மை மற்றும் பொறுமை கொண்ட துணை.",
        "traits_en": ["Grounded & reliable", "Fond of arts & music", "Values security", "Sensual & steady"],
        "traits_ta": ["நம்பகமான அணுகுமுறை", "இசை மற்றும் கலை ஆர்வம்", "பாதுகாப்பு உணர்வு", "நிலையான அன்பு"]
    },
    3: {
        "temperament_en": "Versatile, communicative, witty, and socially engaging companion.",
        "temperament_ta": "சுறுசுறுப்பான, சிறந்த பேச்சாளர், நகைச்சுவை மற்றும் பன்முகத் திறன் கொண்ட துணை.",
        "traits_en": ["Brilliant communicator", "Curious & intellectual", "Multitasker", "Playful & youthful"],
        "traits_ta": ["சிறந்த பேச்சாற்றல்", "கற்றலில் ஆர்வம்", "பன்முக ஆற்றல்", "துள்ளலான இளமைத்தனம்"]
    },
    4: {
        "temperament_en": "Nurturing, deeply emotional, protective, and family-centered partner.",
        "temperament_ta": "பாசமிக்க, உணர்ச்சிமயமான, குடும்பத்தை கண்ணாக காக்கும் தாயுள்ளம் கொண்ட துணை.",
        "traits_en": ["Nurturing & empathetic", "Deep family attachment", "Protective guardian", "Tender-hearted"],
        "traits_ta": ["அரவணைக்கும் அன்பு", "குடும்ப பற்று", "பாதுகாக்கும் உணர்வு", "மென்மையான இதயம்"]
    },
    5: {
        "temperament_en": "Proud, charismatic, commanding, and naturally noble life partner.",
        "temperament_ta": "கம்பீரம், கம்பீரமான தலைமை, தன்மானம் மற்றும் ஈகை குணம் கொண்ட துணை.",
        "traits_en": ["Dignified & regal", "High self-respect", "Generous benefactor", "Commanding presence"],
        "traits_ta": ["கம்பீரமான ஆளுமை", "உயர்ந்த தன்மானம்", "தாராள உள்ளம்", "கவர்ச்சிகரமான தோற்றம்"]
    },
    6: {
        "temperament_en": "Analytical, meticulous, hardworking, and perfectionist partner.",
        "temperament_ta": "கூரிய ஆராய்ச்சி புத்தி, ஒழுக்கம், கடின உழைப்பு மற்றும் நுட்பமான பார்வை கொண்ட துணை.",
        "traits_en": ["Logical & detail-oriented", "Service-minded", "Perfectionist", "Sharp business sense"],
        "traits_ta": ["தர்க்கரீதியான பார்வை", "உதவும் மனப்பான்மை", "நேர்த்தி மற்றும் ஒழுங்கு", "சிறந்த நிர்வாகத்திறன்"]
    },
    7: {
        "temperament_en": "Harmonious, artistic, diplomatic, and aesthetically charming partner.",
        "temperament_ta": "சமநிலை, கலை நேர்த்தி, சமரசப் பண்பு மற்றும் பேரழகு கொண்ட துணை.",
        "traits_en": ["Balanced & diplomatic", "Artistic taste", "Gentle demeanor", "Mutual respect oriented"],
        "traits_ta": ["சமரச பேச்சுவார்த்தை", "கலை நயமிக்க அழகு", "இனிமையான அணுகுமுறை", "பரஸ்பர மதிப்பு"]
    },
    8: {
        "temperament_en": "Intense, deeply passionate, secretive, and magnetically loyal spouse.",
        "temperament_ta": "ஆழ்ந்த ரகசியம், தீவிர பாசம், காந்த வசீகரம் மற்றும் அசைக்க முடியாத உண்மைத் துணை.",
        "traits_en": ["Deep & magnetic", "Fiercely loyal", "Intuitive psychologist", "Intensely emotional"],
        "traits_ta": ["காந்த வசீகர ஈர்ப்பு", "கடுமையான உண்மைப்பற்று", "மறைமுக நுண்ணறிவு", "ஆழமான உணர்ச்சி"]
    },
    9: {
        "temperament_en": "Learned, philosophical, righteous, and status-conscious noble spouse.",
        "temperament_ta": "படித்த மேதை, தர்ம நெறி, ஆன்மீக நாட்டம் மற்றும் சமூக அந்தஸ்து கொண்ட துணை.",
        "traits_en": ["Principled & ethical", "Philosophical learner", "Values status & honor", "Optimistic spirit"],
        "traits_ta": ["ஒழுக்கம் மற்றும் நேர்மை", "சாஸ்திர ஞானம்", "கௌரவ நாட்டம்", "நேர்மறை நம்பிக்கை"]
    },
    10: {
        "temperament_en": "Industrious, practical, disciplined, and goal-oriented dependable spouse.",
        "temperament_ta": "கடுமையான உழைப்பு, லட்சிய நோக்கு, கடமை உணர்வு மற்றும் நம்பகமான துணை.",
        "traits_en": ["Disciplined & patient", "Career-focused", "Enduring loyalty", "Rock-solid reliability"],
        "traits_ta": ["ஒழுக்கமும் பொறுமையும்", "தொழில் வெற்றி நாட்டம்", "நீண்டகால விசுவாசம்", "உறுதியான ஆதரவு"]
    },
    11: {
        "temperament_en": "Humanitarian, visionary, socially progressive, and intellectually unique spouse.",
        "temperament_ta": "சமூக சிந்தனை, பரந்த நட்பு வட்டம், சுதந்திர எண்ணம் மற்றும் புதுமை கொண்ட துணை.",
        "traits_en": ["Independent thinker", "Socially connected", "Innovative ideas", "Loyal friendship in love"],
        "traits_ta": ["சுயாதீன சிந்தனை", "நண்பர்கள் வட்டம்", "புதுமையான பார்வை", "நட்புடன் கூடிய காதல்"]
    },
    12: {
        "temperament_en": "Compassionate, dreamy, artistic, and spiritually receptive gentle partner.",
        "temperament_ta": "இரக்க குணம், கற்பனை வளம், ஆன்மீக ஈடுபாடு மற்றும் மென்மையான காதல் துணை.",
        "traits_en": ["Deeply empathetic", "Artistic & poetic", "Forgiving heart", "Spiritual inclination"],
        "traits_ta": ["உயர்ந்த இரக்கம்", "கலை மற்றும் கவிதை ரசனை", "மன்னிக்கும் சுபாவம்", "ஆன்மீக நாட்டம்"]
    },
}

# ---------------------------------------------------------------------------
# Elemental Traits for 7th Lord
# ---------------------------------------------------------------------------

ELEMENT_DESCRIPTIONS = {
    "Fire": {
        "traits_en": ["Dynamic & courageous", "Ambitious leadership", "Direct communication", "High social dignity"],
        "traits_ta": ["சுறுசுறுப்பும் தைரியமும்", "தலைமைத்துவ லட்சியம்", "நேரடியான பேச்சு", "உயர் சமூக கௌரவம்"],
        "desc_en": (
            "The 7th Lord sits in a Fiery sign (Aries, Leo, or Sagittarius). Your life partner will be "
            "vibrant, bold, active, and confident with high self-esteem and natural authority in society."
        ),
        "desc_ta": (
            "7-ஆம் அதிபதி நெருப்பு ராசியில் (மேஷம், சிம்மம், தனுசு) அமர்ந்துள்ளார். உங்கள் வாழ்க்கைத்துணை "
            "சுறுசுறுப்பான, தன்னம்பிக்கை மிக்க, தைரியமான மற்றும் சமூகத்தில் கம்பீரமான கௌரவம் கொண்டவராக அமைவார்."
        ),
    },
    "Earth": {
        "traits_en": ["Grounded & reliable", "Financial prudence", "Aesthetic appreciation", "Patient & stable"],
        "traits_ta": ["நம்பகமான அணுகுமுறை", "நிதி ஸ்திரத்தன்மை", "அழகியல் ரசனை", "பொறுமையும் ஸ்திரத்தன்மையும்"],
        "desc_en": (
            "The 7th Lord sits in an Earthy sign (Taurus, Virgo, or Capricorn). Your spouse will be "
            "pragmatic, realistic, deeply dependable, hardworking, and attentive to family security and aesthetics."
        ),
        "desc_ta": (
            "7-ஆம் அதிபதி நில ராசியில் (ரிஷபம், கன்னி, மகரம்) அமர்ந்துள்ளார். உங்கள் துணை நடைமுறைக்கு உகந்த, "
            "கடின உழைப்பாளி, நம்பகமான மற்றும் குடும்பத்தின் பொருளாதார ஸ்திரத்தன்மையை உறுதி செய்பவராக விளங்குவார்."
        ),
    },
    "Air": {
        "traits_en": ["Intellectual & curious", "Witty conversation", "Versatile multitasker", "Fun-loving companion"],
        "traits_ta": ["கூரிய அறிவுத்திறன்", "நகைச்சுவை உரையாடல்", "பன்முக ஆற்றல்", "மகிழ்ச்சியான தோழமை"],
        "desc_en": (
            "The 7th Lord sits in an Airy sign (Gemini, Libra, or Aquarius). Your spouse will be "
            "intellectually stimulating, socially engaging, articulate, and skilled in communication and problem-solving."
        ),
        "desc_ta": (
            "7-ஆம் அதிபதி காற்று ராசியில் (மிதுனம், துலாம், கும்பம்) அமர்ந்துள்ளார். உங்கள் துணை அறிவார்ந்த, "
            "சிறந்த தகவல் தொடர்பு, நகைச்சுவை மற்றும் புதிய விஷயங்களை விரைவாகக் கற்கும் சாமர்த்தியம் கொண்டவராக இருப்பார்."
        ),
    },
    "Water": {
        "traits_en": ["Deeply empathetic", "Intuitive connection", "Tender romantic care", "Protective loyalty"],
        "traits_ta": ["ஆழ்ந்த பரிவு", "உள்ளுணர்வு பிணைப்பு", "அன்பான கவனிப்பு", "பாதுகாப்பான பற்றுதல்"],
        "desc_en": (
            "The 7th Lord sits in a Watery sign (Cancer, Scorpio, or Pisces). Your spouse will be "
            "deeply emotional, sensitive, nurturing, caring, and intuitively connected to your innermost feelings."
        ),
        "desc_ta": (
            "7-ஆம் அதிபதி நீர் ராசியில் (கடகம், விருச்சிகம், மீனம்) அமர்ந்துள்ளார். உங்கள் துணை பாசமிக்க, "
            "உணர்ச்சிபூர்வமான, உங்கள் மனதை எளிதில் புரிந்துகொண்டு அரவணைக்கும் தாயுள்ளம் கொண்டவராக அமைவார்."
        ),
    },
}

# ---------------------------------------------------------------------------
# Helper Calculation Functions
# ---------------------------------------------------------------------------

def get_dignity(planet: str, sign_idx: int) -> Tuple[str, str]:
    """Determine classical dignity in English and Tamil."""
    if planet in EXALTATION_SIGNS and sign_idx == EXALTATION_SIGNS[planet]:
        return "Exalted", "உச்சம்"
    if planet in DEBILITATION_SIGNS and sign_idx == DEBILITATION_SIGNS[planet]:
        return "Debilitated", "நீசம்"
    if planet in MOOLATRIKONA_SIGNS and sign_idx == MOOLATRIKONA_SIGNS[planet]:
        return "Moolatrikona", "மூலத்திரிகோணம்"
    if planet in OWN_SIGNS and sign_idx in OWN_SIGNS[planet]:
        return "Own Sign", "சுய ஆட்சி"
    return "Neutral / Comfortable", "நட்பு / சம பலம்"


def check_parashari_aspect(planet_name: str, planet_sign: int, target_sign: int) -> bool:
    """Check if planet casts a Parashari aspect on the target sign."""
    offset = ((target_sign - planet_sign) % 12) + 1
    # All planets aspect the 7th house from their location
    if offset == 7:
        return True
    if planet_name == "Mars" and offset in (4, 8):
        return True
    if planet_name == "Jupiter" and offset in (5, 9):
        return True
    if planet_name == "Saturn" and offset in (3, 10):
        return True
    return False


# ---------------------------------------------------------------------------
# Engine Implementation
# ---------------------------------------------------------------------------

class SpousePredictionService:
    """Production service for Life Partner & Spouse Nature, Character & Type Prediction."""

    @classmethod
    def predict_spouse(cls, request: SpousePredictionRequest) -> SpousePredictionResponse:
        """Execute deterministic 4-step spouse prediction methodology."""
        birth = request.birth
        gender = (request.gender or "male").lower()

        # 1. Astronomical Calculation
        local_dt, utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
            birth.birth_date,
            birth.birth_time,
            birth.timezone,
        )

        # Sidereal positions with Lahiri ayanamsa
        vedic_planets = compute_planetary_positions(birth_jd, ayanamsa_id=0, include_outer=False)
        planet_by_name = {p.name: p for p in vedic_planets}

        # Ascendant calculation
        xswe.set_sid_mode(xswe.SIDM_LAHIRI, 0, 0)
        cusps_raw, ascmc_raw = xswe.houses_ex(birth_jd, birth.latitude, birth.longitude, b"W", xswe.FLG_SIDEREAL)
        asc_deg = ascmc_raw[0] % 360.0
        asc_sign_idx, asc_sign_name, asc_sign_tamil, _ = get_sign_info(asc_deg)

        # Moon sign
        moon_planet = planet_by_name.get("Moon")
        moon_deg = moon_planet.longitude if moon_planet else 0.0
        moon_sign_idx, moon_sign_name, moon_sign_tamil, _ = get_sign_info(moon_deg)

        # Whole Sign Houses: House 1 = asc_sign_idx, House 7 = (asc_sign_idx + 6 - 1) % 12 + 1
        seventh_sign_idx = ((asc_sign_idx + 6 - 1) % 12) + 1
        seventh_sign_name = SIGN_NAMES_EN[seventh_sign_idx]
        seventh_sign_tamil = SIGN_NAMES_TA[seventh_sign_idx]
        seventh_lord_name = SIGN_LORDS[seventh_sign_idx]
        seventh_lord_tamil = PLANET_NAMES_TA.get(seventh_lord_name, seventh_lord_name)

        # Planet house placements
        planet_house: Dict[str, int] = {}
        for p in vedic_planets:
            p_sign = p.sign_index
            h = ((p_sign - asc_sign_idx) % 12) + 1
            planet_house[p.name] = h

        # -----------------------------------------------------------------------
        # Step 1: 7th House Occupants & Aspects
        # -----------------------------------------------------------------------
        planets_in_7th: List[SpousePlanetInfluence] = []
        aspecting_planets: List[SpousePlanetInfluence] = []

        for p in vedic_planets:
            p_name = p.name
            p_sign = p.sign_index
            h = planet_house.get(p_name, 1)

            interp = PLANET_7TH_INTERPRETATIONS.get(p_name)
            if not interp:
                continue

            if h == 7:
                planets_in_7th.append(
                    SpousePlanetInfluence(
                        planet=p_name,
                        planet_tamil=PLANET_NAMES_TA.get(p_name, p_name),
                        status="OCCUPANT",
                        influence_type=f"Direct Presence in 7th House ({seventh_sign_name})",
                        influence_type_tamil=f"7-ஆம் பாவத்தில் நேரடி இருப்பு ({seventh_sign_tamil})",
                        spouse_type_en=interp["spouse_type_en"],
                        spouse_type_ta=interp["spouse_type_ta"],
                        characteristics_en=interp["characteristics_en"],
                        characteristics_ta=interp["characteristics_ta"],
                        positives_en=interp["positives_en"],
                        positives_ta=interp["positives_ta"],
                        watchouts_en=interp["watchouts_en"],
                        watchouts_ta=interp["watchouts_ta"],
                    )
                )
            elif check_parashari_aspect(p_name, p_sign, seventh_sign_idx):
                aspecting_planets.append(
                    SpousePlanetInfluence(
                        planet=p_name,
                        planet_tamil=PLANET_NAMES_TA.get(p_name, p_name),
                        status="ASPECT",
                        influence_type=f"Parashari Aspect from House {h} ({SIGN_NAMES_EN[p_sign]})",
                        influence_type_tamil=f"{h}-ஆம் இடத்தில் இருந்து பார்வை ({SIGN_NAMES_TA[p_sign]})",
                        spouse_type_en=interp["spouse_type_en"],
                        spouse_type_ta=interp["spouse_type_ta"],
                        characteristics_en=interp["characteristics_en"][:2],
                        characteristics_ta=interp["characteristics_ta"][:2],
                        positives_en=interp["positives_en"][:2],
                        positives_ta=interp["positives_ta"][:2],
                        watchouts_en=interp["watchouts_en"][:2],
                        watchouts_ta=interp["watchouts_ta"][:2],
                    )
                )

        # -----------------------------------------------------------------------
        # Step 2: 7th House Sign & 7th Lord Elemental Analysis
        # -----------------------------------------------------------------------
        sign_temp = SIGN_TEMPERAMENTS.get(seventh_sign_idx, SIGN_TEMPERAMENTS[1])
        seventh_sign_analysis = SpouseSignAnalysis(
            sign=seventh_sign_name,
            sign_tamil=seventh_sign_tamil,
            sign_number=seventh_sign_idx,
            ruler=seventh_lord_name,
            ruler_tamil=seventh_lord_tamil,
            temperament_en=sign_temp["temperament_en"],
            temperament_ta=sign_temp["temperament_ta"],
            core_traits_en=sign_temp["traits_en"],
            core_traits_ta=sign_temp["traits_ta"],
        )

        lord_planet = planet_by_name.get(seventh_lord_name)
        lord_sign_idx = lord_planet.sign_index if lord_planet else seventh_sign_idx
        lord_house_num = planet_house.get(seventh_lord_name, 1)
        lord_dignity_en, lord_dignity_ta = get_dignity(seventh_lord_name, lord_sign_idx)

        lord_element_en, lord_element_ta = ELEMENT_BY_SIGN[lord_sign_idx]
        element_meta = ELEMENT_DESCRIPTIONS[lord_element_en]

        seventh_lord_analysis = SeventhLordElementalAnalysis(
            lord_planet=seventh_lord_name,
            lord_planet_tamil=seventh_lord_tamil,
            sign=SIGN_NAMES_EN[lord_sign_idx],
            sign_tamil=SIGN_NAMES_TA[lord_sign_idx],
            sign_number=lord_sign_idx,
            house_placement=lord_house_num,
            dignity=lord_dignity_en,
            dignity_tamil=lord_dignity_ta,
            element=lord_element_en,
            element_tamil=lord_element_ta,
            elemental_traits_en=element_meta["traits_en"],
            elemental_traits_ta=element_meta["traits_ta"],
            description_en=element_meta["desc_en"],
            description_ta=element_meta["desc_ta"],
        )

        # -----------------------------------------------------------------------
        # Step 3: Karakas & Gender-Specific Insights
        # -----------------------------------------------------------------------
        venus_p = planet_by_name.get("Venus")
        venus_sign_idx = venus_p.sign_index if venus_p else 1
        venus_house_num = planet_house.get("Venus", 1)
        venus_dig_en, venus_dig_ta = get_dignity("Venus", venus_sign_idx)

        jupiter_p = planet_by_name.get("Jupiter")
        jupiter_sign_idx = jupiter_p.sign_index if jupiter_p else 1
        jupiter_house_num = planet_house.get("Jupiter", 1)
        jupiter_dig_en, jupiter_dig_ta = get_dignity("Jupiter", jupiter_sign_idx)

        mars_p = planet_by_name.get("Mars")
        mars_sign_idx = mars_p.sign_index if mars_p else 1
        mars_house_num = planet_house.get("Mars", 1)
        mars_dig_en, mars_dig_ta = get_dignity("Mars", mars_sign_idx)

        # Mars-Venus Synergy
        mars_venus_diff = abs((mars_p.longitude if mars_p else 0.0) - (venus_p.longitude if venus_p else 0.0)) % 360.0
        if mars_venus_diff > 180:
            mars_venus_diff = 360.0 - mars_venus_diff

        if mars_sign_idx == venus_sign_idx:
            synergy_en = "Mars and Venus are conjunct: extraordinary magnetic attraction, deep romantic passion, and intense conjugal warmth."
            synergy_ta = "செவ்வாயும் சுக்கிரனும் ஒரே ராசியில் சேர்க்கை: தீவிர கவர்ச்சி, ஆழ்ந்த காதல் ஈர்ப்பு மற்றும் அசாத்திய தாம்பத்திய அந்நியோன்யம்."
        elif abs(mars_house_num - venus_house_num) in (6, 4):
            synergy_en = "Mars and Venus are in mutual Kendra/Drishti: highly vibrant dynamic, passionate chemistry, and active relationship energy."
            synergy_ta = "செவ்வாயும் சுக்கிரனும் கேந்திர பார்வையில்: விறுவிறுப்பான உற்சாகம், ஆழ்ந்த ஈர்ப்பு மற்றும் துடிப்பான உறவுப் பிணைப்பு."
        else:
            synergy_en = "Mars and Venus maintain harmonious separation: balanced emotional expressions, dignified romance, and steady affection."
            synergy_ta = "செவ்வாயும் சுக்கிரனும் சமநிலை தூரத்தில்: அமைதியான உணர்வு வெளிப்பாடு, கண்ணியமான காதல் மற்றும் நிலையான பாசம்."

        if gender == "female":
            gender_en = (
                f"As a female native, Jupiter represents your husband's noble character and spiritual wisdom "
                f"(placed in {SIGN_NAMES_EN[jupiter_sign_idx]}, {jupiter_dig_en}), while Mars signifies his active drive and passion "
                f"(placed in {SIGN_NAMES_EN[mars_sign_idx]})."
            )
            gender_ta = (
                f"பெண் ஜாதகத்தில் குரு கணவனின் ஞானத்தையும் ஒழுக்கத்தையும் குறிக்கிறார் "
                f"({SIGN_NAMES_TA[jupiter_sign_idx]} ராசியில் {jupiter_dig_ta}), செவ்வாய் கணவரின் தைரியத்தையும் ஆண்மையையும் குறிக்கிறார் "
                f"({SIGN_NAMES_TA[mars_sign_idx]} ராசியில்)."
            )
        else:
            gender_en = (
                f"As a male native, Venus is the prime Kalatrakaraka representing your wife's charm, grace, and beauty "
                f"(placed in {SIGN_NAMES_EN[venus_sign_idx]}, {venus_dig_en}). A strong Venus promises a loving and aesthetically refined life partner."
            )
            gender_ta = (
                f"ஆண் ஜாதகத்தில் சுக்கிரன் மனைவியின் அழகு, நளினம் மற்றும் குணத்தைக் குறிக்கும் களத்திரகாரகர் "
                f"({SIGN_NAMES_TA[venus_sign_idx]} ராசியில் {venus_dig_ta}). சுக்கிர பலம் அமைவது பேரழகும் பாசமும் கொண்ட மனைவியை நல்கும்."
            )

        karakas_analysis = SpouseKarakasAnalysis(
            venus_sign=SIGN_NAMES_EN[venus_sign_idx],
            venus_sign_tamil=SIGN_NAMES_TA[venus_sign_idx],
            venus_house=venus_house_num,
            venus_dignity=venus_dig_en,
            venus_dignity_tamil=venus_dig_ta,
            venus_description_en=f"Venus governs love, beauty, elegance, and conjugal happiness ({venus_dig_en} in House {venus_house_num}).",
            venus_description_ta=f"சுக்கிரன் காதல், அழகு, சுகபோகம் மற்றும் தாம்பத்திய மகிழ்ச்சியை ஆள்கிறார் ({venus_house_num}-ஆம் வீட்டில் {venus_dig_ta}).",
            jupiter_sign=SIGN_NAMES_EN[jupiter_sign_idx],
            jupiter_sign_tamil=SIGN_NAMES_TA[jupiter_sign_idx],
            jupiter_house=jupiter_house_num,
            jupiter_dignity=jupiter_dig_en,
            jupiter_dignity_tamil=jupiter_dig_ta,
            jupiter_description_en=f"Jupiter governs moral integrity, status, scholarship, and marital longevity ({jupiter_dig_en} in House {jupiter_house_num}).",
            jupiter_description_ta=f"குரு உயர்ந்த தர்மம், கல்வி, சமூக மரியாதை மற்றும் மாங்கல்ய பலத்தை ஆள்கிறார் ({jupiter_house_num}-ஆம் வீட்டில் {jupiter_dig_ta}).",
            mars_sign=SIGN_NAMES_EN[mars_sign_idx],
            mars_sign_tamil=SIGN_NAMES_TA[mars_sign_idx],
            mars_house=mars_house_num,
            mars_dignity=mars_dig_en,
            mars_dignity_tamil=mars_dig_ta,
            mars_description_en=f"Mars governs physical energy, courage, protective instincts, and vitality ({mars_dig_en} in House {mars_house_num}).",
            mars_description_ta=f"செவ்வாய் தைரியம், பாதுகாப்பு குணம், உடலாற்றல் மற்றும் ஆண்மையை ஆள்கிறார் ({mars_house_num}-ஆம் வீட்டில் {mars_dig_ta}).",
            mars_venus_synergy_en=synergy_en,
            mars_venus_synergy_ta=synergy_ta,
            gender_specific_insight_en=gender_en,
            gender_specific_insight_ta=gender_ta,
        )

        # -----------------------------------------------------------------------
        # Step 4: Navamsa (D9) Chart Deep Dive
        # -----------------------------------------------------------------------
        d9_asc_info = calculate_navamsa_from_longitude(asc_deg)
        d9_asc_sign_idx = d9_asc_info["d9_sign_index"]
        d9_seventh_sign_idx = ((d9_asc_sign_idx + 6 - 1) % 12) + 1
        d9_seventh_sign_name = SIGN_NAMES_EN[d9_seventh_sign_idx]
        d9_seventh_sign_tamil = SIGN_NAMES_TA[d9_seventh_sign_idx]
        d9_seventh_lord = SIGN_LORDS[d9_seventh_sign_idx]
        d9_seventh_lord_tamil = PLANET_NAMES_TA.get(d9_seventh_lord, d9_seventh_lord)

        d9_occupants: List[str] = []
        for p in vedic_planets:
            p_d9 = calculate_navamsa_from_longitude(p.longitude)["d9_sign_index"]
            if p_d9 == d9_seventh_sign_idx:
                d9_occupants.append(p.name)

        if "Jupiter" in d9_occupants or "Saturn" in d9_occupants:
            d9_nature_en = "Deeply loyal, god-fearing, dutiful, and morally steadfast inner soul nature."
            d9_nature_ta = "உயர்ந்த இறையன்பு, கடமை தவறாமை, நேர்மை மற்றும் நிலையான உண்மைத்தன்மை கொண்ட ஆன்மீக சுபாவம்."
        elif "Venus" in d9_occupants or "Moon" in d9_occupants or "Mercury" in d9_occupants:
            d9_nature_en = "Romantic, joyful, aesthetically refined, loving, and intellectually youthful companion."
            d9_nature_ta = "அன்பான, மகிழ்ச்சியான, கலை நயமிக்க, கலகலப்பான மற்றும் எப்போதும் இளமையான உள்ளம் கொண்ட துணை."
        elif "Mars" in d9_occupants or "Sun" in d9_occupants:
            d9_nature_en = "Courageous, straightforward, confident, ambitious, and energetic soul nature."
            d9_nature_ta = "துணிச்சல், ஒளிவுமறைவற்ற உண்மை, தன்னம்பிக்கை மற்றும் சுறுசுறுப்பான ஆன்ம சுபாவம்."
        else:
            d9_nature_en = f"Influenced by {d9_seventh_sign_name} and ruler {d9_seventh_lord}: balanced, adaptable, and faithful partner."
            d9_nature_ta = f"{d9_seventh_sign_tamil} மற்றும் அதிபதி {d9_seventh_lord_tamil} தாக்கத்தால் சமநிலையான, விசுவாசமான துணை."

        navamsa_profile = NavamsaD9SpouseProfile(
            d9_lagna_sign=SIGN_NAMES_EN[d9_asc_sign_idx],
            d9_lagna_sign_tamil=SIGN_NAMES_TA[d9_asc_sign_idx],
            d9_seventh_sign=d9_seventh_sign_name,
            d9_seventh_sign_tamil=d9_seventh_sign_tamil,
            d9_seventh_lord=d9_seventh_lord,
            d9_seventh_lord_tamil=d9_seventh_lord_tamil,
            d9_seventh_occupants=d9_occupants,
            inner_nature_en=d9_nature_en,
            inner_nature_ta=d9_nature_ta,
            marital_bond_en=(
                f"The Navamsa 7th house in {d9_seventh_sign_name} reveals the post-marriage long-term reality: "
                f"the union matures into a stable, spiritually meaningful, and mutually enriching partnership."
            ),
            marital_bond_ta=(
                f"நவாம்சம் 7-ஆம் வீடு ({d9_seventh_sign_tamil}) திருமணத்திற்குப் பிந்தைய உண்மை நிலையை காட்டுகிறது: "
                f"காலப்போக்கில் இப்பந்தம் ஆழ்ந்த புரிதலும், ஆன்மீக பலமும் கொண்ட உறுதியான நல்வாழ்வாக மலரும்."
            ),
        )

        # -----------------------------------------------------------------------
        # Step 5: "What You Want vs What You Get" (Mind's Mirror)
        # -----------------------------------------------------------------------
        seventh_from_moon_idx = ((moon_sign_idx + 6 - 1) % 12) + 1
        seventh_from_moon_name = SIGN_NAMES_EN[seventh_from_moon_idx]
        seventh_from_moon_tamil = SIGN_NAMES_TA[seventh_from_moon_idx]

        moon_temp = SIGN_TEMPERAMENTS.get(seventh_from_moon_idx, SIGN_TEMPERAMENTS[1])

        reality_desc_en = (
            f"7th House from Lagna is {seventh_sign_name}: In the real world, you attract a partner who is "
            f"{sign_temp['temperament_en'].lower()}"
        )
        reality_desc_ta = (
            f"லக்னத்திற்கு 7-ஆம் வீடு {seventh_sign_tamil}: எதார்த்த உலகில் உங்களுக்கு அமையும் துணை "
            f"{sign_temp['temperament_ta']}"
        )

        desire_desc_en = (
            f"7th House from Moon is {seventh_from_moon_name}: Psychologically, your subconscious mind craves a partner who is "
            f"{moon_temp['temperament_en'].lower()}"
        )
        desire_desc_ta = (
            f"சந்திரனுக்கு 7-ஆம் வீடு {seventh_from_moon_tamil}: உங்கள் ஆழ்மனம் உளவியல் ரீதியாக எதிர்பார்க்கும் துணை "
            f"{moon_temp['temperament_ta']}"
        )

        if seventh_sign_idx == seventh_from_moon_idx:
            synth_en = "Magnificent Harmony: Your mental expectations and real-world reality are in perfect alignment!"
            synth_ta = "அற்புதமான ஒற்றுமை: உங்கள் மனதின் எதிர்பார்ப்பும் நிஜ வாழ்க்கை துணையின் சுபாவமும் நூறு சதவீதம் ஒத்துப்போகின்றன!"
        elif ELEMENT_BY_SIGN[seventh_sign_idx][0] == ELEMENT_BY_SIGN[seventh_from_moon_idx][0]:
            synth_en = (
                f"Elemental Harmony ({ELEMENT_BY_SIGN[seventh_sign_idx][0]}): While specific traits differ slightly, "
                f"your core values and partner's temperament share the same foundational wavelength."
            )
            synth_ta = (
                f"தத்துவ ஒற்றுமை ({ELEMENT_BY_SIGN[seventh_sign_idx][1]}): சிறிய குண வேறுபாடுகள் இருந்தாலும், "
                f"உங்கள் இருவரின் அடிப்படை சிந்தனைகளும் ஒரே அலைவரிசையில் இனிதே இணைகின்றன."
            )
        else:
            synth_en = (
                f"Complementary Polarity: You desire {seventh_from_moon_name} qualities, while destiny brings {seventh_sign_name}. "
                f"This contrast provides spiritual growth and allows both partners to complete what the other lacks."
            )
            synth_ta = (
                f"நிரப்புப் பாலம்: உங்கள் மனம் {seventh_from_moon_tamil} குணங்களை விரும்புகிறது, விதி {seventh_sign_tamil} குணங்களை வழங்குகிறது. "
                f"இந்த மாறுபட்ட குணங்கள் ஒருவருக்கொருவர் துணையாக நின்று முழுமை பெற உதவும்."
            )

        desire_vs_reality = DesireVsRealityAnalysis(
            lagna_sign=asc_sign_name,
            lagna_sign_tamil=asc_sign_tamil,
            seventh_from_lagna_sign=seventh_sign_name,
            seventh_from_lagna_sign_tamil=seventh_sign_tamil,
            reality_description_en=reality_desc_en,
            reality_description_ta=reality_desc_ta,
            moon_sign=moon_sign_name,
            moon_sign_tamil=moon_sign_tamil,
            seventh_from_moon_sign=seventh_from_moon_name,
            seventh_from_moon_sign_tamil=seventh_from_moon_tamil,
            desire_description_en=desire_desc_en,
            desire_description_ta=desire_desc_ta,
            synthesis_en=synth_en,
            synthesis_ta=synth_ta,
        )

        # -----------------------------------------------------------------------
        # Step 6: Trait Scoring
        # -----------------------------------------------------------------------
        # 1. Romance & Loving Score
        romance_score = 65
        romance_reasons_en = []
        romance_reasons_ta = []

        occupant_names = [p.planet for p in planets_in_7th]
        if "Venus" in occupant_names:
            romance_score += 20
            romance_reasons_en.append("Venus in 7th House bestows deep romance and marital charm")
            romance_reasons_ta.append("7-ஆம் பாவத்தில் சுக்கிரன் அமர்ந்து பேரன்பையும் காதலையும் நல்குகிறார்")
        if "Moon" in occupant_names:
            romance_score += 15
            romance_reasons_en.append("Moon in 7th House brings tender emotional care")
            romance_reasons_ta.append("7-ஆம் பாவத்தில் சந்திரன் அமர்ந்து கனிவான பாசத்தை ஊட்டுகிறார்")
        if "Mercury" in occupant_names:
            romance_score += 10
            romance_reasons_en.append("Mercury in 7th brings playful banter and friendly joy")
            romance_reasons_ta.append("புதன் 7-ல் நட்புணர்வும் இனிமையான நகைச்சுவையும் தருகிறார்")
        if "Venus" in d9_occupants or "Moon" in d9_occupants:
            romance_score += 10
            romance_reasons_en.append("Benefic presence in Navamsa 7th house enriches romantic warmth")
            romance_reasons_ta.append("நவாம்சம் 7-ல் சுப கிரகங்கள் அமைந்து காதலை மெருகேற்றுகின்றன")
        romance_score = min(romance_score, 98)

        # 2. Loyalty & Faithfulness Score
        loyalty_score = 70
        loyalty_reasons_en = []
        loyalty_reasons_ta = []

        if "Jupiter" in occupant_names or "Saturn" in occupant_names:
            loyalty_score += 20
            loyalty_reasons_en.append("Jupiter or Saturn in 7th House anchors exceptional moral faithfulness and duty")
            loyalty_reasons_ta.append("7-ல் குரு அல்லது சனி அமர்ந்து அசைக்க முடியாத உண்மைத்தன்மையையும் கடமையையும் தருகிறார்")
        if "Jupiter" in d9_occupants or "Saturn" in d9_occupants:
            loyalty_score += 15
            loyalty_reasons_en.append("Navamsa 7th influenced by Saturn/Jupiter ensures lifelong commitment")
            loyalty_reasons_ta.append("நவாம்சம் 7-ல் குரு/சனி செல்வாக்கு வாழ்நாள் முழுவதும் நிலைக்கும் விசுவாசத்தை உறுதி செய்கிறது")
        if jupiter_house_num == 8:
            loyalty_score += 10
            loyalty_reasons_en.append("Jupiter in 8th House (Mangalya Sthana) grants extraordinary marital longevity")
            loyalty_reasons_ta.append("மாங்கல்ய ஸ்தானமான 8-ஆம் வீட்டில் குரு அமர்ந்து தீர்க்க சுமங்கலி யோகம் மற்றும் நீண்ட ஆயுளைத் தருகிறார்")
        if seventh_sign_idx in (2, 5, 8, 11):  # Fixed signs
            loyalty_score += 8
            loyalty_reasons_en.append("Fixed sign on 7th cusp indicates rock-solid constancy")
            loyalty_reasons_ta.append("7-ஆம் பாவத்தில் ஸ்திர ராசி அமைந்து மாறாத பிணைப்பை உறுதி செய்கிறது")
        loyalty_score = min(loyalty_score, 99)

        # 3. Intelligence & Education Score
        intellect_score = 65
        intellect_reasons_en = []
        intellect_reasons_ta = []

        if "Sun" in occupant_names and "Mercury" in occupant_names:
            intellect_score += 25
            intellect_reasons_en.append("Budhaditya Yoga in 7th House gives an exceptionally sharp, educated spouse from a good family")
            intellect_reasons_ta.append("7-ஆம் பாவத்தில் புதாதித்ய யோகம்: உயர்கல்வி, நுண்ணறிவு மற்றும் நற்குடும்ப பின்னணி கொண்ட துணை")
        elif "Mercury" in occupant_names or "Jupiter" in occupant_names:
            intellect_score += 18
            intellect_reasons_en.append("Jupiter / Mercury in 7th House endows brilliant intellect and scholarly wisdom")
            intellect_reasons_ta.append("7-ல் குரு அல்லது புதன் அமைந்து கூரிய மதிநுட்பமும் கல்வி அறிவும் அளிக்கின்றனர்")
        if "Rahu" in occupant_names or "Ketu" in occupant_names:
            intellect_score += 12
            intellect_reasons_en.append("Shadow planet in 7th brings modern technical acumen, computing skills or subtle wisdom")
            intellect_reasons_ta.append("7-ல் நிழல் கிரகம்: நவீன தொழில்நுட்பம், கணிதம் அல்லது நுண்ணிய ஆராய்ச்சித் திறன்")
        if seventh_sign_idx in (3, 6, 9, 11):
            intellect_score += 10
            intellect_reasons_en.append("Intellectual zodiac sign on 7th cusp")
            intellect_reasons_ta.append("7-ஆம் பாவகத்தில் அறிவார்ந்த ராசி அமைவு")
        intellect_score = min(intellect_score, 98)

        # 4. Physical Charm & Aura
        charm_score = 65
        charm_reasons_en = []
        charm_reasons_ta = []

        if "Venus" in occupant_names:
            charm_score += 25
            charm_reasons_en.append("Venus in 7th is the classical signature of extraordinary physical beauty and grace")
            charm_reasons_ta.append("7-ல் சுக்கிரன் அமைவது பேரழகும் வசீகரமும் கொண்ட வாழ்க்கைத்துணையை வழங்கும் யோகம்")
        if "Mercury" in occupant_names:
            charm_score += 15
            charm_reasons_en.append("Mercury in 7th grants a youthful, radiating, and playful countenance")
            charm_reasons_ta.append("7-ல் புதன் எப்போதும் இளமை ததும்பும் பிரகாசமான முக வசீகரத்தை நல்குகிறார்")
        if "Moon" in occupant_names:
            charm_score += 12
            charm_reasons_en.append("Moon in 7th gives a gentle, glowing, and attractive face")
            charm_reasons_ta.append("7-ல் சந்திரன் களங்கமற்ற அழகிய நிலவு போன்ற முகப்பொலிவை தருகிறார்")
        if venus_dig_en in ("Exalted", "Own Sign"):
            charm_score += 10
            charm_reasons_en.append(f"Venus is {venus_dig_en}, radiating refined aesthetic elegance")
            charm_reasons_ta.append(f"சுக்கிரன் {venus_dig_ta} பலம் பெற்று வசீகரத்தை உயர்த்துகிறார்")
        charm_score = min(charm_score, 97)

        trait_scores = SpouseTraitScores(
            romantic_loving_score=romance_score,
            romantic_loving_analysis_en=". ".join(romance_reasons_en) if romance_reasons_en else "Balanced affection with steady domestic warmth.",
            romantic_loving_analysis_ta=". ".join(romance_reasons_ta) if romance_reasons_ta else "அமைதியான குடும்பப் பாசமும் நிலையான அன்பும்.",
            loyalty_faithfulness_score=loyalty_score,
            loyalty_faithfulness_analysis_en=". ".join(loyalty_reasons_en) if loyalty_reasons_en else "Dependable, practical commitment to family duty.",
            loyalty_faithfulness_analysis_ta=". ".join(loyalty_reasons_ta) if loyalty_reasons_ta else "குடும்பக் கடமைகளில் நம்பகமான விசுவாசப் பிணைப்பு.",
            intelligence_education_score=intellect_score,
            intelligence_education_analysis_en=". ".join(intellect_reasons_en) if intellect_reasons_en else "Sound practical judgment and sensible decision-making.",
            intelligence_education_analysis_ta=". ".join(intellect_reasons_ta) if intellect_reasons_ta else "நடைமுறை வாழ்க்கைக்கு ஏற்ற விவேகமும் புத்திசாலித்தனமும்.",
            physical_charm_score=charm_score,
            physical_charm_analysis_en=". ".join(charm_reasons_en) if charm_reasons_en else "Pleasing, dignified, and respectable presence.",
            physical_charm_analysis_ta=". ".join(charm_reasons_ta) if charm_reasons_ta else "கண்ணியமான, மரியாதைக்குரிய அழகிய தோற்றம்.",
        )

        # -----------------------------------------------------------------------
        # Step 7: Astrological Remedies & Lifestyle Guidance
        # -----------------------------------------------------------------------
        # Recommended Gemstone & Fasting Day based on 7th Lord / Venus
        gemstones_by_planet = {
            "Venus": ("White Zircon (or Diamond)", "வெள்ளை ஜிர்கான் (அல்லது வைரம்)", "Friday", "வெள்ளிக்கிழமை", ["White", "Cream", "Silver", "Pastel Pink"], ["வெள்ளை", "கிரீம்", "வெள்ளி", "இளம் இளஞ்சிவப்பு"]),
            "Jupiter": ("Yellow Sapphire (or Topaz)", "புஷ்பராகம் (அல்லது மஞ்சள் தோபாஸ்)", "Thursday", "வியாழக்கிழமை", ["Yellow", "Golden Yellow", "Saffron"], ["மஞ்சள்", "தங்க நிறம்", "காவி நிறம்"]),
            "Saturn": ("Blue Sapphire (or Amethyst / Blue Topaz)", "நீலக்கல் (அல்லது அமேதிஸ்ட்)", "Saturday", "சனிக்கிழமை", ["Navy Blue", "Black", "Charcoal Grey"], ["நீலம்", "கருநீலம்", "சாம்பல்"]),
            "Mercury": ("Emerald (or Green Tourmaline)", "மரகதம் (அல்லது பச்சை டூர்மலைன்)", "Wednesday", "புதன்கிழமை", ["Emerald Green", "Light Green"], ["பச்சை", "இளம் பச்சை நிறம்"]),
            "Mars": ("Red Coral", "செவ்பவளம்", "Tuesday", "செவ்வாய்க்கிழமை", ["Red", "Coral", "Maroon"], ["சிவப்பு", "பவள நிறம்", "மெரூன்"]),
            "Sun": ("Ruby (or Red Garnet)", "மாணிக்கம் (அல்லது கார்னட்)", "Sunday", "ஞாயிற்றுக்கிழமை", ["Orange", "Copper", "Golden Red"], ["ஆரஞ்சு", "தாமிர நிறம்", "தங்க சிவப்பு"]),
            "Moon": ("Natural Pearl (or Moonstone)", "முத்து (அல்லது சந்திரகாந்தக் கல்)", "Monday", "திங்கட்கிழமை", ["Milky White", "Pearl Silver"], ["முத்து வெள்ளை", "வெள்ளி நிறம்"]),
        }

        # Primary ruling planet for remedies is 7th Lord, or Venus if 7th Lord is afflicted
        remedy_planet = seventh_lord_name if seventh_lord_name in gemstones_by_planet else "Venus"
        gem_en, gem_ta, fast_en, fast_ta, colors_en, colors_ta = gemstones_by_planet[remedy_planet]

        remedies = SpouseRemedies(
            primary_gemstone_en=f"{gem_en} (Strengthens 7th House Lord {seventh_lord_name})",
            primary_gemstone_ta=f"{gem_ta} (7-ஆம் அதிபதி {seventh_lord_tamil} பலம் பெற)",
            fasting_day_en=f"Fast or observe sattvic diet on {fast_en}s to invoke grace for early and harmonious marriage.",
            fasting_day_ta=f"{fast_ta}தோறும் விரதம் அல்லது சாத்வீக உணவு மேற்கொள்வது திருமண தடைகளை நீக்கி நல்ல துணையை ஈர்க்கும்.",
            auspicious_colors_en=colors_en,
            auspicious_colors_ta=colors_ta,
            mantra_en="Om Draam Dreem Droum Sah Shukraya Namaha (or worship of Goddess Mahalakshmi / Lord Venkateswara)",
            mantra_ta="ஓம் த்ராம் த்ரீம் த்ரௌம் ச: சுக்ராய நம: (அல்லது ஸ்ரீ மகாலட்சுமி / திருப்பதி வேங்கடேச பெருமாள் வழிபாடு)",
            practical_advice_en=(
                f"Nurture mutual respect and clarity in speech. Since your 7th house lord carries {lord_element_en} temperament, "
                f"encourage open dialogue and appreciate your partner's natural inclinations without imposing rigid expectations."
            ),
            practical_advice_ta=(
                f"பரஸ்பர மரியாதையையும் வெளிப்படைத்தன்மையையும் பேணுங்கள். உங்கள் 7-ஆம் அதிபதி {lord_element_ta} கொண்டுள்ளதால், "
                f"துணையின் இயற்கை சுபாவத்தை மதித்து அன்புடன் வழிநடத்துங்கள்."
            ),
        )

        # -----------------------------------------------------------------------
        # Summary Headlines
        # -----------------------------------------------------------------------
        summary_hl_en = f"Life Partner Profile: {seventh_sign_name} Archetype with {lord_element_en} Elemental Influence"
        summary_hl_ta = f"வாழ்க்கைத் துணை சுயவிவரம்: {seventh_sign_tamil} ராசி பண்புகள் & {lord_element_ta} ஆளுமை"

        summary_body_en = (
            f"Your 7th house (Kalatra Bhava) is in {seventh_sign_name}, ruled by {seventh_lord_name} "
            f"placed in the {lord_house_num}th house in {seventh_lord_analysis.sign} ({lord_element_en} element). "
            f"Destiny indicates a partner who is {seventh_sign_analysis.temperament_en.lower()} "
            f"With Trait Scores of {romance_score}% Romance, {loyalty_score}% Loyalty, and {intellect_score}% Intellect, "
            f"your conjugal bond carries strong classical promises of stability and shared growth."
        )
        summary_body_ta = (
            f"உங்கள் 7-ஆம் பாவம் (களத்திர ஸ்தானம்) {seventh_sign_tamil} ராசியில் அமைந்து, அதன் அதிபதியான {seventh_lord_tamil} "
            f"{lord_house_num}-ஆம் இடத்தில் {seventh_lord_analysis.sign_tamil} ராசியில் ({lord_element_ta}) அமர்ந்துள்ளார். "
            f"விதி உங்களுக்கு {seventh_sign_analysis.temperament_ta} உடைய நற்றுணையை நல்குகிறது. "
            f"{romance_score}% காதல், {loyalty_score}% உண்மைத்தன்மை மற்றும் {intellect_score}% அறிவுத்திறன் மதிப்பெண்களுடன், "
            f"உங்கள் இல்லற வாழ்க்கை நீண்டகால ஸ்திரத்தன்மையும் மகிழ்ச்சியும் கொண்டதாக அமையும்."
        )

        return SpousePredictionResponse(
            native_gender=gender,
            ascendant_sign=asc_sign_name,
            ascendant_sign_tamil=asc_sign_tamil,
            moon_sign=moon_sign_name,
            moon_sign_tamil=moon_sign_tamil,
            seventh_sign=seventh_sign_analysis,
            seventh_lord=seventh_lord_analysis,
            planets_in_seventh=planets_in_7th,
            aspecting_planets=aspecting_planets,
            desire_vs_reality=desire_vs_reality,
            karakas=karakas_analysis,
            navamsa_d9=navamsa_profile,
            trait_scores=trait_scores,
            remedies=remedies,
            summary_headline_en=summary_hl_en,
            summary_headline_ta=summary_hl_ta,
            summary_text_en=summary_body_en,
            summary_text_ta=summary_body_ta,
            metadata=CalculationMetadata(
                engine="XALEN 0.6.0 (Rust)",
                birth_utc_iso=utc_dt.isoformat(),
                julian_day_ut1=birth_jd,
                local_timezone=tz_name,
                utc_offset_hours=offset_hours,
                coordinates={"latitude": birth.latitude, "longitude": birth.longitude},
                ayanamsa_id=0,
                ayanamsa_name="Lahiri",
                ayanamsa_deg=0.0,
                house_system_id=0,
                house_system_name="Whole Sign (Rashi Bhava)",
                calculation_frame="Geocentric Sidereal",
                notes=["Classical Parashari and Bhrigu Nandi Nadi 4-step life partner assessment."],
            ),
        )
