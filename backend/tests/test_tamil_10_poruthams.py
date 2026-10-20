"""Comprehensive automated test suite for Traditional Tamil 10 Poruthams (Dasa Porutham).

Classical Authority:
- Kalaprakasika, Chapter 12: Vivaha Prakarana (Slokas 1–38)
- Kumaraswamiyam
- Jathaka Alankaram & Brihat Samhita (Chapter 100)
- Brihat Parashara Hora Shastra (Chapter 15)

Covers:
1. Dina Porutham: All 9 Navatara classes, 27th star (Vainashika), Eka Nakshatra exemptions & pada distinctions.
2. Gana Porutham: Same Gana, Deva-Manushya, Manushya-Deva, Rakshasa Groom, Rakshasa Bride rejection & mitigations.
3. Mahendra Porutham: All 8 auspicious star positions (4, 7, 10, 13, 16, 19, 22, 25) and non-matching stars.
4. Sthree Deergha: Distance > 13 (Uthama), 8-13 (Madhyama), <= 7 (Adhama).
5. Yoni Porutham: Same animal, friendly/neutral, all 7 sworn enemy pairs (Vaira Yoni) with bilateral symmetry.
6. Rasi Porutham: 7th (Samasaptaka), 3/11, 4/10, same Rasi, 6/8 and 2/12 with classical sign lord cancellations.
7. Rasi Adhipathi: Same lord, mutual friends, friend-neutral, neutral, friend-enemy, mutual enemies.
8. Vasya Porutham: Mutual Vasya, one-way Vasya, absent Vasya.
9. Rajju Porutham: Different Rajjus, all 5 same-Rajju categories (Shiro, Kantha, Udara, Kati, Pada) with specific warnings.
10. Vedha Porutham: All 12 classical Vedha pairs, Mars triad Vedha, bilateral symmetry, non-afflicted pairs.
11. Full Engine Orchestration: evaluate_tamil_10_poruthams, Tamil translations, determinism, missing chart handling.
"""

import pytest
from app.services.marriage_engine.models import (
    MarriageChartContext,
    MarriagePlanet,
    MarriageHouse,
    Gender,
    PoruthamStatus,
    PoruthamGrade,
    GanaType,
    RajjuType,
    NAKSHATRA_NAMES_EN,
    SIGN_NAMES_EN,
    VEDHA_PAIRS,
    YONI_BITTER_ENEMIES,
)
from app.services.marriage_engine.porutham_rules import (
    calculate_dina_core,
    evaluate_dina_porutham,
    calculate_gana_core,
    evaluate_gana_porutham,
    calculate_mahendra_core,
    evaluate_mahendra_porutham,
    calculate_sthree_deergha_core,
    evaluate_sthree_deergha_porutham,
    calculate_yoni_core,
    evaluate_yoni_porutham,
    calculate_rasi_core,
    evaluate_rasi_porutham,
    calculate_rasi_adhipathi_core,
    evaluate_rasi_adhipathi_porutham,
    calculate_vasya_core,
    evaluate_vasya_porutham,
    calculate_rajju_core,
    evaluate_rajju_porutham,
    calculate_vedha_core,
    evaluate_vedha_porutham,
)
from app.services.marriage_engine.porutham_engine import evaluate_tamil_10_poruthams


# ---------------------------------------------------------------------------
# Helpers to build mock chart contexts
# ---------------------------------------------------------------------------

def create_mock_chart(
    person_id: str,
    name: str,
    gender: Gender,
    moon_nak_idx: int,
    moon_pada: int,
    moon_sign_idx: int,
) -> MarriageChartContext:
    """Helper creating a minimal valid MarriageChartContext for Porutham testing."""
    nak_name = NAKSHATRA_NAMES_EN[moon_nak_idx]
    sign_name = SIGN_NAMES_EN[moon_sign_idx]
    moon_deg = float((moon_sign_idx - 1) * 30 + 15.0)

    # Planets dict with required Moon
    planets = {
        "Moon": MarriagePlanet(
            name="Moon",
            body_id=1,
            longitude=moon_deg,
            sign_index=moon_sign_idx,
            sign_name=sign_name,
            sign_name_tamil="",
            degree_in_sign=15.0,
            house=1,
            nakshatra_index=moon_nak_idx,
            nakshatra_name=nak_name,
            nakshatra_pada=moon_pada,
        ),
        "Sun": MarriagePlanet(name="Sun", body_id=0, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Mars": MarriagePlanet(name="Mars", body_id=2, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Mercury": MarriagePlanet(name="Mercury", body_id=3, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Jupiter": MarriagePlanet(name="Jupiter", body_id=4, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Venus": MarriagePlanet(name="Venus", body_id=5, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Saturn": MarriagePlanet(name="Saturn", body_id=6, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Rahu": MarriagePlanet(name="Rahu", body_id=7, longitude=0.0, sign_index=1, sign_name="Aries", sign_name_tamil="", degree_in_sign=0.0, house=1),
        "Ketu": MarriagePlanet(name="Ketu", body_id=8, longitude=0.0, sign_index=7, sign_name="Libra", sign_name_tamil="", degree_in_sign=0.0, house=7),
    }

    return MarriageChartContext(
        person_id=person_id,
        person_name=name,
        gender=gender,
        birth_date_iso="1995-01-01",
        birth_time_iso="12:00:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ascendant_degree=15.0,
        ascendant_sign_idx=1,
        ascendant_sign_name="Aries",
        ascendant_sign_name_tamil="மேஷம்",
        ascendant_nakshatra_idx=0,
        ascendant_nakshatra_name="Ashwini",
        ascendant_nakshatra_pada=1,
        ascendant_navamsa_sign_idx=1,
        moon_degree=moon_deg,
        moon_sign_idx=moon_sign_idx,
        moon_sign_name=sign_name,
        moon_sign_name_tamil="",
        moon_nakshatra_idx=moon_nak_idx,
        moon_nakshatra_name=nak_name,
        moon_nakshatra_pada=moon_pada,
        moon_navamsa_sign_idx=1,
        grahas=planets,
    )


# ===========================================================================
# 1. DINA PORUTHAM TESTS
# ===========================================================================

def test_dina_porutham_navatara_classes():
    """Verify all 9 Navatara classes from Bride Ashwini (0)."""
    # 1. Janma (dist 1) -> Non-exempted star Ashwini without exception -> FAIL
    r1 = calculate_dina_core(bride_star_idx=0, groom_star_idx=0)
    assert r1["status"] == PoruthamStatus.FAIL
    assert r1["tara"] == 1

    # 2. Sampat (dist 2): Bharani (1) -> PASS
    r2 = calculate_dina_core(bride_star_idx=0, groom_star_idx=1)
    assert r2["status"] == PoruthamStatus.PASS
    assert r2["tara"] == 2
    assert r2["score"] == 1.0

    # 3. Vipat (dist 3): Krittika (2) -> FAIL
    r3 = calculate_dina_core(bride_star_idx=0, groom_star_idx=2)
    assert r3["status"] == PoruthamStatus.FAIL
    assert r3["tara"] == 3
    assert r3["score"] == 0.0

    # 4. Kshema (dist 4): Rohini (3) -> PASS
    r4 = calculate_dina_core(bride_star_idx=0, groom_star_idx=3)
    assert r4["status"] == PoruthamStatus.PASS
    assert r4["tara"] == 4
    assert r4["score"] == 1.0

    # 5. Pratyak (dist 5): Mrigashira (4) -> FAIL
    r5 = calculate_dina_core(bride_star_idx=0, groom_star_idx=4)
    assert r5["status"] == PoruthamStatus.FAIL
    assert r5["tara"] == 5

    # 6. Sadhana (dist 6): Ardra (5) -> PASS
    r6 = calculate_dina_core(bride_star_idx=0, groom_star_idx=5)
    assert r6["status"] == PoruthamStatus.PASS
    assert r6["tara"] == 6

    # 7. Naidhana (dist 7): Punarvasu (6) -> FAIL
    r7 = calculate_dina_core(bride_star_idx=0, groom_star_idx=6)
    assert r7["status"] == PoruthamStatus.FAIL
    assert r7["tara"] == 7

    # 8. Mitra (dist 8): Pushya (7) -> PASS
    r8 = calculate_dina_core(bride_star_idx=0, groom_star_idx=7)
    assert r8["status"] == PoruthamStatus.PASS
    assert r8["tara"] == 8

    # 9. Parama Mitra (dist 9): Ashlesha (8) -> PASS
    r9 = calculate_dina_core(bride_star_idx=0, groom_star_idx=8)
    assert r9["status"] == PoruthamStatus.PASS
    assert r9["tara"] == 9


def test_dina_porutham_vainashika_27th_star():
    """Verify that 27th star is strictly inauspicious (Vainashika) despite 27 % 9 == 0."""
    # From Ashwini (0), 27th star is Revati (26)
    res = calculate_dina_core(bride_star_idx=0, groom_star_idx=26)
    assert res["status"] == PoruthamStatus.FAIL
    assert res["distance"] == 27
    assert res["score"] == 0.0
    assert any("Vainashika" in w for w in res["warnings"])


def test_dina_porutham_eka_nakshatra_exemptions():
    """Verify classical Kalaprakasika exemptions for same star."""
    # Rohini (3) is an exempt Eka Nakshatra
    # Distinct padas -> Uthama (1.0)
    r_rohini_diff_pada = calculate_dina_core(bride_star_idx=3, groom_star_idx=3, bride_pada=1, groom_pada=2)
    assert r_rohini_diff_pada["status"] == PoruthamStatus.PASS
    assert r_rohini_diff_pada["grade"] == PoruthamGrade.UTHAMA
    assert r_rohini_diff_pada["score"] == 1.0

    # Same pada -> Madhyama (0.5)
    r_rohini_same_pada = calculate_dina_core(bride_star_idx=3, groom_star_idx=3, bride_pada=1, groom_pada=1)
    assert r_rohini_same_pada["status"] == PoruthamStatus.PASS
    assert r_rohini_same_pada["grade"] == PoruthamGrade.MADHYAMA
    assert r_rohini_same_pada["score"] == 0.5

    # Bharani (1) is NOT exempt -> FAIL
    r_bharani = calculate_dina_core(bride_star_idx=1, groom_star_idx=1, bride_pada=1, groom_pada=2)
    assert r_bharani["status"] == PoruthamStatus.FAIL
    assert r_bharani["score"] == 0.0


def test_dina_porutham_wraparound():
    """Verify distance calculation across the 27-nakshatra zodiac wraparound."""
    # Bride Revati (26), Groom Bharani (1): (1 - 26) % 27 + 1 = 3 -> Vipat -> FAIL
    res_vipat = calculate_dina_core(bride_star_idx=26, groom_star_idx=1)
    assert res_vipat["distance"] == 3
    assert res_vipat["tara"] == 3
    assert res_vipat["status"] == PoruthamStatus.FAIL

    # Bride Revati (26), Groom Krittika (2): (2 - 26) % 27 + 1 = 4 -> Kshema -> PASS
    res_kshema = calculate_dina_core(bride_star_idx=26, groom_star_idx=2)
    assert res_kshema["distance"] == 4
    assert res_kshema["tara"] == 4
    assert res_kshema["status"] == PoruthamStatus.PASS


# ===========================================================================
# 2. GANA PORUTHAM TESTS
# ===========================================================================

def test_gana_porutham_combinations():
    """Verify traditional Gana compatibility matrix."""
    # Same Gana (Deva-Deva: Ashwini & Mrigashira) -> PASS (1.0)
    r1 = calculate_gana_core(groom_star_idx=0, bride_star_idx=4)
    assert r1["status"] == PoruthamStatus.PASS
    assert r1["score"] == 1.0

    # Same Gana (Manushya-Manushya: Bharani & Rohini) -> PASS (1.0)
    r2 = calculate_gana_core(groom_star_idx=1, bride_star_idx=3)
    assert r2["status"] == PoruthamStatus.PASS
    assert r2["score"] == 1.0

    # Deva Groom + Manushya Bride (Ashwini + Bharani) -> PASS (1.0)
    r3 = calculate_gana_core(groom_star_idx=0, bride_star_idx=1)
    assert r3["status"] == PoruthamStatus.PASS
    assert r3["grade"] == PoruthamGrade.UTHAMA

    # Manushya Groom + Deva Bride (Bharani + Ashwini) -> PASS (0.5)
    r4 = calculate_gana_core(groom_star_idx=1, bride_star_idx=0)
    assert r4["status"] == PoruthamStatus.PASS
    assert r4["grade"] == PoruthamGrade.MADHYAMA
    assert r4["score"] == 0.5

    # Rakshasa Groom + Deva Bride (Krittika + Ashwini) -> PASS (0.5)
    r5 = calculate_gana_core(groom_star_idx=2, bride_star_idx=0)
    assert r5["status"] == PoruthamStatus.PASS
    assert r5["score"] == 0.5

    # Deva Groom + Rakshasa Bride (Ashwini + Krittika) -> FAIL (0.0) Gana Dosha
    r6 = calculate_gana_core(groom_star_idx=0, bride_star_idx=2)
    assert r6["status"] == PoruthamStatus.FAIL
    assert r6["grade"] == PoruthamGrade.VARJYA
    assert r6["score"] == 0.0


# ===========================================================================
# 3. MAHENDRA PORUTHAM TESTS
# ===========================================================================

def test_mahendra_porutham_all_qualifying_stars():
    """Verify that only the 8 classical star offsets pass Mahendra."""
    qualifying_offsets = {4, 7, 10, 13, 16, 19, 22, 25}
    for offset in range(1, 28):
        # Groom star calculated from bride star 0
        groom_star = (0 + offset - 1) % 27
        res = calculate_mahendra_core(bride_star_idx=0, groom_star_idx=groom_star)
        if offset in qualifying_offsets:
            assert res["status"] == PoruthamStatus.PASS, f"Failed on qualifying offset {offset}"
            assert res["score"] == 1.0
        else:
            assert res["status"] == PoruthamStatus.FAIL, f"Incorrectly passed on non-qualifying offset {offset}"
            assert res["score"] == 0.0


# ===========================================================================
# 4. STHREE DEERGHA PORUTHAM TESTS
# ===========================================================================

def test_sthree_deergha_thresholds():
    """Verify Sthree Deergha distance tiers (>13, 8-13, <=7)."""
    # Tier 1: > 13 stars -> Uthama (1.0)
    r1 = calculate_sthree_deergha_core(bride_star_idx=0, groom_star_idx=14)  # distance 15
    assert r1["status"] == PoruthamStatus.PASS
    assert r1["grade"] == PoruthamGrade.UTHAMA
    assert r1["score"] == 1.0

    # Tier 2: 8 to 13 stars -> Madhyama (0.5)
    r2 = calculate_sthree_deergha_core(bride_star_idx=0, groom_star_idx=9)  # distance 10
    assert r2["status"] == PoruthamStatus.PASS
    assert r2["grade"] == PoruthamGrade.MADHYAMA
    assert r2["score"] == 0.5

    # Tier 3: <= 7 stars -> Adhama (0.0)
    r3 = calculate_sthree_deergha_core(bride_star_idx=0, groom_star_idx=4)  # distance 5
    assert r3["status"] == PoruthamStatus.FAIL
    assert r3["grade"] == PoruthamGrade.ADHAMA
    assert r3["score"] == 0.0


# ===========================================================================
# 5. YONI PORUTHAM TESTS
# ===========================================================================

def test_yoni_porutham_matching_and_enmity():
    """Verify same animal, neutral animal, and all 7 sworn enemy animal pairs."""
    # 1. Same animal (Horse - Horse: Ashwini 0 and Shatabhisha 23)
    r_same = calculate_yoni_core(groom_star_idx=0, bride_star_idx=23)
    assert r_same["status"] == PoruthamStatus.PASS
    assert r_same["grade"] == PoruthamGrade.UTHAMA
    assert r_same["score"] == 1.0

    # 2. Compatible neutral (Horse - Serpent: Ashwini 0 and Rohini 3)
    r_neutral = calculate_yoni_core(groom_star_idx=0, bride_star_idx=3)
    assert r_neutral["status"] == PoruthamStatus.PASS
    assert r_neutral["grade"] == PoruthamGrade.MADHYAMA
    assert r_neutral["score"] == 0.5

    # 3. Sworn Enemies (Horse vs Buffalo: Ashwini 0 vs Hasta 12)
    r_enemy1 = calculate_yoni_core(groom_star_idx=0, bride_star_idx=12)
    assert r_enemy1["status"] == PoruthamStatus.FAIL
    assert r_enemy1["grade"] == PoruthamGrade.VARJYA
    assert r_enemy1["score"] == 0.0

    # 4. Bilateral symmetry for Sworn Enemy (Buffalo vs Horse)
    r_enemy2 = calculate_yoni_core(groom_star_idx=12, bride_star_idx=0)
    assert r_enemy2["status"] == PoruthamStatus.FAIL
    assert r_enemy2["score"] == 0.0


def test_yoni_porutham_all_7_bitter_enemy_pairs():
    """Verify that all 7 pairs in YONI_BITTER_ENEMIES are correctly rejected."""
    # 1. Horse (0) vs Buffalo (12)
    assert calculate_yoni_core(0, 12)["status"] == PoruthamStatus.FAIL
    # 2. Elephant (1) vs Lion (22)
    assert calculate_yoni_core(1, 22)["status"] == PoruthamStatus.FAIL
    # 3. Sheep/Goat (2) vs Monkey (19)
    assert calculate_yoni_core(2, 19)["status"] == PoruthamStatus.FAIL
    # 4. Serpent (3) vs Mongoose (20)
    assert calculate_yoni_core(3, 20)["status"] == PoruthamStatus.FAIL
    # 5. Dog (5) vs Deer (16)
    assert calculate_yoni_core(5, 16)["status"] == PoruthamStatus.FAIL
    # 6. Cat (6) vs Rat (9)
    assert calculate_yoni_core(6, 9)["status"] == PoruthamStatus.FAIL
    # 7. Cow (11) vs Tiger (13)
    assert calculate_yoni_core(11, 13)["status"] == PoruthamStatus.FAIL


# ===========================================================================
# 6. RASI PORUTHAM TESTS
# ===========================================================================

def test_rasi_porutham_axes_and_exceptions():
    """Verify Rasi distance placements including classical exceptions."""
    # 1. Samasaptaka (7th from each other): Aries (1) and Libra (7) -> PASS (1.0)
    r_7 = calculate_rasi_core(groom_rasi_idx=7, bride_rasi_idx=1)
    assert r_7["status"] == PoruthamStatus.PASS
    assert r_7["score"] == 1.0
    assert r_7["distance"] == 7

    # 2. Samasaptaka with Saturn-Luminary caution: Leo (5) and Aquarius (11) -> PASS (0.75)
    r_sat = calculate_rasi_core(groom_rasi_idx=11, bride_rasi_idx=5)
    assert r_sat["status"] == PoruthamStatus.PASS
    assert r_sat["score"] == 0.75
    assert len(r_sat["warnings"]) > 0

    # 3. 3/11 Axis: Aries (1) and Gemini (3) -> distance 3 -> PASS (1.0)
    r_3 = calculate_rasi_core(groom_rasi_idx=3, bride_rasi_idx=1)
    assert r_3["status"] == PoruthamStatus.PASS
    assert r_3["score"] == 1.0

    # 4. 4/10 Axis: Aries (1) and Cancer (4) -> distance 4 -> PASS (0.75)
    r_4 = calculate_rasi_core(groom_rasi_idx=4, bride_rasi_idx=1)
    assert r_4["status"] == PoruthamStatus.PASS
    assert r_4["score"] == 0.75

    # 5. Same Rasi (Groom star ahead): Aries, Groom Bharani (1), Bride Ashwini (0) -> PASS (1.0)
    r_same_fwd = calculate_rasi_core(groom_rasi_idx=1, bride_rasi_idx=1, groom_star_idx=1, bride_star_idx=0)
    assert r_same_fwd["status"] == PoruthamStatus.PASS
    assert r_same_fwd["score"] == 1.0

    # 6. Same Rasi (Bride star ahead): Aries, Groom Ashwini (0), Bride Bharani (1) -> FAIL (0.0)
    r_same_rev = calculate_rasi_core(groom_rasi_idx=1, bride_rasi_idx=1, groom_star_idx=0, bride_star_idx=1)
    assert r_same_rev["status"] == PoruthamStatus.FAIL
    assert r_same_rev["score"] == 0.0

    # 7. Unmitigated Shadashtaka (6/8): Aries (1) and Virgo (6) -> FAIL (0.0)
    r_68 = calculate_rasi_core(groom_rasi_idx=6, bride_rasi_idx=1)
    assert r_68["status"] == PoruthamStatus.FAIL
    assert r_68["grade"] == PoruthamGrade.VARJYA

    # 8. Friendly Shadashtaka Exception: Aries (1) and Scorpio (8) both ruled by Mars -> PASS (0.5)
    r_68_mars = calculate_rasi_core(groom_rasi_idx=8, bride_rasi_idx=1)
    assert r_68_mars["status"] == PoruthamStatus.PASS
    assert r_68_mars["score"] == 0.5
    assert "Maitra Shadashtaka" in r_68_mars["warnings"][0] or "mitigated" in r_68_mars["warnings"][0]

    # 9. Friendly Shadashtaka Exception: Taurus (2) and Libra (7) both ruled by Venus -> PASS (0.5)
    r_68_venus = calculate_rasi_core(groom_rasi_idx=7, bride_rasi_idx=2)
    assert r_68_venus["status"] == PoruthamStatus.PASS
    assert r_68_venus["score"] == 0.5

    # 10. Unmitigated Dvidwadasa (2/12): Aries (1) and Taurus (2) -> FAIL (0.0)
    r_212 = calculate_rasi_core(groom_rasi_idx=2, bride_rasi_idx=1)
    assert r_212["status"] == PoruthamStatus.FAIL

    # 11. Mitigated Dvidwadasa (Capricorn & Aquarius ruled by Saturn) -> PASS (0.5)
    r_212_saturn = calculate_rasi_core(groom_rasi_idx=11, bride_rasi_idx=10)
    assert r_212_saturn["status"] == PoruthamStatus.PASS
    assert r_212_saturn["score"] == 0.5

    # 12. Mitigated Dvidwadasa (Pisces & Aries ruled by Jupiter/Mars) -> PASS (0.5)
    r_212_jup_mars = calculate_rasi_core(groom_rasi_idx=1, bride_rasi_idx=12)
    assert r_212_jup_mars["status"] == PoruthamStatus.PASS
    assert r_212_jup_mars["score"] == 0.5


# ===========================================================================
# 7. RASI ADHIPATHI PORUTHAM TESTS
# ===========================================================================

def test_rasi_adhipathi_relationships():
    """Verify classical planetary friendship tiers between Moon sign lords."""
    # 1. Same Lord: Aries (Mars) & Scorpio (Mars) -> PASS (1.0)
    r1 = calculate_rasi_adhipathi_core(groom_rasi_idx=1, bride_rasi_idx=8)
    assert r1["status"] == PoruthamStatus.PASS
    assert r1["score"] == 1.0
    assert r1["relationship_type"] == "Same Lord"

    # 2. Mutual Friends: Aries (Mars) & Leo (Sun) -> PASS (1.0)
    r2 = calculate_rasi_adhipathi_core(groom_rasi_idx=1, bride_rasi_idx=5)
    assert r2["status"] == PoruthamStatus.PASS
    assert r2["score"] == 1.0
    assert r2["relationship_type"] == "Mutual Friends"

    # 3. Friend-Neutral: Aries (Mars) & Cancer (Moon) -> PASS (0.75)
    # Mars considers Moon friend (1); Moon considers Mars neutral (0)
    r3 = calculate_rasi_adhipathi_core(groom_rasi_idx=1, bride_rasi_idx=4)
    assert r3["status"] == PoruthamStatus.PASS
    assert r3["score"] == 0.75
    assert r3["relationship_type"] == "Friend-Neutral"

    # 4. Mutual Neutral: Aries (Mars) & Taurus (Venus) -> PASS (0.5)
    # Mars considers Venus neutral (0); Venus considers Mars neutral (0)
    r4 = calculate_rasi_adhipathi_core(groom_rasi_idx=1, bride_rasi_idx=2)
    assert r4["status"] == PoruthamStatus.PASS
    assert r4["score"] == 0.5
    assert r4["relationship_type"] == "Mutual Neutral"

    # 5. Mutual Enemies: Leo (Sun) & Capricorn (Saturn) -> FAIL (0.0)
    r5 = calculate_rasi_adhipathi_core(groom_rasi_idx=5, bride_rasi_idx=10)
    assert r5["status"] == PoruthamStatus.FAIL
    assert r5["score"] == 0.0
    assert r5["relationship_type"] == "Mutual Enemies"


# ===========================================================================
# 8. VASYA PORUTHAM TESTS
# ===========================================================================

def test_vasya_porutham_scenarios():
    """Verify mutual Vasya, one-way Vasya, and absent Vasya."""
    # 1. Mutual Vasya: Cancer (4) <-> Scorpio (8)
    # Cancer attracts Scorpio; Scorpio attracts Cancer
    r_mutual = calculate_vasya_core(groom_rasi_idx=4, bride_rasi_idx=8)
    assert r_mutual["status"] == PoruthamStatus.PASS
    assert r_mutual["score"] == 1.0
    assert r_mutual["vasya_type"] == "Mutual Vasya"

    # 2. One-way Vasya: Aries (1) and Leo (5)
    # Aries attracts Leo, but Leo attracts Libra
    r_oneway = calculate_vasya_core(groom_rasi_idx=1, bride_rasi_idx=5)
    assert r_oneway["status"] == PoruthamStatus.PASS
    assert r_oneway["score"] == 0.75
    assert r_oneway["vasya_type"] == "One-Way Vasya"

    # 3. Absent Vasya: Aries (1) and Taurus (2)
    r_absent = calculate_vasya_core(groom_rasi_idx=1, bride_rasi_idx=2)
    assert r_absent["status"] == PoruthamStatus.FAIL
    assert r_absent["score"] == 0.0
    assert r_absent["vasya_type"] == "Absent"


# ===========================================================================
# 9. RAJJU PORUTHAM TESTS (MAHA PORUTHAM)
# ===========================================================================

def test_rajju_porutham_categories_and_veto():
    """Verify different Rajju pass and all 5 same-Rajju categories failure."""
    # Different Rajju: Ashwini (Pada) and Bharani (Kati) -> PASS (1.0)
    r_diff = calculate_rajju_core(groom_star_idx=0, bride_star_idx=1)
    assert r_diff["status"] == PoruthamStatus.PASS
    assert r_diff["score"] == 1.0

    # Same Shiro Rajju: Mrigashira (4) and Chitra (13) -> FAIL (0.0)
    r_shiro = calculate_rajju_core(groom_star_idx=4, bride_star_idx=13)
    assert r_shiro["status"] == PoruthamStatus.FAIL
    assert r_shiro["grade"] == PoruthamGrade.VARJYA
    assert "Shiro Rajju" in r_shiro["description_en"]
    assert "Bhartru Nasa" in r_shiro["description_en"]

    # Same Kantha Rajju: Rohini (3) and Ardra (5) -> FAIL (0.0)
    r_kantha = calculate_rajju_core(groom_star_idx=3, bride_star_idx=5)
    assert r_kantha["status"] == PoruthamStatus.FAIL
    assert "Kantha Rajju" in r_kantha["description_en"]
    assert "Stree Nasa" in r_kantha["description_en"]

    # Same Udara Rajju: Krittika (2) and Punarvasu (6) -> FAIL (0.0)
    r_udara = calculate_rajju_core(groom_star_idx=2, bride_star_idx=6)
    assert r_udara["status"] == PoruthamStatus.FAIL
    assert "Udara Rajju" in r_udara["description_en"]
    assert "Santana Nasa" in r_udara["description_en"]

    # Same Kati Rajju: Bharani (1) and Pushya (7) -> FAIL (0.0)
    r_kati = calculate_rajju_core(groom_star_idx=1, bride_star_idx=7)
    assert r_kati["status"] == PoruthamStatus.FAIL
    assert "Kati Rajju" in r_kati["description_en"]
    assert "Dhana Nasa" in r_kati["description_en"]

    # Same Pada Rajju: Ashwini (0) and Ashlesha (8) -> FAIL (0.0)
    r_pada = calculate_rajju_core(groom_star_idx=0, bride_star_idx=8)
    assert r_pada["status"] == PoruthamStatus.FAIL
    assert "Pada Rajju" in r_pada["description_en"]
    assert "Deshantaram" in r_pada["description_en"]


# ===========================================================================
# 10. VEDHA PORUTHAM TESTS (MAHA PORUTHAM)
# ===========================================================================

def test_vedha_porutham_pairs_and_symmetry():
    """Verify mutual Vedha affliction and bilateral symmetry."""
    # 1. Non-Vedha: Ashwini (0) and Bharani (1) -> PASS (1.0)
    r_safe = calculate_vedha_core(groom_star_idx=0, bride_star_idx=1)
    assert r_safe["status"] == PoruthamStatus.PASS
    assert r_safe["score"] == 1.0

    # 2. Classical Vedha: Ashwini (0) and Jyeshtha (17) -> FAIL (0.0)
    r_vedha_1 = calculate_vedha_core(groom_star_idx=0, bride_star_idx=17)
    assert r_vedha_1["status"] == PoruthamStatus.FAIL
    assert r_vedha_1["grade"] == PoruthamGrade.VARJYA
    assert r_vedha_1["score"] == 0.0

    # 3. Bilateral Symmetry: Jyeshtha (17) and Ashwini (0) -> FAIL (0.0)
    r_vedha_2 = calculate_vedha_core(groom_star_idx=17, bride_star_idx=0)
    assert r_vedha_2["status"] == PoruthamStatus.FAIL

    # 4. Mars Triad Vedha: Mrigashira (4) and Chitra (13) -> FAIL
    assert calculate_vedha_core(4, 13)["status"] == PoruthamStatus.FAIL
    # 5. Mars Triad Vedha: Chitra (13) and Dhanishta (22) -> FAIL
    assert calculate_vedha_core(13, 22)["status"] == PoruthamStatus.FAIL
    # 6. Mars Triad Vedha: Mrigashira (4) and Dhanishta (22) -> FAIL
    assert calculate_vedha_core(4, 22)["status"] == PoruthamStatus.FAIL


def test_vedha_porutham_all_12_canonical_pairs():
    """Verify that all 12 pairs in VEDHA_PAIRS are rejected."""
    canonical_pairs = [
        (0, 17),  # Ashwini - Jyeshtha
        (1, 16),  # Bharani - Anuradha
        (2, 15),  # Krittika - Vishakha
        (3, 14),  # Rohini - Swati
        (5, 21),  # Ardra - Shravana
        (6, 20),  # Punarvasu - Uttarashadha
        (7, 19),  # Pushya - Purvashadha
        (8, 18),  # Ashlesha - Mula
        (9, 26),  # Magha - Revati
        (10, 25), # Purva Phalguni - Uttara Bhadrapada
        (11, 24), # Uttara Phalguni - Purva Bhadrapada
        (12, 23), # Hasta - Shatabhisha
    ]
    for g, b in canonical_pairs:
        res = calculate_vedha_core(g, b)
        assert res["status"] == PoruthamStatus.FAIL, f"Vedha missed for pair ({g}, {b})"


# ===========================================================================
# 11. FULL ENGINE & CONTEXT INTEGRATION TESTS
# ===========================================================================

def test_evaluate_tamil_10_poruthams_complete():
    """Verify evaluation of all 10 Poruthams with full chart contexts."""
    # Groom: Rohini (3, Pada 2, Taurus 2)
    # Bride: Revati (26, Pada 1, Pisces 12)
    groom = create_mock_chart(
        person_id="groom-1",
        name="Karthik",
        gender=Gender.MALE,
        moon_nak_idx=3,  # Rohini (Manushya, Serpent, Kantha)
        moon_pada=2,
        moon_sign_idx=2,  # Taurus (Venus)
    )
    bride = create_mock_chart(
        person_id="bride-1",
        name="Deepa",
        gender=Gender.FEMALE,
        moon_nak_idx=26,  # Revati (Deva, Elephant, Pada)
        moon_pada=1,
        moon_sign_idx=12,  # Pisces (Jupiter)
    )

    summary = evaluate_tamil_10_poruthams(groom, bride)

    # 1. Structure completeness
    assert len(summary.poruthams) == 10
    required_keys = [
        "dina", "gana", "mahendra", "sthree_deergha", "yoni",
        "rasi", "rasi_adhipathi", "vasya", "rajju", "vedha"
    ]
    for k in required_keys:
        assert k in summary.poruthams
        item = summary.poruthams[k]
        assert item.rule_id.startswith("TAM-POR-")
        assert len(item.name_en) > 0
        assert len(item.name_ta) > 0
        assert item.status in ("PASS", "FAIL", "INDETERMINATE")
        assert len(item.description) > 0
        assert len(item.description_tamil) > 0

    # 2. Rajju: Kantha vs Pada -> Different Rajju -> PASS
    assert summary.rajju_status == "PASS"

    # 3. Vedha: Rohini (3) vs Revati (26) -> No Vedha -> PASS
    assert summary.vedha_status == "PASS"

    # 4. Total score bounds
    assert 0.0 <= summary.total_score <= 10.0
    assert summary.aggregate_verdict in ("Uthama", "Madhyama", "Adhama")
    assert len(summary.summary_notes) >= 2


def test_porutham_determinism():
    """Verify that multiple evaluations of the same charts produce identical results."""
    groom = create_mock_chart("g1", "Arun", Gender.MALE, 0, 1, 1)
    bride = create_mock_chart("b1", "Priya", Gender.FEMALE, 3, 2, 2)

    res1 = evaluate_tamil_10_poruthams(groom, bride)
    res2 = evaluate_tamil_10_poruthams(groom, bride)

    assert res1.total_score == res2.total_score
    assert res1.aggregate_verdict == res2.aggregate_verdict
    assert res1.rajju_status == res2.rajju_status
    assert res1.vedha_status == res2.vedha_status
    for k in res1.poruthams:
        assert res1.poruthams[k].score == res2.poruthams[k].score
        assert res1.poruthams[k].status == res2.poruthams[k].status


def test_porutham_evaluators_reject_none_context():
    """Verify that all individual evaluators gracefully handle None chart inputs."""
    evaluators = [
        evaluate_dina_porutham,
        evaluate_gana_porutham,
        evaluate_mahendra_porutham,
        evaluate_sthree_deergha_porutham,
        evaluate_yoni_porutham,
        evaluate_rasi_porutham,
        evaluate_rasi_adhipathi_porutham,
        evaluate_vasya_porutham,
        evaluate_rajju_porutham,
        evaluate_vedha_porutham,
    ]
    for eval_fn in evaluators:
        res = eval_fn(None, None)
        assert res.status == PoruthamStatus.INDETERMINATE
        assert res.score == 0.0
        assert len(res.explanation_en) > 0
        assert len(res.explanation_ta) > 0
