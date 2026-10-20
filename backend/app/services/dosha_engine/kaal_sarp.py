"""Kaal Sarp Dosha evaluation module.

Evaluates planetary enclosure between the Rahu-Ketu nodal axis, distinguishing
Full, Partial (Ardha), and Absent states across all 12 canonical classical subtypes,
along with traditional mitigating and cancellation factors.
"""

from typing import Dict, List, Optional, Tuple
from app.schemas.dosha import KaalSarpResult
from app.services.dosha_engine.models import (
    DoshaChartContext,
    SEVEN_GRAHAS,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
)

KAAL_SARP_SUBTYPES: Dict[int, Tuple[str, str, str]] = {
    1: (
        "Anant Kaal Sarp",
        "அனந்த கால சர்ப்ப யோகம்",
        "Rahu in 1st house (Tanu Bhava) and Ketu in 7th house (Kalathra Bhava). Inspires self-reliance, leadership, and philosophical depth through early personal trials.",
    ),
    2: (
        "Kulik Kaal Sarp",
        "குளிக கால சர்ப்ப யோகம்",
        "Rahu in 2nd house (Dhana Bhava) and Ketu in 8th house (Ayur Bhava). Focuses karmic lessons on financial discipline, family heritage, and truthful speech.",
    ),
    3: (
        "Vasuki Kaal Sarp",
        "வாசுகி கால சர்ப்ப யோகம்",
        "Rahu in 3rd house (Sahaja Bhava) and Ketu in 9th house (Bhagya Bhava). Confers bold enterprise, athletic vigor, and eventual triumph through persistent courage.",
    ),
    4: (
        "Shankhpal Kaal Sarp",
        "சங்கபால கால சர்ப்ப யோகம்",
        "Rahu in 4th house (Sukha Bhava) and Ketu in 10th house (Karma Bhava). Catalyzes emotional maturity, stability through real estate or education, and grounded family foundations.",
    ),
    5: (
        "Padma Kaal Sarp",
        "பத்ம கால சர்ப்ப யோகம்",
        "Rahu in 5th house (Putra/Purvapunya Bhava) and Ketu in 11th house (Labha Bhava). Enhances deep creative or speculative brilliance, requiring patient investment in progeny and higher education.",
    ),
    6: (
        "Mahapadma Kaal Sarp",
        "மகாபத்ம கால சர்ப்ப யோகம்",
        "Rahu in 6th house (Shatru Bhava) and Ketu in 12th house (Moksha Bhava). Grants formidable victory over adversaries, medical/legal acumen, and resilience in difficult challenges.",
    ),
    7: (
        "Takshak Kaal Sarp",
        "தக்ஷக கால சர்ப்ப யோகம்",
        "Rahu in 7th house (Jaya Bhava) and Ketu in 1st house (Lagna). Emphasizes marital diplomacy, commercial partnerships, and balanced personal boundaries.",
    ),
    8: (
        "Karkotak Kaal Sarp",
        "கார்கோடக கால சர்ப்ப யோகம்",
        "Rahu in 8th house (Randhra Bhava) and Ketu in 2nd house (Dhana Bhava). Cultivates occult wisdom, research capability, and sudden transformative breakthroughs.",
    ),
    9: (
        "Shankhachood Kaal Sarp",
        "சங்கசூட கால சர்ப்ப யோகம்",
        "Rahu in 9th house (Dharma Bhava) and Ketu in 3rd house (Bhratri Bhava). Promotes higher philosophical inquiry, fortune through righteous enterprise, and mentorship.",
    ),
    10: (
        "Ghatak Kaal Sarp",
        "காடக கால சர்ப்ப யோகம்",
        "Rahu in 10th house (Karma Bhava) and Ketu in 4th house (Sukha Bhava). Bestows dynamic professional ambition, executive prominence, and high public standing after perseverance.",
    ),
    11: (
        "Vishdhar Kaal Sarp",
        "விஷதர கால சர்ப்ப யோகம்",
        "Rahu in 11th house (Labha Bhava) and Ketu in 5th house (Suta Bhava). Drives social networking, multiple revenue streams, and expansive long-term humanitarian visions.",
    ),
    12: (
        "Sheshnag Kaal Sarp",
        "சேஷநாக கால சர்ப்ப யோகம்",
        "Rahu in 12th house (Moksha Bhava) and Ketu in 6th house (Ari Bhava). Unlocks foreign journeys, spiritual surrender, meditative transcendence, and charitable service.",
    ),
}


def evaluate_kaal_sarp_dosha(ctx: DoshaChartContext) -> KaalSarpResult:
    """Evaluate classical Kaal Sarp Dosha, its 12 subtypes, direction, and cancellations."""
    rahu = ctx.rahu
    ketu = ctx.ketu

    # If nodes are missing from chart data, return absent
    if not rahu or not ketu:
        return KaalSarpResult(
            is_present=False,
            dosha_type="Absent",
            subtype_name=None,
            subtype_name_tamil=None,
            rahu_house=1,
            ketu_house=7,
            direction=None,
            planets_inside=[],
            planets_outside=[],
            is_cancelled=False,
            cancellation_reasons=[],
            interpretation="Rahu-Ketu lunar nodal axis is not present in input data; Kaal Sarp is absent.",
            interpretation_tamil="ஜாதகத்தில் ராகு-கேது கணக்கீடுகள் இல்லாததால் கால சர்ப்ப தோஷம் பொருந்தாது.",
        )

    rahu_lon = rahu.longitude
    ketu_lon = ketu.longitude

    # Side 1: Rahu to Ketu in zodiacal direction
    side_rahu_to_ketu: List[str] = []
    # Side 2: Ketu to Rahu in zodiacal direction
    side_ketu_to_rahu: List[str] = []

    for name in SEVEN_GRAHAS:
        g = ctx.grahas.get(name)
        if not g:
            continue
        # Distance forward from Rahu
        dist_from_rahu = (g.longitude - rahu_lon) % 360.0
        if dist_from_rahu < 180.0:
            side_rahu_to_ketu.append(name)
        else:
            side_ketu_to_rahu.append(name)

    # Classify enclosure
    total_grahas = len(side_rahu_to_ketu) + len(side_ketu_to_rahu)
    if total_grahas < 7:
        # Fallback if some grahas missing
        side_rahu_count = len(side_rahu_to_ketu)
        side_ketu_count = len(side_ketu_to_rahu)
    else:
        side_rahu_count = len(side_rahu_to_ketu)
        side_ketu_count = len(side_ketu_to_rahu)

    if side_rahu_count == 7 or side_ketu_count == 7:
        dosha_type = "Full"
        is_present = True
        if side_rahu_count == 7:
            direction = "Apasavya (Descending)"
            planets_inside = side_rahu_to_ketu
            planets_outside = []
        else:
            direction = "Savya (Ascending)"
            planets_inside = side_ketu_to_rahu
            planets_outside = []
    elif side_rahu_count == 6 or side_ketu_count == 6:
        dosha_type = "Partial"
        is_present = True
        if side_rahu_count == 6:
            direction = "Apasavya (Descending)"
            planets_inside = side_rahu_to_ketu
            planets_outside = side_ketu_to_rahu
        else:
            direction = "Savya (Ascending)"
            planets_inside = side_ketu_to_rahu
            planets_outside = side_rahu_to_ketu
    else:
        dosha_type = "Absent"
        is_present = False
        direction = None
        planets_inside = []
        planets_outside = list(SEVEN_GRAHAS)

    # Identify Subtype from Rahu's house
    rahu_house = rahu.house
    ketu_house = ketu.house

    subtype_en = None
    subtype_ta = None
    subtype_desc = ""

    if is_present:
        st_info = KAAL_SARP_SUBTYPES.get(rahu_house)
        if st_info:
            subtype_en, subtype_ta, subtype_desc = st_info

    # Classical Mitigations and Cancellations
    cancellations: List[str] = []
    if is_present:
        # 1. Benefic Grahas in Kendras (1, 4, 7, 10)
        kendra_benefics = []
        for b_name in ("Jupiter", "Venus", "Mercury"):
            bg = ctx.grahas.get(b_name)
            if bg and bg.house in KENDRA_HOUSES:
                kendra_benefics.append(f"{b_name} in {bg.house}th house")
        if kendra_benefics:
            cancellations.append(f"Benefic grahas in Kendras ({', '.join(kendra_benefics)}) anchor and neutralize nodal constraints")

        # 2. Exalted Graha in Kendra or Trikona
        for g_name in SEVEN_GRAHAS:
            g = ctx.grahas.get(g_name)
            if g and ctx.is_exalted(g_name) and (g.house in KENDRA_HOUSES or g.house in TRIKONA_HOUSES):
                cancellations.append(f"Exalted {g_name} in house {g.house} provides tremendous strength overcoming nodal hem")

        # 3. Jupiter Aspecting Rahu or conjoined with Lagna
        if ctx.has_aspect_on_graha("Jupiter", "Rahu"):
            cancellations.append("Jupiter's divine 5th/7th/9th Parashari aspect on Rahu spiritually subdues the serpent energy")
        elif ctx.jupiter and ctx.jupiter.house == 1:
            cancellations.append("Jupiter in Lagna gives Hamsa Yoga-like protection, breaking karmic obstacles")

        # 4. Lagna Lord strongly placed in Kendra or Trikona
        lagna_lord = ctx.get_house_lord(1)
        ll_graha = ctx.grahas.get(lagna_lord)
        if ll_graha and (ll_graha.house in KENDRA_HOUSES or ll_graha.house in TRIKONA_HOUSES) and not ctx.is_debilitated(lagna_lord):
            cancellations.append(f"Lagna lord ({lagna_lord}) strongly placed in house {ll_graha.house} elevates the horoscope")

    is_cancelled = is_present and len(cancellations) > 0

    # Formulate objective interpretations
    if not is_present:
        interp_en = (
            "The 7 physical grahas are distributed on both sides of the Rahu-Ketu nodal axis. "
            "Kaal Sarp Dosha is absent, allowing life energies to express freely across diverse life departments."
        )
        interp_ta = (
            "ராகு-கேது அச்சின் இருபுறமும் கிரகங்கள் சீராக பரவியுள்ளன. "
            "கால சர்ப்ப தோஷம் ஜாதகத்தில் அமையவில்லை. கிரகங்கள் சுதந்திரமாக பலனளிக்கும் நிலையில் உள்ளன."
        )
    elif is_cancelled:
        interp_en = (
            f"{dosha_type} Kaal Sarp ({subtype_en}) is technically formed, but is effectively mitigated "
            f"by powerful classical factors: {'; '.join(cancellations)}. "
            "Rather than causing obstruction, this configuration functions as a catalyst for relentless ambition, "
            "high focus, and substantial worldly or spiritual accomplishment."
        )
        interp_ta = (
            f"{subtype_ta} ({dosha_type}) அமைந்திருந்தாலும், ஜாதகத்தில் உள்ள விசேஷ சுப அமைப்புகளாலும் "
            f"({'; '.join(cancellations)}) தோஷ நிவர்த்தி பெறுகிறது. இது தடைகளை உடைத்து உன்னத வெற்றிகளை ஈட்டித் தரும்."
        )
    else:
        outside_note = f" (Graha outside axis: {', '.join(planets_outside)})" if planets_outside else ""
        interp_en = (
            f"Active {dosha_type} Kaal Sarp Dosha ({subtype_en}) is present in {direction} orientation{outside_note}. "
            f"{subtype_desc} "
            "Classical astrology views this as a formative yoga demanding patience and resilience up to age 33-36, "
            "after which natives frequently attain exceptional distinction and enduring success."
        )
        interp_ta = (
            f"{subtype_ta} ({dosha_type}) செயல்பாட்டில் உள்ளது. "
            "ஆரம்ப காலகட்டங்களில் பொறுமையையும் விடாமுயற்சியையும் கோரினாலும், "
            "முப்பது வயதிற்குப் பின் தீவிர உழைப்பால் உயரிய அந்தஸ்தையும் பெரும் புகழையும் அளிக்கவல்லது."
        )

    return KaalSarpResult(
        is_present=is_present,
        dosha_type=dosha_type,
        subtype_name=subtype_en,
        subtype_name_tamil=subtype_ta,
        rahu_house=rahu_house,
        ketu_house=ketu_house,
        direction=direction,
        planets_inside=planets_inside,
        planets_outside=planets_outside,
        is_cancelled=is_cancelled,
        cancellation_reasons=cancellations,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
    )
