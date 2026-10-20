"""Font registration and styling for bilingual English/Tamil PDF reports.

Uses Google Noto Sans Tamil (SIL Open Font License) bundled in backend/app/assets/fonts/.
Ensures complete Unicode glyph coverage for both Tamil script and Latin characters.
"""

from pathlib import Path
import logging
from typing import Dict, Any

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

_FONTS_REGISTERED = False

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


def register_report_fonts() -> None:
    """Register NotoSansTamil regular and bold TrueType fonts in ReportLab."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    if not NOTO_REGULAR.exists() or not NOTO_BOLD.exists():
        logger.warning(
            "Tamil font files not found at %s. Falling back to Helvetica.", FONTS_DIR
        )
        return

    try:
        pdfmetrics.registerFont(TTFont("NotoSansTamil", str(NOTO_REGULAR)))
        pdfmetrics.registerFont(TTFont("NotoSansTamil-Bold", str(NOTO_BOLD)))
        pdfmetrics.registerFontFamily(
            "NotoSansTamil",
            normal="NotoSansTamil",
            bold="NotoSansTamil-Bold",
            italic="NotoSansTamil",
            boldItalic="NotoSansTamil-Bold",
        )
        _FONTS_REGISTERED = True
        logger.info("Successfully registered NotoSansTamil fonts.")
    except Exception as exc:
        logger.error("Error registering NotoSansTamil fonts: %s", exc)


def get_report_styles():
    """Create and return a comprehensive ParagraphStyle collection configured for Tamil/English."""
    register_report_fonts()

    font_name = "NotoSansTamil" if _FONTS_REGISTERED else "Helvetica"
    font_bold = "NotoSansTamil-Bold" if _FONTS_REGISTERED else "Helvetica-Bold"

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

    return styles
