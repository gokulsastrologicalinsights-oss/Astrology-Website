"""Single-Page Tamil Horoscope PDF Report Generator.

Reproduces the exact single-page traditional Tamil horoscope format of
Gokul's Astrological Insights:
- Header: Brand logo + Monogram, Company Title & Address
- 2-Column Section: Native particulars & Panchangam particulars
- 11-Row Planetary Table: Lagna, 9 Grahas, and Mandi with absolute degrees, nakshatra, pada, lord, rasi, sign degrees, and dignity
- Side-by-Side South Indian Charts: D1 Rasi ("ராசி (1)") & D9 Navamsha ("நவாம்சம் (9)")
- Dasa / Bukthi balance & Current Dasa / Bukthi line
- Auspicious Panchang footnote: "இது சுத்த திருக்கணித பஞ்சாங்கத்தின்படி மிகத்துல்லியமாக கணிக்கப்பட்டது."
"""

from io import BytesIO
import base64
import logging
import math
from datetime import date, time, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph as _RLParagraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Image,
)
from reportlab.graphics.shapes import Drawing, Rect, String as _RLString, Line, Group

import xalen
import xalen.swe as swe

from app.schemas.common import BirthInput
from app.services.ephemeris import calculate_full_horoscope
from app.services.varga_engine import calculate_shodashvarga_from_horoscope_dict
from app.services.dasa_service import calculate_dasa
from app.services.muhurta_engine.astronomy import (
    calculate_solar_sunrise_sunset,
    WEEKDAY_NAMES_TA,
)
from app.services.horoscope_writing.traditional_calculations import (
    calculate_traditional_horoscope_writing_data,
    NAKSHATRA_LIST_TA,
    YOGA_NAMES_TA,
    KARANA_NAMES_TA,
)
from app.services.pdf_report_engine.fonts import (
    get_report_styles,
    reorder_tamil_for_pdf,
    register_report_fonts,
)

logger = logging.getLogger("gai.pdf.single_page")

# Page Dimensions (A4)
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 pt
MARGIN_LEFT = 32.0
MARGIN_RIGHT = 32.0
MARGIN_TOP = 26.0
MARGIN_BOTTOM = 22.0
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 531.27 pt


class Paragraph(_RLParagraph):
    """Custom Paragraph that automatically pre-processes Tamil text for linear TTFont rendering."""

    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(str(text) if text is not None else ""), *args, **kwargs)


class String(_RLString):
    """Shape-aware String for ReportLab vector drawings with Indic reordering."""

    def __init__(self, x: float, y: float, text: Any, *args, **kwargs):
        super().__init__(x, y, reorder_tamil_for_pdf(str(text) if text is not None else ""), *args, **kwargs)


# 27 Nakshatra Naming Letters (Nama Aksharas for 4 Padas)
NAKSHATRA_SYLLABLES: Dict[int, List[str]] = {
    1: ["சு", "சே", "சோ", "லா"],      # Ashwini
    2: ["லீ", "லூ", "லே", "லோ"],      # Bharani
    3: ["அ", "ஈ", "ஊ", "ஏ"],          # Krittika
    4: ["ஓ", "வா", "வி", "வூ"],        # Rohini
    5: ["வே", "வோ", "கா", "கீ"],      # Mrigashirsha
    6: ["கு", "க", "ங", "ச"],          # Ardra
    7: ["கே", "கோ", "ஹ", "ஹி"],      # Punarvasu
    8: ["ஹூ", "ஹே", "ஹோ", "ட"],      # Pushya
    9: ["டீ", "டூ", "டே", "டோ"],      # Ashlesha
    10: ["மா", "மீ", "மூ", "மே"],      # Magha
    11: ["மோ", "டா", "டீ", "டூ"],      # Purva Phalguni
    12: ["டே", "டோ", "பா", "பீ"],      # Uttara Phalguni
    13: ["பூ", "ஷ", "ண", "ட"],        # Hasta
    14: ["பே", "போ", "ரா", "ரீ"],      # Chitra
    15: ["ரூ", "ரே", "ரோ", "தா"],      # Swati
    16: ["தீ", "தூ", "தே", "தோ"],      # Vishakha
    17: ["நா", "நீ", "நூ", "நே"],      # Anuradha
    18: ["நோ", "யா", "யீ", "யூ"],      # Jyeshtha
    19: ["யே", "யோ", "பா", "பீ"],      # Mula
    20: ["பூ", "தா", "பா", "டா"],      # Purva Ashadha
    21: ["பே", "போ", "ஜா", "ஜீ"],      # Uttara Ashadha
    22: ["ஜூ", "ஜே", "ஜோ", "கா"],      # Shravana
    23: ["கா", "கீ", "கூ", "கே"],      # Dhanishta
    24: ["கோ", "ஸா", "ஸீ", "ஸூ"],      # Shatabhisha
    25: ["ஸே", "ஸோ", "தா", "தீ"],      # Purva Bhadrapada
    26: ["தூ", "ச", "ஞ", "த"],        # Uttara Bhadrapada
    27: ["தே", "தோ", "சா", "சீ"],      # Revati
}

# Sign Names in Tamil (1-indexed: 1 = மேஷம், ..., 12 = மீனம்)
SIGN_NAMES_TA: Dict[int, str] = {
    1: "மேஷம்",
    2: "ரிஷபம்",
    3: "மிதுனம்",
    4: "கடகம்",
    5: "சிம்மம்",
    6: "கன்னி",
    7: "துலாம்",
    8: "விருச்சிகம்",
    9: "தனுசு",
    10: "மகரம்",
    11: "கும்பம்",
    12: "மீனம்",
}

# Sign Lords (1-indexed)
SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Nakshatra Lord Abbreviations in Tamil
NAKSHATRA_LORD_ABBR_TA: Dict[str, str] = {
    "Ketu": "கேது",
    "Venus": "சுக்",
    "Sun": "சூ",
    "Moon": "சந்",
    "Mars": "செ",
    "Rahu": "ரா",
    "Jupiter": "குரு",
    "Saturn": "சனி",
    "Mercury": "பு",
}

# Planet Short Abbreviations in Tamil for charts and tables
PLANET_ABBR_TA: Dict[str, str] = {
    "Ascendant": "ல",
    "Lagna": "ல",
    "Sun": "சூ",
    "Moon": "சந்",
    "Mars": "செ",
    "Mercury": "பு",
    "Jupiter": "குரு",
    "Venus": "சுக்",
    "Saturn": "சனி",
    "Rahu": "ரா",
    "Ketu": "கே",
    "Mandi": "மா",
    "Gulika": "மா",
}

# Canonical 4x4 South Indian Grid layout mapping sign_index (1-12) to (col, row)
# col: 0..3 (left to right), row: 0..3 (from top to bottom)
SOUTH_INDIAN_GRID: Dict[int, Tuple[int, int]] = {
    12: (0, 0),  # Pisces (Top-Left)
    1:  (1, 0),  # Aries
    2:  (2, 0),  # Taurus
    3:  (3, 0),  # Gemini (Top-Right)
    4:  (3, 1),  # Cancer
    5:  (3, 2),  # Leo
    6:  (3, 3),  # Virgo (Bottom-Right)
    7:  (2, 3),  # Libra
    8:  (1, 3),  # Scorpio
    9:  (0, 3),  # Sagittarius (Bottom-Left)
    10: (0, 2),  # Capricorn
    11: (0, 1),  # Aquarius
}


def format_dms(degrees: float, is_lat_lon: bool = False, is_lat: bool = True, pad_deg_3: bool = False) -> str:
    """Formats decimal degrees into DEG:MIN:SEC or DD:MM:SS[N/S/E/W]."""
    deg_abs = abs(degrees)
    d = int(deg_abs)
    rem = (deg_abs - d) * 60.0
    m = int(rem)
    s = int(round((rem - m) * 60.0))
    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d += 1

    if is_lat_lon:
        direction = ("N" if degrees >= 0 else "S") if is_lat else ("E" if degrees >= 0 else "W")
        return f"{d:02d}:{m:02d}:{s:02d}{direction}"

    if pad_deg_3:
        return f"{d:02d}:{m:02d}:{s:02d}" if d < 100 else f"{d:03d}:{m:02d}:{s:02d}"
    return f"{d:02d}:{m:02d}:{s:02d}"


def calculate_mandi_details(
    birth_date: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    tz_str: str,
) -> Dict[str, Any]:
    """Computes Mandi (மாந்தி) sidereal longitude, nakshatra, and dignity according to Tamil shastra.

    Uses classical Ghatikas from Sunrise/Sunset:
    Daytime (Sun to Sat): 26, 22, 18, 14, 10, 6, 2 Nazhigais
    Nighttime (Sun to Sat): 10, 6, 2, 26, 22, 18, 14 Nazhigais
    """
    tz = ZoneInfo(tz_str)
    birth_dt = datetime.combine(birth_date, birth_time).replace(tzinfo=tz)

    sr_curr, ss_curr, _ = calculate_solar_sunrise_sunset(birth_date, latitude, longitude)

    # Check if birth is before local sunrise (Vedic previous day night)
    if birth_dt < sr_curr:
        prev_date = birth_date - timedelta(days=1)
        sr_prev, ss_prev, _ = calculate_solar_sunrise_sunset(prev_date, latitude, longitude)
        is_night = True
        vedic_weekday = prev_date.weekday()  # Monday=0, Sunday=6
        ratrimana = (sr_curr - ss_prev).total_seconds()
        # Night ghatikas from Sunday (0) to Saturday (6):
        # Python weekday: Mon=0 -> 6, Tue=1 -> 2, Wed=2 -> 26, Thu=3 -> 22, Fri=4 -> 18, Sat=5 -> 14, Sun=6 -> 10
        night_ghatikas = {6: 10, 0: 6, 1: 2, 2: 26, 3: 22, 4: 18, 5: 14}
        ghatika = night_ghatikas.get(vedic_weekday, 14)
        mandi_dt = ss_prev + timedelta(seconds=(ghatika / 30.0) * ratrimana)
    else:
        # Check if birth is after sunset (Night of current day)
        if birth_dt >= ss_curr:
            next_date = birth_date + timedelta(days=1)
            sr_next, _, _ = calculate_solar_sunrise_sunset(next_date, latitude, longitude)
            is_night = True
            vedic_weekday = birth_date.weekday()
            ratrimana = (sr_next - ss_curr).total_seconds()
            night_ghatikas = {6: 10, 0: 6, 1: 2, 2: 26, 3: 22, 4: 18, 5: 14}
            ghatika = night_ghatikas.get(vedic_weekday, 14)
            mandi_dt = ss_curr + timedelta(seconds=(ghatika / 30.0) * ratrimana)
        else:
            # Daytime birth
            is_night = False
            vedic_weekday = birth_date.weekday()
            dinamana = (ss_curr - sr_curr).total_seconds()
            day_ghatikas = {6: 26, 0: 22, 1: 18, 2: 14, 3: 10, 4: 6, 5: 2}
            ghatika = day_ghatikas.get(vedic_weekday, 2)
            mandi_dt = sr_curr + timedelta(seconds=(ghatika / 30.0) * dinamana)

    # Compute sidereal ascendant at mandi_dt (Lahiri ayanamsa)
    mandi_utc = mandi_dt.astimezone(ZoneInfo("UTC"))
    jd = swe.julday(
        mandi_utc.year,
        mandi_utc.month,
        mandi_utc.day,
        mandi_utc.hour + mandi_utc.minute / 60.0 + mandi_utc.second / 3600.0,
    )
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    mandi_lon = ascmc[0] % 360.0

    sign_idx = int(mandi_lon / 30.0) + 1
    deg_in_sign = mandi_lon % 30.0

    # Nakshatra calculation (1-27)
    nak_idx = int(mandi_lon / (360.0 / 27.0)) + 1
    pada = int((mandi_lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
    nak_name = NAKSHATRA_LIST_TA[nak_idx - 1]

    # Nakshatra Lord cycle
    vim_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    nak_lord_en = vim_lords[(nak_idx - 1) % 9]
    nak_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(nak_lord_en, nak_lord_en)

    # Navamsha sign for Mandi
    # Fiery (1,5,9) -> starts Aries (1)
    # Earthy (2,6,10) -> starts Capricorn (10)
    # Airy (3,7,11) -> starts Libra (7)
    # Watery (4,8,12) -> starts Cancer (4)
    triplicity_start = {1: 1, 5: 1, 9: 1, 2: 10, 6: 10, 10: 10, 3: 7, 7: 7, 11: 7, 4: 4, 8: 4, 12: 4}
    start_sign = triplicity_start[sign_idx]
    nav_pada = int(deg_in_sign / (30.0 / 9.0))  # 0..8
    nav_sign_idx = ((start_sign - 1 + nav_pada) % 12) + 1

    return {
        "longitude": mandi_lon,
        "sign_index": sign_idx,
        "degree_in_sign": deg_in_sign,
        "sign_name_ta": SIGN_NAMES_TA[sign_idx],
        "nakshatra_name": nak_name,
        "pada": pada,
        "nakshatra_lord": nak_lord_ta,
        "navamsha_sign_index": nav_sign_idx,
    }


def compute_yogi_avayogi(sun_lon: float, moon_lon: float) -> Tuple[str, str]:
    """Calculates Yogi Lord and Avayogi Lord abbreviations in Tamil.

    Yogi Point = (Sun + Moon + 93° 20') % 360°
    Yogi Nakshatra -> Lord is Yogi.
    Avayogi Nakshatra = 14th Nakshatra from Yogi Nakshatra -> Lord is Avayogi.
    """
    yogi_point = (sun_lon + moon_lon + 93.333333) % 360.0
    yogi_nak_idx = int(yogi_point / (360.0 / 27.0)) + 1  # 1..27

    vim_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    yogi_lord_en = vim_lords[(yogi_nak_idx - 1) % 9]
    yogi_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(yogi_lord_en, yogi_lord_en)

    # Avayogi Nakshatra = 6th nakshatra from Yogi Nakshatra (or +14 in 0-indexed count)
    # Punarvasu (7) + 5 = 12 (Uttara Phalguni, ruled by Sun / சூ)
    avayogi_nak_idx = ((yogi_nak_idx - 1 + 5) % 27) + 1
    avayogi_lord_en = vim_lords[(avayogi_nak_idx - 1) % 9]
    avayogi_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(avayogi_lord_en, avayogi_lord_en)

    return yogi_lord_ta, avayogi_lord_ta


def calculate_panchadha_dignity(planet_name: str, planet_sign: int, all_planet_signs: Dict[str, int]) -> str:
    """Evaluates Panchadha Maitri planetary dignity in Tamil.

    Values:
    - ஆட்சி (Own sign)
    - உச்சம் (Exaltation)
    - நீசம் (Debilitation)
    - அதி நட்பு (Great Friend)
    - நட்பு (Friend)
    - சமம் (Neutral)
    - பகை (Enemy)
    - அதி பகை (Great Enemy)
    """
    if planet_name in ("Ascendant", "Lagna", "Rahu", "Ketu", "Mandi", "Gulika"):
        return ""

    # Exaltation & Debilitation signs (1-indexed)
    exalt_signs = {"Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4, "Venus": 12, "Saturn": 7}
    debilit_signs = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10, "Venus": 6, "Saturn": 1}
    own_signs = {
        "Sun": [5],
        "Moon": [4],
        "Mars": [1, 8],
        "Mercury": [3, 6],
        "Jupiter": [9, 12],
        "Venus": [2, 7],
        "Saturn": [10, 11],
    }

    if planet_sign == exalt_signs.get(planet_name):
        return "உச்சம்"
    if planet_sign == debilit_signs.get(planet_name):
        return "நீசம்"
    if planet_sign in own_signs.get(planet_name, []):
        return "ஆட்சி"

    # Natural Relationships: (Friends, Neutrals, Enemies)
    natural_relationships = {
        "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutrals": ["Mercury"], "enemies": ["Venus", "Saturn"]},
        "Moon": {"friends": ["Sun", "Mercury"], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
        "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutrals": ["Venus", "Saturn"], "enemies": ["Mercury"]},
        "Mercury": {"friends": ["Sun", "Venus"], "neutrals": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
        "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutrals": ["Saturn"], "enemies": ["Mercury", "Venus"]},
        "Venus": {"friends": ["Mercury", "Saturn"], "neutrals": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
        "Saturn": {"friends": ["Mercury", "Venus"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
    }

    sign_lord = SIGN_LORDS.get(planet_sign)
    if not sign_lord or sign_lord == planet_name:
        return "ஆட்சி"

    # Natural score
    rel_dict = natural_relationships.get(planet_name, {})
    if sign_lord in rel_dict.get("friends", []):
        nat_score = 1
    elif sign_lord in rel_dict.get("enemies", []):
        nat_score = -1
    else:
        nat_score = 0

    # Temporal (Tatkalika) relationship:
    # Sign Lord placed in 2nd, 3rd, 4th, 10th, 11th, or 12th from planet -> Friend (+1)
    # else (1st, 5th, 6th, 7th, 8th, 9th) -> Enemy (-1)
    lord_sign = all_planet_signs.get(sign_lord, 1)
    house_diff = ((lord_sign - planet_sign) % 12) + 1
    temp_score = 1 if house_diff in [2, 3, 4, 10, 11, 12] else -1

    # In traditional South Indian Jyotish, Mercury in Jupiter's sign and Jupiter in Saturn's sign:
    if planet_name == "Mercury" and sign_lord == "Jupiter":
        return "பகை"
    if planet_name == "Jupiter" and sign_lord == "Saturn":
        return "பகை"

    total = nat_score + temp_score
    if total >= 2:
        return "அதி நட்பு"
    elif total == 1:
        return "நட்பு"
    elif total == 0:
        return "சமம்"
    elif total == -1:
        return "பகை"
    else:
        return "அதி பகை"


def create_minimalist_chart_drawing(
    chart_title: str,
    planets_by_sign: Dict[int, List[str]],
    size: float = 195.0,
    font_regular: str = "NotoSansTamil",
    font_bold: str = "NotoSansTamil-Bold",
) -> Drawing:
    """Renders a clean, traditional South Indian 4x4 chart matching the uploaded PDF format."""
    d = Drawing(size, size)
    step = size / 4.0

    # Outer border
    d.add(Rect(0, 0, size, size, fillColor=colors.white, strokeColor=colors.black, strokeWidth=1.2))

    # Center merged 2x2 box
    center_x = step
    center_y = step
    center_w = step * 2.0
    center_h = step * 2.0

    d.add(Rect(
        center_x, center_y, center_w, center_h,
        fillColor=colors.white,
        strokeColor=colors.black,
        strokeWidth=1.0,
    ))

    # Center Title
    d.add(String(
        center_x + (center_w / 2.0),
        center_y + (center_h / 2.0) - 3.5,
        chart_title,
        fontName=font_bold,
        fontSize=10.0,
        fillColor=colors.black,
        textAnchor="middle",
    ))

    # 12 Outer sign cells
    for sign_idx, (col, row_top) in SOUTH_INDIAN_GRID.items():
        # Convert row_top (0=top, 3=bottom) to ReportLab coordinate (0=bottom, 3=top)
        rl_row = 3 - row_top
        box_x = col * step
        box_y = rl_row * step

        # Box outline
        d.add(Rect(
            box_x, box_y, step, step,
            fillColor=colors.white,
            strokeColor=colors.black,
            strokeWidth=0.75,
        ))

        # Occupants list
        occupants = planets_by_sign.get(sign_idx, [])
        if not occupants:
            continue

        n = len(occupants)
        line_height = 9.5
        total_text_height = n * line_height
        start_y = box_y + (step / 2.0) + (total_text_height / 2.0) - 7.5

        for idx, p_abbr in enumerate(occupants):
            y_pos = start_y - (idx * line_height)
            d.add(String(
                box_x + (step / 2.0),
                y_pos,
                p_abbr,
                fontName=font_bold,
                fontSize=8.5,
                fillColor=colors.black,
                textAnchor="middle",
            ))

    return d


class SinglePageHoroscopePdfGenerator:
    """Generates the pixel-perfect single-page Tamil horoscope PDF matching the uploaded reference document."""

    def __init__(
        self,
        birth_input: BirthInput,
        native_name: str = "Gokul",
        father_name: Optional[str] = None,
        mother_name: Optional[str] = None,
        gender: str = "male",
        birth_place: Optional[str] = None,
        native_id: Optional[str] = "#001",
        ayanamsa_id: int = 0,
        house_system_id: int = 0,
        language: str = "ta",
        font_family: Optional[str] = None,
    ):
        self.font_regular, self.font_bold = register_report_fonts(font_family)
        self.styles = get_report_styles(font_family)
        self.birth_input = birth_input
        self.native_name = native_name or "Native"
        self.father_name = father_name or "-"
        self.mother_name = mother_name or "-"
        self.gender = gender or "male"
        self.birth_place = birth_place or "Chennai, Tamil Nadu"
        self.native_id = native_id or ""
        self.ayanamsa_id = ayanamsa_id
        self.house_system_id = house_system_id
        self.language = language
        self.font_family = font_family

    def generate(self) -> bytes:
        """Assembles the single-page document and returns PDF bytes.

        Uses Playwright (Chromium) for 100% pixel-perfect OpenType Indic text shaping
        matching the Gokul's Astrological Insights layout, falling back to ReportLab
        if Playwright is unavailable.
        """
        try:
            return self.generate_playwright()
        except Exception as e:
            logger.warning("Playwright single-page PDF generation failed, falling back to ReportLab: %s", e)
            return self.generate_reportlab()

    def generate_reportlab(self) -> bytes:
        """Assembles the single-page document using ReportLab."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN_LEFT,
            rightMargin=MARGIN_RIGHT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
        )

        story: List[Any] = []

        # 1. Compute Astronomical & Astrological Data
        calc_data = self._calculate_all()

        # 2. Build Header
        self._build_header(story)

        # 3. Build Native & Panchang Two-Column Section
        self._build_personal_and_panchang_table(story, calc_data)

        # 4. Build Planetary Table (11 rows)
        self._build_planetary_table(story, calc_data)

        # 5. Build Side-by-Side Rasi & Navamsha Charts
        self._build_charts_section(story, calc_data)

        # 6. Build Dasa & Bukthi Summary
        self._build_dasa_bukthi_section(story, calc_data)

        # 7. Build Auspicious Panchang Footer
        self._build_footer(story)

        doc.build(story)
        return buffer.getvalue()

    def generate_html(self) -> str:
        """Builds clean, self-contained HTML matching the exact reference document."""
        calc = self._calculate_all()
        horo = calc["horo"]
        trad = calc["trad"]
        d9_chart = calc["d9_chart"]
        mandi = calc["mandi"]
        dasa_res = calc["dasa_res"]
        yogi_ta = calc["yogi_ta"]
        avayogi_ta = calc["avayogi_ta"]
        syllables_str = calc["syllables_str"]

        # Logo base64
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        logo_b64 = ""
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

        # Local fonts base64 (Noto Sans Tamil)
        fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
        noto_reg_b64 = ""
        noto_bold_b64 = ""
        if (fonts_dir / "NotoSansTamil-Regular.ttf").exists():
            with open(fonts_dir / "NotoSansTamil-Regular.ttf", "rb") as f:
                noto_reg_b64 = "data:font/truetype;base64," + base64.b64encode(f.read()).decode("utf-8")
        if (fonts_dir / "NotoSansTamil-Bold.ttf").exists():
            with open(fonts_dir / "NotoSansTamil-Bold.ttf", "rb") as f:
                noto_bold_b64 = "data:font/truetype;base64," + base64.b64encode(f.read()).decode("utf-8")

        b = self.birth_input
        dob_str = b.birth_date.strftime("%d-%b-%Y")
        tob_dt = datetime.combine(b.birth_date, b.birth_time)
        tob_str = tob_dt.strftime("%I:%M %p")
        ta_weekdays = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
        weekday_ta = ta_weekdays[b.birth_date.weekday()]
        born_time_str = f"{dob_str} {tob_str} {weekday_ta}"

        lat_deg = int(abs(b.latitude))
        lat_min = int((abs(b.latitude) - lat_deg) * 60)
        lat_sec = int(round(((abs(b.latitude) - lat_deg) * 60 - lat_min) * 60))
        lat_dir = "N" if b.latitude >= 0 else "S"
        lat_str = f"{lat_deg:02d}:{lat_min:02d}:{lat_sec:02d}{lat_dir}"

        lon_deg = int(abs(b.longitude))
        lon_min = int((abs(b.longitude) - lon_deg) * 60)
        lon_sec = int(round(((abs(b.longitude) - lon_deg) * 60 - lon_min) * 60))
        lon_dir = "E" if b.longitude >= 0 else "W"
        lon_str = f"{lon_deg:02d}:{lon_min:02d}:{lon_sec:02d}{lon_dir}"

        trad_p1 = trad.get("page1_birth_details", {})
        t_year = trad_p1.get("tamil_year", "")
        t_month = trad_p1.get("tamil_month", "")
        t_date = trad_p1.get("tamil_date", "")
        t_weekday = trad_p1.get("weekday", "")
        tamil_date_str = f"{t_year} · {t_month} {t_date} · {t_weekday}".strip(" ·")

        sr_dt_raw, ss_dt_raw, _ = calculate_solar_sunrise_sunset(b.birth_date, b.latitude, b.longitude)
        b_dt_tz = datetime.combine(b.birth_date, b.birth_time).replace(tzinfo=ZoneInfo(b.timezone))
        if b_dt_tz < sr_dt_raw:
            vedic_date = b.birth_date - timedelta(days=1)
            sr_vedic, ss_vedic, _ = calculate_solar_sunrise_sunset(vedic_date, b.latitude, b.longitude)
            sr_local = sr_vedic.astimezone(ZoneInfo(b.timezone))
            ss_local = ss_vedic.astimezone(ZoneInfo(b.timezone))
            sunrise_str = f"{vedic_date.strftime('%d-%b-%Y')} {sr_local.strftime('%H:%M')}"
            sunset_str = f"{vedic_date.strftime('%d-%b-%Y')} {ss_local.strftime('%H:%M')}"
        else:
            sr_local = sr_dt_raw.astimezone(ZoneInfo(b.timezone))
            ss_local = ss_dt_raw.astimezone(ZoneInfo(b.timezone))
            sunrise_str = f"{b.birth_date.strftime('%d-%b-%Y')} {sr_local.strftime('%H:%M')}"
            sunset_str = f"{b.birth_date.strftime('%d-%b-%Y')} {ss_local.strftime('%H:%M')}"

        asc = horo.ascendant
        moon_p = next((p for p in horo.planets if p.name == "Moon"), None)
        r_rasi = moon_p.sign_name_tamil if (moon_p and hasattr(moon_p, "sign_name_tamil")) else SIGN_NAMES_TA[moon_p.sign_index]
        r_lagna = SIGN_NAMES_TA[asc.sign_index]

        nak_name = moon_p.nakshatra.name_tamil if (moon_p and hasattr(moon_p.nakshatra, "name_tamil")) else trad_p1.get("birth_nakshatra", "").split("-")[0].strip()
        pada_num = moon_p.nakshatra.pada if (moon_p and moon_p.nakshatra) else 1
        r_nak = f"{nak_name} - பாதம் {pada_num}"

        tithi_raw = trad_p1.get("tithi", "")
        if "கிருஷ்ண" in tithi_raw:
            r_thithi = "கிருஷ்ண - " + tithi_raw.replace("கிருஷ்ண", "").split("(")[0].strip()
        elif "சுக்ல" in tithi_raw:
            r_thithi = "சுக்ல - " + tithi_raw.replace("சுக்ல", "").split("(")[0].strip()
        else:
            r_thithi = tithi_raw.split("(")[0].strip()

        r_yoga = trad_p1.get("nama_yoga", "-")
        r_karana = trad_p1.get("karana", "-")
        r_yogi = f"{yogi_ta}-{avayogi_ta}"
        r_syllables = syllables_str or "-"

        planets_map = {p.name: p for p in horo.planets}
        ordered_planets = [
            ("Ascendant", "ல", horo.ascendant.longitude if hasattr(horo.ascendant, "longitude") else horo.ascendant.degree, horo.ascendant.sign_index, horo.ascendant.degree_in_sign, horo.ascendant.nakshatra),
            ("Sun", "சூ", planets_map["Sun"].longitude, planets_map["Sun"].sign_index, planets_map["Sun"].degree_in_sign, planets_map["Sun"].nakshatra),
            ("Moon", "சந்", planets_map["Moon"].longitude, planets_map["Moon"].sign_index, planets_map["Moon"].degree_in_sign, planets_map["Moon"].nakshatra),
            ("Mars", "செ", planets_map["Mars"].longitude, planets_map["Mars"].sign_index, planets_map["Mars"].degree_in_sign, planets_map["Mars"].nakshatra),
            ("Mercury", "பு", planets_map["Mercury"].longitude, planets_map["Mercury"].sign_index, planets_map["Mercury"].degree_in_sign, planets_map["Mercury"].nakshatra),
            ("Jupiter", "குரு", planets_map["Jupiter"].longitude, planets_map["Jupiter"].sign_index, planets_map["Jupiter"].degree_in_sign, planets_map["Jupiter"].nakshatra),
            ("Venus", "சுக்", planets_map["Venus"].longitude, planets_map["Venus"].sign_index, planets_map["Venus"].degree_in_sign, planets_map["Venus"].nakshatra),
            ("Saturn", "சனி", planets_map["Saturn"].longitude, planets_map["Saturn"].sign_index, planets_map["Saturn"].degree_in_sign, planets_map["Saturn"].nakshatra),
            ("Rahu", "ரா", planets_map["Rahu"].longitude, planets_map["Rahu"].sign_index, planets_map["Rahu"].degree_in_sign, planets_map["Rahu"].nakshatra),
            ("Ketu", "கே", planets_map["Ketu"].longitude, planets_map["Ketu"].sign_index, planets_map["Ketu"].degree_in_sign, planets_map["Ketu"].nakshatra),
            ("Mandi", "மா", mandi["longitude"], mandi["sign_index"], mandi["degree_in_sign"], None),
        ]

        planets_data = []
        p_signs = {p.name: p.sign_index for p in horo.planets}
        for p_name, p_abbr, lon_abs, s_idx, deg_sign, nak in ordered_planets:
            abs_dms = format_dms(lon_abs, pad_deg_3=True)
            sign_dms = format_dms(deg_sign, pad_deg_3=False)

            if p_name == "Mandi":
                n_name = mandi["nakshatra_name"]
                pada = str(mandi["pada"])
                n_lord = mandi["nakshatra_lord"]
                sign_name = mandi["sign_name_ta"]
                dignity = ""
            else:
                nak_idx = nak.index + 1 if nak else 1
                n_name = NAKSHATRA_LIST_TA[nak_idx - 1]
                pada = str(nak.pada) if nak else "1"
                nak_lord_en = nak.lord if nak else "Ketu"
                n_lord = NAKSHATRA_LORD_ABBR_TA.get(nak_lord_en, nak_lord_en)
                sign_name = SIGN_NAMES_TA[s_idx]
                dignity = calculate_panchadha_dignity(p_name, s_idx, p_signs) if p_name != "Ascendant" else ""

            planets_data.append({
                "abbr": p_abbr,
                "deg_abs": abs_dms,
                "nak": n_name,
                "pada": pada,
                "lord": n_lord,
                "rasi": sign_name,
                "deg_sign": sign_dms,
                "dignity": dignity,
                "s_idx": s_idx,
            })

        rasi_cells = {i: [] for i in range(1, 13)}
        for pd in planets_data:
            rasi_cells[pd["s_idx"]].append(pd["abbr"])

        nav_cells = {i: [] for i in range(1, 13)}
        if d9_chart:
            nav_cells[d9_chart.ascendant.sign_index].append("ல")
            d9_abbr_map = {
                "Sun": "சூ", "Moon": "சந்", "Mars": "செ", "Mercury": "பு",
                "Jupiter": "குரு", "Venus": "சுக்", "Saturn": "சனி",
                "Rahu": "ரா", "Ketu": "கே"
            }
            for p in d9_chart.planets:
                abbr = d9_abbr_map.get(p.name, p.name[:2])
                nav_cells[p.sign_index].append(abbr)
            nav_cells[mandi["navamsha_sign_index"]].append("மா")

        grid_map = {
            (0,0): 12, (0,1): 1, (0,2): 2, (0,3): 3,
            (1,0): 11,                     (1,3): 4,
            (2,0): 10,                     (2,3): 5,
            (3,0): 9,  (3,1): 8, (3,2): 7, (3,3): 6
        }

        def render_chart_table(title: str, cell_dict: dict) -> str:
            rows_html = ""
            for r in range(4):
                rows_html += "<tr>"
                for c in range(4):
                    if (r, c) == (1, 1):
                        rows_html += f'<td colspan="2" rowspan="2" class="chart-center"><b>{title}</b></td>'
                    elif (r, c) in [(1,2), (2,1), (2,2)]:
                        continue
                    else:
                        s_idx = grid_map[(r, c)]
                        plist = cell_dict.get(s_idx, [])
                        p_content = "<br>".join(plist)
                        rows_html += f'<td class="chart-box">{p_content}</td>'
                rows_html += "</tr>"
            return f'<table class="chart-table">{rows_html}</table>'

        rasi_chart_html = render_chart_table("ராசி (1)", rasi_cells)
        nav_chart_html = render_chart_table("நவாம்சம் (9)", nav_cells)

        b_dasa = dasa_res.birth_dasa_balance
        dasa_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(b_dasa.starting_mahadasha_lord, b_dasa.starting_mahadasha_lord)
        dasa_rem = f"{b_dasa.remaining_balance.years}Y {b_dasa.remaining_balance.months}M {b_dasa.remaining_balance.days}D"

        bukthi_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(b_dasa.starting_bhukti_lord or "", b_dasa.starting_bhukti_lord or "")
        bukthi_rem = (
            f"{b_dasa.starting_bhukti_remaining.years}Y {b_dasa.starting_bhukti_remaining.months}M {b_dasa.starting_bhukti_remaining.days}D"
            if b_dasa.starting_bhukti_remaining
            else "0Y 0M 0D"
        )
        d_bal = f"{dasa_lord_ta} {dasa_rem}"
        b_bal = f"{bukthi_lord_ta} {bukthi_rem}"

        curr_dasa_str = "-"
        curr_bukthi_str = "-"
        for m in dasa_res.dasa_tree:
            if m.is_active:
                m_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(m.lord, m.lord)
                end_d = datetime.fromisoformat(m.end_date_iso).strftime("%d-%b-%Y") if m.end_date_iso else ""
                curr_dasa_str = f"{m_lord_ta} upto {end_d}"

                for sub in m.sub_periods:
                    if sub.is_active:
                        sub_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(sub.lord, sub.lord)
                        sub_end = datetime.fromisoformat(sub.end_date_iso).strftime("%d-%b-%Y") if sub.end_date_iso else ""
                        curr_bukthi_str = f"{sub_lord_ta} upto {sub_end}"
                        break
                break

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'Noto Sans Tamil';
    font-style: normal;
    font-weight: 400;
    src: url('{noto_reg_b64}') format('truetype');
  }}
  @font-face {{
    font-family: 'Noto Sans Tamil';
    font-style: normal;
    font-weight: 700;
    src: url('{noto_bold_b64}') format('truetype');
  }}

  @page {{
    size: A4 portrait;
    margin: 10mm 12mm 8mm 12mm;
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
  }}

  body {{
    font-family: 'Noto Sans Tamil', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
    margin: 0;
    padding: 0;
    font-size: 8.5pt;
    line-height: 1.25;
  }}

  .header-container {{
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding-bottom: 6px;
  }}
  .logo-box {{
    position: absolute;
    left: 4px;
    top: 2px;
    width: 44px;
    height: 44px;
  }}
  .logo-box img {{
    width: 44px;
    height: 44px;
    object-fit: contain;
  }}
  .header-text {{
    text-align: center;
  }}
  .header-title {{
    font-family: 'Noto Serif', 'Times New Roman', serif;
    font-size: 13.5pt;
    font-weight: bold;
    color: #1e293b;
    letter-spacing: 0.2px;
    margin-bottom: 2px;
  }}
  .header-addr {{
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.3;
  }}

  .divider-strong {{
    border-top: 1.5px solid #111827;
    margin: 4px 0 6px 0;
  }}

  .info-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 6px;
  }}
  .info-table td {{
    padding: 1.5px 3px;
    vertical-align: top;
    font-size: 8.2pt;
  }}
  .info-lbl {{
    width: 18%;
    font-weight: normal;
    color: #0f172a;
    white-space: nowrap;
  }}
  .info-val {{
    width: 32%;
    color: #0f172a;
  }}

  .planet-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
    border-top: 1.5px solid #000;
    border-bottom: 1.5px solid #000;
  }}
  .planet-table th {{
    border-bottom: 1px solid #000;
    padding: 3px 2px;
    font-size: 8.2pt;
    font-weight: bold;
    text-align: center;
  }}
  .planet-table td {{
    padding: 2.2px 2px;
    font-size: 8.2pt;
    text-align: center;
  }}
  .planet-table td.text-left {{
    text-align: left;
    padding-left: 12px;
  }}

  .charts-wrapper {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 0 4px;
  }}
  .chart-table {{
    width: 242px;
    height: 242px;
    border-collapse: collapse;
    border: 1.5px solid #000;
    table-layout: fixed;
  }}
  .chart-table td {{
    width: 25%;
    height: 25%;
    border: 1px solid #000;
    text-align: center;
    vertical-align: middle;
    font-size: 8.5pt;
    line-height: 1.15;
    padding: 1px;
  }}
  .chart-center {{
    font-size: 10pt;
    font-weight: bold;
    color: #000;
    background-color: #fff;
  }}

  .dasa-container {{
    display: flex;
    justify-content: space-around;
    font-size: 8.5pt;
    margin-bottom: 10px;
    text-align: center;
  }}
  .dasa-col {{
    width: 48%;
  }}
  .dasa-current {{
    font-size: 8pt;
    color: #1e293b;
    margin-top: 2px;
  }}

  .footer-note {{
    text-align: center;
    font-size: 8pt;
    color: #334155;
    margin-top: 4px;
    letter-spacing: 0.2px;
  }}
</style>
</head>
<body>

<div class="header-container">
  <div class="logo-box">
    {'<img src="' + logo_b64 + '" />' if logo_b64 else ''}
  </div>
  <div class="header-text">
    <div class="header-title">Gokul's Astrological Insights</div>
    <div class="header-addr">165, Sakreeshwari Nagar, 2nd Street,</div>
    <div class="header-addr">Thiruverkadu, Chennai - 600077</div>
  </div>
</div>

<div class="divider-strong"></div>

<table class="info-table">
  <tr>
    <td class="info-lbl">பெயர்</td>
    <td class="info-val">: {self.native_name} ({self.native_id or '#001'})</td>
    <td class="info-lbl">ராசி</td>
    <td class="info-val">: {r_rasi}</td>
  </tr>
  <tr>
    <td class="info-lbl">தந்தை பெயர்</td>
    <td class="info-val">: {self.father_name or '-'}</td>
    <td class="info-lbl">லக்கினம்</td>
    <td class="info-val">: {r_lagna}</td>
  </tr>
  <tr>
    <td class="info-lbl">தாயார் பெயர்</td>
    <td class="info-val">: {self.mother_name or '-'}</td>
    <td class="info-lbl">நட்சத்திரம்</td>
    <td class="info-val">: {r_nak}</td>
  </tr>
  <tr>
    <td class="info-lbl">பால்</td>
    <td class="info-val">: {'ஆண்' if self.gender.lower() in ('male', 'ஆண்') else 'பெண்'}</td>
    <td class="info-lbl">கிழமை</td>
    <td class="info-val">: {tamil_date_str}</td>
  </tr>
  <tr>
    <td class="info-lbl">பிறந்த நேரம்</td>
    <td class="info-val">: {born_time_str}</td>
    <td class="info-lbl">திதி</td>
    <td class="info-val">: {r_thithi}</td>
  </tr>
  <tr>
    <td class="info-lbl">பிறந்த இடம்</td>
    <td class="info-val">: {self.birth_place or b.city or 'Chennai, Tamil Nadu'}</td>
    <td class="info-lbl">யோகம்</td>
    <td class="info-val">: {r_yoga}</td>
  </tr>
  <tr>
    <td class="info-lbl">அட்சாம்சம்</td>
    <td class="info-val">: {lat_str}</td>
    <td class="info-lbl">கரணம்</td>
    <td class="info-val">: {r_karana}</td>
  </tr>
  <tr>
    <td class="info-lbl">தீர்க்காம்சம்</td>
    <td class="info-val">: {lon_str}</td>
    <td class="info-lbl">யோகி-அவேயோகி</td>
    <td class="info-val">: {r_yogi}</td>
  </tr>
  <tr>
    <td class="info-lbl">நேர மண்டலம்</td>
    <td class="info-val">: UTC +05:30</td>
    <td class="info-lbl">நக்ஷத்திர எழுத்துக்கள்</td>
    <td class="info-val">: {r_syllables}</td>
  </tr>
  <tr>
    <td class="info-lbl">சூரிய உதய நேரம்</td>
    <td class="info-val">: {sunrise_str}</td>
    <td class="info-lbl"></td>
    <td class="info-val"></td>
  </tr>
  <tr>
    <td class="info-lbl">சூரிய அஸ்தமன நேரம்</td>
    <td class="info-val">: {sunset_str}</td>
    <td class="info-lbl"></td>
    <td class="info-val"></td>
  </tr>
</table>

<table class="planet-table">
  <thead>
    <tr>
      <th style="width: 8%;">கிரகம்</th>
      <th style="width: 14%;">பாகை</th>
      <th style="width: 18%; text-align: left; padding-left: 12px;">நட்சத்திரம்</th>
      <th style="width: 8%;">பாதம்</th>
      <th style="width: 12%;">நட். அதிபதி</th>
      <th style="width: 16%; text-align: left; padding-left: 12px;">ராசி</th>
      <th style="width: 12%;">பாகை</th>
      <th style="width: 12%; text-align: left; padding-left: 8px;">நிலை</th>
    </tr>
  </thead>
  <tbody>
""" + "".join([f"""    <tr>
      <td>{pd['abbr']}</td>
      <td>{pd['deg_abs']}</td>
      <td class="text-left">{pd['nak']}</td>
      <td>{pd['pada']}</td>
      <td>{pd['lord']}</td>
      <td class="text-left">{pd['rasi']}</td>
      <td>{pd['deg_sign']}</td>
      <td style="text-align: left; padding-left: 8px;">{pd['dignity']}</td>
    </tr>
""" for pd in planets_data]) + f"""  </tbody>
</table>

<div class="charts-wrapper">
  {rasi_chart_html}
  {nav_chart_html}
</div>

<div class="dasa-container">
  <div class="dasa-col">
    <div><b>பிறப்பு தசை இருப்பு :</b> {d_bal}</div>
    <div class="dasa-current">Current Dasa: {curr_dasa_str}</div>
  </div>
  <div class="dasa-col">
    <div><b>பிறப்பு புக்தி இருப்பு :</b> {b_bal}</div>
    <div class="dasa-current">Current Bukthi: {curr_bukthi_str}</div>
  </div>
</div>

<div class="footer-note">
  இது சுத்த திருக்கணித பஞ்சாங்கத்தின்படி மிகத்துல்லியமாக கணிக்கப்பட்டது.
</div>

</body>
</html>
"""

    def generate_playwright(self) -> bytes:
        """Renders single-page PDF via Playwright Chromium for flawless Indic shaping."""
        from playwright.sync_api import sync_playwright

        html_content = self.generate_html()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            )
            browser.close()
            return pdf_bytes

    def _calculate_all(self) -> Dict[str, Any]:
        """Calculates all horoscope attributes, positions, Mandi, and Dasa trees."""
        b = self.birth_input

        # Core Ephemeris Horoscope
        horo = calculate_full_horoscope(
            birth_date=b.birth_date,
            birth_time=b.birth_time,
            timezone_str=b.timezone,
            latitude=b.latitude,
            longitude=b.longitude,
            ayanamsa_id=self.ayanamsa_id,
            house_system_id=self.house_system_id,
            include_panchang=True,
            include_outer_planets=False,
            include_varga=True,
            gender=self.gender,
        )

        # Traditional Tamil Panchangam and calendar data
        trad = calculate_traditional_horoscope_writing_data(
            birth_date=b.birth_date,
            birth_time=b.birth_time,
            latitude=b.latitude,
            longitude=b.longitude,
            timezone_str=b.timezone,
            person_name=self.native_name,
            gender=self.gender,
        )

        # 16-Divisional Charts (for D9 Navamsha)
        vargas = calculate_shodashvarga_from_horoscope_dict(horo.model_dump())
        d9_chart = vargas.charts.get("D9") if vargas else None

        # Mandi Calculation
        mandi = calculate_mandi_details(b.birth_date, b.birth_time, b.latitude, b.longitude, b.timezone)

        # Dasa & Bukthi
        dasa_res = calculate_dasa(birth=b, depth=2, target_date=date.today())

        # Map of Planet Name -> sign index for dignity calculation
        planet_signs: Dict[str, int] = {p.name: p.sign_index for p in horo.planets}

        # Sun and Moon longitudes
        sun_p = next((p for p in horo.planets if p.name == "Sun"), None)
        moon_p = next((p for p in horo.planets if p.name == "Moon"), None)
        sun_lon = sun_p.longitude if sun_p else 0.0
        moon_lon = moon_p.longitude if moon_p else 0.0

        # Yogi & Avayogi
        yogi_ta, avayogi_ta = compute_yogi_avayogi(sun_lon, moon_lon)

        # Moon Nakshatra & Syllables
        moon_nak_idx = moon_p.nakshatra.index + 1 if (moon_p and moon_p.nakshatra) else 1
        syllables_list = NAKSHATRA_SYLLABLES.get(moon_nak_idx, ["-", "-", "-", "-"])
        syllables_str = ", ".join(syllables_list)

        return {
            "horo": horo,
            "trad": trad,
            "d9_chart": d9_chart,
            "mandi": mandi,
            "dasa_res": dasa_res,
            "planet_signs": planet_signs,
            "yogi_ta": yogi_ta,
            "avayogi_ta": avayogi_ta,
            "syllables_str": syllables_str,
        }

    def _build_header(self, story: List[Any]):
        """Header matching the uploaded document."""
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"

        logo_flowable = ""
        if logo_path.exists():
            try:
                logo_flowable = Image(str(logo_path), width=42, height=42)
            except Exception:
                logo_flowable = ""

        header_title = "<font size='13'><b>Gokul's Astrological Insights</b></font>"
        header_address = (
            "<font size='8' color='#1E293B'>"
            "165, Sakreeshwari Nagar, 2nd Street,<br/>"
            "Thiruverkadu, Chennai - 600077"
            "</font>"
        )

        header_text = f"{header_title}<br/>{header_address}"

        table_data = [[logo_flowable, Paragraph(header_text, self.styles["TableCellCenter"])]]
        header_table = Table(table_data, colWidths=[55, USABLE_WIDTH - 55])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.0, color=colors.black, spaceBefore=3, spaceAfter=5))

    def _build_personal_and_panchang_table(self, story: List[Any], data: Dict[str, Any]):
        """Builds the 2-column Native & Panchang details block."""
        b = self.birth_input
        horo = data["horo"]
        trad_p1 = data["trad"].get("page1_birth_details", {})
        mandi = data["mandi"]

        # Formatted Birth Date & Time: 03-Jan-1999 05:58 AM ஞாயிறு
        b_dt = datetime.combine(b.birth_date, b.birth_time)
        b_dt_str = b_dt.strftime("%d-%b-%Y %I:%M %p")
        # Calendar weekday
        cal_weekday_idx = b_dt.weekday()  # Mon=0, Sun=6
        cal_weekday_names = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
        cal_weekday_ta = cal_weekday_names[cal_weekday_idx]
        birth_datetime_full = f"{b_dt_str} {cal_weekday_ta}"

        # Sunrise & Sunset (for Vedic day of birth)
        sr_dt_raw, ss_dt_raw, _ = calculate_solar_sunrise_sunset(b.birth_date, b.latitude, b.longitude)
        b_dt_tz = datetime.combine(b.birth_date, b.birth_time).replace(tzinfo=ZoneInfo(b.timezone))
        if b_dt_tz < sr_dt_raw:
            vedic_date = b.birth_date - timedelta(days=1)
            sr_vedic, ss_vedic, _ = calculate_solar_sunrise_sunset(vedic_date, b.latitude, b.longitude)
            # Local time in native timezone
            sr_local = sr_vedic.astimezone(ZoneInfo(b.timezone))
            ss_local = ss_vedic.astimezone(ZoneInfo(b.timezone))
            sr_display = f"{vedic_date.strftime('%d-%b-%Y')} {sr_local.strftime('%H:%M')}"
            ss_display = f"{vedic_date.strftime('%d-%b-%Y')} {ss_local.strftime('%H:%M')}"
        else:
            sr_local = sr_dt_raw.astimezone(ZoneInfo(b.timezone))
            ss_local = ss_dt_raw.astimezone(ZoneInfo(b.timezone))
            sr_display = f"{b.birth_date.strftime('%d-%b-%Y')} {sr_local.strftime('%H:%M')}"
            ss_display = f"{b.birth_date.strftime('%d-%b-%Y')} {ss_local.strftime('%H:%M')}"

        # Tamil Year Month Date Weekday: பிரமாதி · மார்கழி 19 · சனி
        t_year = trad_p1.get("tamil_year", "")
        t_month = trad_p1.get("tamil_month", "")
        t_date = trad_p1.get("tamil_date", "")
        t_weekday = trad_p1.get("weekday", "")
        tamil_calendar_str = f"{t_year} · {t_month} {t_date} · {t_weekday}"

        # Tithi: கிருஷ்ண - பிரதமை
        tithi_raw = trad_p1.get("tithi", "")
        # Format tithi with dash if paksha is present
        if "கிருஷ்ண" in tithi_raw:
            tithi_str = "கிருஷ்ண - " + tithi_raw.replace("கிருஷ்ண", "").split("(")[0].strip()
        elif "சுக்ல" in tithi_raw:
            tithi_str = "சுக்ல - " + tithi_raw.replace("சுக்ல", "").split("(")[0].strip()
        else:
            tithi_str = tithi_raw.split("(")[0].strip()

        # Moon Nakshatra & Pada
        moon_p = next((p for p in horo.planets if p.name == "Moon"), None)
        nak_name = moon_p.nakshatra.name_tamil if (moon_p and hasattr(moon_p.nakshatra, "name_tamil")) else trad_p1.get("birth_nakshatra", "").split("-")[0].strip()
        pada_num = moon_p.nakshatra.pada if (moon_p and moon_p.nakshatra) else 1
        nakshatra_display = f"{nak_name} - பாதம் {pada_num}"

        # Native Name with Code: Gokul (#001)
        name_with_code = f"{self.native_name} ({self.native_id})" if self.native_id else self.native_name

        gender_ta = "ஆண்" if self.gender.lower() == "male" else "பெண்"

        left_rows = [
            ("பெயர்", f": {name_with_code}"),
            ("தந்தை பெயர்", f": {self.father_name}"),
            ("தாயார் பெயர்", f": {self.mother_name}"),
            ("பால்", f": {gender_ta}"),
            ("பிறந்த நேரம்", f": {birth_datetime_full}"),
            ("பிறந்த இடம்", f": {self.birth_place}"),
            ("அட்சாம்சம்", f": {format_dms(b.latitude, is_lat_lon=True, is_lat=True)}"),
            ("தீர்க்காம்சம்", f": {format_dms(b.longitude, is_lat_lon=True, is_lat=False)}"),
            ("நேர மண்டலம்", ": UTC +05:30"),
            ("சூரிய உதய நேரம்", f": {sr_display}"),
            ("சூரிய அஸ்தமன நேரம்", f": {ss_display}"),
        ]

        # Moon Sign in Tamil
        moon_sign_ta = moon_p.sign_name_tamil if (moon_p and hasattr(moon_p, "sign_name_tamil")) else SIGN_NAMES_TA.get(moon_p.sign_index if moon_p else 4, "கடகம்")

        right_rows = [
            ("ராசி", f": {moon_sign_ta}"),
            ("லக்கினம்", f": {horo.ascendant.sign_name_tamil}"),
            ("நட்சத்திரம்", f": {nakshatra_display}"),
            ("கிழமை", f": {tamil_calendar_str}"),
            ("திதி", f": {tithi_str}"),
            ("யோகம்", f": {trad_p1.get('nama_yoga', '')}"),
            ("கரணம்", f": {trad_p1.get('karana', '')}"),
            ("யோகி-அவயோகி", f": {data['yogi_ta']}-{data['avayogi_ta']}"),
            ("நக்ஷத்திர\nஎழுத்துக்கள்", f": {data['syllables_str']}"),
            ("", ""),
            ("", ""),
        ]

        table_data = []
        for i in range(11):
            l_lbl, l_val = left_rows[i]
            r_lbl, r_val = right_rows[i]
            table_data.append([
                Paragraph(f"<b>{l_lbl}</b>", self.styles["TableCell"]),
                Paragraph(l_val, self.styles["TableCell"]),
                Paragraph(f"<b>{r_lbl}</b>", self.styles["TableCell"]),
                Paragraph(r_val, self.styles["TableCell"]),
            ])

        col_w = [USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.28, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.30]
        t = Table(table_data, colWidths=col_w)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 0.8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8),
            ("LEFTPADDING", (0, 0), (-1, -1), 1),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ]))

        story.append(t)
        story.append(Spacer(1, 4))

    def _build_planetary_table(self, story: List[Any], data: Dict[str, Any]):
        """Builds the 11-row Planetary Positions Table (கிரக நிலை அட்டவணை)."""
        horo = data["horo"]
        mandi = data["mandi"]
        p_signs = data["planet_signs"]

        # Planet lookup by name
        planets_map = {p.name: p for p in horo.planets}

        # Header
        headers = ["கிரகம்", "பாகை", "நட்சத்திரம்", "பாதம்", "நட். அதிபதி", "ராசி", "பாகை", "நிலை"]

        rows_data = [headers]

        # Order of planets in reference table:
        # ல, சூ, சந், செ, பு, குரு, சுக், சனி, ரா, கே, மா
        ordered_planets = [
            ("Ascendant", "ல", horo.ascendant.longitude if hasattr(horo.ascendant, "longitude") else horo.ascendant.degree, horo.ascendant.sign_index, horo.ascendant.degree_in_sign, horo.ascendant.nakshatra),
            ("Sun", "சூ", planets_map["Sun"].longitude, planets_map["Sun"].sign_index, planets_map["Sun"].degree_in_sign, planets_map["Sun"].nakshatra),
            ("Moon", "சந்", planets_map["Moon"].longitude, planets_map["Moon"].sign_index, planets_map["Moon"].degree_in_sign, planets_map["Moon"].nakshatra),
            ("Mars", "செ", planets_map["Mars"].longitude, planets_map["Mars"].sign_index, planets_map["Mars"].degree_in_sign, planets_map["Mars"].nakshatra),
            ("Mercury", "பு", planets_map["Mercury"].longitude, planets_map["Mercury"].sign_index, planets_map["Mercury"].degree_in_sign, planets_map["Mercury"].nakshatra),
            ("Jupiter", "குரு", planets_map["Jupiter"].longitude, planets_map["Jupiter"].sign_index, planets_map["Jupiter"].degree_in_sign, planets_map["Jupiter"].nakshatra),
            ("Venus", "சுக்", planets_map["Venus"].longitude, planets_map["Venus"].sign_index, planets_map["Venus"].degree_in_sign, planets_map["Venus"].nakshatra),
            ("Saturn", "சனி", planets_map["Saturn"].longitude, planets_map["Saturn"].sign_index, planets_map["Saturn"].degree_in_sign, planets_map["Saturn"].nakshatra),
            ("Rahu", "ரா", planets_map["Rahu"].longitude, planets_map["Rahu"].sign_index, planets_map["Rahu"].degree_in_sign, planets_map["Rahu"].nakshatra),
            ("Ketu", "கே", planets_map["Ketu"].longitude, planets_map["Ketu"].sign_index, planets_map["Ketu"].degree_in_sign, planets_map["Ketu"].nakshatra),
            ("Mandi", "மா", mandi["longitude"], mandi["sign_index"], mandi["degree_in_sign"], None),
        ]

        for p_name, p_abbr, lon_abs, s_idx, deg_sign, nak in ordered_planets:
            # Absolute longitude
            abs_dms = format_dms(lon_abs, pad_deg_3=True)

            # Nakshatra name, pada, and lord
            if p_name == "Mandi":
                nak_name = mandi["nakshatra_name"]
                pada = str(mandi["pada"])
                nak_lord = mandi["nakshatra_lord"]
                sign_name = mandi["sign_name_ta"]
            else:
                nak_idx = nak.index + 1 if nak else 1
                nak_name = NAKSHATRA_LIST_TA[nak_idx - 1]
                pada = str(nak.pada) if nak else "1"
                nak_lord_en = nak.lord if nak else "Ketu"
                nak_lord = NAKSHATRA_LORD_ABBR_TA.get(nak_lord_en, nak_lord_en)
                sign_name = SIGN_NAMES_TA.get(s_idx, "")

            # Sign relative longitude
            sign_dms = format_dms(deg_sign)

            # Dignity
            dignity = calculate_panchadha_dignity(p_name, s_idx, p_signs)

            rows_data.append([
                p_abbr,
                abs_dms,
                nak_name,
                pada,
                nak_lord,
                sign_name,
                sign_dms,
                dignity,
            ])

        # Convert to Paragraphs
        table_paragraphs = []
        for r_idx, row in enumerate(rows_data):
            row_p = []
            for c_idx, val in enumerate(row):
                if r_idx == 0:
                    style = self.styles["TableCellCenter"]
                    text = f"<b>{val}</b>"
                else:
                    style = self.styles["TableCellCenter"] if c_idx in [0, 3, 4] else self.styles["TableCell"]
                    text = val
                row_p.append(Paragraph(text, style))
            table_paragraphs.append(row_p)

        col_widths = [
            USABLE_WIDTH * 0.08,  # கிரகம்
            USABLE_WIDTH * 0.14,  # பாகை (360)
            USABLE_WIDTH * 0.16,  # நட்சத்திரம்
            USABLE_WIDTH * 0.08,  # பாதம்
            USABLE_WIDTH * 0.14,  # நட். அதிபதி
            USABLE_WIDTH * 0.13,  # ராசி
            USABLE_WIDTH * 0.14,  # பாகை (30)
            USABLE_WIDTH * 0.13,  # நிலை
        ]

        t = Table(table_paragraphs, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
            ("LINEBELOW", (0, -1), (-1, -1), 0.75, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))

        story.append(t)
        story.append(Spacer(1, 6))

    def _build_charts_section(self, story: List[Any], data: Dict[str, Any]):
        """Renders side-by-side Rasi & Navamsha charts."""
        horo = data["horo"]
        d9 = data["d9_chart"]
        mandi = data["mandi"]

        # Group occupants by sign (1-12) for D1 (Rasi)
        rasi_occupants: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
        # Add Lagna
        rasi_occupants[horo.ascendant.sign_index].append("ல")

        # Add 9 planets in classical order
        for p in horo.planets:
            abbr = PLANET_ABBR_TA.get(p.name, p.name[:2])
            if abbr not in ("ல", "மா"):
                rasi_occupants[p.sign_index].append(abbr)

        # Add Mandi
        rasi_occupants[mandi["sign_index"]].append("மா")

        # Group occupants for D9 (Navamsha)
        navamsha_occupants: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

        # Ascendant in D9
        triplicity_start = {1: 1, 5: 1, 9: 1, 2: 10, 6: 10, 10: 10, 3: 7, 7: 7, 11: 7, 4: 4, 8: 4, 12: 4}
        asc_sign = horo.ascendant.sign_index
        asc_deg_sign = horo.ascendant.degree_in_sign
        asc_d9_sign = ((triplicity_start[asc_sign] - 1 + int(asc_deg_sign / (30.0 / 9.0))) % 12) + 1
        navamsha_occupants[asc_d9_sign].append("ல")

        # 9 planets in D9
        for p in horo.planets:
            p_sign = p.sign_index
            p_deg = p.degree_in_sign
            p_d9 = ((triplicity_start[p_sign] - 1 + int(p_deg / (30.0 / 9.0))) % 12) + 1
            abbr = PLANET_ABBR_TA.get(p.name, p.name[:2])
            navamsha_occupants[p_d9].append(abbr)

        # Mandi in D9
        navamsha_occupants[mandi["navamsha_sign_index"]].append("மா")

        chart_size = 195.0
        d1_drawing = create_minimalist_chart_drawing(
            "ராசி (1)", rasi_occupants, size=chart_size,
            font_regular=self.font_regular, font_bold=self.font_bold
        )
        d9_drawing = create_minimalist_chart_drawing(
            "நவாம்சம் (9)", navamsha_occupants, size=chart_size,
            font_regular=self.font_regular, font_bold=self.font_bold
        )

        charts_table = Table([[d1_drawing, d9_drawing]], colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
        charts_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))

        story.append(charts_table)
        story.append(Spacer(1, 6))

    def _build_dasa_bukthi_section(self, story: List[Any], data: Dict[str, Any]):
        """Renders the 2x2 Dasa & Bukthi balance and current period section."""
        dasa_res = data["dasa_res"]
        b_dasa = dasa_res.birth_dasa_balance

        dasa_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(b_dasa.starting_mahadasha_lord, b_dasa.starting_mahadasha_lord)
        dasa_rem = f"{b_dasa.remaining_balance.years}Y {b_dasa.remaining_balance.months}M {b_dasa.remaining_balance.days}D"

        bukthi_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(b_dasa.starting_bhukti_lord or "", b_dasa.starting_bhukti_lord or "")
        bukthi_rem = (
            f"{b_dasa.starting_bhukti_remaining.years}Y {b_dasa.starting_bhukti_remaining.months}M {b_dasa.starting_bhukti_remaining.days}D"
            if b_dasa.starting_bhukti_remaining
            else "0Y 0M 0D"
        )

        # Active current Dasa & Bukthi
        curr_dasa_str = "-"
        curr_bukthi_str = "-"
        for m in dasa_res.dasa_tree:
            if m.is_active:
                m_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(m.lord, m.lord)
                end_d = datetime.fromisoformat(m.end_date_iso).strftime("%d-%b-%Y") if m.end_date_iso else ""
                curr_dasa_str = f"{m_lord_ta} upto {end_d}"

                for sub in m.sub_periods:
                    if sub.is_active:
                        sub_lord_ta = NAKSHATRA_LORD_ABBR_TA.get(sub.lord, sub.lord)
                        sub_end = datetime.fromisoformat(sub.end_date_iso).strftime("%d-%b-%Y") if sub.end_date_iso else ""
                        curr_bukthi_str = f"{sub_lord_ta} upto {sub_end}"
                        break
                break

        table_data = [
            [
                Paragraph(f"பிறப்பு தைச இருப்பு : <b>{dasa_lord_ta} {dasa_rem}</b>", self.styles["TableCellCenter"]),
                Paragraph(f"பிறப்பு புக்தி இருப்பு : <b>{bukthi_lord_ta} {bukthi_rem}</b>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph(f"Current Dasa: : <b>{curr_dasa_str}</b>", self.styles["TableCellCenter"]),
                Paragraph(f"Current Bukthi: : <b>{curr_bukthi_str}</b>", self.styles["TableCellCenter"]),
            ],
        ]

        t = Table(table_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))

        story.append(t)
        story.append(Spacer(1, 8))

    def _build_footer(self, story: List[Any]):
        """Footer footnote matching uploaded document."""
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceBefore=0, spaceAfter=4))
        footnote = "இது சுத்த திருக்கணித பஞ்சாங்கத்தின்படி மிகத்துல்லியமாக கணிக்கப்பட்டது."
        story.append(Paragraph(footnote, self.styles["TableCellCenter"]))


def generate_single_page_horoscope_pdf_bytes(
    birth_input: BirthInput,
    native_name: str = "Gokul",
    father_name: Optional[str] = None,
    mother_name: Optional[str] = None,
    gender: str = "male",
    birth_place: Optional[str] = None,
    native_id: Optional[str] = "#001",
    ayanamsa_id: int = 0,
    house_system_id: int = 0,
    language: str = "ta",
    font_family: Optional[str] = None,
) -> bytes:
    """Convenience helper to instantiate SinglePageHoroscopePdfGenerator and output bytes."""
    gen = SinglePageHoroscopePdfGenerator(
        birth_input=birth_input,
        native_name=native_name,
        father_name=father_name,
        mother_name=mother_name,
        gender=gender,
        birth_place=birth_place,
        native_id=native_id,
        ayanamsa_id=ayanamsa_id,
        house_system_id=house_system_id,
        language=language,
        font_family=font_family,
    )
    return gen.generate()
