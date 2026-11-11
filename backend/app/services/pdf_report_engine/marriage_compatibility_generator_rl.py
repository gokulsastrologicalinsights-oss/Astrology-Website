"""Pure-Python ReportLab 5-Page Marriage Compatibility PDF Generator.

Provides a fast, low-memory (<20 MB) ReportLab implementation matching the
5-page print format when headless Chromium is unavailable (e.g. Render 512MB).
Consumes `build_marriage_print_view_model` so Page 1-5 content matches the HTML/Print output.
"""

from __future__ import annotations

import html
from io import BytesIO
import logging
from typing import Any, Dict, List

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String as _RLString
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph as _RLParagraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.pdf_report_engine.chart_drawer import SIGN_GRID_MAP
from app.services.pdf_report_engine.fonts import register_report_fonts, reorder_tamil_for_pdf
from app.services.pdf_report_engine.marriage_print_viewmodel import (
    DASA_COLORS,
    build_marriage_print_view_model,
)

logger = logging.getLogger("gai.pdf.marriage_generator_rl")

MARGIN_PT = 28.35  # 10mm
CONTENT_WIDTH = A4[0] - (2 * MARGIN_PT)  # ~538.57 pt


def _p_text(text: Any, style: ParagraphStyle) -> _RLParagraph:
    raw = str(text if text is not None else "")
    return _RLParagraph(reorder_tamil_for_pdf(raw), style)


def _esc(text: Any) -> str:
    return html.escape(str(text if text is not None else ""))


def _make_tick_drawing(passed: bool) -> Drawing:
    d = Drawing(12, 12)
    if passed:
        col = colors.HexColor("#059669")
        d.add(Line(2.0, 5.5, 4.8, 2.5, strokeColor=col, strokeWidth=1.6))
        d.add(Line(4.8, 2.5, 10.2, 9.5, strokeColor=col, strokeWidth=1.6))
    else:
        col = colors.HexColor("#E11D48")
        d.add(Line(2.5, 2.5, 9.5, 9.5, strokeColor=col, strokeWidth=1.5))
        d.add(Line(2.5, 9.5, 9.5, 2.5, strokeColor=col, strokeWidth=1.5))
    return d


def _make_south_chart_drawing(
    chart: Dict[str, Any],
    font_reg: str,
    font_bold: str,
    width: float = 215.0,
) -> Drawing:
    title_h = 18.0
    total_h = width + title_h
    d = Drawing(width, total_h)
    step = width / 4.0

    # Title above box
    d.add(
        _RLString(
            width / 2.0,
            width + 5.0,
            reorder_tamil_for_pdf(chart["title"]),
            fontName=font_bold,
            fontSize=9.5,
            fillColor=colors.HexColor("#0F172A"),
            textAnchor="middle",
        )
    )

    # White background + outer black frame
    d.add(Rect(0, 0, width, width, fillColor=colors.white, strokeColor=colors.HexColor("#0F172A"), strokeWidth=1.5))

    # Inner horizontal & vertical grid lines (respecting center 2x2 merge)
    for idx in (1, 2, 3):
        pos = idx * step
        if idx == 2:
            d.add(Line(pos, 0, pos, step, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
            d.add(Line(pos, 3 * step, pos, width, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
            d.add(Line(0, pos, step, pos, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
            d.add(Line(3 * step, pos, width, pos, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
        else:
            d.add(Line(pos, 0, pos, width, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))
            d.add(Line(0, pos, width, pos, strokeColor=colors.HexColor("#0F172A"), strokeWidth=0.8))

    # Center label
    d.add(
        _RLString(
            width / 2.0,
            width / 2.0 - 4.0,
            reorder_tamil_for_pdf(chart["center"]),
            fontName=font_bold,
            fontSize=9.5,
            fillColor=colors.HexColor("#0F172A"),
            textAnchor="middle",
        )
    )

    # Planets per sign box
    cells: Dict[int, List[str]] = chart["cells"]
    for sign_idx, (col, row) in SIGN_GRID_MAP.items():
        items = cells.get(sign_idx, [])
        if not items:
            continue
        cx = col * step + step / 2.0
        cy = row * step + step / 2.0
        line_h = 9.8
        total_txt_h = (len(items) - 1) * line_h
        start_y = cy + total_txt_h / 2.0 - 3.0
        for i, txt in enumerate(items[:5]):
            d.add(
                _RLString(
                    cx,
                    start_y - i * line_h,
                    reorder_tamil_for_pdf(txt),
                    fontName=font_reg,
                    fontSize=8.0,
                    fillColor=colors.HexColor("#0F172A"),
                    textAnchor="middle",
                )
            )

    return d


def _make_dasa_timeline_drawing(
    tl: Dict[str, Any],
    font_reg: str,
    font_bold: str,
    draw_w: float = 538.0,
    draw_h: float = 650.0,
) -> Drawing:
    d = Drawing(draw_w, draw_h)
    svg_w = tl["svg_width"]
    svg_h = tl["svg_height"]
    sx = draw_w / svg_w
    sy = draw_h / svg_h
    y_for_year = tl["y_for_year"]
    now_y_svg = tl["now_y"]
    current_yr = tl["current_year_num"]
    max_yr = tl["max_visible_year"]
    g_mds = tl["g_visible_mds"]
    b_mds = tl["b_visible_mds"]

    def rx(x: float) -> float:
        return x * sx

    def ry(y_svg: float) -> float:
        return draw_h - (y_svg * sy)

    def _draw_side_rects(mds: List[Dict[str, Any]], x_bar_svg: float, x_yr_svg: float, anchor: str) -> None:
        bar_w = 145.0 * sx
        bx = rx(x_bar_svg)
        yx = rx(x_yr_svg)
        for idx, md in enumerate(mds):
            yt_s = y_for_year(md["start_year"])
            yb_s = y_for_year(md["end_year"])
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_active = float(md["start_year"]) < current_yr < float(md["end_year"])
            if is_active:
                y1_top = ry(yt_s)
                y1_bot = ry(now_y_svg)
                d.add(Rect(bx, y1_bot, bar_w, max(1.0, y1_top - y1_bot), fillColor=colors.HexColor(col["light_bg"]), strokeColor=colors.white, strokeWidth=0.8))
                y2_bot = ry(yb_s)
                d.add(Rect(bx, y2_bot, bar_w, max(1.0, y1_bot - y2_bot), fillColor=colors.HexColor(col["bg"]), strokeColor=colors.white, strokeWidth=0.8))
            else:
                y_top = ry(yt_s)
                y_bot = ry(yb_s)
                d.add(Rect(bx, y_bot, bar_w, max(1.5, y_top - y_bot), fillColor=colors.HexColor(col["bg"]), strokeColor=colors.white, strokeWidth=0.8))

            d.add(
                _RLString(
                    yx,
                    ry(yt_s + 4.0),
                    str(md.get("start_cal_year") or ""),
                    fontName=font_reg,
                    fontSize=7.8,
                    fillColor=colors.HexColor("#64748B"),
                    textAnchor=anchor,
                )
            )
            if idx == len(mds) - 1:
                d.add(
                    _RLString(
                        yx,
                        ry(yb_s + 3.0),
                        str(md.get("end_cal_year") or ""),
                        fontName=font_reg,
                        fontSize=7.8,
                        fillColor=colors.HexColor("#64748B"),
                        textAnchor=anchor,
                    )
                )

    _draw_side_rects(g_mds, 70.0, 62.0, "end")
    _draw_side_rects(b_mds, 465.0, 618.0, "start")

    if tl["top_pad"] <= now_y_svg <= svg_h - tl["bot_pad"]:
        ny = ry(now_y_svg)
        d.add(Line(rx(32.0), ny, rx(215.0), ny, strokeColor=colors.HexColor("#DC2626"), strokeWidth=1.3))
        now_x = rx(30.0 if tl["now_collides_with_g_start"] else 60.0)
        now_anchor = "start" if tl["now_collides_with_g_start"] else "end"
        d.add(
            _RLString(
                now_x,
                ry(now_y_svg - 4.0),
                "Now",
                fontName=font_bold,
                fontSize=7.8,
                fillColor=colors.HexColor("#DC2626"),
                textAnchor=now_anchor,
            )
        )

    def _draw_side_labels(mds: List[Dict[str, Any]], x_center_svg: float, avoid_now: bool) -> None:
        xc = rx(x_center_svg)
        for md in mds:
            if float(md["start_year"]) >= max_yr:
                continue
            yt_s = y_for_year(md["start_year"])
            yb_s = y_for_year(md["end_year"])
            h_s = max(2.0, yb_s - yt_s)
            if h_s < 18.0:
                continue
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_active = float(md["start_year"]) < current_yr < float(md["end_year"])
            text_y_s = yt_s + h_s / 2.0 + 4.0
            if avoid_now and is_active and abs(now_y_svg - (yt_s + h_s / 2.0)) < 11.0:
                upper_h = now_y_svg - yt_s
                lower_h = yb_s - now_y_svg
                text_y_s = (
                    now_y_svg + max(13.0, lower_h / 2.0 + 3.0)
                    if lower_h >= upper_h
                    else now_y_svg - max(6.0, upper_h / 2.0 - 3.0)
                )
            text_y_s = min(yb_s - 5.0, max(yt_s + 13.0, text_y_s))
            d.add(
                _RLString(
                    xc,
                    ry(text_y_s),
                    reorder_tamil_for_pdf(md.get("lord_ta") or ""),
                    fontName=font_bold,
                    fontSize=9.0,
                    fillColor=colors.HexColor(col["text"]),
                    textAnchor="middle",
                )
            )

    _draw_side_labels(g_mds, 142.5, True)
    _draw_side_labels(b_mds, 537.5, False)

    red = colors.HexColor("#DC2626")
    x1_arrow = rx(221.0)
    x2_arrow = rx(459.0)
    x_mid = rx(340.0)
    for tr in tl["rendered_transitions"]:
        ya = ry(tr["y"])
        d.add(Line(x1_arrow + 3.0, ya, x2_arrow - 3.0, ya, strokeColor=red, strokeWidth=0.9))
        d.add(Polygon([x1_arrow, ya, x1_arrow + 4.5, ya + 2.5, x1_arrow + 4.5, ya - 2.5], fillColor=red, strokeColor=red))
        d.add(Polygon([x2_arrow, ya, x2_arrow - 4.5, ya + 2.5, x2_arrow - 4.5, ya - 2.5], fillColor=red, strokeColor=red))
        d.add(
            _RLString(
                x_mid,
                ry(tr["y"] - 3.0),
                reorder_tamil_for_pdf(tr["label_ta"]),
                fontName=font_bold,
                fontSize=7.4,
                fillColor=colors.HexColor("#7F1D1D"),
                textAnchor="middle",
            )
        )

    return d


def generate_marriage_compatibility_pdf_bytes_rl(data: Dict[str, Any], language: str = "en") -> bytes:
    """ReportLab 5-page generator aligned with `MarriageCompatibilityPrintReport`."""
    font_reg, font_bold = register_report_fonts()
    vm = build_marriage_print_view_model(data)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_PT,
        rightMargin=MARGIN_PT,
        topMargin=MARGIN_PT,
        bottomMargin=MARGIN_PT,
    )

    s_title = ParagraphStyle("RLBrand", fontName=font_bold, fontSize=16, leading=20, alignment=1, textColor=colors.HexColor("#0F172A"))
    s_addr = ParagraphStyle("RLAddr", fontName=font_reg, fontSize=8.5, leading=11.5, alignment=1, textColor=colors.HexColor("#334155"))
    s_sec_h2 = ParagraphStyle("RLH2", fontName=font_bold, fontSize=14, leading=18, textColor=colors.HexColor("#0F172A"), spaceAfter=6)
    s_sec_h3 = ParagraphStyle("RLH3", fontName=font_bold, fontSize=12.5, leading=16, textColor=colors.HexColor("#0F172A"), spaceAfter=6)
    s_sub_h3 = ParagraphStyle("RLSubH3", fontName=font_bold, fontSize=10.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceAfter=4)
    s_groom_hdr = ParagraphStyle("RLGroomH", fontName=font_bold, fontSize=11.5, leading=15, alignment=1, textColor=colors.HexColor("#0284C7"))
    s_bride_hdr = ParagraphStyle("RLBrideH", fontName=font_bold, fontSize=11.5, leading=15, alignment=1, textColor=colors.HexColor("#0D9488"))
    s_prof_lbl = ParagraphStyle("RLProfL", fontName=font_reg, fontSize=8.8, leading=12.5, textColor=colors.HexColor("#64748B"))
    s_prof_val = ParagraphStyle("RLProfV", fontName=font_bold, fontSize=8.8, leading=12.5, textColor=colors.HexColor("#0F172A"))
    s_th = ParagraphStyle("RLTh", fontName=font_bold, fontSize=8.2, leading=10.5, textColor=colors.HexColor("#0F172A"))
    s_th_c = ParagraphStyle("RLThC", fontName=font_bold, fontSize=8.2, leading=10.5, alignment=1, textColor=colors.HexColor("#0F172A"))
    s_td = ParagraphStyle("RLTd", fontName=font_reg, fontSize=8.2, leading=11, textColor=colors.HexColor("#0F172A"))
    s_td_b = ParagraphStyle("RLTdB", fontName=font_bold, fontSize=8.2, leading=11, textColor=colors.HexColor("#0F172A"))
    s_dosha_none = ParagraphStyle("RLDN", fontName=font_reg, fontSize=8.0, leading=10.5, textColor=colors.HexColor("#334155"))
    s_dosha_mit = ParagraphStyle("RLDM", fontName=font_reg, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#047857"))
    s_dosha_pres = ParagraphStyle("RLDP", fontName=font_reg, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#BE123C"))
    s_sage = ParagraphStyle("RLSage", fontName=font_reg, fontSize=9.0, leading=14.0, textColor=colors.HexColor("#0F172A"))

    story: List[Any] = []

    # ======================== PAGE 1 ========================
    logo_cell: Any = ""
    if vm["logo_path"]:
        try:
            logo_cell = Image(vm["logo_path"], width=48, height=48)
        except Exception:
            logo_cell = ""

    header_right = [
        _p_text("<b>Gokul's Astrological Insights</b>", s_title),
        _p_text("165, Sakreeshwari Nagar, 2nd Street,<br/>Thiruverkadu, Chennai - 600077", s_addr),
    ]
    hdr_tbl = Table([[logo_cell, header_right, ""]], colWidths=[56, CONTENT_WIDTH - 112, 56])
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(hdr_tbl)
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=10))

    gp, bp = vm["groom"], vm["bride"]

    def _partner_block(hdr_txt: str, hdr_style: ParagraphStyle, p: Dict[str, Any]) -> Table:
        rows = [
            [_p_text(f"<b>{hdr_txt}</b>", hdr_style), ""],
            [_p_text("பெயர்", s_prof_lbl), _p_text(f"<b>{_esc(p['name'])}</b>", s_prof_val)],
            [_p_text("ராசி", s_prof_lbl), _p_text(f"<b>{_esc(p['rasi_ta'])}</b>", s_prof_val)],
            [_p_text("நட்சத்திரம் (பாதம்)", s_prof_lbl), _p_text(f"<b>{_esc(p['nakshatra_pada_ta'])}</b>", s_prof_val)],
            [_p_text("லக்கினம்", s_prof_lbl), _p_text(f"<b>{_esc(p['lagna_ta'])}</b>", s_prof_val)],
            [_p_text("பிறந்த தேதி", s_prof_lbl), _p_text(f"<b>{_esc(p['dob_age'])}</b>", s_prof_val)],
        ]
        pt = Table(rows, colWidths=[108, (CONTENT_WIDTH - 24) / 2.0 - 108])
        pt.setStyle(TableStyle([
            ("SPAN", (0, 0), (1, 0)),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return pt

    side_tbl = Table(
        [[_partner_block("மணமகன்", s_groom_hdr, gp), _partner_block("மணமகள்", s_bride_hdr, bp)]],
        colWidths=[CONTENT_WIDTH / 2.0, CONTENT_WIDTH / 2.0],
    )
    side_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(side_tbl)
    story.append(Spacer(1, 10))

    # Verdict Box
    tone = vm["verdict"]["tone"]
    if tone == "green":
        v_border, v_bg, v_hdr_bg = "#16A34A", "#F0FDF4", "#15803D"
    elif tone == "amber":
        v_border, v_bg, v_hdr_bg = "#D97706", "#FFFBEB", "#B45309"
    else:
        v_border, v_bg, v_hdr_bg = "#DC2626", "#FFF1F2", "#B91C1C"

    s_v_hdr = ParagraphStyle("RLVHdr", fontName=font_bold, fontSize=12.5, leading=16, alignment=1, textColor=colors.white)
    s_v_lbl = ParagraphStyle("RLVLbl", fontName=font_reg, fontSize=8.0, leading=10.5, alignment=1, textColor=colors.HexColor("#334155"))
    s_v_val = ParagraphStyle("RLVVal", fontName=font_bold, fontSize=10.5, leading=13.5, alignment=1, textColor=colors.HexColor("#0F172A"))

    col_w3 = CONTENT_WIDTH / 3.0
    v_tbl = Table(
        [
            [_p_text(f"<b>{_esc(vm['verdict']['title'])}</b>", s_v_hdr), "", ""],
            [
                [_p_text("பொருத்தம் மதிப்பெண்", s_v_lbl), _p_text(f"<b>{vm['passed_count_11']} / 11</b>", s_v_val)],
                [_p_text("தோஷ சமநிலை", s_v_lbl), _p_text(f"<b>{_esc(vm['kuja_summary_ta'])}</b>", s_v_val)],
                [_p_text("அஷ்டகூட மதிப்பெண் (36)", s_v_lbl), _p_text(f"<b>{_esc(vm['ashtakoota_str'])} / 36</b>", s_v_val)],
            ],
        ],
        colWidths=[col_w3, col_w3, col_w3],
    )
    v_tbl.setStyle(TableStyle([
        ("SPAN", (0, 0), (2, 0)),
        ("BACKGROUND", (0, 0), (2, 0), colors.HexColor(v_hdr_bg)),
        ("BACKGROUND", (0, 1), (2, 1), colors.HexColor(v_bg)),
        ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor(v_border)),
        ("TOPPADDING", (0, 0), (2, 0), 6),
        ("BOTTOMPADDING", (0, 0), (2, 0), 6),
        ("TOPPADDING", (0, 1), (2, 1), 8),
        ("BOTTOMPADDING", (0, 1), (2, 1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(v_tbl)
    story.append(Spacer(1, 12))

    story.append(_p_text("<b>பொருத்த மதிப்பீடு</b>", s_sec_h3))
    p_rows: List[List[Any]] = [
        [
            _p_text("பொருத்தம்<br/>(கூட்டம்)", s_th),
            _p_text("விளக்கம்", s_th),
            _p_text("மணமகன்<br/>அம்சம்", s_th),
            _p_text("மணமகள்<br/>அம்சம்", s_th),
            _p_text("பொருத்தம்", s_th_c),
        ]
    ]
    for r in vm["matching_rows"]:
        p_rows.append([
            _p_text(f"<b>{_esc(r['label'])}</b>", s_td_b),
            _p_text(_esc(r["desc"]), s_td),
            _p_text(_esc(r["groom_val"]), s_td),
            _p_text(_esc(r["bride_val"]), s_td),
            _make_tick_drawing(bool(r["pass"])),
        ])

    p_tbl = Table(p_rows, colWidths=[96, 184, 92, 92, 74])
    p_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#94A3B8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (4, 1), (4, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(p_tbl)

    # ======================== PAGE 2 ========================
    story.append(PageBreak())
    story.append(Spacer(1, 18))
    c_drawings = [_make_south_chart_drawing(ch, font_reg, font_bold, width=215.0) for ch in vm["charts"]]
    charts_tbl = Table(
        [
            [c_drawings[0], c_drawings[1]],
            [c_drawings[2], c_drawings[3]],
        ],
        colWidths=[CONTENT_WIDTH / 2.0, CONTENT_WIDTH / 2.0],
        rowHeights=[265, 250],
    )
    charts_tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(charts_tbl)

    # ======================== PAGE 3 ========================
    story.append(PageBreak())
    story.append(_p_text("<b>தோஷ ஆய்வு</b>", s_sec_h2))

    def _dosha_cell_flow(cell: Dict[str, Any] | None) -> _RLParagraph:
        if not cell or cell.get("status") == "NONE":
            return _p_text("இல்லை", s_dosha_none)
        is_mit = cell.get("status") == "MITIGATED"
        st = s_dosha_mit if is_mit else s_dosha_pres
        hdr = (
            "<b>தோஷ நிவர்த்தி</b>"
            if is_mit
            else f"<b>தோஷம் உள்ளது (Effective Dosha Severity: {cell.get('severity_percent', 40)}%)</b>"
        )
        reasons = cell.get("reasons_ta") or []
        parts = [hdr]
        if reasons:
            parts.append("<b>காரணங்கள்:</b>")
            for r in reasons:
                parts.append(f"&nbsp;&nbsp;{_esc(r)}")
        return _p_text("<br/>".join(parts), st)

    d_rows: List[List[Any]] = [
        [
            _p_text("தோஷ வகை", s_th),
            _p_text("மணமகன் ஜாதகம்", s_th),
            _p_text("மணமகள் ஜாதகம்", s_th),
        ]
    ]
    for row in vm["dosha_audit"]:
        d_rows.append([
            _p_text(f"<b>{_esc(row.get('label_ta'))}</b>", s_td_b),
            _dosha_cell_flow(row.get("groom")),
            _dosha_cell_flow(row.get("bride")),
        ])
    d_tbl = Table(d_rows, colWidths=[128, 205, 205])
    d_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#94A3B8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(d_tbl)

    # ======================== PAGE 4 ========================
    story.append(PageBreak())
    story.append(_p_text("<b>Dasa Bhukti Sequence</b>", s_sec_h2))
    s_col_g = ParagraphStyle("RLColG", fontName=font_bold, fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#0F172A"))
    col_hdr_tbl = Table(
        [[_p_text("மணமகன்", s_col_g), "", _p_text("மணமகள்", s_col_g)]],
        colWidths=[165, CONTENT_WIDTH - 330, 165],
    )
    story.append(col_hdr_tbl)
    story.append(Spacer(1, 6))
    story.append(_make_dasa_timeline_drawing(vm["timeline"], font_reg, font_bold, draw_w=CONTENT_WIDTH, draw_h=650.0))

    # ======================== PAGE 5 ========================
    story.append(PageBreak())
    story.append(_p_text("<b>தசா சந்தி ஆய்வு</b>", s_sec_h2))

    ds = vm["dasa_sandhi"]
    has_sandhi = bool(ds.get("has_sandhi"))
    ds_bg = "#FFF1F2" if has_sandhi else "#ECFDF5"
    ds_border = "#FECDD3" if has_sandhi else "#A7F3D0"
    ds_txt_col = "#9F1239" if has_sandhi else "#065F46"
    s_ds_hdr = ParagraphStyle("RLDSH", fontName=font_bold, fontSize=9.5, leading=13, textColor=colors.HexColor(ds_txt_col))
    s_ds_body = ParagraphStyle("RLDSB", fontName=font_reg, fontSize=8.5, leading=12, textColor=colors.HexColor(ds_txt_col))
    s_ds_note = ParagraphStyle("RLDSN", fontName=font_reg, fontSize=8.0, leading=11, textColor=colors.HexColor("#475569"))

    ds_tbl = Table(
        [[
            [
                _p_text(f"<b>{'நிலை: இருக்கிறது' if has_sandhi else 'நிலை: இல்லை'}</b>", s_ds_hdr),
                Spacer(1, 3),
                _p_text(_esc(ds.get("summary_ta")), s_ds_body),
                Spacer(1, 3),
                _p_text(_esc(ds.get("note_ta")), s_ds_note),
            ]
        ]],
        colWidths=[CONTENT_WIDTH],
    )
    ds_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(ds_bg)),
        ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor(ds_border)),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(ds_tbl)
    story.append(Spacer(1, 14))

    story.append(_p_text("<b>கிரக நிலைகள் ஆய்வு (கிரக பகுப்பாய்வு)</b>", s_sec_h2))

    s_harm = ParagraphStyle("RLHarm", fontName=font_reg, fontSize=8.2, leading=11, textColor=colors.HexColor("#047857"))
    s_incomp = ParagraphStyle("RLInc", fontName=font_reg, fontSize=8.2, leading=11, textColor=colors.HexColor("#BE123C"))
    s_empty = ParagraphStyle("RLEmp", fontName=font_reg, fontSize=8.2, leading=11, textColor=colors.HexColor("#475569"))

    def _build_pa_table(items: List[Dict[str, Any]], txt_style: ParagraphStyle, empty_msg: str, empty_style: ParagraphStyle) -> Table:
        rows: List[List[Any]] = [
            [
                _p_text("மணமகனின்<br/>கிரகம்", s_th),
                _p_text("மணமகளின்<br/>கிரகம்", s_th),
                _p_text("விளக்கம்", s_th),
            ]
        ]
        spans: List[tuple] = []
        if items:
            for item in items:
                rows.append([
                    _p_text(_esc(item.get("groom_planet_ta")), txt_style),
                    _p_text(_esc(item.get("bride_planet_ta")), txt_style),
                    _p_text(_esc(item.get("description_ta")), txt_style),
                ])
        else:
            rows.append([_p_text(empty_msg, empty_style), "", ""])
            spans.append(("SPAN", (0, 1), (2, 1)))
        tbl = Table(rows, colWidths=[96, 96, CONTENT_WIDTH - 192])
        ts = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#94A3B8")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ] + spans
        tbl.setStyle(TableStyle(ts))
        return tbl

    story.append(_p_text("<b>பொருத்தமான இணைப்புகள்</b>", s_sub_h3))
    story.append(
        _build_pa_table(
            vm["harmonious_connections"],
            s_harm,
            "இரு ஜாதகங்களிலும் ஒரே ராசியில் இணையும் சுப கிரக அமைப்புகள் குறைவாக உள்ளன; நட்சத்திரப் பொருத்தம் அடிப்படையில் மதிப்பீடு செய்யப்பட்டது.",
            s_empty,
        )
    )
    story.append(Spacer(1, 10))

    story.append(_p_text("<b>பொருத்தமற்ற சேர்க்கைகள்</b>", s_sub_h3))
    story.append(
        _build_pa_table(
            vm["incompatible_combinations"],
            s_incomp,
            "பொருத்தமற்ற எதிர்மறை கிரக சேர்க்கைகள் எதுவும் கண்டறியப்படவில்லை.",
            s_harm,
        )
    )
    story.append(Spacer(1, 14))

    story.append(_p_text("<b>முனிவரின் வாக்கு</b>", s_sec_h2))
    story.append(_p_text(_esc(vm["sage_verdict_ta"]), s_sage))

    # ======================== PAGE 6 ========================
    story.append(PageBreak())
    p6 = vm["page6"]
    s_p6_h = ParagraphStyle("RLP6H", fontName=font_bold, fontSize=12.5, leading=16, textColor=colors.HexColor("#0F172A"))
    s_p6_badge = ParagraphStyle(
        "RLP6B",
        fontName=font_bold,
        fontSize=8.0,
        leading=10.5,
        alignment=2,
        textColor=colors.HexColor("#047857" if p6["ashtakoota_threshold_met"] else "#BE123C"),
    )
    p6_hdr = Table(
        [
            [
                _p_text("<b>அஷ்டகூட (36) &amp; கூடுதல் பொருத்த ஆய்வுகள்</b>", s_p6_h),
                _p_text(
                    f"<b>மொத்தம்: {p6['ashtakoota_total_str']} / 36 (குறைந்தபட்சம் {p6['ashtakoota_threshold_str']})</b>",
                    s_p6_badge,
                ),
            ]
        ],
        colWidths=[CONTENT_WIDTH * 0.62, CONTENT_WIDTH * 0.38],
    )
    p6_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(p6_hdr)

    s_p6_td = ParagraphStyle("RLP6Td", fontName=font_reg, fontSize=7.8, leading=10.0, textColor=colors.HexColor("#1E293B"))
    s_p6_tdb = ParagraphStyle("RLP6TdB", fontName=font_bold, fontSize=7.8, leading=10.0, textColor=colors.HexColor("#0F172A"))
    s_p6_tdc = ParagraphStyle("RLP6TdC", fontName=font_bold, fontSize=7.8, leading=10.0, alignment=1, textColor=colors.HexColor("#0F172A"))

    ash_rows: List[List[Any]] = [
        [
            _p_text("கூடம் (Koota)", s_th),
            _p_text("விளக்கம் &amp; விலக்கு", s_th),
            _p_text("மதிப்பெண்", s_th_c),
            _p_text("நிலை", s_th_c),
        ]
    ]
    for r in p6["ashtakoota_rows"]:
        tone_col = "#047857" if r["status_tone"] == "green" else ("#B45309" if r["status_tone"] == "amber" else "#BE123C")
        s_st = ParagraphStyle(f"RLA_{r['id']}", fontName=font_bold, fontSize=7.8, leading=10.0, alignment=1, textColor=colors.HexColor(tone_col))
        sig_html = _esc(r["sig_ta"])
        if r.get("cancel_reason"):
            sig_html += f"<br/><font color='#047857'><b>விலக்கு: {_esc(r['cancel_reason'])}</b></font>"
        ash_rows.append([
            _p_text(f"<b>{_esc(r['label_ta'])}</b>", s_p6_tdb),
            _p_text(sig_html, s_p6_td),
            _p_text(f"{_esc(r['earned_str'])} / {_esc(r['max_str'])}", s_p6_tdc),
            _p_text(f"<b>{_esc(r['status_ta'])}</b>", s_st),
        ])

    ash_tbl = Table(ash_rows, colWidths=[122, CONTENT_WIDTH - 262, 66, 74])
    ash_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#94A3B8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ash_tbl)
    story.append(Spacer(1, 8))

    # 2-column Papasamya & KP cards
    papa = p6["papasamya"]
    kp = p6["kp"]
    s_card_t = ParagraphStyle("RLCT", fontName=font_bold, fontSize=8.8, leading=11.5, textColor=colors.HexColor("#0F172A"))
    s_card_b = ParagraphStyle("RLCB", fontName=font_reg, fontSize=7.7, leading=10.5, textColor=colors.HexColor("#1E293B"))

    papa_flow = [
        _p_text("<b>தென் இந்திய பாபசாம்யம் (Papasamya)</b>", s_card_t),
        Spacer(1, 3),
        _p_text(
            f"மணமகன்: <b>{_esc(papa['groom_total'])}</b> | மணமகள்: <b>{_esc(papa['bride_total'])}</b> | வித்தியாசம்: <b>{_esc(papa['diff_str'])}</b>",
            s_card_b,
        ),
        _p_text(f"மணமகன்: {_esc(papa['groom_frames'])}", s_card_b),
        _p_text(f"மணமகள்: {_esc(papa['bride_frames'])}", s_card_b),
        Spacer(1, 2),
        _p_text(f"<b>தீர்ப்பு: {_esc(papa['verdict_ta'])}</b> — {_esc(papa['explanation_ta'])}", s_card_b),
    ]
    if kp["available"]:
        kp_flow = [
            _p_text("<b>கே.பி (KP) 7-ஆம் உப அதிபதி &amp; ஆளுமை கிரகங்கள்</b>", s_card_t),
            Spacer(1, 3),
            _p_text(f"மணமகன் 7-ஆம் உப அதிபதி: <b>{_esc(kp['groom_csl_ta'])}</b> ({_esc(kp['groom_verdict_ta'])}) | பாவங்கள்: [{_esc(kp['groom_houses'])}]", s_card_b),
            _p_text(f"மணமகள் 7-ஆம் உப அதிபதி: <b>{_esc(kp['bride_csl_ta'])}</b> ({_esc(kp['bride_verdict_ta'])}) | பாவங்கள்: [{_esc(kp['bride_houses'])}]", s_card_b),
            Spacer(1, 2),
            _p_text(f"<b>ஆளுமை கிரக ஒப்பீடு:</b> {_esc(kp['agreement_ta'])} | பொது: {_esc(kp['shared_rp_ta'])}", s_card_b),
        ]
    else:
        kp_flow = [
            _p_text("<b>கே.பி (KP) 7-ஆம் உப அதிபதி &amp; ஆளுமை கிரகங்கள்</b>", s_card_t),
            Spacer(1, 3),
            _p_text("கே.பி (KP) 7-ஆம் உப அதிபதி தரவு சேர்க்கப்படவில்லை.", s_card_b),
        ]

    half_w = (CONTENT_WIDTH - 8) / 2.0
    cards_tbl = Table([[papa_flow, "", kp_flow]], colWidths=[half_w, 8, half_w])
    cards_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (0, 0), 0.7, colors.HexColor("#CBD5E1")),
        ("BOX", (2, 0), (2, 0), 0.7, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, 0), 7),
        ("RIGHTPADDING", (0, 0), (0, 0), 7),
        ("LEFTPADDING", (2, 0), (2, 0), 7),
        ("RIGHTPADDING", (2, 0), (2, 0), 7),
    ]))
    story.append(cards_tbl)
    story.append(Spacer(1, 8))

    # Special Insights Panel (Guru Balam, Nandi Yogam, In-Laws, Navamsa)
    guru = p6["guru_balam"]
    nadi_y = p6["nadi_yogam"]
    in_laws = p6["in_laws"]
    nav = p6["navamsa"]
    rem = p6["remedies"]

    panel_flows: List[Any] = [
        _p_text("<b>கோட்சார குரு பலம், நாடி &amp; நவாம்ச சிறப்பு ஆய்வு</b>", s_card_t),
        Spacer(1, 3),
        _p_text(
            f"<b>கோட்சார குரு பலம்:</b> {_esc(guru['label_ta'])}" + (f" — {_esc(guru['description_ta'])}" if guru["description_ta"] else ""),
            s_card_b,
        ),
    ]
    if nadi_y["available"]:
        panel_flows.append(_p_text(f"<b>நாடிப் பொருத்தம் &amp; நந்தியோகம்:</b> {_esc(nadi_y['verdict_ta'])}", s_card_b))
        for obs in nadi_y.get("obstacles_ta") or []:
            panel_flows.append(_p_text(f"&nbsp;&nbsp;• {_esc(obs)}", s_card_b))
    if in_laws["has_special"] and in_laws["findings"]:
        for f_item in in_laws["findings"]:
            st_lbl = "விதிவிலக்கு பொருந்தியது (தோஷமில்லை)" if f_item["is_exempt"] else "கவனம் தேவை"
            panel_flows.append(
                _p_text(f"<b>{_esc(f_item['nakshatra_ta'])} ({_esc(f_item['relative_ta'])}):</b> {st_lbl} — {_esc(f_item['explanation_ta'])}", s_card_b)
            )
    else:
        panel_flows.append(_p_text("<b>மாமனார்/மாமியார் விசேஷ நட்சத்திர ஆய்வு:</b> விசேஷ நட்சத்திர தோஷம் எதுவும் இல்லை.", s_card_b))
    panel_flows.append(_p_text(f"<b>நவாம்ச (D9) நிலை:</b> {_esc(nav['groom_ta'])} | {_esc(nav['bride_ta'])}", s_card_b))
    if nav["boundary_warning"]:
        s_warn = ParagraphStyle("RLNW", fontName=font_bold, fontSize=7.7, leading=10.5, textColor=colors.HexColor("#B45309"))
        panel_flows.append(_p_text("நேர எச்சரிக்கை: பிறப்பு நேர சிறு மாற்றத்தால் நவாம்ச லக்னம் மாற வாய்ப்புள்ளது.", s_warn))

    sp_tbl = Table([[panel_flows]], colWidths=[CONTENT_WIDTH])
    sp_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sp_tbl)
    story.append(Spacer(1, 8))

    # Primary Parikara Sthalam & Remedies
    s_rem_h = ParagraphStyle("RLRemH", fontName=font_bold, fontSize=8.5, leading=11, textColor=colors.HexColor("#92400E"))
    rem_txt = f"<b>{_esc(rem['temple_name_ta'])}</b> — {_esc(rem['temple_sig_ta'])}"
    if rem["hymn_title_ta"]:
        rem_txt += f" | <b>பரிந்துரைக்கப்படும் பாராயணம்:</b> {_esc(rem['hymn_title_ta'])}"
    rem_tbl = Table(
        [[[_p_text("<b>முதன்மை பரிகார ஸ்தலம் &amp; வழிகாட்டுதல்</b>", s_rem_h), Spacer(1, 2), _p_text(rem_txt, s_card_b)]]],
        colWidths=[CONTENT_WIDTH],
    )
    rem_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#FDE68A")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(rem_tbl)
    story.append(Spacer(1, 6))

    s_disc = ParagraphStyle("RLDisc", fontName=font_reg, fontSize=7.2, leading=9.8, textColor=colors.HexColor("#64748B"))
    story.append(
        _p_text(
            "குறிப்பு: இந்த அறிக்கை பாரம்பரிய தமிழ் பொருத்தம், 36 அஷ்டகூடம், பாபசாம்யம், வேத மற்றும் கே.பி. (KP) ஜோதிட விதிகளின் அடிப்படையில் தயாரிக்கப்பட்டது; இறுதி திருமண முடிவிற்கு குடும்ப ஆலோசனையும் சுப முகூர்த்த தேர்வும் பரிந்துரைக்கப்படுகிறது.",
            s_disc,
        )
    )

    doc.build(story)
    return buffer.getvalue()
