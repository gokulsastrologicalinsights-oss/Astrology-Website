"""Deterministic Print Report Data Builder for Marriage Compatibility.

Constructs structured, bilingual-ready (primarily Tamil for the traditional
5-page print format) payload sections derived strictly from already-computed
XALEN chart contexts and marriage compatibility findings:
1. 10-Row Dosha Audit (தோஷ ஆய்வு) for Groom & Bride
2. Proportional Vimshottari Dasa-Bhukti Sequence (depth=2, ~81 nodes, <1ms)
3. Upcoming Dasa Sandhi Overlap Detection (தசா சந்தி ஆய்வு)
4. Cross-Chart Same-Sign Planetary Harmony & Conflict Audit (கிரக நிலைகள் ஆய்வு)
5. Synthesized Sage Verdict Narrative (முனிவரின் வாக்கு)
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.dasa_service import generate_vimshottari_hierarchy
from app.services.marriage_engine.models import (
    MarriageChartContext,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    IndividualVedicAnalysis,
    MutualDoshaAnalysisResult,
)
from app.services.timezone_utils import resolve_birth_datetime


PLANET_NAMES_TA: Dict[str, str] = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "ராகு",
    "Ketu": "கேது",
}

PLANET_SHORT_TA: Dict[str, str] = {
    "Sun": "சூ",
    "Moon": "சந்",
    "Mars": "செ",
    "Mercury": "பு",
    "Jupiter": "குரு",
    "Venus": "சுக்",
    "Saturn": "சனி",
    "Rahu": "ரா",
    "Ketu": "கே",
}


def _to_roman_house(num: int) -> str:
    return f"{num}-ஆம் வீட்டில்"


def _is_in_kendra(house_num: int) -> bool:
    return house_num in (1, 4, 7, 10)


def _is_in_trikona(house_num: int) -> bool:
    return house_num in (1, 5, 9)


def _is_in_dusthana(house_num: int) -> bool:
    return house_num in (6, 8, 12)


def _has_neecha_bhanga(ctx: MarriageChartContext, planet_name: str) -> Optional[str]:
    """Checks classical Neecha Bhanga (debilitation cancellation) reasons in Tamil."""
    p = ctx.grahas.get(planet_name)
    if not p:
        return None
    if DEBILITATION_SIGNS.get(planet_name) != p.sign_index:
        return None

    # 1. Dispositor of debilitated sign is in Kendra from Lagna or Moon
    disp_name = SIGN_LORDS.get(p.sign_index)
    if disp_name and disp_name in ctx.grahas:
        disp_p = ctx.grahas[disp_name]
        from_moon = ((disp_p.sign_index - ctx.moon_sign_idx) % 12) + 1
        if _is_in_kendra(disp_p.house) or _is_in_kendra(from_moon):
            disp_ta = PLANET_NAMES_TA.get(disp_name, disp_name)
            return f"பாதுகாப்பு (நீச்ச பங்க ராஜயோகம்): அதன் அதிபதி {disp_ta} கேந்திரத்தில் இருப்பதால் நீச்சம் பங்கமாகிறது."

    # 2. Exaltation lord of the sign is in Kendra from Lagna or Moon
    exalt_sign = EXALTATION_SIGNS.get(planet_name)
    if exalt_sign:
        exalt_lord = SIGN_LORDS.get(exalt_sign)
        if exalt_lord and exalt_lord in ctx.grahas:
            el_p = ctx.grahas[exalt_lord]
            from_moon = ((el_p.sign_index - ctx.moon_sign_idx) % 12) + 1
            if _is_in_kendra(el_p.house) or _is_in_kendra(from_moon):
                el_ta = PLANET_NAMES_TA.get(exalt_lord, exalt_lord)
                return f"பாதுகாப்பு (நீச்ச பங்கம்): உச்ச அதிபதி {el_ta} கேந்திரத்தில் உள்ளார்."

    # 3. Conjunct an exalted planet
    for other_name, other_p in ctx.grahas.items():
        if other_name != planet_name and other_p.sign_index == p.sign_index:
            if EXALTATION_SIGNS.get(other_name) == other_p.sign_index:
                o_ta = PLANET_NAMES_TA.get(other_name, other_name)
                return f"பாதுகாப்பு (நீச்ச பங்கம்): உச்சம் பெற்ற {o_ta}-உடன் இணைந்துள்ளார்."

    return None


def _evaluate_single_chart_dosha_audit(
    ctx: MarriageChartContext,
    vedic: IndividualVedicAnalysis,
    partner_ctx: MarriageChartContext,
) -> Dict[str, Dict[str, Any]]:
    """Evaluates the 10 Tamil Dosha categories for one chart cleanly and deterministically."""
    audit: Dict[str, Dict[str, Any]] = {}

    jup_p = ctx.grahas.get("Jupiter")
    jup_strong = bool(jup_p and (_is_in_kendra(jup_p.house) or _is_in_trikona(jup_p.house)))

    def _malefics_in_house(h_num: int) -> List[str]:
        return [
            p.name
            for p in ctx.grahas.values()
            if p.house == h_num and p.name in NATURAL_MALEFICS
        ]

    # 1. செவ்வாய் தோஷம் (Kuja Dosha)
    kuja = vedic.kuja_dosha
    if not kuja or not kuja.is_present:
        audit["kuja_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    elif kuja.is_cancelled:
        mars_p = ctx.grahas.get("Mars")
        reasons: List[str] = []
        if mars_p:
            if mars_p.sign_index in OWN_SIGNS.get("Mars", set()):
                reasons.append("தோஷ நிவர்த்தி: செவ்வாய் ஆட்சி பெற்றுள்ளது.")
            elif mars_p.sign_index == EXALTATION_SIGNS.get("Mars"):
                reasons.append("தோஷ நிவர்த்தி: செவ்வாய் உச்சம் பெற்றுள்ளது.")
            if jup_p and (jup_p.sign_index == mars_p.sign_index or ctx.has_aspect_on_graha("Jupiter", "Mars")):
                reasons.append("தோஷ நிவர்த்தி: செவ்வாய் குருவுடன் சேர்க்கை / பார்வை பெற்றுள்ளது.")
        if not reasons:
            for c in kuja.cancellations_applied[:2]:
                reasons.append(f"தோஷ நிவர்த்தி: {c}")
        if not reasons:
            reasons.append("தோஷ நிவர்த்தி: சாஸ்திர விதிவிலக்குகளால் செவ்வாய் தோஷம் நீங்கியுள்ளது.")
        audit["kuja_dosha"] = {"status": "MITIGATED", "severity_percent": 0, "reasons_ta": reasons}
    else:
        sev = min(100, max(25, int(round(kuja.effective_intensity_percent))))
        reasons = [
            f"செவ்வாய் லக்னத்திலிருந்து {kuja.mars_house_from_lagna}-ஆம் வீட்டிலும், சந்திரனிலிருந்து {kuja.mars_house_from_moon}-ஆம் வீட்டிலும் உள்ளார்."
        ]
        audit["kuja_dosha"] = {"status": "PRESENT", "severity_percent": sev, "reasons_ta": reasons}

    # 2. நாக தோஷம் (Naga / Sarpa Dosha)
    naga_triggers: List[str] = []
    for node_name in ("Rahu", "Ketu"):
        np = ctx.grahas.get(node_name)
        if np and np.house in (1, 2, 7, 8):
            node_ta = PLANET_NAMES_TA[node_name]
            naga_triggers.append(f"{node_ta} {np.house}-ஆம் வீட்டில் உள்ளார்.")

    if not naga_triggers:
        audit["naga_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        mitigations: List[str] = []
        if jup_p and (ctx.has_aspect_on_house("Jupiter", 1) or ctx.has_aspect_on_house("Jupiter", 7)):
            mitigations.append("தோஷ நிவர்த்தி: குரு பார்வை லக்னம் / 7-ஆம் வீட்டின் மீது உள்ளது.")
        if jup_strong and len(naga_triggers) == 1:
            mitigations.append("பாதுகாப்பு: குரு கேந்திர/திரிகோணத்தில் வலுவாக உள்ளதால் நாக தோஷம் தணிக்கப்படுகிறது.")
        if mitigations:
            audit["naga_dosha"] = {"status": "MITIGATED", "severity_percent": 0, "reasons_ta": mitigations}
        else:
            audit["naga_dosha"] = {
                "status": "PRESENT",
                "severity_percent": min(75, 30 * len(naga_triggers)),
                "reasons_ta": naga_triggers,
            }

    # 3. புத்ர தோஷம் (Putra Dosha — 5th house, 5th lord, Ketu/Rahu/Saturn)
    h5 = vedic.houses_analysis.get(5)
    putra_afflictions: List[str] = []
    if h5:
        for occ in h5.occupants:
            if occ in ("Rahu", "Ketu", "Saturn", "Mars"):
                putra_afflictions.append(f"{PLANET_NAMES_TA.get(occ, occ)} 5-ஆம் வீட்டில் உள்ளார்.")
        if _is_in_dusthana(h5.lord_house):
            putra_afflictions.append(f"5-ஆம் அதிபதி {h5.lord_house}-ஆம் வீட்டில் (ஒரு துர்ஸ்தானம்) உள்ளார்.")
        if h5.lord_dignity == "Debilitated":
            putra_afflictions.append("5-ஆம் அதிபதி நீசமடைந்துள்ளார்.")
    if jup_p and DEBILITATION_SIGNS.get("Jupiter") == jup_p.sign_index:
        putra_afflictions.append("புத்திரகாரகன் குரு நீசமடைந்துள்ளார்.")

    if not putra_afflictions:
        audit["putra_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        protections: List[str] = []
        if jup_strong and len(putra_afflictions) <= 1 and (not h5 or "Rahu" not in h5.occupants and "Ketu" not in h5.occupants):
            protections.append("வலுவான பாதுகாப்பு அமைப்புகளால், குறிப்பிடத்தக்க புத்திர தோஷம் இல்லை.")
            protections.append("பாதுகாப்பு: குரு கேந்திர/திரிகோணத்தில் நல்ல நிலையில் உள்ளார்.")
        elif h5 and ctx.has_aspect_on_house("Jupiter", 5) and len(putra_afflictions) == 1:
            protections.append("பாதுகாப்பு: குரு பகவான் 5-ஆம் வீட்டைப் பார்வையிடுவதால் தோஷ நிவர்த்தி ஏற்படுகிறது.")

        if protections:
            audit["putra_dosha"] = {"status": "MITIGATED", "severity_percent": 0, "reasons_ta": protections}
        else:
            sev = min(90, 25 * len(putra_afflictions))
            audit["putra_dosha"] = {
                "status": "PRESENT",
                "severity_percent": sev,
                "reasons_ta": ["கண்டறியப்பட்ட பாதிப்புகள்:"] + putra_afflictions,
            }

    # 4. பஞ்சணை தோஷம் (12th House Sayana Sukha)
    h12 = vedic.houses_analysis.get(12)
    h12_afflictions: List[str] = []
    if h12:
        for occ in h12.occupants:
            if occ in ("Saturn", "Rahu", "Ketu", "Mars"):
                h12_afflictions.append(f"பாவ கிரகம் {PLANET_NAMES_TA.get(occ, occ)} 12-ஆம் வீட்டில் உள்ளார்.")
        if h12.lord_dignity == "Debilitated":
            h12_afflictions.append("12-ஆம் அதிபதி நீசமடைந்துள்ளார்.")

    if not h12_afflictions:
        audit["panchanai_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        if h12 and (ctx.has_aspect_on_house("Jupiter", 12) or "Venus" in h12.occupants):
            audit["panchanai_dosha"] = {
                "status": "MITIGATED",
                "severity_percent": 0,
                "reasons_ta": ["தோஷ நிவர்த்தி: சுப கிரக பார்வை/சேர்க்கையால் படுக்கை சுகம் பாதுகாக்கப்படுகிறது."],
            }
        else:
            audit["panchanai_dosha"] = {
                "status": "PRESENT",
                "severity_percent": min(75, 30 * len(h12_afflictions)),
                "reasons_ta": h12_afflictions,
            }

    # 5. சூரிய தோஷம் (அகங்காரம் / ஆதிக்கம்)
    sun_p = ctx.grahas.get("Sun")
    sun_afflictions: List[str] = []
    if sun_p:
        if sun_p.house in (1, 7, 8):
            sun_afflictions.append(f"சூரியன் {sun_p.house}-ஆம் வீட்டில் உள்ளார்.")
        if DEBILITATION_SIGNS.get("Sun") == sun_p.sign_index:
            sun_afflictions.append("சூரியன் நீசமடைந்துள்ளார்.")

    if not sun_afflictions:
        audit["surya_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        mit: List[str] = []
        if sun_p and sun_p.sign_index in (1, 5):
            mit.append("தோஷ நிவர்த்தி: சூரியன் ஆட்சி/உச்ச பலத்துடன் உள்ளார்.")
        nb = _has_neecha_bhanga(ctx, "Sun")
        if nb:
            mit.append(nb)
        if jup_p and ctx.has_aspect_on_graha("Jupiter", "Sun"):
            mit.append("பாதுகாப்பு: குரு பகவான் சூரியனைப் பார்வையிடுகிறார்.")
        if mit and len(sun_afflictions) == 1:
            audit["surya_dosha"] = {"status": "MITIGATED", "severity_percent": 0, "reasons_ta": mit}
        else:
            audit["surya_dosha"] = {
                "status": "PRESENT",
                "severity_percent": min(70, 30 * len(sun_afflictions)),
                "reasons_ta": sun_afflictions,
            }

    # 6. சுக்ர தோஷம் (வெள்ளி கிரகப் பிறழ்வு)
    venus_p = ctx.grahas.get("Venus")
    venus_afflictions: List[str] = []
    if venus_p:
        if DEBILITATION_SIGNS.get("Venus") == venus_p.sign_index:
            venus_afflictions.append("சுக்கிர தோஷம்: சுக்கிரன் நீசமடைந்துள்ளார்.")
        if _is_in_dusthana(venus_p.house):
            venus_afflictions.append(f"சுக்கிர தோஷம்: சுக்கிரன் {venus_p.house}-ஆம் வீட்டில் (துர்ஸ்தானம்) உள்ளார்.")
        if venus_p.is_combust:
            venus_afflictions.append("சுக்கிர தோஷம்: சுக்கிரன் அஸ்தமனம் அடைந்துள்ளார்.")

    if not venus_afflictions:
        audit["shukra_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        v_protections: List[str] = []
        nb_v = _has_neecha_bhanga(ctx, "Venus")
        if nb_v:
            v_protections.append(nb_v)
        if jup_p and venus_p and (jup_p.sign_index == venus_p.sign_index or ctx.has_aspect_on_graha("Jupiter", "Venus")):
            v_protections.append("பாதுகாப்பு: சுக்கிரன் சுப கிரகமான குருவுடன் இணைந்துள்ளார் / பார்வை பெற்றுள்ளார்.")
        if v_protections:
            audit["shukra_dosha"] = {
                "status": "MITIGATED",
                "severity_percent": 0,
                "reasons_ta": ["வலுவான பாதுகாப்பு காரணிகளால் குறிப்பிடத்தக்க சுக்கிர தோஷம் இல்லை."] + v_protections,
            }
        else:
            audit["shukra_dosha"] = {
                "status": "PRESENT",
                "severity_percent": min(80, 40 * len(venus_afflictions)),
                "reasons_ta": ["காணப்படும் பாதிப்புகள்:"] + venus_afflictions,
            }

    # 7. 7 ஆம் வீடு தோஷம்
    h7 = vedic.houses_analysis.get(7)
    h7_afflictions: List[str] = []
    if h7:
        for occ in h7.occupants:
            if occ in ("Saturn", "Rahu", "Ketu", "Mars", "Sun"):
                h7_afflictions.append(f"பாப கிரகம் {PLANET_NAMES_TA.get(occ, occ)} 7-ஆம் வீட்டில் உள்ளார்.")

    if not h7_afflictions:
        audit["seventh_house_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        if h7 and (ctx.has_aspect_on_house("Jupiter", 7) or "Jupiter" in h7.occupants):
            audit["seventh_house_dosha"] = {
                "status": "MITIGATED",
                "severity_percent": 0,
                "reasons_ta": ["தோஷ நிவர்த்தி: குரு பார்வை/சேர்க்கை 7-ஆம் வீட்டைப் பாதுகாக்கிறது."],
            }
        else:
            audit["seventh_house_dosha"] = {
                "status": "PRESENT",
                "severity_percent": min(75, 35 * len(h7_afflictions)),
                "reasons_ta": h7_afflictions,
            }

    # 8. 7 ஆம் அதிபதி தோஷம்
    h7_lord_afflictions: List[str] = []
    if h7:
        lord7_name = h7.lord_name
        lord7_p = ctx.grahas.get(lord7_name)
        if _is_in_dusthana(h7.lord_house):
            h7_lord_afflictions.append(f"7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி துர்ஸ்தானமான {h7.lord_house}-ஆம் வீட்டில் உள்ளார்.")
        if h7.lord_dignity == "Debilitated":
            h7_lord_afflictions.append("7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி நீசமடைந்துள்ளார்.")
        if lord7_p:
            if lord7_p.is_combust:
                h7_lord_afflictions.append("7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி அஸ்தமனம் அடைந்துள்ளார்.")
            for m_name in ("Saturn", "Rahu", "Ketu", "Mars"):
                if m_name != lord7_name:
                    m_p = ctx.grahas.get(m_name)
                    if m_p and m_p.sign_index == lord7_p.sign_index:
                        h7_lord_afflictions.append(
                            f"7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி {PLANET_NAMES_TA[m_name]}-உடன் இணைந்துள்ளார்."
                        )

    if not h7_lord_afflictions:
        audit["seventh_lord_dosha"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        sev = min(85, 20 + 20 * len(h7_lord_afflictions)) if len(h7_lord_afflictions) > 1 else 25
        # Match classical 45% when in dusthana + malefic conjunction
        if len(h7_lord_afflictions) == 2:
            sev = 45
        audit["seventh_lord_dosha"] = {
            "status": "PRESENT",
            "severity_percent": sev,
            "reasons_ta": h7_lord_afflictions,
        }

    # 9. தீய கிரக சேர்க்கைகள் (Malefic Conjunctions on 7th Lord / Venus / Moon)
    mal_conj: List[str] = []
    if h7:
        lord7_p = ctx.grahas.get(h7.lord_name)
        if lord7_p:
            for m_name in ("Saturn", "Rahu", "Ketu"):
                m_p = ctx.grahas.get(m_name)
                if m_p and m_name != h7.lord_name and m_p.sign_index == lord7_p.sign_index:
                    mal_conj.append(
                        f"பாப கிரக சேர்க்கை: 7-ஆம் அதிபதி பாவியான {PLANET_NAMES_TA[m_name]}-உடன் இணைந்துள்ளார்."
                    )
    if venus_p:
        for m_name in ("Saturn", "Rahu", "Ketu"):
            m_p = ctx.grahas.get(m_name)
            if m_p and m_p.sign_index == venus_p.sign_index:
                mal_conj.append(
                    f"பாப கிரக சேர்க்கை: சுக்கிரன் பாவியான {PLANET_NAMES_TA[m_name]}-உடன் இணைந்துள்ளார்."
                )

    if not mal_conj:
        audit["malefic_conjunctions"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}
    else:
        audit["malefic_conjunctions"] = {
            "status": "PRESENT",
            "severity_percent": min(75, 20 if len(mal_conj) == 1 else 35 if len(mal_conj) == 2 else 55),
            "reasons_ta": mal_conj,
        }

    # 10. வதை வைநாசிகம் (27th Vainashika Star Check relative to partner)
    dist_from_partner = ((ctx.moon_nakshatra_idx - partner_ctx.moon_nakshatra_idx) % 27) + 1
    if dist_from_partner == 27:
        audit["vadha_vainashika"] = {
            "status": "PRESENT",
            "severity_percent": 80,
            "reasons_ta": ["இணையரின் நட்சத்திரத்திலிருந்து 27-வது நட்சத்திரமாக (வைநாசிகம்) அமைந்துள்ளது."],
        }
    else:
        audit["vadha_vainashika"] = {"status": "NONE", "severity_percent": 0, "reasons_ta": []}

    return audit


def _build_dasa_timeline(ctx: MarriageChartContext) -> Tuple[List[Dict[str, Any]], float]:
    """Builds depth=2 Vimshottari Mahadasha + Bhukti timeline (<1ms)."""
    t_str = ctx.birth_time_iso[:8] if ctx.birth_time_iso else "12:00:00"
    tz_str = ctx.timezone or "Asia/Kolkata"
    try:
        local_dt, _, birth_jd, _, offset_hours = resolve_birth_datetime(
            ctx.birth_date_iso,
            t_str,
            tz_str,
        )
        birth_date_obj = local_dt.date()
    except Exception:
        birth_date_obj = date.fromisoformat(ctx.birth_date_iso)
        birth_jd = 2450000.0
        offset_hours = 5.5

    tree, _ = generate_vimshottari_hierarchy(
        moon_lon=ctx.moon_degree,
        birth_jd=birth_jd,
        birth_date=birth_date_obj,
        utc_offset_hours=offset_hours,
        depth=2,
    )

    def _to_decimal_year(iso_str: str) -> float:
        d = date.fromisoformat(iso_str[:10])
        return round(d.year + (d.timetuple().tm_yday - 1) / 365.25, 4)

    def _fmt_mon_year(iso_str: str) -> str:
        d = date.fromisoformat(iso_str[:10])
        return d.strftime("%b-%Y")

    mds: List[Dict[str, Any]] = []
    for node in tree:
        bhuktis = [
            {
                "lord_en": b.lord,
                "lord_ta": PLANET_NAMES_TA.get(b.lord, b.lord),
                "short_ta": PLANET_SHORT_TA.get(b.lord, b.lord[:2]),
                "start_date_iso": b.start_date_iso,
                "end_date_iso": b.end_date_iso,
                "start_year": _to_decimal_year(b.start_date_iso),
                "end_year": _to_decimal_year(b.end_date_iso),
            }
            for b in node.sub_periods
        ]
        mds.append({
            "lord_en": node.lord,
            "lord_ta": PLANET_NAMES_TA.get(node.lord, node.lord),
            "start_date_iso": node.start_date_iso,
            "end_date_iso": node.end_date_iso,
            "start_year": _to_decimal_year(node.start_date_iso),
            "end_year": _to_decimal_year(node.end_date_iso),
            "start_cal_year": int(node.start_date_iso[:4]),
            "end_cal_year": int(node.end_date_iso[:4]),
            "start_mon_year": _fmt_mon_year(node.start_date_iso),
            "end_mon_year": _fmt_mon_year(node.end_date_iso),
            "bhuktis": bhuktis,
        })

    return mds, birth_jd


def _lookup_bhukti_at_year(mahadashas: List[Dict[str, Any]], dec_year: float) -> Optional[Dict[str, Any]]:
    for md in mahadashas:
        if md["start_year"] <= dec_year <= md["end_year"]:
            for b in md.get("bhuktis", []):
                if b["start_year"] <= dec_year <= b["end_year"]:
                    return b
            if md.get("bhuktis"):
                return md["bhuktis"][0]
    return None


def _evaluate_dasa_sandhi_overlaps(
    groom_mds: List[Dict[str, Any]],
    bride_mds: List[Dict[str, Any]],
    current_year: int,
) -> Dict[str, Any]:
    """Detects Mahadasha transitions of groom and bride occurring within ~14 months in upcoming years."""
    overlaps: List[Dict[str, Any]] = []
    window_start = current_year - 1
    window_end = current_year + 45

    for idx_g in range(len(groom_mds) - 1):
        g_cur = groom_mds[idx_g]
        g_nxt = groom_mds[idx_g + 1]
        gy = g_cur["end_year"]
        if not (window_start <= gy <= window_end):
            continue

        for idx_b in range(len(bride_mds) - 1):
            b_cur = bride_mds[idx_b]
            b_nxt = bride_mds[idx_b + 1]
            by = b_cur["end_year"]
            if not (window_start <= by <= window_end):
                continue

            diff_months = abs(gy - by) * 12.0
            if diff_months <= 14.0:
                overlaps.append({
                    "groom_transition": f"{g_cur['lord_ta']}->{g_nxt['lord_ta']} ({g_cur['end_mon_year']})",
                    "bride_transition": f"{b_cur['lord_ta']}->{b_nxt['lord_ta']} ({b_cur['end_mon_year']})",
                    "diff_months": round(diff_months, 1),
                    "year": round((gy + by) / 2.0, 2),
                })

    overlaps.sort(key=lambda x: x["year"])
    has_sandhi = len(overlaps) > 0

    if has_sandhi:
        first = overlaps[0]
        sev_label = "கடுமையானது" if first["diff_months"] <= 6.0 else "மிதமானது"
        summary_ta = (
            f"{sev_label} தசா சந்தி: {first['groom_transition']} ஆனது "
            f"{first['bride_transition']}-உடன் மேற்பொடிகிறது."
        )
    else:
        sev_label = "இல்லை"
        summary_ta = "அடுத்த 45 ஆண்டுகளில் இருவரின் மகா தசை மாற்றங்களும் ஒரே ஆண்டிற்குள் மேற்பொடியவில்லை."

    return {
        "has_sandhi": has_sandhi,
        "severity_label_ta": sev_label,
        "summary_ta": summary_ta,
        "note_ta": (
            "குறிப்பு: தசா சந்தி என்பது, தம்பதியர் இருவரும் ஒரு வருட காலத்திற்குள் புதிய மகா தசைக்குள் நுழைவதைக் "
            "குறிக்கிறது. பாரம்பரியமாக, இது தம்பதியருக்கு ஒரு நிலையற்ற காலமாகக் கருதப்படுகிறது."
        ),
        "overlaps": overlaps,
    }


def _evaluate_cross_planetary_analysis(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
) -> Dict[str, List[Dict[str, str]]]:
    """Evaluates same-sign cross-chart Graha pairings into harmonious & incompatible lists."""
    harmonious: List[Dict[str, str]] = []
    incompatible: List[Dict[str, str]] = []

    planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    nodes = {"Rahu", "Ketu"}
    hard_malefics = {"Saturn", "Rahu", "Ketu"}

    for gp_name in planets_order:
        gp = groom_ctx.grahas.get(gp_name)
        if not gp:
            continue
        for bp_name in planets_order:
            bp = bride_ctx.grahas.get(bp_name)
            if not bp or gp.sign_index != bp.sign_index:
                continue

            g_ta = PLANET_NAMES_TA[gp_name]
            b_ta = PLANET_NAMES_TA[bp_name]
            pair_set = {gp_name, bp_name}

            # Skip Sun/Moon mundane minor duplicates unless notable
            if gp_name in nodes or bp_name in nodes:
                if gp_name == bp_name:
                    continue
                if "Moon" in pair_set:
                    incompatible.append({
                        "groom_planet_ta": g_ta,
                        "bride_planet_ta": b_ta,
                        "description_ta": (
                            f"பெண் {b_ta} மற்றும் ஆண் {g_ta} - மன அழுத்தம், வீண் பயம் மற்றும் உணர்ச்சி ரீதியான "
                            "குழப்பங்கள் ஏற்பட வாய்ப்புள்ளது. தியானம் மற்றும் பரஸ்பர புரிதல் அவசியம்."
                        ),
                    })
                elif "Mercury" in pair_set:
                    incompatible.append({
                        "groom_planet_ta": g_ta,
                        "bride_planet_ta": b_ta,
                        "description_ta": (
                            f"பெண் {b_ta}, ஆண் {g_ta} - தவறான புரிதல் அல்லது வெளி நபர்களின் தலையீட்டால் "
                            "குடும்பத்தில் மனக்கசப்பு ஏற்படாமல் கவனமாக இருக்க வேண்டும்."
                        ),
                    })
                elif "Saturn" in pair_set:
                    incompatible.append({
                        "groom_planet_ta": g_ta,
                        "bride_planet_ta": b_ta,
                        "description_ta": (
                            f"பெண் {b_ta} - ஆண் {g_ta}: கணவன் மனைவிக்கு இடையே தொழில் நெருக்கடி மற்றும் "
                            "மந்தநிலை ஏற்பட வாய்ப்புள்ளது; பொறுமையுடன் கையாளவும்."
                        ),
                    })
                elif "Venus" in pair_set or "Jupiter" in pair_set or "Mars" in pair_set:
                    incompatible.append({
                        "groom_planet_ta": g_ta,
                        "bride_planet_ta": b_ta,
                        "description_ta": (
                            f"ஆண் {g_ta} - பெண் {b_ta}: கருத்து வேறுபாடுகள் மற்றும் எதிர்பாராத சவால்கள் தோன்றலாம்; "
                            "விட்டுக்கொடுத்து வாழ்வது நன்று."
                        ),
                    })
            elif gp_name == "Saturn" and bp_name == "Mars" or gp_name == "Mars" and bp_name == "Saturn":
                incompatible.append({
                    "groom_planet_ta": g_ta,
                    "bride_planet_ta": b_ta,
                    "description_ta": (
                        f"பெண்ணின் {b_ta} மற்றும் ஆணின் {g_ta}: இந்தச் சேர்க்கை கணவன் மனைவிக்கு இடையில் "
                        "தொழில் நெருக்கடி, மனச்சுமை மற்றும் கருத்து வேறுபாடுகளை ஏற்படுத்தலாம்."
                    ),
                })
            elif (
                (gp_name in ("Jupiter", "Venus") and bp_name in ("Jupiter", "Venus", "Moon", "Mercury", "Mars"))
                or (bp_name in ("Jupiter", "Venus") and gp_name in ("Jupiter", "Venus", "Moon", "Mercury", "Mars"))
            ):
                if gp_name == "Venus" and bp_name == "Venus":
                    desc = (
                        "பெண்ணின் சுக்கிரனும் ஆணின் சுக்கிரனும் ஒரே ராசியில் இருப்பது - இது ஒரு நல்ல மற்றும் "
                        "இணக்கமான உறவை உருவாக்கும்."
                    )
                elif "Jupiter" in pair_set and "Mars" in pair_set:
                    desc = (
                        f"பெண் {b_ta}, ஆண் {g_ta} - நல்ல இணக்கமான உறவு அமையும். நல்ல மகிழ்ச்சி உண்டாகும். "
                        "இரு குடும்பத்தினருக்கும் இடையே சுமுகமான உறவு ஏற்படும்."
                    )
                elif "Jupiter" in pair_set and "Venus" in pair_set:
                    desc = (
                        f"பெண் {b_ta}, ஆண் {g_ta} - ஒரு நல்ல, இணக்கமான உறவு உருவாகும். ஜாதகர் நல்ல வசதிகளைப் "
                        "பெறுவார், மேலும் அவரது வாழ்க்கைத்தரம் மேம்படும்."
                    )
                else:
                    desc = (
                        f"ஆண் {g_ta} மற்றும் பெண் {b_ta} ஒரே ராசியில் இணைவதால் பரஸ்பர அன்பு, குடும்ப ஒற்றுமை "
                        "மற்றும் சுப வளர்ச்சி உண்டாகும்."
                    )
                harmonious.append({
                    "groom_planet_ta": g_ta,
                    "bride_planet_ta": b_ta,
                    "description_ta": desc,
                })
            elif gp_name not in hard_malefics and bp_name not in hard_malefics and gp_name == bp_name:
                harmonious.append({
                    "groom_planet_ta": g_ta,
                    "bride_planet_ta": b_ta,
                    "description_ta": f"இருவரின் {g_ta} கிரகமும் ஒரே ராசியில் அமைந்துள்ளதால் சிந்தனை ஒற்றுமை சிறக்கும்.",
                })

    return {
        "harmonious_connections": harmonious,
        "incompatible_combinations": incompatible,
    }


def build_print_report_data(
    groom_ctx: MarriageChartContext,
    bride_ctx: MarriageChartContext,
    groom_vedic: IndividualVedicAnalysis,
    bride_vedic: IndividualVedicAnalysis,
    mutual_doshas: MutualDoshaAnalysisResult,
    porutham_passed_count_11: int,
    ashtakoota_points: float,
) -> Dict[str, Any]:
    """Builds the deterministic data structure consumed by the 5-page reference Print view."""
    today = date.today()
    current_year = today.year

    # 1. 10-Row Dosha Audit (Page 3)
    groom_audit = _evaluate_single_chart_dosha_audit(groom_ctx, groom_vedic, bride_ctx)
    bride_audit = _evaluate_single_chart_dosha_audit(bride_ctx, bride_vedic, groom_ctx)

    dosha_rows_meta = [
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
    dosha_audit = [
        {
            "id": d_id,
            "label_ta": d_label,
            "groom": groom_audit[d_id],
            "bride": bride_audit[d_id],
        }
        for d_id, d_label in dosha_rows_meta
    ]

    # 2. Dasa-Bhukti Sequence (Page 4)
    groom_mds, _ = _build_dasa_timeline(groom_ctx)
    bride_mds, _ = _build_dasa_timeline(bride_ctx)

    # Strip full nested bhuktis after computing transitions so response stays compact
    transitions: List[Dict[str, Any]] = []
    window_min = current_year - 16
    window_max = current_year + 95

    for md in groom_mds[:-1]:
        ey = md["end_year"]
        if window_min <= ey <= window_max:
            b_bhukti = _lookup_bhukti_at_year(bride_mds, ey)
            if b_bhukti:
                transitions.append({
                    "year": ey,
                    "side": "groom",
                    "label_ta": f"{b_bhukti['short_ta']} Bukthi",
                })

    for md in bride_mds[:-1]:
        ey = md["end_year"]
        if window_min <= ey <= window_max:
            g_bhukti = _lookup_bhukti_at_year(groom_mds, ey)
            if g_bhukti:
                transitions.append({
                    "year": ey,
                    "side": "bride",
                    "label_ta": f"{g_bhukti['short_ta']} Bukthi",
                })

    transitions.sort(key=lambda t: t["year"])

    # 3. Dasa Sandhi (Page 5)
    dasa_sandhi = _evaluate_dasa_sandhi_overlaps(groom_mds, bride_mds, current_year)

    # Compact Mahadasha lists (strip bhuktis list from JSON response to keep payload lean)
    def _compact_mds(mds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {k: v for k, v in md.items() if k != "bhuktis"}
            for md in mds
        ]

    # 4. Cross-Chart Planetary Analysis (Page 5)
    planetary_analysis = _evaluate_cross_planetary_analysis(groom_ctx, bride_ctx)

    # 5. Sage Verdict (Page 5 - முனிவரின் வாக்கு)
    g_kuja_int = groom_vedic.kuja_dosha.effective_intensity_percent if (groom_vedic.kuja_dosha and not groom_vedic.kuja_dosha.is_cancelled) else 0.0
    b_kuja_int = bride_vedic.kuja_dosha.effective_intensity_percent if (bride_vedic.kuja_dosha and not bride_vedic.kuja_dosha.is_cancelled) else 0.0
    kuja_diff_pct = int(round(abs(g_kuja_int - b_kuja_int)))

    samadosham_status_str = (
        mutual_doshas.samadosham.status.value
        if hasattr(mutual_doshas.samadosham.status, "value")
        else str(mutual_doshas.samadosham.status)
    )
    if g_kuja_int == 0.0 and b_kuja_int == 0.0:
        kuja_label_ta = "செவ்வாய் தோஷம் இல்லை"
    elif samadosham_status_str in ("MUTUALLY_MATCHED", "CANCELLED_BY_RULE", "MITIGATED"):
        kuja_label_ta = "செவ்வாய் தோஷ சமநிலை உள்ளது"
    else:
        kuja_label_ta = "செவ்வாய் தோஷம் கவனிக்கப்பட வேண்டும்"

    porutham_desc_ta = (
        "உயர் பொருத்தத்தன்மையில் இருப்பதைக் குறிக்கிறது"
        if porutham_passed_count_11 >= 8
        else "ஏற்றுக்கொள்ளத்தக்க அளவில் இருப்பதைக் குறிக்கிறது"
        if porutham_passed_count_11 >= 6
        else "மேலும் கவனமான ஆய்வு தேவைப்படுவதைக் குறிக்கிறது"
    )
    sandhi_sentence = (
        "தசா சந்தி உள்ளது, இதற்கு கூடுதல் கவனம் தேவைப்படலாம். திருமணம் தசா சந்தி காலத்திற்குப் பிறகு செய்யப்பட வேண்டும்."
        if dasa_sandhi["has_sandhi"]
        else "முக்கிய தசா சந்தி தடைகள் எதுவும் இல்லை; இருவரின் தசா காலங்களும் சுமுகமாக அமைந்துள்ளன."
    )
    remedy_note = (
        "குறிப்பு: தசா சந்தி காலத்தினால் தீர்ப்பு குறைக்கப்பட்டுள்ளது. பரிகார பூஜைகளை செய்யவும்."
        if dasa_sandhi["has_sandhi"]
        else "குறிப்பு: குலதெய்வ வழிபாடு மற்றும் சுப முகூர்த்த தேர்வில் திருமணத்தை மேற்கொள்ளவும்."
    )

    sage_verdict_ta = (
        f"{sandhi_sentence} பொருத்தம் மதிப்பெண் {porutham_passed_count_11}/11 ஆகும், இது ஒட்டுமொத்தப் பொருத்தத்தன்மை "
        f"{porutham_desc_ta}. அஷ்டகூட மதிப்பெண்: {ashtakoota_points:g}/36. "
        f"மணமக்களின் செவ்வாய் தோஷ வலிமை வித்தியாசம் {kuja_diff_pct}% ஆகும், இது {kuja_label_ta} என வகைப்படுத்தப்பட்டுள்ளது. "
        f"மேலும் மதிப்பாய்வு மற்றும் முடிவெடுப்பதற்கு விரிவான தோஷ பகுப்பாய்வு அட்டவணையை தயவுசெய்து சரிபார்க்கவும். {remedy_note}"
    )

    return {
        "dosha_audit": dosha_audit,
        "kuja_summary_ta": kuja_label_ta,
        "dasa_bhukti_sequence": {
            "groom_mahadashas": _compact_mds(groom_mds),
            "bride_mahadashas": _compact_mds(bride_mds),
            "transitions": transitions,
        },
        "dasa_sandhi": dasa_sandhi,
        "planetary_analysis": planetary_analysis,
        "sage_verdict": {
            "summary_ta": sage_verdict_ta,
        },
    }
