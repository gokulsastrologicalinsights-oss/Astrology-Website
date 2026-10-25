"""PDF Report Generation Engine for Gokul's Astrological Insights.

Produces:
1. Branded 9-page bilingual (English/Tamil) Vedic horoscope reports.
2. Dedicated 6-page bilingual (English/Tamil) KP (Krishnamurti Paddhati) reports.
Utilizing ReportLab, Noto Sans Tamil fonts, and vector South Indian charts.
"""

from app.services.pdf_report_engine.data_builder import ReportData, build_report_data
from app.services.pdf_report_engine.generator import HoroscopePdfReportGenerator
from app.services.pdf_report_engine.chart_drawer import create_south_indian_chart
from app.services.pdf_report_engine.fonts import register_report_fonts, get_report_styles

from app.services.pdf_report_engine.kp_data_builder import KpReportData, build_kp_report_data
from app.services.pdf_report_engine.kp_generator import KpPdfReportGenerator
from app.services.pdf_report_engine.kp_chart_drawer import create_kp_rasi_chart, create_kp_bhava_chart
from app.services.pdf_report_engine.shodashvarga_generator import generate_shodashvarga_pdf_bytes
from app.services.pdf_report_engine.muhurta_certificate_generator import generate_muhurta_certificate_pdf_bytes
from app.services.pdf_report_engine.pancha_pakshi_pdf_generator import generate_pancha_pakshi_pdf_bytes
from app.services.pdf_report_engine.gemstone_rudraksha_playbook_generator import generate_gemstone_rudraksha_playbook_pdf_bytes


def generate_horoscope_pdf_bytes(report_data: ReportData) -> bytes:
    """Convenience entrypoint: generates and returns raw PDF bytes for Vedic Horoscope Report."""
    generator = HoroscopePdfReportGenerator(report_data)
    return generator.generate()


def generate_kp_pdf_bytes(report_data: KpReportData) -> bytes:
    """Convenience entrypoint: generates and returns raw PDF bytes for KP Astrology Report."""
    generator = KpPdfReportGenerator(report_data)
    return generator.generate()


__all__ = [
    # Vedic Report Engine
    "ReportData",
    "build_report_data",
    "HoroscopePdfReportGenerator",
    "generate_horoscope_pdf_bytes",
    "create_south_indian_chart",
    # KP Report Engine
    "KpReportData",
    "build_kp_report_data",
    "KpPdfReportGenerator",
    "generate_kp_pdf_bytes",
    "create_kp_rasi_chart",
    "create_kp_bhava_chart",
    # Specialized Printable PDF Engines
    "generate_shodashvarga_pdf_bytes",
    "generate_muhurta_certificate_pdf_bytes",
    "generate_pancha_pakshi_pdf_bytes",
    "generate_gemstone_rudraksha_playbook_pdf_bytes",
    # Fonts & Styles
    "register_report_fonts",
    "get_report_styles",
]
