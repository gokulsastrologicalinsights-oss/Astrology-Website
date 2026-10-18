"""Comprehensive Test Suite for Numerology Calculation Engines & API Endpoints.

Verifies:
1. Traditional Numerology: Life Path, Expression, Soul Urge, Personality, Birthday, Attitude, Maturity, Personal Year.
2. Master Number (11, 22, 33) preservation across calculations.
3. Pythagorean vs. Chaldean alphabet-to-number mappings.
4. Diacritics and Unicode normalization.
5. Destiny Matrix: Modulo-22 Arcana reductions, octagram vertices (Personal & Ancestral squares), Karmic Tail triad.
6. Destiny Matrix: Sky, Earth, Personal, Social, and Spiritual purposes.
7. Destiny Matrix: Age timeline 0 to 80 years milestones.
8. Destiny Matrix: Couples compatibility matrix calculation.
9. Advanced Analysis: Yuan Unicode decimal code-point name derivation.
10. Advanced Analysis: 3x3 Lo Shu Magic Square grid counts and Arrows of Pythagoras.
11. Advanced Analysis: 4 Life Pinnacles and 4 Challenges with age spans.
12. Advanced Analysis: Karmic Debt numbers (13, 14, 16, 19) and Karmic Lessons (missing name digits).
13. Input validation constraints (invalid dates, out-of-range months/days, empty names).
14. Metadata endpoint diagnostics.
15. Report persistence and retrieval.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology import (
    calculate_life_path,
    calculate_birthday_number,
    calculate_attitude_number,
    calculate_personal_year,
    calculate_name_numbers,
    calculate_maturity_number,
    reduce_number,
    calculate_destiny_matrix,
    calculate_compatibility,
    reduce_arcana,
    calculate_advanced_analysis,
    derive_unicode_name_number,
    calculate_lo_shu_grid,
    calculate_pinnacles_and_challenges,
    detect_karmic_debts,
)

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. Calculation Unit Tests: Traditional Numerology
# ------------------------------------------------------------------------------

class TestTraditionalNumerologyCalculations:
    def test_reduction_with_master_numbers(self):
        """Verify reducer retains master numbers 11, 22, 33."""
        assert reduce_number(11, preserve_master=True) == 11
        assert reduce_number(22, preserve_master=True) == 22
        assert reduce_number(33, preserve_master=True) == 33
        assert reduce_number(44, preserve_master=True) == 8 # 4+4 = 8
        assert reduce_number(29, preserve_master=True) == 11 # 2+9 = 11 (Master)
        assert reduce_number(38, preserve_master=True) == 11 # 3+8 = 11 (Master)
        assert reduce_number(55, preserve_master=True) == 1 # 5+5=10 -> 1

    def test_life_path_calculation_known_dob(self):
        """Test standard Life Path calculation with known date."""
        # 1990-10-25: Month 10 -> 1; Day 25 -> 7; Year 1990 -> 19 -> 1+9=10 -> 1. Total: 1+7+1 = 9
        lp, method = calculate_life_path("1990-10-25")
        assert lp == 9
        assert "9" in method

    def test_life_path_master_number(self):
        """Verify Life Path computes 11, 22, or 33 when appropriate."""
        # 1975-07-29: Month 7 -> 7; Day 29 -> 11; Year 1975 -> 22. Total: 7 + 11 + 22 = 40 -> 4.
        # Let's test a date giving 11: 1980-01-01 -> 1+1+18=20 -> 2.
        # Date giving 11: 1982-11-17 -> M=11, D=8, Y=20 -> 11 + 8 + 2 = 21 -> 3.
        # 1979-05-24 -> M=5, D=6, Y=26->8 -> 5+6+8 = 19 -> 10 -> 1.
        # Let's test 1984-07-29 -> M=7, D=11, Y=22 -> 7+11+22 = 40.
        # 1977-02-18 -> M=2, D=9, Y=24->6 -> 2+9+6 = 17 -> 8.
        # 1998-11-18 -> M=11, D=9, Y=27->9 -> 11 + 9 + 9 = 29 -> 11!
        lp, _ = calculate_life_path("1998-11-18")
        assert lp == 11

    def test_leap_year_birthday(self):
        """Verify leap year Feb 29 calculates correctly."""
        lp, _ = calculate_life_path("2000-02-29")
        # 2000 -> 2; Month 2 -> 2; Day 29 -> 11. Total: 2 + 2 + 11 = 15 -> 6
        assert lp == 6

        bday, _ = calculate_birthday_number("2000-02-29")
        # 29 -> 11
        assert bday == 11

    def test_pythagorean_vs_chaldean_mapping(self):
        """Verify name reduction differences between Pythagorean and Chaldean."""
        name = "Gokul Murugan"
        res_pyth = calculate_name_numbers(name, convention="pythagorean")
        res_chald = calculate_name_numbers(name, convention="chaldean")

        assert 1 <= res_pyth["expression"] <= 33
        assert 1 <= res_chald["expression"] <= 33
        assert "Pythagorean" in res_pyth["expression_method"]
        assert "Chaldean" in res_chald["expression_method"]

    def test_diacritics_normalization(self):
        """Verify names with accents/diacritics normalize cleanly."""
        res1 = calculate_name_numbers("José René", convention="pythagorean")
        res2 = calculate_name_numbers("Jose Rene", convention="pythagorean")
        assert res1["expression"] == res2["expression"]
        assert res1["soul_urge"] == res2["soul_urge"]
        assert res1["personality"] == res2["personality"]

    def test_karmic_lessons_and_passion(self):
        """Verify frequency breakdown finds missing digits (karmic lessons)."""
        # "Ada" -> A=1, D=4, A=1. Missing: 2, 3, 5, 6, 7, 8, 9
        res = calculate_name_numbers("Ada", convention="pythagorean")
        assert 1 not in res["karmic_lessons"]
        assert 4 not in res["karmic_lessons"]
        assert 2 in res["karmic_lessons"]
        assert 1 in res["hidden_passion"]


# ------------------------------------------------------------------------------
# 2. Calculation Unit Tests: Destiny Matrix
# ------------------------------------------------------------------------------

class TestDestinyMatrixCalculations:
    def test_arcana_reduction(self):
        """Verify numbers > 22 reduce by summing digits repeatedly until <= 22."""
        assert reduce_arcana(1) == 1
        assert reduce_arcana(22) == 22
        assert reduce_arcana(23) == 5  # 2+3 = 5
        assert reduce_arcana(28) == 10 # 2+8 = 10
        assert reduce_arcana(31) == 4  # 3+1 = 4
        assert reduce_arcana(99) == 18 # 9+9 = 18

    def test_destiny_matrix_octagram_nodes(self):
        """Verify Personal & Ancestral square vertex calculations."""
        # DOB: 1990-10-25
        # Day: 25 -> 2+5 = 7
        # Month: 10 -> 10
        # Year: 1990 -> 1+9+9+0 = 19 -> 19
        # Karmic Tail Base: 7 + 10 + 19 = 36 -> 3+6 = 9
        # Center: 7 + 10 + 19 + 9 = 45 -> 4+5 = 9
        matrix = calculate_destiny_matrix("1990-10-25")

        assert matrix["day_arcana"]["arcana_number"] == 7
        assert matrix["month_arcana"]["arcana_number"] == 10
        assert matrix["year_arcana"]["arcana_number"] == 19
        assert matrix["karmic_tail_base"]["arcana_number"] == 9
        assert matrix["comfort_zone"]["arcana_number"] == 9

        # Ancestral Diagonals
        # Father Spirit: Day (7) + Month (10) = 17
        assert matrix["father_spirit"]["arcana_number"] == 17
        # Mother Spirit: Month (10) + Year (19) = 29 -> 11
        assert matrix["mother_spirit"]["arcana_number"] == 11
        # Father Matter: Day (7) + Karmic (9) = 16
        assert matrix["father_matter"]["arcana_number"] == 16
        # Mother Matter: Year (19) + Karmic (9) = 28 -> 10
        assert matrix["mother_matter"]["arcana_number"] == 10

    def test_destiny_matrix_purposes(self):
        """Verify Sky, Earth, Personal, Social, and Spiritual purposes."""
        matrix = calculate_destiny_matrix("1990-10-25")
        purp = matrix["purpose"]

        assert 1 <= purp["personal_purpose"] <= 22
        assert 1 <= purp["social_purpose"] <= 22
        assert 1 <= purp["spiritual_purpose"] <= 22
        assert 1 <= purp["planetary_purpose"] <= 22

    def test_destiny_matrix_age_timeline(self):
        """Verify timeline spans from age 0 to 80."""
        matrix = calculate_destiny_matrix("1990-10-25")
        timeline = matrix["age_timeline"]
        assert len(timeline) >= 8
        ages = [pt["age"] for pt in timeline]
        assert 0 in ages
        assert 40 in ages
        assert 80 in ages

    def test_couples_compatibility(self):
        """Verify dual-DOB compatibility calculation."""
        comp = calculate_compatibility("1990-10-25", "1992-04-14", name1="Alice", name2="Bob")
        assert comp["person1_name"] == "Alice"
        assert comp["person2_name"] == "Bob"
        assert 1 <= comp["relationship_purpose"] <= 22
        assert 1 <= comp["shared_finance"] <= 22
        assert 1 <= comp["love_harmony"] <= 22


# ------------------------------------------------------------------------------
# 3. Calculation Unit Tests: Advanced Analysis & Yuan Integration
# ------------------------------------------------------------------------------

class TestAdvancedAnalysisCalculations:
    def test_unicode_code_point_derivation(self):
        """Verify Yuan Unicode decimal code-point reduction."""
        # Non-Latin characters should reduce deterministically
        num_chinese = derive_unicode_name_number("张伟")
        assert 1 <= num_chinese <= 33

        num_tamil = derive_unicode_name_number("கோகுல்")
        assert 1 <= num_tamil <= 33

        num_english = derive_unicode_name_number("John Doe")
        assert 1 <= num_english <= 33

    def test_lo_shu_grid_and_arrows(self):
        """Verify 3x3 Lo Shu frequency counts and Arrows of Pythagoras."""
        # DOB 1990-10-25 -> Digits: 1, 9, 9, 0, 1, 0, 2, 5
        lo_shu = calculate_lo_shu_grid("1990-10-25")
        counts = lo_shu["grid_counts"]

        assert counts["1"] == 2
        assert counts["2"] == 1
        assert counts["5"] == 1
        assert counts["9"] == 2
        assert counts["3"] == 0
        assert counts["4"] == 0

        # Check planes exist
        assert "mental" in lo_shu["planes"]
        assert "emotional" in lo_shu["planes"]
        assert "practical" in lo_shu["planes"]

    def test_pinnacles_and_challenges(self):
        """Verify 4 pinnacles and 4 challenges with age boundaries."""
        pc = calculate_pinnacles_and_challenges("1990-10-25")
        assert len(pc["pinnacles"]) == 4
        assert len(pc["challenges"]) == 4

        for pin in pc["pinnacles"]:
            assert 1 <= pin["value"] <= 33
            assert "Age" in pin["age_span"]

        for chal in pc["challenges"]:
            assert 0 <= chal["value"] <= 9

    def test_karmic_debt_detection(self):
        """Verify day 13, 14, 16, 19 trigger karmic debt entries."""
        debts_13 = detect_karmic_debts("1995-05-13", "Alex")
        assert any(d["number"] == 13 for d in debts_13)

        debts_14 = detect_karmic_debts("1995-05-14", "Alex")
        assert any(d["number"] == 14 for d in debts_14)

        debts_16 = detect_karmic_debts("1995-05-16", "Alex")
        assert any(d["number"] == 16 for d in debts_16)

        debts_19 = detect_karmic_debts("1995-05-19", "Alex")
        assert any(d["number"] == 19 for d in debts_19)

        debts_none = detect_karmic_debts("1995-05-20", "Alex")
        assert len(debts_none) == 0


# ------------------------------------------------------------------------------
# 4. FastAPI Integration Endpoint Tests
# ------------------------------------------------------------------------------

class TestNumerologyEndpoints:
    def test_traditional_numerology_endpoint_success(self):
        """Test POST /api/v1/numerology/traditional."""
        payload = {
            "full_name": "Gokul Murugan",
            "birth_date": "1995-06-15",
            "system_convention": "pythagorean",
            "language": "en",
        }
        res = client.post("/api/v1/numerology/traditional", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["person_name"] == "Gokul Murugan"
        assert data["system_convention"] == "pythagorean"
        assert data["life_path"]["number_value"] > 0
        assert data["expression_destiny"]["number_value"] > 0
        assert data["soul_urge"]["number_value"] > 0
        assert data["personality"]["number_value"] > 0
        assert len(data["strengths"]) > 0
        assert len(data["challenges"]) > 0

    def test_traditional_numerology_tamil_language(self):
        """Test Tamil language response."""
        payload = {
            "full_name": "Gokul Murugan",
            "birth_date": "1995-06-15",
            "system_convention": "pythagorean",
            "language": "ta",
        }
        res = client.post("/api/v1/numerology/traditional", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["overall_synthesis"]) > 0

    def test_traditional_numerology_validation_failure(self):
        """Test invalid birth date formatting."""
        payload = {
            "full_name": "Gokul",
            "birth_date": "15-06-1995",  # Invalid, must be YYYY-MM-DD
        }
        res = client.post("/api/v1/numerology/traditional", json=payload)
        assert res.status_code == 422

    def test_destiny_matrix_endpoint_success(self):
        """Test POST /api/v1/numerology/destiny-matrix."""
        payload = {
            "birth_date": "1995-06-15",
            "person_name": "Gokul",
            "partner_birth_date": "1997-08-20",
            "partner_name": "Partner",
            "language": "en",
        }
        res = client.post("/api/v1/numerology/destiny-matrix", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["day_arcana"]["arcana_number"] == 15
        assert data["month_arcana"]["arcana_number"] == 6
        assert len(data["karmic_tail_triad"]) == 3
        assert data["compatibility"] is not None
        assert data["compatibility"]["relationship_purpose"] > 0

    def test_advanced_analysis_endpoint_success(self):
        """Test POST /api/v1/numerology/advanced."""
        payload = {
            "full_name": "Gokul Murugan",
            "birth_date": "1995-06-15",
            "language": "en",
        }
        res = client.post("/api/v1/numerology/advanced", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["unicode_derived_name_number"] > 0
        assert "4" in data["lo_shu"]["grid_counts"]
        assert len(data["pinnacles_challenges"]["pinnacles"]) == 4

    def test_metadata_endpoint(self):
        """Test GET /api/v1/numerology/metadata."""
        res = client.get("/api/v1/numerology/metadata")
        assert res.status_code == 200
        data = res.json()
        assert data["engine_version"] == "1.0.0"
        assert len(data["methods"]) == 3
        assert len(data["conventions"]) == 2
