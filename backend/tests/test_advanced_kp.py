"""Automated test suite for Advanced KP and Horary Prashna calculation & persistence engines."""

import pytest
from datetime import date, time
from app.schemas.kp import KpRequest, HoraryKpRequest
from app.services.kp_service import calculate_kp_chart, calculate_horary_chart
from app.services.kp_engine.horary import (
    kp_divisions,
    find_armc_for_ascendant,
    compute_horary_cusps,
)
from app.services.kp_engine.kp_chart_repository import (
    save_kp_chart,
    list_kp_charts,
    get_kp_chart,
    delete_kp_chart,
)


def test_horary_division_integrity():
    """Ensure exactly 249 divisions tile 0-360 degrees without gaps or overlaps."""
    divs = kp_divisions()
    assert len(divs) == 249, f"Expected 249 divisions, got {len(divs)}"

    # First division is in Aries, Ketu/Ketu/Ketu
    assert divs[0].number == 1
    assert divs[0].sign == "Aries"
    assert divs[0].star_lord == "Ketu"
    assert divs[0].sub_lord == "Ketu"
    assert abs(divs[0].start_deg - 0.0) < 1e-6
    assert abs(divs[0].end_deg - (46.0 / 60.0 + 40.0 / 3600.0)) < 1e-4

    # Last division is in Pisces, Jupiter/Mercury/Saturn
    assert divs[248].number == 249
    assert divs[248].sign == "Pisces"
    assert abs(divs[248].end_deg - 360.0) < 1e-6


def test_calculate_horary_chart_number_1():
    """Test calculation of Horary #1 chart with authentic KP mechanics."""
    req = HoraryKpRequest(
        horary_number=1,
        question_text="Will the business deal succeed?",
        question_date=date(2026, 10, 18),
        question_time=time(10, 30),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_name="Chennai, India",
        ayanamsa=1,  # KP Ayanamsa
    )
    res = calculate_horary_chart(req)

    # 1. Division and Ascendant
    assert res.horary_number == 1
    assert res.horary_division.number == 1
    assert res.horary_division.sub_lord == "Ketu"
    assert abs(res.ascendant_degree - res.horary_division.mid_degree) < 1e-5

    # 2. 12 Placidus Cusps
    assert len(res.cuspal_analysis) == 12
    assert abs(res.cuspal_analysis[0].cusp_degree - res.ascendant_degree) < 1e-5
    for c in res.cuspal_analysis:
        assert c.promise in ("Positive", "Negative", "Mixed")
        assert c.sub_lord in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

    # 3. 9 Planetary positions
    assert len(res.planetary_positions) == 9
    planet_names = {p.planet for p in res.planetary_positions}
    assert planet_names == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

    # 4. Significators
    assert len(res.house_significators) == 12
    for h in res.house_significators:
        assert isinstance(h.level_a, list)
        assert isinstance(h.level_b, list)
        assert isinstance(h.level_c, list)
        assert isinstance(h.level_d, list)

    # 5. Ruling Planets
    assert res.ruling_planets is not None
    assert len(res.ruling_planets.ruling_planets_list) > 0

    # 6. Dasa Hierarchy
    assert res.dasa_hierarchy is not None
    assert len(res.dasa_hierarchy.current_periods) == 5
    assert len(res.dasa_hierarchy.mahadashas) > 0


def test_calculate_horary_chart_number_249():
    """Test calculation of Horary #249 (Pisces boundary)."""
    req = HoraryKpRequest(
        horary_number=249,
        question_text="Overseas travel confirmation",
        question_date=date(2026, 10, 18),
        question_time=time(14, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    res = calculate_horary_chart(req)
    assert res.horary_number == 249
    assert res.horary_division.sign == "Pisces"
    assert res.horary_division.star_lord == "Mercury"
    assert res.horary_division.sub_lord == "Saturn"
    assert abs(res.ascendant_degree - res.horary_division.mid_degree) < 1e-5


def test_saved_kp_charts_repository_crud(monkeypatch):
    """Test concurrency-safe sequential numbering and CRUD in repository."""
    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: None)
    user_id = "test-user-uuid-1234"

    # 1. Save first chart
    data1 = {
        "chart_type": "natal",
        "title": "Natal Client A",
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {"status": "ok"},
    }
    r1 = save_kp_chart(user_id, data1)
    assert r1["display_number"] == 1
    assert r1["chart_type"] == "natal"
    assert r1["title"] == "Natal Client A"

    # 2. Save second chart (sequential display_number = 2)
    data2 = {
        "chart_type": "horary",
        "title": "Horary Query B",
        "horary_number": 42,
        "question_text": "Will I buy the house?",
        "question_date": "2026-10-18",
        "question_time": "11:15:00",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {"status": "ok"},
    }
    r2 = save_kp_chart(user_id, data2)
    assert r2["display_number"] == 2
    assert r2["chart_type"] == "horary"

    # 3. List records
    charts = list_kp_charts(user_id)
    assert len(charts) >= 2
    # Verify ordered descending by display_number
    assert charts[0]["display_number"] > charts[1]["display_number"]

    # 4. Fetch single record
    fetched = get_kp_chart(user_id, r1["id"])
    assert fetched is not None
    assert fetched["id"] == r1["id"]

    # 5. Delete record and verify sequential numbers of remaining records are preserved
    del_ok = delete_kp_chart(user_id, r1["id"])
    assert del_ok is True
    remaining = list_kp_charts(user_id)
    assert not any(c["id"] == r1["id"] for c in remaining)
    assert any(c["id"] == r2["id"] and c["display_number"] == 2 for c in remaining)


def test_saved_kp_charts_customer_fields_preservation(monkeypatch):
    """Verify that all five customer integration fields are preserved during save and fetch."""
    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: None)
    user_id = "test-user-customer-fields"
    data = {
        "chart_type": "natal",
        "title": "Customer CRM Chart",
        "birth_date": "1990-05-15",
        "birth_time": "09:30:00",
        "location_name": "Coimbatore, India",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "timezone": "Asia/Kolkata",
        "calculation_result": {"status": "ok"},
        "customer_id": "c1234567-89ab-cdef-0123-456789abcdef",
        "customer_phone": "9876543210",
        "country_code": "+91",
        "normalized_phone": "+919876543210",
        "whatsapp_number": "+919876543210",
    }
    saved = save_kp_chart(user_id, data)
    assert saved["customer_id"] == "c1234567-89ab-cdef-0123-456789abcdef"
    assert saved["customer_phone"] == "9876543210"
    assert saved["country_code"] == "+91"
    assert saved["normalized_phone"] == "+919876543210"
    assert saved["whatsapp_number"] == "+919876543210"

    fetched = get_kp_chart(user_id, saved["id"])
    assert fetched is not None
    assert fetched["customer_id"] == "c1234567-89ab-cdef-0123-456789abcdef"
    assert fetched["customer_phone"] == "9876543210"
    assert fetched["country_code"] == "+91"
    assert fetched["normalized_phone"] == "+919876543210"
    assert fetched["whatsapp_number"] == "+919876543210"


def test_saved_kp_charts_ownership_isolation(monkeypatch):
    """Verify that users cannot access or delete charts owned by other users, but admins can."""
    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: None)
    user_a = "user-alice-uuid"
    user_b = "user-bob-uuid"

    data = {
        "chart_type": "natal",
        "title": "Alice's Secret Chart",
        "location_name": "Madurai",
        "latitude": 9.9252,
        "longitude": 78.1198,
        "timezone": "Asia/Kolkata",
        "calculation_result": {},
    }
    saved_a = save_kp_chart(user_a, data)

    # User B cannot access Alice's chart
    assert get_kp_chart(user_b, saved_a["id"]) is None

    # User B listing charts does not include Alice's chart
    bob_charts = list_kp_charts(user_b)
    assert not any(c["id"] == saved_a["id"] for c in bob_charts)

    # User B cannot delete Alice's chart
    assert delete_kp_chart(user_b, saved_a["id"]) is False
    assert get_kp_chart(user_a, saved_a["id"]) is not None

    # Admin CAN access and delete Alice's chart
    assert get_kp_chart(user_b, saved_a["id"], is_admin=True) is not None
    assert delete_kp_chart(user_b, saved_a["id"], is_admin=True) is True
    assert get_kp_chart(user_a, saved_a["id"]) is None


def test_save_kp_chart_raises_on_supabase_error(monkeypatch):
    """Verify that when a Supabase client is active and encounters an error, the failure is raised."""
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.insert.return_value.execute.side_effect = Exception("PGRST204: column customer_id does not exist")

    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: mock_client)

    data = {
        "chart_type": "natal",
        "title": "Failing Chart",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {},
    }

    with pytest.raises(RuntimeError, match="Database write failed: PGRST204"):
        save_kp_chart("test-user-error", data)


def test_list_and_get_kp_chart_raise_on_supabase_error(monkeypatch):
    """Verify list, get, and delete raise RuntimeError when Supabase operations fail."""
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.select.side_effect = Exception("Connection timeout")
    mock_table.delete.side_effect = Exception("Permission denied")

    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: mock_client)

    with pytest.raises(RuntimeError, match="Database query failed: Connection timeout"):
        list_kp_charts("test-user")

    with pytest.raises(RuntimeError, match="Database query failed: Connection timeout"):
        get_kp_chart("test-user", "record-123")

    with pytest.raises(RuntimeError, match="Database deletion failed: Permission denied"):
        delete_kp_chart("test-user", "record-123")


def test_saved_kp_charts_concurrency_and_spoofed_display_number(monkeypatch):
    """Verify concurrent saves produce sequential numbering and repository ignores client-supplied display_number."""
    import concurrent.futures

    monkeypatch.setattr("app.services.kp_engine.kp_chart_repository.get_supabase_client", lambda: None)
    user_id = "concurrent-test-user-uuid"

    # Even if client payload includes a spoofed display_number=999, repository ignores it
    data_with_spoof = {
        "chart_type": "natal",
        "title": "Client Injected Display Number",
        "location_name": "Trichy",
        "latitude": 10.7905,
        "longitude": 78.7047,
        "timezone": "Asia/Kolkata",
        "calculation_result": {},
        "display_number": 999,  # Should be ignored / computed sequentially
    }
    first_save = save_kp_chart(user_id, data_with_spoof)
    assert first_save["display_number"] == 1

    # Run 10 concurrent saves for this user
    def save_worker(idx):
        return save_kp_chart(user_id, {
            "chart_type": "natal",
            "title": f"Concurrent Chart {idx}",
            "location_name": "Trichy",
            "latitude": 10.7905,
            "longitude": 78.7047,
            "timezone": "Asia/Kolkata",
            "calculation_result": {},
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(save_worker, i) for i in range(2, 12)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    all_charts = list_kp_charts(user_id, limit=20)
    display_numbers = sorted([c["display_number"] for c in all_charts])
    assert display_numbers == list(range(1, 12)), f"Expected 1..11, got {display_numbers}"


def test_horary_boundary_validation():
    """Verify Horary seed number boundary enforcement (1..249)."""
    from pydantic import ValidationError

    base_payload = {
        "question_date": date(2026, 10, 19),
        "question_time": time(10, 0),
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }

    # 1. Valid lower boundary: 1
    req1 = HoraryKpRequest(horary_number=1, **base_payload)
    assert req1.horary_number == 1

    # 2. Valid upper boundary: 249
    req249 = HoraryKpRequest(horary_number=249, **base_payload)
    assert req249.horary_number == 249

    # 3. Invalid below lower boundary: 0
    with pytest.raises(ValidationError) as exc0:
        HoraryKpRequest(horary_number=0, **base_payload)
    assert "greater than or equal to 1" in str(exc0.value)

    # 4. Invalid negative number: -5
    with pytest.raises(ValidationError) as exc_neg:
        HoraryKpRequest(horary_number=-5, **base_payload)
    assert "greater than or equal to 1" in str(exc_neg.value)

    # 5. Invalid above upper boundary: 250
    with pytest.raises(ValidationError) as exc250:
        HoraryKpRequest(horary_number=250, **base_payload)
    assert "less than or equal to 249" in str(exc250.value)

    # 6. Invalid out-of-range number: 300
    with pytest.raises(ValidationError) as exc300:
        HoraryKpRequest(horary_number=300, **base_payload)
    assert "less than or equal to 249" in str(exc300.value)

    # 7. Missing required horary_number
    with pytest.raises(ValidationError) as exc_miss:
        HoraryKpRequest(**base_payload)
    assert "Field required" in str(exc_miss.value)


def test_cors_preflight_configuration():
    """Verify CORS middleware allows DELETE, PUT, PATCH, GET, POST, OPTIONS from configured origin."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Preflight for DELETE method from allowed origin
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    response = client.options("/api/v1/horoscope/kp/charts/test-id", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "DELETE" in allowed_methods

    # 2. Preflight from untrusted origin is rejected/not granted access
    untrusted_headers = {
        "Origin": "http://malicious-external-site.com",
        "Access-Control-Request-Method": "DELETE",
    }
    untrusted_response = client.options("/api/v1/horoscope/kp/charts/test-id", headers=untrusted_headers)
    assert untrusted_response.headers.get("access-control-allow-origin") is None


def test_kp_charts_authorization_unauthenticated():
    """Verify unauthenticated requests to KP chart persistence endpoints are rejected with HTTP 401."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. GET charts without auth
    res_get = client.get("/api/v1/horoscope/kp/charts")
    assert res_get.status_code == 401

    # 2. DELETE chart without auth
    res_del = client.delete("/api/v1/horoscope/kp/charts/any-chart-id")
    assert res_del.status_code == 401

    # 3. POST save chart without auth
    res_post = client.post("/api/v1/horoscope/kp/charts", json={
        "chart_type": "natal",
        "title": "Unauthenticated Save",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {},
    })
    assert res_post.status_code == 401



