"""Medical Timing & Prognosis Engine.

Based on Dr. K.S. Charak's research: 'Timing of Disease and Recovery' (pp. 208-232):
- Mrityu Bhaga (MB) fatal degree detection for all planets and Ascendant.
- Trik house (6, 8, 12) and Maraka house (2, 7) dasha analysis.
- Vulnerability to disease onset under adverse dasha/antardasha.
- Retrograde benefics in Kendras failing to protect.
- Subsequent dasha evaluation to forecast recovery vs chronicity.
"""

from typing import Dict, List, Optional, Any, Tuple
from app.services.kn_rao_engine.models import (
    MedicalTimingResult,
    MrityuBhagaPlanetItem,
)
from app.services.kn_rao_engine.career_evaluator import (
    SIGN_LORDS,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    get_parashari_aspects_for_planet,
)

# Classical Mrityu Bhaga (MB) degrees across 12 zodiac signs (1=Aries to 12=Pisces)
# References: Sarwartha Chintamani, Jataka Parijata, Dr. K.S. Charak
MRITYU_BHAGA_TABLE: Dict[str, List[float]] = {
    "Sun": [20.0, 9.0, 12.0, 6.0, 8.0, 24.0, 16.0, 17.0, 22.0, 2.0, 3.0, 23.0],
    "Moon": [26.0, 12.0, 13.0, 25.0, 24.0, 11.0, 26.0, 14.0, 13.0, 25.0, 5.0, 12.0],
    "Mars": [19.0, 28.0, 25.0, 23.0, 29.0, 28.0, 14.0, 21.0, 2.0, 15.0, 11.0, 6.0],
    "Mercury": [15.0, 13.0, 25.0, 12.0, 8.0, 18.0, 20.0, 10.0, 21.0, 22.0, 7.0, 5.0],
    "Jupiter": [19.0, 29.0, 12.0, 27.0, 6.0, 4.0, 13.0, 10.0, 17.0, 11.0, 15.0, 28.0],
    "Venus": [28.0, 15.0, 11.0, 17.0, 10.0, 13.0, 4.0, 6.0, 27.0, 12.0, 29.0, 19.0],
    "Saturn": [10.0, 4.0, 7.0, 9.0, 12.0, 16.0, 3.0, 18.0, 28.0, 14.0, 13.0, 15.0],
    "Rahu": [14.0, 13.0, 12.0, 11.0, 24.0, 23.0, 24.0, 11.0, 12.0, 13.0, 14.0, 13.0],
    "Ketu": [8.0, 18.0, 20.0, 10.0, 21.0, 22.0, 23.0, 24.0, 11.0, 12.0, 13.0, 14.0],
    "Ascendant": [1.0, 9.0, 22.0, 22.0, 25.0, 2.0, 4.0, 23.0, 18.0, 20.0, 24.0, 10.0],
}

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


def check_mrityu_bhaga(
    planets_data: Dict[str, Dict[str, Any]],
    lagna_sign: int,
    lagna_degree: float = 15.0,
    tolerance_deg: float = 1.0
) -> List[MrityuBhagaPlanetItem]:
    """Check which planets (or Ascendant) reside within Mrityu Bhaga fatal degree (+/- tolerance)."""
    mb_results: List[MrityuBhagaPlanetItem] = []
    
    # 1. Check Ascendant
    asc_mb_deg = MRITYU_BHAGA_TABLE["Ascendant"][lagna_sign - 1]
    asc_diff = abs(lagna_degree - asc_mb_deg)
    if asc_diff <= tolerance_deg:
        mb_results.append(
            MrityuBhagaPlanetItem(
                planet="Ascendant",
                sign=SIGN_NAMES_EN[lagna_sign],
                degree_in_sign=round(lagna_degree, 2),
                mrityu_bhaga_degree=asc_mb_deg,
                difference_deg=round(asc_diff, 2),
                is_in_mrityu_bhaga=True,
            )
        )
        
    # 2. Check all planets
    for p, table in MRITYU_BHAGA_TABLE.items():
        if p == "Ascendant" or p not in planets_data:
            continue
            
        p_data = planets_data[p]
        p_sign = p_data.get("sign_index", 1)
        p_deg = p_data.get("degree_in_sign", 0.0)
        
        target_mb_deg = table[p_sign - 1]
        diff = abs(p_deg - target_mb_deg)
        
        if diff <= tolerance_deg:
            mb_results.append(
                MrityuBhagaPlanetItem(
                    planet=p,
                    sign=SIGN_NAMES_EN[p_sign],
                    degree_in_sign=round(p_deg, 2),
                    mrityu_bhaga_degree=target_mb_deg,
                    difference_deg=round(diff, 2),
                    is_in_mrityu_bhaga=True,
                )
            )
            
    return mb_results


def evaluate_medical_timing(
    planets_data: Dict[str, Dict[str, Any]],
    lagna_sign: int = 1,
    lagna_degree: float = 15.0,
    active_mahadasha: Optional[str] = None,
    active_antardasha: Optional[str] = None,
    next_mahadasha: Optional[str] = None
) -> MedicalTimingResult:
    """Evaluate medical vulnerabilities, disease onset indicators, and recovery prognosis."""
    mb_planets = check_mrityu_bhaga(planets_data, lagna_sign, lagna_degree)
    
    # Identify Trik and Maraka Lords
    h6_sign = ((lagna_sign + 4) % 12) + 1
    h8_sign = ((lagna_sign + 6) % 12) + 1
    h12_sign = ((lagna_sign + 10) % 12) + 1
    h2_sign = (lagna_sign % 12) + 1
    h7_sign = ((lagna_sign + 5) % 12) + 1
    
    lord_6 = SIGN_LORDS[h6_sign]
    lord_8 = SIGN_LORDS[h8_sign]
    lord_12 = SIGN_LORDS[h12_sign]
    lord_2 = SIGN_LORDS[h2_sign]
    lord_7 = SIGN_LORDS[h7_sign]
    lagna_lord = SIGN_LORDS[lagna_sign]
    
    trik_lords_set = {lord_6, lord_8, lord_12}
    maraka_lords_set = {lord_2, lord_7}
    
    dasha_lords_health_risk: List[str] = []
    trik_lord_connections: List[str] = []
    protective_factors: List[str] = []
    adverse_factors: List[str] = []
    
    # 1. Analyze active Dasha / Antardasha lords
    dasha_check_list = []
    if active_mahadasha:
        dasha_check_list.append(("Mahadasha", active_mahadasha))
    if active_antardasha:
        dasha_check_list.append(("Antardasha", active_antardasha))
        
    lagna_lord_sign = planets_data.get(lagna_lord, {}).get("sign_index", lagna_sign)
    
    for level, d_lord in dasha_check_list:
        d_lord_data = planets_data.get(d_lord, {})
        d_sign = d_lord_data.get("sign_index", 1)
        
        # Check if dasha lord is trik lord
        if d_lord in trik_lords_set:
            role = "6th (Roga/Disease)" if d_lord == lord_6 else ("8th (Mrityu/Crisis)" if d_lord == lord_8 else "12th (Hospitalization)")
            dasha_lords_health_risk.append(f"{level} Lord {d_lord} is ruler of {role} house")
            adverse_factors.append(f"{level} lord {d_lord} rules adverse dusthana house.")
            
        # Check if dasha lord is maraka lord
        if d_lord in maraka_lords_set:
            dasha_lords_health_risk.append(f"{level} Lord {d_lord} is ruler of Maraka (death-inflicting) house")
            
        # Check if dasha lord is connected to Lagna or Lagna lord
        d_aspects = get_parashari_aspects_for_planet(d_lord, d_sign)
        if lagna_sign in d_aspects or d_sign == lagna_sign:
            dasha_lords_health_risk.append(f"{level} Lord {d_lord} directly afflicts / aspects Tanu Bhava (Lagna)")
        if lagna_lord_sign in d_aspects or d_sign == lagna_lord_sign:
            dasha_lords_health_risk.append(f"{level} Lord {d_lord} afflicts Lagna Lord {lagna_lord}")

    # 2. Check Trik Lord interconnections & combustion
    for t_lord in trik_lords_set:
        t_data = planets_data.get(t_lord, {})
        if t_data.get("is_combust", False):
            trik_lord_connections.append(f"{t_lord} (Dusthana lord) is combust by Sun, intensifying physiological vulnerability.")
            adverse_factors.append(f"Combustion of dusthana ruler {t_lord}.")
            
    # Mutual connection between 6th and 8th lords
    lord_6_sign = planets_data.get(lord_6, {}).get("sign_index")
    lord_8_sign = planets_data.get(lord_8, {}).get("sign_index")
    if lord_6_sign and lord_8_sign and lord_6_sign == lord_8_sign:
        trik_lord_connections.append(f"6th Lord ({lord_6}) and 8th Lord ({lord_8}) are conjoined, forming acute Sarpa/Roga yoga.")
        adverse_factors.append("Conjunction of 6th and 8th lords.")

    # 3. Rahu-Ketu axis on Dasha lords
    rahu_sign = planets_data.get("Rahu", {}).get("sign_index", 1)
    ketu_sign = planets_data.get("Ketu", {}).get("sign_index", 7)
    
    rahu_ketu_axis_on_dasha_lords = False
    for _, d_lord in dasha_check_list:
        d_sign = planets_data.get(d_lord, {}).get("sign_index")
        if d_sign in {rahu_sign, ketu_sign}:
            rahu_ketu_axis_on_dasha_lords = True
            adverse_factors.append(f"Dasha lord {d_lord} is hemmed/conjoined in Rahu-Ketu nodal axis.")

    # 4. Retrograde Benefics in Kendras (Dr. Charak Rule: fail to protect or delay cure)
    kendra_signs = {
        lagna_sign,
        ((lagna_sign + 2) % 12) + 1,  # 4th house
        ((lagna_sign + 5) % 12) + 1,  # 7th house
        ((lagna_sign + 8) % 12) + 1   # 10th house
    }
    
    retrograde_benefics_in_kendras: List[str] = []
    for b in NATURAL_BENEFICS:
        if b in planets_data:
            b_data = planets_data[b]
            if b_data.get("sign_index") in kendra_signs and b_data.get("is_retrograde", False):
                retrograde_benefics_in_kendras.append(b)
                adverse_factors.append(
                    f"Retrograde benefic {b} in Kendra fails to deliver regular medical protection and may delay healing."
                )

    # Check benefic protection on Lagna / Lagna lord
    for b in NATURAL_BENEFICS:
        if b in planets_data and b not in retrograde_benefics_in_kendras:
            b_sign = planets_data[b].get("sign_index", 1)
            b_aspects = get_parashari_aspects_for_planet(b, b_sign)
            if lagna_sign in b_aspects or b_sign == lagna_sign:
                protective_factors.append(f"Direct benefic influence from {b} on Janma Lagna.")
            if lagna_lord_sign in b_aspects or b_sign == lagna_lord_sign:
                protective_factors.append(f"Benefic support from {b} protecting Lagna Lord ({lagna_lord}).")

    if mb_planets:
        for mb in mb_planets:
            adverse_factors.append(f"Planet {mb.planet} is critically placed in Mrityu Bhaga ({mb.degree_in_sign}° in {mb.sign}).")

    # 5. Subsequent Dasha Prognosis (Dr. Charak principle)
    if next_mahadasha:
        if next_mahadasha in NATURAL_BENEFICS or next_mahadasha == lagna_lord:
            subsequent_dasha_prognosis = (
                f"Upcoming Mahadasha of {next_mahadasha} is supportive. Dr. Charak's research indicates that transition into a "
                f"benefic/Lagna-supportive dasha facilitates substantial recovery, therapeutic breakthrough, and renewal of vitality."
            )
            subsequent_dasha_prognosis_tamil = (
                f"அடுத்த வரவிருக்கும் {next_mahadasha} மகாதிசை சுபமானதாகும். இது நோயிலிருந்து முழுமையான குணமடைதல், "
                f"மருத்துவ முன்னேற்றம் மற்றும் உடல் பலம் திரும்புதலை உறுதி செய்கிறது."
            )
        elif next_mahadasha in trik_lords_set or next_mahadasha in NATURAL_MALEFICS:
            subsequent_dasha_prognosis = (
                f"Upcoming Mahadasha of {next_mahadasha} also bears dusthana/malefic lordship. Dr. Charak emphasizes prolonged "
                f"vigilance, proactive medical care, and disciplined lifestyle as recovery may be gradual and require sustained intervention."
            )
            subsequent_dasha_prognosis_tamil = (
                f"அடுத்த வரவிருக்கும் {next_mahadasha} மகாதிசை கடினமான அமைப்பாகும். தொடர் மருத்துவ கவனிப்பு, சீரான உணவு முறை "
                f"மற்றும் தகுந்த முன்னெச்சரிக்கைகள் அவசியம்."
            )
        else:
            subsequent_dasha_prognosis = f"Upcoming Mahadasha of {next_mahadasha} indicates a period of stabilization and gradual health management."
            subsequent_dasha_prognosis_tamil = f"அடுத்த {next_mahadasha} மகாதிசை ஆரோக்கியத்தில் படிப்படியான சமநிலையை ஏற்படுத்தும்."
    else:
        subsequent_dasha_prognosis = "Continuous monitoring advised. Unafflicted benefics aspecting Lagna ensure underlying recuperative potential."
        subsequent_dasha_prognosis_tamil = "தொடர் கவனம் தேவை. லக்னத்திற்கு சுப பார்வை இருப்பது உடல் நலம் தேற உதவும்."

    # Overall prognosis verdict
    if len(adverse_factors) >= 4 or len(mb_planets) >= 2:
        prognosis_verdict = "High Health Vigilance Required"
        prognosis_verdict_tamil = "அதிக ஆரோக்கியக் கண்காணிப்பு தேவைப்படும் காலம்"
    elif len(adverse_factors) >= 2:
        prognosis_verdict = "Moderate Physiological Stress / Manageable"
        prognosis_verdict_tamil = "மிதமான உடல்நல அழுத்தங்கள் / சீர்செய்யக்கூடியது"
    else:
        prognosis_verdict = "Sound Recuperative Strength & Longevity"
        prognosis_verdict_tamil = "சிறந்த நோய் எதிர்ப்பு சக்தி மற்றும் ஆரோக்கிய பாதுகாப்பு"

    return MedicalTimingResult(
        planets_in_mrityu_bhaga=mb_planets,
        dasha_lords_health_risk=dasha_lords_health_risk,
        trik_lord_connections=trik_lord_connections,
        rahu_ketu_axis_on_dasha_lords=rahu_ketu_axis_on_dasha_lords,
        retrograde_benefics_in_kendras=retrograde_benefics_in_kendras,
        subsequent_dasha_prognosis=subsequent_dasha_prognosis,
        subsequent_dasha_prognosis_tamil=subsequent_dasha_prognosis_tamil,
        prognosis_verdict=prognosis_verdict,
        prognosis_verdict_tamil=prognosis_verdict_tamil,
        protective_factors=protective_factors,
        adverse_factors=adverse_factors,
    )
