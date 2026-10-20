"""Unit and Integration Tests for Marriage Compatibility by Numerology Studio.

Verifies:
1. Individual profile calculations for Person A and Person B.
2. Missing and invalid birth dates validation.
3. Optional names and initials handling.
4. Pythagorean vs. Chaldean calculation conventions.
5. Master numbers (11, 22, 33) and Karmic Debt numbers (13, 14, 16, 19) detection.
6. Transparent compatibility formula determinism and weights.
7. Graceful fallback when name-derived numbers are omitted (DOB-only mode).
8. API endpoint POST /api/v1/numerology/marriage/analyze.
9. Saved-report validation with method='marriage'.
10. Tamil & Unicode script support.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.marriage_studio import (
    compute_single_person_profile,
    score_pair_compatibility,
    generate_relationship_themes,
    analyze_marriage_numerology_full,
)
from app.schemas.numerology import SaveNumerologyReportRequest

client = TestClient(app)


class TestMarriageNumerologyCalculations:
    def test_single_person_profile_complete(self):
        """Verify complete individual profile computation with name and date of birth."""
        profile = compute_single_person_profile(
            full_name="Gokul Murugan",
            birth_date="1995-06-15",
            preferred_name="Gokul",
            surname_initials="M",
            convention="pythagorean",
            language="en",
            person_label="Person A",
        )
        assert profile["person_label"] == "Person A"
        assert profile["full_name"] == "Gokul Murugan"
        assert profile["preferred_name"] == "Gokul"
        # 15th -> 1+5 = 6
        assert profile["birth_psychic_number"] == 6
        assert profile["birth_psychic_compound"] == 15
        assert profile["birth_psychic_planet"] == "Venus (Shukra)"
        # 1995-06-15 -> 1+9+9+5 = 24 -> 6, 06 -> 6, 15 -> 6. 6+6+6 = 18 -> 9
        assert profile["life_path_number"] == 9
        assert profile["expression_number"] is not None
        assert profile["soul_urge_number"] is not None
        assert profile["personality_number"] is not None
        assert isinstance(profile["master_numbers"], list)
        assert isinstance(profile["karmic_debts"], list)
        assert len(profile["key_attributes"]) > 0

    def test_single_person_profile_without_name(self):
        """Verify profile handles omitted name gracefully, computing only birth numbers."""
        profile = compute_single_person_profile(
            full_name=None,
            birth_date="1996-09-22",
            convention="pythagorean",
            language="en",
            person_label="Person B",
        )
        assert profile["full_name"] is None
        # 22nd -> psychic number 4 (2+2), raw day 22 (master 22 detected in day)
        assert profile["birth_psychic_number"] == 4
        assert profile["birth_psychic_compound"] == 22
        assert 22 in profile["master_numbers"]
        assert profile["expression_number"] is None
        assert profile["soul_urge_number"] is None
        assert profile["personality_number"] is None

    def test_pythagorean_vs_chaldean_difference(self):
        """Verify that name calculations yield different conventions under Pythagorean and Chaldean."""
        pyth = compute_single_person_profile(
            full_name="Sundar Raman",
            birth_date="1990-10-25",
            convention="pythagorean",
        )
        chal = compute_single_person_profile(
            full_name="Sundar Raman",
            birth_date="1990-10-25",
            convention="chaldean",
        )
        # Date numbers are invariant to letter convention
        assert pyth["birth_psychic_number"] == chal["birth_psychic_number"]
        assert pyth["life_path_number"] == chal["life_path_number"]
        # Name numbers reflect convention differences
        assert pyth["expression_compound"] != chal["expression_compound"]

    def test_master_number_retention(self):
        """Verify master numbers 11, 22, 33 are preserved in Life Path calculations."""
        # 1975-05-29 -> Year 1975 (22/4), Month 5, Day 29 (11/2). Period total: 4+5+2 = 11 (Master)
        profile = compute_single_person_profile(
            full_name="Master Soul",
            birth_date="1975-05-29",
            convention="pythagorean",
        )
        assert profile["life_path_number"] == 11
        assert profile["is_life_path_master"] is True
        assert 11 in profile["master_numbers"]

    def test_karmic_debt_detection(self):
        """Verify karmic debt numbers (13, 14, 16, 19) are detected from day of birth."""
        profile_14 = compute_single_person_profile(
            full_name="Test Person",
            birth_date="1992-04-14",
        )
        debt_numbers = [d["number"] for d in profile_14["karmic_debts"]]
        assert 14 in debt_numbers

    def test_pair_compatibility_identical_numbers(self):
        """Verify high compatibility for identical root numbers."""
        score, level, planet, interp = score_pair_compatibility(6, 6)
        assert score >= 90.0
        assert "Venus" in planet
        assert "Identical Core Wavelength" in level or "Root" in level

    def test_pair_compatibility_friendly_numbers(self):
        """Verify friendly planetary alliance (e.g. 1 Sun & 9 Mars)."""
        score, level, planet, interp = score_pair_compatibility(1, 9)
        assert score >= 80.0
        assert "Sun" in planet and "Mars" in planet

    def test_pair_compatibility_contrasting_numbers(self):
        """Verify contrasting polarities (e.g. 1 Sun & 8 Saturn)."""
        score, level, planet, interp = score_pair_compatibility(1, 8)
        assert score <= 60.0
        assert "Sun" in planet and "Saturn" in planet

    def test_relationship_themes_synthesis(self):
        """Verify synthesis of strengths, challenges, and discussion prompts."""
        prof_a = compute_single_person_profile("Alice", "1994-03-12")
        prof_b = compute_single_person_profile("Bob", "1995-07-25")
        themes = generate_relationship_themes(prof_a, prof_b, lang="en")

        assert len(themes["shared_strengths"]) >= 3
        assert len(themes["potential_challenges"]) >= 2
        assert len(themes["conversation_prompts"]) >= 3
        assert len(themes["growth_recommendations"]) >= 2

    def test_full_pipeline_with_names(self):
        """Verify full marriage compatibility pipeline with both names provided."""
        person_a = {
            "full_name": "Gokul Murugan",
            "birth_date": "1995-06-15",
            "relationship_status": "engaged",
        }
        person_b = {
            "full_name": "Ananya Sharma",
            "birth_date": "1996-09-22",
            "relationship_status": "engaged",
        }
        res = analyze_marriage_numerology_full(person_a, person_b, convention="pythagorean", language="en")

        assert res["relationship_status"] == "engaged"
        assert res["overall_score"] > 0
        assert res["scoring_formula_explanation"]["has_name_derived_comparison"] is True
        assert res["scoring_formula_explanation"]["weights"]["life_path"] == 0.40
        assert res["scoring_formula_explanation"]["weights"]["birth_psychic"] == 0.25
        assert res["scoring_formula_explanation"]["weights"]["expression"] == 0.20
        assert res["scoring_formula_explanation"]["weights"]["soul_urge"] == 0.15
        assert res["expression_compatibility"] is not None
        assert res["soul_urge_compatibility"] is not None
        assert res["personality_compatibility"] is not None
        assert len(res["disclaimer"]) > 50

    def test_full_pipeline_without_names(self):
        """Verify full marriage compatibility pipeline when names are omitted."""
        person_a = {"birth_date": "1995-06-15"}
        person_b = {"birth_date": "1996-09-22"}
        res = analyze_marriage_numerology_full(person_a, person_b, convention="chaldean", language="en")

        assert res["overall_score"] > 0
        assert res["scoring_formula_explanation"]["has_name_derived_comparison"] is False
        assert res["scoring_formula_explanation"]["weights"]["life_path"] == 0.60
        assert res["scoring_formula_explanation"]["weights"]["birth_psychic"] == 0.40
        assert res["expression_compatibility"] is None
        assert res["soul_urge_compatibility"] is None

    def test_tamil_bilingual_synthesis(self):
        """Verify Tamil output when language is 'ta'."""
        person_a = {"full_name": "கோகுல்", "birth_date": "1995-06-15"}
        person_b = {"full_name": "அனன்யா", "birth_date": "1996-09-22"}
        res = analyze_marriage_numerology_full(person_a, person_b, convention="pythagorean", language="ta")

        assert "இணக்க" in res["overall_harmony_level"] or "நிலை" in res["overall_harmony_level"] or "அதிர்வு" in res["overall_harmony_level"]
        assert len(res["conversation_prompts"]) >= 3


class TestMarriageNumerologyApiEndpoints:
    def test_marriage_analyze_endpoint_success(self):
        """Test POST /api/v1/numerology/marriage/analyze endpoint."""
        payload = {
            "person_a": {
                "full_name": "Gokul Murugan",
                "birth_date": "1995-06-15",
                "preferred_name": "Gokul",
                "relationship_status": "dating",
            },
            "person_b": {
                "full_name": "Ananya Sharma",
                "birth_date": "1996-09-22",
                "preferred_name": "Ananya",
                "relationship_status": "dating",
            },
            "system_convention": "pythagorean",
            "language": "en",
        }
        res = client.post("/api/v1/numerology/marriage/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["engine_version"] == "1.0.0"
        assert data["relationship_status"] == "dating"
        assert data["person_a_profile"]["birth_psychic_number"] == 6
        assert data["person_b_profile"]["birth_psychic_number"] == 4
        assert data["psychic_compatibility"]["score"] > 0
        assert data["life_path_compatibility"]["score"] > 0
        assert data["overall_score"] > 0
        assert len(data["conversation_prompts"]) >= 3
        assert "disclaimer" in data

    def test_marriage_analyze_validation_invalid_date(self):
        """Test that invalid birth dates fail with 422."""
        payload = {
            "person_a": {
                "full_name": "Gokul",
                "birth_date": "15-06-1995",  # Invalid, must be YYYY-MM-DD
            },
            "person_b": {
                "full_name": "Ananya",
                "birth_date": "1996-09-22",
            },
        }
        res = client.post("/api/v1/numerology/marriage/analyze", json=payload)
        assert res.status_code == 422

    def test_marriage_analyze_validation_out_of_range_year(self):
        """Test year out of range fails with 422."""
        payload = {
            "person_a": {
                "full_name": "Gokul",
                "birth_date": "1850-06-15",  # Year < 1900
            },
            "person_b": {
                "full_name": "Ananya",
                "birth_date": "1996-09-22",
            },
        }
        res = client.post("/api/v1/numerology/marriage/analyze", json=payload)
        assert res.status_code == 422

    def test_save_marriage_report_schema_validation(self):
        """Verify SaveNumerologyReportRequest validates method='marriage'."""
        req = SaveNumerologyReportRequest(
            person_name="Gokul & Ananya",
            birth_date="1995-06-15",
            method="marriage",
            system_convention="pythagorean",
            calculation_data={"overall_score": 82.5},
            interpretation_data={"synthesis": "High Harmony"},
        )
        assert req.method == "marriage"
