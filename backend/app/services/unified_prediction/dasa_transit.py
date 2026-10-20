"""Vimshottari Dasa and Supporting Transit Evaluator for Marriage Timing.

This module evaluates marriage timing eligibility using:
1. Classical 3-level Vimshottari Dasha hierarchy (Mahadasha, Antardasha, Pratyantardasha).
2. KP significator confluence (planets signifying houses 2, 7, 11).
3. Vedic Dasha eligibility (7th lord, Lagna lord, 2nd/11th lords, Venus).
4. Supporting Double Transit of Jupiter and Saturn (K.N. Rao, Timing of Marriage).

Classical Citations & Provenance:
- Vimshottari Dasha timing: BPHS, Ch. 46. [SOURCE_VERIFIED]
- Double Transit supporting condition: K.N. Rao, Timing of Marriage (1993). [SOURCE_VERIFIED as supporting]
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import date

import xalen
import xalen.swe as xswe
from app.services.dasa_calendar import jd_to_gregorian_datetime, gregorian_to_iso
from app.services.dasa_service import generate_vimshottari_hierarchy
from app.services.unified_prediction.models import (
    TimingWindow,
    UnifiedTimingReport,
    TimingStatus,
    RuleProvenanceTag,
)


def gregorian_to_jd(year: int, month: int, day: int, hour: float = 12.0) -> float:
    """Convert Gregorian date to Julian Day via Swiss Ephemeris."""
    return xswe.julday(year, month, day, hour)


def evaluate_double_transit(
    transit_jd: float,
    target_signs: Set[int],
    ayanamsa_id: int = 0,
) -> bool:
    """Evaluate K.N. Rao's Double Transit condition at a target epoch.
    
    Jupiter aspects 1st (conjunction), 5th, 7th, and 9th from its sign.
    Saturn aspects 1st (conjunction), 3rd, 7th, and 10th from its sign.
    
    Parameters
    ----------
    transit_jd : float
        Julian day of the transit epoch.
    target_signs : set of int
        1-indexed signs of Lagna, 7th house, Lagna lord, and 7th lord.
    """
    try:
        # Body 5 = Jupiter, Body 6 = Saturn
        jup_pos = xalen.planet_position(transit_jd, 5, True, ayanamsa_id)
        sat_pos = xalen.planet_position(transit_jd, 6, True, ayanamsa_id)
        
        jup_sign = int((jup_pos["longitude"] % 360.0) // 30.0) + 1
        sat_sign = int((sat_pos["longitude"] % 360.0) // 30.0) + 1
        
        # Jupiter aspects: 1, 5, 7, 9
        jup_aspect_signs = {((jup_sign - 1 + (h - 1)) % 12) + 1 for h in (1, 5, 7, 9)}
        # Saturn aspects: 1, 3, 7, 10
        sat_aspect_signs = {((sat_sign - 1 + (h - 1)) % 12) + 1 for h in (1, 3, 7, 10)}
        
        jup_satisfied = bool(jup_aspect_signs & target_signs)
        sat_satisfied = bool(sat_aspect_signs & target_signs)
        
        return jup_satisfied and sat_satisfied
    except Exception:
        return False


def find_marriage_timing_windows(
    moon_lon: float,
    birth_jd: float,
    birth_year: int,
    search_start_year: int,
    search_end_year: int,
    lagna_sign: int,
    seventh_house_sign: int,
    lagna_lord_sign: int,
    seventh_lord_sign: int,
    kp_marriage_significators: Set[str],
    vedic_marriage_significators: Set[str],
    utc_offset_hours: float = 0.0,
    max_candidate_windows: int = 5,
) -> Tuple[TimingStatus, Optional[UnifiedTimingReport]]:
    """Scan Vimshottari Dasha tree and evaluate candidate marriage windows.
    
    Returns
    -------
    tuple: (TimingStatus, Optional[UnifiedTimingReport])
    """
    if search_start_year >= search_end_year:
        search_end_year = search_start_year + 5

    try:
        search_start_jd = gregorian_to_jd(search_start_year, 1, 1)
        search_end_jd = gregorian_to_jd(search_end_year, 12, 31)
    except Exception:
        return TimingStatus.TIMING_NOT_DETERMINABLE, None

    search_start_iso = f"{search_start_year}-01-01"
    search_end_iso = f"{search_end_year}-12-31"

    target_signs: Set[int] = {
        lagna_sign,
        seventh_house_sign,
        lagna_lord_sign,
        seventh_lord_sign,
    }

    try:
        # Calculate 3-level Vimshottari tree (MD -> AD -> PD)
        tree, _ = generate_vimshottari_hierarchy(moon_lon, birth_jd, depth=3)
        raw_dasa = [node.model_dump() for node in tree]
    except Exception:
        return TimingStatus.TIMING_NOT_DETERMINABLE, None

    candidate_windows: List[TimingWindow] = []

    for md_node in raw_dasa:
        md_lord = md_node["lord"]
        md_start = md_node["start_jd"]
        md_end = md_node["end_jd"]

        # Fast prune: if Mahadasha is completely outside search window, skip
        if md_end <= search_start_jd or md_start >= search_end_jd:
            continue

        md_is_kp = md_lord in kp_marriage_significators
        md_is_vedic = md_lord in vedic_marriage_significators

        for ad_node in md_node.get("sub_periods", []):
            ad_lord = ad_node["lord"]
            ad_start = ad_node["start_jd"]
            ad_end = ad_node["end_jd"]

            if ad_end <= search_start_jd or ad_start >= search_end_jd:
                continue

            ad_is_kp = ad_lord in kp_marriage_significators
            ad_is_vedic = ad_lord in vedic_marriage_significators

            # Qualifying Dasha Condition:
            # Both MD and AD must connect to marriage significators in at least one system
            has_dasa_qualification = (md_is_kp or md_is_vedic) and (ad_is_kp or ad_is_vedic)
            if not has_dasa_qualification:
                continue

            # Evaluate Supporting Double Transit at midpoint of Antardasha
            mid_jd = 0.5 * (max(ad_start, search_start_jd) + min(ad_end, search_end_jd))
            double_tr = evaluate_double_transit(mid_jd, target_signs)

            # Compute Window Dates
            eff_start_jd = max(ad_start, search_start_jd)
            eff_end_jd = min(ad_end, search_end_jd)
            
            sy, sm, sd, _, _, _ = jd_to_gregorian_datetime(eff_start_jd, utc_offset_hours)
            ey, em, ed, _, _, _ = jd_to_gregorian_datetime(eff_end_jd, utc_offset_hours)

            start_iso = gregorian_to_iso(sy, sm, sd)
            end_iso = gregorian_to_iso(ey, em, ed)

            # Algorithmic Confidence Scoring
            # Base Dasha qualification: 0.50
            # Dual tradition Dasha match: +0.20
            # Supporting Double Transit active: +0.30
            score = 0.50
            if (md_is_kp and ad_is_kp) and (md_is_vedic and ad_is_vedic):
                score += 0.20
            if double_tr:
                score += 0.30

            # Pratyantardasha (PD) refinement if available
            best_pd_lord = None
            for pd_node in ad_node.get("sub_periods", []):
                pd_lord = pd_node["lord"]
                if pd_lord in kp_marriage_significators or pd_lord in vedic_marriage_significators:
                    best_pd_lord = pd_lord
                    break

            candidate_windows.append(
                TimingWindow(
                    start_date=start_iso,
                    end_date=end_iso,
                    mahadasha=md_lord,
                    antardasha=ad_lord,
                    pratyantardasha=best_pd_lord,
                    double_transit_active=double_tr,
                    kp_significator_confluence=(md_is_kp and ad_is_kp),
                    confidence_score=round(min(score, 1.0), 2),
                )
            )

    if not candidate_windows:
        return TimingStatus.NO_WINDOW_IN_RANGE, UnifiedTimingReport(
            best_window=None,
            evaluated_windows_count=0,
            search_start_date=search_start_iso,
            search_end_date=search_end_iso,
            rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
        )

    # Sort candidate windows by confidence score descending, then chronologically
    candidate_windows.sort(key=lambda w: (-w.confidence_score, w.start_date))
    best_window = candidate_windows[0]

    return TimingStatus.WINDOW_FOUND, UnifiedTimingReport(
        best_window=best_window,
        evaluated_windows_count=len(candidate_windows),
        search_start_date=search_start_iso,
        search_end_date=search_end_iso,
        rule_provenance=RuleProvenanceTag.SOURCE_VERIFIED,
    )
