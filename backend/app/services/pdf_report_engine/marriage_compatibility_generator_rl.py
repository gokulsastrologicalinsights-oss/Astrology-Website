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
from app.services.pdf_report_engine.fonts import register_report_fonts, reorder_tamil_for_pdf
from app.services.pdf_report_engine.marriage_dossier_viewmodel import build_marriage_dossier_view_model
from app.services.pdf_report_engine.marriage_print_viewmodel import DASA_COLORS

logger = logging.getLogger("gai.pdf.marriage_generator_rl")

NAVY = colors.HexColor("#153F6B")
GOLD = colors.HexColor("#B4872B")
GOLD_LIGHT = colors.HexColor("#D8BD80")
PARCHMENT = colors.HexColor("#FAF2DE")
SLATE_BORDER = colors.HexColor("#CBD5E1")
ZEBRA = colors.HexColor("#F8FAFC")

MARGIN_PT = 32.0
CONTENT_WIDTH = A4[0] - (2 * MARGIN_PT)


def _esc(val: Any) -> str:
    return html.escape(str(val if val is not None else ""))


def _p(text: Any, style: ParagraphStyle) -> _RLParagraph:
    return _RLParagraph(reorder_tamil_for_pdf(str(text if text is not None else "")), style)


class MarriageDossierCanvas(canvas.Canvas):
    """Draws studio Navy & Gold double border, contact footer, and `Page X of N`."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_chrome(total)
            super().showPage()
        super().save()

    def _draw_chrome(self, page_count: int) -> None:
        w, h = A4
        self.saveState()
        self.setStrokeColor(NAVY)
        self.setLineWidth(1.3)
        self.rect(14, 14, w - 28, h - 28)

        self.setStrokeColor(GOLD_LIGHT)
        self.setLineWidth(0.6)
        self.rect(18, 18, w - 36, h - 36)

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(MARGIN_PT, 27, w - MARGIN_PT, 27)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(
            MARGIN_PT,
            20,
            reorder_tamil_for_pdf(
                "© Gokul's Astrological Insights • 165, Sakreeshwari Nagar, 2nd St, Thiruverkadu, Chennai - 600077 • Ph: 9444 55 9071"
            ),
        )
        self.drawRightString(w - MARGIN_PT, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


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


def _make_dasa_timeline_drawing(tl: Dict[str, Any], font_reg: str, font_bold: str, draw_w: float = 528.0, draw_h: float = 540.0) -> Drawing:
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
        buf, pagesize=A4, leftMargin=MARGIN_PT, rightMargin=MARGIN_PT, topMargin=30.0, bottomMargin=34.0
    )

    s_brand = ParagraphStyle("RLB", fontName=font_bold, fontSize=16.5, leading=20, alignment=1, textColor=NAVY)
    s_addr = ParagraphStyle("RLA", fontName=font_reg, fontSize=8.0, leading=10.5, alignment=1, textColor=colors.HexColor("#475569"))
    s_doc_sub = ParagraphStyle("RLDS", fontName=font_bold, fontSize=9.8, leading=13, alignment=1, textColor=colors.HexColor("#8B6914"))
    s_sec = ParagraphStyle("RLS", fontName=font_bold, fontSize=10.5, leading=14, textColor=colors.white)
    s_sub = ParagraphStyle("RLSub", fontName=font_bold, fontSize=9.0, leading=12, textColor=NAVY, spaceAfter=3)
    s_th = ParagraphStyle("RLTh", fontName=font_bold, fontSize=7.8, leading=10, textColor=colors.white)
    s_th_c = ParagraphStyle("RLThC", fontName=font_bold, fontSize=7.8, leading=10, alignment=1, textColor=colors.white)
    s_td = ParagraphStyle("RLTd", fontName=font_reg, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#0F172A"))
    s_tdb = ParagraphStyle("RLTdB", fontName=font_bold, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#0F172A"))
    s_tdc = ParagraphStyle("RLTdC", fontName=font_bold, fontSize=7.8, leading=10.2, alignment=1, textColor=colors.HexColor("#0F172A"))
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

    def _styled_tbl(rows: List[List[Any]], widths: List[float], pad_v: float = 3.2) -> Table:
        t = Table(rows, colWidths=widths)
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

    # ==================== PAGE 1: COVER, PROFILES & COMPOSITE ASSESSMENT ====================
    logo_cell: Any = ""
    if base["logo_path"]:
        try:
            logo_cell = Image(base["logo_path"], width=46, height=46)
        except Exception:
            logo_cell = ""

    hdr_t = Table(
        [[
            logo_cell,
            [
                _p("<b>Gokul's Astrological Insights</b>", s_brand),
                _p("165, Sakreeshwari Nagar, 2nd St, Thiruverkadu, Chennai - 600077 • Phone: 9444 55 9071", s_addr),
                Spacer(1, 2),
                _p(
                    f"<b>{'திருமணப் பொருத்த முழு ஆய்வு அறிக்கை' if is_ta else 'COMPREHENSIVE MARRIAGE COMPATIBILITY DOSSIER'}</b>",
                    s_doc_sub,
                ),
            ],
            "",
        ]],
        colWidths=[52, CONTENT_WIDTH - 104, 52],
    )
    hdr_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(hdr_t)
    story.append(HRFlowable(width="100%", thickness=1.2, color=GOLD_LIGHT, spaceBefore=3, spaceAfter=8))

    def _profile_card(title: str, p: Dict[str, Any], top_col: Any) -> Table:
        rows = [
            [_p(f"<b>{_esc(title)}: {_esc(p['name'])}</b>", s_th), ""],
            [_p("DOB / Time", s_td), _p(f"<b>{_esc(p['dob_age'])} • {_esc(p['tob'])}</b>", s_tdb)],
            [_p("Coords / TZ", s_td), _p(_esc(f"{p['coords']} ({p['timezone']})"), s_td)],
            [_p("Ascendant", s_td), _p(f"<b>{_esc(p['lagna'])}</b>", s_tdb)],
            [_p("Moon / Star", s_td), _p(f"<b>{_esc(p['rasi'])} — {_esc(p['nakshatra_pada'])}</b>", s_tdb)],
            [_p("Navamsa Lagna", s_td), _p(f"<b>{_esc(p['d9_lagna'])}</b>", s_tdb)],
            [_p("Venus / Jup / Mars", s_td), _p(_esc(f"{p['venus']} / {p['jupiter']} / {p['mars']}"), s_td)],
        ]
        pt = Table(rows, colWidths=[85, (CONTENT_WIDTH - 10) / 2.0 - 85])
        pt.setStyle(TableStyle([
            ("SPAN", (0, 0), (1, 0)),
            ("BACKGROUND", (0, 0), (1, 0), top_col),
            ("BOX", (0, 0), (-1, -1), 0.7, SLATE_BORDER),
            ("LINEBELOW", (0, 1), (-1, -2), 0.4, colors.HexColor("#F1F5F9")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        return pt

    half_w = (CONTENT_WIDTH - 10) / 2.0
    p_grid = Table([[_profile_card("மணமகன்" if is_ta else "GROOM", ge, NAVY), "", _profile_card("மணமகள்" if is_ta else "BRIDE", be, GOLD)]], colWidths=[half_w, 10, half_w])
    p_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(p_grid)
    story.append(Spacer(1, 8))

    story.append(_sec_banner(f"1. {'ஒருங்கிணைந்த இறுதி மதிப்பீடு' if is_ta else 'Master Composite Assessment'} — {comp['outcome_label']}"))
    story.append(Spacer(1, 5))
    v_box = Table([[_p(f"<b>{_esc(comp['outcome_label'])}</b> ({_esc(comp['outcome'])})<br/>{_esc(comp['explanation'])}", s_body)]], colWidths=[CONTENT_WIDTH])
    v_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PARCHMENT), ("BOX", (0, 0), (-1, -1), 1.0, GOLD), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    story.append(v_box)
    story.append(Spacer(1, 6))

    if comp["categories"]:
        cat_rows: List[List[Any]] = [[_p("Layer", s_th), _p("Tradition", s_th), _p("Status", s_th_c), _p("Summary", s_th)]]
        for c in comp["categories"]:
            cat_rows.append([_p(f"<b>{_esc(c['name'])}</b>", s_tdb), _p(_esc(c["tradition"]), s_td), _p(f"<b>{_esc(c['status'])}</b>", s_tdc), _p(_esc(c["summary"]), s_td)])
        story.append(_styled_tbl(cat_rows, [120, 115, 76, CONTENT_WIDTH - 311], pad_v=2.5))
        story.append(Spacer(1, 5))

    supp_txt = "<br/>".join(f"• {_esc(x)}" for x in comp["supportive"][:5]) or "• -"
    chal_txt = "<br/>".join(f"• {_esc(x)}" for x in comp["challenging"][:5]) or "• None"
    sc_tbl = Table([
        [_p("<b>Key Supportive Factors</b>", s_th), _p("<b>Considerations & Mitigations</b>", s_th)],
        [_p(supp_txt, s_td), _p(chal_txt, s_td)],
    ], colWidths=[half_w + 5, half_w + 5])
    sc_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story.append(sc_tbl)

    # ==================== PAGE 2: CHARTS & PLANETARY POSITIONS ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"2. {'ஜாதகக் கட்டங்கள் (D1 & D9) மற்றும் கிரக நிலைகள்' if is_ta else 'Dual Kundli Charts (D1 Rasi & D9 Navamsa) & Planetary Degrees'}"))
    story.append(Spacer(1, 6))
    c_drawings = [_make_chart_drawing(ch, font_reg, font_bold, width=190.0) for ch in base["charts"]]
    ct_tbl = Table([[c_drawings[0], c_drawings[1]], [c_drawings[2], c_drawings[3]]], colWidths=[CONTENT_WIDTH / 2.0, CONTENT_WIDTH / 2.0])
    ct_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(ct_tbl)
    story.append(Spacer(1, 4))

    def _p_tbl(p_rows: List[Dict[str, str]], title: str) -> Table:
        rows: List[List[Any]] = [[_p(f"<b>{_esc(title)}</b>", s_th), "", "", ""], [_p("Planet", s_th), _p("Rasi", s_th), _p("Deg", s_th), _p("D9", s_th)]]
        for r in (p_rows[:10] if p_rows else []):
            mot = f" ({r['retro']})" if r["retro"] != "-" else ""
            rows.append([_p(f"<b>{_esc(r['planet'])}{_esc(mot)}</b>", s_tdb), _p(_esc(r["sign"]), s_td), _p(_esc(r["degree"]), s_td), _p(_esc(r["d9_sign"]), s_td)])
        if len(rows) == 2:
            rows.append([_p("-", s_td), _p("-", s_td), _p("-", s_td), _p("-", s_td)])
        t = Table(rows, colWidths=[68, 72, 48, half_w - 188])
        t.setStyle(TableStyle([("SPAN", (0, 0), (3, 0)), ("BACKGROUND", (0, 0), (-1, 1), NAVY), ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER), ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, ZEBRA]), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
        return t

    pt_side = Table([[_p_tbl(vm["groom_planets"], f"Groom Planets ({ge['name']})"), "", _p_tbl(vm["bride_planets"], f"Bride Planets ({be['name']})")]], colWidths=[half_w, 10, half_w])
    pt_side.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(pt_side)

    # ==================== PAGE 3: TAMIL 10 PORUTHAMS ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"3. {'தமிழ் 10 பொருத்தங்கள்' if is_ta else 'Tamil 10 Poruthams Analysis'} ({pf['total_score']} / {pf['max_score']} • Rajju: {pf['rajju_status']} • Vedha: {pf['vedha_status']})"))
    story.append(Spacer(1, 6))
    por_rows: List[List[Any]] = [[_p("Porutham", s_th), _p("Score", s_th_c), _p("Grade", s_th_c), _p("Pair", s_th), _p("Evaluation & Meaning", s_th)]]
    for r in pf["rows"]:
        por_rows.append([_p(f"<b>{_esc(r['name'])}</b>", s_tdb), _p(f"<b>{_esc(r['score'])}</b>", s_tdc), _p(_esc(r["grade"]), s_tdc), _p(_esc(r["pair"]), s_td), _p(_esc(r["desc"]), s_td)])
    story.append(_styled_tbl(por_rows, [104, 46, 56, 86, CONTENT_WIDTH - 292], pad_v=3.0))
    story.append(Spacer(1, 6))
    chk_rows: List[List[Any]] = [[_p("11-Point Checklist", s_th), _p("Groom", s_th), _p("Bride", s_th), _p("Status", s_th_c)]]
    for mr in pf["checklist_11"]:
        chk_rows.append([_p(f"<b>{_esc(mr['label'])}</b>", s_tdb), _p(_esc(mr["groom_val"]), s_td), _p(_esc(mr["bride_val"]), s_td), _make_tick_drawing(bool(mr["pass"]))])
    story.append(_styled_tbl(chk_rows, [130, 150, 150, CONTENT_WIDTH - 430], pad_v=2.0))

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
    story.append(_make_dasa_timeline_drawing(base["timeline"], font_reg, font_bold, draw_w=CONTENT_WIDTH, draw_h=540.0))
    story.append(Spacer(1, 6))
    ds = base["dasa_sandhi"]
    story.append(_p(f"<b>Dasa Sandhi ({'இருக்கிறது' if ds.get('has_sandhi') else 'இல்லை'}):</b> {_esc(ds.get('summary_ta'))}", s_body))

    # ==================== PAGE 8: SIVADASAN RAVI REMEDIES, VERDICT & BLESSING ====================
    story.append(PageBreak())
    story.append(_sec_banner(f"9. {'சிவதாசன் ரவி ஆய்வு, பரிகார ஸ்தலம், முனிவரின் வாக்கு & வாழ்த்து' if is_ta else 'Sivadasan Ravi Synthesis, Parikara Remedies, Verdict & Blessings'}"))
    story.append(Spacer(1, 6))
    story.append(_p(f"<b>Gochara Guru Balam:</b> {_esc(sr['guru_balam']['label'])} ({_esc(sr['guru_balam']['transit_sign'])}) — {_esc(sr['guru_balam']['desc'])}", s_body))
    if sr["nadi_porutham"]["summary"]:
        story.append(_p(f"<b>Nadi Porutham:</b> {_esc(sr['nadi_porutham']['verdict'])} — {_esc(sr['nadi_porutham']['summary'])}", s_body))
    story.append(Spacer(1, 5))
    story.append(_p(f"<b>Parikara Sthalam:</b> {_esc(sr['temple_name'])} — {_esc(sr['temple_sig'])}", s_body))
    for h_item in sr["hymns"][:2]:
        story.append(Spacer(1, 3))
        story.append(_p(f"<b>{_esc(h_item['title'])}</b> ({_esc(h_item['purpose'])})<br/>{_esc(h_item['verse']).replace(chr(10), '<br/>')}", s_body))
    story.append(Spacer(1, 6))
    story.append(_p(f"<b>முனிவரின் வாக்கு (Sage Verdict):</b> {_esc(base['sage_verdict_ta'])}", s_body))
    story.append(Spacer(1, 4))
    story.append(_p(f"<b>Disclaimer:</b> {_esc(comp['disclaimer'])}", s_td))
    story.append(Spacer(1, 8))

    w_card = Table(
        [[
            _p(
                "<b>மங்கள வாழ்த்துச் செய்தி / Auspicious Blessings</b><br/><br/>"
                "<b>சீக்கிரம் திருமணம் நடைபெற இறைவனை நாங்கள் எங்கள் Gokul's Astrological Insights சார்பாக மனதார வேண்டிக்கொள்கிறோம்... வாழ்த்துக்கள்!</b><br/><br/>"
                "<i>\"sikiram kalyanam nadakanum nu aandavana nanga enga Gokul's Astrological Insights side la irundhu vendikurom..vaazhthukkal\"</i>",
                s_ctr,
            )
        ]],
        colWidths=[CONTENT_WIDTH],
    )
    w_card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PARCHMENT), ("BOX", (0, 0), (-1, -1), 1.4, GOLD), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
    story.append(w_card)

    doc.build(story, canvasmaker=MarriageDossierCanvas)
    return buf.getvalue()
