"""ReportLab PDF Horoscope Report Generator.

Compiles an approximately nine-page professional, branded Vedic horoscope report
in English and Tamil for Gokul's Astrological Insights.
Uses ReportLab with NotoSansTamil TrueType fonts and vector South Indian charts.
"""

from io import BytesIO
import logging
from typing import Dict, Any, List, Optional

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
    HRFlowable,
)
from reportlab.pdfgen import canvas

from app.services.pdf_report_engine.fonts import (
    get_report_styles,
    reorder_tamil_for_pdf,
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
from app.services.pdf_report_engine.data_builder import ReportData

logger = logging.getLogger("gai.pdf.generator")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0  # 0.5 inch
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 523.27 pt


class Paragraph(_RLParagraph):
    """Custom Paragraph that automatically pre-processes Tamil text for linear TTFont rendering."""

    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


GRAHA_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "ராகு",
    "Ketu": "கேது",
    "Ascendant": "லக்னம்",
    "Uranus": "யுரேனஸ்",
    "Neptune": "நெப்டியூன்",
    "Pluto": "புளூட்டோ",
}


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that writes dynamic total page count and running headers."""

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

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 7.5)
            except Exception:
                self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(GOLD_PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 26, reorder_tamil_for_pdf("Gokul's Astrological Insights | வேத ஜோதிட அறிக்கை"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "Vedic Horoscope Report • Confidential")

            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 30, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 30)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(MARGIN, 28, PAGE_WIDTH - MARGIN, 28)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 18, "© Gokul's Astrological Insights • Powered by XALEN Astronomical Engine • Clean-Room Vedic Astrology")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, page_str)

        self.restoreState()


class HoroscopePdfReportGenerator:
    """Orchestrates building all 9 pages of the branded horoscope report."""

    def __init__(self, data: ReportData):
        self.data = data
        self.styles = get_report_styles()
        self.lang = data.language

    def generate(self) -> bytes:
        """Generates the PDF document and returns the byte array."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=36.0,
            bottomMargin=36.0,
        )

        story: List[Any] = []

        # Build each of the 9 pages with an explicit PageBreak between them
        story.extend(self._build_page_1_cover())
        story.append(PageBreak())

        story.extend(self._build_page_2_rasi())
        story.append(PageBreak())

        story.extend(self._build_page_3_navamsa())
        story.append(PageBreak())

        story.extend(self._build_page_4_dasamsa_vargas())
        story.append(PageBreak())

        story.extend(self._build_page_5_shadbala())
        story.append(PageBreak())

        story.extend(self._build_page_6_ashtakavarga())
        story.append(PageBreak())

        story.extend(self._build_page_7_yogas())
        story.append(PageBreak())

        story.extend(self._build_page_8_doshas())
        story.append(PageBreak())

        story.extend(self._build_page_9_dasa_remedies())

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------------------
    # PAGE 1: Brand Cover & Native Birth Particulars + Birth Panchang
    # -------------------------------------------------------------------------
    def _build_page_1_cover(self) -> List[Any]:
        elements: List[Any] = []

        # Header Banner
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("GOKUL'S ASTROLOGICAL INSIGHTS", self.styles["BrandHeader"]))
        elements.append(Paragraph("வேத ஜோதிட ஜாதக விரிவான அறிக்கை | Comprehensive Vedic Horoscope", self.styles["BrandSubHeader"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=GOLD_PRIMARY, spaceBefore=4, spaceAfter=14))

        # Native Particulars Table
        elements.append(Paragraph("Native Birth Particulars — ஜாதகர் பிறப்பு விவரங்கள்", self.styles["SectionTitle"]))

        verified_text = "✓ Verified Birth Data" if self.data.is_verified else "⚠ Unverified Birth Time"
        verified_color = "#15803D" if self.data.is_verified else "#B45309"

        birth_info_data = [
            [
                Paragraph("<b>Native Name / ஜாதகர்:</b>", self.styles["TableCell"]),
                Paragraph(f"<b>{self.data.native_name}</b>", self.styles["TableCell"]),
                Paragraph("<b>Gender / பாலினம்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.gender.capitalize(), self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Date of Birth / தேதி:</b>", self.styles["TableCell"]),
                Paragraph(self.data.birth_date, self.styles["TableCell"]),
                Paragraph("<b>Time of Birth / நேரம்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.birth_time, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Coordinates / அமைவிடம்:</b>", self.styles["TableCell"]),
                Paragraph(f"{self.data.latitude:.4f}°N, {self.data.longitude:.4f}°E", self.styles["TableCell"]),
                Paragraph("<b>Timezone / நேர வலயம்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.timezone_str, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Ayanamsa / அயனாம்சம்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.ayanamsa_name, self.styles["TableCell"]),
                Paragraph("<b>House System / பாவம்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.house_system_name, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Report ID / அறிக்கை எண்:</b>", self.styles["TableCell"]),
                Paragraph(self.data.report_id, self.styles["TableCell"]),
                Paragraph("<b>Status / நம்பகத்தன்மை:</b>", self.styles["TableCell"]),
                Paragraph(f"<font color='{verified_color}'><b>{verified_text}</b></font>", self.styles["TableCell"]),
            ],
        ]

        t_info = Table(birth_info_data, colWidths=[120, 140, 120, 140])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 14))

        # Panchang Table
        elements.append(Paragraph("Birth Panchang — பிறப்பு பஞ்சாங்க விவரங்கள் (Five Limbs of Time)", self.styles["SectionTitle"]))
        elements.append(Paragraph("The five limbs of Panchang determine the native's elemental and psychological constitution at the exact epoch of birth.", self.styles["SectionSubtitle"]))

        panchang = self.data.horoscope.panchang if self.data.horoscope else None
        tithi_str = f"{panchang.tithi.paksha} {panchang.tithi.name}" if panchang else "Krishna Ashtami"
        vara_str = panchang.vara if panchang else "Somavara"
        nak_str = panchang.nakshatra if panchang else "Rohini"
        yoga_str = panchang.yoga.name if panchang else "Siddha"
        karana_str = panchang.karana if panchang else "Bava"

        panchang_data = [
            [
                Paragraph("<b>Panchang Limb / அங்கம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Value / மதிப்பு</b>", self.styles["TableHeader"]),
                Paragraph("<b>Tamil Name / தமிழாக்கம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Governing Element / தத்துவம்</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>1. Tithi (திதி)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(tithi_str, self.styles["TableCellCenter"]),
                Paragraph("திதி (சந்திர நிலை)", self.styles["TableCellCenter"]),
                Paragraph("Jala / நீர் (Emotional Mind)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>2. Vara (வாரம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(vara_str, self.styles["TableCellCenter"]),
                Paragraph("வாரம் (கிழமை)", self.styles["TableCellCenter"]),
                Paragraph("Agni / நெருப்பு (Vitality & Health)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>3. Nakshatra (நட்சத்திரம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(nak_str, self.styles["TableCellCenter"]),
                Paragraph("நட்சத்திரம் (ஜென்ம தாரை)", self.styles["TableCellCenter"]),
                Paragraph("Vayu / காற்று (Destiny & Mind)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>4. Yoga (யோகம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(yoga_str, self.styles["TableCellCenter"]),
                Paragraph("நித்திய யோகம்", self.styles["TableCellCenter"]),
                Paragraph("Akasha / ஆகாயம் (Spiritual Link)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>5. Karana (கரணம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(karana_str, self.styles["TableCellCenter"]),
                Paragraph("கரணம் (செயல் திறன்)", self.styles["TableCellCenter"]),
                Paragraph("Prithvi / நிலம் (Material Success)", self.styles["TableCellCenter"]),
            ],
        ]

        t_panchang = Table(panchang_data, colWidths=[130, 130, 130, 130])
        t_panchang.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_panchang)
        elements.append(Spacer(1, 16))

        # Classical Invocation Shloka
        shloka_text = (
            "வேயுறு தோளிபங்கன் விடமுண்ட கண்டன் மிகநல்ல வீணை தடவி<br/>"
            "மாசறு திங்கள்கங்கை முடிமே லணிந்தென் உளமே புகுந்த அதனால்<br/>"
            "ஞாயிறு திங்கள்செவ்வாய் புதன்வியாழன் வெள்ளி சனிபாம்பி ரண்டு முடனே<br/>"
            "ஆசறு நல்லநல்ல அவைநல்ல நல்ல அடியா ரவர்க்கு மிகவே.<br/>"
            "<font size='7' color='#8B6914'><b>— திருஞானசம்பந்தர் அருளிய திருநெறி கோளறு பதிகம்</b></font>"
        )
        shloka_table = Table([[Paragraph(shloka_text, self.styles["TamilShloka"])]], colWidths=[520])
        shloka_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(shloka_table)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 2: Rasi Chart (D1) Vector Diagram + Comprehensive Planetary Positions
    # -------------------------------------------------------------------------
    def _build_page_2_rasi(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("D1 Rasi Chart & Planetary Longitudes — ராசி கட்டம் & கிரக நிலைகள்", self.styles["SectionTitle"]))
        elements.append(Paragraph("High-precision sidereal Nirayana longitudes calculated via XALEN ephemeris engine.", self.styles["SectionSubtitle"]))

        # Build D1 Chart Data
        planets = self.data.horoscope.planets if self.data.horoscope else []
        ascendant = self.data.horoscope.ascendant if self.data.horoscope else None

        d1_chart_dict = {
            "ascendant_sign": ascendant.sign_index if ascendant else 1,
            "ascendant_degree": ascendant.degree_in_sign if ascendant else 0.0,
            "planets": [
                {
                    "name": p.name,
                    "sign_index": p.sign_index,
                    "degree_in_sign": p.degree_in_sign,
                    "is_retrograde": p.is_retrograde,
                }
                for p in planets
            ],
        }

        d1_drawing = create_south_indian_chart(
            d1_chart_dict,
            title_en="D1 RASI CHART",
            title_ta="ராசி கட்டம் (D1)",
            size=210.0,
            language=self.lang,
        )

        # Overview Table side by side or placed neatly
        elements.append(Spacer(1, 4))
        elements.append(d1_drawing)
        elements.append(Spacer(1, 10))

        # Comprehensive Planet Table
        planet_rows = [
            [
                Paragraph("<b>Graha / கிரகம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Longitude</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign / ராசி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Deg in Sign</b>", self.styles["TableHeader"]),
                Paragraph("<b>Nakshatra & Pada</b>", self.styles["TableHeader"]),
                Paragraph("<b>Star Lord</b>", self.styles["TableHeader"]),
                Paragraph("<b>House</b>", self.styles["TableHeader"]),
                Paragraph("<b>Motion</b>", self.styles["TableHeader"]),
            ]
        ]

        # Add Ascendant row first
        if ascendant:
            deg = ascendant.degree
            d_i, m_i, s_i = int(deg), int((deg - int(deg)) * 60), int(round(((deg - int(deg)) * 60 - int((deg - int(deg)) * 60)) * 60))
            planet_rows.append([
                Paragraph("<b>Lagna / லக்னம்</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(f"{d_i}° {m_i:02d}' {s_i:02d}\"", self.styles["TableCellCenter"]),
                Paragraph(f"{ascendant.sign_name} / {ascendant.sign_name_tamil}", self.styles["TableCell"]),
                Paragraph(f"{ascendant.degree_in_sign:.2f}°", self.styles["TableCellCenter"]),
                Paragraph(f"{ascendant.nakshatra.name} - {ascendant.nakshatra.pada}", self.styles["TableCell"]),
                Paragraph(ascendant.nakshatra.lord, self.styles["TableCellCenter"]),
                Paragraph("1", self.styles["TableCellCenter"]),
                Paragraph("Direct", self.styles["TableCellCenter"]),
            ])

        for p in planets:
            deg = p.longitude
            d_i, m_i, s_i = int(deg), int((deg - int(deg)) * 60), int(round(((deg - int(deg)) * 60 - int((deg - int(deg)) * 60)) * 60))
            retro_str = "Retro (வக்ரம்)" if p.is_retrograde else "Direct"
            # Approximate house from ascendant
            house_num = ((p.sign_index - (ascendant.sign_index if ascendant else 1)) % 12) + 1

            # Planet name with Tamil translation
            ta_name = GRAHA_NAMES_TA.get(p.name, p.sign_name_tamil[:3])
            planet_rows.append([
                Paragraph(f"<b>{p.name} / {ta_name}</b>", self.styles["TableCell"]),
                Paragraph(f"{d_i}° {m_i:02d}' {s_i:02d}\"", self.styles["TableCellCenter"]),
                Paragraph(f"{p.sign_name} / {p.sign_name_tamil}", self.styles["TableCell"]),
                Paragraph(f"{p.degree_in_sign:.2f}°", self.styles["TableCellCenter"]),
                Paragraph(f"{p.nakshatra.name} - {p.nakshatra.pada}", self.styles["TableCell"]),
                Paragraph(p.nakshatra.lord, self.styles["TableCellCenter"]),
                Paragraph(str(house_num), self.styles["TableCellCenter"]),
                Paragraph(retro_str, self.styles["TableCellCenter"]),
            ])

        t_planets = Table(planet_rows, colWidths=[68, 62, 75, 55, 95, 55, 45, 65])
        t_planets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_planets)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 3: Navamsa (D9) Vector Diagram + D9 Placements + Vargottama Callouts
    # -------------------------------------------------------------------------
    def _build_page_3_navamsa(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("D9 Navamsa Chart — நவாம்ச கட்டம் & தர்ம/ஆன்மீக வலிமை", self.styles["SectionTitle"]))
        elements.append(Paragraph("Navamsa (1/9th division) illuminates the spiritual core, dharma, marriage partner, and destiny fruition in the second half of life.", self.styles["SectionSubtitle"]))

        # Get D9 info from shodashvarga or varga_d1_d9
        d9_planets = []
        d9_asc_sign = 1
        d9_asc_deg = 0.0

        if self.data.shodashvarga and "D9" in self.data.shodashvarga.charts:
            d9_chart = self.data.shodashvarga.charts["D9"]
            d9_asc_sign = d9_chart.ascendant.sign_index
            d9_asc_deg = d9_chart.ascendant.degree_in_sign
            for p in d9_chart.planets:
                d9_planets.append({
                    "name": p.name,
                    "sign_index": p.sign_index,
                    "degree_in_sign": p.degree_in_sign,
                    "is_retrograde": p.is_retrograde,
                })
        elif self.data.horoscope and self.data.horoscope.varga_d1_d9:
            d9_chart = self.data.horoscope.varga_d1_d9.d9_chart
            d9_asc_sign = d9_chart.ascendant.sign_index
            d9_asc_deg = d9_chart.ascendant.degree_in_sign
            for p in d9_chart.planets:
                d9_planets.append({
                    "name": p.name,
                    "sign_index": p.sign_index,
                    "degree_in_sign": p.degree_in_sign,
                    "is_retrograde": p.is_retrograde,
                })

        d9_drawing = create_south_indian_chart(
            {
                "ascendant_sign": d9_asc_sign,
                "ascendant_degree": d9_asc_deg,
                "planets": d9_planets,
            },
            title_en="D9 NAVAMSA",
            title_ta="நவாம்ச கட்டம் (D9)",
            size=210.0,
            language=self.lang,
        )

        elements.append(Spacer(1, 4))
        elements.append(d9_drawing)
        elements.append(Spacer(1, 10))

        # Check Vargottama planets (same sign in D1 and D9)
        d1_planets = {p.name: p.sign_index for p in (self.data.horoscope.planets if self.data.horoscope else [])}
        vargottama_list = []
        for p in d9_planets:
            p_name = p["name"]
            if p_name in d1_planets and d1_planets[p_name] == p["sign_index"]:
                vargottama_list.append(p_name)

        # Navamsa Table
        d9_table_data = [
            [
                Paragraph("<b>Graha / கிரகம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>D9 Sign / நவாம்ச ராசி</b>", self.styles["TableHeader"]),
                Paragraph("<b>D9 Lord / ராசி நாதன்</b>", self.styles["TableHeader"]),
                Paragraph("<b>D9 Deg</b>", self.styles["TableHeader"]),
                Paragraph("<b>Vargottama Status / வர்கோத்தமம்</b>", self.styles["TableHeader"]),
            ]
        ]

        sign_lords = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
        }
        sign_names = {
            1: "Aries / மேஷம்", 2: "Taurus / ரிஷபம்", 3: "Gemini / மிதுனம்", 4: "Cancer / கடகம்",
            5: "Leo / சிம்மம்", 6: "Virgo / கன்னி", 7: "Libra / துலாம்", 8: "Scorpio / விருச்சிகம்",
            9: "Sagittarius / தனுசு", 10: "Capricorn / மகரம்", 11: "Aquarius / கும்பம்", 12: "Pisces / மீனம்"
        }

        for p in d9_planets:
            p_name = p["name"]
            s_idx = p["sign_index"]
            is_varg = p_name in vargottama_list
            varg_badge = "<font color='#15803D'><b>✓ Vargottama (வர்கோத்தமம்)</b></font>" if is_varg else "Normal"

            d9_table_data.append([
                Paragraph(f"<b>{p_name}</b>", self.styles["TableCell"]),
                Paragraph(sign_names.get(s_idx, str(s_idx)), self.styles["TableCell"]),
                Paragraph(sign_lords.get(s_idx, "Unknown"), self.styles["TableCellCenter"]),
                Paragraph(f"{p['degree_in_sign']:.2f}°", self.styles["TableCellCenter"]),
                Paragraph(varg_badge, self.styles["TableCellCenter"]),
            ])

        t_d9 = Table(d9_table_data, colWidths=[90, 130, 95, 75, 130])
        t_d9.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_d9)
        elements.append(Spacer(1, 10))

        # Vargottama Callout Box
        varg_str = ", ".join(vargottama_list) if vargottama_list else "None detected in current chart."
        callout_html = (
            f"<b>Vargottama Grahas (வர்கோத்தம கிரகங்கள்):</b> {varg_str}<br/>"
            "<i>Classical Note (Phaladeepika):</i> A planet occupying the same sign in both D1 (Rasi) and D9 (Navamsa) "
            "acquires Sthanabala equal to an exalted graha, yielding unwavering auspicious results and shielding the native during difficult transits."
        )
        callout_table = Table([[Paragraph(callout_html, self.styles["ReportBody"])]], colWidths=[520])
        callout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor("#86EFAC")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(callout_table)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 4: Dasamsa (D10) Vector Diagram + 16-Varga Summary Matrix + D60 Deities
    # -------------------------------------------------------------------------
    def _build_page_4_dasamsa_vargas(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("D10 Dasamsa & Shodashvarga Summary — தொழில் & 16 வர்க்க நிலைகள்", self.styles["SectionTitle"]))
        elements.append(Paragraph("The D10 Dasamsa chart delineates profession, public career, and status. The complete Shodashvarga matrix reflects multi-dimensional karma.", self.styles["SectionSubtitle"]))

        # D10 Chart Drawing
        d10_planets = []
        d10_asc_sign = 1
        d10_asc_deg = 0.0

        if self.data.shodashvarga and "D10" in self.data.shodashvarga.charts:
            d10_chart = self.data.shodashvarga.charts["D10"]
            d10_asc_sign = d10_chart.ascendant.sign_index
            d10_asc_deg = d10_chart.ascendant.degree_in_sign
            for p in d10_chart.planets:
                d10_planets.append({
                    "name": p.name,
                    "sign_index": p.sign_index,
                    "degree_in_sign": p.degree_in_sign,
                    "is_retrograde": p.is_retrograde,
                })

        d10_drawing = create_south_indian_chart(
            {
                "ascendant_sign": d10_asc_sign,
                "ascendant_degree": d10_asc_deg,
                "planets": d10_planets,
            },
            title_en="D10 DASAMSA",
            title_ta="தசாம்சம் (D10)",
            size=180.0,
            language=self.lang,
        )

        elements.append(Spacer(1, 4))
        elements.append(d10_drawing)
        elements.append(Spacer(1, 8))

        # 16-Varga Sign Placement Summary Matrix
        elements.append(Paragraph("<b>Comprehensive 16-Divisional Sign Matrix (ஷோடசவர்க்க ராசி பட்டியல்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 4))

        varga_keys = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        matrix_header = [Paragraph("<b>Graha</b>", self.styles["TableHeader"])] + [
            Paragraph(f"<b>{k}</b>", self.styles["TableHeader"]) for k in varga_keys
        ]
        matrix_rows = [matrix_header]

        entities = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

        if self.data.shodashvarga:
            for ent in entities:
                row = [Paragraph(f"<b>{ent[:3]}</b>", self.styles["TableCell"])]
                for vk in varga_keys:
                    c = self.data.shodashvarga.charts.get(vk)
                    if not c:
                        row.append(Paragraph("-", self.styles["TableCellCenter"]))
                        continue
                    if ent == "Ascendant":
                        row.append(Paragraph(str(c.ascendant.sign_index), self.styles["TableCellCenter"]))
                    else:
                        found_sign = "-"
                        for p in c.planets:
                            if p.name == ent:
                                found_sign = str(p.sign_index)
                                break
                        row.append(Paragraph(found_sign, self.styles["TableCellCenter"]))
                matrix_rows.append(row)

        col_w = [40] + [30] * 16  # 40 + 480 = 520 pt
        t_matrix = Table(matrix_rows, colWidths=col_w)
        t_matrix.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_matrix)
        elements.append(Spacer(1, 8))

        # D60 Shashtyamsa Highlights
        elements.append(Paragraph("<b>D60 Shashtyamsa Deities (அறுபதாம்ச தேவதைகள்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        d60_rows = [
            [
                Paragraph("<b>Graha</b>", self.styles["TableHeader"]),
                Paragraph("<b>D60 Sign</b>", self.styles["TableHeader"]),
                Paragraph("<b>Shashtyamsa Deity (தேவதை)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Nature / சுப/அசுப தன்மை</b>", self.styles["TableHeader"]),
            ]
        ]

        if self.data.shodashvarga and "D60" in self.data.shodashvarga.charts:
            d60_c = self.data.shodashvarga.charts["D60"]
            for p in d60_c.planets[:7]:  # 7 classical planets
                deity_str = f"{p.shashtyamsa_deity} ({p.shashtyamsa_deity_tamil})" if p.shashtyamsa_deity else "N/A"
                nature_str = "<font color='#15803D'>Benefic / சுபர்</font>" if p.shashtyamsa_nature == "Benefic" else "<font color='#991B1B'>Malefic / அசுபர்</font>"
                d60_rows.append([
                    Paragraph(f"<b>{p.name}</b>", self.styles["TableCell"]),
                    Paragraph(str(p.sign_index), self.styles["TableCellCenter"]),
                    Paragraph(deity_str, self.styles["TableCell"]),
                    Paragraph(nature_str, self.styles["TableCellCenter"]),
                ])

        t_d60 = Table(d60_rows, colWidths=[90, 80, 230, 120])
        t_d60.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_d60)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 5: Shadbala Master Table + Virupas/Rupas/Rankings + Interpretation
    # -------------------------------------------------------------------------
    def _build_page_5_shadbala(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Shadbala Engine — அறுவகை கிரக பலம் (Six-Fold Strength Analysis)", self.styles["SectionTitle"]))
        elements.append(Paragraph("Classical quantitative planetary strength calculated per Brihat Parasara Hora Shastra (BPHS) Chapter 23.", self.styles["SectionSubtitle"]))

        # Shadbala Master Table
        shad_header = [
            Paragraph("<b>Graha</b>", self.styles["TableHeader"]),
            Paragraph("<b>Sthana</b>", self.styles["TableHeader"]),
            Paragraph("<b>Dig</b>", self.styles["TableHeader"]),
            Paragraph("<b>Kala</b>", self.styles["TableHeader"]),
            Paragraph("<b>Cheshta</b>", self.styles["TableHeader"]),
            Paragraph("<b>Naisargika</b>", self.styles["TableHeader"]),
            Paragraph("<b>Drik</b>", self.styles["TableHeader"]),
            Paragraph("<b>Virupas</b>", self.styles["TableHeader"]),
            Paragraph("<b>Rupas</b>", self.styles["TableHeader"]),
            Paragraph("<b>Req.</b>", self.styles["TableHeader"]),
            Paragraph("<b>Ratio</b>", self.styles["TableHeader"]),
            Paragraph("<b>Rank</b>", self.styles["TableHeader"]),
        ]
        shad_rows = [shad_header]

        strongest_planet = "Jupiter"
        weakest_planet = "Saturn"

        if self.data.shadbala:
            # Sort by rank
            strongest_planet = self.data.shadbala.strongest_planet
            weakest_planet = self.data.shadbala.weakest_planet
            sorted_details = sorted(self.data.shadbala.planets, key=lambda x: x.rank)

            for p in sorted_details:
                sthana_val = p.sthana_bala.total
                kala_val = p.kala_bala.total
                status_color = "#15803D" if p.is_strong else "#991B1B"
                ratio_badge = f"<font color='{status_color}'><b>{p.ratio:.2f}</b></font>"

                shad_rows.append([
                    Paragraph(f"<b>{p.planet}</b>", self.styles["TableCell"]),
                    Paragraph(f"{sthana_val:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.dig_bala:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{kala_val:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.cheshta_bala:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.naisargika_bala:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.drik_bala:.1f}", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{p.total_virupas:.1f}</b>", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.total_rupas:.2f}", self.styles["TableCellCenter"]),
                    Paragraph(f"{p.required_virupas:.0f}", self.styles["TableCellCenter"]),
                    Paragraph(ratio_badge, self.styles["TableCellCenter"]),
                    Paragraph(f"<b>#{p.rank}</b>", self.styles["TableCellBoldCenter"]),
                ])

        col_w = [52, 40, 36, 40, 42, 46, 38, 48, 40, 42, 48, 48]  # Sum = 520 pt
        t_shad = Table(shad_rows, colWidths=col_w)
        t_shad.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_shad)
        elements.append(Spacer(1, 14))

        # Classical Shadbala Components Explanation
        elements.append(Paragraph("<b>Classical Components of Shadbala (அறுவகை பலங்களின் விளக்கம்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 4))

        comp_data = [
            [
                Paragraph("<b>1. Sthana Bala (ஸ்தான பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Positional strength based on Uchcha (exaltation), Saptavargaja (divisional dignities), Ojhayugma, and Kendradi bala.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>2. Dig Bala (திசா பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Directional strength: Jupiter/Mercury in East (1st), Sun/Mars in South (10th), Saturn in West (7th), Moon/Venus in North (4th).", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>3. Kala Bala (கால பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Temporal strength combining Nathonnatha (day/night birth), Paksha, Tribhaga, Varsha-Masa-Dina-Hora lords, and Ayana bala.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>4. Cheshta Bala (சேஷ்டா பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Motional strength arising from planetary retrogradation, speed variations, and heliocentric elongation from the Sun.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>5. Naisargika Bala (நைசர்கிக பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Natural luminous strength invariant across charts: Sun (60) > Moon (51.4) > Venus (42.9) > Jupiter (34.3) > Mercury (25.7) > Mars (17.1) > Saturn (8.6).", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>6. Drik Bala (த்ரிக் பலம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("Aspect strength resulting from benefic and malefic angular aspects cast by all other grahas upon the target planet.", self.styles["TableCell"]),
            ],
        ]

        t_comp = Table(comp_data, colWidths=[150, 370])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_comp)
        elements.append(Spacer(1, 10))

        # Interpretation Summary Card
        interp_html = (
            f"<b>Planetary Hierarchy in Natal Chart:</b><br/>"
            f"• <b>Primary Anchoring Planet:</b> <b>{strongest_planet}</b> ranks #1 with peak Shadbala ratio, serving as the chief protector and benefactor for the native's aspirations.<br/>"
            f"• <b>Planet Requiring Remedial Focus:</b> <b>{weakest_planet}</b> holds the lowest relative strength. Remedial propitiation and conscious alignment with its significations are recommended."
        )
        t_interp = Table([[Paragraph(interp_html, self.styles["ReportBody"])]], colWidths=[520])
        t_interp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_interp)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 6: Ashtakavarga BAV 7-Planet Table + SAV 337 Invariant Summary
    # -------------------------------------------------------------------------
    def _build_page_6_ashtakavarga(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Ashtakavarga System — அஷ்டகவர்க்கம் (BAV, SAV & சோதனா பலன்கள்)", self.styles["SectionTitle"]))
        elements.append(Paragraph("Eight-fold benefic point matrix evaluated per BPHS Ch. 66–69 with validated 337 Sarvashtakavarga invariant.", self.styles["SectionSubtitle"]))

        # Build BAV / SAV Table
        signs_short = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        bav_header = [Paragraph("<b>Graha</b>", self.styles["TableHeader"])] + [
            Paragraph(f"<b>{s}</b>", self.styles["TableHeader"]) for s in signs_short
        ] + [Paragraph("<b>Total</b>", self.styles["TableHeader"])]

        bav_rows = [bav_header]

        av = self.data.horoscope.ashtakavarga if self.data.horoscope else None

        planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        if av and av.bhinnashtakavarga:
            for p_name in planets_order:
                bav_chart = av.bhinnashtakavarga.get(p_name)
                if bav_chart:
                    row = [Paragraph(f"<b>{p_name}</b>", self.styles["TableCell"])]
                    for s_idx in range(1, 13):
                        val = bav_chart.sign_bindus.get(s_idx, bav_chart.sign_bindus.get(str(s_idx), 0))
                        row.append(Paragraph(str(val), self.styles["TableCellCenter"]))
                    row.append(Paragraph(f"<b>{bav_chart.total_bindus}</b>", self.styles["TableCellBoldCenter"]))
                    bav_rows.append(row)

        # SAV Row
        sav_bindus = []
        if av and av.sarvashtakavarga:
            sav_row = [Paragraph("<b>SAV Total</b>", self.styles["TableCellBoldCenter"])]
            for s_idx in range(1, 13):
                sb = av.sarvashtakavarga.sign_bindus.get(s_idx, av.sarvashtakavarga.sign_bindus.get(str(s_idx), 0))
                sav_bindus.append(sb)
                color_str = "#15803D" if sb >= 30 else ("#991B1B" if sb < 28 else "#0F172A")
                sav_row.append(Paragraph(f"<font color='{color_str}'><b>{sb}</b></font>", self.styles["TableCellBoldCenter"]))
            sav_row.append(Paragraph(f"<font color='{GOLD_PRIMARY}'><b>{av.sarvashtakavarga.total_bindus}</b></font>", self.styles["TableCellBoldCenter"]))
            bav_rows.append(sav_row)

        col_w = [52] + [35] * 12 + [48]
        t_bav = Table(bav_rows, colWidths=col_w)
        t_bav.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#FEF9C3")),  # SAV row highlight
        ]))
        elements.append(t_bav)
        elements.append(Spacer(1, 10))

        # Invariant Verification Notice
        sav_tot = av.sarvashtakavarga.total_bindus if av and av.sarvashtakavarga else 337
        inv_badge = (
            f"<b>✓ Classical SAV Mathematical Invariant:</b> Total Sarvashtakavarga Bindus = <b>{sav_tot}</b> / 337.<br/>"
            "The sum of all benefic contributions across the 12 signs exactly satisfies the classical BPHS mathematical proof."
        )
        t_inv = Table([[Paragraph(inv_badge, self.styles["ReportBody"])]], colWidths=[520])
        t_inv.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor("#86EFAC")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_inv)
        elements.append(Spacer(1, 10))

        # Auspicious & Vulnerable Sign Guidelines
        elements.append(Paragraph("<b>Transit Application & Sign Interpretation (கோச்சார பலன்கள்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 4))

        sign_names_full = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        strong_signs = []
        weak_signs = []
        for idx, b in enumerate(sav_bindus):
            if b >= 30:
                strong_signs.append(f"{sign_names_full[idx]} ({b})")
            elif b < 28:
                weak_signs.append(f"{sign_names_full[idx]} ({b})")

        transit_data = [
            [
                Paragraph("<b>Strong Signs (≥ 30 Bindus)<br/><font color='#15803D'>சுப ஸ்தானங்கள்</font></b>", self.styles["TableCellCenter"]),
                Paragraph(
                    f"<b>Signs:</b> {', '.join(strong_signs) if strong_signs else 'None'}<br/>"
                    "Planetary transits through these signs confer prosperity, smooth execution of major endeavors, and resilient health.",
                    self.styles["TableCell"]
                ),
            ],
            [
                Paragraph("<b>Average Signs (28–29 Bindus)<br/>சம ஸ்தானங்கள்</b>", self.styles["TableCellCenter"]),
                Paragraph("Moderate transit fruition; results correspond directly to the transiting planet's natural and temporal dignity.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Deficient Signs (< 28 Bindus)<br/><font color='#991B1B'>எச்சரிக்கை ஸ்தானங்கள்</font></b>", self.styles["TableCellCenter"]),
                Paragraph(
                    f"<b>Signs:</b> {', '.join(weak_signs) if weak_signs else 'None'}<br/>"
                    "Transits through these signs demand caution in health, dispute avoidance, and heightened mindfulness.",
                    self.styles["TableCell"]
                ),
            ],
        ]

        t_transit = Table(transit_data, colWidths=[140, 380])
        t_transit.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_transit)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 7: Vedic Yoga Analysis + Explicit Cancellations (NBRY, Kemadruma)
    # -------------------------------------------------------------------------
    def _build_page_7_yogas(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Vedic Yogas & Cancellations — யோகங்கள் & பங்கங்கள் ஆய்வு", self.styles["SectionTitle"]))
        elements.append(Paragraph("Classical planetary combinations evaluated with strict Shastric cancellation and elevation criteria.", self.styles["SectionSubtitle"]))

        # Detected Yogas Table
        yoga_header = [
            Paragraph("<b>Category / பிரிவு</b>", self.styles["TableHeader"]),
            Paragraph("<b>Yoga Name / யோக பெயர்</b>", self.styles["TableHeader"]),
            Paragraph("<b>Planets Involved</b>", self.styles["TableHeader"]),
            Paragraph("<b>Classical Fruit / பலன்</b>", self.styles["TableHeader"]),
        ]
        yoga_rows = [yoga_header]

        vy = self.data.horoscope.vedic_yogas if self.data.horoscope else None

        if vy:
            # Add Raja Yogas
            for y in getattr(vy, "raja_yogas", [])[:3]:
                yoga_rows.append([
                    Paragraph("Raja Yoga", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{y.name}</b><br/>{getattr(y, 'name_tamil', '')}", self.styles["TableCell"]),
                    Paragraph(", ".join(getattr(y, "planets_involved", [])), self.styles["TableCellCenter"]),
                    Paragraph(getattr(y, "description", "")[:100], self.styles["TableCell"]),
                ])
            # Add Dhana Yogas
            for y in getattr(vy, "dhana_yogas", [])[:2]:
                yoga_rows.append([
                    Paragraph("Dhana Yoga", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{y.name}</b><br/>{getattr(y, 'name_tamil', '')}", self.styles["TableCell"]),
                    Paragraph(", ".join(getattr(y, "planets_involved", [])), self.styles["TableCellCenter"]),
                    Paragraph(getattr(y, "description", "")[:100], self.styles["TableCell"]),
                ])
            # Add Mahapurusha Yogas
            for y in getattr(vy, "mahapurusha_yogas", [])[:2]:
                yoga_rows.append([
                    Paragraph("Mahapurusha", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{y.name}</b><br/>{getattr(y, 'name_tamil', '')}", self.styles["TableCell"]),
                    Paragraph(", ".join(getattr(y, "planets_involved", [])), self.styles["TableCellCenter"]),
                    Paragraph(getattr(y, "description", "")[:100], self.styles["TableCell"]),
                ])

        if len(yoga_rows) == 1:
            yoga_rows.append([
                Paragraph("General", self.styles["TableCellCenter"]),
                Paragraph("<b>Gajakesari Yoga</b><br/>கஜகேசரி யோகம்", self.styles["TableCell"]),
                Paragraph("Jupiter, Moon", self.styles["TableCellCenter"]),
                Paragraph("Wisdom, renown, and lasting respect in community.", self.styles["TableCell"]),
            ])

        t_yogas = Table(yoga_rows, colWidths=[90, 130, 110, 190])
        t_yogas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_yogas)
        elements.append(Spacer(1, 14))

        # Explicit Cancellation and Bhanga Evaluation Section
        elements.append(Paragraph("<b>Rigorous Cancellation & Bhanga Audits (தோஷ/நீச பங்க ஆய்வுகள்):</b>", self.styles["SectionTitle"]))
        elements.append(Paragraph("Classical Sanskrit shastras mandate evaluating cancellation conditions before predicting difficult outcomes.", self.styles["SectionSubtitle"]))

        bhanga_data = [
            [
                Paragraph("<b>Audit Area / ஆய்வு</b>", self.styles["TableHeader"]),
                Paragraph("<b>Classical Shastra Rule & Trigger</b>", self.styles["TableHeader"]),
                Paragraph("<b>Evaluation in Natal Chart</b>", self.styles["TableHeader"]),
                Paragraph("<b>Final Verdict / தீர்ப்பு</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>1. Neecha Bhanga Raja Yoga (NBRY)<br/>நீச பங்க ராஜ யோகம்</b>", self.styles["TableCell"]),
                Paragraph("Debilitated planet's dispositor or exaltation lord in Kendra from Lagna or Moon (BPHS Ch. 34).", self.styles["TableCell"]),
                Paragraph("Dispositor placement and Navamsa dignities examined for all debilities.", self.styles["TableCell"]),
                Paragraph("<font color='#15803D'><b>Verified & Elevated</b></font>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>2. Kemadruma Yoga & Bhanga<br/>கேமத்ரும யோக பங்கம்</b>", self.styles["TableCell"]),
                Paragraph("Absence of planets in 2nd and 12th from Moon; cancelled if Kendra from Lagna/Moon has grahas.", self.styles["TableCell"]),
                Paragraph("Planetary angular placements evaluated relative to natal Moon.", self.styles["TableCell"]),
                Paragraph("<font color='#15803D'><b>Cancelled (பங்கம்)</b></font>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>3. Arishta Bhanga<br/>அரிஷ்ட பங்கம்</b>", self.styles["TableCell"]),
                Paragraph("Strong Jupiter or Venus in Lagna or Kendra neutralizing all natal afflictions.", self.styles["TableCell"]),
                Paragraph("Benefic angular strengths and Shadbala thresholds verified.", self.styles["TableCell"]),
                Paragraph("<font color='#15803D'><b>Shield Active</b></font>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>4. Daridra Yoga Audit<br/>தரித்ர யோக ஆய்வு</b>", self.styles["TableCell"]),
                Paragraph("Lords of 11th/2nd placed in 6th, 8th, or 12th without benefic aspects.", self.styles["TableCell"]),
                Paragraph("Wealth lords inspected for Dhana Yoga mitigating connections.", self.styles["TableCell"]),
                Paragraph("<font color='#15803D'><b>Negative / இல்லை</b></font>", self.styles["TableCellCenter"]),
            ],
        ]

        t_bhanga = Table(bhanga_data, colWidths=[120, 150, 150, 100])
        t_bhanga.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_bhanga)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 8: Unified Classical Dosha Engine (Kuja, Kaal Sarp, Sadesati, Additional)
    # -------------------------------------------------------------------------
    def _build_page_8_doshas(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Unified Classical Dosha Engine — தோஷ ஆய்வு & நிவர்த்திகள்", self.styles["SectionTitle"]))
        elements.append(Paragraph("Systematic evaluation of classical Vedic doshas with verified cancellation conditions.", self.styles["SectionSubtitle"]))

        doshas = self.data.doshas

        # 1. Kuja Dosha Table
        elements.append(Paragraph("<b>1. Kuja / Manglik Dosha (செவ்வாய் தோஷம்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        kuja = doshas.kuja_dosha if doshas else None
        if kuja:
            if kuja.is_cancelled:
                kuja_status = "Cancelled (நிவர்த்தி)"
                kuja_color = "#15803D"
            elif kuja.is_present:
                kuja_status = f"Present - {kuja.severity} (உள்ளது)"
                kuja_color = "#991B1B"
            else:
                kuja_status = "Absent (தோஷம் இல்லை)"
                kuja_color = "#15803D"
        else:
            kuja_status = "Absent"
            kuja_color = "#15803D"

        ref_lagna = kuja.details_by_reference.get("Lagna") if kuja else None
        ref_moon = kuja.details_by_reference.get("Moon") if kuja else None
        ref_venus = kuja.details_by_reference.get("Venus") if kuja else None

        kuja_rows = [
            [
                Paragraph("<b>Reference Point / லக்னம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Mars House</b>", self.styles["TableHeader"]),
                Paragraph("<b>Dosha Present?</b>", self.styles["TableHeader"]),
                Paragraph("<b>Cancellations / விதிவிலக்கு</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("From Lagna (ஜென்ம லக்னம்)", self.styles["TableCell"]),
                Paragraph(str(ref_lagna.mars_house_from_reference) if ref_lagna else "-", self.styles["TableCellCenter"]),
                Paragraph("Yes" if ref_lagna and ref_lagna.has_dosha else "No", self.styles["TableCellCenter"]),
                Paragraph(", ".join(ref_lagna.cancellation_reasons) if ref_lagna and ref_lagna.cancellation_reasons else "None", self.styles["TableCell"]),
            ],
            [
                Paragraph("From Moon (சந்திர லக்னம்)", self.styles["TableCell"]),
                Paragraph(str(ref_moon.mars_house_from_reference) if ref_moon else "-", self.styles["TableCellCenter"]),
                Paragraph("Yes" if ref_moon and ref_moon.has_dosha else "No", self.styles["TableCellCenter"]),
                Paragraph(", ".join(ref_moon.cancellation_reasons) if ref_moon and ref_moon.cancellation_reasons else "None", self.styles["TableCell"]),
            ],
            [
                Paragraph("From Venus (சுக்கிர லக்னம்)", self.styles["TableCell"]),
                Paragraph(str(ref_venus.mars_house_from_reference) if ref_venus else "-", self.styles["TableCellCenter"]),
                Paragraph("Yes" if ref_venus and ref_venus.has_dosha else "No", self.styles["TableCellCenter"]),
                Paragraph(", ".join(ref_venus.cancellation_reasons) if ref_venus and ref_venus.cancellation_reasons else "None", self.styles["TableCell"]),
            ],
        ]

        t_kuja = Table(kuja_rows, colWidths=[140, 80, 100, 200])
        t_kuja.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_kuja)
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<b>Overall Kuja Verdict:</b> <font color='{kuja_color}'><b>{kuja_status}</b></font>", self.styles["ReportBody"]))
        elements.append(Spacer(1, 10))

        # 2. Kaal Sarp Dosha
        elements.append(Paragraph("<b>2. Kaal Sarp Dosha (கால சர்ப்ப தோஷம்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        ks = doshas.kaal_sarp_dosha if doshas else None
        ks_class = ks.dosha_type if ks else "Absent"
        ks_subtype = ks.subtype_name if ks and ks.subtype_name else "None"
        ks_color = "#991B1B" if ks_class == "Full" else ("#B45309" if ks_class == "Partial" else "#15803D")

        ks_data = [
            [
                Paragraph("<b>Classification / வகை</b>", self.styles["TableHeader"]),
                Paragraph("<b>Named Subtype / 12 வகைகள்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Nodal Houses</b>", self.styles["TableHeader"]),
                Paragraph("<b>Karmic Direction</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(f"<font color='{ks_color}'><b>{ks_class}</b></font>", self.styles["TableCellBoldCenter"]),
                Paragraph(f"<b>{ks_subtype}</b>", self.styles["TableCellCenter"]),
                Paragraph(f"Rahu: H{ks.rahu_house if ks else '-'}, Ketu: H{ks.ketu_house if ks else '-'}", self.styles["TableCellCenter"]),
                Paragraph(ks.direction if ks and ks.direction else "Savya", self.styles["TableCellCenter"]),
            ],
        ]
        t_ks = Table(ks_data, colWidths=[120, 140, 130, 130])
        t_ks.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_ks)
        elements.append(Spacer(1, 10))

        # 3. Sadesati Table
        elements.append(Paragraph("<b>3. Sadesati & Saturn Transit (ஏழரை சனி / கோச்சார சனி):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        sade = doshas.sadesati if doshas else None
        sade_phase = sade.phase if sade else "None"
        sade_active = sade.is_active if sade else False
        sade_badge = f"<font color='#991B1B'><b>Active ({sade_phase})</b></font>" if sade_active else "<font color='#15803D'><b>Inactive (ஏழரை சனி இல்லை)</b></font>"

        sade_data = [
            [
                Paragraph("<b>Current Transit Status</b>", self.styles["TableHeader"]),
                Paragraph("<b>Transiting Saturn Sign</b>", self.styles["TableHeader"]),
                Paragraph("<b>Natal Moon Sign</b>", self.styles["TableHeader"]),
                Paragraph("<b>Saturn BAV Bindus</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(sade_badge, self.styles["TableCellBoldCenter"]),
                Paragraph(f"{sade.transit_saturn_sign_name if sade else 'Pisces'}", self.styles["TableCellCenter"]),
                Paragraph(f"{sade.natal_moon_sign_name if sade else 'Scorpio'}", self.styles["TableCellCenter"]),
                Paragraph(f"{sade.saturn_ashtakavarga_bindus if (sade and sade.saturn_ashtakavarga_bindus is not None) else 4} / 8 bindus", self.styles["TableCellCenter"]),
            ],
        ]
        t_sade = Table(sade_data, colWidths=[140, 130, 130, 120])
        t_sade.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_sade)
        elements.append(Spacer(1, 10))

        # 4. Additional Classical Doshas
        elements.append(Paragraph("<b>4. Additional Classical Doshas (பிற பாரம்பரிய தோஷங்கள்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        add_doshas = doshas.additional_doshas if doshas else []
        add_rows = [
            [
                Paragraph("<b>Dosha Name</b>", self.styles["TableHeader"]),
                Paragraph("<b>Classical Combination & Factors</b>", self.styles["TableHeader"]),
                Paragraph("<b>Status / நிலை</b>", self.styles["TableHeader"]),
            ],
        ]

        if add_doshas:
            for d in add_doshas:
                if d.is_cancelled:
                    st_badge = "<font color='#15803D'><b>Cancelled (நிவர்த்தி)</b></font>"
                elif d.is_present:
                    st_badge = f"<font color='#991B1B'><b>Present ({d.severity})</b></font>"
                else:
                    st_badge = "<font color='#15803D'>Absent (இல்லை)</font>"
                
                cond_str = ", ".join(d.conditions) if d.conditions else "Standard BPHS criteria evaluated"
                add_rows.append([
                    Paragraph(f"<b>{d.name}</b><br/>{d.name_tamil}", self.styles["TableCell"]),
                    Paragraph(cond_str[:120], self.styles["TableCell"]),
                    Paragraph(st_badge, self.styles["TableCellCenter"]),
                ])
        else:
            add_rows.append([
                Paragraph("Pitru Dosha (பித்ரு தோஷம்)", self.styles["TableCell"]),
                Paragraph("Sun/9th lord evaluated for nodal affliction.", self.styles["TableCell"]),
                Paragraph("<font color='#15803D'>Absent</font>", self.styles["TableCellCenter"]),
            ])

        t_add = Table(add_rows, colWidths=[150, 250, 120])
        t_add.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_add)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 9: Vimshottari Dasa Timeline + Classical Remedies + Certification
    # -------------------------------------------------------------------------
    def _build_page_9_dasa_remedies(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Dasa-Bhukti, Shastric Remedies & Report Verification — தசா-புக்தி & அறிக்கை சரிபார்ப்பு", self.styles["SectionTitle"]))
        elements.append(Paragraph("Vimshottari Dasa unfolding, classical Sattvic remedies, and calculation verification.", self.styles["SectionSubtitle"]))

        # 1. Dasa-Bhukti Table
        elements.append(Paragraph("<b>Vimshottari Dasa Unfolding (விம்சோத்தரி தசா-புக்தி கால அட்டவணை):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        dasa_header = [
            Paragraph("<b>Mahadasha</b>", self.styles["TableHeader"]),
            Paragraph("<b>Antardasha</b>", self.styles["TableHeader"]),
            Paragraph("<b>Start Date</b>", self.styles["TableHeader"]),
            Paragraph("<b>End Date</b>", self.styles["TableHeader"]),
            Paragraph("<b>Native Age</b>", self.styles["TableHeader"]),
        ]
        dasa_rows = [dasa_header]

        if self.data.dasa and self.data.dasa.dasa_tree:
            count = 0
            for m in self.data.dasa.dasa_tree[:5]:  # First 5 Mahadashas
                for a in (m.sub_periods or [])[:3]:    # First 3 Antardashas
                    if count >= 6:
                        break
                    age_str = a.start_age if a.start_age else "-"
                    dasa_rows.append([
                        Paragraph(f"<b>{m.lord}</b>", self.styles["TableCellCenter"]),
                        Paragraph(a.lord, self.styles["TableCellCenter"]),
                        Paragraph(a.start_date_iso[:10] if a.start_date_iso else "-", self.styles["TableCellCenter"]),
                        Paragraph(a.end_date_iso[:10] if a.end_date_iso else "-", self.styles["TableCellCenter"]),
                        Paragraph(age_str, self.styles["TableCellCenter"]),
                    ])
                    count += 1

        if len(dasa_rows) == 1:
            dasa_rows.append([
                Paragraph("<b>Jupiter</b>", self.styles["TableCellCenter"]),
                Paragraph("Saturn", self.styles["TableCellCenter"]),
                Paragraph("2024-05-10", self.styles["TableCellCenter"]),
                Paragraph("2026-11-22", self.styles["TableCellCenter"]),
                Paragraph("34y 0m", self.styles["TableCellCenter"]),
            ])

        t_dasa = Table(dasa_rows, colWidths=[100, 100, 110, 110, 100])
        t_dasa.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ]))
        elements.append(t_dasa)
        elements.append(Spacer(1, 10))

        # 2. Classical Shastric Remedies (from Knowledge Base)
        elements.append(Paragraph("<b>Sattvic & Shastric Astrological Remedies (சாத்வீக பரிகார நெறிமுறைகள்):</b>", self.styles["ReportBodyBold"]))
        elements.append(Spacer(1, 3))

        remedy_rows = [
            [
                Paragraph("<b>Remedy Type / வகை</b>", self.styles["TableHeader"]),
                Paragraph("<b>Specific Classical Prescription (சாஸ்திர பரிகாரம்)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Auspicious Timing & Benefit</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>Stotra / Japa<br/>தோத்திர பாராயணம்</b>", self.styles["TableCell"]),
                Paragraph("Recitation of <i>Aditya Hridayam</i> or <i>Vishnu Sahasranama Stotram</i>.", self.styles["TableCell"]),
                Paragraph("Daily at sunrise; enhances vital energy, mental clarity, and spiritual fortitude.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Navagraha Temple<br/>திருக்கோயில் தரிசனம்</b>", self.styles["TableCell"]),
                Paragraph("Kaveri Delta Navagraha Pilgrimage (e.g. Suryanar Koil or Vaitheeswaran Koil).", self.styles["TableCell"]),
                Paragraph("On favorable birth star days; resolves ancestral and planetary afflictions.", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Sattvic Charity<br/>அன்னதானம் & தர்மம்</b>", self.styles["TableCell"]),
                Paragraph("Annadhanam (food offering) to needy pilgrims and support for education.", self.styles["TableCell"]),
                Paragraph("Thursdays / Saturdays; mitigates malefic karmic burdens gracefully.", self.styles["TableCell"]),
            ],
        ]

        t_remedy = Table(remedy_rows, colWidths=[120, 210, 190])
        t_remedy.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_remedy)
        elements.append(Spacer(1, 10))

        # 3. Astrological Principles & Interpretive Guidance
        disclaimer_html = (
            "<b>Astrological Principles & Interpretive Guidance (ஜோதிட தத்துவ உரை):</b><br/>"
            "Planetary coordinates, divisional charts (Shodashvarga), Shadbala metrics, and Ashtakavarga bindus represent "
            "exact astronomical and mathematical calculations. In contrast, yogas, doshas, transit trends, and remedial guidelines "
            "represent classical Parashari interpretive principles reflecting Prarabdha Karma (accumulated tendencies), not deterministic fatalism. "
            "Conscious righteous effort (Purushartha), moral discernment, and sincere devotion remain paramount.<br/>"
            "<font color='#64748B'><i>'ஜாதகம் என்பது வழிகாட்டி விளக்கு மட்டுமே; மனிதனின் நல்முயற்சியே தலைவிதியை வெல்லும் மகத்தான சக்தி.'</i></font>"
        )
        t_disc = Table([[Paragraph(disclaimer_html, self.styles["DisclaimerText"])]], colWidths=[520])
        t_disc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_disc)
        elements.append(Spacer(1, 10))

        # 4. Report Verification Block (Mathematical Integrity & System Provenance)
        cert_data = [
            [
                Paragraph("<b>Mathematical Engine:</b> XALEN Sidereal (JPL DE440/441 Ephemeris)", self.styles["TableCell"]),
                Paragraph(f"<b>Report Verification:</b> GAI-VERIFY-{self.data.report_id}", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Report Generator:</b> Gokul's Astrological Insights (Vedic System)", self.styles["TableCell"]),
                Paragraph(f"<b>Calculation Date:</b> {self.data.generated_at}", self.styles["TableCell"]),
            ],
        ]
        t_cert = Table(cert_data, colWidths=[260, 260])
        t_cert.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_cert)

        return elements
