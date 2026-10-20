"""Unit and Integration Tests for Family & Baby Numerology Studio.

Verifies:
1. Family member profile computations across generational roles (parents, children, grandparents).
2. Graceful fallback for missing birth dates or missing names.
3. Baby name candidate evaluation (Pythagorean & Chaldean), deterministic variations, and harmonic scoring.
4. Pairwise family compatibility dynamics and nurturing/parenting guidance.
5. Family-wide vibrational frequency distribution, dominant/missing numbers, and elemental balance.
6. API endpoint POST /api/v1/numerology/family/analyze.
7. Report schema validation for method='family'.
8. Bilingual PDF generation with ReportLab.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.family_studio import (
    compute_family_member_profile,
    evaluate_family_pair,
    evaluate_baby_name_candidates,
    analyze_family_numerology_full,
    ELEMENT_MAP,
)
from app.services.numerology.pdf_generator import generate_numerology_pdf_bytes
from app.schemas.numerology import SaveNumerologyReportRequest, FamilyNumerologyRequest

client = TestClient(app)


class TestFamilyMemberProfile:
    def test_complete_member_profile(self):
        """Verify full member profile computation with name, DOB, and relationship."""
        profile = compute_family_member_profile(
            member_id="m1",
            name="Aravind",
            relationship="father",
            birth_date="1988-03-14",
            convention="pythagorean",
            language="en",
        )
        assert profile["id"] == "m1"
        assert profile["name"] == "Aravind"
        assert profile["relationship"] == "father"
        # 14 -> 1+4 = 5
        assert profile["birth_psychic_number"] == 5
        assert profile["birth_psychic_planet"] == "Mercury (Budha)"
        # 1988-03-14: 1+9+8+8=26->8, 03->3, 14->5. 8+3+5=16->7
        assert profile["life_path_number"] == 7
        assert profile["expression_number"] is not None
        assert profile["element"] in ["Earth", "Water", "Fire", "Air"]
        assert "archetype_label" in profile
        assert profile["has_birth_data"] is True
        assert profile["has_name_data"] is True

    def test_dob_only_member_profile(self):
        """Verify profile handles missing name gracefully."""
        profile = compute_family_member_profile(
            member_id="m2",
            name="",
            relationship="baby",
            birth_date="2026-05-10",
            convention="chaldean",
            language="en",
        )
        assert profile["name"] == "Baby"
        # 10th -> 1
        assert profile["birth_psychic_number"] == 1
        assert profile["expression_number"] is None
        assert profile["has_birth_data"] is True
        assert profile["has_name_data"] is False

    def test_name_only_member_profile(self):
        """Verify profile handles missing DOB gracefully."""
        profile = compute_family_member_profile(
            member_id="m3",
            name="Deepa",
            relationship="mother",
            birth_date=None,
            convention="pythagorean",
            language="en",
        )
        assert profile["birth_psychic_number"] is None
        assert profile["life_path_number"] is None
        assert profile["expression_number"] is not None
        assert profile["has_birth_data"] is False
        assert profile["has_name_data"] is True


class TestBabyNameCandidates:
    def test_baby_name_candidate_scoring(self):
        """Verify candidate ranking with parent numbers and target DOB."""
        candidates = ["Aarav", "Advik", "Ananya"]
        parent_vibrations = [5, 7, 3]  # e.g., Father=5, Mother=3, LP=7
        results = evaluate_baby_name_candidates(
            candidates=candidates,
            baby_birth_date="2026-06-15",
            parent_vibrations=parent_vibrations,
            convention="pythagorean",
            auto_generate_variations=True,
            target_root=6,
            language="en",
        )
        assert len(results) >= 3
        top = results[0]
        assert "candidate_name" in top
        assert "pythagorean_expression" in top
        assert "chaldean_expression" in top
        assert "composite_score" in top
        assert 0 <= top["composite_score"] <= 100
        assert 0 <= top["dob_harmony_score"] <= 100
        assert 0 <= top["parents_harmony_score"] <= 100

    def test_baby_name_variations_flag(self):
        """Verify variations are generated when toggle is enabled."""
        base_name = ["Kavin"]
        res_with = evaluate_baby_name_candidates(
            candidates=base_name,
            baby_birth_date=None,
            parent_vibrations=[1],
            convention="pythagorean",
            auto_generate_variations=True,
        )
        res_without = evaluate_baby_name_candidates(
            candidates=base_name,
            baby_birth_date=None,
            parent_vibrations=[1],
            convention="pythagorean",
            auto_generate_variations=False,
        )
        assert len(res_with) >= len(res_without)
        assert len(res_without) == 1


class TestFamilyPairwiseAndDistribution:
    def test_pairwise_harmony_evaluation(self):
        """Verify relationship between father and child."""
        father = compute_family_member_profile("1", "Karthik", "father", "1985-04-10")
        child = compute_family_member_profile("2", "Siddharth", "son", "2018-09-15")

        pair = evaluate_family_pair(father, child, language="en")
        assert pair["member_a_name"] == "Karthik"
        assert pair["member_b_name"] == "Siddharth"
        assert pair["relationship_type"] == "parent-child"
        assert 0 <= pair["compatibility_score"] <= 100
        assert pair["harmony_level"] in ["Exceptional", "Harmonious", "Dynamic Growth", "Neutral"]
        assert len(pair["shared_strengths"]) > 0
        assert len(pair["growth_edges"]) > 0
        assert len(pair["parenting_dialogue_prompt"]) > 0

    def test_full_family_analysis_distribution(self):
        """Verify frequency distribution and elemental balance for a 4-person family."""
        members_input = [
            {"id": "1", "name": "Rajesh", "relationship": "father", "birth_date": "1984-01-19"},
            {"id": "2", "name": "Meena", "relationship": "mother", "birth_date": "1986-07-25"},
            {"id": "3", "name": "Diya", "relationship": "daughter", "birth_date": "2015-11-03"},
            {"id": "4", "name": "Baby", "relationship": "baby", "birth_date": "2026-02-14"},
        ]
        result = analyze_family_numerology_full(
            family_name="Rajesh Family",
            members_data=members_input,
            baby_candidates=["Aditya", "Rohan"],
            auto_generate_variations=False,
            convention="pythagorean",
            language="en",
        )
        assert result["family_name"] == "Rajesh Family"
        assert len(result["members"]) == 4
        assert len(result["pairwise_dynamics"]) == 6  # 4 choose 2 = 6 pairs
        assert len(result["distribution"]) == 9       # Numbers 1 through 9
        assert isinstance(result["dominant_vibrations"], list)
        assert isinstance(result["missing_vibrations"], list)
        assert "elemental_balance" in result
        assert "Fire" in result["elemental_balance"]
        assert "Water" in result["elemental_balance"]
        assert "Air" in result["elemental_balance"]
        assert "Earth" in result["elemental_balance"]
        assert len(result["reflection_prompts"]) > 0
        assert 0 <= result["family_harmony_score"] <= 100


class TestFamilyStudioAPIEndpoint:
    def test_api_family_analyze_success(self):
        """Test POST /api/v1/numerology/family/analyze with valid payload."""
        payload = {
            "family_name": "Sundaram Family",
            "members": [
                {"id": "1", "name": "Sundaram", "relationship": "father", "birth_date": "1980-05-12"},
                {"id": "2", "name": "Lakshmi", "relationship": "mother", "birth_date": "1983-08-22"},
            ],
            "baby_candidates": ["Kavya", "Madhav"],
            "target_root_number": 6,
            "auto_generate_variations": True,
            "system_convention": "pythagorean",
            "language": "en",
        }
        res = client.post("/api/v1/numerology/family/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["family_name"] == "Sundaram Family"
        assert len(data["members_evaluated"]) == 2
        assert len(data["pairwise_comparisons"]) == 1
        assert len(data["baby_name_candidates"]) >= 2
        assert len(data["number_distribution"]) == 9
        assert data["overall_family_harmony_score"] >= 0

    def test_api_family_analyze_tamil(self):
        """Test POST /api/v1/numerology/family/analyze with Tamil language."""
        payload = {
            "family_name": "முருகன் குடும்பம்",
            "members": [
                {"id": "1", "name": "முருகன்", "relationship": "father", "birth_date": "1985-10-15"},
            ],
            "baby_candidates": ["செந்தில்"],
            "language": "ta",
        }
        res = client.post("/api/v1/numerology/family/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["members_evaluated"]) == 1
        assert data["members_evaluated"][0]["name"] == "முருகன்"

    def test_saved_report_schema_allows_family(self):
        """Verify SaveNumerologyReportRequest validates method='family'."""
        req = SaveNumerologyReportRequest(
            person_name="Sundaram Family",
            birth_date="2026-01-01",
            method="family",
            system_convention="pythagorean",
            calculation_data={"family_name": "Sundaram Family", "members": []},
            interpretation_data={"overall_synthesis": "Harmonious family matrix"},
        )
        assert req.method == "family"


class TestFamilyPDFExport:
    def test_family_pdf_generation(self):
        """Verify PDF bytes generation for family report."""
        members_input = [
            {"id": "1", "name": "Ravi", "relationship": "father", "birth_date": "1982-11-20"},
            {"id": "2", "name": "Priya", "relationship": "mother", "birth_date": "1985-04-18"},
        ]
        analysis = analyze_family_numerology_full(
            family_name="Ravi & Priya Family",
            members_data=members_input,
            baby_candidates=["Arun", "Tara"],
            convention="pythagorean",
            language="en",
        )
        pdf_bytes = generate_numerology_pdf_bytes(
            report_id="fam-test-123",
            person_name="Ravi & Priya Family",
            birth_date="2026-01-01",
            method="family",
            system_convention="pythagorean",
            language="en",
            calculation_data=analysis,
            interpretation_data={"overall_synthesis": analysis["overall_synthesis"]},
            display_number=101,
        )
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
