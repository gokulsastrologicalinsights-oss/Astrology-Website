"""Models and Data Schemas for K.N. Rao Advanced Astrological Research Engine.

Based on the research treatise 'Advanced Techniques of Astrological Predictions'
(Vedic Astrology Series, B.P.E.S.V. Sansthan / Bharatiya Vidya Bhavan, New Delhi).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# S.N. Kapoor: Service vs Self-Employment Models
# ---------------------------------------------------------------------------

class ServiceVsSelfEmploymentResult(BaseModel):
    """Evaluation of Service vs Self-Employment propensity using S.N. Kapoor's thumb rules."""
    planets_in_7_to_12: int = Field(description="Planets in visible half (7th to 12th houses)")
    planets_in_10_to_3: int = Field(description="Planets in executive axis (10th to 3rd houses)")
    planets_in_4_to_6: int = Field(description="Planets in subordination zone (4th to 6th houses)")
    poorna_parmatmansha_count: int = Field(description="Poorna Parmatmansha planets (Sun, Moon, Mars, Rahu) in 7-12 or 10-3")
    parmatmansha_nakshatras_count: int = Field(description="Planets occupying Parmatmansha nakshatras")
    tattwa_distribution: Dict[str, int] = Field(description="Planetary distribution by element: Agni, Prithvi, Vayu, Jala")
    agni_vayu_count: int = Field(description="Total planets in Agni and Vayu signs (promotes enterprise)")
    prithvi_jala_count: int = Field(description="Total planets in Prithvi and Jala signs (promotes service)")
    is_day_birth: bool = Field(description="Whether born between sunrise and sunset (Sun in 7th to 12th)")
    is_sunset_to_midnight: bool = Field(description="Whether born between sunset and midnight (Sun in 4th, 5th, or 6th)")
    saturn_status: str = Field(description="Gocharastha (exalted/own/unafflicted) vs Agocharastha (debilitated/combust/trik)")
    saturn_aspects_career: bool = Field(description="Whether Saturn aspects Moon, 10th house, 10th lord, or Lagna")
    lagna_lord_avastha: str = Field(description="Dignity and placement of Lagna lord")
    tenth_lord_avastha: str = Field(description="Dignity and placement of 10th lord")
    self_employment_probability: float = Field(description="Probability percentage of Self-Employment / Business (0-100%)")
    service_probability: float = Field(description="Probability percentage of Service / Employment (0-100%)")
    primary_verdict: str = Field(description="Primary vocational trajectory: Self-Employment or Service")
    verdict_tamil: str = Field(description="Tamil translation of vocational trajectory")
    rule_score_breakdown: Dict[str, Any] = Field(default_factory=dict)
    contributing_factors: List[str] = Field(default_factory=list)
    contributing_factors_tamil: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# R.C. Sharma: Technical vs Non-Technical Career Models
# ---------------------------------------------------------------------------

class TechnicalProfessionResult(BaseModel):
    """Evaluation of Technical vs Non-Technical profession using R.C. Sharma's mathematical scoring model."""
    karakamsha_sign: str = Field(description="Karakamsha sign (Navamsha sign of Atmakaraka)")
    score_karakamsha_10th: int = Field(description="Net score from 10th house & 10th lord of Karakamsha")
    score_lagna_10th: int = Field(description="Net score from 10th house & 10th lord of Janma Lagna")
    score_moon_10th: int = Field(description="Net score from 10th house & 10th lord of Chandra Lagna")
    score_nakshatra_10th: int = Field(description="Net score from Nakshatras of 10th lord and 10th house")
    total_score: int = Field(description="Cumulative 4-fold score (negative = technical, positive = non-technical)")
    category: str = Field(description="Technical (Engineering/IT), Semi-Technical, or Non-Technical (Arts/Admin)")
    category_tamil: str = Field(description="Tamil category description")
    rahu_engineering_prominence: bool = Field(description="Whether Rahu significantly influences 10th house/lord, marking engineering")
    technical_planets_influencing: List[str] = Field(default_factory=list)
    non_technical_planets_influencing: List[str] = Field(default_factory=list)
    detailed_breakdown: Dict[str, Any] = Field(default_factory=dict)
    interpretation: str
    interpretation_tamil: str


# ---------------------------------------------------------------------------
# Col. A.K. Gour: Authors & Journalists Models
# ---------------------------------------------------------------------------

class AuthorJournalistResult(BaseModel):
    """Evaluation of Author vs Journalist literary talents using Col. A.K. Gour's principles."""
    pac_bond_present: bool = Field(description="Position-Aspect-Conjunction bonding of 3rd, 5th, 10th lords, Mercury, and Jupiter")
    jupiter_prominence: bool = Field(description="Jupiter dominates: steady, deep, author of books/granths")
    mercury_prominence: bool = Field(description="Mercury dominates: quick, witty, journalistic writer")
    mars_mercury_bond: bool = Field(description="Mars (ink) and Mercury (paper) bond: aspect, sign exchange, or mutual link")
    mars_mercury_bond_details: str
    jaimini_writing_aspects: bool = Field(description="2nd, 3rd, 5th lords, Mercury, and Jupiter in Jaimini mutual aspects")
    karakamsha_influences: List[str] = Field(default_factory=list, description="Planets posited or aspecting 2nd, 3rd, 5th from Karakamsha")
    writing_profile: str = Field(description="Author, Journalist, Author-cum-Journalist, or Non-Literary")
    writing_profile_tamil: str
    synthesis: str
    synthesis_tamil: str


# ---------------------------------------------------------------------------
# Shunny Nigam & Shiv Raj Sharma: Marital Discord & Upapada Models
# ---------------------------------------------------------------------------

class MaritalDiscordResult(BaseModel):
    """Evaluation of Marital Harmony vs Discord using Shunny Nigam & Shiv Raj Sharma's 4 Main + 2 Supplementary Rules."""
    upapada_lagna_sign: str = Field(description="Upapada Lagna sign name (Arudha of 12th house)")
    second_from_upapada_sign: str = Field(description="2nd house from Upapada Lagna sign name")
    malefics_in_second_from_ul: List[str] = Field(default_factory=list, description="Natural malefics in 2nd from UL (Rule A - 96% accuracy)")
    jaimini_malefic_aspects_on_second_from_ul: List[str] = Field(default_factory=list)
    rule_a_matched: bool = Field(description="Rule A: Malefic affliction on 2nd house from Upapada Lagna")
    rule_b_matched: bool = Field(description="Rule B: Natal 7th lord debilitated, combust, or afflicted in Navamsha D9 (64% accuracy)")
    rule_c_matched: bool = Field(description="Rule C: Venus afflicted in Rashi chart (64% accuracy)")
    rule_d_matched: bool = Field(description="Rule D: 6th, 8th, or 12th lords associated with 7th house or 7th lord (84% accuracy)")
    supplementary_shadashtaka: bool = Field(description="Supplementary 1: Lagna lord and 7th lord in 6/8 mutual position (16% friction)")
    supplementary_al_darapada_tension: bool = Field(description="Supplementary 2: Arudha Lagna (AL) and Darapada (A7) in 6/8 or 2/12 position")
    main_rules_matched_count: int = Field(description="Number of main rules matched (0 to 4)")
    discord_intensity: str = Field(description="High Discord Risk, Moderate Friction, Mild / Stressful, or Peaceful / Harmonious")
    discord_intensity_tamil: str
    active_dasha_discord_triggers: List[str] = Field(default_factory=list, description="Dasha periods of 5th/6th/8th lords or planets in 6th/8th from Lagna or Darakaraka")
    darakaraka_planet: str = Field(description="Jaimini Darakaraka (planet with lowest degree)")
    darakaraka_dasha_analysis: str = Field(description="Vimshottari Darakaraka status and marriage fruition/discord analysis")
    reasons: List[str] = Field(default_factory=list)
    reasons_tamil: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Dr. R.K. Aggarwal & P.C. Verma: Consolidated Kakshya Chart & Vimshottari 8-Part Timing
# ---------------------------------------------------------------------------

class KakshyaSegmentItem(BaseModel):
    kakshya_num: int
    kakshya_lord: str
    degree_range: str
    total_bindus: int
    auspicious: bool = Field(description="True if total bindus >= 4, False if < 4")


class ConsolidatedSignKakshya(BaseModel):
    sign_index: int
    sign_name: str
    sign_name_tamil: str
    total_sav_bindus: int
    kakshyas: List[KakshyaSegmentItem]


class VimshottariEightPartItem(BaseModel):
    part_num: int
    kakshya_lord: str
    tenth_lord_prastharaka_bindu: int = Field(description="1 (+) or 0 (-)")
    favorable_for_career: bool
    career_indication: str
    career_indication_tamil: str


class ConsolidatedKakshyaResponse(BaseModel):
    """Dr. R.K. Aggarwal's Table III Consolidated Kakshya Chart + P.C. Verma's 8-Part Timing."""
    matrix: List[ConsolidatedSignKakshya]
    tenth_lord: str
    tenth_lord_rashi: str
    active_mahadasha_lord: Optional[str] = None
    vimshottari_eight_parts: List[VimshottariEightPartItem] = Field(default_factory=list)
    current_transits_evaluations: List[Dict[str, Any]] = Field(default_factory=list)
    summary_insight: str
    summary_insight_tamil: str


# ---------------------------------------------------------------------------
# Dr. K.S. Charak: Medical Astrology Timing Models
# ---------------------------------------------------------------------------

class MrityuBhagaPlanetItem(BaseModel):
    planet: str
    sign: str
    degree_in_sign: float
    mrityu_bhaga_degree: float
    difference_deg: float
    is_in_mrityu_bhaga: bool


class MedicalTimingResult(BaseModel):
    """Dr. K.S. Charak's Disease Onset, Progression, and Outcome Prognosis."""
    planets_in_mrityu_bhaga: List[MrityuBhagaPlanetItem] = Field(default_factory=list)
    dasha_lords_health_risk: List[str] = Field(default_factory=list)
    trik_lord_connections: List[str] = Field(default_factory=list)
    rahu_ketu_axis_on_dasha_lords: bool
    retrograde_benefics_in_kendras: List[str] = Field(default_factory=list, description="Benefics that fail to protect due to retrogression or malefic aspect")
    subsequent_dasha_prognosis: str = Field(description="Recovery expected under benefic subsequent dasha vs prolonged complications")
    subsequent_dasha_prognosis_tamil: str
    prognosis_verdict: str
    prognosis_verdict_tamil: str
    protective_factors: List[str] = Field(default_factory=list)
    adverse_factors: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Master K.N. Rao Advanced Research Bundle Response
# ---------------------------------------------------------------------------

class KnRaoAdvancedResearchResponse(BaseModel):
    """Unified response bundling all empirical research findings from 'Advanced Techniques of Astrological Predictions'."""
    service_vs_self_employment: ServiceVsSelfEmploymentResult
    technical_profession: TechnicalProfessionResult
    author_vs_journalist: AuthorJournalistResult
    marital_discord: MaritalDiscordResult
    medical_timing: MedicalTimingResult
    jaimini_karakas: Dict[str, str] = Field(description="AK, AmK, BK, MK, PK, GK, DK planet mapping")
    karakamsha_sign: str
    arudha_lagna: str
    upapada_lagna: str
    darapada: str
