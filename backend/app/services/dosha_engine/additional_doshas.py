"""Additional classical Vedic Dosha evaluations: Pitru, Guru Chandal, Shrapit, and Grahan Doshas.

All evaluations follow classical treatises (BPHS, Phaladeepika, Saravali, Brihat Samhita)
with explicit condition triggers, classical cancellation/mitigation rules, and balanced
non-fatalistic English/Tamil interpretations.
"""

from typing import List
from app.schemas.dosha import SingleDoshaDetail
from app.services.dosha_engine.models import (
    DoshaChartContext,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


def evaluate_pitru_dosha(ctx: DoshaChartContext) -> SingleDoshaDetail:
    """Evaluate Pitru Dosha (ancestral/paternal karmic debt) per BPHS Ch. 83 & Phaladeepika."""
    sun = ctx.sun
    lord_9_name = ctx.get_house_lord(9)
    lord_9 = ctx.grahas.get(lord_9_name)

    triggers: List[str] = []
    planets_involved: List[str] = []
    houses_involved: List[int] = [9]

    # Check 1: Sun afflicted by Rahu, Ketu, or Saturn
    if sun:
        houses_involved.append(sun.house)
        for malefic in ("Rahu", "Ketu", "Saturn"):
            if ctx.is_conjoined(malefic, "Sun"):
                triggers.append(f"Sun (Pitru Karaka) conjoined with {malefic} in house {sun.house}")
                planets_involved.extend(["Sun", malefic])
            elif ctx.has_aspect_on_graha(malefic, "Sun"):
                triggers.append(f"Sun (Pitru Karaka) receives direct Parashari aspect from {malefic}")
                planets_involved.extend(["Sun", malefic])

    # Check 2: 9th house occupied by Rahu, Ketu, or Saturn
    planets_in_9 = ctx.get_planets_in_house(9)
    for malefic in ("Rahu", "Ketu", "Saturn"):
        if malefic in planets_in_9:
            triggers.append(f"{malefic} occupies 9th house of Dharma/Father")
            planets_involved.append(malefic)

    # Check 3: 9th lord afflicted by Rahu, Ketu, or Saturn
    if lord_9:
        houses_involved.append(lord_9.house)
        for malefic in ("Rahu", "Ketu", "Saturn"):
            if malefic != lord_9_name:
                if ctx.is_conjoined(malefic, lord_9_name):
                    triggers.append(f"9th lord ({lord_9_name}) conjoined with {malefic} in house {lord_9.house}")
                    planets_involved.extend([lord_9_name, malefic])
                elif ctx.has_aspect_on_graha(malefic, lord_9_name):
                    triggers.append(f"9th lord ({lord_9_name}) receives aspect from {malefic}")
                    planets_involved.extend([lord_9_name, malefic])

    is_present = len(triggers) > 0
    cancellations: List[str] = []

    if is_present:
        # Cancellation 1: Jupiter aspects Sun, 9th house, or 9th lord
        if ctx.has_aspect_on_house("Jupiter", 9):
            cancellations.append("Jupiter casts divine aspect directly onto the 9th house of Dharma")
        if sun and ctx.has_aspect_on_graha("Jupiter", "Sun"):
            cancellations.append("Jupiter aspects Sun, purifying paternal karma")
        if lord_9 and ctx.has_aspect_on_graha("Jupiter", lord_9_name):
            cancellations.append(f"Jupiter aspects 9th lord ({lord_9_name}), sanctifying the house lord")

        # Cancellation 2: Sun in high dignity (Aries exaltation or Leo own sign)
        if sun and (sun.sign_index == 1 or sun.sign_index == 5):
            cancellations.append(f"Sun placed in {SIGN_NAMES_EN[sun.sign_index]} holds superior dignity, neutralizing affliction")

        # Cancellation 3: 9th lord strongly placed in Kendra or Trikona with benefic support
        if lord_9 and (lord_9.house in KENDRA_HOUSES or lord_9.house in TRIKONA_HOUSES) and not ctx.is_debilitated(lord_9_name):
            cancellations.append(f"9th lord ({lord_9_name}) is strongly positioned in house {lord_9.house}")

    is_cancelled = is_present and len(cancellations) > 0

    if not is_present:
        severity = "None"
        interp_en = (
            "Sun, the 9th house, and the 9th lord are free from nodal and Saturnine afflictions. "
            "Pitru Dosha is absent, indicating ancestral blessings and strong dharmic heritage."
        )
        interp_ta = (
            "சூரியன், 9-ம் வீடு மற்றும் 9-ம் அதிபதி சுபத்தன்மையுடன் உள்ளனர். "
            "பித்ரு தோஷம் இல்லை. முன்னோர்களின் ஆசியும் தர்ம சிந்தனையும் சிறந்து விளங்கும்."
        )
    elif is_cancelled:
        severity = "Cancelled"
        interp_en = (
            f"Pitru Dosha indicators are neutralized by classical mitigating factors: {'; '.join(cancellations)}. "
            "Ancestral energies are harmonized, supporting steady family continuity and personal progress."
        )
        interp_ta = (
            f"பித்ரு தோஷ அறிகுறிகள் விசேஷ சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகின்றன. "
            "குடும்ப மேன்மையும் அமைதியும் நிலைத்திருக்கும்."
        )
    elif len(triggers) >= 3:
        severity = "High"
        interp_en = (
            f"Pronounced Pitru Dosha is detected ({'; '.join(triggers)}). "
            "Classical wisdom suggests honoring ancestors through charitable acts, caring for elders, "
            "and performing traditional annual rites (Tarpanam/Shraddha) to dissolve karmic blockages."
        )
        interp_ta = (
            f"பித்ரு தோஷம் தீவிர நிலையில் காணப்படுகிறது ({'; '.join(triggers)}). "
            "முன்னோர்களுக்குரிய திதி, தர்ப்பணம் ஆகியவற்றை சிரத்தையுடன் செய்வதும், பெரியோர்களை மதிப்பதும் வாழ்வில் சுப காரியத் தடைகளை நீக்கும்."
        )
    else:
        severity = "Moderate"
        interp_en = (
            f"Moderate Pitru Dosha is detected ({'; '.join(triggers)}). "
            "Focus on integrity, ethical living, and offering food or water to the needy mitigates these influences."
        )
        interp_ta = (
            f"மிதமான பித்ரு தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "அன்னதானம் செய்தல், குலதெய்வ வழிபாடு மற்றும் பெரியோர்களை போற்றுதல் நற்பலன்களைத் தரும்."
        )

    return SingleDoshaDetail(
        id="pitru_dosha",
        name="Pitru Dosha (Paternal Karmic Debt)",
        name_tamil="பித்ரு தோஷம்",
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        planets_involved=list(dict.fromkeys(planets_involved)),
        relevant_houses=list(dict.fromkeys(houses_involved)),
        conditions=triggers,
        cancellation_reasons=cancellations,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
        classical_reference="Brihat Parashara Hora Shastra Ch. 83 & Phaladeepika",
    )


def evaluate_guru_chandal_dosha(ctx: DoshaChartContext) -> SingleDoshaDetail:
    """Evaluate Guru Chandal Dosha (Jupiter-Rahu/Ketu affliction) per Saravali & Jataka Parijata."""
    jupiter = ctx.jupiter
    rahu = ctx.rahu
    ketu = ctx.ketu

    triggers: List[str] = []
    planets_involved: List[str] = []
    houses_involved: List[int] = []

    if jupiter:
        houses_involved.append(jupiter.house)

        # Conjunction with Rahu
        if rahu and ctx.is_conjoined("Jupiter", "Rahu"):
            orb = ctx.angular_separation("Jupiter", "Rahu")
            triggers.append(f"Jupiter conjoined with Rahu in {SIGN_NAMES_EN[jupiter.sign_index]} (Orb: {orb:.2f}°)")
            planets_involved.extend(["Jupiter", "Rahu"])
        # Conjunction with Ketu
        elif ketu and ctx.is_conjoined("Jupiter", "Ketu"):
            orb = ctx.angular_separation("Jupiter", "Ketu")
            triggers.append(f"Jupiter conjoined with Ketu in {SIGN_NAMES_EN[jupiter.sign_index]} (Orb: {orb:.2f}°)")
            planets_involved.extend(["Jupiter", "Ketu"])
        # Direct Aspect from Rahu
        elif rahu and ctx.has_aspect_on_graha("Rahu", "Jupiter"):
            triggers.append("Jupiter receives Parashari 5th/7th/9th aspect from Rahu")
            planets_involved.extend(["Jupiter", "Rahu"])

    is_present = len(triggers) > 0
    cancellations: List[str] = []

    if is_present and jupiter:
        # Cancellation 1: Jupiter in own sign (Sagittarius 9, Pisces 12) or exaltation (Cancer 4)
        if jupiter.sign_index in (4, 9, 12):
            cancellations.append(f"Jupiter in high dignity ({SIGN_NAMES_EN[jupiter.sign_index]}) maintains divine purity")

        # Cancellation 2: Separation exceeds 10 degrees
        if rahu and ctx.is_conjoined("Jupiter", "Rahu"):
            orb = ctx.angular_separation("Jupiter", "Rahu")
            if orb > 10.0:
                cancellations.append(f"Separation between Jupiter and Rahu ({orb:.2f}°) exceeds effective combustion orb (10°)")
        elif ketu and ctx.is_conjoined("Jupiter", "Ketu"):
            orb = ctx.angular_separation("Jupiter", "Ketu")
            if orb > 10.0:
                cancellations.append(f"Separation between Jupiter and Ketu ({orb:.2f}°) exceeds effective orb (10°)")

        # Cancellation 3: Jupiter in Kendra aspected by Venus
        if jupiter.house in KENDRA_HOUSES and ctx.has_aspect_on_graha("Venus", "Jupiter"):
            cancellations.append("Jupiter in Kendra receives benefic aspect from Venus, elevating wisdom")

    is_cancelled = is_present and len(cancellations) > 0

    if not is_present:
        severity = "None"
        interp_en = (
            "Jupiter is free from Rahu-Ketu nodal contamination. Guru Chandal Dosha is absent, "
            "supporting uncorrupted intellect, ethical clarity, and sound spiritual judgement."
        )
        interp_ta = (
            "குரு பகவான் ராகு-கேது சேர்க்கை அல்லது பார்வையின்றி சுபமாக உள்ளார். குரு சண்டாள தோஷம் இல்லை. "
            "நல்ல ஞானமும் சீரிய சிந்தனையும் மேலோங்கும்."
        )
    elif is_cancelled:
        severity = "Cancelled"
        interp_en = (
            f"Guru Chandal Dosha is effectively neutralized by classical factors: {'; '.join(cancellations)}. "
            "The native possesses sharp, unconventional analytical thinking and can achieve remarkable success in innovation."
        )
        interp_ta = (
            f"குரு சண்டாள தோஷம் விசேஷ சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. "
            "புதுமையான சிந்தனைகளும் ஆராய்ச்சித் திறனும் வெளிப்படும்."
        )
    else:
        orb_val = ctx.angular_separation("Jupiter", "Rahu") if rahu else 15.0
        severity = "High" if orb_val < 4.0 else "Moderate"
        interp_en = (
            f"Guru Chandal Dosha is active ({'; '.join(triggers)}) with {severity} intensity. "
            "Prompts unconventional questioning of orthodox dogma, skepticism towards spiritual teachers, and restless intellectual curiosity. "
            "Cultivating grounded ethical mentors and structured learning channels this dynamic energy into high investigative mastery."
        )
        interp_ta = (
            f"குரு சண்டாள தோஷம் ({severity} நிலை) செயல்படுகிறது ({'; '.join(triggers)}). "
            "பாரம்பரிய நம்பிக்கைகளில் சந்தேகங்களும் சலனங்களும் தோன்றலாம். சரியான வழிகாட்டுதலும் நற்பண்புகளும் கொண்ட குருவை நாடுவது வெற்றியைத் தரும்."
        )

    return SingleDoshaDetail(
        id="guru_chandal_dosha",
        name="Guru Chandal Dosha",
        name_tamil="குரு சண்டாள தோஷம்",
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        planets_involved=list(dict.fromkeys(planets_involved)),
        relevant_houses=list(dict.fromkeys(houses_involved)),
        conditions=triggers,
        cancellation_reasons=cancellations,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
        classical_reference="Saravali & Jataka Parijata",
    )


def evaluate_shrapit_dosha(ctx: DoshaChartContext) -> SingleDoshaDetail:
    """Evaluate Shrapit Yoga/Dosha (Saturn-Rahu combination) per BPHS & Bhrigu Samhita."""
    saturn = ctx.saturn
    rahu = ctx.rahu

    triggers: List[str] = []
    planets_involved: List[str] = []
    houses_involved: List[int] = []

    if saturn and rahu:
        houses_involved.extend([saturn.house, rahu.house])

        # Conjunction in same sign
        if ctx.is_conjoined("Saturn", "Rahu"):
            orb = ctx.angular_separation("Saturn", "Rahu")
            triggers.append(f"Saturn and Rahu conjoined in house {saturn.house} in {SIGN_NAMES_EN[saturn.sign_index]} (Orb: {orb:.2f}°)")
            planets_involved.extend(["Saturn", "Rahu"])
        # Mutual Parashari aspect (7th opposition)
        elif saturn.house == ((rahu.house + 5) % 12) + 1:  # 7 houses apart
            triggers.append(f"Saturn in house {saturn.house} and Rahu in house {rahu.house} in mutual 7th aspect")
            planets_involved.extend(["Saturn", "Rahu"])

    is_present = len(triggers) > 0
    cancellations: List[str] = []

    if is_present and saturn:
        # Cancellation 1: Saturn-Rahu in Upachaya houses (3, 6, 10, 11)
        if saturn.house in UPACHAYA_HOUSES:
            cancellations.append(f"Combination situated in Upachaya house {saturn.house}, where malefics produce powerful worldly victory")

        # Cancellation 2: Aspect of unafflicted Jupiter
        if ctx.has_aspect_on_graha("Jupiter", "Saturn"):
            cancellations.append("Jupiter's benefic aspect falls directly on Saturn, dissolving karmic hardship")

        # Cancellation 3: Saturn in own sign (Capricorn 10, Aquarius 11) or exaltation (Libra 7)
        if saturn.sign_index in (7, 10, 11):
            cancellations.append(f"Saturn in high dignity ({SIGN_NAMES_EN[saturn.sign_index]}) disciplines the node into productive focus")

    is_cancelled = is_present and len(cancellations) > 0

    if not is_present:
        severity = "None"
        interp_en = (
            "Saturn and Rahu do not conjoin or mutually aspect. Shrapit Dosha is completely absent."
        )
        interp_ta = (
            "சனி மற்றும் ராகு சேர்க்கையோ அல்லது நேரடி பார்வையோ இல்லை. சாப தோஷம் இல்லை."
        )
    elif is_cancelled:
        severity = "Cancelled"
        interp_en = (
            f"Shrapit Dosha is neutralized by classical mitigating factors: {'; '.join(cancellations)}. "
            "Grants extraordinary endurance, organizational capability, and mastery over complex engineering or enterprise."
        )
        interp_ta = (
            f"சாப தோஷம் விசேஷ அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. "
            "அயராத உழைப்பும் சவால்களை முறியடிக்கும் வல்லமையும் கிடைக்கும்."
        )
    else:
        severity = "Moderate"
        interp_en = (
            f"Active Shrapit Dosha detected ({'; '.join(triggers)}). "
            "Symbolizes ancestral or past-life karmic burdens manifesting as initial delays or feeling unappreciated despite arduous labor. "
            "Dedication to social service, patience, and honoring Saturnine discipline turns this into formidable resilience."
        )
        interp_ta = (
            f"சனி-ராகு சேர்க்கையால் சாப தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "முயற்சிகளில் தாமதங்கள் ஏற்பட்டாலும், நேர்மையான உழைப்பும் ஏழைகளுக்கு செய்யும் தொண்டும் தடைகளை நீக்கி வெற்றியைத் தரும்."
        )

    return SingleDoshaDetail(
        id="shrapit_dosha",
        name="Shrapit Yoga / Dosha (Saturn-Rahu Curse)",
        name_tamil="சாப தோஷம் (சனி-ராகு சேர்க்கை)",
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        planets_involved=list(dict.fromkeys(planets_involved)),
        relevant_houses=list(dict.fromkeys(houses_involved)),
        conditions=triggers,
        cancellation_reasons=cancellations,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
        classical_reference="Brihat Parashara Hora Shastra & Bhrigu Samhita",
    )


def evaluate_grahan_dosha(ctx: DoshaChartContext, luminary: str) -> SingleDoshaDetail:
    """Evaluate Grahan Dosha (Solar/Lunar Eclipse Affliction) within classical 12° orb."""
    lum = ctx.grahas.get(luminary)
    rahu = ctx.rahu
    ketu = ctx.ketu

    triggers: List[str] = []
    planets_involved: List[str] = []
    houses_involved: List[int] = []

    dosha_id = f"grahan_dosha_{luminary.lower()}"
    dosha_name = f"Surya Grahan Dosha (Solar Eclipse Affliction)" if luminary == "Sun" else "Chandra Grahan Dosha (Lunar Eclipse Affliction)"
    dosha_name_ta = "சூரிய கிரகண தோஷம்" if luminary == "Sun" else "சந்திர கிரகண தோஷம்"

    if lum:
        houses_involved.append(lum.house)

        for node_name, node_obj in [("Rahu", rahu), ("Ketu", ketu)]:
            if node_obj and ctx.is_conjoined(luminary, node_name):
                orb = ctx.angular_separation(luminary, node_name)
                if orb <= 12.0:
                    triggers.append(f"{luminary} conjoined with {node_name} within eclipse orb ({orb:.2f}° <= 12.0°)")
                    planets_involved.extend([luminary, node_name])

    is_present = len(triggers) > 0
    cancellations: List[str] = []

    if is_present and lum:
        # Cancellation 1: Separation exceeds 10°
        for node_name in ("Rahu", "Ketu"):
            if ctx.is_conjoined(luminary, node_name):
                orb = ctx.angular_separation(luminary, node_name)
                if orb > 10.0:
                    cancellations.append(f"Separation ({orb:.2f}°) is beyond the critical eclipse core (> 10°)")

        # Cancellation 2: Jupiter aspects Luminary
        if ctx.has_aspect_on_graha("Jupiter", luminary):
            cancellations.append(f"Jupiter casts Parashari aspect onto {luminary}, restoring luminous vitality")

        # Cancellation 3: High dignity of Luminary
        if luminary == "Sun" and lum.sign_index in (1, 5):
            cancellations.append(f"Sun in {SIGN_NAMES_EN[lum.sign_index]} (exalted/own sign) repels eclipse shadow")
        elif luminary == "Moon" and lum.sign_index in (2, 4):
            cancellations.append(f"Moon in {SIGN_NAMES_EN[lum.sign_index]} (exalted/own sign) retains emotional equilibrium")

    is_cancelled = is_present and len(cancellations) > 0

    if not is_present:
        severity = "None"
        interp_en = f"{luminary} is free from close eclipse conjunction with lunar nodes. {dosha_name} is absent."
        interp_ta = f"{luminary} ராகு-கேது கிரகண எல்லைக்குள் இணையவில்லை. {dosha_name_ta} இல்லை."
    elif is_cancelled:
        severity = "Cancelled"
        interp_en = (
            f"{dosha_name} is mitigated by classical factors: {'; '.join(cancellations)}. "
            f"The native preserves {luminary}'s positive vitality."
        )
        interp_ta = (
            f"{dosha_name_ta} சுப அமைப்புகளால் ({'; '.join(cancellations)}) நிவர்த்தி பெறுகிறது. "
            "சுப பலன்கள் தடையின்றி கிடைக்கும்."
        )
    else:
        orb_val = min(
            [ctx.angular_separation(luminary, n) for n in ("Rahu", "Ketu") if ctx.is_conjoined(luminary, n)] or [12.0]
        )
        severity = "High" if orb_val < 5.0 else "Moderate"
        interp_en = (
            f"Active {dosha_name} detected ({'; '.join(triggers)}) with {severity} intensity. "
            f"May cause periodic phases of self-doubt or emotional fluctuations regarding {luminary}'s significations. "
            "Sun meditation, pranayama, and steady routines provide strong equilibrium."
        )
        interp_ta = (
            f"{dosha_name_ta} ({severity} நிலை) காணப்படுகிறது ({'; '.join(triggers)}). "
            "மன அமைதிக்கான தியானமும், பிராணாயாமமும் நலம் பயக்கும்."
        )

    return SingleDoshaDetail(
        id=dosha_id,
        name=dosha_name,
        name_tamil=dosha_name_ta,
        is_present=is_present,
        is_cancelled=is_cancelled,
        severity=severity,
        planets_involved=list(dict.fromkeys(planets_involved)),
        relevant_houses=list(dict.fromkeys(houses_involved)),
        conditions=triggers,
        cancellation_reasons=cancellations,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
        classical_reference="Brihat Samhita Ch. 5 & Phaladeepika",
    )


def evaluate_additional_doshas(ctx: DoshaChartContext) -> List[SingleDoshaDetail]:
    """Evaluate all additional classical doshas: Pitru, Guru Chandal, Shrapit, Grahan Sun, and Grahan Moon."""
    doshas: List[SingleDoshaDetail] = []
    doshas.append(evaluate_pitru_dosha(ctx))
    doshas.append(evaluate_guru_chandal_dosha(ctx))
    doshas.append(evaluate_shrapit_dosha(ctx))
    doshas.append(evaluate_grahan_dosha(ctx, "Sun"))
    doshas.append(evaluate_grahan_dosha(ctx, "Moon"))
    return doshas
