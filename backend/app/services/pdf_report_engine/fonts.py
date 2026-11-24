"""Centralized Tamil Typography and Font Rendering Engine for Gokul's Astrological Insights (GAI).

Production-grade Tamil typography architecture providing:
1. Unified Unicode Tamil input normalization (NFC & logical character order).
2. OpenType glyph shaping via HarfBuzz (uharfbuzz) with Google Noto Sans Tamil & Noto Serif Tamil.
3. Correct PDF ToUnicode CMap extraction mapping for exact text copy-paste and searchability.
4. Two standardized typography profiles:
   - Traditional Tamil (Noto Serif Tamil): Classical astrology, horoscope booklets, muhurta certificates.
   - Modern Tamil (Noto Sans Tamil): Technical tables, KP astrology, numerology, calculations.
5. Standardized reusable components:
   - TamilParagraph (aliased as Paragraph)
   - TamilString (aliased as String)
   - TamilTable (aliased as Table)
   - TamilNumberedCanvas (aliased as NumberedCanvas)
   - HighlightBox, SectionHeader, CardTitle, etc.
"""

from pathlib import Path
import logging
from typing import Dict, Any, Optional, Tuple, List, Union
from functools import lru_cache
import unicodedata
import re

import uharfbuzz as hb
try:
    from fontTools.ttLib import TTFont as FontToolsTTFont
except ImportError:
    FontToolsTTFont = None  # type: ignore
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.pdfbase.ttfonts as _ttfonts
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph as _RLParagraph, Table as _RLTable
from reportlab.graphics.shapes import String as _RLString
from reportlab.pdfgen import canvas

logger = logging.getLogger("gai.pdf.tamil_engine")

# ---------------------------------------------------------------------------
# Font Directories & File Paths
# ---------------------------------------------------------------------------
FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"

NOTO_SANS_REGULAR = FONTS_DIR / "NotoSansTamil-Regular.ttf"
NOTO_SANS_BOLD = FONTS_DIR / "NotoSansTamil-Bold.ttf"
NOTO_SERIF_REGULAR = FONTS_DIR / "NotoSerifTamil-Regular.ttf"
NOTO_SERIF_BOLD = FONTS_DIR / "NotoSerifTamil-Bold.ttf"

# Legacy aliases for backwards compatibility
NOTO_REGULAR = NOTO_SANS_REGULAR
NOTO_BOLD = NOTO_SANS_BOLD

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

_HB_FONTS: Dict[str, Optional[hb.Font]] = {}
_FONT_PUA_MAPS: Dict[str, Dict[int, str]] = {}
_GLOBAL_PUA_TO_UNICODE: Dict[int, str] = {}


# ---------------------------------------------------------------------------
# Palette Constants (Brand Standard)
# ---------------------------------------------------------------------------
GOLD_PRIMARY = colors.HexColor("#8B6914")       # Rich Vedic Gold / Saffron
GOLD_ACCENT = colors.HexColor("#B8860B")        # Dark Goldenrod
NAVY_PRIMARY = colors.HexColor("#0F172A")       # Deep Slate / Midnight
NAVY_SECONDARY = colors.HexColor("#1E293B")     # Charcoal Slate
CRIMSON_ACCENT = colors.HexColor("#991B1B")     # Deep Vedic Red / Lagna
BG_HEADER = colors.HexColor("#F8FAFC")          # Table Header light tint
BG_ZEBRA = colors.HexColor("#F1F5F9")           # Table Zebra stripe
BORDER_COLOR = colors.HexColor("#CBD5E1")       # Subtle border slate
BORDER_GOLD = colors.HexColor("#D4AF37")        # Regal Gold border
EMERALD_GREEN = colors.HexColor("#15803D")      # Auspicious Green


# ---------------------------------------------------------------------------
# 1. Unicode Normalization & Logical Ordering
# ---------------------------------------------------------------------------
def normalize_tamil_text(text: Any) -> Any:
    """Ensures consistent Unicode NFC normalization and correct logical character order.

    Normalizes any decomposed or visual-order left-vowel combinations into canonical
    Unicode characters. Preserves XML/HTML tags and non-Tamil characters.
    """
    if not isinstance(text, str) or not text:
        return text

    # Step 1: Standard NFC decomposition/recomposition
    norm_text = unicodedata.normalize("NFC", text)

    # Step 2: Reorder two-part split vowels in visual order to canonical single characters
    # ெ (0x0BC6) + C + ா (0x0BBE) -> C + ொ (0x0BCA)
    norm_text = re.sub(r"\u0bc6([\u0b95-\u0bb9\u0bd0])\u0bbe", "\\g<1>\u0bca", norm_text)
    # ே (0x0BC7) + C + ா (0x0BBE) -> C + ோ (0x0BCB)
    norm_text = re.sub(r"\u0bc7([\u0b95-\u0bb9\u0bd0])\u0bbe", "\\g<1>\u0bcb", norm_text)
    # ெ (0x0BC6) + C + ௗ (0x0BD7) -> C + ௌ (0x0BCC)
    norm_text = re.sub(r"\u0bc6([\u0b95-\u0bb9\u0bd0])\u0bd7", "\\g<1>\u0bcc", norm_text)

    # Step 3: Reorder single left-vowels ONLY when in displaced visual order
    # A left vowel (ெ, ே, ை) belongs to the following consonant ONLY when the following
    # consonant does not already have a virama (்), and the vowel is not already trailing its base.
    def _swap_left_vowel(m):
        prefix = m.group(1)
        vowel = m.group(2)
        cons = m.group(3)
        post = m.group(4)
        if post == "\u0bcd":
            # Consonant has virama; vowel already belongs to the previous syllable
            return m.group(0)
        return f"{prefix}{cons}{vowel}{post}"

    norm_text = re.sub(
        r"(^|[\s\S])([\u0bc6\u0bc7\u0bc8])([\u0b95-\u0bb9\u0bd0])([\u0bcd\u0bbe-\u0bcd]|$)",
        _swap_left_vowel,
        norm_text,
    )

    def _swap_left_vowel_general(m):
        prefix = m.group(1)
        vowel = m.group(2)
        cons = m.group(3)
        return f"{prefix}{cons}{vowel}"

    norm_text = re.sub(
        r"(^|[^\u0b95-\u0bb9\u0bd0])([\u0bc6\u0bc7\u0bc8])([\u0b95-\u0bb9\u0bd0])(?!\u0bcd)",
        _swap_left_vowel_general,
        norm_text,
    )

    return unicodedata.normalize("NFC", norm_text)


# ---------------------------------------------------------------------------
# 2. HarfBuzz Font & PUA Reverse Mapping for ToUnicode CMap
# ---------------------------------------------------------------------------
_PREFIXES = {
    "k": "\u0b95", "ka": "\u0b95",
    "ng": "\u0b99", "nga": "\u0b99",
    "c": "\u0b9a", "ca": "\u0b9a", "tcha": "\u0b9a",
    "j": "\u0b9c", "ja": "\u0b9c",
    "ny": "\u0b9e", "nya": "\u0b9e",
    "tt": "\u0b9f", "tta": "\u0b9f",
    "nn": "\u0ba3", "nna": "\u0ba3",
    "t": "\u0ba4", "ta": "\u0ba4",
    "n": "\u0ba8", "na": "\u0ba8",
    "nnn": "\u0ba9", "nnna": "\u0ba9",
    "p": "\u0baa", "pa": "\u0baa",
    "m": "\u0bae", "ma": "\u0bae",
    "y": "\u0baf", "ya": "\u0baf",
    "r": "\u0bb0", "ra": "\u0bb0",
    "rr": "\u0bb1", "rra": "\u0bb1",
    "l": "\u0bb2", "la": "\u0bb2",
    "ll": "\u0bb3", "lla": "\u0bb3",
    "lll": "\u0bb4", "llla": "\u0bb4",
    "v": "\u0bb5", "va": "\u0bb5",
    "sh": "\u0bb6", "sha": "\u0bb6",
    "ss": "\u0bb7", "ssa": "\u0bb7",
    "s": "\u0bb8", "sa": "\u0bb8",
    "h": "\u0bb9", "ha": "\u0bb9",
    "kss": "\u0b95\u0bcd\u0bb7", "kssa": "\u0b95\u0bcd\u0bb7",
}

_SUFFIXES = {
    "prehalftamil": "\u0bcd", "prehalf": "\u0bcd",
    "iitamil": "\u0bc0", "iivowelsigntamil": "\u0bc0", "iivowelsign": "\u0bc0",
    "itamil": "\u0bbf", "ivowelsigntamil": "\u0bbf", "ivowelsign": "\u0bbf",
    "uutamil": "\u0bc2", "uuvowelsigntamil": "\u0bc2", "uuvowelsign": "\u0bc2",
    "auuvowelsigntamil": "\u0bc2", "auuvowelsign": "\u0bc2",
    "utamil": "\u0bc1", "uvowelsigntamil": "\u0bc1", "uvowelsign": "\u0bc1",
    "auvowelsigntamil": "\u0bc1", "auvowelsign": "\u0bc1",
    "aavowelsigntamil": "\u0bbe", "aavowelsign": "\u0bbe",
    "evowelsigntamil": "\u0bc6", "evowelsign": "\u0bc6",
    "eevowelsigntamil": "\u0bc7", "eevowelsign": "\u0bc7",
    "aivowelsigntamil": "\u0bc8", "aivowelsign": "\u0bc8",
    "aulengthmarktamil": "\u0bd7", "aulengthmark": "\u0bd7",
    "atamil": "",
}

_NUM_MAP = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}


def _build_font_reverse_map(font_path: Path) -> Dict[int, str]:
    """Builds reverse mapping from PUA glyph code (0xE000 + gid) to Unicode text for ToUnicode CMap."""
    mapping: Dict[int, str] = {}
    if not font_path.exists() or FontToolsTTFont is None:
        return mapping

    try:
        tt = FontToolsTTFont(str(font_path))
        order = tt.getGlyphOrder()
        cmap = tt.getBestCmap()
        rev = {v: chr(k) for k, v in cmap.items() if k < 0xE000}

        for gid, name in enumerate(order):
            pua_code = 0xE000 + gid
            if name in rev:
                mapping[pua_code] = rev[name]
                continue

            # Check uniXXXX format (Adobe standard glyph name)
            if name.startswith("uni") and len(name) >= 7 and all(c in "0123456789ABCDEFabcdef" for c in name[3:7]):
                mapping[pua_code] = chr(int(name[3:7], 16))
                continue

            # Check uXXXX format
            if name.startswith("u") and len(name) >= 5 and all(c in "0123456789ABCDEFabcdef" for c in name[1:5]):
                mapping[pua_code] = chr(int(name[1:5], 16))
                continue

            clean_name = name.split(".")[0]
            if clean_name in _NUM_MAP:
                mapping[pua_code] = _NUM_MAP[clean_name]
                continue

            if clean_name in ("shriitamil", "shritamil", "shri"):
                mapping[pua_code] = "\u0bb8\u0bcd\u0bb0\u0bc0"
                continue

            resolved = ""
            for s_name, s_char in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
                if clean_name.endswith(s_name):
                    p = clean_name[:-len(s_name)]
                    if p in _PREFIXES:
                        resolved = _PREFIXES[p] + s_char
                        break

            if not resolved and clean_name.endswith("tamil"):
                core = clean_name[:-5]
                if core in _PREFIXES:
                    resolved = _PREFIXES[core]
                elif "ivowelsign" in core:
                    resolved = "\u0bbf"
                elif "iivowelsign" in core:
                    resolved = "\u0bc0"
                elif "uvowelsign" in core:
                    resolved = "\u0bc1"
                elif "uuvowelsign" in core:
                    resolved = "\u0bc2"

            if resolved:
                mapping[pua_code] = resolved

    except Exception as exc:
        logger.warning("Failed to build reverse PUA map for %s: %s", font_path.name, exc)

    return mapping


def _init_all_pua_reverse_maps():
    """Builds and caches reverse PUA mappings for all registered fonts."""
    global _FONT_PUA_MAPS, _GLOBAL_PUA_TO_UNICODE
    if _FONT_PUA_MAPS:
        return

    # 1. Noto Sans Tamil Regular & Bold
    if NOTO_SANS_REGULAR.exists():
        m_sans = _build_font_reverse_map(NOTO_SANS_REGULAR)
        _FONT_PUA_MAPS["NotoSansTamil"] = m_sans
        _FONT_PUA_MAPS["NotoSansTamil-Bold"] = m_sans
        _GLOBAL_PUA_TO_UNICODE.update(m_sans)

    # 2. Noto Serif Tamil Regular & Bold
    if NOTO_SERIF_REGULAR.exists():
        m_serif = _build_font_reverse_map(NOTO_SERIF_REGULAR)
        _FONT_PUA_MAPS["NotoSerifTamil"] = m_serif
        _FONT_PUA_MAPS["NotoSerifTamil-Bold"] = m_serif

    # 3. Fallbacks
    for cand_name, cand_path in [
        ("Latha", LATHA_REGULAR),
        ("Vijaya", VIJAYA_REGULAR),
        ("Lohit-Tamil", LOHIT_REGULAR),
    ]:
        if cand_path.exists():
            m_cand = _build_font_reverse_map(cand_path)
            _FONT_PUA_MAPS[cand_name] = m_cand
            _FONT_PUA_MAPS[f"{cand_name}-Bold"] = m_cand


def _install_reportlab_tounicode_patch():
    """Patches ReportLab TTFont makeToUnicodeCMap so extracted PDF text accurately returns Tamil Unicode."""
    _init_all_pua_reverse_maps()
    orig_make_cmap = getattr(_ttfonts, "_gai_orig_makeToUnicodeCMap", None)
    if orig_make_cmap is None:
        _ttfonts._gai_orig_makeToUnicodeCMap = _ttfonts.makeToUnicodeCMap

    def _gai_makeToUnicodeCMap(fontname, subset):
        # Choose font-specific map if available, else global map
        matched_map = None
        for k, m in _FONT_PUA_MAPS.items():
            if k in fontname:
                matched_map = m
                break
        pua_map = matched_map or _GLOBAL_PUA_TO_UNICODE
        if not pua_map:
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
            if v in pua_map and pua_map[v]:
                u_str = pua_map[v]
                hex_str = "".join(f"{ord(c):04X}" for c in u_str)
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
        return "\n".join(lines)

    _ttfonts.makeToUnicodeCMap = _gai_makeToUnicodeCMap


def _get_hb_font(font_name: str = "NotoSansTamil") -> Optional[hb.Font]:
    """Lazy-initializes and caches uharfbuzz fonts for Noto Sans Tamil and Noto Serif Tamil."""
    clean_name = font_name.split("-")[0]
    if clean_name in _HB_FONTS:
        return _HB_FONTS[clean_name]

    target_path = None
    if "Serif" in clean_name:
        target_path = NOTO_SERIF_REGULAR if NOTO_SERIF_REGULAR.exists() else NOTO_SANS_REGULAR
    else:
        target_path = NOTO_SANS_REGULAR

    if target_path and target_path.exists():
        try:
            blob = hb.Blob.from_file_path(str(target_path))
            face = hb.Face(blob)
            font = hb.Font(face)
            _HB_FONTS[clean_name] = font
            return font
        except Exception as exc:
            logger.warning("Failed to initialize HarfBuzz font for %s: %s", clean_name, exc)

    return None


@lru_cache(maxsize=16384)
def _shape_tamil_segment(segment: str, font_family: str = "NotoSansTamil") -> str:
    """Shapes a single text segment containing Tamil Unicode characters into OpenType PUA glyphs."""
    if not segment or not any("\u0b80" <= c <= "\u0bff" for c in segment):
        return segment

    # NFC normalize segment
    norm_segment = unicodedata.normalize("NFC", segment)

    hb_font = _get_hb_font(font_family)
    if not hb_font:
        # Fallback to simple vowel decomposition if HarfBuzz is unavailable
        text = re.sub(r"([\u0b95-\u0bb9])\u0bca", "\u0bc6\\1\u0bbe", norm_segment)
        text = re.sub(r"([\u0b95-\u0bb9])\u0bcb", "\u0bc7\\1\u0bbe", text)
        text = re.sub(r"([\u0b95-\u0bb9])\u0bcc", "\u0bc6\\1\u0bd7", text)
        text = re.sub(r"([\u0b95-\u0bb9])([\u0bc6\u0bc7\u0bc8])", "\\2\\1", text)
        return text

    try:
        buf = hb.Buffer()
        buf.add_str(norm_segment)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        return "".join(chr(0xE000 + info.codepoint) for info in buf.glyph_infos)
    except Exception as exc:
        logger.warning("HarfBuzz shaping error for segment %r: %s", segment, exc)
        return segment


def reorder_tamil_for_pdf(text: Any, font_family: str = "NotoSansTamil") -> Any:
    """Pre-processes text for ReportLab by shaping Tamil syllables using HarfBuzz.

    Uses OpenType HarfBuzz shaping to resolve complex Indic ligatures, viramas, conjuncts,
    and split/pre-base vowels into Noto Tamil glyphs.
    Preserves XML/HTML tags (<b>, <i>, <font>, etc.) and HTML entities (&nbsp;, &amp;, etc.)
    for ReportLab Paragraphs and Canvas drawString.
    """
    if not isinstance(text, str) or not text:
        return text

    if not any("\u0b80" <= c <= "\u0bff" for c in text):
        return text

    # Pre-normalize entire string with NFC
    text = normalize_tamil_text(text)

    # Split by XML/HTML tags, entities, AND isolate Tamil character sequences
    parts = re.split(r"(<[^>]+>|&[a-zA-Z0-9#]+;|[\u0b80-\u0bff]+)", text)
    shaped_parts = []
    for part in parts:
        if not part:
            continue
        if (part.startswith("<") and part.endswith(">")) or (part.startswith("&") and part.endswith(";")):
            shaped_parts.append(part)
        elif any("\u0b80" <= c <= "\u0bff" for c in part):
            shaped_parts.append(_shape_tamil_segment(part, font_family))
        else:
            shaped_parts.append(part)
    return "".join(shaped_parts)


# ---------------------------------------------------------------------------
# 3. Font Registration
# ---------------------------------------------------------------------------
def register_report_fonts(preferred_family: Optional[str] = None) -> Tuple[str, str]:
    """Register TrueType fonts in ReportLab and return (active_regular, active_bold).

    Registers:
    - NotoSansTamil / NotoSansTamil-Bold (Google Noto Sans OFL)
    - NotoSerifTamil / NotoSerifTamil-Bold (Google Noto Serif OFL)
    - Vijaya / Vijaya-Bold
    - Latha / Latha-Bold
    - Lohit-Tamil
    """
    global _FONTS_REGISTERED, _ACTIVE_FONT_REGULAR, _ACTIVE_FONT_BOLD

    # Install ToUnicode CMap patch for exact Unicode text extraction and search
    _install_reportlab_tounicode_patch()

    # 1. Register NotoSansTamil
    if NOTO_SANS_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoSansTamil", str(NOTO_SANS_REGULAR)))
            b_path = NOTO_SANS_BOLD if NOTO_SANS_BOLD.exists() else NOTO_SANS_REGULAR
            pdfmetrics.registerFont(TTFont("NotoSansTamil-Bold", str(b_path)))
        except Exception:
            pass

    # 2. Register NotoSerifTamil
    if NOTO_SERIF_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoSerifTamil", str(NOTO_SERIF_REGULAR)))
            b_serif = NOTO_SERIF_BOLD if NOTO_SERIF_BOLD.exists() else NOTO_SERIF_REGULAR
            pdfmetrics.registerFont(TTFont("NotoSerifTamil-Bold", str(b_serif)))
        except Exception:
            pass

    # 3. Register Latha
    if LATHA_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Latha", str(LATHA_REGULAR)))
            b_path = LATHA_BOLD if LATHA_BOLD.exists() else LATHA_REGULAR
            pdfmetrics.registerFont(TTFont("Latha-Bold", str(b_path)))
        except Exception:
            pass

    # 4. Register Vijaya
    if VIJAYA_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Vijaya", str(VIJAYA_REGULAR)))
            b_path = VIJAYA_BOLD if VIJAYA_BOLD.exists() else VIJAYA_REGULAR
            pdfmetrics.registerFont(TTFont("Vijaya-Bold", str(b_path)))
        except Exception:
            pass

    # 5. Register Lohit-Tamil
    if LOHIT_REGULAR.exists():
        try:
            pdfmetrics.registerFont(TTFont("Lohit-Tamil", str(LOHIT_REGULAR)))
            pdfmetrics.registerFont(TTFont("Lohit-Tamil-Bold", str(LOHIT_REGULAR)))
        except Exception:
            pass

    # 6. Register User Preferred Font if present
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

    # Determine which font to activate based on preference
    req_f = (preferred_family or "").lower().strip()
    if req_f in ("serif", "notoseriftamil", "traditional"):
        _ACTIVE_FONT_REGULAR = "NotoSerifTamil"
        _ACTIVE_FONT_BOLD = "NotoSerifTamil-Bold"
    elif req_f in ("preferred", "custom") and PREFERRED_REGULAR.exists():
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
        # Default to Google Noto Sans Tamil
        _ACTIVE_FONT_REGULAR = "NotoSansTamil"
        _ACTIVE_FONT_BOLD = "NotoSansTamil-Bold"

    return _ACTIVE_FONT_REGULAR, _ACTIVE_FONT_BOLD


# ---------------------------------------------------------------------------
# 4. Standardized Typography Profiles (Phase 3)
# ---------------------------------------------------------------------------
class TypographyProfile:
    TRADITIONAL = "traditional"  # Noto Serif Tamil
    MODERN = "modern"            # Noto Sans Tamil


def get_report_styles(profile: Union[str, Optional[str]] = TypographyProfile.MODERN):
    """Create and return a comprehensive ParagraphStyle collection configured for Tamil/English.

    Profiles:
    - 'traditional' / 'serif': Noto Serif Tamil (Classical horoscope explanations, booklets, muhurta)
    - 'modern' / 'sans': Noto Sans Tamil (Clean headings, technical reports, calculation tables)
    """
    req = (profile or "").lower().strip()
    if req in ("traditional", "serif", "notoserif", "notoseriftamil"):
        font_name, font_bold = register_report_fonts("serif")
    else:
        font_name, font_bold = register_report_fonts("sans")

    styles = getSampleStyleSheet()

    # Brand Header Hierarchy
    styles.add(ParagraphStyle(
        name="BrandHeader",
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=NAVY_PRIMARY,
        alignment=1,  # Center
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="BrandSubHeader",
        fontName=font_bold,
        fontSize=11,
        leading=15,
        textColor=GOLD_PRIMARY,
        alignment=1,  # Center
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName=font_bold,
        fontSize=13,
        leading=17,
        textColor=NAVY_PRIMARY,
        spaceBefore=6,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="SectionSubtitle",
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=NAVY_SECONDARY,
        spaceAfter=4,
    ))

    # Body Text Typography
    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName=font_name,
        fontSize=8.5,
        leading=12,
        textColor=NAVY_SECONDARY,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="ReportBodyBold",
        fontName=font_bold,
        fontSize=8.5,
        leading=12,
        textColor=NAVY_PRIMARY,
        spaceAfter=4,
    ))

    # Table Typography
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName=font_bold,
        fontSize=8,
        leading=10,
        textColor=NAVY_PRIMARY,
        alignment=1,  # Center
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_SECONDARY,
        alignment=0,  # Left
    ))

    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName=font_bold,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_PRIMARY,
        alignment=0,  # Left
    ))

    styles.add(ParagraphStyle(
        name="TableCellCenter",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_SECONDARY,
        alignment=1,  # Center
    ))

    styles.add(ParagraphStyle(
        name="TableCellBoldCenter",
        fontName=font_bold,
        fontSize=7.5,
        leading=10,
        textColor=NAVY_PRIMARY,
        alignment=1,  # Center
    ))

    # Specialized Astrological Blocks
    styles.add(ParagraphStyle(
        name="CardTitle",
        fontName=font_bold,
        fontSize=9.5,
        leading=13,
        textColor=GOLD_PRIMARY,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name="TamilShloka",
        fontName=font_bold,
        fontSize=9,
        leading=14,
        textColor=GOLD_PRIMARY,
        alignment=1,  # Center
        spaceBefore=4,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="DisclaimerText",
        fontName=font_name,
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#64748B"),
        alignment=0,
    ))

    # Aliases for backward compatibility across legacy generators
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName=font_bold,
        fontSize=15,
        leading=19,
        textColor=GOLD_PRIMARY,
        alignment=1,  # Center
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=NAVY_SECONDARY,
        alignment=1,  # Center
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="NormalSmall",
        fontName=font_name,
        fontSize=8,
        leading=11,
        textColor=NAVY_PRIMARY,
    ))

    return styles


def get_traditional_styles():
    """Convenience accessor for Traditional Tamil typography profile (Noto Serif Tamil)."""
    return get_report_styles(TypographyProfile.TRADITIONAL)


def get_modern_styles():
    """Convenience accessor for Modern Tamil typography profile (Noto Sans Tamil)."""
    return get_report_styles(TypographyProfile.MODERN)


# ---------------------------------------------------------------------------
# 5. Standardized Reusable PDF Components (Phase 4)
# ---------------------------------------------------------------------------
class TamilParagraph(_RLParagraph):
    """Centralized Tamil-aware Paragraph component for all ReportLab documents.

    Automatically normalizes input with Unicode NFC, resolves glyph shaping via HarfBuzz
    matching the paragraph style's font family, and handles XML tags and entities.
    """

    def __init__(self, text: Any, style: Any = None, *args, **kwargs):
        font_family = "NotoSerifTamil" if style and getattr(style, "fontName", "").startswith("NotoSerif") else "NotoSansTamil"
        safe_str = str(text) if text is not None else ""
        shaped_text = reorder_tamil_for_pdf(safe_str, font_family=font_family)
        super().__init__(shaped_text, style, *args, **kwargs)


# Alias Paragraph so generators can directly import: from ...fonts import Paragraph
Paragraph = TamilParagraph


class TamilString(_RLString):
    """Centralized Tamil-aware String for vector drawings (astrological charts)."""

    def __init__(self, x: float, y: float, text: Any, font_family: str = "NotoSansTamil", *args, **kwargs):
        safe_str = str(text) if text is not None else ""
        font_name = kwargs.pop("fontName", None) or font_family
        shaped_text = reorder_tamil_for_pdf(safe_str, font_family=font_name)
        super().__init__(x, y, shaped_text, fontName=font_name, *args, **kwargs)


# Alias String so chart generators can directly import: from ...fonts import String
String = TamilString


class TamilTable(_RLTable):
    """Centralized Tamil-aware Table component.

    Automatically traverses data matrix; if a cell contains a raw string, it wraps it in
    TamilParagraph using the provided default_cell_style so Tamil text is never left unshaped.
    """

    def __init__(self, data: List[List[Any]], *args, default_cell_style: Any = None, **kwargs):
        if data and isinstance(data, list):
            cell_style = default_cell_style or get_report_styles()["TableCell"]
            processed_data = []
            for row in data:
                if isinstance(row, (list, tuple)):
                    processed_row = []
                    for cell in row:
                        if isinstance(cell, str) and cell.strip():
                            processed_row.append(TamilParagraph(cell, cell_style))
                        else:
                            processed_row.append(cell)
                    processed_data.append(processed_row)
                else:
                    processed_data.append(row)
            data = processed_data
        super().__init__(data, *args, **kwargs)


Table = TamilTable


class TamilNumberedCanvas(canvas.Canvas):
    """Centralized two-pass running header and footer canvas for multi-page documents.

    Computes total page count accurately ('Page X of Y' / 'பக்கம் X / Y') and prints
    crisp Vedic gold & navy running headers and footers with customizable branding.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.report_title: str = "Gokul's Astrological Insights"
        self.footer_left: str = "Official Astrology Report • Gokul's Astrological Insights"
        self.language: str = "en"
        try:
            self.setTitle("Official Astrology Report - Gokul's Astrological Insights")
            self.setAuthor("Gokul's Astrological Insights")
            self.setCreator("Gokul's Astrological Insights")
            self.setSubject("Official Astrological Calculations and Analysis")
        except Exception:
            pass

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        page_w, page_h = self._pagesize

        # Running Footer
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(36, 32, page_w - 36, 32)

        # Footer Left
        self.setFont(_ACTIVE_FONT_REGULAR, 7)
        self.setFillColor(NAVY_SECONDARY)
        f_left = self.footer_left
        if any("\u0b80" <= c <= "\u0bff" for c in f_left):
            f_left = reorder_tamil_for_pdf(f_left, _ACTIVE_FONT_REGULAR)
        self.drawString(36, 22, f_left)

        # Footer Right: Page X of Y
        is_tamil = self.language == "ta" or any("\u0b80" <= c <= "\u0bff" for c in self.report_title)
        page_str = f"பக்கம் {self._pageNumber} / {total_pages}" if is_tamil else f"Page {self._pageNumber} of {total_pages}"
        if is_tamil:
            page_str = reorder_tamil_for_pdf(page_str, _ACTIVE_FONT_REGULAR)
        self.drawRightString(page_w - 36, 22, page_str)

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(GOLD_ACCENT)
            self.setLineWidth(0.75)
            self.line(36, page_h - 32, page_w - 36, page_h - 32)

            self.setFont(_ACTIVE_FONT_BOLD, 7.5)
            self.setFillColor(GOLD_PRIMARY)
            h_title = self.report_title
            if any("\u0b80" <= c <= "\u0bff" for c in h_title):
                h_title = reorder_tamil_for_pdf(h_title, _ACTIVE_FONT_BOLD)
            self.drawString(36, page_h - 26, h_title)

        self.restoreState()


NumberedCanvas = TamilNumberedCanvas
