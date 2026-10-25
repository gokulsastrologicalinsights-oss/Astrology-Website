"""ReportLab KP (Krishnamurti Paddhati) Astrology PDF Report Generator.

Compiles a dedicated, branded, non-spillable 6-page comprehensive KP report in
English and Tamil for Gokul's Astrological Insights.

Uses ReportLab with NotoSansTamil TrueType fonts, vector South Indian charts (KP Rasi
and KP Bhava Chalit), 4-tier ABCD significators, ruling planets, and 5-level Vimshottari dasa.
"""

from io import BytesIO
import logging
from typing import Dict, Any, List, Optional
import hashlib

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
from app.services.pdf_report_engine.kp_chart_drawer import create_kp_rasi_chart, create_kp_bhava_chart
from app.services.pdf_report_engine.kp_data_builder import KpReportData

logger = logging.getLogger("gai.pdf.kp_generator")

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
    "Lagna": "லக்னம்",
}

SIGN_NAMES_TA: Dict[str, str] = {
    "Aries": "மேஷம்",
    "Taurus": "ரிஷபம்",
    "Gemini": "மிதுனம்",
    "Cancer": "கடகம்",
    "Leo": "சிம்மம்",
    "Virgo": "கன்னி",
    "Libra": "துலாம்",
    "Scorpio": "விருச்சிகம்",
    "Sagittarius": "தனுசு",
    "Capricorn": "மகரம்",
    "Aquarius": "கும்பம்",
    "Pisces": "மீனம்",
}

BHAVA_NAMES_TA: Dict[int, str] = {
    1: "லக்னம் (உடல், ஆயுள்)",
    2: "தனம், குடும்பம், வாக்கு",
    3: "தைரியம், இளைய சகோதரம்",
    4: "தாய், சுகம், சொத்து",
    5: "புத்திரம், அறிவு, பூர்வபுண்ணியம்",
    6: "ருணம், ரோகம், சத்ரு",
    7: "களத்திரம், கூட்டாண்மை",
    8: "ஆயுள், அஷ்டமம், தடைகள்",
    9: "பாக்யம், தந்தை, உயர் கல்வி",
    10: "கர்மம், ஜீவனம், பதவி",
    11: "லாபம், மூத்த சகோதரம், ஆசைகள்",
    12: "விரயம், மோட்சம், வெளிநாடு",
}

BHAVA_NAMES_EN: Dict[int, str] = {
    1: "1st (Health, Longevity, Self)",
    2: "2nd (Wealth, Family, Speech)",
    3: "3rd (Courage, Siblings, Travel)",
    4: "4th (Mother, Property, Assets)",
    5: "5th (Progeny, Mind, Romance)",
    6: "6th (Service, Debts, Disease)",
    7: "7th (Spouse, Partnership)",
    8: "8th (Longevity, Obstacles, Surprises)",
    9: "9th (Fortune, Father, Higher Studies)",
    10: "10th (Profession, Public Standing)",
    11: "11th (Gains, Desires, Friends)",
    12: "12th (Expenses, Foreign, Moksha)",
}


def _format_dms(deg_val: float) -> str:
    """Format decimal degrees to DD° MM' SS\"."""
    norm = deg_val % 30.0
    deg = int(norm)
    rem = (norm - deg) * 60.0
    mins = int(rem)
    secs = int(round((rem - mins) * 60.0))
    if secs >= 60:
        secs = 0
        mins += 1
    if mins >= 60:
        mins = 0
        deg += 1
    return f"{deg:02d}° {mins:02d}' {secs:02d}\""


class KpNumberedCanvas(canvas.Canvas):
    """Two-pass canvas that writes dynamic total page count and KP running headers."""

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

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 7.5)
            except Exception:
                self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(GOLD_PRIMARY)
            self.drawString(
                MARGIN,
                PAGE_HEIGHT - 26,
                reorder_tamil_for_pdf("Gokul's Astrological Insights | கிருஷ்ணமூர்த்தி பத்ததி (KP) அறிக்கை"),
            )

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(
                PAGE_WIDTH - MARGIN,
                PAGE_HEIGHT - 26,
                "KP Astrology Report • Sub-Lord Arbiter • Confidential",
            )

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
        self.drawString(
            MARGIN,
            18,
            "© Gokul's Astrological Insights • Powered by Swiss Ephemeris & XALEN Astronomical Engine • Verified KP System",
        )

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, page_str)

        self.restoreState()


class KpPdfReportGenerator:
    """Orchestrates building all 6 pages of the branded KP astrology report."""

    def __init__(self, data: KpReportData):
        self.data = data
        self.styles = get_report_styles()
        self.lang = data.language

    def generate(self) -> bytes:
        """Generates the 6-page KP PDF document and returns the byte array."""
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

        # 1. Cover, Native/Horary Details, Ephemeris & Panchang
        story.extend(self._build_page_1_cover())
        story.append(PageBreak())

        # 2. Dual KP Vector Charts (Rasi & Bhava Chalit) & 9 Grahas Table
        story.extend(self._build_page_2_charts_planets())
        story.append(PageBreak())

        # 3. 12 Placidus House Cusps & Cuspal Sub-Lord (CSL) House Promise Arbiter
        story.extend(self._build_page_3_cusps_csl())
        story.append(PageBreak())

        # 4. 4-Tier ABCD House Significators (Bhaav Nirdeshan) & Planet-wise Significators
        story.extend(self._build_page_4_significators())
        story.append(PageBreak())

        # 5. Ruling Planets (RP) & 5-Level Vimshottari Dasa Hierarchy
        story.extend(self._build_page_5_ruling_planets_dasa())
        story.append(PageBreak())

        # 6. KP Life Event Matrix, Remedial Directives & Official Certification
        story.extend(self._build_page_6_event_matrix_certification())

        doc.build(story, canvasmaker=KpNumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------------------
    # PAGE 1: Brand Cover, Particulars, Ephemeris Calibration & Panchang
    # -------------------------------------------------------------------------
    def _build_page_1_cover(self) -> List[Any]:
        elements: List[Any] = []

        # Header Banner
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("GOKUL'S ASTROLOGICAL INSIGHTS", self.styles["BrandHeader"]))
        sub_title = (
            "கிருஷ்ணமூர்த்தி பத்ததி (KP) ஜோதிட அறிக்கை | Advanced KP Astrology Report"
            if self.lang == "ta"
            else "Advanced Krishnamurti Paddhati (KP) Astrology Report | கிருஷ்ணமூர்த்தி பத்ததி"
        )
        elements.append(Paragraph(sub_title, self.styles["BrandSubHeader"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=GOLD_PRIMARY, spaceBefore=2, spaceAfter=10))

        # Particulars Section Header
        is_horary = self.data.chart_type == "horary"
        if is_horary:
            section_hdr = "KP Horary Prashna Particulars — கே.பி. பிரசன்ன விவரங்கள் (1–249)"
            section_sub = "Authentic Krishnamurti Paddhati horary chart erected with ARMC inversion and true obliquity."
        else:
            section_hdr = "Native Birth Particulars — ஜாதகர் பிறப்பு விவரங்கள்"
            section_sub = "Astrological birth coordinates and astronomical calibration for Krishnamurti Paddhati evaluation."

        elements.append(Paragraph(section_hdr, self.styles["SectionTitle"]))
        elements.append(Paragraph(section_sub, self.styles["SectionSubtitle"]))

        # Table: Particulars
        verified_text = "✓ Verified KP Engine" if self.data.is_verified else "⚠ Unverified Coordinates"
        verified_color = "#15803D" if self.data.is_verified else "#B45309"

        if is_horary:
            q_display = self.data.question_text or "General Prashna Consultation"
            h_num_str = f"#{self.data.horary_number}" if self.data.horary_number else "N/A"
            info_data = [
                [
                    Paragraph("<b>Querent Name / பெயர்:</b>", self.styles["TableCell"]),
                    Paragraph(f"<b>{self.data.native_name}</b>", self.styles["TableCell"]),
                    Paragraph("<b>Horary Number / எண்:</b>", self.styles["TableCell"]),
                    Paragraph(f"<font color='#B8860B'><b>{h_num_str} (1–249)</b></font>", self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Question / கேள்வி:</b>", self.styles["TableCell"]),
                    Paragraph(f"<i>{q_display}</i>", self.styles["TableCell"]),
                    Paragraph("<b>Chart Type / முறை:</b>", self.styles["TableCell"]),
                    Paragraph("KP Horary Prashna", self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Query Date / தேதி:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.birth_date, self.styles["TableCell"]),
                    Paragraph("<b>Query Time / நேரம்:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.birth_time, self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Coordinates / அமைவிடம்:</b>", self.styles["TableCell"]),
                    Paragraph(f"{self.data.latitude:.4f}°N, {self.data.longitude:.4f}°E", self.styles["TableCell"]),
                    Paragraph("<b>Timezone / நேர வலயம்:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.timezone_str, self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Report ID / அறிக்கை எண்:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.report_id, self.styles["TableCell"]),
                    Paragraph("<b>Engine Status / நிலை:</b>", self.styles["TableCell"]),
                    Paragraph(f"<font color='{verified_color}'><b>{verified_text}</b></font>", self.styles["TableCell"]),
                ],
            ]
        else:
            info_data = [
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
                    Paragraph("<b>Location / இடம்:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.location_name, self.styles["TableCell"]),
                    Paragraph("<b>Chart Type / முறை:</b>", self.styles["TableCell"]),
                    Paragraph("KP Natal Horoscope", self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Report ID / அறிக்கை எண்:</b>", self.styles["TableCell"]),
                    Paragraph(self.data.report_id, self.styles["TableCell"]),
                    Paragraph("<b>Engine Status / நிலை:</b>", self.styles["TableCell"]),
                    Paragraph(f"<font color='{verified_color}'><b>{verified_text}</b></font>", self.styles["TableCell"]),
                ],
            ]

        t_info = Table(info_data, colWidths=[120, 140, 120, 140])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 10))

        # Horary Division Card (if Horary)
        if is_horary and self.data.horary_division:
            hd = self.data.horary_division
            h_card_data = [
                [
                    Paragraph("<b>Horary Seed Arc / பாகை:</b>", self.styles["TableCell"]),
                    Paragraph(f"{hd.get('start_degree', 0.0):.2f}° — {hd.get('end_degree', 0.0):.2f}°", self.styles["TableCell"]),
                    Paragraph("<b>Sign & Lord / ராசி:</b>", self.styles["TableCell"]),
                    Paragraph(f"{hd.get('sign', '')} ({hd.get('sign_lord', '')})", self.styles["TableCell"]),
                ],
                [
                    Paragraph("<b>Star & Lord / நட்சத்திரம்:</b>", self.styles["TableCell"]),
                    Paragraph(f"{hd.get('star', '')} ({hd.get('star_lord', '')})", self.styles["TableCell"]),
                    Paragraph("<b>Sub-Lord (CSL) / உப அதிபதி:</b>", self.styles["TableCell"]),
                    Paragraph(f"<font color='#8B6914'><b>{hd.get('sub_lord', '')}</b></font>", self.styles["TableCell"]),
                ],
            ]
            t_hcard = Table(h_card_data, colWidths=[130, 130, 130, 130])
            t_hcard.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
                ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FDE68A")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t_hcard)
            elements.append(Spacer(1, 10))

        # Astronomical & KP Calibration Table
        elements.append(Paragraph("Astronomical & Ephemeris Calibration — வானியல் கணித அளவீடுகள்", self.styles["SectionTitle"]))
        deg_int = int(self.data.ayanamsa_deg)
        rem_m = (self.data.ayanamsa_deg - deg_int) * 60.0
        min_int = int(rem_m)
        sec_int = int(round((rem_m - min_int) * 60.0))
        ayanamsa_dms = f"{deg_int:02d}° {min_int:02d}' {sec_int:02d}\""

        astro_data = [
            [
                Paragraph("<b>KP Ayanamsa / அயனாம்சம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>House System / பாவக முறை</b>", self.styles["TableHeader"]),
                Paragraph("<b>Julian Day (UT1) / ஜூலியன் நாள்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Ephemeris Engine / எஞ்சின்</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(f"{self.data.ayanamsa_name}<br/><font color='#8B6914'><b>{ayanamsa_dms}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(f"{self.data.house_system_name}<br/>(Placidus Semi-Arc)", self.styles["TableCellCenter"]),
                Paragraph(f"{self.data.julian_day_ut1:.4f}", self.styles["TableCellCenter"]),
                Paragraph("Swiss Ephemeris & XALEN<br/>(Sub-arcsecond precision)", self.styles["TableCellCenter"]),
            ],
        ]
        t_astro = Table(astro_data, colWidths=[140, 125, 125, 130])
        t_astro.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_astro)
        elements.append(Spacer(1, 10))

        # Panchang Table (5 Limbs)
        elements.append(Paragraph("Birth / Query Panchang — பஞ்சாங்க விவரங்கள் (Five Limbs of Time)", self.styles["SectionTitle"]))
        p = self.data.panchang or {}
        tithi_display = f"{p.get('tithi_paksha', '')} {p.get('tithi_name', 'Sukla Prathama')}".strip() or "Sukla Prathama"
        vara_display = p.get("vara", "Somavara")
        nak_display = p.get("nakshatra", "Aswini")
        yoga_display = p.get("yoga", "Siddha")
        karana_display = p.get("karana", "Bava")

        panchang_data = [
            [
                Paragraph("<b>Panchang Limb / அங்கம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Value / மதிப்பு</b>", self.styles["TableHeader"]),
                Paragraph("<b>Tamil Name / தமிழாக்கம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>KP Signification / காரகத்துவம்</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>1. Tithi (திதி)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(tithi_display, self.styles["TableCellCenter"]),
                Paragraph("திதி (சந்திர நிலை)", self.styles["TableCellCenter"]),
                Paragraph("Jala / நீர் (Mental State & Harmony)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>2. Vara (வாரம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(vara_display, self.styles["TableCellCenter"]),
                Paragraph("வாரம் (கிழமை நாதன்)", self.styles["TableCellCenter"]),
                Paragraph("Agni / நெருப்பு (Ruling Planet Day Lord)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>3. Nakshatra (நட்சத்திரம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(nak_display, self.styles["TableCellCenter"]),
                Paragraph("நட்சத்திரம் (ஜென்ம தாரை)", self.styles["TableCellCenter"]),
                Paragraph("Vayu / காற்று (Vimshottari Dasa Balance)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>4. Yoga (யோகம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(yoga_display, self.styles["TableCellCenter"]),
                Paragraph("நித்திய யோகம்", self.styles["TableCellCenter"]),
                Paragraph("Akasha / ஆகாயம் (Spiritual Concordance)", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>5. Karana (கரணம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(karana_display, self.styles["TableCellCenter"]),
                Paragraph("கரணம் (செயல் திறன்)", self.styles["TableCellCenter"]),
                Paragraph("Prithvi / நிலம் (Material Accomplishment)", self.styles["TableCellCenter"]),
            ],
        ]
        t_panch = Table(panchang_data, colWidths=[120, 130, 130, 140])
        t_panch.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(t_panch)
        elements.append(Spacer(1, 10))

        # KP Core Aphorism Box
        kp_axiom_text = (
            "<b>கிருஷ்ணமூர்த்தி பத்ததி தங்க விதி (KP Golden Axiom):</b><br/>"
            "<i>\"கிரகம் சுட்டிக்காட்டும்; சாரநாதன் ஆற்றலைத் தரும்; உப அதிபதியே பலனைத் தீர்மானிக்கும்.\"</i><br/>"
            "\"A planet proposes, the star lord channels energy, but the Cuspal Sub-Lord (CSL) is the sole decider of fructification.\""
        )
        t_axiom = Table([[Paragraph(kp_axiom_text, self.styles["TamilShloka"])]], colWidths=[520])
        t_axiom.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_axiom)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 2: Dual KP Vector Charts (Rasi & Bhava Chalit) & 9 Grahas Table
    # -------------------------------------------------------------------------
    def _build_page_2_charts_planets(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("KP Charts & Planetary Longitudes — ராசி மற்றும் பாவ கட்டங்கள்", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Dual vector display: KP Nirayana Rasi Chart (left) and Placidus Bhava Chalit Chart (right) showing cusp boundaries.",
            self.styles["SectionSubtitle"],
        ))

        # Ascendant sign & degree
        asc_sign = 1
        asc_deg = 0.0
        for c in self.data.cuspal_analysis:
            if c.get("house") == 1:
                asc_sign = c.get("sign_index", 1)
                asc_deg = c.get("cusp_degree", 0.0) % 30.0
                break

        # Chart 1: KP Rasi Chart
        rasi_data = {
            "ascendant_sign": asc_sign,
            "ascendant_degree": asc_deg,
            "planets": [
                {
                    "name": p.get("planet", ""),
                    "sign_index": p.get("sign_index", 1),
                    "degree_in_sign": (p.get("longitude", 0.0) % 30.0),
                    "is_retrograde": False,
                }
                for p in self.data.planetary_positions
            ],
        }
        chart_rasi = create_kp_rasi_chart(
            chart_data=rasi_data,
            title_en="KP RASI CHART",
            title_ta="நிராயண ராசி",
            size=195.0,
            language=self.lang,
        )

        # Chart 2: KP Bhava Chalit Chart
        chart_bhava = create_kp_bhava_chart(
            cusp_data=self.data.cuspal_analysis,
            planet_data=self.data.planetary_positions,
            title_en="KP BHAVA CHALIT",
            title_ta="பாவ சலனம் (பிளாசிடஸ்)",
            size=195.0,
            language=self.lang,
        )

        charts_table = Table([[chart_rasi, chart_bhava]], colWidths=[255, 255])
        charts_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(charts_table)
        elements.append(Spacer(1, 10))

        # 9 Grahas KP Sidereal Coordinates Table
        elements.append(Paragraph("Planetary Coordinates & KP Sub-Divisions — 9 கிரகங்களின் கே.பி. உப நிலைகள்", self.styles["SectionTitle"]))

        planet_rows: List[List[Any]] = [
            [
                Paragraph("<b>Graha / கிரகம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Longitude / பாகை</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign / ராசி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign Lord / அதிபதி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Star Lord / சாரம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sub-Lord / உப நாதன்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sub-Sub / உப-உப</b>", self.styles["TableHeader"]),
                Paragraph("<b>KP #</b>", self.styles["TableHeader"]),
            ]
        ]

        # Add Ascendant row first
        for c in self.data.cuspal_analysis:
            if c.get("house") == 1:
                deg_str = _format_dms(c.get("cusp_degree", 0.0))
                s_name = c.get("sign_name", "")
                s_name_disp = SIGN_NAMES_TA.get(s_name, s_name) if self.lang == "ta" else s_name
                planet_rows.append([
                    Paragraph("<font color='#991B1B'><b>Asc / லக்னம்</b></font>", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{deg_str}</b>", self.styles["TableCellCenter"]),
                    Paragraph(s_name_disp, self.styles["TableCellCenter"]),
                    Paragraph(c.get("sign_lord", ""), self.styles["TableCellCenter"]),
                    Paragraph(c.get("star_lord", ""), self.styles["TableCellCenter"]),
                    Paragraph(f"<font color='#8B6914'><b>{c.get('sub_lord', '')}</b></font>", self.styles["TableCellCenter"]),
                    Paragraph(c.get("sub_sub_lord", "") or "—", self.styles["TableCellCenter"]),
                    Paragraph("—", self.styles["TableCellCenter"]),
                ])
                break

        # Add 9 Grahas
        for p in self.data.planetary_positions:
            p_name = p.get("planet", "")
            p_disp = f"{p_name} ({GRAHA_NAMES_TA.get(p_name, '')})" if self.lang == "ta" else p_name
            deg_str = _format_dms(p.get("longitude", 0.0))
            s_name = p.get("sign_name", "")
            s_name_disp = SIGN_NAMES_TA.get(s_name, s_name) if self.lang == "ta" else s_name
            kp_num = f"#{p.get('kp_number', '')}"

            planet_rows.append([
                Paragraph(f"<b>{p_disp}</b>", self.styles["TableCellCenter"]),
                Paragraph(deg_str, self.styles["TableCellCenter"]),
                Paragraph(s_name_disp, self.styles["TableCellCenter"]),
                Paragraph(p.get("sign_lord", ""), self.styles["TableCellCenter"]),
                Paragraph(p.get("star_lord", ""), self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#8B6914'><b>{p.get('sub_lord', '')}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#1E40AF'>{p.get('sub_sub_lord', '')}</font>", self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#15803D'><b>{kp_num}</b></font>", self.styles["TableCellCenter"]),
            ])

        t_planets = Table(planet_rows, colWidths=[85, 75, 65, 60, 60, 65, 65, 45])
        t_planets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3.2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.2),
        ]))
        elements.append(t_planets)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 3: 12 Placidus House Cusps & Cuspal Sub-Lord (CSL) House Promise Arbiter
    # -------------------------------------------------------------------------
    def _build_page_3_cusps_csl(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("12 Placidus House Cusps — 12 பாவங்களின் ஆரம்ப பாகைகள்", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Exact Placidus semi-arc cusp longitudes, sign lords, star lords, and Cuspal Sub-Lords (CSL).",
            self.styles["SectionSubtitle"],
        ))

        cusp_rows: List[List[Any]] = [
            [
                Paragraph("<b>Cusp / பாவம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Longitude / பாகை</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign / ராசி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign Lord / அதிபதி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Star Lord / சாரம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sub-Lord (CSL) / உப அதிபதி</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sub-Sub / உப-உப</b>", self.styles["TableHeader"]),
                Paragraph("<b>Promise / பலன்</b>", self.styles["TableHeader"]),
            ]
        ]

        for c in self.data.cuspal_analysis:
            h_num = c.get("house", 1)
            deg_str = _format_dms(c.get("cusp_degree", 0.0))
            s_name = c.get("sign_name", "")
            s_name_disp = SIGN_NAMES_TA.get(s_name, s_name) if self.lang == "ta" else s_name
            promise = c.get("promise", "Mixed")

            if promise == "Positive":
                p_color = "#15803D"
                p_text = "Positive / நற்பலன்" if self.lang == "ta" else "Positive"
            elif promise == "Negative":
                p_color = "#991B1B"
                p_text = "Negative / தடை" if self.lang == "ta" else "Negative"
            else:
                p_color = "#475569"
                p_text = "Mixed / கலவை" if self.lang == "ta" else "Mixed"

            cusp_rows.append([
                Paragraph(f"<b>Cusp {h_num}</b>", self.styles["TableCellCenter"]),
                Paragraph(deg_str, self.styles["TableCellCenter"]),
                Paragraph(s_name_disp, self.styles["TableCellCenter"]),
                Paragraph(c.get("sign_lord", ""), self.styles["TableCellCenter"]),
                Paragraph(c.get("star_lord", ""), self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#8B6914'><b>{c.get('sub_lord', '')}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(c.get("sub_sub_lord", "") or "—", self.styles["TableCellCenter"]),
                Paragraph(f"<font color='{p_color}'><b>{p_text}</b></font>", self.styles["TableCellCenter"]),
            ])

        t_cusps = Table(cusp_rows, colWidths=[60, 75, 65, 60, 60, 80, 60, 60])
        t_cusps.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.8),
        ]))
        elements.append(t_cusps)
        elements.append(Spacer(1, 10))

        # CSL 12-Bhava Promise Arbiter Table
        elements.append(Paragraph("12 Bhavas Cuspal Sub-Lord (CSL) Promise Arbiter — பாவ காரக பலன் உறுதி", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Evaluation of each house's foundational promise through its Cuspal Sub-Lord (CSL) and planetary significations.",
            self.styles["SectionSubtitle"],
        ))

        # Build planet significator map
        sig_map: Dict[str, List[int]] = {}
        for s in self.data.significators:
            sig_map[s.get("planet", "")] = s.get("signified_houses", [])

        csl_arbiter_rows: List[List[Any]] = [
            [
                Paragraph("<b>Bhava / பாவம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Signification / காரகத்துவம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>CSL</b>", self.styles["TableHeader"]),
                Paragraph("<b>Signified Houses / குறிக்கும் வீடுகள்</b>", self.styles["TableHeader"]),
                Paragraph("<b>KP Promise Verdict / உறுதி பலன்</b>", self.styles["TableHeader"]),
            ]
        ]

        for c in self.data.cuspal_analysis:
            h = c.get("house", 1)
            csl = c.get("sub_lord", "")
            houses = sig_map.get(csl, [])
            houses_str = ", ".join(str(x) for x in sorted(houses)) if houses else "—"

            bhava_label = BHAVA_NAMES_TA.get(h, "") if self.lang == "ta" else BHAVA_NAMES_EN.get(h, f"House {h}")
            promise = c.get("promise", "Mixed")

            if promise == "Positive":
                v_badge = "<font color='#15803D'><b>Auspicious / சாதகமானது</b></font>"
            elif promise == "Negative":
                v_badge = "<font color='#991B1B'><b>Challenging / கவனிக்கத்தக்கது</b></font>"
            else:
                v_badge = "<font color='#475569'><b>Neutral / மிதமான பலன்</b></font>"

            csl_arbiter_rows.append([
                Paragraph(f"<b>House {h}</b>", self.styles["TableCellCenter"]),
                Paragraph(bhava_label, self.styles["TableCell"]),
                Paragraph(f"<font color='#8B6914'><b>{csl}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(houses_str, self.styles["TableCellCenter"]),
                Paragraph(v_badge, self.styles["TableCellCenter"]),
            ])

        t_arbiter = Table(csl_arbiter_rows, colWidths=[55, 175, 55, 115, 120])
        t_arbiter.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.8),
        ]))
        elements.append(t_arbiter)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 4: 4-Tier ABCD House Significators & Planet-wise Significators
    # -------------------------------------------------------------------------
    def _build_page_4_significators(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("4-Tier ABCD House Significators — பாவ காரகர்கள் (பாவ நிர்தேசம்)", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "<b>Hierarchy:</b> Level A = Star of Occupants (Strongest) | Level B = House Occupants | Level C = Star of House Lord | Level D = House Lord",
            self.styles["SectionSubtitle"],
        ))

        abcd_rows: List[List[Any]] = [
            [
                Paragraph("<b>House</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign & Lord</b>", self.styles["TableHeader"]),
                Paragraph("<b>Level A<br/>(Star of Occ.)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Level B<br/>(Occupants)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Level C<br/>(Star of Lord)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Level D<br/>(Lord)</b>", self.styles["TableHeader"]),
                Paragraph("<b>Ordered Significators<br/>(A → B → C → D)</b>", self.styles["TableHeader"]),
            ]
        ]

        for hs in self.data.house_significators:
            h = hs.get("house", 1)
            s_name = hs.get("sign_name", "")
            s_lord = hs.get("sign_lord", "")
            sign_info = f"{s_name} ({s_lord})"

            la = ", ".join(hs.get("level_a", [])) or "—"
            lb = ", ".join(hs.get("level_b", [])) or "—"
            lc = ", ".join(hs.get("level_c", [])) or "—"
            ld = ", ".join(hs.get("level_d", [])) or "—"
            all_s = ", ".join(hs.get("all_significators", [])) or "—"

            abcd_rows.append([
                Paragraph(f"<b>House {h}</b>", self.styles["TableCellCenter"]),
                Paragraph(sign_info, self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#15803D'><b>{la}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(lb, self.styles["TableCellCenter"]),
                Paragraph(lc, self.styles["TableCellCenter"]),
                Paragraph(ld, self.styles["TableCellCenter"]),
                Paragraph(f"<b>{all_s}</b>", self.styles["TableCellCenter"]),
            ])

        t_abcd = Table(abcd_rows, colWidths=[55, 75, 75, 70, 75, 55, 115])
        t_abcd.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.8),
        ]))
        elements.append(t_abcd)
        elements.append(Spacer(1, 10))

        # Planet-wise Significators Table
        elements.append(Paragraph("Planet-wise Significators — கிரக காரகத்துவ அட்டவணை", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Planetary agency indicating all houses influenced by each planet sorted by strength order.",
            self.styles["SectionSubtitle"],
        ))

        planet_sig_rows: List[List[Any]] = [
            [
                Paragraph("<b>Planet / கிரகம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Signified Houses / குறிக்கும் வீடுகள்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Agency Order / காரகத்துவ வரிசை</b>", self.styles["TableHeader"]),
            ]
        ]

        for s in self.data.significators:
            p_name = s.get("planet", "")
            p_disp = f"{p_name} ({GRAHA_NAMES_TA.get(p_name, '')})" if self.lang == "ta" else p_name
            houses = s.get("signified_houses", [])
            houses_str = ", ".join(str(h) for h in sorted(houses)) if houses else "—"

            order_entries = s.get("strength_order", [])
            order_strs = [f"H{oe.get('house', '')} ({oe.get('type', '')})" for oe in order_entries]
            order_display = " • ".join(order_strs) if order_strs else "—"

            planet_sig_rows.append([
                Paragraph(f"<b>{p_disp}</b>", self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#8B6914'><b>{houses_str}</b></font>", self.styles["TableCellCenter"]),
                Paragraph(order_display, self.styles["TableCell"]),
            ])

        t_psig = Table(planet_sig_rows, colWidths=[90, 110, 320])
        t_psig.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3.2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.2),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_psig)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 5: Ruling Planets (RP) & 5-Level Vimshottari Dasa Hierarchy
    # -------------------------------------------------------------------------
    def _build_page_5_ruling_planets_dasa(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("Ruling Planets (RP) of the Moment — ஆளும் கிரகங்கள்", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Divine rulers of the judgment epoch used for confirmation, birth time rectification, and prashna timing.",
            self.styles["SectionSubtitle"],
        ))

        rp = self.data.ruling_planets or {}
        day_lord = rp.get("day_lord", "—")
        asc_sign_lord = rp.get("ascendant_sign_lord", "—")
        asc_star_lord = rp.get("ascendant_star_lord", "—")
        asc_sub_lord = rp.get("ascendant_sub_lord", "—")
        moon_sign_lord = rp.get("moon_sign_lord", "—")
        moon_star_lord = rp.get("moon_star_lord", "—")
        moon_sub_lord = rp.get("moon_sub_lord", "—")
        rp_list = rp.get("ruling_planets_list", [])
        rp_str = ", ".join(rp_list) if rp_list else "—"

        rp_data = [
            [
                Paragraph("<b>Role / ஸ்தானம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sign Lord / ராசி நாதன்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Star Lord / சார நாதன்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Sub-Lord / உப நாதன்</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>Ascendant (லக்னம்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(asc_sign_lord, self.styles["TableCellCenter"]),
                Paragraph(asc_star_lord, self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#8B6914'><b>{asc_sub_lord}</b></font>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>Moon (சந்திரன்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(moon_sign_lord, self.styles["TableCellCenter"]),
                Paragraph(moon_star_lord, self.styles["TableCellCenter"]),
                Paragraph(f"<font color='#8B6914'><b>{moon_sub_lord}</b></font>", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>Day Lord (கிழமை நாதன்)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(day_lord, self.styles["TableCellCenter"]),
                Paragraph("—", self.styles["TableCellCenter"]),
                Paragraph("—", self.styles["TableCellCenter"]),
            ],
            [
                Paragraph("<b>Ruling Planets Summary</b>", self.styles["TableCellBoldCenter"]),
                Paragraph(f"<font color='#15803D'><b>{rp_str}</b></font>", self.styles["TableCellCenter"]),
                Paragraph("—", self.styles["TableCellCenter"]),
                Paragraph("—", self.styles["TableCellCenter"]),
            ],
        ]
        t_rp = Table(rp_data, colWidths=[140, 125, 125, 130])
        t_rp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('SPAN', (1, 4), (3, 4)),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_rp)
        elements.append(Spacer(1, 10))

        # 5-Level Vimshottari Dasa Hierarchy
        elements.append(Paragraph("Vimshottari Dasa Hierarchy — விம்சோத்தரி தசா-புக்தி இருப்பு", self.styles["SectionTitle"]))

        dasa = self.data.dasa_hierarchy or {}
        md_lord = dasa.get("mahadasha_lord", "—")
        md_bal_y = dasa.get("mahadasha_balance_years", 0.0)
        md_bal_d = dasa.get("mahadasha_balance_days", 0.0)
        ad_lord = dasa.get("antardasha_lord", "—")
        pd_lord = dasa.get("pratyantardasha_lord", "—")

        dasa_bal_data = [
            [
                Paragraph("<b>Dasa Balance at Epoch / பிறப்பு தசா இருப்பு:</b>", self.styles["TableCell"]),
                Paragraph(f"<b>{md_lord} Mahadasha:</b> {md_bal_y:.2f} Years ({int(md_bal_d)} Days)", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Active Sub-Periods / நடப்பு புக்தி & அந்தரம்:</b>", self.styles["TableCell"]),
                Paragraph(f"<b>Bhukti:</b> {ad_lord} • <b>Andharam:</b> {pd_lord}", self.styles["TableCell"]),
            ],
        ]
        t_dbal = Table(dasa_bal_data, colWidths=[200, 320])
        t_dbal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.0, GOLD_ACCENT),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FDE68A")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_dbal)
        elements.append(Spacer(1, 10))

        # 120-Year Mahadasha Timeline Table
        elements.append(Paragraph("120-Year Vimshottari Mahadasha Sequence — 120 வருட தசா காலவரிசை", self.styles["SectionTitle"]))

        mahadashas = dasa.get("mahadashas", [])
        md_rows: List[List[Any]] = [
            [
                Paragraph("<b>Mahadasha Lord / தசா நாதன்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Vedic Name / பெயர்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Start Date / ஆரம்பம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>End Date / முடிவு</b>", self.styles["TableHeader"]),
                Paragraph("<b>Duration / காலம்</b>", self.styles["TableHeader"]),
            ]
        ]

        if mahadashas:
            for m in mahadashas:
                lord = m.get("lord", "")
                dur_y = round(m.get("duration_days", 0.0) / 365.25, 1)
                md_rows.append([
                    Paragraph(f"<b>{lord}</b>", self.styles["TableCellCenter"]),
                    Paragraph(f"{lord} Dasa ({GRAHA_NAMES_TA.get(lord, '')})", self.styles["TableCellCenter"]),
                    Paragraph(m.get("start_date", "")[:10], self.styles["TableCellCenter"]),
                    Paragraph(m.get("end_date", "")[:10], self.styles["TableCellCenter"]),
                    Paragraph(f"{dur_y} Years", self.styles["TableCellCenter"]),
                ])
        else:
            md_rows.append([
                Paragraph(f"<b>{md_lord}</b>", self.styles["TableCellCenter"]),
                Paragraph(f"{md_lord} Dasa", self.styles["TableCellCenter"]),
                Paragraph("Epoch Date", self.styles["TableCellCenter"]),
                Paragraph("Future", self.styles["TableCellCenter"]),
                Paragraph(f"{md_bal_y:.1f} Years (Balance)", self.styles["TableCellCenter"]),
            ])

        t_md = Table(md_rows, colWidths=[110, 120, 100, 100, 90])
        t_md.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3.2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.2),
        ]))
        elements.append(t_md)

        return elements

    # -------------------------------------------------------------------------
    # PAGE 6: KP Life Event Matrix, Remedial Directives & Official Certification
    # -------------------------------------------------------------------------
    def _build_page_6_event_matrix_certification(self) -> List[Any]:
        elements: List[Any] = []

        elements.append(Paragraph("KP Event Signification Matrix — முக்கிய வாழ்க்கை நிகழ்வுகளின் பலன் உறுதி", self.styles["SectionTitle"]))
        elements.append(Paragraph(
            "Evaluation of life events via primary Cuspal Sub-Lords (CSL) and supporting vs denying bhava linkages.",
            self.styles["SectionSubtitle"],
        ))

        matrix_rows: List[List[Any]] = [
            [
                Paragraph("<b>Life Event / நிகழ்வு</b>", self.styles["TableHeader"]),
                Paragraph("<b>Primary Cusp & CSL</b>", self.styles["TableHeader"]),
                Paragraph("<b>Significations / வீடுகள்</b>", self.styles["TableHeader"]),
                Paragraph("<b>Supporting / Denying</b>", self.styles["TableHeader"]),
                Paragraph("<b>KP Cuspal Promise / பலன்</b>", self.styles["TableHeader"]),
            ]
        ]

        for ev in self.data.event_evaluations:
            ev_name = ev.get("name_ta") if self.lang == "ta" else ev.get("name_en")
            csl_info = f"Cusp {ev.get('primary_cusp')}: <b>{ev.get('csl')}</b>"
            sigs_str = ", ".join(str(x) for x in ev.get("signified_houses", [])) or "—"
            supp_deny = f"<font color='#15803D'>+{','.join(str(x) for x in ev.get('supporting_houses', []))}</font> / <font color='#991B1B'>-{','.join(str(x) for x in ev.get('denying_houses', []))}</font>"
            color = ev.get("color", "#475569")
            promise_badge = f"<font color='{color}'><b>{ev.get('promise')}</b></font>"

            matrix_rows.append([
                Paragraph(f"<b>{ev_name}</b>", self.styles["TableCell"]),
                Paragraph(csl_info, self.styles["TableCellCenter"]),
                Paragraph(sigs_str, self.styles["TableCellCenter"]),
                Paragraph(supp_deny, self.styles["TableCellCenter"]),
                Paragraph(promise_badge, self.styles["TableCellCenter"]),
            ])

        t_matrix = Table(matrix_rows, colWidths=[120, 100, 95, 105, 100])
        t_matrix.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_matrix)
        elements.append(Spacer(1, 10))

        # Remedial Directives Box
        elements.append(Paragraph("KP Astrological Remedial Directives — பரிகார ஆலோசனைகள்", self.styles["SectionTitle"]))
        remedy_text = (
            "<b>1. Sub-Lord Period Guidance:</b> During the sub-period (Bhukti/Andharam) of planets signifying unfavorable "
            "houses (e.g. 6, 8, 12), avoid high-risk financial speculation and unnecessary conflicts.<br/>"
            "<b>2. Sattvic Graha Shanti:</b> Chant the Navagraha Stotra or Vishnu Sahasranama for benefic planet strength. "
            "Light ghee lamps on corresponding planetary weekdays to harmonize energies.<br/>"
            "<b>3. Timing with Ruling Planets:</b> Important agreements, travels, and investments should be initiated "
            "during favorable Ruling Planet transits and strong Cuspal Sub-Lord muhurtas."
        )
        t_remedy = Table([[Paragraph(remedy_text, self.styles["ReportBody"])]], colWidths=[520])
        t_remedy.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_remedy)
        elements.append(Spacer(1, 10))

        # Certification Seal & Verification Hash Block
        elements.append(Paragraph("Official Certification & Security Seal — சான்றொப்பம் & பாதுகாப்பு முத்திரை", self.styles["SectionTitle"]))

        raw_fingerprint = f"{self.data.report_id}:{self.data.native_name}:{self.data.birth_date}:{self.data.birth_time}:{self.data.latitude}:{self.data.longitude}"
        cert_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest().upper()

        cert_data = [
            [
                Paragraph("<b>Report Identifier / அறிக்கை எண்:</b>", self.styles["TableCell"]),
                Paragraph(f"<b>{self.data.report_id}</b>", self.styles["TableCell"]),
                Paragraph("<b>Generation Timestamp:</b>", self.styles["TableCell"]),
                Paragraph(self.data.generated_at, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>SHA-256 Verification Hash:</b>", self.styles["TableCell"]),
                Paragraph(f"<font size='6' face='Courier'><b>{cert_hash[:32]}...</b></font>", self.styles["TableCell"]),
                Paragraph("<b>Ephemeris Calibration:</b>", self.styles["TableCell"]),
                Paragraph("Krishnamurti VP291 • Placidus Semi-Arc", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Astrological Certification:</b>", self.styles["TableCell"]),
                Paragraph(
                    "<font color='#15803D'><b>✓ Certified Deterministic KP Computation</b></font><br/>"
                    "Gokul's Astrological Insights Astronomical Calibration Seal",
                    self.styles["TableCell"],
                ),
                Paragraph("<b>Confidentiality:</b>", self.styles["TableCell"]),
                Paragraph("Private & Confidential. Prepared solely for client use.", self.styles["TableCell"]),
            ],
        ]
        t_cert = Table(cert_data, colWidths=[130, 130, 130, 130])
        t_cert.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ('BOX', (0, 0), (-1, -1), 1.2, GOLD_PRIMARY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FDE68A")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_cert)
        elements.append(Spacer(1, 8))

        # Legal Disclaimer
        disclaimer = (
            "<b>Ethical Astrological Disclaimer:</b> This KP Astrology report is prepared based on classical Krishnamurti "
            "Paddhati astronomical principles and ephemeris algorithms. Astrology provides guidance, probabilistic trends, "
            "and cosmic tendencies, but does not substitute for professional medical, legal, or financial counsel. Free will "
            "and ethical action (Purushartha) remain sovereign."
        )
        elements.append(Paragraph(disclaimer, self.styles["DisclaimerText"]))

        return elements
