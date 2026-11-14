"""Facebook Social Integration API Router.

Endpoints for previewing (Tamil text format), testing, and triggering
KP Daily Raasi Palan publications to a connected Facebook Page.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings
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

logger = logging.getLogger("gai.facebook.router")

router = APIRouter(prefix="/api/v1/social/facebook", tags=["Facebook Social Media"])


class PublishRequest(BaseModel):
    date: Optional[str] = None
    rashi: Optional[str] = "all"
    dry_run: bool = False
    background: bool = False
    force: bool = False
    mode: Optional[str] = "text"


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
    mode: Optional[str] = Query("text", description="Post mode (text)"),
):
    """Generates the formatted Tamil post text without publishing to Facebook."""
    try:
        return await generate_and_post_daily_raasi_palan(
            target_date=target_date,
            rashi=rashi,
            dry_run=True,
            post_mode="text",
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


@router.post("/scheduler/toggle", summary="Enable or Disable Daily Facebook Auto-Poster")
async def toggle_scheduler(payload: SchedulerToggleRequest):
    """Enables or disables the background daily post scheduler."""
    if payload.enable:
        start_facebook_scheduler()
    else:
        stop_facebook_scheduler()
    return get_scheduler_status()
