"""Independent mathematical validation and API tests for Prastarashtakavarga and Kaksha transit engine.

Classical References:
- Brihat Parashara Hora Shastra (BPHS), Chapters 66–67.
- Dr. B.V. Raman, 'Ashtakavarga System of Direction', Chapters 5 & 6.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ashtakavarga_engine.calculator import calculate_ashtakavarga
from app.services.ashtakavarga_engine.prastara import (
    KAKSHA_CONTRIBUTOR_ORDER,
    compute_planet_prastara,
    compute_all_prastara_matrices,
)
from app.services.ashtakavarga_engine.kaksha import (
    KAKSHA_WIDTH_DEG,
    KAKSHA_RANGES,
    get_kaksha_division_for_degree,
    build_planet_kaksha_grid,
    build_all_kaksha_grids,
    evaluate_kaksha_transit,
)
from app.services.ashtakavarga_engine.tables import (
    ASHTAKAVARGA_CONTRIBUTIONS,
    EXPECTED_TOTALS,
    PLANETS_7,
    TOTAL_SAV_BINDUS,
)

client = TestClient(app)

SAMPLE_CHART_PLANETS = [
    {"name": "Sun", "sign_index": 2},       # Taurus
    {"name": "Moon", "sign_index": 4},      # Cancer
    {"name": "Mars", "sign_index": 10},     # Capricorn
    {"name": "Mercury", "sign_index": 3},   # Gemini
    {"name": "Jupiter", "sign_index": 9},   # Sagittarius
    {"name": "Venus", "sign_index": 12},    # Pisces
    {"name": "Saturn", "sign_index": 7},    # Libra
    {"name": "Rahu", "sign_index": 11},
    {"name": "Ketu", "sign_index": 5},
]
SAMPLE_ASCENDANT_SIGN = 1  # Aries


def test_prastara_donor_order_and_cardinality():
    """Verify that the 8 donors follow the classical Kaksha sequence (slowest to fastest + Lagna)."""
    expected_order = ("Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna")
    assert KAKSHA_CONTRIBUTOR_ORDER == expected_order
    assert len(KAKSHA_CONTRIBUTOR_ORDER) == 8


def test_prastara_matrix_reconciliation_with_bav():
    """Verify that column sums in every Prastara matrix reconcile exactly with BAV sign bindus."""
    ashtaka_res = calculate_ashtakavarga(SAMPLE_CHART_PLANETS, SAMPLE_ASCENDANT_SIGN)
    contributor_signs = {p["name"]: p["sign_index"] for p in SAMPLE_CHART_PLANETS if p["name"] in PLANETS_7}
    contributor_signs["Lagna"] = SAMPLE_ASCENDANT_SIGN

    prastara_dict = compute_all_prastara_matrices(contributor_signs)

    for planet in PLANETS_7:
        prastara = prastara_dict[planet]
        bav = ashtaka_res.bhinnashtakavarga[planet]

        # 1. Row count must be exactly 8 donors
        assert len(prastara.rows) == 8
        donors_in_rows = [r.contributor for r in prastara.rows]
        assert tuple(donors_in_rows) == KAKSHA_CONTRIBUTOR_ORDER

        # 2. Grand total of matrix must equal canonical BAV total
        assert prastara.total_bindus == EXPECTED_TOTALS[planet]
        assert prastara.total_bindus == bav.total_bindus

        # 3. Column totals must match BAV sign bindus for all 12 signs
        for s in range(1, 13):
            assert prastara.sign_totals[s] == bav.sign_bindus[s], (
                f"Mismatch in {planet} Prastara for sign {s}: "
                f"Prastara={prastara.sign_totals[s]} vs BAV={bav.sign_bindus[s]}"
            )

        # 4. Each donor row total must match the count of benefic houses in BPHS
        rules = ASHTAKAVARGA_CONTRIBUTIONS[planet]
        for row in prastara.rows:
            expected_donor_bindus = len(rules.get(row.contributor, ()))
            assert row.total_contributions == expected_donor_bindus, (
                f"Donor {row.contributor} in {planet} Prastara: "
                f"row sum {row.total_contributions} != expected {expected_donor_bindus}"
            )
            # Binary values only
            for s in range(1, 13):
                assert row.sign_bindus[s] in (0, 1)


def test_prastara_grand_total_337_invariant():
    """Verify that the sum of bindus across all 7 Prastara matrices equals 337."""
    contributor_signs = {p["name"]: p["sign_index"] for p in SAMPLE_CHART_PLANETS if p["name"] in PLANETS_7}
    contributor_signs["Lagna"] = SAMPLE_ASCENDANT_SIGN

    prastara_dict = compute_all_prastara_matrices(contributor_signs)
    grand_sum = sum(p.total_bindus for p in prastara_dict.values())
    assert grand_sum == TOTAL_SAV_BINDUS == 337


def test_kaksha_division_boundaries():
    """Test precise degree boundary handling and lord assignment across 0° to 30°."""
    # 8 divisions: 3°45' (3.75°) each
    test_cases = [
        # degree, expected_kaksha (1-8), expected_lord, expected_start, expected_end
        (0.0, 1, "Saturn", 0.0, 3.75),
        (1.5, 1, "Saturn", 0.0, 3.75),
        (3.7499, 1, "Saturn", 0.0, 3.75),
        (3.75, 2, "Jupiter", 3.75, 7.50),
        (5.0, 2, "Jupiter", 3.75, 7.50),
        (7.4999, 2, "Jupiter", 3.75, 7.50),
        (7.5, 3, "Mars", 7.50, 11.25),
        (11.2499, 3, "Mars", 7.50, 11.25),
        (11.25, 4, "Sun", 11.25, 15.00),
        (14.9999, 4, "Sun", 11.25, 15.00),
        (15.0, 5, "Venus", 15.00, 18.75),
        (18.7499, 5, "Venus", 15.00, 18.75),
        (18.75, 6, "Mercury", 18.75, 22.50),
        (22.4999, 6, "Mercury", 18.75, 22.50),
        (22.5, 7, "Moon", 22.50, 26.25),
        (26.2499, 7, "Moon", 22.50, 26.25),
        (26.25, 8, "Lagna", 26.25, 30.00),
        (29.9999, 8, "Lagna", 26.25, 30.00),
        (30.0, 8, "Lagna", 26.25, 30.00),
    ]

    for deg, exp_k, exp_lord, exp_start, exp_end in test_cases:
        k_num, lord, start_d, end_d, range_str = get_kaksha_division_for_degree(deg)
        assert k_num == exp_k, f"Deg {deg}: Kaksha {k_num} != expected {exp_k}"
        assert lord == exp_lord, f"Deg {deg}: Lord {lord} != expected {exp_lord}"
        assert abs(start_d - exp_start) < 1e-4
        assert abs(end_d - exp_end) < 1e-4
        assert range_str == KAKSHA_RANGES[exp_k - 1]


def test_kaksha_grid_construction_and_bav_reconciliation():
    """Verify that build_all_kaksha_grids creates 96 divisions per planet reconciling with BAV."""
    contributor_signs = {p["name"]: p["sign_index"] for p in SAMPLE_CHART_PLANETS if p["name"] in PLANETS_7}
    contributor_signs["Lagna"] = SAMPLE_ASCENDANT_SIGN

    prastara_dict = compute_all_prastara_matrices(contributor_signs)
    kaksha_grids = build_all_kaksha_grids(prastara_dict)

    for planet in PLANETS_7:
        assert planet in kaksha_grids
        sign_details = kaksha_grids[planet]
        assert len(sign_details) == 12  # 12 signs

        prastara = prastara_dict[planet]

        for s_idx, s_detail in enumerate(sign_details, start=1):
            assert s_detail.sign_index == s_idx
            assert len(s_detail.divisions) == 8  # 8 Kakshas per sign

            # Bindu count in this sign must equal the count of divisions where has_bindu is True
            auspicious_count = sum(1 for d in s_detail.divisions if d.has_bindu)
            assert s_detail.total_bindus == auspicious_count
            assert s_detail.total_bindus == prastara.sign_totals[s_idx]

            # Contiguous range without gaps or overlaps
            for i in range(8):
                div = s_detail.divisions[i]
                assert div.kaksha_number == i + 1
                assert div.lord == KAKSHA_CONTRIBUTOR_ORDER[i]
                assert abs(div.start_degree - i * KAKSHA_WIDTH_DEG) < 1e-4
                assert abs(div.end_degree - (i + 1) * KAKSHA_WIDTH_DEG) < 1e-4
                assert div.auspicious == div.has_bindu


def test_evaluate_kaksha_transit():
    """Test Kaksha transit auspiciousness evaluation using absolute longitude and sign/degree."""
    contributor_signs = {p["name"]: p["sign_index"] for p in SAMPLE_CHART_PLANETS if p["name"] in PLANETS_7}
    contributor_signs["Lagna"] = SAMPLE_ASCENDANT_SIGN
    prastara_dict = compute_all_prastara_matrices(contributor_signs)

    # Let's inspect Sun's Prastara in Aries (Sign 1)
    sun_prastara = prastara_dict["Sun"]
    donor_map = {r.contributor: r.sign_bindus[1] for r in sun_prastara.rows}

    # Test each Kaksha in Aries for Sun:
    # Aries: 0° to 30° longitude
    for k_idx, lord in enumerate(KAKSHA_CONTRIBUTOR_ORDER):
        mid_deg = k_idx * 3.75 + 1.875  # middle of each Kaksha
        result = evaluate_kaksha_transit(
            transiting_planet="Sun",
            prastara_dict=prastara_dict,
            transit_longitude=mid_deg,
        )
        assert result.transiting_planet == "Sun"
        assert result.sign_index == 1
        assert result.kaksha_number == k_idx + 1
        assert result.kaksha_lord == lord

        expected_bindu = donor_map[lord] == 1
        assert result.has_bindu == expected_bindu
        if expected_bindu:
            assert result.effect == "Auspicious"
            assert "auspicious and produces favorable results" in result.interpretation
        else:
            assert result.effect == "Inauspicious"
            assert "inauspicious or obstructive" in result.interpretation

    # Test sign_index + degree_in_sign input mode
    result_deg = evaluate_kaksha_transit(
        transiting_planet="Jupiter",
        prastara_dict=prastara_dict,
        transit_sign_index=4,  # Cancer
        transit_degree_in_sign=5.0,  # Kaksha 2: 3.75 - 7.50° -> Lord: Jupiter
    )
    assert result_deg.transiting_planet == "Jupiter"
    assert result_deg.sign_index == 4
    assert result_deg.kaksha_number == 2
    assert result_deg.kaksha_lord == "Jupiter"

    # Test error cases
    with pytest.raises(ValueError, match="Must provide either"):
        evaluate_kaksha_transit(transiting_planet="Jupiter", prastara_dict=prastara_dict)

    with pytest.raises(ValueError, match="No Prastara matrix available"):
        evaluate_kaksha_transit(transiting_planet="UnknownPlanet", prastara_dict=prastara_dict, transit_longitude=10.0)


def test_ashtakavarga_api_prastara_and_kaksha_endpoints():
    """Test dedicated API endpoints for Prastara and Kaksha grids."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 2,
    }

    # 1. Test POST /api/v1/vedic/ashtakavarga/prastara
    resp_prastara = client.post("/api/v1/vedic/ashtakavarga/prastara", json=payload)
    assert resp_prastara.status_code == 200
    p_data = resp_prastara.json()
    assert "prastara" in p_data
    assert p_data["grand_total_bindus"] == 337
    assert p_data["validation_status"] == "PASSED"
    for planet in PLANETS_7:
        assert planet in p_data["prastara"]
        assert p_data["prastara"][planet]["total_bindus"] == EXPECTED_TOTALS[planet]
        assert len(p_data["prastara"][planet]["rows"]) == 8

    # 2. Test POST /api/v1/vedic/ashtakavarga/kaksha
    resp_kaksha = client.post("/api/v1/vedic/ashtakavarga/kaksha", json=payload)
    assert resp_kaksha.status_code == 200
    k_data = resp_kaksha.json()
    assert "kaksha_grids" in k_data
    for planet in PLANETS_7:
        assert planet in k_data["kaksha_grids"]
        assert len(k_data["kaksha_grids"][planet]) == 12
        for sign_detail in k_data["kaksha_grids"][planet]:
            assert len(sign_detail["divisions"]) == 8

    # 3. Test POST /api/v1/vedic/ashtakavarga/kaksha/transit
    transit_payload = {
        **payload,
        "transit": {
            "transiting_planet": "Jupiter",
            "transit_longitude": 75.5,  # Gemini 15°30' -> Kaksha 5 (Venus)
        },
    }
    resp_transit = client.post("/api/v1/vedic/ashtakavarga/kaksha/transit", json=transit_payload)
    assert resp_transit.status_code == 200
    t_data = resp_transit.json()
    assert t_data["transiting_planet"] == "Jupiter"
    assert t_data["sign_index"] == 3  # Gemini
    assert t_data["sign_name"] == "Gemini"
    assert t_data["kaksha_number"] == 5
    assert t_data["kaksha_lord"] == "Venus"
    assert t_data["effect"] in ("Auspicious", "Inauspicious")

    # 4. Test master POST /api/v1/vedic/ashtakavarga includes prastara and kaksha_grids
    resp_master = client.post("/api/v1/vedic/ashtakavarga", json=payload)
    assert resp_master.status_code == 200
    m_data = resp_master.json()
    assert "prastara" in m_data and m_data["prastara"] is not None
    assert "kaksha_grids" in m_data and m_data["kaksha_grids"] is not None
    assert len(m_data["prastara"]) == 7
    assert len(m_data["kaksha_grids"]) == 7
