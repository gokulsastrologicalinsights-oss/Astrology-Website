"""Birth Time Rectification (BTR) Assistant Service.

Integrates KP Krishnamurti Paddhati principles, Vimshottari Dasa-Bhukti-Antara,
Ruling Planets, and Divisional Lagna Shifts (D9 Navamsha & D60 Shashtiamsha)
to rectify birth times down to second-level precision.
"""

from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.btr import (
    BtrCandidateDetail,
    BtrCredibleInterval,
    BtrEventBreakdown,
    BtrLifeEventInput,
    BtrRequest,
    BtrResponse,
    BtrShiftComparison,
    BtrTransitSummary,
    VargaLagnaDetail,
)
from app.services.kp_engine.chart import BirthInfo
from app.services.kp_engine.constants import SIGN_LORDS
from app.services.kp_engine.ephemeris import SwissEphemeris
from app.services.kp_engine.rectification import (
    LifeEvent,
    _candidate_sort_key,
    _chart_for,
    _datetime_from_jd,
    _ruling_planet_set,
    _scan_snapshot,
    credible_interval,
    score_candidate,
    transit_confirmation,
)
from app.services.kp_engine.vedic import normalize_longitude, sign_name, star_lord, sub_lord
from app.services.timezone_utils import resolve_birth_datetime


# Standard Classical Life Event Presets for quick user selection
EVENT_TEMPLATES = [
    {
        "id": "marriage",
        "label": "Marriage / Sacred Union",
        "label_ta": "திருமணம்",
        "primary_house": 7,
        "secondary_houses": [2, 11],
        "description": "Primary 7th house (spouse/legal union) with 2nd (family addition) & 11th (fulfillment of desire).",
    },
    {
        "id": "first_job",
        "label": "First Job / Major Career Milestone",
        "label_ta": "முதல் வேலை / தொழில் உயர்வு",
        "primary_house": 10,
        "secondary_houses": [2, 6, 11],
        "description": "Primary 10th house (karma/status) with 2nd (income), 6th (service/employment) & 11th (gains).",
    },
    {
        "id": "childbirth",
        "label": "Childbirth / Progeny Blessing",
        "label_ta": "குழந்தைப் பிறப்பு",
        "primary_house": 5,
        "secondary_houses": [2, 11],
        "description": "Primary 5th house (progeny/putra) with 2nd (family expansion) & 11th (longed-for wish fulfilled).",
    },
    {
        "id": "accident_surgery",
        "label": "Major Accident / Surgery / Critical Illness",
        "label_ta": "விபத்து / அறுவை சிகிச்சை",
        "primary_house": 8,
        "secondary_houses": [6, 12],
        "description": "Primary 8th house (trauma/surgery) with 6th (disease/injury) & 12th (hospitalization).",
    },
    {
        "id": "relocation_foreign",
        "label": "Relocation / Long-Distance Foreign Settlement",
        "label_ta": "வெளிநாட்டுப் பயணம் / இடமாற்றம்",
        "primary_house": 12,
        "secondary_houses": [3, 9],
        "description": "Primary 12th house (foreign land) with 3rd (change of residence) & 9th (long-distance voyage).",
    },
    {
        "id": "property_vehicle",
        "label": "Property / Vehicle Purchase",
        "label_ta": "வீடு / வாகனம் வாங்குதல்",
        "primary_house": 4,
        "secondary_houses": [11, 12],
        "description": "Primary 4th house (fixed assets/conveyance) with 11th (acquisition) & 12th (capital expenditure).",
    },
    {
        "id": "education_degree",
        "label": "Higher Education Graduation / Degree",
        "label_ta": "உயர் கல்வி / பட்டம் பெறுதல்",
        "primary_house": 9,
        "secondary_houses": [4, 11],
        "description": "Primary 9th house (higher knowledge) with 4th (academic learning) & 11th (success).",
    },
    {
        "id": "lawsuit_dispute",
        "label": "Lawsuit Resolution / Court Decree",
        "label_ta": "வழக்கு வெற்றி / தீர்ப்பு",
        "primary_house": 6,
        "secondary_houses": [1, 11],
        "description": "Primary 6th house (litigation/disputes) with 1st (self victory) & 11th (triumph).",
    },
]

# 60 Classical Shashtiamsha (D60) Names & Nature according to BPHS
D60_NAMES = [
    ("Ghora", "Malefic"), ("Rakshasa", "Malefic"), ("Deva", "Benefic"), ("Kubera", "Benefic"),
    ("Yaksha", "Benefic"), ("Kinnara", "Benefic"), ("Bhrashta", "Malefic"), ("Kulaghna", "Malefic"),
    ("Garala", "Malefic"), ("Vahni", "Malefic"), ("Maya", "Malefic"), ("Purishaka", "Malefic"),
    ("Apampathi", "Benefic"), ("Marutvan", "Benefic"), ("Kala", "Malefic"), ("Sarpa", "Malefic"),
    ("Amrita", "Benefic"), ("Indu", "Benefic"), ("Mridu", "Benefic"), ("Komala", "Benefic"),
    ("Heramba", "Benefic"), ("Brahma", "Benefic"), ("Vishnu", "Benefic"), ("Maheshwara", "Benefic"),
    ("Deva", "Benefic"), ("Ardra", "Benefic"), ("Kalinasa", "Benefic"), ("Kshiteesvara", "Benefic"),
    ("Kamalakara", "Benefic"), ("Mandatmaja", "Benefic"), ("Mrityu", "Malefic"), ("Kala", "Malefic"),
    ("Davagni", "Malefic"), ("Ghora", "Malefic"), ("Adhama", "Malefic"), ("Kantaka", "Malefic"),
    ("Sudha", "Benefic"), ("Amrita", "Benefic"), ("Purnachandra", "Benefic"), ("Vishadagdha", "Malefic"),
    ("Kulanasa", "Malefic"), ("Vamshakshaya", "Malefic"), ("Utpata", "Malefic"), ("Kala", "Malefic"),
    ("Saumya", "Benefic"), ("Komala", "Benefic"), ("Sheetala", "Benefic"), ("Karaladamshtra", "Malefic"),
    ("Chandramukhi", "Benefic"), ("Praveena", "Benefic"), ("Kalapavaka", "Malefic"), ("Dandayudha", "Malefic"),
    ("Nirmala", "Benefic"), ("Saumya", "Benefic"), ("Kragara", "Malefic"), ("Atisheetala", "Benefic"),
    ("Amrita", "Benefic"), ("Payodhi", "Benefic"), ("Bhramana", "Malefic"), ("Chandrarekha", "Benefic"),
]

SIGN_NAMES_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def _calc_varga_lagna(asc_deg: float) -> Tuple[VargaLagnaDetail, VargaLagnaDetail]:
    """Computes exact D9 Navamsha Lagna and D60 Shashtiamsha Lagna from Ascendant longitude."""
    norm_asc = asc_deg % 360.0
    d1_sign_idx = int(norm_asc // 30.0) + 1  # 1 to 12
    deg_in_sign = norm_asc % 30.0

    # 1. D9 Navamsha calculation (each part is 3°20' = 3.333333°)
    nav_idx = min(8, int(deg_in_sign // (3.0 + 20.0 / 60.0)))
    # Fire (1,5,9) starts Aries(1); Earth (2,6,10) starts Cap(10); Air (3,7,11) starts Lib(7); Water (4,8,12) starts Can(4)
    if d1_sign_idx in (1, 5, 9):
        base_start = 1
    elif d1_sign_idx in (2, 6, 10):
        base_start = 10
    elif d1_sign_idx in (3, 7, 11):
        base_start = 7
    else:
        base_start = 4

    d9_sign_idx = ((base_start - 1 + nav_idx) % 12) + 1
    d9_sign_name = SIGN_NAMES_ORDER[d9_sign_idx - 1]
    d9_deg = (deg_in_sign % (3.0 + 20.0 / 60.0)) * 9.0
    pada_num = (nav_idx % 4) + 1
    d9_detail = VargaLagnaDetail(
        sign_index=d9_sign_idx,
        sign_name=d9_sign_name,
        degree_in_sign=round(d9_deg, 2),
        division_specific=f"Pada {pada_num} (Navamsha {nav_idx + 1}/9)",
    )

    # 2. D60 Shashtiamsha calculation (each part is 0.5° = 30 arcminutes)
    d60_part = min(59, int(deg_in_sign // 0.5))
    d60_sign_idx = ((d1_sign_idx - 1 + d60_part) % 12) + 1
    d60_sign_name = SIGN_NAMES_ORDER[d60_sign_idx - 1]
    d60_deg = (deg_in_sign % 0.5) * 60.0
    d60_name, d60_nature = D60_NAMES[d60_part]
    d60_detail = VargaLagnaDetail(
        sign_index=d60_sign_idx,
        sign_name=d60_sign_name,
        degree_in_sign=round(d60_deg, 2),
        division_specific=f"Part {d60_part + 1}/60: {d60_name} ({d60_nature})",
    )

    return d9_detail, d60_detail


def _parse_time_offset_str(offset_seconds: float) -> str:
    """Formats offset seconds into a human-readable +/- MMm SSs string."""
    sign = "+" if offset_seconds >= 0 else "-"
    abs_sec = round(abs(offset_seconds))
    mins = abs_sec // 60
    secs = abs_sec % 60
    if mins > 0:
        return f"{sign}{mins}m {secs:02d}s"
    return f"{sign}{secs}s"


def run_birth_time_rectification(request: BtrRequest) -> BtrResponse:
    """Performs full high-precision KP Birth Time Rectification.

    1. Coarse grid scan (e.g. 1.0 min steps over +/- window_minutes).
    2. Fine-grained refinement down to the second around top peak candidate.
    3. Cross-checks Dasa-Bhukti-Antara, Lagna Sub-Lord specificity, and Ruling Planets.
    4. Evaluates D9 Navamsha and D60 Shashtiamsha lagna shifts.
    """
    ayanamsa_str = "lahiri" if request.ayanamsa == 0 else "kp"
    eph = SwissEphemeris(ayanamsa=ayanamsa_str, node="true")

    # Build internal KP LifeEvent objects
    life_events = [
        LifeEvent(
            date=ev.event_date,
            primary=ev.primary_house,
            secondary=tuple(ev.secondary_houses),
            label=ev.label,
            time=ev.event_time or time(12, 0),
        )
        for ev in request.events
    ]

    # Resolve timezone & UTC moments
    local_dt, utc_dt, approx_jd, tz_name, offset_hours = resolve_birth_datetime(
        request.birth_date, request.birth_time, request.timezone
    )
    approx_local = local_dt.replace(tzinfo=None)
    approx_ut = utc_dt.replace(tzinfo=None)
    event_jds = tuple(ev.jd_ut(offset_hours, eph) for ev in life_events)

    earliest_candidate = approx_jd - request.window_minutes / 1440.0
    for ev, ev_jd in zip(life_events, event_jds):
        if ev_jd < earliest_candidate:
            raise ValueError(
                f"Life event '{ev.label}' on {ev.date} predates the candidate birth time range."
            )

    # Pre-calculate Ruling Planets if requested
    rp_set = None
    if request.use_ruling_planets:
        now_utc = datetime.now(dt_timezone.utc).replace(tzinfo=None)
        now_jd = eph.jd_ut(now_utc)
        rp_set = _ruling_planet_set(
            now_jd, request.latitude, request.longitude, eph, offset_hours
        )

    # 1. Coarse Scan
    snapshot = _scan_snapshot(approx_jd, eph)
    step_min = max(0.2, min(5.0, request.step_minutes))
    window_min = max(5.0, min(180.0, request.window_minutes))
    n_coarse_steps = max(2, round(window_min * 2.0 / step_min))

    scored_candidates = []
    for s in range(n_coarse_steps + 1):
        cand_jd = approx_jd - window_min / 1440.0 + (s * step_min) / 1440.0
        sc = score_candidate(
            cand_jd,
            request.latitude,
            request.longitude,
            life_events,
            tz_hours=offset_hours,
            rp_set=rp_set,
            identity=None,
            eph=eph,
            approx_jd=approx_jd,
            event_jds=event_jds,
            _snapshot=snapshot,
        )
        scored_candidates.append(sc)

    scored_candidates.sort(key=_candidate_sort_key)
    top_coarse = scored_candidates[0]

    # 2. Second-Level Refinement if requested
    best_candidate_raw = top_coarse
    if request.refine_seconds:
        # Fine grid around top candidate (+/- 2 minutes in 5-second steps)
        refine_window_min = min(2.0, step_min * 1.5)
        fine_step_min = 5.0 / 60.0  # 5 seconds
        n_fine_steps = round(refine_window_min * 2.0 / fine_step_min)

        fine_candidates = []
        base_fine_jd = top_coarse.jd_ut - refine_window_min / 1440.0
        for fs in range(n_fine_steps + 1):
            f_cand_jd = base_fine_jd + (fs * fine_step_min) / 1440.0
            f_sc = score_candidate(
                f_cand_jd,
                request.latitude,
                request.longitude,
                life_events,
                tz_hours=offset_hours,
                rp_set=rp_set,
                identity=None,
                eph=eph,
                approx_jd=approx_jd,
                event_jds=event_jds,
                _snapshot=snapshot,
            )
            fine_candidates.append(f_sc)

        fine_candidates.sort(key=_candidate_sort_key)
        best_candidate_raw = fine_candidates[0]
        # Include top fine candidates into the master pool
        scored_candidates.extend(fine_candidates[:5])
        scored_candidates.sort(key=_candidate_sort_key)

    # 3. Posterior Credible Interval
    ci = credible_interval(scored_candidates)

    # 4. Transit Cross-Check
    transit_info = transit_confirmation(
        best_candidate_raw.jd_ut,
        request.latitude,
        request.longitude,
        life_events,
        tz_hours=offset_hours,
        eph=eph,
    )

    # Convert candidate to local times & compute Varga lagnas
    def _cand_to_dto(c) -> BtrCandidateDetail:
        local_cand_dt = _datetime_from_jd(c.jd_ut) + timedelta(hours=offset_hours)
        offset_sec = (c.jd_ut - approx_jd) * 86400.0
        _pos, _cusps, asc = _chart_for(c.jd_ut, request.latitude, request.longitude, eph)
        d9, d60 = _calc_varga_lagna(asc)

        # Normalise confidence: max score ratio clamped to 0..100%
        conf = min(99.0, max(30.0, (c.total / (len(life_events) * 3.5 + 1.0)) * 100.0))

        ev_breakdowns = []
        for es in c.events:
            ev_breakdowns.append(
                BtrEventBreakdown(
                    label=es.label,
                    event_date=str(es.date),
                    primary_house=es.primary,
                    secondary_houses=list(es.secondary),
                    lsl_hit=es.lsl_hit,
                    lsl_score=round(es.lsl_score, 2),
                    mahadasha_lord=es.mahadasha_lord,
                    antardasha_lord=es.antardasha_lord,
                    pratyantardasha_lord=es.pratyantar_lord,
                    dasha_hit=es.dasha_hit,
                    dasha_score=round(es.dasha_score, 2),
                )
            )

        return BtrCandidateDetail(
            time_str=local_cand_dt.strftime("%H:%M:%S"),
            offset_minutes=round(c.offset_minutes, 2),
            offset_seconds=round(offset_sec, 1),
            offset_formatted=_parse_time_offset_str(offset_sec),
            lsl=c.lsl,
            specificity=round(c.specificity, 2),
            lsl_score=round(c.lsl_score, 2),
            dasha_score=round(c.dasha_score, 2),
            rp_score=round(c.rp_score, 2),
            identity_score=round(c.identity_score, 2),
            total_score=round(c.total, 2),
            confidence_percentage=round(conf, 1),
            strikes=c.strikes,
            d9_sign=d9.sign_name,
            d60_sign=d60.sign_name,
            events=ev_breakdowns,
        )

    best_dto = _cand_to_dto(best_candidate_raw)

    # 5. Build Shift Comparison between Approx Time vs Rectified Time
    _pos_approx, _cusps_approx, asc_approx = _chart_for(
        approx_jd, request.latitude, request.longitude, eph
    )
    approx_lsl = sub_lord(asc_approx)
    approx_d9, approx_d60 = _calc_varga_lagna(asc_approx)

    _pos_rect, _cusps_rect, asc_rect = _chart_for(
        best_candidate_raw.jd_ut, request.latitude, request.longitude, eph
    )
    rect_lsl = sub_lord(asc_rect)
    rect_d9, rect_d60 = _calc_varga_lagna(asc_rect)

    lsl_diff = approx_lsl != rect_lsl
    d9_diff = approx_d9.sign_name != rect_d9.sign_name or approx_d9.division_specific != rect_d9.division_specific
    d60_diff = approx_d60.sign_name != rect_d60.sign_name or approx_d60.division_specific != rect_d60.division_specific

    explanation_parts = []
    if lsl_diff:
        explanation_parts.append(
            f"The KP Lagna Sub-Lord (LSL) shifted from {approx_lsl} to {rect_lsl}, which dramatically aligns with the signifying houses of your life milestones."
        )
    else:
        explanation_parts.append(
            f"The KP Lagna Sub-Lord remained {rect_lsl}, but the degrees consolidated closer to the sub-lord cusp center."
        )

    if d9_diff:
        explanation_parts.append(
            f"D9 Navamsha Lagna moved to {rect_d9.sign_name} ({rect_d9.division_specific}), altering your soul's karmic partnership blueprint."
        )
    if d60_diff:
        explanation_parts.append(
            f"D60 Shashtiamsha Lagna shifted to {rect_d60.sign_name} ({rect_d60.division_specific}), settling root-cause past-life karma precisely."
        )

    shift_comparison = BtrShiftComparison(
        approx_time=request.birth_time.strftime("%H:%M:%S"),
        rectified_time=best_dto.time_str,
        time_offset_seconds=best_dto.offset_seconds,
        time_offset_formatted=best_dto.offset_formatted,
        approx_lsl=approx_lsl,
        rectified_lsl=rect_lsl,
        lsl_changed=lsl_diff,
        approx_d9=approx_d9,
        rectified_d9=rect_d9,
        d9_changed=d9_diff,
        approx_d60=approx_d60,
        rectified_d60=rect_d60,
        d60_changed=d60_diff,
        explanation=" ".join(explanation_parts),
    )

    # 6. Deduplicate and collect top 10 candidates
    unique_candidates = {}
    for c in scored_candidates:
        t_str = (_datetime_from_jd(c.jd_ut) + timedelta(hours=offset_hours)).strftime("%H:%M:%S")
        if t_str not in unique_candidates or c.total > unique_candidates[t_str].total:
            unique_candidates[t_str] = c

    sorted_uniques = sorted(unique_candidates.values(), key=_candidate_sort_key)
    top_dtos = [_cand_to_dto(c) for c in sorted_uniques[:10]]

    # Candidate distribution for frontend visualization curve
    distribution = [
        {
            "time": (_datetime_from_jd(c.jd_ut) + timedelta(hours=offset_hours)).strftime("%H:%M:%S"),
            "offset_min": round(c.offset_minutes, 2),
            "score": round(c.total, 2),
            "lsl": c.lsl,
        }
        for c in sorted_uniques[:40]
    ]

    ci_dto = BtrCredibleInterval(
        start_time=(ci.start_ut + timedelta(hours=offset_hours)).strftime("%H:%M:%S"),
        end_time=(ci.end_ut + timedelta(hours=offset_hours)).strftime("%H:%M:%S"),
        peak_time=best_dto.time_str,
        spread_minutes=round(ci.spread_minutes, 2),
        posterior_mass_percentage=round(ci.mass * 100.0, 1),
    )

    transit_summary = BtrTransitSummary(
        confirmed_tests=transit_info.matched,
        total_tests=transit_info.total,
        match_percentage=round((transit_info.matched / max(1, transit_info.total)) * 100.0, 1),
    )

    rect_local_dt = datetime.combine(
        request.birth_date,
        datetime.strptime(best_dto.time_str, "%H:%M:%S").time(),
    )

    verdict = (
        f"Rectification confirmed! Your exact rectified birth time is {best_dto.time_str} "
        f"({best_dto.offset_formatted} from recorded time). Lagna Sub-Lord: {best_dto.lsl}, "
        f"Navamsha D9 Lagna: {rect_d9.sign_name}, Shashtiamsha D60: {rect_d60.sign_name}."
    )

    return BtrResponse(
        approx_birth_datetime=approx_local.strftime("%Y-%m-%d %H:%M:%S"),
        rectified_birth_datetime=rect_local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        rectified_time=best_dto.time_str,
        offset_seconds=best_dto.offset_seconds,
        offset_formatted=best_dto.offset_formatted,
        rectified_lsl=best_dto.lsl,
        best_candidate=best_dto,
        shift_comparison=shift_comparison,
        credible_interval=ci_dto,
        transit_confirmation=transit_summary,
        top_candidates=top_dtos,
        candidate_distribution=distribution,
        total_candidates_evaluated=len(scored_candidates),
        astrological_verdict=verdict,
    )
