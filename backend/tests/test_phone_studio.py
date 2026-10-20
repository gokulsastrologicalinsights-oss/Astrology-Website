"""Comprehensive test suite for Phase 4: Phone & Mobile Number Numerology Analyzer."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.numerology.phone_studio import (
    normalize_phone_number,
    mask_phone_number,
    calculate_single_phone_numerology,
    analyze_patterns_and_rhythm,
    evaluate_phone_dob_compatibility,
    evaluate_phone_industry_compatibility,
    evaluate_phone_candidates,
    analyze_phone_numerology_full,
    COMMON_COUNTRY_CODES,
    DIGIT_VIBRATION_MEANINGS,
)

client = TestClient(app)


class TestPhoneNormalizationAndPrivacy:
    """Test phone string parsing, ITU-T bounds, country code extraction, and privacy masking."""

    def test_indian_10_digit_mobile_standard(self):
        res = normalize_phone_number("9876543210")
        assert res["national_number"] == "9876543210"
        assert res["formatted_national"] == "98765 43210"
        assert res["is_indian_mobile"] is True
        assert res["detected_country_code"] == "91"

    def test_indian_mobile_with_country_code_plus(self):
        res = normalize_phone_number("+91 98765-43210")
        assert res["national_number"] == "9876543210"
        assert res["detected_country_code"] == "91"
        assert res["detected_country_name"] == "India"
        assert res["is_indian_mobile"] is True
        assert res["display_international"] == "+91 98765 43210"

    def test_indian_mobile_with_trunk_zero(self):
        res = normalize_phone_number("09876543210")
        assert res["national_number"] == "9876543210"
        assert res["is_indian_mobile"] is True

    def test_international_us_number(self):
        res = normalize_phone_number("+1 (555) 234-5678")
        assert res["detected_country_code"] == "1"
        assert res["detected_country_name"] == "USA / Canada"
        assert res["national_number"] == "5552345678"
        assert res["is_indian_mobile"] is False

    def test_international_singapore_number(self):
        res = normalize_phone_number("+65 9123 4567")
        assert res["detected_country_code"] == "65"
        assert res["detected_country_name"] == "Singapore"
        assert res["national_number"] == "91234567"

    def test_privacy_masking(self):
        masked_int = mask_phone_number("+91 98765 43210")
        assert masked_int.startswith("+91")
        assert masked_int.endswith("210")
        assert "*" in masked_int
        assert "765" not in masked_int

        masked_nat = mask_phone_number("9876543210")
        assert masked_nat.startswith("98")
        assert masked_nat.endswith("10")
        assert "*" in masked_nat

    def test_invalid_and_out_of_bounds_numbers(self):
        # Empty
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_phone_number("   ")

        # Non-phone alphabetic characters
        with pytest.raises(ValueError, match="invalid characters"):
            normalize_phone_number("98765CALLME")

        # Too short (< 7 digits)
        with pytest.raises(ValueError, match="too short"):
            normalize_phone_number("12345")

        # Too long (> 15 digits)
        with pytest.raises(ValueError, match="exceeds ITU-T E.164"):
            normalize_phone_number("12345678901234567")


class TestPhoneNumerologyCalculationsAndPatterns:
    """Test digit sums, frequencies, zero significance, and sequence/rhythm scoring."""

    def test_digit_sum_and_reduction(self):
        # 9876543210 -> sum: 45 -> 4+5 = 9
        res = calculate_single_phone_numerology("9876543210")
        assert res["compound_sum"] == 45
        assert res["root_number"] == 9
        assert res["single_root"] == 9
        assert "Mars" in res["ruling_planet"]
        assert res["zero_count"] == 1
        assert res["frequencies"]["0"] == 1
        assert res["frequencies"]["9"] == 1
        # All digits 0-9 are present exactly once, so missing_digits is empty
        assert res["missing_digits"] == []

    def test_repeated_digits_and_missing_digits(self):
        # Number with repeats: 9988776655
        res = calculate_single_phone_numerology("9988776655")
        assert res["frequencies"]["9"] == 2
        assert res["frequencies"]["8"] == 2
        assert res["frequencies"]["7"] == 2
        assert res["frequencies"]["6"] == 2
        assert res["frequencies"]["5"] == 2
        assert res["frequencies"]["1"] == 0
        assert res["frequencies"]["0"] == 0
        assert 1 in res["missing_digits"]
        assert 2 in res["missing_digits"]
        assert 3 in res["missing_digits"]
        assert 4 in res["missing_digits"]
        assert res["zero_count"] == 0

    def test_vip_vanity_triplets_and_runs(self):
        # VIP number: 9991237777
        patterns = analyze_patterns_and_rhythm("9991237777")
        assert patterns["vanity_score"] > 75.0
        assert patterns["is_vip_vanity"] is True

        repeats = patterns["repeats"]
        assert any(r["pattern"] == "999" for r in repeats)
        assert any(r["pattern"] == "7777" for r in repeats)

        seqs = patterns["sequences"]
        assert any(s["sequence"] == "123" for s in seqs)

    def test_master_number_preservation(self):
        # 29 -> 2+9 = 11 (Master number)
        # Digits that sum to 11: 335 -> 11
        res = calculate_single_phone_numerology("335", preserve_master=True)
        assert res["compound_sum"] == 11
        assert res["root_number"] == 11
        assert res["is_master"] is True
        assert res["single_root"] == 2


class TestProfileAndIndustryCompatibility:
    """Test personal DOB alignment and industry sector resonance."""

    def test_dob_compatibility_calculation(self):
        # Phone root 1 (Sun), DOB 1994-06-15 (Day 15 -> 6 Venus, Life Path -> 8 Saturn)
        # 1 vs 6 is traditionally challenging/incompatible
        res = evaluate_phone_dob_compatibility(phone_root=1, birth_date_str="1994-06-15")
        assert res["psychic_number"] == 6
        assert res["life_path_number"] == 8
        assert "personal_score" in res
        assert res["personal_score"] >= 0.0

    def test_industry_compatibility_calculation(self):
        # Tech primary numbers: 5, 1
        res_tech_5 = evaluate_phone_industry_compatibility(phone_root=5, industry_category="technology")
        assert res_tech_5["score"] == 100.0
        assert "Primary Industry Match" in res_tech_5["description"]

        # Finance primary numbers: 8, 3, 5
        res_fin_8 = evaluate_phone_industry_compatibility(phone_root=8, industry_category="finance")
        assert res_fin_8["score"] == 100.0


class TestCandidateRankingAndDeterminism:
    """Test multi-candidate comparison and ranking order."""

    def test_candidate_ranking_order(self):
        candidates = [
            "9876543210", # standard
            "9999988888", # high repeat / VIP vanity
            "9123456780", # runs 12345678
            "9840123456",
        ]
        ranked = evaluate_phone_candidates(
            candidates_list=candidates,
            industry_category="technology",
            birth_date="1995-05-14",
            max_candidates=10,
        )
        assert len(ranked) == 4
        # Verify sorted descending by composite_score
        for i in range(len(ranked) - 1):
            assert ranked[i]["composite_score"] >= ranked[i + 1]["composite_score"]

    def test_candidate_deduplication(self):
        candidates = [
            "+91 98765 43210",
            "9876543210",
            "09876543210",
        ]
        ranked = evaluate_phone_candidates(candidates_list=candidates)
        # All three resolve to same national subscriber number 9876543210
        assert len(ranked) == 1


class TestAPIEndpointsAndValidation:
    """Test FastAPI endpoint validation, responses, and error handling."""

    def test_api_phone_analyze_success(self):
        payload = {
            "phone_number": "+91 98765 43210",
            "system_convention": "chaldean",
            "include_country_code": False,
            "birth_date": "1994-06-15",
            "industry_category": "technology",
            "candidate_numbers": ["+91 98765 43211", "9999988888"],
            "language": "en",
        }
        response = client.post("/api/v1/numerology/phone/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["national_number"] == "9876543210"
        assert data["is_indian_mobile"] is True
        assert data["detected_country_name"] == "India"
        assert data["primary_analysis"]["compound_sum"] == 45
        assert data["primary_analysis"]["root_number"] == 9
        assert data["personal_compatibility"] is not None
        assert data["industry_compatibility"] is not None
        assert len(data["candidates"]) >= 2
        assert "scoring_explanation" in data

    def test_api_validation_invalid_phone_formatting(self):
        # Letters inside phone number
        response = client.post(
            "/api/v1/numerology/phone/analyze",
            json={"phone_number": "+91 98765HELLO"},
        )
        assert response.status_code == 422

    def test_api_validation_too_short_phone(self):
        response = client.post(
            "/api/v1/numerology/phone/analyze",
            json={"phone_number": "12345"},
        )
        assert response.status_code == 422

    def test_api_metadata_includes_phone(self):
        response = client.get("/api/v1/numerology/metadata")
        assert response.status_code == 200
        data = response.json()
        method_ids = [m["id"] for m in data["methods"]]
        assert "phone" in method_ids
        assert len(data["methods"]) >= 6

