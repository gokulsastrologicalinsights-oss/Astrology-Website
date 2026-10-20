"""Comprehensive Individual Vedic Marriage Analysis & Individual Kuja Dosha Evaluator.

Evaluates groom and bride charts independently according to classical Parashari principles:
1. Lagna and Lagna Lord condition, dignity, and vitality.
2. Marriage Houses & Lords: 2nd (Kutumba), 4th (Sukha), 5th (Putra), 7th (Kalatra),
   8th (Mangalya), and 12th (Sayana Sukha).
3. Marriage Significators (Karakas): Venus, Jupiter, Moon, Mars, Saturn, Rahu-Ketu,
   distinguishing natural nature from functional beneficence/maleficence by Lagna.
4. D1 and D9 Navamsa cross-validation: D9 Lagna, D9 7th house, D1 7th lord in D9,
   D9 7th lord in D1, Vargottama planets, Pushkara Navamsas, and boundary sensitivity.
5. Individual Kuja / Manglik Dosha evaluation reusing the verified single-chart Dosha engine
   (BPHS Ch. 81, Muhurta Chintamani) with full cancellation tracking and bilingual outputs.

Classical Authorities:
- Brihat Parashara Hora Shastra (BPHS), Chapters 9, 13, 15, 18, 20, 34, 81.
- Phaladeepika, Chapter 10 (Kalatra Bhava).
- Jataka Parijata & Muhurta Chintamani.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple, Set

from app.services.marriage_engine.models import (
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    PoruthamStatus,
    DignityType,
    FunctionalNature,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    PARASHARI_ASPECT_OFFSETS,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS,
    MOOLATRIKONA_SIGNS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    LAGNA_PLANETARY_NATURE,
    PLANETARY_NATURAL_FRIENDSHIP,
    VedicHouseFinding,
    VedicSignificatorFinding,
    NavamsaCrossFinding,
    IndividualKujaAssessment,
    IndividualVedicAnalysis,
    DualVedicAnalysis,
)
from app.services.dosha_engine.models import DoshaChartContext
from app.services.dosha_engine.kuja_dosha import evaluate_kuja_dosha, KujaDoshaResult
from app.services.varga_engine import calculate_navamsa_from_longitude, PUSHKARA_NAVAMSAS


# ---------------------------------------------------------------------------
# Classical Dignity and Functional Nature Helpers
# ---------------------------------------------------------------------------

def get_planetary_dignity(planet: str, sign_idx: int) -> DignityType:
    """Determine classical planetary dignity in a given zodiac sign (1 to 12)."""
    if planet in EXALTATION_SIGNS and sign_idx == EXALTATION_SIGNS[planet]:
        return DignityType.EXALTED
    if planet in DEBILITATION_SIGNS and sign_idx == DEBILITATION_SIGNS[planet]:
        return DignityType.DEBILITATED
    if planet in MOOLATRIKONA_SIGNS and sign_idx == MOOLATRIKONA_SIGNS[planet]:
        return DignityType.MOOLATRIKONA
    if planet in OWN_SIGNS and sign_idx in OWN_SIGNS[planet]:
        return DignityType.OWN_SIGN

    lord = SIGN_LORDS.get(sign_idx)
    if not lord:
        return DignityType.NEUTRAL

    rel = PLANETARY_NATURAL_FRIENDSHIP.get(planet, {}).get(lord, 0)
    if rel == 1:
        return DignityType.FRIENDLY
    if rel == -1:
        return DignityType.INIMICAL
    return DignityType.NEUTRAL


def get_functional_nature(planet: str, asc_sign_idx: int) -> FunctionalNature:
    """Determine functional nature (Yogakaraka, Benefic, Malefic, Neutral) per BPHS Ch. 34."""
    asc_name = SIGN_NAMES_EN.get(asc_sign_idx, "Aries").lower()
    nature_map = LAGNA_PLANETARY_NATURE.get(asc_name, {})

    yk = nature_map.get("yogakaraka")
    if yk and yk.lower() == planet.lower():
        return FunctionalNature.YOGAKARAKA

    benefics = {b.lower() for b in nature_map.get("benefics", set())}
    if planet.lower() in benefics:
        return FunctionalNature.FUNCTIONAL_BENEFIC

    malefics = {m.lower() for m in nature_map.get("malefics", set())}
    if planet.lower() in malefics:
        return FunctionalNature.FUNCTIONAL_MALEFIC

    return FunctionalNature.FUNCTIONAL_NEUTRAL


def check_navamsa_boundary_sensitivity(lon_deg: float) -> Tuple[bool, float]:
    """Check if a celestial longitude is within 10 arcminutes of a 3°20' Navamsa boundary."""
    deg_in_sign = lon_deg % 30.0
    nav_span = 10.0 / 3.0  # 3°20' = 3.3333333333333335°
    rem_in_nav = deg_in_sign % nav_span
    dist_deg = min(rem_in_nav, nav_span - rem_in_nav)
    dist_arcmin = dist_deg * 60.0
    is_at_risk = dist_arcmin <= 10.0
    return is_at_risk, round(dist_arcmin, 2)


def chart_context_to_dosha_context(ctx: MarriageChartContext) -> DoshaChartContext:
    """Transform MarriageChartContext into DoshaChartContext for existing dosha evaluators."""
    planets_data = []
    for p in ctx.grahas.values():
        planets_data.append({
            "name": p.name,
            "sign_index": p.sign_index,
            "longitude": p.longitude,
            "degree_in_sign": p.degree_in_sign,
            "is_retrograde": p.is_retrograde,
        })
    return DoshaChartContext(
        planets=planets_data,
        ascendant_sign_idx=ctx.ascendant_sign_idx,
        ascendant_degree=ctx.ascendant_degree,
    )


# ---------------------------------------------------------------------------
# Marriage Houses Metadata & Evaluation
# ---------------------------------------------------------------------------

HOUSE_METADATA: Dict[int, Dict[str, str]] = {
    2: {
        "name_en": "2nd House - Kutumba Bhava (Family, Household Formation & Speech)",
        "name_ta": "2-ஆம் பாவம் - குடும்ப ஸ்தானம் (குடும்ப அமைதி, வாக்கு வன்மை)",
    },
    4: {
        "name_en": "4th House - Sukha Bhava (Domestic Life, Contentment & Home Environment)",
        "name_ta": "4-ஆம் பாவம் - சுக ஸ்தானம் (இல்லற அமைதி, மன நிம்மதி)",
    },
    5: {
        "name_en": "5th House - Putra / Purvapunya Bhava (Romance, Affection & Progeny Prospects)",
        "name_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் & புத்திர ஸ்தானம் (காதல், புத்திர பாக்கியம்)",
    },
    7: {
        "name_en": "7th House - Kalatra Bhava (Primary Marriage & Partnership Union)",
        "name_ta": "7-ஆம் பாவம் - களத்திர ஸ்தானம் (திருமண பந்தம், வாழ்க்கை துணை)",
    },
    8: {
        "name_en": "8th House - Mangalya / Ayur Bhava (Marital Longevity, Shared Resources & Stability)",
        "name_ta": "8-ஆம் பாவம் - மாங்கல்ய / ஆயுள் ஸ்தானம் (மாங்கல்ய பலம், ஆயுள் சௌக்கியம்)",
    },
    12: {
        "name_en": "12th House - Sayana Sukha Bhava (Intimate Life, Bedroom Harmony & Subconscious Compatibility)",
        "name_ta": "12-ஆம் பாவம் - அயன சயன சுக ஸ்தானம் (அந்தரங்க அமைதி, நிம்மதியான உறக்கம்)",
    },
}


def evaluate_vedic_house(ctx: MarriageChartContext, house_num: int) -> VedicHouseFinding:
    """Evaluate an individual marriage house (2, 4, 5, 7, 8, or 12) for a chart."""
    meta = HOUSE_METADATA.get(house_num, {
        "name_en": f"{house_num}th House",
        "name_ta": f"{house_num}-ஆம் பாவம்",
    })

    # Sign calculation
    sign_idx = ((ctx.ascendant_sign_idx + house_num - 2) % 12) + 1
    sign_name_en = SIGN_NAMES_EN[sign_idx]
    sign_name_ta = SIGN_NAMES_TA[sign_idx]
    lord_name = SIGN_LORDS[sign_idx]

    h_obj = ctx.houses.get(house_num)
    cusp_deg = h_obj.cusp_degree if h_obj else float((sign_idx - 1) * 30.0)

    # Lord placement and dignity
    lord_planet = ctx.grahas.get(lord_name)
    if lord_planet:
        lord_house = lord_planet.house
        lord_sign_idx = lord_planet.sign_index
        lord_sign_name = lord_planet.sign_name
        lord_dignity = get_planetary_dignity(lord_name, lord_sign_idx).value
    else:
        lord_house = 1
        lord_sign_idx = sign_idx
        lord_sign_name = sign_name_en
        lord_dignity = DignityType.NEUTRAL.value

    # Occupants
    occupants = [p.name for p in ctx.grahas.values() if p.house == house_num]

    # Aspecting planets
    aspecting_planets = [
        p.name for p in ctx.grahas.values()
        if p.house != house_num and ctx.has_aspect_on_house(p.name, house_num)
    ]

    supporting: List[str] = []
    conflicting: List[str] = []

    # 1. Evaluate Lord Placement & Dignity
    if lord_dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value, DignityType.MOOLATRIKONA.value):
        supporting.append(f"House lord {lord_name} enjoys strong dignity ({lord_dignity}) in {lord_sign_name}.")
    elif lord_dignity == DignityType.DEBILITATED.value:
        conflicting.append(f"House lord {lord_name} is debilitated in {lord_sign_name}.")
    elif lord_dignity == DignityType.FRIENDLY.value:
        supporting.append(f"House lord {lord_name} is placed in friendly sign {lord_sign_name}.")

    if lord_house in (1, 4, 7, 10):
        supporting.append(f"House lord {lord_name} is favorably situated in Kendra house {lord_house}.")
    elif lord_house in (5, 9):
        supporting.append(f"House lord {lord_name} is placed in auspicious Trikona house {lord_house}.")
    elif lord_house in (6, 8, 12):
        conflicting.append(f"House lord {lord_name} is located in Dusthana house {lord_house}.")

    if lord_planet and lord_planet.is_combust:
        conflicting.append(f"House lord {lord_name} is combust with Sun within classical orb.")
    if lord_planet and lord_planet.is_retrograde and lord_name not in ("Rahu", "Ketu"):
        supporting.append(f"House lord {lord_name} is retrograde, conferring strong Chesta Bala.")

    # 2. Evaluate Occupants
    for occ in occupants:
        occ_p = ctx.grahas.get(occ)
        func_nature = get_functional_nature(occ, ctx.ascendant_sign_idx)
        if func_nature == FunctionalNature.YOGAKARAKA:
            supporting.append(f"Yogakaraka {occ} occupies the house, uplifting its significations.")
        elif occ in NATURAL_BENEFICS:
            supporting.append(f"Natural benefic {occ} graces the house as an occupant.")
        elif occ in NATURAL_MALEFICS:
            if func_nature == FunctionalNature.FUNCTIONAL_BENEFIC:
                supporting.append(f"{occ} (functional benefic for Lagna) occupies the house.")
            else:
                conflicting.append(f"Malefic influence of occupant {occ} impacts the house.")

    # 3. Evaluate Aspects
    for asp in aspecting_planets:
        func_nature = get_functional_nature(asp, ctx.ascendant_sign_idx)
        if asp in ("Jupiter", "Venus"):
            supporting.append(f"Auspicious Parashari aspect from natural benefic {asp} protects the house.")
        elif func_nature == FunctionalNature.YOGAKARAKA:
            supporting.append(f"Protective aspect from Yogakaraka {asp} strengthens the house.")
        elif asp in ("Saturn", "Mars", "Rahu", "Ketu"):
            if func_nature == FunctionalNature.FUNCTIONAL_BENEFIC:
                supporting.append(f"{asp} aspects the house with functional beneficence for this Lagna.")
            else:
                conflicting.append(f"Afflicting aspect cast by {asp} on the house.")

    # Status assessment
    if len(conflicting) > 0 and len(supporting) == 0:
        status = PoruthamStatus.FAIL
    else:
        status = PoruthamStatus.PASS

    # Summaries
    occ_str = ", ".join(occupants) if occupants else "None"
    asp_str = ", ".join(aspecting_planets) if aspecting_planets else "None"
    summary_en = (
        f"{meta['name_en']}: Ruled by {lord_name} ({lord_dignity} in {lord_sign_name}, House {lord_house}). "
        f"Occupants: {occ_str}. Aspected by: {asp_str}. "
        f"Positive factors: {len(supporting)}; Challenging factors: {len(conflicting)}."
    )
    summary_ta = (
        f"{meta['name_ta']}: அதிபதி {lord_name} ({lord_sign_name}ல் {lord_dignity}, பாவம் {lord_house}). "
        f"அமர்ந்த கிரகங்கள்: {occ_str}. பார்வை தரும் கிரகங்கள்: {asp_str}. "
        f"சுப காரணிகள்: {len(supporting)}; கவனிக்கத்தக்கவை: {len(conflicting)}."
    )

    return VedicHouseFinding(
        house_number=house_num,
        house_name_en=meta["name_en"],
        house_name_ta=meta["name_ta"],
        sign_index=sign_idx,
        sign_name_en=sign_name_en,
        sign_name_ta=sign_name_ta,
        cusp_degree=cusp_deg,
        lord_name=lord_name,
        lord_house=lord_house,
        lord_sign_index=lord_sign_idx,
        lord_sign_name=lord_sign_name,
        lord_dignity=lord_dignity,
        occupants=occupants,
        aspecting_planets=aspecting_planets,
        supporting_influences=supporting,
        conflicting_influences=conflicting,
        status=status,
        summary_en=summary_en,
        summary_ta=summary_ta,
    )


# ---------------------------------------------------------------------------
# Marriage Significators (Karakas) Evaluation
# ---------------------------------------------------------------------------

MARRIAGE_SIGNIFICATORS = ("Venus", "Jupiter", "Moon", "Mars", "Saturn", "Rahu", "Ketu")


def evaluate_vedic_significator(ctx: MarriageChartContext, planet_name: str) -> VedicSignificatorFinding:
    """Evaluate an individual marriage significator (Karaka) in D1 and D9."""
    p = ctx.grahas.get(planet_name)
    if not p:
        return VedicSignificatorFinding(
            planet_name=planet_name,
            sign_index=1,
            sign_name="Unknown",
            house=1,
            longitude=0.0,
            natural_nature="Benefic" if planet_name in NATURAL_BENEFICS else "Malefic",
            functional_nature=FunctionalNature.FUNCTIONAL_NEUTRAL.value,
            dignity=DignityType.NEUTRAL.value,
            is_retrograde=False,
            is_combust=False,
            d9_sign_index=1,
            d9_sign_name="Unknown",
            is_vargottama=False,
            is_pushkara_navamsa=False,
            summary_en=f"Planet {planet_name} data unavailable.",
            summary_ta=f"கிரகம் {planet_name} தரவு கிடைக்கவில்லை.",
        )

    natural_nature = "Benefic" if planet_name in NATURAL_BENEFICS else "Malefic"
    functional_nature = get_functional_nature(planet_name, ctx.ascendant_sign_idx).value
    dignity = get_planetary_dignity(planet_name, p.sign_index).value

    # Conjunctions in same sign
    conjunctions = [
        other.name for other in ctx.grahas.values()
        if other.name != planet_name and other.sign_index == p.sign_index
    ]

    # Aspects received
    aspects_received = [
        other.name for other in ctx.grahas.values()
        if other.name != planet_name and ctx.has_aspect_on_graha(other.name, planet_name)
    ]

    # D9 Navamsa status
    d9_sign_idx = p.navamsa_sign_index
    d9_sign_name = SIGN_NAMES_EN.get(d9_sign_idx, "Unknown")
    is_vargottama = (p.sign_index == d9_sign_idx)

    # Pushkara Navamsa check
    nav_in_sign = int((p.degree_in_sign // (10.0 / 3.0))) + 1
    is_pushkara = nav_in_sign in PUSHKARA_NAVAMSAS.get(p.sign_index, set())

    # Formulate bilingual summary
    summary_parts_en = [
        f"{planet_name} placed in {p.sign_name} (House {p.house}) with {dignity} dignity.",
        f"Nature: {natural_nature}, Function: {functional_nature}.",
    ]
    if p.is_combust:
        summary_parts_en.append("Afflicted by solar combustion.")
    if p.is_retrograde:
        summary_parts_en.append("Retrograde motion conferring enhanced vitality.")
    if is_vargottama:
        summary_parts_en.append("Vargottama in D9 Navamsa (resilient placement).")
    if is_pushkara:
        summary_parts_en.append("Blessed by sacred Pushkara Navamsa position.")
    if conjunctions:
        summary_parts_en.append(f"Conjoined with: {', '.join(conjunctions)}.")
    if aspects_received:
        summary_parts_en.append(f"Aspected by: {', '.join(aspects_received)}.")

    summary_parts_ta = [
        f"{planet_name} {p.sign_name_tamil}ல் (பாவம் {p.house}) {dignity} நிலையில் உள்ளது.",
    ]
    if is_vargottama:
        summary_parts_ta.append("வர்கோத்தம நவாம்சம் பெற்றுள்ளது.")
    if is_pushkara:
        summary_parts_ta.append("புஷ்கர நவாம்ச சுபத்துவத்தை பெற்றுள்ளது.")
    if p.is_combust:
        summary_parts_ta.append("அஸ்தமன தோஷம் பெற்றுள்ளது.")

    return VedicSignificatorFinding(
        planet_name=planet_name,
        sign_index=p.sign_index,
        sign_name=p.sign_name,
        house=p.house,
        longitude=p.longitude,
        natural_nature=natural_nature,
        functional_nature=functional_nature,
        dignity=dignity,
        is_retrograde=p.is_retrograde,
        is_combust=p.is_combust,
        d9_sign_index=d9_sign_idx,
        d9_sign_name=d9_sign_name,
        is_vargottama=is_vargottama,
        is_pushkara_navamsa=is_pushkara,
        conjunctions=conjunctions,
        aspects_received=aspects_received,
        summary_en=" ".join(summary_parts_en),
        summary_ta=" ".join(summary_parts_ta),
    )


# ---------------------------------------------------------------------------
# D1 and D9 Navamsa Cross-Validation
# ---------------------------------------------------------------------------

def evaluate_navamsa_cross_analysis(ctx: MarriageChartContext) -> NavamsaCrossFinding:
    """Perform rigorous cross-validation between D1 Rasi and D9 Navamsa charts."""
    # 1. D9 Lagna and Lord
    d9_lagna_idx = ctx.ascendant_navamsa_sign_idx
    d9_lagna_name = SIGN_NAMES_EN[d9_lagna_idx]
    d9_lagna_lord = SIGN_LORDS[d9_lagna_idx]

    # 2. D9 7th House and Lord
    d9_7th_idx = ((d9_lagna_idx + 7 - 2) % 12) + 1
    d9_7th_name = SIGN_NAMES_EN[d9_7th_idx]
    d9_7th_lord = SIGN_LORDS[d9_7th_idx]

    # 3. D1 7th Lord in D9
    d1_7th_lord_name = ctx.get_house_lord(7)
    d1_7th_planet = ctx.grahas.get(d1_7th_lord_name)
    if d1_7th_planet:
        d1_7th_in_d9_sign_idx = d1_7th_planet.navamsa_sign_index
        d1_7th_in_d9_sign = SIGN_NAMES_EN[d1_7th_in_d9_sign_idx]
        d1_7th_in_d9_house = ((d1_7th_in_d9_sign_idx - d9_lagna_idx) % 12) + 1
        d1_7th_in_d9_dignity = get_planetary_dignity(d1_7th_lord_name, d1_7th_in_d9_sign_idx).value
    else:
        d1_7th_in_d9_sign = "Unknown"
        d1_7th_in_d9_house = 1
        d1_7th_in_d9_dignity = DignityType.NEUTRAL.value

    # 4. D9 7th Lord in D1
    d9_7th_planet_in_d1 = ctx.grahas.get(d9_7th_lord)
    if d9_7th_planet_in_d1:
        d9_7th_in_d1_sign = d9_7th_planet_in_d1.sign_name
        d9_7th_in_d1_house = d9_7th_planet_in_d1.house
        d9_7th_in_d1_dignity = get_planetary_dignity(d9_7th_lord, d9_7th_planet_in_d1.sign_index).value
    else:
        d9_7th_in_d1_sign = "Unknown"
        d9_7th_in_d1_house = 1
        d9_7th_in_d1_dignity = DignityType.NEUTRAL.value

    # 5. Venus and Jupiter in D9
    venus_p = ctx.grahas.get("Venus")
    if venus_p:
        venus_d9_sign_idx = venus_p.navamsa_sign_index
        venus_in_d9_sign = SIGN_NAMES_EN[venus_d9_sign_idx]
        venus_in_d9_house = ((venus_d9_sign_idx - d9_lagna_idx) % 12) + 1
        venus_in_d9_dignity = get_planetary_dignity("Venus", venus_d9_sign_idx).value
    else:
        venus_in_d9_sign = "Unknown"
        venus_in_d9_house = 1
        venus_in_d9_dignity = DignityType.NEUTRAL.value

    jupiter_p = ctx.grahas.get("Jupiter")
    if jupiter_p:
        jupiter_d9_sign_idx = jupiter_p.navamsa_sign_index
        jupiter_in_d9_sign = SIGN_NAMES_EN[jupiter_d9_sign_idx]
        jupiter_in_d9_house = ((jupiter_d9_sign_idx - d9_lagna_idx) % 12) + 1
        jupiter_in_d9_dignity = get_planetary_dignity("Jupiter", jupiter_d9_sign_idx).value
    else:
        jupiter_in_d9_sign = "Unknown"
        jupiter_in_d9_house = 1
        jupiter_in_d9_dignity = DignityType.NEUTRAL.value

    # 6. Vargottama & Pushkara planets
    vargottama = [
        p.name for p in ctx.grahas.values()
        if p.sign_index == p.navamsa_sign_index
    ]
    pushkara = []
    for p in ctx.grahas.values():
        nav_idx = int((p.degree_in_sign // (10.0 / 3.0))) + 1
        if nav_idx in PUSHKARA_NAVAMSAS.get(p.sign_index, set()):
            pushkara.append(p.name)

    # 7. Navamsa Boundary Sensitivity Check for Ascendant
    is_boundary_risk, dist_arcmin = check_navamsa_boundary_sensitivity(ctx.ascendant_degree)

    # 8. Synthesis Notes
    notes: List[str] = []
    if d1_7th_in_d9_house in (1, 4, 7, 10, 5, 9):
        notes.append(f"D1 7th Lord ({d1_7th_lord_name}) is placed in auspicious house {d1_7th_in_d9_house} in D9 Navamsa.")
    elif d1_7th_in_d9_house in (6, 8, 12):
        notes.append(f"D1 7th Lord ({d1_7th_lord_name}) occupies Dusthana house {d1_7th_in_d9_house} in D9, advising emotional adaptability.")

    if venus_in_d9_dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value):
        notes.append(f"Venus gains high dignity ({venus_in_d9_dignity}) in D9 Navamsa ({venus_in_d9_sign}), supporting long-term romance.")
    if jupiter_in_d9_dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value):
        notes.append(f"Jupiter gains noble dignity ({jupiter_in_d9_dignity}) in D9 Navamsa ({jupiter_in_d9_sign}), conferring marital wisdom.")

    if vargottama:
        notes.append(f"Vargottama planets ({', '.join(vargottama)}) grant deep constitutional strength.")
    if pushkara:
        notes.append(f"Pushkara Navamsa planets ({', '.join(pushkara)}) impart benefic planetary vitality.")

    if is_boundary_risk:
        notes.append(
            f"Birth-time sensitivity: Ascendant is within {dist_arcmin:.1f} arcminutes of a Navamsa boundary. "
            "A birth time variation of ~40 seconds may shift the D9 Lagna."
        )

    exp_en = (
        f"Navamsa Lagna: {d9_lagna_name} (ruled by {d9_lagna_lord}); Navamsa 7th House: {d9_7th_name} (ruled by {d9_7th_lord}). "
        f"D1 7th Lord ({d1_7th_lord_name}) occupies {d1_7th_in_d9_sign} (House {d1_7th_in_d9_house}, {d1_7th_in_d9_dignity}). "
        f"Venus in D9: {venus_in_d9_sign} (House {venus_in_d9_house}); Jupiter in D9: {jupiter_in_d9_sign} (House {jupiter_in_d9_house}). "
        f"Vargottama: {', '.join(vargottama) if vargottama else 'None'}; Pushkara: {', '.join(pushkara) if pushkara else 'None'}."
    )

    exp_ta = (
        f"நவாம்ச லக்னம்: {d9_lagna_name} (அதிபதி {d9_lagna_lord}); நவாம்ச 7-ஆம் பாவம்: {d9_7th_name} (அதிபதி {d9_7th_lord}). "
        f"ராசி 7-ஆம் அதிபதி ({d1_7th_lord_name}) நவாம்சத்தில் {d1_7th_in_d9_sign}ல் (பாவம் {d1_7th_in_d9_house}, {d1_7th_in_d9_dignity}) உள்ளது. "
        f"வர்கோத்தமம்: {', '.join(vargottama) if vargottama else 'இல்லை'}; புஷ்கரம்: {', '.join(pushkara) if pushkara else 'இல்லை'}."
    )

    return NavamsaCrossFinding(
        d9_lagna_sign_index=d9_lagna_idx,
        d9_lagna_sign_name=d9_lagna_name,
        d9_lagna_lord=d9_lagna_lord,
        d9_7th_sign_index=d9_7th_idx,
        d9_7th_sign_name=d9_7th_name,
        d9_7th_lord=d9_7th_lord,
        d1_7th_lord_in_d9_sign=d1_7th_in_d9_sign,
        d1_7th_lord_in_d9_house=d1_7th_in_d9_house,
        d1_7th_lord_in_d9_dignity=d1_7th_in_d9_dignity,
        d9_7th_lord_in_d1_sign=d9_7th_in_d1_sign,
        d9_7th_lord_in_d1_house=d9_7th_in_d1_house,
        d9_7th_lord_in_d1_dignity=d9_7th_in_d1_dignity,
        venus_in_d9_sign=venus_in_d9_sign,
        venus_in_d9_house=venus_in_d9_house,
        venus_in_d9_dignity=venus_in_d9_dignity,
        jupiter_in_d9_sign=jupiter_in_d9_sign,
        jupiter_in_d9_house=jupiter_in_d9_house,
        jupiter_in_d9_dignity=jupiter_in_d9_dignity,
        navamsa_boundary_risk=is_boundary_risk,
        boundary_distance_arcmin=dist_arcmin,
        vargottama_planets=vargottama,
        pushkara_navamsa_planets=pushkara,
        synthesis_notes=notes,
        explanation_en=exp_en,
        explanation_ta=exp_ta,
    )


# ---------------------------------------------------------------------------
# Individual Kuja / Manglik Dosha Assessment
# ---------------------------------------------------------------------------

def evaluate_individual_kuja_assessment(
    ctx: MarriageChartContext,
    role: str = "groom",
    include_2nd_house: bool = True,
) -> IndividualKujaAssessment:
    """Evaluate individual Kuja Dosha reusing the existing verified single-chart Dosha engine."""
    dosha_ctx = chart_context_to_dosha_context(ctx)
    result: KujaDoshaResult = evaluate_kuja_dosha(dosha_ctx, include_2nd_house=include_2nd_house)

    mars_p = ctx.grahas.get("Mars")
    mars_lon = mars_p.longitude if mars_p else 0.0
    mars_sign_idx = mars_p.sign_index if mars_p else 1
    mars_sign_name = mars_p.sign_name if mars_p else "Aries"
    mars_deg_in_sign = mars_p.degree_in_sign if mars_p else 0.0

    mars_house_lagna = ctx.house_from("Mars", ctx.ascendant_sign_idx) if mars_p else 1
    mars_house_moon = ctx.house_from("Mars", ctx.moon_sign_idx) if mars_p else 1
    mars_house_venus = ctx.house_from("Mars", ctx.venus.sign_index) if (mars_p and ctx.venus) else 1

    triggering: List[str] = []
    cancellations_checked: List[str] = [
        "Mars in own sign (Aries/Scorpio)",
        "Mars in exaltation (Capricorn)",
        "Mars debilitated in 7th/8th house",
        "Sign-house specific classical exemptions (2nd in Gemini/Virgo, 12th in Taurus/Libra, 8th in Sagittarius/Pisces, 7/8 in Leo/Aquarius)",
        "Yogakaraka status for Cancer and Leo Lagna",
        "Jupiter conjunction or Parashari aspect",
        "Moon conjunction (Chandra-Mangala)",
        "Saturn conjunction or Parashari aspect",
    ]
    cancellations_applied: List[str] = []

    for ref_name, ref_detail in result.details_by_reference.items():
        if ref_detail.has_dosha:
            triggering.append(
                f"Mars in house {ref_detail.mars_house_from_reference} from {ref_name} ({ref_detail.reference_sign_name})"
            )
            for r_canc in ref_detail.cancellation_reasons:
                if r_canc not in cancellations_applied:
                    cancellations_applied.append(r_canc)

    # Calculate effective active intensity
    active_intensity = sum(
        d.effective_intensity_percent for d in result.details_by_reference.values()
        if d.has_dosha and not d.is_cancelled
    )

    warnings: List[str] = []
    if result.is_present and not result.is_cancelled:
        warnings.append(
            f"Active individual Kuja Dosha detected with {result.severity} severity ({active_intensity:.1f}% weighted intensity). "
            "Classical matchmaking recommends evaluating partner chart's Martian balance in Phase 5."
        )

    return IndividualKujaAssessment(
        subject_role=role,
        is_present=result.is_present,
        is_cancelled=result.is_cancelled,
        severity=result.severity,
        house_convention=result.house_convention,
        mars_longitude=mars_lon,
        mars_sign_index=mars_sign_idx,
        mars_sign_name=mars_sign_name,
        mars_degree_in_sign=mars_deg_in_sign,
        mars_house_from_lagna=mars_house_lagna,
        mars_house_from_moon=mars_house_moon,
        mars_house_from_venus=mars_house_venus,
        effective_intensity_percent=active_intensity,
        references_evaluated={
            k: {
                "reference_point": v.reference_point,
                "reference_sign": v.reference_sign_name,
                "mars_house": v.mars_house_from_reference,
                "has_dosha": v.has_dosha,
                "is_cancelled": v.is_cancelled,
                "cancellations": v.cancellation_reasons,
                "intensity_percent": v.effective_intensity_percent,
            }
            for k, v in result.details_by_reference.items()
        },
        triggering_conditions=triggering,
        cancellations_checked=cancellations_checked,
        cancellations_applied=cancellations_applied,
        source_and_version="BPHS Ch. 81, Muhurta Chintamani, Brihat Samhita (v1.0)",
        explanation_en=result.interpretation,
        explanation_ta=result.interpretation_tamil,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Individual Vedic Marriage Analysis Master Evaluator
# ---------------------------------------------------------------------------

def evaluate_individual_vedic_marriage_analysis(
    ctx: MarriageChartContext,
    role: str = "groom",
) -> IndividualVedicAnalysis:
    """Evaluate comprehensive independent Vedic marriage analysis for one individual."""
    if ctx is None:
        raise ValueError("MarriageChartContext must be provided.")

    # 1. Lagna and Lagna Lord
    lagna_sign_idx = ctx.ascendant_sign_idx
    lagna_sign_name = ctx.ascendant_sign_name
    lagna_sign_name_ta = ctx.ascendant_sign_name_tamil
    lagna_deg = ctx.ascendant_degree
    lagna_lord = SIGN_LORDS[lagna_sign_idx]

    lagna_lord_p = ctx.grahas.get(lagna_lord)
    if lagna_lord_p:
        lagna_lord_house = lagna_lord_p.house
        lagna_lord_dignity = get_planetary_dignity(lagna_lord, lagna_lord_p.sign_index).value
    else:
        lagna_lord_house = 1
        lagna_lord_dignity = DignityType.NEUTRAL.value

    # 2. Marriage Houses: 2, 4, 5, 7, 8, 12
    houses_analysis: Dict[int, VedicHouseFinding] = {}
    for h_num in (2, 4, 5, 7, 8, 12):
        houses_analysis[h_num] = evaluate_vedic_house(ctx, h_num)

    # 3. Marriage Significators
    significators: Dict[str, VedicSignificatorFinding] = {}
    for sig_name in MARRIAGE_SIGNIFICATORS:
        significators[sig_name] = evaluate_vedic_significator(ctx, sig_name)

    # 4. Navamsa Cross-Analysis
    navamsa_cross = evaluate_navamsa_cross_analysis(ctx)

    # 5. Individual Kuja Dosha
    kuja = evaluate_individual_kuja_assessment(ctx, role=role, include_2nd_house=True)

    # 6. Synthesize Supporting & Conflicting Indicators
    supporting: List[str] = []
    conflicting: List[str] = []
    warnings: List[str] = []

    # Lagna Lord condition
    if lagna_lord_dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value, DignityType.MOOLATRIKONA.value):
        supporting.append(f"Lagna lord {lagna_lord} is highly dignified ({lagna_lord_dignity}), conferring personal vitality and stability.")
    elif lagna_lord_dignity == DignityType.DEBILITATED.value:
        conflicting.append(f"Lagna lord {lagna_lord} is debilitated, requiring supportive lifestyle habits.")

    # 7th House & 7th Lord
    h7 = houses_analysis.get(7)
    if h7:
        if h7.status == PoruthamStatus.PASS:
            supporting.append("7th House (Kalatra Bhava) is well-supported by benefic influences or strong lord disposition.")
        else:
            conflicting.append("7th House (Kalatra Bhava) experiences malefic pressure requiring conscious emotional communication.")

    # Karakas
    v_sig = significators.get("Venus")
    if v_sig and v_sig.dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value):
        supporting.append("Venus (primary marriage Karaka) is in strong dignity, fostering affection and aesthetic harmony.")
    elif v_sig and v_sig.dignity == DignityType.DEBILITATED.value:
        conflicting.append("Venus is in debilitation; patience and clear expectations are advised in interpersonal relationships.")

    j_sig = significators.get("Jupiter")
    if j_sig and j_sig.dignity in (DignityType.EXALTED.value, DignityType.OWN_SIGN.value):
        supporting.append("Jupiter (Dharma & family Karaka) is well-disposed, bestowing ethical commitment and benevolence.")

    # Kuja
    if kuja.is_present and not kuja.is_cancelled:
        conflicting.append(f"Active Kuja Dosha present ({kuja.severity} severity from {', '.join(kuja.triggering_conditions)}).")
    elif kuja.is_cancelled:
        supporting.append(f"Kuja Dosha was neutralized by classical cancellations ({', '.join(kuja.cancellations_applied[:2])}).")
    else:
        supporting.append("Chart is completely free from Kuja Dosha afflictions.")

    # Navamsa boundary
    if navamsa_cross.navamsa_boundary_risk:
        warnings.append(
            f"Birth time precision advisory: Ascendant is within {navamsa_cross.boundary_distance_arcmin:.1f} arcminutes of a Navamsa boundary."
        )

    # Executive summaries
    summary_en = (
        f"{role.capitalize()} ({ctx.person_name}): {lagna_sign_name} Lagna (Lord {lagna_lord} in House {lagna_lord_house}, {lagna_lord_dignity}). "
        f"7th House in {h7.sign_name_en if h7 else 'Unknown'} ruled by {h7.lord_name if h7 else 'Unknown'}. "
        f"Kuja Dosha: {kuja.severity} ({'Free' if not kuja.is_present else ('Cancelled' if kuja.is_cancelled else 'Active')}). "
        f"Navamsa Lagna: {navamsa_cross.d9_lagna_sign_name}. "
        f"Key strengths: {len(supporting)}; Areas for conscious care: {len(conflicting)}."
    )

    summary_ta = (
        f"{role.capitalize()} ({ctx.person_name}): {lagna_sign_name_ta} லக்னம் (அதிபதி {lagna_lord} பாவம் {lagna_lord_house}ல் {lagna_lord_dignity}). "
        f"7-ஆம் பாவம் {h7.sign_name_ta if h7 else ''}ல் அதிபதி {h7.lord_name if h7 else ''}. "
        f"செவ்வாய் தோஷம்: {kuja.severity}. "
        f"நவாம்ச லக்னம்: {navamsa_cross.d9_lagna_sign_name}. "
        f"சுப பலங்கள்: {len(supporting)}; கவனிக்கத்தக்கவை: {len(conflicting)}."
    )

    provenance = {
        "ayanamsa": "Lahiri Chitrapaksha (v1.0)",
        "house_system": "Whole-Sign (Canonical Vedic)",
        "coordinates": {"latitude": ctx.latitude, "longitude": ctx.longitude},
        "timezone": ctx.timezone,
        "birth_date": ctx.birth_date_iso,
        "birth_time": ctx.birth_time_iso,
    }

    rule_sources = [
        "Brihat Parashara Hora Shastra (BPHS), Ch. 9, 13, 15, 18, 20, 34, 81",
        "Phaladeepika, Ch. 10 (Kalatra Bhava)",
        "Muhurta Chintamani, Ch. 6 (Vivaha Prakarana)",
        "Jataka Parijata, Ch. 1, Sloka 58 (Pushkara Navamsa)",
    ]

    return IndividualVedicAnalysis(
        subject_role=role,
        person_name=ctx.person_name,
        gender=ctx.gender.value,
        lagna_sign_index=lagna_sign_idx,
        lagna_sign_name=lagna_sign_name,
        lagna_sign_name_tamil=lagna_sign_name_ta,
        lagna_degree=lagna_deg,
        lagna_lord=lagna_lord,
        lagna_lord_house=lagna_lord_house,
        lagna_lord_dignity=lagna_lord_dignity,
        houses_analysis=houses_analysis,
        significators=significators,
        navamsa_cross_analysis=navamsa_cross,
        kuja_dosha=kuja,
        provenance=provenance,
        supporting_indicators=supporting,
        conflicting_indicators=conflicting,
        uncertainty_warnings=warnings,
        rule_sources=rule_sources,
        summary_en=summary_en,
        summary_ta=summary_ta,
    )


# ---------------------------------------------------------------------------
# Dual Vedic Marriage Analysis (Pair-Wise Evaluation)
# ---------------------------------------------------------------------------

def evaluate_dual_vedic_marriage_analysis(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> DualVedicAnalysis:
    """Evaluate dual-chart Vedic marriage analysis independently for groom and bride.
    
    Preserves strict boundary: Does NOT compute an unclassical single composite score or verdict.
    """
    groom_eval = evaluate_individual_vedic_marriage_analysis(groom, role="groom")
    bride_eval = evaluate_individual_vedic_marriage_analysis(bride, role="bride")

    # Comparative D9 Cross-Check Summary
    g_d9 = groom_eval.navamsa_cross_analysis
    b_d9 = bride_eval.navamsa_cross_analysis
    d9_summary_parts = []
    if g_d9 and b_d9:
        d9_summary_parts.append(
            f"Groom D9 Lagna is {g_d9.d9_lagna_sign_name} (Lord: {g_d9.d9_lagna_lord}); "
            f"Bride D9 Lagna is {b_d9.d9_lagna_sign_name} (Lord: {b_d9.d9_lagna_lord})."
        )
        if g_d9.vargottama_planets:
            d9_summary_parts.append(f"Groom brings Vargottama strength in: {', '.join(g_d9.vargottama_planets)}.")
        if b_d9.vargottama_planets:
            d9_summary_parts.append(f"Bride brings Vargottama strength in: {', '.join(b_d9.vargottama_planets)}.")
    d9_summary = " ".join(d9_summary_parts) if d9_summary_parts else "Navamsa cross-analysis completed."

    # Venus-Jupiter Significator Resonance
    g_venus = groom_eval.significators.get("Venus")
    b_venus = bride_eval.significators.get("Venus")
    g_jup = groom_eval.significators.get("Jupiter")
    b_jup = bride_eval.significators.get("Jupiter")

    resonance_parts = []
    if g_venus and b_venus:
        resonance_parts.append(
            f"Groom Venus in {g_venus.sign_name} ({g_venus.dignity}); Bride Venus in {b_venus.sign_name} ({b_venus.dignity})."
        )
    if g_jup and b_jup:
        resonance_parts.append(
            f"Groom Jupiter in {g_jup.sign_name} ({g_jup.dignity}); Bride Jupiter in {b_jup.sign_name} ({b_jup.dignity})."
        )
    resonance_summary = " ".join(resonance_parts) if resonance_parts else "Significator resonance evaluated."

    # Key Observations
    key_obs: List[str] = []
    key_obs.append(f"Groom 7th Lord: {groom_eval.houses_analysis[7].lord_name} in House {groom_eval.houses_analysis[7].lord_house}.")
    key_obs.append(f"Bride 7th Lord: {bride_eval.houses_analysis[7].lord_name} in House {bride_eval.houses_analysis[7].lord_house}.")
    key_obs.append(f"Groom Kuja Dosha Status: {groom_eval.kuja_dosha.severity if groom_eval.kuja_dosha else 'None'}.")
    key_obs.append(f"Bride Kuja Dosha Status: {bride_eval.kuja_dosha.severity if bride_eval.kuja_dosha else 'None'}.")

    return DualVedicAnalysis(
        groom_analysis=groom_eval,
        bride_analysis=bride_eval,
        d9_cross_check_summary=d9_summary,
        venus_jupiter_resonance=resonance_summary,
        key_observations=key_obs,
    )
