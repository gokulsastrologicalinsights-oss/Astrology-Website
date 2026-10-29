"""Unit tests for Marriage Timing, Navamsa & Jaimini Rules."""

import pytest
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from tests.test_prediction_rules_engine import make_sample_horoscope


def test_marriage_timing_rules_registered():
    """Verify all 15 marriage timing rules are correctly loaded in RulesRegistry."""
    all_rules = RulesRegistry.get_all_rules()
    timing_rules = [r for r in all_rules if r.rule_id.startswith("RULE-MARR-TIME-")]
    assert len(timing_rules) == 15, f"Expected 15 timing rules, found {len(timing_rules)}"

    rule_ids = {r.rule_id for r in timing_rules}
    for i in range(1, 16):
        expected_id = f"RULE-MARR-TIME-{i:02d}"
        assert expected_id in rule_ids, f"Missing rule ID: {expected_id}"


def test_evaluate_7th_lord_timing_rule():
    """Test RULE-MARR-TIME-01 with a chart where 7th lord is placed in 1st house (Kendra)."""
    # Aries Lagna (1): 7th house is Libra (7), 7th lord is Venus. Place Venus in 1st house (Aries - 1).
    chart = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Venus": (1, 15.0), # 7th lord in 1st house
            "Jupiter": (4, 10.0),
            "Sun": (1, 10.0),
            "Moon": (2, 10.0),
            "Mars": (10, 10.0),
            "Mercury": (3, 10.0),
            "Saturn": (11, 10.0),
            "Rahu": (2, 20.0),
            "Ketu": (8, 20.0),
        }
    )

    ctx = ChartContext(horoscope=chart)
    rule = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-01")
    assert rule is not None

    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert len(res.evidence) > 0


def test_evaluate_guru_drishti_on_7th():
    """Test RULE-MARR-TIME-14 where Jupiter aspects 7th house."""
    # Aries Lagna (1): 7th house is Libra (7).
    # Jupiter in Gemini (sign 3, 3rd house) aspects 7th house via 5th drishti (sign 3 + 4 = sign 7).
    chart = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Jupiter": (3, 15.0), # Aspects sign 7 (7th house) with 5th aspect!
            "Venus": (2, 10.0),
            "Sun": (1, 10.0),
            "Moon": (2, 10.0),
            "Mars": (10, 10.0),
            "Mercury": (3, 10.0),
            "Saturn": (11, 10.0),
            "Rahu": (2, 20.0),
            "Ketu": (8, 20.0),
        }
    )

    ctx = ChartContext(horoscope=chart)
    rule = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-14")
    assert rule is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert len(res.evidence) > 0


def test_evaluate_delayed_marriage_saturn_in_7th():
    """Test RULE-MARR-TIME-12 where Saturn in 7th triggers delayed marriage evaluation."""
    # Aries Lagna: Saturn in Libra (sign 7) in 7th house.
    chart = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Saturn": (7, 15.0), # In 7th house
            "Jupiter": (4, 15.0),
            "Venus": (2, 10.0),
            "Sun": (1, 10.0),
            "Moon": (2, 10.0),
            "Mars": (10, 10.0),
            "Mercury": (3, 10.0),
            "Rahu": (2, 20.0),
            "Ketu": (8, 20.0),
        }
    )

    ctx = ChartContext(horoscope=chart)
    rule = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-12")
    assert rule is not None
    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert len(res.evidence) > 0
