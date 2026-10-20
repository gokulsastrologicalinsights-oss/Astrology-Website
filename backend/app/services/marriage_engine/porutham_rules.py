"""Independent deterministic evaluators for the Traditional Tamil 10 Poruthams (Dasa Porutham).

Classical Authority:
- Kalaprakasika, Chapter 12: Vivaha Prakarana (Slokas 1–38)
- Kumaraswamiyam (Traditional Tamil Astrological Canon)
- Jathaka Alankaram & Brihat Samhita (Chapter 100)
- Brihat Parashara Hora Shastra (Chapter 15: Naisargika Sambandha)

Rules Evaluated:
1. Dina Porutham (TAM-POR-01): Health, vitality, and longevity via Tara Bala count.
2. Gana Porutham (TAM-POR-02): Temperament and psychological harmony.
3. Mahendra Porutham (TAM-POR-03): Progeny, lineage growth, and family blessing.
4. Sthree Deergha Porutham (TAM-POR-04): Longevity, wealth, and auspiciousness for bride.
5. Yoni Porutham (TAM-POR-05): Biological harmony, mutual attraction, and intimacy.
6. Rasi Porutham (TAM-POR-06): Lineage stability, domestic bliss, and family harmony.
7. Rasi Adhipathi Porutham (TAM-POR-07): Friendship between Moon sign lords.
8. Vasya Porutham (TAM-POR-08): Mutual magnetic attraction and devotion.
9. Rajju Porutham (TAM-POR-09): Vital life-cord / Mangalya protection (Maha Porutham).
10. Vedha Porutham (TAM-POR-10): Repulsion and psychic affliction check (Maha Porutham).
"""

from typing import Dict, Any, List, Optional, Tuple, Set

from app.services.marriage_engine.models import (
    MarriageChartContext,
    PoruthamResult,
    PoruthamStatus,
    PoruthamGrade,
    GanaType,
    RajjuType,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    NAKSHATRA_GANA,
    NAKSHATRA_RAJJU,
    NAKSHATRA_YONI_ANIMAL,
    YONI_BITTER_ENEMIES,
    VEDHA_PAIRS,
    PLANETARY_NATURAL_FRIENDSHIP,
    TAMIL_VASYA_MAP,
    EKA_NAKSHATRA_AUSPICIOUS,
)

# Canonical 9 Navatara Names
NAVATARA_NAMES_EN: Dict[int, str] = {
    1: "Janma",
    2: "Sampat",
    3: "Vipat",
    4: "Kshema",
    5: "Pratyak",
    6: "Sadhana",
    7: "Naidhana",
    8: "Mitra",
    9: "Parama Mitra",
}

NAVATARA_NAMES_TA: Dict[int, str] = {
    1: "ஜென்மம்",
    2: "சம்பத்து",
    3: "விபத்து",
    4: "க்ஷேமம்",
    5: "ப்ரத்யக்கு",
    6: "சாதனம்",
    7: "நைதனம் (வதம்)",
    8: "மித்ரம்",
    9: "பரம மித்ரம்",
}

# Animal Names in Tamil
ANIMAL_NAMES_TA: Dict[str, str] = {
    "Horse": "குதிரை",
    "Elephant": "யானை",
    "Sheep": "ஆடு",
    "Serpent": "பாம்பு",
    "Dog": "நாய்",
    "Cat": "பூனை",
    "Rat": "எலி",
    "Cow": "பசு/மாடு",
    "Buffalo": "எருமை",
    "Tiger": "புலி",
    "Deer": "மான்",
    "Monkey": "குரங்கு",
    "Mongoose": "கீரி",
    "Lion": "சிங்கம்",
}

# Rajju Names in Tamil
RAJJU_NAMES_TA: Dict[RajjuType, str] = {
    RajjuType.SHIRO: "சிரசு ரஜ்ஜு (தலை)",
    RajjuType.KANTHA: "கண்ட ரஜ்ஜு (கழுத்து)",
    RajjuType.UDARA: "உதர ரஜ்ஜு (வயிறு)",
    RajjuType.KATI: "கடி ரஜ்ஜு (இடை)",
    RajjuType.PADA: "பாத ரஜ்ஜு (கால்)",
}

# Gana Names in Tamil
GANA_NAMES_TA: Dict[GanaType, str] = {
    GanaType.DEVA: "தேவ கணம்",
    GanaType.MANUSHYA: "மனுஷ கணம்",
    GanaType.RAKSHASA: "ராட்சஸ கணம்",
}


# ===========================================================================
# 1. DINA PORUTHAM (TAM-POR-01)
# ===========================================================================

def calculate_dina_core(
    bride_star_idx: int,
    groom_star_idx: int,
    bride_pada: int = 1,
    groom_pada: int = 1,
) -> Dict[str, Any]:
    """Pure calculation for Dina Porutham (Tara Bala count from Bride to Groom)."""
    # Count from Bride's star (inclusive: 1 to 27)
    distance = ((groom_star_idx - bride_star_idx) % 27) + 1
    tara = distance % 9
    if tara == 0:
        tara = 9

    tara_name_en = NAVATARA_NAMES_EN[tara]
    tara_name_ta = NAVATARA_NAMES_TA[tara]

    warnings: List[str] = []
    is_favorable = False
    grade = PoruthamGrade.ADHAMA
    score = 0.0
    status = PoruthamStatus.FAIL

    if distance == 27:
        # Vainashika star
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.ADHAMA
        score = 0.0
        is_favorable = False
        warnings.append("The 27th star from the Bride's star is Vainashika (destruction) and is classified as inauspicious.")
        desc_en = (
            f"Groom star {NAKSHATRA_NAMES_EN[groom_star_idx]} is the 27th star from Bride star "
            f"{NAKSHATRA_NAMES_EN[bride_star_idx]} (Vainashika). Dina Porutham is unfavorable."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் 27-வது நட்சத்திரமாக (வைநாசிகம்) "
            f"வருவதால் தினப் பொருத்தம் அமையவில்லை."
        )
    elif distance == 1:
        # Eka Nakshatra (Same Nakshatra)
        if bride_star_idx in EKA_NAKSHATRA_AUSPICIOUS:
            if groom_pada != bride_pada:
                status = PoruthamStatus.PASS
                grade = PoruthamGrade.UTHAMA
                score = 1.0
                is_favorable = True
                desc_en = (
                    f"Both share the auspicious Eka Nakshatra {NAKSHATRA_NAMES_EN[bride_star_idx]} "
                    f"with distinct Padas (Groom Pada {groom_pada}, Bride Pada {bride_pada}). Permitted under classical Kalaprakasika exception."
                )
                desc_ta = (
                    f"இருவரும் உத்தம ஏக நட்சத்திரமான {NAKSHATRA_NAMES_TA[bride_star_idx]} நட்சத்திரத்தில் "
                    f"வெவ்வேறு பாதங்களில் (மணமகன் பாதம் {groom_pada}, மணமகள் பாதம் {bride_pada}) அமைந்துள்ளதால் தினப் பொருத்தம் உத்தமம்."
                )
            else:
                status = PoruthamStatus.PASS
                grade = PoruthamGrade.MADHYAMA
                score = 0.5
                is_favorable = True
                warnings.append("Same Nakshatra and same Pada (Eka Pada) requires evaluation of other primary Poruthams.")
                desc_en = (
                    f"Both share the auspicious Eka Nakshatra {NAKSHATRA_NAMES_EN[bride_star_idx]} "
                    f"in the same Pada {groom_pada}. Classified as Madhyama."
                )
                desc_ta = (
                    f"இருவரும் ஏக நட்சத்திரமான {NAKSHATRA_NAMES_TA[bride_star_idx]} ஒரே பாதத்தில் "
                    f"({groom_pada}) அமைந்துள்ளதால் தினப் பொருத்தம் மத்திமம்."
                )
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            warnings.append("Same Nakshatra (Eka Nakshatra) is not among the 8 classically permitted stars.")
            desc_en = (
                f"Both share Janma Nakshatra {NAKSHATRA_NAMES_EN[bride_star_idx]}, which is not among "
                f"the 8 exempted Eka Nakshatras in classical tradition. Dina Porutham is unfavorable."
            )
            desc_ta = (
                f"இருவருக்கும் ஒரே நட்சத்திரமாக ({NAKSHATRA_NAMES_TA[bride_star_idx]}) அமைந்திருப்பது "
                f"மரபுப்படி தினப் பொருத்தக் குறைபாடாகும்."
            )
    else:
        # Standard Tara check: 2, 4, 6, 8, 9 are auspicious
        if tara in (2, 4, 6, 8, 9):
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.UTHAMA
            score = 1.0
            is_favorable = True
            desc_en = (
                f"Distance from {NAKSHATRA_NAMES_EN[bride_star_idx]} to {NAKSHATRA_NAMES_EN[groom_star_idx]} "
                f"is {distance} stars ({tara_name_en} Tara, {tara}/9). Dina Porutham is favorable, conferring vitality, health, and mutual longevity."
            )
            desc_ta = (
                f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance}-வது நட்சத்திரமாக "
                f"({tara_name_ta} தாரை) அமைவதால் தினப் பொருத்தம் உத்தமம். தம்பதியரின் ஆரோக்கியம் மற்றும் ஆயுளைக் காக்கும்."
            )
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            desc_en = (
                f"Distance from {NAKSHATRA_NAMES_EN[bride_star_idx]} to {NAKSHATRA_NAMES_EN[groom_star_idx]} "
                f"is {distance} stars ({tara_name_en} Tara, {tara}/9). Dina Porutham is unfavorable."
            )
            desc_ta = (
                f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance}-வது நட்சத்திரமாக "
                f"({tara_name_ta} தாரை) அமைவதால் தினப் பொருத்தம் அமையவில்லை."
            )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "distance": distance,
        "tara": tara,
        "tara_name_en": tara_name_en,
        "tara_name_ta": tara_name_ta,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_dina_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Dina Porutham (TAM-POR-01) from groom and bride chart contexts."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-01",
            name_en="Dina Porutham",
            name_ta="தினப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bride to Groom",
            applied_acceptance_criteria="Tara count modulo 9 in {2, 4, 6, 8, 9} excluding 27th star (Vainashika)",
            source_and_version="Kalaprakasika Ch. 12, Slokas 1–6 (v1.0)",
            explanation_en="Incomplete chart data provided for Dina Porutham evaluation.",
            explanation_ta="தினப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_dina_core(
        bride_star_idx=bride.moon_nakshatra_idx,
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_pada=bride.moon_nakshatra_pada,
        groom_pada=groom.moon_nakshatra_pada,
    )

    return PoruthamResult(
        rule_id="TAM-POR-01",
        name_en="Dina Porutham",
        name_ta="தினப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
            "nakshatra_pada": groom.moon_nakshatra_pada,
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
            "nakshatra_pada": bride.moon_nakshatra_pada,
        },
        intermediate_calculation={
            "counting_distance": res["distance"],
            "tara_number": res["tara"],
            "tara_name": res["tara_name_en"],
            "tara_name_tamil": res["tara_name_ta"],
        },
        counting_direction="Bride Nakshatra to Groom Nakshatra (inclusive count)",
        applied_acceptance_criteria="Tara count modulo 9 in {2, 4, 6, 8, 9} excluding 27th star (Vainashika), with Eka Nakshatra exemptions",
        source_and_version="Kalaprakasika Ch. 12, Slokas 1–6 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 2. GANA PORUTHAM (TAM-POR-02)
# ===========================================================================

def calculate_gana_core(
    groom_star_idx: int,
    bride_star_idx: int,
    distance_stars: Optional[int] = None,
    rasi_lords_friendly: bool = False,
    rasi_samasaptaka: bool = False,
) -> Dict[str, Any]:
    """Pure calculation for Gana Porutham."""
    groom_gana = NAKSHATRA_GANA[groom_star_idx]
    bride_gana = NAKSHATRA_GANA[bride_star_idx]

    groom_gana_ta = GANA_NAMES_TA[groom_gana]
    bride_gana_ta = GANA_NAMES_TA[bride_gana]

    warnings: List[str] = []
    dist = distance_stars if distance_stars is not None else (((groom_star_idx - bride_star_idx) % 27) + 1)

    if groom_gana == bride_gana:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Both Groom and Bride belong to the same Gana ({groom_gana.value}). "
            f"Temperamental harmony, psychological alignment, and domestic concord are excellent."
        )
        desc_ta = (
            f"இருவரும் ஒரே கணத்தில் ({groom_gana_ta}) அமைந்துள்ளதால் கணப் பொருத்தம் உத்தமம். "
            f"மன ஒற்றுமையும் இணக்கமும் சிறப்பாக அமையும்."
        )
    elif groom_gana == GanaType.DEVA and bride_gana == GanaType.MANUSHYA:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            "Groom is Deva Gana and Bride is Manushya Gana. Highly favorable temperamental concord; "
            "the divine qualities of the groom harmonize smoothly with the human temperament of the bride."
        )
        desc_ta = "மணமகன் தேவ கணம், மணமகள் மனுஷ கணம். கணப் பொருத்தம் உத்தமம். குடும்ப ஒற்றுமை சிறக்கும்."
    elif groom_gana == GanaType.MANUSHYA and bride_gana == GanaType.DEVA:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.5
        is_favorable = True
        desc_en = (
            "Groom is Manushya Gana and Bride is Deva Gana. Classified as Madhyama in traditional Tamil matching; "
            "acceptable psychological concord with occasional mutual adjustments."
        )
        desc_ta = "மணமகன் மனுஷ கணம், மணமகள் தேவ கணம். கணப் பொருத்தம் மத்திமம். சுமாரான இணக்கம் இருக்கும்."
    elif groom_gana == GanaType.RAKSHASA and bride_gana in (GanaType.DEVA, GanaType.MANUSHYA):
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.5
        is_favorable = True
        desc_en = (
            f"Groom is Rakshasa Gana and Bride is {bride_gana.value} Gana. Classified as Madhyama in Tamil tradition "
            f"when groom carries fierce energy and bride possesses adaptable temperament."
        )
        desc_ta = f"மணமகன் ராட்சஸ கணம், மணமகள் {bride_gana_ta}. கணப் பொருத்தம் மத்திமம்."
    else:
        # Bride is Rakshasa and Groom is Deva or Manushya -> Gana Dosha
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.VARJYA
        score = 0.0
        is_favorable = False
        desc_en = (
            f"Bride is Rakshasa Gana while Groom is {groom_gana.value} Gana. Strictly rejected in classical Tamil matching "
            f"(Gana Dosha), as it portends sharp temperamental friction and emotional discord."
        )
        desc_ta = (
            f"மணமகள் ராட்சஸ கணமாகவும் மணமகன் {groom_gana_ta}மாகவும் அமைவது மரபுப்படி கணப் பொருத்தக் குறைபாடாகும் "
            f"(கண தோஷம்). கருத்து வேறுபாடுகளுக்கு வாய்ப்புள்ளது."
        )
        if rasi_lords_friendly or rasi_samasaptaka or dist > 14:
            warnings.append(
                "Gana defect is partially mitigated by favorable Rasi/Lord alignment or star distance > 14, "
                "but classical Tamil matching maintains caution for Rakshasa bride with Deva/Manushya groom."
            )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "groom_gana": groom_gana.value,
        "bride_gana": bride_gana.value,
        "groom_gana_ta": groom_gana_ta,
        "bride_gana_ta": bride_gana_ta,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_gana_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Gana Porutham (TAM-POR-02)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-02",
            name_en="Gana Porutham",
            name_ta="கணப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Mutual Gana Alignment",
            applied_acceptance_criteria="Same Gana or Deva Groom + Manushya Bride; Rakshasa Bride forbidden",
            source_and_version="Kalaprakasika Ch. 12, Slokas 7–12; Muhurta Chintamani (v1.0)",
            explanation_en="Incomplete chart data provided for Gana Porutham evaluation.",
            explanation_ta="கணப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    g_lord = SIGN_LORDS.get(groom.moon_sign_idx, "")
    b_lord = SIGN_LORDS.get(bride.moon_sign_idx, "")
    friendly = False
    if g_lord and b_lord:
        friendly = (g_lord == b_lord) or (PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, -1) >= 0)
    samasaptaka = (((groom.moon_sign_idx - bride.moon_sign_idx) % 12) + 1) == 7

    res = calculate_gana_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
        rasi_lords_friendly=friendly,
        rasi_samasaptaka=samasaptaka,
    )

    return PoruthamResult(
        rule_id="TAM-POR-02",
        name_en="Gana Porutham",
        name_ta="கணப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
            "gana": res["groom_gana"],
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
            "gana": res["bride_gana"],
        },
        intermediate_calculation={
            "groom_gana": res["groom_gana"],
            "bride_gana": res["bride_gana"],
            "groom_gana_tamil": res["groom_gana_ta"],
            "bride_gana_tamil": res["bride_gana_ta"],
        },
        counting_direction="Mutual / Bidirectional Gana alignment",
        applied_acceptance_criteria="Same Gana or Deva Groom + Manushya Bride; Rakshasa Bride forbidden per Kalaprakasika",
        source_and_version="Kalaprakasika Ch. 12, Slokas 7–12; Muhurta Chintamani (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 3. MAHENDRA PORUTHAM (TAM-POR-03)
# ===========================================================================

MAHENDRA_STARS_SET: Set[int] = {4, 7, 10, 13, 16, 19, 22, 25}

def calculate_mahendra_core(
    bride_star_idx: int,
    groom_star_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Mahendra Porutham."""
    distance = ((groom_star_idx - bride_star_idx) % 27) + 1
    is_present = distance in MAHENDRA_STARS_SET

    if is_present:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Groom star {NAKSHATRA_NAMES_EN[groom_star_idx]} is the {distance}th star from Bride star "
            f"{NAKSHATRA_NAMES_EN[bride_star_idx]}. Mahendra Porutham is fully present, conferring progeny, "
            f"lineage prosperity, and family well-being (Putra Pautra Vriddhi)."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance}-வது நட்சத்திரமாக வருவதால் "
            f"மகேந்திரப் பொருத்தம் உத்தமம். புத்திர பாக்கியம், வம்ச விருத்தி மற்றும் குடும்ப நல்வாழ்வை அருளும்."
        )
    else:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.ADHAMA
        score = 0.0
        is_favorable = False
        desc_en = (
            f"Groom star {NAKSHATRA_NAMES_EN[groom_star_idx]} is the {distance}th star from Bride star "
            f"{NAKSHATRA_NAMES_EN[bride_star_idx]} (not in the auspicious set [4, 7, 10, 13, 16, 19, 22, 25]). "
            f"Mahendra Porutham is absent. Note: Mahendra is a secondary Porutham; its absence does not veto marriage."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance}-வது நட்சத்திரமாக அமைவதால் "
            f"மகேந்திரப் பொருத்தம் அமையவில்லை. (இது இரண்டாம் நிலை பொருத்தம்; ரஜ்ஜு, ராசி பொருத்தம் இருப்பின் விவாகம் செய்யலாம்)."
        )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "distance": distance,
        "is_present": is_present,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_mahendra_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Mahendra Porutham (TAM-POR-03)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-03",
            name_en="Mahendra Porutham",
            name_ta="மகேந்திரப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bride to Groom",
            applied_acceptance_criteria="Groom star is 4th, 7th, 10th, 13th, 16th, 19th, 22nd, or 25th from Bride star",
            source_and_version="Kalaprakasika Ch. 12, Slokas 13–15 (v1.0)",
            explanation_en="Incomplete chart data provided for Mahendra Porutham evaluation.",
            explanation_ta="மகேந்திரப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_mahendra_core(
        bride_star_idx=bride.moon_nakshatra_idx,
        groom_star_idx=groom.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-03",
        name_en="Mahendra Porutham",
        name_ta="மகேந்திரப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
        },
        intermediate_calculation={
            "counting_distance": res["distance"],
            "is_in_mahendra_set": res["is_present"],
            "eligible_stars": sorted(list(MAHENDRA_STARS_SET)),
        },
        counting_direction="Bride Nakshatra to Groom Nakshatra (inclusive count)",
        applied_acceptance_criteria="Groom star is 4th, 7th, 10th, 13th, 16th, 19th, 22nd, or 25th from Bride star",
        source_and_version="Kalaprakasika Ch. 12, Slokas 13–15 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=[],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 4. STHREE DEERGHA PORUTHAM (TAM-POR-04)
# ===========================================================================

def calculate_sthree_deergha_core(
    bride_star_idx: int,
    groom_star_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Sthree Deergha Porutham."""
    distance = ((groom_star_idx - bride_star_idx) % 27) + 1

    if distance > 13:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Distance from Bride star {NAKSHATRA_NAMES_EN[bride_star_idx]} to Groom star "
            f"{NAKSHATRA_NAMES_EN[groom_star_idx]} is {distance} nakshatras (> 13). Sthree Deergha Porutham is Uthama, "
            f"conferring long married life, health, and prosperity for the wife."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance} நட்சத்திரங்கள் இடைவெளியில் (13-க்கு மேல்) "
            f"அமைவதால் ஸ்திரீ தீர்க்கப் பொருத்தம் உத்தமம். மணப்பெண்ணுக்கு தீர்க்க சுமங்கலி பாக்கியம் மற்றும் சகல ஐஸ்வர்யங்களையும் தரும்."
        )
    elif 8 <= distance <= 13:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.5
        is_favorable = True
        desc_en = (
            f"Distance from Bride star {NAKSHATRA_NAMES_EN[bride_star_idx]} to Groom star "
            f"{NAKSHATRA_NAMES_EN[groom_star_idx]} is {distance} nakshatras (between 8 and 13). "
            f"Sthree Deergha Porutham is Madhyama (acceptable)."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance} நட்சத்திரங்கள் இடைவெளியில் (8 முதல் 13 வரை) "
            f"அமைவதால் ஸ்திரீ தீர்க்கப் பொருத்தம் மத்திமம்."
        )
    else:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.ADHAMA
        score = 0.0
        is_favorable = False
        desc_en = (
            f"Distance from Bride star {NAKSHATRA_NAMES_EN[bride_star_idx]} to Groom star "
            f"{NAKSHATRA_NAMES_EN[groom_star_idx]} is {distance} nakshatras (<= 7). "
            f"Sthree Deergha Porutham is unfavorable (too close to Bride's star)."
        )
        desc_ta = (
            f"மணமகள் நட்சத்திரத்திலிருந்து மணமகன் நட்சத்திரம் {distance} நட்சத்திரங்கள் இடைவெளியில் (7-க்குள்) "
            f"மிக அருகில் அமைவதால் ஸ்திரீ தீர்க்கப் பொருத்தம் அமையவில்லை."
        )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "distance": distance,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_sthree_deergha_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Sthree Deergha Porutham (TAM-POR-04)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-04",
            name_en="Sthree Deergha Porutham",
            name_ta="ஸ்திரீ தீர்க்கப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bride to Groom",
            applied_acceptance_criteria="Groom star distance > 13 is Uthama, 8 to 13 is Madhyama, <= 7 is Adhama",
            source_and_version="Kalaprakasika Ch. 12, Sloka 16 (v1.0)",
            explanation_en="Incomplete chart data provided for Sthree Deergha Porutham evaluation.",
            explanation_ta="ஸ்திரீ தீர்க்கப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_sthree_deergha_core(
        bride_star_idx=bride.moon_nakshatra_idx,
        groom_star_idx=groom.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-04",
        name_en="Sthree Deergha Porutham",
        name_ta="ஸ்திரீ தீர்க்கப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
        },
        intermediate_calculation={
            "counting_distance": res["distance"],
            "threshold_tier": "Uthama (>13)" if res["distance"] > 13 else ("Madhyama (8-13)" if res["distance"] >= 8 else "Adhama (<=7)"),
        },
        counting_direction="Bride Nakshatra to Groom Nakshatra (inclusive count)",
        applied_acceptance_criteria="Distance > 13: Uthama (1.0 pt), 8-13: Madhyama (0.5 pt), <= 7: Adhama (0.0 pt)",
        source_and_version="Kalaprakasika Ch. 12, Sloka 16 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=[],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 5. YONI PORUTHAM (TAM-POR-05)
# ===========================================================================

def calculate_yoni_core(
    groom_star_idx: int,
    bride_star_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Yoni Porutham."""
    groom_animal = NAKSHATRA_YONI_ANIMAL[groom_star_idx]
    bride_animal = NAKSHATRA_YONI_ANIMAL[bride_star_idx]

    groom_animal_ta = ANIMAL_NAMES_TA.get(groom_animal, groom_animal)
    bride_animal_ta = ANIMAL_NAMES_TA.get(bride_animal, bride_animal)

    warnings: List[str] = []

    if (groom_animal, bride_animal) in YONI_BITTER_ENEMIES:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.VARJYA
        score = 0.0
        is_favorable = False
        warnings.append(f"Mortal animal enmity detected between {groom_animal} and {bride_animal} (Vaira Yoni).")
        desc_en = (
            f"Groom Yoni is {groom_animal} and Bride Yoni is {bride_animal}, which form a sworn inimical pair "
            f"(Vaira Yoni). Yoni Porutham is strictly afflicted, causing severe physical and biological friction."
        )
        desc_ta = (
            f"மணமகன் யோனி {groom_animal_ta}, மணமகள் யோனி {bride_animal_ta}. இரண்டும் பரஸ்பர விரோத (வைர) "
            f"யோனிகளாக அமைவதால் யோனிப் பொருத்தம் அமையவில்லை. தாம்பத்திய உறவில் கருத்து வேறுபாடுகளை உண்டாக்கலாம்."
        )
    elif groom_animal == bride_animal:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Both Groom and Bride share the same Yoni animal ({groom_animal}). "
            f"Yoni Porutham is Uthama, conferring biological concord, physical harmony, and deep mutual affection."
        )
        desc_ta = (
            f"இருவரும் ஒரே யோனி மிருகத்தை ({groom_animal_ta}) கொண்டுள்ளதால் யோனிப் பொருத்தம் உத்தமம். "
            f"தாம்பத்திய சுகம், உடல் இணக்கம் மற்றும் அன்யோன்யம் சிறக்கும்."
        )
    else:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.5
        is_favorable = True
        desc_en = (
            f"Groom Yoni is {groom_animal} and Bride Yoni is {bride_animal}. Neither identical nor bitter enemies; "
            f"classified as Madhyama (compatible animal archetypes)."
        )
        desc_ta = (
            f"மணமகன் யோனி {groom_animal_ta}, மணமகள் யோனி {bride_animal_ta}. பகை யோனி இல்லாததால் யோனிப் பொருத்தம் மத்திமமாக அமைகிறது."
        )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "groom_animal": groom_animal,
        "bride_animal": bride_animal,
        "groom_animal_ta": groom_animal_ta,
        "bride_animal_ta": bride_animal_ta,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_yoni_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Yoni Porutham (TAM-POR-05)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-05",
            name_en="Yoni Porutham",
            name_ta="யோனிப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Mutual Animal Archetype Alignment",
            applied_acceptance_criteria="Same animal is Uthama, non-inimical is Madhyama, 7 sworn inimical pairs are Varjya",
            source_and_version="Kalaprakasika Ch. 12; Brihat Samhita Ch. 100 (v1.0)",
            explanation_en="Incomplete chart data provided for Yoni Porutham evaluation.",
            explanation_ta="யோனிப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_yoni_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-05",
        name_en="Yoni Porutham",
        name_ta="யோனிப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
            "yoni_animal": res["groom_animal"],
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
            "yoni_animal": res["bride_animal"],
        },
        intermediate_calculation={
            "groom_animal": res["groom_animal"],
            "bride_animal": res["bride_animal"],
            "groom_animal_tamil": res["groom_animal_ta"],
            "bride_animal_tamil": res["bride_animal_ta"],
            "is_bitter_enemy_pair": (res["groom_animal"], res["bride_animal"]) in YONI_BITTER_ENEMIES,
        },
        counting_direction="Mutual / Bidirectional Animal Archetype alignment",
        applied_acceptance_criteria="Same animal is Uthama (1.0 pt), non-inimical is Madhyama (0.5 pt), sworn enemy pairs are Varjya (0.0 pt)",
        source_and_version="Kalaprakasika Ch. 12; Brihat Samhita Ch. 100 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 6. RASI PORUTHAM (TAM-POR-06)
# ===========================================================================

def calculate_rasi_core(
    groom_rasi_idx: int,
    bride_rasi_idx: int,
    groom_star_idx: int = 0,
    bride_star_idx: int = 0,
) -> Dict[str, Any]:
    """Pure calculation for Rasi Porutham (Moon sign distance from Bride to Groom)."""
    # Count inclusive from Bride's Rasi (1 to 12)
    distance = ((groom_rasi_idx - bride_rasi_idx) % 12) + 1

    groom_sign_en = SIGN_NAMES_EN[groom_rasi_idx]
    bride_sign_en = SIGN_NAMES_EN[bride_rasi_idx]
    groom_sign_ta = SIGN_NAMES_TA[groom_rasi_idx]
    bride_sign_ta = SIGN_NAMES_TA[bride_rasi_idx]

    warnings: List[str] = []
    g_lord = SIGN_LORDS[groom_rasi_idx]
    b_lord = SIGN_LORDS[bride_rasi_idx]
    lords_are_friends = (g_lord == b_lord) or (PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, -1) >= 0)

    if distance == 7:
        # Samasaptaka (7th from each other)
        # Cancer (4) - Capricorn (10) and Leo (5) - Aquarius (11) have Saturn vs Sun/Moon rulership
        if {groom_rasi_idx, bride_rasi_idx} in ({4, 10}, {5, 11}):
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.75
            is_favorable = True
            warnings.append("Samasaptaka between signs ruled by planetary enemies (Sun/Moon vs Saturn) requires emotional maturity.")
            desc_en = (
                f"Moon signs are in Samasaptaka (7th from each other: {groom_sign_en} and {bride_sign_en}). "
                f"Favorable Kendra alignment with moderate caution due to Saturn-Luminary rulership."
            )
            desc_ta = (
                f"இருவரின் ராசிகளும் சமசப்தமமாக (7-ம் இடம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளன. "
                f"அதிபதிகள் பகை கிரகங்களாக அமைந்ததால் நடுத்தர இணக்கம் தரும்."
            )
        else:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.UTHAMA
            score = 1.0
            is_favorable = True
            desc_en = (
                f"Moon signs are in Samasaptaka (7th from each other: {groom_sign_en} and {bride_sign_en}). "
                f"Highly auspicious Rasi Porutham conferring domestic harmony, mutual respect, and marital stability."
            )
            desc_ta = (
                f"இருவரின் ராசிகளும் சமசப்தமமாக (7-ம் இடம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் "
                f"ராசிப் பொருத்தம் உத்தமம். குடும்ப ஒற்றுமை மற்றும் பரிபூரண இணக்கத்தை தரும்."
            )
    elif distance in (3, 11):
        # 3rd and 11th axis (Upachaya)
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Moon sign relationship is 3/11 (Upachaya axis: {groom_sign_en} is {distance}th from {bride_sign_en}). "
            f"Highly auspicious for family prosperity, wealth, and mutual happiness."
        )
        desc_ta = (
            f"ராசித் தொடர்பு 3/11 அக்ஷத்தில் (உபசய ஸ்தானம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் "
            f"ராசிப் பொருத்தம் உத்தமம். செல்வ விருத்தியும் குடும்ப மேன்மையும் தரும்."
        )
    elif distance in (4, 10):
        # 4th and 10th axis (Kendra)
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.75
        is_favorable = True
        desc_en = (
            f"Moon sign relationship is 4/10 (Kendra axis: {groom_sign_en} is {distance}th from {bride_sign_en}). "
            f"Promotes domestic foundation and steady marital alignment."
        )
        desc_ta = (
            f"ராசித் தொடர்பு 4/10 அக்ஷத்தில் (கேந்திர ஸ்தானம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் "
            f"ராசிப் பொருத்தம் மத்திமம். நிலையான குடும்ப வாழ்க்கையை அளிக்கும்."
        )
    elif distance == 1:
        # Same Rasi (Eka Rasi)
        if groom_star_idx > bride_star_idx:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.UTHAMA
            score = 1.0
            is_favorable = True
            desc_en = (
                f"Both share the same Moon sign ({bride_sign_en}), and Groom's Nakshatra "
                f"({NAKSHATRA_NAMES_EN[groom_star_idx]}) is ahead of Bride's Nakshatra ({NAKSHATRA_NAMES_EN[bride_star_idx]}). "
                f"Rasi Porutham is favorable."
            )
            desc_ta = (
                f"இருவரும் ஒரே ராசியில் ({bride_sign_ta}) அமைந்து, மணமகன் நட்சத்திரம் முன்னே உள்ளதால் ராசிப் பொருத்தம் உத்தமம்."
            )
        elif groom_star_idx == bride_star_idx:
            if bride_star_idx in EKA_NAKSHATRA_AUSPICIOUS:
                status = PoruthamStatus.PASS
                grade = PoruthamGrade.UTHAMA
                score = 1.0
                is_favorable = True
                desc_en = (
                    f"Both share the same Moon sign ({bride_sign_en}) and auspicious Eka Nakshatra "
                    f"({NAKSHATRA_NAMES_EN[bride_star_idx]}). Favorable under classical exemptions."
                )
                desc_ta = (
                    f"இருவரும் ஒரே ராசியில் ({bride_sign_ta}) உத்தம ஏக நட்சத்திரத்தில் அமைந்துள்ளதால் ராசிப் பொருத்தம் உத்தமம்."
                )
            else:
                status = PoruthamStatus.PASS
                grade = PoruthamGrade.MADHYAMA
                score = 0.5
                is_favorable = True
                warnings.append("Same Rasi and same Nakshatra without primary Eka exemption.")
                desc_en = (
                    f"Both share the same Moon sign ({bride_sign_en}) and Nakshatra "
                    f"({NAKSHATRA_NAMES_EN[bride_star_idx]}). Classified as Madhyama."
                )
                desc_ta = f"இருவரும் ஒரே ராசியில் ({bride_sign_ta}) ஒரே நட்சத்திரத்தில் அமைந்துள்ளதால் ராசிப் பொருத்தம் மத்திமம்."
        else:
            # Bride's Nakshatra is ahead of Groom's in same Rasi
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            warnings.append("Same Rasi with Bride's Nakshatra preceding Groom's Nakshatra is discouraged in traditional Tamil matching.")
            desc_en = (
                f"Both share the same Moon sign ({bride_sign_en}), but Bride's Nakshatra "
                f"({NAKSHATRA_NAMES_EN[bride_star_idx]}) precedes Groom's Nakshatra ({NAKSHATRA_NAMES_EN[groom_star_idx]}). "
                f"Rasi Porutham is unfavorable."
            )
            desc_ta = (
                f"இருவரும் ஒரே ராசியில் அமைந்து மணமகள் நட்சத்திரம் முன்னே இருப்பதால் மரபுப்படி ராசிப் பொருத்தம் அமையவில்லை."
            )
    elif distance in (2, 12):
        # Dvidwadasa (2/12)
        # Exception 1: Capricorn (10) and Aquarius (11) both ruled by Saturn
        if {groom_rasi_idx, bride_rasi_idx} == {10, 11}:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.5
            is_favorable = True
            warnings.append("Dvidwadasa (2/12) mitigated because both signs (Capricorn & Aquarius) are ruled by Saturn.")
            desc_en = (
                "Dvidwadasa (2/12) placement mitigated by common sign lord (Saturn for Capricorn and Aquarius). "
                "Classified as Madhyama."
            )
            desc_ta = (
                "மகரம்-கும்பம் ராசிகளுக்கு சனி பகவான் பொது அதிபதியாக அமைவதால் துவித்வாதச தோஷம் நீங்கி மத்திம பொருத்தம் ஆகிறது."
            )
        # Exception 2: Pisces (12) and Aries (1) ruled by Jupiter & Mars (friends)
        elif {groom_rasi_idx, bride_rasi_idx} == {1, 12}:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.5
            is_favorable = True
            warnings.append("Dvidwadasa (2/12) mitigated because sign lords Jupiter and Mars are mutual friends.")
            desc_en = (
                "Dvidwadasa (2/12) placement mitigated by mutual friendship of sign lords (Jupiter and Mars for Pisces & Aries). "
                "Classified as Madhyama."
            )
            desc_ta = (
                "மீனம்-மேஷம் ராசிகளுக்கு அதிபதிகளான குரு மற்றும் செவ்வாய் பரஸ்பர மித்திரர்கள் என்பதால் துவித்வாதச தோஷம் நீங்கி மத்திம பொருத்தம் ஆகிறது."
            )
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            desc_en = (
                f"Moon signs are in 2/12 relationship (Dvidwadasa: {groom_sign_en} is {distance}th from {bride_sign_en}). "
                f"Unfavorable in classical tradition, indicating financial expenditure and misunderstandings."
            )
            desc_ta = (
                f"ராசிகள் 2/12-ல் (துவித்வாதசம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் ராசிப் பொருத்தம் அமையவில்லை. "
                f"பண விரயம் மற்றும் கருத்து வேறுபாடுகளைத் தோற்றுவிக்கலாம்."
            )
    elif distance in (6, 8):
        # Shadashtaka (6/8)
        # Exception: Friendly Shadashtaka (Aries-Scorpio ruled by Mars; Taurus-Libra ruled by Venus)
        if {groom_rasi_idx, bride_rasi_idx} in ({1, 8}, {2, 7}):
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.5
            is_favorable = True
            warnings.append(f"Shadashtaka (6/8) axis is mitigated because both signs ({groom_sign_en} & {bride_sign_en}) share the same planetary ruler.")
            desc_en = (
                f"Shadashtaka (6/8) axis is mitigated because both signs ({groom_sign_en} and {bride_sign_en}) "
                f"are ruled by the same planet ({g_lord}). Classified as Madhyama."
            )
            desc_ta = (
                f"இரு ராசிகளும் ({groom_sign_ta} மற்றும் {bride_sign_ta}) ஒரே அதிபதியால் ({g_lord}) ஆளப்படுவதால் "
                f"(மைத்ர சஷ்டாஷ்டகம்) தோஷம் நீங்கி மத்திம பொருத்தம் ஆகிறது."
            )
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.VARJYA
            score = 0.0
            is_favorable = False
            warnings.append(f"Uncancelled Shadashtaka Dosha between {groom_sign_en} and {bride_sign_en}.")
            desc_en = (
                f"Moon signs are in 6/8 relationship (Shadashtaka: {groom_sign_en} is {distance}th from {bride_sign_en}). "
                f"Strictly unfavorable, indicating emotional friction, health vulnerabilities, and discord."
            )
            desc_ta = (
                f"ராசிகள் 6/8-ல் (சஷ்டாஷ்டகம்: {groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் ராசிப் பொருத்தம் அமையவில்லை "
                f"(சஷ்டாஷ்டக தோஷம்)."
            )
    elif distance in (5, 9):
        # Navapanchama (5/9)
        if lords_are_friends:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.5
            is_favorable = True
            warnings.append("Navapanchama (5/9) mitigated by mutual friendship of sign lords.")
            desc_en = (
                f"Navapanchama (5/9) axis between {groom_sign_en} and {bride_sign_en} is mitigated by "
                f"mutual friendship between sign lords ({g_lord} and {b_lord}). Classified as Madhyama."
            )
            desc_ta = (
                f"ராசிகள் 5/9-ல் அமைந்தாலும் அதிபதிகள் ({g_lord} மற்றும் {b_lord}) மித்திரர்களாக இருப்பதால் "
                f"தோஷம் நீங்கி மத்திம பொருத்தம் ஆகிறது."
            )
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            desc_en = (
                f"Moon signs are in 5/9 relationship (Navapanchama: {groom_sign_en} and {bride_sign_en}). "
                f"Unfavorable in traditional Tamil Vivaha Prakarana without Graha Maitri mitigation."
            )
            desc_ta = (
                f"ராசிகள் 5/9-ல் ({groom_sign_ta} - {bride_sign_ta}) அமைந்துள்ளதால் மரபுப்படி ராசிப் பொருத்தம் அமையவில்லை."
            )
    else:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.ADHAMA
        score = 0.0
        is_favorable = False
        desc_en = f"Rasi distance is {distance}; unfavorable alignment."
        desc_ta = f"ராசி இடைவெளி {distance}; அனுகூலமற்ற அமைப்பு."

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "distance": distance,
        "groom_sign": groom_sign_en,
        "bride_sign": bride_sign_en,
        "groom_sign_ta": groom_sign_ta,
        "bride_sign_ta": bride_sign_ta,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_rasi_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Rasi Porutham (TAM-POR-06)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-06",
            name_en="Rasi Porutham",
            name_ta="ராசிப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bride Moon Sign to Groom Moon Sign",
            applied_acceptance_criteria="Samasaptaka (7th) or 3/11 or 4/10 is favorable; 6/8 and 2/12 require specific classical lord exceptions",
            source_and_version="Kalaprakasika Ch. 12, Slokas 20–25 (v1.0)",
            explanation_en="Incomplete chart data provided for Rasi Porutham evaluation.",
            explanation_ta="ராசிப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_rasi_core(
        groom_rasi_idx=groom.moon_sign_idx,
        bride_rasi_idx=bride.moon_sign_idx,
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-06",
        name_en="Rasi Porutham",
        name_ta="ராசிப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "moon_sign_index": groom.moon_sign_idx,
            "moon_sign_name": groom.moon_sign_name,
            "nakshatra_index": groom.moon_nakshatra_idx,
        },
        bride_input={
            "moon_sign_index": bride.moon_sign_idx,
            "moon_sign_name": bride.moon_sign_name,
            "nakshatra_index": bride.moon_nakshatra_idx,
        },
        intermediate_calculation={
            "counting_distance": res["distance"],
            "groom_sign": res["groom_sign"],
            "bride_sign": res["bride_sign"],
            "groom_sign_tamil": res["groom_sign_ta"],
            "bride_sign_tamil": res["bride_sign_ta"],
        },
        counting_direction="Bride Moon Sign to Groom Moon Sign (inclusive count)",
        applied_acceptance_criteria="7th, 3rd, 11th, 4th, 10th favorable; 6/8 and 2/12 evaluated with classical lord exceptions",
        source_and_version="Kalaprakasika Ch. 12, Slokas 20–25 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 7. RASI ADHIPATHI PORUTHAM (TAM-POR-07)
# ===========================================================================

def calculate_rasi_adhipathi_core(
    groom_rasi_idx: int,
    bride_rasi_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Rasi Adhipathi Porutham (Planetary Friendship of Moon sign lords)."""
    g_lord = SIGN_LORDS[groom_rasi_idx]
    b_lord = SIGN_LORDS[bride_rasi_idx]

    warnings: List[str] = []

    if g_lord == b_lord:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Both Moon signs ({SIGN_NAMES_EN[groom_rasi_idx]} and {SIGN_NAMES_EN[bride_rasi_idx]}) "
            f"are ruled by the same Graha ({g_lord}). Complete planetary alignment conferring deep mutual empathy."
        )
        desc_ta = (
            f"இருவரின் ராசிகளையும் ({SIGN_NAMES_TA[groom_rasi_idx]} மற்றும் {SIGN_NAMES_TA[bride_rasi_idx]}) "
            f"ஒரே கிரகமான {g_lord} ஆட்சி செய்வதால் ராசி அதிபதிப் பொருத்தம் உத்தமம். மன ஒற்றுமை சிறப்பாக அமையும்."
        )
        rel_type = "Same Lord"
    else:
        g_to_b = PLANETARY_NATURAL_FRIENDSHIP.get(g_lord, {}).get(b_lord, 0)
        b_to_g = PLANETARY_NATURAL_FRIENDSHIP.get(b_lord, {}).get(g_lord, 0)

        if g_to_b == 1 and b_to_g == 1:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.UTHAMA
            score = 1.0
            is_favorable = True
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} are natural mutual friends. "
                f"Rasi Adhipathi Porutham is Uthama, fostering psychological harmony and emotional resonance."
            )
            desc_ta = (
                f"ராசி அதிபதிகளான {g_lord} மற்றும் {b_lord} பரஸ்பர மித்திரர்கள் என்பதால் "
                f"ராசி அதிபதிப் பொருத்தம் உத்தமம். தம்பதியரின் எண்ணங்கள் ஒத்துப் போகும்."
            )
            rel_type = "Mutual Friends"
        elif (g_to_b == 1 and b_to_g == 0) or (g_to_b == 0 and b_to_g == 1):
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.UTHAMA
            score = 0.75
            is_favorable = True
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} have a friend-neutral relationship. "
                f"Favorable planetary alignment conferring good mutual understanding."
            )
            desc_ta = (
                f"ராசி அதிபதிகள் ({g_lord} - {b_lord}) மித்திர-சம நிலையில் உள்ளதால் "
                f"ராசி அதிபதிப் பொருத்தம் உத்தமம்."
            )
            rel_type = "Friend-Neutral"
        elif g_to_b == 0 and b_to_g == 0:
            status = PoruthamStatus.PASS
            grade = PoruthamGrade.MADHYAMA
            score = 0.5
            is_favorable = True
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} are mutually neutral. "
                f"Rasi Adhipathi Porutham is Madhyama (acceptable concord)."
            )
            desc_ta = (
                f"ராசி அதிபதிகள் ({g_lord} - {b_lord}) பரஸ்பர சம நிலையில் உள்ளதால் "
                f"ராசி அதிபதிப் பொருத்தம் மத்திமம்."
            )
            rel_type = "Mutual Neutral"
        elif (g_to_b == 0 and b_to_g == -1) or (g_to_b == -1 and b_to_g == 0):
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.25
            is_favorable = False
            warnings.append(f"Neutral-Enemy relationship between Moon sign lords {g_lord} and {b_lord}.")
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} have a neutral-enemy relationship. "
                f"Rasi Adhipathi Porutham is sub-optimal."
            )
            desc_ta = (
                f"ராசி அதிபதிகள் ({g_lord} - {b_lord}) சம-சத்ரு நிலையில் உள்ளதால் "
                f"ராசி அதிபதிப் பொருத்தம் சுமாராக உள்ளது."
            )
            rel_type = "Neutral-Enemy"
        elif (g_to_b == 1 and b_to_g == -1) or (g_to_b == -1 and b_to_g == 1):
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.25
            is_favorable = False
            warnings.append(f"Friend-Enemy mixed relationship between Moon sign lords {g_lord} and {b_lord}.")
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} have a mixed friend-enemy relationship. "
                f"Rasi Adhipathi Porutham is sub-optimal."
            )
            desc_ta = (
                f"ராசி அதிபதிகள் ({g_lord} - {b_lord}) மித்திர-சத்ரு கலவை நிலையில் உள்ளதால் "
                f"ராசி அதிபதிப் பொருத்தம் சுமாராக உள்ளது."
            )
            rel_type = "Friend-Enemy"
        else:
            status = PoruthamStatus.FAIL
            grade = PoruthamGrade.ADHAMA
            score = 0.0
            is_favorable = False
            warnings.append(f"Mutual enmity between Moon sign lords {g_lord} and {b_lord}.")
            desc_en = (
                f"Moon sign lords {g_lord} and {b_lord} are natural mutual enemies. "
                f"Rasi Adhipathi Porutham is unfavorable."
            )
            desc_ta = (
                f"ராசி அதிபதிகள் ({g_lord} மற்றும் {b_lord}) பரஸ்பர சத்ருக்கள் (விரோதிகள்) என்பதால் "
                f"ராசி அதிபதிப் பொருத்தம் அமையவில்லை."
            )
            rel_type = "Mutual Enemies"

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "groom_lord": g_lord,
        "bride_lord": b_lord,
        "relationship_type": rel_type,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_rasi_adhipathi_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Rasi Adhipathi Porutham (TAM-POR-07)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-07",
            name_en="Rasi Adhipathi Porutham",
            name_ta="ராசி அதிபதிப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Mutual Sign Lord Relationship",
            applied_acceptance_criteria="Same lord or mutual friends is Uthama (1.0), friend-neutral is 0.75, mutual neutral is Madhyama (0.5), inimical is Adhama",
            source_and_version="Kalaprakasika Ch. 12; Phaladeepika Ch. 2; BPHS Ch. 15 (v1.0)",
            explanation_en="Incomplete chart data provided for Rasi Adhipathi Porutham evaluation.",
            explanation_ta="ராசி அதிபதிப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_rasi_adhipathi_core(
        groom_rasi_idx=groom.moon_sign_idx,
        bride_rasi_idx=bride.moon_sign_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-07",
        name_en="Rasi Adhipathi Porutham",
        name_ta="ராசி அதிபதிப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "moon_sign_index": groom.moon_sign_idx,
            "moon_sign_name": groom.moon_sign_name,
            "moon_sign_lord": res["groom_lord"],
        },
        bride_input={
            "moon_sign_index": bride.moon_sign_idx,
            "moon_sign_name": bride.moon_sign_name,
            "moon_sign_lord": res["bride_lord"],
        },
        intermediate_calculation={
            "groom_lord": res["groom_lord"],
            "bride_lord": res["bride_lord"],
            "relationship_classification": res["relationship_type"],
        },
        counting_direction="Mutual / Bidirectional Sign Lord Natural Relationship",
        applied_acceptance_criteria="Same lord / mutual friends is Uthama (1.0), friend-neutral (0.75), neutral (0.5), inimical (0.0-0.25)",
        source_and_version="Kalaprakasika Ch. 12; Phaladeepika Ch. 2; BPHS Ch. 15 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 8. VASYA PORUTHAM (TAM-POR-08)
# ===========================================================================

def calculate_vasya_core(
    groom_rasi_idx: int,
    bride_rasi_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Vasya Porutham (Magnetic attraction between Moon signs)."""
    g_attracts_b = bride_rasi_idx in TAMIL_VASYA_MAP.get(groom_rasi_idx, [])
    b_attracts_g = groom_rasi_idx in TAMIL_VASYA_MAP.get(bride_rasi_idx, [])

    groom_sign_en = SIGN_NAMES_EN[groom_rasi_idx]
    bride_sign_en = SIGN_NAMES_EN[bride_rasi_idx]
    groom_sign_ta = SIGN_NAMES_TA[groom_rasi_idx]
    bride_sign_ta = SIGN_NAMES_TA[bride_rasi_idx]

    warnings: List[str] = []

    if g_attracts_b and b_attracts_g:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Mutual Vasya present: {groom_sign_en} and {bride_sign_en} exert mutual magnetic attraction "
            f"upon each other. Deep mutual devotion, emotional responsiveness, and marital affection are assured."
        )
        desc_ta = (
            f"இருவருக்கும் பரஸ்பர வசியம் உள்ளதால் ({groom_sign_ta} - {bride_sign_ta}) வசியப் பொருத்தம் உத்தமம். "
            f"தம்பதியரிடையே அளவற்ற அன்பும், ஈர்ப்பும், அன்யோன்யமும் நிறைந்திருக்கும்."
        )
        vasya_type = "Mutual Vasya"
    elif g_attracts_b or b_attracts_g:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.MADHYAMA
        score = 0.75
        is_favorable = True
        desc_en = (
            f"One-way Vasya present between {groom_sign_en} and {bride_sign_en}. "
            f"Natural attraction and marital devotion are active."
        )
        desc_ta = (
            f"இருவருள் ஒருவருக்கு வசியம் உள்ளதால் ({groom_sign_ta} - {bride_sign_ta}) வசியப் பொருத்தம் மத்திமமாக அமைகிறது."
        )
        vasya_type = "One-Way Vasya"
    else:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.ADHAMA
        score = 0.0
        is_favorable = False
        desc_en = (
            f"Vasya is absent between {groom_sign_en} and {bride_sign_en}. "
            f"Note: Vasya is a secondary Porutham; its absence does not veto marriage if primary Poruthams are favorable."
        )
        desc_ta = (
            f"வசியப் பொருத்தம் அமையவில்லை. (இது இரண்டாம் நிலை பொருத்தம்; ரஜ்ஜு, ராசி பொருத்தம் இருப்பின் விவாகம் செய்யலாம்)."
        )
        vasya_type = "Absent"

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "groom_attracts_bride": g_attracts_b,
        "bride_attracts_groom": b_attracts_g,
        "vasya_type": vasya_type,
        "groom_sign": groom_sign_en,
        "bride_sign": bride_sign_en,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_vasya_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Vasya Porutham (TAM-POR-08)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-08",
            name_en="Vasya Porutham",
            name_ta="வசியப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Mutual Rasi Attraction",
            applied_acceptance_criteria="Mutual Vasya is Uthama (1.0), One-way Vasya is Madhyama (0.75), Absent is Adhama (0.0)",
            source_and_version="Kalaprakasika Ch. 12, Slokas 26–28 (v1.0)",
            explanation_en="Incomplete chart data provided for Vasya Porutham evaluation.",
            explanation_ta="வசியப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_vasya_core(
        groom_rasi_idx=groom.moon_sign_idx,
        bride_rasi_idx=bride.moon_sign_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-08",
        name_en="Vasya Porutham",
        name_ta="வசியப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "moon_sign_index": groom.moon_sign_idx,
            "moon_sign_name": groom.moon_sign_name,
        },
        bride_input={
            "moon_sign_index": bride.moon_sign_idx,
            "moon_sign_name": bride.moon_sign_name,
        },
        intermediate_calculation={
            "groom_attracts_bride": res["groom_attracts_bride"],
            "bride_attracts_groom": res["bride_attracts_groom"],
            "vasya_classification": res["vasya_type"],
        },
        counting_direction="Mutual / Bidirectional Rasi magnetic affinity",
        applied_acceptance_criteria="Mutual Vasya is Uthama (1.0 pt), One-way Vasya is Madhyama (0.75 pt), Absent is Adhama (0.0 pt)",
        source_and_version="Kalaprakasika Ch. 12, Slokas 26–28 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 9. RAJJU PORUTHAM (TAM-POR-09) — MAHA PORUTHAM
# ===========================================================================

def calculate_rajju_core(
    groom_star_idx: int,
    bride_star_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Rajju Porutham (Maha Porutham - Longevity & Mangalya protection)."""
    groom_rajju = NAKSHATRA_RAJJU[groom_star_idx]
    bride_rajju = NAKSHATRA_RAJJU[bride_star_idx]

    groom_rajju_ta = RAJJU_NAMES_TA[groom_rajju]
    bride_rajju_ta = RAJJU_NAMES_TA[bride_rajju]

    warnings: List[str] = []

    if groom_rajju != bride_rajju:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"Different Rajjus: Groom belongs to {groom_rajju.value} Rajju and Bride belongs to {bride_rajju.value} Rajju. "
            f"The vital life cords are independent, protecting Mangalya Bhagya and conferring long married life. "
            f"Rajju Porutham is fully satisfied."
        )
        desc_ta = (
            f"இருவரும் வெவ்வேறு ரஜ்ஜுவில் (மணமகன்: {groom_rajju_ta}, மணமகள்: {bride_rajju_ta}) "
            f"அமைந்துள்ளதால் ரஜ்ஜுப் பொருத்தம் உத்தமம். மாங்கல்ய பலமும், தம்பதியருக்கு தீர்க்காயுளும் உண்டாகும்."
        )
    else:
        # Same Rajju -> Rajju Dosha (Rajju Thatu)
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.VARJYA
        score = 0.0
        is_favorable = False

        if groom_rajju == RajjuType.SHIRO:
            affliction_en = "Shiro Rajju Dosha: Threat to the longevity and vitality of the husband (Bhartru Nasa)."
            affliction_ta = "சிரசு ரஜ்ஜு தோஷம்: கணவனின் ஆயுள் மற்றும் ஆரோக்கியத்திற்கு கடுமையான பாதகம் (பர்த்ரு நாசம்)."
        elif groom_rajju == RajjuType.KANTHA:
            affliction_en = "Kantha Rajju Dosha: Threat to the health and longevity of the wife (Stree Nasa)."
            affliction_ta = "கண்ட (கழுத்து) ரஜ்ஜு தோஷம்: மனைவியின் ஆரோக்கியம் மற்றும் மாங்கல்யத்திற்கு பாதகம் (ஸ்திரீ நாசம்)."
        elif groom_rajju == RajjuType.UDARA:
            affliction_en = "Udara Rajju Dosha: Severe obstacles to childbirth and progeny welfare (Santana Nasa)."
            affliction_ta = "உதர (வயிற்று) ரஜ்ஜு தோஷம்: புத்திர பாக்கியத் தடை மற்றும் வம்ச விருத்தி குறைபாடு (சந்தான நாசம்)."
        elif groom_rajju == RajjuType.KATI:
            affliction_en = "Kati Rajju Dosha: Financial loss, distress, and economic adversity (Dhana Nasa)."
            affliction_ta = "கடி (இடை) ரஜ்ஜு தோஷம்: கடுமையான வறுமை மற்றும் பொருளாதார நஷ்டம் (தன நாசம்)."
        else:  # PADA
            affliction_en = "Pada Rajju Dosha: Instability, restlessness, separation, and displacement (Deshantaram)."
            affliction_ta = "பாத ரஜ்ஜு தோஷம்: அலைச்சல், நிம்மதியின்மை மற்றும் ஊர் விட்டு ஊர் செல்லும் நிலை (தேசாந்தரம்)."

        warnings.append(f"Rajju Dosha ({groom_rajju.value} Rajju Thatu). In classical South Indian/Tamil tradition, Rajju has NO CANCELLATION.")

        desc_en = (
            f"Same Rajju detected ({groom_rajju.value} Rajju). {affliction_en} "
            f"In classical South Indian tradition, Rajju Dosha has no cancellation and is regarded as a primary impediment."
        )
        desc_ta = (
            f"இருவரும் ஒரே ரஜ்ஜுவில் ({groom_rajju_ta}) அமைந்துள்ளதால் ஏக ரஜ்ஜு தோஷம் (ரஜ்ஜு தட்டு) ஏற்படுகிறது. "
            f"{affliction_ta} மரபுப்படி ரஜ்ஜு தோஷத்திற்கு விதிவிலக்கு இல்லை."
        )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "groom_rajju": groom_rajju.value,
        "bride_rajju": bride_rajju.value,
        "groom_rajju_ta": groom_rajju_ta,
        "bride_rajju_ta": bride_rajju_ta,
        "is_same_rajju": groom_rajju == bride_rajju,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_rajju_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Rajju Porutham (TAM-POR-09)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-09",
            name_en="Rajju Porutham",
            name_ta="ரஜ்ஜுப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bidirectional Vital Cord Compatibility (Maha Porutham)",
            applied_acceptance_criteria="Different Rajju is Uthama (1.0); Same Rajju is Varjya (0.0) with zero cancellation",
            source_and_version="Kalaprakasika Ch. 12, Slokas 29–35; Kumaraswamiyam (v1.0)",
            explanation_en="Incomplete chart data provided for Rajju Porutham evaluation.",
            explanation_ta="ரஜ்ஜுப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_rajju_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-09",
        name_en="Rajju Porutham",
        name_ta="ரஜ்ஜுப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
            "rajju": res["groom_rajju"],
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
            "rajju": res["bride_rajju"],
        },
        intermediate_calculation={
            "groom_rajju": res["groom_rajju"],
            "bride_rajju": res["bride_rajju"],
            "groom_rajju_tamil": res["groom_rajju_ta"],
            "bride_rajju_tamil": res["bride_rajju_ta"],
            "is_rajju_thatu": res["is_same_rajju"],
        },
        counting_direction="Bidirectional Vital Cord Compatibility (Maha Porutham)",
        applied_acceptance_criteria="Different Rajju is Uthama (1.0 pt); Same Rajju is Varjya (0.0 pt) with zero cancellation in South Indian canon",
        source_and_version="Kalaprakasika Ch. 12, Slokas 29–35; Kumaraswamiyam (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )


# ===========================================================================
# 10. VEDHA PORUTHAM (TAM-POR-10) — MAHA PORUTHAM
# ===========================================================================

def calculate_vedha_core(
    groom_star_idx: int,
    bride_star_idx: int,
) -> Dict[str, Any]:
    """Pure calculation for Vedha Porutham (Repulsion and mutual affliction check)."""
    is_vedha = (groom_star_idx, bride_star_idx) in VEDHA_PAIRS or (bride_star_idx, groom_star_idx) in VEDHA_PAIRS

    groom_star_en = NAKSHATRA_NAMES_EN[groom_star_idx]
    bride_star_en = NAKSHATRA_NAMES_EN[bride_star_idx]
    groom_star_ta = NAKSHATRA_NAMES_TA[groom_star_idx]
    bride_star_ta = NAKSHATRA_NAMES_TA[bride_star_idx]

    warnings: List[str] = []

    if is_vedha:
        status = PoruthamStatus.FAIL
        grade = PoruthamGrade.VARJYA
        score = 0.0
        is_favorable = False
        warnings.append(f"Mutual Vedha affliction detected between {groom_star_en} and {bride_star_en}.")
        desc_en = (
            f"Mutual Vedha affliction detected between Groom star ({groom_star_en}) and Bride star ({bride_star_en}). "
            f"The magnetic rays of these stars are in classical opposition, causing psychic discord, emotional repulsion, and persistent strife."
        )
        desc_ta = (
            f"மணமகன் நட்சத்திரம் {groom_star_ta} மற்றும் மணமகள் நட்சத்திரம் {bride_star_ta} இடையே "
            f"பரஸ்பர வேதை (பகை) உள்ளது. இது தம்பதியரிடையே கருத்து மோதல்களையும் பிரிவினையையும் உண்டாக்கும் (வேதைத் தோஷம்)."
        )
    else:
        status = PoruthamStatus.PASS
        grade = PoruthamGrade.UTHAMA
        score = 1.0
        is_favorable = True
        desc_en = (
            f"No Vedha affliction between Groom star ({groom_star_en}) and Bride star ({bride_star_en}). "
            f"Freedom from psychic repulsion and mutual affliction. Vedha Porutham is fully satisfied."
        )
        desc_ta = (
            f"இருவரின் நட்சத்திரங்களுக்கும் ({groom_star_ta} - {bride_star_ta}) இடையே எவ்வித வேதை (பகை) "
            f"தோஷமும் இல்லை. வேதைப் பொருத்தம் உத்தமம்."
        )

    return {
        "status": status,
        "grade": grade,
        "score": score,
        "is_favorable": is_favorable,
        "is_vedha_present": is_vedha,
        "groom_star": groom_star_en,
        "bride_star": bride_star_en,
        "warnings": warnings,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


def evaluate_vedha_porutham(
    groom: MarriageChartContext,
    bride: MarriageChartContext,
) -> PoruthamResult:
    """Evaluate Vedha Porutham (TAM-POR-10)."""
    if groom is None or bride is None:
        return PoruthamResult(
            rule_id="TAM-POR-10",
            name_en="Vedha Porutham",
            name_ta="வேதைப் பொருத்தம்",
            status=PoruthamStatus.INDETERMINATE,
            groom_input={},
            bride_input={},
            intermediate_calculation={},
            counting_direction="Bidirectional Repulsion and Affliction Check (Maha Porutham)",
            applied_acceptance_criteria="Absence of mutual Vedha pair is Uthama (1.0); Presence of Vedha pair is Varjya (0.0)",
            source_and_version="Kalaprakasika Ch. 12, Slokas 36–38 (v1.0)",
            explanation_en="Incomplete chart data provided for Vedha Porutham evaluation.",
            explanation_ta="வேதைப் பொருத்தம் கணிக்க போதிய ஜாதகத் தகவல் இல்லை.",
        )

    res = calculate_vedha_core(
        groom_star_idx=groom.moon_nakshatra_idx,
        bride_star_idx=bride.moon_nakshatra_idx,
    )

    return PoruthamResult(
        rule_id="TAM-POR-10",
        name_en="Vedha Porutham",
        name_ta="வேதைப் பொருத்தம்",
        status=res["status"],
        groom_input={
            "nakshatra_index": groom.moon_nakshatra_idx,
            "nakshatra_name": groom.moon_nakshatra_name,
        },
        bride_input={
            "nakshatra_index": bride.moon_nakshatra_idx,
            "nakshatra_name": bride.moon_nakshatra_name,
        },
        intermediate_calculation={
            "is_vedha_afflicted": res["is_vedha_present"],
        },
        counting_direction="Bidirectional Repulsion and Affliction Check (Maha Porutham)",
        applied_acceptance_criteria="Absence of mutual Vedha pair is Uthama (1.0 pt); Presence of Vedha pair is Varjya (0.0 pt)",
        source_and_version="Kalaprakasika Ch. 12, Slokas 36–38 (v1.0)",
        explanation_en=res["description_en"],
        explanation_ta=res["description_ta"],
        warnings=res["warnings"],
        grade=res["grade"],
        score=res["score"],
        max_score=1.0,
        is_favorable=res["is_favorable"],
    )
