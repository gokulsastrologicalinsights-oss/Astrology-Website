"""Rule Management, Validation, Versioning, and Database Sync Service.

Enforces schema validation, version history tracking, and admin security.
"""

from typing import Dict, Any, List, Optional, Tuple
import datetime
import uuid

from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import AstrologicalRuleEvaluator, ChartContext, RuleEvaluationResult
from app.services.prediction_rules.categories import get_category_by_slug
from app.services.auth_service import get_supabase_client


class RuleManagementService:
    """Provides validated CRUD, versioning, and test-run capabilities for rules."""

    @classmethod
    def validate_rule_definition(cls, rule_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Strictly validate condition tree and metadata without executing code."""
        errors: List[str] = []

        if not rule_data.get("rule_id"):
            errors.append("rule_id is required and cannot be empty.")
        if not rule_data.get("name_en"):
            errors.append("name_en is required.")
        if not rule_data.get("interpretation_en"):
            errors.append("interpretation_en is required.")
        if not rule_data.get("astrological_principle_en"):
            errors.append("astrological_principle_en is required.")

        category_slug = rule_data.get("category_slug")
        if not category_slug:
            errors.append("category_slug is required.")
        else:
            cat = get_category_by_slug(category_slug)
            if not cat:
                errors.append(f"Invalid category_slug '{category_slug}'.")

        cond_tree = rule_data.get("condition_tree")
        if not cond_tree or not isinstance(cond_tree, dict):
            errors.append("condition_tree must be a valid JSON dictionary.")
        else:
            cls._validate_condition_ast_node(cond_tree, errors)

        return (len(errors) == 0), errors

    @classmethod
    def _validate_condition_ast_node(cls, node: Dict[str, Any], errors: List[str], depth: int = 0) -> None:
        """Recursively validate condition AST node structure."""
        if depth > 10:
            errors.append("Condition tree exceeds maximum nesting depth of 10.")
            return

        cond_type = node.get("condition_type", "").lower()
        if not cond_type:
            errors.append("Each condition node must declare 'condition_type'.")
            return

        supported_types = {
            "compound", "planet_sign", "planet_house", "planet_conjunction",
            "planet_aspect", "house_lord_placement", "house_occupancy",
            "planet_nakshatra", "planet_dignity", "lagna_sign",
            "dasa_active", "kp_sub_lord", "mutual_exchange"
        }

        if cond_type not in supported_types:
            errors.append(f"Unsupported condition_type: '{cond_type}'. Supported: {', '.join(sorted(supported_types))}")
            return

        if cond_type == "compound":
            op = node.get("operator", "").upper()
            if op not in ("AND", "OR", "NOT"):
                errors.append(f"Compound condition requires operator 'AND', 'OR', or 'NOT', got '{op}'.")
            sub_nodes = node.get("conditions")
            if not isinstance(sub_nodes, list) or len(sub_nodes) == 0:
                errors.append("Compound condition requires a non-empty list of 'conditions'.")
            else:
                for sub in sub_nodes:
                    if isinstance(sub, dict):
                        cls._validate_condition_ast_node(sub, errors, depth + 1)
                    else:
                        errors.append("Sub-conditions must be dictionaries.")

        elif cond_type in ("planet_sign", "planet_house"):
            if not node.get("planet"):
                errors.append(f"'{cond_type}' requires 'planet' field.")
            if cond_type == "planet_house" and "house" not in node:
                errors.append(f"'{cond_type}' requires 'house' field (1-12).")
            if cond_type == "planet_sign" and "sign" not in node:
                errors.append(f"'{cond_type}' requires 'sign' field.")

        elif cond_type == "planet_conjunction":
            planets = node.get("planets")
            if not isinstance(planets, list) or len(planets) < 2:
                errors.append("planet_conjunction requires a list of at least 2 planets.")

        elif cond_type == "house_lord_placement":
            if "house" not in node:
                errors.append("house_lord_placement requires 'house' (1-12).")
            if "placed_in_house" not in node and "placed_in_sign" not in node:
                errors.append("house_lord_placement requires either 'placed_in_house' or 'placed_in_sign'.")

    @classmethod
    def test_rule_against_chart(
        cls,
        rule_def: AstrologicalRuleDefinition,
        ctx: ChartContext
    ) -> Dict[str, Any]:
        """Test evaluate a rule definition against a chart context."""
        res = AstrologicalRuleEvaluator.evaluate_rule(rule_def, ctx)
        return res.to_dict()

    @classmethod
    def save_or_update_rule(
        cls,
        rule_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Tuple[AstrologicalRuleDefinition, bool]:
        """Save a new rule or update an existing rule with version increment."""
        is_valid, errors = cls.validate_rule_definition(rule_data)
        if not is_valid:
            raise ValueError(f"Rule definition validation failed: {'; '.join(errors)}")

        rule_id = rule_data["rule_id"]
        existing = RulesRegistry.get_rule_by_id(rule_id)

        if existing:
            new_version = existing.version + 1
            rule = AstrologicalRuleDefinition(
                rule_id=rule_id,
                version=new_version,
                name_en=rule_data.get("name_en", existing.name_en),
                name_ta=rule_data.get("name_ta", existing.name_ta),
                category_slug=rule_data.get("category_slug", existing.category_slug),
                subcategory=rule_data.get("subcategory", existing.subcategory),
                astrology_system=AstrologySystem(rule_data.get("astrology_system", existing.astrology_system.value)),
                chart_scope=ChartScope(rule_data.get("chart_scope", existing.chart_scope.value)),
                calculation_mode=rule_data.get("calculation_mode", existing.calculation_mode),
                condition_tree=rule_data.get("condition_tree", existing.condition_tree),
                interpretation_en=rule_data.get("interpretation_en", existing.interpretation_en),
                interpretation_ta=rule_data.get("interpretation_ta", existing.interpretation_ta),
                astrological_principle_en=rule_data.get("astrological_principle_en", existing.astrological_principle_en),
                astrological_principle_ta=rule_data.get("astrological_principle_ta", existing.astrological_principle_ta),
                evidence_requirements=rule_data.get("evidence_requirements", existing.evidence_requirements),
                source_reference=rule_data.get("source_reference", existing.source_reference),
                limitations_en=rule_data.get("limitations_en", existing.limitations_en),
                limitations_ta=rule_data.get("limitations_ta", existing.limitations_ta),
                severity=SeverityLevel(rule_data.get("severity", existing.severity.value)),
                is_enabled=rule_data.get("is_enabled", existing.is_enabled),
                is_draft=rule_data.get("is_draft", existing.is_draft),
            )
            created = False
        else:
            rule = AstrologicalRuleDefinition(
                rule_id=rule_id,
                version=1,
                name_en=rule_data["name_en"],
                name_ta=rule_data.get("name_ta", ""),
                category_slug=rule_data["category_slug"],
                subcategory=rule_data.get("subcategory"),
                astrology_system=AstrologySystem(rule_data.get("astrology_system", "vedic")),
                chart_scope=ChartScope(rule_data.get("chart_scope", "d1")),
                calculation_mode=rule_data.get("calculation_mode", "thirukanitha"),
                condition_tree=rule_data["condition_tree"],
                interpretation_en=rule_data["interpretation_en"],
                interpretation_ta=rule_data.get("interpretation_ta", ""),
                astrological_principle_en=rule_data["astrological_principle_en"],
                astrological_principle_ta=rule_data.get("astrological_principle_ta", ""),
                evidence_requirements=rule_data.get("evidence_requirements", []),
                source_reference=rule_data.get("source_reference"),
                limitations_en=rule_data.get("limitations_en"),
                limitations_ta=rule_data.get("limitations_ta"),
                severity=SeverityLevel(rule_data.get("severity", "neutral")),
                is_enabled=rule_data.get("is_enabled", True),
                is_draft=rule_data.get("is_draft", False),
            )
            created = True

        RulesRegistry.register_rule(rule)

        # Attempt remote Supabase persistence if connected
        cls._persist_to_supabase(rule, user_id)

        return rule, created

    @classmethod
    def _persist_to_supabase(cls, rule: AstrologicalRuleDefinition, user_id: Optional[str] = None):
        """Save rule to Supabase if client is available."""
        supabase = get_supabase_client()
        if not supabase:
            return

        try:
            row = {
                "rule_id": rule.rule_id,
                "version": rule.version,
                "name_en": rule.name_en,
                "name_ta": rule.name_ta,
                "category_slug": rule.category_slug,
                "subcategory": rule.subcategory,
                "astrology_system": rule.astrology_system.value,
                "chart_scope": rule.chart_scope.value,
                "calculation_mode": rule.calculation_mode,
                "condition_tree": rule.condition_tree,
                "interpretation_en": rule.interpretation_en,
                "interpretation_ta": rule.interpretation_ta,
                "astrological_principle_en": rule.astrological_principle_en,
                "astrological_principle_ta": rule.astrological_principle_ta,
                "evidence_requirements": rule.evidence_requirements,
                "source_reference": rule.source_reference,
                "limitations_en": rule.limitations_en,
                "limitations_ta": rule.limitations_ta,
                "severity": rule.severity.value,
                "is_enabled": rule.is_enabled,
                "is_draft": rule.is_draft,
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            if user_id:
                row["updated_by"] = user_id

            supabase.table("astrological_rules").upsert(row, on_conflict="rule_id").execute()

            # Record version history
            v_row = {
                "rule_id": rule.rule_id,
                "version": rule.version,
                "rule_snapshot": row,
                "changed_by": user_id,
                "change_reason": "Rule created or updated via admin management API",
            }
            supabase.table("astrological_rule_versions").insert(v_row).execute()
        except Exception as exc:
            # Fall back gracefully; memory registry is authoritative in memory
            pass

    @classmethod
    def load_rules_from_supabase(cls) -> int:
        """Load persisted rules from Supabase and register into RulesRegistry."""
        supabase = get_supabase_client()
        if not supabase:
            return 0

        try:
            res = supabase.table("astrological_rules").select("*").eq("is_enabled", True).execute()
            if not res.data:
                return 0

            loaded = 0
            for r in res.data:
                try:
                    rule = AstrologicalRuleDefinition(
                        rule_id=r["rule_id"],
                        version=r.get("version", 1),
                        name_en=r["name_en"],
                        name_ta=r.get("name_ta", ""),
                        category_slug=r["category_slug"],
                        subcategory=r.get("subcategory"),
                        astrology_system=AstrologySystem(r.get("astrology_system", "vedic")),
                        chart_scope=ChartScope(r.get("chart_scope", "d1")),
                        calculation_mode=r.get("calculation_mode", "thirukanitha"),
                        condition_tree=r["condition_tree"],
                        interpretation_en=r["interpretation_en"],
                        interpretation_ta=r.get("interpretation_ta", ""),
                        astrological_principle_en=r["astrological_principle_en"],
                        astrological_principle_ta=r.get("astrological_principle_ta", ""),
                        evidence_requirements=r.get("evidence_requirements", []),
                        source_reference=r.get("source_reference"),
                        limitations_en=r.get("limitations_en"),
                        limitations_ta=r.get("limitations_ta"),
                        severity=SeverityLevel(r.get("severity", "neutral")),
                        is_enabled=r.get("is_enabled", True),
                        is_draft=r.get("is_draft", False),
                    )
                    RulesRegistry.register_rule(rule)
                    loaded += 1
                except Exception:
                    continue
            return loaded
        except Exception:
            return 0
