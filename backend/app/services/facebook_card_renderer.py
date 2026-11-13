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

SOCIAL_ASSETS_DIR = ASSETS_DIR / "social"
PRISTINE_BASE_CANVAS_PATH = SOCIAL_ASSETS_DIR / "pristine_navy_gold_base_1080.png"

RASHI_GEMS_TA: Dict[int, Tuple[str, str]] = {
    1: ("பவளம்", "செவ்வாய் பலம் பெற அணியலாம்"),
    2: ("வைரம்", "சுக்கிர பலம் பெற அணியலாம்"),
    3: ("மரகதம்", "புதன் பலம் பெற அணியலாம்"),
    4: ("முத்து", "சந்திர பலம் பெற அணியலாம்"),
    5: ("மாணிக்கம்", "சூரிய பலம் பெற அணியலாம்"),
    6: ("மரகதம்", "புதன் பலம் பெற அணியலாம்"),
    7: ("வைரம்", "சுக்கிர பலம் பெற அணியலாம்"),
    8: ("பவளம்", "செவ்வாய் பலம் பெற அணியலாம்"),
    9: ("புஷ்பராகம்", "குரு பலம் பெற அணியலாம்"),
    10: ("நீலம்", "சனி பலம் பெற அணியலாம்"),
    11: ("நீலம்", "சனி பலம் பெற அணியலாம்"),
    12: ("புஷ்பராகம்", "குரு பலம் பெற அணியலாம்"),
}

SIGN_LORDS_TA: Dict[int, str] = {
    1: "செவ்வாய்",
    2: "சுக்கிரன்",
    3: "புதன்",
    4: "சந்திரன்",
    5: "சூரியன்",
    6: "புதன்",
    7: "சுக்கிரன்",
    8: "செவ்வாய்",
    9: "குரு",
    10: "சனி",
    11: "சனி",
    12: "குரு",
}

DEPARTMENT_BAR_COLORS = [
    colors.HexColor("#38BDF8"),  # Blue
    colors.HexColor("#FACC15"),  # Yellow
    colors.HexColor("#F472B6"),  # Pink
    colors.HexColor("#34D399"),  # Green
    colors.HexColor("#A78BFA"),  # Purple
]


def render_rashi_daily_card_png(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
    slide_index: Optional[int] = None,
    total_slides: Optional[int] = None,
) -> bytes:
    """Renders the EXACT approved 1080x1350 card matching user's finalized image 100%."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_PT_WIDTH, CARD_PT_HEIGHT))
    c.setTitle(f"KP Daily Raasi Palan - {prediction.rashi_name_en} - {horoscope_data.date}")

    def pt_x(px: float) -> float:
        return px * (CARD_PT_WIDTH / 1080.0)

    def pt_y(py: float) -> float:
        return (1350.0 - py) * (CARD_PT_HEIGHT / 1350.0)

    # 1. Base Navy Background
    c.saveState()
    c.setFillColor(colors.HexColor("#030811"))
    c.rect(0, 0, CARD_PT_WIDTH, CARD_PT_HEIGHT, stroke=0, fill=1)

    c.setFillColor(colors.HexColor("#0D2544"))
    c.circle(CARD_PT_WIDTH * 0.5, CARD_PT_HEIGHT * 0.85, 200, stroke=0, fill=1)
    c.circle(CARD_PT_WIDTH * 0.15, CARD_PT_HEIGHT * 0.15, 150, stroke=0, fill=1)

    # Outer Gold Frame
    c.setStrokeColor(colors.HexColor("#D4AF37"))
    c.setLineWidth(3.0)
    c.roundRect(pt_x(12), pt_y(1338), pt_x(1056), pt_y(12), 16, stroke=1, fill=0)

    c.setStrokeColor(colors.HexColor("#F6D365"))
    c.setLineWidth(1.0)
    c.roundRect(pt_x(20), pt_y(1330), pt_x(1040), pt_y(20), 12, stroke=1, fill=0)
    c.restoreState()

    # 2. HEADER
    # Left: Logo
    logo_cx, logo_cy, logo_r = pt_x(105), pt_y(88), pt_x(65)
    c.saveState()
    c.setFillColor(colors.HexColor("#020B18"))
    c.setStrokeColor(colors.HexColor("#FFD700"))
    c.setLineWidth(2.2)
    c.circle(logo_cx, logo_cy, logo_r, stroke=1, fill=1)
    logo_file = SOCIAL_ASSETS_DIR / "logo_g.jpg"
    if logo_file.is_file():
        c.drawImage(ImageReader(str(logo_file)), logo_cx - logo_r + 2, logo_cy - logo_r + 2, width=(logo_r - 2) * 2, height=(logo_r - 2) * 2, mask="auto")
    elif LOGO_PATH.is_file():
        c.drawImage(ImageReader(str(LOGO_PATH)), logo_cx - logo_r + 2, logo_cy - logo_r + 2, width=(logo_r - 2) * 2, height=(logo_r - 2) * 2, mask="auto")
    c.restoreState()

    # Center: Company Title & Big WhatsApp Pill
    draw_shaped_text(
        c,
        "Gokul's Astrological Insights",
        CARD_PT_WIDTH / 2.0,
        pt_y(62),
        font_key="bold",
        font_size=19.0,
        color=colors.HexColor("#FFD700"),
        align="center",
    )

    wa_w, wa_h = pt_x(650), pt_x(52)
    wa_x = (CARD_PT_WIDTH - wa_w) / 2.0
    wa_y = pt_y(125)
    c.saveState()
    c.setFillColor(colors.HexColor("#092013"))
    c.setStrokeColor(colors.HexColor("#25D366"))
    c.setLineWidth(1.8)
    c.roundRect(wa_x, wa_y, wa_w, wa_h, wa_h / 2.0, stroke=1, fill=1)
    c.restoreState()

    draw_shaped_text(
        c,
        "வாட்ஸ்அப் / தொடர்புக்கு: 9444 55 9071",
        CARD_PT_WIDTH / 2.0,
        wa_y + 9.5,
        font_key="bold",
        font_size=11.5,
        color=colors.HexColor("#FFFFFF"),
        align="center",
    )

    # Right: Photo
    photo_cx, photo_cy, photo_r = pt_x(975), pt_y(88), pt_x(65)
    c.saveState()
    c.setFillColor(colors.HexColor("#020B18"))
    c.setStrokeColor(colors.HexColor("#FFD700"))
    c.setLineWidth(2.2)
    c.circle(photo_cx, photo_cy, photo_r, stroke=1, fill=1)
    founder_file = SOCIAL_ASSETS_DIR / "founder_portrait.jpg"
    if founder_file.is_file():
        c.drawImage(ImageReader(str(founder_file)), photo_cx - photo_r + 2, photo_cy - photo_r + 2, width=(photo_r - 2) * 2, height=(photo_r - 2) * 2, mask="auto")
    c.restoreState()

    # 3. DATE RIBBON
    date_parts = horoscope_data.date.split("-")
    date_ddmmyyyy = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}" if len(date_parts) == 3 else horoscope_data.date
    date_title = f"{date_ddmmyyyy} தினசரி ராசிபலன்கள்"
    date_sub = f"{format_tamil_date_prefix(horoscope_data.date)} • {horoscope_data.day_of_week_ta}"

    ribbon_w = CARD_PT_WIDTH - pt_x(68)
    ribbon_h = pt_x(72)
    ribbon_x = pt_x(34)
    ribbon_y = pt_y(218)
    c.saveState()
    c.setFillColor(colors.HexColor("#123763"))
    c.setStrokeColor(colors.HexColor("#D4AF37"))
    c.setLineWidth(1.4)
    c.rect(ribbon_x, ribbon_y, ribbon_w, ribbon_h, stroke=1, fill=1)
    c.restoreState()

    draw_shaped_text(c, date_title, CARD_PT_WIDTH / 2.0, ribbon_y + 21.0, font_key="bold", font_size=15.2, color=colors.HexColor("#FFFFFF"), align="center")
    draw_shaped_text(c, date_sub, CARD_PT_WIDTH / 2.0, ribbon_y + 6.0, font_key="bold", font_size=10.0, color=colors.HexColor("#FFD700"), align="center")

    # 4. RASI HERO SECTION (Cancer Emblem Circle & Grand Name Pill)
    zodiac_cx, zodiac_cy, zodiac_r = pt_x(180), pt_y(308), pt_x(72)
    c.saveState()
    c.setFillColor(colors.HexColor("#14355E"))
    c.setStrokeColor(colors.HexColor("#FFD700"))
    c.setLineWidth(2.4)
    c.circle(zodiac_cx, zodiac_cy, zodiac_r, stroke=1, fill=1)
    c.restoreState()

    _draw_zodiac_emblem(c, prediction.rashi_id, zodiac_cx, zodiac_cy + pt_x(5), pt_x(48), accent=colors.HexColor("#FFD700"))
    draw_shaped_text(c, prediction.rashi_name_en.upper(), zodiac_cx, zodiac_cy - pt_x(36), font_key="bold", font_size=7.5, color=colors.HexColor("#FFD700"), align="center")

    rp_x = pt_x(285)
    rp_w = pt_x(650)
    rp_h = pt_x(98)
    rp_y = pt_y(342)
    c.saveState()
    c.setFillColor(colors.HexColor("#103762"))
    c.setStrokeColor(colors.HexColor("#FFD700"))
    c.setLineWidth(2.4)
    c.roundRect(rp_x, rp_y, rp_w, rp_h, pt_x(20), stroke=1, fill=1)
    c.restoreState()

    draw_shaped_text(c, "❖", rp_x + pt_x(35), rp_y + pt_y(28), font_key="bold", font_size=16.0, color=colors.HexColor("#FFD700"), align="center")
    draw_shaped_text(c, "❖", rp_x + rp_w - pt_x(35), rp_y + pt_y(28), font_key="bold", font_size=16.0, color=colors.HexColor("#FFD700"), align="center")
    draw_shaped_text(c, prediction.rashi_name_ta, rp_x + rp_w / 2.0, rp_y + 11.0, font_key="bold", font_size=32.0, color=colors.HexColor("#FFD700"), align="center")

    # 5. MAIN PREDICTIONS PARCHMENT BOX (4 Crisp Points)
    pbox_x = pt_x(44)
    pbox_w = CARD_PT_WIDTH - pt_x(88)
    pbox_h = pt_x(360)
    pbox_y = pt_y(735)
    c.saveState()
    c.setFillColor(colors.HexColor("#FFFDF5"))
    c.setStrokeColor(colors.HexColor("#D4AF37"))
    c.setLineWidth(2.4)
    c.roundRect(pbox_x, pbox_y, pbox_w, pbox_h, pt_x(16), stroke=1, fill=1)
    c.restoreState()

    # Points to display
    pts: List[str] = []
    if prediction.brief_statement_ta:
        b_c = clean_brief_ta(prediction.brief_statement_ta)
        if b_c:
            pts.append(b_c)
    for a in prediction.aspects:
        if len(pts) >= 4:
            break
        a_t = format_aspect_text_ta(a.insight_ta, a.key_recommendation_ta)
        if a_t and a_t not in pts:
            pts.append(a_t)
    if prediction.daily_remedy_ta and len(pts) < 4:
        pts.append(prediction.daily_remedy_ta)
    while len(pts) < 4:
        pts.append("எடுத்த காரியங்களில் அனுகூலமான வெற்றியும் மனமகிழ்ச்சியும் உண்டாகும்.")

    pts_y = [pt_y(430), pt_y(505), pt_y(580), pt_y(655)]
    for idx, p_txt in enumerate(pts[:4]):
        ly = pts_y[idx]
        draw_shaped_text(c, "❖", pbox_x + pt_x(25), ly, font_key="bold", font_size=12.5, color=colors.HexColor("#0B2E59"))
        wrapped = wrap_shaped_text(p_txt, "bold", 10.8, max_width=pbox_w - pt_x(65), max_lines=2)
        for w_i, line in enumerate(wrapped):
            draw_shaped_text(c, line, pbox_x + pt_x(52), ly - (w_i * 15.0), font_key="bold", font_size=10.8, color=colors.HexColor("#0A192F"))

    # 6. LUCKY DETAILS (3 Golden Tiles)
    tile_w = (pbox_w - pt_x(24)) / 3.0
    tile_h = pt_x(82)
    tile_y = pt_y(840)

    lucky_dir = prediction.lucky_direction_ta or "வடக்கு"
    lucky_num = str(prediction.lucky_number or "2, 7")
    lucky_color = prediction.lucky_color_ta.split("&")[0].strip() if prediction.lucky_color_ta else "வெள்ளை / கிரீம்"

    tiles = [
        ("🧭", "அதிர்ஷ்ட திசை", lucky_dir),
        (lucky_num.split(",")[0].strip() if "," in lucky_num else lucky_num, "அதிர்ஷ்ட எண்", lucky_num),
        ("⚪", "அதிர்ஷ்ட நிறம்", lucky_color),
    ]

    for t_i, (t_icon, t_lbl, t_val) in enumerate(tiles):
        tx = pbox_x + t_i * (tile_w + pt_x(12))
        c.saveState()
        c.setFillColor(colors.HexColor("#0C2442"))
        c.setStrokeColor(colors.HexColor("#D4AF37"))
        c.setLineWidth(1.6)
        c.roundRect(tx, tile_y, tile_w, tile_h, pt_x(12), stroke=1, fill=1)

        ic_r = pt_x(25)
        c.setFillColor(colors.HexColor("#FFD700"))
        c.circle(tx + pt_x(36), tile_y + tile_h / 2.0, ic_r, stroke=0, fill=1)
        c.restoreState()

        draw_shaped_text(c, t_icon, tx + pt_x(36), tile_y + (tile_h / 2.0) - 4.5, font_key="bold", font_size=10.5, color=colors.HexColor("#0A192F"), align="center")
        draw_shaped_text(c, t_lbl, tx + pt_x(72), tile_y + tile_h - 13.0, font_key="bold", font_size=7.2, color=colors.HexColor("#FFD700"))
        draw_shaped_text(c, t_val, tx + pt_x(72), tile_y + 9.0, font_key="bold", font_size=10.2, color=colors.HexColor("#FFFFFF"))

    # 7. NAKSHATRAS (3 Rows)
    nbox_h = pt_x(165)
    nbox_y = pt_y(1025)
    c.saveState()
    c.setFillColor(colors.HexColor("#07192E"))
    c.setStrokeColor(colors.HexColor("#D4AF37"))
    c.setLineWidth(1.8)
    c.roundRect(pbox_x, nbox_y, pbox_w, nbox_h, pt_x(14), stroke=1, fill=1)
    c.restoreState()

    rashi_stars = {
        1: [("அஸ்வினி", "எடுத்த காரியங்களில் அனுகூலமான வெற்றி கிடைக்கும்."), ("பரணி", "பணவரவு திருப்திகரமாக இருக்கும்; குடும்பத்தில் மகிழ்ச்சி."), ("கார்த்திகை", "தொழில் ரீதியான புதிய முயற்சிகளில் ஆதாயம் கிட்டும்.")],
        2: [("கார்த்திகை", "அலுவலகப் பணிகளில் நிதானமும் கவனமும் தேவை."), ("ரோகிணி", "சுபகாரிய பேச்சுவார்த்தைகள் சுமுகமாக முடியும்."), ("மிருகசீரிஷம்", "புதிய நபர்களின் அறிமுகமும் ஆதரவும் உற்சாகம் தரும்.")],
        3: [("மிருகசீரிஷம்", "திட்டமிட்ட காரியங்கள் தடையின்றி நிறைவேறும்."), ("திருவாதிரை", "பயணங்களால் நன்மையும் புதிய அனுபவங்களும் கிடைக்கும்."), ("புனர்பூசம்", "குடும்பத்தில் அமைதியும் மகிழ்ச்சியான சூழலும் நிலவும்.")],
        4: [("புனர்பூசம்", "எடுத்த காரியங்களில் அனுகூலமான வெற்றியும் மனமகிழ்ச்சியும் உண்டாகும்."), ("பூசம்", "குடும்பத்தில் சுபகாரிய பேச்சுவார்த்தைகள் கைகூடி மகிழ்ச்சி பெருகும்."), ("ஆயில்யம்", "தொழில் ரீதியான புதிய முயற்சிகளில் எதிர்பார்த்த நல்ல ஆதாயம் கிட்டும்.")],
        5: [("மகம்", "தொழில் மற்றும் உத்தியோகத்தில் புதிய வாய்ப்புகள் தேடி வரும்."), ("பூரம்", "உறவினர்கள் மூலம் சுபச்செய்திகள் வந்து சேரும்."), ("உத்திரம்", "பெரியோர்களின் ஆதரவு மற்றும் வழிகாட்டுதல் மனத்தெளிவு தரும்.")],
        6: [("உத்திரம்", "பணவரவு சீராக இருக்கும்; பழைய பாக்கிகள் வசூலாகும்."), ("அஸ்தம்", "பணியிடத்தில் மேலதிகாரிகளின் நன்மதிப்பும் பாராட்டுகளும் கிட்டும்."), ("சித்திரை", "உடன் பிறந்தவர்கள் மற்றும் நண்பர்களின் ஒத்துழைப்பு கிடைக்கும்.")],
        7: [("சித்திரை", "வியாபாரத்தில் புதிய வாடிக்கையாளர்கள் மூலம் லாபம் கூடும்."), ("சுவாதி", "நீண்ட நாள் ஆசைகள் மற்றும் திட்டங்கள் நிறைவேறும்."), ("விசாகம்", "குடும்பத்தினருடன் மகிழ்ச்சியான நேரத்தைச் செலவிடுவீர்கள்.")],
        8: [("விசாகம்", "எதிர்பாராத தனவரவு மற்றும் நல்ல மாற்றங்கள் உண்டாகும்."), ("அனுஷம்", "தொழில் பணிகளில் நிலவி வந்த தடைகள் விலகும்."), ("கேட்டை", "உத்தியோகத்தில் புதிய பொறுப்புகள் மற்றும் அங்கீகாரம் கிடைக்கும்.")],
        9: [("மூலம்", "ஆன்மீக ஈடுபாடும் மன அமைதியும் கூடும்."), ("பூராடம்", "சுபகாரிய முயற்சிகளில் எதிர்பார்த்த அனுகூலம் உண்டு."), ("உத்திராடம்", "நிதி நிலைமை உயரும்; குடும்பத் தேவைகள் பூர்த்தியாகும்.")],
        10: [("உத்திராடம்", "உழைப்பிற்கேற்ற நல்ல பலன்களும் நன்மதிப்பும் கிட்டும்."), ("திருவோணம்", "புதிய முதலீடுகள் மற்றும் திட்டங்களில் விவேகம் தேவை."), ("அவிட்டம்", "நண்பர்கள் மற்றும் உடன் பணிபுரிபவர்களின் ஆதரவு உற்சாகம் தரும்.")],
        11: [("அவிட்டம்", "பணவரவு தாராளமாக இருக்கும்; சேமிப்பு உயரும்."), ("சதயம்", "தொழில் விரிவாக்க முயற்சிகள் நல்ல பலனைத் தரும்."), ("பூரட்டாதி", "குடும்பத்தில் இருந்த கருத்து வேறுபாடுகள் நீங்கி ஒற்றுமை பலப்படும்.")],
        12: [("பூரட்டாதி", "மனதில் நிலவிய கவலைகள் நீங்கி புத்துணர்ச்சி பிறக்கும்."), ("உத்திரட்டாதி", "தொழில் மற்றும் வியாபாரத்தில் நல்ல முன்னேற்றம் காணப்படும்."), ("ரேவதி", "சுபச்செலவுகள் மூலம் குடும்பத்தில் சுபமங்கள நிகழ்வுகள் கைகூடும்.")],
    }

    stars = rashi_stars.get(prediction.rashi_id, rashi_stars[4])
    star_ys = [pt_y(895), pt_y(945), pt_y(995)]
    for s_i, (s_n, s_p) in enumerate(stars[:3]):
        sy = star_ys[s_i]
        draw_shaped_text(c, f"★ {s_n}", pbox_x + pt_x(20), sy, font_key="bold", font_size=10.2, color=colors.HexColor("#FFD700"))
        draw_shaped_text(c, ":", pbox_x + pt_x(135), sy, font_key="bold", font_size=10.2, color=colors.HexColor("#FFD700"))
        wrapped_s = wrap_shaped_text(s_p, "bold", 9.8, max_width=pbox_w - pt_x(160), max_lines=1)
        stxt = wrapped_s[0] if wrapped_s else s_p
        draw_shaped_text(c, stxt, pbox_x + pt_x(155), sy, font_key="bold", font_size=9.8, color=colors.HexColor("#FFFFFF"))

    # 8. FOOTER
    draw_shaped_text(
        c,
        "© Gokul's Astrological Insights • Daily Horoscope",
        CARD_PT_WIDTH / 2.0,
        pt_y(1055),
        font_key="bold",
        font_size=8.2,
        color=colors.HexColor("#8DA4BE"),
        align="center",
    )

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
