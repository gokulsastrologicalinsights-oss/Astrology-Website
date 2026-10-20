"""Comprehensive Test Suite for Business & Brand Numerology Studio.

Verifies:
1. Corporate legal name vs. normalized brand name parsing and suffix isolation.
2. Dual tradition calculations: Pythagorean vs. Chaldean for company names.
3. Industry sector vibrational alignments and traditional correspondences.
4. Single-founder and multi-founder partnership compatibility matrices.
5. Slogan/tagline synergy and domain/social handle vibration analysis.
6. Tamil and Unicode business names.
7. Candidate ranking determinism and scoring weights.
8. Input validation constraints (empty names, invalid industry, invalid DOB, excessive limits).
9. API endpoint integration (/api/v1/numerology/business/analyze).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.numerology.business_studio import (
    normalize_business_name,
    score_industry_harmony,
    evaluate_single_founder_harmony,
    evaluate_partnership_matrix,
    analyze_tagline,
    analyze_domain_or_handle,
    evaluate_business_brand_candidates,
    INDUSTRY_PROFILES,
)

client = TestClient(app)


class TestBusinessNormalizationAndSuffixes:
    def test_pvt_ltd_normalization(self):
        """Verify Private Limited / Pvt Ltd isolation without losing original legal name."""
        legal = "Tata Consultancy Services Private Limited"
        res = normalize_business_name(legal)
        assert res["full_legal_name"] == legal
        assert res["cleaned_brand_name"] == "Tata Consultancy Services"
        assert len(res["detected_suffixes"]) > 0
        assert "TCS" in res["acronym"]
        assert res["is_modified"] is True

    def test_llp_and_inc_normalization(self):
        """Verify LLP and Inc corporate suffix detection."""
        res_llp = normalize_business_name("Apex Capital Ventures LLP")
        assert "LLP" in [s.upper() for s in res_llp["detected_suffixes"]]
        assert "Apex Capital" in res_llp["cleaned_brand_name"]

        res_inc = normalize_business_name("Nova Health Global Inc.")
        assert "INC" in [s.upper() for s in res_inc["detected_suffixes"]]
        assert "Nova Health" in res_inc["cleaned_brand_name"]

    def test_name_without_suffixes(self):
        """Verify clean brand names without corporate suffixes remain unmodified."""
        brand = "Gokul Insights"
        res = normalize_business_name(brand)
        assert res["full_legal_name"] == brand
        assert res["cleaned_brand_name"] == brand
        assert len(res["detected_suffixes"]) == 0
        assert res["is_modified"] is False
        assert res["acronym"] == "GI"


class TestIndustryVibrationsAndTraditions:
    def test_tech_industry_harmony(self):
        """Verify tech sector favors Mercury (5), Rahu (4), Sun (1)."""
        score_5, desc_5 = score_industry_harmony(5, "technology")
        assert score_5 == 100.0
        assert "Primary" in desc_5

        score_4, desc_4 = score_industry_harmony(4, "technology")
        assert score_4 == 100.0

        # Unaligned number should still get a respectful base score
        score_8, _ = score_industry_harmony(8, "technology")
        assert 40.0 <= score_8 < 100.0

    def test_finance_industry_harmony(self):
        """Verify finance sector favors Saturn (8) and Jupiter (3)."""
        score_8, _ = score_industry_harmony(8, "finance")
        assert score_8 == 100.0

        score_3, _ = score_industry_harmony(3, "finance")
        assert score_3 == 100.0

    def test_all_industry_categories_documented(self):
        """Ensure all required industry sectors have documented profiles."""
        required = [
            "technology",
            "retail",
            "education",
            "healthcare",
            "finance",
            "manufacturing",
            "astrology",
            "creative",
            "other",
        ]
        for cat in required:
            assert cat in INDUSTRY_PROFILES
            assert len(INDUSTRY_PROFILES[cat]["primary_numbers"]) >= 2
            assert "traditional_rationale" in INDUSTRY_PROFILES[cat]


class TestFounderAndPartnershipCompatibility:
    def test_single_founder_with_dob(self):
        """Verify single founder calculates Mulank & Bhagyank and compares with brand."""
        founder = {
            "name": "Gokul Murugan",
            "birth_date": "1990-10-15", # Mulank: 1+5 = 6 (Venus)
            "role": "Founder & CEO",
        }
        # Brand expression 6 (Venus) matching Mulank 6
        res = evaluate_single_founder_harmony(founder, brand_expression=6, convention="chaldean")
        assert res["psychic_number"] == 6
        assert res["psychic_harmony_score"] == 100.0
        assert res["alignment_score"] >= 80.0
        assert res["alignment_level"] in ("Excellent", "Harmonious")

    def test_single_founder_without_dob_fallback(self):
        """Verify founder without birth date falls back to founder name expression."""
        founder = {
            "name": "Alexander",
            "role": "Partner",
        }
        res = evaluate_single_founder_harmony(founder, brand_expression=5, convention="pythagorean")
        assert res["birth_date"] is None
        assert res["psychic_number"] is None
        assert res["name_expression"] > 0
        assert 0.0 <= res["alignment_score"] <= 100.0

    def test_multi_founder_partnership_matrix_weighted(self):
        """Verify multi-founder partnership matrix with equity share weighting."""
        founders = [
            {
                "name": "Founder Alpha",
                "birth_date": "1985-05-14", # Day 14 -> 5
                "share_percentage": 70.0,
            },
            {
                "name": "Founder Beta",
                "birth_date": "1992-08-26", # Day 26 -> 8
                "share_percentage": 30.0,
            },
        ]
        # Brand expression 5
        matrix = evaluate_partnership_matrix(founders, brand_expression=5, convention="chaldean")
        assert "overall_partnership_score" in matrix
        assert 0.0 <= matrix["overall_partnership_score"] <= 100.0
        assert len(matrix["founder_results"]) == 2
        # Alpha (5 matches 5) should have 100 psychic harmony
        alpha_res = matrix["founder_results"][0]
        assert alpha_res["psychic_number"] == 5
        assert alpha_res["psychic_harmony_score"] == 100.0


class TestTaglineAndDomainHandleAnalysis:
    def test_tagline_synergy(self):
        """Verify slogan / tagline calculation and synergy evaluation."""
        tagline = "Empowering Astrological Wisdom"
        res = analyze_tagline(tagline, brand_expression=3, convention="chaldean")
        assert res["expression_number"] > 0
        assert 0.0 <= res["synergy_score"] <= 100.0
        assert "synergy_interpretation" in res

    def test_domain_handle_sanitization(self):
        """Verify URL and handle stripping (.com, @, etc.) and evaluation."""
        handle = "https://www.gokulastrology.com/about"
        res = analyze_domain_or_handle(handle, brand_expression=5, convention="chaldean")
        assert res["clean_handle"] == "gokulastrology"
        assert res["expression_number"] > 0

        social = "@gokulastrology"
        res_soc = analyze_domain_or_handle(social, brand_expression=5, convention="chaldean")
        assert res_soc["clean_handle"] == "gokulastrology"


class TestTamilAndUnicodeBusinessNames:
    def test_tamil_business_name(self):
        """Verify Tamil business name evaluation."""
        tamil_biz = "ஸ்ரீ முருகன் என்டர்பிரைசஸ்"
        res = evaluate_business_brand_candidates(
            legal_name=tamil_biz,
            convention="chaldean",
            industry_category="retail",
            max_candidates=5,
        )
        assert res["legal_name"] == tamil_biz
        assert res["legal_analysis"]["expression_number"] > 0
        assert len(res["candidates"]) > 0


class TestBusinessCandidatesRankingAndDeterminism:
    def test_candidate_ranking_order(self):
        """Verify candidates are sorted in descending order of composite score."""
        res = evaluate_business_brand_candidates(
            legal_name="Apex Global Technologies Private Limited",
            brand_name="Apex Tech",
            convention="chaldean",
            industry_category="technology",
            custom_candidates=["Apex Quantum", "Apex Innovations"],
            max_candidates=15,
        )
        scores = [c["composite_score"] for c in res["candidates"]]
        assert scores == sorted(scores, reverse=True)
        assert len(res["candidates"]) <= 15
        assert res["legal_analysis"] is not None
        assert res["brand_analysis"] is not None


class TestAPIEndpointsAndValidation:
    def test_api_business_analyze_success(self):
        """Test POST /api/v1/numerology/business/analyze endpoint."""
        payload = {
            "legal_name": "Gokul Astrological Insights Private Limited",
            "brand_name": "Gokul Insights",
            "tagline": "Ancient Wisdom for Modern Destinies",
            "domain_or_handle": "gokulinsights.com",
            "system_convention": "chaldean",
            "industry_category": "astrology",
            "founders": [
                {
                    "name": "Gokul Murugan",
                    "birth_date": "1990-10-15",
                    "role": "Founder & Chief Astrologer",
                    "share_percentage": 100.0,
                }
            ],
            "custom_candidates": ["Gokul Divine", "Gokul Astro"],
            "max_candidates": 20,
            "language": "en",
        }
        response = client.post("/api/v1/numerology/business/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["legal_name"] == "Gokul Astrological Insights Private Limited"
        assert data["normalized_brand_name"] == "Gokul Insights"
        assert len(data["detected_suffixes"]) > 0
        assert data["legal_analysis"] is not None
        assert data["brand_analysis"] is not None
        assert data["tagline_analysis"] is not None
        assert data["domain_analysis"] is not None
        assert len(data["candidates"]) > 0
        assert "scoring_explanation" in data

    def test_api_validation_empty_or_punctuation_company_name(self):
        """Verify rejection of empty or punctuation-only company names."""
        res_empty = client.post("/api/v1/numerology/business/analyze", json={"legal_name": "   "})
        assert res_empty.status_code == 422

        res_punct = client.post("/api/v1/numerology/business/analyze", json={"legal_name": "...---!!!"})
        assert res_punct.status_code == 422

    def test_api_validation_invalid_industry_or_limit(self):
        """Verify rejection of invalid industry category or excessive candidate limits."""
        res_bad_ind = client.post(
            "/api/v1/numerology/business/analyze",
            json={"legal_name": "Valid Name", "industry_category": "crypto_gambling"},
        )
        assert res_bad_ind.status_code == 422

        res_bad_lim = client.post(
            "/api/v1/numerology/business/analyze",
            json={"legal_name": "Valid Name", "max_candidates": 100},
        )
        assert res_bad_lim.status_code == 422

    def test_api_validation_invalid_founder_dob(self):
        """Verify rejection of invalid founder birth date format."""
        payload = {
            "legal_name": "Valid Corp",
            "founders": [{"name": "John", "birth_date": "15-10-1990"}], # Bad format
        }
        res = client.post("/api/v1/numerology/business/analyze", json=payload)
        assert res.status_code == 422
