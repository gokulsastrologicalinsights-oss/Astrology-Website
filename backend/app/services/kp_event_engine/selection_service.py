"""KP Event Prediction Engine - Event Selection and Ordering Service.

Implements deterministic filtering, ranking, and display limits:
1. Calculates grades for all configured events.
2. Shows GREEN and ORANGE events.
3. Shows at most two RED events, selected by highest support score.
4. Orders displayed events by:
   - Final grade: GREEN (0), ORANGE (1), RED (2).
   - Support score descending.
   - Denial score ascending.
   - Event name ascending (tie-breaker).
5. Limits to a maximum of 5 displayed events per period while retaining
   all evaluated events in calculation metadata.
"""

from __future__ import annotations
from typing import List, Tuple
from .grading_service import GradeResult

GRADE_SORT_ORDER = {
    "green": 0,
    "STRONG": 0,
    "orange": 1,
    "MODERATE": 1,
    "red": 2,
    "WEAK": 2,
}


def sort_key_for_event(event: GradeResult) -> Tuple[int, int, int, str]:
    """Deterministic sorting key:
    1. Color order: green=0, orange=1, red=2
    2. Support score: descending (-support_score)
    3. Denial score: ascending (+denial_score)
    4. Event name: alphabetical ascending (case-insensitive)
    """
    color_rank = GRADE_SORT_ORDER.get(event.final_color, 99)
    return (
        color_rank,
        -event.support_score,
        event.denial_score,
        event.event_name.lower(),
    )


def select_and_order_events(
    all_graded_events: List[GradeResult],
    max_displayed: int = 5,
    max_red: int = 2,
) -> Tuple[List[GradeResult], List[GradeResult]]:
    """Filters and ranks events for display according to strict Section 7 rules:
    - Includes GREEN and ORANGE events.
    - Limits RED events to at most max_red (default 2), chosen by highest support score.
    - Orders by: Final grade (GREEN, ORANGE, RED), support desc, denial asc, name asc.
    - Caps total displayed events at max_displayed (default 5).

    Returns:
        (displayed_events, all_evaluated_events_sorted)
    """
    # 1. Sort all events deterministically
    sorted_all = sorted(all_graded_events, key=sort_key_for_event)

    # 2. Partition by final color
    greens = [e for e in sorted_all if e.final_color == "green"]
    oranges = [e for e in sorted_all if e.final_color == "orange"]
    reds = [e for e in sorted_all if e.final_color == "red"]

    # 3. For RED events: select top max_red by highest support score,
    # then lowest denial score, then alphabetical name
    def red_sort_key(e: GradeResult):
        return (-e.support_score, e.denial_score, e.event_name.lower())

    sorted_reds = sorted(reds, key=red_sort_key)
    allowed_reds = sorted_reds[:max_red]

    # 4. Pool candidate events: GREENs, then ORANGEs, plus allowed REDs
    candidates: List[GradeResult] = []
    candidates.extend(greens)
    candidates.extend(oranges)
    candidates.extend(allowed_reds)

    # Re-sort candidates using the standard deterministic sort key
    candidates_sorted = sorted(candidates, key=sort_key_for_event)

    # 5. Cap at max_displayed (default 5)
    # If more than 5, priority is GREEN, then ORANGE, then strongest RED (up to max 2 RED)
    displayed = candidates_sorted[:max_displayed]

    return (displayed, sorted_all)
