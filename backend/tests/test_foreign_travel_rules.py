"""Tests for Classical Foreign Travel and Foreign Settlement Rules Catalogue."""

import pytest
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import (
    AstrologicalRuleEvaluator,
    ChartContext,
)
from tests.test_prediction_rules_engine import make_sample_horoscope


def test_foreign_travel_catalogue_completeness():
    """Verify all Foreign Travel & Settlement rules from Debraj / classical synthesis are registered."""
    all_rules = RulesRegistry.get_all_rules()
    trv_rules = [r for r in all_rules if r.rule_id.startswith("RULE-TRV-")]

    # We have RULE-TRV-01 plus 19 new rules (02 to 20) = 20 total
    assert len(trv_rules) >= 20, f"Expected at least 20 travel rules, got {len(trv_rules)}"

    # Check rule IDs from 01 to 20
    expected_ids = [f"RULE-TRV-{i:02d}" for i in range(1, 21)]
    actual_ids = {r.rule_id for r in trv_rules}

    for eid in expected_ids:
        assert eid in actual_ids, f"Missing expected rule ID: {eid}"

    # Verify each rule has English and Tamil fields
    for r in trv_rules:
        assert r.name_en and len(r.name_en) > 5
        assert r.name_ta and len(r.name_ta) > 5
        assert r.interpretation_en and len(r.interpretation_en) > 10
        assert r.interpretation_ta and len(r.interpretation_ta) > 10
        assert r.astrological_principle_en and len(r.astrological_principle_en) > 10
        assert r.astrological_principle_ta and len(r.astrological_principle_ta) > 10
        assert r.source_reference and len(r.source_reference) > 5
        assert r.limitations_en is not None
        assert r.limitations_ta is not None
        assert r.category_slug in ("education_travel", "career_business")
        assert r.condition_tree is not None


def test_evaluate_rahu_in_12th_house():
    """Verify evaluation of RULE-TRV-03 (Rahu in 12th House)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-03")
    assert rule is not None

    # Aries Lagna (Sign 1). 12th house is Pisces (Sign 12).
    # Place Rahu in Pisces.
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Rahu": (12, 10.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0


def test_evaluate_4th_lord_in_12th_house():
    """Verify evaluation of RULE-TRV-02 (4th Lord in 12th House)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-02")
    assert rule is not None

    # Aries Lagna (Sign 1). 4th house is Cancer (Sign 4), ruled by Moon.
    # 12th house is Pisces (Sign 12).
    # Place Moon (4th lord) in Pisces (12th house).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Moon": (12, 15.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0


def test_evaluate_moon_rahu_conjunction_ocean_voyage():
    """Verify evaluation of RULE-TRV-05 (Moon conjunct Rahu in Watery Sign)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-05")
    assert rule is not None

    # Cancer (Sign 4 = Watery sign) with Moon & Rahu conjunct
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Moon": (4, 12.0),
            "Rahu": (4, 14.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0


def test_evaluate_foreign_employment_11th_lord_in_6th():
    """Verify evaluation of RULE-TRV-13 (11th Lord in 6th House)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-13")
    assert rule is not None

    # Aries Lagna (Sign 1). 11th house is Aquarius (Sign 11), ruled by Saturn.
    # 6th house is Virgo (Sign 6).
    # Place Saturn (11th lord) in Virgo (6th house).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Saturn": (6, 18.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0


def test_evaluate_sun_in_5th_diplomacy():
    """Verify evaluation of RULE-TRV-08 (Sun in 5th House)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-08")
    assert rule is not None

    # Aries Lagna (Sign 1). 5th house is Leo (Sign 5).
    # Place Sun in Leo (House 5).
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Sun": (5, 22.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0


def test_evaluate_chara_lagna_mobility():
    """Verify evaluation of RULE-TRV-19 (Lagna in Movable Sign)."""
    rule = RulesRegistry.get_rule_by_id("RULE-TRV-19")
    assert rule is not None

    # Aries Lagna (Sign 1 = Chara)
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Sun": (1, 10.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert result.matched is True
    assert len(result.evidence) > 0
