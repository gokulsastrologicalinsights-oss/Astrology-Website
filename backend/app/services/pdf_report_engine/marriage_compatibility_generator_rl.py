"""ReportLab fallback generator for Marriage Compatibility PDF Report."""

from __future__ import annotations
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
    HRFlowable,
)
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle

from app.services.pdf_report_engine.fonts import (
    get_report_styles,
    reorder_tamil_for_pdf,
    register_report_fonts,
    GOLD_PRIMARY,
    GOLD_ACCENT,
    BORDER_COLOR,
    BG_ZEBRA,
)
from app.services.pdf_report_engine.chart_drawer import create_south_indian_chart

logger = logging.getLogger("gai.pdf.marriage_generator_rl")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 32.0


class Paragraph(_RLParagraph):
    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class MarriageReportBorderCanvas(canvas.Canvas):
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
        self.setStrokeColor(colors.HexColor("#153F6B"))
        self.setLineWidth(1.2)
        self.rect(16, 16, PAGE_WIDTH - 32, PAGE_HEIGHT - 32)

        self.setStrokeColor(colors.HexColor("#D8BD80"))
        self.setLineWidth(0.6)
        self.rect(20, 20, PAGE_WIDTH - 40, PAGE_HEIGHT - 40)

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
            17,
            reorder_tamil_for_pdf("© Gokul's Astrological Insights • 165, Sakreeshwari Nagar, 2nd st, Thiruverkadu, Chennai - 600077 • Ph: 9444 55 9071"),
        )
        self.drawRightString(PAGE_WIDTH - MARGIN, 17, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_marriage_compatibility_pdf_bytes_rl(data: Dict[str, Any], language: str = "en") -> bytes:
    """ReportLab fallback generator."""
    register_report_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=32.0,
        bottomMargin=32.0,
    )
    styles = get_report_styles()
    lang = "ta" if str(language).lower() in ("ta", "tamil") else "en"
    elements: List[Any] = []

    # Title
    elements.append(Paragraph("<b>Gokul's Astrological Insights</b>", styles["BrandHeader"]))
    elements.append(Paragraph("165, Sakreeshwari Nagar, 2nd street, Thiruverkadu, Chennai -600077 | Phone: 9444 55 9071", styles["Subtitle"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD_ACCENT, spaceBefore=4, spaceAfter=8))
    doc_title = "திருமணப் பொருத்தம் & 36 அஷ்டகூட ஆய்வு அறிக்கை" if lang == "ta" else "KUNDLI MATCHING & 36 ASHTA KUTA COMPATIBILITY REPORT"
    elements.append(Paragraph(f"<b>{doc_title}</b>", styles["DocTitle"]))
    elements.append(Spacer(1, 10))

    # Profiles
    g_prof = data.get("groom_profile", {}) or {}
    b_prof = data.get("bride_profile", {}) or {}
    t_data = [
        [Paragraph("<b>Parameter</b>", styles["TableHeader"]), Paragraph(f"<b>Groom: {g_prof.get('name', 'Groom')}</b>", styles["TableHeader"]), Paragraph(f"<b>Bride: {b_prof.get('name', 'Bride')}</b>", styles["TableHeader"])],
        [Paragraph("DOB & TOB", styles["TableCellBold"]), Paragraph(f"{g_prof.get('birth_date', '-')} {g_prof.get('birth_time', '-')}", styles["TableCell"]), Paragraph(f"{b_prof.get('birth_date', '-')} {b_prof.get('birth_time', '-')}", styles["TableCell"])],
        [Paragraph("Lagna & Rasi", styles["TableCellBold"]), Paragraph(f"{g_prof.get('ascendant_sign', '-')} / {g_prof.get('moon_sign', '-')}", styles["TableCell"]), Paragraph(f"{b_prof.get('ascendant_sign', '-')} / {b_prof.get('moon_sign', '-')}", styles["TableCell"])],
        [Paragraph("Nakshatra & Pada", styles["TableCellBold"]), Paragraph(f"{g_prof.get('moon_nakshatra', '-')} - {g_prof.get('moon_pada', 1)}", styles["TableCell"]), Paragraph(f"{b_prof.get('moon_nakshatra', '-')} - {b_prof.get('moon_pada', 1)}", styles["TableCell"])],
    ]
    t = Table(t_data, colWidths=[150, 190, 190])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#153F6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1.0, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Wishing card
    wishing_content = (
        "<b>✨ மங்கள வாழ்த்துச் செய்தி / Auspicious Blessings ✨</b><br/><br/>"
        "<b>சீக்கிரம் திருமணம் நடைபெற இறைவனை நாங்கள் எங்கள் Gokul's Astrological Insights சார்பாக மனதார வேண்டிக்கொள்கிறோம்... வாழ்த்துக்கள்!</b><br/><br/>"
        "<i>&ldquo;sikiram kalyanam nadakanum nu aandavana nanga enga Gokul's Astrological Insights side la irundhu vendikurom..vaazhthukkal&rdquo;</i><br/><br/>"
        "Gokul's Astrological Insights • 165, Sakreeshwari Nagar, 2nd street, Thiruverkadu, Chennai -600077 • Phone: 9444 55 9071"
    )
    w_t = Table([[Paragraph(wishing_content, styles["TableCellCenter"])]], colWidths=[530])
    w_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAF2DE")),
        ("BOX", (0, 0), (-1, -1), 1.5, GOLD_ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    elements.append(w_t)

    doc.build(elements, canvasmaker=MarriageReportBorderCanvas)
    return buffer.getvalue()
