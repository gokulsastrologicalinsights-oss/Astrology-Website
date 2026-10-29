"""Unit and integration tests for Sannu Ahmed Vedic Astrology Rituals & Remedies engine."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.remedy_engine.sannu_rituals_engine import (
    SannuRitualsEngine,
    NAKSHATRA_RITUALS_ENCYCLOPEDIA,
    KARMA_ARCHITECTURE,
    SOUL_BODY_CIRCUIT,
    PROPITIATION_VS_EMPOWERMENT,
    PLANETARY_WEAKNESS_ATLAS,
    HOUSE_WEAKNESS_MANIFESTATION,
    NAKSHATRA_DOSHAS,
    SACRED_TIMING_RULES,
)

client = TestClient(app)


def test_all_27_nakshatras_present():
    """Verify all 27 classical nakshatras have complete sacred ritual attributes."""
    rituals = SannuRitualsEngine.get_all_nakshatra_rituals()
    assert len(rituals) == 27
    names = [r["name"] for r in rituals]
    assert "Ashwini" in names
    assert "Pushya" in names
    assert "Mula" in names
    assert "Revati" in names

    for r in rituals:
        assert r["number"] >= 1 and r["number"] <= 27
        assert r["ruling_deity"]
        assert r["animal_yoni"]
        assert r["tattva"] in ("Earth (Prithvi)", "Water (Apas)", "Fire (Agni)", "Air (Vayu)", "Ether (Akasha)")
        assert r["symbol"]
        assert r["esoteric_symbol_meaning"]
        assert r["sacred_geometry"]
        assert r["sound_mantra"]
        assert r["offerings_dravya"]
        assert r["ritual_procedure"]
        assert r["sacred_tree"]


def test_lookup_nakshatra_by_name():
    """Verify lookup by normalized name handles variations."""
    rohini = SannuRitualsEngine.get_nakshatra_ritual_by_name("Rohini")
    assert rohini is not None
    assert rohini["name"] == "Rohini"
    assert "Prajapati" in rohini["ruling_deity"]

    mula = SannuRitualsEngine.get_nakshatra_ritual_by_name("mula")
    assert mula is not None
    assert mula["name"] == "Mula"
    assert "Nirriti" in mula["ruling_deity"]

    none_res = SannuRitualsEngine.get_nakshatra_ritual_by_name("NonExistentStar")
    assert none_res is None


def test_gandanta_and_abhukta_mula_dosha_detection():
    """Verify Gandanta and Abhukta Mula are flagged when Moon is in critical junctions."""
    # Test Mula: Gandanta + Abhukta Mula + Vishaghati
    diag_mula = SannuRitualsEngine.diagnose_chart_karma_and_rituals(
        lagna_sign="Sagittarius",
        moon_sign="Sagittarius",
        moon_nakshatra="Mula",
        planets_dict={"moon": {"sign": "sagittarius", "house": 1}},
    )
    dosha_types = [d["dosha_type"] for d in diag_mula["detected_nakshatra_doshas"]]
    assert "gandanta_dosha" in dosha_types
    assert "abhukta_mula_dosha" in dosha_types
    assert "vishaghati_nakshatra" in dosha_types

    # Test Revati: Gandanta (Pisces-Aries knot)
    diag_revati = SannuRitualsEngine.diagnose_chart_karma_and_rituals(
        lagna_sign="Pisces",
        moon_sign="Pisces",
        moon_nakshatra="Revati",
        planets_dict={"moon": {"sign": "pisces", "house": 1}},
    )
    rev_doshas = [d["dosha_type"] for d in diag_revati["detected_nakshatra_doshas"]]
    assert "gandanta_dosha" in rev_doshas
    assert "abhukta_mula_dosha" not in rev_doshas


def test_propitiation_vs_empowerment_safeguards():
    """Verify Picatrix & BPHS rule: Afflicted planets get propitiation_only, Yogakarakas get empowerment_allowed."""
    diag = SannuRitualsEngine.diagnose_chart_karma_and_rituals(
        lagna_sign="Taurus",  # Saturn is Yogakaraka
        moon_sign="Taurus",
        moon_nakshatra="Rohini",
        planets_dict={"saturn": {"sign": "capricorn", "house": 9}, "sun": {"sign": "libra", "house": 6}},
        yogakaraka_planets=["saturn"],
        debilitated_planets=["sun"],
        combust_planets=["mercury"],
        functional_malefics=["jupiter"],
    )
    status_map = {item["graha"]: item for item in diag["propitiation_vs_empowerment_status"]}

    # Saturn: Yogakaraka, not afflicted -> empowerment_allowed
    assert status_map["saturn"]["action_type"] == "empowerment_allowed"
    assert status_map["saturn"]["gemstone_rules"] is not None

    # Sun: Debilitated in Libra -> propitiation_only
    assert status_map["sun"]["action_type"] == "propitiation_only"
    assert status_map["sun"]["charity_prescribed"] is not None
    assert "NEVER empower" in status_map["sun"]["justification_en"]

    # Mercury: Combust -> propitiation_only
    assert status_map["mercury"]["action_type"] == "propitiation_only"


def test_api_sannu_knowledge():
    """Test GET /api/v1/remedies/sannu-knowledge returns comprehensive overview."""
    resp = client.get("/api/v1/remedies/sannu-knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert "source" in data
    assert data["source"]["code"] == "SANNU_AHMED_RITUALS"
    assert "karma_architecture" in data
    assert "sanchita" in data["karma_architecture"]
    assert "soul_body_circuit" in data
    assert "propitiation_vs_empowerment" in data
    assert "nakshatra_doshas" in data


def test_api_nakshatra_rituals():
    """Test GET /api/v1/remedies/nakshatra-rituals and single lookup."""
    resp = client.get("/api/v1/remedies/nakshatra-rituals")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_nakshatras"] == 27
    assert len(data["items"]) == 27

    # Single lookup
    resp_single = client.get("/api/v1/remedies/nakshatra-rituals/Pushya")
    assert resp_single.status_code == 200
    p_data = resp_single.json()
    assert p_data["name"] == "Pushya"
    assert "Brihaspati" in p_data["ruling_deity"]
    assert p_data["symbol"] == "Cow's Udder or Blossoming Lotus"


def test_api_analyze_karma_rituals():
    """Test POST /api/v1/remedies/analyze-karma-rituals."""
    payload = {
        "ascendant_sign": "Cancer",
        "moon_sign": "Scorpio",
        "moon_nakshatra": "Jyeshtha",
        "running_mahadasha": "Saturn",
        "running_bhukti": "Mercury",
    }
    resp = client.post("/api/v1/remedies/analyze-karma-rituals", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["moon_nakshatra_ritual"]["name"] == "Jyeshtha"
    assert len(data["detected_nakshatra_doshas"]) >= 1
    assert "threefold_karma_blueprint" in data
    assert "sanchita" in data["threefold_karma_blueprint"]
    assert "prarabdha" in data["threefold_karma_blueprint"]
    assert "kriyamana" in data["threefold_karma_blueprint"]
    assert len(data["propitiation_vs_empowerment_status"]) == 9
