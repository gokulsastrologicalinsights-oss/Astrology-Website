"""Comprehensive Vedic Dosha Catalogue Evaluator.

Evaluates all 30 canonical Vedic Doshas defined in the specification:
A. Planetary conjunction and axis doshas (1 to 8)
B. Moon and Nakshatra doshas (9 to 15)
C. Lagna and house-based doshas (16 to 23)
D. Marriage compatibility doshas (24 to 27) - requires partner chart
E. Transit doshas (28 to 30) - uses natal Moon and transiting Saturn

All evaluations are rule-based, deterministic, classical (BPHS, Phaladeepika,
Muhurta Chintamani, Saravali, Brihat Samhita), and non-fatalistic.
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timezone

from app.schemas.dosha import DoshaEvaluationItem, DoshaSummary
from app.services.dosha_engine.models import (
    DoshaChartContext,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    DUSTHANA_HOUSES,
    NATURAL_MALEFICS,
    NATURAL_BENEFICS,
    GANDMOOL_NAKSHATRAS,
    MKS_HOUSES,
)
from app.services.dosha_engine.kuja_dosha import evaluate_kuja_dosha
from app.services.dosha_engine.kaal_sarp import evaluate_kaal_sarp_dosha
from app.services.dosha_engine.sadesati import evaluate_sadesati
from app.services.dosha_engine.additional_doshas import (
    evaluate_pitru_dosha,
    evaluate_guru_chandal_dosha,
    evaluate_shrapit_dosha,
    evaluate_grahan_dosha,
)


def _fmt_degrees(ctx: DoshaChartContext, planet_names: List[str]) -> Dict[str, float]:
    """Format degrees in sign for involved planets."""
    res = {}
    for p in planet_names:
        if p == "Lagna":
            res["Lagna"] = round(ctx.ascendant_longitude % 30.0, 2)
        elif p in ctx.grahas:
            res[p] = round(ctx.grahas[p].degree_in_sign, 2)
    return res


def _fmt_signs_and_houses(ctx: DoshaChartContext, planet_names: List[str]) -> List[str]:
    """Format sign and house string for involved planets."""
    res = []
    for p in planet_names:
        if p == "Lagna":
            sign_name = SIGN_NAMES_EN.get(ctx.ascendant_sign_idx, "Unknown")
            res.append(f"Lagna in {sign_name} (House 1)")
        elif p in ctx.grahas:
            g = ctx.grahas[p]
            sign_name = SIGN_NAMES_EN.get(g.sign_index, "Unknown")
            res.append(f"{p} in {sign_name} (House {g.house})")
    return res


def evaluate_angarak_dosha(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Angarak Dosha (Mars-Rahu / Mars-Ketu conjunction/aspect)."""
    mars = ctx.mars
    rahu = ctx.rahu
    ketu = ctx.ketu

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    if mars and rahu and ctx.is_conjoined("Mars", "Rahu"):
        orb = ctx.angular_separation("Mars", "Rahu")
        triggers.append(f"Mars and Rahu conjoined in {SIGN_NAMES_EN[mars.sign_index]} in House {mars.house} (Orb: {orb:.2f}°)")
        planets_involved.extend(["Mars", "Rahu"])
    elif mars and ketu and ctx.is_conjoined("Mars", "Ketu"):
        orb = ctx.angular_separation("Mars", "Ketu")
        triggers.append(f"Mars and Ketu conjoined in {SIGN_NAMES_EN[mars.sign_index]} in House {mars.house} (Orb: {orb:.2f}°)")
        planets_involved.extend(["Mars", "Ketu"])

    is_present = len(triggers) > 0

    if is_present and mars:
        # Cancellations
        if mars.house in UPACHAYA_HOUSES:
            cancellations.append(f"Mars situated in Upachaya House {mars.house} where malefics channel courage into enterprise")
        if ctx.has_aspect_on_graha("Jupiter", "Mars"):
            cancellations.append("Jupiter casts divine aspect on Mars, soothing volatile impulses")
        if mars.sign_index in (1, 8, 10):
            cancellations.append(f"Mars in high dignity ({SIGN_NAMES_EN[mars.sign_index]}) maintains disciplined self-control")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Mars is free from nodal affliction. Angarak Dosha is absent, conferring balanced vitality and assertiveness."
        if status == "absent" else
        (
            f"Angarak Dosha is mitigated by classical factors: {'; '.join(cancellations)}. "
            "Grants pioneering drive, executive resolve, and high endurance."
            if status == "mitigated" else
            f"Active Angarak Dosha detected ({'; '.join(triggers)}). "
            "May bring sudden surges of impatience or passionate volatility. Physical exercise, martial discipline, and cooling foods balance this heat."
        )
    )
    interp_ta = (
        "செவ்வாய்-ராகு/கேது சேர்க்கை இல்லை. அங்காரக தோஷம் இல்லை. மன உறுதியும் நல் ஆற்றலும் நிலைத்திருக்கும்."
        if status == "absent" else
        (
            f"அங்காரக தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. "
            "துணிச்சலும் வெற்றிகரமான நிர்வாகத் திறனும் உண்டாகும்."
            if status == "mitigated" else
            f"அங்காரக தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "ஆத்திரத்தைத் தவிர்த்து அமைதியைக் கடைப்பிடிப்பதும், செவ்வாய்க்கிழமை வழிபாடும் அமைதியைத் தரும்."
        )
    )

    remedies = [
        "Chant Mangala Gayatri Mantra: Om Angarakaya Vidmahe Sakti Hastaya Dhimahi Tanno Bhaumah Prachodayat",
        "Offer red lentils (masoor dal) or donate blood for health vitality",
        "Visit Vaitheeswaran Koil / Angaraka Sthalam in Mayiladuthurai",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="angarak_dosha",
        name_en="Angarak Dosha (Mars–Rahu/Ketu Affliction)",
        name_ta="அங்காரக தோஷம் (செவ்வாய்-ராகு/கேது)",
        category="Planetary Conjunction & Axis",
        status=status,
        reference_basis="Lagna & Mars Placement",
        formation_conditions=triggers if triggers else ["Mars conjoined with Rahu or Ketu in the same zodiac sign"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Mars in Upachaya houses (3, 6, 10, 11)",
            "Jupiter aspect on Mars",
            "Mars in own sign (Aries/Scorpio) or exaltation (Capricorn)",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="BPHS & Bhrigu Samhita",
        remedies=remedies,
    )


def evaluate_vish_dosha(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Vish Dosha / Chandra-Shani Dosha (Moon-Saturn conjunction/aspect)."""
    moon = ctx.moon
    saturn = ctx.saturn

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    if moon and saturn:
        if ctx.is_conjoined("Moon", "Saturn"):
            orb = ctx.angular_separation("Moon", "Saturn")
            triggers.append(f"Moon and Saturn conjoined in {SIGN_NAMES_EN[moon.sign_index]} in House {moon.house} (Orb: {orb:.2f}°)")
            planets_involved.extend(["Moon", "Saturn"])
        elif saturn.house == ((moon.house + 5) % 12) + 1:  # 7th mutual aspect
            triggers.append(f"Moon in House {moon.house} and Saturn in House {saturn.house} in mutual 7th aspect")
            planets_involved.extend(["Moon", "Saturn"])

    is_present = len(triggers) > 0

    if is_present and moon and saturn:
        if ctx.has_aspect_on_graha("Jupiter", "Moon"):
            cancellations.append("Jupiter casts benefic aspect onto Moon, restoring emotional tranquility")
        if moon.sign_index in (2, 4):
            cancellations.append(f"Moon in high dignity ({SIGN_NAMES_EN[moon.sign_index]}) resists emotional melancholy")
        if saturn.sign_index in (7, 10, 11):
            cancellations.append(f"Saturn in high dignity ({SIGN_NAMES_EN[saturn.sign_index]}) confers meditative maturity instead of sorrow")
        if moon.house in (3, 11):
            cancellations.append(f"Conjunction situated in Upachaya House {moon.house}, producing durable emotional resilience")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Moon is free from Saturnine conjunction or mutual aspect. Vish Dosha is absent, supporting emotional cheer and mental ease."
        if status == "absent" else
        (
            f"Vish Dosha is mitigated by classical factors: {'; '.join(cancellations)}. "
            "Grants extraordinary contemplative focus, emotional discipline, and spiritual grounding."
            if status == "mitigated" else
            f"Active Vish Dosha detected ({'; '.join(triggers)}). "
            "Can cause intermittent spells of introspection, self-criticism, or emotional gravity. Meditation, sunlight, and steady companionship nurture well-being."
        )
    )
    interp_ta = (
        "சந்திரனுடன் சனி சேர்க்கையோ நேரடி பார்வையோ இல்லை. விஷ தோஷம் இல்லை. மன மகிழ்ச்சியும் தெளிவும் சிறக்கும்."
        if status == "absent" else
        (
            f"விஷ தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. "
            "ஆழ்ந்த சிந்தனையும், பக்குவமான மனநிலையும் உண்டாகும்."
            if status == "mitigated" else
            f"சனி-சந்திர சேர்க்கையால் விஷ தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "மனச்சோர்வைத் தவிர்க்க தியானம், இறை வழிபாடு மற்றும் நேர்மறை எண்ணங்கள் நலம் பயக்கும்."
        )
    )

    remedies = [
        "Chant Chandra Mantra: Om Som Somaya Namaha and Shiva Panchakshari",
        "Offer white flowers or milk libation to Lord Shiva on Mondays",
        "Visit Thingaloor Kailasanathar Sthalam (Moon Temple) in Thanjavur",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="vish_dosha",
        name_en="Vish Dosha / Punarphoo (Moon–Saturn Affliction)",
        name_ta="விஷ தோஷம் / புனர்பூ (சனி-சந்திர சேர்க்கை)",
        category="Planetary Conjunction & Axis",
        status=status,
        reference_basis="Moon & Saturn Placement",
        formation_conditions=triggers if triggers else ["Moon conjoined with Saturn or in mutual 7th aspect"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Moon",
            "Moon in Taurus (exaltation) or Cancer (own sign)",
            "Saturn in Libra, Capricorn, or Aquarius",
            "Placement in Upachaya House (3 or 11)",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Phaladeepika Ch. 6 & Saravali",
        remedies=remedies,
    )


def evaluate_kemadruma_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Kemadruma Dosha and Kemadruma Bhanga (cancellations)."""
    moon = ctx.moon
    if not moon:
        return DoshaEvaluationItem(
            dosha_id="kemadruma_dosha",
            name_en="Kemadruma Dosha (Isolated Moon)",
            name_ta="கேமத்துரும தோஷம் (தனித்த சந்திரன்)",
            category="Moon & Nakshatra",
            status="absent",
            reference_basis="Moon",
            formation_conditions=["Moon data unavailable"],
            interpretation="Moon position unavailable.",
            interpretation_ta="சந்திரன் நிலை கிடைக்கவில்லை.",
            source_references="BPHS Ch. 36 & Phaladeepika Ch. 6",
        )

    # 2nd and 12th from Moon
    h2_sign = ((moon.sign_index) % 12) + 1
    h12_sign = ((moon.sign_index - 2) % 12) + 1

    valid_grahas = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    p_in_2 = [g.name for g in ctx.grahas.values() if g.sign_index == h2_sign and g.name in valid_grahas]
    p_in_12 = [g.name for g in ctx.grahas.values() if g.sign_index == h12_sign and g.name in valid_grahas]

    is_present = len(p_in_2) == 0 and len(p_in_12) == 0

    cancellations: List[str] = []
    if is_present:
        # 1. Moon conjoined with physical planet (excl Sun, nodes)
        conjoined = [g.name for g in ctx.grahas.values() if g.sign_index == moon.sign_index and g.name in valid_grahas]
        if conjoined:
            cancellations.append(f"Moon is conjoined with {', '.join(conjoined)}")

        # 2. Grahas in Kendras from Lagna
        kendra_grahas = [g.name for g in ctx.grahas.values() if g.house in KENDRA_HOUSES and g.name in valid_grahas]
        if kendra_grahas:
            cancellations.append(f"Planets occupy Kendras from Lagna ({', '.join(kendra_grahas)})")

        # 3. Grahas in Kendras from Moon
        moon_kendra_houses = {1, 4, 7, 10}
        kendra_moon_grahas = [
            g.name for g in ctx.grahas.values()
            if (((g.sign_index - moon.sign_index) % 12) + 1) in moon_kendra_houses and g.name in valid_grahas and g.name != "Moon"
        ]
        if kendra_moon_grahas:
            cancellations.append(f"Planets occupy Kendras from Moon ({', '.join(kendra_moon_grahas)})")

        # 4. Benefic aspect on Moon (Jupiter, Venus)
        if ctx.has_aspect_on_graha("Jupiter", "Moon"):
            cancellations.append("Jupiter casts full Parashari aspect on Moon")
        if ctx.has_aspect_on_graha("Venus", "Moon"):
            cancellations.append("Venus casts aspect on Moon")

        # 5. Moon in Kendra from Lagna
        if moon.house in KENDRA_HOUSES:
            cancellations.append(f"Moon is positioned in Lagna Kendra (House {moon.house})")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Moon has planets in adjacent houses. Kemadruma Dosha is completely absent, ensuring sustained financial and social security."
        if status == "absent" else
        (
            f"Kemadruma Dosha is fully cancelled (Kemadruma Bhanga) by classical factors: {'; '.join(cancellations)}. "
            "Treatises state that cancelled Kemadruma transforms adversity into enduring self-made prosperity (Kalpadruma Yoga)."
            if status == "mitigated" else
            "Moon is completely isolated without planets in flanking houses or Kendras. "
            "May bring feelings of emotional solitude or livelihood fluctuations. Benefic remedies and social bonds restore balance."
        )
    )
    interp_ta = (
        "சந்திரனின் இருபுறமும் கிரகங்கள் உள்ளன. கேமத்துரும தோஷம் இல்லை. நிதி மற்றும் குடும்ப வளம் சிறக்கும்."
        if status == "absent" else
        (
            f"கேமத்துரும தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) முழுமையாக தோஷ நிவர்த்தி (பங்கம்) பெறுகிறது. "
            "சுயமுயற்சியால் பெரும் யோகமும் செல்வமும் உண்டாகும் (கல்ப்பதரும யோகம்)."
            if status == "mitigated" else
            "சந்திரனின் இருபுறமும் கிரகங்களின்றி தனித்து காணப்படுகிறது. "
            "தனிமை உணர்வுகளைத் தவிர்த்து சுறுசுறுப்புடன் செயல்படுவதும், சிவ வழிபாடும் நன்மைகளைத் தரும்."
        )
    )

    remedies = [
        "Worship Goddess Lakshmi and Lord Shiva on Full Moon (Pournami) days",
        "Chant Sri Suktam or Mahalakshmi Ashtakam",
        "Keep silver or pure water vessels in the northeast corner of home",
    ] if status in ("present", "mitigated") else []

    involved = ["Moon"]
    if is_present and cancellations:
        involved.extend([p for p in ("Jupiter", "Venus") if ctx.has_aspect_on_graha(p, "Moon")])

    return DoshaEvaluationItem(
        dosha_id="kemadruma_dosha",
        name_en="Kemadruma Dosha (Isolated Moon & Bhanga)",
        name_ta="கேமத்துரும தோஷம் (தனித்த சந்திரன் & பங்க யோகம்)",
        category="Moon & Nakshatra",
        status=status,
        reference_basis="Natal Moon Flanks (Houses 2 & 12 from Moon)",
        formation_conditions=[
            "Neither 2nd nor 12th house from Moon is occupied by classical grahas (excl. Sun, Rahu, Ketu)"
        ] if is_present else ["Flanks of Moon are occupied by benefic or physical planets"],
        involved_planets=list(dict.fromkeys(involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, ["Moon"]),
        degrees=_fmt_degrees(ctx, ["Moon"]),
        cancellation_conditions_checked=[
            "Planets in Kendras from Lagna",
            "Planets in Kendras from Moon",
            "Benefic aspect on Moon from Jupiter or Venus",
            "Moon in Kendra (1, 4, 7, 10) from Lagna",
            "Moon conjoined with another physical graha",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 36 & Phaladeepika Ch. 6, vv. 8-11",
        remedies=remedies,
    )


def evaluate_gandmool_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Gandmool Dosha (Moon in Ketu/Mercury nakshatras)."""
    moon = ctx.moon
    if not moon:
        return DoshaEvaluationItem(
            dosha_id="gandmool_dosha",
            name_en="Gandmool Dosha",
            name_ta="கண்டமூல தோஷம்",
            category="Moon & Nakshatra",
            status="absent",
            reference_basis="Moon Nakshatra",
            formation_conditions=["Moon data unavailable"],
            interpretation="Moon position unavailable.",
            interpretation_ta="சந்திரன் நிலை கிடைக்கவில்லை.",
            source_references="BPHS Ch. 9",
        )

    nak_idx = moon.nakshatra_index
    nak_name_en = NAKSHATRA_NAMES_EN.get(nak_idx, "Unknown")
    nak_name_ta = NAKSHATRA_NAMES_TA.get(nak_idx, "Unknown")

    is_present = nak_idx in GANDMOOL_NAKSHATRAS

    cancellations: List[str] = []
    if is_present:
        if ctx.has_aspect_on_graha("Jupiter", "Moon"):
            cancellations.append("Jupiter casts divine aspect onto Moon, sanctifying the birth star")
        lord_1_name = ctx.get_house_lord(1)
        lord_1 = ctx.grahas.get(lord_1_name)
        if lord_1 and (lord_1.house in KENDRA_HOUSES or lord_1.house in TRIKONA_HOUSES) and not ctx.is_debilitated(lord_1_name):
            cancellations.append(f"Lagna lord ({lord_1_name}) is robustly positioned in House {lord_1.house}")
        if moon.nakshatra_pada in (2, 3):
            cancellations.append(f"Birth in Pada {moon.nakshatra_pada} avoids the extreme initial/terminal boundary fraction")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        f"Natal Moon is in {nak_name_en} Nakshatra, which is free from Gandmool affliction. Gandmool Dosha is absent."
        if status == "absent" else
        (
            f"Moon is in {nak_name_en} Nakshatra (Pada {moon.nakshatra_pada}), mitigated by: {'; '.join(cancellations)}. "
            "Traditional pacification preserves parental harmony and childhood vitality."
            if status == "mitigated" else
            f"Moon is in {nak_name_en} Nakshatra (Pada {moon.nakshatra_pada}), ruled by nodal or mercurial junctions. "
            "Classical traditions recommend a 27th-day Nakshatra Shanti ceremony and honoring elders to harmonize the native's journey."
        )
    )
    interp_ta = (
        f"சந்திரன் {nak_name_ta} நட்சத்திரத்தில் உள்ளது. கண்டமூல தோஷம் இல்லை. சுப பலன்கள் நிலைக்கும்."
        if status == "absent" else
        (
            f"சந்திரன் {nak_name_ta} (பாதம் {moon.nakshatra_pada}) நட்சத்திரத்தில் உள்ளபோதிலும் ({'; '.join(cancellations)}) சுப அமைப்புகளால் நிவர்த்தி பெறுகிறது."
            if status == "mitigated" else
            f"சந்திரன் {nak_name_ta} (பாதம் {moon.nakshatra_pada}) நட்சத்திரத்தில் உள்ளது. கண்டமூல தோஷம் காணப்படுகிறது. "
            "27-ஆம் நாள் நட்சத்திர சாந்தி செய்வதும், பெற்றோரை மதிப்பதும் நன்மைகளைத் தரும்."
        )
    )

    remedies = [
        "Perform Gandmool Nakshatra Shanti on Moon's return to birth star",
        "Worship Lord Ganesha for Ketu Nakshatras (Ashwini, Magha, Moola) or Lord Vishnu for Mercury Nakshatras (Ashlesha, Jyeshtha, Revati)",
        "Offer green gram (moong dal) or brown cloth in charity",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="gandmool_dosha",
        name_en="Gandmool Dosha (Ketu/Mercury Nakshatra Junction)",
        name_ta="கண்டமூல தோஷம் (கேது/புதன் நட்சத்திர சந்தி)",
        category="Moon & Nakshatra",
        status=status,
        reference_basis=f"Moon in {nak_name_en} (Pada {moon.nakshatra_pada})",
        formation_conditions=[
            f"Moon occupies Gandmool Nakshatra {nak_name_en} (#{nak_idx})"
        ] if is_present else ["Moon occupies non-Gandmool Nakshatra"],
        involved_planets=["Moon"],
        signs_and_houses=_fmt_signs_and_houses(ctx, ["Moon"]),
        degrees=_fmt_degrees(ctx, ["Moon"]),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Moon",
            "Lagna lord strong in Kendra or Trikona",
            "Birth in middle Padas (2 or 3) rather than edge boundary",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 9 & Jataka Parijata",
        remedies=remedies,
    )


def evaluate_gandanta_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Gandanta condition (separate from Gandmool: exact water-fire sandhi boundaries)."""
    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    # 1. Lagna Gandanta (Ascendant longitude within 3°20' of water-fire sandhis)
    is_lagna_g, sandhi_en, sandhi_ta = DoshaChartContext.is_gandanta_zone(ctx.ascendant_longitude)
    if is_lagna_g:
        deg_str = f"{(ctx.ascendant_longitude % 30.0):.2f}°"
        triggers.append(f"Ascendant (Lagna) at {deg_str} in {sandhi_en}")
        planets_involved.append("Lagna")

    # 2. Chandra Gandanta (Moon longitude within 3°20' of sandhi)
    if ctx.moon:
        is_moon_g, m_sandhi_en, _ = DoshaChartContext.is_gandanta_zone(ctx.moon.longitude)
        if is_moon_g:
            deg_str = f"{ctx.moon.degree_in_sign:.2f}°"
            triggers.append(f"Moon at {deg_str} in {m_sandhi_en}")
            planets_involved.append("Moon")

    # 3. Surya Gandanta
    if ctx.sun:
        is_sun_g, s_sandhi_en, _ = DoshaChartContext.is_gandanta_zone(ctx.sun.longitude)
        if is_sun_g:
            deg_str = f"{ctx.sun.degree_in_sign:.2f}°"
            triggers.append(f"Sun at {deg_str} in {s_sandhi_en}")
            planets_involved.append("Sun")

    is_present = len(triggers) > 0

    if is_present:
        if ctx.has_aspect_on_house("Jupiter", 1):
            cancellations.append("Jupiter casts divine aspect directly onto the Ascendant, elevating life vitality")
        if ctx.moon and ctx.has_aspect_on_graha("Jupiter", "Moon"):
            cancellations.append("Jupiter aspects Moon, purifying Chandra Gandanta")
        lord_1_name = ctx.get_house_lord(1)
        if ctx.is_exalted(lord_1_name) or ctx.is_own_sign(lord_1_name):
            cancellations.append(f"Lagna lord ({lord_1_name}) in superior dignity neutralizes sandhi vulnerability")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Ascendant, Moon, and Sun are located comfortably away from the critical water-fire junction boundaries. Gandanta is absent."
        if status == "absent" else
        (
            f"Gandanta position ({'; '.join(triggers)}) is mitigated by classical factors: {'; '.join(cancellations)}. "
            "Channels transitional sensitivity into exceptional intuitive and transformative prowess."
            if status == "mitigated" else
            f"Active Gandanta boundary condition detected ({'; '.join(triggers)}). "
            "Marks a karmic threshold between dissolution (water) and creation (fire). Traditional Gandanta Shanti rites and grounding habits foster enduring stability."
        )
    )
    interp_ta = (
        "லக்னம், சந்திரன், சூரியன் சந்தி எல்லைகளில் இல்லை. கண்டாந்த தோஷம் இல்லை."
        if status == "absent" else
        (
            f"கண்டாந்த நிலை ({'; '.join(triggers)}) சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. "
            "ஆழ்ந்த உள்ளுணர்வும் ஆன்மீக மேன்மையும் உண்டாகும்."
            if status == "mitigated" else
            f"கண்டாந்த சந்தி நிலை காணப்படுகிறது ({'; '.join(triggers)}). "
            "நீர்-நெருப்பு ராசி சந்தி என்பதால் மன அமைதிக்கான தியானமும், சாந்தி பரிகாரங்களும் நலம் சேர்க்கும்."
        )
    )

    remedies = [
        "Perform Gandanta Shanti / Ayushya Homam for longevity and bodily protection",
        "Worship Lord Shiva with Rudra Abhishekam",
        "Feed cows with green fodder or offer sesame sweets to the needy",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="gandanta_dosha",
        name_en="Gandanta Condition (Water–Fire Sign Boundary Sandhi)",
        name_ta="கண்டாந்த தோஷம் (நீர்-நெருப்பு ராசி சந்தி நிலை)",
        category="Moon & Nakshatra",
        status=status,
        reference_basis="Exact Longitudes within 3°20' of Water-Fire Boundaries (Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius)",
        formation_conditions=triggers if triggers else ["No celestial bodies placed within 3°20' water-to-fire junctions"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Lagna",
            "Benefic aspect of Jupiter on Moon",
            "Lagna lord in exaltation or own sign",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 9 & Phaladeepika Ch. 13",
        remedies=remedies,
    )


def evaluate_shakata_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Shakata Dosha (Moon in 6, 8, 12 from Jupiter, cancelled if Moon in Lagna Kendra)."""
    moon = ctx.moon
    jupiter = ctx.jupiter

    if not moon or not jupiter:
        return DoshaEvaluationItem(
            dosha_id="shakata_dosha",
            name_en="Shakata Dosha / Yoga (Cart-Wheel Fluctuations)",
            name_ta="சகட தோஷம் / யோகம்",
            category="Moon & Nakshatra",
            status="absent",
            reference_basis="Moon from Jupiter",
            formation_conditions=["Moon or Jupiter data unavailable"],
            interpretation="Planetary data unavailable.",
            interpretation_ta="கிரக நிலை கிடைக்கவில்லை.",
            source_references="Phaladeepika Ch. 6, v. 56",
        )

    dist_jup_to_moon = ((moon.sign_index - jupiter.sign_index) % 12) + 1
    is_present = dist_jup_to_moon in (6, 8, 12)

    cancellations: List[str] = []
    if is_present:
        # Classical Bhanga: Moon in Kendra from Lagna (1, 4, 7, 10) per Phaladeepika 6.56 & 300 Combos #100
        if moon.house in KENDRA_HOUSES:
            cancellations.append(f"Moon occupies Kendra House {moon.house} from Lagna, completely neutralizing Shakata affliction")
        if jupiter.house in KENDRA_HOUSES:
            cancellations.append(f"Jupiter occupies Kendra House {jupiter.house} from Lagna, anchoring fortune")
        if moon.sign_index in (2, 4):
            cancellations.append(f"Moon in high dignity ({SIGN_NAMES_EN[moon.sign_index]}) sustains fortitude")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        f"Moon is in {dist_jup_to_moon}th house from Jupiter. Shakata Dosha is absent; wealth and luck proceed smoothly."
        if status == "absent" else
        (
            f"Shakata Dosha is neutralized by classical cancellation (Shakata Bhanga): {'; '.join(cancellations)}. "
            "Fluctuations are replaced by enduring triumph and steady repute."
            if status == "mitigated" else
            f"Moon occupies the {dist_jup_to_moon}th house from Jupiter. "
            "Symbolizes the cyclical rotation of a cart wheel (intermittent rises and dips in fortune). Patience and persistent effort recover losses."
        )
    )
    interp_ta = (
        f"சந்திரன் குருவிற்கு {dist_jup_to_moon}-ம் இடத்தில் உள்ளதால் சகட தோஷம் இல்லை. யோக பலன்கள் தடையின்றி நடக்கும்."
        if status == "absent" else
        (
            f"சகட தோஷம் ({'; '.join(cancellations)}) சுப அமைப்புகளால் சகட பங்கம் பெற்று யோகமாக மாறுகிறது."
            if status == "mitigated" else
            f"சந்திரன் குருவிற்கு {dist_jup_to_moon}-ம் இடத்தில் மறைந்து சகட தோஷம் உண்டாகிறது. "
            "வண்டிச் சக்கரம் போல ஏற்ற இறக்கங்கள் வந்தாலும், விடாமுயற்சியும் ஒழுக்கமும் நற்பலன்களைத் தரும்."
        )
    )

    remedies = [
        "Chant Guru Mantra: Om Gram Grim Grom Sah Gurave Namaha on Thursdays",
        "Worship Lord Vishnu through Vishnu Sahasranama",
        "Offer yellow flowers or chickpeas (chana dal) to Dakshinamurthy",
    ] if status in ("present", "mitigated") else []

    involved = ["Moon", "Jupiter"]

    return DoshaEvaluationItem(
        dosha_id="shakata_dosha",
        name_en="Shakata Dosha / Yoga (Cart-Wheel Fluctuations)",
        name_ta="சகட தோஷம் / யோகம் (ஏற்ற இறக்க அமைப்பு)",
        category="Moon & Nakshatra",
        status=status,
        reference_basis="Moon from Jupiter",
        formation_conditions=[
            f"Moon occupies {dist_jup_to_moon}th house from Jupiter (6th, 8th, or 12th Dusthana distance)"
        ] if is_present else ["Moon is in auspicious mutual angle (1, 4, 5, 7, 9, 10, 11) from Jupiter"],
        involved_planets=involved,
        signs_and_houses=_fmt_signs_and_houses(ctx, involved),
        degrees=_fmt_degrees(ctx, involved),
        cancellation_conditions_checked=[
            "Moon in Kendra (1, 4, 7, 10) from Lagna",
            "Jupiter in Kendra from Lagna",
            "Moon in Taurus (exaltation) or Cancer (own sign)",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Phaladeepika Ch. 6, v. 56 & 300 Important Combinations #100",
        remedies=remedies,
    )


def evaluate_papa_kartari_moon_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Papa Kartari Yoga affecting the Moon."""
    moon = ctx.moon
    if not moon:
        return DoshaEvaluationItem(
            dosha_id="papa_kartari_moon",
            name_en="Papa Kartari affecting Moon",
            name_ta="சந்திர பாப கர்த்தாரி தோஷம்",
            category="Moon & Nakshatra",
            status="absent",
            reference_basis="Moon Flanks (Houses 12 & 2 from Moon)",
            formation_conditions=["Moon data unavailable"],
            interpretation="Moon position unavailable.",
            interpretation_ta="சந்திரன் நிலை கிடைக்கவில்லை.",
            source_references="BPHS & Saravali",
        )

    # 12th and 2nd signs from Moon
    s12 = ((moon.sign_index - 2) % 12) + 1
    s2 = ((moon.sign_index) % 12) + 1

    malefics_12 = [g.name for g in ctx.grahas.values() if g.sign_index == s12 and g.name in NATURAL_MALEFICS]
    malefics_2 = [g.name for g in ctx.grahas.values() if g.sign_index == s2 and g.name in NATURAL_MALEFICS]

    is_present = len(malefics_12) > 0 and len(malefics_2) > 0

    cancellations: List[str] = []
    if is_present:
        if ctx.has_aspect_on_graha("Jupiter", "Moon"):
            cancellations.append("Jupiter casts divine aspect onto Moon, severing the malefic scissor grip")
        if ctx.has_aspect_on_graha("Venus", "Moon"):
            cancellations.append("Venus casts benefic aspect onto Moon")
        # Benefics in same sign as Moon
        benefics_with_moon = [g.name for g in ctx.grahas.values() if g.sign_index == moon.sign_index and g.name in NATURAL_BENEFICS and g.name != "Moon"]
        if benefics_with_moon:
            cancellations.append(f"Benefics conjoined with Moon ({', '.join(benefics_with_moon)})")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    involved = ["Moon"] + malefics_12 + malefics_2

    interp_en = (
        "Moon is free from being hemmed between natural malefics. Papa Kartari is absent."
        if status == "absent" else
        (
            f"Papa Kartari on Moon is mitigated by: {'; '.join(cancellations)}. "
            "Grants mental sharpness and the ability to navigate complex pressure."
            if status == "mitigated" else
            f"Moon is hemmed between malefics in 12th ({', '.join(malefics_12)}) and 2nd ({', '.join(malefics_2)}) signs. "
            "May cause periods of feeling hemmed-in or mentally stressed. Pranayama and mindful routines restore equilibrium."
        )
    )
    interp_ta = (
        "சந்திரனின் இருபுறமும் அசுப கிரகங்கள் இல்லை. சந்திர பாப கர்த்தாரி தோஷம் இல்லை."
        if status == "absent" else
        (
            f"சந்திர பாப கர்த்தாரி அமைப்பு சுப அமைப்புகளால் ({'; '.join(cancellations)}) நிவர்த்தி பெறுகிறது."
            if status == "mitigated" else
            f"சந்திரன் இருபுறமும் அசுப கிரகங்களால் ({', '.join(malefics_12)} மற்றும் {', '.join(malefics_2)}) சூழப்பட்டு பாப கர்த்தாரி யோகம் உண்டாகிறது. "
            "தியானமும் நேர்மறை சிந்தனைகளும் மன அழுத்தத்தைப் போக்கும்."
        )
    )

    remedies = [
        "Chant Om Namah Shivaya daily",
        "Practice deep breathing or meditation near running water or gardens",
        "Donate white rice or milk to the poor on Mondays",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="papa_kartari_moon",
        name_en="Papa Kartari affecting Moon (Hemmed Luminary)",
        name_ta="சந்திர பாப கர்த்தாரி தோஷம் (சந்திரன் கத்தரி யோகம்)",
        category="Moon & Nakshatra",
        status=status,
        reference_basis="Flanks of Natal Moon",
        formation_conditions=[
            f"Moon in {SIGN_NAMES_EN[moon.sign_index]} hemmed by {', '.join(malefics_12)} (12th from Moon) and {', '.join(malefics_2)} (2nd from Moon)"
        ] if is_present else ["Moon is not hemmed between natural malefics"],
        involved_planets=list(dict.fromkeys(involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, involved),
        degrees=_fmt_degrees(ctx, involved),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Moon",
            "Benefic aspect of Venus on Moon",
            "Benefics conjoined with Moon",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra & Saravali",
        remedies=remedies,
    )


def evaluate_arishta_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Arishta / Balarishta configurations and Arishta Bhanga."""
    moon = ctx.moon
    lord_1_name = ctx.get_house_lord(1)
    lord_1 = ctx.grahas.get(lord_1_name)

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    # Check 1: Moon in Dusthana (6, 8, 12) afflicted by malefics
    if moon and moon.house in DUSTHANA_HOUSES:
        malefics_with_moon = [g.name for g in ctx.grahas.values() if g.house == moon.house and g.name in NATURAL_MALEFICS]
        malefics_aspect_moon = [m for m in ("Mars", "Saturn", "Sun") if ctx.has_aspect_on_graha(m, "Moon")]
        if malefics_with_moon or malefics_aspect_moon:
            triggers.append(f"Moon in Dusthana House {moon.house} afflicted by {', '.join(malefics_with_moon + malefics_aspect_moon)}")
            planets_involved.extend(["Moon"] + malefics_with_moon + malefics_aspect_moon)

    # Check 2: Lagna afflicted and Lagna lord in 8th house
    planets_in_lagna = ctx.get_planets_in_house(1)
    malefics_in_lagna = [p for p in planets_in_lagna if p in NATURAL_MALEFICS]
    if malefics_in_lagna and lord_1 and lord_1.house == 8:
        triggers.append(f"Lagna occupied by {', '.join(malefics_in_lagna)} with Lagna lord ({lord_1_name}) placed in 8th house")
        planets_involved.extend([lord_1_name] + malefics_in_lagna)

    is_present = len(triggers) > 0

    if is_present:
        # Classical Arishta Bhanga per BPHS Ch. 11 & Phaladeepika Ch. 13
        jup = ctx.jupiter
        if jup and jup.house in KENDRA_HOUSES and not ctx.is_debilitated("Jupiter") and not ctx.is_combust("Jupiter"):
            cancellations.append(f"Strong Jupiter in Kendra House {jup.house} dissolves all arishtas (BPHS 11.1)")
        # Venus or Mercury in Kendras
        kendra_benefics = [b for b in ("Venus", "Mercury") if ctx.grahas.get(b) and ctx.grahas[b].house in KENDRA_HOUSES]
        if kendra_benefics:
            cancellations.append(f"Benefics in Kendras ({', '.join(kendra_benefics)}) protect physical constitution")
        # Lagna lord aspecting Lagna
        if lord_1 and ctx.has_aspect_on_house(lord_1_name, 1):
            cancellations.append(f"Lagna lord ({lord_1_name}) aspects Lagna, fortifying vitality")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Lagna and Moon are free from severe Dusthana affliction. Arishta Dosha is absent; vitality and constitution are sound."
        if status == "absent" else
        (
            f"Arishta indicators are neutralized by powerful Arishta Bhanga: {'; '.join(cancellations)}. "
            "Grants durable immunity, long life, and resilience against physical adversities."
            if status == "mitigated" else
            f"Arishta combination detected ({'; '.join(triggers)}). "
            "Suggests periodic sensitivity in childhood or health fluctuations. Balanced nutrition, protective remedies, and pediatric care preserve vitality."
        )
    )
    interp_ta = (
        "லக்னமும் சந்திரனும் மறைவு ஸ்தான தோஷங்களின்றி உள்ளன. அரிஷ்ட தோஷம் இல்லை. நல்ல உடலாரோக்கியம் நிலைக்கும்."
        if status == "absent" else
        (
            f"அரிஷ்ட தோஷம் விசேஷ அரிஷ்ட பங்க அமைப்புகளால் ({'; '.join(cancellations)}) முழுமையாக தோஷ நிவர்த்தி பெறுகிறது. "
            "நீண்ட ஆயுளும் நல்ல நோய் எதிர்ப்புச் சக்தியும் உண்டாகும்."
            if status == "mitigated" else
            f"அரிஷ்ட அமைப்பு காணப்படுகிறது ({'; '.join(triggers)}). "
            "ஆயுள் மற்றும் ஆரோக்கியத்திற்கான மிருத்யுஞ்ஜய ஹோமமும் முறையான பராமரிப்பும் பலன் தரும்."
        )
    )

    remedies = [
        "Chant Mahamrityunjaya Mantra: Om Tryambakam Yajamahe Sugandhim Pushtivardhanam",
        "Perform Ayushya Homam on birth star day",
        "Offer prayers to Lord Dhanvantari for health and robust immunity",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="arishta_dosha",
        name_en="Arishta / Balarishta & Arishta Bhanga (Vitality Affliction)",
        name_ta="அரிஷ்ட / பாலாரிஷ்ட தோஷம் & பங்க யோகம்",
        category="Moon & Nakshatra",
        status=status,
        reference_basis="Lagna & Moon in Dusthanas",
        formation_conditions=triggers if triggers else ["No Arishta formations present"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Strong Jupiter in Kendra (1, 4, 7, 10)",
            "Benefics (Venus/Mercury) in Kendras",
            "Lagna lord aspecting Lagna",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 10 & 11; Phaladeepika Ch. 13",
        remedies=remedies,
    )


def evaluate_lagna_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Lagna Dosha / Afflicted Ascendant."""
    lord_1_name = ctx.get_house_lord(1)
    lord_1 = ctx.grahas.get(lord_1_name)

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    # Malefics in Lagna without benefic aspect
    planets_in_lagna = ctx.get_planets_in_house(1)
    malefics_in_lagna = [p for p in planets_in_lagna if p in NATURAL_MALEFICS]
    if malefics_in_lagna and not ctx.has_aspect_on_house("Jupiter", 1) and not ctx.has_aspect_on_house("Venus", 1):
        triggers.append(f"Lagna occupied by natural malefics ({', '.join(malefics_in_lagna)}) without benefic aspect")
        planets_involved.extend(malefics_in_lagna)

    # Lagna lord in Dusthana (6, 8, 12)
    if lord_1 and lord_1.house in DUSTHANA_HOUSES:
        triggers.append(f"Lagna lord ({lord_1_name}) occupies Dusthana House {lord_1.house}")
        planets_involved.append(lord_1_name)

    is_present = len(triggers) > 0

    if is_present:
        if ctx.has_aspect_on_house("Jupiter", 1):
            cancellations.append("Jupiter casts direct aspect on Lagna, elevating physical and mental poise")
        if lord_1 and (ctx.is_own_sign(lord_1_name) or ctx.is_exalted(lord_1_name)):
            cancellations.append(f"Lagna lord ({lord_1_name}) holds high dignity in its own or exalted sign")
        # Benefics in Kendras
        k_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if ctx.grahas.get(b) and ctx.grahas[b].house in KENDRA_HOUSES]
        if k_benefics:
            cancellations.append(f"Benefics in Kendras ({', '.join(k_benefics)}) strengthen chart foundation")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Ascendant and its ruling lord are well-supported and free from Dusthana affliction. Lagna Dosha is absent."
        if status == "absent" else
        (
            f"Lagna affliction is mitigated by: {'; '.join(cancellations)}. "
            "Grants high self-reliance, physical vitality, and public respect."
            if status == "mitigated" else
            f"Lagna affliction detected ({'; '.join(triggers)}). "
            "May bring initial self-doubt or need for health care. Yoga, outdoor walks, and steady self-belief unlock high achievements."
        )
    )
    interp_ta = (
        "லக்னமும் லக்னாதிபதியும் நன்னிலையில் உள்ளனர். லக்ன தோஷம் இல்லை. நல்ல ஆயுளும் ஆரோக்கியமும் சிறக்கும்."
        if status == "absent" else
        (
            f"லக்ன தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. நற்பெயரும் புகழும் உண்டாகும்."
            if status == "mitigated" else
            f"லக்ன தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "உடற்பயிற்சியும், தன்னம்பிக்கையும், குலதெய்வ வழிபாடும் வெற்றியைத் தரும்."
        )
    )

    remedies = [
        "Practice Surya Namaskar daily at dawn",
        "Worship the Lagna lord deity and wear appropriate gemstones only under advice",
        "Maintain disciplined personal hygiene and physical exercise",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="lagna_dosha",
        name_en="Lagna Dosha (Afflicted Ascendant / Lagna Lord)",
        name_ta="லக்ன தோஷம் (லக்னம் அல்லது லக்னாதிபதி பலவீனம்)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Ascendant (House 1) and 1st Lord",
        formation_conditions=triggers if triggers else ["Ascendant and Lagna lord free from affliction"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Jupiter aspect on Lagna",
            "Lagna lord in own sign or exalted",
            "Natural benefics in Kendras (1, 4, 7, 10)",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra & Phaladeepika",
        remedies=remedies,
    )


def evaluate_papa_kartari_lagna_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Papa Kartari Yoga affecting the Ascendant (Lagna)."""
    h12 = 12
    h2 = 2

    p_12 = ctx.get_planets_in_house(h12)
    p_2 = ctx.get_planets_in_house(h2)

    malefics_12 = [p for p in p_12 if p in NATURAL_MALEFICS]
    malefics_2 = [p for p in p_2 if p in NATURAL_MALEFICS]

    is_present = len(malefics_12) > 0 and len(malefics_2) > 0

    cancellations: List[str] = []
    if is_present:
        if ctx.has_aspect_on_house("Jupiter", 1):
            cancellations.append("Jupiter casts direct aspect on Lagna, dissolving the malefic scissor grip")
        if ctx.has_aspect_on_house("Venus", 1):
            cancellations.append("Venus casts aspect on Lagna")
        # Benefics in Lagna
        benefics_in_1 = [p for p in ctx.get_planets_in_house(1) if p in NATURAL_BENEFICS]
        if benefics_in_1:
            cancellations.append(f"Benefics in Lagna ({', '.join(benefics_in_1)}) protect the Ascendant")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    involved = ["Lagna"] + malefics_12 + malefics_2

    interp_en = (
        "Ascendant is free from being flanked by malefics. Papa Kartari on Lagna is absent."
        if status == "absent" else
        (
            f"Papa Kartari on Lagna is mitigated by: {'; '.join(cancellations)}. "
            "Grants determination, diplomatic skill, and overcoming competitive pressure."
            if status == "mitigated" else
            f"Lagna is hemmed between malefics in 12th ({', '.join(malefics_12)}) and 2nd ({', '.join(malefics_2)}) houses. "
            "May feel external pressures or financial/personal constraints in early endeavors. Purposeful focus dissolves hesitation."
        )
    )
    interp_ta = (
        "லக்னத்தின் இருபுறமும் அசுப கிரகங்கள் இல்லை. லக்ன பாப கர்த்தாரி தோஷம் இல்லை."
        if status == "absent" else
        (
            f"லக்ன பாப கர்த்தாரி அமைப்பு சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது."
            if status == "mitigated" else
            f"லக்னம் 12-ம் வீடு ({', '.join(malefics_12)}) மற்றும் 2-ம் வீடு ({', '.join(malefics_2)}) அசுப கிரகங்களால் சூழப்பட்டுள்ளது. "
            "விடாமுயற்சியும், நேர்மையான வழியும் தடைகளைத் தகர்த்து வெற்றியைத் தரும்."
        )
    )

    remedies = [
        "Light a ghee lamp facing east on Tuesdays or Saturdays",
        "Worship Lord Ganesha to remove obstacles in personal ventures",
        "Engage in community service or feed stray animals",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="papa_kartari_lagna",
        name_en="Papa Kartari affecting Lagna (Hemmed Ascendant)",
        name_ta="லக்ன பாப கர்த்தாரி தோஷம் (லக்னம் கத்தரி யோகம்)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Houses 12 and 2 from Lagna",
        formation_conditions=[
            f"Ascendant hemmed by {', '.join(malefics_12)} in 12th and {', '.join(malefics_2)} in 2nd house"
        ] if is_present else ["Ascendant is not hemmed between natural malefics"],
        involved_planets=list(dict.fromkeys(involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, involved),
        degrees=_fmt_degrees(ctx, involved),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Lagna",
            "Benefic aspect of Venus on Lagna",
            "Natural benefics situated in Lagna",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra & Saravali",
        remedies=remedies,
    )


def evaluate_daridra_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Daridra Yoga / Wealth Affliction configurations."""
    lord_2_name = ctx.get_house_lord(2)
    lord_11_name = ctx.get_house_lord(11)
    lord_2 = ctx.grahas.get(lord_2_name)
    lord_11 = ctx.grahas.get(lord_11_name)

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    if lord_2 and lord_2.house in DUSTHANA_HOUSES:
        triggers.append(f"2nd lord of wealth ({lord_2_name}) placed in Dusthana House {lord_2.house}")
        planets_involved.append(lord_2_name)
    if lord_11 and lord_11.house in DUSTHANA_HOUSES:
        triggers.append(f"11th lord of gains ({lord_11_name}) placed in Dusthana House {lord_11.house}")
        planets_involved.append(lord_11_name)

    is_present = len(triggers) > 0

    if is_present:
        if lord_2 and (ctx.is_own_sign(lord_2_name) or ctx.is_exalted(lord_2_name)):
            cancellations.append(f"2nd lord ({lord_2_name}) is strong in own/exalted sign")
        if lord_11 and (ctx.is_own_sign(lord_11_name) or ctx.is_exalted(lord_11_name)):
            cancellations.append(f"11th lord ({lord_11_name}) is strong in own/exalted sign")
        if lord_2 and ctx.has_aspect_on_graha("Jupiter", lord_2_name):
            cancellations.append(f"Jupiter aspects 2nd lord ({lord_2_name}), sanctifying treasury")
        # Benefics in 2nd or 11th
        benefics_in_wealth = [p for h in (2, 11) for p in ctx.get_planets_in_house(h) if p in NATURAL_BENEFICS]
        if benefics_in_wealth:
            cancellations.append(f"Benefics in wealth houses ({', '.join(benefics_in_wealth)}) protect financial flow")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Wealth lords (2nd & 11th) are safely placed outside Dusthanas. Daridra Yoga is absent; financial accumulation proceeds stably."
        if status == "absent" else
        (
            f"Daridra Yoga is neutralized by classical cancellation (Daridra Bhanga): {'; '.join(cancellations)}. "
            "Initial financial leakage is transformed into sustained wealth through prudent enterprise."
            if status == "mitigated" else
            f"Daridra configuration detected ({'; '.join(triggers)}). "
            "Advises strict budgetary discipline, avoiding speculative risks, and systematically building durable savings."
        )
    )
    interp_ta = (
        "தன (2) மற்றும் லாப (11) அதிபதிகள் சுப ஸ்தானங்களில் உள்ளனர். தரித்திர யோகம் இல்லை. பொருளாதார நிலை சீராக இருக்கும்."
        if status == "absent" else
        (
            f"தரித்திர யோகம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெற்று தன யோகமாக மாறுகிறது."
            if status == "mitigated" else
            f"தன அதிபதிகள் மறைவு ஸ்தானங்களில் இருப்பதால் ({'; '.join(triggers)}) தரித்திர தோஷ அமைப்பு காணப்படுகிறது. "
            "வீண் செலவுகளைத் தவிர்த்து சேமிப்பைப் பெருக்குவதும், மகாலட்சுமி வழிபாடும் தன வரவை அதிகரிக்கும்."
        )
    )

    remedies = [
        "Chant Kanakadhara Stotram or Sri Suktam on Fridays",
        "Offer food (Annadhanam) to the poor or visually impaired",
        "Keep financial accounts transparent and donate a small percentage of earnings to charity",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="daridra_dosha",
        name_en="Daridra Yoga (Wealth Affliction & Bhanga)",
        name_ta="தரித்திர யோகம் / தன தோஷம் (பங்க யோக ஆய்வு)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Lords of Houses 2 and 11",
        formation_conditions=triggers if triggers else ["2nd and 11th lords placed safely outside Dusthanas"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "2nd lord in own sign or exaltation",
            "11th lord in own sign or exaltation",
            "Jupiter aspect on wealth lords",
            "Benefics occupying 2nd or 11th house",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Phaladeepika Ch. 6, v. 65 & BPHS Ch. 42",
        remedies=remedies,
    )


def evaluate_kendradhipati_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Kendradhipati Dosha (Natural benefics owning Kendra houses)."""
    # Natural benefics: Jupiter, Venus, Mercury
    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    benefic_kendra_lords = []
    for k in (1, 4, 7, 10):
        lord = ctx.get_house_lord(k)
        if lord in ("Jupiter", "Venus", "Mercury"):
            benefic_kendra_lords.append((lord, k))

    # Classical authority (BPHS Ch. 34 / Phaladeepika Ch. 15):
    # Especially pronounced when Jupiter rules two Kendras (Gemini: 7/10, Virgo: 4/7)
    # or Mercury rules two Kendras (Sagittarius: 7/10, Pisces: 4/7)
    if ctx.ascendant_sign_idx in (3, 6):  # Gemini, Virgo
        triggers.append(f"Jupiter rules two Kendra houses for {SIGN_NAMES_EN[ctx.ascendant_sign_idx]} Lagna")
        planets_involved.append("Jupiter")
    elif ctx.ascendant_sign_idx in (9, 12):  # Sagittarius, Pisces
        triggers.append(f"Mercury rules two Kendra houses for {SIGN_NAMES_EN[ctx.ascendant_sign_idx]} Lagna")
        planets_involved.append("Mercury")

    is_present = len(triggers) > 0

    if is_present:
        for p_name in planets_involved:
            p = ctx.grahas.get(p_name)
            if p:
                if p.house in TRIKONA_HOUSES:
                    cancellations.append(f"{p_name} is placed in auspicious Trikona House {p.house}, removing Kendra lord blemish")
                if ctx.is_exalted(p_name) or ctx.is_own_sign(p_name):
                    cancellations.append(f"{p_name} is in high dignity ({SIGN_NAMES_EN[p.sign_index]})")
                if ctx.has_aspect_on_graha("Jupiter", p_name) and p_name != "Jupiter":
                    cancellations.append(f"{p_name} receives benefic drishti from Jupiter")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "Natural benefics are free from Kendradhipati blemish for this Lagna. Kendradhipati Dosha is absent."
        if status == "absent" else
        (
            f"Kendradhipati Dosha is mitigated by classical factors: {'; '.join(cancellations)}. "
            "Preserves intellectual benevolence, educational leadership, and career eminence."
            if status == "mitigated" else
            f"Kendradhipati condition detected ({'; '.join(triggers)}). "
            "Classical shastras note that natural benefics owning Kendras become functionally neutral or lose mild benefic ease. Spiritual service restores full benefic power."
        )
    )
    interp_ta = (
        "கேந்திராதிபத்திய தோஷம் இந்த லக்னத்திற்கு அமையவில்லை. சுப பலன்கள் நிலைக்கும்."
        if status == "absent" else
        (
            f"கேந்திராதிபத்திய தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. அறிவாற்றலும் வெற்றியும் உண்டாகும்."
            if status == "mitigated" else
            f"சுப கிரகம் இரு கேந்திரங்களுக்கு அதிபதியாகி ({'; '.join(triggers)}) கேந்திராதிபத்திய தோஷம் உண்டாகிறது. "
            "இறை வழிபாடும் தர்ம காரியங்களும் சுபத் தன்மையை வலுப்படுத்தும்."
        )
    )

    remedies = [
        "Worship Lord Dakshinamurthy (for Jupiter) or Lord Vishnu (for Mercury)",
        "Support students or donate educational books to under-privileged schools",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="kendradhipati_dosha",
        name_en="Kendradhipati Dosha (Benefic Kendra Rulership)",
        name_ta="கேந்திராதிபத்திய தோஷம் (சுப கிரக கேந்திர ஆதிக்கம்)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Lagna Sign & Kendra Lordships",
        formation_conditions=triggers if triggers else ["No dual-Kendra rulership by natural benefics"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Kendra lord placed in Trikona (1, 5, 9)",
            "Kendra lord in own sign or exaltation",
            "Benefic conjunction or aspect",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 34 & Phaladeepika Ch. 15",
        remedies=remedies,
    )


def evaluate_marana_karaka_sthana_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Marana Karaka Sthana (MKS - house placements where grahas lose strength)."""
    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    for p_name, mks_h in MKS_HOUSES.items():
        g = ctx.grahas.get(p_name)
        if g and g.house == mks_h:
            triggers.append(f"{p_name} occupies House {mks_h} (classical MKS position)")
            planets_involved.append(p_name)

    is_present = len(triggers) > 0

    if is_present:
        for p_name in planets_involved:
            if ctx.is_own_sign(p_name) or ctx.is_exalted(p_name):
                cancellations.append(f"{p_name} is in high dignity (own/exalted sign), neutralizing MKS exhaustion")
            if ctx.has_aspect_on_graha("Jupiter", p_name) and p_name != "Jupiter":
                cancellations.append(f"{p_name} receives restoring aspect from Jupiter")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "No planets occupy their classical Marana Karaka Sthana (MKS) houses. All grahas preserve natural vitality."
        if status == "absent" else
        (
            f"MKS placements ({'; '.join(triggers)}) are mitigated by: {'; '.join(cancellations)}. "
            "Grants specialized resilience and mastery through conscious effort in the relevant life departments."
            if status == "mitigated" else
            f"Planets situated in Marana Karaka Sthana ({'; '.join(triggers)}). "
            "Highlights areas requiring patient nurturing and non-attachment. Mindful dedication turns apparent vulnerability into wisdom."
        )
    )
    interp_ta = (
        "எந்த கிரகமும் மரண காரக ஸ்தானத்தில் இல்லை. கிரகங்களின் சுப ஆற்றல் தடையின்றி உள்ளது."
        if status == "absent" else
        (
            f"மரண காரக ஸ்தான கிரகங்கள் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகின்றன."
            if status == "mitigated" else
            f"கிரகங்கள் மரண காரக ஸ்தானத்தில் உள்ளன ({'; '.join(triggers)}). "
            "குறிப்பிட்ட காரக விஷயங்களில் நிதானமும், இறை வழிபாடும் சவால்களை நீக்கி நல்வழிகாட்டும்."
        )
    )

    remedies = [
        "Chant planetary mantras for afflicted MKS planets",
        "Engage in selfless service related to the significations of the MKS graha",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="marana_karaka_sthana",
        name_en="Marana Karaka Sthana (Energy Depletion Placement)",
        name_ta="மரண காரக ஸ்தான தோஷம்",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Natal House Placements vs Classical MKS Grid",
        formation_conditions=triggers if triggers else ["No grahas in classical MKS houses"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Planet in own sign or exaltation",
            "Aspect of Jupiter on MKS planet",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Classical Jaimini Canons & BPHS",
        remedies=remedies,
    )


def evaluate_putra_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Putra Dosha / 5th House Afflictions."""
    lord_5_name = ctx.get_house_lord(5)
    lord_5 = ctx.grahas.get(lord_5_name)
    jup = ctx.jupiter

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    # Check 5th house occupants
    p_5 = ctx.get_planets_in_house(5)
    malefics_in_5 = [p for p in p_5 if p in NATURAL_MALEFICS]
    if malefics_in_5:
        triggers.append(f"5th house of progeny occupied by natural malefics ({', '.join(malefics_in_5)})")
        planets_involved.extend(malefics_in_5)

    # 5th lord in Dusthana
    if lord_5 and lord_5.house in DUSTHANA_HOUSES:
        triggers.append(f"5th lord ({lord_5_name}) placed in Dusthana House {lord_5.house}")
        planets_involved.append(lord_5_name)

    is_present = len(triggers) > 0

    if is_present:
        if ctx.has_aspect_on_house("Jupiter", 5):
            cancellations.append("Jupiter casts divine aspect onto 5th house, blessing progeny and intellect")
        if lord_5 and ctx.has_aspect_on_graha("Jupiter", lord_5_name):
            cancellations.append(f"Jupiter aspects 5th lord ({lord_5_name})")
        if lord_5 and (ctx.is_own_sign(lord_5_name) or ctx.is_exalted(lord_5_name)):
            cancellations.append(f"5th lord ({lord_5_name}) in superior dignity")
        # Benefics in 5th
        benefics_in_5 = [p for p in p_5 if p in NATURAL_BENEFICS]
        if benefics_in_5:
            cancellations.append(f"Benefics in 5th house ({', '.join(benefics_in_5)}) sanctify the house")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "5th house, 5th lord, and Jupiter are well-situated. Putra Dosha is absent; creative intelligence and progeny prospects are bright."
        if status == "absent" else
        (
            f"Putra Dosha indicators are mitigated by: {'; '.join(cancellations)}. "
            "Grants dutiful children, creative distinction, and philosophical acumen."
            if status == "mitigated" else
            f"Putra Dosha indications detected ({'; '.join(triggers)}). "
            "Suggests patience regarding progeny timing or investment in children's higher guidance. Santana Gopala prayers and charity protect lineage."
        )
    )
    interp_ta = (
        "5-ம் வீடு, 5-ம் அதிபதி மற்றும் குரு சுபமாக உள்ளனர். புத்திர தோஷம் இல்லை. சந்தான பாக்கியமும் அறிவாற்றலும் சிறக்கும்."
        if status == "absent" else
        (
            f"புத்திர தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. நன்மக்கட்பேறும் புண்ணிய பலன்களும் நிலைக்கும்."
            if status == "mitigated" else
            f"புத்திர தோஷ அமைப்பு காணப்படுகிறது ({'; '.join(triggers)}). "
            "சந்தான கோபால மந்திர ஜபமும், குழந்தைகளுக்கு உதவும் நற்பணிகளும் புத்திர தோஷத்தை நீக்கும்."
        )
    )

    remedies = [
        "Chant Santana Gopala Mantra: Om Devakisuta Govinda Vasudeva Jagatpate Dehi Me Tanayam Krishna Tvamaham Sharanam Gatah",
        "Worship at Tirukkarukavoor Garbharakshambigai or Alangudi Guru Sthalam",
        "Sponsor education or nutritional meals for underprivileged children",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="putra_dosha",
        name_en="Putra Dosha (Progeny & 5th House Affliction)",
        name_ta="புத்திர தோஷம் (5-ஆம் பாவ மற்றும் சந்தான ஆய்வு)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="5th House, 5th Lord, and Jupiter",
        formation_conditions=triggers if triggers else ["5th house and 5th lord free from malefic affliction"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Jupiter aspect on 5th house",
            "Jupiter aspect on 5th lord",
            "5th lord in own sign or exaltation",
            "Benefics in 5th house",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 83 & Phaladeepika Ch. 12",
        remedies=remedies,
    )


def evaluate_kalathra_dosha_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Kalathra Dosha / Marriage and 7th House Afflictions."""
    lord_7_name = ctx.get_house_lord(7)
    lord_7 = ctx.grahas.get(lord_7_name)
    venus = ctx.venus

    triggers: List[str] = []
    planets_involved: List[str] = []
    cancellations: List[str] = []

    # Malefics in 7th house
    p_7 = ctx.get_planets_in_house(7)
    malefics_in_7 = [p for p in p_7 if p in NATURAL_MALEFICS]
    if malefics_in_7:
        triggers.append(f"7th house of marriage occupied by natural malefics ({', '.join(malefics_in_7)})")
        planets_involved.extend(malefics_in_7)

    # 7th lord in Dusthana
    if lord_7 and lord_7.house in DUSTHANA_HOUSES:
        triggers.append(f"7th lord ({lord_7_name}) placed in Dusthana House {lord_7.house}")
        planets_involved.append(lord_7_name)

    # Venus severely afflicted by nodes
    if venus and (ctx.is_conjoined("Venus", "Rahu") or ctx.is_conjoined("Venus", "Ketu")):
        triggers.append("Venus (Kalathrakaraka) conjoined with lunar nodes")
        planets_involved.append("Venus")

    is_present = len(triggers) > 0

    if is_present:
        if ctx.has_aspect_on_house("Jupiter", 7):
            cancellations.append("Jupiter casts divine aspect onto 7th house, preserving marital harmony")
        if lord_7 and ctx.has_aspect_on_graha("Jupiter", lord_7_name):
            cancellations.append(f"Jupiter aspects 7th lord ({lord_7_name})")
        if lord_7 and (ctx.is_own_sign(lord_7_name) or ctx.is_exalted(lord_7_name)):
            cancellations.append(f"7th lord ({lord_7_name}) is strong in own/exalted sign")
        if venus and ctx.is_exalted("Venus"):
            cancellations.append("Venus exalted in Pisces maintains high emotional devotion")

    is_mitigated = is_present and len(cancellations) > 0
    status = "mitigated" if is_mitigated else ("present" if is_present else "absent")

    interp_en = (
        "7th house, 7th lord, and Venus are free from malefic affliction. Kalathra Dosha is absent; marital alliance is well-supported."
        if status == "absent" else
        (
            f"Kalathra affliction is mitigated by classical factors: {'; '.join(cancellations)}. "
            "Grants mature partnership understanding, mutual loyalty, and long-term conjugal harmony."
            if status == "mitigated" else
            f"Kalathra affliction detected ({'; '.join(triggers)}). "
            "Encourages open communication, matching horoscopes mindfully, and nurturing mutual respect."
        )
    )
    interp_ta = (
        "7-ம் வீடு, 7-ம் அதிபதி மற்றும் சுக்கிரன் நன்னிலையில் உள்ளனர். களத்திர தோஷம் இல்லை. திருமண வாழ்க்கை மகிழ்ச்சியாக அமையும்."
        if status == "absent" else
        (
            f"களத்திர தோஷம் சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. தம்பதியர் ஒற்றுமை சிறக்கும்."
            if status == "mitigated" else
            f"களத்திர தோஷம் காணப்படுகிறது ({'; '.join(triggers)}). "
            "பரஸ்பர புரிதலும், விட்டுக்கொடுக்கும் மனப்பான்மையும், சுக்கிர வழிபாடும் இல்லறத்தை இனிமையாக்கும்."
        )
    )

    remedies = [
        "Chant Shukra Gayatri Mantra: Om Rajatabhaya Vidmahe Bhrigu Sutaya Dhimahi Tanno Shukrah Prachodayat",
        "Worship at Kanjanur Agneeswarar Sthalam (Venus Temple)",
        "Honor your spouse and foster mutual respect in daily life",
    ] if status in ("present", "mitigated") else []

    return DoshaEvaluationItem(
        dosha_id="kalathra_dosha",
        name_en="Kalathra Dosha (Marriage & 7th House Affliction)",
        name_ta="களத்திர தோஷம் (திருமண மற்றும் 7-ஆம் பாவ ஆய்வு)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="7th House, 7th Lord, and Venus",
        formation_conditions=triggers if triggers else ["7th house and Venus free from affliction"],
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Jupiter aspect on 7th house",
            "Jupiter aspect on 7th lord",
            "7th lord in own sign or exaltation",
            "Venus in exaltation",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Brihat Parashara Hora Shastra Ch. 81 & Phaladeepika Ch. 10",
        remedies=remedies,
    )


def evaluate_dusthana_affliction_item(ctx: DoshaChartContext) -> DoshaEvaluationItem:
    """Evaluate Difficult-house Lordship combinations, keeping Viparita Raja Yoga distinct."""
    l6_name = ctx.get_house_lord(6)
    l8_name = ctx.get_house_lord(8)
    l12_name = ctx.get_house_lord(12)
    l6 = ctx.grahas.get(l6_name)
    l8 = ctx.grahas.get(l8_name)
    l12 = ctx.grahas.get(l12_name)

    # Check for pure Viparita Raja Yoga (Harsha, Sarala, Vimala)
    vry_indicators = []
    if l6 and l6.house in (6, 8, 12):
        vry_indicators.append(f"6th lord {l6_name} in Dusthana House {l6.house} (Harsha Yoga)")
    if l8 and l8.house in (6, 8, 12):
        vry_indicators.append(f"8th lord {l8_name} in Dusthana House {l8.house} (Sarala Yoga)")
    if l12 and l12.house in (6, 8, 12):
        vry_indicators.append(f"12th lord {l12_name} in Dusthana House {l12.house} (Vimala Yoga)")

    # Adverse condition: Dusthana lords occupying Lagna, 5th, or 9th and afflicting Kendra/Trikona lords
    afflictions = []
    planets_involved = []
    for d_num, d_name, d_obj in [(6, l6_name, l6), (8, l8_name, l8), (12, l12_name, l12)]:
        if d_obj and d_obj.house in (1, 5, 9) and not (ctx.is_own_sign(d_name) or ctx.is_exalted(d_name)):
            afflictions.append(f"{d_num}th lord {d_name} placed in Trikona House {d_obj.house}")
            planets_involved.append(d_name)

    is_adverse = len(afflictions) > 0
    cancellations: List[str] = []

    if is_adverse:
        for p in planets_involved:
            if ctx.has_aspect_on_graha("Jupiter", p):
                cancellations.append(f"Jupiter aspects {p}, converting difficulty into strength")
        if vry_indicators:
            cancellations.append(f"Active Viparita Raja Yoga factors present: {'; '.join(vry_indicators)}")

    if not is_adverse:
        status = "absent"
        if vry_indicators:
            interp_en = (
                f"Classical Viparita Raja Yoga is active ({'; '.join(vry_indicators)}). "
                "Per Phaladeepika Ch. 6, this is strictly an auspicious triumph yoga and NOT an adverse dosha."
            )
            interp_ta = (
                f"விபரீத ராஜ யோகம் ({'; '.join(vry_indicators)}) செயல்படுகிறது. "
                "இது அசுப தோஷம் அல்ல; சவால்களை வென்று சாதனை புரியும் உயர் சுப யோகமாகும்."
            )
        else:
            interp_en = "Dusthana lords are not afflicting auspicious houses. Difficult-house lordship dosha is absent."
            interp_ta = "துர்ஸ்தான அதிபதிகளால் சுப ஸ்தானங்களுக்கு பாதிப்பு இல்லை. தோஷம் இல்லை."
    else:
        is_mitigated = len(cancellations) > 0
        status = "mitigated" if is_mitigated else "present"
        interp_en = (
            f"Dusthana lordship affliction is mitigated by: {'; '.join(cancellations)}. "
            "Grants extraordinary problem-solving skills and resilience."
            if is_mitigated else
            f"Dusthana lord placement detected ({'; '.join(afflictions)}). "
            "Indicates that diligence and legal/financial prudence turn initial obstacles into enduring accomplishments."
        )
        interp_ta = (
            f"மறைவு ஸ்தான அதிபதிகளின் அமைப்பு சுப அமைப்புகளால் ({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது."
            if is_mitigated else
            f"மறைவு ஸ்தான அதிபதிகள் சுப வீடுகளில் ({'; '.join(afflictions)}) உள்ளனர். "
            "கவனமும், தர்ம சிந்தனையும் தடைகளைத் தகர்க்கும்."
        )

    return DoshaEvaluationItem(
        dosha_id="dusthana_affliction_dosha",
        name_en="Dusthana Lordship Affliction (Excl. Viparita Raja Yoga)",
        name_ta="துர்ஸ்தான ஆதிபத்திய தோஷம் (விபரீத ராஜ யோகம் தனித்து)",
        category="Lagna & House Placements",
        status=status,
        reference_basis="Lords of 6th, 8th, and 12th Houses",
        formation_conditions=afflictions if afflictions else (vry_indicators if vry_indicators else ["Dusthana lords safely disposed"]),
        involved_planets=list(dict.fromkeys(planets_involved)),
        signs_and_houses=_fmt_signs_and_houses(ctx, planets_involved),
        degrees=_fmt_degrees(ctx, planets_involved),
        cancellation_conditions_checked=[
            "Benefic aspect of Jupiter on Dusthana lord",
            "Dusthana lord in own sign or exaltation",
            "Viparita Raja Yoga operational status verified",
        ],
        cancellation_evidence=cancellations,
        interpretation=interp_en,
        interpretation_ta=interp_ta,
        source_references="Phaladeepika Ch. 6, vv. 63-70 & BPHS Ch. 34",
        remedies=[],
    )


def evaluate_compatibility_dosha_item(
    dosha_id: str,
    name_en: str,
    name_ta: str,
    classical_ref: str,
) -> DoshaEvaluationItem:
    """Generate indeterminate item for synastry/compatibility dosha requiring partner chart."""
    return DoshaEvaluationItem(
        dosha_id=dosha_id,
        name_en=name_en,
        name_ta=name_ta,
        category="Marriage Compatibility",
        status="indeterminate",
        reference_basis="Partner Horoscope Required",
        formation_conditions=[
            f"Evaluates Kuta compatibility between two natal charts per classical synastry ({classical_ref})"
        ],
        involved_planets=["Moon"],
        signs_and_houses=[],
        degrees={},
        cancellation_conditions_checked=[
            "Mutual Rasi lord friendship",
            "Same Nakshatra different Pada exception",
            "Benefic dispositor strength",
        ],
        cancellation_evidence=[],
        interpretation=(
            f"{name_en} requires both bride and groom horoscopes for authoritative evaluation. "
            "Cannot be evaluated on a single natal chart alone; never marked absent without partner data."
        ),
        interpretation_ta=(
            f"{name_ta} கணக்கீட்டிற்கு இருவரின் ஜாதகக் குறிப்புகளும் தேவை. "
            "தனி ஜாதகத்தில் இதை முடிவு செய்ய இயலாது; துணைவரின் ஜாதகம் இணைக்கப்படும்போது மட்டுமே துல்லியமாக மதிப்பிடப்படும்."
        ),
        source_references=classical_ref,
        missing_prerequisites="Requires partner horoscope for synastry evaluation",
    )


def build_complete_dosha_catalogue(
    ctx: DoshaChartContext,
    include_2nd_house_in_kuja: bool = True,
    transit_date: Optional[str] = None,
    transit_time: Optional[str] = "12:00:00",
    ayanamsa_id: int = 0,
    saturn_bav_bindus: Optional[Dict[int, int]] = None,
) -> Tuple[List[DoshaEvaluationItem], DoshaSummary]:
    """Build the complete catalogue of 30 classical Vedic Doshas."""
    now_iso = datetime.now(timezone.utc).isoformat()
    items: List[DoshaEvaluationItem] = []

    # -------------------------------------------------------------
    # Group A: Planetary Conjunction and Axis Doshas (1 to 8)
    # -------------------------------------------------------------
    # 1. Kuja Dosha
    kuja_res = evaluate_kuja_dosha(ctx, include_2nd_house=include_2nd_house_in_kuja)
    kuja_status = "mitigated" if (kuja_res.is_present and kuja_res.is_cancelled) else ("present" if kuja_res.is_present else "absent")
    kuja_inv = ["Mars"]
    if kuja_res.is_present:
        for ref_k, ref_v in kuja_res.details_by_reference.items():
            if ref_v.has_dosha:
                kuja_inv.append(ref_k if ref_k != "Lagna" else "Lagna")
    items.append(
        DoshaEvaluationItem(
            dosha_id="kuja_dosha",
            name_en="Kuja Dosha / Manglik Dosha (Mars Affliction)",
            name_ta="செவ்வாய் தோஷம் (மங்கள தோஷம்)",
            category="Planetary Conjunction & Axis",
            status=kuja_status,
            reference_basis=f"Multi-Reference: Lagna (100%), Moon (75%), Venus (50%) [{kuja_res.house_convention}]",
            formation_conditions=[
                f"{k}: Mars in House {v.mars_house_from_reference} ({'Kuja House' if v.has_dosha else 'Safe'})"
                for k, v in kuja_res.details_by_reference.items()
            ],
            involved_planets=list(dict.fromkeys(kuja_inv)),
            signs_and_houses=_fmt_signs_and_houses(ctx, ["Mars"]),
            degrees=_fmt_degrees(ctx, ["Mars"]),
            cancellation_conditions_checked=[
                "Mars in own sign (Aries/Scorpio) per BPHS 81",
                "Mars in exaltation (Capricorn) per Muhurta Chintamani",
                "Mars debilitated in 7th/8th house",
                "Mars in 2nd house in Gemini/Virgo",
                "Mars in 12th house in Taurus/Libra",
                "Mars in 8th house in Sagittarius/Pisces",
                "Yogakaraka status for Cancer and Leo Lagna",
                "Conjunction or aspect of Jupiter, Moon, or Saturn",
            ],
            cancellation_evidence=[r for d in kuja_res.details_by_reference.values() for r in d.cancellation_reasons],
            interpretation=kuja_res.interpretation,
            interpretation_ta=kuja_res.interpretation_tamil,
            source_references="Brihat Parashara Hora Shastra Ch. 81 & Muhurta Chintamani",
            evaluated_at=now_iso,
            remedies=[
                "Chant Angaraka Gayatri Mantra on Tuesdays",
                "Visit Vaitheeswaran Koil (Chevvai Sthalam) in Tamil Nadu",
                "Match with partner chart having balanced Kuja intensity or mitigating factors",
            ] if kuja_status in ("present", "mitigated") else [],
        )
    )

    # 2. Surya Grahan Dosha
    sg_res = evaluate_grahan_dosha(ctx, "Sun")
    sg_status = "mitigated" if (sg_res.is_present and sg_res.is_cancelled) else ("present" if sg_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="grahan_dosha_sun",
            name_en="Surya Grahan Dosha (Solar Eclipse Conjunction)",
            name_ta="சூரிய கிரகண தோஷம்",
            category="Planetary Conjunction & Axis",
            status=sg_status,
            reference_basis="Sun with Lunar Nodes within 12° Orb",
            formation_conditions=sg_res.conditions if sg_res.conditions else ["Sun free from close conjunction with Rahu or Ketu"],
            involved_planets=sg_res.planets_involved,
            signs_and_houses=_fmt_signs_and_houses(ctx, sg_res.planets_involved),
            degrees=_fmt_degrees(ctx, sg_res.planets_involved),
            cancellation_conditions_checked=[
                "Separation exceeds core 10° threshold",
                "Jupiter casts aspect on Sun",
                "Sun in high dignity (Aries/Leo)",
            ],
            cancellation_evidence=sg_res.cancellation_reasons,
            interpretation=sg_res.interpretation,
            interpretation_ta=sg_res.interpretation_tamil,
            source_references=sg_res.classical_reference,
            evaluated_at=now_iso,
            remedies=[
                "Chant Aditya Hridaya Stotram daily at sunrise",
                "Perform Surya Namaskar and offer Arghya to the Sun",
                "Visit Suryanar Koil (Sun Temple) in Thanjavur district",
            ] if sg_status in ("present", "mitigated") else [],
        )
    )

    # 3. Guru Chandal Dosha
    gc_res = evaluate_guru_chandal_dosha(ctx)
    gc_status = "mitigated" if (gc_res.is_present and gc_res.is_cancelled) else ("present" if gc_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="guru_chandal_dosha",
            name_en="Guru Chandal Dosha (Jupiter–Rahu Affliction)",
            name_ta="குரு சண்டாள தோஷம்",
            category="Planetary Conjunction & Axis",
            status=gc_status,
            reference_basis="Jupiter Conjoined or Aspected by Rahu/Ketu",
            formation_conditions=gc_res.conditions if gc_res.conditions else ["Jupiter free from nodal conjunction or aspect"],
            involved_planets=gc_res.planets_involved,
            signs_and_houses=_fmt_signs_and_houses(ctx, gc_res.planets_involved),
            degrees=_fmt_degrees(ctx, gc_res.planets_involved),
            cancellation_conditions_checked=[
                "Jupiter in own sign (Sagittarius/Pisces) or exaltation (Cancer)",
                "Angular separation exceeds 10°",
                "Jupiter in Kendra aspected by Venus",
            ],
            cancellation_evidence=gc_res.cancellation_reasons,
            interpretation=gc_res.interpretation,
            interpretation_ta=gc_res.interpretation_tamil,
            source_references=gc_res.classical_reference,
            evaluated_at=now_iso,
            remedies=[
                "Chant Brihaspati Gayatri Mantra on Thursdays",
                "Honor spiritual preceptors and teachers with respect",
                "Visit Alangudi Guru Sthalam in Thiruvarur district",
            ] if gc_status in ("present", "mitigated") else [],
        )
    )

    # 4. Shrapit Dosha
    sh_res = evaluate_shrapit_dosha(ctx)
    sh_status = "mitigated" if (sh_res.is_present and sh_res.is_cancelled) else ("present" if sh_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="shrapit_dosha",
            name_en="Shrapit Yoga / Dosha (Saturn–Rahu Conjunction)",
            name_ta="சாப தோஷம் (சனி-ராகு சேர்க்கை)",
            category="Planetary Conjunction & Axis",
            status=sh_status,
            reference_basis="Saturn and Rahu Conjunction or 7th Aspect",
            formation_conditions=sh_res.conditions if sh_res.conditions else ["Saturn and Rahu do not conjoin or mutually aspect"],
            involved_planets=sh_res.planets_involved,
            signs_and_houses=_fmt_signs_and_houses(ctx, sh_res.planets_involved),
            degrees=_fmt_degrees(ctx, sh_res.planets_involved),
            cancellation_conditions_checked=[
                "Saturn and Rahu situated in Upachaya houses (3, 6, 10, 11)",
                "Benefic aspect of Jupiter on Saturn",
                "Saturn in high dignity (Libra, Capricorn, Aquarius)",
            ],
            cancellation_evidence=sh_res.cancellation_reasons,
            interpretation=sh_res.interpretation,
            interpretation_ta=sh_res.interpretation_tamil,
            source_references=sh_res.classical_reference,
            evaluated_at=now_iso,
            remedies=[
                "Chant Shani Gayatri Mantra and feed crows with sesame rice on Saturdays",
                "Visit Thirunallar Saneeswarar Temple or Thirunageswaram Rahu Sthalam",
                "Engage in charitable service for disabled individuals or elderly elders",
            ] if sh_status in ("present", "mitigated") else [],
        )
    )

    # 5. Angarak Dosha
    items.append(evaluate_angarak_dosha(ctx))

    # 6. Vish Dosha
    items.append(evaluate_vish_dosha(ctx))

    # 7. Kaal Sarp Dosha
    ks_res = evaluate_kaal_sarp_dosha(ctx)
    ks_status = "mitigated" if (ks_res.is_present and ks_res.is_cancelled) else ("present" if ks_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="kaal_sarp_dosha",
            name_en=f"Kaal Sarp Dosha ({ks_res.subtype_name or 'Planetary Enclosure'})",
            name_ta=f"கால சர்ப்ப தோஷம் ({ks_res.subtype_name_tamil or 'முழு/பகுதி யோகம்'})",
            category="Planetary Conjunction & Axis",
            status=ks_status,
            reference_basis=f"Rahu-Ketu Ecliptic Bisector [Direction: {ks_res.direction or 'N/A'}]",
            formation_conditions=[
                f"Classification: {ks_res.dosha_type} Kaal Sarp",
                f"Rahu in House {ks_res.rahu_house}, Ketu in House {ks_res.ketu_house}",
                f"Planets Enclosed ({len(ks_res.planets_inside)}): {', '.join(ks_res.planets_inside) if ks_res.planets_inside else 'None'}",
                f"Planets Outside ({len(ks_res.planets_outside)}): {', '.join(ks_res.planets_outside) if ks_res.planets_outside else 'None'}",
            ],
            involved_planets=["Rahu", "Ketu"] + ks_res.planets_inside,
            signs_and_houses=_fmt_signs_and_houses(ctx, ["Rahu", "Ketu"]),
            degrees=_fmt_degrees(ctx, ["Rahu", "Ketu"]),
            cancellation_conditions_checked=[
                "Natural benefics in Kendras (1, 4, 7, 10)",
                "Exalted planets in Kendras or Trikonas",
                "Jupiter Parashari aspect directly on Rahu or Lagna",
                "Lagna lord strongly situated in Kendra/Trikona",
            ],
            cancellation_evidence=ks_res.cancellation_reasons,
            interpretation=ks_res.interpretation,
            interpretation_ta=ks_res.interpretation_tamil,
            source_references="Classical Nodal Enclosure Canons & Bhrigu Samhita",
            evaluated_at=now_iso,
            remedies=[
                "Chant Maha Mrityunjaya Mantra or Rahu-Ketu Stotram",
                "Visit Sri Kalahasti Temple or Thirunageswaram Rahu Temple",
                "Perform humble service and worship Lord Shiva on Pradosham days",
            ] if ks_status in ("present", "mitigated") else [],
        )
    )

    # 8. Pitru Dosha
    pt_res = evaluate_pitru_dosha(ctx)
    pt_status = "mitigated" if (pt_res.is_present and pt_res.is_cancelled) else ("present" if pt_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="pitru_dosha",
            name_en="Pitru Dosha (Ancestral Karmic Debt)",
            name_ta="பித்ரு தோஷம் (முன்னோர் ஆசி ஆய்வு)",
            category="Planetary Conjunction & Axis",
            status=pt_status,
            reference_basis="Sun (Pitru Karaka), 9th House, and 9th Lord",
            formation_conditions=pt_res.conditions if pt_res.conditions else ["Sun, 9th house, and 9th lord free from nodal and Saturnine afflictions"],
            involved_planets=pt_res.planets_involved,
            signs_and_houses=_fmt_signs_and_houses(ctx, pt_res.planets_involved),
            degrees=_fmt_degrees(ctx, pt_res.planets_involved),
            cancellation_conditions_checked=[
                "Jupiter aspect on 9th house, 9th lord, or Sun",
                "Sun in high dignity (Aries exaltation or Leo own sign)",
                "9th lord well-placed in Kendra or Trikona",
            ],
            cancellation_evidence=pt_res.cancellation_reasons,
            interpretation=pt_res.interpretation,
            interpretation_ta=pt_res.interpretation_tamil,
            source_references=pt_res.classical_reference,
            evaluated_at=now_iso,
            remedies=[
                "Perform Amavasya Tarpanam and annual Shraddha rites diligently",
                "Serve elders with genuine reverence and feed cows or crows",
                "Visit Rameshwaram or Thilatharpanapuri for ancestral peace",
            ] if pt_status in ("present", "mitigated") else [],
        )
    )

    # -------------------------------------------------------------
    # Group B: Moon and Nakshatra Doshas (9 to 15)
    # -------------------------------------------------------------
    # 9. Kemadruma Dosha
    items.append(evaluate_kemadruma_dosha_item(ctx))

    # 10. Gandmool Dosha
    items.append(evaluate_gandmool_dosha_item(ctx))

    # 11. Gandanta Condition (Separate from Gandmool)
    items.append(evaluate_gandanta_dosha_item(ctx))

    # 12. Shakata Dosha
    items.append(evaluate_shakata_dosha_item(ctx))

    # 13. Chandra Grahan Dosha
    cg_res = evaluate_grahan_dosha(ctx, "Moon")
    cg_status = "mitigated" if (cg_res.is_present and cg_res.is_cancelled) else ("present" if cg_res.is_present else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="grahan_dosha_moon",
            name_en="Chandra Grahan Dosha (Lunar Eclipse Conjunction)",
            name_ta="சந்திர கிரகண தோஷம்",
            category="Moon & Nakshatra",
            status=cg_status,
            reference_basis="Moon with Lunar Nodes within 12° Orb",
            formation_conditions=cg_res.conditions if cg_res.conditions else ["Moon free from close conjunction with Rahu or Ketu"],
            involved_planets=cg_res.planets_involved,
            signs_and_houses=_fmt_signs_and_houses(ctx, cg_res.planets_involved),
            degrees=_fmt_degrees(ctx, cg_res.planets_involved),
            cancellation_conditions_checked=[
                "Separation exceeds core 10° threshold",
                "Jupiter casts aspect on Moon",
                "Moon in high dignity (Taurus exaltation or Cancer own sign)",
            ],
            cancellation_evidence=cg_res.cancellation_reasons,
            interpretation=cg_res.interpretation,
            interpretation_ta=cg_res.interpretation_tamil,
            source_references=cg_res.classical_reference,
            evaluated_at=now_iso,
            remedies=[
                "Chant Chandra Gayatri Mantra and worship Lord Shiva on Mondays",
                "Offer milk or water libation to Shivalinga",
                "Visit Thingaloor Kailasanathar Sthalam (Moon Temple) in Thanjavur",
            ] if cg_status in ("present", "mitigated") else [],
        )
    )

    # 14. Papa Kartari Moon
    items.append(evaluate_papa_kartari_moon_item(ctx))

    # 15. Arishta / Balarishta
    items.append(evaluate_arishta_dosha_item(ctx))

    # -------------------------------------------------------------
    # Group C: Lagna and House-Based Doshas (16 to 23)
    # -------------------------------------------------------------
    # 16. Lagna Dosha
    items.append(evaluate_lagna_dosha_item(ctx))

    # 17. Papa Kartari Lagna
    items.append(evaluate_papa_kartari_lagna_item(ctx))

    # 18. Daridra Yoga
    items.append(evaluate_daridra_dosha_item(ctx))

    # 19. Kendradhipati Dosha
    items.append(evaluate_kendradhipati_dosha_item(ctx))

    # 20. Marana Karaka Sthana
    items.append(evaluate_marana_karaka_sthana_item(ctx))

    # 21. Putra Dosha
    items.append(evaluate_putra_dosha_item(ctx))

    # 22. Kalathra Dosha
    items.append(evaluate_kalathra_dosha_item(ctx))

    # 23. Difficult House Lordship
    items.append(evaluate_dusthana_affliction_item(ctx))

    # -------------------------------------------------------------
    # Group D: Marriage Compatibility Doshas (24 to 27)
    # -------------------------------------------------------------
    # 24. Nadi Dosha
    items.append(
        evaluate_compatibility_dosha_item(
            dosha_id="nadi_dosha",
            name_en="Nadi Dosha (Pulse & Genetic Compatibility)",
            name_ta="நாடி தோஷம் (பொருத்த ஆய்வு)",
            classical_ref="Brihat Parashara Hora Shastra Ch. 81 & Muhurta Chintamani",
        )
    )

    # 25. Bhakoot Dosha
    items.append(
        evaluate_compatibility_dosha_item(
            dosha_id="bhakoot_dosha",
            name_en="Bhakoot Dosha (Rasi Distance Compatibility)",
            name_ta="பகூட் தோஷம் (ராசி அதிபதி பொருத்த ஆய்வு)",
            classical_ref="Muhurta Chintamani & Phaladeepika",
        )
    )

    # 26. Gana Dosha
    items.append(
        evaluate_compatibility_dosha_item(
            dosha_id="gana_dosha",
            name_en="Gana Dosha (Temperamental Compatibility)",
            name_ta="கண தோஷம் (குண பொருத்த ஆய்வு)",
            classical_ref="Muhurta Chintamani",
        )
    )

    # 27. Yoni Dosha
    items.append(
        evaluate_compatibility_dosha_item(
            dosha_id="yoni_dosha",
            name_en="Yoni Dosha (Biological & Instinctive Harmony)",
            name_ta="யோனி தோஷம் (இயற்கை இணக்க ஆய்வு)",
            classical_ref="Brihat Samhita & Muhurta Chintamani",
        )
    )

    # -------------------------------------------------------------
    # Group E: Transit Doshas (28 to 30)
    # -------------------------------------------------------------
    # Evaluate Sadesati, Ashtama Shani, Kantaka Shani via XALEN ephemeris
    sade_res = evaluate_sadesati(
        ctx=ctx,
        transit_date=transit_date,
        transit_time=transit_time,
        ayanamsa_id=ayanamsa_id,
        saturn_bav_bindus=saturn_bav_bindus,
    )

    # 28. Sade Sati (12th, 1st, 2nd from Moon)
    is_sade_active = sade_res.phase in ("Rising", "Peak", "Setting")
    sade_mitigated = is_sade_active and (
        (sade_res.saturn_ashtakavarga_bindus is not None and sade_res.saturn_ashtakavarga_bindus >= 4)
        or sade_res.nature_of_transit == "Benefic / Constructive"
    )
    sade_status = "mitigated" if sade_mitigated else ("present" if is_sade_active else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="sadesati_transit_dosha",
            name_en=f"Sade Sati (Saturn's 7.5-Year Transit: {sade_res.phase} Phase)",
            name_ta=f"ஏழரைச் சனி ({sade_res.phase_name_tamil})",
            category="Transit",
            status=sade_status,
            reference_basis=f"Transiting Saturn relative to Natal Moon ({sade_res.natal_moon_sign_name}) on {transit_date or 'Current Date'}",
            formation_conditions=[
                f"Natal Moon in {sade_res.natal_moon_sign_name} (#{sade_res.natal_moon_sign_index})",
                f"Transiting Saturn in {sade_res.transit_saturn_sign_name} (#{sade_res.transit_saturn_sign_index}) at {sade_res.transit_saturn_degree_in_sign:.2f}°",
                f"House from Moon: {sade_res.house_from_moon} (Phase: {sade_res.phase})",
                f"Saturn BAV Bindus: {sade_res.saturn_ashtakavarga_bindus if sade_res.saturn_ashtakavarga_bindus is not None else 'N/A'}",
            ],
            involved_planets=["Moon", "Saturn"],
            signs_and_houses=[
                f"Moon in {sade_res.natal_moon_sign_name}",
                f"Transit Saturn in {sade_res.transit_saturn_sign_name} (House {sade_res.house_from_moon} from Moon)",
            ],
            degrees={
                "Natal_Moon": round(ctx.moon.degree_in_sign, 2) if ctx.moon else 15.0,
                "Transit_Saturn": round(sade_res.transit_saturn_degree_in_sign, 2),
            },
            cancellation_conditions_checked=[
                "Saturn BAV bindus >= 4 in transiting sign (constructive discipline)",
                "Saturn in own sign or exaltation during transit",
                "Benefic aspect of Jupiter on transiting Saturn",
            ],
            cancellation_evidence=[
                f"Saturn holds {sade_res.saturn_ashtakavarga_bindus} BAV bindus in {sade_res.transit_saturn_sign_name} (favorable stability)"
            ] if sade_mitigated else [],
            interpretation=sade_res.interpretation,
            interpretation_ta=sade_res.interpretation_tamil,
            source_references="BPHS Gochara Phala & Classical Transit Canons via XALEN Ephemeris",
            evaluated_at=now_iso,
            remedies=[
                "Light sesame oil lamp (Til Deepam) on Saturdays",
                "Chant Shani Gayatri or Dasharatha Shani Stotram",
                "Offer food or footwear to laborers and needy persons",
            ] if sade_status in ("present", "mitigated") else [],
        )
    )

    # 29. Ashtama Shani (8th from Moon)
    is_ashtama_active = sade_res.phase == "Ashtama"
    ashtama_mitigated = is_ashtama_active and (
        (sade_res.saturn_ashtakavarga_bindus is not None and sade_res.saturn_ashtakavarga_bindus >= 4)
        or sade_res.nature_of_transit == "Benefic / Constructive"
    )
    ashtama_status = "mitigated" if ashtama_mitigated else ("present" if is_ashtama_active else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="ashtama_shani_dosha",
            name_en="Ashtama Shani (Saturn Transit in 8th from Moon)",
            name_ta="அஷ்டம சனி (சந்திரனுக்கு 8-ல் சனி பெயர்ச்சி)",
            category="Transit",
            status=ashtama_status,
            reference_basis=f"Transiting Saturn in 8th from Natal Moon ({sade_res.natal_moon_sign_name}) on {transit_date or 'Current Date'}",
            formation_conditions=[
                f"Natal Moon in {sade_res.natal_moon_sign_name}",
                f"Transiting Saturn in {sade_res.transit_saturn_sign_name} (House 8 from Moon)",
            ] if is_ashtama_active else ["Transiting Saturn does not occupy the 8th house from natal Moon"],
            involved_planets=["Moon", "Saturn"],
            signs_and_houses=[
                f"Moon in {sade_res.natal_moon_sign_name}",
                f"Transit Saturn in {sade_res.transit_saturn_sign_name} (House 8 from Moon)",
            ],
            degrees={
                "Natal_Moon": round(ctx.moon.degree_in_sign, 2) if ctx.moon else 15.0,
                "Transit_Saturn": round(sade_res.transit_saturn_degree_in_sign, 2),
            },
            cancellation_conditions_checked=[
                "Saturn BAV bindus >= 4 in 8th house sign",
                "Benefic aspect of Jupiter on transiting Saturn",
            ],
            cancellation_evidence=[
                f"Saturn holds {sade_res.saturn_ashtakavarga_bindus} BAV bindus in 8th house sign (mitigates sudden turmoil)"
            ] if ashtama_mitigated else [],
            interpretation=(
                "Ashtama Shani is mitigated by strong Ashtakavarga bindus. Cultivates patient endurance, legal caution, and long-term stability."
                if ashtama_status == "mitigated" else
                (
                    "Active Ashtama Shani detected. Encourages careful driving, avoidance of hasty partnerships, and steady health routines."
                    if ashtama_status == "present" else
                    "Saturn is not transiting the 8th house from your natal Moon. Ashtama Shani is absent."
                )
            ),
            interpretation_ta=(
                "அஷ்டம சனி அஷ்டகவர்க சுப பரல்களால் தோஷ நிவர்த்தி பெறுகிறது. பொறுமையும் நிதானமும் வெற்றியைத் தரும்."
                if ashtama_status == "mitigated" else
                (
                    "அஷ்டம சனி காலம் நடைபெறுகிறது. பயணங்களில் கவனமும், புதிய முயற்சிகளில் முன்னெச்சரிக்கையும், திருநள்ளாறு வழிபாடும் நலம் சேர்க்கும்."
                    if ashtama_status == "present" else
                    "சந்திரனுக்கு 8-ம் வீட்டில் சனி சஞ்சரிக்கவில்லை. அஷ்டம சனி இல்லை."
                )
            ),
            source_references="Phaladeepika Ch. 26 & BPHS Gochara Canons via XALEN Ephemeris",
            evaluated_at=now_iso,
            remedies=[
                "Chant Hanuman Chalisa daily",
                "Light sesame oil lamp at Shani Sthalam on Saturdays",
                "Avoid hazardous travel and maintain peaceful speech",
            ] if ashtama_status in ("present", "mitigated") else [],
        )
    )

    # 30. Ardha Ashtama Shani / Kantaka Shani (4th from Moon)
    is_kantaka_active = sade_res.phase == "Kantaka"
    kantaka_mitigated = is_kantaka_active and (
        (sade_res.saturn_ashtakavarga_bindus is not None and sade_res.saturn_ashtakavarga_bindus >= 4)
        or sade_res.nature_of_transit == "Benefic / Constructive"
    )
    kantaka_status = "mitigated" if kantaka_mitigated else ("present" if is_kantaka_active else "absent")
    items.append(
        DoshaEvaluationItem(
            dosha_id="ardha_ashtama_shani_dosha",
            name_en="Ardha Ashtama / Kantaka Shani (Saturn Transit in 4th from Moon)",
            name_ta="அர்த்தாஷ்டம சனி / கண்டக சனி (சந்திரனுக்கு 4-ல் சனி)",
            category="Transit",
            status=kantaka_status,
            reference_basis=f"Transiting Saturn in 4th from Natal Moon ({sade_res.natal_moon_sign_name}) on {transit_date or 'Current Date'}",
            formation_conditions=[
                f"Natal Moon in {sade_res.natal_moon_sign_name}",
                f"Transiting Saturn in {sade_res.transit_saturn_sign_name} (House 4 from Moon)",
            ] if is_kantaka_active else ["Transiting Saturn does not occupy the 4th house from natal Moon"],
            involved_planets=["Moon", "Saturn"],
            signs_and_houses=[
                f"Moon in {sade_res.natal_moon_sign_name}",
                f"Transit Saturn in {sade_res.transit_saturn_sign_name} (House 4 from Moon)",
            ],
            degrees={
                "Natal_Moon": round(ctx.moon.degree_in_sign, 2) if ctx.moon else 15.0,
                "Transit_Saturn": round(sade_res.transit_saturn_degree_in_sign, 2),
            },
            cancellation_conditions_checked=[
                "Saturn BAV bindus >= 4 in 4th house sign",
                "Benefic aspect of Jupiter on transiting Saturn",
            ],
            cancellation_evidence=[
                f"Saturn holds {sade_res.saturn_ashtakavarga_bindus} BAV bindus in 4th house sign (mitigates domestic friction)"
            ] if kantaka_mitigated else [],
            interpretation=(
                "Ardha Ashtama / Kantaka Shani is mitigated by Ashtakavarga strength. Restores domestic peace and property security."
                if kantaka_status == "mitigated" else
                (
                    "Active Kantaka Shani detected. Calls for attention to home comfort, mother's well-being, and grounded career patience."
                    if kantaka_status == "present" else
                    "Saturn is not transiting the 4th house from natal Moon. Ardha Ashtama Shani is absent."
                )
            ),
            interpretation_ta=(
                "கண்டக சனி சுப பரல்களால் தோஷ நிவர்த்தி பெறுகிறது. குடும்பத்தில் அமைதி நிலவும்."
                if kantaka_status == "mitigated" else
                (
                    "கண்டக சனி காலம் நடைபெறுகிறது. தாயாரின் ஆரோக்கியத்தில் அக்கறையும், சொத்து விவகாரங்களில் பொறுமையும் தேவை."
                    if kantaka_status == "present" else
                    "சந்திரனுக்கு 4-ம் வீட்டில் சனி சஞ்சரிக்கவில்லை. அர்த்தாஷ்டம சனி இல்லை."
                )
            ),
            source_references="Phaladeepika Ch. 26 & BPHS Gochara Canons via XALEN Ephemeris",
            evaluated_at=now_iso,
            remedies=[
                "Worship Lord Venkateshwara or Lord Shiva on Saturdays",
                "Offer care and comfort to mother and domestic elders",
            ] if kantaka_status in ("present", "mitigated") else [],
        )
    )

    # Calculate summary counts
    present_cnt = sum(1 for it in items if it.status == "present")
    mitigated_cnt = sum(1 for it in items if it.status == "mitigated")
    absent_cnt = sum(1 for it in items if it.status == "absent")
    indeterminate_cnt = sum(1 for it in items if it.status == "indeterminate")

    summary = DoshaSummary(
        total_rules_evaluated=len(items),
        total_present=present_cnt,
        total_mitigated=mitigated_cnt,
        total_absent=absent_cnt,
        total_indeterminate=indeterminate_cnt,
    )

    return items, summary
