"""Tamil & English Visual Social Card Renderer for Facebook Page Publishing.

Generates 1080x1350 (4:5 portrait) branded infographic PNG cards using
pure-Python HarfBuzz OpenType shaping (uharfbuzz), ReportLab vector graphics,
and PyPDFium2 rasterization—delivering native Tamil ligature accuracy at low
memory footprint (suitable for Render's 512 MB tier without headless Chromium).
"""

from __future__ import annotations

from io import BytesIO
import logging
import math
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw
import pypdfium2 as pdfium
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import uharfbuzz as hb

from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.kp_horary_prediction_service import (
    PLANET_NAMES_TA,
    SIGN_NAMES_TA,
    STAR_NAMES_TA,
)

logger = logging.getLogger("gai.facebook.cards")

CARD_PT_WIDTH = 540.0
CARD_PT_HEIGHT = 675.0
RASTER_SCALE = 2.0  # 540x675 pt * 2 => 1080x1350 px (4:5 Facebook/IG portrait)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
LOGO_PATH = ASSETS_DIR / "logo.png"

NOTO_REGULAR_PATH = FONTS_DIR / "NotoSansTamil-Regular.ttf"
NOTO_BOLD_PATH = FONTS_DIR / "NotoSansTamil-Bold.ttf"

# Shared Tamil localization constants
SENTIMENT_MAP_TA: Dict[str, str] = {
    "Excellent": "மிகச் சிறப்பான நாள்",
    "Favorable": "சாதகமான நாள்",
    "Mixed": "மிதமான நாள்",
    "Challenging": "சவாலான நாள்",
}

SENTIMENT_SHORT_TA: Dict[str, str] = {
    "Excellent": "மிகச் சிறப்பு",
    "Favorable": "சாதகம்",
    "Mixed": "மிதமானது",
    "Challenging": "கவனம்",
}

MONTHS_TA: Dict[int, str] = {
    1: "ஜனவரி",
    2: "பிப்ரவரி",
    3: "மார்ச்",
    4: "ஏப்ரல்",
    5: "மே",
    6: "ஜூன்",
    7: "ஜூலை",
    8: "ஆகஸ்ட்",
    9: "செப்டம்பர்",
    10: "அக்டோபர்",
    11: "நவம்பர்",
    12: "டிசம்பர்",
}

# Color Palette — Royal Midnight Navy & Sacred Vedic Gold
C_BG_DEEP = colors.HexColor("#080F1E")
C_BG_NAVY = colors.HexColor("#0F1A33")
C_CARD_BG = colors.HexColor("#13203D")
C_CARD_ALT = colors.HexColor("#182748")
C_CARD_WARM = colors.HexColor("#1B2336")
C_BORDER_SUBTLE = colors.HexColor("#26395E")
C_BORDER_GOLD = colors.HexColor("#C59B27")
C_GOLD_BRIGHT = colors.HexColor("#F4CE6A")
C_GOLD_PRIMARY = colors.HexColor("#D4AF37")
C_GOLD_DIM = colors.HexColor("#8A6D22")
C_TEXT_IVORY = colors.HexColor("#F8FAFC")
C_TEXT_SILVER = colors.HexColor("#CBD5E1")
C_TEXT_MUTED = colors.HexColor("#94A3B8")
C_TRACK_DARK = colors.HexColor("#223254")

# Sentiment Accents (fg, bg_tint, border)
SENTIMENT_COLORS: Dict[str, Tuple[colors.Color, colors.Color, colors.Color]] = {
    "Excellent": (
        colors.HexColor("#34D399"),
        colors.HexColor("#0B332A"),
        colors.HexColor("#10B981"),
    ),
    "Favorable": (
        colors.HexColor("#38BDF8"),
        colors.HexColor("#0D2B42"),
        colors.HexColor("#0EA5E9"),
    ),
    "Mixed": (
        colors.HexColor("#FBBF24"),
        colors.HexColor("#38280B"),
        colors.HexColor("#D97706"),
    ),
    "Challenging": (
        colors.HexColor("#FB7185"),
        colors.HexColor("#3D1521"),
        colors.HexColor("#E11D48"),
    ),
}

ASPECT_COLORS: Dict[str, colors.Color] = {
    "career": colors.HexColor("#60A5FA"),
    "finance": colors.HexColor("#F4CE6A"),
    "love": colors.HexColor("#F472B6"),
    "health": colors.HexColor("#34D399"),
    "travel": colors.HexColor("#A78BFA"),
}


def format_tamil_date_prefix(date_str: str) -> str:
    """Formats YYYY-MM-DD into '10 நவம்பர் 2026' without weekday."""
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            year = parts[0]
            month = int(parts[1])
            day = int(parts[2])
            month_name = MONTHS_TA.get(month, parts[1])
            return f"{day} {month_name} {year}"
    except Exception:
        pass
    return date_str


def format_tamil_date(date_str: str, day_ta: str) -> str:
    """Formats YYYY-MM-DD into '10 நவம்பர் 2026 – செவ்வாய்க்கிழமை'."""
    return f"{format_tamil_date_prefix(date_str)} – {day_ta}"


def clean_brief_ta(text: str) -> str:
    """Strips sign prefix (e.g., 'மேஷம் (8-ம் இடத்தில்...):') from brief statement."""
    if not text:
        return ""
    cleaned = re.sub(r"^.*?\):\s*", "", text).strip(" \"'")
    return cleaned or text


def format_aspect_text_ta(insight: str, rec: str) -> str:
    """Cleans technical KP jargon and combines insight and key recommendation into readable Tamil."""
    clean = re.sub(
        r"(?:KP\s*பாவகங்கள்|(?:\d+(?:\s*அல்லது\s*\d+)?|\[[\d,\s]+\]|\{houses\}|\d+(?:,\s*\d+)*)-ம்\s*பாவக[^.;]*[.;]?)",
        "",
        insight or "",
        flags=re.IGNORECASE,
    )
    clean = re.sub(r"\{houses\}", "", clean)
    clean = re.sub(r",\s*உப-அதிபதியின் ஆதிக்கத்தால்", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    if len(clean) < 35 and rec:
        rec_short = rec.split(";")[0].strip().rstrip(".")
        if rec_short:
            clean = f"{clean.rstrip('.')}. {rec_short}." if clean else f"{rec_short}."
    return clean or rec or insight


def _to_tamil_planet(name: str) -> str:
    return PLANET_NAMES_TA.get(name, name)


def _to_tamil_sign(name: str) -> str:
    return SIGN_NAMES_TA.get(name, name)


def _to_tamil_star(name: str) -> str:
    return STAR_NAMES_TA.get(name, name)


# ---------------------------------------------------------------------------
# HarfBuzz OpenType Shaping + Cached Glyph Outline Renderer
# ---------------------------------------------------------------------------

_RENDER_LOCK = threading.Lock()
_HB_FONTS: Dict[str, Tuple[hb.Face, hb.Font, int, set[int]]] = {}
_GLYPH_OUTLINE_CACHE: Dict[Tuple[str, int], List[Tuple[Any, ...]]] = {}
_CIRCULAR_LOGO_BYTES: Optional[bytes] = None


def _get_hb_font(font_key: str) -> Tuple[hb.Face, hb.Font, int, set[int]]:
    """Loads and caches a HarfBuzz Face, Font, UPEM, and supported Unicode codepoints."""
    cached = _HB_FONTS.get(font_key)
    if cached is not None:
        return cached

    if font_key == "bold" and NOTO_BOLD_PATH.is_file():
        font_path = NOTO_BOLD_PATH
    elif NOTO_REGULAR_PATH.is_file():
        font_path = NOTO_REGULAR_PATH
    else:
        fallback = next(FONTS_DIR.glob("*.ttf"), None)
        if not fallback:
            raise FileNotFoundError(f"No TTF font files found in {FONTS_DIR}")
        font_path = fallback

    blob = hb.Blob.from_file_path(str(font_path))
    face = hb.Face(blob)
    font = hb.Font(face)
    upem = face.upem or 1000
    font.scale = (upem, upem)
    if hasattr(face, "unicodes"):
        unicodes = set(face.unicodes)
    else:
        from fontTools.ttLib import TTFont

        with TTFont(str(font_path)) as tt:
            unicodes = set((tt.getBestCmap() or {}).keys())
    entry = (face, font, upem, unicodes)
    _HB_FONTS[font_key] = entry
    return entry


def _sanitize_for_font(text: str, unicodes: set[int]) -> str:
    """Keeps characters covered by the TTF cmap (replacing missing symbols cleanly)."""
    if not text:
        return ""
    out: List[str] = []
    for ch in text:
        cp = ord(ch)
        if cp in unicodes or ch in (" ", "\t"):
            out.append(ch)
        elif ch in ("\u2013", "\u2014"):
            out.append("-" if ord("-") in unicodes else " ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _shape_run(text: str, font_key: str = "regular") -> Tuple[List[Tuple[int, int, int, int]], int, str]:
    """Shapes text via HarfBuzz OpenType GSUB/GPOS and returns (glyph_tuples, total_advance, clean_text)."""
    _, font, upem, unicodes = _get_hb_font(font_key)
    clean = _sanitize_for_font(text, unicodes)
    if not clean:
        return [], 0, ""

    buf = hb.Buffer()
    buf.add_str(clean)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    glyphs: List[Tuple[int, int, int, int]] = []
    total_adv = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((info.codepoint, pos.x_advance, pos.x_offset, pos.y_offset))
        total_adv += pos.x_advance
    return glyphs, total_adv, clean


def _get_glyph_outline(font_key: str, gid: int) -> List[Tuple[Any, ...]]:
    """Extracts and caches normalized vector drawing commands for a single glyph ID."""
    cache_key = (font_key, gid)
    cached = _GLYPH_OUTLINE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    _, font, _, _ = _get_hb_font(font_key)
    ops: List[Tuple[Any, ...]] = []
    df = hb.DrawFuncs()
    df.set_move_to_func(lambda x, y, c: c.append(("M", x, y)))
    df.set_line_to_func(lambda x, y, c: c.append(("L", x, y)))
    df.set_quadratic_to_func(lambda cx, cy, x, y, c: c.append(("Q", cx, cy, x, y)))
    df.set_cubic_to_func(lambda c1x, c1y, c2x, c2y, x, y, c: c.append(("C", c1x, c1y, c2x, c2y, x, y)))
    df.set_close_path_func(lambda c: c.append(("Z",)))

    if hasattr(font, "draw_glyph"):
        font.draw_glyph(gid, df, ops)
    else:
        df.draw_glyph(font, gid, ops)

    _GLYPH_OUTLINE_CACHE[cache_key] = ops
    return ops


def measure_shaped_width(text: str, font_key: str = "regular", font_size: float = 10.0) -> float:
    """Measures exact rendered width in points using HarfBuzz glyph advances."""
    with _RENDER_LOCK:
        _, _, upem, _ = _get_hb_font(font_key)
        _, total_adv, _ = _shape_run(text, font_key=font_key)
        return total_adv * (font_size / upem)


def wrap_shaped_text(
    text: str,
    font_key: str,
    font_size: float,
    max_width: float,
    max_lines: Optional[int] = None,
    ellipsis: bool = True,
) -> List[str]:
    """Wraps Tamil/English text strictly by HarfBuzz measured widths."""
    words = (text or "").strip().split()
    if not words:
        return []

    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if measure_shaped_width(candidate, font_key=font_key, font_size=font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)

    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if ellipsis and lines:
            last = lines[-1]
            suffix = "..."
            while last and measure_shaped_width(last + suffix, font_key=font_key, font_size=font_size) > max_width:
                if " " in last:
                    last = last.rsplit(" ", 1)[0]
                else:
                    last = last[:-1]
            lines[-1] = (last.rstrip(".,;: ") + suffix) if last else suffix
    return lines


def draw_shaped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font_key: str = "regular",
    font_size: float = 10.0,
    color: colors.Color = C_TEXT_IVORY,
    align: str = "left",
) -> float:
    """Draws OpenType-shaped text onto a ReportLab canvas using HarfBuzz glyph outlines.

    Returns the rendered width in points.
    """
    with _RENDER_LOCK:
        _, _, upem, _ = _get_hb_font(font_key)
        glyphs, total_adv, _ = _shape_run(text, font_key=font_key)
        if not glyphs:
            return 0.0

        scale = font_size / upem
        total_w = total_adv * scale

        cursor_x = x
        if align == "center":
            cursor_x -= total_w / 2.0
        elif align == "right":
            cursor_x -= total_w

        path = c.beginPath()
        pen_x = 0.0
        for gid, x_adv, x_off, y_off in glyphs:
            ops = _get_glyph_outline(font_key, gid)
            gx = cursor_x + (pen_x + x_off) * scale
            gy = y + y_off * scale
            cur_x = 0.0
            cur_y = 0.0
            for op in ops:
                kind = op[0]
                if kind == "M":
                    cur_x, cur_y = op[1], op[2]
                    path.moveTo(gx + cur_x * scale, gy + cur_y * scale)
                elif kind == "L":
                    cur_x, cur_y = op[1], op[2]
                    path.lineTo(gx + cur_x * scale, gy + cur_y * scale)
                elif kind == "Q":
                    cx, cy, nx, ny = op[1], op[2], op[3], op[4]
                    c1x = cur_x + (2.0 / 3.0) * (cx - cur_x)
                    c1y = cur_y + (2.0 / 3.0) * (cy - cur_y)
                    c2x = nx + (2.0 / 3.0) * (cx - nx)
                    c2y = ny + (2.0 / 3.0) * (cy - ny)
                    path.curveTo(
                        gx + c1x * scale,
                        gy + c1y * scale,
                        gx + c2x * scale,
                        gy + c2y * scale,
                        gx + nx * scale,
                        gy + ny * scale,
                    )
                    cur_x, cur_y = nx, ny
                elif kind == "C":
                    path.curveTo(
                        gx + op[1] * scale,
                        gy + op[2] * scale,
                        gx + op[3] * scale,
                        gy + op[4] * scale,
                        gx + op[5] * scale,
                        gy + op[6] * scale,
                    )
                    cur_x, cur_y = op[5], op[6]
                elif kind == "Z":
                    path.close()
            pen_x += x_adv

        c.saveState()
        c.setFillColor(color)
        # fillMode=0 selects PDF non-zero winding operator ('f'), matching TrueType contour orientation
        c.drawPath(path, stroke=0, fill=1, fillMode=0)
        c.restoreState()
        return total_w


# ---------------------------------------------------------------------------
# Vector Graphic Primitives (Logo, Zodiac Emblems, Stars, Gauges, Bars)
# ---------------------------------------------------------------------------

def _get_circular_logo_reader() -> Optional[ImageReader]:
    """Loads app/assets/logo.png masked cleanly into a circle."""
    global _CIRCULAR_LOGO_BYTES
    if not LOGO_PATH.is_file():
        return None
    if _CIRCULAR_LOGO_BYTES is None:
        with Image.open(LOGO_PATH) as img:
            rgba = img.convert("RGBA")
            size = min(rgba.size)
            left = (rgba.width - size) // 2
            top = (rgba.height - size) // 2
            cropped = rgba.crop((left, top, left + size, top + size)).resize(
                (256, 256), Image.Resampling.LANCZOS
            )
            mask = Image.new("L", (256, 256), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((2, 2, 254, 254), fill=255)
            cropped.putalpha(mask)
            buf = BytesIO()
            cropped.save(buf, format="PNG")
            _CIRCULAR_LOGO_BYTES = buf.getvalue()
    return ImageReader(BytesIO(_CIRCULAR_LOGO_BYTES))


def _draw_canvas_backdrop(c: canvas.Canvas) -> None:
    """Draws the signature Royal Midnight Navy & Sacred Gold card background + frame."""
    c.saveState()
    c.setFillColor(C_BG_DEEP)
    c.rect(0, 0, CARD_PT_WIDTH, CARD_PT_HEIGHT, stroke=0, fill=1)

    # Subtle layered cosmic depth bands & ambient glows
    c.setFillColor(C_BG_NAVY)
    c.setFillAlpha(0.72)
    c.circle(CARD_PT_WIDTH * 0.85, CARD_PT_HEIGHT * 0.86, 260, stroke=0, fill=1)
    c.circle(CARD_PT_WIDTH * 0.14, CARD_PT_HEIGHT * 0.16, 230, stroke=0, fill=1)

    # Sacred mandala corner rings (subtle gold watermark geometry)
    c.setStrokeColor(C_GOLD_PRIMARY)
    c.setStrokeAlpha(0.11)
    c.setLineWidth(1.0)
    for radius in (95, 130, 165):
        c.circle(CARD_PT_WIDTH * 0.88, CARD_PT_HEIGHT * 0.88, radius, stroke=1, fill=0)
    for radius in (75, 110):
        c.circle(CARD_PT_WIDTH * 0.10, CARD_PT_HEIGHT * 0.12, radius, stroke=1, fill=0)

    # Double outer gold border frame
    c.setStrokeAlpha(0.85)
    c.setStrokeColor(C_BORDER_GOLD)
    c.setLineWidth(1.1)
    c.roundRect(10, 10, CARD_PT_WIDTH - 20, CARD_PT_HEIGHT - 20, 14, stroke=1, fill=0)

    c.setStrokeAlpha(0.32)
    c.setLineWidth(0.6)
    c.roundRect(14, 14, CARD_PT_WIDTH - 28, CARD_PT_HEIGHT - 28, 11, stroke=1, fill=0)
    c.restoreState()


def _draw_brand_header(
    c: canvas.Canvas,
    subtitle_ta: str,
    date_label_ta: str,
) -> None:
    """Draws the top GAI branding strip with logo, title, and Tamil date pill."""
    # Circular logo with gold halo
    logo_cx, logo_cy, logo_r = 40.0, CARD_PT_HEIGHT - 40.0, 17.5
    c.saveState()
    c.setFillColor(C_CARD_BG)
    c.setStrokeColor(C_GOLD_BRIGHT)
    c.setLineWidth(1.2)
    c.circle(logo_cx, logo_cy, logo_r + 1.5, stroke=1, fill=1)
    reader = _get_circular_logo_reader()
    if reader is not None:
        c.drawImage(
            reader,
            logo_cx - logo_r,
            logo_cy - logo_r,
            width=logo_r * 2,
            height=logo_r * 2,
            mask="auto",
        )
    c.restoreState()

    draw_shaped_text(
        c,
        "Gokul's Astrological Insights",
        65.0,
        CARD_PT_HEIGHT - 36.0,
        font_key="bold",
        font_size=13.5,
        color=C_GOLD_BRIGHT,
    )
    draw_shaped_text(
        c,
        subtitle_ta,
        65.0,
        CARD_PT_HEIGHT - 51.0,
        font_key="regular",
        font_size=9.3,
        color=C_TEXT_SILVER,
    )

    # Right-aligned Tamil date pill
    pill_w = min(248.0, max(168.0, measure_shaped_width(date_label_ta, "bold", 8.5) + 22.0))
    pill_h = 22.0
    pill_x = CARD_PT_WIDTH - 22.0 - pill_w
    pill_y = CARD_PT_HEIGHT - 48.0
    c.saveState()
    c.setFillColor(C_CARD_ALT)
    c.setStrokeColor(C_GOLD_DIM)
    c.setLineWidth(0.8)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 11, stroke=1, fill=1)
    c.restoreState()

    draw_shaped_text(
        c,
        date_label_ta,
        pill_x + pill_w / 2.0,
        pill_y + 7.5,
        font_key="bold",
        font_size=8.6,
        color=C_TEXT_IVORY,
        align="center",
    )


def _draw_brand_footer(c: canvas.Canvas, right_label: str = "gai-astrology.com") -> None:
    """Draws the clean bottom signature bar."""
    c.saveState()
    c.setStrokeColor(C_BORDER_SUBTLE)
    c.setLineWidth(0.6)
    c.line(24, 34, CARD_PT_WIDTH - 24, 34)
    c.restoreState()

    draw_shaped_text(
        c,
        "Gokul Murugan  |  Thiruverkadu, Chennai",
        24.0,
        20.5,
        font_key="regular",
        font_size=8.3,
        color=C_TEXT_MUTED,
    )
    draw_shaped_text(
        c,
        right_label,
        CARD_PT_WIDTH - 24.0,
        20.5,
        font_key="bold",
        font_size=8.6,
        color=C_GOLD_PRIMARY,
        align="right",
    )


def _draw_zodiac_emblem(
    c: canvas.Canvas,
    rashi_id: int,
    cx: float,
    cy: float,
    radius: float,
    accent: colors.Color = C_GOLD_BRIGHT,
) -> None:
    """Draws a crisp vector zodiac glyph inside a celestial medallion."""
    c.saveState()
    c.setFillColor(C_BG_DEEP)
    c.setStrokeColor(accent)
    c.setLineWidth(1.3)
    c.circle(cx, cy, radius, stroke=1, fill=1)

    c.setStrokeAlpha(0.25)
    c.setLineWidth(0.6)
    c.circle(cx, cy, radius - 3.5, stroke=1, fill=0)

    c.setStrokeAlpha(1.0)
    c.setStrokeColor(accent)
    c.setFillColor(accent)
    c.setLineWidth(max(1.3, radius * 0.085))
    c.setLineCap(1)
    c.setLineJoin(1)

    s = radius * 0.46
    p = c.beginPath()

    if rashi_id == 1:  # Aries - Ram horns
        p.moveTo(cx, cy - s * 0.9)
        p.lineTo(cx, cy + s * 0.2)
        p.curveTo(cx, cy + s * 1.0, cx - s * 1.05, cy + s * 1.0, cx - s * 0.85, cy + s * 0.25)
        p.moveTo(cx, cy + s * 0.2)
        p.curveTo(cx, cy + s * 1.0, cx + s * 1.05, cy + s * 1.0, cx + s * 0.85, cy + s * 0.25)
    elif rashi_id == 2:  # Taurus - Circle & horns
        c.drawPath(p, stroke=1, fill=0)
        c.circle(cx, cy - s * 0.25, s * 0.52, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(cx - s * 0.72, cy + s * 0.82)
        p.curveTo(cx - s * 0.55, cy + s * 0.22, cx + s * 0.55, cy + s * 0.22, cx + s * 0.72, cy + s * 0.82)
    elif rashi_id == 3:  # Gemini - Twin pillars
        p.moveTo(cx - s * 0.7, cy + s * 0.78)
        p.curveTo(cx - s * 0.2, cy + s * 0.55, cx + s * 0.2, cy + s * 0.55, cx + s * 0.7, cy + s * 0.78)
        p.moveTo(cx - s * 0.7, cy - s * 0.78)
        p.curveTo(cx - s * 0.2, cy - s * 0.55, cx + s * 0.2, cy - s * 0.55, cx + s * 0.7, cy - s * 0.78)
        p.moveTo(cx - s * 0.3, cy - s * 0.62)
        p.lineTo(cx - s * 0.3, cy + s * 0.62)
        p.moveTo(cx + s * 0.3, cy - s * 0.62)
        p.lineTo(cx + s * 0.3, cy + s * 0.62)
    elif rashi_id == 4:  # Cancer - Twin spirals
        c.circle(cx - s * 0.42, cy + s * 0.35, s * 0.28, stroke=1, fill=0)
        c.circle(cx + s * 0.42, cy - s * 0.35, s * 0.28, stroke=1, fill=0)
        p.moveTo(cx - s * 0.5, cy + s * 0.63)
        p.curveTo(cx + s * 0.1, cy + s * 0.78, cx + s * 0.65, cy + s * 0.55, cx + s * 0.78, cy + s * 0.22)
        p.moveTo(cx + s * 0.5, cy - s * 0.63)
        p.curveTo(cx - s * 0.1, cy - s * 0.78, cx - s * 0.65, cy - s * 0.55, cx - s * 0.78, cy - s * 0.22)
    elif rashi_id == 5:  # Leo - Lion loop & tail
        c.circle(cx - s * 0.48, cy - s * 0.18, s * 0.30, stroke=1, fill=0)
        p.moveTo(cx - s * 0.22, cy)
        p.curveTo(cx - s * 0.1, cy + s * 0.95, cx + s * 0.75, cy + s * 0.85, cx + s * 0.45, cy - s * 0.2)
        p.curveTo(cx + s * 0.30, cy - s * 0.75, cx + s * 0.65, cy - s * 0.85, cx + s * 0.88, cy - s * 0.55)
    elif rashi_id == 6:  # Virgo - M with cross loop
        p.moveTo(cx - s * 0.78, cy + s * 0.65)
        p.lineTo(cx - s * 0.78, cy - s * 0.55)
        p.moveTo(cx - s * 0.78, cy + s * 0.32)
        p.curveTo(cx - s * 0.55, cy + s * 0.75, cx - s * 0.25, cy + s * 0.75, cx - s * 0.25, cy + s * 0.2)
        p.lineTo(cx - s * 0.25, cy - s * 0.55)
        p.moveTo(cx - s * 0.25, cy + s * 0.32)
        p.curveTo(cx, cy + s * 0.75, cx + s * 0.30, cy + s * 0.75, cx + s * 0.30, cy + s * 0.2)
        p.lineTo(cx + s * 0.30, cy - s * 0.65)
        p.curveTo(cx + s * 0.55, cy - s * 0.82, cx + s * 0.82, cy - s * 0.2, cx + s * 0.30, cy + s * 0.18)
    elif rashi_id == 7:  # Libra - Balanced scales
        p.moveTo(cx - s * 0.85, cy - s * 0.52)
        p.lineTo(cx + s * 0.85, cy - s * 0.52)
        p.moveTo(cx - s * 0.85, cy - s * 0.12)
        p.lineTo(cx - s * 0.42, cy - s * 0.12)
        p.curveTo(cx - s * 0.48, cy + s * 0.65, cx + s * 0.48, cy + s * 0.65, cx + s * 0.42, cy - s * 0.12)
        p.lineTo(cx + s * 0.85, cy - s * 0.12)
    elif rashi_id == 8:  # Scorpio - M with upward sting arrow
        p.moveTo(cx - s * 0.82, cy + s * 0.62)
        p.lineTo(cx - s * 0.82, cy - s * 0.55)
        p.moveTo(cx - s * 0.82, cy + s * 0.28)
        p.curveTo(cx - s * 0.55, cy + s * 0.75, cx - s * 0.26, cy + s * 0.75, cx - s * 0.26, cy + s * 0.2)
        p.lineTo(cx - s * 0.26, cy - s * 0.55)
        p.moveTo(cx - s * 0.26, cy + s * 0.28)
        p.curveTo(cx, cy + s * 0.75, cx + s * 0.30, cy + s * 0.75, cx + s * 0.30, cy + s * 0.2)
        p.lineTo(cx + s * 0.30, cy - s * 0.45)
        p.curveTo(cx + s * 0.30, cy - s * 0.78, cx + s * 0.65, cy - s * 0.72, cx + s * 0.84, cy - s * 0.38)
        p.lineTo(cx + s * 0.84, cy - s * 0.68)
        p.moveTo(cx + s * 0.84, cy - s * 0.38)
        p.lineTo(cx + s * 0.56, cy - s * 0.42)
    elif rashi_id == 9:  # Sagittarius - Diagonal bow arrow
        p.moveTo(cx - s * 0.68, cy - s * 0.68)
        p.lineTo(cx + s * 0.68, cy + s * 0.68)
        p.moveTo(cx + s * 0.12, cy + s * 0.68)
        p.lineTo(cx + s * 0.68, cy + s * 0.68)
        p.lineTo(cx + s * 0.68, cy + s * 0.12)
        p.moveTo(cx - s * 0.55, cy + s * 0.08)
        p.lineTo(cx + s * 0.08, cy - s * 0.55)
    elif rashi_id == 10:  # Capricorn - V with loop tail
        p.moveTo(cx - s * 0.75, cy + s * 0.62)
        p.lineTo(cx - s * 0.28, cy - s * 0.55)
        p.lineTo(cx + s * 0.20, cy + s * 0.52)
        p.curveTo(cx + s * 0.68, cy + s * 0.52, cx + s * 0.82, cy - s * 0.25, cx + s * 0.35, cy - s * 0.55)
        p.curveTo(cx + s * 0.08, cy - s * 0.72, cx + s * 0.65, cy - s * 0.85, cx + s * 0.84, cy - s * 0.55)
    elif rashi_id == 11:  # Aquarius - Twin waves
        for dy in (s * 0.28, -s * 0.28):
            p.moveTo(cx - s * 0.82, cy + dy - s * 0.12)
            p.lineTo(cx - s * 0.40, cy + dy + s * 0.16)
            p.lineTo(cx, cy + dy - s * 0.12)
            p.lineTo(cx + s * 0.40, cy + dy + s * 0.16)
            p.lineTo(cx + s * 0.82, cy + dy - s * 0.12)
    else:  # Pisces - Twin crescents & crossbar
        p.moveTo(cx - s * 0.68, cy + s * 0.74)
        p.curveTo(cx - s * 0.15, cy + s * 0.3, cx - s * 0.15, cy - s * 0.3, cx - s * 0.68, cy - s * 0.74)
        p.moveTo(cx + s * 0.68, cy + s * 0.74)
        p.curveTo(cx + s * 0.15, cy + s * 0.3, cx + s * 0.15, cy - s * 0.3, cx + s * 0.68, cy - s * 0.74)
        p.moveTo(cx - s * 0.78, cy)
        p.lineTo(cx + s * 0.78, cy)

    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def _draw_star(c: canvas.Canvas, cx: float, cy: float, outer_r: float, filled: bool, color: colors.Color) -> None:
    """Draws a crisp 5-pointed star."""
    inner_r = outer_r * 0.42
    p = c.beginPath()
    for i in range(10):
        angle = math.radians(90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        if i == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    p.close()

    c.saveState()
    if filled:
        c.setFillColor(color)
        c.setStrokeColor(color)
        c.setLineWidth(0.5)
        c.drawPath(p, stroke=1, fill=1)
    else:
        c.setFillColor(C_TRACK_DARK)
        c.setStrokeColor(C_TEXT_MUTED)
        c.setLineWidth(0.7)
        c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def _draw_stars_row(c: canvas.Canvas, x: float, y: float, stars: float, size: float = 5.5) -> float:
    """Draws 5 rating stars left-to-right and returns ending x coordinate."""
    earned = int(round(stars))
    cx = x + size
    for idx in range(5):
        _draw_star(c, cx, y, size, filled=(idx < earned), color=C_GOLD_BRIGHT)
        cx += size * 2.35
    return cx


def _draw_score_ring(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    radius: float,
    score: int,
    accent: colors.Color,
) -> None:
    """Draws a radial progress gauge with centered percentage text."""
    c.saveState()
    c.setStrokeColor(C_TRACK_DARK)
    c.setLineWidth(5.5)
    c.circle(cx, cy, radius, stroke=1, fill=0)

    # Progress arc clockwise from 12 o'clock
    pct = max(0, min(100, int(score)))
    if pct > 0:
        steps = max(8, int(48 * pct / 100))
        c.setStrokeColor(accent)
        c.setLineWidth(5.5)
        c.setLineCap(1)
        p = c.beginPath()
        for step in range(steps + 1):
            frac = (pct / 100.0) * (step / steps)
            angle = math.radians(90.0 - 360.0 * frac)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            if step == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    draw_shaped_text(
        c,
        f"{pct}%",
        cx,
        cy - 2.5,
        font_key="bold",
        font_size=14.5,
        color=C_TEXT_IVORY,
        align="center",
    )
    draw_shaped_text(
        c,
        "சாதகம்",
        cx,
        cy - 13.5,
        font_key="regular",
        font_size=6.8,
        color=C_TEXT_MUTED,
        align="center",
    )


def _draw_aspect_icon(c: canvas.Canvas, aspect_code: str, cx: float, cy: float, r: float, accent: colors.Color) -> None:
    """Draws a crisp vector icon inside a colored badge for each life aspect."""
    c.saveState()
    c.setFillColor(C_BG_DEEP)
    c.setStrokeColor(accent)
    c.setLineWidth(1.0)
    c.circle(cx, cy, r, stroke=1, fill=1)

    c.setStrokeColor(accent)
    c.setFillColor(accent)
    c.setLineWidth(1.2)
    c.setLineCap(1)
    c.setLineJoin(1)
    s = r * 0.48
    if aspect_code == "career":
        c.roundRect(cx - s, cy - s * 0.72, s * 2, s * 1.32, 1.5, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(cx - s * 0.42, cy + s * 0.6)
        p.lineTo(cx - s * 0.42, cy + s * 0.92)
        p.lineTo(cx + s * 0.42, cy + s * 0.92)
        p.lineTo(cx + s * 0.42, cy + s * 0.6)
        c.drawPath(p, stroke=1, fill=0)
    elif aspect_code == "finance":
        c.circle(cx, cy, s * 0.85, stroke=1, fill=0)
        c.circle(cx, cy, s * 0.30, stroke=0, fill=1)
    elif aspect_code == "love":
        p = c.beginPath()
        p.moveTo(cx, cy - s * 0.72)
        p.curveTo(cx - s * 1.1, cy - s * 0.05, cx - s * 0.95, cy + s * 0.85, cx, cy + s * 0.35)
        p.curveTo(cx + s * 0.95, cy + s * 0.85, cx + s * 1.1, cy - s * 0.05, cx, cy - s * 0.72)
        c.drawPath(p, stroke=1, fill=1)
    elif aspect_code == "health":
        c.setLineWidth(1.8)
        c.line(cx - s * 0.75, cy, cx + s * 0.75, cy)
        c.line(cx, cy - s * 0.75, cx, cy + s * 0.75)
    else:  # travel
        p = c.beginPath()
        p.moveTo(cx - s * 0.82, cy - s * 0.25)
        p.lineTo(cx + s * 0.85, cy + s * 0.55)
        p.lineTo(cx + s * 0.10, cy - s * 0.82)
        p.lineTo(cx - s * 0.05, cy - s * 0.15)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def _draw_progress_bar(c: canvas.Canvas, x: float, y: float, w: float, h: float, score: int, fill_color: colors.Color) -> None:
    """Draws a rounded progress track with score fill."""
    pct = max(0, min(100, int(score)))
    c.saveState()
    c.setFillColor(C_TRACK_DARK)
    c.roundRect(x, y, w, h, h / 2.0, stroke=0, fill=1)
    if pct > 0:
        fill_w = max(h, w * (pct / 100.0))
        c.setFillColor(fill_color)
        c.roundRect(x, y, fill_w, h, h / 2.0, stroke=0, fill=1)
    c.restoreState()


def _rasterize_pdf_to_png(pdf_bytes: bytes, scale: float = RASTER_SCALE) -> bytes:
    """Rasterizes a single-page ReportLab PDF buffer into an optimized RGB PNG using PyPDFium2."""
    doc = pdfium.PdfDocument(pdf_bytes)
    try:
        page = doc[0]
        try:
            bitmap = page.render(scale=scale)
            try:
                pil_img = bitmap.to_pil().convert("RGB")
                out = BytesIO()
                pil_img.save(out, format="PNG", optimize=True)
                return out.getvalue()
            finally:
                bitmap.close()
        finally:
            page.close()
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Public Card Generators
# ---------------------------------------------------------------------------

def render_rashi_daily_card_png(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
    slide_index: Optional[int] = None,
    total_slides: Optional[int] = None,
) -> bytes:
    """Renders a 1080x1350 branded Tamil KP Daily Raasi Palan PNG card for one Rashi."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_PT_WIDTH, CARD_PT_HEIGHT))
    c.setTitle(f"KP Daily Raasi Palan - {prediction.rashi_name_en} - {horoscope_data.date}")

    _draw_canvas_backdrop(c)
    date_label_ta = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    _draw_brand_header(c, "தினசரி ராசிபலன்  •  KP துல்லியக் கணிப்பு", date_label_ta)

    fg_accent, bg_tint, border_accent = SENTIMENT_COLORS.get(
        prediction.day_sentiment,
        SENTIMENT_COLORS["Mixed"],
    )
    sentiment_ta = SENTIMENT_MAP_TA.get(prediction.day_sentiment, prediction.day_sentiment)

    # 1. Hero Rashi Banner Card (y: 514..606)
    hx, hy, hw, hh = 22.0, 514.0, CARD_PT_WIDTH - 44.0, 92.0
    c.saveState()
    c.setFillColor(C_CARD_BG)
    c.setStrokeColor(C_BORDER_GOLD)
    c.setLineWidth(1.0)
    c.roundRect(hx, hy, hw, hh, 12, stroke=1, fill=1)
    c.restoreState()

    _draw_zodiac_emblem(c, prediction.rashi_id, hx + 42.0, hy + hh / 2.0, 27.0, accent=C_GOLD_BRIGHT)

    # Rashi Name + English Tag + Stars + Sentiment Pill
    title_x = hx + 82.0
    title_w = draw_shaped_text(
        c,
        prediction.rashi_name_ta,
        title_x,
        hy + 60.0,
        font_key="bold",
        font_size=21.0,
        color=C_TEXT_IVORY,
    )
    en_pill_x = title_x + title_w + 10.0
    en_text = prediction.rashi_name_en.upper()
    en_pill_w = max(56.0, measure_shaped_width(en_text, "bold", 8.5) + 16.0)
    c.saveState()
    c.setFillColor(C_CARD_ALT)
    c.setStrokeColor(C_GOLD_DIM)
    c.setLineWidth(0.7)
    c.roundRect(en_pill_x, hy + 59.0, en_pill_w, 17.5, 8.5, stroke=1, fill=1)
    c.restoreState()
    draw_shaped_text(
        c,
        en_text,
        en_pill_x + en_pill_w / 2.0,
        hy + 64.5,
        font_key="bold",
        font_size=8.5,
        color=C_GOLD_BRIGHT,
        align="center",
    )

    # Stars & Sentiment pill on second row
    stars_end_x = _draw_stars_row(c, title_x, hy + 41.0, prediction.daily_rating_stars, size=5.2)
    sent_pill_x = stars_end_x + 6.0
    sent_pill_w = max(96.0, measure_shaped_width(sentiment_ta, "bold", 8.8) + 18.0)
    c.saveState()
    c.setFillColor(bg_tint)
    c.setStrokeColor(border_accent)
    c.setLineWidth(0.8)
    c.roundRect(sent_pill_x, hy + 32.0, sent_pill_w, 18.0, 9.0, stroke=1, fill=1)
    c.restoreState()
    draw_shaped_text(
        c,
        sentiment_ta,
        sent_pill_x + sent_pill_w / 2.0,
        hy + 37.5,
        font_key="bold",
        font_size=8.8,
        color=fg_accent,
        align="center",
    )

    # Moon Transit Metadata Line
    moon_star_ta = _to_tamil_star(horoscope_data.moon_star_at_noon)
    sub_lord_ta = _to_tamil_planet(horoscope_data.moon_sub_lord_at_noon)
    day_lord_ta = _to_tamil_planet(horoscope_data.day_lord)
    draw_shaped_text(
        c,
        f"நட்சத்திரம்: {moon_star_ta}  •  உப-அதிபதி: {sub_lord_ta}  •  தின அதிபதி: {day_lord_ta}",
        title_x,
        hy + 14.5,
        font_key="regular",
        font_size=8.3,
        color=C_TEXT_MUTED,
    )

    # Score Gauge on the Right
    _draw_score_ring(c, hx + hw - 44.0, hy + hh / 2.0 + 1.0, 27.5, prediction.daily_score, fg_accent)

    # 2. General Summary Card (y: 432..504)
    bx, by, bw, bh = 22.0, 432.0, CARD_PT_WIDTH - 44.0, 72.0
    c.saveState()
    c.setFillColor(C_CARD_ALT)
    c.setStrokeColor(C_BORDER_SUBTLE)
    c.setLineWidth(0.8)
    c.roundRect(bx, by, bw, bh, 10, stroke=1, fill=1)
    c.setFillColor(C_GOLD_PRIMARY)
    c.roundRect(bx + 1.0, by + 10.0, 3.2, bh - 20.0, 1.5, stroke=0, fill=1)
    c.restoreState()

    draw_shaped_text(
        c,
        "இன்றைய பொதுப்பலன்",
        bx + 14.0,
        by + bh - 18.0,
        font_key="bold",
        font_size=10.2,
        color=C_GOLD_BRIGHT,
    )
    brief_lines = wrap_shaped_text(
        clean_brief_ta(prediction.brief_statement_ta),
        font_key="regular",
        font_size=9.6,
        max_width=bw - 28.0,
        max_lines=3,
    )
    line_y = by + bh - 34.5
    for line in brief_lines:
        draw_shaped_text(c, line, bx + 14.0, line_y, font_key="regular", font_size=9.6, color=C_TEXT_IVORY)
        line_y -= 14.0

    # 3. Five Life Aspects Section (y: 196..422)
    ax, ay, aw, ah = 22.0, 196.0, CARD_PT_WIDTH - 44.0, 226.0
    c.saveState()
    c.setFillColor(C_CARD_BG)
    c.setStrokeColor(C_BORDER_SUBTLE)
    c.setLineWidth(0.8)
    c.roundRect(ax, ay, aw, ah, 10, stroke=1, fill=1)
    c.restoreState()

    draw_shaped_text(
        c,
        "இன்றைய விரிவான பலன்கள்",
        ax + 14.0,
        ay + ah - 18.0,
        font_key="bold",
        font_size=10.2,
        color=C_GOLD_BRIGHT,
    )

    row_top = ay + ah - 28.0
    row_h = 37.5
    row_gap = 2.0
    for idx, aspect in enumerate(prediction.aspects[:5]):
        ry = row_top - idx * (row_h + row_gap) - row_h
        a_color = ASPECT_COLORS.get(aspect.aspect_code, C_GOLD_PRIMARY)

        c.saveState()
        c.setFillColor(C_CARD_ALT)
        c.roundRect(ax + 10.0, ry, aw - 20.0, row_h, 7, stroke=0, fill=1)
        c.restoreState()

        _draw_aspect_icon(c, aspect.aspect_code, ax + 27.0, ry + row_h / 2.0, 10.5, a_color)

        # Top row inside aspect: Name + Score% + Progress Bar
        text_x = ax + 44.0
        draw_shaped_text(
            c,
            aspect.aspect_name_tamil,
            text_x,
            ry + row_h - 14.0,
            font_key="bold",
            font_size=9.3,
            color=C_TEXT_IVORY,
        )

        bar_w = 88.0
        bar_x = ax + aw - 22.0 - bar_w
        _draw_progress_bar(c, bar_x, ry + row_h - 13.5, bar_w, 5.5, aspect.score, a_color)
        draw_shaped_text(
            c,
            f"{aspect.score}%",
            bar_x - 8.0,
            ry + row_h - 14.0,
            font_key="bold",
            font_size=9.3,
            color=a_color,
            align="right",
        )

        # Single crisp insight line underneath (prefer complete first sentence if full text exceeds 1 line)
        cleaned_insight = format_aspect_text_ta(aspect.insight_ta, aspect.key_recommendation_ta)
        insight_max_w = aw - 56.0
        if measure_shaped_width(cleaned_insight, "regular", 8.0) > insight_max_w and "." in cleaned_insight:
            first_sentence = cleaned_insight.split(".", 1)[0].strip() + "."
            if len(first_sentence) >= 18 and measure_shaped_width(first_sentence, "regular", 8.0) <= insight_max_w:
                cleaned_insight = first_sentence
        wrapped = wrap_shaped_text(
            cleaned_insight,
            font_key="regular",
            font_size=8.0,
            max_width=insight_max_w,
            max_lines=1,
        )
        if wrapped:
            draw_shaped_text(
                c,
                wrapped[0],
                text_x,
                ry + 7.5,
                font_key="regular",
                font_size=8.0,
                color=C_TEXT_SILVER,
            )

    # 4. Timing & Lucky Grid (y: 102..186)
    golden_times = (
        ", ".join(
            f"{w.start_time} – {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "golden"
        )
        or (prediction.golden_hour_window.replace(" - ", " – ") if prediction.golden_hour_window else "")
        or "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"
    )
    caution_times = (
        ", ".join(
            f"{w.start_time} – {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "caution"
        )
        or (prediction.caution_hour_window.replace(" - ", " – ") if prediction.caution_hour_window else "")
        or "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"
    )

    gap = 8.0
    half_w = (CARD_PT_WIDTH - 44.0 - gap) / 2.0
    time_y, time_h = 148.0, 38.0
    time_cards = [
        (22.0, "அதிர்ஷ்ட நேரம் (Golden Hours)", golden_times, colors.HexColor("#34D399"), colors.HexColor("#0A2D25"), colors.HexColor("#10B981")),
        (22.0 + half_w + gap, "கவனமான நேரம் (Caution)", caution_times, colors.HexColor("#FB7185"), colors.HexColor("#33141E"), colors.HexColor("#E11D48")),
    ]
    for tx, label, val, fg_c, bg_c, bd_c in time_cards:
        c.saveState()
        c.setFillColor(bg_c)
        c.setStrokeColor(bd_c)
        c.setLineWidth(0.75)
        c.roundRect(tx, time_y, half_w, time_h, 8, stroke=1, fill=1)
        c.restoreState()
        draw_shaped_text(c, label, tx + 11.0, time_y + time_h - 12.0, font_key="bold", font_size=8.1, color=fg_c)
        single_fit = measure_shaped_width(val, "bold", 8.4) <= (half_w - 22.0)
        if single_fit:
            draw_shaped_text(c, val, tx + 11.0, time_y + 8.5, font_key="bold", font_size=8.4, color=C_TEXT_IVORY)
        else:
            val_lines = wrap_shaped_text(val, "bold", 7.4, half_w - 20.0, max_lines=2)
            vy = time_y + 15.5 if len(val_lines) > 1 else time_y + 8.5
            for vline in val_lines:
                draw_shaped_text(c, vline, tx + 11.0, vy, font_key="bold", font_size=7.4, color=C_TEXT_IVORY)
                vy -= 9.5

    # Lucky Color / Number / Direction row (y: 102..140)
    lucky_y, lucky_h = 102.0, 38.0
    third_w = (CARD_PT_WIDTH - 44.0 - gap * 2) / 3.0
    lucky_color_short = prediction.lucky_color_ta.split("&")[0].strip() if prediction.lucky_color_ta else ""
    lucky_items = [
        ("அதிர்ஷ்ட நிறம்", lucky_color_short),
        ("அதிர்ஷ்ட எண்", str(prediction.lucky_number)),
        ("அதிர்ஷ்ட திசை", prediction.lucky_direction_ta),
    ]
    for i, (lbl, val) in enumerate(lucky_items):
        lx = 22.0 + i * (third_w + gap)
        c.saveState()
        c.setFillColor(C_CARD_ALT)
        c.setStrokeColor(C_BORDER_SUBTLE)
        c.setLineWidth(0.75)
        c.roundRect(lx, lucky_y, third_w, lucky_h, 8, stroke=1, fill=1)
        c.restoreState()
        draw_shaped_text(c, lbl, lx + third_w / 2.0, lucky_y + lucky_h - 13.5, font_key="regular", font_size=8.0, color=C_TEXT_MUTED, align="center")
        val_fit = wrap_shaped_text(val, "bold", 9.8, third_w - 14.0, max_lines=1)
        if val_fit:
            draw_shaped_text(c, val_fit[0], lx + third_w / 2.0, lucky_y + 8.5, font_key="bold", font_size=9.8, color=C_GOLD_BRIGHT, align="center")

    # 5. Daily Remedy Banner (y: 44..94)
    rx, ry, rw, rh = 22.0, 44.0, CARD_PT_WIDTH - 44.0, 50.0
    c.saveState()
    c.setFillColor(C_CARD_WARM)
    c.setStrokeColor(C_GOLD_DIM)
    c.setLineWidth(0.85)
    c.roundRect(rx, ry, rw, rh, 9, stroke=1, fill=1)
    c.restoreState()
    draw_shaped_text(c, "இன்றைய ஆலோசனை & பரிகாரம்", rx + 12.0, ry + rh - 14.5, font_key="bold", font_size=8.8, color=C_GOLD_BRIGHT)
    rem_lines = wrap_shaped_text(prediction.daily_remedy_ta, "regular", 8.6, rw - 24.0, max_lines=2)
    rem_y = ry + rh - 28.5
    for line in rem_lines:
        draw_shaped_text(c, line, rx + 12.0, rem_y, font_key="regular", font_size=8.6, color=C_TEXT_IVORY)
        rem_y -= 12.0

    right_lbl = f"ராசி {slide_index} / {total_slides}  •  gai-astrology.com" if slide_index and total_slides else "gai-astrology.com"
    _draw_brand_footer(c, right_label=right_lbl)
    c.showPage()
    c.save()
    return _rasterize_pdf_to_png(buf.getvalue())


def render_daily_overview_card_png(horoscope_data: KpDailyHoroscopeResponse) -> bytes:
    """Renders a 1080x1350 'Top 3 & All 12 Rashis Summary' Hero Card PNG."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_PT_WIDTH, CARD_PT_HEIGHT))
    c.setTitle(f"KP Daily Raasi Palan Overview - {horoscope_data.date}")

    _draw_canvas_backdrop(c)
    date_label_ta = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    _draw_brand_header(c, "இன்றைய 12 ராசிகளின் சாதக நிலை – சுருக்கம்", date_label_ta)

    # Transit Banner (y: 578..604)
    mx, my, mw, mh = 22.0, 578.0, CARD_PT_WIDTH - 44.0, 26.0
    c.saveState()
    c.setFillColor(C_CARD_ALT)
    c.setStrokeColor(C_BORDER_SUBTLE)
    c.setLineWidth(0.75)
    c.roundRect(mx, my, mw, mh, 8, stroke=1, fill=1)
    c.restoreState()

    moon_sign_ta = _to_tamil_sign(horoscope_data.moon_sign_at_noon)
    moon_star_ta = _to_tamil_star(horoscope_data.moon_star_at_noon)
    sub_lord_ta = _to_tamil_planet(horoscope_data.moon_sub_lord_at_noon)
    day_lord_ta = _to_tamil_planet(horoscope_data.day_lord)
    draw_shaped_text(
        c,
        f"சந்திர ராசி: {moon_sign_ta}  •  நட்சத்திரம்: {moon_star_ta}  •  உப-அதிபதி: {sub_lord_ta}  •  அதிபதி: {day_lord_ta}",
        mx + mw / 2.0,
        my + 9.0,
        font_key="bold",
        font_size=8.6,
        color=C_TEXT_SILVER,
        align="center",
    )

    # Top 3 Lucky Rashis Section (y: 462..568)
    draw_shaped_text(
        c,
        "இன்றைய அதிர்ஷ்ட ராசிகள் – டாப் 3",
        24.0,
        556.0,
        font_key="bold",
        font_size=10.8,
        color=C_GOLD_BRIGHT,
    )
    ranked = sorted(horoscope_data.predictions, key=lambda p: (-p.daily_score, p.rashi_id))[:3]
    podium_gap = 10.0
    podium_w = (CARD_PT_WIDTH - 44.0 - podium_gap * 2) / 3.0
    podium_y, podium_h = 460.0, 88.0
    medal_colors = [
        colors.HexColor("#F4CE6A"),
        colors.HexColor("#CBD5E1"),
        colors.HexColor("#D99B66"),
    ]
    for rank_idx, pred in enumerate(ranked):
        px = 22.0 + rank_idx * (podium_w + podium_gap)
        medal_c = medal_colors[rank_idx]
        c.saveState()
        c.setFillColor(C_CARD_WARM if rank_idx == 0 else C_CARD_BG)
        c.setStrokeColor(medal_c)
        c.setLineWidth(1.1 if rank_idx == 0 else 0.85)
        c.roundRect(px, podium_y, podium_w, podium_h, 10, stroke=1, fill=1)
        c.restoreState()

        # Rank pill
        c.saveState()
        c.setFillColor(medal_c)
        c.roundRect(px + 10.0, podium_y + podium_h - 21.0, 26.0, 14.0, 7.0, stroke=0, fill=1)
        c.restoreState()
        draw_shaped_text(c, f"#{rank_idx + 1}", px + 23.0, podium_y + podium_h - 17.5, font_key="bold", font_size=8.2, color=C_BG_DEEP, align="center")

        _draw_zodiac_emblem(c, pred.rashi_id, px + podium_w - 24.0, podium_y + podium_h - 22.0, 13.5, accent=medal_c)

        draw_shaped_text(c, pred.rashi_name_ta, px + 10.0, podium_y + 44.0, font_key="bold", font_size=12.5, color=C_TEXT_IVORY)
        draw_shaped_text(c, f"{pred.daily_score}%", px + 10.0, podium_y + 22.0, font_key="bold", font_size=16.5, color=medal_c)
        _draw_stars_row(c, px + 52.0, podium_y + 27.0, pred.daily_rating_stars, size=3.8)
        gh = pred.golden_hour_window.split(",")[0].replace(" - ", "–").strip() if pred.golden_hour_window else "-"
        draw_shaped_text(c, f"நேரம்: {gh}", px + 10.0, podium_y + 8.0, font_key="regular", font_size=7.4, color=C_TEXT_MUTED)

    # All 12 Rashis 3x4 Scorecard Grid (y: 80..448)
    draw_shaped_text(
        c,
        "12 ராசிகள் இன்றைய மதிப்பெண்",
        24.0,
        438.0,
        font_key="bold",
        font_size=10.8,
        color=C_GOLD_BRIGHT,
    )

    cols = 3
    col_gap = 8.0
    row_gap = 8.0
    grid_w = CARD_PT_WIDTH - 44.0
    cell_w = (grid_w - col_gap * (cols - 1)) / cols
    cell_h = 80.0
    grid_top = 428.0

    for idx, pred in enumerate(horoscope_data.predictions[:12]):
        row = idx // cols
        col = idx % cols
        cx = 22.0 + col * (cell_w + col_gap)
        cy = grid_top - (row + 1) * cell_h - row * row_gap

        fg_c, _, _ = SENTIMENT_COLORS.get(pred.day_sentiment, SENTIMENT_COLORS["Mixed"])
        short_sent = SENTIMENT_SHORT_TA.get(pred.day_sentiment, pred.day_sentiment)

        c.saveState()
        c.setFillColor(C_CARD_BG)
        c.setStrokeColor(C_BORDER_SUBTLE)
        c.setLineWidth(0.75)
        c.roundRect(cx, cy, cell_w, cell_h, 9, stroke=1, fill=1)
        c.restoreState()

        _draw_zodiac_emblem(c, pred.rashi_id, cx + 22.0, cy + cell_h - 22.0, 12.5, accent=fg_c)
        draw_shaped_text(c, pred.rashi_name_ta, cx + 40.0, cy + cell_h - 21.0, font_key="bold", font_size=10.8, color=C_TEXT_IVORY)
        draw_shaped_text(c, pred.rashi_name_en.upper(), cx + 40.0, cy + cell_h - 32.0, font_key="regular", font_size=7.0, color=C_TEXT_MUTED)

        draw_shaped_text(c, f"{pred.daily_score}%", cx + 12.0, cy + 24.0, font_key="bold", font_size=13.5, color=fg_c)
        draw_shaped_text(c, short_sent, cx + cell_w - 10.0, cy + 25.5, font_key="bold", font_size=7.8, color=fg_c, align="right")

        _draw_progress_bar(c, cx + 12.0, cy + 12.0, cell_w - 24.0, 4.5, pred.daily_score, fg_c)

    # Bottom CTA pill (y: 44..70)
    cta_x, cta_y, cta_w, cta_h = 22.0, 44.0, CARD_PT_WIDTH - 44.0, 26.0
    c.saveState()
    c.setFillColor(C_CARD_WARM)
    c.setStrokeColor(C_GOLD_PRIMARY)
    c.setLineWidth(0.8)
    c.roundRect(cta_x, cta_y, cta_w, cta_h, 8, stroke=1, fill=1)
    c.restoreState()
    draw_shaped_text(
        c,
        "ஒவ்வொரு ராசியின் முழுப் பலன், அதிர்ஷ்ட நேரம் & பரிகாரங்களை அடுத்த படங்களில் காண்க",
        cta_x + cta_w / 2.0,
        cta_y + 9.0,
        font_key="bold",
        font_size=8.4,
        color=C_GOLD_BRIGHT,
        align="center",
    )

    _draw_brand_footer(c, right_label="KP Daily Raasi Palan  •  gai-astrology.com")
    c.showPage()
    c.save()
    return _rasterize_pdf_to_png(buf.getvalue())
