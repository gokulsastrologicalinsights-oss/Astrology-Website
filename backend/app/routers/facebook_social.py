"""Facebook Social Integration API Router.

Endpoints for previewing (text & PNG image cards), testing, and triggering
KP Daily Raasi Palan publications to a connected Facebook Page.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.services.facebook_card_renderer import (
    render_daily_overview_card_png,
    render_rashi_daily_card_png,
)
from app.services.facebook_publisher import (
    generate_and_post_daily_raasi_palan,
    verify_facebook_credentials,
)
from app.services.facebook_scheduler import (
    get_scheduler_status,
    run_and_record_daily_publish,
    start_facebook_scheduler,
    stop_facebook_scheduler,
    trigger_background_publish,
)
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

logger = logging.getLogger("gai.facebook.router")

router = APIRouter(prefix="/api/v1/social/facebook", tags=["Facebook Social Media"])


class PublishRequest(BaseModel):
    date: Optional[str] = None
    rashi: Optional[str] = "all"
    dry_run: bool = False
    background: bool = False
    force: bool = False
    mode: Optional[str] = None  # "carousel" | "cards" | "image" | "text"


class SchedulerToggleRequest(BaseModel):
    enable: bool


@router.get("/status", summary="Check Facebook Integration and Scheduler Status")
async def get_facebook_status():
    """Returns Facebook configuration status and daily scheduler state."""
    cred_status = await verify_facebook_credentials()
    scheduler_status = get_scheduler_status()
    return {
        "credentials": cred_status,
        "scheduler": scheduler_status,
    }


@router.get("/preview", summary="Preview KP Daily Raasi Palan Facebook Post")
async def preview_post(
    target_date: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD (defaults to today in IST)"),
    rashi: str = Query("Aries", description="Rashi name (e.g. Aries, Mesha, Taurus, or all)"),
    mode: Optional[str] = Query(None, description="carousel | cards | image | text"),
):
    """Generates the formatted Tamil post text without publishing to Facebook."""
    try:
        extra_kwargs = {"post_mode": mode} if mode else {}
        return await generate_and_post_daily_raasi_palan(
            target_date=target_date,
            rashi=rashi,
            dry_run=True,
            **extra_kwargs,
        )
    except Exception as exc:
        logger.exception(f"Error previewing Facebook post: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview generation failed: {str(exc)}",
        )


@router.get("/preview-card", summary="Preview Branded Tamil Raasi Palan PNG Card")
async def preview_card_image(
    target_date: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD (defaults to today in IST)"),
    rashi: str = Query("Aries", description="Rashi name (e.g. Aries, Mesha) or 'overview'"),
):
    """Renders and returns the 1080x1350 branded Tamil PNG card directly."""
    try:
        resolved_date = target_date or datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
        req_rashi = (rashi or "Aries").strip()
        if req_rashi.lower() in ("overview", "all", "summary"):
            horoscope_data = await asyncio.to_thread(
                compute_kp_daily_horoscope,
                target_date=resolved_date,
                timezone_str="Asia/Kolkata",
                rashi_filter="all",
            )
            png_bytes = await asyncio.to_thread(render_daily_overview_card_png, horoscope_data)
            filename = f"raasi_palan_overview_{resolved_date}.png"
        else:
            horoscope_data = await asyncio.to_thread(
                compute_kp_daily_horoscope,
                target_date=resolved_date,
                timezone_str="Asia/Kolkata",
                rashi_filter=req_rashi,
            )
            if not horoscope_data.predictions:
                raise ValueError(f"Unknown Rashi: {req_rashi}")
            prediction = horoscope_data.predictions[0]
            png_bytes = await asyncio.to_thread(
                render_rashi_daily_card_png,
                horoscope_data,
                prediction,
                slide_index=prediction.rashi_id,
                total_slides=12,
            )
            filename = f"raasi_palan_{prediction.rashi_name_en.lower()}_{resolved_date}.png"

        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Cache-Control": "public, max-age=300",
            },
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.exception(f"Error rendering Facebook preview card: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Card rendering failed: {str(exc)}",
        )


@router.post("/publish", summary="Publish KP Daily Raasi Palan to Facebook")
async def publish_to_facebook(payload: PublishRequest):
    """Publishes today's (or requested date's) KP Daily Raasi Palan to Facebook Page."""
    target_rashi = (payload.rashi or "Aries").strip()
    mode_kwargs = {"post_mode": payload.mode} if payload.mode else {}
    try:
        if payload.background and not payload.dry_run:
            if not settings.fb_page_id or not settings.fb_page_access_token:
                raise ValueError("FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN is not configured.")
            queued = trigger_background_publish(
                execution_date=payload.date,
                rashi=target_rashi,
                force=payload.force,
                **mode_kwargs,
            )
            return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=queued)

        if not payload.dry_run and target_rashi.lower() == "all":
            return await run_and_record_daily_publish(
                execution_date=payload.date,
                rashi=target_rashi,
                force=payload.force,
                **mode_kwargs,
            )

        skip_dup = False if payload.force else (True if target_rashi.lower() == "all" else False)
        return await generate_and_post_daily_raasi_palan(
            target_date=payload.date,
            rashi=target_rashi,
            dry_run=payload.dry_run,
            skip_if_already_posted=skip_dup,
            **mode_kwargs,
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


@router.post("/scheduler/toggle", summary="Enable or Disable Daily Facebook Auto-Poster")
async def toggle_scheduler(payload: SchedulerToggleRequest):
    """Enables or disables the background daily post scheduler."""
    if payload.enable:
        start_facebook_scheduler()
    else:
        stop_facebook_scheduler()
    return get_scheduler_status()
