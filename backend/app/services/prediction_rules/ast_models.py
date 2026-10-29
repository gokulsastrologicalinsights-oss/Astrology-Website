"""Declarative AST Data Models for Astrological Conditions.

Supports recursive boolean trees (AND, OR, NOT) and strictly typed leaf predicates.
Zero eval/exec is used; evaluation is 100% deterministic and safe.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, model_validator


class AstrologySystem(str, Enum):
    VEDIC = "vedic"
    KP = "kp"
    COMBINED = "combined"


class ChartScope(str, Enum):
    D1 = "d1"
    D9 = "d9"
    BOTH = "both"


class SeverityLevel(str, Enum):
    INFO = "info"
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ConditionOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class DignityType(str, Enum):
    EXALTED = "exalted"
    DEBILITATED = "debilitated"
    OWN_SIGN = "own_sign"
    MOOLATRIKONA = "moolatrikona"
    VARGOTTAMA = "vargottama"
    PUSHKARA_NAVAMSA = "pushkara_navamsa"


class BaseCondition(BaseModel):
    """Base model for all condition nodes."""
    condition_type: str = Field(..., description="Unique discriminator for condition node type")


class PlanetSignCondition(BaseCondition):
    condition_type: str = "planet_sign"
    planet: str
    sign: Union[int, str, List[Union[int, str]]]
    chart: ChartScope = ChartScope.D1


class PlanetHouseCondition(BaseCondition):
    condition_type: str = "planet_house"
    planet: str
    house: Union[int, List[int]]
    chart: ChartScope = ChartScope.D1


class PlanetConjunctionCondition(BaseCondition):
    condition_type: str = "planet_conjunction"
    planets: List[str]
    same_sign_only: bool = True
    orb_degrees: Optional[float] = None
    chart: ChartScope = ChartScope.D1


class PlanetAspectCondition(BaseCondition):
    condition_type: str = "planet_aspect"
    aspecting_planet: str
    target_type: str = Field("house", description="'house' or 'planet'")
    target_value: Union[int, str] = Field(..., description="House number (1-12) or planet name")
    aspect_type: str = Field("any", description="'any', '7th', or 'special'")
    chart: ChartScope = ChartScope.D1


class HouseLordPlacementCondition(BaseCondition):
    condition_type: str = "house_lord_placement"
    house: int
    placed_in_house: Optional[Union[int, List[int]]] = None
    placed_in_sign: Optional[Union[int, str, List[Union[int, str]]]] = None
    chart: ChartScope = ChartScope.D1


class HouseOccupancyCondition(BaseCondition):
    condition_type: str = "house_occupancy"
    house: int
    occupied_by: Optional[List[str]] = None
    match_all: bool = False
    is_empty: Optional[bool] = None
    chart: ChartScope = ChartScope.D1


class PlanetNakshatraCondition(BaseCondition):
    condition_type: str = "planet_nakshatra"
    planet: str
    nakshatra: Union[str, int, List[Union[str, int]]]
    pada: Optional[Union[int, List[int]]] = None


class PlanetDignityCondition(BaseCondition):
    condition_type: str = "planet_dignity"
    planet: str
    dignity: DignityType
    chart: ChartScope = ChartScope.D1


class DasaActiveCondition(BaseCondition):
    condition_type: str = "dasa_active"
    level: str = Field("mahadasha", description="'mahadasha', 'bhukti', 'anthara', or 'any'")
    lord: Union[str, List[str]]


class KpSubLordCondition(BaseCondition):
    condition_type: str = "kp_sub_lord"
    cusp: int
    sub_lord: Union[str, List[str]]


class KpSignificatorCondition(BaseCondition):
    condition_type: str = "kp_significator"
    planet: str
    house: int
    levels: Optional[List[str]] = Field(default_factory=lambda: ["A", "B", "C", "D"])


class MutualExchangeCondition(BaseCondition):
    condition_type: str = "mutual_exchange"
    house1: int
    house2: int
    chart: ChartScope = ChartScope.D1


class LagnaSignCondition(BaseCondition):
    condition_type: str = "lagna_sign"
    sign: Union[int, str, List[Union[int, str]]]
    chart: ChartScope = ChartScope.D1


class PlanetaryAvasthaCondition(BaseCondition):
    condition_type: str = "planetary_avastha"
    planet: Optional[str] = "any"
    stage: Optional[str] = None  # "bala", "kumara", "yuva", "vriddha", "mrita"
    min_deg: Optional[float] = None
    max_deg: Optional[float] = None
    loses_aspect_potency: Optional[bool] = False
    chart: ChartScope = ChartScope.D1


class CombustionAspectLossCondition(BaseCondition):
    condition_type: str = "combustion_aspect_loss"
    planet: Optional[str] = "any"
    check_exemptions: Optional[bool] = True
    chart: ChartScope = ChartScope.D1


class GrahaYuddhaCondition(BaseCondition):
    condition_type: str = "graha_yuddha"
    planet: Optional[str] = "any"
    status: Optional[str] = "defeated"  # "defeated", "victor", "any_war"
    max_orb: float = 1.0
    chart: ChartScope = ChartScope.D1


class CompoundCondition(BaseCondition):
    condition_type: str = "compound"
    operator: ConditionOperator
    conditions: List[Dict[str, Any]] = Field(..., description="Child conditions to evaluate under operator")


# ---------------------------------------------------------------------------
# Astrological Rule Definition Model
# ---------------------------------------------------------------------------

class AstrologicalRuleDefinition(BaseModel):
    rule_id: str
    version: int = 1
    name_en: str
    name_ta: str
    category_slug: str
    subcategory: Optional[str] = None
    astrology_system: AstrologySystem = AstrologySystem.VEDIC
    chart_scope: ChartScope = ChartScope.D1
    calculation_mode: str = "thirukanitha"
    condition_tree: Dict[str, Any]
    interpretation_en: str
    interpretation_ta: str
    astrological_principle_en: str
    astrological_principle_ta: str
    evidence_requirements: Optional[List[str]] = Field(default_factory=list)
    source_reference: Optional[str] = None
    limitations_en: Optional[str] = None
    limitations_ta: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.NEUTRAL
    applicable_gender: Optional[str] = Field("both", description="'male', 'female', or 'both'")
    is_enabled: bool = True
    is_draft: bool = False
