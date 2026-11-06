"""Siddhayogi Sivadasan Ravi Marriage Astrology Engine.

Based on the canonical Tamil astrological treatise:
"திருமண யோக பொருத்த திறவுகோல்" (Thirumana Yoga Porutha Thiravukol)
By சித்தயோகி சிவதாசன் ரவி (Siddhayogi Sivadasan Ravi), Sri Aromira Prasuram.

Implements:
1. Dasa Porutham:
   - Eka Dasa Sandhi (ஏக தசா சந்திப்பு): Identical concurrent Mahadashas under age 60.
   - Dasa Maatra Sandhi / Dasa Gandanta (தசை மாற்ற சந்திப்பு): Mahadasha shift within 12 months under age 60.
2. Gochara Guru Balam (கோட்சார குரு பலம்):
   - Transit Jupiter in 2, 5, 7, 9, 11 from Janma Rasi giving Daiva Anugraha (தெய்வ அனுகூலம்).
3. Nadi Astrology Porutham (நாடி ஜோதிட முறை பொருத்தம்):
   - Groom: Guru (Jivatma) & Shukra (Kalathra/Wife).
   - Bride: Shukra (Jivatma) & Sevvai (Bharta/Husband).
   - 1-5-9, 3-7-11, 2-12 planetary connectivity matrices.
4. Nandi Yogam Detection (நந்தியோகம்):
   - Inimical planets (Saturn, Rahu, Moon, Ketu) positioned between Mars and Venus / Guru and Venus.
5. In-Laws Special Nakshatra Doshas & Lagna Exemption Verification:
   - Moolam (Father-in-law / மாமனார்)
   - Aslesha (Mother-in-law / மாமியார்)
   - Jyeshtha (Elder Brother-in-law / மூத்த மைத்துனர்)
   - Visakha (Younger Brother-in-law / இளைய மைத்துனர்)
6. Sacred Thirumurai & Classical Wedding Remedies:
   - Saiva Tirumurai, Andal Kalyanam, Divya Prabandham, and Thirunelveli Nellaiyappar-Kanthimathi Ambal.
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date

import xalen
from app.services.dasa_service import calculate_direct_dasa
from app.services.marriage_engine.models import (
    MarriageChartContext,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
)


def _get_birth_jd(chart: MarriageChartContext) -> float:
    """Computes UTC Julian Day from chart birth date and time."""
    try:
        t_str = chart.birth_time_iso[:8] if chart.birth_time_iso else "12:00:00"
        dt = datetime.strptime(f"{chart.birth_date_iso} {t_str}", "%Y-%m-%d %H:%M:%S")
        hour_dec = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        return float(xalen.swe.julday(dt.year, dt.month, dt.day, hour_dec))
    except Exception:
        return 2450000.0


def _get_dasa_info(chart: MarriageChartContext) -> Tuple[str, float, float]:
    """Calculates active Mahadasha lord, end JD, and native age."""
    b_jd = _get_birth_jd(chart)
    today = date.today()
    try:
        b_date = datetime.strptime(chart.birth_date_iso, "%Y-%m-%d").date()
        age = (today - b_date).days / 365.25
    except Exception:
        age = 28.0

    try:
        dasa_res = calculate_direct_dasa(
            moon_sidereal_deg=chart.moon_degree,
            birth_jd=b_jd,
            target_date=today,
        )
        mahadasha_lord = dasa_res.active_period.mahadasha if dasa_res.active_period else dasa_res.birth_dasa_lord
        end_jd = 0.0
        for node in dasa_res.dasa_tree:
            if node.is_active:
                end_jd = node.end_jd
                break
        return mahadasha_lord, end_jd, age
    except Exception:
        # Fallback based on Moon Nakshatra Lord
        from app.services.marriage_engine.models import NAKSHATRA_LORDS
        lord = NAKSHATRA_LORDS[chart.moon_nakshatra_idx] if 0 <= chart.moon_nakshatra_idx < 27 else "Jupiter"
        return lord, b_jd + 365.25 * 7, age


# ---------------------------------------------------------------------------
# 1. DASA PORUTHAM (தசைப் பொருத்தம்)
# ---------------------------------------------------------------------------

def evaluate_dasa_porutham(
    groom_chart: MarriageChartContext,
    bride_chart: MarriageChartContext,
) -> Dict[str, Any]:
    """Evaluates Eka Dasa Sandhi and Dasa Maatra Sandhi (Dasa Gandanta)."""
    g_dasa, g_end_jd, g_age = _get_dasa_info(groom_chart)
    b_dasa, b_end_jd, b_age = _get_dasa_info(bride_chart)

    is_under_60 = (g_age < 60.0) or (b_age < 60.0)

    # 1. Eka Dasa Sandhi
    is_eka_dasa = (g_dasa.lower() == b_dasa.lower()) if g_dasa and b_dasa else False
    eka_dasa_afflicted = is_eka_dasa and is_under_60

    # 2. Dasa Maatra Sandhi (Transition difference <= 365.25 days)
    transition_diff_days = abs(g_end_jd - b_end_jd) if (g_end_jd > 0 and b_end_jd > 0) else 9999.0
    is_dasa_transition_close = transition_diff_days <= 365.25
    dasa_transition_afflicted = is_dasa_transition_close and is_under_60

    if eka_dasa_afflicted or dasa_transition_afflicted:
        verdict = "AFFLICTED"
        score = 0.25
        verdict_ta = "தசா தோஷம் உள்ளது"
    elif is_eka_dasa or is_dasa_transition_close:
        verdict = "MITIGATED_BY_AGE"
        score = 0.75
        verdict_ta = "வயது முதிர்வால் தோஷமில்லை"
    else:
        verdict = "EXCELLENT"
        score = 1.0
        verdict_ta = "சுப தசா பொருத்தம்"

    findings_en = []
    findings_ta = []

    if eka_dasa_afflicted:
        findings_en.append(
            f"Eka Dasa Sandhi active: Both are running {g_dasa} Mahadasha concurrently under age 60. "
            f"Classical Tamil authority compares this to Rajju Thatu, advising caution and remedial prayers."
        )
        findings_ta.append(
            f"ஏக தசா சந்திப்பு உள்ளது: இருவருக்கும் ஒரே நேரத்தில் {g_dasa} தசை நடைபெறுகிறது (60 வயதிற்குள்). "
            f"சித்தயோகி சிவதாசன் ரவி விதிப்படி இது ரஜ்ஜு தோஷத்திற்கு இணையானது; பரிகாரங்கள் தேவை."
        )
    elif is_eka_dasa:
        findings_en.append(
            f"Eka Dasa Sandhi present ({g_dasa} Dasa), but permitted because native age exceeds 60 years."
        )
        findings_ta.append(
            f"இருவருக்கும் ஒரே {g_dasa} தசை நடைபெற்றாலும், 60 வயதிற்கு மேல் என்பதால் சாஸ்திர விதிவிலக்கு உண்டு."
        )

    if dasa_transition_afflicted:
        findings_en.append(
            f"Dasa Maatra Sandhi (Dasa Gandanta): Both partners change Mahadashas within {int(transition_diff_days)} days "
            f"(less than 1 year). Simultaneous life condition shifts may cause domestic tension."
        )
        findings_ta.append(
            f"தசை மாற்ற சந்திப்பு (தசைக் கண்டாந்தம்): இருவருக்கும் {int(transition_diff_days)} நாட்களுக்குள் (ஒரு வருடத்திற்குள்) "
            f"தசை மாற்றம் நிகழ்வதால் கருத்து வேறுபாடுகள் மற்றும் வாழ்க்கை சூழ்நிலை மாற்றங்கள் ஏற்படும்."
        )
    elif is_dasa_transition_close:
        findings_en.append(
            f"Dasa transition within 1 year detected, but mitigated by age over 60."
        )
        findings_ta.append(
            f"ஒரு வருடத்திற்குள் தசை மாற்றம் நிகழ்ந்தாலும் 60 வயதிற்கு மேல் என்பதால் பாதிப்பு குறைவு."
        )

    if not findings_en:
        findings_en.append(
            f"No Eka Dasa Sandhi or transition clash: Groom is running {g_dasa} Dasa and Bride is running {b_dasa} Dasa. Harmonious timing."
        )
        findings_ta.append(
            f"ஏக தசா சந்திப்போ, தசை மாற்றக் கண்டாந்தமோ இல்லை (மணமகன்: {g_dasa}, மணமகள்: {b_dasa}). தசா பொருத்தம் நன்று."
        )

    return {
        "verdict": verdict,
        "verdict_ta": verdict_ta,
        "score": score,
        "is_eka_dasa": is_eka_dasa,
        "eka_dasa_afflicted": eka_dasa_afflicted,
        "groom_mahadasha": g_dasa,
        "bride_mahadasha": b_dasa,
        "transition_diff_days": round(transition_diff_days, 1),
        "is_dasa_transition_close": is_dasa_transition_close,
        "dasa_transition_afflicted": dasa_transition_afflicted,
        "findings_en": findings_en,
        "findings_ta": findings_ta,
    }


# ---------------------------------------------------------------------------
# 2. GOCHARA GURU BALAM (கோட்சார குரு பலம்)
# ---------------------------------------------------------------------------

def evaluate_gochara_guru_balam(
    groom_chart: MarriageChartContext,
    bride_chart: MarriageChartContext,
) -> Dict[str, Any]:
    """Evaluates Gochara (Transit) Jupiter from Janma Rasi of Groom and Bride."""
    today = date.today()
    cur_jd = 2460310.5 + (today - date(2024, 1, 1)).days
    transit_jupiter_sign = int(((cur_jd - 2460310.5) / 361.3 + 1)) % 12 + 1
    if transit_jupiter_sign <= 0:
        transit_jupiter_sign = 1

    g_rasi = groom_chart.moon_sign_idx
    b_rasi = bride_chart.moon_sign_idx

    g_house = ((transit_jupiter_sign - g_rasi) % 12) + 1
    b_house = ((transit_jupiter_sign - b_rasi) % 12) + 1

    auspicious_houses = {2, 5, 7, 9, 11}
    g_has_guru_balam = g_house in auspicious_houses
    b_has_guru_balam = b_house in auspicious_houses

    jupiter_sign_en = SIGN_NAMES_EN.get(transit_jupiter_sign, "Unknown")
    jupiter_sign_ta = SIGN_NAMES_TA.get(transit_jupiter_sign, "தெரியவில்லை")

    if g_has_guru_balam and b_has_guru_balam:
        status = "FULL_GURU_BALAM"
        score = 1.0
        label_en = "Both Groom & Bride possess Guru Balam"
        label_ta = "இருவருக்கும் பூரண குரு பலம் உள்ளது"
        desc_en = (
            f"Current transit Jupiter is in {jupiter_sign_en} (Groom's {g_house}th house, Bride's {b_house}th house). "
            f"Both enjoy direct Guru Balam. According to Siddhayogi Sivadasan Ravi, divine grace (Daiva Anugraha) "
            f"is abundant, dissolving impediments and blessing the matrimonial alliance."
        )
        desc_ta = (
            f"தற்போது கோட்சார குரு {jupiter_sign_ta} ராசியில் சஞ்சரிக்கிறார் (மணமகனுக்கு {g_house}-ம் இடம், மணமகளுக்கு {b_house}-ம் இடம்). "
            f"இருவருக்கும் குரு பலம் பரிபூரணமாக இருப்பதால் தெய்வ அனுகூலத்தால் தடைகள் அனைத்தும் நீங்கி திருமண வாழ்க்கை இனிதே அமையும்."
        )
    elif g_has_guru_balam or b_has_guru_balam:
        status = "PARTIAL_GURU_BALAM"
        score = 0.7
        benefitted = "Groom" if g_has_guru_balam else "Bride"
        benefitted_ta = "மணமகனுக்கு" if g_has_guru_balam else "மணமகளுக்கு"
        label_en = f"Guru Balam active for {benefitted}"
        label_ta = f"{benefitted_ta} மட்டும் குரு பலம் உள்ளது"
        desc_en = (
            f"Current transit Jupiter is in {jupiter_sign_en}. {benefitted} possesses Guru Balam "
            f"(Groom: {g_house}th, Bride: {b_house}th). Marriage can proceed favorably."
        )
        desc_ta = (
            f"தற்போது கோட்சார குரு {jupiter_sign_ta} ராசியில் உள்ளதால் {benefitted_ta} குரு பலம் உள்ளது. "
            f"திருமணம் செய்ய உகந்த காலமாகும்."
        )
    else:
        status = "NO_CURRENT_GURU_BALAM"
        score = 0.4
        label_en = "Neither possesses direct Gochara Guru Balam"
        label_ta = "இருவருக்கும் தற்போது நேரடி குரு பலம் அமையவில்லை"
        desc_en = (
            f"Transit Jupiter is in {jupiter_sign_en} (Groom: {g_house}th, Bride: {b_house}th). "
            f"Sivadasan Ravi notes: Even without Guru Balam, marriages take place under favorable Dasa-Bhukthi, "
            f"though seeking Lord Shiva/Dakshinamurthy blessings prior to wedding is recommended."
        )
        desc_ta = (
            f"தற்போது கோட்சார குரு மணமகனுக்கு {g_house}-லும், மணமகளுக்கு {b_house}-லும் சஞ்சரிப்பதால் "
            f"நேரடி குரு பலம் அமையவில்லை. இருப்பினும் அனுகூலமான தசா-புக்தி காலத்தில் திருமணம் நடைபெறும்; "
            f"குரு பகவான் மற்றும் குலதெய்வ வழிபாடு செய்து தொடங்கலாம்."
        )

    return {
        "status": status,
        "score": score,
        "label_en": label_en,
        "label_ta": label_ta,
        "transit_jupiter_sign_en": jupiter_sign_en,
        "transit_jupiter_sign_ta": jupiter_sign_ta,
        "groom_house_from_moon": g_house,
        "bride_house_from_moon": b_house,
        "groom_has_balam": g_has_guru_balam,
        "bride_has_balam": b_has_guru_balam,
        "description_en": desc_en,
        "description_ta": desc_ta,
    }


# ---------------------------------------------------------------------------
# 3. NADI ASTROLOGY PORUTHAM & NANDI YOGAM (நாடி ஜோதிட முறை & நந்தியோகம்)
# ---------------------------------------------------------------------------

def evaluate_nadi_porutham_and_nandi_yogam(
    groom_chart: MarriageChartContext,
    bride_chart: MarriageChartContext,
) -> Dict[str, Any]:
    """Evaluates Nadi Porutham & Nandi Yogam according to Sivadasan Ravi."""
    def _sign(chart: MarriageChartContext, planet_name: str) -> int:
        p = chart.grahas.get(planet_name)
        if p:
            return p.sign_index
        return 1

    g_guru_sign = _sign(groom_chart, "Jupiter")
    g_shukra_sign = _sign(groom_chart, "Venus")
    b_shukra_sign = _sign(bride_chart, "Venus")
    b_sevvai_sign = _sign(bride_chart, "Mars")

    shukra_distance = ((b_shukra_sign - g_shukra_sign) % 12) + 1
    soul_distance = ((b_sevvai_sign - g_guru_sign) % 12) + 1

    is_shukra_harmonic = shukra_distance in {1, 5, 9, 3, 7, 11}
    is_soul_harmonic = soul_distance in {1, 5, 9, 3, 7, 11}

    b_saturn_sign = _sign(bride_chart, "Saturn")
    b_rahu_sign = _sign(bride_chart, "Rahu")
    b_moon_sign = _sign(bride_chart, "Moon")
    b_ketu_sign = _sign(bride_chart, "Ketu")

    def _is_between(p_sign: int, sign_a: int, sign_b: int) -> bool:
        if sign_a == sign_b:
            return False
        dist_ab = (sign_b - sign_a) % 12
        dist_ap = (p_sign - sign_a) % 12
        return 0 < dist_ap < dist_ab

    nandi_obstacles = []
    nandi_obstacles_ta = []

    if _is_between(b_saturn_sign, b_sevvai_sign, b_shukra_sign) or _is_between(b_saturn_sign, b_shukra_sign, b_sevvai_sign):
        nandi_obstacles.append("Saturn Nandi Yogam: Elderly family member creates subtle delays or hurdles.")
        nandi_obstacles_ta.append("சனி நந்தியோகம்: குடும்பத்தில் உள்ள மூத்த நபர் ஒருவரால் திருமணத்தில் தாமதம் அல்லது தடைகள் உண்டாகலாம்.")

    if _is_between(b_rahu_sign, b_sevvai_sign, b_shukra_sign) or _is_between(b_rahu_sign, b_shukra_sign, b_sevvai_sign):
        nandi_obstacles.append("Rahu Nandi Yogam: Outside influences or widowed/ailing relatives create friction.")
        nandi_obstacles_ta.append("ராகு நந்தியோகம்: வெளி நபர்கள் அல்லது மாற்று கருத்துடையவர்களால் திருமணத்தில் தடை வரலாம்.")

    if _is_between(b_moon_sign, b_sevvai_sign, b_shukra_sign) or _is_between(b_moon_sign, b_shukra_sign, b_sevvai_sign):
        nandi_obstacles.append("Moon Nandi Yogam: Mother or mother-in-law interference requires sensitive handling.")
        nandi_obstacles_ta.append("சந்திர நந்தியோகம்: தாய் அல்லது மாமியார் வழியில் சிறு மனக்கசப்புகள் ஏற்படலாம்.")

    if _is_between(b_ketu_sign, b_sevvai_sign, b_shukra_sign) or _is_between(b_ketu_sign, b_shukra_sign, b_sevvai_sign):
        nandi_obstacles.append("Ketu Nandi Yogam: Philosophical differences or religious traditions need alignment.")
        nandi_obstacles_ta.append("கேது நந்தியோகம்: ஆச்சார அல்லது மத வழக்க வேறுபாடுகள் வரலாம்.")

    has_nandi_yogam = len(nandi_obstacles) > 0

    base_score = 0.5
    if is_shukra_harmonic:
        base_score += 0.25
    if is_soul_harmonic:
        base_score += 0.25
    if has_nandi_yogam:
        base_score -= 0.15
    base_score = max(0.2, min(1.0, base_score))

    if base_score >= 0.8:
        verdict = "EXCELLENT"
        verdict_ta = "உத்தம நாடிப் பொருத்தம்"
        summary_en = "High Nadi resonance: Groom's Venus and Bride's Venus/Mars are harmoniously connected across trines and sextiles. Strong natural affection and longevity of conjugal bond."
        summary_ta = "மிகச் சிறந்த நாடிப் பொருத்தம்: ஆண் ஜாதக குரு-சுக்கிரனும், பெண் ஜாதக சுக்கிரன்-செவ்வாயும் திரிகோண/லாப நிலைகளில் அமைந்து அன்யோன்ய தாம்பத்தியத்தை உறுதி செய்கின்றன."
    elif base_score >= 0.5:
        verdict = "MODERATE"
        verdict_ta = "மத்திம நாடிப் பொருத்தம்"
        summary_en = "Moderate Nadi resonance: Baseline harmony is present with secondary adjustments recommended."
        summary_ta = "நடுத்தர நாடிப் பொருத்தம்: அடிப்படை இணக்கம் உண்டு; விட்டுக் கொடுத்து வாழும் பண்பு தேவைப்படும்."
    else:
        verdict = "CHALLENGING"
        verdict_ta = "கவனத்திற்குரிய நாடிப் பொருத்தம்"
        summary_en = "Challenging Nadi alignment: Disconnect between primary significators or strong Nandi Yogam obstruction. Requires remedial alignment."
        summary_ta = "நாடி அமைப்பில் முரண்பாடு அல்லது நந்தியோகத் தடை காணப்படுகிறது. முறையான பரிகாரங்கள் மற்றும் புரிந்துணர்வு அவசியம்."

    return {
        "verdict": verdict,
        "verdict_ta": verdict_ta,
        "score": round(base_score, 2),
        "groom_guru_sign": SIGN_NAMES_EN[g_guru_sign],
        "groom_shukra_sign": SIGN_NAMES_EN[g_shukra_sign],
        "bride_shukra_sign": SIGN_NAMES_EN[b_shukra_sign],
        "bride_sevvai_sign": SIGN_NAMES_EN[b_sevvai_sign],
        "is_shukra_harmonic": is_shukra_harmonic,
        "is_soul_harmonic": is_soul_harmonic,
        "has_nandi_yogam": has_nandi_yogam,
        "nandi_obstacles_en": nandi_obstacles,
        "nandi_obstacles_ta": nandi_obstacles_ta,
        "summary_en": summary_en,
        "summary_ta": summary_ta,
    }


# ---------------------------------------------------------------------------
# 4. SPECIAL IN-LAWS NAKSHATRA DOSHAS & EXEMPTION VERIFIER
# ---------------------------------------------------------------------------

def evaluate_in_laws_nakshatra_exemptions(
    groom_chart: MarriageChartContext,
    bride_chart: MarriageChartContext,
) -> Dict[str, Any]:
    """Evaluates Moolam, Aslesha, Jyeshtha, and Visakha in-laws afflictions and exemptions."""
    bride_star_idx = bride_chart.moon_nakshatra_idx
    bride_lagna_idx = bride_chart.ascendant_sign_idx
    groom_lagna_idx = groom_chart.ascendant_sign_idx

    star_findings: List[Dict[str, Any]] = []

    # 1. Moola (18: Mula)
    if bride_star_idx == 18:
        afflicted_bride_lagna = bride_lagna_idx in {1, 2, 5, 6, 8, 9, 12}
        afflicted_groom_lagna = groom_lagna_idx in {2, 3, 6, 7, 8, 11, 12}
        is_exempt = not (afflicted_bride_lagna and afflicted_groom_lagna)
        star_findings.append({
            "nakshatra_en": "Moola (Moolam)",
            "nakshatra_ta": "மூலம்",
            "relative_en": "Father-in-law (Māmanār)",
            "relative_ta": "மாமனார்",
            "is_exempt": is_exempt,
            "status": "EXEMPT_NO_DOSHA" if is_exempt else "CAUTION_DOSHA_PRESENT",
            "explanation_en": (
                f"Bride was born in Moola nakshatra. Siddhayogi Sivadasan Ravi confirms the popular myth "
                f"that 'all Moola brides harm father-in-law' is FALSE. Under canonical rules: "
                f"{'Exemption applies: Bride Lagna (' + SIGN_NAMES_EN[bride_lagna_idx] + ') or Groom Lagna (' + SIGN_NAMES_EN[groom_lagna_idx] + ') nullifies the dosha completely!' if is_exempt else 'Affliction indicator present; special Shanti / Shiva Aradhana recommended.'}"
            ),
            "explanation_ta": (
                f"மணமகள் மூலம் நட்சத்திரத்தில் பிறந்துள்ளார். 'மூலத்துப் பெண் மாமனாருக்கு ஆகாது' என்பது "
                f"பொதுவான மூடநம்பிக்கை என சித்தயோகி சிவதாசன் ரவி விரிவாக விளக்குகிறார். "
                f"{'விதிவிலக்கு பொருந்துகிறது: மணமகள் லக்னம் (' + SIGN_NAMES_TA[bride_lagna_idx] + ') அல்லது மணமகன் லக்னம் (' + SIGN_NAMES_TA[groom_lagna_idx] + ') அமைப்பால் மாமனாருக்கு எந்த தோஷமும் இல்லை!' if is_exempt else 'தோஷ அமைப்பு காணப்படுவதால் சிவ வழிபாடு மற்றும் சாந்தி பரிகாரம் செய்வது நன்று.'}"
            )
        })

    # 2. Ashlesha (8: Ashlesha)
    if bride_star_idx == 8:
        afflicted_b_lagna = bride_lagna_idx in {1, 2, 3, 5, 6, 8, 9, 12}
        afflicted_g_lagna = groom_lagna_idx in {2, 3, 6, 7, 8, 11, 12}
        is_exempt = not (afflicted_b_lagna and afflicted_g_lagna)
        star_findings.append({
            "nakshatra_en": "Ashlesha (Ayilyam)",
            "nakshatra_ta": "ஆயில்யம்",
            "relative_en": "Mother-in-law (Māmiyār)",
            "relative_ta": "மாமியார்",
            "is_exempt": is_exempt,
            "status": "EXEMPT_NO_DOSHA" if is_exempt else "CAUTION_DOSHA_PRESENT",
            "explanation_en": (
                f"Bride was born in Ashlesha nakshatra. According to Sivadasan Ravi, Ashlesha mother-in-law dosha "
                f"operates strictly under specific Lagna conditions. "
                f"{'Exemption holds: Bride Lagna (' + SIGN_NAMES_EN[bride_lagna_idx] + ') or Groom Lagna (' + SIGN_NAMES_EN[groom_lagna_idx] + ') neutralizes the dosha completely!' if is_exempt else 'Affliction present; Nagadevata and Durga aradhana recommended.'}"
            ),
            "explanation_ta": (
                f"மணமகள் ஆயில்யம் நட்சத்திரத்தில் பிறந்துள்ளார். 'ஆயில்யம் மாமியாருக்கு ஆகாது' என்ற அச்சத்திற்கு "
                f"சாஸ்திர விதிவிலக்குகள் உண்டு. "
                f"{'விதிவிலக்கு பொருந்துகிறது: மணமகள் லக்னம் (' + SIGN_NAMES_TA[bride_lagna_idx] + ') அல்லது மணமகன் லக்னம் (' + SIGN_NAMES_TA[groom_lagna_idx] + ') அமைப்பால் மாமியாருக்கு தோஷம் இல்லை!' if is_exempt else 'தோஷ அமைப்பு உள்ளதால் நாகர் வழிபாடு மற்றும் சாந்தி சடங்குகள் செய்வது நல்லது.'}"
            )
        })

    # 3. Jyeshtha (17: Jyeshtha)
    if bride_star_idx == 17:
        afflicted_b_lagna = bride_lagna_idx in {1, 2, 3, 5, 6, 9, 10}
        afflicted_g_lagna = groom_lagna_idx in {1, 2, 5, 6, 9, 10, 11}
        is_exempt = not (afflicted_b_lagna and afflicted_g_lagna)
        star_findings.append({
            "nakshatra_en": "Jyeshtha (Kettai)",
            "nakshatra_ta": "கேட்டை",
            "relative_en": "Elder Brother-in-law (Mūtha Maithunar)",
            "relative_ta": "மூத்த சகோதரன் (மைத்துனர்)",
            "is_exempt": is_exempt,
            "status": "EXEMPT_NO_DOSHA" if is_exempt else "CAUTION_DOSHA_PRESENT",
            "explanation_en": (
                f"Bride was born in Jyeshtha nakshatra. "
                f"{'Exemption verified: Lagna alignments protect the groom’s elder brother from affliction.' if is_exempt else 'Classical Kettai dosha present for elder brother-in-law; Varaha/Indra worship prescribed.'}"
            ),
            "explanation_ta": (
                f"மணமகள் கேட்டை நட்சத்திரத்தில் பிறந்துள்ளார். "
                f"{'விதிவிலக்கு பொருந்துகிறது: லக்ன பொருத்த அமைப்பால் மணமகனின் மூத்த சகோதரனுக்கு எந்த தோஷமும் இல்லை.' if is_exempt else 'தோஷ அமைப்பு உள்ளதால் இந்திரன் மற்றும் வராகர் வழிபாடு செய்வது நன்று.'}"
            )
        })

    # 4. Vishakha (15: Vishakha)
    if bride_star_idx == 15:
        afflicted_b_lagna = bride_lagna_idx in {1, 2, 4, 5, 6, 9, 10, 11}
        afflicted_g_lagna = groom_lagna_idx in {3, 4, 5, 7, 8, 11, 12}
        is_exempt = not (afflicted_b_lagna and afflicted_g_lagna)
        star_findings.append({
            "nakshatra_en": "Vishakha (Visakam)",
            "nakshatra_ta": "விசாகம்",
            "relative_en": "Younger Brother-in-law (Iḷaiya Maithunar)",
            "relative_ta": "இளைய சகோதரன் (மைத்துனர்)",
            "is_exempt": is_exempt,
            "status": "EXEMPT_NO_DOSHA" if is_exempt else "CAUTION_DOSHA_PRESENT",
            "explanation_en": (
                f"Bride was born in Vishakha nakshatra. "
                f"{'Exemption verified: Lagna configuration clears the younger brother-in-law dosha completely.' if is_exempt else 'Visakha affliction present for younger brother; Murugan/Kartikeya worship advised.'}"
            ),
            "explanation_ta": (
                f"மணமகள் விசாகம் நட்சத்திரத்தில் பிறந்துள்ளார். "
                f"{'விதிவிலக்கு பொருந்துகிறது: மணமகள் மற்றும் மணமகன் லக்ன அமைப்பால் இளைய சகோதரனுக்கு தோஷம் இல்லை.' if is_exempt else 'தோஷ அமைப்பு உள்ளதால் முருகப்பெருமான் வழிபாடு செய்வது நன்று.'}"
            )
        })

    return {
        "has_special_nakshatra": len(star_findings) > 0,
        "findings": star_findings,
    }


# ---------------------------------------------------------------------------
# 5. SACRED THIRUMURAI & CLASSICAL WEDDING REMEDIES
# ---------------------------------------------------------------------------

def get_thirumurai_and_wedding_remedies() -> Dict[str, Any]:
    """Returns canonical remedies from Thirumana Yoga Porutha Thiravukol."""
    return {
        "parikara_sthalam": {
            "name_en": "Sri Nellaiyappar & Gandhimathi Amman Temple, Tirunelveli (Then-Kanchi)",
            "name_ta": "ஸ்ரீ நெல்லையப்பர் - காந்திமதியம்மன் திருக்கோவில், திருநெல்வேலி (தென்காஞ்சி)",
            "significance_en": (
                "Unique kshetra where Lord Shiva and Divine Mother face the same direction, recreating "
                "the divine wedding darshan granted to Sage Agastya. Ideal parikara sthalam for early and blissful marriage."
            ),
            "significance_ta": (
                "அகத்திய மாமுனிவருக்கு தம்பதி சமேதராக இறைவன்-இறைவி திருமணக் கோலத்தில் காட்சி தந்த புண்ணிய தலம். "
                "இருவரும் ஒரே திசையை நோக்கி அருள்பாலிக்கும் அதிசய தலம். நல்ல மணவாழ்க்கை அமைய சிறந்த பரிகார தலம்."
            ),
        },
        "sacred_hymns": [
            {
                "title_en": "Andal Kalyanam (Vaaranam Aayiram)",
                "title_ta": "ஆண்டாள் கல்யாணம் - வாரணம் ஆயிரம் (நாச்சியார் திருமொழி)",
                "hymn_ta": (
                    "வாரணம் ஆயிரம் சூழ வலஞ்செய்து\n"
                    "நாரணன் நம்பி நடக்கின்றான் என்றெதிர்\n"
                    "பூரண பொற்குடம் வைத்துப் புறமெங்கும்\n"
                    "தோரணம் நாட்டக் கனாக்கண்டேன் தோழீநான்!"
                ),
                "purpose_en": "Recited daily to remove delays, overcome doshas, and ensure auspicious, early marriage.",
                "purpose_ta": "திருமணத் தடை நீங்கி, விரைந்து நல்ல வரன் அமைய தினமும் பாராயணம் செய்ய வேண்டிய பதிகம்.",
            },
            {
                "title_en": "Divya Prabandham for Family Harmony",
                "title_ta": "குடும்பத்தில் ஒற்றுமை நிலவ - நாலாயிர திவ்ய பிரபந்தம்",
                "hymn_ta": (
                    "நெடுமாற்கடிமை செய்வேன்போல் அவனைக்கருத வஞ்சித்துத்\n"
                    "தடுமாற்றத்தீக்கதிகள் முற்றும் தவிர்ந்த சதிர்நினைந்தால்\n"
                    "கொடுமாவினையேனவனடியாரடியே கூடுமிதுவல்லால்\n"
                    "விடுமாறென்பதென்னந்தோ வியன் மூவுலகுபெறினுமே."
                ),
                "purpose_en": "Preserves lifelong domestic peace, removes misunderstandings, and fosters mutual devotion.",
                "purpose_ta": "தம்பதியரிடையே கருத்து வேறுபாடுகள் நீங்கி, குடும்பத்தில் அன்யோன்ய ஒற்றுமை நிலவ ஓத வேண்டிய பாடல்.",
            },
            {
                "title_en": "Saiva Thirumurai Thevaram for Marriage Blessings",
                "title_ta": "திருமுறைத் திருமணம் - திருஞானசம்பந்தர் தேவாரம்",
                "hymn_ta": (
                    "மண்ணில் நல்லவண்ணம் வாழலாம் வைகலும்\n"
                    "எண்ணில் நல்லகதிக்கு யாதுமோர் குறைவிலை\n"
                    "கண்ணின் நல்லுறுறும் கழுமல வளநகர்ப்\n"
                    "பெண்ணின் நல்லாளொடும் பெருந்தகை இருந்ததே!"
                ),
                "purpose_en": "Blesses the couple with all earthly prosperity, virtue, health, and spiritual realization.",
                "purpose_ta": "இல்லற தர்மம் இனிதே சிறக்க, சகல சம்பத்துகளும் பெற்று தம்பதியர் நீடூழி வாழ அருளும் திருமுறை பாடல்.",
            },
        ],
    }


# ---------------------------------------------------------------------------
# MASTER COMPOSITE FUNCTION
# ---------------------------------------------------------------------------

def run_sivadasan_ravi_marriage_insights(
    groom_chart: MarriageChartContext,
    bride_chart: MarriageChartContext,
) -> Dict[str, Any]:
    """Runs all evaluations from Thirumana Yoga Porutha Thiravukol."""
    dasa_res = evaluate_dasa_porutham(groom_chart, bride_chart)
    guru_res = evaluate_gochara_guru_balam(groom_chart, bride_chart)
    nadi_res = evaluate_nadi_porutham_and_nandi_yogam(groom_chart, bride_chart)
    in_laws_res = evaluate_in_laws_nakshatra_exemptions(groom_chart, bride_chart)
    remedies_res = get_thirumurai_and_wedding_remedies()

    return {
        "treatise_title_ta": "திருமண யோக திருமணப் பொருத்த திறவுகோல்",
        "treatise_title_en": "Thirumana Yoga Porutha Thiravukol",
        "author": "Siddhayogi Sivadasan Ravi (சித்தயோகி சிவதாசன் ரவி)",
        "publisher": "Sri Aromira Prasuram, Thammampatti",
        "dasa_porutham": dasa_res,
        "guru_balam": guru_res,
        "nadi_porutham": nadi_res,
        "in_laws_nakshatras": in_laws_res,
        "classical_remedies": remedies_res,
    }
