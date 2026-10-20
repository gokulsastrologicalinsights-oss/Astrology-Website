"""Unit and Integration Tests for Marriage Compatibility Report Persistence (Phase 11C).

Tests:
1. Save report with sequential display_number assignment (1, 2, ...).
2. List reports newest first (display_number desc) with pagination (limit, offset).
3. Get report by ID with full calculation snapshot.
4. Update permitted metadata only (title, groom_name, bride_name, groom_saved_horoscope_id, bride_saved_horoscope_id).
5. Reject attempted modification of immutable calculation fields (overall_outcome, report_data, porutham_score, etc.).
6. Cross-user isolation: User B cannot view, update, or delete User A's report.
7. Cross-user linked-horoscope rejection on save: User A cannot link a horoscope owned by User B.
8. Cross-user linked-horoscope rejection on update: User A cannot patch a horoscope owned by User B.
9. Delete report and confirm subsequent GET returns 404.
10. Unauthenticated access rejection (HTTP 401).
11. Admin access: Admin can list all users' reports when requested.
12. Malformed UUID validation (HTTP 400).
13. Empty or invalid metadata validation (HTTP 422).
14. Both /saved and /reports endpoint aliases.
15. Offline in-memory fallback when database client is unavailable.
"""

from __future__ import annotations
import copy
import uuid
from typing import Any, Dict, List, Optional
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import get_current_user
from app.services.marriage_engine.report_repository import (
    clear_local_storage,
    _LOCAL_SAVED_HOROSCOPES,
    _LOCAL_SAVED_MARRIAGE_REPORTS,
)

client = TestClient(app)

USER_A_ID = "11111111-1111-1111-1111-111111111111"
USER_B_ID = "22222222-2222-2222-2222-222222222222"
ADMIN_USER_ID = "99999999-9999-9999-9999-999999999999"

HOROSCOPE_USER_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
HOROSCOPE_USER_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

MOCK_USER_A = {
    "id": USER_A_ID,
    "email": "user.a@example.com",
    "role": "authenticated",
}

MOCK_USER_B = {
    "id": USER_B_ID,
    "email": "user.b@example.com",
    "role": "authenticated",
}

MOCK_ADMIN = {
    "id": ADMIN_USER_ID,
    "email": "admin@example.com",
    "role": "admin",
}

SAMPLE_REPORT_PAYLOAD = {
    "title": "Karthik & Revathi Vivaha Porutham",
    "groom_name": "Karthik",
    "bride_name": "Revathi",
    "groom_birth_date": "1992-04-14",
    "bride_birth_date": "1994-08-20",
    "groom_is_approximate": False,
    "bride_is_approximate": False,
    "rule_system": "all",
    "ayanamsa_id": 0,
    "house_system_id": 0,
    "include_kp": True,
    "include_timing": True,
    "overall_outcome": "FAVOURABLE_UNDER_SELECTED_RULES",
    "porutham_score": 7.5,
    "ashtakoota_points": 24.5,
    "samadosham_status": "BALANCED",
    "papasamya_verdict": "FAVORABLE",
    "ruling_planets_agreement": "Positive",
    "report_data": {
        "overall_outcome": "FAVOURABLE_UNDER_SELECTED_RULES",
        "composite_assessment": {"decision": "Approved"},
        "tamil_porutham": {"total_score": 7.5},
        "ashtakoota": {"total_points": 24.5},
    },
    "engine_version": "1.0.0",
    "report_schema_version": "1.0.0",
}


class MockTableQuery:
    """Mock query builder for PostgREST / Supabase Python client."""

    def __init__(self, table_name: str, db_state: Dict[str, List[Dict[str, Any]]]):
        self.table_name = table_name
        self.db_state = db_state
        self.filters: List[tuple[str, Any]] = []
        self._action = "select"
        self._insert_data: Optional[Dict[str, Any]] = None
        self._update_data: Optional[Dict[str, Any]] = None
        self._order_field: Optional[str] = None
        self._order_desc: bool = False
        self._range_start: int = 0
        self._range_end: Optional[int] = None

    def select(self, *args, **kwargs) -> MockTableQuery:
        self._action = "select"
        return self

    def insert(self, data: Dict[str, Any], *args, **kwargs) -> MockTableQuery:
        self._action = "insert"
        self._insert_data = data
        return self

    def update(self, data: Dict[str, Any], *args, **kwargs) -> MockTableQuery:
        self._action = "update"
        self._update_data = data
        return self

    def delete(self, *args, **kwargs) -> MockTableQuery:
        self._action = "delete"
        return self

    def eq(self, field: str, value: Any) -> MockTableQuery:
        self.filters.append((field, value))
        return self

    def order(self, field: str, desc: bool = False) -> MockTableQuery:
        self._order_field = field
        self._order_desc = desc
        return self

    def range(self, start: int, end: int) -> MockTableQuery:
        self._range_start = start
        self._range_end = end
        return self

    def execute(self) -> MagicMock:
        records = self.db_state.setdefault(self.table_name, [])

        if self._action == "insert":
            rec = dict(self._insert_data)
            if "id" not in rec or not rec["id"]:
                rec["id"] = str(uuid.uuid4())
            if "display_number" not in rec or rec["display_number"] is None:
                user_recs = [r for r in records if str(r.get("user_id")) == str(rec.get("user_id"))]
                max_disp = max([r.get("display_number", 0) for r in user_recs], default=0)
                rec["display_number"] = max_disp + 1
            rec.setdefault("created_at", "2026-10-19T12:00:00Z")
            rec.setdefault("updated_at", "2026-10-19T12:00:00Z")
            records.append(rec)
            return MagicMock(data=[dict(rec)])

        # Apply eq filters
        matched = list(records)
        for field, val in self.filters:
            matched = [r for r in matched if str(r.get(field)) == str(val)]

        if self._action == "select":
            if self._order_field:
                matched.sort(
                    key=lambda r: r.get(self._order_field, 0),
                    reverse=self._order_desc,
                )
            if self._range_end is not None:
                matched = matched[self._range_start : self._range_end + 1]
            return MagicMock(data=[dict(r) for r in matched])

        elif self._action == "update":
            updated_list = []
            for r in matched:
                if self._update_data:
                    r.update(self._update_data)
                updated_list.append(dict(r))
            return MagicMock(data=updated_list)

        elif self._action == "delete":
            deleted_list = []
            for r in matched:
                if r in records:
                    records.remove(r)
                    deleted_list.append(dict(r))
            return MagicMock(data=deleted_list)

        return MagicMock(data=[])


class MockSupabaseClient:
    """Mock Supabase client providing isolated table storage for tests."""

    def __init__(self, db_state: Dict[str, List[Dict[str, Any]]]):
        self.db_state = db_state

    def table(self, table_name: str) -> MockTableQuery:
        return MockTableQuery(table_name, self.db_state)


@pytest.fixture(autouse=True)
def mock_supabase_env():
    """Patches get_supabase_client to use a clean in-memory MockSupabaseClient for every test."""
    db_state: Dict[str, List[Dict[str, Any]]] = {
        "saved_horoscopes": [
            {
                "id": HOROSCOPE_USER_A,
                "user_id": USER_A_ID,
                "person_name": "Karthik",
            },
            {
                "id": HOROSCOPE_USER_B,
                "user_id": USER_B_ID,
                "person_name": "Foreign Partner",
            },
        ],
        "saved_marriage_compatibility_reports": [],
    }

    mock_client = MockSupabaseClient(db_state)

    clear_local_storage()
    _LOCAL_SAVED_HOROSCOPES[HOROSCOPE_USER_A] = {
        "id": HOROSCOPE_USER_A,
        "user_id": USER_A_ID,
        "person_name": "Karthik",
    }
    _LOCAL_SAVED_HOROSCOPES[HOROSCOPE_USER_B] = {
        "id": HOROSCOPE_USER_B,
        "user_id": USER_B_ID,
        "person_name": "Foreign Partner",
    }

    with patch("app.services.marriage_engine.report_repository.get_supabase_client", return_value=mock_client):
        yield mock_client

    clear_local_storage()
    app.dependency_overrides.clear()


# ===========================================================================
# 1. Unauthenticated Access Rejection
# ===========================================================================

def test_01_unauthenticated_requests_rejected():
    """All persistence endpoints must return 401 when no auth token is provided."""
    resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    assert resp.status_code == 401

    resp = client.get("/api/marriage-compatibility/saved")
    assert resp.status_code == 401

    resp = client.get(f"/api/marriage-compatibility/saved/{USER_A_ID}")
    assert resp.status_code == 401

    resp = client.patch(f"/api/marriage-compatibility/saved/{USER_A_ID}", json={"title": "New"})
    assert resp.status_code == 401

    resp = client.delete(f"/api/marriage-compatibility/saved/{USER_A_ID}")
    assert resp.status_code == 401


# ===========================================================================
# 2. Successful Save & Sequential Display Numbering
# ===========================================================================

def test_02_save_report_and_sequential_display_numbering():
    """Saving reports for the same user assigns incrementing sequential display_numbers."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    # Save first report
    resp1 = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    assert resp1.status_code == 201, resp1.text
    data1 = resp1.json()
    assert data1["display_number"] == 1
    assert data1["user_id"] == USER_A_ID
    assert data1["title"] == "Karthik & Revathi Vivaha Porutham"
    assert data1["overall_outcome"] == "FAVOURABLE_UNDER_SELECTED_RULES"
    assert data1["report_data"]["tamil_porutham"]["total_score"] == 7.5
    assert "id" in data1
    assert "created_at" in data1

    # Save second report for same user
    payload2 = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    payload2["title"] = "Second Match Assessment"
    resp2 = client.post("/api/marriage-compatibility/saved", json=payload2)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["display_number"] == 2
    assert data2["id"] != data1["id"]

    # Save report for User B - starts at display_number 1 for User B
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_B
    resp_b = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    assert resp_b.status_code == 201
    data_b = resp_b.json()
    assert data_b["display_number"] == 1
    assert data_b["user_id"] == USER_B_ID


# ===========================================================================
# 3. Listing Reports Newest First with Pagination
# ===========================================================================

def test_03_list_reports_newest_first_and_pagination():
    """Listing reports orders by display_number descending and supports limit/offset."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    # Create 3 reports for User A
    for i in range(1, 4):
        p = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
        p["title"] = f"Report #{i}"
        client.post("/api/marriage-compatibility/saved", json=p)

    # List all
    resp = client.get("/api/marriage-compatibility/saved")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 3
    reports = data["reports"]
    assert len(reports) == 3
    # Newest first: display_number 3, 2, 1
    assert reports[0]["display_number"] == 3
    assert reports[1]["display_number"] == 2
    assert reports[2]["display_number"] == 1

    # Pagination: limit=2, offset=0
    resp_page1 = client.get("/api/marriage-compatibility/saved?limit=2&offset=0")
    assert resp_page1.status_code == 200
    assert len(resp_page1.json()["reports"]) == 2
    assert resp_page1.json()["reports"][0]["display_number"] == 3

    # Pagination: limit=2, offset=2
    resp_page2 = client.get("/api/marriage-compatibility/saved?limit=2&offset=2")
    assert resp_page2.status_code == 200
    assert len(resp_page2.json()["reports"]) == 1
    assert resp_page2.json()["reports"][0]["display_number"] == 1


# ===========================================================================
# 4. Get Report by ID with Full Snapshot
# ===========================================================================

def test_04_get_report_by_id_includes_full_snapshot():
    """Fetching a saved report by ID returns the full calculation snapshot."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    get_resp = client.get(f"/api/marriage-compatibility/saved/{report_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == report_id
    assert data["report_data"] == SAMPLE_REPORT_PAYLOAD["report_data"]
    assert data["porutham_score"] == 7.5
    assert data["ashtakoota_points"] == 24.5


# ===========================================================================
# 5. Update Permitted Metadata Only
# ===========================================================================

def test_05_update_permitted_metadata():
    """Updating permitted metadata fields (title, names, horoscope IDs) succeeds."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    update_payload = {
        "title": "Updated Auspicious Match Title",
        "groom_name": "Karthikeyan G",
        "bride_name": "Revathi S",
        "groom_saved_horoscope_id": HOROSCOPE_USER_A,
    }

    patch_resp = client.patch(f"/api/marriage-compatibility/saved/{report_id}", json=update_payload)
    assert patch_resp.status_code == 200, patch_resp.text
    data = patch_resp.json()
    assert data["title"] == "Updated Auspicious Match Title"
    assert data["groom_name"] == "Karthikeyan G"
    assert data["bride_name"] == "Revathi S"
    assert data["groom_saved_horoscope_id"] == HOROSCOPE_USER_A
    # Calculation outcomes remain unchanged
    assert data["overall_outcome"] == "FAVOURABLE_UNDER_SELECTED_RULES"
    assert data["display_number"] == 1


# ===========================================================================
# 6. Reject Attempted Modification of Immutable Fields
# ===========================================================================

def test_06_reject_update_of_immutable_fields():
    """Submitting changes to calculation parameters, outcomes, or snapshot must be rejected."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    # Attempting to mutate overall_outcome
    resp = client.patch(
        f"/api/marriage-compatibility/saved/{report_id}",
        json={"overall_outcome": "UNFAVOURABLE_UNDER_SELECTED_RULES"},
    )
    assert resp.status_code in (400, 422)

    # Attempting to mutate report_data snapshot
    resp = client.patch(
        f"/api/marriage-compatibility/saved/{report_id}",
        json={"report_data": {"fake": "score"}},
    )
    assert resp.status_code in (400, 422)

    # Attempting to mutate display_number or user_id
    resp = client.patch(
        f"/api/marriage-compatibility/saved/{report_id}",
        json={"display_number": 999, "user_id": USER_B_ID},
    )
    assert resp.status_code in (400, 422)


# ===========================================================================
# 7. Cross-User Isolation (User B cannot access User A's report)
# ===========================================================================

def test_07_cross_user_isolation():
    """User B cannot view, update, or delete User A's saved report."""
    # User A creates a report
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A
    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    # Switch to User B
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_B

    # User B attempts GET
    resp = client.get(f"/api/marriage-compatibility/saved/{report_id}")
    assert resp.status_code == 404
    assert "not found or unauthorized" in resp.json()["detail"].lower()

    # User B attempts PATCH
    resp = client.patch(f"/api/marriage-compatibility/saved/{report_id}", json={"title": "Hacked"})
    assert resp.status_code == 404

    # User B attempts DELETE
    resp = client.delete(f"/api/marriage-compatibility/saved/{report_id}")
    assert resp.status_code == 404

    # Confirm report still exists untouched under User A
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A
    resp = client.get(f"/api/marriage-compatibility/saved/{report_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == SAMPLE_REPORT_PAYLOAD["title"]


# ===========================================================================
# 8. Cross-User Linked-Horoscope Rejection on Save
# ===========================================================================

def test_08_cross_user_linked_horoscope_rejected_on_save():
    """User A cannot save a report referencing a horoscope owned by User B."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    payload = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    # Reference User B's horoscope as groom
    payload["groom_saved_horoscope_id"] = HOROSCOPE_USER_B

    resp = client.post("/api/marriage-compatibility/saved", json=payload)
    assert resp.status_code == 403
    assert "Unauthorized" in resp.json()["detail"]


# ===========================================================================
# 9. Cross-User Linked-Horoscope Rejection on Update
# ===========================================================================

def test_09_cross_user_linked_horoscope_rejected_on_update():
    """User A cannot patch a report to link to User B's horoscope."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    resp = client.patch(
        f"/api/marriage-compatibility/saved/{report_id}",
        json={"bride_saved_horoscope_id": HOROSCOPE_USER_B},
    )
    assert resp.status_code == 403
    assert "Unauthorized" in resp.json()["detail"]


# ===========================================================================
# 10. Delete Report Lifecycle
# ===========================================================================

def test_10_delete_report_lifecycle():
    """Deleting a report succeeds and ensures it can no longer be retrieved."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    save_resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
    report_id = save_resp.json()["id"]

    # Delete report
    del_resp = client.delete(f"/api/marriage-compatibility/saved/{report_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Subsequent GET returns 404
    get_resp = client.get(f"/api/marriage-compatibility/saved/{report_id}")
    assert get_resp.status_code == 404

    # Subsequent DELETE returns 404
    del_resp2 = client.delete(f"/api/marriage-compatibility/saved/{report_id}")
    assert del_resp2.status_code == 404


# ===========================================================================
# 11. Admin Access
# ===========================================================================

def test_11_admin_can_view_all_reports():
    """Admin user can list reports across all users when all_users=True is specified."""
    # User A creates a report
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A
    client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)

    # User B creates a report
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_B
    p_b = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    p_b["title"] = "User B Report"
    client.post("/api/marriage-compatibility/saved", json=p_b)

    # Admin lists with all_users=True
    app.dependency_overrides[get_current_user] = lambda: MOCK_ADMIN
    admin_resp = client.get("/api/marriage-compatibility/saved?all_users=true")
    assert admin_resp.status_code == 200
    assert admin_resp.json()["total_count"] == 2


# ===========================================================================
# 12. Input Validations (Empty title/names, bad outcome, bad UUID)
# ===========================================================================

def test_12_input_validations():
    """Invalid input payloads return appropriate 400/422 status codes."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    # Empty title
    bad_payload = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    bad_payload["title"] = "   "
    resp = client.post("/api/marriage-compatibility/saved", json=bad_payload)
    assert resp.status_code == 422

    # Invalid overall_outcome
    bad_payload = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    bad_payload["overall_outcome"] = "SUPER_GOOD"
    resp = client.post("/api/marriage-compatibility/saved", json=bad_payload)
    assert resp.status_code == 422

    # Invalid UUID for report_id
    resp = client.get("/api/marriage-compatibility/saved/not-a-uuid")
    assert resp.status_code == 400

    # Invalid UUID for horoscope reference
    bad_payload = copy.deepcopy(SAMPLE_REPORT_PAYLOAD)
    bad_payload["groom_saved_horoscope_id"] = "not-a-uuid"
    resp = client.post("/api/marriage-compatibility/saved", json=bad_payload)
    assert resp.status_code == 422


# ===========================================================================
# 13. Endpoint Aliases (/reports behaves identically to /saved)
# ===========================================================================

def test_13_reports_endpoint_aliases():
    """The /reports endpoint aliases work identically to /saved."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

    # Save via /reports
    resp = client.post("/api/marriage-compatibility/reports", json=SAMPLE_REPORT_PAYLOAD)
    assert resp.status_code == 201
    rep_id = resp.json()["id"]

    # List via /reports
    list_resp = client.get("/api/marriage-compatibility/reports")
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] == 1

    # Get via /reports/{id}
    get_resp = client.get(f"/api/marriage-compatibility/reports/{rep_id}")
    assert get_resp.status_code == 200

    # Patch via /reports/{id}
    patch_resp = client.patch(f"/api/marriage-compatibility/reports/{rep_id}", json={"title": "Alias Title"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Alias Title"

    # Delete via /reports/{id}
    del_resp = client.delete(f"/api/marriage-compatibility/reports/{rep_id}")
    assert del_resp.status_code == 200


# ===========================================================================
# 14. Offline In-Memory Fallback Test
# ===========================================================================

def test_14_offline_in_memory_fallback():
    """Verify in-memory fallback works seamlessly when Supabase client returns None."""
    with patch("app.services.marriage_engine.report_repository.get_supabase_client", return_value=None):
        app.dependency_overrides[get_current_user] = lambda: MOCK_USER_A

        # Save offline
        resp = client.post("/api/marriage-compatibility/saved", json=SAMPLE_REPORT_PAYLOAD)
        assert resp.status_code == 201
        offline_id = resp.json()["id"]
        assert resp.json()["display_number"] == 1

        # List offline
        list_resp = client.get("/api/marriage-compatibility/saved")
        assert list_resp.status_code == 200
        assert list_resp.json()["total_count"] == 1

        # Get offline
        get_resp = client.get(f"/api/marriage-compatibility/saved/{offline_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == SAMPLE_REPORT_PAYLOAD["title"]

        # Patch offline
        patch_resp = client.patch(
            f"/api/marriage-compatibility/saved/{offline_id}",
            json={"title": "Offline Updated Title"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["title"] == "Offline Updated Title"

        # Delete offline
        del_resp = client.delete(f"/api/marriage-compatibility/saved/{offline_id}")
        assert del_resp.status_code == 200

        # Verify 404 after delete
        assert client.get(f"/api/marriage-compatibility/saved/{offline_id}").status_code == 404
