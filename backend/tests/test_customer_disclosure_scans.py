"""Automated Customer Disclosure Regression Suite for GAI.

Validates that no proprietary engine names, third-party ephemeris libraries,
modern authors, classical book chapter citations, or internal rule IDs are
leaked in:
1. /health and /api/v1/metadata responses.
2. /api/v1/horoscope/calculate calculation responses.
3. /api/v1/unified/predict responses.
4. /api/v1/rules/inventory and /api/v1/rules/evaluate responses.
5. Generated 9-Page Comprehensive Vedic PDF text and metadata.
6. Generated 6-Page KP Astrology PDF text and metadata.
"""

from datetime import date, time
from io import BytesIO
import re
import pytest
import pypdf
from fastapi.testclient import TestClient

from app.main import app
from app.routers.rules import get_admin_user
from app.schemas.common import BirthInput
from app.services.pdf_report_engine import (
    build_report_data,
    generate_horoscope_pdf_bytes,
    build_kp_report_data,
    generate_kp_pdf_bytes,
)

client = TestClient(app)

FORBIDDEN_API_TERMS = [
    r"\bxalen\b",
    r"\bswisseph\b",
    r"\bswiss\s+ephemeris\b",
    r"\bpyswisseph\b",
]

FORBIDDEN_AUTHOR_AND_DISCLOSURE_TERMS = [
    r"\bxalen\b",
    r"\bswiss\s+ephemeris\b",
    r"\bmarc\s+boney\b",
    r"\bmark\s+boney\b",
    r"\bdr\.?\s*s\.?\s*krishna\s*kumar\b",
    r"\bheinrich\s+d[aä]ath\b",
    r"\bsivadasan\s+ravi\b",
    r"\bsannu\s+ahmed\b",
    r"\bpicatrix\b",
]

SAMPLE_BIRTH = BirthInput(
    birth_date=date(1990, 5, 15),
    birth_time=time(14, 30),
    timezone="Asia/Kolkata",
    latitude=13.0827,
    longitude=80.2707,
)


def _assert_no_forbidden_strings(text: str, forbidden_patterns: list[str], context_label: str):
    for pattern in forbidden_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        assert match is None, (
            f"Forbidden technical disclosure found in {context_label}: '{match.group(0)}' "
            f"(matched pattern: {pattern})"
        )


def test_api_health_and_metadata_clean():
    """Verify /health and /api/v1/metadata contain no proprietary engine or library disclosures."""
    # 1. Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    health_json = res_health.json()
    assert "engine" not in health_json
    _assert_no_forbidden_strings(res_health.text, FORBIDDEN_API_TERMS, "/health")

    # 2. Metadata
    res_meta = client.get("/api/v1/metadata")
    assert res_meta.status_code == 200
    meta_json = res_meta.json()
    assert "engine" not in meta_json
    assert "version" not in meta_json
    _assert_no_forbidden_strings(res_meta.text, FORBIDDEN_API_TERMS, "/api/v1/metadata")


def test_api_horoscope_calculate_metadata_clean():
    """Verify /api/v1/horoscope/calculate returns clean calculation metadata without engine disclosure."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa_id": 0,
        "house_system_id": 1,
    }
    res = client.post("/api/v1/horoscope/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "engine" not in data["metadata"]
    _assert_no_forbidden_strings(res.text, FORBIDDEN_API_TERMS, "horoscope.calculate")


def test_api_rules_inventory_clean():
    """Verify /api/v1/rules/inventory denies anonymous access and returns clean rules for admin."""
    # Anon check
    res_anon = client.get("/api/v1/rules/inventory")
    assert res_anon.status_code == 401

    # Admin check
    app.dependency_overrides[get_admin_user] = lambda: {"id": "admin-1", "role": "admin"}
    try:
        res = client.get("/api/v1/rules/inventory")
        assert res.status_code == 200
        rules = res.json()
        assert isinstance(rules, list)
        assert len(rules) > 0

        for r in rules:
            ref = r.get("documentation_ref", "")
            assert "validation_suite" not in ref, f"Internal path found in {r['rule_id']}"
            assert "xalen" not in ref.lower(), f"XALEN found in {r['rule_id']}"
            assert "swiss ephemeris" not in ref.lower(), f"Swiss Ephemeris found in {r['rule_id']}"
            assert "app/services" not in ref, f"Internal file path found in {r['rule_id']}"
    finally:
        app.dependency_overrides.clear()


def test_api_rules_evaluate_source_reference_concealment():
    """Verify /api/v1/rules/evaluate conceals source_reference from customer output."""
    from backend.tests.test_prediction_rules_engine import make_sample_horoscope
    horoscope = make_sample_horoscope()
    payload = {
        "horoscope": horoscope.model_dump(mode="json"),
        "rule_ids": None,
        "astrology_system": None,
    }
    res = client.post("/api/v1/rules/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    results = data.get("results", [])
    assert len(results) > 0
    for r in results:
        assert r.get("source_reference") is None, f"Source reference leaked in {r.get('rule_id')}"


def test_pdf_9page_text_and_metadata_clean():
    """Verify the 9-page PDF contains no disclosures in its text content or document metadata."""
    data = build_report_data(
        birth_input=SAMPLE_BIRTH,
        native_name="Arun Kumar",
        gender="male",
        language="en",
    )
    pdf_bytes = generate_horoscope_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 20000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 9

    # Check Document Metadata (Author, Title, Creator)
    meta = reader.metadata or {}
    meta_str = " ".join(str(v) for v in meta.values())
    _assert_no_forbidden_strings(meta_str, FORBIDDEN_AUTHOR_AND_DISCLOSURE_TERMS, "9-Page PDF Metadata")
    assert "Gokul's Astrological Insights" in meta.get("/Author", "")

    # Check all 9 pages text
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    _assert_no_forbidden_strings(full_text, FORBIDDEN_AUTHOR_AND_DISCLOSURE_TERMS, "9-Page PDF Text")


def test_pdf_kp_6page_text_and_metadata_clean():
    """Verify the KP 6-page PDF contains no disclosures in its text content or document metadata."""
    data = build_kp_report_data(
        birth_input=SAMPLE_BIRTH,
        native_name="Kavitha Raman",
        gender="female",
        language="en",
    )
    assert data.chart_type == "natal"
    pdf_bytes = generate_kp_pdf_bytes(data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 10000

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    meta = reader.metadata or {}
    meta_str = " ".join(str(v) for v in meta.values())
    _assert_no_forbidden_strings(meta_str, FORBIDDEN_AUTHOR_AND_DISCLOSURE_TERMS, "KP PDF Metadata")
    assert "Gokul's Astrological Insights" in meta.get("/Author", "")

    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    _assert_no_forbidden_strings(full_text, FORBIDDEN_AUTHOR_AND_DISCLOSURE_TERMS, "KP PDF Text")
