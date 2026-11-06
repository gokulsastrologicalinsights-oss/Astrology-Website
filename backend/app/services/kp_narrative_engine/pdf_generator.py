"""PDF Booklet Generator for KP Predictive Narrative Engine.

Generates a print-ready, publication-grade, bilingual English/Tamil PDF report
using ReportLab with two-pass canvas, NotoSansTamil typography, gold-and-navy accents,
and clean structured layout.
"""

from io import BytesIO
import logging
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph as _RLParagraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.pdf_report_engine.fonts import (
    BG_HEADER,
    BG_ZEBRA,
    BORDER_COLOR,
    CRIMSON_ACCENT,
    EMERALD_GREEN,
    GOLD_ACCENT,
    GOLD_PRIMARY,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    get_report_styles,
    reorder_tamil_for_pdf,
)

logger = logging.getLogger("gai.kp_narrative.pdf")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0  # 0.5 in
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 523.27 pt


class Paragraph(_RLParagraph):
    """Custom Paragraph that automatically reorders Indic vowels for ReportLab TTFont linear rendering."""

    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class KpNarrativeNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for exact total page count, running headers, and footers."""

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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int):
        self.saveState()

        # Outer decorative double border
        self.setStrokeColor(GOLD_PRIMARY)
        self.setLineWidth(1.2)
        self.rect(20, 20, PAGE_WIDTH - 40, PAGE_HEIGHT - 40)
        self.setStrokeColor(NAVY_PRIMARY)
        self.setLineWidth(0.5)
        self.rect(23, 23, PAGE_WIDTH - 46, PAGE_HEIGHT - 46)

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 8)
            except Exception:
                self.setFont("Helvetica-Bold", 8)
            self.setFillColor(NAVY_PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 28, reorder_tamil_for_pdf("GOKUL'S ASTROLOGICAL INSIGHTS | கே.பி. கணிப்பு உரை அறிக்கை"))
            try:
                self.setFont("NotoSansTamil", 8)
            except Exception:
                self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 28, "KP Stellar Predictive Narrative")
            self.setStrokeColor(GOLD_ACCENT)
            self.setLineWidth(0.6)
            self.line(MARGIN, PAGE_HEIGHT - 32, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 32)

        # Running Footer (all pages)
        self.setStrokeColor(GOLD_ACCENT)
        self.setLineWidth(0.6)
        self.line(MARGIN, 36, PAGE_WIDTH - MARGIN, 36)

        try:
            self.setFont("NotoSansTamil", 7.5)
        except Exception:
            self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 26, reorder_tamil_for_pdf("Deterministic KP Astrology Engine • Krishnamurti Paddhati"))

        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(NAVY_PRIMARY)
        self.drawRightString(PAGE_WIDTH - MARGIN, 26, page_str)

        self.restoreState()


class KpNarrativePdfGenerator:
    """Renders structured KP Predictive Narrative report as PDF."""

    def __init__(self, data: Dict[str, Any], language: str = "ta"):
        self.data = data
        self.language = language  # "en", "ta", or "bilingual"
        self.styles = get_report_styles("auto")

        font_name = self.styles["ReportBody"].fontName
        font_bold = self.styles["ReportBodyBold"].fontName

        # Add custom aligned styles safely if not present
        if "CenterBold" not in self.styles:
            self.styles.add(
                ParagraphStyle(
                    name="CenterBold",
                    parent=self.styles["Normal"],
                    fontName=font_bold,
                    alignment=1,
                    leading=14,
                )
            )
        if "Center" not in self.styles:
            self.styles.add(
                ParagraphStyle(
                    name="Center",
                    parent=self.styles["Normal"],
                    fontName=font_name,
                    alignment=1,
                    leading=12,
                )
            )
        if "Bold" not in self.styles:
            self.styles.add(
                ParagraphStyle(
                    name="Bold",
                    parent=self.styles["Normal"],
                    fontName=font_bold,
                    leading=12,
                )
            )
        if "RightBold" not in self.styles:
            self.styles.add(
                ParagraphStyle(
                    name="RightBold",
                    parent=self.styles["Normal"],
                    fontName=font_bold,
                    alignment=2,
                    leading=12,
                )
            )
        if "Right" not in self.styles:
            self.styles.add(
                ParagraphStyle(
                    name="Right",
                    parent=self.styles["Normal"],
                    fontName=font_name,
                    alignment=2,
                    leading=12,
                )
            )

    def _t(self, en_text: str, ta_text: str) -> str:
        if self.language == "ta":
            return ta_text or en_text
        elif self.language == "bilingual":
            return f"{en_text}<br/><font size='7.5' color='#1E3A8A'>{ta_text}</font>"
        return en_text

    def generate(self) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )
        story: List[Any] = []

        # 1. Header Banner
        self._build_header(story)

        # 2. Native Particulars Table
        self._build_native_details(story)

        # 3. Section 1: Natal Event Promise (ஜாதக வாக்குறுதி)
        self._build_natal_promise(story)

        # PageBreak for Clean Section Separation
        story.append(PageBreak())

        # 4. Section 2: Running Dasha-Bhukti Analysis (தற்போதைய தசா-புத்தி பலன்கள்)
        self._build_running_dasha(story)

        # 5. Section 3: Upcoming Milestone Windows (அடுத்த 12-24 மாதங்கள்)
        self._build_milestone_windows(story)

        # PageBreak for Remedies
        story.append(PageBreak())

        # 6. Section 4: Do's, Don'ts & Actionable Remedial Advice
        self._build_remedies_and_disclaimer(story)

        doc.build(story, canvasmaker=KpNarrativeNumberedCanvas)
        return buf.getvalue()

    def _build_header(self, story: List[Any]):
        title_ta = "கே.பி. கணிப்பு உரை அறிக்கை (ஜாதக வாக்குறுதி & தசா பலன்கள்)"
        title_en = "AUTOMATED KP PREDICTIVE NARRATIVE REPORT"
        sub_text = self._t(
            "Plain-Language Stellar Predictive Report • Krishnamurti Paddhati System",
            "எளிய நடை ஜோதிட கணிப்பு அறிக்கை • கிருஷ்ணமூர்த்தி பத்ததி முறை",
        )

        header_tbl = Table(
            [
                [
                    Paragraph(
                        "<font size='14' color='#B4872B'><b>GOKUL'S ASTROLOGICAL INSIGHTS</b></font>",
                        self.styles["CenterBold"],
                    )
                ],
                [
                    Paragraph(
                        f"<font size='12' color='#0A192F'><b>{self._t(title_en, title_ta)}</b></font>",
                        self.styles["CenterBold"],
                    )
                ],
                [
                    Paragraph(
                        f"<font size='8' color='#475569'>{sub_text}</font>",
                        self.styles["Center"],
                    )
                ],
            ],
            colWidths=[USABLE_WIDTH],
        )
        header_tbl.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ])
        )
        story.append(header_tbl)
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD_PRIMARY, spaceBefore=2, spaceAfter=8))

    def _build_native_details(self, story: List[Any]):
        p = self.data.get("person_details", {})
        target_date = self.data.get("target_date", "")

        sec_title = self._t("Native Particulars & Reference Horizon", "ஜாதகர் குறிப்பு & ஆய்வு விவரங்கள்")
        story.append(Paragraph(f"<b><font size='9' color='#0A192F'>{sec_title}</font></b>", self.styles["Bold"]))
        story.append(Spacer(1, 4))

        data = [
            [
                Paragraph(f"<b>{self._t('Name', 'பெயர்')}:</b> {p.get('name', 'Native')}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Birth Date', 'பிறந்த தேதி')}:</b> {p.get('birth_date', '')}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Birth Time', 'பிறந்த நேரம்')}:</b> {p.get('birth_time', '')}", self.styles["Normal"]),
            ],
            [
                Paragraph(f"<b>{self._t('Ascendant (Lagna)', 'லக்னம்')}:</b> {self._t(p.get('lagna', ''), p.get('lagna_ta', ''))}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Moon Sign (Rashi)', 'ராசி')}:</b> {self._t(p.get('moon_sign', ''), p.get('moon_sign_ta', ''))}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Nakshatra', 'நட்சத்திரம்')}:</b> {self._t(p.get('nakshatra', ''), p.get('nakshatra_ta', ''))}", self.styles["Normal"]),
            ],
            [
                Paragraph(f"<b>{self._t('Current Age', 'தற்போதைய வயது')}:</b> {p.get('current_age', '')}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Reference Date', 'ஆய்வுத் தேதி')}:</b> {target_date}", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('System', 'முறை')}:</b> KP Ayanamsa (249 Sub)", self.styles["Normal"]),
            ],
        ]

        t = Table(data, colWidths=[USABLE_WIDTH / 3.0] * 3)
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(t)
        story.append(Spacer(1, 10))

    def _build_natal_promise(self, story: List[Any]):
        np_data = self.data.get("natal_promise", {})
        items = np_data.get("items", [])

        sec_title = self._t(
            "1. Natal Event Promise (Evaluated Primary Cuspal Sub-Lords)",
            "1. ஜாதக வாக்குறுதி (முக்கிய பாவக உப-அதிபதி தீர்ப்பு)",
        )
        story.append(
            Table(
                [[Paragraph(f"<b><font size='9.5' color='#FFFFFF'>{sec_title}</font></b>", self.styles["Normal"])]],
                colWidths=[USABLE_WIDTH],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY_PRIMARY),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]),
            )
        )
        story.append(Spacer(1, 5))

        # Overall synthesis callout
        syn_text = self._t(np_data.get("overall_synthesis_en", ""), np_data.get("overall_synthesis_ta", ""))
        syn_tbl = Table(
            [[
                Paragraph(
                    f"<b>{self._t('Life Blueprint Synthesis', 'ஜாதக வாக்குறுதி பொது சுருக்கம்')}:</b> {syn_text}",
                    self.styles["Normal"],
                )
            ]],
            colWidths=[USABLE_WIDTH],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),  # light yellow
                ("BOX", (0, 0), (-1, -1), 0.8, GOLD_PRIMARY),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]),
        )
        story.append(syn_tbl)
        story.append(Spacer(1, 8))

        # Render each of the 6 cuspal sub-lords
        for item in items:
            cusp_num = item.get("cusp")
            dom_text = self._t(item.get("domain_en", ""), item.get("domain_ta", ""))
            v_badge = self._t(item.get("verdict_label_en", ""), item.get("verdict_label_ta", ""))
            verdict = item.get("verdict", "")

            # Badge color
            if verdict == "strongly_promised":
                b_color = "#166534"  # emerald green
                bg_color = "#DCFCE7"
            elif verdict == "delayed_fruition":
                b_color = "#854D0E"  # amber / brown
                bg_color = "#FEF3C7"
            else:
                b_color = "#991B1B"  # red
                bg_color = "#FEE2E2"

            csl = item.get("cusp_sub_lord", "")
            star = item.get("star_lord", "")
            narrative = self._t(item.get("plain_narrative_en", ""), item.get("plain_narrative_ta", ""))
            takeaway = self._t(item.get("practical_takeaway_en", ""), item.get("practical_takeaway_ta", ""))

            header_cell = Paragraph(
                f"<b><font size='8.5' color='#0A192F'>Cusp {cusp_num}: {dom_text}</font></b> "
                f"<font size='7' color='#64748B'>(CSL: {csl} | Star: {star})</font>",
                self.styles["Normal"],
            )
            badge_cell = Paragraph(
                f"<font size='7.5' color='{b_color}'><b>{v_badge}</b></font>",
                self.styles["RightBold"],
            )

            box_content = [
                [header_cell, badge_cell],
                [
                    Paragraph(
                        f"<font size='7.5' color='#1E293B'>{narrative}</font><br/>"
                        f"<font size='7.5' color='#0F766E'><b>{self._t('Actionable Guidance', 'நடைமுறை வழிகாட்டல்')}:</b> {takeaway}</font>",
                        self.styles["Normal"],
                    ),
                    "",
                ],
            ]

            card = Table(box_content, colWidths=[USABLE_WIDTH - 140, 140])
            card.setStyle(
                TableStyle([
                    ("SPAN", (0, 1), (1, 1)),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                    ("LINEBELOW", (0, 0), (1, 0), 0.4, colors.HexColor("#E2E8F0")),
                    ("BACKGROUND", (1, 0), (1, 0), colors.HexColor(bg_color)),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(card)
            story.append(Spacer(1, 4))

    def _build_running_dasha(self, story: List[Any]):
        rd = self.data.get("running_dasha", {})
        sec_title = self._t(
            "2. Running Dasha-Bhukti Analysis & Real-World Impact",
            "2. தற்போதைய தசா-புத்தி பலன்கள் (நிகழ்கால தாக்கம்)",
        )
        story.append(
            Table(
                [[Paragraph(f"<b><font size='9.5' color='#FFFFFF'>{sec_title}</font></b>", self.styles["Normal"])]],
                colWidths=[USABLE_WIDTH],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY_PRIMARY),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]),
            )
        )
        story.append(Spacer(1, 5))

        phase_title = self._t(rd.get("phase_title_en", ""), rd.get("phase_title_ta", ""))
        phase_theme = self._t(rd.get("phase_theme_en", ""), rd.get("phase_theme_ta", ""))
        fav_score = rd.get("favorable_score", 65)

        banner = Table(
            [[
                Paragraph(f"<b><font size='9' color='#B4872B'>{phase_title}</font></b>", self.styles["Normal"]),
                Paragraph(f"<b>{self._t('Favorability Index', 'சாதகக் குறியீடு')}: {fav_score}%</b>", self.styles["RightBold"]),
            ]],
            colWidths=[USABLE_WIDTH - 120, 120],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#94A3B8")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]),
        )
        story.append(banner)
        story.append(Spacer(1, 4))

        # Periods hierarchy table
        md = rd.get("mahadasha", {})
        ad = rd.get("bhukti", {})
        pd = rd.get("antara", {})

        tbl_data = [
            [
                Paragraph(f"<b>{self._t('Level', 'நிலை')}</b>", self.styles["Bold"]),
                Paragraph(f"<b>{self._t('Lord', 'அதிபதி')}</b>", self.styles["Bold"]),
                Paragraph(f"<b>{self._t('Star Lord', 'நட்சத்திர நாதன்')}</b>", self.styles["Bold"]),
                Paragraph(f"<b>{self._t('Sub-Lord', 'உப-நாதன்')}</b>", self.styles["Bold"]),
                Paragraph(f"<b>{self._t('Timeline', 'கால அளவு')}</b>", self.styles["Bold"]),
            ],
            [
                Paragraph(self._t(md.get("level_name_en", ""), md.get("level_name_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(md.get("lord", ""), md.get("lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(md.get("star_lord", ""), md.get("star_lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(md.get("sub_lord", ""), md.get("sub_lord_ta", "")), self.styles["Normal"]),
                Paragraph(f"{md.get('start_date', '')} to {md.get('end_date', '')}", self.styles["Normal"]),
            ],
            [
                Paragraph(self._t(ad.get("level_name_en", ""), ad.get("level_name_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(ad.get("lord", ""), ad.get("lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(ad.get("star_lord", ""), ad.get("star_lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(ad.get("sub_lord", ""), ad.get("sub_lord_ta", "")), self.styles["Normal"]),
                Paragraph(f"{ad.get('start_date', '')} to {ad.get('end_date', '')}", self.styles["Normal"]),
            ],
            [
                Paragraph(self._t(pd.get("level_name_en", ""), pd.get("level_name_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(pd.get("lord", ""), pd.get("lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(pd.get("star_lord", ""), pd.get("star_lord_ta", "")), self.styles["Normal"]),
                Paragraph(self._t(pd.get("sub_lord", ""), pd.get("sub_lord_ta", "")), self.styles["Normal"]),
                Paragraph(f"{pd.get('start_date', '')} to {pd.get('end_date', '')}", self.styles["Normal"]),
            ],
        ]

        t_dasa = Table(tbl_data, colWidths=[95, 75, 95, 85, USABLE_WIDTH - 350])
        t_dasa.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_dasa)
        story.append(Spacer(1, 6))

        # 4 Dimensions of Real World Impact
        dims = [
            ("💼 " + self._t("Career & Work Environment", "தொழில் மற்றும் பணிச் சூழல்"), self._t(rd.get("career_impact_en", ""), rd.get("career_impact_ta", ""))),
            ("💰 " + self._t("Financial Liquidity & Savings", "பணப்புழக்கம் மற்றும் சேமிப்பு"), self._t(rd.get("finance_impact_en", ""), rd.get("finance_impact_ta", ""))),
            ("❤️ " + self._t("Family & Marital Harmony", "குடும்பம் மற்றும் தாம்பத்திய உறவு"), self._t(rd.get("relationship_impact_en", ""), rd.get("relationship_impact_ta", ""))),
            ("🌿 " + self._t("Health, Energy & Vitality", "உடல் நலம் மற்றும் மன அமைதி"), self._t(rd.get("health_impact_en", ""), rd.get("health_impact_ta", ""))),
        ]

        dim_cells = []
        for title_str, text_str in dims:
            dim_cells.append([
                Paragraph(f"<b><font size='8' color='#1E3A8A'>{title_str}</font></b>", self.styles["Normal"]),
            ])
            dim_cells.append([
                Paragraph(f"<font size='7.5' color='#334155'>{text_str}</font>", self.styles["Normal"]),
            ])

        dim_tbl = Table(dim_cells, colWidths=[USABLE_WIDTH])
        dim_tbl.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#F8FAFC")),
                ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#F8FAFC")),
                ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                ("LINEBELOW", (0, 1), (-1, 1), 0.5, colors.HexColor("#E2E8F0")),
                ("LINEBELOW", (0, 3), (-1, 3), 0.5, colors.HexColor("#E2E8F0")),
                ("LINEBELOW", (0, 5), (-1, 5), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(dim_tbl)
        story.append(Spacer(1, 10))

    def _build_milestone_windows(self, story: List[Any]):
        milestones = self.data.get("milestone_windows", [])
        sec_title = self._t(
            "3. Upcoming Milestone Windows (Next 12–24 Months)",
            "3. அடுத்த 12–24 மாதங்களின் முக்கிய காலக்கட்டங்கள் (மைல்கற்கள்)",
        )
        story.append(
            Table(
                [[Paragraph(f"<b><font size='9.5' color='#FFFFFF'>{sec_title}</font></b>", self.styles["Normal"])]],
                colWidths=[USABLE_WIDTH],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY_PRIMARY),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]),
            )
        )
        story.append(Spacer(1, 5))

        for m in milestones:
            w_title = self._t(m.get("window_title_en", ""), m.get("window_title_ta", ""))
            dom_label = self._t(m.get("domain_label_en", ""), m.get("domain_label_ta", ""))
            status_str = self._t(m.get("status", ""), m.get("status_ta", ""))
            headline = self._t(m.get("headline_en", ""), m.get("headline_ta", ""))
            narr = self._t(m.get("plain_narrative_en", ""), m.get("plain_narrative_ta", ""))
            actions = m.get("action_plan_ta", []) if self.language == "ta" else m.get("action_plan_en", [])
            act_text = " • ".join(actions)

            card_data = [
                [
                    Paragraph(f"<b><font size='8.5' color='#0A192F'>{w_title} — {dom_label}</font></b>", self.styles["Normal"]),
                    Paragraph(f"<b><font size='8' color='#166534'>{status_str}</font></b>", self.styles["RightBold"]),
                ],
                [
                    Paragraph(
                        f"<b>{headline}</b><br/>"
                        f"<font size='7.5' color='#334155'>{narr}</font><br/>"
                        f"<font size='7' color='#0F766E'><b>{self._t('Action Checklist', 'செயல் திட்டம்')}:</b> {act_text}</font>",
                        self.styles["Normal"],
                    ),
                    "",
                ],
            ]

            card = Table(card_data, colWidths=[USABLE_WIDTH - 130, 130])
            card.setStyle(
                TableStyle([
                    ("SPAN", (0, 1), (1, 1)),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                    ("LINEBELOW", (0, 0), (1, 0), 0.4, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(card)
            story.append(Spacer(1, 4))

    def _build_remedies_and_disclaimer(self, story: List[Any]):
        rem = self.data.get("remedies", {})
        sec_title = self._t(
            "4. Actionable Do's & Don'ts and Tailored Remedial Guidance",
            "4. செய்ய வேண்டியவை, தவிர்க்க வேண்டியவை & பரிகார ஆலோசனைகள்",
        )
        story.append(
            Table(
                [[Paragraph(f"<b><font size='9.5' color='#FFFFFF'>{sec_title}</font></b>", self.styles["Normal"])]],
                colWidths=[USABLE_WIDTH],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY_PRIMARY),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]),
            )
        )
        story.append(Spacer(1, 6))

        dos = rem.get("dos_ta", []) if self.language == "ta" else rem.get("dos_en", [])
        donts = rem.get("donts_ta", []) if self.language == "ta" else rem.get("donts_en", [])

        dos_p = "<br/>".join([f"• {d}" for d in dos])
        donts_p = "<br/>".join([f"• {d}" for d in donts])

        dos_table = Table(
            [
                [
                    Paragraph(f"<b><font size='8.5' color='#166534'>✅ {self._t('What To Do (Do’s)', 'செய்ய வேண்டிய நற்செயல்கள்')}</font></b>", self.styles["Normal"]),
                    Paragraph(f"<b><font size='8.5' color='#991B1B'>❌ {self._t('What To Avoid (Don’ts)', 'தவிர்க்க வேண்டியவை')}</font></b>", self.styles["Normal"]),
                ],
                [
                    Paragraph(f"<font size='7.5' color='#1E293B'>{dos_p}</font>", self.styles["Normal"]),
                    Paragraph(f"<font size='7.5' color='#1E293B'>{donts_p}</font>", self.styles["Normal"]),
                ],
            ],
            colWidths=[USABLE_WIDTH / 2.0, USABLE_WIDTH / 2.0],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#DCFCE7")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F0FDF4")),
                ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FEF2F2")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]),
        )
        story.append(dos_table)
        story.append(Spacer(1, 8))

        # Spiritual & Lifestyle Remedies Table
        deity_text = self._t(rem.get("deity_prayer_en", ""), rem.get("deity_prayer_ta", ""))
        charity_text = self._t(rem.get("charity_action_en", ""), rem.get("charity_action_ta", ""))
        lifestyle_text = self._t(rem.get("lifestyle_guidance_en", ""), rem.get("lifestyle_guidance_ta", ""))
        lucky_text = self._t(rem.get("lucky_day_color_en", ""), rem.get("lucky_day_color_ta", ""))

        rem_grid = [
            [
                Paragraph(f"<b>🕉️ {self._t('Deity Meditation', 'இறை வழிபாடு & மந்திரம்')}:</b> {deity_text}", self.styles["Normal"]),
            ],
            [
                Paragraph(f"<b>🤝 {self._t('Charitable Dhanam', 'தானம் & கர்ம பரிகாரம்')}:</b> {charity_text}", self.styles["Normal"]),
            ],
            [
                Paragraph(f"<b>🧘 {self._t('Lifestyle & Focus Habits', 'வாழ்க்கை முறை சீரமைப்பு')}:</b> {lifestyle_text}", self.styles["Normal"]),
            ],
            [
                Paragraph(f"<b>🍀 {self._t('Auspicious Days & Colors', 'அதிர்ஷ்ட தினங்கள் & நிறங்கள்')}:</b> {lucky_text}", self.styles["Normal"]),
            ],
        ]

        t_rem = Table(rem_grid, colWidths=[USABLE_WIDTH])
        t_rem.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAF5FF")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D8B4FE")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E9D5FF")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(t_rem)
        story.append(Spacer(1, 12))

        # Ethical Disclaimer Box
        disc_text = self._t(self.data.get("disclaimer_en", ""), self.data.get("disclaimer_ta", ""))
        disc_tbl = Table(
            [[
                Paragraph(
                    f"<b>{self._t('Standard Astrological Advisory', 'பொறுப்புத் துறப்பு')}:</b> "
                    f"<font size='7' color='#64748B'>{disc_text}</font>",
                    self.styles["Normal"],
                )
            ]],
            colWidths=[USABLE_WIDTH],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]),
        )
        story.append(disc_tbl)
