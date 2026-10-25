"""Unit and integration tests for Pancha Pakshi Shastra calculation engine."""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.services.pancha_pakshi.constants import (
    BIRDS,
    ACTIVITIES,
    SHUKLA_PAKSHA_STAR_BIRD,
    KRISHNA_PAKSHA_STAR_BIRD,
)
from app.services.pancha_pakshi.calculator import (
    get_birth_bird,
    calculate_pancha_pakshi_bio_rhythms,
)

client = TestClient(app)


def test_birth_bird_mapping_shukla_paksha():
    """Verify classical star-to-bird mapping for Shukla Paksha (வளர்பிறை)."""
    # 1. Ashwini (1) -> Vulture (வல்லூறு)
    b_ashwini = get_birth_bird(1, "shukla")
    assert b_ashwini["id"] == "vulture"
    assert b_ashwini["name_ta"] == "வல்லூறு"

    # 2. Ardra (6) -> Owl (ஆந்தை)
    b_ardra = get_birth_bird(6, "shukla")
    assert b_ardra["id"] == "owl"
    assert b_ardra["name_ta"] == "ஆந்தை"

    # 3. Uttara Phalguni (12) -> Crow (காகம்)
    b_uphal = get_birth_bird(12, "shukla")
    assert b_uphal["id"] == "crow"
    assert b_uphal["name_ta"] == "காகம்"

    # 4. Anuradha (17) -> Cock (கோழி)
    b_anuradha = get_birth_bird(17, "shukla")
    assert b_anuradha["id"] == "cock"
    assert b_anuradha["name_ta"] == "கோழி"

    # 5. Shravana (22) -> Peacock (மயில்)
    b_shravana = get_birth_bird(22, "shukla")
    assert b_shravana["id"] == "peacock"
    assert b_shravana["name_ta"] == "மயில்"


def test_birth_bird_mapping_krishna_paksha():
    """Verify classical star-to-bird mapping for Krishna Paksha (தேய்பிறை)."""
    # 1. Ashwini (1) -> Peacock (மயில்)
    b_ashwini = get_birth_bird(1, "krishna")
    assert b_ashwini["id"] == "peacock"
    assert b_ashwini["name_ta"] == "மயில்"

    # 2. Ardra (6) -> Cock (கோழி)
    b_ardra = get_birth_bird(6, "krishna")
    assert b_ardra["id"] == "cock"
    assert b_ardra["name_ta"] == "கோழி"

    # 3. Uttara Phalguni (12) -> Crow (காகம்)
    b_uphal = get_birth_bird(12, "krishna")
    assert b_uphal["id"] == "crow"
    assert b_uphal["name_ta"] == "காகம்"

    # 4. Anuradha (17) -> Owl (ஆந்தை)
    b_anuradha = get_birth_bird(17, "krishna")
    assert b_anuradha["id"] == "owl"
    assert b_anuradha["name_ta"] == "ஆந்தை"

    # 5. Shravana (22) -> Vulture (வல்லூறு)
    b_shravana = get_birth_bird(22, "krishna")
    assert b_shravana["id"] == "vulture"
    assert b_shravana["name_ta"] == "வல்லூறு"


def test_pancha_pakshi_computational_intervals():
    """Verify 5-Yamam and 25-Antara astronomical subdivisions and boundary continuity."""
    test_date = date(2026, 10, 18)
    res = calculate_pancha_pakshi_bio_rhythms(
        target_date=test_date,
        latitude=13.0827,
        longitude=80.2707,
        timezone_str="Asia/Kolkata",
        birth_nakshatra_idx=4,  # Rohini -> Vulture in Shukla
        birth_paksha="shukla",
    )

    assert res["birth_bird"]["id"] == "vulture"
    assert len(res["day_yamams"]) == 5
    assert len(res["night_yamams"]) == 5
    assert len(res["all_antaras"]) == 50  # 25 day + 25 night

    # First day yamam starts with sunrise
    day_1 = res["day_yamams"][0]
    assert day_1["start_time_local"] == res["astronomical"]["sunrise_local"]

    # Fifth day yamam ends with sunset
    day_5 = res["day_yamams"][4]
    assert day_5["end_time_local"] == res["astronomical"]["sunset_local"]

    # First night yamam starts with sunset
    night_1 = res["night_yamams"][0]
    assert night_1["start_time_local"] == res["astronomical"]["sunset_local"]

    # Fifth night yamam ends with next sunrise
    night_5 = res["night_yamams"][4]
    assert night_5["end_time_local"] == res["astronomical"]["next_sunrise_local"]

    # Sub-periods in Day Yamam 1 have power scores
    for sub in day_1["sub_periods"]:
        assert 0 <= sub["power_score"] <= 100
        assert sub["start_time_local"] != ""
        assert sub["end_time_local"] != ""

    # Golden windows have high power
    assert len(res["golden_windows"]) > 0
    for g in res["golden_windows"]:
        assert g["power_score"] >= 80

    # Padupakshi windows have low power
    assert len(res["padupakshi_windows"]) > 0
    for p in res["padupakshi_windows"]:
        assert p["power_score"] <= 25


def test_pancha_pakshi_api_endpoints():
    """Verify FastAPI GET /birds and POST /calculate endpoints."""
    # GET /birds
    get_res = client.get("/api/v1/pancha-pakshi/birds")
    assert get_res.status_code == 200
    birds_data = get_res.json()
    assert len(birds_data["birds"]) == 5
    assert "ruling" in birds_data["activities"]

    # POST /calculate
    post_payload = {
        "target_date": "2026-10-18",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "birth_nakshatra": 13,  # Hasta
        "birth_paksha": "shukla",
    }
    calc_res = client.post("/api/v1/pancha-pakshi/calculate", json=post_payload)
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["birth_bird"]["name_en"] == "Crow"
    assert len(calc_data["day_yamams"]) == 5
    assert len(calc_data["all_antaras"]) == 50
    assert calc_data["total_golden_windows"] > 0
