"""Automated Daily Scheduler for Facebook Page Publishing.

Runs as a lightweight, robust background worker inside FastAPI.
Calculates the exact daily IST execution window (e.g. 06:00 AM IST), sleeps asynchronously,
computes real-time KP predictions, and publishes directly to Facebook Page.

Features automatic catch-up: if the server was powered off or sleeping during the
scheduled 06:00 AM window, it automatically publishes today's 12 Rashis as soon as
the server starts up.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.facebook_publisher import (
    fetch_posted_rashis_for_date,
    generate_and_post_daily_raasi_palan,
)

logger = logging.getLogger("gai.facebook.scheduler")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
STATE_FILE = os.path.join(DATA_DIR, "facebook_scheduler_state.json")

_scheduler_task: Optional[asyncio.Task] = None
_background_publish_task: Optional[asyncio.Task] = None
_publish_in_progress: bool = False
_last_run_info: Dict[str, Any] = {
    "last_run_time": None,
    "last_posted_date": None,
    "status": "idle",
    "post_id": None,
    "error": None,
}


def _load_persisted_state() -> Dict[str, Any]:
    """Loads previous run history from disk."""
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_persisted_state(state: Dict[str, Any]) -> None:
    """Persists run state to disk so server restarts don't lose track of daily posts."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.error(f"Failed to persist facebook scheduler state: {exc}")


def calculate_next_run(target_time_str: str = "06:00", tz_name: str = "Asia/Kolkata") -> datetime:
    """Calculates the upcoming datetime in the target timezone for the given HH:MM."""
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)

    try:
        parts = target_time_str.split(":")
        target_hour = int(parts[0])
        target_minute = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        target_hour, target_minute = 6, 0

    candidate = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # If the target time for today has already passed, schedule for tomorrow
    if candidate <= now:
        candidate += timedelta(days=1)

    return candidate


def is_past_target_time(target_time_str: str = "06:00", tz_name: str = "Asia/Kolkata") -> bool:
    """Checks whether the current time in the timezone is past today's scheduled target time."""
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)

    try:
        parts = target_time_str.split(":")
        target_hour = int(parts[0])
        target_minute = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        target_hour, target_minute = 6, 0

    today_target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    return now >= today_target


def get_scheduler_status() -> Dict[str, Any]:
    """Returns current status and telemetry of the daily scheduler."""
    is_running = _scheduler_task is not None and not _scheduler_task.done()
    next_run = calculate_next_run(settings.fb_post_time_ist, "Asia/Kolkata") if is_running else None

    # Merge persisted state only while idle before any run has occurred in this process
    if not _publish_in_progress and _last_run_info.get("status") == "idle" and not _last_run_info.get("last_posted_date"):
        persisted = _load_persisted_state()
        if persisted:
            _last_run_info.update(persisted)

    return {
        "auto_post_enabled": settings.fb_auto_post_enabled,
        "is_running": is_running,
        "in_progress": _publish_in_progress,
        "post_time_ist": settings.fb_post_time_ist,
        "post_rashi": settings.fb_post_rashi,
        "next_run_ist": next_run.strftime("%Y-%m-%d %H:%M:%S %Z") if next_run else None,
        "last_run": _last_run_info,
    }


def _summarize_publish_result(result: Dict[str, Any]) -> str:
    """Builds a concise status label for scheduler telemetry."""
    if result.get("post_id"):
        return str(result["post_id"])
    total = result.get("total_attempted", 12)
    ok = result.get("successful_posts", 0)
    skipped = result.get("skipped_existing", 0)
    if skipped == total and total > 0:
        return f"{ok}/{total} posted (already on page)"
    return f"{ok}/{total} posted"


async def run_and_record_daily_publish(
    execution_date: Optional[str] = None,
    rashi: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """Publishes daily horoscope (idempotently by default) and records scheduler telemetry."""
    global _publish_in_progress
    tz = ZoneInfo("Asia/Kolkata")
    target_date = execution_date or datetime.now(tz).strftime("%Y-%m-%d")
    target_rashi = (rashi or settings.fb_post_rashi or "all").strip()
    skip_dup = False if force else (True if target_rashi.lower() == "all" else False)

    logger.info(
        f"Running Facebook publish for date: {target_date} (Rashi: {target_rashi}, skip_existing={skip_dup})"
    )
    _publish_in_progress = True
    _last_run_info["status"] = "running"
    _last_run_info["error"] = None

    try:
        result = await generate_and_post_daily_raasi_palan(
            target_date=target_date,
            rashi=target_rashi,
            dry_run=False,
            skip_if_already_posted=skip_dup,
        )
        succeeded = bool(result.get("success"))
        _last_run_info["last_run_time"] = datetime.now(tz).isoformat()
        if succeeded:
            _last_run_info["last_posted_date"] = target_date
            _last_run_info["status"] = "success"
            _last_run_info["error"] = None
        else:
            _last_run_info["status"] = "partial" if result.get("successful_posts", 0) > 0 else "failed"
            _last_run_info["error"] = f"{result.get('failed_posts', 0)} rashi(s) failed to post"
        _last_run_info["post_id"] = _summarize_publish_result(result)
        _save_persisted_state(_last_run_info)
        logger.info(
            f"Facebook publish finished for {target_date}: status={_last_run_info['status']}, result={_last_run_info['post_id']}"
        )
        return result
    except Exception as post_err:
        logger.exception(f"Error publishing daily Facebook post for {target_date}: {post_err}")
        _last_run_info["last_run_time"] = datetime.now(tz).isoformat()
        _last_run_info["status"] = "failed"
        _last_run_info["error"] = str(post_err)
        _save_persisted_state(_last_run_info)
        raise
    finally:
        _publish_in_progress = False


def trigger_background_publish(
    execution_date: Optional[str] = None,
    rashi: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """Schedules a non-blocking daily publish task on the running loop if one is not active."""
    global _background_publish_task, _publish_in_progress
    tz = ZoneInfo("Asia/Kolkata")
    target_date = execution_date or datetime.now(tz).strftime("%Y-%m-%d")
    target_rashi = (rashi or settings.fb_post_rashi or "all").strip()

    if _publish_in_progress or (_background_publish_task is not None and not _background_publish_task.done()):
        return {
            "success": True,
            "accepted": True,
            "status": "already_running",
            "target_date": target_date,
            "rashi": target_rashi,
        }

    async def _runner() -> None:
        try:
            await run_and_record_daily_publish(
                execution_date=target_date,
                rashi=target_rashi,
                force=force,
            )
        except Exception:
            # Errors are already logged and recorded in _last_run_info
            pass

    _publish_in_progress = True
    _last_run_info["status"] = "running"
    _last_run_info["error"] = None
    loop = asyncio.get_running_loop()
    try:
        _background_publish_task = loop.create_task(_runner())
    except Exception:
        _publish_in_progress = False
        raise
    return {
        "success": True,
        "accepted": True,
        "status": "queued",
        "target_date": target_date,
        "rashi": target_rashi,
    }


async def _execute_daily_publish(execution_date: str) -> None:
    """Helper to publish horoscope from the scheduler loop without crashing the loop."""
    try:
        await run_and_record_daily_publish(execution_date=execution_date)
    except Exception:
        pass


async def run_startup_catchup_check() -> bool:
    """Checks whether today's scheduled post was missed and publishes only missing Rashis.

    Returns True if a catch-up publish or state sync ran, False otherwise.
    """
    tz = ZoneInfo("Asia/Kolkata")
    persisted = _load_persisted_state()
    today_str = datetime.now(tz).strftime("%Y-%m-%d")
    last_date = persisted.get("last_posted_date")

    if not is_past_target_time(settings.fb_post_time_ist, "Asia/Kolkata") or last_date == today_str:
        return False

    already_posted = await fetch_posted_rashis_for_date(today_str)
    target_rashi = settings.fb_post_rashi.strip().lower()
    is_already_complete = (
        len(already_posted) >= 12
        if target_rashi == "all"
        else target_rashi in already_posted
    )

    if is_already_complete:
        logger.info(
            f"Catch-up: {today_str} ({settings.fb_post_rashi}) is already posted on Facebook. Syncing state without re-posting."
        )
        _last_run_info.update({
            "last_run_time": datetime.now(tz).isoformat(),
            "last_posted_date": today_str,
            "status": "success",
            "post_id": "12/12 posted (already on page)" if target_rashi == "all" else already_posted[target_rashi].get("post_id"),
            "error": None,
        })
        _save_persisted_state(_last_run_info)
        return True

    logger.info(
        f"Catch-up: Today's ({today_str}) scheduled post has {len(already_posted)}/12 on Facebook after {settings.fb_post_time_ist} IST. Publishing remaining..."
    )
    await _execute_daily_publish(today_str)
    return True


async def _daily_scheduler_loop() -> None:
    """Continuous loop running every 24 hours at the designated IST time, with startup catch-up."""
    tz = ZoneInfo("Asia/Kolkata")
    logger.info(
        f"Facebook Daily Poster scheduler active. Target daily time: {settings.fb_post_time_ist} IST (Rashi: {settings.fb_post_rashi})"
    )

    # 1. Startup Catch-Up Check:
    try:
        await run_startup_catchup_check()
    except Exception as catchup_exc:
        logger.error(f"Error during startup catch-up post: {catchup_exc}")

    # 2. Main Daily Loop
    while True:
        try:
            now = datetime.now(tz)
            next_run = calculate_next_run(settings.fb_post_time_ist, "Asia/Kolkata")
            wait_seconds = (next_run - now).total_seconds()

            logger.info(
                f"Next scheduled Facebook post at: {next_run.strftime('%Y-%m-%d %H:%M:%S IST')} (sleeping for {int(wait_seconds)} seconds)"
            )

            await asyncio.sleep(wait_seconds)

            # Execution time: publish KP daily horoscope
            execution_date = datetime.now(tz).strftime("%Y-%m-%d")
            await _execute_daily_publish(execution_date)

            # Sleep 60 seconds to prevent re-triggering within the same minute
            await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Facebook scheduler background task was cancelled.")
            break
        except Exception as exc:
            logger.exception(f"Unexpected error in Facebook scheduler loop: {exc}")
            await asyncio.sleep(300)


def start_facebook_scheduler() -> bool:
    """Launches the background scheduler task if enabled and not already running."""
    global _scheduler_task
    if _scheduler_task is not None and not _scheduler_task.done():
        logger.info("Facebook scheduler task is already running.")
        return True

    loop = asyncio.get_event_loop()
    _scheduler_task = loop.create_task(_daily_scheduler_loop())
    logger.info("Facebook background scheduler task created successfully.")
    return True


def stop_facebook_scheduler() -> None:
    """Cancels the active background scheduler task."""
    global _scheduler_task
    if _scheduler_task is not None and not _scheduler_task.done():
        _scheduler_task.cancel()
        _scheduler_task = None
        logger.info("Facebook background scheduler stopped.")
