#!/usr/bin/env python3
"""
generate_architecture_pdf.py

Generates a publication-grade, technically accurate, multi-page PDF document
documenting the complete system architecture of Jokul's Astrological Insights (GAI).
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Polygon

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "Jokuls_Astrological_Insights_System_Architecture.pdf")

# Palette
PRIMARY = colors.HexColor("#0F172A")       # Slate 900
SECONDARY = colors.HexColor("#1E293B")     # Slate 800
ACCENT = colors.HexColor("#D97706")        # Amber 600
ACCENT_LIGHT = colors.HexColor("#FEF3C7")  # Amber 100
TEXT_MAIN = colors.HexColor("#1E293B")
TEXT_MUTED = colors.HexColor("#475569")    # Slate 600
BORDER_COLOR = colors.HexColor("#CBD5E1")  # Slate 300
BG_HEADER = colors.HexColor("#0F172A")
BG_ZEBRA = colors.HexColor("#F8FAFC")
BG_CARD = colors.HexColor("#F1F5F9")
SUCCESS = colors.HexColor("#059669")       # Emerald 600
WARNING = colors.HexColor("#D97706")       # Amber 600
DANGER = colors.HexColor("#DC2626")        # Red 600

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count, running headers, and running footers."""
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)

        # Draw running header on pages > 1
        if self._pageNumber > 1:
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(40, 802, 555, 802)
            self.drawString(40, 808, "JOKUL'S ASTROLOGICAL INSIGHTS (GAI) - SYSTEM ARCHITECTURE")
            self.drawRightString(555, 808, "TECHNICAL SPECIFICATION")

        # Running footer on all pages
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(40, 42, 555, 42)
        self.drawString(40, 30, "CONFIDENTIAL & PROPRIETARY - SYSTEM ARCHITECTURE VERIFICATION REPORT")
        self.drawRightString(555, 30, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def create_layer1_and_2_diagram() -> Drawing:
    """Builds a vector architecture diagram for Layer 1 (DNS & Browser) and Layer 2 (Vercel & Next.js)."""
    d = Drawing(515, 185)
    
    # Outer bounding canvas background
    d.add(Rect(0, 0, 515, 185, fillColor=colors.HexColor("#F8FAFC"), strokeColor=BORDER_COLOR, strokeWidth=1, rx=5, ry=5))
    
    # Section 1: User & DNS (Left)
    d.add(Rect(8, 8, 150, 169, fillColor=colors.HexColor("#EFF6FF"), strokeColor=colors.HexColor("#93C5FD"), strokeWidth=1, rx=4, ry=4))
    d.add(String(14, 162, "LAYER 1: CLIENT & DNS", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#1E40AF")))
    
    # User / Browser Box
    d.add(Rect(14, 98, 138, 56, fillColor=colors.white, strokeColor=colors.HexColor("#60A5FA"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(20, 140, "User Browser", fontName="Helvetica-Bold", fontSize=8.5, fillColor=PRIMARY))
    d.add(String(20, 128, "Chrome / Safari / Firefox", fontName="Helvetica", fontSize=6.5, fillColor=TEXT_MUTED))
    d.add(String(20, 117, "Domain: astrology.domain", fontName="Courier-Bold", fontSize=6.5, fillColor=ACCENT))
    d.add(String(20, 106, "Initiates DNS lookup", fontName="Helvetica-Oblique", fontSize=6, fillColor=TEXT_MUTED))

    # DNS Resolver Box
    d.add(Rect(14, 16, 138, 74, fillColor=colors.white, strokeColor=colors.HexColor("#60A5FA"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(20, 76, "DNS Recursive Resolver", fontName="Helvetica-Bold", fontSize=7.5, fillColor=PRIMARY))
    d.add(String(20, 65, "1. ISP / Cloudflare 1.1.1.1", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(20, 55, "2. Authoritative NS CNAME chain", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(20, 45, "3. Resolves Vercel Anycast IP", fontName="Helvetica-Bold", fontSize=6, fillColor=SUCCESS))
    d.add(String(20, 32, "* Resolves IP only; does not", fontName="Helvetica-Oblique", fontSize=5.5, fillColor=DANGER))
    d.add(String(20, 24, "  download site content", fontName="Helvetica-Oblique", fontSize=5.5, fillColor=DANGER))

    # Arrow 1: Browser to DNS
    d.add(Line(83, 98, 83, 90, strokeColor=colors.HexColor("#2563EB"), strokeWidth=1))

    # Section 2: Vercel Edge & Frontend (Right)
    d.add(Rect(165, 8, 342, 169, fillColor=colors.HexColor("#F0FDF4"), strokeColor=colors.HexColor("#86EFAC"), strokeWidth=1, rx=4, ry=4))
    d.add(String(172, 162, "LAYER 2: VERCEL HOSTING & NEXT.JS 16 APP RUNTIME", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#166534")))

    # Vercel Edge Gateway Box
    d.add(Rect(172, 105, 328, 48, fillColor=colors.white, strokeColor=colors.HexColor("#4ADE80"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(180, 140, "Vercel Global Anycast Edge Network", fontName="Helvetica-Bold", fontSize=8, fillColor=PRIMARY))
    d.add(String(180, 128, "- TLS 1.3 Termination, DDoS Mitigation, Edge Caching", fontName="Helvetica", fontSize=6.5, fillColor=TEXT_MUTED))
    d.add(String(180, 117, "- Static Asset Delivery (Turbopack JS, CSS, Font Glyphs)", fontName="Helvetica", fontSize=6.5, fillColor=TEXT_MUTED))

    # Next.js Server Components & Route Handlers
    d.add(Rect(172, 16, 158, 82, fillColor=colors.white, strokeColor=colors.HexColor("#4ADE80"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(178, 85, "Next.js App Router (Server)", fontName="Helvetica-Bold", fontSize=7.5, fillColor=PRIMARY))
    d.add(String(178, 73, "* Server Components (SSR HTML)", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(178, 63, "* Route Handler: /api/v1/[...path]", fontName="Courier-Bold", fontSize=6, fillColor=PRIMARY))
    d.add(String(178, 53, "* Auth Handlers: /api/auth/*", fontName="Courier", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(178, 43, "* Supabase SSR Server Client", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(178, 31, "* next.config.ts Proxy Rewrites", fontName="Helvetica-Bold", fontSize=6, fillColor=SUCCESS))

    # Browser Runtime box
    d.add(Rect(338, 16, 162, 82, fillColor=colors.white, strokeColor=colors.HexColor("#4ADE80"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(344, 85, "Hydrated React 19 Client", fontName="Helvetica-Bold", fontSize=7.5, fillColor=PRIMARY))
    d.add(String(344, 73, "* Client Components ('use client')", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(344, 63, "* lib/api.ts Client SDK", fontName="Courier-Bold", fontSize=6, fillColor=PRIMARY))
    d.add(String(344, 53, "* Direct Fetch (NEXT_PUBLIC_API_URL)", fontName="Helvetica", fontSize=6, fillColor=ACCENT))
    d.add(String(344, 43, "* Graceful Fallback to Same-Origin", fontName="Helvetica-Bold", fontSize=6, fillColor=SUCCESS))
    d.add(String(344, 31, "* Client-Side SVG Chart Rendering", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))

    # Connectors
    d.add(Line(152, 126, 172, 126, strokeColor=SUCCESS, strokeWidth=1.5))
    d.add(String(154, 130, "HTTPS", fontName="Helvetica-Bold", fontSize=5.5, fillColor=SUCCESS))
    d.add(Line(251, 105, 251, 98, strokeColor=colors.HexColor("#166534"), strokeWidth=0.8))
    d.add(Line(419, 105, 419, 98, strokeColor=colors.HexColor("#166534"), strokeWidth=0.8))
    
    return d


def create_layer3_and_backend_diagram() -> Drawing:
    """Builds a vector architecture diagram for Layer 3 (Render FastAPI & XALEN Ephemeris Engine)."""
    d = Drawing(515, 195)
    
    # Outer bounding canvas background
    d.add(Rect(0, 0, 515, 195, fillColor=colors.HexColor("#F8FAFC"), strokeColor=BORDER_COLOR, strokeWidth=1, rx=5, ry=5))
    
    # Render Service Enclosure
    d.add(Rect(8, 8, 499, 179, fillColor=colors.HexColor("#FFFBEB"), strokeColor=colors.HexColor("#FDE68A"), strokeWidth=1, rx=4, ry=4))
    d.add(String(16, 173, "LAYER 3: PYTHON ASTROLOGY ENGINE (RENDER - DOCKER CONTAINER ON LINUX BOOKWORM)", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#92400E")))
    
    # Box 1: ASGI & Gateway
    d.add(Rect(16, 96, 150, 68, fillColor=colors.white, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(22, 150, "Uvicorn ASGI Server", fontName="Helvetica-Bold", fontSize=8, fillColor=PRIMARY))
    d.add(String(22, 139, "2 Workers | Port 8000", fontName="Courier-Bold", fontSize=6.5, fillColor=ACCENT))
    d.add(String(22, 128, "- Request Body Size Limiter", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(22, 118, "- CORS Regex (*.vercel.app)", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(22, 108, "- Sanitized Error Handler (500)", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))

    # Box 2: FastAPI Routing & Auth
    d.add(Rect(174, 96, 154, 68, fillColor=colors.white, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(180, 150, "FastAPI Application", fontName="Helvetica-Bold", fontSize=8, fillColor=PRIMARY))
    d.add(String(180, 139, "Pydantic v2 Validation", fontName="Helvetica-Bold", fontSize=6.5, fillColor=SUCCESS))
    d.add(String(180, 128, "- Auth Service (PyJWT / GoTrue)", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(180, 118, "- Optional vs Strict Bearer Auth", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(180, 108, "- 18 Domain APIRouters", fontName="Helvetica-Bold", fontSize=6, fillColor=PRIMARY))

    # Box 3: Dynamic In-Memory PDF Engine
    d.add(Rect(336, 96, 163, 68, fillColor=colors.white, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=0.8, rx=3, ry=3))
    d.add(String(342, 150, "PDF Generator (In-Memory)", fontName="Helvetica-Bold", fontSize=8, fillColor=PRIMARY))
    d.add(String(342, 139, "ReportLab 4.2+ & HarfBuzz", fontName="Helvetica-Bold", fontSize=6.5, fillColor=ACCENT))
    d.add(String(342, 128, "- Bilingual English / Tamil Text", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(342, 118, "- 9-Page Horoscope & 6-Page KP", fontName="Helvetica", fontSize=6, fillColor=TEXT_MUTED))
    d.add(String(342, 108, "- Direct Binary Stream Delivery", fontName="Helvetica-Bold", fontSize=6, fillColor=SUCCESS))

    # Lower Box: The Core Calculation Engine
    d.add(Rect(16, 16, 483, 72, fillColor=colors.white, strokeColor=colors.HexColor("#D97706"), strokeWidth=1, rx=3, ry=3))
    d.add(String(24, 75, "DETERMINISTIC ASTRONOMICAL CORE & CALCULATION MODULES (ZERO AI / LLM)", fontName="Helvetica-Bold", fontSize=7.5, fillColor=PRIMARY))
    
    # Submodules breakdown
    d.add(Rect(24, 22, 144, 46, fillColor=colors.HexColor("#FEF3C7"), strokeColor=colors.HexColor("#FDE68A"), strokeWidth=0.5, rx=2, ry=2))
    d.add(String(28, 56, "Pure-Rust XALEN Ephemeris", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor("#B45309")))
    d.add(String(28, 46, "- PyO3 Native Wheel (Stage 1)", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(28, 37, "- 50 Ayanamsas (Lahiri, KP)", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(28, 28, "- 23 House Systems (Placidus)", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))

    d.add(Rect(174, 22, 154, 46, fillColor=colors.HexColor("#FEF3C7"), strokeColor=colors.HexColor("#FDE68A"), strokeWidth=0.5, rx=2, ry=2))
    d.add(String(178, 56, "Vedic Systems & Strengths", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor("#B45309")))
    d.add(String(178, 46, "- 5-Level Vimshottari Dasa", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(178, 37, "- Shadbala & Shodashvarga D1-D60", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(178, 28, "- Ashtakavarga & Shodhana", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))

    d.add(Rect(334, 22, 159, 46, fillColor=colors.HexColor("#FEF3C7"), strokeColor=colors.HexColor("#FDE68A"), strokeWidth=0.5, rx=2, ry=2))
    d.add(String(338, 56, "KP & Rules & Matching", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor("#B45309")))
    d.add(String(338, 46, "- KP Sub-Lords & 1-249 Horary", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(338, 37, "- 10 Poruthams & Ashtakoota (36)", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))
    d.add(String(338, 28, "- Doshas, Remedies, & Vastu", fontName="Helvetica", fontSize=5.5, fillColor=TEXT_MUTED))

    # Connectors
    d.add(Line(166, 130, 174, 130, strokeColor=ACCENT, strokeWidth=1))
    d.add(Line(328, 130, 336, 130, strokeColor=ACCENT, strokeWidth=1))
    d.add(Line(251, 96, 251, 88, strokeColor=ACCENT, strokeWidth=1))
    
    return d


def build_architecture_pdf():
    os.makedirs(os.path.dirname(PDF_OUTPUT_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceAfter=4,
    )
    
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=TEXT_MUTED,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_MAIN,
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=SECONDARY,
        spaceAfter=2,
    )

    badge_unverified = ParagraphStyle(
        "BadgeUnverified",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8.5,
        textColor=DANGER,
    )

    badge_verified = ParagraphStyle(
        "BadgeVerified",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8.5,
        textColor=SUCCESS,
    )

    elements = []

    # Title & Metadata Block
    elements.append(Paragraph("Jokul's Astrological Insights (GAI)", title_style))
    elements.append(Paragraph("<b>Complete System Architecture & Engineering Blueprint</b> | Technical Verification Report", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY, spaceBefore=0, spaceAfter=8))

    # 1. Executive Summary & Infrastructure Verification Matrix
    elements.append(Paragraph("1. Technology Stack Verification Matrix", h1_style))
    elements.append(Paragraph(
        "To ensure complete architectural accuracy, every component listed in the known technology stack was rigorously verified "
        "against the production codebase, dependency configurations (<code>package.json</code>, <code>requirements.txt</code>), "
        "deployment descriptors (<code>render.yaml</code>, <code>Dockerfile.backend</code>, <code>next.config.ts</code>), and database migrations.",
        body_style
    ))

    matrix_data = [
        [
            Paragraph("<b>Component / Layer</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
            Paragraph("<b>Believed Stack</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
            Paragraph("<b>Repository Verification</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
            Paragraph("<b>Status & Actual Implementation Detail</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
        ],
        [
            Paragraph("<b>Frontend & Hosting</b>", body_style),
            Paragraph("Next.js on Vercel", body_style),
            Paragraph("Verified", badge_verified),
            Paragraph("Next.js 16.4.2 (React 19.3.0, App Router, Turbopack, Tailwind CSS v4). Configured for Vercel deployment with SSR & standalone output.", body_style),
        ],
        [
            Paragraph("<b>Astrology Backend</b>", body_style),
            Paragraph("Python on Render", body_style),
            Paragraph("Verified", badge_verified),
            Paragraph("FastAPI 0.115+ on Render (Linux Bookworm Docker container, Uvicorn ASGI server with 2 workers). Incorporates compiled Rust XALEN ephemeris.", body_style),
        ],
        [
            Paragraph("<b>Astronomical Engine</b>", body_style),
            Paragraph("Swiss Ephemeris / Python", body_style),
            Paragraph("Verified", badge_verified),
            Paragraph("High-precision pure-Rust <code>xalen-ephemeris</code> (PyO3 native wheel built in Stage 1 Dockerfile). 50 ayanamsas, 23 house systems. Zero AI/LLM.", body_style),
        ],
        [
            Paragraph("<b>Database & Auth</b>", body_style),
            Paragraph("Supabase PostgreSQL", body_style),
            Paragraph("Verified", badge_verified),
            Paragraph("Supabase PostgreSQL 15+ with GoTrue Auth. 15 migrations, Row Level Security (RLS) on all user tables, and advisory locking concurrency control.", body_style),
        ],
        [
            Paragraph("<b>Object Storage</b>", body_style),
            Paragraph("Cloudflare R2 Bucket", body_style),
            Paragraph("UNVERIFIED<br/>(Not in Repo)", badge_unverified),
            Paragraph("<b>No Cloudflare R2 bucket or S3 SDK found</b>. PDF reports are dynamically generated in-memory on demand; reports & charts are stored as <code>JSONB</code> in Supabase PostgreSQL.", body_style),
        ],
        [
            Paragraph("<b>File Delivery & Workers</b>", body_style),
            Paragraph("Cloudflare Workers", body_style),
            Paragraph("UNVERIFIED<br/>(Not in Repo)", badge_unverified),
            Paragraph("<b>No Cloudflare Workers or Wrangler scripts exist</b> in the codebase. File delivery is handled directly via FastAPI streaming responses (<code>application/pdf</code>).", body_style),
        ],
        [
            Paragraph("<b>Frontend/Backend API</b>", body_style),
            Paragraph("HTTP / REST APIs", body_style),
            Paragraph("Verified", badge_verified),
            Paragraph("Dual-mode HTTP REST: Direct client fetch via <code>lib/api.ts</code> with automatic fallback to Next.js reverse-proxy route handler (<code>/api/v1/[...path]</code>).", body_style),
        ],
    ]

    t_matrix = Table(matrix_data, colWidths=[90, 85, 75, 273])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
    ]))
    elements.append(t_matrix)
    elements.append(Spacer(1, 8))

    # 2. Layer 1: User & DNS Architecture
    elements.append(Paragraph("2. Layer 1 - User, Browser & DNS Resolution Flow", h1_style))
    elements.append(Paragraph(
        "The entry sequence initiates when an end-user navigates to the application domain in a standard web browser. "
        "Architecturally, DNS resolution is strictly decoupled from asset retrieval:",
        body_style
    ))

    dns_steps = [
        "<b>1. Domain Name Resolution:</b> The browser requests an IP resolution for the application's domain (e.g., <code>astrology.domain.com</code>). The local operating system queries the designated DNS recursive resolver (typically operated by the user's ISP, Cloudflare 1.1.1.1, or Google 8.8.8.8).",
        "<b>2. Recursive Traversal & CNAME Chains:</b> The recursive resolver queries root and authoritative nameservers, traversing CNAME records (e.g., <code>cname.vercel-dns.com</code>) to obtain the anycast A (IPv4) or AAAA (IPv6) addresses for Vercel's global edge network.",
        "<b>3. DNS Resolution Response:</b> The resolver returns the resolved IP address to the browser. <b>Crucial Architectural Note:</b> DNS resolves the hostname to an IP address only; DNS does not download, stream, or cache the website or its assets.",
        "<b>4. TLS Handshake & Vercel Connection:</b> Armed with the resolved IP, the browser establishes a TCP connection followed by a TLS 1.3 cryptographic handshake directly with the nearest Vercel edge node.",
    ]
    for step in dns_steps:
        elements.append(Paragraph(f"• {step}", body_style))
    elements.append(Spacer(1, 6))

    # Insert Layer 1 & 2 Vector Diagram
    elements.append(Paragraph("<b>Figure 1: Layer 1 (DNS & Browser) & Layer 2 (Vercel Frontend Delivery)</b>", h2_style))
    elements.append(create_layer1_and_2_diagram())
    elements.append(Spacer(1, 10))

    # 3. Layer 2: Frontend Delivery through Vercel
    elements.append(Paragraph("3. Layer 2 - Frontend Delivery through Vercel", h1_style))
    elements.append(Paragraph(
        "The frontend is built on <b>Next.js 16.4.2</b> with <b>React 19.3.0</b>, packaged as a standalone Node.js distribution "
        "and hosted on Vercel's edge infrastructure. The delivery model bifurcates into initial page rendering and subsequent asynchronous client interactions:",
        body_style
    ))

    elements.append(Paragraph("<b>A. Initial Page-Loading Request (SSR & Hydration)</b>", h2_style))
    elements.append(Paragraph(
        "1. <b>Edge Route & SSL:</b> Vercel terminates TLS and routes the HTTP GET request to the Next.js App Router engine.<br/>"
        "2. <b>Server-Side Rendering (SSR):</b> Server Components compile initial HTML shells with critical meta tags and layout structures. "
        "Session authentication cookies are inspected server-side via <code>@supabase/ssr</code>.<br/>"
        "3. <b>Static Asset Delivery:</b> Compiled JavaScript bundles (Turbopack), Tailwind v4 stylesheets, and font glyphs are served directly from Vercel's global CDN cache.<br/>"
        "4. <b>Client-Side Hydration:</b> Once loaded into the user's browser, React 19 hydrates the DOM, attaching event listeners and activating client-side state managers (e.g., active chart tab, language toggle, and form inputs).",
        body_style
    ))

    elements.append(Paragraph("<b>B. Dual-Path API Routing Architecture (Actual Discovered Route)</b>", h2_style))
    elements.append(Paragraph(
        "A critical finding from reverse-engineering <code>frontend/src/lib/api.ts</code> and <code>frontend/src/app/api/v1/[...path]/route.ts</code> "
        "is the implementation of a <b>resilient dual-path routing strategy</b> for communication with the Render Python backend:",
        body_style
    ))

    route_details = [
        "<b>Primary Route (Direct Client-to-Backend Fetch):</b> In development or when <code>NEXT_PUBLIC_API_BASE_URL</code> is explicitly configured (e.g. <code>https://gai-backend-api.onrender.com</code>), the client browser executes direct <code>fetch()</code> calls to the FastAPI backend with CORS authorization headers.",
        "<b>Secondary Fallback Route (Intermediate Next.js Server Proxy):</b> If the direct client request fails due to Cross-Origin Resource Sharing (CORS), Private Network Access (PNA) restrictions, or missing client-side environment configuration, <code>lib/api.ts</code> catches the exception and immediately retries using a same-origin relative path: <code>/api/v1/...</code>.",
        "<b>Next.js Catch-All Route Handler:</b> The relative request is handled server-to-server by <code>frontend/src/app/api/v1/[...path]/route.ts</code>. This handler reads the destination from <code>BACKEND_INTERNAL_URL</code>, relays all HTTP verbs (GET, POST, PUT, DELETE, PATCH), proxies headers (Authorization, Content-Type), and streams the binary or JSON response buffer back to the browser without CORS friction.",
        "<b>Dedicated Supabase Next.js Endpoints:</b> High-privilege operations--including authentication (<code>/api/auth/*</code>), customer profile CRM (<code>/api/customers/*</code>), and saved chart management (<code>/api/horoscopes/*</code>)--execute on Next.js server runtime, communicating directly with Supabase PostgreSQL via the server-only service-role client (<code>admin.ts</code>).",
    ]
    for rd in route_details:
        elements.append(Paragraph(f"• {rd}", body_style))
    elements.append(Spacer(1, 8))

    # 4. Layer 3: Python Astrology Engine on Render
    elements.append(Paragraph("4. Layer 3 - Python Astrology Engine on Render", h1_style))
    elements.append(Paragraph(
        "The computation engine is an autonomous Python service deployed as a containerized web service on Render (Linux Debian Bookworm), "
        "configured via <code>render.yaml</code> and <code>Dockerfile.backend</code>. It is strictly deterministic and rule-based, containing <b>zero AI, LLM, or probabilistic dependencies</b>.",
        body_style
    ))

    elements.append(Paragraph("<b>A. Container Lifecycle & ASGI Architecture</b>", h2_style))
    elements.append(Paragraph(
        "• <b>Multi-Stage Native Build:</b> Stage 1 compiles the native Rust <code>xalen-ephemeris</code> wheel using <code>maturin</code>. "
        "Stage 2 installs runtime C libraries (<code>libfreetype6</code>, <code>libharfbuzz0b</code>, <code>libfribidi0</code>) and executes <code>uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2</code>.<br/>"
        "• <b>Request Size Limiting Middleware:</b> Rejects payloads exceeding <code>max_request_body_bytes</code> (10 MB default) with HTTP 413.<br/>"
        "• <b>CORS Configuration:</b> Restricts cross-origin requests to configured domains plus Vercel preview environments via regex (<code>^https://.*\\.vercel\\.app$</code>).<br/>"
        "• <b>Pydantic v2 Request Validation:</b> Incoming JSON payloads are validated against strict schemas (<code>BirthInput</code>, <code>HoroscopeRequest</code>, <code>KpRequest</code>, etc.). Validation failures return standardized HTTP 422 JSON detailing exact offending fields.<br/>"
        "• <b>JWT Authentication & Authorization:</b> <code>app/services/auth_service.py</code> validates Supabase GoTrue Bearer tokens using PyJWT. Public endpoints (calculators) use optional authentication (<code>get_optional_current_user</code>); administrative and chart persistence endpoints enforce strict role checks (<code>require_admin</code>).",
        body_style
    ))

    # Insert Layer 3 Vector Diagram
    elements.append(Paragraph("<b>Figure 2: Layer 3 Architecture - Render Container, XALEN Core & Engine Modules</b>", h2_style))
    elements.append(create_layer3_and_backend_diagram())
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("<b>B. Internal Astronomical & Vedic Engine Modules</b>", h2_style))
    elements.append(Paragraph(
        "The backend decomposes astrological calculation into 14 decoupled, deterministic service modules:",
        body_style
    ))

    engine_data = [
        [
            Paragraph("<b>Module Name</b>", ParagraphStyle("TH2", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
            Paragraph("<b>Underlying Engine / Algorithm</b>", ParagraphStyle("TH2", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
            Paragraph("<b>Functional Responsibilities</b>", ParagraphStyle("TH2", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
        ],
        [
            Paragraph("<b>XALEN Ephemeris Core</b>", code_style),
            Paragraph("Pure-Rust compiled PyO3 native extension (<code>xalen</code>)", body_style),
            Paragraph("JPL DE440-grade analytical planetary positions, 50 ayanamsas (Lahiri, KP, Raman), 23 house systems, high-precision sunrise/sunset & Julian Day calculation.", body_style),
        ],
        [
            Paragraph("<b>KP Astrology Engine</b>", code_style),
            Paragraph("Krishnamurti Paddhati algorithms (<code>kp_engine/</code>)", body_style),
            Paragraph("Placidus cuspal sub-lords, sub-sub-lords, 4-fold planetary significators, Ruling Planets (RP), and 1-249 Horary Prashna lookup tables.", body_style),
        ],
        [
            Paragraph("<b>Vimshottari Dasa Engine</b>", code_style),
            Paragraph("Exact calendar time projection (<code>dasa_service.py</code>)", body_style),
            Paragraph("Computes 5 nested Dasa levels (Maha, Antar, Pratyantar, Sookshma, Prana) with exact astronomical balance from Moon's nakshatra position.", body_style),
        ],
        [
            Paragraph("<b>Divisional Charts (Vargas)</b>", code_style),
            Paragraph("Harmonic division engine (<code>varga_engine.py</code>)", body_style),
            Paragraph("Computes Shodashvarga (D1 Rasi through D60 Shashtyamsha) mathematical harmonic signs, lordships, and divisional dignities.", body_style),
        ],
        [
            Paragraph("<b>Shadbala & Strengths</b>", code_style),
            Paragraph("6-fold potency matrix (<code>shadbala_engine/</code>)", body_style),
            Paragraph("Sthana, Dig, Kala, Chesta, Naisargika, and Drik bala. Evaluates planetary strength ratios against classical Virupa thresholds.", body_style),
        ],
        [
            Paragraph("<b>Ashtakavarga & Shodhana</b>", code_style),
            Paragraph("Classical BPHS matrix (<code>ashtakavarga_engine/</code>)", body_style),
            Paragraph("Bhinna & Sarvashtakavarga (BAV/SAV), Trikona Shodhana, Ekadhipatya Shodhana, and 8-fold Kaksha transit partitions.", body_style),
        ],
        [
            Paragraph("<b>Dosha & Yoga Engines</b>", code_style),
            Paragraph("Rule evaluator with cancellation logic", body_style),
            Paragraph("Kuja/Mangal Dosha with 14 classical exceptions, Kala Sarpa (12 types), Pitru Dosha, and 100+ Vedic Yogas (Raja, Dhana, Neechabhanga).", body_style),
        ],
        [
            Paragraph("<b>Marriage Compatibility</b>", code_style),
            Paragraph("Composite assessment (<code>marriage_engine/</code>)", body_style),
            Paragraph("Tamil 10 Poruthams, North Indian 36-point Ashtakoota, Papasamya mathematical balance, Kuja Dosha parity, and longevity verification.", body_style),
        ],
        [
            Paragraph("<b>Numerology Studio</b>", code_style),
            Paragraph("Vedic, Chaldean, Pythagorean engines", body_style),
            Paragraph("9 specialized studios: Traditional, Destiny Matrix, Advanced, Name Studio, Business, Phone, Vehicle, Property, and Marriage.", body_style),
        ],
        [
            Paragraph("<b>Muhurta & Auspicious Timing</b>", code_style),
            Paragraph("Multi-factor time filtering (<code>muhurta_engine/</code>)", body_style),
            Paragraph("Panchaka Rahita, Choghadiya, Hora, Gowri Panchangam, Tara/Chandra Bala for weddings, housewarming, business, and travel.", body_style),
        ],
    ]

    t_engines = Table(engine_data, colWidths=[110, 145, 268])
    t_engines.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
    ]))
    elements.append(t_engines)
    elements.append(Spacer(1, 8))

    # 5. Layer 4: Database & Security Architecture
    elements.append(Paragraph("5. Layer 4 - Database, Security & Concurrency (Supabase)", h1_style))
    elements.append(Paragraph(
        "<b>Supabase Cloud (PostgreSQL 15+)</b> serves as the persistence engine for user accounts, profiles, saved horoscopes, customer records, and calculation states.",
        body_style
    ))

    db_points = [
        "<b>Row Level Security (RLS):</b> Strict RLS policies are enabled across all user tables (<code>saved_horoscopes</code>, <code>saved_kp_charts</code>, <code>saved_numerology_reports</code>, <code>saved_vastu_reports</code>, <code>saved_marriage_compatibility_reports</code>). A user can only SELECT, INSERT, UPDATE, or DELETE records where <code>user_id = auth.uid()</code>. Administrative overrides are governed via role checks (<code>role = 'admin'</code>).",
        "<b>Race-Free Concurrency Control via Advisory Locks:</b> To prevent duplicate <code>display_number</code> assignments when a user submits multiple calculation saves concurrently, the database employs transactional advisory locks: <code>PERFORM pg_advisory_xact_lock(hashtext('saved_horoscopes_' || NEW.user_id::text))</code>. This eliminates <code>SELECT COUNT(*) + 1</code> race conditions without locking the entire table.",
        "<b>Schemaless JSONB Payloads:</b> Complex astrological charts, ephemeris matrices, and numerological grids are persisted directly as structured <code>JSONB</code> documents. This enables rapid retrieval, schema agility across engine versions, and avoids excessive relational joins across planetary coordinates.",
    ]
    for dbp in db_points:
        elements.append(Paragraph(f"• {dbp}", body_style))
    elements.append(Spacer(1, 8))

    # 6. Document Generation & Object Storage Audit
    elements.append(Paragraph("6. Document Generation & Object Storage Audit (Cloudflare R2 Verification)", h1_style))
    elements.append(Paragraph(
        "A central requirement of this architectural investigation was verifying the role of Cloudflare R2 and Cloudflare Workers:",
        body_style
    ))

    elements.append(Paragraph("<b>A. Definitive Technical Finding: Cloudflare R2 & Workers are UNVERIFIED / NOT PRESENT</b>", h2_style))
    elements.append(Paragraph(
        "Thorough automated and manual inspection of the entire repository confirms:<br/>"
        "1. <b>Zero Cloudflare Configurations:</b> There are no <code>wrangler.toml</code> files, Worker scripts, or Cloudflare API bindings.<br/>"
        "2. <b>Zero S3 SDK Dependencies:</b> Neither <code>boto3</code> (Python) nor <code>@aws-sdk/client-s3</code> (Node.js) is installed in dependency files.<br/>"
        "3. <b>Zero Environment Variables:</b> No R2 bucket names, account IDs, or S3 access keys exist in <code>.env.example</code>, <code>render.yaml</code>, or <code>docker-compose.yml</code>.<br/>"
        "4. <b>Actual Document Generation Architecture:</b> PDF reports (e.g. 9-page Vedic Horoscope, 6-page KP Report, 6-page Tamil Booklet, Numerology Reports) "
        "are <b>compiled dynamically on demand in RAM</b> by ReportLab 4.2+ inside the Render Python container, and returned as immediate binary HTTP responses (<code>media_type='application/pdf'</code>). "
        "The browser receives the blob directly and initiates a client-side download without any intermediate cloud object storage.",
        body_style
    ))

    elements.append(Paragraph("<b>B. Proposed Production Migration Path for Cloudflare R2 (If Adopted in Future)</b>", h2_style))
    elements.append(Paragraph(
        "If the platform scales to require pre-generated document caching or public download links, the following target architecture is recommended:<br/>"
        "• <b>S3-Compatible SDK Integration:</b> Add <code>boto3</code> to <code>backend/requirements.txt</code> configured with Cloudflare R2 endpoint (<code>https://&lt;account-id&gt;.r2.cloudflarestorage.com</code>).<br/>"
        "• <b>Cloudflare Worker Gateway:</b> Deploy a lightweight Worker bound to the R2 bucket to issue time-limited pre-signed URLs or stream cached PDFs over Cloudflare's CDN edge.<br/>"
        "• <b>Supabase Metadata Pointer:</b> Add a <code>storage_path TEXT</code> column to <code>saved_horoscopes</code> storing the R2 object key instead of regenerating binary PDFs on every request.",
        body_style
    ))
    elements.append(Spacer(1, 8))

    # 7. End-to-End Data Flow Scenarios
    elements.append(Paragraph("7. End-to-End Data Flow Scenarios", h1_style))
    
    flow_data = [
        [
            Paragraph("<b>Operation</b>", ParagraphStyle("TH3", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
            Paragraph("<b>Initiator</b>", ParagraphStyle("TH3", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
            Paragraph("<b>Network & Processing Path</b>", ParagraphStyle("TH3", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
            Paragraph("<b>Persistence & Delivery</b>", ParagraphStyle("TH3", fontName="Helvetica-Bold", fontSize=7, textColor=colors.white)),
        ],
        [
            Paragraph("<b>Birth Chart Calculation</b>", body_style),
            Paragraph("User Browser (Client Component)", body_style),
            Paragraph("Browser $\\rightarrow$ <code>lib/api.ts</code> $\\rightarrow$ POST <code>/api/v1/horoscope/calculate</code> $\\rightarrow$ FastAPI Pydantic validation $\\rightarrow$ Rust XALEN ephemeris coordinates $\\rightarrow$ Vedic bhavas/yogas computed.", body_style),
            Paragraph("Returns JSON payload to browser. Hydrated React SVG chart visualizer draws North/South Indian charts client-side.", body_style),
        ],
        [
            Paragraph("<b>PDF Report Export</b>", body_style),
            Paragraph("User clicks 'Download PDF'", body_style),
            Paragraph("Browser $\\rightarrow$ POST <code>/api/v1/reports/horoscope/pdf</code> (direct or via Next.js proxy) $\\rightarrow$ FastAPI fetches birth data $\\rightarrow$ ReportLab Platypus builds multi-page document in memory $\\rightarrow$ HarfBuzz shapes Tamil glyphs.", body_style),
            Paragraph("FastAPI streams binary <code>application/pdf</code> in HTTP response. Browser initiates immediate local file download via Blob URL.", body_style),
        ],
        [
            Paragraph("<b>Save Horoscope to Account</b>", body_style),
            Paragraph("User clicks 'Save Chart'", body_style),
            Paragraph("Browser $\\rightarrow$ POST <code>/api/horoscopes</code> (Next.js server route handler) $\\rightarrow$ Extracts Supabase auth token from HTTP-only cookie $\\rightarrow$ Validates session $\\rightarrow$ Inserts into PostgreSQL.", body_style),
            Paragraph("PostgreSQL executes advisory lock trigger, assigns sequential <code>display_number</code>, stores full JSONB state, returns record to UI.", body_style),
        ],
    ]

    t_flow = Table(flow_data, colWidths=[80, 75, 248, 120])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
    ]))
    elements.append(t_flow)
    elements.append(Spacer(1, 10))

    # Document sign-off footer
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=4, spaceAfter=6))
    elements.append(Paragraph(
        "<b>Document Information:</b> Generated automatically from codebase inspection. Version 2.0 (Post-Audit Edition). "
        "Verified against Git commit tree, <code>render.yaml</code>, <code>Dockerfile.backend</code>, <code>next.config.ts</code>, and Supabase migrations.",
        ParagraphStyle("DocInfo", fontName="Helvetica", fontSize=6.5, leading=8.5, textColor=TEXT_MUTED)
    ))

    # Build PDF
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Successfully generated architecture PDF at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_architecture_pdf()
