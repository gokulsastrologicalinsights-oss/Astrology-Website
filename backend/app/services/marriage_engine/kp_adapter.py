"""Read-only KP (Krishnamurti Paddhati) Marriage and Timing Adapter.

Consumes validated chart data and existing KP / XALEN outputs in read-only mode:
- Evaluates 7th Cuspal Sub-Lord (CSL) marriage promise against supporting houses (2, 7, 11)
  and denying houses (1, 6, 10).
- Extracts and preserves 4-tier KP house significators (Levels A, B, C, D) for marriage houses.
- Extracts and compares Ruling Planets (RP) agreement between partners.
- Evaluates Vimshottari Dasa-Bhukti timing windows for marriage fruitfulness.
- Formulates bilingual, non-deterministic explanations (EN/TA) emphasizing astrological
  propensity rather than absolute destiny or event guarantees.

Classical references:
- KP-MARR-01: 7th Cuspal Sub-Lord (CSL) Marriage Promise Analysis (KP Reader II & III, Prof. K.S. Krishnamurti)
- KP-MARR-02: 4-Tier KP Significators for Marriage Houses (KP Reader II)
- KP-MARR-03: Ruling Planets (RP) Agreement and Vimshottari Timing Alignment (KP Reader III)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from app.schemas.common import BirthInput
from app.schemas.kp import (
    KpResponse,
    KpCuspDetail,
    PlanetSignificator,
    HouseSignificatorEntry,
    RulingPlanetsDetail,
    KpDasaPeriod,
    KpDasaBalance,
)
from app.services.kp_service import calculate_kp_chart
from app.services.marriage_engine.models import (
    Gender,
    MarriageChartContext,
    KpPromiseVerdict,
    KpCslFinding,
    KpHouseSignificatorLevelFinding,
    KpSignificatorsFinding,
    KpRulingPlanetsFinding,
    KpDasaBhuktiTimingPeriod,
    KpTimingFinding,
    KpIndividualAnalysis,
    KpMarriageAnalysisResult,
)


# Canonical KP House Sets for Marriage (KP Reader II & III)
KP_SUPPORTING_HOUSES: Set[int] = {2, 7, 11}
KP_DENYING_HOUSES: Set[int] = {1, 6, 10}

# Standard Disclaimer Text
DISCLAIMER_EN: str = (
    "KP astrological indicators represent potential astronomical and karmic tendencies "
    "rather than deterministic certainty. Planetary significations do not constitute an "
    "absolute guarantee or denial of marriage; human agency, socio-cultural context, "
    "and personal life choices remain paramount."
)

DISCLAIMER_TA: str = (
    "கே.பி ஜோதிடக் குறிப்புகள் சாத்தியமான கிரக நிலைகளையும் கர்ம போக்குகளையும் மட்டுமே "
    "குறிக்கின்றன; அவை உறுதியான விதியல்ல. கிரக நிருபணங்கள் திருமணத்தை முழுமையாக "
    "உறுதிப்படுத்தவோ அல்லது மறுக்கவோ செய்யாது; தனிநபர் முடிவுகளும் சூழ்நிலைகளும் முதன்மையானவை."
)


# ---------------------------------------------------------------------------
# Internal Helper Functions
# ---------------------------------------------------------------------------

def _extract_kp_response_from_input(
    chart_input: Optional[Union[MarriageChartContext, KpResponse, BirthInput, Dict[str, Any]]]
) -> Tuple[Optional[KpResponse], Optional[str], Optional[Gender], List[str]]:
    """Resolve a unified KpResponse from MarriageChartContext, KpResponse, BirthInput, or dict.

    Does not mutate any input context.
    """
    warnings: List[str] = []
    if chart_input is None:
        return None, None, None, ["No chart data provided."]

    # If already a KpResponse
    if isinstance(chart_input, KpResponse):
        return chart_input, "Unknown", Gender.MALE, warnings

    # If MarriageChartContext
    if isinstance(chart_input, MarriageChartContext):
        person_id = chart_input.person_id
        gender = chart_input.gender
        if (
            not chart_input.birth_date_iso
            or not chart_input.birth_time_iso
            or chart_input.latitude is None
            or chart_input.longitude is None
        ):
            warnings.append(
                f"Missing birth datetime or geographic coordinates for {chart_input.person_name} ({person_id}); "
                "cannot compute dedicated KP chart."
            )
            return None, person_id, gender, warnings

        try:
            birth = BirthInput(
                birth_date=chart_input.birth_date_iso,
                birth_time=chart_input.birth_time_iso,
                latitude=chart_input.latitude,
                longitude=chart_input.longitude,
                timezone=chart_input.timezone or "Asia/Kolkata",
            )
            kp_resp = calculate_kp_chart(birth)
            return kp_resp, person_id, gender, warnings
        except Exception as exc:
            warnings.append(f"Failed to calculate KP chart for {person_id}: {str(exc)}")
            return None, person_id, gender, warnings

    # If BirthInput
    if isinstance(chart_input, BirthInput):
        try:
            kp_resp = calculate_kp_chart(chart_input)
            return kp_resp, "Unknown", Gender.MALE, warnings
        except Exception as exc:
            warnings.append(f"Failed to calculate KP chart from BirthInput: {str(exc)}")
            return None, None, None, warnings

    # If dictionary resembling KpResponse
    if isinstance(chart_input, dict):
        try:
            kp_resp = KpResponse(**chart_input)
            return kp_resp, "Unknown", Gender.MALE, warnings
        except Exception as exc:
            warnings.append(f"Failed to parse dictionary as KpResponse: {str(exc)}")
            return None, None, None, warnings

    warnings.append(f"Unsupported chart input type: {type(chart_input)}")
    return None, None, None, warnings


# ---------------------------------------------------------------------------
# Core Evaluators
# ---------------------------------------------------------------------------

def evaluate_kp_csl_promise(
    cusp_number: int,
    csl_planet: Optional[str],
    planet_significators: Union[Dict[str, List[int]], List[PlanetSignificator], Dict[str, Any]],
    star_lord: str = "",
    sign_lord: str = "",
    sub_sub_lord: Optional[str] = None,
    person_id: str = "",
) -> KpCslFinding:
    """Evaluate Cuspal Sub-Lord promise for a given cusp (primarily 7th CSL for marriage).

    Rule: KP-MARR-01 (KP Reader II & III)
    Supporting houses: 2 (kutumba), 7 (spouse/union), 11 (fulfillment).
    Denying houses: 1 (12th to 2), 6 (12th to 7), 10 (12th to 11).

    Classification:
    - FAVORABLE: signifies {2, 7, 11} and does not signify {1, 6, 10}
    - UNFAVORABLE: signifies {1, 6, 10} and does not signify {2, 7, 11}
    - MIXED: signifies both supporting and denying houses
    - INDETERMINATE: missing CSL, no primary significations, or unsupported data
    """
    warnings: List[str] = []

    if not csl_planet or not isinstance(csl_planet, str) or not csl_planet.strip():
        return KpCslFinding(
            person_id=person_id,
            cusp_number=cusp_number,
            sub_lord="",
            star_lord=star_lord,
            sign_lord=sign_lord,
            sub_sub_lord=sub_sub_lord,
            signified_houses=[],
            supporting_houses_signified=[],
            denying_houses_signified=[],
            verdict=KpPromiseVerdict.INDETERMINATE,
            is_valid=False,
            explanation_en=f"Cusp {cusp_number} Sub-Lord is missing or invalid; promise cannot be evaluated.",
            explanation_ta=f"{cusp_number}-ம் பாவ உப அதிபதி கிடைக்கவில்லை; திருமண நிருபணத்தை மதிப்பிட இயலவில்லை.",
            rule_sources=["KP-MARR-01"],
            warnings=["Missing Cuspal Sub-Lord planet identifier."],
        )

    # Normalize planet significators into Dict[str, List[int]]
    sig_map: Dict[str, List[int]] = {}
    if isinstance(planet_significators, dict):
        for p, houses in planet_significators.items():
            if isinstance(houses, list):
                # Could be list of int or list of objects
                int_houses = []
                for h in houses:
                    if isinstance(h, int):
                        int_houses.append(h)
                    elif hasattr(h, "house"):
                        int_houses.append(int(h.house))
                sig_map[p] = sorted(list(set(int_houses)))
            elif isinstance(houses, set):
                sig_map[p] = sorted(list(houses))
    elif isinstance(planet_significators, list):
        for ps in planet_significators:
            p_name = getattr(ps, "planet", None) or (ps.get("planet") if isinstance(ps, dict) else None)
            houses_raw = getattr(ps, "signified_houses", None) or (ps.get("signified_houses") if isinstance(ps, dict) else [])
            if p_name:
                sig_map[p_name] = sorted(list(set(houses_raw)))

    signified = set(sig_map.get(csl_planet, []))
    supporting = sorted(list(signified & KP_SUPPORTING_HOUSES))
    denying = sorted(list(signified & KP_DENYING_HOUSES))
    all_signified = sorted(list(signified))

    if not all_signified:
        verdict = KpPromiseVerdict.INDETERMINATE
        warnings.append(f"No house significations found for Sub-Lord {csl_planet}.")
        en_desc = (
            f"7th Cuspal Sub-Lord {csl_planet} does not exhibit documented significations "
            f"in the chart. Promise remains indeterminate."
        )
        ta_desc = (
            f"7-ம் பாவ உப அதிபதி {csl_planet} எந்த பாவ நிருபணங்களையும் காட்டவில்லை. "
            f"திருமண நிருபணம் தீர்மானிக்கப்படவில்லை."
        )
    elif supporting and not denying:
        verdict = KpPromiseVerdict.FAVORABLE
        en_desc = (
            f"7th Cuspal Sub-Lord {csl_planet} favorably signifies supporting houses "
            f"{supporting} (addition to family, spouse, permanent ties) without obstructive "
            f"significations ({denying}). Auspicious marital promise under classical KP rules."
        )
        ta_desc = (
            f"7-ம் பாவ உப அதிபதி {csl_planet} சாதகமான பாவங்களான {supporting}-ஐ குறிக்கிறார் "
            f"(குடும்ப சேர்க்கை, களத்திரம், ஆசை நிறைவேற்றம்); தடையான பாவங்கள் ({denying}) இல்லை. "
            f"கே.பி விதிகளின்படி நன்மையான திருமண வாக்குறுதி."
        )
    elif denying and not supporting:
        verdict = KpPromiseVerdict.UNFAVORABLE
        en_desc = (
            f"7th Cuspal Sub-Lord {csl_planet} signifies separating/denying houses "
            f"{denying} (12th to marriage houses: 1, 6, 10) without supporting significations. "
            f"Indicates astrological challenges or delays under classical KP principles."
        )
        ta_desc = (
            f"7-ம் பாவ உப அதிபதி {csl_planet} பிரிவினை அல்லது சவாலான பாவங்களான {denying}-ஐ "
            f"மட்டுமே குறிக்கிறார்; சாதக பாவங்கள் இல்லை. கே.பி விதிகளின்படி சவால்கள் அல்லது "
            f"தாமதங்களைக் குறிக்கிறது."
        )
    elif supporting and denying:
        verdict = KpPromiseVerdict.MIXED
        en_desc = (
            f"7th Cuspal Sub-Lord {csl_planet} exhibits dual significations: supporting houses "
            f"{supporting} alongside separating houses {denying}. Marital promise is mixed, "
            f"indicating partnership with periods of adjustment or delay."
        )
        ta_desc = (
            f"7-ம் பாவ உப அதிபதி {csl_planet} சாதகமான பாவங்கள் ({supporting}) மற்றும் "
            f"தடையான பாவங்கள் ({denying}) இரண்டையும் குறிக்கிறார். கலவையான திருமண வாக்குறுதி."
        )
    else:
        # Signifies neutral houses only (e.g. 3, 4, 5, 8, 9, 12)
        verdict = KpPromiseVerdict.INDETERMINATE
        en_desc = (
            f"7th Cuspal Sub-Lord {csl_planet} signifies neutral houses {all_signified} "
            f"without directly activating primary marriage houses (2, 7, 11) or separating houses (1, 6, 10)."
        )
        ta_desc = (
            f"7-ம் பாவ உப அதிபதி {csl_planet} நடுநிலையான பாவங்களை ({all_signified}) குறிக்கிறார்; "
            f"முக்கிய திருமண (2, 7, 11) அல்லது பிரிவினை பாவங்கள் (1, 6, 10) நேரடியாக அமையவில்லை."
        )

    return KpCslFinding(
        person_id=person_id,
        cusp_number=cusp_number,
        sub_lord=csl_planet,
        star_lord=star_lord,
        sign_lord=sign_lord,
        sub_sub_lord=sub_sub_lord,
        signified_houses=all_signified,
        supporting_houses_signified=supporting,
        denying_houses_signified=denying,
        verdict=verdict,
        is_valid=True,
        explanation_en=en_desc,
        explanation_ta=ta_desc,
        rule_sources=["KP-MARR-01"],
        warnings=warnings,
    )


def extract_kp_significators(
    target_house: int,
    house_significators: Union[List[HouseSignificatorEntry], List[Dict[str, Any]]],
    planet_significators: Union[List[PlanetSignificator], Dict[str, Any], List[Dict[str, Any]]],
    person_id: str = "",
) -> KpSignificatorsFinding:
    """Extract and categorize 4-tier KP significators for key marriage and separating houses.

    Rule: KP-MARR-02 (KP Reader II)
    Preserves exact Level A, B, C, D provenance without fabricating missing tiers.
    """
    warnings: List[str] = []
    significators_by_house: Dict[int, KpHouseSignificatorLevelFinding] = {}

    relevant_houses = {2, 7, 11, 1, 6, 10, target_house}

    # Normalize house significators
    if isinstance(house_significators, list):
        for hs in house_significators:
            h_num = getattr(hs, "house", None) if not isinstance(hs, dict) else hs.get("house")
            if h_num in relevant_houses:
                level_a = getattr(hs, "level_a", None) if not isinstance(hs, dict) else hs.get("level_a", [])
                level_b = getattr(hs, "level_b", None) if not isinstance(hs, dict) else hs.get("level_b", [])
                level_c = getattr(hs, "level_c", None) if not isinstance(hs, dict) else hs.get("level_c", [])
                level_d = getattr(hs, "level_d", None) if not isinstance(hs, dict) else hs.get("level_d", [])
                all_sigs = getattr(hs, "all_significators", None) if not isinstance(hs, dict) else hs.get("all_significators", [])

                significators_by_house[int(h_num)] = KpHouseSignificatorLevelFinding(
                    house=int(h_num),
                    level_a=list(level_a or []),
                    level_b=list(level_b or []),
                    level_c=list(level_c or []),
                    level_d=list(level_d or []),
                    all_significators=list(all_sigs or []),
                )

    if not significators_by_house:
        warnings.append("House significator data is unavailable or could not be mapped.")

    # Collect union of marriage (2, 7, 11) and detrimental (1, 6, 10) significators
    marriage_sigs: Set[str] = set()
    for h in [2, 7, 11]:
        if h in significators_by_house:
            marriage_sigs.update(significators_by_house[h].all_significators)

    detrimental_sigs: Set[str] = set()
    for h in [1, 6, 10]:
        if h in significators_by_house:
            detrimental_sigs.update(significators_by_house[h].all_significators)

    target_hf = significators_by_house.get(target_house)
    target_all = target_hf.all_significators if target_hf else []

    en_desc = (
        f"House {target_house} significators: Level A={target_hf.level_a if target_hf else []}, "
        f"Level B={target_hf.level_b if target_hf else []}, Level C={target_hf.level_c if target_hf else []}, "
        f"Level D={target_hf.level_d if target_hf else []}. Total marriage significators (2, 7, 11): {sorted(list(marriage_sigs))}."
    )
    ta_desc = (
        f"{target_house}-ம் பாவ நிருபணங்கள்: நிலை A={target_hf.level_a if target_hf else []}, "
        f"நிலை B={target_hf.level_b if target_hf else []}, நிலை C={target_hf.level_c if target_hf else []}, "
        f"நிலை D={target_hf.level_d if target_hf else []}. மொத்த திருமண கிரகங்கள் (2, 7, 11): {sorted(list(marriage_sigs))}."
    )

    return KpSignificatorsFinding(
        person_id=person_id,
        target_house=target_house,
        significators_by_house=significators_by_house,
        all_marriage_significators=sorted(list(marriage_sigs)),
        all_detrimental_significators=sorted(list(detrimental_sigs)),
        explanation_en=en_desc,
        explanation_ta=ta_desc,
        rule_sources=["KP-MARR-02"],
        warnings=warnings,
    )


def evaluate_kp_ruling_planets(
    ruling_planets_detail: Optional[Union[RulingPlanetsDetail, Dict[str, Any]]],
    partner_ruling_planets_detail: Optional[Union[RulingPlanetsDetail, Dict[str, Any]]] = None,
    person_id: str = "",
) -> KpRulingPlanetsFinding:
    """Extract Ruling Planets (RP) and evaluate mutual RP agreement if partner data is provided.

    Rule: KP-MARR-03 (KP Reader III)
    RPs encompass: Day Lord, Ascendant Sign/Star/Sub Lords, Moon Sign/Star/Sub Lords.
    Agreement assesses commonality of RPs as an indicator of astrological synchronicity.
    """
    warnings: List[str] = []

    if ruling_planets_detail is None:
        return KpRulingPlanetsFinding(
            person_id=person_id,
            explanation_en="Ruling Planets data is unavailable.",
            explanation_ta="ஆளும் கிரகங்களின் விவரங்கள் கிடைக்கவில்லை.",
            rule_sources=["KP-MARR-03"],
            warnings=["Ruling Planets data is missing."],
        )

    def _get_val(obj: Any, key: str, default: Any = "") -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    day_lord = str(_get_val(ruling_planets_detail, "day_lord", ""))
    asc_sign = str(_get_val(ruling_planets_detail, "ascendant_sign_lord", ""))
    asc_star = str(_get_val(ruling_planets_detail, "ascendant_star_lord", ""))
    asc_sub = str(_get_val(ruling_planets_detail, "ascendant_sub_lord", ""))
    moon_sign = str(_get_val(ruling_planets_detail, "moon_sign_lord", ""))
    moon_star = str(_get_val(ruling_planets_detail, "moon_star_lord", ""))
    moon_sub = str(_get_val(ruling_planets_detail, "moon_sub_lord", ""))

    raw_list = _get_val(ruling_planets_detail, "ruling_planets_list", [])
    if not raw_list:
        # Fall back to unique non-empty extracted lords
        extracted = [p for p in [day_lord, asc_sign, asc_star, asc_sub, moon_sign, moon_star, moon_sub] if p]
        rps = []
        for p in extracted:
            if p not in rps:
                rps.append(p)
    else:
        rps = list(raw_list)

    # Check partner agreement if provided
    shared: List[str] = []
    agreement_score: float = 0.0

    if partner_ruling_planets_detail is not None:
        partner_rps_raw = _get_val(partner_ruling_planets_detail, "ruling_planets_list", [])
        if not partner_rps_raw:
            p_day = _get_val(partner_ruling_planets_detail, "day_lord", "")
            p_as = _get_val(partner_ruling_planets_detail, "ascendant_sign_lord", "")
            p_ast = _get_val(partner_ruling_planets_detail, "ascendant_star_lord", "")
            p_asb = _get_val(partner_ruling_planets_detail, "ascendant_sub_lord", "")
            p_ms = _get_val(partner_ruling_planets_detail, "moon_sign_lord", "")
            p_mst = _get_val(partner_ruling_planets_detail, "moon_star_lord", "")
            p_msb = _get_val(partner_ruling_planets_detail, "moon_sub_lord", "")
            partner_rps = [p for p in [p_day, p_as, p_ast, p_asb, p_ms, p_mst, p_msb] if p]
        else:
            partner_rps = list(partner_rps_raw)

        shared = sorted(list(set(rps) & set(partner_rps)))
        union_count = len(set(rps) | set(partner_rps))
        agreement_score = round(len(shared) / max(1, union_count), 4)

    en_desc = (
        f"Ruling Planets: {rps}. "
        + (f"Shared with partner: {shared} (Agreement score: {agreement_score})." if partner_ruling_planets_detail else "Individual ruling planets recorded.")
    )
    ta_desc = (
        f"ஆளும் கிரகங்கள்: {rps}. "
        + (f"இணையருடன் பொதுவான கிரகங்கள்: {shared} (பொருத்த நிலை: {agreement_score})." if partner_ruling_planets_detail else "தனிநபர் ஆளும் கிரகங்கள் பதிவு செய்யப்பட்டன.")
    )

    return KpRulingPlanetsFinding(
        person_id=person_id,
        day_lord=day_lord,
        ascendant_sign_lord=asc_sign,
        ascendant_star_lord=asc_star,
        ascendant_sub_lord=asc_sub,
        moon_sign_lord=moon_sign,
        moon_star_lord=moon_star,
        moon_sub_lord=moon_sub,
        ruling_planets_list=rps,
        shared_with_partner=shared,
        agreement_score=agreement_score,
        explanation_en=en_desc,
        explanation_ta=ta_desc,
        rule_sources=["KP-MARR-03"],
        warnings=warnings,
    )


def evaluate_kp_timing(
    current_periods: Optional[Union[List[KpDasaPeriod], List[Dict[str, Any]]]],
    planet_significators: Union[Dict[str, List[int]], List[PlanetSignificator], Dict[str, Any]],
    person_id: str = "",
) -> KpTimingFinding:
    """Evaluate Vimshottari Dasa-Bhukti periods for marital activation.

    Rule: KP-MARR-03 (KP Reader II & III)
    Identifies whether active Mahadasha, Bhukti (Antardasha), and Pratyantardasha
    lords signify marriage houses (2, 7, 11) or separating houses (1, 6, 10).
    """
    warnings: List[str] = []

    if not current_periods:
        return KpTimingFinding(
            person_id=person_id,
            overall_timing_verdict=KpPromiseVerdict.INDETERMINATE,
            explanation_en="Current Dasa-Bhukti periods unavailable; timing cannot be evaluated.",
            explanation_ta="தற்போதைய தசா-புக்தி காலங்கள் கிடைக்கவில்லை; கால நிர்ணயத்தை மதிப்பிட இயலவில்லை.",
            rule_sources=["KP-MARR-03"],
            warnings=["Current Dasa periods data missing."],
        )

    # Normalize planet significators
    sig_map: Dict[str, List[int]] = {}
    if isinstance(planet_significators, dict):
        for p, houses in planet_significators.items():
            if isinstance(houses, (list, set)):
                sig_map[p] = sorted(list(houses))
    elif isinstance(planet_significators, list):
        for ps in planet_significators:
            p_name = getattr(ps, "planet", None) or (ps.get("planet") if isinstance(ps, dict) else None)
            houses_raw = getattr(ps, "signified_houses", None) or (ps.get("signified_houses") if isinstance(ps, dict) else [])
            if p_name:
                sig_map[p_name] = sorted(list(set(houses_raw)))

    def _build_timing_period(p_obj: Any) -> KpDasaBhuktiTimingPeriod:
        lvl_name = getattr(p_obj, "level_name", None) or (p_obj.get("level_name") if isinstance(p_obj, dict) else "Unknown")
        lord = getattr(p_obj, "lord", None) or (p_obj.get("lord") if isinstance(p_obj, dict) else "")
        signified = set(sig_map.get(lord, []))

        supports = bool(signified & KP_SUPPORTING_HOUSES)
        denies = bool(signified & KP_DENYING_HOUSES)

        if supports and not denies:
            fav = "FAVORABLE"
        elif denies and not supports:
            fav = "UNFAVORABLE"
        elif supports and denies:
            fav = "MIXED"
        else:
            fav = "NEUTRAL"

        return KpDasaBhuktiTimingPeriod(
            level=lvl_name,
            lord=lord,
            signified_houses=sorted(list(signified)),
            supports_marriage=supports,
            denies_marriage=denies,
            timing_favorability=fav,
        )

    parsed_periods: List[KpDasaBhuktiTimingPeriod] = [_build_timing_period(p) for p in current_periods]

    cur_md = parsed_periods[0] if len(parsed_periods) > 0 else None
    cur_bk = parsed_periods[1] if len(parsed_periods) > 1 else None
    cur_pr = parsed_periods[2] if len(parsed_periods) > 2 else None

    # Evaluate overall active timing verdict
    # Prioritizes Bhukti (Antardasha) and Mahadasha per KP Reader III
    if cur_bk and cur_md:
        if cur_bk.timing_favorability == "FAVORABLE" and cur_md.timing_favorability in ("FAVORABLE", "MIXED", "NEUTRAL"):
            timing_verdict = KpPromiseVerdict.FAVORABLE
        elif cur_bk.timing_favorability == "UNFAVORABLE" and cur_md.timing_favorability == "UNFAVORABLE":
            timing_verdict = KpPromiseVerdict.UNFAVORABLE
        elif cur_bk.timing_favorability == "FAVORABLE" or cur_md.timing_favorability == "FAVORABLE":
            timing_verdict = KpPromiseVerdict.FAVORABLE
        elif cur_bk.timing_favorability == "UNFAVORABLE" or cur_md.timing_favorability == "UNFAVORABLE":
            timing_verdict = KpPromiseVerdict.MIXED
        else:
            timing_verdict = KpPromiseVerdict.MIXED
    elif cur_md:
        if cur_md.timing_favorability == "FAVORABLE":
            timing_verdict = KpPromiseVerdict.FAVORABLE
        elif cur_md.timing_favorability == "UNFAVORABLE":
            timing_verdict = KpPromiseVerdict.UNFAVORABLE
        else:
            timing_verdict = KpPromiseVerdict.MIXED
    else:
        timing_verdict = KpPromiseVerdict.INDETERMINATE

    en_desc = (
        f"Active Dasa: {cur_md.lord if cur_md else 'N/A'} ({cur_md.timing_favorability if cur_md else 'N/A'}), "
        f"Bhukti: {cur_bk.lord if cur_bk else 'N/A'} ({cur_bk.timing_favorability if cur_bk else 'N/A'}). "
        f"Timing alignment: {timing_verdict.value} for marriage manifestation."
    )
    ta_desc = (
        f"நடப்பு தசா: {cur_md.lord if cur_md else 'இல்லை'} ({cur_md.timing_favorability if cur_md else 'இல்லை'}), "
        f"புக்தி: {cur_bk.lord if cur_bk else 'இல்லை'} ({cur_bk.timing_favorability if cur_bk else 'இல்லை'}). "
        f"காலப் பொருத்தம்: {timing_verdict.value}."
    )

    return KpTimingFinding(
        person_id=person_id,
        current_mahadasha=cur_md,
        current_bhukti=cur_bk,
        current_pratyantar=cur_pr,
        upcoming_promising_periods=[p for p in parsed_periods if p.supports_marriage],
        overall_timing_verdict=timing_verdict,
        explanation_en=en_desc,
        explanation_ta=ta_desc,
        rule_sources=["KP-MARR-03"],
        warnings=warnings,
    )


def evaluate_individual_kp_analysis(
    chart_input: Optional[Union[MarriageChartContext, KpResponse, BirthInput, Dict[str, Any]]],
    partner_rps: Optional[Union[RulingPlanetsDetail, Dict[str, Any]]] = None,
    person_id_override: Optional[str] = None,
    person_name_override: Optional[str] = None,
    gender_override: Optional[Gender] = None,
) -> KpIndividualAnalysis:
    """Execute complete read-only KP analysis for a single person.

    Evaluates:
    - 7th Cuspal Sub-Lord (CSL) promise (KP-MARR-01)
    - 4-tier house significators (KP-MARR-02)
    - Ruling Planets (KP-MARR-03)
    - Vimshottari timing activation (KP-MARR-03)
    """
    kp_resp, detected_id, detected_gender, warnings = _extract_kp_response_from_input(chart_input)

    person_id = person_id_override or detected_id or "Unknown"
    person_name = person_name_override or (
        chart_input.person_name if isinstance(chart_input, MarriageChartContext) else person_id
    )
    gender = gender_override or detected_gender or Gender.MALE

    if kp_resp is None:
        # Fallback when KP data could not be generated
        csl_fallback = KpCslFinding(
            person_id=person_id,
            cusp_number=7,
            sub_lord="",
            verdict=KpPromiseVerdict.INDETERMINATE,
            is_valid=False,
            explanation_en=f"KP chart calculation unavailable for {person_name}.",
            explanation_ta=f"{person_name}-க்கு கே.பி ஜாதகக் கணிப்பு கிடைக்கவில்லை.",
            rule_sources=["KP-MARR-01"],
            warnings=warnings,
        )
        sig_fallback = KpSignificatorsFinding(
            person_id=person_id,
            target_house=7,
            explanation_en="Significators unavailable.",
            explanation_ta="பாவ நிருபணங்கள் கிடைக்கவில்லை.",
            rule_sources=["KP-MARR-02"],
            warnings=warnings,
        )
        rp_fallback = KpRulingPlanetsFinding(
            person_id=person_id,
            explanation_en="Ruling planets unavailable.",
            explanation_ta="ஆளும் கிரகங்கள் கிடைக்கவில்லை.",
            rule_sources=["KP-MARR-03"],
            warnings=warnings,
        )
        timing_fallback = KpTimingFinding(
            person_id=person_id,
            overall_timing_verdict=KpPromiseVerdict.INDETERMINATE,
            explanation_en="Dasa-Bhukti timing unavailable.",
            explanation_ta="தசா-புக்தி அமைப்புகள் கிடைக்கவில்லை.",
            rule_sources=["KP-MARR-03"],
            warnings=warnings,
        )

        return KpIndividualAnalysis(
            person_id=person_id,
            person_name=person_name,
            gender=gender,
            csl_7th=csl_fallback,
            significators=sig_fallback,
            ruling_planets=rp_fallback,
            timing=timing_fallback,
            overall_promise_verdict=KpPromiseVerdict.INDETERMINATE,
            rule_sources=["KP-MARR-01", "KP-MARR-02", "KP-MARR-03"],
            disclaimers=[DISCLAIMER_EN, DISCLAIMER_TA],
            warnings=warnings,
        )

    # 1. 7th CSL
    cusp_7 = None
    if kp_resp.cuspal_analysis:
        for c in kp_resp.cuspal_analysis:
            if c.house == 7:
                cusp_7 = c
                break

    csl_planet = cusp_7.sub_lord if cusp_7 else ""
    star_lord = cusp_7.star_lord if cusp_7 else ""
    sign_lord = cusp_7.sign_lord if cusp_7 else ""
    sub_sub_lord = cusp_7.sub_sub_lord if cusp_7 else None

    csl_finding = evaluate_kp_csl_promise(
        cusp_number=7,
        csl_planet=csl_planet,
        planet_significators=kp_resp.significators,
        star_lord=star_lord,
        sign_lord=sign_lord,
        sub_sub_lord=sub_sub_lord,
        person_id=person_id,
    )

    # 2. Significators
    sig_finding = extract_kp_significators(
        target_house=7,
        house_significators=kp_resp.house_significators,
        planet_significators=kp_resp.significators,
        person_id=person_id,
    )

    # 3. Ruling Planets
    rp_finding = evaluate_kp_ruling_planets(
        ruling_planets_detail=kp_resp.ruling_planets,
        partner_ruling_planets_detail=partner_rps,
        person_id=person_id,
    )

    # 4. Vimshottari Timing
    cur_periods = kp_resp.dasa_hierarchy.current_periods if kp_resp.dasa_hierarchy else []
    timing_finding = evaluate_kp_timing(
        current_periods=cur_periods,
        planet_significators=kp_resp.significators,
        person_id=person_id,
    )

    overall_verdict = csl_finding.verdict

    return KpIndividualAnalysis(
        person_id=person_id,
        person_name=person_name,
        gender=gender,
        csl_7th=csl_finding,
        significators=sig_finding,
        ruling_planets=rp_finding,
        timing=timing_finding,
        overall_promise_verdict=overall_verdict,
        rule_sources=["KP-MARR-01", "KP-MARR-02", "KP-MARR-03"],
        disclaimers=[DISCLAIMER_EN, DISCLAIMER_TA],
        warnings=warnings,
    )


def evaluate_kp_marriage_analysis(
    groom_chart: Optional[Union[MarriageChartContext, KpResponse, BirthInput, Dict[str, Any]]],
    bride_chart: Optional[Union[MarriageChartContext, KpResponse, BirthInput, Dict[str, Any]]],
) -> KpMarriageAnalysisResult:
    """Execute complete read-only KP marriage and timing evaluation for a prospective couple.

    Aggregates:
    - Groom individual KP evaluation
    - Bride individual KP evaluation
    - Ruling Planets agreement
    - Timing synchronicity analysis
    - Non-guarantee disclaimers

    Preserves strict independence without outputting a combined composite compatibility verdict (Phase 8).
    """
    all_warnings: List[str] = []

    # First pass: Extract RPs to pass into partner analysis
    groom_kp, _, _, g_warns = _extract_kp_response_from_input(groom_chart)
    bride_kp, _, _, b_warns = _extract_kp_response_from_input(bride_chart)
    all_warnings.extend(g_warns)
    all_warnings.extend(b_warns)

    groom_rps = groom_kp.ruling_planets if groom_kp else None
    bride_rps = bride_kp.ruling_planets if bride_kp else None

    # Individual analyses
    groom_analysis = evaluate_individual_kp_analysis(
        chart_input=groom_chart,
        partner_rps=bride_rps,
        gender_override=Gender.MALE,
    )

    bride_analysis = evaluate_individual_kp_analysis(
        chart_input=bride_chart,
        partner_rps=groom_rps,
        gender_override=Gender.FEMALE,
    )

    # Ruling Planets Agreement
    g_rp_list = groom_analysis.ruling_planets.ruling_planets_list
    b_rp_list = bride_analysis.ruling_planets.ruling_planets_list
    shared_rps = sorted(list(set(g_rp_list) & set(b_rp_list)))

    if len(shared_rps) >= 3:
        agreement_level = "STRONG"
    elif len(shared_rps) == 2:
        agreement_level = "MODERATE"
    elif len(shared_rps) == 1:
        agreement_level = "LOW"
    else:
        agreement_level = "NONE"

    # Timing Synchronicity Notes
    timing_notes: List[str] = []
    g_timing = groom_analysis.timing.overall_timing_verdict
    b_timing = bride_analysis.timing.overall_timing_verdict

    if g_timing == KpPromiseVerdict.FAVORABLE and b_timing == KpPromiseVerdict.FAVORABLE:
        timing_notes.append(
            "Both prospective partners are currently experiencing astrologically auspicious "
            "Dasa-Bhukti periods activating marriage significations (2, 7, 11)."
        )
    elif g_timing == KpPromiseVerdict.FAVORABLE or b_timing == KpPromiseVerdict.FAVORABLE:
        timing_notes.append(
            "One partner is in a favorable marital period, while the other is experiencing mixed/neutral "
            "planetary periods."
        )
    elif g_timing == KpPromiseVerdict.UNFAVORABLE and b_timing == KpPromiseVerdict.UNFAVORABLE:
        timing_notes.append(
            "Both partners are currently traversing periods with dominant separating or delaying significations (1, 6, 10)."
        )
    else:
        timing_notes.append(
            "Dasa-Bhukti timing presents mixed or standard indicators across both birth horoscopes."
        )

    return KpMarriageAnalysisResult(
        groom_analysis=groom_analysis,
        bride_analysis=bride_analysis,
        shared_ruling_planets=shared_rps,
        ruling_planets_agreement_level=agreement_level,
        timing_synchronicity_notes=timing_notes,
        disclaimers=[DISCLAIMER_EN, DISCLAIMER_TA],
        rule_sources=["KP-MARR-01", "KP-MARR-02", "KP-MARR-03"],
        warnings=all_warnings,
    )
