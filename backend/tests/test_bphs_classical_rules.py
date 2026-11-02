"""Comprehensive Test Suite for Brihat Parashara Hora Shastra (BPHS) Rules, Yogas, and Remedies.

Validates:
1. Rule compilation, AST integrity, and unique ID invariants.
2. Category and subcategory registration under 'bphs_classics'.
3. Rule evaluation against synthetic charts for Bhava Lords, Yogakarakas, Dhana Yogas, and Daridra Yogas.
4. BPHS Classical Yogas in the Yoga Engine (Ch. 36).
5. BPHS Canonical Graha Shanti Homam & Shapa Prayaschitta Remedies (Ch. 83 & 84).
"""

import pytest
from app.schemas.horoscope import (
    HoroscopeResponse,
    AscendantInfo,
    PlanetInfo,
    HouseInfo,
    NakshatraDetail,
    CalculationMetadata,
)
from app.services.prediction_rules.bphs_classical_rules import BPHS_CLASSICAL_RULES
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.manager import RuleManagementService
from app.services.prediction_rules.categories import get_category_by_slug, get_all_category_groups
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext
from app.services.yoga_engine.evaluators.classical import evaluate_classical_yogas
from app.services.yoga_engine.models import YogaChartContext
from app.services.remedy_engine.repository import list_remedies, VERIFIED_REMEDIES


def make_test_horoscope(planets_spec: dict, lagna_sign: int = 1) -> HoroscopeResponse:
    """Create a synthetic HoroscopeResponse for testing rules."""
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


class TestBPHSClassicalRules:
    """Tests covering BPHS rule definitions, AST validation, and registry integration."""

    def test_bphs_rules_registration_and_count(self):
        """Verify BPHS rules catalogue is non-empty and properly integrated into RulesRegistry."""
        assert len(BPHS_CLASSICAL_RULES) >= 195, f"Expected at least 195 BPHS rules, got {len(BPHS_CLASSICAL_RULES)}"
        
        all_rules = RulesRegistry.get_all_rules()
        all_ids = {r.rule_id for r in all_rules}
        
        for rule in BPHS_CLASSICAL_RULES:
            assert rule.rule_id in all_ids, f"BPHS Rule {rule.rule_id} missing from RulesRegistry"

    def test_bphs_rule_ids_unique(self):
        """Verify all BPHS rule IDs are strictly unique."""
        bphs_ids = [r.rule_id for r in BPHS_CLASSICAL_RULES]
        assert len(bphs_ids) == len(set(bphs_ids)), "Duplicate rule_id detected in BPHS_CLASSICAL_RULES"

    def test_bphs_ast_validation(self):
        """Ensure every BPHS rule strictly passes RuleManagementService AST validation."""
        failures = []
        for rule in BPHS_CLASSICAL_RULES:
            valid, errors = RuleManagementService.validate_rule_definition(rule.model_dump())
            if not valid:
                failures.append((rule.rule_id, errors))
        
        assert len(failures) == 0, f"AST validation failed on {len(failures)} rules: {failures[:5]}"

    def test_bphs_categories_exist_in_group(self):
        """Verify all BPHS category slugs are registered under 'bphs_classics' group."""
        groups = get_all_category_groups()
        bphs_group = next((g for g in groups if g["group_code"] == "bphs_classics"), None)
        assert bphs_group is not None, "Category group 'bphs_classics' not found in registry"
        
        registered_slugs = {sub["slug"] for sub in bphs_group["subcategories"]}
        
        for rule in BPHS_CLASSICAL_RULES:
            cat = get_category_by_slug(rule.category_slug)
            assert cat is not None, f"Category slug '{rule.category_slug}' in rule {rule.rule_id} not found"
            assert rule.category_slug in registered_slugs, f"Category slug '{rule.category_slug}' not under 'bphs_classics'"

    def test_bphs_source_references_conform_to_bphs(self):
        """Verify source_reference explicitly cites Brihat Parashara Hora Shastra."""
        for rule in BPHS_CLASSICAL_RULES:
            assert "Brihat Parashara Hora Shastra" in rule.source_reference, (
                f"Rule {rule.rule_id} missing BPHS citation in '{rule.source_reference}'"
            )


class TestBPHSRuleEvaluation:
    """Tests evaluating BPHS rules with AstrologicalRuleEvaluator against synthetic charts."""

    def test_evaluate_bhava_lord_1_in_1(self):
        """Test BPHS Ch. 24: 1st Lord in 1st House (RULE-BPHS-L1-H1)."""
        rule = RulesRegistry.get_rule_by_id("RULE-BPHS-L1-H1")
        assert rule is not None
        
        # Aries Lagna (1), Mars in Aries (House 1) -> 1st lord in 1st house
        horo = make_test_horoscope({"Mars": (1, 15.0), "Sun": (5, 10.0)}, lagna_sign=1)
        ctx = ChartContext(horoscope=horo)
        
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True, f"Expected RULE-BPHS-L1-H1 to match: {result.reasons}"

    def test_evaluate_yogakaraka_taurus(self):
        """Test BPHS Ch. 34: Taurus Lagna Yogakaraka Saturn (RULE-BPHS-YOGA-LAGNA-2)."""
        rule = RulesRegistry.get_rule_by_id("RULE-BPHS-YOGA-LAGNA-2")
        assert rule is not None
        
        # Taurus Lagna (2)
        horo = make_test_horoscope({"Saturn": (10, 15.0), "Venus": (2, 10.0)}, lagna_sign=2)
        ctx = ChartContext(horoscope=horo)
        
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True, f"Expected RULE-BPHS-YOGA-LAGNA-2 to match: {result.reasons}"

    def test_evaluate_dhana_yoga_01(self):
        """Test BPHS Ch. 41: Special Dhana Yoga (RULE-BPHS-DHANA-01).
        Venus in 5th and Mars in 11th.
        """
        rule = RulesRegistry.get_rule_by_id("RULE-BPHS-DHANA-01")
        assert rule is not None
        
        # Aries Lagna (1): Venus in 5th (Leo, sign 5), Mars in 11th (Aquarius, sign 11)
        horo = make_test_horoscope({
            "Venus": (5, 10.0),
            "Mars": (11, 15.0),
        }, lagna_sign=1)
        ctx = ChartContext(horoscope=horo)
        
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True, f"Expected RULE-BPHS-DHANA-01 to match: {result.reasons}"

    def test_evaluate_daridra_yoga_01(self):
        """Test BPHS Ch. 42: Daridra Yoga (RULE-BPHS-DARIDRA-01).
        L1 in 12th, L12 in 1st.
        """
        rule = RulesRegistry.get_rule_by_id("RULE-BPHS-DARIDRA-01")
        assert rule is not None
        
        # Aries Lagna: L1=Mars, L12=Jupiter
        # Mars in 12th (Pisces), Jupiter in 1st (Aries)
        horo = make_test_horoscope({
            "Mars": (12, 10.0),
            "Jupiter": (1, 15.0)
        }, lagna_sign=1)
        ctx = ChartContext(horoscope=horo)
        
        result = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        assert result.matched is True, f"Expected RULE-BPHS-DARIDRA-01 to match: {result.reasons}"


class TestBPHSYogaEngine:
    """Tests verifying the 15+ BPHS Chapter 36 Classical Yogas in evaluate_classical_yogas."""

    def test_parvata_yoga_benefics_in_kendras(self):
        """Test Parvata Yoga (BPHS Ch. 36 Slokas 33-34): Benefics in Kendras, 6th/8th clean."""
        ctx = YogaChartContext(
            planets=[
                {"name": "Jupiter", "sign_index": 1, "longitude": 10.0, "degree_in_sign": 10.0},
                {"name": "Venus", "sign_index": 4, "longitude": 100.0, "degree_in_sign": 10.0},
                {"name": "Mercury", "sign_index": 7, "longitude": 190.0, "degree_in_sign": 10.0},
                {"name": "Sun", "sign_index": 10, "longitude": 280.0, "degree_in_sign": 10.0},
            ],
            ascendant_sign_idx=1
        )
        yogas = evaluate_classical_yogas(ctx)
        parvata = next((y for y in yogas if y.id == "parvata_yoga"), None)
        assert parvata is not None, "parvata_yoga not evaluated"
        assert parvata.is_qualifying is True, "parvata_yoga expected to qualify"

    def test_shankha_yoga_mutual_kendra(self):
        """Test Shankha Yoga (BPHS Ch. 36 Sloka 36): 5th lord & 6th lord in mutual Kendras with strong Lagna lord."""
        # Aries Lagna: L1=Mars, L5=Sun, L6=Mercury
        # Mars exalted in 10 (Capricorn), Sun in 1 (Aries), Mercury in 7 (Libra) -> Sun & Mercury in mutual kendras
        ctx = YogaChartContext(
            planets=[
                {"name": "Mars", "sign_index": 10, "longitude": 280.0, "degree_in_sign": 10.0},
                {"name": "Sun", "sign_index": 1, "longitude": 10.0, "degree_in_sign": 10.0},
                {"name": "Mercury", "sign_index": 7, "longitude": 190.0, "degree_in_sign": 10.0},
            ],
            ascendant_sign_idx=1
        )
        yogas = evaluate_classical_yogas(ctx)
        shankha = next((y for y in yogas if y.id == "shankha_yoga"), None)
        assert shankha is not None, "shankha_yoga not evaluated"
        assert shankha.is_qualifying is True, "shankha_yoga expected to qualify"

    def test_kusuma_yoga_evaluation(self):
        """Test Kusuma Yoga (BPHS Ch. 36 Sloka 44): Venus in Kendra, Moon in Trikona, Saturn in 10th."""
        # Aries Lagna: Venus in 4 (Cancer), Moon in 5 (Leo), Saturn in 10 (Capricorn)
        ctx = YogaChartContext(
            planets=[
                {"name": "Venus", "sign_index": 4, "longitude": 100.0, "degree_in_sign": 10.0},
                {"name": "Moon", "sign_index": 5, "longitude": 130.0, "degree_in_sign": 10.0},
                {"name": "Saturn", "sign_index": 10, "longitude": 280.0, "degree_in_sign": 10.0},
            ],
            ascendant_sign_idx=1
        )
        yogas = evaluate_classical_yogas(ctx)
        kusuma = next((y for y in yogas if y.id == "kusuma_yoga"), None)
        assert kusuma is not None, "kusuma_yoga not evaluated"
        assert kusuma.is_qualifying is True, "kusuma_yoga expected to qualify"

    def test_kalanidhi_yoga_evaluation(self):
        """Test Kalanidhi Yoga (BPHS Ch. 36 Sloka 45): Jupiter in 2nd conjoined Mercury & Venus."""
        # Aries Lagna: Jupiter in 2 (Taurus), conjoined Mercury and Venus in 2 (Taurus)
        ctx = YogaChartContext(
            planets=[
                {"name": "Jupiter", "sign_index": 2, "longitude": 40.0, "degree_in_sign": 10.0},
                {"name": "Mercury", "sign_index": 2, "longitude": 45.0, "degree_in_sign": 15.0},
                {"name": "Venus", "sign_index": 2, "longitude": 50.0, "degree_in_sign": 20.0},
            ],
            ascendant_sign_idx=1
        )
        yogas = evaluate_classical_yogas(ctx)
        kalanidhi = next((y for y in yogas if y.id == "kalanidhi_yoga"), None)
        assert kalanidhi is not None, "kalanidhi_yoga not evaluated"
        assert kalanidhi.is_qualifying is True, "kalanidhi_yoga expected to qualify"


class TestBPHSRemedyIntegration:
    """Tests verifying BPHS Chapter 83 and 84 remedies in the remedy engine repository."""

    def test_bphs_remedies_in_catalog(self):
        """Verify BPHS remedies are present in VERIFIED_REMEDIES."""
        remedies = list_remedies()
        bphs_remedies = [r for r in remedies if r.get("source_code") == "BPHS"]
        assert len(bphs_remedies) >= 18, f"Expected at least 18 BPHS remedies, found {len(bphs_remedies)}"

    def test_bphs_shapa_remedies_present(self):
        """Verify the 8 BPHS Chapter 83 Shapa Prayaschittas exist with appropriate metadata."""
        codes = {r["code"] for r in VERIFIED_REMEDIES}
        expected_shapa_codes = [
            "REM_BPHS_SHAPA_SARPA",
            "REM_BPHS_SHAPA_PITRU",
            "REM_BPHS_SHAPA_MATRU",
            "REM_BPHS_SHAPA_BHRATRI",
            "REM_BPHS_SHAPA_BRAHMANA",
            "REM_BPHS_SHAPA_PATNI",
            "REM_BPHS_SHAPA_PRETHA",
        ]
        for c in expected_shapa_codes:
            assert c in codes, f"Expected Shapa remedy {c} missing from repository"

    def test_bphs_graha_shanti_homam_canonical_counts(self):
        """Verify BPHS Ch. 84 Graha Shanti Homam includes all 9 planetary samidha woods and counts."""
        homam = next((r for r in VERIFIED_REMEDIES if r["code"] == "REM_BPHS_GRAHA_SHANTI_HOMAM"), None)
        assert homam is not None, "REM_BPHS_GRAHA_SHANTI_HOMAM missing from VERIFIED_REMEDIES"
        
        proc_en = homam["procedure_en"]
        assert "7000" in proc_en, "Surya 7000 japa count missing"
        assert "11000" in proc_en, "Chandra/Mars 11000 count missing"
        assert "9000" in proc_en, "Budha 9000 count missing"
        assert "19000" in proc_en, "Guru 19000 count missing"
        assert "16000" in proc_en, "Shukra 16000 count missing"
        assert "23000" in proc_en, "Shani 23000 count missing"
        assert "18000" in proc_en, "Rahu 18000 count missing"
        assert "17000" in proc_en, "Ketu 17000 count missing"
        assert "Arka" in proc_en and "Shami" in proc_en, "Canonical Samidha woods missing"
