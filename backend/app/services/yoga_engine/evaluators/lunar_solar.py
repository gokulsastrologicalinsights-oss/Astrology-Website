"""Lunar, Solar, and Classical Avayogas: Sunapha, Anapha, Dhurdhura, Kemadruma (with Bhanga), Vesi, Vasi, Obhayachari, Adhi, Dur, Daridra, and Sakata."""

from typing import List
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    count_houses_inclusive,
    get_nth_house,
    KENDRA_HOUSES,
    DUSTHANA_HOUSES,
    SIGN_NAMES_EN,
)

VALID_LUNAR_GRAHAS = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
VALID_SOLAR_GRAHAS = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}


def evaluate_lunar_solar_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    results: List[YogaDetail] = []
    moon_house = ctx.planet_house.get("Moon")
    sun_house = ctx.planet_house.get("Sun")
    jup_house = ctx.planet_house.get("Jupiter")

    # -------------------------------------------------------------
    # 1. Sunapha, Anapha, Dhurdhura Yogas
    # -------------------------------------------------------------
    h2_moon = get_nth_house(moon_house, 2) if moon_house else None
    h12_moon = get_nth_house(moon_house, 12) if moon_house else None

    p_in_2_moon = [p for p in ctx.house_occupants.get(h2_moon, []) if p in VALID_LUNAR_GRAHAS] if h2_moon else []
    p_in_12_moon = [p for p in ctx.house_occupants.get(h12_moon, []) if p in VALID_LUNAR_GRAHAS] if h12_moon else []

    # 1.1 Sunapha Yoga
    sunapha_qualifies = bool(p_in_2_moon)
    results.append(
        YogaDetail(
            id="sunapha_yoga",
            name="Sunapha Yoga",
            name_tamil="சுனாபா யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if sunapha_qualifies else "Not Qualifying",
            is_qualifying=sunapha_qualifies,
            planets_involved=p_in_2_moon if p_in_2_moon else ["Moon"],
            relevant_houses=[h for h in (moon_house, h2_moon) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Sun, Rahu, and Ketu occupy the 2nd house from Moon",
                    passed=sunapha_qualifies,
                    detail=f"Planets in 2nd from Moon (House {h2_moon}): {', '.join(p_in_2_moon) if p_in_2_moon else 'None'}."
                )
            ],
            short_interpretation="Self-earned wealth, intellectual sharp judgment, prosperous conveyances, and honorable social status.",
            classical_definition="Planets other than Sun, Rahu, or Ketu are situated in the 2nd house from Moon.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 5; 300 Important Combinations #6",
            verification_status="Corrected from Reference (strictly excludes Rahu/Ketu)"
        )
    )

    # 1.2 Anapha Yoga
    anapha_qualifies = bool(p_in_12_moon)
    results.append(
        YogaDetail(
            id="anapha_yoga",
            name="Anapha Yoga",
            name_tamil="அனபா யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if anapha_qualifies else "Not Qualifying",
            is_qualifying=anapha_qualifies,
            planets_involved=p_in_12_moon if p_in_12_moon else ["Moon"],
            relevant_houses=[h for h in (moon_house, h12_moon) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Sun, Rahu, and Ketu occupy the 12th house from Moon",
                    passed=anapha_qualifies,
                    detail=f"Planets in 12th from Moon (House {h12_moon}): {', '.join(p_in_12_moon) if p_in_12_moon else 'None'}."
                )
            ],
            short_interpretation="Generous virtues, physical well-being, polite manners, freedom from agony, and refined pleasures.",
            classical_definition="Planets other than Sun, Rahu, or Ketu are situated in the 12th house from Moon.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 6; 300 Important Combinations #7",
            verification_status="Corrected from Reference (strictly excludes Rahu/Ketu)"
        )
    )

    # 1.3 Dhurdhura Yoga
    dhurdhura_qualifies = bool(p_in_2_moon and p_in_12_moon)
    results.append(
        YogaDetail(
            id="dhurdhura_yoga",
            name="Dhurdhura Yoga",
            name_tamil="துருதுரா யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if dhurdhura_qualifies else "Not Qualifying",
            is_qualifying=dhurdhura_qualifies,
            planets_involved=list(set(p_in_2_moon + p_in_12_moon)) if dhurdhura_qualifies else ["Moon"],
            relevant_houses=[h for h in (moon_house, h2_moon, h12_moon) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Sun, Rahu, and Ketu occupy both the 2nd and 12th houses from Moon",
                    passed=dhurdhura_qualifies,
                    detail=f"2nd from Moon: {p_in_2_moon}; 12th from Moon: {p_in_12_moon}."
                )
            ],
            short_interpretation="Immense bounties of wealth, leadership over conveyances, steady financial security, and benevolence.",
            classical_definition="Planets other than Sun, Rahu, or Ketu occupy both flanks (2nd and 12th) of the Moon.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 7; 300 Important Combinations #8",
            verification_status="Verified"
        )
    )

    # -------------------------------------------------------------
    # 2. Kemadruma Yoga & Kemadruma Bhanga (Cancellation)
    # -------------------------------------------------------------
    # Kemadruma occurs when neither 2nd nor 12th from Moon is occupied by valid grahas
    has_kemadruma_formation = (len(p_in_2_moon) == 0 and len(p_in_12_moon) == 0)

    # Cancellation criteria per BPHS & Phaladeepika:
    # 1. Moon conjunct another planet (excl Sun, Rahu, Ketu)
    moon_conjoined = [p for p in ctx.house_occupants.get(moon_house, []) if p in VALID_LUNAR_GRAHAS]
    bhanga_c1 = len(moon_conjoined) > 0

    # 2. Planets occupy Kendras from Lagna
    planets_in_lagna_kendras = [
        p for h in KENDRA_HOUSES for p in ctx.house_occupants.get(h, []) if p in VALID_LUNAR_GRAHAS
    ]
    bhanga_c2 = len(planets_in_lagna_kendras) > 0

    # 3. Planets occupy Kendras from Moon
    kendra_moon_houses = [get_nth_house(moon_house, offset) for offset in (1, 4, 7, 10)] if moon_house else []
    planets_in_moon_kendras = [
        p for h in kendra_moon_houses for p in ctx.house_occupants.get(h, [])
        if p in VALID_LUNAR_GRAHAS and p != "Moon"
    ]
    bhanga_c3 = len(planets_in_moon_kendras) > 0

    # 4. Benefic aspect on Moon (Jupiter, Venus)
    bhanga_c4 = ctx.planet_aspects_planet("Jupiter", "Moon") or ctx.planet_aspects_planet("Venus", "Moon")

    is_kemadruma_cancelled = bhanga_c1 or bhanga_c2 or bhanga_c3 or bhanga_c4
    kemadruma_operative = has_kemadruma_formation and not is_kemadruma_cancelled

    bhanga_reasons = []
    if bhanga_c1: bhanga_reasons.append(f"Moon conjoined with {', '.join(moon_conjoined)}")
    if bhanga_c2: bhanga_reasons.append(f"Grahas in Kendras from Lagna ({', '.join(planets_in_lagna_kendras)})")
    if bhanga_c3: bhanga_reasons.append(f"Grahas in Kendras from Moon ({', '.join(planets_in_moon_kendras)})")
    if bhanga_c4: bhanga_reasons.append("Benefic drishti on Moon from Jupiter or Venus")

    cancellation_text = "; ".join(bhanga_reasons) if bhanga_reasons else None

    status_str = "Not Qualifying"
    if has_kemadruma_formation:
        status_str = "Cancelled" if is_kemadruma_cancelled else "Qualifying"

    results.append(
        YogaDetail(
            id="kemadruma_yoga",
            name="Kemadruma Yoga",
            name_tamil="கேமத்துரும யோகம்",
            category="Lunar/Solar",
            status=status_str,
            is_qualifying=kemadruma_operative,
            planets_involved=["Moon"],
            relevant_houses=[h for h in (moon_house, h2_moon, h12_moon) if h],
            conditions=[
                YogaConditionItem(
                    condition="Formation: 2nd and 12th houses from Moon are completely unoccupied by grahas (excl. Sun/nodes)",
                    passed=has_kemadruma_formation,
                    detail=f"Flanks of Moon (Houses {h2_moon} and {h12_moon}) contain no qualifying planets."
                ),
                YogaConditionItem(
                    condition="Classical Bhanga (Cancellation): Neutralized if planets are in Kendras or aspect Moon",
                    passed=not is_kemadruma_cancelled,
                    detail=f"Cancellation active: {cancellation_text}" if is_kemadruma_cancelled else "No cancellation found."
                )
            ],
            short_interpretation=(
                "Adverse loneliness and financial trials when operative; completely neutralized by Kemadruma Bhanga into prosperity."
                if not kemadruma_operative else
                "Isolation, fluctuations in livelihood, and periods of dependency; remedies and benefic aspects soften impacts."
            ),
            classical_definition="No planets occupy the 2nd or 12th from Moon. Cancelled if planets occupy Kendras from Lagna/Moon or benefics aspect Moon.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, verses 8-11; 300 Important Combinations #9",
            verification_status="Corrected from Reference (Fixed 1st vs 2nd house index bug and added classical Bhanga cancellation)",
            cancellation_reason=cancellation_text if is_kemadruma_cancelled else None
        )
    )

    # -------------------------------------------------------------
    # 3. Solar Yogas: Vesi, Vasi, Obhayachari
    # -------------------------------------------------------------
    h2_sun = get_nth_house(sun_house, 2) if sun_house else None
    h12_sun = get_nth_house(sun_house, 12) if sun_house else None

    p_in_2_sun = [p for p in ctx.house_occupants.get(h2_sun, []) if p in VALID_SOLAR_GRAHAS] if h2_sun else []
    p_in_12_sun = [p for p in ctx.house_occupants.get(h12_sun, []) if p in VALID_SOLAR_GRAHAS] if h12_sun else []

    # 3.1 Vesi Yoga
    vesi_qualifies = bool(p_in_2_sun)
    results.append(
        YogaDetail(
            id="vesi_yoga",
            name="Vesi Yoga",
            name_tamil="வேசி யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if vesi_qualifies else "Not Qualifying",
            is_qualifying=vesi_qualifies,
            planets_involved=p_in_2_sun if p_in_2_sun else ["Sun"],
            relevant_houses=[h for h in (sun_house, h2_sun) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Moon, Rahu, and Ketu occupy the 2nd house from Sun",
                    passed=vesi_qualifies,
                    detail=f"Planets in 2nd from Sun (House {h2_sun}): {', '.join(p_in_2_sun) if p_in_2_sun else 'None'}."
                )
            ],
            short_interpretation="Fortunate speech, steady economic accumulation, honorable stature, and dignified demeanor.",
            classical_definition="Planets other than Moon, Rahu, or Ketu are placed in the 2nd house from Sun.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 1; 300 Important Combinations #11",
            verification_status="Verified"
        )
    )

    # 3.2 Vasi Yoga
    vasi_qualifies = bool(p_in_12_sun)
    results.append(
        YogaDetail(
            id="vasi_yoga",
            name="Vasi Yoga",
            name_tamil="வாசி யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if vasi_qualifies else "Not Qualifying",
            is_qualifying=vasi_qualifies,
            planets_involved=p_in_12_sun if p_in_12_sun else ["Sun"],
            relevant_houses=[h for h in (sun_house, h12_sun) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Moon, Rahu, and Ketu occupy the 12th house from Sun",
                    passed=vasi_qualifies,
                    detail=f"Planets in 12th from Sun (House {h12_sun}): {', '.join(p_in_12_sun) if p_in_12_sun else 'None'}."
                )
            ],
            short_interpretation="Skilled intellect, valorous enterprise, renowned learning, and royal favor.",
            classical_definition="Planets other than Moon, Rahu, or Ketu are placed in the 12th house from Sun.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 2; 300 Important Combinations #12",
            verification_status="Verified"
        )
    )

    # 3.3 Obhayachari Yoga
    obhaya_qualifies = bool(p_in_2_sun and p_in_12_sun)
    results.append(
        YogaDetail(
            id="obhayachari_yoga",
            name="Obhayachari Yoga",
            name_tamil="உபயசாரி யோகம்",
            category="Lunar/Solar",
            status="Qualifying" if obhaya_qualifies else "Not Qualifying",
            is_qualifying=obhaya_qualifies,
            planets_involved=list(set(p_in_2_sun + p_in_12_sun)) if obhaya_qualifies else ["Sun"],
            relevant_houses=[h for h in (sun_house, h2_sun, h12_sun) if h],
            conditions=[
                YogaConditionItem(
                    condition="Planets other than Moon, Rahu, and Ketu occupy both 2nd and 12th from Sun",
                    passed=obhaya_qualifies,
                    detail=f"2nd from Sun: {p_in_2_sun}; 12th from Sun: {p_in_12_sun}."
                )
            ],
            short_interpretation="Equal to a king, poised balance of speech and authority, eloquent, charming, and commanding immense respect.",
            classical_definition="Planets other than Moon occupy both sides (2nd and 12th) of the Sun.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 3; 300 Important Combinations #13",
            verification_status="Verified"
        )
    )

    # -------------------------------------------------------------
    # 4. Adhi Yoga (Chandradhi / Lagnadhi)
    # Natural benefics (Jupiter, Venus, Mercury) in 6, 7, 8 from Moon or Lagna
    # -------------------------------------------------------------
    benefics_list = ["Jupiter", "Venus", "Mercury"]
    h6_m = get_nth_house(moon_house, 6) if moon_house else None
    h7_m = get_nth_house(moon_house, 7) if moon_house else None
    h8_m = get_nth_house(moon_house, 8) if moon_house else None

    chandra_adhi_benefics = [
        p for p in benefics_list if ctx.planet_house.get(p) in {h6_m, h7_m, h8_m}
    ]
    lagna_adhi_benefics = [
        p for p in benefics_list if ctx.planet_house.get(p) in {6, 7, 8}
    ]

    chandra_adhi = len(chandra_adhi_benefics) >= 2
    lagna_adhi = len(lagna_adhi_benefics) >= 2
    adhi_qualifies = chandra_adhi or lagna_adhi

    results.append(
        YogaDetail(
            id="adhi_yoga",
            name="Adhi Yoga (Chandradhi / Lagnadhi)",
            name_tamil="அதி யோகம் (சந்திராதி / லக்னாதி)",
            category="Major Classical",
            status="Qualifying" if adhi_qualifies else "Not Qualifying",
            is_qualifying=adhi_qualifies,
            planets_involved=list(set(chandra_adhi_benefics + lagna_adhi_benefics)) if adhi_qualifies else benefics_list,
            relevant_houses=[h for h in (h6_m, h7_m, h8_m, 6, 7, 8) if h],
            conditions=[
                YogaConditionItem(
                    condition="Chandradhi: Natural benefics (Mercury, Venus, Jupiter) occupy 6th, 7th, or 8th from Moon",
                    passed=chandra_adhi,
                    detail=f"Benefics in 6,7,8 from Moon: {', '.join(chandra_adhi_benefics) if chandra_adhi_benefics else 'None'} ({len(chandra_adhi_benefics)}/3)."
                ),
                YogaConditionItem(
                    condition="Lagnadhi: Natural benefics occupy 6th, 7th, or 8th from Lagna",
                    passed=lagna_adhi,
                    detail=f"Benefics in 6,7,8 from Lagna: {', '.join(lagna_adhi_benefics) if lagna_adhi_benefics else 'None'} ({len(lagna_adhi_benefics)}/3)."
                )
            ],
            short_interpretation="Commander of forces, minister, luxurious affluence, triumph over rivals, and vibrant longevity.",
            classical_definition="Natural benefics occupy the 6th, 7th, and/or 8th houses from Moon or Lagna.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6, v. 20; 300 Important Combinations #39",
            verification_status="Corrected from Reference (Evaluates fractional strength instead of rigid impossible requirement)"
        )
    )

    # -------------------------------------------------------------
    # 5. Avayogas: Dur Yoga & Daridra Yoga
    # -------------------------------------------------------------
    # 5.1 Dur Yoga: 10th lord in 6, 8, 12
    l_10 = ctx.house_lords[10]
    h_l10 = ctx.planet_house.get(l_10)
    dur_qualifies = (h_l10 in DUSTHANA_HOUSES) if h_l10 else False

    results.append(
        YogaDetail(
            id="dur_yoga",
            name="Dur Yoga",
            name_tamil="துர் யோகம்",
            category="Avayoga",
            status="Qualifying" if dur_qualifies else "Not Qualifying",
            is_qualifying=dur_qualifies,
            planets_involved=[l_10],
            relevant_houses=[h_l10] if h_l10 else [],
            conditions=[
                YogaConditionItem(
                    condition="10th house lord occupies a Dusthana (6th, 8th, or 12th house)",
                    passed=dur_qualifies,
                    detail=f"10th Lord {l_10} occupies House {h_l10}."
                )
            ],
            short_interpretation="Efforts in public career or business face unacknowledged toil or obstacles; requires resilience and adaptability.",
            classical_definition="The lord of the 10th house is situated in the 6th, 8th, or 12th house from Lagna.",
            classical_reference="Phaladeepika Ch. 6, v. 58",
            verification_status="Verified"
        )
    )

    # 5.2 Daridra Yoga: 11th lord in 6, 8, 12
    l_11 = ctx.house_lords[11]
    h_l11 = ctx.planet_house.get(l_11)
    daridra_qualifies = (h_l11 in DUSTHANA_HOUSES) if h_l11 else False

    results.append(
        YogaDetail(
            id="daridra_yoga",
            name="Daridra Yoga",
            name_tamil="தரித்திர யோகம்",
            category="Avayoga",
            status="Qualifying" if daridra_qualifies else "Not Qualifying",
            is_qualifying=daridra_qualifies,
            planets_involved=[l_11],
            relevant_houses=[h_l11] if h_l11 else [],
            conditions=[
                YogaConditionItem(
                    condition="11th house lord occupies a Dusthana (6th, 8th, or 12th house)",
                    passed=daridra_qualifies,
                    detail=f"11th Lord {l_11} occupies House {h_l11}."
                )
            ],
            short_interpretation="Fluctuations in commercial gains, high financial drain, and unexpected liabilities; remedied by steady fiscal prudence.",
            classical_definition="The lord of the 11th house occupies the 6th, 8th, or 12th house from Lagna.",
            classical_reference="Phaladeepika Ch. 6, v. 68",
            verification_status="Verified"
        )
    )

    # 5.3 Sakata Yoga & Sakata Bhanga
    # Moon in 6, 8, 12 from Jupiter; cancelled if Moon in Kendra from Lagna
    dist_jup_to_moon = count_houses_inclusive(jup_house, moon_house) if (jup_house and moon_house) else None
    has_sakata_formation = dist_jup_to_moon in {6, 8, 12} if dist_jup_to_moon else False
    moon_in_lagna_kendra = moon_house in KENDRA_HOUSES if moon_house else False
    sakata_cancelled = moon_in_lagna_kendra
    sakata_operative = has_sakata_formation and not sakata_cancelled

    sakata_status = "Not Qualifying"
    if has_sakata_formation:
        sakata_status = "Cancelled" if sakata_cancelled else "Qualifying"

    results.append(
        YogaDetail(
            id="sakata_yoga",
            name="Sakata Yoga",
            name_tamil="சகட யோகம்",
            category="Avayoga",
            status=sakata_status,
            is_qualifying=sakata_operative,
            planets_involved=["Moon", "Jupiter"],
            relevant_houses=[h for h in (moon_house, jup_house) if h],
            conditions=[
                YogaConditionItem(
                    condition="Formation: Moon is in the 6th, 8th, or 12th house from Jupiter",
                    passed=has_sakata_formation,
                    detail=f"Moon is {dist_jup_to_moon}th from Jupiter (House {jup_house} to House {moon_house})."
                ),
                YogaConditionItem(
                    condition="Classical Bhanga (Cancellation): Neutralized if Moon occupies a Kendra (1, 4, 7, 10) from Lagna",
                    passed=not sakata_cancelled,
                    detail=f"Moon in House {moon_house} ({'In Lagna Kendra -> Sakata Cancelled' if moon_in_lagna_kendra else 'Not in Lagna Kendra'})."
                )
            ],
            short_interpretation=(
                "Cyclical wheel of fortune (ups and downs like a wheel cart); fully neutralized when Moon is in Kendra from Lagna."
                if not sakata_operative else
                "Fluctuations in wealth and status like a wheel cart; patient resilience restores lost fortune over time."
            ),
            classical_definition="Moon occupies the 6th, 8th, or 12th from Jupiter. Cancelled if Moon is in a Kendra from Lagna.",
            classical_reference="Phaladeepika Ch. 6, v. 56; 300 Important Combinations #100",
            verification_status="Corrected from Reference (Added classical Moon in Lagna Kendra cancellation rule)",
            cancellation_reason="Moon occupies a Kendra from Lagna, cancelling Sakata Yoga." if (has_sakata_formation and sakata_cancelled) else None
        )
    )

    return results
