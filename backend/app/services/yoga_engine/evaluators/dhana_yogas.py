"""Dhana (Wealth) Yogas: Wealth-house combinations, Lakshmi Yoga, and Vasumathi Yoga."""

from typing import List, Tuple
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    UPACHAYA_HOUSES,
    count_houses_inclusive,
    SIGN_LORDS,
    SIGN_NAMES_EN,
)


def _check_dhana_sambandha(ctx: YogaChartContext, planet_a: str, planet_b: str) -> Tuple[bool, str]:
    """Check conjunction, mutual aspect, or exchange between two wealth lords."""
    if planet_a == planet_b:
        h_val = ctx.planet_house.get(planet_a)
        s_val = ctx.planet_sign.get(planet_a)
        sign_str = SIGN_NAMES_EN.get(s_val, "")
        is_strong = (
            ctx.is_in_kendra(planet_a) or ctx.is_in_trikona(planet_a) or
            ctx.is_in_own_sign(planet_a) or ctx.is_exalted(planet_a)
        )
        if is_strong:
            return True, f"Single planet ({planet_a}) rules both wealth houses and is strongly placed in {sign_str} (House {h_val})."
        elif ctx.is_in_dusthana(planet_a):
            return True, f"Single planet ({planet_a}) rules both wealth houses; situated in Dusthana House {h_val} ({sign_str}), wealth accrues through disciplined effort."
        else:
            return True, f"Single planet ({planet_a}) rules both wealth houses in House {h_val} ({sign_str})."

    h_a = ctx.planet_house.get(planet_a)
    h_b = ctx.planet_house.get(planet_b)
    if not h_a or not h_b:
        return False, "Planetary positions missing."

    if h_a == h_b:
        return True, f"{planet_a} and {planet_b} are conjoined in House {h_a} ({SIGN_NAMES_EN[ctx.planet_sign[planet_a]]})."

    if ctx.are_mutually_aspecting(planet_a, planet_b):
        return True, f"{planet_a} (House {h_a}) and {planet_b} (House {h_b}) cast mutual aspects."

    sign_a = ctx.planet_sign.get(planet_a)
    sign_b = ctx.planet_sign.get(planet_b)
    if SIGN_LORDS.get(sign_a) == planet_b and SIGN_LORDS.get(sign_b) == planet_a:
        return True, f"{planet_a} and {planet_b} form a mutual sign exchange (Parivartana)."

    return False, f"No conjunction or aspect between {planet_a} (House {h_a}) and {planet_b} (House {h_b})."


def evaluate_dhana_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    results: List[YogaDetail] = []

    # -------------------------------------------------------------
    # 1. Classical Wealth House Lord Combinations
    # -------------------------------------------------------------
    dhana_pairs = [
        (2, 11, "2nd Lord and 11th Lord Dhana Yoga", "2-ஆம் அதிபதி மற்றும் 11-ஆம் அதிபதி தன யோகம்"),
        (2, 9, "2nd Lord and 9th Lord Dhana Yoga", "2-ஆம் அதிபதி மற்றும் 9-ஆம் அதிபதி தன யோகம்"),
        (1, 2, "1st Lord and 2nd Lord Dhana Yoga", "லக்னாதிபதி மற்றும் 2-ஆம் அதிபதி தன யோகம்"),
        (1, 11, "1st Lord and 11th Lord Dhana Yoga", "லக்னாதிபதி மற்றும் 11-ஆம் அதிபதி தன யோகம்"),
        (5, 11, "5th Lord and 11th Lord Dhana Yoga", "5-ஆம் அதிபதி மற்றும் 11-ஆம் அதிபதி தன யோகம்"),
        (5, 9, "5th Lord and 9th Lord Dhana Yoga", "5-ஆம் அதிபதி மற்றும் 9-ஆம் அதிபதி தன யோகம்"),
        (9, 11, "9th Lord and 11th Lord Dhana Yoga", "9-ஆம் அதிபதி மற்றும் 11-ஆம் அதிபதி தன யோகம்"),
    ]

    for h1, h2, name_en, name_ta in dhana_pairs:
        l1 = ctx.house_lords[h1]
        l2 = ctx.house_lords[h2]
        qual, detail_str = _check_dhana_sambandha(ctx, l1, l2)

        results.append(
            YogaDetail(
                id=f"dhana_yoga_{h1}_{h2}",
                name=name_en,
                name_tamil=name_ta,
                category="Dhana Yoga",
                status="Qualifying" if qual else "Not Qualifying",
                is_qualifying=qual,
                planets_involved=list({l1, l2}),
                relevant_houses=[h for h in (ctx.planet_house.get(l1), ctx.planet_house.get(l2)) if h],
                conditions=[
                    YogaConditionItem(
                        condition=f"Lord of House {h1} ({l1}) and Lord of House {h2} ({l2}) form Sambandha",
                        passed=qual,
                        detail=detail_str
                    )
                ],
                short_interpretation="Magnifies accumulated assets, financial inflows, successful investments, and sustainable prosperity.",
                classical_definition=f"The ruler of wealth house {h1} and wealth house {h2} associate by conjunction, mutual aspect, or exchange.",
                classical_reference="Brihat Parashara Hora Shastra Ch. 41 & 42; Bhavartha Ratnakara",
                verification_status="Classical Independent Implementation"
            )
        )

    # -------------------------------------------------------------
    # 2. Lakshmi Yoga
    # 9th lord in Kendra/Trikona in its own or exaltation sign,
    # and Lagna lord is powerfully placed.
    # -------------------------------------------------------------
    l_9 = ctx.house_lords[9]
    l_1 = ctx.house_lords[1]
    h_9 = ctx.planet_house.get(l_9)
    in_kendra_trikona_9 = (h_9 in {1, 4, 5, 7, 9, 10}) if h_9 else False
    is_dignified_9 = ctx.is_in_own_sign(l_9) or ctx.is_exalted(l_9)
    lagna_lord_strong = (
        ctx.is_in_kendra(l_1) or ctx.is_in_trikona(l_1) or ctx.is_in_own_sign(l_1) or ctx.is_exalted(l_1)
    )

    lakshmi_qualifies = in_kendra_trikona_9 and is_dignified_9 and lagna_lord_strong

    results.append(
        YogaDetail(
            id="lakshmi_yoga",
            name="Lakshmi Yoga",
            name_tamil="லட்சுமி யோகம்",
            category="Dhana Yoga",
            status="Qualifying" if lakshmi_qualifies else "Not Qualifying",
            is_qualifying=lakshmi_qualifies,
            planets_involved=[l_9, l_1],
            relevant_houses=[h for h in (h_9, ctx.planet_house.get(l_1)) if h],
            conditions=[
                YogaConditionItem(
                    condition="9th house lord occupies a Kendra or Trikona in own sign or exaltation",
                    passed=in_kendra_trikona_9 and is_dignified_9,
                    detail=f"9th Lord {l_9} in House {h_9} ({'Kendra/Trikona' if in_kendra_trikona_9 else 'Other'}), Dignity: Own={ctx.is_in_own_sign(l_9)}, Exalted={ctx.is_exalted(l_9)}."
                ),
                YogaConditionItem(
                    condition="Lagna lord is powerfully disposed (in Kendra, Trikona, own sign, or exaltation)",
                    passed=lagna_lord_strong,
                    detail=f"Lagna lord {l_1} is in House {ctx.planet_house.get(l_1)}."
                )
            ],
            short_interpretation="Goddess of Wealth bestows perpetual riches, regal elegance, noble character, philanthropy, and lasting family fortunes.",
            classical_definition="The lord of the 9th occupies a Kendra or Trikona in its own or exaltation sign, while the lord of Lagna is strong.",
            classical_reference="Brihat Parashara Hora Shastra; 300 Important Combinations #36",
            verification_status="Classical Independent Implementation"
        )
    )

    # -------------------------------------------------------------
    # 3. Vasumathi Yoga (Corrected)
    # All 3 natural benefics (Jupiter, Venus, Mercury) situated
    # in Upachaya houses (3, 6, 10, 11) from Lagna or Moon.
    # -------------------------------------------------------------
    moon_house = ctx.planet_house.get("Moon")
    benefics = ["Jupiter", "Venus", "Mercury"]

    # Check from Lagna
    benefics_in_upachaya_lagna = [
        p for p in benefics if ctx.planet_house.get(p) in UPACHAYA_HOUSES
    ]
    all_in_upachaya_lagna = len(benefics_in_upachaya_lagna) == 3

    # Check from Moon
    def _in_moon_upachaya(p: str) -> bool:
        h = ctx.planet_house.get(p)
        if not h or not moon_house:
            return False
        dist = count_houses_inclusive(moon_house, h)
        return dist in UPACHAYA_HOUSES

    benefics_in_upachaya_moon = [p for p in benefics if _in_moon_upachaya(p)]
    all_in_upachaya_moon = len(benefics_in_upachaya_moon) == 3

    vasu_qualifies = all_in_upachaya_lagna or all_in_upachaya_moon
    vasu_partial = (len(benefics_in_upachaya_lagna) >= 2 or len(benefics_in_upachaya_moon) >= 2)

    results.append(
        YogaDetail(
            id="vasumathi_yoga",
            name="Vasumathi Yoga",
            name_tamil="வசுமதி யோகம்",
            category="Dhana Yoga",
            status="Qualifying" if vasu_qualifies else ("Partially Qualifying" if vasu_partial else "Not Qualifying"),
            is_qualifying=vasu_qualifies,
            planets_involved=benefics,
            relevant_houses=[ctx.planet_house.get(p) for p in benefics if ctx.planet_house.get(p)],
            conditions=[
                YogaConditionItem(
                    condition="All three natural benefics (Jupiter, Venus, Mercury) occupy Upachaya houses (3, 6, 10, 11) from Lagna",
                    passed=all_in_upachaya_lagna,
                    detail=f"Benefics in Lagna Upachayas: {', '.join(benefics_in_upachaya_lagna) if benefics_in_upachaya_lagna else 'None'} ({len(benefics_in_upachaya_lagna)}/3)."
                ),
                YogaConditionItem(
                    condition="Alternative: All three natural benefics occupy Upachaya houses (3, 6, 10, 11) from Moon",
                    passed=all_in_upachaya_moon,
                    detail=f"Benefics in Moon Upachayas: {', '.join(benefics_in_upachaya_moon) if benefics_in_upachaya_moon else 'None'} ({len(benefics_in_upachaya_moon)}/3)."
                )
            ],
            short_interpretation="Independent accumulation of vast wealth, self-made financial empire, victory over debt, and boundless material comfort.",
            classical_definition="All natural benefics (Jupiter, Venus, Mercury) occupy Upachaya houses (3, 6, 10, 11) from Lagna or Moon.",
            classical_reference="Brihat Parashara Hora Shastra; Phaladeepika Ch. 6, v. 23; 300 Important Combinations #40",
            verification_status="Corrected from Reference (Fixed 3-benefics in 4-houses logical bug)"
        )
    )

    return results
