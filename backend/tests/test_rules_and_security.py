"""Automated tests for Rule Engine, CORS, and Security limits."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
}


def test_rules_inventory():
    response = client.get("/api/v1/rules/inventory")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) >= 5
    rule_ids = [r["rule_id"] for r in rules]
    assert "RULE-HORO-01" in rule_ids
    assert "RULE-DASA-01" in rule_ids
    assert "RULE-KP-01" in rule_ids
    assert "RULE-CAREER-01" in rule_ids

    # Verify every rule has tradition and documentation ref
    for r in rules:
        assert r["tradition"] != ""
        assert r["status"] in ("Implemented", "Draft", "Requires Verification", "Pending Canon Specification")


def test_career_rule_analysis():
    response = client.post("/api/v1/rules/career", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["tenth_house_sign"] != ""
    assert data["tenth_house_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    assert isinstance(data["tenth_house_occupants"], list)
    assert isinstance(data["planets_aspecting_tenth"], list)
    assert data["amatyakaraka"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    # Disclaimer must explicitly warn that these are traditional cultural heuristics
    assert "not scientifically proven" in data["disclaimer"]
    # Outstanding work list must be transparent
    assert len(data["outstanding_work"]) > 0


def test_cors_headers_allowed_origin():
    # Pre-flight OPTIONS request with allowed origin
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/api/v1/horoscope/calculate", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_request_body_size_limit():
    # Sending payload with declared Content-Length exceeding 1MB (1,048,576 bytes)
    headers = {
        "Content-Length": "2000000",  # 2MB
        "Content-Type": "application/json",
    }
    response = client.post("/api/v1/horoscope/calculate", headers=headers, content=b"{}")
    assert response.status_code == 413
    assert response.json()["error"] == "Request entity too large"
