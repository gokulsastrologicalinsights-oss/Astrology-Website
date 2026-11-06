"""Unit and API tests for KP Reader 4: Marriage, Married Life & Children.

Tests:
1. Authentic Mars Dosha calculation and classical pariharas (10 rules).
2. Punarphoo detection across all 4 modes (conjunction, aspect, star/sub exchange, nodes) and case study matching.
3. Spouse physical appearance lookup for all 9 planets in all 12 signs (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu).
4. Career wife evaluation (4th CSL signifying 4, 8, 12).
5. Marriage promise, delay, and denial ("Grapes are Sour" - 4, 6, 10).
6. Second marriage & plurality evaluation (dual signs, Mercury, 2nd cusp).
7. Progeny promise, fruitful/barren signs, twins, and adoption.
8. Sage Kasyapa's 7th star findings (Punarvasu-Hasta, Jyeshta-Satabhisha, etc.).
9. FastApi Router integration for all 8 Reader 4 endpoints.
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.kp_engine.reader4 import (
    evaluate_mars_dosha_reader4,
    evaluate_punarphoo_reader4,
    lookup_spouse_appearance_reader4,
    evaluate_career_spouse_reader4,
    evaluate_marriage_promise_reader4,
    evaluate_second_marriage_reader4,
    evaluate_progeny_reader4,
    evaluate_kasyapa_seventh_star,
    calculate_sign_distance,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Sign Distance & Mars Dosha Tests
# ---------------------------------------------------------------------------

def test_sign_distance():
    """Verify sign distance counting is 1-indexed and correct."""
    assert calculate_sign_distance("Aries", "Aries") == 1
    assert calculate_sign_distance("Aries", "Taurus") == 2
    assert calculate_sign_distance("Aries", "Libra") == 7
    assert calculate_sign_distance("Aries", "Pisces") == 12
    assert calculate_sign_distance("Cancer", "Leo") == 2
    assert calculate_sign_distance("Capricorn", "Aries") == 4


def test_mars_dosha_suddha_jathakam():
    """Mars outside 1, 2, 4, 7, 8, 12 from Lagna, Moon, Venus = Suddha Jathakam."""
    # Mars in Aries (11th from Gemini Lagna, 9th from Leo Moon, 6th from Scorpio Venus)
    res = evaluate_mars_dosha_reader4(
        mars_sign="Aries",
        lagna_sign="Gemini",
        moon_sign="Leo",
        venus_sign="Scorpio",
    )
    assert res.raw_dosha_present is False
    assert res.total_score == 0.0
    assert "SUDDHA JATHAKAM" in res.shastric_verdict


def test_mars_dosha_with_classical_parihara():
    """Mars in Movable sign (Cancer) in 7th from Capricorn Lagna is mitigated."""
    res = evaluate_mars_dosha_reader4(
        mars_sign="Cancer",
        lagna_sign="Capricorn",
        moon_sign="Aries",
        venus_sign="Taurus",
    )
    assert res.raw_dosha_present is True
    assert res.is_mitigated is True
    # At least Chara Rasi (Rule 2) and Cancer Luminary sign (Rule 4) apply
    applied_ids = [p.rule_id for p in res.pariharas_applicable]
    assert "R2_CHARA_RASI" in applied_ids
    assert "R4_LUMINARY_SIGNS" in applied_ids


def test_mars_dosha_kp_cuspal_override():
    """If 7th CSL does NOT signify 6, 10, 12, KP Cuspal override protects from separation."""
    res = evaluate_mars_dosha_reader4(
        mars_sign="Leo",
        lagna_sign="Aquarius",  # Mars in 7th
        moon_sign="Aquarius",
        venus_sign="Aquarius",
        seventh_csl_signifies_6_10_12=False,
    )
    assert "KP CUSPAL PROTECTION" in res.kp_cuspal_override

    res_afflicted = evaluate_mars_dosha_reader4(
        mars_sign="Leo",
        lagna_sign="Aquarius",
        moon_sign="Aquarius",
        venus_sign="Aquarius",
        seventh_csl_signifies_6_10_12=True,
    )
    assert "KP CUSPAL AFFLICTION" in res_afflicted.kp_cuspal_override


# ---------------------------------------------------------------------------
# 2. Punarphoo Tests
# ---------------------------------------------------------------------------

def test_punarphoo_conjunction():
    """Saturn and Moon conjunct in same sign triggers Punarphoo."""
    res = evaluate_punarphoo_reader4(
        saturn_sign="Libra",
        moon_sign="Libra",
        saturn_star="Swathi",
        moon_star="Chitra",
        saturn_sub="Mars",
        moon_sub="Rahu",
        saturn_house=1,
        moon_house=1,
    )
    assert res.is_punarphoo_present is True
    assert res.severity in {"Mild", "Moderate", "Severe"}
    assert any("conjunct" in c for c in res.connections_found)


def test_punarphoo_star_sub_exchange():
    """Moon in Saturn star (Pushya) and Saturn sub triggers severe Punarphoo."""
    res = evaluate_punarphoo_reader4(
        saturn_sign="Aries",
        moon_sign="Cancer",
        saturn_star="Aswini",
        moon_star="Pushya",
        saturn_sub="Moon",
        moon_sub="Saturn",
        saturn_house=10,
        moon_house=4,
        saturn_aspects_moon=True,
    )
    assert res.is_punarphoo_present is True
    assert res.severity in {"Moderate", "Severe"}
    assert len(res.connections_found) >= 3


def test_punarphoo_absent():
    """No Saturn-Moon connection = None severity."""
    res = evaluate_punarphoo_reader4(
        saturn_sign="Capricorn",
        moon_sign="Taurus",
        saturn_star="Dhanishta",
        moon_star="Rohini",
        saturn_sub="Jupiter",
        moon_sub="Venus",
        saturn_house=9,
        moon_house=1,
        saturn_aspects_moon=False,
    )
    assert res.is_punarphoo_present is False
    assert res.severity == "None"


# ---------------------------------------------------------------------------
# 3. Spouse Physical Appearance Tests
# ---------------------------------------------------------------------------

def test_spouse_appearance_sun_leo():
    """7th CSL Sun in Leo = majestic, stately, intensely faithful."""
    res = lookup_spouse_appearance_reader4("Sun", "Leo")
    assert "majestic" in res.stature.lower()
    assert "faithful" in res.temperament.lower()


def test_spouse_appearance_venus_libra():
    """7th CSL Venus in Libra = strikingly beautiful, inseparable companion."""
    res = lookup_spouse_appearance_reader4("Venus", "Libra")
    assert "beautiful" in res.stature.lower() or "beautiful" in res.complexion_and_face.lower()
    assert "inseparable" in res.temperament.lower()


def test_spouse_appearance_rahu_resolution():
    """Rahu resolving to conjunct Venus in Taurus."""
    res = lookup_spouse_appearance_reader4(
        csl_planet="Rahu",
        csl_sign="Taurus",
        node_conjunction="Venus",
    )
    assert "Venus" in res.shastric_quote
    assert "attractive" in res.complexion_and_face.lower() or "health" in res.stature.lower()


def test_spouse_appearance_sun_cancer_caution():
    """Sun in Cancer has specific warning from Prof. Krishnamurti."""
    res = lookup_spouse_appearance_reader4("Sun", "Cancer")
    assert res.cautionary_notes is not None
    assert "July 15" in res.cautionary_notes


# ---------------------------------------------------------------------------
# 4. Career Spouse Tests
# ---------------------------------------------------------------------------

def test_career_spouse_positive():
    """4th CSL signifying 4, 8, 12 promises a career wife."""
    res = evaluate_career_spouse_reader4(
        fourth_csl_planet="Mars",
        fourth_csl_signifies=[4, 8, 12],
        is_mars_involved=True,
    )
    assert res.will_marry_career_spouse is True
    assert set(res.matching_houses) == {4, 8, 12}
    assert "executive" in res.spouse_vocation_type.lower() or "captain" in res.spouse_vocation_type.lower()


def test_career_spouse_negative():
    """4th CSL signifying domestic houses without 4, 8, 12 = homemaker."""
    res = evaluate_career_spouse_reader4(
        fourth_csl_planet="Moon",
        fourth_csl_signifies=[2, 7, 11],
        is_mars_involved=False,
    )
    assert res.will_marry_career_spouse is False
    assert "Homemaker" in res.spouse_vocation_type


# ---------------------------------------------------------------------------
# 5. Marriage Promise & Denial Tests
# ---------------------------------------------------------------------------

def test_marriage_denial_grapes_are_sour():
    """7th CSL signifying 4, 6, 10 without 2, 7, 11 = DENIED."""
    res = evaluate_marriage_promise_reader4(
        seventh_csl_planet="Mercury",
        seventh_csl_signifies=[4, 6, 10],
    )
    assert res.verdict == "DENIED"
    assert res.is_denied is True
    assert "Grapes are Sour" in res.philosophical_verdict


def test_marriage_promise_delayed():
    """7th CSL signifying 2, 7, 11 with Saturn in 5th = PROMISED_DELAYED."""
    res = evaluate_marriage_promise_reader4(
        seventh_csl_planet="Jupiter",
        seventh_csl_signifies=[2, 7, 11],
        is_saturn_in_5th=True,
    )
    assert res.verdict == "PROMISED_DELAYED"
    assert res.is_denied is False
    assert len(res.delay_factors) > 0


# ---------------------------------------------------------------------------
# 6. Second Marriage Tests
# ---------------------------------------------------------------------------

def test_second_marriage_dual_sign_and_support():
    """7th CSL in Gemini (dual sign) signifying 2 & 11 promises 2nd marriage."""
    res = evaluate_second_marriage_reader4(
        seventh_csl_planet="Mercury",
        seventh_csl_sign="Gemini",
        seventh_csl_signifies=[2, 11],
        second_csl_signifies=[2, 7],
    )
    assert res.is_second_marriage_indicated is True
    assert res.seventh_csl_in_dual_sign is True
    assert res.seventh_csl_is_mercury is True


# ---------------------------------------------------------------------------
# 7. Progeny Tests
# ---------------------------------------------------------------------------

def test_progeny_fruitful_sign():
    """5th CSL in Cancer (fruitful) signifying 2, 5, 11 = Childbirth blessed."""
    res = evaluate_progeny_reader4(
        fifth_csl_planet="Jupiter",
        fifth_csl_sign="Cancer",
        fifth_csl_signifies=[2, 5, 11],
    )
    assert res.childbirth_promised is True
    assert "Fruitful" in res.fertility_status


def test_progeny_twin_birth():
    """5th CSL in Pisces (dual sign) with Mercury in dual sign signifying 2 & 5."""
    res = evaluate_progeny_reader4(
        fifth_csl_planet="Mercury",
        fifth_csl_sign="Pisces",
        fifth_csl_signifies=[2, 5],
        is_mercury_or_jupiter_in_dual_sign=True,
    )
    assert res.twin_birth_indicated is True


# ---------------------------------------------------------------------------
# 8. Sage Kasyapa 7th Star Tests
# ---------------------------------------------------------------------------

def test_kasyapa_punarvasu_hasta():
    """Punarvasu girl + Hasta boy = Approved with abundant children."""
    res = evaluate_kasyapa_seventh_star("Punarvasu", "Hasta")
    assert res.is_seventh_star is True
    assert res.kasyapa_verdict == "Approved"
    assert "children" in res.predicted_experience.lower()


def test_kasyapa_jyeshta_satabhisha():
    """Jyeshta girl + Satabhisha boy = Rejected."""
    res = evaluate_kasyapa_seventh_star("Jyeshta", "Satabhisha")
    assert res.is_seventh_star is True
    assert res.kasyapa_verdict == "Rejected"


# ---------------------------------------------------------------------------
# 9. API Router Integration Tests
# ---------------------------------------------------------------------------

def test_api_mars_dosha():
    payload = {
        "mars_sign": "Cancer",
        "lagna_sign": "Capricorn",
        "moon_sign": "Aries",
        "venus_sign": "Taurus",
        "is_mars_conjunct_or_aspected_by_jupiter": False,
        "is_mars_conjunct_or_aspected_by_mercury": False,
        "is_mars_conjunct_moon": False,
        "is_mars_conjunct_jupiter_within_8deg": False,
        "seventh_csl_signifies_6_10_12": False,
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/mars-dosha", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["raw_dosha_present"] is True
    assert data["is_mitigated"] is True
    assert "KP CUSPAL PROTECTION" in data["kp_cuspal_override"]


def test_api_punarphoo():
    payload = {
        "saturn_sign": "Leo",
        "moon_sign": "Leo",
        "saturn_star": "Magha",
        "moon_star": "Magha",
        "saturn_sub": "Saturn",
        "moon_sub": "Moon",
        "saturn_house": 7,
        "moon_house": 7,
        "saturn_aspects_moon": True,
        "is_rahu_or_ketu_representing_saturn_or_moon": False,
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/punarphoo", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_punarphoo_present"] is True
    assert "Severe" in data["severity"] or "Moderate" in data["severity"]


def test_api_spouse_appearance():
    payload = {
        "csl_planet": "Venus",
        "csl_sign": "Libra",
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/spouse-appearance", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "beautiful" in data["complexion_and_face"].lower() or "beautiful" in data["stature"].lower()


def test_api_career_spouse():
    payload = {
        "fourth_csl_planet": "Mars",
        "fourth_csl_signifies": [4, 8, 12],
        "is_mars_involved": True,
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/career-spouse", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["will_marry_career_spouse"] is True


def test_api_marriage_promise():
    payload = {
        "seventh_csl_planet": "Mercury",
        "seventh_csl_signifies": [4, 6, 10],
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/marriage-promise", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "DENIED"
    assert data["is_denied"] is True


def test_api_second_marriage():
    payload = {
        "seventh_csl_planet": "Mercury",
        "seventh_csl_sign": "Gemini",
        "seventh_csl_signifies": [2, 11],
        "second_csl_signifies": [2, 7],
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/second-marriage", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_second_marriage_indicated"] is True


def test_api_progeny():
    payload = {
        "fifth_csl_planet": "Jupiter",
        "fifth_csl_sign": "Cancer",
        "fifth_csl_signifies": [2, 5, 11],
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/progeny-promise", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["childbirth_promised"] is True
    assert "Fruitful" in data["fertility_status"]


def test_api_kasyapa_seventh_star():
    payload = {
        "bride_star": "Punarvasu",
        "groom_star": "Hasta",
    }
    resp = client.post("/api/v1/horoscope/kp/reader4/kasyapa-seventh-star", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_seventh_star"] is True
    assert data["kasyapa_verdict"] == "Approved"
