"""Font registration and styling for bilingual English/Tamil PDF reports.

Uses Google Noto Sans Tamil (SIL Open Font License) bundled in backend/app/assets/fonts/.
Ensures complete Unicode glyph coverage for both Tamil script and Latin characters.
"""

from pathlib import Path
import logging
from typing import Dict, Any, Optional, Tuple

import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger("gai.pdf.fonts")


def reorder_tamil_for_pdf(text: Any) -> Any:
    """Reorder Indic pre-base and split vowels for simple TrueType renderers like ReportLab.

    ReportLab TTFont renders glyphs in sequential left-to-right order without OpenType
    GSUB/GPOS glyph reordering.

    In standard Unicode:
      Consonant + VowelSign

    This function converts syllables into visual rendering order:
      1. Split vowels (o, oo, au):
         - \\u0bca (o)  -> \\u0bc6 + consonant + \\u0bbe
         - \\u0bcb (oo) -> \\u0bc7 + consonant + \\u0bbe
         - \\u0bcc (au) -> \\u0bc6 + consonant + \\u0bd7
      2. Pre-base vowels (e, ee, ai):
         - consonant + \\u0bc6 -> \\u0bc6 + consonant
         - consonant + \\u0bc7 -> \\u0bc7 + consonant
         - consonant + \\u0bc8 -> \\u0bc8 + consonant
    """
    if not isinstance(text, str) or not text:
        return text

    # 1. Decompose split vowels (o, oo, au)
    text = re.sub(r'([\u0b95-\u0bb9])\u0bca', '\u0bc6\\1\u0bbe', text)
    text = re.sub(r'([\u0b95-\u0bb9])\u0bcb', '\u0bc7\\1\u0bbe', text)
    text = re.sub(r'([\u0b95-\u0bb9])\u0bcc', '\u0bc6\\1\u0bd7', text)

    # 2. Reorder pre-base vowels (e, ee, ai)
    text = re.sub(r'([\u0b95-\u0bb9])([\u0bc6\u0bc7\u0bc8])', '\\2\\1', text)

    return text


FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
NOTO_REGULAR = FONTS_DIR / "NotoSansTamil-Regular.ttf"
NOTO_BOLD = FONTS_DIR / "NotoSansTamil-Bold.ttf"
LATHA_REGULAR = FONTS_DIR / "Latha.ttf"
LATHA_BOLD = FONTS_DIR / "Latha-Bold.ttf"
VIJAYA_REGULAR = FONTS_DIR / "Vijaya.ttf"
VIJAYA_BOLD = FONTS_DIR / "Vijaya-Bold.ttf"
LOHIT_REGULAR = FONTS_DIR / "Lohit-Tamil.ttf"
PREFERRED_REGULAR = FONTS_DIR / "preferred_tamil.ttf"
PREFERRED_BOLD = FONTS_DIR / "preferred_tamil_bold.ttf"

_FONTS_REGISTERED = False
_ACTIVE_FONT_REGULAR = "NotoSansTamil"
_ACTIVE_FONT_BOLD = "NotoSansTamil-Bold"

# Palette constants
GOLD_PRIMARY = colors.HexColor("#8B6914")       # Rich Vedic Gold / Saffron
GOLD_ACCENT = colors.HexColor("#B8860B")        # Dark Goldenrod
NAVY_PRIMARY = colors.HexColor("#0F172A")       # Deep Slate / Midnight
NAVY_SECONDARY = colors.HexColor("#1E293B")     # Charcoal Slate
CRIMSON_ACCENT = colors.HexColor("#991B1B")     # Deep Vedic Red / Lagna
BG_HEADER = colors.HexColor("#F8FAFC")          # Table Header light tint
BG_ZEBRA = colors.HexColor("#F1F5F9")           # Table Zebra stripe
BORDER_COLOR = colors.HexColor("#CBD5E1")       # Subtle border slate
EMERALD_GREEN = colors.HexColor("#15803D")      # Auspicious Green


def register_report_fonts(preferred_family: Optional[str] = None) -> Tuple[str, str]:
    """Register TrueType fonts in ReportLab and return (active_regular, active_bold).

    Supports:
    - User Preferred Font: preferred_tamil.ttf / custom_tamil.ttf in assets/fonts/
    - Vijaya / Vijaya-Bold (Traditional Tamil serif)
    - Latha / Latha-Bold (Standard Windows Tamil)
    - Lohit-Tamil (Open-source Indic font)
    - NotoSansTamil / NotoSansTamil-Bold (Google Noto OFL)
    """
    global _FONTS_REGISTERED, _ACTIVE_FONT_REGULAR, _ACTIVE_FONT_BOLD

    # 1. Register NotoSansTamil
    if NOTO_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoSansTamil", str(NOTO_REGULAR)))
            if NOTO_BOLD.exists():
                pdfmetrics.registerFont(TTFont("NotoSansTamil-Bold", str(NOTO_BOLD)))
        except Exception:
            pass

    # 2. Register Latha
    if LATHA_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Latha", str(LATHA_REGULAR)))
            b_path = LATHA_BOLD if LATHA_BOLD.exists() else LATHA_REGULAR
            pdfmetrics.registerFont(TTFont("Latha-Bold", str(b_path)))
        except Exception:
            pass

    # 3. Register Vijaya
    if VIJAYA_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Vijaya", str(VIJAYA_REGULAR)))
            b_path = VIJAYA_BOLD if VIJAYA_BOLD.exists() else VIJAYA_REGULAR
            pdfmetrics.registerFont(TTFont("Vijaya-Bold", str(b_path)))
        except Exception:
            pass

    # 4. Register Lohit-Tamil
    if LOHIT_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Lohit-Tamil", str(LOHIT_REGULAR)))
            pdfmetrics.registerFont(TTFont("Lohit-Tamil-Bold", str(LOHIT_REGULAR)))
        except Exception:
            pass

    # 5. Register User's custom preferred font if present
    for custom_candidate in [PREFERRED_REGULAR, FONTS_DIR / "preferred_font.ttf", FONTS_DIR / "custom_tamil.ttf"]:
        if custom_candidate.exists():
            try:
                pdfmetrics.registerFont(TTFont("PreferredTamil", str(custom_candidate)))
                b_cand = PREFERRED_BOLD if PREFERRED_BOLD.exists() else custom_candidate
                pdfmetrics.registerFont(TTFont("PreferredTamil-Bold", str(b_cand)))
                _ACTIVE_FONT_REGULAR = "PreferredTamil"
                _ACTIVE_FONT_BOLD = "PreferredTamil-Bold"
                break
            except Exception as e:
                logger.warning("Could not register preferred custom font: %s", e)

    _FONTS_REGISTERED = True

    # Determine which font to activate based on user preference
    req_f = (preferred_family or "").lower().strip()
    if req_f in ("preferred", "custom") and PREFERRED_REGULAR.exists():
        _ACTIVE_FONT_REGULAR = "PreferredTamil"
        _ACTIVE_FONT_BOLD = "PreferredTamil-Bold"
    elif req_f == "vijaya" and VIJAYA_REGULAR.exists():
        _ACTIVE_FONT_REGULAR = "Vijaya"
        _ACTIVE_FONT_BOLD = "Vijaya-Bold"
    elif req_f == "latha" and LATHA_REGULAR.exists():
        _ACTIVE_FONT_REGULAR = "Latha"
        _ACTIVE_FONT_BOLD = "Latha-Bold"
    elif req_f == "lohit" and LOHIT_REGULAR.exists():
        _ACTIVE_FONT_REGULAR = "Lohit-Tamil"
        _ACTIVE_FONT_BOLD = "Lohit-Tamil-Bold"
    elif req_f == "noto":
        _ACTIVE_FONT_REGULAR = "NotoSansTamil"
        _ACTIVE_FONT_BOLD = "NotoSansTamil-Bold"
    elif PREFERRED_REGULAR.exists():
        _ACTIVE_FONT_REGULAR = "PreferredTamil"
        _ACTIVE_FONT_BOLD = "PreferredTamil-Bold"

    return _ACTIVE_FONT_REGULAR, _ACTIVE_FONT_BOLD


def get_report_styles(preferred_family: Optional[str] = None):
    """Create and return a comprehensive ParagraphStyle collection configured for Tamil/English."""
    font_name, font_bold = register_report_fonts(preferred_family)

    styles = getSampleStyleSheet()

    # Modify Base styles
    styles.add(ParagraphStyle(
        name="BrandHeader",
        fontName=font_bold,
        fontSize=20,
        leading=24,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="BrandSubHeader",
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=GOLD_PRIMARY,
        alignment=1, # Center
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName=font_bold,
        fontSize=14,
        leading=18,
        textColor=NAVY_PRIMARY,
        spaceBefore=4,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionSubtitle",
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=NAVY_SECONDARY,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName=font_name,
        fontSize=8.5,
        leading=12,
        textColor=NAVY_SECONDARY,
    ))

    styles.add(ParagraphStyle(
        name="ReportBodyBold",
        fontName=font_bold,
        fontSize=8.5,
        leading=12,
        textColor=NAVY_PRIMARY,
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName=font_bold,
        fontSize=8,
        leading=10,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_SECONDARY,
        alignment=0, # Left
    ))

    styles.add(ParagraphStyle(
        name="TableCellCenter",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_SECONDARY,
        alignment=1, # Center
    ))

    styles.add(ParagraphStyle(
        name="TableCellBoldCenter",
        fontName=font_bold,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
    ))

    styles.add(ParagraphStyle(
        name="CardTitle",
        fontName=font_bold,
        fontSize=9.5,
        leading=13,
        textColor=GOLD_PRIMARY,
    ))

    styles.add(ParagraphStyle(
        name="TamilShloka",
        fontName=font_bold,
        fontSize=9,
        leading=14,
        textColor=GOLD_PRIMARY,
        alignment=1,
    ))

    styles.add(ParagraphStyle(
        name="DisclaimerText",
        fontName=font_name,
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#64748B"),
        alignment=0,
    ))

    # Standard aliases & utility styles
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName=font_bold,
        fontSize=15,
        leading=19,
        textColor=GOLD_PRIMARY,
        alignment=1, # Center
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=NAVY_SECONDARY,
        alignment=1, # Center
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName=font_bold,
        fontSize=8,
        leading=10,
        textColor=NAVY_PRIMARY,
    ))

    styles.add(ParagraphStyle(
        name="NormalSmall",
        fontName=font_name,
        fontSize=8,
        leading=11,
        textColor=NAVY_PRIMARY,
    ))

    return styles
