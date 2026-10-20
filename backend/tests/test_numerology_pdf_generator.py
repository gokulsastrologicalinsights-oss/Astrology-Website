"""Unit and Integration tests for Numerology PDF Report Generator.

Verifies:
1. Valid PDF generation (%PDF- magic bytes, non-empty content) for all 9 numerology methods:
   - traditional
   - destiny_matrix
   - advanced
   - name_correction
   - business
   - phone
   - vehicle
   - property
   - marriage
2. Bilingual rendering (English and Tamil).
3. API endpoints:
   - POST /api/v1/numerology/export-pdf
   - GET /api/v1/numerology/reports/{report_id}/pdf
4. Ownership security and error handling.
"""

from io import BytesIO
from unittest.mock import patch
import pytest
import pypdf
from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import get_current_user
from app.services.numerology.pdf_generator import (
    NumerologyPdfGenerator,
    generate_numerology_pdf_bytes,
)

client = TestClient(app)

MOCK_USER = {
    "id": "11111111-1111-1111-1111-111111111111",
    "email": "testuser@example.com",
    "role": "authenticated",
}


def test_generate_pdf_traditional_bilingual():
    """Verify traditional numerology PDF generates valid bytes in English and Tamil."""
    calc_data = {
        "birth_psychic_number": {
            "number_value": 7,
            "number_name": "Birth / Psychic Number",
            "ruling_planet": "Ketu",
            "calculation_method": "Day of month reduction",
            "detailed_interpretation": "Analytical, spiritual seeker, reflective and introspective.",
            "is_master": False,
        },
        "life_path": {
            "number_value": 11,
            "number_name": "Life Path Number",
            "ruling_planet": "Moon",
            "calculation_method": "Period reduction",
            "detailed_interpretation": "Master Intuitive, inspirational teacher and visionary channel.",
            "is_master": True,
        },
        "expression_destiny": {
            "number_value": 9,
            "number_name": "Expression / Destiny Number",
            "ruling_planet": "Mars",
            "calculation_method": "Pythagorean letter sum",
            "detailed_interpretation": "Universal humanitarian, broad compassion and artistic philanthropy.",
            "is_master": False,
        },
        "soul_urge": {
            "number_value": 3,
            "number_name": "Soul Urge",
            "ruling_planet": "Jupiter",
            "calculation_method": "Vowels sum",
        },
        "personality": {
            "number_value": 6,
            "number_name": "Personality",
            "ruling_planet": "Venus",
            "calculation_method": "Consonants sum",
        },
        "personal_year": 5,
        "calculation_breakdown": {
            "source_birth_date": "1990-05-16",
        },
    }
    interp_data = {
        "strengths": ["Spiritual intuition", "Philosophical depth", "Strategic foresight"],
        "challenges": ["Overthinking", "Tendency to isolate", "Perfectionism"],
        "career_tendencies": ["Research", "Astrology", "Data architecture"],
        "financial_tendencies": ["Prudent investments", "Values intellectual wealth"],
        "love_themes": ["Seeks profound mental connection"],
        "overall_synthesis": "Balanced combination of psychic inquiry and visionary expression.",
    }

    # 1. English PDF
    pdf_en = generate_numerology_pdf_bytes(
        person_name="Gokul Murugan",
        birth_date="1990-05-16",
        method="traditional",
        system_convention="pythagorean",
        calculation_data=calc_data,
        interpretation_data=interp_data,
        language="en",
        display_number=101,
        report_id="TEST-TRAD-EN",
    )
    assert isinstance(pdf_en, bytes)
    assert pdf_en.startswith(b"%PDF-")
    assert len(pdf_en) > 5000

    reader_en = pypdf.PdfReader(BytesIO(pdf_en))
    assert len(reader_en.pages) >= 1
    text_en = reader_en.pages[0].extract_text()
    assert "GOKUL'S ASTROLOGICAL INSIGHTS" in text_en
    assert "Gokul Murugan" in text_en

    # 2. Tamil PDF
    pdf_ta = generate_numerology_pdf_bytes(
        person_name="கோகுல் முருகன்",
        birth_date="1990-05-16",
        method="traditional",
        system_convention="pythagorean",
        calculation_data=calc_data,
        interpretation_data=interp_data,
        language="ta",
        display_number=102,
        report_id="TEST-TRAD-TA",
    )
    assert isinstance(pdf_ta, bytes)
    assert pdf_ta.startswith(b"%PDF-")
    assert len(pdf_ta) > 5000


def test_generate_pdf_destiny_matrix():
    """Verify destiny matrix 22 arcana octagram PDF generates valid bytes."""
    calc_data = {
        "personal_square": {"point_a": 16, "point_b": 5, "point_c": 19, "point_d": 4},
        "social_square": {"point_e": 21, "point_f": 7, "point_g": 12, "point_h": 10},
        "center_comfort_zone": {"point_r": 9},
        "purposes": {"personal": 14, "social": 8, "spiritual": 22},
        "karmic_tail": {
            "points": [18, 6, 15],
            "title": "Magical Knowledge & Passions",
            "description": "Overcoming temptations and using intuitive intellect constructively.",
        },
        "money_line": {"entrance": 19, "center": 21, "blockers": "Self-doubt"},
        "love_line": {"entrance": 7, "partner_qualities": "Spiritual, dynamic, purposeful"},
    }
    interp_data = {
        "overall_synthesis": "Strong awakening potential anchored by Tower arcana transformation.",
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Maya Sundaram",
        birth_date="1995-10-16",
        method="destiny_matrix",
        system_convention="pythagorean",
        calculation_data=calc_data,
        interpretation_data=interp_data,
        language="en",
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_advanced_lo_shu():
    """Verify advanced Lo Shu grid & pinnacles PDF generates valid bytes."""
    calc_data = {
        "unicode_derived_name_number": 8,
        "karmic_lessons": [4, 7],
        "dominant_vibrations": [1, 9],
        "lo_shu": {
            "digit_frequencies": {"1": 2, "9": 3, "5": 1},
            "arrows_of_strength": ["Arrow of Will (1-5-9)"],
            "arrows_of_weakness": ["Arrow of Frustration (4-5-6)"],
        },
        "pinnacles": {
            "pinnacle_1": {"number": 3, "start_age": 0, "end_age": 31},
            "pinnacle_2": {"number": 5, "start_age": 32, "end_age": 40},
        },
        "challenges": {
            "challenge_1": {"number": 2},
            "challenge_2": {"number": 4},
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Vikram Raman",
        birth_date="1988-09-19",
        method="advanced",
        system_convention="pythagorean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_name_correction():
    """Verify name correction studio PDF generates valid bytes."""
    calc_data = {
        "target_expression": 1,
        "original_name_analysis": {
            "expression": 4,
            "compound_expression": 31,
            "soul_urge": 8,
            "personality": 5,
        },
        "candidates": [
            {
                "name": "VIKKRAM RAMAN",
                "variation_type": "consonant_doubling",
                "expression_number": 1,
                "compound_expression": 37,
                "harmony_score": 95,
                "pronunciation_score": 90,
                "simplicity_score": 88,
                "composite_score": 91,
                "is_master": False,
                "vibrational_synthesis": "Dynamic leadership alignment.",
            },
            {
                "name": "VIKRAAM RAMAN",
                "variation_type": "vowel_lengthening",
                "expression_number": 1,
                "compound_expression": 28,
                "harmony_score": 92,
                "pronunciation_score": 85,
                "simplicity_score": 82,
                "composite_score": 86,
                "is_master": False,
                "vibrational_synthesis": "Harmonic sun leadership.",
            },
        ],
        "best_candidate": {
            "name": "VIKKRAM RAMAN",
            "expression_number": 1,
            "composite_score": 91,
            "harmony_score": 95,
            "simplicity_score": 88,
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Vikram Raman",
        birth_date="1988-09-19",
        method="name_correction",
        system_convention="chaldean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_business_studio():
    """Verify business & brand studio PDF generates valid bytes."""
    calc_data = {
        "legal_analysis": {
            "expression_number": 8,
            "compound_expression": 44,
            "vibrational_synthesis": "Corporate governance and structural authority.",
        },
        "brand_analysis": {
            "expression_number": 5,
            "compound_expression": 23,
            "industry_harmony_score": 90,
            "founder_harmony_score": 85,
            "composite_score": 88,
            "vibrational_synthesis": "Royal star of the lion and adaptive commercial agility.",
        },
        "tagline_analysis": {
            "expression_number": 3,
            "synergy_score": 86,
        },
        "founders_evaluation": [
            {
                "founder_name": "Gokul M",
                "birth_date": "1990-05-16",
                "psychic_number": 7,
                "life_path_number": 11,
                "harmony_score": 88,
                "resonance_level": "High Resonance",
            },
            {
                "founder_name": "Arun Kumar",
                "birth_date": "1992-08-23",
                "psychic_number": 5,
                "life_path_number": 7,
                "harmony_score": 92,
                "resonance_level": "Exceptional Resonance",
            },
        ],
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Solaris Technologies Pvt Ltd",
        birth_date="2024-01-15",
        method="business",
        system_convention="chaldean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_phone_studio():
    """Verify phone numerology PDF generates valid bytes."""
    calc_data = {
        "subscriber_digits": "9876543210",
        "formatted_national": "98765 43210",
        "primary_analysis": {
            "compound_sum": 45,
            "root_number": 9,
            "ruling_planet": "Mars",
            "keyword": "Universal Leader",
            "zero_count": 1,
            "missing_digits": [0],
            "patterns": {"vanity_score": 80},
        },
        "personal_compatibility": {
            "personal_score": 88,
            "level": "Harmonious",
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="+91 98765 43210",
        birth_date="1990-05-16",
        method="phone",
        system_convention="pythagorean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_vehicle_studio():
    """Verify vehicle registration numerology PDF generates valid bytes."""
    calc_data = {
        "formatted_registration": "TN 09 AB 1234",
        "parsed_state": "Tamil Nadu",
        "parsed_rto": "09",
        "parsed_series": "AB",
        "parsed_number": "1234",
        "calculation_mode": "digits_only",
        "primary_analysis": {
            "compound_sum": 10,
            "root_number": 1,
            "ruling_planet": "Sun",
            "keyword": "Pioneer & Executive Transport",
            "mode_label": "Digits Only (1+2+3+4 = 10 -> 1)",
            "reduction_steps": [10, 1],
        },
    }
    interp_data = {
        "usage_alignment": {
            "vehicle_usage": "personal_luxury",
            "score": 92,
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="TN 09 AB 1234",
        birth_date="2023-08-10",
        method="vehicle",
        system_convention="pythagorean",
        calculation_data=calc_data,
        interpretation_data=interp_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_property_studio():
    """Verify property numerology PDF generates valid bytes."""
    calc_data = {
        "components": {
            "door_analysis": {"input_string": "104", "formula": "1+0+4", "root_number": 5},
            "building_analysis": {"input_string": "B-Wing", "formula": "Chaldean B(2)", "root_number": 2},
            "floor_analysis": {"input_string": "10", "formula": "1+0", "root_number": 1},
            "combined_analysis": {"input_string": "B-104", "formula": "Door(5) + Building(2) = 7", "root_number": 7, "compound_sum": 16},
        },
        "vastu_alignment": {
            "facing_direction": "North-East (Ishanya)",
            "element": "Water & Ether",
            "ruler": "Jupiter (Guru)",
            "vastu_score": 95,
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Flat B-104, Sunrise Heights",
        birth_date="2022-03-20",
        method="property",
        system_convention="chaldean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_marriage_studio():
    """Verify marriage numerology PDF generates valid bytes."""
    calc_data = {
        "overall_score": 88,
        "overall_harmony_level": "Excellent Compatibility",
        "person_a_profile": {
            "name": "Karthik",
            "birth_psychic_number": 1,
            "birth_psychic_planet": "Sun",
            "life_path_number": 7,
            "life_path_planet": "Ketu",
            "expression_number": 5,
            "soul_urge_number": 3,
        },
        "person_b_profile": {
            "name": "Priyanka",
            "birth_psychic_number": 3,
            "birth_psychic_planet": "Jupiter",
            "life_path_number": 7,
            "life_path_planet": "Ketu",
            "expression_number": 6,
            "soul_urge_number": 9,
        },
        "life_path_compatibility": {
            "score": 95,
            "harmony_level": "Deep Soul Resonance",
            "planetary_dynamic": "Identical Life Paths",
        },
        "psychic_compatibility": {
            "score": 85,
            "harmony_level": "Harmonious",
        },
        "expression_compatibility": {
            "score": 80,
            "harmony_level": "Supportive",
        },
        "soul_urge_compatibility": {
            "score": 82,
            "harmony_level": "Complementary",
        },
        "shared_strengths": ["Spiritual alignment", "Mutual intellectual respect"],
        "potential_challenges": ["Need for individual quiet time"],
        "conversation_prompts": ["How do we honor each other's contemplative periods?"],
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Karthik & Priyanka",
        birth_date="1991-01-10",
        method="marriage",
        system_convention="pythagorean",
        calculation_data=calc_data,
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_api_export_pdf_direct():
    """Verify POST /api/v1/numerology/export-pdf endpoint returns valid PDF."""
    payload = {
        "person_name": "Direct Export Test",
        "birth_date": "1990-05-16",
        "method": "traditional",
        "system_convention": "pythagorean",
        "language": "en",
        "calculation_data": {
            "birth_psychic_number": {"number_value": 7, "ruling_planet": "Ketu"},
            "life_path": {"number_value": 11, "ruling_planet": "Moon"},
        },
    }

    res = client.post("/api/v1/numerology/export-pdf", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-")
    assert "Direct_Export_Test" in res.headers.get("content-disposition", "")


def test_api_saved_report_pdf():
    """Verify GET /api/v1/numerology/reports/{report_id}/pdf endpoint."""
    report_dict = {
        "id": "22222222-2222-2222-2222-222222222222",
        "user_id": MOCK_USER["id"],
        "display_number": 42,
        "person_name": "Saved Report Native",
        "birth_date": "1994-08-12",
        "method": "phone",
        "system_convention": "chaldean",
        "calculation_data": {
            "primary_analysis": {"root_number": 6, "compound_sum": 33},
        },
        "interpretation_data": {
            "overall_synthesis": "Harmonic Venusian vibration.",
        },
        "engine_version": "1.0.0",
    }

    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    try:
        with patch("app.routers.numerology.get_numerology_report", return_value=report_dict):
            res = client.get(
                f"/api/v1/numerology/reports/{report_dict['id']}/pdf?lang=en",
                headers={"Authorization": "Bearer mock-token"},
            )
            assert res.status_code == 200
            assert res.headers["content-type"] == "application/pdf"
            assert res.content.startswith(b"%PDF-")
            assert "Numerology_Report_42_Saved_Report_Native_en.pdf" in res.headers.get("content-disposition", "")
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_api_saved_report_pdf_not_found():
    """Verify GET /api/v1/numerology/reports/{id}/pdf returns 404 when report not found."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    try:
        with patch("app.routers.numerology.get_numerology_report", return_value=None):
            res = client.get(
                "/api/v1/numerology/reports/missing-uuid/pdf",
                headers={"Authorization": "Bearer mock-token"},
            )
            assert res.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_generate_pdf_advanced_lo_shu_dict_arrows():
    """Verify advanced Lo Shu grid PDF handles dictionary arrow definitions cleanly."""
    calc_data = {
        "unicode_derived_name_number": 5,
        "karmic_lessons": [2, 4],
        "dominant_vibrations": [1, 5, 9],
        "lo_shu": {
            "digit_frequencies": {"1": 2, "9": 1, "5": 1},
            "arrows_of_strength": [
                {"numbers": "1-5-9", "name": "Arrow of Determination", "meaning": "High willpower"}
            ],
            "arrows_of_weakness": [
                {"numbers": "3-5-7", "arrow_name": "Arrow of Skepticism", "meaning": "Disillusionment"}
            ],
        },
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Gokul Murugan",
        birth_date="1990-05-16",
        method="advanced",
        system_convention="pythagorean",
        calculation_data=calc_data,
        language="ta",
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000


def test_generate_pdf_family_studio():
    """Verify Family & Baby Numerology PDF generates valid bytes in English and Tamil."""
    calc_data = {
        "overall_family_harmony_score": 90,
        "overall_family_harmony_level": "Deep Harmonious Synergy",
        "dominant_vibrations": [1, 5],
        "elemental_balance": {"dominant_element": "Fire", "Fire": 3, "Water": 1, "Air": 2, "Earth": 1},
        "members_evaluated": [
            {
                "name": "Father",
                "role": "father",
                "birth_date": "1990-05-16",
                "birth_psychic_number": 7,
                "life_path_number": 9,
                "expression_number": 3,
                "element": "Water",
                "ruling_planet": "Ketu",
                "archetype": "Intuitive Guide",
            },
            {
                "name": "Mother",
                "role": "mother",
                "birth_date": "1992-08-20",
                "birth_psychic_number": 2,
                "life_path_number": 4,
                "expression_number": 6,
                "element": "Earth",
                "ruling_planet": "Moon",
                "archetype": "Nurturing Anchor",
            },
        ],
        "baby_name_candidates": [
            {
                "name": "Aarav",
                "expression_number": 1,
                "composite_score": 94.0,
                "phonetic_analysis": "Pioneering vibration",
                "balance_rating": "Optimal",
            }
        ],
        "pairwise_comparisons": [
            {
                "person_a_name": "Father",
                "person_b_name": "Mother",
                "relationship_type": "Spouse Dynamics",
                "composite_harmony_score": 88,
                "planetary_dynamic": "Ketu & Moon",
                "nurturing_prompt": "Cultivate shared mindful communication.",
            }
        ],
    }

    pdf_bytes = generate_numerology_pdf_bytes(
        person_name="Gokul Family",
        birth_date="1990-05-16",
        method="family",
        system_convention="pythagorean",
        calculation_data=calc_data,
        language="ta",
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000
