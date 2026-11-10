#!/usr/bin/env python3
"""Standalone CLI script to publish KP Daily Raasi Palan to Facebook Page.

Can be run manually or invoked via:
- Linux Cron (e.g. `0 6 * * * /path/to/venv/bin/python /path/to/backend/scripts/daily_facebook_poster.py`)
- Windows Task Scheduler
- Render Cron Job / GitHub Actions

Usage:
  python backend/scripts/daily_facebook_poster.py
  python backend/scripts/daily_facebook_poster.py --dry-run
  python backend/scripts/daily_facebook_poster.py --date 2026-11-11 --rashi Aries
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import settings
from app.services.facebook_publisher import generate_and_post_daily_raasi_palan


def main():
    parser = argparse.ArgumentParser(description="Publish KP Daily Raasi Palan to Facebook Page")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date in YYYY-MM-DD (defaults to today in Asia/Kolkata)",
    )
    parser.add_argument(
        "--rashi",
        type=str,
        default=settings.fb_post_rashi or "all",
        help="Rashi to post: 'all' for all 12 rashis, or single e.g. 'Aries' (default: all)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=settings.fb_post_delay_seconds or 20,
        help="Delay in seconds between posts when posting all 12 rashis (default: 20s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the formatted post without sending to Facebook",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Gokul's Astrological Insights - Daily Facebook Raasi Palan Poster")
    print("=" * 70)
    print(f"Target Date : {args.date or 'Today (IST)'}")
    print(f"Target Rashi: {args.rashi}")
    print(f"Delay (sec) : {args.delay}s between posts")
    print(f"Dry Run     : {args.dry_run}")
    print("-" * 70)

    try:
        result = asyncio.run(
            generate_and_post_daily_raasi_palan(
                target_date=args.date,
                rashi=args.rashi,
                dry_run=args.dry_run,
            )
        )

        if args.dry_run:
            print("\n[DRY RUN PREVIEW - NOT POSTED TO FACEBOOK]:\n")
            if "posts" in result:
                for idx, item in enumerate(result["posts"], 1):
                    print(f"--- ({idx}/12) {item['rashi_name']} ---")
                    print(item["message"])
                    print("\n" + ("-" * 50) + "\n")
            else:
                print(result.get("message"))
            print("=" * 70)
            print("Preview generated successfully!")
        else:
            print("\n[SUCCESSFULLY PUBLISHED TO FACEBOOK!]")
            if "results" in result:
                print(f"Total Attempted : {result.get('total_attempted')}")
                print(f"Successful      : {result.get('successful_posts')}")
                print(f"Failed          : {result.get('failed_posts')}")
                for r in result.get("results", []):
                    status_tag = "✓" if r.get("success") else "✗"
                    print(f"  [{status_tag}] {r.get('rashi')}: {r.get('post_id') or r.get('error')}")
            else:
                print(f"Post ID : {result.get('post_id')}")
                print(f"URL     : {result.get('fb_url')}")
            print("=" * 70)

    except Exception as exc:
        print(f"\n[ERROR]: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
