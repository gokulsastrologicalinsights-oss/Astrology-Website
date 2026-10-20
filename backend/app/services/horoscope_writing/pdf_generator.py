"""Traditional Six-Page Tamil Horoscope Booklet PDF Generator.

Produces an authentic, print-ready, professional 6-page traditional Tamil
horoscope booklet with ReportLab, NotoSansTamil typography, running headers/footers,
and elegant traditional borders.
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

logger = logging.getLogger("gai.horoscope_writing.pdf")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0  # 0.5 inch (36 pt)
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 523.27 pt


class Paragraph(_RLParagraph):
    """Custom Paragraph that automatically reorders Indic vowels for ReportLab TTFont linear rendering."""

    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class TraditionalHoroscopeNumberedCanvas(canvas.Canvas):
    """Two-pass canvas enforcing exact Page X of 6 and running headers/footers."""

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
            self.drawString(MARGIN, PAGE_HEIGHT - 26, reorder_tamil_for_pdf("Gokul's Astrological Insights | பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "Traditional Tamil Horoscope Booklet")

            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 30, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 30)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(MARGIN, 28, PAGE_WIDTH - MARGIN, 28)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 18, reorder_tamil_for_pdf("© கோகுலின் பாரம்பரிய ஜோதிடக் குறிப்பு • Gokul's Astrological Insights • திருக்கணித முறை"))

        page_str = f"பக்கம் {self._pageNumber} / {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, reorder_tamil_for_pdf(page_str))

        self.restoreState()


class TraditionalHoroscopePdfGenerator:
    """Generates the six-page traditional Tamil horoscope booklet."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.styles = get_report_styles()

    def generate(self) -> bytes:
        """Assembles all six pages and returns PDF bytes."""
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

        # Build each of the 6 canonical pages
        self._build_page1_birth_details(story)
        story.append(PageBreak())

        self._build_page2_dinasuthi(story)
        story.append(PageBreak())

        self._build_page3_udumaka_dasa(story)
        story.append(PageBreak())

        self._build_page4_kurippu(story)
        story.append(PageBreak())

        self._build_page5_padupakshi(story)
        story.append(PageBreak())

        self._build_page6_archana_slip(story)

        doc.build(story, canvasmaker=TraditionalHoroscopeNumberedCanvas)
        return buffer.getvalue()

    def _make_page_header(self, title_ta: str, subtitle_ta: str, english_badge: str) -> List[Any]:
        """Creates a standardized traditional page header block."""
        elements = []
        header_table = Table(
            [
                [
                    Paragraph(f"<b>{title_ta}</b>", self.styles["SectionTitle"]),
                    Paragraph(f"<font color='#B4872B'><b>{english_badge}</b></font>", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph(f"<font color='#64748B'>{subtitle_ta}</font>", self.styles["SectionSubtitle"]),
                    "",
                ],
            ],
            colWidths=[USABLE_WIDTH * 0.75, USABLE_WIDTH * 0.25],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1, color=GOLD_PRIMARY, spaceBefore=2, spaceAfter=8))
        return elements

    def _build_page1_birth_details(self, story: List[Any]):
        """Page 1: நிகழும் ஆண்டு மற்றும் ஜனன விவரங்கள்."""
        p1 = self.data.get("page1_birth_details", {})
        person = self.data.get("person_details", {})

        # Brand Banner at top of Page 1
        story.append(Paragraph("|| ஸ்ரீ கணேசாய நம: || ஸ்ரீ குருப்யோ நம: ||", self.styles["TamilShloka"]))
        story.append(Paragraph("<b>கோகுலின் பாரம்பரிய ஜோதிடக் குறிப்பு</b>", self.styles["BrandHeader"]))
        story.append(Paragraph("Gokul's Astrological Insights • Traditional Tamil Horoscope Booklet", self.styles["BrandSubHeader"]))
        story.append(Spacer(1, 4))

        # Native Info summary row
        native_summary = (
            f"<b>ஜாதகர் பெயர்:</b> {person.get('name', 'Native')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>பிறந்த தேதி:</b> {person.get('birth_date')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>பிறந்த நேரம்:</b> {person.get('birth_time')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>இடம்:</b> {person.get('birth_place', '')}"
        )
        native_table = Table([[Paragraph(native_summary, self.styles["TableCellCenter"])]], colWidths=[USABLE_WIDTH])
        native_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
            ("BOX", (0, 0), (-1, -1), 0.75, GOLD_PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(native_table)
        story.append(Spacer(1, 10))

        story.extend(self._make_page_header(
            "பக்கம் 1: நிகழும் ஆண்டு மற்றும் ஜனன விவரங்கள்",
            "பாரம்பரிய பஞ்சாங்க அங்கங்கள் மற்றும் பிறப்பு நேரக் கணிப்புகள்",
            "Page 1: Birth Particulars",
        ))

        # Main 18-row Panchang table (displayed cleanly in a balanced 2-column key-value format)
        table_rows = [
            ("வருஷம் / மாதம் / தேதி", p1.get("tamil_year_month_date", "")),
            ("கிழமை (வாரம்)", p1.get("weekday", "")),
            ("அயணம்", p1.get("ayanam", "")),
            ("ருது (பருவம்)", p1.get("ritu", "")),
            ("பக்ஷம்", p1.get("paksha", "")),
            ("திதி", p1.get("tithi", "")),
            ("முதல் நாள் நக்ஷத்திரம்", p1.get("prev_nakshatra", "")),
            ("ஜனன நக்ஷத்திரம் (பிறப்பு)", p1.get("birth_nakshatra", "")),
            ("மறுநாள் நக்ஷத்திரம்", p1.get("next_nakshatra", "")),
            ("நாமயோகம்", p1.get("nama_yoga", "")),
            ("கர்ணம்", p1.get("karana", "")),
            ("தியாஜ்ஜியம் (வர்ஜ்யம்)", p1.get("tyajyam", "")),
            ("அகஸ் (பகல் அளவு)", p1.get("ahas", "")),
            ("பிறந்த நேரம்", f"{p1.get('birth_time', '')} மணி"),
            ("உதயாதி நாழிகை", f"{p1.get('udayadhi_nazhigai', '')} ({p1.get('udayadhi_hours', '')})"),
            ("சூரிய உதயம்", f"{p1.get('sunrise', '')} மணி (அஸ்தமனம்: {p1.get('sunset', '')})"),
            ("உதய லக்னம்", p1.get("udaya_lagna", "")),
            ("வார யோகம்", p1.get("vara_yoga", "")),
        ]

        table_data = []
        for i, (label, val) in enumerate(table_rows, start=1):
            table_data.append([
                Paragraph(f"<font color='#64748B'>{i:02d}.</font> <b>{label}</b>", self.styles["TableCell"]),
                Paragraph(str(val), self.styles["TableCell"]),
            ])

        main_table = Table(table_data, colWidths=[USABLE_WIDTH * 0.42, USABLE_WIDTH * 0.58])
        main_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(main_table)

    def _build_page2_dinasuthi(self, story: List[Any]):
        """Page 2: தினசுத்திப் படலம்."""
        p2 = self.data.get("page2_dinasuthi", {})

        story.extend(self._make_page_header(
            "பக்கம் 2: தினசுத்திப் படலம்",
            "காலக் கணிப்பு, பாரம்பரிய சகாப்தங்கள் & பஞ்சாங்க கணக்கீட்டு முறை",
            "Page 2: Calendar Eras",
        ))

        eras = [
            ("சகாப்தம் (சாலிவாகன சகாப்தம்)", p2.get("saka_year", "")),
            ("கலியுகாதி (கலியுக வருடம்)", p2.get("kali_year", "")),
            ("ஹிஜிரி (இஸ்லாமிய சகாப்தம்)", p2.get("hijri_year", "")),
            ("கொல்லம் ஆண்டு (மலையாள வருடம்)", p2.get("kollam_year", "")),
            ("ஆங்கில வருஷம்", str(p2.get("english_year", ""))),
            ("ஆங்கில தேதி", str(p2.get("english_date", ""))),
            ("தமிழ் மாதம் மற்றும் தேதி", str(p2.get("tamil_month_date", ""))),
            ("பஞ்சாங்கம்", str(p2.get("panchangam", ""))),
            ("கணக்கீட்டு முறை", str(p2.get("calculation_method", ""))),
        ]

        table_data = [
            [
                Paragraph("<b>பாரம்பரிய காலம் / சகாப்தப் பிரிவு</b>", self.styles["TableHeader"]),
                Paragraph("<b>கணக்கிடப்பட்ட விவரம்</b>", self.styles["TableHeader"]),
            ]
        ]
        for label, val in eras:
            table_data.append([
                Paragraph(f"<b>{label}</b>", self.styles["TableCell"]),
                Paragraph(str(val), self.styles["TableCell"]),
            ])

        table = Table(table_data, colWidths=[USABLE_WIDTH * 0.45, USABLE_WIDTH * 0.55])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(table)
        story.append(Spacer(1, 15))

        # Historical & Shastric Notes Box
        notes_content = (
            "<b>தினசுத்திப் படலக் குறிப்பு விளக்கம்:</b><br/>"
            "1. <b>சாலிவாகன சகாப்தம்:</b> கி.பி. 78-ஆம் ஆண்டு சாலிவாகன மன்னரின் வெற்றியை முன்னிட்டுத் தொடங்கப்பட்ட "
            "இந்திய தேசிய மற்றும் பாரம்பரிய பஞ்சாங்க முறை.<br/>"
            "2. <b>கலியுகாதி:</b> கி.மு. 3102 பிப்ரவரி 18 அன்று ஸ்ரீகிருஷ்ண பரமாத்மாவின் அவதார பூர்த்தியைத் தொடர்ந்து "
            "துவங்கிய கலியுக ஆண்டு கணக்கீடு.<br/>"
            "3. <b>கொல்லம் ஆண்டு:</b> கி.பி. 825-ஆம் ஆண்டு சிம்ம சங்கிராந்தி (ஆவணி 1) அன்று தொடங்கப்பட்ட தென்மண்டல "
            "பாரம்பரிய ஆண்டுக் கணக்கு.<br/>"
            "4. <b>திருக்கணித முறை:</b> நவீன வானியல் நுட்பங்களை வேத ஜோதிட சித்தாந்த விதிகளுடன் இணைத்து "
            "துல்லியமான கிரக ஸ்புடங்களைக் கணக்கிடும் முறைமை."
        )
        notes_table = Table([[Paragraph(notes_content, self.styles["TableCell"])]], colWidths=[USABLE_WIDTH])
        notes_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.75, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(notes_table)

    def _build_page3_udumaka_dasa(self, story: List[Any]):
        """Page 3: உடுமகா திசை."""
        p3 = self.data.get("page3_udumaka_dasa", {})

        story.extend(self._make_page_header(
            "பக்கம் 3: உடுமகா திசை",
            "நட்சத்திர பரம நாழிகை & விம்சோத்தரி மகா திசா-புக்தி கணக்கீட்டுப் படலம்",
            "Page 3: Vimshottari Dasa",
        ))

        dasa_params = [
            ("ஆதிபத்யம் பரம நாழிகை", p3.get("param_nazhigai", "")),
            ("பாதம் ஒன்றுக்கு", p3.get("pada_duration", "")),
            ("பிறந்த பாதம்", f"{p3.get('birth_pada', '')} ஆம் பாதம்"),
            ("பிறந்த பாதத்தில் சென்றது", p3.get("pada_sentrathu", "")),
            ("பிறந்த பாதத்தில் நின்றது", p3.get("pada_nindrathu", "")),
            ("ஜனன திசை நாயகன்", p3.get("dasa_lord", "")),
            ("திசை மொத்த காலம்", p3.get("dasa_full_years", "")),
            ("திசையில் சென்றது", p3.get("dasa_sentrathu", "")),
            ("செல் நீக்கி இருப்பு", p3.get("dasa_iruppu", "")),
        ]

        param_table_data = [
            [
                Paragraph("<b>திசா கணக்கீட்டு அங்கம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>நாழிகை / கால அளவு விவரம்</b>", self.styles["TableHeader"]),
            ]
        ]
        for label, val in dasa_params:
            param_table_data.append([
                Paragraph(f"<b>{label}</b>", self.styles["TableCell"]),
                Paragraph(f"<b>{val}</b>" if "இருப்பு" in label else str(val), self.styles["TableCell"]),
            ])

        ptable = Table(param_table_data, colWidths=[USABLE_WIDTH * 0.45, USABLE_WIDTH * 0.55])
        ptable.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(ptable)
        story.append(Spacer(1, 10))

        story.append(Paragraph("<b>விம்சோத்தரி மகா திசைகளின் வரிசைக் கால அட்டவணை (120 ஆண்டுகள்)</b>", self.styles["CardTitle"]))
        story.append(Spacer(1, 4))

        seq_headers = ["வ.எண்", "திசா நாயகன்", "மொத்த காலம்", "கால இருப்பு / அளவு", "தொடக்க தேதி", "முடிவு தேதி"]
        seq_data = [[Paragraph(f"<b>{h}</b>", self.styles["TableHeader"]) for h in seq_headers]]

        for row in p3.get("dasa_sequence", []):
            seq_data.append([
                Paragraph(str(row.get("order", "")), self.styles["TableCellCenter"]),
                Paragraph(f"<b>{row.get('lord_ta', '')}</b> திசை", self.styles["TableCell"]),
                Paragraph(f"{row.get('total_years', '')} ஆ", self.styles["TableCellCenter"]),
                Paragraph(str(row.get("balance_str", "")), self.styles["TableCell"]),
                Paragraph(str(row.get("start_date", "")), self.styles["TableCellCenter"]),
                Paragraph(str(row.get("end_date", "")), self.styles["TableCellCenter"]),
            ])

        seq_table = Table(seq_data, colWidths=[
            USABLE_WIDTH * 0.10,
            USABLE_WIDTH * 0.22,
            USABLE_WIDTH * 0.14,
            USABLE_WIDTH * 0.22,
            USABLE_WIDTH * 0.16,
            USABLE_WIDTH * 0.16,
        ])
        seq_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEF9C3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(seq_table)

    def _build_page4_kurippu(self, story: List[Any]):
        """Page 4: குறிப்பு."""
        p4 = self.data.get("page4_kurippu", {})

        story.extend(self._make_page_header(
            "பக்கம் 4: குறிப்பு",
            "ஜனன காலக் குறிப்புகள், பட்சி, மரம், மிருகம் & நாடி-கண அமைப்புகள்",
            "Page 4: Horoscope Reference",
        ))

        kurippu_items = [
            ("உதயாதி மணி", p4.get("udayadhi_mani", "")),
            ("லக்ன இருப்பு", p4.get("lagna_iruppu", "")),
            ("அகஸ்", p4.get("ahas", "")),
            ("காலம் ஒன்றுக்கு", p4.get("kalam_ontrukku", "")),
            ("காலம் (பகல் / இரவு)", p4.get("kalam", "")),
            ("லக்னம்", f"{p4.get('lagna', '')} லக்னம்"),
            ("இராசி", f"{p4.get('rasi', '')} ராசி"),
            ("நட்சத்திரம்", p4.get("nakshatra", "")),
            ("நட்சத்திரப் பாதம்", f"{p4.get('pada', '')} ஆம் பாதம்"),
            ("மிருகம்", p4.get("mrigam", "")),
            ("பட்சி", p4.get("pakshi", "")),
            ("மரம் (விருட்சம்)", p4.get("maram", "")),
            ("கணம்", p4.get("gana", "")),
            ("ரஜ்ஜு", p4.get("rajju", "")),
            ("நாடி", p4.get("nadi", "")),
        ]

        table_data = [
            [
                Paragraph("<b>சாஸ்திரக் குறிப்புப் பிரிவு</b>", self.styles["TableHeader"]),
                Paragraph("<b>ஜாதகருக்குரிய அமைப்புகள்</b>", self.styles["TableHeader"]),
            ]
        ]
        for label, val in kurippu_items:
            table_data.append([
                Paragraph(f"<b>{label}</b>", self.styles["TableCell"]),
                Paragraph(str(val), self.styles["TableCell"]),
            ])

        table = Table(table_data, colWidths=[USABLE_WIDTH * 0.45, USABLE_WIDTH * 0.55])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(table)
        story.append(Spacer(1, 10))

        expl = (
            "<b>விளக்கக் குறிப்பு:</b> மேற்கண்ட அம்சங்கள் திருமணப் பொருத்தம், தொழில் தொடக்கம், ஆயுள் பலம் "
            "மற்றும் ஆன்மீக பரிகாரக் கிரியைகளுக்கு முதன்மையாகப் பயன்படும் பாரம்பரிய வாழ்வியல் அடையாளங்களாகும்."
        )
        exp_table = Table([[Paragraph(expl, self.styles["TableCell"])]], colWidths=[USABLE_WIDTH])
        exp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(exp_table)

    def _build_page5_padupakshi(self, story: List[Any]):
        """Page 5: ஸ்ரீ படுபட்சி பலன்."""
        p5 = self.data.get("page5_padupakshi", {})

        story.extend(self._make_page_header(
            "பக்கம் 5: ஸ்ரீ படுபட்சி பலன்",
            "பஞ்ச பட்சி சாஸ்திரம் • உயிர் பட்சி அவஸ்தைகள் & பலன் வழிகாட்டல்",
            "Page 5: Padupakshi Shastra",
        ))

        summary_rows = [
            ("ஜென்ம நட்சத்திரம்", p5.get("birth_nakshatra", "")),
            ("உயிர் பட்சி", f"<b><font color='#991B1B'>{p5.get('uyir_pakshi', '')}</font></b>"),
            ("பக்ஷம் (பிறப்பு நிலை)", p5.get("paksha", "")),
            ("ஆதிக்க நிலை", p5.get("dominant_state", "")),
            ("வளர்பிறை பலன் வழிகாட்டல்", p5.get("valarpirai_guidance", "")),
            ("தேய்பிறை பலன் வழிகாட்டல்", p5.get("theypirai_guidance", "")),
        ]

        sum_data = []
        for l, v in summary_rows:
            sum_data.append([
                Paragraph(f"<b>{l}</b>", self.styles["TableCell"]),
                Paragraph(str(v), self.styles["TableCell"]),
            ])

        sum_table = Table(sum_data, colWidths=[USABLE_WIDTH * 0.40, USABLE_WIDTH * 0.60])
        sum_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 5.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("<b>பஞ்ச பட்சி சாஸ்திர அவஸ்தைகள் & அவற்றின் பலன்கள்</b>", self.styles["CardTitle"]))
        story.append(Spacer(1, 4))

        avathai_data = [
            [
                Paragraph("<b>அவஸ்தை நிலை</b>", self.styles["TableHeader"]),
                Paragraph("<b>இயல்பு & ஆற்றல் விகிதம்</b>", self.styles["TableHeader"]),
                Paragraph("<b>செய்யத்தக்க சுப காரியங்கள் & எச்சரிக்கைகள்</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph("<b>அரசு (Ruling)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("100% முழு பலம் (உச்ச நிலை)", self.styles["TableCellCenter"]),
                Paragraph("முக்கிய முடிவுகள், அரசு வேலை, வழக்கு வெற்றி, ஒப்பந்தங்கள்", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>ஊண் (Eating)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("80% உயர்ந்த பலம்", self.styles["TableCellCenter"]),
                Paragraph("தொழில் தொடக்கம், விருந்து, கல்வி, மங்கல நற்காரியங்கள்", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>நடை (Walking)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("50% மத்தியம பலம்", self.styles["TableCellCenter"]),
                Paragraph("பிரயாணம், பண்டமாற்று, சாதாரண பேச்சுவார்த்தைகள்", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>துயில் (Sleeping)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("20% குறைந்த பலம்", self.styles["TableCellCenter"]),
                Paragraph("ஓய்வு, தியானம், இறை வழிபாடு; புதிய விவகாரங்களைத் தவிர்க்கவும்", self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>சாவு (Dying)</b>", self.styles["TableCellBoldCenter"]),
                Paragraph("0% அதம நிலை (ஆபத்து)", self.styles["TableCellCenter"]),
                Paragraph("எந்த ஒரு முக்கிய சுப காரியமும் செய்யலாகாது; அமைதி காக்கவும்", self.styles["TableCell"]),
            ],
        ]

        av_table = Table(avathai_data, colWidths=[USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.30, USABLE_WIDTH * 0.45])
        av_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(av_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph(
            f"<b>விரிவான சாஸ்திர பலன்:</b> {p5.get('detailed_guidance', '')}",
            self.styles["ReportBody"]
        ))

    def _build_page6_archana_slip(self, story: List[Any]):
        """Page 6: அர்ச்சனை பேப்பரில் பலன்."""
        p6 = self.data.get("page6_archana_slip", {})
        person = self.data.get("person_details", {})

        story.extend(self._make_page_header(
            "பக்கம் 6: அர்ச்சனை பேப்பரில் பலன்",
            "ஆலய வழிபாடு, சங்கல்ப சுருக்கம் & மங்கல வழிகாட்டல் குறிப்பு",
            "Page 6: Archana Slip",
        ))

        story.append(Paragraph(
            "ஆலயங்களில் சங்கல்பம் செய்யும் போதும், பூஜை அர்ச்சனை சீட்டுகளில் குறிக்கும் போதும் "
            "பயன்படுத்த வேண்டிய சுருக்கமான பாரம்பரிய விவரங்கள்:",
            self.styles["ReportBody"]
        ))
        story.append(Spacer(1, 8))

        slip_rows = [
            ("ஜாதகர் பெயர்", person.get("name", "Native")),
            ("இராசி", f"{p6.get('rasi', '')} ராசி"),
            ("நட்சத்திரம்", p6.get("nakshatra", "")),
            ("லக்கனம்", f"{p6.get('lagna', '')} லக்னம்"),
            ("வாசல் திசை (சுப வாசல்)", f"<b>{p6.get('entrance_direction', '')}</b>"),
            ("பிறந்த ஆங்கில தேதி", p6.get("birth_date", "")),
            ("பிறந்த தமிழ் தேதி", p6.get("tamil_date", "")),
            ("அதிர்ஷ்ட நாள்", p6.get("lucky_day", "")),
            ("அதிர்ஷ்ட நிறம்", p6.get("lucky_color", "")),
            ("அதிர்ஷ்ட கல் (ரத்தினம்)", p6.get("lucky_gem", "")),
            ("வணங்க வேண்டிய தெய்வம் (குல/இஷ்ட)", f"<b>{p6.get('worship_deity', '')}</b>"),
        ]

        slip_data = []
        for l, v in slip_rows:
            slip_data.append([
                Paragraph(f"<b>{l}</b>", self.styles["TableCell"]),
                Paragraph(str(v), self.styles["TableCell"]),
            ])

        slip_table = Table(slip_data, colWidths=[USABLE_WIDTH * 0.42, USABLE_WIDTH * 0.58])
        slip_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_ZEBRA]),
            ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#B8860B")),
            ("TOPPADDING", (0, 0), (-1, -1), 5.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(slip_table)
        story.append(Spacer(1, 15))

        # Sacred Shloka Box
        shloka_text = (
            "வேயுறு தோளிபங்கன் விடமுண்ட கண்டன் மிகநல்ல வீணை தடவி<br/>"
            "மாசறு திங்கள்கங்கை முடிமே லணிந்தென் உளமே புகுந்த அதனால்<br/>"
            "ஞாயிறு திங்கள்செவ்வாய் புதன்வியாழன் வெள்ளி சனிபாம்பி ரண்டு முடனே<br/>"
            "ஆசறு நல்லநல்ல அவைநல்ல நல்ல அடியாரவர்க்கு மிகவே.<br/>"
            "<font size='7' color='#64748B'>— திருஞானசம்பந்தர் அருளிய கோளறு திருப்பதிகம்</font>"
        )
        shloka_table = Table([[Paragraph(shloka_text, self.styles["TamilShloka"])]], colWidths=[USABLE_WIDTH])
        shloka_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAF2DE")),
            ("BOX", (0, 0), (-1, -1), 1, GOLD_PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(shloka_table)
        story.append(Spacer(1, 12))

        # Astrologer Attestation / Certification Seal Block
        cert_data = [
            [
                Paragraph("<b>ஜோதிடரின் குறிப்புரை & சான்றிதழ்:</b><br/>மேற்கண்ட ஜாதகக் குறிப்பு பாரம்பரிய தர்ம சாஸ்திர முறைப்படியும் திருக்கணித வானியல் கணிதப்படியும் கணக்கிடப்பட்டுத் துல்லியமாக எழுதப்பட்டது.", self.styles["TableCell"]),
                Paragraph("<b>கோகுலின் பாரம்பரிய ஜோதிடக் குறிப்பு</b><br/>Gokul's Astrological Insights<br/>(அங்கீகரிக்கப்பட்ட முத்திரை)", self.styles["TableCellCenter"]),
            ]
        ]
        cert_table = Table(cert_data, colWidths=[USABLE_WIDTH * 0.65, USABLE_WIDTH * 0.35])
        cert_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(cert_table)
