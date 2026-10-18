"""Integration and security tests for KP Transit Timeline API endpoint.

Tests:
POST /api/v1/horoscope/kp/transit-timeline

Verifies:
1. Authentication enforcement (missing token, invalid token, valid token).
2. Valid requests with default and custom options, Pydantic response schema integrity.
3. Explicit start/end dates and window boundaries.
4. Input validation (invalid dates, timezones, unsupported planets, invalid ayanamsa).
5. Window limits (7 to 30 days) and event-count truncation (max_events).
6. Empty windows and single-planet runs with zero boundary crossings.
7. Malformed payloads and safe 500 error masking (no credential/stack leaks).
8. Mathematical validation via API (0° Aries crossing, retrograde status, DST transition).
9. Regression protection for existing KP endpoints (/kp natal and /kp/horary).
"""

from datetime import date, time
from unittest.mock import patch
import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import get_current_user

client = TestClient(app)

TEST_USER_ID = "33333333-3333-3333-3333-333333333333"
VALID_JWT_TOKEN = jwt.encode(
    {
        "sub": TEST_USER_ID,
        "email": "astrologer@example.com",
        "role": "user",
        "user_metadata": {"username": "astro_user", "display_name": "Astro User"},
    },
    "test-secret",
    algorithm="HS256",
)
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_JWT_TOKEN}"}

VALID_TIMELINE_PAYLOAD = {
    "start_date": "2026-10-18",
    "start_time": "00:00:00",
    "forecast_days": 7,
    "timezone": "Asia/Kolkata",
    "planets": ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"],
    "ayanamsa": 0,
    "max_events": 500,
}


@pytest.fixture(autouse=True)
def authenticate_user():
    """Default authenticated user for endpoint testing."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": TEST_USER_ID,
        "email": "astrologer@example.com",
        "role": "user",
        "username": "astro_user",
    }
    yield
    app.dependency_overrides.clear()


# ===========================================================================
# 1. Authentication Enforcement Tests
# ===========================================================================

def test_transit_timeline_unauthenticated_fails_with_401():
    """Verify that request without Authorization header returns 401 Unauthorized."""
    app.dependency_overrides.clear()
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=VALID_TIMELINE_PAYLOAD)
    assert response.status_code == 401
    assert "token required" in response.json()["detail"].lower()
    assert response.headers.get("www-authenticate") == "Bearer"


def test_transit_timeline_malformed_token_fails_with_401():
    """Verify that request with malformed Bearer token returns 401 Unauthorized."""
    app.dependency_overrides.clear()
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=VALID_TIMELINE_PAYLOAD,
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert response.status_code == 401


def test_transit_timeline_valid_auth_succeeds_with_200():
    """Verify that request with valid authenticated user returns 200 OK."""
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=VALID_TIMELINE_PAYLOAD,
    )
    assert response.status_code == 200


# ===========================================================================
# 2. Valid Requests and Response Schema Tests
# ===========================================================================

def test_transit_timeline_default_payload_and_schema():
    """Verify default request options and full response schema conformity."""
    payload = {
        "start_date": "2026-10-18",
        "timezone": "Asia/Kolkata",
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()

    # Metadata checks
    assert data["start_time_utc"] == "2026-10-17T18:30:00Z"
    assert "+05:30" in data["start_time_local"]
    assert "Z" in data["end_time_utc"]
    assert data["timezone"] == "Asia/Kolkata"
    assert data["utc_offset_hours"] == 5.5
    assert data["ayanamsa_id"] == 0
    assert data["ayanamsa_name"] == "Lahiri"
    assert data["forecast_days"] == 7.0
    assert data["planets_analyzed"] == ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"]
    assert data["truncated"] is False
    assert data["total_events"] > 0
    assert len(data["events"]) == data["total_events"]

    # Benchmark stats
    bench = data["benchmark_stats"]
    assert bench is not None
    assert bench["duration_ms"] > 0.0
    assert bench["total_evaluations"] > 0
    assert bench["step_evaluations"] > 0
    assert bench["bisection_evaluations"] > 0

    # Event fields and chronological ordering
    events = data["events"]
    for i in range(len(events)):
        ev = events[i]
        assert ev["planet"] in data["planets_analyzed"]
        assert isinstance(ev["planet_id"], int)
        assert ev["utc_datetime"].endswith("Z")
        assert "+05:30" in ev["local_datetime"]
        assert ev["jd"] > 2460000.0
        assert ev["boundary_type"] in ("rashi", "nakshatra", "sub_lord")
        assert 0.0 <= ev["boundary_longitude"] < 360.0
        assert isinstance(ev["is_retrograde"], bool)
        assert isinstance(ev["speed_deg_per_day"], float)
        assert 1 <= ev["from_kp_number"] <= 249
        assert 1 <= ev["to_kp_number"] <= 249
        assert ev["calculation_precision_seconds"] <= 0.5

        if i > 0:
            assert ev["jd"] >= events[i - 1]["jd"]


def test_transit_timeline_kp_ayanamsa_and_single_planet():
    """Verify request with KP Ayanamsa (1) and Moon only."""
    payload = {
        "start_date": "2026-10-18",
        "start_time": "12:00:00",
        "forecast_days": 10,
        "timezone": "UTC",
        "planets": ["Moon"],
        "ayanamsa": 1,
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ayanamsa_name"] == "KP"
    assert data["ayanamsa_id"] == 1
    assert data["forecast_days"] == 10.0
    assert data["planets_analyzed"] == ["Moon"]
    assert all(e["planet"] == "Moon" for e in data["events"])


def test_transit_timeline_explicit_start_and_end_date():
    """Verify window defined by explicit start_date and end_date."""
    payload = {
        "start_date": "2026-10-18",
        "start_time": "06:00:00",
        "end_date": "2026-10-26",
        "end_time": "06:00:00",
        "timezone": "UTC",
        "planets": ["Sun"],
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_days"] == 8.0
    assert data["start_time_utc"] == "2026-10-18T06:00:00Z"
    assert data["end_time_utc"] == "2026-10-26T06:00:00Z"


# ===========================================================================
# 3. Input Validation Tests (Invalid Dates, Timezones, Planets, Date Ranges)
# ===========================================================================

def test_transit_timeline_invalid_date_format():
    """Verify that invalid date formats return 422 Unprocessable Entity."""
    payload = {**VALID_TIMELINE_PAYLOAD, "start_date": "not-a-date"}
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422


def test_transit_timeline_invalid_timezone():
    """Verify that invalid timezone names return 422 Unprocessable Entity."""
    payload = {**VALID_TIMELINE_PAYLOAD, "timezone": "Fantasy/Zone"}
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    assert "invalid timezone" in response.text.lower()


def test_transit_timeline_unsupported_planet():
    """Verify that unsupported planets return 422 Unprocessable Entity."""
    payload = {**VALID_TIMELINE_PAYLOAD, "planets": ["Moon", "Krypton"]}
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    assert "unsupported planet" in response.text.lower()


def test_transit_timeline_empty_planets_list():
    """Verify that empty planets list returns 422 Unprocessable Entity."""
    payload = {**VALID_TIMELINE_PAYLOAD, "planets": []}
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    assert "planets list cannot be empty" in response.text.lower()


def test_transit_timeline_inverted_date_range():
    """Verify that end_date earlier than start_date returns 422 Unprocessable Entity."""
    payload = {
        **VALID_TIMELINE_PAYLOAD,
        "start_date": "2026-10-25",
        "end_date": "2026-10-18",
    }
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    assert "earlier than start_date" in response.text.lower()


def test_transit_timeline_invalid_ayanamsa():
    """Verify that ayanamsa outside 0 or 1 returns 422 Unprocessable Entity."""
    payload = {**VALID_TIMELINE_PAYLOAD, "ayanamsa": 99}
    response = client.post("/api/v1/horoscope/kp/transit-timeline", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    assert "ayanamsa must be 0" in response.text.lower()


# ===========================================================================
# 4. Window and Event-Count Limits Tests
# ===========================================================================

def test_transit_timeline_window_below_minimum():
    """Verify that window < 7 days returns 422 Unprocessable Entity."""
    # Via forecast_days
    res1 = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={**VALID_TIMELINE_PAYLOAD, "forecast_days": 6},
        headers=AUTH_HEADERS,
    )
    assert res1.status_code == 422

    # Via end_date (3 days)
    res2 = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={
            **VALID_TIMELINE_PAYLOAD,
            "start_date": "2026-10-18",
            "end_date": "2026-10-21",
            "forecast_days": None,
        },
        headers=AUTH_HEADERS,
    )
    assert res2.status_code == 422
    assert "between 7 and 30 days" in res2.text.lower()


def test_transit_timeline_window_above_maximum():
    """Verify that window > 30 days returns 422 Unprocessable Entity."""
    # Via forecast_days
    res1 = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={**VALID_TIMELINE_PAYLOAD, "forecast_days": 31},
        headers=AUTH_HEADERS,
    )
    assert res1.status_code == 422

    # Via end_date (40 days)
    res2 = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={
            **VALID_TIMELINE_PAYLOAD,
            "start_date": "2026-10-18",
            "end_date": "2026-11-27",
            "forecast_days": None,
        },
        headers=AUTH_HEADERS,
    )
    assert res2.status_code == 422
    assert "between 7 and 30 days" in res2.text.lower()


def test_transit_timeline_event_truncation():
    """Verify max_events limits returned events and sets truncated=True."""
    payload = {
        "start_date": "2026-10-18",
        "forecast_days": 7,
        "planets": ["Moon"],
        "max_events": 10,
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 10
    assert len(data["events"]) == 10
    assert data["truncated"] is True


def test_transit_timeline_invalid_max_events():
    """Verify that max_events < 1 or > 1000 returns 422."""
    res_zero = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={**VALID_TIMELINE_PAYLOAD, "max_events": 0},
        headers=AUTH_HEADERS,
    )
    assert res_zero.status_code == 422

    res_excess = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={**VALID_TIMELINE_PAYLOAD, "max_events": 1001},
        headers=AUTH_HEADERS,
    )
    assert res_excess.status_code == 422


# ===========================================================================
# 5. Empty Windows and Boundary Crossings Tests
# ===========================================================================

def test_transit_timeline_empty_boundary_crossings():
    """Verify that a slow-moving planet with no boundary crossing returns an empty events list."""
    # Jupiter does not cross any KP sub-division boundary between 2026-10-18 and 2026-10-25
    payload = {
        "start_date": "2026-10-18",
        "forecast_days": 7,
        "planets": ["Jupiter"],
        "timezone": "UTC",
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 0
    assert data["events"] == []
    assert data["truncated"] is False


# ===========================================================================
# 6. Malformed Payloads and Internal Server Error Masking
# ===========================================================================

def test_transit_timeline_missing_required_fields():
    """Verify that omitting start_date returns 422."""
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json={"timezone": "UTC"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 422


def test_transit_timeline_internal_error_masking():
    """Verify that unexpected service errors return sanitized 500 without leaking stack traces."""
    with patch(
        "app.routers.kp.compute_transit_timeline",
        side_effect=RuntimeError("Simulated internal database/ephemeris explosion with secrets=XYZ123"),
    ):
        response = client.post(
            "/api/v1/horoscope/kp/transit-timeline",
            json=VALID_TIMELINE_PAYLOAD,
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "KP Transit Timeline calculation failed."
        # Confirm internal secrets and tracebacks are never exposed
        assert "XYZ123" not in response.text
        assert "Traceback" not in response.text


# ===========================================================================
# 7. Mathematical Validation via API (Wraparound, Retrograde, DST)
# ===========================================================================

def test_api_zero_degree_aries_wraparound():
    """Verify that the 0° Aries / Pisces Revati circular boundary is cleanly returned via the API."""
    payload = {
        "start_date": "2026-10-18",
        "forecast_days": 10,
        "planets": ["Moon"],
        "timezone": "UTC",
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    aries_crossings = [
        e for e in data["events"]
        if e["from_kp_number"] == 249 and e["to_kp_number"] == 1
    ]
    assert len(aries_crossings) == 1
    cross = aries_crossings[0]
    assert cross["boundary_longitude"] == 0.0
    assert cross["boundary_type"] == "rashi"
    assert cross["from_sign"] == "Pisces"
    assert cross["to_sign"] == "Aries"
    assert cross["from_sign_lord"] == "Jupiter"
    assert cross["to_sign_lord"] == "Mars"
    assert cross["from_star_lord"] == "Mercury"
    assert cross["to_star_lord"] == "Ketu"
    assert cross["from_sub_lord"] == "Saturn"
    assert cross["to_sub_lord"] == "Ketu"


def test_api_retrograde_planets_division_decrement():
    """Verify that retrograde planets (Venus, Saturn, Rahu) have descending KP division numbers."""
    payload = {
        "start_date": "2026-10-18",
        "forecast_days": 30,
        "planets": ["Venus", "Saturn", "Rahu"],
        "timezone": "UTC",
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    events = data["events"]
    assert len(events) >= 8

    for ev in events:
        assert ev["is_retrograde"] is True
        assert ev["speed_deg_per_day"] < 0.0
        # In retrograde, from_kp_number > to_kp_number (unless 1 -> 249 wrap)
        if not (ev["from_kp_number"] == 1 and ev["to_kp_number"] == 249):
            assert ev["to_kp_number"] == ev["from_kp_number"] - 1


def test_api_dst_timezone_transition():
    """Verify America/New_York DST fallback (-04:00 to -05:00) is accurately reflected in local_datetime."""
    payload = {
        "start_date": "2026-10-28",
        "forecast_days": 7,
        "planets": ["Moon"],
        "timezone": "America/New_York",
    }
    response = client.post(
        "/api/v1/horoscope/kp/transit-timeline",
        json=payload,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert "-04:00" in data["start_time_local"]
    assert "-05:00" in data["end_time_local"]

    # First event is in EDT (-04:00), last event is in EST (-05:00)
    assert "-04:00" in data["events"][0]["local_datetime"]
    assert "-05:00" in data["events"][-1]["local_datetime"]


# ===========================================================================
# 8. Regression Protection for Existing KP Endpoints
# ===========================================================================

def test_regression_existing_kp_natal_endpoint():
    """Verify POST /api/v1/horoscope/kp still works without auth and returns complete chart."""
    natal_payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 1,
        "house_system": 2,
    }
    response = client.post("/api/v1/horoscope/kp", json=natal_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["planetary_positions"]) == 9
    assert len(data["cuspal_analysis"]) == 12
    assert len(data["significators"]) == 9
    assert "dasa_hierarchy" in data


def test_regression_existing_kp_horary_endpoint():
    """Verify POST /api/v1/horoscope/kp/horary still works without auth and returns valid horary chart."""
    horary_payload = {
        "horary_number": 108,
        "question_text": "Will I complete Phase 2 successfully?",
        "question_date": "2026-10-18",
        "question_time": "16:00:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 1,
        "house_system": 2,
    }
    response = client.post("/api/v1/horoscope/kp/horary", json=horary_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["horary_number"] == 108
    assert data["horary_division"]["number"] == 108
