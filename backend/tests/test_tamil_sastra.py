"""Tests for the Tamil Astrology & Daily Dharma Sastra API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_medical_deities(client):
    response = client.get("/api/v1/tamil-sastra/medical-deities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 22
    # Verify Palani Murugan for diabetes / renal
    diabetes_item = next((item for item in data if item["id"] == 7), None)
    assert diabetes_item is not None
    assert "பழனி முருகன்" in diabetes_item["deity_ta"]
    assert "Palani Murugan" in diabetes_item["deity_en"]


def test_search_medical_deities(client):
    response = client.get("/api/v1/tamil-sastra/medical-deities?query=asthma")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Vishnu" in data[0]["deity_en"] or "விஷ்ணு" in data[0]["deity_ta"]


def test_get_life_wishes(client):
    response = client.get("/api/v1/tamil-sastra/life-wishes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20
    # Ganesha for obstacles
    assert data[0]["id"] == 1
    assert "விநாயகர்" in data[0]["deity_ta"]


def test_get_ramayana_parayanam(client):
    response = client.get("/api/v1/tamil-sastra/ramayana-parayanam")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 19
    # Seetha kalyanam for marriage
    kalyanam = next((item for item in data if "சீதாகல்யாணம்" in item["sarga_title_ta"]), None)
    assert kalyanam is not None
    assert "Bala Kanda" in kalyanam["kandam_en"]


def test_get_vastu_timings(client):
    response = client.get("/api/v1/tamil-sastra/vastu-timings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    assert data[0]["tamil_month"] == "சித்திரை"
    assert data[0]["solar_day"] == 10


def test_get_vastu_rules(client):
    response = client.get("/api/v1/tamil-sastra/vastu-rules")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 18
    # Filter by category
    water_resp = client.get("/api/v1/tamil-sastra/vastu-rules?category=water")
    assert water_resp.status_code == 200
    assert len(water_resp.json()) >= 1


def test_get_soolam_pariharam(client):
    response = client.get("/api/v1/tamil-sastra/soolam-pariharam")
    assert response.status_code == 200
    data = response.json()
    assert "vaara_soolam" in data
    assert "tithi_soolam" in data
    assert "nakshatra_soolam" in data


def test_get_gowri_panchangam(client):
    # Test Monday (0)
    response = client.get("/api/v1/tamil-sastra/gowri-panchangam?weekday=0")
    assert response.status_code == 200
    slots = response.json()
    assert len(slots) == 8
    assert slots[0]["name_ta"] == "அமிர்தம்"
    assert slots[0]["is_favorable"] is True


def test_get_special_muhurtas(client):
    response = client.get("/api/v1/tamil-sastra/special-muhurtas")
    assert response.status_code == 200
    data = response.json()
    assert "kadan_theera" in data
    assert "pudhu_kanakku" in data
    assert "deepam_rules" in data
    assert "temple_pradakshina" in data


def test_get_tamil_numerology(client):
    response = client.get("/api/v1/tamil-sastra/numerology?birth_number=1")
    assert response.status_code == 200
    data = response.json()
    assert data["ruling_planet"] == "Sun (சூரியன்)"
    assert 8 in data["unlucky_numbers"]
    assert 1 in data["lucky_numbers"]


def test_compute_daily_guidance(client):
    payload = {"date": "2026-11-01"}
    response = client.post("/api/v1/tamil-sastra/daily-guidance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-11-01"
    assert "naal_vizhippu_ta" in data
    assert "vaara_soolam_ta" in data
    assert len(data["gowri_panchangam_day"]) == 8
    assert len(data["dos_for_today_ta"]) > 0
