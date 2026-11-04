"""Unit tests for the Single-Page Traditional Tamil Horoscope PDF Generator."""

import pytest
from datetime import date, time
from io import BytesIO
from pypdf import PdfReader
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.services.pdf_report_engine import (
    SinglePageHoroscopePdfGenerator,
    generate_single_page_horoscope_pdf_bytes,
)


def test_single_page_pdf_exact_one_page():
    """Verifies that the PDF generator strictly produces exactly 1 page."""
    birth = BirthInput(
        birth_date=date(1999, 1, 3),
        birth_time=time(5, 58, 0),
        timezone="Asia/Kolkata",
        latitude=13.0878,
        longitude=80.2783,
    )

    pdf_bytes = generate_single_page_horoscope_pdf_bytes(
        birth_input=birth,
        native_name="Gokul",
        father_name="Murugan",
        mother_name="Nirmala",
        gender="male",
        birth_place="Chennai, Tamil Nadu",
        native_id="#001",
    )

    assert len(pdf_bytes) > 10000, "PDF output is too small"
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 1, f"Expected exactly 1 page, got {len(reader.pages)}"

    extracted_text = reader.pages[0].extract_text()
    # Check for core sections in extracted text
    assert "Gokul's Astrological Insights" in extracted_text
    assert "Gokul (#001)" in extracted_text
    assert "Murugan" in extracted_text
    assert "Nirmala" in extracted_text
    assert "03-Jan-1999" in extracted_text
    assert "Current Dasa:" in extracted_text
    assert "Current Bukthi:" in extracted_text


def test_single_page_pdf_endpoint():
    """Tests the REST API endpoint POST /api/v1/reports/horoscope/single-page-pdf."""
    client = TestClient(app)
    payload = {
        "birth_input": {
            "birth_date": "1999-01-03",
            "birth_time": "05:58:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0878,
            "longitude": 80.2783,
        },
        "native_name": "Gokul",
        "father_name": "Murugan",
        "mother_name": "Nirmala",
        "gender": "male",
        "birth_place": "Chennai, Tamil Nadu",
        "native_id": "#001",
        "language": "ta",
    }

    response = client.post("/api/v1/reports/horoscope/single-page-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "Single_Page_Horoscope_Gokul.pdf" in response.headers.get("content-disposition", "")

    reader = PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 1
