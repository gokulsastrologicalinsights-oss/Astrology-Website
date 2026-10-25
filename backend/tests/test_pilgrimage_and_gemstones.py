"""Tests for Kaveri Delta Navagraha Pilgrimage Circuit Planner & Gemstone Advisory Engine."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.remedy_engine.pilgrimage import PilgrimageCircuitEngine
from app.services.remedy_engine.gemstone_advisory import GemstoneAdvisoryEngine


client = TestClient(app)


# ==============================================================================
# 1. Pilgrimage Circuit Engine Unit Tests
# ==============================================================================

def test_standard_circuits_count_and_ids():
    circuits = PilgrimageCircuitEngine.get_standard_circuits()
    assert len(circuits) == 2
    c_ids = [c.circuit_id for c in circuits]
    assert "1_day_express" in c_ids
    assert "2_day_comprehensive" in c_ids


def test_1_day_express_circuit_structure():
    circuit = PilgrimageCircuitEngine.build_1_day_express_circuit()
    assert circuit.total_temples == 9
    assert len(circuit.day_plans) == 1
    day1 = circuit.day_plans[0]
    assert len(day1.temple_stops) == 9
    assert day1.base_camp_en == "Kumbakonam"
    assert day1.total_distance_km > 100.0

    # Verify all 9 grahas are present
    grahas = {s.graha for s in day1.temple_stops}
    assert grahas == {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}

    # Verify bilingual fields exist
    for stop in day1.temple_stops:
        assert stop.name_en and stop.name_ta
        assert stop.presiding_deity_en and stop.presiding_deity_ta
        assert stop.special_ritual_en and stop.special_ritual_ta
        assert stop.remedy_offerings_en and stop.remedy_offerings_ta
        assert stop.darshan_timings_en and stop.darshan_timings_ta


def test_2_day_comprehensive_circuit_structure():
    circuit = PilgrimageCircuitEngine.build_2_day_comprehensive_circuit()
    assert circuit.total_temples == 9
    assert len(circuit.day_plans) == 2

    day1 = circuit.day_plans[0]
    day2 = circuit.day_plans[1]
    assert len(day1.temple_stops) == 4  # Coastal/East: Mars, Mercury, Ketu, Saturn
    assert len(day2.temple_stops) == 5  # Central/West: Sun, Venus, Rahu, Jupiter, Moon

    all_grahas = {s.graha for s in day1.temple_stops} | {s.graha for s in day2.temple_stops}
    assert all_grahas == {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}


def test_personalized_circuit_chart_priority_flagging():
    chart_context = {
        "running_mahadasha": "Mars",
        "running_bhukti": "Rahu",
        "debilitated_planets": ["Jupiter"],
        "combust_planets": ["Venus"],
        "kuja_dosha_status": "present",
    }
    circuit = PilgrimageCircuitEngine.generate_personalized_circuit(chart_context, circuit_type="2_day")
    assert circuit.chart_priorities_present is True

    stops = [s for day in circuit.day_plans for s in day.temple_stops]
    priority_stops = [s for s in stops if s.is_chart_priority]

    priority_grahas = {s.graha for s in priority_stops}
    assert "mars" in priority_grahas
    assert "rahu" in priority_grahas
    assert "jupiter" in priority_grahas
    assert "venus" in priority_grahas

    # Check that reasons are populated
    for s in priority_stops:
        assert s.chart_priority_reason_en
        assert s.chart_priority_reason_ta


# ==============================================================================
# 2. Gemstone Advisory Engine Unit Tests
# ==============================================================================

def test_gemstone_advisory_aries_lagna():
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Aries")
    assert adv.lagna_sign == "Aries"

    # Life Stone: Mars (Red Coral)
    assert adv.life_stone.graha == "mars"
    assert "Coral" in adv.life_stone.primary_gem_en

    # Lucky Stone: Sun (Ruby)
    assert adv.lucky_stone.graha == "sun"
    assert "Ruby" in adv.lucky_stone.primary_gem_en

    # Fortune Stone: Jupiter (Yellow Sapphire)
    assert adv.fortune_stone.graha == "jupiter"
    assert "Yellow Sapphire" in adv.fortune_stone.primary_gem_en

    # Prohibited: Mercury rules 3rd and 6th (Dusthana)
    proh_grahas = [p.graha for p in adv.prohibited_gemstones]
    assert "mercury" in proh_grahas


def test_gemstone_advisory_taurus_lagna_yogakaraka():
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Taurus")
    assert adv.lagna_sign == "Taurus"

    # Life Stone: Venus (Diamond)
    assert adv.life_stone.graha == "venus"

    # Lucky Stone: Mercury (Emerald)
    assert adv.lucky_stone.graha == "mercury"

    # Fortune Stone: Saturn (Blue Sapphire) - 9th & 10th Yogakaraka!
    assert adv.fortune_stone.graha == "saturn"
    assert adv.fortune_stone.safety_status == "auspicious"

    # Jupiter rules 8th & 11th -> strictly prohibited
    proh_grahas = [p.graha for p in adv.prohibited_gemstones]
    assert "jupiter" in proh_grahas


def test_gemstone_advisory_cancer_lagna():
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Cancer")
    assert adv.lagna_sign == "Cancer"

    # Life Stone: Moon (Pearl)
    assert adv.life_stone.graha == "moon"
    # Lucky Stone: Mars (Red Coral) - 5th & 10th Yogakaraka!
    assert adv.lucky_stone.graha == "mars"
    # Fortune Stone: Jupiter (Yellow Sapphire)
    assert adv.fortune_stone.graha == "jupiter"

    # Saturn rules 7th & 8th -> strictly prohibited
    proh_grahas = [p.graha for p in adv.prohibited_gemstones]
    assert "saturn" in proh_grahas


def test_gemstone_advisory_pisces_lagna():
    adv = GemstoneAdvisoryEngine.evaluate_advisory("Pisces")
    assert adv.lagna_sign == "Pisces"

    # Life Stone: Jupiter (Yellow Sapphire)
    assert adv.life_stone.graha == "jupiter"
    # Lucky Stone: Moon (Pearl)
    assert adv.lucky_stone.graha == "moon"
    # Fortune Stone: Mars (Red Coral)
    assert adv.fortune_stone.graha == "mars"

    # Venus rules 3rd & 8th -> supreme functional malefic
    proh_grahas = [p.graha for p in adv.prohibited_gemstones]
    assert "venus" in proh_grahas


# ==============================================================================
# 3. FastAPI Endpoint Tests
# ==============================================================================

def test_api_get_pilgrimage_circuits():
    resp = client.get("/api/v1/remedies/pilgrimage/circuits")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["circuit_id"] == "1_day_express"
    assert data[1]["circuit_id"] == "2_day_comprehensive"


def test_api_post_personalized_pilgrimage():
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "circuit_type": "2_day",
    }
    resp = client.post("/api/v1/remedies/pilgrimage/personalized", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["circuit_id"] == "2_day_comprehensive"
    assert len(data["day_plans"]) == 2
    assert "rahu_kalam_guidelines_en" in data


def test_api_get_gemstone_advisory_by_lagna():
    payload = {"ascendant_sign": "Leo"}
    resp = client.post("/api/v1/remedies/gemstones/advisory", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lagna_sign"] == "Leo"
    assert data["life_stone"]["graha"] == "sun"
    assert data["fortune_stone"]["graha"] == "mars"
    assert len(data["prohibited_gemstones"]) > 0


def test_api_get_gemstone_advisory_by_live_coordinates():
    payload = {
        "birth_date": "1995-10-25",
        "birth_time": "06:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    resp = client.post("/api/v1/remedies/gemstones/advisory", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lagna_sign"]
    assert data["life_stone"]["primary_gem_en"]
    assert data["lucky_stone"]["primary_gem_en"]
    assert data["fortune_stone"]["primary_gem_en"]


def test_api_gemstone_advisory_invalid_lagna_400():
    payload = {"ascendant_sign": "Atlantis"}
    resp = client.post("/api/v1/remedies/gemstones/advisory", json=payload)
    assert resp.status_code == 400
