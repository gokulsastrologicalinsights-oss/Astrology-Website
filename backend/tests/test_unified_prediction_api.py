"""Integration and Contract Tests for Unified Marriage Prediction API Router.

Tests:
1. Unauthorized request rejection (401).
2. Valid authenticated request execution and response schema verification (200).
3. Missing and malformed request payload validation (422).
4. Invalid timezone and coordinate range validation (422).
5. Invalid birth-time uncertainty bounds (422).
6. Reversed timing search ranges (422).
7. Unsupported polar-latitude handling (INDETERMINATE with SCAN_FAILED_OR_INCOMPLETE).
8. Calculation error handling (500 without leaking stack traces).
9. Decoupled timing status and natal verdict preservation.
10. Regression checks confirming existing endpoints remain unaffected.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import xalen

from app.main import app
from app.services.auth_service import get_current_user
from app.services.unified_prediction.models import (
    EventVerdict,
    TimingStatus,
    PromiseVerdict,
    KPInternalModifier,
    VedicInternalModifier,
    RuleProvenanceTag,
    KPPromiseDetail,
    VedicPromiseDetail,
    ScanStatus,
)

client = TestClient(app)

MOCK_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "testuser@example.com",
    "role": "authenticated",
}

VALID_PAYLOAD = {
    "birth": {
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    },
    "birth_time_uncertainty_seconds": 120.0,
    "start_year": 2024,
    "end_year": 2030,
}


@pytest.fixture(autouse=True)
def override_auth():
    """Default fixture to authenticate requests, with test-level clear option."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.pop(get_current_user, None)


# ===========================================================================
# 1. Authentication & Authorization Enforcement
# ===========================================================================

def test_api_unauthorized_request_rejected():
    """Unauthenticated requests without Bearer token must return HTTP 401."""
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
    assert resp.status_code == 401
    assert "detail" in resp.json()


# ===========================================================================
# 2. Valid Authenticated Prediction & Schema Contract
# ===========================================================================

def test_api_valid_authenticated_prediction_success():
    """Valid authenticated request executes full pipeline and returns complete schema."""
    resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()

    assert data["final_verdict"] in [v.value for v in EventVerdict]
    assert data["timing_status"] in [t.value for t in TimingStatus]
    assert "kp_promise" in data
    assert "vedic_promise" in data
    assert "birth_time_sensitivity" in data
    assert "metadata" in data
    assert data["reconciliation_rule_id"] == "UNI-MARR-REC-001"


# ===========================================================================
# 3. Input Validation & Error Handling (HTTP 422)
# ===========================================================================

def test_api_missing_required_fields():
    """Missing birth_date or coordinates must return HTTP 422."""
    malformed_payload = {
        "birth": {
            "birth_time": "14:30:00",
            "timezone": "Asia/Kolkata",
            # missing birth_date, latitude, longitude
        }
    }
    resp = client.post("/api/v1/predictions/marriage", json=malformed_payload)
    assert resp.status_code == 422


def test_api_invalid_timezone():
    """Invalid timezone string format must return HTTP 422."""
    payload = {
        **VALID_PAYLOAD,
        "birth": {
            **VALID_PAYLOAD["birth"],
            "timezone": "Invalid/Space Zone!",
        },
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload)
    assert resp.status_code == 422


def test_api_invalid_geographic_coordinates():
    """Coordinates outside physical limits must return HTTP 422."""
    payload_bad_lat = {
        **VALID_PAYLOAD,
        "birth": {
            **VALID_PAYLOAD["birth"],
            "latitude": 95.0,  # Invalid: > 90
        },
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_bad_lat)
    assert resp.status_code == 422

    payload_bad_lon = {
        **VALID_PAYLOAD,
        "birth": {
            **VALID_PAYLOAD["birth"],
            "longitude": -190.0,  # Invalid: < -180
        },
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_bad_lon)
    assert resp.status_code == 422


def test_api_invalid_birth_time_uncertainty():
    """Uncertainty outside [0.0, 1800.0] range must return HTTP 422."""
    payload_neg = {
        **VALID_PAYLOAD,
        "birth_time_uncertainty_seconds": -10.0,
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_neg)
    assert resp.status_code == 422

    payload_excess = {
        **VALID_PAYLOAD,
        "birth_time_uncertainty_seconds": 3600.0,  # > 1800.0
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_excess)
    assert resp.status_code == 422


def test_api_invalid_reversed_timing_range():
    """Reversed timing range (end_year < start_year) must return HTTP 422."""
    payload_reversed = {
        **VALID_PAYLOAD,
        "start_year": 2035,
        "end_year": 2025,
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_reversed)
    assert resp.status_code == 422


# ===========================================================================
# 4. Polar Latitude and Calculation Error Handling
# ===========================================================================

def test_api_polar_latitude_safe_indeterminacy():
    """Polar latitudes (|lat| > 66.0°) safely return INDETERMINATE with SCAN_FAILED_OR_INCOMPLETE."""
    payload_polar = {
        **VALID_PAYLOAD,
        "birth": {
            **VALID_PAYLOAD["birth"],
            "latitude": 71.0,  # Arctic latitude
        },
    }
    resp = client.post("/api/v1/predictions/marriage", json=payload_polar)
    assert resp.status_code == 200
    data = resp.json()
    assert data["final_verdict"] == EventVerdict.INDETERMINATE.value
    assert data["birth_time_sensitivity"]["scan_status"] == ScanStatus.SCAN_FAILED_OR_INCOMPLETE.value
    assert "exceeds Placidus" in (data["birth_time_sensitivity"]["error_detail"] or "")


def test_api_calculation_failure_returns_safe_500():
    """Unexpected internal calculation exception returns safe HTTP 500 without stack trace leaks."""
    with patch(
        "app.services.unified_prediction.engine.UnifiedMarriagePredictionService.predict_marriage_event"
    ) as mock_service:
        mock_service.side_effect = RuntimeError("Simulated internal astronomical solver crash at /var/secrets")
        resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
        assert resp.status_code == 500
        data = resp.json()
        assert "detail" in data
        # Ensure no sensitive internal paths or stack trace details leaked to client
        assert "/var/secrets" not in str(data)
        assert "Traceback" not in str(data)


# ===========================================================================
# 5. Separation of Natal Verdict and Timing Status
# ===========================================================================

def test_api_natal_verdict_preserved_on_timing_calculation_failure():
    """Timing calculation failure must return TIMING_NOT_DETERMINABLE while preserving EVENT_INDICATED."""
    with patch(
        "app.services.unified_prediction.engine.find_marriage_timing_windows"
    ) as mock_timing:
        mock_timing.return_value = (TimingStatus.TIMING_NOT_DETERMINABLE, None)
        with patch(
            "app.services.unified_prediction.engine.evaluate_vedic_marriage_promise"
        ) as mock_vedic:
            mock_vedic.return_value = VedicPromiseDetail(
                verdict=PromiseVerdict.PROMISED,
                internal_modifier=VedicInternalModifier.PROMISED_FAVORABLE,
                seventh_lord_d1="Venus",
                seventh_house_sign_d1="Libra",
                seventh_lord_house_d1=2,
                venus_combustion=False,
                venus_debilitation=False,
                venus_dusthana=False,
                kuja_dosha_present=False,
                kuja_dosha_cancelled=False,
                d9_seventh_sign="Libra",
                d9_seventh_lord="Venus",
                d9_venus_sign="Taurus",
                d9_afflicted=False,
                compound_denial_gates_met=0,
                rule_id="VED-MARR-PROM-001",
                rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                explanation="Favorable",
            )
            with patch(
                "app.services.unified_prediction.engine.evaluate_kp_marriage_promise"
            ) as mock_kp:
                mock_kp.return_value = KPPromiseDetail(
                    verdict=PromiseVerdict.PROMISED,
                    internal_modifier=KPInternalModifier.PROMISED_SMOOTH,
                    cuspal_sub_lord_7="Venus",
                    star_lord_of_csl="Jupiter",
                    star_lord_significations=[2, 7],
                    sub_lord_significations=[7, 11],
                    is_csl_retrograde=False,
                    is_star_lord_retrograde=False,
                    rule_id="KP-MARR-PROM-001",
                    rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
                    explanation="Promised",
                )
                resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
                assert resp.status_code == 200
                data = resp.json()
                assert data["final_verdict"] == EventVerdict.EVENT_INDICATED.value
                assert data["timing_status"] == TimingStatus.TIMING_NOT_DETERMINABLE.value


# ===========================================================================
# 6. Legacy Endpoint Regression Availability Checks
# ===========================================================================

def test_api_regression_existing_endpoints_available():
    """Verify that existing health, metadata, horoscope, and KP prediction endpoints remain available."""
    # Health endpoint
    resp_health = client.get("/health")
    assert resp_health.status_code == 200

    # Metadata endpoint
    resp_meta = client.get("/api/v1/metadata")
    assert resp_meta.status_code == 200

    # KP Prediction events list
    resp_events = client.get("/api/v1/kp-prediction/events")
    assert resp_events.status_code == 200
    assert "events" in resp_events.json()


# ===========================================================================
# 7. Ayanamsa Metadata Integrity & Dual-Tradition Verification
# ===========================================================================

def test_api_ayanamsa_metadata_nonzero_and_accurate():
    """Verify metadata.ayanamsa_deg is nonzero, matches KP Krishnamurti, and Vedic Lahiri is in notes."""
    resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    meta = data["metadata"]

    # 1. Verify ayanamsa_deg is a genuine positive float (not 0.0 or default placeholder)
    assert meta["ayanamsa_deg"] > 0.0
    assert isinstance(meta["ayanamsa_deg"], float)

    # 2. Verify metadata fields adhere to schema contract
    assert meta["ayanamsa_id"] == 1
    assert "Krishnamurti (KP)" in meta["ayanamsa_name"]
    assert "Chitrapaksha Lahiri (Vedic)" in meta["ayanamsa_name"]
    assert meta["engine"] == "XALEN 0.6.0 (Rust) + Unified Prediction Engine"
    assert meta["house_system_name"] == "Placidus (KP) + Whole Sign (Vedic)"

    # 3. Verify numerical accuracy against XALEN directly using returned Julian Day
    birth_jd = meta["julian_day_ut1"]
    assert birth_jd > 2400000.0
    expected_kp = round(float(xalen.ayanamsa(birth_jd, 1)), 6)
    expected_vedic = round(float(xalen.ayanamsa(birth_jd, 0)), 6)

    assert meta["ayanamsa_deg"] == pytest.approx(expected_kp, abs=1e-5)

    # 4. Verify both traditions are documented in notes with exact degrees and IDs
    notes = meta["notes"]
    assert len(notes) >= 3
    kp_notes = [n for n in notes if f"KP Krishnamurti ayanamsa: {expected_kp}° (ID: 1)" in n]
    assert len(kp_notes) == 1, f"Expected KP note not found in: {notes}"

    vedic_notes = [n for n in notes if f"Vedic Chitrapaksha Lahiri ayanamsa: {expected_vedic}° (ID: 0)" in n]
    assert len(vedic_notes) == 1, f"Expected Vedic note not found in: {notes}"

    # 5. Verify KP and Vedic values are distinct and not interchanged
    assert abs(expected_kp - expected_vedic) > 0.05
    assert meta["ayanamsa_deg"] != pytest.approx(expected_vedic, abs=1e-5)

    # 6. Verify core verdict and sensitivity invariance
    assert data["final_verdict"] in [v.value for v in EventVerdict]
    assert data["timing_status"] in [t.value for t in TimingStatus]
    assert data["birth_time_sensitivity"]["tolerance_guarantee"]["time_tolerance_seconds"] == 0.5


def test_api_ayanamsa_metadata_calculation_exception_fallback():
    """Verify that even when house calculation throws an exception, ayanamsa metadata is preserved."""
    with patch("xalen.swe.houses_ex") as mock_houses:
        mock_houses.side_effect = RuntimeError("Simulated Placidus convergence exception")
        resp = client.post("/api/v1/predictions/marriage", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["final_verdict"] == EventVerdict.INDETERMINATE.value
        meta = data["metadata"]
        assert meta["ayanamsa_deg"] > 0.0
        birth_jd = meta["julian_day_ut1"]
        expected_kp = round(float(xalen.ayanamsa(birth_jd, 1)), 6)
        assert meta["ayanamsa_deg"] == pytest.approx(expected_kp, abs=1e-5)
        notes_str = " ".join(meta["notes"])
        assert "Simulated Placidus convergence exception" in notes_str
        assert "KP Krishnamurti ayanamsa:" in notes_str
        assert "Vedic Chitrapaksha Lahiri ayanamsa:" in notes_str

