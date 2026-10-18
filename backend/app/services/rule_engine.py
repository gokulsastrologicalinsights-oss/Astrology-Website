"""Rule-based analysis engine for marriage compatibility and career indicators.

Deterministic heuristics following classical Brihat Parashara Hora Shastra (BPHS)
and Krishnamurti Paddhati (KP) canons.

IMPORTANT DISCLAIMER:
These rules are traditional cultural heuristics. They are NOT scientifically proven
predictions and must NEVER be presented as deterministic life outcomes, medical,
financial, or legal advice.
"""

from typing import List, Dict, Any, Optional
from app.schemas.rules import (
    RuleAuditNote,
    KujaDoshaStatus,
    CompatibilitySummary,
    CareerAnalysisSummary,
)
from app.schemas.horoscope import HoroscopeResponse


# Sign Rulership according to classical Parashari Jyotish
SIGN_LORDS = {
    1: "Mars",      # Aries
    2: "Venus",     # Taurus
    3: "Mercury",   # Gemini
    4: "Moon",      # Cancer
    5: "Sun",       # Leo
    6: "Mercury",   # Virgo
    7: "Venus",     # Libra
    8: "Mars",      # Scorpio
    9: "Jupiter",   # Sagittarius
    10: "Saturn",   # Capricorn
    11: "Saturn",   # Aquarius
    12: "Jupiter",  # Pisces
}

# Classical houses considered for Manglik / Kuja Dosha (1st, 2nd, 4th, 7th, 8th, 12th)
# Note: South Indian tradition emphasizes 2, 4, 7, 8, 12; North Indian often includes 1st (Lagna).
KUJA_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}


def get_house_from_reference(target_sign_idx: int, ref_sign_idx: int) -> int:
    """Calculate house distance (1 to 12) from reference sign index (1-12)."""
    return ((target_sign_idx - ref_sign_idx) % 12) + 1


def check_kuja_dosha_basic(
    mars_sign_idx: int,
    lagna_sign_idx: int,
    moon_sign_idx: int,
    venus_sign_idx: Optional[int] = None,
) -> KujaDoshaStatus:
    """Evaluate preliminary Kuja (Mangal) Dosha houses from Lagna, Moon, and Venus.

    Complex cancellations (own house, Jupiter aspect, mutual pairing) are flagged
    as outstanding work to avoid false confidence.
    """
    h_lagna = get_house_from_reference(mars_sign_idx, lagna_sign_idx)
    h_moon = get_house_from_reference(mars_sign_idx, moon_sign_idx)
    h_venus = get_house_from_reference(mars_sign_idx, venus_sign_idx) if venus_sign_idx else None

    has_dosha = (
        h_lagna in KUJA_DOSHA_HOUSES
        or h_moon in KUJA_DOSHA_HOUSES
        or (h_venus is not None and h_venus in KUJA_DOSHA_HOUSES)
    )

    reasons = []
    if h_lagna in KUJA_DOSHA_HOUSES:
        reasons.append(f"Mars in {h_lagna}th house from Lagna")
    if h_moon in KUJA_DOSHA_HOUSES:
        reasons.append(f"Mars in {h_moon}th house from Moon")
    if h_venus and h_venus in KUJA_DOSHA_HOUSES:
        reasons.append(f"Mars in {h_venus}th house from Venus")

    return KujaDoshaStatus(
        has_dosha=has_dosha,
        mars_house_from_lagna=h_lagna,
        mars_house_from_moon=h_moon,
        mars_house_from_venus=h_venus,
        is_cancelled=False,
        cancellation_reasons=reasons,
    )


def analyze_career_indicators(horoscope: HoroscopeResponse) -> CareerAnalysisSummary:
    """Extract 10th house, 10th lord, planetary occupants and aspects for career analysis."""
    # Find 10th house
    tenth_house = next((h for h in horoscope.houses if h.house_number == 10), None)
    tenth_sign_idx = tenth_house.sign_index if tenth_house else ((horoscope.ascendant.sign_index + 8) % 12 + 1)
    tenth_sign_name = tenth_house.sign_name if tenth_house else "Unknown"
    tenth_lord = SIGN_LORDS.get(tenth_sign_idx, "Unknown")

    # Find planets occupying 10th sign
    occupants = [
        p.name for p in horoscope.planets
        if p.sign_index == tenth_sign_idx
    ]

    # Find planets aspecting 10th house (7th from 10th is 4th house; Mars also aspects 4th & 8th; Jupiter 5th & 9th; Saturn 3rd & 10th)
    aspecting = []
    for p in horoscope.planets:
        diff = get_house_from_reference(tenth_sign_idx, p.sign_index)
        if diff == 7:
            aspecting.append(f"{p.name} (7th aspect)")
        elif p.name == "Mars" and diff in (4, 8):
            aspecting.append(f"Mars ({diff}th special aspect)")
        elif p.name == "Jupiter" and diff in (5, 9):
            aspecting.append(f"Jupiter ({diff}th special aspect)")
        elif p.name == "Saturn" and diff in (3, 10):
            aspecting.append(f"Saturn ({diff}th special aspect)")

    # Find Sun, Mercury, Jupiter signs
    sun_sign = next((p.sign_name for p in horoscope.planets if p.name == "Sun"), "Unknown")
    mercury_sign = next((p.sign_name for p in horoscope.planets if p.name == "Mercury"), "Unknown")
    jupiter_sign = next((p.sign_name for p in horoscope.planets if p.name == "Jupiter"), "Unknown")

    # Jaimini Amatyakaraka (planet with 2nd highest degree in sign among 7 charakarakas)
    seven_grahas = [p for p in horoscope.planets if p.name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")]
    sorted_by_deg = sorted(seven_grahas, key=lambda p: p.degree_in_sign, reverse=True)
    amatyakaraka = sorted_by_deg[1].name if len(sorted_by_deg) > 1 else None

    notes = [
        f"10th house is {tenth_sign_name}, ruled by {tenth_lord}.",
        f"Occupants in 10th house: {', '.join(occupants) if occupants else 'None'}.",
        f"Planetary aspects on 10th house: {', '.join(aspecting) if aspecting else 'None'}.",
        f"Amatyakaraka (career significator per Jaimini): {amatyakaraka}.",
    ]

    return CareerAnalysisSummary(
        tenth_house_sign=tenth_sign_name,
        tenth_house_lord=tenth_lord,
        tenth_house_occupants=occupants,
        planets_aspecting_tenth=aspecting,
        sun_position_sign=sun_sign,
        mercury_position_sign=mercury_sign,
        jupiter_position_sign=jupiter_sign,
        amatyakaraka=amatyakaraka,
        rule_notes=notes,
    )


def list_documented_rules() -> List[RuleAuditNote]:
    """Return inventory of documented rules and their implementation/verification status."""
    return [
        RuleAuditNote(
            rule_id="RULE-HORO-01",
            rule_name="Sidereal Planetary Ephemeris",
            tradition="Astronomical Sidereal",
            status="Implemented",
            description="True geocentric sidereal positions via Swiss Ephemeris JPL DE431 integration.",
            documentation_ref="XALEN Ephemeris core",
        ),
        RuleAuditNote(
            rule_id="RULE-DASA-01",
            rule_name="Vimshottari Dasa Balance and Hierarchy",
            tradition="Brihat Parashara Hora Shastra",
            status="Implemented",
            description="365.25-day year convention, 120-year cycle, 27 Nakshatra boundary-clamped balance.",
            documentation_ref="BPHS Chapter 46; validation_suite/phase_d_verification.py",
        ),
        RuleAuditNote(
            rule_id="RULE-KP-01",
            rule_name="KP 249 Sub-Divisions and Cuspal Analysis",
            tradition="Krishnamurti Paddhati",
            status="Implemented",
            description="249 unequal sub-lord intervals and 4-tier significator strength table.",
            documentation_ref="K.S. Krishnamurti KP Reader I & II; validation_suite/test_kp_boundaries.py",
        ),
        RuleAuditNote(
            rule_id="RULE-MARR-01",
            rule_name="Basic Kuja Dosha House Identification",
            tradition="South/North Indian Parashari",
            status="Draft",
            description="Identifies Mars in 1, 2, 4, 7, 8, 12 from Lagna, Moon, and Venus.",
            documentation_ref="Outstanding: 28 canonical cancellation exceptions per Muhurtha Chintamani.",
        ),
        RuleAuditNote(
            rule_id="RULE-MARR-02",
            rule_name="Ashtakuta / 10-Porutham Matching",
            tradition="Vedic / Tamil",
            status="Requires Verification",
            description="Dina, Gana, Mahendra, Stree-Deergha, Yoni, Rasi, Rasyadhipati, Vasya, Rajju, Vedha.",
            documentation_ref="Pending canon specification for Tamil vs North Indian score weights.",
        ),
        RuleAuditNote(
            rule_id="RULE-CAREER-01",
            rule_name="10th House and Amatyakaraka Disposition",
            tradition="Parashari & Jaimini Upadesha Sutras",
            status="Draft",
            description="Extracts 10th sign, ruler, occupants, aspecting grahas, and Amatyakaraka.",
            documentation_ref="Outstanding: Dashamsha (D10) divisional verification and Shadbala weights.",
        ),
        RuleAuditNote(
            rule_id="RULE-YOGA-01",
            rule_name="Classical Nabhasha Yoga Detection",
            tradition="Brihat Parashara Hora Shastra Chapter 35",
            status="Implemented",
            description="Complete 32 Nabhasha Yoga taxonomy (Ashraya, Dala, Aakriti, Sankhya) with classical precedence rules.",
            documentation_ref="BPHS Chapter 35; Brihat Jataka Chapter 12; app/services/nabhasha_engine",
        ),
        RuleAuditNote(
            rule_id="RULE-ASHTA-01",
            rule_name="Parashari Ashtakavarga, Shodhana and Pinda Sadhana",
            tradition="Brihat Parashara Hora Shastra Chapters 66-69",
            status="Implemented",
            description="7-planet Bhinnashtakavarga, 337-invariant Sarvashtakavarga, Trikona & Ekadhipatya Shodhana, and Shodhya Pindas.",
            documentation_ref="BPHS Chapters 66–69; app/services/ashtakavarga_engine",
        ),
    ]
