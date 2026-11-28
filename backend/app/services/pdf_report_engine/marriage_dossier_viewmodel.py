"""Comprehensive bilingual view-model builder for the Detailed Marriage Matching PDF Dossier.

Reuses base charts, timeline, dosha audit, and Tamil nomenclature from
`marriage_print_viewmodel.py`, and extracts every detailed section from
`MarriageCompatibilityResponse` (Composite Assessment, 8 Category Verdicts, Planetary
Degrees, Full 10 Poruthams, 36 Ashtakoota, Tri-Ref Kuja + Papasamya Frame/Planet Breakdown,
Vedic 6 Marriage Houses + Karakas + D9 Cross-Analysis, Bidirectional Synastry, KP 7th CSL
+ 4-Tier Significators, Divergences, Proportional Dasa-Bhukti Sequence, and Sivadasan Ravi
Classical Treatise + Full Sacred Thirumurai Remedies).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.pdf_report_engine.marriage_print_viewmodel import (
    ASHTAKOOTA_META_TA,
    PLANET_NAME_TA,
    SIGN_NAME_TO_IDX,
    SIGN_NAMES_TA,
    build_marriage_print_view_model,
    format_points,
    get_sign_ta,
    safe_dict,
)

PLANET_ORDER: List[str] = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGN_NAMES_EN: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}
PORUTHAM_KEY_ORDER: List[str] = [
    "dina", "gana", "mahendra", "sthree_deergha", "yoni",
    "rasi", "rasi_adhipathi", "vasya", "rajju", "vedha",
]
ASHTAKOOTA_LABELS_EN: Dict[str, tuple[str, str]] = {
    "varna": ("Varna (1.0)", "Spiritual temperament & ego compatibility"),
    "vashya": ("Vashya (2.0)", "Mutual magnetic attraction & harmony"),
    "tara": ("Tara (3.0)", "Navatara longevity, luck & star destiny"),
    "yoni": ("Yoni (4.0)", "Physical & emotional intimacy"),
    "graha_maitri": ("Graha Maitri (5.0)", "Moon sign lords' mental friendship"),
    "gana": ("Gana (6.0)", "Deva / Manushya / Rakshasa temperament"),
    "bhakoot": ("Bhakoot (7.0)", "Family growth, prosperity & 6/8 or 2/12 audit"),
    "nadi": ("Nadi (8.0)", "Biological vitality & progeny welfare"),
}
VEDIC_HOUSE_KEYS: List[str] = ["2", "4", "5", "7", "8", "12"]

STATUS_PALETTE: Dict[str, Dict[str, str]] = {
    "GREEN": {"text": "#14532D", "bg": "#DCFCE7", "border": "#16A34A", "icon": "✓"},
    "ORANGE": {"text": "#9A3412", "bg": "#FFEDD5", "border": "#EA580C", "icon": "!"},
    "RED": {"text": "#7F1D1D", "bg": "#FEE2E2", "border": "#DC2626", "icon": "✕"},
    "NEUTRAL": {"text": "#334155", "bg": "#F1F5F9", "border": "#94A3B8", "icon": "?"},
}


def get_status_style(tone: str) -> Dict[str, str]:
    """Returns consistent GREEN/ORANGE/RED/NEUTRAL colours and icon for UI/PDF rendering."""
    return STATUS_PALETTE.get(str(tone or "NEUTRAL").upper(), STATUS_PALETTE["NEUTRAL"])


def _fmt_dob_long(dob_str: Any, is_ta: bool) -> tuple[str, str]:
    """Formats ISO birth_date into readable date and dynamic age as of report generation."""
    from datetime import date
    raw = str(dob_str or "").strip()
    if not raw or raw == "-":
        return ("-", "-")
    try:
        dob = date.fromisoformat(raw[:10])
    except ValueError:
        return (raw, "-")
    months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    today = date.today()
    age = max(0, today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))
    date_txt = f"{dob.day:02d} {months_en[dob.month - 1]} {dob.year}"
    age_txt = f"{age} {'வயது' if is_ta else 'Years'}"
    return (date_txt, age_txt)


def _fmt_tob_short(tob_str: Any) -> str:
    raw = str(tob_str or "").strip()
    if not raw or raw == "-":
        return "-"
    parts = raw.split(":")
    return f"{parts[0]}:{parts[1]}" if len(parts) >= 2 else raw


def _fmt_deg(deg: Any) -> str:
    if deg is None:
        return "-"
    try:
        val = float(deg) % 30.0
        d = int(val)
        m = int(round((val - d) * 60.0))
        if m >= 60:
            d += 1
            m = 0
        return f"{d:02d}° {m:02d}'"
    except (TypeError, ValueError):
        return "-"


def _sign_label(sign_name: Any, sign_ta: Any, is_ta: bool) -> str:
    if is_ta:
        return get_sign_ta(sign_name, sign_ta)
    return str(sign_name or "-")


def _planet_label(name: Any, is_ta: bool) -> str:
    s = str(name or "-")
    if is_ta:
        return PLANET_NAME_TA.get(s, s)
    return s


def _planet_rows_from_chart(chart_data: Any, d9_data: Any, is_ta: bool) -> List[Dict[str, str]]:
    """Extracts Ascendant + 9 Vedic planets with Rasi & Navamsa signs and degrees."""
    d1 = safe_dict(chart_data)
    d9 = safe_dict(d9_data)
    d1_asc = safe_dict(d1.get("ascendant"))
    d9_asc = safe_dict(d9.get("ascendant"))

    d9_by_name: Dict[str, Dict[str, Any]] = {}
    raw_d9_p = d9.get("planets") or []
    for p in (raw_d9_p.values() if isinstance(raw_d9_p, dict) else raw_d9_p):
        if isinstance(p, dict) and p.get("name"):
            d9_by_name[str(p["name"])] = p

    d1_by_name: Dict[str, Dict[str, Any]] = {}
    raw_d1_p = d1.get("planets") or []
    for p in (raw_d1_p.values() if isinstance(raw_d1_p, dict) else raw_d1_p):
        if isinstance(p, dict) and p.get("name"):
            d1_by_name[str(p["name"])] = p

    rows: List[Dict[str, str]] = []
    if d1_asc:
        s1_idx = d1_asc.get("sign_index") or 1
        s9_idx = d9_asc.get("sign_index")
        s1_name = SIGN_NAMES_TA.get(s1_idx, "") if is_ta else (d1_asc.get("sign_name") or SIGN_NAMES_EN.get(s1_idx, "-"))
        s9_name = (SIGN_NAMES_TA.get(s9_idx, "-") if is_ta else (d9_asc.get("sign_name") or SIGN_NAMES_EN.get(s9_idx, "-"))) if s9_idx else "-"
        rows.append({
            "planet": "லக்னம் (Asc)" if is_ta else "Ascendant",
            "sign": str(s1_name),
            "degree": _fmt_deg(d1_asc.get("degree_in_sign")),
            "retro": "-",
            "d9_sign": str(s9_name),
        })

    for p_en in PLANET_ORDER:
        p = d1_by_name.get(p_en)
        if not p:
            continue
        s1_idx = p.get("sign_index") or 1
        s1_name = SIGN_NAMES_TA.get(s1_idx, "") if is_ta else (p.get("sign_name") or SIGN_NAMES_EN.get(s1_idx, "-"))
        p9 = d9_by_name.get(p_en) or {}
        s9_idx = p9.get("sign_index")
        s9_name = (SIGN_NAMES_TA.get(s9_idx, "-") if is_ta else (p9.get("sign_name") or SIGN_NAMES_EN.get(s9_idx, "-"))) if s9_idx else "-"
        is_ret = bool(p.get("is_retrograde"))
        retro_lbl = ("வக்ரம்" if is_ta else "Retro") if is_ret else "-"
        rows.append({
            "planet": _planet_label(p_en, is_ta),
            "sign": str(s1_name),
            "degree": _fmt_deg(p.get("degree_in_sign")),
            "retro": retro_lbl,
            "d9_sign": str(s9_name),
        })
    return rows


def _extract_kp_partner(partner_kp: Dict[str, Any], fallback_planet: Any, fallback_promise: Any, is_ta: bool) -> Dict[str, Any]:
    csl = safe_dict(partner_kp.get("csl_7th"))
    sig_map = safe_dict(safe_dict(partner_kp.get("significators")).get("significators_by_house"))

    sub_lord = str(csl.get("sub_lord") or fallback_planet or "-")
    star_lord = str(csl.get("star_lord") or "-")
    sign_lord = str(csl.get("sign_lord") or "-")
    sub_sub_lord = str(csl.get("sub_sub_lord") or "-")
    verdict_raw = csl.get("verdict") or partner_kp.get("overall_promise_verdict") or fallback_promise or "-"
    verdict = str(getattr(verdict_raw, "value", verdict_raw)).split(".")[-1]
    signified = csl.get("signified_houses") or []
    supp = csl.get("supporting_houses_signified") or []
    deny = csl.get("denying_houses_signified") or []
    expl = csl.get("explanation_ta" if is_ta else "explanation_en") or csl.get("explanation_en") or ""

    house_tiers: List[Dict[str, str]] = []
    for h_num in ("2", "7", "11"):
        h_obj = safe_dict(sig_map.get(h_num) or sig_map.get(int(h_num) if h_num.isdigit() else h_num))
        if not h_obj:
            continue
        lvl_a = [_planet_label(x, is_ta) for x in (h_obj.get("level_a") or [])]
        lvl_b = [_planet_label(x, is_ta) for x in (h_obj.get("level_b") or [])]
        lvl_c = [_planet_label(x, is_ta) for x in (h_obj.get("level_c") or [])]
        lvl_d = [_planet_label(x, is_ta) for x in (h_obj.get("level_d") or [])]
        house_tiers.append({
            "house": f"{h_num}-ஆம் பாவம்" if is_ta else f"House {h_num}",
            "a": ", ".join(lvl_a) or "-",
            "b": ", ".join(lvl_b) or "-",
            "c": ", ".join(lvl_c) or "-",
            "d": ", ".join(lvl_d) or "-",
        })

    return {
        "sub_lord": _planet_label(sub_lord, is_ta),
        "star_lord": _planet_label(star_lord, is_ta),
        "sign_lord": _planet_label(sign_lord, is_ta),
        "sub_sub_lord": _planet_label(sub_sub_lord, is_ta),
        "verdict": verdict,
        "signified": ", ".join(str(x) for x in signified) or "-",
        "supporting": ", ".join(str(x) for x in supp) or ("இல்லை" if is_ta else "None"),
        "denying": ", ".join(str(x) for x in deny) or ("இல்லை" if is_ta else "None"),
        "explanation": str(expl),
        "house_tiers": house_tiers,
    }


def _extract_vedic_partner(vedic_dict: Dict[str, Any], is_ta: bool) -> Dict[str, Any]:
    houses_map = safe_dict(vedic_dict.get("houses_analysis"))
    house_rows: List[Dict[str, str]] = []
    for hk in VEDIC_HOUSE_KEYS:
        h = safe_dict(houses_map.get(hk) or houses_map.get(int(hk)))
        if not h:
            continue
        occ = [_planet_label(p, is_ta) for p in (h.get("occupants") or [])]
        asp = [_planet_label(p, is_ta) for p in (h.get("aspecting_planets") or [])]
        house_rows.append({
            "house_num": hk,
            "house_title": str(h.get("house_name_ta" if is_ta else "house_name_en") or f"House {hk}"),
            "sign": str(h.get("sign_name_ta" if is_ta else "sign_name_en") or "-"),
            "lord": f"{_planet_label(h.get('lord_name'), is_ta)} (H{h.get('lord_house', '-')}, {h.get('lord_dignity', '-')})",
            "occupants": ", ".join(occ) or ("-" if is_ta else "None"),
            "aspects": ", ".join(asp) or ("-" if is_ta else "None"),
            "status": str(getattr(h.get("status"), "value", h.get("status")) or "PASS").split(".")[-1],
            "summary": str(h.get("summary_ta" if is_ta else "summary_en") or ""),
        })

    sig_map = safe_dict(vedic_dict.get("significators"))
    sig_rows: List[Dict[str, str]] = []
    for p_name, p_raw in sig_map.items():
        s = safe_dict(p_raw)
        if not s:
            continue
        flags: List[str] = []
        if s.get("is_vargottama"):
            flags.append("வர்கோத்தமம்" if is_ta else "Vargottama")
        if s.get("is_pushkara_navamsa"):
            flags.append("புஷ்கர நவாம்சம்" if is_ta else "Pushkara D9")
        if s.get("is_retrograde"):
            flags.append("வக்ரம்" if is_ta else "Retro")
        if s.get("is_combust"):
            flags.append("அஸ்தமனம்" if is_ta else "Combust")
        sig_rows.append({
            "planet": _planet_label(s.get("planet_name") or p_name, is_ta),
            "rasi": f"{_sign_label(s.get('sign_name'), None, is_ta)} (H{s.get('house', '-')})",
            "dignity": str(s.get("dignity") or "-"),
            "nature": str(s.get("functional_nature") or s.get("natural_nature") or "-"),
            "d9_sign": _sign_label(s.get("d9_sign_name"), None, is_ta),
            "flags": ", ".join(flags) or "-",
        })

    d9 = safe_dict(vedic_dict.get("navamsa_cross_analysis"))
    d9_info = {
        "available": bool(d9),
        "d9_lagna": _sign_label(d9.get("d9_lagna_sign_name"), None, is_ta),
        "d9_lagna_lord": _planet_label(d9.get("d9_lagna_lord"), is_ta),
        "d9_7th": _sign_label(d9.get("d9_7th_sign_name"), None, is_ta),
        "d9_7th_lord": _planet_label(d9.get("d9_7th_lord"), is_ta),
        "d1_7th_in_d9": f"{_sign_label(d9.get('d1_7th_lord_in_d9_sign'), None, is_ta)} (H{d9.get('d1_7th_lord_in_d9_house', '-')}, {d9.get('d1_7th_lord_in_d9_dignity', '-')})" if d9 else "-",
        "venus_in_d9": f"{_sign_label(d9.get('venus_in_d9_sign'), None, is_ta)} (H{d9.get('venus_in_d9_house', '-')}, {d9.get('venus_in_d9_dignity', '-')})" if d9 else "-",
        "jupiter_in_d9": f"{_sign_label(d9.get('jupiter_in_d9_sign'), None, is_ta)} (H{d9.get('jupiter_in_d9_house', '-')}, {d9.get('jupiter_in_d9_dignity', '-')})" if d9 else "-",
        "vargottama": ", ".join(_planet_label(x, is_ta) for x in (d9.get("vargottama_planets") or [])) or "-",
        "pushkara": ", ".join(_planet_label(x, is_ta) for x in (d9.get("pushkara_navamsa_planets") or [])) or "-",
        "boundary_risk": bool(d9.get("navamsa_boundary_risk")),
        "arcmin": d9.get("boundary_distance_arcmin"),
        "explanation": str(d9.get("explanation_ta" if is_ta else "explanation_en") or ""),
    }

    kuja = safe_dict(vedic_dict.get("kuja_dosha"))
    return {
        "lagna_lord": f"{_planet_label(vedic_dict.get('lagna_lord'), is_ta)} (H{vedic_dict.get('lagna_lord_house', '-')}, {vedic_dict.get('lagna_lord_dignity', '-')})" if vedic_dict.get("lagna_lord") else "-",
        "summary": str(vedic_dict.get("summary_ta" if is_ta else "summary_en") or ""),
        "houses": house_rows,
        "significators": sig_rows,
        "d9": d9_info,
        "kuja_detailed": kuja,
        "supporting": vedic_dict.get("supporting_indicators") or [],
        "conflicting": vedic_dict.get("conflicting_indicators") or [],
    }


def _extract_kuja_card(kd_vedic: Dict[str, Any], kd_dosha: Dict[str, Any], is_ta: bool) -> Dict[str, Any]:
    src = kd_vedic if kd_vedic else kd_dosha
    is_present = bool(src.get("is_present"))
    is_cancelled = bool(src.get("is_cancelled"))
    return {
        "is_present": is_present,
        "is_cancelled": is_cancelled,
        "severity": str(src.get("severity") or ("Cancelled" if is_cancelled else ("Active" if is_present else "None"))),
        "intensity": format_points(src.get("effective_intensity_percent", 0)),
        "mars_sign": _sign_label(src.get("mars_sign_name"), None, is_ta),
        "mars_deg": _fmt_deg(src.get("mars_degree_in_sign")),
        "h_lagna": src.get("mars_house_from_lagna", "-"),
        "h_moon": src.get("mars_house_from_moon", "-"),
        "h_venus": src.get("mars_house_from_venus", "-"),
        "triggers": src.get("triggering_conditions") or [],
        "cancellations": src.get("cancellations_applied") or [],
        "explanation": str(src.get("explanation_ta" if is_ta else "explanation_en") or src.get("explanation_en") or ""),
    }


def build_marriage_dossier_view_model(data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    """Builds the full bilingual view model covering every website module for the Royal Gold PDF Dossier."""
    lang = "ta" if str(language).lower() in ("ta", "tamil") else "en"
    is_ta = (lang == "ta")
    d = safe_dict(data)
    base_vm = build_marriage_print_view_model(d)

    gp = safe_dict(d.get("groom_profile"))
    bp = safe_dict(d.get("bride_profile"))

    def _partner_ext(prof: Dict[str, Any], base_p: Dict[str, Any]) -> Dict[str, Any]:
        dob_fmt, age_str = _fmt_dob_long(prof.get("birth_date"), is_ta)
        raw_place = prof.get("birth_place") or prof.get("place_of_birth") or prof.get("city") or ""
        place_str = str(raw_place).strip() if str(raw_place).strip() else ("குறிப்பிடப்படவில்லை" if is_ta else "Not Provided")
        rasi_ta = base_p["rasi_ta"]
        rasi_en = str(prof.get("moon_sign") or "-")
        rasi_disp = f"{rasi_ta} / {rasi_en}" if (rasi_ta and rasi_en and rasi_ta != rasi_en) else (rasi_ta if is_ta else rasi_en)
        nak_ta = str(prof.get("moon_nakshatra_tamil") or base_p.get("nakshatra_ta") or "-")
        nak_en = str(prof.get("moon_nakshatra") or "-")
        nak_disp = f"{nak_ta} / {nak_en}" if (is_ta and nak_ta != "-" and nak_en != "-" and nak_ta != nak_en) else (nak_ta if is_ta else nak_en)
        pada_val = str(prof.get("moon_pada") or 1)
        lagna_ta = _sign_label(prof.get("ascendant_sign"), prof.get('ascendant_sign_tamil'), True)
        lagna_en = str(prof.get("ascendant_sign") or "-")
        lagna_disp = f"{lagna_ta} / {lagna_en}" if (lagna_ta != "-" and lagna_en != "-" and lagna_ta != lagna_en) else (lagna_ta if is_ta else lagna_en)
        raw_name = str(prof.get("name") or base_p.get("name") or "").strip()
        if not raw_name or raw_name == "<PRIVATE_PERSON>":
            raw_name = str(base_p.get("name") or "-")
        has_coords = (
            prof.get("latitude") is not None
            and prof.get("longitude") is not None
            and bool(str(prof.get("timezone") or "").strip())
        )
        return {
            "name": raw_name,
            "dob": str(prof.get("birth_date") or "-"),
            "dob_fmt": dob_fmt,
            "age_str": age_str,
            "tob": _fmt_tob_short(prof.get("birth_time")),
            "birth_place": place_str,
            "has_place_name": bool(str(raw_place).strip()),
            "has_valid_coords": has_coords,
            "dob_age": base_p["dob_age"],
            "timezone": str(prof.get("timezone") or ""),
            "coords": f"{prof.get('latitude')}°, {prof.get('longitude')}°" if prof.get("latitude") is not None else "-",
            "lagna": f"{_sign_label(prof.get('ascendant_sign'), prof.get('ascendant_sign_tamil'), is_ta)} ({_fmt_deg(prof.get('ascendant_degree'))})",
            "lagna_clean": lagna_disp,
            "rasi": base_p["rasi_ta"] if is_ta else rasi_en,
            "rasi_bilingual": rasi_disp,
            "nakshatra_only": nak_disp,
            "pada_str": pada_val,
            "nakshatra_pada": base_p["nakshatra_pada_ta"] if is_ta else f"{prof.get('moon_nakshatra', '-')} (Pada {prof.get('moon_pada', 1)})",
            "d9_lagna": _sign_label(prof.get("ascendant_navamsa_sign"), None, is_ta),
            "venus": _sign_label(prof.get("venus_sign"), None, is_ta),
            "jupiter": _sign_label(prof.get("jupiter_sign"), None, is_ta),
            "mars": _sign_label(prof.get("mars_sign"), None, is_ta),
        }

    # Composite Assessment
    comp = safe_dict(d.get("composite_assessment"))
    final_a = safe_dict(d.get("final_assessment"))
    outcome = str(comp.get("overall_outcome") or final_a.get("verdict") or "MIXED_OR_CONDITIONAL")
    _OUTCOME_MAP_EN = {
        "FAVOURABLE_UNDER_SELECTED_RULES": "Favourable Compatibility",
        "MIXED_OR_CONDITIONAL": "Moderate / Conditional Compatibility",
        "UNFAVOURABLE_UNDER_SELECTED_RULES": "Unfavourable Compatibility",
        "INDETERMINATE": "Requires Further Astrological Review",
    }
    _OUTCOME_MAP_TA = {
        "FAVOURABLE_UNDER_SELECTED_RULES": "சிறந்த பொருத்தம்",
        "MIXED_OR_CONDITIONAL": "மிதமான அல்லது நிபந்தனைக்குட்பட்ட பொருத்தம்",
        "UNFAVOURABLE_UNDER_SELECTED_RULES": "பொருத்தம் குறைவானது",
        "INDETERMINATE": "மேலும் ஜோதிட ஆய்வு தேவை",
    }
    _STATUS_MAP_TA = {
        "FAVORABLE": "சாதகம்",
        "MIXED": "மிதமானது",
        "UNFAVORABLE": "சாதகமற்றது",
        "INDETERMINATE": "ஆய்வு தேவை",
    }
    _STATUS_MAP_EN = {
        "FAVORABLE": "Favorable",
        "MIXED": "Moderate",
        "UNFAVORABLE": "Unfavorable",
        "INDETERMINATE": "Review Needed",
    }
    outcome_label = str(
        comp.get("overall_outcome_label_ta" if is_ta else "overall_outcome_label_en")
        or final_a.get("verdict_label_ta" if is_ta else "verdict_label_en")
        or (_OUTCOME_MAP_TA if is_ta else _OUTCOME_MAP_EN).get(outcome, outcome.replace("_", " ").title())
    )
    outcome_expl = str(comp.get("explanation_ta" if is_ta else "explanation_en") or "")
    for raw_code, clean_lbl in (_OUTCOME_MAP_TA if is_ta else _OUTCOME_MAP_EN).items():
        outcome_expl = outcome_expl.replace(raw_code, clean_lbl)
    for raw_st, clean_st in (_STATUS_MAP_TA if is_ta else _STATUS_MAP_EN).items():
        outcome_expl = outcome_expl.replace(f": {raw_st}", f": {clean_st}")
    cat_raw = safe_dict(comp.get("category_verdicts"))
    categories: List[Dict[str, str]] = []
    for cv_raw in cat_raw.values():
        cv = safe_dict(cv_raw)
        if not cv:
            continue
        raw_cat_st = str(cv.get("status") or "INDETERMINATE")
        disp_cat_st = (_STATUS_MAP_TA if is_ta else _STATUS_MAP_EN).get(raw_cat_st, raw_cat_st)
        raw_sum = str(cv.get("score_summary") or "")
        if cv.get("category_id") == "kuja_samadosham":
            up_sum = raw_sum.upper()
            if "CANCELLED" in up_sum:
                raw_sum = "தோஷ நிவர்த்தி (0% • சமநிலை)" if is_ta else "Cancelled (0% • Balanced)"
            elif "MUTUALLY_MATCHED" in up_sum or "BALANCED" in up_sum:
                raw_sum = "சமதோஷம் (சமநிலை)" if is_ta else "Balanced (Samadosham)"
        categories.append({
            "id": str(cv.get("category_id") or ""),
            "name": str(cv.get("category_name_ta" if is_ta else "category_name_en") or cv.get("category_id") or ""),
            "tradition": str(cv.get("tradition") or ""),
            "status": disp_cat_st,
            "summary": raw_sum,
        })

    conflicts: List[Dict[str, str]] = []
    for cf_raw in (comp.get("conflicting_findings") or []):
        cf = safe_dict(cf_raw)
        if cf:
            conflicts.append({
                "title": str(cf.get("title_ta" if is_ta else "title_en") or ""),
                "type": str(cf.get("conflict_type") or "").replace("_", " "),
                "finding_a": str(cf.get("finding_a") or ""),
                "finding_b": str(cf.get("finding_b") or ""),
                "resolution": str(cf.get("resolution_principle") or ""),
                "explanation": str(cf.get("explanation_ta" if is_ta else "explanation_en") or ""),
            })

    disclaimers = comp.get("disclaimers") or []
    disclaimer_txt = (
        (disclaimers[1] if (is_ta and len(disclaimers) > 1) else (disclaimers[0] if disclaimers else ""))
        or str(final_a.get("scientific_disclaimer") or "")
        or (
            "இந்த திருமணப் பொருத்த மதிப்பீடு பாரம்பரிய செவ்வியல் நூல்கள் மற்றும் கே.பி விதிகளின் அடிப்படையிலான ஜோதிட பகுப்பாய்வை வழங்குகிறது."
            if is_ta
            else "This compatibility assessment provides traditional astrological analysis based on classical texts and KP principles as an interpretive advisory guide."
        )
    )

    # Full Tamil 10 Poruthams
    tp = safe_dict(d.get("tamil_porutham"))
    tp_raw = tp.get("poruthams")
    tp_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(tp_raw, dict):
        tp_map = {str(k).lower(): safe_dict(v) for k, v in tp_raw.items()}
    elif isinstance(tp_raw, list):
        for item in tp_raw:
            it = safe_dict(item)
            key = str(it.get("porutham_id") or it.get("id") or it.get("name_en") or "").lower().replace(" ", "_")
            if key:
                tp_map[key] = it

    porutham_rows: List[Dict[str, Any]] = []
    for key in PORUTHAM_KEY_ORDER:
        p = tp_map.get(key)
        if not p:
            continue
        g_in = safe_dict(p.get("groom_input"))
        b_in = safe_dict(p.get("bride_input"))
        porutham_rows.append({
            "name": str(p.get("name_ta" if is_ta else "name_en") or key.title()),
            "ref": str(p.get("classical_reference") or ""),
            "score": f"{format_points(p.get('score', 0))} / {format_points(p.get('max_score', 1))}",
            "grade": str(p.get("grade") or p.get("status") or "-"),
            "is_favorable": bool(p.get("is_favorable")),
            "desc": str(p.get("description_tamil" if is_ta else "description") or p.get("description") or ""),
            "pair": f"{g_in.get('nakshatra_name') or g_in.get('moon_sign') or ''} vs {b_in.get('nakshatra_name') or b_in.get('moon_sign') or ''}".strip(" vs"),
        })
    if not porutham_rows:
        for mr in base_vm["matching_rows"]:
            if mr["label"].startswith("நாடி"):
                continue
            porutham_rows.append({
                "name": mr["label"],
                "ref": "",
                "score": "1 / 1" if mr["pass"] else "0 / 1",
                "grade": "PASS" if mr["pass"] else "FAIL",
                "is_favorable": mr["pass"],
                "desc": mr["desc"],
                "pair": f"{mr['groom_val']} / {mr['bride_val']}",
            })

    # Full 8-Koota Ashtakoota
    ash = safe_dict(d.get("ashtakoota"))
    ash_k_raw = ash.get("kootas")
    ash_k_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(ash_k_raw, dict):
        ash_k_map = {str(k).lower(): safe_dict(v) for k, v in ash_k_raw.items()}
    elif isinstance(ash_k_raw, list):
        for item in ash_k_raw:
            it = safe_dict(item)
            k = str(it.get("koota_id") or it.get("id") or "").lower()
            if k:
                ash_k_map[k] = it

    ash_meta_map = {k: (lbl_ta, max_d, sig_ta) for k, lbl_ta, max_d, sig_ta in ASHTAKOOTA_META_TA}
    ash_rows: List[Dict[str, Any]] = []
    for k_id in ("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi"):
        ko = ash_k_map.get(k_id, {})
        lbl_ta, max_def, sig_ta = ash_meta_map[k_id]
        lbl_en, sig_en = ASHTAKOOTA_LABELS_EN[k_id]
        max_pts = float(ko.get("max_points", max_def) or max_def)
        earned = float(ko.get("earned_points", 0.0) or 0.0)
        is_cancel = bool(ko.get("is_cancelled"))
        ash_rows.append({
            "name": lbl_ta if is_ta else lbl_en,
            "ref": str(ko.get("classical_reference") or ""),
            "earned": format_points(earned),
            "max": format_points(max_pts),
            "status": str(ko.get("status") or ("PASS" if earned >= max_pts * 0.5 else "FAIL")),
            "is_cancelled": is_cancel,
            "cancel_reason": str(ko.get("cancellation_reason") or ""),
            "raw_calc": str(ko.get("raw_calculation") or ""),
            "desc": str(ko.get("description") or (sig_ta if is_ta else sig_en)),
        })

    # Kuja & Papasamya
    da = safe_dict(d.get("dosha_analysis"))
    g_vedic_raw = safe_dict(d.get("groom_vedic"))
    b_vedic_raw = safe_dict(d.get("bride_vedic"))
    groom_kuja = _extract_kuja_card(safe_dict(g_vedic_raw.get("kuja_dosha")), safe_dict(da.get("groom_kuja")), is_ta)
    bride_kuja = _extract_kuja_card(safe_dict(b_vedic_raw.get("kuja_dosha")), safe_dict(da.get("bride_kuja")), is_ta)

    g_papa = safe_dict(da.get("groom_papasamya"))
    b_papa = safe_dict(da.get("bride_papasamya"))

    def _papa_planet_list(p_obj: Dict[str, Any]) -> List[Dict[str, str]]:
        bd = safe_dict(p_obj.get("breakdown_by_planet"))
        return [{"planet": _planet_label(k, is_ta), "pts": format_points(v)} for k, v in bd.items()]

    # Synastry
    syn = safe_dict(d.get("synastry"))
    m2m = safe_dict(syn.get("moon_to_moon"))
    l2l = safe_dict(syn.get("lagna_to_lagna"))

    # KP Marriage
    kp_raw = safe_dict(d.get("kp_marriage"))
    tim_raw = safe_dict(d.get("timing_analysis"))
    kp_section = {
        "available": bool(kp_raw or tim_raw),
        "groom": _extract_kp_partner(
            safe_dict(kp_raw.get("groom_analysis")),
            kp_raw.get("groom_7th_csl_planet"),
            kp_raw.get("groom_7th_csl_promise"),
            is_ta,
        ),
        "bride": _extract_kp_partner(
            safe_dict(kp_raw.get("bride_analysis")),
            kp_raw.get("bride_7th_csl_planet"),
            kp_raw.get("bride_7th_csl_promise"),
            is_ta,
        ),
        "agreement_level": str(kp_raw.get("ruling_planets_agreement_level") or kp_raw.get("significators_agreement") or "-"),
        "shared_rp": ", ".join(_planet_label(x, is_ta) for x in (kp_raw.get("shared_ruling_planets") or [])) or "-",
        "timing_notes": kp_raw.get("timing_synchronicity_notes") or (
            [tim_raw.get("matrimonial_window_assessment")] if tim_raw.get("matrimonial_window_assessment") else []
        ),
        "groom_active_dasa": str(tim_raw.get("groom_active_dasa_bhukti") or ""),
        "bride_active_dasa": str(tim_raw.get("bride_active_dasa_bhukti") or ""),
    }

    # Sivadasan Ravi Full Synthesis + All Hymns
    sr = safe_dict(d.get("sivadasan_ravi_insights"))
    sr_dp = safe_dict(sr.get("dasa_porutham"))
    sr_gb = safe_dict(sr.get("guru_balam"))
    sr_nd = safe_dict(sr.get("nadi_porutham"))
    sr_il = safe_dict(sr.get("in_laws_nakshatras"))
    sr_rem = safe_dict(sr.get("classical_remedies"))
    parikara = safe_dict(sr_rem.get("parikara_sthalam"))
    hymns_out: List[Dict[str, str]] = []
    for h_raw in (sr_rem.get("sacred_hymns") or []):
        h_obj = safe_dict(h_raw)
        if h_obj:
            hymns_out.append({
                "title": str(h_obj.get("title_ta" if is_ta else "title_en") or h_obj.get("title_en") or ""),
                "purpose": str(h_obj.get("purpose_ta" if is_ta else "purpose_en") or ""),
                "verse": str(h_obj.get("hymn_ta") or ""),
            })

    # ==================== PAGE 1 FAMILY DECISION SUMMARY ====================
    tp_score_num = float(tp.get("total_score", 0) or 0)
    tp_max_num = float(tp.get("max_score", 10) or 10)
    rajju_st = str(tp.get("rajju_status") or "PASS").upper()
    vedha_st = str(tp.get("vedha_status") or "PASS").upper()
    if rajju_st == "FAIL" or vedha_st == "FAIL" or tp_score_num < 5.0:
        por_tone = "RED"
        por_status_txt = "சாதகமற்ற பொருத்தம்" if is_ta else "Unfavourable Match"
    elif tp_score_num >= 6.0:
        por_tone = "GREEN"
        por_status_txt = "சாதகமான பொருத்தம்" if is_ta else "Favourable Match"
    else:
        por_tone = "ORANGE"
        por_status_txt = "மிதமான பொருத்தம்" if is_ta else "Moderate Match"

    ash_pts_num = float(ash.get("total_points", 0) or 0)
    ash_max_num = float(ash.get("max_points", 36) or 36)
    ash_thresh_num = float(ash.get("minimum_threshold", 18) or 18)
    nadi_active_dosha = bool(ash.get("nadi_dosha_present")) and not bool(ash.get("nadi_dosha_cancelled"))
    bhakoot_active_dosha = bool(ash.get("bhakoot_dosha_present")) and not bool(ash.get("bhakoot_dosha_cancelled"))
    if nadi_active_dosha or bhakoot_active_dosha or ash_pts_num < ash_thresh_num:
        ash_tone = "RED"
        ash_status_txt = "சாதகமற்ற பொருத்தம்" if is_ta else "Unfavourable Match"
    elif ash_pts_num >= 24.0:
        ash_tone = "GREEN"
        ash_status_txt = "சாதகமான பொருத்தம்" if is_ta else "Favourable Match"
    else:
        ash_tone = "ORANGE"
        ash_status_txt = "மிதமான பொருத்தம்" if is_ta else "Moderate Match"

    outcome_upper = outcome.upper()
    if "FAVOUR" in outcome_upper or "FAVOR" in outcome_upper:
        verdict_tone = "GREEN"
        verdict_title_ta = "சாதகமான பொருத்தம்"
        verdict_title_en = "FAVOURABLE MATCH"
        verdict_sub = (
            "முக்கிய ஜாதக மற்றும் பாரம்பரியப் பொருத்த அம்சங்கள் திருமணத்திற்குச் சாதகமாக அமைந்துள்ளன."
            if is_ta
            else "Core traditional and Vedic compatibility indicators are favourable for proceeding."
        )
        rec_txt = (
            "இந்த ஜாதகப் பொருத்தம் நல்ல நிலையில் உள்ளது. இரு குடும்பங்களும் பரஸ்பர விருப்பம் மற்றும் சுப முகூர்த்தம் குறித்துப் பேசி திருமண ஏற்பாடுகளைத் தொடரலாம்."
            if is_ta
            else "This horoscope compatibility is favourable. Both families may proceed with mutual discussions and auspicious Muhurta planning."
        )
    elif "UNFAVOUR" in outcome_upper or "UNFAVOR" in outcome_upper:
        verdict_tone = "RED"
        verdict_title_ta = "கூடுதல் பரிசீலனை தேவை"
        verdict_title_en = "FURTHER REVIEW RECOMMENDED"
        verdict_sub = (
            "முக்கிய ஜோதிட அம்சங்களில் சாதகமற்ற நிலை காணப்படுகிறது; அனுபவமிக்க ஜோதிடரின் ஆலோசனை அவசியம்."
            if is_ta
            else "Significant astrological concerns were identified; careful consultation with a senior astrologer is advised."
        )
        rec_txt = (
            "இந்த ஜாதகப் பொருத்தத்தில் சில முக்கியக் குறைபாடுகள் காணப்படுகின்றன. எனவே, உடனடி முடிவெடுப்பதைத் தவிர்த்து, அனுபவமிக்க ஜோதிடருடன் விரிவாக ஆலோசித்து முடிவெடுப்பது நலம்."
            if is_ta
            else "Significant astrological concerns are present. We recommend consulting an experienced astrologer and reviewing the detailed analysis before proceeding."
        )
    elif "INDETERMINATE" in outcome_upper:
        verdict_tone = "NEUTRAL"
        verdict_title_ta = "சரிபார்ப்பு தேவை"
        verdict_title_en = "VERIFICATION REQUIRED"
        verdict_sub = (
            "சில ஜாதகத் தகவல்கள் முழுமையாக இல்லாததால் கூடுதல் சரிபார்ப்பு தேவைப்படுகிறது."
            if is_ta
            else "Some birth or chart details are incomplete and require verification."
        )
        rec_txt = (
            "துல்லியமான பிறப்பு விவரங்களைச் சரிபார்த்த பிறகு ஜோதிடரின் ஆலோசனையுடன் அடுத்தகட்ட முடிவெடுக்கவும்."
            if is_ta
            else "Please verify complete birth details and consult an astrologer before making a final decision."
        )
    else:
        verdict_tone = "ORANGE"
        verdict_title_ta = "நிபந்தனையுடன் தொடரலாம்"
        verdict_title_en = "PROCEED WITH FURTHER DISCUSSION"
        verdict_sub = (
            "இந்த அறிக்கை மிதமான மற்றும் நிபந்தனைக்குட்பட்ட பொருத்தத்தைக் காட்டுகிறது; சில அம்சங்களில் கூடுதல் கவனம் தேவை."
            if is_ta
            else "This report indicates a mixed/conditional compatibility assessment where some factors require additional attention."
        )
        rec_txt = (
            "இந்த ஜாதகப் பொருத்தம் மிதமான நிலையில் உள்ளது. சில சாதகமான அம்சங்கள் இருந்தாலும், சில ஜோதிடக் காரணிகள் கூடுதல் கவனத்தைக் கோருகின்றன. எனவே, இரு குடும்பங்களும் பரஸ்பர விருப்பம், எதிர்பார்ப்புகள் மற்றும் வாழ்க்கை ஒற்றுமையைப் பற்றி பேசி, விரிவான அறிக்கையையும் புரிந்துகொண்டு திருமணப் பேச்சைத் தொடர்வது பொருத்தமானது."
            if is_ta
            else "This horoscope compatibility is at a moderate level. While there are supportive indicators, certain astrological factors require additional attention. Therefore, both families should discuss mutual expectations and life harmony, understand the detailed report, and proceed thoughtfully with marriage discussions."
        )

    pos_factors: List[Dict[str, str]] = []
    if rajju_st == "PASS":
        pos_factors.append({"tone": "GREEN", "text": "ரஜ்ஜுப் பொருத்தம் சாதகமாக உள்ளது (மாங்கல்ய பலம் நன்று)." if is_ta else "Rajju Porutham is favourable (supports longevity and marital stability)."})
    if vedha_st == "PASS":
        pos_factors.append({"tone": "GREEN", "text": "வேதைப் பொருத்தம் சாதகமாக உள்ளது (நட்சத்திரப் பகை இல்லை)." if is_ta else "Vedha Porutham is favourable (no mutual star repulsion)."})
    if not nadi_active_dosha and not bhakoot_active_dosha:
        pos_factors.append({"tone": "GREEN", "text": "அஷ்டகூட நாடி மற்றும் பகூட் பொருத்தங்கள் சாதகமாக உள்ளன." if is_ta else "Ashtakoota Nadi & Bhakoot Kootas are favourable."})
    elif not nadi_active_dosha:
        pos_factors.append({"tone": "GREEN", "text": "அஷ்டகூட முறையில் நாடிப் பொருத்தம் சாதகமாக உள்ளது." if is_ta else "Ashtakoota Nadi Koota is clear (supports health and progeny harmony)."})
    elif not bhakoot_active_dosha:
        pos_factors.append({"tone": "GREEN", "text": "பகூட் பொருத்தம் சாதகமாக உள்ளது (குடும்ப வளர்ச்சி நன்று)." if is_ta else "Bhakoot Koota is favourable (supports family prosperity)."})
    papa_v_upper = str(getattr(da.get("papasamya_verdict"), "value", da.get("papasamya_verdict")) or "").upper()
    if "FAVOR" in papa_v_upper or "FAVOUR" in papa_v_upper:
        pos_factors.append({"tone": "GREEN", "text": "பாபசாம்ய மதிப்பீடு சாதகமாக உள்ளது (தோஷ சமநிலை நன்று)." if is_ta else "Papasamya balance is favourable between both charts."})
    if (not groom_kuja["is_present"] or groom_kuja["is_cancelled"]) and (not bride_kuja["is_present"] or bride_kuja["is_cancelled"]):
        if groom_kuja["is_cancelled"] or bride_kuja["is_cancelled"]:
            pos_factors.append({"tone": "GREEN", "text": "செவ்வாய் தோஷம்: இருவருக்கும் சாஸ்திர விதிப்படி தோஷ நிவர்த்தி (0%)." if is_ta else "Kuja Dosha: Cancelled by classical rules for both (0%)."})
        else:
            pos_factors.append({"tone": "GREEN", "text": "செவ்வாய் தோஷம் இல்லை (இருவருக்கும் 0%)." if is_ta else "No Kuja Dosha in either chart (0%)."})

    attn_factors: List[Dict[str, str]] = []
    if rajju_st == "FAIL" or vedha_st == "FAIL":
        attn_factors.append({"tone": "RED", "text": "முக்கிய மகா பொருத்தமான ரஜ்ஜு / வேதை பொருந்தவில்லை." if is_ta else "Critical Maha Porutham (Rajju / Vedha) is unfavourable."})
    elif tp_score_num < 6.0:
        attn_factors.append({"tone": "ORANGE", "text": "சில பாரம்பரிய நட்சத்திரப் பொருத்தங்கள் அமையவில்லை." if is_ta else "Some traditional birth-star Poruthams are not matched."})
    if nadi_active_dosha or bhakoot_active_dosha or ash_pts_num < ash_thresh_num:
        attn_factors.append({"tone": "RED", "text": "அஷ்டகூடப் பொருத்தத்தில் கூடுதல் கவனம் தேவைப்படும் அமைப்பு உள்ளது." if is_ta else "Ashtakoota analysis shows an active Dosha or low score."})

    kp_g_v = str(kp_section["groom"]["verdict"]).upper()
    kp_b_v = str(kp_section["bride"]["verdict"]).upper()
    if "UNFAVOR" in kp_g_v or "UNFAVOR" in kp_b_v or "NEGATIVE" in kp_g_v or "NEGATIVE" in kp_b_v:
        attn_factors.append({"tone": "RED", "text": "கே.பி. திருமண வாக்குறுதி ஆய்வில் சாதகமற்ற அம்சங்கள் உள்ளன." if is_ta else "KP marriage promise analysis indicates unfavourable factors."})
    elif "MIXED" in kp_g_v or "MIXED" in kp_b_v:
        attn_factors.append({"tone": "ORANGE", "text": "கே.பி. திருமண வாக்குறுதி ஆய்வில் மிதமான நிலை உள்ளது." if is_ta else "KP marriage promise analysis shows mixed indicators."})

    vedic_cv_st = str(safe_dict(cat_raw.get("vedic_individual")).get("status") or "").upper()
    if vedic_cv_st in ("MIXED", "UNFAVORABLE") or (groom_kuja["is_present"] and not groom_kuja["is_cancelled"]) or (bride_kuja["is_present"] and not bride_kuja["is_cancelled"]):
        t_v = "RED" if vedic_cv_st == "UNFAVORABLE" else "ORANGE"
        attn_factors.append({"tone": t_v, "text": "திருமண வாழ்க்கை தொடர்பான சில ஜோதிட அம்சங்களில் கூடுதல் கவனம் தேவை." if is_ta else "Certain astrological factors related to married life require additional attention."})
    if "INDETERMINATE" in papa_v_upper:
        attn_factors.append({"tone": "NEUTRAL", "text": "பாபசாம்ய மதிப்பீட்டில் கூடுதல் சரிபார்ப்பு தேவை." if is_ta else "Papasamya evaluation requires further verification."})

    if not pos_factors:
        pos_factors.append({"tone": "NEUTRAL", "text": "சாதகமான அம்சங்கள் விவரப் பக்கங்களில் கொடுக்கப்பட்டுள்ளன." if is_ta else "Supporting indicators are detailed in the technical pages."})
    if not attn_factors:
        attn_factors.append({"tone": "GREEN", "text": "குறிப்பிடத்தக்க எதிர்மறை அமைப்புகள் எதுவும் கண்டறியப்படவில்லை." if is_ta else "No significant adverse astrological factors were detected."})

    decision_summary = {
        "verdict": {
            "tone": verdict_tone,
            "title_ta": verdict_title_ta,
            "title_en": verdict_title_en,
            "subtitle": verdict_sub,
        },
        "porutham_card": {
            "tone": por_tone,
            "title": "தமிழ் 10 பொருத்தங்கள்" if is_ta else "Tamil 10 Poruthams",
            "score_text": f"{format_points(tp_score_num)} / {format_points(tp_max_num)}",
            "status_text": por_status_txt,
        },
        "ashtakoota_card": {
            "tone": ash_tone,
            "title": "வட இந்திய அஷ்டகூடப் பொருத்தம்" if is_ta else "North Indian Ashtakoota",
            "score_text": f"{format_points(ash_pts_num)} / {format_points(ash_max_num)}",
            "status_text": ash_status_txt,
        },
        "positive_factors": pos_factors[:5],
        "attention_factors": attn_factors[:5],
        "recommendation": rec_txt,
        "disclaimer": (
            "இந்த அறிக்கை ஜோதிடக் கணக்கீடுகளின் அடிப்படையிலான வழிகாட்டுதல் மட்டுமே. திருமண முடிவில் இருவரின் விருப்பம், பரஸ்பர புரிதல் மற்றும் குடும்பங்களின் ஆலோசனை முக்கியமானவை."
            if is_ta
            else "This report provides astrological guidance based on traditional calculations. Mutual consent, understanding, and family consultation remain paramount in marriage decisions."
        ),
    }

    groom_ext = _partner_ext(gp, base_vm["groom"])
    bride_ext = _partner_ext(bp, base_vm["bride"])

    birthplace_note = ""
    if not groom_ext["has_place_name"] or not bride_ext["has_place_name"]:
        if groom_ext["has_valid_coords"] and bride_ext["has_valid_coords"]:
            birthplace_note = (
                "குறிப்பு: பிறந்த ஊர் பெயர் வழங்கப்படவில்லை; எனினும் வழங்கப்பட்ட அட்சரேகை, தீர்க்கரேகை மற்றும் நேர மண்டலத்தின் அடிப்படையில் லக்னம் மற்றும் பாவங்கள் துல்லியமாகக் கணக்கிடப்பட்டுள்ளன."
                if is_ta
                else "Note: Birthplace name was not provided; Lagna and house positions are computed from the verified coordinates and timezone."
            )
        else:
            birthplace_note = (
                "சரிபார்ப்பு எச்சரிக்கை: பிறந்த இடம் மற்றும் ஆயத்தொலைவுகள்/நேர மண்டலம் முழுமையாக இல்லை; லக்னம் மற்றும் பாவம் சார்ந்த பலன்களைச் சரிபார்க்கவும்."
                if is_ta
                else "Verification Flag: Birthplace coordinates or timezone are unavailable; please verify Lagna and house-based results."
            )

    # Hierarchical Page 9 Final Verdict (concise, non-repetitive)
    if (not groom_kuja["is_present"] or groom_kuja["is_cancelled"]) and (not bride_kuja["is_present"] or bride_kuja["is_cancelled"]):
        if groom_kuja["is_cancelled"] or bride_kuja["is_cancelled"]:
            dosha_summary_p9 = (
                f"செவ்வாய் தோஷம்: இருவருக்கும் சாஸ்திர விதிப்படி தோஷ நிவர்த்தி (0% — சமநிலை). பாபசாம்யம்: மணமகன் {format_points(g_papa.get('total_papam'))} vs மணமகள் {format_points(b_papa.get('total_papam'))} ({base_vm['page6']['papasamya']['verdict_ta']})."
                if is_ta
                else f"Kuja Dosha: Cancelled by classical rules for both (0% — Balanced). Papasamya: Groom {format_points(g_papa.get('total_papam'))} vs Bride {format_points(b_papa.get('total_papam'))} ({str(getattr(da.get('papasamya_verdict'), 'value', da.get('papasamya_verdict')) or 'FAVORABLE').split('.')[-1]})."
            )
        else:
            dosha_summary_p9 = (
                f"செவ்வாய் தோஷம் இல்லை (0%). பாபசாம்யம்: மணமகன் {format_points(g_papa.get('total_papam'))} vs மணமகள் {format_points(b_papa.get('total_papam'))} ({base_vm['page6']['papasamya']['verdict_ta']})."
                if is_ta
                else f"Kuja Dosha: Absent in both charts (0%). Papasamya: Groom {format_points(g_papa.get('total_papam'))} vs Bride {format_points(b_papa.get('total_papam'))}."
            )
    else:
        dosha_summary_p9 = (
            f"செவ்வாய் தோஷம்: மணமகன் ({groom_kuja['severity']} • {groom_kuja['intensity']}%), மணமகள் ({bride_kuja['severity']} • {bride_kuja['intensity']}%). பாபசாம்யம்: {base_vm['page6']['papasamya']['verdict_ta']}."
            if is_ta
            else f"Kuja Dosha: Groom ({groom_kuja['severity']} • {groom_kuja['intensity']}%), Bride ({bride_kuja['severity']} • {bride_kuja['intensity']}%)."
        )

    kp_g_v_disp = kp_section["groom"]["verdict"]
    kp_b_v_disp = kp_section["bride"]["verdict"]
    if "UNFAVOR" in kp_g_v or "UNFAVOR" in kp_b_v or "MIXED" in kp_g_v or "MIXED" in kp_b_v:
        kp_summary_p9 = (
            f"கே.பி. 7-ம் பாவ உப அதிபதி ஆய்வில் மணமகனுக்கு {kp_g_v_disp} நிலையும், மணமகளுக்கு {kp_b_v_disp} நிலையும் காணப்படுகிறது. இது திருமணம் தோல்வியடையும் என்பதைக் குறிக்காது; மாறாக எதிர்பார்ப்புகள், காலதாமதம் அல்லது பரஸ்பர அனுசரிப்பில் கூடுதல் புரிதலும் பொறுமையும் தேவை என்பதை மட்டுமே உணர்த்துகிறது."
            if is_ta
            else f"KP 7th Cuspal Sub-Lord analysis shows {kp_g_v_disp} promise for the Groom and {kp_b_v_disp} promise for the Bride. This does not mean the marriage will fail; rather, it indicates potential timing delays or differing expectations that benefit from open communication and mutual adjustment."
        )
    else:
        kp_summary_p9 = (
            f"கே.பி. 7-ம் பாவ உப அதிபதி ஆய்வு இருவருக்கும் சாதகமாக ({kp_g_v_disp} / {kp_b_v_disp}) அமைந்துள்ளது."
            if is_ta
            else f"KP 7th Cuspal Sub-Lord analysis is supportive for both partners ({kp_g_v_disp} / {kp_b_v_disp})."
        )

    ds_info = base_vm["dasa_sandhi"]
    if ds_info.get("has_sandhi") and ds_info.get("is_imminent"):
        timing_p9 = (
            "தற்போது அருகாமையில் தசா சந்தி உள்ளதால் தகுந்த முகூர்த்தத் தேர்வு பரிந்துரைக்கப்படுகிறது. "
            if is_ta
            else "An imminent Dasa Sandhi is present; careful Muhurta selection is recommended. "
        )
    elif ds_info.get("has_sandhi"):
        yrs = int(round(ds_info.get("years_away", 0)))
        timing_p9 = (
            f"தற்போதைய திருமண காலத்திற்குத் தசா சந்தித் தடை இல்லை (அடுத்த தசா சந்தி சுமார் {yrs} ஆண்டுகளுக்குப் பிறகு). "
            if is_ta
            else f"No imminent Dasa Sandhi obstacle (next Dasa Sandhi is ~{yrs} years away). "
        )
    else:
        timing_p9 = (
            "இருவரின் தசா காலங்களும் சுமுகமாக அமைந்துள்ளன. "
            if is_ta
            else "Both partners' Dasa periods are well-synchronized. "
        )
    timing_p9 += (
        f"கோட்சார குரு பலம் (சந்திர ராசியிலிருந்து): {sr_gb.get('label_ta', '')}."
        if is_ta
        else f"Gochara Guru Balam (from Moon Sign): {sr_gb.get('label_en', '')}."
    )

    final_verdict_p9 = {
        "overall_title": outcome_label,
        "overall_line": verdict_sub,
        "positive_line": " • ".join(x["text"] for x in pos_factors[:4]),
        "concerns_line": " • ".join(x["text"] for x in attn_factors[:4]),
        "dosha_line": dosha_summary_p9,
        "kp_line": kp_summary_p9,
        "timing_line": timing_p9,
        "recommendation_line": rec_txt,
    }

    return {
        "lang": lang,
        "is_ta": is_ta,
        "base": base_vm,
        "birthplace_note": birthplace_note,
        "final_verdict_p9": final_verdict_p9,
        "decision_summary": decision_summary,
        "groom_ext": groom_ext,
        "bride_ext": bride_ext,
        "groom_planets": _planet_rows_from_chart(d.get("groom_chart"), d.get("groom_d9_chart"), is_ta),
        "bride_planets": _planet_rows_from_chart(d.get("bride_chart"), d.get("bride_d9_chart"), is_ta),
        "composite": {
            "outcome": outcome,
            "outcome_label": outcome_label,
            "explanation": outcome_expl,
            "categories": categories,
            "supportive": comp.get("major_supportive_indicators") or final_a.get("primary_strengths") or [],
            "challenging": comp.get("major_challenging_indicators") or final_a.get("primary_concerns") or [],
            "missing": comp.get("missing_or_uncertain_evidence") or [],
            "review": comp.get("recommended_astrologer_review") or [],
            "conflicts": conflicts,
            "disclaimer": disclaimer_txt,
            "fingerprint": str(final_a.get("reproducibility_fingerprint") or ""),
        },
        "porutham_full": {
            "total_score": format_points(tp.get("total_score", 0)),
            "max_score": format_points(tp.get("max_score", 10)),
            "verdict": str(tp.get("aggregate_verdict") or "-"),
            "rajju_status": str(tp.get("rajju_status") or "-"),
            "vedha_status": str(tp.get("vedha_status") or "-"),
            "rows": porutham_rows,
            "checklist_11": base_vm["matching_rows"],
        },
        "ashtakoota_full": {
            "total": format_points(ash.get("total_points", 0)),
            "max": format_points(ash.get("max_points", 36)),
            "threshold": format_points(ash.get("minimum_threshold", 18)),
            "is_met": bool(base_vm["page6"]["ashtakoota_threshold_met"]),
            "nadi_present": bool(ash.get("nadi_dosha_present")),
            "nadi_cancelled": bool(ash.get("nadi_dosha_cancelled")),
            "bhakoot_present": bool(ash.get("bhakoot_dosha_present")),
            "bhakoot_cancelled": bool(ash.get("bhakoot_dosha_cancelled")),
            "rows": ash_rows,
        },
        "kuja_full": {
            "mutual_balance": str(
                da.get("mutual_kuja_balance")
                or safe_dict(cat_raw.get("kuja_samadosham")).get("score_summary")
                or ("BALANCED" if (not groom_kuja["is_present"] or groom_kuja["is_cancelled"]) and (not bride_kuja["is_present"] or bride_kuja["is_cancelled"]) else "EVALUATED")
            ),
            "samadosham_status": str(
                da.get("samadosham_status")
                or da.get("mutual_kuja_balance")
                or safe_dict(cat_raw.get("kuja_samadosham")).get("score_summary")
                or ("தோஷ நிவர்த்தி (Balanced / Cancelled)" if is_ta else "Balanced / Cancelled")
            ),
            "samadosham_expl": str(
                da.get("samadosham_explanation_ta" if is_ta else "samadosham_explanation_en")
                or da.get("samadosham_explanation_en")
                or "; ".join(str(x) for x in (safe_dict(cat_raw.get("kuja_samadosham")).get("key_factors") or []))
                or ""
            ),
            "groom": groom_kuja,
            "bride": bride_kuja,
        },
        "papasamya_full": {
            "verdict": str(getattr(da.get("papasamya_verdict"), "value", da.get("papasamya_verdict")) or "TOLERABLE").split(".")[-1],
            "verdict_ta": base_vm["page6"]["papasamya"]["verdict_ta"],
            "diff_str": base_vm["page6"]["papasamya"]["diff_str"],
            "expl": str(da.get("papasamya_explanation_ta" if is_ta else "papasamya_explanation_en") or da.get("papasamya_explanation_en") or ""),
            "groom_total": format_points(g_papa.get("total_papam")),
            "bride_total": format_points(b_papa.get("total_papam")),
            "groom_frames": f"Lagna: {format_points(g_papa.get('lagna_papam'))} | Moon: {format_points(g_papa.get('moon_papam'))} | Venus: {format_points(g_papa.get('venus_papam'))}" if g_papa else "-",
            "bride_frames": f"Lagna: {format_points(b_papa.get('lagna_papam'))} | Moon: {format_points(b_papa.get('moon_papam'))} | Venus: {format_points(b_papa.get('venus_papam'))}" if b_papa else "-",
            "groom_breakdown": _papa_planet_list(g_papa),
            "bride_breakdown": _papa_planet_list(b_papa),
        },
        "vedic_full": {
            "groom": _extract_vedic_partner(g_vedic_raw, is_ta),
            "bride": _extract_vedic_partner(b_vedic_raw, is_ta),
        },
        "synastry_full": {
            "available": bool(syn),
            "explanation": str(syn.get("explanation_ta" if is_ta else "explanation_en") or syn.get("explanation_en") or ""),
            "moon_to_moon": {
                "rel": str(m2m.get("sign_relationship") or "-"),
                "assessment": str(m2m.get("sign_assessment") or "-"),
                "dist": f"{m2m.get('sign_distance_g_to_b', '-')} / {m2m.get('sign_distance_b_to_g', '-')}",
                "nak_dist": f"{m2m.get('nakshatra_distance_g_to_b', '-')} / {m2m.get('nakshatra_distance_b_to_g', '-')}",
                "pada_res": str(m2m.get("pada_resonance") or "-"),
                "lord_rel": str(m2m.get("moon_lord_relationship") or "-"),
                "expl": str(m2m.get("explanation_en") or ""),
            },
            "lagna_to_lagna": {
                "rel": str(l2l.get("lagna_relationship") or "-"),
                "assessment": str(l2l.get("lagna_assessment") or l2l.get("sign_assessment") or "-"),
                "expl": str(l2l.get("explanation_en") or ""),
            },
        },
        "kp_full": kp_section,
        "sivadasan_full": {
            "available": bool(sr),
            "treatise_title": str(sr.get("treatise_title_ta" if is_ta else "treatise_title_en") or ("திருமண யோகப் பொருத்த திறவுகோல்" if is_ta else "Thirumana Yoga Porutha Thiravukol")),
            "author": str(sr.get("author") or "Siddhayogi Sivadasan Ravi"),
            "dasa_porutham": {
                "verdict": str(sr_dp.get("verdict_ta" if is_ta else "verdict") or "-"),
                "groom_md": f"{_planet_label(sr_dp.get('groom_mahadasha'), is_ta)}",
                "bride_md": f"{_planet_label(sr_dp.get('bride_mahadasha'), is_ta)}",
                "findings": sr_dp.get("findings_ta" if is_ta else "findings_en") or [],
            },
            "guru_balam": {
                "label": str(sr_gb.get("label_ta" if is_ta else "label_en") or "-"),
                "transit_sign": str(sr_gb.get("transit_jupiter_sign_ta" if is_ta else "transit_jupiter_sign_en") or "-"),
                "groom_house": sr_gb.get("groom_house_from_moon", "-"),
                "bride_house": sr_gb.get("bride_house_from_moon", "-"),
                "desc": str(sr_gb.get("description_ta" if is_ta else "description_en") or ""),
            },
            "nadi_porutham": {
                "verdict": str(sr_nd.get("verdict_ta" if is_ta else "verdict") or "-"),
                "summary": str(sr_nd.get("summary_ta" if is_ta else "summary_en") or ""),
                "has_nandi": bool(sr_nd.get("has_nandi_yogam")),
                "obstacles": sr_nd.get("nandi_obstacles_ta" if is_ta else "nandi_obstacles_en") or [],
            },
            "in_laws": {
                "has_special": bool(sr_il.get("has_special_nakshatra")),
                "findings": [
                    {
                        "star": str(safe_dict(f).get("nakshatra_ta" if is_ta else "nakshatra_en") or ""),
                        "relative": str(safe_dict(f).get("relative_ta" if is_ta else "relative_en") or ""),
                        "is_exempt": bool(safe_dict(f).get("is_exempt")),
                        "expl": str(safe_dict(f).get("explanation_ta" if is_ta else "explanation_en") or ""),
                    }
                    for f in (sr_il.get("findings") or [])
                ],
            },
            "temple_name": str(parikara.get("name_ta" if is_ta else "name_en") or ("ஸ்ரீ நெல்லையப்பர் - காந்திமதியம்மன் திருக்கோவில், திருநெல்வேலி" if is_ta else "Sri Nellaiyappar & Gandhimathi Amman Temple, Tirunelveli")),
            "temple_sig": str(parikara.get("significance_ta" if is_ta else "significance_en") or ""),
            "hymns": hymns_out,
        },
    }
