"""Comprehensive Numerology PDF Report Generator.

Compiles professional, branded, downloadable PDF reports for all nine registered
Numerology studios in Gokul's Astrological Insights.

Supports bilingual English and Tamil text rendering using ReportLab,
Noto Sans Tamil TrueType fonts, and automated Indic glyph reordering.
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
from app.services.numerology.report_repository import ENGINE_VERSION

logger = logging.getLogger("gai.numerology.pdf_generator")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0  # 0.5 inch margins
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 523.27 pt


class Paragraph(_RLParagraph):
    """Custom Paragraph that automatically pre-processes Tamil text for linear TTFont rendering."""

    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class NumerologyNumberedCanvas(canvas.Canvas):
    """Two-pass canvas that writes dynamic total page count and running headers/footers."""

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
            self.drawString(
                MARGIN,
                PAGE_HEIGHT - 26,
                reorder_tamil_for_pdf("Gokul's Astrological Insights | எண் கணித ஆய்வு அறிக்கை"),
            )

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(
                PAGE_WIDTH - MARGIN,
                PAGE_HEIGHT - 26,
                "Deterministic Numerology Report • Confidential",
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
            "© Gokul's Astrological Insights • Deterministic Numerology Engine • Pythagorean & Chaldean Matrix",
        )

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, page_str)

        self.restoreState()


# Bilingual dictionary mapping for labels
I18N: Dict[str, Dict[str, str]] = {
    "brand_title": {
        "en": "GOKUL'S ASTROLOGICAL INSIGHTS",
        "ta": "கோகுல் ஜோதிட மையம் (GOKUL'S ASTROLOGICAL INSIGHTS)",
    },
    "report_subtitle": {
        "en": "Deterministic Numerology & Vibrational Analysis Report",
        "ta": "எண் கணித முழுமையான அதிர்வு ஆய்வு அறிக்கை",
    },
    "subject_details": {
        "en": "Subject & Client Particulars",
        "ta": "ஜாதகர் / நிறுவன விவரங்கள்",
    },
    "core_metrics": {
        "en": "Core Vibrational Metrics",
        "ta": "முதன்மை எண் கணித குறியீடுகள்",
    },
    "calculations_breakdown": {
        "en": "Deterministic Calculation Breakdown",
        "ta": "படிமுறை கணக்கீடுகள் & எண் மாற்றங்கள்",
    },
    "vibrational_synthesis": {
        "en": "Vibrational Synthesis & Interpretations",
        "ta": "எண் அதிர்வு பலன்கள் & வழிகாட்டுதல்",
    },
    "comparative_analysis": {
        "en": "Comparative & Resonance Analysis",
        "ta": "ஒப்பீட்டு & பொருத்தம் மதிப்பீடு",
    },
    "methodology_notes": {
        "en": "System Convention & Methodological Rules",
        "ta": "கணித முறை & விதிமுறைகள்",
    },
    "disclaimer_title": {
        "en": "Philosophical Disclaimer & Ethical Guidance",
        "ta": "பொறுப்புத் துறப்பு & நல்வழிகாட்டுதல்",
    },
    "disclaimer_text": {
        "en": (
            "Numerological calculations, compound reductions, and interpretations provided herein are intended for "
            "self-reflection, educational exploration, and philosophical enrichment. They do not constitute deterministic "
            "scientific guarantees, medical diagnoses, legal opinions, or commercial warranties. Individual conscious free will, "
            "pragmatic decision-making, and ethical action remain paramount in shaping one's destiny."
        ),
        "ta": (
            "இவ்வறிக்கையில் வழங்கப்பட்டுள்ள எண் கணித கணக்கீடுகளும் விளக்கங்களும் தனிநபர் சுய ஆய்வு மற்றும் தத்துவ விழிப்புணர்வுக்காக "
            "மட்டுமே வழங்கப்படுகின்றன. இவை திட்டவட்டமான அறிவியல் விதிகளோ, சட்ட, நிதி, மருத்துவ ஆலோசனைகளோ அல்ல. மனித முயற்சி, விவேகம், "
            "நற்பண்புகள் மற்றும் தர்ம நெறியே வாழ்வின் உயர்வுக்கு அடிப்படையானவை."
        ),
    },
}


def _t(key: str, lang: str = "en") -> str:
    """Helper to retrieve bilingual translated string."""
    item = I18N.get(key, {})
    return item.get(lang, item.get("en", key))


class NumerologyPdfGenerator:
    """Generates professional, multi-page branded PDF reports for all Numerology studios."""

    def __init__(
        self,
        person_name: str,
        birth_date: Optional[str],
        method: str,
        system_convention: str,
        calculation_data: Dict[str, Any],
        interpretation_data: Optional[Dict[str, Any]] = None,
        language: str = "en",
        display_number: Optional[int] = None,
        report_id: Optional[str] = None,
        engine_version: str = ENGINE_VERSION,
    ):
        self.person_name = person_name.strip() or "Client / Subject"
        self.birth_date = (birth_date or "").strip() or "N/A"
        self.method = method
        self.system_convention = system_convention or "pythagorean"
        self.calc = calculation_data or {}
        self.interp = interpretation_data or {}
        self.language = language if language in ("en", "ta") else "en"
        self.display_number = display_number
        self.report_id = report_id or "NUM-PREVIEW"
        self.engine_version = engine_version
        self.styles = get_report_styles()

    def generate(self) -> bytes:
        """Compile document story and render PDF bytes."""
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

        # 1. Header Banner
        story.extend(self._build_header_banner())

        # 2. Subject & System Particulars
        story.extend(self._build_subject_particulars())

        # 3. Core Vibrational Metrics Cards
        story.extend(self._build_core_metrics())

        # 4. Method Specific Analysis & Highlights
        story.extend(self._build_method_analysis())

        # 5. Detailed Step-by-Step Calculations
        story.extend(self._build_detailed_calculations())

        # 6. Thematic Interpretations (Strengths, Challenges, Life Domains)
        story.extend(self._build_thematic_interpretations())

        # 7. Methodology & Ethical Disclaimer
        story.extend(self._build_methodology_and_disclaimer())

        doc.build(story, canvasmaker=NumerologyNumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------------------
    # 1. Header Banner
    # -------------------------------------------------------------------------
    def _build_header_banner(self) -> List[Any]:
        elements: List[Any] = [Spacer(1, 4)]
        brand_title = _t("brand_title", self.language)
        sub_title = _t("report_subtitle", self.language)
        method_label = self._get_method_title()

        elements.append(Paragraph(brand_title, self.styles["BrandHeader"]))
        elements.append(Paragraph(f"{sub_title} • {method_label}", self.styles["BrandSubHeader"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=GOLD_PRIMARY, spaceBefore=4, spaceAfter=10))
        return elements

    def _get_method_title(self) -> str:
        titles = {
            "traditional": "Core Traditional Numerology (முழுமையான எண் கணிதம்)",
            "destiny_matrix": "Destiny Matrix 22 Arcana (விதி அட்சக்கோடு மேட்ரிக்ஸ்)",
            "advanced": "Advanced Lo Shu Grid & Pinnacles (லோ ஷூ கட்டம் & உச்சங்கள்)",
            "name_correction": "Name Suggestion & Correction Studio (பெயர் திருத்த ஆய்வு)",
            "business": "Business & Brand Numerology Studio (வணிக & பிராண்ட் எண் கணிதம்)",
            "phone": "Phone & Mobile Number Numerology (தொலைபேசி எண் கணிதம்)",
            "vehicle": "Vehicle Registration Numerology (வாகன எண் கணிதம்)",
            "property": "House, Flat & Property Numerology (வீட்டு & மனை எண் கணிதம்)",
            "marriage": "Marriage Compatibility by Numerology (திருமண எண் கணிதப் பொருத்தம்)",
            "family": "Family & Baby Numerology Studio (குடும்ப & குழந்தை எண் கணிதம்)",
        }
        return titles.get(self.method, self.method.replace("_", " ").title())

    # -------------------------------------------------------------------------
    # 2. Subject Particulars Table
    # -------------------------------------------------------------------------
    def _build_subject_particulars(self) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph(_t("subject_details", self.language), self.styles["SectionTitle"]))

        record_label = f"#{self.display_number}" if self.display_number else self.report_id
        convention_text = f"{self.system_convention.capitalize()} System"

        subject_rows = [
            [
                Paragraph("<b>Subject / Name:</b>", self.styles["TableCell"]),
                Paragraph(f"<b>{self.person_name}</b>", self.styles["TableCell"]),
                Paragraph("<b>Birth / Event Date:</b>", self.styles["TableCell"]),
                Paragraph(self.birth_date, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Studio Method:</b>", self.styles["TableCell"]),
                Paragraph(self.method.replace("_", " ").title(), self.styles["TableCell"]),
                Paragraph("<b>Calculation System:</b>", self.styles["TableCell"]),
                Paragraph(convention_text, self.styles["TableCell"]),
            ],
            [
                Paragraph("<b>Report Identifier:</b>", self.styles["TableCell"]),
                Paragraph(record_label, self.styles["TableCell"]),
                Paragraph("<b>Engine Version:</b>", self.styles["TableCell"]),
                Paragraph(f"v{self.engine_version}", self.styles["TableCell"]),
            ],
        ]

        t_sub = Table(subject_rows, colWidths=[120, 140, 120, 143])
        t_sub.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_sub)
        elements.append(Spacer(1, 10))
        return elements

    # -------------------------------------------------------------------------
    # 3. Core Vibrational Metrics Cards
    # -------------------------------------------------------------------------
    def _build_core_metrics(self) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph(_t("core_metrics", self.language), self.styles["SectionTitle"]))

        cards_data: List[Dict[str, str]] = []

        if self.method == "traditional":
            bp = self.calc.get("birth_psychic_number") or {}
            lp = self.calc.get("life_path") or {}
            ex = self.calc.get("expression_destiny") or {}
            su = self.calc.get("soul_urge") or {}
            pe = self.calc.get("personality") or {}
            cards_data = [
                {"title": "Birth / Psychic (Mulank)", "value": str(bp.get("number_value", "-")), "sub": f"Ruler: {bp.get('ruling_planet', 'Sun')}"},
                {"title": "Life Path (Bhagyank)", "value": str(lp.get("number_value", "-")), "sub": f"Ruler: {lp.get('ruling_planet', 'Moon')}"},
                {"title": "Expression (Destiny)", "value": str(ex.get("number_value", "-")), "sub": f"Master: {'Yes' if ex.get('is_master') else 'No'}"},
                {"title": "Soul Urge (Desire)", "value": str(su.get("number_value", "-")), "sub": f"Vowel Sum: {su.get('compound_number', '-')}"},
                {"title": "Personality Number", "value": str(pe.get("number_value", "-")), "sub": f"Outer Aura: {pe.get('ruling_planet', '-')}"},
                {"title": "Personal Year", "value": str(self.calc.get("personal_year", "-")), "sub": "Current Annual Cycle"},
            ]
        elif self.method == "destiny_matrix":
            ps = self.calc.get("personal_square") or {}
            ss = self.calc.get("social_square") or {}
            cards_data = [
                {"title": "Day / Physical (A)", "value": str(ps.get("point_a", "-")), "sub": "Earthly Personality"},
                {"title": "Month / Spiritual (B)", "value": str(ps.get("point_b", "-")), "sub": "Intuition & Spirit"},
                {"title": "Year / Past Karma (C)", "value": str(ps.get("point_c", "-")), "sub": "Material Ancestral"},
                {"title": "Sum / Karmic Tail (D)", "value": str(ps.get("point_d", "-")), "sub": "Main Past Life Debt"},
                {"title": "Comfort Center (R)", "value": str(self.calc.get("center_comfort_zone", {}).get("point_r", "-")), "sub": "Core Soul Vibration"},
                {"title": "Spiritual Purpose", "value": str(self.calc.get("purposes", {}).get("spiritual", "-")), "sub": "Third Life Stage (60+)"},
            ]
        elif self.method == "advanced":
            pc = self.calc.get("pinnacles_challenges") or {}
            pins = pc.get("pinnacles") if isinstance(pc, dict) else None
            if pins is None:
                pins = self.calc.get("pinnacles")
            
            p1_val = "-"
            if isinstance(pins, list) and pins:
                first = pins[0]
                if isinstance(first, dict):
                    p1_val = str(first.get("value") or first.get("number") or "-")
                else:
                    p1_val = str(first)
            elif isinstance(pins, dict):
                p1_val = str(pins.get("pinnacle_1", {}).get("number") or pins.get("pinnacle_1", {}).get("value", "-"))

            chals = pc.get("challenges") if isinstance(pc, dict) else None
            if chals is None:
                chals = self.calc.get("challenges")
            
            c1_val = "-"
            if isinstance(chals, list) and chals:
                first = chals[0]
                if isinstance(first, dict):
                    c1_val = str(first.get("value") or first.get("number") or "-")
                else:
                    c1_val = str(first)
            elif isinstance(chals, dict):
                c1_val = str(chals.get("challenge_1", {}).get("number") or chals.get("challenge_1", {}).get("value", "-"))

            cards_data = [
                {"title": "Unicode Derived Root", "value": str(self.calc.get("unicode_derived_name_number", "-")), "sub": "Universal Code Point"},
                {"title": "Missing Lessons", "value": str(len(self.calc.get("karmic_lessons", []))), "sub": ", ".join(map(str, self.calc.get("karmic_lessons", []))) or "None"},
                {"title": "Dominant Vibrations", "value": ", ".join(map(str, self.calc.get("dominant_vibrations", []))) or "None", "sub": "Most Repeated Digits"},
                {"title": "Pinnacle 1 Vibration", "value": p1_val, "sub": "First Life Phase"},
                {"title": "Challenge 1 Root", "value": c1_val, "sub": "Early Life Hurdle"},
                {"title": "Lo Shu Arrows Active", "value": str(len(self.calc.get("lo_shu", {}).get("arrows_of_strength", []))), "sub": "Strength Lines"},
            ]
        elif self.method == "name_correction":
            orig = self.calc.get("original_name_analysis") or {}
            best = self.calc.get("best_candidate") or (self.calc.get("candidates", [{}])[0] if self.calc.get("candidates") else {})
            cards_data = [
                {"title": "Original Expression", "value": str(orig.get("expression", "-")), "sub": f"Compound: {orig.get('compound_expression', '-')}"},
                {"title": "Target Expression", "value": str(self.calc.get("target_expression", "-")), "sub": "Desired Harmonic Vibration"},
                {"title": "Best Candidate", "value": str(best.get("name", "-")), "sub": f"Expression: {best.get('expression_number', '-')}"},
                {"title": "Composite Score", "value": f"{best.get('composite_score', '-')}/100", "sub": "Overall Viability"},
                {"title": "Harmony Score", "value": f"{best.get('harmony_score', '-')}%", "sub": "Resonance with DOB"},
                {"title": "Simplicity Score", "value": f"{best.get('simplicity_score', '-')}%", "sub": "Ease of Adoption"},
            ]
        elif self.method == "business":
            leg = self.calc.get("legal_analysis") or {}
            brd = self.calc.get("brand_analysis") or {}
            tag = self.calc.get("tagline_analysis") or {}
            cards_data = [
                {"title": "Legal Entity Number", "value": str(leg.get("expression_number", "-")), "sub": f"Compound: {leg.get('compound_expression', '-')}"},
                {"title": "Public Brand Number", "value": str(brd.get("expression_number", "-")), "sub": f"Compound: {brd.get('compound_expression', '-')}"},
                {"title": "Industry Harmony", "value": f"{brd.get('industry_harmony_score', '-')}%", "sub": "Sector Compatibility"},
                {"title": "Founder Alignment", "value": f"{brd.get('founder_harmony_score', '-')}%", "sub": "Leadership Resonance"},
                {"title": "Tagline Expression", "value": str(tag.get("expression_number", "-")), "sub": f"Synergy: {tag.get('synergy_score', '-')}%"},
                {"title": "Brand Composite", "value": f"{brd.get('composite_score', '-')}/100", "sub": "Commercial Rating"},
            ]
        elif self.method == "phone":
            pri = self.calc.get("primary_analysis") or {}
            per = self.calc.get("personal_compatibility") or {}
            cards_data = [
                {"title": "National Root Number", "value": str(pri.get("root_number", "-")), "sub": f"Planet: {pri.get('ruling_planet', '-')}"},
                {"title": "Compound Sum", "value": str(pri.get("compound_sum", "-")), "sub": f"Keyword: {pri.get('keyword', '-')}"},
                {"title": "Personal Compatibility", "value": f"{per.get('personal_score', '-')}%", "sub": f"Resonance: {per.get('level', '-')}"},
                {"title": "Vanity Rhythm Score", "value": f"{pri.get('patterns', {}).get('vanity_score', '-')}%", "sub": "Memorability Rhythm"},
                {"title": "Zero (0) Count", "value": str(pri.get("zero_count", "0")), "sub": "Cipher Energy"},
                {"title": "Missing Digits Count", "value": str(len(pri.get("missing_digits", []))), "sub": ", ".join(map(str, pri.get("missing_digits", []))) or "None"},
            ]
        elif self.method == "vehicle":
            pri = self.calc.get("primary_analysis") or {}
            usg = self.interp.get("usage_alignment") or {}
            cards_data = [
                {"title": "Registration Root", "value": str(pri.get("root_number", "-")), "sub": f"Planet: {pri.get('ruling_planet', '-')}"},
                {"title": "Compound Total", "value": str(pri.get("compound_sum", "-")), "sub": f"Archetype: {pri.get('keyword', '-')}"},
                {"title": "Usage Compatibility", "value": f"{usg.get('score', '-')}%", "sub": f"Category: {usg.get('vehicle_usage', '-')}"},
                {"title": "Calculation Mode", "value": self.calc.get("calculation_mode", "digits_only").replace("_", " ").title(), "sub": pri.get("mode_label", "Mode")},
                {"title": "Parsed Plate State", "value": str(self.calc.get("parsed_state", "-")), "sub": f"RTO: {self.calc.get('parsed_rto', '-')}"},
                {"title": "Registered Digits", "value": str(self.calc.get("parsed_number", "-")), "sub": f"Series: {self.calc.get('parsed_series', '-')}"},
            ]
        elif self.method == "property":
            comb = self.calc.get("components", {}).get("combined_analysis") or {}
            vast = self.calc.get("vastu_alignment") or {}
            cards_data = [
                {"title": "Combined Property Root", "value": str(comb.get("root_number", "-")), "sub": f"Compound: {comb.get('compound_sum', '-')}"},
                {"title": "Vastu Facing Alignment", "value": f"{vast.get('vastu_score', '-')}%", "sub": f"Facing: {vast.get('facing_direction', '-')}"},
                {"title": "Door / Flat Root", "value": str(self.calc.get("components", {}).get("door_analysis", {}).get("root_number", "-")), "sub": "Primary Entryway"},
                {"title": "Building Root", "value": str(self.calc.get("components", {}).get("building_analysis", {}).get("root_number", "-")), "sub": "Structure Total"},
                {"title": "Floor Vibration", "value": str(self.calc.get("components", {}).get("floor_analysis", {}).get("root_number", "-")), "sub": "Vertical Plane"},
                {"title": "Vastu Element", "value": str(vast.get("element", "-")), "sub": f"Ruler: {vast.get('ruler', '-')}"},
            ]
        elif self.method == "marriage":
            cards_data = [
                {"title": "Overall Compatibility", "value": f"{self.calc.get('overall_score', '-')}%", "sub": self.calc.get('overall_harmony_level', 'Harmony Level')},
                {"title": "Life Path Synergy", "value": f"{self.calc.get('life_path_compatibility', {}).get('score', '-')}%", "sub": self.calc.get('life_path_compatibility', {}).get('harmony_level', '-')},
                {"title": "Psychic Day Harmony", "value": f"{self.calc.get('psychic_compatibility', {}).get('score', '-')}%", "sub": self.calc.get('psychic_compatibility', {}).get('harmony_level', '-')},
                {"title": "Expression Synergy", "value": f"{self.calc.get('expression_compatibility', {}).get('score', '-')}%" if self.calc.get('expression_compatibility', {}).get('score') else "N/A", "sub": "Name Vibration"},
                {"title": "Soul Urge Harmony", "value": f"{self.calc.get('soul_urge_compatibility', {}).get('score', '-')}%" if self.calc.get('soul_urge_compatibility', {}).get('score') else "N/A", "sub": "Heart Desire"},
                {"title": "Planetary Dynamic", "value": str(self.calc.get('life_path_compatibility', {}).get('planetary_dynamic', '-')), "sub": "Inter-Planetary Flow"},
            ]
        elif self.method == "family":
            elem = self.calc.get("elemental_balance") or {}
            dom = ", ".join(map(str, self.calc.get("dominant_vibrations") or [])) or "Balanced"
            cards_data = [
                {"title": "Family Harmony Score", "value": f"{self.calc.get('family_harmony_score', 80)}%", "sub": f"{len(self.calc.get('members', []))} Members Profiled"},
                {"title": "Dominant Vibration", "value": dom, "sub": "Core Archetype Vibration"},
                {"title": "Baby Candidates", "value": str(len(self.calc.get("candidate_names") or [])), "sub": "Evaluated Names"},
                {"title": "Leading Element", "value": str(elem.get("dominant_element", "Balanced")), "sub": f"Fire:{elem.get('Fire', 0)} Earth:{elem.get('Earth', 0)}"},
                {"title": "Pairwise Synergy", "value": f"{len(self.calc.get('pairwise_dynamics', []))} Pairs", "sub": "Harmonic Matrix"},
                {"title": "Vibrational Gaps", "value": ", ".join(map(str, self.calc.get("missing_vibrations") or [])) or "None", "sub": "Missing Numbers"},
            ]

        # Render 2 rows of 3 columns
        grid_rows: List[List[Any]] = []
        for i in range(0, len(cards_data), 3):
            chunk = cards_data[i:i+3]
            row = []
            for item in chunk:
                cell_content = [
                    Paragraph(f"<b>{item['title']}</b>", self.styles["CardTitle"]),
                    Paragraph(f"<font size='16' color='{NAVY_PRIMARY}'><b>{item['value']}</b></font>", self.styles["TableCellCenter"]),
                    Paragraph(f"<font size='7' color='#64748B'>{item['sub']}</font>", self.styles["TableCellCenter"]),
                ]
                row.append(cell_content)
            # pad row to 3 items if needed
            while len(row) < 3:
                row.append([Paragraph("", self.styles["TableCell"])])
            grid_rows.append(row)

        t_cards = Table(grid_rows, colWidths=[174, 174, 175])
        t_cards.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FCFBF9")),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2DCD5")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(t_cards)
        elements.append(Spacer(1, 12))
        return elements

    # -------------------------------------------------------------------------
    # 4. Method Specific Analysis Sections
    # -------------------------------------------------------------------------
    def _build_method_analysis(self) -> List[Any]:
        elements: List[Any] = []

        if self.method == "destiny_matrix":
            elements.append(Paragraph("Destiny Matrix Octagram & Life Spheres", self.styles["SectionTitle"]))
            purp = self.calc.get("purposes") or {}
            kt = self.calc.get("karmic_tail") or {}
            dm_rows = [
                [Paragraph("<b>Sphere</b>", self.styles["TableHeader"]), Paragraph("<b>Arcana / Points</b>", self.styles["TableHeader"]), Paragraph("<b>Theme & Interpretive Focus</b>", self.styles["TableHeader"])],
                [Paragraph("Personal Purpose", self.styles["TableCellBoldCenter"]), Paragraph(str(purp.get("personal", "-")), self.styles["TableCellCenter"]), Paragraph("Self-realization, inner growth, and physical health (Ages 20-40).", self.styles["TableCell"])],
                [Paragraph("Social Purpose", self.styles["TableCellBoldCenter"]), Paragraph(str(purp.get("social", "-")), self.styles["TableCellCenter"]), Paragraph("Community contribution, family duty, and professional legacy (Ages 40-60).", self.styles["TableCell"])],
                [Paragraph("Spiritual Purpose", self.styles["TableCellBoldCenter"]), Paragraph(str(purp.get("spiritual", "-")), self.styles["TableCellCenter"]), Paragraph("Soul transcendence, higher consciousness, and inner liberation (Ages 60+).", self.styles["TableCell"])],
                [Paragraph("Karmic Tail", self.styles["TableCellBoldCenter"]), Paragraph(str(kt.get("points", "-")), self.styles["TableCellCenter"]), Paragraph(f"<b>{kt.get('title', 'Karmic Program')}</b>: {kt.get('description', '')}", self.styles["TableCell"])],
                [Paragraph("Financial Entrance", self.styles["TableCellBoldCenter"]), Paragraph(str(self.calc.get("money_line", {}).get("entrance", "-")), self.styles["TableCellCenter"]), Paragraph(f"Blockers: {self.calc.get('money_line', {}).get('blockers', '-')}", self.styles["TableCell"])],
                [Paragraph("Love Entrance", self.styles["TableCellBoldCenter"]), Paragraph(str(self.calc.get("love_line", {}).get("entrance", "-")), self.styles["TableCellCenter"]), Paragraph(f"Partner Qualities: {self.calc.get('love_line', {}).get('partner_qualities', '-')}", self.styles["TableCell"])],
            ]
            t_dm = Table(dm_rows, colWidths=[110, 90, 323])
            t_dm.setStyle(self._default_table_style())
            elements.append(t_dm)
            elements.append(Spacer(1, 10))

        elif self.method == "advanced":
            elements.append(Paragraph("Lo Shu Magic Square & Life Pinnacles", self.styles["SectionTitle"]))
            lo_shu = self.calc.get("lo_shu") or {}
            freq = lo_shu.get("digit_frequencies") or {}
            # 3x3 Magic Square table representation:
            # Row 1: 4, 9, 2
            # Row 2: 3, 5, 7
            # Row 3: 8, 1, 6
            ls_table_data = [
                [
                    Paragraph(f"<b>Wood (4)</b><br/>{freq.get('4', freq.get(4, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Fire (9)</b><br/>{freq.get('9', freq.get(9, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Earth (2)</b><br/>{freq.get('2', freq.get(2, '-'))}x", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph(f"<b>Wood (3)</b><br/>{freq.get('3', freq.get(3, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Earth (5)</b><br/>{freq.get('5', freq.get(5, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Metal (7)</b><br/>{freq.get('7', freq.get(7, '-'))}x", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph(f"<b>Earth (8)</b><br/>{freq.get('8', freq.get(8, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Water (1)</b><br/>{freq.get('1', freq.get(1, '-'))}x", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>Metal (6)</b><br/>{freq.get('6', freq.get(6, '-'))}x", self.styles["TableCellCenter"]),
                ],
            ]
            t_ls = Table(ls_table_data, colWidths=[174, 174, 175])
            t_ls.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF8F5")),
                ('BOX', (0, 0), (-1, -1), 1.0, GOLD_PRIMARY),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(t_ls)
            elements.append(Spacer(1, 8))

            arrows_s = lo_shu.get("arrows_of_strength") or []
            arrows_w = lo_shu.get("arrows_of_weakness") or []
            if arrows_s or arrows_w:
                def _fmt_arrow(item: Any) -> str:
                    if isinstance(item, dict):
                        nums = item.get("numbers") or ""
                        name = item.get("name") or item.get("arrow_name") or item.get("title") or ""
                        return f"{nums} ({name})".strip(" ()") or str(item)
                    return str(item)

                arr_text = []
                if arrows_s:
                    arr_text.append(f"<b>Arrows of Strength:</b> {', '.join(_fmt_arrow(a) for a in arrows_s)}")
                if arrows_w:
                    arr_text.append(f"<b>Arrows of Weakness:</b> {', '.join(_fmt_arrow(a) for a in arrows_w)}")
                elements.append(Paragraph("<br/>".join(arr_text), self.styles["ReportBody"]))
                elements.append(Spacer(1, 10))

        elif self.method == "name_correction":
            elements.append(Paragraph("Name Correction Candidate Rankings", self.styles["SectionTitle"]))
            cand_rows = [
                [
                    Paragraph("<b>Candidate Name</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Variation</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Expr.</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Cmpd.</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Harm. %</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Pron. %</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Simp. %</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Total /100</b>", self.styles["TableHeader"]),
                ]
            ]
            candidates = (self.calc.get("candidates") or [])[:5]
            for c in candidates:
                cand_rows.append([
                    Paragraph(f"<b>{c.get('name', '-')}</b>", self.styles["TableCell"]),
                    Paragraph(c.get("variation_type", "-").replace("_", " "), self.styles["TableCellCenter"]),
                    Paragraph(str(c.get("expression_number", "-")), self.styles["TableCellBoldCenter"]),
                    Paragraph(str(c.get("compound_expression", "-")), self.styles["TableCellCenter"]),
                    Paragraph(f"{c.get('harmony_score', '-')}%", self.styles["TableCellCenter"]),
                    Paragraph(f"{c.get('pronunciation_score', '-')}%", self.styles["TableCellCenter"]),
                    Paragraph(f"{c.get('simplicity_score', '-')}%", self.styles["TableCellCenter"]),
                    Paragraph(f"<b>{c.get('composite_score', '-')}/100</b>", self.styles["TableCellBoldCenter"]),
                ])
            t_cand = Table(cand_rows, colWidths=[130, 85, 45, 45, 52, 52, 52, 62])
            t_cand.setStyle(self._default_table_style())
            elements.append(t_cand)
            elements.append(Spacer(1, 10))

        elif self.method == "business":
            founders = self.calc.get("founders_evaluation") or []
            if founders:
                elements.append(Paragraph("Founder & Leadership Alignment Matrix", self.styles["SectionTitle"]))
                f_rows = [
                    [
                        Paragraph("<b>Founder Name</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Birth Date</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Psychic</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Life Path</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Harmony %</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Resonance Level</b>", self.styles["TableHeader"]),
                    ]
                ]
                for f in founders:
                    f_rows.append([
                        Paragraph(f"<b>{f.get('founder_name', '-')}</b>", self.styles["TableCell"]),
                        Paragraph(str(f.get("birth_date", "-")), self.styles["TableCellCenter"]),
                        Paragraph(str(f.get("psychic_number", "-")), self.styles["TableCellCenter"]),
                        Paragraph(str(f.get("life_path_number", "-")), self.styles["TableCellCenter"]),
                        Paragraph(f"{f.get('harmony_score', '-')}%", self.styles["TableCellCenter"]),
                        Paragraph(str(f.get("resonance_level", "-")), self.styles["TableCell"]),
                    ])
                t_f = Table(f_rows, colWidths=[130, 80, 50, 50, 60, 153])
                t_f.setStyle(self._default_table_style())
                elements.append(t_f)
                elements.append(Spacer(1, 10))

        elif self.method == "marriage":
            elements.append(Paragraph("Couple Profile Alignment & Harmonization", self.styles["SectionTitle"]))
            pa = self.calc.get("person_a_profile") or {}
            pb = self.calc.get("person_b_profile") or {}
            m_rows = [
                [Paragraph("<b>Numerological Sphere</b>", self.styles["TableHeader"]), Paragraph(f"<b>Partner A: {pa.get('name', 'Person A')}</b>", self.styles["TableHeader"]), Paragraph(f"<b>Partner B: {pb.get('name', 'Person B')}</b>", self.styles["TableHeader"]), Paragraph("<b>Harmonic Dynamic</b>", self.styles["TableHeader"])],
                [
                    Paragraph("Birth / Psychic Number (Mulank)", self.styles["TableCellBoldCenter"]),
                    Paragraph(f"{pa.get('birth_psychic_number', '-')} ({pa.get('birth_psychic_planet', '-')})", self.styles["TableCellCenter"]),
                    Paragraph(f"{pb.get('birth_psychic_number', '-')} ({pb.get('birth_psychic_planet', '-')})", self.styles["TableCellCenter"]),
                    Paragraph(f"{self.calc.get('psychic_compatibility', {}).get('score', '-')}% • {self.calc.get('psychic_compatibility', {}).get('harmony_level', '-')}", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph("Life Path Number (Bhagyank)", self.styles["TableCellBoldCenter"]),
                    Paragraph(f"{pa.get('life_path_number', '-')} ({pa.get('life_path_planet', '-')})", self.styles["TableCellCenter"]),
                    Paragraph(f"{pb.get('life_path_number', '-')} ({pb.get('life_path_planet', '-')})", self.styles["TableCellCenter"]),
                    Paragraph(f"{self.calc.get('life_path_compatibility', {}).get('score', '-')}% • {self.calc.get('life_path_compatibility', {}).get('harmony_level', '-')}", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph("Expression Name Vibration", self.styles["TableCellBoldCenter"]),
                    Paragraph(str(pa.get("expression_number", "-")), self.styles["TableCellCenter"]),
                    Paragraph(str(pb.get("expression_number", "-")), self.styles["TableCellCenter"]),
                    Paragraph(f"{self.calc.get('expression_compatibility', {}).get('score', '-')}% • {self.calc.get('expression_compatibility', {}).get('harmony_level', '-')}", self.styles["TableCellCenter"]),
                ],
                [
                    Paragraph("Soul Urge (Heart's Desire)", self.styles["TableCellBoldCenter"]),
                    Paragraph(str(pa.get("soul_urge_number", "-")), self.styles["TableCellCenter"]),
                    Paragraph(str(pb.get("soul_urge_number", "-")), self.styles["TableCellCenter"]),
                    Paragraph(f"{self.calc.get('soul_urge_compatibility', {}).get('score', '-')}% • {self.calc.get('soul_urge_compatibility', {}).get('harmony_level', '-')}", self.styles["TableCellCenter"]),
                ],
            ]
            t_m = Table(m_rows, colWidths=[140, 115, 115, 153])
            t_m.setStyle(self._default_table_style())
            elements.append(t_m)
            elements.append(Spacer(1, 10))

            # Dialogue prompts if available
            prompts = self.calc.get("conversation_prompts") or []
            if prompts:
                elements.append(Paragraph("<b>Couples Intimacy & Dialogue Prompts:</b>", self.styles["ReportBodyBold"]))
                for p in prompts[:3]:
                    elements.append(Paragraph(f"• {p}", self.styles["ReportBody"]))
                elements.append(Spacer(1, 10))

        elif self.method == "family":
            elements.append(Paragraph("Family Member Vibrational Profiles", self.styles["SectionTitle"]))
            mems = self.calc.get("members") or []
            if mems:
                f_rows = [
                    [
                        Paragraph("<b>Member / Role</b>", self.styles["TableHeader"]),
                        Paragraph("<b>DOB / Psychic</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Life Path (Bhagyank)</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Expression Name</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Ruling Planet</b>", self.styles["TableHeader"]),
                    ]
                ]
                for m in mems:
                    b_val = str(m.get("birth_psychic_number") or "-")
                    lp_val = str(m.get("life_path_number") or "-")
                    ex_val = str(m.get("expression_number") or "-")
                    f_rows.append([
                        Paragraph(f"<b>{m.get('name', 'Member')}</b><br/><font size='7' color='#64748B'>{m.get('relationship', 'Member').title()}</font>", self.styles["TableCell"]),
                        Paragraph(f"{m.get('birth_date') or '-'}<br/>Root: <b>{b_val}</b>", self.styles["TableCellCenter"]),
                        Paragraph(f"<b>{lp_val}</b>", self.styles["TableCellCenter"]),
                        Paragraph(f"<b>{ex_val}</b>", self.styles["TableCellCenter"]),
                        Paragraph(f"{m.get('ruling_planet', '-')}<br/><font size='7' color='#64748B'>{m.get('archetype_label', '')}</font>", self.styles["TableCellCenter"]),
                    ])
                t_f = Table(f_rows, colWidths=[120, 100, 100, 100, 103])
                t_f.setStyle(self._default_table_style())
                elements.append(t_f)
                elements.append(Spacer(1, 10))

            # Baby Name Candidates if any
            cands = self.calc.get("candidate_names") or []
            if cands:
                elements.append(Paragraph("Baby Name Candidate Rankings", self.styles["SectionTitle"]))
                c_rows = [
                    [
                        Paragraph("<b>Rank / Name</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Pythagorean</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Chaldean</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Harmony & Phonetics</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Score</b>", self.styles["TableHeader"]),
                    ]
                ]
                for idx, c in enumerate(cands[:8], start=1):
                    pyth_str = f"Root {c.get('pythagorean_expression', '-')} (Sum {c.get('pythagorean_compound', '-')})"
                    chald_str = f"Root {c.get('chaldean_expression', '-')} (Sum {c.get('chaldean_compound', '-')})"
                    c_rows.append([
                        Paragraph(f"<b>#{idx} {c.get('candidate_name')}</b>", self.styles["TableCell"]),
                        Paragraph(pyth_str, self.styles["TableCellCenter"]),
                        Paragraph(chald_str, self.styles["TableCellCenter"]),
                        Paragraph(f"DOB: {c.get('dob_harmony_score', '-')}% • Phonetic: {c.get('pronunciation_score', '-')}%", self.styles["TableCellCenter"]),
                        Paragraph(f"<b>{c.get('composite_score', 0)}/100</b>", self.styles["TableCellBoldCenter"]),
                    ])
                t_c = Table(c_rows, colWidths=[120, 105, 105, 120, 73])
                t_c.setStyle(self._default_table_style())
                elements.append(t_c)
                elements.append(Spacer(1, 10))

            # Pairwise dynamics summary if any
            pairs = self.calc.get("pairwise_dynamics") or []
            if pairs:
                elements.append(Paragraph("Family Pairwise Harmony Dynamics", self.styles["SectionTitle"]))
                p_rows = [
                    [
                        Paragraph("<b>Relationship Pair</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Planetary Flow</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Harmony Rating</b>", self.styles["TableHeader"]),
                        Paragraph("<b>Nurturing Key</b>", self.styles["TableHeader"]),
                    ]
                ]
                for p in pairs[:5]:
                    p_rows.append([
                        Paragraph(f"<b>{p.get('member_a_name')} & {p.get('member_b_name')}</b><br/><font size='7' color='#64748B'>{p.get('relationship_type', '').title()}</font>", self.styles["TableCell"]),
                        Paragraph(p.get("planetary_dynamic", "-"), self.styles["TableCellCenter"]),
                        Paragraph(f"<b>{p.get('compatibility_score', '-')}%</b> ({p.get('harmony_level', '-')})", self.styles["TableCellCenter"]),
                        Paragraph(p.get("parenting_dialogue_prompt", "")[:90] + "...", self.styles["TableCell"]),
                    ])
                t_p = Table(p_rows, colWidths=[130, 115, 105, 173])
                t_p.setStyle(self._default_table_style())
                elements.append(t_p)
                elements.append(Spacer(1, 10))

            # Mindful reflection prompts if available
            prompts = self.calc.get("reflection_prompts") or []
            if prompts:
                elements.append(Paragraph("<b>Family Mindful Dialogue & Reflection Prompts:</b>", self.styles["ReportBodyBold"]))
                for pr in prompts[:3]:
                    elements.append(Paragraph(f"• {pr}", self.styles["ReportBody"]))
                elements.append(Spacer(1, 10))

        return elements

    # -------------------------------------------------------------------------
    # 5. Detailed Step-by-Step Calculations
    # -------------------------------------------------------------------------
    def _build_detailed_calculations(self) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph(_t("calculations_breakdown", self.language), self.styles["SectionTitle"]))

        calc_rows: List[List[Any]] = [
            [
                Paragraph("<b>Component / Dimension</b>", self.styles["TableHeader"]),
                Paragraph("<b>Input / Target</b>", self.styles["TableHeader"]),
                Paragraph("<b>Reduction Formula</b>", self.styles["TableHeader"]),
                Paragraph("<b>Resulting Root</b>", self.styles["TableHeader"]),
            ]
        ]

        # Extract breakdown depending on method
        if self.method == "traditional":
            cb = self.calc.get("calculation_breakdown") or {}
            bp = self.calc.get("birth_psychic_number") or {}
            lp = self.calc.get("life_path") or {}
            ex = self.calc.get("expression_destiny") or {}
            calc_rows.append([
                Paragraph("Birth Number (Mulank)", self.styles["TableCell"]),
                Paragraph(cb.get("source_birth_date", self.birth_date), self.styles["TableCellCenter"]),
                Paragraph(bp.get("calculation_method", "Day reduction"), self.styles["TableCell"]),
                Paragraph(f"<b>{bp.get('number_value', '-')}</b>", self.styles["TableCellBoldCenter"]),
            ])
            calc_rows.append([
                Paragraph("Life Path (Bhagyank)", self.styles["TableCell"]),
                Paragraph(cb.get("source_birth_date", self.birth_date), self.styles["TableCellCenter"]),
                Paragraph(lp.get("calculation_method", "Period reduction (Month + Day + Year)"), self.styles["TableCell"]),
                Paragraph(f"<b>{lp.get('number_value', '-')}</b>", self.styles["TableCellBoldCenter"]),
            ])
            calc_rows.append([
                Paragraph("Expression (Destiny)", self.styles["TableCell"]),
                Paragraph(self.person_name, self.styles["TableCellCenter"]),
                Paragraph(ex.get("calculation_method", f"{self.system_convention.capitalize()} letter sum"), self.styles["TableCell"]),
                Paragraph(f"<b>{ex.get('number_value', '-')}</b>", self.styles["TableCellBoldCenter"]),
            ])
        elif self.method == "phone":
            pri = self.calc.get("primary_analysis") or {}
            calc_rows.append([
                Paragraph("Subscriber Digits", self.styles["TableCell"]),
                Paragraph(str(self.calc.get("subscriber_digits", "-")), self.styles["TableCellCenter"]),
                Paragraph("Direct Sum of all 10 subscriber digits", self.styles["TableCell"]),
                Paragraph(f"<b>{pri.get('root_number', '-')}</b> (Sum: {pri.get('compound_sum', '-')})", self.styles["TableCellBoldCenter"]),
            ])
            calc_rows.append([
                Paragraph("Frequency Density", self.styles["TableCell"]),
                Paragraph(self.calc.get("formatted_national", "-"), self.styles["TableCellCenter"]),
                Paragraph(f"Zero count: {pri.get('zero_count', 0)}, Unique digits: {10 - len(pri.get('missing_digits', []))}/10", self.styles["TableCell"]),
                Paragraph(f"Rhythm: {pri.get('patterns', {}).get('vanity_score', '-')}%", self.styles["TableCellBoldCenter"]),
            ])
        elif self.method == "vehicle":
            pri = self.calc.get("primary_analysis") or {}
            steps = pri.get("reduction_steps") or []
            calc_rows.append([
                Paragraph("Registration Plate", self.styles["TableCell"]),
                Paragraph(self.calc.get("formatted_registration", self.person_name), self.styles["TableCellCenter"]),
                Paragraph(f"{pri.get('mode_label', 'Mode')}: {' -> '.join(map(str, steps))}", self.styles["TableCell"]),
                Paragraph(f"<b>{pri.get('root_number', '-')}</b> (Sum: {pri.get('compound_sum', '-')})", self.styles["TableCellBoldCenter"]),
            ])
        elif self.method == "property":
            comps = self.calc.get("components") or {}
            for name, comp in comps.items():
                calc_rows.append([
                    Paragraph(name.replace("_", " ").title(), self.styles["TableCell"]),
                    Paragraph(str(comp.get("input_string", "-")), self.styles["TableCellCenter"]),
                    Paragraph(comp.get("formula", "Sum reduction"), self.styles["TableCell"]),
                    Paragraph(f"<b>{comp.get('root_number', '-')}</b>", self.styles["TableCellBoldCenter"]),
                ])
        elif self.method == "family":
            mems = self.calc.get("members") or []
            for m in mems:
                calc_rows.append([
                    Paragraph(f"{m.get('name', 'Member')} ({m.get('relationship', 'Member').title()})", self.styles["TableCell"]),
                    Paragraph(m.get('birth_date') or m.get('name', '-'), self.styles["TableCellCenter"]),
                    Paragraph("Birth Psychic + Life Path + Expression", self.styles["TableCell"]),
                    Paragraph(f"Mulank: <b>{m.get('birth_psychic_number', '-')}</b> | LP: <b>{m.get('life_path_number', '-')}</b>", self.styles["TableCellBoldCenter"]),
                ])
        else:
            calc_rows.append([
                Paragraph("Primary Subject Calculation", self.styles["TableCell"]),
                Paragraph(self.person_name, self.styles["TableCellCenter"]),
                Paragraph(f"{self.system_convention.capitalize()} Deterministic Engine", self.styles["TableCell"]),
                Paragraph("Verified", self.styles["TableCellBoldCenter"]),
            ])

        t_calc = Table(calc_rows, colWidths=[140, 110, 190, 83])
        t_calc.setStyle(self._default_table_style())
        elements.append(t_calc)
        elements.append(Spacer(1, 10))
        return elements

    # -------------------------------------------------------------------------
    # 6. Thematic Interpretations
    # -------------------------------------------------------------------------
    def _build_thematic_interpretations(self) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph(_t("vibrational_synthesis", self.language), self.styles["SectionTitle"]))

        # Overall synthesis
        synth = self.interp.get("overall_synthesis") or self.calc.get("overall_synthesis")
        if not synth and self.method == "traditional":
            synth = self.calc.get("birth_psychic_number", {}).get("detailed_interpretation", "")
        if synth:
            elements.append(Paragraph("<b>Executive Vibrational Summary:</b>", self.styles["ReportBodyBold"]))
            elements.append(Paragraph(synth, self.styles["ReportBody"]))
            elements.append(Spacer(1, 8))

        # Strengths & Challenges table
        strengths = self.interp.get("strengths") or self.calc.get("shared_strengths") or []
        challenges = self.interp.get("challenges") or self.calc.get("potential_challenges") or []

        if strengths or challenges:
            str_paras = [Paragraph(f"• {s}", self.styles["TableCell"]) for s in strengths[:4]] or [Paragraph("None specified.", self.styles["TableCell"])]
            cha_paras = [Paragraph(f"• {c}", self.styles["TableCell"]) for c in challenges[:4]] or [Paragraph("None specified.", self.styles["TableCell"])]

            sc_table = Table(
                [
                    [Paragraph("<b>Key Vibrational Strengths & Synergies</b>", self.styles["TableHeader"]), Paragraph("<b>Growth Edges & Friction Points</b>", self.styles["TableHeader"])],
                    [str_paras, cha_paras],
                ],
                colWidths=[261, 262],
            )
            sc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F0FDF4")),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#FEF2F2")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FAFAFA")),
                ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(sc_table)
            elements.append(Spacer(1, 10))

        # Career / Financial / Love tendencies if present
        career = self.interp.get("career_tendencies") or []
        finance = self.interp.get("financial_tendencies") or []
        love = self.interp.get("love_themes") or []

        if career or finance or love:
            themes_rows = [
                [Paragraph("<b>Life Dimension</b>", self.styles["TableHeader"]), Paragraph("<b>Archetypal Tendencies & Practical Guidance</b>", self.styles["TableHeader"])],
            ]
            if career:
                themes_rows.append([Paragraph("Career & Vocation", self.styles["TableCellBoldCenter"]), Paragraph("; ".join(career[:3]), self.styles["TableCell"])])
            if finance:
                themes_rows.append([Paragraph("Wealth & Prosperity", self.styles["TableCellBoldCenter"]), Paragraph("; ".join(finance[:3]), self.styles["TableCell"])])
            if love:
                themes_rows.append([Paragraph("Relationships & Bonds", self.styles["TableCellBoldCenter"]), Paragraph("; ".join(love[:3]), self.styles["TableCell"])])

            t_themes = Table(themes_rows, colWidths=[140, 383])
            t_themes.setStyle(self._default_table_style())
            elements.append(t_themes)
            elements.append(Spacer(1, 10))

        return elements

    # -------------------------------------------------------------------------
    # 7. Methodology & Ethical Disclaimer
    # -------------------------------------------------------------------------
    def _build_methodology_and_disclaimer(self) -> List[Any]:
        elements: List[Any] = [Spacer(1, 4)]
        elements.append(Paragraph(_t("methodology_notes", self.language), self.styles["SectionTitle"]))

        rule_body = (
            f"<b>Convention Applied:</b> {self.system_convention.capitalize()} System. "
            "Single-digit root reductions preserve ancient master numbers 11, 22, and 33 without further reduction where applicable. "
            "Compound vibrations reflect subtle esoteric undertones, whereas root numbers govern outward psychological manifestations."
        )
        elements.append(Paragraph(rule_body, self.styles["ReportBody"]))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(_t("disclaimer_title", self.language), self.styles["SectionTitle"]))
        elements.append(Paragraph(_t("disclaimer_text", self.language), self.styles["DisclaimerText"]))
        return elements

    # -------------------------------------------------------------------------
    # Helper: Default Table Styling
    # -------------------------------------------------------------------------
    def _default_table_style(self) -> TableStyle:
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 1.0, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])


def generate_numerology_pdf_bytes(
    person_name: str,
    birth_date: Optional[str],
    method: str,
    system_convention: str,
    calculation_data: Dict[str, Any],
    interpretation_data: Optional[Dict[str, Any]] = None,
    language: str = "en",
    display_number: Optional[int] = None,
    report_id: Optional[str] = None,
    engine_version: str = ENGINE_VERSION,
) -> bytes:
    """Convenience helper to generate numerology PDF bytes."""
    generator = NumerologyPdfGenerator(
        person_name=person_name,
        birth_date=birth_date,
        method=method,
        system_convention=system_convention,
        calculation_data=calculation_data,
        interpretation_data=interpretation_data,
        language=language,
        display_number=display_number,
        report_id=report_id,
        engine_version=engine_version,
    )
    return generator.generate()
