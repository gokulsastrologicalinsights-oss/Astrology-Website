"""Vector drawing of South Indian astrological chart for ReportLab PDF documents.

Renders high-resolution vector representations (Drawing, Rect, String, Line)
for D1 (Rasi), D9 (Navamsa), D10 (Dasamsa), and other divisional charts.
Supports bilingual Tamil and English labels with highlight for the Lagna sign.
"""

from typing import Dict, List, Optional, Any
from reportlab.graphics.shapes import Drawing, Rect, String as _RLString, Line, Group
from reportlab.lib import colors

from app.services.pdf_report_engine.fonts import reorder_tamil_for_pdf


class String(_RLString):
    """Shape-aware String for ReportLab vector drawings with Indic reordering."""

    def __init__(self, x: float, y: float, text: Any, *args, **kwargs):
        super().__init__(x, y, reorder_tamil_for_pdf(text), *args, **kwargs)


# Canonical South Indian Chart Box Coordinates (Col 0..3, Row 0..3 from top)
# In ReportLab coordinate system: (0,0) is bottom-left.
# Col 0: x=0, Col 1: x=step, Col 2: x=2*step, Col 3: x=3*step
# Row 0 (Top): y = 3*step
# Row 1: y = 2*step
# Row 2: y = 1*step
# Row 3 (Bottom): y = 0
SIGN_GRID_MAP: Dict[int, tuple[int, int]] = {
    12: (0, 3),  # Pisces / மீனம்
    1:  (1, 3),  # Aries / மேஷம்
    2:  (2, 3),  # Taurus / ரிஷபம்
    3:  (3, 3),  # Gemini / மிதுனம்
    4:  (3, 2),  # Cancer / கடகம்
    5:  (3, 1),  # Leo / சிம்மம்
    6:  (3, 0),  # Virgo / கன்னி
    7:  (2, 0),  # Libra / துலாம்
    8:  (1, 0),  # Scorpio / விருச்சிகம்
    9:  (0, 0),  # Sagittarius / தனுசு
    10: (0, 1),  # Capricorn / மகரம்
    11: (0, 2),  # Aquarius / கும்பம்
}

SIGN_NAMES_SHORT_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

SIGN_NAMES_SHORT_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

GRAHA_ABBR_EN: Dict[str, str] = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "Asc", "Lagna": "Asc"
}

GRAHA_ABBR_TA: Dict[str, str] = {
    "Sun": "சூரி", "Moon": "சந்", "Mars": "செவ்", "Mercury": "புதன்",
    "Jupiter": "குரு", "Venus": "சுக்", "Saturn": "சனி",
    "Rahu": "ராகு", "Ketu": "கேது", "Ascendant": "லக்", "Lagna": "லக்"
}


def create_south_indian_chart(
    chart_data: Dict[str, Any],
    title_en: str = "RASI CHART (D1)",
    title_ta: str = "ராசி கட்டம் (D1)",
    size: float = 210.0,
    font_name: str = "NotoSansTamil",
    font_bold: str = "NotoSansTamil-Bold",
    language: str = "en",
) -> Drawing:
    """Create a vector drawing of a South Indian 4x4 chart.

    chart_data must contain:
    - 'ascendant_sign': int (1-12)
    - 'planets': list of dicts with:
        - 'name': str (e.g. 'Sun', 'Moon', ...)
        - 'sign_index': int (1-12)
        - 'degree_in_sign': Optional[float]
        - 'is_retrograde': Optional[bool]
    - optional 'ascendant_degree': Optional[float]
    """
    d = Drawing(size, size)
    step = size / 4.0

    # 1. Outer Frame
    d.add(Rect(0, 0, size, size, fillColor=colors.white, strokeColor=colors.HexColor("#334155"), strokeWidth=1.5))

    # Identify Ascendant sign
    asc_sign = chart_data.get("ascendant_sign", 1)
    asc_deg = chart_data.get("ascendant_degree", None)

    # Group occupants by sign index (1-12)
    occupants: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

    # Add Ascendant
    if 1 <= asc_sign <= 12:
        asc_label = "Asc" if language != "ta" else "லக்னம்"
        if asc_deg is not None:
            deg_int = int(asc_deg)
            min_int = int(round((asc_deg - deg_int) * 60))
            asc_label += f" {deg_int:02d}°{min_int:02d}'"
        occupants[asc_sign].append(f"[ {asc_label} ]")

    # Add Planets
    for p in chart_data.get("planets", []):
        s_idx = p.get("sign_index", 1)
        if 1 <= s_idx <= 12:
            p_name = p.get("name", "")
            abbr = GRAHA_ABBR_TA.get(p_name, p_name) if language == "ta" else GRAHA_ABBR_EN.get(p_name, p_name[:2])
            is_retro = p.get("is_retrograde", False)
            deg_val = p.get("degree_in_sign", None)
            
            p_str = abbr
            if is_retro and p_name not in ("Rahu", "Ketu"):
                p_str += "(R)"
            if deg_val is not None:
                d_i = int(deg_val)
                m_i = int(round((deg_val - d_i) * 60))
                p_str += f" {d_i:02d}°{m_i:02d}'"
            occupants[s_idx].append(p_str)

    # 2. Draw 12 Outer Sign Boxes
    for s_idx, (col, row) in SIGN_GRID_MAP.items():
        box_x = col * step
        box_y = row * step

        # Highlight Ascendant Box
        is_asc = (s_idx == asc_sign)
        box_bg = colors.HexColor("#FEF9C3") if is_asc else colors.white  # Soft warm yellow for Lagna

        d.add(Rect(
            box_x, box_y, step, step,
            fillColor=box_bg,
            strokeColor=colors.HexColor("#94A3B8"),
            strokeWidth=0.75
        ))

        # Sign Title at top of box
        sign_name = SIGN_NAMES_SHORT_TA.get(s_idx, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(s_idx, "")
        header_text = f"{s_idx}. {sign_name}"
        d.add(String(
            box_x + 3, box_y + step - 9,
            header_text,
            fontName=font_bold if is_asc else font_name,
            fontSize=6.0,
            fillColor=colors.HexColor("#8B6914") if is_asc else colors.HexColor("#64748B"),
        ))

        # Divider line under sign header
        d.add(Line(
            box_x + 2, box_y + step - 11,
            box_x + step - 2, box_y + step - 11,
            strokeColor=colors.HexColor("#E2E8F0"),
            strokeWidth=0.5
        ))

        # Render occupants inside box
        occ_list = occupants[s_idx]
        text_y = box_y + step - 19
        for item in occ_list[:4]:  # Fit up to 4 items per box
            is_item_asc = item.startswith("[")
            f_name = font_bold if is_item_asc else font_name
            f_color = colors.HexColor("#991B1B") if is_item_asc else colors.HexColor("#0F172A")
            f_size = 5.8 if is_item_asc else 5.5

            d.add(String(
                box_x + 3, text_y,
                item,
                fontName=f_name,
                fontSize=f_size,
                fillColor=f_color,
            ))
            text_y -= 8

    # 3. Center 2x2 Cell (Merged)
    center_x = step
    center_y = step
    center_w = step * 2
    center_h = step * 2

    d.add(Rect(
        center_x, center_y, center_w, center_h,
        fillColor=colors.HexColor("#F8FAFC"),
        strokeColor=colors.HexColor("#0F172A"),
        strokeWidth=1.2
    ))

    # Inner decorative border in center box
    d.add(Rect(
        center_x + 3, center_y + 3, center_w - 6, center_h - 6,
        fillColor=None,
        strokeColor=colors.HexColor("#CBD5E1"),
        strokeWidth=0.5
    ))

    # Center Text
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 + 12,
        title_ta if language == "ta" else title_en,
        fontName=font_bold,
        fontSize=8.5,
        fillColor=colors.HexColor("#8B6914"),
        textAnchor="middle",
    ))

    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 2,
        title_en if language == "ta" else title_ta,
        fontName=font_name,
        fontSize=7.5,
        fillColor=colors.HexColor("#475569"),
        textAnchor="middle",
    ))

    lagna_name = SIGN_NAMES_SHORT_TA.get(asc_sign, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(asc_sign, "")
    lagna_str = f"லக்னம்: {lagna_name}" if language == "ta" else f"Lagna: {lagna_name}"
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 16,
        lagna_str,
        fontName=font_bold,
        fontSize=7.0,
        fillColor=colors.HexColor("#991B1B"),
        textAnchor="middle",
    ))

    return d
