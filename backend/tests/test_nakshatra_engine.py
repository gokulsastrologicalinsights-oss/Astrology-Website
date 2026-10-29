"""Tests for 28 Nakshatras Engine & Electional Suitability."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.nakshatra_engine import (
    get_all_nakshatras,
    get_nakshatra_by_id_or_name,
    get_functional_natures_summary,
    check_activity_suitability,
    evaluate_birth_star_pada,
    get_28_nakshatra_table,
    NAKSHATRAS_CATALOG,
    FUNCTIONAL_NATURE_GROUPS,
    NAKSHATRAS_SUMMARY_TABLE,
)
from app.services.prediction_rules.rules_registry import RulesRegistry

client = TestClient(app)


def test_nakshatras_catalog_integrity():
    """Verify all 28 Nakshatras exist and have complete attributes."""
    assert len(NAKSHATRAS_CATALOG) == 28

    expected_names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Abhijit"
    ]

    for idx, expected in enumerate(expected_names, start=1):
        item = NAKSHATRAS_CATALOG[idx - 1]
        assert item["id"] == idx
        assert item["name"] == expected
        assert len(item["name_tamil"]) > 0
        assert len(item["ruling_deity"]) > 0
        assert item["gaze_direction"] in ("Forward", "Upward", "Downward")
        assert item["result_grade"] in ("GOOD", "OK", "HARM", "MISERY")
        assert len(item["padas"]) == 4
        for p in item["padas"]:
            assert p["pada_number"] in (1, 2, 3, 4)
            assert len(p["traits"]) > 0


def test_summary_table():
    """Verify classical 28 Nakshatras summary table."""
    table = get_28_nakshatra_table()
    assert len(table) == 28
    assert table[0]["name"] == "ASWINI"
    assert table[0]["direction"] == "FORWARD"
    assert table[27]["name"] == "ABHIJIT"
    assert table[27]["nature"] == "BRAHMA"
    assert table[27]["direction"] == "UPWARD"


def test_functional_natures():
    """Verify the 7 functional transit categories."""
    summary = get_functional_natures_summary()
    assert len(summary) == 7
    expected_categories = ["FIXED", "SOFT", "LIGHT", "DREADFUL", "MOVABLE", "FIERCE", "MIXED"]
    for cat in expected_categories:
        assert cat in summary
        assert len(summary[cat]["nakshatras"]) > 0
        assert len(summary[cat]["suitable_actions_en"]) > 0

    # Test individual memberships
    assert "Rohini" in summary["FIXED"]["nakshatras"]
    assert "Uttara Phalguni" in summary["FIXED"]["nakshatras"]
    assert "Mrigashira" in summary["SOFT"]["nakshatras"]
    assert "Ashwini" in summary["LIGHT"]["nakshatras"]
    assert "Ardra" in summary["DREADFUL"]["nakshatras"]
    assert "Swati" in summary["MOVABLE"]["nakshatras"]
    assert "Bharani" in summary["FIERCE"]["nakshatras"]
    assert "Krittika" in summary["MIXED"]["nakshatras"]
    assert "Vishakha" in summary["MIXED"]["nakshatras"]


def test_activity_suitability():
    """Verify electional activity recommendations."""
    # Laying foundation in Fixed Rohini
    res_rohini = check_activity_suitability("laying foundations", "Rohini")
    assert res_rohini["valid"] is True
    assert res_rohini["is_suitable"] is True

    # Warfare in Sharp/Dreadful Ardra
    res_ardra = check_activity_suitability("warfare", "Ardra")
    assert res_ardra["valid"] is True
    assert res_ardra["is_suitable"] is True

    # Marriage in Fierce Bharani
    res_bharani = check_activity_suitability("marriage", "Bharani")
    assert res_bharani["valid"] is True
    assert res_bharani["recommendation"] == "AVOID"


def test_pada_doshas_and_remedies():
    """Verify specific classical Pada blemishes and remedial upayas."""
    # 1. Ashwini Pada 1
    ash_p1 = evaluate_birth_star_pada("Ashwini", 1)
    assert ash_p1["has_dosha"] is True
    assert "father" in ash_p1["dosha_affects"].lower() or "child" in ash_p1["dosha_affects"].lower()
    assert "gold" in ash_p1["remedial_upaya"].lower()

    # 2. Ashwini Pada 2 (clean)
    ash_p2 = evaluate_birth_star_pada("Ashwini", 2)
    assert ash_p2["has_dosha"] is False
    assert ash_p2["remedial_upaya"] is not None  # Falls back to general upaya if present

    # 3. Bharani Pada 3
    bhar_p3 = evaluate_birth_star_pada("Bharani", 3)
    assert bhar_p3["has_dosha"] is True
    assert "father" in bhar_p3["dosha_affects"].lower()
    assert "annadaanam" in bhar_p3["remedial_upaya"].lower() or "meal" in bhar_p3["remedial_upaya"].lower()

    # 4. Rohini Pada 1
    roh_p1 = evaluate_birth_star_pada("Rohini", 1)
    assert roh_p1["has_dosha"] is True
    assert "mother" in roh_p1["dosha_affects"].lower()
    assert "gingelly" in roh_p1["remedial_upaya"].lower() or "sesame" in roh_p1["remedial_upaya"].lower()

    # 5. Ashlesha Pada 3 (Gandanta)
    ashl_p3 = evaluate_birth_star_pada("Ashlesha", 3)
    assert ashl_p3["has_dosha"] is True
    assert ashl_p3["is_severe_gandanta"] is True
    assert "21" in ashl_p3["remedial_upaya"]

    # 6. Jyeshtha Pada 4 (Gandanta)
    jyes_p4 = evaluate_birth_star_pada("Jyeshtha", 4)
    assert jyes_p4["has_dosha"] is True
    assert "godaan" in jyes_p4["remedial_upaya"].lower() or "cow" in jyes_p4["remedial_upaya"].lower()

    # 7. Mula Pada 1 (Gandanta)
    mula_p1 = evaluate_birth_star_pada("Mula", 1)
    assert mula_p1["has_dosha"] is True
    assert "buffalo" in mula_p1["remedial_upaya"].lower()

    # 8. Revati Pada 4 (Gandanta)
    rev_p4 = evaluate_birth_star_pada("Revati", 4)
    assert rev_p4["has_dosha"] is True
    assert "gold" in rev_p4["remedial_upaya"].lower()


def test_api_endpoints():
    """Verify FastAPI router endpoints."""
    # List all
    r = client.get("/api/v1/nakshatras")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 28

    # Filter by nature
    r_fixed = client.get("/api/v1/nakshatras?nature=Fixed")
    assert r_fixed.status_code == 200
    assert len(r_fixed.json()) == 4

    # Summary table
    r_tab = client.get("/api/v1/nakshatras/summary-table")
    assert r_tab.status_code == 200
    assert len(r_tab.json()) == 28

    # Functional natures
    r_fn = client.get("/api/v1/nakshatras/functional-natures")
    assert r_fn.status_code == 200
    assert "FIXED" in r_fn.json()
    assert "MIXED" in r_fn.json()

    # Single lookup by id and name
    r_single = client.get("/api/v1/nakshatras/4")
    assert r_single.status_code == 200
    assert r_single.json()["name"] == "Rohini"

    r_single_name = client.get("/api/v1/nakshatras/Revati")
    assert r_single_name.status_code == 200
    assert r_single_name.json()["id"] == 27

    # Check activity
    r_act = client.post("/api/v1/nakshatras/check-activity", json={
        "activity": "constructing a house",
        "nakshatra": "Rohini"
    })
    assert r_act.status_code == 200
    assert r_act.json()["is_suitable"] is True

    # Pada dosha
    r_pd = client.post("/api/v1/nakshatras/pada-dosha", json={
        "nakshatra": "Ashwini",
        "pada": 1
    })
    assert r_pd.status_code == 200
    assert r_pd.json()["has_dosha"] is True
    assert "gold" in r_pd.json()["remedial_upaya"].lower()

    # E-Book Treatise endpoint
    r_tr = client.get("/api/v1/nakshatras/treatise")
    assert r_tr.status_code == 200
    assert "chapters" in r_tr.json()
    assert len(r_tr.json()["chapters"]) == 12

    # Star prediction endpoint
    r_pred = client.get("/api/v1/nakshatras/prediction/Ashwini?pada=1")
    assert r_pred.status_code == 200
    pred_data = r_pred.json()
    assert pred_data["valid"] is True
    assert "moon_prediction" in pred_data
    assert "ascendant_prediction" in pred_data
    assert pred_data["selected_pada"] == 1
    assert pred_data["selected_pada_detail"]["dosha_status"] == "Dosha Present"


def test_prediction_rules_extension():
    """Verify prediction rules registry now contains the extended Nakshatra rules."""
    all_rules = RulesRegistry.get_all_rules()
    rule_ids = {r.rule_id for r in all_rules}

    # Verify new moon nakshatra rules
    assert "RULE-STAR-ROHINI" in rule_ids
    assert "RULE-STAR-16" in rule_ids
    assert "RULE-STAR-17" in rule_ids
    assert "RULE-STAR-18" in rule_ids
    assert "RULE-STAR-19" in rule_ids
    assert "RULE-STAR-20" in rule_ids
    assert "RULE-STAR-21" in rule_ids
    assert "RULE-STAR-22" in rule_ids
    assert "RULE-STAR-23" in rule_ids
    assert "RULE-STAR-24" in rule_ids
    assert "RULE-STAR-25" in rule_ids
    assert "RULE-STAR-26" in rule_ids

    # Verify mixed functional nature rule
    assert "RULE-NAK-MIXED-01" in rule_ids

    # Verify Pada dosha rules
    assert "RULE-PADA-DOSH-ASHWINI-1" in rule_ids
    assert "RULE-PADA-DOSH-ROHINI-123" in rule_ids
    assert "RULE-PADA-DOSH-ASHLESHA-GANDANTA" in rule_ids
    assert "RULE-PADA-DOSH-MAGHA-1" in rule_ids
    assert "RULE-PADA-DOSH-JYESTHA-GANDANTA" in rule_ids
    assert "RULE-PADA-DOSH-MULA-GANDANTA" in rule_ids
    assert "RULE-PADA-DOSH-REVATI-4" in rule_ids
