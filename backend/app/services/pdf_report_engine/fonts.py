"""Font registration and styling for bilingual English/Tamil PDF reports.

Uses Google Noto Sans Tamil (SIL Open Font License) bundled in backend/app/assets/fonts/.
Ensures complete Unicode glyph coverage for both Tamil script and Latin characters.
"""

from pathlib import Path
import logging
from typing import Dict, Any, Optional, Tuple
from functools import lru_cache

import re
import uharfbuzz as hb
from fontTools.ttLib import TTFont as FontToolsTTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.pdfbase.ttfonts as _ttfonts
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger("gai.pdf.fonts")

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

_hb_font: Optional[hb.Font] = None
_PUA_TO_UNICODE: Dict[int, str] = {}


def _init_pua_reverse_map():
    """Builds reverse mapping from PUA glyph code (0xE000 + gid) to Unicode text for ToUnicode CMap."""
    global _PUA_TO_UNICODE
    if _PUA_TO_UNICODE or not NOTO_REGULAR.exists():
        return
    try:
        tt = FontToolsTTFont(str(NOTO_REGULAR))
        order = tt.getGlyphOrder()
        cmap = tt.getBestCmap()
        rev = {v: chr(k) for k, v in cmap.items() if k < 0xE000}

        prefixes = {
            'k': '\u0b95', 'ka': '\u0b95',
            'ng': '\u0b99', 'nga': '\u0b99',
            'c': '\u0b9a', 'ca': '\u0b9a', 'tcha': '\u0b9a',
            'j': '\u0b9c', 'ja': '\u0b9c',
            'ny': '\u0b9e', 'nya': '\u0b9e',
            'tt': '\u0b9f', 'tta': '\u0b9f',
            'nn': '\u0ba3', 'nna': '\u0ba3',
            't': '\u0ba4', 'ta': '\u0ba4',
            'n': '\u0ba8', 'na': '\u0ba8',
            'nnn': '\u0ba9', 'nnna': '\u0ba9',
            'p': '\u0baa', 'pa': '\u0baa',
            'm': '\u0bae', 'ma': '\u0bae',
            'y': '\u0baf', 'ya': '\u0baf',
            'r': '\u0bb0', 'ra': '\u0bb0',
            'rr': '\u0bb1', 'rra': '\u0bb1',
            'l': '\u0bb2', 'la': '\u0bb2',
            'll': '\u0bb3', 'lla': '\u0bb3',
            'lll': '\u0bb4', 'llla': '\u0bb4',
            'v': '\u0bb5', 'va': '\u0bb5',
            'sh': '\u0bb6', 'sha': '\u0bb6',
            'ss': '\u0bb7', 'ssa': '\u0bb7',
            's': '\u0bb8', 'sa': '\u0bb8',
            'h': '\u0bb9', 'ha': '\u0bb9',
        }
        suffixes = {
            'prehalf': '\u0bcd',
            'aivowelsign': '\u0bbf',
            'aiivowelsign': '\u0bc0',
            'auvowelsign': '\u0bc1',
            'auuvowelsign': '\u0bc2',
            'aavowelsign': '\u0bbe',
        }

        def resolve(name: str) -> str:
            if name in rev:
                return rev[name]
            if name.endswith('tamil'):
                core = name[:-5]
                for s_name, s_char in suffixes.items():
                    if core.endswith(s_name):
                        p = core[:-len(s_name)]
                        if p in prefixes:
                            return prefixes[p] + s_char
                if core in prefixes:
                    return prefixes[core]
                if core.startswith('ivowelsign'):
                    return '\u0bbf'
                if core.startswith('iivowelsign'):
                    return '\u0bc0'
                if core.startswith('uvowelsign'):
                    return '\u0bc1'
                if core.startswith('uuvowelsign'):
                    return '\u0bc2'
                if core == 'tchaiivowelsign':
                    return '\u0b9a\u0bc0'
                if 'candrabindu' in core:
                    return '\u0b82'
                if core == 'shri':
                    return '\u0bb8\u0bcd\u0bb0\u0bc0'
                if core == 'kssha':
                    return '\u0b95\u0bcd\u0bb7'
                if core == 'ksshaprehalf':
                    return '\u0b95\u0bcd\u0bb7\u0bcd'
                if core == 'ksshauvowelsign':
                    return '\u0b95\u0bcd\u0bb7\u0bc1'
                if core == 'ksshauuvowelsign':
                    return '\u0b95\u0bcd\u0bb7\u0bc2'
            return ''

        _PUA_TO_UNICODE = {
            0xE000 + gid: resolve(name)
            for gid, name in enumerate(order)
            if resolve(name)
        }
    except Exception as exc:
        logger.warning("Failed to initialize PUA reverse map: %s", exc)


def _install_reportlab_tounicode_patch():
    """Patches ReportLab TTFont makeToUnicodeCMap so extracted PDF text accurately returns Tamil Unicode."""
    _init_pua_reverse_map()
    orig_make_cmap = getattr(_ttfonts, "_gai_orig_makeToUnicodeCMap", None)
    if orig_make_cmap is None:
        _ttfonts._gai_orig_makeToUnicodeCMap = _ttfonts.makeToUnicodeCMap

    def _gai_makeToUnicodeCMap(fontname, subset):
        if not _PUA_TO_UNICODE:
            return _ttfonts._gai_orig_makeToUnicodeCMap(fontname, subset)
        lines = [
            "/CIDInit /ProcSet findresource begin",
            "12 dict begin",
            "begincmap",
            "/CIDSystemInfo",
            f"<< /Registry ({fontname}) /Ordering ({fontname}) /Supplement 0 >> def",
            f"/CMapName /{fontname} def",
            "/CMapType 2 def",
            "1 begincodespacerange",
            f"<00> <{len(subset) - 1:02X}>",
            "endcodespacerange",
            f"{len(subset)} beginbfchar",
        ]
        for i, v in enumerate(subset):
            if v in _PUA_TO_UNICODE and _PUA_TO_UNICODE[v]:
                u_str = _PUA_TO_UNICODE[v]
                hex_str = ''.join(f"{ord(c):04X}" for c in u_str)
                lines.append(f"<{i:02X}> <{hex_str}>")
            else:
                lines.append(f"<{i:02X}> <{v:04X}>")
        lines.extend([
            "endbfchar",
            "endcmap",
            "CMapName currentdict /CMap defineresource pop",
            "end",
            "end",
        ])
        return '\n'.join(lines)

    _ttfonts.makeToUnicodeCMap = _gai_makeToUnicodeCMap


def _get_hb_font() -> Optional[hb.Font]:
    """Lazy-initializes and caches the uharfbuzz font for NotoSansTamil."""
    global _hb_font
    if _hb_font is None and NOTO_REGULAR.exists():
        try:
            blob = hb.Blob.from_file_path(str(NOTO_REGULAR))
            face = hb.Face(blob)
            _hb_font = hb.Font(face)
        except Exception as exc:
            logger.warning("Failed to initialize HarfBuzz font for NotoSansTamil: %s", exc)
    return _hb_font


@lru_cache(maxsize=16384)
def _shape_tamil_segment(segment: str) -> str:
    """Shapes a single text segment containing Tamil Unicode characters into Noto Sans Tamil PUA glyphs."""
    if not segment or not any('\u0b80' <= c <= '\u0bff' for c in segment):
        return segment
    hb_font = _get_hb_font()
    if not hb_font:
        # Fallback to simple vowel decomposition if HarfBuzz is unavailable
        text = re.sub(r'([\u0b95-\u0bb9])\u0bca', '\u0bc6\\1\u0bbe', segment)
        text = re.sub(r'([\u0b95-\u0bb9])\u0bcb', '\u0bc7\\1\u0bbe', text)
        text = re.sub(r'([\u0b95-\u0bb9])\u0bcc', '\u0bc6\\1\u0bd7', text)
        text = re.sub(r'([\u0b95-\u0bb9])([\u0bc6\u0bc7\u0bc8])', '\\2\\1', text)
        return text
    try:
        buf = hb.Buffer()
        buf.add_str(segment)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        return ''.join(chr(0xE000 + info.codepoint) for info in buf.glyph_infos)
    except Exception as exc:
        logger.warning("HarfBuzz shaping error for segment %r: %s", segment, exc)
        return segment


def reorder_tamil_for_pdf(text: Any) -> Any:
    """Pre-processes text for ReportLab by shaping Tamil syllables using HarfBuzz and Google Noto Sans Tamil.

    Uses OpenType HarfBuzz shaping to resolve complex Indic ligatures, viramas, conjuncts,
    and split/pre-base vowels into crystal-clear Noto Sans Tamil glyphs matching the website.
    Preserves XML/HTML tags (<b>, <i>, <font>, etc.) and HTML entities (&nbsp;, &amp;, etc.)
    for ReportLab Paragraphs and Canvas drawString.
    """
    if not isinstance(text, str) or not text:
        return text

    if not any('\u0b80' <= c <= '\u0bff' for c in text):
        return text

    # Split by XML/HTML tags, entities, AND isolate Tamil character sequences
    parts = re.split(r'(<[^>]+>|&[a-zA-Z0-9#]+;|[\u0b80-\u0bff]+)', text)
    shaped_parts = []
    for part in parts:
        if not part:
            continue
        if (part.startswith('<') and part.endswith('>')) or (part.startswith('&') and part.endswith(';')):
            shaped_parts.append(part)
        elif any('\u0b80' <= c <= '\u0bff' for c in part):
            shaped_parts.append(_shape_tamil_segment(part))
        else:
            shaped_parts.append(part)
    return ''.join(shaped_parts)

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

    # Install ToUnicode CMap patch for exact Unicode text extraction and search
    _install_reportlab_tounicode_patch()

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

    # Determine which font to activate based on user preference; default to Google Noto Sans Tamil
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
    else:
        # Default to Google Noto Sans Tamil across all Tamil PDF reports
        _ACTIVE_FONT_REGULAR = "NotoSansTamil"
        _ACTIVE_FONT_BOLD = "NotoSansTamil-Bold"

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
