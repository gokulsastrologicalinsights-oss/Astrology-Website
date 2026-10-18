"""Deterministic detector for classical Nabhasha Yogas per Brihat Parashara Hora Shastra Chapter 35."""

from typing import List, Dict, Set, Tuple, Optional, Any
from app.schemas.nabhasha import (
    NabhashaYogaDetail,
    NabhashaDistribution,
    NabhashaResponse,
)
from app.services.nabhasha_engine.models import (
    NABHASHA_GRAHAS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    CHARA_SIGNS,
    STHIRA_SIGNS,
    DVISVABHAVA_SIGNS,
    KENDRA_HOUSES,
    PANAPHARA_HOUSES,
    APOKLIMA_HOUSES,
    TRIKONA_HOUSES,
    SANKHYA_YOGAS,
)


def _get_continuous_houses(start_house: int, count: int) -> Set[int]:
    """Return set of continuous houses wrapping around 1-12."""
    return {((start_house + i - 1) % 12) + 1 for i in range(count)}


def detect_nabhasha_yogas(
    planets: List[Any],
    ascendant_sign_idx: int,
) -> NabhashaResponse:
    """Detect all qualifying Nabhasha Yogas and resolve the classical primary yoga.

    Parameters:
    - planets: list of planet objects or dicts having 'name' and 'sign_index' (1-12).
    - ascendant_sign_idx: Ascendant sign index (1-12).
    """
    # 1. Filter and normalize strictly the 7 classical grahas
    graha_positions: Dict[str, Tuple[int, int]] = {} # planet -> (sign_idx, house_num)
    planets_by_house: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    planets_by_sign: Dict[int, List[str]] = {s: [] for s in range(1, 13)}

    for p in planets:
        p_name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else None)
        p_sign = getattr(p, "sign_index", None) or (p.get("sign_index") if isinstance(p, dict) else None)

        if p_name in NABHASHA_GRAHAS and p_sign is not None:
            house_num = ((p_sign - ascendant_sign_idx) % 12) + 1
            graha_positions[p_name] = (p_sign, house_num)
            planets_by_house[house_num].append(p_name)
            planets_by_sign[p_sign].append(p_name)

    occupied_houses: Set[int] = {h for h, occupants in planets_by_house.items() if occupants}
    occupied_signs: Set[int] = {s for s, occupants in planets_by_sign.items() if occupants}

    kendra_planets = [p for p, (_, h) in graha_positions.items() if h in KENDRA_HOUSES]
    panaphara_planets = [p for p, (_, h) in graha_positions.items() if h in PANAPHARA_HOUSES]
    apoklima_planets = [p for p, (_, h) in graha_positions.items() if h in APOKLIMA_HOUSES]
    trikona_planets = [p for p, (_, h) in graha_positions.items() if h in TRIKONA_HOUSES]

    distribution = NabhashaDistribution(
        distinct_signs_count=len(occupied_signs),
        distinct_houses_count=len(occupied_houses),
        planets_by_house={h: occ for h, occ in planets_by_house.items() if occ},
        planets_by_sign={s: occ for s, occ in planets_by_sign.items() if occ},
        kendra_planets=kendra_planets,
        panaphara_planets=panaphara_planets,
        apoklima_planets=apoklima_planets,
        trikona_planets=trikona_planets,
    )

    qualifying_yogas: List[NabhashaYogaDetail] = []

    # ---------------------------------------------------------
    # 2. AAKRITI YOGAS (20 Yogas) - Specific Geometrical Formations
    # ---------------------------------------------------------

    # 2.1 Gada (Planets in two adjacent Kendras: 1-4, 4-7, 7-10, or 10-1)
    gada_pairs = [(1, 4), (4, 7), (7, 10), (10, 1)]
    for k1, k2 in gada_pairs:
        if occupied_houses.issubset({k1, k2}) and k1 in occupied_houses and k2 in occupied_houses:
            qualifying_yogas.append(
                NabhashaYogaDetail(
                    name="Gada",
                    category="Aakriti",
                    formation_rule=f"All 7 planets occupy two adjacent Kendras ({k1} and {k2}).",
                    qualifying_houses=[k1, k2],
                    qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in (k1, k2)],
                    planets_involved=list(NABHASHA_GRAHAS),
                    description="Gives wealth, dedication to righteous deeds, and proficiency in scriptures or arts.",
                )
            )
            break

    # 2.2 Shakata (Planets in 1st and 7th houses only)
    if occupied_houses.issubset({1, 7}) and 1 in occupied_houses and 7 in occupied_houses:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Shakata",
                category="Aakriti",
                formation_rule="All 7 planets occupy only the 1st (Lagna) and 7th houses.",
                qualifying_houses=[1, 7],
                qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in (1, 7)],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Indicates periods of financial fluctuation, carriage or transport endeavors, and resilient spirit.",
            )
        )

    # 2.3 Vihaga / Pakshi (Planets in 4th and 10th houses only)
    if occupied_houses.issubset({4, 10}) and 4 in occupied_houses and 10 in occupied_houses:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Vihaga",
                category="Aakriti",
                formation_rule="All 7 planets occupy only the 4th and 10th houses.",
                qualifying_houses=[4, 10],
                qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in (4, 10)],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Bestows a roaming disposition, swift messenger abilities, and involvement in public dealings.",
            )
        )

    # 2.4 Shringataka (Planets in Trikonas: 1, 5, 9 only)
    if occupied_houses.issubset({1, 5, 9}) and {1, 5, 9}.issubset(occupied_houses):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Shringataka",
                category="Aakriti",
                formation_rule="All 7 planets occupy all three Trikona houses (1st, 5th, and 9th).",
                qualifying_houses=[1, 5, 9],
                qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in (1, 5, 9)],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Conveys enduring fortune, strategic acumen, success in leadership, and domestic happiness.",
            )
        )

    # 2.5 Hala (Planets in mutual trines from non-Lagna houses: 2-6-10, 3-7-11, or 4-8-12)
    hala_triads = [(2, 6, 10), (3, 7, 11), (4, 8, 12)]
    for t1, t2, t3 in hala_triads:
        if occupied_houses.issubset({t1, t2, t3}) and {t1, t2, t3}.issubset(occupied_houses):
            qualifying_yogas.append(
                NabhashaYogaDetail(
                    name="Hala",
                    category="Aakriti",
                    formation_rule=f"All 7 planets occupy the trinal houses {t1}, {t2}, and {t3}.",
                    qualifying_houses=[t1, t2, t3],
                    qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in (t1, t2, t3)],
                    planets_involved=list(NABHASHA_GRAHAS),
                    description="Associated with agriculture, earnest manual or practical endeavors, and self-made prosperity.",
                )
            )
            break

    # 2.6 Vajra (Benefics in 1 & 7, Malefics in 4 & 10)
    benefics_in_1_7 = all(graha_positions[p][1] in {1, 7} for p in NATURAL_BENEFICS if p in graha_positions)
    malefics_in_4_10 = all(graha_positions[p][1] in {4, 10} for p in NATURAL_MALEFICS if p in graha_positions)
    if benefics_in_1_7 and malefics_in_4_10 and occupied_houses.issubset({1, 4, 7, 10}):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Vajra",
                category="Aakriti",
                formation_rule="All benefic planets in 1st & 7th houses, and all malefic planets in 4th & 10th houses.",
                qualifying_houses=[1, 4, 7, 10],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Endows physical vigor, bravery, wealth, and an imposing persona.",
            )
        )

    # 2.7 Yava (Malefics in 1 & 7, Benefics in 4 & 10)
    malefics_in_1_7 = all(graha_positions[p][1] in {1, 7} for p in NATURAL_MALEFICS if p in graha_positions)
    benefics_in_4_10 = all(graha_positions[p][1] in {4, 10} for p in NATURAL_BENEFICS if p in graha_positions)
    if malefics_in_1_7 and benefics_in_4_10 and occupied_houses.issubset({1, 4, 7, 10}):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Yava",
                category="Aakriti",
                formation_rule="All malefic planets in 1st & 7th houses, and all benefic planets in 4th & 10th houses.",
                qualifying_houses=[1, 4, 7, 10],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Gives virtuous character, restraint, charitable tendencies, and peace in mid-life.",
            )
        )

    # 2.8 Kamala / Padma (Planets distributed in all 4 Kendras: 1, 4, 7, 10)
    if occupied_houses == {1, 4, 7, 10}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Kamala",
                category="Aakriti",
                formation_rule="All four Kendras (1, 4, 7, 10) are occupied by planets, with none in other houses.",
                qualifying_houses=[1, 4, 7, 10],
                qualifying_signs=[s for p, (s, h) in graha_positions.items() if h in KENDRA_HOUSES],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Bestows eminence, pure character, spotless fame, and high societal honor.",
            )
        )

    # 2.9 Vapi (Planets outside Kendras: all in Panaphara 2,5,8,11 OR all in Apoklima 3,6,9,12)
    if occupied_houses.issubset(PANAPHARA_HOUSES) and len(occupied_houses) >= 2:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Vapi",
                category="Aakriti",
                formation_rule="All 7 planets occupy Panaphara houses (2, 5, 8, 11) outside of Kendras.",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Bestows steady wealth accumulation, reserved disposition, and enduring assets.",
            )
        )
    elif occupied_houses.issubset(APOKLIMA_HOUSES) and len(occupied_houses) >= 2:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Vapi",
                category="Aakriti",
                formation_rule="All 7 planets occupy Apoklima houses (3, 6, 9, 12) outside of Kendras.",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Bestows steady wealth accumulation, reserved disposition, and enduring assets.",
            )
        )

    # 2.10 Yupa (4 continuous houses from Lagna: 1, 2, 3, 4)
    if occupied_houses == {1, 2, 3, 4}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Yupa",
                category="Aakriti",
                formation_rule="All 7 planets occupy the four continuous houses from Lagna (1, 2, 3, 4).",
                qualifying_houses=[1, 2, 3, 4],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Associated with sacrificial virtues, spiritual wisdom, and disciplined conduct.",
            )
        )

    # 2.11 Ishu / Sara (4 continuous houses from 4th: 4, 5, 6, 7)
    if occupied_houses == {4, 5, 6, 7}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Ishu",
                category="Aakriti",
                formation_rule="All 7 planets occupy the four continuous houses from the 4th (4, 5, 6, 7).",
                qualifying_houses=[4, 5, 6, 7],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Associated with manufacturing, mechanical or military aptitude, and assertive drive.",
            )
        )

    # 2.12 Shakti (4 continuous houses from 7th: 7, 8, 9, 10)
    if occupied_houses == {7, 8, 9, 10}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Shakti",
                category="Aakriti",
                formation_rule="All 7 planets occupy the four continuous houses from the 7th (7, 8, 9, 10).",
                qualifying_houses=[7, 8, 9, 10],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Indicates courage, overcoming adversaries, and persevering through initial obstacles.",
            )
        )

    # 2.13 Danda (4 continuous houses from 10th: 10, 11, 12, 1)
    if occupied_houses == {10, 11, 12, 1}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Danda",
                category="Aakriti",
                formation_rule="All 7 planets occupy the four continuous houses from the 10th (10, 11, 12, 1).",
                qualifying_houses=[10, 11, 12, 1],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Associated with justice, disciplinary authority, independence, and strict adherence to duty.",
            )
        )

    # 2.14 Nauka (7 continuous houses from Lagna: 1 to 7)
    if occupied_houses == {1, 2, 3, 4, 5, 6, 7}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Nauka",
                category="Aakriti",
                formation_rule="All 7 planets occupy the seven continuous houses from Lagna (1 through 7).",
                qualifying_houses=list(range(1, 8)),
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Associated with waterborne enterprise, fluctuating fortunes, and resourceful adaptability.",
            )
        )

    # 2.15 Kuta (7 continuous houses from 4th: 4 to 10)
    if occupied_houses == {4, 5, 6, 7, 8, 9, 10}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Kuta",
                category="Aakriti",
                formation_rule="All 7 planets occupy the seven continuous houses from the 4th (4 through 10).",
                qualifying_houses=list(range(4, 11)),
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Gives mountain-like steadfastness, protective nature, and strategic caution.",
            )
        )

    # 2.16 Chhatra (7 continuous houses from 7th: 7 to 1)
    if occupied_houses == {7, 8, 9, 10, 11, 12, 1}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Chhatra",
                category="Aakriti",
                formation_rule="All 7 planets occupy the seven continuous houses from the 7th (7 through 1).",
                qualifying_houses=[7, 8, 9, 10, 11, 12, 1],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Like an umbrella, provides shelter to family and dependents; brings high executive dignity.",
            )
        )

    # 2.17 Chapa / Dhanus (7 continuous houses from 10th: 10 to 4)
    if occupied_houses == {10, 11, 12, 1, 2, 3, 4}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Chapa",
                category="Aakriti",
                formation_rule="All 7 planets occupy the seven continuous houses from the 10th (10 through 4).",
                qualifying_houses=[10, 11, 12, 1, 2, 3, 4],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Bow-shaped disposition; bold, assertive, skilled in defense and ambitious accomplishments.",
            )
        )

    # 2.18 Ardha-Chandra (7 continuous houses starting from non-Kendra houses)
    non_kendra_starts = [2, 3, 5, 6, 8, 9, 11, 12]
    for start_h in non_kendra_starts:
        cont_7 = _get_continuous_houses(start_h, 7)
        if occupied_houses == cont_7:
            qualifying_yogas.append(
                NabhashaYogaDetail(
                    name="Ardha-Chandra",
                    category="Aakriti",
                    formation_rule=f"All 7 planets occupy seven continuous houses starting from house {start_h} (non-Kendra).",
                    qualifying_houses=sorted(list(cont_7)),
                    qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                    planets_involved=list(NABHASHA_GRAHAS),
                    description="Crescent moon formation; confers pleasant countenance, governmental favor, and affluence.",
                )
            )
            break

    # 2.19 Chakra (Alternate 6 odd houses from Lagna: 1, 3, 5, 7, 9, 11)
    if occupied_houses == {1, 3, 5, 7, 9, 11}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Chakra",
                category="Aakriti",
                formation_rule="All 7 planets occupy all six alternate houses starting from Lagna (1, 3, 5, 7, 9, 11).",
                qualifying_houses=[1, 3, 5, 7, 9, 11],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Conveys regal status, vast prestige, intellectual mastery, and sovereign recognition.",
            )
        )

    # 2.20 Samudra (Alternate 6 even houses from 2nd house: 2, 4, 6, 8, 10, 12)
    if occupied_houses == {2, 4, 6, 8, 10, 12}:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Samudra",
                category="Aakriti",
                formation_rule="All 7 planets occupy all six alternate houses starting from 2nd house (2, 4, 6, 8, 10, 12).",
                qualifying_houses=[2, 4, 6, 8, 10, 12],
                qualifying_signs=[s for p, (s, _) in graha_positions.items()],
                planets_involved=list(NABHASHA_GRAHAS),
                description="Ocean-like boundless wealth, benevolent generosity, domestic happiness, and broad acclaim.",
            )
        )

    # ---------------------------------------------------------
    # 3. ASHRAYA YOGAS (3 Yogas) - Based on Sign Modality
    # ---------------------------------------------------------
    if occupied_signs.issubset(CHARA_SIGNS):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Rajju",
                category="Ashraya",
                formation_rule="All 7 planets occupy Chara (Movable) signs (Aries, Cancer, Libra, Capricorn).",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=sorted(list(occupied_signs)),
                planets_involved=list(NABHASHA_GRAHAS),
                description="Fond of travel, enterprising, ambitious, flourishes in foreign lands.",
            )
        )
    elif occupied_signs.issubset(STHIRA_SIGNS):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Musala",
                category="Ashraya",
                formation_rule="All 7 planets occupy Sthira (Fixed) signs (Taurus, Leo, Scorpio, Aquarius).",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=sorted(list(occupied_signs)),
                planets_involved=list(NABHASHA_GRAHAS),
                description="Firm, steadfast, persevering, proud, stable wealth and unwavering convictions.",
            )
        )
    elif occupied_signs.issubset(DVISVABHAVA_SIGNS):
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Nala",
                category="Ashraya",
                formation_rule="All 7 planets occupy Dvisvabhava (Dual) signs (Gemini, Virgo, Sagittarius, Pisces).",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=sorted(list(occupied_signs)),
                planets_involved=list(NABHASHA_GRAHAS),
                description="Versatile intellect, skilled in multiple crafts, adaptable, charming and diplomatic.",
            )
        )

    # ---------------------------------------------------------
    # 4. DALA YOGAS (2 Yogas) - Benefics/Malefics in Kendras
    # ---------------------------------------------------------
    benefics_in_kendra = [p for p in NATURAL_BENEFICS if p in graha_positions and graha_positions[p][1] in KENDRA_HOUSES]
    malefics_in_kendra = [p for p in NATURAL_MALEFICS if p in graha_positions and graha_positions[p][1] in KENDRA_HOUSES]

    # Mala: Kendras occupied by benefics only, and no malefics in Kendras
    if len(benefics_in_kendra) >= 2 and len(malefics_in_kendra) == 0:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Mala",
                category="Dala",
                formation_rule="Benefics occupy Kendra houses while malefic planets are placed outside Kendras.",
                qualifying_houses=[graha_positions[p][1] for p in benefics_in_kendra],
                qualifying_signs=[graha_positions[p][0] for p in benefics_in_kendra],
                planets_involved=benefics_in_kendra,
                description="Garland of blessings: pleasant life, generous disposition, vehicles, and fond friendships.",
            )
        )
    # Sarpa: Kendras occupied by malefics only, and no benefics in Kendras
    elif len(malefics_in_kendra) >= 2 and len(benefics_in_kendra) == 0:
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name="Sarpa",
                category="Dala",
                formation_rule="Malefics occupy Kendra houses while benefic planets are placed outside Kendras.",
                qualifying_houses=[graha_positions[p][1] for p in malefics_in_kendra],
                qualifying_signs=[graha_positions[p][0] for p in malefics_in_kendra],
                planets_involved=malefics_in_kendra,
                description="Serpent-like disposition: requires patience in early adversity, tough resilience, and sharp survival instincts.",
            )
        )

    # ---------------------------------------------------------
    # 5. SANKHYA YOGAS (7 Yogas) - Always Evaluated by Sign Count
    # ---------------------------------------------------------
    count_signs = len(occupied_signs)
    if count_signs in SANKHYA_YOGAS:
        sankhya_name, sankhya_desc = SANKHYA_YOGAS[count_signs]
        qualifying_yogas.append(
            NabhashaYogaDetail(
                name=sankhya_name,
                category="Sankhya",
                formation_rule=f"All 7 planets occupy exactly {count_signs} distinct zodiac signs.",
                qualifying_houses=sorted(list(occupied_houses)),
                qualifying_signs=sorted(list(occupied_signs)),
                planets_involved=list(NABHASHA_GRAHAS),
                description=sankhya_desc,
            )
        )

    # ---------------------------------------------------------
    # 6. RESOLVE PRIMARY OPERATIVE YOGA PER CLASSICAL PRECEDENCE
    # ---------------------------------------------------------
    # Precedence Order:
    # 1. Aakriti Yogas (Most specific celestial geometric forms)
    # 2. Ashraya Yogas (Sign modality - only if no Aakriti is formed)
    # 3. Dala Yogas (Kendra polarity)
    # 4. Sankhya Yogas (Pure planetary count fallback)
    primary_yoga: Optional[NabhashaYogaDetail] = None

    aakriti_candidates = [y for y in qualifying_yogas if y.category == "Aakriti"]
    ashraya_candidates = [y for y in qualifying_yogas if y.category == "Ashraya"]
    dala_candidates = [y for y in qualifying_yogas if y.category == "Dala"]
    sankhya_candidates = [y for y in qualifying_yogas if y.category == "Sankhya"]

    if aakriti_candidates:
        primary_yoga = aakriti_candidates[0]
    elif ashraya_candidates:
        primary_yoga = ashraya_candidates[0]
    elif dala_candidates:
        primary_yoga = dala_candidates[0]
    elif sankhya_candidates:
        primary_yoga = sankhya_candidates[0]

    # Set is_primary flag
    for y in qualifying_yogas:
        if primary_yoga and y.name == primary_yoga.name and y.category == primary_yoga.category:
            y.is_primary = True
        else:
            y.is_primary = False

    return NabhashaResponse(
        distribution=distribution,
        primary_yoga=primary_yoga,
        all_qualifying_yogas=qualifying_yogas,
    )
