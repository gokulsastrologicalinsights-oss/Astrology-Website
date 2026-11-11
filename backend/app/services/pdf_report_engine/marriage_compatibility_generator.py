"""Marriage Compatibility PDF Report Generator (5-Page Print-Aligned Format).

Generates the exact 5-page Tamil/English A4 layout matching the frontend Print
template (`MarriageCompatibilityPrintReport.tsx`) using Playwright Chromium with
bundled Noto Sans Tamil fonts and local brand logo, falling back to ReportLab
when headless Chromium is unavailable.
"""

from __future__ import annotations

import html
import logging
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from app.services.pdf_report_engine.marriage_print_viewmodel import (
    DASA_COLORS,
    NOTO_BOLD_PATH,
    NOTO_REGULAR_PATH,
    build_marriage_print_view_model,
)

logger = logging.getLogger("gai.pdf.marriage_generator")


def _esc(val: Any) -> str:
    return html.escape(str(val if val is not None else ""))


def _render_chart_html(chart: Dict[str, Any]) -> str:
    cells: Dict[int, List[str]] = chart["cells"]

    def _cell(sign_idx: int) -> str:
        items = "".join(f"<span>{_esc(txt)}</span>" for txt in cells.get(sign_idx, []))
        return f'<td class="si-cell"><div class="si-items">{items}</div></td>'

    return f"""
    <div class="chart-wrap">
      <div class="chart-title">{_esc(chart["title"])}</div>
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
        return '<span class="dosha-none">இல்லை</span>'
    is_mitigated = cell.get("status") == "MITIGATED"
    cls = "dosha-mitigated" if is_mitigated else "dosha-present"
    header = (
        "தோஷ நிவர்த்தி"
        if is_mitigated
        else f"தோஷம் உள்ளது (Effective Dosha Severity: {cell.get('severity_percent', 40)}%)"
    )
    reasons = cell.get("reasons_ta") or []
    reasons_html = ""
    if reasons:
        lines = "".join(f'<div class="dosha-reason-line">{_esc(r)}</div>' for r in reasons)
        reasons_html = f'<div class="dosha-reason-hdr">காரணங்கள்:</div>{lines}'
    return f'<div class="{cls}"><div class="dosha-hdr">{_esc(header)}</div>{reasons_html}</div>'


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
        f'<svg viewBox="0 0 {int(svg_w)} {int(svg_h)}" class="dasa-svg" role="img" aria-label="Dasa Bhukti Sequence Timeline">',
        """<defs>
          <marker id="arrowRedEnd" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#DC2626" />
          </marker>
          <marker id="arrowRedStart" markerWidth="6" markerHeight="6" refX="1" refY="3" orient="auto">
            <path d="M6,0 L0,3 L6,6 Z" fill="#DC2626" />
          </marker>
        </defs>""",
    ]

    def _draw_side_rects(mds: List[Dict[str, Any]], x_bar: float, x_yr: float, anchor: str) -> None:
        for idx, md in enumerate(mds):
            y_top = y_for_year(md["start_year"])
            y_bot = y_for_year(md["end_year"])
            h = max(2.0, y_bot - y_top)
            col = DASA_COLORS.get(md["lord_en"], {"bg": "#64748B", "light_bg": "#CBD5E1", "text": "#FFFFFF"})
            is_active = float(md["start_year"]) < current_yr < float(md["end_year"])
            if is_active:
                parts.append(
                    f'<rect x="{x_bar}" y="{y_top:.2f}" width="145" height="{max(1.0, now_y - y_top):.2f}" '
                    f'fill="{col["light_bg"]}" stroke="#FFFFFF" stroke-width="1" />'
                )
                parts.append(
                    f'<rect x="{x_bar}" y="{now_y:.2f}" width="145" height="{max(1.0, y_bot - now_y):.2f}" '
                    f'fill="{col["bg"]}" stroke="#FFFFFF" stroke-width="1" />'
                )
            else:
                parts.append(
                    f'<rect x="{x_bar}" y="{y_top:.2f}" width="145" height="{h:.2f}" '
                    f'fill="{col["bg"]}" stroke="#FFFFFF" stroke-width="1" />'
                )
            parts.append(
                f'<text x="{x_yr}" y="{y_top + 4:.2f}" text-anchor="{anchor}" font-size="10" fill="#64748B">{_esc(md.get("start_cal_year"))}</text>'
            )
            if idx == len(mds) - 1:
                parts.append(
                    f'<text x="{x_yr}" y="{y_bot + 3:.2f}" text-anchor="{anchor}" font-size="10" fill="#64748B">{_esc(md.get("end_cal_year"))}</text>'
                )

    _draw_side_rects(g_mds, 70, 62, "end")
    _draw_side_rects(b_mds, 465, 618, "start")

    if top_pad <= now_y <= svg_h - bot_pad:
        now_x = 30 if tl["now_collides_with_g_start"] else 60
        now_anchor = "start" if tl["now_collides_with_g_start"] else "end"
        parts.append(f'<line x1="32" y1="{now_y:.2f}" x2="215" y2="{now_y:.2f}" stroke="#DC2626" stroke-width="1.5" />')
        parts.append(
            f'<text x="{now_x}" y="{now_y - 4:.2f}" text-anchor="{now_anchor}" font-size="10" font-weight="700" fill="#DC2626">Now</text>'
        )

    def _draw_side_labels(mds: List[Dict[str, Any]], x_center: float, avoid_now: bool) -> None:
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
                upper_h = now_y - y_top
                lower_h = y_bot - now_y
                text_y = (
                    now_y + max(13.0, lower_h / 2.0 + 3.0)
                    if lower_h >= upper_h
                    else now_y - max(6.0, upper_h / 2.0 - 3.0)
                )
            text_y = min(y_bot - 5.0, max(y_top + 13.0, text_y))
            label_bg = col["light_bg"] if (is_active and text_y < now_y) else col["bg"]
            parts.append(
                f'<text x="{x_center}" y="{text_y:.2f}" text-anchor="middle" font-size="12" font-weight="700" '
                f'fill="{col["text"]}" stroke="{label_bg}" stroke-width="3" paint-order="stroke">{_esc(md.get("lord_ta"))}</text>'
            )

    _draw_side_labels(g_mds, 142.5, True)
    _draw_side_labels(b_mds, 537.5, False)

    for tr in tl["rendered_transitions"]:
        y_t = tr["y"]
        parts.append(
            f'<line x1="221" y1="{y_t:.2f}" x2="459" y2="{y_t:.2f}" stroke="#DC2626" stroke-width="1.1" '
            f'marker-start="url(#arrowRedStart)" marker-end="url(#arrowRedEnd)" />'
        )
        parts.append(
            f'<text x="340" y="{y_t - 3:.2f}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#7F1D1D">{_esc(tr["label_ta"])}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def generate_html_report(data: Dict[str, Any], lang: str = "ta") -> str:
    """Compiles the 5-page print-ready HTML document matching `MarriageCompatibilityPrintReport`."""
    vm = build_marriage_print_view_model(data)
    gp = vm["groom"]
    bp = vm["bride"]
    verdict = vm["verdict"]
    tone = verdict["tone"]

    if tone == "green":
        v_border, v_bg, v_hdr_bg = "#16A34A", "#F0FDF4", "#15803D"
    elif tone == "amber":
        v_border, v_bg, v_hdr_bg = "#D97706", "#FFFBEB", "#B45309"
    else:
        v_border, v_bg, v_hdr_bg = "#DC2626", "#FFF1F2", "#B91C1C"

    font_faces: List[str] = []
    if NOTO_REGULAR_PATH.exists():
        font_faces.append(
            f"@font-face {{ font-family: 'Noto Sans Tamil'; font-weight: 400; src: url('{NOTO_REGULAR_PATH.as_uri()}') format('truetype'); }}"
        )
    if NOTO_BOLD_PATH.exists():
        font_faces.append(
            f"@font-face {{ font-family: 'Noto Sans Tamil'; font-weight: 700; src: url('{NOTO_BOLD_PATH.as_uri()}') format('truetype'); }}"
        )
    font_face_css = "\n".join(font_faces)

    logo_img = (
        f'<img src="{vm["logo_data_uri"]}" alt="Gokul\'s Astrological Insights Logo" class="logo-img" />'
        if vm["logo_data_uri"]
        else ""
    )

    porutham_rows_html = "".join(
        f"""
        <tr>
          <td class="p-lbl">{_esc(r["label"])}</td>
          <td class="p-desc">{_esc(r["desc"])}</td>
          <td class="p-val">{_esc(r["groom_val"])}</td>
          <td class="p-val">{_esc(r["bride_val"])}</td>
          <td class="p-status">
            <span class="{'tick-ok' if r['pass'] else 'tick-no'}">{'✓' if r['pass'] else '✗'}</span>
          </td>
        </tr>
        """
        for r in vm["matching_rows"]
    )

    charts_html = "".join(_render_chart_html(ch) for ch in vm["charts"])

    dosha_rows_html = "".join(
        f"""
        <tr>
          <td class="d-lbl">{_esc(row.get("label_ta"))}</td>
          <td class="d-cell">{_render_dosha_cell_html(row.get("groom"))}</td>
          <td class="d-cell">{_render_dosha_cell_html(row.get("bride"))}</td>
        </tr>
        """
        for row in vm["dosha_audit"]
    )

    ds = vm["dasa_sandhi"]
    ds_box_cls = "sandhi-box sandhi-yes" if ds.get("has_sandhi") else "sandhi-box sandhi-no"
    ds_status_lbl = "நிலை: இருக்கிறது" if ds.get("has_sandhi") else "நிலை: இல்லை"

    harm_rows = vm["harmonious_connections"]
    harm_html = (
        "".join(
            f"""
            <tr>
              <td class="harm-planet">{_esc(item.get("groom_planet_ta"))}</td>
              <td class="harm-planet">{_esc(item.get("bride_planet_ta"))}</td>
              <td class="harm-desc">{_esc(item.get("description_ta"))}</td>
            </tr>
            """
            for item in harm_rows
        )
        if harm_rows
        else '<tr><td colspan="3" class="empty-msg">இரு ஜாதகங்களிலும் ஒரே ராசியில் இணையும் சுப கிரக அமைப்புகள் குறைவாக உள்ளன; நட்சத்திரப் பொருத்தம் அடிப்படையில் மதிப்பீடு செய்யப்பட்டது.</td></tr>'
    )

    incomp_rows = vm["incompatible_combinations"]
    incomp_html = (
        "".join(
            f"""
            <tr>
              <td class="incomp-planet">{_esc(item.get("groom_planet_ta"))}</td>
              <td class="incomp-planet">{_esc(item.get("bride_planet_ta"))}</td>
              <td class="incomp-desc">{_esc(item.get("description_ta"))}</td>
            </tr>
            """
            for item in incomp_rows
        )
        if incomp_rows
        else '<tr><td colspan="3" class="incomp-empty">பொருத்தமற்ற எதிர்மறை கிரக சேர்க்கைகள் எதுவும் கண்டறியப்படவில்லை.</td></tr>'
    )

    p6 = vm["page6"]
    ash_badge_cls = "p6-badge-ok" if p6["ashtakoota_threshold_met"] else "p6-badge-no"
    ash_badge_txt = f"மொத்தம்: {p6['ashtakoota_total_str']} / 36 (குறைந்தபட்சம் {p6['ashtakoota_threshold_str']})"

    def _ash_tone_cls(tone: str) -> str:
        return "st-ok" if tone == "green" else ("st-warn" if tone == "amber" else "st-bad")

    ash_rows_html = "".join(
        f"""
        <tr>
          <td class="a-lbl">{_esc(r["label_ta"])}</td>
          <td class="a-sig">{_esc(r["sig_ta"])}{f'<div class="a-cancel">விலக்கு: {_esc(r["cancel_reason"])}</div>' if r.get("cancel_reason") else ''}</td>
          <td class="a-pts">{_esc(r["earned_str"])} / {_esc(r["max_str"])}</td>
          <td class="a-st"><span class="{_ash_tone_cls(r['status_tone'])}">{_esc(r["status_ta"])}</span></td>
        </tr>
        """
        for r in p6["ashtakoota_rows"]
    )

    papa = p6["papasamya"]
    papa_tone_cls = _ash_tone_cls(papa["verdict_tone"])
    kp = p6["kp"]
    kp_body_html = (
        f"""
        <div class="card-row"><span>மணமகன் 7-ஆம் உப அதிபதி:</span> <b>{_esc(kp["groom_csl_ta"])}</b> ({_esc(kp["groom_verdict_ta"])})</div>
        <div class="card-sub">சாதக பாவங்கள்: [{_esc(kp["groom_houses"])}]</div>
        <div class="card-row" style="margin-top:4px;"><span>மணமகள் 7-ஆம் உப அதிபதி:</span> <b>{_esc(kp["bride_csl_ta"])}</b> ({_esc(kp["bride_verdict_ta"])})</div>
        <div class="card-sub">சாதக பாவங்கள்: [{_esc(kp["bride_houses"])}]</div>
        <div class="card-foot">ஆளுமை கிரக ஒப்பீடு: <b>{_esc(kp["agreement_ta"])}</b> | பொது கிரகங்கள்: {_esc(kp["shared_rp_ta"])}</div>
        """
        if kp["available"]
        else '<div class="card-sub">கே.பி (KP) 7-ஆம் உப அதிபதி தரவு சேர்க்கப்படவில்லை.</div>'
    )

    guru = p6["guru_balam"]
    nadi_y = p6["nadi_yogam"]
    in_laws = p6["in_laws"]
    nav = p6["navamsa"]
    rem = p6["remedies"]

    nadi_obs_html = "".join(f'<div class="sp-sub">• {_esc(o)}</div>' for o in (nadi_y.get("obstacles_ta") or []))
    inlaws_html = (
        "".join(
            f'<div class="sp-line"><b>{_esc(f["nakshatra_ta"])} ({_esc(f["relative_ta"])}):</b> {"விதிவிலக்கு பொருந்தியது (தோஷமில்லை)" if f["is_exempt"] else "கவனம் தேவை"} — {_esc(f["explanation_ta"])}</div>'
            for f in in_laws["findings"]
        )
        if in_laws["has_special"] and in_laws["findings"]
        else '<div class="sp-line"><b>மாமனார்/மாமியார் விசேஷ நட்சத்திர ஆய்வு:</b> விசேஷ நட்சத்திர தோஷம் எதுவும் இல்லை.</div>'
    )
    nav_warn_html = (
        '<div class="nav-warn">நேர எச்சரிக்கை: பிறப்பு நேர சிறு மாற்றத்தால் நவாம்ச லக்னம் மாற வாய்ப்புள்ளதால் நேர உறுதிப்படுத்தல் நல்லது.</div>'
        if nav["boundary_warning"]
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="ta">
<head>
<meta charset="utf-8" />
<title>Marriage Compatibility Report</title>
<style>
  {font_face_css}

  @page {{
    size: A4 portrait;
    margin: 10mm;
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  body {{
    margin: 0;
    padding: 0;
    background: #FFFFFF;
    color: #0F172A;
    font-family: 'Noto Sans Tamil', 'Nirmala UI', 'Latha', system-ui, -apple-system, sans-serif;
  }}

  .report-root {{
    max-width: 190mm;
    margin: 0 auto;
  }}

  .print-page {{
    break-after: page;
    page-break-after: always;
  }}
  .print-page:last-child {{
    break-after: auto;
    page-break-after: auto;
  }}

  /* Page 1 */
  .brand-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #CBD5E1;
    padding-bottom: 10px;
    margin-bottom: 14px;
  }}
  .logo-box {{ width: 64px; height: 64px; flex-shrink: 0; }}
  .logo-img {{ width: 64px; height: 64px; object-fit: contain; display: block; }}
  .brand-center {{ flex: 1; text-align: center; padding-right: 64px; }}
  .brand-title {{ margin: 0; font-size: 20px; font-weight: 700; color: #0F172A; line-height: 1.2; }}
  .brand-addr {{ margin: 3px 0 0 0; font-size: 11px; color: #334155; line-height: 1.35; }}

  .profiles-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin-bottom: 14px;
    font-size: 11.5px;
  }}
  .profile-col h2 {{ margin: 0 0 8px 0; text-align: center; font-size: 15px; font-weight: 700; }}
  .groom-h2 {{ color: #0284C7; }}
  .bride-h2 {{ color: #0D9488; }}
  .profile-tbl {{ width: 100%; border-collapse: collapse; }}
  .profile-tbl td {{ padding: 2.5px 0; vertical-align: top; }}
  .profile-lbl {{ color: #64748B; width: 44%; }}
  .profile-val {{ font-weight: 700; color: #0F172A; }}

  .verdict-box {{
    border: 1.5px solid {v_border};
    background: {v_bg};
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 16px;
  }}
  .verdict-hdr {{
    background: {v_hdr_bg};
    color: #FFFFFF;
    text-align: center;
    padding: 7px 12px;
    font-size: 16px;
    font-weight: 700;
  }}
  .verdict-metrics {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    text-align: center;
    padding: 10px 8px;
  }}
  .metric-col {{ padding: 0 8px; }}
  .metric-lbl {{ font-size: 10.5px; color: #334155; font-weight: 500; }}
  .metric-val {{ font-size: 14px; font-weight: 700; color: #0F172A; margin-top: 2px; }}
  .metric-val-mid {{ font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 2px; }}

  .sec-h3 {{ margin: 0 0 8px 0; font-size: 17px; font-weight: 700; color: #0F172A; }}
  .sec-h2 {{ margin: 0 0 10px 0; font-size: 19px; font-weight: 700; color: #0F172A; }}

  .porutham-tbl {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
  .porutham-tbl th, .porutham-tbl td {{ border: 1px solid #94A3B8; }}
  .porutham-tbl th {{ background: #F1F5F9; color: #0F172A; font-weight: 700; padding: 7px; text-align: left; }}
  .porutham-tbl th.center {{ text-align: center; }}
  .porutham-tbl td {{ background: #FFFFFF; padding: 5.5px 8px; vertical-align: middle; }}
  .p-lbl {{ font-weight: 700; color: #0F172A; }}
  .p-desc {{ color: #1E293B; line-height: 1.35; }}
  .p-val {{ color: #0F172A; }}
  .p-status {{ text-align: center; font-weight: 700; font-size: 13px; }}
  .tick-ok {{ color: #059669; }}
  .tick-no {{ color: #E11D48; }}

  /* Page 2 */
  .charts-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 32px;
    row-gap: 38px;
    padding-top: 12px;
  }}
  .chart-wrap {{ display: flex; flex-direction: column; align-items: center; }}
  .chart-title {{ font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 6px; text-align: center; }}
  .si-table {{ width: 100%; max-width: 300px; border-collapse: collapse; border: 2px solid #0F172A; table-layout: fixed; background: #FFFFFF; }}
  .si-cell {{ border: 1px solid #0F172A; width: 25%; height: 68px; text-align: center; vertical-align: middle; padding: 4px; }}
  .si-items {{ display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1.25; font-size: 10.5px; font-weight: 500; color: #0F172A; }}
  .si-center {{ border: 1px solid #0F172A; text-align: center; vertical-align: middle; font-weight: 700; font-size: 12px; color: #0F172A; background: #FFFFFF; }}

  /* Page 3 */
  .dosha-tbl {{ width: 100%; border-collapse: collapse; font-size: 10.5px; }}
  .dosha-tbl th, .dosha-tbl td {{ border: 1px solid #94A3B8; }}
  .dosha-tbl th {{ background: #F1F5F9; color: #0F172A; font-weight: 700; padding: 7px 8px; text-align: left; }}
  .dosha-tbl td {{ background: #FFFFFF; padding: 7px 9px; vertical-align: middle; }}
  .d-lbl {{ font-weight: 700; color: #0F172A; }}
  .dosha-none {{ color: #334155; font-weight: 500; }}
  .dosha-mitigated {{ color: #047857; line-height: 1.35; }}
  .dosha-present {{ color: #BE123C; line-height: 1.35; }}
  .dosha-hdr {{ font-weight: 700; }}
  .dosha-reason-hdr {{ font-weight: 600; margin-top: 2px; }}
  .dosha-reason-line {{ padding-left: 4px; margin-top: 1px; }}

  /* Page 4 */
  .dasa-cols-hdr {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    text-align: center;
    font-weight: 700;
    font-size: 13px;
    color: #0F172A;
    margin-bottom: 6px;
  }}
  .dasa-col-g {{ padding-right: 64px; }}
  .dasa-col-b {{ padding-left: 64px; }}
  .dasa-svg {{ width: 100%; height: auto; max-height: 240mm; display: block; margin: 0 auto; }}

  /* Page 5 */
  .page5-stack {{ padding-top: 4px; }}
  .sandhi-box {{ border-radius: 6px; padding: 12px 14px; font-size: 11px; margin-bottom: 18px; }}
  .sandhi-yes {{ background: #FFF1F2; border: 1px solid #FECDD3; color: #9F1239; }}
  .sandhi-no {{ background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; }}
  .sandhi-status {{ font-weight: 700; font-size: 12px; margin-bottom: 5px; }}
  .sandhi-summary {{ font-weight: 500; line-height: 1.4; margin-bottom: 5px; }}
  .sandhi-note {{ color: #475569; font-size: 10.5px; line-height: 1.4; }}

  .sub-h3 {{ margin: 0 0 6px 0; font-size: 13px; font-weight: 700; color: #0F172A; }}
  .pa-tbl {{ width: 100%; border-collapse: collapse; font-size: 10.5px; margin-bottom: 14px; }}
  .pa-tbl th, .pa-tbl td {{ border: 1px solid #94A3B8; }}
  .pa-tbl th {{ background: #F1F5F9; color: #0F172A; font-weight: 700; padding: 7px 8px; text-align: left; }}
  .pa-tbl td {{ background: #FFFFFF; padding: 7px 9px; vertical-align: middle; }}
  .harm-planet {{ font-weight: 500; color: #047857; }}
  .harm-desc {{ color: #047857; line-height: 1.35; }}
  .incomp-planet {{ font-weight: 500; color: #BE123C; }}
  .incomp-desc {{ color: #BE123C; line-height: 1.35; }}
  .empty-msg {{ color: #475569; }}
  .incomp-empty {{ color: #047857; }}
  .sage-text {{ margin: 0; font-size: 11.5px; line-height: 1.65; color: #0F172A; }}

  /* Page 6 */
  .page6-stack {{ padding-top: 2px; }}
  .p6-hdr-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .p6-badge-ok {{ background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .p6-badge-no {{ background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .ash-tbl {{ width: 100%; border-collapse: collapse; font-size: 9.8px; margin-bottom: 10px; }}
  .ash-tbl th, .ash-tbl td {{ border: 1px solid #94A3B8; padding: 4px 6px; }}
  .ash-tbl th {{ background: #F1F5F9; font-weight: 700; text-align: left; color: #0F172A; }}
  .ash-tbl th.center {{ text-align: center; }}
  .a-lbl {{ font-weight: 700; color: #0F172A; width: 25%; }}
  .a-sig {{ color: #334155; width: 47%; line-height: 1.3; }}
  .a-cancel {{ color: #047857; font-weight: 600; font-size: 9px; margin-top: 1px; }}
  .a-pts {{ text-align: center; font-weight: 700; color: #0F172A; width: 14%; }}
  .a-st {{ text-align: center; font-weight: 700; width: 14%; }}
  .st-ok {{ color: #047857; font-weight: 700; }}
  .st-warn {{ color: #B45309; font-weight: 700; }}
  .st-bad {{ color: #BE123C; font-weight: 700; }}

  .cards-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px; }}
  .info-card {{ border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 10px; background: #F8FAFC; font-size: 9.8px; }}
  .card-title {{ font-weight: 700; font-size: 11px; color: #0F172A; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px; margin-bottom: 6px; }}
  .card-row {{ color: #0F172A; line-height: 1.35; }}
  .card-sub {{ color: #475569; font-size: 9px; line-height: 1.3; margin-top: 1px; }}
  .card-foot {{ margin-top: 5px; padding-top: 4px; border-top: 1px dashed #CBD5E1; color: #1E293B; font-size: 9.2px; line-height: 1.35; }}

  .sp-panel {{ border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 10px; background: #FFFFFF; font-size: 9.8px; margin-bottom: 10px; }}
  .sp-line {{ color: #1E293B; line-height: 1.4; margin-bottom: 4px; }}
  .sp-sub {{ color: #475569; font-size: 9px; padding-left: 10px; line-height: 1.35; margin-bottom: 2px; }}
  .nav-warn {{ color: #B45309; font-weight: 600; font-size: 9.2px; margin-top: 2px; }}

  .rem-box {{ border: 1px solid #FDE68A; background: #FFFBEB; border-radius: 6px; padding: 8px 10px; font-size: 9.8px; margin-bottom: 8px; }}
  .rem-title {{ font-weight: 700; color: #92400E; margin-bottom: 3px; font-size: 10.5px; }}
  .rem-text {{ color: #334155; line-height: 1.38; }}
  .disc-note {{ font-size: 8.8px; color: #64748B; line-height: 1.35; border-top: 1px solid #E2E8F0; padding-top: 5px; margin: 0; }}
</style>
</head>
<body>
  <div class="report-root">
    <!-- PAGE 1 -->
    <section class="print-page">
      <div class="brand-header">
        <div class="logo-box">{logo_img}</div>
        <div class="brand-center">
          <h1 class="brand-title">Gokul's Astrological Insights</h1>
          <p class="brand-addr">165, Sakreeshwari Nagar, 2nd Street,<br/>Thiruverkadu, Chennai - 600077</p>
        </div>
      </div>

      <div class="profiles-grid">
        <div class="profile-col">
          <h2 class="groom-h2">மணமகன்</h2>
          <table class="profile-tbl">
            <tr><td class="profile-lbl">பெயர்</td><td class="profile-val">{_esc(gp["name"])}</td></tr>
            <tr><td class="profile-lbl">ராசி</td><td class="profile-val">{_esc(gp["rasi_ta"])}</td></tr>
            <tr><td class="profile-lbl">நட்சத்திரம் (பாதம்)</td><td class="profile-val">{_esc(gp["nakshatra_pada_ta"])}</td></tr>
            <tr><td class="profile-lbl">லக்கினம்</td><td class="profile-val">{_esc(gp["lagna_ta"])}</td></tr>
            <tr><td class="profile-lbl">பிறந்த தேதி</td><td class="profile-val">{_esc(gp["dob_age"])}</td></tr>
          </table>
        </div>
        <div class="profile-col">
          <h2 class="bride-h2">மணமகள்</h2>
          <table class="profile-tbl">
            <tr><td class="profile-lbl">பெயர்</td><td class="profile-val">{_esc(bp["name"])}</td></tr>
            <tr><td class="profile-lbl">ராசி</td><td class="profile-val">{_esc(bp["rasi_ta"])}</td></tr>
            <tr><td class="profile-lbl">நட்சத்திரம் (பாதம்)</td><td class="profile-val">{_esc(bp["nakshatra_pada_ta"])}</td></tr>
            <tr><td class="profile-lbl">லக்கினம்</td><td class="profile-val">{_esc(bp["lagna_ta"])}</td></tr>
            <tr><td class="profile-lbl">பிறந்த தேதி</td><td class="profile-val">{_esc(bp["dob_age"])}</td></tr>
          </table>
        </div>
      </div>

      <div class="verdict-box">
        <div class="verdict-hdr">{_esc(verdict["title"])}</div>
        <div class="verdict-metrics">
          <div class="metric-col">
            <div class="metric-lbl">பொருத்தம் மதிப்பெண்</div>
            <div class="metric-val">{vm["passed_count_11"]} / 11</div>
          </div>
          <div class="metric-col">
            <div class="metric-lbl">தோஷ சமநிலை</div>
            <div class="metric-val-mid">{_esc(vm["kuja_summary_ta"])}</div>
          </div>
          <div class="metric-col">
            <div class="metric-lbl">அஷ்டகூட மதிப்பெண் (36)</div>
            <div class="metric-val">{_esc(vm["ashtakoota_str"])} / 36</div>
          </div>
        </div>
      </div>

      <h3 class="sec-h3">பொருத்த மதிப்பீடு</h3>
      <table class="porutham-tbl">
        <thead>
          <tr>
            <th style="width:18%;">பொருத்தம்<br/>(கூட்டம்)</th>
            <th style="width:34%;">விளக்கம்</th>
            <th style="width:17%;">மணமகன்<br/>அம்சம்</th>
            <th style="width:17%;">மணமகள்<br/>அம்சம்</th>
            <th style="width:14%;" class="center">பொருத்தம்</th>
          </tr>
        </thead>
        <tbody>
          {porutham_rows_html}
        </tbody>
      </table>
    </section>

    <!-- PAGE 2 -->
    <section class="print-page">
      <div class="charts-grid">
        {charts_html}
      </div>
    </section>

    <!-- PAGE 3 -->
    <section class="print-page">
      <h2 class="sec-h2">தோஷ ஆய்வு</h2>
      <table class="dosha-tbl">
        <thead>
          <tr>
            <th style="width:24%;">தோஷ வகை</th>
            <th style="width:38%;">மணமகன் ஜாதகம்</th>
            <th style="width:38%;">மணமகள் ஜாதகம்</th>
          </tr>
        </thead>
        <tbody>
          {dosha_rows_html}
        </tbody>
      </table>
    </section>

    <!-- PAGE 4 -->
    <section class="print-page">
      <h2 class="sec-h2">Dasa Bhukti Sequence</h2>
      <div class="dasa-cols-hdr">
        <div class="dasa-col-g">மணமகன்</div>
        <div class="dasa-col-b">மணமகள்</div>
      </div>
      {_render_dasa_svg(vm["timeline"])}
    </section>

    <!-- PAGE 5 -->
    <section class="print-page page5-stack">
      <h2 class="sec-h2">தசா சந்தி ஆய்வு</h2>
      <div class="{ds_box_cls}">
        <div class="sandhi-status">{ds_status_lbl}</div>
        <div class="sandhi-summary">{_esc(ds.get("summary_ta"))}</div>
        <div class="sandhi-note">{_esc(ds.get("note_ta"))}</div>
      </div>

      <h2 class="sec-h2">கிரக நிலைகள் ஆய்வு (கிரக பகுப்பாய்வு)</h2>
      <h3 class="sub-h3">பொருத்தமான இணைப்புகள்</h3>
      <table class="pa-tbl">
        <thead>
          <tr>
            <th style="width:18%;">மணமகனின்<br/>கிரகம்</th>
            <th style="width:18%;">மணமகளின்<br/>கிரகம்</th>
            <th style="width:64%;">விளக்கம்</th>
          </tr>
        </thead>
        <tbody>{harm_html}</tbody>
      </table>

      <h3 class="sub-h3">பொருத்தமற்ற சேர்க்கைகள்</h3>
      <table class="pa-tbl">
        <thead>
          <tr>
            <th style="width:18%;">மணமகனின்<br/>கிரகம்</th>
            <th style="width:18%;">மணமகளின்<br/>கிரகம்</th>
            <th style="width:64%;">விளக்கம்</th>
          </tr>
        </thead>
        <tbody>{incomp_html}</tbody>
      </table>

      <h2 class="sec-h2">முனிவரின் வாக்கு</h2>
      <p class="sage-text">{_esc(vm["sage_verdict_ta"])}</p>
    </section>

    <!-- PAGE 6 -->
    <section class="print-page page6-stack">
      <div class="p6-hdr-row">
        <h2 class="sec-h2" style="margin:0;">அஷ்டகூட (36) &amp; கூடுதல் பொருத்த ஆய்வுகள்</h2>
        <span class="{ash_badge_cls}">{_esc(ash_badge_txt)}</span>
      </div>

      <table class="ash-tbl">
        <thead>
          <tr>
            <th>கூடம் (Koota)</th>
            <th>விளக்கம் &amp; விலக்கு</th>
            <th class="center">மதிப்பெண்</th>
            <th class="center">நிலை</th>
          </tr>
        </thead>
        <tbody>
          {ash_rows_html}
        </tbody>
      </table>

      <div class="cards-2col">
        <div class="info-card">
          <div class="card-title">தென் இந்திய பாபசாம்யம் (Papasamya)</div>
          <div class="card-row">மணமகன் பாபம்: <b>{_esc(papa["groom_total"])}</b> | மணமகள் பாபம்: <b>{_esc(papa["bride_total"])}</b></div>
          <div class="card-sub">மணமகன்: {_esc(papa["groom_frames"])}</div>
          <div class="card-sub">மணமகள்: {_esc(papa["bride_frames"])}</div>
          <div class="card-foot">வித்தியாசம்: <b>{_esc(papa["diff_str"])}</b> | தீர்ப்பு: <span class="{papa_tone_cls}">{_esc(papa["verdict_ta"])}</span><br/>{_esc(papa["explanation_ta"])}</div>
        </div>
        <div class="info-card">
          <div class="card-title">கே.பி (KP) 7-ஆம் உப அதிபதி &amp; ஆளுமை கிரகங்கள்</div>
          {kp_body_html}
        </div>
      </div>

      <div class="sp-panel">
        <div class="card-title" style="margin-bottom:5px;">கோட்சார குரு பலம், நாடி &amp; நவாம்ச சிறப்பு ஆய்வு</div>
        <div class="sp-line"><b>கோட்சார குரு பலம்:</b> {_esc(guru["label_ta"])}{f' — {_esc(guru["description_ta"])}' if guru["description_ta"] else ''}</div>
        {f'<div class="sp-line"><b>நாடிப் பொருத்தம் &amp; நந்தியோகம்:</b> {_esc(nadi_y["verdict_ta"])}</div>{nadi_obs_html}' if nadi_y["available"] else ''}
        {inlaws_html}
        <div class="sp-line"><b>நவாம்ச (D9) நிலை:</b> {_esc(nav["groom_ta"])} | {_esc(nav["bride_ta"])}</div>
        {nav_warn_html}
      </div>

      <div class="rem-box">
        <div class="rem-title">முதன்மை பரிகார ஸ்தலம் &amp; வழிகாட்டுதல்</div>
        <div class="rem-text"><b>{_esc(rem["temple_name_ta"])}</b> — {_esc(rem["temple_sig_ta"])}{f' | <b>பரிந்துரைக்கப்படும் பாராயணம்:</b> {_esc(rem["hymn_title_ta"])}' if rem["hymn_title_ta"] else ''}</div>
      </div>

      <p class="disc-note">குறிப்பு: இந்த அறிக்கை பாரம்பரிய தமிழ் பொருத்தம், 36 அஷ்டகூடம், பாபசாம்யம், வேத மற்றும் கே.பி. (KP) ஜோதிட விதிகளின் அடிப்படையில் தயாரிக்கப்பட்டது; இறுதி திருமண முடிவிற்கு குடும்ப ஆலோசனையும் சுப முகூர்த்த தேர்வும் பரிந்துரைக்கப்படுகிறது.</p>
    </section>
  </div>
</body>
</html>"""


def generate_marriage_compatibility_pdf_bytes(data: Dict[str, Any], language: str = "en") -> bytes:
    """Compiles the 5-page print-aligned Marriage Compatibility PDF via Playwright or ReportLab."""
    lang = "ta" if str(language).lower() in ("ta", "tamil") else "en"
    html_doc = generate_html_report(data, lang=lang)

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
