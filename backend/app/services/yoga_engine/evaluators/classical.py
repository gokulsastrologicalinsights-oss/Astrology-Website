"""Classical Major Vedic Yogas: Gajakesari, Budha-Aditya, Chandra-Mangala, Panch Mahapurusha, Amala, Maha Bhagya."""

from typing import List
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    count_houses_inclusive,
    KENDRA_HOUSES,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


def evaluate_classical_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    results: List[YogaDetail] = []

    # 1. Gajakesari Yoga
    # Jupiter in Kendra (1, 4, 7, 10) from Moon (or Lagna)
    moon_house = ctx.planet_house.get("Moon")
    jup_house = ctx.planet_house.get("Jupiter")
    gaj_conditions: List[YogaConditionItem] = []
    gaj_qualifies = False
    rel_houses = []
    planets_inv = ["Moon", "Jupiter"]

    if moon_house and jup_house:
        rel_houses = [moon_house, jup_house]
        dist_from_moon = count_houses_inclusive(moon_house, jup_house)
        kendra_from_moon = dist_from_moon in {1, 4, 7, 10}
        kendra_from_lagna = jup_house in KENDRA_HOUSES

        gaj_conditions.append(
            YogaConditionItem(
                condition="Primary: Jupiter is placed in a Kendra (1st, 4th, 7th, or 10th house) from the Moon",
                passed=kendra_from_moon,
                detail=f"Jupiter is in house {jup_house} ({dist_from_moon}th from Moon in house {moon_house})."
            )
        )
        gaj_conditions.append(
            YogaConditionItem(
                condition="Supplementary dignity: Jupiter is also in a Kendra (1, 4, 7, 10) from Lagna",
                passed=kendra_from_lagna,
                detail=f"Jupiter house {jup_house} {'is' if kendra_from_lagna else 'is not'} in Kendra from Lagna."
            )
        )
        gaj_qualifies = kendra_from_moon
    else:
        gaj_conditions.append(
            YogaConditionItem(
                condition="Moon and Jupiter positions available",
                passed=False,
                detail="Planetary coordinates missing."
            )
        )

    results.append(
        YogaDetail(
            id="gajakesari_yoga",
            name="Gajakesari Yoga",
            name_tamil="கஜகேசரி யோகம்",
            category="Major Classical",
            status="Qualifying" if gaj_qualifies else "Not Qualifying",
            is_qualifying=gaj_qualifies,
            planets_involved=planets_inv,
            relevant_houses=rel_houses,
            conditions=gaj_conditions,
            short_interpretation="Bestows noble reputation, administrative authority, eloquence, wisdom, and lasting prominence.",
            classical_definition="Jupiter occupies an angular (Kendra) house from the Moon or from Lagna.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 18; 300 Important Combinations #38",
            verification_status="Verified"
        )
    )

    # 2. Budha-Aditya Yoga
    # Sun and Mercury conjunct in the same sign
    sun_sign = ctx.planet_sign.get("Sun")
    merc_sign = ctx.planet_sign.get("Mercury")
    sun_house = ctx.planet_house.get("Sun")
    merc_house = ctx.planet_house.get("Mercury")
    ba_conditions: List[YogaConditionItem] = []
    ba_qualifies = False
    ba_houses = []

    if sun_sign and merc_sign:
        same_sign = (sun_sign == merc_sign)
        ba_houses = [sun_house] if same_sign and sun_house else ([h for h in (sun_house, merc_house) if h])
        is_combust = ctx.is_combust("Mercury")

        ba_conditions.append(
            YogaConditionItem(
                condition="Sun and Mercury occupy the same sign/house (Yuti)",
                passed=same_sign,
                detail=(
                    f"Sun in {SIGN_NAMES_EN[sun_sign]} (House {sun_house}) and "
                    f"Mercury in {SIGN_NAMES_EN[merc_sign]} (House {merc_house})."
                )
            )
        )
        ba_conditions.append(
            YogaConditionItem(
                condition="Combustion dignity assessment",
                passed=not is_combust,
                detail=(
                    "Mercury is within combustion orb of Sun (can modify pure expression)."
                    if is_combust else "Mercury is beyond combustion orb, expressing sharp intellect."
                )
            )
        )
        ba_qualifies = same_sign
    else:
        ba_conditions.append(
            YogaConditionItem(
                condition="Sun and Mercury positions available",
                passed=False,
                detail="Sun or Mercury data missing."
            )
        )

    results.append(
        YogaDetail(
            id="budha_aditya_yoga",
            name="Budha-Aditya Yoga",
            name_tamil="புதாதித்ய யோகம்",
            category="Major Classical",
            status="Qualifying" if ba_qualifies else "Not Qualifying",
            is_qualifying=ba_qualifies,
            planets_involved=["Sun", "Mercury"],
            relevant_houses=ba_houses,
            conditions=ba_conditions,
            short_interpretation="Sharp analytical intellect, skill in communication, leadership, and professional respect.",
            classical_definition="Sun and Mercury conjoin in the same sign / bhava.",
            classical_reference="Brihat Parashara Hora Shastra; Saravali; 300 Important Combinations #41",
            verification_status="Verified"
        )
    )

    # 3. Chandra-Mangala Yoga
    # Moon and Mars conjunct in the same sign
    moon_sign = ctx.planet_sign.get("Moon")
    mars_sign = ctx.planet_sign.get("Mars")
    mars_house = ctx.planet_house.get("Mars")
    cm_conditions: List[YogaConditionItem] = []
    cm_qualifies = False
    cm_houses = []

    if moon_sign and mars_sign:
        same_sign = (moon_sign == mars_sign)
        cm_houses = [moon_house] if same_sign and moon_house else ([h for h in (moon_house, mars_house) if h])

        cm_conditions.append(
            YogaConditionItem(
                condition="Moon and Mars occupy the same sign/house (Yuti)",
                passed=same_sign,
                detail=(
                    f"Moon in {SIGN_NAMES_EN[moon_sign]} (House {moon_house}) and "
                    f"Mars in {SIGN_NAMES_EN[mars_sign]} (House {mars_house})."
                )
            )
        )
        cm_qualifies = same_sign
    else:
        cm_conditions.append(
            YogaConditionItem(
                condition="Moon and Mars positions available",
                passed=False,
                detail="Moon or Mars coordinate missing."
            )
        )

    results.append(
        YogaDetail(
            id="chandra_mangala_yoga",
            name="Chandra-Mangala Yoga",
            name_tamil="சந்திர மங்கள யோகம்",
            category="Dhana Yoga",
            status="Qualifying" if cm_qualifies else "Not Qualifying",
            is_qualifying=cm_qualifies,
            planets_involved=["Moon", "Mars"],
            relevant_houses=cm_houses,
            conditions=cm_conditions,
            short_interpretation="Earns wealth through enterprise, real estate, commerce, and relentless financial energy.",
            classical_definition="Moon and Mars conjoin in the same sign.",
            classical_reference="Brihat Parashara Hora Shastra; Phaladeepika Ch. 6, v. 14; 300 Important Combinations #43",
            verification_status="Corrected from Reference (classified as Dhana Yoga rather than negative)"
        )
    )

    # 4. PANCH MAHAPURUSHA YOGAS
    # 4.1 Ruchaka Yoga (Mars)
    # Mars in Kendra in Aries/Scorpio (own) or Capricorn (exalted)
    mars_kendra = ctx.is_in_kendra("Mars")
    mars_own = ctx.is_in_own_sign("Mars")
    mars_exalted = ctx.is_exalted("Mars")
    ruchaka_qualifies = mars_kendra and (mars_own or mars_exalted)

    results.append(
        YogaDetail(
            id="ruchaka_yoga",
            name="Ruchaka Yoga (Mahapurusha)",
            name_tamil="ருசக யோகம் (பஞ்ச மகாபுருஷ)",
            category="Panch Mahapurusha",
            status="Qualifying" if ruchaka_qualifies else "Not Qualifying",
            is_qualifying=ruchaka_qualifies,
            planets_involved=["Mars"],
            relevant_houses=[mars_house] if mars_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Mars occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=mars_kendra,
                    detail=f"Mars is in house {mars_house} ({'Kendra' if mars_kendra else 'Non-kendra'})."
                ),
                YogaConditionItem(
                    condition="Mars is in its own sign (Aries, Scorpio) or exaltation sign (Capricorn)",
                    passed=mars_own or mars_exalted,
                    detail=f"Mars sign is {SIGN_NAMES_EN.get(mars_sign, 'Unknown')} (Exalted: {mars_exalted}, Own: {mars_own})."
                )
            ],
            short_interpretation="Endows physical strength, military/executive authority, real estate prowess, courage, and leadership.",
            classical_definition="Mars occupies a Kendra from Lagna in its own or exaltation sign.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 75; Brihat Jataka Ch. 24; 300 Important Combinations #1",
            verification_status="Verified"
        )
    )

    # 4.2 Bhadra Yoga (Mercury)
    # Mercury in Kendra in Gemini (own) or Virgo (own/exalted)
    merc_kendra = ctx.is_in_kendra("Mercury")
    merc_own = ctx.is_in_own_sign("Mercury")
    merc_exalted = ctx.is_exalted("Mercury")
    bhadra_qualifies = merc_kendra and (merc_own or merc_exalted)

    results.append(
        YogaDetail(
            id="bhadra_yoga",
            name="Bhadra Yoga (Mahapurusha)",
            name_tamil="பத்ர யோகம் (பஞ்ச மகாபுருஷ)",
            category="Panch Mahapurusha",
            status="Qualifying" if bhadra_qualifies else "Not Qualifying",
            is_qualifying=bhadra_qualifies,
            planets_involved=["Mercury"],
            relevant_houses=[merc_house] if merc_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Mercury occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=merc_kendra,
                    detail=f"Mercury is in house {merc_house} ({'Kendra' if merc_kendra else 'Non-kendra'})."
                ),
                YogaConditionItem(
                    condition="Mercury is in its own sign (Gemini, Virgo) or exaltation sign (Virgo)",
                    passed=merc_own or merc_exalted,
                    detail=f"Mercury sign is {SIGN_NAMES_EN.get(merc_sign, 'Unknown')} (Exalted: {merc_exalted}, Own: {merc_own})."
                )
            ],
            short_interpretation="Bestows scholastic genius, mathematical agility, persuasive speech, administrative skill, and long life.",
            classical_definition="Mercury occupies a Kendra from Lagna in its own or exaltation sign.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 75; Brihat Jataka Ch. 24; 300 Important Combinations #2",
            verification_status="Verified"
        )
    )

    # 4.3 Hamsa Yoga (Jupiter)
    # Jupiter in Kendra in Sagittarius/Pisces (own) or Cancer (exalted)
    jup_sign = ctx.planet_sign.get("Jupiter")
    jup_kendra = ctx.is_in_kendra("Jupiter")
    jup_own = ctx.is_in_own_sign("Jupiter")
    jup_exalted = ctx.is_exalted("Jupiter")
    hamsa_qualifies = jup_kendra and (jup_own or jup_exalted)

    results.append(
        YogaDetail(
            id="hamsa_yoga",
            name="Hamsa Yoga (Mahapurusha)",
            name_tamil="ஹம்ச யோகம் (பஞ்ச மகாபுருஷ)",
            category="Panch Mahapurusha",
            status="Qualifying" if hamsa_qualifies else "Not Qualifying",
            is_qualifying=hamsa_qualifies,
            planets_involved=["Jupiter"],
            relevant_houses=[jup_house] if jup_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Jupiter occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=jup_kendra,
                    detail=f"Jupiter is in house {jup_house} ({'Kendra' if jup_kendra else 'Non-kendra'})."
                ),
                YogaConditionItem(
                    condition="Jupiter is in its own sign (Sagittarius, Pisces) or exaltation sign (Cancer)",
                    passed=jup_own or jup_exalted,
                    detail=f"Jupiter sign is {SIGN_NAMES_EN.get(jup_sign, 'Unknown')} (Exalted: {jup_exalted}, Own: {jup_own})."
                )
            ],
            short_interpretation="Graces the native with spiritual wisdom, righteous conduct, benevolence, reverence from peers, and prosperity.",
            classical_definition="Jupiter occupies a Kendra from Lagna in its own or exaltation sign.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 75; Brihat Jataka Ch. 24; 300 Important Combinations #3",
            verification_status="Verified"
        )
    )

    # 4.4 Malavya Yoga (Venus)
    # Venus in Kendra in Taurus/Libra (own) or Pisces (exalted)
    ven_sign = ctx.planet_sign.get("Venus")
    ven_house = ctx.planet_house.get("Venus")
    ven_kendra = ctx.is_in_kendra("Venus")
    ven_own = ctx.is_in_own_sign("Venus")
    ven_exalted = ctx.is_exalted("Venus")
    malavya_qualifies = ven_kendra and (ven_own or ven_exalted)

    results.append(
        YogaDetail(
            id="malavya_yoga",
            name="Malavya Yoga (Mahapurusha)",
            name_tamil="மாளவ்ய யோகம் (பஞ்ச மகாபுருஷ)",
            category="Panch Mahapurusha",
            status="Qualifying" if malavya_qualifies else "Not Qualifying",
            is_qualifying=malavya_qualifies,
            planets_involved=["Venus"],
            relevant_houses=[ven_house] if ven_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Venus occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=ven_kendra,
                    detail=f"Venus is in house {ven_house} ({'Kendra' if ven_kendra else 'Non-kendra'})."
                ),
                YogaConditionItem(
                    condition="Venus is in its own sign (Taurus, Libra) or exaltation sign (Pisces)",
                    passed=ven_own or ven_exalted,
                    detail=f"Venus sign is {SIGN_NAMES_EN.get(ven_sign, 'Unknown')} (Exalted: {ven_exalted}, Own: {ven_own})."
                )
            ],
            short_interpretation="Bestows aesthetic refinement, conveyances, domestic luxuries, artistic talent, and magnetic charisma.",
            classical_definition="Venus occupies a Kendra from Lagna in its own or exaltation sign.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 75; Brihat Jataka Ch. 24; 300 Important Combinations #4",
            verification_status="Verified"
        )
    )

    # 4.5 Shasha (Sasa) Yoga (Saturn)
    # Saturn in Kendra in Capricorn/Aquarius (own) or Libra (exalted)
    sat_sign = ctx.planet_sign.get("Saturn")
    sat_house = ctx.planet_house.get("Saturn")
    sat_kendra = ctx.is_in_kendra("Saturn")
    sat_own = ctx.is_in_own_sign("Saturn")
    sat_exalted = ctx.is_exalted("Saturn")
    sasa_qualifies = sat_kendra and (sat_own or sat_exalted)

    results.append(
        YogaDetail(
            id="sasa_yoga",
            name="Shasha (Sasa) Yoga (Mahapurusha)",
            name_tamil="சச யோகம் (பஞ்ச மகாபுருஷ)",
            category="Panch Mahapurusha",
            status="Qualifying" if sasa_qualifies else "Not Qualifying",
            is_qualifying=sasa_qualifies,
            planets_involved=["Saturn"],
            relevant_houses=[sat_house] if sat_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Saturn occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=sat_kendra,
                    detail=f"Saturn is in house {sat_house} ({'Kendra' if sat_kendra else 'Non-kendra'})."
                ),
                YogaConditionItem(
                    condition="Saturn is in its own sign (Capricorn, Aquarius) or exaltation sign (Libra)",
                    passed=sat_own or sat_exalted,
                    detail=f"Saturn sign is {SIGN_NAMES_EN.get(sat_sign, 'Unknown')} (Exalted: {sat_exalted}, Own: {sat_own})."
                )
            ],
            short_interpretation="Brings enduring power over masses, executive discipline, mastery of perseverance, and political or judicial influence.",
            classical_definition="Saturn occupies a Kendra from Lagna in its own or exaltation sign.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 75; Brihat Jataka Ch. 24; 300 Important Combinations #5",
            verification_status="Corrected from Reference (classified as Panch Mahapurusha Raja Yoga rather than negative)"
        )
    )

    # 5. Amala Yoga
    # Natural benefic (Mercury, Venus, Jupiter) occupying 10th from Lagna or Moon
    h10_lagna = 10
    h10_moon = count_houses_inclusive(1, count_houses_inclusive(1, moon_house) + 9) if moon_house else None
    # 10th from Moon = ((moon_house - 1 + 9) % 12) + 1
    h10_moon = (((moon_house - 1 + 9) % 12) + 1) if moon_house else None

    lagna_10_benefics = [p for p in ctx.house_occupants.get(10, []) if p in {"Jupiter", "Venus", "Mercury"}]
    moon_10_benefics = [p for p in ctx.house_occupants.get(h10_moon, []) if p in {"Jupiter", "Venus", "Mercury"}] if h10_moon else []

    amala_qualifies = bool(lagna_10_benefics or moon_10_benefics)
    amala_planets = list(set(lagna_10_benefics + moon_10_benefics))

    results.append(
        YogaDetail(
            id="amala_yoga",
            name="Amala Yoga",
            name_tamil="அமல யோகம்",
            category="Major Classical",
            status="Qualifying" if amala_qualifies else "Not Qualifying",
            is_qualifying=amala_qualifies,
            planets_involved=amala_planets if amala_planets else ["Jupiter", "Venus", "Mercury"],
            relevant_houses=[10] + ([h10_moon] if h10_moon and h10_moon != 10 else []),
            conditions=[
                YogaConditionItem(
                    condition="A natural benefic (Jupiter, Venus, Mercury) occupies the 10th house from Lagna",
                    passed=bool(lagna_10_benefics),
                    detail=f"Benefics in 10th from Lagna: {', '.join(lagna_10_benefics) if lagna_10_benefics else 'None'}."
                ),
                YogaConditionItem(
                    condition="A natural benefic occupies the 10th house from Moon",
                    passed=bool(moon_10_benefics),
                    detail=f"Benefics in 10th from Moon (House {h10_moon}): {', '.join(moon_10_benefics) if moon_10_benefics else 'None'}."
                )
            ],
            short_interpretation="Bestows spotless reputation, honourable career conduct, lasting social stature, and philanthropic prosperity.",
            classical_definition="The 10th house from Lagna or the 10th house from Moon is occupied by a natural benefic without malefic affliction.",
            classical_reference="Phaladeepika Ch. 6, v. 21; 300 Important Combinations #45",
            verification_status="Verified"
        )
    )

    # 6. Chatussagara Yoga
    # All four Kendras from Lagna or Moon are occupied by planets
    kendras_lagna_occupied = all(len(ctx.house_occupants.get(h, [])) > 0 for h in (1, 4, 7, 10))
    kendras_moon_houses = [(((moon_house - 1 + offset) % 12) + 1) for offset in (0, 3, 6, 9)] if moon_house else []
    kendras_moon_occupied = all(len(ctx.house_occupants.get(h, [])) > 0 for h in kendras_moon_houses) if kendras_moon_houses else False

    chat_qualifies = kendras_lagna_occupied or kendras_moon_occupied

    results.append(
        YogaDetail(
            id="chatussagara_yoga",
            name="Chatussagara Yoga",
            name_tamil="சதுஸாகர யோகம்",
            category="Major Classical",
            status="Qualifying" if chat_qualifies else "Not Qualifying",
            is_qualifying=chat_qualifies,
            planets_involved=[p for h in (1, 4, 7, 10) for p in ctx.house_occupants.get(h, [])],
            relevant_houses=[1, 4, 7, 10],
            conditions=[
                YogaConditionItem(
                    condition="All four Kendra houses (1, 4, 7, 10) from Lagna are occupied by grahas",
                    passed=kendras_lagna_occupied,
                    detail=f"Occupancies: 1:{ctx.house_occupants.get(1)}, 4:{ctx.house_occupants.get(4)}, 7:{ctx.house_occupants.get(7)}, 10:{ctx.house_occupants.get(10)}."
                ),
                YogaConditionItem(
                    condition="Alternative: All four Kendra houses from Moon are occupied by grahas",
                    passed=kendras_moon_occupied,
                    detail=f"Kendras from Moon ({kendras_moon_houses}) {'all occupied' if kendras_moon_occupied else 'not all occupied'}."
                )
            ],
            short_interpretation="Fame spreading across the four oceans; commanding sovereignty, strong offspring, long life, and comprehensive security.",
            classical_definition="All four angular houses (1, 4, 7, 10) from Lagna or Moon are occupied by planets.",
            classical_reference="Brihat Parashara Hora Shastra; 300 Important Combinations #24",
            verification_status="Verified"
        )
    )

    # 7. Maha Bhagya Yoga
    # Male born during day with Lagna, Sun, Moon all in odd signs;
    # Female born at night with Lagna, Sun, Moon all in even signs.
    lagna_sign = ctx.lagna_sign_idx
    lagna_is_odd = (lagna_sign % 2 == 1)
    sun_is_odd = bool(sun_sign and (sun_sign % 2 == 1))
    moon_is_odd = bool(moon_sign and (moon_sign % 2 == 1))

    male_qualifies = (ctx.gender == "male" and ctx.is_day_birth and lagna_is_odd and sun_is_odd and moon_is_odd)
    female_qualifies = (ctx.gender == "female" and not ctx.is_day_birth and not lagna_is_odd and not sun_is_odd and not moon_is_odd)
    mb_qualifies = male_qualifies or female_qualifies

    results.append(
        YogaDetail(
            id="maha_bhagya_yoga",
            name="Maha Bhagya Yoga",
            name_tamil="மகா பாக்ய யோகம்",
            category="Major Classical",
            status="Qualifying" if mb_qualifies else "Not Qualifying",
            is_qualifying=mb_qualifies,
            planets_involved=["Sun", "Moon"],
            relevant_houses=[h for h in (1, sun_house, moon_house) if h],
            conditions=[
                YogaConditionItem(
                    condition="Male daytime birth: Lagna, Sun, and Moon all situated in odd signs (1, 3, 5, 7, 9, 11)",
                    passed=male_qualifies,
                    detail=(
                        f"Gender: {ctx.gender}, Day Birth: {ctx.is_day_birth}; Signs: Lagna={SIGN_NAMES_EN.get(lagna_sign)} (Odd: {lagna_is_odd}), "
                        f"Sun={SIGN_NAMES_EN.get(sun_sign, 'Unknown')} (Odd: {sun_is_odd}), "
                        f"Moon={SIGN_NAMES_EN.get(moon_sign, 'Unknown')} (Odd: {moon_is_odd})."
                    )
                ),
                YogaConditionItem(
                    condition="Female nighttime birth: Lagna, Sun, and Moon all situated in even signs (2, 4, 6, 8, 10, 12)",
                    passed=female_qualifies,
                    detail=(
                        f"Gender: {ctx.gender}, Night Birth: {not ctx.is_day_birth}; Signs: Lagna={SIGN_NAMES_EN.get(lagna_sign)} (Even: {not lagna_is_odd}), "
                        f"Sun={SIGN_NAMES_EN.get(sun_sign, 'Unknown')} (Even: {not sun_is_odd}), "
                        f"Moon={SIGN_NAMES_EN.get(moon_sign, 'Unknown')} (Even: {not moon_is_odd})."
                    )
                )
            ],
            short_interpretation="Supreme auspicious fortune, noble lineage, royal benevolence, flawless character, and extensive prosperity.",
            classical_definition="Male born during daytime with Lagna, Sun, and Moon in odd signs; or female born at night with all three in even signs.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 19; 300 Important Combinations #44",
            verification_status="Verified"
        )
    )

    return results
