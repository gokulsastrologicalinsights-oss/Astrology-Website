"""Tests for Classical Planetary Debilitation & Aspect Loss Rules Registry (319).

Validates:
1. Adhirshta Jothida Kalanjiyam 9 Planetary Debilitation rules (Sun in Libra, Moon in Scorpio,
   Mars in Cancer, Mercury in Pisces, Jupiter in Capricorn, Venus in Virgo, Saturn in Aries,
   Rahu in Sagittarius/Scorpio, Ketu in Gemini/Taurus) along with their Tamil interpretations and remedies.
2. The 3 conditions of Total Planetary Aspect Loss:
   a. Planetary Avasthas (Bala 0°-6° infant and Mrita 24°-30° senile degree states).
   b. Combustion (Mars, Jupiter, Venus, Saturn near Sun) and exemptions (Moon Amavasya, Mercury Budhaditya, Rahu/Ketu).
   c. Graha Yuddha (Planetary war within 1° orb; defeated planet loses aspect power).
"""

import pytest
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from app.schemas.horoscope import (
    HoroscopeResponse,
    AscendantInfo,
    PlanetInfo,
    HouseInfo,
    NakshatraDetail,
    CalculationMetadata,
)


def _build_test_horoscope(planets_config, lagna_sign=1, lagna_deg=15.0) -> HoroscopeResponse:
    """Build mock HoroscopeResponse with specified planetary positions."""
    sign_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_names_ta = [
        "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
        "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
    ]

    nakshatra_sample = NakshatraDetail(
        index=1,
        name="Ashwini",
        pada=1,
        lord="Ketu",
        deity="Ashvins",
    )

    planet_objs = []
    for p_name, (s_idx, deg_in_sign, is_retro) in planets_config.items():
        total_long = (s_idx - 1) * 30.0 + deg_in_sign
        planet_objs.append(
            PlanetInfo(
                name=p_name,
                body_id=1,
                longitude=total_long,
                latitude=0.0,
                distance_au=1.0,
                speed_deg_per_day=1.0,
                is_retrograde=is_retro,
                sign_index=s_idx,
                sign_name=sign_names[s_idx - 1],
                sign_name_tamil=sign_names_ta[s_idx - 1],
                degree_in_sign=deg_in_sign,
                nakshatra=nakshatra_sample,
            )
        )

    houses: list[HouseInfo] = []
    for h in range(1, 13):
        h_sign = ((lagna_sign - 1 + h - 1) % 12) + 1
        houses.append(
            HouseInfo(
                house_number=h,
                cusp_degree=(h_sign - 1) * 30.0,
                sign_index=h_sign,
                sign_name=sign_names[h_sign - 1],
                sign_name_tamil=sign_names_ta[h_sign - 1],
                degree_in_sign=0.0,
                nakshatra="Ashwini",
                pada=1,
                star_lord="Ketu",
            )
        )

    return HoroscopeResponse(
        ascendant=AscendantInfo(
            degree=(lagna_sign - 1) * 30.0 + lagna_deg,
            degree_in_sign=lagna_deg,
            sign_index=lagna_sign,
            sign_name=sign_names[lagna_sign - 1],
            sign_name_tamil=sign_names_ta[lagna_sign - 1],
            nakshatra=nakshatra_sample,
        ),
        midheaven=AscendantInfo(
            degree=270.0,
            sign_index=10,
            sign_name="Capricorn",
            sign_name_tamil="மகரம்",
            degree_in_sign=0.0,
            nakshatra=nakshatra_sample,
        ),
        planets=planet_objs,
        houses=houses,
        aspects=[],
        metadata=CalculationMetadata(
            engine="XALEN Ephemeris",
            birth_utc_iso="1995-04-15T09:30:00Z",
            julian_day_ut1=2449822.8958,
            local_timezone="Asia/Kolkata",
            utc_offset_hours=5.5,
            coordinates={"latitude": 13.0827, "longitude": 80.2707},
            ayanamsa_id=0,
            ayanamsa_name="Lahiri",
            ayanamsa_deg=23.75,
            house_system_id=0,
            house_system_name="WholeSign",
        ),
    )


def test_debilitation_rules_registered_in_registry():
    """Verify all 9 debilitation rules and 6 aspect potency rules are registered."""
    rule_ids = [
        "RULE-NEECHA-SUR-01",
        "RULE-NEECHA-CHA-01",
        "RULE-NEECHA-MAR-01",
        "RULE-NEECHA-MER-01",
        "RULE-NEECHA-JUP-01",
        "RULE-NEECHA-VEN-01",
        "RULE-NEECHA-SAT-01",
        "RULE-NEECHA-RAH-01",
        "RULE-NEECHA-KET-01",
        "RULE-DRISHTI-AVASTHA-BALA",
        "RULE-DRISHTI-AVASTHA-MRITA",
        "RULE-DRISHTI-AVASTHA-ANY-LOSS",
        "RULE-DRISHTI-COMBUSTION-LOSS",
        "RULE-DRISHTI-COMBUSTION-EXEMPT",
        "RULE-DRISHTI-GRAHA-YUDDHA",
    ]
    for r_id in rule_ids:
        rule = RulesRegistry.get_rule_by_id(r_id)
        assert rule is not None, f"Rule {r_id} must be registered in RulesRegistry"
        assert "அதிர்ஷ்ட ஜோதிடக் களஞ்சியம்" in rule.source_reference or "கிரக பார்வை தெளிவு" in rule.source_reference
        assert len(rule.interpretation_ta) > 0


def test_sun_debilitated_in_libra():
    """Verify Sun in Libra triggers RULE-NEECHA-SUR-01."""
    horoscope = _build_test_horoscope({
        "Sun": (7, 10.0, False),  # Libra
        "Moon": (2, 15.0, False),
    })
    ctx = ChartContext(horoscope)
    rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-SUR-01")
    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert "Sun is debilitated (Neecha)" in res.evidence[0]


def test_moon_debilitated_in_scorpio():
    """Verify Moon in Scorpio triggers RULE-NEECHA-CHA-01."""
    horoscope = _build_test_horoscope({
        "Sun": (1, 10.0, False),
        "Moon": (8, 3.0, False),  # Scorpio
    })
    ctx = ChartContext(horoscope)
    rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-CHA-01")
    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True
    assert "Moon is debilitated (Neecha)" in res.evidence[0]


def test_mars_debilitated_in_cancer():
    """Verify Mars in Cancer triggers RULE-NEECHA-MAR-01."""
    horoscope = _build_test_horoscope({
        "Mars": (4, 28.0, False),  # Cancer
        "Sun": (1, 10.0, False),
    })
    ctx = ChartContext(horoscope)
    rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-MAR-01")
    res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
    assert res.matched is True


def test_mercury_and_jupiter_debilitation():
    """Verify Mercury in Pisces (12) and Jupiter in Capricorn (10)."""
    horoscope = _build_test_horoscope({
        "Mercury": (12, 15.0, False),  # Pisces
        "Jupiter": (10, 5.0, False),   # Capricorn
        "Sun": (1, 10.0, False),
    })
    ctx = ChartContext(horoscope)

    mer_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-MER-01")
    res_mer = AstrologicalRuleEvaluator.evaluate_rule(mer_rule, ctx)
    assert res_mer.matched is True

    jup_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-JUP-01")
    res_jup = AstrologicalRuleEvaluator.evaluate_rule(jup_rule, ctx)
    assert res_jup.matched is True


def test_venus_and_saturn_debilitation():
    """Verify Venus in Virgo (6) and Saturn in Aries (1)."""
    horoscope = _build_test_horoscope({
        "Venus": (6, 27.0, False),  # Virgo
        "Saturn": (1, 20.0, False),  # Aries
        "Sun": (2, 10.0, False),
    })
    ctx = ChartContext(horoscope)

    ven_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-VEN-01")
    assert AstrologicalRuleEvaluator.evaluate_rule(ven_rule, ctx).matched is True

    sat_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-SAT-01")
    assert AstrologicalRuleEvaluator.evaluate_rule(sat_rule, ctx).matched is True


def test_rahu_and_ketu_debilitation():
    """Verify Rahu in Sagittarius (9) and Ketu in Gemini (3)."""
    horoscope = _build_test_horoscope({
        "Rahu": (9, 14.0, True),  # Sagittarius
        "Ketu": (3, 14.0, True),  # Gemini
        "Sun": (1, 10.0, False),
    })
    ctx = ChartContext(horoscope)

    rah_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-RAH-01")
    assert AstrologicalRuleEvaluator.evaluate_rule(rah_rule, ctx).matched is True

    ket_rule = RulesRegistry.get_rule_by_id("RULE-NEECHA-KET-01")
    assert AstrologicalRuleEvaluator.evaluate_rule(ket_rule, ctx).matched is True


def test_bala_and_mrita_avastha_aspect_loss():
    """Verify planets in 0°-6° (Bala) and 24°-30° (Mrita) lose aspect potency."""
    horoscope = _build_test_horoscope({
        "Mars": (1, 3.5, False),     # 3.5° in Aries = Bala avastha (0°-6°)
        "Jupiter": (5, 27.2, False),  # 27.2° in Leo = Mrita avastha (24°-30°)
        "Sun": (2, 15.0, False),
    })
    ctx = ChartContext(horoscope)

    bala_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-AVASTHA-BALA")
    res_bala = AstrologicalRuleEvaluator.evaluate_rule(bala_rule, ctx)
    assert res_bala.matched is True
    assert "Mars is at 3.50°" in res_bala.evidence[0]
    assert "பால அவஸ்தை" in res_bala.evidence[0]

    mrita_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-AVASTHA-MRITA")
    res_mrita = AstrologicalRuleEvaluator.evaluate_rule(mrita_rule, ctx)
    assert res_mrita.matched is True
    assert "Jupiter is at 27.20°" in res_mrita.evidence[0]
    assert "மிரித அவஸ்தை" in res_mrita.evidence[0]

    any_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-AVASTHA-ANY-LOSS")
    res_any = AstrologicalRuleEvaluator.evaluate_rule(any_rule, ctx)
    assert res_any.matched is True


def test_combustion_aspect_loss_and_exemption():
    """Verify Mars combust with Sun loses aspect potency, while Mercury is exempt."""
    # Sun at Aries 10°, Mars at Aries 16° (diff 6° <= 17° Mars limit), Mercury at Aries 13° (exempt)
    horoscope = _build_test_horoscope({
        "Sun": (1, 10.0, False),
        "Mars": (1, 16.0, False),     # 6° from Sun -> combust
        "Mercury": (1, 13.0, False),  # exempt
    })
    ctx = ChartContext(horoscope)

    combust_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-COMBUSTION-LOSS")
    res_combust = AstrologicalRuleEvaluator.evaluate_rule(combust_rule, ctx)
    assert res_combust.matched is True
    assert "Mars" in res_combust.evidence[0]
    assert "Astangata" in res_combust.evidence[0]

    exempt_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-COMBUSTION-EXEMPT")
    res_exempt = AstrologicalRuleEvaluator.evaluate_rule(exempt_rule, ctx)
    assert res_exempt.matched is True
    assert "Budhaditya Yoga" in res_exempt.evidence[0]


def test_graha_yuddha_defeat_loses_aspect_potency():
    """Verify Graha Yuddha between Mars and Jupiter within 1°: lower degree loses aspect potency."""
    # Mars at Taurus 15.2°, Jupiter at Taurus 15.8° -> diff 0.6° <= 1.0°
    # Jupiter has higher degree (Victor), Mars has lower degree (Defeated, loses aspect)
    horoscope = _build_test_horoscope({
        "Mars": (2, 15.2, False),     # Defeated
        "Jupiter": (2, 15.8, False),  # Victor
        "Sun": (10, 10.0, False),
    })
    ctx = ChartContext(horoscope)

    war_rule = RulesRegistry.get_rule_by_id("RULE-DRISHTI-GRAHA-YUDDHA")
    res_war = AstrologicalRuleEvaluator.evaluate_rule(war_rule, ctx)
    assert res_war.matched is True
    assert "Defeated=Mars" in res_war.evidence[0]
    assert "Victor=Jupiter" in res_war.evidence[0]
    assert "பார்வை வலுவை முழுதாக இழக்கும்" in res_war.evidence[0]
