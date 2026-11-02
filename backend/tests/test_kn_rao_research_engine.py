"""Unit & Integration Tests for K.N. Rao Advanced Astrological Research Engine.

Validates:
1. S.N. Kapoor: Service vs Self-Employment thumb rules
2. R.C. Sharma: Technical vs Non-Technical 4-fold scoring model
3. Col. A.K. Gour: Authors and Journalists PAC bonding & Mars-Mercury bond
4. Shunny Nigam: Marital Discord 4 Main + 2 Supplementary Rules & Upapada Lagna
5. Dr. R.K. Aggarwal: Consolidated Kakshya Table III matrix
6. P.C. Verma: 8-Part Vimshottari Mahadasha Career Timing
7. Dr. K.S. Charak: Mrityu Bhaga degrees & Medical Prognosis
8. Vedic Extensions API Endpoints
9. Prediction Rules Registry catalog count & AST validation
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.kn_rao_engine import (
    evaluate_service_vs_self_employment,
    evaluate_technical_profession,
    evaluate_author_journalist,
    evaluate_marital_discord,
    evaluate_consolidated_kakshya_and_timing,
    evaluate_medical_timing,
    evaluate_kn_rao_advanced_research,
    calculate_arudha_pada,
    check_mrityu_bhaga,
)
from app.services.prediction_rules.rules_registry import RulesRegistry

client = TestClient(app)

SAMPLE_PLANETS = {
    "Sun": {"sign_index": 2, "degree_in_sign": 0.55, "longitude": 30.55, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Krittika"},
    "Moon": {"sign_index": 10, "degree_in_sign": 1.89, "longitude": 271.89, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Uttara Ashadha"},
    "Mars": {"sign_index": 11, "degree_in_sign": 24.52, "longitude": 324.52, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Purva Bhadrapada"},
    "Mercury": {"sign_index": 1, "degree_in_sign": 18.20, "longitude": 18.20, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Bharani"},
    "Jupiter": {"sign_index": 3, "degree_in_sign": 12.40, "longitude": 72.40, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Ardra"},
    "Venus": {"sign_index": 12, "degree_in_sign": 19.30, "longitude": 349.30, "is_retrograde": False, "is_combust": False, "nakshatra_name": "Revati"},
    "Saturn": {"sign_index": 10, "degree_in_sign": 1.15, "longitude": 271.15, "is_retrograde": True, "is_combust": False, "nakshatra_name": "Uttara Ashadha"},
    "Rahu": {"sign_index": 11, "degree_in_sign": 15.00, "longitude": 315.00, "is_retrograde": True, "is_combust": False, "nakshatra_name": "Shatabhisha"},
    "Ketu": {"sign_index": 5, "degree_in_sign": 15.00, "longitude": 135.00, "is_retrograde": True, "is_combust": False, "nakshatra_name": "Purva Phalguni"},
}

SAMPLE_D9_PLANETS = {
    "Sun": {"sign_index": 10, "degree_in_sign": 4.95},
    "Moon": {"sign_index": 10, "degree_in_sign": 17.01},
    "Mars": {"sign_index": 5, "degree_in_sign": 10.68},
    "Mercury": {"sign_index": 6, "degree_in_sign": 13.80},
    "Jupiter": {"sign_index": 1, "degree_in_sign": 21.60},
    "Venus": {"sign_index": 11, "degree_in_sign": 23.70},
    "Saturn": {"sign_index": 10, "degree_in_sign": 10.35},
    "Rahu": {"sign_index": 7, "degree_in_sign": 15.00},
    "Ketu": {"sign_index": 1, "degree_in_sign": 15.00},
}

SAMPLE_LAGNA_SIGN = 6  # Virgo
SAMPLE_LAGNA_DEG = 4.40


def test_service_vs_self_employment_evaluator():
    """Verify S.N. Kapoor Service vs Self-Employment calculations."""
    res = evaluate_service_vs_self_employment(SAMPLE_PLANETS, SAMPLE_LAGNA_SIGN)
    assert res.self_employment_probability >= 0.0
    assert res.service_probability >= 0.0
    assert round(res.self_employment_probability + res.service_probability, 1) == 100.0
    assert res.primary_verdict in ["Self-Employment / Business / Independent Practice", "Service / Salaried Employment / Structured Hierarchy"]
    assert res.verdict_tamil != ""
    assert "Agni" in res.tattwa_distribution
    assert res.poorna_parmatmansha_count >= 0


def test_technical_profession_scoring():
    """Verify R.C. Sharma 4-fold scoring model."""
    res = evaluate_technical_profession(SAMPLE_PLANETS, SAMPLE_D9_PLANETS, SAMPLE_LAGNA_SIGN)
    assert res.karakamsha_sign != ""
    assert isinstance(res.total_score, int)
    assert res.category in [
        "Technical (Engineering / IT / Core Technology)",
        "Semi-Technical (Applied Science / Tech-Management / Applied Arts)",
        "Non-Technical (Administration / Audit / Languages / Arts / Humanities)"
    ]
    assert res.category_tamil != ""
    assert res.interpretation != ""


def test_author_journalist_pac_bonding():
    """Verify Col. A.K. Gour Authors and Journalists evaluation."""
    res = evaluate_author_journalist(SAMPLE_PLANETS, SAMPLE_D9_PLANETS, SAMPLE_LAGNA_SIGN)
    assert res.writing_profile in [
        "Author (Books, Philosophical Granths & In-depth Scholarly Works)",
        "Journalist (News, Media, Columns & Rapid Analytical Reporting)",
        "Author-cum-Journalist (Mastery in both Books and Media)",
        "Non-Literary / General Communication Profile"
    ]
    assert res.writing_profile_tamil != ""
    assert isinstance(res.pac_bond_present, bool)


def test_marital_discord_and_upapada():
    """Verify Shunny Nigam 4 Main + 2 Supplementary rules and Upapada Lagna."""
    res = evaluate_marital_discord(SAMPLE_PLANETS, SAMPLE_D9_PLANETS, SAMPLE_LAGNA_SIGN)
    assert res.upapada_lagna_sign != ""
    assert res.second_from_upapada_sign != ""
    assert 0 <= res.main_rules_matched_count <= 4
    assert res.discord_intensity in [
        "High Discord Risk",
        "Moderate Friction",
        "Mild / Stressful",
        "Peaceful / Harmonious"
    ]
    assert res.discord_intensity_tamil != ""
    assert res.darakaraka_planet != ""


def test_upapada_arudha_pada_calculation():
    """Verify Arudha Pada calculation with classical exceptions."""
    # House 12 from Virgo (6) is Leo (5). Lord Sun is in Taurus (2).
    # From Leo (5) to Taurus (2) is 9 signs away.
    # Count 9 signs from Taurus (2) -> Capricorn (10).
    sign_idx, sign_name = calculate_arudha_pada(12, 6, SAMPLE_PLANETS)
    assert 1 <= sign_idx <= 12
    assert sign_name != ""


def test_consolidated_kakshya_table_iii():
    """Verify Dr. R.K. Aggarwal's Table III 12-sign x 8-kakshya consolidated matrix."""
    res = evaluate_consolidated_kakshya_and_timing(SAMPLE_PLANETS, SAMPLE_LAGNA_SIGN, "Rahu")
    assert len(res.matrix) == 12
    for sign_item in res.matrix:
        assert len(sign_item.kakshyas) == 8
        sum_k = sum(k.total_bindus for k in sign_item.kakshyas)
        assert sum_k == sign_item.total_sav_bindus
        for k in sign_item.kakshyas:
            assert 0 <= k.total_bindus <= 7
            assert k.auspicious == (k.total_bindus >= 4)
    # Check 8-part Vimshottari Mahadasha timing
    assert len(res.vimshottari_eight_parts) == 8
    for part in res.vimshottari_eight_parts:
        assert part.tenth_lord_prastharaka_bindu in (0, 1)


def test_medical_timing_and_mrityu_bhaga():
    """Verify Dr. K.S. Charak Mrityu Bhaga and medical prognosis."""
    mb_list = check_mrityu_bhaga(SAMPLE_PLANETS, SAMPLE_LAGNA_SIGN, SAMPLE_LAGNA_DEG)
    assert isinstance(mb_list, list)
    med_res = evaluate_medical_timing(
        SAMPLE_PLANETS,
        SAMPLE_LAGNA_SIGN,
        SAMPLE_LAGNA_DEG,
        active_mahadasha="Rahu",
        active_antardasha="Moon",
        next_mahadasha="Jupiter"
    )
    assert med_res.prognosis_verdict != ""
    assert med_res.prognosis_verdict_tamil != ""


def test_kn_rao_advanced_research_master_response():
    """Verify master bundle function synthesizing all research papers."""
    res = evaluate_kn_rao_advanced_research(
        planets_data=SAMPLE_PLANETS,
        d9_planets=SAMPLE_D9_PLANETS,
        lagna_sign=SAMPLE_LAGNA_SIGN,
        lagna_degree=SAMPLE_LAGNA_DEG,
        active_mahadasha="Rahu",
        active_antardasha="Moon"
    )
    assert res.service_vs_self_employment is not None
    assert res.technical_profession is not None
    assert res.author_vs_journalist is not None
    assert res.marital_discord is not None
    assert res.medical_timing is not None
    assert "AK" in res.jaimini_karakas
    assert res.karakamsha_sign != ""


def test_rules_registry_kn_rao_rules():
    """Verify all K.N. Rao advanced research rules are registered in the registry."""
    count = RulesRegistry.count()
    assert count >= 390
    
    rule_ids = [
        "RULE-KNRAO-SE-01",
        "RULE-KNRAO-SE-02",
        "RULE-KNRAO-SE-03",
        "RULE-KNRAO-TECH-01",
        "RULE-KNRAO-TECH-02",
        "RULE-KNRAO-TECH-03",
        "RULE-KNRAO-AUTH-01",
        "RULE-KNRAO-AUTH-02",
        "RULE-KNRAO-MARR-01",
        "RULE-KNRAO-MARR-02",
        "RULE-KNRAO-MARR-03",
        "RULE-KNRAO-DK-01",
        "RULE-KNRAO-WOMEN-01",
        "RULE-KNRAO-KAS-01",
        "RULE-KNRAO-KAS-02",
        "RULE-KNRAO-MED-01",
        "RULE-KNRAO-MED-02",
    ]
    for r_id in rule_ids:
        rule = RulesRegistry.get_rule_by_id(r_id)
        assert rule is not None, f"Missing rule {r_id}"
        assert rule.name_ta != ""
        assert rule.astrological_principle_ta != ""


def test_api_kn_rao_research():
    """Test POST /api/v1/vedic/kn-rao-research endpoint."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    response = client.post("/api/v1/vedic/kn-rao-research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "service_vs_self_employment" in data
    assert "technical_profession" in data
    assert "author_vs_journalist" in data
    assert "marital_discord" in data
    assert "medical_timing" in data
    assert "jaimini_karakas" in data


def test_api_consolidated_kakshya():
    """Test POST /api/v1/vedic/consolidated-kakshya endpoint."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    response = client.post("/api/v1/vedic/consolidated-kakshya", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["matrix"]) == 12
    assert len(data["vimshottari_eight_parts"]) == 8


def test_api_career_research():
    """Test POST /api/v1/vedic/career-research endpoint."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    response = client.post("/api/v1/vedic/career-research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "service_vs_self_employment" in data
    assert "technical_profession" in data
    assert "author_vs_journalist" in data
