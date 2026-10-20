"""Pydantic schemas for the Unified Classical Dosha Engine.

Covers:
1. Kuja / Manglik Dosha (from Lagna, Moon, and Venus with classical cancellations).
2. Kaal Sarp Dosha (Full, Partial, Absent enclosure with 12 canonical subtypes).
3. Sadesati (Saturn's 7.5-year transit through 12th, 1st, 2nd from natal Moon, plus Kantaka and Ashtama).
4. Additional Classical Doshas (Pitru Dosha, Guru Chandal Dosha, Shrapit Dosha, Grahan Dosha).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import CalculationMetadata
from app.schemas.horoscope import HoroscopeRequest


class KujaDoshaReferenceDetail(BaseModel):
    """Kuja Dosha evaluation from a single reference point (Lagna, Moon, or Venus)."""
    reference_point: str = Field(..., description="Reference point: 'Lagna', 'Moon', or 'Venus'")
    reference_sign_index: int = Field(..., description="1-indexed zodiac sign of the reference point (1=Aries .. 12=Pisces)")
    reference_sign_name: str = Field(..., description="Zodiac sign name of the reference point")
    mars_house_from_reference: int = Field(..., description="House occupied by Mars from this reference point (1-12)")
    has_dosha: bool = Field(..., description="True if Mars occupies a Kuja house from this reference point")
    is_cancelled: bool = Field(..., description="True if classical cancellation rules neutralize the dosha from this reference point")
    cancellation_reasons: List[str] = Field(default_factory=list, description="Classical cancellation rules satisfied")
    effective_intensity_percent: float = Field(..., description="Effective intensity weight (100% Lagna, 75% Moon, 50% Venus, 0% if cancelled)")


class KujaDoshaResult(BaseModel):
    """Complete multi-reference Kuja / Manglik Dosha evaluation."""
    is_present: bool = Field(..., description="True if Kuja Dosha is formed from at least one reference point")
    is_cancelled: bool = Field(..., description="True if all detected Kuja Dosha manifestations are cancelled")
    severity: str = Field(..., description="Severity level: 'None', 'Cancelled', 'Mild', 'Moderate', or 'High'")
    house_convention: str = Field(..., description="Applied house convention, e.g. 'South Indian (1, 2, 4, 7, 8, 12)'")
    details_by_reference: Dict[str, KujaDoshaReferenceDetail] = Field(
        ...,
        description="Individual breakdowns evaluated from Lagna, Moon, and Venus"
    )
    cancellation_summary: Optional[str] = Field(None, description="Summary of active cancellation factors")
    interpretation: str = Field(..., description="Balanced classical and contemporary marital interpretation")
    interpretation_tamil: str = Field(..., description="Tamil interpretation and astrological guidance")


class KaalSarpResult(BaseModel):
    """Kaal Sarp Dosha evaluation analyzing planetary enclosure between the Rahu-Ketu nodal axis."""
    is_present: bool = Field(..., description="True if all or majority of classical planets are hemmed between Rahu and Ketu")
    dosha_type: str = Field(..., description="'Full', 'Partial', or 'Absent'")
    subtype_name: Optional[str] = Field(None, description="Classical subtype (Anant, Kulik, Vasuki, Shankhpal, etc.)")
    subtype_name_tamil: Optional[str] = Field(None, description="Tamil name of the Kaal Sarp subtype")
    rahu_house: int = Field(..., description="House occupied by Rahu from Lagna (1-12)")
    ketu_house: int = Field(..., description="House occupied by Ketu from Lagna (1-12)")
    direction: Optional[str] = Field(None, description="'Savya (Ascending)' or 'Apasavya (Descending)'")
    planets_inside: List[str] = Field(default_factory=list, description="Grahas completely enclosed between Rahu and Ketu")
    planets_outside: List[str] = Field(default_factory=list, description="Grahas situated outside the nodal axis")
    is_cancelled: bool = Field(..., description="True if classical mitigations (Kendra benefics, exalted planets) neutralize the dosha")
    cancellation_reasons: List[str] = Field(default_factory=list, description="Active mitigating factors")
    interpretation: str = Field(..., description="Balanced traditional interpretation emphasizing perseverance and delayed success")
    interpretation_tamil: str = Field(..., description="Tamil interpretation and guidance")


class SadesatiPhaseInfo(BaseModel):
    """Saturn's 7.5-year transit (Sadesati) relative to the natal Moon, plus Kantaka and Ashtama Shani."""
    is_active: bool = Field(..., description="True if native is currently undergoing Sadesati or Kantaka/Ashtama Shani")
    phase: str = Field(..., description="'Rising', 'Peak', 'Setting', 'Kantaka', 'Ashtama', or 'None'")
    phase_name_tamil: str = Field(..., description="Tamil nomenclature: 'விரைய சனி', 'ஜென்ம சனி', 'பாத சனி', 'கண்டக சனி', 'அஷ்டம சனி', 'இல்லை'")
    natal_moon_sign_index: int = Field(..., description="Zodiac sign index of natal Moon (1-12)")
    natal_moon_sign_name: str = Field(..., description="Name of natal Moon sign (Rasi)")
    transit_saturn_sign_index: int = Field(..., description="Zodiac sign index of transiting Saturn (1-12)")
    transit_saturn_sign_name: str = Field(..., description="Name of transiting Saturn sign")
    transit_saturn_degree_in_sign: float = Field(..., description="Degree of transiting Saturn in sign (0.0 to 30.0°)")
    saturn_is_retrograde: bool = Field(..., description="True if transiting Saturn is retrograde")
    house_from_moon: int = Field(..., description="House distance from natal Moon to transiting Saturn (1-12)")
    saturn_ashtakavarga_bindus: Optional[int] = Field(
        None,
        description="Saturn's natal BAV bindus in the transiting sign (>= 4 indicates favorable/constructive transit)"
    )
    nature_of_transit: str = Field(..., description="'Benefic / Constructive', 'Moderate / Disciplined', or 'Testing / Transformative'")
    interpretation: str = Field(..., description="Objective non-fatalistic description of Saturn's current transit lessons")
    interpretation_tamil: str = Field(..., description="Tamil guidance emphasizing patience, discipline, and practical remedies")


class SingleDoshaDetail(BaseModel):
    """Standardized representation for Pitru, Guru Chandal, Shrapit, and Grahan Doshas."""
    id: str = Field(..., description="Machine-readable identifier: pitru_dosha, guru_chandal_dosha, shrapit_dosha, grahan_dosha_sun, grahan_dosha_moon")
    name: str = Field(..., description="English/Sanskrit name of the Dosha")
    name_tamil: str = Field(..., description="Tamil name of the Dosha")
    is_present: bool = Field(..., description="True if triggering conditions are satisfied")
    is_cancelled: bool = Field(..., description="True if classical cancellation or mitigating factors operate")
    severity: str = Field(..., description="'None', 'Cancelled', 'Mild', 'Moderate', or 'High'")
    planets_involved: List[str] = Field(default_factory=list, description="Grahas forming or afflicting in this dosha")
    relevant_houses: List[int] = Field(default_factory=list, description="House numbers involved")
    conditions: List[str] = Field(default_factory=list, description="Specific triggers detected in the chart")
    cancellation_reasons: List[str] = Field(default_factory=list, description="Mitigating or neutralizing classical factors")
    interpretation: str = Field(..., description="Traditional and psychological significance")
    interpretation_tamil: str = Field(..., description="Tamil explanation and traditional remedy indications")
    classical_reference: str = Field(..., description="Classical textual authority")


class DoshaEvaluationItem(BaseModel):
    """Complete, normalized Vedic Dosha analysis item conforming to specification Section 7."""
    dosha_id: str = Field(..., description="Unique machine-readable identifier")
    name_en: str = Field(..., description="English/Sanskrit name of the dosha")
    name_ta: str = Field(..., description="Tamil name of the dosha")
    category: str = Field(
        ...,
        description="Category: 'Planetary Conjunction & Axis', 'Moon & Nakshatra', 'Lagna & House Placements', 'Marriage Compatibility', 'Transit'"
    )
    status: str = Field(
        ...,
        description="Explicit evaluation status: 'present', 'mitigated', 'absent', or 'indeterminate'"
    )
    reference_basis: str = Field(
        ...,
        description="Primary reference basis (e.g. 'Lagna', 'Moon', 'Venus', 'Transit Date', 'Partner Horoscope Required')"
    )
    formation_conditions: List[str] = Field(default_factory=list, description="Exact formation rules and triggers checked")
    involved_planets: List[str] = Field(default_factory=list, description="Planets involved in the formation or affliction")
    signs_and_houses: List[str] = Field(default_factory=list, description="Occupied signs and houses from Lagna or reference")
    degrees: Dict[str, float] = Field(default_factory=dict, description="Exact longitudes and degrees within sign for involved bodies")
    cancellation_conditions_checked: List[str] = Field(default_factory=list, description="Rule-specific cancellation conditions verified")
    cancellation_evidence: List[str] = Field(default_factory=list, description="Active mitigating or neutralizing factors found")
    interpretation: str = Field(..., description="Balanced traditional and psychological interpretation")
    interpretation_ta: str = Field(..., description="Tamil guidance and interpretation")
    rule_set_version: str = Field("1.0.0", description="Dosha rule-set version")
    source_references: str = Field(..., description="Classical textual authorities (BPHS, Phaladeepika, etc.)")
    evaluated_at: Optional[str] = Field(None, description="ISO timestamp of evaluation")
    remedies: List[str] = Field(default_factory=list, description="Remedies from verified repository when applicable")
    missing_prerequisites: Optional[str] = Field(None, description="Missing prerequisite data (e.g. partner chart for synastry doshas)")


class DoshaSummary(BaseModel):
    """Statistical summary across all evaluated dosha rules."""
    total_rules_evaluated: int = Field(..., description="Total number of dosha rules evaluated")
    total_present: int = Field(..., description="Doshas currently active and unmitigated")
    total_mitigated: int = Field(..., description="Doshas formed but neutralized or mitigated by classical cancellations")
    total_absent: int = Field(..., description="Doshas completely absent in the chart")
    total_indeterminate: int = Field(..., description="Rules not evaluated due to missing prerequisites (e.g. partner chart)")


class DoshaEvaluationRequest(HoroscopeRequest):
    """Request model for comprehensive Dosha evaluation."""
    include_2nd_house_in_kuja: bool = Field(
        True,
        description="Include 2nd house in Kuja Dosha evaluation (True=South Indian convention, False=North Indian convention)"
    )
    transit_date: Optional[str] = Field(
        None,
        description="Optional ISO transit date (YYYY-MM-DD) for Sadesati evaluation. Defaults to current date if omitted."
    )
    transit_time: Optional[str] = Field(
        "12:00:00",
        description="Optional transit time (HH:MM:SS) for Sadesati evaluation. Defaults to midday."
    )


class UnifiedDoshaResponse(BaseModel):
    """Unified API response encapsulating all classical Vedic Dosha evaluations."""
    metadata: Optional[CalculationMetadata] = None
    kuja_dosha: KujaDoshaResult
    kaal_sarp_dosha: KaalSarpResult
    sadesati: SadesatiPhaseInfo
    additional_doshas: List[SingleDoshaDetail]
    summary_counts: Dict[str, int] = Field(
        ...,
        description="Summary counters: total_doshas_evaluated, total_active_doshas, total_cancelled_doshas"
    )
    all_doshas: List[DoshaEvaluationItem] = Field(
        default_factory=list,
        description="Complete normalized catalogue of all 30 evaluated Vedic Doshas"
    )
    summary: Optional[DoshaSummary] = Field(
        None,
        description="Normalized statistics breakdown (evaluated, present, mitigated, absent, indeterminate)"
    )
