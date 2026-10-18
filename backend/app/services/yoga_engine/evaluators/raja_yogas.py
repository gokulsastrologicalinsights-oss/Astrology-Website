"""Raja Yogas: Kendra-Trikona lord combinations, Dharma-Karmadhipati, Neecha Bhanga Raja Yoga, and Vipareeta Raja Yogas."""

from typing import List, Tuple, Set
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    count_houses_inclusive,
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    SIGN_LORDS,
    SIGN_NAMES_EN,
    KENDRA_HOUSES,
    DUSTHANA_HOUSES,
)


def _check_sambandha(ctx: YogaChartContext, planet_a: str, planet_b: str) -> Tuple[bool, str]:
    """Check if two planets form Sambandha (conjunction or mutual aspect)."""
    if planet_a == planet_b:
        h_val = ctx.planet_house.get(planet_a)
        s_val = ctx.planet_sign.get(planet_a)
        sign_str = SIGN_NAMES_EN.get(s_val, "")
        is_strong = (
            ctx.is_in_kendra(planet_a) or ctx.is_in_trikona(planet_a) or
            ctx.is_in_own_sign(planet_a) or ctx.is_exalted(planet_a)
        )
        if is_strong:
            return True, f"Single planet ({planet_a}) is sole lord of both houses (Yogakaraka disposition) and strongly placed in {sign_str} (House {h_val})."
        elif ctx.is_in_dusthana(planet_a):
            return True, f"Single planet ({planet_a}) is sole lord of both houses (Yogakaraka disposition); situated in Dusthana House {h_val} ({sign_str}), manifestation requires persistence."
        else:
            return True, f"Single planet ({planet_a}) is sole lord of both houses (Yogakaraka disposition) in House {h_val} ({sign_str})."

    h_a = ctx.planet_house.get(planet_a)
    h_b = ctx.planet_house.get(planet_b)
    if not h_a or not h_b:
        return False, "Planetary positions missing."

    if h_a == h_b:
        return True, f"{planet_a} and {planet_b} are conjoined in House {h_a} ({SIGN_NAMES_EN[ctx.planet_sign[planet_a]]})."

    if ctx.are_mutually_aspecting(planet_a, planet_b):
        return True, f"{planet_a} (House {h_a}) and {planet_b} (House {h_b}) cast full mutual aspects."

    # Check Parivartana
    sign_a = ctx.planet_sign.get(planet_a)
    sign_b = ctx.planet_sign.get(planet_b)
    lord_sign_a = SIGN_LORDS.get(sign_a)
    lord_sign_b = SIGN_LORDS.get(sign_b)
    if lord_sign_a == planet_b and lord_sign_b == planet_a:
        return True, f"{planet_a} and {planet_b} form a mutual Parivartana (sign exchange)."

    return False, f"No conjunction or mutual aspect between {planet_a} (House {h_a}) and {planet_b} (House {h_b})."


def evaluate_raja_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    results: List[YogaDetail] = []

    # -------------------------------------------------------------
    # 1. Dharma-Karmadhipati Yoga (9th Lord & 10th Lord)
    # -------------------------------------------------------------
    lord_9 = ctx.house_lords[9]
    lord_10 = ctx.house_lords[10]
    has_dk, dk_detail = _check_sambandha(ctx, lord_9, lord_10)

    results.append(
        YogaDetail(
            id="dharma_karmadhipati_yoga",
            name="Dharma-Karmadhipati Yoga",
            name_tamil="தர்ம-கர்மாதிபதி யோகம்",
            category="Raja Yoga",
            status="Qualifying" if has_dk else "Not Qualifying",
            is_qualifying=has_dk,
            planets_involved=list({lord_9, lord_10}),
            relevant_houses=[ctx.planet_house.get(lord_9, 9), ctx.planet_house.get(lord_10, 10)],
            conditions=[
                YogaConditionItem(
                    condition="Lord of 9th (Dharma) and Lord of 10th (Karma) form Sambandha (conjunction, mutual aspect, or exchange)",
                    passed=has_dk,
                    detail=f"9th Lord is {lord_9}, 10th Lord is {lord_10}. Result: {dk_detail}"
                )
            ],
            short_interpretation="Foremost royal combination: Bestows executive sovereignty, moral leadership, great philanthropic enterprises, and enduring status.",
            classical_definition="The lord of the 9th house and the lord of the 10th house unite by conjunction, mutual aspect, or sign exchange.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 41; Phaladeepika Ch. 6; 300 Important Combinations #110",
            verification_status="Classical Independent Implementation"
        )
    )

    # -------------------------------------------------------------
    # 2. General Kendra-Trikona Lord Raja Yogas
    # Kendras: (1, 4, 7, 10); Trikonas: (1, 5, 9)
    # Exclude 9-10 pair as it is specifically handled above
    # -------------------------------------------------------------
    kt_pairs = [
        (1, 5, "Lagna Lord and 5th Lord Raja Yoga", "லக்னாதிபதி மற்றும் 5-ஆம் அதிபதி ராஜ யோகம்"),
        (1, 9, "Lagna Lord and 9th Lord Raja Yoga", "லக்னாதிபதி மற்றும் 9-ஆம் அதிபதி ராஜ யோகம்"),
        (4, 5, "4th Lord and 5th Lord Raja Yoga", "4-ஆம் அதிபதி மற்றும் 5-ஆம் அதிபதி ராஜ யோகம்"),
        (4, 9, "4th Lord and 9th Lord Raja Yoga", "4-ஆம் அதிபதி மற்றும் 9-ஆம் அதிபதி ராஜ யோகம்"),
        (5, 7, "5th Lord and 7th Lord Raja Yoga", "5-ஆம் அதிபதி மற்றும் 7-ஆம் அதிபதி ராஜ யோகம்"),
        (5, 10, "5th Lord and 10th Lord Raja Yoga", "5-ஆம் அதிபதி மற்றும் 10-ஆம் அதிபதி ராஜ யோகம்"),
        (7, 9, "7th Lord and 9th Lord Raja Yoga", "7-ஆம் அதிபதி மற்றும் 9-ஆம் அதிபதி ராஜ யோகம்"),
        (7, 10, "7th Lord and 10th Lord Raja Yoga", "7-ஆம் அதிபதி மற்றும் 10-ஆம் அதிபதி ராஜ யோகம்"),
    ]

    for h_k, h_t, name_en, name_ta in kt_pairs:
        l_k = ctx.house_lords[h_k]
        l_t = ctx.house_lords[h_t]
        qual, detail_str = _check_sambandha(ctx, l_k, l_t)

        results.append(
            YogaDetail(
                id=f"raja_yoga_{h_k}_{h_t}",
                name=name_en,
                name_tamil=name_ta,
                category="Raja Yoga",
                status="Qualifying" if qual else "Not Qualifying",
                is_qualifying=qual,
                planets_involved=list({l_k, l_t}),
                relevant_houses=[h for h in (ctx.planet_house.get(l_k), ctx.planet_house.get(l_t)) if h],
                conditions=[
                    YogaConditionItem(
                        condition=f"Lord of Kendra (House {h_k}: {l_k}) and Lord of Trikona (House {h_t}: {l_t}) form Sambandha",
                        passed=qual,
                        detail=detail_str
                    )
                ],
                short_interpretation="Augments royal dignities, executive influence, high career achievements, and patronage from superiors.",
                classical_definition=f"The lord of Kendra house {h_k} and Trikona house {h_t} associate by conjunction, mutual aspect, or exchange.",
                classical_reference="Brihat Parashara Hora Shastra Ch. 34 & 41; Bhavartha Ratnakara",
                verification_status="Classical Independent Implementation"
            )
        )

    # -------------------------------------------------------------
    # 3. Yogakaraka Planet Raja Yoga
    # When a single planet rules both a Kendra and a Trikona (e.g., Mars for Cancer/Leo; Saturn for Taurus/Libra; Venus for Capricorn/Aquarius)
    # -------------------------------------------------------------
    kendra_lords = {ctx.house_lords[h] for h in (4, 7, 10)} # 1 is already both
    trikona_lords = {ctx.house_lords[h] for h in (5, 9)}
    yogakaraka_planets = list(kendra_lords.intersection(trikona_lords))

    for yk_planet in yogakaraka_planets:
        yk_house = ctx.planet_house.get(yk_planet)
        is_strong = ctx.is_exalted(yk_planet) or ctx.is_in_own_sign(yk_planet) or ctx.is_in_kendra(yk_planet) or ctx.is_in_trikona(yk_planet)
        results.append(
            YogaDetail(
                id=f"yogakaraka_raja_yoga_{yk_planet.lower()}",
                name=f"Yogakaraka {yk_planet} Raja Yoga",
                name_tamil=f"யோககாரக {yk_planet} ராஜ யோகம்",
                category="Raja Yoga",
                status="Qualifying" if is_strong else "Not Qualifying",
                is_qualifying=is_strong,
                planets_involved=[yk_planet],
                relevant_houses=[yk_house] if yk_house else [],
                conditions=[
                    YogaConditionItem(
                        condition=f"{yk_planet} is the functional Yogakaraka ruling both a Kendra and a Trikona house",
                        passed=True,
                        detail=f"{yk_planet} rules houses {', '.join(str(h) for h, l in ctx.house_lords.items() if l == yk_planet)}."
                    ),
                    YogaConditionItem(
                        condition=f"{yk_planet} is favorably disposed in Kendra, Trikona, own sign, or exaltation",
                        passed=is_strong,
                        detail=f"{yk_planet} is in House {yk_house} ({SIGN_NAMES_EN[ctx.planet_sign[yk_planet]]})."
                    )
                ],
                short_interpretation=f"Single-handed benefic power of {yk_planet} elevates personal destiny, granting status, prosperity, and authority.",
                classical_definition="A single planet simultaneous lord of a Kendra and a Trikona house.",
                classical_reference="Brihat Parashara Hora Shastra Ch. 34; Phaladeepika Ch. 6",
                verification_status="Classical Independent Implementation"
            )
        )

    # -------------------------------------------------------------
    # 4. Neecha Bhanga Raja Yoga (NBRY)
    # Debilitated planet receiving cancellation
    # -------------------------------------------------------------
    moon_house = ctx.planet_house.get("Moon")

    for deb_planet, deb_sign in DEBILITATION_SIGNS.items():
        if ctx.planet_sign.get(deb_planet) == deb_sign:
            # Planet is debilitated! Evaluate cancellation criteria
            deb_planet_house = ctx.planet_house[deb_planet]
            dispositor = SIGN_LORDS[deb_sign]
            disp_house = ctx.planet_house.get(dispositor)

            # Exaltation lord: The planet that gets exalted in the sign where deb_planet is debilitated
            exalt_planet = next((p for p, ex_sign in EXALTATION_SIGNS.items() if ex_sign == deb_sign), None)
            exalt_planet_house = ctx.planet_house.get(exalt_planet) if exalt_planet else None

            # Debilitation planet's own exaltation lord
            own_ex_sign = EXALTATION_SIGNS.get(deb_planet)
            own_ex_lord = SIGN_LORDS.get(own_ex_sign) if own_ex_sign else None
            own_ex_lord_house = ctx.planet_house.get(own_ex_lord) if own_ex_lord else None

            # Criteria 1: Dispositor of debilitated sign is in Kendra from Lagna or Moon
            c1_lagna = disp_house in KENDRA_HOUSES if disp_house else False
            c1_moon = (count_houses_inclusive(moon_house, disp_house) in {1, 4, 7, 10}) if (moon_house and disp_house) else False
            c1 = c1_lagna or c1_moon

            # Criteria 2: Exalted ruler of the debilitation sign is in Kendra from Lagna or Moon
            c2_lagna = exalt_planet_house in KENDRA_HOUSES if exalt_planet_house else False
            c2_moon = (count_houses_inclusive(moon_house, exalt_planet_house) in {1, 4, 7, 10}) if (moon_house and exalt_planet_house) else False
            c2 = c2_lagna or c2_moon

            # Criteria 3: Lord of exaltation sign of debilitated planet is in Kendra from Lagna or Moon
            c3_lagna = own_ex_lord_house in KENDRA_HOUSES if own_ex_lord_house else False
            c3_moon = (count_houses_inclusive(moon_house, own_ex_lord_house) in {1, 4, 7, 10}) if (moon_house and own_ex_lord_house) else False
            c3 = c3_lagna or c3_moon

            # Criteria 4: Debilitated planet itself is in a Kendra from Lagna or Moon
            c4_lagna = deb_planet_house in KENDRA_HOUSES
            c4_moon = (count_houses_inclusive(moon_house, deb_planet_house) in {1, 4, 7, 10}) if moon_house else False
            c4 = c4_lagna or c4_moon

            # Criteria 5: Debilitated planet is aspected by its dispositor
            c5 = ctx.planet_aspects_planet(dispositor, deb_planet)

            # Criteria 6 (Navamsha): Debilitated planet in D1 is exalted in Navamsha (D9)
            deb_nav_sign = ctx.planet_navamsa_sign.get(deb_planet)
            c6 = (deb_nav_sign == own_ex_sign) if (deb_nav_sign and own_ex_sign) else False

            nbry_qualifies = c1 or c2 or c3 or c4 or c5 or c6
            qualifying_criteria = []
            if c1: qualifying_criteria.append(f"Dispositor {dispositor} in Kendra from Lagna/Moon (House {disp_house})")
            if c2: qualifying_criteria.append(f"Exalted lord {exalt_planet} in Kendra from Lagna/Moon (House {exalt_planet_house})")
            if c3: qualifying_criteria.append(f"Exaltation sign ruler {own_ex_lord} in Kendra from Lagna/Moon (House {own_ex_lord_house})")
            if c4: qualifying_criteria.append(f"{deb_planet} itself is in a Kendra (House {deb_planet_house})")
            if c5: qualifying_criteria.append(f"{deb_planet} is aspected by dispositor {dispositor}")
            if c6: qualifying_criteria.append(f"{deb_planet} is exalted in Navamsha D9 ({SIGN_NAMES_EN.get(deb_nav_sign, '')})")

            results.append(
                YogaDetail(
                    id=f"neecha_bhanga_raja_yoga_{deb_planet.lower()}",
                    name=f"Neecha Bhanga Raja Yoga ({deb_planet})",
                    name_tamil=f"நீச பங்க ராஜ யோகம் ({deb_planet})",
                    category="Raja Yoga",
                    status="Qualifying" if nbry_qualifies else "Not Qualifying",
                    is_qualifying=nbry_qualifies,
                    planets_involved=[deb_planet, dispositor] + ([exalt_planet] if exalt_planet and c2 else []),
                    relevant_houses=[deb_planet_house] + ([disp_house] if disp_house else []),
                    conditions=[
                        YogaConditionItem(
                            condition=f"{deb_planet} is debilitated in {SIGN_NAMES_EN[deb_sign]}",
                            passed=True,
                            detail=f"{deb_planet} occupies {SIGN_NAMES_EN[deb_sign]} (House {deb_planet_house})."
                        ),
                        YogaConditionItem(
                            condition="At least one classical Parashari Neecha Bhanga cancellation rule is satisfied",
                            passed=nbry_qualifies,
                            detail="; ".join(qualifying_criteria) if qualifying_criteria else "No cancellation conditions satisfied."
                        )
                    ],
                    short_interpretation=(
                        f"Initial hurdles transformed into phenomenal success; {deb_planet}'s cancellation creates sovereign power, resilience, and renown."
                    ),
                    classical_definition="A debilitated planet whose debilitation is cancelled by its dispositor, exaltation ruler, or Kendra placement.",
                    classical_reference="Phaladeepika Ch. 6, verses 26-30; Brihat Parashara Hora Shastra; 300 Important Combinations #46",
                    verification_status="Classical Independent Implementation"
                )
            )

    # -------------------------------------------------------------
    # 5. Vipareeta Raja Yogas (Harsha, Sarala, Vimala)
    # Dusthana lords (6, 8, 12) occupying other Dusthanas
    # -------------------------------------------------------------
    l_6 = ctx.house_lords[6]
    l_8 = ctx.house_lords[8]
    l_12 = ctx.house_lords[12]

    h_l6 = ctx.planet_house.get(l_6)
    h_l8 = ctx.planet_house.get(l_8)
    h_l12 = ctx.planet_house.get(l_12)

    # 5.1 Harsha Yoga (6th lord in 6th, 8th, or 12th)
    harsha_pass = (h_l6 in DUSTHANA_HOUSES) if h_l6 else False
    results.append(
        YogaDetail(
            id="harsha_yoga",
            name="Harsha Yoga (Vipareeta Raja)",
            name_tamil="ஹர்ஷ யோகம் (விபரீத ராஜ)",
            category="Vipareeta Raja",
            status="Qualifying" if harsha_pass else "Not Qualifying",
            is_qualifying=harsha_pass,
            planets_involved=[l_6],
            relevant_houses=[h_l6] if h_l6 else [],
            conditions=[
                YogaConditionItem(
                    condition="6th house lord occupies 6th, 8th, or 12th house (Dusthanas)",
                    passed=harsha_pass,
                    detail=f"6th Lord {l_6} occupies House {h_l6} ({'Dusthana' if harsha_pass else 'Non-dusthana'})."
                )
            ],
            short_interpretation="Victory over adversaries, physical fortitude, triumph in litigation, and gain through unforeseen adversity.",
            classical_definition="Lord of the 6th occupies the 6th, 8th, or 12th house without malefic destruction.",
            classical_reference="Phaladeepika Ch. 6, v. 57; Uttara Kalamrita",
            verification_status="Verified"
        )
    )

    # 5.2 Sarala Yoga (8th lord in 6th, 8th, or 12th)
    sarala_pass = (h_l8 in DUSTHANA_HOUSES) if h_l8 else False
    results.append(
        YogaDetail(
            id="sarala_yoga",
            name="Sarala Yoga (Vipareeta Raja)",
            name_tamil="சரள யோகம் (விபரீத ராஜ)",
            category="Vipareeta Raja",
            status="Qualifying" if sarala_pass else "Not Qualifying",
            is_qualifying=sarala_pass,
            planets_involved=[l_8],
            relevant_houses=[h_l8] if h_l8 else [],
            conditions=[
                YogaConditionItem(
                    condition="8th house lord occupies 6th, 8th, or 12th house (Dusthanas)",
                    passed=sarala_pass,
                    detail=f"8th Lord {l_8} occupies House {h_l8} ({'Dusthana' if sarala_pass else 'Non-dusthana'})."
                )
            ],
            short_interpretation="Long life, fearless demeanor, sudden windfall of wealth, scholarly erudition, and immunity to secret plots.",
            classical_definition="Lord of the 8th occupies the 6th, 8th, or 12th house.",
            classical_reference="Phaladeepika Ch. 6, v. 63; Uttara Kalamrita",
            verification_status="Verified"
        )
    )

    # 5.3 Vimala Yoga (12th lord in 6th, 8th, or 12th)
    vimala_pass = (h_l12 in DUSTHANA_HOUSES) if h_l12 else False
    results.append(
        YogaDetail(
            id="vimala_yoga",
            name="Vimala Yoga (Vipareeta Raja)",
            name_tamil="விமல யோகம் (விபரீத ராஜ)",
            category="Vipareeta Raja",
            status="Qualifying" if vimala_pass else "Not Qualifying",
            is_qualifying=vimala_pass,
            planets_involved=[l_12],
            relevant_houses=[h_l12] if h_l12 else [],
            conditions=[
                YogaConditionItem(
                    condition="12th house lord occupies 6th, 8th, or 12th house (Dusthanas)",
                    passed=vimala_pass,
                    detail=f"12th Lord {l_12} occupies House {h_l12} ({'Dusthana' if vimala_pass else 'Non-dusthana'})."
                )
            ],
            short_interpretation="Spending on righteous causes, independence, serene contentment, and freedom from financial liabilities.",
            classical_definition="Lord of the 12th occupies the 6th, 8th, or 12th house.",
            classical_reference="Phaladeepika Ch. 6, v. 69; Uttara Kalamrita",
            verification_status="Verified"
        )
    )

    # -------------------------------------------------------------
    # 6. Kahala Yoga
    # Lords of 4th and 9th in mutual Kendras, and Lagna lord strong
    # -------------------------------------------------------------
    l_4 = ctx.house_lords[4]
    l_9 = ctx.house_lords[9]
    l_1 = ctx.house_lords[1]
    h_l4 = ctx.planet_house.get(l_4)
    h_l9 = ctx.planet_house.get(l_9)
    dist_4_9 = count_houses_inclusive(h_l4, h_l9) if (h_l4 and h_l9) else None
    mutual_kendra_4_9 = dist_4_9 in {1, 4, 7, 10} if dist_4_9 else False
    lagna_lord_strong = (
        ctx.is_exalted(l_1) or ctx.is_in_own_sign(l_1) or ctx.is_in_kendra(l_1) or ctx.is_in_trikona(l_1)
    )
    kahala_qualifies = mutual_kendra_4_9 and lagna_lord_strong

    results.append(
        YogaDetail(
            id="kahala_yoga",
            name="Kahala Yoga",
            name_tamil="காகல யோகம்",
            category="Raja Yoga",
            status="Qualifying" if kahala_qualifies else "Not Qualifying",
            is_qualifying=kahala_qualifies,
            planets_involved=[l_4, l_9, l_1],
            relevant_houses=[h for h in (h_l4, h_l9, ctx.planet_house.get(l_1)) if h],
            conditions=[
                YogaConditionItem(
                    condition="4th lord and 9th lord are in mutual Kendras (1st, 4th, 7th, 10th from each other)",
                    passed=mutual_kendra_4_9,
                    detail=f"4th Lord {l_4} (House {h_l4}), 9th Lord {l_9} (House {h_l9}) - Distance: {dist_4_9}."
                ),
                YogaConditionItem(
                    condition="Lagna lord is strongly disposed (in Kendra, Trikona, own sign, or exaltation)",
                    passed=lagna_lord_strong,
                    detail=f"Lagna lord {l_1} is in House {ctx.planet_house.get(l_1)}."
                )
            ],
            short_interpretation="Courageous, commanding personality, authority over armies or civic bodies, prosperous and respected.",
            classical_definition="Lords of 4th and 9th in mutual Kendras and the lord of Lagna is strong.",
            classical_reference="Phaladeepika Ch. 6, v. 34; 300 Important Combinations #50",
            verification_status="Verified"
        )
    )

    # -------------------------------------------------------------
    # 7. Chamara Yoga
    # Lagna lord exalted in a Kendra aspected by Jupiter, or two benefics in Lagna/7th/9th/10th
    # -------------------------------------------------------------
    c_cond1 = ctx.is_exalted(l_1) and ctx.is_in_kendra(l_1) and ctx.planet_aspects_planet("Jupiter", l_1)
    benefics_auspicious = [
        p for p in ("Jupiter", "Venus", "Mercury")
        if ctx.planet_house.get(p) in {1, 7, 9, 10}
    ]
    c_cond2 = len(benefics_auspicious) >= 2
    chamara_qualifies = c_cond1 or c_cond2

    results.append(
        YogaDetail(
            id="chamara_yoga",
            name="Chamara Yoga",
            name_tamil="சாமர யோகம்",
            category="Raja Yoga",
            status="Qualifying" if chamara_qualifies else "Not Qualifying",
            is_qualifying=chamara_qualifies,
            planets_involved=[l_1, "Jupiter"] if c_cond1 else benefics_auspicious,
            relevant_houses=[ctx.planet_house.get(l_1, 1)],
            conditions=[
                YogaConditionItem(
                    condition="Condition 1: Lagna lord exalted in a Kendra and aspected by Jupiter",
                    passed=c_cond1,
                    detail=f"Lagna lord {l_1} Exalted: {ctx.is_exalted(l_1)}, Kendra: {ctx.is_in_kendra(l_1)}, Jup Aspect: {ctx.planet_aspects_planet('Jupiter', l_1)}."
                ),
                YogaConditionItem(
                    condition="Condition 2: Two natural benefics occupy 1st, 7th, 9th, or 10th houses",
                    passed=c_cond2,
                    detail=f"Benefics in 1, 7, 9, 10: {', '.join(benefics_auspicious) if benefics_auspicious else 'None'}."
                )
            ],
            short_interpretation="Royal insignia, philosophical wisdom, eloquence in assemblies, and celebrated fame.",
            classical_definition="Lagna lord exalted in Kendra with Jupiter aspect, or two benefics in 1st, 7th, 9th, or 10th.",
            classical_reference="Phaladeepika Ch. 6, v. 44; 300 Important Combinations #47",
            verification_status="Verified"
        )
    )

    return results
