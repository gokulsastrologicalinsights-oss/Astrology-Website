"""Numerology calculation and persistence services package."""
from app.services.numerology.traditional import (
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
    reduce_number,
    reduce_number_steps,
    get_letter_info,
    PYTHAGOREAN_MAP,
    CHALDEAN_MAP,
)
from app.services.numerology.destiny_matrix import (
    calculate_destiny_matrix,
    calculate_compatibility,
    reduce_arcana,
)
from app.services.numerology.advanced import (
    calculate_advanced_analysis,
    derive_unicode_name_number,
    calculate_lo_shu_grid,
    calculate_pinnacles_and_challenges,
)
from app.services.numerology.report_repository import (
    save_numerology_report,
    list_numerology_reports,
    get_numerology_report,
    delete_numerology_report,
    ENGINE_VERSION,
)
from app.services.numerology.name_studio import (
    analyze_name_components,
    generate_candidate_spellings,
    generate_and_score_name_corrections,
    assess_number_harmony,
    calculate_pronunciation_preservation,
    calculate_spelling_simplicity,
    NUMEROLOGICAL_HARMONY,
)
from app.services.numerology.business_studio import (
    normalize_business_name,
    score_industry_harmony,
    evaluate_single_founder_harmony,
    evaluate_partnership_matrix,
    analyze_tagline,
    analyze_domain_or_handle,
    evaluate_business_brand_candidates,
    INDUSTRY_PROFILES,
    CORPORATE_SUFFIXES,
)
from app.services.numerology.phone_studio import (
    normalize_phone_number,
    mask_phone_number,
    calculate_single_phone_numerology,
    analyze_patterns_and_rhythm,
    evaluate_phone_dob_compatibility,
    evaluate_phone_industry_compatibility,
    evaluate_phone_candidates,
    analyze_phone_numerology_full,
    COMMON_COUNTRY_CODES,
    DIGIT_VIBRATION_MEANINGS,
    MISSING_DIGIT_LESSONS,
)
from app.services.numerology.vehicle_studio import (
    parse_vehicle_registration,
    calculate_vehicle_character_mapping,
    analyze_vehicle_mode,
    analyze_vehicle_patterns,
    evaluate_vehicle_usage_harmony,
    evaluate_single_driver_compatibility,
    evaluate_vehicle_candidates,
    analyze_vehicle_numerology_full,
    INDIAN_STATES_UTS,
    VEHICLE_VIBRATIONAL_ARCHETYPES,
    VEHICLE_USE_ARCHETYPES,
)
from app.services.numerology.property_studio import (
    calculate_property_character_mapping,
    analyze_property_component,
    calculate_combined_property_formula,
    evaluate_property_usage_harmony,
    evaluate_property_vastu_facing,
    evaluate_single_resident_compatibility,
    evaluate_property_candidates,
    analyze_property_numerology_full,
    VASTU_DIRECTIONS_MAP,
    PROPERTY_VIBRATIONAL_ARCHETYPES,
    PROPERTY_USE_ARCHETYPES,
)
from app.services.numerology.marriage_studio import (
    score_pair_compatibility,
    compute_single_person_profile,
    generate_relationship_themes,
    analyze_marriage_numerology_full,
    NUMBER_ARCHETYPES,
    PLANET_DYNAMIC_DESCRIPTIONS,
)
from app.services.numerology.pdf_generator import (
    NumerologyPdfGenerator,
    generate_numerology_pdf_bytes,
)
from app.services.numerology.family_studio import (
    compute_family_member_profile,
    evaluate_family_pair,
    evaluate_baby_name_candidates,
    analyze_family_numerology_full,
    ELEMENT_MAP,
    ROLE_TITLES,
)


