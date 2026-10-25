"""Unit & API Tests for Remedial Gemstone & Rudraksha Recommendation Engine.

Tests:
- Anukula (benefic strengthening) vs Pratikula (malefic pacification) doctrine
- Primary life stone (Lagnesha), lucky stone (5th), fortune stone (9th)
- Secondary support stone (Yogakaraka: Taurus, Cancer, Leo, Libra, Capricorn, Aquarius)
- Dynamic weight calculation (1 Ratti per 10 kg body weight)
- Rahu (Gomed) & Ketu (Vaiduryam) Ratna metadata and prohibition rules
- 1-to-14 Mukhi Rudraksha Catalogue + Gauri Shankar & Ganesh beads
- Personalized Rudraksha recommendations (Sade Sati, Kaal Sarp, Kuja Dosha)
- API endpoint integration
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.remedy_engine.gemstone_advisory import GemstoneAdvisoryEngine
from app.services.remedy_engine.rudraksha_advisory import RudrakshaAdvisoryEngine

client = TestClient(app)


def test_anukula_vs_pratikula_doctrine():
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Aries")
    assert adv.anukula_vs_pratikula_doctrine_en is not None
    assert "Anukula" in adv.anukula_vs_pratikula_doctrine_en["title"]
    assert "Pratikula" in adv.anukula_vs_pratikula_doctrine_en["title"]
    assert "Mani Mala" in adv.anukula_vs_pratikula_doctrine_en["authority"]

    assert adv.anukula_vs_pratikula_doctrine_ta is not None
    assert "அனுகூல" in adv.anukula_vs_pratikula_doctrine_ta["title"]


def test_secondary_support_stone_yogakarakas():
    # 1. Taurus Lagna -> Saturn is Yogakaraka (rules 9 & 10)
    adv_tau = GemstoneAdvisoryEngine.evaluate_advisory("Taurus")
    assert adv_tau.fortune_stone.graha == "saturn"

    # 2. Cancer Lagna -> Mars is Yogakaraka (rules 5 & 10)
    adv_can = GemstoneAdvisoryEngine.evaluate_advisory("Cancer")
    assert adv_can.lucky_stone.graha == "mars"

    # 3. Leo Lagna -> Mars is Yogakaraka (rules 4 & 9)
    adv_leo = GemstoneAdvisoryEngine.evaluate_advisory("Leo")
    assert adv_leo.fortune_stone.graha == "mars"

    # 4. Libra Lagna -> Saturn is Yogakaraka (rules 4 & 5)
    adv_lib = GemstoneAdvisoryEngine.evaluate_advisory("Libra")
    assert adv_lib.lucky_stone.graha == "saturn"

    # 5. Capricorn Lagna -> Venus is Yogakaraka (rules 5 & 10)
    adv_cap = GemstoneAdvisoryEngine.evaluate_advisory("Capricorn")
    assert adv_cap.lucky_stone.graha == "venus"

    # 6. Aquarius Lagna -> Venus is Yogakaraka (rules 4 & 9)
    adv_aqu = GemstoneAdvisoryEngine.evaluate_advisory("Aquarius")
    assert adv_aqu.fortune_stone.graha == "venus"


def test_dynamic_body_weight_formula():
    # 70 kg native -> 7.0 Rattis -> ~6.37 Carats
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Leo", body_weight_kg=70.0)
    assert adv.body_weight_kg == 70.0
    assert adv.life_stone.minimum_rattis == 7.0
    assert adv.life_stone.minimum_carats == 6.37
    assert "70.0 kg ÷ 10" in adv.life_stone.weight_guideline_formula_en
    assert "70.0 கிலோ ÷ 10" in adv.life_stone.weight_guideline_formula_ta


def test_rahu_and_ketu_gemstone_metadata():
    from app.services.remedy_engine.gemstone_advisory import PLANET_GEMSTONE_DATA
    assert "rahu" in PLANET_GEMSTONE_DATA
    assert "ketu" in PLANET_GEMSTONE_DATA

    rahu_data = PLANET_GEMSTONE_DATA["rahu"]
    assert "Hessonite" in rahu_data["primary_gem_en"]
    assert "கோமேதகம்" in rahu_data["primary_gem_ta"]
    assert rahu_data["consecration_mantra_sanskrit"]
    assert rahu_data["gayatri_mantra_sanskrit"]

    ketu_data = PLANET_GEMSTONE_DATA["ketu"]
    assert "Cat's Eye" in ketu_data["primary_gem_en"]
    assert "வைடூரியம்" in ketu_data["primary_gem_ta"]
    assert ketu_data["consecration_mantra_sanskrit"]


def test_rudraksha_catalogue_1_to_14_mukhi():
    all_beads = RudrakshaAdvisoryEngine.get_all_beads()
    assert len(all_beads) >= 16  # 1-14 + Gauri Shankar + Ganesh

    mukhis = {b.mukhi for b in all_beads if b.mukhi > 0}
    assert mukhis == set(range(1, 15))

    # Test 5 Mukhi (Kalagni Rudra / Universal)
    five_mukhi = next(b for b in all_beads if b.mukhi == 5)
    assert "Kalagni Rudra" in five_mukhi.ruling_deity_en
    assert five_mukhi.ruling_graha == "jupiter"
    assert "ஹ்ரீம்" in five_mukhi.beeja_mantra_ta

    # Test 7 Mukhi (Mahalakshmi / Saturn Sade Sati)
    seven_mukhi = next(b for b in all_beads if b.mukhi == 7)
    assert "Mahalakshmi" in seven_mukhi.ruling_deity_en
    assert seven_mukhi.ruling_graha == "saturn"
    assert "Sade Sati" in seven_mukhi.doshas_mitigated_en[0]


def test_personalized_rudraksha_recommendations():
    # 1. Sade Sati native should get 7 Mukhi
    rec_sade = RudrakshaAdvisoryEngine.evaluate_rudraksha("Cancer", has_sade_sati=True)
    assert rec_sade.primary_bead.mukhi == 7
    assert rec_sade.universal_bead.mukhi == 5

    # 2. Kaal Sarp native should get 8 Mukhi
    rec_kaal = RudrakshaAdvisoryEngine.evaluate_rudraksha("Gemini", has_kaal_sarp=True)
    assert rec_kaal.primary_bead.mukhi == 8

    # 3. Kuja Dosha native should get 3 Mukhi
    rec_kuja = RudrakshaAdvisoryEngine.evaluate_rudraksha("Virgo", has_kuja_dosha=True)
    assert rec_kuja.primary_bead.mukhi == 3


def test_api_gemstone_advisory_with_rudraksha_payload():
    payload = {
        "ascendant_sign": "Sagittarius",
        "body_weight_kg": 65.0,
    }
    resp = client.post("/api/v1/remedies/gemstones/advisory", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["lagna_sign"] == "Sagittarius"
    assert data["body_weight_kg"] == 65.0
    assert data["life_stone"]["graha"] == "jupiter"
    assert data["fortune_stone"]["graha"] == "sun"
    assert data["anukula_vs_pratikula_doctrine_en"] is not None
    assert data["recommended_rudraksha"] is not None
    assert len(data["rudraksha_catalog"]) >= 16


def test_api_rudraksha_matrix_endpoint():
    resp = client.get("/api/v1/remedies/rudraksha/matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_beads"] >= 16
    assert len(data["items"]) >= 16


def test_api_rudraksha_recommendation_endpoint():
    payload = {
        "ascendant_sign": "Scorpio",
        "has_kuja_dosha": True,
    }
    resp = client.post("/api/v1/remedies/rudraksha/recommendation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_bead"]["mukhi"] == 3
    assert data["universal_bead"]["mukhi"] == 5
