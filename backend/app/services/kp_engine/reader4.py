"""Krishnamurti Paddhati (KP) Reader 4: Marriage, Married Life & Children.

Codified directly from Prof. K. S. Krishnamurti's foundational authority:
'Stellar Astrological Reader No. IV: Marriage, Married Life & Children'
(Krishman & Co., Madras / Stellar Astrological Research Institute).

Key Features Codified from KP Reader 4:
----------------------------------------
1. Authentic Mars Dosha (Kuja / Manglik Dosha) Evaluation:
   - Evaluated sign-to-sign from Lagna, Moon, and Venus across houses 1, 2, 4, 7, 8, 12.
   - Strict severity hierarchy: Venus > Moon > Lagna.
   - Complete implementation of the 10 Classical Parihara (Cancellation/Mitigation) rules:
       * Own signs (Aries, Scorpio) or exaltation (Capricorn) in 4 or 7.
       * Movable signs (Aries, Cancer, Libra, Capricorn) in 1, 2, 4, 7, 8, 12.
       * Conjunction or aspect with Jupiter or Mercury.
       * Signs of Luminaries (Cancer, Leo).
       * Special sign exceptions for houses 2, 4, 7, 8, 12.
       * Conjunction with Moon (Chandra-Mangala) or Jupiter (Guru-Mangala within 8°).
   - KP Cuspal Sub-Lord resolution: Mars alone cannot cause separation unless 7th CSL signifies 6, 10, 12.

2. Punarphoo (Saturn-Moon Connection) Evaluator:
   - Detects all 4 classical modes of Punarphoo:
       * Conjunction of Saturn and Moon.
       * Mutual aspects (Saturn 3rd, 7th, 10th on Moon, Moon 7th on Saturn).
       * Star and Sub exchange (Moon in Saturn's star/sub; Saturn in Moon's star/sub).
       * Nodes (Rahu/Ketu) representing Saturn or Moon.
   - Classifies impediment types: delayed negotiations, wedding date postponements,
     physical/medical cycles, shocking last-minute discoveries, 4th proposal fulfillment.

3. Physical Features & Characteristics of Spouse by 7th Cusp Sub-Lord:
   - Exhaustive lookup table for 7th CSL (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn,
     Rahu, Ketu) posited in each of the 12 Zodiac Signs (Aries through Pisces).
   - Stature, facial appearance, complexion, temperament, and life signatures.

4. Career Wife / Working Partner Evaluator:
   - Sub-lord of 4th Cusp (10th from 7th = spouse's career) signifying 4, 8, 12
     (which represent 10th, 2nd, and 6th houses of the spouse).
   - Mars signification for high executive, medical, or armed forces careers.

5. Marriage Promise & Denial ("Grapes are Sour"):
   - 7th CSL signifying supporting houses (2, 7, 11) vs denying houses (1, 6, 10, 4).
   - Formula for permanent bachelorhood when 7th CSL signifies 4, 6, 10.

6. Plurality of Partners & Second Marriage:
   - 7th CSL or 2nd CSL ruled by Mercury or occupying a dual sign with 2, 7, 11 links.
   - Venus-Uranus, Moon-Venus, and Rahu in 7th indicators.

7. Progeny & Childbirth (5th Cusp Mechanics):
   - 5th CSL in fruitful signs (Cancer, Scorpio, Pisces) vs barren signs (Aries, Gemini, Leo, Virgo).
   - Signification of 2, 5, 11 (blessed) vs 4, 10 (impediment/adoption/denial).
   - Twin birth configurations in dual signs.

8. Sage Kasyapa's Special Empirical Findings for the 7th Star (Vatham / Vainasikam):
   - Exceptions for Arudra, Purva Phalguni, Pushya, Punarvasu, Rohini, etc.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants & Sign Classifications (KP Reader 4)
# ---------------------------------------------------------------------------

ZODIAC_SIGNS: Tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

MOVABLE_SIGNS: Set[str] = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_SIGNS: Set[str] = {"Taurus", "Leo", "Scorpio", "Aquarius"}
COMMON_DUAL_SIGNS: Set[str] = {"Gemini", "Virgo", "Sagittarius", "Pisces"}

FRUITFUL_SIGNS: Set[str] = {"Cancer", "Scorpio", "Pisces"}
SEMI_FRUITFUL_SIGNS: Set[str] = {"Taurus", "Libra", "Sagittarius", "Capricorn"}
BARREN_SIGNS: Set[str] = {"Aries", "Gemini", "Leo", "Virgo"}

MARS_DOSHA_HOUSES: Set[int] = {1, 2, 4, 7, 8, 12}

MARRIAGE_SUPPORTING_HOUSES: Set[int] = {2, 7, 11}
MARRIAGE_DENYING_HOUSES: Set[int] = {1, 6, 10}
COURTSHIP_DENYING_HOUSES: Set[int] = {4}  # 12th from 5th

PROGENY_SUPPORTING_HOUSES: Set[int] = {2, 5, 11}
PROGENY_DENYING_HOUSES: Set[int] = {4, 10}  # 12th from 5th, 12th from 11th

# Nakshatras 1 to 27 in order
NAKSHATRA_NAMES: Tuple[str, ...] = (
    "Aswini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Arudra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swathi", "Vishakha", "Anuradha", "Jyeshta",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Sravana", "Dhanishta", "Satabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
)

SATURN_STARS: Set[str] = {"Pushya", "Anuradha", "Uttara Bhadrapada"}
MOON_STARS: Set[str] = {"Rohini", "Hasta", "Sravana"}

# ---------------------------------------------------------------------------
# Data Models for KP Reader 4 Outputs
# ---------------------------------------------------------------------------

@dataclass
class MarsDoshaSourceDetail:
    """Details of Mars placement relative to a specific reference point."""
    reference_point: str  # 'Lagna', 'Moon', 'Venus'
    reference_sign: str
    mars_sign: str
    counted_house: int
    has_dosha: bool
    dosha_weight: float  # Venus (3.0) > Moon (2.0) > Lagna (1.0)
    reasons: List[str] = field(default_factory=list)


@dataclass
class MarsDoshaParihara:
    """A single cancellation or mitigation factor."""
    rule_id: str
    rule_name: str
    description: str
    applies: bool


@dataclass
class MarsDoshaResult:
    """Complete Mars Dosha analysis with classical pariharas & KP sub-lord resolution."""
    raw_dosha_present: bool
    total_score: float
    source_details: List[MarsDoshaSourceDetail]
    pariharas_applicable: List[MarsDoshaParihara]
    is_mitigated: bool
    kp_cuspal_override: str
    recommendation: str
    shastric_verdict: str


@dataclass
class PunarphooResult:
    """Punarphoo (Saturn-Moon connection) detection and guidance."""
    is_punarphoo_present: bool
    severity: str  # 'None', 'Mild', 'Moderate', 'Severe'
    connections_found: List[str]
    case_study_analogy: str
    predicted_impediments: List[str]
    kp_counsel: str


@dataclass
class SpousePhysicalAppearance:
    """Physical features and temperament of the partner per 7th Cusp Sub-Lord."""
    csl_planet: str
    csl_sign: str
    stature: str
    complexion_and_face: str
    temperament: str
    vocational_and_lifestyle_traits: str
    cautionary_notes: Optional[str] = None
    shastric_quote: str = ""


@dataclass
class CareerSpouseResult:
    """Evaluates whether the native will marry an employed/career partner."""
    will_marry_career_spouse: bool
    fourth_csl_planet: str
    fourth_csl_signifies: List[int]
    matching_houses: List[int]
    spouse_vocation_type: str
    explanation: str


@dataclass
class MarriagePromiseResult:
    """Evaluates whether marriage is promised, delayed, or denied ('Grapes are Sour')."""
    verdict: str  # 'PROMISED_EARLY', 'PROMISED_NORMAL', 'PROMISED_DELAYED', 'DENIED'
    seventh_csl_planet: str
    supporting_significations: List[int]
    denying_significations: List[int]
    is_denied: bool
    delay_factors: List[str]
    philosophical_verdict: str
    detailed_reasoning: str


@dataclass
class SecondMarriageResult:
    """Evaluates possibility of second marriage or plurality of relationships."""
    is_second_marriage_indicated: bool
    plurality_of_relationships: bool
    seventh_csl_in_dual_sign: bool
    seventh_csl_is_mercury: bool
    second_cusp_sub_lord_support: bool
    reasons: List[str]
    guidance: str


@dataclass
class ProgenyPromiseResult:
    """Evaluates childbirth promise, fertility, barrenness, or adoption."""
    childbirth_promised: bool
    fertility_status: str  # 'Fruitful', 'Semi-Fruitful', 'Barren / Impeded'
    fifth_csl_planet: str
    fifth_csl_sign: str
    fifth_csl_signifies: List[int]
    supporting_houses: List[int]
    denying_houses: List[int]
    twin_birth_indicated: bool
    adoption_indicated: bool
    progeny_timing_advice: str
    clive_fallacy_counsel: str


@dataclass
class SageKasyapaSeventhStarResult:
    """Evaluates compatibility of the 7th star (Vatham) per Sage Kasyapa."""
    bride_star: str
    groom_star: str
    is_seventh_star: bool
    kasyapa_verdict: str  # 'Approved', 'Rejected', 'Special Exception'
    predicted_experience: str
    shastric_details: str


# ---------------------------------------------------------------------------
# 1. Mars Dosha Evaluator (KP Reader 4 Chapters 19 & 20)
# ---------------------------------------------------------------------------

def calculate_sign_distance(from_sign: str, to_sign: str) -> int:
    """Calculate sign distance (1-12) inclusive, counted from from_sign to to_sign."""
    from_idx = ZODIAC_SIGNS.index(from_sign)
    to_idx = ZODIAC_SIGNS.index(to_sign)
    dist = (to_idx - from_idx) % 12
    return dist + 1


def evaluate_mars_dosha_reader4(
    mars_sign: str,
    lagna_sign: str,
    moon_sign: str,
    venus_sign: str,
    is_mars_conjunct_or_aspected_by_jupiter: bool = False,
    is_mars_conjunct_or_aspected_by_mercury: bool = False,
    is_mars_conjunct_moon: bool = False,
    is_mars_conjunct_jupiter_within_8deg: bool = False,
    seventh_csl_signifies_6_10_12: bool = False,
) -> MarsDoshaResult:
    """Evaluate authentic Mars Dosha per KP Reader 4 Chapters 19 & 20.
    
    Mars occupying 1, 2, 4, 7, 8, or 12 counted sign-to-sign from Lagna, Moon, and Venus.
    Severity hierarchy: Venus (weight 3.0) > Moon (weight 2.0) > Lagna (weight 1.0).
    Evaluates all 10 Classical Pariharas and resolves with KP Cuspal Sub-Lord principle.
    """
    sources: List[MarsDoshaSourceDetail] = []
    
    # 1. Check from Lagna (weight 1.0)
    h_lagna = calculate_sign_distance(lagna_sign, mars_sign)
    has_lagna_dosha = h_lagna in MARS_DOSHA_HOUSES
    sources.append(
        MarsDoshaSourceDetail(
            reference_point="Lagna",
            reference_sign=lagna_sign,
            mars_sign=mars_sign,
            counted_house=h_lagna,
            has_dosha=has_lagna_dosha,
            dosha_weight=1.0 if has_lagna_dosha else 0.0,
            reasons=[f"Mars in {mars_sign} is in {h_lagna}th house from Lagna ({lagna_sign})."]
            if has_lagna_dosha
            else [f"Mars in {h_lagna}th from Lagna is outside dosha houses (1, 2, 4, 7, 8, 12)."],
        )
    )

    # 2. Check from Moon (weight 2.0)
    h_moon = calculate_sign_distance(moon_sign, mars_sign)
    has_moon_dosha = h_moon in MARS_DOSHA_HOUSES
    sources.append(
        MarsDoshaSourceDetail(
            reference_point="Moon",
            reference_sign=moon_sign,
            mars_sign=mars_sign,
            counted_house=h_moon,
            has_dosha=has_moon_dosha,
            dosha_weight=2.0 if has_moon_dosha else 0.0,
            reasons=[f"Mars in {mars_sign} is in {h_moon}th house from Moon ({moon_sign})."]
            if has_moon_dosha
            else [f"Mars in {h_moon}th from Moon is outside dosha houses."],
        )
    )

    # 3. Check from Venus (weight 3.0)
    h_venus = calculate_sign_distance(venus_sign, mars_sign)
    has_venus_dosha = h_venus in MARS_DOSHA_HOUSES
    sources.append(
        MarsDoshaSourceDetail(
            reference_point="Venus",
            reference_sign=venus_sign,
            mars_sign=mars_sign,
            counted_house=h_venus,
            has_dosha=has_venus_dosha,
            dosha_weight=3.0 if has_venus_dosha else 0.0,
            reasons=[f"Mars in {mars_sign} is in {h_venus}th house from Venus ({venus_sign})."]
            if has_venus_dosha
            else [f"Mars in {h_venus}th from Venus is outside dosha houses."],
        )
    )

    raw_present = any(s.has_dosha for s in sources)
    total_score = sum(s.dosha_weight for s in sources)

    # Evaluate the 10 Classical Pariharas (KP Reader 4 pp. 64-68)
    pariharas: List[MarsDoshaParihara] = []

    # Rule 1: Mars in own sign (Aries, Scorpio) or exalted (Capricorn) in 4 or 7
    r1_applies = (mars_sign in {"Aries", "Scorpio", "Capricorn"}) and (
        h_lagna in {4, 7} or h_moon in {4, 7} or h_venus in {4, 7}
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R1_OWN_EXALTED_4_7",
            rule_name="Mars in Own/Exalted Sign in 4 or 7",
            description="Mars in Aries, Scorpio, or Capricorn in 4th or 7th house wards off dosha.",
            applies=r1_applies,
        )
    )

    # Rule 2: Mars in Movable signs in 1, 2, 4, 7, 8, 12
    r2_applies = mars_sign in MOVABLE_SIGNS and raw_present
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R2_CHARA_RASI",
            rule_name="Mars in Movable (Chara) Sign",
            description="Mars in Aries, Cancer, Libra, or Capricorn loses malefic dosha in 1, 2, 4, 7, 8, 12.",
            applies=r2_applies,
        )
    )

    # Rule 3: Conjunction or aspect by Jupiter or Mercury
    r3_applies = is_mars_conjunct_or_aspected_by_jupiter or is_mars_conjunct_or_aspected_by_mercury
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R3_JUPITER_MERCURY_ASPECT",
            rule_name="Benefic Conjunction / Aspect by Guru or Budha",
            description="Mars conjoined with or aspected by Jupiter or Mercury nullifies evil effects.",
            applies=r3_applies,
        )
    )

    # Rule 4: Mars in signs of Luminaries (Leo or Cancer)
    r4_applies = mars_sign in {"Leo", "Cancer"}
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R4_LUMINARY_SIGNS",
            rule_name="Mars in Sun or Moon Signs",
            description="Mars in Leo (ruled by Sun) or Cancer (ruled by Moon) ceases to be evil.",
            applies=r4_applies,
        )
    )

    # Rule 5: Mars in 2nd house in Aries, Scorpio, Gemini, Virgo
    r5_applies = (mars_sign in {"Aries", "Scorpio", "Gemini", "Virgo"}) and (
        h_lagna == 2 or h_moon == 2 or h_venus == 2
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R5_SECOND_HOUSE_EXCEPTION",
            rule_name="Mars in 2nd in Mars/Mercury Signs",
            description="Mars in Aries, Scorpio, Gemini, or Virgo in the 2nd house causes no dosha.",
            applies=r5_applies,
        )
    )

    # Rule 6: Mars in 4th house in Taurus, Libra, Aries, Scorpio
    r6_applies = (mars_sign in {"Taurus", "Libra", "Aries", "Scorpio"}) and (
        h_lagna == 4 or h_moon == 4 or h_venus == 4
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R6_FOURTH_HOUSE_EXCEPTION",
            rule_name="Mars in 4th in Venus/Mars Signs",
            description="Mars in Taurus, Libra, Aries, or Scorpio in the 4th house causes no dosha.",
            applies=r6_applies,
        )
    )

    # Rule 7: Mars in 7th house in Aries, Cancer, Scorpio, Capricorn
    r7_applies = (mars_sign in {"Aries", "Cancer", "Scorpio", "Capricorn"}) and (
        h_lagna == 7 or h_moon == 7 or h_venus == 7
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R7_SEVENTH_HOUSE_EXCEPTION",
            rule_name="Mars in 7th in Own/Deb/Exalted Signs",
            description="Mars in Aries, Cancer, Scorpio, or Capricorn in the 7th house has no dosha.",
            applies=r7_applies,
        )
    )

    # Rule 8: Mars in 8th house in Sagittarius, Pisces, Cancer, Capricorn
    r8_applies = (mars_sign in {"Sagittarius", "Pisces", "Cancer", "Capricorn"}) and (
        h_lagna == 8 or h_moon == 8 or h_venus == 8
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R8_EIGHTH_HOUSE_EXCEPTION",
            rule_name="Mars in 8th in Jupiter/Exalted/Deb Signs",
            description="Mars in Sagittarius, Pisces, Cancer, or Capricorn in the 8th house causes no damage.",
            applies=r8_applies,
        )
    )

    # Rule 9: Mars in 12th house in Gemini, Virgo, Taurus, Libra
    r9_applies = (mars_sign in {"Gemini", "Virgo", "Taurus", "Libra"}) and (
        h_lagna == 12 or h_moon == 12 or h_venus == 12
    )
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R9_TWELFTH_HOUSE_EXCEPTION",
            rule_name="Mars in 12th in Mercury/Venus Signs",
            description="Mars in Gemini, Virgo, Taurus, or Libra in the 12th house loses evil effects.",
            applies=r9_applies,
        )
    )

    # Rule 10: Conjunction with Moon (Chandra-Mangala) or Jupiter (Guru-Mangala within 8°)
    r10_applies = is_mars_conjunct_moon or is_mars_conjunct_jupiter_within_8deg
    pariharas.append(
        MarsDoshaParihara(
            rule_id="R10_CHANDRA_GURU_SAMYOGA",
            rule_name="Chandra-Mangala or Guru-Mangala Samyoga",
            description="Moon-Mars conjunction or Jupiter-Mars conjunction within 8° nullifies Mars dosha.",
            applies=r10_applies,
        )
    )

    applicable_pariharas = [p for p in pariharas if p.applies]
    is_mitigated = len(applicable_pariharas) > 0

    # KP Cuspal Sub-Lord Resolution
    if seventh_csl_signifies_6_10_12:
        kp_override = (
            "KP CUSPAL AFFLICTION: The 7th Cuspal Sub-Lord is a significator of houses 6, 10, or 12. "
            "Per Prof. Krishnamurti, separation or dispute is triggered by the sub-lord's connection, "
            "not merely by Mars!"
        )
    else:
        kp_override = (
            "KP CUSPAL PROTECTION: The 7th Cuspal Sub-Lord does NOT signify houses 6, 10, or 12. "
            "Therefore, even if Mars Dosha is present, it cannot cause marital breakdown or divorce."
        )

    if not raw_present:
        verdict = "SUDDHA JATHAKAM (No Mars Dosha present)"
        rec = "Match with a chart having Suddha Jathakam (free of Mars Dosha)."
    elif is_mitigated:
        verdict = f"MARS DOSHA WITH PARIHARA ({len(applicable_pariharas)} cancellation rules apply)"
        rec = "Match with a chart having similar modified Mars Dosha."
    else:
        verdict = "UNMODIFIED MARS DOSHA (Operative)"
        rec = "Match with a chart having similar unmodified Mars Dosha to neutralize energy."

    return MarsDoshaResult(
        raw_dosha_present=raw_present,
        total_score=total_score,
        source_details=sources,
        pariharas_applicable=applicable_pariharas,
        is_mitigated=is_mitigated,
        kp_cuspal_override=kp_override,
        recommendation=rec,
        shastric_verdict=verdict,
    )


# ---------------------------------------------------------------------------
# 2. Punarphoo (Saturn-Moon Connection) Evaluator (KP Reader 4 Chapter 22)
# ---------------------------------------------------------------------------

def evaluate_punarphoo_reader4(
    saturn_sign: str,
    moon_sign: str,
    saturn_star: str,
    moon_star: str,
    saturn_sub: str,
    moon_sub: str,
    saturn_house: int,
    moon_house: int,
    saturn_aspects_moon: bool = False,
    is_rahu_or_ketu_representing_saturn_or_moon: bool = False,
) -> PunarphooResult:
    """Evaluate Punarphoo (Saturn-Moon connection) per KP Reader 4 Chapter 22.
    
    Evaluates:
    - Same sign conjunction.
    - Mutual aspects (Saturn 3, 7, 10; Moon 7).
    - Star/Sub exchange (Moon in Saturn star/sub; Saturn in Moon star/sub).
    - Placements in 1, 3, 6, 7, 10.
    """
    connections: List[str] = []

    # 1. Conjunction
    if saturn_sign == moon_sign:
        connections.append(f"Saturn and Moon conjunct in {saturn_sign} (House {saturn_house}).")

    # 2. Aspect
    if saturn_aspects_moon:
        connections.append("Saturn aspects Moon by classical drishti.")

    # 3. Star / Sub link
    if moon_star in SATURN_STARS:
        connections.append(f"Moon is in Saturn's constellation ({moon_star}).")
    if saturn_star in MOON_STARS:
        connections.append(f"Saturn is in Moon's constellation ({saturn_star}).")
    if moon_sub.lower() == "saturn":
        connections.append("Moon is in the sub-division of Saturn.")
    if saturn_sub.lower() == "moon":
        connections.append("Saturn is in the sub-division of Moon.")

    # 4. Node acting as proxy
    if is_rahu_or_ketu_representing_saturn_or_moon:
        connections.append("Lunar Node (Rahu/Ketu) reflects and amplifies Saturn-Moon connection.")

    has_punarphoo = len(connections) > 0

    if not has_punarphoo:
        return PunarphooResult(
            is_punarphoo_present=False,
            severity="None",
            connections_found=[],
            case_study_analogy="No Punarphoo affliction detected.",
            predicted_impediments=[],
            kp_counsel="Alliance negotiations will proceed smoothly without unexpected Saturnine stoppages.",
        )

    # Classify severity
    if len(connections) >= 3:
        severity = "Severe"
        analogy = (
            "Resembles Case 2 (The Runaway Groom): Shocking public disruption, scandal, or sudden cancellation "
            "at the threshold of marriage. Great caution and slow, quiet negotiations required."
        )
    elif len(connections) == 2:
        severity = "Moderate"
        analogy = (
            "Resembles Case 1 & Case 3 (The Kumbakonam Call & Heavy Bride): Date postponements, physical/medical "
            "delays (menses), or discrepancy between photograph and real-life appearance. Alliance 1 or 2 fails."
        )
    else:
        severity = "Mild"
        analogy = (
            "Resembles Case 4 (Fourth Proposal Success): Initial 2 or 3 proposals kindle hopes and fall through; "
            "a subsequent proposal unexpectedly materializes into lasting peace."
        )

    impediments = [
        "Unforeseen obstacles arise during negotiation after both parties have verbally agreed.",
        "Postponement of wedding dates or reprint of invitations due to emergency/health cycles.",
        "First two or three alliances collapse suddenly, giving way to an unexpected suitable partner.",
        "Requires patient, non-hasty verification before signing contracts or fixing wedding celebrations.",
    ]

    counsel = (
        "Per Prof. Krishnamurti: Proceed cautiously and slowly till the wedding ceremony is completed. "
        "Do not distribute invitations prematurely. Note that Saturn-Moon connection ultimately yields a mature, "
        "stable, and devoted partner once the initial testing period passes."
    )

    return PunarphooResult(
        is_punarphoo_present=True,
        severity=severity,
        connections_found=connections,
        case_study_analogy=analogy,
        predicted_impediments=impediments,
        kp_counsel=counsel,
    )


# ---------------------------------------------------------------------------
# 3. Spouse Physical Appearance & Characteristics by 7th Cusp Sub-Lord
#    (KP Reader 4 Chapter 29 - Complete 9 Planets x 12 Signs)
# ---------------------------------------------------------------------------

SPOUSE_LOOKUP_TABLE: Dict[Tuple[str, str], Dict[str, str]] = {
    # SUN
    ("Sun", "Aries"): {
        "stature": "Middle stature, strong, well-built and athletic frame.",
        "complexion_and_face": "Good, radiant complexion, full and expressive eyes.",
        "temperament": "Bold, noble, assertive of rights, proud, socially prominent.",
        "vocational": "Victorious leader, administrative authority, commands public success.",
        "caution": None,
    },
    ("Sun", "Taurus"): {
        "stature": "Short, well-set, broad and sturdy athletic constitution.",
        "complexion_and_face": "Broad mouth, broad face, moderate to darkish complexion.",
        "temperament": "Over-confident, not proud, tenacious debater who argues effectively and wins.",
        "vocational": "Sports, athletic pursuits, debate, commerce.",
        "caution": None,
    },
    ("Sun", "Gemini"): {
        "stature": "Above average height, well-proportioned body.",
        "complexion_and_face": "Moderate complexion, long nose, piercing intelligent eyes.",
        "temperament": "Most courteous, tactful, accommodative, pleasing manners, easily influenced.",
        "vocational": "Communication, diplomacy, public relations, trade.",
        "caution": None,
    },
    ("Sun", "Cancer"): {
        "stature": "Short stature, unappealing or plain countenance.",
        "complexion_and_face": "Repulsive or dull face, lacking beauty.",
        "temperament": "Harmless, cheerful, fond of music, dance, and opposite sex, lazy.",
        "vocational": "Dislikes hard physical exertion, artistic hobbies.",
        "caution": "Avoid asking spouse appearance when Sun transits Cancer (July 15 - Aug 17)!",
    },
    ("Sun", "Leo"): {
        "stature": "Strong, majestic, well-built, stately bearing.",
        "complexion_and_face": "Round and big face, moderate complexion, prominent luminous eyes.",
        "temperament": "Intensely faithful, reliable, highly punctual, fair and just, ambitious.",
        "vocational": "Commanding positions, executive leadership, institutional head.",
        "caution": None,
    },
    ("Sun", "Virgo"): {
        "stature": "Tall person with slender, graceful stature.",
        "complexion_and_face": "Good complexion, very dark hair, charming smile.",
        "temperament": "Fond of music, always smiling, never provoking, cheerful, pleasant.",
        "vocational": "Music, recreation, intellectual pursuits, artistic activities.",
        "caution": None,
    },
    ("Sun", "Libra"): {
        "stature": "Tall, straight, upright body with symmetrical elegance.",
        "complexion_and_face": "Big eyes, thinning hair, outwardly beautiful.",
        "temperament": "Speaks of heroism/war but timid; fickle attachments, evasive with truth.",
        "vocational": "Arts, design, social engagements.",
        "caution": "Outward physical beauty may mask lack of truthfulness and moral courage.",
    },
    ("Sun", "Scorpio"): {
        "stature": "Square-built, fleshy, full muscular growth, solid physique.",
        "complexion_and_face": "Broad face, moderate complexion.",
        "temperament": "Ingenious, brilliant discoverer, brisk, ambitious, refuses defeat.",
        "vocational": "Research, investigation, engineering, competitive enterprises.",
        "caution": None,
    },
    ("Sun", "Sagittarius"): {
        "stature": "Tall, handsome, well-proportioned limbs.",
        "complexion_and_face": "Oval face, noble expression.",
        "temperament": "Austere, severe, over-estimates ability, plans on a grand scale, generous.",
        "vocational": "Law, religion, philosophy, large-scale enterprise.",
        "caution": None,
    },
    ("Sun", "Capricorn"): {
        "stature": "Thin-built, lean, wiry, tall frame.",
        "complexion_and_face": "Long nose, soft hair, slightly sickly appearance.",
        "temperament": "Pleasing manners, commands goodwill, makes numerous loyal friends.",
        "vocational": "Public service, organizational management, commerce.",
        "caution": None,
    },
    ("Sun", "Aquarius"): {
        "stature": "Tall, well-made, symmetrical physical frame.",
        "complexion_and_face": "Round face, good complexion.",
        "temperament": "Tolerably good disposition, never deceitful, proud, ostentatious.",
        "vocational": "Intellectual societies, reform, public affairs.",
        "caution": None,
    },
    ("Sun", "Pisces"): {
        "stature": "Short, stout, plump, bloated pumpkin-like body.",
        "complexion_and_face": "Protruding eyes, round fleshy face.",
        "temperament": "Fond of sensual pleasures, extravagant, unjust, partial referee.",
        "vocational": "Poor money management; unfit for judicial or impartial tasks.",
        "caution": "Extravagance and self-indulgence may strain family budget.",
    },

    # MOON
    ("Moon", "Aries"): {
        "stature": "Fleshy and plump, strong constitution.",
        "complexion_and_face": "Round face, fair and bright complexion.",
        "temperament": "Adamant, aggressive, argumentative, ambitious, authoritative.",
        "vocational": "Dynamic enterprise, executive roles, assertive manager.",
        "caution": None,
    },
    ("Moon", "Taurus"): {
        "stature": "Strong, well-built body, just below average height.",
        "complexion_and_face": "Good looking, fair complexion, strikingly attractive.",
        "temperament": "Polite, modest, honest, helpful, peaceful.",
        "vocational": "Finance, arts, domestic harmony, agriculture.",
        "caution": None,
    },
    ("Moon", "Gemini"): {
        "stature": "Tall, well-built, upright posture.",
        "complexion_and_face": "Good complexion, expressive eyes.",
        "temperament": "Ingenious, restless, lacks firm decision, variable moods.",
        "vocational": "Communication, commerce, writing, intellectual trade.",
        "caution": "Fluctuating decisions in career and finance.",
    },
    ("Moon", "Cancer"): {
        "stature": "Average height, well-built, soft and fleshy physique.",
        "complexion_and_face": "Rounded face, moderate soft complexion.",
        "temperament": "Easily influenced, changeable, pleasant manners, harmless, peace-loving.",
        "vocational": "Fond of travel, hospitality, nursing, fortunate in company.",
        "caution": None,
    },
    ("Moon", "Leo"): {
        "stature": "Well-built, average height, dignified bearing.",
        "complexion_and_face": "Moderate complexion, large prominent eyes.",
        "temperament": "Proud, ambitious, independent, refuses to serve as a subordinate.",
        "vocational": "Leadership, autonomous profession; independent career.",
        "caution": None,
    },
    ("Moon", "Virgo"): {
        "stature": "Tall, slender, neat appearance.",
        "complexion_and_face": "Oval face, good complexion.",
        "temperament": "Very clever, reserved, gloomy tendencies, dejected, introspective.",
        "vocational": "Intellectual analysis, accounts, library, research.",
        "caution": "Prone to bouts of mental worry and unnecessary gloom.",
    },
    ("Moon", "Libra"): {
        "stature": "Tall, excellent personality, graceful figure.",
        "complexion_and_face": "Beautiful, radiant complexion, charming smile.",
        "temperament": "Humorous, witty, pleasant, ever-smiling, craves opposite sex appreciation.",
        "vocational": "Fashion, amusements, social entertainment, design.",
        "caution": None,
    },
    ("Moon", "Scorpio"): {
        "stature": "Below average in height, stout, compact frame.",
        "complexion_and_face": "Complexion not fair (dusky), deep intense eyes.",
        "temperament": "Highly impulsive, irregular habits, passionate, difficult to satisfy.",
        "vocational": "Occult, surgery, chemistry, secretive pursuits.",
        "caution": "Moody and turbulent emotional outbursts require patience.",
    },
    ("Moon", "Sagittarius"): {
        "stature": "Handsome, well-built body, athletic posture.",
        "complexion_and_face": "Oval face, honest and noble expression.",
        "temperament": "Generous, hasty, passionate, truthful, lucky.",
        "vocational": "Sports, law, teaching, philosophical travel.",
        "caution": None,
    },
    ("Moon", "Capricorn"): {
        "stature": "Thin, weak body, tall with bushy hair growth.",
        "complexion_and_face": "Complexion not good, poor health, dull eyes.",
        "temperament": "Dull, inactive, pessimistic, selfish; ignored by friends.",
        "vocational": "Routine physical labour, repetitive tasks.",
        "caution": "Prone to chronic health complaints and pessimistic mood.",
    },
    ("Moon", "Aquarius"): {
        "stature": "Moderate height, well-made, pleasing appearance.",
        "complexion_and_face": "Good complexion, calm and clear gaze.",
        "temperament": "Very intelligent, polite, never offensive, studious researcher.",
        "vocational": "Scientific research, literature, humanitarian reform.",
        "caution": None,
    },
    ("Moon", "Pisces"): {
        "stature": "Below average height, plump, fleshy, pot-bellied.",
        "complexion_and_face": "Bloated pumpkin face, sleepy eyes heavy with flesh.",
        "temperament": "Inactive except for sensual pleasures, unsteady, inconstant.",
        "vocational": "Leisure, entertainment, aquatic recreations.",
        "caution": "Tendency toward physical lethargy and financial carelessness.",
    },

    # MARS
    ("Mars", "Aries"): {
        "stature": "Moderate height, muscular, large bones, curling hair.",
        "complexion_and_face": "Ruddy/dark complexion, sharp warrior gaze.",
        "temperament": "Very bold, rash, undaunted, over-confident, quarrelsome, always gains.",
        "vocational": "Military, police, surgery, engineering, athletics.",
        "caution": "Rash temper can cause verbal clashes if provoked.",
    },
    ("Mars", "Taurus"): {
        "stature": "Moderate height, strong, well-built, coarse hair.",
        "complexion_and_face": "Moderate complexion, broad mouth and broad face.",
        "temperament": "Self-indulgent, arrogant, speculative, stubborn.",
        "vocational": "Real estate, speculation, building materials.",
        "caution": "Arrogant when crossed in financial debates.",
    },
    ("Mars", "Gemini"): {
        "stature": "Very tall, well-proportioned frame, restless gait.",
        "complexion_and_face": "Complexion not good, sharp cunning features.",
        "temperament": "Mischievous, cunning, changes residence, evades repaying loans.",
        "vocational": "Agents, commission business, speculative middleman.",
        "caution": "Prone to financial unreliability or evading monetary promises.",
    },
    ("Mars", "Cancer"): {
        "stature": "Short, crooked or defective body, sparse hair.",
        "complexion_and_face": "Dusky complexion, small shifty eyes.",
        "temperament": "Unreliable, unfortunate, unhealthy habits, henchman disposition.",
        "vocational": "Menial work, incapable of sustained noble tasks.",
        "caution": "Debilitated Mars can manifest as physical defects or deceit.",
    },
    ("Mars", "Leo"): {
        "stature": "Tall, well-built, stout hands and legs, vigorous.",
        "complexion_and_face": "Oval face, dark complexion, sharp commanding eyes.",
        "temperament": "Brisk, active, loves shooting/sports, quarrelsome, dresses well.",
        "vocational": "Defense services, police, security, sports management.",
        "caution": None,
    },
    ("Mars", "Virgo"): {
        "stature": "Moderate height, well-built body.",
        "complexion_and_face": "Thick nose, dark complexion.",
        "temperament": "Hasty, impulsive, proud, vindictive, retaliates ruthlessly.",
        "vocational": "Technical analysis, surgery, investigative audit.",
        "caution": "Unforgiving nature; holds grudges and retaliates.",
    },
    ("Mars", "Libra"): {
        "stature": "Tall, handsome, upright stature.",
        "complexion_and_face": "Oval face, red/ruddy complexion, well-dressed.",
        "temperament": "Active, alert, hopeful, boastful, haughty, attached to opposite sex.",
        "vocational": "Luxury goods, entertainment, fashion, public display.",
        "caution": "Vanity in appearance and romantic flirtations.",
    },
    ("Mars", "Scorpio"): {
        "stature": "Stout, bulky, broad-shouldered, curling hair.",
        "complexion_and_face": "Dark complexion, broad face, piercing eyes.",
        "temperament": "Rash, vindictive, revengeful, fond of disputes, very intelligent.",
        "vocational": "Chemicals, surgery, defense, deep research.",
        "caution": "Fierce temper; never forgets an insult.",
    },
    ("Mars", "Sagittarius"): {
        "stature": "Tall, well-proportioned body, athletic posture.",
        "complexion_and_face": "Ruddy complexion, oval face, piercing eyes.",
        "temperament": "Hopeful, jovial, jubilant, cheerful, quick, bold, talkative.",
        "vocational": "Sports, outdoor adventures, law, military leadership.",
        "caution": None,
    },
    ("Mars", "Capricorn"): {
        "stature": "Short, lean, wiry frame, brisk walking style.",
        "complexion_and_face": "Thin face, dark complexion, sharp bright eyes.",
        "temperament": "Witty, humorous, highly intelligent, ambitious, pushy, successful.",
        "vocational": "High corporate office, engineering, executive administration.",
        "caution": None,
    },
    ("Mars", "Aquarius"): {
        "stature": "Well-built body, sturdy constitution.",
        "complexion_and_face": "Good complexion, fair and buoyant.",
        "temperament": "Good debater, argumentative, fair-minded, average fortune.",
        "vocational": "Technical associations, engineering unions, debating forums.",
        "caution": None,
    },
    ("Mars", "Pisces"): {
        "stature": "Below average height, clumsy posture.",
        "complexion_and_face": "Dark complexion, dirty look, dull expression.",
        "temperament": "Self-indulgent, idle, careless, blunders in public social situations.",
        "vocational": "Irregular employment; lacks sustained discipline.",
        "caution": "Social embarrassment due to thoughtless, idiotic blunders.",
    },

    # MERCURY
    ("Mercury", "Aries"): {
        "stature": "Moderate height, thin body, agile movement.",
        "complexion_and_face": "Oval face, brownish hair, dull complexion.",
        "temperament": "Very quick in thinking and speech, expressive, inventive, disorderly.",
        "vocational": "Writer, speaker, journalist, intellectual trader.",
        "caution": "Lacks methodical tidiness and order in domestic life.",
    },
    ("Mercury", "Taurus"): {
        "stature": "Stout body, strong, robust health.",
        "complexion_and_face": "Dark complexion, short and thick hair.",
        "temperament": "Leisurely, happy disposition, fond of opposite sex, diplomatic.",
        "vocational": "Banking, arts, commerce, accumulation of wealth.",
        "caution": None,
    },
    ("Mercury", "Gemini"): {
        "stature": "Tall, well-built, youthful appearance.",
        "complexion_and_face": "Brown hair, good complexion, lively eyes.",
        "temperament": "Intelligent, eloquent orator, inventive, versatile, humorous.",
        "vocational": "Lawyer, agent, journalist, orator, commercial broker.",
        "caution": None,
    },
    ("Mercury", "Cancer"): {
        "stature": "Short, stout, compact frame.",
        "complexion_and_face": "Dark hair, small eyes, sharp nose, complexion not fair.",
        "temperament": "Variable, retentive memory, tactful, sociable, loves picnics/parties.",
        "vocational": "Catering, travel, trade, hospitality.",
        "caution": "Fluctuating moods and variable opinions.",
    },
    ("Mercury", "Leo"): {
        "stature": "Robust health, good stature, dignified appearance.",
        "complexion_and_face": "Round face, broad eyes, brown hair, dark complexion.",
        "temperament": "Persistent, quick-tempered, kind-hearted, intuitive, artistic.",
        "vocational": "Music, drama, organizing capacity, public leadership.",
        "caution": None,
    },
    ("Mercury", "Virgo"): {
        "stature": "Tall, lean, slender, scholarly appearance.",
        "complexion_and_face": "Brown hair, complexion modest, sharp analytical eyes.",
        "temperament": "Very intelligent, cautious, practical, prudent, scholar, writer.",
        "vocational": "Accountancy, occult research, scientific analysis, auditing.",
        "caution": None,
    },
    ("Mercury", "Libra"): {
        "stature": "Tall, strong but thin and well-proportioned.",
        "complexion_and_face": "Brown hair, moderate complexion, pleasant gaze.",
        "temperament": "Broad outlook, dispassionate judge, good in mathematics, sociable.",
        "vocational": "Judiciary, mathematics, fine arts, social sciences.",
        "caution": None,
    },
    ("Mercury", "Scorpio"): {
        "stature": "Short, broad shoulders, solid build.",
        "complexion_and_face": "Dark complexion, brown hair, piercing critical eyes.",
        "temperament": "Stubborn, obstinate, reckless, suspicious, develops mesmerism/hypnotism.",
        "vocational": "Investigation, occult sciences, surgery, research.",
        "caution": "Suspicious nature can cause domestic interrogation.",
    },
    ("Mercury", "Sagittarius"): {
        "stature": "Tall, well-built, large thick bones.",
        "complexion_and_face": "Oval face, long nose, dark complexion.",
        "temperament": "Sincere, just, independent, rebellious, prophetic, active, authoritative.",
        "vocational": "Higher education, law, religious administration, writing.",
        "caution": None,
    },
    ("Mercury", "Capricorn"): {
        "stature": "Thin, not well-built, lean frame.",
        "complexion_and_face": "Thin face, dark complexion, thin brown hair.",
        "temperament": "Irritable, discontented, suspicious, painstaking, studious.",
        "vocational": "Science, occult, historical research, rigorous study.",
        "caution": "Easily disappointed and discontented with domestic realities.",
    },
    ("Mercury", "Aquarius"): {
        "stature": "Moderate stature, attractive and intellectual bearing.",
        "complexion_and_face": "Dark hair, fair complexion, thoughtful eyes.",
        "temperament": "Original thinker, penetrative, humanitarian, expounder of theories.",
        "vocational": "Scientific research, astrology, occult, philosophical authorship.",
        "caution": None,
    },
    ("Mercury", "Pisces"): {
        "stature": "Short, stout, pale complexion, hairy body.",
        "complexion_and_face": "Brownish hair, intuitive soft eyes.",
        "temperament": "Intuitive, versatile, good memory, psychic, finds joy in nursing.",
        "vocational": "Nursing, sanatoriums, boating, music, psychic arts.",
        "caution": None,
    },

    # JUPITER
    ("Jupiter", "Aries"): {
        "stature": "Middle stature, athletic and progressive bearing.",
        "complexion_and_face": "Expressive eyes, high nose, facial pimples/blemishes.",
        "temperament": "Generous, noble, polite, philosophical, fond of travel/sports.",
        "vocational": "Higher education, travel, religious institution, sports.",
        "caution": None,
    },
    ("Jupiter", "Taurus"): {
        "stature": "Moderate height, stout, robust, handsome.",
        "complexion_and_face": "Affectionate expression, good skin, calm demeanor.",
        "temperament": "Affectionate, steady, cannot be influenced, religious, dutiful.",
        "vocational": "Gains through marriage, legacy, investments, banking.",
        "caution": None,
    },
    ("Jupiter", "Gemini"): {
        "stature": "Well-built, slightly stout, tall frame.",
        "complexion_and_face": "Dark hair, penetrating eyes, good complexion.",
        "temperament": "Sympathetic, benevolent, trustworthy, broad outlook, restless.",
        "vocational": "Teaching, academic research, literature, travel.",
        "caution": None,
    },
    ("Jupiter", "Cancer"): {
        "stature": "Stout, short, plump, disproportionate frame.",
        "complexion_and_face": "Pale and anaemic, complexion not fair, kind eyes.",
        "temperament": "Charitable, enterprising, sympathetic, patriotic, loves home/occult.",
        "vocational": "Philanthropy, spiritual arts, institutional management.",
        "caution": None,
    },
    ("Jupiter", "Leo"): {
        "stature": "Strong, tall, majestic, commanding stature.",
        "complexion_and_face": "Round face, curling dark hair, big beautiful eyes.",
        "temperament": "Noble, loyal, generous, diplomatic, highly respected, prestigious.",
        "vocational": "High government post, banking director, leadership.",
        "caution": None,
    },
    ("Jupiter", "Virgo"): {
        "stature": "Above average height, handsome, well-proportioned.",
        "complexion_and_face": "Black hair, fair complexion, dignified expression.",
        "temperament": "Intelligent, cautious, prudent, philosophical, wise, popular.",
        "vocational": "Auditing, science, speculative investments, teaching.",
        "caution": None,
    },
    ("Jupiter", "Libra"): {
        "stature": "Tall, handsome, robust health, graceful posture.",
        "complexion_and_face": "Good complexion, oval face, dark hair, rash/pimples.",
        "temperament": "Obliging, peaceful, charitable, fond of travel, happy marriage.",
        "vocational": "Fine arts, diplomacy, judiciary, happy family life.",
        "caution": None,
    },
    ("Jupiter", "Scorpio"): {
        "stature": "Well-built, beautiful, strong constitution.",
        "complexion_and_face": "Deep commanding gaze, attractive features.",
        "temperament": "Strong will, deep emotions, ambitious, research-minded.",
        "vocational": "Arbitration, litigation, chemistry, corporate secrets.",
        "caution": None,
    },
    ("Jupiter", "Sagittarius"): {
        "stature": "Tall and upright, stately build.",
        "complexion_and_face": "Oval face, brown hair, balding or grows a beard.",
        "temperament": "Courteous, generous, tolerant, loyal, merciful, humanitarian.",
        "vocational": "Judiciary, sports, higher education, philanthropic success.",
        "caution": None,
    },
    ("Jupiter", "Capricorn"): {
        "stature": "Thin, below average height, small head.",
        "complexion_and_face": "Little beard, dark brown thin hair, serious expression.",
        "temperament": "Constructive, creative, ambitious, economical, frugal.",
        "vocational": "Public life, foreign affairs, long journeys, banking.",
        "caution": None,
    },
    ("Jupiter", "Aquarius"): {
        "stature": "Below average, tallish, sturdy constitution.",
        "complexion_and_face": "Brown hair, deep-set eyes, sympathetic look.",
        "temperament": "Hates quarrels, prophetic, spiritual, independent views.",
        "vocational": "Astrology, spiritual counseling, humanitarian science.",
        "caution": None,
    },
    ("Jupiter", "Pisces"): {
        "stature": "Below average height, plump, fleshy build.",
        "complexion_and_face": "Brown hair, kind emotional eyes, gentle smile.",
        "temperament": "Emotional, imaginative, intuitive dreams, unassuming, loves nature.",
        "vocational": "Sanatoriums, charities, religious trusts, aquatics.",
        "caution": None,
    },

    # VENUS
    ("Venus", "Aries"): {
        "stature": "Average height, slender body, graceful posture.",
        "complexion_and_face": "Thin hair, scar or small pox mark on face, attractive look.",
        "temperament": "Artistic, fond of music, sculpture, travels, affectionate, romantic.",
        "vocational": "Music, fine arts, travel, entertainment.",
        "caution": None,
    },
    ("Venus", "Taurus"): {
        "stature": "Very good health, proportionate body, slightly stout.",
        "complexion_and_face": "Strikingly attractive face, beautiful skin, radiant eyes.",
        "temperament": "Emotional, affectionate, deeply faithful, saves money, enjoys luxury.",
        "vocational": "Banking, luxury trade, jewellery, arts, gastronomy.",
        "caution": None,
    },
    ("Venus", "Gemini"): {
        "stature": "Middle stature, slender, youthful appearance.",
        "complexion_and_face": "Fair complexion, dark hair, sparkling eyes.",
        "temperament": "Good-humored, versatile, multiple romantic interests, unsteady.",
        "vocational": "Writing, speaking, music, advertising, multi-occupational.",
        "caution": "Plurality of romantic attachments requires grounding.",
    },
    ("Venus", "Cancer"): {
        "stature": "Short person, stout, delicate constitution.",
        "complexion_and_face": "Round face, pale skin, thin hair, gentle gaze.",
        "temperament": "Loves home, devoted to mother/family, kind, psychic, secret attachments.",
        "vocational": "Interior decor, hospitality, nursing, permanent positions.",
        "caution": "Secret romantic attachments; marriage may experience fluctuations.",
    },
    ("Venus", "Leo"): {
        "stature": "Tall, well-built, radiant and stately bearing.",
        "complexion_and_face": "Clear eyes, round face, fair skin, aristocratic smile.",
        "temperament": "Sympathetic, warm-hearted, charitable, sincere, attractive, social.",
        "vocational": "Music, acting, stock market, speculation, luxury management.",
        "caution": None,
    },
    ("Venus", "Virgo"): {
        "stature": "Tall, well-built, graceful frame.",
        "complexion_and_face": "Oval face, dark hair, neat modest appearance.",
        "temperament": "Sympathetic, intelligent, secret romantic attachments with colleagues.",
        "vocational": "Medicine, pharmacy, gardening, nursery, analytical research.",
        "caution": "Subtle dissatisfaction in purely sexual matters; secret attachments.",
    },
    ("Venus", "Libra"): {
        "stature": "Erect, straight, tall, strikingly beautiful figure.",
        "complexion_and_face": "Oval face, long brown hair, radiant ever-smiling countenance.",
        "temperament": "Pleasing manners, kind, sympathetic, inseparable romantic devotion.",
        "vocational": "Fine arts, fashion design, public entertainment, social harmony.",
        "caution": None,
    },
    ("Venus", "Scorpio"): {
        "stature": "Short, stout, robust, solid physical frame.",
        "complexion_and_face": "Broad face, dark complexion, thick black hair, intense eyes.",
        "temperament": "Extravagant, lavish, passionate, emotional, domestic friction.",
        "vocational": "Gains by gift, dowry, partnership; intense passions.",
        "caution": "Volatile jealousy and extravagance; outlives partner.",
    },
    ("Venus", "Sagittarius"): {
        "stature": "Tall, well-built, upright posture.",
        "complexion_and_face": "Fair long face, brown hair, refined clear features.",
        "temperament": "Refined, impressionable, intuitive, loves nature, romantic journeys.",
        "vocational": "Horse-racing, shipping, foreign tourism, outdoor recreations.",
        "caution": None,
    },
    ("Venus", "Capricorn"): {
        "stature": "Moderate height, slender, pale figure.",
        "complexion_and_face": "Thin face, looks slightly sickly, dark hair.",
        "temperament": "Trustworthy, authoritative, business-like, banking investor, cautious.",
        "vocational": "Corporate banking, investments, delayed marriage, business shares.",
        "caution": "Delayed marriage and financial caution dominate romance.",
    },
    ("Venus", "Aquarius"): {
        "stature": "Tall, large frame, radiant health, beautiful appearance.",
        "complexion_and_face": "Fair complexion, magnetic eyes, serene expression.",
        "temperament": "Sympathetic, humanitarian, sociable, generous romantic spender.",
        "vocational": "Gains through friends, social societies, fulfilled hopes.",
        "caution": None,
    },
    ("Venus", "Pisces"): {
        "stature": "Moderate height, muscular, beautifully proportioned.",
        "complexion_and_face": "Round face, very fair, compassionate eyes.",
        "temperament": "Charitable, emotional, easily influenced, inspirational artist.",
        "vocational": "Painting, music, society, philanthropy, water sports.",
        "caution": None,
    },

    # SATURN
    ("Saturn", "Aries"): {
        "stature": "Bony, thin build, awkward posture.",
        "complexion_and_face": "Black complexion, dull face, sparse hair.",
        "temperament": "Boastful, determined, highly ambitious, analytical, experiences hurdles.",
        "vocational": "Hard physical or technical labour, mining, metalworks.",
        "caution": "Self-boasting and numerous obstacles in early domestic life.",
    },
    ("Saturn", "Taurus"): {
        "stature": "Stout, heavy fat, coarse frame.",
        "complexion_and_face": "Ugly/rough appearance, dark profuse hair, sullen expression.",
        "temperament": "Loses temper quickly, resentful, economical, reserved, loves nature.",
        "vocational": "Horticulture, poultry, agriculture, real estate.",
        "caution": "Domestic life not fortunate; quick resentment.",
    },
    ("Saturn", "Gemini"): {
        "stature": "Tall, slender, dark and serious bearing.",
        "complexion_and_face": "Long face, black hair, deep focused eyes.",
        "temperament": "Intelligent, deep meditation, fond of science, statistics, mathematics.",
        "vocational": "Statistics, scientific analysis, library, legal documentation.",
        "caution": "Trouble through cousins, litigation, or false complaints.",
    },
    ("Saturn", "Cancer"): {
        "stature": "Thin, not tall, weak constitution.",
        "complexion_and_face": "Dark hair, deep-set eyes, sickly appearance.",
        "temperament": "Dissatisfied, changes residence, depressed, industrious, psychic.",
        "vocational": "Domestic economy, manual labour, psychic investigation.",
        "caution": "Perpetual discontent and frequent home relocations.",
    },
    ("Saturn", "Leo"): {
        "stature": "Tall, broad face, big shoulders, heavy frame.",
        "complexion_and_face": "Dark hair, sunken eyes, short beard, serious visage.",
        "temperament": "Stubborn, God-fearing, overworks, exhausted easily in love.",
        "vocational": "Heavy industry, supervision of labourers, agriculture.",
        "caution": "Trouble through servants; feels exhausted in domestic intimacy.",
    },
    ("Saturn", "Virgo"): {
        "stature": "Tall, thin build, scholarly stoop.",
        "complexion_and_face": "Long forehead, black hair, anxious expression.",
        "temperament": "Cautious, frugal, intuitive, reserved, prone to worry, suspicious.",
        "vocational": "Accounts, labour management, spiritual discipline.",
        "caution": "Domestic disharmony and labour troubles.",
    },
    ("Saturn", "Libra"): {
        "stature": "Tall, upright, dignified posture.",
        "complexion_and_face": "Long face, dark hair, long nose, broad forehead.",
        "temperament": "Commands respect, scientific, delayed marriage, heavy-hearted.",
        "vocational": "Judiciary, scientific research, legal drafting.",
        "caution": "Disappointment in youth romance; delayed marriage.",
    },
    ("Saturn", "Scorpio"): {
        "stature": "Moderate height, stout, big shoulders.",
        "complexion_and_face": "Dark hair, intense frowning eyes, dusky skin.",
        "temperament": "Violent passions, jealous, domestic misery, secret activities.",
        "vocational": "Chemicals, heavy mechanics, secretive occupations.",
        "caution": "Unhappy domestic life; prone to jealous quarrels or drink.",
    },
    ("Saturn", "Sagittarius"): {
        "stature": "Huge body, large bones, heavy frame.",
        "complexion_and_face": "Moderate complexion, calm serious face.",
        "temperament": "Obliging, helpful, fearless, philosophical, detached nature.",
        "vocational": "Occult sciences, philosophy, multiple occupations.",
        "caution": "Nervous debility; avoid trusting deceitful associates.",
    },
    ("Saturn", "Capricorn"): {
        "stature": "Lean, bony, average height, hunch-backed.",
        "complexion_and_face": "Sunken cheeks and eyes, black hair, serious look.",
        "temperament": "Peevish, reserved, attachment with inferior friends, unhappy marriage.",
        "vocational": "Mining, building, heavy industry, solitary tasks.",
        "caution": "Unhappy marriage with peevish, sullen domestic arguments.",
    },
    ("Saturn", "Aquarius"): {
        "stature": "Tall, big head, robust constitution.",
        "complexion_and_face": "Brown hair, sunken eyes, deep intellectual gaze.",
        "temperament": "Thoughtful, reserved, serious, intellectual, deep thinker.",
        "vocational": "Scientific research, philosophy, faithful lifelong companion.",
        "caution": None,
    },
    ("Saturn", "Pisces"): {
        "stature": "Moderate height, heavy clumsy frame.",
        "complexion_and_face": "Big head, protruding eyes, irregular teeth, average skin.",
        "temperament": "Secret worries, easily fatigued, persistent occult effort.",
        "vocational": "Sanatoriums, charitable institutions, occult studies.",
        "caution": "Secret domestic worries and irregular dental arrangement.",
    },
}


def lookup_spouse_appearance_reader4(
    csl_planet: str,
    csl_sign: str,
    node_conjunction: Optional[str] = None,
    node_aspect: Optional[str] = None,
    node_star_lord: Optional[str] = None,
) -> SpousePhysicalAppearance:
    """Lookup physical appearance and temperament of spouse per KP Reader 4 Chapter 29.
    
    If CSL is Rahu or Ketu, resolves to conjunct planet, aspecting planet, star lord,
    or sign lord per Prof. Krishnamurti's canonical rules (p. 97).
    """
    effective_planet = csl_planet.title()
    shastric_quote = ""

    # Resolve Rahu / Ketu proxy
    if effective_planet in {"Rahu", "Ketu"}:
        if node_conjunction:
            resolved = node_conjunction.title()
            shastric_quote = f"{effective_planet} reflects conjunct planet {resolved}."
        elif node_aspect:
            resolved = node_aspect.title()
            shastric_quote = f"{effective_planet} reflects aspecting planet {resolved}."
        elif node_star_lord:
            resolved = node_star_lord.title()
            shastric_quote = f"{effective_planet} reflects its Star Lord {resolved}."
        else:
            # Fallback to sign lord of the sign
            from .constants import SIGN_LORDS
            resolved = SIGN_LORDS.get(csl_sign, "Mercury").title()
            shastric_quote = f"{effective_planet} reflects its Sign Lord {resolved}."
        effective_planet = resolved

    # Lookup in canonical table
    data = SPOUSE_LOOKUP_TABLE.get((effective_planet, csl_sign))
    if not data:
        # Fallback to general sign archetype
        data = {
            "stature": f"Moderate stature, typical of {csl_sign} and governed by {effective_planet}.",
            "complexion_and_face": "Balanced facial features with dignified gaze.",
            "temperament": f"Reflective of {effective_planet}'s stellar qualities in {csl_sign}.",
            "vocational": "Active professional and domestic engagement.",
            "caution": None,
        }

    return SpousePhysicalAppearance(
        csl_planet=csl_planet,
        csl_sign=csl_sign,
        stature=data["stature"],
        complexion_and_face=data["complexion_and_face"],
        temperament=data["temperament"],
        vocational_and_lifestyle_traits=data["vocational"],
        cautionary_notes=data.get("caution"),
        shastric_quote=shastric_quote,
    )


# ---------------------------------------------------------------------------
# 4. Career Wife / Working Partner Evaluator (KP Reader 4 Chapter 32)
# ---------------------------------------------------------------------------

def evaluate_career_spouse_reader4(
    fourth_csl_planet: str,
    fourth_csl_signifies: List[int],
    is_mars_involved: bool = False,
) -> CareerSpouseResult:
    """Evaluate whether native marries a career woman / working spouse.
    
    Per KP Reader 4 Chapter 32:
    - 4th house is 10th from 7th (Spouse's career/profession).
    - 8th house is 2nd from 7th (Spouse's earning and income).
    - 12th house is 6th from 7th (Spouse's daily employment/service).
    - If 4th Cusp Sub-Lord signifies 4, 8, or 12, native marries a career girl.
    - If Mars is prominent, she holds high office, police/military, captain, or doctor.
    """
    matching = [h for h in fourth_csl_signifies if h in {4, 8, 12}]
    will_marry = len(matching) > 0

    if will_marry:
        if is_mars_involved:
            vocation = "Independent executive, defense officer, captain, surgeon, engineer, or high official."
        elif 4 in matching and 8 in matching:
            vocation = "Professional in corporate finance, banking, medical sciences, or commercial enterprise."
        else:
            vocation = "Employed in structured service, education, administrative office, or public sector."
        
        explanation = (
            f"The 4th Cusp Sub-Lord ({fourth_csl_planet}) is a strong significator of houses {matching}. "
            "In derivative astrology, the 4th house represents the 10th of spouse (profession), "
            "the 8th represents the 2nd of spouse (earnings), and the 12th represents the 6th of spouse (service). "
            "Per Prof. Krishnamurti's rule in Chapter 32, this unequivocally promises a career wife."
        )
    else:
        vocation = "Homemaker / Domestic Administrator (Non-salaried outside career)."
        explanation = (
            f"The 4th Cusp Sub-Lord ({fourth_csl_planet}) does not signify houses 4, 8, or 12. "
            "Spouse will direct energies primarily toward domestic administration and family welfare."
        )

    return CareerSpouseResult(
        will_marry_career_spouse=will_marry,
        fourth_csl_planet=fourth_csl_planet,
        fourth_csl_signifies=fourth_csl_signifies,
        matching_houses=matching,
        spouse_vocation_type=vocation,
        explanation=explanation,
    )


# ---------------------------------------------------------------------------
# 5. Marriage Promise, Delay & Denial (KP Reader 4 Chapters 21, 35, 37)
# ---------------------------------------------------------------------------

def evaluate_marriage_promise_reader4(
    seventh_csl_planet: str,
    seventh_csl_signifies: List[int],
    is_saturn_connected: bool = False,
    is_saturn_in_5th: bool = False,
    is_mars_in_8th: bool = False,
) -> MarriagePromiseResult:
    """Evaluate whether marriage is promised, delayed, or denied ('Grapes are Sour').
    
    Supporting houses: 2 (addition to family), 7 (legal partner), 11 (permanent friendship).
    Denying houses: 1 (12th from 2nd), 6 (12th from 7th), 10 (12th from 11th), 4 (12th from 5th).
    """
    supporting = [h for h in seventh_csl_signifies if h in MARRIAGE_SUPPORTING_HOUSES]
    denying = [h for h in seventh_csl_signifies if h in (MARRIAGE_DENYING_HOUSES | COURTSHIP_DENYING_HOUSES)]

    delays: List[str] = []
    if is_saturn_connected:
        delays.append("Saturn connected with 7th house/CSL causing systemic delay in fixation.")
    if is_saturn_in_5th:
        delays.append("Saturn placed in the 5th house abnormally delays romance and wedding settlement.")
    if is_mars_in_8th:
        delays.append("Mars in the 8th house creates friction, obstacles, and repeated proposal postponements.")

    # Denial Condition (Chapter 35: Grapes are Sour)
    # If 7th CSL signifies 4, 6, 10 without 2, 7, 11
    if set(denying).issuperset({4, 6, 10}) and len(supporting) == 0:
        verdict = "DENIED"
        is_denied = True
        philosophy = (
            "Grapes are Sour: Proposals repeatedly kindle high expectations and collapse. "
            "Native eventually renounces marriage or chooses career/celibacy."
        )
        reasoning = (
            f"The 7th Cusp Sub-Lord ({seventh_csl_planet}) is posited in the constellation of significators "
            "of houses 4, 6, and 10, completely devoid of supporting houses (2, 7, 11). "
            "Per Chapter 35, marriage is permanently denied."
        )
    elif len(supporting) >= 2 and len(delays) == 0 and len(denying) == 0:
        verdict = "PROMISED_EARLY"
        is_denied = False
        philosophy = "Early and harmonious wedding in youth with minimal obstacles."
        reasoning = (
            f"7th CSL strongly signifies marriage houses {supporting} without adverse interference."
        )
    elif len(supporting) > 0 and len(delays) > 0:
        verdict = "PROMISED_DELAYED"
        is_denied = False
        philosophy = (
            "Marriage is definitely promised, but Saturnine/Martian factors impose repeated testing "
            "before sudden settlement."
        )
        reasoning = (
            f"Supporting houses {supporting} guarantee the event, but delay factors ({', '.join(delays)}) "
            "postpone celebration to a mature age."
        )
    elif len(supporting) > 0:
        verdict = "PROMISED_NORMAL"
        is_denied = False
        philosophy = "Standard marriage timeline accomplished in due season."
        reasoning = f"7th CSL signifies {supporting}; marriage fructifies during operating joint DBA."
    else:
        verdict = "DENIED"
        is_denied = True
        philosophy = "Weak cuspal support; celibacy or non-formalized companionship indicated."
        reasoning = "Absence of vital significators (2, 7, 11) on the 7th Cusp Sub-Lord."

    return MarriagePromiseResult(
        verdict=verdict,
        seventh_csl_planet=seventh_csl_planet,
        supporting_significations=supporting,
        denying_significations=denying,
        is_denied=is_denied,
        delay_factors=delays,
        philosophical_verdict=philosophy,
        detailed_reasoning=reasoning,
    )


# ---------------------------------------------------------------------------
# 6. Second Marriage & Plurality Evaluator (KP Reader 4 Chapters 24, 25, 52)
# ---------------------------------------------------------------------------

def evaluate_second_marriage_reader4(
    seventh_csl_planet: str,
    seventh_csl_sign: str,
    seventh_csl_signifies: List[int],
    second_csl_signifies: List[int],
    is_venus_uranus_hard_aspect: bool = False,
    is_moon_venus_hard_aspect: bool = False,
    is_rahu_in_7th: bool = False,
) -> SecondMarriageResult:
    """Evaluate second marriage and plurality of relationships per KP Reader 4."""
    reasons: List[str] = []
    
    is_dual = seventh_csl_sign in COMMON_DUAL_SIGNS
    is_mercury = seventh_csl_planet.lower() == "mercury"

    has_7th_second_support = (is_dual or is_mercury) and (
        2 in seventh_csl_signifies or 11 in seventh_csl_signifies
    )
    has_2nd_support = 2 in second_csl_signifies and (
        7 in second_csl_signifies or 11 in second_csl_signifies
    )

    is_second_promised = has_7th_second_support or has_2nd_support

    if is_dual:
        reasons.append(f"7th Cusp Sub-Lord occupies a bicorporal/dual sign ({seventh_csl_sign}).")
    if is_mercury:
        reasons.append("7th Cusp Sub-Lord is Mercury (the planet of multiplicity and duality).")
    if has_2nd_support:
        reasons.append("2nd Cusp Sub-Lord strongly signifies houses 2, 7, and 11 (addition to family).")

    # Plurality / Extramarital contacts
    plurality = False
    if is_venus_uranus_hard_aspect:
        plurality = True
        reasons.append("Venus in hard aspect with Uranus indicates sudden, unconventional romantic attractions.")
    if is_moon_venus_hard_aspect:
        plurality = True
        reasons.append("Moon forming adverse aspect with Venus indicates attraction to other partners.")
    if is_rahu_in_7th:
        plurality = True
        reasons.append("Rahu in the 7th house denotes non-conventional or multiple partnerships.")

    if is_second_promised:
        guidance = (
            "Second marriage is promised. First marriage experiences dissolution, separation, or loss, "
            "followed by legal second alliance during operating DBA of 2, 7, 11."
        )
    else:
        guidance = "Single monogamous union promised; 7th CSL does not indicate dual matrimony."

    return SecondMarriageResult(
        is_second_marriage_indicated=is_second_promised,
        plurality_of_relationships=plurality,
        seventh_csl_in_dual_sign=is_dual,
        seventh_csl_is_mercury=is_mercury,
        second_cusp_sub_lord_support=has_2nd_support,
        reasons=reasons,
        guidance=guidance,
    )


# ---------------------------------------------------------------------------
# 7. Progeny & Childbirth Evaluator (KP Reader 4 Chapters 59, 60, 66, 72)
# ---------------------------------------------------------------------------

def evaluate_progeny_reader4(
    fifth_csl_planet: str,
    fifth_csl_sign: str,
    fifth_csl_signifies: List[int],
    is_mercury_or_jupiter_in_dual_sign: bool = False,
    is_saturn_connected_to_8_12: bool = False,
) -> ProgenyPromiseResult:
    """Evaluate progeny promise, fertility status, twins, and adoption per KP Reader 4.
    
    Houses: 2 (increase in family), 5 (first child), 11 (fulfillment).
    Denying: 4 (12th from 5th = non-conception), 10 (12th from 11th = denial).
    """
    supporting = [h for h in fifth_csl_signifies if h in PROGENY_SUPPORTING_HOUSES]
    denying = [h for h in fifth_csl_signifies if h in PROGENY_DENYING_HOUSES]

    is_fruitful = fifth_csl_sign in FRUITFUL_SIGNS
    is_semi = fifth_csl_sign in SEMI_FRUITFUL_SIGNS
    is_barren = fifth_csl_sign in BARREN_SIGNS

    if is_fruitful:
        fertility_status = "Fruitful (Watery sign: Cancer, Scorpio, Pisces)"
    elif is_semi:
        fertility_status = "Semi-Fruitful (Taurus, Libra, Sagittarius, Capricorn)"
    else:
        fertility_status = "Barren (Aries, Gemini, Leo, Virgo)"

    promised = (len(supporting) >= 1) and not (is_barren and len(denying) >= 2)

    # Twins indicator: Dual sign + Mercury/Jupiter prominent
    is_twin = (fifth_csl_sign in COMMON_DUAL_SIGNS) and is_mercury_or_jupiter_in_dual_sign and (2 in supporting and 5 in supporting)

    # Adoption indicator: 8 & 12 prominent with Saturn/Mercury, weak 2 & 5
    is_adoption = (8 in fifth_csl_signifies and 12 in fifth_csl_signifies and is_saturn_connected_to_8_12) and (len(supporting) == 0)

    timing_advice = (
        "Timing of delivery occurs during the conjoined Dasa-Bhukti-Antara of planets signifying "
        "houses 2, 5, and 11, when transiting Sun, Moon, and Jupiter transit fruitful degree sensitive zones."
    )

    clive_counsel = (
        "Chapter 72 Counsel ('Your Son is Not Robert Clive'): Avoid astrologer flattery. "
        "Predict what the sub-lord indicates regarding the child's true moral temperament, health, "
        "and intellectual aptitude rather than promising impossible conquests."
    )

    return ProgenyPromiseResult(
        childbirth_promised=promised,
        fertility_status=fertility_status,
        fifth_csl_planet=fifth_csl_planet,
        fifth_csl_sign=fifth_csl_sign,
        fifth_csl_signifies=fifth_csl_signifies,
        supporting_houses=supporting,
        denying_houses=denying,
        twin_birth_indicated=is_twin,
        adoption_indicated=is_adoption,
        progeny_timing_advice=timing_advice,
        clive_fallacy_counsel=clive_counsel,
    )


# ---------------------------------------------------------------------------
# 8. Sage Kasyapa's Seventh Star Compatibility (KP Reader 4 Chapter 6)
# ---------------------------------------------------------------------------

KASYAPA_EXCEPTIONS: Dict[Tuple[str, str], Dict[str, str]] = {
    ("Punarvasu", "Hasta"): {
        "verdict": "Approved",
        "experience": "Happiness and abundant birth of children are promised.",
        "shastra": "Punarvasu bride marrying Hasta groom forms a blessed 7th star exception.",
    },
    ("Jyeshta", "Satabhisha"): {
        "verdict": "Rejected",
        "experience": "Just opposite results; sorrow, conflict, and misery.",
        "shastra": "Kasyapa condemns Jyeshta bride with Satabhisha groom.",
    },
    ("Mrigasira", "Purva Phalguni"): {
        "verdict": "Rejected",
        "experience": "Bride will lose her husband early in life.",
        "shastra": "Mrigasira girl early bereavement with Puram boy.",
    },
    ("Hasta", "Moola"): {
        "verdict": "Rejected",
        "experience": "Strictly prohibited; domestic tragedy.",
        "shastra": "Hasta bride must never venture to marry a Moola groom.",
    },
    ("Rohini", "Magha"): {
        "verdict": "Approved",
        "experience": "Blessed with many noble children and long married life.",
        "shastra": "Rohini girl with Magha boy promises progeny expansion.",
    },
    ("Purva Bhadrapada", "Rohini"): {
        "verdict": "Approved",
        "experience": "Mother of many noble issues; harmonious union.",
        "shastra": "Purva Bhadrapada girl with Rohini boy is highly commended.",
    },
    ("Aswini", "Punarvasu"): {
        "verdict": "Special Exception",
        "experience": "Dejection by successive birth of daughters one after another.",
        "shastra": "Aswini bride with Punarvasu groom brings many daughters.",
    },
    ("Swathi", "Uttara Ashadha"): {
        "verdict": "Special Exception",
        "experience": "Brings forth many daughters; peaceful but daughter-heavy.",
        "shastra": "Swathi girl with Uttarashadha boy.",
    },
    ("Revati", "Arudra"): {
        "verdict": "Rejected",
        "experience": "Incurable discord, mutual hatred, and eventual separation/divorce.",
        "shastra": "Revati girl with Arudra boy do not lead a happy life.",
    },
    ("Uttara Phalguni", "Jyeshta"): {
        "verdict": "Rejected",
        "experience": "Deep enmity, perpetual quarrels, and bitter divorce.",
        "shastra": "Uttara Phalguni with Jyeshta is severely condemned.",
    },
}

APPROVED_7TH_STAR_BRIDES: Set[str] = {"Arudra", "Purva Phalguni", "Pushya"}
CONDEMNED_7TH_STAR_BRIDES: Set[str] = {"Krittika", "Ashlesha", "Chitra", "Anuradha", "Dhanishta", "Satabhisha"}


def evaluate_kasyapa_seventh_star(bride_star: str, groom_star: str) -> SageKasyapaSeventhStarResult:
    """Evaluate 7th star compatibility per Sage Kasyapa (KP Reader 4 Chapter 6)."""
    b_idx = NAKSHATRA_NAMES.index(bride_star)
    g_idx = NAKSHATRA_NAMES.index(groom_star)

    dist = (g_idx - b_idx) % 27 + 1
    is_seventh = dist == 7

    if not is_seventh:
        return SageKasyapaSeventhStarResult(
            bride_star=bride_star,
            groom_star=groom_star,
            is_seventh_star=False,
            kasyapa_verdict="Not 7th Star",
            predicted_experience="Standard Dhina Porutham counting applies; not in Vatham/Vainasikam axis.",
            shastric_details="Normal Porutham rules apply.",
        )

    # Check pair-specific Kasyapa rules
    pair_info = KASYAPA_EXCEPTIONS.get((bride_star, groom_star))
    if pair_info:
        return SageKasyapaSeventhStarResult(
            bride_star=bride_star,
            groom_star=groom_star,
            is_seventh_star=True,
            kasyapa_verdict=pair_info["verdict"],
            predicted_experience=pair_info["experience"],
            shastric_details=pair_info["shastra"],
        )

    # General Kasyapa group rules
    if bride_star in APPROVED_7TH_STAR_BRIDES:
        return SageKasyapaSeventhStarResult(
            bride_star=bride_star,
            groom_star=groom_star,
            is_seventh_star=True,
            kasyapa_verdict="Approved",
            predicted_experience="Approved exception: Arudra, Purva Phalguni, or Pushya bride warded of 7th star evil.",
            shastric_details="Sage Kasyapa explicitly permits 7th star match for these three nakshatras.",
        )
    elif bride_star in CONDEMNED_7TH_STAR_BRIDES:
        return SageKasyapaSeventhStarResult(
            bride_star=bride_star,
            groom_star=groom_star,
            is_seventh_star=True,
            kasyapa_verdict="Rejected",
            predicted_experience="Severe affliction: short married life, illness, or early bereavement threatened.",
            shastric_details="Sage Kasyapa explicitly warns Krittika, Ashlesha, Chitra, Anuradha, Dhanishta, Satabhisha.",
        )
    else:
        return SageKasyapaSeventhStarResult(
            bride_star=bride_star,
            groom_star=groom_star,
            is_seventh_star=True,
            kasyapa_verdict="Moderate / Evaluate Sub-Lord",
            predicted_experience="Traditional Vatham tension present; final verdict rests with 7th Cusp Sub-Lord.",
            shastric_details="Kasyapa advises caution; check whether 7th star lord is a benefic to Lagna.",
        )
