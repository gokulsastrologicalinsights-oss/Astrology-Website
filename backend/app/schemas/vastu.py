"""Vastu Data Schemas - Requests, Outputs, Rules, and Persistence Models.

Provides strictly typed, validated models for 8 & 16 Vastu Directions,
Layout Evaluations, Classical Dosha Checks, Astro-Vastu Overlays, and Supabase Persistence.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
import re


# ------------------------------------------------------------------------------
# 1. Direction and Metadata Schemas
# ------------------------------------------------------------------------------

VALID_16_DIRECTIONS = (
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
)

VALID_8_DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")

VALID_PROPERTY_TYPES = ("residential", "commercial", "plot", "industrial")


class DirectionMetadata(BaseModel):
    """Metadata for a single Vastu direction."""
    code: str
    sanskrit_name: str
    english_name: str
    chinese_name: str
    center_degree: float
    start_degree: float
    end_degree: float
    deity: str
    element: str
    planet: str
    traditional_significance: str
    recommended_colors: List[str]
    color_hex: List[str]
    traditional_remedies: List[str]
    suitable_uses: List[str]
    prohibited_uses: List[str]


class PadaDeityMetadata(BaseModel):
    """Metadata for one of the 32 outer padas in the Paramasayika mandala."""
    pada_index: int
    direction_side: str  # North, East, South, West
    sanskrit_name: str
    chinese_name: str
    nature: str  # auspicious, neutral, inauspicious
    governing_direction: str
    traditional_result: str
    start_degree: Optional[float] = None
    end_degree: Optional[float] = None


class VastuDirectionsResponse(BaseModel):
    """Collection of directions and padas."""
    directions_8: List[DirectionMetadata]
    directions_16: List[DirectionMetadata]
    padas_32: List[PadaDeityMetadata]
    engine_version: str


# ------------------------------------------------------------------------------
# 2. Evaluation Request and Input Schemas
# ------------------------------------------------------------------------------

class RoomPlacementsInput(BaseModel):
    """Room and functional zone placements for a property."""
    # Shared / Residential placements
    main_entrance_direction: Optional[str] = None
    main_entrance_pada: Optional[str] = None  # e.g. N4, Soma, Jayanta, etc.
    kitchen_direction: Optional[str] = None
    master_bedroom_direction: Optional[str] = None
    pooja_room_direction: Optional[str] = None
    toilet_directions: Optional[List[str]] = Field(default_factory=list)
    septic_tank_direction: Optional[str] = None
    underground_water_tank_direction: Optional[str] = None
    overhead_water_tank_direction: Optional[str] = None
    living_room_direction: Optional[str] = None
    dining_room_direction: Optional[str] = None
    staircase_direction: Optional[str] = None
    study_room_direction: Optional[str] = None
    brahmasthan_status: Optional[Literal["clear", "partially_obstructed", "heavily_obstructed", "unassessed"]] = "unassessed"
    plot_shape: Optional[Literal["square", "rectangular", "gaumukhi", "shermukhi", "triangular", "irregular", "unassessed"]] = "unassessed"
    slope_direction: Optional[str] = None

    # Commercial-specific placements
    owner_cabin_direction: Optional[str] = None
    accounts_cash_direction: Optional[str] = None
    conference_room_direction: Optional[str] = None
    reception_direction: Optional[str] = None

    # Industrial-specific placements
    heavy_machinery_direction: Optional[str] = None
    raw_material_storage_direction: Optional[str] = None
    finished_goods_direction: Optional[str] = None
    boiler_furnace_direction: Optional[str] = None
    effluent_treatment_direction: Optional[str] = None

    @field_validator("main_entrance_direction", "kitchen_direction", "master_bedroom_direction",
                     "pooja_room_direction", "septic_tank_direction", "underground_water_tank_direction",
                     "overhead_water_tank_direction", "living_room_direction", "dining_room_direction",
                     "staircase_direction", "study_room_direction", "slope_direction",
                     "owner_cabin_direction", "accounts_cash_direction", "conference_room_direction",
                     "reception_direction", "heavy_machinery_direction", "raw_material_storage_direction",
                     "finished_goods_direction", "boiler_furnace_direction", "effluent_treatment_direction")
    @classmethod
    def validate_direction_codes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        norm = v.strip().upper()
        if norm and norm not in VALID_16_DIRECTIONS:
            raise ValueError(f"Invalid direction '{v}'. Must be one of: {', '.join(VALID_16_DIRECTIONS)}")
        return norm

    @field_validator("toilet_directions")
    @classmethod
    def validate_toilet_list(cls, v: Optional[List[str]]) -> List[str]:
        if not v:
            return []
        cleaned = []
        for item in v:
            norm = item.strip().upper()
            if norm not in VALID_16_DIRECTIONS:
                raise ValueError(f"Invalid toilet direction '{item}'. Must be one of: {', '.join(VALID_16_DIRECTIONS)}")
            cleaned.append(norm)
        return cleaned


class VastuEvaluationRequest(BaseModel):
    """Complete input for evaluating a property against Vastu Shastra rules."""
    property_name: str = Field(..., min_length=1, max_length=150, description="Name or label of the property")
    property_type: Literal["residential", "commercial", "plot", "industrial"] = "residential"
    facing_direction: Optional[str] = None
    facing_degrees: Optional[float] = Field(None, ge=0.0, lt=360.0, description="Compass bearing (0-359.99°)")
    placements: RoomPlacementsInput = Field(default_factory=RoomPlacementsInput)

    # Optional Astro-Vastu linkage
    saved_horoscope_id: Optional[str] = None
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    timezone: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

    @field_validator("facing_direction")
    @classmethod
    def validate_facing(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        norm = v.strip().upper()
        if norm and norm not in VALID_16_DIRECTIONS:
            raise ValueError(f"Invalid facing direction '{v}'. Must be one of: {', '.join(VALID_16_DIRECTIONS)}")
        return norm


# ------------------------------------------------------------------------------
# 3. Evaluation Result Models
# ------------------------------------------------------------------------------

class FactorEvaluation(BaseModel):
    """Evaluation result for an individual architectural factor."""
    factor_key: str
    factor_name: str
    assessed: bool
    input_value: Optional[str] = None
    score: Optional[float] = None
    max_weight: float
    severity: Literal["ideal", "acceptable", "moderate_defect", "severe_defect", "unassessed"]
    traditional_rule: str
    rule_source: str
    explanation: str
    remedy: Optional[str] = None


class VastuDosha(BaseModel):
    """Specific Vastu defect identified during assessment."""
    dosha_code: str
    dosha_name: str
    severity: Literal["critical", "major", "moderate", "minor"]
    zone: str
    traditional_impact: str
    traditional_source: str
    remedies: List[str]


class AstroOverlayResult(BaseModel):
    """Personalized Astro-Vastu alignment when birth-chart data is provided."""
    lagna_sign: str
    lagna_ruler: str
    moon_sign: Optional[str] = None
    nakshatra: Optional[str] = None
    favorable_directions: List[str]
    unfavorable_directions: List[str]
    elemental_synergy: str
    planetary_zone_notes: List[str]
    calculation_source: str  # e.g. "XALEN Ephemeris Native Engine"


class VastuEvaluationResponse(BaseModel):
    """Complete evaluated report returned by the calculation engine."""
    property_name: str
    property_type: str
    facing_direction: str
    facing_degrees: Optional[float]
    engine_version: str
    rubric_version: str
    compliance_score: Optional[int] = None
    score_grade: Optional[str] = None
    factors_assessed: int
    factors_total: int
    factor_results: List[FactorEvaluation]
    doshas: List[VastuDosha]
    general_remedies: List[str]
    missing_data_warnings: List[str]
    conflicting_input_warnings: List[str]
    astro_overlay: Optional[AstroOverlayResult] = None
    disclaimer: str


# ------------------------------------------------------------------------------
# 4. Supabase Persistence Models
# ------------------------------------------------------------------------------

class SaveVastuReportRequest(BaseModel):
    """Request payload to persist an evaluation to Supabase."""
    property_name: str = Field(..., min_length=1, max_length=150)
    property_type: Literal["residential", "commercial", "plot", "industrial"] = "residential"
    facing_direction: str
    facing_degrees: Optional[float] = None
    horoscope_id: Optional[str] = None
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    evaluation_data: Dict[str, Any]

    @field_validator("facing_direction")
    @classmethod
    def validate_facing_req(cls, v: str) -> str:
        norm = v.strip().upper()
        if norm not in VALID_16_DIRECTIONS:
            raise ValueError(f"Invalid facing direction '{v}'. Must be one of: {', '.join(VALID_16_DIRECTIONS)}")
        return norm


class SavedVastuReportResponse(BaseModel):
    """Persisted Vastu report schema from Supabase."""
    id: str
    user_id: str
    display_number: int
    property_name: str
    property_type: str
    facing_direction: str
    facing_degrees: Optional[float] = None
    horoscope_id: Optional[str] = None
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    calculation_data: Dict[str, Any]
    dosha_evaluations: List[Dict[str, Any]]
    remedy_recommendations: List[str]
    compliance_score: int
    engine_version: str
    created_at: str
    updated_at: str


class SavedVastuReportsListResponse(BaseModel):
    """Paginated list of saved Vastu reports."""
    reports: List[SavedVastuReportResponse]
    total_count: int
    limit: int
    offset: int
