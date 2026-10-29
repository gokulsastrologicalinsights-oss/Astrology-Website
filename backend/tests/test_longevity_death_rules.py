import pytest
from app.services.prediction_rules.rules_registry import INITIAL_RULES_CATALOGUE
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from app.services.ephemeris import calculate_full_horoscope
from app.services.kp_service import calculate_kp_chart
from app.schemas.common import BirthInput


def test_longevity_death_rules_evaluation():
    b = BirthInput(
        birth_date="1990-05-15",
        birth_time="10:30",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )

    horo = calculate_full_horoscope(b.birth_date, b.birth_time, b.timezone, b.latitude, b.longitude)
    kp = calculate_kp_chart(b)
    ctx = ChartContext(horoscope=horo, kp_data=kp.model_dump())

    longevity_rules = [
        r for r in INITIAL_RULES_CATALOGUE
        if ("LONG" in r.rule_id or "DEATH" in r.rule_id or "SURG" in r.rule_id or "SUIC" in r.rule_id)
    ]
    assert len(longevity_rules) >= 13

    matched = []
    for r in longevity_rules:
        res = AstrologicalRuleEvaluator.evaluate_rule(r, ctx)
        assert not res.unevaluable, f"Rule {r.rule_id} was marked unevaluable: {res.unevaluable_reason}"
        assert not any("Unsupported condition type" in reas for reas in res.reasons), f"Rule {r.rule_id} failed with unsupported type: {res.reasons}"
        if res.matched:
            matched.append(r.rule_id)

    # In this chart, Deergha Ayu, Surgical indicator, and accident hazard rules should evaluate properly
    assert len(matched) > 0, "At least some longevity/health rules should match in this chart"
    assert "RULE-KP-LONG-01" in matched or "RULE-KP-DEATH-03" in matched
