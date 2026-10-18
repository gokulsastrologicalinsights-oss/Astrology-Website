"""Automated Unit & Integration Tests for Vastu Service and Endpoints.

Covers:
- Direction azimuth sequence & Kinvastu interleaving bug resolution.
- Multi-factor evaluation across all 4 property profiles.
- Score normalization with missing/unassessed inputs.
- Classical Dosha detection & traditional remedies.
- 32 Outer Pada Deities metadata.
- Astro-Vastu native overlay.
- FastAPI endpoints, validation rules, authentication, and persistence CRUD.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.vastu_service import (
    azimuth_to_direction,
    azimuth_to_pada,
    lookup_pada,
    get_all_directions_metadata,
    evaluate_vastu_layout,
    DIRECTIONS_16_CONFIG,
    PADAS_32_CONFIG,
    save_vastu_report,
    list_vastu_reports,
    get_vastu_report,
    delete_vastu_report,
)
from app.schemas.vastu import (
    VastuEvaluationRequest,
    RoomPlacementsInput,
    SaveVastuReportRequest,
)
from app.services.auth_service import get_current_user

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. Direction Azimuth & Geometry Tests (Resolving Kinvastu Bug)
# ------------------------------------------------------------------------------

def test_16_directions_clockwise_azimuth_order():
    """Verify that the 16 directions are arranged strictly in clockwise azimuth order.
    Kinvastu's critical bug of placing ENE after East is completely resolved.
    """
    codes = [d["code"] for d in DIRECTIONS_16_CONFIG]
    expected_order = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    assert codes == expected_order, f"Direction sequence mismatch: {codes}"

    # Verify center degrees increase monotonically clockwise
    centers = [d["center_degree"] for d in DIRECTIONS_16_CONFIG]
    for i in range(len(centers) - 1):
        assert centers[i] < centers[i + 1], f"Non-monotonic azimuth at index {i}: {centers}"


def test_azimuth_to_direction_boundaries():
    """Test boundary and midpoint conversions from degrees to direction code."""
    # North around 0°
    assert azimuth_to_direction(0.0) == "N"
    assert azimuth_to_direction(359.5) == "N"
    assert azimuth_to_direction(5.0) == "N"
    assert azimuth_to_direction(348.8) == "N"

    # NNE boundary (11.25° to 33.75°)
    assert azimuth_to_direction(11.26) == "NNE"
    assert azimuth_to_direction(22.5) == "NNE"
    assert azimuth_to_direction(33.74) == "NNE"

    # NE (33.75° to 56.25°)
    assert azimuth_to_direction(45.0) == "NE"

    # East (78.75° to 101.25°)
    assert azimuth_to_direction(90.0) == "E"

    # South (168.75° to 191.25°)
    assert azimuth_to_direction(180.0) == "S"

    # West (258.75° to 281.25°)
    assert azimuth_to_direction(270.0) == "W"


def test_32_outer_padas_integrity():
    """Verify all 32 outer padas exist with valid sides and auspicious/neutral/inauspicious classifications."""
    assert len(PADAS_32_CONFIG) == 32
    sides = [p["direction_side"] for p in PADAS_32_CONFIG]
    assert sides.count("North") == 8
    assert sides.count("East") == 8
    assert sides.count("South") == 8
    assert sides.count("West") == 8

    # Auspicious gates check
    names = [p["sanskrit_name"].split(" ")[0].lower() for p in PADAS_32_CONFIG]
    assert "mukhya" in names
    assert "bhallāṭa" in names
    assert "jayanta" in names
    assert "indra" in names
    assert "gṛhakṣata" in names
    assert "puṣpadanta" in names
    assert "varuṇa" in names


# ------------------------------------------------------------------------------
# 2. Multi-Factor Evaluation & Normalization Tests
# ------------------------------------------------------------------------------

def test_residential_ideal_evaluation():
    """Test a property with ideal placements achieves high score and no critical Doshas."""
    req = VastuEvaluationRequest(
        property_name="Vaikuntha Villa",
        property_type="residential",
        facing_direction="E",
        placements=RoomPlacementsInput(
            main_entrance_direction="E",
            kitchen_direction="SE",
            master_bedroom_direction="SW",
            pooja_room_direction="NE",
            toilet_directions=["WNW"],
            brahmasthan_status="clear",
            plot_shape="square",
        ),
    )
    res = evaluate_vastu_layout(req)
    assert res.compliance_score is not None
    assert res.compliance_score >= 85
    assert "A+" in res.score_grade
    assert len(res.doshas) == 0
    assert res.factors_assessed == 7
    assert len(res.disclaimer) > 50


def test_score_normalization_with_partial_inputs():
    """Ensure missing inputs do NOT artificially penalize the score.
    Score is normalized strictly across assessed factors.
    """
    # Only entrance (E = ideal, max 25) and kitchen (SE = ideal, max 20) provided
    req = VastuEvaluationRequest(
        property_name="Partial House",
        property_type="residential",
        facing_direction="N",
        placements=RoomPlacementsInput(
            main_entrance_direction="E",
            kitchen_direction="SE",
        ),
    )
    res = evaluate_vastu_layout(req)
    assert res.factors_assessed == 2
    # Both evaluated at 100% of their weights (25/25 and 20/20) -> normalized score must be 100!
    assert res.compliance_score == 100
    assert len(res.missing_data_warnings) >= 1


def test_zero_assessable_inputs_returns_none_score():
    """When no assessable placements are provided, score must be None with explicit warning."""
    req = VastuEvaluationRequest(
        property_name="Empty Draft",
        property_type="residential",
    )
    res = evaluate_vastu_layout(req)
    assert res.compliance_score is None
    assert "Unassessed" in (res.score_grade or "")
    assert res.factors_assessed == 0
    assert any("No assessable room or plot factors" in w for w in res.missing_data_warnings)


# ------------------------------------------------------------------------------
# 3. Classical Dosha Detection Tests
# ------------------------------------------------------------------------------

def test_ishanya_dosha_detected():
    """Placing toilet or kitchen in North-East must trigger Īśānya Dosha."""
    req = VastuEvaluationRequest(
        property_name="Defective NE House",
        property_type="residential",
        placements=RoomPlacementsInput(
            kitchen_direction="NE",  # Severe water-fire conflict in Ishanya
            toilet_directions=["NE"],
        ),
    )
    res = evaluate_vastu_layout(req)
    dosha_codes = [d.dosha_code for d in res.doshas]
    assert "ISHANYA_CORRUPTION" in dosha_codes
    ishanya = next(d for d in res.doshas if d.dosha_code == "ISHANYA_CORRUPTION")
    assert ishanya.severity == "critical"
    assert len(ishanya.remedies) > 0


def test_agneya_dosha_detected():
    """Underground water tank in South-East must trigger Āgneya Dosha."""
    req = VastuEvaluationRequest(
        property_name="Defective SE House",
        property_type="residential",
        placements=RoomPlacementsInput(
            underground_water_tank_direction="SE",
        ),
    )
    res = evaluate_vastu_layout(req)
    dosha_codes = [d.dosha_code for d in res.doshas]
    assert "AGNEYA_WATER_DEFECT" in dosha_codes


def test_nairruti_dosha_detected():
    """Main entrance or underground water in South-West must trigger Nairṛtya Dosha."""
    req = VastuEvaluationRequest(
        property_name="Defective SW House",
        property_type="residential",
        placements=RoomPlacementsInput(
            main_entrance_direction="SW",
            underground_water_tank_direction="SW",
        ),
    )
    res = evaluate_vastu_layout(req)
    dosha_codes = [d.dosha_code for d in res.doshas]
    assert "NAIRRUTI_DEFECT" in dosha_codes


def test_brahmasthan_obstruction_dosha():
    """Heavily obstructed center zone must trigger Brahmasthan Dosha."""
    req = VastuEvaluationRequest(
        property_name="Blocked Center House",
        property_type="residential",
        placements=RoomPlacementsInput(
            brahmasthan_status="heavily_obstructed",
        ),
    )
    res = evaluate_vastu_layout(req)
    dosha_codes = [d.dosha_code for d in res.doshas]
    assert "BRAHMASTHAN_OBSTRUCTION" in dosha_codes


# ------------------------------------------------------------------------------
# 4. Property Profiles Isolation Tests
# ------------------------------------------------------------------------------

def test_commercial_profile_evaluation():
    """Commercial profile evaluates owner cabin, cash counter, and entrance."""
    req = VastuEvaluationRequest(
        property_name="Apex Financial HQ",
        property_type="commercial",
        facing_direction="N",
        placements=RoomPlacementsInput(
            main_entrance_direction="N",
            owner_cabin_direction="SW",
            accounts_cash_direction="N",
            conference_room_direction="NW",
        ),
    )
    res = evaluate_vastu_layout(req)
    factor_keys = [f.factor_key for f in res.factor_results]
    assert "owner_cabin" in factor_keys
    assert "accounts_cash" in factor_keys
    assert "kitchen" not in factor_keys  # Residential-only factor excluded!
    assert res.compliance_score is not None
    assert res.compliance_score >= 80


def test_plot_profile_evaluation():
    """Plot profile evaluates plot shape and natural slope."""
    req = VastuEvaluationRequest(
        property_name="East Greens Plot",
        property_type="plot",
        placements=RoomPlacementsInput(
            plot_shape="rectangular",
            slope_direction="NE",
        ),
    )
    res = evaluate_vastu_layout(req)
    factor_keys = [f.factor_key for f in res.factor_results]
    assert "plot_shape" in factor_keys
    assert "slope_orientation" in factor_keys
    assert "master_bedroom" not in factor_keys


def test_industrial_profile_evaluation():
    """Industrial profile evaluates heavy machinery and furnace/boiler."""
    req = VastuEvaluationRequest(
        property_name="Zenith Heavy Engineering",
        property_type="industrial",
        placements=RoomPlacementsInput(
            main_entrance_direction="N",
            heavy_machinery_direction="SW",
            boiler_furnace_direction="SE",
        ),
    )
    res = evaluate_vastu_layout(req)
    factor_keys = [f.factor_key for f in res.factor_results]
    assert "heavy_machinery" in factor_keys
    assert "boiler_furnace" in factor_keys


# ------------------------------------------------------------------------------
# 5. Astro-Vastu Overlay Integration Test (Native XALEN Engine)
# ------------------------------------------------------------------------------

def test_astro_vastu_overlay_native_ephemeris():
    """When birth data is provided, verify native XALEN ephemeris computes Lagna & favorable directions."""
    req = VastuEvaluationRequest(
        property_name="Personalized Home",
        property_type="residential",
        birth_date="1990-05-15",
        birth_time="08:30",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        placements=RoomPlacementsInput(
            main_entrance_direction="E",
        ),
    )
    res = evaluate_vastu_layout(req)
    assert res.astro_overlay is not None
    assert res.astro_overlay.lagna_sign != ""
    assert res.astro_overlay.lagna_ruler != ""
    assert len(res.astro_overlay.favorable_directions) > 0
    assert "XALEN" in res.astro_overlay.calculation_source


# ------------------------------------------------------------------------------
# 6. API Endpoints & Auth Mock Tests
# ------------------------------------------------------------------------------

def test_api_get_directions_metadata():
    """GET /api/v1/vastu/directions returns full metadata."""
    resp = client.get("/api/v1/vastu/directions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["directions_8"]) == 8
    assert len(data["directions_16"]) == 16
    assert len(data["padas_32"]) == 32
    assert data["directions_16"][0]["code"] == "N"
    assert data["directions_16"][1]["code"] == "NNE"
    assert data["directions_16"][2]["code"] == "NE"
    assert data["directions_16"][3]["code"] == "ENE"
    assert data["directions_16"][4]["code"] == "E"


def test_api_evaluate_endpoint():
    """POST /api/v1/vastu/evaluate returns structured response."""
    payload = {
        "property_name": "API Test Residence",
        "property_type": "residential",
        "facing_direction": "N",
        "placements": {
            "main_entrance_direction": "N",
            "kitchen_direction": "SE",
            "master_bedroom_direction": "SW",
            "pooja_room_direction": "NE",
        },
    }
    resp = client.post("/api/v1/vastu/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["property_name"] == "API Test Residence"
    assert data["compliance_score"] is not None
    assert len(data["factor_results"]) > 0
    assert "disclaimer" in data


def test_api_evaluate_invalid_direction_422():
    """Invalid direction code triggers 422 Unprocessable Entity."""
    payload = {
        "property_name": "Invalid Test",
        "facing_direction": "INVALID_DIR",
    }
    resp = client.post("/api/v1/vastu/evaluate", json=payload)
    assert resp.status_code == 422


def test_api_reports_unauthenticated_401():
    """Unauthenticated requests to persistence endpoints must return 401."""
    resp = client.get("/api/v1/vastu/reports")
    assert resp.status_code == 401

    resp_post = client.post("/api/v1/vastu/reports", json={"property_name": "Test", "facing_direction": "E", "evaluation_data": {}})
    assert resp_post.status_code == 401


def test_api_reports_authenticated_crud():
    """Mock authenticated user and test report CRUD lifecycle."""
    mock_user = {"id": "00000000-0000-0000-0000-000000000001", "role": "user"}
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        # 1. Create / Save Report
        payload = {
            "property_name": "My Dream Abode",
            "property_type": "residential",
            "facing_direction": "NE",
            "facing_degrees": 45.0,
            "evaluation_data": {
                "compliance_score": 92,
                "score_grade": "A+",
                "doshas": [],
                "general_remedies": ["Keep entrance bright."],
            },
        }
        res_post = client.post("/api/v1/vastu/reports", json=payload)
        assert res_post.status_code == 201
        created = res_post.json()
        assert created["property_name"] == "My Dream Abode"
        report_id = created["id"]

        # 2. List Reports
        res_list = client.get("/api/v1/vastu/reports")
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert list_data["total_count"] >= 1
        assert any(r["id"] == report_id for r in list_data["reports"])

        # 3. Get Report by ID
        res_get = client.get(f"/api/v1/vastu/reports/{report_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == report_id

        # 4. Update Report
        payload["property_name"] = "My Dream Abode (Updated)"
        res_put = client.put(f"/api/v1/vastu/reports/{report_id}", json=payload)
        assert res_put.status_code == 200
        assert res_put.json()["property_name"] == "My Dream Abode (Updated)"

        # 5. Delete Report
        res_del = client.delete(f"/api/v1/vastu/reports/{report_id}")
        assert res_del.status_code == 204

        # 6. Get Deleted Report -> 404
        res_del_chk = client.get(f"/api/v1/vastu/reports/{report_id}")
        assert res_del_chk.status_code == 404

    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ------------------------------------------------------------------------------
# 7. Independent Verification: Pada Boundaries, Aliases, & Geometry
# ------------------------------------------------------------------------------

def test_azimuth_to_pada_boundaries_and_midpoints():
    """Verify exact 11.25° pada boundaries and wraparound across cardinal directions."""
    # North wraparound (Pada 4: Bhallata, 348.75° to 360.0°; Pada 5: Soma, 0.0° to 11.25°)
    p_bhallata = azimuth_to_pada(350.0)
    assert p_bhallata["pada_index"] == 4
    assert "Bhallāṭa" in p_bhallata["sanskrit_name"]

    p_soma_zero = azimuth_to_pada(0.0)
    assert p_soma_zero["pada_index"] == 5
    assert "Soma" in p_soma_zero["sanskrit_name"]

    p_soma_mid = azimuth_to_pada(5.625)
    assert p_soma_mid["pada_index"] == 5

    # Boundary transition at 11.25° (Bhujaga)
    p_bhujaga = azimuth_to_pada(11.26)
    assert p_bhujaga["pada_index"] == 6

    # East auspicious gates: Pada 11 (Jayanta: 67.5° - 78.75°) and Pada 12 (Indra: 78.75° - 90.0°)
    p_jayanta = azimuth_to_pada(72.0)
    assert p_jayanta["pada_index"] == 11
    assert "Jayanta" in p_jayanta["sanskrit_name"]

    p_indra = azimuth_to_pada(85.0)
    assert p_indra["pada_index"] == 12
    assert "Indra" in p_indra["sanskrit_name"]

    # South auspicious gate: Pada 20 (Grihakshata: 168.75° - 180.0°)
    p_griha = azimuth_to_pada(174.0)
    assert p_griha["pada_index"] == 20
    assert "Gṛhakṣata" in p_griha["sanskrit_name"]

    # West auspicious gates: Pada 28 (Pushpadanta: 258.75° - 270.0°) and Pada 29 (Varuna: 270.0° - 281.25°)
    p_pushpa = azimuth_to_pada(264.0)
    assert p_pushpa["pada_index"] == 28
    assert "Puṣpadanta" in p_pushpa["sanskrit_name"]

    p_varuna = azimuth_to_pada(275.0)
    assert p_varuna["pada_index"] == 29
    assert "Varuṇa" in p_varuna["sanskrit_name"]


def test_lookup_pada_aliases():
    """Verify lookup_pada resolves wall codes, direct indices, and Sanskrit names."""
    # Wall codes (N1..N8, E1..E8, S1..S8, W1..W8)
    e3 = lookup_pada("E3")
    assert e3 is not None and e3["pada_index"] == 11  # Jayanta
    assert "Jayanta" in e3["sanskrit_name"]

    s4 = lookup_pada("S4")
    assert s4 is not None and s4["pada_index"] == 20  # Grihakshata

    w5 = lookup_pada("W5")
    assert w5 is not None and w5["pada_index"] == 29  # Varuna

    n4 = lookup_pada("N4")
    assert n4 is not None and n4["pada_index"] == 4   # Bhallata

    # Index formats
    p11 = lookup_pada("p11")
    assert p11 is not None and p11["pada_index"] == 11
    p20_num = lookup_pada("20")
    assert p20_num is not None and p20_num["pada_index"] == 20

    # Name formats
    j_name = lookup_pada("jayanta")
    assert j_name is not None and j_name["pada_index"] == 11

    # Invalid input
    assert lookup_pada("") is None
    assert lookup_pada("xyz_nonexistent") is None


def test_main_entrance_pada_evaluation():
    """Verify residential evaluation accurately scores auspicious vs inauspicious entrance padas."""
    # Auspicious pada E3 (Jayanta)
    req_auspicious = VastuEvaluationRequest(
        property_name="Auspicious Gate Abode",
        property_type="residential",
        placements=RoomPlacementsInput(
            main_entrance_direction="E",
            main_entrance_pada="Jayanta",
        ),
    )
    res_auspicious = evaluate_vastu_layout(req_auspicious)
    fe_a = next(f for f in res_auspicious.factor_results if f.factor_key == "main_entrance")
    assert fe_a.severity == "ideal"
    assert fe_a.score == 25.0
    assert "auspicious pada 'Jayanta" in fe_a.explanation

    # Inauspicious pada S1 (Pitri / Nairruti)
    req_inauspicious = VastuEvaluationRequest(
        property_name="Inauspicious Gate Abode",
        property_type="residential",
        placements=RoomPlacementsInput(
            main_entrance_direction="SW",
            main_entrance_pada="Pitri",
        ),
    )
    res_inauspicious = evaluate_vastu_layout(req_inauspicious)
    fe_i = next(f for f in res_inauspicious.factor_results if f.factor_key == "main_entrance")
    assert fe_i.severity == "severe_defect"
    assert fe_i.score <= 5.0
    assert fe_i.remedy is not None


def test_astro_vastu_verification_fixtures():
    """Verify Astro-Vastu against native XALEN ephemeris fixtures:
    Native born 1990-05-15 14:30 at Chennai (13.0827°N, 80.2707°E) with Lahiri ayanamsa.
    Ascendant: Virgo (Kanya), Lord: Mercury.
    Moon: Capricorn (Makara), Nakshatra: Uttara Ashadha.
    """
    req = VastuEvaluationRequest(
        property_name="Chennai Resident Astro-Vastu",
        property_type="residential",
        birth_date="1990-05-15",
        birth_time="14:30",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        placements=RoomPlacementsInput(
            main_entrance_direction="N",
        ),
    )
    res = evaluate_vastu_layout(req)
    assert res.astro_overlay is not None
    assert res.astro_overlay.lagna_sign == "Virgo"
    assert res.astro_overlay.lagna_ruler == "Mercury"
    assert res.astro_overlay.moon_sign == "Capricorn"
    assert res.astro_overlay.nakshatra is not None
    assert "Uttara Ashadha" in res.astro_overlay.nakshatra
    assert "N" in res.astro_overlay.favorable_directions
    assert "W" in res.astro_overlay.favorable_directions
    assert "S" in res.astro_overlay.unfavorable_directions
    assert res.astro_overlay.calculation_source == "Native XALEN Ephemeris Engine (Verified)"


def test_multi_user_report_isolation():
    """Verify local cache / service isolation across distinct authenticated users."""
    user_a = "user-11111111-1111-1111-1111-111111111111"
    user_b = "user-22222222-2222-2222-2222-222222222222"

    rep_a_data = SaveVastuReportRequest(
        property_name="User A Sanctuary",
        property_type="residential",
        facing_direction="N",
        evaluation_data={"compliance_score": 88, "score_grade": "A"},
    )
    rep_b_data = SaveVastuReportRequest(
        property_name="User B Commercial Hub",
        property_type="commercial",
        facing_direction="E",
        evaluation_data={"compliance_score": 75, "score_grade": "B"},
    )

    created_a = save_vastu_report(user_id=user_a, request=rep_a_data)
    created_b = save_vastu_report(user_id=user_b, request=rep_b_data)

    # User A listing must only see User A's reports
    reports_a, count_a = list_vastu_reports(user_id=user_a)
    assert any(r["id"] == created_a["id"] for r in reports_a)
    assert not any(r["id"] == created_b["id"] for r in reports_a)

    # User B listing must only see User B's reports
    reports_b, count_b = list_vastu_reports(user_id=user_b)
    assert any(r["id"] == created_b["id"] for r in reports_b)
    assert not any(r["id"] == created_a["id"] for r in reports_b)

    # Cross-user retrieval attempt fails
    assert get_vastu_report(user_id=user_b, report_id=created_a["id"]) is None
    assert get_vastu_report(user_id=user_a, report_id=created_b["id"]) is None

    # Cross-user deletion attempt fails
    assert delete_vastu_report(user_id=user_b, report_id=created_a["id"]) is False
    assert get_vastu_report(user_id=user_a, report_id=created_a["id"]) is not None

    # Clean up
    delete_vastu_report(user_id=user_a, report_id=created_a["id"])
    delete_vastu_report(user_id=user_b, report_id=created_b["id"])

