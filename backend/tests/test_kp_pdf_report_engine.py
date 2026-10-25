"""Comprehensive test suite for the dedicated 6-page bilingual KP Astrology PDF Generator.

Validates:
1. Exact 6-page budget and non-spillable layout structure for both Natal and Horary KP charts.
2. South Indian vector chart drawer for KP Nirayana Rasi and KP Placidus Bhava Chalit.
3. Complete bilingual English and Tamil Unicode rendering and Indic reordering.
4. Comprehensive integration with KP 249 sub-divisions, Placidus cusps, CSL promise, 4-tier ABCD significators,
   Ruling Planets, 5-level Vimshottari dasa, and KP life event matrix.
5. API endpoints:
   - POST /api/v1/reports/kp/pdf (ad-hoc natal & horary)
   - GET /api/v1/reports/kp/pdf/{chart_id} (saved chart with security & auth)
   - POST /api/v1/horoscope/kp/pdf (convenience endpoint)
   - GET /api/v1/horoscope/kp/charts/{chart_id}/pdf (convenience endpoint)
"""

from io import BytesIO
from datetime import date, time
import pytest
import pypdf
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.schemas.kp import HoraryKpRequest
from app.schemas.pdf_report import KpPdfReportRequest
from app.services.pdf_report_engine import (
    build_kp_report_data,
    generate_kp_pdf_bytes,
    create_kp_rasi_chart,
    create_kp_bhava_chart,
)
from app.services.kp_engine.kp_chart_repository import save_kp_chart

client = TestClient(app)

SAMPLE_NATAL_BIRTH = BirthInput(
    birth_date=date(1990, 5, 15),
    birth_time=time(14, 30),
    timezone="Asia/Kolkata",
    latitude=13.0827,
    longitude=80.2707,
)

SAMPLE_HORARY_REQ = HoraryKpRequest(
    horary_number=142,
    question_text="Will I secure the job promotion?",
    question_date=date(2026, 10, 20),
    question_time=time(10, 15),
    timezone="Asia/Kolkata",
    latitude=13.0827,
    longitude=80.2707,
    location_name="Chennai, India",
    ayanamsa=1,
    house_system=2,
)


def test_kp_rasi_chart_drawer():
    """Verify vector KP Nirayana Rasi chart drawer produces a valid Drawing."""
    rasi_data = {
        "ascendant_sign": 6,  # Virgo / கன்னி
        "ascendant_degree": 14.5,
        "planets": [
            {"name": "Sun", "sign_index": 2, "degree_in_sign": 0.75, "is_retrograde": False},
            {"name": "Moon", "sign_index": 10, "degree_in_sign": 15.2, "is_retrograde": False},
            {"name": "Jupiter", "sign_index": 4, "degree_in_sign": 8.1, "is_retrograde": True},
        ],
    }

    drawing_en = create_kp_rasi_chart(rasi_data, title_en="KP RASI", title_ta="நிராயண ராசி", size=195.0, language="en")
    assert drawing_en.width == 195.0
    assert drawing_en.height == 195.0
    assert len(drawing_en.contents) > 20

    drawing_ta = create_kp_rasi_chart(rasi_data, title_en="KP RASI", title_ta="நிராயண ராசி", size=195.0, language="ta")
    assert drawing_ta.width == 195.0
    assert drawing_ta.height == 195.0


def test_kp_bhava_chart_drawer():
    """Verify vector KP Placidus Bhava Chalit chart drawer produces a valid Drawing."""
    cusp_data = [
        {"house": 1, "sign_index": 6, "cusp_degree": 164.5},
        {"house": 2, "sign_index": 7, "cusp_degree": 194.2},
        {"house": 3, "sign_index": 8, "cusp_degree": 225.1},
        {"house": 4, "sign_index": 9, "cusp_degree": 256.3},
        {"house": 5, "sign_index": 10, "cusp_degree": 286.9},
        {"house": 6, "sign_index": 11, "cusp_degree": 316.5},
        {"house": 7, "sign_index": 12, "cusp_degree": 344.5},
        {"house": 8, "sign_index": 1, "cusp_degree": 14.2},
        {"house": 9, "sign_index": 2, "cusp_degree": 45.1},
        {"house": 10, "sign_index": 3, "cusp_degree": 76.3},
        {"house": 11, "sign_index": 4, "cusp_degree": 106.9},
        {"house": 12, "sign_index": 5, "cusp_degree": 136.5},
    ]
    planet_data = [
        {"planet": "Sun", "sign_index": 2, "longitude": 30.75},
        {"planet": "Moon", "sign_index": 10, "longitude": 285.2},
        {"planet": "Mars", "sign_index": 1, "longitude": 12.1},
    ]

    drawing_en = create_kp_bhava_chart(cusp_data, planet_data, size=195.0, language="en")
    assert drawing_en.width == 195.0
    assert drawing_en.height == 195.0
    assert len(drawing_en.contents) > 20

    drawing_ta = create_kp_bhava_chart(cusp_data, planet_data, size=195.0, language="ta")
    assert drawing_ta.width == 195.0
    assert drawing_ta.height == 195.0


def test_kp_pdf_natal_exact_six_pages():
    """Verify that ad-hoc natal KP report produces exactly 6 pages with all required sections."""
    data = build_kp_report_data(
        birth_input=SAMPLE_NATAL_BIRTH,
        native_name="Gokul Murugan",
        gender="male",
        language="en",
    )
    assert data.chart_type == "natal"
    assert len(data.planetary_positions) == 9
    assert len(data.cuspal_analysis) == 12
    assert len(data.significators) == 9
    assert len(data.house_significators) == 12
    assert data.ruling_planets is not None
    assert len(data.event_evaluations) >= 8

    pdf_bytes = generate_kp_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 20000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 6, f"Expected exactly 6 pages, got {len(reader.pages)}"

    # Page 1: Particulars, Ephemeris & Panchang
    p1 = reader.pages[0].extract_text()
    assert "GOKUL'S ASTROLOGICAL INSIGHTS" in p1
    assert "Gokul Murugan" in p1
    assert "Ayanamsa" in p1 or "அயனாம்சம்" in p1
    assert "Placidus" in p1 or "பிளாசிடஸ்" in p1

    # Page 2: KP Charts & 9 Grahas Table
    p2 = reader.pages[1].extract_text()
    assert "Planetary Coordinates" in p2 or "கிரகங்கள்" in p2
    assert "Sun" in p2
    assert "Moon" in p2

    # Page 3: 12 Placidus House Cusps & CSL Promise Arbiter
    p3 = reader.pages[2].extract_text()
    assert "12 Placidus House Cusps" in p3
    assert "Cusp 1" in p3 or "House 1" in p3
    assert "Promise" in p3 or "உறுதி" in p3

    # Page 4: 4-Tier ABCD House Significators & Planet-wise Significators
    p4 = reader.pages[3].extract_text()
    assert "4-Tier ABCD" in p4 or "Level A" in p4
    assert "Significators" in p4

    # Page 5: Ruling Planets & Vimshottari Dasa
    p5 = reader.pages[4].extract_text()
    assert "Ruling Planets" in p5 or "ஆளும் கிரகங்கள்" in p5
    assert "Vimshottari Dasa" in p5 or "தசா" in p5

    # Page 6: Event Matrix & Certification
    p6 = reader.pages[5].extract_text()
    assert "KP Event Signification Matrix" in p6 or "முக்கிய வாழ்க்கை நிகழ்வுகள்" in p6
    assert "Certification" in p6 or "சான்றொப்பம்" in p6
    assert "SHA-256" in p6


def test_kp_pdf_horary_exact_six_pages():
    """Verify that ad-hoc horary KP report (#142) produces exactly 6 pages with horary seed card."""
    data = build_kp_report_data(
        horary_input=SAMPLE_HORARY_REQ,
        native_name="Anand Querent",
        language="en",
    )
    assert data.chart_type == "horary"
    assert data.horary_number == 142
    assert data.horary_division is not None
    assert data.question_text == "Will I secure the job promotion?"

    pdf_bytes = generate_kp_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 6, f"Expected exactly 6 pages, got {len(reader.pages)}"

    p1 = reader.pages[0].extract_text()
    assert "#142" in p1
    assert "Will I secure the job promotion?" in p1
    assert "Horary Seed Arc" in p1 or "Seed" in p1


def test_kp_pdf_tamil_unicode_rendering():
    """Verify that Tamil language generation renders full Unicode Tamil strings without errors."""
    data = build_kp_report_data(
        birth_input=SAMPLE_NATAL_BIRTH,
        native_name="கோகுல் முருகன்",
        gender="male",
        language="ta",
    )
    assert data.language == "ta"

    pdf_bytes = generate_kp_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 20000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 6

    # Extract text from page 1 and page 2
    full_text = "".join(page.extract_text() for page in reader.pages)
    assert "கிருஷ்ணமூர்த்தி" in full_text or "ஜோதிட" in full_text or "ராசி" in full_text


def test_api_generate_kp_pdf_natal_adhoc():
    """Test API endpoint POST /api/v1/reports/kp/pdf for ad-hoc natal request."""
    payload = {
        "chart_type": "natal",
        "birth_input": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "native_name": "Gokul Test",
        "gender": "male",
        "language": "en",
    }
    response = client.post("/api/v1/reports/kp/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=\"KP_Natal_Report_" in response.headers["Content-Disposition"]
    assert response.content.startswith(b"%PDF-")

    reader = pypdf.PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 6


def test_api_generate_kp_pdf_horary_adhoc():
    """Test API endpoint POST /api/v1/reports/kp/pdf for ad-hoc horary query."""
    payload = {
        "chart_type": "horary",
        "horary_input": {
            "horary_number": 1,
            "question_text": "Will the venture succeed?",
            "question_date": "2026-10-24",
            "question_time": "12:00:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "location_name": "Chennai",
            "ayanamsa": 1,
            "house_system": 2,
        },
        "native_name": "Querent Tester",
        "language": "ta",
    }
    response = client.post("/api/v1/reports/kp/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=\"KP_Horary_Report_" in response.headers["Content-Disposition"]

    reader = pypdf.PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 6


def test_api_generate_kp_pdf_missing_parameters_422():
    """Test API endpoint POST /api/v1/reports/kp/pdf with missing inputs returns 422."""
    payload = {
        "chart_type": "natal",
        # Neither birth_input nor saved_chart_id
    }
    response = client.post("/api/v1/reports/kp/pdf", json=payload)
    assert response.status_code == 422


def test_api_saved_kp_chart_pdf_security_and_download():
    """Test security: downloading saved KP chart without auth fails, with saved chart succeeds."""
    from unittest.mock import patch
    from app.routers.pdf_reports import get_optional_current_user

    fake_uuid = "00000000-0000-0000-0000-000000000001"

    # 1. Unauthenticated request without token should fail with 401
    res_unauth = client.get(f"/api/v1/reports/kp/pdf/{fake_uuid}")
    assert res_unauth.status_code == 401

    # 2. Invalid UUID format -> 400 Bad Request
    user_a = {"id": "11111111-1111-1111-1111-111111111111", "email": "usera@example.com", "role": "user"}
    app.dependency_overrides[get_optional_current_user] = lambda: user_a
    try:
        res_inv = client.get("/api/v1/reports/kp/pdf/not-a-valid-uuid")
        assert res_inv.status_code == 400

        # 3. Requesting non-existent UUID with mock auth returns 404
        with patch("app.routers.pdf_reports.get_kp_chart", return_value=None):
            non_existent_uuid = "00000000-0000-0000-0000-999999999999"
            res_404 = client.get(f"/api/v1/reports/kp/pdf/{non_existent_uuid}")
            assert res_404.status_code == 404

        # 4. Fetch the real saved chart by ID -> 200 OK
        chart_id = "33333333-3333-3333-3333-333333333333"
        calc_data = build_kp_report_data(
            birth_input=SAMPLE_NATAL_BIRTH,
            native_name="Saved Client",
            gender="male",
        )
        mock_record = {
            "id": chart_id,
            "user_id": user_a["id"],
            "chart_type": "natal",
            "title": "Saved Client KP Chart",
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "location_name": "Chennai",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
            "ayanamsa_id": 1,
            "house_system_id": 2,
            "calculation_result": {
                "metadata": {
                    "engine": "Swiss Ephemeris & XALEN",
                    "ayanamsa_name": calc_data.ayanamsa_name,
                    "ayanamsa_deg": calc_data.ayanamsa_deg,
                    "house_system_name": calc_data.house_system_name,
                    "julian_day_ut1": calc_data.julian_day_ut1,
                },
                "planetary_positions": calc_data.planetary_positions,
                "cuspal_analysis": calc_data.cuspal_analysis,
                "significators": calc_data.significators,
                "house_significators": calc_data.house_significators,
                "ruling_planets": calc_data.ruling_planets,
                "dasa_hierarchy": calc_data.dasa_hierarchy,
            },
        }
        with patch("app.routers.pdf_reports.get_kp_chart", return_value=mock_record):
            res_ok = client.get(f"/api/v1/reports/kp/pdf/{chart_id}")
            assert res_ok.status_code == 200
            assert res_ok.headers["Content-Type"] == "application/pdf"
            assert res_ok.content.startswith(b"%PDF-")

            reader = pypdf.PdfReader(BytesIO(res_ok.content))
            assert len(reader.pages) == 6
    finally:
        app.dependency_overrides.clear()


def test_api_kp_convenience_endpoints():
    """Verify convenience routes POST /api/v1/horoscope/kp/pdf and GET /api/v1/horoscope/kp/charts/{id}/pdf."""
    from unittest.mock import patch
    from app.services.auth_service import get_current_user

    # 1. POST /api/v1/horoscope/kp/pdf
    payload = {
        "chart_type": "natal",
        "birth_input": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "native_name": "Gokul Direct",
    }
    # Unauthenticated works for ad-hoc
    res = client.post("/api/v1/horoscope/kp/pdf", json=payload)
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF-")

    # 2. GET /api/v1/horoscope/kp/charts/{chart_id}/pdf
    from app.routers.pdf_reports import get_optional_current_user
    user = {"id": "11111111-1111-1111-1111-111111111111", "email": "test@example.com"}
    app.dependency_overrides[get_optional_current_user] = lambda: user
    try:
        mock_rec = {
            "id": "33333333-3333-3333-3333-333333333333",
            "user_id": user["id"],
            "chart_type": "natal",
            "title": "Direct KP Chart",
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
            "calculation_result": {},
        }
        with patch("app.routers.pdf_reports.get_kp_chart", return_value=mock_rec):
            res_get = client.get("/api/v1/horoscope/kp/charts/33333333-3333-3333-3333-333333333333/pdf")
            assert res_get.status_code == 200
            assert res_get.content.startswith(b"%PDF-")
    finally:
        app.dependency_overrides.clear()

