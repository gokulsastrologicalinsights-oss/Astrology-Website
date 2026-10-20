"""Independent deterministic evaluators for the North Indian 36-Point Ashtakoota Matching.

Classical Authority:
- Muhurta Chintamani, Chapter 6: Vivaha Prakarana (Slokas 1–25)
- Brihat Parashara Hora Shastra, Chapter 81: Vivaha Melana
- Jataka Parijata & Phaladeepika

Kootas Evaluated (Total 36 Points):
1. Varna Koota (ASHTA-01): 1 point max (Spiritual/Ego alignment via Rasi Varna)
2. Vashya Koota (ASHTA-02): 2 points max (Mutual magnetic control/influence)
3. Tara Koota (ASHTA-03): 3 points max (Destiny, health, and mutual longevity via Navatara)
4. Yoni Koota (ASHTA-04): 4 points max (Biological, physical, and sexual compatibility)
5. Graha Maitri Koota (ASHTA-05): 5 points max (Psychological harmony of Moon sign lords)
6. Gana Koota (ASHTA-06): 6 points max (Temperamental, social, and behavioral harmony)
7. Bhakoot Koota (ASHTA-07): 7 points max (Emotional, health, and financial growth)
8. Nadi Koota (ASHTA-08): 8 points max (Genetic, nervous, and physiological resonance)
"""

from typing import Dict, Any, List, Optional, Tuple, Set

from app.services.marriage_engine.models import (
    MarriageChartContext,
    KootaResult,
    PoruthamStatus,
    GanaType,
    NadiType,
    VashyaCategory,
    NAKSHATRA_NAMES_EN,
    SIGN_NAMES_EN,
    SIGN_LORDS,
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    NAKSHATRA_YONI_ANIMAL,
    YONI_BITTER_ENEMIES,
    SIGN_VASHYA_CATEGORY,
    PLANETARY_NATURAL_FRIENDSHIP,
    SIGN_VARNA,
    VARNA_RANKS,
    get_yoni_koota_points,
)


# ===========================================================================
# 1. VARNA KOOTA (ASHTA-01) — 1 POINT
# ===========================================================================

def calculate_varna_core(groom_rasi_idx: int, bride_rasi_idx: int) -> Dict[str, Any]:
    """Pure calculation for Varna Koota (1 point max)."""
    g_varna = SIGN_VARNA[groom_rasi_idx]
    b_varna = SIGN_VARNA[bride_rasi_idx]

    g_rank = VARNA_RANKS[g_varna]
    b_rank = VARNA_RANKS[b_varna]

    if g_rank >= b_rank:
        status = PoruthamStatus.PASS
        earned = 1.0
        desc = (
            f"Groom Varna ({g_varna}) is equal to or higher than Bride Varna ({b_varna}). "
            "Varna Koota is fully satisfied (1.0 / 1.0)."
        )
    else:
        status = PoruthamStatus.FAIL
        earned = 0.0
        desc = (
            f"Groom Varna ({g_varna}) is lower than Bride Varna ({b_varna}) (Anuloma exception). "
            "Varna Koota yields 0 points (0.0 / 1.0)."
        )

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 1.0,
        "groom_varna": g_varna,
        "bride_varna": b_varna,
        "groom_rank": g_rank,
        "bride_rank": b_rank,
        "description": desc,
    }


def evaluate_varna_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Varna Koota (ASHTA-01)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-01",
            name_en="Varna Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=1.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Varna Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Sloka 1 (v1.0)",
        )

    res = calculate_varna_core(groom.moon_sign_idx, bride.moon_sign_idx)

    return KootaResult(
        koota_id="ASHTA-01",
        name_en="Varna Koota",
        status=res["status"],
        max_points=1.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Varna: {res['groom_varna']} (Rank {res['groom_rank']}) vs Bride Varna: {res['bride_varna']} (Rank {res['bride_rank']})",
        groom_input={"moon_sign": groom.moon_sign_name, "varna": res["groom_varna"]},
        bride_input={"moon_sign": bride.moon_sign_name, "varna": res["bride_varna"]},
        intermediate_calculation={
            "groom_varna": res["groom_varna"],
            "bride_varna": res["bride_varna"],
            "groom_rank": res["groom_rank"],
            "bride_rank": res["bride_rank"],
        },
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Sloka 1 (v1.0)",
    )


# ===========================================================================
# 2. VASHYA KOOTA (ASHTA-02) — 2 POINTS
# ===========================================================================

# Classical North Indian Vashya Attraction Map (Muhurta Chintamani Ch. 6 Sloka 2)
# Rasi index -> List of Rasi indices attracted to it
ASHTAKOOTA_VASHYA_MAP: Dict[int, List[int]] = {
    1: [5, 8],     # Aries -> Leo, Scorpio
    2: [4, 7],     # Taurus -> Cancer, Libra
    3: [6],        # Gemini -> Virgo
    4: [8, 9],     # Cancer -> Scorpio, Sagittarius
    5: [7],        # Leo -> Libra
    6: [12, 3],    # Virgo -> Pisces, Gemini
    7: [10, 6],    # Libra -> Capricorn, Virgo
    8: [4],        # Scorpio -> Cancer
    9: [12],       # Sagittarius -> Pisces
    10: [1, 11],   # Capricorn -> Aries, Aquarius
    11: [1],       # Aquarius -> Aries
    12: [10],      # Pisces -> Capricorn
}

def calculate_vashya_core(groom_rasi_idx: int, bride_rasi_idx: int) -> Dict[str, Any]:
    """Pure calculation for Vashya Koota (2 points max)."""
    g_cat = SIGN_VASHYA_CATEGORY[groom_rasi_idx]
    b_cat = SIGN_VASHYA_CATEGORY[bride_rasi_idx]

    g_attracts_b = bride_rasi_idx in ASHTAKOOTA_VASHYA_MAP.get(groom_rasi_idx, [])
    b_attracts_g = groom_rasi_idx in ASHTAKOOTA_VASHYA_MAP.get(bride_rasi_idx, [])

    # Sworn predator-prey enmity: Vanachara Leo (5) vs Chatushpada (Aries, Taurus, Capricorn) or Keeta (Scorpio)
    is_predator_enemy = (
        (g_cat == VashyaCategory.VANACHARA and b_cat in (VashyaCategory.CHATUSHPADA, VashyaCategory.DWIPADA))
        or (b_cat == VashyaCategory.VANACHARA and g_cat in (VashyaCategory.CHATUSHPADA, VashyaCategory.DWIPADA))
    )

    if g_cat == b_cat:
        earned = 2.0
        status = PoruthamStatus.PASS
        desc = f"Both Moon signs belong to the same Vashya category ({g_cat.value}). Full 2.0 points awarded."
    elif g_attracts_b and b_attracts_g:
        earned = 2.0
        status = PoruthamStatus.PASS
        desc = "Mutual Vashya attraction present between both Moon signs. Full 2.0 points awarded."
    elif g_attracts_b:
        earned = 1.0
        status = PoruthamStatus.PASS
        desc = "Bride sign is Vashya (amenable) to Groom sign. 1.0 point awarded."
    elif b_attracts_g:
        earned = 1.0
        status = PoruthamStatus.PASS
        desc = "Groom sign is Vashya to Bride sign. 1.0 point awarded."
    elif is_predator_enemy:
        earned = 0.0
        status = PoruthamStatus.FAIL
        desc = f"Inimical predator-prey Vashya relationship ({g_cat.value} vs {b_cat.value}). 0.0 points awarded."
    else:
        earned = 1.0
        status = PoruthamStatus.PASS
        desc = f"Neutral Vashya relationship between {g_cat.value} and {b_cat.value}. 1.0 point awarded."

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 2.0,
        "groom_category": g_cat.value,
        "bride_category": b_cat.value,
        "mutual_attraction": g_attracts_b and b_attracts_g,
        "description": desc,
    }


def evaluate_vashya_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Vashya Koota (ASHTA-02)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-02",
            name_en="Vashya Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=2.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Vashya Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Sloka 2 (v1.0)",
        )

    res = calculate_vashya_core(groom.moon_sign_idx, bride.moon_sign_idx)

    return KootaResult(
        koota_id="ASHTA-02",
        name_en="Vashya Koota",
        status=res["status"],
        max_points=2.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Vashya: {res['groom_category']} vs Bride Vashya: {res['bride_category']}",
        groom_input={"moon_sign": groom.moon_sign_name, "vashya_category": res["groom_category"]},
        bride_input={"moon_sign": bride.moon_sign_name, "vashya_category": res["bride_category"]},
        intermediate_calculation={
            "groom_vashya_category": res["groom_category"],
            "bride_vashya_category": res["bride_category"],
            "is_mutual": res["mutual_attraction"],
        },
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Sloka 2 (v1.0)",
    )


# ===========================================================================
# 3. TARA KOOTA (ASHTA-03) — 3 POINTS (BIDIRECTIONAL)
# ===========================================================================

def calculate_tara_core(bride_star_idx: int, groom_star_idx: int) -> Dict[str, Any]:
    """Pure calculation for bidirectional Tara Koota (3 points max: 1.5 pts each direction)."""
    # Direction 1: Bride to Groom
    d1 = ((groom_star_idx - bride_star_idx) % 27) + 1
    t1 = d1 % 9
    if t1 == 0:
        t1 = 9
    t1_auspicious = t1 in (2, 4, 6, 8, 9)
    pts1 = 1.5 if t1_auspicious else 0.0

    # Direction 2: Groom to Bride
    d2 = ((bride_star_idx - groom_star_idx) % 27) + 1
    t2 = d2 % 9
    if t2 == 0:
        t2 = 9
    t2_auspicious = t2 in (2, 4, 6, 8, 9)
    pts2 = 1.5 if t2_auspicious else 0.0

    total_earned = pts1 + pts2
    status = PoruthamStatus.PASS if total_earned >= 1.5 else PoruthamStatus.FAIL

    desc = (
        f"Bidirectional Tara evaluation: Bride-to-Groom distance {d1} (Tara {t1}) earned {pts1} pts; "
        f"Groom-to-Bride distance {d2} (Tara {t2}) earned {pts2} pts. Total Tara points: {total_earned:.1f} / 3.0."
    )

    return {
        "status": status,
        "earned_points": total_earned,
        "max_points": 3.0,
        "direction_b_to_g": {"distance": d1, "tara": t1, "is_auspicious": t1_auspicious, "points": pts1},
        "direction_g_to_b": {"distance": d2, "tara": t2, "is_auspicious": t2_auspicious, "points": pts2},
        "description": desc,
    }


def evaluate_tara_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Tara Koota (ASHTA-03)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-03",
            name_en="Tara Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=3.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Tara Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 3–5 (v1.0)",
        )

    res = calculate_tara_core(bride.moon_nakshatra_idx, groom.moon_nakshatra_idx)

    return KootaResult(
        koota_id="ASHTA-03",
        name_en="Tara Koota",
        status=res["status"],
        max_points=3.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Bride->Groom: Tara {res['direction_b_to_g']['tara']} ({res['direction_b_to_g']['points']} pts), Groom->Bride: Tara {res['direction_g_to_b']['tara']} ({res['direction_g_to_b']['points']} pts)",
        groom_input={"nakshatra": groom.moon_nakshatra_name, "nakshatra_index": groom.moon_nakshatra_idx},
        bride_input={"nakshatra": bride.moon_nakshatra_name, "nakshatra_index": bride.moon_nakshatra_idx},
        intermediate_calculation={
            "bride_to_groom": res["direction_b_to_g"],
            "groom_to_bride": res["direction_g_to_b"],
        },
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 3–5 (v1.0)",
    )


# ===========================================================================
# 4. YONI KOOTA (ASHTA-04) — 4 POINTS
# ===========================================================================

def calculate_yoni_ashtakoota_core(groom_star_idx: int, bride_star_idx: int) -> Dict[str, Any]:
    """Pure calculation for Yoni Koota (4 points max)."""
    g_animal = NAKSHATRA_YONI_ANIMAL[groom_star_idx]
    b_animal = NAKSHATRA_YONI_ANIMAL[bride_star_idx]

    pts = get_yoni_koota_points(g_animal, b_animal)
    is_bitter_enemy = pts == 0.0
    status = PoruthamStatus.PASS if pts >= 2.0 else PoruthamStatus.FAIL

    if is_bitter_enemy:
        desc = (
            f"Groom Yoni ({g_animal}) and Bride Yoni ({b_animal}) form a sworn inimical pair (Vaira Yoni). "
            f"0.0 / 4.0 points awarded. Severe biological/intimacy conflict."
        )
    elif pts == 4.0:
        desc = f"Both share the same Yoni animal ({g_animal}). Full 4.0 / 4.0 points awarded. Perfect biological concord."
    elif pts == 3.0:
        desc = f"Friendly Yoni archetypes ({g_animal} and {b_animal}). 3.0 / 4.0 points awarded."
    elif pts == 2.0:
        desc = f"Neutral Yoni archetypes ({g_animal} and {b_animal}). 2.0 / 4.0 points awarded."
    else:
        desc = f"Inimical Yoni archetypes ({g_animal} and {b_animal}). 1.0 / 4.0 points awarded."

    return {
        "status": status,
        "earned_points": pts,
        "max_points": 4.0,
        "groom_animal": g_animal,
        "bride_animal": b_animal,
        "is_dosha_present": is_bitter_enemy,
        "description": desc,
    }


def evaluate_yoni_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Yoni Koota (ASHTA-04)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-04",
            name_en="Yoni Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=4.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Yoni Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 6–9; BPHS Ch. 81 (v1.0)",
        )

    res = calculate_yoni_ashtakoota_core(groom.moon_nakshatra_idx, bride.moon_nakshatra_idx)

    return KootaResult(
        koota_id="ASHTA-04",
        name_en="Yoni Koota",
        status=res["status"],
        max_points=4.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Yoni: {res['groom_animal']} vs Bride Yoni: {res['bride_animal']} -> {res['earned_points']:.1f} pts",
        groom_input={"nakshatra": groom.moon_nakshatra_name, "yoni_animal": res["groom_animal"]},
        bride_input={"nakshatra": bride.moon_nakshatra_name, "yoni_animal": res["bride_animal"]},
        intermediate_calculation={
            "groom_animal": res["groom_animal"],
            "bride_animal": res["bride_animal"],
            "points": res["earned_points"],
        },
        is_dosha_present=res["is_dosha_present"],
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 6–9; BPHS Ch. 81 (v1.0)",
    )


# ===========================================================================
# 5. GRAHA MAITRI KOOTA (ASHTA-05) — 5 POINTS
# ===========================================================================

def calculate_graha_maitri_core(groom_rasi_idx: int, bride_rasi_idx: int) -> Dict[str, Any]:
    """Pure calculation for Graha Maitri Koota (5 points max)."""
    g_lord = SIGN_LORDS[groom_rasi_idx]
    b_lord = SIGN_LORDS[bride_rasi_idx]

    if g_lord == b_lord:
        earned = 5.0
        status = PoruthamStatus.PASS
        rel_str = "Same Lord"
        desc = f"Both Moon signs share the identical planetary ruler ({g_lord}). Full 5.0 / 5.0 points awarded."
    else:
        g_to_b = PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, 0)
        b_to_g = PLANETARY_NATURAL_FRIENDSHIP.get(b_lord, {}).get(g_lord, 0)

        if g_to_b == 1 and b_to_g == 1:
            earned = 5.0
            status = PoruthamStatus.PASS
            rel_str = "Mutual Friends"
            desc = f"Moon sign lords {g_lord} and {b_lord} are mutual natural friends. Full 5.0 / 5.0 points awarded."
        elif (g_to_b == 1 and b_to_g == 0) or (g_to_b == 0 and b_to_g == 1):
            earned = 4.0
            status = PoruthamStatus.PASS
            rel_str = "Friend-Neutral"
            desc = f"Moon sign lords {g_lord} and {b_lord} have a friend-neutral relationship. 4.0 / 5.0 points awarded."
        elif g_to_b == 0 and b_to_g == 0:
            earned = 3.0
            status = PoruthamStatus.PASS
            rel_str = "Mutual Neutral"
            desc = f"Moon sign lords {g_lord} and {b_lord} are mutually neutral. 3.0 / 5.0 points awarded."
        elif (g_to_b == 1 and b_to_g == -1) or (g_to_b == -1 and b_to_g == 1):
            earned = 1.0
            status = PoruthamStatus.FAIL
            rel_str = "Friend-Enemy"
            desc = f"Moon sign lords {g_lord} and {b_lord} have a mixed friend-enemy relationship. 1.0 / 5.0 points awarded."
        elif (g_to_b == 0 and b_to_g == -1) or (g_to_b == -1 and b_to_g == 0):
            earned = 0.5
            status = PoruthamStatus.FAIL
            rel_str = "Neutral-Enemy"
            desc = f"Moon sign lords {g_lord} and {b_lord} have a neutral-enemy relationship. 0.5 / 5.0 points awarded."
        else:
            earned = 0.0
            status = PoruthamStatus.FAIL
            rel_str = "Mutual Enemies"
            desc = f"Moon sign lords {g_lord} and {b_lord} are natural mutual enemies. 0.0 / 5.0 points awarded."

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 5.0,
        "groom_lord": g_lord,
        "bride_lord": b_lord,
        "relationship": rel_str,
        "description": desc,
    }


def evaluate_graha_maitri_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Graha Maitri Koota (ASHTA-05)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-05",
            name_en="Graha Maitri Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=5.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Graha Maitri Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 10–12; BPHS Ch. 81 (v1.0)",
        )

    res = calculate_graha_maitri_core(groom.moon_sign_idx, bride.moon_sign_idx)

    return KootaResult(
        koota_id="ASHTA-05",
        name_en="Graha Maitri Koota",
        status=res["status"],
        max_points=5.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Lord {res['groom_lord']} vs Bride Lord {res['bride_lord']} -> {res['relationship']} ({res['earned_points']:.1f} pts)",
        groom_input={"moon_sign": groom.moon_sign_name, "lord": res["groom_lord"]},
        bride_input={"moon_sign": bride.moon_sign_name, "lord": res["bride_lord"]},
        intermediate_calculation={
            "groom_lord": res["groom_lord"],
            "bride_lord": res["bride_lord"],
            "relationship": res["relationship"],
        },
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 10–12; BPHS Ch. 81 (v1.0)",
    )


# ===========================================================================
# 6. GANA KOOTA (ASHTA-06) — 6 POINTS
# ===========================================================================

def calculate_gana_ashtakoota_core(
    groom_star_idx: int,
    bride_star_idx: int,
    groom_rasi_idx: int,
    bride_rasi_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Gana Koota in Ashtakoota (6 points max)."""
    g_gana = NAKSHATRA_GANA[groom_star_idx]
    b_gana = NAKSHATRA_GANA[bride_star_idx]

    # Base points
    if g_gana == b_gana:
        base_pts = 6.0
    elif (g_gana == GanaType.DEVA and b_gana == GanaType.MANUSHYA) or (g_gana == GanaType.MANUSHYA and b_gana == GanaType.DEVA):
        base_pts = 5.0
    elif g_gana == GanaType.DEVA and b_gana == GanaType.RAKSHASA:
        base_pts = 1.0
    elif g_gana == GanaType.RAKSHASA and b_gana == GanaType.DEVA:
        base_pts = 1.0
    else:  # Manushya + Rakshasa in either direction
        base_pts = 0.0

    # Mitigation / Cancellation check per Muhurta Chintamani Ch. 6 Sloka 15:
    # If base_pts < 5.0, but Moon signs are Samasaptaka (7th) or lords are identical/friends -> 3.0 pts
    g_lord = SIGN_LORDS[groom_rasi_idx]
    b_lord = SIGN_LORDS[bride_rasi_idx]
    lords_friendly = (g_lord == b_lord) or (
        PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, 0) == 1
        and PLANETARY_NATURAL_FRIENDSHIP.get(b_lord, {}).get(g_lord, 0) == 1
    )
    is_samasaptaka = (((groom_rasi_idx - bride_rasi_idx) % 12) + 1) == 7

    is_cancelled = False
    cancellation_reason = None
    earned = base_pts

    if base_pts < 5.0 and (is_samasaptaka or lords_friendly):
        is_cancelled = True
        earned = 3.0
        reason_parts = []
        if is_samasaptaka:
            reason_parts.append("Samasaptaka (7th) Moon signs")
        if lords_friendly:
            reason_parts.append(f"friendly Moon sign lords ({g_lord} & {b_lord})")
        cancellation_reason = f"Gana defect mitigated to 3.0 points due to {' and '.join(reason_parts)} per Muhurta Chintamani Ch. 6 Sloka 15."

    status = PoruthamStatus.PASS if earned >= 3.0 else PoruthamStatus.FAIL
    desc = f"Groom Gana ({g_gana.value}) and Bride Gana ({b_gana.value}). Points awarded: {earned:.1f} / 6.0."
    if cancellation_reason:
        desc += f" {cancellation_reason}"

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 6.0,
        "groom_gana": g_gana.value,
        "bride_gana": b_gana.value,
        "base_points": base_pts,
        "is_cancelled": is_cancelled,
        "cancellation_reason": cancellation_reason,
        "description": desc,
    }


def evaluate_gana_koota_ashtakoota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Gana Koota (ASHTA-06)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-06",
            name_en="Gana Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=6.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Gana Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 13–15; BPHS Ch. 81 (v1.0)",
        )

    res = calculate_gana_ashtakoota_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
        groom_rasi_idx=groom.moon_sign_idx,
        bride_rasi_idx=bride.moon_sign_idx,
    )

    return KootaResult(
        koota_id="ASHTA-06",
        name_en="Gana Koota",
        status=res["status"],
        max_points=6.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Gana: {res['groom_gana']} vs Bride Gana: {res['bride_gana']} -> {res['earned_points']:.1f} pts",
        groom_input={"nakshatra": groom.moon_nakshatra_name, "gana": res["groom_gana"]},
        bride_input={"nakshatra": bride.moon_nakshatra_name, "gana": res["bride_gana"]},
        intermediate_calculation={
            "groom_gana": res["groom_gana"],
            "bride_gana": res["bride_gana"],
            "base_points": res["base_points"],
            "is_mitigated": res["is_cancelled"],
        },
        is_dosha_present=res["base_points"] < 5.0,
        is_cancelled=res["is_cancelled"],
        cancellation_reason=res["cancellation_reason"],
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 13–15; BPHS Ch. 81 (v1.0)",
    )


# ===========================================================================
# 7. BHAKOOT KOOTA (ASHTA-07) — 7 POINTS
# ===========================================================================

def calculate_bhakoot_core(groom_rasi_idx: int, bride_rasi_idx: int) -> Dict[str, Any]:
    """Pure calculation for Bhakoot Koota (7 points max) with classical lord cancellations."""
    distance = ((groom_rasi_idx - bride_rasi_idx) % 12) + 1

    g_sign = SIGN_NAMES_EN[groom_rasi_idx]
    b_sign = SIGN_NAMES_EN[bride_rasi_idx]
    g_lord = SIGN_LORDS[groom_rasi_idx]
    b_lord = SIGN_LORDS[bride_rasi_idx]

    # Favorable distances: 1/1, 3/11, 4/10, 7/7
    if distance in (1, 3, 4, 7, 10, 11):
        earned = 7.0
        status = PoruthamStatus.PASS
        is_dosha = False
        is_cancelled = False
        cancellation_reason = None
        desc = (
            f"Favorable Moon sign relationship ({g_sign} is {distance}th from {b_sign}). "
            f"Full 7.0 / 7.0 Bhakoot points awarded. No Bhakoot Dosha."
        )
    else:
        # Inauspicious axes: 2/12, 5/9, 6/8 -> Bhakoot Dosha
        is_dosha = True
        is_cancelled = False
        cancellation_reason = None
        earned = 0.0

        # Check classical cancellations (Muhurta Chintamani Ch. 6 Slokas 18–20):
        # 1. 6/8 Shadashtaka Cancellation: Same lord (Aries & Scorpio; Taurus & Libra)
        if distance in (6, 8) and {groom_rasi_idx, bride_rasi_idx} in ({1, 8}, {2, 7}):
            is_cancelled = True
            earned = 7.0
            cancellation_reason = f"Shadashtaka (6/8) cancelled: both {g_sign} and {b_sign} are ruled by the same planet ({g_lord}) per Muhurta Chintamani."
        # 2. 2/12 Dvidwadasa Cancellation: Same lord (Capricorn & Aquarius)
        elif distance in (2, 12) and {groom_rasi_idx, bride_rasi_idx} == {10, 11}:
            is_cancelled = True
            earned = 7.0
            cancellation_reason = "Dvidwadasa (2/12) cancelled: both Capricorn and Aquarius are ruled by Saturn per Muhurta Chintamani."
        # 3. 2/12 Dvidwadasa Cancellation: Mutual friends (Pisces & Aries)
        elif distance in (2, 12) and {groom_rasi_idx, bride_rasi_idx} == {1, 12}:
            is_cancelled = True
            earned = 7.0
            cancellation_reason = "Dvidwadasa (2/12) cancelled: sign lords Jupiter and Mars are mutual friends per Muhurta Chintamani."
        # 4. 5/9 Navapanchama Cancellation: Mutual friendly lords
        elif distance in (5, 9):
            lords_are_mutual_friends = (
                PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, 0) == 1
                and PLANETARY_NATURAL_FRIENDSHIP.get(b_lord, {}).get(g_lord, 0) == 1
            )
            if lords_are_mutual_friends or {groom_rasi_idx, bride_rasi_idx} in ({1, 5}, {1, 9}, {4, 12}, {5, 9}):
                is_cancelled = True
                earned = 7.0
                cancellation_reason = f"Navapanchama (5/9) cancelled: Moon sign lords {g_lord} and {b_lord} are mutual friends per Muhurta Chintamani."

        if is_cancelled:
            status = PoruthamStatus.PASS
            desc = f"Bhakoot Dosha ({g_sign} - {b_sign}, distance {distance}) is present but CANCELLED: {cancellation_reason} Full 7.0 points awarded."
        else:
            status = PoruthamStatus.FAIL
            desc = f"Active Bhakoot Dosha ({g_sign} - {b_sign}, distance {distance}). 0.0 / 7.0 points awarded."

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 7.0,
        "distance": distance,
        "groom_sign": g_sign,
        "bride_sign": b_sign,
        "is_dosha_present": is_dosha,
        "is_cancelled": is_cancelled,
        "cancellation_reason": cancellation_reason,
        "description": desc,
    }


def evaluate_bhakoot_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Bhakoot Koota (ASHTA-07)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-07",
            name_en="Bhakoot Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=7.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Bhakoot Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 16–20; BPHS Ch. 81 (v1.0)",
        )

    res = calculate_bhakoot_core(groom.moon_sign_idx, bride.moon_sign_idx)

    return KootaResult(
        koota_id="ASHTA-07",
        name_en="Bhakoot Koota",
        status=res["status"],
        max_points=7.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Moon sign distance: {res['distance']} ({res['groom_sign']} from {res['bride_sign']}) -> {res['earned_points']:.1f} pts",
        groom_input={"moon_sign": groom.moon_sign_name, "sign_index": groom.moon_sign_idx},
        bride_input={"moon_sign": bride.moon_sign_name, "sign_index": bride.moon_sign_idx},
        intermediate_calculation={
            "distance": res["distance"],
            "is_dosha": res["is_dosha_present"],
            "is_cancelled": res["is_cancelled"],
        },
        is_dosha_present=res["is_dosha_present"],
        is_cancelled=res["is_cancelled"],
        cancellation_reason=res["cancellation_reason"],
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 16–20; BPHS Ch. 81 (v1.0)",
    )


# ===========================================================================
# 8. NADI KOOTA (ASHTA-08) — 8 POINTS
# ===========================================================================

# Classical Designated Eka Nakshatras for Nadi Dosha cancellation (Muhurta Chintamani Ch. 6 Sloka 25)
NADI_EXEMPT_EKA_NAKSHATRAS: Set[int] = {
    3,   # Rohini
    4,   # Mrigashira
    5,   # Ardra
    7,   # Pushya
    21,  # Shravana
    25,  # Uttara Bhadrapada
}

def calculate_nadi_core(
    groom_star_idx: int,
    bride_star_idx: int,
    groom_pada: int = 1,
    bride_pada: int = 1,
    groom_rasi_idx: int = 1,
    bride_rasi_idx: int = 1,
) -> Dict[str, Any]:
    """Pure calculation for Nadi Koota (8 points max) with classical cancellations."""
    g_nadi = NAKSHATRA_NADI[groom_star_idx]
    b_nadi = NAKSHATRA_NADI[bride_star_idx]

    if g_nadi != b_nadi:
        earned = 8.0
        status = PoruthamStatus.PASS
        is_dosha = False
        is_cancelled = False
        cancellation_reason = None
        desc = (
            f"Different Nadis: Groom is {g_nadi.value} Nadi and Bride is {b_nadi.value} Nadi. "
            "Full 8.0 / 8.0 Nadi points awarded. No Nadi Dosha."
        )
    else:
        # Same Nadi -> Nadi Dosha
        is_dosha = True
        is_cancelled = False
        cancellation_reason = None
        earned = 0.0

        # Classical Nadi Cancellations (Muhurta Chintamani Ch. 6 Slokas 23–25):
        # 1. Same Rasi, Different Nakshatras
        if groom_rasi_idx == bride_rasi_idx and groom_star_idx != bride_star_idx:
            is_cancelled = True
            earned = 8.0
            cancellation_reason = (
                f"Same Moon sign ({SIGN_NAMES_EN[groom_rasi_idx]}) with different Nakshatras "
                f"({NAKSHATRA_NAMES_EN[groom_star_idx]} and {NAKSHATRA_NAMES_EN[bride_star_idx]}) "
                "cancels Nadi Dosha per Muhurta Chintamani Ch. 6 Sloka 23."
            )
        # 2. Same Nakshatra, Different Rasi (Pada crosses sign boundary)
        elif groom_star_idx == bride_star_idx and groom_rasi_idx != bride_rasi_idx:
            is_cancelled = True
            earned = 8.0
            cancellation_reason = (
                f"Same Nakshatra ({NAKSHATRA_NAMES_EN[groom_star_idx]}) with different Moon signs "
                f"({SIGN_NAMES_EN[groom_rasi_idx]} and {SIGN_NAMES_EN[bride_rasi_idx]}) "
                "cancels Nadi Dosha per Muhurta Chintamani Ch. 6 Sloka 24."
            )
        # 3. Designated Eka Nakshatras with distinct Padas
        elif (
            groom_star_idx == bride_star_idx
            and groom_star_idx in NADI_EXEMPT_EKA_NAKSHATRAS
            and groom_pada != bride_pada
        ):
            is_cancelled = True
            earned = 8.0
            cancellation_reason = (
                f"Designated auspicious Eka Nakshatra ({NAKSHATRA_NAMES_EN[groom_star_idx]}) with different Padas "
                f"(Groom Pada {groom_pada}, Bride Pada {bride_pada}) cancels Nadi Dosha per Muhurta Chintamani Ch. 6 Sloka 25."
            )

        if is_cancelled:
            status = PoruthamStatus.PASS
            desc = f"Nadi Dosha ({g_nadi.value} Nadi) is present but CANCELLED: {cancellation_reason} Full 8.0 points awarded."
        else:
            status = PoruthamStatus.FAIL
            desc = f"Active Nadi Dosha ({g_nadi.value} Nadi). 0.0 / 8.0 points awarded. Physiological/genetic disharmony."

    return {
        "status": status,
        "earned_points": earned,
        "max_points": 8.0,
        "groom_nadi": g_nadi.value,
        "bride_nadi": b_nadi.value,
        "is_dosha_present": is_dosha,
        "is_cancelled": is_cancelled,
        "cancellation_reason": cancellation_reason,
        "description": desc,
    }


def evaluate_nadi_koota(groom: MarriageChartContext, bride: MarriageChartContext) -> KootaResult:
    """Evaluate Nadi Koota (ASHTA-08)."""
    if groom is None or bride is None:
        return KootaResult(
            koota_id="ASHTA-08",
            name_en="Nadi Koota",
            status=PoruthamStatus.INDETERMINATE,
            max_points=8.0,
            earned_points=0.0,
            raw_calculation="Missing chart data",
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            description="Incomplete chart data provided for Nadi Koota evaluation.",
            classical_reference="Muhurta Chintamani Ch. 6, Slokas 21–25; BPHS Ch. 81 (v1.0)",
        )

    res = calculate_nadi_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
        groom_pada=groom.moon_nakshatra_pada,
        bride_pada=bride.moon_nakshatra_pada,
        groom_rasi_idx=groom.moon_sign_idx,
        bride_rasi_idx=bride.moon_sign_idx,
    )

    return KootaResult(
        koota_id="ASHTA-08",
        name_en="Nadi Koota",
        status=res["status"],
        max_points=8.0,
        earned_points=res["earned_points"],
        raw_calculation=f"Groom Nadi: {res['groom_nadi']} vs Bride Nadi: {res['bride_nadi']} -> {res['earned_points']:.1f} pts",
        groom_input={"nakshatra": groom.moon_nakshatra_name, "nadi": res["groom_nadi"], "pada": groom.moon_nakshatra_pada},
        bride_input={"nakshatra": bride.moon_nakshatra_name, "nadi": res["bride_nadi"], "pada": bride.moon_nakshatra_pada},
        intermediate_calculation={
            "groom_nadi": res["groom_nadi"],
            "bride_nadi": res["bride_nadi"],
            "is_dosha": res["is_dosha_present"],
            "is_cancelled": res["is_cancelled"],
        },
        is_dosha_present=res["is_dosha_present"],
        is_cancelled=res["is_cancelled"],
        cancellation_reason=res["cancellation_reason"],
        description=res["description"],
        classical_reference="Muhurta Chintamani Ch. 6, Slokas 21–25; BPHS Ch. 81 (v1.0)",
    )
