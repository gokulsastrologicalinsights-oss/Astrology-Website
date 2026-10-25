"""Tests for Specialized Client-Facing Printable PDF Reports.

Tests:
1. Comprehensive Kundli & Shodashvarga Chart Book (D1-D60)
2. Ceremonial Auspicious Muhurta Selection Certificate
3. Agastya Pancha Pakshi 24-Hour Bio-Rhythm Chart
4. Remedial Gemstone & Rudraksha Sanctification Playbook
"""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.common import BirthInput
from app.schemas.pdf_report import (
    ShodashvargaPdfReportRequest,
    MuhurtaCertificatePdfRequest,
    PanchaPakshiPdfReportRequest,
    GemstoneRudrakshaPlaybookPdfRequest,
)
from app.services.pdf_report_engine import (
    generate_shodashvarga_pdf_bytes,
    generate_muhurta_certificate_pdf_bytes,
    generate_pancha_pakshi_pdf_bytes,
    generate_gemstone_rudraksha_playbook_pdf_bytes,
)

client = TestClient(app)


def test_shodashvarga_pdf_bytes_generation():
    birth_in = BirthInput(
        birth_date=date(1995, 10, 25),
        birth_time=time(6, 15),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    req = ShodashvargaPdfReportRequest(
        native_name="Siddharth Raman",
        gender="male",
        language="en",
        ayanamsa=0,
    )
    pdf_bytes = generate_shodashvarga_pdf_bytes(req, birth_in)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 25000  # Multi-page document with 16 vector charts


def test_muhurta_certificate_pdf_bytes_generation():
    req = MuhurtaCertificatePdfRequest(
        occasion="Marriage",
        primary_person_name="Gokul Murugan",
        secondary_person_name="Divya Lakshmi",
        primary_gotra="Kashyapa",
        secondary_gotra="Bharadwaja",
        primary_nakshatra="Rohini",
        secondary_nakshatra="Uttara Phalguni",
        event_date="2026-11-20",
        start_time="06:30",
        end_time="08:00",
        location_name="Chennai, Tamil Nadu",
        latitude=13.0827,
        longitude=80.2707,
        language="ta",
        astrologer_name="Gokul's Astrological Insights",
    )
    pdf_bytes = generate_muhurta_certificate_pdf_bytes(req)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 10000


def test_pancha_pakshi_pdf_bytes_generation():
    req = PanchaPakshiPdfReportRequest(
        nakshatra="Ashwini",
        paksha="shukla",
        target_date="2026-10-26",
        latitude=13.0827,
        longitude=80.2707,
        native_name="Arun Kumar",
        language="ta",
    )
    pdf_bytes = generate_pancha_pakshi_pdf_bytes(req)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 15000


def test_gemstone_rudraksha_playbook_pdf_bytes_generation():
    req = GemstoneRudrakshaPlaybookPdfRequest(
        ascendant_sign="Cancer",
        native_name="Meenakshi Sundaram",
        body_weight_kg=65.0,
        has_kuja_dosha=True,
        has_sade_sati=True,
        language="en",
    )
    pdf_bytes = generate_gemstone_rudraksha_playbook_pdf_bytes(req)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 15000


def test_api_shodashvarga_pdf_endpoint():
    payload = {
        "native_name": "Test Native",
        "gender": "male",
        "language": "en",
        "birth_input": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
    }
    resp = client.post("/api/v1/reports/shodashvarga/pdf", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "Shodashvarga" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF")


def test_api_muhurta_certificate_endpoint():
    payload = {
        "occasion": "Vivaha (Marriage)",
        "primary_person_name": "Raghavan",
        "secondary_person_name": "Ananya",
        "event_date": "2026-12-05",
        "start_time": "07:15",
        "end_time": "08:45",
        "location_name": "Madurai, Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198,
        "language": "ta",
    }
    resp = client.post("/api/v1/reports/muhurta-certificate/pdf", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


def test_api_pancha_pakshi_pdf_endpoint():
    payload = {
        "nakshatra": "Rohini",
        "paksha": "shukla",
        "target_date": "2026-10-27",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "native_name": "Karthik",
        "language": "en",
    }
    resp = client.post("/api/v1/reports/pancha-pakshi/pdf", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


def test_api_gemstone_rudraksha_pdf_endpoint():
    payload = {
        "ascendant_sign": "Leo",
        "native_name": "Vijay",
        "body_weight_kg": 72.0,
        "language": "ta",
    }
    resp = client.post("/api/v1/reports/gemstone-rudraksha/pdf", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
