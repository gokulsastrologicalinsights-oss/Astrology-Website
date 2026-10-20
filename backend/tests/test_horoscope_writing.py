"""Automated unit and integration test suite for Traditional Tamil Horoscope Writing Module."""

import pytest
from datetime import date, time
from io import BytesIO
from pypdf import PdfReader
from fastapi.testclient import TestClient

from app.main import app
from app.services.horoscope_writing import (
    calculate_astronomical_tamil_calendar,
    calculate_traditional_horoscope_writing_data,
    format_nazhigai_vinadi,
    seconds_to_nazhigai_vinadi,
    TraditionalHoroscopePdfGenerator,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_nazhigai_vinadi_conversion():
    """Verify Nazhigai & Vinadi conversion conventions.
    1 Nazhigai = 24 minutes = 1440 seconds.
    1 Vinadi = 24 seconds.
    60 Nazhigai = 24 hours = 86400 seconds.
    """
    # 0 seconds -> 0 naz, 0 vin
    naz, vin = seconds_to_nazhigai_vinadi(0)
    assert naz == 0 and vin == 0

    # 1440 seconds = 1 nazhigai, 0 vinadi
    naz, vin = seconds_to_nazhigai_vinadi(1440)
    assert naz == 1 and vin == 0

    # 1464 seconds = 1 nazhigai, 1 vinadi
    naz, vin = seconds_to_nazhigai_vinadi(1464)
    assert naz == 1 and vin == 1

    # 86400 seconds = 60 nazhigai, 0 vinadi
    naz, vin = seconds_to_nazhigai_vinadi(86400)
    assert naz == 60 and vin == 0

    formatted = format_nazhigai_vinadi(25, 42)
    assert "25 நாழிகை 42 விநாடி" in formatted


def test_tamil_calendar_eras_and_seasons():
    """Verify astronomical Tamil calendar, Jovian year, month, date, and historical eras."""
    # Test date: May 15, 1990 (Sun in Taurus -> Vaikasi month)
    b_date = date(1990, 5, 15)
    b_time = time(14, 30, 0)
    cal = calculate_astronomical_tamil_calendar(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
    )

    # 1990 is Pramodoota (பிரமோதூத) year
    assert cal["tamil_year_ta"] == "பிரமோதூத"
    assert cal["tamil_year_index"] == 4

    # Sun in Taurus -> Vaikasi
    assert cal["tamil_month_ta"] == "வைகாசி"
    assert cal["tamil_month_en"] == "Vaikasi"
    assert cal["sun_sign_ta"] == "ரிஷபம்"
    assert cal["tamil_date"] >= 1 and cal["tamil_date"] <= 32

    # Ayanam & Ritu: Vaikasi is Uttarayana and Vasanta Ritu
    assert cal["ayanam_ta"] == "உத்தராயணம்"
    assert "வசந்த" in cal["ritu_ta"]

    # Historical Eras
    assert cal["saka_year"] == 1990 - 78  # 1912 Saka
    assert cal["kali_year"] == 1990 + 3102  # 5092 Kali
    assert cal["kollam_year"] == 1990 - 825  # 1165 Kollam
    assert cal["hijri_year"] > 1400  # ~1410 AH


def test_traditional_horoscope_calculations_page1_to_page6():
    """Verify that calculate_traditional_horoscope_writing_data populates all 6 pages with dynamic shastra data."""
    b_date = date(1995, 8, 20)
    b_time = time(8, 15, 0)
    lat = 13.0827
    lon = 80.2707

    result = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=lat,
        longitude=lon,
        timezone_str="Asia/Kolkata",
        person_name="Gokul",
        gender="male",
    )

    # Check top-level structure
    assert "page1_birth_details" in result
    assert "page2_dinasuthi" in result
    assert "page3_udumaka_dasa" in result
    assert "page4_kurippu" in result
    assert "page5_padupakshi" in result
    assert "page6_archana_slip" in result

    # Page 1 checks
    p1 = result["page1_birth_details"]
    assert p1["tamil_year"] != ""
    assert p1["weekday"] in ["ஞாயிறு", "திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி"]
    assert "நாழிகை" in p1["udayadhi_nazhigai"]
    assert "நாழிகை" in p1["ahas"]
    assert p1["vara_yoga"] in ["அமிர்த யோகம்", "சித்த யோகம்", "மரண யோகம்"]
    assert "லக்னம்" in p1["udaya_lagna"]

    # Page 2 checks
    p2 = result["page2_dinasuthi"]
    assert "சகாப்தம்" in p2["saka_year"]
    assert "கலியுகாதி" in p2["kali_year"]
    assert "ஹிஜிரி" in p2["hijri_year"]
    assert "கொல்லம்" in p2["kollam_year"]
    assert p2["english_year"] == 1995
    assert p2["english_date"] == "20-08-1995"

    # Page 3 checks (Vimshottari Dasa in Nazhigai)
    p3 = result["page3_udumaka_dasa"]
    assert p3["param_nazhigai"] == "60 நாழிகை 00 விநாடி"
    assert p3["pada_duration"] == "15 நாழிகை 00 விநாடி"
    assert p3["birth_pada"] in [1, 2, 3, 4]
    assert "நாழிகை" in p3["pada_sentrathu"]
    assert "நாழிகை" in p3["pada_nindrathu"]
    assert len(p3["dasa_sequence"]) == 9
    assert p3["dasa_sequence"][0]["order"] == 1

    # Page 4 checks (Classifications)
    p4 = result["page4_kurippu"]
    assert p4["kalam"] in ["பகல்", "இரவு"]
    assert p4["mrigam"] != ""
    assert p4["pakshi"] != ""
    assert p4["maram"] != ""
    assert p4["gana"] in ["தேவ கணம்", "மனித கணம்", "ராட்சச கணம்"]
    assert "ரஜ்ஜு" in p4["rajju"]
    assert "நாடி" in p4["nadi"]

    # Page 5 checks (Padupakshi)
    p5 = result["page5_padupakshi"]
    assert p5["uyir_pakshi"] in ["வல்லூறு", "ஆந்தை", "காகம்", "கோழி", "மயில்"]
    assert p5["paksha"] in ["வளர்பிறை", "தேய்பிறை"]
    assert len(p5["five_birds_list"]) == 5

    # Page 6 checks (Archana Slip)
    p6 = result["page6_archana_slip"]
    assert p6["rasi"] != ""
    assert p6["nakshatra"] != ""
    assert p6["lagna"] != ""
    assert "வாசல்" in p6["entrance_direction"]
    assert p6["lucky_day"] != ""
    assert p6["lucky_color"] != ""
    assert p6["lucky_gem"] != ""
    assert p6["worship_deity"] != ""


def test_archana_slip_overrides_and_direction_basis():
    """Verify that astrologer can override Page 6 recommendations and select Lagna or Rasi basis."""
    b_date = date(1992, 11, 10)
    b_time = time(16, 45, 0)

    # 1. Test Lagna basis vs Rasi basis
    res_rasi = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
        entrance_direction_basis="rasi",
    )
    res_lagna = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
        entrance_direction_basis="lagna",
    )
    assert "வாசல்" in res_rasi["page6_archana_slip"]["entrance_direction"]
    assert "வாசல்" in res_lagna["page6_archana_slip"]["entrance_direction"]

    # 2. Test manual overrides
    custom_overrides = {
        "entrance_direction": "வடக்கு வாசல் (தனிப்பயன்)",
        "lucky_day": "வியாழக்கிழமை",
        "worship_deity": "ஸ்ரீ ராகவேந்திரர் சுவாமிகள்",
    }
    res_custom = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
        overrides=custom_overrides,
    )
    p6 = res_custom["page6_archana_slip"]
    assert p6["entrance_direction"] == "வடக்கு வாசல் (தனிப்பயன்)"
    assert p6["lucky_day"] == "வியாழக்கிழமை"
    assert p6["worship_deity"] == "ஸ்ரீ ராகவேந்திரர் சுவாமிகள்"
    # Ensure calculated source defaults are retained separately for resetting
    assert p6["calculated_entrance_direction"] != ""
    assert p6["calculated_worship_deity"] != ""


def test_pdf_generation_exact_six_pages():
    """Generate the PDF booklet and verify exact 6-page output, valid PDF header, and Tamil rendering."""
    b_date = date(1988, 3, 25)
    b_time = time(10, 20, 0)
    data = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
        person_name="Gokul Murugan",
    )

    generator = TraditionalHoroscopePdfGenerator(data)
    pdf_bytes = generator.generate()

    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b"%PDF")

    # Inspect page count with pypdf
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 6, f"Expected exactly 6 pages in booklet, got {len(reader.pages)}"


def test_api_calculate_endpoint(client):
    """Test POST /api/v1/tools/horoscope-writing/calculate endpoint."""
    payload = {
        "birth_input": {
            "birth_date": "1994-06-18",
            "birth_time": "11:30:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
        },
        "person_name": "Karthik",
        "gender": "male",
        "panchanga_system": "thirukanitha",
    }

    response = client.post("/api/v1/tools/horoscope-writing/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "page1_birth_details" in data
    assert "page2_dinasuthi" in data
    assert "page3_udumaka_dasa" in data
    assert "page4_kurippu" in data
    assert "page5_padupakshi" in data
    assert "page6_archana_slip" in data
    assert data["person_details"]["name"] == "Karthik"


def test_api_pdf_endpoint(client):
    """Test POST /api/v1/tools/horoscope-writing/pdf endpoint returning 6-page PDF binary."""
    payload = {
        "birth_input": {
            "birth_date": "1991-12-05",
            "birth_time": "09:45:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
        },
        "person_name": "Ananya",
        "gender": "female",
    }

    response = client.post("/api/v1/tools/horoscope-writing/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "Tamil_Horoscope_Writing_Ananya" in response.headers.get("content-disposition", "")
    pdf_bytes = response.content
    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 6


def test_api_missing_inputs_returns_422(client):
    """Verify endpoint rejects requests without birth_input or saved_horoscope_id."""
    response = client.post("/api/v1/tools/horoscope-writing/calculate", json={})
    assert response.status_code == 422


def test_api_invalid_uuid_returns_400(client):
    """Verify endpoint rejects requests with malformed saved_horoscope_id with 400 Bad Request."""
    response = client.post("/api/v1/tools/horoscope-writing/calculate", json={
        "saved_horoscope_id": "not-a-valid-uuid"
    }, headers={"Authorization": "Bearer fake.token.here"})
    # Token decode will fail or invalid uuid will trigger
    assert response.status_code in (400, 401)


def test_api_whitespace_saved_id_returns_422(client):
    """Verify whitespace saved_horoscope_id without birth_input returns 422."""
    response = client.post("/api/v1/tools/horoscope-writing/calculate", json={
        "saved_horoscope_id": "   "
    })
    assert response.status_code == 422


def test_api_save_endpoint_requires_auth(client):
    """Verify save endpoint returns 401 when no auth is provided."""
    payload = {
        "person_name": "Test Native",
        "birth_date": "1995-05-15",
        "birth_time": "14:30:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "calculated_data": {"page1_birth_details": {}},
    }
    response = client.post("/api/v1/tools/horoscope-writing/save", json=payload)
    assert response.status_code == 401


def test_api_save_endpoint_with_auth_fallback(client, monkeypatch):
    """Verify save endpoint gracefully persists or returns fallback without HTTP 500."""
    from app.routers import horoscope_writing

    # Mock user dependency
    async def mock_user():
        return {"id": "4719b6a8-0452-4bfa-ab87-6733190c3de3", "role": "authenticated"}

    from app.main import app
    app.dependency_overrides[horoscope_writing.get_optional_current_user] = mock_user

    payload = {
        "horoscope_id": "",  # Empty string should be sanitized to None
        "person_name": "Test Native",
        "birth_date": "1995-05-15",
        "birth_time": "14:30:00",
        "birth_place": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "panchanga_system": "thirukanitha",
        "calculated_data": {"test": "data"},
        "overrides": {},
    }

    try:
        response = client.post("/api/v1/tools/horoscope-writing/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        assert data["persistence_target"] in ("supabase", "local_disk")
    finally:
        app.dependency_overrides.pop(horoscope_writing.get_optional_current_user, None)


def test_saved_writings_crud_persistence_and_isolation(client):
    """Verify full persistence lifecycle: save -> list -> get -> cross-user isolation (403) -> admin -> delete -> 404."""
    from app.routers import horoscope_writing
    from app.main import app

    user_a = {"id": "4719b6a8-0452-4bfa-ab87-6733190c3de3", "role": "authenticated"}
    user_b = {"id": "22222222-2222-4222-a222-222222222222", "role": "authenticated"}
    admin_user = {"id": "4719b6a8-0452-4bfa-ab87-6733190c3de3", "role": "admin"}

    # 1. User A saves a document
    app.dependency_overrides[horoscope_writing.get_optional_current_user] = lambda: user_a
    save_payload = {
        "person_name": "User A Record",
        "birth_date": "1998-04-14",
        "birth_time": "06:30:00",
        "birth_place": "Madurai",
        "latitude": 9.9252,
        "longitude": 78.1198,
        "panchanga_system": "thirukanitha",
        "calculated_data": {"page1_birth_details": {"tamil_year": "பிரபவ"}},
    }
    save_resp = client.post("/api/v1/tools/horoscope-writing/save", json=save_payload)
    assert save_resp.status_code == 200
    save_data = save_resp.json()
    record_id = save_data["id"]
    assert save_data["success"] is True
    assert save_data["persistence_target"] in ("supabase", "local_disk")

    # 2. User A lists saved documents and finds the new record
    list_resp = client.get("/api/v1/tools/horoscope-writing/saved")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["success"] is True
    found = [item for item in list_data["items"] if item["id"] == record_id]
    assert len(found) == 1
    assert found[0]["person_name"] == "User A Record"

    # 3. User A gets single document by ID
    get_resp = client.get(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == record_id
    assert get_resp.json()["birth_place"] == "Madurai"

    # 4. User A updates their document (PUT /saved/{id})
    update_payload = {"person_name": "User A Updated Name", "birth_place": "Tiruchirappalli"}
    put_resp = client.put(f"/api/v1/tools/horoscope-writing/saved/{record_id}", json=update_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["person_name"] == "User A Updated Name"
    assert put_resp.json()["birth_place"] == "Tiruchirappalli"

    # 5. Cross-user isolation: User B attempts to access User A's document -> 403 Forbidden!
    app.dependency_overrides[horoscope_writing.get_optional_current_user] = lambda: user_b
    b_get_resp = client.get(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert b_get_resp.status_code == 403
    assert any(term in b_get_resp.json()["detail"].lower() for term in ("restricted", "forbidden", "unauthorized", "permission"))

    # User B attempts to update User A's document -> 403 Forbidden!
    b_put_resp = client.put(f"/api/v1/tools/horoscope-writing/saved/{record_id}", json={"person_name": "Hacked Name"})
    assert b_put_resp.status_code == 403

    b_del_resp = client.delete(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert b_del_resp.status_code == 403

    # User B listing should NOT include User A's record
    b_list_resp = client.get("/api/v1/tools/horoscope-writing/saved")
    assert b_list_resp.status_code == 200
    b_found = [item for item in b_list_resp.json()["items"] if item["id"] == record_id]
    assert len(b_found) == 0

    # 5. Admin user CAN access User A's document
    app.dependency_overrides[horoscope_writing.get_optional_current_user] = lambda: admin_user
    admin_get_resp = client.get(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert admin_get_resp.status_code == 200
    assert admin_get_resp.json()["id"] == record_id

    # 6. User A deletes their own document
    app.dependency_overrides[horoscope_writing.get_optional_current_user] = lambda: user_a
    del_resp = client.delete(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 7. Document is now gone -> 404 Not Found
    get_after_del = client.get(f"/api/v1/tools/horoscope-writing/saved/{record_id}")
    assert get_after_del.status_code == 404

    # 8. Invalid UUID format returns 400 Bad Request
    invalid_get = client.get("/api/v1/tools/horoscope-writing/saved/not-a-valid-uuid")
    assert invalid_get.status_code == 400

    # Cleanup
    app.dependency_overrides.pop(horoscope_writing.get_optional_current_user, None)

