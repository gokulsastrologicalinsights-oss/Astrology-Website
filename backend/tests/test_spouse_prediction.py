"""Unit tests for Life Partner & Spouse Nature, Character & Type Prediction."""

import pytest
from datetime import date, time
from app.schemas.common import BirthInput
from app.schemas.spouse_prediction import SpousePredictionRequest, SpousePredictionResponse
from app.services.spouse_prediction_engine import SpousePredictionService


def test_spouse_prediction_basic():
    """Test standard horoscope spouse prediction for male native."""
    birth = BirthInput(
        birth_date=date(1995, 10, 24),
        birth_time=time(14, 30, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    req = SpousePredictionRequest(birth=birth, gender="male")
    res: SpousePredictionResponse = SpousePredictionService.predict_spouse(req)

    assert res.ascendant_sign
    assert res.ascendant_sign_tamil
    assert res.seventh_sign.sign
    assert res.seventh_sign.ruler
    assert res.seventh_lord.element in ("Fire", "Earth", "Air", "Water")
    assert res.karakas.venus_sign
    assert res.karakas.jupiter_sign
    assert res.karakas.mars_sign
    assert res.navamsa_d9.d9_seventh_sign
    assert res.desire_vs_reality.reality_description_en
    assert res.desire_vs_reality.desire_description_en
    assert 0 <= res.trait_scores.romantic_loving_score <= 100
    assert 0 <= res.trait_scores.loyalty_faithfulness_score <= 100
    assert 0 <= res.trait_scores.intelligence_education_score <= 100
    assert 0 <= res.trait_scores.physical_charm_score <= 100
    assert res.remedies.primary_gemstone_en
    assert res.summary_headline_en
    assert res.summary_headline_ta


def test_spouse_prediction_female_native():
    """Test spouse prediction for female native with Jupiter & Mars significators."""
    birth = BirthInput(
        birth_date=date(1998, 5, 15),
        birth_time=time(9, 15, 0),
        timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
    )
    req = SpousePredictionRequest(birth=birth, gender="female")
    res = SpousePredictionService.predict_spouse(req)

    assert res.native_gender == "female"
    assert "husband" in res.karakas.gender_specific_insight_en.lower()
    assert res.navamsa_d9.d9_seventh_lord
