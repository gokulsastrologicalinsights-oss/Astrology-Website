"""Astrological Rule Evaluator Engine.

Pure deterministic AST evaluation consuming canonical horoscope, D1/D9 varga,
KP, and Dasa structures without recalculating planetary coordinates.
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
import math

from app.schemas.horoscope import HoroscopeResponse, PlanetInfo
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    ChartScope,
    AstrologySystem,
    DignityType,
)

# ---------------------------------------------------------------------------
# Canonical Astronomical & Astrological Reference Constants
# ---------------------------------------------------------------------------

SIGN_NAME_TO_INDEX: Dict[str, int] = {
    "aries": 1, "mesha": 1, "mesham": 1, "மேஷம்": 1,
    "taurus": 2, "vrishabha": 2, "rishabam": 2, "ரிஷபம்": 2,
    "gemini": 3, "mithuna": 3, "mithunam": 3, "மிதுனம்": 3,
    "cancer": 4, "karka": 4, "katakam": 4, "கடகம்": 4,
    "leo": 5, "simha": 5, "simham": 5, "சிம்மம்": 5,
    "virgo": 6, "kanya": 6, "kanni": 6, "கன்னி": 6,
    "libra": 7, "tula": 7, "thulam": 7, "துலாம்": 7,
    "scorpio": 8, "vrishchika": 8, "viruchigam": 8, "விருச்சிகம்": 8,
    "sagittarius": 9, "dhanus": 9, "dhanusu": 9, "தனுசு": 9,
    "capricorn": 10, "makara": 10, "makaram": 10, "மகரம்": 10,
    "aquarius": 11, "kumbha": 11, "kumbam": 11, "கும்பம்": 11,
    "pisces": 12, "meena": 12, "meenam": 12, "மீனம்": 12,
}

INDEX_TO_SIGN_NAME: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

INDEX_TO_SIGN_NAME_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்"
}

SIGN_LORDS: Dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

EXALTATION_SIGNS: Dict[str, int] = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7, "Rahu": 2, "Ketu": 8
}

DEBILITATION_SIGNS: Dict[str, Union[int, Set[int]]] = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
    "Jupiter": 10, "Venus": 6, "Saturn": 1, "Rahu": {8, 9}, "Ketu": {2, 3}
}

OWN_SIGNS: Dict[str, Set[int]] = {
    "Sun": {5},
    "Moon": {4},
    "Mars": {1, 8},
    "Mercury": {3, 6},
    "Jupiter": {9, 12},
    "Venus": {2, 7},
    "Saturn": {10, 11},
    "Rahu": {11},
    "Ketu": {8},
}

# Classical 24 Pushkara Navamsas (Jataka Parijata Ch. 1, Sloka 58)
PUSHKARA_NAVAMSAS: Dict[int, Set[int]] = {
    1: {7, 9}, 5: {7, 9}, 9: {7, 9},
    2: {3, 5}, 6: {3, 5}, 10: {3, 5},
    3: {6, 8}, 7: {6, 8}, 11: {6, 8},
    4: {1, 3}, 8: {1, 3}, 12: {1, 3},
}


def normalize_sign_index(val: Union[int, str]) -> int:
    """Safely convert sign number or sign name string to 1-12 integer index."""
    if isinstance(val, int):
        return ((val - 1) % 12) + 1
    s = str(val).strip().lower()
    if s.isdigit():
        return ((int(s) - 1) % 12) + 1
    return SIGN_NAME_TO_INDEX.get(s, 1)


def circular_distance_deg(deg1: float, deg2: float) -> float:
    """Compute the shortest angular distance between two longitudes on 360 circle."""
    diff = abs(deg1 - deg2) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


# ---------------------------------------------------------------------------
# Chart Context Builder
# ---------------------------------------------------------------------------

class ChartContext:
    """Precomputed lookup context for D1, D9, KP, and Dasa chart features."""

    def __init__(
        self,
        horoscope: HoroscopeResponse,
        dasa_data: Optional[Dict[str, Any]] = None,
        kp_data: Optional[Dict[str, Any]] = None,
    ):
        self.horoscope = horoscope
        self.dasa_data = dasa_data
        self.kp_data = kp_data or {}
        if isinstance(self.kp_data, dict):
            if "cuspal_analysis" in self.kp_data and "cusp_details" not in self.kp_data:
                self.kp_data["cusp_details"] = self.kp_data["cuspal_analysis"]
            if "significators" in self.kp_data and "planet_significators" not in self.kp_data:
                self.kp_data["planet_significators"] = self.kp_data["significators"]
        self.metadata = horoscope.metadata

        # D1 Ascendant
        self.d1_lagna_sign = horoscope.ascendant.sign_index
        self.d1_lagna_deg = horoscope.ascendant.degree_in_sign
        self.d1_lagna_long = horoscope.ascendant.degree
        self.d1_lagna_nakshatra = getattr(horoscope.ascendant, "nakshatra", None)

        # D1 Planets lookup
        self.d1_planets: Dict[str, Dict[str, Any]] = {}
        for p in horoscope.planets:
            p_house = ((p.sign_index - self.d1_lagna_sign) % 12) + 1
            self.d1_planets[p.name] = {
                "name": p.name,
                "sign_index": p.sign_index,
                "sign_name": p.sign_name,
                "sign_name_tamil": p.sign_name_tamil,
                "degree_in_sign": p.degree_in_sign,
                "longitude": p.longitude,
                "house": p_house,
                "is_retrograde": p.is_retrograde,
                "nakshatra_name": p.nakshatra.name if p.nakshatra else "Unknown",
                "nakshatra_pada": p.nakshatra.pada if p.nakshatra else 1,
                "star_lord": getattr(p.nakshatra, "lord", ""),
            }

        # Include Ascendant / Lagna into D1 lookups for Nakshatra evaluation
        if hasattr(horoscope, "ascendant") and horoscope.ascendant:
            asc = horoscope.ascendant
            asc_nak_name = getattr(asc.nakshatra, "name", "Unknown") if getattr(asc, "nakshatra", None) else "Unknown"
            asc_pada = getattr(asc.nakshatra, "pada", 1) if getattr(asc, "nakshatra", None) else 1
            asc_star_lord = getattr(asc.nakshatra, "lord", "") if getattr(asc, "nakshatra", None) else ""
            asc_entry = {
                "name": "Ascendant",
                "sign_index": asc.sign_index,
                "sign_name": asc.sign_name,
                "sign_name_tamil": getattr(asc, "sign_name_tamil", ""),
                "degree_in_sign": asc.degree_in_sign,
                "longitude": asc.degree,
                "house": 1,
                "is_retrograde": False,
                "nakshatra_name": asc_nak_name,
                "nakshatra_pada": asc_pada,
                "star_lord": asc_star_lord,
            }
            self.d1_planets["Ascendant"] = asc_entry
            self.d1_planets["Lagna"] = asc_entry

        # D1 House Occupants & Lords
        self.d1_house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for p_name, p_info in self.d1_planets.items():
            self.d1_house_occupants[p_info["house"]].append(p_name)

        self.d1_house_lords: Dict[int, str] = {}
        self.d1_house_signs: Dict[int, int] = {}
        for h in range(1, 13):
            sign_idx = ((self.d1_lagna_sign - 1 + h - 1) % 12) + 1
            self.d1_house_signs[h] = sign_idx
            self.d1_house_lords[h] = SIGN_LORDS[sign_idx]

        # D9 Navamsa context
        self._init_d9_context()

    def _init_d9_context(self):
        """Extract or compute D9 Navamsa positions."""
        varga = getattr(self.horoscope, "varga_d1_d9", None)
        if varga and hasattr(varga, "ascendant") and hasattr(varga, "planets"):
            self.d9_lagna_sign = varga.ascendant.d9_sign_index
            self.d9_lagna_deg = varga.ascendant.d9_degree_in_sign
            self.d9_planets = {}
            for vp in varga.planets:
                self.d9_planets[vp.name] = {
                    "name": vp.name,
                    "sign_index": vp.d9_sign_index,
                    "sign_name": vp.d9_sign_name,
                    "sign_name_tamil": vp.d9_sign_name_tamil,
                    "degree_in_sign": vp.d9_degree_in_sign,
                    "house": vp.d9_house,
                    "is_vargottama": vp.is_vargottama,
                    "is_pushkara_navamsa": vp.is_pushkara_navamsa,
                    "is_retrograde": vp.is_retrograde,
                    "nakshatra_name": vp.nakshatra_name,
                    "nakshatra_pada": vp.pada,
                }
        else:
            # Fallback deterministic classical Navamsa calculation (BPHS Ch. 6)
            def compute_d9(sign_idx: int, deg_in_sign: float) -> Tuple[int, float, int]:
                elem = sign_idx % 4
                if elem == 1:
                    start_sign = 1  # Fire -> Aries
                elif elem == 2:
                    start_sign = 10 # Earth -> Capricorn
                elif elem == 3:
                    start_sign = 7  # Air -> Libra
                else:
                    start_sign = 4  # Water -> Cancer
                pada_idx = min(8, max(0, int(deg_in_sign / (30.0 / 9.0))))
                d9_sign = ((start_sign - 1 + pada_idx) % 12) + 1
                d9_deg = (deg_in_sign % (30.0 / 9.0)) * 9.0
                return d9_sign, d9_deg, pada_idx + 1

            d9_l_sign, d9_l_deg, _ = compute_d9(self.d1_lagna_sign, self.d1_lagna_deg)
            self.d9_lagna_sign = d9_l_sign
            self.d9_lagna_deg = d9_l_deg
            self.d9_planets = {}

            for p_name, p_info in self.d1_planets.items():
                p_d9_sign, p_d9_deg, navamsa_pada = compute_d9(p_info["sign_index"], p_info["degree_in_sign"])
                p_d9_house = ((p_d9_sign - self.d9_lagna_sign) % 12) + 1
                is_varg = (p_info["sign_index"] == p_d9_sign)
                pushkaras = PUSHKARA_NAVAMSAS.get(p_info["sign_index"], set())
                is_pushk = (navamsa_pada in pushkaras)

                self.d9_planets[p_name] = {
                    "name": p_name,
                    "sign_index": p_d9_sign,
                    "sign_name": INDEX_TO_SIGN_NAME[p_d9_sign],
                    "sign_name_tamil": INDEX_TO_SIGN_NAME_TA[p_d9_sign],
                    "degree_in_sign": p_d9_deg,
                    "house": p_d9_house,
                    "is_vargottama": is_varg,
                    "is_pushkara_navamsa": is_pushk,
                    "is_retrograde": p_info["is_retrograde"],
                    "nakshatra_name": p_info["nakshatra_name"],
                    "nakshatra_pada": p_info["nakshatra_pada"],
                }

        self.d9_house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for p_name, p_info in self.d9_planets.items():
            self.d9_house_occupants[p_info["house"]].append(p_name)

        self.d9_house_lords: Dict[int, str] = {}
        for h in range(1, 13):
            sign_idx = ((self.d9_lagna_sign - 1 + h - 1) % 12) + 1
            self.d9_house_lords[h] = SIGN_LORDS[sign_idx]

    def get_planet(self, planet_name: str, scope: str = "d1") -> Optional[Dict[str, Any]]:
        if scope.lower() == "d9":
            return self.d9_planets.get(planet_name)
        return self.d1_planets.get(planet_name)


# ---------------------------------------------------------------------------
# Evaluator Class
# ---------------------------------------------------------------------------

class RuleEvaluationResult:
    def __init__(
        self,
        rule: AstrologicalRuleDefinition,
        matched: bool,
        evidence: List[str],
        reasons: List[str],
        unevaluable: bool = False,
        unevaluable_reason: Optional[str] = None,
    ):
        self.rule = rule
        self.matched = matched
        self.evidence = evidence
        self.reasons = reasons
        self.unevaluable = unevaluable
        self.unevaluable_reason = unevaluable_reason

    def to_dict(self, language: str = "en") -> Dict[str, Any]:
        use_ta = (language == "ta")
        status = "unevaluable" if self.unevaluable else ("matched" if self.matched else "not_matched")

        return {
            "rule_id": self.rule.rule_id,
            "version": self.rule.version,
            "name": self.rule.name_ta if use_ta and self.rule.name_ta else self.rule.name_en,
            "name_en": self.rule.name_en,
            "name_ta": self.rule.name_ta,
            "category_slug": self.rule.category_slug,
            "subcategory": self.rule.subcategory,
            "astrology_system": self.rule.astrology_system.value,
            "chart_scope": self.rule.chart_scope.value,
            "calculation_mode": self.rule.calculation_mode,
            "severity": self.rule.severity.value,
            "status": status,
            "matched": self.matched,
            "unevaluable": self.unevaluable,
            "unevaluable_reason": self.unevaluable_reason,
            "interpretation": self.rule.interpretation_ta if use_ta and self.rule.interpretation_ta else self.rule.interpretation_en,
            "interpretation_en": self.rule.interpretation_en,
            "interpretation_ta": self.rule.interpretation_ta,
            "astrological_principle": self.rule.astrological_principle_ta if use_ta and self.rule.astrological_principle_ta else self.rule.astrological_principle_en,
            "astrological_principle_en": self.rule.astrological_principle_en,
            "astrological_principle_ta": self.rule.astrological_principle_ta,
            "chart_evidence": self.evidence,
            "match_reasons": self.reasons,
            "source_reference": self.rule.source_reference,
            "applicable_gender": getattr(self.rule, "applicable_gender", "both"),
            "limitations": self.rule.limitations_ta if use_ta and self.rule.limitations_ta else self.rule.limitations_en,
            "limitations_en": self.rule.limitations_en,
            "limitations_ta": self.rule.limitations_ta,
        }


class AstrologicalRuleEvaluator:
    """Evaluates rules against a ChartContext."""

    @classmethod
    def evaluate_rule(cls, rule: AstrologicalRuleDefinition, ctx: ChartContext) -> RuleEvaluationResult:
        """Evaluate a single rule against chart context."""
        # Check system applicability
        if rule.astrology_system == AstrologySystem.KP and not ctx.kp_data:
            return RuleEvaluationResult(
                rule=rule,
                matched=False,
                evidence=[],
                reasons=[],
                unevaluable=True,
                unevaluable_reason="Rule requires KP chart cusps/sub-lords, which are absent in this chart view."
            )

        evidence: List[str] = []
        reasons: List[str] = []

        try:
            matched, cond_evidence, cond_reasons = cls._evaluate_condition_node(
                rule.condition_tree, ctx, rule.chart_scope.value
            )
            evidence.extend(cond_evidence)
            reasons.extend(cond_reasons)
            return RuleEvaluationResult(
                rule=rule,
                matched=matched,
                evidence=evidence,
                reasons=reasons,
                unevaluable=False
            )
        except Exception as exc:
            return RuleEvaluationResult(
                rule=rule,
                matched=False,
                evidence=[],
                reasons=[f"Evaluation exception: {str(exc)}"],
                unevaluable=True,
                unevaluable_reason=str(exc)
            )

    @classmethod
    def _evaluate_condition_node(
        cls,
        node: Dict[str, Any],
        ctx: ChartContext,
        default_scope: str = "d1"
    ) -> Tuple[bool, List[str], List[str]]:
        """Recursively evaluate declarative condition node."""
        cond_type = (node.get("condition_type") or node.get("type") or "").lower()
        if cond_type == "planet_house_placement":
            cond_type = "planet_house"
        elif cond_type == "planet_sign_placement":
            cond_type = "planet_sign"

        # 1. Compound Operator Node (AND, OR, NOT)
        if cond_type == "compound":
            op = node.get("operator", "AND").upper()
            sub_nodes = node.get("conditions", [])
            if not sub_nodes:
                return True, [], []

            if op == "AND":
                all_matched = True
                ev_accum: List[str] = []
                reas_accum: List[str] = []
                for sub in sub_nodes:
                    m, ev, reas = cls._evaluate_condition_node(sub, ctx, default_scope)
                    ev_accum.extend(ev)
                    reas_accum.extend(reas)
                    if not m:
                        all_matched = False
                return all_matched, ev_accum, reas_accum

            elif op == "OR":
                ev_accum: List[str] = []
                reas_accum: List[str] = []
                any_matched = False
                for sub in sub_nodes:
                    m, ev, reas = cls._evaluate_condition_node(sub, ctx, default_scope)
                    if m:
                        any_matched = True
                        ev_accum.extend(ev)
                        reas_accum.extend(reas)
                return any_matched, ev_accum, reas_accum

            elif op == "NOT":
                if not sub_nodes:
                    return False, [], ["Empty NOT condition"]
                m, ev, reas = cls._evaluate_condition_node(sub_nodes[0], ctx, default_scope)
                not_matched = not m
                not_reas = [f"Negative condition satisfied: Inner condition was NOT met ({'; '.join(reas) if reas else 'unmatched'})"]
                return not_matched, ev, not_reas

        # 2. Planet Sign Condition
        elif cond_type == "planet_sign":
            planet = node.get("planet")
            target_sign = node.get("sign")
            chart = node.get("chart", default_scope).lower()

            scopes_to_check = ["d1", "d9"] if chart == "both" else [chart]
            all_satisfied = True
            ev: List[str] = []
            reas: List[str] = []

            for sc in scopes_to_check:
                p_info = ctx.get_planet(planet, sc)
                if not p_info:
                    return False, [], [f"Planet {planet} not present in {sc.upper()} chart"]

                actual_sign_idx = p_info["sign_index"]
                target_indices = (
                    [normalize_sign_index(s) for s in target_sign]
                    if isinstance(target_sign, list)
                    else [normalize_sign_index(target_sign)]
                )

                if actual_sign_idx in target_indices:
                    ev.append(f"{planet} is in {p_info['sign_name']} ({actual_sign_idx}) in {sc.upper()}")
                    reas.append(f"{planet} occupies required sign {p_info['sign_name']} in {sc.upper()}")
                else:
                    all_satisfied = False

            return all_satisfied, ev, reas

        # 3. Planet House Condition
        elif cond_type == "planet_house":
            planet = node.get("planet")
            target_house = node.get("house")
            chart = node.get("chart", default_scope).lower()

            scopes_to_check = ["d1", "d9"] if chart == "both" else [chart]
            all_satisfied = True
            ev: List[str] = []
            reas: List[str] = []

            target_houses = target_house if isinstance(target_house, list) else [target_house]

            for sc in scopes_to_check:
                p_info = ctx.get_planet(planet, sc)
                if not p_info:
                    return False, [], [f"Planet {planet} not found in {sc.upper()}"]

                actual_house = p_info["house"]
                if actual_house in target_houses:
                    ev.append(f"{planet} is in House {actual_house} ({p_info['sign_name']}) in {sc.upper()}")
                    reas.append(f"{planet} placed in target house {actual_house} in {sc.upper()}")
                else:
                    all_satisfied = False

            return all_satisfied, ev, reas

        # 4. Planet Conjunction Condition (distinguishes same sign vs angular orb)
        elif cond_type == "planet_conjunction":
            planets = node.get("planets", [])
            same_sign_only = node.get("same_sign_only", True)
            orb = node.get("orb_degrees")
            chart = node.get("chart", default_scope).lower()

            if len(planets) < 2:
                return False, [], ["Conjunction requires at least 2 planets"]

            scopes_to_check = ["d1", "d9"] if chart == "both" else [chart]
            all_satisfied = True
            ev: List[str] = []
            reas: List[str] = []

            for sc in scopes_to_check:
                p_infos = [ctx.get_planet(p, sc) for p in planets]
                if any(p is None for p in p_infos):
                    return False, [], [f"One or more planets {planets} missing in {sc.upper()}"]

                signs = {p["sign_index"] for p in p_infos}
                if same_sign_only and len(signs) > 1:
                    all_satisfied = False
                    continue

                if orb is not None:
                    # Check maximum pairwise angular distance
                    max_dist = 0.0
                    for i in range(len(p_infos)):
                        for j in range(i + 1, len(p_infos)):
                            d = circular_distance_deg(p_infos[i]["longitude"], p_infos[j]["longitude"])
                            if d > max_dist:
                                max_dist = d
                    if max_dist > orb:
                        all_satisfied = False
                        continue
                    ev.append(
                        f"{' + '.join(planets)} in true conjunction (max orb {max_dist:.2f}° <= {orb}°) in {p_infos[0]['sign_name']} ({sc.upper()})"
                    )
                    reas.append(f"Planets {', '.join(planets)} conjunct within {orb}° orb in {sc.upper()}")
                else:
                    ev.append(f"{' + '.join(planets)} co-occupy {p_infos[0]['sign_name']} (Sign {p_infos[0]['sign_index']}) in {sc.upper()}")
                    reas.append(f"Planets {', '.join(planets)} share sign {p_infos[0]['sign_name']} in {sc.upper()}")

            return all_satisfied, ev, reas

        # 5. Planet Aspect Condition (Parashari special & 7th aspects)
        elif cond_type == "planet_aspect":
            asp_planet = node.get("aspecting_planet")
            target_type = node.get("target_type", "house")
            target_val = node.get("target_value")
            chart = node.get("chart", default_scope).lower()

            p_info = ctx.get_planet(asp_planet, chart)
            if not p_info:
                return False, [], [f"Aspecting planet {asp_planet} not found in {chart.upper()}"]

            p_sign = p_info["sign_index"]

            # Determine target sign
            if target_type == "house":
                target_house = int(target_val)
                target_sign = ((ctx.d1_lagna_sign - 1 + target_house - 1) % 12) + 1 if chart == "d1" else ((ctx.d9_lagna_sign - 1 + target_house - 1) % 12) + 1
                target_desc = f"House {target_house} ({INDEX_TO_SIGN_NAME[target_sign]})"
            else:
                tgt_planet_info = ctx.get_planet(str(target_val), chart)
                if not tgt_planet_info:
                    return False, [], [f"Target planet {target_val} not found in {chart.upper()}"]
                target_sign = tgt_planet_info["sign_index"]
                target_desc = f"{target_val} in {tgt_planet_info['sign_name']}"

            # Calculate sign distance (1 to 12) from aspecting planet
            sign_dist = ((target_sign - p_sign) % 12) + 1

            has_aspect = False
            aspect_name = ""

            if sign_dist == 7:
                has_aspect = True
                aspect_name = "7th full aspect"
            elif asp_planet == "Mars" and sign_dist in (4, 8):
                has_aspect = True
                aspect_name = f"Mars {sign_dist}th special aspect"
            elif asp_planet == "Jupiter" and sign_dist in (5, 9):
                has_aspect = True
                aspect_name = f"Jupiter {sign_dist}th special trinal aspect"
            elif asp_planet == "Saturn" and sign_dist in (3, 10):
                has_aspect = True
                aspect_name = f"Saturn {sign_dist}th special aspect"

            if has_aspect:
                ev = [f"{asp_planet} in {p_info['sign_name']} casts {aspect_name} on {target_desc} in {chart.upper()}"]
                reas = [f"Valid Parashari aspect ({aspect_name}) detected from {asp_planet}"]
                return True, ev, reas
            return False, [], []

        # 6. House Lord Placement Condition
        elif cond_type == "house_lord_placement":
            h = int(node.get("house"))
            chart = node.get("chart", default_scope).lower()
            placed_h = node.get("placed_in_house")
            placed_s = node.get("placed_in_sign")

            lord = ctx.d1_house_lords.get(h) if chart == "d1" else ctx.d9_house_lords.get(h)
            if not lord:
                return False, [], [f"Lord for house {h} not identified"]

            lord_info = ctx.get_planet(lord, chart)
            if not lord_info:
                return False, [], [f"Lord {lord} not found in {chart.upper()}"]

            ev: List[str] = []
            reas: List[str] = []

            # Check house placement
            if placed_h is not None:
                target_houses = placed_h if isinstance(placed_h, list) else [placed_h]
                if lord_info["house"] not in target_houses:
                    return False, [], []
                ev.append(f"{chart.upper()} {h}th Lord ({lord}) is placed in House {lord_info['house']} ({lord_info['sign_name']})")
                reas.append(f"{h}th Lord {lord} occupies required house {lord_info['house']}")

            # Check sign placement
            if placed_s is not None:
                target_signs = (
                    [normalize_sign_index(s) for s in placed_s]
                    if isinstance(placed_s, list)
                    else [normalize_sign_index(placed_s)]
                )
                if lord_info["sign_index"] not in target_signs:
                    return False, [], []
                ev.append(f"{chart.upper()} {h}th Lord ({lord}) placed in {lord_info['sign_name']}")
                reas.append(f"{h}th Lord {lord} occupies required sign {lord_info['sign_name']}")

            return True, ev, reas

        # 7. House Occupancy Condition
        elif cond_type == "house_occupancy":
            h = int(node.get("house"))
            chart = node.get("chart", default_scope).lower()
            occupied_by = node.get("occupied_by", [])
            match_all = node.get("match_all", False)
            is_empty = node.get("is_empty")

            occupants = ctx.d1_house_occupants.get(h, []) if chart == "d1" else ctx.d9_house_occupants.get(h, [])

            if is_empty is True:
                if len(occupants) == 0:
                    return True, [f"House {h} is empty (no planetary occupants) in {chart.upper()}"], [f"House {h} is unoccupied"]
                return False, [], []

            if is_empty is False:
                if len(occupants) > 0:
                    return True, [f"House {h} is occupied by {', '.join(occupants)} in {chart.upper()}"], [f"House {h} has occupants"]
                return False, [], []

            if occupied_by:
                if match_all:
                    if all(p in occupants for p in occupied_by):
                        return True, [f"House {h} occupied by all required planets: {', '.join(occupied_by)} in {chart.upper()}"], [f"All required occupants present in House {h}"]
                    return False, [], []
                else:
                    present = [p for p in occupied_by if p in occupants]
                    if present:
                        return True, [f"House {h} occupied by {', '.join(present)} in {chart.upper()}"], [f"Occupant {', '.join(present)} matches requirement for House {h}"]
                    return False, [], []

            return False, [], ["Incomplete house_occupancy specification"]

        # 8. Planet / Lagna Nakshatra Condition
        elif cond_type in ("planet_nakshatra", "lagna_nakshatra", "ascendant_nakshatra"):
            planet = node.get("planet") or ("Ascendant" if "lagna" in cond_type or "ascendant" in cond_type else "Moon")
            target_nak = node.get("nakshatra")
            target_pada = node.get("pada")

            p_info = ctx.get_planet(planet, "d1")
            if not p_info:
                return False, [], [f"Planet {planet} not found"]

            nak_name = p_info["nakshatra_name"].lower()
            target_naks = (
                [str(n).lower() for n in target_nak]
                if isinstance(target_nak, list)
                else [str(target_nak).lower()]
            )

            # Match nakshatra name substring or exact
            matched_nak = any(tn in nak_name for tn in target_naks)
            if not matched_nak:
                return False, [], []

            if target_pada is not None:
                target_padas = target_pada if isinstance(target_pada, list) else [target_pada]
                if p_info["nakshatra_pada"] not in target_padas:
                    return False, [], []

            ev = [f"{planet} is in Nakshatra {p_info['nakshatra_name']}, Pada {p_info['nakshatra_pada']}"]
            reas = [f"{planet} matches required star {p_info['nakshatra_name']} (Pada {p_info['nakshatra_pada']})"]
            return True, ev, reas

        # 9. Planet Dignity Condition
        elif cond_type == "planet_dignity":
            planet = node.get("planet")
            dignity = str(node.get("dignity", "")).lower()
            chart = node.get("chart", default_scope).lower()

            p_info = ctx.get_planet(planet, chart)
            if not p_info:
                return False, [], [f"Planet {planet} not found in {chart.upper()}"]

            sign_idx = p_info["sign_index"]
            matched = False
            evidence_str = ""

            if dignity == "exalted":
                ex_sign = EXALTATION_SIGNS.get(planet)
                if ex_sign and sign_idx == ex_sign:
                    matched = True
                    evidence_str = f"{planet} is exalted (Uchcha) in {p_info['sign_name']} in {chart.upper()}"
            elif dignity == "debilitated":
                deb_sign = DEBILITATION_SIGNS.get(planet)
                if deb_sign is not None:
                    if isinstance(deb_sign, (set, list, tuple)):
                        if sign_idx in deb_sign:
                            matched = True
                    elif sign_idx == deb_sign:
                        matched = True
                if matched:
                    evidence_str = f"{planet} is debilitated (Neecha) in {p_info['sign_name']} in {chart.upper()}"
            elif dignity == "own_sign":
                own_set = OWN_SIGNS.get(planet, set())
                if sign_idx in own_set:
                    matched = True
                    evidence_str = f"{planet} is in own sign (Swakshetra) {p_info['sign_name']} in {chart.upper()}"
            elif dignity == "vargottama":
                # Check Vargottama across D1 and D9
                p_d1 = ctx.get_planet(planet, "d1")
                p_d9 = ctx.get_planet(planet, "d9")
                if p_d1 and p_d9 and (p_d1["sign_index"] == p_d9["sign_index"]):
                    matched = True
                    evidence_str = f"{planet} is Vargottama (occupies {p_d1['sign_name']} in both D1 and D9)"
            elif dignity == "pushkara_navamsa":
                p_d9 = ctx.get_planet(planet, "d9")
                if p_d9 and p_d9.get("is_pushkara_navamsa"):
                    matched = True
                    evidence_str = f"{planet} is in Pushkara Navamsa ({p_d9['sign_name']} Pada {p_d9.get('nakshatra_pada')})"

            if matched:
                return True, [evidence_str], [f"{planet} satisfies dignity '{dignity}'"]
            return False, [], []

        # 10. Lagna Sign Condition
        elif cond_type == "lagna_sign":
            target_sign = node.get("sign")
            chart = node.get("chart", default_scope).lower()
            lagna_sign = ctx.d1_lagna_sign if chart == "d1" else ctx.d9_lagna_sign

            target_indices = (
                [normalize_sign_index(s) for s in target_sign]
                if isinstance(target_sign, list)
                else [normalize_sign_index(target_sign)]
            )

            if lagna_sign in target_indices:
                sign_name = INDEX_TO_SIGN_NAME[lagna_sign]
                ev = [f"{chart.upper()} Ascendant (Lagna) is in {sign_name} (Sign {lagna_sign})"]
                reas = [f"Ascendant matches required sign {sign_name} in {chart.upper()}"]
                return True, ev, reas
            return False, [], []

        # 11. Dasa Active Condition
        elif cond_type == "dasa_active":
            target_level = node.get("level", "mahadasha").lower()
            target_lord = node.get("lord")
            target_lords = (
                [l.lower() for l in target_lord]
                if isinstance(target_lord, list)
                else [str(target_lord).lower()]
            )

            if not ctx.dasa_data:
                return False, [], ["Dasa balance information not available"]

            active_path = ctx.dasa_data.get("current_period_path") or {}
            # Check mahadasha or bhukti
            actual_maha = (active_path.get("mahadasha") or "").lower()
            actual_bhukti = (active_path.get("antardasha") or active_path.get("bhukti") or "").lower()

            matched = False
            active_info = ""

            if target_level in ("mahadasha", "maha") and actual_maha in target_lords:
                matched = True
                active_info = f"Current active Mahadasha lord is {actual_maha.capitalize()}"
            elif target_level in ("bhukti", "antar", "antardasha") and actual_bhukti in target_lords:
                matched = True
                active_info = f"Current active Bhukti lord is {actual_bhukti.capitalize()}"
            elif target_level == "any" and (actual_maha in target_lords or actual_bhukti in target_lords):
                matched = True
                active_info = f"Active period lord is {actual_maha.capitalize()} (MD) / {actual_bhukti.capitalize()} (AD)"

            if matched:
                return True, [active_info], [f"Vimshottari Dasa matches required lord {', '.join(target_lords)}"]
            return False, [], []

        # 12. KP Sub Lord Condition
        elif cond_type == "kp_sub_lord":
            cusp = int(node.get("cusp", 1))
            target_sl = node.get("sub_lord")
            target_sls = (
                [s.lower() for s in target_sl]
                if isinstance(target_sl, list)
                else [str(target_sl).lower()]
            )

            if not ctx.kp_data or "cusp_details" not in ctx.kp_data:
                return False, [], ["KP cusp details not available"]

            cusps = ctx.kp_data.get("cusp_details", [])
            target_detail = next((c for c in cusps if c.get("house") == cusp), None)
            if not target_detail:
                return False, [], [f"KP Cusp {cusp} not found"]

            actual_sl = (target_detail.get("sub_lord") or "").lower()
            if actual_sl in target_sls:
                ev = [f"KP Cusp {cusp} Sub-Lord is {actual_sl.capitalize()} ({target_detail.get('sign_name')} {target_detail.get('cusp_degree', 0):.2f}°)"]
                reas = [f"KP Cusp {cusp} sub-lord matches {actual_sl.capitalize()}"]
                return True, ev, reas
            return False, [], []

        # 13. Parivartana / Mutual Exchange Condition
        elif cond_type == "mutual_exchange":
            h1 = int(node.get("house1"))
            h2 = int(node.get("house2"))
            chart = node.get("chart", default_scope).lower()

            lord1 = ctx.d1_house_lords.get(h1) if chart == "d1" else ctx.d9_house_lords.get(h1)
            lord2 = ctx.d1_house_lords.get(h2) if chart == "d1" else ctx.d9_house_lords.get(h2)

            if not lord1 or not lord2 or lord1 == lord2:
                return False, [], []

            p1_info = ctx.get_planet(lord1, chart)
            p2_info = ctx.get_planet(lord2, chart)

            if p1_info and p2_info and (p1_info["house"] == h2) and (p2_info["house"] == h1):
                ev = [
                    f"Parivartana Yoga (Mutual Exchange): {lord1} (Lord of {h1}) is in House {h2}, and {lord2} (Lord of {h2}) is in House {h1} in {chart.upper()}"
                ]
                reas = [f"House {h1} and House {h2} lords have exchanged signs"]
                return True, ev, reas
            return False, [], []

        # 14. Barren / Fruitful Sign Condition
        elif cond_type == "barren_fruitful_sign":
            target_type = node.get("target_type", "cusp")
            target_val = node.get("target_value")
            nature = node.get("sign_nature", "fruitful").lower()
            chart = node.get("chart", default_scope).lower()

            FRUITFUL = {4, 8, 12}
            BARREN = {1, 3, 5, 6, 10}
            SEMI_FRUITFUL = {2, 7, 9, 10}

            if target_type == "cusp":
                h = int(target_val)
                sign_idx = ctx.d1_house_signs.get(h) if chart == "d1" else None
                desc = f"House {h} cusp"
            else:
                p_info = ctx.get_planet(str(target_val), chart)
                sign_idx = p_info["sign_index"] if p_info else None
                desc = f"Planet {target_val}"

            if not sign_idx:
                return False, [], [f"{desc} sign position not found"]

            sign_name = INDEX_TO_SIGN_NAME.get(sign_idx, f"Sign {sign_idx}")
            matched = False
            if nature == "fruitful" and sign_idx in FRUITFUL:
                matched = True
            elif nature == "barren" and sign_idx in BARREN:
                matched = True
            elif nature == "semi_fruitful" and sign_idx in SEMI_FRUITFUL:
                matched = True

            if matched:
                ev = [f"{desc} is in {sign_name} which is classically classified as a {nature} sign"]
                reas = [f"{desc} meets {nature} sign requirement in {chart.upper()}"]
                return True, ev, reas
            return False, [], []

        # 15. Badhaka & Maraka Condition
        elif cond_type == "badhaka_maraka":
            check = (node.get("check") or node.get("check_role") or "badhaka").lower()
            target_house = node.get("house")
            planet = node.get("planet")
            cusp = node.get("cusp")

            if ctx.d1_lagna_sign in (1, 4, 7, 10):
                badhaka_house = 11
                lagna_type = "Moveable (Cardinal)"
            elif ctx.d1_lagna_sign in (2, 5, 8, 11):
                badhaka_house = 9
                lagna_type = "Fixed"
            else:
                badhaka_house = 7
                lagna_type = "Common (Mutable)"

            if check == "badhaka":
                if target_house is not None:
                    if int(target_house) == badhaka_house:
                        return True, [f"House {target_house} is the Badhaka Sthana for {lagna_type} Lagna ({INDEX_TO_SIGN_NAME.get(ctx.d1_lagna_sign)})"], [f"Badhaka house {badhaka_house} active"]
                if planet:
                    p_info = ctx.get_planet(planet, "d1")
                    if p_info and p_info["house"] == badhaka_house:
                        return True, [f"{planet} occupies Badhaka House {badhaka_house} for {lagna_type} Lagna"], [f"{planet} is in Badhaka Sthana"]
                # If neither planet nor target_house is explicitly specified, evaluate cuspal / KP significator link (e.g. 8th cusp CSL connection)
                check_cusp = int(cusp if cusp is not None else 8)
                if ctx.kp_data and "cusp_details" in ctx.kp_data:
                    cusps = ctx.kp_data.get("cusp_details", [])
                    cd = next((c for c in cusps if c.get("house") == check_cusp), None)
                    if cd:
                        sl = cd.get("sub_lord", "")
                        planet_sigs = ctx.kp_data.get("planet_significators", [])
                        p_entry = next((ps for ps in planet_sigs if ps.get("planet", "").lower() == sl.lower()), None)
                        signified = p_entry.get("signified_houses", []) if p_entry else []
                        if badhaka_house in signified or 2 in signified or 7 in signified:
                            ev = [f"Cusp {check_cusp} Sub-Lord ({sl}) signifies Badhaka/Maraka house ({[h for h in (badhaka_house, 2, 7) if h in signified]}) for {lagna_type} Lagna"]
                            reas = [f"Cusp {check_cusp} Sub-Lord connects to Badhaka/Maraka house"]
                            return True, ev, reas
                return False, [], []

            elif check in ("maraka", "both", "badhaka_maraka"):
                if target_house is not None:
                    if int(target_house) in (2, 7):
                        return True, [f"House {target_house} is a Maraka Sthana (Death-inflicting house)"], [f"Maraka house {target_house} active"]
                if planet:
                    p_info = ctx.get_planet(planet, "d1")
                    if p_info and p_info["house"] in (2, 7):
                        return True, [f"{planet} occupies Maraka House {p_info['house']} ({p_info['sign_name']})"], [f"{planet} is placed in Maraka house"]
                check_cusp = int(cusp if cusp is not None else 8)
                if ctx.kp_data and "cusp_details" in ctx.kp_data:
                    cusps = ctx.kp_data.get("cusp_details", [])
                    cd = next((c for c in cusps if c.get("house") == check_cusp), None)
                    if cd:
                        sl = cd.get("sub_lord", "")
                        planet_sigs = ctx.kp_data.get("planet_significators", [])
                        p_entry = next((ps for ps in planet_sigs if ps.get("planet", "").lower() == sl.lower()), None)
                        signified = p_entry.get("signified_houses", []) if p_entry else []
                        matches = [h for h in (2, 7, badhaka_house) if h in signified]
                        if matches:
                            ev = [f"Cusp {check_cusp} Sub-Lord ({sl}) signifies Maraka/Badhaka houses {matches}"]
                            reas = [f"Cusp {check_cusp} Sub-Lord links to {matches}"]
                            return True, ev, reas
                return False, [], []

        # 16. Mute & Voice Signs Condition
        elif cond_type == "mute_voice_sign":
            sign_type = node.get("sign_type", "mute").lower()
            planet = node.get("planet")
            house = node.get("house")

            MUTE_SIGNS = {4, 8, 12}
            VOICE_SIGNS = {3, 7, 11, 2, 6, 9}

            target_sign = None
            desc = ""
            if planet:
                p_info = ctx.get_planet(planet, "d1")
                if p_info:
                    target_sign = p_info["sign_index"]
                    desc = f"{planet} in {p_info['sign_name']}"
            elif house is not None:
                h = int(house)
                target_sign = ctx.d1_house_signs.get(h)
                desc = f"House {h} cusp ({INDEX_TO_SIGN_NAME.get(target_sign)})"

            if not target_sign:
                return False, [], ["Target sign not determined"]

            if sign_type == "mute" and target_sign in MUTE_SIGNS:
                return True, [f"{desc} is located in a classical Mute sign ({INDEX_TO_SIGN_NAME.get(target_sign)})"], [f"Mute sign active"]
            elif sign_type == "voice" and target_sign in VOICE_SIGNS:
                return True, [f"{desc} is located in a classical Voice/Musical sign ({INDEX_TO_SIGN_NAME.get(target_sign)})"], [f"Voice sign active"]
            return False, [], []

        # 17. Punarphoo Condition (Saturn-Moon Marital Delay & Cancellation)
        elif cond_type == "punarphoo":
            check_cancellation = node.get("check_cancellation", False)

            sa = ctx.get_planet("Saturn", "d1")
            mo = ctx.get_planet("Moon", "d1")
            su = ctx.get_planet("Sun", "d1")

            if not sa or not mo:
                return False, [], ["Saturn or Moon data missing"]

            is_same_sign = (sa["sign_index"] == mo["sign_index"])
            sa_star = sa.get("star_lord", "").lower()
            mo_star = mo.get("star_lord", "").lower()
            star_conn = (sa_star == "moon" or mo_star == "saturn")
            dist_sa_to_mo = ((mo["sign_index"] - sa["sign_index"]) % 12) + 1
            is_aspect = (dist_sa_to_mo in (3, 7, 10))

            has_punarphoo = is_same_sign or star_conn or is_aspect
            if not has_punarphoo:
                return False, [], []

            is_cancelled = False
            cancel_reasons = []
            if su:
                if su["sign_index"] in (sa["sign_index"], mo["sign_index"]):
                    is_cancelled = True
                    cancel_reasons.append("Sun conjoins Saturn or Moon in same sign")
                su_star = su.get("star_lord", "").lower()
                if su_star in ("saturn", "moon"):
                    is_cancelled = True
                    cancel_reasons.append(f"Sun is in the star of {su_star.capitalize()}")

            if check_cancellation:
                if is_cancelled:
                    return True, [f"Punarphoo Delay is Cancelled: {'; '.join(cancel_reasons)}"], ["Cancellation of Punarphoo verified"]
                return False, [], []
            else:
                if not is_cancelled:
                    ev_notes = []
                    if is_same_sign: ev_notes.append(f"Moon and Saturn conjoin in {mo['sign_name']}")
                    if star_conn: ev_notes.append("Saturn-Moon star connection detected")
                    if is_aspect: ev_notes.append(f"Saturn casts {dist_sa_to_mo}th aspect on Moon")
                    return True, [f"Active Punarphoo Yoga: {'; '.join(ev_notes)} (causes delay/obstacles in marital timing)"], ["Punarphoo connection active"]
                return False, [], ["Punarphoo is cancelled by Sun association"]

        # 18. Magi Astrology Sexual Aspect Condition
        elif cond_type == "magi_aspect":
            p1 = node.get("planet1")
            p2 = node.get("planet2")
            max_orb = float(node.get("orb_degrees", 8.0))

            p1_info = ctx.get_planet(p1, "d1")
            p2_info = ctx.get_planet(p2, "d1")

            if not p1_info or not p2_info:
                return False, [], [f"Planets {p1} or {p2} not found"]

            ang_dist = circular_distance_deg(p1_info["longitude"], p2_info["longitude"])
            aspects_targets = [(0.0, "Conjunction"), (90.0, "Square"), (120.0, "Trine"), (180.0, "Opposition")]

            for tgt_deg, asp_name in aspects_targets:
                diff = abs(ang_dist - tgt_deg)
                if diff <= max_orb:
                    ev = [f"Magi Sexual Aspect: {p1} ({p1_info['sign_name']} {p1_info['degree_in_sign']:.2f}°) forms {asp_name} ({ang_dist:.2f}°, orb {diff:.2f}°) with {p2} ({p2_info['sign_name']} {p2_info['degree_in_sign']:.2f}°)"]
                    reas = [f"Valid {asp_name} detected between {p1} and {p2} within {max_orb}° orb"]
                    return True, ev, reas

            sign_dist = ((p2_info["sign_index"] - p1_info["sign_index"]) % 12) + 1
            if sign_dist in (1, 4, 5, 7, 9, 10):
                asp_label = "Conjunction" if sign_dist == 1 else ("Trine" if sign_dist in (5, 9) else ("Square" if sign_dist in (4, 10) else "Opposition"))
                ev = [f"Magi Sign-Based Aspect ({asp_label}): {p1} in {p1_info['sign_name']} and {p2} in {p2_info['sign_name']}"]
                reas = [f"{asp_label} alignment between {p1} and {p2}"]
                return True, ev, reas

            return False, [], []

        # 19. KP Cuspal Significator Condition
        elif cond_type == "kp_significator":
            cusp = int(node.get("cusp", 7))
            raw_target_houses = node.get("houses") if node.get("houses") is not None else node.get("required_houses", [])
            target_houses = raw_target_houses if isinstance(raw_target_houses, list) else [raw_target_houses]
            target_set = set(int(h) for h in target_houses)
            match_mode = (node.get("match_mode") or "any").lower()

            if not ctx.kp_data or "cusp_details" not in ctx.kp_data:
                lord = ctx.d1_house_lords.get(cusp)
                lord_p = ctx.get_planet(lord, "d1") if lord else None
                if lord_p and lord_p["house"] in target_set:
                    return True, [f"Cusp {cusp} Lord ({lord}) occupies House {lord_p['house']} signifying target matters {list(target_set)}"], [f"Cusp {cusp} connected with target houses"]
                return False, [], ["KP significator details not loaded"]

            cusps = ctx.kp_data.get("cusp_details", [])
            target_detail = next((c for c in cusps if c.get("house") == cusp), None)
            if not target_detail:
                return False, [], [f"KP Cusp {cusp} not found"]

            sl = target_detail.get("sub_lord", "")
            planet_sigs = ctx.kp_data.get("planet_significators", [])
            p_entry = next((ps for ps in planet_sigs if ps.get("planet", "").lower() == sl.lower()), None)
            signified = p_entry.get("signified_houses", []) if p_entry else []

            matches = [h for h in signified if h in target_set]
            p_info = ctx.get_planet(sl, "d1")
            if p_info and p_info.get("house") in target_set and p_info.get("house") not in matches:
                matches.append(p_info["house"])

            if match_mode == "all":
                is_satisfied = bool(target_set and target_set.issubset(set(matches)))
            else:
                is_satisfied = len(matches) > 0

            if is_satisfied:
                ev = [f"KP Cusp {cusp} Sub-Lord ({sl}) signifies required houses {matches} (Full significations: {signified})"]
                reas = [f"Sub-lord {sl} links to key houses {matches} (mode: {match_mode})"]
                return True, ev, reas

            return False, [], []

        # 20. Planetary Avastha Condition (Bala, Kumara, Yuva, Vriddha, Mrita & Aspect Loss)
        elif cond_type == "planetary_avastha":
            req_planet = node.get("planet", "any")
            stage = (node.get("stage") or "").lower()
            loses_aspect = node.get("loses_aspect_potency", False)
            chart = node.get("chart", default_scope).lower()

            target_planets = [req_planet] if req_planet != "any" else list(ctx.d1_planets.keys())
            matched_events = []

            for p_name in target_planets:
                p_info = ctx.get_planet(p_name, chart)
                if not p_info:
                    continue
                deg = p_info["degree_in_sign"]

                is_bala = (0.0 <= deg < 6.0)
                is_kumara = (6.0 <= deg < 12.0)
                is_yuva = (12.0 <= deg < 18.0)
                is_vriddha = (18.0 <= deg < 24.0)
                is_mrita = (24.0 <= deg <= 30.0)

                cur_stage = "bala" if is_bala else ("kumara" if is_kumara else ("yuva" if is_yuva else ("vriddha" if is_vriddha else "mrita")))
                cur_stage_ta = "பால அவஸ்தை (குழந்தை பருவம்)" if is_bala else ("குமார பருவம்" if is_kumara else ("யுவ பருவம் (இளமை)" if is_yuva else ("முதிர்ந்த பருவம்" if is_vriddha else "மிரித அவஸ்தை (முதுமை பருவம்)")))

                match_found = False
                if stage in ("bala", "child") and is_bala:
                    match_found = True
                elif stage in ("kumara", "youth") and is_kumara:
                    match_found = True
                elif stage in ("yuva", "adult") and is_yuva:
                    match_found = True
                elif stage in ("vriddha", "advanced") and is_vriddha:
                    match_found = True
                elif stage in ("mrita", "old", "senile") and is_mrita:
                    match_found = True
                elif loses_aspect and (is_bala or is_mrita):
                    match_found = True

                if match_found:
                    aspect_loss_note = " மற்றும் அதன் பார்வை வலுவை முழுதாக இழக்கிறது" if (is_bala or is_mrita) else ""
                    matched_events.append(
                        f"{p_name} is at {deg:.2f}° in {p_info['sign_name']} ({cur_stage_ta}{aspect_loss_note})"
                    )

            if matched_events:
                ev = [f"Planetary Avastha: {', '.join(matched_events)}"]
                reas = ["Planet occupies an avastha degree threshold matching classical canon"]
                return True, ev, reas
            return False, [], [f"No planet matched avastha '{stage or 'loses_aspect'}' in {chart.upper()}"]

        # 21. Combustion & Classical Aspect Potency Loss Condition
        elif cond_type == "combustion_aspect_loss":
            req_planet = node.get("planet", "any")
            check_exemptions = node.get("check_exemptions", True)
            chart = node.get("chart", default_scope).lower()

            sun_info = ctx.get_planet("Sun", chart)
            if not sun_info:
                return False, [], [f"Sun position not found in {chart.upper()}"]

            # Classical combustion orbs (in degrees)
            combustion_limits = {
                "Mars": 17.0,
                "Jupiter": 11.0,
                "Venus": 10.0,
                "Saturn": 15.0,
            }

            # Check exemptions explicitly if requested
            if check_exemptions and req_planet in ("Moon", "Mercury", "Rahu", "Ketu"):
                p_info = ctx.get_planet(req_planet, chart)
                if not p_info:
                    return False, [], [f"Planet {req_planet} not found in {chart.upper()}"]
                diff = abs(sun_info["longitude"] - p_info["longitude"])
                if diff > 180.0:
                    diff = 360.0 - diff
                if diff <= 12.0:
                    reason_map = {
                        "Moon": "Moon near Sun forms Amavasya (அமாவாசை), exempt from combustion aspect blemish",
                        "Mercury": "Mercury travels adjacent to Sun forming Budhaditya Yoga, exempt from combustion aspect blemish",
                        "Rahu": "Rahu near Sun causes Solar Eclipse, no combustion blemish on the node itself",
                        "Ketu": "Ketu near Sun causes Solar Eclipse, no combustion blemish on the node itself",
                    }
                    ev = [f"{req_planet} is within {diff:.2f}° of Sun: {reason_map.get(req_planet)}"]
                    return True, ev, ["Classical exemption from combustion aspect loss confirmed"]
                return False, [], [f"{req_planet} is not within conjunction range of Sun"]

            # Check vulnerable planets: Mars, Jupiter, Venus, Saturn
            candidates = [req_planet] if req_planet != "any" else list(combustion_limits.keys())
            combust_matches = []

            for p_name in candidates:
                if p_name not in combustion_limits:
                    continue
                p_info = ctx.get_planet(p_name, chart)
                if not p_info:
                    continue

                diff = abs(sun_info["longitude"] - p_info["longitude"])
                if diff > 180.0:
                    diff = 360.0 - diff

                limit = combustion_limits[p_name]
                if p_name == "Venus" and p_info.get("is_retrograde"):
                    limit = 8.0

                if diff <= limit:
                    combust_matches.append(
                        f"{p_name} ({p_info['sign_name']} {p_info['degree_in_sign']:.2f}°) is within {diff:.2f}° of Sun (limit {limit:.1f}°), causing Astangata (அஸ்தங்கம்) and total loss of aspectual potency"
                    )

            if combust_matches:
                ev = [f"Combustion Aspect Loss: {'; '.join(combust_matches)}"]
                reas = ["Planet is combust (Astangata) with the Sun and loses its aspectual strength"]
                return True, ev, reas
            return False, [], [f"No combust planet found among {candidates} in {chart.upper()}"]

        # 22. Graha Yuddha (Planetary War & Defeat Aspect Loss)
        elif cond_type == "graha_yuddha":
            req_planet = node.get("planet", "any")
            req_status = node.get("status", "defeated")  # "defeated", "victor", or "any_war"
            max_orb = float(node.get("max_orb", 1.0))
            chart = node.get("chart", default_scope).lower()

            tara_grahas = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            war_matches = []

            # Compare all pairs of Tara grahas
            for i in range(len(tara_grahas)):
                for j in range(i + 1, len(tara_grahas)):
                    p1_name = tara_grahas[i]
                    p2_name = tara_grahas[j]
                    p1 = ctx.get_planet(p1_name, chart)
                    p2 = ctx.get_planet(p2_name, chart)
                    if not p1 or not p2:
                        continue

                    # Must be in the same sign and within max_orb
                    if p1["sign_index"] == p2["sign_index"]:
                        diff = abs(p1["degree_in_sign"] - p2["degree_in_sign"])
                        if diff <= max_orb:
                            if p1["degree_in_sign"] >= p2["degree_in_sign"]:
                                victor, defeated = p1, p2
                            else:
                                victor, defeated = p2, p1

                            matched_this_pair = False
                            if req_status == "any_war":
                                matched_this_pair = (req_planet == "any" or req_planet in (p1_name, p2_name))
                            elif req_status == "victor":
                                matched_this_pair = (req_planet == "any" or req_planet == victor["name"])
                            elif req_status == "defeated":
                                matched_this_pair = (req_planet == "any" or req_planet == defeated["name"])

                            if matched_this_pair:
                                war_matches.append(
                                    f"Graha Yuddha in {victor['sign_name']}: Victor={victor['name']} ({victor['degree_in_sign']:.2f}°), Defeated={defeated['name']} ({defeated['degree_in_sign']:.2f}°, orb {diff:.2f}°). Defeated planet loses all aspect potency (பார்வை வலுவை முழுதாக இழக்கும்)"
                                )

            if war_matches:
                ev = [f"Planetary War: {'; '.join(war_matches)}"]
                reas = ["Planets are engaged in Graha Yuddha within 1.0° orb in the same sign"]
                return True, ev, reas
            return False, [], [f"No Graha Yuddha event matching status '{req_status}' in {chart.upper()}"]

        return False, [], [f"Unsupported condition type '{cond_type}'"]
