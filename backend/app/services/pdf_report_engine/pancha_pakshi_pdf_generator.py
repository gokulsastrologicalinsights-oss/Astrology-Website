"""Agastya Pancha Pakshi 24-Hour Bio-Rhythm Chart PDF Generator.

Produces a classical Tamil Siddha predictive dossier detailing the native's
Janma Pakshi (Vulture, Owl, Crow, Cock, Peacock), 5 elements, ruling graha,
the 50 day/night Antara intervals, Golden Victory Windows, and Padupakshi Warning Windows.
Supports bilingual Tamil and English rendering with NotoSansTamil fonts.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph as _RLParagraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.pdfgen import canvas

from app.services.pdf_report_engine.fonts import (
    get_report_styles,
    reorder_tamil_for_pdf,
    register_report_fonts,
    GOLD_PRIMARY,
    GOLD_ACCENT,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    CRIMSON_ACCENT,
    BG_HEADER,
    BG_ZEBRA,
    BORDER_COLOR,
    EMERALD_GREEN,
)
from app.services.pancha_pakshi.calculator import calculate_pancha_pakshi_bio_rhythms
from app.schemas.pdf_report import PanchaPakshiPdfReportRequest

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)

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


class Paragraph(_RLParagraph):
    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class PanchaPakshiNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 7.5)
            except Exception:
                self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(GOLD_PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 26, reorder_tamil_for_pdf("Gokul's Astrological Insights | அகத்தியர் பஞ்ச பட்சி சாஸ்திரம்"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "24-Hour Bio-Rhythm Dossier")

            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 30, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 30)

        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(MARGIN, 26, PAGE_WIDTH - MARGIN, 26)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 16, "© Gokul's Astrological Insights • Classical Agastya Pancha Pakshi Shastra • Clean-Room Calculations")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 16, page_str)
        self.restoreState()


def generate_pancha_pakshi_pdf_bytes(
    req: PanchaPakshiPdfReportRequest,
) -> bytes:
    """Calculates the 24-hour bio-rhythm intervals and compiles an executive PDF dossier."""
    register_report_fonts()
    styles = get_report_styles()
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

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=38,
        bottomMargin=36,
    )
    story: List[Any] = []

    # --------------------------------------------------------------------------
    # PAGE 1: EXECUTIVE BIO-RHYTHM PROFILE & DAYTIME SCHEDULE
    # --------------------------------------------------------------------------
    doc_title = "அகத்தியர் பஞ்ச பட்சி 24 மணி நேர அட்டவணை" if is_ta else "AGASTYA PANCHA PAKSHI 24-HOUR BIO-RHYTHM DOSSIER"
    doc_sub = "தமிழ் சித்தர்களின் பஞ்ச பட்சி சாஸ்திரப்படி நாள் முழுமைக்குமான வெற்றி மற்றும் எச்சரிக்கை நேரங்கள்" if is_ta else "Classical Tamil Predictive Bio-Rhythms for Strategic Timing (Ruling, Eating, Walking, Sleeping, Dying)"

    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>{doc_title}</b></font>", styles["DocTitle"]))
    story.append(Paragraph(f"<font color='{NAVY_SECONDARY.hexval()}'>{doc_sub}</font>", styles["Subtitle"]))
    story.append(Spacer(1, 8))

    # Native & Janma Pakshi Summary Table
    paksha_label = "வளர்பிறை (Shukla)" if "shukla" in req.paksha.lower() else "தேய்பிறை (Krishna)"
    native_data = [
        [
            Paragraph(f"<b>பெயர் / Native:</b> {req.native_name}", styles["NormalSmall"]),
            Paragraph(f"<b>கணித்த நாள் / Date:</b> {req.target_date} ({weekday_str})", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>ஜன்ம நட்சத்திரம் / Star:</b> {req.nakshatra}", styles["NormalSmall"]),
            Paragraph(f"<b>பக்ஷம் / Paksha:</b> {paksha_label}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>ஜன்ம பட்சி / Birth Bird:</b> <font color='{CRIMSON_ACCENT.hexval()}'><b>{bird_name_ta} ({bird_name_en})</b></font>", styles["NormalSmall"]),
            Paragraph(f"<b>பூதம் / Element:</b> {element_ta} ({element_en})", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>ஆட்சி கிரகம் / Ruling Graha:</b> {ruling_planet_ta if is_ta else ruling_planet}", styles["NormalSmall"]),
            Paragraph(f"<b>திசை & நிறம் / Direction & Color:</b> {direction} | {color}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>சூரிய உதயம் / Sunrise:</b> {sunrise_local}", styles["NormalSmall"]),
            Paragraph(f"<b>சூரிய அஸ்தமனம் / Sunset:</b> {sunset_local}", styles["NormalSmall"]),
        ],
    ]
    t_native = Table(native_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_native.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_native)
    story.append(Spacer(1, 10))

    # Golden Windows & Padupakshi Highlights Box
    golden_windows = res.get("golden_windows", [])
    padupakshi_windows = res.get("padupakshi_windows", [])

    gold_items = []
    for w in golden_windows[:3]:
        t_span = f"{w['start_time_local']} - {w['end_time_local']}"
        act = f"{w['major_activity_ta']} ({w['sub_activity_ta']})" if is_ta else f"{w['major_activity_en']} - {w['sub_activity_en']}"
        p_val = w.get("power_score", 100)
        gold_items.append(f"• <b>{t_span}</b>: {act} [{p_val}%]")
    gold_str = "<br/>".join(gold_items)

    padu_items = []
    for w in padupakshi_windows[:3]:
        t_span = f"{w['start_time_local']} - {w['end_time_local']}"
        act = f"{w['major_activity_ta']} ({w['sub_activity_ta']})" if is_ta else f"{w['major_activity_en']} - {w['sub_activity_en']}"
        padu_items.append(f"• <b>{t_span}</b>: {act} [எச்சரிக்கை / Caution]")
    padu_str = "<br/>".join(padu_items)

    windows_table_data = [
        [
            Paragraph("<b>பொன் நேரங்கள் / Golden Victory Windows (80-100%):</b>", styles["TableHeader"]),
            Paragraph("<b>படுபட்சி எச்சரிக்கை நேரங்கள் / Caution (0-25%):</b>", styles["TableHeader"]),
        ],
        [
            Paragraph(gold_str or ("இன்று தனிப்பட்ட பொன் நேரங்கள் இல்லை" if is_ta else "No golden windows for this date"), styles["NormalSmall"]),
            Paragraph(padu_str or ("இன்று படுபட்சி நேரங்கள் இல்லை" if is_ta else "No padupakshi caution windows"), styles["NormalSmall"]),
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
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_windows)
    story.append(Spacer(1, 10))

    # Daytime 25 Antara Table (Sunrise to Sunset)
    day_antara_head = [
        Paragraph("<b>நேரம் / Time Window</b>", styles["TableHeader"]),
        Paragraph("<b>முதன்மை / Major</b>", styles["TableHeader"]),
        Paragraph("<b>அந்தர செயல் / Sub</b>", styles["TableHeader"]),
        Paragraph("<b>சக்தி / Power</b>", styles["TableHeader"]),
        Paragraph("<b>பலன் / Guidance</b>", styles["TableHeader"]),
    ]
    day_rows = [day_antara_head]
    all_antaras = res.get("all_antaras", [])
    day_antaras = all_antaras[:25]
    night_antaras = all_antaras[25:]

    for slot in day_antaras:
        p_score = slot.get("power_score", 50)
        is_golden = p_score >= 80
        is_padu = p_score <= 25

        t_win = f"{slot['start_time_local']} - {slot['end_time_local']}"
        m_act = slot.get("major_activity_ta" if is_ta else "major_activity_en", "")
        s_act = slot.get("sub_activity_ta" if is_ta else "sub_activity_en", "")
        
        if is_golden:
            guidance = "வெற்றி சுப நேரம்" if is_ta else "Golden Victory"
        elif is_padu:
            guidance = "தவிர்க்கவும்" if is_ta else "Critical Caution"
        elif p_score >= 50:
            guidance = "நலன் பயக்கும்" if is_ta else "Favorable"
        else:
            guidance = "நடுத்தரம்" if is_ta else "Routine"

        day_rows.append([
            Paragraph(f"<b>{t_win}</b>", styles["TableCellBold"]),
            Paragraph(m_act, styles["TableCell"]),
            Paragraph(f"<b>{s_act}</b>", styles["TableCell"]),
            Paragraph(f"{p_score}%", styles["TableCellBold"]),
            Paragraph(guidance, styles["TableCell"]),
        ])

    story.append(Paragraph("<b>பகல் கால அந்தர அட்டவணை (Daytime Schedule - 25 Sub-periods):</b>", styles["NormalSmall"]))
    story.append(Spacer(1, 3))
    t_day = Table(day_rows, colWidths=[USABLE_WIDTH * 0.28, USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.14, USABLE_WIDTH * 0.20])
    t_day.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_day)

    # --------------------------------------------------------------------------
    # PAGE 2: NIGHTTIME SCHEDULE (Sunset to Next Sunrise) & AGASTYA SIDDHA LORE
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>இரவு கால அந்தர அட்டவணை (Nighttime Schedule - 25 Sub-periods)</b></font>", styles["SectionTitle"]))
    story.append(Spacer(1, 4))

    night_antara_head = [
        Paragraph("<b>நேரம் / Time Window</b>", styles["TableHeader"]),
        Paragraph("<b>முதன்மை / Major</b>", styles["TableHeader"]),
        Paragraph("<b>அந்தர செயல் / Sub</b>", styles["TableHeader"]),
        Paragraph("<b>சக்தி / Power</b>", styles["TableHeader"]),
        Paragraph("<b>பலன் / Guidance</b>", styles["TableHeader"]),
    ]
    night_rows = [night_antara_head]
    for slot in night_antaras:
        p_score = slot.get("power_score", 50)
        is_golden = p_score >= 80
        is_padu = p_score <= 25

        t_win = f"{slot['start_time_local']} - {slot['end_time_local']}"
        m_act = slot.get("major_activity_ta" if is_ta else "major_activity_en", "")
        s_act = slot.get("sub_activity_ta" if is_ta else "sub_activity_en", "")

        if is_golden:
            guidance = "வெற்றி சுப நேரம்" if is_ta else "Golden Victory"
        elif is_padu:
            guidance = "தவிர்க்கவும்" if is_ta else "Critical Caution"
        elif p_score >= 50:
            guidance = "நலன் பயக்கும்" if is_ta else "Favorable"
        else:
            guidance = "நடுத்தரம்" if is_ta else "Routine"

        night_rows.append([
            Paragraph(f"<b>{t_win}</b>", styles["TableCellBold"]),
            Paragraph(m_act, styles["TableCell"]),
            Paragraph(f"<b>{s_act}</b>", styles["TableCell"]),
            Paragraph(f"{p_score}%", styles["TableCellBold"]),
            Paragraph(guidance, styles["TableCell"]),
        ])

    t_night = Table(night_rows, colWidths=[USABLE_WIDTH * 0.28, USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.14, USABLE_WIDTH * 0.20])
    t_night.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_night)
    story.append(Spacer(1, 10))

    # Agastya Siddha Lore & Guidance
    lore_text = (
        "<b>அகத்தியர் பஞ்ச பட்சி சாஸ்திர பொன்மொழிகள்:</b><br/>"
        "1. <b>அரசு (Ruling - 100%):</b> புதிய ஒப்பந்தங்கள், அரசு காரியங்கள், முக்கிய முதலீடுகள் மற்றும் பதவி ஏற்பிற்கு உத்தமமானது.<br/>"
        "2. <b>ஊண் (Eating - 80%):</b> சுப பேச்சுவார்த்தைகள், பணப் பரிவர்த்தனைகள், பயணம் மற்றும் மருந்து உட்கொள்ள ஏற்றது.<br/>"
        "3. <b>நடை (Walking - 50%):</b> வழக்கமான பணிகள், பயணங்கள் மற்றும் உடற்பயிற்சி செய்ய உகந்தது.<br/>"
        "4. <b>துயில் (Sleeping - 20%):</b> ஓய்வெடுக்கவும் தியானம் செய்யவும் உகந்தது; முக்கிய செயல்களைத் தவிர்க்கவும்.<br/>"
        "5. <b>சாவு / படுபட்சி (Dying - 0%):</b> படுபட்சி காலத்தில் புதிய முயற்சிகள், கடன் கொடுத்தல்/வாங்குதல், அறுவை சிகிச்சை மற்றும் வாக்குவாதங்களை முற்றிலும் தவிர்க்க வேண்டும்."
    ) if is_ta else (
        "<b>Agastya Pancha Pakshi Shastra Principles:</b><br/>"
        "1. <b>Ruling (Arasu - 100%):</b> Peak authority. Supreme for contracts, inaugurations, promotions, and major asset acquisitions.<br/>"
        "2. <b>Eating (Oon - 80%):</b> Nourishing vitality. Ideal for negotiations, financial transactions, journeys, and healing.<br/>"
        "3. <b>Walking (Nadai - 50%):</b> Dynamic motion. Good for routine commerce, site visits, athletics, and dispatching letters.<br/>"
        "4. <b>Sleeping (Thuyil - 20%):</b> Dormant phase. Best for meditation, contemplative prayer, and resting. Avoid major launches.<br/>"
        "5. <b>Dying (Saavu / Padupakshi - 0%):</b> Critical caution. Zero vital immunity. Avoid surgery, litigation, loans, or conflicts."
    )
    story.append(Table([[Paragraph(lore_text, styles["NormalSmall"])]], colWidths=[USABLE_WIDTH], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
        ('BOX', (0, 0), (-1, -1), 0.5, GOLD_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    doc.build(story, canvasmaker=PanchaPakshiNumberedCanvas)
    return buffer.getvalue()
