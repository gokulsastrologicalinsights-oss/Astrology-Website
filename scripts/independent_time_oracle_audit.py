"""
Standalone Independent Pure Time-Interval Oracle & Vimshottari Audit
====================================================================
Gokul's Astrological Insights

This test oracle does NOT import or reuse any production code from dasa_service.py
or kp_engine/vedic.py. It evaluates Vimshottari five-level periods purely in the
TIME DOMAIN:
1. Calculates Moon's angular progress within its birth Nakshatra (800' = 13°20').
2. Determines the starting Mahadasha lord from the birth Nakshatra.
3. Computes the theoretical unelapsed start instant of the Mahadasha:
   t_MD_start = t_birth - (progress * full_MD_days)
4. Recursively partitions the TIME interval [t_start, t_end] of each parent period
   into 9 child intervals proportional to the canonical Vimshottari years:
   duration_child = duration_parent * (years_child / 120.0)
5. Selects the child containing the birth instant:
   t_child_start <= t_birth < t_child_end  (or <= for final period)
6. Verifies that all 5 levels contain t_birth, interval containment holds,
   and child durations sum exactly to parent duration.
7. Tests:
   - 7 Astronomical balance fixtures
   - Boundary cases: before, at, and after a Bhukti boundary
   - Boundary cases: before, at, and after a Nakshatra boundary
   - Verification against backend API response and snapshot persistence.
"""

import sys
import os
import math

# Canonical Vimshottari Order and Durations (120 years total)
VIMSHOTTARI_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

VIMSHOTTARI_YEARS = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
}

TOTAL_VIMSHOTTARI_YEARS = 120.0
JULIAN_YEAR_DAYS = 365.25
JULIAN_MONTH_DAYS = 30.4375
STAR_SPAN_DEG = 800.0 / 60.0  # 13.333333333333334 degrees

LEVEL_NAMES = [
    "Mahadasha",
    "Antardasha",
    "Pratyantardasha",
    "Sookshmadasha",
    "Pranadasha",
]

def pure_time_oracle(moon_deg: float, birth_jd: float):
    """
    Pure time-interval evaluation of the active 5-level Vimshottari path.
    Completely decoupled from any production code.
    """
    norm_moon = moon_deg % 360.0
    star_idx = int(norm_moon // STAR_SPAN_DEG)
    star_start_deg = star_idx * STAR_SPAN_DEG
    star_end_deg = star_start_deg + STAR_SPAN_DEG

    progress = (norm_moon - star_start_deg) / STAR_SPAN_DEG
    rem_fraction = (star_end_deg - norm_moon) / STAR_SPAN_DEG

    md_lord = VIMSHOTTARI_ORDER[star_idx % 9]
    full_md_days = VIMSHOTTARI_YEARS[md_lord] * JULIAN_YEAR_DAYS
    elapsed_md_days = progress * full_md_days
    rem_md_days = rem_fraction * full_md_days

    # Theoretical start of the Mahadasha in time
    md_start_jd = birth_jd - elapsed_md_days
    md_end_jd = birth_jd + rem_md_days

    # Container for all 5 active levels
    active_path = []
    
    current_lord = md_lord
    current_start_jd = md_start_jd
    current_end_jd = md_end_jd
    current_duration = full_md_days

    active_path.append({
        "level": LEVEL_NAMES[0],
        "lord": current_lord,
        "start_jd": current_start_jd,
        "end_jd": current_end_jd,
        "full_duration_days": current_duration,
        "elapsed_at_birth": elapsed_md_days,
        "remaining_at_birth": rem_md_days,
        "contains_birth": (current_start_jd <= birth_jd <= current_end_jd),
    })

    # Recursively partition in TIME for levels 2..5
    for lvl in range(1, 5):
        parent_pos = VIMSHOTTARI_ORDER.index(current_lord)
        run_jd = current_start_jd
        selected_child = None
        children_sum = 0.0

        for k in range(9):
            child_lord = VIMSHOTTARI_ORDER[(parent_pos + k) % 9]
            child_dur = current_duration * (VIMSHOTTARI_YEARS[child_lord] / TOTAL_VIMSHOTTARI_YEARS)
            children_sum += child_dur
            child_end_jd = run_jd + child_dur

            # Half-open containment [run_jd, child_end_jd), inclusive on last interval
            is_in_interval = (run_jd <= birth_jd < child_end_jd) or (k == 8 and birth_jd >= run_jd - 1e-12)
            if is_in_interval and selected_child is None:
                selected_child = {
                    "level": LEVEL_NAMES[lvl],
                    "lord": child_lord,
                    "start_jd": run_jd,
                    "end_jd": child_end_jd,
                    "full_duration_days": child_dur,
                    "elapsed_at_birth": birth_jd - run_jd,
                    "remaining_at_birth": child_end_jd - birth_jd,
                    "contains_birth": (run_jd <= birth_jd <= child_end_jd + 1e-10),
                }

            run_jd = child_end_jd

        # Verify child duration sum equals parent duration
        assert abs(children_sum - current_duration) < 1e-9, f"Children sum mismatch at level {lvl}"
        assert selected_child is not None, f"No active child found at level {lvl}"

        # Verify interval containment: [child_start, child_end] is inside [parent_start, parent_end]
        assert selected_child["start_jd"] >= current_start_jd - 1e-9, "Child start precedes parent start"
        assert selected_child["end_jd"] <= current_end_jd + 1e-9, "Child end exceeds parent end"

        active_path.append(selected_child)
        current_lord = selected_child["lord"]
        current_start_jd = selected_child["start_jd"]
        current_end_jd = selected_child["end_jd"]
        current_duration = selected_child["full_duration_days"]

    return {
        "moon_deg": norm_moon,
        "star_index": star_idx,
        "star_start_deg": star_start_deg,
        "star_end_deg": star_end_deg,
        "progress": progress,
        "remaining_fraction": rem_fraction,
        "starting_mahadasha_lord": md_lord,
        "full_mahadasha_days": full_md_days,
        "elapsed_mahadasha_days": elapsed_md_days,
        "remaining_mahadasha_days": rem_md_days,
        "next_mahadasha_transition_jd": md_end_jd,
        "active_path": active_path,
    }


def main():
    print("================================================================================")
    print("STANDALONE PURE TIME-INTERVAL ORACLE AUDIT")
    print("================================================================================\n")

    sys.path.insert(0, os.path.abspath("backend"))
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # ---------------------------------------------------------------------------
    # TEST 1: The 7 Astronomical Reference Fixtures
    # ---------------------------------------------------------------------------
    fixtures = [
        {"name": "Chart 0: Uttara Ashadha (275.9224°)", "moon_deg": 275.9224, "birth_jd": 2448027.104167},
        {"name": "Chart 1: Standard Mid-Nakshatra (Rohini 45.5°)", "moon_deg": 45.5, "birth_jd": 2451545.0},
        {"name": "Chart 2: Partway Bhukti (Pushya 105.75°)", "moon_deg": 105.75, "birth_jd": 2450000.0},
        {"name": "Chart 3: Partway Antharam (Anuradha 218.42°)", "moon_deg": 218.42, "birth_jd": 2448000.0},
        {"name": "Chart 4: Near Nakshatra Ingress (Ashwini/Bharani 13.3333°)", "moon_deg": 13.3333, "birth_jd": 2452000.0},
        {"name": "Chart 5: Near Ingress Boundary (Shatabhisha 306.6660°)", "moon_deg": 306.6660, "birth_jd": 2453000.0},
        {"name": "Chart 6: Short Sookshma/Prana (Sun star Krittika 32.5°)", "moon_deg": 32.5, "birth_jd": 2454000.0},
    ]

    print("--- 1. AUDITING 7 ASTRONOMICAL FIXTURES AGAINST TIME-INTERVAL ORACLE ---")
    for fx in fixtures:
        oracle = pure_time_oracle(fx["moon_deg"], fx["birth_jd"])
        path_str = " -> ".join([lvl["lord"] for lvl in oracle["active_path"]])

        # Query backend API
        resp = client.post(
            "/api/v1/horoscope/dasa/direct",
            json={"moon_sidereal_deg": fx["moon_deg"], "birth_jd": fx["birth_jd"], "depth": 5}
        )
        assert resp.status_code == 200
        app_data = resp.json()
        bal = app_data["birth_dasa_balance"]

        # Validate Balance
        assert bal["starting_mahadasha_lord"] == oracle["starting_mahadasha_lord"]
        assert bal["starting_bhukti_lord"] == oracle["active_path"][1]["lord"]

        diff_full = abs(bal["mahadasha_full_duration"]["total_days"] - oracle["full_mahadasha_days"])
        diff_elapsed = abs(bal["elapsed_duration"]["total_days"] - oracle["elapsed_mahadasha_days"])
        diff_rem = abs(bal["remaining_balance"]["total_days"] - oracle["remaining_mahadasha_days"])
        diff_trans = abs(bal["next_dasa_transition_jd"] - oracle["next_mahadasha_transition_jd"])

        assert diff_full < 1e-4, f"Full days diff: {diff_full}"
        assert diff_elapsed < 1e-4, f"Elapsed days diff: {diff_elapsed}"
        assert diff_rem < 1e-4, f"Remaining days diff: {diff_rem}"
        assert diff_trans < 1e-4, f"Transition JD diff: {diff_trans}"

        # Validate active path in dasa_tree down to Level 5
        tree = app_data["dasa_tree"]
        active_nodes = []
        curr = tree
        while curr:
            act = [n for n in curr if n.get("is_active_at_birth")]
            if act:
                active_nodes.append(act[0])
                curr = act[0].get("sub_periods", [])
            else:
                break

        assert len(active_nodes) == 5, f"Expected 5 active nodes, got {len(active_nodes)}"
        for lvl_idx in range(5):
            expected_lord = oracle["active_path"][lvl_idx]["lord"]
            actual_lord = active_nodes[lvl_idx]["lord"]
            assert actual_lord == expected_lord, f"Level {lvl_idx+1} mismatch: expected {expected_lord}, got {actual_lord}"
            
            # Verify every level contains the birth instant
            assert oracle["active_path"][lvl_idx]["contains_birth"], f"Oracle level {lvl_idx+1} does not contain birth instant"

        print(f"[PASS] {fx['name']}")
        print(f"       Remaining Balance: {oracle['remaining_mahadasha_days']:.6f} days")
        print(f"       Active Path: {path_str}")

    # ---------------------------------------------------------------------------
    # TEST 1B: Explicit Mathematical Verification of Case 0 Mercury Bhukti Start
    # ---------------------------------------------------------------------------
    print("\n--- 1B. DETAILED 5-LEVEL TIMING BREAKDOWN FOR CASE 0 (UTTARA ASHADHA 275.9224°) ---")
    case0 = pure_time_oracle(275.9224, 2448027.104167)
    
    # Preceding Bhuktis in Sun Mahadasha: Sun(6), Moon(10), Mars(7), Rahu(18), Jupiter(16), Saturn(19)
    weights_prec = [6, 10, 7, 18, 16, 19]
    sum_w = sum(weights_prec) # 76
    assert sum_w == 76
    full_md = 6.0 * 365.25 # 2191.5 days
    comb_days = full_md * (sum_w / 120.0) # 1387.950000 days
    assert abs(comb_days - 1387.95) < 1e-9
    
    md_start_jd = case0["active_path"][0]["start_jd"] # 2446505.808697
    calc_mercury_start = md_start_jd + comb_days # 2447893.758697
    assert abs(calc_mercury_start - case0["active_path"][1]["start_jd"]) < 1e-9
    print(f"[PASS] Preceding Bhukti weights {weights_prec} sum to {sum_w}/120 (3.8 years exactly).")
    print(f"       3.8 years * 365.25 d/y = {comb_days:.6f} days (NOT 1387.6125d).")
    print(f"       MD Start ({md_start_jd:.6f}) + {comb_days:.6f}d = Mercury Start JD {calc_mercury_start:.6f}.")

    print("\n  Level-by-Level Timing Breakdown:")
    for lvl in case0["active_path"]:
        print(f"  - {lvl['level']} ({lvl['lord']}): Start JD={lvl['start_jd']:.6f}, End JD={lvl['end_jd']:.6f}, Full Dur={lvl['full_duration_days']:.6f}d, Elapsed={lvl['elapsed_at_birth']:.6f}d, Rem={lvl['remaining_at_birth']:.6f}d, Contains Birth={lvl['contains_birth']}")

    # ---------------------------------------------------------------------------
    # TEST 2: Exact Bhukti Boundary Cases (Before, At, and After)
    # ---------------------------------------------------------------------------
    print("\n--- 2. AUDITING BHUKTI BOUNDARY INSTANTS (BEFORE, AT, AFTER) ---")
    # In Sun MD (starts at 266.666667°):
    # Bhukti 1 is Sun (span = 13.333333333333334 * 6 / 120 = 0.6666666666666666°)
    # Bhukti 1 ends and Bhukti 2 (Moon) begins at: 266.6666666666667 + 0.6666666666666666 = 267.3333333333333°
    boundary_b_deg = 267.3333333333333
    delta = 0.00001 # approx 0.036 arcseconds

    # A. Immediately Before Bhukti Boundary -> Sun Bhukti
    res_before = pure_time_oracle(boundary_b_deg - delta, 2450000.0)
    assert res_before["active_path"][1]["lord"] == "Sun", f"Expected Sun Bhukti, got {res_before['active_path'][1]['lord']}"
    print(f"[PASS] Just Before Bhukti Boundary ({boundary_b_deg - delta:.6f}°): Bhukti = {res_before['active_path'][1]['lord']}")

    # B. Exactly At Bhukti Boundary -> Moon Bhukti (standard half-open [start, end))
    res_at = pure_time_oracle(boundary_b_deg, 2450000.0)
    assert res_at["active_path"][1]["lord"] == "Moon", f"Expected Moon Bhukti at boundary, got {res_at['active_path'][1]['lord']}"
    print(f"[PASS] Exactly At Bhukti Boundary ({boundary_b_deg:.6f}°): Bhukti = {res_at['active_path'][1]['lord']}")

    # C. Immediately After Bhukti Boundary -> Moon Bhukti
    res_after = pure_time_oracle(boundary_b_deg + delta, 2450000.0)
    assert res_after["active_path"][1]["lord"] == "Moon", f"Expected Moon Bhukti, got {res_after['active_path'][1]['lord']}"
    print(f"[PASS] Just After Bhukti Boundary ({boundary_b_deg + delta:.6f}°): Bhukti = {res_after['active_path'][1]['lord']}")

    # ---------------------------------------------------------------------------
    # TEST 3: Exact Nakshatra Boundary Cases (Before, At, and After)
    # ---------------------------------------------------------------------------
    print("\n--- 3. AUDITING NAKSHATRA BOUNDARY INSTANTS (BEFORE, AT, AFTER) ---")
    # Ashwini (Ketu) ends and Bharani (Venus) begins at exactly 13.333333333333334°
    boundary_nak_deg = 13.333333333333334

    # A. Immediately Before Nakshatra Boundary -> Ketu Mahadasha (Mercury Bhukti, ending subperiod)
    res_nak_before = pure_time_oracle(boundary_nak_deg - delta, 2450000.0)
    assert res_nak_before["starting_mahadasha_lord"] == "Ketu"
    assert res_nak_before["active_path"][1]["lord"] == "Mercury"
    print(f"[PASS] Just Before Nakshatra Boundary ({boundary_nak_deg - delta:.6f}°): MD={res_nak_before['starting_mahadasha_lord']}, Bhukti={res_nak_before['active_path'][1]['lord']}")

    # B. Exactly At Nakshatra Boundary -> Venus Mahadasha (Venus Bhukti, opening subperiod)
    res_nak_at = pure_time_oracle(boundary_nak_deg, 2450000.0)
    assert res_nak_at["starting_mahadasha_lord"] == "Venus"
    assert res_nak_at["active_path"][1]["lord"] == "Venus"
    print(f"[PASS] Exactly At Nakshatra Boundary ({boundary_nak_deg:.6f}°): MD={res_nak_at['starting_mahadasha_lord']}, Bhukti={res_nak_at['active_path'][1]['lord']}")

    # C. Immediately After Nakshatra Boundary -> Venus Mahadasha (Venus Bhukti)
    res_nak_after = pure_time_oracle(boundary_nak_deg + delta, 2450000.0)
    assert res_nak_after["starting_mahadasha_lord"] == "Venus"
    assert res_nak_after["active_path"][1]["lord"] == "Venus"
    print(f"[PASS] Just After Nakshatra Boundary ({boundary_nak_deg + delta:.6f}°): MD={res_nak_after['starting_mahadasha_lord']}, Bhukti={res_nak_after['active_path'][1]['lord']}")

    # ---------------------------------------------------------------------------
    # TEST 4: Date Convention and Balance Identity Verification
    # ---------------------------------------------------------------------------
    print("\n--- 4. AUDITING BALANCE IDENTITY AND CONVENTIONS ---")
    ref_case = pure_time_oracle(275.9224, 2448027.104167)
    elapsed = ref_case["elapsed_mahadasha_days"]
    rem = ref_case["remaining_mahadasha_days"]
    full = ref_case["full_mahadasha_days"]
    
    # Exact equality: Elapsed + Remaining = Full
    assert abs((elapsed + rem) - full) < 1e-11
    print(f"[PASS] Identity Elapsed ({elapsed:.6f}d) + Remaining ({rem:.6f}d) == Full ({full:.6f}d)")
    assert abs(rem - 670.204530) < 1e-5, f"Expected 670.204530 days, got {rem}"
    print(f"[PASS] Verified remaining balance for 275.9224° is exactly 670.204530 days within tolerance.")

    print("\n================================================================================")
    print("ALL TIME-INTERVAL ORACLE VERIFICATIONS PASSED CLEANLY.")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
