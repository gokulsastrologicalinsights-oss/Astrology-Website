"""Kuja (Manglik) Dosha evaluation module.

Evaluates Mars affliction from Lagna, Moon, and Venus across classical house placements,
supporting configurable North/South Indian house conventions and rigorous classical
cancellations (BPHS Ch. 81, Muhurta Chintamani, Brihat Samhita).
"""

from typing import Dict, List, Set, Tuple
from app.schemas.dosha import KujaDoshaReferenceDetail, KujaDoshaResult
from app.services.dosha_engine.models import (
    DoshaChartContext,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


def evaluate_kuja_reference(
    ctx: DoshaChartContext,
    ref_name: str,
    ref_sign_idx: int,
    weight: float,
    kuja_houses: Set[int],
) -> KujaDoshaReferenceDetail:
    """Evaluate Kuja Dosha from a single reference point (Lagna, Moon, or Venus)."""
    mars = ctx.mars
    if not mars:
        return KujaDoshaReferenceDetail(
            reference_point=ref_name,
            reference_sign_index=ref_sign_idx,
            reference_sign_name=SIGN_NAMES_EN.get(ref_sign_idx, "Unknown"),
            mars_house_from_reference=1,
            has_dosha=False,
            is_cancelled=False,
            cancellation_reasons=[],
            effective_intensity_percent=0.0,
        )

    mars_house = ctx.house_from("Mars", ref_sign_idx)
    mars_sign = mars.sign_index
    has_dosha = mars_house in kuja_houses

    cancellations: List[str] = []

    if has_dosha:
        # 1. Mars in Own Sign (Aries or Scorpio)
        if mars_sign in (1, 8):
            sign_name = SIGN_NAMES_EN[mars_sign]
            cancellations.append(f"Mars in own sign ({sign_name}) neutralizes malefic fire (BPHS Ch. 81)")

        # 2. Mars in Exaltation (Capricorn)
        elif mars_sign == 10:
            cancellations.append("Mars in exaltation sign (Capricorn) acts as a high-dignity protector (Muhurta Chintamani)")

        # 3. Mars in Debilitation (Cancer) in 7th or 8th house
        elif mars_sign == 4 and mars_house in (7, 8):
            cancellations.append("Mars debilitated in Cancer in 7th/8th house lacks malefic strength to disrupt marital alliance")

        # 4. Classical Sign-House Specific Placements
        # Mars in 2nd house in Gemini (3) or Virgo (6)
        if mars_house == 2 and mars_sign in (3, 6):
            cancellations.append(f"Mars in 2nd house in Mercury's sign ({SIGN_NAMES_EN[mars_sign]}) cancels 2nd-house Kuja dosha")

        # Mars in 12th house in Taurus (2) or Libra (7)
        if mars_house == 12 and mars_sign in (2, 7):
            cancellations.append(f"Mars in 12th house in Venus's sign ({SIGN_NAMES_EN[mars_sign]}) neutralizes bedroom affliction")

        # Mars in 8th house in Sagittarius (9) or Pisces (12)
        if mars_house == 8 and mars_sign in (9, 12):
            cancellations.append(f"Mars in 8th house in Jupiter's sign ({SIGN_NAMES_EN[mars_sign]}) removes marital longevity threat")

        # Mars in 7th or 8th house in Leo (5) or Aquarius (11)
        if mars_house in (7, 8) and mars_sign in (5, 11):
            cancellations.append(f"Mars in {mars_house}th house in {SIGN_NAMES_EN[mars_sign]} is classical friendly/neutral cancellation")

        # 5. Yogakaraka Exception (Evaluated specifically when reference is Lagna)
        if ref_name == "Lagna":
            # Cancer Lagna: Mars rules 5th (Scorpio) & 10th (Aries)
            if ctx.ascendant_sign_idx == 4:
                cancellations.append("Mars is Yogakaraka (lord of 5th & 10th) for Cancer Lagna and cannot cause Kuja Dosha")
            # Leo Lagna: Mars rules 4th (Scorpio) & 9th (Aries)
            elif ctx.ascendant_sign_idx == 5:
                cancellations.append("Mars is Yogakaraka (lord of 4th & 9th) for Leo Lagna and cannot cause Kuja Dosha")

        # 6. Benefic Conjunction / Aspect
        # Jupiter conjoined or aspecting Mars
        if ctx.is_conjoined("Jupiter", "Mars"):
            cancellations.append("Jupiter conjoined with Mars forms auspicious Guru-Mangala combination neutralizing dosha")
        elif ctx.has_aspect_on_graha("Jupiter", "Mars"):
            cancellations.append("Jupiter casts divine Parashari aspect on Mars, extinguishing malefic heat")

        # Moon conjoined with Mars
        if ctx.is_conjoined("Moon", "Mars"):
            cancellations.append("Moon conjoined with Mars creates auspicious Chandra-Mangala yoga mitigating marital friction")

        # 7. Saturn Conjunction / Aspect
        if ctx.is_conjoined("Saturn", "Mars"):
            cancellations.append("Saturn conjoined with Mars checks impulsive marital aggression (BPHS Ch. 81)")
        elif ctx.has_aspect_on_graha("Saturn", "Mars"):
            cancellations.append("Saturn casts Parashari aspect on Mars, tempering planetary volatility")

    is_cancelled = has_dosha and len(cancellations) > 0
    effective_intensity = 0.0 if (not has_dosha or is_cancelled) else weight

    return KujaDoshaReferenceDetail(
        reference_point=ref_name,
        reference_sign_index=ref_sign_idx,
        reference_sign_name=SIGN_NAMES_EN.get(ref_sign_idx, "Unknown"),
        mars_house_from_reference=mars_house,
        has_dosha=has_dosha,
        is_cancelled=is_cancelled,
        cancellation_reasons=cancellations,
        effective_intensity_percent=effective_intensity,
    )


def evaluate_kuja_dosha(
    ctx: DoshaChartContext,
    include_2nd_house: bool = True,
) -> KujaDoshaResult:
    """Evaluate multi-reference Kuja / Manglik Dosha from Lagna, Moon, and Venus."""
    if include_2nd_house:
        kuja_houses = {1, 2, 4, 7, 8, 12}
        convention_name = "South Indian (1, 2, 4, 7, 8, 12)"
    else:
        kuja_houses = {1, 4, 7, 8, 12}
        convention_name = "North Indian (1, 4, 7, 8, 12)"

    # Reference points and their classical weights
    ref_configs: List[Tuple[str, int, float]] = [
        ("Lagna", ctx.ascendant_sign_idx, 100.0),
        ("Moon", ctx.moon_sign_idx, 75.0),
        ("Venus", ctx.venus_sign_idx, 50.0),
    ]

    details: Dict[str, KujaDoshaReferenceDetail] = {}
    for ref_name, ref_sign, weight in ref_configs:
        details[ref_name] = evaluate_kuja_reference(
            ctx=ctx,
            ref_name=ref_name,
            ref_sign_idx=ref_sign,
            weight=weight,
            kuja_houses=kuja_houses,
        )

    present_refs = [r for r in details.values() if r.has_dosha]
    active_refs = [r for r in details.values() if r.has_dosha and not r.is_cancelled]
    all_cancellations = [reason for r in details.values() for reason in r.cancellation_reasons]

    is_present = len(present_refs) > 0
    is_cancelled = is_present and len(active_refs) == 0

    total_active_weight = sum(r.effective_intensity_percent for r in active_refs)

    if not is_present:
        severity = "None"
    elif is_cancelled:
        severity = "Cancelled"
    elif total_active_weight <= 50.0:
        severity = "Mild"
    elif total_active_weight <= 100.0:
        severity = "Moderate"
    else:
        severity = "High"

    cancellation_summary = (
        "; ".join(dict.fromkeys(all_cancellations)) if all_cancellations else None
    )

    # Balanced interpretations
    if not is_present:
        interp_en = (
            "Mars is situated in non-afflicting houses from Lagna, Moon, and Venus. "
            "Kuja Dosha is completely absent in the chart, supporting natural marital harmony and emotional balance."
        )
        interp_ta = (
            "லக்னம், சந்திரன், சுக்கிரன் ஆகிய எந்த இடத்திலிருந்தும் செவ்வாய் பாதகமான இடங்களில் அமையவில்லை. "
            "செவ்வாய் தோஷம் முற்றிலும் இல்லை. களத்திர ஸ்தானம் சுபத்தன்மையுடன் விளங்குகிறது."
        )
    elif is_cancelled:
        interp_en = (
            f"Kuja Dosha was initially triggered from {', '.join(r.reference_point for r in present_refs)}, "
            f"but is fully neutralized by classical cancellation rules ({cancellation_summary}). "
            "The native does not suffer matrimonial disharmony on account of Mars; planetary energies are channeled constructively."
        )
        interp_ta = (
            f"செவ்வாய் தோஷம் ஆரம்பத்தில் காணப்பட்டாலும், பாரம்பரிய விதிவிலக்குகளின்படி ({cancellation_summary}) "
            "முழுமையாக தோஷ நிவர்த்தி பெறுகிறது. திருமண வாழ்க்கையில் பாதகமான தாக்கம் எதுவும் இருக்காது."
        )
    else:
        active_sources = ", ".join(r.reference_point for r in active_refs)
        interp_en = (
            f"Active Kuja Dosha is identified from {active_sources} with a severity level of {severity}. "
            "Classical astrology recommends matching with a compatible partner who also possesses similar Martian balance, "
            "along with fostering patience, mutual respect, and mature communication in interpersonal relationships."
        )
        interp_ta = (
            f"{active_sources} வழியே செவ்வாய் தோஷம் ({severity} நிலை) காணப்படுகிறது. "
            "இதேபோன்ற சமதோஷ ஜாதகத்தை பொருத்துவதும், தம்பதியிடையே பொறுமையும் பரஸ்பர புரிதலும் அமைதியான திருமண வாழ்வுக்கு நலம் பயக்கும்."
        )

    return KujaDoshaResult(
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        house_convention=convention_name,
        details_by_reference=details,
        cancellation_summary=cancellation_summary,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
    )
