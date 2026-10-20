"""Ashtakavarga calculator: Bhinnashtakavarga, Sarvashtakavarga aggregation, and Shodhana reductions."""

from typing import List, Dict, Any, Tuple
from app.schemas.ashtakavarga import (
    PlanetBavDetail,
    SavDetail,
    AshtakavargaResponse,
)
from app.services.ashtakavarga_engine.tables import (
    PLANETS_7,
    EXPECTED_TOTALS,
    TOTAL_SAV_BINDUS,
    ASHTAKAVARGA_CONTRIBUTIONS,
)
from app.services.ashtakavarga_engine.shodhana import (
    apply_trikona_shodhana,
    apply_ekadhipatya_shodhana,
    compute_shodhya_pinda,
)
from app.services.ashtakavarga_engine.prastara import compute_all_prastara_matrices
from app.services.ashtakavarga_engine.kaksha import build_all_kaksha_grids


def calculate_ashtakavarga(
    planets: List[Any],
    ascendant_sign_idx: int,
    apply_shodhana: bool = True,
    include_prastara: bool = True,
    include_kaksha: bool = True,
) -> AshtakavargaResponse:
    """Compute Bhinnashtakavarga (BAV) for 7 planets, aggregate Sarvashtakavarga (SAV),
    calculate Shodhana reductions, and optionally generate Prastara matrices and Kaksha grids.

    Parameters:
    - planets: list of planet objects or dicts having 'name' and 'sign_index' (1-12)
    - ascendant_sign_idx: Ascendant sign index (1-12)
    - apply_shodhana: whether to compute reductions and pindas (default: True)
    - include_prastara: whether to compute complete 8x12 Prastara matrices (default: True)
    - include_kaksha: whether to compute 96-Kaksha transit grids (default: True)
    """
    # 1. Map positions of the 7 planets and Lagna
    contributor_signs: Dict[str, int] = {}
    planet_signs: Dict[str, int] = {}

    for p in planets:
        p_name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else None)
        p_sign = getattr(p, "sign_index", None) or (p.get("sign_index") if isinstance(p, dict) else None)

        if p_name in PLANETS_7 and p_sign is not None:
            contributor_signs[p_name] = p_sign
            planet_signs[p_name] = p_sign

    contributor_signs["Lagna"] = ascendant_sign_idx

    # 2. Compute Bhinnashtakavarga for each of the 7 classical planets
    bav_dict: Dict[str, PlanetBavDetail] = {}
    sav_sign_totals: Dict[int, int] = {s: 0 for s in range(1, 13)}

    for target_p in PLANETS_7:
        sign_bindus: Dict[int, int] = {s: 0 for s in range(1, 13)}
        rules_for_target = ASHTAKAVARGA_CONTRIBUTIONS[target_p]

        # Calculate contributions from all 8 donors
        for donor_name, houses in rules_for_target.items():
            if donor_name in contributor_signs:
                donor_sign = contributor_signs[donor_name]
                for h in houses:
                    # Beneficiary sign = donor_sign + (h - 1) wrapping around 1-12
                    beneficiary_sign = ((donor_sign - 1 + (h - 1)) % 12) + 1
                    sign_bindus[beneficiary_sign] += 1

        total_b = sum(sign_bindus.values())
        expected_b = EXPECTED_TOTALS[target_p]

        # House-wise bindus measured from Lagna (House 1 = Lagna sign)
        house_bindus: Dict[int, int] = {}
        for h in range(1, 13):
            sign_at_house = ((ascendant_sign_idx - 1 + (h - 1)) % 12) + 1
            house_bindus[h] = sign_bindus[sign_at_house]

        # Accumulate into Sarvashtakavarga
        for s in range(1, 13):
            sav_sign_totals[s] += sign_bindus[s]

        # Optional Shodhana reductions
        trikona_red = None
        ekadhipatya_red = None
        r_pinda = None
        g_pinda = None
        s_pinda = None

        if apply_shodhana:
            trikona_red = apply_trikona_shodhana(sign_bindus)
            ekadhipatya_red = apply_ekadhipatya_shodhana(trikona_red, planet_signs)
            r_pinda, g_pinda, s_pinda = compute_shodhya_pinda(ekadhipatya_red, planet_signs)

        bav_dict[target_p] = PlanetBavDetail(
            planet=target_p,
            sign_bindus=sign_bindus,
            house_bindus=house_bindus,
            total_bindus=total_b,
            expected_total=expected_b,
            trikona_reduced=trikona_red,
            ekadhipatya_reduced=ekadhipatya_red,
            rashi_pinda=r_pinda,
            graha_pinda=g_pinda,
            shodhya_pinda=s_pinda,
        )

    # 3. Assemble Sarvashtakavarga (SAV)
    sav_house_totals: Dict[int, int] = {}
    for h in range(1, 13):
        sign_at_house = ((ascendant_sign_idx - 1 + (h - 1)) % 12) + 1
        sav_house_totals[h] = sav_sign_totals[sign_at_house]

    sav_grand_total = sum(sav_sign_totals.values())
    validation_status = "PASSED" if sav_grand_total == TOTAL_SAV_BINDUS else "FAILED_INVARIANT"

    sav_detail = SavDetail(
        sign_bindus=sav_sign_totals,
        house_bindus=sav_house_totals,
        total_bindus=sav_grand_total,
        average_per_sign=round(sav_grand_total / 12.0, 2),
        auspicious_signs=[s for s in range(1, 13) if sav_sign_totals[s] >= 28],
        inauspicious_signs=[s for s in range(1, 13) if sav_sign_totals[s] < 28],
    )

    # 4. Optional Prastara & Kaksha calculations
    prastara_data = None
    kaksha_data = None
    if include_prastara or include_kaksha:
        prastara_data = compute_all_prastara_matrices(contributor_signs)
        if include_kaksha:
            kaksha_data = build_all_kaksha_grids(prastara_data)
        if not include_prastara:
            prastara_data = None

    return AshtakavargaResponse(
        bhinnashtakavarga=bav_dict,
        sarvashtakavarga=sav_detail,
        lagna_sign_index=ascendant_sign_idx,
        validation_status=validation_status,
        prastara=prastara_data,
        kaksha_grids=kaksha_data,
    )

