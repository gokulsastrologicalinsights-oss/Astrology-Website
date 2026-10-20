"""Composite Marriage Compatibility Assessment Module.

Synthesizes results from all completed marriage engine layers (Phases 1–7):
1. Traditional Tamil 10 Poruthams (original score and status)
2. North Indian 36-Point Ashtakoota (original points out of 36)
3. Groom & Bride individual Vedic marriage analysis (7th house, Karakas, D9)
4. Mutual Kuja Dosha & South Indian Papasamya analysis
5. Bidirectional Vedic Synastry (Moon, Lagna, 7th Lords, Karakas)
6. Read-Only KP 7th CSL promise, 4-tier significators, and Vimshottari timing

Strict Governance & Integrity Principles:
- Preserves independent scores and inspectable findings without alteration.
- Never commingles or sums Tamil Porutham (out of 10) and Ashtakoota (out of 36) into a synthetic metric.
- Preserves individual Kuja Dosha findings even when partner's chart provides mutual Samadosham.
- Explicitly flags, explains, and resolves divergences between traditions.
- Uses documented deterministic thresholds from RULE_SOURCE_REGISTER.md Section 8.
- Never derives arbitrary numerical weights from indicator counts.
- Formulates non-deterministic, non-frightening bilingual explanations (EN/TA) emphasizing
  human agency, emotional maturity, and personal choice.
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from app.schemas.marriage import (
    TamilPoruthamSummary,
    AshtakootaSummary,
    PersonProfileSummary,
    MarriageCompatibilityResponse,
    FinalAssessmentSummary,
)
from app.services.marriage_engine.models import (
    Gender,
    CompatibilityOutcome,
    MarriageChartContext,
    IndividualVedicAnalysis,
    DualVedicAnalysis,
    MutualDoshaAnalysisResult,
    BidirectionalSynastryResult,
    KpMarriageAnalysisResult,
    SamadoshamOutcome,
    PapasamyaVerdict,
    KpPromiseVerdict,
    ConflictType,
    ConflictFinding,
    CategoryVerdict,
    CompositeMarriageAssessment,
)
from app.services.marriage_engine.porutham_engine import evaluate_tamil_10_poruthams
from app.services.marriage_engine.ashtakoota_engine import evaluate_ashtakoota_matching
from app.services.marriage_engine.vedic_analysis import evaluate_dual_vedic_marriage_analysis
from app.services.marriage_engine.mutual_doshas import evaluate_mutual_dosha_analysis
from app.services.marriage_engine.synastry import evaluate_bidirectional_synastry
from app.services.marriage_engine.kp_adapter import evaluate_kp_marriage_analysis


# Standard Non-Guarantee Disclaimers
COMPOSITE_DISCLAIMER_EN: str = (
    "This compatibility assessment provides traditional astrological analysis based on classical "
    "texts and Krishnamurti Paddhati (KP) principles. It represents astronomical propensities and "
    "karmic tendencies rather than an absolute guarantee or denial of marital success. Human agency, "
    "mutual understanding, emotional maturity, socio-cultural context, and personal life choices "
    "remain paramount."
)

COMPOSITE_DISCLAIMER_TA: str = (
    "இந்த திருமணப் பொருத்த மதிப்பீடு பாரம்பரிய செவ்வியல் நூல்கள் மற்றும் கே.பி விதிகளின் "
    "அடிப்படையிலான ஜோதிட பகுப்பாய்வை வழங்குகிறது. இது சாத்தியமான கிரக நிலைகளையும் கர்ம போக்குகளையும் "
    "மட்டுமே குறிக்கிறது; மாறாக திருமண வெற்றியின் உறுதியான உத்திரவாதம் அல்லது மறுப்பு அல்ல. மனித "
    "முயற்சி, பரஸ்பர புரிதல், மன முதிர்ச்சி மற்றும் தனிநபர் தேர்வுகளே முதன்மையானவை."
)


# ---------------------------------------------------------------------------
# Category Evaluators
# ---------------------------------------------------------------------------

def _evaluate_porutham_category(
    porutham: Optional[TamilPoruthamSummary],
) -> Tuple[CategoryVerdict, List[str], List[str]]:
    """Evaluate Tamil 10 Porutham category per Kalaprakasika Ch. 12."""
    if porutham is None:
        return (
            CategoryVerdict(
                category_id="tamil_porutham",
                category_name_en="Tamil 10 Poruthams",
                category_name_ta="தமிழ் 10 பொருத்தங்கள்",
                status="INDETERMINATE",
                tradition="Tamil Traditional (South Indian)",
                score_summary="Data Unavailable",
                key_factors=["Porutham calculations not provided or incomplete."],
            ),
            [],
            [],
        )

    score = porutham.total_score
    rajju = str(porutham.rajju_status).upper()
    vedha = str(porutham.vedha_status).upper()
    vetoes: List[str] = []
    supportive: List[str] = []
    challenging: List[str] = []

    if rajju == "FAIL":
        vetoes.append("Rajju Thatu (Same Rajju affliction; South Indian tradition critical veto per Kalaprakasika Ch. 12)")
        challenging.append("Rajju Porutham failed (Same Rajju - Rajju Thatu).")
    else:
        supportive.append("Rajju Porutham satisfied (Different Rajju - Mangalya protection preserved).")

    if vedha == "FAIL":
        vetoes.append("Mutual Vedha affliction detected (Repulsive Nakshatra axis per Kalaprakasika Ch. 12)")
        challenging.append("Vedha Porutham failed (Repulsive star axis detected).")
    else:
        supportive.append("Vedha Porutham satisfied (No mutual repulsion detected).")

    if vetoes:
        status = "UNFAVORABLE"
        challenging.append(f"Critical Porutham veto detected ({'; '.join(vetoes)}).")
    elif score >= 6.0:
        status = "FAVORABLE"
        supportive.append(f"High Porutham match score: {score:.1f}/10.0.")
    elif score >= 5.0:
        status = "MIXED"
        supportive.append(f"Acceptable Porutham match score: {score:.1f}/10.0.")
    else:
        status = "UNFAVORABLE"
        challenging.append(f"Low or afflicted Porutham match score: {score:.1f}/10.0.")

    summary_str = f"{score:.1f}/10.0 matches (Rajju: {rajju}, Vedha: {vedha})"

    return (
        CategoryVerdict(
            category_id="tamil_porutham",
            category_name_en="Tamil 10 Poruthams",
            category_name_ta="தமிழ் 10 பொருத்தங்கள்",
            status=status,
            tradition="Tamil Traditional (South Indian)",
            score_summary=summary_str,
            key_factors=porutham.summary_notes or [f"Score: {score:.1f}/10.0"],
            vetoes_applied=vetoes,
        ),
        supportive,
        challenging,
    )


def _evaluate_ashtakoota_category(
    ashtakoota: Optional[AshtakootaSummary],
) -> Tuple[CategoryVerdict, List[str], List[str]]:
    """Evaluate North Indian 36-Point Ashtakoota category per Muhurta Chintamani Ch. 6."""
    if ashtakoota is None:
        return (
            CategoryVerdict(
                category_id="ashtakoota",
                category_name_en="North Indian Ashtakoota",
                category_name_ta="வட இந்திய அஷ்டகூட பொருத்தம்",
                status="INDETERMINATE",
                tradition="North Indian Vedic (Muhurta Chintamani)",
                score_summary="Data Unavailable",
                key_factors=["Ashtakoota calculations not provided or incomplete."],
            ),
            [],
            [],
        )

    pts = ashtakoota.total_points
    nadi_present = bool(ashtakoota.nadi_dosha_present)
    nadi_cancelled = bool(ashtakoota.nadi_dosha_cancelled)
    bhakoot_present = bool(ashtakoota.bhakoot_dosha_present)
    bhakoot_cancelled = bool(ashtakoota.bhakoot_dosha_cancelled)

    vetoes: List[str] = []
    supportive: List[str] = []
    challenging: List[str] = []

    if nadi_present and not nadi_cancelled:
        vetoes.append("Active uncancelled Nadi Dosha (North Indian tradition critical veto per Muhurta Chintamani Ch. 6)")
        challenging.append("Active Nadi Dosha present without classical cancellation (0/8 points).")
    elif nadi_present and nadi_cancelled:
        supportive.append("Nadi Dosha present but neutralized by classical cancellation rules.")
    else:
        supportive.append("Nadi Koota clear (Full 8/8 points awarded).")

    if bhakoot_present and not bhakoot_cancelled:
        challenging.append("Bhakoot Dosha present without classical cancellation (0/7 points).")
    elif bhakoot_present and bhakoot_cancelled:
        supportive.append("Bhakoot Dosha present but mitigated by common sign lord or mutual planetary friendship.")
    else:
        supportive.append("Bhakoot Koota clear (Full 7/7 points awarded).")

    if pts >= 21.0 and not vetoes and not (bhakoot_present and not bhakoot_cancelled):
        status = "FAVORABLE"
        supportive.append(f"Auspicious Ashtakoota score: {pts:.1f}/36.0 points (exceeds 21.0 threshold).")
    elif pts >= 18.0 and not vetoes:
        status = "MIXED"
        supportive.append(f"Acceptable Ashtakoota score: {pts:.1f}/36.0 points (satisfies 18.0 minimum threshold).")
    else:
        status = "UNFAVORABLE"
        challenging.append(f"Ashtakoota score below standard threshold or afflicted: {pts:.1f}/36.0 points.")

    summary_str = f"{pts:.1f}/36.0 points (Nadi: {'Dosha' if (nadi_present and not nadi_cancelled) else 'Clear'}, Bhakoot: {'Dosha' if (bhakoot_present and not bhakoot_cancelled) else 'Clear'})"

    return (
        CategoryVerdict(
            category_id="ashtakoota",
            category_name_en="North Indian Ashtakoota",
            category_name_ta="வட இந்திய அஷ்டகூட பொருத்தம்",
            status=status,
            tradition="North Indian Vedic (Muhurta Chintamani)",
            score_summary=summary_str,
            key_factors=ashtakoota.summary_notes or [f"Points: {pts:.1f}/36.0"],
            vetoes_applied=vetoes,
        ),
        supportive,
        challenging,
    )


def _evaluate_mutual_dosha_category(
    mutual_doshas: Optional[Any],
) -> Tuple[CategoryVerdict, CategoryVerdict, List[str], List[str]]:
    """Evaluate Mutual Kuja Samadosham and South Indian Papasamya balance."""
    supportive: List[str] = []
    challenging: List[str] = []

    # 1. Kuja Samadosham
    mk = getattr(mutual_doshas, "samadosham", None) or getattr(mutual_doshas, "mutual_kuja", None)
    if mk is None:
        kuja_cv = CategoryVerdict(
            category_id="kuja_samadosham",
            category_name_en="Kuja Dosha & Samadosham",
            category_name_ta="செவ்வாய் தோஷ சமதோஷம்",
            status="INDETERMINATE",
            tradition="Muhurta Chintamani & Kalaprakasika",
            score_summary="Data Unavailable",
        )
    else:
        outcome = getattr(mk, "mutual_balance", None) or getattr(mk, "samadosham_outcome", None)
        vetoes = []

        if outcome in (SamadoshamOutcome.MUTUALLY_MATCHED, SamadoshamOutcome.CANCELLED_BY_RULE):
            status = "FAVORABLE"
            if outcome == SamadoshamOutcome.MUTUALLY_MATCHED:
                supportive.append("Both charts carry comparable Kuja Dosha, resulting in classical Samadosham (mutual neutralization).")
            else:
                supportive.append("Kuja Dosha neutralized by canonical dignity/aspect cancellation rules in both charts.")
        elif outcome == SamadoshamOutcome.MITIGATED:
            status = "MIXED"
            supportive.append("Kuja Dosha is partially balanced or mitigated by counterpoising planetary placements.")
        elif outcome == SamadoshamOutcome.NOT_MUTUALLY_MATCHED:
            status = "UNFAVORABLE"
            vetoes.append("Severe active Kuja Dosha present in one chart without reciprocal placement in partner's chart.")
            challenging.append("Kuja Dosha mismatch: one partner carries active Kuja Dosha without counterpoise.")
        else:
            status = "INDETERMINATE"

        mitigations = getattr(mk, "cancellations_or_mitigations_applied", None) or getattr(mk, "mitigating_factors", [])
        kuja_cv = CategoryVerdict(
            category_id="kuja_samadosham",
            category_name_en="Kuja Dosha & Samadosham",
            category_name_ta="செவ்வாய் தோஷ சமதோஷம்",
            status=status,
            tradition="Muhurta Chintamani & Kalaprakasika",
            score_summary=str(outcome.value) if hasattr(outcome, "value") else str(outcome),
            key_factors=mitigations or [f"Outcome: {getattr(outcome, 'value', outcome)}"],
            vetoes_applied=vetoes,
        )

    # 2. Papasamya Balance
    g_papa = getattr(mutual_doshas, "groom_papasamya", None)
    b_papa = getattr(mutual_doshas, "bride_papasamya", None)
    p_verdict = getattr(mutual_doshas, "papasamya_verdict", None)

    if g_papa is None or b_papa is None or p_verdict is None:
        papa_cv = CategoryVerdict(
            category_id="papasamya",
            category_name_en="South Indian Papasamya",
            category_name_ta="பாபசாம்யம் (பாவ சமநிலை)",
            status="INDETERMINATE",
            tradition="Kalaprakasika & Jathaka Alankaram",
            score_summary="Data Unavailable",
        )
    else:
        g_pts = getattr(g_papa, "total_papam", None)
        if g_pts is None:
            g_pts = getattr(g_papa, "total_points", 0.0)
        b_pts = getattr(b_papa, "total_papam", None)
        if b_pts is None:
            b_pts = getattr(b_papa, "total_points", 0.0)
        diff_pct = getattr(mutual_doshas, "papasamya_diff_percent", 0.0)

        if p_verdict == PapasamyaVerdict.FAVORABLE:
            p_status = "FAVORABLE"
            supportive.append(f"Optimum Papasamya malefic balance (Groom: {g_pts:.1f}, Bride: {b_pts:.1f}, diff: {diff_pct:.1f}%).")
        elif p_verdict == PapasamyaVerdict.TOLERABLE:
            p_status = "MIXED"
            supportive.append(f"Tolerable Papasamya malefic balance (Groom: {g_pts:.1f}, Bride: {b_pts:.1f}, diff: {diff_pct:.1f}%).")
        elif p_verdict == PapasamyaVerdict.UNFAVORABLE:
            p_status = "UNFAVORABLE"
            challenging.append(f"Papasamya malefic imbalance: Bride carrying significantly higher malefic load ({b_pts:.1f} vs {g_pts:.1f}, diff: {diff_pct:.1f}%).")
        else:
            p_status = "INDETERMINATE"

        v_val = getattr(p_verdict, "value", str(p_verdict))
        papa_cv = CategoryVerdict(
            category_id="papasamya",
            category_name_en="South Indian Papasamya",
            category_name_ta="பாபசாம்யம் (பாவ சமநிலை)",
            status=p_status,
            tradition="Kalaprakasika & Jathaka Alankaram",
            score_summary=f"Groom: {g_pts:.1f} pts, Bride: {b_pts:.1f} pts ({v_val})",
            key_factors=[f"Verdict: {v_val}", f"Difference: {diff_pct:.1f}%"],
            vetoes_applied=["Bride Papam exceeds Groom Papam by > 25%"] if p_verdict == PapasamyaVerdict.UNFAVORABLE else [],
        )

    return kuja_cv, papa_cv, supportive, challenging


def _evaluate_vedic_individual_category(
    groom_vedic: Optional[IndividualVedicAnalysis],
    bride_vedic: Optional[IndividualVedicAnalysis],
) -> Tuple[CategoryVerdict, List[str], List[str]]:
    """Evaluate individual Vedic marriage indicators (7th house, Karakas, D9) for both partners."""
    supportive: List[str] = []
    challenging: List[str] = []

    if groom_vedic is None or bride_vedic is None:
        return (
            CategoryVerdict(
                category_id="vedic_individual",
                category_name_en="Individual Vedic Marriage Houses (D1 & D9)",
                category_name_ta="தனிநபர் களத்திர பாவ ஆய்வு (D1 & D9)",
                status="INDETERMINATE",
                tradition="Brihat Parashara Hora Shastra",
                score_summary="Data Unavailable",
            ),
            [],
            [],
        )

    g_7th = groom_vedic.houses_analysis.get(7)
    b_7th = bride_vedic.houses_analysis.get(7)

    g_afflicted = bool(g_7th and g_7th.is_afflicted)
    b_afflicted = bool(b_7th and b_7th.is_afflicted)

    if not g_afflicted and not b_afflicted:
        status = "FAVORABLE"
        supportive.append("Both charts exhibit unblemished 7th houses (Kalatra Bhava) supported by natural benefics.")
    elif g_afflicted and b_afflicted:
        status = "MIXED"
        challenging.append("Both prospective partners exhibit minor malefic influences on the 7th house.")
    elif g_afflicted or b_afflicted:
        status = "MIXED"
        afflicted_person = groom_vedic.person_name if g_afflicted else bride_vedic.person_name
        challenging.append(f"Minor affliction detected in 7th house for {afflicted_person}.")
    else:
        status = "FAVORABLE"

    # Preserved individual Kuja notes
    if groom_vedic.kuja_dosha and groom_vedic.kuja_dosha.is_present:
        challenging.append(f"Groom natal chart carries Kuja Dosha ({groom_vedic.kuja_dosha.severity}).")
    if bride_vedic.kuja_dosha and bride_vedic.kuja_dosha.is_present:
        challenging.append(f"Bride natal chart carries Kuja Dosha ({bride_vedic.kuja_dosha.severity}).")

    return (
        CategoryVerdict(
            category_id="vedic_individual",
            category_name_en="Individual Vedic Marriage Houses (D1 & D9)",
            category_name_ta="தனிநபர் களத்திர பாவ ஆய்வு (D1 & D9)",
            status=status,
            tradition="Brihat Parashara Hora Shastra",
            score_summary=f"Groom 7th: {'Afflicted' if g_afflicted else 'Clear'}, Bride 7th: {'Afflicted' if b_afflicted else 'Clear'}",
            key_factors=groom_vedic.supporting_indicators[:2] + bride_vedic.supporting_indicators[:2],
        ),
        supportive,
        challenging,
    )


def _evaluate_synastry_category(
    synastry: Optional[BidirectionalSynastryResult],
) -> Tuple[CategoryVerdict, List[str], List[str]]:
    """Evaluate Bidirectional Vedic Synastry overlays (Moon, Lagna, 7th Lords, Venus/Jupiter)."""
    supportive: List[str] = []
    challenging: List[str] = []

    if synastry is None:
        return (
            CategoryVerdict(
                category_id="synastry",
                category_name_en="Bidirectional Vedic Synastry",
                category_name_ta="இருவழி ஜாதக இணைவு ஆய்வு",
                status="INDETERMINATE",
                tradition="Parashari Cross-Chart Overlays",
                score_summary="Data Unavailable",
            ),
            [],
            [],
        )

    moon_axis = getattr(synastry.moon_to_moon, "sign_relationship", "") or getattr(synastry.moon_to_moon, "axis_type", "")
    lagna_axis = getattr(synastry.lagna_to_lagna, "lagna_relationship", "") or getattr(synastry.lagna_to_lagna, "axis_type", "")

    if "SAMASAPTAKA" in moon_axis or "TRIKONA" in moon_axis:
        supportive.append(f"Harmonious Moon-to-Moon axis: {moon_axis} (emotional resonance and mutual empathy).")
    elif "SHADASHTAKA" in moon_axis:
        challenging.append(f"Tense Moon-to-Moon axis: {moon_axis} (temperamental differences requiring active communication).")

    if "SAMASAPTAKA" in lagna_axis or "TRIKONA" in lagna_axis:
        supportive.append(f"Harmonious Lagna-to-Lagna axis: {lagna_axis} (complementary personalities and shared outlook).")
    elif "SHADASHTAKA" in lagna_axis:
        challenging.append(f"Tense Lagna-to-Lagna axis: {lagna_axis} (differing approaches to life goals).")

    strong_cnt = len(synastry.strong_indicators)
    weak_cnt = len(synastry.weak_indicators)

    if strong_cnt > weak_cnt and "SHADASHTAKA" not in moon_axis:
        status = "FAVORABLE"
    elif weak_cnt > strong_cnt:
        status = "UNFAVORABLE"
    else:
        status = "MIXED"

    return (
        CategoryVerdict(
            category_id="synastry",
            category_name_en="Bidirectional Vedic Synastry",
            category_name_ta="இருவழி ஜாதக இணைவு ஆய்வு",
            status=status,
            tradition="Parashari Cross-Chart Overlays",
            score_summary=f"Moon Axis: {moon_axis}, Lagna Axis: {lagna_axis}",
            key_factors=synastry.strong_indicators[:2] + synastry.weak_indicators[:2],
        ),
        supportive,
        challenging,
    )


def _evaluate_kp_category(
    kp_marriage: Optional[KpMarriageAnalysisResult],
) -> Tuple[CategoryVerdict, CategoryVerdict, List[str], List[str]]:
    """Evaluate KP 7th Cuspal Sub-Lord promise, RPs, and Vimshottari timing."""
    supportive: List[str] = []
    challenging: List[str] = []

    if kp_marriage is None:
        kp_promise_cv = CategoryVerdict(
            category_id="kp_promise",
            category_name_en="KP 7th Cuspal Sub-Lord Promise",
            category_name_ta="கே.பி 7-ம் பாவ உப அதிபதி வாக்குறுதி",
            status="INDETERMINATE",
            tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
            score_summary="Data Unavailable",
        )
        kp_timing_cv = CategoryVerdict(
            category_id="kp_timing",
            category_name_en="KP Vimshottari Timing Window",
            category_name_ta="கே.பி தசா-புக்தி கால அமைவு",
            status="INDETERMINATE",
            tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
            score_summary="Data Unavailable",
        )
        return kp_promise_cv, kp_timing_cv, supportive, challenging

    g_csl = kp_marriage.groom_analysis.csl_7th
    b_csl = kp_marriage.bride_analysis.csl_7th

    g_verd = g_csl.verdict
    b_verd = b_csl.verdict

    # 1. KP Cuspal Promise
    if g_verd == KpPromiseVerdict.FAVORABLE and b_verd == KpPromiseVerdict.FAVORABLE:
        p_status = "FAVORABLE"
        supportive.append("Both Groom and Bride 7th Cuspal Sub-Lords favorably signify marriage houses (2, 7, 11).")
    elif g_verd == KpPromiseVerdict.UNFAVORABLE or b_verd == KpPromiseVerdict.UNFAVORABLE:
        p_status = "UNFAVORABLE"
        challenging.append("7th Cuspal Sub-Lord signifies separating houses (1, 6, 10), indicating marital hurdles or delay.")
    elif g_verd == KpPromiseVerdict.MIXED or b_verd == KpPromiseVerdict.MIXED:
        p_status = "MIXED"
        supportive.append("7th Cuspal Sub-Lords signify supporting houses alongside secondary separating houses.")
    else:
        p_status = "INDETERMINATE"

    kp_promise_cv = CategoryVerdict(
        category_id="kp_promise",
        category_name_en="KP 7th Cuspal Sub-Lord Promise",
        category_name_ta="கே.பி 7-ம் பாவ உப அதிபதி வாக்குறுதி",
        status=p_status,
        tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
        score_summary=f"Groom 7th CSL: {g_verd.value}, Bride 7th CSL: {b_verd.value}",
        key_factors=[g_csl.explanation_en, b_csl.explanation_en],
    )

    # 2. KP Timing Window (Temporal Dimension - Non-veto)
    g_time = kp_marriage.groom_analysis.timing.overall_timing_verdict
    b_time = kp_marriage.bride_analysis.timing.overall_timing_verdict

    if g_time == KpPromiseVerdict.FAVORABLE and b_time == KpPromiseVerdict.FAVORABLE:
        t_status = "FAVORABLE"
        supportive.append("Both prospective partners are currently traversing astrologically auspicious Dasa-Bhukti periods for marriage.")
    elif g_time == KpPromiseVerdict.FAVORABLE or b_time == KpPromiseVerdict.FAVORABLE:
        t_status = "MIXED"
        supportive.append("One partner is in an active matrimonial Dasa-Bhukti period while the other is in a neutral period.")
    elif g_time == KpPromiseVerdict.UNFAVORABLE and b_time == KpPromiseVerdict.UNFAVORABLE:
        t_status = "UNFAVORABLE"
        challenging.append("Both partners are currently in Dasa-Bhukti periods signifying separating houses (1, 6, 10) suggesting delay.")
    else:
        t_status = "MIXED"

    kp_timing_cv = CategoryVerdict(
        category_id="kp_timing",
        category_name_en="KP Vimshottari Timing Window",
        category_name_ta="கே.பி தசா-புக்தி கால அமைவு",
        status=t_status,
        tradition="Krishnamurti Paddhati (Prof. K.S. Krishnamurti)",
        score_summary=f"Groom Timing: {g_time.value}, Bride Timing: {b_time.value}",
        key_factors=kp_marriage.timing_synchronicity_notes or ["Timing windows evaluated without deterministic guarantees."],
    )

    return kp_promise_cv, kp_timing_cv, supportive, challenging


# ---------------------------------------------------------------------------
# Conflict Detection Engine
# ---------------------------------------------------------------------------

def _detect_astrological_conflicts(
    category_verdicts: Dict[str, CategoryVerdict],
    porutham: Optional[TamilPoruthamSummary],
    ashtakoota: Optional[AshtakootaSummary],
    groom_vedic: Optional[IndividualVedicAnalysis],
    bride_vedic: Optional[IndividualVedicAnalysis],
    mutual_doshas: Optional[MutualDoshaAnalysisResult],
    synastry: Optional[BidirectionalSynastryResult],
    kp_marriage: Optional[KpMarriageAnalysisResult],
) -> List[ConflictFinding]:
    """Inspect all component findings and identify cross-tradition or cross-lens conflicts."""
    conflicts: List[ConflictFinding] = []

    # 1. Divergence between Tamil 10 Porutham and North Indian Ashtakoota
    p_cv = category_verdicts.get("tamil_porutham")
    a_cv = category_verdicts.get("ashtakoota")
    if p_cv and a_cv and p_cv.status != "INDETERMINATE" and a_cv.status != "INDETERMINATE":
        if (p_cv.status == "FAVORABLE" and a_cv.status == "UNFAVORABLE") or (p_cv.status == "UNFAVORABLE" and a_cv.status == "FAVORABLE"):
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.TRADITIONAL_SYSTEM_DIVERGENCE,
                    title_en="Divergence Between Tamil Porutham and North Indian Ashtakoota",
                    title_ta="தமிழ் பொருத்தம் மற்றும் வட இந்திய அஷ்டகூட முரண்பாடு",
                    finding_a=f"Tamil 10 Poruthams evaluated as {p_cv.status} ({p_cv.score_summary}).",
                    finding_b=f"North Indian Ashtakoota evaluated as {a_cv.status} ({a_cv.score_summary}).",
                    resolution_principle=(
                        "Preserve both traditional results independently without commingling or averaging scores. "
                        "Tamil tradition prioritizes Nakshatra Rajju/Dina longevity, whereas Ashtakoota heavily weights "
                        "Nadi (8 pts) and Bhakoot (7 pts). Couples should consult family elders or spiritual preceptors "
                        "regarding which ancestral tradition governs their lineage."
                    ),
                    explanation_en=(
                        f"Tamil 10 Porutham indicates {p_cv.status} while North Indian Ashtakoota indicates {a_cv.status}. "
                        "This divergence arises from regional differences in point allocation and cancellation rules."
                    ),
                    explanation_ta=(
                        f"தமிழ் 10 பொருத்தம் {p_cv.status} எனவும், வட இந்திய அஷ்டகூடம் {a_cv.status} எனவும் வேறுபடுகிறது. "
                        "இவ்வேறுபாடு பிராந்திய மரபுகளின் விதிமுறைகளை பிரதிபலிக்கிறது."
                    ),
                    rule_sources=["TAM-POR-01", "ASHTA-01", "RULE-MATRIX-08"],
                )
            )

    # 2. Traditional Matching Favorable vs Individual Vedic Affliction
    v_cv = category_verdicts.get("vedic_individual")
    if v_cv and (p_cv and p_cv.status == "FAVORABLE" or a_cv and a_cv.status == "FAVORABLE"):
        if v_cv.status in ("UNFAVORABLE", "MIXED"):
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.PORUTHAM_VS_VEDIC_INDIVIDUAL,
                    title_en="Traditional Nakshatra Matching Favorable but Individual Vedic Affliction Present",
                    title_ta="நட்சத்திரப் பொருத்தம் சாதகம் ஆனால் தனிநபர் ஜாதக களத்திர பாவம் சவால்",
                    finding_a="Traditional Nakshatra-based matching (Porutham / Ashtakoota) is favorable.",
                    finding_b=f"Individual Vedic 7th house analysis shows {v_cv.status} ({v_cv.score_summary}).",
                    resolution_principle=(
                        "Nakshatra matching reflects generic psycho-biological resonance between Moon positions. "
                        "Individual 7th house and Karaka disposition reflects real-world matrimonial promise. "
                        "Individual afflictions must not be ignored simply because Moon stars match."
                    ),
                    explanation_en=(
                        "While Nakshatra matching is favorable, individual chart analysis reveals planetary afflictions "
                        "requiring mature alignment, horoscope counseling, and remedies."
                    ),
                    explanation_ta=(
                        "நட்சத்திரப் பொருத்தம் சாதகமாக இருந்தாலும், தனிநபர் ஜாதக களத்திர பாவத்தில் சில கிரக பாதிப்புகள் உள்ளன."
                    ),
                    rule_sources=["VED-MARR-01", "VED-MARR-02", "RULE-MATRIX-08"],
                )
            )

    # 3. Individual Kuja Dosha Present vs Mutual Samadosham Mitigation
    mk = getattr(mutual_doshas, "samadosham", None) or getattr(mutual_doshas, "mutual_kuja", None)
    if mk:
        g_has_kuja = bool(groom_vedic and groom_vedic.kuja_dosha and groom_vedic.kuja_dosha.is_present)
        b_has_kuja = bool(bride_vedic and bride_vedic.kuja_dosha and bride_vedic.kuja_dosha.is_present)
        outcome = getattr(mk, "mutual_balance", None) or getattr(mk, "samadosham_outcome", None)

        if (g_has_kuja or b_has_kuja) and outcome in (SamadoshamOutcome.MUTUALLY_MATCHED, SamadoshamOutcome.MITIGATED):
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.INDIVIDUAL_DOSHA_VS_MUTUAL_MITIGATION,
                    title_en="Individual Kuja Dosha Preserved Despite Mutual Balancing (Samadosham)",
                    title_ta="செவ்வாய் தோஷம் சமதோஷ சமநிலைக்குப் பிறகும் தனிப்பட்ட முறையில் பதிவு செய்யப்பட்டுள்ளது",
                    finding_a=f"Individual Kuja Dosha active (Groom: {g_has_kuja}, Bride: {b_has_kuja}).",
                    finding_b=f"Mutual analysis reports {outcome.value if hasattr(outcome, 'value') else outcome} due to partner's matching chart.",
                    resolution_principle=(
                        "Muhurta Chintamani affirms that mutual matching balances the dynamic between partners "
                        "(Doshasya samyam bhavati), but does NOT erase the individual natal Mars placement. "
                        "Individual findings remain transparently documented."
                    ),
                    explanation_en=(
                        "Individual Kuja Dosha is retained in chart findings, but mutual counterpoise significantly "
                        "mitigates matrimonial friction."
                    ),
                    explanation_ta=(
                        "தனிநபர் ஜாதகத்தில் செவ்வாய் தோஷம் இருந்தாலும், இருவர் ஜாதகங்களின் சமதோஷ சமநிலை அதன் தாக்கத்தை தணிக்கிறது."
                    ),
                    rule_sources=["DOS-KUJA-01", "DOS-KUJA-06", "RULE-MATRIX-08"],
                )
            )

    # 4. Synastry Polarity Divergence (Moon vs Lagna)
    if synastry:
        m_axis = getattr(synastry.moon_to_moon, "sign_relationship", "") or getattr(synastry.moon_to_moon, "axis_type", "")
        l_axis = getattr(synastry.lagna_to_lagna, "lagna_relationship", "") or getattr(synastry.lagna_to_lagna, "axis_type", "")
        if ("SAMASAPTAKA" in m_axis or "TRIKONA" in m_axis) and "SHADASHTAKA" in l_axis:
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.SYNASTRY_POLARITY_CONFLICT,
                    title_en="Harmonious Moon Axis Accompanied by Tense Lagna Axis",
                    title_ta="சாதகமான சந்திர அச்சு ஆனால் சவாலான லக்ன அச்சு",
                    finding_a=f"Moon-to-Moon axis is harmonious ({m_axis}).",
                    finding_b=f"Lagna-to-Lagna axis is tense ({l_axis}).",
                    resolution_principle=(
                        "Moon axis governs emotional sensitivity and instinctive bonding; Lagna axis governs conscious "
                        "personality and daily life philosophies. Couple will experience deep internal affection but may "
                        "differ in administrative or external matters."
                    ),
                    explanation_en="Instinctive emotional harmony is strong, but external habits and worldviews require conscious patience.",
                    explanation_ta="மனரீதியான ஒற்றுமை சிறப்பாக உள்ளது, ஆனால் வெளிப்புற பழக்கவழக்கங்களில் பரஸ்பர அனுசரிப்பு தேவை.",
                    rule_sources=["VED-MARR-05", "RULE-MATRIX-08"],
                )
            )

    # 5. KP 7th CSL Promise Divergence
    kp_cv = category_verdicts.get("kp_promise")
    if kp_cv and kp_cv.status != "INDETERMINATE":
        if (p_cv and p_cv.status == "FAVORABLE") and kp_cv.status == "UNFAVORABLE":
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.KP_PROMISE_VS_COMPATIBILITY,
                    title_en="Favorable Traditional Compatibility Diverges from KP Cuspal Promise",
                    title_ta="சாதகமான பாரம்பரிய பொருத்தம் கே.பி உப அதிபதி நிருபணத்துடன் வேறுபடுகிறது",
                    finding_a="Traditional Nakshatra matching is Favorable.",
                    finding_b="KP 7th Cuspal Sub-Lord signifies separating houses (1, 6, 10).",
                    resolution_principle=(
                        "Traditional matching evaluates inter-chart resonance, whereas KP CSL evaluates the natal "
                        "promise of marital fruition. If the CSL signifies separating houses, potential hurdles in "
                        "legal execution or timing may occur regardless of mutual fondness."
                    ),
                    explanation_en="Strong mutual compatibility exists, but KP cuspal sub-lords indicate timing hurdles or delays in formalizing the alliance.",
                    explanation_ta="இருவரிடையே நல்ல பொருத்தம் இருந்தாலும், கே.பி உப அதிபதி திருமண நிகழ்வில் சில தாமதங்களை காட்டுகிறார்.",
                    rule_sources=["KP-MARR-01", "RULE-MATRIX-08"],
                )
            )

    # 6. Birth Time Boundary Sensitivity
    if synastry and synastry.has_boundary_sensitivity:
        conflicts.append(
            ConflictFinding(
                conflict_type=ConflictType.BIRTH_TIME_BOUNDARY_SENSITIVITY,
                title_en="Birth-Time Boundary Sensitivity Detected",
                title_ta="பிறப்பு நேர எல்லை உணர்திறன் கண்டறியப்பட்டுள்ளது",
                finding_a="Planetary coordinates fall within 15 arcminutes of a Navamsa (D9) or Cusp boundary.",
                finding_b="Small uncertainties in recorded birth time could shift Navamsa signs or Cusp Sub-Lords.",
                resolution_principle=(
                    "Highlight boundary proximity transparently without manufacturing unwarranted certainty. "
                    "Recommend professional birth-time rectification if exact timing is uncertain."
                ),
                explanation_en="Certain divisional placements are sensitive to minor birth-time inaccuracies. Rectification recommended.",
                explanation_ta="சில நவாம்ச அமைப்புகள் சில நிமிட பிறப்பு நேர மாற்றத்தால் மாறக்கூடும். நேர உறுதிப்படுத்தல் நல்லது.",
                rule_sources=["VED-MARR-04", "RULE-MATRIX-08"],
            )
        )

    # 7. Missing or Unsupported Components
    for cat_id, cv in category_verdicts.items():
        if cv.status == "INDETERMINATE":
            conflicts.append(
                ConflictFinding(
                    conflict_type=ConflictType.MISSING_OR_UNSUPPORTED_DATA,
                    title_en=f"Incomplete Data in Category: {cv.category_name_en}",
                    title_ta=f"முழுமையற்ற தரவு: {cv.category_name_ta}",
                    finding_a=f"Category {cv.category_name_en} returned INDETERMINATE.",
                    finding_b="Mandatory chart data or astrological coordinates were not supplied.",
                    resolution_principle="Missing data is never treated as favorable; category remains explicitly indeterminate.",
                    explanation_en=f"Category {cv.category_name_en} could not be fully calculated.",
                    explanation_ta=f"{cv.category_name_ta} முழுமையாக கணிக்கப்படவில்லை.",
                    rule_sources=["RULE-MATRIX-08"],
                )
            )

    return conflicts


# ---------------------------------------------------------------------------
# Core Composite Engine Function
# ---------------------------------------------------------------------------

def evaluate_composite_marriage_assessment(
    groom_chart: Optional[MarriageChartContext] = None,
    bride_chart: Optional[MarriageChartContext] = None,
    tamil_porutham: Optional[TamilPoruthamSummary] = None,
    ashtakoota: Optional[AshtakootaSummary] = None,
    groom_vedic: Optional[IndividualVedicAnalysis] = None,
    bride_vedic: Optional[IndividualVedicAnalysis] = None,
    mutual_doshas: Optional[MutualDoshaAnalysisResult] = None,
    synastry: Optional[BidirectionalSynastryResult] = None,
    kp_marriage: Optional[KpMarriageAnalysisResult] = None,
) -> CompositeMarriageAssessment:
    """Execute complete deterministic Phase 8 composite marriage compatibility assessment.

    Consumes existing phase results without recalculating their internal logic.
    If full MarriageChartContext instances are supplied and phase results are omitted,
    dispatches cleanly to completed engine modules.
    """
    decision_path: List[str] = []
    all_warnings: List[str] = []
    missing_evidence: List[str] = []
    supportive_indicators: List[str] = []
    challenging_indicators: List[str] = []

    # Safe extraction of IDs
    g_id = getattr(groom_chart, "person_id", "Groom") or "Groom"
    b_id = getattr(bride_chart, "person_id", "Bride") or "Bride"
    g_name = getattr(groom_chart, "person_name", "Groom") or "Groom"
    b_name = getattr(bride_chart, "person_name", "Bride") or "Bride"

    # Step 0: Execute missing components if chart contexts are available
    if groom_chart and bride_chart:
        if tamil_porutham is None:
            try:
                tamil_porutham = evaluate_tamil_10_poruthams(groom_chart, bride_chart)
            except Exception as exc:
                all_warnings.append(f"Could not compute Tamil 10 Poruthams: {str(exc)}")

        if ashtakoota is None:
            try:
                ashtakoota = evaluate_ashtakoota_matching(groom_chart, bride_chart)
            except Exception as exc:
                all_warnings.append(f"Could not compute Ashtakoota: {str(exc)}")

        if groom_vedic is None or bride_vedic is None:
            try:
                dual_vedic = evaluate_dual_vedic_marriage_analysis(groom_chart, bride_chart)
                groom_vedic = dual_vedic.groom_analysis
                bride_vedic = dual_vedic.bride_analysis
            except Exception as exc:
                all_warnings.append(f"Could not compute Vedic analysis: {str(exc)}")

        if mutual_doshas is None:
            try:
                mutual_doshas = evaluate_mutual_dosha_analysis(groom_chart, bride_chart)
            except Exception as exc:
                all_warnings.append(f"Could not compute Mutual Dosha analysis: {str(exc)}")

        if synastry is None:
            try:
                synastry = evaluate_bidirectional_synastry(groom_chart, bride_chart)
            except Exception as exc:
                all_warnings.append(f"Could not compute Synastry: {str(exc)}")

        if kp_marriage is None:
            try:
                kp_marriage = evaluate_kp_marriage_analysis(groom_chart, bride_chart)
            except Exception as exc:
                all_warnings.append(f"Could not compute KP analysis: {str(exc)}")

    # Step 1: Category Verdicts
    p_cv, p_supp, p_chal = _evaluate_porutham_category(tamil_porutham)
    a_cv, a_supp, a_chal = _evaluate_ashtakoota_category(ashtakoota)
    k_cv, papa_cv, m_supp, m_chal = _evaluate_mutual_dosha_category(mutual_doshas)
    v_cv, v_supp, v_chal = _evaluate_vedic_individual_category(groom_vedic, bride_vedic)
    s_cv, s_supp, s_chal = _evaluate_synastry_category(synastry)
    kp_cv, kp_time_cv, kp_supp, kp_chal = _evaluate_kp_category(kp_marriage)

    supportive_indicators.extend(p_supp + a_supp + m_supp + v_supp + s_supp + kp_supp)
    challenging_indicators.extend(p_chal + a_chal + m_chal + v_chal + s_chal + kp_chal)

    category_verdicts: Dict[str, CategoryVerdict] = {
        "tamil_porutham": p_cv,
        "ashtakoota": a_cv,
        "kuja_samadosham": k_cv,
        "papasamya": papa_cv,
        "vedic_individual": v_cv,
        "synastry": s_cv,
        "kp_promise": kp_cv,
        "kp_timing": kp_time_cv,
    }

    # Record missing evidence
    for cat_key, cv in category_verdicts.items():
        if cv.status == "INDETERMINATE":
            missing_evidence.append(f"{cv.category_name_en} data missing or indeterminate.")

    # Step 2: Detect Conflicts
    conflicts = _detect_astrological_conflicts(
        category_verdicts=category_verdicts,
        porutham=tamil_porutham,
        ashtakoota=ashtakoota,
        groom_vedic=groom_vedic,
        bride_vedic=bride_vedic,
        mutual_doshas=mutual_doshas,
        synastry=synastry,
        kp_marriage=kp_marriage,
    )

    # Step 3: Top-Level Decision Matrix Synthesis
    # Check for all indeterminate / empty inputs
    evaluated_cats = [cv for cv in category_verdicts.values() if cv.status != "INDETERMINATE"]

    if not evaluated_cats or (p_cv.status == "INDETERMINATE" and a_cv.status == "INDETERMINATE" and v_cv.status == "INDETERMINATE"):
        overall_outcome = CompatibilityOutcome.INDETERMINATE
        decision_path.append("Insufficient or missing foundational chart data across all major traditions.")

    # Check for critical classical vetoes within their traditions
    elif p_cv.vetoes_applied or a_cv.vetoes_applied:
        overall_outcome = CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
        all_vetoes = p_cv.vetoes_applied + a_cv.vetoes_applied
        decision_path.append(
            f"Unfavorable verdict assigned due to tradition-specific critical veto(es): {'; '.join(all_vetoes)}."
        )

    # Check for severe mutual Kuja imbalance
    elif k_cv.vetoes_applied:
        overall_outcome = CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
        decision_path.append("Unfavorable verdict assigned due to severe active Kuja Dosha mismatch without counterpoise.")

    # Check for severe Papasamya excess
    elif papa_cv.vetoes_applied and p_cv.status == "UNFAVORABLE":
        overall_outcome = CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
        decision_path.append("Unfavorable verdict assigned due to critical Papasamya malefic excess against bride.")

    # Check for dual-tradition rejection
    elif p_cv.status == "UNFAVORABLE" and a_cv.status == "UNFAVORABLE":
        overall_outcome = CompatibilityOutcome.UNFAVOURABLE_UNDER_SELECTED_RULES
        decision_path.append("Unfavorable verdict assigned because both Tamil Porutham and North Indian Ashtakoota are unfavorable.")

    # Check for full favorable alignment
    elif (
        p_cv.status in ("FAVORABLE", "INDETERMINATE")
        and a_cv.status in ("FAVORABLE", "INDETERMINATE")
        and k_cv.status in ("FAVORABLE", "INDETERMINATE")
        and papa_cv.status in ("FAVORABLE", "INDETERMINATE")
        and kp_cv.status != "UNFAVORABLE"
        and v_cv.status != "UNFAVORABLE"
        and (p_cv.status == "FAVORABLE" or a_cv.status == "FAVORABLE")
    ):
        overall_outcome = CompatibilityOutcome.FAVOURABLE_UNDER_SELECTED_RULES
        decision_path.append(
            "All evaluated classical traditions (Tamil Porutham, Ashtakoota, Samadosham, Papasamya) "
            "satisfy favorable criteria without critical afflictions."
        )

    # Otherwise MIXED_OR_CONDITIONAL
    else:
        overall_outcome = CompatibilityOutcome.MIXED_OR_CONDITIONAL
        reasons = []
        if p_cv.status == "MIXED":
            reasons.append("Tamil Porutham is within acceptable/moderate range (5.0-5.5)")
        if a_cv.status == "MIXED":
            reasons.append("Ashtakoota satisfies minimum threshold (18.0-20.5 pts)")
        if k_cv.status == "MIXED":
            reasons.append("Kuja Dosha mitigated by counterpoise")
        if papa_cv.status == "MIXED":
            reasons.append("Papasamya is within tolerable boundaries (25-50% excess)")
        if v_cv.status == "MIXED":
            reasons.append("Individual Vedic 7th house shows minor afflictions with aspectual relief")
        if conflicts:
            reasons.append(f"{len(conflicts)} cross-tradition or cross-lens divergence(s) identified")
        decision_path.append(
            f"Mixed / Conditional verdict assigned: {'; '.join(reasons) if reasons else 'Secondary afflictions present requiring mature communication and astrological mitigation'}."
        )

    # Recommendations for human astrologer review
    recommendations: List[str] = []
    if conflicts:
        recommendations.append("Review documented traditional divergences with family elders to align on preferred ancestral tradition.")
    if k_cv.status in ("MIXED", "UNFAVORABLE"):
        recommendations.append("Verify Mars placements and divisional counterpoise with an experienced Vedic astrologer.")
    if any(c.conflict_type == ConflictType.BIRTH_TIME_BOUNDARY_SENSITIVITY for c in conflicts):
        recommendations.append("Perform birth-time rectification if exact birth minutes are subject to memory inaccuracy.")
    if p_cv.vetoes_applied:
        recommendations.append("Rajju / Vedha affliction noted; seek guidance from a traditional Tamil Jyotish scholar.")
    if not recommendations:
        recommendations.append("Both charts demonstrate harmonious astrological alignment. Standard auspicious Muhurta recommended.")

    # Bilingual Explanations
    en_desc = (
        f"Overall Compatibility Verdict: {overall_outcome.value}. "
        f"Tamil Porutham: {p_cv.status} ({p_cv.score_summary}). "
        f"Ashtakoota: {a_cv.status} ({a_cv.score_summary}). "
        f"Kuja Samadosham: {k_cv.status}. Papasamya: {papa_cv.status}. "
        f"Vedic 7th House: {v_cv.status}. Synastry: {s_cv.status}. "
        f"KP Promise: {kp_cv.status}."
    )
    ta_desc = (
        f"ஒட்டுமொத்த பொருத்த முடிவு: {overall_outcome.value}. "
        f"தமிழ் பொருத்தம்: {p_cv.status} ({p_cv.score_summary}). "
        f"அஷ்டகூடம்: {a_cv.status} ({a_cv.score_summary}). "
        f"செவ்வாய் சமதோஷம்: {k_cv.status}. பாபசாம்யம்: {papa_cv.status}. "
        f"களத்திர பாவம்: {v_cv.status}. ஜாதக இணைவு: {s_cv.status}. "
        f"கே.பி வாக்குறுதி: {kp_cv.status}."
    )

    # Collect rule sources
    all_rule_sources = [
        "TAM-POR-01", "TAM-POR-02", "TAM-POR-03", "TAM-POR-04", "TAM-POR-05",
        "TAM-POR-06", "TAM-POR-07", "TAM-POR-08", "TAM-POR-09", "TAM-POR-10",
        "ASHTA-01", "ASHTA-02", "ASHTA-03", "ASHTA-04", "ASHTA-05", "ASHTA-06",
        "ASHTA-07", "ASHTA-08", "DOS-KUJA-01", "DOS-KUJA-06", "DOS-PAPA-01",
        "DOS-PAPA-02", "VED-MARR-01", "VED-MARR-04", "VED-MARR-05", "KP-MARR-01",
        "KP-MARR-02", "KP-MARR-03", "RULE-MATRIX-08",
    ]

    return CompositeMarriageAssessment(
        groom_person_id=g_id,
        bride_person_id=b_id,
        groom_name=g_name,
        bride_name=b_name,
        overall_outcome=overall_outcome,
        category_verdicts=category_verdicts,
        tamil_porutham=tamil_porutham,
        ashtakoota=ashtakoota,
        groom_vedic=groom_vedic,
        bride_vedic=bride_vedic,
        mutual_doshas=mutual_doshas,
        synastry=synastry,
        kp_marriage=kp_marriage,
        major_supportive_indicators=supportive_indicators,
        major_challenging_indicators=challenging_indicators,
        conflicting_findings=conflicts,
        missing_or_uncertain_evidence=missing_evidence,
        recommended_astrologer_review=recommendations,
        decision_path=decision_path,
        disclaimers=[COMPOSITE_DISCLAIMER_EN, COMPOSITE_DISCLAIMER_TA],
        rule_sources=all_rule_sources,
        warnings=all_warnings,
        explanation_en=en_desc,
        explanation_ta=ta_desc,
    )
