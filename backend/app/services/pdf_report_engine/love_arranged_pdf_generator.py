"""Love vs Arranged Marriage Astrological Report PDF Generator.

Produces an executive, publication-grade matrimonial pathway report detailing:
1. Definitive Verdict (Love, Arranged, or Love-cum-Arranged with Family Blessings)
2. Probability Percentage Distribution Meter
3. The Origin & Direction of Spouse (2 to 3 concise points on how the bride/groom arrives)
4. Who Will Be Their Life Partner (nature, physical stature, and career background)
5. When Love Started / Courtship Genesis Period (age range, calendar years, and triggering dasha)
6. Key Astrological Deciding Factors and Cuspal Sub-Lord planetary positions.

Supports bilingual Tamil and English rendering with NotoSansTamil fonts and official GAI letterhead.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from app.schemas.love_marriage import LoveOrArrangedResponse
from app.services.pdf_report_engine.fonts import (
    Paragraph,
    reorder_tamil_for_pdf,
    register_report_fonts,
    GOLD_PRIMARY,
    GOLD_ACCENT,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    CRIMSON_ACCENT,
    BORDER_COLOR,
)
from app.services.pdf_report_engine.letterhead_renderer import (
    make_letterhead_canvas_class,
    PAGE_SIZE,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    LEFT_MARGIN,
    RIGHT_MARGIN,
    USABLE_WIDTH,
)

PLANET_NAMES_TA = {
    "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்",
    "Mercury": "புதன்", "Jupiter": "குரு", "Venus": "சுக்கிரன்",
    "Saturn": "சனி", "Rahu": "ராகு", "Ketu": "கேது",
}


def generate_love_arranged_pdf_bytes(
    report_data: LoveOrArrangedResponse,
    language: str = "en",
) -> bytes:
    """Compiles a professional executive Love vs Arranged Marriage PDF report."""
    font_name, font_bold = register_report_fonts()
    is_ta = (language == "ta")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=PAGE_SIZE,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    story: List[Any] = []

    # =========================================================================
    # Typography Styles - Calibrated for Zero Overlaps & Pixel-Perfect Line Heights
    # =========================================================================
    report_title_style = ParagraphStyle(
        "LAReportTitle",
        fontName=font_bold,
        fontSize=12.5,
        leading=15,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
        spaceAfter=2,
    )
    report_sub_style = ParagraphStyle(
        "LAReportSub",
        fontName=font_name,
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=4,
    )
    section_head_style = ParagraphStyle(
        "LASectionHead",
        fontName=font_bold,
        fontSize=9,
        leading=11.5,
        textColor=NAVY_PRIMARY,
        spaceBefore=2,
        spaceAfter=2,
    )
    cell_val_style = ParagraphStyle(
        "LACellVal",
        fontName=font_name,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )
    body_style = ParagraphStyle(
        "LABody",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#334155"),
    )
    bullet_style = ParagraphStyle(
        "LABullet",
        fontName=font_name,
        fontSize=7.3,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )
    table_cell_style = ParagraphStyle(
        "LATableCell",
        fontName=font_name,
        fontSize=7,
        leading=9.2,
        textColor=colors.HexColor("#1E293B"),
    )
    table_cell_bold = ParagraphStyle(
        "LATableCellBold",
        fontName=font_bold,
        fontSize=7,
        leading=9.2,
        textColor=NAVY_PRIMARY,
    )

    # 1. Header Titles
    header_title = (
        "காதல் அல்லது நிச்சயிக்கப்பட்ட திருமண அறிக்கை"
        if is_ta
        else "Love vs. Arranged Marriage Predictor Report"
    )
    header_sub = (
        "வேத சாஸ்திரம் மற்றும் கே.பி உப-அதிபதி விதிகளின்படி திருமண வகை & வாழ்க்கைத் துணைவர் கணிப்பு"
        if is_ta
        else "Vedic Astrology & KP Cuspal Sub-Lord Matrimonial Pathway & Life Partner Analysis"
    )
    story.append(Paragraph(header_title, report_title_style))
    story.append(Paragraph(header_sub, report_sub_style))
    story.append(Spacer(1, 3))

    # 2. Native Metadata Grid
    meta_name_lbl = "ஜாதகர் பெயர்:" if is_ta else "Native Name:"
    meta_gender_lbl = "பாலினம்:" if is_ta else "Gender:"
    meta_birth_lbl = "பிறந்த விவரங்கள்:" if is_ta else "Birth Details:"
    meta_date_lbl = "கணிக்கப்பட்ட தேதி:" if is_ta else "Evaluation Date:"

    gender_display = (
        ("ஆண் (Male)" if report_data.native_gender == "male" else "பெண் (Female)")
        if is_ta
        else report_data.native_gender.title()
    )

    eval_date_str = datetime.now().strftime("%d %b %Y, %I:%M %p")

    meta_table_data = [
        [
            Paragraph(f"<b>{meta_name_lbl}</b> {report_data.native_name or 'Native'}", cell_val_style),
            Paragraph(f"<b>{meta_gender_lbl}</b> {gender_display}", cell_val_style),
        ],
        [
            Paragraph(f"<b>{meta_birth_lbl}</b> {report_data.birth_summary}", cell_val_style),
            Paragraph(f"<b>{meta_date_lbl}</b> {eval_date_str}", cell_val_style),
        ],
    ]
    t_meta = Table(meta_table_data, colWidths=[USABLE_WIDTH * 0.52, USABLE_WIDTH * 0.48])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 5))

    # 3. Grand Outcome Verdict Card (Structured Multiple Rows - Zero Overlap)
    badge_bg = "#FFF1F2" if report_data.verdict_badge == "LOVE" else "#FAF5FF" if report_data.verdict_badge == "LOVE_ARRANGED" else "#EFF6FF"
    badge_border = "#FDA4AF" if report_data.verdict_badge == "LOVE" else "#D8B4FE" if report_data.verdict_badge == "LOVE_ARRANGED" else "#93C5FD"
    badge_text_color = "#BE123C" if report_data.verdict_badge == "LOVE" else "#6B21A8" if report_data.verdict_badge == "LOVE_ARRANGED" else "#1D4ED8"

    verdict_title = report_data.verdict_ta if is_ta else report_data.verdict
    summary_text = report_data.summary_ta if is_ta else report_data.summary_en
    family_support_text = report_data.family_support_ta if is_ta else report_data.family_support

    v_kicker_style = ParagraphStyle(
        "VKicker",
        fontName=font_bold,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor(badge_text_color),
        alignment=1,
    )
    v_title_style = ParagraphStyle(
        "VTitle",
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=NAVY_PRIMARY,
        alignment=1,
    )
    v_desc_style = ParagraphStyle(
        "VDesc",
        fontName=font_name,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#334155"),
        alignment=1,
    )
    v_stat_style = ParagraphStyle(
        "VStat",
        fontName=font_bold,
        fontSize=7.8,
        leading=10,
        alignment=1,
    )
    v_fam_style = ParagraphStyle(
        "VFam",
        fontName=font_name,
        fontSize=7.3,
        leading=9.5,
        textColor=colors.HexColor("#047857"),
        alignment=1,
    )

    kicker_label = "• திருமண வகை தீர்ப்பு •" if is_ta else "• PRIMARY MARRIAGE OUTCOME VERDICT •"
    stats_html = (
        f"<font color='#BE123C'><b>{'காதல் வாய்ப்பு:' if is_ta else 'Love Probability:'} {report_data.love_percentage}%</b></font>"
        f" &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<font color='#1D4ED8'><b>{'நிச்சயிக்கப்பட்ட வாய்ப்பு:' if is_ta else 'Arranged Probability:'} {report_data.arranged_percentage}%</b></font>"
    )
    fam_html = f"<b>{'பெற்றோர் & குடும்பத்தார் ஆதரவு:' if is_ta else 'Parental & Family Blessing:'}</b> {family_support_text}"

    verdict_rows = [
        [Paragraph(kicker_label, v_kicker_style)],
        [Paragraph(verdict_title, v_title_style)],
        [Paragraph(summary_text, v_desc_style)],
        [Paragraph(stats_html, v_stat_style)],
        [Paragraph(fam_html, v_fam_style)],
    ]
    t_verdict = Table(verdict_rows, colWidths=[USABLE_WIDTH])
    t_verdict.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(badge_bg)),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor(badge_border)),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 1.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_verdict)
    story.append(Spacer(1, 5))

    # 4. In-Depth Section 1: Way Bride / Groom Comes From (2-3 Points)
    spouse_orig = report_data.spouse_origin
    if spouse_orig:
        origin_sec_title = (
            "1. வாழ்க்கைத் துணைவர் வரும் திசை & வழிமுறை (Arrival Pathway & Direction)"
            if is_ta
            else "1. Direction & Origin Pathway of Life Partner (2 to 3 Key Indicators)"
        )
        story.append(Paragraph(origin_sec_title, section_head_style))

        dir_lbl = "வரும் திசை:" if is_ta else "Arrival Direction:"
        dist_lbl = "தொலைவு வகை:" if is_ta else "Distance Category:"
        chan_lbl = "அறிமுக களம்:" if is_ta else "Meeting Channel:"

        dir_val = spouse_orig.direction_ta if is_ta else spouse_orig.direction_en
        dist_val = spouse_orig.distance_type_ta if is_ta else spouse_orig.distance_type_en
        chan_val = spouse_orig.source_channel_ta if is_ta else spouse_orig.source_channel_en

        pts = spouse_orig.points_ta if is_ta else spouse_orig.points_en
        bullet_html = "<br/>".join([f"• <b>{'குறிப்பு' if is_ta else 'Point'} {i+1}:</b> {pt}" for i, pt in enumerate(pts)])

        origin_box_html = f"""
        <b>{dir_lbl}</b> {dir_val} &nbsp;&nbsp;|&nbsp;&nbsp; <b>{dist_lbl}</b> {dist_val}<br/>
        <b>{chan_lbl}</b> {chan_val}<br/><br/>
        {bullet_html}
        """
        t_origin = Table([[Paragraph(origin_box_html, bullet_style)]], colWidths=[USABLE_WIDTH])
        t_origin.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
            ('BOX', (0, 0), (-1, -1), 0.6, GOLD_PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_origin)
        story.append(Spacer(1, 5))

    # 5. In-Depth Section 2: Who Will Be Their Life Partner (Non-Repetitive, Balanced)
    partner = report_data.life_partner
    if partner:
        partner_sec_title = (
            "2. வாழ்க்கைத் துணைவரின் அடையாளம் & குணநலன்கள் (Life Partner Astrological Identity)"
            if is_ta
            else "2. Who Will Be Their Life Partner (Personality, Appearance & Career)"
        )
        story.append(Paragraph(partner_sec_title, section_head_style))

        nature_lbl = "குணம் & சுபாவம்:" if is_ta else "Nature & Temperament:"
        features_lbl = "தோற்றம் & உடல்வாகு:" if is_ta else "Physical Appearance:"
        career_lbl = "தொழில் & கல்விப் பின்னணி:" if is_ta else "Career & Social Sphere:"

        nature_val = partner.nature_temperament_ta if is_ta else partner.nature_temperament_en
        features_val = partner.physical_features_ta if is_ta else partner.physical_features_en
        career_val = partner.career_background_ta if is_ta else partner.career_background_en
        summary_val = partner.summary_ta if is_ta else partner.summary_en

        partner_box_html = f"""
        • <b>{nature_lbl}</b> {nature_val}<br/>
        • <b>{features_lbl}</b> {features_val}<br/>
        • <b>{career_lbl}</b> {career_val}<br/><br/>
        <font color="#475569"><i>{summary_val}</i></font>
        """
        t_partner = Table([[Paragraph(partner_box_html, bullet_style)]], colWidths=[USABLE_WIDTH])
        t_partner.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_partner)

    # =========================================================================
    # BALANCED PAGE BREAK: Timing, Deciding Factors & Technical Data on Page 2
    # =========================================================================
    story.append(PageBreak())

    # 6. Page 2 Top: Courtship Genesis & When Love Started
    timing = report_data.love_timing
    if timing:
        timing_sec_title = (
            "3. காதல் / ஈர்ப்பு தொடங்கிய காலம் (When Love Was Started & Courtship Genesis)"
            if is_ta
            else "3. Courtship Genesis & When Love Started (Astrological Timing)"
        )
        story.append(Paragraph(timing_sec_title, section_head_style))

        age_lbl = "பருவ வயது:" if is_ta else "Estimated Age Range:"
        cal_lbl = "ஆண்டு காலம்:" if is_ta else "Calendar Window:"
        dasha_lbl = "காரக தசா-புத்தி:" if is_ta else "Triggering Dasha/Bhukti:"
        context_lbl = "சூழல் & களம்:" if is_ta else "Courtship Context:"

        dasha_val = timing.trigger_dasha_ta if is_ta else timing.trigger_dasha_en
        context_val = timing.context_ta if is_ta else timing.context_en

        timing_box_html = f"""
        <b>{age_lbl}</b> {timing.estimated_age_range} &nbsp;&nbsp;|&nbsp;&nbsp; <b>{cal_lbl}</b> {timing.approximate_period}<br/>
        <b>{dasha_lbl}</b> {dasha_val}<br/>
        <b>{context_lbl}</b> {context_val}
        """
        t_timing = Table([[Paragraph(timing_box_html, bullet_style)]], colWidths=[USABLE_WIDTH])
        t_timing.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FDF2F8")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#F472B6")),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_timing)
        story.append(Spacer(1, 6))

    # 7. Page 2: Primary Astrological Deciding Factors
    factors_sec_title = (
        "4. முக்கிய ஜோதிடக் காரணிகள் (Primary Astrological Deciding Factors)"
        if is_ta
        else "4. Primary Astrological Deciding Factors & Planetary Signatures"
    )
    story.append(Paragraph(factors_sec_title, section_head_style))

    # Factors Table with concise headers (never wrapping)
    th_category = "ஜோதிடப் பிரிவு" if is_ta else "Category"
    th_factor = "கிரக அமைப்பு & பலன்" if is_ta else "Astrological Factor"
    th_influence = "தாக்கம்" if is_ta else "Influence"
    th_weight = "பலம்" if is_ta else "Strength"

    factor_rows = [[
        Paragraph(f"<b>{th_category}</b>", table_cell_bold),
        Paragraph(f"<b>{th_factor}</b>", table_cell_bold),
        Paragraph(f"<b>{th_influence}</b>", table_cell_bold),
        Paragraph(f"<b>{th_weight}</b>", table_cell_bold),
    ]]

    for f in report_data.key_factors:
        title = f.title_ta if is_ta else f.title_en
        desc = f.description_ta if is_ta else f.description_en
        inf_txt = (
            "காதல்" if f.influence == "LOVE" else "மரபு/நிச்சயம்" if f.influence == "ARRANGED" else "நடுநிலை"
        ) if is_ta else (
            "Love" if f.influence == "LOVE" else "Arranged" if f.influence == "ARRANGED" else "Neutral"
        )
        inf_color = "#BE123C" if f.influence == "LOVE" else "#1D4ED8" if f.influence == "ARRANGED" else "#475569"

        factor_content = f"<b>{title}</b><br/><font size='6.5' color='#475569'>{desc}</font>"
        strength_str = f"<b>{f.weight} / 5</b>"

        factor_rows.append([
            Paragraph(f.category, table_cell_style),
            Paragraph(factor_content, table_cell_style),
            Paragraph(f"<font color='{inf_color}'><b>{inf_txt}</b></font>", table_cell_style),
            Paragraph(strength_str, table_cell_style),
        ])

    t_factors = Table(
        factor_rows,
        colWidths=[USABLE_WIDTH * 0.23, USABLE_WIDTH * 0.49, USABLE_WIDTH * 0.16, USABLE_WIDTH * 0.12],
    )
    t_factors.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
    ]))
    story.append(t_factors)
    story.append(Spacer(1, 6))

    # 8. Page 2: Technical Planetary Positions & Astrological References
    tech_sec_title = (
        "5. நுட்பமான கிரக அமைப்புகள் & கே.பி உப-அதிபதி விபரங்கள்"
        if is_ta
        else "5. Technical Planetary Positions & Cuspal Sub-Lord References"
    )
    story.append(Paragraph(tech_sec_title, section_head_style))

    tech_content = f"""
    • <b>{'5-ஆம் பாவம் (காதல்/ஈர்ப்பு):' if is_ta else '5th House (Courtship & Romance):'}</b> {report_data.fifth_house_summary}<br/>
    • <b>{'7-ஆம் பாவம் (களத்திரம்/திருமணம்):' if is_ta else '7th House (Matrimony & Partner):'}</b> {report_data.seventh_house_summary}<br/>
    • <b>{'சுக்கிரன் நிலை (காதல் காரகன்):' if is_ta else 'Venus Placement (Karaka of Love):'}</b> {report_data.venus_summary}<br/>
    """
    if report_data.kp_sublord_summary:
        tech_content += f"• <b>{'கே.பி உப-அதிபதி விதி:' if is_ta else 'KP Cuspal Sub-Lord Rule:'}</b> {report_data.kp_sublord_summary}<br/>"

    t_tech = Table([[Paragraph(tech_content, bullet_style)]], colWidths=[USABLE_WIDTH])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 6))

    # 9. Page 2 Bottom: Classical Astrological Notes & Disclaimer
    notes_title = "சாஸ்திரக் குறிப்பு & அங்கீகாரம் (Vedic Authenticity Notes)" if is_ta else "Vedic Authenticity & Advisory Notes"
    notes_body = (
        "இந்த திருமண வகை கணிப்பு பராசர முறை, கே.பி உப-அதிபதி விதி மற்றும் சித்தயோகி சிவதாசன் ரவி நாடி விதிகளின்படி "
        "ஜாதகரின் 5 மற்றும் 7-ஆம் பாவக தொடர்புகளை ஆராய்ந்து துல்லியமாக வழங்கப்பட்டுள்ளது. "
        "வாழ்க்கைத் துணைவர் திசை, குணாதிசயங்கள் மற்றும் காதல் மலர்ந்த காலம் ஆகியவை கிரக காரகத்துவங்கள் மற்றும் தசா-புக்தி அடிப்படையில் கணிக்கப்பட்டுள்ளன."
    ) if is_ta else (
        "This evaluation integrates Maharishi Parashara's classical 5th-7th lord sambandhas, Prof. K.S. Krishnamurti's Cuspal Sub-Lord (CSL) "
        "rules, and Siddhayogi Sivadasan Ravi Nadi aphorisms. The direction of the spouse, spousal personality, and courtship genesis period "
        "are synthesized from 7th house planetary rulers, karakas, and operating Vimshottari Dasha intervals."
    )
    t_notes = Table([[Paragraph(f"<b>{notes_title}:</b> {notes_body}", body_style)]], colWidths=[USABLE_WIDTH])
    t_notes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
        ('BOX', (0, 0), (-1, -1), 0.5, GOLD_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_notes)

    # Document Builder with Letterhead Canvas
    canvasmaker = make_letterhead_canvas_class(
        language=language,
        report_title="Gokul's Astrological Insights | Love vs. Arranged Marriage Predictor",
        draw_page_numbers=True,
    )
    doc.build(story, canvasmaker=canvasmaker)
    return buffer.getvalue()
