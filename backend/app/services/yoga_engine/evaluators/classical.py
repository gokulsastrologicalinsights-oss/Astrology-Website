"""Classical Major Vedic Yogas: Gajakesari, Budha-Aditya, Chandra-Mangala, Panch Mahapurusha, Amala, Maha Bhagya."""

from typing import List
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    count_houses_inclusive,
    KENDRA_HOUSES,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    get_nth_house,
    TRIKONA_HOUSES,
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


    # -------------------------------------------------------------
    # BPHS Ch. 36 Special Classical Yogas
    # -------------------------------------------------------------
    lagna_lord = ctx.house_lords.get(1)
    h2_lord = ctx.house_lords.get(2)
    h5_lord = ctx.house_lords.get(5)
    h6_lord = ctx.house_lords.get(6)
    h7_lord = ctx.house_lords.get(7)
    h9_lord = ctx.house_lords.get(9)
    h10_lord = ctx.house_lords.get(10)
    h11_lord = ctx.house_lords.get(11)
    h12_lord = ctx.house_lords.get(12)

    # 8. Parvata Yoga (BPHS Ch. 36, Slokas 33-34)
    kendra_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if ctx.planet_house.get(b) in {1, 4, 7, 10}]
    h6_occupants = ctx.house_occupants.get(6, [])
    h8_occupants = ctx.house_occupants.get(8, [])
    malefics_6_8 = [m for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") if m in h6_occupants or m in h8_occupants]
    parvata_cond_a = len(kendra_benefics) >= 2 and len(malefics_6_8) == 0
    parvata_cond_b = False
    if lagna_lord and h12_lord:
        ll_h = ctx.planet_house.get(lagna_lord)
        h12_h = ctx.planet_house.get(h12_lord)
        if ll_h and h12_h:
            parvata_cond_b = count_houses_inclusive(ll_h, h12_h) in {1, 4, 7, 10}
    parvata_qualifies = parvata_cond_a or parvata_cond_b

    results.append(
        YogaDetail(
            id="parvata_yoga",
            name="Parvata Yoga",
            name_tamil="பர்வத யோகம்",
            category="Major Classical",
            status="Qualifying" if parvata_qualifies else "Not Qualifying",
            is_qualifying=parvata_qualifies,
            planets_involved=kendra_benefics or ([lagna_lord, h12_lord] if lagna_lord and h12_lord else []),
            relevant_houses=[1, 4, 7, 10, 6, 8],
            conditions=[
                YogaConditionItem(
                    condition="Benefics occupy Kendras (1, 4, 7, 10) with 6th and 8th free from malefics; OR Lagna lord and 12th lord are in mutual Kendras",
                    passed=parvata_qualifies,
                    detail=f"Benefics in Kendras: {kendra_benefics}; Malefics in 6/8: {malefics_6_8}; Mutual Kendra L1/L12: {parvata_cond_b}."
                )
            ],
            short_interpretation="Immovable fortune, leadership of town or army, renowned eloquence, charitable nature, and high social standing.",
            classical_definition="Benefics in Kendras while 6th and 8th are unoccupied or occupied only by benefics; or Lagna lord and 12th lord in mutual Kendras.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Slokas 33-34; 300 Important Combinations #61",
            verification_status="Verified"
        )
    )

    # 9. Shankha Yoga (BPHS Ch. 36, Sloka 36)
    shankha_qualifies = False
    shankha_planets = []
    if h5_lord and h6_lord and lagna_lord:
        h5_pos = ctx.planet_house.get(h5_lord)
        h6_pos = ctx.planet_house.get(h6_lord)
        ll_strong = ctx.is_in_kendra(lagna_lord) or ctx.is_in_trikona(lagna_lord) or ctx.is_exalted(lagna_lord) or ctx.is_in_own_sign(lagna_lord)
        if h5_pos and h6_pos and ll_strong:
            shankha_qualifies = count_houses_inclusive(h5_pos, h6_pos) in {1, 4, 7, 10}
            shankha_planets = [lagna_lord, h5_lord, h6_lord]

    results.append(
        YogaDetail(
            id="shankha_yoga",
            name="Shankha Yoga",
            name_tamil="சங்க யோகம்",
            category="Major Classical",
            status="Qualifying" if shankha_qualifies else "Not Qualifying",
            is_qualifying=shankha_qualifies,
            planets_involved=shankha_planets,
            relevant_houses=[ctx.planet_house.get(p) for p in shankha_planets if ctx.planet_house.get(p)],
            conditions=[
                YogaConditionItem(
                    condition="5th lord and 6th lord in mutual Kendras with Lagna lord possessing strength (in Kendra/Trikona or dignified)",
                    passed=shankha_qualifies,
                    detail=f"5th Lord ({h5_lord}) and 6th Lord ({h6_lord}) mutual Kendra disposition with strong Lagna Lord ({lagna_lord})."
                )
            ],
            short_interpretation="Blessed with devoted spouse and children, righteous conduct, profound scriptural knowledge, and lasting wealth.",
            classical_definition="5th lord and 6th lord in mutual Kendras while the lord of Lagna is strong.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 36; 300 Important Combinations #65",
            verification_status="Verified"
        )
    )

    # 10. Bheri Yoga (BPHS Ch. 36, Sloka 37)
    bheri_qualifies = False
    bheri_planets = []
    if h9_lord and lagna_lord:
        h9_strong = ctx.is_in_kendra(h9_lord) or ctx.is_in_trikona(h9_lord) or ctx.is_exalted(h9_lord) or ctx.is_in_own_sign(h9_lord)
        jup_k = ctx.is_in_kendra("Jupiter")
        ven_k = ctx.is_in_kendra("Venus")
        ll_k = ctx.is_in_kendra(lagna_lord)
        bheri_qualifies = bool(h9_strong and jup_k and ven_k and ll_k)
        if bheri_qualifies:
            bheri_planets = ["Jupiter", "Venus", lagna_lord, h9_lord]

    results.append(
        YogaDetail(
            id="bheri_yoga",
            name="Bheri Yoga",
            name_tamil="பேரி யோகம்",
            category="Major Classical",
            status="Qualifying" if bheri_qualifies else "Not Qualifying",
            is_qualifying=bheri_qualifies,
            planets_involved=bheri_planets,
            relevant_houses=[1, 4, 7, 10],
            conditions=[
                YogaConditionItem(
                    condition="9th lord strong, and Jupiter, Venus, and Lagna lord occupy Kendra houses (1, 4, 7, 10)",
                    passed=bheri_qualifies,
                    detail=f"9th Lord ({h9_lord}) strong; Jupiter, Venus, Lagna Lord ({lagna_lord}) in Kendras."
                )
            ],
            short_interpretation="Long-lived, of noble renown, prosperous with vehicles and estates, heroic in nature and surrounded by devoted relatives.",
            classical_definition="Lord of 9th is strong, and Jupiter, Venus, and Lagna lord occupy Kendras.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 37; 300 Important Combinations #66",
            verification_status="Verified"
        )
    )

    # 11. Mridanga Yoga (BPHS Ch. 36, Sloka 38)
    ll_strong = lagna_lord and (ctx.is_in_kendra(lagna_lord) or ctx.is_in_trikona(lagna_lord) or ctx.is_exalted(lagna_lord) or ctx.is_in_own_sign(lagna_lord))
    strong_kendra_trikona_planets = [
        p for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        if (ctx.is_in_kendra(p) or ctx.is_in_trikona(p)) and (ctx.is_exalted(p) or ctx.is_in_own_sign(p)) and p != lagna_lord
    ]
    mridanga_qualifies = bool(ll_strong and len(strong_kendra_trikona_planets) >= 2)

    results.append(
        YogaDetail(
            id="mridanga_yoga",
            name="Mridanga Yoga",
            name_tamil="மிருதங்க யோகம்",
            category="Major Classical",
            status="Qualifying" if mridanga_qualifies else "Not Qualifying",
            is_qualifying=mridanga_qualifies,
            planets_involved=([lagna_lord] if lagna_lord else []) + strong_kendra_trikona_planets,
            relevant_houses=[ctx.planet_house.get(p) for p in strong_kendra_trikona_planets if ctx.planet_house.get(p)],
            conditions=[
                YogaConditionItem(
                    condition="Lagna lord strong, and 2 or more grahas placed in Kendras or Trikonas in exaltation or own signs",
                    passed=mridanga_qualifies,
                    detail=f"Lagna lord strong: {bool(ll_strong)}; Dignified planets in Kendra/Trikona: {strong_kendra_trikona_planets}."
                )
            ],
            short_interpretation="Commanding executive authority, regal honors, artistic elegance, boundless happiness, and lasting legacy.",
            classical_definition="Lagna lord strong and other planets occupy Kendras/Trikonas in exaltation or own signs.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 38; 300 Important Combinations #67",
            verification_status="Verified"
        )
    )

    # 12. Shrinatha Yoga (BPHS Ch. 36, Sloka 39)
    shrinatha_qualifies = False
    shrinatha_planets = []
    if h7_lord and h10_lord and h9_lord:
        h7_in_10 = (ctx.planet_house.get(h7_lord) == 10)
        h10_exalted = ctx.is_exalted(h10_lord)
        h10_conj_h9 = ctx.are_conjoined(h10_lord, h9_lord)
        shrinatha_qualifies = bool(h7_in_10 and h10_exalted and h10_conj_h9)
        if shrinatha_qualifies:
            shrinatha_planets = [h7_lord, h10_lord, h9_lord]

    results.append(
        YogaDetail(
            id="shrinatha_yoga",
            name="Shrinatha Yoga",
            name_tamil="ஸ்ரீநாத யோகம்",
            category="Major Classical",
            status="Qualifying" if shrinatha_qualifies else "Not Qualifying",
            is_qualifying=shrinatha_qualifies,
            planets_involved=shrinatha_planets,
            relevant_houses=[10],
            conditions=[
                YogaConditionItem(
                    condition="7th lord in 10th house, and 10th lord exalted and conjoined with 9th lord",
                    passed=shrinatha_qualifies,
                    detail=f"7th lord ({h7_lord}) in 10th, 10th lord ({h10_lord}) exalted conjoined 9th lord ({h9_lord})."
                )
            ],
            short_interpretation="Endowed with marks of Vishnu, blessed with noble spouse, regal speech, enormous fame, and divine benevolence.",
            classical_definition="The 7th lord is placed in the 10th house, and the 10th lord is exalted and conjoined with the 9th lord.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 39; 300 Important Combinations #68",
            verification_status="Verified"
        )
    )

    # 13. Sharada Yoga (BPHS Ch. 36, Sloka 40)
    sharada_qualifies = False
    sharada_planets = []
    if h10_lord:
        h10_in_5 = (ctx.planet_house.get(h10_lord) == 5)
        merc_k = ctx.is_in_kendra("Mercury")
        sun_in_leo = (ctx.planet_sign.get("Sun") == 5)
        sharada_qualifies = bool(h10_in_5 and merc_k and sun_in_leo)
        if sharada_qualifies:
            sharada_planets = [h10_lord, "Mercury", "Sun"]

    results.append(
        YogaDetail(
            id="sharada_yoga",
            name="Sharada Yoga",
            name_tamil="சாரதா யோகம்",
            category="Major Classical",
            status="Qualifying" if sharada_qualifies else "Not Qualifying",
            is_qualifying=sharada_qualifies,
            planets_involved=sharada_planets,
            relevant_houses=[5, ctx.planet_house.get("Mercury", 0)],
            conditions=[
                YogaConditionItem(
                    condition="10th lord in 5th house, Mercury in Kendra, and Sun in Leo (own sign)",
                    passed=sharada_qualifies,
                    detail=f"10th lord ({h10_lord}) in 5th; Mercury in Kendra ({ctx.planet_house.get('Mercury')}); Sun in Leo ({sun_in_leo})."
                )
            ],
            short_interpretation="Blessed by Goddess Sharada (Saraswati); distinguished scholarship, righteous progeny, artistic genius, and kingly favors.",
            classical_definition="The 10th lord occupies the 5th house, Mercury is in a Kendra, and the Sun is in own sign Leo.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 40; 300 Important Combinations #69",
            verification_status="Verified"
        )
    )

    # 14. Matsya Yoga (BPHS Ch. 36, Sloka 41)
    benefics_1_9 = all(any(b in ctx.house_occupants.get(h, []) for b in ("Jupiter", "Venus", "Mercury")) for h in (1, 9))
    malefics_4_8 = all(any(m in ctx.house_occupants.get(h, []) for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")) for h in (4, 8))
    matsya_qualifies = benefics_1_9 and malefics_4_8

    results.append(
        YogaDetail(
            id="matsya_yoga",
            name="Matsya Yoga",
            name_tamil="மத்ஸ்ய யோகம்",
            category="Major Classical",
            status="Qualifying" if matsya_qualifies else "Not Qualifying",
            is_qualifying=matsya_qualifies,
            planets_involved=[p for h in (1, 9, 4, 8) for p in ctx.house_occupants.get(h, [])],
            relevant_houses=[1, 9, 4, 8],
            conditions=[
                YogaConditionItem(
                    condition="Natural benefics occupy 1st and 9th houses, while malefics occupy 4th and 8th houses",
                    passed=matsya_qualifies,
                    detail=f"Benefics in 1/9: {benefics_1_9}; Malefics in 4/8: {malefics_4_8}."
                )
            ],
            short_interpretation="Compassionate, wise, oceanic thinker, celebrated astrologer or occult scholar, blessed with wealth and religious devotion.",
            classical_definition="Benefics in 1st and 9th houses, while malefics occupy 4th and 8th houses.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 41; 300 Important Combinations #70",
            verification_status="Verified"
        )
    )

    # 15. Kurma Yoga (BPHS Ch. 36, Sloka 42)
    benefics_5_6_7 = all(any(b in ctx.house_occupants.get(h, []) for b in ("Jupiter", "Venus", "Mercury")) for h in (5, 6, 7))
    benefics_1_3_11 = all(any(b in ctx.house_occupants.get(h, []) and (ctx.is_exalted(b) or ctx.is_in_own_sign(b)) for b in ("Jupiter", "Venus", "Mercury")) for h in (1, 3, 11))
    kurma_qualifies = benefics_5_6_7 or benefics_1_3_11

    results.append(
        YogaDetail(
            id="kurma_yoga",
            name="Kurma Yoga",
            name_tamil="கூர்ம யோகம்",
            category="Major Classical",
            status="Qualifying" if kurma_qualifies else "Not Qualifying",
            is_qualifying=kurma_qualifies,
            planets_involved=[p for h in (5, 6, 7, 1, 3, 11) for p in ctx.house_occupants.get(h, [])],
            relevant_houses=[5, 6, 7] if benefics_5_6_7 else [1, 3, 11],
            conditions=[
                YogaConditionItem(
                    condition="Benefics occupy 5th, 6th, and 7th houses; OR benefics occupy 1st, 3rd, and 11th in own/exalted signs",
                    passed=kurma_qualifies,
                    detail=f"Benefics in 5/6/7: {benefics_5_6_7}; Benefics dignified in 1/3/11: {benefics_1_3_11}."
                )
            ],
            short_interpretation="Unshakable stability, sovereign administrator, protector of many, principled conduct, and sustained lifelong prominence.",
            classical_definition="Benefics occupy 5th, 6th, and 7th houses, or benefics occupy 1st, 3rd, and 11th in own or exaltation signs.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 42; 300 Important Combinations #71",
            verification_status="Verified"
        )
    )

    # 16. Khadga Yoga (BPHS Ch. 36, Sloka 43)
    khadga_qualifies = False
    khadga_planets = []
    if h2_lord and h9_lord and lagna_lord:
        h2_in_9 = (ctx.planet_house.get(h2_lord) == 9)
        h9_in_2 = (ctx.planet_house.get(h9_lord) == 2)
        ll_in_kt = ctx.is_in_kendra(lagna_lord) or ctx.is_in_trikona(lagna_lord)
        khadga_qualifies = bool(h2_in_9 and h9_in_2 and ll_in_kt)
        if khadga_qualifies:
            khadga_planets = [lagna_lord, h2_lord, h9_lord]

    results.append(
        YogaDetail(
            id="khadga_yoga",
            name="Khadga Yoga",
            name_tamil="கட்க யோகம்",
            category="Major Classical",
            status="Qualifying" if khadga_qualifies else "Not Qualifying",
            is_qualifying=khadga_qualifies,
            planets_involved=khadga_planets,
            relevant_houses=[2, 9, ctx.planet_house.get(lagna_lord, 1)],
            conditions=[
                YogaConditionItem(
                    condition="Exchange (Parivartana) between 2nd lord and 9th lord with Lagna lord placed in Kendra or Trikona",
                    passed=khadga_qualifies,
                    detail=f"2nd lord ({h2_lord}) in 9th, 9th lord ({h9_lord}) in 2nd, Lagna lord ({lagna_lord}) in Kendra/Trikona."
                )
            ],
            short_interpretation="Wielder of the sword of wisdom and sovereignty; wealthy, grateful, courageous, and victorious over rivals.",
            classical_definition="2nd lord in 9th, 9th lord in 2nd (Parivartana), and Lagna lord in Kendra or Trikona.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 43; 300 Important Combinations #73",
            verification_status="Verified"
        )
    )

    # 17. Kusuma Yoga (BPHS Ch. 36, Sloka 44)
    ven_in_k = ctx.is_in_kendra("Venus")
    moon_in_t = ctx.is_in_trikona("Moon")
    sat_in_10 = (ctx.planet_house.get("Saturn") == 10)
    kusuma_qualifies = bool(ven_in_k and moon_in_t and sat_in_10)

    results.append(
        YogaDetail(
            id="kusuma_yoga",
            name="Kusuma Yoga",
            name_tamil="குசும யோகம்",
            category="Major Classical",
            status="Qualifying" if kusuma_qualifies else "Not Qualifying",
            is_qualifying=kusuma_qualifies,
            planets_involved=["Venus", "Moon", "Saturn"],
            relevant_houses=[ctx.planet_house.get("Venus", 0), ctx.planet_house.get("Moon", 0), 10],
            conditions=[
                YogaConditionItem(
                    condition="Venus occupies a Kendra (1, 4, 7, 10), Moon in a Trikona (1, 5, 9), and Saturn occupies the 10th house",
                    passed=kusuma_qualifies,
                    detail=f"Venus in Kendra: {ven_in_k}; Moon in Trikona: {moon_in_t}; Saturn in 10th: {sat_in_10}."
                )
            ],
            short_interpretation="Flowering reputation, political minister or sovereign leader, artistic celebrations, unmatched generosity and wealth.",
            classical_definition="Venus in a Kendra, Moon in a Trikona, and Saturn in the 10th house.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 44; 300 Important Combinations #74",
            verification_status="Verified"
        )
    )

    # 18. Kalanidhi Yoga (BPHS Ch. 36, Sloka 45)
    jup_h = ctx.planet_house.get("Jupiter")
    kalanidhi_qualifies = False
    if jup_h in {2, 5}:
        merc_connects = ctx.are_conjoined("Jupiter", "Mercury") or ctx.planet_aspects_planet("Mercury", "Jupiter")
        ven_connects = ctx.are_conjoined("Jupiter", "Venus") or ctx.planet_aspects_planet("Venus", "Jupiter")
        kalanidhi_qualifies = bool(merc_connects and ven_connects)

    results.append(
        YogaDetail(
            id="kalanidhi_yoga",
            name="Kalanidhi Yoga",
            name_tamil="கலாநிதி யோகம்",
            category="Major Classical",
            status="Qualifying" if kalanidhi_qualifies else "Not Qualifying",
            is_qualifying=kalanidhi_qualifies,
            planets_involved=["Jupiter", "Mercury", "Venus"],
            relevant_houses=[jup_h] if jup_h else [2, 5],
            conditions=[
                YogaConditionItem(
                    condition="Jupiter occupies the 2nd or 5th house, joined or aspected by both Mercury and Venus",
                    passed=kalanidhi_qualifies,
                    detail=f"Jupiter in house {jup_h}; Mercury & Venus aspecting/conjoining Jupiter: {kalanidhi_qualifies}."
                )
            ],
            short_interpretation="Treasure-house of arts and wisdom; celebrated by kings, virtuous character, spotless speech, and radiant health.",
            classical_definition="Jupiter in the 2nd or 5th house conjoined or aspected by Mercury and Venus.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 45; 300 Important Combinations #75",
            verification_status="Verified"
        )
    )

    # 19. Kalpadruma Yoga (BPHS Ch. 36, Sloka 32)
    kalpadruma_qualifies = False
    if lagna_lord:
        ll_sign = ctx.planet_sign.get(lagna_lord)
        disp1 = SIGN_LORDS.get(ll_sign) if ll_sign else None
        disp1_sign = ctx.planet_sign.get(disp1) if disp1 else None
        disp2 = SIGN_LORDS.get(disp1_sign) if disp1_sign else None
        if disp1 and disp2:
            disp1_ok = ctx.is_in_kendra(disp1) or ctx.is_in_trikona(disp1) or ctx.is_exalted(disp1)
            disp2_ok = ctx.is_in_kendra(disp2) or ctx.is_in_trikona(disp2) or ctx.is_exalted(disp2)
            ll_ok = ctx.is_in_kendra(lagna_lord) or ctx.is_in_trikona(lagna_lord) or ctx.is_exalted(lagna_lord)
            kalpadruma_qualifies = bool(ll_ok and disp1_ok and disp2_ok)

    results.append(
        YogaDetail(
            id="kalpadruma_yoga",
            name="Kalpadruma Yoga",
            name_tamil="கல்பத்ரும யோகம்",
            category="Major Classical",
            status="Qualifying" if kalpadruma_qualifies else "Not Qualifying",
            is_qualifying=kalpadruma_qualifies,
            planets_involved=[lagna_lord] if lagna_lord else [],
            relevant_houses=[1, 4, 7, 10, 5, 9],
            conditions=[
                YogaConditionItem(
                    condition="Lagna lord, its dispositor, and the dispositor's dispositor are all placed in Kendras/Trikonas or exalted",
                    passed=kalpadruma_qualifies,
                    detail=f"Kalpadruma dispositor lineage strong: {kalpadruma_qualifies}."
                )
            ],
            short_interpretation="Celestial wish-fulfilling tree; sovereign leader, universal philanthropist, conquering all obstacles and desires.",
            classical_definition="Lagna lord, its dispositor, and that dispositor's dispositor occupy Kendras/Trikonas or exaltation signs.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 32; 300 Important Combinations #60",
            verification_status="Verified"
        )
    )

    # 20. Hari Yoga (BPHS Ch. 36, Slokas 28-29)
    hari_qualifies = False
    if h2_lord:
        h2_lord_pos = ctx.planet_house.get(h2_lord)
        if h2_lord_pos:
            b_houses = {get_nth_house(h2_lord_pos, n) for n in (2, 12, 8)}
            hari_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if ctx.planet_house.get(b) in b_houses]
            hari_qualifies = len(hari_benefics) >= 2

    results.append(
        YogaDetail(
            id="hari_yoga",
            name="Hari Yoga",
            name_tamil="ஹரி யோகம்",
            category="Major Classical",
            status="Qualifying" if hari_qualifies else "Not Qualifying",
            is_qualifying=hari_qualifies,
            planets_involved=[h2_lord] if h2_lord else [],
            relevant_houses=[ctx.planet_house.get(h2_lord, 2)],
            conditions=[
                YogaConditionItem(
                    condition="Natural benefics occupy 2nd, 12th, and 8th houses counted from the 2nd lord",
                    passed=hari_qualifies,
                    detail=f"Benefics in 2nd, 12th, 8th from 2nd Lord ({h2_lord}): {hari_qualifies}."
                )
            ],
            short_interpretation="Devotee of Lord Hari (Vishnu), immensely wealthy, sweet and persuasive speech, happy and righteous demeanor.",
            classical_definition="Benefics placed in 2nd, 12th, and 8th houses from the 2nd lord.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Slokas 28-29; 300 Important Combinations #58",
            verification_status="Verified"
        )
    )

    # 21. Hara Yoga (BPHS Ch. 36, Slokas 30-31)
    hara_qualifies = False
    if h7_lord:
        h7_lord_pos = ctx.planet_house.get(h7_lord)
        if h7_lord_pos:
            b_houses_hara = {get_nth_house(h7_lord_pos, n) for n in (4, 9, 8)}
            hara_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if ctx.planet_house.get(b) in b_houses_hara]
            hara_qualifies = len(hara_benefics) >= 2

    results.append(
        YogaDetail(
            id="hara_yoga",
            name="Hara Yoga",
            name_tamil="ஹர யோகம்",
            category="Major Classical",
            status="Qualifying" if hara_qualifies else "Not Qualifying",
            is_qualifying=hara_qualifies,
            planets_involved=[h7_lord] if h7_lord else [],
            relevant_houses=[ctx.planet_house.get(h7_lord, 7)],
            conditions=[
                YogaConditionItem(
                    condition="Natural benefics occupy 4th, 9th, and 8th houses counted from the 7th lord",
                    passed=hara_qualifies,
                    detail=f"Benefics in 4th, 9th, 8th from 7th Lord ({h7_lord}): {hara_qualifies}."
                )
            ],
            short_interpretation="Devotee of Lord Shiva (Hara), victorious in contests, fearless, spiritually enlightened and blessed with royal status.",
            classical_definition="Benefics placed in 4th, 9th, and 8th houses from the 7th lord.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Slokas 30-31; 300 Important Combinations #59",
            verification_status="Verified"
        )
    )

    # 22. Brahma Yoga (BPHS Ch. 36, Sloka 27)
    brahma_qualifies = False
    if h9_lord and h11_lord:
        h9_pos = ctx.planet_house.get(h9_lord)
        h11_pos = ctx.planet_house.get(h11_lord)
        jup_pos = ctx.planet_house.get("Jupiter")
        ven_pos = ctx.planet_house.get("Venus")
        if h9_pos and h11_pos and jup_pos and ven_pos:
            jup_from_9 = count_houses_inclusive(h9_pos, jup_pos) in {1, 4, 7, 10}
            ven_from_11 = count_houses_inclusive(h11_pos, ven_pos) in {1, 4, 7, 10}
            jup_ven_kendra = (jup_pos in {1, 4, 7, 10}) or (ven_pos in {1, 4, 7, 10})
            brahma_qualifies = bool(jup_from_9 and ven_from_11 and jup_ven_kendra)

    results.append(
        YogaDetail(
            id="brahma_yoga",
            name="Brahma Yoga",
            name_tamil="பிரம்ம யோகம்",
            category="Major Classical",
            status="Qualifying" if brahma_qualifies else "Not Qualifying",
            is_qualifying=brahma_qualifies,
            planets_involved=["Jupiter", "Venus", "Mercury"],
            relevant_houses=[ctx.planet_house.get("Jupiter", 0), ctx.planet_house.get("Venus", 0)],
            conditions=[
                YogaConditionItem(
                    condition="Jupiter in Kendra from 9th lord, Venus in Kendra from 11th lord, and Jupiter/Venus in Kendra from Lagna",
                    passed=brahma_qualifies,
                    detail=f"Jupiter Kendra from 9th lord, Venus Kendra from 11th lord: {brahma_qualifies}."
                )
            ],
            short_interpretation="Supreme intellect, long life, revered by kings and sacred scholars, virtuous deeds, and profound wisdom.",
            classical_definition="Jupiter in a Kendra from 9th lord, Venus in a Kendra from 11th lord, and Jupiter/Venus in Kendras from Lagna.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36, Sloka 27; 300 Important Combinations #57",
            verification_status="Verified"
        )
    )

    return results
