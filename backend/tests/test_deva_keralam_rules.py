"""Test suite for Deva Keralam (Chandra Kala Nadi) Volume 3 classical rules codification."""

import pytest
from app.schemas.horoscope import (
    HoroscopeResponse,
    AscendantInfo,
    PlanetInfo,
    HouseInfo,
    NakshatraDetail,
    CalculationMetadata,
)
from app.services.prediction_rules.deva_keralam_rules import DEVA_KERALAM_RULES
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext


def make_test_horoscope(planets_spec: dict, lagna_sign: int = 1) -> HoroscopeResponse:
    """Create a synthetic HoroscopeResponse for testing rules.
    
    planets_spec: {planet_name: (sign_index_1_based, degree_in_sign)}
    """
    nakshatra_sample = NakshatraDetail(name="Ashwini", index=0, pada=1, lord="Ketu", deity="Ashvins")
    sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sign_names_ta = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]

    planets: list[PlanetInfo] = []
    for p_name, (s_idx, deg) in planets_spec.items():
        planets.append(
            PlanetInfo(
                name=p_name,
                body_id=1,
                longitude=(s_idx - 1) * 30.0 + deg,
                latitude=0.0,
                distance_au=1.0,
                speed_deg_per_day=1.0,
                is_retrograde=False,
                sign_index=s_idx,
                sign_name=sign_names[s_idx - 1],
                sign_name_tamil=sign_names_ta[s_idx - 1],
                degree_in_sign=deg,
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

    asc = AscendantInfo(
        degree=(lagna_sign - 1) * 30.0 + 15.0,
        sign_index=lagna_sign,
        sign_name=sign_names[lagna_sign - 1],
        sign_name_tamil=sign_names_ta[lagna_sign - 1],
        degree_in_sign=15.0,
        nakshatra=nakshatra_sample,
    )

    mid = AscendantInfo(
        degree=270.0,
        sign_index=10,
        sign_name="Capricorn",
        sign_name_tamil="மகரம்",
        degree_in_sign=0.0,
        nakshatra=nakshatra_sample,
    )

    meta = CalculationMetadata(
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
    )

    return HoroscopeResponse(
        metadata=meta,
        ascendant=asc,
        midheaven=mid,
        planets=planets,
        houses=houses,
    )


class TestDevaKeralamRulesRegistry:
    """Verify registration, integrity, and retrieval of Deva Keralam rules."""

    def test_all_rules_registered(self):
        """Ensure all 23 Deva Keralam rules are registered in the Master RulesRegistry."""
        for rule in DEVA_KERALAM_RULES:
            retrieved = RulesRegistry.get_rule_by_id(rule.rule_id)
            assert retrieved is not None, f"Rule {rule.rule_id} not found in RulesRegistry"
            assert retrieved.rule_id == rule.rule_id

    def test_rule_metadata_integrity(self):
        """Ensure each rule contains required bilingual metadata and valid conditions."""
        for rule in DEVA_KERALAM_RULES:
            assert rule.name_en and len(rule.name_en) > 10, f"Incomplete name_en for {rule.rule_id}"
            assert rule.name_ta and len(rule.name_ta) > 10, f"Incomplete name_ta for {rule.rule_id}"
            assert rule.interpretation_en and len(rule.interpretation_en) > 30, f"Incomplete interpretation_en for {rule.rule_id}"
            assert rule.interpretation_ta and len(rule.interpretation_ta) > 30, f"Incomplete interpretation_ta for {rule.rule_id}"
            assert rule.source_reference and "Deva Keralam" in rule.source_reference, f"Invalid source_reference for {rule.rule_id}"
            assert rule.condition_tree and "condition_type" in rule.condition_tree, f"Invalid condition_tree for {rule.rule_id}"


class TestDevaKeralamEvaluator:
    """Evaluate Deva Keralam classical rules against synthetic astronomical chart contexts."""

    def test_koorma_yoga_evaluation(self):
        """Koorma Yoga: Libra Lagna (7), Jupiter in Sagittarius (9) in 3rd house, Venus in Leo (5) in 11th house."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (9, 10.0),  # Sagittarius (9), house 3 from Libra
                "Venus": (5, 12.0),    # Leo (5), house 11 from Libra
                "Sun": (7, 5.0),
                "Moon": (1, 15.0),
                "Mars": (2, 8.0),
                "Mercury": (8, 14.0),
                "Saturn": (11, 20.0),
                "Rahu": (3, 10.0),
                "Ketu": (9, 10.0),
            },
            lagna_sign=7,  # Libra
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-KOORMA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True
        assert len(result.evidence) > 0

    def test_kubera_yoga_evaluation(self):
        """Kubera Yoga: Aries Lagna (1), Venus in Taurus (2) in 2nd house, Jupiter in Aquarius (11) in 11th house."""
        chart = make_test_horoscope(
            planets_spec={
                "Venus": (2, 10.0),     # Taurus (2nd house)
                "Jupiter": (11, 15.0),  # Aquarius (11th house)
                "Sun": (1, 20.0),
                "Moon": (4, 12.0),
                "Mars": (10, 5.0),
                "Mercury": (1, 10.0),
                "Saturn": (7, 14.0),
                "Rahu": (6, 18.0),
                "Ketu": (12, 18.0),
            },
            lagna_sign=1,  # Aries
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-KUBERA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_rudrasana_yoga_evaluation(self):
        """Rudrasana Yoga: Mars in 1st house (Aries), Venus and Rahu conjoined in Taurus (2nd house)."""
        chart = make_test_horoscope(
            planets_spec={
                "Mars": (1, 15.0),    # 1st house
                "Venus": (2, 10.0),   # Taurus
                "Rahu": (2, 12.0),    # Taurus conjoined Venus
                "Jupiter": (9, 5.0),
                "Saturn": (11, 14.0),
                "Sun": (1, 5.0),
                "Moon": (4, 10.0),
                "Mercury": (12, 2.0),
                "Ketu": (8, 12.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-RUDRASANA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_scorpio_sama_astrology_yoga(self):
        """Scorpio Lagna Sama Nadiamsa: Scorpio (8) Lagna, Venus and Saturn in Pisces (12 - 5th house)."""
        chart = make_test_horoscope(
            planets_spec={
                "Venus": (12, 27.0),  # Pisces (5th house) - Exalted
                "Saturn": (12, 14.0), # Pisces (5th house)
                "Jupiter": (9, 10.0),
                "Mars": (8, 5.0),
                "Sun": (10, 15.0),
                "Moon": (4, 20.0),
                "Mercury": (11, 8.0),
                "Rahu": (6, 11.0),
                "Ketu": (12, 11.0),
            },
            lagna_sign=8,  # Scorpio
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-SCORPIO-SAMA-ASTROLOGY-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_cancer_kubera_mars_exaltation(self):
        """Cancer Lagna Kubera Nadiamsa: Cancer (4) Lagna, Mars exalted in Capricorn (10 - 7th house)."""
        chart = make_test_horoscope(
            planets_spec={
                "Mars": (10, 28.0),   # Capricorn (7th house) - Exalted
                "Jupiter": (4, 15.0), # Cancer Lagna
                "Sun": (5, 10.0),
                "Moon": (2, 3.0),
                "Venus": (6, 12.0),
                "Mercury": (5, 20.0),
                "Saturn": (7, 18.0),
                "Rahu": (3, 14.0),
                "Ketu": (9, 14.0),
            },
            lagna_sign=4,  # Cancer
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-CANCER-KUBERA-MARS-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_chandra_kampita_avastha(self):
        """Chandra Kampita Avastha: Moon in Leo (5), Saturn and Mars conjoined in Aries (1)."""
        chart = make_test_horoscope(
            planets_spec={
                "Moon": (5, 12.0),    # Leo
                "Saturn": (1, 10.0),  # Aries
                "Mars": (1, 14.0),    # Aries conjoined Saturn
                "Sun": (6, 5.0),
                "Jupiter": (9, 20.0),
                "Venus": (7, 15.0),
                "Mercury": (6, 18.0),
                "Rahu": (11, 4.0),
                "Ketu": (5, 4.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-CHANDRA-KAMPITA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_garga_kali_yuga_rule(self):
        """Sage Garga Kali Yuga Rule: Sun exalted in Aries (1) D1 and in Libra (7) D9.
        
        In D9 (Navamsa), 19° Aries: (19° * 9 / 30) = 5.7 -> 6th Navamsa of Aries = Virgo (6) or Libra (7) depending on calculation.
        For Aries: Navamsas are 1=Aries, 2=Taurus, 3=Gemini, 4=Cancer, 5=Leo, 6=Virgo, 7=Libra.
        7th Navamsa is 20°00' to 23°20' Aries.
        Let's put Sun at 21.0° Aries: it falls in Libra (7) Navamsa!
        """
        chart = make_test_horoscope(
            planets_spec={
                "Sun": (1, 21.0),     # Aries (1) at 21° -> D9 falls in Libra (7) (Debilitated)
                "Jupiter": (4, 15.0),
                "Moon": (2, 10.0),
                "Mars": (10, 5.0),
                "Mercury": (1, 10.0),
                "Venus": (12, 15.0),
                "Saturn": (7, 20.0),
                "Rahu": (3, 8.0),
                "Ketu": (9, 8.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-GARGA-KALI-YUGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True
        assert "d1" in result.evidence[0].lower() or "d9" in result.evidence[0].lower()

    def test_mathanga_yoga_evaluation(self):
        """Mathanga Yoga: Aries Lagna, Jupiter in 1st (1), Venus in 4th (4), Sun in 10th (10)."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (1, 10.0),   # 1st house
                "Venus": (4, 15.0),     # 4th house
                "Sun": (10, 20.0),      # 10th house
                "Moon": (2, 12.0),
                "Mars": (1, 5.0),
                "Mercury": (10, 8.0),
                "Saturn": (7, 14.0),
                "Rahu": (3, 11.0),
                "Ketu": (9, 11.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-MATHANGA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True
        assert len(result.evidence) >= 3

    def test_malavya_cancellation_evaluation(self):
        """Malavya Yoga Cancellation: Sagittarius Lagna (9), Venus in Pisces (12 - 4th house) conjoined Saturn."""
        chart = make_test_horoscope(
            planets_spec={
                "Venus": (12, 15.0),    # Pisces (4th house) - Exalted
                "Saturn": (12, 20.0),   # Conjoined Venus
                "Jupiter": (9, 10.0),
                "Sun": (1, 12.0),
                "Moon": (4, 8.0),
                "Mars": (10, 5.0),
                "Mercury": (11, 14.0),
                "Rahu": (2, 7.0),
                "Ketu": (8, 7.0),
            },
            lagna_sign=9,  # Sagittarius
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-MALAVYA-CANCELLATION-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_chhatra_yoga_evaluation(self):
        """Chhatra Yoga: Aries Lagna (1), Moon in 2nd (2), Venus in 9th (9), Jupiter in 1st (1)."""
        chart = make_test_horoscope(
            planets_spec={
                "Moon": (2, 14.0),      # 2nd house
                "Venus": (9, 18.0),     # 9th house
                "Jupiter": (1, 12.0),   # 1st house
                "Sun": (10, 5.0),
                "Mars": (10, 15.0),
                "Mercury": (9, 10.0),
                "Saturn": (11, 22.0),
                "Rahu": (4, 6.0),
                "Ketu": (10, 6.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-CHHATRA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_mani_pravada_yoga_evaluation(self):
        """Mani Pravada Yoga: Aries Lagna, Jupiter in 2nd (2), Mars in 3rd (3), Venus in 4th (4)."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (2, 10.0),   # 2nd house
                "Mars": (3, 15.0),      # 3rd house
                "Venus": (4, 12.0),     # 4th house
                "Sun": (1, 5.0),
                "Moon": (5, 20.0),
                "Mercury": (1, 15.0),
                "Saturn": (11, 10.0),
                "Rahu": (6, 8.0),
                "Ketu": (12, 8.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-MANI-PRAVADA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_maha_pandita_yoga_evaluation(self):
        """Maha Pandita Yoga: Jupiter in 1st house."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (1, 15.0),   # 1st house
                "Sun": (10, 10.0),
                "Moon": (4, 12.0),
                "Mars": (2, 8.0),
                "Mercury": (11, 14.0),
                "Venus": (12, 20.0),
                "Saturn": (7, 18.0),
                "Rahu": (5, 9.0),
                "Ketu": (11, 9.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-MAHA-PANDITA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_aquarius_champaka_evaluation(self):
        """Aquarius Lagna Champakamsa: Aquarius (11) Lagna, Jupiter in Cancer (4 - watery sign), Venus in 11th (9)."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (4, 12.0),   # Cancer (watery sign)
                "Venus": (9, 15.0),     # 11th house from Aquarius
                "Sun": (11, 10.0),
                "Moon": (2, 20.0),
                "Mars": (1, 8.0),
                "Mercury": (10, 14.0),
                "Saturn": (11, 5.0),
                "Rahu": (6, 12.0),
                "Ketu": (12, 12.0),
            },
            lagna_sign=11,  # Aquarius
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-AQUARIUS-CHAMPAKA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_gemini_indramsa_evaluation(self):
        """Gemini Lagna Indramsa: Gemini (3) Lagna, Mercury in 1st (3), Jupiter in 5th (7)."""
        chart = make_test_horoscope(
            planets_spec={
                "Mercury": (3, 10.0),   # 1st house
                "Jupiter": (7, 14.0),   # 5th house
                "Sun": (4, 12.0),
                "Moon": (2, 8.0),
                "Mars": (10, 5.0),
                "Venus": (5, 18.0),
                "Saturn": (11, 20.0),
                "Rahu": (1, 15.0),
                "Ketu": (7, 15.0),
            },
            lagna_sign=3,  # Gemini
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-GEMINI-INDRAMSA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_ksheera_kumbha_remedy_evaluation(self):
        """Ksheera Kumbha Remedy: Aries Lagna, Sun and Saturn conjoined in 9th house (Sagittarius 9)."""
        chart = make_test_horoscope(
            planets_spec={
                "Sun": (9, 12.0),       # 9th house
                "Saturn": (9, 16.0),    # Conjoined Sun
                "Jupiter": (4, 10.0),
                "Moon": (1, 15.0),
                "Mars": (6, 8.0),
                "Mercury": (8, 14.0),
                "Venus": (10, 20.0),
                "Rahu": (5, 11.0),
                "Ketu": (11, 11.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-KSHEERA-KUMBHA-REMEDY-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_matanga_yoga_evaluation(self):
        """Deva Keralam Matanga Yoga: Exalted Jupiter (4), Venus (4), and Moon (4) in Cancer."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (4, 28.0),   # Cancer Exalted (Pisces Navamsa)
                "Venus": (4, 15.0),     # Cancer
                "Moon": (4, 10.0),      # Cancer
                "Sun": (1, 10.0),
                "Mars": (10, 5.0),
                "Mercury": (12, 14.0),
                "Saturn": (11, 20.0),
                "Rahu": (3, 11.0),
                "Ketu": (9, 11.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-MATANGA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_koorma_yoga_evaluation(self):
        """Deva Keralam Koorma Yoga: Jupiter in 1st, Venus in 3rd."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (1, 12.0),   # 1st house
                "Venus": (3, 15.0),     # 3rd house
                "Sun": (10, 5.0),
                "Moon": (4, 10.0),
                "Mars": (11, 8.0),
                "Mercury": (9, 14.0),
                "Saturn": (11, 22.0),
                "Rahu": (2, 11.0),
                "Ketu": (8, 11.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-KOORMA-YOGA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_sagittarius_varuna_royal_yoga_evaluation(self):
        """Deva Keralam Varuna Royal Yoga: Sagittarius (9) Lagna, Jup+Moon in 1st, Saturn in 3rd."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (9, 7.8),    # Sagittarius Lagna Varuna Nadiamsa
                "Moon": (9, 15.0),      # Conjoined in Lagna
                "Saturn": (11, 14.0),   # 3rd house Aquarius (Moolatrikona)
                "Venus": (12, 27.0),    # Exalted 4th house
                "Sun": (2, 10.0),
                "Mars": (2, 14.0),
                "Mercury": (2, 18.0),
                "Rahu": (6, 12.0),
                "Ketu": (12, 12.0),
            },
            lagna_sign=9,  # Sagittarius
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-SAGITTARIUS-VARUNA-ROYAL-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_aquarius_viswambhara_writer_evaluation(self):
        """Deva Keralam Viswambhara Nadiamsa: Aquarius Lagna (11), Jupiter in Scorpio (8)."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (8, 8.9),    # Scorpio (10th house)
                "Sun": (10, 5.0),
                "Moon": (2, 12.0),
                "Mars": (1, 15.0),
                "Venus": (12, 20.0),
                "Mercury": (6, 14.0),
                "Saturn": (11, 10.0),
                "Rahu": (5, 8.0),
                "Ketu": (11, 8.0),
            },
            lagna_sign=11,  # Aquarius
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-AQUARIUS-VISWAMBHARA-WRITER-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_taurus_progeny_brahma_shapa_evaluation(self):
        """Deva Keralam Progeny Curse: Taurus (2) Lagna, Jupiter in Virgo (6 - 5th house), Saturn in Pisces (12) aspecting Jupiter."""
        chart = make_test_horoscope(
            planets_spec={
                "Jupiter": (6, 12.0),   # 5th house (Virgo)
                "Saturn": (12, 10.0),   # 11th house (Pisces) - 7th aspect onto Virgo
                "Sun": (1, 15.0),
                "Moon": (4, 10.0),
                "Mars": (8, 6.0),
                "Mercury": (5, 14.0),
                "Venus": (2, 18.0),
                "Rahu": (3, 11.0),
                "Ketu": (9, 11.0),
            },
            lagna_sign=2,  # Taurus
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-PROGENY-BRAHMA-SHAPA-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True

    def test_rahu_10th_ganga_setu_evaluation(self):
        """Deva Keralam 10th House Rahu: Rahu in 10th house."""
        chart = make_test_horoscope(
            planets_spec={
                "Rahu": (10, 15.0),     # 10th house
                "Sun": (1, 10.0),
                "Moon": (4, 12.0),
                "Mars": (7, 14.0),
                "Mercury": (2, 8.0),
                "Jupiter": (9, 18.0),
                "Venus": (12, 22.0),
                "Saturn": (11, 5.0),
                "Ketu": (4, 15.0),
            },
            lagna_sign=1,
        )
        ctx = ChartContext(chart)
        rule = RulesRegistry.get_rule_by_id("RULE-DK-B1-RAHU-10TH-GANGA-SETU-01")
        assert rule is not None
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True
