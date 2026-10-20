"""Main Medical Astrology calculation engine.

Orchestrates Vedic and KP medical astrology analysis cleanly, adhering to strict
ethical and safety rules:
- No medical diagnoses
- No disease onset predictions
- No lifespan predictions
- No clinical percentages or health scores
- Complete separation between Vedic and KP systems
- Classical source citations for all triggered rules
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.medical_astrology import (
    SAFETY_DISCLAIMER_EN,
    SAFETY_DISCLAIMER_TA,
    MedicalConditionItem,
    MedicalRule,
    HouseHealthAnalysis,
    AnatomicalSystemMapping,
    BirthChartPerspective,
    TransitInfluence,
    CurrentPeriodPerspective,
    HistoricalPeriodItem,
    HistoricalPeriodPerspective,
    VedicMedicalAnalysis,
    SignificatorSourceDetail,
    KpCslAnalysis,
    KpDasaSignification,
    KpMedicalAnalysis,
    MedicalAstrologyResponse,
)
from app.services.medical_astrology_engine.registry import (
    RULE_SET_VERSION,
    MEDICAL_RULES_REGISTRY,
    KALAPURUSHA_ANATOMY,
    PLANET_ANATOMY_GOVERNANCE,
    ClassicalMedicalRuleDefinition,
)
from app.services.yoga_engine.models import (
    YogaChartContext,
    SIGN_LORDS,
    OWN_SIGNS,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


def _get_planet_dignity(planet: str, sign_idx: int, is_combust: bool) -> str:
    """Helper to determine dignified status for display."""
    if is_combust:
        return "Combust (Asta)"
    if sign_idx == EXALTATION_SIGNS.get(planet):
        return "Exalted (Uccha)"
    if sign_idx == DEBILITATION_SIGNS.get(planet):
        return "Debilitated (Neecha)"
    if sign_idx in OWN_SIGNS.get(planet, set()):
        return "Own Sign (Swa-kshetra)"
    return "Normal"


def _build_house_analysis(
    house_num: int,
    ctx: YogaChartContext,
) -> HouseHealthAnalysis:
    """Build detailed analysis for a specific house (1, 6, 8, or 12)."""
    sign_idx = ctx.house_to_sign[house_num]
    sign_name_en = SIGN_NAMES_EN.get(sign_idx, f"Sign {sign_idx}")
    sign_name_ta = SIGN_NAMES_TA.get(sign_idx, f"ராசி {sign_idx}")
    lord = ctx.house_lords[house_num]
    lord_house = ctx.planet_house.get(lord)
    lord_sign_idx = ctx.planet_sign.get(lord)
    lord_sign = SIGN_NAMES_EN.get(lord_sign_idx, "") if lord_sign_idx else None

    is_combust, _, _ = ctx.get_combustion_details(lord)
    dignity = _get_planet_dignity(lord, lord_sign_idx or 0, is_combust)

    occupants = ctx.house_occupants.get(house_num, [])
    aspecting = [p for p in ctx.planet_house if ctx.planet_aspects_house(p, house_num)]

    anatomy_info = KALAPURUSHA_ANATOMY.get(sign_idx, {})
    system_en = anatomy_info.get("system_en", "General Body")
    system_ta = anatomy_info.get("system_ta", "பொது உடலமைப்பு")

    afflictions: List[str] = []
    mitigations: List[str] = []

    # Check occupants
    malefic_occupants = [p for p in occupants if p in NATURAL_MALEFICS]
    benefic_occupants = [p for p in occupants if p in NATURAL_BENEFICS]
    if malefic_occupants:
        afflictions.append(f"Occupied by natural malefic(s): {', '.join(malefic_occupants)}")
    if benefic_occupants:
        mitigations.append(f"Occupied by natural benefic(s): {', '.join(benefic_occupants)}")

    # Check aspects
    malefic_aspects = [p for p in aspecting if p in NATURAL_MALEFICS]
    benefic_aspects = [p for p in aspecting if p in NATURAL_BENEFICS]
    if malefic_aspects:
        afflictions.append(f"Aspected by natural malefic(s): {', '.join(malefic_aspects)}")
    if benefic_aspects:
        mitigations.append(f"Aspected by natural benefic(s): {', '.join(benefic_aspects)}")

    # Check lord placement & dignity
    if is_combust:
        afflictions.append(f"House lord {lord} is combust by solar proximity")
    if ctx.is_debilitated(lord):
        afflictions.append(f"House lord {lord} is debilitated in {lord_sign}")
    if ctx.is_exalted(lord):
        mitigations.append(f"House lord {lord} is exalted in {lord_sign}")
    elif lord_sign_idx in OWN_SIGNS.get(lord, set()):
        mitigations.append(f"House lord {lord} is fortified in own sign {lord_sign}")

    if lord_house in (6, 8, 12) and house_num not in (6, 8, 12):
        afflictions.append(f"House lord {lord} is placed in Dusthana house {lord_house}")

    # Generate classical summary
    if house_num == 1:
        if mitigations and not afflictions:
            summary_en = "Lagna and its lord are well-fortified, indicating robust natural vitality and strong recuperative capacity."
            summary_ta = "லக்னமும் லக்னாதிபதியும் பலம் பெற்றுள்ளதால் சிறந்த உடலமைப்பு, வலிமையான நோய் எதிர்ப்பு மற்றும் விரைவான குணமடையும் தன்மை அமைகிறது."
        elif afflictions and not mitigations:
            summary_en = "Lagna receives stress factors; classical texts advise conscious physical conditioning, balanced diet, and rest."
            summary_ta = "லக்னத்திற்கு அசுப தொடர்புகள் உள்ளதால் உடற்பயிற்சி, சத்தான உணவு மற்றும் போதுமான ஓய்வு மூலம் ஆரோக்கியத்தைப் பேண பாரம்பரிய சாஸ்திரங்கள் அறிவுறுத்துகின்றன."
        else:
            summary_en = "Lagna displays balanced vitality; natural resilience is supported by planetary mitigations."
            summary_ta = "லக்னம் சமநிலையான உடற்பலத்தைக் காட்டுகிறது; சுப பார்வைகள் மற்றும் பலங்களால் ஆரோக்கியம் பாதுகாக்கப்படுகிறது."
    elif house_num == 6:
        if malefic_occupants:
            summary_en = f"Natural malefics ({', '.join(malefic_occupants)}) in the 6th house classically bestow formidable power to conquer diseases and enemies, alongside periodic heat or inflammatory notices."
            summary_ta = f"6-ம் பாவத்தில் அசுப கிரகங்கள் ({', '.join(malefic_occupants)}) இருப்பது நோய்களை வெல்லும் அபார எதிர்ப்பு சக்தியைத் தரும்; அதேசமயம் உஷ்ண சமநிலையைப் பேணுவது நல்லது."
        elif benefic_occupants:
            summary_en = f"Natural benefics ({', '.join(benefic_occupants)}) in the 6th house protect through gentle recovery and responsiveness to healthcare guidance."
            summary_ta = f"6-ம் பாவத்தில் சுப கிரகங்கள் ({', '.join(benefic_occupants)}) இருப்பது மருத்துவ ஆலோசனைகளுக்கு சிறந்த முறையில் உடல் ஒத்துழைத்து குணமாகும் தன்மையைக் குறிக்கும்."
        else:
            summary_en = "6th house (Roga Bhava) is undisturbed by occupants, with health conditions governed primarily by its lord and aspects."
            summary_ta = "6-ம் பாவம் கிரக ஆக்கிரமிப்பு இன்றி உள்ளது; இதன் பலன்கள் அதிபதியின் நிலை மற்றும் பார்வைகளால் தீர்மானிக்கப்படுகின்றன."
    elif house_num == 8:
        if mitigations:
            summary_en = "8th house (Ayur Bhava) is protected by benefic factors, traditionally conferring longevity and cellular regeneration."
            summary_ta = "8-ம் பாவம் (ஆயுள் பாவம்) சுப தொடர்புகளால் பாதுகாக்கப்படுவதால் நீண்ட ஆயுளும், செல்களின் மீளுருவாக்கமும் உறுதி செய்யப்படுகின்றன."
        else:
            summary_en = "8th house governs chronic endurance, cellular recovery, and unexpected stress thresholds."
            summary_ta = "8-ம் பாவம் நீண்டகால சகிப்புத்தன்மை, உடல் ஆற்றல் சேமிப்பு மற்றும் திடீர் மாற்றங்களை நிர்வகிக்கிறது."
    else:  # 12
        if mitigations:
            summary_en = "12th house (Vyaya Bhava) is supported by benefics, indicating restful recuperation and quick discharge from medical facilities."
            summary_ta = "12-ம் பாவம் சுப பலம் பெற்றுள்ளதால் ஆழ்ந்த தூக்கம், சிறந்த ஓய்வு மற்றும் சிகிச்சையிலிருந்து விரைவான குணம் பெறுதல் அமையும்."
        else:
            summary_en = "12th house governs sleep quality, lymphatic drainage, and health-related expenditures."
            summary_ta = "12-ம் பாவம் தூக்கத்தின் தரம், நிணநீர் ஓட்டம் மற்றும் ஆரோக்கியத்திற்கான நற்செலவுகளைக் குறிக்கிறது."

    return HouseHealthAnalysis(
        house_number=house_num,
        sign_index=sign_idx,
        sign_name_en=sign_name_en,
        sign_name_ta=sign_name_ta,
        lord=lord,
        lord_house=lord_house,
        lord_sign=lord_sign,
        lord_dignity=dignity,
        occupants=occupants,
        aspecting_planets=aspecting,
        anatomical_system_en=system_en,
        anatomical_system_ta=system_ta,
        traditional_summary_en=summary_en,
        traditional_summary_ta=summary_ta,
        afflictions=afflictions,
        mitigations=mitigations,
    )


def _evaluate_vedic_rules(ctx: YogaChartContext) -> Tuple[List[MedicalRule], List[str]]:
    """Evaluate classical Vedic medical rules from registry."""
    triggered_rules: List[MedicalRule] = []
    conflicting_indications: List[str] = []

    # 1. BPHS single-planet in 6th
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        rule_id = f"bphs_17_{'1_sun' if planet == 'Sun' else '3_moon' if planet == 'Moon' else '5_mars' if planet == 'Mars' else '7_mercury' if planet == 'Mercury' else '9_jupiter' if planet == 'Jupiter' else '11_venus' if planet == 'Venus' else '13_saturn' if planet == 'Saturn' else '15_rahu' if planet == 'Rahu' else '16_ketu'}_6th"
        rule_def = MEDICAL_RULES_REGISTRY.get(rule_id)
        if not rule_def:
            continue

        p_house = ctx.planet_house.get(planet)
        passed = (p_house == 6)
        if passed:
            is_combust, _, _ = ctx.get_combustion_details(planet)
            triggered_rules.append(
                MedicalRule(
                    id=rule_def.id,
                    name=rule_def.name,
                    name_tamil=rule_def.name_tamil,
                    source=rule_def.source,
                    chapter_verse=rule_def.chapter_verse,
                    category=rule_def.category,
                    system=rule_def.system,
                    required_placements=rule_def.required_placements,
                    mandatory_conditions=rule_def.mandatory_conditions,
                    traditional_interpretation=rule_def.traditional_interpretation,
                    interpretation_tamil=rule_def.interpretation_tamil,
                    anatomical_system=rule_def.anatomical_system,
                    modifiers=rule_def.modifiers,
                    conflicting_indications=rule_def.conflicting_indications,
                    is_active=True,
                    status="Qualifying",
                    triggered_positions=[f"{planet} in House 6 ({SIGN_NAMES_EN.get(ctx.planet_sign.get(planet, 0), '')})"],
                    planets_involved=[planet],
                    relevant_houses=[6],
                    conditions=[
                        MedicalConditionItem(
                            condition=f"{planet} occupies House 6 from Lagna",
                            passed=True,
                            detail=f"{planet} is located at House 6 ({ctx.planet_sign.get(planet)}° {SIGN_NAMES_EN.get(ctx.planet_sign.get(planet, 0), '')})"
                        )
                    ],
                )
            )

    # 2. House Lords
    # 6th lord in Lagna
    l6 = ctx.house_lords[6]
    h_l6 = ctx.planet_house.get(l6)
    if h_l6 == 1:
        r_def = MEDICAL_RULES_REGISTRY["bphs_17_17_lord6_in_1"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th Lord {l6} placed in House 1 (Lagna)"],
                planets_involved=[l6],
                relevant_houses=[1, 6],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Lord placed in 1st house",
                        passed=True,
                        detail=f"{l6} (Lord of 6) resides in House 1."
                    )
                ],
            )
        )

    # 6th lord in 6th (Harsha)
    if h_l6 == 6:
        r_def = MEDICAL_RULES_REGISTRY["bphs_17_22_lord6_in_6"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th Lord {l6} in own House 6"],
                planets_involved=[l6],
                relevant_houses=[6],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Lord in 6th house (Swa-kshetra)",
                        passed=True,
                        detail=f"{l6} occupies House 6 in its own rashi."
                    )
                ],
            )
        )

    # 6th lord in 8th
    if h_l6 == 8:
        r_def = MEDICAL_RULES_REGISTRY["bphs_17_24_lord6_in_8"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th Lord {l6} placed in House 8"],
                planets_involved=[l6],
                relevant_houses=[6, 8],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Lord placed in 8th house",
                        passed=True,
                        detail=f"{l6} resides in House 8."
                    )
                ],
            )
        )

    # 6th lord in 12th
    if h_l6 == 12:
        r_def = MEDICAL_RULES_REGISTRY["bphs_17_28_lord6_in_12"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th Lord {l6} placed in House 12"],
                planets_involved=[l6],
                relevant_houses=[6, 12],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Lord placed in 12th house",
                        passed=True,
                        detail=f"{l6} resides in House 12."
                    )
                ],
            )
        )

    # Lagna lord in 6th
    l1 = ctx.house_lords[1]
    h_l1 = ctx.planet_house.get(l1)
    if h_l1 == 6:
        r_def = MEDICAL_RULES_REGISTRY["bphs_17_29_lagna_lord_in_6"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"Lagna Lord {l1} placed in House 6"],
                planets_involved=[l1],
                relevant_houses=[1, 6],
                conditions=[
                    MedicalConditionItem(
                        condition="Lagna Lord placed in 6th house",
                        passed=True,
                        detail=f"{l1} resides in House 6."
                    )
                ],
            )
        )

    # 3. Two-Planet Combinations
    # Sun - Saturn
    sun_h = ctx.planet_house.get("Sun")
    sat_h = ctx.planet_house.get("Saturn")
    if sun_h and sat_h:
        are_conjoined = (sun_h == sat_h)
        are_opposed = (((sat_h - sun_h) % 12) + 1 == 7)
        if are_conjoined or are_opposed:
            r_def = MEDICAL_RULES_REGISTRY["saravali_sun_saturn"]
            rel_txt = "conjunction" if are_conjoined else "mutual opposition (7th aspect)"
            triggered_rules.append(
                MedicalRule(
                    id=r_def.id,
                    name=r_def.name,
                    name_tamil=r_def.name_tamil,
                    source=r_def.source,
                    chapter_verse=r_def.chapter_verse,
                    category=r_def.category,
                    system=r_def.system,
                    required_placements=r_def.required_placements,
                    mandatory_conditions=r_def.mandatory_conditions,
                    traditional_interpretation=r_def.traditional_interpretation,
                    interpretation_tamil=r_def.interpretation_tamil,
                    anatomical_system=r_def.anatomical_system,
                    modifiers=r_def.modifiers,
                    conflicting_indications=r_def.conflicting_indications,
                    is_active=True,
                    status="Qualifying",
                    triggered_positions=[f"Sun in H{sun_h} and Saturn in H{sat_h} ({rel_txt})"],
                    planets_involved=["Sun", "Saturn"],
                    relevant_houses=[sun_h, sat_h],
                    conditions=[
                        MedicalConditionItem(
                            condition="Sun and Saturn in mutual aspect or conjunction",
                            passed=True,
                            detail=f"Sun in House {sun_h}, Saturn in House {sat_h} ({rel_txt})."
                        )
                    ],
                )
            )

    # Mars - Saturn
    mars_h = ctx.planet_house.get("Mars")
    if mars_h and sat_h:
        m_s_conjoined = (mars_h == sat_h)
        m_s_opposed = (((sat_h - mars_h) % 12) + 1 in {4, 7, 8}) or (((mars_h - sat_h) % 12) + 1 in {3, 7, 10})
        if m_s_conjoined or m_s_opposed:
            r_def = MEDICAL_RULES_REGISTRY["saravali_mars_saturn"]
            rel_txt = "conjunction" if m_s_conjoined else "mutual aspect"
            triggered_rules.append(
                MedicalRule(
                    id=r_def.id,
                    name=r_def.name,
                    name_tamil=r_def.name_tamil,
                    source=r_def.source,
                    chapter_verse=r_def.chapter_verse,
                    category=r_def.category,
                    system=r_def.system,
                    required_placements=r_def.required_placements,
                    mandatory_conditions=r_def.mandatory_conditions,
                    traditional_interpretation=r_def.traditional_interpretation,
                    interpretation_tamil=r_def.interpretation_tamil,
                    anatomical_system=r_def.anatomical_system,
                    modifiers=r_def.modifiers,
                    conflicting_indications=r_def.conflicting_indications,
                    is_active=True,
                    status="Qualifying",
                    triggered_positions=[f"Mars in H{mars_h} and Saturn in H{sat_h} ({rel_txt})"],
                    planets_involved=["Mars", "Saturn"],
                    relevant_houses=[mars_h, sat_h],
                    conditions=[
                        MedicalConditionItem(
                            condition="Mars and Saturn in conjunction or mutual aspect",
                            passed=True,
                            detail=f"Mars in House {mars_h}, Saturn in House {sat_h} ({rel_txt})."
                        )
                    ],
                )
            )

    # Moon - Rahu / Ketu
    moon_h = ctx.planet_house.get("Moon")
    rahu_h = ctx.planet_house.get("Rahu")
    ketu_h = ctx.planet_house.get("Ketu")
    if moon_h and (moon_h == rahu_h or moon_h == ketu_h):
        r_def = MEDICAL_RULES_REGISTRY["phaladeepika_moon_rahu"]
        nodal = "Rahu" if moon_h == rahu_h else "Ketu"
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"Moon conjoined {nodal} in House {moon_h}"],
                planets_involved=["Moon", nodal],
                relevant_houses=[moon_h],
                conditions=[
                    MedicalConditionItem(
                        condition=f"Moon conjoined {nodal} in the same house",
                        passed=True,
                        detail=f"Moon and {nodal} both occupy House {moon_h}."
                    )
                ],
            )
        )

    # Three-planet combination: Sun, Mars, Saturn in Dusthanas (6, 8, 12)
    dusthanas = {6, 8, 12}
    if sun_h in dusthanas and mars_h in dusthanas and sat_h in dusthanas:
        r_def = MEDICAL_RULES_REGISTRY["bphs_three_malefics_dusthana"]
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"Sun in H{sun_h}, Mars in H{mars_h}, Saturn in H{sat_h}"],
                planets_involved=["Sun", "Mars", "Saturn"],
                relevant_houses=[sun_h, mars_h, sat_h],
                conditions=[
                    MedicalConditionItem(
                        condition="Sun, Mars, and Saturn all located in Dusthana houses (6, 8, 12)",
                        passed=True,
                        detail=f"Sun in H{sun_h}, Mars in H{mars_h}, Saturn in H{sat_h}."
                    )
                ],
            )
        )

    # 4. Mitigations / Arishta Bhanga
    # Jupiter aspecting House 1 or House 6
    jup_h = ctx.planet_house.get("Jupiter")
    is_jup_combust, _, _ = ctx.get_combustion_details("Jupiter")
    if jup_h and not is_jup_combust:
        jup_aspects_h1 = (1 in [((jup_h - 1 + n - 1) % 12) + 1 for n in (5, 7, 9)])
        jup_aspects_h6 = (6 in [((jup_h - 1 + n - 1) % 12) + 1 for n in (5, 7, 9)])
        if jup_aspects_h1 or jup_aspects_h6:
            r_def = MEDICAL_RULES_REGISTRY["arishta_bhanga_jupiter_aspect"]
            targ = "House 1 (Lagna)" if jup_aspects_h1 else "House 6 (Roga Bhava)"
            if jup_aspects_h1 and jup_aspects_h6:
                targ = "both House 1 and House 6"
            conflicting_indications.append(
                f"Classical Mitigation: Jupiter in H{jup_h} casts aspect on {targ}, conferring Arishta Bhanga immunity protection."
            )
            triggered_rules.append(
                MedicalRule(
                    id=r_def.id,
                    name=r_def.name,
                    name_tamil=r_def.name_tamil,
                    source=r_def.source,
                    chapter_verse=r_def.chapter_verse,
                    category=r_def.category,
                    system=r_def.system,
                    required_placements=r_def.required_placements,
                    mandatory_conditions=r_def.mandatory_conditions,
                    traditional_interpretation=r_def.traditional_interpretation,
                    interpretation_tamil=r_def.interpretation_tamil,
                    anatomical_system=r_def.anatomical_system,
                    modifiers=r_def.modifiers,
                    conflicting_indications=r_def.conflicting_indications,
                    is_active=True,
                    status="Qualifying",
                    triggered_positions=[f"Jupiter in H{jup_h} aspecting {targ}"],
                    planets_involved=["Jupiter"],
                    relevant_houses=[jup_h, 1 if jup_aspects_h1 else 6],
                    conditions=[
                        MedicalConditionItem(
                            condition="Uncombust Jupiter aspects House 1 or House 6",
                            passed=True,
                            detail=f"Jupiter in House {jup_h} aspects {targ}."
                        )
                    ],
                )
            )

    # Benefics in Kendras (1, 4, 7, 10)
    kendra_benefics = []
    for b in ("Jupiter", "Venus", "Mercury"):
        bh = ctx.planet_house.get(b)
        if bh in (1, 4, 7, 10):
            kendra_benefics.append((b, bh))

    if kendra_benefics:
        r_def = MEDICAL_RULES_REGISTRY["arishta_bhanga_benefics_kendras"]
        ben_str = ", ".join(f"{b} in H{h}" for b, h in kendra_benefics)
        conflicting_indications.append(
            f"Classical Longevity Citadel: Natural benefics in quadrant houses ({ben_str}) sustain constitutional vitality."
        )
        triggered_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=r_def.anatomical_system,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[ben_str],
                planets_involved=[b for b, _ in kendra_benefics],
                relevant_houses=[h for _, h in kendra_benefics],
                conditions=[
                    MedicalConditionItem(
                        condition="At least one natural benefic occupies a Kendra house (1, 4, 7, 10)",
                        passed=True,
                        detail=f"Benefics in Kendras: {ben_str}."
                    )
                ],
            )
        )

    return triggered_rules, conflicting_indications


def _build_anatomical_mappings(ctx: YogaChartContext) -> List[AnatomicalSystemMapping]:
    """Map 12-sign Kalapurusha anatomical zones to chart status."""
    mappings: List[AnatomicalSystemMapping] = []

    for sign_idx in range(1, 13):
        sign_info = KALAPURUSHA_ANATOMY[sign_idx]
        house_num = ctx.sign_to_house.get(sign_idx, 0)
        occupants = ctx.sign_occupants.get(sign_idx, [])

        malefics = [p for p in occupants if p in NATURAL_MALEFICS]
        benefics = [p for p in occupants if p in NATURAL_BENEFICS]

        if malefics and not benefics:
            status = "Afflicted"
            obs_en = f"Occupied by natural malefic(s) ({', '.join(malefics)}) in House {house_num}; classical texts suggest mindful care of {sign_info['organs_en']}."
            obs_ta = f"வீடு {house_num}-ல் அசுப கிரகங்கள் ({', '.join(malefics)}) உள்ளதால் {sign_info['organs_ta']} பகுதியில் கவனமும் பராமரிப்பும் தேவை."
        elif benefics and not malefics:
            status = "Mitigated"
            obs_en = f"Benefic presence ({', '.join(benefics)}) in House {house_num} nourishes and protects this anatomical zone."
            obs_ta = f"வீடு {house_num}-ல் சுப கிரகங்கள் ({', '.join(benefics)}) அமர்ந்து இந்த உடல் பகுதியை பலப்படுத்துகின்றன."
        elif benefics and malefics:
            status = "Balanced"
            obs_en = f"Mixed influences ({', '.join(occupants)}) in House {house_num}; malefic strain is mitigated by benefic presence."
            obs_ta = f"வீடு {house_num}-ல் சுப மற்றும் அசுப கிரகங்களின் கலவையான தாக்கம் காணப்படுகிறது."
        else:
            status = "Neutral"
            obs_en = f"No direct planetary occupants in House {house_num}; functions in accordance with sign lord {sign_info['lord']}."
            obs_ta = f"நேரடி கிரக ஆக்கிரமிப்பு இன்றி உள்ளது; ராசிநாதன் {sign_info['lord']}-ன் நிலைக்கு ஏற்ப செயல்படுகிறது."

        mappings.append(
            AnatomicalSystemMapping(
                system_name_en=sign_info["system_en"],
                system_name_ta=sign_info["system_ta"],
                organs_en=sign_info["organs_en"],
                organs_ta=sign_info["organs_ta"],
                sign_governance=f"{sign_info['sign_en']} ({sign_idx})",
                planetary_governance=f"{sign_info['lord']} (Natural: {sign_info['humor']})",
                status=status,
                observations_en=obs_en,
                observations_ta=obs_ta,
            )
        )

    return mappings


def _build_current_period_perspective(
    dasa: Optional[Any],
    live_transits: Optional[Any],
    lagna_sign_idx: int,
    ctx: YogaChartContext,
) -> CurrentPeriodPerspective:
    """Build Perspective B: Current-period research."""
    maha_lord = "Unknown"
    bhukti_lord = None
    antara_lord = None
    start_iso = None
    end_iso = None

    # Extract active period from dasa
    if dasa:
        active = getattr(dasa, "active_period", None)
        if isinstance(active, dict):
            maha_lord = active.get("mahadasha", "Unknown")
            bhukti_lord = active.get("antardasha")
            antara_lord = active.get("pratyantardasha")
            start_iso = active.get("target_date_iso")
        elif hasattr(active, "mahadasha"):
            maha_lord = active.mahadasha
            bhukti_lord = getattr(active, "antardasha", None)
            antara_lord = getattr(active, "pratyantardasha", None)
            start_iso = getattr(active, "target_date_iso", None)
        elif hasattr(dasa, "birth_dasa_lord"):
            maha_lord = dasa.birth_dasa_lord

    # Match rules for active lords
    matching_rules: List[MedicalRule] = []
    active_lords = [l for l in (maha_lord, bhukti_lord, antara_lord) if l and l != "Unknown"]
    for l in active_lords:
        gov = PLANET_ANATOMY_GOVERNANCE.get(l, {})
        matching_rules.append(
            MedicalRule(
                id=f"active_period_{l.lower()}",
                name=f"Vimshottari Period of {l} (Classical Anatomical Resonance)",
                name_tamil=f"{l} தசா-புத்தி காலம் (பாரம்பரிய உடல் உறுப்புத் தொடர்பு)",
                source="Brihat Parashara Hora Shastra & Phaladeepika",
                chapter_verse="BPHS Dasa Phala Adhyaya; Phaladeepika Ch. 20",
                category="Vedic Birth Chart",
                system="vedic",
                required_placements=f"Active period ruled by {l}",
                mandatory_conditions=[f"{l} is currently operating as Dasa or Bhukti lord"],
                traditional_interpretation=(
                    f"Under the rulership of {l}, classical texts observe traditional focus on the {gov.get('organs_en', 'governed organs')}. "
                    f"Its natural humor is {gov.get('dosha', 'Tridosha')}. A well-placed {l} enhances systemic vitality, "
                    f"while afflicted placements suggest attention to rest and moderation."
                ),
                interpretation_tamil=(
                    f"{l} தசா-புத்தி காலத்தில் {gov.get('organs_ta', 'உடல் உறுப்புகள்')} மீது பாரம்பரிய கவனம் செலுத்தப்படுகிறது. "
                    f"இதன் சுபாவம் {gov.get('dosha', 'தோஷம்')} ஆகும். {l} பலம் பெற்றிருந்தால் உடல் வலிமை கூடும்."
                ),
                anatomical_system=gov.get("organs_en", "General Vitality"),
                modifiers=f"{l} occupies House {ctx.planet_house.get(l, 0)} in natal chart.",
                conflicting_indications="Jupiter aspect on period lord ensures swift resolution of temporary fatigue.",
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"{l} is currently active period lord"],
                planets_involved=[l],
                relevant_houses=[ctx.planet_house.get(l, 0)],
                conditions=[
                    MedicalConditionItem(
                        condition=f"{l} is active Dasa/Bhukti ruler",
                        passed=True,
                        detail=f"{l} rules the current temporal astrological window."
                    )
                ],
            )
        )

    # Process verified live transits if available
    transits_list: List[TransitInfluence] = []
    if live_transits:
        planets_data = getattr(live_transits, "planets", [])
        if isinstance(planets_data, list):
            for tp in planets_data[:9]:
                name = getattr(tp, "name", None) or (tp.get("name") if isinstance(tp, dict) else "")
                sign_idx = getattr(tp, "sign_index", None) or (tp.get("sign_index") if isinstance(tp, dict) else 1)
                deg = getattr(tp, "degree_in_sign", None) or (tp.get("degree_in_sign") if isinstance(tp, dict) else 0.0)
                is_retro = bool(getattr(tp, "is_retrograde", False) or (tp.get("is_retrograde") if isinstance(tp, dict) else False))

                if name and sign_idx:
                    house_from_lagna = ((sign_idx - lagna_sign_idx + 12) % 12) + 1
                    s_name_en = SIGN_NAMES_EN.get(sign_idx, "")
                    s_name_ta = SIGN_NAMES_TA.get(sign_idx, "")

                    symbolism_en = f"Transiting {s_name_en} (H{house_from_lagna} from Lagna)"
                    symbolism_ta = f"லக்னத்திலிருந்து {house_from_lagna}-ம் வீடான {s_name_ta}-ல் கோசாரம் செய்கிறது"

                    transits_list.append(
                        TransitInfluence(
                            planet=name,
                            sign_index=sign_idx,
                            sign_name_en=s_name_en,
                            sign_name_ta=s_name_ta,
                            degree=round(float(deg), 2),
                            house_from_lagna=house_from_lagna,
                            is_retrograde=is_retro,
                            traditional_symbolism_en=symbolism_en,
                            traditional_symbolism_ta=symbolism_ta,
                        )
                    )

    synth_en = (
        f"Active Vimshottari period is governed by {maha_lord}"
        + (f" with Bhukti of {bhukti_lord}" if bhukti_lord else "")
        + (f" and Antara of {antara_lord}" if antara_lord else "")
        + ". In traditional astrological research, health vitality during this temporal window "
        "is interpreted according to the natural humors and house lordships of these planets. "
        "This is an educational astrological perspective and does not forecast illness onset."
    )
    synth_ta = (
        f"நடப்பு விம்சோத்தரி தசா நாதர்: {maha_lord}"
        + (f", புத்தி நாதர்: {bhukti_lord}" if bhukti_lord else "")
        + (f", அந்தர நாதர்: {antara_lord}" if antara_lord else "")
        + ". பாரம்பரிய ஜோதிட ஆராய்ச்சியின்படி இக்காலகட்டத்தின் உடல் பலம் இந்நாதர்களின் சுபாவம் மற்றும் "
        "ஆதிபத்தியங்களின் அடிப்படையில் விவரிக்கப்படுகிறது. இது கல்வி நோக்கிலான ஆய்வு மட்டுமே; நோயைக் கணிப்பது அல்ல."
    )

    return CurrentPeriodPerspective(
        mahadasha=maha_lord,
        bhukti=bhukti_lord,
        antara=antara_lord,
        start_date_iso=start_iso,
        end_date_iso=end_iso,
        matching_rules=matching_rules,
        transits=transits_list,
        traditional_synthesis_en=synth_en,
        traditional_synthesis_ta=synth_ta,
    )


def _build_historical_period_perspective(
    dasa: Optional[Any],
    ctx: YogaChartContext,
) -> HistoricalPeriodPerspective:
    """Build Perspective C: Historical period research."""
    periods: List[HistoricalPeriodItem] = []
    tree = getattr(dasa, "dasa_tree", []) if dasa else []

    if isinstance(tree, list):
        for node in tree[:9]:  # Up to 9 Mahadashas
            lord = getattr(node, "lord", None) or (node.get("lord") if isinstance(node, dict) else "")
            start_iso = getattr(node, "start_date_iso", None) or (node.get("start_date_iso") if isinstance(node, dict) else "")
            end_iso = getattr(node, "end_date_iso", None) or (node.get("end_date_iso") if isinstance(node, dict) else "")
            start_age = getattr(node, "start_age", None) or (node.get("start_age") if isinstance(node, dict) else "")
            end_age = getattr(node, "end_age", None) or (node.get("end_age") if isinstance(node, dict) else "")

            age_str = f"Age {start_age} – {end_age}" if start_age and end_age else "Documented span"

            gov = PLANET_ANATOMY_GOVERNANCE.get(lord, {})
            notes_en = (
                f"Historical Vimshottari Mahadasha of {lord}. Classical texts associate this planetary phase with "
                f"{gov.get('organs_en', 'vital reserves')}. Astrological records trace bodily rhythm shifts without "
                "inferring diagnosed historical ailments."
            )
            notes_ta = (
                f"{lord} மகா தசை காலம். பாரம்பரிய நூல்கள் இக்காலகட்டத்தை {gov.get('organs_ta', 'உடற்பலம்')}-உடன் "
                "தொடர்புபடுத்துகின்றன. இது கடந்த கால ஜோதிட ஆய்வு மட்டுமே; கடந்த கால நோய்களைக் குறிப்பது அல்ல."
            )

            periods.append(
                HistoricalPeriodItem(
                    period_name=f"{lord} Mahadasha",
                    lord=lord,
                    sub_lord=None,
                    start_date_iso=str(start_iso or ""),
                    end_date_iso=str(end_iso or ""),
                    age_range=age_str,
                    traditional_rules=[],
                    traditional_notes_en=notes_en,
                    traditional_notes_ta=notes_ta,
                )
            )

    return HistoricalPeriodPerspective(periods=periods)


def _evaluate_kp_medical(
    kp: Optional[Any],
    dasa: Optional[Any],
) -> Optional[KpMedicalAnalysis]:
    """Evaluate clean-room KP Medical Astrology using documented CSL rules."""
    if not kp:
        return None

    cuspal = getattr(kp, "cuspal_analysis", None) or (kp.get("cuspal_analysis") if isinstance(kp, dict) else [])
    if not isinstance(cuspal, list) or len(cuspal) < 6:
        return None

    # 1. Planetary positions map (to resolve CSL planet's Star Lord)
    planet_map: Dict[str, Any] = {}
    planets_list = getattr(kp, "planetary_positions", None) or (kp.get("planetary_positions") if isinstance(kp, dict) else [])
    if isinstance(planets_list, list):
        for p in planets_list:
            p_name = getattr(p, "planet", None) or (p.get("planet") if isinstance(p, dict) else "")
            if p_name:
                planet_map[p_name] = p

    # 2. Get Cusp details map
    cusp_map: Dict[int, Any] = {}
    for c in cuspal:
        h = getattr(c, "house", None) or (c.get("house") if isinstance(c, dict) else 0)
        cusp_map[h] = c

    # 3. Helper to get significators for a planet from kp
    sig_map: Dict[str, List[int]] = {}
    sig_details_map: Dict[str, List[SignificatorSourceDetail]] = {}

    significators = getattr(kp, "significators", None) or (kp.get("significators") if isinstance(kp, dict) else [])
    if isinstance(significators, list):
        for s in significators:
            p_name = getattr(s, "planet", None) or (s.get("planet") if isinstance(s, dict) else "")
            if not p_name:
                continue

            houses: Set[int] = set()
            details: List[SignificatorSourceDetail] = []

            # Primary field: signified_houses
            sh = getattr(s, "signified_houses", None) or (s.get("signified_houses") if isinstance(s, dict) else [])
            if isinstance(sh, (list, set, tuple)):
                for x in sh:
                    try:
                        houses.add(int(x))
                    except (ValueError, TypeError):
                        pass

            # Strength order / mechanisms
            so = getattr(s, "strength_order", None) or (s.get("strength_order") if isinstance(s, dict) else [])
            if isinstance(so, list):
                for entry in so:
                    h_num = getattr(entry, "house", None) or (entry.get("house") if isinstance(entry, dict) else 0)
                    t_type = getattr(entry, "type", None) or (entry.get("type") if isinstance(entry, dict) else "")
                    if h_num:
                        try:
                            h_int = int(h_num)
                            houses.add(h_int)
                            p_obj = planet_map.get(p_name)
                            p_star = getattr(p_obj, "star_lord", "") or (p_obj.get("star_lord", "") if isinstance(p_obj, dict) else "")
                            
                            if t_type == "StarLord":
                                lvl_en = "Level 1 / 3 (Star Lord Agency)"
                                lvl_ta = "நிலை 1 / 3 (நட்சத்திர நாதர் வழி காரகம்)"
                                channel = f"{p_name} -> {p_star}" if p_star else f"{p_name} (Star Lord)"
                                desc_en = f"{p_name} signifies House {h_int} through star lord {p_star or 'agency'}."
                                desc_ta = f"{p_name} தனது நட்சத்திர நாதர் {p_star or ''} மூலம் {h_int}-ம் பாவத்தைக் குறிக்கிறது."
                            elif t_type == "Occupant":
                                lvl_en = "Level 2 (Planetary Occupation)"
                                lvl_ta = "நிலை 2 (நேரடி பாவக அமர்வு)"
                                channel = f"{p_name} (Direct)"
                                desc_en = f"{p_name} physically occupies House {h_int} in Placidus sidereal division."
                                desc_ta = f"{p_name} நேரடி பாகைப்படி {h_int}-ம் பாவத்தில் அமர்ந்துள்ளது."
                            elif t_type == "Owner":
                                lvl_en = "Level 4 (House Ownership / Lordship)"
                                lvl_ta = "நிலை 4 (பாவக ஆதிபத்தியம் / உரிமை)"
                                channel = f"{p_name} (Lord)"
                                desc_en = f"{p_name} rules the sign on the cusp of House {h_int}."
                                desc_ta = f"{p_name} {h_int}-ம் பாவ ஆரம்ப முனையின் ராசி நாதராக விளங்குகிறது."
                            else:
                                lvl_en = f"Significator ({t_type})"
                                lvl_ta = f"காரகம் ({t_type})"
                                channel = f"{p_name} ({t_type})"
                                desc_en = f"{p_name} signifies House {h_int} via {t_type}."
                                desc_ta = f"{p_name} {t_type} வாயிலாக {h_int}-ம் பாவத்தைக் குறிக்கிறது."

                            details.append(SignificatorSourceDetail(
                                house=h_int,
                                source_type=str(t_type),
                                planet_channel=channel,
                                level_name_en=lvl_en,
                                level_name_ta=lvl_ta,
                                description_en=desc_en,
                                description_ta=desc_ta,
                            ))
                        except (ValueError, TypeError):
                            pass

            # Fallback check for level_a/b/c/d on s
            for lvl_attr, s_type, lvl_label_en, lvl_label_ta in [
                ("level_a", "StarLord", "Level A (Star of Occupant)", "நிலை A (அமர்ந்த கிரகத்தின் நட்சத்திரம்)"),
                ("level_b", "Occupant", "Level B (Occupant)", "நிலை B (நேரடி அமர்வு)"),
                ("level_c", "StarLord", "Level C (Star of House Lord)", "நிலை C (அதிபதியின் நட்சத்திரம்)"),
                ("level_d", "Owner", "Level D (House Lord)", "நிலை D (பாவக அதிபதி)"),
            ]:
                val = getattr(s, lvl_attr, None) or (s.get(lvl_attr) if isinstance(s, dict) else [])
                if isinstance(val, (list, set, tuple)):
                    for h_val in val:
                        if isinstance(h_val, int):
                            houses.add(h_val)
                            if not any(d.house == h_val and d.source_type == s_type for d in details):
                                p_obj = planet_map.get(p_name)
                                p_star = getattr(p_obj, "star_lord", "") or (p_obj.get("star_lord", "") if isinstance(p_obj, dict) else "")
                                channel = f"{p_name} -> {p_star}" if (s_type == "StarLord" and p_star) else f"{p_name} ({s_type})"
                                details.append(SignificatorSourceDetail(
                                    house=h_val,
                                    source_type=s_type,
                                    planet_channel=channel,
                                    level_name_en=lvl_label_en,
                                    level_name_ta=lvl_label_ta,
                                    description_en=f"{p_name} signifies House {h_val} via {lvl_label_en}.",
                                    description_ta=f"{p_name} {lvl_label_ta} வாயிலாக {h_val}-ம் பாவத்தைக் குறிக்கிறது.",
                                ))

            sig_map[p_name] = sorted(list(houses))
            sig_details_map[p_name] = details

    # 4. Complement with house_significators (Bhaav Nirdeshan)
    house_significators = getattr(kp, "house_significators", None) or (kp.get("house_significators") if isinstance(kp, dict) else [])
    if isinstance(house_significators, list):
        for hs in house_significators:
            h_num = getattr(hs, "house", None) or (hs.get("house") if isinstance(hs, dict) else 0)
            if not h_num:
                continue
            for lvl_name, s_type, lvl_en, lvl_ta in [
                ("level_a", "StarLord", "Level A (Star of Occupant)", "நிலை A (அமர்ந்த கிரகத்தின் நட்சத்திரம்)"),
                ("level_b", "Occupant", "Level B (House Occupant)", "நிலை B (நேரடி பாவக அமர்வு)"),
                ("level_c", "StarLord", "Level C (Star of House Lord)", "நிலை C (அதிபதியின் நட்சத்திரம்)"),
                ("level_d", "Owner", "Level D (House Lord)", "நிலை D (பாவக அதிபதி)"),
            ]:
                p_list = getattr(hs, lvl_name, None) or (hs.get(lvl_name) if isinstance(hs, dict) else [])
                if isinstance(p_list, (list, set, tuple)):
                    for pl in p_list:
                        if isinstance(pl, str) and pl:
                            if pl not in sig_map:
                                sig_map[pl] = []
                            if h_num not in sig_map[pl]:
                                sig_map[pl].append(h_num)
                                sig_map[pl].sort()
                            if pl not in sig_details_map:
                                sig_details_map[pl] = []
                            if not any(d.house == h_num and d.source_type == s_type for d in sig_details_map[pl]):
                                pl_obj = planet_map.get(pl)
                                pl_star = getattr(pl_obj, "star_lord", "") or (pl_obj.get("star_lord", "") if isinstance(pl_obj, dict) else "")
                                channel = f"{pl} -> {pl_star}" if (s_type == "StarLord" and pl_star) else f"{pl} ({s_type})"
                                sig_details_map[pl].append(SignificatorSourceDetail(
                                    house=h_num,
                                    source_type=s_type,
                                    planet_channel=channel,
                                    level_name_en=lvl_en,
                                    level_name_ta=lvl_ta,
                                    description_en=f"{pl} signifies House {h_num} as {lvl_en}.",
                                    description_ta=f"{pl} {lvl_ta} வாயிலாக {h_num}-ம் பாவத்தைக் குறிக்கிறது.",
                                ))

    def analyze_cusp(h_num: int) -> KpCslAnalysis:
        cd = cusp_map.get(h_num)
        if not cd:
            return KpCslAnalysis(
                cusp_number=h_num,
                csl_planet="Unavailable",
                csl_star_lord="Unavailable",
                star_lord="Unavailable",
                primary_signification_en=f"Cusp {h_num} data unavailable in KP chart.",
                primary_signification_ta=f"கே.பி. அட்டவணையில் {h_num}-ம் பாவத் தரவு கிடைக்கவில்லை.",
                anatomical_rulership_en="General Bodily Zone",
                anatomical_rulership_ta="பொது உடலமைப்பு",
                recovery_status="data_unavailable",
                disease_status="data_unavailable",
                chronic_status="data_unavailable",
                hospitalization_status="data_unavailable",
                recovery_signified=False,
                disease_signified=False,
                chronic_signified=False,
                hospitalization_signified=False,
                is_data_available=False,
                missing_data_reason=f"Cusp {h_num} not found in KP cuspal analysis",
            )

        csl = getattr(cd, "sub_lord", "") or (cd.get("sub_lord", "") if isinstance(cd, dict) else "")
        cusp_star_l = getattr(cd, "star_lord", "") or (cd.get("star_lord", "") if isinstance(cd, dict) else "")
        cusp_deg = getattr(cd, "cusp_degree", None) or (cd.get("cusp_degree") if isinstance(cd, dict) else None)
        sign_n = getattr(cd, "sign_name", None) or (cd.get("sign_name") if isinstance(cd, dict) else None)
        sign_l = getattr(cd, "sign_lord", None) or (cd.get("sign_lord") if isinstance(cd, dict) else None)
        sub_sub_l = getattr(cd, "sub_sub_lord", None) or (cd.get("sub_sub_lord") if isinstance(cd, dict) else None)

        if not csl:
            return KpCslAnalysis(
                cusp_number=h_num,
                cusp_degree=cusp_deg,
                sign_name=sign_n,
                sign_lord=sign_l,
                cusp_star_lord=cusp_star_l,
                csl_planet="Unavailable",
                csl_star_lord="Unavailable",
                star_lord="Unavailable",
                primary_signification_en=f"Sub-Lord for Cusp {h_num} is unavailable in KP chart.",
                primary_signification_ta=f"{h_num}-ம் பாவ உப அதிபதி (CSL) கே.பி. அட்டவணையில் கிடைக்கவில்லை.",
                anatomical_rulership_en="General Bodily Zone",
                anatomical_rulership_ta="பொது உடலமைப்பு",
                recovery_status="data_unavailable",
                disease_status="data_unavailable",
                chronic_status="data_unavailable",
                hospitalization_status="data_unavailable",
                recovery_signified=False,
                disease_signified=False,
                chronic_signified=False,
                hospitalization_signified=False,
                is_data_available=False,
                missing_data_reason=f"Sub-Lord (CSL) missing for Cusp {h_num}",
            )

        # Star lord of the CSL planet from planetary positions
        csl_planet_data = planet_map.get(csl)
        csl_star_l = (
            getattr(csl_planet_data, "star_lord", "")
            or (csl_planet_data.get("star_lord", "") if isinstance(csl_planet_data, dict) else "")
            or cusp_star_l
        )

        houses_sig = sig_map.get(csl, [])
        details_sig = sig_details_map.get(csl, [])

        if not houses_sig:
            return KpCslAnalysis(
                cusp_number=h_num,
                cusp_degree=cusp_deg,
                sign_name=sign_n,
                sign_lord=sign_l,
                cusp_star_lord=cusp_star_l,
                csl_planet=csl,
                csl_star_lord=csl_star_l,
                star_lord=csl_star_l,
                sub_lord=sub_sub_l,
                signified_houses=[],
                signification_details=[],
                primary_signification_en=f"Cusp {h_num} Sub-Lord is {csl} (in star of {csl_star_l}), but planetary house significations are unavailable.",
                primary_signification_ta=f"{h_num}-ம் பாவ CSL {csl} ({csl_star_l} நட்சத்திரம்); ஆனால் பாவகக் காரகத்துவத் தரவுகள் கிடைக்கவில்லை.",
                anatomical_rulership_en="General Bodily Zone",
                anatomical_rulership_ta="பொது உடலமைப்பு",
                recovery_status="data_unavailable",
                disease_status="data_unavailable",
                chronic_status="data_unavailable",
                hospitalization_status="data_unavailable",
                recovery_signified=False,
                disease_signified=False,
                chronic_signified=False,
                hospitalization_signified=False,
                is_data_available=False,
                missing_data_reason=f"House significations unavailable for CSL planet {csl}",
            )

        rec_houses = [h for h in (1, 5, 11) if h in houses_sig]
        dis_houses = [6] if 6 in houses_sig else []
        chr_houses = [8] if 8 in houses_sig else []
        hosp_houses = [12] if 12 in houses_sig else []

        rec = len(rec_houses) > 0
        dis = len(dis_houses) > 0
        chr_aff = len(chr_houses) > 0
        hosp = len(hosp_houses) > 0

        rec_status = "present" if rec else "not_found"
        dis_status = "present" if dis else "not_found"
        chr_status = "present" if chr_aff else "not_found"
        hosp_status = "present" if hosp else "not_found"

        gov = PLANET_ANATOMY_GOVERNANCE.get(csl, {})
        anat_en = gov.get("organs_en", "General Bodily Zone")
        anat_ta = gov.get("organs_ta", "பொது உடலமைப்பு")

        houses_str = ", ".join(str(h) for h in houses_sig)

        if h_num == 6:
            parts_en = [f"6th Cusp Sub-Lord {csl} (in star of {csl_star_l}) signifies houses {houses_str}."]
            parts_ta = [f"6-ம் பாவ உப அதிபதி (CSL) {csl} ({csl_star_l} நட்சத்திரத்தில்) பாவங்கள் {houses_str}-ஐக் குறிக்கிறது."]

            if rec:
                parts_en.append(f"Recovery / negation houses {rec_houses} are present in calculated significations, indicating recuperative resilience.")
                parts_ta.append(f"குணமடைதலைக் குறிக்கும் பாவங்கள் {rec_houses} காரகத்துவங்களில் உள்ளதால் விரைவான நலம் பெறும் ஆற்றல் அமைகிறது.")
            else:
                parts_en.append("Recovery houses (1, 5, 11) are not found in current significations.")
                parts_ta.append("குணமடைதல் பாவங்கள் (1, 5, 11) இந்த காரகத்துவங்களில் அமையவில்லை.")

            susc_tags = []
            susc_tags_ta = []
            if dis:
                susc_tags.append("House 6 (acute symptoms)")
                susc_tags_ta.append("6-ம் பாவம் (நோய் நிலை)")
            if chr_aff:
                susc_tags.append("House 8 (chronic vulnerability / surgical diagnostics)")
                susc_tags_ta.append("8-ம் பாவம் (நீண்டகால நிலை / அறுவை சிகிச்சை)")
            if hosp:
                susc_tags.append("House 12 (clinical care / hospitalization)")
                susc_tags_ta.append("12-ம் பாவம் (மருத்துவமனை அனுமதி / படுக்கை ஓய்வு)")

            if susc_tags:
                parts_en.append(f"Susceptibility indications: {', '.join(susc_tags)} are present; classical KP advises proactive care.")
                parts_ta.append(f"கவனிக்கப்பட வேண்டியவை: {', '.join(susc_tags_ta)} காரகத்துவத்தில் உள்ளதால் உரிய உடல்நலப் பராமரிப்பு அவசியம்.")
            else:
                parts_en.append("Susceptibility houses (6, 8, 12) are not found in the primary CSL significations.")
                parts_ta.append("பாதிப்பு பாவங்கள் (6, 8, 12) இந்த CSL காரகத்துவங்களில் அமையவில்லை.")

            prim_en = " ".join(parts_en).replace("{csl}", csl).replace("{csl_star_l}", csl_star_l).replace("{cslStarL}", csl_star_l)
            prim_ta = " ".join(parts_ta).replace("{csl}", csl).replace("{csl_star_l}", csl_star_l).replace("{cslStarL}", csl_star_l)
        else:
            prim_en = f"Cusp {h_num} Sub-Lord {csl} (star: {csl_star_l}) signifies houses {houses_str}.".replace("{csl}", csl).replace("{csl_star_l}", csl_star_l)
            prim_ta = f"{h_num}-ம் பாவ CSL {csl} ({csl_star_l} நட்சத்திரத்தில்) பாவங்கள் {houses_str}-ஐக் குறிக்கிறது.".replace("{csl}", csl).replace("{csl_star_l}", csl_star_l)

        return KpCslAnalysis(
            cusp_number=h_num,
            cusp_degree=cusp_deg,
            sign_name=sign_n,
            sign_lord=sign_l,
            cusp_star_lord=cusp_star_l,
            csl_planet=csl,
            csl_star_lord=csl_star_l,
            star_lord=csl_star_l,
            sub_lord=sub_sub_l,
            signified_houses=houses_sig,
            signification_details=details_sig,
            primary_signification_en=prim_en,
            primary_signification_ta=prim_ta,
            anatomical_rulership_en=anat_en,
            anatomical_rulership_ta=anat_ta,
            recovery_status=rec_status,
            disease_status=dis_status,
            chronic_status=chr_status,
            hospitalization_status=hosp_status,
            recovery_signified=rec,
            disease_signified=dis,
            chronic_signified=chr_aff,
            hospitalization_signified=hosp,
            recovery_houses=rec_houses,
            disease_houses=dis_houses,
            chronic_houses=chr_houses,
            hospitalization_houses=hosp_houses,
            is_data_available=True,
            missing_data_reason=None,
            calculation_provenance="KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)",
        )

    sixth_csl = analyze_cusp(6)
    lagna_csl = analyze_cusp(1) if 1 in cusp_map else None
    eighth_csl = analyze_cusp(8) if 8 in cusp_map else None
    twelfth_csl = analyze_cusp(12) if 12 in cusp_map else None

    # KP Rules Evaluation
    kp_rules: List[MedicalRule] = []
    recovery_indicators: List[str] = []
    susceptibility_indicators: List[str] = []

    # Rule 6csl -> 6
    if sixth_csl.disease_signified:
        r_def = MEDICAL_RULES_REGISTRY["kp_rule_6csl_signifies_6"]
        susceptibility_indicators.append(f"6th CSL {sixth_csl.csl_planet} signifies House 6 (acute roga)")
        kp_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=sixth_csl.anatomical_rulership_en,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th CSL {sixth_csl.csl_planet} signifies House 6"],
                planets_involved=[sixth_csl.csl_planet],
                relevant_houses=[6],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Cusp Sub-Lord signifies House 6",
                        passed=True,
                        detail=f"{sixth_csl.csl_planet} signifies houses {sixth_csl.signified_houses}."
                    )
                ],
            )
        )

    # Rule 6csl -> 8
    if sixth_csl.chronic_signified:
        r_def = MEDICAL_RULES_REGISTRY["kp_rule_6csl_signifies_8"]
        susceptibility_indicators.append(f"6th CSL {sixth_csl.csl_planet} signifies House 8 (chronic/surgical attention)")
        kp_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=sixth_csl.anatomical_rulership_en,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th CSL {sixth_csl.csl_planet} signifies House 8"],
                planets_involved=[sixth_csl.csl_planet],
                relevant_houses=[8],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Cusp Sub-Lord signifies House 8",
                        passed=True,
                        detail=f"{sixth_csl.csl_planet} signifies houses {sixth_csl.signified_houses}."
                    )
                ],
            )
        )

    # Rule 6csl -> 12
    if sixth_csl.hospitalization_signified:
        r_def = MEDICAL_RULES_REGISTRY["kp_rule_6csl_signifies_12"]
        susceptibility_indicators.append(f"6th CSL {sixth_csl.csl_planet} signifies House 12 (bed rest/hospitalization)")
        kp_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system=sixth_csl.anatomical_rulership_en,
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th CSL {sixth_csl.csl_planet} signifies House 12"],
                planets_involved=[sixth_csl.csl_planet],
                relevant_houses=[12],
                conditions=[
                    MedicalConditionItem(
                        condition="6th Cusp Sub-Lord signifies House 12",
                        passed=True,
                        detail=f"{sixth_csl.csl_planet} signifies houses {sixth_csl.signified_houses}."
                    )
                ],
            )
        )

    # Rule 6csl -> 1, 5, 11 (Recovery)
    if sixth_csl.recovery_signified:
        r_def = MEDICAL_RULES_REGISTRY["kp_rule_recovery_1_5_11"]
        rec_houses = [h for h in (1, 5, 11) if h in sixth_csl.signified_houses]
        recovery_indicators.append(f"6th CSL {sixth_csl.csl_planet} signifies recovery houses {rec_houses}")
        kp_rules.append(
            MedicalRule(
                id=r_def.id,
                name=r_def.name,
                name_tamil=r_def.name_tamil,
                source=r_def.source,
                chapter_verse=r_def.chapter_verse,
                category=r_def.category,
                system=r_def.system,
                required_placements=r_def.required_placements,
                mandatory_conditions=r_def.mandatory_conditions,
                traditional_interpretation=r_def.traditional_interpretation,
                interpretation_tamil=r_def.interpretation_tamil,
                anatomical_system="Cellular Restoration & Cure",
                modifiers=r_def.modifiers,
                conflicting_indications=r_def.conflicting_indications,
                is_active=True,
                status="Qualifying",
                triggered_positions=[f"6th CSL signifies houses {rec_houses}"],
                planets_involved=[sixth_csl.csl_planet],
                relevant_houses=rec_houses,
                conditions=[
                    MedicalConditionItem(
                        condition="6th Cusp Sub-Lord signifies houses 1, 5, or 11",
                        passed=True,
                        detail=f"{sixth_csl.csl_planet} signifies {rec_houses}."
                    )
                ],
            )
        )

    # Dasa Significations in KP
    dasa_sigs: List[KpDasaSignification] = []
    if dasa:
        active = getattr(dasa, "active_period", None)
        active_map: Dict[str, str] = {}
        if isinstance(active, dict):
            active_map = {"Mahadasha": active.get("mahadasha", ""), "Bhukti": active.get("antardasha", "")}
        elif hasattr(active, "mahadasha"):
            active_map = {"Mahadasha": active.mahadasha, "Bhukti": getattr(active, "antardasha", "")}

        for lvl, lord in active_map.items():
            if lord:
                h_sig = sorted(list(sig_map.get(lord, set())))
                ind_en = f"Period lord {lord} signifies houses {h_sig}."
                ind_ta = f"தசா நாதர் {lord} பாவங்கள் {h_sig}-ஐக் குறிக்கிறார்."
                dasa_sigs.append(
                    KpDasaSignification(
                        period_level=lvl,
                        lord=lord,
                        signified_houses=h_sig,
                        indication_en=ind_en,
                        indication_ta=ind_ta,
                    )
                )

                # Check susceptibility or recovery
                if any(x in h_sig for x in (6, 8, 12)):
                    susceptibility_indicators.append(f"Active {lvl} lord {lord} signifies houses {[x for x in (6, 8, 12) if x in h_sig]}")
                if any(x in h_sig for x in (1, 5, 11)):
                    recovery_indicators.append(f"Active {lvl} lord {lord} signifies recovery houses {[x for x in (1, 5, 11) if x in h_sig]}")

    return KpMedicalAnalysis(
        sixth_csl=sixth_csl,
        lagna_csl=lagna_csl,
        eighth_csl=eighth_csl,
        twelfth_csl=twelfth_csl,
        current_dasa_significations=dasa_sigs,
        kp_rules=kp_rules,
        recovery_indicators=recovery_indicators,
        susceptibility_indicators=susceptibility_indicators,
    )


def calculate_medical_astrology(
    horoscope: Any,
    dasa: Optional[Any] = None,
    kp: Optional[Any] = None,
    live_transits: Optional[Any] = None,
    gender: str = "male",
) -> MedicalAstrologyResponse:
    """Main orchestrator calculating complete Medical Astrology response."""
    planets = getattr(horoscope, "planets", [])
    ascendant = getattr(horoscope, "ascendant", None)
    houses = getattr(horoscope, "houses", None)
    metadata = getattr(horoscope, "metadata", None)

    asc_idx = getattr(ascendant, "sign_index", 1) if ascendant else 1

    ctx = YogaChartContext(
        planets=planets,
        ascendant_sign_idx=asc_idx,
        houses=houses,
        gender=gender,
    )

    # Perspective A: Birth Chart
    h1 = _build_house_analysis(1, ctx)
    h6 = _build_house_analysis(6, ctx)
    h8 = _build_house_analysis(8, ctx)
    h12 = _build_house_analysis(12, ctx)

    triggered_rules, conflicting_indications = _evaluate_vedic_rules(ctx)
    anatomical_mappings = _build_anatomical_mappings(ctx)

    birth_chart = BirthChartPerspective(
        lagna_analysis=h1,
        sixth_house_analysis=h6,
        eighth_house_analysis=h8,
        twelfth_house_analysis=h12,
        triggered_rules=triggered_rules,
        conflicting_indications=conflicting_indications,
        anatomical_mappings=anatomical_mappings,
    )

    # Perspective B: Current Period
    current_period = _build_current_period_perspective(
        dasa=dasa,
        live_transits=live_transits,
        lagna_sign_idx=asc_idx,
        ctx=ctx,
    )

    # Perspective C: Historical Periods
    historical_periods = _build_historical_period_perspective(dasa=dasa, ctx=ctx)

    vedic_analysis = VedicMedicalAnalysis(
        birth_chart=birth_chart,
        current_period=current_period,
        historical_periods=historical_periods,
    )

    # KP Analytical System (Strictly separate)
    kp_analysis = _evaluate_kp_medical(kp=kp, dasa=dasa)

    return MedicalAstrologyResponse(
        metadata=metadata,
        rule_set_version=RULE_SET_VERSION,
        disclaimer_en=SAFETY_DISCLAIMER_EN,
        disclaimer_ta=SAFETY_DISCLAIMER_TA,
        vedic_analysis=vedic_analysis,
        kp_analysis=kp_analysis,
    )
