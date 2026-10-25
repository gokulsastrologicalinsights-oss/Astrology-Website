"""Rule-based analysis router (Cultural heuristics, canon audit, and predictions engine)."""

from typing import List, Dict, Any, Optional
import uuid
from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.rules import (
    RuleAuditNote,
    KujaDoshaStatus,
    CareerAnalysisSummary,
)
from app.schemas.horoscope import HoroscopeRequest, HoroscopeResponse
from app.services.ephemeris import calculate_full_horoscope
from app.services.rule_engine import (
    analyze_career_indicators,
    check_kuja_dosha_basic,
    list_documented_rules,
)

# Prediction Rules Engine Imports
from app.schemas.prediction_rules import (
    CategoryGroupSchema,
    EvaluateRulesRequest,
    EvaluateRulesResponse,
    EvaluatedRuleItem,
    RuleValidationRequest,
    RuleValidationResponse,
    RuleTestRequest,
)
from app.services.prediction_rules.categories import (
    PREDICTION_CATEGORY_GROUPS,
    get_all_category_groups,
)
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
)
from app.services.prediction_rules.rules_registry import RulesRegistry
from app.services.prediction_rules.evaluator import (
    AstrologicalRuleEvaluator,
    ChartContext,
)
from app.services.prediction_rules.manager import RuleManagementService
from app.services.auth_service import (
    get_current_user,
    get_admin_user,
    get_supabase_client,
    security,
)

router = APIRouter(prefix="/api/v1/rules", tags=["Rule Engine"])


# ===========================================================================
# 1. Backward-Compatible Endpoints (Preserved for test_rules_and_security.py)
# ===========================================================================

@router.get("/inventory", response_model=List[RuleAuditNote])
def get_rule_inventory() -> List[RuleAuditNote]:
    """List all documented astrological rules and their verification/audit status."""
    return list_documented_rules()


@router.post("/career", response_model=CareerAnalysisSummary)
def get_career_analysis(request: HoroscopeRequest) -> CareerAnalysisSummary:
    """Analyze 10th house, 10th lord, planetary aspects, and Amatyakaraka.

    Traditional Parashari & Jaimini heuristic indicators only.
    """
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
        )
        return analyze_career_indicators(horoscope)
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Career rule analysis failed: {str(exc)}",
        )


# ===========================================================================
# 2. Prediction Categories Registry Endpoint
# ===========================================================================

@router.get("/categories", response_model=List[CategoryGroupSchema])
def get_prediction_categories() -> List[CategoryGroupSchema]:
    """Retrieve all 8 category groups and their 67 subcategories."""
    return PREDICTION_CATEGORY_GROUPS


# ===========================================================================
# 3. Rule Evaluation Engine Endpoint
# ===========================================================================

@router.post("/evaluate", response_model=EvaluateRulesResponse)
async def evaluate_rules(
    request: EvaluateRulesRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> EvaluateRulesResponse:
    """Deterministically evaluate prediction rules against opened horoscope or saved ID.

    Consumes precalculated chart data without recalculating planetary coordinates.
    """
    horoscope_data: Optional[HoroscopeResponse] = request.horoscope
    dasa_data = request.dasa
    kp_data = request.kp

    # If saved_horoscope_id is provided, fetch and verify ownership
    if request.saved_horoscope_id:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client unavailable for saved horoscope lookup.",
            )

        clean_id = request.saved_horoscope_id.strip()
        res = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
        if not res.data or len(res.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saved horoscope '{clean_id}' not found.",
            )

        row = res.data[0]
        # Authorization check: verify token if present, or enforce user matches
        if credentials and credentials.credentials:
            current_user = await get_current_user(credentials)
            is_admin = current_user.get("role") == "admin"
            if not is_admin and str(row.get("user_id")) != str(current_user["id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: You do not have permission to access this saved horoscope.",
                )

        calc_result = row.get("calculation_result") or {}
        if "horoscope" in calc_result:
            horoscope_data = HoroscopeResponse(**calc_result["horoscope"])
            if not dasa_data and "dasa" in calc_result:
                dasa_data = calc_result["dasa"]
            if not kp_data and "kp" in calc_result:
                kp_data = calc_result["kp"]
        else:
            horoscope_data = HoroscopeResponse(**calc_result)

    if not horoscope_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'horoscope' payload or valid 'saved_horoscope_id' must be provided.",
        )

    # Build context
    ctx = ChartContext(horoscope=horoscope_data, dasa_data=dasa_data, kp_data=kp_data)

    # Filter applicable rules from registry
    all_rules = RulesRegistry.get_all_rules()
    target_category = request.category_slug
    target_subcategory = request.subcategory
    target_scope = (request.chart_scope or "both").lower()
    target_system = (request.astrology_system or "all").lower()

    filtered_rules = []
    for r in all_rules:
        if not r.is_enabled:
            continue
        if target_category and r.category_slug != target_category:
            continue
        if target_subcategory and r.subcategory and r.subcategory != target_subcategory:
            continue
        if target_scope != "both" and r.chart_scope != ChartScope.BOTH and r.chart_scope.value != target_scope:
            continue
        if target_system != "all" and r.astrology_system.value != target_system and r.astrology_system != AstrologySystem.COMBINED:
            continue
        filtered_rules.append(r)

    # Evaluate rules deterministically
    results: List[EvaluatedRuleItem] = []
    total_matched = 0
    total_unevaluable = 0

    for rule in filtered_rules:
        eval_res = AstrologicalRuleEvaluator.evaluate_rule(rule, ctx)
        item_dict = eval_res.to_dict(language=request.language)
        results.append(EvaluatedRuleItem(**item_dict))
        if eval_res.matched:
            total_matched += 1
        elif eval_res.unevaluable:
            total_unevaluable += 1

    return EvaluateRulesResponse(
        total_rules_evaluated=len(filtered_rules),
        total_matched=total_matched,
        total_unevaluable=total_unevaluable,
        category_slug=target_category,
        subcategory=target_subcategory,
        language=request.language,
        results=results,
    )


# ===========================================================================
# 4. Manual Rule Management Endpoints (Admin Authorized)
# ===========================================================================

@router.get("/definitions", response_model=List[Dict[str, Any]])
def list_rule_definitions(
    category_slug: Optional[str] = None,
    subcategory: Optional[str] = None,
    enabled_only: bool = False,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
) -> List[Dict[str, Any]]:
    """List all rules in the registry for administrative inspection."""
    rules = RulesRegistry.get_all_rules()
    out = []
    for r in rules:
        if category_slug and r.category_slug != category_slug:
            continue
        if subcategory and r.subcategory and r.subcategory != subcategory:
            continue
        if enabled_only and not r.is_enabled:
            continue
        out.append(r.model_dump())
    return out


@router.post("/validate", response_model=RuleValidationResponse)
def validate_rule_ast(request: RuleValidationRequest) -> RuleValidationResponse:
    """Validate a rule condition AST and metadata without executing code."""
    is_valid, errors = RuleManagementService.validate_rule_definition(request.rule)
    return RuleValidationResponse(is_valid=is_valid, errors=errors)


@router.post("/test", response_model=Dict[str, Any])
def test_rule_against_horoscope(
    request: RuleTestRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Test a proposed rule definition against a test chart without saving."""
    is_valid, errors = RuleManagementService.validate_rule_definition(request.rule)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rule validation failed: {'; '.join(errors)}",
        )

    horoscope_data = request.horoscope
    if request.saved_horoscope_id:
        supabase = get_supabase_client()
        if supabase:
            res = supabase.table("saved_horoscopes").select("*").eq("id", request.saved_horoscope_id.strip()).execute()
            if res.data and len(res.data) > 0:
                calc_res = res.data[0].get("calculation_result") or {}
                if "horoscope" in calc_res:
                    horoscope_data = HoroscopeResponse(**calc_res["horoscope"])
                else:
                    horoscope_data = HoroscopeResponse(**calc_res)

    if not horoscope_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Must provide either 'horoscope' or valid 'saved_horoscope_id' to test rule.",
        )

    ctx = ChartContext(horoscope=horoscope_data, dasa_data=request.dasa, kp_data=request.kp)
    temp_rule = AstrologicalRuleDefinition(**request.rule)
    res = AstrologicalRuleEvaluator.evaluate_rule(temp_rule, ctx)
    return res.to_dict(language=request.language)


@router.post("/definitions", status_code=status.HTTP_201_CREATED)
def create_or_update_rule(
    rule_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Create or update a rule definition. Requires administrative authorization."""
    try:
        rule, created = RuleManagementService.save_or_update_rule(rule_data, user_id=admin_user.get("id"))
        return {
            "status": "success",
            "action": "created" if created else "updated",
            "rule": rule.model_dump(),
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save rule: {str(exc)}",
        )


@router.put("/definitions/{rule_id}")
def update_existing_rule(
    rule_id: str,
    rule_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Update an existing rule and increment its version."""
    rule_data["rule_id"] = rule_id
    try:
        rule, created = RuleManagementService.save_or_update_rule(rule_data, user_id=admin_user.get("id"))
        return {
            "status": "success",
            "action": "created" if created else "updated",
            "rule": rule.model_dump(),
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )


@router.patch("/definitions/{rule_id}/status")
def toggle_rule_status(
    rule_id: str,
    enabled: bool,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Enable or disable a rule in the registry."""
    rule = RulesRegistry.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule '{rule_id}' not found in registry.",
        )
    rule.is_enabled = enabled
    return {
        "status": "success",
        "rule_id": rule_id,
        "is_enabled": rule.is_enabled,
    }
