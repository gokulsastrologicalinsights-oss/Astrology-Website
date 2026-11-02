"""Consolidated Kakshya Chart and Vimshottari 8-Part Career Timing Engine.

Based on empirical research papers:
1. Dr. R.K. Aggarwal: 'Predicting through Ashtakavarga and Kakshya' (pp. 176-192)
   - Table III: Consolidated Kakshya Chart summing all 7 planets' Prastara contributions
     across the 8 kakshyas for each sign.
   - Rule: Kakshyas with >= 4 bindus yield auspicious, productive transit results;
     Kakshyas with < 4 bindus yield obstacles, delays, and drain.
2. P.C. Verma: 'Timing Events: An Easy Method' (pp. 194-206)
   - Vimshottari Mahadasha 8-Part Division based on the 8 Kakshya lords.
   - Correlation with the 10th lord's Prastarashtakavarga at its natal placement sign.
   - Presence of 1 bindu (+) marks professional advancement; 0 (rekha) marks professional friction.
"""

from typing import Dict, List, Optional, Any, Tuple
from app.services.kn_rao_engine.models import (
    ConsolidatedKakshyaResponse,
    ConsolidatedSignKakshya,
    KakshyaSegmentItem,
    VimshottariEightPartItem,
)
from app.services.kn_rao_engine.career_evaluator import (
    SIGN_LORDS,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)
from app.services.ashtakavarga_engine.prastara import (
    KAKSHA_CONTRIBUTOR_ORDER,
    compute_all_prastara_matrices,
)
from app.services.ashtakavarga_engine.kaksha import KAKSHA_RANGES, get_kaksha_division_for_degree
from app.services.ashtakavarga_engine.tables import PLANETS_7

# Standard Vimshottari Dasha durations in years
DASHA_YEARS: Dict[str, float] = {
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
    "Ketu": 7.0,
    "Venus": 20.0,
}


def build_consolidated_kakshya_matrix(
    planets_data: Dict[str, Dict[str, Any]],
    lagna_sign: int
) -> List[ConsolidatedSignKakshya]:
    """Build Dr. R.K. Aggarwal's Table III: Consolidated Kakshya Chart (12 signs x 8 kakshyas).
    
    Sums bindus from all 7 planets' Prastarashtakavarga tables.
    """
    contributor_signs: Dict[str, int] = {
        p: planets_data.get(p, {}).get("sign_index", 1)
        for p in PLANETS_7
    }
    contributor_signs["Lagna"] = lagna_sign
    
    prastara_dict = compute_all_prastara_matrices(contributor_signs)
    
    consolidated_matrix: List[ConsolidatedSignKakshya] = []
    
    for sign_idx in range(1, 13):
        sign_name = SIGN_NAMES_EN[sign_idx]
        sign_ta = SIGN_NAMES_TA[sign_idx]
        
        kakshya_items: List[KakshyaSegmentItem] = []
        sign_sav_total = 0
        
        for k_idx, k_lord in enumerate(KAKSHA_CONTRIBUTOR_ORDER, start=1):
            deg_range = KAKSHA_RANGES[k_idx - 1]
            
            # Sum bindus contributed by all 7 planets for this (sign_idx, k_lord)
            total_bindus_in_kakshya = 0
            for planet in PLANETS_7:
                prastara = prastara_dict[planet]
                # find row for k_lord
                for row in prastara.rows:
                    if row.contributor == k_lord:
                        bindu = row.sign_bindus.get(sign_idx, 0)
                        total_bindus_in_kakshya += bindu
                        break
                        
            sign_sav_total += total_bindus_in_kakshya
            is_auspicious = total_bindus_in_kakshya >= 4
            
            kakshya_items.append(
                KakshyaSegmentItem(
                    kakshya_num=k_idx,
                    kakshya_lord=k_lord,
                    degree_range=deg_range,
                    total_bindus=total_bindus_in_kakshya,
                    auspicious=is_auspicious,
                )
            )
            
        consolidated_matrix.append(
            ConsolidatedSignKakshya(
                sign_index=sign_idx,
                sign_name=sign_name,
                sign_name_tamil=sign_ta,
                total_sav_bindus=sign_sav_total,
                kakshyas=kakshya_items,
            )
        )
        
    return consolidated_matrix


def evaluate_vimshottari_eight_parts(
    planets_data: Dict[str, Dict[str, Any]],
    lagna_sign: int,
    active_mahadasha_lord: Optional[str] = None
) -> Tuple[str, str, List[VimshottariEightPartItem]]:
    """Evaluate P.C. Verma's 8-Part division of Vimshottari Mahadasha correlated with 10th lord's Prastharaka.
    
    Returns:
    (tenth_lord_name, tenth_lord_rashi_name, eight_parts_breakdown)
    """
    # 1. Identify 10th house and 10th lord
    h10_sign = ((lagna_sign + 8) % 12) + 1
    tenth_lord = SIGN_LORDS[h10_sign]
    
    # Sign occupied by 10th lord
    tenth_lord_sign = planets_data.get(tenth_lord, {}).get("sign_index", h10_sign)
    tenth_lord_rashi_name = SIGN_NAMES_EN[tenth_lord_sign]
    
    contributor_signs: Dict[str, int] = {
        p: planets_data.get(p, {}).get("sign_index", 1)
        for p in PLANETS_7
    }
    contributor_signs["Lagna"] = lagna_sign
    prastara_dict = compute_all_prastara_matrices(contributor_signs)
    
    # If 10th lord is Rahu or Ketu, fallback to dispositor or Saturn/Mars
    effective_calc_planet = tenth_lord if tenth_lord in PLANETS_7 else "Saturn"
    prastara_10th = prastara_dict.get(effective_calc_planet)
    
    eight_parts: List[VimshottariEightPartItem] = []
    
    total_dasha_duration = DASHA_YEARS.get(active_mahadasha_lord, 10.0) if active_mahadasha_lord else 10.0
    part_duration = total_dasha_duration / 8.0
    
    for part_idx, k_lord in enumerate(KAKSHA_CONTRIBUTOR_ORDER, start=1):
        # Check bindu in 10th lord's Prastarashtakavarga at 10th lord's sign
        bindu = 0
        if prastara_10th:
            for row in prastara_10th.rows:
                if row.contributor == k_lord:
                    bindu = row.sign_bindus.get(tenth_lord_sign, 0)
                    break
                    
        favorable = (bindu == 1)
        start_yr = (part_idx - 1) * part_duration
        end_yr = part_idx * part_duration
        time_span_str = f"Yr {start_yr:.1f} – {end_yr:.1f}"
        
        if favorable:
            indication = (
                f"{time_span_str}: Ruled by {k_lord}. Bindu present (1). Favorable for career advancement, "
                f"promotions, recognition, and successful business initiatives."
            )
            indication_ta = (
                f"{time_span_str}: {k_lord} ஆதிக்கம். பிந்து உள்ளது (1). உத்தியோக உயர்வு, கெளரவம், "
                f"தொழில் முன்னேற்றத்திற்கு சாதகமானது."
            )
        else:
            indication = (
                f"{time_span_str}: Ruled by {k_lord}. Rekha / Zero bindu (0). Career challenges, increased "
                f"workload, unexpected transfers, delays, or administrative friction."
            )
            indication_ta = (
                f"{time_span_str}: {k_lord} ஆதிக்கம். பிந்து இல்லை (0). வேலையில் தடைகள், அதிக பணிச்சுமை, "
                f"இடமாற்றம் அல்லது நிர்வாக சிக்கல்கள் ஏற்பட வாய்ப்பு."
            )
            
        eight_parts.append(
            VimshottariEightPartItem(
                part_num=part_idx,
                kakshya_lord=k_lord,
                tenth_lord_prastharaka_bindu=bindu,
                favorable_for_career=favorable,
                career_indication=indication,
                career_indication_tamil=indication_ta,
            )
        )
        
    return tenth_lord, tenth_lord_rashi_name, eight_parts


def evaluate_consolidated_kakshya_and_timing(
    planets_data: Dict[str, Dict[str, Any]],
    lagna_sign: int = 1,
    active_mahadasha_lord: Optional[str] = None,
    transit_planets: Optional[Dict[str, Dict[str, Any]]] = None
) -> ConsolidatedKakshyaResponse:
    """Master evaluator combining Dr. R.K. Aggarwal's Table III and P.C. Verma's 8-Part timing."""
    matrix = build_consolidated_kakshya_matrix(planets_data, lagna_sign)
    
    tenth_lord, tenth_lord_rashi, eight_parts = evaluate_vimshottari_eight_parts(
        planets_data, lagna_sign, active_mahadasha_lord
    )
    
    # Evaluate transits if provided
    transit_evaluations: List[Dict[str, Any]] = []
    if transit_planets:
        for p, t_data in transit_planets.items():
            t_sign = t_data.get("sign_index", 1)
            t_deg = t_data.get("degree_in_sign", 0.0)
            kakshya_div = get_kaksha_division_for_degree(t_deg)
            k_num = kakshya_div.kaksha_number
            k_lord = kakshya_div.kaksha_lord
            
            # Lookup in matrix
            sign_item = matrix[t_sign - 1]
            k_item = sign_item.kakshyas[k_num - 1]
            
            transit_evaluations.append({
                "planet": p,
                "transit_sign": SIGN_NAMES_EN[t_sign],
                "degree": t_deg,
                "kakshya_num": k_num,
                "kakshya_lord": k_lord,
                "total_bindus": k_item.total_bindus,
                "is_auspicious": k_item.auspicious,
                "verdict": "Auspicious (Smooth)" if k_item.auspicious else "Inauspicious (Friction)",
                "verdict_tamil": "சுப பலன் (மகிழ்ச்சி)" if k_item.auspicious else "அசுப பலன் (தடைகள்)"
            })
            
    favorable_parts_count = sum(1 for part in eight_parts if part.favorable_for_career)
    
    summary_insight = (
        f"Consolidated Kakshya Chart synthesized across all 12 signs. Active Mahadasha ({active_mahadasha_lord or 'General'}) "
        f"is divided into 8 Kakshya sub-periods; {favorable_parts_count} out of 8 segments yield positive bindus in "
        f"10th lord ({tenth_lord}) Prastharashtakavarga in {tenth_lord_rashi}."
    )
    summary_insight_tamil = (
        f"12 ராசிகளின் ஒருங்கிணைந்த கக்ஷ்யா அட்டவணை கணக்கிடப்பட்டது. தசா நாதரின் காலம் 8 கக்ஷ்யா கூறுகளாக "
        f"பிரிக்கப்பட்டு, 10-ம் அதிபதியான {tenth_lord}-ன் பிரஸ்தார அட்டவணையில் 8-ல் {favorable_parts_count} கூறுகள் "
        f"சுப பிந்துக்களைக் கொண்டு தொழில் மேன்மையை உணர்த்துகின்றன."
    )

    return ConsolidatedKakshyaResponse(
        matrix=matrix,
        tenth_lord=tenth_lord,
        tenth_lord_rashi=tenth_lord_rashi,
        active_mahadasha_lord=active_mahadasha_lord,
        vimshottari_eight_parts=eight_parts,
        current_transits_evaluations=transit_evaluations,
        summary_insight=summary_insight,
        summary_insight_tamil=summary_insight_tamil,
    )
