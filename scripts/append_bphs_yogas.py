# scripts/append_bphs_yogas.py
from pathlib import Path

path = Path("backend/app/services/yoga_engine/evaluators/classical.py")
content = path.read_text(encoding="utf-8")

# Check imports
if "SIGN_LORDS" not in content:
    content = content.replace(
        "    SIGN_NAMES_TA,\n)",
        "    SIGN_NAMES_TA,\n    SIGN_LORDS,\n    get_nth_house,\n    TRIKONA_HOUSES,\n)",
    )

bphs_yogas_code = '''
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
            name_tamil="பிரம்streetsம யோகம்",
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
'''

# Note: In Tamil, "பிரம்streetsம யோகம்" typo, let's fix to "பிரம்ம யோகம்"
bphs_yogas_code = bphs_yogas_code.replace("பிரம்streetsம யோகம்", "பிரம்ம யோகம்")

# Append before return results
return_idx = content.rfind("    return results")
if return_idx != -1:
    new_content = content[:return_idx] + bphs_yogas_code + "\n" + content[return_idx:]
    path.write_text(new_content, encoding="utf-8")
    print("Successfully appended BPHS yogas to classical.py!")
else:
    print("Could not find return results in classical.py")
