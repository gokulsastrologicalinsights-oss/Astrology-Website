"""Schemas for rule-based analysis (Marriage compatibility and Career indicators)."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class RuleAuditNote(BaseModel):
    rule_id: str
    rule_name: str
    tradition: str  # e.g., "Parashara", "KP", "Jaimini", "South Indian / Tamil"
    status: str  # "Implemented", "Draft", "Requires Verification", "Pending Canon Specification"
    description: str
    documentation_ref: Optional[str] = None


class KujaDoshaStatus(BaseModel):
    has_dosha: bool
    mars_house_from_lagna: Optional[int] = None
    mars_house_from_moon: Optional[int] = None
    mars_house_from_venus: Optional[int] = None
    is_cancelled: bool = False
    cancellation_reasons: List[str] = Field(default_factory=list)
    pending_rules: List[str] = Field(
        default_factory=lambda: [
            "Mars in own/exaltation sign cancellation (Mesha, Vrishchika, Makara)",
            "Mars in Jupiter/Mercury houses cancellation (Dhanus, Meena, Mithuna, Kanya)",
            "Benefic Jupiter aspect cancellation",
            "Mutual Kuja Dosha pairing parity",
        ]
    )


class CompatibilitySummary(BaseModel):
    groom_nakshatra: str
    bride_nakshatra: str
    total_score: float
    max_score: float = 36.0
    status: str  # "Draft Heuristic Only - Not for Real-World Decisions"
    kutas_evaluated: Dict[str, float] = Field(default_factory=dict)
    kuja_dosha_groom: KujaDoshaStatus
    kuja_dosha_bride: KujaDoshaStatus
    dasa_sandhi_note: str = "Pending exact ephemeris intersection threshold implementation"
    outstanding_work: List[str] = Field(
        default_factory=lambda: [
            "Complete 10-Porutham South Indian canon integration",
            "Dasa Sandhi vulnerability window (less than 1 year overlap between major ending dasas)",
            "Ashtakoota exceptions for identical rasi lords",
            "Rajju dosha absolute cancellation rules",
        ]
    )


class CareerAnalysisSummary(BaseModel):
    tenth_house_sign: str
    tenth_house_lord: str
    tenth_house_occupants: List[str] = Field(default_factory=list)
    planets_aspecting_tenth: List[str] = Field(default_factory=list)
    sun_position_sign: str
    mercury_position_sign: str
    jupiter_position_sign: str
    amatyakaraka: Optional[str] = None
    rule_notes: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "Astrological career indicators are based on traditional Vedic texts (Brihat Parashara Hora Shastra) "
        "and KP significator tables. They are deterministic symbolic heuristics for traditional cultural analysis, "
        "not scientifically proven predictive career counseling or professional advice."
    )
    outstanding_work: List[str] = Field(
        default_factory=lambda: [
            "Jaimini Karakamsha and Dashamsha (D10) divisional chart analysis",
            "Shadbala strength threshold integration for 10th lord and karakas",
            "KP 10th cusp sub-lord promise evaluation for profession",
            "Indu Lagna and Dhana yoga verification",
        ]
    )
