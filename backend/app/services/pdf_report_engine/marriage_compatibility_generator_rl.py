"""Royal Navy & Temple Gold Comprehensive Marriage Compatibility ReportLab Generator.

Fallback renderer for environments without headless Chromium (e.g. Render 512 MB).
Consumes `build_marriage_dossier_view_model` so all website compatibility sections,
charts, Dasa Bhukti timeline bars/arrows, Sivadasan Ravi remedies, and blessings are
compiled cleanly inside double Navy/Gold page borders with dynamic `Page X of N`.
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
from reportlab.pdfgen import canvas
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
from app.services.pdf_report_engine.fonts import (
    register_report_fonts,
    reorder_tamil_for_pdf,
    Paragraph as _RLParagraph,
    String as _RLString,
)
from app.services.pdf_report_engine.marriage_dossier_viewmodel import (
    build_marriage_dossier_view_model,
    get_status_style,
)
from app.services.pdf_report_engine.marriage_print_viewmodel import DASA_COLORS
from app.services.pdf_report_engine.letterhead_renderer import (
    GAILetterheadCanvas,
    PAGE_SIZE,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    LEFT_MARGIN,
    RIGHT_MARGIN,
    USABLE_WIDTH,
)

logger = logging.getLogger("gai.pdf.marriage_generator_rl")

NAVY = colors.HexColor("#153F6B")
GOLD = colors.HexColor("#B4872B")
GOLD_LIGHT = colors.HexColor("#D8BD80")
PARCHMENT = colors.HexColor("#FAF2DE")
SLATE_BORDER = colors.HexColor("#CBD5E1")
ZEBRA = colors.HexColor("#F8FAFC")

MARGIN_PT = LEFT_MARGIN
CONTENT_WIDTH = USABLE_WIDTH
MarriageDossierCanvas = GAILetterheadCanvas


def _esc(val: Any) -> str:
    return html.escape(str(val if val is not None else ""))


def _p(text: Any, style: ParagraphStyle) -> _RLParagraph:
    return _RLParagraph(text, style)


def _make_tick_drawing(passed: bool) -> Drawing:
    d = Drawing(11, 11)
    if passed:
        col = colors.HexColor("#047857")
        d.add(Line(1.8, 5.2, 4.4, 2.2, strokeColor=col, strokeWidth=1.5))
        d.add(Line(4.4, 2.2, 9.5, 8.8, strokeColor=col, strokeWidth=1.5))
    else:
        col = colors.HexColor("#BE123C")
        d.add(Line(2.2, 2.2, 8.8, 8.8, strokeColor=col, strokeWidth=1.4))
        d.add(Line(2.2, 8.8, 8.8, 2.2, strokeColor=col, strokeWidth=1.4))
    return d


def _make_chart_drawing(chart: Dict[str, Any], font_reg: str, font_bold: str, width: float = 195.0) -> Drawing:
    title_h = 16.0
    d = Drawing(width, width + title_h)
    step = width / 4.0

    d.add(
        _RLString(
            width / 2.0,
            width + 4.0,
            reorder_tamil_for_pdf(chart["title"]),
            fontName=font_bold,
            fontSize=9.0,
            fillColor=NAVY,
            textAnchor="middle",
        )
    )
    d.add(Rect(0, 0, width, width, fillColor=colors.white, strokeColor=NAVY, strokeWidth=1.4))
    d.add(Rect(step, step, 2 * step, 2 * step, fillColor=PARCHMENT, strokeColor=SLATE_BORDER, strokeWidth=0.6))

    for idx in (1, 2, 3):
        pos = idx * step
        if idx == 2:
            d.add(Line(pos, 0, pos, step, strokeColor=SLATE_BORDER, strokeWidth=0.7))
            d.add(Line(pos, 3 * step, pos, width, strokeColor=SLATE_BORDER, strokeWidth=0.7))
            d.add(Line(0, pos, step, pos, strokeColor=SLATE_BORDER, strokeWidth=0.7))
            d.add(Line(3 * step, pos, width, pos, strokeColor=SLATE_BORDER, strokeWidth=0.7))
        else:
            d.add(Line(pos, 0, pos, width, strokeColor=SLATE_BORDER, strokeWidth=0.7))
            d.add(Line(0, pos, width, pos, strokeColor=SLATE_BORDER, strokeWidth=0.7))

    d.add(
        _RLString(
            width / 2.0,
            width / 2.0 - 4.0,
            reorder_tamil_for_pdf(chart["center"]),
            fontName=font_bold,
            fontSize=9.0,
            fillColor=colors.HexColor("#8B6914"),
            textAnchor="middle",
        )
    )

    for sign_idx, (col, row) in SIGN_GRID_MAP.items():
        items = chart["cells"].get(sign_idx, [])
        if not items:
            continue
        cx, cy = col * step + step / 2.0, row * step + step / 2.0
        lh = 9.0
        start_y = cy + ((len(items) - 1) * lh) / 2.0 - 3.0
        for i, txt in enumerate(items[:5]):
            d.add(
                _RLString(
                    cx,
                    start_y - i * lh,
                    reorder_tamil_for_pdf(txt),
                    fontName=font_reg,
                    fontSize=7.4,
                    fillColor=colors.HexColor("#0F172A"),
                    textAnchor="middle",
                )
            )
    return d


def _make_dasa_timeline_drawing(tl: Dict[str, Any], font_reg: str, font_bold: str, draw_w: float = 528.0, draw_h: float = 430.0) -> Drawing:
    d = Drawing(draw_w, draw_h)
    sx, sy = draw_w / tl["svg_width"], draw_h / tl["svg_height"]
    y_for_year = tl["y_for_year"]
    now_y_s, current_yr, max_yr = tl["now_y"], tl["current_year_num"], tl["max_visible_year"]

    def rx(x: float) -> float:
        return x * sx

    def ry(y: float) -> float:
        return draw_h - (y * sy)

    def _side_rects(mds: List[Dict[str, Any]], xb: float, xy: float, anchor: str) -> None:
        bw = 145.0 * sx
        for idx, md in enumerate(mds):
            yts, ybs = y_for_year(md["start_year"]), y_for_year(md["end_year"])
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_act = float(md["start_year"]) < current_yr < float(md["end_year"])
            if is_act:
                y1t, y1b, y2b = ry(yts), ry(now_y_s), ry(ybs)
                d.add(Rect(rx(xb), y1b, bw, max(1.0, y1t - y1b), fillColor=colors.HexColor(col["light_bg"]), strokeColor=colors.white, strokeWidth=0.7))
                d.add(Rect(rx(xb), y2b, bw, max(1.0, y1b - y2b), fillColor=colors.HexColor(col["bg"]), strokeColor=colors.white, strokeWidth=0.7))
            else:
                yt, yb = ry(yts), ry(ybs)
                d.add(Rect(rx(xb), yb, bw, max(1.5, yt - yb), fillColor=colors.HexColor(col["bg"]), strokeColor=colors.white, strokeWidth=0.7))
            d.add(_RLString(rx(xy), ry(yts + 4.0), str(md.get("start_cal_year") or ""), fontName=font_reg, fontSize=7.4, fillColor=colors.HexColor("#475569"), textAnchor=anchor))
            if idx == len(mds) - 1:
                d.add(_RLString(rx(xy), ry(ybs + 3.0), str(md.get("end_cal_year") or ""), fontName=font_reg, fontSize=7.4, fillColor=colors.HexColor("#475569"), textAnchor=anchor))

    _side_rects(tl["g_visible_mds"], 70.0, 62.0, "end")
    _side_rects(tl["b_visible_mds"], 465.0, 618.0, "start")

    if tl["top_pad"] <= now_y_s <= tl["svg_height"] - tl["bot_pad"]:
        ny = ry(now_y_s)
        d.add(Line(rx(32.0), ny, rx(215.0), ny, strokeColor=colors.HexColor("#DC2626"), strokeWidth=1.2))
        nx = rx(30.0 if tl["now_collides_with_g_start"] else 60.0)
        na = "start" if tl["now_collides_with_g_start"] else "end"
        d.add(_RLString(nx, ry(now_y_s - 4.0), "Now", fontName=font_bold, fontSize=7.4, fillColor=colors.HexColor("#DC2626"), textAnchor=na))

    def _side_labels(mds: List[Dict[str, Any]], xc: float, avoid_now: bool) -> None:
        for md in mds:
            if float(md["start_year"]) >= max_yr:
                continue
            yts, ybs = y_for_year(md["start_year"]), y_for_year(md["end_year"])
            hs = max(2.0, ybs - yts)
            if hs < 18.0:
                continue
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_act = float(md["start_year"]) < current_yr < float(md["end_year"])
            tys = yts + hs / 2.0 + 4.0
            if avoid_now and is_act and abs(now_y_s - (yts + hs / 2.0)) < 11.0:
                uh, lh = now_y_s - yts, ybs - now_y_s
                tys = now_y_s + max(13.0, lh / 2.0 + 3.0) if lh >= uh else now_y_s - max(6.0, uh / 2.0 - 3.0)
            tys = min(ybs - 5.0, max(yts + 13.0, tys))
            d.add(_RLString(rx(xc), ry(tys), reorder_tamil_for_pdf(md.get("lord_ta") or ""), fontName=font_bold, fontSize=8.4, fillColor=colors.HexColor(col["text"]), textAnchor="middle"))

    _side_labels(tl["g_visible_mds"], 142.5, True)
    _side_labels(tl["b_visible_mds"], 537.5, False)

    red = colors.HexColor("#DC2626")
    x1, x2, xm = rx(221.0), rx(459.0), rx(340.0)
    for tr in tl["rendered_transitions"]:
        ya = ry(tr["y"])
        d.add(Line(x1 + 3.0, ya, x2 - 3.0, ya, strokeColor=red, strokeWidth=0.85))
        d.add(Polygon([x1, ya, x1 + 4.0, ya + 2.2, x1 + 4.0, ya - 2.2], fillColor=red, strokeColor=red))
        d.add(Polygon([x2, ya, x2 - 4.0, ya + 2.2, x2 - 4.0, ya - 2.2], fillColor=red, strokeColor=red))
        d.add(_RLString(xm, ry(tr["y"] - 3.0), reorder_tamil_for_pdf(tr["label_ta"]), fontName=font_bold, fontSize=7.0, fillColor=colors.HexColor("#7F1D1D"), textAnchor="middle"))

    return d


def generate_marriage_compatibility_pdf_bytes_rl(data: Dict[str, Any], language: str = "en") -> bytes:
    """Comprehensive Royal Navy & Gold ReportLab fallback PDF generator."""
    font_reg, font_bold = register_report_fonts()
    vm = build_marriage_dossier_view_model(data, language=language)
    is_ta = vm["is_ta"]
    base = vm["base"]
    ge, be = vm["groom_ext"], vm["bride_ext"]
    comp = vm["composite"]
    pf = vm["porutham_full"]
    af = vm["ashtakoota_full"]
    kf = vm["kuja_full"]
    pp = vm["papasamya_full"]
    vf = vm["vedic_full"]
    sf = vm["synastry_full"]
    kp = vm["kp_full"]
    sr = vm["sivadasan_full"]

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=PAGE_SIZE,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    s_brand = ParagraphStyle("RLB", fontName=font_bold, fontSize=15.0, leading=18, alignment=1, textColor=NAVY)
    s_addr = ParagraphStyle("RLA", fontName=font_reg, fontSize=8.0, leading=10.5, alignment=1, textColor=colors.HexColor("#475569"))
    s_doc_sub = ParagraphStyle("RLDS", fontName=font_bold, fontSize=9.5, leading=12.5, alignment=1, textColor=colors.HexColor("#8B6914"))
    s_sec = ParagraphStyle("RLS", fontName=font_bold, fontSize=10.5, leading=14, textColor=colors.white)
    s_sub = ParagraphStyle("RLSub", fontName=font_bold, fontSize=9.0, leading=12, textColor=NAVY, spaceAfter=3)
    s_th = ParagraphStyle("RLTh", fontName=font_bold, fontSize=7.8, leading=10, textColor=colors.white)
    s_th_c = ParagraphStyle("RLThC", fontName=font_bold, fontSize=7.8, leading=10, alignment=1, textColor=colors.white)
    s_td = ParagraphStyle("RLTd", fontName=font_reg, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#0F172A"))
    s_tdb = ParagraphStyle("RLTdB", fontName=font_bold, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#0F172A"))
    s_tdc = ParagraphStyle("RLTdC", fontName=font_bold, fontSize=7.8, leading=10.2, alignment=1, textColor=colors.HexColor("#0F172A"))
    s_td_sm = ParagraphStyle("RLTdSm", fontName=font_reg, fontSize=7.0, leading=8.8, textColor=colors.HexColor("#0F172A"))
    s_tdb_sm = ParagraphStyle("RLTdBSm", fontName=font_bold, fontSize=7.0, leading=8.8, textColor=colors.HexColor("#0F172A"))
    s_tdc_sm = ParagraphStyle("RLTdCSm", fontName=font_bold, fontSize=7.0, leading=8.8, alignment=1, textColor=colors.HexColor("#0F172A"))
    s_body = ParagraphStyle("RLBo", fontName=font_reg, fontSize=8.2, leading=11.2, textColor=colors.HexColor("#1E293B"))
    s_ctr = ParagraphStyle("RLCtr", fontName=font_reg, fontSize=8.2, leading=11.2, alignment=1, textColor=NAVY)

    def _sec_banner(title: str) -> Table:
        t = Table([[_p(f"<b>{_esc(title)}</b>", s_sec)]], colWidths=[CONTENT_WIDTH])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("LINEBEFORE", (0, 0), (0, -1), 3.5, GOLD_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    def _styled_tbl(rows: List[List[Any]], widths: List[float], pad_v: float = 3.2, repeat_rows: int = 1) -> Table:
        t = Table(rows, colWidths=widths, repeatRows=repeat_rows)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), pad_v),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return t

    story: List[Any] = []

    # ==================== PAGE 1: FAMILY DECISION SUMMARY ====================
    ds_vm = vm["decision_summary"]
    doc_title = (
        "திருமணப் பொருத்த அறிக்கை — குடும்ப முடிவுச் சுருக்கம்"
        if is_ta
        else "MARRIAGE COMPATIBILITY – FAMILY DECISION SUMMARY"
    )
    doc_sub = (
        "Gokul's Astrological Insights • எளிய குடும்ப முடிவுச் சுருக்கம்"
        if is_ta
        else "Gokul's Astrological Insights • Clear Family Decision Summary"
    )
    story.append(_p(f"<font color='{NAVY.hexval()}'><b>{doc_title}</b></font>", s_brand))
    story.append(_p(f"<font color='{GOLD.hexval()}'>{doc_sub}</font>", s_doc_sub))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1.0, color=GOLD_LIGHT, spaceBefore=1, spaceAfter=4))

    def _birth_card_p1(title: str, p: Dict[str, Any]) -> Table:
        s_p1_name = ParagraphStyle("RLP1N", fontName=font_bold, fontSize=9.0, leading=11.5, textColor=NAVY)
        s_p1_lbl = ParagraphStyle("RLP1L", fontName=font_reg, fontSize=7.7, leading=10.0, textColor=colors.HexColor("#475569"))
        s_p1_val = ParagraphStyle("RLP1V", fontName=font_reg, fontSize=7.7, leading=10.0, textColor=colors.HexColor("#0F172A"))
        lbl_name = "பெயர்" if is_ta else "Full Name"
        lbl_dob = "பிறந்த தேதி" if is_ta else "Date of Birth"
        lbl_age = "வயது" if is_ta else "Age"
        lbl_tob = "பிறந்த நேரம்" if is_ta else "Time of Birth"
        lbl_pob = "பிறந்த இடம்" if is_ta else "Place of Birth"
        lbl_rasi = "ராசி" if is_ta else "Rasi / Moon Sign"
        lbl_star = "நட்சத்திரம்" if is_ta else "Birth Star"
        lbl_pada = "பாதம்" if is_ta else "Pada"
        lbl_lagna = "லக்னம்" if is_ta else "Lagna / Ascendant"
        rows = [
            [_p(f"<b>{_esc(title)}</b>", s_th), ""],
            [_p(lbl_name, s_p1_lbl), _p(f"<b>{_esc(p['name'])}</b>", s_p1_name)],
            [_p(lbl_dob, s_p1_lbl), _p(_esc(p["dob_fmt"]), s_p1_val)],
            [_p(lbl_age, s_p1_lbl), _p(_esc(p["age_str"]), s_p1_val)],
            [_p(lbl_tob, s_p1_lbl), _p(_esc(p["tob"]), s_p1_val)],
            [_p(lbl_pob, s_p1_lbl), _p(_esc(p["birth_place"]), s_p1_val)],
            [_p(lbl_rasi, s_p1_lbl), _p(_esc(p["rasi_bilingual"]), s_p1_val)],
            [_p(lbl_star, s_p1_lbl), _p(_esc(p["nakshatra_only"]), s_p1_val)],
            [_p(lbl_pada, s_p1_lbl), _p(_esc(p["pada_str"]), s_p1_val)],
            [_p(lbl_lagna, s_p1_lbl), _p(_esc(p["lagna_clean"]), s_p1_val)],
        ]
        pt = Table(rows, colWidths=[76, (CONTENT_WIDTH - 10) / 2.0 - 76])
        pt.setStyle(TableStyle([
            ("SPAN", (0, 0), (1, 0)),
            ("BACKGROUND", (0, 0), (1, 0), NAVY),
            ("LINEBELOW", (0, 0), (1, 0), 1.5, GOLD_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.9, GOLD),
            ("LINEBELOW", (0, 1), (-1, -2), 0.35, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return pt

    half_w = (CONTENT_WIDTH - 10) / 2.0
    p_grid = Table(
        [[_birth_card_p1("மணமகன் / GROOM", ge), "", _birth_card_p1("மணமகள் / BRIDE", be)]],
        colWidths=[half_w, 10, half_w],
    )
    p_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(p_grid)
    if vm.get("birthplace_note"):
        story.append(Spacer(1, 2))
        s_bp_note = ParagraphStyle("RLBpNote", fontName=font_reg, fontSize=6.8, leading=8.5, alignment=1, textColor=colors.HexColor("#475569"))
        story.append(_p(_esc(vm["birthplace_note"]), s_bp_note))
    story.append(Spacer(1, 4))

    # 3. Large Overall Compatibility Verdict
    vd = ds_vm["verdict"]
    vd_st = get_status_style(vd["tone"])
    s_vd_title = ParagraphStyle("RLVdT", fontName=font_bold, fontSize=12.0, leading=15.0, alignment=1, textColor=colors.HexColor(vd_st["text"]))
    s_vd_sub = ParagraphStyle("RLVdS", fontName=font_reg, fontSize=8.0, leading=10.5, alignment=1, textColor=colors.HexColor(vd_st["text"]))
    vd_box = Table(
        [[_p(f"<b>{vd_st['icon']}  {_esc(vd['title_ta'])}  |  {_esc(vd['title_en'])}</b>", s_vd_title)], [_p(_esc(vd["subtitle"]), s_vd_sub)]],
        colWidths=[CONTENT_WIDTH],
    )
    vd_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(vd_st["bg"])),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(vd_st["border"])),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
        ("TOPPADDING", (0, 1), (-1, 1), 1),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(vd_box)
    story.append(Spacer(1, 4))

    # 4 & 5. Two Prominent Score Cards
    def _score_card(card: Dict[str, Any]) -> Table:
        cst = get_status_style(card["tone"])
        s_sc_hdr = ParagraphStyle("RLScH", fontName=font_bold, fontSize=8.5, leading=11.0, alignment=1, textColor=NAVY)
        s_sc_val = ParagraphStyle("RLScV", fontName=font_bold, fontSize=13.5, leading=16.0, alignment=1, textColor=colors.HexColor(cst["text"]))
        s_sc_st = ParagraphStyle("RLScS", fontName=font_bold, fontSize=8.0, leading=10.5, alignment=1, textColor=colors.HexColor(cst["text"]))
        ct = Table(
            [
                [_p(f"<b>{_esc(card['title'])}</b>", s_sc_hdr)],
                [_p(f"<b>{_esc(card['score_text'])}</b>", s_sc_val)],
                [_p(f"<b>{cst['icon']} {_esc(card['status_text'])}</b>", s_sc_st)],
            ],
            colWidths=[half_w],
        )
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(cst["bg"])),
            ("BOX", (0, 0), (-1, -1), 1.1, colors.HexColor(cst["border"])),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return ct

    score_grid = Table(
        [[_score_card(ds_vm["porutham_card"]), "", _score_card(ds_vm["ashtakoota_card"])]],
        colWidths=[half_w, 10, half_w],
    )
    score_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(score_grid)
    story.append(Spacer(1, 4))

    # 6 & 7. Positive Factors (GREEN) & Areas Requiring Attention (ORANGE / RED)
    def _factor_box(title: str, hdr_tone: str, items: List[Dict[str, str]]) -> Table:
        hst = get_status_style(hdr_tone)
        s_fh = ParagraphStyle("RLFH", fontName=font_bold, fontSize=8.5, leading=11.0, textColor=colors.white)
        rows: List[List[Any]] = [[_p(f"<b>{hst['icon']} {_esc(title)}</b>", s_fh)]]
        for it in items:
            ist = get_status_style(it["tone"])
            s_fi = ParagraphStyle("RLFI", fontName=font_reg, fontSize=7.6, leading=9.8, textColor=colors.HexColor(ist["text"]))
            rows.append([_p(f"<b>{ist['icon']}</b> {_esc(it['text'])}", s_fi)])
        ft = Table(rows, colWidths=[half_w])
        ts_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(hst["border"])),
            ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor(hst["border"])),
            ("TOPPADDING", (0, 0), (-1, -1), 2.0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]
        for idx, it in enumerate(items, start=1):
            ist = get_status_style(it["tone"])
            ts_cmds.append(("BACKGROUND", (0, idx), (0, idx), colors.HexColor(ist["bg"])))
            if idx < len(items):
                ts_cmds.append(("LINEBELOW", (0, idx), (0, idx), 0.4, colors.white))
        ft.setStyle(TableStyle(ts_cmds))
        return ft

    pos_title = "நல்ல அம்சங்கள் (Positive Factors)" if is_ta else "Positive Factors"
    attn_title = "கவனிக்க வேண்டிய அம்சங்கள் (Areas Requiring Attention)" if is_ta else "Areas Requiring Attention"
    attn_hdr_tone = "RED" if any(x["tone"] == "RED" for x in ds_vm["attention_factors"]) else "ORANGE"
    fac_grid = Table(
        [[_factor_box(pos_title, "GREEN", ds_vm["positive_factors"]), "", _factor_box(attn_title, attn_hdr_tone, ds_vm["attention_factors"])]],
        colWidths=[half_w, 10, half_w],
    )
    fac_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(fac_grid)
    story.append(Spacer(1, 4))

    # 8. Family-Friendly Final Recommendation
    rec_title = "எங்களின் பரிந்துரை (Our Recommendation)" if is_ta else "Our Recommendation"
    s_p1_rec = ParagraphStyle("RLP1Rec", fontName=font_reg, fontSize=8.0, leading=11.0, textColor=colors.HexColor("#0F172A"))
    rec_box = Table(
        [[_p(f"<b>{_esc(rec_title)}:</b><br/>{_esc(ds_vm['recommendation'])}", s_p1_rec)]],
        colWidths=[CONTENT_WIDTH],
    )
    rec_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PARCHMENT),
        ("BOX", (0, 0), (-1, -1), 1.0, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 4.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.0),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(rec_box)
    story.append(Spacer(1, 3))

    # 9. Short First-Page Disclaimer
    s_disc_p1 = ParagraphStyle("RLDiscP1", fontName=font_reg, fontSize=7.0, leading=9.0, alignment=1, textColor=colors.HexColor("#475569"))
    story.append(_p(_esc(ds_vm["disclaimer"]), s_disc_p1))

    # ==================== PAGE 2: CHARTS & PLANETARY POSITIONS ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"2. {'ஜாதகக் கட்டங்கள் (D1 & D9) மற்றும் கிரக நிலைகள்' if is_ta else 'Dual Kundli Charts (D1 Rasi & D9 Navamsa) & Planetary Degrees'}"))
    story.append(Spacer(1, 3))
    c_drawings = [_make_chart_drawing(ch, font_reg, font_bold, width=124.0) for ch in base["charts"]]
    ct_tbl = Table([[c_drawings[0], c_drawings[1]], [c_drawings[2], c_drawings[3]]], colWidths=[CONTENT_WIDTH / 2.0, CONTENT_WIDTH / 2.0])
    ct_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    story.append(ct_tbl)
    story.append(Spacer(1, 2))

    def _p_tbl(p_rows: List[Dict[str, str]], title: str) -> Table:
        c1 = "கிரகம்" if is_ta else "Planet"
        c2 = "ராசி" if is_ta else "Rasi"
        c3 = "பாகை" if is_ta else "Deg"
        c4 = "நவாம்சம்" if is_ta else "D9"
        rows: List[List[Any]] = [[_p(f"<b>{_esc(title)}</b>", s_th), "", "", ""], [_p(c1, s_th), _p(c2, s_th), _p(c3, s_th), _p(c4, s_th)]]
        for r in (p_rows[:10] if p_rows else []):
            mot = f" ({r['retro']})" if r["retro"] != "-" else ""
            rows.append([_p(f"<b>{_esc(r['planet'])}{_esc(mot)}</b>", s_tdb_sm), _p(_esc(r["sign"]), s_td_sm), _p(_esc(r["degree"]), s_td_sm), _p(_esc(r["d9_sign"]), s_td_sm)])
        if len(rows) == 2:
            rows.append([_p("-", s_td_sm), _p("-", s_td_sm), _p("-", s_td_sm), _p("-", s_td_sm)])
        t = Table(rows, colWidths=[76, 66, 46, half_w - 188], repeatRows=2)
        t.setStyle(TableStyle([("SPAN", (0, 0), (3, 0)), ("BACKGROUND", (0, 0), (-1, 1), NAVY), ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER), ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, ZEBRA]), ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
        return t

    g_pl_hdr = f"மணமகன் கிரக நிலைகள் ({ge['name']})" if is_ta else f"Groom Planets ({ge['name']})"
    b_pl_hdr = f"மணமகள் கிரக நிலைகள் ({be['name']})" if is_ta else f"Bride Planets ({be['name']})"
    pt_side = Table([[_p_tbl(vm["groom_planets"], g_pl_hdr), "", _p_tbl(vm["bride_planets"], b_pl_hdr)]], colWidths=[half_w, 10, half_w])
    pt_side.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(pt_side)

    # ==================== PAGE 3: TAMIL 10 PORUTHAMS ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"3. {'தமிழ் 10 பொருத்தங்கள்' if is_ta else 'Tamil 10 Poruthams Analysis'} ({pf['total_score']} / {pf['max_score']} • Rajju: {pf['rajju_status']} • Vedha: {pf['vedha_status']})"))
    story.append(Spacer(1, 2))
    p_c1 = "பொருத்தம்" if is_ta else "Porutham"
    p_c2 = "மதிப்." if is_ta else "Score"
    p_c3 = "தரம்" if is_ta else "Grade"
    p_c4 = "நட்சத்திர இணை" if is_ta else "Pair"
    p_c5 = "விளக்கம் & பலன்" if is_ta else "Evaluation & Meaning"
    por_rows: List[List[Any]] = [[_p(p_c1, s_th), _p(p_c2, s_th_c), _p(p_c3, s_th_c), _p(p_c4, s_th), _p(p_c5, s_th)]]
    for r in pf["rows"]:
        por_rows.append([_p(f"<b>{_esc(r['name'])}</b>", s_tdb_sm), _p(f"<b>{_esc(r['score'])}</b>", s_tdc_sm), _p(_esc(r["grade"]), s_tdc_sm), _p(_esc(r["pair"]), s_td_sm), _p(_esc(r["desc"]), s_td_sm)])
    story.append(_styled_tbl(por_rows, [86, 40, 58, 72, CONTENT_WIDTH - 256], pad_v=1.1))
    story.append(Spacer(1, 2))

    passed_11 = sum(1 for mr in pf["checklist_11"] if mr.get("pass"))
    chk_note = (
        f"குறிப்பு: மேலே உள்ள 10 பொருத்தங்கள் எடை மதிப்பெண் முறையில் ({pf['total_score']}/{pf['max_score']}); "
        f"கீழே உள்ள 11-அம்ச சுருக்கப் பட்டியல் 10 பொருத்தங்கள் + அஷ்டகூட நாடி ஆகியவற்றை தேர்ச்சி/தோல்வி அடிப்படையில் ({passed_11}/11) காட்டுகிறது."
        if is_ta
        else f"Note: The 10 Poruthams above use weighted scoring ({pf['total_score']}/{pf['max_score']}); the 11-point checklist below evaluates the 10 Poruthams plus Ashtakoota Nadi as binary Pass/Fail ({passed_11}/11)."
    )
    story.append(_p(f"<i>{_esc(chk_note)}</i>", s_td_sm))
    story.append(Spacer(1, 2))
    chk_h1 = f"11-அம்ச பாரம்பரியச் சுருக்கப் பட்டியல் ({passed_11}/11)" if is_ta else f"11-Point Summary Checklist ({passed_11}/11)"
    chk_h2 = "மணமகன்" if is_ta else "Groom"
    chk_h3 = "மணமகள்" if is_ta else "Bride"
    chk_h4 = "நிலை" if is_ta else "Status"
    chk_rows: List[List[Any]] = [[_p(chk_h1, s_th), _p(chk_h2, s_th), _p(chk_h3, s_th), _p(chk_h4, s_th_c)]]
    for mr in pf["checklist_11"]:
        chk_rows.append([_p(f"<b>{_esc(mr['label'])}</b>", s_tdb_sm), _p(_esc(mr["groom_val"]), s_td_sm), _p(_esc(mr["bride_val"]), s_td_sm), _make_tick_drawing(bool(mr["pass"]))])
    story.append(_styled_tbl(chk_rows, [145, 142, 142, CONTENT_WIDTH - 429], pad_v=1.0))

    # ==================== PAGE 4: ASHTAKOOTA 36 + KUJA + PAPASAMYA ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"4. {'வட இந்திய 36 அஷ்டகூட ஆய்வு' if is_ta else 'North Indian 36-Point Ashtakoota Analysis'} ({af['total']} / {af['max']})"))
    story.append(Spacer(1, 6))
    ash_rows: List[List[Any]] = [[_p("Koota", s_th), _p("Calculation", s_th), _p("Pts", s_th_c), _p("Status", s_th_c), _p("Interpretation", s_th)]]
    for r in af["rows"]:
        st_txt = "CANCELLED" if r["is_cancelled"] else r["status"]
        desc_html = _esc(r["desc"]) + (f"<br/><b>Cancellation:</b> {_esc(r['cancel_reason'])}" if r["cancel_reason"] else "")
        ash_rows.append([_p(f"<b>{_esc(r['name'])}</b>", s_tdb), _p(_esc(r["raw_calc"] or "-"), s_td), _p(f"<b>{_esc(r['earned'])}/{_esc(r['max'])}</b>", s_tdc), _p(st_txt, s_tdc), _p(desc_html, s_td)])
    story.append(_styled_tbl(ash_rows, [96, 118, 44, 58, CONTENT_WIDTH - 316], pad_v=3.0))
    story.append(Spacer(1, 8))

    story.append(_sec_banner(f"5. {'செவ்வாய் தோஷ சமதோஷம் & பாபசாம்யம்' if is_ta else 'Kuja Samadosham & South Indian Papasamya'}"))
    story.append(Spacer(1, 5))
    kj_tbl = Table([
        [_p(f"<b>Groom Kuja ({kf['groom']['severity']} • {kf['groom']['intensity']}%)</b>", s_th), _p(f"<b>Bride Kuja ({kf['bride']['severity']} • {kf['bride']['intensity']}%)</b>", s_th)],
        [
            _p(f"Mars H{kf['groom']['h_lagna']} Lagna / H{kf['groom']['h_moon']} Moon / H{kf['groom']['h_venus']} Venus<br/>{_esc(kf['groom']['explanation'])}", s_td),
            _p(f"Mars H{kf['bride']['h_lagna']} Lagna / H{kf['bride']['h_moon']} Moon / H{kf['bride']['h_venus']} Venus<br/>{_esc(kf['bride']['explanation'])}", s_td),
        ],
        [_p(f"<b>Papasamya:</b> Groom {_esc(pp['groom_total'])} pts | Bride {_esc(pp['bride_total'])} pts | Diff {_esc(pp['diff_str'])} — <b>{_esc(pp['verdict'])}</b><br/>{_esc(pp['expl'])}", s_td), ""],
    ], colWidths=[half_w + 5, half_w + 5])
    kj_tbl.setStyle(TableStyle([("SPAN", (0, 2), (1, 2)), ("BACKGROUND", (0, 0), (1, 0), NAVY), ("BACKGROUND", (0, 2), (1, 2), PARCHMENT), ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story.append(kj_tbl)

    # ==================== PAGE 5: 10-POINT DOSHA AUDIT ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"6. {'விரிவான 10-வகை தோஷ ஆய்வு' if is_ta else 'Comprehensive 10-Point Dosha Audit Matrix'}"))
    story.append(Spacer(1, 6))

    def _d_flow(cell: Dict[str, Any] | None) -> _RLParagraph:
        if not cell or cell.get("status") == "NONE":
            return _p("இல்லை", s_td)
        hdr = "<b>தோஷ நிவர்த்தி</b>" if cell.get("status") == "MITIGATED" else f"<b>தோஷம் உள்ளது (Severity: {cell.get('severity_percent', 40)}%)</b>"
        parts = [hdr] + [f"• {_esc(r)}" for r in (cell.get("reasons_ta") or [])]
        return _p("<br/>".join(parts), s_td)

    d_rows: List[List[Any]] = [[_p("Dosha Category", s_th), _p(f"Groom: {_esc(ge['name'])}", s_th), _p(f"Bride: {_esc(be['name'])}", s_th)]]
    for row in base["dosha_audit"]:
        d_rows.append([_p(f"<b>{_esc(row.get('label_ta'))}</b>", s_tdb), _d_flow(row.get("groom")), _d_flow(row.get("bride"))])
    story.append(_styled_tbl(d_rows, [120, (CONTENT_WIDTH - 120) / 2.0, (CONTENT_WIDTH - 120) / 2.0], pad_v=3.0))

    # ==================== PAGE 6: VEDIC HOUSES, SYNASTRY & KP ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"7. {'வேத களத்திர பாவங்கள், இருவழி இணைவு & கே.பி ஆய்வு' if is_ta else 'Vedic Houses (2,4,5,7,8,12), Synastry & KP 7th CSL'}"))
    story.append(Spacer(1, 5))
    for role_lbl, v_obj in [(f"Groom Vedic ({ge['name']})", vf["groom"]), (f"Bride Vedic ({be['name']})", vf["bride"])]:
        story.append(_p(f"<b>{_esc(role_lbl)}</b> — Lagna Lord: {_esc(v_obj['lagna_lord'])}", s_sub))
        if v_obj["houses"]:
            vh_rows: List[List[Any]] = [[_p("H", s_th_c), _p("Sign", s_th), _p("Lord", s_th), _p("Occupants / Aspects", s_th), _p("Status", s_th_c)]]
            for h in v_obj["houses"]:
                vh_rows.append([_p(f"<b>H{h['house_num']}</b>", s_tdc), _p(_esc(h["sign"]), s_td), _p(_esc(h["lord"]), s_td), _p(_esc(f"{h['occupants']} | {h['aspects']}"), s_td), _p(_esc(h["status"]), s_tdc)])
            story.append(_styled_tbl(vh_rows, [32, 74, 130, CONTENT_WIDTH - 288, 52], pad_v=2.0))
        elif v_obj["summary"]:
            story.append(_p(_esc(v_obj["summary"]), s_body))
        story.append(Spacer(1, 4))

    kp_rows: List[List[Any]] = [
        [_p("KP Partner", s_th), _p("7th CSL / Star", s_th), _p("Signified Houses", s_th), _p("Verdict", s_th_c)],
        [_p(f"<b>Groom</b>", s_tdb), _p(f"<b>{_esc(kp['groom']['sub_lord'])}</b> ({_esc(kp['groom']['star_lord'])})", s_td), _p(f"[{_esc(kp['groom']['signified'])}] (+{_esc(kp['groom']['supporting'])})", s_td), _p(_esc(kp["groom"]["verdict"]), s_tdc)],
        [_p(f"<b>Bride</b>", s_tdb), _p(f"<b>{_esc(kp['bride']['sub_lord'])}</b> ({_esc(kp['bride']['star_lord'])})", s_td), _p(f"[{_esc(kp['bride']['signified'])}] (+{_esc(kp['bride']['supporting'])})", s_td), _p(_esc(kp["bride"]["verdict"]), s_tdc)],
    ]
    story.append(_styled_tbl(kp_rows, [80, 145, CONTENT_WIDTH - 295, 70], pad_v=2.8))
    story.append(Spacer(1, 4))
    story.append(_p(f"<b>Ruling Planets Agreement:</b> {_esc(kp['agreement_level'])} | <b>Shared RP:</b> {_esc(kp['shared_rp'])}", s_body))
    if sf["available"]:
        story.append(_p(f"<b>Synastry Axes:</b> Moon-to-Moon: {_esc(sf['moon_to_moon']['rel'])} ({_esc(sf['moon_to_moon']['assessment'])}) • Lagna-to-Lagna: {_esc(sf['lagna_to_lagna']['rel'])}", s_body))

    # ==================== PAGE 7: DASA BHUKTI TIMELINE ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"8. {'தசா புக்தி காலவரிசை (Dasa Bhukti Sequence) & தசா சந்தி' if is_ta else 'Dasa Bhukti Sequence Timeline & Dasa Sandhi'}"))
    story.append(Spacer(1, 5))
    story.append(_make_dasa_timeline_drawing(base["timeline"], font_reg, font_bold, draw_w=CONTENT_WIDTH, draw_h=430.0))
    story.append(Spacer(1, 6))
    ds = base["dasa_sandhi"]
    ds_lbl = "தசா சந்தி" if is_ta else "Dasa Sandhi"
    ds_st = ("உள்ளது" if ds.get("has_sandhi") else "இல்லை") if is_ta else ("Present" if ds.get("has_sandhi") else "None")
    story.append(_p(f"<b>{ds_lbl} ({ds_st}):</b> {_esc(ds.get('summary_ta'))}", s_body))

    # ==================== PAGE 8: GOCHARA & REMEDIES ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"9. {'கோட்சார குரு பலம், நாடி ஆய்வு & பரிகார ஸ்தலம்' if is_ta else 'Gochara Guru Balam, Nadi Porutham & Parikara Remedies'}"))
    story.append(Spacer(1, 6))
    gb_hdr = "கோட்சார குரு பலம் (Gochara Guru Balam)" if is_ta else "Gochara Guru Balam"
    story.append(_p(f"<b>{gb_hdr}:</b> {_esc(sr['guru_balam']['label'])} ({_esc(sr['guru_balam']['transit_sign'])}) — {_esc(sr['guru_balam']['desc'])}", s_body))
    story.append(Spacer(1, 4))
    if sr["nadi_porutham"]["summary"]:
        nd_hdr = "நாடி ஜோதிட முறை பொருத்தம் (Sivadasan Ravi Nadi Porutham)" if is_ta else "Nadi Astrology Porutham (Sivadasan Ravi)"
        story.append(_p(f"<b>{nd_hdr}:</b> {_esc(sr['nadi_porutham']['verdict'])} — {_esc(sr['nadi_porutham']['summary'])}", s_body))
        story.append(Spacer(1, 4))
    ps_hdr = "பரிகார ஸ்தலம் (Parikara Sthalam)" if is_ta else "Parikara Sthalam"
    story.append(_p(f"<b>{ps_hdr}:</b> {_esc(sr['temple_name'])} — {_esc(sr['temple_sig'])}", s_body))
    for h_item in sr["hymns"][:2]:
        story.append(Spacer(1, 5))
        story.append(_p(f"<b>{_esc(h_item['title'])}</b> ({_esc(h_item['purpose'])})<br/>{_esc(h_item['verse']).replace(chr(10), '<br/>')}", s_body))

    # ==================== PAGE 9: FINAL VERDICT, TIMING & BLESSINGS ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"10. {'இறுதித் தீர்ப்பு, திருமண காலம் & மங்கள வாழ்த்து' if is_ta else 'Final Verdict, Marriage Timing & Auspicious Blessings'}"))
    story.append(Spacer(1, 5))
    fv = vm["final_verdict_p9"]
    story.append(_p(f"<b>{'ஒட்டுமொத்தப் பொருத்த முடிவு' if is_ta else 'Overall Compatibility'}:</b> {_esc(fv['overall_title'])}", s_sub))
    story.append(_p(_esc(fv["overall_line"]), s_body))
    story.append(Spacer(1, 4))
    if comp["categories"]:
        h_layer = "பிரிவு" if is_ta else "Layer"
        h_trad = "மரபு" if is_ta else "Tradition"
        h_stat = "நிலை" if is_ta else "Status"
        h_sum = "சுருக்கம்" if is_ta else "Summary"
        cat_rows_p9: List[List[Any]] = [[_p(h_layer, s_th), _p(h_trad, s_th), _p(h_stat, s_th_c), _p(h_sum, s_th)]]
        for c in comp["categories"]:
            cat_rows_p9.append([_p(f"<b>{_esc(c['name'])}</b>", s_tdb_sm), _p(_esc(c["tradition"]), s_td_sm), _p(f"<b>{_esc(c['status'])}</b>", s_tdc_sm), _p(_esc(c["summary"]), s_td_sm)])
        story.append(_styled_tbl(cat_rows_p9, [118, 112, 68, CONTENT_WIDTH - 298], pad_v=1.1))
        story.append(Spacer(1, 3))

    hier_rows: List[List[Any]] = [
        [_p(f"<b>{'நல்ல அம்சங்கள்' if is_ta else 'Positive Factors'}</b>", s_tdb_sm), _p(_esc(fv["positive_line"]), s_td_sm)],
        [_p(f"<b>{'கவனிக்க வேண்டியவை' if is_ta else 'Concerns'}</b>", s_tdb_sm), _p(_esc(fv["concerns_line"]), s_td_sm)],
        [_p(f"<b>{'தோஷ நிலை' if is_ta else 'Dosha Status'}</b>", s_tdb_sm), _p(_esc(fv["dosha_line"]), s_td_sm)],
        [_p(f"<b>{'கே.பி. ஆய்வு' if is_ta else 'KP Assessment'}</b>", s_tdb_sm), _p(_esc(fv["kp_line"]), s_td_sm)],
        [_p(f"<b>{'திருமண காலம்' if is_ta else 'Timing Assessment'}</b>", s_tdb_sm), _p(_esc(fv["timing_line"]), s_td_sm)],
        [_p(f"<b>{'இறுதிப் பரிந்துரை' if is_ta else 'Final Recommendation'}</b>", s_tdb_sm), _p(_esc(fv["recommendation_line"]), s_td_sm)],
    ]
    hier_tbl = Table(hier_rows, colWidths=[112, CONTENT_WIDTH - 112])
    hier_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, SLATE_BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, ZEBRA]),
        ("BACKGROUND", (0, 0), (0, -1), PARCHMENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(hier_tbl)
    story.append(Spacer(1, 3))
    story.append(_p(f"<b>{'பொறுப்புத் துறப்பு (Disclaimer)' if is_ta else 'Disclaimer'}:</b> {_esc(comp['disclaimer'])}", s_td_sm))
    story.append(Spacer(1, 4))

    w_card = Table(
        [[
            _p(
                "<b>மங்கள வாழ்த்துச் செய்தி / Auspicious Blessings</b><br/>"
                "<b>சீக்கிரம் திருமணம் நடைபெற இறைவனை நாங்கள் எங்கள் Gokul's Astrological Insights சார்பாக மனதார வேண்டிக்கொள்கிறோம்... வாழ்த்துகள்!</b><br/>"
                "<i>We sincerely pray to the Almighty on behalf of Gokul's Astrological Insights for an auspicious, harmonious, and blessed marriage at the earliest.</i>",
                s_ctr,
            )
        ]],
        colWidths=[CONTENT_WIDTH],
    )
    w_card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PARCHMENT), ("BOX", (0, 0), (-1, -1), 1.4, GOLD), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    story.append(w_card)

    doc.build(story, canvasmaker=MarriageDossierCanvas)
    return buf.getvalue()
