"""Phase 5: Mutual Dosha Analysis — Kuja Samadosham & South Indian Papasamya.

Implements bidirectional mutual Dosha analysis:
1. Kuja Samadosham (mutual Manglik balancing):
   - Compares individual Kuja severity between groom and bride.
   - Outcomes: MUTUALLY_MATCHED, CANCELLED_BY_RULE, MITIGATED, NOT_MUTUALLY_MATCHED,
     INDETERMINATE, UNSUPPORTED.
   - Sources: Muhurta Chintamani Ch. 6, Kalaprakasika Ch. 12,
     BPHS Ch. 81 (mutual balancing commentary).

2. South Indian Papasamya (malefic point balancing):
   - Malefics: Mars 1.0, Saturn 1.0, Rahu 0.5, Ketu 0.5, Sun 0.5.
   - Reference frames: Lagna, Moon, Venus.
   - Afflicted houses per frame: 1, 2, 4, 7, 8, 12.
   - Verdicts: FAVORABLE, TOLERABLE, UNFAVORABLE, INDETERMINATE.
   - Sources: Kalaprakasika Ch. 12, Jathaka Alankaram (South Indian tradition).

3. Partner-dependent Dosha cross-reference:
   - Nadi, Bhakoot, Gana, Yoni, Rajju, Vedha doshas from Tamil/Ashtakoota layers.
   - Rajju Thatu and Vedha are independent vetoes; they are NEVER cancelled by
     favorable Kuja or Papasamya outcomes.

Design constraints:
- No duplication of Porutham or Ashtakoota logic.
- No synthetic composite verdict (reserved for Phase 6).
- Fully deterministic; identical inputs always produce identical outputs.
- Bilingual explanations in English and Tamil.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.services.marriage_engine.models import (
    MarriageChartContext,
    IndividualKujaAssessment,
    MutualKujaResult,
    MutualDoshaAnalysisResult,
    PapasamyaResult,
    PapasamyaVerdict,
    PoruthamStatus,
    SamadoshamOutcome,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


# ---------------------------------------------------------------------------
# Papasamya Constants
# ---------------------------------------------------------------------------

# Malefic weights for Papasamya calculation
# Source: Kalaprakasika Ch. 12, Jathaka Alankaram
PAPASAMYA_WEIGHTS: Dict[str, float] = {
    "Mars":   1.0,
    "Saturn": 1.0,
    "Rahu":   0.5,
    "Ketu":   0.5,
    "Sun":    0.5,
}

# Houses (from reference planet/lagna) that constitute Papasamya positions
# Source: Kalaprakasika Ch. 12 — houses 1, 2, 4, 7, 8, 12
PAPASAMYA_HOUSES: frozenset = frozenset({1, 2, 4, 7, 8, 12})

# Reference frames for Papasamya calculation
PAPASAMYA_REFERENCE_PLANETS: List[str] = ["Lagna", "Moon", "Venus"]


# ---------------------------------------------------------------------------
# Kuja Samadosham Intensity Thresholds
# ---------------------------------------------------------------------------

# Delta threshold for "balanced" mutual match (both have comparable intensity)
SAMADOSHAM_BALANCE_DELTA_PERCENT: float = 25.0

# Threshold below which one-sided Kuja is considered "mild" — eligible for MITIGATED
SAMADOSHAM_MILD_THRESHOLD_PERCENT: float = 50.0

# Counterpoise: Saturn or Rahu in 7th or 8th house from Lagna counts as partial mitigation
COUNTERPOISE_PLANETS: frozenset = frozenset({"Saturn", "Rahu"})
COUNTERPOISE_HOUSES: frozenset = frozenset({7, 8})


# ---------------------------------------------------------------------------
# Individual Papasamya Calculation
# ---------------------------------------------------------------------------

def calculate_single_papasamya(ctx: MarriageChartContext, role: str) -> PapasamyaResult:
    """Calculate South Indian Papasamya malefic load for one person.

    Evaluates the five classical malefics (Mars, Saturn, Rahu, Ketu, Sun)
    across three reference frames (Lagna, Moon, Venus) in six afflicted houses
    (1, 2, 4, 7, 8, 12) and accumulates weighted malefic points.

    Args:
        ctx: Validated MarriageChartContext for the individual.
        role: 'groom' or 'bride' — used for labelling only.

    Returns:
        PapasamyaResult with per-frame, per-planet breakdown and totals.

    Source: Kalaprakasika Ch. 12; Jathaka Alankaram (South Indian tradition).
    """
    breakdown_by_planet: Dict[str, float] = {p: 0.0 for p in PAPASAMYA_WEIGHTS}
    placements_detail: List[Dict[str, Any]] = []

    lagna_papam: float = 0.0
    moon_papam: float = 0.0
    venus_papam: float = 0.0

    # --- Reference sign indices ---
    lagna_sign = ctx.ascendant_sign_idx  # 1 to 12
    moon_planet = ctx.grahas.get("Moon")
    moon_sign = moon_planet.sign_index if moon_planet else None
    venus_planet = ctx.grahas.get("Venus")
    venus_sign = venus_planet.sign_index if venus_planet else None

    for malefic_name, weight in PAPASAMYA_WEIGHTS.items():
        malefic = ctx.grahas.get(malefic_name)
        if not malefic:
            continue
        malefic_sign = malefic.sign_index

        # Compute house from each reference frame
        def house_from(reference_sign: int) -> int:
            return ((malefic_sign - reference_sign) % 12) + 1

        # --- Lagna frame ---
        lagna_house = house_from(lagna_sign)
        in_lagna_frame = lagna_house in PAPASAMYA_HOUSES
        if in_lagna_frame:
            lagna_papam += weight
            breakdown_by_planet[malefic_name] += weight
            placements_detail.append({
                "frame": "Lagna",
                "planet": malefic_name,
                "malefic_sign": malefic_sign,
                "malefic_sign_en": SIGN_NAMES_EN.get(malefic_sign, ""),
                "house_from_lagna": lagna_house,
                "weight": weight,
            })

        # --- Moon frame ---
        if moon_sign is not None:
            moon_house = house_from(moon_sign)
            in_moon_frame = moon_house in PAPASAMYA_HOUSES
            if in_moon_frame:
                moon_papam += weight
                breakdown_by_planet[malefic_name] += weight
                placements_detail.append({
                    "frame": "Moon",
                    "planet": malefic_name,
                    "malefic_sign": malefic_sign,
                    "malefic_sign_en": SIGN_NAMES_EN.get(malefic_sign, ""),
                    "house_from_moon": house_from(moon_sign),
                    "weight": weight,
                })

        # --- Venus frame ---
        if venus_sign is not None:
            venus_house = house_from(venus_sign)
            in_venus_frame = venus_house in PAPASAMYA_HOUSES
            if in_venus_frame:
                venus_papam += weight
                breakdown_by_planet[malefic_name] += weight
                placements_detail.append({
                    "frame": "Venus",
                    "planet": malefic_name,
                    "malefic_sign": malefic_sign,
                    "malefic_sign_en": SIGN_NAMES_EN.get(malefic_sign, ""),
                    "house_from_venus": house_from(venus_sign),
                    "weight": weight,
                })

    total_papam = lagna_papam + moon_papam + venus_papam

    # Build bilingual explanation
    planet_summary = "; ".join(
        f"{p}: {v:.1f} pts" for p, v in breakdown_by_planet.items() if v > 0
    ) or "No malefic afflictions found"
    explanation_en = (
        f"{role.capitalize()} Papasamya — "
        f"Lagna frame: {lagna_papam:.1f}, Moon frame: {moon_papam:.1f}, "
        f"Venus frame: {venus_papam:.1f}. Total: {total_papam:.1f} pts. "
        f"Breakdown: {planet_summary}."
    )
    if moon_sign is None:
        explanation_en += " Warning: Moon position unavailable; Moon-frame skipped."
    if venus_sign is None:
        explanation_en += " Warning: Venus position unavailable; Venus-frame skipped."

    explanation_ta = (
        f"{role} பாபசமயம் — "
        f"லக்னம்: {lagna_papam:.1f}, சந்திரன்: {moon_papam:.1f}, "
        f"சுக்கிரன்: {venus_papam:.1f}. மொத்தம்: {total_papam:.1f}."
    )

    return PapasamyaResult(
        subject_role=role,
        lagna_papam=lagna_papam,
        moon_papam=moon_papam,
        venus_papam=venus_papam,
        total_papam=total_papam,
        breakdown_by_planet=breakdown_by_planet,
        placements_detail=placements_detail,
        explanation_en=explanation_en,
        explanation_ta=explanation_ta,
    )


# ---------------------------------------------------------------------------
# Mutual Papasamya Comparison
# ---------------------------------------------------------------------------

def evaluate_mutual_papasamya(
    groom_p: PapasamyaResult,
    bride_p: PapasamyaResult,
) -> Tuple[PapasamyaVerdict, float, str, str]:
    """Compare groom and bride Papasamya loads to determine mutual compatibility.

    Rules (Kalaprakasika Ch. 12, South Indian tradition):
    - FAVORABLE:   Groom >= Bride AND diff <= 25% of max(groom, bride),
                   OR absolute diff <= 0.5 pts (effectively equal).
    - TOLERABLE:   Groom > Bride AND diff > 25% but <= 50% of max(groom, bride).
    - UNFAVORABLE: Bride > Groom AND diff > 25% of max(groom, bride) AND diff >= 0.5 pts.
                   (Classical: bride carrying higher malefic load is strictly forbidden.)
    - INDETERMINATE: Both totals are 0.0 (no malefics in afflicted positions).

    Args:
        groom_p: PapasamyaResult for groom.
        bride_p: PapasamyaResult for bride.

    Returns:
        (verdict, diff_percent, explanation_en, explanation_ta)
    """
    G = groom_p.total_papam
    B = bride_p.total_papam
    diff = G - B  # positive = groom excess; negative = bride excess
    abs_diff = abs(diff)
    denom = max(G, B, 0.001)  # avoid zero division
    diff_percent = (abs_diff / denom) * 100.0

    # Both zero — fully clean charts
    if G == 0.0 and B == 0.0:
        verdict = PapasamyaVerdict.INDETERMINATE
        en = (
            "Both partners have zero Papasamya. No malefic planets occupy "
            "the classical afflicted houses (1, 2, 4, 7, 8, 12) from Lagna, Moon, or Venus. "
            "Verdict: INDETERMINATE (no data to compare)."
        )
        ta = "இருவருக்கும் பாபசமயம் இல்லை. ஒப்பிட தரவு இல்லை."
        return verdict, diff_percent, en, ta

    # Effectively equal (absolute diff <= 0.5 pts regardless of direction)
    if abs_diff <= 0.5:
        verdict = PapasamyaVerdict.FAVORABLE
        en = (
            f"Papasamya nearly equal (Groom: {G:.1f}, Bride: {B:.1f}, "
            f"diff: {abs_diff:.1f} pts ≤ 0.5 threshold). "
            "Verdict: FAVORABLE — balanced malefic loads."
        )
        ta = (
            f"பாபசமயம் சமம் (மணமகன்: {G:.1f}, மணமகள்: {B:.1f}). "
            "தீர்ப்பு: சாதகமான சமனிலை."
        )
        return verdict, diff_percent, en, ta

    if diff >= 0:
        # Groom >= Bride
        if diff_percent <= 25.0:
            verdict = PapasamyaVerdict.FAVORABLE
            en = (
                f"Groom Papasamya ({G:.1f}) ≥ Bride ({B:.1f}), "
                f"excess {diff_percent:.1f}% ≤ 25% threshold. "
                "Verdict: FAVORABLE — classical tradition accepts groom carrying same or higher malefic load."
            )
            ta = (
                f"மணமகன் பாபம் ({G:.1f}) ≥ மணமகள் ({B:.1f}), "
                f"அதிகம் {diff_percent:.1f}%. தீர்ப்பு: சாதகம்."
            )
        elif diff_percent <= 50.0:
            verdict = PapasamyaVerdict.TOLERABLE
            en = (
                f"Groom Papasamya ({G:.1f}) exceeds Bride ({B:.1f}) "
                f"by {diff_percent:.1f}% (25–50% range). "
                "Verdict: TOLERABLE — groom's higher malefic load is traditionally accepted within this range."
            )
            ta = (
                f"மணமகன் பாபம் ({G:.1f}) மணமகளை விட {diff_percent:.1f}% அதிகம். "
                "தீர்ப்பு: சகிப்பு நிலை."
            )
        else:
            verdict = PapasamyaVerdict.TOLERABLE
            en = (
                f"Groom Papasamya ({G:.1f}) significantly exceeds Bride ({B:.1f}) "
                f"by {diff_percent:.1f}% (>50%). "
                "Verdict: TOLERABLE — groom excess is traditionally acceptable, "
                "but the magnitude warrants attention."
            )
            ta = (
                f"மணமகன் பாபம் ({G:.1f}) மணமகளை விட {diff_percent:.1f}% அதிகம் (>50%). "
                "தீர்ப்பு: சகிப்பு நிலை, கவனம் தேவை."
            )
    else:
        # Bride > Groom
        if diff_percent > 25.0 and abs_diff >= 0.5:
            verdict = PapasamyaVerdict.UNFAVORABLE
            en = (
                f"Bride Papasamya ({B:.1f}) exceeds Groom ({G:.1f}) "
                f"by {diff_percent:.1f}% and {abs_diff:.1f} pts. "
                "Verdict: UNFAVORABLE — classical South Indian tradition strictly forbids "
                "the bride carrying a higher malefic load than the groom."
            )
            ta = (
                f"மணமகள் பாபம் ({B:.1f}) மணமகனை விட {diff_percent:.1f}% அதிகம். "
                "தீர்ப்பு: சாதகமற்றது — பாரம்பரிய தெற்கிந்திய மரபு இதை தடை செய்கிறது."
            )
        else:
            verdict = PapasamyaVerdict.FAVORABLE
            en = (
                f"Bride Papasamya ({B:.1f}) marginally exceeds Groom ({G:.1f}) "
                f"by {diff_percent:.1f}% (below 25% threshold or diff < 0.5 pts). "
                "Verdict: FAVORABLE — within classical tolerance."
            )
            ta = (
                f"மணமகள் பாபம் ({B:.1f}) சிறிதளவு அதிகம் ({diff_percent:.1f}%). "
                "தீர்ப்பு: சாதகம் — வரம்புக்குள் உள்ளது."
            )

    return verdict, diff_percent, en, ta


# ---------------------------------------------------------------------------
# Mutual Kuja Samadosham Evaluation
# ---------------------------------------------------------------------------

def _has_counterpoise(ctx: MarriageChartContext) -> bool:
    """Check if chart has Saturn or Rahu in the 7th or 8th house from Lagna.

    Classical counterpoise (Kalaprakasika Ch. 12): the presence of Saturn or Rahu
    in the 7th or 8th house from Lagna partially offsets an unmatched Kuja in the
    partner's chart, qualifying the outcome for MITIGATED rather than NOT_MUTUALLY_MATCHED.
    """
    for planet_name in COUNTERPOISE_PLANETS:
        planet = ctx.grahas.get(planet_name)
        if planet and planet.house in COUNTERPOISE_HOUSES:
            return True
    return False


def evaluate_mutual_kuja_samadosham(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
    groom_kuja: Optional[IndividualKujaAssessment] = None,
    bride_kuja: Optional[IndividualKujaAssessment] = None,
) -> MutualKujaResult:
    """Evaluate mutual Kuja Dosha (Samadosham) between groom and bride.

    Rules (Muhurta Chintamani Ch. 6; Kalaprakasika Ch. 12):
    1. NEITHER_AFFLICTED → MUTUALLY_MATCHED: Neither partner has Kuja Dosha.
    2. BOTH_CANCELLED → CANCELLED_BY_RULE: Both have Kuja but both are cancelled
       by individual classical cancellation rules.
    3. BALANCED (both active) → MUTUALLY_MATCHED: Both have active Kuja with
       comparable intensity (Δ ≤ 25% or same reference house triggered).
    4. MITIGATED: One partner has active Kuja; the other lacks Kuja but has
       Saturn/Rahu counterpoise in 7th/8th, OR has mild Kuja (≤ 50%).
    5. NOT_MUTUALLY_MATCHED: One partner has severe active Kuja, the other has
       zero Kuja and no counterpoise — a gross disparity.
    6. INDETERMINATE: Missing or incomplete chart data.

    Args:
        groom_ctx: Validated groom MarriageChartContext.
        bride_ctx: Validated bride MarriageChartContext.
        groom_kuja: Optional pre-computed IndividualKujaAssessment for groom.
        bride_kuja: Optional pre-computed IndividualKujaAssessment for bride.

    Returns:
        MutualKujaResult with outcome, balance label, severity labels,
        intensities, and bilingual explanations.
    """
    warnings: List[str] = []
    cancellations_applied: List[str] = []

    # --- Resolve Kuja data ---
    # If pre-computed assessments are not provided, derive from chart context directly
    # by checking if Mars occupies any classical Kuja houses (1,2,4,7,8,12).
    KUJA_HOUSES = frozenset({1, 2, 4, 7, 8, 12})

    def _derive_basic_kuja(ctx: MarriageChartContext, role: str) -> Dict[str, Any]:
        """Minimal Kuja presence check when IndividualKujaAssessment is unavailable."""
        mars = ctx.grahas.get("Mars")
        if mars is None:
            return {"is_present": False, "is_cancelled": False, "severity": "None",
                    "intensity": 0.0, "derived": True}
        in_house = mars.house in KUJA_HOUSES
        return {
            "is_present": in_house,
            "is_cancelled": False,
            "severity": "Moderate" if in_house else "None",
            "intensity": 50.0 if in_house else 0.0,
            "derived": True,
        }

    if groom_kuja is not None:
        g_present = groom_kuja.is_present
        g_cancelled = groom_kuja.is_cancelled
        g_severity = groom_kuja.severity
        g_intensity = groom_kuja.effective_intensity_percent
        g_derived = False
    else:
        gd = _derive_basic_kuja(groom_ctx, "groom")
        g_present, g_cancelled, g_severity = gd["is_present"], gd["is_cancelled"], gd["severity"]
        g_intensity = gd["intensity"]
        g_derived = True
        warnings.append("Groom IndividualKujaAssessment not provided; basic Kuja detection used.")

    if bride_kuja is not None:
        b_present = bride_kuja.is_present
        b_cancelled = bride_kuja.is_cancelled
        b_severity = bride_kuja.severity
        b_intensity = bride_kuja.effective_intensity_percent
        b_derived = False
    else:
        bd = _derive_basic_kuja(bride_ctx, "bride")
        b_present, b_cancelled, b_severity = bd["is_present"], bd["is_cancelled"], bd["severity"]
        b_intensity = bd["intensity"]
        b_derived = True
        warnings.append("Bride IndividualKujaAssessment not provided; basic Kuja detection used.")

    # --- Determine active Kuja (present AND not cancelled) ---
    g_active = g_present and not g_cancelled
    b_active = b_present and not b_cancelled

    triggering_comparison: Dict[str, Any] = {
        "groom_present": g_present,
        "groom_cancelled": g_cancelled,
        "groom_active": g_active,
        "groom_intensity": g_intensity,
        "bride_present": b_present,
        "bride_cancelled": b_cancelled,
        "bride_active": b_active,
        "bride_intensity": b_intensity,
    }

    # --- Apply Samadosham rules ---

    # Rule 1: Neither afflicted
    if not g_present and not b_present:
        mutual_balance = "NEITHER_AFFLICTED"
        status = SamadoshamOutcome.MUTUALLY_MATCHED
        en = (
            "Neither partner has Kuja Dosha. "
            "Verdict: MUTUALLY_MATCHED (NEITHER_AFFLICTED) — "
            "no malefic Mars affliction in either chart."
        )
        ta = (
            "இருவருக்கும் குஜதோஷம் இல்லை. "
            "தீர்ப்பு: பரஸ்பர சமனிலை — குஜதோஷ பாதிப்பு இல்லை."
        )

    # Rule 2: Both present but both cancelled by individual rules
    elif g_present and b_present and not g_active and not b_active:
        mutual_balance = "BALANCED"
        status = SamadoshamOutcome.CANCELLED_BY_RULE
        cancellations_applied.append(
            "Both groom and bride Kuja Dosha individually cancelled by classical cancellation rules."
        )
        en = (
            "Both partners have Kuja Dosha, but both are individually cancelled by "
            "classical source-backed cancellation rules. "
            "Verdict: CANCELLED_BY_RULE — effective affliction nullified for both partners."
        )
        ta = (
            "இருவருக்கும் குஜதோஷம் உண்டு, ஆனால் இருவரும் தனித்தனியாக ரத்தாகியுள்ளது. "
            "தீர்ப்பு: விதியால் ரத்தாகியது."
        )

    # Rule 3: Both have active Kuja — check intensity balance
    elif g_active and b_active:
        intensity_diff = abs(g_intensity - b_intensity)
        max_intensity = max(g_intensity, b_intensity, 0.001)
        delta_percent = (intensity_diff / max_intensity) * 100.0
        triggering_comparison["intensity_delta_percent"] = delta_percent

        if delta_percent <= SAMADOSHAM_BALANCE_DELTA_PERCENT:
            mutual_balance = "BALANCED"
            status = SamadoshamOutcome.MUTUALLY_MATCHED
            en = (
                f"Both partners have active Kuja Dosha with comparable intensity "
                f"(Groom: {g_intensity:.0f}%, Bride: {b_intensity:.0f}%, "
                f"delta: {delta_percent:.1f}% ≤ {SAMADOSHAM_BALANCE_DELTA_PERCENT}%). "
                "Verdict: MUTUALLY_MATCHED (BALANCED) — Doshasya samyam bhavati "
                "(Muhurta Chintamani Ch. 6)."
            )
            ta = (
                f"இருவருக்கும் குஜதோஷம் சமம் (ஆண்: {g_intensity:.0f}%, பெண்: {b_intensity:.0f}%). "
                "தீர்ப்பு: பரஸ்பர சமனிலை."
            )
        else:
            # Different intensities but both active — still balanced under broader rule
            mutual_balance = "BALANCED"
            status = SamadoshamOutcome.MUTUALLY_MATCHED
            en = (
                f"Both partners have active Kuja Dosha (Groom: {g_intensity:.0f}%, "
                f"Bride: {b_intensity:.0f}%, delta: {delta_percent:.1f}% > 25%). "
                "Both have active affliction; mutual balance principle applies. "
                "Verdict: MUTUALLY_MATCHED — unequal but mutual affliction accepted "
                "per Kalaprakasika Ch. 12 (Kuja Samadosham)."
            )
            ta = (
                f"இருவருக்கும் குஜதோஷம் உண்டு (ஆண்: {g_intensity:.0f}%, பெண்: {b_intensity:.0f}%). "
                "தீர்ப்பு: பரஸ்பர சமனிலை."
            )
            warnings.append(
                f"Intensity delta {delta_percent:.1f}% exceeds 25% — consider further scrutiny."
            )

    # Rule 4 & 5: One active, one not
    elif g_active and not b_active:
        # Groom has severe Kuja; bride does not
        mutual_balance = "GROOM_EXCESS"
        bride_has_counterpoise = _has_counterpoise(bride_ctx)
        triggering_comparison["bride_has_counterpoise"] = bride_has_counterpoise

        if g_intensity <= SAMADOSHAM_MILD_THRESHOLD_PERCENT or bride_has_counterpoise:
            status = SamadoshamOutcome.MITIGATED
            mitigation_reason = (
                "Bride has Saturn/Rahu counterpoise in 7th/8th house"
                if bride_has_counterpoise else f"Groom Kuja intensity mild (≤ {SAMADOSHAM_MILD_THRESHOLD_PERCENT}%)"
            )
            cancellations_applied.append(mitigation_reason)
            en = (
                f"Groom has active Kuja ({g_intensity:.0f}%); Bride has no active Kuja. "
                f"Mitigation: {mitigation_reason}. "
                "Verdict: MITIGATED — affliction partially offset, proceed with caution."
            )
            ta = (
                f"மணமகனுக்கு குஜதோஷம் ({g_intensity:.0f}%); மணமகளுக்கு இல்லை. "
                f"தணிப்பு: {mitigation_reason}. தீர்ப்பு: குறைந்த தீவிரம்."
            )
        else:
            status = SamadoshamOutcome.NOT_MUTUALLY_MATCHED
            en = (
                f"Groom has severe active Kuja ({g_intensity:.0f}%); Bride has no Kuja and no counterpoise. "
                "Verdict: NOT_MUTUALLY_MATCHED (GROOM_EXCESS) — classical tradition considers "
                "this a significant incompatibility risk."
            )
            ta = (
                f"மணமகனுக்கு கடுமையான குஜதோஷம் ({g_intensity:.0f}%); மணமகளுக்கு இல்லை. "
                "தீர்ப்பு: பொருந்தாத நிலை — குஜன் ஒருதரப்பு."
            )

    elif b_active and not g_active:
        # Bride has active Kuja; groom does not
        mutual_balance = "BRIDE_EXCESS"
        groom_has_counterpoise = _has_counterpoise(groom_ctx)
        triggering_comparison["groom_has_counterpoise"] = groom_has_counterpoise

        if b_intensity <= SAMADOSHAM_MILD_THRESHOLD_PERCENT or groom_has_counterpoise:
            status = SamadoshamOutcome.MITIGATED
            mitigation_reason = (
                "Groom has Saturn/Rahu counterpoise in 7th/8th house"
                if groom_has_counterpoise else f"Bride Kuja intensity mild (≤ {SAMADOSHAM_MILD_THRESHOLD_PERCENT}%)"
            )
            cancellations_applied.append(mitigation_reason)
            en = (
                f"Bride has active Kuja ({b_intensity:.0f}%); Groom has no active Kuja. "
                f"Mitigation: {mitigation_reason}. "
                "Verdict: MITIGATED — affliction partially offset, proceed with caution."
            )
            ta = (
                f"மணமகளுக்கு குஜதோஷம் ({b_intensity:.0f}%); மணமகனுக்கு இல்லை. "
                f"தணிப்பு: {mitigation_reason}. தீர்ப்பு: குறைந்த தீவிரம்."
            )
        else:
            status = SamadoshamOutcome.NOT_MUTUALLY_MATCHED
            en = (
                f"Bride has severe active Kuja ({b_intensity:.0f}%); Groom has no Kuja and no counterpoise. "
                "Verdict: NOT_MUTUALLY_MATCHED (BRIDE_EXCESS) — classical tradition considers "
                "this a significant incompatibility risk."
            )
            ta = (
                f"மணமகளுக்கு கடுமையான குஜதோஷம் ({b_intensity:.0f}%); மணமகனுக்கு இல்லை. "
                "தீர்ப்பு: பொருந்தாத நிலை."
            )

    else:
        # Should not reach here under normal conditions
        mutual_balance = "NEITHER_AFFLICTED"
        status = SamadoshamOutcome.INDETERMINATE
        en = "Kuja Samadosham: INDETERMINATE — unable to classify mutual Kuja state."
        ta = "குஜசமதோஷம்: நிர்ணயிக்க முடியவில்லை."
        warnings.append("Unexpected Kuja state combination; review IndividualKujaAssessment inputs.")

    return MutualKujaResult(
        status=status,
        mutual_balance=mutual_balance,
        groom_severity=g_severity,
        bride_severity=b_severity,
        groom_effective_intensity=g_intensity,
        bride_effective_intensity=b_intensity,
        triggering_comparison=triggering_comparison,
        cancellations_or_mitigations_applied=cancellations_applied,
        explanation_en=en,
        explanation_ta=ta,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Partner-Dependent Dosha Cross-Reference
# ---------------------------------------------------------------------------

# Doshas that are bidirectional and governed by the pair together
PARTNER_DEPENDENT_DOSHA_KEYS = [
    "nadi",     # Nadi Koota (Ashtakoota) — BPHS
    "bhakoot",  # Bhakoot Koota (Ashtakoota) — BPHS
    "gana",     # Gana Koota (Ashtakoota / Tamil) — Nature compatibility
    "yoni",     # Yoni Koota (Ashtakoota) — Sexual compatibility
    "rajju",    # Rajju Porutham (Tamil) — INDEPENDENT VETO; never cancelled by Papasamya/Kuja
    "vedha",    # Vedha Porutham (Tamil) — INDEPENDENT VETO; never cancelled by Papasamya/Kuja
]

# These two are absolute vetoes — they preserve their status regardless of Kuja/Papasamya
INDEPENDENT_VETO_DOSHAS = frozenset({"rajju", "vedha"})


def _build_partner_dosha_summary(
    porutham_results: Optional[Dict[str, Any]] = None,
    ashtakoota_results: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """Collect partner-dependent dosha statuses without duplicating rule logic.

    Args:
        porutham_results: Dict mapping porutham name → PoruthamResult or status dict.
        ashtakoota_results: Dict mapping koota name → KootaResult or status dict.

    Returns:
        (partner_dependent_doshas dict, independent_vetoes_preserved list)
    """
    doshas: Dict[str, Any] = {}
    vetoes_preserved: List[str] = []

    # Collect from Tamil Porutham results
    if porutham_results:
        for key in ["rajju", "vedha", "gana", "nadi", "yoni"]:
            result = porutham_results.get(key)
            if result is not None:
                status = getattr(result, "status", None) or result.get("status")
                doshas[key] = {
                    "source": "tamil_porutham",
                    "status": str(status) if status else "UNKNOWN",
                    "is_dosha": str(status) == "FAIL" if status else False,
                    "is_veto": key in INDEPENDENT_VETO_DOSHAS,
                    "note": (
                        "Independent veto — cannot be cancelled by Kuja or Papasamya outcome."
                        if key in INDEPENDENT_VETO_DOSHAS else ""
                    ),
                }
                if key in INDEPENDENT_VETO_DOSHAS and str(status) == "FAIL":
                    vetoes_preserved.append(
                        f"{key.capitalize()} Porutham FAIL: veto preserved regardless of Kuja/Papasamya."
                    )

    # Collect from Ashtakoota results
    if ashtakoota_results:
        for key in ["nadi", "bhakoot", "gana", "yoni"]:
            result = ashtakoota_results.get(key)
            if result is not None and key not in doshas:  # Don't overwrite Tamil porutham
                score = getattr(result, "score_awarded", None)
                max_score = getattr(result, "max_score", None)
                is_dosha = (score == 0 and max_score is not None and max_score > 0)
                doshas[key] = {
                    "source": "ashtakoota",
                    "score_awarded": score,
                    "max_score": max_score,
                    "is_dosha": is_dosha,
                    "is_veto": False,
                    "note": "",
                }

    return doshas, vetoes_preserved


# ---------------------------------------------------------------------------
# Top-Level Mutual Dosha Analysis Entry Point
# ---------------------------------------------------------------------------

def evaluate_mutual_dosha_analysis(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
    groom_kuja: Optional[IndividualKujaAssessment] = None,
    bride_kuja: Optional[IndividualKujaAssessment] = None,
    porutham_results: Optional[Dict[str, Any]] = None,
    ashtakoota_results: Optional[Dict[str, Any]] = None,
) -> MutualDoshaAnalysisResult:
    """Full Phase 5 mutual dosha analysis pipeline.

    Computes:
    1. Individual Papasamya for groom and bride.
    2. Mutual Papasamya verdict.
    3. Kuja Samadosham (mutual Kuja balancing).
    4. Partner-dependent dosha cross-reference (Rajju, Vedha, Nadi, etc.)
       with independent veto preservation.

    DOES NOT produce a composite final marriage compatibility verdict —
    that is reserved for Phase 6.

    Args:
        groom_ctx: Validated groom MarriageChartContext.
        bride_ctx: Validated bride MarriageChartContext.
        groom_kuja: Optional pre-computed IndividualKujaAssessment for groom.
        bride_kuja: Optional pre-computed IndividualKujaAssessment for bride.
        porutham_results: Optional dict of Tamil Porutham results keyed by name.
        ashtakoota_results: Optional dict of Ashtakoota results keyed by name.

    Returns:
        MutualDoshaAnalysisResult combining all Phase 5 outputs.
    """
    # Step 1: Individual Papasamya
    groom_papasamya = calculate_single_papasamya(groom_ctx, "groom")
    bride_papasamya = calculate_single_papasamya(bride_ctx, "bride")

    # Step 2: Mutual Papasamya verdict
    papasamya_verdict, diff_percent, papa_en, papa_ta = evaluate_mutual_papasamya(
        groom_papasamya, bride_papasamya
    )

    # Step 3: Kuja Samadosham
    samadosham = evaluate_mutual_kuja_samadosham(
        groom_ctx, bride_ctx, groom_kuja, bride_kuja
    )

    # Step 4: Partner-dependent dosha cross-reference
    partner_doshas, vetoes_preserved = _build_partner_dosha_summary(
        porutham_results, ashtakoota_results
    )

    # Collect active doshas with exception notes
    active_doshas: List[Dict[str, Any]] = []
    for key, info in partner_doshas.items():
        if info.get("is_dosha"):
            active_doshas.append({
                "dosha": key,
                "source": info.get("source"),
                "is_veto": info.get("is_veto", False),
                "status_or_score": info.get("status") or info.get("score_awarded"),
                "note": info.get("note", ""),
            })

    return MutualDoshaAnalysisResult(
        groom_kuja=groom_kuja,
        bride_kuja=bride_kuja,
        samadosham=samadosham,
        groom_papasamya=groom_papasamya,
        bride_papasamya=bride_papasamya,
        papasamya_verdict=papasamya_verdict,
        papasamya_diff_percent=diff_percent,
        papasamya_explanation_en=papa_en,
        papasamya_explanation_ta=papa_ta,
        partner_dependent_doshas=partner_doshas,
        active_doshas_with_exceptions=active_doshas,
        independent_vetoes_preserved=vetoes_preserved,
    )
