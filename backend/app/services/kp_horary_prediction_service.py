"""Instant KP Horary / Prashna (1-249) Automated Event Predictor Service.

Calculates the horary chart fixed at the sub-lord division midpoint for seed numbers 1-249,
resolves query topic to relevant primary cusps and supporting/denying houses,
evaluates Cuspal Sub-Lord (CSL) connections, verifies Ruling Planets (RP),
computes outcome verdict (YES / DELAYED / NO), determines timing of fructification
(Dasha window + exact Moon transit window), and formats explanations in English and Tamil.
"""

from __future__ import annotations
import math
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe
import xalen
from app.schemas.kp import (
    HoraryKpRequest,
    HoraryKpResponse,
    HoraryDivisionDetail,
    PlanetaryKpPosition,
    KpCuspDetail,
)
from app.schemas.kp_horary_prediction import (
    InstantHoraryPredictionRequest,
    InstantHoraryPredictionResponse,
    HoraryTopicInfo,
    OutcomeVerdict,
    TimingWindow,
    AstrologicalExplanation,
)
from app.services.kp_service import calculate_horary_chart
from app.services.kp_engine.horary import kp_divisions
from app.services.kp_engine.vedic import point_info, star_name, sign_name
from app.services.timezone_utils import resolve_birth_datetime


# Planet Names in English and Tamil
PLANET_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
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

# Nakshatras in English and Tamil
STAR_NAMES_TA: Dict[str, str] = {
    "Ashwini": "அசுவினி",
    "Bharani": "பரணி",
    "Krittika": "கிருத்திகை",
    "Rohini": "ரோகிணி",
    "Mrigashira": "மிருகசீரிஷம்",
    "Ardra": "திருவாதிரை",
    "Punarvasu": "புனர்பூசம்",
    "Pushya": "பூசம்",
    "Ashlesha": "ஆயில்யம்",
    "Magha": "மகம்",
    "Purva Phalguni": "பூரம்",
    "Uttara Phalguni": "உத்திரம்",
    "Hasta": "ஹஸ்தம்",
    "Chitra": "சித்திரை",
    "Swati": "சுவாதி",
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

# 27 Nakshatras and their Vimshottari Lords
NAKSHATRA_LORDS: List[Tuple[str, str, float, float]] = [
    ("Ashwini", "Ketu", 0.0, 13.333333),
    ("Bharani", "Venus", 13.333333, 26.666667),
    ("Krittika", "Sun", 26.666667, 40.0),
    ("Rohini", "Moon", 40.0, 53.333333),
    ("Mrigashira", "Mars", 53.333333, 66.666667),
    ("Ardra", "Rahu", 66.666667, 80.0),
    ("Punarvasu", "Jupiter", 80.0, 93.333333),
    ("Pushya", "Saturn", 93.333333, 106.666667),
    ("Ashlesha", "Mercury", 106.666667, 120.0),
    ("Magha", "Ketu", 120.0, 133.333333),
    ("Purva Phalguni", "Venus", 133.333333, 146.666667),
    ("Uttara Phalguni", "Sun", 146.666667, 160.0),
    ("Hasta", "Moon", 160.0, 173.333333),
    ("Chitra", "Mars", 173.333333, 186.666667),
    ("Swati", "Rahu", 186.666667, 200.0),
    ("Vishakha", "Jupiter", 200.0, 213.333333),
    ("Anuradha", "Saturn", 213.333333, 226.666667),
    ("Jyeshtha", "Mercury", 226.666667, 240.0),
    ("Mula", "Ketu", 240.0, 253.333333),
    ("Purva Ashadha", "Venus", 253.333333, 266.666667),
    ("Uttara Ashadha", "Sun", 266.666667, 280.0),
    ("Shravana", "Moon", 280.0, 293.333333),
    ("Dhanishta", "Mars", 293.333333, 306.666667),
    ("Shatabhisha", "Rahu", 306.666667, 320.0),
    ("Purva Bhadrapada", "Jupiter", 320.0, 333.333333),
    ("Uttara Bhadrapada", "Saturn", 333.333333, 346.666667),
    ("Revati", "Mercury", 346.666667, 360.0),
]

# Standard Topic Definitions
HORARY_TOPICS: Dict[str, Dict[str, Any]] = {
    "visa": {
        "id": "visa",
        "name_en": "Visa & Foreign Travel",
        "name_ta": "விசா & வெளிநாட்டுப் பயணம்",
        "sample_query_en": "Will I get this visa?",
        "sample_query_ta": "விசா அனுமதி கிடைக்குமா?",
        "category": "Travel",
        "primary_cusp": 12,
        "primary_cusp_desc_en": "12th Cusp (Foreign Residence & Long Distant Land)",
        "primary_cusp_desc_ta": "12-ஆம் பாவகம் (வெளிநாட்டு வாசம், தூரப் பயணம் & விசா ஒப்புதல்)",
        "supporting_houses": [3, 9, 12],
        "denying_houses": [2, 11],
        "supporting_desc_en": "3 (leaving home), 9 (long journey & visa), 12 (stay on foreign soil)",
        "supporting_desc_ta": "3 (பிரயாணம்), 9 (நீண்ட தூரப் பயணம்), 12 (அயல்நாட்டு வாசம்)",
        "denying_desc_en": "2 & 11 (retention in native place / domestic return)",
        "denying_desc_ta": "2 & 11 (சொந்த ஊரிலேயே தங்குதல்)",
        "icon": "Plane",
        "keywords": ["visa", "foreign", "passport", "travel", "overseas", "immigration", "embassy", "abroad", "விசா", "வெளிநாடு"],
    },
    "job": {
        "id": "job",
        "name_en": "Job Interview & Employment",
        "name_ta": "வேலை நேர்காணல் & உத்தியோகம்",
        "sample_query_en": "Will my job interview succeed?",
        "sample_query_ta": "வேலை நேர்காணலில் வெற்றி கிடைக்குமா?",
        "category": "Career",
        "primary_cusp": 6,
        "primary_cusp_desc_en": "6th Cusp (Service, Employment & Competitive Success)",
        "primary_cusp_desc_ta": "6-ஆம் பாவகம் (உத்தியோகம், நேர்காணல் & போட்டி வெற்றி)",
        "supporting_houses": [2, 6, 10, 11],
        "denying_houses": [1, 5, 9],
        "supporting_desc_en": "2 (regular income), 6 (job selection), 10 (profession/position), 11 (gain/fulfillment)",
        "supporting_desc_ta": "2 (பண வரவு), 6 (வேலை வாய்ப்பு), 10 (தொழில் பதவி), 11 (லாபம்/நிறைவு)",
        "denying_desc_en": "1, 5, 9 (5 is 12th to 6th [loss of opportunity], 9 is 12th to 10th)",
        "denying_desc_ta": "1, 5, 9 (5-ஆம் பாவம் 6-க்கு விரயம் / வாய்ப்பு நழுவுதல்)",
        "icon": "Briefcase",
        "keywords": ["job", "interview", "employment", "hire", "offer", "career", "placement", "salary", "வேலை", "நேர்காணல்", "உத்தியோகம்"],
    },
    "court_case": {
        "id": "court_case",
        "name_en": "Court Case & Legal Dispute Settlement",
        "name_ta": "நீதிமன்ற வழக்கு & சட்ட தீர்வு",
        "sample_query_en": "Will this court case settle in my favor?",
        "sample_query_ta": "நீதிமன்ற வழக்கு எனக்கு சாதகமாக தீருமா?",
        "category": "Legal",
        "primary_cusp": 6,
        "primary_cusp_desc_en": "6th Cusp (Defeating Opponents, Litigation & Legal Verdict)",
        "primary_cusp_desc_ta": "6-ஆம் பாவகம் (எதிரிகளை வெல்லுதல், வழக்கு வெற்றி & சாதகமான தீர்ப்பு)",
        "supporting_houses": [1, 6, 11],
        "denying_houses": [5, 8, 12],
        "supporting_desc_en": "1 (querent success), 6 (opponent defeat [12th to 7th]), 11 (winning final verdict)",
        "supporting_desc_ta": "1 (கேட்பவர் வெற்றி), 6 (எதிரிக்கு விரயம்), 11 (நீதிமன்ற வெற்றி)",
        "denying_desc_en": "5, 8, 12 (5 is gain to opponent [11th to 7th], 8 is distress/penalty, 12 is loss)",
        "denying_desc_ta": "5, 8, 12 (5 எதிரியின் லாபம், 8 அபராதம், 12 தோல்வி)",
        "icon": "Scale",
        "keywords": ["court", "case", "lawsuit", "legal", "dispute", "litigation", "settle", "trial", "judge", "advocate", "வழக்கு", "நீதிமன்றம்"],
    },
    "marriage": {
        "id": "marriage",
        "name_en": "Marriage & Matrimonial Alliance",
        "name_ta": "திருமண உறுதி & வரன் அமைதல்",
        "sample_query_en": "Will this marriage proposal finalize?",
        "sample_query_ta": "இந்த வரன் திருமணமாக கைகூடுமா?",
        "category": "Relationship",
        "primary_cusp": 7,
        "primary_cusp_desc_en": "7th Cusp (Spouse, Legal Partnership & Marriage)",
        "primary_cusp_desc_ta": "7-ஆம் பாவகம் (வாழ்க்கைத் துணை & திருமண பந்தம்)",
        "supporting_houses": [2, 7, 11],
        "denying_houses": [1, 6, 10],
        "supporting_desc_en": "2 (family growth), 7 (matrimonial partner), 11 (fulfillment of desires)",
        "supporting_desc_ta": "2 (குடும்ப சேர்க்கை), 7 (வாழ்க்கைத் துணை), 11 (ஆசை நிறைவேறுதல்)",
        "denying_desc_en": "1, 6, 10 (6 is 12th to 7th [separation/denial], 1 & 10 oppose family)",
        "denying_desc_ta": "1, 6, 10 (6-ஆம் பாவம் பிரிவினை மற்றும் மறுப்பு)",
        "icon": "Heart",
        "keywords": ["marriage", "wedding", "proposal", "matrimony", "alliance", "bride", "groom", "திருமணம்", "வரன்", "மணமகன்"],
    },
    "property": {
        "id": "property",
        "name_en": "Property & Real Estate Purchase",
        "name_ta": "சொத்து & வீடு வாங்குதல்",
        "sample_query_en": "Will I be able to purchase this property?",
        "sample_query_ta": "இந்த சொத்தை / வீட்டை வாங்க முடியுமா?",
        "category": "Property",
        "primary_cusp": 4,
        "primary_cusp_desc_en": "4th Cusp (Fixed Assets, Land & Residential Property)",
        "primary_cusp_desc_ta": "4-ஆம் பாவகம் (நிலம், வீடு & அசையா சொத்துக்கள்)",
        "supporting_houses": [4, 11, 12],
        "denying_houses": [3, 10],
        "supporting_desc_en": "4 (property asset), 11 (gain/possession), 12 (capital investment for acquisition)",
        "supporting_desc_ta": "4 (சொத்து சேர்க்கை), 11 (கைப்பற்றுதல்), 12 (முதலீடு)",
        "denying_desc_en": "3 & 10 (3 is 12th to 4th [loss of deal], 10 denies asset gain)",
        "denying_desc_ta": "3 & 10 (3-ஆம் பாவம் சொத்து கைநழுவுதல்)",
        "icon": "Home",
        "keywords": ["property", "house", "flat", "land", "plot", "real estate", "apartment", "சொத்து", "வீடு", "மனை"],
    },
    "childbirth": {
        "id": "childbirth",
        "name_en": "Childbirth & Progeny",
        "name_ta": "குழந்தைப் பேறு & புத்திர பாக்கியம்",
        "sample_query_en": "Will we be blessed with a child?",
        "sample_query_ta": "புத்திர பாக்கியம் கைகூடுமா?",
        "category": "Family",
        "primary_cusp": 5,
        "primary_cusp_desc_en": "5th Cusp (Progeny, Conception & Childbirth)",
        "primary_cusp_desc_ta": "5-ஆம் பாவகம் (குழந்தைப் பேறு, கருவுறுதல் & சந்ததி பாக்கியம்)",
        "supporting_houses": [2, 5, 11],
        "denying_houses": [1, 4, 10],
        "supporting_desc_en": "2 (expansion of family), 5 (birth of child), 11 (realization of wish)",
        "supporting_desc_ta": "2 (குடும்ப விரிவாக்கம்), 5 (குழந்தைப் பேறு), 11 (நிறைவேறிய ஆசை)",
        "denying_desc_en": "1, 4, 10 (4 is 12th to 5th [impediment to conception])",
        "denying_desc_ta": "1, 4, 10 (4-ஆம் பாவம் குழந்தைப் பேற்றிற்கு விரயம்)",
        "icon": "Baby",
        "keywords": ["child", "baby", "conception", "pregnancy", "progeny", "குழந்தை", "புத்திர", "கருவுறுதல்"],
    },
    "financial_gain": {
        "id": "financial_gain",
        "name_en": "Financial Gain & Wealth Inflow",
        "name_ta": "பண வரவு & நிதி ஆதாயம்",
        "sample_query_en": "Will I receive money / financial gain?",
        "sample_query_ta": "எதிர்பார்த்த பணம் கைக்கு வருமா?",
        "category": "Finance",
        "primary_cusp": 11,
        "primary_cusp_desc_en": "11th Cusp (Profits, Cash Flow & Financial Fulfillment)",
        "primary_cusp_desc_ta": "11-ஆம் பாவகம் (லாபம், பண வரவு & நிதி வெற்றி)",
        "supporting_houses": [2, 6, 11],
        "denying_houses": [5, 8, 12],
        "supporting_desc_en": "2 (liquid cash), 6 (recovery of funds), 11 (lucrative gains)",
        "supporting_desc_ta": "2 (தனம்), 6 (வரவேண்டிய பணம் வருதல்), 11 (பண லாபம்)",
        "denying_desc_en": "5, 8, 12 (8 is financial blockage, 12 is expenditure)",
        "denying_desc_ta": "5, 8, 12 (8 முடக்கம், 12 விரயம்)",
        "icon": "Coins",
        "keywords": ["money", "gain", "wealth", "profit", "funds", "cash", "finance", "payment", "பணம்", "லாபம்", "தனம்"],
    },
    "recovery": {
        "id": "recovery",
        "name_en": "Recovery from Illness & Health Restoration",
        "name_ta": "உடல் நலம் & நோய் குணமாகுதல்",
        "sample_query_en": "Will the illness be cured quickly?",
        "sample_query_ta": "நோய் விரைவில் குணமாகுமா?",
        "category": "Health",
        "primary_cusp": 11,
        "primary_cusp_desc_en": "11th Cusp (Cure of Disease [12th to 12th] & Vitality Recovery)",
        "primary_cusp_desc_ta": "11-ஆம் பாவகம் (நோய் நிவாரணம், பூரண குணம் & ஆரோக்கியம்)",
        "supporting_houses": [1, 5, 11],
        "denying_houses": [6, 8, 12],
        "supporting_desc_en": "1 (robust vitality), 5 (healing [12th to 6th]), 11 (total cure)",
        "supporting_desc_ta": "1 (ஆயுள் பலம்), 5 (நோய் நீங்குதல்), 11 (பூரண ஆரோக்கியம்)",
        "denying_desc_en": "6, 8, 12 (6 is disease persistence, 8 is complications, 12 is hospital stay)",
        "denying_desc_ta": "6, 8, 12 (6 நோய் தொடர்தல், 8 அவதி, 12 மருத்துவமனை வாசம்)",
        "icon": "Activity",
        "keywords": ["health", "cure", "recovery", "disease", "illness", "hospital", "patient", "sick", "நோய்", "உடல் நலம்", "குணம்"],
    },
    "higher_education": {
        "id": "higher_education",
        "name_en": "Higher Education & University Admission",
        "name_ta": "உயர் கல்வி & பல்கலைக்கழக சேர்க்கை",
        "sample_query_en": "Will I secure university admission?",
        "sample_query_ta": "கல்லூரி / பல்கலைக்கழக சேர்க்கை கிடைக்குமா?",
        "category": "Education",
        "primary_cusp": 9,
        "primary_cusp_desc_en": "9th Cusp (Higher Academics, Research & University Degrees)",
        "primary_cusp_desc_ta": "9-ஆம் பாவகம் (உயர் கல்வி, பல்கலைக்கழக பட்டம் & ஆராய்ச்சி)",
        "supporting_houses": [4, 9, 11],
        "denying_houses": [3, 8],
        "supporting_desc_en": "4 (schooling/basic degrees), 9 (higher university studies), 11 (admission success)",
        "supporting_desc_ta": "4 (அடிப்படை கல்வி), 9 (உயர் கல்வி), 11 (சேர்க்கை வெற்றி)",
        "denying_desc_en": "3 & 8 (3 is break in study, 8 is academic obstacle)",
        "denying_desc_ta": "3 & 8 (3 கல்வி தடை, 8 இழுபறி)",
        "icon": "GraduationCap",
        "keywords": ["college", "university", "admission", "study", "education", "degree", "masters", "கல்லூரி", "கல்வி", "படிப்பு"],
    },
    "competitive_exam": {
        "id": "competitive_exam",
        "name_en": "Competitive Exam & Selection",
        "name_ta": "போட்டித் தேர்வு வெற்றி",
        "sample_query_en": "Will I pass this competitive exam?",
        "sample_query_ta": "போட்டித் தேர்வில் தேர்ச்சி பெறுவேனா?",
        "category": "Education",
        "primary_cusp": 6,
        "primary_cusp_desc_en": "6th Cusp (Competitive Screenings, Entrance Exams & Outranking Competitors)",
        "primary_cusp_desc_ta": "6-ஆம் பாவகம் (போட்டித் தேர்வு, தரவரிசை தேர்ச்சி & வெற்றி)",
        "supporting_houses": [6, 10, 11],
        "denying_houses": [5, 8, 12],
        "supporting_desc_en": "6 (competitive victory), 10 (merit rank), 11 (qualification)",
        "supporting_desc_ta": "6 (போட்டியில் வெல்லுதல்), 10 (தகுதிப் பட்டியல்), 11 (வெற்றி)",
        "denying_desc_en": "5, 8, 12 (5 is 12th to 6th [failure to qualify], 12 is rejection)",
        "denying_desc_ta": "5, 8, 12 (5 தேர்ச்சி பெறாமை, 12 தோல்வி)",
        "icon": "Award",
        "keywords": ["exam", "test", "competitive", "screening", "upsc", "neet", "entrance", "தேர்வு", "போட்டி"],
    },
    "business": {
        "id": "business",
        "name_en": "Business Start & Commercial Venture",
        "name_ta": "புதிய தொழில் துவக்கம் & வர்த்தகம்",
        "sample_query_en": "Will starting this business be profitable?",
        "sample_query_ta": "புதிய தொழில் துவங்கினால் லாபம் தருமா?",
        "category": "Career",
        "primary_cusp": 7,
        "primary_cusp_desc_en": "7th Cusp (Independent Business, Clients & Commercial Trade)",
        "primary_cusp_desc_ta": "7-ஆம் பாவகம் (சொந்த தொழில், வாடிக்கையாளர்கள் & வர்த்தகம்)",
        "supporting_houses": [2, 7, 10, 11],
        "denying_houses": [1, 5, 9],
        "supporting_desc_en": "2 (revenue), 7 (clients), 10 (commercial establishment), 11 (lucrative profits)",
        "supporting_desc_ta": "2 (பண வரவு), 7 (வாடிக்கையாளர்கள்), 10 (வர்த்தகம்), 11 (லாபம்)",
        "denying_desc_en": "1, 5, 9 (lack of commercial momentum)",
        "denying_desc_ta": "1, 5, 9 (வணிக மந்தநிலை)",
        "icon": "TrendingUp",
        "keywords": ["business", "trade", "enterprise", "venture", "startup", "partnership", "commerce", "தொழில்", "வர்த்தகம்"],
    },
    "lost_article": {
        "id": "lost_article",
        "name_en": "Recovery of Lost Article / Missing Object",
        "name_ta": "தொலைந்த பொருள் கிடைக்குமா?",
        "sample_query_en": "Will I recover the missing item?",
        "sample_query_ta": "காணாமல் போன பொருள் மீண்டும் கிடைக்குமா?",
        "category": "General",
        "primary_cusp": 2,
        "primary_cusp_desc_en": "2nd Cusp (Possessions, Valuables & Movable Wealth)",
        "primary_cusp_desc_ta": "2-ஆம் பாவகம் (தனிநபர் உடமைகள், ஆபரணங்கள் & பொருள்கள்)",
        "supporting_houses": [2, 6, 11],
        "denying_houses": [8, 12],
        "supporting_desc_en": "2 (recovery into possession), 6 (retrieval from misplacement), 11 (reunion with object)",
        "supporting_desc_ta": "2 (மீண்டும் கைக்கு வருதல்), 6 (கண்டுபிடித்தல்), 11 (பொருள் கிடைத்தல்)",
        "denying_desc_en": "8 & 12 (8 is irreversible loss/theft, 12 is complete disappearance)",
        "denying_desc_ta": "8 & 12 (பொருள் நிரந்தரமாக தொலைந்து போதல்)",
        "icon": "Search",
        "keywords": ["lost", "missing", "theft", "stolen", "item", "article", "gold", "jewel", "money", "தொலைந்த பொருள்", "காணாமல்"],
    },
}


def get_all_topics() -> List[HoraryTopicInfo]:
    """Returns all supported standard horary prediction topics."""
    result: List[HoraryTopicInfo] = []
    for topic_id, data in HORARY_TOPICS.items():
        result.append(
            HoraryTopicInfo(
                id=data["id"],
                name_en=data["name_en"],
                name_ta=data["name_ta"],
                sample_query_en=data["sample_query_en"],
                sample_query_ta=data["sample_query_ta"],
                category=data["category"],
                primary_cusp=data["primary_cusp"],
                supporting_houses=data["supporting_houses"],
                denying_houses=data["denying_houses"],
                icon=data.get("icon"),
            )
        )
    return result


def resolve_topic(topic_str: str, custom_text: Optional[str] = None) -> Dict[str, Any]:
    """Resolves topic identifier or freeform text to a valid topic configuration."""
    clean_topic = topic_str.strip().lower()
    if clean_topic in HORARY_TOPICS:
        return HORARY_TOPICS[clean_topic]

    # Check keywords in topic_str
    for key, data in HORARY_TOPICS.items():
        for kw in data["keywords"]:
            if kw in clean_topic:
                return data

    # Check custom_text if provided
    if custom_text:
        clean_text = custom_text.strip().lower()
        for key, data in HORARY_TOPICS.items():
            for kw in data["keywords"]:
                if kw in clean_text:
                    return data

    # Default fallback: Job / Interview (most common)
    return HORARY_TOPICS["job"]


def calculate_instant_horary_prediction(
    request: InstantHoraryPredictionRequest,
) -> InstantHoraryPredictionResponse:
    """Executes the full KP Horary prediction pipeline:
    1. Fix Horary Ascendant at division midpoint (1-249).
    2. Compute Placidus cusps, planets at question moment, and 4-tier significators.
    3. Evaluate primary Cusp Sub-Lord (CSL) against supporting & denying houses.
    4. Compute Ruling Planets (RP) and cross-verify with fruitful significators.
    5. Determine Outcome Verdict (YES / DELAYED / NO).
    6. Derive Timing of Fructification (Dasha window + exact Moon transit window).
    7. Generate dual-language explanations in plain English and Tamil.
    """
    # 1. Resolve date, time, and timezone
    now_dt = datetime.now(ZoneInfo(request.timezone))
    q_date_str = request.question_date or now_dt.strftime("%Y-%m-%d")
    q_time_str = request.question_time or now_dt.strftime("%H:%M:%S")

    # Parse date and time objects
    q_date = date.fromisoformat(q_date_str)
    t_parts = [int(p) for p in q_time_str.split(":")[:3]]
    q_time = time(*t_parts)

    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(
        q_date, q_time, request.timezone
    )

    # 2. Compute Horary Chart snapshot
    horary_kp_req = HoraryKpRequest(
        horary_number=request.horary_number,
        question_text=request.question_text or f"Horary Prashna #{request.horary_number}",
        question_date=q_date,
        question_time=q_time,
        timezone=request.timezone,
        latitude=request.latitude,
        longitude=request.longitude,
        location_name=request.location_name or "Chennai, India",
        ayanamsa=request.ayanamsa,
        house_system=2,  # Placidus
    )
    chart_res: HoraryKpResponse = calculate_horary_chart(horary_kp_req)

    # 3. Resolve Topic & Primary Cusp
    topic_data = resolve_topic(request.question_topic, request.question_text)
    primary_cusp_num = int(topic_data["primary_cusp"])
    supporting_houses = topic_data["supporting_houses"]
    denying_houses = topic_data["denying_houses"]

    # 4. Extract Primary Cusp and CSL Details
    cuspal_analysis = chart_res.cuspal_analysis
    primary_cusp_detail = next(
        (c for c in cuspal_analysis if c.house == primary_cusp_num),
        cuspal_analysis[primary_cusp_num - 1]
    )

    csl = primary_cusp_detail.sub_lord
    csl_star = primary_cusp_detail.star_lord
    csl_sub_sub = primary_cusp_detail.sub_sub_lord
    csl_deg = primary_cusp_detail.cusp_degree

    # Check retrograde status of planets at question moment
    planet_positions = {p.planet: p for p in chart_res.planetary_positions}
    
    # Retrograde detection via Swiss Ephemeris speed
    is_csl_retro = False
    is_star_retro = False
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI if request.ayanamsa == 1 else swe.SIDM_LAHIRI, 0, 0)
    
    # Check CSL speed
    planet_swe_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.MEAN_NODE,
    }

    if csl in planet_swe_ids and csl not in ("Sun", "Moon", "Rahu", "Ketu"):
        try:
            res_swe, _ = swe.calc_ut(jd, planet_swe_ids[csl], swe.FLG_SIDEREAL | swe.FLG_SPEED)
            if res_swe[3] < 0:
                is_csl_retro = True
        except Exception:
            pass

    if csl_star in planet_swe_ids and csl_star not in ("Sun", "Moon", "Rahu", "Ketu"):
        try:
            res_swe, _ = swe.calc_ut(jd, planet_swe_ids[csl_star], swe.FLG_SIDEREAL | swe.FLG_SPEED)
            if res_swe[3] < 0:
                is_star_retro = True
        except Exception:
            pass

    # 5. Extract Signified Houses of CSL (Levels A, B, C, D)
    csl_signified_houses: Set[int] = set()

    # From PlanetSignificator list
    if chart_res.significators:
        for p_sig in chart_res.significators:
            if p_sig.planet == csl:
                csl_signified_houses.update(p_sig.signified_houses)

    # From house significators (Tiers A, B, C, D)
    if chart_res.house_significators:
        for h_entry in chart_res.house_significators:
            if csl in h_entry.all_significators:
                csl_signified_houses.add(h_entry.house)

    # In case still empty, include primary cusp
    if not csl_signified_houses:
        csl_signified_houses.add(primary_cusp_num)

    csl_signified_list = sorted(list(csl_signified_houses))
    supporting_hits = sorted(list(csl_signified_houses.intersection(set(supporting_houses))))
    denying_hits = sorted(list(csl_signified_houses.intersection(set(denying_houses))))

    # 6. Ruling Planets (RP) Analysis
    rp_obj = chart_res.ruling_planets
    active_rps = list(dict.fromkeys(rp_obj.ruling_planets_list))  # preserve order, unique
    
    # Check RP matches: does CSL, CSL star lord, or any supporting significator appear in RP?
    rp_matches: List[str] = []
    if csl in active_rps:
        rp_matches.append(csl)
    if csl_star in active_rps and csl_star not in rp_matches:
        rp_matches.append(csl_star)

    # Check if other planets signifying supporting houses are in RPs
    for p_sig in chart_res.significators:
        p_name = p_sig.planet
        if p_name in active_rps and p_name not in rp_matches:
            if any(h in supporting_houses for h in p_sig.signified_houses):
                rp_matches.append(p_name)

    rp_agreement = len(rp_matches) > 0

    # 7. Outcome Verdict Determination
    # Classical KP Rules:
    # 1. If CSL signifies supporting houses (especially primary cusp or >=2 supporting houses) without heavy denying houses: Promised.
    # 2. If CSL or star lord is retrograde: Delayed with effort / obstacles.
    # 3. If CSL signifies both supporting and denying houses: Delayed / Mixed.
    # 4. If CSL signifies primarily denying houses (e.g. 5, 8, 12 for court case; 1, 5, 9 for job) or misses supporting: Denied.
    if len(supporting_hits) >= 2 or (len(supporting_hits) >= 1 and len(denying_hits) == 0):
        if is_csl_retro or is_star_retro:
            outcome = OutcomeVerdict.DELAYED
            outcome_label_en = "DELAYED (With Effort & Patience)"
            outcome_label_ta = "தாமதத்துடன் வெற்றி (முயற்சி & பொறுமை தேவை)"
            outcome_badge = "warning"
            confidence_score = 74 if rp_agreement else 66
        else:
            outcome = OutcomeVerdict.YES
            outcome_label_en = "YES (Promised)"
            outcome_label_ta = "ஆம் (வெற்றி நிச்சயம் / சாதகமானது)"
            outcome_badge = "success"
            confidence_score = 94 if rp_agreement else 85
    elif len(supporting_hits) > 0 and len(denying_hits) > 0:
        outcome = OutcomeVerdict.DELAYED
        outcome_label_en = "DELAYED (Obstacles Before Success)"
        outcome_label_ta = "தாமதத்துடன் வெற்றி (தடைகளுக்குப் பின் நற்பலன்)"
        outcome_badge = "warning"
        confidence_score = 68 if rp_agreement else 58
    else:
        outcome = OutcomeVerdict.NO
        outcome_label_en = "NO (Denied / Not Favorable Currently)"
        outcome_label_ta = "இல்லை (சாதகமற்றது / தடை)"
        outcome_badge = "danger"
        confidence_score = 90 if rp_agreement else 82

    # 8. Timing of Fructification Calculation (Dasha & Moon Transit Window)
    # A. Active Vimshottari Dasa
    cur_dasa_list = chart_res.dasa_hierarchy.current_periods if chart_res.dasa_hierarchy else []
    md_lord = "Saturn"
    ad_lord = "Jupiter"
    pd_lord = "Venus"
    dasa_start_str = q_date_str
    dasa_end_str = (q_date + timedelta(days=60)).isoformat()

    for p in cur_dasa_list:
        if p.level == 1:
            md_lord = p.lord
        elif p.level == 2:
            ad_lord = p.lord
        elif p.level == 3:
            pd_lord = p.lord
            dasa_start_str = p.start_date.split("T")[0]
            dasa_end_str = p.end_date.split("T")[0]

    # B. Identify Chief Fruitful Planet for Moon Transit Trigger
    fruitful_candidate = csl_star if (csl_star in rp_matches or csl_star not in ("Rahu", "Ketu")) else csl
    if rp_matches:
        fruitful_candidate = rp_matches[0]

    # C. Calculate Moon Transit Window (Scan next 30 days)
    # Find upcoming nakshatra ruled by fruitful_candidate
    moon_transit_info = _calculate_moon_transit_window(jd, fruitful_candidate, local_dt.tzinfo, request.ayanamsa)

    timing_summary_en = (
        f"Fructification is strongly supported during {md_lord} Dasa - {ad_lord} Bhukti - {pd_lord} Antara "
        f"({dasa_start_str} to {dasa_end_str}). The critical trigger window occurs when the Moon transits "
        f"{moon_transit_info['star_en']} ({moon_transit_info['sign_en']}) between {moon_transit_info['start_str']} "
        f"and {moon_transit_info['end_str']}."
    )

    timing_summary_ta = (
        f"காரிய சித்தி காலம்: {PLANET_NAMES_TA.get(md_lord, md_lord)} மகாதிசை - "
        f"{PLANET_NAMES_TA.get(ad_lord, ad_lord)} புக்தி - "
        f"{PLANET_NAMES_TA.get(pd_lord, pd_lord)} அந்தரக் காலத்திற்குள் ({dasa_start_str} முதல் {dasa_end_str} வரை) நிகழும். "
        f"குறிப்பாக, சந்திரன் {STAR_NAMES_TA.get(moon_transit_info['star_en'], moon_transit_info['star_en'])} நட்சத்திரத்தில் "
        f"({SIGN_NAMES_TA.get(moon_transit_info['sign_en'], moon_transit_info['sign_en'])} ராசி) பிரவேசிக்கும் "
        f"{moon_transit_info['start_str']} முதல் {moon_transit_info['end_str']} வரையிலான நேரத்தில் இக்காரியம் கைகூடும்."
    )

    timing_obj = TimingWindow(
        dasha_mahadasha=md_lord,
        dasha_bhukti=ad_lord,
        dasha_antara=pd_lord,
        dasha_window_start=dasa_start_str,
        dasha_window_end=dasa_end_str,
        moon_transit_star=moon_transit_info["star_en"],
        moon_transit_star_ta=STAR_NAMES_TA.get(moon_transit_info["star_en"], moon_transit_info["star_en"]),
        moon_transit_sign=moon_transit_info["sign_en"],
        moon_transit_sign_ta=SIGN_NAMES_TA.get(moon_transit_info["sign_en"], moon_transit_info["sign_en"]),
        moon_transit_lord=fruitful_candidate,
        moon_transit_lord_ta=PLANET_NAMES_TA.get(fruitful_candidate, fruitful_candidate),
        moon_transit_start=moon_transit_info["start_str"],
        moon_transit_end=moon_transit_info["end_str"],
        summary_en=timing_summary_en,
        summary_ta=timing_summary_ta,
    )

    # 9. Build Astrological Explanations in English and Tamil
    csl_ta = PLANET_NAMES_TA.get(csl, csl)
    csl_star_ta = PLANET_NAMES_TA.get(csl_star, csl_star)
    topic_name_en = topic_data["name_en"]
    topic_name_ta = topic_data["name_ta"]
    p_cusp_desc_en = topic_data["primary_cusp_desc_en"]
    p_cusp_desc_ta = topic_data["primary_cusp_desc_ta"]

    # English texts
    primary_cusp_en = (
        f"The query topic '{topic_name_en}' is governed by {p_cusp_desc_en}. "
        f"The Horary Ascendant (fixed by Seed #{request.horary_number} at {round(chart_res.ascendant_degree % 30.0, 2)}° in "
        f"{chart_res.horary_division.sign}) establishes the 12 Placidus cusps. "
        f"The {primary_cusp_num}th Cuspal Sub-Lord (CSL) is {csl}, located in {primary_cusp_detail.sign_name} "
        f"under the constellation of {csl_star}."
    )

    csl_conn_en = (
        f"According to KP Paddhati, the planet offers the result of its constellation lord ({csl_star}), "
        f"while its sub-lord ({csl}) arbitrates the final favorable or unfavorable outcome. "
        f"The Cuspal Sub-Lord {csl} signifies houses: {csl_signified_list}. "
        f"Supporting houses for this query are {supporting_houses} (matched: {supporting_hits or 'None'}). "
        f"Denying/obstructing houses are {denying_houses} (matched: {denying_hits or 'None'}). "
        f"{'Note: CSL or Star Lord is in retrograde motion, indicating fruition requires sustained effort and persistence.' if (is_csl_retro or is_star_retro) else 'Both CSL and Star Lord are in direct motion, allowing unhindered fruition.'}"
    )

    rp_en = (
        f"Ruling Planets at the moment of query: Day Lord: {rp_obj.day_lord}, "
        f"Moon: [Sign: {rp_obj.moon_sign_lord}, Star: {rp_obj.moon_star_lord}, Sub: {rp_obj.moon_sub_lord}], "
        f"Ascendant: [Sign: {rp_obj.ascendant_sign_lord}, Star: {rp_obj.ascendant_star_lord}, Sub: {rp_obj.ascendant_sub_lord}]. "
        f"Active Ruling Planets ({', '.join(active_rps)}) cross-matched with query significators: {', '.join(rp_matches) if rp_matches else 'No direct overlap'}. "
        f"{'This strong Ruling Planet harmony confirms authentic querent intention and guarantees genuine fructification.' if rp_agreement else 'Moderate RP resonance observed.'}"
    )

    verdict_summary_en = (
        f"Verdict: {outcome_label_en} ({confidence_score}% Confidence). "
        f"{'The 12th/relevant CSL strongly aligns with supportive houses without dominant negative impedance.' if outcome == OutcomeVerdict.YES else ('Planetary indications show fruition will occur with delay or effort.' if outcome == OutcomeVerdict.DELAYED else 'The CSL fails to link to fruitful houses or is dominated by negating houses.')}"
    )

    # Tamil texts
    primary_cusp_ta = (
        f"கேட்கப்பட்ட '{topic_name_ta}' கேள்விக்கான முதன்மை பாவகம் {p_cusp_desc_ta} ஆகும். "
        f"தேர்ந்தெடுக்கப்பட்ட பிரஸ்ன எண் #{request.horary_number}-ன் படி லக்னம் {chart_res.horary_division.sign} ராசியில் நிர்ணயிக்கப்பட்டு, "
        f"12 பாவக முனைகளும் துல்லியமாக கணக்கிடப்பட்டன. "
        f"{primary_cusp_num}-ஆம் பாவக முனையின் உப-அதிபதி (CSL) **{csl_ta}** ஆவார். இவர் {primary_cusp_detail.sign_name} ராசியில் "
        f"{csl_star_ta} நட்சத்திரத்தில் சஞ்சரிக்கிறார்."
    )

    csl_conn_ta = (
        f"கே.பி. ஜோதிட விதிகளின்படி, நட்சத்திர அதிபதி ({csl_star_ta}) காரியத்தின் தன்மையையும், "
        f"உப-அதிபதி ({csl_ta}) காரியத்தின் வெற்றி அல்லது தோல்வியையும் தீர்மானிக்கிறார். "
        f"இங்கு உப-அதிபதி {csl_ta} {csl_signified_list}-ஆம் பாவகங்களுக்கு தொடர்பு பெறுகிறார். "
        f"இக்கேள்விக்குரிய சுப பாவகங்கள்: {supporting_houses} (தொடர்பு பெற்றவை: {supporting_hits or 'எதுவுமில்லை'}). "
        f"மறுக்கும் பாவகங்கள்: {denying_houses} (தொடர்பு பெற்றவை: {denying_hits or 'எதுவுமில்லை'}). "
        f"{'கவனிக்க: உப-அதிபதி அல்லது நட்சத்திர அதிபதி வக்கிர கதியில் இருப்பதால் காரியம் காலதாமதத்திற்குப் பின்பே கைகூடும்.' if (is_csl_retro or is_star_retro) else 'உப-அதிபதியும் நட்சத்திர அதிபதியும் நேர்கதியில் இருப்பதால் காரியம் தடையின்றி நடக்கும்.'}"
    )

    rp_ta = (
        f"கேள்வி நேர ஆளும் கிரகங்கள் (Ruling Planets): கிழமை அதிபதி: {PLANET_NAMES_TA.get(rp_obj.day_lord, rp_obj.day_lord)}, "
        f"சந்திரன் நின்ற ராசி/நட்சத்திர/உப அதிபதிகள்: ({PLANET_NAMES_TA.get(rp_obj.moon_sign_lord, rp_obj.moon_sign_lord)}, {PLANET_NAMES_TA.get(rp_obj.moon_star_lord, rp_obj.moon_star_lord)}, {PLANET_NAMES_TA.get(rp_obj.moon_sub_lord, rp_obj.moon_sub_lord)}), "
        f"லக்ன ராசி/நட்சத்திர/உப அதிபதிகள்: ({PLANET_NAMES_TA.get(rp_obj.ascendant_sign_lord, rp_obj.ascendant_sign_lord)}, {PLANET_NAMES_TA.get(rp_obj.ascendant_star_lord, rp_obj.ascendant_star_lord)}, {PLANET_NAMES_TA.get(rp_obj.ascendant_sub_lord, rp_obj.ascendant_sub_lord)}). "
        f"ஆளும் கிரகங்களுடன் பொருந்தியுள்ள சுப கிரகங்கள்: {', '.join([PLANET_NAMES_TA.get(p, p) for p in rp_matches]) if rp_matches else 'நேரடி தொடர்பு இல்லை'}. "
        f"{'ஆளும் கிரகங்களின் உடன்பாடு இக்கேள்வியின் நியாயத்தையும் காரிய வெற்றியையும் அறுதியிட்டு உறுதி செய்கிறது.' if rp_agreement else 'ஆளும் கிரகங்களின் மிதமான ஒத்துழைப்பு உள்ளது.'}"
    )

    verdict_summary_ta = (
        f"முடிவு: **{outcome_label_ta}** (நம்பகத்தன்மை: {confidence_score}%). "
        f"{'பாவக உப-அதிபதி சுப பாவகங்களுடன் வலுவாக இணைந்து காரிய சித்தியை உறுதி செய்கிறது.' if outcome == OutcomeVerdict.YES else ('காரியம் நிச்சயம் நடக்கும், எனினும் சிறு தடைகள் மற்றும் முயற்சிகளுக்குப் பின்னரே கைகூடும்.' if outcome == OutcomeVerdict.DELAYED else 'தற்போதைய கிரக நிலைகளின்படி பாவக உப-அதிபதி சாதகமான பாவகங்களுடன் இணையாததால் காரியம் நிறைவேறுவது கடினம்.')}"
    )

    explanation_obj = AstrologicalExplanation(
        summary_en=verdict_summary_en,
        summary_ta=verdict_summary_ta,
        primary_cusp_analysis_en=primary_cusp_en,
        primary_cusp_analysis_ta=primary_cusp_ta,
        csl_connection_en=csl_conn_en,
        csl_connection_ta=csl_conn_ta,
        ruling_planets_en=rp_en,
        ruling_planets_ta=rp_ta,
        timing_explanation_en=timing_summary_en,
        timing_explanation_ta=timing_summary_ta,
    )

    # 10. Assemble full response
    return InstantHoraryPredictionResponse(
        horary_number=request.horary_number,
        horary_division=chart_res.horary_division,
        question_topic=topic_data["id"],
        question_text=request.question_text or topic_data["sample_query_en"],
        query_timestamp=local_dt.isoformat(),
        location_name=request.location_name or "Chennai, India",
        primary_cusp=primary_cusp_num,
        primary_cusp_name_en=topic_data["name_en"],
        primary_cusp_name_ta=topic_data["name_ta"],
        supporting_houses=supporting_houses,
        denying_houses=denying_houses,
        cusp_sub_lord=csl,
        cusp_sub_lord_ta=csl_ta,
        cusp_star_lord=csl_star,
        cusp_star_lord_ta=csl_star_ta,
        cusp_sub_sub_lord=csl_sub_sub,
        cusp_longitude=round(csl_deg, 6),
        csl_signified_houses=csl_signified_list,
        supporting_hits=supporting_hits,
        denying_hits=denying_hits,
        is_csl_retrograde=is_csl_retro,
        is_star_lord_retrograde=is_star_retro,
        outcome=outcome,
        outcome_label_en=outcome_label_en,
        outcome_label_ta=outcome_label_ta,
        outcome_badge=outcome_badge,
        confidence_score=confidence_score,
        ruling_planets=active_rps,
        rp_matching_planets=rp_matches,
        rp_agreement=rp_agreement,
        timing=timing_obj,
        explanation=explanation_obj,
        ascendant_degree=chart_res.ascendant_degree,
        planetary_positions=chart_res.planetary_positions,
        cuspal_analysis=chart_res.cuspal_analysis,
    )


def _calculate_moon_transit_window(
    start_jd: float,
    lord_name: str,
    tz_obj: Any,
    ayanamsa_id: int,
) -> Dict[str, str]:
    """Calculates the nearest upcoming window where transiting Moon traverses
    a Nakshatra ruled by lord_name within the next 30 days.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI if ayanamsa_id == 1 else swe.SIDM_LAHIRI, 0, 0)
    
    # 1. Candidate Nakshatras ruled by this lord
    candidate_stars = [star for star in NAKSHATRA_LORDS if star[1].lower() == lord_name.lower()]
    if not candidate_stars:
        candidate_stars = [NAKSHATRA_LORDS[6]]  # Fallback: Punarvasu (Jupiter)

    # 2. Get current Moon position at start_jd
    res, _ = swe.calc_ut(start_jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    current_moon_lon = res[0] % 360.0

    # 3. Find which candidate star is next in forward motion
    best_star = candidate_stars[0]
    min_forward_dist = 999.0

    for star in candidate_stars:
        s_name, _, s_start, s_end = star
        dist = (s_start - current_moon_lon) % 360.0
        if dist < min_forward_dist:
            min_forward_dist = dist
            best_star = star

    s_name, _, s_start, s_end = best_star

    # 4. Moon travels ~13.176 degrees per day (roughly ~1.01 days per nakshatra)
    # Estimate time to ingress and egress
    days_to_start = min_forward_dist / 13.176
    days_to_end = days_to_start + (13.333333 / 13.176)

    # Refine exact ingress using bisection
    ingress_jd = _find_moon_crossing_jd(start_jd + max(0.0, days_to_start - 0.5), start_jd + days_to_start + 0.5, s_start)
    egress_jd = _find_moon_crossing_jd(ingress_jd + 0.5, ingress_jd + 1.5, s_end)

    # Format datetime strings in local timezone
    start_dt = _jd_to_local_dt(ingress_jd, tz_obj)
    end_dt = _jd_to_local_dt(egress_jd, tz_obj)

    star_info = point_info((s_start + 0.1) % 360.0)

    return {
        "star_en": s_name,
        "sign_en": star_info.sign,
        "start_str": start_dt.strftime("%d %b %Y, %I:%M %p"),
        "end_str": end_dt.strftime("%d %b %Y, %I:%M %p"),
    }


def _find_moon_crossing_jd(jd_min: float, jd_max: float, target_lon: float, tol_sec: float = 2.0) -> float:
    """Finds exact JD when Moon crosses target_lon using bracketed bisection."""
    tol_days = tol_sec / 86400.0
    a, b = jd_min, jd_max

    def moon_diff(t: float) -> float:
        res, _ = swe.calc_ut(t, swe.MOON, swe.FLG_SIDEREAL)
        lon = res[0] % 360.0
        return (lon - target_lon + 180.0) % 360.0 - 180.0

    fa = moon_diff(a)
    fb = moon_diff(b)

    # Handle sign mismatch or fallback
    if fa * fb > 0:
        return a + (b - a) / 2.0

    for _ in range(25):
        mid = (a + b) / 2.0
        if (b - a) < tol_days:
            return mid
        fmid = moon_diff(mid)
        if abs(fmid) < 1e-6:
            return mid
        if fa * fmid <= 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    return (a + b) / 2.0


def _jd_to_local_dt(jd: float, tz_obj: Any) -> datetime:
    """Converts Julian Day to local datetime."""
    unix_secs = (jd - 2440587.5) * 86400.0
    utc_dt = datetime.fromtimestamp(unix_secs, tz=ZoneInfo("UTC"))
    return utc_dt.astimezone(tz_obj if isinstance(tz_obj, ZoneInfo) else ZoneInfo("Asia/Kolkata"))
