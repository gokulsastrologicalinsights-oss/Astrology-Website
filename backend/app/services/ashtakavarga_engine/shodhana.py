"""Classical Shodhana (Reductions) and Pinda Sadhana per Brihat Parashara Hora Shastra Chapters 67-69."""

from typing import Dict, List, Tuple, Set, Any
from app.services.ashtakavarga_engine.tables import (
    RASHI_GUNAKA,
    GRAHA_GUNAKA,
    DUAL_LORDSHIP_PAIRS,
)

# The four trikona triads (BPHS Ch. 67)
TRIKONA_TRIADS: Tuple[Tuple[int, int, int], ...] = (
    (1, 5, 9),    # Fire (Aries, Leo, Sagittarius)
    (2, 6, 10),   # Earth (Taurus, Virgo, Capricorn)
    (3, 7, 11),   # Air (Gemini, Libra, Aquarius)
    (4, 8, 12),   # Water (Cancer, Scorpio, Pisces)
)


def apply_trikona_shodhana(sign_bindus: Dict[int, int]) -> Dict[int, int]:
    """Perform Trikona Shodhana (Trinal Reduction) on a planet's BAV grid.

    BPHS Chapter 67:
    In each trikona triad of signs, subtract the minimum bindu count from all three signs.
    If all three signs have equal points, all three become 0.
    If any sign in the triad has 0, the minimum is 0, so no reduction occurs.
    """
    reduced = dict(sign_bindus)

    for s1, s2, s3 in TRIKONA_TRIADS:
        b1, b2, b3 = reduced[s1], reduced[s2], reduced[s3]
        min_b = min(b1, b2, b3)
        if min_b > 0:
            reduced[s1] = b1 - min_b
            reduced[s2] = b2 - min_b
            reduced[s3] = b3 - min_b

    return reduced


def apply_ekadhipatya_shodhana(
    trikona_reduced: Dict[int, int],
    planet_signs: Dict[str, int],
) -> Dict[int, int]:
    """Perform Ekadhipatya Shodhana (Dual-Lordship Reduction) per BPHS Chapter 68.

    Applied to the Trikona-reduced bindus for signs sharing the same lord:
    - Mars (1 & 8), Venus (2 & 7), Mercury (3 & 6), Jupiter (9 & 12), Saturn (10 & 11).
    - Sun (Leo 5) and Moon (Cancer 4) have single lordship, so are not modified here.

    Rules:
    1. If both signs have 0 bindus, remain 0.
    2. If one sign has 0 bindus, the other sign remains unchanged.
    3. If both signs are occupied by planets, no reduction occurs.
    4. If neither sign is occupied:
       - If equal bindus, both become 0.
       - If unequal, both become equal to the smaller bindu count.
    5. If one sign is occupied and the other is unoccupied:
       - The occupied sign retains its bindus.
       - The unoccupied sign:
         - If unoccupied bindus > occupied bindus, unoccupied is reduced to equal occupied.
         - If unoccupied bindus <= occupied bindus, unoccupied becomes 0.
    """
    reduced = dict(trikona_reduced)

    # Set of signs occupied by at least one of the 7 classical planets
    occupied_signs: Set[int] = set(planet_signs.values())

    for _, s1, s2 in DUAL_LORDSHIP_PAIRS:
        b1, b2 = reduced[s1], reduced[s2]

        # Rule 1 & 2: If either sign is 0, no reduction
        if b1 == 0 or b2 == 0:
            continue

        occ1 = s1 in occupied_signs
        occ2 = s2 in occupied_signs

        # Rule 3: If both signs are occupied, no reduction
        if occ1 and occ2:
            continue

        # Rule 4: If neither sign is occupied
        if not occ1 and not occ2:
            if b1 == b2:
                reduced[s1] = 0
                reduced[s2] = 0
            else:
                smaller = min(b1, b2)
                reduced[s1] = smaller
                reduced[s2] = smaller
            continue

        # Rule 5: One sign is occupied, the other is unoccupied
        if occ1 and not occ2:
            # s1 is occupied, s2 is unoccupied
            if b2 > b1:
                reduced[s2] = b1
            else:
                reduced[s2] = 0
        elif occ2 and not occ1:
            # s2 is occupied, s1 is unoccupied
            if b1 > b2:
                reduced[s1] = b2
            else:
                reduced[s1] = 0

    return reduced


def compute_shodhya_pinda(
    ekadhipatya_reduced: Dict[int, int],
    planet_signs: Dict[str, int],
) -> Tuple[int, int, int]:
    """Calculate Rashi Pinda, Graha Pinda, and Total Shodhya Pinda per BPHS Chapter 69.

    Returns:
    (rashi_pinda, graha_pinda, total_shodhya_pinda)
    """
    # 1. Rashi Pinda: Sum of (reduced_bindus * rashi_gunaka) for all 12 signs
    rashi_pinda = sum(
        ekadhipatya_reduced[s] * RASHI_GUNAKA[s]
        for s in range(1, 13)
    )

    # 2. Graha Pinda: For each sign occupied by classical planets,
    # multiply the sign's reduced bindus by the occupant's graha_gunaka
    graha_pinda = 0
    for p_name, sign_idx in planet_signs.items():
        if p_name in GRAHA_GUNAKA:
            graha_pinda += ekadhipatya_reduced[sign_idx] * GRAHA_GUNAKA[p_name]

    shodhya_pinda = rashi_pinda + graha_pinda
    return rashi_pinda, graha_pinda, shodhya_pinda
