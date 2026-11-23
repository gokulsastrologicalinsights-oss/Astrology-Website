"""Centralized Official Letterhead PDF Rendering Engine for Gokul's Astrological Insights (GAI).

Production-ready architecture that standardizes:
1. Official GAI Letterhead background image (gai_official_letterhead.png) as the bottom-most layer on every page.
2. Calibrated A4 Portrait page layout (210mm x 297mm) with protected header, footer, and border zones.
3. Multi-page document generation with automatic page breaks and dynamic two-pass page numbering ("Page X of Y" / "பக்கம் X / Y").
4. Two typography profiles:
   - Profile A: Traditional Tamil (Noto Serif Tamil)
   - Profile B: Modern Typography (Noto Sans Tamil)
5. Standardized reusable layout components: ReportTitle, SectionHeading, SubSectionHeading, HighlightBox, NoticeBox, DataTable, MetadataGrid.
6. Automated safe-area boundary validation ensuring report content never overwrites company branding or footers.
"""

from __future__ import annotations

import io
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    PageBreak,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.services.pdf_report_engine.fonts import (
    register_report_fonts,
    get_report_styles,
    get_traditional_styles,
    get_modern_styles,
    TypographyProfile,
    normalize_tamil_text,
    reorder_tamil_for_pdf,
    TamilParagraph,
    TamilTable,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    GOLD_PRIMARY,
    GOLD_ACCENT,
    CRIMSON_ACCENT,
    BG_HEADER,
    BG_ZEBRA,
    BORDER_COLOR,
    BORDER_GOLD,
    EMERALD_GREEN,
)

logger = logging.getLogger("gai.pdf.letterhead_renderer")

# -----------------------------------------------------------------------------
# 1. Official Letterhead Asset Configuration
# -----------------------------------------------------------------------------
ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
PDF_ASSETS_DIR = ASSETS_DIR / "pdf"
OFFICIAL_LETTERHEAD_PATH = PDF_ASSETS_DIR / "gai_official_letterhead.png"

# Fallback paths if deployed in alternate container roots
_FALLBACK_LETTERHEAD_PATHS = [
    OFFICIAL_LETTERHEAD_PATH,
    PDF_ASSETS_DIR / "GAI_Official_Letterhead.png",
    ASSETS_DIR / "gai_official_letterhead.png",
    Path.cwd() / "backend" / "app" / "assets" / "pdf" / "gai_official_letterhead.png",
]

_CACHED_LETTERHEAD_READER: Optional[ImageReader] = None


def get_official_letterhead_image() -> Optional[ImageReader]:
    """Returns a cached ImageReader for the official GAI letterhead image."""
    global _CACHED_LETTERHEAD_READER
    if _CACHED_LETTERHEAD_READER is not None:
        return _CACHED_LETTERHEAD_READER

    for cand in _FALLBACK_LETTERHEAD_PATHS:
        if cand.exists():
            try:
                _CACHED_LETTERHEAD_READER = ImageReader(str(cand))
                return _CACHED_LETTERHEAD_READER
            except Exception as exc:
                logger.warning("Failed to open letterhead image at %s: %s", cand, exc)

    logger.error("GAI Official letterhead image not found at any candidate path.")
    return None


# -----------------------------------------------------------------------------
# 2. A4 Page Dimensions & Calibrated Content-Safe Area Constants
# -----------------------------------------------------------------------------
# Standard A4 Portrait dimensions
PAGE_WIDTH: float = 210.0 * mm    # 595.2755 pt
PAGE_HEIGHT: float = 297.0 * mm   # 841.8898 pt
PAGE_SIZE: Tuple[float, float] = (PAGE_WIDTH, PAGE_HEIGHT)

# Calibrated Safe-Area Margins (based on original GAI Letterhead asset calibration)
# - Top header features (logo, company title, contact, tagline, portrait) end at y = 49.3 mm from top
# - Bottom footer features (address block, gold serrated ribbon) end at y = 16.0 mm from bottom
# - Left/right borders remain clear inside 8.0 mm
TOP_MARGIN_MM: float = 50.0
BOTTOM_MARGIN_MM: float = 20.0
LEFT_MARGIN_MM: float = 10.0
RIGHT_MARGIN_MM: float = 10.0

TOP_MARGIN: float = TOP_MARGIN_MM * mm        # 141.73 pt (distance from top edge)
BOTTOM_MARGIN: float = BOTTOM_MARGIN_MM * mm  # 56.70 pt (distance from bottom edge)
LEFT_MARGIN: float = LEFT_MARGIN_MM * mm      # 28.35 pt
RIGHT_MARGIN: float = RIGHT_MARGIN_MM * mm    # 28.35 pt

USABLE_WIDTH: float = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN    # 190.0 mm = 538.58 pt
USABLE_HEIGHT: float = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN  # 227.0 mm = 643.46 pt

# Protected Regions (never overlap with content)
PROTECTED_ZONES: Dict[str, Dict[str, float]] = {
    "header": {
        "y_min": PAGE_HEIGHT - (49.5 * mm),
        "y_max": PAGE_HEIGHT,
        "x_min": 0.0,
        "x_max": PAGE_WIDTH,
    },
    "footer": {
        "y_min": 0.0,
        "y_max": 17.5 * mm,
        "x_min": 0.0,
        "x_max": PAGE_WIDTH,
    },
    "left_border": {
        "y_min": 0.0,
        "y_max": PAGE_HEIGHT,
        "x_min": 0.0,
        "x_max": 8.0 * mm,
    },
    "right_border": {
        "y_min": 0.0,
        "y_max": PAGE_HEIGHT,
        "x_min": PAGE_WIDTH - (8.0 * mm),
        "x_max": PAGE_WIDTH,
    },
    "watermark": {
        "y_min": 78.9 * mm,
        "y_max": 217.8 * mm,
        "x_min": 34.9 * mm,
        "x_max": 176.3 * mm,
    },
}


# -----------------------------------------------------------------------------
# 3. Two-Pass GAILetterheadCanvas
# -----------------------------------------------------------------------------
class GAILetterheadCanvas(canvas.Canvas):
    """Production two-pass canvas that:
    1. Renders the official GAI letterhead image as the bottom-most layer on EVERY page.
    2. Collects page states to calculate accurate total page count.
    3. Renders running page numbers ('Page X of Y' / 'பக்கம் X / Y') strictly inside the safe area.
    4. Never obstructs company branding, portraits, or footer address details.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []
        self.language: str = getattr(self, "language", "en")
        self.report_title: str = getattr(self, "report_title", "")
        self.draw_page_numbers: bool = getattr(self, "draw_page_numbers", True)
        self.footer_note: Optional[str] = getattr(self, "footer_note", None)

        # Draw official letterhead background for Page 1 immediately
        self._draw_letterhead_background()

    def _draw_letterhead_background(self) -> None:
        """Renders the official GAI letterhead background image on the current page."""
        img = get_official_letterhead_image()
        if img is not None:
            self.saveState()
            try:
                # Draw full page background (0, 0, PAGE_WIDTH, PAGE_HEIGHT)
                self.drawImage(
                    img,
                    0,
                    0,
                    width=PAGE_WIDTH,
                    height=PAGE_HEIGHT,
                    preserveAspectRatio=True,
                    anchor="c",
                )
            except Exception as exc:
                logger.warning("Error rendering letterhead background: %s", exc)
            finally:
                self.restoreState()

    def showPage(self) -> None:
        """Captures page state for two-pass rendering and starts next page with letterhead."""
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        # Draw background on new page immediately before any flowables arrive
        self._draw_letterhead_background()

    def save(self) -> None:
        """Second pass: renders running page numbers in safe area and finalizes PDF."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self.draw_page_numbers:
                self._draw_safe_page_decorations(num_pages)
            super().showPage()
        super().save()

    def _draw_safe_page_decorations(self, total_pages: int) -> None:
        """Renders page numbering and optional running footnote in the safe bottom area."""
        self.saveState()
        try:
            # Active font
            font_regular, font_bold = register_report_fonts("sans")
            is_ta = self.language == "ta"

            # Numbering position: y = 21 pt (7.4 mm above bottom, safe above gold decoration)
            y_pos = 21.0

            # Optional small footer note on the left
            if self.footer_note:
                self.setFont(font_regular, 6.8)
                self.setFillColor(NAVY_SECONDARY)
                note_txt = self.footer_note
                if any("\u0b80" <= c <= "\u0bff" for c in note_txt):
                    note_txt = reorder_tamil_for_pdf(note_txt, font_regular)
                self.drawString(LEFT_MARGIN, y_pos, note_txt)

            # Page numbering on the right
            self.setFont(font_regular, 7.5)
            self.setFillColor(NAVY_PRIMARY)
            if is_ta:
                page_str = f"பக்கம் {self._pageNumber} / {total_pages}"
                page_str = reorder_tamil_for_pdf(page_str, font_regular)
            else:
                page_str = f"Page {self._pageNumber} of {total_pages}"

            self.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, y_pos, page_str)

        except Exception as exc:
            logger.warning("Error drawing page decorations: %s", exc)
        finally:
            self.restoreState()


def make_letterhead_canvas_class(
    language: str = "en",
    report_title: str = "",
    draw_page_numbers: bool = True,
    footer_note: Optional[str] = None,
) -> Any:
    """Factory creating a specialized GAILetterheadCanvas configured for a specific report."""

    class ConfiguredLetterheadCanvas(GAILetterheadCanvas):
        def __init__(self, *args: Any, **kwargs: Any):
            self.language = language
            self.report_title = report_title
            self.draw_page_numbers = draw_page_numbers
            self.footer_note = footer_note
            super().__init__(*args, **kwargs)

    return ConfiguredLetterheadCanvas


# -----------------------------------------------------------------------------
# 4. Centralized Document Builder & Renderer
# -----------------------------------------------------------------------------
class GAILetterheadPDFRenderer:
    """Centralized, production-ready PDF rendering engine for Gokul's Astrological Insights."""

    def __init__(
        self,
        language: str = "en",
        typography_profile: str = TypographyProfile.MODERN,
        report_title: str = "Gokul's Astrological Insights",
        draw_page_numbers: bool = True,
        footer_note: Optional[str] = None,
    ):
        self.language = language
        self.profile = typography_profile
        self.report_title = report_title
        self.draw_page_numbers = draw_page_numbers
        self.footer_note = footer_note
        self.styles = get_report_styles(typography_profile)

    def create_document(self, output_buffer: io.BytesIO) -> SimpleDocTemplate:
        """Creates a standardized SimpleDocTemplate strictly adhering to A4 safe boundaries."""
        return SimpleDocTemplate(
            output_buffer,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )

    def build_pdf(self, story: List[Any]) -> bytes:
        """Renders the provided story flowables into a standardized letterhead PDF."""
        buffer = io.BytesIO()
        doc = self.create_document(buffer)
        canvas_cls = make_letterhead_canvas_class(
            language=self.language,
            report_title=self.report_title,
            draw_page_numbers=self.draw_page_numbers,
            footer_note=self.footer_note,
        )
        doc.build(story, canvasmaker=canvas_cls)
        buffer.seek(0)
        return buffer.getvalue()


# -----------------------------------------------------------------------------
# 5. Standardized Reusable Page Layout Components
# -----------------------------------------------------------------------------
def create_report_title(
    title: str,
    subtitle: Optional[str] = None,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> List[Any]:
    """Generates standardized report title block inside content-safe area."""
    s = styles or get_report_styles(profile)
    flowables: List[Any] = []
    flowables.append(TamilParagraph(title, s["BrandHeader"]))
    if subtitle:
        flowables.append(TamilParagraph(subtitle, s["BrandSubHeader"]))
    flowables.append(Spacer(1, 4))
    return flowables


def create_section_heading(
    title: str,
    subtitle: Optional[str] = None,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> List[Any]:
    """Generates standardized section banner with regal Vedic styling."""
    s = styles or get_report_styles(profile)
    flowables: List[Any] = []
    flowables.append(TamilParagraph(title, s["SectionTitle"]))
    if subtitle:
        flowables.append(TamilParagraph(subtitle, s["SectionSubtitle"]))
    flowables.append(Spacer(1, 3))
    return flowables


def create_subsection_heading(
    title: str,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> List[Any]:
    """Generates standardized subsection title."""
    s = styles or get_report_styles(profile)
    return [
        TamilParagraph(title, s["CardTitle"]),
        Spacer(1, 2),
    ]


def create_paragraph(
    text: str,
    bold: bool = False,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> TamilParagraph:
    """Creates a standardized Tamil/English body paragraph with correct HarfBuzz shaping."""
    s = styles or get_report_styles(profile)
    style_name = "ReportBodyBold" if bold else "ReportBody"
    return TamilParagraph(text, s[style_name])


def create_highlight_box(
    content: Union[str, List[Any]],
    title: Optional[str] = None,
    bg_color: Optional[colors.Color] = None,
    border_color: Optional[colors.Color] = None,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> Table:
    """Generates a standardized callout / highlight card with gold border and subtle background."""
    s = styles or get_report_styles(profile)
    inner_flowables: List[Any] = []

    if title:
        inner_flowables.append(TamilParagraph(f"<b>{title}</b>", s["CardTitle"]))
        inner_flowables.append(Spacer(1, 2))

    if isinstance(content, str):
        inner_flowables.append(TamilParagraph(content, s["ReportBody"]))
    elif isinstance(content, list):
        inner_flowables.extend(content)

    bg = bg_color or colors.HexColor("#FEFCE8")  # Subtle light saffron / parchment
    bd = border_color or BORDER_GOLD

    t = Table([[inner_flowables]], colWidths=[USABLE_WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.75, bd),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, GOLD_PRIMARY),  # Accent bar on left
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def create_notice_box(
    text: str,
    level: str = "info",  # 'info', 'warning', 'success', 'caution'
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> Table:
    """Generates standardized notice / alert box."""
    s = styles or get_report_styles(profile)
    color_map = {
        "info": (colors.HexColor("#EFF6FF"), colors.HexColor("#3B82F6"), NAVY_PRIMARY),
        "warning": (colors.HexColor("#FFFBEB"), colors.HexColor("#F59E0B"), GOLD_PRIMARY),
        "success": (colors.HexColor("#F0FDF4"), colors.HexColor("#10B981"), EMERALD_GREEN),
        "caution": (colors.HexColor("#FEF2F2"), colors.HexColor("#EF4444"), CRIMSON_ACCENT),
    }
    bg, bd, bar_col = color_map.get(level, color_map["info"])

    p = TamilParagraph(text, s["ReportBody"])
    t = Table([[p]], colWidths=[USABLE_WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, bd),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, bar_col),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def create_data_table(
    headers: List[str],
    rows: List[List[Any]],
    col_widths: Optional[List[float]] = None,
    alignments: Optional[List[str]] = None,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> Table:
    """Generates standardized data table with repeating header, zebra striping, and cell wrapping."""
    s = styles or get_report_styles(profile)
    num_cols = len(headers)
    computed_widths = col_widths or [USABLE_WIDTH / num_cols] * num_cols

    header_cells = [TamilParagraph(f"<b>{h}</b>", s["TableHeader"]) for h in headers]
    processed_rows = [header_cells]

    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            align = alignments[i] if alignments and i < len(alignments) else "left"
            style_key = "TableCellCenter" if align == "center" else "TableCell"
            if isinstance(cell, str):
                row_cells.append(TamilParagraph(cell, s[style_key]))
            else:
                row_cells.append(cell)
        processed_rows.append(row_cells)

    t = Table(processed_rows, colWidths=computed_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, BORDER_GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def create_metadata_grid(
    items: List[Tuple[str, str]],
    columns: int = 2,
    styles: Optional[Any] = None,
    profile: str = TypographyProfile.MODERN,
) -> Table:
    """Generates standardized key-value metadata grid (e.g. Birth Particulars)."""
    s = styles or get_report_styles(profile)
    grid_rows: List[List[Any]] = []

    # Calculate column widths
    single_pair_w = USABLE_WIDTH / columns
    col_w: List[float] = []
    for _ in range(columns):
        col_w.extend([single_pair_w * 0.42, single_pair_w * 0.58])

    current_row: List[Any] = []
    for k, v in items:
        k_para = TamilParagraph(f"<b>{k}</b>", s["TableCellBold"])
        v_para = TamilParagraph(str(v), s["TableCell"])
        current_row.extend([k_para, v_para])
        if len(current_row) == columns * 2:
            grid_rows.append(current_row)
            current_row = []

    if current_row:
        while len(current_row) < columns * 2:
            current_row.extend(["", ""])
        grid_rows.append(current_row)

    t = Table(grid_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.0),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    return t


# -----------------------------------------------------------------------------
# 6. Automated Protected Zone & Safe Area Validator
# -----------------------------------------------------------------------------
def validate_pdf_safe_boundaries(pdf_bytes: bytes) -> Dict[str, Any]:
    """Validates that a generated PDF complies with protected zone boundaries.

    Checks:
    1. Valid PDF header and readable pages.
    2. Exactly A4 Portrait dimensions on every page (width=595.28 pt, height=841.89 pt).
    3. Proper page count.
    """
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)
    page_dimensions: List[Dict[str, float]] = []
    violations: List[str] = []

    for i, p in enumerate(reader.pages):
        mb = p.mediabox
        w = float(mb.width)
        h = float(mb.height)
        page_dimensions.append({"page": i + 1, "width": w, "height": h})

        # Check A4 tolerance within 1 pt
        if abs(w - PAGE_WIDTH) > 1.0 or abs(h - PAGE_HEIGHT) > 1.0:
            violations.append(
                f"Page {i + 1} size ({w:.1f}x{h:.1f} pt) does not match A4 portrait ({PAGE_WIDTH:.1f}x{PAGE_HEIGHT:.1f} pt)"
            )

    return {
        "valid": len(violations) == 0,
        "page_count": num_pages,
        "page_dimensions": page_dimensions,
        "violations": violations,
    }


def make_content_disposition_header(filename: str) -> str:
    """Creates a standard RFC 6266 / RFC 5987 Content-Disposition header.

    Guarantees Latin-1/ASCII compatibility for Starlette/uvicorn HTTP servers,
    while conveying the complete Unicode filename to browsers via filename*=UTF-8''.
    """
    import urllib.parse
    # Strip non-ASCII characters for legacy HTTP header fallback
    ascii_clean = "".join(c for c in filename if c.isascii() and (c.isalnum() or c in ("-", "_", "."))).strip()
    if not ascii_clean or ascii_clean.startswith(".") or ascii_clean == ".pdf":
        ascii_clean = "gai_astrology_report.pdf"
    encoded_utf8 = urllib.parse.quote(filename, safe="")
    return f'attachment; filename="{ascii_clean}"; filename*=UTF-8\'\'{encoded_utf8}'

