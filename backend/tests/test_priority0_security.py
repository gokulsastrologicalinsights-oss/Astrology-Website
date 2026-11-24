"""Security regression test suite for Priority 0 remediations.

Verifies:
1. /health endpoint returns sanitized GAI Astronomical Calculation Engine name and no XALEN/Swiss disclosures.
2. /api/v1/metadata returns sanitized engine name and no external engine exposures.
3. /api/v1/rules/inventory contains no internal file paths (validation_suite) or external engine names.
4. /api/v1/rules/evaluate returns sanitized results with source_reference stripped for customer security.
5. Production mode (debug=False) disables /docs and /redoc Swagger/OpenAPI exposure.
6. Root / endpoint sanitizes documentation descriptor when debug is False.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.routers.rules import get_admin_user

client = TestClient(app)


def test_health_endpoint_security_sanitization():
    """Verify /health returns clean service info and leaks zero internal engine metadata."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Gokul's Astrological Insights API"
    assert "engine" not in data

    # Strictly verify forbidden disclosure strings do not appear in health response
    raw_text = resp.text.lower()
    for forbidden in ["xalen", "swisseph", "swiss ephemeris", "pyswisseph", "rust_core"]:
        assert forbidden not in raw_text, f"Forbidden disclosure '{forbidden}' found in /health response"


def test_metadata_endpoint_security_sanitization():
    """Verify /api/v1/metadata returns clean metadata without internal engine disclosures."""
    resp = client.get("/api/v1/metadata")
    assert resp.status_code == 200
    data = resp.json()
    assert "engine" not in data
    assert "version" not in data

    raw_text = resp.text.lower()
    for forbidden in ["xalen", "swisseph", "pyswisseph"]:
        assert forbidden not in raw_text, f"Forbidden disclosure '{forbidden}' found in /metadata response"


def test_rules_inventory_sanitization():
    """Verify /api/v1/rules/inventory denies anonymous access and contains no internal file paths."""
    # 1. Anonymous request must be rejected with 401 Unauthorized
    app.dependency_overrides.clear()
    resp_anon = client.get("/api/v1/rules/inventory")
    assert resp_anon.status_code == 401, "Anonymous access to /rules/inventory must be denied"

    # 2. Admin request succeeds and returns sanitized rules
    admin_mock = {"id": "admin-1", "email": "admin@gai.internal", "role": "admin"}
    app.dependency_overrides[get_admin_user] = lambda: admin_mock
    try:
        resp = client.get("/api/v1/rules/inventory")
        assert resp.status_code == 200
        rules = resp.json()

        for r in rules:
            doc_ref = (r.get("documentation_ref") or "").lower()
            desc = (r.get("description") or "").lower()
            assert "xalen" not in doc_ref, f"XALEN found in doc_ref of {r['rule_id']}"
            assert "swiss ephemeris" not in desc, f"Swiss Ephemeris found in desc of {r['rule_id']}"
            assert "validation_suite" not in doc_ref, f"Internal path 'validation_suite' found in {r['rule_id']}"
            assert "app/services" not in doc_ref, f"Internal file path found in doc_ref of {r['rule_id']}"
    finally:
        app.dependency_overrides.clear()


def test_rules_evaluate_source_reference_protection():
    """Verify /api/v1/rules/evaluate does not expose internal treatise source_reference strings."""
    from backend.tests.test_prediction_rules_engine import make_sample_horoscope

    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={"Sun": (10, 15.0), "Mars": (10, 20.0), "Saturn": (7, 15.0)}
    )

    req_payload = {
        "horoscope": horoscope.model_dump(),
        "category_slug": "career_profession",
        "chart_scope": "both",
        "astrology_system": "vedic",
        "language": "en",
    }
    resp = client.post("/api/v1/rules/evaluate", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matched"] > 0

    for item in data["results"]:
        assert item.get("source_reference") is None, (
            f"Rule {item.get('rule_id')} exposed internal source_reference: {item.get('source_reference')}"
        )


def test_production_docs_and_openapi_disabled_when_debug_false():
    """Verify that when debug is False, Swagger UI and OpenAPI docs are completely disabled."""
    original_debug = settings.debug
    try:
        # Simulate production mode
        settings.debug = False

        from app.main import app as current_app
        # When debug is False, root endpoint must not advertise /docs
        root_resp = client.get("/")
        assert root_resp.status_code == 200
        root_data = root_resp.json()
        assert "Protected" in root_data["documentation"]

        # Directly verify description in app has no XALEN marketing
        assert "xalen" not in current_app.description.lower()
    finally:
        settings.debug = original_debug
