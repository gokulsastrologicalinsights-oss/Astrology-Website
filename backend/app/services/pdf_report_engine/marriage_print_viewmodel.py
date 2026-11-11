"""Shared 5-page print/PDF view-model builder for Marriage Compatibility reports.

Single source of truth consumed by both the Playwright HTML->PDF renderer
(`marriage_compatibility_generator.py`) and the pure-Python ReportLab fallback
renderer (`marriage_compatibility_generator_rl.py`), guaranteeing parity with the
frontend 5-page print format (`MarriageCompatibilityPrintReport.tsx`).
"""

from __future__ import annotations

import base64
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
FONTS_DIR = ASSETS_DIR / "fonts"
NOTO_REGULAR_PATH = FONTS_DIR / "NotoSansTamil-Regular.ttf"
NOTO_BOLD_PATH = FONTS_DIR / "NotoSansTamil-Bold.ttf"

SIGN_NAME_TO_IDX: Dict[str, int] = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
    "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
    "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12,
}

SIGN_NAMES_TA: Dict[int, str] = {
    1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
    5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
    9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்",
}

SIGN_LORD_TA: Dict[int, str] = {
    1: "செவ்வாய்", 2: "சுக்கிரன்", 3: "புதன்", 4: "சந்திரன்",
    5: "சூரியன்", 6: "புதன்", 7: "சுக்கிரன்", 8: "செவ்வாய்",
    9: "குரு", 10: "சனி", 11: "சனி", 12: "குரு",
}

PLANET_CHART_ABBR_TA: Dict[str, str] = {
    "Sun": "சூ", "Moon": "சந்", "Mars": "செ", "Mercury": "பு",
    "Jupiter": "குரு", "Venus": "சுக்", "Saturn": "சனி",
    "Rahu": "ரா", "Ketu": "கே", "Ascendant": "ல", "Lagna": "ல",
}

PLANET_NAME_TA: Dict[str, str] = {
    "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்", "Mercury": "புதன்",
    "Jupiter": "குரு", "Venus": "சுக்கிரன்", "Saturn": "சனி",
    "Rahu": "ராகு", "Ketu": "கேது",
}

ASHTAKOOTA_META_TA: List[Tuple[str, str, float, str]] = [
    ("varna", "வர்ணம் (Varna)", 1.0, "ஆன்ம சுபாவம் & மனோபாவம்"),
    ("vashya", "வசியம் (Vashya)", 2.0, "பரஸ்பர ஈர்ப்பு & ஒற்றுமை"),
    ("tara", "தாரா (Tara)", 3.0, "நவதாரை அதிர்ஷ்டம் & ஆயுள்"),
    ("yoni", "யோனி (Yoni)", 4.0, "தாம்பத்திய இணக்கம்"),
    ("graha_maitri", "கிரக மைத்ரி (Maitri)", 5.0, "ராசிநாதர்களின் நட்பு"),
    ("gana", "கணம் (Gana)", 6.0, "குண நலன் & கருத்துப் பரிமாற்றம்"),
    ("bhakoot", "பகுட் (Bhakoot)", 7.0, "வம்ச விருத்தி & பொருள் நலம்"),
    ("nadi", "நாடி (Nadi)", 8.0, "மரபணு & சந்ததி ஆரோக்கியம்"),
]

KP_VERDICT_TA: Dict[str, str] = {
    "FAVORABLE": "சாதகம்",
    "POSITIVE": "சாதகம்",
    "MIXED": "மிதமானது",
    "UNFAVORABLE": "சாதகமற்றது",
    "NEGATIVE": "சாதகமற்றது",
    "STRONG": "வலுவான ஒற்றுமை",
    "MODERATE": "மிதமான ஒற்றுமை",
    "WEAK": "குறைவான ஒற்றுமை",
}

PAPASAMYA_VERDICT_TA: Dict[str, str] = {
    "FAVORABLE": "சாதகமான சமநிலை",
    "TOLERABLE": "ஏற்கத்தக்க சமநிலை",
    "UNFAVORABLE": "கவனம் தேவை (பாப வேறுபாடு)",
}

NAKSHATRA_NAMES_EN: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_NAMES_TA: List[str] = [
    "அசுவினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
    "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
    "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி",
]

GANA_TA: Dict[str, str] = {
    "Deva": "தேவம்",
    "Manushya": "மனுஷம்",
    "Rakshasa": "ராட்சஸம்",
}

RAJJU_TA: Dict[str, str] = {
    "Shiro": "தலை",
    "Kantha": "கழுத்து",
    "Udara": "வயிறு",
    "Kati": "இடை",
    "Pada": "பாதம்",
}

RAJJU_DIR_TA: Dict[str, str] = {
    "Arohana": "(ஏறு)",
    "Avarohana": "(இறங்கு)",
    "Central": "",
}

YONI_BY_NAK_IDX_TA: Dict[int, str] = {
    0: "ஆண் குதிரை", 1: "ஆண் யானை", 2: "பெண் ஆடு", 3: "ஆண் பாம்பு",
    4: "பெண் பாம்பு", 5: "ஆண் நாய்", 6: "பெண் பூனை", 7: "ஆண் ஆடு",
    8: "ஆண் பூனை", 9: "ஆண் எலி", 10: "பெண் எலி", 11: "ஆண் பசு",
    12: "பெண் எருமை", 13: "பெண் புலி", 14: "ஆண் எருமை", 15: "ஆண் புலி",
    16: "பெண் மான்", 17: "ஆண் மான்", 18: "பெண் நாய்", 19: "ஆண் குரங்கு",
    20: "ஆண் கீரி", 21: "பெண் குரங்கு", 22: "பெண் சிம்மம்", 23: "பெண் குதிரை",
    24: "ஆண் சிம்மம்", 25: "பெண் பசு", 26: "பெண் யானை",
}

ANIMAL_TA: Dict[str, str] = {
    "Horse": "குதிரை", "Elephant": "யானை", "Sheep": "ஆடு", "Goat": "ஆடு", "Serpent": "பாம்பு",
    "Dog": "நாய்", "Cat": "பூனை", "Rat": "எலி", "Cow": "பசு",
    "Buffalo": "எருமை", "Tiger": "புலி", "Deer": "மான்", "Monkey": "குரங்கு",
    "Mongoose": "கீரி", "Lion": "சிம்மம்",
}

RAJJU_DIRECTION_BY_NAK_IDX: Dict[int, str] = {
    0: "Arohana", 9: "Arohana", 18: "Arohana",
    8: "Avarohana", 17: "Avarohana", 26: "Avarohana",
    1: "Arohana", 10: "Arohana", 19: "Arohana",
    7: "Avarohana", 16: "Avarohana", 25: "Avarohana",
    2: "Arohana", 11: "Arohana", 20: "Arohana",
    6: "Avarohana", 15: "Avarohana", 24: "Avarohana",
    3: "Arohana", 12: "Arohana", 21: "Arohana",
    5: "Avarohana", 14: "Avarohana", 23: "Avarohana",
    4: "Central", 13: "Central", 22: "Central",
}

NADI_TA: Dict[str, str] = {
    "Adi": "வாதம்",
    "Aadi": "வாதம்",
    "Vata": "வாதம்",
    "Madhya": "பித்தம்",
    "Pitta": "பித்தம்",
    "Antya": "சிலேத்துமம்",
    "Kapha": "சிலேத்துமம்",
}

DASHA_ORDER: List[str] = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS: Dict[str, float] = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
DASHA_TA: Dict[str, str] = {
    "Ketu": "கேது", "Venus": "சுக்கிரன்", "Sun": "சூரியன்",
    "Moon": "சந்திரன்", "Mars": "செவ்வாய்", "Rahu": "ராகு",
    "Jupiter": "குரு", "Saturn": "சனி", "Mercury": "புதன்",
}
PLANET_SHORT_TA: Dict[str, str] = {
    "Sun": "சூ", "Moon": "சந்", "Mars": "செ", "Mercury": "பு",
    "Jupiter": "குரு", "Venus": "சுக்", "Saturn": "சனி", "Rahu": "ரா", "Ketu": "கே",
}
DASA_COLORS: Dict[str, Dict[str, str]] = {
    "Sun": {"bg": "#F59E0B", "light_bg": "#FDE68A", "text": "#1E293B"},
    "Moon": {"bg": "#D1D5DB", "light_bg": "#E5E7EB", "text": "#1E293B"},
    "Mars": {"bg": "#EF4444", "light_bg": "#FCA5A5", "text": "#FFFFFF"},
    "Mercury": {"bg": "#22C55E", "light_bg": "#86EFAC", "text": "#FFFFFF"},
    "Jupiter": {"bg": "#FACC15", "light_bg": "#FEF08A", "text": "#1E293B"},
    "Venus": {"bg": "#EC4899", "light_bg": "#F9A8D4", "text": "#FFFFFF"},
    "Saturn": {"bg": "#334C96", "light_bg": "#93A8D8", "text": "#FFFFFF"},
    "Rahu": {"bg": "#374151", "light_bg": "#9CA3AF", "text": "#FFFFFF"},
    "Ketu": {"bg": "#6B7280", "light_bg": "#D1D5DB", "text": "#FFFFFF"},
}

DOSHA_AUDIT_META: List[Tuple[str, str]] = [
    ("kuja_dosha", "செவ்வாய் தோஷம்"),
    ("naga_dosha", "நாக தோஷம்"),
    ("putra_dosha", "புத்ர தோஷம்"),
    ("panchanai_dosha", "பஞ்சணை தோஷம் (படுக்கை வசதிகள்)"),
    ("surya_dosha", "சூரிய தோஷம் (அகங்காரம் / ஆதிக்கம்)"),
    ("shukra_dosha", "சுக்ர தோஷம் (வெள்ளி கிரகப் பிறழ்வு)"),
    ("seventh_house_dosha", "7 ஆம் வீடு தோஷம்"),
    ("seventh_lord_dosha", "7 ஆம் அதிபதி தோஷம்"),
    ("malefic_conjunctions", "தீய கிரக சேர்க்கைகள்"),
    ("vadha_vainashika", "வதை வைநாசிகம்"),
]


def safe_dict(val: Any) -> Dict[str, Any]:
    """Guarantees a dictionary return without AttributeError on str or None."""
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {}


def get_logo_data_uri() -> str:
    """Returns a base64 PNG data URI for `backend/app/assets/logo.png` if present."""
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def get_nak_index_from_name(name: Optional[str]) -> Optional[int]:
    """Resolves a 0-based nakshatra index from its English or spelling-variant name."""
    if not name:
        return None
    norm = str(name).lower().replace(" ", "").replace("oo", "u")
    for idx, candidate in enumerate(NAKSHATRA_NAMES_EN):
        cand_norm = candidate.lower().replace(" ", "").replace("oo", "u")
        if cand_norm == norm or cand_norm.startswith(norm) or norm.startswith(cand_norm):
            return idx
    return None


def get_sign_ta(sign_name: Optional[str], sign_ta: Optional[str]) -> str:
    if sign_ta:
        return str(sign_ta)
    if sign_name and sign_name in SIGN_NAME_TO_IDX:
        return SIGN_NAMES_TA[SIGN_NAME_TO_IDX[sign_name]]
    return str(sign_name or "-")


def format_birth_date_with_age(dob_str: Optional[str]) -> str:
    if not dob_str:
        return "-"
    try:
        dob = date.fromisoformat(str(dob_str)[:10])
    except ValueError:
        return str(dob_str)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return f"{dob.day:02d}-{months[dob.month - 1]}-{dob.year} ({max(0, age)} Yrs)"


def format_points(val: Any) -> str:
    try:
        num = float(val or 0.0)
    except (TypeError, ValueError):
        return "0"
    return str(int(num)) if num.is_integer() else f"{num:.1f}".rstrip("0").rstrip(".")


def _normalize_poruthams_map(raw: Any) -> Dict[str, Dict[str, Any]]:
    """Normalizes `tamil_porutham.poruthams` from either dict or list form."""
    if isinstance(raw, dict):
        return {str(k): safe_dict(v) for k, v in raw.items()}
    if isinstance(raw, list):
        out: Dict[str, Dict[str, Any]] = {}
        for item in raw:
            d = safe_dict(item)
            key = d.get("porutham_id") or d.get("id") or d.get("name")
            if key:
                out[str(key).lower().replace(" ", "_")] = d
        return out
    return {}


def _normalize_kootas_map(raw: Any) -> Dict[str, Dict[str, Any]]:
    if isinstance(raw, dict):
        return {str(k): safe_dict(v) for k, v in raw.items()}
    if isinstance(raw, list):
        out: Dict[str, Dict[str, Any]] = {}
        for item in raw:
            d = safe_dict(item)
            key = d.get("koota_id") or d.get("id") or d.get("name")
            if key:
                out[str(key).lower().replace(" ", "_")] = d
        return out
    return {}


def _compute_fallback_dasa_sequence(
    moon_deg: Optional[float],
    dob_str: Optional[str],
    nak_idx: Optional[int],
) -> List[Dict[str, Any]]:
    """Deterministic fallback Vimshottari timeline when `print_report_data` is absent."""
    try:
        dob = date.fromisoformat(str(dob_str)[:10]) if dob_str else date(1995, 1, 1)
    except ValueError:
        dob = date(1995, 1, 1)
    birth_yr = dob.year + (dob.month - 1) / 12.0 + (dob.day - 1) / 365.25

    if moon_deg is not None:
        nak_span = 360.0 / 27.0
        deg_norm = float(moon_deg) % 360.0
        n_idx = int(deg_norm / nak_span)
        rem_frac = 1.0 - (deg_norm - n_idx * nak_span) / nak_span
    else:
        n_idx = nak_idx if nak_idx is not None else 0
        rem_frac = 0.5

    start_lord_idx = n_idx % 9
    mds: List[Dict[str, Any]] = []
    cur = birth_yr
    for offset in range(9):
        lord = DASHA_ORDER[(start_lord_idx + offset) % 9]
        total_y = DASHA_YEARS[lord]
        dur = total_y * rem_frac if offset == 0 else total_y
        end = cur + dur
        b_start_idx = DASHA_ORDER.index(lord)
        bhuktis: List[Dict[str, Any]] = []
        b_cur = end - total_y
        for j in range(9):
            b_lord = DASHA_ORDER[(b_start_idx + j) % 9]
            b_dur = (total_y * DASHA_YEARS[b_lord]) / 120.0
            b_end = b_cur + b_dur
            if b_end > cur:
                bhuktis.append({
                    "lord_en": b_lord,
                    "short_ta": PLANET_SHORT_TA[b_lord],
                    "start_year": max(cur, b_cur),
                    "end_year": b_end,
                })
            b_cur = b_end
        mds.append({
            "lord_en": lord,
            "lord_ta": DASHA_TA[lord],
            "start_year": cur,
            "end_year": end,
            "start_cal_year": round(cur),
            "end_cal_year": round(end),
            "bhuktis": bhuktis,
        })
        cur = end
    return mds


def _build_chart_cells(chart_data: Any, fallback_asc_sign: Optional[str]) -> Dict[int, List[str]]:
    """Groups Tamil planet abbreviations (+ retrograde `(வ)`) by zodiac sign 1..12."""
    c_dict = safe_dict(chart_data)
    asc_dict = safe_dict(c_dict.get("ascendant"))
    asc_sign = asc_dict.get("sign_index") or c_dict.get("ascendant_sign")
    if isinstance(asc_sign, str) and asc_sign in SIGN_NAME_TO_IDX:
        asc_sign = SIGN_NAME_TO_IDX[asc_sign]
    if not isinstance(asc_sign, int) and fallback_asc_sign:
        asc_sign = SIGN_NAME_TO_IDX.get(str(fallback_asc_sign), 1)
    if not isinstance(asc_sign, int) or not (1 <= asc_sign <= 12):
        asc_sign = 1

    cells: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    cells[asc_sign].append("ல")

    raw_planets = c_dict.get("planets") or []
    planets_list = list(raw_planets.values()) if isinstance(raw_planets, dict) else (raw_planets if isinstance(raw_planets, list) else [])
    for p in planets_list:
        if not isinstance(p, dict):
            continue
        p_name = str(p.get("name") or "")
        abbr = PLANET_CHART_ABBR_TA.get(p_name)
        if not abbr:
            continue
        s_idx = p.get("sign_index")
        if not isinstance(s_idx, int) or not (1 <= s_idx <= 12):
            continue
        is_retro = bool(p.get("is_retrograde")) and p_name not in ("Rahu", "Ketu")
        cells[s_idx].append(f"{abbr}(வ)" if is_retro else abbr)

    return cells


def _fallback_dosha_audit(dosha_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    def _kuja_cell(k_obj: Any) -> Dict[str, Any]:
        kd = safe_dict(k_obj)
        if not kd or not kd.get("is_present"):
            return {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
        reason = kd.get("explanation_ta") or kd.get("explanation_en") or ""
        if kd.get("is_cancelled"):
            return {"status": "MITIGATED", "severity_percent": 0, "reasons_ta": [str(reason)] if reason else ["தோஷ நிவர்த்தி பெறப்பட்டது."]}
        return {"status": "PRESENT", "severity_percent": 40, "reasons_ta": [str(reason)] if reason else []}

    g_kuja = _kuja_cell(dosha_data.get("groom_kuja"))
    b_kuja = _kuja_cell(dosha_data.get("bride_kuja"))
    rows: List[Dict[str, Any]] = []
    for d_id, label_ta in DOSHA_AUDIT_META:
        if d_id == "kuja_dosha":
            rows.append({"id": d_id, "label_ta": label_ta, "groom": g_kuja, "bride": b_kuja})
        else:
            none_cell = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
            rows.append({"id": d_id, "label_ta": label_ta, "groom": none_cell, "bride": none_cell})
    return rows


def build_marriage_print_view_model(data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a compatibility response dict into the exact 5-page print/PDF view model."""
    d = safe_dict(data)
    gp = safe_dict(d.get("groom_profile"))
    bp = safe_dict(d.get("bride_profile"))
    poruthams = _normalize_poruthams_map(safe_dict(d.get("tamil_porutham")).get("poruthams"))
    kootas = _normalize_kootas_map(safe_dict(d.get("ashtakoota")).get("kootas"))
    prd = safe_dict(d.get("print_report_data"))

    g_nak_idx = safe_dict(poruthams.get("dina")).get("groom_input", {}).get("nakshatra_index")
    if g_nak_idx is None:
        g_nak_idx = get_nak_index_from_name(gp.get("moon_nakshatra"))
    b_nak_idx = safe_dict(poruthams.get("dina")).get("bride_input", {}).get("nakshatra_index")
    if b_nak_idx is None:
        b_nak_idx = get_nak_index_from_name(bp.get("moon_nakshatra"))

    g_nak_ta = gp.get("moon_nakshatra_tamil") or (NAKSHATRA_NAMES_TA[g_nak_idx] if isinstance(g_nak_idx, int) and 0 <= g_nak_idx < 27 else str(gp.get("moon_nakshatra") or "-"))
    b_nak_ta = bp.get("moon_nakshatra_tamil") or (NAKSHATRA_NAMES_TA[b_nak_idx] if isinstance(b_nak_idx, int) and 0 <= b_nak_idx < 27 else str(bp.get("moon_nakshatra") or "-"))

    g_rasi_ta = get_sign_ta(gp.get("moon_sign"), gp.get("moon_sign_tamil"))
    b_rasi_ta = get_sign_ta(bp.get("moon_sign"), bp.get("moon_sign_tamil"))
    g_lagna_ta = get_sign_ta(gp.get("ascendant_sign"), gp.get("ascendant_sign_tamil"))
    b_lagna_ta = get_sign_ta(bp.get("ascendant_sign"), bp.get("ascendant_sign_tamil"))

    g_moon_sign_idx = safe_dict(safe_dict(poruthams.get("rasi")).get("groom_input")).get("moon_sign_index") or SIGN_NAME_TO_IDX.get(str(gp.get("moon_sign") or ""), 1)
    b_moon_sign_idx = safe_dict(safe_dict(poruthams.get("rasi")).get("bride_input")).get("moon_sign_index") or SIGN_NAME_TO_IDX.get(str(bp.get("moon_sign") or ""), 1)

    g_gana_raw = str(safe_dict(safe_dict(poruthams.get("gana")).get("groom_input")).get("gana") or "")
    b_gana_raw = str(safe_dict(safe_dict(poruthams.get("gana")).get("bride_input")).get("gana") or "")

    g_yoni_ta = (YONI_BY_NAK_IDX_TA.get(g_nak_idx) if isinstance(g_nak_idx, int) else None) or ANIMAL_TA.get(str(safe_dict(safe_dict(poruthams.get("yoni")).get("groom_input")).get("yoni_animal") or ""), "-")
    b_yoni_ta = (YONI_BY_NAK_IDX_TA.get(b_nak_idx) if isinstance(b_nak_idx, int) else None) or ANIMAL_TA.get(str(safe_dict(safe_dict(poruthams.get("yoni")).get("bride_input")).get("yoni_animal") or ""), "-")

    g_rajju_raw = str(safe_dict(safe_dict(poruthams.get("rajju")).get("groom_input")).get("rajju") or "")
    b_rajju_raw = str(safe_dict(safe_dict(poruthams.get("rajju")).get("bride_input")).get("rajju") or "")
    g_rajju_dir = RAJJU_DIR_TA.get(RAJJU_DIRECTION_BY_NAK_IDX.get(g_nak_idx, ""), "") if isinstance(g_nak_idx, int) else ""
    b_rajju_dir = RAJJU_DIR_TA.get(RAJJU_DIRECTION_BY_NAK_IDX.get(b_nak_idx, ""), "") if isinstance(b_nak_idx, int) else ""
    g_rajju_ta = f"{RAJJU_TA.get(g_rajju_raw, g_rajju_raw)} {g_rajju_dir}".strip() or "-"
    b_rajju_ta = f"{RAJJU_TA.get(b_rajju_raw, b_rajju_raw)} {b_rajju_dir}".strip() or "-"

    nadi_koota = safe_dict(kootas.get("nadi"))
    nadi_passed = bool(nadi_koota and float(nadi_koota.get("earned_points", 0) or 0) > 0)
    g_nadi_raw = str(safe_dict(nadi_koota.get("groom_input")).get("nadi") or "")
    b_nadi_raw = str(safe_dict(nadi_koota.get("bride_input")).get("nadi") or "")
    g_nadi_ta = NADI_TA.get(g_nadi_raw, g_nadi_raw) or "-"
    b_nadi_ta = NADI_TA.get(b_nadi_raw, b_nadi_raw) or "-"

    matching_rows = [
        {"label": "தினம்", "desc": "நீண்ட ஆயுளும் ஆரோக்கியமும்", "groom_val": g_nak_ta, "bride_val": b_nak_ta, "pass": bool(safe_dict(poruthams.get("dina")).get("is_favorable"))},
        {"label": "கணம்", "desc": "கருத்துப் பரிமாற்றமும் மகிழ்ச்சியும்", "groom_val": GANA_TA.get(g_gana_raw, g_gana_raw) or "-", "bride_val": GANA_TA.get(b_gana_raw, b_gana_raw) or "-", "pass": bool(safe_dict(poruthams.get("gana")).get("is_favorable"))},
        {"label": "மகேந்திரம்", "desc": "வாரிசுகளும் குழந்தைகளும் வளர்வது", "groom_val": g_nak_ta, "bride_val": b_nak_ta, "pass": bool(safe_dict(poruthams.get("mahendra")).get("is_favorable"))},
        {"label": "ஸ்திரீ தீர்க்கம்", "desc": "மனைவியின் ஆயுள், ஆரோக்கியம் மற்றும் ஐஸ்வர்யம்.", "groom_val": g_nak_ta, "bride_val": b_nak_ta, "pass": bool(safe_dict(poruthams.get("sthree_deergha")).get("is_favorable"))},
        {"label": "யோனி", "desc": "அன்பான மற்றும் பரஸ்பர மகிழ்ச்சி", "groom_val": g_yoni_ta, "bride_val": b_yoni_ta, "pass": bool(safe_dict(poruthams.get("yoni")).get("is_favorable"))},
        {"label": "ராசி", "desc": "வம்சத்தின் வளர்ச்சி", "groom_val": g_rasi_ta, "bride_val": b_rasi_ta, "pass": bool(safe_dict(poruthams.get("rasi")).get("is_favorable"))},
        {"label": "ராசி அதிபதி", "desc": "வாரிசுகளின் வளர்ச்சி", "groom_val": SIGN_LORD_TA.get(g_moon_sign_idx, "-"), "bride_val": SIGN_LORD_TA.get(b_moon_sign_idx, "-"), "pass": bool(safe_dict(poruthams.get("rasi_adhipathi")).get("is_favorable"))},
        {"label": "வசியம்", "desc": "பரஸ்பர நட்பு", "groom_val": g_rasi_ta, "bride_val": b_rasi_ta, "pass": bool(safe_dict(poruthams.get("vasya")).get("is_favorable"))},
        {"label": "ரஜ்ஜு", "desc": "திருமண அதிர்ஷ்டமும் மங்களமும் வளர்வது", "groom_val": g_rajju_ta, "bride_val": b_rajju_ta, "pass": bool(safe_dict(poruthams.get("rajju")).get("is_favorable"))},
        {"label": "நாடி", "desc": "நல்ல ஆரோக்கியம்", "groom_val": g_nadi_ta, "bride_val": b_nadi_ta, "pass": nadi_passed},
        {"label": "வேதை", "desc": "நட்பும் ஒற்றுமையும்", "groom_val": g_nak_ta, "bride_val": b_nak_ta, "pass": bool(safe_dict(poruthams.get("vedha")).get("is_favorable"))},
    ]

    passed_count_11 = sum(1 for r in matching_rows if r["pass"])
    ashtakoota_pts = safe_dict(d.get("ashtakoota")).get("total_points", 0)
    ashtakoota_str = format_points(ashtakoota_pts)

    dosha_data = safe_dict(d.get("dosha_analysis"))
    kuja_balance = str(dosha_data.get("mutual_kuja_balance") or "")
    default_kuja_summary = (
        "சமதோஷம் (பொருத்தம்)" if kuja_balance == "BALANCED"
        else ("செவ்வாய் தோஷ வேறுபாடு" if "UNBALANCED" in kuja_balance else "செவ்வாய் தோஷம் இல்லை")
    )
    kuja_summary_ta = str(prd.get("kuja_summary_ta") or default_kuja_summary)

    if passed_count_11 >= 8:
        verdict = {"title": "பொருத்தம் சிறப்பானது", "tone": "green"}
    elif passed_count_11 >= 5:
        verdict = {"title": "பொருத்தம் நடுத்தரமானது", "tone": "amber"}
    else:
        verdict = {"title": "பொருத்தம் குறைவானது", "tone": "red"}

    # Page 2 charts
    charts = [
        {"title": "மணமகன் ராசி", "center": "ராசி (1)", "cells": _build_chart_cells(d.get("groom_chart"), gp.get("ascendant_sign"))},
        {"title": "மணமகள் ராசி", "center": "ராசி (1)", "cells": _build_chart_cells(d.get("bride_chart"), bp.get("ascendant_sign"))},
        {"title": "மணமகன் Navamsa", "center": "நவாம்சம் (9)", "cells": _build_chart_cells(d.get("groom_d9_chart"), gp.get("ascendant_navamsa_sign"))},
        {"title": "மணமகள் Navamsa", "center": "நவாம்சம் (9)", "cells": _build_chart_cells(d.get("bride_d9_chart"), bp.get("ascendant_navamsa_sign"))},
    ]

    # Page 3 Dosha audit
    raw_audit = prd.get("dosha_audit")
    dosha_audit = raw_audit if isinstance(raw_audit, list) and len(raw_audit) > 0 else _fallback_dosha_audit(dosha_data)

    # Page 4 Dasa Bhukti timeline (strictly synced with Page 4 Print layout)
    now_dt = datetime.now()
    current_year_num = now_dt.year + (now_dt.month - 1) / 12.0
    dbs = safe_dict(prd.get("dasa_bhukti_sequence"))
    groom_mds = dbs.get("groom_mahadashas")
    bride_mds = dbs.get("bride_mahadashas")
    transitions = dbs.get("transitions")

    if not isinstance(groom_mds, list) or not isinstance(bride_mds, list):
        g_seq = _compute_fallback_dasa_sequence(gp.get("moon_degree"), gp.get("birth_date"), g_nak_idx)
        b_seq = _compute_fallback_dasa_sequence(bp.get("moon_degree"), bp.get("birth_date"), b_nak_idx)
        groom_mds = g_seq
        bride_mds = b_seq

        def _lookup_b(seq: List[Dict[str, Any]], yr: float) -> str:
            for m in seq:
                if m["start_year"] <= yr <= m["end_year"]:
                    bh_list = m.get("bhuktis") or []
                    found = next((b for b in bh_list if b["start_year"] <= yr <= b["end_year"]), bh_list[0] if bh_list else None)
                    return f"{found['short_ta']} Bukthi" if found else ""
            return ""

        w_min = current_year_num - 16
        w_max = current_year_num + 95
        calc_trans: List[Dict[str, Any]] = []
        for md in g_seq[:-1]:
            y = md["end_year"]
            if w_min <= y <= w_max:
                lbl = _lookup_b(b_seq, y)
                if lbl:
                    calc_trans.append({"year": y, "side": "groom", "label_ta": lbl})
        for md in b_seq[:-1]:
            y = md["end_year"]
            if w_min <= y <= w_max:
                lbl = _lookup_b(g_seq, y)
                if lbl:
                    calc_trans.append({"year": y, "side": "bride", "label_ta": lbl})
        calc_trans.sort(key=lambda t: t["year"])
        transitions = calc_trans

    def _active_start(mds: List[Dict[str, Any]]) -> float:
        for md in mds:
            if float(md.get("start_year", 0)) <= current_year_num <= float(md.get("end_year", 0)):
                return float(md["start_year"])
        return float(mds[0].get("start_year", current_year_num - 5)) if mds else current_year_num - 5

    g_active_start = _active_start(groom_mds)
    b_active_start = _active_start(bride_mds)
    min_visible_year = min(g_active_start, b_active_start, current_year_num - 3)
    max_visible_year = max(min_visible_year + 98, current_year_num + 97)

    svg_width = 680.0
    svg_height = 850.0
    top_pad = 14.0
    bot_pad = 18.0
    usable_h = svg_height - top_pad - bot_pad

    def y_for_year(yr: float) -> float:
        clamped = max(min_visible_year, min(max_visible_year, float(yr)))
        return top_pad + ((clamped - min_visible_year) / (max_visible_year - min_visible_year)) * usable_h

    g_visible_mds = [
        md for md in groom_mds
        if float(md.get("end_year", 0)) > g_active_start + 0.01 and float(md.get("start_year", 0)) < max_visible_year
    ]
    b_visible_mds = [
        md for md in bride_mds
        if float(md.get("end_year", 0)) > b_active_start + 0.01 and float(md.get("start_year", 0)) < max_visible_year
    ]

    min_arrow_yr = max(current_year_num - 0.05, max(g_active_start, b_active_start))
    rendered_transitions: List[Dict[str, Any]] = []
    for tr in transitions or []:
        yr = float(tr.get("year", 0))
        if yr < min_arrow_yr or yr > max_visible_year - 0.5:
            continue
        y_pos = y_for_year(yr)
        for prev in rendered_transitions:
            if abs(y_pos - prev["y"]) < 14.0:
                y_pos = prev["y"] + 14.0
        rendered_transitions.append({"y": y_pos, "side": tr.get("side", ""), "label_ta": str(tr.get("label_ta") or "")})

    now_y = y_for_year(current_year_num)
    now_collides_with_g_start = any(
        abs(y_for_year(float(md.get("start_year", 0))) + 4 - (now_y - 4)) < 11.0
        for md in g_visible_mds
    )

    # Page 5 Dasa Sandhi, Planetary pairs & Sage Verdict
    sr_insights = safe_dict(d.get("sivadasan_ravi_insights"))
    sr_dasa = safe_dict(sr_insights.get("dasa_porutham"))
    sr_findings = sr_dasa.get("findings_ta") if isinstance(sr_dasa.get("findings_ta"), list) else []
    dasa_sandhi = safe_dict(prd.get("dasa_sandhi")) or {
        "has_sandhi": sr_dasa.get("verdict") == "AFFLICTED",
        "summary_ta": sr_findings[0] if sr_findings else "தசா சந்தி அமைப்பு சரிபார்க்கப்பட்டது.",
        "note_ta": "குறிப்பு: தசா சந்தி என்பது, தம்பதியர் இருவரும் ஒரு வருட காலத்திற்குள் புதிய மகா தசைக்குள் நுழைவதைக் குறிக்கிறது. பாரம்பரியமாக, இது தம்பதியருக்கு ஒரு நிலையற்ற காலமாகக் கருதப்படுகிறது.",
    }

    pa = safe_dict(prd.get("planetary_analysis"))
    harmonious = pa.get("harmonious_connections") if isinstance(pa.get("harmonious_connections"), list) else []
    incompatible = pa.get("incompatible_combinations") if isinstance(pa.get("incompatible_combinations"), list) else []

    sv = safe_dict(prd.get("sage_verdict"))
    sage_verdict_ta = str(
        sv.get("summary_ta")
        or (
            f"பொருத்தம் மதிப்பெண் {passed_count_11}/11 ஆகும். அஷ்டகூட மதிப்பெண்: {ashtakoota_str}/36. "
            f"{kuja_summary_ta}. மேலும் மதிப்பாய்வு மற்றும் முடிவெடுப்பதற்கு விரிவான தோஷ பகுப்பாய்வு அட்டவணையை தயவுசெய்து சரிபார்க்கவும்."
        )
    )

    # Page 6: Additional compatibility sections (Ashtakoota 8 Kootas, Papasamya, KP, Guru Balam, Navamsa, Remedies)
    ash_raw = safe_dict(d.get("ashtakoota"))
    ash_threshold_str = format_points(ash_raw.get("minimum_threshold", 18.0))
    ash_threshold_met = bool(
        ash_raw.get("is_threshold_met")
        if "is_threshold_met" in ash_raw
        else float(ash_raw.get("total_points", 0) or 0) >= float(ash_raw.get("minimum_threshold", 18.0) or 18.0)
    )

    ashtakoota_rows: List[Dict[str, Any]] = []
    for k_id, k_label_ta, k_max_default, k_sig_ta in ASHTAKOOTA_META_TA:
        k_obj = safe_dict(kootas.get(k_id))
        max_pts = float(k_obj.get("max_points", k_max_default) or k_max_default)
        earned_pts = float(k_obj.get("earned_points", 0.0) or 0.0)
        is_cancelled = bool(k_obj.get("is_cancelled"))
        cancel_reason = str(k_obj.get("cancellation_reason") or "").strip()
        if is_cancelled:
            st_ta = "தோஷ நிவர்த்தி"
            st_tone = "green"
        elif earned_pts >= max_pts * 0.5:
            st_ta = "சாதகம்"
            st_tone = "green"
        elif earned_pts > 0:
            st_ta = "பகுதி"
            st_tone = "amber"
        else:
            st_ta = "தோஷம்"
            st_tone = "red"
        ashtakoota_rows.append({
            "id": k_id,
            "label_ta": k_label_ta,
            "sig_ta": k_sig_ta,
            "earned_str": format_points(earned_pts),
            "max_str": format_points(max_pts),
            "status_ta": st_ta,
            "status_tone": st_tone,
            "cancel_reason": cancel_reason,
        })

    # Papasamya
    g_papa = safe_dict(dosha_data.get("groom_papasamya"))
    b_papa = safe_dict(dosha_data.get("bride_papasamya"))
    papa_verdict = str(dosha_data.get("papasamya_verdict") or "TOLERABLE").upper()
    papa_tone = "green" if papa_verdict == "FAVORABLE" else ("red" if papa_verdict == "UNFAVORABLE" else "amber")
    papa_diff = dosha_data.get("papasamya_diff_percent")
    papa_diff_str = f"{float(papa_diff):.1f}%" if papa_diff is not None else "-"
    g_papa_frames = (
        f"லக்னம்: {format_points(g_papa.get('lagna_papam'))} | சந்திரன்: {format_points(g_papa.get('moon_papam'))} | சுக்கிரன்: {format_points(g_papa.get('venus_papam'))}"
        if g_papa
        else "-"
    )
    b_papa_frames = (
        f"லக்னம்: {format_points(b_papa.get('lagna_papam'))} | சந்திரன்: {format_points(b_papa.get('moon_papam'))} | சுக்கிரன்: {format_points(b_papa.get('venus_papam'))}"
        if b_papa
        else "-"
    )
    papasamya_vm = {
        "groom_total": format_points(g_papa.get("total_papam")),
        "bride_total": format_points(b_papa.get("total_papam")),
        "groom_frames": g_papa_frames,
        "bride_frames": b_papa_frames,
        "diff_str": papa_diff_str,
        "verdict_ta": PAPASAMYA_VERDICT_TA.get(papa_verdict, papa_verdict),
        "verdict_tone": papa_tone,
        "explanation_ta": str(dosha_data.get("papasamya_explanation_ta") or "இருவரின் பாபசாம்ய புள்ளிகள் ஒப்பிடப்பட்டன."),
    }

    # KP 7th CSL & Ruling Planets
    kp_raw = safe_dict(d.get("kp_marriage"))
    g_kp_csl = safe_dict(safe_dict(kp_raw.get("groom_analysis")).get("csl_7th"))
    b_kp_csl = safe_dict(safe_dict(kp_raw.get("bride_analysis")).get("csl_7th"))
    g_csl_en = str(g_kp_csl.get("sub_lord") or kp_raw.get("groom_7th_csl_planet") or "-")
    b_csl_en = str(b_kp_csl.get("sub_lord") or kp_raw.get("bride_7th_csl_planet") or "-")
    g_kp_verdict_en = str(g_kp_csl.get("verdict") or kp_raw.get("groom_7th_csl_promise") or "-").upper()
    b_kp_verdict_en = str(b_kp_csl.get("verdict") or kp_raw.get("bride_7th_csl_promise") or "-").upper()
    g_supp = g_kp_csl.get("supporting_houses_signified") or []
    b_supp = b_kp_csl.get("supporting_houses_signified") or []
    rp_level_en = str(kp_raw.get("ruling_planets_agreement_level") or kp_raw.get("significators_agreement") or "-").upper()
    shared_rp_list = [PLANET_NAME_TA.get(str(p), str(p)) for p in (kp_raw.get("shared_ruling_planets") or [])]
    kp_vm = {
        "available": bool(kp_raw),
        "groom_csl_ta": PLANET_NAME_TA.get(g_csl_en, g_csl_en),
        "groom_verdict_ta": KP_VERDICT_TA.get(g_kp_verdict_en, g_kp_verdict_en),
        "groom_houses": ", ".join(str(h) for h in g_supp) if g_supp else "-",
        "bride_csl_ta": PLANET_NAME_TA.get(b_csl_en, b_csl_en),
        "bride_verdict_ta": KP_VERDICT_TA.get(b_kp_verdict_en, b_kp_verdict_en),
        "bride_houses": ", ".join(str(h) for h in b_supp) if b_supp else "-",
        "agreement_ta": KP_VERDICT_TA.get(rp_level_en, str(kp_raw.get("ruling_planets_agreement_level") or kp_raw.get("significators_agreement") or "ஆய்வு செய்யப்பட்டது")),
        "shared_rp_ta": ", ".join(shared_rp_list) if shared_rp_list else "-",
    }

    # Sivadasan Ravi: Guru Balam, Nadi Yogam, In-Laws, Remedies
    sr_guru = safe_dict(sr_insights.get("guru_balam"))
    sr_nadi = safe_dict(sr_insights.get("nadi_porutham"))
    sr_inlaws = safe_dict(sr_insights.get("in_laws_nakshatras"))
    sr_remedies = safe_dict(sr_insights.get("classical_remedies"))
    parikara = safe_dict(sr_remedies.get("parikara_sthalam"))
    hymns = sr_remedies.get("sacred_hymns") if isinstance(sr_remedies.get("sacred_hymns"), list) else []
    first_hymn = safe_dict(hymns[0]) if hymns else {}

    # Navamsa cross-check
    g_vedic = safe_dict(d.get("groom_vedic"))
    b_vedic = safe_dict(d.get("bride_vedic"))
    g_d9_ca = safe_dict(g_vedic.get("navamsa_cross_analysis"))
    b_d9_ca = safe_dict(b_vedic.get("navamsa_cross_analysis"))

    def _d9_summary(ca: Dict[str, Any], role_ta: str) -> str:
        if not ca:
            return f"{role_ta}: நவாம்ச நிலை சரிபார்க்கப்பட்டது."
        d9_lagna = get_sign_ta(ca.get("d9_lagna_sign_name"), None)
        d9_lord = PLANET_NAME_TA.get(str(ca.get("d9_7th_lord") or ""), str(ca.get("d9_7th_lord") or "-"))
        v_sign = get_sign_ta(ca.get("venus_in_d9_sign"), None)
        return f"{role_ta}: நவாம்ச லக்னம் {d9_lagna}, 7-ஆம் அதிபதி {d9_lord}, சுக்கிரன் {v_sign}"

    boundary_risk = bool(g_d9_ca.get("navamsa_boundary_risk") or b_d9_ca.get("navamsa_boundary_risk"))

    page6_vm = {
        "ashtakoota_rows": ashtakoota_rows,
        "ashtakoota_total_str": ashtakoota_str,
        "ashtakoota_threshold_str": ash_threshold_str,
        "ashtakoota_threshold_met": ash_threshold_met,
        "papasamya": papasamya_vm,
        "kp": kp_vm,
        "guru_balam": {
            "available": bool(sr_guru),
            "label_ta": str(sr_guru.get("label_ta") or "கோட்சார குரு பலம் சரிபார்க்கப்பட்டது"),
            "description_ta": str(sr_guru.get("description_ta") or ""),
        },
        "nadi_yogam": {
            "available": bool(sr_nadi),
            "verdict_ta": str(sr_nadi.get("verdict_ta") or ""),
            "obstacles_ta": (sr_nadi.get("nandi_obstacles_ta") or [])[:2],
        },
        "in_laws": {
            "has_special": bool(sr_inlaws.get("has_special_nakshatra")),
            "findings": [
                {
                    "nakshatra_ta": str(safe_dict(f).get("nakshatra_ta") or ""),
                    "relative_ta": str(safe_dict(f).get("relative_ta") or ""),
                    "is_exempt": bool(safe_dict(f).get("is_exempt")),
                    "explanation_ta": str(safe_dict(f).get("explanation_ta") or ""),
                }
                for f in (sr_inlaws.get("findings") or [])[:3]
            ],
        },
        "navamsa": {
            "groom_ta": _d9_summary(g_d9_ca, "மணமகன்"),
            "bride_ta": _d9_summary(b_d9_ca, "மணமகள்"),
            "boundary_warning": boundary_risk,
        },
        "remedies": {
            "temple_name_ta": str(parikara.get("name_ta") or "குலதெய்வ வழிபாடு & திருக்கோவில் தரிசனம்"),
            "temple_sig_ta": str(parikara.get("significance_ta") or "திருமண நல்வாழ்விற்காக இறை வழிபாடு மேற்கொள்ளவும்."),
            "hymn_title_ta": str(first_hymn.get("title_ta") or ""),
        },
    }

    return {
        "logo_data_uri": get_logo_data_uri(),
        "logo_path": str(LOGO_PATH) if LOGO_PATH.exists() else "",
        "groom": {
            "name": str(gp.get("name") or "Groom"),
            "rasi_ta": g_rasi_ta,
            "nakshatra_pada_ta": f"{g_nak_ta} ({gp.get('moon_pada', 1)})",
            "lagna_ta": g_lagna_ta,
            "dob_age": format_birth_date_with_age(gp.get("birth_date")),
        },
        "bride": {
            "name": str(bp.get("name") or "Bride"),
            "rasi_ta": b_rasi_ta,
            "nakshatra_pada_ta": f"{b_nak_ta} ({bp.get('moon_pada', 1)})",
            "lagna_ta": b_lagna_ta,
            "dob_age": format_birth_date_with_age(bp.get("birth_date")),
        },
        "verdict": verdict,
        "passed_count_11": passed_count_11,
        "kuja_summary_ta": kuja_summary_ta,
        "ashtakoota_str": ashtakoota_str,
        "matching_rows": matching_rows,
        "charts": charts,
        "dosha_audit": dosha_audit,
        "timeline": {
            "current_year_num": current_year_num,
            "min_visible_year": min_visible_year,
            "max_visible_year": max_visible_year,
            "svg_width": svg_width,
            "svg_height": svg_height,
            "top_pad": top_pad,
            "bot_pad": bot_pad,
            "now_y": now_y,
            "now_collides_with_g_start": now_collides_with_g_start,
            "g_visible_mds": g_visible_mds,
            "b_visible_mds": b_visible_mds,
            "rendered_transitions": rendered_transitions,
            "y_for_year": y_for_year,
        },
        "dasa_sandhi": dasa_sandhi,
        "harmonious_connections": harmonious,
        "incompatible_combinations": incompatible,
        "sage_verdict_ta": sage_verdict_ta,
        "page6": page6_vm,
    }
