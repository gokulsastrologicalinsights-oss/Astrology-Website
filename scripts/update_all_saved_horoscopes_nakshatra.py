"""Batch Script to update in-depth Nakshatra analysis for all saved horoscopes in Supabase."""

import sys
import os
import time
import json

# Setup backend path
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND_DIR)

import app.config  # Loads .env files automatically
from app.services.auth_service import get_supabase_client
from app.services.ephemeris import calculate_full_horoscope
from app.services.nakshatra_engine import analyze_saved_chart_nakshatras

def run_update():
    sb = get_supabase_client()
    if not sb:
        print("[Error] Supabase client could not be initialized.", flush=True)
        return

    print("Fetching saved horoscopes count...", flush=True)
    head_resp = sb.table("saved_horoscopes").select("id", count="exact").limit(1).execute()
    total_count = head_resp.count or 700
    print(f"Total saved horoscopes in database: {total_count}", flush=True)

    page_size = 25
    offset = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0

    out_dir = os.path.join(BACKEND_DIR, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "saved_horoscope_nakshatra_analyses.json")

    all_analyses = {}
    if os.path.exists(out_path):
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                all_analyses = json.load(f)
            print(f"Loaded {len(all_analyses)} previously cached analyses from disk.", flush=True)
        except Exception:
            all_analyses = {}

    stats = {
        "Ashwini": 0, "Bharani": 0, "Krittika": 0, "Rohini": 0,
        "Mrigashira": 0, "Ardra": 0, "Punarvasu": 0, "Pushya": 0, "Ashlesha": 0,
        "total_rules_triggered": 0,
    }

    while offset < total_count:
        print(f"\nProcessing batch {offset} to {min(offset + page_size, total_count)}...", flush=True)
        rows = []
        retries = 3
        while retries > 0:
            try:
                resp = sb.table("saved_horoscopes") \
                    .select("id, person_name, birth_date, birth_time, latitude, longitude, timezone, ayanamsa_id, calculation_result") \
                    .order("created_at", desc=True) \
                    .range(offset, offset + page_size - 1) \
                    .execute()
                rows = resp.data or []
                break
            except Exception as e:
                print(f"  [Retry {4 - retries}] Fetch failed at offset {offset}: {e}", flush=True)
                retries -= 1
                time.sleep(2.0)

        if not rows and retries == 0:
            print(f"  Skipping batch at offset {offset} due to persistent timeout.", flush=True)
            offset += page_size
            continue

        if not rows:
            break

        for row in rows:
            r_id = row["id"]
            p_name = row.get("person_name") or "Unnamed"
            b_date = row.get("birth_date")
            b_time = row.get("birth_time")
            calc_res = row.get("calculation_result") or {}

            # If already has natchathira_analysis in database, collect and skip update
            existing_analysis = calc_res.get("natchathira_analysis")
            if existing_analysis and existing_analysis.get("valid"):
                all_analyses[r_id] = existing_analysis
                for active in existing_analysis.get("active_nakshatras_summary", []):
                    n_name = active["nakshatra"]
                    if n_name in stats:
                        stats[n_name] += 1
                stats["total_rules_triggered"] += existing_analysis.get("total_rules_matched", 0)
                updated_count += 1
                continue

            # Check if we already have it in local cache
            if r_id in all_analyses:
                cached_analysis = all_analyses[r_id]
                calc_res["natchathira_analysis"] = cached_analysis
                for active in cached_analysis.get("active_nakshatras_summary", []):
                    n_name = active["nakshatra"]
                    if n_name in stats:
                        stats[n_name] += 1
                stats["total_rules_triggered"] += cached_analysis.get("total_rules_matched", 0)
                try:
                    sb.table("saved_horoscopes").update({"calculation_result": calc_res}).eq("id", r_id).execute()
                    updated_count += 1
                except Exception as e:
                    print(f"  [Error] Failed to update row {r_id}: {e}", flush=True)
                    error_count += 1
                continue

            # Get or calculate horoscope data
            horo_data = calc_res.get("horoscope")
            if not horo_data and b_date and b_time:
                try:
                    computed = calculate_full_horoscope(
                        birth_date=b_date,
                        birth_time=b_time,
                        latitude=float(row.get("latitude") or 13.0827),
                        longitude=float(row.get("longitude") or 80.2707),
                        timezone=row.get("timezone") or "Asia/Kolkata",
                        ayanamsa_id=int(row.get("ayanamsa_id") or 0),
                    )
                    horo_data = computed.model_dump()
                    calc_res["horoscope"] = horo_data
                except Exception as e:
                    print(f"  [Skip] Calculation failed for {p_name} ({r_id}): {e}", flush=True)
                    skipped_count += 1
                    continue

            if not horo_data:
                skipped_count += 1
                continue

            # Run in-depth analysis
            analysis = analyze_saved_chart_nakshatras(horo_data, birth_date_str=b_date)
            analysis["person_name"] = p_name
            analysis["horoscope_id"] = r_id

            # Update stats
            for active in analysis.get("active_nakshatras_summary", []):
                n_name = active["nakshatra"]
                if n_name in stats:
                    stats[n_name] += 1
            stats["total_rules_triggered"] += analysis.get("total_rules_matched", 0)

            all_analyses[r_id] = analysis
            calc_res["natchathira_analysis"] = analysis

            try:
                sb.table("saved_horoscopes").update({"calculation_result": calc_res}).eq("id", r_id).execute()
                updated_count += 1
            except Exception as e:
                print(f"  [Error] Failed to update row {r_id}: {e}", flush=True)
                error_count += 1

        print(f"  Batch complete. Cumulative verified/updated: {updated_count}, Errors: {error_count}, Skipped: {skipped_count}", flush=True)
        offset += page_size

        # Periodically persist cache after each batch
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_analyses, f, ensure_ascii=False, indent=2)

        time.sleep(0.3)

    print("\n" + "="*60, flush=True)
    print("ALL SAVED HOROSCOPES NATCHATHIRA ANALYSIS COMPLETED!", flush=True)
    print(f"Total Charts Analyzed & Cached: {len(all_analyses)}", flush=True)
    print(f"Total Rules Triggered across database: {stats['total_rules_triggered']}", flush=True)
    print(f"Star Occurrence Frequencies in charts:", flush=True)
    for star, count in stats.items():
        if star != "total_rules_triggered":
            print(f"  - {star}: {count} charts", flush=True)
    print(f"Local cache written to: {out_path}", flush=True)
    print("="*60, flush=True)

if __name__ == "__main__":
    run_update()
