"""Kaksha-based Transit Analysis Engine.

Classical Reference:
- Brihat Parashara Hora Shastra (BPHS), Chapter 67: Kaksha Vibhaga.
- Dr. B.V. Raman, 'Ashtakavarga System of Direction', Chapter 6: Transits.

Kaksha Subdivision Principles:
1. Each of the 12 zodiac signs (30°00′) is partitioned into eight equal Kakshas of 3°45′ (3.75°).
2. The eight Kakshas within each sign are governed in a fixed classical sequence
   corresponding to descending geocentric orbital speed plus Lagna:
     - Kaksha 1: 00°00′ – 03°45′ (0.00 – 3.75°)  → Lord: Saturn
     - Kaksha 2: 03°45′ – 07°30′ (3.75 – 7.50°)  → Lord: Jupiter
     - Kaksha 3: 07°30′ – 11°15′ (7.50 – 11.25°) → Lord: Mars
     - Kaksha 4: 11°15′ – 15°00′ (11.25 – 15.00°)→ Lord: Sun
     - Kaksha 5: 15°00′ – 18°45′ (15.00 – 18.75°)→ Lord: Venus
     - Kaksha 6: 18°45′ – 22°30′ (18.75 – 22.50°)→ Lord: Mercury
     - Kaksha 7: 22°30′ – 26°15′ (22.50 – 26.25°)→ Lord: Moon
     - Kaksha 8: 26°15′ – 30°00′ (26.25 – 30.00°)→ Lord: Lagna (Ascendant)
3. Transit Principle: When a planet transits through a Kaksha whose lord contributed
   a bindu (1) in that planet's natal Prastara matrix, the transit produces auspicious
   and constructive fruits. If the Kaksha lord contributed a zero (rekha), the transit
   is unfavorable or brings delays and obstacles.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from app.schemas.ashtakavarga import (
    KakshaDivisionInfo,
    KakshaTransitQuery,
    KakshaTransitResult,
    PlanetKakshaSignDetail,
    PrastaraDetail,
)
from app.services.ashtakavarga_engine.prastara import KAKSHA_CONTRIBUTOR_ORDER

KAKSHA_WIDTH_DEG: float = 3.75  # 3°45'

KAKSHA_RANGES: Tuple[str, ...] = (
    "00°00′ – 03°45′",
    "03°45′ – 07°30′",
    "07°30′ – 11°15′",
    "11°15′ – 15°00′",
    "15°00′ – 18°45′",
    "18°45′ – 22°30′",
    "22°30′ – 26°15′",
    "26°15′ – 30°00′",
)

SIGN_NAMES_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}


def get_kaksha_division_for_degree(degree_in_sign: float) -> Tuple[int, str, float, float, str]:
    """Identify the Kaksha division (1 to 8), lord, boundaries, and range string for a given degree.

    Parameters:
    - degree_in_sign: Float degree within sign (0.0 to 30.0)

    Returns:
    - (kaksha_number 1-8, lord_name, start_degree, end_degree, range_display_str)
    """
    # Handle exact 0.0 to 30.0 range cleanly
    deg = max(0.0, min(30.0, float(degree_in_sign)))

    if deg >= 30.0:
        k_idx = 7
    else:
        k_idx = int(deg // KAKSHA_WIDTH_DEG)
        if k_idx > 7:
            k_idx = 7

    kaksha_num = k_idx + 1
    lord = KAKSHA_CONTRIBUTOR_ORDER[k_idx]
    start_deg = round(k_idx * KAKSHA_WIDTH_DEG, 4)
    end_deg = round((k_idx + 1) * KAKSHA_WIDTH_DEG, 4)
    range_str = KAKSHA_RANGES[k_idx]

    return kaksha_num, lord, start_deg, end_deg, range_str


def build_planet_kaksha_grid(
    planet_name: str,
    prastara_detail: PrastaraDetail,
) -> List[PlanetKakshaSignDetail]:
    """Construct the complete 96-Kaksha breakdown (12 signs × 8 divisions) for one planet.

    Reconciles with Prastara matrix:
    - Each division has has_bindu=True if the Kaksha lord contributed 1 in this sign.
    - Total bindus in each sign exactly equals the BAV sign bindus!
    """
    donor_map: Dict[str, Dict[int, int]] = {
        row.contributor: row.sign_bindus for row in prastara_detail.rows
    }

    result: List[PlanetKakshaSignDetail] = []

    for s in range(1, 13):
        divisions: List[KakshaDivisionInfo] = []
        sign_bindu_count = 0

        for k_idx in range(8):
            lord = KAKSHA_CONTRIBUTOR_ORDER[k_idx]
            start_d = round(k_idx * KAKSHA_WIDTH_DEG, 4)
            end_d = round((k_idx + 1) * KAKSHA_WIDTH_DEG, 4)
            has_bindu = donor_map.get(lord, {}).get(s, 0) == 1

            if has_bindu:
                sign_bindu_count += 1

            divisions.append(
                KakshaDivisionInfo(
                    kaksha_number=k_idx + 1,
                    lord=lord,
                    start_degree=start_d,
                    end_degree=end_d,
                    range_display=KAKSHA_RANGES[k_idx],
                    has_bindu=has_bindu,
                    auspicious=has_bindu,
                )
            )

        result.append(
            PlanetKakshaSignDetail(
                sign_index=s,
                sign_name=SIGN_NAMES_EN[s],
                divisions=divisions,
                total_bindus=sign_bindu_count,
            )
        )

    return result


def build_all_kaksha_grids(
    prastara_dict: Dict[str, PrastaraDetail],
) -> Dict[str, List[PlanetKakshaSignDetail]]:
    """Build full Kaksha grids for all 7 classical planets."""
    return {
        planet: build_planet_kaksha_grid(planet, prastara_detail)
        for planet, prastara_detail in prastara_dict.items()
    }


def evaluate_kaksha_transit(
    transiting_planet: str,
    prastara_dict: Dict[str, PrastaraDetail],
    transit_longitude: Optional[float] = None,
    transit_sign_index: Optional[int] = None,
    transit_degree_in_sign: Optional[float] = None,
) -> KakshaTransitResult:
    """Evaluate whether a transiting planet's current position falls in an auspicious Kaksha.

    Parameters:
    - transiting_planet: Graha name (e.g. 'Jupiter', 'Saturn', 'Mars')
    - prastara_dict: Dictionary of PrastaraDetail matrices for all planets
    - transit_longitude: Absolute sidereal longitude (0.0 to 360.0°) OR
    - transit_sign_index (1-12) and transit_degree_in_sign (0.0-30.0°)
    """
    if transit_longitude is not None:
        norm_lon = float(transit_longitude) % 360.0
        sign_idx = int(norm_lon // 30.0) + 1
        deg_in_sign = norm_lon % 30.0
    elif transit_sign_index is not None and transit_degree_in_sign is not None:
        sign_idx = int(transit_sign_index)
        deg_in_sign = float(transit_degree_in_sign) % 30.0
    else:
        raise ValueError("Must provide either transit_longitude or (transit_sign_index and transit_degree_in_sign)")

    sign_name = SIGN_NAMES_EN.get(sign_idx, f"Sign_{sign_idx}")
    kaksha_num, lord, start_deg, end_deg, range_str = get_kaksha_division_for_degree(deg_in_sign)

    prastara_for_planet = prastara_dict.get(transiting_planet)
    if not prastara_for_planet:
        raise ValueError(f"No Prastara matrix available for planet '{transiting_planet}'")

    donor_map = {row.contributor: row.sign_bindus for row in prastara_for_planet.rows}
    has_bindu = donor_map.get(lord, {}).get(sign_idx, 0) == 1

    if has_bindu:
        effect = "Auspicious"
        interp = (
            f"Transiting {transiting_planet} is in Kaksha {kaksha_num} ({range_str}) of {sign_name}, "
            f"ruled by {lord}. {lord} contributes a bindu (1) in {transiting_planet}'s natal Prastara; "
            f"this transit period is auspicious and produces favorable results."
        )
    else:
        effect = "Inauspicious"
        interp = (
            f"Transiting {transiting_planet} is in Kaksha {kaksha_num} ({range_str}) of {sign_name}, "
            f"ruled by {lord}. {lord} contributes no bindu (0) in {transiting_planet}'s natal Prastara; "
            f"this transit period is inauspicious or obstructive."
        )

    return KakshaTransitResult(
        transiting_planet=transiting_planet,
        sign_index=sign_idx,
        sign_name=sign_name,
        degree_in_sign=round(deg_in_sign, 4),
        kaksha_number=kaksha_num,
        kaksha_lord=lord,
        kaksha_range=range_str,
        has_bindu=has_bindu,
        effect=effect,
        interpretation=interp,
    )
