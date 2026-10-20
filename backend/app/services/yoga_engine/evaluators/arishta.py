"""Classical Arishta Bhanga (Neutralization of Afflictions / Vitality Preservation) Engine.

Classical References:
- Brihat Parashara Hora Shastra (BPHS), Chapters 10 & 11 (Balarishta and Arishta Bhanga).
- Phaladeepika, Chapter 13 (Arishta and Arishta Bhanga).
- Saravali, Chapter 12 (Arishta Phala and Bhanga).
- Dr. B.V. Raman, '300 Important Combinations', Combinations #184–190.

Arishta combinations represent severe planetary afflictions to the Lagna or Moon that threaten
vitality, health, and infant well-being. Classical Vedic astrology defines specific, powerful
Arishta Bhanga formations that completely neutralize these adverse combinations, conferring
long life, immunity, and resilience.
"""

from typing import List
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    KENDRA_HOUSES,
    UPACHAYA_HOUSES,
    DUSTHANA_HOUSES,
    SIGN_NAMES_EN,
)


def evaluate_arishta_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    """Evaluate classical Arishta Bhanga (cancellation of life/health danger) yogas."""
    results: List[YogaDetail] = []

    # -------------------------------------------------------------
    # 1. Arishta Bhanga: Jupiter in Kendra / Lagna
    # -------------------------------------------------------------
    # BPHS 11.1 & Phaladeepika 13.9: Strong Jupiter in Lagna or Kendra destroys all arishta.
    jup_house = ctx.planet_house.get("Jupiter")
    jup_is_combust, jup_sep, jup_orb = ctx.get_combustion_details("Jupiter")
    jup_is_debilitated = ctx.is_debilitated("Jupiter")

    jup_in_lagna = (jup_house == 1)
    jup_in_kendra = (jup_house in KENDRA_HOUSES) if jup_house else False

    # Operative if in Kendra, not combust, and not uncancelled debilitated
    c1_passed = jup_in_kendra and not jup_is_combust and not jup_is_debilitated
    c1_cancelled = jup_in_kendra and (jup_is_combust or jup_is_debilitated)

    c1_status = "Not Qualifying"
    c1_cancel_reason = None
    if jup_in_kendra:
        if c1_cancelled:
            c1_status = "Cancelled"
            c1_cancel_reason = "Jupiter is in Kendra but weakened by combustion or debilitation."
        else:
            c1_status = "Qualifying"

    results.append(
        YogaDetail(
            id="arishta_bhanga_jupiter_kendra",
            name="Arishta Bhanga (Jupiter in Kendra)",
            name_tamil="அரிஷ்ட பங்க யோகம் (கேந்திரத்தில் குரு)",
            category="Arishta Bhanga",
            status=c1_status,
            is_qualifying=c1_passed,
            planets_involved=["Jupiter"],
            relevant_houses=[jup_house] if jup_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Jupiter occupies Lagna (House 1) or a Kendra house (1, 4, 7, 10)",
                    passed=jup_in_kendra,
                    detail=f"Jupiter occupies House {jup_house}." if jup_house else "Jupiter position unavailable."
                ),
                YogaConditionItem(
                    condition="Jupiter is free from Combustion (Asta) and debility",
                    passed=not (jup_is_combust or jup_is_debilitated),
                    detail=(
                        f"Combust ({jup_sep:.1f}° from Sun)" if jup_is_combust else
                        ("Debilitated in Capricorn" if jup_is_debilitated else "Well-dignified and free from combustion.")
                    )
                )
            ],
            short_interpretation=(
                "All bodily afflictions and life threats are dissolved by Jupiter's divine protection, granting longevity and robust vitality."
                if c1_passed else
                (
                    "Arishta Bhanga neutralized due to Jupiter's combustion or debility."
                    if c1_status == "Cancelled" else
                    "Jupiter does not occupy a Kendra from Lagna."
                )
            ),
            classical_definition="Even as a single brave archer routs thousands of foes, strong Jupiter in the Ascendant or Kendra dissolves all arishtas.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 11, v. 1; Phaladeepika Ch. 13, v. 9; 300 Important Combinations #184",
            verification_status="Classical Independent Implementation",
            cancellation_reason=c1_cancel_reason,
        )
    )

    # -------------------------------------------------------------
    # 2. Arishta Bhanga: Benefics in Kendras
    # -------------------------------------------------------------
    # BPHS 11.2: Jupiter, Venus, or Mercury in Kendras free from malefic conjunctions
    kendra_benefics = []
    malefics = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

    for b in ("Jupiter", "Venus", "Mercury"):
        b_h = ctx.planet_house.get(b)
        if b_h in KENDRA_HOUSES:
            occupants = set(ctx.house_occupants.get(b_h, []))
            conjoined_malefics = occupants & malefics - {b}
            is_combust, _, _ = ctx.get_combustion_details(b)
            if not conjoined_malefics and not is_combust:
                kendra_benefics.append((b, b_h))

    c2_passed = len(kendra_benefics) > 0
    results.append(
        YogaDetail(
            id="arishta_bhanga_benefics_kendras",
            name="Arishta Bhanga (Benefics in Kendras)",
            name_tamil="அரிஷ்ட பங்க யோகம் (சுப கிரகங்கள் கேந்திரத்தில்)",
            category="Arishta Bhanga",
            status="Qualifying" if c2_passed else "Not Qualifying",
            is_qualifying=c2_passed,
            planets_involved=[b for b, _ in kendra_benefics],
            relevant_houses=[h for _, h in kendra_benefics],
            conditions=[
                YogaConditionItem(
                    condition="Natural benefics (Jupiter, Venus, Mercury) occupy Kendras free from malefic conjunction or combustion",
                    passed=c2_passed,
                    detail=(
                        "; ".join(f"{b} in House {h}" for b, h in kendra_benefics)
                        if c2_passed else
                        "No unafflicted natural benefics found in Kendras."
                    )
                )
            ],
            short_interpretation=(
                "Presence of natural benefics in quadrant houses shields the constitutional health and overcomes pediatric and adult bodily perils."
                if c2_passed else
                "No unafflicted benefic occupies a Kendra to trigger this specific cancellation."
            ),
            classical_definition="Natural benefics occupying Kendra houses (1, 4, 7, 10) free from malefic conjunction extinguish all arishta doshas.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 11, v. 2; Phaladeepika Ch. 13, v. 8",
            verification_status="Classical Independent Implementation",
        )
    )

    # -------------------------------------------------------------
    # 3. Arishta Bhanga: Lagna Lord Strong in Kendra
    # -------------------------------------------------------------
    # BPHS 11.4: Lagna lord in Kendra, aspected by benefics, uncombust
    l_1 = ctx.house_lords[1]
    h_l1 = ctx.planet_house.get(l_1)
    l1_in_kendra = (h_l1 in KENDRA_HOUSES) if h_l1 else False
    l1_is_combust, _, _ = ctx.get_combustion_details(l_1) if l_1 != "Sun" else (False, 0.0, 0.0)
    l1_is_debilitated = ctx.is_debilitated(l_1) if l_1 else False
    l1_aspected_by_benefic = (
        ctx.planet_aspects_planet("Jupiter", l_1) or ctx.planet_aspects_planet("Venus", l_1)
    ) if l_1 else False

    c3_passed = l1_in_kendra and not l1_is_combust and not l1_is_debilitated
    c3_status = "Qualifying" if c3_passed else "Not Qualifying"

    results.append(
        YogaDetail(
            id="arishta_bhanga_lagna_lord",
            name="Arishta Bhanga (Lagna Lord in Kendra)",
            name_tamil="அரிஷ்ட பங்க யோகம் (லக்னாதிபதி பலம்)",
            category="Arishta Bhanga",
            status=c3_status,
            is_qualifying=c3_passed,
            planets_involved=[l_1] if l_1 else [],
            relevant_houses=[h_l1] if h_l1 else [],
            conditions=[
                YogaConditionItem(
                    condition="Lagna lord occupies a Kendra house (1, 4, 7, 10) from Lagna",
                    passed=l1_in_kendra,
                    detail=f"Lagna lord {l_1} occupies House {h_l1}." if l_1 else "Lagna lord unavailable."
                ),
                YogaConditionItem(
                    condition="Lagna lord is free from combustion and debility",
                    passed=not (l1_is_combust or l1_is_debilitated),
                    detail="Lagna lord is dignified and uncombust." if not (l1_is_combust or l1_is_debilitated) else "Lagna lord combust or debilitated."
                )
            ],
            short_interpretation=(
                "A strong Lagna lord situated in an angular house anchors the life force, protecting against physical adversity and disease."
                if c3_passed else
                "Lagna lord is not situated in a Kendra or suffers from debility/combustion."
            ),
            classical_definition="Lord of the Ascendant well-placed in an angular quadrant without debility or combustion neutralizes bodily afflictions.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 11, v. 4; Saravali Ch. 12, v. 10",
            verification_status="Classical Independent Implementation",
        )
    )

    # -------------------------------------------------------------
    # 4. Arishta Bhanga: Rahu in Upachaya Houses (3, 6, 11)
    # -------------------------------------------------------------
    # BPHS 11.6 & Phaladeepika 13.10: Rahu in 3, 6, or 11 destroys all arishta like wind disperses mist
    rahu_house = ctx.planet_house.get("Rahu")
    rahu_in_upachaya = (rahu_house in {3, 6, 11}) if rahu_house else False

    results.append(
        YogaDetail(
            id="arishta_bhanga_rahu_upachaya",
            name="Arishta Bhanga (Rahu in Upachaya)",
            name_tamil="அரிஷ்ட பங்க யோகம் (உபசெயத்தில் ராகு)",
            category="Arishta Bhanga",
            status="Qualifying" if rahu_in_upachaya else "Not Qualifying",
            is_qualifying=rahu_in_upachaya,
            planets_involved=["Rahu"] if rahu_in_upachaya else [],
            relevant_houses=[rahu_house] if rahu_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Rahu occupies an Upachaya house (3rd, 6th, or 11th house) from Lagna",
                    passed=rahu_in_upachaya,
                    detail=f"Rahu occupies House {rahu_house}." if rahu_house else "Rahu position unavailable."
                )
            ],
            short_interpretation=(
                "Rahu in an Upachaya house converts latent adversity into unyielding immune resilience, destroying all arishtas as wind sweeps away mist."
                if rahu_in_upachaya else
                "Rahu is not situated in the 3rd, 6th, or 11th house."
            ),
            classical_definition="Rahu occupying the 3rd, 6th, or 11th house from Lagna completely dissolves all arishta doshas.",
            classical_reference="Brihat Parashara Hora Shastra Ch. 11, v. 6; Phaladeepika Ch. 13, v. 10; Jataka Parijata Ch. 6, v. 56",
            verification_status="Classical Independent Implementation",
        )
    )

    # -------------------------------------------------------------
    # 5. Arishta Bhanga: Benefic Drishti on Moon in Dusthana
    # -------------------------------------------------------------
    # Phaladeepika 13.12: Moon in 6, 8, 12 aspected by Jupiter or Venus converts danger into longevity
    moon_house = ctx.planet_house.get("Moon")
    moon_in_dusthana = (moon_house in DUSTHANA_HOUSES) if moon_house else False
    moon_aspected_by_guru_sukra = (
        ctx.planet_aspects_planet("Jupiter", "Moon") or ctx.planet_aspects_planet("Venus", "Moon")
    )
    c5_passed = moon_in_dusthana and moon_aspected_by_guru_sukra

    results.append(
        YogaDetail(
            id="arishta_bhanga_moon_benefic_drishti",
            name="Arishta Bhanga (Benefic Drishti on Moon)",
            name_tamil="அரிஷ்ட பங்க யோகம் (சந்திரன் மீது சுப பார்வை)",
            category="Arishta Bhanga",
            status="Qualifying" if c5_passed else "Not Qualifying",
            is_qualifying=c5_passed,
            planets_involved=["Moon"] + [p for p in ("Jupiter", "Venus") if ctx.planet_aspects_planet(p, "Moon")],
            relevant_houses=[moon_house] if moon_house else [],
            conditions=[
                YogaConditionItem(
                    condition="Moon occupies a Dusthana house (6th, 8th, or 12th)",
                    passed=moon_in_dusthana,
                    detail=f"Moon occupies House {moon_house}." if moon_house else "Moon position unavailable."
                ),
                YogaConditionItem(
                    condition="Moon receives the full aspect (Drishti) of natural benefics Jupiter or Venus",
                    passed=moon_aspected_by_guru_sukra,
                    detail="Moon receives drishti from Jupiter/Venus." if moon_aspected_by_guru_sukra else "No benefic aspect on Moon."
                )
            ],
            short_interpretation=(
                "Afflictions arising from lunar placement in a difficult house are redeemed by benefic aspect, granting long life and mental peace."
                if c5_passed else
                "Moon is either not in a Dusthana or lacks benefic aspect from Jupiter or Venus."
            ),
            classical_definition="Even when the Moon occupies the 6th, 8th, or 12th house, receiving the aspect of Jupiter or Venus dissolves all danger.",
            classical_reference="Phaladeepika Ch. 13, v. 12; Brihat Parashara Hora Shastra Ch. 11, v. 7",
            verification_status="Classical Independent Implementation",
        )
    )

    return results
