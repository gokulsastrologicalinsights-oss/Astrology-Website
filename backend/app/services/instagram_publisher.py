"""Instagram Graph API Publishing Service.

Handles automated and manual publishing of Daily Raasi Palan 1:1 square
carousel posts (3 posts x 4 Rasis) directly to Instagram Professional / Business
accounts via the official Meta Graph API.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.daily_poster_generator import generate_all_12_posters
from app.services.facebook_publisher import format_carousel_caption, format_tamil_date_prefix

logger = logging.getLogger("gai.instagram")

GRAPH_API_BASE = "https://graph.facebook.com"


def _resolve_ig_credentials(
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Tuple[str, str]:
    uid = (ig_user_id or settings.ig_user_id or "").strip()
    token = (access_token or settings.ig_access_token or settings.fb_page_access_token or "").strip()
    if not uid:
        raise ValueError("IG_USER_ID is not configured in settings or environment.")
    if not token:
        raise ValueError("IG_ACCESS_TOKEN (or FB_PAGE_ACCESS_TOKEN) is not configured.")
    return uid, token


def _raise_for_ig_error(resp: httpx.Response, resp_data: Dict[str, Any], uid: str) -> None:
    if resp.status_code == 200 and "error" not in resp_data:
        return
    error_obj = resp_data.get("error", {})
    err_message = error_obj.get("message", f"Instagram API returned HTTP {resp.status_code}")
    err_type = error_obj.get("type", "OAuthException")
    err_code = error_obj.get("code")
    logger.error(f"Failed Instagram API request for user {uid}: [{err_code}] {err_message}")
    raise RuntimeError(f"Instagram Graph API Error ({err_code} - {err_type}): {err_message}")


async def verify_instagram_credentials(
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Tests the configured Instagram Business Account credentials."""
    try:
        uid, token = _resolve_ig_credentials(ig_user_id, access_token)
    except ValueError as val_err:
        return {
            "configured": False,
            "error": str(val_err),
        }

    url = f"{GRAPH_API_BASE}/{settings.fb_graph_api_version}/{uid}"
    params = {
        "fields": "id,username,name,profile_picture_url",
        "access_token": token,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if resp.status_code != 200 or "error" in data:
                err_msg = data.get("error", {}).get("message", "Unknown Instagram API error")
                return {"configured": True, "valid": False, "error": err_msg}
            return {
                "configured": True,
                "valid": True,
                "ig_user_id": data.get("id"),
                "username": data.get("username"),
                "name": data.get("name"),
            }
    except Exception as exc:
        logger.exception(f"Error checking Instagram credentials: {exc}")
        return {"configured": True, "valid": False, "error": str(exc)}


def build_public_poster_url(target_date: str, image_filename: str) -> str:
    """Constructs the public internet URL where Meta's crawler can fetch the poster image."""
    base = settings.public_backend_url.rstrip("/")
    return f"{base}/api/v1/social/facebook/posters/{target_date}/{image_filename}"


def get_or_upload_public_poster_url(target_date: str, local_image_path: str) -> str:
    """Uploads the poster to Supabase Storage ('daily-posters') to provide an instant high-speed public CDN URL, or falls back to public_backend_url."""
    filename = os.path.basename(local_image_path)
    try:
        from app.services.auth_service import get_supabase_client
        sb = get_supabase_client()
        if sb and os.path.isfile(local_image_path):
            storage_path = f"{target_date}/{filename}"
            with open(local_image_path, "rb") as f:
                data = f.read()
            sb.storage.from_("daily-posters").upload(
                storage_path,
                data,
                file_options={"content-type": "image/png", "upsert": "true"}
            )
            public_url = sb.storage.from_("daily-posters").get_public_url(storage_path)
            if public_url:
                logger.info(f"Uploaded {filename} to Supabase CDN: {public_url}")
                return str(public_url)
    except Exception as exc:
        logger.warning(f"Failed to upload poster {filename} to Supabase storage: {exc}")

    return build_public_poster_url(target_date, filename)


async def create_ig_carousel_item(
    image_url: str,
    ig_user_id: str,
    access_token: str,
    client: httpx.AsyncClient,
) -> str:
    """Creates a single item container for an Instagram carousel."""
    url = f"{GRAPH_API_BASE}/{settings.fb_graph_api_version}/{ig_user_id}/media"
    payload = {
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": access_token,
    }
    resp = await client.post(url, data=payload)
    resp_data = resp.json()
    _raise_for_ig_error(resp, resp_data, ig_user_id)
    container_id = resp_data.get("id")
    if not container_id:
        raise RuntimeError("No container ID returned for Instagram carousel item.")
    return str(container_id)


async def post_instagram_carousel(
    image_urls: Sequence[str],
    caption: str,
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Uploads multiple images via public URLs and publishes an Instagram carousel feed post."""
    uid, token = _resolve_credentials(ig_user_id, access_token)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Create individual item containers
        item_ids = []
        for img_url in image_urls:
            item_id = await create_ig_carousel_item(img_url, uid, token, client)
            item_ids.append(item_id)

        # Step 2: Create parent carousel container
        container_url = f"{GRAPH_API_BASE}/{settings.fb_graph_api_version}/{uid}/media"
        children_str = ",".join(item_ids)
        container_payload = {
            "media_type": "CAROUSEL",
            "children": children_str,
            "caption": caption,
            "access_token": token,
        }
        resp = await client.post(container_url, data=container_payload)
        resp_data = resp.json()
        _raise_for_ig_error(resp, resp_data, uid)
        carousel_container_id = resp_data.get("id")
        if not carousel_container_id:
            raise RuntimeError("No container ID returned for Instagram carousel parent.")

        # Allow Meta a brief buffer to process the media containers
        await asyncio.sleep(2.0)

        # Step 3: Publish the carousel container
        publish_url = f"{GRAPH_API_BASE}/{settings.fb_graph_api_version}/{uid}/media_publish"
        pub_payload = {
            "creation_id": carousel_container_id,
            "access_token": token,
        }
        pub_resp = await client.post(publish_url, data=pub_payload)
        pub_data = pub_resp.json()
        _raise_for_ig_error(pub_resp, pub_data, uid)
        post_id = pub_data.get("id")

        logger.info(f"Successfully published carousel to Instagram account {uid}. Post ID: {post_id}")
        return {
            "success": True,
            "platform": "instagram",
            "post_id": post_id,
            "ig_user_id": uid,
            "photo_count": len(image_urls),
            "ig_url": f"https://www.instagram.com/p/{post_id}" if post_id else None,
        }


def _resolve_credentials(
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Tuple[str, str]:
    return _resolve_ig_credentials(ig_user_id, access_token)


async def fetch_posted_instagram_parts_for_date(
    target_date: str,
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 30,
) -> Dict[int, Dict[str, Any]]:
    """Checks the Instagram account media feed for carousel parts (1, 2, 3) already posted for target_date."""
    try:
        uid, token = _resolve_credentials(ig_user_id, access_token)
    except Exception:
        return {}

    date_prefix = format_tamil_date_prefix(target_date)
    url = f"{GRAPH_API_BASE}/{settings.fb_graph_api_version}/{uid}/media"
    params = {
        "fields": "id,caption,media_type,timestamp,permalink",
        "limit": limit,
        "access_token": token,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if resp.status_code != 200 or "error" in data:
                logger.warning(f"Could not read existing Instagram posts for deduplication: {data.get('error')}")
                return {}
    except Exception as exc:
        logger.warning(f"Error reading existing Instagram posts for deduplication: {exc}")
        return {}

    posted_parts: Dict[int, Dict[str, Any]] = {}
    for item in data.get("data", []):
        caption = item.get("caption") or ""
        is_daily_horoscope = ("தினசரி ராசிபலன்" in caption or "ராசிபலன்" in caption or "DailyHoroscope" in caption)
        is_matching_date = (date_prefix in caption or target_date in caption)
        if not (is_daily_horoscope and is_matching_date):
            continue

        part_match = re.search(r"பகுதி\s*(\d+)", caption)
        if part_match:
            part_num = int(part_match.group(1))
            if part_num not in posted_parts:
                posted_parts[part_num] = {
                    "post_id": item.get("id"),
                    "ig_url": item.get("permalink"),
                    "timestamp": item.get("timestamp"),
                }

    return posted_parts


async def post_daily_instagram_carousels(
    horoscope_data: KpDailyHoroscopeResponse,
    target_date: str,
    delay_seconds: float = 15.0,
    dry_run: bool = False,
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
    skip_if_already_posted: bool = True,
    posters_map: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
    """Publishes the 3 carousel posts to Instagram with strict deduplication check."""
    group_size = settings.fb_carousel_group_size or 4
    predictions = horoscope_data.predictions
    groups = [predictions[i : i + group_size] for i in range(0, len(predictions), group_size)]

    posted_parts: Dict[int, Dict[str, Any]] = {}
    if skip_if_already_posted and not dry_run:
        posted_parts = await fetch_posted_instagram_parts_for_date(
            target_date=target_date,
            ig_user_id=ig_user_id,
            access_token=access_token,
        )
        if posted_parts:
            logger.info(
                f"Instagram deduplication check: Found {len(posted_parts)}/{len(groups)} carousel part(s) already posted for {target_date}: {list(posted_parts.keys())}"
            )

    parts_to_publish = [
        idx for idx in range(1, len(groups) + 1)
        if not (skip_if_already_posted and not dry_run and idx in posted_parts)
    ]

    poster_map: Dict[int, str] = posters_map or {}
    if not poster_map and (dry_run or parts_to_publish):
        loop = asyncio.get_running_loop()
        posters_meta = await loop.run_in_executor(None, generate_all_12_posters, horoscope_data)
        poster_map = {m[0]: m[3] for m in posters_meta}

    results: List[Dict[str, Any]] = []
    newly_posted = 0
    skipped_existing = 0

    for idx, group in enumerate(groups, start=1):
        group_names = ", ".join(f"{p.rashi_name_ta} ({p.rashi_name_en})" for p in group)
        caption = format_carousel_caption(horoscope_data, idx, group)

        if dry_run:
            image_urls = [
                get_or_upload_public_poster_url(target_date, poster_map[p.rashi_id])
                for p in group
                if p.rashi_id in poster_map
            ]
            results.append({
                "post_part": idx,
                "platform": "instagram",
                "rashis": group_names,
                "photo_count": len(image_urls),
                "image_urls": image_urls,
                "caption": caption,
                "dry_run": True,
                "success": True,
            })
            continue

        if skip_if_already_posted and idx in posted_parts:
            existing = posted_parts[idx]
            skipped_existing += 1
            logger.info(
                f"Skipping Instagram Carousel Part {idx}/{len(groups)} ({group_names}) - already posted on Instagram (ID: {existing.get('post_id')})."
            )
            results.append({
                "post_part": idx,
                "platform": "instagram",
                "rashis": group_names,
                "success": True,
                "skipped": True,
                "reason": "already_posted_today",
                "post_id": existing.get("post_id"),
                "ig_url": existing.get("ig_url"),
                "photo_count": len(group),
            })
            continue

        image_urls = [
            get_or_upload_public_poster_url(target_date, poster_map[p.rashi_id])
            for p in group
            if p.rashi_id in poster_map
        ]

        try:
            logger.info(f"Publishing Instagram Carousel {idx}/{len(groups)} ({group_names})...")
            post_res = await post_instagram_carousel(
                image_urls=image_urls,
                caption=caption,
                ig_user_id=ig_user_id,
                access_token=access_token,
            )
            newly_posted += 1
            results.append({
                "post_part": idx,
                "platform": "instagram",
                "rashis": group_names,
                "success": True,
                "post_id": post_res.get("post_id"),
                "photo_count": len(image_urls),
            })
        except Exception as exc:
            logger.error(f"Failed to publish Instagram Carousel {idx}/{len(groups)}: {exc}")
            results.append({
                "post_part": idx,
                "platform": "instagram",
                "rashis": group_names,
                "success": False,
                "error": str(exc),
            })

        has_more = any(
            next_idx > idx and next_idx in parts_to_publish
            for next_idx in range(idx + 1, len(groups) + 1)
        )
        if has_more and delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    success_count = sum(1 for r in results if r.get("success"))
    failed_count = len(results) - success_count
    return {
        "success": failed_count == 0 and (success_count > 0 or dry_run),
        "platform": "instagram",
        "dry_run": dry_run,
        "target_date": target_date,
        "total_posts": len(groups),
        "successful_posts": success_count,
        "newly_posted": newly_posted,
        "skipped_existing": skipped_existing,
        "failed_posts": failed_count,
        "results": results,
    }
