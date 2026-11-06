"""Pydantic schemas for KP Reader 4 (Marriage, Married Life & Children) endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Mars Dosha Schemas
# ---------------------------------------------------------------------------

class MarsDoshaSourceDetailSchema(BaseModel):
    reference_point: str = Field(..., description="'Lagna', 'Moon', or 'Venus'")
    reference_sign: str = Field(..., description="Zodiac sign of the reference point")
    mars_sign: str = Field(..., description="Zodiac sign occupied by Mars")
    counted_house: int = Field(..., ge=1, le=12, description="House distance (1-12) sign-to-sign")
    has_dosha: bool = Field(..., description="Whether Mars falls in 1, 2, 4, 7, 8, or 12")
    dosha_weight: float = Field(..., description="Weight (Venus 3.0, Moon 2.0, Lagna 1.0)")
    reasons: List[str] = Field(default_factory=list)


class MarsDoshaPariharaSchema(BaseModel):
    rule_id: str = Field(..., description="Classical parihara identifier")
    rule_name: str = Field(..., description="Name of the mitigation rule")
    description: str = Field(..., description="Shastric principle from KP Reader 4")
    applies: bool = Field(..., description="Whether this parihara is satisfied in chart")


class MarsDoshaRequest(BaseModel):
    mars_sign: str = Field(..., description="Zodiac sign of Mars (e.g. 'Aries')")
    lagna_sign: str = Field(..., description="Zodiac sign of Lagna (Ascendant)")
    moon_sign: str = Field(..., description="Zodiac sign of Moon (Janma Rasi)")
    venus_sign: str = Field(..., description="Zodiac sign of Venus")
    is_mars_conjunct_or_aspected_by_jupiter: bool = Field(
        False, description="Mars conjoined with or aspected by Jupiter"
    )
    is_mars_conjunct_or_aspected_by_mercury: bool = Field(
        False, description="Mars conjoined with or aspected by Mercury"
    )
    is_mars_conjunct_moon: bool = Field(
        False, description="Chandra-Mangala yoga (Moon and Mars conjunct)"
    )
    is_mars_conjunct_jupiter_within_8deg: bool = Field(
        False, description="Guru-Mangala yoga within 8° orb"
    )
    seventh_csl_signifies_6_10_12: bool = Field(
        False, description="Whether 7th Cuspal Sub-Lord signifies denying houses 6, 10, or 12"
    )


class MarsDoshaResponse(BaseModel):
    raw_dosha_present: bool = Field(..., description="Whether Mars occupies 1, 2, 4, 7, 8, 12 from any point")
    total_score: float = Field(..., description="Sum of weighted dosha scores")
    source_details: List[MarsDoshaSourceDetailSchema] = Field(..., description="Breakdown from Lagna, Moon, Venus")
    pariharas_applicable: List[MarsDoshaPariharaSchema] = Field(..., description="Applicable cancellation rules")
    is_mitigated: bool = Field(..., description="Whether classical pariharas neutralize the dosha")
    kp_cuspal_override: str = Field(..., description="KP 7th Cuspal Sub-Lord definitive ruling")
    recommendation: str = Field(..., description="Partner matching guidance")
    shastric_verdict: str = Field(..., description="Summary verdict (Suddha Jathakam / Parihara / Operative)")


# ---------------------------------------------------------------------------
# 2. Punarphoo Schemas
# ---------------------------------------------------------------------------

class PunarphooRequest(BaseModel):
    saturn_sign: str = Field(..., description="Zodiac sign of Saturn")
    moon_sign: str = Field(..., description="Zodiac sign of Moon")
    saturn_star: str = Field(..., description="Nakshatra of Saturn (e.g. 'Pushya')")
    moon_star: str = Field(..., description="Nakshatra of Moon (e.g. 'Rohini')")
    saturn_sub: str = Field(..., description="Sub-Lord of Saturn")
    moon_sub: str = Field(..., description="Sub-Lord of Moon")
    saturn_house: int = Field(1, ge=1, le=12, description="House occupied by Saturn")
    moon_house: int = Field(1, ge=1, le=12, description="House occupied by Moon")
    saturn_aspects_moon: bool = Field(False, description="Whether Saturn aspects Moon (3rd, 7th, 10th drishti)")
    is_rahu_or_ketu_representing_saturn_or_moon: bool = Field(
        False, description="Whether a Node (Rahu/Ketu) reflects Saturn or Moon"
    )


class PunarphooResponse(BaseModel):
    is_punarphoo_present: bool = Field(..., description="Whether Saturn-Moon impediment exists")
    severity: str = Field(..., description="'None', 'Mild', 'Moderate', or 'Severe'")
    connections_found: List[str] = Field(default_factory=list, description="Specific astrological linkages")
    case_study_analogy: str = Field(..., description="Analogy to Prof. Krishnamurti's 4 famous cases")
    predicted_impediments: List[str] = Field(default_factory=list, description="Specific life manifestations")
    kp_counsel: str = Field(..., description="Actionable timing and negotiation counsel")


# ---------------------------------------------------------------------------
# 3. Spouse Physical Appearance Schemas
# ---------------------------------------------------------------------------

class SpouseAppearanceRequest(BaseModel):
    csl_planet: str = Field(..., description="Sub-Lord of the 7th Cusp (e.g. 'Venus')")
    csl_sign: str = Field(..., description="Zodiac sign of 7th Cusp Sub-Lord (e.g. 'Libra')")
    node_conjunction: Optional[str] = Field(None, description="Planet conjunct with Node (if CSL is Rahu/Ketu)")
    node_aspect: Optional[str] = Field(None, description="Planet aspecting Node (if CSL is Rahu/Ketu)")
    node_star_lord: Optional[str] = Field(None, description="Star Lord of Node (if CSL is Rahu/Ketu)")


class SpouseAppearanceResponse(BaseModel):
    csl_planet: str
    csl_sign: str
    stature: str = Field(..., description="Height, build, and physical frame")
    complexion_and_face: str = Field(..., description="Facial shape, eyes, hair, and complexion")
    temperament: str = Field(..., description="Psychological, moral, and emotional temperament")
    vocational_and_lifestyle_traits: str = Field(..., description="Career, hobbies, and social tendencies")
    cautionary_notes: Optional[str] = Field(None, description="Special warnings from KP Reader 4")
    shastric_quote: str = Field("", description="Node resolution or shastric note")


# ---------------------------------------------------------------------------
# 4. Career Spouse Schemas
# ---------------------------------------------------------------------------

class CareerSpouseRequest(BaseModel):
    fourth_csl_planet: str = Field(..., description="Sub-Lord of the 4th Cusp (10th of spouse)")
    fourth_csl_signifies: List[int] = Field(..., description="Houses signified by 4th CSL (e.g. [4, 8, 12])")
    is_mars_involved: bool = Field(False, description="Whether Mars is connected to 4th CSL")


class CareerSpouseResponse(BaseModel):
    will_marry_career_spouse: bool = Field(..., description="Whether native marries a career woman / working partner")
    fourth_csl_planet: str
    fourth_csl_signifies: List[int]
    matching_houses: List[int] = Field(..., description="Matching houses among 4, 8, 12")
    spouse_vocation_type: str = Field(..., description="Predicted vocational status of partner")
    explanation: str = Field(..., description="Detailed KP Chapter 32 astrological explanation")


# ---------------------------------------------------------------------------
# 5. Marriage Promise & Denial Schemas
# ---------------------------------------------------------------------------

class MarriagePromiseRequest(BaseModel):
    seventh_csl_planet: str = Field(..., description="Sub-Lord of 7th Cusp")
    seventh_csl_signifies: List[int] = Field(..., description="Houses signified by 7th CSL")
    is_saturn_connected: bool = Field(False, description="Saturn connected with 7th house/CSL")
    is_saturn_in_5th: bool = Field(False, description="Saturn posited in 5th house")
    is_mars_in_8th: bool = Field(False, description="Mars posited in 8th house")


class MarriagePromiseResponse(BaseModel):
    verdict: str = Field(..., description="'PROMISED_EARLY', 'PROMISED_NORMAL', 'PROMISED_DELAYED', 'DENIED'")
    seventh_csl_planet: str
    supporting_significations: List[int] = Field(..., description="Significations among 2, 7, 11")
    denying_significations: List[int] = Field(..., description="Significations among 1, 6, 10, 4")
    is_denied: bool = Field(..., description="Whether marriage is denied ('Grapes are Sour')")
    delay_factors: List[str] = Field(default_factory=list, description="Factors delaying celebration")
    philosophical_verdict: str = Field(..., description="KP philosophical summary")
    detailed_reasoning: str = Field(..., description="Full cuspal logic")


# ---------------------------------------------------------------------------
# 6. Second Marriage Schemas
# ---------------------------------------------------------------------------

class SecondMarriageRequest(BaseModel):
    seventh_csl_planet: str = Field(..., description="Sub-Lord of 7th Cusp")
    seventh_csl_sign: str = Field(..., description="Zodiac sign of 7th CSL")
    seventh_csl_signifies: List[int] = Field(..., description="Houses signified by 7th CSL")
    second_csl_signifies: List[int] = Field(..., description="Houses signified by 2nd CSL")
    is_venus_uranus_hard_aspect: bool = Field(False, description="Venus-Uranus hard aspect")
    is_moon_venus_hard_aspect: bool = Field(False, description="Moon-Venus hard aspect")
    is_rahu_in_7th: bool = Field(False, description="Rahu posited in 7th house")


class SecondMarriageResponse(BaseModel):
    is_second_marriage_indicated: bool = Field(..., description="Whether second marriage is indicated")
    plurality_of_relationships: bool = Field(..., description="Whether multiple affairs/plurality is present")
    seventh_csl_in_dual_sign: bool = Field(..., description="Whether 7th CSL is in dual sign")
    seventh_csl_is_mercury: bool = Field(..., description="Whether 7th CSL is Mercury")
    second_cusp_sub_lord_support: bool = Field(..., description="Whether 2nd CSL signifies 2, 7, 11")
    reasons: List[str] = Field(default_factory=list)
    guidance: str = Field(..., description="Marital counsel and trajectory")


# ---------------------------------------------------------------------------
# 7. Progeny Promise Schemas
# ---------------------------------------------------------------------------

class ProgenyPromiseRequest(BaseModel):
    fifth_csl_planet: str = Field(..., description="Sub-Lord of 5th Cusp")
    fifth_csl_sign: str = Field(..., description="Zodiac sign of 5th CSL")
    fifth_csl_signifies: List[int] = Field(..., description="Houses signified by 5th CSL")
    is_mercury_or_jupiter_in_dual_sign: bool = Field(False, description="Mercury/Jupiter in dual sign")
    is_saturn_connected_to_8_12: bool = Field(False, description="Saturn connected to 8 and 12")


class ProgenyPromiseResponse(BaseModel):
    childbirth_promised: bool = Field(..., description="Whether childbirth is promised")
    fertility_status: str = Field(..., description="'Fruitful', 'Semi-Fruitful', or 'Barren / Impeded'")
    fifth_csl_planet: str
    fifth_csl_sign: str
    fifth_csl_signifies: List[int]
    supporting_houses: List[int] = Field(..., description="Significations among 2, 5, 11")
    denying_houses: List[int] = Field(..., description="Significations among 4, 10")
    twin_birth_indicated: bool = Field(..., description="Whether twin birth is indicated")
    adoption_indicated: bool = Field(..., description="Whether adoption is indicated")
    progeny_timing_advice: str = Field(..., description="Timing instructions for delivery")
    clive_fallacy_counsel: str = Field(..., description="Counsel regarding child's true future")


# ---------------------------------------------------------------------------
# 8. Sage Kasyapa 7th Star Schemas
# ---------------------------------------------------------------------------

class KasyapaSeventhStarRequest(BaseModel):
    bride_star: str = Field(..., description="Nakshatra of the bride (e.g. 'Punarvasu')")
    groom_star: str = Field(..., description="Nakshatra of the groom (e.g. 'Hasta')")


class KasyapaSeventhStarResponse(BaseModel):
    bride_star: str
    groom_star: str
    is_seventh_star: bool = Field(..., description="Whether groom's star is 7th from bride's")
    kasyapa_verdict: str = Field(..., description="'Approved', 'Rejected', or 'Special Exception'")
    predicted_experience: str = Field(..., description="Specific marital life experience")
    shastric_details: str = Field(..., description="Sage Kasyapa's historical aphorism")
