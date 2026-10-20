"""Integration, contract, and validation tests for the Marriage Compatibility API.

Covers all Phase 9 requirements:
1. Valid request and response serialization.
2. Invalid or missing partner data.
3. Invalid dates, birth-time values, and out-of-range coordinates.
4. Unknown or approximate birth time handling and uncertainty propagation.
5. Missing KP evidence handling (include_kp=False).
6. Missing or unsupported chart data rejection (422).
7. Conflicting underlying compatibility findings and explanation transparency.
8. Preservation of separate Porutham (10.0) and Ashtakoota (36.0) scores.
9. Explicit indeterminate results without score fabrication.
10. Authentication behavior for saved records (401 when unauthenticated).
11. Saved-record ownership enforcement (404/unauthorized for foreign records).
12. No persistence or database writes during transient analysis.
13. Input immutability (no payload modification).
14. Deterministic responses for identical inputs.
15. Correct error handling without sensitive stack traces.
16. Correct OpenAPI schema generation.
17. Rules inventory endpoint availability.
"""

from __future__ import annotations
import copy
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import get_current_user, get_supabase_client
from app.schemas.marriage import (
    MarriageCompatibilityRequest,
    MarriagePartnerInput,
    MarriageCompatibilityResponse,
    RuleRegisterResponse,
)

client = TestClient(app)

MOCK_USER_A = {
    "id": "11111111-1111-1111-1111-111111111111",
    "email": "user.a@example.com",
    "role": "authenticated",
}

MOCK_USER_B = {
    "id": "22222222-2222-2222-2222-222222222222",
    "email": "user.b@example.com",
    "role": "authenticated",
}

VALID_GROOM_PAYLOAD = {
    "name": "Karthik",
    "gender": "male",
    "birth_date": "1992-04-14",
    "birth_time": "05:30:00",
    "is_birth_time_approximate": False,
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
}

VALID_BRIDE_PAYLOAD = {
    "name": "Revathi",
    "gender": "female",
    "birth_date": "1994-08-20",
    "birth_time": "14:15:00",
    "is_birth_time_approximate": False,
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
}

VALID_REQUEST_PAYLOAD = {
    "groom": VALID_GROOM_PAYLOAD,
    "bride": VALID_BRIDE_PAYLOAD,
    "rule_system": "all",
    "ayanamsa_id": 0,
    "house_system_id": 0,
    "include_timing": True,
    "include_kp": True,
}


# ===========================================================================
# 1. Valid Request & Serialization
# ===========================================================================

def test_01_valid_request_and_response_serialization():
    """Verify that a valid dual-horoscope analysis completes with HTTP 200 and valid schema."""
    resp = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Core top-level structure
    assert "metadata" in data
    assert "groom_profile" in data
    assert "bride_profile" in data
    assert "composite_assessment" in data
    assert "tamil_porutham" in data
    assert "ashtakoota" in data
    assert "dosha_analysis" in data
    assert "synastry" in data
    assert "kp_marriage" in data
    assert "final_assessment" in data

    # Validate Pydantic response parsing
    validated = MarriageCompatibilityResponse.model_validate(data)
    assert validated.groom_profile.name == "Karthik"
    assert validated.bride_profile.name == "Revathi"
    assert validated.composite_assessment.overall_outcome in (
        "FAVOURABLE_UNDER_SELECTED_RULES",
        "MIXED_OR_CONDITIONAL",
        "UNFAVOURABLE_UNDER_SELECTED_RULES",
        "INDETERMINATE",
    )


# ===========================================================================
# 2. Invalid or Missing Partner Data
# ===========================================================================

def test_02_invalid_or_missing_partner_data():
    """Missing groom or bride must fail with HTTP 422 Unprocessable Entity."""
    # Omit bride
    incomplete = {"groom": VALID_GROOM_PAYLOAD}
    resp = client.post("/api/marriage-compatibility/analyze", json=incomplete)
    assert resp.status_code == 422

    # Incomplete groom (missing birth_date and saved_horoscope_id)
    bad_groom = {"name": "NoDate", "latitude": 13.0, "longitude": 80.0, "timezone": "Asia/Kolkata"}
    resp2 = client.post(
        "/api/marriage-compatibility/analyze",
        json={"groom": bad_groom, "bride": VALID_BRIDE_PAYLOAD},
    )
    assert resp2.status_code == 422


# ===========================================================================
# 3. Invalid Dates, Time Values & Coordinate Bounds
# ===========================================================================

def test_03_invalid_dates_and_birth_time_values():
    """Malformed dates, impossible times, and invalid coordinates must fail with 422."""
    # Impossible date (Feb 30)
    bad_date_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    bad_date_payload["groom"]["birth_date"] = "1992-02-30"
    resp = client.post("/api/marriage-compatibility/analyze", json=bad_date_payload)
    assert resp.status_code == 422

    # Latitude out of bounds (> 90.0)
    bad_lat_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    bad_lat_payload["bride"]["latitude"] = 95.0
    resp_lat = client.post("/api/marriage-compatibility/analyze", json=bad_lat_payload)
    assert resp_lat.status_code == 422

    # Longitude out of bounds (< -180.0)
    bad_lon_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    bad_lon_payload["bride"]["longitude"] = -195.0
    resp_lon = client.post("/api/marriage-compatibility/analyze", json=bad_lon_payload)
    assert resp_lon.status_code == 422

    # Out of supported astronomical ephemeris range (year 1600)
    old_year_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    old_year_payload["groom"]["birth_date"] = "1650-01-01"
    resp_old = client.post("/api/marriage-compatibility/analyze", json=old_year_payload)
    assert resp_old.status_code == 422


# ===========================================================================
# 4. Unknown or Approximate Birth Time
# ===========================================================================

def test_04_unknown_or_approximate_birth_time():
    """Preserve approximate birth time uncertainty through pipeline and response."""
    approx_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    approx_payload["groom"]["is_birth_time_approximate"] = True

    resp = client.post("/api/marriage-compatibility/analyze", json=approx_payload)
    assert resp.status_code == 200
    data = resp.json()

    comp = data["composite_assessment"]
    # Check that uncertainty is documented
    has_approx_evidence = any(
        "approximate" in ev.lower() or "rectification" in ev.lower()
        for ev in comp["missing_or_uncertain_evidence"]
    )
    assert has_approx_evidence, "Expected approximate birth time note in missing_or_uncertain_evidence"

    # Check conflict findings for boundary sensitivity
    conflict_types = [c["conflict_type"] for c in comp["conflicting_findings"]]
    assert "BIRTH_TIME_BOUNDARY_SENSITIVITY" in conflict_types


# ===========================================================================
# 5. Missing KP Evidence Handling
# ===========================================================================

def test_05_missing_kp_evidence():
    """When include_kp=False, KP evaluation is cleanly bypassed and reported as INDETERMINATE."""
    no_kp_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    no_kp_payload["include_kp"] = False

    resp = client.post("/api/marriage-compatibility/analyze", json=no_kp_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["kp_marriage"] is None
    kp_cat = data["composite_assessment"]["category_verdicts"]["kp_promise"]
    assert kp_cat["status"] == "INDETERMINATE"


# ===========================================================================
# 6. Missing or Unsupported Chart Data
# ===========================================================================

def test_06_missing_or_unsupported_chart_data():
    """Providing empty objects or null coordinates must trigger clean 422 errors."""
    payload = {
        "groom": {},
        "bride": {},
    }
    resp = client.post("/api/marriage-compatibility/analyze", json=payload)
    assert resp.status_code == 422


# ===========================================================================
# 7. Conflicting Underlying Compatibility Findings
# ===========================================================================

def test_07_conflicting_underlying_compatibility_findings():
    """Engine must isolate and explain divergences between traditions without masking them."""
    resp = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()

    conflicts = data["composite_assessment"]["conflicting_findings"]
    assert isinstance(conflicts, list)
    for c in conflicts:
        assert "conflict_type" in c
        assert "title_en" in c
        assert "title_ta" in c
        assert "resolution_principle" in c
        assert "explanation_en" in c
        assert "explanation_ta" in c


# ===========================================================================
# 8. Preservation of Separate Porutham and Ashtakoota Scales
# ===========================================================================

def test_08_preservation_of_separate_porutham_and_ashtakoota_scores():
    """Ensure Porutham (out of 10.0) and Ashtakoota (out of 36.0) are never blended."""
    resp = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()

    # Tamil 10 Porutham
    porutham = data["tamil_porutham"]
    assert porutham["max_score"] == 10.0
    assert 0.0 <= porutham["total_score"] <= 10.0

    # North Indian Ashtakoota
    ashtakoota = data["ashtakoota"]
    assert ashtakoota["max_points"] == 36.0
    assert 0.0 <= ashtakoota["total_points"] <= 36.0

    # Ensure no combined percentage field exists
    assert "blended_score" not in data
    assert "composite_score" not in data


# ===========================================================================
# 9. Explicit Indeterminate Results
# ===========================================================================

def test_09_explicit_indeterminate_results():
    """Indeterminate components must remain explicitly INDETERMINATE."""
    no_kp_payload = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    no_kp_payload["include_kp"] = False

    resp = client.post("/api/marriage-compatibility/analyze", json=no_kp_payload)
    assert resp.status_code == 200
    data = resp.json()

    cats = data["composite_assessment"]["category_verdicts"]
    assert cats["kp_promise"]["status"] == "INDETERMINATE"


# ===========================================================================
# 10. Authentication Behavior for Saved Records
# ===========================================================================

def test_10_authentication_behavior_for_saved_records():
    """Accessing saved_horoscope_id without authentication credentials must return HTTP 401."""
    saved_payload = {
        "groom": {"saved_horoscope_id": "33333333-3333-3333-3333-333333333333"},
        "bride": VALID_BRIDE_PAYLOAD,
    }
    # No auth header provided
    resp = client.post("/api/marriage-compatibility/analyze", json=saved_payload)
    assert resp.status_code == 401
    assert "Authentication token required" in resp.json()["detail"]


# ===========================================================================
# 11. Saved-Record Ownership Enforcement
# ===========================================================================

def test_11_saved_record_ownership_enforcement():
    """Accessing another user's saved horoscope must return HTTP 404 / Unauthorized."""
    saved_payload = {
        "groom": {"saved_horoscope_id": "33333333-3333-3333-3333-333333333333"},
        "bride": VALID_BRIDE_PAYLOAD,
    }

    from app.routers.marriage_compatibility import get_optional_current_user

    # Mock authenticated user as User A
    app.dependency_overrides[get_optional_current_user] = lambda: MOCK_USER_A

    # Mock Supabase returning a record owned by User B
    mock_supabase = MagicMock()
    mock_supabase.table().select().eq().execute.return_value = MagicMock(
        data=[{
            "id": "33333333-3333-3333-3333-333333333333",
            "user_id": MOCK_USER_B["id"],  # Owned by User B
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "timezone": "Asia/Kolkata",
            "latitude": 13.0,
            "longitude": 80.0,
        }]
    )

    with patch("app.services.marriage_engine.service.get_supabase_client", return_value=mock_supabase):
        resp = client.post(
            "/api/marriage-compatibility/analyze",
            json=saved_payload,
            headers={"Authorization": "Bearer valid-token"},
        )
        # Must return 404 Not Found to prevent ID enumeration
        assert resp.status_code == 404
        assert "not found or unauthorized" in resp.json()["detail"].lower()

    app.dependency_overrides.pop(get_optional_current_user, None)


# ===========================================================================
# 12. No Database Writes During Transient Analysis
# ===========================================================================

def test_12_no_persistence_or_database_writes_during_transient_analysis():
    """Transient birth input analysis must execute without any DB write operations."""
    mock_supabase = MagicMock()
    with patch("app.services.marriage_engine.service.get_supabase_client", return_value=mock_supabase):
        resp = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
        assert resp.status_code == 200

        # Assert no table writes were performed
        mock_supabase.table().insert.assert_not_called()
        mock_supabase.table().update.assert_not_called()
        mock_supabase.table().delete.assert_not_called()


# ===========================================================================
# 13. Input Immutability
# ===========================================================================

def test_13_no_modification_of_input_data():
    """Payload passed to endpoint must not be mutated."""
    payload_copy = copy.deepcopy(VALID_REQUEST_PAYLOAD)
    resp = client.post("/api/marriage-compatibility/analyze", json=payload_copy)
    assert resp.status_code == 200
    assert payload_copy == VALID_REQUEST_PAYLOAD


# ===========================================================================
# 14. Deterministic Responses for Identical Inputs
# ===========================================================================

def test_14_deterministic_responses_for_identical_inputs():
    """Two requests with identical inputs must return identical verdicts and fingerprints."""
    resp1 = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
    resp2 = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    d1 = resp1.json()
    d2 = resp2.json()

    assert d1["composite_assessment"]["overall_outcome"] == d2["composite_assessment"]["overall_outcome"]
    assert d1["final_assessment"]["reproducibility_fingerprint"] == d2["final_assessment"]["reproducibility_fingerprint"]
    assert d1["tamil_porutham"]["total_score"] == d2["tamil_porutham"]["total_score"]
    assert d1["ashtakoota"]["total_points"] == d2["ashtakoota"]["total_points"]


# ===========================================================================
# 15. Correct Error Handling Without Stack Traces
# ===========================================================================

def test_15_correct_error_handling_without_sensitive_stack_traces():
    """Internal exceptions must return HTTP 500 without leaking python stack traces."""
    with patch(
        "app.services.marriage_engine.service.evaluate_composite_marriage_assessment",
        side_effect=RuntimeError("Simulated internal astronomical calculation failure"),
    ):
        resp = client.post("/api/marriage-compatibility/analyze", json=VALID_REQUEST_PAYLOAD)
        assert resp.status_code == 500
        data = resp.json()
        assert "detail" in data
        assert "Traceback" not in data["detail"]
        assert "File \"" not in data["detail"]


# ===========================================================================
# 16. Correct OpenAPI Schema Generation
# ===========================================================================

def test_16_correct_openapi_schema_generation():
    """Verify OpenAPI schema publishes marriage endpoints, request models, and schemas."""
    schema = app.openapi()
    paths = schema.get("paths", {})

    # Check endpoints
    assert "/api/marriage-compatibility/analyze" in paths
    assert "/api/v1/marriage-compatibility/analyze" in paths
    assert "/api/marriage-compatibility/rules" in paths

    post_op = paths["/api/marriage-compatibility/analyze"].get("post", {})
    assert post_op.get("summary") == "Analyze Marriage Compatibility"
    assert "200" in post_op.get("responses", {})
    assert "422" in post_op.get("responses", {})

    # Check schemas
    components = schema.get("components", {}).get("schemas", {})
    assert "MarriageCompatibilityRequest" in components
    assert "MarriageCompatibilityResponse" in components
    assert "CompositeAssessmentSummary" in components


# ===========================================================================
# 17. Rules Inventory Endpoint
# ===========================================================================

def test_17_rules_inventory_endpoint():
    """Verify GET /api/marriage-compatibility/rules returns approved ruleset."""
    resp = client.get("/api/marriage-compatibility/rules")
    assert resp.status_code == 200
    data = resp.json()

    validated = RuleRegisterResponse.model_validate(data)
    assert len(validated.rules) >= 9
    rule_ids = [r.rule_id for r in validated.rules]
    assert "POR-01" in rule_ids
    assert "POR-09" in rule_ids  # Rajju
    assert "KOT-08" in rule_ids  # Nadi
    assert "DOS-KUJA-01" in rule_ids
    assert "KP-MARR-01" in rule_ids
