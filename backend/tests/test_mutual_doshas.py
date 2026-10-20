"""Tests for Phase 5: Mutual Dosha Analysis — Kuja Samadosham & Papasamya.

Test coverage:
1. Papasamya individual calculation — Lagna, Moon, Venus frames, all 5 malefics.
2. Mutual Papasamya verdict — FAVORABLE (equal, groom>=bride), TOLERABLE, UNFAVORABLE.
3. Kuja Samadosham — NEITHER_AFFLICTED, CANCELLED_BY_RULE, MUTUALLY_MATCHED (balanced),
   MITIGATED (counterpoise / mild), NOT_MUTUALLY_MATCHED (gross disparity).
4. Partner-dependent dosha summary — Rajju and Vedha vetoes preserved.
5. Full pipeline: evaluate_mutual_dosha_analysis.
6. Determinism — identical inputs always produce identical outputs.
7. Edge cases — missing planets, None kuja assessments.
"""

from __future__ import annotations

import pytest
from typing import Dict, Any, Optional

from app.services.marriage_engine.models import (
    Gender,
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    PapasamyaResult,
    PapasamyaVerdict,
    SamadoshamOutcome,
    IndividualKujaAssessment,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)
from app.services.marriage_engine.mutual_doshas import (
    calculate_single_papasamya,
    evaluate_mutual_papasamya,
    evaluate_mutual_kuja_samadosham,
    evaluate_mutual_dosha_analysis,
    PAPASAMYA_WEIGHTS,
    PAPASAMYA_HOUSES,
    INDEPENDENT_VETO_DOSHAS,
    COUNTERPOISE_HOUSES,
    COUNTERPOISE_PLANETS,
)


# ---------------------------------------------------------------------------
# Test Chart Factory Helpers
# ---------------------------------------------------------------------------

def _make_planet(
    name: str,
    sign_index: int,
    house: int,
    longitude: Optional[float] = None,
    is_retrograde: bool = False,
) -> MarriagePlanet:
    """Create a minimal MarriagePlanet for testing."""
    if longitude is None:
        longitude = (sign_index - 1) * 30.0 + 5.0
    return MarriagePlanet(
        name=name,
        body_id=0,
        longitude=longitude,
        sign_index=sign_index,
        sign_name=SIGN_NAMES_EN.get(sign_index, "Unknown"),
        sign_name_tamil=SIGN_NAMES_TA.get(sign_index, ""),
        degree_in_sign=longitude % 30.0,
        house=house,
        is_retrograde=is_retrograde,
        nakshatra_index=0,
        nakshatra_name="Ashwini",
        nakshatra_pada=1,
        navamsa_sign_index=1,
    )


def _make_house(house_number: int, sign_index: int) -> MarriageHouse:
    """Create a minimal MarriageHouse for testing."""
    return MarriageHouse(
        house_number=house_number,
        sign_index=sign_index,
        sign_name=SIGN_NAMES_EN.get(sign_index, "Unknown"),
        sign_name_tamil=SIGN_NAMES_TA.get(sign_index, ""),
        cusp_degree=(sign_index - 1) * 30.0,
        degree_in_sign=0.0,
        lord_name="Unknown",
    )


def _make_chart(
    person_id: str,
    gender: Gender,
    lagna_sign: int,
    moon_sign: int,
    venus_sign: int,
    extra_planets: Optional[Dict[str, MarriagePlanet]] = None,
) -> MarriageChartContext:
    """Create a minimal MarriageChartContext for Papasamya and Samadosham testing."""
    grahas: Dict[str, MarriagePlanet] = {}

    # Moon
    moon_house = ((moon_sign - lagna_sign) % 12) + 1
    grahas["Moon"] = _make_planet("Moon", moon_sign, moon_house)

    # Venus
    venus_house = ((venus_sign - lagna_sign) % 12) + 1
    grahas["Venus"] = _make_planet("Venus", venus_sign, venus_house)

    # Add Sun as a natural malefic in a neutral sign (sign 3, house depends on lagna)
    sun_sign = 3
    sun_house = ((sun_sign - lagna_sign) % 12) + 1
    grahas["Sun"] = _make_planet("Sun", sun_sign, sun_house)

    if extra_planets:
        grahas.update(extra_planets)

    houses: Dict[int, MarriageHouse] = {}
    for h in range(1, 13):
        sign = ((lagna_sign + h - 2) % 12) + 1
        houses[h] = _make_house(h, sign)

    return MarriageChartContext(
        person_id=person_id,
        person_name=person_id,
        gender=gender,
        birth_date_iso="1990-01-01",
        birth_time_iso="06:00:00",
        timezone="Asia/Kolkata",
        latitude=13.08,
        longitude=80.27,
        ascendant_degree=0.0,
        ascendant_sign_idx=lagna_sign,
        ascendant_sign_name=SIGN_NAMES_EN.get(lagna_sign, "Aries"),
        ascendant_sign_name_tamil=SIGN_NAMES_TA.get(lagna_sign, "மேஷம்"),
        ascendant_nakshatra_idx=0,
        ascendant_nakshatra_name="Ashwini",
        ascendant_nakshatra_pada=1,
        ascendant_navamsa_sign_idx=1,
        moon_degree=(moon_sign - 1) * 30.0 + 5.0,
        moon_sign_idx=moon_sign,
        moon_sign_name=SIGN_NAMES_EN.get(moon_sign, "Unknown"),
        moon_sign_name_tamil=SIGN_NAMES_TA.get(moon_sign, ""),
        moon_nakshatra_idx=0,
        moon_nakshatra_name="Ashwini",
        moon_nakshatra_pada=1,
        moon_navamsa_sign_idx=1,
        grahas=grahas,
        houses=houses,
    )


def _make_kuja(
    role: str,
    is_present: bool,
    is_cancelled: bool,
    severity: str,
    intensity: float,
) -> IndividualKujaAssessment:
    """Create a test IndividualKujaAssessment."""
    return IndividualKujaAssessment(
        subject_role=role,
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        house_convention="South Indian (1,2,4,7,8,12)",
        mars_longitude=60.0,
        mars_sign_index=3,
        mars_sign_name="Gemini",
        mars_degree_in_sign=0.0,
        mars_house_from_lagna=2,
        mars_house_from_moon=5,
        mars_house_from_venus=3,
        effective_intensity_percent=intensity,
        explanation_en=f"{role} Kuja test",
        explanation_ta=f"{role} குஜ சோதனை",
    )


# ---------------------------------------------------------------------------
# 1. Papasamya Individual Calculation Tests
# ---------------------------------------------------------------------------

class TestCalculateSinglePapasamya:
    """Tests for calculate_single_papasamya."""

    def test_no_malefics_in_afflicted_positions(self):
        """Chart with no malefics in houses 1,2,4,7,8,12 gives 0.0 total.

        Setup: lagna=6(Virgo), moon=9(Sagittarius), venus=9(Sagittarius).
        Place all malefics at sign 11 (Aquarius):
          - from lagna(6): (11-6)%12+1 = 6  — not in {1,2,4,7,8,12} ✓
          - from moon(9):  (11-9)%12+1 = 3  — not in {1,2,4,7,8,12} ✓
          - from venus(9): (11-9)%12+1 = 3  — not in {1,2,4,7,8,12} ✓
        Sun is also placed at sign 11 to override the default sign 3 placement.
        """
        safe_sign = 11
        planets = {}
        for name in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]:
            house_from_lagna = (safe_sign - 6) % 12 + 1  # = 6
            planets[name] = _make_planet(name, safe_sign, house_from_lagna)
        chart = _make_chart(
            "test", Gender.MALE,
            lagna_sign=6, moon_sign=9, venus_sign=9,
            extra_planets=planets,
        )
        result = calculate_single_papasamya(chart, "groom")
        assert result.total_papam == 0.0, (
            f"Expected 0.0 but got {result.total_papam}. "
            f"Placements: {result.placements_detail}"
        )
        assert result.lagna_papam == 0.0
        assert result.moon_papam == 0.0
        assert result.venus_papam == 0.0


    def test_mars_in_lagna_house_1(self):
        """Mars in house 1 from Lagna adds 1.0 to Lagna papam."""
        # Lagna = Aries (1); Mars in house 1 from lagna = sign 1
        # Moon and Venus in neutral positions (sign 6, house 6)
        mars = _make_planet("Mars", 1, 1)  # house 1 from lagna = sign 1
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=6, venus_sign=6,
            extra_planets={"Mars": mars},
        )
        result = calculate_single_papasamya(chart, "groom")
        # Mars in sign 1: from lagna(1) = house 1 (afflicted), from moon(6): (1-6)%12+1 = 8 (afflicted!),
        # from venus(6): same as moon = house 8 (afflicted!)
        assert result.lagna_papam == 1.0
        assert result.total_papam >= 1.0  # At least lagna contribution
        assert result.breakdown_by_planet["Mars"] >= 1.0

    def test_saturn_in_house_8_from_moon(self):
        """Saturn in house 8 from Moon contributes 1.0 to Moon papam."""
        # Lagna = Aries (1), Moon = Aries (1), Saturn in sign 8 (house 8 from lagna AND moon)
        saturn = _make_planet("Saturn", 8, 8)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=1, venus_sign=6,
            extra_planets={"Saturn": saturn},
        )
        result = calculate_single_papasamya(chart, "groom")
        # Saturn sign 8: from lagna(1) = house 8 (afflicted), from moon(1) = house 8 (afflicted)
        # from venus(6): (8-6)%12+1 = 3 (not afflicted)
        assert result.lagna_papam >= 1.0
        assert result.moon_papam >= 1.0
        assert result.breakdown_by_planet["Saturn"] >= 2.0  # lagna + moon frames

    def test_rahu_half_weight(self):
        """Rahu in an afflicted house contributes 0.5 points."""
        # Lagna = Aries (1), Rahu in house 7 from lagna = sign 7
        # Moon in sign 5 (house 5 from lagna, not afflicted relative to moon reference)
        rahu = _make_planet("Rahu", 7, 7)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=5, venus_sign=5,
            extra_planets={"Rahu": rahu},
        )
        result = calculate_single_papasamya(chart, "groom")
        # Rahu sign 7: from lagna(1) = house 7 (afflicted, +0.5)
        # from moon(5): (7-5)%12+1 = 3 (not afflicted)
        # from venus(5): same as moon = 3 (not afflicted)
        assert result.lagna_papam == pytest.approx(0.5, abs=0.01)
        assert result.breakdown_by_planet["Rahu"] == pytest.approx(0.5, abs=0.01)

    def test_ketu_half_weight(self):
        """Ketu in an afflicted house contributes 0.5 points."""
        ketu = _make_planet("Ketu", 2, 2)  # house 2 from lagna = sign 2 (afflicted)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=9, venus_sign=9,
            extra_planets={"Ketu": ketu},
        )
        result = calculate_single_papasamya(chart, "groom")
        # Ketu sign 2: from lagna(1) = house 2 (afflicted, +0.5)
        # from moon(9): (2-9)%12+1 = 6 (not afflicted)
        assert result.lagna_papam == pytest.approx(0.5, abs=0.01)
        assert result.breakdown_by_planet["Ketu"] == pytest.approx(0.5, abs=0.01)

    def test_sun_half_weight(self):
        """Sun in afflicted house contributes 0.5 points."""
        # Sun is added in all charts by default in house 3 from lagna (sign 3)
        # For lagna=1, moon=9, venus=9: Sun at sign 3 → house 3 from lagna (not afflicted)
        # But if lagna=1, sun at sign 4 → house 4 (afflicted)
        sun = _make_planet("Sun", 4, 4)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=9, venus_sign=9,
            extra_planets={"Sun": sun},
        )
        result = calculate_single_papasamya(chart, "groom")
        # Sun sign 4: from lagna(1) = house 4 (afflicted, +0.5)
        # from moon(9): (4-9)%12+1 = 8 (afflicted, +0.5)
        # from venus(9): same = house 8 (afflicted, +0.5)
        assert result.breakdown_by_planet["Sun"] >= 0.5

    def test_all_five_malefics_in_house_7(self):
        """All five malefics in house 7 from lagna accumulate correctly."""
        # Lagna = 1 (Aries); sign 7 = house 7 from lagna
        mars = _make_planet("Mars", 7, 7)
        saturn = _make_planet("Saturn", 7, 7)
        rahu = _make_planet("Rahu", 7, 7)
        ketu = _make_planet("Ketu", 7, 7)
        sun = _make_planet("Sun", 7, 7)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=9, venus_sign=9,
            extra_planets={"Mars": mars, "Saturn": saturn, "Rahu": rahu, "Ketu": ketu, "Sun": sun},
        )
        result = calculate_single_papasamya(chart, "groom")
        # From lagna(1): sign 7 = house 7 (afflicted)
        # weights: Mars 1.0, Saturn 1.0, Rahu 0.5, Ketu 0.5, Sun 0.5 = 3.5
        assert result.lagna_papam == pytest.approx(3.5, abs=0.01)
        assert result.total_papam >= 3.5

    def test_placements_detail_populated(self):
        """placements_detail list is populated for each afflicted placement."""
        mars = _make_planet("Mars", 7, 7)
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=9, venus_sign=9,
            extra_planets={"Mars": mars},
        )
        result = calculate_single_papasamya(chart, "groom")
        assert len(result.placements_detail) >= 1
        frames = [d["frame"] for d in result.placements_detail]
        assert "Lagna" in frames

    def test_missing_moon_skips_moon_frame(self):
        """If Moon is absent from grahas, Moon frame is skipped (no crash)."""
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=7, venus_sign=9,
        )
        del chart.grahas["Moon"]
        chart.moon_sign_idx = 0  # invalid — triggers None path
        # Override moon_sign_idx to a sign that doesn't match any planet
        result = calculate_single_papasamya(chart, "groom")
        # Should not crash; moon_papam should be 0 (no Moon planet found)
        assert isinstance(result, PapasamyaResult)

    def test_missing_venus_skips_venus_frame(self):
        """If Venus is absent from grahas, Venus frame is skipped (no crash)."""
        chart = _make_chart(
            "g", Gender.MALE, lagna_sign=1, moon_sign=9, venus_sign=3,
        )
        del chart.grahas["Venus"]
        result = calculate_single_papasamya(chart, "bride")
        assert isinstance(result, PapasamyaResult)
        assert "Warning" in result.explanation_en


# ---------------------------------------------------------------------------
# 2. Mutual Papasamya Verdict Tests
# ---------------------------------------------------------------------------

def _make_papa_result(role: str, lagna: float, moon: float, venus: float) -> PapasamyaResult:
    total = lagna + moon + venus
    return PapasamyaResult(
        subject_role=role,
        lagna_papam=lagna,
        moon_papam=moon,
        venus_papam=venus,
        total_papam=total,
        breakdown_by_planet={},
        placements_detail=[],
        explanation_en="",
        explanation_ta="",
    )


class TestEvaluateMutualPapasamya:
    """Tests for evaluate_mutual_papasamya."""

    def test_both_zero_indeterminate(self):
        """Both zero → INDETERMINATE."""
        g = _make_papa_result("groom", 0.0, 0.0, 0.0)
        b = _make_papa_result("bride", 0.0, 0.0, 0.0)
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.INDETERMINATE

    def test_equal_totals_favorable(self):
        """Equal totals → FAVORABLE."""
        g = _make_papa_result("groom", 1.0, 1.0, 0.5)
        b = _make_papa_result("bride", 1.0, 1.0, 0.5)
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.FAVORABLE
        assert diff_pct == pytest.approx(0.0, abs=0.1)

    def test_groom_slightly_higher_favorable(self):
        """Groom 10% above bride → FAVORABLE."""
        g = _make_papa_result("groom", 2.0, 1.0, 0.5)  # total 3.5
        b = _make_papa_result("bride", 1.5, 1.0, 0.5)  # total 3.0
        # diff = 0.5; max = 3.5; pct = 14.3% ≤ 25%
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.FAVORABLE

    def test_groom_excess_25_to_50_tolerable(self):
        """Groom 35% above bride → TOLERABLE."""
        g = _make_papa_result("groom", 2.7, 1.0, 0.5)  # total 4.2
        b = _make_papa_result("bride", 1.5, 1.0, 0.5)  # total 3.0
        # diff = 1.2; max = 4.2; pct ≈ 28.6%
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.TOLERABLE

    def test_bride_excess_above_25pct_unfavorable(self):
        """Bride > Groom by >25% and >=0.5pts → UNFAVORABLE."""
        g = _make_papa_result("groom", 1.0, 0.5, 0.5)  # total 2.0
        b = _make_papa_result("bride", 2.0, 1.0, 0.5)  # total 3.5
        # diff = -1.5 (bride excess); abs=1.5; pct = 1.5/3.5*100 ≈ 42.9% > 25%
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.UNFAVORABLE

    def test_bride_slight_excess_below_threshold_favorable(self):
        """Bride barely above groom by <25% → FAVORABLE."""
        g = _make_papa_result("groom", 1.5, 0.5, 0.5)  # total 2.5
        b = _make_papa_result("bride", 1.8, 0.5, 0.5)  # total 2.8
        # diff = 0.3; abs=0.3 < 0.5 → FAVORABLE (under absolute threshold)
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert verdict == PapasamyaVerdict.FAVORABLE

    def test_explanations_bilingual(self):
        """Both English and Tamil explanations are populated."""
        g = _make_papa_result("groom", 1.0, 1.0, 0.5)
        b = _make_papa_result("bride", 2.0, 1.0, 0.5)
        verdict, diff_pct, en, ta = evaluate_mutual_papasamya(g, b)
        assert len(en) > 10
        assert len(ta) > 5


# ---------------------------------------------------------------------------
# 3. Kuja Samadosham Tests
# ---------------------------------------------------------------------------

class TestEvaluateMutualKujaSamadosham:
    """Tests for evaluate_mutual_kuja_samadosham."""

    def _make_clean_chart(self, role: str, gender: Gender) -> MarriageChartContext:
        """Chart with no Mars in any Kuja house."""
        mars = _make_planet("Mars", 3, 3)  # house 3 — not a Kuja house
        return _make_chart(role, gender, lagna_sign=1, moon_sign=5, venus_sign=9,
                           extra_planets={"Mars": mars})

    def test_neither_afflicted_mutually_matched(self):
        """Both have no Kuja → MUTUALLY_MATCHED (NEITHER_AFFLICTED)."""
        g = _make_kuja("groom", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        b = _make_kuja("bride", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.MUTUALLY_MATCHED
        assert result.mutual_balance == "NEITHER_AFFLICTED"

    def test_both_cancelled_cancelled_by_rule(self):
        """Both have Kuja but both cancelled → CANCELLED_BY_RULE."""
        g = _make_kuja("groom", is_present=True, is_cancelled=True, severity="Cancelled", intensity=0.0)
        b = _make_kuja("bride", is_present=True, is_cancelled=True, severity="Cancelled", intensity=0.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.CANCELLED_BY_RULE
        assert result.mutual_balance == "BALANCED"
        assert len(result.cancellations_or_mitigations_applied) >= 1

    def test_both_active_balanced_mutually_matched(self):
        """Both active with similar intensity (≤25% delta) → MUTUALLY_MATCHED."""
        g = _make_kuja("groom", is_present=True, is_cancelled=False, severity="Moderate", intensity=60.0)
        b = _make_kuja("bride", is_present=True, is_cancelled=False, severity="Moderate", intensity=70.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        # delta = |60-70| = 10; max = 70; pct = 14.3% ≤ 25%
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.MUTUALLY_MATCHED
        assert result.mutual_balance == "BALANCED"

    def test_both_active_unequal_still_matched(self):
        """Both active but delta >25% — still MUTUALLY_MATCHED per Kalaprakasika mutual affliction rule."""
        g = _make_kuja("groom", is_present=True, is_cancelled=False, severity="High", intensity=90.0)
        b = _make_kuja("bride", is_present=True, is_cancelled=False, severity="Mild", intensity=30.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.MUTUALLY_MATCHED
        assert len(result.warnings) >= 1  # Warning about high delta

    def test_groom_active_bride_mild_mitigated(self):
        """Groom active (mild ≤50%), Bride none → MITIGATED."""
        g = _make_kuja("groom", is_present=True, is_cancelled=False, severity="Mild", intensity=40.0)
        b = _make_kuja("bride", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.MITIGATED
        assert result.mutual_balance == "GROOM_EXCESS"

    def test_bride_active_mild_mitigated(self):
        """Bride active (mild ≤50%), Groom none → MITIGATED."""
        g = _make_kuja("groom", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        b = _make_kuja("bride", is_present=True, is_cancelled=False, severity="Mild", intensity=40.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.MITIGATED
        assert result.mutual_balance == "BRIDE_EXCESS"

    def test_groom_severe_bride_none_no_counterpoise_not_matched(self):
        """Groom severe (>50%), Bride none, no counterpoise → NOT_MUTUALLY_MATCHED."""
        g = _make_kuja("groom", is_present=True, is_cancelled=False, severity="High", intensity=90.0)
        b = _make_kuja("bride", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        # Bride chart: no Saturn/Rahu in 7th or 8th
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert result.status == SamadoshamOutcome.NOT_MUTUALLY_MATCHED
        assert result.mutual_balance == "GROOM_EXCESS"

    def test_bride_severe_groom_none_with_counterpoise_mitigated(self):
        """Bride severe, Groom none, but Groom has Saturn in 7th → MITIGATED."""
        g_kuja = _make_kuja("groom", is_present=False, is_cancelled=False, severity="None", intensity=0.0)
        b_kuja = _make_kuja("bride", is_present=True, is_cancelled=False, severity="High", intensity=80.0)
        # Add Saturn in house 7 to groom chart
        saturn_h7 = _make_planet("Saturn", 7, 7)  # house 7 from lagna=1 → sign 7
        groom_ctx = _make_chart("groom", Gender.MALE, lagna_sign=1, moon_sign=5, venus_sign=9,
                                extra_planets={"Saturn": saturn_h7, "Mars": _make_planet("Mars", 3, 3)})
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g_kuja, b_kuja)
        assert result.status == SamadoshamOutcome.MITIGATED
        assert result.mutual_balance == "BRIDE_EXCESS"
        assert any("counterpoise" in r.lower() for r in result.cancellations_or_mitigations_applied)

    def test_no_kuja_assessments_provided_basic_detection(self):
        """When kuja assessments are None, basic Mars-house detection is used."""
        groom_ctx = self._make_clean_chart("groom", Gender.MALE)
        bride_ctx = self._make_clean_chart("bride", Gender.FEMALE)
        result = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, None, None)
        assert result.status in {s for s in SamadoshamOutcome}  # valid enum
        assert len(result.warnings) >= 2  # both kuja assessments missing


# ---------------------------------------------------------------------------
# 4. Partner-Dependent Dosha & Veto Preservation
# ---------------------------------------------------------------------------

class TestPartnerDependentDoshas:
    """Tests for veto preservation in evaluate_mutual_dosha_analysis."""

    def _make_groom_bride_clean(self):
        """Both charts: no malefics in afflicted houses, no Kuja."""
        mars = _make_planet("Mars", 3, 3)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 9, 9, extra_planets={"Mars": mars})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 9, 9, extra_planets={"Mars": mars})
        return groom_ctx, bride_ctx

    def test_rajju_fail_preserved_despite_favorable_kuja(self):
        """Rajju FAIL remains a veto even when Kuja is NEITHER_AFFLICTED."""
        groom_ctx, bride_ctx = self._make_groom_bride_clean()
        g_kuja = _make_kuja("groom", False, False, "None", 0.0)
        b_kuja = _make_kuja("bride", False, False, "None", 0.0)

        # Simulate Rajju FAIL
        from types import SimpleNamespace
        rajju_result = SimpleNamespace(status="FAIL")
        vedha_result = SimpleNamespace(status="PASS")

        result = evaluate_mutual_dosha_analysis(
            groom_ctx, bride_ctx, g_kuja, b_kuja,
            porutham_results={"rajju": rajju_result, "vedha": vedha_result},
        )
        assert "rajju" in result.independent_vetoes_preserved or \
               any("Rajju" in v for v in result.independent_vetoes_preserved)
        # Rajju veto must be in partner_dependent_doshas
        assert "rajju" in result.partner_dependent_doshas
        assert result.partner_dependent_doshas["rajju"]["is_veto"] is True

    def test_vedha_fail_preserved(self):
        """Vedha FAIL is an independent veto, not cancelled by Papasamya."""
        groom_ctx, bride_ctx = self._make_groom_bride_clean()
        from types import SimpleNamespace
        rajju_result = SimpleNamespace(status="PASS")
        vedha_result = SimpleNamespace(status="FAIL")

        result = evaluate_mutual_dosha_analysis(
            groom_ctx, bride_ctx, None, None,
            porutham_results={"rajju": rajju_result, "vedha": vedha_result},
        )
        assert "vedha" in result.partner_dependent_doshas
        assert result.partner_dependent_doshas["vedha"]["is_veto"] is True
        assert any("Vedha" in v for v in result.independent_vetoes_preserved)

    def test_rajju_pass_not_in_vetoes(self):
        """Rajju PASS does not appear in independent_vetoes_preserved."""
        groom_ctx, bride_ctx = self._make_groom_bride_clean()
        from types import SimpleNamespace
        rajju_result = SimpleNamespace(status="PASS")

        result = evaluate_mutual_dosha_analysis(
            groom_ctx, bride_ctx, None, None,
            porutham_results={"rajju": rajju_result},
        )
        # Rajju PASS → no veto triggered
        assert not any("Rajju" in v for v in result.independent_vetoes_preserved)

    def test_nadi_from_ashtakoota(self):
        """Nadi dosha (score=0) from ashtakoota results is captured."""
        groom_ctx, bride_ctx = self._make_groom_bride_clean()
        from types import SimpleNamespace
        nadi_result = SimpleNamespace(score_awarded=0, max_score=8)

        result = evaluate_mutual_dosha_analysis(
            groom_ctx, bride_ctx, None, None,
            ashtakoota_results={"nadi": nadi_result},
        )
        assert "nadi" in result.partner_dependent_doshas
        assert result.partner_dependent_doshas["nadi"]["is_dosha"] is True
        assert result.partner_dependent_doshas["nadi"]["is_veto"] is False


# ---------------------------------------------------------------------------
# 5. Full Pipeline Tests
# ---------------------------------------------------------------------------

class TestEvaluateMutualDoshaAnalysis:
    """Integration tests for evaluate_mutual_dosha_analysis."""

    def test_full_pipeline_returns_correct_type(self):
        """Full pipeline returns MutualDoshaAnalysisResult."""
        from app.services.marriage_engine.models import MutualDoshaAnalysisResult
        mars = _make_planet("Mars", 3, 3)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 9, 9, extra_planets={"Mars": mars})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 5, 9, extra_planets={"Mars": mars})
        result = evaluate_mutual_dosha_analysis(groom_ctx, bride_ctx)
        assert isinstance(result, MutualDoshaAnalysisResult)
        assert isinstance(result.samadosham.status, SamadoshamOutcome)
        assert isinstance(result.papasamya_verdict, PapasamyaVerdict)

    def test_full_pipeline_papasamya_totals_non_negative(self):
        """Papasamya totals are always ≥ 0."""
        mars = _make_planet("Mars", 3, 3)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 9, 9, extra_planets={"Mars": mars})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 5, 9, extra_planets={"Mars": mars})
        result = evaluate_mutual_dosha_analysis(groom_ctx, bride_ctx)
        assert result.groom_papasamya.total_papam >= 0.0
        assert result.bride_papasamya.total_papam >= 0.0

    def test_full_pipeline_diff_percent_non_negative(self):
        """papasamya_diff_percent is always ≥ 0."""
        mars = _make_planet("Mars", 3, 3)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 9, 9, extra_planets={"Mars": mars})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 5, 9, extra_planets={"Mars": mars})
        result = evaluate_mutual_dosha_analysis(groom_ctx, bride_ctx)
        assert result.papasamya_diff_percent >= 0.0


# ---------------------------------------------------------------------------
# 6. Determinism Tests
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Identical inputs produce identical outputs."""

    def test_papasamya_deterministic(self):
        """calculate_single_papasamya is fully deterministic."""
        mars = _make_planet("Mars", 7, 7)
        chart = _make_chart("g", Gender.MALE, 1, 5, 9, extra_planets={"Mars": mars})
        r1 = calculate_single_papasamya(chart, "groom")
        r2 = calculate_single_papasamya(chart, "groom")
        assert r1.total_papam == r2.total_papam
        assert r1.lagna_papam == r2.lagna_papam
        assert r1.moon_papam == r2.moon_papam

    def test_samadosham_deterministic(self):
        """evaluate_mutual_kuja_samadosham is fully deterministic."""
        g = _make_kuja("groom", True, False, "High", 80.0)
        b = _make_kuja("bride", True, False, "Moderate", 60.0)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 5, 9,
                                extra_planets={"Mars": _make_planet("Mars", 3, 3)})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 9, 9,
                                extra_planets={"Mars": _make_planet("Mars", 3, 3)})
        r1 = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        r2 = evaluate_mutual_kuja_samadosham(groom_ctx, bride_ctx, g, b)
        assert r1.status == r2.status
        assert r1.mutual_balance == r2.mutual_balance

    def test_full_pipeline_deterministic(self):
        """evaluate_mutual_dosha_analysis is fully deterministic."""
        mars = _make_planet("Mars", 3, 3)
        groom_ctx = _make_chart("g", Gender.MALE, 1, 9, 9, extra_planets={"Mars": mars})
        bride_ctx = _make_chart("b", Gender.FEMALE, 4, 5, 9, extra_planets={"Mars": mars})
        r1 = evaluate_mutual_dosha_analysis(groom_ctx, bride_ctx)
        r2 = evaluate_mutual_dosha_analysis(groom_ctx, bride_ctx)
        assert r1.samadosham.status == r2.samadosham.status
        assert r1.papasamya_verdict == r2.papasamya_verdict
        assert r1.groom_papasamya.total_papam == r2.groom_papasamya.total_papam


# ---------------------------------------------------------------------------
# 7. Constants and Module Integrity
# ---------------------------------------------------------------------------

class TestModuleConstants:
    """Validate Phase 5 constants are well-formed."""

    def test_papasamya_weights_sum(self):
        """Papasamya weights sum to 3.5."""
        assert sum(PAPASAMYA_WEIGHTS.values()) == pytest.approx(3.5, abs=0.01)

    def test_papasamya_houses_correct(self):
        """Papasamya afflicted houses are {1, 2, 4, 7, 8, 12}."""
        assert PAPASAMYA_HOUSES == frozenset({1, 2, 4, 7, 8, 12})

    def test_independent_veto_doshas(self):
        """Rajju and Vedha are independent vetoes."""
        assert "rajju" in INDEPENDENT_VETO_DOSHAS
        assert "vedha" in INDEPENDENT_VETO_DOSHAS

    def test_counterpoise_planets(self):
        """Saturn and Rahu are counterpoise planets."""
        assert "Saturn" in COUNTERPOISE_PLANETS
        assert "Rahu" in COUNTERPOISE_PLANETS

    def test_counterpoise_houses(self):
        """Counterpoise houses are 7th and 8th."""
        assert COUNTERPOISE_HOUSES == frozenset({7, 8})
