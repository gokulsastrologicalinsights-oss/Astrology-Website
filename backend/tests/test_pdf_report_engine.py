"""Comprehensive test suite for the 9-page bilingual PDF Horoscope Report Engine.

Validates:
1. Exact 9-page budget and layout structure.
2. Complete bilingual English and Tamil Unicode rendering.
3. South Indian vector chart drawing (D1, D9, D10).
4. Full integration with XALEN, Shodashvarga, Shadbala, Ashtakavarga, Yogas, Doshas, and Dasa.
5. API endpoints (POST /api/v1/reports/horoscope/pdf and GET /api/v1/reports/horoscope/pdf/{id}).
6. Security and ownership enforcement on saved horoscope reports.
"""

from io import BytesIO
from datetime import date, time
import pytest
import pypdf
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.schemas.pdf_report import HoroscopePdfReportRequest
from app.services.pdf_report_engine import (
    build_report_data,
    generate_horoscope_pdf_bytes,
    create_south_indian_chart,
)

client = TestClient(app)

SAMPLE_BIRTH = BirthInput(
    birth_date=date(1990, 5, 15),
    birth_time=time(14, 30),
    timezone="Asia/Kolkata",
    latitude=13.0827,
    longitude=80.2707,
)


def test_south_indian_chart_drawer():
    """Verify vector South Indian chart drawer produces a valid Drawing with correct dimensions."""
    chart_data = {
        "ascendant_sign": 6,  # Virgo / கன்னி
        "ascendant_degree": 14.5,
        "planets": [
            {"name": "Sun", "sign_index": 2, "degree_in_sign": 0.75, "is_retrograde": False},
            {"name": "Moon", "sign_index": 10, "degree_in_sign": 15.2, "is_retrograde": False},
            {"name": "Jupiter", "sign_index": 4, "degree_in_sign": 8.1, "is_retrograde": True},
        ],
    }

    drawing_en = create_south_indian_chart(chart_data, title_en="D1 RASI", title_ta="ராசி", size=210.0, language="en")
    assert drawing_en.width == 210.0
    assert drawing_en.height == 210.0
    assert len(drawing_en.contents) > 20

    drawing_ta = create_south_indian_chart(chart_data, title_en="D1 RASI", title_ta="ராசி", size=210.0, language="ta")
    assert drawing_ta.width == 210.0
    assert drawing_ta.height == 210.0


def test_pdf_report_exact_nine_pages():
    """Verify that ad-hoc horoscope generation produces exactly 9 pages with all sections."""
    data = build_report_data(
        birth_input=SAMPLE_BIRTH,
        native_name="Gokul Murugan",
        gender="male",
        language="en",
    )
    assert data.horoscope is not None
    assert data.shodashvarga is not None
    assert data.shadbala is not None
    assert data.doshas is not None
    assert data.dasa is not None

    pdf_bytes = generate_horoscope_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 20000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 9, f"Expected exactly 9 pages, got {len(reader.pages)}"

    # Page 1: Native Particulars & Panchang
    p1 = reader.pages[0].extract_text()
    assert "GOKUL'S ASTROLOGICAL INSIGHTS" in p1
    assert "Gokul Murugan" in p1
    assert "Panchang" in p1 or "திதி" in p1

    # Page 2: Rasi Chart & Planets
    p2 = reader.pages[1].extract_text()
    assert "D1 Rasi Chart" in p2
    assert "Lagna" in p2 or "Sun" in p2

    # Page 3: Navamsa D9
    p3 = reader.pages[2].extract_text()
    assert "D9 Navamsa" in p3
    assert "Vargottama" in p3

    # Page 4: Dasamsa D10 & 16-Varga Matrix
    p4 = reader.pages[3].extract_text()
    assert "D10 Dasamsa" in p4 or "Shodashvarga" in p4

    # Page 5: Shadbala
    p5 = reader.pages[4].extract_text()
    assert "Shadbala Engine" in p5
    assert "Sthana" in p5

    # Page 6: Ashtakavarga
    p6 = reader.pages[5].extract_text()
    assert "Ashtakavarga" in p6
    assert "337" in p6

    # Page 7: Yogas & Cancellations
    p7 = reader.pages[6].extract_text()
    assert "Yogas" in p7 or "யோகம்" in p7

    # Page 8: Unified Doshas
    p8 = reader.pages[7].extract_text()
    assert "Dosha" in p8 or "Kuja" in p8 or "Manglik" in p8

    # Page 9: Dasa, Remedies & Report Verification
    p9 = reader.pages[8].extract_text()
    assert "Dasa" in p9 or "Remedies" in p9
    assert "Report Verification" in p9
    assert "Official Certification" not in p9


def test_pdf_report_tamil_language():
    """Verify Tamil language report renders cleanly with Tamil Unicode strings."""
    data = build_report_data(
        birth_input=SAMPLE_BIRTH,
        native_name="சுவாமிநாதன்",
        language="ta",
    )
    pdf_bytes = generate_horoscope_pdf_bytes(data)
    assert len(pdf_bytes) > 20000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 9

    p1_bytes = reader.pages[0].extract_text().encode("utf-8")
    # Verify presence of native name and Tamil headers
    assert "சுவாமிநாதன்".encode("utf-8") in p1_bytes
    assert "ஜாதகர்".encode("utf-8") in p1_bytes


def test_api_generate_pdf_ad_hoc_success():
    """Verify POST /api/v1/reports/horoscope/pdf returns a valid 200 PDF attachment."""
    payload = {
        "birth_input": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "native_name": "API Test Native",
        "gender": "male",
        "language": "en",
    }
    response = client.post("/api/v1/reports/horoscope/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert len(response.content) > 20000

    reader = pypdf.PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 9


def test_api_generate_pdf_missing_parameters_422():
    """Verify POST /api/v1/reports/horoscope/pdf rejects requests missing both birth_input and saved_horoscope_id."""
    payload = {
        "native_name": "Incomplete Native",
    }
    response = client.post("/api/v1/reports/horoscope/pdf", json=payload)
    assert response.status_code == 422


def test_api_generate_pdf_saved_horoscope_unauthenticated_401():
    """Verify requesting a saved horoscope without an authorization token returns 401."""
    payload = {
        "saved_horoscope_id": "00000000-0000-0000-0000-000000000001",
    }
    response = client.post("/api/v1/reports/horoscope/pdf", json=payload)
    assert response.status_code == 401
    assert "Authentication token required" in response.json()["detail"]


def test_api_download_pdf_saved_id_unauthenticated_401():
    """Verify GET /api/v1/reports/horoscope/pdf/{id} returns 401 when unauthenticated."""
    response = client.get("/api/v1/reports/horoscope/pdf/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 401


def test_api_download_pdf_invalid_uuid_format_400():
    """Verify invalid UUID returns 400 Bad Request."""
    headers = {"Authorization": "Bearer fake-token-for-test"}
    # Even if mock user passes or fails, bad UUID format is rejected
    response = client.get("/api/v1/reports/horoscope/pdf/not-a-valid-uuid", headers=headers)
    assert response.status_code in (400, 401)


def test_saved_horoscope_pdf_authorization_lifecycle():
    """Prove User A cannot download or generate User B's saved horoscope report, and vice-versa."""
    from unittest.mock import patch
    from app.routers.pdf_reports import get_optional_current_user

    user_a = {"id": "11111111-1111-1111-1111-111111111111", "email": "usera@example.com", "role": "user"}
    user_b = {"id": "22222222-2222-2222-2222-222222222222", "email": "userb@example.com", "role": "user"}

    id_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    id_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    horoscope_a = {
        "id": id_a,
        "user_id": user_a["id"],
        "name": "User A Natal Chart",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "gender": "male",
        "ayanamsa_id": 0,
        "house_system_id": 0,
    }

    horoscope_b = {
        "id": id_b,
        "user_id": user_b["id"],
        "name": "User B Natal Chart",
        "birth_date": "1992-08-20",
        "birth_time": "09:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "gender": "female",
        "ayanamsa_id": 0,
        "house_system_id": 0,
    }

    class MockTable:
        def __init__(self, data):
            self._data = data
            self._filtered = list(data)

        def select(self, *a, **k):
            return self

        def eq(self, f, v):
            self._filtered = [r for r in self._filtered if str(r.get(f)) == str(v)]
            return self

        def execute(self):
            class R:
                def __init__(self, d):
                    self.data = d
            return R(self._filtered)

    class MockSupabase:
        def table(self, t):
            if t == "saved_horoscopes":
                return MockTable([horoscope_a, horoscope_b])
            return MockTable([])

    with patch("app.routers.pdf_reports.get_supabase_client", return_value=MockSupabase()):
        # 1. User A downloads own horoscope A -> 200 OK
        app.dependency_overrides[get_optional_current_user] = lambda: user_a
        r_a_own = client.get("/api/v1/reports/horoscope/pdf/" + id_a)
        assert r_a_own.status_code == 200
        assert r_a_own.headers["content-type"] == "application/pdf"
        assert len(r_a_own.content) > 20000

        # 2. User A attempts to download User B's horoscope B -> 404 Not Found / Unauthorized
        r_a_b = client.get("/api/v1/reports/horoscope/pdf/" + id_b)
        assert r_a_b.status_code == 404
        assert "not found or unauthorized" in r_a_b.json()["detail"].lower()

        # 3. User A attempts to generate PDF using User B's saved horoscope ID -> 404
        r_post_a_b = client.post("/api/v1/reports/horoscope/pdf", json={"saved_horoscope_id": id_b})
        assert r_post_a_b.status_code == 404

        # 4. User B downloads own horoscope B -> 200 OK
        app.dependency_overrides[get_optional_current_user] = lambda: user_b
        r_b_own = client.get("/api/v1/reports/horoscope/pdf/" + id_b)
        assert r_b_own.status_code == 200
        assert r_b_own.headers["content-type"] == "application/pdf"

        # 5. User B attempts to download User A's horoscope A -> 404
        r_b_a = client.get("/api/v1/reports/horoscope/pdf/" + id_a)
        assert r_b_a.status_code == 404

        # 6. Unauthenticated request -> 401
        app.dependency_overrides.clear()
        r_unauth = client.get("/api/v1/reports/horoscope/pdf/" + id_a)
        assert r_unauth.status_code == 401

        # 7. Invalid UUID format -> 400 Bad Request
        app.dependency_overrides[get_optional_current_user] = lambda: user_a
        r_inv = client.get("/api/v1/reports/horoscope/pdf/not-a-valid-uuid")
        assert r_inv.status_code == 400

        app.dependency_overrides.clear()


def test_controlled_chart_calculation_consistency():
    """Compare PDF report data directly against domain calculation engines for 1990-05-15 chart."""
    from app.services.ephemeris import calculate_full_horoscope
    from app.services.shadbala_engine import calculate_shadbala
    from app.services.dosha_engine import calculate_unified_doshas
    from app.services.dasa_service import calculate_dasa

    birth = SAMPLE_BIRTH  # 1990-05-15 14:30 IST Chennai

    # 1. Build ReportData
    report_data = build_report_data(birth, "Controlled Chart Native", "en")

    # 2. Independent Engine Executions
    direct_horoscope = calculate_full_horoscope(
        birth_date=birth.birth_date,
        birth_time=birth.birth_time,
        timezone_str=birth.timezone,
        latitude=birth.latitude,
        longitude=birth.longitude,
        include_panchang=True,
        include_outer_planets=True,
        include_nabhasha=True,
        include_ashtakavarga=True,
        include_vedic_yogas=True,
        include_varga=True,
    )
    direct_shadbala = calculate_shadbala(
        planets=direct_horoscope.planets,
        ascendant=direct_horoscope.ascendant,
        houses=direct_horoscope.houses,
        panchang=direct_horoscope.panchang,
        birth_date=birth.birth_date.isoformat(),
        birth_time=birth.birth_time.isoformat(),
        timezone_str=birth.timezone,
        latitude=birth.latitude,
        longitude=birth.longitude,
    )
    direct_doshas = calculate_unified_doshas(
        planets=direct_horoscope.planets,
        ascendant_sign_idx=direct_horoscope.ascendant.sign_index,
        houses=direct_horoscope.houses,
    )
    direct_dasa = calculate_dasa(
        birth=birth,
        depth=2,
        target_date=date.today(),
    )

    # D1 Planetary Coordinates & Signs
    assert len(report_data.horoscope.planets) == len(direct_horoscope.planets)
    for p_rep, p_dir in zip(report_data.horoscope.planets, direct_horoscope.planets):
        assert p_rep.name == p_dir.name
        assert abs(p_rep.longitude - p_dir.longitude) < 1e-4
        assert p_rep.sign_index == p_dir.sign_index
        assert p_rep.nakshatra.name == p_dir.nakshatra.name
        assert p_rep.nakshatra.pada == p_dir.nakshatra.pada

    # Ascendant
    assert abs(report_data.horoscope.ascendant.degree - direct_horoscope.ascendant.degree) < 1e-4
    assert report_data.horoscope.ascendant.sign_index == direct_horoscope.ascendant.sign_index

    # 16 Shodashvarga Charts
    assert len(report_data.shodashvarga.charts) == 16
    for code in ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
        assert code in report_data.shodashvarga.charts

    # Shadbala Virupas & Rankings
    for p_rep in report_data.shadbala.planets:
        p_dir = next(p for p in direct_shadbala.planets if p.planet == p_rep.planet)
        assert abs(p_rep.total_virupas - p_dir.total_virupas) < 1e-3
        assert abs(p_rep.total_rupas - p_dir.total_rupas) < 1e-3
        assert p_rep.rank == p_dir.rank

    # Ashtakavarga SAV 337 Invariant
    assert report_data.horoscope.ashtakavarga.sarvashtakavarga.total_bindus == 337
    assert direct_horoscope.ashtakavarga.sarvashtakavarga.total_bindus == 337
    for s_idx in range(1, 13):
        assert report_data.horoscope.ashtakavarga.sarvashtakavarga.sign_bindus[s_idx] == direct_horoscope.ashtakavarga.sarvashtakavarga.sign_bindus[s_idx]

    # Unified Dosha Engine (Kuja, Kaal Sarp, Sadesati)
    assert report_data.doshas.kuja_dosha.is_present == direct_doshas.kuja_dosha.is_present
    assert report_data.doshas.kuja_dosha.is_cancelled == direct_doshas.kuja_dosha.is_cancelled
    assert report_data.doshas.kuja_dosha.severity == direct_doshas.kuja_dosha.severity
    assert report_data.doshas.kaal_sarp_dosha.is_present == direct_doshas.kaal_sarp_dosha.is_present
    assert report_data.doshas.kaal_sarp_dosha.dosha_type == direct_doshas.kaal_sarp_dosha.dosha_type
    assert report_data.doshas.sadesati.is_active == direct_doshas.sadesati.is_active
    assert report_data.doshas.sadesati.phase == direct_doshas.sadesati.phase

    # Vimshottari Dasa Balance
    assert report_data.dasa.birth_dasa_lord == direct_dasa.birth_dasa_lord
    assert abs(report_data.dasa.birth_balance_years - direct_dasa.birth_balance_years) < 1e-4

    # Generated PDF Binary Validation
    pdf_bytes = generate_horoscope_pdf_bytes(report_data)
    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 9
    p9_text = reader.pages[8].extract_text()
    assert "Report Verification" in p9_text
    assert "Official Certification" not in p9_text

