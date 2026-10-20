"""Phase 6: Bidirectional Vedic Horoscope Synastry Engine.

Evaluates cross-chart synastric interactions between groom and bride horoscopes:
1. Moon-to-Moon Comparison (Chandra Synastry):
   - Relative Moon sign axis (Samasaptaka, Trikona, Shadashtaka, etc.)
   - Nakshatra & Pada resonance
   - Moon sign lord natural friendship
   - Cross-chart Parashari aspects between Moons
   - Navamsa boundary sensitivity check on Moon longitudes

2. Lagna-to-Lagna Comparison (Ascendant Synastry):
   - Ascendant sign relative axis (structural & physical resonance)
   - Lagna lord identities, dignities, and natural friendship
   - Cross-chart Lagna overlay (where each partner's Lagna falls in the other's chart)
   - Cross-chart Parashari aspects between Lagna lords
   - Navamsa boundary sensitivity check on Ascendants
   - Note: Sign compatibility indicates structural harmony, not guaranteed personality concord

3. Marriage-Lord Cross-Chart Analysis (7th Lord Synastry):
   - Groom's 7th lord position, house, and dignity in Bride's chart
   - Bride's 7th lord position, house, and dignity in Groom's chart
   - Mutual relationship and cross-aspects between the two 7th lords
   - Cross-placement in key marital houses (2nd, 4th, 5th, 7th, 8th, 12th)

4. Primary Marriage Karakas (Venus & Jupiter Synastry):
   - Groom's Venus (Kalatra Karaka) placement and dignity in Bride's chart
   - Bride's Jupiter (Pati Karaka) placement and dignity in Groom's chart
   - Cross-aspects and natural tension between Venus (passion) and Jupiter (dharma)

Classical Authorities:
- Brihat Parashara Hora Shastra (BPHS), Chapters 9, 15, 18, 32
- Phaladeepika, Chapter 10 (Kalatra Bhava)
- Jataka Parijata & Muhurta Chintamani

Design Principles:
- Reuses existing validated calculations from Phase 1, Phase 4, and Phase 5.
- Does not recalculate or alter Tamil Porutham or Ashtakoota scores.
- Does not synthesize a final composite marriage verdict (reserved for Phase 7).
- Completely deterministic with full bilingual (English & Tamil) explanations.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple, Set

from app.services.marriage_engine.models import (
    MarriageChartContext,
    MarriagePlanet,
    MoonToMoonFinding,
    LagnaToLagnaFinding,
    MarriageLordCrossChartFinding,
    VenusJupiterCrossChartFinding,
    BidirectionalSynastryResult,
    DignityType,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    PLANETARY_NATURAL_FRIENDSHIP,
    PARASHARI_ASPECT_OFFSETS,
)
from app.services.marriage_engine.vedic_analysis import (
    get_planetary_dignity,
    check_navamsa_boundary_sensitivity,
)

# Marriage-related houses for cross-placement checking
MARRIAGE_HOUSES: frozenset = frozenset({2, 4, 5, 7, 8, 12})


# ---------------------------------------------------------------------------
# Internal Helper Functions
# ---------------------------------------------------------------------------

def _parashari_aspects_sign(planet_name: str, source_sign: int, target_sign: int) -> bool:
    """Check if planet in source_sign aspects target_sign under Parashari rules."""
    diff = ((target_sign - source_sign) % 12) + 1
    valid_offsets = PARASHARI_ASPECT_OFFSETS.get(planet_name, {7})
    return diff in valid_offsets


def _get_friendship_score(planet_a: str, planet_b: str) -> Tuple[str, float]:
    """Calculate natural planetary friendship between two grahas per BPHS Ch. 15.

    Returns:
        (relationship_label, friendship_score)
        Score: 1.0 for Friends/Same, 0.5 for Neutral, 0.0 for Enemies
    """
    if planet_a == planet_b:
        return "Same", 1.0

    rel_a_to_b = PLANETARY_NATURAL_FRIENDSHIP.get(planet_a, {}).get(planet_b, 0)
    rel_b_to_a = PLANETARY_NATURAL_FRIENDSHIP.get(planet_b, {}).get(planet_a, 0)

    # Composite sum: 2=Mutual Friends, 1=Friend-Neutral, 0=Mutual Neutral, -1=Friend-Enemy, -2=Mutual Enemy
    comp = rel_a_to_b + rel_b_to_a
    if comp >= 1:
        return "Friends", 1.0
    elif comp == 0:
        return "Neutrals", 0.5
    else:
        return "Enemies", 0.0


# ---------------------------------------------------------------------------
# 1. Moon-to-Moon Comparison
# ---------------------------------------------------------------------------

def evaluate_moon_to_moon_synastry(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> MoonToMoonFinding:
    """Evaluate bilateral Moon-to-Moon relationship without recalculating Porutham/Ashtakoota.

    Source: BPHS Ch. 81; Phaladeepika Ch. 10.
    """
    g_moon_sign = groom_ctx.moon_sign_idx
    b_moon_sign = bride_ctx.moon_sign_idx

    g_moon_nak = groom_ctx.moon_nakshatra_idx
    b_moon_nak = bride_ctx.moon_nakshatra_idx

    g_moon_pada = groom_ctx.moon_nakshatra_pada
    b_moon_pada = bride_ctx.moon_nakshatra_pada

    g_moon_lord = SIGN_LORDS.get(g_moon_sign, "Moon")
    b_moon_lord = SIGN_LORDS.get(b_moon_sign, "Moon")

    # Mutual sign distances
    dist_g_to_b = ((b_moon_sign - g_moon_sign) % 12) + 1
    dist_b_to_g = ((g_moon_sign - b_moon_sign) % 12) + 1

    # Classify Moon sign relationship
    if dist_g_to_b == 1:
        sign_rel = "Eka Rasi (Same Sign)"
        sign_assess = "Favorable"
    elif dist_g_to_b == 7:
        sign_rel = "Samasaptaka (Mutual 7th Axis)"
        sign_assess = "Favorable"
    elif dist_g_to_b in (5, 9):
        sign_rel = "Trikona (Trine 5/9 Axis)"
        sign_assess = "Favorable"
    elif dist_g_to_b in (3, 11):
        sign_rel = "Upachaya (Growth 3/11 Axis)"
        sign_assess = "Favorable"
    elif dist_g_to_b in (4, 10):
        sign_rel = "Kendra (Quadrature 4/10 Axis)"
        sign_assess = "Neutral"
    elif dist_g_to_b in (6, 8):
        sign_rel = "Shadashtaka (Frictional 6/8 Axis)"
        # Cancellation: same lord (Aries-Scorpio, Taurus-Libra)
        if g_moon_lord == b_moon_lord:
            sign_assess = "Neutral"
        else:
            sign_assess = "Unfavorable"
    elif dist_g_to_b in (2, 12):
        sign_rel = "Dvidwadasa (Expenditure 2/12 Axis)"
        if g_moon_lord == b_moon_lord:
            sign_assess = "Neutral"
        else:
            sign_assess = "Unfavorable"
    else:
        sign_rel = f"Relative {dist_g_to_b}th Axis"
        sign_assess = "Neutral"

    # Nakshatra relationship
    same_nak = (g_moon_nak == b_moon_nak)
    nak_dist_g_to_b = ((b_moon_nak - g_moon_nak) % 27) + 1
    nak_dist_b_to_g = ((g_moon_nak - b_moon_nak) % 27) + 1

    # Pada resonance
    if g_moon_pada == b_moon_pada:
        pada_res = "Same"
    elif abs(g_moon_pada - b_moon_pada) == 2:
        pada_res = "Complementary"
    else:
        pada_res = "Neutral"

    # Moon sign lord relationship
    lord_rel, lord_score = _get_friendship_score(g_moon_lord, b_moon_lord)

    # Cross-chart Moon aspects (Moon aspects 7th sign)
    g_aspects_b = _parashari_aspects_sign("Moon", g_moon_sign, b_moon_sign)
    b_aspects_g = _parashari_aspects_sign("Moon", b_moon_sign, g_moon_sign)

    # Navamsa boundary sensitivity
    g_bound_risk, g_bound_arcmin = check_navamsa_boundary_sensitivity(groom_ctx.moon_degree)
    b_bound_risk, b_bound_arcmin = check_navamsa_boundary_sensitivity(bride_ctx.moon_degree)

    observations: List[str] = []
    warnings: List[str] = []

    if sign_assess == "Favorable":
        observations.append(f"Moon signs form a supportive {sign_rel} relationship promoting emotional rapport.")
    elif sign_assess == "Unfavorable":
        observations.append(f"Moon signs form a challenging {sign_rel} relationship indicating potential emotional friction.")
        if g_moon_lord == b_moon_lord:
            observations.append(f"Shared Moon lord ({g_moon_lord}) mitigates sign-distance tension.")
    else:
        observations.append(f"Moon signs form a neutral {sign_rel} dynamic requiring mutual attunement.")

    if lord_score == 1.0:
        observations.append(f"Moon sign lords ({g_moon_lord} & {b_moon_lord}) share friendly disposition.")
    elif lord_score == 0.0:
        observations.append(f"Moon sign lords ({g_moon_lord} & {b_moon_lord}) are inimical, suggesting distinct instinctual temperaments.")

    if same_nak:
        observations.append(f"Both share the same birth star ({NAKSHATRA_NAMES_EN[g_moon_nak]}).")

    if g_aspects_b and b_aspects_g:
        observations.append("Mutual direct 7th aspect between Moons fosters bilateral emotional recognition.")

    if g_bound_risk:
        warnings.append(f"Groom Moon is within {g_bound_arcmin:.1f}' of Navamsa boundary — birth time accuracy is critical.")
    if b_bound_risk:
        warnings.append(f"Bride Moon is within {b_bound_arcmin:.1f}' of Navamsa boundary — birth time accuracy is critical.")

    g_sign_en = SIGN_NAMES_EN.get(g_moon_sign, "")
    b_sign_en = SIGN_NAMES_EN.get(b_moon_sign, "")
    g_sign_ta = SIGN_NAMES_TA.get(g_moon_sign, "")
    b_sign_ta = SIGN_NAMES_TA.get(b_moon_sign, "")

    en = (
        f"Groom Moon in {g_sign_en} ({NAKSHATRA_NAMES_EN[g_moon_nak]} Pada {g_moon_pada}), "
        f"Bride Moon in {b_sign_en} ({NAKSHATRA_NAMES_EN[b_moon_nak]} Pada {b_moon_pada}). "
        f"Axis: {sign_rel} ({sign_assess}). Moon Lords: {lord_rel} (score {lord_score:.1f})."
    )
    ta = (
        f"மணமகன் சந்திரன்: {g_sign_ta} ({NAKSHATRA_NAMES_TA[g_moon_nak]} பாதம் {g_moon_pada}), "
        f"மணமகள் சந்திரன்: {b_sign_ta} ({NAKSHATRA_NAMES_TA[b_moon_nak]} பாதம் {b_moon_pada}). "
        f"அச்சு: {sign_rel}. ராசி அதிபதிகள்: {lord_rel}."
    )

    return MoonToMoonFinding(
        groom_moon_sign_idx=g_moon_sign,
        groom_moon_sign_name=g_sign_en,
        groom_moon_nakshatra_idx=g_moon_nak,
        groom_moon_nakshatra_name=NAKSHATRA_NAMES_EN[g_moon_nak],
        groom_moon_nakshatra_pada=g_moon_pada,
        groom_moon_lord=g_moon_lord,
        bride_moon_sign_idx=b_moon_sign,
        bride_moon_sign_name=b_sign_en,
        bride_moon_nakshatra_idx=b_moon_nak,
        bride_moon_nakshatra_name=NAKSHATRA_NAMES_EN[b_moon_nak],
        bride_moon_nakshatra_pada=b_moon_pada,
        bride_moon_lord=b_moon_lord,
        sign_distance_g_to_b=dist_g_to_b,
        sign_distance_b_to_g=dist_b_to_g,
        sign_relationship=sign_rel,
        sign_assessment=sign_assess,
        same_nakshatra=same_nak,
        nakshatra_distance_g_to_b=nak_dist_g_to_b,
        nakshatra_distance_b_to_g=nak_dist_b_to_g,
        pada_resonance=pada_res,
        moon_lord_relationship=lord_rel,
        moon_lord_friendship_score=lord_score,
        groom_moon_aspects_bride_moon=g_aspects_b,
        bride_moon_aspects_groom_moon=b_aspects_g,
        groom_navamsa_boundary_risk=g_bound_risk,
        bride_navamsa_boundary_risk=b_bound_risk,
        groom_boundary_arcmin=g_bound_arcmin,
        bride_boundary_arcmin=b_bound_arcmin,
        observations=observations,
        explanation_en=en,
        explanation_ta=ta,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# 2. Lagna-to-Lagna Comparison
# ---------------------------------------------------------------------------

def evaluate_lagna_to_lagna_synastry(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> LagnaToLagnaFinding:
    """Evaluate bilateral Ascendant (Lagna) relationship.

    Source: BPHS Ch. 9, 15; Phaladeepika Ch. 2.
    Note: Structural resonance reflects constitutional compatibility, not personality guarantee.
    """
    g_lagna = groom_ctx.ascendant_sign_idx
    b_lagna = bride_ctx.ascendant_sign_idx

    g_lord = SIGN_LORDS.get(g_lagna, "Mars")
    b_lord = SIGN_LORDS.get(b_lagna, "Mars")

    # Lagna lord placements in natal charts
    g_lord_p = groom_ctx.grahas.get(g_lord)
    b_lord_p = bride_ctx.grahas.get(b_lord)

    g_lord_sign = g_lord_p.sign_index if g_lord_p else g_lagna
    b_lord_sign = b_lord_p.sign_index if b_lord_p else b_lagna

    g_lord_dignity = get_planetary_dignity(g_lord, g_lord_sign).value if g_lord_p else "Unknown"
    b_lord_dignity = get_planetary_dignity(b_lord, b_lord_sign).value if b_lord_p else "Unknown"

    # Mutual Lagna distances
    dist_g_to_b = ((b_lagna - g_lagna) % 12) + 1
    dist_b_to_g = ((g_lagna - b_lagna) % 12) + 1

    # Classify Lagna axis
    if dist_g_to_b == 1:
        lagna_rel = "Eka Lagna (Same Ascendant)"
        lagna_assess = "Supportive"
    elif dist_g_to_b == 7:
        lagna_rel = "Samasaptaka (Mutual 7th Axis)"
        lagna_assess = "Supportive"
    elif dist_g_to_b in (5, 9):
        lagna_rel = "Trikona (Trine 5/9 Axis)"
        lagna_assess = "Supportive"
    elif dist_g_to_b in (3, 11):
        lagna_rel = "Upachaya (Growth 3/11 Axis)"
        lagna_assess = "Supportive"
    elif dist_g_to_b in (4, 10):
        lagna_rel = "Kendra (Quadrature 4/10 Axis)"
        lagna_assess = "Neutral"
    elif dist_g_to_b in (6, 8):
        lagna_rel = "Shadashtaka (Frictional 6/8 Axis)"
        lagna_assess = "Challenging"
    elif dist_g_to_b in (2, 12):
        lagna_rel = "Dvidwadasa (Asymmetric 2/12 Axis)"
        lagna_assess = "Challenging"
    else:
        lagna_rel = f"Relative {dist_g_to_b}th Axis"
        lagna_assess = "Neutral"

    # Lagna lord natural friendship
    lord_rel, lord_score = _get_friendship_score(g_lord, b_lord)

    # Cross-chart house overlay: where does Groom's Lagna sign fall in Bride's chart?
    # Sign index relative to bride's Lagna
    g_in_b_house = ((g_lagna - b_lagna) % 12) + 1
    b_in_g_house = ((b_lagna - g_lagna) % 12) + 1

    # Cross aspects between Lagna lords
    g_lord_aspects_b_lagna = _parashari_aspects_sign(g_lord, g_lord_sign, b_lagna)
    b_lord_aspects_g_lagna = _parashari_aspects_sign(b_lord, b_lord_sign, g_lagna)

    # Boundary sensitivity on Ascendant longitudes
    g_bound_risk, g_bound_arcmin = check_navamsa_boundary_sensitivity(groom_ctx.ascendant_degree)
    b_bound_risk, b_bound_arcmin = check_navamsa_boundary_sensitivity(bride_ctx.ascendant_degree)

    observations: List[str] = []
    warnings: List[str] = []

    if lagna_assess == "Supportive":
        observations.append(f"Ascendants form a harmonious {lagna_rel} axis reflecting compatible constitutional outlooks.")
    elif lagna_assess == "Challenging":
        observations.append(f"Ascendants form a {lagna_rel} axis, indicating contrasting approaches to life and decision-making.")
    else:
        observations.append(f"Ascendants form a {lagna_rel} relationship indicating dynamic balance.")

    observations.append(f"Lagna lords ({g_lord} & {b_lord}) relate as {lord_rel} (score: {lord_score:.1f}).")
    observations.append(f"Groom Lagna overlays Bride's {g_in_b_house}th house; Bride Lagna overlays Groom's {b_in_g_house}th house.")

    if g_lord_aspects_b_lagna:
        observations.append(f"Groom's Lagna lord ({g_lord}) aspects Bride's Ascendant sign.")
    if b_lord_aspects_g_lagna:
        observations.append(f"Bride's Lagna lord ({b_lord}) aspects Groom's Ascendant sign.")

    if g_bound_risk:
        warnings.append(f"Groom Ascendant is within {g_bound_arcmin:.1f}' of Navamsa cusp — exact birth time is critical.")
    if b_bound_risk:
        warnings.append(f"Bride Ascendant is within {b_bound_arcmin:.1f}' of Navamsa cusp — exact birth time is critical.")

    g_sign_en = SIGN_NAMES_EN.get(g_lagna, "")
    b_sign_en = SIGN_NAMES_EN.get(b_lagna, "")
    g_sign_ta = SIGN_NAMES_TA.get(g_lagna, "")
    b_sign_ta = SIGN_NAMES_TA.get(b_lagna, "")

    en = (
        f"Groom Lagna: {g_sign_en} ({groom_ctx.ascendant_degree % 30.0:.2f}°, Lord {g_lord}), "
        f"Bride Lagna: {b_sign_en} ({bride_ctx.ascendant_degree % 30.0:.2f}°, Lord {b_lord}). "
        f"Axis: {lagna_rel} ({lagna_assess}). Lagna Lords: {lord_rel}."
    )
    ta = (
        f"மணமகன் லக்னம்: {g_sign_ta} (அதிபதி {g_lord}), "
        f"மணமகள் லக்னம்: {b_sign_ta} (அதிபதி {b_lord}). "
        f"அச்சு: {lagna_rel}. லக்னாதிபதிகள்: {lord_rel}."
    )

    return LagnaToLagnaFinding(
        groom_lagna_sign_idx=g_lagna,
        groom_lagna_sign_name=g_sign_en,
        groom_lagna_degree=groom_ctx.ascendant_degree,
        groom_lagna_lord=g_lord,
        groom_lagna_lord_sign_idx=g_lord_sign,
        groom_lagna_lord_dignity=g_lord_dignity,
        bride_lagna_sign_idx=b_lagna,
        bride_lagna_sign_name=b_sign_en,
        bride_lagna_degree=bride_ctx.ascendant_degree,
        bride_lagna_lord=b_lord,
        bride_lagna_lord_sign_idx=b_lord_sign,
        bride_lagna_lord_dignity=b_lord_dignity,
        lagna_sign_distance_g_to_b=dist_g_to_b,
        lagna_sign_distance_b_to_g=dist_b_to_g,
        lagna_relationship=lagna_rel,
        lagna_sign_assessment=lagna_assess,
        lagna_lord_relationship=lord_rel,
        lagna_lord_friendship_score=lord_score,
        groom_lagna_in_bride_chart_house=g_in_b_house,
        bride_lagna_in_groom_chart_house=b_in_g_house,
        groom_lord_aspects_bride_lagna=g_lord_aspects_b_lagna,
        bride_lord_aspects_groom_lagna=b_lord_aspects_g_lagna,
        groom_lagna_boundary_risk=g_bound_risk,
        bride_lagna_boundary_risk=b_bound_risk,
        groom_lagna_boundary_arcmin=g_bound_arcmin,
        bride_lagna_boundary_arcmin=b_bound_arcmin,
        observations=observations,
        explanation_en=en,
        explanation_ta=ta,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# 3. Marriage-Lord Cross-Chart Analysis (7th Lords)
# ---------------------------------------------------------------------------

def evaluate_marriage_lord_cross_synastry(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> MarriageLordCrossChartFinding:
    """Evaluate cross-chart placements and interactions of 7th house lords.

    Source: BPHS Ch. 18 (Kalatra Bhava); Phaladeepika Ch. 10.
    """
    g_7th_sign = ((groom_ctx.ascendant_sign_idx + 5) % 12) + 1
    b_7th_sign = ((bride_ctx.ascendant_sign_idx + 5) % 12) + 1

    g_7th_lord = SIGN_LORDS.get(g_7th_sign, "Venus")
    b_7th_lord = SIGN_LORDS.get(b_7th_sign, "Jupiter")

    g_7th_planet = groom_ctx.grahas.get(g_7th_lord)
    b_7th_planet = bride_ctx.grahas.get(b_7th_lord)

    g_7th_lord_sign = g_7th_planet.sign_index if g_7th_planet else g_7th_sign
    b_7th_lord_sign = b_7th_planet.sign_index if b_7th_planet else b_7th_sign

    # Groom's 7th lord position in Bride's chart
    # House from bride's Lagna
    g_in_b_house = ((g_7th_lord_sign - bride_ctx.ascendant_sign_idx) % 12) + 1
    g_in_b_dignity = get_planetary_dignity(g_7th_lord, g_7th_lord_sign).value
    g_aspects_b_7th = _parashari_aspects_sign(g_7th_lord, g_7th_lord_sign, b_7th_sign)
    g_in_b_marr_house = (g_in_b_house in MARRIAGE_HOUSES)

    # Bride's 7th lord position in Groom's chart
    b_in_g_house = ((b_7th_lord_sign - groom_ctx.ascendant_sign_idx) % 12) + 1
    b_in_g_dignity = get_planetary_dignity(b_7th_lord, b_7th_lord_sign).value
    b_aspects_g_7th = _parashari_aspects_sign(b_7th_lord, b_7th_lord_sign, g_7th_sign)
    b_in_g_marr_house = (b_in_g_house in MARRIAGE_HOUSES)

    # Mutual relationship between 7th lords
    lord_rel, lord_score = _get_friendship_score(g_7th_lord, b_7th_lord)

    # Mutual aspects between 7th lords
    mutual_aspect = (
        _parashari_aspects_sign(g_7th_lord, g_7th_lord_sign, b_7th_lord_sign)
        or _parashari_aspects_sign(b_7th_lord, b_7th_lord_sign, g_7th_lord_sign)
    )

    observations: List[str] = []
    warnings: List[str] = []

    observations.append(
        f"Groom's 7th Lord ({g_7th_lord}) occupies Bride's {g_in_b_house}th house ({g_in_b_dignity})."
    )
    if g_in_b_marr_house:
        observations.append(f"Groom's 7th lord activates a key marriage house ({g_in_b_house}th) in Bride's chart.")
    if g_aspects_b_7th:
        observations.append(f"Groom's 7th lord aspects Bride's 7th house ({SIGN_NAMES_EN[b_7th_sign]}).")

    observations.append(
        f"Bride's 7th Lord ({b_7th_lord}) occupies Groom's {b_in_g_house}th house ({b_in_g_dignity})."
    )
    if b_in_g_marr_house:
        observations.append(f"Bride's 7th lord activates a key marriage house ({b_in_g_house}th) in Groom's chart.")
    if b_aspects_g_7th:
        observations.append(f"Bride's 7th lord aspects Groom's 7th house ({SIGN_NAMES_EN[g_7th_sign]}).")

    observations.append(f"7th House lords ({g_7th_lord} & {b_7th_lord}) are naturally {lord_rel}.")
    if mutual_aspect:
        observations.append("Cross-chart Parashari aspect connects both 7th lords directly.")

    en = (
        f"Groom 7th Lord ({g_7th_lord}) in Bride's {g_in_b_house}th house ({g_in_b_dignity}); "
        f"Bride 7th Lord ({b_7th_lord}) in Groom's {b_in_g_house}th house ({b_in_g_dignity}). "
        f"7th Lords Relationship: {lord_rel} (score: {lord_score:.1f})."
    )
    ta = (
        f"மணமகன் 7-ஆம் அதிபதி ({g_7th_lord}) மணமகளின் {g_in_b_house}-ஆம் பாவத்தில்; "
        f"மணமகள் 7-ஆம் அதிபதி ({b_7th_lord}) மணமகனின் {b_in_g_house}-ஆம் பாவத்தில். "
        f"7-ஆம் அதிபதிகள் தொடர்பு: {lord_rel}."
    )

    return MarriageLordCrossChartFinding(
        groom_7th_lord=g_7th_lord,
        groom_7th_lord_sign_idx=g_7th_lord_sign,
        groom_7th_lord_in_bride_house=g_in_b_house,
        groom_7th_lord_in_bride_dignity=g_in_b_dignity,
        groom_7th_lord_aspects_bride_7th=g_aspects_b_7th,
        groom_7th_lord_in_bride_marriage_house=g_in_b_marr_house,
        bride_7th_lord=b_7th_lord,
        bride_7th_lord_sign_idx=b_7th_lord_sign,
        bride_7th_lord_in_groom_house=b_in_g_house,
        bride_7th_lord_in_groom_dignity=b_in_g_dignity,
        bride_7th_lord_aspects_groom_7th=b_aspects_g_7th,
        bride_7th_lord_in_groom_marriage_house=b_in_g_marr_house,
        seventh_lord_mutual_relationship=lord_rel,
        seventh_lord_friendship_score=lord_score,
        mutual_aspect_between_7th_lords=mutual_aspect,
        observations=observations,
        explanation_en=en,
        explanation_ta=ta,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# 4. Venus & Jupiter Cross-Chart Analysis (Natural Marriage Karakas)
# ---------------------------------------------------------------------------

def evaluate_venus_jupiter_cross_synastry(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> VenusJupiterCrossChartFinding:
    """Evaluate cross-chart placements of natural marriage significators: Venus & Jupiter.

    For Groom: Venus is primary Kalatra Karaka (wife/marriage significator).
    For Bride: Jupiter is primary Pati Karaka (husband/dharma significator).

    Source: BPHS Ch. 32; Phaladeepika Ch. 10.
    """
    g_venus = groom_ctx.grahas.get("Venus")
    b_jupiter = bride_ctx.grahas.get("Jupiter")

    g_venus_sign = g_venus.sign_index if g_venus else 1
    b_jupiter_sign = b_jupiter.sign_index if b_jupiter else 1

    b_7th_sign = ((bride_ctx.ascendant_sign_idx + 5) % 12) + 1
    g_7th_sign = ((groom_ctx.ascendant_sign_idx + 5) % 12) + 1

    # Groom Venus in Bride's chart
    g_venus_in_b_house = ((g_venus_sign - bride_ctx.ascendant_sign_idx) % 12) + 1
    g_venus_in_b_dignity = get_planetary_dignity("Venus", g_venus_sign).value
    g_venus_aspects_b_7th = _parashari_aspects_sign("Venus", g_venus_sign, b_7th_sign)
    g_venus_in_b_marr_house = (g_venus_in_b_house in MARRIAGE_HOUSES)

    # Bride Jupiter in Groom's chart
    b_jup_in_g_house = ((b_jupiter_sign - groom_ctx.ascendant_sign_idx) % 12) + 1
    b_jup_in_g_dignity = get_planetary_dignity("Jupiter", b_jupiter_sign).value
    b_jup_aspects_g_7th = _parashari_aspects_sign("Jupiter", b_jupiter_sign, g_7th_sign)
    b_jup_in_g_marr_house = (b_jup_in_g_house in MARRIAGE_HOUSES)

    # Cross Karaka natural relationship: Venus considers Jupiter neutral, Jupiter considers Venus enemy
    # Overall natural relationship classified as "Enemies" per BPHS Ch. 15 matrix
    rel, score = _get_friendship_score("Venus", "Jupiter")

    # Cross aspects between Groom Venus and Bride Jupiter
    g_venus_aspects_b_jup = _parashari_aspects_sign("Venus", g_venus_sign, b_jupiter_sign)
    b_jup_aspects_g_venus = _parashari_aspects_sign("Jupiter", b_jupiter_sign, g_venus_sign)

    observations: List[str] = []
    warnings: List[str] = []

    observations.append(
        f"Groom's Venus ({SIGN_NAMES_EN.get(g_venus_sign, '')}) falls in Bride's {g_venus_in_b_house}th house ({g_venus_in_b_dignity})."
    )
    if g_venus_in_b_marr_house:
        observations.append(f"Groom's Venus occupies an auspicious marriage house ({g_venus_in_b_house}th) in Bride's chart.")
    if g_venus_aspects_b_7th:
        observations.append("Groom's Venus directly aspects Bride's 7th house cusp.")

    observations.append(
        f"Bride's Jupiter ({SIGN_NAMES_EN.get(b_jupiter_sign, '')}) falls in Groom's {b_jup_in_g_house}th house ({b_jup_in_g_dignity})."
    )
    if b_jup_in_g_marr_house:
        observations.append(f"Bride's Jupiter occupies an auspicious marriage house ({b_jup_in_g_house}th) in Groom's chart.")
    if b_jup_aspects_g_7th:
        observations.append("Bride's Jupiter directly aspects Groom's 7th house cusp.")

    if g_venus_aspects_b_jup or b_jup_aspects_g_venus:
        observations.append("Cross-aspect between Groom Venus and Bride Jupiter unites romantic desire with dharmic growth.")

    en = (
        f"Groom Venus in Bride's {g_venus_in_b_house}th house ({g_venus_in_b_dignity}); "
        f"Bride Jupiter in Groom's {b_jup_in_g_house}th house ({b_jup_in_g_dignity}). "
        f"Karaka Cross-Resonance: Venus-Jupiter {rel}."
    )
    ta = (
        f"மணமகன் சுக்கிரன் மணமகளின் {g_venus_in_b_house}-ஆம் பாவத்தில் ({g_venus_in_b_dignity}); "
        f"மணமகள் குரு மணமகனின் {b_jup_in_g_house}-ஆம் பாவத்தில் ({b_jup_in_g_dignity})."
    )

    return VenusJupiterCrossChartFinding(
        groom_venus_sign_idx=g_venus_sign,
        groom_venus_sign_name=SIGN_NAMES_EN.get(g_venus_sign, ""),
        groom_venus_in_bride_house=g_venus_in_b_house,
        groom_venus_in_bride_dignity=g_venus_in_b_dignity,
        groom_venus_aspects_bride_7th=g_venus_aspects_b_7th,
        groom_venus_in_bride_marriage_house=g_venus_in_b_marr_house,
        bride_jupiter_sign_idx=b_jupiter_sign,
        bride_jupiter_sign_name=SIGN_NAMES_EN.get(b_jupiter_sign, ""),
        bride_jupiter_in_groom_house=b_jup_in_g_house,
        bride_jupiter_in_groom_dignity=b_jup_in_g_dignity,
        bride_jupiter_aspects_groom_7th=b_jup_aspects_g_7th,
        bride_jupiter_in_groom_marriage_house=b_jup_in_g_marr_house,
        venus_jupiter_relationship=rel,
        venus_jupiter_friendship_score=score,
        groom_venus_aspects_bride_jupiter=g_venus_aspects_b_jup,
        bride_jupiter_aspects_groom_venus=b_jup_aspects_g_venus,
        observations=observations,
        explanation_en=en,
        explanation_ta=ta,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# 5. Top-Level Bidirectional Synastry Entry Point
# ---------------------------------------------------------------------------

def evaluate_bidirectional_synastry(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> BidirectionalSynastryResult:
    """Execute complete Phase 6 bidirectional Vedic synastry analysis.

    Evaluates:
    - Moon-to-Moon (Chandra) synastry
    - Lagna-to-Lagna (Ascendant) synastry
    - 7th Lord cross-chart placements and mutual aspects
    - Venus & Jupiter cross-chart Karaka overlays
    - Aggregates indicators and boundary sensitivity

    DOES NOT synthesize a final composite compatibility verdict (Phase 7).

    Args:
        groom_ctx: Validated groom MarriageChartContext.
        bride_ctx: Validated bride MarriageChartContext.

    Returns:
        BidirectionalSynastryResult with full multidimensional breakdown.
    """
    moon_finding = evaluate_moon_to_moon_synastry(groom_ctx, bride_ctx)
    lagna_finding = evaluate_lagna_to_lagna_synastry(groom_ctx, bride_ctx)
    marriage_lord_finding = evaluate_marriage_lord_cross_synastry(groom_ctx, bride_ctx)
    venus_jupiter_finding = evaluate_venus_jupiter_cross_synastry(groom_ctx, bride_ctx)

    strong_ind: List[str] = []
    mixed_ind: List[str] = []
    weak_ind: List[str] = []

    # Moon synthesis
    if moon_finding.sign_assessment == "Favorable":
        strong_ind.append(f"Supportive Moon axis: {moon_finding.sign_relationship}.")
    elif moon_finding.sign_assessment == "Unfavorable":
        weak_ind.append(f"Challenging Moon axis: {moon_finding.sign_relationship}.")
    else:
        mixed_ind.append(f"Neutral Moon axis: {moon_finding.sign_relationship}.")

    if moon_finding.moon_lord_friendship_score == 1.0:
        strong_ind.append(f"Harmonious Moon lords: {moon_finding.groom_moon_lord} & {moon_finding.bride_moon_lord}.")
    elif moon_finding.moon_lord_friendship_score == 0.0:
        weak_ind.append(f"Inimical Moon lords: {moon_finding.groom_moon_lord} & {moon_finding.bride_moon_lord}.")

    # Lagna synthesis
    if lagna_finding.lagna_sign_assessment == "Supportive":
        strong_ind.append(f"Harmonious Ascendant axis: {lagna_finding.lagna_relationship}.")
    elif lagna_finding.lagna_sign_assessment == "Challenging":
        weak_ind.append(f"Challenging Ascendant axis: {lagna_finding.lagna_relationship}.")
    else:
        mixed_ind.append(f"Dynamic Ascendant axis: {lagna_finding.lagna_relationship}.")

    if lagna_finding.lagna_lord_friendship_score == 1.0:
        strong_ind.append(f"Friendly Lagna lords: {lagna_finding.groom_lagna_lord} & {lagna_finding.bride_lagna_lord}.")
    elif lagna_finding.lagna_lord_friendship_score == 0.0:
        weak_ind.append(f"Inimical Lagna lords: {lagna_finding.groom_lagna_lord} & {lagna_finding.bride_lagna_lord}.")

    # 7th Lord synthesis
    if marriage_lord_finding.groom_7th_lord_in_bride_marriage_house:
        strong_ind.append(f"Groom's 7th lord activates Bride's marriage house ({marriage_lord_finding.groom_7th_lord_in_bride_house}th).")
    if marriage_lord_finding.bride_7th_lord_in_groom_marriage_house:
        strong_ind.append(f"Bride's 7th lord activates Groom's marriage house ({marriage_lord_finding.bride_7th_lord_in_groom_house}th).")

    if marriage_lord_finding.mutual_aspect_between_7th_lords:
        strong_ind.append("Direct cross-aspect connects both 7th house lords.")

    # Karaka synthesis
    if venus_jupiter_finding.groom_venus_in_bride_marriage_house:
        strong_ind.append("Groom's Venus connects to Bride's marriage houses.")
    if venus_jupiter_finding.bride_jupiter_in_groom_marriage_house:
        strong_ind.append("Bride's Jupiter connects to Groom's marriage houses.")

    # Boundary sensitivities
    has_boundary = (
        moon_finding.groom_navamsa_boundary_risk
        or moon_finding.bride_navamsa_boundary_risk
        or lagna_finding.groom_lagna_boundary_risk
        or lagna_finding.bride_lagna_boundary_risk
    )
    boundary_notes: List[str] = []
    if moon_finding.groom_navamsa_boundary_risk:
        boundary_notes.append(f"Groom Moon within {moon_finding.groom_boundary_arcmin:.1f}' of Navamsa boundary.")
    if moon_finding.bride_navamsa_boundary_risk:
        boundary_notes.append(f"Bride Moon within {moon_finding.bride_boundary_arcmin:.1f}' of Navamsa boundary.")
    if lagna_finding.groom_lagna_boundary_risk:
        boundary_notes.append(f"Groom Ascendant within {lagna_finding.groom_lagna_boundary_arcmin:.1f}' of Navamsa boundary.")
    if lagna_finding.bride_lagna_boundary_risk:
        boundary_notes.append(f"Bride Ascendant within {lagna_finding.bride_lagna_boundary_arcmin:.1f}' of Navamsa boundary.")

    rule_sources = [
        "BPHS Ch. 9 (Lagna & Rasi)",
        "BPHS Ch. 15 (Naisargika Sambandha)",
        "BPHS Ch. 18 (Kalatra Bhava)",
        "BPHS Ch. 32 (Karakatwa)",
        "Phaladeepika Ch. 10 (Kalatra Bhava Phala)",
        "Muhurta Chintamani Ch. 6 (Vivaha Prakarana)",
    ]

    all_warnings = (
        moon_finding.warnings
        + lagna_finding.warnings
        + marriage_lord_finding.warnings
        + venus_jupiter_finding.warnings
    )

    return BidirectionalSynastryResult(
        groom_person_id=groom_ctx.person_id,
        bride_person_id=bride_ctx.person_id,
        moon_to_moon=moon_finding,
        lagna_to_lagna=lagna_finding,
        marriage_lord_cross=marriage_lord_finding,
        venus_jupiter_cross=venus_jupiter_finding,
        strong_indicators=strong_ind,
        mixed_indicators=mixed_ind,
        weak_indicators=weak_ind,
        has_boundary_sensitivity=has_boundary,
        boundary_sensitivity_notes=boundary_notes,
        rule_sources=rule_sources,
        analysis_warnings=all_warnings,
    )
