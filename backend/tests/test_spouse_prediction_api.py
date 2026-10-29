"""FastAPI endpoint integration test for /api/v1/predictions/spouse."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_spouse_prediction_endpoint_guest(client):
    """Test calling /api/v1/predictions/spouse without bearer token (guest/preview mode)."""
    payload = {
        "birth": {
            "birth_date": "1995-10-24",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "gender": "male",
    }
    response = client.post("/api/v1/predictions/spouse", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "ascendant_sign" in data
    assert "seventh_sign" in data
    assert "seventh_lord" in data
    assert "desire_vs_reality" in data
    assert "karakas" in data
    assert "navamsa_d9" in data
    assert "trait_scores" in data
    assert "remedies" in data
    assert data["seventh_sign"]["sign"] == "Aries" or data["seventh_sign"]["sign"]
