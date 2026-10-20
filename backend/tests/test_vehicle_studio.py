"""Comprehensive Unit & Integration Test Suite for Vehicle Registration Number Numerology Studio.

Tests:
1. Registration Format Parsing (Standard Indian, Delhi style, Bharat BH series, International).
2. Normalization, case insensitivity, whitespace, hyphens, and dots.
3. Component extraction: State, RTO, Series, Numeric Digits.
4. Calculation Modes:
   - digits_only: strictly numeric registration digits.
   - numeric_all: RTO numeric prefix + numeric registration digits.
   - full_alphanumeric: full plate characters mapped via Pythagorean or Chaldean.
5. System Conventions: Pythagorean vs Chaldean letter mappings.
6. Pattern & Rhythm Detection: Single VIP, Quads, Triples, Pairs, Mirrors, Ascending/Descending sequences.
7. Vanity / Memorability Score determinism (0-100).
8. Vehicle Usage Archetypes (Personal, Family, Commercial, Fleet).
9. Owner & Multi-Driver Compatibility (Psychic & Life Path harmony).
10. Multi-candidate evaluation & ranking (deduplication, max limits, sorting).
11. Validation constraints & error handling.
12. API Endpoint integration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.vehicle_studio import (
    parse_vehicle_registration,
    calculate_vehicle_character_mapping,
    analyze_vehicle_mode,
    analyze_vehicle_patterns,
    evaluate_vehicle_usage_harmony,
    evaluate_single_driver_compatibility,
    evaluate_vehicle_candidates,
    analyze_vehicle_numerology_full,
    INDIAN_STATES_UTS,
)

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. Parsing and Component Extraction Tests
# ------------------------------------------------------------------------------

class TestVehicleRegistrationParsing:
    def test_standard_indian_plate_with_spaces(self):
        """Parse standard Indian format: TN 09 AB 1234."""
        parsed = parse_vehicle_registration("TN 09 AB 1234")
        assert parsed["state_code"] == "TN"
        assert parsed["state_name"] == "Tamil Nadu"
        assert parsed["rto_code"] == "09"
        assert parsed["series_letters"] == "AB"
        assert parsed["numeric_digits"] == "1234"
        assert parsed["is_valid_indian_format"] is True
        assert parsed["formatted_registration"] == "TN 09 AB 1234"
        assert parsed["compact_registration"] == "TN09AB1234"

    def test_plate_with_hyphens_and_lowercase(self):
        """Parse format with hyphens and lowercase: mh-12-cd-5678."""
        parsed = parse_vehicle_registration("mh-12-cd-5678")
        assert parsed["state_code"] == "MH"
        assert parsed["state_name"] == "Maharashtra"
        assert parsed["rto_code"] == "12"
        assert parsed["series_letters"] == "CD"
        assert parsed["numeric_digits"] == "5678"
        assert parsed["is_valid_indian_format"] is True
        assert parsed["formatted_registration"] == "MH 12 CD 5678"

    def test_delhi_style_alphanumeric_rto(self):
        """Parse Delhi format where RTO has a digit and letter: DL 3C AB 1234."""
        parsed = parse_vehicle_registration("DL 3C AB 1234")
        assert parsed["state_code"] == "DL"
        assert parsed["state_name"] == "Delhi"
        assert parsed["rto_code"] == "3C"
        assert parsed["series_letters"] == "AB"
        assert parsed["numeric_digits"] == "1234"
        assert parsed["is_valid_indian_format"] is True

    def test_plate_without_series_letters(self):
        """Parse old/simple Indian format without running series: KA 01 1234."""
        parsed = parse_vehicle_registration("KA 01 1234")
        assert parsed["state_code"] == "KA"
        assert parsed["state_name"] == "Karnataka"
        assert parsed["rto_code"] == "01"
        assert parsed["series_letters"] == ""
        assert parsed["numeric_digits"] == "1234"
        assert parsed["is_valid_indian_format"] is True

    def test_bharat_series_bh_format(self):
        """Parse Bharat (BH) series: 22 BH 1234 AA."""
        parsed = parse_vehicle_registration("22 BH 1234 AA")
        assert parsed["state_code"] == "BH"
        assert "Bharat" in parsed["state_name"]
        assert parsed["rto_code"] == "22"
        assert parsed["series_letters"] == "AA"
        assert parsed["numeric_digits"] == "1234"
        assert parsed["is_valid_indian_format"] is True
        assert "BH" in parsed["plate_classification"]

    def test_international_or_custom_plate_fallback(self):
        """Parse non-standard or foreign plate gracefully: NY 777."""
        parsed = parse_vehicle_registration("NY 777")
        assert parsed["numeric_digits"] == "777"
        assert parsed["is_valid_indian_format"] is False
        assert "Custom" in parsed["plate_classification"]

    def test_empty_registration_raises_error(self):
        """Empty string or whitespace-only raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_vehicle_registration("   ")

    def test_invalid_characters_raises_error(self):
        """Disallowed symbols like @#$ raise ValueError."""
        with pytest.raises(ValueError, match="invalid characters"):
            parse_vehicle_registration("TN 09 @#$ 1234")


# ------------------------------------------------------------------------------
# 2. Calculation Modes & Letter Mapping Tests
# ------------------------------------------------------------------------------

class TestVehicleCalculationModes:
    def test_digits_only_mode(self):
        """Verify digits_only mode sums strictly numeric registration digits."""
        # '1234' -> 1+2+3+4 = 10 -> 1+0 = 1
        res = analyze_vehicle_mode("1234", "digits_only", "Numeric Digits Only", convention="chaldean")
        assert res["compound_sum"] == 10
        assert res["root_number"] == 1
        assert res["single_root"] == 1
        assert res["is_master"] is False
        assert len(res["character_mappings"]) == 4

    def test_numeric_all_mode(self):
        """Verify numeric_all sums RTO digits + registration digits."""
        # RTO '09' + Digits '1234' = '091234' -> 0+9+1+2+3+4 = 19 -> 1+9 = 10 -> 1
        res = analyze_vehicle_mode("091234", "numeric_all", "Numeric Prefix + Digits", convention="chaldean")
        assert res["compound_sum"] == 19
        assert res["root_number"] == 1
        assert res["single_root"] == 1

    def test_pythagorean_vs_chaldean_full_alphanumeric(self):
        """Verify difference between Pythagorean and Chaldean mapping on letters."""
        # Plate: 'TN09AB1234'
        # Letters: T, N, A, B
        # Pythagorean: T=2, N=5, A=1, B=2. Digits: 0, 9, 1, 2, 3, 4
        # Pyth Sum: 2 + 5 + 0 + 9 + 1 + 2 + 1 + 2 + 3 + 4 = 29 -> 11 (Master!)
        res_pyth = analyze_vehicle_mode("TN09AB1234", "full_alphanumeric", "Full Plate", convention="pythagorean")
        assert res_pyth["compound_sum"] == 29
        assert res_pyth["root_number"] == 11
        assert res_pyth["is_master"] is True

        # Chaldean: T=4, N=5, A=1, B=2. Digits: 0, 9, 1, 2, 3, 4
        # Chald Sum: 4 + 5 + 0 + 9 + 1 + 2 + 1 + 2 + 3 + 4 = 31 -> 4
        res_chald = analyze_vehicle_mode("TN09AB1234", "full_alphanumeric", "Full Plate", convention="chaldean")
        assert res_chald["compound_sum"] == 31
        assert res_chald["root_number"] == 4
        assert res_chald["is_master"] is False


# ------------------------------------------------------------------------------
# 3. Pattern Detection & Vanity Score Tests
# ------------------------------------------------------------------------------

class TestVehiclePatternsAndVanity:
    def test_single_digit_vip(self):
        """Verify single digit VIP numbers (0001, 0007) receive high vanity scores."""
        pat = analyze_vehicle_patterns("0001")
        assert pat["is_vip_number"] is True
        assert pat["vanity_score"] >= 85.0
        assert any("Single Digit" in t for t in pat["pattern_tags"])

    def test_quad_repetition(self):
        """Verify quad repeats (9999) receive top vanity scores."""
        pat = analyze_vehicle_patterns("9999")
        assert pat["is_vip_number"] is True
        assert pat["vanity_score"] >= 85.0
        assert any("VIP Quad" in t for t in pat["pattern_tags"])

    def test_ascending_sequence(self):
        """Verify ascending sequence (1234)."""
        pat = analyze_vehicle_patterns("1234")
        assert pat["is_ascending"] is True
        assert any("Ascending" in t for t in pat["pattern_tags"])

    def test_mirror_palindrome(self):
        """Verify mirror numbers (1221, 8008)."""
        pat = analyze_vehicle_patterns("1221")
        assert pat["is_mirror"] is True
        assert any("Mirror" in t for t in pat["pattern_tags"])

    def test_twin_rhythm(self):
        """Verify twin rhythm patterns (1212)."""
        pat = analyze_vehicle_patterns("1212")
        assert any("Twin Rhythm" in t for t in pat["pattern_tags"])


# ------------------------------------------------------------------------------
# 4. Usage Archetype & Driver Alignment Tests
# ------------------------------------------------------------------------------

class TestVehicleUsageAndDriverAlignment:
    def test_vehicle_usage_harmony(self):
        """Verify personal, family, commercial, and fleet usage scoring."""
        # Root 1 with personal use (Sun is primary for personal executive)
        usage_res = evaluate_vehicle_usage_harmony(vehicle_root=1, usage_type="personal")
        assert usage_res["score"] == 95.0
        assert "Optimal" in usage_res["level"]

        # Root 8 with fleet transport (Saturn is primary for heavy fleet)
        fleet_res = evaluate_vehicle_usage_harmony(vehicle_root=8, usage_type="fleet")
        assert fleet_res["score"] == 95.0

    def test_driver_dob_compatibility(self):
        """Verify driver Psychic and Life Path calculation and scoring."""
        # Driver born 1994-06-15: Day 15 -> Psychic 6 (Venus)
        # Vehicle root: 6
        res = evaluate_single_driver_compatibility(vehicle_root=6, birth_date_str="1994-06-15", name="Gokul")
        assert res["psychic_number"] == 6
        assert res["personal_score"] >= 80.0
        assert res["level"] in ("Harmonious", "Complementary")


# ------------------------------------------------------------------------------
# 5. Candidate Ranking & Multi-Vehicle Evaluation Tests
# ------------------------------------------------------------------------------

class TestVehicleCandidateRanking:
    def test_candidate_ranking_and_deduplication(self):
        """Verify multi-candidate list ranks candidates by composite score and removes duplicates."""
        candidates = [
            "TN 09 AB 1234",
            "TN09AB1234",  # duplicate in compact form
            "KA 01 MG 9999",  # VIP Quad
            "DL 3C AB 0001",  # Super VIP Single
            "MH 12 CD 3456",  # Ascending
        ]
        results = evaluate_vehicle_candidates(
            candidates_list=candidates,
            calculation_mode="digits_only",
            convention="chaldean",
            vehicle_usage="personal",
            primary_birth_date="1994-06-15",
            max_candidates=25,
        )

        assert len(results) == 4  # 5 minus 1 duplicate
        # Top candidates should have high vanity/composite scores
        assert results[0]["composite_score"] >= results[1]["composite_score"]
        assert results[1]["composite_score"] >= results[2]["composite_score"]

    def test_max_candidates_limit_enforced(self):
        """Verify max_candidates boundary."""
        candidates = [f"TN 01 AB {i:04d}" for i in range(1, 35)]
        results = evaluate_vehicle_candidates(candidates_list=candidates, max_candidates=10)
        assert len(results) == 10


# ------------------------------------------------------------------------------
# 6. End-to-End Orchestration & API Endpoint Tests
# ------------------------------------------------------------------------------

class TestVehicleStudioAPI:
    def test_full_vehicle_numerology_orchestration(self):
        """Verify analyze_vehicle_numerology_full pipeline output."""
        res = analyze_vehicle_numerology_full(
            registration_number="TN 09 AB 1234",
            convention="chaldean",
            calculation_mode="digits_only",
            vehicle_usage="personal",
            primary_birth_date="1994-06-15",
            primary_owner_name="Gokul",
            co_owners=[{"name": "Co-Driver", "birth_date": "1996-03-22", "role": "Spouse"}],
            candidate_numbers=["KA 01 9999"],
        )

        assert res["state_code"] == "TN"
        assert res["rto_code"] == "09"
        assert res["series_letters"] == "AB"
        assert res["numeric_digits"] == "1234"
        assert res["primary_analysis"]["calculation_mode"] == "digits_only"
        assert res["digits_only_analysis"]["root_number"] == 1
        assert len(res["owner_alignments"]) == 2
        assert res["overall_owner_score"] is not None
        assert len(res["candidates"]) == 1
        assert "disclaimer" in res

    def test_api_vehicle_analyze_endpoint_success(self):
        """Test POST /api/v1/numerology/vehicle/analyze."""
        payload = {
            "registration_number": "MH 12 CD 5678",
            "system_convention": "chaldean",
            "calculation_mode": "digits_only",
            "vehicle_usage": "commercial",
            "primary_birth_date": "1990-10-25",
            "candidate_numbers": ["MH 12 CD 1111"],
        }
        response = client.post("/api/v1/numerology/vehicle/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["state_code"] == "MH"
        assert data["rto_code"] == "12"
        assert data["series_letters"] == "CD"
        assert data["numeric_digits"] == "5678"
        assert data["vehicle_usage"] == "commercial"
        assert data["usage_alignment"]["vehicle_usage"] == "commercial"
        assert len(data["candidates"]) == 1

    def test_api_vehicle_validation_error(self):
        """Test invalid registration number returns 422."""
        payload = {
            "registration_number": "$$$$$",  # No valid characters
        }
        response = client.post("/api/v1/numerology/vehicle/analyze", json=payload)
        assert response.status_code == 422
