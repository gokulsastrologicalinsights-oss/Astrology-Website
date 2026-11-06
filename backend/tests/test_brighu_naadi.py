"""Unit tests for Brighu Naadi Engine & Endpoints.

Validates Dr. N. Srinivasan Shastry's "Brighu Naadi Sangraha" principles:
- Jeeva Karaka (Jupiter) & Karma Karaka (Saturn)
- Vastu & Birth Environment (road direction, entrance door, temple)
- Exact milestone age timing (marriage, property, career, fame, danger)
- Physical & health markers
"""

import pytest
from app.services.brighu_naadi.engine import evaluate_brighu_naadi
from app.services.brighu_naadi.registry import (
    ROAD_DIRECTION_MAP,
    DOOR_FACING_MAP,
    TEMPLE_NEAR_BIRTH_MAP,
    MARRIAGE_AGE_BY_VENUS_FROM_JUPITER,
    PROPERTY_AGE_BY_JUPITER_FROM_MARS,
)


def test_brighu_naadi_case_study_evaluation():
    """Validates the Case Study Horoscope from pages 128-129 of Brighu Naadi Sangraha.

    Chart:
    Jupiter in Sagittarius (sign 9)
    Saturn in Sagittarius (sign 9)
    Sun in Virgo (sign 6)
    Mercury in Virgo (sign 6)
    Mars in Gemini (sign 3)
    Moon in Libra (sign 7)
    Venus in Libra (sign 7)
    Rahu in Leo (sign 5)
    Ketu in Aquarius (sign 11)
    Ascendant in Scorpio (sign 8)
    """
    planets_data = {
        "Jupiter": {"sign_index": 9, "degree": 12.0, "is_retrograde": False},
        "Saturn": {"sign_index": 9, "degree": 14.0, "is_retrograde": False},
        "Sun": {"sign_index": 6, "degree": 18.0, "is_retrograde": False},
        "Mercury": {"sign_index": 6, "degree": 22.0, "is_retrograde": False},
        "Mars": {"sign_index": 3, "degree": 8.0, "is_retrograde": False},
        "Moon": {"sign_index": 7, "degree": 15.0, "is_retrograde": False},
        "Venus": {"sign_index": 7, "degree": 20.0, "is_retrograde": False},
        "Rahu": {"sign_index": 5, "degree": 4.0, "is_retrograde": False},
        "Ketu": {"sign_index": 11, "degree": 4.0, "is_retrograde": False},
    }

    res = evaluate_brighu_naadi(
        planets_data=planets_data,
        ascendant_sign=8,
        gender="male",
    )

    # 1. Vastu / Birth Environment
    # Rahu in Leo (sign 5): Road is East to West, Door facing East, City sector Eastern part
    assert res.birth_environment.road_direction_en == "East to West"
    assert res.birth_environment.door_facing_en == "Facing East"
    assert "Eastern part" in res.birth_environment.city_sector_en
    # Sun in Virgo (sign 6): Vishnu Temple
    assert "Vishnu" in res.birth_environment.temple_near_birth_en

    # 2. Jeeva Karaka (Jupiter)
    assert res.jeeva_karaka.sign == "Sagittarius"
    assert res.jeeva_karaka.prosperity_after_41 is True  # In Sagittarius
    # Planents in bhavas from Jupiter
    # Sun and Mercury in Virgo (sign 6) -> 10th from Sagittarius (9 -> 6 is 10 houses)
    assert "Sun" in res.jeeva_karaka.planets_in_bhavas_from_jupiter[10]
    assert "Mercury" in res.jeeva_karaka.planets_in_bhavas_from_jupiter[10]

    # 3. Karma Karaka (Saturn)
    assert res.karma_karaka.sign == "Sagittarius"
    # Saturn conjoined with Jupiter
    assert any("Banking" in f or "Astrology" in f for f in res.karma_karaka.career_fields_en)

    # 4. Marriage Timing
    # Venus in Libra (sign 7) from Jupiter in Sagittarius (sign 9): (7 - 9) % 12 + 1 = 11th house
    # In table, Venus in 11th from Jupiter gives marriage at 22-23 years!
    marr_milestone = next((m for m in res.timing_milestones if m.category == "marriage"), None)
    assert marr_milestone is not None
    assert 22 in marr_milestone.age_years or 23 in marr_milestone.age_years

    # 5. Property Timing
    # Jupiter in Sagittarius (sign 9) from Mars in Gemini (sign 3): (9 - 3) % 12 + 1 = 7th house
    # In table, Jupiter in 7th from Mars gives property/land at 31/43!
    prop_milestone = next((m for m in res.timing_milestones if m.category == "property"), None)
    assert prop_milestone is not None
    assert 31 in prop_milestone.age_years

    # 6. Physical Markers
    assert len(res.physical_health_markers) >= 3


def test_api_endpoint(client=None):
    """Test FastAPI endpoint for Brighu Naadi calculation."""
    from fastapi.testclient import TestClient
    from app.main import app

    test_client = TestClient(app)
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "gender": "male",
        "ayanamsa": 0,
    }
    response = test_client.post("/api/v1/vedic/brighu-naadi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "birth_environment" in data
    assert "jeeva_karaka" in data
    assert "karma_karaka" in data
    assert "timing_milestones" in data
    assert len(data["timing_milestones"]) > 0
    assert "bnn_research_metadata" in data
    assert "bnn_directional_groups" in data
    assert "bnn_20_rules_evaluations" in data
    assert len(data["bnn_20_rules_evaluations"]) == 20


def test_bnn_research_paper_rules_and_directions():
    """Validates Bhrigu Nandi Nadi (R. G. Rao system) academic rules from A. Jagadeesan & Dr. K. Jothimani (IJCRME 2022)."""
    planets_data = {
        "Jupiter": {"sign_index": 9, "degree": 12.0, "is_retrograde": False},
        "Saturn": {"sign_index": 7, "degree": 14.0, "is_retrograde": True},  # Exalted Libra, Retrograde
        "Sun": {"sign_index": 6, "degree": 18.0, "is_retrograde": False},
        "Mercury": {"sign_index": 6, "degree": 22.0, "is_retrograde": False},
        "Mars": {"sign_index": 3, "degree": 8.0, "is_retrograde": False},
        "Moon": {"sign_index": 2, "degree": 15.0, "is_retrograde": False},
        "Venus": {"sign_index": 7, "degree": 20.0, "is_retrograde": False},
        "Rahu": {"sign_index": 5, "degree": 4.0, "is_retrograde": False},
        "Ketu": {"sign_index": 11, "degree": 4.0, "is_retrograde": False},
    }

    # Female chart: Venus is Jeeva Karaka per R. G. Rao BNN
    res_female = evaluate_brighu_naadi(
        planets_data=planets_data,
        ascendant_sign=8,
        gender="female",
    )
    assert res_female.jeeva_karaka.primary_karaka_planet == "Venus"
    assert res_female.jeeva_karaka.gender_applied == "female"

    # Direction of Saturn: Libra (sign 7) is Air/West
    assert "West" in res_female.karma_karaka.direction
    # Saturn in Libra exalted career
    assert "judge" in (res_female.karma_karaka.saturn_sign_career_en or "").lower() or "legal" in (res_female.karma_karaka.saturn_sign_career_en or "").lower()

    # Rule 10: Rahu in 5 (Leo), Ketu in 11 (Aquarius).
    # Jupiter in 9 (Sagittarius) is in side between 5 and 11.
    # Saturn in 7 (Libra) is also in side between 5 and 11.
    assert res_female.rahu_ketu_axis_career_outside is not None

    # Check the 20 rules
    assert len(res_female.bnn_20_rules_evaluations) == 20
    # Rule 14 should be active because Saturn is retrograde
    r14 = next((r for r in res_female.bnn_20_rules_evaluations if r["rule_number"] == 14), None)
    assert r14 is not None
    assert r14["is_active"] is True


def test_bnn_500_charts_new_rules_and_karmic_remedies():
    """Validates R. G. Rao's Bhrigu Nandi Nadi (500 Charts) specialized rules and karmic remedies."""
    planets = {
        "Jupiter": {"sign_index": 1, "degree": 10.0, "is_retrograde": False},
        "Rahu": {"sign_index": 1, "degree": 12.0, "is_retrograde": False},
        "Saturn": {"sign_index": 7, "degree": 14.0, "is_retrograde": False},
        "Moon": {"sign_index": 7, "degree": 12.0, "is_retrograde": False},
        "Sun": {"sign_index": 3, "degree": 15.0, "is_retrograde": False},
        "Mercury": {"sign_index": 4, "degree": 20.0, "is_retrograde": False},
        "Mars": {"sign_index": 5, "degree": 5.0, "is_retrograde": False},
        "Venus": {"sign_index": 6, "degree": 10.0, "is_retrograde": False},
        "Ketu": {"sign_index": 7, "degree": 12.0, "is_retrograde": False},
    }

    res = evaluate_brighu_naadi(planets, ascendant_sign=1, gender="male")
    matched_ids = [m.rule_id for m in res.matched_rules]

    # Chandra Mouli Yoga: Saturn + Moon in Libra
    assert "BN-SAT-013" in matched_ids

    # Guru Chandal Yoga: Jupiter + Rahu
    assert "BN-JUP-018" in matched_ids

    # Daivadroha / Sadhu Curse: Jupiter + Rahu with Saturn in 7th
    assert "BN-KRM-001" in matched_ids

    # Check that interpretation contains Somavara Vratam remedy
    krm1 = next(m for m in res.matched_rules if m.rule_id == "BN-KRM-001")
    assert "Somavara" in krm1.interpretation_en or "Gokarna" in krm1.interpretation_en


def test_pankajj_duaa_bnn_compendium():
    """Validates BNN Astrology Notes by Pankajj K Duaa compendium integration."""
    planets = {
        "Jupiter": {"sign_index": 1, "degree": 10.0, "is_retrograde": False},  # Aries (1)
        "Sun": {"sign_index": 11, "degree": 28.5, "is_retrograde": False},  # Aquarius (11) - near border (next house Pisces)
        "Saturn": {"sign_index": 7, "degree": 14.0, "is_retrograde": False},  # Libra (7)
        "Rahu": {"sign_index": 7, "degree": 16.0, "is_retrograde": False},  # Libra (7) - Saturn + Rahu Cancer Yoga
        "Ketu": {"sign_index": 1, "degree": 16.0, "is_retrograde": False},  # Aries (1)
        "Mars": {"sign_index": 4, "degree": 2.0, "is_retrograde": False},  # Cancer (4) - 0-3 deg border
        "Venus": {"sign_index": 4, "degree": 5.0, "is_retrograde": False},  # Cancer (4) - Venus + Mars Colonizer Yoga
        "Moon": {"sign_index": 8, "degree": 15.0, "is_retrograde": False},  # Scorpio (8)
        "Mercury": {"sign_index": 12, "degree": 20.0, "is_retrograde": False},  # Pisces (12)
    }

    res = evaluate_brighu_naadi(planets, ascendant_sign=1, gender="male")

    # Verify that pankajj_duaa_compendium is present in response
    assert res.pankajj_duaa_compendium is not None
    pkd = res.pankajj_duaa_compendium

    # 1. Metadata check
    assert "Pankajj K Duaa" in pkd["metadata"]["title"]

    # 2. Rashi mobility summary
    mob = pkd["rashi_mobility_summary"]
    assert mob["char_movable_count"] > 0

    # 3. Naadi house quality
    hq = pkd["naadi_house_qualities"]
    assert "Sun" in hq
    assert hq["Sun"]["house"] == 11
    assert "Good" in hq["Sun"]["status"]

    # 4. Medical astrology: Cancer yoga check (Saturn + Rahu in same sign Libra)
    med = pkd["medical_astrology"]
    assert med["cancer_yoga"]["is_active"] is True

    # 5. Organ afflictions: house 7 holds Saturn & Rahu (enemies)
    afflictions = med["organ_afflictions"]
    assert any(a["house"] == 7 for a in afflictions)

    # 6. Matched Yogas
    yogas = pkd["matched_yogas"]
    yoga_names = [y["yoga_name"] for y in yogas]
    # Venus + Mars Colonizer Yoga
    assert any("Colonizer" in name for name in yoga_names)
    # Sun in 11th House Vegetarian Mandate
    assert any("Sun in 11th House" in name for name in yoga_names)

    # 7. Degree border alerts: Sun is at 28.5 deg
    deg_alerts = pkd["degree_border_alerts"]
    assert any(d["planet"] == "Sun" and "NEXT house" in d["shift_en"] for d in deg_alerts)

    # 8. Prescribed Remedies
    remedies = pkd["prescribed_remedies"]
    assert len(remedies) > 0
    # Must have remedies for Saturn / Rahu
    rem_planets = [r["planet"] for r in remedies]
    assert "Saturn" in rem_planets or "Rahu" in rem_planets


def test_brighu_prashna_oracle():
    """Validates R. G. Rao's Brighu Prashna Nadi oracle engine and API."""
    from app.schemas.brighu_naadi import BrighuPrashnaRequest
    from app.services.brighu_naadi.prashna_engine import evaluate_brighu_prashna
    from fastapi.testclient import TestClient
    from app.main import app

    # Example 1 from page 7 of Brighu Prashna Nadi:
    # Native born 15-02-1955, query on 01-04-1993 -> Completed age 38 -> 107 - 38 = 69
    req = BrighuPrashnaRequest(
        birth_date="1955-02-15",
        query_date="1993-04-01",
        query_category="general",
    )
    res = evaluate_brighu_prashna(req)
    assert res.completed_age == 38
    assert res.prediction_number == 69
    assert "Sthagitha" in res.yoga_name_en
    assert "Sarva Kaame Vijayee Bhava" in res.yoga_name_en or "SARVA KAAME" in (res.sanskrit_sloka or "")
    assert "ANNA DANA" in res.prescribed_remedy_en

    # Example 2: Infant under 1 year of age -> maps to 107
    req_infant = BrighuPrashnaRequest(completed_age=0)
    res_infant = evaluate_brighu_prashna(req_infant)
    assert res_infant.prediction_number == 107
    assert "Suyoga" in res_infant.yoga_name_en

    # Test FastAPI endpoint
    client = TestClient(app)
    resp = client.post(
        "/api/v1/vedic/brighu-naadi/prashna",
        json={"completed_age": 36},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["prediction_number"] == 71  # 107 - 36 = 71
    assert "Shani-Angaraka" in data["yoga_name_en"] or "Angaraka" in data["yoga_name_en"]


