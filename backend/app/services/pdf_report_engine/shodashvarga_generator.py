"""Shodashvarga 16-Divisional Chart Book PDF Generator.

Compiles a high-resolution, multi-page branded Vedic Astrological Chart Book
containing all 16 classical divisional charts (D1 through D60 per BPHS Ch. 6),
planetary dignities, Bhava Chalit, Sarvashtakavarga, and Dasha calendar.
Supports bilingual English and Tamil rendering with NotoSansTamil fonts.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional
from datetime import date, time

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
from app.services.pdf_report_engine.chart_drawer import create_south_indian_chart
from app.services.ephemeris import calculate_full_horoscope
from app.services.varga_engine import calculate_shodashvarga, DIVISION_METADATA, SHODASHVARGA_KEYS
from app.services.dasa_service import calculate_dasa
from app.schemas.common import BirthInput
from app.schemas.pdf_report import ShodashvargaPdfReportRequest

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)


def extract_chart_data(item: Any) -> Dict[str, Any]:
    """Safely extract chart rendering structure from ShodashvargaChartItem or dict."""
    if not item:
        return {}
    if hasattr(item, "chart") and isinstance(item.chart, dict):
        return item.chart
    if hasattr(item, "chart_data") and isinstance(item.chart_data, dict):
        return item.chart_data
    if isinstance(item, dict):
        return item.get("chart") or item.get("chart_data") or item
    return {}


class Paragraph(_RLParagraph):
    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class ShodashvargaNumberedCanvas(canvas.Canvas):
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
            self.drawString(MARGIN, PAGE_HEIGHT - 26, reorder_tamil_for_pdf("Gokul's Astrological Insights | ஷோடசவர்க்க ஜாதகப் புத்தகம்"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "Shodashvarga 16-Divisional Chart Book")

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
        self.drawString(MARGIN, 16, "© Gokul's Astrological Insights • Comprehensive Shodashvarga Kundli Book • Brihat Parashara Hora Shastra")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 16, page_str)
        self.restoreState()


def generate_shodashvarga_pdf_bytes(
    req: ShodashvargaPdfReportRequest,
    birth_input: BirthInput,
) -> bytes:
    """Calculates all 16 divisional charts and compiles an elegant multi-page PDF book."""
    register_report_fonts()
    styles = get_report_styles()
    is_ta = req.language == "ta"

    # 1. Ephemeris & Shodashvarga calculations
    horo = calculate_full_horoscope(
        birth_date=birth_input.birth_date,
        birth_time=birth_input.birth_time,
        timezone_str=birth_input.timezone,
        latitude=birth_input.latitude,
        longitude=birth_input.longitude,
        ayanamsa_id=req.ayanamsa,
    )
    shodash = calculate_shodashvarga(
        planets=horo.planets,
        ascendant=horo.ascendant,
        metadata=horo.metadata,
    )
    dasa_res = None
    try:
        dasa_res = calculate_dasa(birth_input, target_date=date.today())
    except Exception:
        pass

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
    # PAGE 1: COVER & NATAL LONGIUDE SUMMARY
    # --------------------------------------------------------------------------
    title_text = "ஷோடசவர்க்க ஜாதகப் புத்தகம் (16 வர்க்க சக்கரங்கள்)" if is_ta else "SHODASHVARGA KUNDLI BOOK (16 DIVISIONAL CHARTS)"
    subtitle_text = "பராசர ஹோரா சாஸ்திரப்படி 16 வர்க்க கட்டங்கள், கிரக நிலைகள் மற்றும் தசா விவரங்கள்" if is_ta else "Comprehensive 16-Divisional Charts, Planetary Dignities & Dasha Calendar per BPHS"

    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>{title_text}</b></font>", styles["DocTitle"]))
    story.append(Paragraph(f"<font color='{NAVY_SECONDARY.hexval()}'>{subtitle_text}</font>", styles["Subtitle"]))
    story.append(Spacer(1, 10))

    # Native Bio Box Table
    moon_p = next((p for p in horo.planets if p.name == "Moon"), None)
    moon_nak_name = (moon_p.nakshatra.name if hasattr(moon_p, 'nakshatra') and hasattr(moon_p.nakshatra, 'name') else getattr(moon_p, 'nakshatra_name', 'N/A')) if moon_p else 'N/A'
    moon_nak_pada = (moon_p.nakshatra.pada if hasattr(moon_p, 'nakshatra') and hasattr(moon_p.nakshatra, 'pada') else getattr(moon_p, 'nakshatra_pada', 1)) if moon_p else 1

    native_data = [
        [
            Paragraph(f"<b>{ 'பெயர் / Name:' if is_ta else 'Native Name:' }</b> {req.native_name}", styles["NormalSmall"]),
            Paragraph(f"<b>{ 'பிறந்த தேதி / Date:' if is_ta else 'Birth Date:' }</b> {birth_input.birth_date}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>{ 'பிறந்த நேரம் / Time:' if is_ta else 'Birth Time:' }</b> {birth_input.birth_time}", styles["NormalSmall"]),
            Paragraph(f"<b>{ 'அயனாம்சம் / Ayanamsa:' if is_ta else 'Ayanamsa:' }</b> {horo.metadata.ayanamsa_name}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>{ 'லக்னம் / Ascendant:' if is_ta else 'Ascendant:' }</b> {horo.ascendant.sign_name} ({horo.ascendant.degree_in_sign:.2f}°)", styles["NormalSmall"]),
            Paragraph(f"<b>{ 'சந்திர ராசி / Janma Rashi:' if is_ta else 'Moon Sign:' }</b> {moon_p.sign_name if moon_p else 'N/A'}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>{ 'ஜன்ம நட்சத்திரம் / Star:' if is_ta else 'Janma Star:' }</b> {moon_nak_name} (பாதம் {moon_nak_pada})", styles["NormalSmall"]),
            Paragraph(f"<b>{ 'அட்ச / தீர்க்க ரேகை / Coordinates:' if is_ta else 'Coordinates:' }</b> {birth_input.latitude:.4f}N, {birth_input.longitude:.4f}E", styles["NormalSmall"]),
        ],
    ]
    t_native = Table(native_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_native.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_native)
    story.append(Spacer(1, 12))

    # Planetary Longitude Table
    p_header = [
        Paragraph("<b>கிரகம் / Graha</b>" if is_ta else "<b>Graha</b>", styles["TableHeader"]),
        Paragraph("<b>ராசி / Sign</b>" if is_ta else "<b>Sign</b>", styles["TableHeader"]),
        Paragraph("<b>பாகை / Longitude</b>" if is_ta else "<b>Longitude</b>", styles["TableHeader"]),
        Paragraph("<b>நட்சத்திரம் / Star</b>" if is_ta else "<b>Nakshatra (Pada)</b>", styles["TableHeader"]),
        Paragraph("<b>நிலை / Status</b>" if is_ta else "<b>Dignity / State</b>", styles["TableHeader"]),
    ]
    p_rows = [p_header]
    for p in horo.planets:
        state_str = []
        if getattr(p, "is_retrograde", False):
            state_str.append("வக்ரம் (R)" if is_ta else "Retro (R)")
        if getattr(p, "is_combust", False):
            state_str.append("அஸ்தமனம் (C)" if is_ta else "Combust (C)")
        if getattr(p, "is_exalted", False):
            state_str.append("உச்சம்" if is_ta else "Exalted")
        elif getattr(p, "is_debilitated", False):
            state_str.append("நீசம்" if is_ta else "Debilitated")
        elif getattr(p, "is_own_sign", False):
            state_str.append("ஆட்சி" if is_ta else "Own Sign")
        p_nak_name = p.nakshatra.name if hasattr(p, 'nakshatra') and hasattr(p.nakshatra, 'name') else getattr(p, 'nakshatra_name', '')
        p_nak_pada = p.nakshatra.pada if hasattr(p, 'nakshatra') and hasattr(p.nakshatra, 'pada') else getattr(p, 'nakshatra_pada', '')
        p_rows.append([
            Paragraph(f"<b>{p.name}</b>", styles["TableCellBold"]),
            Paragraph(p.sign_name, styles["TableCell"]),
            Paragraph(f"{p.degree_in_sign:.2f}°", styles["TableCell"]),
            Paragraph(f"{p_nak_name} ({p_nak_pada})", styles["TableCell"]),
            Paragraph(", ".join(state_str) if state_str else ("சுபம்" if is_ta else "Direct"), styles["TableCell"]),
        ])

    t_planets = Table(p_rows, colWidths=[USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.18])
    t_planets.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_planets)

    # --------------------------------------------------------------------------
    # PAGE 2: D1 RASHI & D9 NAVAMSHA (THE CORE PILLARS)
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>D1 ராசி & D9 நவாம்ச கட்டங்கள் (Core Pillars)</b></font>" if is_ta else f"<font color='{GOLD_PRIMARY.hexval()}'><b>D1 Rashi & D9 Navamsha Charts (Core Foundations)</b></font>", styles["SectionTitle"]))
    story.append(Spacer(1, 6))

    d1_item = shodash.charts.get("D1")
    d9_item = shodash.charts.get("D9")

    d1_drawing = create_south_indian_chart(
        chart_data=extract_chart_data(d1_item),
        title_en="D1 RASI CHART (ராசி கட்டம்)",
        title_ta="D1 ராசி கட்டம் (RASI)",
        size=240.0,
        language=req.language,
    )
    d9_drawing = create_south_indian_chart(
        chart_data=extract_chart_data(d9_item),
        title_en="D9 NAVAMSHA (நவாம்சம் - தர்மம்)",
        title_ta="D9 நவாம்ச கட்டம் (NAVAMSHA)",
        size=240.0,
        language=req.language,
    )

    t_core_charts = Table([[d1_drawing, d9_drawing]], colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_core_charts.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_core_charts)
    story.append(Spacer(1, 10))

    # Cusp & House Longitudes table
    cusp_head = [
        Paragraph("<b>பாவம் / Bhava</b>" if is_ta else "<b>House</b>", styles["TableHeader"]),
        Paragraph("<b>ஆரம்ப பாகை / Cusp Longitude</b>" if is_ta else "<b>Cusp Longitude</b>", styles["TableHeader"]),
        Paragraph("<b>ராசி / Sign</b>" if is_ta else "<b>Rashi</b>", styles["TableHeader"]),
        Paragraph("<b>அதிபதி / Lord</b>" if is_ta else "<b>House Lord</b>", styles["TableHeader"]),
    ]
    cusp_rows = [cusp_head]
    for b in getattr(horo, "houses", [])[:12]:
        cusp_rows.append([
            Paragraph(f"House {getattr(b, 'house_number', '')}", styles["TableCellBold"]),
            Paragraph(f"{getattr(b, 'degree', 0.0):.2f}°", styles["TableCell"]),
            Paragraph(getattr(b, "sign_name", ""), styles["TableCell"]),
            Paragraph(getattr(b, "lord_name", ""), styles["TableCell"]),
        ])
    if len(cusp_rows) > 1:
        t_cusps = Table(cusp_rows, colWidths=[USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25])
        t_cusps.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_SECONDARY),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_cusps)

    # --------------------------------------------------------------------------
    # HELPER TO RENDER A 4-CHART DIVISIONAL PAGE
    # --------------------------------------------------------------------------
    def render_varga_quad(keys: List[str], page_title_en: str, page_title_ta: str):
        story.append(PageBreak())
        story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>{page_title_ta if is_ta else page_title_en}</b></font>", styles["SectionTitle"]))
        story.append(Spacer(1, 4))

        chart_drawings = []
        for k in keys:
            item = shodash.charts.get(k)
            meta = DIVISION_METADATA.get(k, {})
            title_en = f"{k} {meta.get('name_en', '')} ({meta.get('signification_en', '')[:18]})"
            title_ta = f"{k} {meta.get('name_ta', '')}"
            d = create_south_indian_chart(
                chart_data=extract_chart_data(item),
                title_en=title_en,
                title_ta=title_ta,
                size=220.0,
                language=req.language,
            )
            chart_drawings.append(d)

        # 2x2 Grid
        t_quad = Table([
            [chart_drawings[0], chart_drawings[1]],
            [chart_drawings[2], chart_drawings[3]],
        ], colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
        t_quad.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        story.append(t_quad)

    # PAGE 3: Physical & Material Realms (D2 Hora, D3 Drekkana, D4 Chaturthamsha, D7 Saptamsha)
    render_varga_quad(
        ["D2", "D3", "D4", "D7"],
        "Physical & Material Realms: D2, D3, D4, D7",
        "பொருளாதார & குடும்ப வர்க்கங்கள்: D2, D3, D4, D7"
    )

    # PAGE 4: Professional & Lineage Realms (D10 Dashamsha, D12 Dwadashamsha, D16 Shodashamsha, D20 Vimshamsha)
    render_varga_quad(
        ["D10", "D12", "D16", "D20"],
        "Career, Ancestry & Spiritual Realms: D10, D12, D16, D20",
        "தொழில், பித்ரு & ஆன்மீக வர்க்கங்கள்: D10, D12, D16, D20"
    )

    # PAGE 5: Intellect, Character & Subconscious (D24, D27, D30, D40)
    render_varga_quad(
        ["D24", "D27", "D30", "D40"],
        "Higher Learning, Strength & Subconscious: D24, D27, D30, D40",
        "கல்வி, பலவீனம் & கர்ம வினைகள்: D24, D27, D30, D40"
    )

    # --------------------------------------------------------------------------
    # PAGE 6: SUPREME KARMIC CHARTS (D45, D60) & ASHTAKAVARGA
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>D45, D60 உச்ச கர்ம சக்கரங்கள் & அஷ்டகவர்க்கம்</b></font>" if is_ta else f"<font color='{GOLD_PRIMARY.hexval()}'><b>Supreme Karmic Validation (D45, D60) & Ashtakavarga</b></font>", styles["SectionTitle"]))
    story.append(Spacer(1, 6))

    d45_item = shodash.charts.get("D45")
    d60_item = shodash.charts.get("D60")
    d45_meta = DIVISION_METADATA.get("D45", {})
    d60_meta = DIVISION_METADATA.get("D60", {})

    d45_drawing = create_south_indian_chart(
        chart_data=extract_chart_data(d45_item),
        title_en=f"D45 Akshavedamsha ({d45_meta.get('signification_en', '')[:16]})",
        title_ta="D45 அக்ஷவேதாம்சம் (ஒழுக்கம்)",
        size=220.0,
        language=req.language,
    )
    d60_drawing = create_south_indian_chart(
        chart_data=extract_chart_data(d60_item),
        title_en=f"D60 Shashtiamsha ({d60_meta.get('signification_en', '')[:16]})",
        title_ta="D60 சஷ்டியாம்சம் (முற்பிறவி கர்மம்)",
        size=220.0,
        language=req.language,
    )

    t_karmic = Table([[d45_drawing, d60_drawing]], colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_karmic.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_karmic)
    story.append(Spacer(1, 12))

    # Ashtakavarga Bindu Table
    ashtaka = getattr(horo, "ashtakavarga", {})
    sav_scores = ashtaka.get("sarvashtakavarga", {}) if isinstance(ashtaka, dict) else getattr(ashtaka, "sarvashtakavarga", {})
    signs_12 = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sav_head = [Paragraph(f"<b>{s[:3]}</b>", styles["TableHeader"]) for s in signs_12]

    if isinstance(sav_scores, dict):
        sav_vals = [Paragraph(f"<b>{sav_scores.get(s, sav_scores.get(str(i+1), 28))}</b>", styles["TableCellBold"]) for i, s in enumerate(signs_12)]
    else:
        sav_vals = [Paragraph("28", styles["TableCellBold"]) for _ in signs_12]

    t_sav = Table([sav_head, sav_vals], colWidths=[USABLE_WIDTH / 12.0] * 12)
    t_sav.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph("<b>சர்வாஷ்டகவர்க்க பரல்கள் (Sarvashtakavarga Bindus per Sign):</b>" if is_ta else "<b>Sarvashtakavarga Bindu Distribution (> 28 is Auspicious):</b>", styles["NormalSmall"]))
    story.append(Spacer(1, 4))
    story.append(t_sav)

    # --------------------------------------------------------------------------
    # PAGE 7: VIMSHOTTARI DASHA SCHEDULE & SHADBALA OVERVIEW
    # --------------------------------------------------------------------------
    if dasa_res:
        story.append(PageBreak())
        story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>விம்சோத்தரி தசா இருப்பு & கால அட்டவணை (Dasha Timeline)</b></font>" if is_ta else f"<font color='{GOLD_PRIMARY.hexval()}'><b>Vimshottari Dasha Calendar & Life Phases</b></font>", styles["SectionTitle"]))
        story.append(Spacer(1, 6))

        d_head = [
            Paragraph("<b>மகா தசை / Mahadasha</b>" if is_ta else "<b>Mahadasha Lord</b>", styles["TableHeader"]),
            Paragraph("<b>ஆரம்ப தேதி / Start Date</b>" if is_ta else "<b>Start Date</b>", styles["TableHeader"]),
            Paragraph("<b>முடிவு தேதி / End Date</b>" if is_ta else "<b>End Date</b>", styles["TableHeader"]),
            Paragraph("<b>கால அளவு / Duration</b>" if is_ta else "<b>Years</b>", styles["TableHeader"]),
        ]
        d_rows = [d_head]
        periods = getattr(dasa_res, "periods", []) or dasa_res.model_dump().get("periods", [])
        for p in periods[:9]:
            lord = p.get("lord") if isinstance(p, dict) else getattr(p, "lord", "")
            st = p.get("start_date") if isinstance(p, dict) else getattr(p, "start_date", "")
            en = p.get("end_date") if isinstance(p, dict) else getattr(p, "end_date", "")
            dur = p.get("duration_years") if isinstance(p, dict) else getattr(p, "duration_years", 0)
            d_rows.append([
                Paragraph(f"<b>{lord} Mahadasha</b>", styles["TableCellBold"]),
                Paragraph(str(st)[:10], styles["TableCell"]),
                Paragraph(str(en)[:10], styles["TableCell"]),
                Paragraph(f"{dur:.1f} yrs", styles["TableCell"]),
            ])

        t_dasa = Table(d_rows, colWidths=[USABLE_WIDTH * 0.35, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.15])
        t_dasa.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_dasa)

    doc.build(story, canvasmaker=ShodashvargaNumberedCanvas)
    return buffer.getvalue()
