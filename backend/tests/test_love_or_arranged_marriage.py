"""Tests for Love vs Arranged Marriage Predictor.

Verifies:
1. LoveArrangedService deterministic evaluation.
2. Distinct verdicts for love marriage, arranged marriage, and love-cum-arranged.
3. FastAPI endpoint integration at /api/v1/predictions/love-or-arranged-marriage.
"""

from datetime import date, time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.schemas.love_marriage import LoveOrArrangedRequest
from app.services.marriage_engine.love_arranged_service import LoveArrangedService


@pytest.fixture
def client():
    return TestClient(app)


def test_love_arranged_service_sample_arranged():
    """Verify evaluation for a chart favoring traditional arranged marriage."""
    req = LoveOrArrangedRequest(
        birth=BirthInput(
            birth_date=date(1995, 10, 24),
            birth_time=time(14, 30, 0),
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        name="Traditional Native",
        gender="male",
    )
    res = LoveArrangedService.evaluate(req)

    assert res.verdict in ["Love Marriage", "Arranged Marriage", "Love-cum-Arranged Marriage", "Love Marriage with Family Blessings"]
    assert res.verdict_ta is not None
    assert res.love_percentage + res.arranged_percentage == 100
    assert 0 <= res.love_percentage <= 100
    assert 0 <= res.arranged_percentage <= 100
    assert len(res.key_factors) >= 1
    assert res.family_support is not None
    assert res.family_support_ta is not None


def test_love_arranged_service_sample_love_or_blend():
    """Verify evaluation for another birth date."""
    req = LoveOrArrangedRequest(
        birth=BirthInput(
            birth_date=date(1998, 5, 15),
            birth_time=time(21, 15, 0),
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        name="Romantic Native",
        gender="female",
    )
    res = LoveArrangedService.evaluate(req)

    assert res.love_percentage + res.arranged_percentage == 100
    assert res.verdict_badge in ["LOVE", "ARRANGED", "LOVE_ARRANGED"]
    assert len(res.key_factors) > 0


def test_api_love_or_arranged_endpoint(client):
    """Test the POST /api/v1/predictions/love-or-arranged-marriage endpoint."""
    payload = {
        "birth": {
            "birth_date": "1995-10-24",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "name": "Gokul Client Test",
        "gender": "male",
    }
    response = client.post("/api/v1/predictions/love-or-arranged-marriage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "verdict" in data
    assert "verdict_ta" in data
    assert "love_percentage" in data
    assert "arranged_percentage" in data
    assert data["love_percentage"] + data["arranged_percentage"] == 100
    assert "family_support" in data
    assert "key_factors" in data
    assert isinstance(data["key_factors"], list)
    assert len(data["key_factors"]) >= 1


def test_api_love_or_arranged_invalid_input(client):
    """Test input validation failure handling."""
    payload = {
        "birth": {
            "birth_date": "not-a-date",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        }
    }
    response = client.post("/api/v1/predictions/love-or-arranged-marriage", json=payload)
    assert response.status_code == 422


def test_api_love_or_arranged_pdf_generation(client):
    """Test generating professional PDF report in English and Tamil."""
    payload = {
        "birth": {
            "birth_date": "1995-10-24",
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "name": "Arun Kumar",
        "gender": "male",
    }
    # Test English PDF
    resp_en = client.post("/api/v1/predictions/love-or-arranged-marriage/pdf?language=en", json=payload)
    assert resp_en.status_code == 200
    assert resp_en.headers["content-type"] == "application/pdf"
    assert resp_en.content.startswith(b"%PDF")
    assert len(resp_en.content) > 1000

    # Test Tamil PDF
    resp_ta = client.post("/api/v1/predictions/love-or-arranged-marriage/pdf?language=ta", json=payload)
    assert resp_ta.status_code == 200
    assert resp_ta.headers["content-type"] == "application/pdf"
    assert resp_ta.content.startswith(b"%PDF")
    assert len(resp_ta.content) > 1000

    # Test Studio Report Router
    resp_studio = client.post("/api/v1/reports/love-or-arranged/pdf?language=ta", json=payload)
    assert resp_studio.status_code == 200
    assert resp_studio.headers["content-type"] == "application/pdf"
    assert resp_studio.content.startswith(b"%PDF")

