"""Marriage Evaluation Module: Marital Discord, Upapada Affliction, and Darakaraka Timing.

Based on empirical researches:
1. Shunny Nigam: 'Marital Discord: An Analysis' (pp. 110-136)
   - Rule A (96%): Malefic influence on 2nd house from Upapada Lagna (UL) via placement or Jaimini aspect.
   - Rule B (64%): Natal 7th lord debilitated, combust, or afflicted in Navamsha (D9).
   - Rule C (64%): Venus afflicted in Rashi chart (by Saturn, Mars, Sun, Rahu/Ketu, combustion, papakartari).
   - Rule D (84%): 6th, 8th, or 12th lords associated with 7th house or 7th lord (conjunction, aspect, mutual exchange).
   - Supplementary 1 (16%): Lagna lord and 7th lord in 6/8 Shadashtaka mutual position.
   - Supplementary 2: Arudha Lagna (AL) and Darapada (A7) in 6/8 or 2/12 mutual disposition.
2. Shiv Raj Sharma: 'Dasha and Timing of Marital Discord' (pp. 138-154)
   - Friction and separation events triggered in dasha/antardasha of 5th/6th/8th lords or planets in 6/8.
3. Supriya Jagdish: 'Darakaraka in Vimshottari' (pp. 156-174)
   - Marriage fruition and discord inflection points during Darakaraka (DK) Mahadasha/Antardasha.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from app.services.kn_rao_engine.models import MaritalDiscordResult
from app.services.kn_rao_engine.career_evaluator import (
    SIGN_LORDS,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    calculate_jaimini_7_karakas,
    get_jaimini_aspects_for_sign,
    get_parashari_aspects_for_planet,
)

NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}


def calculate_arudha_pada(house_num: int, lagna_sign: int, planets_data: Dict[str, Dict[str, Any]]) -> Tuple[int, str]:
    """Calculate Arudha Pada for a given house number (1 to 12).
    
    Rule:
    1. House sign H = ((lagna_sign + house_num - 2) % 12) + 1
    2. Find Lord of house sign L
    3. Find sign of Lord S_lord
    4. Distance d from H to S_lord (counting inclusive)
    5. Raw Arudha = ((S_lord + d - 2) % 12) + 1
    6. Exception: If Raw Arudha is same house or 7th from house, shift 10 signs forward (i.e. +9 signs).
    """
    house_sign = ((lagna_sign + house_num - 2) % 12) + 1
    lord_name = SIGN_LORDS.get(house_sign, "Mars")
    
    lord_sign = planets_data.get(lord_name, {}).get("sign_index", house_sign)
    
    dist = (lord_sign - house_sign) % 12
    raw_arudha = ((lord_sign + dist - 1) % 12) + 1
    
    seventh_from_house = ((house_sign + 5) % 12) + 1
    
    if raw_arudha == house_sign or raw_arudha == seventh_from_house:
        final_arudha = ((raw_arudha + 8) % 12) + 1
    else:
        final_arudha = raw_arudha
        
    return final_arudha, SIGN_NAMES_EN[final_arudha]


def evaluate_marital_discord(
    planets_data: Dict[str, Dict[str, Any]],
    d9_planets: Optional[Dict[str, Dict[str, Any]]] = None,
    lagna_sign: int = 1,
    active_mahadasha: Optional[str] = None,
    active_antardasha: Optional[str] = None
) -> MaritalDiscordResult:
    """Evaluate marital discord and harmony using Shunny Nigam's empirical rules and dasha triggers."""
    if d9_planets is None:
        d9_planets = {}

    reasons: List[str] = []
    reasons_tamil: List[str] = []
    
    # 1. Calculate Upapada Lagna (UL, Arudha of 12th house)
    ul_sign_idx, ul_sign_name = calculate_arudha_pada(12, lagna_sign, planets_data)
    ul_sign_ta = SIGN_NAMES_TA[ul_sign_idx]
    
    # 2nd house from Upapada Lagna
    second_from_ul_idx = (ul_sign_idx % 12) + 1
    second_from_ul_name = SIGN_NAMES_EN[second_from_ul_idx]
    second_from_ul_ta = SIGN_NAMES_TA[second_from_ul_idx]

    # Arudha Lagna (AL, H1) and Darapada (A7, H7)
    al_sign_idx, al_sign_name = calculate_arudha_pada(1, lagna_sign, planets_data)
    a7_sign_idx, a7_sign_name = calculate_arudha_pada(7, lagna_sign, planets_data)
    
    # -----------------------------------------------------------------------
    # Rule A (96%): Malefic influence on 2nd house from Upapada Lagna
    # -----------------------------------------------------------------------
    malefics_in_second_from_ul: List[str] = []
    jaimini_malefic_aspects_on_second_from_ul: List[str] = []
    
    # Check planets posited in 2nd from UL
    for p, pdata in planets_data.items():
        if p in NATURAL_MALEFICS and pdata.get("sign_index") == second_from_ul_idx:
            malefics_in_second_from_ul.append(p)
            
    # Check Jaimini aspects onto 2nd from UL
    # Find which signs aspect second_from_ul_idx via Jaimini
    aspecting_signs_to_2nd_ul = set()
    for s in range(1, 13):
        if second_from_ul_idx in get_jaimini_aspects_for_sign(s):
            aspecting_signs_to_2nd_ul.add(s)
            
    for p, pdata in planets_data.items():
        if p in NATURAL_MALEFICS and pdata.get("sign_index") in aspecting_signs_to_2nd_ul:
            jaimini_malefic_aspects_on_second_from_ul.append(p)

    rule_a_matched = len(malefics_in_second_from_ul) > 0 or len(jaimini_malefic_aspects_on_second_from_ul) > 0

    if rule_a_matched:
        afflictors = list(set(malefics_in_second_from_ul + jaimini_malefic_aspects_on_second_from_ul))
        reasons.append(
            f"Rule A (96% Research Accuracy): 2nd house from Upapada Lagna ({second_from_ul_name}) is afflicted by "
            f"natural malefics: {', '.join(afflictors)}."
        )
        reasons_tamil.append(
            f"விRule A (96% உறுதி): உபபத லக்னத்திற்கு 2-ம் வீடான {second_from_ul_ta}-ல் பாபக் கிரகங்கள் "
            f"({', '.join(afflictors)}) நிலை அல்லது ஜெமினி பார்வையில் உள்ளன."
        )

    # -----------------------------------------------------------------------
    # Rule B (64%): Natal 7th lord debilitated, combust, or afflicted in Navamsha D9
    # -----------------------------------------------------------------------
    h7_sign = ((lagna_sign + 5) % 12) + 1
    h7_lord = SIGN_LORDS[h7_sign]
    h7_lord_data = planets_data.get(h7_lord, {})
    
    h7_lord_d9_sign = d9_planets.get(h7_lord, {}).get("sign_index") if d9_planets else None
    
    rule_b_matched = False
    b_details = []
    
    # Check natal combustion / debility
    if h7_lord_data.get("is_combust", False):
        rule_b_matched = True
        b_details.append(f"{h7_lord} is combust in natal chart")
    if h7_lord_data.get("sign_index") == DEBILITATION_SIGNS.get(h7_lord):
        rule_b_matched = True
        b_details.append(f"{h7_lord} is debilitated in natal chart")
        
    # Check D9 debilitation or affliction
    if h7_lord_d9_sign is not None:
        if h7_lord_d9_sign == DEBILITATION_SIGNS.get(h7_lord):
            rule_b_matched = True
            b_details.append(f"{h7_lord} is debilitated in Navamsha (D9)")
        # Check if D9 sign has malefics
        d9_co_tenants = [
            p for p, d in d9_planets.items()
            if p != h7_lord and p in NATURAL_MALEFICS and d.get("sign_index") == h7_lord_d9_sign
        ]
        if d9_co_tenants:
            rule_b_matched = True
            b_details.append(f"{h7_lord} is conjoined by malefic(s) {', '.join(d9_co_tenants)} in Navamsha")

    if rule_b_matched:
        reasons.append(
            f"Rule B (64% Research Accuracy): 7th lord ({h7_lord}) suffers debility/combustion/Navamsha affliction: "
            f"{'; '.join(b_details)}."
        )
        reasons_tamil.append(
            f"Rule B (64% உறுதி): 7-ம் அதிபதி ({h7_lord}) நீசம்/அஸ்தமனம்/நவாம்சத்தில் பாப சேர்க்கை பெற்றுள்ளது."
        )

    # -----------------------------------------------------------------------
    # Rule C (64%): Venus afflicted in Rashi chart
    # -----------------------------------------------------------------------
    venus_data = planets_data.get("Venus", {})
    venus_sign = venus_data.get("sign_index", 1)
    
    rule_c_matched = False
    c_details = []
    
    if venus_data.get("is_combust", False):
        rule_c_matched = True
        c_details.append("combust")
    if venus_sign == DEBILITATION_SIGNS.get("Venus"):
        rule_c_matched = True
        c_details.append("debilitated in Virgo")
        
    # Conjunction with natural malefics
    malefics_with_venus = [
        p for p in NATURAL_MALEFICS
        if p in planets_data and planets_data[p].get("sign_index") == venus_sign
    ]
    if malefics_with_venus:
        rule_c_matched = True
        c_details.append(f"conjoined with {', '.join(malefics_with_venus)}")
        
    # Parashari aspects onto Venus from Saturn/Mars/Sun/Rahu/Ketu
    aspecting_malefics_venus = []
    for m in NATURAL_MALEFICS:
        if m in planets_data and m not in malefics_with_venus:
            m_sign = planets_data[m].get("sign_index", 1)
            aspects = get_parashari_aspects_for_planet(m, m_sign)
            if venus_sign in aspects:
                aspecting_malefics_venus.append(m)
    if aspecting_malefics_venus:
        rule_c_matched = True
        c_details.append(f"aspected by malefic(s) {', '.join(aspecting_malefics_venus)}")

    # Papakartari Yoga on Venus (hemmed between malefics in adjacent signs)
    prev_sign = ((venus_sign - 2) % 12) + 1
    next_sign = (venus_sign % 12) + 1
    malefic_in_prev = any(planets_data.get(p, {}).get("sign_index") == prev_sign for p in NATURAL_MALEFICS)
    malefic_in_next = any(planets_data.get(p, {}).get("sign_index") == next_sign for p in NATURAL_MALEFICS)
    if malefic_in_prev and malefic_in_next:
        rule_c_matched = True
        c_details.append("hemmed in Papakartari Yoga")

    if rule_c_matched:
        reasons.append(
            f"Rule C (64% Research Accuracy): Kalatrakaraka Venus is afflicted in Rashi chart ({', '.join(c_details)})."
        )
        reasons_tamil.append(
            f"Rule C (64% உறுதி): களத்திரகாரகன் சுக்கிரன் பாபக் கிரகங்களால் பீடிக்கப்பட்டுள்ளார் ({', '.join(c_details)})."
        )

    # -----------------------------------------------------------------------
    # Rule D (84%): 6th, 8th, or 12th lords associated with 7th house or 7th lord
    # -----------------------------------------------------------------------
    h6_sign = ((lagna_sign + 4) % 12) + 1
    h8_sign = ((lagna_sign + 6) % 12) + 1
    h12_sign = ((lagna_sign + 10) % 12) + 1
    
    trik_lords = {
        "6th_lord": SIGN_LORDS[h6_sign],
        "8th_lord": SIGN_LORDS[h8_sign],
        "12th_lord": SIGN_LORDS[h12_sign]
    }
    
    rule_d_matched = False
    d_details = []
    
    h7_lord_sign = h7_lord_data.get("sign_index", 1)
    
    for role, t_lord in trik_lords.items():
        if t_lord == h7_lord:
            continue  # e.g., for some lagnas where same lord rules 7 and 12 (Taurus: Mars rules 7 & 12)
        t_lord_data = planets_data.get(t_lord, {})
        t_sign = t_lord_data.get("sign_index")
        if not t_sign:
            continue
            
        # 1. Conjunction with 7th lord
        if t_sign == h7_lord_sign:
            rule_d_matched = True
            d_details.append(f"{role} ({t_lord}) conjoins 7th lord ({h7_lord})")
            
        # 2. Placed in 7th house
        if t_sign == h7_sign:
            rule_d_matched = True
            d_details.append(f"{role} ({t_lord}) occupies 7th house")
            
        # 3. Aspects 7th house
        t_aspects = get_parashari_aspects_for_planet(t_lord, t_sign)
        if h7_sign in t_aspects:
            rule_d_matched = True
            d_details.append(f"{role} ({t_lord}) aspects 7th house")
            
        # 4. Aspects 7th lord
        if h7_lord_sign in t_aspects:
            rule_d_matched = True
            d_details.append(f"{role} ({t_lord}) aspects 7th lord ({h7_lord})")
            
        # 5. 7th lord placed in 6th, 8th, or 12th house
        if h7_lord_sign in {h6_sign, h8_sign, h12_sign}:
            rule_d_matched = True
            house_name = "6th" if h7_lord_sign == h6_sign else ("8th" if h7_lord_sign == h8_sign else "12th")
            d_details.append(f"7th lord ({h7_lord}) is placed in dusthana ({house_name} house)")

    if rule_d_matched:
        # deduplicate
        d_unique = list(set(d_details))
        reasons.append(
            f"Rule D (84% Research Accuracy): Dusthana (6/8/12) connection with 7th house/lord: {'; '.join(d_unique)}."
        )
        reasons_tamil.append(
            f"Rule D (84% உறுதி): 6, 8, 12-ம் அதிபதிகள் களத்திர ஸ்தானத்துடன் (7-ம் வீடு/அதிபதி) தொடர்பு கொண்டுள்ளனர்."
        )

    # -----------------------------------------------------------------------
    # Supplementary Rules: 6/8 Shadashtaka & AL/A7 Tension
    # -----------------------------------------------------------------------
    h1_lord = SIGN_LORDS[lagna_sign]
    h1_lord_sign = planets_data.get(h1_lord, {}).get("sign_index", 1)
    
    # 6/8 mutual disposition between Lagna Lord and 7th Lord
    dist_1_to_7_lord = (h7_lord_sign - h1_lord_sign) % 12
    supplementary_shadashtaka = dist_1_to_7_lord in {5, 7}  # 6th (5 away) or 8th (7 away)
    
    if supplementary_shadashtaka:
        reasons.append(
            f"Supplementary Rule 1 (16% Empirical Friction): Lagna lord ({h1_lord}) and 7th lord ({h7_lord}) "
            f"are in mutual 6/8 (Shadashtaka) disposition."
        )
        reasons_tamil.append(
            f"துணை விதி 1: லக்னாதிபதியும் ({h1_lord}) 7-ம் அதிபதியும் ({h7_lord}) பரஸ்பரம் 6/8 ஷடாஷ்டக நிலையில் உள்ளனர்."
        )

    # AL and A7 tension (6/8 or 2/12 disposition)
    dist_al_a7 = (a7_sign_idx - al_sign_idx) % 12
    supplementary_al_darapada_tension = dist_al_a7 in {1, 5, 7, 11}  # 2nd/12th or 6th/8th
    
    if supplementary_al_darapada_tension:
        reasons.append(
            f"Supplementary Rule 2: Arudha Lagna ({al_sign_name}) and Darapada ({a7_sign_name}) are in "
            f"inharmonious {'6/8' if dist_al_a7 in {5, 7} else '2/12'} relationship, signifying socio-marital friction."
        )
        reasons_tamil.append(
            f"துணை விதி 2: ஆருட லக்னமும் ({SIGN_NAMES_TA[al_sign_idx]}) தாரபதமும் ({SIGN_NAMES_TA[a7_sign_idx]}) "
            f"ஒத்துவராத 6/8 அல்லது 2/12 அமைப்பில் உள்ளன."
        )

    # Count of main rules matched (0 to 4)
    main_rules_matched_count = sum([
        1 if rule_a_matched else 0,
        1 if rule_b_matched else 0,
        1 if rule_c_matched else 0,
        1 if rule_d_matched else 0,
    ])

    if main_rules_matched_count >= 3:
        discord_intensity = "High Discord Risk"
        discord_intensity_tamil = "அதிக தாம்பத்திய விரிசல் வாய்ப்பு"
    elif main_rules_matched_count == 2:
        discord_intensity = "Moderate Friction"
        discord_intensity_tamil = "மிதமான கருத்து வேறுபாடுகள்"
    elif main_rules_matched_count == 1:
        discord_intensity = "Mild / Stressful"
        discord_intensity_tamil = "சாதாரண மன அழுத்தங்கள் / தற்காலிக சங்கடங்கள்"
    else:
        discord_intensity = "Peaceful / Harmonious"
        discord_intensity_tamil = "அமைதியான மற்றும் இணக்கமான தாம்பத்தியம்"

    # -----------------------------------------------------------------------
    # Darakaraka & Shiv Raj Sharma Dasha Discord Triggers
    # -----------------------------------------------------------------------
    karakas = calculate_jaimini_7_karakas(planets_data)
    darakaraka = karakas.get("DK", "Venus")
    dk_sign = planets_data.get(darakaraka, {}).get("sign_index", 1)

    active_dasha_discord_triggers: List[str] = []
    
    # Check active Mahadasha / Antardasha lords
    h5_sign = ((lagna_sign + 3) % 12) + 1
    h5_lord = SIGN_LORDS[h5_sign]
    
    dasha_candidates = []
    if active_mahadasha:
        dasha_candidates.append(("Mahadasha", active_mahadasha))
    if active_antardasha:
        dasha_candidates.append(("Antardasha", active_antardasha))

    for level, d_lord in dasha_candidates:
        d_lord_sign = planets_data.get(d_lord, {}).get("sign_index")
        if not d_lord_sign:
            continue
            
        # Is dasha lord the 5th, 6th, or 8th lord? (Shiv Raj Sharma rule)
        if d_lord in {h5_lord, trik_lords["6th_lord"], trik_lords["8th_lord"]}:
            active_dasha_discord_triggers.append(
                f"{level} Lord {d_lord} is ruler of discord-triggering house (5th/6th/8th)"
            )
            
        # Is dasha lord placed in 6th or 8th from Lagna?
        dist_from_lagna = (d_lord_sign - lagna_sign) % 12
        if dist_from_lagna in {5, 7}:
            active_dasha_discord_triggers.append(
                f"{level} Lord {d_lord} occupies 6th/8th house from Janma Lagna"
            )
            
        # Is dasha lord placed in 6th or 8th from Darakaraka?
        dist_from_dk = (d_lord_sign - dk_sign) % 12
        if dist_from_dk in {5, 7}:
            active_dasha_discord_triggers.append(
                f"{level} Lord {d_lord} is in 6/8 Shadashtaka position from Darakaraka ({darakaraka})"
            )

    # Supriya Jagdish Darakaraka analysis
    dk_is_active_dasha = (active_mahadasha == darakaraka) or (active_antardasha == darakaraka)
    if dk_is_active_dasha:
        darakaraka_dasha_analysis = (
            f"Currently running {darakaraka} (Darakaraka) dasha period. As demonstrated in Supriya Jagdish's research, "
            f"DK periods trigger vital relationship developments: fruition of marriage when benefic influences prevail, "
            f"or profound relational recalibration if afflicted."
        )
    else:
        darakaraka_dasha_analysis = (
            f"Darakaraka is {darakaraka} (posited in {SIGN_NAMES_EN[dk_sign]}). When {darakaraka} Mahadasha or Antardasha "
            f"operates, marital fruition or intense relational transitions manifest."
        )

    return MaritalDiscordResult(
        upapada_lagna_sign=ul_sign_name,
        second_from_upapada_sign=second_from_ul_name,
        malefics_in_second_from_ul=malefics_in_second_from_ul,
        jaimini_malefic_aspects_on_second_from_ul=jaimini_malefic_aspects_on_second_from_ul,
        rule_a_matched=rule_a_matched,
        rule_b_matched=rule_b_matched,
        rule_c_matched=rule_c_matched,
        rule_d_matched=rule_d_matched,
        supplementary_shadashtaka=supplementary_shadashtaka,
        supplementary_al_darapada_tension=supplementary_al_darapada_tension,
        main_rules_matched_count=main_rules_matched_count,
        discord_intensity=discord_intensity,
        discord_intensity_tamil=discord_intensity_tamil,
        active_dasha_discord_triggers=active_dasha_discord_triggers,
        darakaraka_planet=darakaraka,
        darakaraka_dasha_analysis=darakaraka_dasha_analysis,
        reasons=reasons,
        reasons_tamil=reasons_tamil,
    )
