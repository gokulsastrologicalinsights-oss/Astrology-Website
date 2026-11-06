"""Comprehensive test suite for KP Reader 2 (Fundamental Principles) integration."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.kp_engine.reader2 import (
    classify_sign,
    evaluate_astrologer_proficiency,
    evaluate_speech_and_fertility,
    evaluate_karma_category,
    calculate_kp_fortuna,
    POSITIVE_SIGNS,
    NEGATIVE_SIGNS,
    NORTHERN_SIGNS,
    SOUTHERN_SIGNS,
    EQUINOCTIAL_SIGNS,
    TROPICAL_SIGNS,
    FIERY_SIGNS,
    EARTHY_SIGNS,
    AIRY_SIGNS,
    WATERY_SIGNS,
    MOVABLE_SIGNS,
    FIXED_SIGNS,
    COMMON_SIGNS,
    FRUITFUL_SIGNS,
    BARREN_SIGNS,
    MUTE_SIGNS,
    VOICE_SIGNS,
    VIOLENT_SIGNS,
    HUMAN_SIGNS,
    BESTIAL_SIGNS,
    DUAL_SIGNS,
    BICORPORAL_SIGNS,
    SHORT_ASCENSION_SIGNS_NORTH,
    LONG_ASCENSION_SIGNS_NORTH,
    SIGN_SIGNIFICATIONS,
    HOUSE_SIGNIFICATIONS_KP,
    PLANET_SIGNIFICATIONS_KP,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. 13-fold Zodiac Classifications Tests
# ---------------------------------------------------------------------------

def test_sign_classification_cardinalities():
    """Verify total counts across all 13 classical divisions."""
    assert len(POSITIVE_SIGNS) == 6
    assert len(NEGATIVE_SIGNS) == 6
    assert set(POSITIVE_SIGNS) | set(NEGATIVE_SIGNS) == set(SIGN_SIGNIFICATIONS.keys())

    assert len(NORTHERN_SIGNS) == 6
    assert len(SOUTHERN_SIGNS) == 6

    assert len(EQUINOCTIAL_SIGNS) == 2
    assert "Aries" in EQUINOCTIAL_SIGNS and "Libra" in EQUINOCTIAL_SIGNS

    assert len(TROPICAL_SIGNS) == 2
    assert "Cancer" in TROPICAL_SIGNS and "Capricorn" in TROPICAL_SIGNS

    assert len(FIERY_SIGNS) == 3
    assert len(EARTHY_SIGNS) == 3
    assert len(AIRY_SIGNS) == 3
    assert len(WATERY_SIGNS) == 3

    assert len(MOVABLE_SIGNS) == 4
    assert len(FIXED_SIGNS) == 4
    assert len(COMMON_SIGNS) == 4

    assert len(FRUITFUL_SIGNS) == 3
    assert set(FRUITFUL_SIGNS) == {"Cancer", "Scorpio", "Pisces"}

    assert len(BARREN_SIGNS) == 4
    assert set(BARREN_SIGNS) == {"Aries", "Gemini", "Leo", "Virgo"}

    assert len(MUTE_SIGNS) == 3
    assert set(MUTE_SIGNS) == {"Cancer", "Scorpio", "Pisces"}

    assert len(VOICE_SIGNS) == 3
    assert set(VOICE_SIGNS) == {"Gemini", "Libra", "Aquarius"}

    assert set(VIOLENT_SIGNS) == {"Aries", "Scorpio"}
    assert set(DUAL_SIGNS) == {"Gemini", "Sagittarius", "Pisces"}
    assert set(BICORPORAL_SIGNS) == {"Gemini", "Sagittarius", "Pisces"}


def test_classify_sign_helper():
    """Verify detailed 13-fold classification for individual signs."""
    aries_cls = classify_sign("Aries")
    assert aries_cls.polarity == "Positive"
    assert aries_cls.gender == "Masculine"
    assert aries_cls.hemisphere == "Northern"
    assert aries_cls.element == "Fiery"
    assert aries_cls.mobility == "Movable"
    assert aries_cls.guna == "Rajas"
    assert aries_cls.fertility == "Barren"
    assert aries_cls.is_violent is True
    assert aries_cls.is_bestial is True
    assert aries_cls.ascension_north == "Short"

    cancer_cls = classify_sign("Cancer")
    assert cancer_cls.polarity == "Negative"
    assert cancer_cls.element == "Watery"
    assert cancer_cls.fertility == "Fruitful"
    assert cancer_cls.speech_type == "Mute"
    assert cancer_cls.ascension_north == "Long"

    gemini_cls = classify_sign("Gemini")
    assert gemini_cls.element == "Airy"
    assert gemini_cls.speech_type == "Voice/Musical"
    assert gemini_cls.is_human is True
    assert gemini_cls.is_dual is True
    assert gemini_cls.is_bicorporal is True


# ---------------------------------------------------------------------------
# 2. Sign Significations Tests (Chapter 16)
# ---------------------------------------------------------------------------

def test_all_12_signs_present_and_complete():
    """Verify all 12 signs have comprehensive significations."""
    expected_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    for s_name in expected_signs:
        assert s_name in SIGN_SIGNIFICATIONS
        sig = SIGN_SIGNIFICATIONS[s_name]
        assert sig.sign_name == s_name
        assert sig.sanskrit_name
        assert sig.ruling_planet
        assert len(sig.constellations_included) >= 3
        assert sig.physical_appearance
        assert sig.mental_tendencies
        assert sig.characteristics
        assert len(sig.health_and_diseases) > 0
        assert len(sig.body_parts) > 0
        assert sig.finance_and_fortune
        assert sig.romance_and_marriage
        assert len(sig.ideal_partner_signs) > 0
        assert len(sig.professions) > 0
        assert len(sig.places) > 0
        assert sig.direction in {"East", "South", "West", "North"}
        assert len(sig.products) > 0
        assert len(sig.countries_and_cities) > 0
        assert sig.handwriting
        assert len(sig.lucky_days) > 0
        assert len(sig.lucky_numbers) > 0
        assert len(sig.lucky_stones) > 0


# ---------------------------------------------------------------------------
# 3. House Significations Tests (Chapter 17)
# ---------------------------------------------------------------------------

def test_all_12_houses_significations():
    """Verify Bhavas 1 through 12 have complete KP Reader 2 significations."""
    assert len(HOUSE_SIGNIFICATIONS_KP) == 12
    for h in range(1, 13):
        h_data = HOUSE_SIGNIFICATIONS_KP[h]
        assert h_data.house == h
        assert h_data.sanskrit_name
        assert len(h_data.primary_matters) > 0
        assert len(h_data.anatomical_parts) > 0
        assert len(h_data.relatives_signified) > 0
        assert len(h_data.karakas) > 0
        assert h_data.detailed_signification


# ---------------------------------------------------------------------------
# 4. Planetary Significations Tests (Chapter 18)
# ---------------------------------------------------------------------------

def test_all_planets_significations():
    """Verify 9 Vedic planets + Uranus + Neptune + Fortuna significations."""
    expected_planets = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
        "Rahu", "Ketu", "Uranus", "Neptune", "Fortuna",
    ]
    for p in expected_planets:
        assert p in PLANET_SIGNIFICATIONS_KP
        p_data = PLANET_SIGNIFICATIONS_KP[p]
        assert p_data.planet == p
        assert p_data.sanskrit_name
        assert p_data.nature
        assert len(p_data.governs_body_parts) > 0
        assert len(p_data.mental_qualities) > 0
        assert len(p_data.professions) > 0
        assert len(p_data.lucky_numbers) > 0
        assert p_data.lucky_stone
        assert p_data.kp_special_doctrine


# ---------------------------------------------------------------------------
# 5. KP Astrological Evaluators Tests
# ---------------------------------------------------------------------------

def test_astrologer_proficiency_evaluation():
    """Test astrology aptitude scoring per Reader 2 Chapter 14."""
    # Strong combination: Moon in Cancer, Mercury-Moon harmony, Saturn-Mercury harmony
    high_res = evaluate_astrologer_proficiency(
        mercury_sign="Virgo",
        moon_sign="Cancer",
        mercury_house=10,
        is_moon_mercury_aspect=True,
        is_saturn_mercury_aspect=True,
        is_jupiter_mercury_aspect=True,
        is_uranus_mercury_aspect=True,
    )
    assert high_res.score >= 80
    assert high_res.aptitude_grade == "Excellent"
    assert "Harmonious Moon-Mercury aspect" in high_res.factors_present

    # Minimal combination
    mod_res = evaluate_astrologer_proficiency(
        mercury_sign="Aries",
        moon_sign="Taurus",
        mercury_house=8,
    )
    assert mod_res.score < 50
    assert mod_res.aptitude_grade in {"Moderate", "Unfavorable"}


def test_speech_and_fertility_evaluation():
    """Test speech defect indicators and fertility promise."""
    # Voice sign on 2nd cusp + Fruitful signs on 5 and 11
    res1 = evaluate_speech_and_fertility(
        cusp_2_sign="Libra",
        cusp_5_sign="Cancer",
        cusp_11_sign="Pisces",
    )
    assert res1.speech_condition == "Vocal Gift"
    assert res1.fertility_promise == "Promised"

    # Mute sign on 2nd cusp with afflicted Mercury + Barren signs on 5 and 11
    res2 = evaluate_speech_and_fertility(
        cusp_2_sign="Scorpio",
        cusp_5_sign="Aries",
        cusp_11_sign="Leo",
        mercury_afflicted_by_saturn_mars=True,
    )
    assert res2.speech_condition == "Impediment Risk"
    assert res2.fertility_promise == "Challenging / Barren"


def test_karma_evaluation():
    """Test Karma classification (Dhruda, Dhruda-Adhruda, Adhruda)."""
    # Adhruda Karma
    k_adh = evaluate_karma_category(
        lagna_aspect_from_jupiter_or_9th_lord=True,
        moon_aspect_from_jupiter_or_9th_lord=True,
        dasa_lord_aspect_from_jupiter_or_9th_lord=True,
        jupiter_or_9th_lord_in_lagna_or_moon=True,
    )
    assert k_adh.karma_type == "Adhruda Karma"
    assert k_adh.mitigation_potential == "Immediate / Effortless"

    # Dhruda-Adhruda Karma
    k_d_adh = evaluate_karma_category(
        lagna_aspect_from_jupiter_or_9th_lord=True,
        moon_aspect_from_jupiter_or_9th_lord=False,
        dasa_lord_aspect_from_jupiter_or_9th_lord=False,
    )
    assert k_d_adh.karma_type == "Dhruda-Adhruda Karma"
    assert k_d_adh.mitigation_potential == "High via Shanti / Virtue"

    # Dhruda Karma
    k_dhr = evaluate_karma_category(
        lagna_aspect_from_jupiter_or_9th_lord=False,
        moon_aspect_from_jupiter_or_9th_lord=False,
        dasa_lord_aspect_from_jupiter_or_9th_lord=False,
    )
    assert k_d_adh.karma_type != "Dhruda Karma"
    assert k_dhr.karma_type == "Dhruda Karma"
    assert k_dhr.severity_level == "Inexorable / Rigid"


def test_fortuna_calculation():
    """Test Pars Fortunae day and night calculations."""
    # Day birth: Asc (100) + Moon (50) - Sun (30) = 120 (Leo 0°)
    fort_day = calculate_kp_fortuna(
        ascendant_deg=100.0,
        moon_deg=50.0,
        sun_deg=30.0,
        is_day_birth=True,
    )
    assert fort_day.longitude == 120.0
    assert fort_day.sign == "Leo"
    assert fort_day.formula_used == "Ascendant + Moon - Sun"

    # Night birth: Asc (100) + Sun (30) - Moon (50) = 80 (Gemini 20°)
    fort_night = calculate_kp_fortuna(
        ascendant_deg=100.0,
        moon_deg=50.0,
        sun_deg=30.0,
        is_day_birth=False,
    )
    assert fort_night.longitude == 80.0
    assert fort_night.sign == "Gemini"
    assert fort_night.formula_used == "Ascendant + Sun - Moon"


# ---------------------------------------------------------------------------
# 6. REST API Endpoints Tests
# ---------------------------------------------------------------------------

def test_api_reader2_classifications():
    """Test GET /api/v1/horoscope/kp/reader2/classifications."""
    # All signs
    res = client.get("/api/v1/horoscope/kp/reader2/classifications")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 12
    assert "Aries" in data

    # Single sign
    res_single = client.get("/api/v1/horoscope/kp/reader2/classifications?sign=Cancer")
    assert res_single.status_code == 200
    cancer = res_single.json()
    assert cancer["sign"] == "Cancer"
    assert cancer["fertility"] == "Fruitful"
    assert cancer["element"] == "Watery"

    # Invalid sign
    res_invalid = client.get("/api/v1/horoscope/kp/reader2/classifications?sign=UnknownSign")
    assert res_invalid.status_code == 404


def test_api_reader2_signs():
    """Test GET /api/v1/horoscope/kp/reader2/signs."""
    res = client.get("/api/v1/horoscope/kp/reader2/signs?sign=Taurus")
    assert res.status_code == 200
    taurus = res.json()
    assert taurus["sign_name"] == "Taurus"
    assert taurus["ruling_planet"] == "Venus"
    assert taurus["exaltation_planet"] == "Moon"
    assert "Diamond" in taurus["lucky_stones"]


def test_api_reader2_houses():
    """Test GET /api/v1/horoscope/kp/reader2/houses."""
    res = client.get("/api/v1/horoscope/kp/reader2/houses?house=7")
    assert res.status_code == 200
    h7 = res.json()
    assert h7["house"] == 7
    assert "Venus" in h7["karakas"]
    assert "Spouse (Husband/Wife)" in h7["relatives_signified"]


def test_api_reader2_planets():
    """Test GET /api/v1/horoscope/kp/reader2/planets."""
    res = client.get("/api/v1/horoscope/kp/reader2/planets?planet=Mercury")
    assert res.status_code == 200
    merc = res.json()
    assert merc["planet"] == "Mercury"
    assert "Emerald" in merc["lucky_stone"]
    assert "Astrologers" in merc["professions"]

    # Test Uranus & Fortuna
    res_ur = client.get("/api/v1/horoscope/kp/reader2/planets?planet=Uranus")
    assert res_ur.status_code == 200
    assert res_ur.json()["planet"] == "Uranus"

    res_fort = client.get("/api/v1/horoscope/kp/reader2/planets?planet=Fortuna")
    assert res_fort.status_code == 200
    assert res_fort.json()["planet"] == "Fortuna"


def test_api_reader2_evaluate_astrologer():
    """Test POST /api/v1/horoscope/kp/reader2/evaluate-astrologer."""
    payload = {
        "mercury_sign": "Virgo",
        "moon_sign": "Cancer",
        "mercury_house": 10,
        "is_moon_mercury_aspect": True,
        "is_saturn_mercury_aspect": True,
    }
    res = client.post("/api/v1/horoscope/kp/reader2/evaluate-astrologer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["score"] >= 70
    assert data["aptitude_grade"] in {"Good", "Excellent"}


def test_api_reader2_speech_fertility():
    """Test POST /api/v1/horoscope/kp/reader2/speech-fertility."""
    payload = {
        "cusp_2_sign": "Gemini",
        "cusp_5_sign": "Cancer",
        "cusp_11_sign": "Scorpio",
    }
    res = client.post("/api/v1/horoscope/kp/reader2/speech-fertility", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["speech_condition"] == "Vocal Gift"
    assert data["fertility_promise"] == "Promised"


def test_api_reader2_karma():
    """Test POST /api/v1/horoscope/kp/reader2/karma."""
    payload = {
        "lagna_aspect_from_jupiter_or_9th_lord": True,
        "moon_aspect_from_jupiter_or_9th_lord": True,
        "dasa_lord_aspect_from_jupiter_or_9th_lord": False,
        "jupiter_or_9th_lord_in_lagna_or_moon": False,
    }
    res = client.post("/api/v1/horoscope/kp/reader2/karma", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["karma_type"] == "Dhruda-Adhruda Karma"


def test_api_reader2_fortuna():
    """Test POST /api/v1/horoscope/kp/reader2/fortuna."""
    payload = {
        "ascendant_deg": 125.5,
        "moon_deg": 45.2,
        "sun_deg": 15.0,
        "is_day_birth": True,
    }
    res = client.post("/api/v1/horoscope/kp/reader2/fortuna", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["sign"]
    assert data["sub_lord"]
    assert data["formula_used"] == "Ascendant + Moon - Sun"


def test_natal_kp_chart_includes_reader2_and_fortuna():
    """Test that POST /api/v1/horoscope/kp returns enriched Fortuna & Reader 2 data."""
    birth_payload = {
        "birth_date": "1990-05-15",
        "birth_time": "10:30:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "ayanamsa": 1,
        "house_system": 2,
    }
    res = client.post("/api/v1/horoscope/kp", json=birth_payload)
    assert res.status_code == 200
    data = res.json()
    assert "fortuna" in data and data["fortuna"] is not None
    assert "reader2_insights" in data and data["reader2_insights"] is not None
    assert "ascendant_classification" in data["reader2_insights"]
    assert "speech_condition" in data["reader2_insights"]
    assert "fertility_promise" in data["reader2_insights"]
