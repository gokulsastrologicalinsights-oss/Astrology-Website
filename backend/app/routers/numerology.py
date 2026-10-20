"""Numerology Calculation & Reports Router.

Deterministic endpoints for Traditional Numerology, Destiny Matrix,
Advanced Analysis (Lo Shu / Pinnacles), and Supabase Report Management.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query

from app.schemas.numerology import (
    TraditionalNumerologyRequest,
    TraditionalNumerologyResponse,
    TraditionalNumberDetail,
    LetterMapping,
    WordBreakdown,
    KarmicDebtItem,
    CalculationBreakdown,
    DestinyMatrixRequest,
    DestinyMatrixResponse,
    AdvancedAnalysisRequest,
    AdvancedAnalysisResponse,
    SaveNumerologyReportRequest,
    SavedNumerologyReportResponse,
    ExportNumerologyPdfRequest,
    NumerologyMetadataResponse,
    NameComponentDetail,
    NameAnalysisRequest,
    NameAnalysisResponse,
    NameCorrectionRequest,
    NameCandidateResult,
    NameCorrectionResponse,
    FounderInput,
    FounderEvaluationResult,
    TaglineAnalysisResult,
    DomainHandleAnalysisResult,
    BusinessCandidateResult,
    BusinessNumerologyRequest,
    BusinessNumerologyResponse,
    PhoneAnalysisDetail,
    PhoneCandidateResult,
    PhoneNumerologyRequest,
    PhoneNumerologyResponse,
    VehicleOwnerInput,
    VehicleOwnerEvaluation,
    VehicleAnalysisDetail,
    VehicleCandidateResult,
    VehicleNumerologyRequest,
    VehicleNumerologyResponse,
    PropertyResidentInput,
    PropertyResidentEvaluation,
    PropertyComponentDetail,
    PropertyCandidateInput,
    PropertyCandidateResult,
    PropertyNumerologyRequest,
    PropertyNumerologyResponse,
    MarriagePersonProfile,
    MarriageComponentComparison,
    MarriageNumerologyRequest,
    MarriageNumerologyResponse,
    FamilyMemberInput,
    FamilyMemberEvaluation,
    BabyNameCandidateResult,
    FamilyPairwiseComparison,
    FamilyDistributionItem,
    FamilyNumerologyRequest,
    FamilyNumerologyResponse,
)
from app.services.auth_service import get_current_user
from app.services.numerology import (
    calculate_birth_psychic_number,
    calculate_life_path,
    calculate_life_path_detailed,
    calculate_birthday_number,
    calculate_attitude_number,
    calculate_personal_year,
    calculate_name_numbers,
    calculate_maturity_number,
    detect_karmic_debts,
    get_interpretation_for_number,
    generate_synthesized_reports,
    calculate_destiny_matrix,
    calculate_compatibility,
    calculate_advanced_analysis,
    save_numerology_report,
    list_numerology_reports,
    get_numerology_report,
    delete_numerology_report,
    analyze_name_components,
    generate_and_score_name_corrections,
    evaluate_business_brand_candidates,
    analyze_phone_numerology_full,
    mask_phone_number,
    analyze_vehicle_numerology_full,
    analyze_property_numerology_full,
    analyze_marriage_numerology_full,
    analyze_family_numerology_full,
    generate_numerology_pdf_bytes,
    ENGINE_VERSION,
)

router = APIRouter(prefix="/api/v1/numerology", tags=["Numerology"])


# ------------------------------------------------------------------------------
# 1. Traditional Numerology
# ------------------------------------------------------------------------------

@router.post("/traditional", response_model=TraditionalNumerologyResponse)
def compute_traditional_numerology(request: TraditionalNumerologyRequest) -> TraditionalNumerologyResponse:
    """Calculate core numbers, master numbers, and interpretations for Traditional Numerology."""
    try:
        lang = request.language
        conv = request.system_convention

        # 1. Birthdate derivations
        psychic_num, psychic_method, psychic_data = calculate_birth_psychic_number(request.birth_date)
        lp_res = calculate_life_path_detailed(request.birth_date)
        lp = lp_res["life_path"]
        lp_method = lp_res["method_str"]
        b_num, b_method = calculate_birthday_number(request.birth_date)
        att, att_method = calculate_attitude_number(request.birth_date)
        py, py_method = calculate_personal_year(request.birth_date, target_year=2026)

        # 2. Name derivations
        name_res = calculate_name_numbers(request.full_name, convention=conv)
        expr = name_res["expression"]
        soul = name_res["soul_urge"]
        pers = name_res["personality"]

        # 3. Maturity number
        mat, mat_method = calculate_maturity_number(lp, expr)

        # 4. Karmic debts detection across Day, Life Path, Expression, Soul Urge
        debts = detect_karmic_debts(
            birth_date=request.birth_date,
            name=request.full_name,
            lang=lang,
            lp_compound=lp_res.get("compound_period_total"),
            expr_compound=name_res.get("compound_expression"),
            soul_compound=name_res.get("compound_soul_urge"),
        )
        karmic_debt_items = [
            KarmicDebtItem(
                number=d["number"],
                source=d["source"],
                title=d["title"],
                description=d["description"],
                remedy_focus=d["remedy_focus"],
            )
            for d in debts
        ]

        # 5. Interpretations
        def build_detail(
            name: str,
            val: int,
            method: str,
            raw_val: Optional[int] = None,
            steps: Optional[List[str]] = None,
        ) -> TraditionalNumberDetail:
            interp = get_interpretation_for_number("life_path", val, lang=lang)
            return TraditionalNumberDetail(
                number_name=name,
                number_value=val,
                calculation_method=method,
                is_master=val in (11, 22, 33),
                short_interpretation=interp["short"],
                detailed_interpretation=interp["detailed"],
                key_attributes=interp["attributes"],
                raw_value=raw_val,
                reduction_steps=steps,
            )

        psychic_detail = build_detail(
            "Birth / Psychic Number (Mulank)",
            psychic_num,
            psychic_method,
            raw_val=psychic_data["raw_day"],
            steps=psychic_data["reduction_steps"],
        )
        lp_detail = build_detail(
            "Life Path Number",
            lp,
            lp_method,
            raw_val=lp_res.get("compound_period_total"),
            steps=lp_res["period_breakdown"]["reduction_steps"],
        )
        expr_detail = build_detail(
            "Expression / Destiny Number",
            expr,
            name_res["expression_method"],
            raw_val=name_res.get("compound_expression"),
            steps=name_res.get("expression_steps"),
        )
        soul_detail = build_detail(
            "Soul Urge Number",
            soul,
            name_res["soul_urge_method"],
            raw_val=name_res.get("compound_soul_urge"),
            steps=name_res.get("soul_urge_steps"),
        )
        pers_detail = build_detail(
            "Personality Number",
            pers,
            name_res["personality_method"],
            raw_val=name_res.get("compound_personality"),
            steps=name_res.get("personality_steps"),
        )
        bday_detail = build_detail("Birthday Number", b_num, b_method)
        att_detail = build_detail("Attitude Number", att, att_method)
        mat_detail = build_detail("Maturity / Divine Purpose Number", mat, mat_method)
        py_detail = build_detail("Personal Year Number (2026)", py, py_method)

        # 6. Synthesized themes
        synth = generate_synthesized_reports(lp, expr, soul, pers, conv, lang=lang)

        # 7. Transparent Calculation Breakdown
        breakdown = CalculationBreakdown(
            system_convention=conv,
            source_birth_date=request.birth_date,
            birth_date_digits=lp_res["full_sum_breakdown"]["digits"],
            life_path_period_reduction=lp_res["period_breakdown"],
            life_path_full_sum=lp_res["full_sum_breakdown"],
            birth_number_reduction=psychic_data,
            letter_mappings=[
                LetterMapping(
                    char=m["char"],
                    value=m["value"],
                    is_vowel=m["is_vowel"],
                    word=m["word"],
                )
                for m in name_res.get("letter_mappings", [])
            ],
            word_breakdowns=[
                WordBreakdown(
                    word=w["word"],
                    letter_sum=w["letter_sum"],
                    vowel_sum=w["vowel_sum"],
                    consonant_sum=w["consonant_sum"],
                    reduced_expression=w["reduced_expression"],
                )
                for w in name_res.get("word_breakdowns", [])
            ],
            expression_reduction=name_res.get("expression_steps", []),
            soul_urge_reduction=name_res.get("soul_urge_steps", []),
            personality_reduction=name_res.get("personality_steps", []),
            maturity_reduction=[
                f"Life Path ({lp}) + Expression ({expr}) = {lp + expr}",
                f"Reduced -> {mat}",
            ],
        )

        return TraditionalNumerologyResponse(
            person_name=request.full_name.strip(),
            birth_date=request.birth_date,
            system_convention=conv,
            engine_version=ENGINE_VERSION,
            birth_psychic_number=psychic_detail,
            life_path=lp_detail,
            expression_destiny=expr_detail,
            soul_urge=soul_detail,
            personality=pers_detail,
            birthday_number=bday_detail,
            attitude_number=att_detail,
            maturity_number=mat_detail,
            personal_year=py_detail,
            karmic_debts=karmic_debt_items,
            calculation_breakdown=breakdown,
            karmic_lessons=name_res["karmic_lessons"],
            hidden_passion=name_res["hidden_passion"],
            strengths=synth["strengths"],
            challenges=synth["challenges"],
            career_tendencies=synth["career_tendencies"],
            financial_tendencies=synth["financial_tendencies"],
            love_themes=synth["love_themes"],
            overall_synthesis=synth["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Traditional Numerology calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 2. Name Analysis & Correction Studio Endpoints
# ------------------------------------------------------------------------------

@router.post("/name/analyze", response_model=NameAnalysisResponse)
def compute_name_analysis(request: NameAnalysisRequest) -> NameAnalysisResponse:
    """Analyze multi-component name: first, middle, surname, initials, and full name with letter breakdowns."""
    try:
        conv = request.system_convention
        res = analyze_name_components(request.full_name, convention=conv)
        return NameAnalysisResponse(
            full_name=request.full_name.strip(),
            convention=conv,
            engine_version=ENGINE_VERSION,
            expression=res["expression"],
            compound_expression=res["compound_expression"],
            soul_urge=res["soul_urge"],
            personality=res["personality"],
            is_master=res["is_master"],
            reduction_steps=res["reduction_steps"],
            letter_mappings=[
                LetterMapping(
                    char=m["char"],
                    value=m["value"],
                    is_vowel=m["is_vowel"],
                    word=m["word"],
                )
                for m in res["letter_mappings"]
            ],
            word_breakdowns=[
                WordBreakdown(
                    word=w["word"],
                    letter_sum=w["letter_sum"],
                    vowel_sum=w["vowel_sum"],
                    consonant_sum=w["consonant_sum"],
                    reduced_expression=w["reduced_expression"],
                )
                for w in res["word_breakdowns"]
            ],
            components=[
                NameComponentDetail(
                    component_type=c["component_type"],
                    text=c["text"],
                    expression=c["expression"],
                    compound_expression=c["compound_expression"],
                    soul_urge=c["soul_urge"],
                    personality=c["personality"],
                    reduction_steps=c["reduction_steps"],
                    letter_mappings=[
                        LetterMapping(
                            char=m["char"],
                            value=m["value"],
                            is_vowel=m["is_vowel"],
                            word=m["word"],
                        )
                        for m in c["letter_mappings"]
                    ],
                )
                for c in res["components"]
            ],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Name analysis error: {str(exc)}",
        )


@router.post("/name/suggest-corrections", response_model=NameCorrectionResponse)
def compute_name_corrections(request: NameCorrectionRequest) -> NameCorrectionResponse:
    """Generate, score, and rank candidate spelling variations for target vibrational harmony."""
    try:
        conv = request.system_convention
        res = generate_and_score_name_corrections(
            original_name=request.original_name,
            convention=conv,
            target_number=request.target_number,
            birth_date=request.birth_date,
            custom_variations=request.custom_variations,
            language=request.language,
            max_candidates=request.max_candidates,
            allow_vowel_changes=request.allow_vowel_changes,
            allow_consonant_doubling=request.allow_consonant_doubling,
            allow_phonetic_replacements=request.allow_phonetic_replacements,
        )

        orig = res["original_analysis"]
        orig_analysis_model = NameAnalysisResponse(
            full_name=request.original_name.strip(),
            convention=conv,
            engine_version=ENGINE_VERSION,
            expression=orig["expression"],
            compound_expression=orig["compound_expression"],
            soul_urge=orig["soul_urge"],
            personality=orig["personality"],
            is_master=orig["is_master"],
            reduction_steps=orig["reduction_steps"],
            letter_mappings=[
                LetterMapping(
                    char=m["char"],
                    value=m["value"],
                    is_vowel=m["is_vowel"],
                    word=m["word"],
                )
                for m in orig["letter_mappings"]
            ],
            word_breakdowns=[
                WordBreakdown(
                    word=w["word"],
                    letter_sum=w["letter_sum"],
                    vowel_sum=w["vowel_sum"],
                    consonant_sum=w["consonant_sum"],
                    reduced_expression=w["reduced_expression"],
                )
                for w in orig["word_breakdowns"]
            ],
            components=[
                NameComponentDetail(
                    component_type=c["component_type"],
                    text=c["text"],
                    expression=c["expression"],
                    compound_expression=c["compound_expression"],
                    soul_urge=c["soul_urge"],
                    personality=c["personality"],
                    reduction_steps=c["reduction_steps"],
                    letter_mappings=[
                        LetterMapping(
                            char=m["char"],
                            value=m["value"],
                            is_vowel=m["is_vowel"],
                            word=m["word"],
                        )
                        for m in c["letter_mappings"]
                    ],
                )
                for c in orig["components"]
            ],
        )

        candidates_model: List[NameCandidateResult] = []
        for c in res["candidates"]:
            candidates_model.append(
                NameCandidateResult(
                    name=c["name"],
                    variation_type=c["variation_type"],
                    expression_number=c["expression_number"],
                    compound_expression=c["compound_expression"],
                    soul_urge_number=c["soul_urge_number"],
                    personality_number=c["personality_number"],
                    is_master=c["is_master"],
                    matches_target=c["matches_target"],
                    harmony_score=c["harmony_score"],
                    pronunciation_score=c["pronunciation_score"],
                    simplicity_score=c["simplicity_score"],
                    composite_score=c["composite_score"],
                    letter_mappings=[
                        LetterMapping(
                            char=m["char"],
                            value=m["value"],
                            is_vowel=m["is_vowel"],
                            word=m["word"],
                        )
                        for m in c["letter_mappings"]
                    ],
                    word_breakdowns=[
                        WordBreakdown(
                            word=w["word"],
                            letter_sum=w["letter_sum"],
                            vowel_sum=w["vowel_sum"],
                            consonant_sum=w["consonant_sum"],
                            reduced_expression=w["reduced_expression"],
                        )
                        for w in c["word_breakdowns"]
                    ],
                    reduction_steps=c["reduction_steps"],
                    vibrational_synthesis=c["vibrational_synthesis"],
                )
            )

        return NameCorrectionResponse(
            original_name=request.original_name.strip(),
            system_convention=conv,
            engine_version=ENGINE_VERSION,
            target_number=res["target_number"],
            target_source=res["target_source"],
            original_analysis=orig_analysis_model,
            candidates=candidates_model,
            scoring_explanation=res["scoring_explanation"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Name correction error: {str(exc)}",
        )


@router.post("/business/analyze", response_model=BusinessNumerologyResponse)
def compute_business_numerology(request: BusinessNumerologyRequest) -> BusinessNumerologyResponse:
    """Analyze corporate legal vs brand name, multi-founder alignment, industry vibrations, and candidate ranking."""
    try:
        conv = request.system_convention
        founders_data = [f.model_dump() for f in request.founders]
        res = evaluate_business_brand_candidates(
            legal_name=request.legal_name,
            brand_name=request.brand_name,
            tagline=request.tagline,
            domain_or_handle=request.domain_or_handle,
            convention=conv,
            industry_category=request.industry_category,
            founders=founders_data,
            custom_candidates=request.custom_candidates,
            max_candidates=request.max_candidates,
            language=request.language,
        )

        def build_cand_model(c: Dict[str, Any]) -> BusinessCandidateResult:
            return BusinessCandidateResult(
                name=c["name"],
                candidate_type=c["candidate_type"],
                expression_number=c["expression_number"],
                compound_expression=c["compound_expression"],
                soul_urge_number=c["soul_urge_number"],
                personality_number=c["personality_number"],
                is_master=c["is_master"],
                industry_harmony_score=c["industry_harmony_score"],
                founder_harmony_score=c["founder_harmony_score"],
                pronunciation_score=c["pronunciation_score"],
                simplicity_score=c["simplicity_score"],
                composite_score=c["composite_score"],
                is_favorable=c["is_favorable"],
                vibrational_synthesis=c["vibrational_synthesis"],
                letter_mappings=[
                    LetterMapping(char=m["char"], value=m["value"], is_vowel=m["is_vowel"], word=m["word"])
                    for m in c.get("letter_mappings", [])
                ],
                reduction_steps=c.get("reduction_steps", []),
                founder_alignments=[
                    FounderEvaluationResult(**f) for f in c.get("founder_alignments", [])
                ],
            )

        tagline_model = TaglineAnalysisResult(**res["tagline_analysis"]) if res.get("tagline_analysis") else None
        domain_model = DomainHandleAnalysisResult(**res["domain_analysis"]) if res.get("domain_analysis") else None

        return BusinessNumerologyResponse(
            legal_name=res["legal_name"],
            normalized_brand_name=res["normalized_brand_name"],
            acronym=res["acronym"],
            detected_suffixes=res["detected_suffixes"],
            system_convention=conv,
            industry_category=res["industry_category"],
            industry_vibrations=res["industry_vibrations"],
            engine_version=ENGINE_VERSION,
            legal_analysis=build_cand_model(res["legal_analysis"]),
            brand_analysis=build_cand_model(res["brand_analysis"]),
            tagline_analysis=tagline_model,
            domain_analysis=domain_model,
            partnership_matrix=res["partnership_matrix"],
            candidates=[build_cand_model(c) for c in res["candidates"]],
            scoring_explanation=res["scoring_explanation"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business Numerology error: {str(exc)}",
        )


@router.post("/phone/analyze", response_model=PhoneNumerologyResponse)
def compute_phone_numerology(request: PhoneNumerologyRequest) -> PhoneNumerologyResponse:
    """Analyze phone number vibrations, digit frequencies, missing digits, patterns, and compatibility."""
    try:
        res = analyze_phone_numerology_full(
            phone_number=request.phone_number,
            convention=request.system_convention,
            include_country_code=request.include_country_code,
            birth_date=request.birth_date,
            industry_category=request.industry_category,
            candidate_numbers=request.candidate_numbers,
            language=request.language,
            max_candidates=request.max_candidates,
        )

        def build_phone_detail(d: Dict[str, Any]) -> PhoneAnalysisDetail:
            return PhoneAnalysisDetail(
                digits=d["digits"],
                digit_count=d["digit_count"],
                compound_sum=d["compound_sum"],
                root_number=d["root_number"],
                single_root=d["single_root"],
                is_master=d["is_master"],
                reduction_steps=d["reduction_steps"],
                frequencies=d["frequencies"],
                dominant_digits=d["dominant_digits"],
                missing_digits=d["missing_digits"],
                zero_count=d["zero_count"],
                ruling_planet=d["ruling_planet"],
                keyword=d["keyword"],
                vibrational_meaning=d["vibrational_meaning"],
                patterns=d["patterns"],
            )

        def build_cand_phone(c: Dict[str, Any]) -> PhoneCandidateResult:
            return PhoneCandidateResult(
                raw_input=c["raw_input"],
                masked_phone=c["masked_phone"],
                national_number=c["national_number"],
                formatted_national=c["formatted_national"],
                display_international=c["display_international"],
                country_name=c.get("country_name"),
                country_code=c.get("country_code"),
                compound_sum=c["compound_sum"],
                root_number=c["root_number"],
                single_root=c["single_root"],
                is_master=c["is_master"],
                reduction_steps=c["reduction_steps"],
                frequencies=c["frequencies"],
                dominant_digits=c["dominant_digits"],
                missing_digits=c["missing_digits"],
                zero_count=c["zero_count"],
                ruling_planet=c["ruling_planet"],
                keyword=c["keyword"],
                vibrational_meaning=c["vibrational_meaning"],
                patterns=c["patterns"],
                personal_compatibility=c.get("personal_compatibility"),
                industry_compatibility=c.get("industry_compatibility"),
                personal_score=c.get("personal_score"),
                industry_score=c.get("industry_score"),
                vanity_score=c["vanity_score"],
                composite_score=c["composite_score"],
                is_favorable=c["is_favorable"],
            )

        return PhoneNumerologyResponse(
            raw_input=res["raw_input"],
            masked_phone=res["masked_phone"],
            national_number=res["national_number"],
            formatted_national=res["formatted_national"],
            all_digits=res["all_digits"],
            display_international=res["display_international"],
            detected_country_code=res["detected_country_code"],
            detected_country_name=res["detected_country_name"],
            is_indian_mobile=res["is_indian_mobile"],
            system_convention=res["system_convention"],
            include_country_code=res["include_country_code"],
            engine_version=ENGINE_VERSION,
            primary_analysis=build_phone_detail(res["primary_analysis"]),
            national_analysis=build_phone_detail(res["national_analysis"]),
            international_analysis=build_phone_detail(res["international_analysis"]),
            missing_digits_analysis=res["missing_digits_analysis"],
            zero_significance=res["zero_significance"],
            personal_compatibility=res["personal_compatibility"],
            industry_compatibility=res["industry_compatibility"],
            candidates=[build_cand_phone(c) for c in res["candidates"]],
            scoring_explanation=res["scoring_explanation"],
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phone Numerology error: {str(exc)}",
        )


@router.post("/vehicle/analyze", response_model=VehicleNumerologyResponse)
def compute_vehicle_numerology(request: VehicleNumerologyRequest) -> VehicleNumerologyResponse:
    """Analyze motor vehicle registration plate numbers, RTO components, usage harmony, and owner resonance."""
    try:
        co_owners_data = [co.model_dump() for co in request.co_owners] if request.co_owners else []
        res = analyze_vehicle_numerology_full(
            registration_number=request.registration_number,
            convention=request.system_convention,
            calculation_mode=request.calculation_mode,
            vehicle_usage=request.vehicle_usage,
            primary_birth_date=request.primary_birth_date,
            primary_owner_name=request.primary_owner_name,
            co_owners=co_owners_data,
            candidate_numbers=request.candidate_numbers,
            language=request.language,
            max_candidates=request.max_candidates,
        )

        def build_veh_detail(d: Dict[str, Any]) -> VehicleAnalysisDetail:
            return VehicleAnalysisDetail(
                calculation_mode=d["calculation_mode"],
                mode_label=d["mode_label"],
                source_string=d["source_string"],
                character_mappings=d["character_mappings"],
                compound_sum=d["compound_sum"],
                root_number=d["root_number"],
                single_root=d["single_root"],
                is_master=d["is_master"],
                reduction_steps=d["reduction_steps"],
                ruling_planet=d["ruling_planet"],
                keyword=d["keyword"],
                vibrational_meaning=d["vibrational_meaning"],
            )

        def build_cand_veh(c: Dict[str, Any]) -> VehicleCandidateResult:
            return VehicleCandidateResult(
                raw_input=c["raw_input"],
                normalized_registration=c["normalized_registration"],
                plate_classification=c["plate_classification"],
                state_code=c.get("state_code"),
                state_name=c.get("state_name"),
                rto_code=c.get("rto_code"),
                series_letters=c.get("series_letters"),
                numeric_digits=c["numeric_digits"],
                calculation_mode=c["calculation_mode"],
                compound_sum=c["compound_sum"],
                root_number=c["root_number"],
                single_root=c["single_root"],
                is_master=c["is_master"],
                reduction_steps=c["reduction_steps"],
                patterns=c["patterns"],
                vanity_score=c["vanity_score"],
                usage_score=c.get("usage_score"),
                owner_score=c.get("owner_score"),
                composite_score=c["composite_score"],
                is_favorable=c["is_favorable"],
            )

        def build_driver_eval(o: Dict[str, Any]) -> VehicleOwnerEvaluation:
            return VehicleOwnerEvaluation(
                name=o["name"],
                birth_date=o["birth_date"],
                role=o["role"],
                is_primary=o["is_primary"],
                psychic_number=o["psychic_number"],
                life_path_number=o["life_path_number"],
                psychic_harmony_score=o["psychic_harmony_score"],
                life_path_harmony_score=o["life_path_harmony_score"],
                personal_score=o["personal_score"],
                level=o["level"],
                synthesis=o["synthesis"],
            )

        return VehicleNumerologyResponse(
            raw_input=res["raw_input"],
            normalized_registration=res["normalized_registration"],
            formatted_registration=res["formatted_registration"],
            state_code=res.get("state_code"),
            state_name=res.get("state_name"),
            rto_code=res.get("rto_code"),
            series_letters=res.get("series_letters"),
            numeric_digits=res["numeric_digits"],
            is_valid_indian_format=res["is_valid_indian_format"],
            plate_classification=res["plate_classification"],
            system_convention=res["system_convention"],
            calculation_mode=res["calculation_mode"],
            vehicle_usage=res["vehicle_usage"],
            engine_version=ENGINE_VERSION,
            primary_analysis=build_veh_detail(res["primary_analysis"]),
            digits_only_analysis=build_veh_detail(res["digits_only_analysis"]),
            numeric_all_analysis=build_veh_detail(res["numeric_all_analysis"]),
            full_alphanumeric_analysis=build_veh_detail(res["full_alphanumeric_analysis"]),
            patterns=res["patterns"],
            vanity_score=res["vanity_score"],
            usage_alignment=res["usage_alignment"],
            owner_alignments=[build_driver_eval(o) for o in res["owner_alignments"]],
            overall_owner_score=res.get("overall_owner_score"),
            candidates=[build_cand_veh(c) for c in res["candidates"]],
            scoring_explanation=res["scoring_explanation"],
            disclaimer=res["disclaimer"],
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vehicle Numerology error: {str(exc)}",
        )


@router.post("/property/analyze", response_model=PropertyNumerologyResponse)
def compute_property_numerology(request: PropertyNumerologyRequest) -> PropertyNumerologyResponse:
    """Analyze real estate property numbers (door, building, floor, plot, combined), usage harmony, and resident resonance."""
    try:
        co_residents_data = [cr.model_dump() for cr in request.co_residents] if request.co_residents else []
        candidates_data = [cp.model_dump() for cp in request.candidate_properties] if request.candidate_properties else []

        res = analyze_property_numerology_full(
            property_category=request.property_category,
            tenure_type=request.tenure_type,
            door_flat_number=request.door_flat_number,
            building_number=request.building_number,
            block_or_wing=request.block_or_wing,
            floor_number=request.floor_number,
            plot_number=request.plot_number,
            building_name=request.building_name,
            facing_direction=request.facing_direction,
            property_usage=request.property_usage,
            convention=request.system_convention,
            calculation_mode=request.calculation_mode,
            primary_birth_date=request.primary_birth_date,
            primary_owner_name=request.primary_owner_name,
            co_residents=co_residents_data,
            candidate_properties=candidates_data,
            language=request.language,
            max_candidates=request.max_candidates,
        )

        def build_prop_comp(d: Dict[str, Any]) -> PropertyComponentDetail:
            return PropertyComponentDetail(
                component_name=d["component_name"],
                component_label=d["component_label"],
                calculation_mode=d.get("calculation_mode", d["component_name"]),
                source_string=d["source_string"],
                included_characters=d["included_characters"],
                character_mappings=d["character_mappings"],
                compound_sum=d["compound_sum"],
                root_number=d["root_number"],
                single_root=d["single_root"],
                is_master=d["is_master"],
                reduction_steps=d["reduction_steps"],
                ruling_planet=d["ruling_planet"],
                keyword=d["keyword"],
                vibrational_meaning=d["vibrational_meaning"],
                formula_explanation=d.get("formula_explanation"),
            )

        def build_cand_prop(c: Dict[str, Any]) -> PropertyCandidateResult:
            return PropertyCandidateResult(
                label=c["label"],
                door_flat_number=c.get("door_flat_number"),
                building_number=c.get("building_number"),
                floor_number=c.get("floor_number"),
                plot_number=c.get("plot_number"),
                building_name=c.get("building_name"),
                calculation_mode=c["calculation_mode"],
                compound_sum=c["compound_sum"],
                root_number=c["root_number"],
                single_root=c["single_root"],
                is_master=c["is_master"],
                reduction_steps=c["reduction_steps"],
                ruling_planet=c["ruling_planet"],
                keyword=c["keyword"],
                usage_score=c["usage_score"],
                owner_score=c.get("owner_score"),
                composite_score=c["composite_score"],
                is_favorable=c["is_favorable"],
            )

        def build_res_eval(r: Dict[str, Any]) -> PropertyResidentEvaluation:
            return PropertyResidentEvaluation(
                name=r["name"],
                birth_date=r["birth_date"],
                role=r["role"],
                is_primary=r["is_primary"],
                psychic_number=r["psychic_number"],
                life_path_number=r["life_path_number"],
                psychic_harmony_score=r["psychic_harmony_score"],
                life_path_harmony_score=r["life_path_harmony_score"],
                personal_score=r["personal_score"],
                level=r["level"],
                synthesis=r["synthesis"],
            )

        return PropertyNumerologyResponse(
            property_category=res["property_category"],
            tenure_type=res["tenure_type"],
            door_flat_number=res["door_flat_number"],
            building_number=res["building_number"],
            block_or_wing=res["block_or_wing"],
            floor_number=res["floor_number"],
            plot_number=res["plot_number"],
            building_name=res["building_name"],
            facing_direction=res.get("facing_direction"),
            full_identifier=res["full_identifier"],
            system_convention=res["system_convention"],
            calculation_mode=res["calculation_mode"],
            property_usage=res["property_usage"],
            primary_analysis=build_prop_comp(res["primary_analysis"]),
            door_analysis=build_prop_comp(res["door_analysis"]),
            building_analysis=build_prop_comp(res["building_analysis"]),
            floor_analysis=build_prop_comp(res["floor_analysis"]),
            plot_analysis=build_prop_comp(res["plot_analysis"]),
            combined_analysis=build_prop_comp(res["combined_analysis"]),
            full_alphanumeric_analysis=build_prop_comp(res["full_alphanumeric_analysis"]),
            usage_alignment=res["usage_alignment"],
            vastu_alignment=res.get("vastu_alignment"),
            resident_alignments=[build_res_eval(r) for r in res["resident_alignments"]],
            overall_household_score=res.get("overall_household_score"),
            candidates=[build_cand_prop(c) for c in res["candidates"]],
            scoring_explanation=res["scoring_explanation"],
            disclaimer=res["disclaimer"],
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Property Numerology error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 2F. Marriage Compatibility by Numerology Studio
# ------------------------------------------------------------------------------

@router.post("/marriage/analyze", response_model=MarriageNumerologyResponse)
def compute_marriage_compatibility(request: MarriageNumerologyRequest) -> MarriageNumerologyResponse:
    """Analyze couple numerology compatibility across Birth/Psychic, Life Path, Expression,
    Soul Urge, and Personality numbers with relationship themes and practical discussion prompts.
    """
    try:
        res = analyze_marriage_numerology_full(
            person_a_input=request.person_a.model_dump(),
            person_b_input=request.person_b.model_dump(),
            convention=request.system_convention,
            language=request.language,
        )

        def build_person_profile(p: Dict[str, Any]) -> MarriagePersonProfile:
            return MarriagePersonProfile(
                person_label=p["person_label"],
                full_name=p["full_name"],
                preferred_name=p["preferred_name"],
                surname_initials=p["surname_initials"],
                birth_date=p["birth_date"],
                birth_psychic_number=p["birth_psychic_number"],
                birth_psychic_compound=p["birth_psychic_compound"],
                birth_psychic_planet=p["birth_psychic_planet"],
                birth_psychic_archetype=p["birth_psychic_archetype"],
                birth_psychic_reduction_steps=p["birth_psychic_reduction_steps"],
                life_path_number=p["life_path_number"],
                life_path_compound=p["life_path_compound"],
                life_path_planet=p["life_path_planet"],
                life_path_archetype=p["life_path_archetype"],
                life_path_reduction_steps=p["life_path_reduction_steps"],
                is_life_path_master=p["is_life_path_master"],
                expression_number=p["expression_number"],
                expression_compound=p["expression_compound"],
                expression_planet=p["expression_planet"],
                expression_reduction_steps=p["expression_reduction_steps"],
                is_expression_master=p["is_expression_master"],
                soul_urge_number=p["soul_urge_number"],
                soul_urge_compound=p["soul_urge_compound"],
                personality_number=p["personality_number"],
                personality_compound=p["personality_compound"],
                master_numbers=p["master_numbers"],
                karmic_debts=p["karmic_debts"],
                key_attributes=p["key_attributes"],
            )

        def build_comp_item(c: Optional[Dict[str, Any]]) -> Optional[MarriageComponentComparison]:
            if not c:
                return None
            return MarriageComponentComparison(
                component_name=c["component_name"],
                person_a_number=c["person_a_number"],
                person_b_number=c["person_b_number"],
                person_a_label=c["person_a_label"],
                person_b_label=c["person_b_label"],
                score=c["score"],
                weight=c["weight"],
                harmony_level=c["harmony_level"],
                planetary_dynamic=c["planetary_dynamic"],
                interpretation=c["interpretation"],
            )

        return MarriageNumerologyResponse(
            system_convention=res["system_convention"],
            engine_version=res["engine_version"],
            relationship_status=res["relationship_status"],
            person_a_profile=build_person_profile(res["person_a_profile"]),
            person_b_profile=build_person_profile(res["person_b_profile"]),
            psychic_compatibility=build_comp_item(res["psychic_compatibility"]),
            life_path_compatibility=build_comp_item(res["life_path_compatibility"]),
            expression_compatibility=build_comp_item(res["expression_compatibility"]),
            soul_urge_compatibility=build_comp_item(res["soul_urge_compatibility"]),
            personality_compatibility=build_comp_item(res["personality_compatibility"]),
            emotional_themes=res["emotional_themes"],
            communication_themes=res["communication_themes"],
            shared_strengths=res["shared_strengths"],
            potential_challenges=res["potential_challenges"],
            conversation_prompts=res["conversation_prompts"],
            growth_recommendations=res["growth_recommendations"],
            overall_score=res["overall_score"],
            overall_harmony_level=res["overall_harmony_level"],
            overall_synthesis=res["overall_synthesis"],
            scoring_formula_explanation=res["scoring_formula_explanation"],
            disclaimer=res["disclaimer"],
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Marriage Numerology error: {str(exc)}",
        )


@router.post("/family/analyze", response_model=FamilyNumerologyResponse)
def compute_family_numerology(request: FamilyNumerologyRequest) -> FamilyNumerologyResponse:
    """Analyze multi-generational family group, parent-child compatibility, and baby name numerology."""
    try:
        members_data = [m.model_dump() for m in request.members]
        res = analyze_family_numerology_full(
            family_name=request.family_name or "Family",
            members=members_data,
            candidate_names=request.candidate_names,
            baby_dob=request.baby_dob,
            surname=request.surname,
            target_root=request.target_root,
            system_convention=request.system_convention,
            generate_suggestions=request.generate_suggestions,
            language=request.language,
        )

        return FamilyNumerologyResponse(
            family_name=res["family_name"],
            system_convention=res["system_convention"],
            language=res["language"],
            members_evaluated=[
                FamilyMemberEvaluation(
                    id=m["id"],
                    name=m["name"],
                    role=m["role"],
                    birth_date=m["birth_date"],
                    birth_psychic_number=m["birth_psychic_number"],
                    birth_psychic_planet=m["birth_psychic_planet"],
                    life_path_number=m["life_path_number"],
                    life_path_planet=m["life_path_planet"],
                    is_life_path_master=m["is_life_path_master"],
                    expression_number=m["expression_number"],
                    compound_expression=m["compound_expression"],
                    soul_urge_number=m["soul_urge_number"],
                    personality_number=m["personality_number"],
                    karmic_debts=m["karmic_debts"],
                    archetype=m["archetype"],
                    element=m["element"],
                    reduction_steps=m["reduction_steps"],
                    short_summary=m["short_summary"],
                )
                for m in res["members_evaluated"]
            ],
            pairwise_comparisons=[
                FamilyPairwiseComparison(
                    person_a_id=p["person_a_id"],
                    person_a_name=p["person_a_name"],
                    person_a_role=p["person_a_role"],
                    person_b_id=p["person_b_id"],
                    person_b_name=p["person_b_name"],
                    person_b_role=p["person_b_role"],
                    relationship_type=p["relationship_type"],
                    psychic_harmony_score=p["psychic_harmony_score"],
                    life_path_harmony_score=p["life_path_harmony_score"],
                    expression_harmony_score=p["expression_harmony_score"],
                    composite_harmony_score=p["composite_harmony_score"],
                    harmony_level=p["harmony_level"],
                    planetary_dynamic=p["planetary_dynamic"],
                    shared_strengths=p["shared_strengths"],
                    growth_edges=p["growth_edges"],
                    nurturing_prompt=p["nurturing_prompt"],
                )
                for p in res["pairwise_comparisons"]
            ],
            number_distribution=[
                FamilyDistributionItem(
                    number=d["number"],
                    count=d["count"],
                    percentage=d["percentage"],
                    ruling_planet=d["ruling_planet"],
                    element=d["element"],
                    members_with_number=d["members_with_number"],
                )
                for d in res["number_distribution"]
            ],
            dominant_vibrations=res["dominant_vibrations"],
            missing_vibrations=res["missing_vibrations"],
            elemental_balance=res["elemental_balance"],
            baby_name_candidates=[
                BabyNameCandidateResult(
                    name=c["name"],
                    is_generated=c["is_generated"],
                    variation_type=c["variation_type"],
                    pythagorean_expression=c["pythagorean_expression"],
                    pythagorean_compound=c["pythagorean_compound"],
                    chaldean_expression=c["chaldean_expression"],
                    chaldean_compound=c["chaldean_compound"],
                    active_expression=c["active_expression"],
                    active_compound=c["active_compound"],
                    soul_urge=c["soul_urge"],
                    personality=c["personality"],
                    ruling_planet=c["ruling_planet"],
                    archetype=c["archetype"],
                    dob_harmony_score=c["dob_harmony_score"],
                    parent_harmony_score=c["parent_harmony_score"],
                    pronunciation_score=c["pronunciation_score"],
                    simplicity_score=c["simplicity_score"],
                    composite_score=c["composite_score"],
                    is_master=c["is_master"],
                    reduction_steps=c["reduction_steps"],
                    letter_mappings=[
                        LetterMapping(
                            char=lm["char"],
                            value=lm["value"],
                            is_vowel=lm["is_vowel"],
                            word=lm.get("word", ""),
                        )
                        for lm in c["letter_mappings"]
                    ],
                    vibrational_synthesis=c["vibrational_synthesis"],
                )
                for c in res["baby_name_candidates"]
            ],
            overall_family_harmony_score=res["overall_family_harmony_score"],
            overall_family_harmony_level=res["overall_family_harmony_level"],
            scoring_formula_explanation=res["scoring_formula_explanation"],
            family_strengths=res["family_strengths"],
            family_challenges=res["family_challenges"],
            reflection_questions=res["reflection_questions"],
            overall_synthesis=res["overall_synthesis"],
            engine_version=res["engine_version"],
            disclaimer=res["disclaimer"],
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Family Numerology Studio error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 3. Destiny Matrix
# ------------------------------------------------------------------------------

@router.post("/destiny-matrix", response_model=DestinyMatrixResponse)
def compute_destiny_matrix(request: DestinyMatrixRequest) -> DestinyMatrixResponse:
    """Calculate 22-Arcana Destiny Matrix octagram, karmic tail, purpose, and age timeline."""
    try:
        matrix = calculate_destiny_matrix(request.birth_date, lang=request.language)

        compatibility = None
        if request.partner_birth_date:
            compatibility = calculate_compatibility(
                request.birth_date,
                request.partner_birth_date,
                name1=request.person_name or "Partner 1",
                name2=request.partner_name or "Partner 2",
                lang=request.language,
            )

        return DestinyMatrixResponse(
            birth_date=request.birth_date,
            person_name=request.person_name,
            engine_version=ENGINE_VERSION,
            day_arcana=matrix["day_arcana"],
            month_arcana=matrix["month_arcana"],
            year_arcana=matrix["year_arcana"],
            karmic_tail_base=matrix["karmic_tail_base"],
            karmic_tail_triad=matrix["karmic_tail_triad"],
            comfort_zone=matrix["comfort_zone"],
            father_spirit=matrix["father_spirit"],
            mother_spirit=matrix["mother_spirit"],
            father_matter=matrix["father_matter"],
            mother_matter=matrix["mother_matter"],
            love_line=matrix["love_line"],
            money_line=matrix["money_line"],
            purpose=matrix["purpose"],
            age_timeline=matrix["age_timeline"],
            compatibility=compatibility,
            strengths=matrix["strengths"],
            challenges=matrix["challenges"],
            career_tendencies=matrix["career_tendencies"],
            financial_tendencies=matrix["financial_tendencies"],
            love_themes=matrix["love_themes"],
            overall_synthesis=matrix["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Destiny Matrix calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 3. Advanced Analysis (Lo Shu, Pinnacles, Yuan Integration)
# ------------------------------------------------------------------------------

@router.post("/advanced", response_model=AdvancedAnalysisResponse)
def compute_advanced_analysis(request: AdvancedAnalysisRequest) -> AdvancedAnalysisResponse:
    """Execute Advanced Analysis: Lo Shu 3x3 Magic Square, Arrows of Pythagoras, Pinnacles & Challenges."""
    try:
        res = calculate_advanced_analysis(request.full_name, request.birth_date, lang=request.language)
        return AdvancedAnalysisResponse(
            full_name=request.full_name.strip(),
            birth_date=request.birth_date,
            engine_version=ENGINE_VERSION,
            unicode_derived_name_number=res["unicode_derived_name_number"],
            lo_shu=res["lo_shu"],
            pinnacles_challenges=res["pinnacles_challenges"],
            karmic_debts=res["karmic_debts"],
            karmic_lessons=res["karmic_lessons"],
            dominant_vibrations=res["dominant_vibrations"],
            strengths=res["strengths"],
            challenges=res["challenges"],
            career_tendencies=res["career_tendencies"],
            financial_tendencies=res["financial_tendencies"],
            love_themes=res["love_themes"],
            overall_synthesis=res["overall_synthesis"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced Analysis calculation error: {str(exc)}",
        )


# ------------------------------------------------------------------------------
# 4. Engine Metadata & Diagnostics
# ------------------------------------------------------------------------------

@router.get("/metadata", response_model=NumerologyMetadataResponse)
def get_numerology_metadata() -> NumerologyMetadataResponse:
    """Return calculation engine versions, available conventions, and operational status."""
    return NumerologyMetadataResponse(
        service="Gokul's Astrological Insights - Numerology Engine",
        engine_version=ENGINE_VERSION,
        methods=[
            {
                "id": "traditional",
                "name": "Traditional Numerology",
                "description": "Calculates Life Path, Expression, Soul Urge, Personality, Attitude, and Maturity numbers with Master Number (11, 22, 33) preservation.",
            },
            {
                "id": "destiny_matrix",
                "name": "Destiny Matrix (22 Arcana)",
                "description": "22 Major Arcana reduction octagram mapping, ancestral lines, karmic tail, love/money entrance, age cycles (0-80), and couples compatibility.",
            },
            {
                "id": "advanced",
                "name": "Advanced Analysis & Yuan Integration",
                "description": "Yuan-compatible Unicode code-point name reduction, 3x3 Lo Shu magic square, 8 arrows of Pythagoras, 4 Life Pinnacles, and 4 Life Challenges.",
            },
            {
                "id": "name_correction",
                "name": "Name Suggestion & Correction Studio",
                "description": "Deterministic candidate spelling generator, vowel/consonant tuning, Tamil transliteration, and multi-dimensional vibration scoring.",
            },
            {
                "id": "business",
                "name": "Business & Brand Numerology Studio",
                "description": "Corporate normalization (legal vs brand), multi-founder partnership alignment, industry sector harmony, and commercial brand ranking.",
            },
            {
                "id": "phone",
                "name": "Phone & Mobile Number Numerology Studio",
                "description": "Deterministic subscriber digits vs country code analysis, digit frequency, missing vibrations, rhythm/vanity patterns, and personal/business profile alignment.",
            },
            {
                "id": "vehicle",
                "name": "Vehicle & Asset Registration Numerology Studio",
                "description": "Registration plate parsing (State/RTO/Series/Digits), digits-only vs full alphanumeric conventions, vehicle usage archetypes, and multi-driver compatibility.",
            },
            {
                "id": "property",
                "name": "House, Flat & Property Numerology Studio",
                "description": "Door, building, floor, plot, and combined property calculations, Vastu Shastra directional alignment, and resident family compatibility.",
            },
            {
                "id": "marriage",
                "name": "Marriage Compatibility by Numerology Studio",
                "description": "Couple numerology compatibility evaluating Birth/Psychic, Life Path, Expression, and Soul Urge dynamics, emotional resonance, shared strengths, and practical dialogue prompts.",
            },
            {
                "id": "family",
                "name": "Family & Baby Numerology Studio",
                "description": "Multi-generational family vibration grid, baby name suggestions with Pythagorean/Chaldean scoring, and parent-child nurturing compatibility dynamics.",
            },
        ],
        conventions=[
            {"id": "pythagorean", "name": "Pythagorean (Western Standard 1-9)", "default": True},
            {"id": "chaldean", "name": "Chaldean (Ancient Esoteric 1-8)", "default": False},
        ],
        supported_languages=["en", "ta"],
        disclaimer=(
            "Numerological calculations and interpretations are for self-reflection, personal exploration, "
            "and philosophical enrichment. They are not deterministic scientific predictions or guaranteed outcomes."
        ),
    )


# ------------------------------------------------------------------------------
# 5. Saved Reports Persistence Endpoints
# ------------------------------------------------------------------------------

@router.post("/reports", response_model=SavedNumerologyReportResponse)
def create_report(
    payload: SaveNumerologyReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SavedNumerologyReportResponse:
    """Persist generated report to Supabase with transactional advisory-lock sequential display numbering."""
    try:
        report = save_numerology_report(current_user["id"], payload)
        return SavedNumerologyReportResponse(
            id=str(report["id"]),
            user_id=str(report["user_id"]),
            display_number=report["display_number"],
            person_name=report["person_name"],
            birth_date=str(report["birth_date"]),
            method=report["method"],
            system_convention=report["system_convention"],
            calculation_data=report["calculation_data"],
            interpretation_data=report["interpretation_data"],
            engine_version=report["engine_version"],
            created_at=str(report["created_at"]),
            updated_at=str(report["updated_at"]),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist numerology report: {str(exc)}",
        )


@router.get("/reports")
def list_reports(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve saved numerology reports for the authenticated user, or all for admins."""
    is_admin = current_user.get("role") == "admin"
    reports = list_numerology_reports(current_user["id"], is_admin=is_admin, limit=limit, offset=offset)
    return {"reports": reports, "count": len(reports)}


@router.get("/reports/{report_id}")
def get_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve specific saved report, enforcing user ownership or admin privilege."""
    is_admin = current_user.get("role") == "admin"
    report = get_numerology_report(current_user["id"], report_id, is_admin=is_admin)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Numerology report not found or unauthorized.",
        )
    return report


@router.delete("/reports/{report_id}")
def delete_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a saved report, enforcing user ownership or admin privilege."""
    is_admin = current_user.get("role") == "admin"
    success = delete_numerology_report(current_user["id"], report_id, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or delete unauthorized.",
        )
    return {"success": True, "message": "Numerology report removed successfully."}


# ------------------------------------------------------------------------------
# 6. PDF Report Generation Endpoints
# ------------------------------------------------------------------------------

@router.get("/reports/{report_id}/pdf")
def export_saved_report_pdf(
    report_id: str,
    lang: str = Query("en", pattern="^(en|ta)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Response:
    """Generate and download a branded, multi-page PDF for a saved numerology report."""
    is_admin = current_user.get("role") == "admin"
    report = get_numerology_report(current_user["id"], report_id, is_admin=is_admin)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Numerology report not found or unauthorized.",
        )

    try:
        pdf_bytes = generate_numerology_pdf_bytes(
            person_name=report["person_name"],
            birth_date=str(report["birth_date"]),
            method=report["method"],
            system_convention=report["system_convention"],
            calculation_data=report["calculation_data"],
            interpretation_data=report["interpretation_data"],
            language=lang,
            display_number=report.get("display_number"),
            report_id=str(report.get("id")),
            engine_version=report.get("engine_version", ENGINE_VERSION),
        )

        safe_name = "".join(c if c.isalnum() else "_" for c in report["person_name"]).strip("_") or "Report"
        disp_num = report.get("display_number", "001")
        filename = f"Numerology_Report_{disp_num}_{safe_name}_{lang}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile numerology PDF report: {str(exc)}",
        )


@router.post("/export-pdf")
def export_ad_hoc_numerology_pdf(
    payload: ExportNumerologyPdfRequest,
) -> Response:
    """Generate and stream a branded PDF directly from live studio calculation payload."""
    try:
        pdf_bytes = generate_numerology_pdf_bytes(
            person_name=payload.person_name,
            birth_date=payload.birth_date,
            method=payload.method,
            system_convention=payload.system_convention,
            calculation_data=payload.calculation_data,
            interpretation_data=payload.interpretation_data,
            language=payload.language,
            display_number=payload.display_number,
            report_id=payload.report_id,
            engine_version=ENGINE_VERSION,
        )

        safe_name = "".join(c if c.isalnum() else "_" for c in payload.person_name).strip("_") or "Subject"
        filename = f"Numerology_{payload.method.title()}_{safe_name}_{payload.language}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ad-hoc numerology PDF: {str(exc)}",
        )
