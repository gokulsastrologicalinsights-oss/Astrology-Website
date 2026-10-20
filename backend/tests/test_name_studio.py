"""Unit & Integration Tests for Name Suggestion and Correction Studio.

Verifies:
1. Multi-component name analysis (first, middle, surname, initials).
2. Pythagorean and Chaldean system calculations and distinctions.
3. Candidate spelling variation generation (consonants, vowels, phonetics, transliterations).
4. Candidate deduplication and maximum bounds enforcement.
5. Multi-dimensional scoring (Numerological harmony, pronunciation preservation, simplicity).
6. Target number matching & ranking determinism.
7. Automatic target derivation from birth date (Mulank/Bhagyank).
8. Tamil name support and Unicode transliteration.
9. Input validation constraints (empty, punctuation-only, invalid targets, excessive limits).
10. API endpoints (/api/v1/numerology/name/analyze, /api/v1/numerology/name/suggest-corrections).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.name_studio import (
    analyze_name_components,
    generate_candidate_spellings,
    generate_and_score_name_corrections,
    assess_number_harmony,
    calculate_pronunciation_preservation,
    calculate_spelling_simplicity,
    levenshtein_distance,
)

client = TestClient(app)


class TestNameStudioComponentsAndCalculations:
    def test_name_component_analysis_full(self):
        """Verify full name, first name, middle name, surname, and initials breakdown."""
        name = "Gokul Anand Murugan"
        res = analyze_name_components(name, convention="pythagorean")

        assert res["full_name"] == name
        assert res["convention"] == "pythagorean"
        assert 1 <= res["expression"] <= 33
        assert 1 <= res["soul_urge"] <= 33
        assert 1 <= res["personality"] <= 33

        # Components breakdown check
        comp_types = [c["component_type"] for c in res["components"]]
        assert "First Name" in comp_types
        assert "Middle Name(s)" in comp_types
        assert "Surname / Last Name" in comp_types
        assert "Initials Only" in comp_types

        first_comp = next(c for c in res["components"] if c["component_type"] == "First Name")
        assert first_comp["text"] == "Gokul"
        assert first_comp["expression"] > 0

    def test_pythagorean_vs_chaldean_name_analysis(self):
        """Verify differences in calculation between Pythagorean and Chaldean systems."""
        name = "Gokul Murugan"
        res_pyth = analyze_name_components(name, convention="pythagorean")
        res_chald = analyze_name_components(name, convention="chaldean")

        assert res_pyth["expression"] != res_chald["expression"] or res_pyth["compound_expression"] != res_chald["compound_expression"]
        assert res_pyth["convention"] == "pythagorean"
        assert res_chald["convention"] == "chaldean"

    def test_single_word_name(self):
        """Test single-word name analysis without middle name or surname errors."""
        name = "Gokul"
        res = analyze_name_components(name, convention="chaldean")
        assert res["expression"] > 0
        first_comp = next(c for c in res["components"] if c["component_type"] == "First Name")
        assert first_comp["text"] == "Gokul"


class TestCandidateGenerationAndDeduplication:
    def test_consonant_doubling_variations(self):
        """Verify consonant doubling and de-doubling candidate generation."""
        variations = generate_candidate_spellings(
            "Gokul",
            allow_consonant_doubling=True,
            allow_vowel_changes=False,
            allow_phonetic_replacements=False,
        )
        names = [v["name"] for v in variations]
        # Should generate 'Gokull' by doubling 'l'
        assert "Gokull" in names

        # De-doubling
        variations_dedouble = generate_candidate_spellings(
            "Kavithaa",
            allow_consonant_doubling=True,
            allow_vowel_changes=False,
            allow_phonetic_replacements=False,
        )
        # Should contain Kavitha or variations
        assert len(variations_dedouble) > 0

    def test_vowel_alternations(self):
        """Verify vowel substitutions like ee <-> i and oo <-> u."""
        variations = generate_candidate_spellings(
            "Praveen",
            allow_vowel_changes=True,
            allow_consonant_doubling=False,
            allow_phonetic_replacements=False,
        )
        names = [v["name"] for v in variations]
        assert "Pravin" in names

        variations_oo = generate_candidate_spellings(
            "Pooja",
            allow_vowel_changes=True,
            allow_consonant_doubling=False,
            allow_phonetic_replacements=False,
        )
        names_oo = [v["name"] for v in variations_oo]
        assert "Puja" in names_oo

    def test_phonetic_and_indic_transliteration_swaps(self):
        """Verify Indic transliteration rules (th <-> t, d <-> dh, etc.)."""
        variations = generate_candidate_spellings(
            "Karthik",
            allow_phonetic_replacements=True,
            allow_vowel_changes=False,
            allow_consonant_doubling=False,
        )
        names = [v["name"] for v in variations]
        assert "Kartik" in names

    def test_candidate_bounding_and_deduplication(self):
        """Verify strict candidate bounding and deduplication."""
        max_bound = 10
        variations = generate_candidate_spellings(
            "Gokul Anand Murugan",
            max_candidates=max_bound,
        )
        assert len(variations) <= max_bound
        # Check uniqueness
        names = [v["name"].lower() for v in variations]
        assert len(names) == len(set(names))


class TestScoringAndRanking:
    def test_levenshtein_and_pronunciation_score(self):
        """Verify pronunciation preservation scoring."""
        # Exact match
        assert calculate_pronunciation_preservation("Gokul", "Gokul") == 100.0
        # Very close single letter doubling
        score_doubled = calculate_pronunciation_preservation("Gokul", "Gokull")
        assert score_doubled >= 85.0
        # Completely different name should have low score
        score_diff = calculate_pronunciation_preservation("Gokul", "Alexander")
        assert score_diff < 40.0

    def test_spelling_simplicity_penalties(self):
        """Verify triple-repeat penalties."""
        clean_score = calculate_spelling_simplicity("Gokul", "Gokull")
        assert clean_score >= 90.0
        # Triple consonant 'lll'
        triple_score = calculate_spelling_simplicity("Gokul", "Gokulll")
        assert triple_score < clean_score

    def test_harmony_scoring(self):
        """Verify numerical harmony evaluation."""
        # Exact match
        score, desc = assess_number_harmony(1, 1)
        assert score == 100.0
        assert "Exact" in desc

        # Sun (1) and Mars (9) are friends
        score_friend, _ = assess_number_harmony(9, 1)
        assert score_friend >= 80.0

        # Sun (1) and Saturn (8) are traditional enemies
        score_enemy, _ = assess_number_harmony(8, 1)
        assert score_enemy <= 40.0

    def test_suggest_corrections_with_explicit_target(self):
        """Verify candidate suggestions prioritize exact target match."""
        target = 1
        res = generate_and_score_name_corrections(
            original_name="Gokul",
            convention="chaldean",
            target_number=target,
            max_candidates=20,
        )

        assert res["target_number"] == target
        assert len(res["candidates"]) > 0

        # Any candidate matching target should have matches_target=True and harmony_score=100
        matching = [c for c in res["candidates"] if c["expression_number"] == target]
        for m in matching:
            assert m["matches_target"] is True
            assert m["harmony_score"] == 100.0

    def test_suggest_corrections_with_dob_auto_target(self):
        """Verify birth date auto-derives target from Psychic Number (Mulank)."""
        # 1990-10-15: Day 15 -> 1+5 = 6 (Venus)
        res = generate_and_score_name_corrections(
            original_name="Gokul",
            convention="chaldean",
            birth_date="1990-10-15",
            max_candidates=15,
        )
        assert res["target_number"] == 6
        assert "Psychic Number" in res["target_source"]


class TestTamilAndUnicodeSupport:
    def test_tamil_name_analysis(self):
        """Verify Tamil script name is analyzed correctly without throwing errors."""
        tamil_name = "கோகுல்"
        res = analyze_name_components(tamil_name, convention="chaldean")
        assert res["expression"] > 0
        assert len(res["letter_mappings"]) > 0

    def test_tamil_name_in_correction_studio(self):
        """Verify Tamil name can run through the suggestion studio."""
        res = generate_and_score_name_corrections(
            original_name="கோகுல்",
            convention="chaldean",
            custom_variations=["கோகுலன்"],
            max_candidates=10,
        )
        assert len(res["candidates"]) >= 1
        assert res["target_number"] > 0


class TestAPIEndpointsAndValidation:
    def test_api_name_analyze_success(self):
        """Test POST /api/v1/numerology/name/analyze endpoint."""
        payload = {
            "full_name": "Gokul Murugan",
            "system_convention": "chaldean",
            "language": "en",
        }
        response = client.post("/api/v1/numerology/name/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Gokul Murugan"
        assert data["convention"] == "chaldean"
        assert "components" in data
        assert len(data["components"]) >= 2

    def test_api_suggest_corrections_success(self):
        """Test POST /api/v1/numerology/name/suggest-corrections endpoint."""
        payload = {
            "original_name": "Gokul",
            "system_convention": "chaldean",
            "target_number": 5,
            "custom_variations": ["Gokhul", "Gokulll"],
            "max_candidates": 20,
        }
        response = client.post("/api/v1/numerology/name/suggest-corrections", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["original_name"] == "Gokul"
        assert data["target_number"] == 5
        assert len(data["candidates"]) > 0
        assert "scoring_explanation" in data

    def test_api_validation_empty_or_punctuation_name(self):
        """Verify rejection of empty or punctuation-only names."""
        res_empty = client.post("/api/v1/numerology/name/analyze", json={"full_name": "   "})
        assert res_empty.status_code == 422

        res_punct = client.post("/api/v1/numerology/name/analyze", json={"full_name": "...---!!!"})
        assert res_punct.status_code == 422

    def test_api_validation_invalid_target_or_excessive_limit(self):
        """Verify rejection of invalid target numbers and excessive candidate limits."""
        # Invalid target 15 (only 1-9, 11, 22, 33 allowed)
        res_bad_target = client.post(
            "/api/v1/numerology/name/suggest-corrections",
            json={"original_name": "Gokul", "target_number": 15},
        )
        assert res_bad_target.status_code == 422

        # Excessive limit > 50
        res_bad_limit = client.post(
            "/api/v1/numerology/name/suggest-corrections",
            json={"original_name": "Gokul", "max_candidates": 100},
        )
        assert res_bad_limit.status_code == 422
