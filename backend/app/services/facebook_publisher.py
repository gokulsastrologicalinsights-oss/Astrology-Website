"""Facebook Social Media Publishing Service.

Handles automated and manual posting of KP Daily Raasi Palan updates
for all 12 Rashis to Facebook Pages using the Meta Graph API.
Supports branded Tamil infographic image cards, multi-photo carousel albums,
and plain-text fallback posts.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import json
import logging
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple
import weakref
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.facebook_card_renderer import (
    MONTHS_TA,
    SENTIMENT_MAP_TA,
    clean_brief_ta,
    format_aspect_text_ta,
    format_tamil_date,
    format_tamil_date_prefix,
    render_daily_overview_card_png,
    render_rashi_daily_card_png,
)
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

logger = logging.getLogger("gai.facebook")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

_LOOP_PUBLISH_LOCKS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
    weakref.WeakKeyDictionary()
)


def _get_publish_lock() -> asyncio.Lock:
    """Returns an asyncio.Lock bound to the currently running event loop."""
    loop = asyncio.get_running_loop()
    lock = _LOOP_PUBLISH_LOCKS.get(loop)
    if lock is None:
        lock = asyncio.Lock()
        _LOOP_PUBLISH_LOCKS[loop] = lock
    return lock


FACEBOOK_API_BASE = "https://graph.facebook.com"
OVERVIEW_MARKER = "12 ராசிகள் சுருக்கம்"

RASHI_SYMBOLS: Dict[int, str] = {
    1: "♈",
    2: "♉",
    3: "♊",
    4: "♋",
    5: "♌",
    6: "♍",
    7: "♎",
    8: "♏",
    9: "♐",
    10: "♑",
    11: "♒",
    12: "♓",
}

ASPECT_ICONS: Dict[str, str] = {
    "career": "💼",
    "finance": "💰",
    "love": "❤️",
    "health": "🩺",
    "travel": "✈️",
}

_RASHI_HEADER_RE = re.compile(r"\(([A-Za-z]+)\)\s*-\s*⭐")

# Aliases preserved for internal/external callers expecting the earlier helper names
_format_tamil_date_prefix = format_tamil_date_prefix
_format_tamil_date = format_tamil_date
_clean_brief = clean_brief_ta
_format_aspect_text_ta = format_aspect_text_ta


def _resolve_credentials(
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Tuple[str, str]:
    pid = (page_id or settings.fb_page_id or "").strip()
    token = (access_token or settings.fb_page_access_token or "").strip()
    if not pid:
        raise ValueError("FB_PAGE_ID is not configured in settings or environment.")
    if not token:
        raise ValueError("FB_PAGE_ACCESS_TOKEN is not configured in settings or environment.")
    return pid, token


def _raise_for_graph_error(resp: httpx.Response, resp_data: Dict[str, Any], pid: str) -> None:
    if resp.status_code == 200 and "error" not in resp_data:
        return
    error_obj = resp_data.get("error", {})
    err_message = error_obj.get("message", f"Facebook API returned HTTP {resp.status_code}")
    err_type = error_obj.get("type", "OAuthException")
    err_code = error_obj.get("code")
    logger.error(f"Failed to post to Facebook Page {pid}: [{err_code}] {err_message}")
    raise RuntimeError(f"Facebook Graph API Error ({err_code} - {err_type}): {err_message}")


def _resolve_post_mode(requested_mode: Optional[str], is_batch: bool) -> str:
    """Resolves requested/configured mode into 'carousel' | 'cards' | 'image' | 'text'."""
    raw = (requested_mode or settings.fb_post_mode or "carousel").strip().lower()
    if raw == "text":
        return "text"
    if not is_batch:
        return "image"
    if raw in ("cards", "image"):
        return "cards"
    return "carousel"


def format_kp_daily_tamil_post(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
) -> str:
    """Formats the KP Daily Horoscope for a given Rashi into the exact Tamil post text matching the website."""
    r_name_ta = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"
    symbol = RASHI_SYMBOLS.get(prediction.rashi_id, "✨")
    formatted_date = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)

    golden_times = (
        ", ".join(
            f"{w.start_time} – {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "golden"
        )
        or (prediction.golden_hour_window.replace(" - ", " – ") if prediction.golden_hour_window else "")
        or "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"
    )

    caution_times = (
        ", ".join(
            f"{w.start_time} – {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "caution"
        )
        or (prediction.caution_hour_window.replace(" - ", " – ") if prediction.caution_hour_window else "")
        or "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"
    )

    aspects_ta = "\n\n".join(
        f"{ASPECT_ICONS.get(a.aspect_code, '•')} {a.aspect_name_tamil} – {a.score}%\n"
        f"{format_aspect_text_ta(a.insight_ta, a.key_recommendation_ta)}"
        for a in prediction.aspects
    )

    stars_display = int(round(prediction.daily_rating_stars)) if prediction.daily_rating_stars else 2
    sentiment_ta = SENTIMENT_MAP_TA.get(prediction.day_sentiment, prediction.day_sentiment)
    lucky_color = prediction.lucky_color_ta.split("&")[0].strip() if prediction.lucky_color_ta else ""

    return (
        f"தினசரி ராசிபலன்\n"
        f"📅 தேதி: {formatted_date}\n\n"
        f"{symbol} {r_name_ta} - ⭐ இன்றைய சாதக நிலை: {prediction.daily_score}% ({stars_display}/5 – {sentiment_ta})\n\n"
        f"🔮 இன்றைய பொதுப்பலன்:\n\n"
        f"{clean_brief_ta(prediction.brief_statement_ta)}\n\n"
        f"📊 இன்றைய விரிவான பலன்கள்:\n\n"
        f"{aspects_ta}\n\n"
        f"⏰ இன்றைய நேர வழிகாட்டல்:\n\n"
        f"🌟 அதிர்ஷ்ட நேரம்: {golden_times}\n\n"
        f"⚠️ கவனமான நேரம்: {caution_times}\n\n"
        f"🎨 அதிர்ஷ்ட நிறம்: {lucky_color}\n\n"
        f"🔢 அதிர்ஷ்ட எண்: {prediction.lucky_number}\n\n"
        f"🧭 அதிர்ஷ்ட திசை: {prediction.lucky_direction_ta}\n\n"
        f"🛡️ இன்றைய ஆலோசனை:\n\n"
        f"{prediction.daily_remedy_ta}\n\n"
        f"🙏 Gokul's Astrological Insights\n"
        f"Gokul Murugan | Thiruverkadu"
    )


def format_kp_daily_overview_post(horoscope_data: KpDailyHoroscopeResponse) -> str:
    """Formats the caption for the Top-3 & 12-Rashi Overview Hero Card."""
    formatted_date = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    ranked = sorted(horoscope_data.predictions, key=lambda p: (-p.daily_score, p.rashi_id))
    top_lines = "\n".join(
        f"{idx}. {RASHI_SYMBOLS.get(p.rashi_id, '✨')} {p.rashi_name_ta} — {p.daily_score}% ({SENTIMENT_MAP_TA.get(p.day_sentiment, p.day_sentiment)})"
        for idx, p in enumerate(ranked[:3], start=1)
    )
    all_lines = "\n".join(
        f"{RASHI_SYMBOLS.get(p.rashi_id, '•')} {p.rashi_name_ta}: {p.daily_score}% | எண்: {p.lucky_number} | நேரம்: {(p.golden_hour_window or '-').replace(' - ', ' – ')}"
        for p in horoscope_data.predictions
    )
    return (
        f"தினசரி ராசிபலன் – {OVERVIEW_MARKER}\n"
        f"📅 தேதி: {formatted_date}\n\n"
        f"🏆 இன்றைய அதிர்ஷ்ட ராசிகள் (Top 3):\n"
        f"{top_lines}\n\n"
        f"📊 12 ராசிகள் சுருக்கப் பலன்:\n"
        f"{all_lines}\n\n"
        f"👇 உங்கள் ராசியின் விரிவான படத்தைப் பார்க்க அடுத்த பதிவுகளைப் பார்வையிடுங்கள்!\n\n"
        f"🙏 Gokul's Astrological Insights\n"
        f"Gokul Murugan | Thiruverkadu"
    )


def format_kp_daily_carousel_group_post(
    horoscope_data: KpDailyHoroscopeResponse,
    predictions: Sequence[RashiDailyPrediction],
    group_index: int,
    total_groups: int,
) -> str:
    """Formats a 4-Rashi carousel post message containing deduplication headers for every slide."""
    formatted_date = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    first_ta = predictions[0].rashi_name_ta
    last_ta = predictions[-1].rashi_name_ta

    blocks: List[str] = []
    for p in predictions:
        symbol = RASHI_SYMBOLS.get(p.rashi_id, "✨")
        stars_display = int(round(p.daily_rating_stars)) if p.daily_rating_stars else 2
        sentiment_ta = SENTIMENT_MAP_TA.get(p.day_sentiment, p.day_sentiment)
        gh = (p.golden_hour_window or "").replace(" - ", " – ") or "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"
        blocks.append(
            f"{symbol} {p.rashi_name_ta} ({p.rashi_name_en}) - ⭐ {p.daily_score}% ({stars_display}/5 – {sentiment_ta})\n"
            f"🔮 {clean_brief_ta(p.brief_statement_ta)}\n"
            f"🌟 அதிர்ஷ்ட நேரம்: {gh} | 🔢 எண்: {p.lucky_number}"
        )

    joined_blocks = "\n\n".join(blocks)
    return (
        f"தினசரி ராசிபலன் ({first_ta} – {last_ta}) [{group_index}/{total_groups}]\n"
        f"📅 தேதி: {formatted_date}\n\n"
        f"{joined_blocks}\n\n"
        f"👆 ஒவ்வொரு ராசியின் முழு 5-துறை பலன், கவனமான நேரம் & பரிகாரத்தைத் தனித்தனி படத்தில் கிளிக் செய்து பார்க்கலாம்!\n\n"
        f"🙏 Gokul's Astrological Insights\n"
        f"Gokul Murugan | Thiruverkadu"
    )


async def verify_facebook_credentials() -> Dict[str, Any]:
    """Tests the configured Facebook Page credentials and returns page profile info."""
    page_id = settings.fb_page_id
    access_token = settings.fb_page_access_token

    if not page_id or not access_token:
        return {
            "configured": False,
            "error": "Facebook Page ID or Page Access Token is not set in environment.",
        }

    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{page_id}"
    params = {
        "fields": "id,name,link",
        "access_token": access_token,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if resp.status_code != 200 or "error" in data:
                err_msg = data.get("error", {}).get("message", "Unknown Facebook API error")
                logger.error(f"Facebook credential verification failed: {err_msg}")
                return {"configured": True, "valid": False, "error": err_msg}
            return {
                "configured": True,
                "valid": True,
                "page_id": data.get("id"),
                "page_name": data.get("name"),
                "page_link": data.get("link"),
            }
    except Exception as exc:
        logger.exception(f"Error checking Facebook page credentials: {exc}")
        return {"configured": True, "valid": False, "error": str(exc)}


async def post_to_facebook(
    message: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Posts a plain-text message directly to the Facebook Page feed."""
    pid, token = _resolve_credentials(page_id, access_token)
    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/feed"
    payload = {
        "message": message,
        "access_token": token,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, data=payload)
        resp_data = resp.json()
        _raise_for_graph_error(resp, resp_data, pid)

        post_id = resp_data.get("id")
        logger.info(f"Successfully posted text to Facebook Page {pid}. Post ID: {post_id}")
        return {
            "success": True,
            "post_id": post_id,
            "page_id": pid,
            "post_type": "text",
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


async def post_photo_to_facebook(
    image_bytes: bytes,
    caption: str,
    filename: str = "raasi_palan_card.png",
    published: bool = True,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Uploads a PNG card directly from memory to /{page_id}/photos."""
    pid, token = _resolve_credentials(page_id, access_token)
    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/photos"
    data = {
        "caption": caption,
        "published": "true" if published else "false",
        "access_token": token,
    }
    files = {"source": (filename, image_bytes, "image/png")}

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, data=data, files=files)
        resp_data = resp.json()
        _raise_for_graph_error(resp, resp_data, pid)

        photo_id = resp_data.get("id")
        post_id = resp_data.get("post_id") or photo_id
        logger.info(
            f"Uploaded photo to Facebook Page {pid} (published={published}). photo_id={photo_id}, post_id={post_id}"
        )
        return {
            "success": True,
            "photo_id": photo_id,
            "post_id": post_id,
            "page_id": pid,
            "post_type": "photo",
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


async def post_carousel_to_facebook(
    photos: Sequence[Tuple[bytes, str, str]],
    message: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Uploads multiple unpublished PNG cards and attaches them to a single Page feed post."""
    if not photos:
        raise ValueError("At least one photo is required to publish a Facebook carousel.")

    pid, token = _resolve_credentials(page_id, access_token)
    if len(photos) == 1:
        img_bytes, fname, _ = photos[0]
        return await post_photo_to_facebook(
            image_bytes=img_bytes,
            caption=message,
            filename=fname,
            published=True,
            page_id=pid,
            access_token=token,
        )

    media_fbids: List[str] = []
    for img_bytes, fname, photo_caption in photos:
        upload_res = await post_photo_to_facebook(
            image_bytes=img_bytes,
            caption=photo_caption,
            filename=fname,
            published=False,
            page_id=pid,
            access_token=token,
        )
        fbid = upload_res.get("photo_id") or upload_res.get("post_id")
        if not fbid:
            raise RuntimeError(f"Facebook photo upload returned no media ID for {fname}")
        media_fbids.append(str(fbid))

    feed_url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/feed"
    feed_payload: Dict[str, Any] = {
        "message": message,
        "published": "true",
        "access_token": token,
    }
    for idx, fbid in enumerate(media_fbids):
        feed_payload[f"attached_media[{idx}]"] = json.dumps({"media_fbid": fbid})

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(feed_url, data=feed_payload)
        resp_data = resp.json()
        _raise_for_graph_error(resp, resp_data, pid)

        post_id = resp_data.get("id")
        logger.info(
            f"Successfully published {len(media_fbids)}-card carousel to Facebook Page {pid}. Post ID: {post_id}"
        )
        return {
            "success": True,
            "post_id": post_id,
            "page_id": pid,
            "post_type": "carousel",
            "media_fbids": media_fbids,
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


async def _fetch_feed_state_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Tuple[Dict[str, Dict[str, Any]], bool]:
    """Reads recent Page posts and returns (posted_rashis_map, overview_posted_today)."""
    pid = (page_id or settings.fb_page_id or "").strip()
    token = (access_token or settings.fb_page_access_token or "").strip()
    if not pid or not token:
        return {}, False

    date_marker = f"📅 தேதி: {format_tamil_date_prefix(target_date)}"
    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/posts"
    params = {
        "fields": "id,created_time,message,permalink_url",
        "limit": limit,
        "access_token": token,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if resp.status_code != 200 or "error" in data:
                err_msg = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
                logger.warning(f"Could not read existing Facebook Page posts for deduplication: {err_msg}")
                return {}, False
    except Exception as exc:
        logger.warning(f"Error reading existing Facebook Page posts for deduplication: {exc}")
        return {}, False

    posted: Dict[str, Dict[str, Any]] = {}
    overview_posted = False

    for item in data.get("data", []):
        msg = item.get("message") or ""
        if "தினசரி ராசிபலன்" not in msg or date_marker not in msg:
            continue
        if OVERVIEW_MARKER in msg:
            overview_posted = True
        post_id = item.get("id")
        fb_url = item.get("permalink_url") or (f"https://www.facebook.com/{post_id}" if post_id else None)
        for match in _RASHI_HEADER_RE.finditer(msg):
            rashi_key = match.group(1).strip().lower()
            if rashi_key not in posted:
                posted[rashi_key] = {
                    "post_id": post_id,
                    "fb_url": fb_url,
                    "created_time": item.get("created_time"),
                }

    return posted, overview_posted


async def fetch_posted_rashis_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Dict[str, Dict[str, Any]]:
    """Checks the Facebook Page feed for Rashis already posted for target_date (YYYY-MM-DD)."""
    posted, _ = await _fetch_feed_state_for_date(
        target_date=target_date,
        page_id=page_id,
        access_token=access_token,
        limit=limit,
    )
    return posted


async def generate_and_post_daily_raasi_palan(
    target_date: Optional[str] = None,
    rashi: Optional[str] = None,
    dry_run: bool = False,
    skip_if_already_posted: Optional[bool] = None,
    post_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates today's KP Daily Raasi Palan in Tamil and posts it (image card/carousel or text) to Facebook."""
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    target_rashi = (rashi or settings.fb_post_rashi or "all").strip()

    if target_rashi.lower() == "all":
        skip_dup = True if skip_if_already_posted is None else skip_if_already_posted
        return await post_all_12_raasi_palans(
            target_date=target_date,
            delay_seconds=settings.fb_post_delay_seconds,
            dry_run=dry_run,
            skip_if_already_posted=skip_dup,
            post_mode=post_mode,
        )

    effective_mode = _resolve_post_mode(post_mode, is_batch=False)
    horoscope_data = compute_kp_daily_horoscope(
        target_date=target_date,
        timezone_str="Asia/Kolkata",
        rashi_filter=target_rashi,
    )

    if not horoscope_data.predictions:
        raise ValueError(f"No prediction generated for Rashi: {target_rashi} on {target_date}")

    prediction = horoscope_data.predictions[0]
    post_text = format_kp_daily_tamil_post(horoscope_data, prediction)
    rashi_label = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "rashi": rashi_label,
            "post_mode": effective_mode,
            "has_image": effective_mode != "text",
            "message": post_text,
        }

    skip_dup = False if skip_if_already_posted is None else skip_if_already_posted
    async with _get_publish_lock():
        if skip_dup:
            already_posted = await fetch_posted_rashis_for_date(target_date)
            existing = already_posted.get(prediction.rashi_name_en.lower())
            if existing:
                logger.info(f"Skipping {rashi_label} for {target_date}; already posted ({existing.get('post_id')}).")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "already_posted_today",
                    "post_id": existing.get("post_id"),
                    "fb_url": existing.get("fb_url"),
                    "target_date": target_date,
                    "rashi": rashi_label,
                }

        if effective_mode == "text":
            post_result = await post_to_facebook(post_text)
        else:
            card_bytes = await asyncio.to_thread(
                render_rashi_daily_card_png,
                horoscope_data,
                prediction,
            )
            post_result = await post_photo_to_facebook(
                image_bytes=card_bytes,
                caption=post_text,
                filename=f"raasi_palan_{prediction.rashi_name_en.lower()}_{target_date}.png",
            )

        post_result.update({
            "target_date": target_date,
            "rashi": rashi_label,
            "post_mode": effective_mode,
            "posted_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "preview_text": post_text[:200] + "...",
        })
        return post_result


def _skipped_result(prediction: RashiDailyPrediction, existing: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rashi_id": prediction.rashi_id,
        "rashi": f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})",
        "success": True,
        "skipped": True,
        "reason": "already_posted_today",
        "post_id": existing.get("post_id"),
        "fb_url": existing.get("fb_url"),
    }


def _build_batch_summary(
    target_date: str,
    post_mode: str,
    results: List[Dict[str, Any]],
    newly_posted: int,
    skipped_existing: int,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = len(results) - success_count
    summary: Dict[str, Any] = {
        "success": failed_count == 0 and success_count > 0,
        "target_date": target_date,
        "post_mode": post_mode,
        "total_attempted": len(results),
        "successful_posts": success_count,
        "newly_posted": newly_posted,
        "skipped_existing": skipped_existing,
        "failed_posts": failed_count,
        "results": results,
    }
    if extra:
        summary.update(extra)
    return summary


async def _post_all_12_sequential_unlocked(
    horoscope_data: KpDailyHoroscopeResponse,
    target_date: str,
    delay_seconds: float,
    skip_if_already_posted: bool,
    effective_mode: str,
) -> Dict[str, Any]:
    """Posts 12 individual Rashi updates (either PNG photo cards or legacy plain text)."""
    already_posted = (
        await fetch_posted_rashis_for_date(target_date)
        if skip_if_already_posted
        else {}
    )
    if already_posted:
        logger.info(
            f"Found {len(already_posted)} Rashi(s) already posted on Facebook for {target_date}; they will be skipped."
        )

    results: List[Dict[str, Any]] = []
    newly_posted = 0
    skipped_existing = 0

    for index, prediction in enumerate(horoscope_data.predictions):
        post_text = format_kp_daily_tamil_post(horoscope_data, prediction)
        rashi_label = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"
        existing = already_posted.get(prediction.rashi_name_en.lower())

        if existing:
            skipped_existing += 1
            logger.info(f"Skipping {index + 1}/12: {rashi_label} (already posted today: {existing.get('post_id')}).")
            results.append(_skipped_result(prediction, existing))
            continue

        try:
            logger.info(f"Posting {index + 1}/12 ({effective_mode}): {rashi_label} to Facebook...")
            if effective_mode == "text":
                post_res = await post_to_facebook(post_text)
            else:
                card_bytes = await asyncio.to_thread(
                    render_rashi_daily_card_png,
                    horoscope_data,
                    prediction,
                    slide_index=index + 1,
                    total_slides=len(horoscope_data.predictions),
                )
                post_res = await post_photo_to_facebook(
                    image_bytes=card_bytes,
                    caption=post_text,
                    filename=f"raasi_palan_{prediction.rashi_name_en.lower()}_{target_date}.png",
                )
            newly_posted += 1
            results.append({
                "rashi_id": prediction.rashi_id,
                "rashi": rashi_label,
                "success": True,
                "skipped": False,
                "post_id": post_res.get("post_id"),
                "fb_url": post_res.get("fb_url"),
            })
        except Exception as exc:
            logger.error(f"Failed to post {rashi_label} to Facebook: {exc}")
            results.append({
                "rashi_id": prediction.rashi_id,
                "rashi": rashi_label,
                "success": False,
                "error": str(exc),
            })

        has_more_to_post = any(
            p.rashi_name_en.lower() not in already_posted
            for p in horoscope_data.predictions[index + 1:]
        )
        if has_more_to_post and delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    return _build_batch_summary(target_date, effective_mode, results, newly_posted, skipped_existing)


async def _post_all_12_carousel_unlocked(
    horoscope_data: KpDailyHoroscopeResponse,
    target_date: str,
    delay_seconds: float,
    skip_if_already_posted: bool,
) -> Dict[str, Any]:
    """Publishes 1 Daily Overview Hero Card + grouped 4-card Tamil carousels (<=10 photos/post)."""
    already_posted = (
        await fetch_posted_rashis_for_date(target_date)
        if skip_if_already_posted
        else {}
    )
    overview_posted = bool(already_posted)
    if skip_if_already_posted and not already_posted:
        _, overview_posted = await _fetch_feed_state_for_date(target_date)

    if already_posted:
        logger.info(
            f"Found {len(already_posted)} Rashi(s) already posted on Facebook for {target_date}; skipping completed entries."
        )

    predictions = list(horoscope_data.predictions)
    group_size = max(1, min(10, settings.fb_carousel_group_size))
    groups = [predictions[i:i + group_size] for i in range(0, len(predictions), group_size)]

    results: List[Dict[str, Any]] = []
    carousel_posts: List[Dict[str, Any]] = []
    newly_posted = 0
    skipped_existing = 0
    overview_result: Optional[Dict[str, Any]] = None

    # 1. Overview Hero Card (posted first if missing and not all 12 Rashis are already posted)
    all_rashis_done = all(p.rashi_name_en.lower() in already_posted for p in predictions)
    if not overview_posted and not all_rashis_done:
        try:
            logger.info(f"Publishing Daily Overview Hero Card for {target_date}...")
            overview_png = await asyncio.to_thread(render_daily_overview_card_png, horoscope_data)
            overview_caption = format_kp_daily_overview_post(horoscope_data)
            ov_res = await post_photo_to_facebook(
                image_bytes=overview_png,
                caption=overview_caption,
                filename=f"raasi_palan_overview_{target_date}.png",
            )
            overview_result = {
                "success": True,
                "post_id": ov_res.get("post_id"),
                "fb_url": ov_res.get("fb_url"),
            }
            if delay_seconds > 0:
                await asyncio.sleep(min(delay_seconds, 10.0))
        except Exception as ov_exc:
            logger.warning(f"Daily Overview Hero Card upload failed (continuing with Rashis): {ov_exc}")
            overview_result = {"success": False, "error": str(ov_exc)}

    # 2. Grouped Carousel Posts (default: 3 posts x 4 Rashi cards each)
    total_groups = len(groups)
    for g_idx, group in enumerate(groups, start=1):
        missing_in_group: List[RashiDailyPrediction] = []
        for p in group:
            existing = already_posted.get(p.rashi_name_en.lower())
            if existing:
                skipped_existing += 1
                results.append(_skipped_result(p, existing))
            else:
                missing_in_group.append(p)

        if not missing_in_group:
            logger.info(f"Skipping Carousel Group {g_idx}/{total_groups}; all {len(group)} Rashis already posted.")
            continue

        try:
            photo_payloads: List[Tuple[bytes, str, str]] = []
            for p in missing_in_group:
                png_bytes = await asyncio.to_thread(
                    render_rashi_daily_card_png,
                    horoscope_data,
                    p,
                    slide_index=p.rashi_id,
                    total_slides=len(predictions),
                )
                rashi_caption = format_kp_daily_tamil_post(horoscope_data, p)
                photo_payloads.append(
                    (png_bytes, f"raasi_palan_{p.rashi_id:02d}_{p.rashi_name_en.lower()}_{target_date}.png", rashi_caption)
                )

            if len(missing_in_group) == 1:
                # Single remaining Rashi posts cleanly as a standalone photo with its full caption
                post_res = await post_photo_to_facebook(
                    image_bytes=photo_payloads[0][0],
                    caption=photo_payloads[0][2],
                    filename=photo_payloads[0][1],
                )
            else:
                group_msg = format_kp_daily_carousel_group_post(
                    horoscope_data,
                    missing_in_group,
                    group_index=g_idx,
                    total_groups=total_groups,
                )
                post_res = await post_carousel_to_facebook(photo_payloads, message=group_msg)

            carousel_posts.append({
                "group_index": g_idx,
                "rashis": [p.rashi_name_en for p in missing_in_group],
                "success": True,
                "post_id": post_res.get("post_id"),
                "fb_url": post_res.get("fb_url"),
            })
            for p in missing_in_group:
                newly_posted += 1
                results.append({
                    "rashi_id": p.rashi_id,
                    "rashi": f"{p.rashi_name_ta} ({p.rashi_name_en})",
                    "success": True,
                    "skipped": False,
                    "post_id": post_res.get("post_id"),
                    "fb_url": post_res.get("fb_url"),
                })
        except Exception as exc:
            logger.error(f"Failed Carousel Group {g_idx}/{total_groups}: {exc}")
            carousel_posts.append({
                "group_index": g_idx,
                "rashis": [p.rashi_name_en for p in missing_in_group],
                "success": False,
                "error": str(exc),
            })
            for p in missing_in_group:
                results.append({
                    "rashi_id": p.rashi_id,
                    "rashi": f"{p.rashi_name_ta} ({p.rashi_name_en})",
                    "success": False,
                    "error": str(exc),
                })

        has_more_groups = any(
            any(p.rashi_name_en.lower() not in already_posted for p in rem_group)
            for rem_group in groups[g_idx:]
        )
        if has_more_groups and delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    results.sort(key=lambda r: r.get("rashi_id", 0))
    return _build_batch_summary(
        target_date,
        "carousel",
        results,
        newly_posted,
        skipped_existing,
        extra={
            "overview_post": overview_result,
            "carousel_posts": carousel_posts,
        },
    )


async def post_all_12_raasi_palans(
    target_date: Optional[str] = None,
    delay_seconds: float = 20.0,
    dry_run: bool = False,
    skip_if_already_posted: bool = True,
    post_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Computes and posts KP Daily Raasi Palan for all 12 Rashis.

    Defaults to 'carousel' mode (1 Overview Card + grouped 4-Rashi multi-photo posts).
    Also supports 'cards' (12 individual photo cards) and 'text' (legacy plain text).
    """
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    effective_mode = _resolve_post_mode(post_mode, is_batch=True)
    horoscope_data = compute_kp_daily_horoscope(
        target_date=target_date,
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
    )

    if dry_run:
        messages = [
            {
                "rashi_id": prediction.rashi_id,
                "rashi_name": f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})",
                "message": format_kp_daily_tamil_post(horoscope_data, prediction),
            }
            for prediction in horoscope_data.predictions
        ]
        payload: Dict[str, Any] = {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "post_mode": effective_mode,
            "has_image": effective_mode != "text",
            "total_rashis": len(messages),
            "posts": messages,
        }
        if effective_mode == "carousel":
            group_size = max(1, min(10, settings.fb_carousel_group_size))
            preds = list(horoscope_data.predictions)
            groups = [preds[i:i + group_size] for i in range(0, len(preds), group_size)]
            payload["overview_message"] = format_kp_daily_overview_post(horoscope_data)
            payload["carousel_groups"] = [
                {
                    "group_index": idx,
                    "rashis": [p.rashi_name_en for p in grp],
                    "message": format_kp_daily_carousel_group_post(horoscope_data, grp, idx, len(groups)),
                }
                for idx, grp in enumerate(groups, start=1)
            ]
        return payload

    async with _get_publish_lock():
        if effective_mode == "carousel":
            return await _post_all_12_carousel_unlocked(
                horoscope_data=horoscope_data,
                target_date=target_date,
                delay_seconds=delay_seconds,
                skip_if_already_posted=skip_if_already_posted,
            )
        return await _post_all_12_sequential_unlocked(
            horoscope_data=horoscope_data,
            target_date=target_date,
            delay_seconds=delay_seconds,
            skip_if_already_posted=skip_if_already_posted,
            effective_mode=effective_mode,
        )
