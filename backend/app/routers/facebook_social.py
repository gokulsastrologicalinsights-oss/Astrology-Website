"""Facebook Social Integration API Router.

Endpoints for previewing (Tamil text format), testing, and triggering
KP Daily Raasi Palan publications to a connected Facebook Page.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.services.facebook_publisher import (
    generate_and_post_daily_raasi_palan,
    verify_facebook_credentials,
)
from app.services.instagram_publisher import verify_instagram_credentials
from app.services.telegram_notifier import (
    send_daily_posters_to_telegram,
    send_telegram_text,
    verify_telegram_credentials,
)
from app.services.facebook_scheduler import (
    get_scheduler_status,
    run_and_record_daily_publish,
    start_facebook_scheduler,
    stop_facebook_scheduler,
    trigger_background_publish,
)

logger = logging.getLogger("gai.facebook.router")

router = APIRouter(prefix="/api/v1/social/facebook", tags=["Facebook Social Media"])


class PublishRequest(BaseModel):
    date: Optional[str] = None
    rashi: Optional[str] = "all"
    dry_run: bool = False
    background: bool = False
    force: bool = False
    mode: Optional[str] = "carousel"


class SchedulerToggleRequest(BaseModel):
    enable: bool


@router.get("/status", summary="Check Facebook Integration and Scheduler Status")
async def get_facebook_status():
    """Returns Facebook, Instagram & Telegram configuration status and daily scheduler state."""
    cred_status = await verify_facebook_credentials()
    ig_status = await verify_instagram_credentials()
    tg_status = await verify_telegram_credentials()
    scheduler_status = get_scheduler_status()
    return {
        "credentials": cred_status,
        "instagram": ig_status,
        "telegram": tg_status,
        "scheduler": scheduler_status,
    }


@router.get("/posters/{target_date}/{filename}", summary="Serve public poster image for Instagram and Facebook crawlers")
async def get_poster_image(target_date: str, filename: str):
    """Serves the generated 1:1 square poster image file for Meta's Instagram crawler."""
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "generated_posters",
        target_date,
    )
    file_path = os.path.join(data_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Poster image {filename} not found for date {target_date}",
        )
    return FileResponse(file_path, media_type="image/png")


@router.get("/preview", summary="Preview KP Daily Raasi Palan Facebook Post")
async def preview_post(
    target_date: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD (defaults to today in IST)"),
    rashi: str = Query("all", description="Rashi name (e.g. all, Aries, Taurus)"),
    mode: Optional[str] = Query("carousel", description="Post mode (carousel or text)"),
):
    """Generates the formatted Tamil post cards or text preview without publishing to Facebook."""
    try:
        return await generate_and_post_daily_raasi_palan(
            target_date=target_date,
            rashi=rashi,
            dry_run=True,
            post_mode=mode or "carousel",
        )
    except Exception as exc:
        logger.exception(f"Error previewing Facebook post: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview generation failed: {str(exc)}",
        )


@router.post("/publish", summary="Publish KP Daily Raasi Palan to Facebook")
async def publish_to_facebook(payload: PublishRequest):
    """Publishes today's (or requested date's) KP Daily Raasi Palan to Facebook Page."""
    target_rashi = (payload.rashi or "Aries").strip()
    try:
        if payload.background and not payload.dry_run:
            if not settings.fb_page_id or not settings.fb_page_access_token:
                raise ValueError("FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN is not configured.")
            queued = trigger_background_publish(
                execution_date=payload.date,
                rashi=target_rashi,
                force=payload.force,
            )
            return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=queued)

        if not payload.dry_run and target_rashi.lower() == "all":
            return await run_and_record_daily_publish(
                execution_date=payload.date,
                rashi=target_rashi,
                force=payload.force,
            )

        skip_dup = False if payload.force else (True if target_rashi.lower() == "all" else False)
        return await generate_and_post_daily_raasi_palan(
            target_date=payload.date,
            rashi=target_rashi,
            dry_run=payload.dry_run,
            skip_if_already_posted=skip_dup,
            post_mode="text",
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as exc:
        logger.exception(f"Error publishing to Facebook: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Facebook publication failed: {str(exc)}",
        )


@router.get("/trigger", summary="Cron Webhook to Trigger Daily Raasi Palan")
async def trigger_cron_publish(
    force: bool = False,
    mode: Optional[str] = "carousel",
):
    """Lightweight GET webhook for external cron providers (e.g. cron-job.org) to wake Render and trigger daily Raasi Palan."""
    queued = trigger_background_publish(
        rashi="all",
        force=force,
        post_mode=mode or "carousel",
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=queued)


@router.post("/scheduler/toggle", summary="Enable or Disable Daily Facebook Auto-Poster")
async def toggle_scheduler(payload: SchedulerToggleRequest):
    """Enables or disables the background daily post scheduler."""
    if payload.enable:
        start_facebook_scheduler()
    else:
        stop_facebook_scheduler()
    return get_scheduler_status()


@router.post("/telegram/test", summary="Send a test notification to Admin Telegram")
async def test_telegram_notification():
    """Sends a quick test message to verify Telegram bot token and chat ID."""
    cred = await verify_telegram_credentials()
    if not cred.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram credentials invalid: {cred.get('error')}",
        )
    test_msg = (
        "🔮 <b>Gokul's Astrological Insights - Telegram Alert Test</b>\n\n"
        "✅ Your Telegram Bot integration is working properly!\n"
        "Every morning, daily Raasi Palan posters will be delivered here for 1-click sharing to WhatsApp."
    )
    result = await send_telegram_text(test_msg)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deliver message: {result.get('error')}",
        )
    return {"success": True, "message": "Test message sent to Telegram successfully!", "bot": cred.get("bot_username")}


@router.post("/telegram/send", summary="Manually dispatch today's 12 posters to Telegram")
async def dispatch_posters_to_telegram(
    date: Optional[str] = Query(None, description="Target date in YYYY-MM-DD format (defaults to today)"),
):
    """Generates (or uses cached) 12 posters and sends them as 3 photo albums to Admin Telegram."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope
    from app.services.daily_poster_generator import generate_all_12_posters

    cred = await verify_telegram_credentials()
    if not cred.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram credentials invalid: {cred.get('error')}",
        )

    target_date = date or datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    horoscope_data = compute_kp_daily_horoscope(target_date=target_date, timezone_str="Asia/Kolkata")

    # Generate posters in executor
    import asyncio
    loop = asyncio.get_running_loop()
    posters_meta = await loop.run_in_executor(None, generate_all_12_posters, horoscope_data)
    poster_map = {m[0]: m[3] for m in posters_meta}

    res = await send_daily_posters_to_telegram(horoscope_data=horoscope_data, posters_map=poster_map)
    return res
