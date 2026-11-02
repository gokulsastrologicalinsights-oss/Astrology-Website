"""K.N. Rao Advanced Astrological Research Engine.

Treatise: 'Advanced Techniques of Astrological Predictions'
(Vedic Astrology Series, B.P.E.S.V. Sansthan / Bharatiya Vidya Bhavan, New Delhi).
"""

from app.services.kn_rao_engine.models import (
    ServiceVsSelfEmploymentResult,
    TechnicalProfessionResult,
    AuthorJournalistResult,
    MaritalDiscordResult,
    ConsolidatedKakshyaResponse,
    ConsolidatedSignKakshya,
    KakshyaSegmentItem,
    VimshottariEightPartItem,
    MedicalTimingResult,
    MrityuBhagaPlanetItem,
    KnRaoAdvancedResearchResponse,
)
from app.services.kn_rao_engine.career_evaluator import (
    evaluate_service_vs_self_employment,
    evaluate_technical_profession,
    evaluate_author_journalist,
    calculate_jaimini_7_karakas,
    calculate_karakamsha_sign,
    get_jaimini_aspects_for_sign,
    get_parashari_aspects_for_planet,
)
from app.services.kn_rao_engine.marriage_evaluator import (
    evaluate_marital_discord,
    calculate_arudha_pada,
)
from app.services.kn_rao_engine.kakshya_timing import (
    build_consolidated_kakshya_matrix,
    evaluate_vimshottari_eight_parts,
    evaluate_consolidated_kakshya_and_timing,
)
from app.services.kn_rao_engine.medical_evaluator import (
    check_mrityu_bhaga,
    evaluate_medical_timing,
    MRITYU_BHAGA_TABLE,
)


def evaluate_kn_rao_advanced_research(
    planets_data: dict,
    d9_planets: dict,
    lagna_sign: int,
    lagna_degree: float = 15.0,
    active_mahadasha: str = None,
    active_antardasha: str = None,
    next_mahadasha: str = None,
    transit_planets: dict = None
) -> KnRaoAdvancedResearchResponse:
    """Run the complete suite of empirical research models from the K.N. Rao treatise."""
    # 1. Career Evaluator
    service_res = evaluate_service_vs_self_employment(planets_data, lagna_sign)
    tech_res = evaluate_technical_profession(planets_data, d9_planets, lagna_sign)
    author_res = evaluate_author_journalist(planets_data, d9_planets, lagna_sign)
    
    # 2. Marriage Evaluator
    marriage_res = evaluate_marital_discord(
        planets_data=planets_data,
        d9_planets=d9_planets,
        lagna_sign=lagna_sign,
        active_mahadasha=active_mahadasha,
        active_antardasha=active_antardasha
    )
    
    # 3. Medical Evaluator
    medical_res = evaluate_medical_timing(
        planets_data=planets_data,
        lagna_sign=lagna_sign,
        lagna_degree=lagna_degree,
        active_mahadasha=active_mahadasha,
        active_antardasha=active_antardasha,
        next_mahadasha=next_mahadasha
    )
    
    # 4. Jaimini Karakas & Arudhas
    karakas = calculate_jaimini_7_karakas(planets_data)
    _, karakamsha_str = calculate_karakamsha_sign(planets_data, d9_planets)
    _, al_str = calculate_arudha_pada(1, lagna_sign, planets_data)
    _, ul_str = calculate_arudha_pada(12, lagna_sign, planets_data)
    _, a7_str = calculate_arudha_pada(7, lagna_sign, planets_data)
    
    return KnRaoAdvancedResearchResponse(
        service_vs_self_employment=service_res,
        technical_profession=tech_res,
        author_vs_journalist=author_res,
        marital_discord=marriage_res,
        medical_timing=medical_res,
        jaimini_karakas=karakas,
        karakamsha_sign=karakamsha_str,
        arudha_lagna=al_str,
        upapada_lagna=ul_str,
        darapada=a7_str,
    )
