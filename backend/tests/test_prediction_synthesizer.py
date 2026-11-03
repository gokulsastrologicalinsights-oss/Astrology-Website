"""Tests for Astrological Prediction Synthesizer and Dignity Detection."""

import pytest
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from app.services.prediction_rules.synthesizer import PredictionSynthesizer
from app.schemas.prediction_rules import EvaluatedRuleItem
from tests.test_prediction_rules_engine import make_sample_horoscope


def make_gokul_chart():
    """Builds test horoscope matching Gokul's chart:

    - Lagna: Sagittarius (Dhanus, sign 9)
    - 7th House: Gemini (Mithuna, sign 3)
    - Saturn: Aries (Mesha, sign 1) -> 5th house, casting 3rd special aspect on 7th house (Gemini)
    - Jupiter: Aquarius (Kumbha, sign 11) -> 3rd house, casting 5th special aspect on 7th house (Gemini)
    """
    return make_sample_horoscope(
        lagna_sign=9,
        planets_spec={
            "Saturn": (1, 15.0),   # In Aries (sign 1) -> Debilitated
            "Jupiter": (11, 12.0), # In Aquarius (sign 11) -> 5th aspect to Gemini
            "Mars": (1, 10.0),
            "Sun": (9, 5.0),
            "Moon": (4, 20.0),
            "Mercury": (10, 8.0),
            "Venus": (11, 18.0),
            "Rahu": (5, 15.0),
            "Ketu": (11, 15.0),
        }
    )


def test_evaluator_dignity_detection_for_saturn_aspect():
    """Verify evaluator detects Saturn's debilitation in aspect evidence."""
    chart = make_gokul_chart()
    ctx = ChartContext(horoscope=chart)

    rule12 = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-12")
    assert rule12 is not None
    res12 = AstrologicalRuleEvaluator.evaluate_rule(rule12, ctx)
    assert res12.matched is True
    # Saturn in Aries is debilitated
    assert any("Debilitated/நீசம்" in ev for ev in res12.evidence)


def test_synthesizer_generates_unified_reading_for_saturn_and_jupiter():
    """Verify that when both Saturn delay and Jupiter blessing match,

    PredictionSynthesizer produces a unified verdict card.
    """
    chart = make_gokul_chart()
    ctx = ChartContext(horoscope=chart)

    rule12 = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-12")
    rule14 = RulesRegistry.get_rule_by_id("RULE-MARR-TIME-14")

    res12 = AstrologicalRuleEvaluator.evaluate_rule(rule12, ctx)
    res14 = AstrologicalRuleEvaluator.evaluate_rule(rule14, ctx)

    evaluated_items = [
        EvaluatedRuleItem(**res12.to_dict(language="ta")),
        EvaluatedRuleItem(**res14.to_dict(language="ta")),
    ]

    syntheses = PredictionSynthesizer.synthesize_evaluated_rules(evaluated_items, ctx, language="ta")
    assert len(syntheses) >= 1

    synth = syntheses[0]
    assert synth.synthesis_id == "SYNTH-MARR-SATURN-JUPITER-7H"
    assert "RULE-MARR-TIME-12" in synth.interacting_rule_ids
    assert "RULE-MARR-TIME-14" in synth.interacting_rule_ids
    assert "Saturn" in synth.participating_planets
    assert "Jupiter" in synth.participating_planets
    assert "நீச" in synth.summary_ta
    assert "குரு" in synth.summary_ta
