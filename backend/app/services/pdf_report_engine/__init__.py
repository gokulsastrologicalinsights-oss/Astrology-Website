"""PDF Report Generation Engine for Gokul's Astrological Insights.

Produces an approximately 9-page bilingual (English/Tamil) branded Vedic horoscope
report utilizing ReportLab, Noto Sans Tamil fonts, and vector South Indian charts.
"""

from app.services.pdf_report_engine.data_builder import ReportData, build_report_data
from app.services.pdf_report_engine.generator import HoroscopePdfReportGenerator
from app.services.pdf_report_engine.chart_drawer import create_south_indian_chart
from app.services.pdf_report_engine.fonts import register_report_fonts, get_report_styles


def generate_horoscope_pdf_bytes(report_data: ReportData) -> bytes:
    """Convenience entrypoint: generates and returns raw PDF bytes for a given ReportData."""
    generator = HoroscopePdfReportGenerator(report_data)
    return generator.generate()


__all__ = [
    "ReportData",
    "build_report_data",
    "HoroscopePdfReportGenerator",
    "generate_horoscope_pdf_bytes",
    "create_south_indian_chart",
    "register_report_fonts",
    "get_report_styles",
]
