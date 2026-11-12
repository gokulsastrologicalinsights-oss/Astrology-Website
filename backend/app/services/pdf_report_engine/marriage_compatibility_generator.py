"""Comprehensive Royal Navy & Temple Gold Marriage Compatibility PDF Generator.

Compiles a detailed multi-page bilingual (English / Tamil) compatibility dossier covering
every analytical layer shown in the web studio:
1. Cover, Partner Particulars & Master Composite Assessment (8 Category Verdicts)
2. Dual Kundli Charts (D1 Rasi & D9 Navamsa) & Exact Planetary Degrees
3. South Indian Tamil 10 Poruthams + 11-Point Compatibility Checklist
4. North Indian 36-Point Ashtakoota Breakdown & Cancellations
5. Tri-Reference Kuja Samadosham & South Indian Papasamya Frame/Planet Audit
6. 10-Point Individual Dosha Audit Matrix
7. Individual Vedic Marriage Houses (2, 4, 5, 7, 8, 12), Karakas & Navamsa D9 Cross-Check
8. Bidirectional Synastry, Cross-Chart Planetary Pairs & Divergences
9. KP 7th Cuspal Sub-Lord, 4-Tier Significators & Ruling Planets
10. Proportional Dasa-Bhukti Sequence Timeline & Dasa Sandhi Analysis
11. Sivadasan Ravi Treatise Synthesis, Gochara Guru Balam, Nandi Yogam, In-Laws Exemptions,
    Full Sacred Thirumurai Remedies, Sage's Verdict & Studio Blessing.

Uses Playwright Chromium for native OpenType Tamil glyph shaping with bundled Noto Sans Tamil
fonts and falls back to the matching ReportLab dossier builder when Chromium is unavailable.
"""

from __future__ import annotations

import html
import logging
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from app.services.pdf_report_engine.marriage_dossier_viewmodel import build_marriage_dossier_view_model
from app.services.pdf_report_engine.marriage_print_viewmodel import (
    DASA_COLORS,
    NOTO_BOLD_PATH,
    NOTO_REGULAR_PATH,
)

logger = logging.getLogger("gai.pdf.marriage_generator")


def _esc(val: Any) -> str:
    return html.escape(str(val if val is not None else ""))


def _status_badge(status: str) -> str:
    s = str(status or "").upper()
    if any(k in s for k in ("FAVOR", "PASS", "EXCELLENT", "POSITIVE", "STRONG", "BALANCED")):
        return "badge-ok"
    if any(k in s for k in ("UNFAVOR", "FAIL", "NEGATIVE", "AFFLICT", "WEAK")):
        return "badge-bad"
    if any(k in s for k in ("MIXED", "MODERATE", "TOLERABLE", "PARTIAL")):
        return "badge-warn"
    return "badge-neutral"


def _render_chart_html(chart: Dict[str, Any]) -> str:
    cells: Dict[int, List[str]] = chart["cells"]

    def _cell(sign_idx: int) -> str:
        items = "".join(f"<span>{_esc(txt)}</span>" for txt in cells.get(sign_idx, []))
        return f'<td class="si-cell"><div class="si-items">{items}</div></td>'

    return f"""
    <div class="chart-card">
      <div class="chart-card-hdr">{_esc(chart["title"])}</div>
      <table class="si-table">
        <tr>{_cell(12)}{_cell(1)}{_cell(2)}{_cell(3)}</tr>
        <tr>
          {_cell(11)}
          <td colspan="2" rowspan="2" class="si-center">{_esc(chart["center"])}</td>
          {_cell(4)}
        </tr>
        <tr>{_cell(10)}{_cell(5)}</tr>
        <tr>{_cell(9)}{_cell(8)}{_cell(7)}{_cell(6)}</tr>
      </table>
    </div>
    """


def _render_dosha_cell_html(cell: Dict[str, Any] | None) -> str:
    if not cell or cell.get("status") == "NONE":
        return '<span class="txt-muted">இல்லை</span>'
    is_mit = cell.get("status") == "MITIGATED"
    cls = "txt-ok" if is_mit else "txt-bad"
    hdr = (
        "தோஷ நிவர்த்தி"
        if is_mit
        else f"தோஷம் உள்ளது (Effective Dosha Severity: {cell.get('severity_percent', 40)}%)"
    )
    reasons = cell.get("reasons_ta") or []
    r_html = ""
    if reasons:
        lines = "".join(f'<div class="dosha-line">{_esc(r)}</div>' for r in reasons)
        r_html = f'<div class="dosha-subhdr">காரணங்கள்:</div>{lines}'
    return f'<div class="{cls}"><div class="dosha-hdr">{_esc(hdr)}</div>{r_html}</div>'


def _render_dasa_svg(tl: Dict[str, Any]) -> str:
    y_for_year = tl["y_for_year"]
    now_y = tl["now_y"]
    current_yr = tl["current_year_num"]
    max_yr = tl["max_visible_year"]
    svg_w = tl["svg_width"]
    svg_h = tl["svg_height"]
    top_pad = tl["top_pad"]
    bot_pad = tl["bot_pad"]
    g_mds = tl["g_visible_mds"]
    b_mds = tl["b_visible_mds"]

    parts: List[str] = [
        f'<svg viewBox="0 0 {int(svg_w)} {int(svg_h)}" class="dasa-svg" role="img" aria-label="Dasa Bhukti Sequence">',
        """<defs>
          <marker id="arrowRedEnd" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#DC2626" />
          </marker>
          <marker id="arrowRedStart" markerWidth="6" markerHeight="6" refX="1" refY="3" orient="auto">
            <path d="M6,0 L0,3 L6,6 Z" fill="#DC2626" />
          </marker>
        </defs>""",
    ]

    def _draw_rects(mds: List[Dict[str, Any]], x_bar: float, x_yr: float, anchor: str) -> None:
        for idx, md in enumerate(mds):
            y_top = y_for_year(md["start_year"])
            y_bot = y_for_year(md["end_year"])
            h = max(2.0, y_bot - y_top)
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_active = float(md["start_year"]) < current_yr < float(md["end_year"])
            if is_active:
                parts.append(f'<rect x="{x_bar}" y="{y_top:.2f}" width="145" height="{max(1.0, now_y - y_top):.2f}" fill="{col["light_bg"]}" stroke="#FFFFFF" stroke-width="1" />')
                parts.append(f'<rect x="{x_bar}" y="{now_y:.2f}" width="145" height="{max(1.0, y_bot - now_y):.2f}" fill="{col["bg"]}" stroke="#FFFFFF" stroke-width="1" />')
            else:
                parts.append(f'<rect x="{x_bar}" y="{y_top:.2f}" width="145" height="{h:.2f}" fill="{col["bg"]}" stroke="#FFFFFF" stroke-width="1" />')
            parts.append(f'<text x="{x_yr}" y="{y_top + 4:.2f}" text-anchor="{anchor}" font-size="10" fill="#475569">{_esc(md.get("start_cal_year"))}</text>')
            if idx == len(mds) - 1:
                parts.append(f'<text x="{x_yr}" y="{y_bot + 3:.2f}" text-anchor="{anchor}" font-size="10" fill="#475569">{_esc(md.get("end_cal_year"))}</text>')

    _draw_rects(g_mds, 70, 62, "end")
    _draw_rects(b_mds, 465, 618, "start")

    if top_pad <= now_y <= svg_h - bot_pad:
        now_x = 30 if tl["now_collides_with_g_start"] else 60
        now_anchor = "start" if tl["now_collides_with_g_start"] else "end"
        parts.append(f'<line x1="32" y1="{now_y:.2f}" x2="215" y2="{now_y:.2f}" stroke="#DC2626" stroke-width="1.5" />')
        parts.append(f'<text x="{now_x}" y="{now_y - 4:.2f}" text-anchor="{now_anchor}" font-size="10" font-weight="700" fill="#DC2626">Now</text>')

    def _draw_labels(mds: List[Dict[str, Any]], x_center: float, avoid_now: bool) -> None:
        for md in mds:
            if float(md["start_year"]) >= max_yr:
                continue
            y_top = y_for_year(md["start_year"])
            y_bot = y_for_year(md["end_year"])
            h = max(2.0, y_bot - y_top)
            if h < 18.0:
                continue
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_active = float(md["start_year"]) < current_yr < float(md["end_year"])
            text_y = y_top + h / 2.0 + 4.0
            if avoid_now and is_active and abs(now_y - (y_top + h / 2.0)) < 11.0:
                uh, lh = now_y - y_top, y_bot - now_y
                text_y = now_y + max(13.0, lh / 2.0 + 3.0) if lh >= uh else now_y - max(6.0, uh / 2.0 - 3.0)
            text_y = min(y_bot - 5.0, max(y_top + 13.0, text_y))
            l_bg = col["light_bg"] if (is_active and text_y < now_y) else col["bg"]
            parts.append(
                f'<text x="{x_center}" y="{text_y:.2f}" text-anchor="middle" font-size="12" font-weight="700" '
                f'fill="{col["text"]}" stroke="{l_bg}" stroke-width="3" paint-order="stroke">{_esc(md.get("lord_ta"))}</text>'
            )

    _draw_labels(g_mds, 142.5, True)
    _draw_labels(b_mds, 537.5, False)

    for tr in tl["rendered_transitions"]:
        y_t = tr["y"]
        parts.append(
            f'<line x1="221" y1="{y_t:.2f}" x2="459" y2="{y_t:.2f}" stroke="#DC2626" stroke-width="1.1" '
            f'marker-start="url(#arrowRedStart)" marker-end="url(#arrowRedEnd)" />'
        )
        parts.append(f'<text x="340" y="{y_t - 3:.2f}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#7F1D1D">{_esc(tr["label_ta"])}</text>')

    parts.append("</svg>")
    return "".join(parts)


def _render_planet_table(rows: List[Dict[str, str]], title: str, is_ta: bool) -> str:
    body = (
        "".join(
            f"<tr><td><b>{_esc(r['planet'])}</b></td><td>{_esc(r['sign'])}</td><td>{_esc(r['degree'])}</td><td>{_esc(r['retro'])}</td><td>{_esc(r['d9_sign'])}</td></tr>"
            for r in rows
        )
        if rows
        else f"<tr><td colspan='5' class='txt-muted'>{_esc('கிரக தரவு இல்லை' if is_ta else 'No planetary longitudes provided')}</td></tr>"
    )
    return f"""
    <div class="subtable-wrap">
      <div class="subtable-hdr">{_esc(title)}</div>
      <table class="data-tbl compact">
        <thead><tr>
          <th>{'கிரகம்' if is_ta else 'Planet'}</th>
          <th>{'ராசி' if is_ta else 'Rasi'}</th>
          <th>{'பாகை' if is_ta else 'Degree'}</th>
          <th>{'நிலை' if is_ta else 'Motion'}</th>
          <th>{'நவாம்சம் (D9)' if is_ta else 'D9 Sign'}</th>
        </tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    """


def _render_vedic_partner_block(v: Dict[str, Any], name: str, is_ta: bool) -> str:
    h_rows = (
        "".join(
            f"""<tr>
              <td><b>H{_esc(h['house_num'])}</b></td>
              <td>{_esc(h['sign'])}</td>
              <td>{_esc(h['lord'])}</td>
              <td>{_esc(h['occupants'])}</td>
              <td>{_esc(h['aspects'])}</td>
              <td class="center"><span class="pill {_status_badge(h['status'])}">{_esc(h['status'])}</span></td>
            </tr>"""
            for h in v["houses"]
        )
        if v["houses"]
        else f"<tr><td colspan='6' class='txt-muted'>{_esc(v['summary'] or ('தனிநபர் வேத பாவ தரவு இல்லை' if is_ta else 'Individual house details unavailable'))}</td></tr>"
    )
    s_rows = (
        "".join(
            f"<tr><td><b>{_esc(s['planet'])}</b></td><td>{_esc(s['rasi'])}</td><td>{_esc(s['dignity'])}</td><td>{_esc(s['d9_sign'])}</td><td>{_esc(s['flags'])}</td></tr>"
            for s in v["significators"]
        )
        if v["significators"]
        else f"<tr><td colspan='5' class='txt-muted'>{_esc('காரக தரவு இல்லை' if is_ta else 'Significator data unavailable')}</td></tr>"
    )
    d9 = v["d9"]
    d9_line = (
        f"D9 Lagna: <b>{_esc(d9['d9_lagna'])}</b> (Lord: {_esc(d9['d9_lagna_lord'])}) • "
        f"D9 7th: <b>{_esc(d9['d9_7th'])}</b> (Lord: {_esc(d9['d9_7th_lord'])}) • "
        f"D1 7th Lord in D9: {_esc(d9['d1_7th_in_d9'])} • Venus in D9: {_esc(d9['venus_in_d9'])} • "
        f"Vargottama: {_esc(d9['vargottama'])} • Pushkara: {_esc(d9['pushkara'])}"
        if d9["available"]
        else (_esc("நவாம்ச ஒப்பீட்டுத் தரவு இல்லை") if is_ta else "Navamsa cross-check unavailable")
    )
    warn_html = (
        f'<div class="warn-strip">{"நேர எச்சரிக்கை: பிறப்பு நேர சிறு மாற்றம் நவாம்சத்தை மாற்றக்கூடும்" if is_ta else "Navamsa Boundary Sensitivity"} ({_esc(d9.get("arcmin"))} arcmin).</div>'
        if d9.get("boundary_risk")
        else ""
    )

    return f"""
    <div class="partner-vedic-card avoid-break">
      <div class="pv-hdr">{_esc(name)} — {'லக்னாதிபதி:' if is_ta else 'Lagna Lord:'} {_esc(v['lagna_lord'])}</div>
      <table class="data-tbl compact" style="margin-bottom:6px;">
        <thead><tr>
          <th style="width:7%;">H</th>
          <th style="width:15%;">{'ராசி' if is_ta else 'Sign'}</th>
          <th style="width:28%;">{'அதிபதி' if is_ta else 'Lord Placement'}</th>
          <th style="width:19%;">{'அமர்ந்தவை' if is_ta else 'Occupants'}</th>
          <th style="width:19%;">{'பார்வை' if is_ta else 'Aspects'}</th>
          <th style="width:12%;" class="center">{'நிலை' if is_ta else 'Status'}</th>
        </tr></thead>
        <tbody>{h_rows}</tbody>
      </table>
      <table class="data-tbl compact" style="margin-bottom:5px;">
        <thead><tr>
          <th>{'காரகர்' if is_ta else 'Karaka'}</th>
          <th>{'ராசி (பாவம்)' if is_ta else 'Rasi (House)'}</th>
          <th>{'நிலை' if is_ta else 'Dignity'}</th>
          <th>{'நவாம்சம்' if is_ta else 'D9 Sign'}</th>
          <th>{'சிறப்பு' if is_ta else 'Dignity Flags'}</th>
        </tr></thead>
        <tbody>{s_rows}</tbody>
      </table>
      <div class="d9-strip">{d9_line}</div>
      {warn_html}
    </div>
    """


def _render_kp_partner_block(k: Dict[str, Any], role_title: str, is_ta: bool) -> str:
    tiers = (
        "".join(
            f"<tr><td><b>{_esc(t['house'])}</b></td><td>{_esc(t['a'])}</td><td>{_esc(t['b'])}</td><td>{_esc(t['c'])}</td><td>{_esc(t['d'])}</td></tr>"
            for t in k["house_tiers"]
        )
        if k["house_tiers"]
        else f"<tr><td colspan='5' class='txt-muted'>{_esc('4-நிலை காரகர்கள் வழங்கப்படவில்லை' if is_ta else '4-Tier significators unavailable')}</td></tr>"
    )
    return f"""
    <div class="kp-card avoid-break">
      <div class="kp-card-hdr">
        <span>{_esc(role_title)}</span>
        <span class="pill {_status_badge(k['verdict'])}">{_esc(k['verdict'])}</span>
      </div>
      <div class="kp-meta-grid">
        <div><span>{'ராசி அதிபதி' if is_ta else 'Sign Lord'}:</span> <b>{_esc(k['sign_lord'])}</b></div>
        <div><span>{'நட்சத்திர அதிபதி' if is_ta else 'Star Lord'}:</span> <b>{_esc(k['star_lord'])}</b></div>
        <div><span>{'உப அதிபதி (CSL)' if is_ta else 'Sub-Lord (CSL)'}:</span> <b>{_esc(k['sub_lord'])}</b></div>
        <div><span>{'உப-உப அதிபதி' if is_ta else 'Sub-Sub Lord'}:</span> <b>{_esc(k['sub_sub_lord'])}</b></div>
      </div>
      <div class="kp-houses">
        {'குறிக்கும் பாவங்கள்' if is_ta else 'Signified Houses'}: <b>[{_esc(k['signified'])}]</b> |
        {'சாதகம்' if is_ta else 'Supporting'}: <b class="txt-ok">[{_esc(k['supporting'])}]</b> |
        {'தடை' if is_ta else 'Denying'}: <b class="txt-bad">[{_esc(k['denying'])}]</b>
      </div>
      <p class="kp-expl">{_esc(k['explanation'])}</p>
      <table class="data-tbl compact" style="margin-top:6px;">
        <thead><tr>
          <th>{'பாவம்' if is_ta else 'House'}</th>
          <th>Level A</th><th>Level B</th><th>Level C</th><th>Level D</th>
        </tr></thead>
        <tbody>{tiers}</tbody>
      </table>
    </div>
    """


def _render_kuja_detail(k: Dict[str, Any], title: str, is_ta: bool) -> str:
    trig = ", ".join(str(x) for x in k["triggers"]) if k["triggers"] else ("இல்லை" if is_ta else "None")
    canc = ", ".join(str(x) for x in k["cancellations"]) if k["cancellations"] else ("-" if is_ta else "None")
    return f"""
    <div class="dosha-box avoid-break">
      <div class="dosha-box-hdr">
        <b>{_esc(title)}</b>
        <span class="pill {_status_badge('PASS' if not k['is_present'] or k['is_cancelled'] else 'FAIL')}">{_esc(k['severity'])} ({_esc(k['intensity'])}%)</span>
      </div>
      <div class="kv-mini">
        <span>{'செவ்வாய்' if is_ta else 'Mars'}: <b>{_esc(k['mars_sign'])} ({_esc(k['mars_deg'])})</b></span> •
        <span>{'லக்னத்திலிருந்து' if is_ta else 'From Lagna'}: <b>H{_esc(k['h_lagna'])}</b></span> •
        <span>{'சந்திரனிலிருந்து' if is_ta else 'From Moon'}: <b>H{_esc(k['h_moon'])}</b></span> •
        <span>{'சுக்கிரனிலிருந்து' if is_ta else 'From Venus'}: <b>H{_esc(k['h_venus'])}</b></span>
      </div>
      <div class="dosha-detail-p"><b>{'தூண்டுதல்' if is_ta else 'Triggers'}:</b> {_esc(trig)}</div>
      <div class="dosha-detail-p"><b>{'விதிவிலக்கு' if is_ta else 'Cancellations Applied'}:</b> {_esc(canc)}</div>
      <div class="dosha-detail-p" style="margin-top:3px;">{_esc(k['explanation'])}</div>
    </div>
    """


def generate_html_report(data: Dict[str, Any], lang: str = "en") -> str:
    """Compiles the comprehensive Royal Navy & Gold Marriage Compatibility HTML Dossier."""
    vm = build_marriage_dossier_view_model(data, language=lang)
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

    font_faces: List[str] = []
    if NOTO_REGULAR_PATH.exists():
        font_faces.append(f"@font-face {{ font-family: 'Noto Sans Tamil'; font-weight: 400; src: url('{NOTO_REGULAR_PATH.as_uri()}') format('truetype'); }}")
    if NOTO_BOLD_PATH.exists():
        font_faces.append(f"@font-face {{ font-family: 'Noto Sans Tamil'; font-weight: 700; src: url('{NOTO_BOLD_PATH.as_uri()}') format('truetype'); }}")
    font_face_css = "\n".join(font_faces)

    logo_img = (
        f'<img src="{base["logo_data_uri"]}" alt="Logo" class="cover-logo" />'
        if base["logo_data_uri"]
        else ""
    )

    cat_cards_html = "".join(
        f"""
        <div class="cat-card">
          <div class="cat-name">{_esc(c['name'])}</div>
          <div class="cat-trad">{_esc(c['tradition'])}</div>
          <span class="pill {_status_badge(c['status'])}">{_esc(c['status'])}</span>
          <div class="cat-sum">{_esc(c['summary'])}</div>
        </div>
        """
        for c in comp["categories"]
    )
    supp_lis = "".join(f"<li>{_esc(x)}</li>" for x in comp["supportive"]) or f"<li class='txt-muted'>{'குறிப்பிடத்தக்கவை சேர்க்கப்பட்டுள்ளன' if is_ta else 'See detailed breakdown below'}</li>"
    chal_lis = "".join(f"<li>{_esc(x)}</li>" for x in comp["challenging"]) or f"<li class='txt-muted'>{'கடுமையான தோஷங்கள் இல்லை' if is_ta else 'No major afflictions flagged'}</li>"
    miss_html = (
        f'<div class="advisory-box warn-box avoid-break"><b>{"கவனிக்கத்தக்க நிச்சயமற்ற காரணிகள்" if is_ta else "Missing / Sensitivity Advisory"}:</b><ul>'
        + "".join(f"<li>{_esc(m)}</li>" for m in comp["missing"])
        + "</ul></div>"
        if comp["missing"]
        else ""
    )
    rev_html = (
        f'<div class="advisory-box info-box avoid-break"><b>{"ஜோதிடர் நேரடி ஆலோசனைப் பரிந்துரைகள்" if is_ta else "Recommended Consultation Focus"}:</b><ul>'
        + "".join(f"<li>{_esc(r)}</li>" for r in comp["review"])
        + "</ul></div>"
        if comp["review"]
        else ""
    )

    charts_html = "".join(_render_chart_html(ch) for ch in base["charts"])

    por_rows_html = "".join(
        f"""<tr>
          <td><b>{_esc(r['name'])}</b><div class="micro-ref">{_esc(r['ref'])}</div></td>
          <td class="center"><b>{_esc(r['score'])}</b></td>
          <td class="center"><span class="pill {_status_badge('PASS' if r['is_favorable'] else 'FAIL')}">{_esc(r['grade'])}</span></td>
          <td>{_esc(r['pair'])}</td>
          <td>{_esc(r['desc'])}</td>
        </tr>"""
        for r in pf["rows"]
    )
    chk_11_html = " ".join(
        f'<span class="chk-pill {"chk-ok" if r["pass"] else "chk-no"}">{_esc(r["label"])}: {"✓" if r["pass"] else "✗"}</span>'
        for r in pf["checklist_11"]
    )

    ash_rows_html = "".join(
        f"""<tr>
          <td><b>{_esc(r['name'])}</b><div class="micro-ref">{_esc(r['ref'])}</div></td>
          <td>{_esc(r['raw_calc'] or '-')}</td>
          <td class="center"><b>{_esc(r['earned'])} / {_esc(r['max'])}</b></td>
          <td class="center"><span class="pill {_status_badge('PASS' if r['is_cancelled'] or r['status']=='PASS' else r['status'])}">{_esc('CANCELLED' if r['is_cancelled'] else r['status'])}</span></td>
          <td>{_esc(r['desc'])}{f'<div class="txt-ok"><b>விலக்கு / Cancellation:</b> {_esc(r["cancel_reason"])}</div>' if r['cancel_reason'] else ''}</td>
        </tr>"""
        for r in af["rows"]
    )

    def _papa_badges(items: List[Dict[str, str]]) -> str:
        if not items:
            return "-"
        return " | ".join(f"{_esc(x['planet'])}: <b>{_esc(x['pts'])}</b>" for x in items)

    dosha_10_html = "".join(
        f"<tr><td><b>{_esc(row.get('label_ta'))}</b></td><td>{_render_dosha_cell_html(row.get('groom'))}</td><td>{_render_dosha_cell_html(row.get('bride'))}</td></tr>"
        for row in base["dosha_audit"]
    )

    harm_html = (
        "".join(f"<tr><td class='txt-ok'><b>{_esc(i.get('groom_planet_ta'))}</b></td><td class='txt-ok'><b>{_esc(i.get('bride_planet_ta'))}</b></td><td class='txt-ok'>{_esc(i.get('description_ta'))}</td></tr>" for i in base["harmonious_connections"])
        if base["harmonious_connections"]
        else f"<tr><td colspan='3' class='txt-muted'>{'குறைவான ஒரே ராசி சுப இணைவுகள்; நட்சத்திரப் பொருத்தம் முதன்மையானது.' if is_ta else 'No major same-sign benefic pairs detected.'}</td></tr>"
    )
    incomp_html = (
        "".join(f"<tr><td class='txt-bad'><b>{_esc(i.get('groom_planet_ta'))}</b></td><td class='txt-bad'><b>{_esc(i.get('bride_planet_ta'))}</b></td><td class='txt-bad'>{_esc(i.get('description_ta'))}</td></tr>" for i in base["incompatible_combinations"])
        if base["incompatible_combinations"]
        else f"<tr><td colspan='3' class='txt-ok'>{'பொருத்தமற்ற எதிர்மறை சேர்க்கைகள் இல்லை.' if is_ta else 'No adverse cross-chart planetary combinations detected.'}</td></tr>"
    )
    conf_html = (
        "".join(
            f"""<div class="conflict-card avoid-break">
              <div class="conflict-hdr"><b>{_esc(c['title'])}</b> <span class="pill badge-warn">{_esc(c['type'])}</span></div>
              <div class="conflict-cols">
                <div><span>Finding A:</span> {_esc(c['finding_a'])}</div>
                <div><span>Finding B:</span> {_esc(c['finding_b'])}</div>
              </div>
              <div class="conflict-res"><b>{'தீர்வு விதி' if is_ta else 'Resolution Principle'}:</b> {_esc(c['resolution'])}</div>
            </div>"""
            for c in comp["conflicts"]
        )
        if comp["conflicts"]
        else f'<div class="parchment-box txt-ok">{"எல்லா ஜோதிட முறைகளிலும் குறிப்பிடத்தக்க முரண்பாடுகள் இல்லை." if is_ta else "No cross-tradition divergences detected across evaluated layers."}</div>'
    )

    nandi_obs_html = "".join(f"<li>{_esc(x)}</li>" for x in sr["nadi_porutham"]["obstacles"])
    inlaws_html = (
        "".join(
            f'<div class="inlaw-item"><b>{_esc(f["star"])} ({_esc(f["relative"])}):</b> {"Exempt / தோஷமில்லை" if f["is_exempt"] else "Active / கவனம் தேவை"} — {_esc(f["expl"])}</div>'
            for f in sr["in_laws"]["findings"]
        )
        if sr["in_laws"]["has_special"] and sr["in_laws"]["findings"]
        else f'<div class="inlaw-item txt-ok">{"விசேஷ மாமனார்/மாமியார் நட்சத்திர தோஷம் ஏதும் இல்லை." if is_ta else "No special In-Laws Nakshatra afflictions triggered."}</div>'
    )
    hymns_html = "".join(
        f"""<div class="hymn-card avoid-break">
          <div class="hymn-hdr"><b>{_esc(h['title'])}</b> <span class="pill badge-gold">{_esc(h['purpose'])}</span></div>
          <pre class="hymn-verse">{_esc(h['verse'])}</pre>
        </div>"""
        for h in sr["hymns"]
    )
    ash_pct = min(100.0, max(0.0, (float(af["total"]) / float(af["max"] or 36.0)) * 100.0))

    return f"""<!DOCTYPE html>
<html lang="{'ta' if is_ta else 'en'}">
<head>
<meta charset="utf-8" />
<title>Marriage Compatibility Dossier</title>
<style>
  {font_face_css}
  @page {{
    size: A4 portrait;
    margin: 16mm 12mm 16mm 12mm;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  body {{
    margin: 0;
    padding: 0;
    font-family: 'Noto Sans Tamil', 'Nirmala UI', 'Segoe UI', system-ui, sans-serif;
    color: #0F172A;
    background: #FFFFFF;
    font-size: 9.8px;
    line-height: 1.42;
  }}
  /* Fixed Navy & Gold studio double-border frame drawn cleanly on every A4 page */
  .page-frame-outer {{
    position: fixed;
    top: 0mm; left: -3.5mm; right: -3.5mm; bottom: 0mm;
    border: 1.6px solid #153F6B;
    border-radius: 3px;
    pointer-events: none;
    z-index: 9999;
  }}
  .page-frame-inner {{
    position: fixed;
    top: 1.4mm; left: -2.1mm; right: -2.1mm; bottom: 1.4mm;
    border: 0.7px solid #D8BD80;
    border-radius: 2px;
    pointer-events: none;
    z-index: 9999;
  }}
  .content-root {{ width: 100%; padding: 4.5mm 1.5mm 4.5mm 1.5mm; }}
  .new-page {{ break-before: page; page-break-before: always; }}
  .avoid-break {{ break-inside: avoid; page-break-inside: avoid; }}

  /* Cover & Section Headings */
  .cover-hdr {{
    display: flex; align-items: center; gap: 14px;
    border-bottom: 2px solid #D8BD80; padding-bottom: 8px; margin-bottom: 10px;
  }}
  .cover-logo {{ width: 58px; height: 58px; object-fit: contain; flex-shrink: 0; }}
  .cover-titles {{ flex: 1; text-align: center; padding-right: 58px; }}
  .studio-name {{ margin: 0; font-size: 19px; font-weight: 800; color: #153F6B; letter-spacing: 0.3px; }}
  .studio-addr {{ margin: 2px 0 0 0; font-size: 9.2px; color: #475569; }}
  .dossier-badge {{
    display: inline-block; margin-top: 5px; padding: 3px 12px;
    background: #FAF2DE; border: 1px solid #B4872B; border-radius: 4px;
    color: #8B6914; font-weight: 700; font-size: 11px;
  }}
  .sec-title {{
    margin: 0 0 8px 0; padding: 5px 10px;
    background: linear-gradient(90deg, #153F6B 0%, #1E5692 100%);
    color: #FFFFFF; font-size: 12px; font-weight: 700;
    border-left: 4px solid #D8BD80; border-radius: 3px;
    display: flex; justify-content: space-between; align-items: center;
  }}
  .sec-sub {{ margin: 0 0 8px 0; font-size: 9.2px; color: #475569; }}

  /* Grid & Tables */
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px; }}
  .data-tbl {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; font-size: 9.2px; }}
  .data-tbl th, .data-tbl td {{ border: 1px solid #CBD5E1; padding: 4.5px 6px; text-align: left; vertical-align: middle; }}
  .data-tbl th {{ background: #153F6B; color: #FFFFFF; font-weight: 700; border-color: #153F6B; }}
  .data-tbl.compact th, .data-tbl.compact td {{ padding: 3px 5px; font-size: 8.6px; }}
  .data-tbl tr:nth-child(even) td {{ background: #F8FAFC; }}
  .center {{ text-align: center !important; }}
  .micro-ref {{ font-size: 7.5px; color: #64748B; font-weight: 400; margin-top: 1px; }}

  .partner-card {{ border: 1px solid #CBD5E1; border-top: 3px solid #153F6B; border-radius: 4px; padding: 8px; background: #FFFFFF; }}
  .partner-card.bride {{ border-top-color: #B4872B; }}
  .partner-hdr {{ font-size: 11.5px; font-weight: 700; color: #153F6B; margin-bottom: 5px; text-align: center; }}
  .partner-card.bride .partner-hdr {{ color: #8B6914; }}
  .kv-tbl {{ width: 100%; border-collapse: collapse; font-size: 8.8px; }}
  .kv-tbl td {{ padding: 2px 3px; border-bottom: 1px solid #F1F5F9; }}
  .kv-lbl {{ color: #64748B; width: 42%; }}
  .kv-val {{ color: #0F172A; font-weight: 700; }}

  .verdict-banner {{
    border: 1.5px solid #B4872B; background: #FAF2DE; border-radius: 5px;
    padding: 9px 12px; margin-bottom: 10px;
  }}
  .vb-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
  .vb-lbl {{ font-size: 13px; font-weight: 800; color: #153F6B; }}
  .vb-expl {{ font-size: 9.2px; color: #334155; margin: 0; }}

  .cat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 10px; }}
  .cat-card {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px 6px; background: #F8FAFC; text-align: center; }}
  .cat-name {{ font-weight: 700; font-size: 8.6px; color: #153F6B; margin-bottom: 1px; }}
  .cat-trad {{ font-size: 7.4px; color: #64748B; margin-bottom: 3px; }}
  .cat-sum {{ font-size: 7.5px; color: #334155; margin-top: 3px; line-height: 1.25; }}

  .pill {{ display: inline-block; padding: 1.5px 6px; border-radius: 3px; font-size: 7.8px; font-weight: 700; border: 1px solid transparent; }}
  .badge-ok {{ background: #ECFDF5; color: #047857; border-color: #A7F3D0; }}
  .badge-bad {{ background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }}
  .badge-warn {{ background: #FFFBEB; color: #B45309; border-color: #FDE68A; }}
  .badge-gold {{ background: #FAF2DE; color: #8B6914; border-color: #D8BD80; }}
  .badge-neutral {{ background: #F1F5F9; color: #334155; border-color: #CBD5E1; }}

  .ind-box {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 7px 9px; font-size: 8.8px; }}
  .ind-ok {{ background: #F0FDF4; border-color: #BBF7D0; }}
  .ind-warn {{ background: #FFFBEB; border-color: #FDE68A; }}
  .ind-box ul, .advisory-box ul {{ margin: 4px 0 0 14px; padding: 0; }}
  .ind-box li, .advisory-box li {{ margin-bottom: 2px; }}
  .advisory-box {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px 9px; margin-bottom: 7px; font-size: 8.6px; }}
  .warn-box {{ background: #FFFBEB; border-color: #FDE68A; color: #78350F; }}
  .info-box {{ background: #EFF6FF; border-color: #BFDBFE; color: #1E3A8A; }}

  /* Charts Page */
  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; margin-bottom: 10px; }}
  .chart-card {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px; background: #FFFFFF; text-align: center; }}
  .chart-card-hdr {{ font-weight: 700; font-size: 10px; color: #153F6B; margin-bottom: 4px; }}
  .si-table {{ width: 100%; max-width: 245px; margin: 0 auto; border-collapse: collapse; border: 1.8px solid #153F6B; table-layout: fixed; }}
  .si-cell {{ border: 1px solid #94A3B8; width: 25%; height: 48px; text-align: center; vertical-align: middle; padding: 2px; }}
  .si-items {{ display: flex; flex-direction: column; align-items: center; font-size: 8.8px; font-weight: 600; color: #0F172A; line-height: 1.2; }}
  .si-center {{ border: 1px solid #94A3B8; background: #FAF2DE; color: #8B6914; font-weight: 700; font-size: 10px; text-align: center; }}
  .subtable-wrap {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px; background: #FFFFFF; }}
  .subtable-hdr {{ font-weight: 700; font-size: 9.5px; color: #153F6B; margin-bottom: 4px; }}

  .score-bar-wrap {{ border: 1px solid #CBD5E1; background: #F8FAFC; border-radius: 4px; padding: 6px 10px; margin-bottom: 8px; }}
  .score-track {{ height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden; margin-top: 4px; }}
  .score-fill {{ height: 100%; background: linear-gradient(90deg, #153F6B, #B4872B); }}
  .chk-wrap {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; padding: 6px; background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 4px; }}
  .chk-pill {{ padding: 2px 6px; border-radius: 3px; font-size: 8.2px; font-weight: 700; }}
  .chk-ok {{ background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }}
  .chk-no {{ background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }}

  .dosha-box {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 7px 9px; background: #FFFFFF; font-size: 8.8px; }}
  .dosha-box-hdr {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px; margin-bottom: 4px; color: #153F6B; }}
  .kv-mini {{ font-size: 8.5px; color: #334155; margin-bottom: 3px; }}
  .dosha-detail-p {{ font-size: 8.5px; color: #1E293B; line-height: 1.35; }}
  .txt-ok {{ color: #047857; }}
  .txt-bad {{ color: #BE123C; }}
  .txt-muted {{ color: #64748B; }}
  .dosha-hdr {{ font-weight: 700; }}
  .dosha-subhdr {{ font-weight: 600; margin-top: 2px; }}
  .dosha-line {{ padding-left: 5px; font-size: 8.6px; }}

  .partner-vedic-card {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 7px; margin-bottom: 9px; background: #FFFFFF; }}
  .pv-hdr {{ font-weight: 700; font-size: 10px; color: #153F6B; margin-bottom: 5px; border-bottom: 1px solid #D8BD80; padding-bottom: 3px; }}
  .d9-strip {{ font-size: 8.5px; background: #FAF2DE; border: 1px solid #D8BD80; border-radius: 3px; padding: 4px 6px; color: #1E293B; }}
  .warn-strip {{ font-size: 8.3px; background: #FFFBEB; border: 1px solid #FDE68A; color: #B45309; padding: 3px 6px; margin-top: 3px; font-weight: 700; }}

  .syn-card {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 8px; background: #F8FAFC; font-size: 8.8px; }}
  .syn-hdr {{ font-weight: 700; color: #153F6B; font-size: 10px; margin-bottom: 4px; }}
  .conflict-card {{ border: 1px solid #FDE68A; background: #FFFBEB; border-radius: 4px; padding: 7px; margin-bottom: 6px; font-size: 8.6px; }}
  .conflict-hdr {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; color: #92400E; }}
  .conflict-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 4px; }}
  .conflict-cols div {{ background: #FFFFFF; padding: 4px 6px; border: 1px solid #FDE68A; border-radius: 3px; }}
  .conflict-cols span {{ font-weight: 700; color: #64748B; display: block; font-size: 7.8px; }}
  .conflict-res {{ color: #78350F; }}

  .kp-card {{ border: 1px solid #CBD5E1; border-radius: 4px; padding: 8px; margin-bottom: 9px; background: #FFFFFF; }}
  .kp-card-hdr {{ display: flex; justify-content: space-between; align-items: center; font-weight: 700; color: #153F6B; font-size: 10px; border-bottom: 1px solid #D8BD80; padding-bottom: 4px; margin-bottom: 5px; }}
  .kp-meta-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; font-size: 8.6px; margin-bottom: 4px; background: #F8FAFC; padding: 4px 6px; border-radius: 3px; }}
  .kp-meta-grid span {{ color: #64748B; }}
  .kp-houses {{ font-size: 8.8px; margin-bottom: 3px; }}
  .kp-expl {{ margin: 0; font-size: 8.5px; color: #334155; }}

  .dasa-cols-hdr {{ display: grid; grid-template-columns: 1fr 1fr; text-align: center; font-weight: 700; font-size: 11px; color: #153F6B; margin-bottom: 4px; }}
  .dasa-svg {{ width: 100%; height: auto; max-height: 195mm; display: block; margin: 0 auto; }}
  .sandhi-card {{ border-radius: 4px; padding: 7px 9px; margin-top: 8px; font-size: 8.8px; }}
  .sandhi-yes {{ background: #FFF1F2; border: 1px solid #FECDD3; color: #9F1239; }}
  .sandhi-no {{ background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; }}

  .parchment-box {{ border: 1px solid #D8BD80; background: #FAF2DE; border-radius: 4px; padding: 7px 10px; font-size: 8.8px; margin-bottom: 8px; }}
  .hymn-card {{ border: 1px solid #D8BD80; border-radius: 4px; padding: 6px 8px; margin-bottom: 6px; background: #FFFFFF; }}
  .hymn-hdr {{ display: flex; justify-content: space-between; align-items: center; font-size: 9px; color: #153F6B; margin-bottom: 3px; }}
  .hymn-verse {{ margin: 0; font-family: inherit; white-space: pre-wrap; font-size: 8.4px; line-height: 1.4; background: #FFFBEB; padding: 5px 7px; border-radius: 3px; color: #1E293B; }}
  .inlaw-item {{ font-size: 8.6px; margin-bottom: 3px; }}
  .blessing-box {{
    margin-top: 8px; padding: 10px; border: 1.5px solid #B4872B; background: #FAF2DE;
    border-radius: 5px; text-align: center; font-size: 9px; color: #153F6B;
  }}
</style>
</head>
<body>
  <div class="page-frame-outer"></div>
  <div class="page-frame-inner"></div>
  <div class="content-root">

    <!-- PAGE 1: COVER, PROFILES & MASTER COMPOSITE ASSESSMENT -->
    <section>
      <div class="cover-hdr">
        {logo_img}
        <div class="cover-titles">
          <h1 class="studio-name">Gokul&apos;s Astrological Insights</h1>
          <p class="studio-addr">165, Sakreeshwari Nagar, 2nd Street, Thiruverkadu, Chennai - 600077 • Ph: 9444 55 9071</p>
          <span class="dossier-badge">{'திருமணப் பொருத்த முழு ஆய்வு அறிக்கை' if is_ta else 'COMPREHENSIVE MARRIAGE COMPATIBILITY DOSSIER'}</span>
        </div>
      </div>

      <div class="grid-2">
        <div class="partner-card">
          <div class="partner-hdr">{'மணமகன் ஜாதக விவரங்கள்' if is_ta else 'GROOM PROFILE'}: {_esc(ge['name'])}</div>
          <table class="kv-tbl">
            <tr><td class="kv-lbl">{'பிறந்த தேதி & நேரம்' if is_ta else 'DOB / Time'}</td><td class="kv-val">{_esc(ge['dob_age'])} • {_esc(ge['tob'])}</td></tr>
            <tr><td class="kv-lbl">{'இடம் / நேர மண்டலம்' if is_ta else 'Coords / TZ'}</td><td class="kv-val">{_esc(ge['coords'])} ({_esc(ge['timezone'])})</td></tr>
            <tr><td class="kv-lbl">{'லக்கினம் (பாகை)' if is_ta else 'Ascendant (D1)'}</td><td class="kv-val">{_esc(ge['lagna'])}</td></tr>
            <tr><td class="kv-lbl">{'ராசி & நட்சத்திரம்' if is_ta else 'Moon Sign / Star'}</td><td class="kv-val">{_esc(ge['rasi'])} — {_esc(ge['nakshatra_pada'])}</td></tr>
            <tr><td class="kv-lbl">{'நவாம்ச லக்கினம்' if is_ta else 'Navamsa (D9) Lagna'}</td><td class="kv-val">{_esc(ge['d9_lagna'])}</td></tr>
            <tr><td class="kv-lbl">{'சுக்கிரன் / குரு / செவ்வாய்' if is_ta else 'Venus / Jup / Mars'}</td><td class="kv-val">{_esc(ge['venus'])} / {_esc(ge['jupiter'])} / {_esc(ge['mars'])}</td></tr>
          </table>
        </div>
        <div class="partner-card bride">
          <div class="partner-hdr">{'மணமகள் ஜாதக விவரங்கள்' if is_ta else 'BRIDE PROFILE'}: {_esc(be['name'])}</div>
          <table class="kv-tbl">
            <tr><td class="kv-lbl">{'பிறந்த தேதி & நேரம்' if is_ta else 'DOB / Time'}</td><td class="kv-val">{_esc(be['dob_age'])} • {_esc(be['tob'])}</td></tr>
            <tr><td class="kv-lbl">{'இடம் / நேர மண்டலம்' if is_ta else 'Coords / TZ'}</td><td class="kv-val">{_esc(be['coords'])} ({_esc(be['timezone'])})</td></tr>
            <tr><td class="kv-lbl">{'லக்கினம் (பாகை)' if is_ta else 'Ascendant (D1)'}</td><td class="kv-val">{_esc(be['lagna'])}</td></tr>
            <tr><td class="kv-lbl">{'ராசி & நட்சத்திரம்' if is_ta else 'Moon Sign / Star'}</td><td class="kv-val">{_esc(be['rasi'])} — {_esc(be['nakshatra_pada'])}</td></tr>
            <tr><td class="kv-lbl">{'நவாம்ச லக்கினம்' if is_ta else 'Navamsa (D9) Lagna'}</td><td class="kv-val">{_esc(be['d9_lagna'])}</td></tr>
            <tr><td class="kv-lbl">{'சுக்கிரன் / குரு / செவ்வாய்' if is_ta else 'Venus / Jup / Mars'}</td><td class="kv-val">{_esc(be['venus'])} / {_esc(be['jupiter'])} / {_esc(be['mars'])}</td></tr>
          </table>
        </div>
      </div>

      <h2 class="sec-title">
        <span>{'1. ஒருங்கிணைந்த இறுதி மதிப்பீடு (Master Composite Assessment)' if is_ta else '1. Master Composite Assessment'}</span>
        <span>{_esc(comp['outcome_label'])}</span>
      </h2>
      <div class="verdict-banner">
        <div class="vb-top">
          <span class="vb-lbl">{_esc(comp['outcome_label'])}</span>
          <span class="pill {_status_badge(comp['outcome'])}">{_esc(comp['outcome'])}</span>
        </div>
        <p class="vb-expl">{_esc(comp['explanation'])}</p>
      </div>

      <div class="cat-grid">{cat_cards_html}</div>

      <div class="grid-2">
        <div class="ind-box ind-ok">
          <b class="txt-ok">{'முதன்மை சாதகங்கள் (Key Supportive Factors)' if is_ta else 'Key Supportive Factors'}</b>
          <ul>{supp_lis}</ul>
        </div>
        <div class="ind-box ind-warn">
          <b style="color:#B45309;">{'கவனிக்கப்பட வேண்டியவை (Considerations & Mitigations)' if is_ta else 'Considerations & Mitigations'}</b>
          <ul>{chal_lis}</ul>
        </div>
      </div>
      {miss_html}
      {rev_html}
    </section>

    <!-- PAGE 2: DUAL KUNDLI CHARTS & PLANETARY LONGITUDES -->
    <section class="new-page">
      <h2 class="sec-title"><span>{'2. இருவர் ஜாதகக் கட்டங்கள் (D1 ராசி & D9 நவாம்சம்) மற்றும் கிரக நிலைகள்' if is_ta else '2. Dual Kundli Charts (D1 Rasi & D9 Navamsa) & Planetary Longitudes'}</span></h2>
      <div class="charts-grid">{charts_html}</div>
      <div class="grid-2">
        {_render_planet_table(vm['groom_planets'], ('மணமகன் கிரக நிலைகள்' if is_ta else f'Groom Planets: {ge["name"]}'), is_ta)}
        {_render_planet_table(vm['bride_planets'], ('மணமகள் கிரக நிலைகள்' if is_ta else f'Bride Planets: {be["name"]}'), is_ta)}
      </div>
    </section>

    <!-- PAGE 3: TAMIL 10 PORUTHAMS DETAILED + 11 CHECKLIST -->
    <section class="new-page">
      <h2 class="sec-title">
        <span>{'3. தமிழ் 10 பொருத்தங்கள் (விளக்கமான மதிப்பீடு)' if is_ta else '3. South Indian Tamil 10 Poruthams (Detailed Evaluation)'}</span>
        <span>{_esc(pf['total_score'])} / {_esc(pf['max_score'])} • {_esc(pf['verdict'])}</span>
      </h2>
      <div class="score-bar-wrap" style="display:flex; justify-content:space-between; align-items:center;">
        <div><b>{'மொத்த மதிப்பெண்:' if is_ta else 'Aggregate Verdict:'}</b> {_esc(pf['total_score'])} / {_esc(pf['max_score'])} ({_esc(pf['verdict'])})</div>
        <div>
          <span class="pill {_status_badge(pf['rajju_status'])}">Rajju: {_esc(pf['rajju_status'])}</span>
          <span class="pill {_status_badge(pf['vedha_status'])}">Vedha: {_esc(pf['vedha_status'])}</span>
        </div>
      </div>
      <table class="data-tbl compact">
        <thead><tr>
          <th style="width:20%;">{'பொருத்தம் & ஆதாரம்' if is_ta else 'Porutham & Ref'}</th>
          <th style="width:9%;" class="center">{'புள்ளி' if is_ta else 'Score'}</th>
          <th style="width:11%;" class="center">{'நிலை' if is_ta else 'Grade'}</th>
          <th style="width:17%;">{'மணமகன் / மணமகள்' if is_ta else 'Star Pair'}</th>
          <th style="width:43%;">{'விரிவான விளக்கம்' if is_ta else 'Evaluation & Meaning'}</th>
        </tr></thead>
        <tbody>{por_rows_html}</tbody>
      </table>
      <div class="chk-wrap">
        <b style="width:100%; font-size:8.6px; color:#153F6B;">{'11-பொருத்த சுருக்கப் பட்டியல் (தினம் முதல் வேதை & நாடி வரை):' if is_ta else '11-Porutham Quick Checklist (incl. Nadi):'}</b>
        {chk_11_html}
      </div>
    </section>

    <!-- PAGE 4: NORTH INDIAN 36-POINT ASHTAKOOTA -->
    <section class="new-page">
      <h2 class="sec-title">
        <span>{'4. வட இந்திய 36 அஷ்டகூட ஆய்வு (Ashtakoota Analysis)' if is_ta else '4. North Indian 36-Point Ashtakoota Analysis'}</span>
        <span>{_esc(af['total'])} / {_esc(af['max'])}</span>
      </h2>
      <div class="score-bar-wrap">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div><b>{'அஷ்டகூட மதிப்பெண்:' if is_ta else 'Total Earned Points:'}</b> {_esc(af['total'])} / {_esc(af['max'])} (Min: {_esc(af['threshold'])})</div>
          <div>
            <span class="pill {'badge-ok' if af['is_met'] else 'badge-bad'}">{'THRESHOLD MET' if af['is_met'] else 'BELOW MIN'}</span>
            <span class="pill {'badge-ok' if not af['nadi_present'] or af['nadi_cancelled'] else 'badge-bad'}">Nadi: {'Cancelled' if af['nadi_cancelled'] else ('Dosha' if af['nadi_present'] else 'Clear')}</span>
            <span class="pill {'badge-ok' if not af['bhakoot_present'] or af['bhakoot_cancelled'] else 'badge-bad'}">Bhakoot: {'Cancelled' if af['bhakoot_cancelled'] else ('Dosha' if af['bhakoot_present'] else 'Clear')}</span>
          </div>
        </div>
        <div class="score-track"><div class="score-fill" style="width:{ash_pct:.1f}%;"></div></div>
      </div>
      <table class="data-tbl">
        <thead><tr>
          <th style="width:19%;">{'கூடம்' if is_ta else 'Koota'}</th>
          <th style="width:23%;">{'கணக்கீடு' if is_ta else 'Calculation'}</th>
          <th style="width:10%;" class="center">{'புள்ளி' if is_ta else 'Points'}</th>
          <th style="width:11%;" class="center">{'நிலை' if is_ta else 'Status'}</th>
          <th style="width:37%;">{'விளக்கம் & விலக்கு விதிகள்' if is_ta else 'Interpretation & Exceptions'}</th>
        </tr></thead>
        <tbody>{ash_rows_html}</tbody>
      </table>
    </section>

    <!-- PAGE 5: KUJA SAMADOSHAM & SOUTH INDIAN PAPASAMYA -->
    <section class="new-page">
      <h2 class="sec-title">
        <span>{'5. செவ்வாய் தோஷ சமதோஷம் & தென் இந்திய பாபசாம்யம்' if is_ta else '5. Kuja Samadosham & South Indian Papasamya'}</span>
        <span>{_esc(kf['samadosham_status'] if kf['samadosham_status'] != '-' else kf['mutual_balance'])}</span>
      </h2>
      <div class="parchment-box">
        <b>{'செவ்வாய் சமதோஷ முடிவு' if is_ta else 'Mutual Kuja Samadosham Verdict'}:</b> {_esc(kf['samadosham_status'] if kf['samadosham_status'] != '-' else kf['mutual_balance'])}<br/>
        {_esc(kf['samadosham_expl'] or ('இருவர் ஜாதகங்களிலும் செவ்வாய் நிலை & சமதோஷ விதிவிலக்குகள் சரிபார்க்கப்பட்டன.' if is_ta else 'Tri-reference Mars placement and mutual balance evaluated across both charts.'))}
      </div>
      <div class="grid-2">
        {_render_kuja_detail(kf['groom'], ('மணமகன் செவ்வாய் தோஷ ஆய்வு' if is_ta else f'Groom Kuja Dosha: {ge["name"]}'), is_ta)}
        {_render_kuja_detail(kf['bride'], ('மணமகள் செவ்வாய் தோஷ ஆய்வு' if is_ta else f'Bride Kuja Dosha: {be["name"]}'), is_ta)}
      </div>

      <h2 class="sec-title" style="margin-top:8px;">
        <span>{'தென் இந்திய பாபசாம்யம் (Papasamya Malefic Balance)' if is_ta else 'South Indian Papasamya Malefic Balance'}</span>
        <span>{_esc(pp['verdict'])} ({_esc(pp['diff_str'])})</span>
      </h2>
      <div class="grid-2">
        <div class="dosha-box">
          <div class="dosha-box-hdr"><b>{'மணமகன் பாபம்' if is_ta else 'Groom Papasamya'}</b><span class="pill badge-neutral">{_esc(pp['groom_total'])} pts</span></div>
          <div class="kv-mini">{_esc(pp['groom_frames'])}</div>
          <div class="dosha-detail-p"><b>{'கிரக வாரியாக' if is_ta else 'Planets'}:</b> {_papa_badges(pp['groom_breakdown'])}</div>
        </div>
        <div class="dosha-box">
          <div class="dosha-box-hdr"><b>{'மணமகள் பாபம்' if is_ta else 'Bride Papasamya'}</b><span class="pill badge-neutral">{_esc(pp['bride_total'])} pts</span></div>
          <div class="kv-mini">{_esc(pp['bride_frames'])}</div>
          <div class="dosha-detail-p"><b>{'கிரக வாரியாக' if is_ta else 'Planets'}:</b> {_papa_badges(pp['bride_breakdown'])}</div>
        </div>
      </div>
      <div class="parchment-box">
        <b>{'பாபசாம்யம் தீர்ப்பு' if is_ta else 'Papasamya Verdict'}:</b> {_esc(pp['verdict'])} — {_esc(pp['expl'])}
      </div>
    </section>

    <!-- PAGE 6: 10-POINT INDIVIDUAL DOSHA AUDIT -->
    <section class="new-page">
      <h2 class="sec-title"><span>{'6. விரிவான 10-வகை தோஷ ஆய்வு (Individual Dosha Audit)' if is_ta else '6. Comprehensive 10-Point Dosha Audit Matrix'}</span></h2>
      <table class="data-tbl compact">
        <thead><tr>
          <th style="width:24%;">{'தோஷ வகை' if is_ta else 'Dosha Category'}</th>
          <th style="width:38%;">{'மணமகன் ஜாதகம்' if is_ta else f'Groom: {ge["name"]}'}</th>
          <th style="width:38%;">{'மணமகள் ஜாதகம்' if is_ta else f'Bride: {be["name"]}'}</th>
        </tr></thead>
        <tbody>{dosha_10_html}</tbody>
      </table>
    </section>

    <!-- PAGE 7: INDIVIDUAL VEDIC HOUSES (2,4,5,7,8,12), KARAKAS & D9 CROSS-ANALYSIS -->
    <section class="new-page">
      <h2 class="sec-title"><span>{'7. வேத களத்திர பாவங்கள் (2,4,5,7,8,12), காரகர்கள் & நவாம்ச ஒப்பீடு' if is_ta else '7. Vedic Marriage Houses (2,4,5,7,8,12), Karakas & D9 Cross-Analysis'}</span></h2>
      {_render_vedic_partner_block(vf['groom'], ('மணமகன்' if is_ta else 'Groom') + f': {ge["name"]}', is_ta)}
      {_render_vedic_partner_block(vf['bride'], ('மணமகள்' if is_ta else 'Bride') + f': {be["name"]}', is_ta)}
    </section>

    <!-- PAGE 8: BIDIRECTIONAL SYNASTRY, PLANETARY CONNECTIONS & DIVERGENCES -->
    <section class="new-page">
      <h2 class="sec-title"><span>{'8. இருவழி இணைவு (Synastry), கிரக நிலைகள் ஆய்வு & முரண்பாடுகள்' if is_ta else '8. Bidirectional Synastry, Planetary Pairs & Divergences'}</span></h2>
      <div class="parchment-box">{_esc(sf['explanation'] or ('சந்திர அச்சு & லக்ன அச்சு ஒப்பீட்டு ஆய்வு.' if is_ta else 'Cross-chart Moon and Lagna relationship evaluated.'))}</div>
      <div class="grid-2">
        <div class="syn-card">
          <div class="syn-hdr">{'சந்திரன் - சந்திரன் அச்சு (Moon-to-Moon Axis)' if is_ta else 'Moon-to-Moon Axis'}</div>
          <div><b>{_esc(sf['moon_to_moon']['rel'])}</b> <span class="pill {_status_badge(sf['moon_to_moon']['assessment'])}">{_esc(sf['moon_to_moon']['assessment'])}</span></div>
          <div class="kv-mini" style="margin-top:3px;">Sign Dist: {_esc(sf['moon_to_moon']['dist'])} | Star Dist: {_esc(sf['moon_to_moon']['nak_dist'])} | Pada: {_esc(sf['moon_to_moon']['pada_res'])}</div>
          <p style="margin:3px 0 0 0;">{_esc(sf['moon_to_moon']['expl'])}</p>
        </div>
        <div class="syn-card">
          <div class="syn-hdr">{'லக்னம் - லக்னம் அச்சு (Lagna-to-Lagna Axis)' if is_ta else 'Lagna-to-Lagna Axis'}</div>
          <div><b>{_esc(sf['lagna_to_lagna']['rel'])}</b> <span class="pill {_status_badge(sf['lagna_to_lagna']['assessment'])}">{_esc(sf['lagna_to_lagna']['assessment'])}</span></div>
          <p style="margin:5px 0 0 0;">{_esc(sf['lagna_to_lagna']['expl'])}</p>
        </div>
      </div>

      <h3 class="subtable-hdr">{'பொருத்தமான இணைப்புகள் (Harmonious Connections)' if is_ta else 'Harmonious Planetary Connections'}</h3>
      <table class="data-tbl compact">
        <thead><tr><th style="width:18%;">{'மணமகன் கிரகம்' if is_ta else 'Groom'}</th><th style="width:18%;">{'மணமகள் கிரகம்' if is_ta else 'Bride'}</th><th>{'விளக்கம்' if is_ta else 'Interpretation'}</th></tr></thead>
        <tbody>{harm_html}</tbody>
      </table>

      <h3 class="subtable-hdr">{'பொருத்தமற்ற சேர்க்கைகள் (Challenging Combinations)' if is_ta else 'Incompatible Planetary Combinations'}</h3>
      <table class="data-tbl compact">
        <thead><tr><th style="width:18%;">{'மணமகன் கிரகம்' if is_ta else 'Groom'}</th><th style="width:18%;">{'மணமகள் கிரகம்' if is_ta else 'Bride'}</th><th>{'விளக்கம்' if is_ta else 'Interpretation'}</th></tr></thead>
        <tbody>{incomp_html}</tbody>
      </table>

      <h3 class="subtable-hdr" style="margin-top:6px;">{'முறைசார் முரண்பாடுகள் & தீர்வு (Cross-Tradition Divergences)' if is_ta else 'Cross-Tradition Divergences & Resolution'}</h3>
      {conf_html}
    </section>

    <!-- PAGE 9: KP 7TH CSL & SIGNIFICATORS -->
    <section class="new-page">
      <h2 class="sec-title">
        <span>{'9. கே.பி (KP) 7-ஆம் உப அதிபதி, காரகர்கள் & ஆளுமை கிரகங்கள்' if is_ta else '9. KP 7th Cuspal Sub-Lord, Significators & Ruling Planets'}</span>
        <span>{_esc(kp['agreement_level'])}</span>
      </h2>
      {_render_kp_partner_block(kp['groom'], ('மணமகன் 7-ஆம் உப அதிபதி:' if is_ta else 'Groom 7th CSL:') + f' {ge["name"]}', is_ta)}
      {_render_kp_partner_block(kp['bride'], ('மணமகள் 7-ஆம் உப அதிபதி:' if is_ta else 'Bride 7th CSL:') + f' {be["name"]}', is_ta)}
      <div class="parchment-box avoid-break">
        <b>{'ஆளுமை கிரக ஒப்பீடு (Ruling Planets Agreement):' if is_ta else 'Ruling Planets Agreement:'}</b> {_esc(kp['agreement_level'])} |
        <b>{'பொதுவான கிரகங்கள்' if is_ta else 'Shared RP'}:</b> {_esc(kp['shared_rp'])}
        {''.join(f'<div>• {_esc(n)}</div>' for n in kp['timing_notes'])}
      </div>
    </section>

    <!-- PAGE 10: DASA BHUKTI SEQUENCE & DASA SANDHI -->
    <section class="new-page">
      <h2 class="sec-title"><span>{'10. தசா புக்தி காலவரிசை (Dasa Bhukti Sequence) & தசா சந்தி ஆய்வு' if is_ta else '10. Dasa Bhukti Sequence Timeline & Dasa Sandhi'}</span></h2>
      <div class="dasa-cols-hdr">
        <div>{'மணமகன்' if is_ta else 'Groom'} ({_esc(ge['name'])})</div>
        <div>{'மணமகள்' if is_ta else 'Bride'} ({_esc(be['name'])})</div>
      </div>
      {_render_dasa_svg(base['timeline'])}
      <div class="sandhi-card {'sandhi-yes' if base['dasa_sandhi'].get('has_sandhi') else 'sandhi-no'} avoid-break">
        <b>{'தசா சந்தி ஆய்வு' if is_ta else 'Dasa Sandhi Analysis'}: {'நிலை: இருக்கிறது' if base['dasa_sandhi'].get('has_sandhi') else 'நிலை: இல்லை'}</b>
        <div>{_esc(base['dasa_sandhi'].get('summary_ta'))}</div>
        <div style="font-size:8.2px; color:#475569; margin-top:2px;">{_esc(base['dasa_sandhi'].get('note_ta'))}</div>
      </div>
    </section>

    <!-- PAGE 11: SIVADASAN RAVI SYNTHESIS, HYMNS, SAGE VERDICT & BLESSING -->
    <section class="new-page">
      <h2 class="sec-title">
        <span>{'11. ' + sr['treatise_title'] if is_ta else '11. Sivadasan Ravi Treatise Insights, Remedies & Verdict'}</span>
        <span>{_esc(sr['author'])}</span>
      </h2>
      <div class="grid-2">
        <div class="dosha-box">
          <div class="dosha-box-hdr"><b>{'தசைப் பொருத்தம்' if is_ta else 'Dasa Porutham'}</b><span class="pill {_status_badge(sr['dasa_porutham']['verdict'])}">{_esc(sr['dasa_porutham']['verdict'])}</span></div>
          <div class="kv-mini">Groom: <b>{_esc(sr['dasa_porutham']['groom_md'])}</b> | Bride: <b>{_esc(sr['dasa_porutham']['bride_md'])}</b></div>
          {''.join(f'<div class="dosha-detail-p">• {_esc(f)}</div>' for f in sr['dasa_porutham']['findings'])}
        </div>
        <div class="dosha-box">
          <div class="dosha-box-hdr"><b>{'கோட்சார குரு பலம் (Guru Balam)' if is_ta else 'Gochara Guru Balam'}</b><span class="pill badge-gold">{_esc(sr['guru_balam']['transit_sign'])}</span></div>
          <div class="kv-mini"><b>{_esc(sr['guru_balam']['label'])}</b> (G: H{_esc(sr['guru_balam']['groom_house'])} / B: H{_esc(sr['guru_balam']['bride_house'])})</div>
          <div class="dosha-detail-p">{_esc(sr['guru_balam']['desc'])}</div>
        </div>
      </div>

      <div class="dosha-box avoid-break" style="margin-bottom:8px;">
        <div class="dosha-box-hdr"><b>{'நாடிப் பொருத்தம் & நந்தியோகம்' if is_ta else 'Nadi Porutham & Nandi Yogam'}</b><span class="pill {_status_badge(sr['nadi_porutham']['verdict'])}">{_esc(sr['nadi_porutham']['verdict'])}</span></div>
        <div class="dosha-detail-p">{_esc(sr['nadi_porutham']['summary'])}</div>
        {f'<ul style="margin:3px 0 0 14px; color:#92400E;">{nandi_obs_html}</ul>' if sr['nadi_porutham']['has_nandi'] and nandi_obs_html else ''}
      </div>

      <div class="dosha-box avoid-break" style="margin-bottom:8px;">
        <div class="dosha-box-hdr"><b>{'விசேஷ நட்சத்திர மாமனார்/மாமியார் ஆய்வு' if is_ta else 'Special In-Laws Nakshatra Afflictions & Exemptions'}</b></div>
        {inlaws_html}
      </div>

      <div class="parchment-box avoid-break">
        <b>{'முதன்மை பரிகார ஸ்தலம் (Primary Parikara Sthalam):' if is_ta else 'Primary Parikara Sthalam:'}</b> {_esc(sr['temple_name'])}<br/>
        {_esc(sr['temple_sig'])}
      </div>

      {hymns_html}

      <div class="parchment-box avoid-break" style="margin-top:6px;">
        <b style="color:#153F6B; font-size:10px;">{'முனிவரின் வாக்கு (Sage Verdict)' if is_ta else "Sage's Final Summary"}:</b><br/>
        {_esc(base['sage_verdict_ta'])}
      </div>

      <div class="advisory-box info-box avoid-break">
        <b>{'ஜோதிட நெறிமுறை அறிவிப்பு' if is_ta else 'Ethical Astrological Disclaimer'}:</b> {_esc(comp['disclaimer'])}
      </div>

      <div class="blessing-box avoid-break">
        <div style="font-weight:800; font-size:10.5px; color:#8B6914; margin-bottom:4px;">✦ {'மங்கள வாழ்த்துச் செய்தி' if is_ta else 'Auspicious Blessings'} ✦</div>
        <div><b>சீக்கிரம் திருமணம் நடைபெற இறைவனை நாங்கள் எங்கள் Gokul&apos;s Astrological Insights சார்பாக மனதார வேண்டிக்கொள்கிறோம்... வாழ்த்துக்கள்!</b></div>
        <div style="font-style:italic; color:#475569; margin-top:3px;">&ldquo;sikiram kalyanam nadakanum nu aandavana nanga enga Gokul&apos;s Astrological Insights side la irundhu vendikurom..vaazhthukkal&rdquo;</div>
        <div style="margin-top:4px; font-size:8.4px; color:#475569;">Gokul&apos;s Astrological Insights • Thiruverkadu, Chennai - 600077 • Ph: 9444 55 9071</div>
      </div>
    </section>

  </div>
</body>
</html>"""


def generate_marriage_compatibility_pdf_bytes(data: Dict[str, Any], language: str = "en") -> bytes:
    """Compiles the Comprehensive Royal Gold Marriage Compatibility PDF via Playwright or ReportLab."""
    lang = "ta" if str(language).lower() in ("ta", "tamil") else "en"
    html_doc = generate_html_report(data, lang=lang)

    header_tpl = (
        '<div style="width:100%; font-family: system-ui, sans-serif; font-size:7.5px; color:#153F6B; '
        'font-weight:700; padding:0 12mm; display:flex; justify-content:space-between; border-bottom:0.5px solid #D8BD80;">'
        '<span>Gokul&apos;s Astrological Insights • Marriage Compatibility Dossier</span>'
        '<span style="color:#8B6914;">Confidential Vedic &amp; KP Synthesis</span></div>'
    )
    footer_tpl = (
        '<div style="width:100%; font-family: system-ui, sans-serif; font-size:7.5px; color:#475569; '
        'padding:0 12mm; display:flex; justify-content:space-between; border-top:0.5px solid #D8BD80;">'
        '<span>© Gokul&apos;s Astrological Insights • 165, Sakreeshwari Nagar, 2nd St, Thiruverkadu, Chennai - 600077 • Ph: 9444 55 9071</span>'
        '<span style="font-weight:700; color:#153F6B;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_content(html_doc, wait_until="load")
                return page.pdf(
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                    display_header_footer=True,
                    header_template=header_tpl,
                    footer_template=footer_tpl,
                )
            finally:
                browser.close()
    except Exception as exc:
        logger.warning("Chromium PDF generation unavailable, falling back to ReportLab: %s", exc)
        from app.services.pdf_report_engine.marriage_compatibility_generator_rl import (
            generate_marriage_compatibility_pdf_bytes_rl,
        )
        return generate_marriage_compatibility_pdf_bytes_rl(data, language=language)


class MarriageCompatibilityPdfGenerator:
    """Wrapper class matching engine generator interface."""

    def __init__(self, data: Dict[str, Any], language: str = "en"):
        self.data = data
        self.language = language

    def generate(self) -> bytes:
        return generate_marriage_compatibility_pdf_bytes(self.data, language=self.language)
