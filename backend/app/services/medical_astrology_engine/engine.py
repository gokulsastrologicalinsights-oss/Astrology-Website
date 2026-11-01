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
    NakshatraMedicalDetail,
    GestationalMonthDetail,
    ProgenyShapaDetail,
    ClinicalCaseStudy,
    TatwaNavadwaraDetail,
    DrKrishnaKumarCompendium,
    SaptaDhatuDetail,
    EndocrineGlandDetail,
    TridoshaSiteDetail,
    DeathPointCalculation,
    DiabetesMellitusAssessment,
    ModernComplexDiseaseDetail,
    NaturalRemediesGuide,
    DrChatterjeeCompendium,
    HeindelSignAnatomy,
    HeindelPlanetPhysiology,
    HeindelViciousCircle,
    HeindelNailDiagnosis,
    HeindelPlanetaryAntidote,
    HeindelAphorism,
    HeindelNebularSpot,
    MaxHeindelCompendium,
    JaneDecumbitureEvaluation,
    JaneArabianParts,
    JaneElementalAnalysis,
    JaneCellSaltCorrespondence,
    JaneBachFlowerCorrespondence,
    JaneAcupunctureMeridian,
    JaneRidderPatrickCompendium,
    DaathSignAnatomy,
    DaathPlanetAction,
    DaathAntipathicTherapy,
    DaathPlanetaryPeriod,
    DaathDecumbitureCriticalDays,
    DaathStrengthEvaluation,
    HeinrichDaathCompendium,
)
from app.services.medical_astrology_engine.daath_registry import (
    DAATH_METADATA,
    DAATH_SIGNS_ANATOMY,
    DAATH_PLANETS_BIODYNAMICS,
    DAATH_TEMPERAMENTS_AND_CROSSES,
    DAATH_ANTIPATHIC_THERAPEUTICS,
    DAATH_PLANETARY_PERIODS,
    DAATH_DECUMBITURE_DATA,
    DAATH_RULES_REGISTRY,
)
from app.services.medical_astrology_engine.heindel_registry import (
    MAX_HEINDEL_METADATA,
    HEINDEL_SIGNS_ANATOMY,
    HEINDEL_PLANETS_PHYSIOLOGY,
    HEINDEL_SENSE_ORGANS,
    HEINDEL_VICIOUS_CIRCLES,
    HEINDEL_NAIL_DIAGNOSIS_DATA,
    HEINDEL_PLANETARY_ANTIDOTES,
    HEINDEL_NEBULAR_SPOTS,
    HEINDEL_APHORISMS_LIST,
    HEINDEL_RULES_REGISTRY,
)
from app.services.medical_astrology_engine.registry import (
    RULE_SET_VERSION,
    MEDICAL_RULES_REGISTRY,
    KALAPURUSHA_ANATOMY,
    PLANET_ANATOMY_GOVERNANCE,
    ClassicalMedicalRuleDefinition,
    DR_KRISHNA_KUMAR_METADATA,
    NAKSHATRA_27_MEDICAL_MATRIX,
    PREGNANCY_GESTATIONAL_MONTHS,
    PROGENY_CURSES_AND_REMEDIES,
    TATWAS_AND_NAVADWARAS,
    CLASSICAL_CASE_STUDIES,
    DR_KRISHNA_KUMAR_RULES_REGISTRY,
    DR_CHATTERJEE_GOLDEN_RULES_REGISTRY,
    CHATTERJEE_CASE_STUDIES,
    JANE_RIDDER_PATRICK_METADATA,
    CULPEPER_7_RULES,
    JANE_THREE_CROSSES,
    JANE_CELL_SALTS,
    JANE_BACH_FLOWERS,
    JANE_ACUPUNCTURE_MERIDIANS,
    JANE_ELEMENTAL_BALANCING,
    JANE_CASE_STUDIES,
    JANE_RIDDER_PATRICK_RULES_REGISTRY,
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

        # Robust Fallback: Search dasa_tree dynamically with current Julian Day
        d_tree = getattr(dasa, "dasa_tree", None) or []
        if (maha_lord == "Unknown" or not bhukti_lord) and d_tree:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            now_jd = xalen.julian_day(now.year, now.month, now.day, now.hour + now.minute / 60.0)
            for m in d_tree:
                m_start = getattr(m, "start_jd", 0.0) if hasattr(m, "start_jd") else m.get("start_jd", 0.0)
                m_end = getattr(m, "end_jd", 0.0) if hasattr(m, "end_jd") else m.get("end_jd", 0.0)
                if m_start <= now_jd < m_end:
                    maha_lord = getattr(m, "lord", None) or m.get("lord", "Unknown")
                    sub = getattr(m, "sub_periods", []) or (m.get("sub_periods", []) if isinstance(m, dict) else [])
                    for b in (sub or []):
                        b_start = getattr(b, "start_jd", 0.0) if hasattr(b, "start_jd") else b.get("start_jd", 0.0)
                        b_end = getattr(b, "end_jd", 0.0) if hasattr(b, "end_jd") else b.get("end_jd", 0.0)
                        if b_start <= now_jd < b_end:
                            bhukti_lord = getattr(b, "lord", None) or b.get("lord", None)
                            andhar = getattr(b, "sub_periods", []) or (b.get("sub_periods", []) if isinstance(b, dict) else [])
                            for a in (andhar or []):
                                a_start = getattr(a, "start_jd", 0.0) if hasattr(a, "start_jd") else a.get("start_jd", 0.0)
                                a_end = getattr(a, "end_jd", 0.0) if hasattr(a, "end_jd") else a.get("end_jd", 0.0)
                                if a_start <= now_jd < a_end:
                                    antara_lord = getattr(a, "lord", None) or a.get("lord", None)
                                    break
                            break
                    break

        if maha_lord == "Unknown" and hasattr(dasa, "birth_dasa_lord"):
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


def _resolve_nakshatra_info(nak_obj: Any) -> Optional[NakshatraMedicalDetail]:
    """Helper to resolve NakshatraMedicalDetail from nakshatra object or string."""
    if not nak_obj:
        return None
    star_num: Optional[int] = None
    if hasattr(nak_obj, "index"):
        star_num = getattr(nak_obj, "index") + 1
    elif hasattr(nak_obj, "number"):
        star_num = getattr(nak_obj, "number")
    elif isinstance(nak_obj, dict):
        if "index" in nak_obj:
            star_num = nak_obj["index"] + 1
        elif "number" in nak_obj:
            star_num = nak_obj["number"]
    elif isinstance(nak_obj, str):
        for num, n_data in NAKSHATRA_27_MEDICAL_MATRIX.items():
            if n_data["name"].lower() in nak_obj.lower():
                star_num = num
                break

    if star_num and star_num in NAKSHATRA_27_MEDICAL_MATRIX:
        d = NAKSHATRA_27_MEDICAL_MATRIX[star_num]
        return NakshatraMedicalDetail(
            number=d["number"],
            name=d["name"],
            name_ta=d["name_ta"],
            body_part_en=d["body_part_en"],
            body_part_ta=d["body_part_ta"],
            devata=d["devata"],
            disease_tendency_en=d["disease_tendency_en"],
            disease_tendency_ta=d["disease_tendency_ta"],
            propitiation_en=d["propitiation_en"],
            propitiation_ta=d["propitiation_ta"],
        )
    return None


def _evaluate_dr_krishna_kumar_compendium(
    ctx: YogaChartContext,
    horoscope: Any,
) -> DrKrishnaKumarCompendium:
    """Evaluates Dr. S. Krishna Kumar's Medical Astrology and Progeny Compendium."""
    # 1. Native Stars
    moon_star: Optional[NakshatraMedicalDetail] = None
    planets = getattr(horoscope, "planets", [])
    for p in planets:
        p_name = getattr(p, "name", "")
        if p_name == "Moon":
            moon_star = _resolve_nakshatra_info(getattr(p, "nakshatra", None))
            break

    asc_obj = getattr(horoscope, "ascendant", None)
    lagna_star = _resolve_nakshatra_info(getattr(asc_obj, "nakshatra", None)) if asc_obj else None

    # 2. All 27 Nakshatras
    all_27 = [
        NakshatraMedicalDetail(
            number=d["number"],
            name=d["name"],
            name_ta=d["name_ta"],
            body_part_en=d["body_part_en"],
            body_part_ta=d["body_part_ta"],
            devata=d["devata"],
            disease_tendency_en=d["disease_tendency_en"],
            disease_tendency_ta=d["disease_tendency_ta"],
            propitiation_en=d["propitiation_en"],
            propitiation_ta=d["propitiation_ta"],
        )
        for d in NAKSHATRA_27_MEDICAL_MATRIX.values()
    ]

    # 3. Gestational Months
    gest_months = [
        GestationalMonthDetail(
            month=gm["month"],
            ruling_planet=gm["ruling_planet"],
            sanskrit_term=gm["sanskrit_term"],
            stage_en=gm["stage_en"],
            stage_ta=gm["stage_ta"],
            description_en=gm["description_en"],
            description_ta=gm["description_ta"],
        )
        for gm in PREGNANCY_GESTATIONAL_MONTHS
    ]

    # 4. Progeny Curses & Remedies
    h5_occ = ctx.house_occupants.get(5, [])
    l5 = ctx.house_lords[5]
    h_l5 = ctx.planet_house.get(l5)
    l9 = ctx.house_lords[9]
    h_l9 = ctx.planet_house.get(l9)
    l3 = ctx.house_lords[3]
    h_l3 = ctx.planet_house.get(l3)
    l7 = ctx.house_lords[7]
    h_l7 = ctx.planet_house.get(l7)
    l4 = ctx.house_lords[4]
    h_l4 = ctx.planet_house.get(l4)

    jup_h = ctx.planet_house.get("Jupiter")
    rahu_h = ctx.planet_house.get("Rahu")
    sat_h = ctx.planet_house.get("Saturn")
    mars_h = ctx.planet_house.get("Mars")
    moon_h = ctx.planet_house.get("Moon")
    sun_h = ctx.planet_house.get("Sun")
    merc_h = ctx.planet_house.get("Mercury")
    ven_h = ctx.planet_house.get("Venus")

    progeny_shapas: List[ProgenyShapaDetail] = []
    for sh in PROGENY_CURSES_AND_REMEDIES:
        sh_id = sh["id"]
        is_ind = False
        obs = None

        if sh_id == "sarpa_shapa":
            if "Rahu" in h5_occ or ctx.planet_sign.get("Rahu") in (1, 8):
                is_ind = True
                obs = "Rahu placed in 5th house or Mars sign (Aries/Scorpio) aligns with Sarpa Shapa indications."
            elif sat_h == 5 and h_l5 == 5:
                is_ind = True
                obs = "Saturn conjoins 5th lord in the 5th house."
        elif sh_id == "pitru_shapa":
            if sun_h == 5 and ctx.planet_sign.get("Sun") == 7:
                is_ind = True
                obs = "Sun is debilitated in the 5th house."
            elif sun_h in (5, 9) and any(m in (ctx.house_occupants.get(sun_h, [])) for m in NATURAL_MALEFICS if m != "Sun"):
                is_ind = True
                obs = f"Sun posited in house {sun_h} with natural malefics."
            elif h_l9 in (6, 8, 12):
                is_ind = True
                obs = f"9th lord {l9} placed in Dusthana (House {h_l9})."
        elif sh_id == "bhratru_shapa":
            if h_l3 == 5 and ("Mars" in h5_occ or "Rahu" in h5_occ):
                is_ind = True
                obs = f"3rd lord {l3} occupies 5th house alongside Mars/Rahu."
            elif mars_h == 1 and sat_h == 5:
                is_ind = True
                obs = "Mars occupies Lagna while Saturn is placed in 5th house."
        elif sh_id == "matru_shapa":
            if l5 == "Moon" and (moon_h in (6, 8, 12) or ctx.planet_sign.get("Moon") == 8):
                is_ind = True
                obs = "Moon is 5th lord in debilitation or placed in a Dusthana."
            elif sat_h == 11 and moon_h == 5 and ctx.planet_sign.get("Moon") == 8:
                is_ind = True
                obs = "Saturn in 11th with debilitated Moon in 5th house."
        elif sh_id == "matula_shapa":
            if "Mercury" in h5_occ and any(m in h5_occ for m in ("Mars", "Rahu", "Saturn")):
                is_ind = True
                obs = "Mercury occupies 5th house with natural malefics (Mars/Rahu/Saturn)."
        elif sh_id == "brahma_shapa":
            if ctx.planet_sign.get("Rahu") in (9, 12) and jup_h in (5, 8):
                is_ind = True
                obs = "Rahu in Jupiter's signs (Sagittarius/Pisces) while Jupiter is in 5th/8th."
            elif jup_h in (1, 5) and ctx.planet_sign.get("Jupiter") == 10 and h_l5 in (6, 8, 12):
                is_ind = True
                obs = "Jupiter debilitated in 1st/5th while 5th lord occupies Dusthana."
        elif sh_id == "patni_shapa":
            if h_l7 == 5 and h_l5 == 8:
                is_ind = True
                obs = f"7th lord {l7} in 5th house while 5th lord {l5} occupies 8th house."
            elif ven_h in (6, 8, 12) and any(m in (ctx.house_occupants.get(ven_h, [])) for m in NATURAL_MALEFICS):
                is_ind = True
                obs = f"Venus in Dusthana house {ven_h} afflicted by malefics."
        elif sh_id == "preta_shapa":
            if "Saturn" in h5_occ and "Sun" in h5_occ:
                is_ind = True
                obs = "Saturn and Sun conjoined in 5th house."
            elif rahu_h == 1 and sat_h == 5:
                is_ind = True
                obs = "Rahu in Lagna while Saturn occupies 5th house."
        elif sh_id == "parashara_planetary_progeny_remedies":
            is_ind = bool(any(p in h5_occ for p in NATURAL_MALEFICS) or h_l5 in (6, 8, 12))
            obs = "Evaluated against 5th house occupants and 5th lord status."

        progeny_shapas.append(
            ProgenyShapaDetail(
                id=sh["id"],
                shapa_name=sh["shapa_name"],
                shapa_name_ta=sh["shapa_name_ta"],
                afflicted_karaka=sh["afflicted_karaka"],
                cause_en=sh["cause_en"],
                cause_ta=sh["cause_ta"],
                combinations=sh["combinations"],
                remedy_en=sh["remedy_en"],
                remedy_ta=sh["remedy_ta"],
                is_indicated=is_ind,
                chart_observation=obs,
            )
        )

    # 5. Case studies & Tatwas
    case_studies = [
        ClinicalCaseStudy(
            id=cs["id"],
            title_en=cs["title_en"],
            title_ta=cs["title_ta"],
            patient_profile=cs["patient_profile"],
            disease_diagnosed=cs["disease_diagnosed"],
            astrological_indicators=cs["astrological_indicators"],
            dasha_timing=cs["dasha_timing"],
            key_takeaway=cs["key_takeaway"],
        )
        for cs in CLASSICAL_CASE_STUDIES
    ]

    tatwas_senses = [
        TatwaNavadwaraDetail(
            tatwa_en=t["tatwa_en"],
            tatwa_ta=t["tatwa_ta"],
            planet=t["planet"],
            sense_en=t["sense_en"],
            sense_ta=t["sense_ta"],
            body_parts_en=t["body_parts_en"],
            body_parts_ta=t["body_parts_ta"],
            abhimani_devata=t["abhimani_devata"],
        )
        for t in TATWAS_AND_NAVADWARAS
    ]

    # 6. Evaluate Manasika & Buddhi Yogas and Organ Yogas from DR_KRISHNA_KUMAR_RULES_REGISTRY
    manasika_rules: List[MedicalRule] = []
    organ_rules: List[MedicalRule] = []

    for r_id, r_def in DR_KRISHNA_KUMAR_RULES_REGISTRY.items():
        is_active = False
        trig_pos: List[str] = []
        planets_inv: List[str] = []
        rel_houses: List[int] = []

        if r_id == "kk_theevra_buddhi":
            if h_l5 in (1, 4, 5, 7, 9, 10):
                is_active = True
                trig_pos = [f"5th Lord {l5} well-placed in House {h_l5}"]
                planets_inv = [l5]
                rel_houses = [5, h_l5]
        elif r_id == "kk_parengita_gnana":
            if jup_h in (1, 4, 5, 7, 9, 10):
                is_active = True
                trig_pos = [f"Jupiter in auspicious Kendra/Trikona (House {jup_h})"]
                planets_inv = ["Jupiter"]
                rel_houses = [jup_h]
        elif r_id == "kk_buddhida_yoga":
            ben_in_5 = [p for p in h5_occ if p in NATURAL_BENEFICS]
            if ben_in_5:
                is_active = True
                trig_pos = [f"Benefic(s) {', '.join(ben_in_5)} occupy House 5"]
                planets_inv = ben_in_5
                rel_houses = [5]
        elif r_id == "kk_dharanadhi_samartha":
            if h_l5 in (1, 4, 5, 7, 9, 10) and jup_h in (1, 4, 5, 7, 9, 10):
                is_active = True
                trig_pos = [f"5th Lord {l5} (House {h_l5}) and Jupiter (House {jup_h}) both in Kendras/Trikonas"]
                planets_inv = [l5, "Jupiter"]
                rel_houses = [h_l5, jup_h]
        elif r_id == "kk_buddhi_nasha":
            mal_in_5 = [p for p in h5_occ if p in NATURAL_MALEFICS]
            if mal_in_5 and h_l5 in (6, 8, 12):
                is_active = True
                trig_pos = [f"Malefic(s) {', '.join(mal_in_5)} in 5th and 5th Lord {l5} in Dusthana {h_l5}"]
                planets_inv = mal_in_5 + [l5]
                rel_houses = [5, h_l5]
        elif r_id == "kk_unmada_yoga":
            if jup_h == 1 and mars_h == 7:
                is_active = True
                trig_pos = ["Jupiter in Lagna and Mars in 7th House"]
                planets_inv = ["Jupiter", "Mars"]
                rel_houses = [1, 7]
            elif sat_h == 1 and mars_h in (5, 9, 7):
                is_active = True
                trig_pos = [f"Saturn in Lagna with Mars in House {mars_h}"]
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [1, mars_h]
        elif r_id == "kk_mati_bhramana":
            if moon_h == 12 and sat_h == 12:
                is_active = True
                trig_pos = ["Moon conjoined Saturn in House 12"]
                planets_inv = ["Moon", "Saturn"]
                rel_houses = [12]
        elif r_id == "kk_krodha_yoga":
            l2 = ctx.house_lords[2]
            if l2 in ("Mars", "Sun", "Saturn") and (ctx.planet_house.get(l2) in (6, 8, 12) or ctx.planet_sign.get(l2) in (ctx.planet_sign.get("Rahu"), ctx.planet_sign.get("Ketu"))):
                is_active = True
                trig_pos = [f"2nd Lord {l2} is a natural malefic afflicted in chart"]
                planets_inv = [l2]
                rel_houses = [2]
        elif r_id == "kk_shiro_vyadhi":
            l1 = ctx.house_lords[1]
            l6 = ctx.house_lords[6]
            if ctx.planet_sign.get(l1) in (ctx.planet_sign.get("Rahu"), ctx.planet_sign.get("Ketu")) or ctx.planet_sign.get(l6) in (ctx.planet_sign.get("Rahu"), ctx.planet_sign.get("Ketu")):
                is_active = True
                trig_pos = [f"Lagna lord {l1} or 6th lord {l6} conjoined Rahu/Ketu"]
                planets_inv = [l1, l6, "Rahu"]
                rel_houses = [1, 6]
        elif r_id == "kk_nethra_roga":
            l2 = ctx.house_lords[2]
            h_l2 = ctx.planet_house.get(l2)
            if h_l2 in (6, 8, 12) or sun_h in (6, 8, 12) or moon_h in (6, 8, 12):
                is_active = True
                trig_pos = [f"Eye indicator in Dusthana: 2nd Lord in {h_l2}, Sun in {sun_h}, Moon in {moon_h}"]
                planets_inv = [l2, "Sun", "Moon"]
                rel_houses = [2, 12]
        elif r_id == "kk_badhira_yoga":
            l3_h = ctx.planet_house.get(ctx.house_lords[3])
            if l3_h in (6, 8, 12) or any(m in (ctx.house_occupants.get(3, [])) for m in NATURAL_MALEFICS):
                is_active = True
                trig_pos = ["3rd house or 3rd lord configured with malefic/Dusthana influences"]
                planets_inv = [ctx.house_lords[3]]
                rel_houses = [3]
        elif r_id == "kk_dantha_roga":
            if "Rahu" in (ctx.house_occupants.get(6, [])) or "Ketu" in (ctx.house_occupants.get(6, [])) or "Rahu" in (ctx.house_occupants.get(2, [])):
                is_active = True
                trig_pos = ["Rahu/Ketu occupying House 6 or House 2"]
                planets_inv = ["Rahu"]
                rel_houses = [2, 6]
        elif r_id == "kk_gala_roga":
            l3_planet = ctx.house_lords[3]
            if merc_h == ctx.planet_house.get(l3_planet) or rahu_h == ctx.planet_house.get(l3_planet):
                is_active = True
                trig_pos = [f"3rd Lord {l3_planet} associated with Mercury/Rahu"]
                planets_inv = [l3_planet, "Mercury"]
                rel_houses = [3]
        elif r_id == "kk_hridaya_roga":
            if h_l4 in (6, 8, 12) or (sun_h in (6, 8, 12) and (ctx.planet_aspects_planet("Saturn", "Sun") or ctx.planet_aspects_planet("Mars", "Sun"))):
                is_active = True
                trig_pos = [f"4th Lord in House {h_l4} or Sun in Dusthana with malefic aspect"]
                planets_inv = [l4, "Sun"]
                rel_houses = [4]
        elif r_id == "kk_mutra_krichra":
            if ctx.planet_sign.get("Moon") in (4, 8, 12) and ctx.planet_sign.get(ctx.house_lords[6]) in (4, 8, 12):
                is_active = True
                trig_pos = ["Moon and 6th lord both occupy watery signs (Cancer/Scorpio/Pisces)"]
                planets_inv = ["Moon", ctx.house_lords[6]]
                rel_houses = [6, 7]
        elif r_id == "kk_arsha_roga":
            if sat_h == 1 and mars_h == 7:
                is_active = True
                trig_pos = ["Saturn in Lagna and Mars in 7th House"]
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [1, 7, 8]
            elif ctx.planet_house.get(ctx.house_lords[8]) == 7 and ctx.house_lords[8] in NATURAL_MALEFICS:
                is_active = True
                trig_pos = [f"8th Lord {ctx.house_lords[8]} (malefic) placed in 7th House"]
                planets_inv = [ctx.house_lords[8]]
                rel_houses = [7, 8]
        elif r_id == "kk_deha_sthoulya":
            if ctx.lagna_sign_idx in (4, 8, 12) and (jup_h == 1 or ctx.planet_aspects_house("Jupiter", 1)):
                is_active = True
                trig_pos = ["Watery Lagna with Jupiter occupying or aspecting the Ascendant"]
                planets_inv = ["Jupiter"]
                rel_houses = [1]
        elif r_id == "kk_mrityunjaya_resuscitation":
            l8 = ctx.house_lords[8]
            if ctx.planet_house.get(l8) in (1, 4, 7, 10) and ctx.planet_house.get(l8) == sat_h:
                is_active = True
                trig_pos = [f"8th Lord {l8} conjoined Saturn in Kendra (House {sat_h})"]
                planets_inv = [l8, "Saturn"]
                rel_houses = [8, sat_h]

        rule_obj = MedicalRule(
            id=r_def.id,
            name=r_def.name,
            name_tamil=r_def.name_tamil,
            source=r_def.source,
            chapter_verse=r_def.chapter_verse,
            category=r_def.category,
            system=r_def.system,
            required_placements=", ".join(r_def.required_placements) if isinstance(r_def.required_placements, list) else str(r_def.required_placements),
            mandatory_conditions=r_def.mandatory_conditions,
            traditional_interpretation=r_def.traditional_interpretation,
            interpretation_tamil=r_def.interpretation_tamil,
            anatomical_system=r_def.anatomical_system,
            modifiers=", ".join(r_def.modifiers) if isinstance(r_def.modifiers, list) else (str(r_def.modifiers) if r_def.modifiers else None),
            conflicting_indications=", ".join(r_def.conflicting_indications) if isinstance(r_def.conflicting_indications, list) else (str(r_def.conflicting_indications) if r_def.conflicting_indications else None),
            is_active=is_active,
            status="Qualifying" if is_active else "Not Qualifying",
            triggered_positions=trig_pos,
            planets_involved=planets_inv,
            relevant_houses=rel_houses,
            conditions=[
                MedicalConditionItem(
                    condition=r_def.required_placements,
                    passed=is_active,
                    detail=trig_pos[0] if trig_pos else "Conditions not fulfilled in natal positions.",
                )
            ],
        )

        if r_def.category == "Manasika & Buddhi Yogas":
            manasika_rules.append(rule_obj)
        else:
            organ_rules.append(rule_obj)

    # 7. Caesarean vs Normal Delivery
    mars_aspects_7 = ctx.planet_aspects_house("Mars", 7)
    mars_aspects_moon = ctx.planet_aspects_planet("Mars", "Moon")
    jup_aspects_7 = ctx.planet_aspects_house("Jupiter", 7)
    jup_aspects_moon = ctx.planet_aspects_planet("Jupiter", "Moon")
    jup_aspects_5 = ctx.planet_aspects_house("Jupiter", 5)

    if (mars_aspects_7 or mars_aspects_moon) and not (jup_aspects_7 or jup_aspects_moon or jup_aspects_5):
        deliv_obs = (
            "Classical criteria from Chapter 4 of Dr. S. Krishna Kumar's book indicate that Mars casting aspect on "
            "the 7th house (abdominal zone) or Moon (governor of natural labour pains) without mitigating aspects "
            "from Jupiter classically indicates Caesarean surgical intervention."
        )
    else:
        deliv_obs = (
            "Classical criteria from Chapter 4 of Dr. S. Krishna Kumar's book indicate that the absence of Mars's "
            "surgical aspect on the Moon and 7th house, along with Jupiter's protective benefic influence, strongly "
            "favors an uncomplicated natural delivery."
        )

    # 8. Sperm / Beeja Potency
    moon_sat = ctx.planet_aspects_planet("Saturn", "Moon") or moon_h == sat_h
    moon_merc = ctx.planet_aspects_planet("Mercury", "Moon") or moon_h == merc_h
    moon_ketu = moon_h == ctx.planet_house.get("Ketu")
    ven_sat = ctx.planet_aspects_planet("Saturn", "Venus") or ven_h == sat_h
    ven_merc = ctx.planet_aspects_planet("Mercury", "Venus") or ven_h == merc_h
    ven_ketu = ven_h == ctx.planet_house.get("Ketu")

    if (moon_sat or moon_merc or moon_ketu) and (ven_sat or ven_merc or ven_ketu):
        sperm_obs = (
            "Classical Beeja Dosha notice (Chapter 3): Both Moon (producer of semen) and Venus (potency / Veeryanu) "
            "interact with neutral/eunuch planets (Saturn/Mercury) or Ketu. Ancient texts advocate reciting "
            "the Payasa Paravrithi sarga of Valmiki Ramayana and performing Santana Gopala Krishna Homa on Shravana "
            "star falling on Dwadashi tithi."
        )
    else:
        sperm_obs = (
            "Balanced Beeja / Veeryanu indicators: Vital reproductive significators (Moon and Venus) maintain favorable "
            "constitutional strength without severe dual affliction from eunuch planets."
        )

    return DrKrishnaKumarCompendium(
        book_title=DR_KRISHNA_KUMAR_METADATA["book_title"],
        book_title_ta=DR_KRISHNA_KUMAR_METADATA["book_title_ta"],
        author=DR_KRISHNA_KUMAR_METADATA["author"],
        publisher=DR_KRISHNA_KUMAR_METADATA["publisher"],
        salient_features=DR_KRISHNA_KUMAR_METADATA["salient_features"],
        native_moon_star=moon_star,
        native_lagna_star=lagna_star,
        all_27_nakshatras=all_27,
        gestational_months=gest_months,
        progeny_shapas=progeny_shapas,
        case_studies=case_studies,
        tatwas_and_senses=tatwas_senses,
        manasika_buddhi_yogas=manasika_rules,
        organ_specific_yogas=organ_rules,
        caesarean_vs_normal_delivery_observation=deliv_obs,
        sperm_potency_observation=sperm_obs,
    )



def _evaluate_dr_chatterjee_compendium(
    ctx: YogaChartContext,
    horoscope: Any,
    live_transits: Optional[Any] = None,
) -> DrChatterjeeCompendium:
    """Evaluates Dr. S. S. Chatterjee's Advance Medical Astrology compendium.
    
    Includes:
    1. Mathematical Death Point and Saturn's transit aspect trigger
    2. Parijata Yoga and Kendra-Benefic longevity shield
    3. 7 Sapta Dhatus mapped to 7 physical planets
    4. Endocrine glands planetary governance
    5. Tridosha anatomical site matrix
    6. Special Diabetes Mellitus (Madhumeha) diagnostic module
    7. 10 modern 21st-century complex diseases
    8. Natural therapies: Colour therapy, metal-charged waters, and 13 urges
    9. 28 evaluated Golden Rules of Health Hazards
    10. Documented clinical case histories from Dr. Chatterjee's research diary
    """
    planets = getattr(horoscope, "planets", [])
    ascendant = getattr(horoscope, "ascendant", None)

    asc_long = float(getattr(ascendant, "longitude", 0.0)) if ascendant else 0.0
    sun_long = 0.0
    moon_long = 0.0
    jup_long = 0.0
    sat_natal_sign = ctx.planet_sign.get("Saturn", 10)

    for p in planets:
        p_name = getattr(p, "name", "")
        p_long = float(getattr(p, "longitude", 0.0))
        if p_name == "Sun":
            sun_long = p_long
        elif p_name == "Moon":
            moon_long = p_long
        elif p_name == "Jupiter":
            jup_long = p_long

    # 1. Death Point Calculation: (Ascendant + Sun + Moon + Jupiter) % 360
    dp_long = (asc_long + sun_long + moon_long + jup_long) % 360.0
    dp_sign_idx = int(dp_long // 30) + 1
    deg_in_sign = round(dp_long % 30.0, 2)
    dp_sign_en = SIGN_NAMES_EN.get(dp_sign_idx, "Unknown")
    dp_sign_ta = SIGN_NAMES_TA.get(dp_sign_idx, "தெரியவில்லை")

    nakshatra_names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    nak_span = 360.0 / 27.0
    dp_nak_idx = int(dp_long / nak_span)
    dp_nak_name = nakshatra_names[dp_nak_idx % 27]
    deg_in_nak = dp_long % nak_span
    dp_nak_pada = int(deg_in_nak / (nak_span / 4.0)) + 1

    # Check Transit Saturn aspect on Death Point
    sat_curr_sign = sat_natal_sign
    if live_transits and hasattr(live_transits, "planets"):
        trans_planets = getattr(live_transits, "planets", {})
        if isinstance(trans_planets, dict) and "Saturn" in trans_planets:
            sat_curr_sign = getattr(trans_planets["Saturn"], "sign_index", sat_natal_sign)

    # Saturn aspects: Conjunction (1st), 3rd Drishti, 7th Drishti, 10th Drishti
    sat_aspect_signs = {
        sat_curr_sign,  # Conjunction
        ((sat_curr_sign + 2 - 1) % 12) + 1,  # 3rd aspect
        ((sat_curr_sign + 6 - 1) % 12) + 1,  # 7th aspect
        ((sat_curr_sign + 9 - 1) % 12) + 1,  # 10th aspect
    }
    sat_aspect_active = dp_sign_idx in sat_aspect_signs

    aspect_desc_en = (
        f"Death Point at {deg_in_sign:.2f}° {dp_sign_en} ({dp_nak_name} Pada {dp_nak_pada}). "
        f"Transit Saturn currently occupying Sign {sat_curr_sign} ({SIGN_NAMES_EN.get(sat_curr_sign, '')}) "
        + ("casts direct drishti/conjunction upon this sensitive point, indicating heightened constitutional vigilance."
           if sat_aspect_active else
           "does not aspect this sensitive point, signifying general vital stability.")
    )
    aspect_desc_ta = (
        f"மிருத்யு புள்ளி {dp_sign_ta} ராசியில் {deg_in_sign:.2f}° ({dp_nak_name} பாதம் {dp_nak_pada})-ல் அமைந்துள்ளது. "
        f"கோச்சார சனி {SIGN_NAMES_TA.get(sat_curr_sign, '')}-ல் நின்று "
        + ("இப்புள்ளியைப் பார்ப்பதால் உடல் ஆரோக்கியத்தில் கூடுதல் விழிப்புணர்வு தேவைப்படுகிறது."
           if sat_aspect_active else
           "இப்புள்ளியைப் பார்க்கவில்லை; எனவே ஆயுள் பலம் சீராக உள்ளது.")
    )

    death_point_calc = DeathPointCalculation(
        formula="Ascendant Longitude + Sun Longitude + Moon Longitude + Jupiter Longitude (mod 360°)",
        longitude_deg=round(dp_long, 4),
        sign_index=dp_sign_idx,
        sign_name_en=dp_sign_en,
        sign_name_ta=dp_sign_ta,
        degree_in_sign=deg_in_sign,
        nakshatra_name=dp_nak_name,
        nakshatra_pada=dp_nak_pada,
        transit_saturn_aspect_active=sat_aspect_active,
        aspect_details_en=aspect_desc_en,
        aspect_details_ta=aspect_desc_ta,
    )

    # 2. Parijata Yoga & Longevity Evaluation
    l1 = ctx.house_lords.get(1, "Mars")
    l1_sign = ctx.planet_sign.get(l1, 1)
    disp1 = SIGN_LORDS.get(l1_sign, "Mars")
    disp1_sign = ctx.planet_sign.get(disp1, 1)
    disp2 = SIGN_LORDS.get(disp1_sign, "Mars")
    disp2_h = ctx.planet_house.get(disp2, 1)

    has_parijata = disp2_h in (1, 4, 7, 10, 5, 9)
    ben_in_kendras = [p for p in ("Jupiter", "Venus", "Mercury") if ctx.planet_house.get(p) in (1, 4, 7, 10, 5, 9)]
    mal_in_upachaya = [p for p in ("Rahu", "Ketu", "Mars", "Saturn", "Sun") if ctx.planet_house.get(p) in (3, 11)]

    parijata_eval = {
        "has_parijata_yoga": has_parijata,
        "benefics_in_kendras_trines": ben_in_kendras,
        "malefics_in_3_or_11": mal_in_upachaya,
        "longevity_shield_status": "Vigorous / High Immunity" if (len(ben_in_kendras) >= 2 or has_parijata) else "Moderate",
        "description_en": (
            f"Lagna lord {l1}'s dispositor chain reaches {disp2} in House {disp2_h}. "
            f"Benefics in Kendras/Trines: {', '.join(ben_in_kendras) or 'None'}. "
            f"Malefics in Upachaya (3/11): {', '.join(mal_in_upachaya) or 'None'}."
        ),
        "description_ta": (
            f"லக்னாதிபதி {l1}-ன் பரிவார கிரகங்கள் கேந்திர/திரிகோணங்களில் உள்ளன. "
            f"கேந்திர சுபர்கள்: {', '.join(ben_in_kendras) or 'இல்லை'}. "
            f"3/11 அசுபர்கள்: {', '.join(mal_in_upachaya) or 'இல்லை'}."
        ),
    }

    # 3. Seven Sapta Dhatus Matrix (Seven Planets)
    dhatu_configs = [
        (1, "Asthi (Bone System)", "அஸ்தி (எலும்பு மண்டலம்)", "Asthi", "Sun",
         "Forms skeletal framework, structural integrity, and cranial/calcium matrix",
         "உடலின் எலும்புக்கூடு, கட்டமைப்பு மற்றும் மண்டை ஓட்டு உறுதி"),
        (2, "Rasa (Bodily Fluids & Plasma)", "ரஸம் (உடல் திரவங்கள் & பிளாஸ்மா)", "Rasa", "Moon",
         "Circulates lymph, nutrients, cellular hydration, and emotional homeostasis",
         "நிணநீர், ஊட்டச்சத்து ரத்த ஓட்டம், நீர்ச்சத்து சமநிலை"),
        (3, "Rakta & Majja (Blood & Bone Marrow)", "ரக்தம் & மஜ்ஜை (ரத்தம் & எலும்பு மஜ்ஜை)", "Rakta/Majja", "Mars",
         "Controls hemoglobin synthesis, red blood cells, muscular vitality, and cellular oxygenation",
         "ரத்த சிவப்பணு உற்பத்தி, தசை ஆற்றல், ஆக்ஸிஜன் விநியோகம்"),
        (4, "Mamsa & Twak (Flesh, Muscle & Skin)", "மாமிசம் & த்வக் (தசை திசு & தோல்)", "Mamsa/Twak", "Mercury",
         "Maintains cutaneous nerve endings, muscular elasticity, and dermal barrier protection",
         "தோலின் நரம்பு முனைகள், தசை மீள்தன்மை மற்றும் தோல் பாதுகாப்பு"),
        (5, "Medas (Adipose Tissue & Glycogen)", "மேதஸ் (கொழுப்பு திசு & கிளைகோஜன்)", "Medas", "Jupiter",
         "Regulates adipose cushioning, liver lipid reserves, and systemic metabolic temperature",
         "உடல் கொழுப்பு திசுக்கள், கல்லீரல் கொழுப்பு சேமிப்பு, வளர்சிதை மாற்ற வெப்பநிலை"),
        (6, "Shukra (Reproductive Fluids & Ojas)", "சுக்கிரன் / சுக்லம் (விந்தணு & கருமுட்டை வீரியம்)", "Shukra", "Venus",
         "Governs endocrine secretion, generative vitality, reproductive essence, and cellular immunity (Ojas)",
         "நாளமில்லா சுரப்பி சுரப்புகள், விந்து-நாத பலம், ஓஜஸ் எனப்படும் நோய் எதிர்ப்பு சக்தி"),
        (7, "Snayu (Sinews, Tendons & Ligaments)", "ஸ்நாயு (நரம்பு இணைப்புகள் & தசைநார்கள்)", "Snayu", "Saturn",
         "Binds joints, reinforces articulation cartilage, tendons, ligaments, and fibrous stability",
         "மூட்டு தசைநார்கள், குருத்தெலும்பு இணைப்புகள், மூட்டுகளின் வளைந்து கொடுக்கும் தன்மை"),
    ]

    sapta_dhatus: List[SaptaDhatuDetail] = []
    for d_num, name_en, name_ta, skt, planet, func_en, func_ta in dhatu_configs:
        p_house = ctx.planet_house.get(planet, 1)
        p_sign = ctx.planet_sign.get(planet, 1)
        is_ex = (EXALTATION_SIGNS.get(planet) == p_sign)
        is_deb = (DEBILITATION_SIGNS.get(planet) == p_sign)
        is_own = p_sign in OWN_SIGNS.get(planet, [])
        is_dusthana = p_house in (6, 8, 12)

        if is_ex or is_own:
            status = "Fortified"
            obs_en = f"{planet} is dignified in own/exaltation sign (House {p_house}), conferring robust tissue vigor."
            obs_ta = f"{planet} ஆட்சி/உச்சம் பெற்று (பாவம் {p_house}) நின்று இத்திசுவுக்கு அபார ஆற்றலை அளிக்கிறது."
        elif is_deb:
            status = "Afflicted"
            obs_en = f"{planet} is in debilitation sign {p_sign}, indicating systemic tissue sensitivity requiring dietary care."
            obs_ta = f"{planet} நீசம் பெற்று நிற்பதால் இந்நாடி திசுவுக்கு உரிய இயற்கை ஊட்டச்சத்து ஆதரவு தேவை."
        elif is_dusthana:
            status = "Weakened"
            obs_en = f"{planet} occupies Dusthana House {p_house}, advising regular metabolic toning."
            obs_ta = f"{planet} மறைவு ஸ்தானமான {p_house}-ல் உள்ளதால் தொடர் உடற்பயிற்சியும் கவனமும் தேவை."
        else:
            status = "Balanced"
            obs_en = f"{planet} occupies House {p_house} in harmonious dignity."
            obs_ta = f"{planet} பாவம் {p_house}-ல் இயல்பான சுப பலத்துடன் அமர்ந்துள்ளது."

        sapta_dhatus.append(
            SaptaDhatuDetail(
                dhatu_number=d_num,
                dhatu_name_en=name_en,
                dhatu_name_ta=name_ta,
                sanskrit_term=skt,
                governing_planet=planet,
                physiological_function_en=func_en,
                physiological_function_ta=func_ta,
                status=status,
                observations_en=obs_en,
                observations_ta=obs_ta,
            )
        )

    # 4. Endocrine Glands Governance (Dr. S. S. Chatterjee)
    gland_configs = [
        ("Pituitary Gland (Master Gland)", "பிட்யூட்டரி சுரப்பி (தலைமை நாளமில்லா சுரப்பி)",
         ["Sun", "Mars", "Moon"], "Growth Hormone, TSH, ACTH, Oxytocin",
         "Governs growth, somatic rhythm, cranial blood flow, and somatic homeostasis",
         "உடல் வளர்ச்சி, நாளமில்லா சுரப்பிகளின் ஒட்டுமொத்த இயக்கம், ரத்த ஓட்ட கட்டுப்பாடு"),
        ("Pineal Gland", "பீனியல் சுரப்பி",
         ["Ketu", "Moon"], "Melatonin, Serotonin",
         "Synchronizes the circadian biological clock, deep sleep, and spiritual intuition",
         "சிர்காடியன் உயிரியல் கடிகாரம், தூக்க சுழற்சி, மன அமைதி"),
        ("Thyroid Gland", "தைராய்டு சுரப்பி",
         ["Jupiter", "Sun"], "Thyroxine (T4), Triiodothyronine (T3), Calcitonin",
         "Controls basal metabolic rate, systemic cellular energy consumption, and neck vitality",
         "வளர்சிதை மாற்ற வேகம், உடலின் ஆற்றல் பயன்பாடு, கழுத்துப் பகுதி உறுதி"),
        ("Parathyroid Gland", "பாரா தைராய்டு சுரப்பிகள்",
         ["Saturn", "Mercury"], "Parathyroid Hormone (PTH)",
         "Regulates calcium-phosphate serum ratios, neuro-muscular electrical transmission",
         "கால்சியம் மற்றும் பாஸ்பரஸ் சமநிலை, நரம்பு-தசை மின் சமிக்ஞைகள்"),
        ("Thymus Gland", "தைமஸ் சுரப்பி",
         ["Moon"], "Thymosin",
         "Matures T-lymphocytes, pediatric immune competence, and thoracic lymphatic defense",
         "டி-செல்கள் முதிர்ச்சி, நோய் எதிர்ப்பு மண்டலத்தின் ஆரம்பக்கட்ட பலம்"),
        ("Pancreas (Endocrine Islets)", "கணையம் (லாங்கர்ஹான்ஸ் திட்டுகள்)",
         ["Mars", "Jupiter", "Venus"], "Insulin, Glucagon, Somatostatin",
         "Maintains blood glucose homeostasis, glycogen conversion, and digestive enzymes",
         "ரத்த சர்க்கரை சமநிலை, இன்சுலின் சுரப்பு, செரிமான நொதிகள்"),
        ("Adrenal Glands", "அட்ரினல் சுரப்பிகள்",
         ["Mars", "Venus", "Jupiter"], "Epinephrine, Cortisol, Aldosterone",
         "Governs stress fight-or-flight response, blood pressure, renal electrolyte balance",
         "மன அழுத்தப் போராட்டம், அவசரகால ரத்த அழுத்தம், எலக்ட்ரோலைட் சமநிலை"),
        ("Sex Glands (Gonads / Ovaries / Testes)", "இனப்பெருக்க சுரப்பிகள் (கருப்பை / விந்தகம்)",
         ["Mars", "Venus"], "Estrogen, Progesterone, Testosterone",
         "Drives secondary sexual characteristics, reproductive fertility, and hormonal vitality",
         "இனப்பெருக்க ஆற்றல், பாலியல் ஹார்மோன் சமநிலை, கருவுறுதல் திறன்"),
    ]

    endocrine_glands: List[EndocrineGlandDetail] = []
    for g_en, g_ta, gov_planets, hormones, role_en, role_ta in gland_configs:
        vulnerable_count = sum(1 for p in gov_planets if ctx.planet_house.get(p) in (6, 8, 12) or ctx.planet_sign.get(p) == DEBILITATION_SIGNS.get(p))
        if vulnerable_count >= 2:
            g_status = "Afflicted"
            g_obs_en = f"Multiple governing planets ({', '.join(gov_planets)}) occupy Dusthana houses or debilitation."
            g_obs_ta = f"இச்சுரப்பியை ஆளும் பல கிரகங்கள் ({', '.join(gov_planets)}) மறைவு ஸ்தானங்களில் உள்ளன."
        elif vulnerable_count == 1:
            g_status = "Vulnerable"
            g_obs_en = f"One governing planet faces placement strain; maintain balanced dietary habits."
            g_obs_ta = f"ஆளும் கிரகங்களில் ஒன்று பலவீனமாக உள்ளது; சீரான உணவுப் பழக்கம் நலம் தரும்."
        else:
            g_status = "Balanced"
            g_obs_en = f"Governing planets ({', '.join(gov_planets)}) possess supportive natal strength."
            g_obs_ta = f"இச்சுரப்பியை ஆளும் கிரகங்கள் ({', '.join(gov_planets)}) நற்பலத்துடன் உள்ளன."

        endocrine_glands.append(
            EndocrineGlandDetail(
                gland_name_en=g_en,
                gland_name_ta=g_ta,
                governing_planets=gov_planets,
                hormones_secreted=hormones,
                physiological_role_en=role_en,
                physiological_role_ta=role_ta,
                status=g_status,
                observations_en=g_obs_en,
                observations_ta=g_obs_ta,
            )
        )

    # 5. Tridosha Anatomical Site Matrix
    tridosha_sites = [
        TridoshaSiteDetail(
            site_en="Head (Cranial Axis)",
            site_ta="தலைப் பகுதி (மண்டை ஓட்டு மண்டலம்)",
            governing_signs="Aries (Mesha) & Leo (Simha)",
            vata_manifestation="Thrombosis of cerebral vessels, hemiplegia, sudden stroke, nervous vertigo",
            pitta_manifestation="Meningitis, acute encephalitis, cranial fevers, migraine, heat exhaustion",
            kapha_manifestation="Cerebral edema, hydrocephalus, morning dullness, sinus fluid blockages",
        ),
        TridoshaSiteDetail(
            site_en="Neck & Throat (Cervical Axis)",
            site_ta="கழுத்து & தொண்டை பகுதி",
            governing_signs="Taurus (Vrishabha) & Gemini (Mithuna)",
            vata_manifestation="Vocal cord palsy, spasmodic torticollis, dry cough, hoarse stammering",
            pitta_manifestation="Acute laryngitis, pharyngitis, burning throat ulcers, tonsillar heat",
            kapha_manifestation="Tonsillitis, follicular goiter, excessive salivary secretions, mucus plug",
        ),
        TridoshaSiteDetail(
            site_en="Chest & Lungs (Thoracic Axis)",
            site_ta="மார்பு & நுரையீரல் பகுதி",
            governing_signs="Cancer (Karka) & Leo (Simha)",
            vata_manifestation="Bronchial asthma, dry pleurodynia, erratic cardiac palpitations",
            pitta_manifestation="Acute bronchitis, lobar pneumonia, pericardial inflammation, hot hemoptysis",
            kapha_manifestation="Pleurisy with effusion, chronic phlegm accumulation, congestive pulmonary edema",
        ),
        TridoshaSiteDetail(
            site_en="Abdomen (Epigastric & Intestinal Axis)",
            site_ta="வயிறு & குடல் பகுதி",
            governing_signs="Virgo (Kanya) & Scorpio (Vrishchika)",
            vata_manifestation="Chronic irritable bowel, intestinal colic, painful flatulence, spastic constipation",
            pitta_manifestation="Peptic ulcers, acute appendicitis, cholecystitis, rupture of inflamed bowels",
            kapha_manifestation="Ascites, abdominal tumors, hepatic fatty congestion, lymphatic stagnation",
        ),
        TridoshaSiteDetail(
            site_en="Legs & Feet (Locomotor Axis)",
            site_ta="கால்கள் & பாதங்கள் (நடமாட்ட மண்டலம்)",
            governing_signs="Aquarius (Kumbha) & Pisces (Meena)",
            vata_manifestation="Buerger's disease, Raynaud's cold ischemia, sciatic tremors, ankle stiffness",
            pitta_manifestation="Acute osteomyelitis, cellulitis, hot varicose phlebitis, burning soles",
            kapha_manifestation="Filariasis (elephantiasis), pedal edema, cold synovial effusions in knees",
        ),
    ]

    # 6. Diabetes Mellitus (Madhumeha) Special Module
    ven_sign = ctx.planet_sign.get("Venus", 1)
    ven_h = ctx.planet_house.get("Venus", 1)
    jup_sign = ctx.planet_sign.get("Jupiter", 1)
    jup_h = ctx.planet_house.get("Jupiter", 1)
    h6_occ = ctx.house_occupants.get(6, [])
    h12_occ = ctx.house_occupants.get(12, [])
    virgo_occ = ctx.sign_occupants.get(6, [])

    affliction_score = 0
    if ven_sign == 6 or ven_h in (6, 8, 12):  # Venus debilitated or in Dusthana
        affliction_score += 1
    if any(m in virgo_occ for m in ("Saturn", "Mars", "Rahu", "Ketu")):
        affliction_score += 1
    if any(m in h6_occ for m in ("Mars", "Saturn", "Rahu")) and any(m in h12_occ for m in ("Mars", "Saturn", "Rahu")):
        affliction_score += 1
    if jup_sign == 10 or jup_h in (6, 8, 12):  # Jupiter debilitated or in Dusthana
        affliction_score += 1
    if "Sun" in h6_occ or "Saturn" in h6_occ:
        affliction_score += 1

    risk_level = "High" if affliction_score >= 3 else ("Moderate" if affliction_score >= 1 else "Low")

    diabetes_assessment = DiabetesMellitusAssessment(
        venus_status=f"Occupies House {ven_h} in Sign {SIGN_NAMES_EN.get(ven_sign, '')}" + (" (Debilitated/Dusthana)" if ven_sign == 6 or ven_h in (6, 8, 12) else " (Stable)"),
        jupiter_status=f"Occupies House {jup_h} in Sign {SIGN_NAMES_EN.get(jup_sign, '')}" + (" (Debilitated/Dusthana)" if jup_sign == 10 or jup_h in (6, 8, 12) else " (Stable)"),
        virgo_status=f"Occupants in Virgo: {', '.join(virgo_occ) or 'Unoccupied (Clear)'}",
        sixth_house_status=f"Occupants in 6th: {', '.join(h6_occ) or 'Unoccupied (Clear)'}",
        affliction_score=affliction_score,
        risk_level=risk_level,
        symptoms_noted=[
            "Sudden loss of physical stamina and unexplained fatigue",
            "Polydipsia (excessive thirst) and polyuria (frequent urination)",
            "Polyphagia (excessive hunger) coupled with sudden weight loss",
            "Slow-healing dermal boils, skin dryness, and neuritis tingling in extremities",
            "Fluctuating blood glucose levels causing ocular or emotional distress",
        ],
        remedial_measures_en=[
            "50g germinated grams (sprouted chickpeas) taken with fresh curd daily to nourish glandular Venus",
            "20 fresh green neem leaves or neem juice taken on empty stomach to cleanse blood glucose",
            "Fresh bitter gourd (karela) juice taken regularly in morning hours",
            "1 spoonful of fenugreek (methi) powder taken with warm low-fat milk for 60 consecutive days",
            "Diet rich in okra (bhindi) soup, drumsticks (moringa), and avoiding hydrogenated/saturated trans-fats",
            "30 minutes of brisk daily walking to regulate insulin receptor sensitivity",
        ],
        remedial_measures_ta=[
            "சுக்கிரனை பலப்படுத்த 50 கிராம் முளைகட்டிய பாசிப்பயறு/சுண்டலை தயிருடன் தினசரி உண்ணுதல்",
            "ரத்த சர்க்கரையை சீராக்க 20 புதிய வேப்பிலைகளை மென்று தின்னுதல் அல்லது வேப்பிலை சாறு அருந்துதல்",
            "தினசரி காலையில் புதிய பாகற்காய் (கரேலா) சாறு அருந்துதல்",
            "ஒரு ஸ்பூன் வெந்தயப் பொடியை வெதுவெதுப்பான கொழுப்பு நீக்கிய பாலில் கலந்து 60 நாட்கள் தொடர்ந்து குடித்தல்",
            "வெண்டைக்காய் சூப், முருங்கைக்காய் சேர்த்த சத்தான உணவுகளை உண்பது மற்றும் கொழுப்பு உணவுகளைத் தவிர்த்தல்",
            "தினசரி 30 நிமிடங்கள் விறுவிறுப்பான நடைபயிற்சி மேற்கொண்டு இன்சுலின் ஏற்பித் திறனை அதிகரித்தல்",
        ],
    )

    # 7. Modern 21st-Century Complex Diseases (Dr. S. S. Chatterjee)
    modern_diseases = [
        ModernComplexDiseaseDetail(
            name_en="Hepatitis C Viral Hepatic Strain",
            name_ta="ஹெபடைடிஸ் சி கல்லீரல் பாதிப்பு",
            key_symptoms="Severe abdominal cramps, persistent nausea, late-stage serious liver infection, jaundice",
            astrological_indicators="Ketu in Lagna with 8th lord affliction and Jupiter-Mars friction in Dusthanas",
        ),
        ModernComplexDiseaseDetail(
            name_en="Systemic Lupus Erythematosus (Autoimmune)",
            name_ta="லூபஸ் தன்னுடல் தாக்கு நோய்",
            key_symptoms="Butterfly rash on cheeks and bridge of nose, photosensitivity, arthritic joint stiffness, hair loss",
            astrological_indicators="Sun-Rahu in 4th/8th combined with afflicted Venus and Lagna lord hemmed in malefic scissors",
        ),
        ModernComplexDiseaseDetail(
            name_en="Celiac Disease & Gluten Enteropathy",
            name_ta="சீலியாக் குடல் ஒவ்வாமை நோய்",
            key_symptoms="Abdominal cramping, chronic bloating, severe gas, unexplained anemia, and persistent weight drop",
            astrological_indicators="Virgo afflicted by Saturn, Moon-Mars in 6th/8th, and afflicted Mercury",
        ),
        ModernComplexDiseaseDetail(
            name_en="Colorectal Mucosal Vulnerability",
            name_ta="பெருங்குடல் & மலக்குடல் சளிச்சவ்வு குறைபாடு",
            key_symptoms="Persistent bowel irregularities, alternating diarrhea and constipation, unexplained fatigue",
            astrological_indicators="Saturn-Rahu in 2nd/8th houses with afflicted 6th lord and lack of Jupiter aspect",
        ),
        ModernComplexDiseaseDetail(
            name_en="Benign Paroxysmal Positional Vertigo (BPPV)",
            name_ta="நிலை சார்ந்த திடீர் தலைச்சுற்றல் (BPPV)",
            key_symptoms="Sudden sensation that surroundings are spinning, light headache, blurred vision, postural nausea",
            astrological_indicators="Mercury in 6th receiving Saturn's cold aspect, combined with weak Moon in dual signs",
        ),
        ModernComplexDiseaseDetail(
            name_en="Chlamydia & Deep Urogenital Inflammation",
            name_ta="கிளமிடியா & பிறப்புறுப்புப் பாதை அழற்சி",
            key_symptoms="Dysuria (burning on urination), pelvic tenderness, reproductive mucosal irritation",
            astrological_indicators="Mars-Venus conjunction in 8th house or Rahu with Venus in 7th house",
        ),
        ModernComplexDiseaseDetail(
            name_en="Obstructive Sleep Apnea",
            name_ta="தூக்கத்தில் மூச்சுத்திணறல் (ஸ்லீப் அப்னியா)",
            key_symptoms="Loud irregular snoring, abrupt awakenings with choking, excessive daytime sleepiness",
            astrological_indicators="Sun in 12th afflicted by Saturn/Rahu, or Saturn in Lagna with Moon in 12th",
        ),
        ModernComplexDiseaseDetail(
            name_en="Cranial & Aortic Vascular Aneurysm",
            name_ta="மூளை மற்றும் பெருந்தமனி ரத்த நாள வீக்கம்",
            key_symptoms="Sudden piercing headache, vomiting, transient visual blurring, loss of balance",
            astrological_indicators="Sun-Mars conjunction in Lagna or 8th house with malefic aspect across arterial signs",
        ),
        ModernComplexDiseaseDetail(
            name_en="Fluorosis & Mineral Imbalance",
            name_ta="ஃப்ளூரோசிஸ் எலும்பு மற்றும் பற்கள் பாதிப்பு",
            key_symptoms="Mottled enamel on teeth, early joint stiffness, calcification of ligaments, bone fragility",
            astrological_indicators="Saturn in 2nd with Rahu, accompanied by afflicted Sun (bones) and Mercury (teeth)",
        ),
        ModernComplexDiseaseDetail(
            name_en="Gestational & Clinical Hypothyroidism",
            name_ta="ஹைப்போ தைராய்டிசம் (தைராய்டு சுரப்புக் குறைவு)",
            key_symptoms="Unexplained weight gain, cold intolerance, profound morning lethargy, memory lapses",
            astrological_indicators="Jupiter and Sun both afflicted by Saturn/Nodes, impairing metabolic basal rate",
        ),
    ]

    # 8. Natural Remedies & Health Maintenance Guide
    natural_remedies = NaturalRemediesGuide(
        planetary_colour_therapy=[
            {"planet": "Sun", "colour": "Maroon / Deep Red", "diet_items": "Watermelon, Carrot, Tomato, Red Pomegranate", "beneficial_for": "Cardiovascular stamina, bone density, vital energy"},
            {"planet": "Moon", "colour": "Natural White", "diet_items": "Milk, Fresh Curd, Coconut Water, White Rice, Cauliflower", "beneficial_for": "Mental calmness, lymphatic fluid balance, mucosal healing"},
            {"planet": "Mars", "colour": "Bright Scarlet Red", "diet_items": "Beetroot, Red lentils (Masoor dal), Apples, Red Bell Pepper", "beneficial_for": "Hemoglobin generation, muscle tone, inflammatory immunity"},
            {"planet": "Mercury", "colour": "Emerald Green", "diet_items": "Green leafy vegetables, Green Gram (Moong), Mint, Coriander, Cucumber", "beneficial_for": "Nervous coordination, dermal elasticity, speech clarity"},
            {"planet": "Jupiter", "colour": "Golden Yellow", "diet_items": "Turmeric (Curcumin), Papaya, Banana, Yellow Lentils, Oranges, Lemon", "beneficial_for": "Liver detoxification, glycogen storage, deep tissue recovery"},
            {"planet": "Venus", "colour": "Cream / Pure White", "diet_items": "Sprouted Chickpeas, Cow's Ghee, Almonds, Cashews, Low-fat Curd", "beneficial_for": "Glandular harmony, reproductive vitality, skin radiance"},
            {"planet": "Saturn", "colour": "Violet / Dark Blue", "diet_items": "Black sesame, Blueberries, Black grapes, Figs, Prunes", "beneficial_for": "Bone-joint binding, tendon flexibility, longevity preservation"},
        ],
        metal_charged_waters=[
            {"metal": "Copper-Charged Water (Tamra Jal)", "preparation": "Boil 50-60g pure copper piece in 1.5 litres of water for 45 mins until reduced", "therapeutic_use": "Nervous disorders, high arterial blood pressure, arthritis joint pain, neuro-muscular vitality"},
            {"metal": "Silver-Charged Water (Rajat Jal)", "preparation": "Boil 50-60g pure silver coin/vessel in water for 45 mins", "therapeutic_use": "Digestive tract cooling, gastritis, urinary burning, kidney fluid balance, internal fevers"},
            {"metal": "Gold-Charged Water (Swarna Jal)", "preparation": "Boil 24k pure gold piece (approx 10-20g) in drinking water for 1 hour", "therapeutic_use": "Supreme tonic for heart, lungs, asthma, bronchial strength, intellect, memory retention"},
            {"metal": "Iron-Charged Water (Loha Jal)", "preparation": "Boil sanitized wrought iron piece in water for 45 mins", "therapeutic_use": "Iron deficiency anemia, low red blood cell count, postpartum weakness, tissue pallor"},
        ],
        fasting_and_diet=[
            "Fasting on Tuesdays (Mangalavara): Calms excess Pitta fire, reduces inflammatory tendencies, prevents sudden accidents",
            "Fasting on Saturdays (Shanivara): Pacifies Vata wind, eases joint stiffness, detoxifies sluggish digestive residues",
            "Low-Salt Regimen on Saturdays: Avoiding table salt (NaCl) on Saturdays preserves vascular resilience and reduces water retention",
            "Colour Harmonization: Strictly avoid wearing or consuming dominant colors of functional 6th and 8th lords to prevent symptom aggravation",
            "Sprouted Grams & Curd Therapy: 50g sprouted gram with fresh curd and 20 neem leaves for 60 days cures pancreatic and skin distress",
        ],
        vega_dharana_urges=[
            {"urge": "Urge to Pass Urine (Mutra Vega)", "consequences_if_suppressed": "Severe bladder and pelvic pain, dysuria, renal stone formation, reflex headache"},
            {"urge": "Urge to Eliminate Feces (Purisha Vega)", "consequences_if_suppressed": "Abdominal cramps, chronic flatulence, severe colonic constipation, calf muscle spasms"},
            {"urge": "Urge to Eliminate Semen (Shukra Vega)", "consequences_if_suppressed": "Testicular tenderness, cardiac distress, urinary hesitancy, prostate congestion"},
            {"urge": "Urge to Pass Flatus (Vata Vega)", "consequences_if_suppressed": "Intestinal bloating, sharp epigastric pain, upward reflux, diaphragm displacement"},
            {"urge": "Urge to Vomit (Chardi Vega)", "consequences_if_suppressed": "Severe urticaria, skin rashes, jaundice, anemia, black facial pigmentation, fever"},
            {"urge": "Urge to Sneeze (Kshavathu Vega)", "consequences_if_suppressed": "Headache, facial nerve palsy, neck torticollis, sensory organ dullness"},
            {"urge": "Urge to Belch (Udgara Vega)", "consequences_if_suppressed": "Hiccups, breathlessness, thoracic tightness, cardiac arrhythmia sensations"},
            {"urge": "Urge to Yawn (Jrimbha Vega)", "consequences_if_suppressed": "Tremors, convulsions, muscular contractions, numbness, aggravated Vata"},
            {"urge": "Urge to Eat / Hunger (Kshudha Vega)", "consequences_if_suppressed": "Severe emaciation, giddiness, cognitive exhaustion, gastric ulceration"},
            {"urge": "Urge to Drink / Thirst (Trishna Vega)", "consequences_if_suppressed": "Dry throat, auditory dimness, cardiac fatigue, hemoconcentration"},
            {"urge": "Urge to Weep / Tears (Bashpa Vega)", "consequences_if_suppressed": "Severe ocular pressure, heart disease, vertigo, clinical depression, migraines"},
            {"urge": "Urge to Sleep (Nidra Vega)", "consequences_if_suppressed": "Heaviness in eyes, chronic daytime drowsiness, delirium, loss of cell immunity"},
            {"urge": "Urge for Heavy Breathing after Exertion (Shrama Shwasa)", "consequences_if_suppressed": "Acute cardiac syncope, fainting, chest pain, chronic pulmonary distress"},
        ],
    )

    # 9. Evaluate 28 Dr. Chatterjee Golden Rules
    evaluated_golden_rules: List[MedicalRule] = []
    
    sun_h = ctx.planet_house.get("Sun", 1)
    moon_h = ctx.planet_house.get("Moon", 1)
    mars_h = ctx.planet_house.get("Mars", 1)
    merc_h = ctx.planet_house.get("Mercury", 1)
    jup_h = ctx.planet_house.get("Jupiter", 1)
    ven_h = ctx.planet_house.get("Venus", 1)
    sat_h = ctx.planet_house.get("Saturn", 1)
    rahu_h = ctx.planet_house.get("Rahu", 1)
    ketu_h = ctx.planet_house.get("Ketu", 1)

    h1_occ = ctx.house_occupants.get(1, [])
    h2_occ = ctx.house_occupants.get(2, [])
    h4_occ = ctx.house_occupants.get(4, [])
    h5_occ = ctx.house_occupants.get(5, [])
    h6_occ = ctx.house_occupants.get(6, [])
    h7_occ = ctx.house_occupants.get(7, [])
    h8_occ = ctx.house_occupants.get(8, [])
    h12_occ = ctx.house_occupants.get(12, [])

    l1_planet = ctx.house_lords.get(1, "Mars")
    l4_planet = ctx.house_lords.get(4, "Moon")
    l6_planet = ctx.house_lords.get(6, "Mercury")
    l7_planet = ctx.house_lords.get(7, "Venus")
    l8_planet = ctx.house_lords.get(8, "Mars")

    for r_id, r_def in DR_CHATTERJEE_GOLDEN_RULES_REGISTRY.items():
        is_active = False
        trig_pos: List[str] = []
        planets_inv: List[str] = []
        rel_houses: List[int] = []

        if r_id == "chatterjee_death_point_saturn":
            if sat_aspect_active:
                is_active = True
                trig_pos = [f"Transit Saturn in Sign {sat_curr_sign} casts drishti on Death Point at {deg_in_sign:.1f}° {dp_sign_en}"]
                planets_inv = ["Saturn"]
                rel_houses = [dp_sign_idx]

        elif r_id == "chatterjee_parijata_longevity":
            if (len(ben_in_kendras) >= 2 or has_parijata) and len(mal_in_upachaya) >= 1:
                is_active = True
                trig_pos = [f"Benefics in Kendras/Trines ({', '.join(ben_in_kendras)}) and Malefics in 3/11 ({', '.join(mal_in_upachaya)})"]
                planets_inv = ben_in_kendras + mal_in_upachaya
                rel_houses = [1, 4, 7, 10, 3, 11]

        elif r_id == "chatterjee_diabetes_mellitus":
            if affliction_score >= 2:
                is_active = True
                trig_pos = [f"Diabetes marker score {affliction_score}/5: Venus in House {ven_h}, 6th/Virgo affliction noted"]
                planets_inv = ["Venus", "Jupiter"]
                rel_houses = [6, 12, ven_h]

        elif r_id == "chatterjee_rahu_5th_gastro":
            if rahu_h == 5:
                is_active = True
                trig_pos = ["Rahu posited in 5th House"]
                planets_inv = ["Rahu"]
                rel_houses = [5]

        elif r_id == "chatterjee_saturn_5th_dyspepsia":
            if sat_h == 5:
                is_active = True
                trig_pos = ["Saturn posited in 5th House"]
                planets_inv = ["Saturn"]
                rel_houses = [5]

        elif r_id == "chatterjee_sun_rahu_4th_skin":
            if sun_h == 4 and rahu_h == 4:
                is_active = True
                trig_pos = ["Sun and Rahu conjoined in 4th House"]
                planets_inv = ["Sun", "Rahu"]
                rel_houses = [4]

        elif r_id == "chatterjee_venus_saturn_8th_chronic":
            if ven_h == 8 and sat_h == 8:
                is_active = True
                trig_pos = ["Venus and Saturn conjoined in 8th House"]
                planets_inv = ["Venus", "Saturn"]
                rel_houses = [8]

        elif r_id == "chatterjee_mars_venus_8th_urogenital":
            if mars_h == 8 and ven_h == 8:
                is_active = True
                trig_pos = ["Mars and Venus conjoined in 8th House"]
                planets_inv = ["Mars", "Venus"]
                rel_houses = [8]

        elif r_id == "chatterjee_mars_saturn_8th_digestive":
            if mars_h == 8 and sat_h == 8:
                is_active = True
                trig_pos = ["Mars and Saturn conjoined in 8th House"]
                planets_inv = ["Mars", "Saturn"]
                rel_houses = [8]

        elif r_id == "chatterjee_saturn_rahu_8th_obesity":
            if sat_h == 8 and rahu_h == 8:
                is_active = True
                trig_pos = ["Saturn and Rahu conjoined in 8th House"]
                planets_inv = ["Saturn", "Rahu"]
                rel_houses = [8]

        elif r_id == "chatterjee_saturn_ketu_8th_gangrene":
            if sat_h == 8 and ketu_h == 8:
                is_active = True
                trig_pos = ["Saturn and Ketu conjoined in 8th House"]
                planets_inv = ["Saturn", "Ketu"]
                rel_houses = [8]

        elif r_id == "chatterjee_sun_mars_8th_pitta_burn":
            if sun_h == 8 and mars_h == 8:
                is_active = True
                trig_pos = ["Sun and Mars conjoined in 8th House"]
                planets_inv = ["Sun", "Mars"]
                rel_houses = [8]

        elif r_id == "chatterjee_moon_saturn_8th_injury":
            if moon_h == 8 and sat_h == 8:
                is_active = True
                trig_pos = ["Moon and Saturn conjoined in 8th House"]
                planets_inv = ["Moon", "Saturn"]
                rel_houses = [8]

        elif r_id == "chatterjee_saturn_mercury_respiratory":
            if sat_h == merc_h and ctx.planet_sign.get("Saturn") not in (7, 10, 11) and ctx.planet_sign.get("Mercury") not in (3, 6):
                is_active = True
                trig_pos = [f"Saturn and Mercury conjoined in House {sat_h} without exaltation/own sign"]
                planets_inv = ["Saturn", "Mercury"]
                rel_houses = [sat_h]

        elif r_id == "chatterjee_sun_mars_lagna_bp":
            if sun_h == 1 and mars_h == 1:
                is_active = True
                trig_pos = ["Sun and Mars conjoined in Lagna (1st House)"]
                planets_inv = ["Sun", "Mars"]
                rel_houses = [1]

        elif r_id == "chatterjee_blood_4th_mars_moon":
            is_4th_affl = any(m in h4_occ for m in ("Mars", "Saturn", "Rahu", "Ketu")) or ctx.planet_house.get(l4_planet) in (6, 8, 12)
            is_moon_affl = moon_h in (6, 8, 12) or any(ctx.planet_aspects_planet(m, "Moon") for m in ("Saturn", "Mars"))
            is_mars_affl = mars_h in (6, 8, 12) or any(ctx.planet_aspects_planet(m, "Mars") for m in ("Saturn", "Rahu"))
            if is_4th_affl and (is_moon_affl or is_mars_affl):
                is_active = True
                trig_pos = [f"4th house afflicted and blood karakas Moon (H{moon_h}) / Mars (H{mars_h}) under malefic pressure"]
                planets_inv = ["Moon", "Mars"]
                rel_houses = [4]

        elif r_id == "chatterjee_mercury_6th_saturn_aspect_ear":
            if merc_h == 6 and ctx.planet_aspects_planet("Saturn", "Mercury"):
                is_active = True
                trig_pos = ["Mercury in 6th house receiving aspect from Saturn"]
                planets_inv = ["Mercury", "Saturn"]
                rel_houses = [6]

        elif r_id == "chatterjee_lagna_papa_kartari":
            if (sat_h == 12 and mars_h == 2) or (mars_h == 12 and sat_h == 2):
                is_active = True
                trig_pos = [f"Lagna flanked by Saturn (H{sat_h}) and Mars (H{mars_h}) in Papa-Kartari"]
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [1, 2, 12]

        elif r_id == "chatterjee_jupiter_mars_stomach":
            if ctx.planet_aspects_planet("Mars", "Jupiter") or ctx.planet_aspects_planet(l8_planet, "Jupiter"):
                is_active = True
                trig_pos = [f"Jupiter in House {jup_h} aspected by Mars or 8th lord {l8_planet}"]
                planets_inv = ["Jupiter", "Mars"]
                rel_houses = [jup_h]

        elif r_id == "chatterjee_kidney_7th_taurus_libra":
            is_7th_affl = l6_planet in h7_occ or ctx.planet_aspects_planet(l6_planet, l7_planet)
            is_ven_affl = ven_sign == 6 or ven_h in (6, 8, 12) or any(m in ("Mars", "Saturn", "Rahu") for m in ctx.sign_occupants.get(ven_sign, []))
            if is_7th_affl and is_ven_affl:
                is_active = True
                trig_pos = [f"7th house afflicted by 6th lord {l6_planet} and Venus afflicted in Sign {SIGN_NAMES_EN.get(ven_sign, '')}"]
                planets_inv = ["Venus", l6_planet]
                rel_houses = [7]

        elif r_id == "chatterjee_lagna_lord_shubha_kartari":
            h_l1 = ctx.planet_house.get(l1_planet, 1)
            prev_h = 12 if h_l1 == 1 else h_l1 - 1
            next_h = 1 if h_l1 == 12 else h_l1 + 1
            has_prev_ben = any(p in ctx.house_occupants.get(prev_h, []) for p in ("Jupiter", "Venus", "Mercury"))
            has_next_ben = any(p in ctx.house_occupants.get(next_h, []) for p in ("Jupiter", "Venus", "Mercury"))
            no_mal_kartari = not any(p in ctx.house_occupants.get(prev_h, []) for p in ("Saturn", "Mars", "Rahu", "Ketu")) and not any(p in ctx.house_occupants.get(next_h, []) for p in ("Saturn", "Mars", "Rahu", "Ketu"))
            if has_prev_ben and has_next_ben and no_mal_kartari:
                is_active = True
                trig_pos = [f"Lagna lord {l1_planet} hemmed between benefics in houses {prev_h} and {next_h}"]
                planets_inv = [l1_planet]
                rel_houses = [h_l1, prev_h, next_h]

        elif r_id == "chatterjee_urinary_sun_venus_saturn_5th":
            if "Sun" in h5_occ and "Venus" in h5_occ and "Saturn" in h5_occ:
                is_active = True
                trig_pos = ["Sun, Venus, and Saturn conjoined in 5th House"]
                planets_inv = ["Sun", "Venus", "Saturn"]
                rel_houses = [5]

        elif r_id == "chatterjee_mars_4th_moon_blood":
            if (mars_h == 4 and ctx.planet_aspects_planet("Mars", "Moon")) or (moon_h == 4 and ctx.planet_aspects_planet("Mars", "Moon")):
                is_active = True
                trig_pos = ["Mars in 4th aspecting Moon or Moon in 4th aspected by Mars"]
                planets_inv = ["Mars", "Moon"]
                rel_houses = [4]

        elif r_id == "chatterjee_insomnia_sun_12th":
            sun_12th_h = 12 if sun_h == 1 else sun_h - 1
            sun_12th_occ = ctx.house_occupants.get(sun_12th_h, [])
            if any(m in h12_occ for m in ("Saturn", "Mars", "Rahu", "Ketu")) or any(m in sun_12th_occ for m in ("Saturn", "Mars", "Rahu", "Ketu")):
                is_active = True
                trig_pos = [f"Malefic in 12th from Lagna (H12) or 12th from Sun (House {sun_12th_h})"]
                planets_inv = ["Sun", "Saturn"]
                rel_houses = [12, sun_12th_h]

        elif r_id == "chatterjee_saturn_mars_vata_rakta":
            if sat_h in (1, 6, 8) and ctx.planet_aspects_planet("Mars", "Saturn"):
                is_active = True
                trig_pos = [f"Saturn in House {sat_h} aspected by Mars"]
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [sat_h]

        elif r_id == "chatterjee_moon_6_12_saturn_lagna_asthma":
            if sat_h == 1 and moon_h in (6, 12):
                is_active = True
                trig_pos = [f"Saturn in Lagna with Moon in House {moon_h}"]
                planets_inv = ["Saturn", "Moon"]
                rel_houses = [1, moon_h]

        elif r_id == "chatterjee_saturn_rahu_2nd_constipation":
            if "Saturn" in h2_occ and "Rahu" in h2_occ:
                is_active = True
                trig_pos = ["Saturn and Rahu conjoined in 2nd House"]
                planets_inv = ["Saturn", "Rahu"]
                rel_houses = [2]

        elif r_id == "chatterjee_disease_free_benefic_6th":
            ben_in_6 = [p for p in h6_occ if p in ("Jupiter", "Venus", "Mercury")]
            mal_in_6 = [p for p in h6_occ if p in ("Mars", "Saturn", "Rahu", "Ketu", "Sun")]
            h_l6 = ctx.planet_house.get(l6_planet, 1)
            if ben_in_6 and not mal_in_6 and h_l6 in (1, 4, 7, 10):
                is_active = True
                trig_pos = [f"Benefic(s) {', '.join(ben_in_6)} in 6th without malefics; 6th lord {l6_planet} in Kendra {h_l6}"]
                planets_inv = ben_in_6 + [l6_planet]
                rel_houses = [6, h_l6]

        evaluated_golden_rules.append(
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
                is_active=is_active,
                status="Qualifying" if is_active else "Not Qualifying",
                triggered_positions=trig_pos,
                planets_involved=planets_inv,
                relevant_houses=rel_houses,
                conditions=[
                    MedicalConditionItem(
                        condition=c,
                        passed=is_active,
                        detail="; ".join(trig_pos) if is_active else "Conditions not met in current chart.",
                    )
                    for c in r_def.mandatory_conditions
                ],
            )
        )

    return DrChatterjeeCompendium(
        book_title="Advance Medical Astrology",
        book_title_ta="அட்வான்ஸ் மருத்துவ ஜோதிடம்",
        author="Dr. S. S. Chatterjee, Ph.D. (BHU), Ex-Executive Engineer PDIL, Recipient of Shri Santhanam Award",
        publisher="Rave Publication, Sumerpur",
        salient_features=[
            "Scientific & Electro-chemical correlation with classical Vedic and Ayurvedic medical astrology principles",
            "Signature mathematical Death Point formula: (Ascendant + Sun + Moon + Jupiter) % 360 with transit Saturn drishti triggers",
            "Sapta Dhatus (7 bodily tissues) ruled by 7 physical planets",
            "Detailed endocrine gland planetary governance matrix",
            "Anatomical Tridosha (Vata, Pitta, Kapha) diagnosis and site mapping",
            "Exhaustive Diabetes Mellitus (Madhumeha) biochemical analysis, symptoms, and empirical natural dietetic remedies",
            "10 Modern complex 21st-century illnesses (Hepatitis C, Lupus, Celiac, Vertigo, etc.) with planetary markers",
            "Natural therapies: Planetary colour therapy, metal-charged waters (Copper, Silver, Gold, Iron), and Vega Dharana natural urges",
            "Comprehensive clinical research backed by over 100 practical horoscopes from author's research diary",
        ],
        death_point=death_point_calc,
        parijata_longevity_eval=parijata_eval,
        sapta_dhatus=sapta_dhatus,
        endocrine_glands=endocrine_glands,
        tridosha_sites=tridosha_sites,
        diabetes_assessment=diabetes_assessment,
        modern_diseases=modern_diseases,
        natural_remedies=natural_remedies,
        golden_rules=evaluated_golden_rules,
        case_studies=CHATTERJEE_CASE_STUDIES,
    )




def _evaluate_max_heindel_compendium(
    ctx: YogaChartContext,
    horoscope: Any,
) -> MaxHeindelCompendium:
    """Evaluates Max Heindel and Augusta Foss Heindel Astro-Diagnosis and Classical Western Medical Astrology."""
    lagna_sign = ctx.lagna_sign_idx  # 1-12
    sun_sign = ctx.planet_sign.get("Sun", 1)
    moon_sign = ctx.planet_sign.get("Moon", 1)

    # 1. 12 Signs Anatomy & Pathology
    signs_anatomy: List[HeindelSignAnatomy] = []
    for s in HEINDEL_SIGNS_ANATOMY:
        s_idx = s["sign_index"]
        signs_anatomy.append(
            HeindelSignAnatomy(
                sign_index=s_idx,
                sign_name_en=s["sign_name_en"],
                sign_name_ta=s["sign_name_ta"],
                manilius_rulership=s["manilius_rulership"],
                heindel_anatomical_systems=s["heindel_anatomical_systems"],
                pathological_qualities=s["pathological_qualities"],
                physiological_afflictions=s["physiological_afflictions"],
                temperament_and_healing_reaction=s["temperament_and_healing_reaction"],
                is_native_ascendant=(s_idx == lagna_sign),
                is_native_sun_sign=(s_idx == sun_sign),
                is_native_moon_sign=(s_idx == moon_sign),
            )
        )

    # 2. Planetary Physiology & Chart Status
    planets_physiology: List[HeindelPlanetPhysiology] = []
    for p in HEINDEL_PLANETS_PHYSIOLOGY:
        p_name = p["planet"]
        p_sign = ctx.planet_sign.get(p_name)
        p_h = ctx.planet_house.get(p_name)
        status = "Balanced"
        if p_sign is not None and p_h is not None:
            if p_h in (6, 8, 12):
                status = f"In House {p_h} (Dusthana/Sensitive)"
            elif p_sign in (1, 5, 9):
                status = f"In Fire Sign {SIGN_NAMES_EN.get(p_sign, '')}"
            elif p_sign in (2, 6, 10):
                status = f"In Earth Sign {SIGN_NAMES_EN.get(p_sign, '')}"
            elif p_sign in (3, 7, 11):
                status = f"In Air Sign {SIGN_NAMES_EN.get(p_sign, '')}"
            else:
                status = f"In Water Sign {SIGN_NAMES_EN.get(p_sign, '')}"

            if p_name in ("Saturn", "Mars") and p_h in (1, 6, 8):
                status += " (Active Constitutional Afflicter)"
        planets_physiology.append(
            HeindelPlanetPhysiology(
                planet=p["planet"],
                planet_ta=p["planet_ta"],
                salient_keyword=p["salient_keyword"],
                anatomical_rulership=p["anatomical_rulership"],
                pathological_quality=p["pathological_quality"],
                positive_expression=p["positive_expression"],
                afflicted_expression=p["afflicted_expression"],
                chart_status=status,
            )
        )

    # 3. Three Vicious Circles
    vicious_circles: List[HeindelViciousCircle] = []
    cardinal_signs = {1, 4, 7, 10}
    fixed_signs = {2, 5, 8, 11}
    mutable_signs = {3, 6, 9, 12}

    for vc in HEINDEL_VICIOUS_CIRCLES:
        c_name = vc["cross_name"]
        if "Cardinal" in c_name:
            is_active = lagna_sign in cardinal_signs
            planets_in_cross = [p for p, s in ctx.planet_sign.items() if s in cardinal_signs]
            planets_str = ", ".join(planets_in_cross) if planets_in_cross else "None"
            notes = f"Native's Lagna ({SIGN_NAMES_EN.get(lagna_sign, '')}) is in this Cross. Key planets: {planets_str}."
        elif "Fixed" in c_name:
            is_active = lagna_sign in fixed_signs
            planets_in_cross = [p for p, s in ctx.planet_sign.items() if s in fixed_signs]
            planets_str = ", ".join(planets_in_cross) if planets_in_cross else "None"
            notes = f"Native's Lagna ({SIGN_NAMES_EN.get(lagna_sign, '')}) is in this Cross. Key planets: {planets_str}."
        else:
            is_active = lagna_sign in mutable_signs
            planets_in_cross = [p for p, s in ctx.planet_sign.items() if s in mutable_signs]
            planets_str = ", ".join(planets_in_cross) if planets_in_cross else "None"
            notes = f"Native's Lagna ({SIGN_NAMES_EN.get(lagna_sign, '')}) is in this Cross. Key planets: {planets_str}."

        vicious_circles.append(
            HeindelViciousCircle(
                cross_name=vc["cross_name"],
                cross_name_ta=vc["cross_name_ta"],
                signs_involved=vc["signs_involved"],
                organ_sympathies=vc["organ_sympathies"],
                clinical_mechanism=vc["clinical_mechanism"],
                clinical_examples=vc["clinical_examples"],
                is_native_cross_active=is_active,
                chart_notes=notes,
            )
        )

    # 4. Nail Diagnosis
    nail_and_hand_diagnosis: List[HeindelNailDiagnosis] = []
    for nd in HEINDEL_NAIL_DIAGNOSIS_DATA:
        nail_and_hand_diagnosis.append(
            HeindelNailDiagnosis(
                nail_type_en=nd["nail_type_en"],
                nail_type_ta=nd["nail_type_ta"],
                physical_indicators=nd["physical_indicators"],
                pathological_significance=nd["pathological_significance"],
                constitutional_correlation=nd["constitutional_correlation"],
                remedial_and_hygiene_guidance=nd["remedial_and_hygiene_guidance"],
            )
        )

    # 5. Planetary Antidotes
    planetary_antidotes: List[HeindelPlanetaryAntidote] = []
    for pa in HEINDEL_PLANETARY_ANTIDOTES:
        planetary_antidotes.append(
            HeindelPlanetaryAntidote(
                afflicting_planet=pa["afflicting_planet"],
                afflicting_metal=pa["afflicting_metal"],
                antidote_planet=pa["antidote_planet"],
                antidote_metal=pa["antidote_metal"],
                antidote_gem=pa["antidote_gem"],
                antidote_color=pa["antidote_color"],
                polarity_law=pa["polarity_law"],
                practical_application=pa["practical_application"],
            )
        )

    # 6. Nebular Spots
    nebular_spots: List[HeindelNebularSpot] = []
    planets_list = getattr(horoscope, "planets", [])

    for ns in HEINDEL_NEBULAR_SPOTS:
        name = ns["name"]
        prox = False
        details = "No natal planets conjoined this nebular spot."
        conjoined_planets = []
        for pl in planets_list:
            p_name = getattr(pl, "name", "")
            p_sign = getattr(pl, "sign", "")
            p_deg = getattr(pl, "degree", 0.0)
            if name == "Pleiades" and ("Taurus" in p_sign or "Rishaba" in p_sign) and p_deg >= 26.0:
                conjoined_planets.append(f"{p_name} ({p_deg:.1f}° Taurus)")
            elif name == "Ascelli" and ("Leo" in p_sign or "Simha" in p_sign) and 3.0 <= p_deg <= 9.0:
                conjoined_planets.append(f"{p_name} ({p_deg:.1f}° Leo)")
            elif name == "Antares" and ("Sagittarius" in p_sign or "Dhanus" in p_sign) and 5.0 <= p_deg <= 11.0:
                conjoined_planets.append(f"{p_name} ({p_deg:.1f}° Sagittarius)")

        if conjoined_planets:
            prox = True
            details = f"Natal presence within orb: {', '.join(conjoined_planets)}. Ocular awareness advised."

        nebular_spots.append(
            HeindelNebularSpot(
                name=ns["name"],
                zodiac_degree=ns["zodiac_degree"],
                pathological_focus=ns["pathological_focus"],
                esoteric_mitigation=ns["esoteric_mitigation"],
                native_chart_proximity=prox,
                chart_details=details,
            )
        )

    # 7. 43 Golden Aphorisms
    aphorisms: List[HeindelAphorism] = []
    for a in HEINDEL_APHORISMS_LIST:
        aphorisms.append(
            HeindelAphorism(
                number=a["number"],
                category=a["category"],
                aphorism_en=a["aphorism_en"],
                aphorism_ta=a["aphorism_ta"],
                practical_implication=a["practical_implication"],
            )
        )

    # 8. Evaluate Heindel Rules
    matched_rules: List[MedicalRule] = []
    sat_sign = ctx.planet_sign.get("Saturn", 1)
    sat_h = ctx.planet_house.get("Saturn", 1)
    sun_h = ctx.planet_house.get("Sun", 1)
    mars_h = ctx.planet_house.get("Mars", 1)
    mars_sign = ctx.planet_sign.get("Mars", 1)
    merc_h = ctx.planet_house.get("Mercury", 1)
    merc_sign = ctx.planet_sign.get("Mercury", 1)
    ven_sign = ctx.planet_sign.get("Venus", 1)

    for r_id, r_def in HEINDEL_RULES_REGISTRY.items():
        is_active = False
        trig_pos: List[str] = []
        planets_inv: List[str] = []
        rel_houses: List[int] = []
        cond_items: List[MedicalConditionItem] = []

        if r_id == "heindel_saturn_in_cancer":
            if sat_sign == 4:
                is_active = True
                trig_pos = [f"Saturn posited in Cancer (4th sign / Sign of Fall) in House {sat_h}"]
                planets_inv = ["Saturn"]
                rel_houses = [sat_h, 4]
            cond_items.append(MedicalConditionItem(condition="Saturn in Cancer", passed=sat_sign == 4, detail=f"Saturn in Sign {sat_sign}"))

        elif r_id == "heindel_saturn_in_6th":
            if sat_h == 6:
                is_active = True
                trig_pos = ["Saturn posited in the 6th House of Sickness"]
                planets_inv = ["Saturn"]
                rel_houses = [6]
            cond_items.append(MedicalConditionItem(condition="Saturn in 6th House", passed=sat_h == 6, detail=f"Saturn in House {sat_h}"))

        elif r_id == "heindel_sun_in_6th":
            if sun_h == 6:
                is_active = True
                trig_pos = ["Sun posited in the 6th House of Sickness"]
                planets_inv = ["Sun"]
                rel_houses = [6]
            cond_items.append(MedicalConditionItem(condition="Sun in 6th House", passed=sun_h == 6, detail=f"Sun in House {sun_h}"))

        elif r_id == "heindel_sun_in_8th":
            if sun_h == 8:
                is_active = True
                trig_pos = ["Sun posited in the 8th House of Crisis & Death-Dealing Forces"]
                planets_inv = ["Sun"]
                rel_houses = [8]
            cond_items.append(MedicalConditionItem(condition="Sun in 8th House", passed=sun_h == 8, detail=f"Sun in House {sun_h}"))

        elif r_id == "heindel_sun_mars_fiery_fever":
            has_sun_mars = (sun_h == mars_h) or (abs(sun_h - mars_h) in (4, 8)) or (mars_sign in (1, 5) and sun_h in (1, 5, 9))
            if has_sun_mars:
                is_active = True
                trig_pos = [f"Sun in House {sun_h} and Mars in House {mars_h} (fiery connection)"]
                planets_inv = ["Sun", "Mars"]
                rel_houses = [sun_h, mars_h]
            cond_items.append(MedicalConditionItem(condition="Sun-Mars fiery connection", passed=has_sun_mars, detail=f"Sun H{sun_h}, Mars H{mars_h}"))

        elif r_id == "heindel_mercury_saturn_melancholy":
            has_merc_sat = (merc_h == sat_h) or (abs(merc_h - sat_h) == 6) or (abs(merc_h - sat_h) in (3, 9))
            if has_merc_sat:
                is_active = True
                trig_pos = [f"Mercury (H{merc_h}) afflicted by Saturn (H{sat_h})"]
                planets_inv = ["Mercury", "Saturn"]
                rel_houses = [merc_h, sat_h]
            cond_items.append(MedicalConditionItem(condition="Mercury-Saturn aspect", passed=has_merc_sat, detail=f"Mercury H{merc_h}, Saturn H{sat_h}"))

        elif r_id == "heindel_venus_scorpio_fall":
            if ven_sign == 8:
                is_active = True
                trig_pos = [f"Venus in Scorpio (8th sign) in House {ctx.planet_house.get('Venus', 1)}"]
                planets_inv = ["Venus"]
                rel_houses = [ctx.planet_house.get("Venus", 1)]
            cond_items.append(MedicalConditionItem(condition="Venus in Scorpio", passed=ven_sign == 8, detail=f"Venus in Sign {ven_sign}"))

        elif r_id == "heindel_saturn_gemini_sagittarius_lungs":
            if sat_sign in (3, 9) and (abs(sat_h - sun_h) in (0, 6, 3, 9)):
                is_active = True
                trig_pos = [f"Saturn in {SIGN_NAMES_EN.get(sat_sign, '')} aspecting Sun (H{sun_h})"]
                planets_inv = ["Saturn", "Sun"]
                rel_houses = [sat_h, sun_h]
            cond_items.append(MedicalConditionItem(condition="Saturn in Gemini/Sagittarius aspecting Sun", passed=sat_sign in (3, 9), detail=f"Saturn in Sign {sat_sign}"))

        elif r_id == "heindel_mercury_12th_hearing":
            if merc_h == 12 or (merc_sign == 10 and any(m in ctx.house_occupants.get(merc_h, []) for m in ("Saturn", "Mars", "Rahu"))):
                is_active = True
                trig_pos = [f"Mercury in House {merc_h} in Sign {merc_sign}"]
                planets_inv = ["Mercury"]
                rel_houses = [merc_h]
            cond_items.append(MedicalConditionItem(condition="Mercury in 12th or Capricorn afflicted", passed=merc_h == 12 or merc_sign == 10, detail=f"Mercury H{merc_h}, S{merc_sign}"))

        elif r_id == "heindel_common_signs_angular_vitality":
            if lagna_sign in (3, 6, 9, 12):
                is_active = True
                trig_pos = [f"Ascendant in {SIGN_NAMES_EN.get(lagna_sign, '')} (Common Sign) places Common signs on all 4 angles"]
                planets_inv = []
                rel_houses = [1, 4, 7, 10]
            cond_items.append(MedicalConditionItem(condition="Common signs on the 4 angles", passed=lagna_sign in (3, 6, 9, 12), detail=f"Lagna in Sign {lagna_sign}"))

        elif r_id == "heindel_fixed_signs_angles_resilience":
            if lagna_sign in (2, 5, 8, 11):
                is_active = True
                trig_pos = [f"Ascendant in {SIGN_NAMES_EN.get(lagna_sign, '')} (Fixed Sign) places Fixed signs on all 4 angles"]
                planets_inv = []
                rel_houses = [1, 4, 7, 10]
            cond_items.append(MedicalConditionItem(condition="Fixed signs on the 4 angles", passed=lagna_sign in (2, 5, 8, 11), detail=f"Lagna in Sign {lagna_sign}"))

        matched_rules.append(
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
                is_active=is_active,
                status="Qualifying" if is_active else "Not Qualifying",
                triggered_positions=trig_pos,
                planets_involved=planets_inv,
                relevant_houses=rel_houses,
                conditions=cond_items,
                remedy_en=r_def.remedy_en,
                remedy_ta=r_def.remedy_ta,
            )
        )

    chart_eval = {
        "lagna_sign": SIGN_NAMES_EN.get(lagna_sign, ""),
        "lagna_sign_ta": SIGN_NAMES_TA.get(lagna_sign, ""),
        "sun_sign": SIGN_NAMES_EN.get(sun_sign, ""),
        "sun_sign_ta": SIGN_NAMES_TA.get(sun_sign, ""),
        "moon_sign": SIGN_NAMES_EN.get(moon_sign, ""),
        "moon_sign_ta": SIGN_NAMES_TA.get(moon_sign, ""),
        "active_rules_count": len([r for r in matched_rules if r.is_active]),
    }

    return MaxHeindelCompendium(
        book_title=MAX_HEINDEL_METADATA["book_title"],
        book_title_ta=MAX_HEINDEL_METADATA["book_title_ta"],
        authors=MAX_HEINDEL_METADATA["authors"],
        historical_foundation=MAX_HEINDEL_METADATA["historical_foundation"],
        core_philosophy_en=MAX_HEINDEL_METADATA["core_philosophy_en"],
        core_philosophy_ta=MAX_HEINDEL_METADATA["core_philosophy_ta"],
        healer_injunctions=MAX_HEINDEL_METADATA["healer_injunctions"],
        signs_anatomy=signs_anatomy,
        planets_physiology=planets_physiology,
        sense_organs_affinities=HEINDEL_SENSE_ORGANS,
        vicious_circles=vicious_circles,
        nail_and_hand_diagnosis=nail_and_hand_diagnosis,
        planetary_antidotes=planetary_antidotes,
        nebular_spots=nebular_spots,
        aphorisms=aphorisms,
        chart_evaluation=chart_eval,
        matched_rules=matched_rules,
    )


def _evaluate_jane_ridder_patrick_compendium(
    ctx: YogaChartContext,
    horoscope: Any,
    live_transits: Optional[Any] = None,
) -> JaneRidderPatrickCompendium:
    """Evaluates Jane Ridder-Patrick's A Handbook of Medical Astrology compendium.
    
    Includes:
    1. The Astrological Alphabet Framework (WHAT, WHERE, HOW, WHICH, WHEN)
    2. The Three Crosses (Cardinal Regulation, Fixed Vital Functions, Mutable Metabolism)
    3. Decumbiture diagnostics: Strictures on Judgement, Hours, Direction/Sidedness, Critical Days
    4. Exact calculated Arabian Parts: Part of Sickness, Part of Surgery, Part of Death
    5. Elemental balance (Ayurvedic/Western) and Materia Medica balancing diets/herbs
    6. 12 Biochemic Cell Salts (Carey & Perry), Bach Flowers (Peter Damian), and Meridians (Ebertin)
    7. Nicholas Culpeper's 7 Rules for Astrological Therapeutics
    8. 3 Stages of Astrological Therapy (Identification, Exploration, Upgrading)
    9. Chart-matched clinical rules from Jane Ridder-Patrick's registry
    """
    planets = getattr(horoscope, "planets", [])
    ascendant = getattr(horoscope, "ascendant", None)
    houses_list = getattr(horoscope, "houses", [])

    asc_long = float(getattr(ascendant, "longitude", 0.0)) if ascendant else 0.0
    asc_deg = asc_long % 30.0
    asc_sign_idx = ctx.ascendant_sign_idx
    lagna_lord = ctx.house_lords.get(1, "Mars")

    # 1. Decumbiture Strictures & Planetary Hours Evaluation
    is_asc_early_or_late = (asc_deg < 3.0) or (asc_deg > 27.0)
    if asc_deg < 3.0:
        asc_stricture_note = (
            f"Ascendant is at {asc_deg:.2f}° (< 3°): According to William Lilly and Jane Ridder-Patrick, "
            "this indicates the condition is in its formative embryonic stage or premature for definitive horary resolution."
        )
    elif asc_deg > 27.0:
        asc_stricture_note = (
            f"Ascendant is at {asc_deg:.2f}° (> 27°): The condition is chronic, deeply entrenched, or past its decisive turning point."
        )
    else:
        asc_stricture_note = f"Ascendant is at {asc_deg:.2f}° (within 3°–27° safe zone), fully radical for diagnostic evaluation."

    planet_longs: Dict[str, float] = {}
    for p in planets:
        p_name = getattr(p, "name", "")
        p_l = float(getattr(p, "longitude", 0.0))
        planet_longs[p_name] = p_l

    moon_long = planet_longs.get("Moon", 0.0)
    sun_long = planet_longs.get("Sun", 0.0)
    mars_long = planet_longs.get("Mars", 0.0)
    sat_long = planet_longs.get("Saturn", 0.0)
    merc_long = planet_longs.get("Mercury", 0.0)
    ven_long = planet_longs.get("Venus", 0.0)
    jup_long = planet_longs.get("Jupiter", 0.0)
    uranus_long = planet_longs.get("Uranus", 0.0)
    neptune_long = planet_longs.get("Neptune", 0.0)
    pluto_long = planet_longs.get("Pluto", 0.0)

    # Moon in Via Combusta: 15° Libra (195°) to 15° Scorpio (225°)
    moon_in_via_combusta = (195.0 <= moon_long <= 225.0)

    # Moon Void of Course
    moon_deg_in_sign = moon_long % 30.0
    moon_void_of_course = (moon_deg_in_sign >= 28.0)

    # Saturn in 7th
    sat_h = ctx.planet_house.get("Saturn", 1)
    saturn_in_seventh = (sat_h == 7)

    # 7th house afflicted or 7th lord Rx/weak
    h7_occ = ctx.house_occupants.get(7, [])
    seventh_house_afflicted = any(m in h7_occ for m in ["Saturn", "Mars", "Rahu", "Ketu"]) or (ctx.planet_house.get(ctx.house_lords.get(7, "Venus"), 1) in (6, 8, 12))

    # Asc lord combust or Saturn in 1st
    lagna_lord_long = planet_longs.get(lagna_lord, 0.0)
    combust_dist = min((lagna_lord_long - sun_long) % 360, (sun_long - lagna_lord_long) % 360)
    asc_lord_combust_or_saturn_in_first = (sat_h == 1) or (combust_dist < 8.5 and lagna_lord != "Sun")

    critical_days_en = (
        "Acute illness critical days: Transiting Moon at 45°, 90°, 135°, and 180° from decumbiture Moon. "
        "Indicative checkpoints occur at 22.5° intervals. For chronic conditions, transiting Sun is observed at 45°, 90°, 135°, and 180°."
    )
    critical_days_ta = (
        "கடுமையான நோய்க்கான திருப்புமுனை நாட்கள்: சந்திரன் 45°, 90°, 135°, 180° கோணங்களை அடையும் போது. "
        "நாள்பட்ட நோய்களுக்கு சூரியனின் 45°, 90°, 135°, 180° சுழற்சி திருப்புமுனையாகும்."
    )

    # Sidedness & Direction
    l6_planet = ctx.house_lords.get(6, "Mercury")
    l6_h = ctx.planet_house.get(l6_planet, 6)
    l6_sign = ctx.planet_sign.get(l6_planet, 6)
    is_masculine_sign = (l6_sign % 2 == 1)
    is_above_earth = (l6_h in (7, 8, 9, 10, 11, 12))
    if is_masculine_sign or is_above_earth:
        sidedness = "Right side / Front of the body (Masculine / Diurnal influence)"
    else:
        sidedness = "Left side / Back of the body (Feminine / Nocturnal influence)"

    decumbiture_eval = JaneDecumbitureEvaluation(
        ascendant_degree=round(asc_deg, 2),
        is_asc_early_or_late=is_asc_early_or_late,
        asc_stricture_note=asc_stricture_note,
        moon_in_via_combusta=moon_in_via_combusta,
        moon_void_of_course=moon_void_of_course,
        saturn_in_seventh=saturn_in_seventh,
        seventh_house_afflicted=seventh_house_afflicted,
        asc_lord_combust_or_saturn_in_first=asc_lord_combust_or_saturn_in_first,
        critical_days_cycle_en=critical_days_en,
        critical_days_cycle_ta=critical_days_ta,
        sidedness_indicator=sidedness,
    )

    # 2. Arabian Parts (Chapter 5, p. 151)
    part_sickness_deg = (asc_long + mars_long - sat_long) % 360.0
    sickness_sign_idx = int(part_sickness_deg // 30) + 1
    sickness_deg_in_sign = part_sickness_deg % 30.0
    sickness_sign_name = SIGN_NAMES_EN.get(sickness_sign_idx, "Aries")
    sickness_coord = f"{int(sickness_deg_in_sign)}°{int((sickness_deg_in_sign % 1) * 60):02d}' {sickness_sign_name}"

    part_surgery_deg = (asc_long + sat_long - mars_long) % 360.0
    surgery_sign_idx = int(part_surgery_deg // 30) + 1
    surgery_deg_in_sign = part_surgery_deg % 30.0
    surgery_sign_name = SIGN_NAMES_EN.get(surgery_sign_idx, "Aries")
    surgery_coord = f"{int(surgery_deg_in_sign)}°{int((surgery_deg_in_sign % 1) * 60):02d}' {surgery_sign_name}"

    h8_cusp = (asc_long + 210.0) % 360.0
    if len(houses_list) >= 8:
        try:
            h8_cusp = float(getattr(houses_list[7], "longitude", h8_cusp))
        except Exception:
            pass
    part_death_deg = (asc_long + h8_cusp - moon_long) % 360.0
    death_sign_idx = int(part_death_deg // 30) + 1
    death_deg_in_sign = part_death_deg % 30.0
    death_sign_name = SIGN_NAMES_EN.get(death_sign_idx, "Aries")
    death_coord = f"{int(death_deg_in_sign)}°{int((death_deg_in_sign % 1) * 60):02d}' {death_sign_name}"

    clinical_notes_en = (
        f"Arabian Parts are sensitive trigger points activated by transits, lunations, and eclipses. "
        f"Part of Sickness at {sickness_coord} reveals primary somatic vulnerability; "
        f"Part of Surgery at {surgery_coord} highlights surgical timing sensitivity; "
        f"Part of Death at {death_coord} marks the critical threshold of vital release and transformative renewal."
    )
    clinical_notes_ta = (
        f"அரேபியப் பாகைகள் கிரகப் பெயர்ச்சிகள், அமாவாசை/பௌர்ணமி மற்றும் கிரகணங்களால் தூண்டப்படும் உணர்வு புள்ளிகள் ஆகும். "
        f"நோய் பாகை ({sickness_coord}): உடலின் பிரதான பலவீனப் புள்ளி; "
        f"அறுவை சிகிச்சை பாகை ({surgery_coord}): அறுவை சிகிச்சைக்கான எச்சரிக்கைப் புள்ளி; "
        f"ஆயுள் நிறைவு பாகை ({death_coord}): தீவிர மாற்றத்திற்கான திருப்புமுனைப் புள்ளி."
    )

    arabian_parts = JaneArabianParts(
        part_of_sickness_deg=round(part_sickness_deg, 2),
        part_of_sickness_sign=sickness_sign_name,
        part_of_sickness_coord=sickness_coord,
        part_of_surgery_deg=round(part_surgery_deg, 2),
        part_of_surgery_sign=surgery_sign_name,
        part_of_surgery_coord=surgery_coord,
        part_of_death_deg=round(part_death_deg, 2),
        part_of_death_sign=death_sign_name,
        part_of_death_coord=death_coord,
        clinical_notes_en=clinical_notes_en,
        clinical_notes_ta=clinical_notes_ta,
    )

    # 3. Elemental Balance Analysis
    air_signs = {3, 7, 11}
    fire_signs = {1, 5, 9}
    water_signs = {4, 8, 12}
    earth_signs = {2, 6, 10}

    air_count = sum(1 for p, s in ctx.planet_sign.items() if s in air_signs)
    fire_count = sum(1 for p, s in ctx.planet_sign.items() if s in fire_signs)
    water_count = sum(1 for p, s in ctx.planet_sign.items() if s in water_signs)
    earth_count = sum(1 for p, s in ctx.planet_sign.items() if s in earth_signs)

    moon_s = ctx.planet_sign.get("Moon", 1)
    if moon_s in air_signs:
        moon_elem = "Air"
    elif moon_s in fire_signs:
        moon_elem = "Fire"
    elif moon_s in water_signs:
        moon_elem = "Water"
    else:
        moon_elem = "Earth"

    counts = {"Air": air_count, "Fire": fire_count, "Water": water_count, "Earth": earth_count}
    dominant_elem = max(counts, key=counts.get)
    deficient_elem = min(counts, key=counts.get)

    diet_key = f"Excess {dominant_elem}" if counts[dominant_elem] >= 4 else f"Low {deficient_elem}"
    diet_info = JANE_ELEMENTAL_BALANCING.get(diet_key, JANE_ELEMENTAL_BALANCING.get("Excess Air", {}))

    diet_en = f"Constitutional Temperament: {dominant_elem} dominant ({counts[dominant_elem]} planets), {deficient_elem} deficient ({counts[deficient_elem]} planets). Natal Moon in {moon_elem}. Recommended balancing diet: {diet_info.get('balancing_diet', '')} Avoid: {diet_info.get('avoid', '')}"
    diet_ta = f"பூத தத்துவம்: {dominant_elem} ஆதிக்கம் ({counts[dominant_elem]} கிரகங்கள்), {deficient_elem} குறைவு ({counts[deficient_elem]} கிரகங்கள்). சந்திரன் {moon_elem}-ல் உள்ளார். சமநிலைப்படுத்தும் உணவு முறை: {diet_info.get('balancing_diet', '')} தவிர்க்க வேண்டியவை: {diet_info.get('avoid', '')}"

    herbs_str = diet_info.get("indicated_herbs", "")
    indicated_herbal_classes = [h.strip() for h in herbs_str.split(",") if h.strip()]

    elemental_analysis = JaneElementalAnalysis(
        air_count=air_count,
        fire_count=fire_count,
        water_count=water_count,
        earth_count=earth_count,
        moon_element=moon_elem,
        dominant_element=dominant_elem,
        deficient_element=deficient_elem,
        dietary_balancing_en=diet_en,
        dietary_balancing_ta=diet_ta,
        herbal_classes_indicated=indicated_herbal_classes,
    )

    # 4. Cell Salts (Carey & Perry)
    cell_salts: List[JaneCellSaltCorrespondence] = []
    sun_s = ctx.planet_sign.get("Sun", 1)
    for cs in JANE_CELL_SALTS:
        sign_idx = list(SIGN_NAMES_EN.values()).index(cs["sign"]) + 1 if cs["sign"] in SIGN_NAMES_EN.values() else 1
        is_native = (sign_idx in (asc_sign_idx, moon_s, sun_s))
        cell_salts.append(
            JaneCellSaltCorrespondence(
                sign=cs["sign"],
                sign_ta=cs["sign_ta"],
                cell_salt=cs["cell_salt"],
                abbreviation=cs["abbreviation"],
                physiological_action_en=cs["action_en"],
                physiological_action_ta=cs["action_ta"],
                is_native_sign=is_native,
            )
        )

    # 5. Bach Flowers (Peter Damian)
    bach_flowers: List[JaneBachFlowerCorrespondence] = []
    for bf in JANE_BACH_FLOWERS:
        sign_idx = list(SIGN_NAMES_EN.values()).index(bf["sign"]) + 1 if bf["sign"] in SIGN_NAMES_EN.values() else 1
        is_native = (sign_idx in (asc_sign_idx, moon_s, sun_s))
        bach_flowers.append(
            JaneBachFlowerCorrespondence(
                sign=bf["sign"],
                sign_ta=bf["sign_ta"],
                flower_remedy=bf["flower"],
                emotional_archetype_en=bf["action_en"],
                emotional_archetype_ta=bf["action_ta"],
                is_native_sign=is_native,
            )
        )

    # 6. Acupuncture Meridians (Ebertin)
    acupuncture_meridians: List[JaneAcupunctureMeridian] = []
    for am in JANE_ACUPUNCTURE_MERIDIANS:
        sign_idx = list(SIGN_NAMES_EN.values()).index(am["sign"]) + 1 if am["sign"] in SIGN_NAMES_EN.values() else 1
        is_native = (sign_idx in (asc_sign_idx, moon_s, sun_s))
        acupuncture_meridians.append(
            JaneAcupunctureMeridian(
                sign=am["sign"],
                sign_ta=am["sign_ta"],
                meridian=am["meridian"],
                meridian_ta=am["meridian_ta"],
                is_native_sign=is_native,
            )
        )

    # 7. Evaluate Chart-Matched Rules
    matched_rules: List[MedicalRule] = []

    def _is_hard_aspect(deg1: float, deg2: float) -> Tuple[bool, str]:
        diff = abs(deg1 - deg2) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
        if diff <= 9.0:
            return True, f"Conjunction ({diff:.1f}° orb)"
        if 82.0 <= diff <= 98.0:
            return True, f"Square ({diff:.1f}°)"
        if 171.0 <= diff <= 180.0:
            return True, f"Opposition ({diff:.1f}°)"
        return False, ""

    def _is_trine_aspect(deg1: float, deg2: float) -> Tuple[bool, str]:
        diff = abs(deg1 - deg2) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
        if 112.0 <= diff <= 128.0:
            return True, f"Trine ({diff:.1f}°)"
        return False, ""

    for r_id, r_def in JANE_RIDDER_PATRICK_RULES_REGISTRY.items():
        is_active = False
        trig_pos: List[str] = []
        planets_inv: List[str] = []
        rel_houses: List[int] = []

        if r_id == "jrp_sun_saturn":
            has_asp, desc = _is_hard_aspect(sun_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Sun at {sun_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Sun", "Saturn"]
                rel_houses = [ctx.planet_house.get("Sun", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_sun_mars":
            has_asp, desc = _is_hard_aspect(sun_long, mars_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Sun at {sun_long:.1f}° and Mars at {mars_long:.1f}°: {desc}")
                planets_inv = ["Sun", "Mars"]
                rel_houses = [ctx.planet_house.get("Sun", 1), ctx.planet_house.get("Mars", 1)]

        elif r_id == "jrp_sun_neptune":
            has_asp, desc = _is_hard_aspect(sun_long, neptune_long)
            if has_asp and neptune_long > 0:
                is_active = True
                trig_pos.append(f"Sun at {sun_long:.1f}° and Neptune at {neptune_long:.1f}°: {desc}")
                planets_inv = ["Sun", "Neptune"]
                rel_houses = [ctx.planet_house.get("Sun", 1)]

        elif r_id == "jrp_sun_uranus":
            has_asp, desc = _is_hard_aspect(sun_long, uranus_long)
            if has_asp and uranus_long > 0:
                is_active = True
                trig_pos.append(f"Sun at {sun_long:.1f}° and Uranus at {uranus_long:.1f}°: {desc}")
                planets_inv = ["Sun", "Uranus"]
                rel_houses = [ctx.planet_house.get("Sun", 1)]

        elif r_id == "jrp_sun_pluto":
            has_asp, desc = _is_hard_aspect(sun_long, pluto_long)
            if has_asp and pluto_long > 0:
                is_active = True
                trig_pos.append(f"Sun at {sun_long:.1f}° and Pluto at {pluto_long:.1f}°: {desc}")
                planets_inv = ["Sun", "Pluto"]
                rel_houses = [ctx.planet_house.get("Sun", 1)]

        elif r_id == "jrp_moon_saturn":
            has_asp, desc = _is_hard_aspect(moon_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Moon at {moon_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Moon", "Saturn"]
                rel_houses = [ctx.planet_house.get("Moon", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_moon_neptune":
            has_hard, desc_h = _is_hard_aspect(moon_long, neptune_long)
            has_trine, desc_t = _is_trine_aspect(moon_long, neptune_long)
            if (has_hard or has_trine) and neptune_long > 0:
                is_active = True
                desc = desc_h if has_hard else desc_t
                trig_pos.append(f"Moon at {moon_long:.1f}° and Neptune at {neptune_long:.1f}°: {desc}")
                planets_inv = ["Moon", "Neptune"]
                rel_houses = [ctx.planet_house.get("Moon", 1)]

        elif r_id == "jrp_moon_mars":
            has_asp, desc = _is_hard_aspect(moon_long, mars_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Moon at {moon_long:.1f}° and Mars at {mars_long:.1f}°: {desc}")
                planets_inv = ["Moon", "Mars"]
                rel_houses = [ctx.planet_house.get("Moon", 1), ctx.planet_house.get("Mars", 1)]

        elif r_id == "jrp_moon_uranus":
            has_asp, desc = _is_hard_aspect(moon_long, uranus_long)
            if has_asp and uranus_long > 0:
                is_active = True
                trig_pos.append(f"Moon at {moon_long:.1f}° and Uranus at {uranus_long:.1f}°: {desc}")
                planets_inv = ["Moon", "Uranus"]
                rel_houses = [ctx.planet_house.get("Moon", 1)]

        elif r_id == "jrp_moon_pluto":
            has_asp, desc = _is_hard_aspect(moon_long, pluto_long)
            if has_asp and pluto_long > 0:
                is_active = True
                trig_pos.append(f"Moon at {moon_long:.1f}° and Pluto at {pluto_long:.1f}°: {desc}")
                planets_inv = ["Moon", "Pluto"]
                rel_houses = [ctx.planet_house.get("Moon", 1)]

        elif r_id == "jrp_mars_neptune":
            has_asp, desc = _is_hard_aspect(mars_long, neptune_long)
            if has_asp and neptune_long > 0:
                is_active = True
                trig_pos.append(f"Mars at {mars_long:.1f}° and Neptune at {neptune_long:.1f}°: {desc}")
                planets_inv = ["Mars", "Neptune"]
                rel_houses = [ctx.planet_house.get("Mars", 1)]

        elif r_id == "jrp_mars_saturn":
            has_asp, desc = _is_hard_aspect(mars_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Mars at {mars_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Mars", "Saturn"]
                rel_houses = [ctx.planet_house.get("Mars", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_mercury_mars":
            has_asp, desc = _is_hard_aspect(merc_long, mars_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Mercury at {merc_long:.1f}° and Mars at {mars_long:.1f}°: {desc}")
                planets_inv = ["Mercury", "Mars"]
                rel_houses = [ctx.planet_house.get("Mercury", 1), ctx.planet_house.get("Mars", 1)]

        elif r_id == "jrp_mercury_saturn":
            has_asp, desc = _is_hard_aspect(merc_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Mercury at {merc_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Mercury", "Saturn"]
                rel_houses = [ctx.planet_house.get("Mercury", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_venus_saturn":
            has_asp, desc = _is_hard_aspect(ven_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Venus at {ven_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Venus", "Saturn"]
                rel_houses = [ctx.planet_house.get("Venus", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_jupiter_saturn":
            has_asp, desc = _is_hard_aspect(jup_long, sat_long)
            if has_asp:
                is_active = True
                trig_pos.append(f"Jupiter at {jup_long:.1f}° and Saturn at {sat_long:.1f}°: {desc}")
                planets_inv = ["Jupiter", "Saturn"]
                rel_houses = [ctx.planet_house.get("Jupiter", 1), ctx.planet_house.get("Saturn", 1)]

        elif r_id == "jrp_jupiter_neptune":
            has_asp, desc = _is_hard_aspect(jup_long, neptune_long)
            if has_asp and neptune_long > 0:
                is_active = True
                trig_pos.append(f"Jupiter at {jup_long:.1f}° and Neptune at {neptune_long:.1f}°: {desc}")
                planets_inv = ["Jupiter", "Neptune"]
                rel_houses = [ctx.planet_house.get("Jupiter", 1)]

        elif r_id == "jrp_cardinal_cross_reflex":
            cardinal_pl = [p for p, s in ctx.planet_sign.items() if s in {1, 4, 7, 10}]
            if len(cardinal_pl) >= 3 or (asc_sign_idx in {1, 4, 7, 10} and len(cardinal_pl) >= 2):
                is_active = True
                trig_pos.append(f"Planets in Cardinal Cross (Aries, Cancer, Libra, Capricorn): {', '.join(cardinal_pl)}")
                planets_inv = cardinal_pl
                rel_houses = [1, 4, 7, 10]

        elif r_id == "jrp_fixed_cross_reflex":
            fixed_pl = [p for p, s in ctx.planet_sign.items() if s in {2, 5, 8, 11}]
            if len(fixed_pl) >= 3 or (asc_sign_idx in {2, 5, 8, 11} and len(fixed_pl) >= 2):
                is_active = True
                trig_pos.append(f"Planets in Fixed Cross (Taurus, Leo, Scorpio, Aquarius): {', '.join(fixed_pl)}")
                planets_inv = fixed_pl
                rel_houses = [2, 5, 8, 11]

        elif r_id == "jrp_mutable_cross_reflex":
            mutable_pl = [p for p, s in ctx.planet_sign.items() if s in {3, 6, 9, 12}]
            if len(mutable_pl) >= 3 or (asc_sign_idx in {3, 6, 9, 12} and len(mutable_pl) >= 2):
                is_active = True
                trig_pos.append(f"Planets in Mutable Cross (Gemini, Virgo, Sagittarius, Pisces): {', '.join(mutable_pl)}")
                planets_inv = mutable_pl
                rel_houses = [3, 6, 9, 12]

        elif r_id == "jrp_decumbiture_early_late_asc":
            if is_asc_early_or_late:
                is_active = True
                trig_pos.append(f"Ascendant at {asc_deg:.2f}° in {SIGN_NAMES_EN.get(asc_sign_idx, '')}")
                rel_houses = [1]

        elif r_id == "jrp_decumbiture_via_combusta":
            if moon_in_via_combusta:
                is_active = True
                trig_pos.append(f"Moon at {moon_long:.1f}° (between 15° Libra and 15° Scorpio)")
                planets_inv = ["Moon"]
                rel_houses = [ctx.planet_house.get("Moon", 1)]

        elif r_id == "jrp_decumbiture_void_moon":
            if moon_void_of_course:
                is_active = True
                trig_pos.append(f"Moon at {moon_deg_in_sign:.1f}° of {SIGN_NAMES_EN.get(moon_s, '')}")
                planets_inv = ["Moon"]
                rel_houses = [ctx.planet_house.get("Moon", 1)]

        elif r_id == "jrp_culpeper_ascendant_fortification":
            is_active = True
            trig_pos.append(f"Ascendant in {SIGN_NAMES_EN.get(asc_sign_idx, '')}, governed by Lord {lagna_lord}")
            planets_inv = [lagna_lord]
            rel_houses = [1]

        cond_items = [
            MedicalConditionItem(
                condition=c,
                passed=is_active,
                detail=f"Condition status: {'Fulfilled' if is_active else 'Not satisfied'} in native's chart",
            )
            for c in r_def.mandatory_conditions
        ]

        rule_obj = MedicalRule(
            id=r_def.id,
            name=r_def.name,
            name_tamil=r_def.name_tamil,
            source=r_def.source,
            chapter_verse=r_def.chapter_verse,
            category=r_def.category,
            system=r_def.system,
            required_placements=", ".join(r_def.required_placements) if isinstance(r_def.required_placements, list) else str(r_def.required_placements),
            mandatory_conditions=r_def.mandatory_conditions,
            traditional_interpretation=r_def.traditional_interpretation,
            interpretation_tamil=r_def.interpretation_tamil,
            anatomical_system=r_def.anatomical_system,
            modifiers=", ".join(r_def.modifiers) if isinstance(r_def.modifiers, list) else (str(r_def.modifiers) if r_def.modifiers else None),
            conflicting_indications=", ".join(r_def.conflicting_indications) if isinstance(r_def.conflicting_indications, list) else (str(r_def.conflicting_indications) if r_def.conflicting_indications else None),
            is_active=is_active,
            status="Qualifying" if is_active else "Not Qualifying",
            triggered_positions=trig_pos,
            planets_involved=planets_inv,
            relevant_houses=rel_houses,
            conditions=cond_items,
            remedy_en=r_def.remedy_en,
            remedy_ta=r_def.remedy_ta,
        )
        matched_rules.append(rule_obj)

    return JaneRidderPatrickCompendium(
        book_title=JANE_RIDDER_PATRICK_METADATA["book_title"],
        book_title_ta=JANE_RIDDER_PATRICK_METADATA["book_title_ta"],
        author=JANE_RIDDER_PATRICK_METADATA["author"],
        publisher=JANE_RIDDER_PATRICK_METADATA["publisher"],
        alphabet_framework=JANE_RIDDER_PATRICK_METADATA["alphabet_framework"],
        three_crosses=JANE_THREE_CROSSES,
        decumbiture=decumbiture_eval,
        arabian_parts=arabian_parts,
        elemental_analysis=elemental_analysis,
        culpeper_therapeutic_rules=CULPEPER_7_RULES,
        stages_of_therapy=[
            {"stage": "1. Identification", "stage_ta": "1. இனங்காணல்", "description_en": "Locate and define problem areas upstream in the psyche to produce a sparing effect downstream in the physical body.", "description_ta": "உடலில் தோன்றும் முன், மனதில் உள்ள அடிப்படை ஜோதிட ஆதிக்கங்களை இனங்கண்டு சரிசெய்தல்."},
            {"stage": "2. Exploration", "stage_ta": "2. ஆய்வு செய்தல்", "description_en": "Observe patterns without judgement. Keep a symptom journal, write personal belief statements, and trace transit triggers.", "description_ta": "சுய குற்ற உணர்ச்சியின்றி நடத்தைகளை கவனித்தல், நாட்குறிப்பு எழுதுதல், கிரகப் பெயர்ச்சிகளின் தாக்கத்தை உற்றுநோக்குதல்."},
            {"stage": "3. Upgrading", "stage_ta": "3. மேன்மைப்படுத்துதல்", "description_en": "Find constructive creative outlets for difficult planetary energies (e.g. Karate for Mars-Saturn, Dance for Venus-Mars, Altruism for Mars-Neptune).", "description_ta": "கடினமான கிரக ஆற்றல்களை நேர்மறையான ஆக்கப்பூர்வ வழிகளில் வெளிப்படுத்துதல் (எ.கா: செவ்வாய்-சனிக்கு தற்காப்புக் கலை, செவ்வாய்-நெப்டியூனுக்கு ஆன்மீக அறப்பணி)."}
        ],
        cell_salts=cell_salts,
        bach_flowers=bach_flowers,
        acupuncture_meridians=acupuncture_meridians,
        matched_rules=matched_rules,
    )




def _evaluate_heinrich_daath_compendium(
    ctx: YogaChartContext,
    horoscope: Any,
    dasa: Optional[Any] = None,
    live_transits: Optional[Any] = None,
) -> HeinrichDaathCompendium:
    asc_sign_idx = ctx.ascendant_sign_idx
    sun_s = ctx.planet_sign.get("Sun", 1)
    moon_s = ctx.planet_sign.get("Moon", 1)
    sixth_s = ((asc_sign_idx - 1 + 5) % 12) + 1

    # 1. 12 Sign Anatomical Rulerships
    signs_anatomy: List[DaathSignAnatomy] = []
    for s_data in DAATH_SIGNS_ANATOMY:
        idx = s_data["sign_index"]
        signs_anatomy.append(
            DaathSignAnatomy(
                sign_index=idx,
                sign_name_en=s_data["sign_name_en"],
                sign_name_ta=s_data["sign_name_ta"],
                symbolic_quality=s_data["symbolic_quality"],
                principal_bones=s_data["principal_bones"],
                muscles=s_data["muscles"],
                arteries=s_data["arteries"],
                veins=s_data["veins"],
                morbid_actions=s_data["morbid_actions"],
                kidney_pelvis_distinction=s_data["kidney_pelvis_distinction"],
                is_native_ascendant=(idx == asc_sign_idx),
                is_native_sun_sign=(idx == sun_s),
                is_native_moon_sign=(idx == moon_s),
                is_native_sixth_house=(idx == sixth_s),
            )
        )

    # 2. 9 Planets Biodynamics and Chart Status
    planets_biodynamics: List[DaathPlanetAction] = []
    sat_house = ctx.planet_house.get("Saturn", 1)
    mars_house = ctx.planet_house.get("Mars", 1)
    jup_sign = ctx.planet_sign.get("Jupiter", 1)
    mars_sign = ctx.planet_sign.get("Mars", 1)
    sun_house = ctx.planet_house.get("Sun", 1)

    for p_data in DAATH_PLANETS_BIODYNAMICS:
        p_name = p_data["planet"]
        chart_cond = "Normal / Balanced"
        p_info = None
        horo_planets = getattr(horoscope, "planets", []) if horoscope else []
        for pl in horo_planets:
            if getattr(pl, "name", "") == p_name:
                p_info = pl
                break

        is_rx = getattr(p_info, "is_retrograde", False) if p_info else False

        if p_name == "Mars":
            if mars_sign == 4:
                chart_cond = "Perverted / Atonic Heat (Fall in Cancer - Gastric Irritability)"
            elif ctx.planet_sign.get("Mars") in (1, 8):
                chart_cond = "Tonic / High Tension (Ruler in Own Sign)"
            elif is_rx:
                chart_cond = "Retrograde / Internalized Combustive Heat"
        elif p_name == "Saturn":
            if ctx.planet_sign.get("Saturn") in (10, 11):
                chart_cond = "Tonic Structural Limitation (Strong in Own Sign)"
            elif ctx.planet_sign.get("Saturn") == 1:
                chart_cond = "Atonic / Excessive Depressive Cold (Fall in Aries)"
            elif is_rx:
                chart_cond = "Retrograde Centripetal Contraction"
        elif p_name == "Jupiter":
            if is_rx:
                chart_cond = "Retrograde (Weakened Life-Preserving Power - Däath Doctrine)"
            elif jup_sign in (9, 12, 4):
                chart_cond = "Tonic / Splendid Vital Preservation"
        elif p_name == "Sun":
            if sun_s == 7:
                chart_cond = "Atonic Vitality (Fall in Libra)"
            elif sun_s in (1, 5):
                chart_cond = "Tonic / High Caloric Vitality"
        elif p_name == "Moon":
            if moon_s == 8:
                chart_cond = "Atonic / Perverted Radical Moisture (Fall in Scorpio)"
            elif moon_s in (2, 4):
                chart_cond = "Tonic Fluidic Plenitude"

        planets_biodynamics.append(
            DaathPlanetAction(
                planet=p_name,
                planet_ta=p_data["planet_ta"],
                esoteric_title=p_data["esoteric_title"],
                biodynamic_motion=p_data["biodynamic_motion"],
                polarity=p_data["polarity"],
                functional_group=p_data["functional_group"],
                tissue_building=p_data["tissue_building"],
                elemental_degrees=p_data["elemental_degrees"],
                salient_pathognomy=p_data["salient_pathognomy"],
                typical_drugs=p_data["typical_drugs"],
                typical_plants=p_data["typical_plants"],
                therapeutic_properties=p_data["therapeutic_properties"],
                metals_minerals=p_data["metals_minerals"],
                native_chart_condition=chart_cond,
            )
        )

    # 3. Temperaments & Quadruplicities
    fire_signs = {1, 5, 9}
    earth_signs = {2, 6, 10}
    air_signs = {3, 7, 11}
    water_signs = {4, 8, 12}

    cardinal_signs = {1, 4, 7, 10}
    fixed_signs = {2, 5, 8, 11}
    mutable_signs = {3, 6, 9, 12}

    fire_count = sum(1 for s in ctx.planet_sign.values() if s in fire_signs)
    earth_count = sum(1 for s in ctx.planet_sign.values() if s in earth_signs)
    air_count = sum(1 for s in ctx.planet_sign.values() if s in air_signs)
    water_count = sum(1 for s in ctx.planet_sign.values() if s in water_signs)

    counts = [("Sanguine (Air)", air_count), ("Choleric/Bilious (Fire)", fire_count), ("Nervous (Earth)", earth_count), ("Lymphatic (Water)", water_count)]
    dominant_temperament = max(counts, key=lambda x: x[1])[0]

    cardinal_count = sum(1 for s in ctx.planet_sign.values() if s in cardinal_signs)
    fixed_count = sum(1 for s in ctx.planet_sign.values() if s in fixed_signs)
    mutable_count = sum(1 for s in ctx.planet_sign.values() if s in mutable_signs)

    temperament_data = {
        "dominant_temperament": dominant_temperament,
        "fire_count": fire_count,
        "earth_count": earth_count,
        "air_count": air_count,
        "water_count": water_count,
        "cardinal_count": cardinal_count,
        "fixed_count": fixed_count,
        "mutable_count": mutable_count,
        "temperament_definitions": DAATH_TEMPERAMENTS_AND_CROSSES["temperaments"],
        "cross_definitions": DAATH_TEMPERAMENTS_AND_CROSSES["quadruplicities"],
    }

    # 4. Antipathic Therapeutics
    antipathic_therapies: List[DaathAntipathicTherapy] = [
        DaathAntipathicTherapy(
            category=at["category"],
            category_ta=at["category_ta"],
            opposing_polarity_rule=at["opposing_polarity_rule"],
            afflicting_planetary_force=at["afflicting_planetary_force"],
            curative_planetary_remedy=at["curative_planetary_remedy"],
            substances_and_application=at["substances_and_application"],
        )
        for at in DAATH_ANTIPATHIC_THERAPEUTICS
    ]

    # 5. Seven Ages of Man (Planetary Periods)
    birth_date_str = getattr(horoscope, "metadata", None)
    birth_year = 1990
    try:
        if birth_date_str and hasattr(birth_date_str, "birth_date"):
            b_str = str(birth_date_str.birth_date)
            birth_year = int(b_str.split("-")[0])
    except Exception:
        pass
    current_year = datetime.now(timezone.utc).year
    native_age = max(0, current_year - birth_year)

    seven_ages: List[DaathPlanetaryPeriod] = []
    for sap in DAATH_PLANETARY_PERIODS:
        is_current = (sap["start_age"] <= native_age < sap["end_age"])
        seven_ages.append(
            DaathPlanetaryPeriod(
                planet=sap["planet"],
                planet_ta=sap["planet_ta"],
                start_age=sap["start_age"],
                end_age=sap["end_age"],
                age_label=sap["age_label"],
                age_label_ta=sap["age_label_ta"],
                biological_development=sap["biological_development"],
                astrological_vulnerability=sap["astrological_vulnerability"],
                is_native_current_age=is_current,
            )
        )

    # 6. Decumbiture & Cycles
    decumbiture_data = DaathDecumbitureCriticalDays(
        lunar_critical_cycles=DAATH_DECUMBITURE_DATA["lunar_critical_cycles"],
        lunar_phases_metabolism=DAATH_DECUMBITURE_DATA["lunar_phases_metabolism"],
        climacteric_seven_year_law=DAATH_DECUMBITURE_DATA["climacteric_seven_year_law"],
        climacteric_seven_year_law_ta=DAATH_DECUMBITURE_DATA["climacteric_seven_year_law_ta"],
    )

    # 7. Strength Evaluation (Aspect, Positional, Natural/Sign Receptions, Motional, Directional)
    SIGN_RULERS = {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
        5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
        9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
    }
    mutual_receptions: List[str] = []
    checked_pairs = set()
    for p1, s1 in ctx.planet_sign.items():
        ruler_of_s1 = SIGN_RULERS.get(s1)
        if ruler_of_s1 and ruler_of_s1 != p1 and ruler_of_s1 in ctx.planet_sign:
            s2 = ctx.planet_sign[ruler_of_s1]
            ruler_of_s2 = SIGN_RULERS.get(s2)
            if ruler_of_s2 == p1:
                pair_key = tuple(sorted([p1, ruler_of_s1]))
                if pair_key not in checked_pairs:
                    checked_pairs.add(pair_key)
                    mutual_receptions.append(
                        f"Mutual Reception: {p1} in sign of {ruler_of_s1} ({SIGN_NAMES_EN.get(s1, '')}) <-> {ruler_of_s1} in sign of {p1} ({SIGN_NAMES_EN.get(s2, '')})"
                    )

    if not mutual_receptions:
        mutual_receptions.append("No strict mutual reception by domicile sign detected in chart.")

    horo_planets = getattr(horoscope, "planets", []) if horoscope else []
    retro_planets = [getattr(p, "name", "") for p in horo_planets if getattr(p, "is_retrograde", False)]
    motional_summary = (
        f"Retrograde bodies in chart: {', '.join(retro_planets) if retro_planets else 'None (All direct progression)'}. "
        f"{'Note Däath doctrine: Retrograde Jupiter is robbed of much of its sustaining life-force.' if 'Jupiter' in retro_planets else 'Jupiter is direct, preserving full aphetic vitality.'}"
    )

    angles_count = sum(1 for h in ctx.planet_house.values() if h in (1, 4, 7, 10))
    cadent_count = sum(1 for h in ctx.planet_house.values() if h in (3, 6, 9, 12))
    mundane_summary = (
        f"Planets on Angles (1, 4, 7, 10): {angles_count} (High dynamic potency). "
        f"Planets in Cadent Houses (3, 6, 9, 12): {cadent_count} (Morbific falling away / chronic vulnerability in 6th & 12th)."
    )

    strength_eval = DaathStrengthEvaluation(
        drikbalam_aspect_summary="Trine aspects (120°) function as Anabolic (life-force sustaining); Quartiles (90°) and Oppositions (180°) function as Katabolic (life-force consuming); Conjunctions act as interdependent focal poles.",
        sthanabalam_summary=f"Sun in {SIGN_NAMES_EN.get(sun_s, '')}, Moon in {SIGN_NAMES_EN.get(moon_s, '')}, Mars in {SIGN_NAMES_EN.get(mars_sign, '')}, Saturn in {SIGN_NAMES_EN.get(ctx.planet_sign.get('Saturn', 1), '')}.",
        nisargikabalam_mutual_receptions=mutual_receptions,
        mundane_strength_summary=mundane_summary,
        motional_strength_summary=motional_summary,
        directional_hexis_vs_diathesis="Hexis (permanent constitutional habit) is determined by the radical chart; Diathesis (transient excitability) is aroused during corresponding planetary periods and transits.",
    )

    # 8. Matched Classical Rules
    matched_rules: List[MedicalRule] = []

    def _is_hard_asp(deg1: float, deg2: float) -> Tuple[bool, str]:
        diff = abs(deg1 - deg2) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
        if diff <= 9.0:
            return True, f"Conjunction ({diff:.1f}° orb)"
        if 82.0 <= diff <= 98.0:
            return True, f"Square ({diff:.1f}°)"
        if 171.0 <= diff <= 180.0:
            return True, f"Opposition ({diff:.1f}°)"
        return False, ""

    horo_planets_list = getattr(horoscope, "planets", []) if horoscope else []
    planet_longs: Dict[str, float] = {
        getattr(p, "name", ""): float(getattr(p, "longitude", 0.0)) for p in horo_planets_list
    }
    sun_deg = planet_longs.get("Sun", 0.0)
    moon_deg = planet_longs.get("Moon", 0.0)
    mars_deg = planet_longs.get("Mars", 0.0)
    sat_deg = planet_longs.get("Saturn", 0.0)
    merc_deg = planet_longs.get("Mercury", 0.0)
    ven_deg = planet_longs.get("Venus", 0.0)
    jup_deg = planet_longs.get("Jupiter", 0.0)
    uranus_deg = planet_longs.get("Uranus", 0.0)
    neptune_deg = planet_longs.get("Neptune", 0.0)

    for r_def in DAATH_RULES_REGISTRY:
        r_id = r_def.id
        is_active = False
        trig_pos: List[str] = []
        planets_inv: List[str] = []
        rel_houses: List[int] = []

        if r_id == "daath_diphtheria_fixed_signs":
            fixed_pls = [p for p, s in ctx.planet_sign.items() if s in fixed_signs]
            has_sat_moon, _ = _is_hard_asp(sat_deg, moon_deg)
            has_mars_sun, _ = _is_hard_asp(mars_deg, sun_deg)
            if (asc_sign_idx in fixed_signs or len(fixed_pls) >= 3) and (has_sat_moon or has_mars_sun or asc_sign_idx in (2, 8)):
                is_active = True
                trig_pos.append(f"Fixed signs prominent ({len(fixed_pls)} planets), Ascendant in {SIGN_NAMES_EN.get(asc_sign_idx, '')}")
                planets_inv = ["Saturn", "Mars"] if (has_sat_moon or has_mars_sun) else ["Moon"]
                rel_houses = [1, 12, 6]

        elif r_id == "daath_renal_pelvis_calculus":
            has_ven_sat, v_desc = _is_hard_asp(ven_deg, sat_deg)
            scorpio_pls = [p for p, s in ctx.planet_sign.items() if s == 8]
            if has_ven_sat or "Saturn" in scorpio_pls or "Mars" in scorpio_pls:
                is_active = True
                trig_pos.append(f"Renal Pelvis zone: {'Venus-Saturn ' + v_desc if has_ven_sat else 'Scorpio tenanted by ' + ', '.join(scorpio_pls)}")
                planets_inv = ["Venus", "Saturn"] if has_ven_sat else scorpio_pls
                rel_houses = [ctx.planet_house.get("Saturn", 8), 8]

        elif r_id == "daath_brights_disease_nephritis":
            has_ven_sat, _ = _is_hard_asp(ven_deg, sat_deg)
            has_ven_jup, _ = _is_hard_asp(ven_deg, jup_deg)
            has_sun_jup, _ = _is_hard_asp(sun_deg, jup_deg)
            if (has_ven_sat or has_ven_jup or has_sun_jup) and (moon_s in water_signs or fixed_count >= 3):
                is_active = True
                trig_pos.append(f"Bright's disease indicators: Venus/Sun aspected by Saturn/Jupiter; Moon in water sign ({SIGN_NAMES_EN.get(moon_s, '')})")
                planets_inv = ["Venus", "Jupiter", "Saturn"]
                rel_houses = [7, 8, 6]

        elif r_id == "daath_ocular_blindness_rule":
            has_lum_asp, _ = _is_hard_asp(sun_deg, moon_deg)
            eye_signs = {1, 2, 4, 5, 10, 11}
            has_sat_aff, _ = _is_hard_asp(sat_deg, sun_deg)
            has_mars_aff, _ = _is_hard_asp(mars_deg, moon_deg)
            if (has_lum_asp or (sun_s in eye_signs and moon_s in eye_signs)) and (has_sat_aff or has_mars_aff):
                is_active = True
                trig_pos.append(f"Ocular affliction: Luminaries in sensitive signs ({SIGN_NAMES_EN.get(sun_s, '')}/{SIGN_NAMES_EN.get(moon_s, '')}) aspected by Mars/Saturn")
                planets_inv = ["Sun", "Moon", "Saturn"]
                rel_houses = [1, 2, 12]

        elif r_id == "daath_pulmonary_consumption_phthisis":
            has_gem_aff = any(ctx.planet_sign.get(p) == 3 for p in ("Saturn", "Mars", "Rahu"))
            lum_in_cadent_common = (sun_s in mutable_signs and sun_house in (6, 12)) or (moon_s in mutable_signs and ctx.planet_house.get("Moon") in (6, 12))
            if has_gem_aff or lum_in_cadent_common:
                is_active = True
                trig_pos.append(f"Pulmonary affliction: Gemini tenanted or Luminaries in cadent mutable signs (6th/12th)")
                planets_inv = ["Mercury", "Saturn"]
                rel_houses = [3, 6, 12]

        elif r_id == "daath_mental_genius_vs_derangement":
            has_merc_mars, mm_desc = _is_hard_asp(merc_deg, mars_deg)
            has_merc_sat, ms_desc = _is_hard_asp(merc_deg, sat_deg)
            has_moon_merc, mom_desc = _is_hard_asp(moon_deg, merc_deg)
            if has_merc_mars or has_merc_sat or has_moon_merc:
                is_active = True
                trig_pos.append(f"Mental dynamics: {mm_desc if has_merc_mars else (ms_desc if has_merc_sat else mom_desc)}")
                planets_inv = ["Mercury", "Mars"] if has_merc_mars else ["Mercury", "Moon"]
                rel_houses = [ctx.planet_house.get("Mercury", 1), 3, 9]

        elif r_id == "daath_varicose_veins_lower_limbs":
            ven_in_aq = (ctx.planet_sign.get("Venus") == 11)
            moon_in_aq = (moon_s == 11)
            has_aff = any(ctx.planet_sign.get(p) == 11 for p in ("Mars", "Saturn", "Rahu"))
            if ven_in_aq or moon_in_aq or (has_aff and ctx.planet_house.get("Venus") == 11):
                is_active = True
                trig_pos.append(f"Aquarius (calves/venous return) tenanted by Venus/Moon/Malefics")
                planets_inv = ["Venus", "Mars"]
                rel_houses = [11, 1]

        elif r_id == "daath_hip_joint_coxalgia_rule":
            sag_aff = (ctx.planet_sign.get("Saturn") == 9) or (ctx.planet_sign.get("Mars") == 9)
            has_mars_sat, _ = _is_hard_asp(mars_deg, sat_deg)
            if sag_aff or (has_mars_sat and (ctx.planet_sign.get("Saturn") in mutable_signs)):
                is_active = True
                trig_pos.append("Sagittarius (hips/femur) influenced by Saturn and Mars")
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [9, 6]

        elif r_id == "daath_gastritis_peptic_irritability":
            if mars_sign == 4 or (ctx.planet_house.get("Mars") == 4 and moon_s == 4):
                is_active = True
                trig_pos.append(f"Mars in Cancer (fall sign, stomach seat) - acute gastric irritability")
                planets_inv = ["Mars", "Moon"]
                rel_houses = [4, 6]

        elif r_id == "daath_spasms_ruptures_uranus":
            if uranus_deg > 0:
                has_u_mars, _ = _is_hard_asp(uranus_deg, mars_deg)
                has_u_moon, _ = _is_hard_asp(uranus_deg, moon_deg)
                if has_u_mars or has_u_moon:
                    is_active = True
                    trig_pos.append("Uranian spasmodic aspect to Mars or Moon")
                    planets_inv = ["Uranus", "Mars"]
                    rel_houses = [1, 6, 8]

        elif r_id == "daath_coma_psychic_drugs_neptune":
            if neptune_deg > 0:
                has_nep_moon, _ = _is_hard_asp(neptune_deg, moon_deg)
                has_nep_merc, _ = _is_hard_asp(neptune_deg, merc_deg)
                if has_nep_moon or has_nep_merc or (moon_s == 12):
                    is_active = True
                    trig_pos.append("Neptune aspect to Moon/Mercury or Moon in 12th/Pisces")
                    planets_inv = ["Neptune", "Moon"]
                    rel_houses = [12, 6]

        elif r_id == "daath_short_life_early_infancy":
            has_sun_sat, _ = _is_hard_asp(sun_deg, sat_deg)
            low_vit_signs = {4, 10, 12}
            if has_sun_sat and (sun_s in low_vit_signs or moon_s in low_vit_signs):
                is_active = True
                trig_pos.append(f"Sun afflicted by Saturn in low vitality sign ({SIGN_NAMES_EN.get(sun_s, '')})")
                planets_inv = ["Sun", "Saturn"]
                rel_houses = [1, 8]

        elif r_id == "daath_cardiac_aneurism_spinal_rule":
            leo_aff = any(ctx.planet_sign.get(p) == 5 for p in ("Mars", "Saturn", "Rahu"))
            has_sun_mars, sm_desc = _is_hard_asp(sun_deg, mars_deg)
            if leo_aff or has_sun_mars or (sun_house == 5 and mars_house == 5):
                is_active = True
                trig_pos.append(f"Cardiac & spinal focus: Leo afflicted or Sun-Mars {sm_desc}")
                planets_inv = ["Sun", "Mars"]
                rel_houses = [5, 1]

        elif r_id == "daath_enteritis_intestinal_digestion":
            virgo_aff = any(ctx.planet_sign.get(p) == 6 for p in ("Mars", "Saturn", "Rahu"))
            if virgo_aff or ctx.planet_house.get("Mars") == 6 or ctx.planet_house.get("Saturn") == 6:
                is_active = True
                trig_pos.append("Virgo / 6th house (chylification/enteric absorption) influenced by Mars or Saturn")
                planets_inv = ["Mars", "Saturn"]
                rel_houses = [6]

        elif r_id == "daath_cutaneous_epidermal_saturn":
            cap_aff = any(ctx.planet_sign.get(p) == 10 for p in ("Mars", "Saturn", "Rahu"))
            if cap_aff or sat_house in (1, 6):
                is_active = True
                trig_pos.append(f"Capricorn / Saturn prominent on epidermal boundary (House {sat_house})")
                planets_inv = ["Saturn"]
                rel_houses = [10, sat_house]

        elif r_id == "daath_blood_poisoning_oxygenation":
            aq_aff = any(ctx.planet_sign.get(p) == 11 for p in ("Mars", "Saturn", "Rahu"))
            if aq_aff or ctx.planet_house.get("Saturn") == 11:
                is_active = True
                trig_pos.append("Aquarius (fixed air / carbonic acid elimination) influenced by Mars/Saturn")
                planets_inv = ["Saturn", "Mars"]
                rel_houses = [11]

        cond_items = [
            MedicalConditionItem(
                condition=c,
                passed=is_active,
                detail=f"Condition status: {'Fulfilled' if is_active else 'Not satisfied'} in native's chart",
            )
            for c in r_def.mandatory_conditions
        ]

        rule_obj = MedicalRule(
            id=r_def.id,
            name=r_def.name,
            name_tamil=r_def.name_tamil,
            source=r_def.source,
            chapter_verse=r_def.chapter_verse,
            category=r_def.category,
            system=r_def.system,
            required_placements=", ".join(r_def.required_placements) if isinstance(r_def.required_placements, list) else str(r_def.required_placements),
            mandatory_conditions=r_def.mandatory_conditions,
            traditional_interpretation=r_def.traditional_interpretation,
            interpretation_tamil=r_def.interpretation_tamil,
            anatomical_system=r_def.anatomical_system,
            modifiers=", ".join(r_def.modifiers) if isinstance(r_def.modifiers, list) else (str(r_def.modifiers) if r_def.modifiers else None),
            conflicting_indications=", ".join(r_def.conflicting_indications) if isinstance(r_def.conflicting_indications, list) else (str(r_def.conflicting_indications) if r_def.conflicting_indications else None),
            is_active=is_active,
            status="Qualifying" if is_active else "Not Qualifying",
            triggered_positions=trig_pos,
            planets_involved=planets_inv,
            relevant_houses=rel_houses,
            conditions=cond_items,
            remedy_en=r_def.remedy_en,
            remedy_ta=r_def.remedy_ta,
        )
        matched_rules.append(rule_obj)

    return HeinrichDaathCompendium(
        book_title=DAATH_METADATA["book_title"],
        book_title_ta=DAATH_METADATA["book_title_ta"],
        author=DAATH_METADATA["author"],
        publisher=DAATH_METADATA["publisher"],
        historical_foundation=DAATH_METADATA["historical_foundation"],
        core_philosophy_en=DAATH_METADATA["core_philosophy_en"],
        core_philosophy_ta=DAATH_METADATA["core_philosophy_ta"],
        signs_anatomy=signs_anatomy,
        planets_biodynamics=planets_biodynamics,
        temperaments_and_crosses=temperament_data,
        antipathic_therapeutics=antipathic_therapies,
        seven_ages_of_man=seven_ages,
        decumbiture_and_cycles=decumbiture_data,
        strength_evaluation=strength_eval,
        matched_rules=matched_rules,
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

    # Dr. S. Krishna Kumar Compendium & Research Module
    dr_compendium = _evaluate_dr_krishna_kumar_compendium(ctx=ctx, horoscope=horoscope)

    # Dr. S. S. Chatterjee Compendium & Research Module
    dr_chatterjee_compendium = _evaluate_dr_chatterjee_compendium(
        ctx=ctx,
        horoscope=horoscope,
        live_transits=live_transits,
    )

    # Max Heindel & Augusta Foss Heindel Astro-Diagnosis Compendium
    max_heindel_compendium = _evaluate_max_heindel_compendium(
        ctx=ctx,
        horoscope=horoscope,
    )

    # Jane Ridder-Patrick "A Handbook of Medical Astrology" Compendium & Research Module
    jane_ridder_patrick_compendium = _evaluate_jane_ridder_patrick_compendium(
        ctx=ctx,
        horoscope=horoscope,
        live_transits=live_transits,
    )

    # Heinrich Daath Medical Astrology Compendium
    heinrich_daath_compendium = _evaluate_heinrich_daath_compendium(
        ctx=ctx,
        horoscope=horoscope,
        dasa=dasa,
        live_transits=live_transits,
    )

    return MedicalAstrologyResponse(
        metadata=metadata,
        rule_set_version=RULE_SET_VERSION,
        disclaimer_en=SAFETY_DISCLAIMER_EN,
        disclaimer_ta=SAFETY_DISCLAIMER_TA,
        vedic_analysis=vedic_analysis,
        kp_analysis=kp_analysis,
        dr_krishna_kumar_compendium=dr_compendium,
        dr_chatterjee_compendium=dr_chatterjee_compendium,
        max_heindel_compendium=max_heindel_compendium,
        jane_ridder_patrick_compendium=jane_ridder_patrick_compendium,
        heinrich_daath_compendium=heinrich_daath_compendium,
    )
