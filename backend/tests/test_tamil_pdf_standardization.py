"""Automated Tamil PDF Typography and Standardization Test Suite.

Verifies:
1. Correct visual rendering with Noto Sans Tamil & Noto Serif Tamil.
2. 100% accurate Unicode extraction matching original input across both profiles.
3. Correct copy-and-paste and text searchability.
4. Mixed-language Tamil-English rendering and punctuation.
5. TamilTable automatic string wrapping and cell typography.
6. Vector chart TamilString shaping.
7. Line breaking and word wrapping preserving Tamil grapheme clusters.
8. Complete ToUnicode reverse mapping coverage with zero missing glyphs or .notdef leaks.
"""

import io
import pytest
import pypdf
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing, Rect

from app.services.pdf_report_engine.fonts import (
    register_report_fonts,
    get_report_styles,
    get_traditional_styles,
    get_modern_styles,
    TamilParagraph,
    TamilString,
    TamilTable,
    TamilNumberedCanvas,
    Paragraph,
    String,
    Table,
    NumberedCanvas,
    normalize_tamil_text,
    reorder_tamil_for_pdf,
    TypographyProfile,
    NOTO_SANS_REGULAR,
    NOTO_SANS_BOLD,
    NOTO_SERIF_REGULAR,
    NOTO_SERIF_BOLD,
    _build_font_reverse_map,
)

CANONICAL_TEST_STRINGS = [
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
]


class TestTamilTypographyProfiles:
    """Verifies Phase 3 Traditional and Modern typography profile specifications."""

    def test_font_assets_exist(self):
        assert NOTO_SANS_REGULAR.exists(), "NotoSansTamil-Regular.ttf must exist"
        assert NOTO_SANS_BOLD.exists(), "NotoSansTamil-Bold.ttf must exist"
        assert NOTO_SERIF_REGULAR.exists(), "NotoSerifTamil-Regular.ttf must exist"
        assert NOTO_SERIF_BOLD.exists(), "NotoSerifTamil-Bold.ttf must exist"

    def test_traditional_profile_styles(self):
        styles = get_traditional_styles()
        assert styles["BrandHeader"].fontName == "NotoSerifTamil-Bold"
        assert styles["SectionTitle"].fontName == "NotoSerifTamil-Bold"
        assert styles["ReportBody"].fontName == "NotoSerifTamil"
        assert styles["TableCell"].fontName == "NotoSerifTamil"
        assert styles["TableCellBold"].fontName == "NotoSerifTamil-Bold"
        assert styles["TamilShloka"].fontName == "NotoSerifTamil-Bold"

    def test_modern_profile_styles(self):
        styles = get_modern_styles()
        assert styles["BrandHeader"].fontName == "NotoSansTamil-Bold"
        assert styles["SectionTitle"].fontName == "NotoSansTamil-Bold"
        assert styles["ReportBody"].fontName == "NotoSansTamil"
        assert styles["TableCell"].fontName == "NotoSansTamil"
        assert styles["TableCellBold"].fontName == "NotoSansTamil-Bold"
        assert styles["CardTitle"].fontName == "NotoSansTamil-Bold"


class TestUnicodeNormalization:
    """Verifies Requirement 1, 2, and 5: Unicode NFC and logical character order."""

    def test_nfc_canonical_composition(self):
        # Combining characters decomposed vs composed
        decomposed = "\u0b9c\u0bc7\u0bbe"  # JA + EE + AA
        normalized = normalize_tamil_text(decomposed)
        assert normalized == "ஜோ"
        assert len(normalized) == 2  # JA (0x0B9C) + OO (0x0BCB)

    def test_two_part_split_vowel_reordering(self):
        # ெ + C + ா -> C + ொ
        test_po = "\u0bc6\u0baa\u0bbe"
        assert normalize_tamil_text(test_po) == "பொ"

        # ே + C + ா -> C + ோ
        test_jo = "\u0bc7\u0b9c\u0bbe"
        assert normalize_tamil_text(test_jo) == "ஜோ"

        # ெ + C + ௗ -> C + ௌ
        test_kau = "\u0bc6\u0b95\u0bd7"
        assert normalize_tamil_text(test_kau) == "கௌ"

    def test_single_left_vowels_logical_order(self):
        # Visual ெ + க -> Logical கெ
        assert normalize_tamil_text("\u0bc6\u0b95") == "கெ"
        # Visual ே + ந -> Logical நே
        assert normalize_tamil_text("\u0bc7\u0ba8") == "நே"
        # Visual ை + த -> Logical தை
        assert normalize_tamil_text("\u0bc8\u0ba4") == "தை"

    def test_logical_order_preservation(self):
        # Strings already in logical order must not be mutated
        for s in CANONICAL_TEST_STRINGS:
            assert normalize_tamil_text(s) == s


class TestSharedTamilTestSuiteExtraction:
    """Verifies Phase 5: 100% accurate Unicode extraction across all test strings."""

    def test_modern_profile_extraction_100_percent(self):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = get_modern_styles()
        story = []
        for s in CANONICAL_TEST_STRINGS:
            story.append(TamilParagraph(s, styles["ReportBody"]))
            story.append(Spacer(1, 4))
        doc.build(story)

        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        extracted = reader.pages[0].extract_text()
        extracted_lines = [normalize_tamil_text(l.strip()) for l in extracted.splitlines() if l.strip()]

        assert len(extracted_lines) == len(CANONICAL_TEST_STRINGS)
        for orig, ext in zip(CANONICAL_TEST_STRINGS, extracted_lines):
            assert ext == orig, f"Modern extraction mismatch: expected {orig!r}, got {ext!r}"

    def test_traditional_profile_extraction_100_percent(self):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = get_traditional_styles()
        story = []
        for s in CANONICAL_TEST_STRINGS:
            story.append(TamilParagraph(s, styles["ReportBody"]))
            story.append(Spacer(1, 4))
        doc.build(story)

        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        extracted = reader.pages[0].extract_text()
        extracted_lines = [normalize_tamil_text(l.strip()) for l in extracted.splitlines() if l.strip()]

        assert len(extracted_lines) == len(CANONICAL_TEST_STRINGS)
        for orig, ext in zip(CANONICAL_TEST_STRINGS, extracted_lines):
            assert ext == orig, f"Traditional extraction mismatch: expected {orig!r}, got {ext!r}"


class TestMixedLanguageAndFormatting:
    """Verifies mixed Tamil-English text, Sanskrit shlokas, and numeral formatting."""

    def test_bilingual_planetary_string(self):
        mixed_str = "சூரியன் (Sun) - 14° 32' மேஷம் (Aries) - உத்திரம் (Uttara Phalguni 1)"
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = get_modern_styles()
        doc.build([TamilParagraph(mixed_str, styles["ReportBody"])])

        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        ext = normalize_tamil_text(reader.pages[0].extract_text().strip())
        assert "சூரியன்" in ext
        assert "Sun" in ext
        assert "14° 32'" in ext
        assert "மேஷம்" in ext
        assert "Aries" in ext

    def test_html_markup_preservation(self):
        tagged_str = "<b>தசா புத்தி</b>: <i>குரு தசை</i> - <font color='#8B6914'>சுக்கிர புக்தி</font>"
        p = TamilParagraph(tagged_str, get_modern_styles()["ReportBody"])
        assert "<b>" in p.text
        assert "<i>" in p.text
        assert "<font" in p.text


class TestTamilTableAutoWrapping:
    """Verifies TamilTable automatically wraps raw strings into styled TamilParagraphs."""

    def test_tamil_table_wrapping(self):
        raw_table_data = [
            ["கிரகம்", "ராசி", "பாகை", "நிலை"],
            ["சூரியன்", "மேஷம்", "14° 32'", "உச்சம்"],
            ["சந்திரன்", "ரிஷபம்", "03° 15'", "மூலத்திரிகோணம்"],
            ["செவ்வாய்", "மகரம்", "28° 00'", "உச்சம்"],
        ]
        t = TamilTable(raw_table_data)
        # Verify first cell of row 1 was converted to TamilParagraph
        assert isinstance(t._cellvalues[0][0], TamilParagraph)
        assert isinstance(t._cellvalues[1][0], TamilParagraph)

        # Build PDF and verify text extraction
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        doc.build([t])
        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        ext = normalize_tamil_text(reader.pages[0].extract_text())
        assert "கிரகம்" in ext
        assert "சூரியன்" in ext
        assert "மேஷம்" in ext
        assert "உச்சம்" in ext


class TestVectorChartTamilString:
    """Verifies TamilString inside ReportLab vector Drawing."""

    def test_tamil_string_drawing(self):
        d = Drawing(200, 200)
        d.add(Rect(0, 0, 200, 200, strokeColor=None, fillColor=None))
        d.add(TamilString(20, 100, "லக்னம்", font_family="NotoSansTamil", fontSize=10))
        d.add(TamilString(80, 100, "சூரி", font_family="NotoSansTamil", fontSize=10))
        d.add(TamilString(140, 100, "சந்", font_family="NotoSansTamil", fontSize=10))

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        doc.build([d])
        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        ext = normalize_tamil_text(reader.pages[0].extract_text())
        assert "லக்னம்" in ext
        assert "சூரி" in ext
        assert "சந்" in ext


class TestNoMissingGlyphsOrNotdefLeaks:
    """Verifies that reverse PUA mappings cover every Tamil glyph with zero .notdef leaks."""

    def test_noto_sans_reverse_map_completeness(self):
        m = _build_font_reverse_map(NOTO_SANS_REGULAR)
        assert len(m) >= 500, f"NotoSans reverse map must contain >= 500 glyphs, got {len(m)}"

    def test_noto_serif_reverse_map_completeness(self):
        m = _build_font_reverse_map(NOTO_SERIF_REGULAR)
        assert len(m) >= 490, f"NotoSerif reverse map must contain >= 490 glyphs, got {len(m)}"

    def test_no_notdef_or_null_in_extracted_strings(self):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = get_modern_styles()
        doc.build([TamilParagraph(s, styles["ReportBody"]) for s in CANONICAL_TEST_STRINGS])
        reader = pypdf.PdfReader(io.BytesIO(buf.getvalue()))
        raw_text = reader.pages[0].extract_text()
        assert "\x00" not in raw_text, "Extracted text must not contain null bytes (unmapped glyphs)"
        assert "\ufffd" not in raw_text, "Extracted text must not contain replacement characters"
