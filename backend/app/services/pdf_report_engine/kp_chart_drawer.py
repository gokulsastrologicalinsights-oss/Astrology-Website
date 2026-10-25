"""Vector drawing of KP (Krishnamurti Paddhati) astrological charts for ReportLab PDF documents.

Renders high-resolution vector representations:
1. KP Nirayana Rasi Chart (Planetary placements across 12 sidereal signs with Lagna highlight).
2. KP Bhava Chalit Chart (12 Placidus house cusps positioned in zodiac signs with planet bhava occupancy).

Supports bilingual Tamil and English typography with ReportLab shape primitives.
"""

from typing import Dict, List, Optional, Any, Tuple
from reportlab.graphics.shapes import Drawing, Rect, String as _RLString, Line, Group
from reportlab.lib import colors

from app.services.pdf_report_engine.fonts import reorder_tamil_for_pdf


class String(_RLString):
    """Shape-aware String for ReportLab vector drawings with Indic reordering."""

    def __init__(self, x: float, y: float, text: Any, *args, **kwargs):
        super().__init__(x, y, reorder_tamil_for_pdf(text), *args, **kwargs)


SIGN_GRID_MAP: Dict[int, Tuple[int, int]] = {
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

ROMAN_CUSPS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def create_kp_rasi_chart(
    chart_data: Dict[str, Any],
    title_en: str = "KP NIRAYANA RASI",
    title_ta: str = "கே.பி. நிராயண ராசி",
    size: float = 210.0,
    font_name: str = "NotoSansTamil",
    font_bold: str = "NotoSansTamil-Bold",
    language: str = "en",
) -> Drawing:
    """Create a vector drawing of the KP Nirayana Rasi Chart in South Indian 4x4 style."""
    d = Drawing(size, size)
    step = size / 4.0

    # 1. Outer Frame
    d.add(Rect(0, 0, size, size, fillColor=colors.white, strokeColor=colors.HexColor("#0F172A"), strokeWidth=1.2))

    asc_sign = chart_data.get("ascendant_sign", 1)
    asc_deg = chart_data.get("ascendant_degree", None)

    # Group occupants by sign index (1-12)
    occupants: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

    # Add Ascendant
    if 1 <= asc_sign <= 12:
        asc_label = "Asc" if language != "ta" else "லக்"
        if asc_deg is not None:
            deg_int = int(asc_deg)
            min_int = int(round((asc_deg - deg_int) * 60))
            asc_label += f" {deg_int:02d}°{min_int:02d}'"
        occupants[asc_sign].append(f"[{asc_label}]")

    # Add Planets
    for p in chart_data.get("planets", []):
        s_idx = p.get("sign_index", 1)
        if 1 <= s_idx <= 12:
            p_name = p.get("name", "")
            abbr = GRAHA_ABBR_TA.get(p_name, p_name[:2]) if language == "ta" else GRAHA_ABBR_EN.get(p_name, p_name[:2])
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

    # Draw 12 Outer Sign Boxes
    for s_idx, (col, row) in SIGN_GRID_MAP.items():
        box_x = col * step
        box_y = row * step

        is_asc = (s_idx == asc_sign)
        box_bg = colors.HexColor("#FEF9C3") if is_asc else colors.white

        d.add(Rect(
            box_x, box_y, step, step,
            fillColor=box_bg,
            strokeColor=colors.HexColor("#94A3B8"),
            strokeWidth=0.75
        ))

        # Sign Title
        sign_name = SIGN_NAMES_SHORT_TA.get(s_idx, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(s_idx, "")
        header_text = f"{s_idx}. {sign_name}"
        d.add(String(
            box_x + 3, box_y + step - 9,
            header_text,
            fontName=font_bold if is_asc else font_name,
            fontSize=5.5,
            fillColor=colors.HexColor("#8B6914") if is_asc else colors.HexColor("#64748B"),
        ))

        # Divider line
        d.add(Line(
            box_x + 2, box_y + step - 11,
            box_x + step - 2, box_y + step - 11,
            strokeColor=colors.HexColor("#E2E8F0"),
            strokeWidth=0.5
        ))

        # Occupants
        occ_list = occupants[s_idx]
        text_y = box_y + step - 18
        for item in occ_list[:4]:
            is_item_asc = item.startswith("[")
            f_name = font_bold if is_item_asc else font_name
            f_color = colors.HexColor("#991B1B") if is_item_asc else colors.HexColor("#0F172A")
            f_size = 5.4 if is_item_asc else 5.1

            d.add(String(
                box_x + 3, text_y,
                item,
                fontName=f_name,
                fontSize=f_size,
                fillColor=f_color,
            ))
            text_y -= 8

    # Center 2x2 Cell (Merged)
    center_x = step
    center_y = step
    center_w = step * 2
    center_h = step * 2

    d.add(Rect(
        center_x, center_y, center_w, center_h,
        fillColor=colors.HexColor("#F8FAFC"),
        strokeColor=colors.HexColor("#0F172A"),
        strokeWidth=1.0
    ))
    d.add(Rect(
        center_x + 3, center_y + 3, center_w - 6, center_h - 6,
        fillColor=None,
        strokeColor=colors.HexColor("#CBD5E1"),
        strokeWidth=0.5
    ))

    # Center text
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 + 10,
        title_ta if language == "ta" else title_en,
        fontName=font_bold,
        fontSize=8.0,
        fillColor=colors.HexColor("#8B6914"),
        textAnchor="middle",
    ))
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 2,
        title_en if language == "ta" else title_ta,
        fontName=font_name,
        fontSize=7.0,
        fillColor=colors.HexColor("#475569"),
        textAnchor="middle",
    ))
    lagna_name = SIGN_NAMES_SHORT_TA.get(asc_sign, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(asc_sign, "")
    lagna_str = f"லக்னம்: {lagna_name}" if language == "ta" else f"Lagna: {lagna_name}"
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 14,
        lagna_str,
        fontName=font_bold,
        fontSize=6.5,
        fillColor=colors.HexColor("#991B1B"),
        textAnchor="middle",
    ))

    return d


def create_kp_bhava_chart(
    cusp_data: List[Dict[str, Any]],
    planet_data: List[Dict[str, Any]],
    title_en: str = "KP BHAVA CHALIT",
    title_ta: str = "கே.பி. பாவ சலனம்",
    size: float = 210.0,
    font_name: str = "NotoSansTamil",
    font_bold: str = "NotoSansTamil-Bold",
    language: str = "en",
) -> Drawing:
    """Create a vector drawing of the KP Placidus Bhava Chalit Chart.

    Displays each Placidus house cusp (I through XII) in its actual zodiac sign,
    and shows which planets reside inside each bhava.
    """
    d = Drawing(size, size)
    step = size / 4.0

    # 1. Outer Frame
    d.add(Rect(0, 0, size, size, fillColor=colors.white, strokeColor=colors.HexColor("#0F172A"), strokeWidth=1.2))

    # Map cusps to signs
    # cusp_data is list of dicts: {'house': 1..12, 'cusp_degree': float, 'sign_index': 1..12, ...}
    sign_cusps: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(1, 13)}
    c1_sign = 1
    for c in cusp_data:
        h = c.get("house", 1)
        s = c.get("sign_index", 1)
        if h == 1:
            c1_sign = s
        if 1 <= s <= 12:
            sign_cusps[s].append(c)

    # Determine bhava occupancy for each planet
    # A planet is in bhava H if its longitude falls between Cusp H and Cusp H+1
    sorted_cusps = sorted(cusp_data, key=lambda x: x.get("house", 1))
    cusp_degs = [c.get("cusp_degree", 0.0) % 360.0 for c in sorted_cusps]
    if len(cusp_degs) != 12:
        cusp_degs = [i * 30.0 for i in range(12)]

    def get_bhava_for_longitude(lon: float) -> int:
        lon_norm = lon % 360.0
        for i in range(12):
            c_start = cusp_degs[i]
            c_end = cusp_degs[(i + 1) % 12]
            if c_start < c_end:
                if c_start <= lon_norm < c_end:
                    return i + 1
            else:  # Spans 0/360 boundary
                if lon_norm >= c_start or lon_norm < c_end:
                    return i + 1
        return 1

    # Map planets to their zodiac signs, annotating with their Bhava
    sign_planets: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(1, 13)}
    for p in planet_data:
        s_idx = p.get("sign_index", 1)
        lon = p.get("longitude", 0.0)
        bhava_num = get_bhava_for_longitude(lon)
        if 1 <= s_idx <= 12:
            p_copy = dict(p)
            p_copy["bhava"] = bhava_num
            sign_planets[s_idx].append(p_copy)

    # Draw 12 Outer Sign Boxes
    for s_idx, (col, row) in SIGN_GRID_MAP.items():
        box_x = col * step
        box_y = row * step

        is_c1 = (s_idx == c1_sign)
        box_bg = colors.HexColor("#FEF9C3") if is_c1 else colors.white

        d.add(Rect(
            box_x, box_y, step, step,
            fillColor=box_bg,
            strokeColor=colors.HexColor("#94A3B8"),
            strokeWidth=0.75
        ))

        # Sign Header
        sign_name = SIGN_NAMES_SHORT_TA.get(s_idx, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(s_idx, "")
        header_text = f"{s_idx}. {sign_name}"
        d.add(String(
            box_x + 3, box_y + step - 9,
            header_text,
            fontName=font_bold if is_c1 else font_name,
            fontSize=5.5,
            fillColor=colors.HexColor("#8B6914") if is_c1 else colors.HexColor("#64748B"),
        ))

        # Divider line
        d.add(Line(
            box_x + 2, box_y + step - 11,
            box_x + step - 2, box_y + step - 11,
            strokeColor=colors.HexColor("#E2E8F0"),
            strokeWidth=0.5
        ))

        text_y = box_y + step - 18

        # 1. Draw House Cusps falling in this sign (in Crimson/Bold)
        for c in sign_cusps[s_idx]:
            h_num = c.get("house", 1)
            deg_val = c.get("cusp_degree", 0.0) % 30.0
            d_i = int(deg_val)
            m_i = int(round((deg_val - d_i) * 60))
            c_label = f"C{h_num}" if language != "ta" else f"பா{h_num}"
            c_str = f"<{c_label} {d_i:02d}°{m_i:02d}'>"
            d.add(String(
                box_x + 3, text_y,
                c_str,
                fontName=font_bold,
                fontSize=5.2,
                fillColor=colors.HexColor("#991B1B"),
            ))
            text_y -= 8

        # 2. Draw Planets falling in this sign with their bhava number in brackets
        for p in sign_planets[s_idx][:3]:  # Up to 3 planets
            p_name = p.get("name") or p.get("planet", "")
            abbr = GRAHA_ABBR_TA.get(p_name, p_name[:2]) if language == "ta" else GRAHA_ABBR_EN.get(p_name, p_name[:2])
            b_num = p.get("bhava", 1)
            b_tag = f"H{b_num}" if language != "ta" else f"ப{b_num}"
            deg_val = (p.get("longitude", 0.0) % 30.0)
            d_i = int(deg_val)
            p_str = f"{abbr}({b_tag}) {d_i:02d}°"
            d.add(String(
                box_x + 3, text_y,
                p_str,
                fontName=font_name,
                fontSize=5.0,
                fillColor=colors.HexColor("#0F172A"),
            ))
            text_y -= 7.5

    # Center 2x2 Cell (Merged)
    center_x = step
    center_y = step
    center_w = step * 2
    center_h = step * 2

    d.add(Rect(
        center_x, center_y, center_w, center_h,
        fillColor=colors.HexColor("#F8FAFC"),
        strokeColor=colors.HexColor("#0F172A"),
        strokeWidth=1.0
    ))
    d.add(Rect(
        center_x + 3, center_y + 3, center_w - 6, center_h - 6,
        fillColor=None,
        strokeColor=colors.HexColor("#CBD5E1"),
        strokeWidth=0.5
    ))

    # Center text
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 + 10,
        title_ta if language == "ta" else title_en,
        fontName=font_bold,
        fontSize=8.0,
        fillColor=colors.HexColor("#8B6914"),
        textAnchor="middle",
    ))
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 2,
        "Placidus Semi-Arc / பிளாசிடஸ் முறை",
        fontName=font_name,
        fontSize=6.5,
        fillColor=colors.HexColor("#475569"),
        textAnchor="middle",
    ))
    c1_name = SIGN_NAMES_SHORT_TA.get(c1_sign, "") if language == "ta" else SIGN_NAMES_SHORT_EN.get(c1_sign, "")
    c1_str = f"1-ம் பாவம்: {c1_name}" if language == "ta" else f"Cusp 1: {c1_name}"
    d.add(String(
        center_x + center_w / 2.0, center_y + center_h / 2.0 - 14,
        c1_str,
        fontName=font_bold,
        fontSize=6.5,
        fillColor=colors.HexColor("#991B1B"),
        textAnchor="middle",
    ))

    return d
