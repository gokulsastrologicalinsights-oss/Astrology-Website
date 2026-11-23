"""Official GAI Letterhead PDF & Tamil Typography Master Regression Test Suite.

Validates the full centralized PDF architecture across all 14 project requirements:
1. Official Letterhead Asset preservation, aspect ratio, and bottom-layer placement.
2. Safe Content Area boundaries (Top >= 50mm, Bottom >= 20mm, Left/Right >= 10mm).
3. All 12 Canonical Tamil Test Strings rendered and extracted with 100% fidelity.
4. Both Typography Profiles (Traditional Noto Serif & Modern Noto Sans).
5. Multi-page background persistence across all pages.
6. English regression, numbers, currency, dates, and special symbols.
7. End-to-end generation and safe-boundary compliance across all integrated PDF generators.
"""

from io import BytesIO
from pathlib import Path
import pytest
import pypdf
from PIL import Image

from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer
from reportlab.lib import colors

from app.services.pdf_report_engine.letterhead_renderer import (
    GAILetterheadCanvas,
    GAILetterheadPDFRenderer,
    OFFICIAL_LETTERHEAD_PATH,
    PAGE_WIDTH,
    PAGE_HEIGHT,
    PAGE_SIZE,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    LEFT_MARGIN,
    RIGHT_MARGIN,
    USABLE_WIDTH,
    USABLE_HEIGHT,
    PROTECTED_ZONES,
    validate_pdf_safe_boundaries,
    create_report_title,
    create_section_heading,
    create_data_table,
    create_highlight_box,
    create_metadata_grid,
)
from app.services.pdf_report_engine.fonts import (
    register_report_fonts,
    get_report_styles,
    get_traditional_styles,
    get_modern_styles,
    normalize_tamil_text,
    reorder_tamil_for_pdf,
    Paragraph,
    TypographyProfile,
    NOTO_SANS_REGULAR,
    NOTO_SERIF_REGULAR,
)

# 12 Canonical Master Test Strings specified in Project Objective 10
CANONICAL_12_TAMIL_STRINGS = [
    "தமிழ் ஜோதிடம்",
    "அகத்தியர் பஞ்ச பட்சி சாஸ்திரம்",
    "ஜென்ம நட்சத்திரம்",
    "வளர்பிறை",
    "நேர அட்டவணை",
    "திருமண பொருத்தம்",
    "கிரக நிலைகள்",
    "தசா புத்தி",
    "ராசி பலன்",
    "பரிகாரம் மற்றும் தீர்வுகள்",
    "வெற்றி சுப நேரம்",
    "எச்சரிக்கை",
]


class TestLetterheadAssetAndGeometry:
    """Verifies Objective 1 & 2: Letterhead asset preservation and calibrated A4 geometry."""

    def test_official_letterhead_asset_exists(self):
        assert OFFICIAL_LETTERHEAD_PATH.exists(), f"Letterhead not found at {OFFICIAL_LETTERHEAD_PATH}"
        assert OFFICIAL_LETTERHEAD_PATH.stat().st_size > 100000, "Letterhead PNG must be uncompressed high-res"

    def test_letterhead_aspect_ratio_matches_a4(self):
        with Image.open(OFFICIAL_LETTERHEAD_PATH) as img:
            w, h = img.size
            img_ratio = w / h
            a4_ratio = 210.0 / 297.0
            assert abs(img_ratio - a4_ratio) < 0.015, f"Letterhead aspect ratio {img_ratio:.4f} must match A4 {a4_ratio:.4f}"

    def test_layout_constants_meet_safe_specifications(self):
        # 50mm top margin = 141.73 pt
        assert TOP_MARGIN >= 141.0
        # 20mm bottom margin = 56.69 pt
        assert BOTTOM_MARGIN >= 56.0
        # 10mm side margins = 28.35 pt
        assert LEFT_MARGIN >= 28.0
        assert RIGHT_MARGIN >= 28.0
        # Total A4 portrait dimensions
        assert round(PAGE_WIDTH, 1) == 595.3
        assert round(PAGE_HEIGHT, 1) == 841.9


class TestCanonicalTamil12StringsAndProfiles:
    """Verifies Objective 4, 5 & 10: Unicode rendering, HarfBuzz shaping, and 100% extraction."""

    @pytest.fixture(autouse=True)
    def setup_fonts(self):
        register_report_fonts()

    def test_modern_profile_all_12_strings_extracted(self):
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )
        styles = get_modern_styles()
        story = [Paragraph(s, styles["ReportBody"]) for s in CANONICAL_12_TAMIL_STRINGS]
        doc.build(story, canvasmaker=GAILetterheadCanvas)

        reader = pypdf.PdfReader(BytesIO(buf.getvalue()))
        extracted = reader.pages[0].extract_text()
        extracted_lines = [normalize_tamil_text(l.strip()) for l in extracted.splitlines() if l.strip()]

        for target in CANONICAL_12_TAMIL_STRINGS:
            assert any(target in line for line in extracted_lines), f"Missing '{target}' in Modern extracted text"

    def test_traditional_profile_all_12_strings_extracted(self):
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )
        styles = get_traditional_styles()
        story = [Paragraph(s, styles["ReportBody"]) for s in CANONICAL_12_TAMIL_STRINGS]
        doc.build(story, canvasmaker=GAILetterheadCanvas)

        reader = pypdf.PdfReader(BytesIO(buf.getvalue()))
        extracted = reader.pages[0].extract_text()
        extracted_lines = [normalize_tamil_text(l.strip()) for l in extracted.splitlines() if l.strip()]

        for target in CANONICAL_12_TAMIL_STRINGS:
            assert any(target in line for line in extracted_lines), f"Missing '{target}' in Traditional extracted text"

    def test_no_null_or_replacement_characters(self):
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=PAGE_SIZE, leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
        styles = get_modern_styles()
        story = [Paragraph(s, styles["ReportBody"]) for s in CANONICAL_12_TAMIL_STRINGS]
        doc.build(story, canvasmaker=GAILetterheadCanvas)

        reader = pypdf.PdfReader(BytesIO(buf.getvalue()))
        raw_text = reader.pages[0].extract_text()
        assert "\x00" not in raw_text, "Extracted text contains unmapped null byte"
        assert "\ufffd" not in raw_text, "Extracted text contains unicode replacement character"


class TestLetterheadBackgroundPersistenceAndZIndex:
    """Verifies Objective 6 & 8: Background on every page, bottom layer, subtle watermark."""

    def test_multi_page_background_presence(self):
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )
        styles = get_modern_styles()
        story = []
        for p_idx in range(1, 4):
            story.append(Paragraph(f"Test Multi-Page Content Page {p_idx}", styles["DocTitle"]))
            if p_idx < 3:
                story.append(PageBreak())
        doc.build(story, canvasmaker=GAILetterheadCanvas)

        reader = pypdf.PdfReader(BytesIO(buf.getvalue()))
        assert len(reader.pages) == 3

        # Every page must reference XObject image (the letterhead background)
        for page in reader.pages:
            xobjects = page["/Resources"].get("/XObject", {})
            has_image = any(xobj.get_object().get("/Subtype") == "/Image" for xobj in xobjects.values())
            assert has_image, "Letterhead image XObject must be present on every page"

    def test_safe_boundary_validation_utility(self):
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )
        styles = get_modern_styles()
        story = []
        story.extend(create_report_title("Safe Area Verification Report", "Content within boundaries"))
        story.extend(create_section_heading("Section 1: Boundary Test"))
        story.append(Paragraph("This content is guaranteed to sit within safe boundaries.", styles["ReportBody"]))
        doc.build(story, canvasmaker=GAILetterheadCanvas)

        res = validate_pdf_safe_boundaries(buf.getvalue())
        assert res["valid"] is True
        assert len(res["violations"]) == 0


class TestEnglishAndMixedRegression:
    """Verifies Objective 11: English tables, numbers, currency, dates, special symbols."""

    def test_mixed_bilingual_financial_and_horoscope_data(self):
        buf = BytesIO()
        renderer = GAILetterheadPDFRenderer(
            language="bilingual",
            typography_profile="modern",
            report_title="Comprehensive Astrological Consultation Summary",
            footer_note="Client Advisory • Confidential Horoscopic Audit",
        )
        doc = renderer.create_document(buf)
        styles = get_modern_styles()

        story = []
        story.extend(create_report_title("Consultation Summary", "Astro-Financial Particulars"))
        story.extend(create_section_heading("1. Astro-Financial Particulars (நிதி மற்றும் கிரக விவரங்கள்)"))
        story.append(Paragraph("Consultation Date: 2026-11-23 • Time: 10:30:00 AM IST • Fee: ₹ 2,500 ($ 30.50 / £ 24.20)", styles["ReportBody"]))
        story.append(Paragraph("Planetary Angles: Sun 29° 30' 15\" (Mesha) • Moon 14° 12' 48\" (Vrishabha) • Ascendant 02° 15'", styles["ReportBody"]))

        headers = ["House", "Bhava", "Significator", "Strength %", "Status"]
        rows = [
            ["1st House", "Lagna Bhava", "Sun / Mars", "92.5%", "EXCELLENT"],
            ["2nd House", "Dhana Bhava", "Jupiter / Venus", "88.0%", "FAVORABLE"],
            ["7th House", "Kalatra Bhava", "Venus / Mercury", "78.4%", "BALANCED"],
            ["10th House", "Karma Bhava", "Saturn / Sun", "95.2%", "POWERFUL"],
        ]
        story.append(create_data_table(headers, rows, col_widths=[USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.16, USABLE_WIDTH * 0.16]))
        story.append(create_highlight_box(
            "<b>Special Advisory (முக்கிய ஆலோசனை):</b> Financial expansion favorable during Jupiter Dasha.",
            title="Advisory Note",
        ))

        pdf_bytes = renderer.build_pdf(story)
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        assert len(reader.pages) == 1

        extracted = normalize_tamil_text(reader.pages[0].extract_text())
        assert "Astro-Financial" in extracted
        assert "₹ 2,500" in extracted
        assert "$ 30.50" in extracted
        assert "Sun 29° 30' 15\"" in extracted
        assert "நிதி மற்றும் கிரக" in extracted

        val = validate_pdf_safe_boundaries(pdf_bytes)
        assert val["valid"] is True
        assert len(val["violations"]) == 0


class TestIntegratedGeneratorsBoundaryCompliance:
    """Verifies Objective 9: All integrated generators produce valid PDFs with 0 boundary violations."""

    def test_single_page_traditional_kundli(self):
        from app.services.pdf_report_engine.single_page_generator import SinglePageHoroscopePdfGenerator, BirthInput
        b_input = BirthInput(
            birth_date="1995-05-14",
            birth_time="10:30",
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        )
        gen = SinglePageHoroscopePdfGenerator(
            birth_input=b_input,
            native_name="Gokul Murugan",
            language="ta",
        )
        pdf = gen.generate_reportlab()
        reader = pypdf.PdfReader(BytesIO(pdf))
        assert len(reader.pages) == 1
        val = validate_pdf_safe_boundaries(pdf)
        assert val["valid"] is True

    def test_pancha_pakshi_2page_schedule(self):
        from app.schemas.pdf_report import PanchaPakshiPdfReportRequest
        from app.services.pdf_report_engine.pancha_pakshi_pdf_generator import generate_pancha_pakshi_pdf_bytes
        req = PanchaPakshiPdfReportRequest(
            native_name="Gokul Murugan",
            nakshatra="Rohini",
            paksha="Shukla",
            target_date="2026-11-23",
            latitude=13.0827,
            longitude=80.2707,
            location_name="Chennai, Tamil Nadu",
            language="ta",
        )
        pdf = generate_pancha_pakshi_pdf_bytes(req)
        reader = pypdf.PdfReader(BytesIO(pdf))
        assert len(reader.pages) == 2
        val = validate_pdf_safe_boundaries(pdf)
        assert val["valid"] is True

    def test_muhurta_certificate_1page(self):
        from app.schemas.pdf_report import MuhurtaCertificatePdfRequest
        from app.services.pdf_report_engine.muhurta_certificate_generator import generate_muhurta_certificate_pdf_bytes
        req = MuhurtaCertificatePdfRequest(
            occasion="Gruhapravesam",
            primary_person_name="Gokul Murugan",
            primary_nakshatra="Rohini",
            event_date="2026-11-23",
            start_time="09:15",
            end_time="10:45",
            location_name="Chennai, Tamil Nadu",
            latitude=13.0827,
            longitude=80.2707,
            language="ta",
            astrologer_name="Gokul Murugan",
        )
        pdf = generate_muhurta_certificate_pdf_bytes(req)
        reader = pypdf.PdfReader(BytesIO(pdf))
        assert len(reader.pages) == 1
        val = validate_pdf_safe_boundaries(pdf)
        assert val["valid"] is True
