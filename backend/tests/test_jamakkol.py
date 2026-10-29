"""Unit and integration tests for Jamakkol Prasanam (ஜாமக்கோள் பிரசன்னம்) calculation engine."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.jamakkol.calculator import calculate_jamakkol_prasanam
from app.services.jamakkol.constants import (
    ZODIAC_SIGNS,
    JAMA_GRAHAS,
    JAMA_SIGNS_ANTICLOCKWISE,
    SURYA_VEETHI_RULES,
)

client = TestClient(app)


def test_metadata_endpoint():
    """Verify metadata endpoint returns 8 Jama Grahas, 12 Signs, and Surya Veethi rules."""
    response = client.get("/api/v1/jamakkol-prasanam/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "jama_grahas" in data
    assert len(data["jama_grahas"]) == 8
    assert "surya_veethi_rules" in data
    assert "zodiac_signs" in data
    assert len(data["zodiac_signs"]) == 12


def test_jamakkol_calculation_daytime():
    """Verify daytime Jamakkol calculation for Chennai with classical rules output."""
    payload = {
        "query_datetime": "2026-10-28T10:30:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "query_text": "Will my business contract be approved today?",
        "query_category": "business_finance",
    }
    response = client.post("/api/v1/jamakkol-prasanam/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # 1. Solar Info
    assert data["solar_info"]["is_day"] is True
    assert "sunrise_local" in data["solar_info"]
    assert "sunset_local" in data["solar_info"]

    # 2. Jamam Info
    jamam = data["jamam_info"]
    assert jamam["period_type"] == "Day"
    assert 1 <= jamam["jamam_number"] <= 8
    assert "jamam_ruler_en" in jamam
    assert "jamam_ruler_ta" in jamam

    # 3. Three Pillars
    pillars = data["three_pillars"]
    assert "udhayam" in pillars
    assert "aarudham" in pillars
    assert "kavippu" in pillars

    assert 1 <= pillars["udhayam"]["sign_index"] <= 12
    assert 1 <= pillars["aarudham"]["sign_index"] <= 12
    assert 1 <= pillars["kavippu"]["sign_index"] <= 12

    # 4. Jama Grahas (8 planets in 8 chara/ubhaya signs)
    assert len(data["jama_grahas"]) == 8
    for g in data["jama_grahas"]:
        assert g["sign_index"] in JAMA_SIGNS_ANTICLOCKWISE

    # 5. House placements (12 signs)
    assert len(data["house_placements"]) == 12

    # 6. Prediction verdict
    pred = data["prediction_verdict"]
    assert pred["status"] in ["favorable", "delayed_success", "unfavorable"]
    assert len(pred["category_specific_insights_en"]) > 0
    assert len(pred["remedial_measures_en"]) > 0

    # 7. Classical rules breakdown
    assert "classical_rules" in data
    rules = data["classical_rules"]
    assert "watch_time_relation" in rules
    assert "facing_direction" in rules
    assert "rising_nature" in rules
    assert "subh_balance" in rules
    assert "lord_connections" in rules
    assert "kavippu_afflictions" in rules
    assert "approaching_planets" in rules
    assert "crossed_planets" in rules


def test_jamakkol_watch_time_predictions():
    """Verify specific watch time relation calculations."""
    # Test with seed numbers to force relative distances
    # For instance seed 1 gives Arudham sign 1
    res = calculate_jamakkol_prasanam(
        query_dt_str="2026-10-28T09:15:00",
        latitude=13.0827,
        longitude=80.2707,
        tz_str="Asia/Kolkata",
        querent_seed=1,
    )
    rules = res["classical_rules"]
    assert rules["watch_time_relation"]["result"] in ["Success", "Failure", "Delay and Failure"]
    assert rules["facing_direction"]["facing_type"] in ["Ardhomukha", "Urdhomukha", "Triyangmukha"]
    assert rules["rising_nature"]["nature_type"] in ["Sirosodayam", "Pristodaya", "Siropristodaya"]
    assert isinstance(rules["subh_balance"]["is_subh_udayam"], bool)
    assert isinstance(rules["subh_balance"]["is_subh_arudam"], bool)


def test_jamakkol_calculation_nighttime():
    """Verify nighttime Jamakkol calculation (after sunset)."""
    payload = {
        "query_datetime": "2026-10-28T22:15:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "query_category": "lost_property",
    }
    response = client.post("/api/v1/jamakkol-prasanam/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["solar_info"]["is_day"] is False
    assert data["jamam_info"]["period_type"] == "Night"
    assert 1 <= data["jamam_info"]["jamam_number"] <= 8


def test_jamakkol_querent_seed_override():
    """Verify that specifying a seed number (1-108) correctly derives Aarudham."""
    payload = {
        "query_datetime": "2026-10-28T14:00:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "querent_seed": 7,  # Seed 7 -> (7-1)%12 + 1 = Sign 7 (Libra)
    }
    response = client.post("/api/v1/jamakkol-prasanam/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    aarudham = data["three_pillars"]["aarudham"]
    assert aarudham["sign_index"] == 7
    assert aarudham["sign_name_en"] == "Libra"
    assert "Seed Number (7)" in aarudham["calculation_basis"]


def test_direct_calculator_function():
    """Direct functional verification of calculator service."""
    res = calculate_jamakkol_prasanam(
        query_dt_str="2026-10-28T09:15:00",
        latitude=13.0827,
        longitude=80.2707,
        tz_str="Asia/Kolkata",
        query_category="health_illness",
    )
    assert "three_pillars" in res
    assert "prediction_verdict" in res
    assert "classical_rules" in res
    assert res["prediction_verdict"]["directional_guidance_en"] != ""


def test_jamakkol_specialized_domain_analyses():
    """Verify that all specialized domain analyses (Relationship, Politics, Foreign, Courts, Loans, Agri, Shares) are populated."""
    res = calculate_jamakkol_prasanam(
        query_dt_str="2026-10-28T11:45:00",
        latitude=13.0827,
        longitude=80.2707,
        tz_str="Asia/Kolkata",
    )
    rules = res["classical_rules"]
    assert "relationship_analysis" in rules
    assert "father" in rules["relationship_analysis"]
    assert "mother" in rules["relationship_analysis"]
    assert "wife" in rules["relationship_analysis"]
    assert "uncle" in rules["relationship_analysis"]

    assert "politics_govt_analysis" in rules
    assert "posts_breakdown" in rules["politics_govt_analysis"]
    assert "president" in rules["politics_govt_analysis"]["posts_breakdown"]
    assert "prime_minister" in rules["politics_govt_analysis"]["posts_breakdown"]

    assert "foreign_travel_analysis" in rules
    assert "travel_purpose_en" in rules["foreign_travel_analysis"]
    assert "citizenship_green_card_favorable" in rules["foreign_travel_analysis"]

    assert "court_case_analysis" in rules
    assert "kavippu_in_7th_house" in rules["court_case_analysis"]

    assert "loans_analysis" in rules
    assert "loan_approved" in rules["loans_analysis"]

    assert "agriculture_borewell_rain_analysis" in rules
    assert "rain_expected" in rules["agriculture_borewell_rain_analysis"]
    assert "borewell_water_available" in rules["agriculture_borewell_rain_analysis"]

    assert "share_market_analysis" in rules
    assert "commodities" in rules["share_market_analysis"]
    assert "gold" in rules["share_market_analysis"]["commodities"]

    assert "kavippu_bhava_effect" in rules
    assert "udayam_lord_thought" in rules
    assert "conjoined_inner_outer_planets" in rules
    assert "parivartana_exchanges" in rules
    assert "eighth_lord_in_udayam" in rules
    assert "snake_udayam_analysis" in rules

    # Verify evil spirits and black magic analysis
    assert "evil_spirits_black_magic_analysis" in rules
    es = rules["evil_spirits_black_magic_analysis"]
    assert "querent_under_evil_spirits" in es
    assert "perpetrator_profile" in es
    assert "haunted_residence_mandi_in_4th" in es

    # Verify natural vs unnatural death analysis
    assert "natural_unnatural_death_analysis" in rules
    assert "death_nature" in rules["natural_unnatural_death_analysis"]

    # Verify cyclone & disaster analysis
    assert "rain_disaster_catastrophe_analysis" in rules
    assert "cyclone_protection_active" in rules["rain_disaster_catastrophe_analysis"]

    # Verify Muhurta analysis
    assert "muhurta_analysis" in rules
    muh = rules["muhurta_analysis"]
    assert "marriage_muhurta" in muh
    assert "couple_reunion" in muh
    assert "business_startup_muhurta" in muh
    assert "construction_muhurta" in muh
    assert "loan_application_muhurta" in muh

    # Verify Planet attributes (Rays, Age, Height, Places, Direction)
    assert "planet_attributes_table" in rules
    assert "Sun" in rules["planet_attributes_table"]
    assert rules["planet_attributes_table"]["Sun"]["rays"] == 5
    assert rules["planet_attributes_table"]["Moon"]["rays"] == 21
