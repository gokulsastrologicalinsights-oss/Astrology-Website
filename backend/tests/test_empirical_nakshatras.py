"""Tests for Empirical Nakshatra Deep Analysis Engine (Ashwini through Ashlesha)."""

import pytest
from app.services.nakshatra_engine.natchathira_deep_analyzer import (
    analyze_saved_chart_nakshatras,
    extract_chart_contexts,
)


def test_empirical_nakshatra_pipeline():
    mock_horoscope = {
        "ascendant": {"sign_name": "Aries", "degree_in_sign": 5.0, "nakshatra": {"name": "Ashwini", "pada": 2}},
        "planets": [
            {"name": "Sun", "sign_name": "Aries", "degree_in_sign": 28.0, "nakshatra": {"name": "Krittika", "pada": 1}},
            {"name": "Moon", "sign_name": "Taurus", "degree_in_sign": 15.0, "nakshatra": {"name": "Rohini", "pada": 2}},
            {"name": "Mars", "sign_name": "Taurus", "degree_in_sign": 28.0, "nakshatra": {"name": "Mrigashira", "pada": 2}},
            {"name": "Mercury", "sign_name": "Gemini", "degree_in_sign": 12.0, "nakshatra": {"name": "Ardra", "pada": 2}},
            {"name": "Jupiter", "sign_name": "Gemini", "degree_in_sign": 25.0, "nakshatra": {"name": "Punarvasu", "pada": 2}},
            {"name": "Venus", "sign_name": "Cancer", "degree_in_sign": 10.0, "nakshatra": {"name": "Pushya", "pada": 3}},
            {"name": "Saturn", "sign_name": "Cancer", "degree_in_sign": 20.0, "nakshatra": {"name": "Ashlesha", "pada": 2}},
            {"name": "Rahu", "sign_name": "Aries", "degree_in_sign": 20.0, "nakshatra": {"name": "Bharani", "pada": 3}},
            {"name": "Ketu", "sign_name": "Libra", "degree_in_sign": 20.0, "nakshatra": {"name": "Vishakha", "pada": 1}},
        ],
        "houses": [
            {"sign_name": "Aries", "house_number": 1},
            {"sign_name": "Taurus", "house_number": 2},
            {"sign_name": "Gemini", "house_number": 3},
            {"sign_name": "Cancer", "house_number": 4},
            {"sign_name": "Leo", "house_number": 5},
            {"sign_name": "Virgo", "house_number": 6},
            {"sign_name": "Libra", "house_number": 7},
            {"sign_name": "Scorpio", "house_number": 8},
            {"sign_name": "Sagittarius", "house_number": 9},
            {"sign_name": "Capricorn", "house_number": 10},
            {"sign_name": "Aquarius", "house_number": 11},
            {"sign_name": "Pisces", "house_number": 12},
        ],
    }

    res = analyze_saved_chart_nakshatras(mock_horoscope, birth_date_str="1996-01-01")
    assert res["valid"] is True
    assert res["total_rules_matched"] > 0
    assert len(res["age_milestones"]) >= 2
    assert len(res["body_part_alerts"]) >= 1

    rule_ids = {r["technique_id"] for r in res["matched_rules"]}
    assert "ROHINI_T1_FALSE_ACCUSATION" in rule_ids
    assert "ARDRA_T1_ANIMALS_CONNECTION" in rule_ids
    assert "PUNARVASU_T1_TECH_FASCINATION" in rule_ids
    assert "PUSHYA_T2_NARAYANA_KAVACH_REMEDY" in rule_ids
    assert "ASHLESHA_T1_AGE_18_20_PIVOT" in rule_ids
