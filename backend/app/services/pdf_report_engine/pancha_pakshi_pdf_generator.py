"""Agastya Pancha Pakshi 24-Hour Bio-Rhythm Chart PDF Generator.

Produces a classical Tamil Siddha predictive dossier detailing the native's
Janma Pakshi (Vulture, Owl, Crow, Cock, Peacock), 5 elements, ruling graha,
the 50 day/night Antara intervals, Golden Victory Windows, and Padupakshi Warning Windows.
Supports bilingual Tamil and English rendering with NotoSansTamil fonts.
Designed for 100% pixel-perfect printable professional copy across exactly 2 balanced pages.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfgen import canvas

from app.services.pdf_report_engine.fonts import (
    Paragraph,
    reorder_tamil_for_pdf,
    register_report_fonts,
    GOLD_PRIMARY,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    CRIMSON_ACCENT,
    BORDER_COLOR,
)
from app.services.pancha_pakshi.calculator import calculate_pancha_pakshi_bio_rhythms
from app.schemas.pdf_report import PanchaPakshiPdfReportRequest

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 32.0
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 531.27 pt

NAKSHATRA_NAMES = [
    "ashwini", "bharani", "krittika", "rohini", "mrigashira", "ardra",
    "punarvasu", "pushya", "ashlesha", "magha", "purva phalguni", "uttara phalguni",
    "hasta", "chitra", "swati", "vishakha", "anuradha", "jyeshtha",
    "mula", "purva ashadha", "uttara ashadha", "shravana", "dhanishta",
    "shatabhisha", "purva bhadrapada", "uttara bhadrapada", "revati"
]

TAMIL_NAKSHATRA_NAMES = [
    "அசுவினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை",
    "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்",
    "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
]

ENGLISH_NAKSHATRAS_CAPITALIZED = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

ACTIVITY_NAMES_TA = {
    "ruling": "அரசு",
    "eating": "ஊண்",
    "walking": "நடை",
    "sleeping": "துயில்",
    "dying": "சாவு",
}

ACTIVITY_NAMES_EN = {
    "ruling": "Ruling (Arasu)",
    "eating": "Eating (Oon)",
    "walking": "Walking (Nadai)",
    "sleeping": "Sleeping (Thuyil)",
    "dying": "Dying (Saavu)",
}


def resolve_nakshatra_index(nak_input: Any) -> int:
    """Map nakshatra name or number to 1-27 index."""
    if isinstance(nak_input, int):
        return max(1, min(27, nak_input))
    if isinstance(nak_input, str):
        cleaned = nak_input.strip().lower()
        if cleaned.isdigit():
            return max(1, min(27, int(cleaned)))
        for idx, name in enumerate(NAKSHATRA_NAMES):
            if name in cleaned or cleaned in name:
                return idx + 1
        for idx, name in enumerate(TAMIL_NAKSHATRA_NAMES):
            if name in cleaned:
                return idx + 1
    return 1


def format_time_hm(time_str: str) -> str:
    """Safely extracts HH:MM from HH:MM:SS format."""
    if not time_str:
        return "--:--"
    parts = time_str.strip().split(":")
    if len(parts) >= 2:
        return f"{parts[0]:0>2}:{parts[1]:0>2}"
    return time_str[:5]


def format_window_hm(start_str: str, end_str: str) -> str:
    """Takes start and end times and returns a clean, compact 'HH:MM - HH:MM' string."""
    return f"{format_time_hm(start_str)} - {format_time_hm(end_str)}"


def get_guidance_and_color(power: int, is_ta_lang: bool) -> Tuple[str, str]:
    """Returns (guidance_verdict, text_color_hex)."""
    if power >= 80:
        return ("வெற்றி சுப நேரம்" if is_ta_lang else "Golden Victory"), "#15803D"
    elif power >= 50:
        return ("நலன் பயக்கும்" if is_ta_lang else "Favorable"), "#1E40AF"
    elif power >= 30:
        return ("நடுத்தரம்" if is_ta_lang else "Routine"), "#475569"
    else:
        return ("எச்சரிக்கை / தவிர்" if is_ta_lang else "Critical Caution"), "#DC2626"


def get_power_color(power: int) -> str:
    """Returns color hex string based on vitality percentage."""
    if power >= 80:
        return "#15803D"
    elif power >= 50:
        return "#1E40AF"
    elif power >= 30:
        return "#475569"
    else:
        return "#DC2626"


class PanchaPakshiNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()

        # Outer decorative frame (Classic Vedic double-border)
        self.setStrokeColor(GOLD_PRIMARY)
        self.setLineWidth(1.0)
        self.rect(MARGIN - 12, 16, PAGE_WIDTH - 2 * (MARGIN - 12), PAGE_HEIGHT - 32)

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.rect(MARGIN - 9, 19, PAGE_WIDTH - 2 * (MARGIN - 9), PAGE_HEIGHT - 38)

        # Running header on Page 2+
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 7.5)
            except Exception:
                self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(GOLD_PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 24, reorder_tamil_for_pdf("Gokul's Astrological Insights | அகத்தியர் பஞ்ச பட்சி சாஸ்திரம்"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 24, "24-Hour Bio-Rhythm Dossier")

            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 27, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 27)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(MARGIN, 28, PAGE_WIDTH - MARGIN, 28)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 18, reorder_tamil_for_pdf("© Gokul's Astrological Insights • Classical Agastya Pancha Pakshi Shastra • Clean-Room Calculations"))

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, page_str)
        self.restoreState()


def generate_pancha_pakshi_pdf_bytes(
    req: PanchaPakshiPdfReportRequest,
) -> bytes:
    """Calculates the 24-hour bio-rhythm intervals and compiles an executive printable PDF dossier."""
    font_name, font_bold = register_report_fonts()
    is_ta = req.language == "ta"

    t_date = date.fromisoformat(req.target_date)
    nak_idx = resolve_nakshatra_index(req.nakshatra)

    res = calculate_pancha_pakshi_bio_rhythms(
        target_date=t_date,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone_str="Asia/Kolkata",
        birth_nakshatra_idx=nak_idx,
        birth_paksha=req.paksha,
    )

    bird = res.get("birth_bird", {})
    astro = res.get("astronomical", {})
    weekday_str = t_date.strftime("%A")
    sunrise_local = astro.get("sunrise_local", "06:00")
    sunset_local = astro.get("sunset_local", "18:00")

    bird_name_en = bird.get("name_en", "Vulture")
    bird_name_ta = bird.get("name_ta", "வல்லூறு")
    element_en = bird.get("element_en", "Ether")
    element_ta = bird.get("element_ta", "ஆகாயம்")
    ruling_planet = bird.get("ruling_planet", "Jupiter")
    ruling_planet_ta = bird.get("ruling_planet_ta", "குரு")
    direction = bird.get("lucky_direction_ta" if is_ta else "lucky_direction", "North")
    color = bird.get("lucky_color_ta" if is_ta else "lucky_color", "Golden Yellow")

    # Custom Paragraph Styles for Precise Alignment
    brand_title = ParagraphStyle(
        "PPBrandTitle",
        fontName=font_bold,
        fontSize=12.5,
        leading=15,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
    )
    doc_title_style = ParagraphStyle(
        "PPDocTitle",
        fontName=font_bold,
        fontSize=11,
        leading=13.5,
        textColor=GOLD_PRIMARY,
        alignment=1, # Center
        spaceAfter=1,
    )
    doc_sub_style = ParagraphStyle(
        "PPDocSub",
        fontName=font_name,
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#475569"),
        alignment=1, # Center
        spaceAfter=4,
    )
    section_head_style = ParagraphStyle(
        "PPSectionHead",
        fontName=font_bold,
        fontSize=8.2,
        leading=10.2,
        textColor=NAVY_PRIMARY,
        spaceBefore=2,
        spaceAfter=2,
    )

    # Table cell styles
    th_white_center = ParagraphStyle(
        "PPTHWhiteCenter",
        fontName=font_bold,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1, # Center
    )
    th_white_left = ParagraphStyle(
        "PPTHWhiteLeft",
        fontName=font_bold,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0, # Left
    )
    cell_center = ParagraphStyle(
        "PPCellCenter",
        fontName=font_name,
        fontSize=7.2,
        leading=9.2,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
    )
    cell_bold_center = ParagraphStyle(
        "PPCellBoldCenter",
        fontName=font_bold,
        fontSize=7.2,
        leading=9.2,
        textColor=NAVY_PRIMARY,
        alignment=1, # Center
    )
    cell_left = ParagraphStyle(
        "PPCellLeft",
        fontName=font_name,
        fontSize=7.0,
        leading=9.0,
        textColor=NAVY_PRIMARY,
        alignment=0, # Left
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=30,
        bottomMargin=30,
    )
    story: List[Any] = []

    # --------------------------------------------------------------------------
    # PAGE 1: BRAND HEADER, BIO-RHYTHM IDENTITY & DAYTIME SCHEDULE
    # --------------------------------------------------------------------------
    doc_title = "அகத்தியர் பஞ்ச பட்சி 24 மணி நேர அட்டவணை" if is_ta else "AGASTYA PANCHA PAKSHI 24-HOUR BIO-RHYTHM REPORT"
    doc_sub = (
        "தமிழ் சித்தர்களின் பஞ்ச பட்சி சாஸ்திரப்படி நாள் முழுமைக்குமான உத்தம மற்றும் எச்சரிக்கை அந்தர காலங்கள்"
        if is_ta
        else "Classical Siddha Bio-Rhythms for Action & Auspicious Timing (Ruling, Eating, Walking, Sleeping, Dying)"
    )

    story.append(Paragraph("<b>GOKUL'S ASTROLOGICAL INSIGHTS</b>", brand_title))
    story.append(Paragraph(f"<b>{doc_title}</b>", doc_title_style))
    story.append(Paragraph(doc_sub, doc_sub_style))

    # Decorative Divider Line
    divider_table = Table([[""]], colWidths=[USABLE_WIDTH], rowHeights=[2])
    divider_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.0, GOLD_PRIMARY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider_table)
    story.append(Spacer(1, 4))

    # Native & Janma Pakshi Summary Table (Balanced 2-column card)
    paksha_label = ("வளர்பிறை (சுக்ல)" if is_ta else "Shukla (Waxing)") if "shukla" in req.paksha.lower() else ("தேய்பிறை (கிருஷ்ண)" if is_ta else "Krishna (Waning)")
    nak_name_clean = TAMIL_NAKSHATRA_NAMES[nak_idx - 1] if is_ta else ENGLISH_NAKSHATRAS_CAPITALIZED[nak_idx - 1]
    nak_display = f"{nak_name_clean} (#{nak_idx})"
    bird_display = f"{bird_name_ta} ({bird_name_en})" if is_ta else f"{bird_name_en} ({bird_name_ta})"
    element_display = f"{element_ta} ({element_en})" if is_ta else f"{element_en} ({element_ta})"
    ruling_planet_display = ruling_planet_ta if is_ta else f"{ruling_planet} ({ruling_planet_ta})"
    loc_display = req.location_name or f"Coordinates: {req.latitude:.2f}°, {req.longitude:.2f}°"

    native_data = [
        [
            Paragraph(f"<b>{'ஜாதகர் பெயர்' if is_ta else 'Native Name'}:</b> {req.native_name}", cell_left),
            Paragraph(f"<b>{'கணித்த நாள்' if is_ta else 'Target Date'}:</b> {req.target_date} ({weekday_str})", cell_left),
        ],
        [
            Paragraph(f"<b>{'ஜென்ம நட்சத்திரம்' if is_ta else 'Janma Star'}:</b> {nak_display}", cell_left),
            Paragraph(f"<b>{'பிறந்த பட்சம்' if is_ta else 'Birth Paksha'}:</b> {paksha_label}", cell_left),
        ],
        [
            Paragraph(f"<b>{'ஜென்ம பட்சி' if is_ta else 'Janma Bird'}:</b> <font color='{CRIMSON_ACCENT.hexval()}'><b>{bird_display}</b></font>", cell_left),
            Paragraph(f"<b>{'பூதம் (தத்துவம்)' if is_ta else 'Element (Tattva)'}:</b> {element_display}", cell_left),
        ],
        [
            Paragraph(f"<b>{'ஆட்சி கிரகம்' if is_ta else 'Ruling Graha'}:</b> {ruling_planet_display}", cell_left),
            Paragraph(f"<b>{'சுப திசை & நிறம்' if is_ta else 'Lucky Direction & Color'}:</b> {direction} | {color}", cell_left),
        ],
        [
            Paragraph(f"<b>{'சூரிய உதயம் / அஸ்தமனம்' if is_ta else 'Sunrise / Sunset'}:</b> {sunrise_local} - {sunset_local}", cell_left),
            Paragraph(f"<b>{'கணிப்பு இடம்' if is_ta else 'Location'}:</b> {loc_display}", cell_left),
        ],
    ]
    t_native = Table(native_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_native.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_native)
    story.append(Spacer(1, 5))

    # Golden Windows & Padupakshi Highlights Box
    golden_windows = res.get("golden_windows", [])
    padupakshi_windows = res.get("padupakshi_windows", [])

    gold_items = []
    for w in golden_windows[:3]:
        t_span = format_window_hm(w['start_time_local'], w['end_time_local'])
        m_id = w.get("major_activity_id", "")
        s_id = w.get("sub_activity_id", "")
        m_name = (ACTIVITY_NAMES_TA.get(m_id) if is_ta else ACTIVITY_NAMES_EN.get(m_id, m_id)) or w.get('major_activity_ta' if is_ta else 'major_activity_en', '')
        s_name = (ACTIVITY_NAMES_TA.get(s_id) if is_ta else ACTIVITY_NAMES_EN.get(s_id, s_id)) or w.get('sub_activity_ta' if is_ta else 'sub_activity_en', '')
        p_val = w.get("power_score", 100)
        gold_items.append(f"• <b>{t_span}</b>: {m_name} &gt; {s_name} [{p_val}%]")
    gold_str = "<br/>".join(gold_items) if gold_items else ("இன்று தனிப்பட்ட பொன் நேரங்கள் இல்லை" if is_ta else "No golden victory windows on this date")

    padu_items = []
    for w in padupakshi_windows[:3]:
        t_span = format_window_hm(w['start_time_local'], w['end_time_local'])
        m_id = w.get("major_activity_id", "")
        s_id = w.get("sub_activity_id", "")
        m_name = (ACTIVITY_NAMES_TA.get(m_id) if is_ta else ACTIVITY_NAMES_EN.get(m_id, m_id)) or w.get('major_activity_ta' if is_ta else 'major_activity_en', '')
        s_name = (ACTIVITY_NAMES_TA.get(s_id) if is_ta else ACTIVITY_NAMES_EN.get(s_id, s_id)) or w.get('sub_activity_ta' if is_ta else 'sub_activity_en', '')
        p_val = w.get("power_score", 0)
        padu_items.append(f"• <b>{t_span}</b>: {m_name} &gt; {s_name} [{p_val}%]")
    padu_str = "<br/>".join(padu_items) if padu_items else ("இன்று படுபட்சி எச்சரிக்கை நேரங்கள் இல்லை" if is_ta else "No padupakshi caution windows on this date")

    win_head_left = "சுப பொன் நேரங்கள் (வெற்றி சுப காலம்: 80% - 100%)" if is_ta else "Golden Victory Windows (Peak Vitality: 80% - 100%)"
    win_head_right = "படுபட்சி எச்சரிக்கை நேரங்கள் (முக்கிய காரியம் தவிர்க்க: 0% - 25%)" if is_ta else "Padupakshi Caution Windows (Critical Caution: 0% - 25%)"

    windows_table_data = [
        [
            Paragraph(f"<b>{win_head_left}</b>", th_white_left),
            Paragraph(f"<b>{win_head_right}</b>", th_white_left),
        ],
        [
            Paragraph(gold_str, cell_left),
            Paragraph(padu_str, cell_left),
        ],
    ]
    t_windows = Table(windows_table_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_windows.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#15803D")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#991B1B")),
        ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#F0FDF4")),
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_windows)
    story.append(Spacer(1, 4))

    # Daytime 25 Antara Table (Sunrise to Sunset)
    day_sec_title = (
        "பகல் கால அந்தர அட்டவணை (Daytime Schedule - 25 Sub-periods: சூரிய உதயம் முதல் அஸ்தமனம் வரை)"
        if is_ta
        else "DAYTIME BIO-RHYTHM SCHEDULE (Sunrise to Sunset - 25 Sub-periods)"
    )
    story.append(Paragraph(f"<b>{day_sec_title}</b>", section_head_style))
    story.append(Spacer(1, 1))

    # Table Column Widths: Exactly 531.27 pt (USABLE_WIDTH)
    # [Time: 110pt, Major: 100pt, Sub: 100pt, Power: 75pt, Guidance: 146.27pt]
    col_w = [110.0, 100.0, 100.0, 75.0, 146.27]

    day_antara_head = [
        Paragraph(f"<b>{'நேரம்' if is_ta else 'Time Window'}</b>", th_white_center),
        Paragraph(f"<b>{'முதன்மை தொழில்' if is_ta else 'Major Phase'}</b>", th_white_center),
        Paragraph(f"<b>{'அந்தர செயல்' if is_ta else 'Antara Sub-Period'}</b>", th_white_center),
        Paragraph(f"<b>{'ஆற்றல் %' if is_ta else 'Vitality %'}</b>", th_white_center),
        Paragraph(f"<b>{'பலன் & வழிகாட்டல்' if is_ta else 'Action Guidance'}</b>", th_white_center),
    ]
    day_rows = [day_antara_head]
    all_antaras = res.get("all_antaras", [])
    day_antaras = all_antaras[:25]
    night_antaras = all_antaras[25:]

    for slot in day_antaras:
        p_score = slot.get("power_score", 50)
        t_win = format_window_hm(slot['start_time_local'], slot['end_time_local'])
        m_id = slot.get("major_activity_id", "")
        s_id = slot.get("sub_activity_id", "")

        m_act = (ACTIVITY_NAMES_TA.get(m_id) if is_ta else ACTIVITY_NAMES_EN.get(m_id, m_id)) or slot.get("major_activity_ta" if is_ta else "major_activity_en", "")
        s_act = (ACTIVITY_NAMES_TA.get(s_id) if is_ta else ACTIVITY_NAMES_EN.get(s_id, s_id)) or slot.get("sub_activity_ta" if is_ta else "sub_activity_en", "")

        guidance, g_col = get_guidance_and_color(p_score, is_ta)
        p_col = get_power_color(p_score)

        day_rows.append([
            Paragraph(f"<b>{t_win}</b>", cell_bold_center),
            Paragraph(m_act, cell_center),
            Paragraph(f"<b>{s_act}</b>", cell_center),
            Paragraph(f"<font color='{p_col}'><b>{p_score}%</b></font>", cell_bold_center),
            Paragraph(f"<font color='{g_col}'><b>{guidance}</b></font>", cell_center),
        ])

    t_day = Table(day_rows, colWidths=col_w)
    t_day.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_day)

    # --------------------------------------------------------------------------
    # PAGE 2: NIGHTTIME SCHEDULE (Sunset to Next Sunrise) & AGASTYA SIDDHA LORE
    # --------------------------------------------------------------------------
    story.append(PageBreak())

    night_sec_title = (
        "இரவு கால அந்தர அட்டவணை (Nighttime Schedule - 25 Sub-periods: சூரிய அஸ்தமனம் முதல் மறுநாள் உதயம் வரை)"
        if is_ta
        else "NIGHTTIME BIO-RHYTHM SCHEDULE (Sunset to Next Sunrise - 25 Sub-periods)"
    )
    story.append(Paragraph(f"<b>{night_sec_title}</b>", section_head_style))
    story.append(Spacer(1, 2))

    night_antara_head = [
        Paragraph(f"<b>{'நேரம்' if is_ta else 'Time Window'}</b>", th_white_center),
        Paragraph(f"<b>{'முதன்மை தொழில்' if is_ta else 'Major Phase'}</b>", th_white_center),
        Paragraph(f"<b>{'அந்தர செயல்' if is_ta else 'Antara Sub-Period'}</b>", th_white_center),
        Paragraph(f"<b>{'ஆற்றல் %' if is_ta else 'Vitality %'}</b>", th_white_center),
        Paragraph(f"<b>{'பலன் & வழிகாட்டல்' if is_ta else 'Action Guidance'}</b>", th_white_center),
    ]
    night_rows = [night_antara_head]
    for slot in night_antaras:
        p_score = slot.get("power_score", 50)
        t_win = format_window_hm(slot['start_time_local'], slot['end_time_local'])
        m_id = slot.get("major_activity_id", "")
        s_id = slot.get("sub_activity_id", "")

        m_act = (ACTIVITY_NAMES_TA.get(m_id) if is_ta else ACTIVITY_NAMES_EN.get(m_id, m_id)) or slot.get("major_activity_ta" if is_ta else "major_activity_en", "")
        s_act = (ACTIVITY_NAMES_TA.get(s_id) if is_ta else ACTIVITY_NAMES_EN.get(s_id, s_id)) or slot.get("sub_activity_ta" if is_ta else "sub_activity_en", "")

        guidance, g_col = get_guidance_and_color(p_score, is_ta)
        p_col = get_power_color(p_score)

        night_rows.append([
            Paragraph(f"<b>{t_win}</b>", cell_bold_center),
            Paragraph(m_act, cell_center),
            Paragraph(f"<b>{s_act}</b>", cell_center),
            Paragraph(f"<font color='{p_col}'><b>{p_score}%</b></font>", cell_bold_center),
            Paragraph(f"<font color='{g_col}'><b>{guidance}</b></font>", cell_center),
        ])

    t_night = Table(night_rows, colWidths=col_w)
    t_night.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_night)
    story.append(Spacer(1, 8))

    # Agastya Siddha Lore & Practical Action Guide
    lore_text = (
        "<b>அகத்தியர் சித்த பஞ்ச பட்சி சாஸ்திர செயல் வழிகாட்டி (Agastya Siddha Practical Guide):</b><br/>"
        "1. <b>அரசு (Ruling - 100% உச்ச சக்தி):</b> புதிய ஒப்பந்தங்கள், அரசு காரியங்கள், முக்கிய முதலீடுகள், பதவி ஏற்பு, பத்திரப்பதிவு மற்றும் சுப முயற்சிகளுக்கு நிகரற்ற வெற்றி தரும் நேரம்.<br/>"
        "2. <b>ஊண் (Eating - 80% பலமான நிலை):</b> பணப் பரிவர்த்தனைகள், சுப பேச்சுவார்த்தைகள், புதுமனை புகுதல், ஆடை ஆபரணம் வாங்குதல் மற்றும் மருத்துவம் தொடங்க உகந்தது.<br/>"
        "3. <b>நடை (Walking - 50% நடுத்தர இயக்கம்):</b> அன்றாட வியாபாரம், களப்பணிகள், பயணங்கள் தொடங்குதல், விளையாட்டு மற்றும் வழக்கமான பணிகளுக்கு சிறந்தது.<br/>"
        "4. <b>துயில் (Sleeping - 20% ஓய்வு நிலை):</b> மன அமைதி, தியானம், இறை வழிபாடு மற்றும் ஓய்வெடுக்க உகந்தது; முக்கிய வர்த்தக முடிவுகளை தவிர்க்கவும்.<br/>"
        "5. <b>சாவு / படுபட்சி (Dying - 0% அபாய எச்சரிக்கை):</b> படுபட்சி காலத்தில் புதிய முயற்சிகள், கடன் கொடுத்தல்/வாங்குதல், அறுவை சிகிச்சை, பிரயாணம் மற்றும் வாக்குவாதங்களை முற்றிலும் தவிர்க்க வேண்டும்."
    ) if is_ta else (
        "<b>Agastya Siddha Pancha Pakshi Shastra Strategic Action Principles:</b><br/>"
        "1. <b>Ruling (Arasu - 100% Peak Authority):</b> Supreme vital immunity. Supreme for contracts, inaugurations, promotions, asset registration, and entering office.<br/>"
        "2. <b>Eating (Oon - 80% High Vitality):</b> Nourishing and productive state. Ideal for financial transactions, matrimonial alliance talks, journeys, and healing cures.<br/>"
        "3. <b>Walking (Nadai - 50% Dynamic Motion):</b> Active mobility. Good for routine commerce, sports, marketing, commuting, and standard communications.<br/>"
        "4. <b>Sleeping (Thuyil - 20% Low Energy / Rest):</b> Dormant phase. Best for contemplation, spiritual prayer, study, and resting. Postpone major corporate launches.<br/>"
        "5. <b>Dying (Saavu / Padupakshi - 0% Critical Caution):</b> Zero vital immunity. Do NOT initiate surgery, litigation, loans, contracts, or hostile confrontation."
    )
    t_lore = Table([[Paragraph(lore_text, cell_left)]], colWidths=[USABLE_WIDTH])
    t_lore.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
        ('BOX', (0, 0), (-1, -1), 0.5, GOLD_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_lore)

    doc.build(story, canvasmaker=PanchaPakshiNumberedCanvas)
    return buffer.getvalue()
