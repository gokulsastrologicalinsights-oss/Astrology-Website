"""Tests for Jataka Tatva 33 Adultery Yogas & Brihat Jataka Stri Rules Catalogue."""

import pytest
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import (
    AstrologicalRuleEvaluator,
    ChartContext,
)
from tests.test_prediction_rules_engine import make_sample_horoscope


def test_jataka_tatva_catalogue_completeness():
    """Verify all 33 Jataka Tatva Adultery Yogas are registered."""
    all_rules = RulesRegistry.get_all_rules()
    jt_rules = [r for r in all_rules if r.rule_id.startswith("RULE-JT-ADULT-")]

    assert len(jt_rules) == 33, f"Expected 33 Jataka Tatva rules, got {len(jt_rules)}"

    # Check rule IDs from 01 to 33
    expected_ids = [f"RULE-JT-ADULT-{i:02d}" for i in range(1, 34)]
    actual_ids = {r.rule_id for r in jt_rules}

    for eid in expected_ids:
        assert eid in actual_ids, f"Missing expected rule ID: {eid}"

    # Verify each rule has English and Tamil fields
    for r in jt_rules:
        assert r.name_en and len(r.name_en) > 5
        assert r.name_ta and len(r.name_ta) > 5
        assert r.interpretation_en and len(r.interpretation_en) > 10
        assert r.interpretation_ta and len(r.interpretation_ta) > 10
        assert r.astrological_principle_en and len(r.astrological_principle_en) > 10
        assert r.astrological_principle_ta and len(r.astrological_principle_ta) > 10
        assert r.source_reference and "Jataka Tatva" in r.source_reference
        assert r.limitations_en is not None
        assert r.limitations_ta is not None
        assert r.category_slug == "sexuality_intimacy"
        assert r.condition_tree is not None


def test_brihat_jataka_stri_rules_completeness():
    """Verify all Brihat Jataka Stri Jataka rules are registered."""
    all_rules = RulesRegistry.get_all_rules()
    bj_rules = [r for r in all_rules if r.rule_id.startswith("RULE-BJ-STRI-")]

    assert len(bj_rules) >= 5, f"Expected at least 5 Brihat Jataka rules, got {len(bj_rules)}"

    for r in bj_rules:
        assert r.name_en and len(r.name_en) > 5
        assert r.name_ta and len(r.name_ta) > 5
        assert r.interpretation_en and len(r.interpretation_en) > 10
        assert r.interpretation_ta and len(r.interpretation_ta) > 10
        assert r.source_reference and "Brihat Jataka" in r.source_reference
        assert r.limitations_en is not None
        assert r.limitations_ta is not None
        assert r.category_slug == "sexuality_intimacy"


def test_evaluate_jt_yoga_01_synthetic_match():
    """Verify evaluation of Jataka Tatva Yoga 1 (Venus & Mercury in 7th/8th/10th)."""
    r1 = RulesRegistry.get_rule_by_id("RULE-JT-ADULT-01")
    assert r1 is not None

    # Aries Lagna (1), Venus and Mercury placed in 10th house (Capricorn = Sign 10)
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Venus": (10, 15.0),
            "Mercury": (10, 20.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    eval_result = AstrologicalRuleEvaluator.evaluate_rule(r1, ctx)
    assert eval_result.matched is True
    assert len(eval_result.evidence) > 0


def test_evaluate_bj_stri_04_navamsa_parivartana():
    """Verify Navamsa Venus-Mars Parivartana (Brihat Jataka Stri 4)."""
    r4 = RulesRegistry.get_rule_by_id("RULE-BJ-STRI-04")
    assert r4 is not None

    # Venus in Aries (Sign 1, deg 2.0 -> Aries Navamsa)
    # Mars in Aries (Sign 1, deg 5.0 -> Taurus Navamsa)
    horoscope = make_sample_horoscope(
        lagna_sign=1,
        planets_spec={
            "Venus": (1, 2.0),
            "Mars": (1, 5.0),
        }
    )
    ctx = ChartContext(horoscope=horoscope)

    eval_result = AstrologicalRuleEvaluator.evaluate_rule(r4, ctx)
    assert eval_result.matched is True
    assert len(eval_result.evidence) > 0
