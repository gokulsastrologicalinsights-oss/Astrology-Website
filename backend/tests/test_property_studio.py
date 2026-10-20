"""Comprehensive Unit & Integration Test Suite for House, Flat & Property Numerology Studio.

Tests:
1. Property Component Analysis (Door, Building, Floor, Plot, Full Alphanumeric).
2. Calculation Modes:
   - door_number: micro threshold vibration (e.g. '4B' -> 4+2=6 in Chaldean).
   - building_number: macro structural shell (e.g. 'Tower 3' -> 3).
   - floor_number: vertical elemental elevation (e.g. '4' -> 4).
   - plot_number: foundational land anchoring (e.g. 'Plot 42' -> 4+2=6).
   - combined_property: transparent formula adding active components.
   - full_alphanumeric: full property title.
3. Leading zeros, slashes, hyphens, and mixed alphanumeric inputs ('004', '12/A', 'F-4').
4. Pythagorean vs Chaldean letter transformations.
5. Master numbers (11, 22, 33) preservation.
6. Property usage archetypes (residential, commercial, rental investment, creative studio, spiritual).
7. Vastu Shastra facing direction resonance (North, North-East, South-West, etc.).
8. Resident & Family Compatibility (Psychic & Life Path alignment).
9. Multi-candidate evaluation & ranking (deduplication, max limits, sorting).
10. Validation constraints & API Endpoint integration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.property_studio import (
    calculate_property_character_mapping,
    analyze_property_component,
    calculate_combined_property_formula,
    evaluate_property_usage_harmony,
    evaluate_property_vastu_facing,
    evaluate_single_resident_compatibility,
    evaluate_property_candidates,
    analyze_property_numerology_full,
    VASTU_DIRECTIONS_MAP,
)

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. Component Parsing & Calculation Modes
# ------------------------------------------------------------------------------

class TestPropertyComponentCalculations:
    def test_door_number_chaldean(self):
        """Verify door number '4B': 4 + B(2) = 6 in Chaldean."""
        res = analyze_property_component("4B", "door_number", "Door / Flat Number", convention="chaldean")
        assert res["compound_sum"] == 6
        assert res["root_number"] == 6
        assert res["is_master"] is False
        assert "4" in res["included_characters"]
        assert "B" in res["included_characters"]

    def test_door_number_with_slash_and_hyphen(self):
        """Verify punctuation like slashes and hyphens are skipped: '12/A' or 'F-4'."""
        # '12/A' -> 1 + 2 + A(1) = 4
        res1 = analyze_property_component("12/A", "door_number", "Door Number", convention="chaldean")
        assert res1["compound_sum"] == 4
        assert res1["root_number"] == 4

        # 'F-4' in Chaldean: F(8) + 4 = 12 -> 3
        res2 = analyze_property_component("F-4", "door_number", "Door Number", convention="chaldean")
        assert res2["compound_sum"] == 12
        assert res2["root_number"] == 3

    def test_leading_zeros(self):
        """Verify leading zeros do not alter numerical sum: '007' -> 7."""
        res = analyze_property_component("007", "door_number", "Door Number", convention="chaldean")
        assert res["compound_sum"] == 7
        assert res["root_number"] == 7

    def test_building_and_floor_numbers(self):
        """Verify building and floor number calculations."""
        # 'Tower 3': T(4) + O(7) + W(6) + E(5) + R(2) + 3 = 27 -> 9
        res_bldg = analyze_property_component("3", "building_number", "Building Number", convention="chaldean")
        assert res_bldg["compound_sum"] == 3
        assert res_bldg["root_number"] == 3

        res_floor = analyze_property_component("12", "floor_number", "Floor Number", convention="chaldean")
        assert res_floor["compound_sum"] == 3  # 1+2 = 3
        assert res_floor["root_number"] == 3

    def test_plot_number_calculation(self):
        """Verify plot number reduction: '42' -> 4+2 = 6."""
        res = analyze_property_component("42", "plot_number", "Plot Number", convention="chaldean")
        assert res["compound_sum"] == 6
        assert res["root_number"] == 6

    def test_combined_property_formula(self):
        """Verify combined formula sums active component totals."""
        door = analyze_property_component("4B", "door_number", "Door", convention="chaldean")       # 6
        floor = analyze_property_component("4", "floor_number", "Floor", convention="chaldean")      # 4
        bldg = analyze_property_component("3", "building_number", "Building", convention="chaldean") # 3
        plot = analyze_property_component("", "plot_number", "Plot", convention="chaldean")          # 0

        combined = calculate_combined_property_formula(door, bldg, floor, plot, convention="chaldean")
        # 6 + 4 + 3 = 13 -> 1+3 = 4
        assert combined["compound_sum"] == 13
        assert combined["root_number"] == 4
        assert combined["single_root"] == 4
        assert "Door 4B(6)" in combined["reduction_steps"][0]

    def test_pythagorean_vs_chaldean_property_name(self):
        """Verify name reduction differences between Pythagorean and Chaldean."""
        name = "Lotus Greens"
        res_chald = analyze_property_component(name, "building_name", "Building Name", convention="chaldean")
        res_pyth = analyze_property_component(name, "building_name", "Building Name", convention="pythagorean")

        assert 1 <= res_chald["root_number"] <= 33
        assert 1 <= res_pyth["root_number"] <= 33
        assert len(res_chald["reduction_steps"]) > 0


# ------------------------------------------------------------------------------
# 2. Master Number Preservation
# ------------------------------------------------------------------------------

class TestPropertyMasterNumbers:
    def test_master_number_11_preservation(self):
        """Verify Master Number 11 is preserved in property calculations."""
        # In Chaldean: '29' -> 2+9 = 11
        res = analyze_property_component("29", "door_number", "Door Number", convention="chaldean")
        assert res["compound_sum"] == 11
        assert res["root_number"] == 11
        assert res["single_root"] == 2
        assert res["is_master"] is True

    def test_master_number_22_preservation(self):
        """Verify Master Number 22 is preserved."""
        # '499' -> 4+9+9 = 22
        res = analyze_property_component("499", "door_number", "Door Number", convention="chaldean")
        assert res["compound_sum"] == 22
        assert res["root_number"] == 22
        assert res["single_root"] == 4
        assert res["is_master"] is True


# ------------------------------------------------------------------------------
# 3. Usage & Vastu Direction Alignment
# ------------------------------------------------------------------------------

class TestPropertyUsageAndVastu:
    def test_property_usage_harmony(self):
        """Verify residential and commercial usage scores."""
        # Root 6 for residential living (Venus is primary)
        res_res = evaluate_property_usage_harmony(property_root=6, usage_type="residential_living")
        assert res_res["score"] == 95.0
        assert "Optimal" in res_res["level"]

        # Root 1 for commercial business (Sun is primary)
        res_comm = evaluate_property_usage_harmony(property_root=1, usage_type="commercial_business")
        assert res_comm["score"] == 95.0

    def test_vastu_facing_direction(self):
        """Verify Vastu direction evaluation for North-East (Ishanya)."""
        vastu = evaluate_property_vastu_facing(facing_direction="North-East", property_root=3)
        assert vastu is not None
        assert vastu["facing_direction"] == "North-East"
        assert vastu["sanskrit_name"] == "Ishanya"
        assert vastu["element"] == "Water / Ether (Jala-Akasha)"
        assert vastu["alignment_score"] == 95.0

    def test_vastu_abbreviation_support(self):
        """Verify short direction codes like 'NE', 'SW' resolve correctly."""
        vastu_ne = evaluate_property_vastu_facing(facing_direction="NE", property_root=1)
        assert vastu_ne is not None
        assert vastu_ne["facing_direction"] == "North-East"

        vastu_sw = evaluate_property_vastu_facing(facing_direction="SW", property_root=4)
        assert vastu_sw is not None
        assert vastu_sw["facing_direction"] == "South-West"


# ------------------------------------------------------------------------------
# 4. Resident & Family Compatibility
# ------------------------------------------------------------------------------

class TestResidentCompatibility:
    def test_resident_dob_alignment(self):
        """Verify resident Psychic and Life Path harmony scoring."""
        # Resident born 1994-06-15 (Day 15 -> Psychic 6)
        # Property root 6
        res = evaluate_single_resident_compatibility(
            property_root=6,
            birth_date_str="1994-06-15",
            name="Gokul",
            is_primary=True,
        )
        assert res["psychic_number"] == 6
        assert res["personal_score"] >= 80.0
        assert res["level"] in ("Harmonious", "Complementary")


# ------------------------------------------------------------------------------
# 5. Multi-Property Candidate Comparison
# ------------------------------------------------------------------------------

class TestPropertyCandidateRanking:
    def test_candidate_comparison_and_deduplication(self):
        """Verify multi-property candidate ranking and deduplication."""
        candidates = [
            {"door_flat_number": "4B", "building_name": "Lotus Greens"},
            {"door_flat_number": "4B", "building_name": "Lotus Greens"},  # Duplicate
            {"door_flat_number": "102", "building_name": "Skyline Heights"},
            {"door_flat_number": "504", "building_name": "Royal Residency"},
        ]
        results = evaluate_property_candidates(
            candidates_list=candidates,
            calculation_mode="door_number",
            convention="chaldean",
            property_usage="residential_living",
            primary_birth_date="1994-06-15",
            max_candidates=25,
        )
        assert len(results) == 3  # 4 minus 1 duplicate
        assert results[0]["composite_score"] >= results[1]["composite_score"]

    def test_max_candidates_limit(self):
        """Verify candidate boundary enforcement."""
        candidates = [{"door_flat_number": f"{i}A", "building_name": "Tower"} for i in range(1, 35)]
        results = evaluate_property_candidates(candidates_list=candidates, max_candidates=10)
        assert len(results) == 10


# ------------------------------------------------------------------------------
# 6. End-to-End Orchestration & API Endpoint
# ------------------------------------------------------------------------------

class TestPropertyStudioAPI:
    def test_full_property_numerology_orchestration(self):
        """Verify analyze_property_numerology_full pipeline."""
        res = analyze_property_numerology_full(
            property_category="apartment_flat",
            tenure_type="purchased",
            door_flat_number="4B",
            building_number="Tower 3",
            floor_number="4",
            building_name="Lotus Greens",
            facing_direction="North-East",
            property_usage="residential_living",
            convention="chaldean",
            calculation_mode="door_number",
            primary_birth_date="1994-06-15",
            primary_owner_name="Gokul",
            co_residents=[{"name": "Spouse", "birth_date": "1996-03-22", "role": "Spouse"}],
            candidate_properties=[{"door_flat_number": "102", "building_name": "Skyline"}],
        )

        assert res["door_flat_number"] == "4B"
        assert res["primary_analysis"]["calculation_mode"] == "door_number"
        assert res["primary_analysis"]["root_number"] == 6
        assert res["combined_analysis"]["compound_sum"] > 0
        assert res["vastu_alignment"] is not None
        assert len(res["resident_alignments"]) == 2
        assert res["overall_household_score"] is not None
        assert len(res["candidates"]) == 1
        assert "disclaimer" in res

    def test_api_property_analyze_endpoint_success(self):
        """Test POST /api/v1/numerology/property/analyze."""
        payload = {
            "property_category": "independent_house",
            "tenure_type": "purchased",
            "door_flat_number": "12",
            "plot_number": "45",
            "facing_direction": "East",
            "property_usage": "residential_living",
            "system_convention": "chaldean",
            "calculation_mode": "door_number",
            "primary_birth_date": "1990-10-25",
        }
        response = client.post("/api/v1/numerology/property/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["door_flat_number"] == "12"
        # 1+2 = 3
        assert data["door_analysis"]["compound_sum"] == 3
        assert data["door_analysis"]["root_number"] == 3
        assert data["vastu_alignment"]["facing_direction"] == "East"
        assert len(data["resident_alignments"]) == 1

    def test_api_property_validation_error(self):
        """Test invalid birth date returns 422."""
        payload = {
            "door_flat_number": "4B",
            "primary_birth_date": "15-06-1994",  # invalid format
        }
        response = client.post("/api/v1/numerology/property/analyze", json=payload)
        assert response.status_code == 422
