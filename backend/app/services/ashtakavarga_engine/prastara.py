"""Prastarashtakavarga (Spread-out / Expanded Ashtakavarga) Engine.

Classical Reference:
- Brihat Parashara Hora Shastra (BPHS), Chapters 66 & 67.
- Dr. B.V. Raman, 'Ashtakavarga System of Direction', Chapter 5.

For each of the seven classical planets, the Prastara matrix consists of:
- 8 Donors / Contributors (ordered in classical Kaksha descending speed):
  1. Saturn (slowest planet)
  2. Jupiter
  3. Mars
  4. Sun
  5. Venus
  6. Mercury
  7. Moon (fastest planet)
  8. Lagna (Ascendant)
- 12 Zodiac signs (Columns: 1=Aries to 12=Pisces).

Invariants & Mathematical Reconciliations:
1. Column Sum: For any sign s, sum across all 8 donors equals the BAV bindus for sign s.
2. Row Sum: For any donor c, sum across all 12 signs equals the number of auspicious houses
   prescribed in BPHS for donor c.
3. Matrix Total: Grand sum of all 1s in a planet's matrix equals EXPECTED_TOTALS[planet]
   (Sun: 48, Moon: 49, Mars: 39, Mercury: 54, Jupiter: 56, Venus: 52, Saturn: 39).
4. Aggregate Total: Grand sum across all 7 matrices equals 337.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from app.schemas.ashtakavarga import PrastaraDetail, PrastaraRow
from app.services.ashtakavarga_engine.tables import (
    ASHTAKAVARGA_CONTRIBUTIONS,
    EXPECTED_TOTALS,
    PLANETS_7,
)

# Canonical 8-donor sequence in classical Kaksha order (slowest to fastest + Lagna)
KAKSHA_CONTRIBUTOR_ORDER: Tuple[str, ...] = (
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Lagna",
)


def compute_planet_prastara(
    target_planet: str,
    contributor_signs: Dict[str, int],
) -> PrastaraDetail:
    """Compute the 8-donor by 12-sign Prastara matrix for one target graha.

    Parameters:
    - target_planet: Graha name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)
    - contributor_signs: Dict mapping donor names (7 grahas + Lagna) to their 1-indexed sign (1-12)
    """
    rules_for_target = ASHTAKAVARGA_CONTRIBUTIONS[target_planet]
    rows: List[PrastaraRow] = []
    sign_column_totals: Dict[int, int] = {s: 0 for s in range(1, 13)}

    for donor in KAKSHA_CONTRIBUTOR_ORDER:
        donor_sign = contributor_signs.get(donor, 1)
        beneficial_houses = frozenset(rules_for_target.get(donor, ()))

        row_sign_bindus: Dict[int, int] = {}
        row_total = 0

        for s in range(1, 13):
            # House distance from donor_sign to sign s (1-indexed, 1 to 12)
            house_dist = ((s - donor_sign) % 12) + 1
            has_bindu = 1 if house_dist in beneficial_houses else 0
            row_sign_bindus[s] = has_bindu
            row_total += has_bindu
            sign_column_totals[s] += has_bindu

        rows.append(
            PrastaraRow(
                contributor=donor,
                sign_bindus=row_sign_bindus,
                total_contributions=row_total,
            )
        )

    matrix_grand_total = sum(sign_column_totals.values())

    return PrastaraDetail(
        planet=target_planet,
        rows=rows,
        sign_totals=sign_column_totals,
        total_bindus=matrix_grand_total,
    )


def compute_all_prastara_matrices(
    contributor_signs: Dict[str, int],
) -> Dict[str, PrastaraDetail]:
    """Compute complete Prastara matrices for all seven classical planets."""
    result: Dict[str, PrastaraDetail] = {}
    for target_p in PLANETS_7:
        result[target_p] = compute_planet_prastara(target_p, contributor_signs)
    return result
