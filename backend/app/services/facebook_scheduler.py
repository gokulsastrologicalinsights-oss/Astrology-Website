"""Automated Daily Scheduler for Facebook Page Publishing.

Runs as a lightweight, robust background worker inside FastAPI.
Calculates the exact daily IST execution window (e.g. 06:00 AM IST), sleeps asynchronously,
computes real-time KP predictions, and publishes directly to Facebook Page.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.facebook_publisher import generate_and_post_daily_raasi_palan

logger = logging.getLogger("gai.facebook.scheduler")

_scheduler_task: Optional[asyncio.Task] = None
_last_run_info: Dict[str, Any] = {
    "last_run_time": None,
    "status": "idle",
    "post_id": None,
    "error": None,
}


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


def get_scheduler_status() -> Dict[str, Any]:
    """Returns current status and telemetry of the daily scheduler."""
    is_running = _scheduler_task is not None and not _scheduler_task.done()
    next_run = calculate_next_run(settings.fb_post_time_ist, "Asia/Kolkata") if is_running else None
    
    return {
        "auto_post_enabled": settings.fb_auto_post_enabled,
        "is_running": is_running,
        "post_time_ist": settings.fb_post_time_ist,
        "post_rashi": settings.fb_post_rashi,
        "next_run_ist": next_run.strftime("%Y-%m-%d %H:%M:%S %Z") if next_run else None,
        "last_run": _last_run_info,
    }


async def _daily_scheduler_loop() -> None:
    """Continuous loop running every 24 hours at the designated IST time."""
    logger.info(
        f"Facebook Daily Poster scheduler active. Target daily time: {settings.fb_post_time_ist} IST (Rashi: {settings.fb_post_rashi})"
    )

    while True:
        try:
            tz = ZoneInfo("Asia/Kolkata")
            now = datetime.now(tz)
            next_run = calculate_next_run(settings.fb_post_time_ist, "Asia/Kolkata")
            wait_seconds = (next_run - now).total_seconds()

            logger.info(
                f"Next scheduled Facebook post at: {next_run.strftime('%Y-%m-%d %H:%M:%S IST')} (sleeping for {int(wait_seconds)} seconds)"
            )
            
            await asyncio.sleep(wait_seconds)

            # Execution time: publish KP daily horoscope
            execution_date = datetime.now(tz).strftime("%Y-%m-%d")
            logger.info(f"Triggering scheduled daily Facebook post for date: {execution_date}")

            try:
                result = await generate_and_post_daily_raasi_palan(
                    target_date=execution_date,
                    rashi=settings.fb_post_rashi,
                    dry_run=False,
                )
                _last_run_info["last_run_time"] = datetime.now(tz).isoformat()
                _last_run_info["status"] = "success" if result.get("success") else "failed"
                _last_run_info["post_id"] = result.get("post_id") or f"{result.get('successful_posts', 0)}/12 posted"
                _last_run_info["error"] = None
                logger.info(f"Daily Facebook post successful! Result: {_last_run_info['post_id']}")
            except Exception as post_err:
                logger.exception(f"Error publishing daily Facebook post: {post_err}")
                _last_run_info["last_run_time"] = datetime.now(tz).isoformat()
                _last_run_info["status"] = "failed"
                _last_run_info["error"] = str(post_err)

            # Sleep 60 seconds to prevent re-triggering within the same minute
            await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Facebook scheduler background task was cancelled.")
            break
        except Exception as exc:
            logger.exception(f"Unexpected error in Facebook scheduler loop: {exc}")
            # Brief pause before restarting loop on unexpected error
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
