"""Integration test for Medical Astrology FastAPI endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_PAYLOAD = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 0,
    "house_system": 0,
    "gender": "male",
}


def test_medical_astrology_endpoint_success():
    """Verify POST /api/v1/vedic/medical-astrology returns 200 with valid schema."""
    response = client.post("/api/v1/vedic/medical-astrology", json=TEST_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    assert data["rule_set_version"] == "1.0.0"
    assert "Medical Astrology presents traditional astrological interpretations" in data["disclaimer_en"]
    assert "மருத்துவ ஜோதிடம் பாரம்பரிய ஜோதிட விளக்கங்களை" in data["disclaimer_ta"]

    # Check Vedic Perspective A, B, C
    va = data["vedic_analysis"]
    assert "birth_chart" in va
    assert va["birth_chart"]["lagna_analysis"]["house_number"] == 1
    assert va["birth_chart"]["sixth_house_analysis"]["house_number"] == 6
    assert len(va["birth_chart"]["anatomical_mappings"]) == 12

    assert "current_period" in va
    assert "historical_periods" in va

    # Check KP Analytical system
    if data.get("kp_analysis"):
        kp = data["kp_analysis"]
        assert kp["sixth_csl"]["cusp_number"] == 6
        assert kp["sixth_csl"]["csl_planet"]


def test_medical_astrology_endpoint_invalid_date():
    """Verify 422 validation on invalid birth date."""
    bad_payload = dict(TEST_PAYLOAD)
    bad_payload["birth_date"] = "invalid-date"
    response = client.post("/api/v1/vedic/medical-astrology", json=bad_payload)
    assert response.status_code in (422, 400)
