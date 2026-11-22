"""Facebook Social Media Publishing Service.

Handles automated and manual posting of KP Daily Raasi Palan updates
for all 12 Rashis to Facebook Pages using the Meta Graph API in clean,
authentic Tamil text format matching the official website.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import json
import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple
import weakref
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope
from app.services.daily_poster_generator import generate_single_poster, generate_all_12_posters

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

SENTIMENT_MAP_TA: Dict[str, str] = {
    "Excellent": "மிகச் சிறப்பான நாள்",
    "Favorable": "சாதகமான நாள்",
    "Mixed": "மிதமான நாள்",
    "Challenging": "சவாலான நாள்",
}

MONTHS_TA: Dict[int, str] = {
    1: "ஜனவரி",
    2: "பிப்ரவரி",
    3: "மார்ச்",
    4: "ஏப்ரல்",
    5: "மே",
    6: "ஜூன்",
    7: "ஜூலை",
    8: "ஆகஸ்ட்",
    9: "செப்டம்பர்",
    10: "அக்டோபர்",
    11: "நவம்பர்",
    12: "டிசம்பர்",
}

_RASHI_HEADER_RE = re.compile(r"\(([A-Za-z]+)\)\s*-\s*⭐")

RASHI_TA_TO_EN: Dict[str, str] = {
    "மேஷம்": "aries",
    "ரிஷபம்": "taurus",
    "மிதுனம்": "gemini",
    "கடகம்": "cancer",
    "சிம்மம்": "leo",
    "கன்னி": "virgo",
    "துலாம்": "libra",
    "விருச்சிகம்": "scorpio",
    "தனுசு": "sagittarius",
    "மகரம்": "capricorn",
    "கும்பம்": "aquarius",
    "மீனம்": "pisces",
}
ALL_RASHIS_EN = set(RASHI_TA_TO_EN.values())

CAROUSEL_PART_TO_RASHIS: Dict[int, List[str]] = {
    1: ["aries", "taurus", "gemini", "cancer"],
    2: ["leo", "virgo", "libra", "scorpio"],
    3: ["sagittarius", "capricorn", "aquarius", "pisces"],
}


def format_tamil_date_prefix(date_str: str) -> str:
    """Formats YYYY-MM-DD into '10 நவம்பர் 2026' without weekday."""
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            year = parts[0]
            month = int(parts[1])
            day = int(parts[2])
            month_name = MONTHS_TA.get(month, parts[1])
            return f"{day} {month_name} {year}"
    except Exception:
        pass
    return date_str


def format_tamil_date(date_str: str, day_ta: str) -> str:
    """Formats YYYY-MM-DD into '10 நவம்பர் 2026 – செவ்வாய்க்கிழமை'."""
    return f"{format_tamil_date_prefix(date_str)} – {day_ta}"


def clean_brief_ta(text: str) -> str:
    """Strips sign prefix (e.g., 'மேஷம் (8-ம் இடத்தில்...):') from brief statement."""
    if not text:
        return ""
    cleaned = re.sub(r"^.*?\):\s*", "", text).strip(" \"'")
    return cleaned or text


def format_aspect_text_ta(insight: str, rec: str) -> str:
    """Cleans technical KP jargon and combines insight and key recommendation into readable Tamil."""
    clean = re.sub(
        r"(?:KP\s*பாவகங்கள்|(?:\d+(?:\s*அல்லது\s*\d+)?|\[[\d,\s]+\]|\{houses\}|\d+(?:,\s*\d+)*)-ம்\s*பாவக[^.;]*[.;]?)",
        "",
        insight or "",
        flags=re.IGNORECASE,
    )
    clean = re.sub(r"\s+", " ", clean).strip()
    if clean.startswith(("-", "•", "–")):
        clean = clean.lstrip("-•– ").strip()

    clean_rec = re.sub(r"\s+", " ", rec or "").strip()
    if clean_rec.startswith(("-", "•", "–")):
        clean_rec = clean_rec.lstrip("-•– ").strip()

    if clean and clean_rec:
        if clean.rstrip(".").endswith(clean_rec.rstrip(".")):
            return clean
        if clean_rec in clean:
            return clean
        return f"{clean} {clean_rec}"
    return clean or clean_rec or "சாதகமான பலன் உண்டு."


# Backwards-compatibility aliases
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


def _resolve_post_mode(requested_mode: Optional[str] = None, is_batch: bool = False) -> str:
    """Resolves post mode: 'carousel' (for batch of 12 rashis), 'text', or 'image'."""
    if requested_mode:
        mode = requested_mode.strip().lower()
        if mode in ("carousel", "image", "photos"):
            return "carousel"
        if mode == "text":
            return "text"
    if is_batch:
        mode = (settings.fb_post_mode or "carousel").strip().lower()
        return "carousel" if mode in ("carousel", "image", "photos") else "text"
    return "text"


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


async def post_single_photo_to_facebook(
    image_path: str,
    message: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Posts a single image with caption to Facebook Page."""
    pid, token = _resolve_credentials(page_id, access_token)
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Poster image not found at {image_path}")

    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/photos"
    async with httpx.AsyncClient(timeout=45.0) as client:
        with open(image_path, "rb") as f:
            photo_bytes = f.read()
        resp = await client.post(
            url,
            data={"caption": message, "access_token": token},
            files={"source": (os.path.basename(image_path), photo_bytes, "image/png")},
        )
        resp_data = resp.json()
        _raise_for_graph_error(resp, resp_data, pid)
        post_id = resp_data.get("post_id") or resp_data.get("id")
        return {
            "success": True,
            "post_id": post_id,
            "page_id": pid,
            "post_type": "photo",
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


async def post_photo_carousel_to_facebook(
    image_paths: Sequence[str],
    message: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Uploads multiple images as unpublished photos and publishes a single multi-photo feed post."""
    pid, token = _resolve_credentials(page_id, access_token)
    photo_ids: List[str] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for img_path in image_paths:
            if not os.path.isfile(img_path):
                raise FileNotFoundError(f"Poster image not found at {img_path}")
            with open(img_path, "rb") as f:
                photo_bytes = f.read()

            upload_url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/photos"
            resp = await client.post(
                upload_url,
                data={"published": "false", "access_token": token},
                files={"source": (os.path.basename(img_path), photo_bytes, "image/png")},
            )
            resp_data = resp.json()
            _raise_for_graph_error(resp, resp_data, pid)
            photo_id = resp_data.get("id")
            if photo_id:
                photo_ids.append(str(photo_id))

        if not photo_ids:
            raise RuntimeError("No photo IDs returned from Facebook photo uploads.")

        feed_url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/feed"
        attached_media = [{"media_fbid": pid_str} for pid_str in photo_ids]
        feed_resp = await client.post(
            feed_url,
            data={
                "message": message,
                "attached_media": json.dumps(attached_media),
                "access_token": token,
            },
        )
        feed_data = feed_resp.json()
        _raise_for_graph_error(feed_resp, feed_data, pid)
        post_id = feed_data.get("id")
        logger.info(f"Successfully posted carousel ({len(photo_ids)} photos) to Facebook Page {pid}. Post ID: {post_id}")
        return {
            "success": True,
            "post_id": post_id,
            "page_id": pid,
            "post_type": "carousel",
            "photo_count": len(photo_ids),
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


def format_carousel_caption(
    horoscope_data: KpDailyHoroscopeResponse,
    group_index: int,
    predictions_group: Sequence[RashiDailyPrediction],
) -> str:
    """Formats engaging Tamil caption for a 4-Rasi carousel post."""
    formatted_date = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    rashi_names = ", ".join(p.rashi_name_ta for p in predictions_group)
    hashtags = " ".join(f"#{p.rashi_name_en}" for p in predictions_group)

    return (
        f"✨ இன்றைய தினசரி ராசிபலன் – பகுதி {group_index} ({rashi_names})\n"
        f"📅 தேதி: {formatted_date}\n\n"
        f"{rashi_names} ராசிகளுக்கான விரிவான சாதக நிலை, தொழில், தனம், குடும்ப பலன்கள், "
        f"அதிர்ஷ்ட நேரம் மற்றும் பரிகாரங்களை மேலே உள்ள படங்களில் காண்க! 👆\n\n"
        f"🙏 Gokul's Astrological Insights\n"
        f"Gokul Murugan | Thiruverkadu\n\n"
        f"#தினசரிராசிபலன் #DailyHoroscope #TamilAstrology {hashtags} #GokulsAstrologicalInsights"
    )


async def _fetch_feed_state_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Tuple[Dict[str, Dict[str, Any]], bool, Dict[int, Dict[str, Any]]]:
    """Reads recent Page posts and returns (posted_rashis_map, overview_posted_today, posted_parts_map)."""
    pid = (page_id or settings.fb_page_id or "").strip()
    token = (access_token or settings.fb_page_access_token or "").strip()
    if not pid or not token:
        return {}, False, {}

    date_prefix = format_tamil_date_prefix(target_date)
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
                return {}, False, {}
    except Exception as exc:
        logger.warning(f"Error reading existing Facebook Page posts for deduplication: {exc}")
        return {}, False, {}

    posted: Dict[str, Dict[str, Any]] = {}
    posted_parts: Dict[int, Dict[str, Any]] = {}
    overview_posted = False

    for item in data.get("data", []):
        msg = item.get("message") or ""
        is_daily_horoscope = ("தினசரி ராசிபலன்" in msg or "ராசிபலன்" in msg or "DailyHoroscope" in msg)
        is_matching_date = (date_prefix in msg or target_date in msg)
        if not (is_daily_horoscope and is_matching_date):
            continue

        if OVERVIEW_MARKER in msg:
            overview_posted = True

        post_id = item.get("id")
        fb_url = item.get("permalink_url") or (f"https://www.facebook.com/{post_id}" if post_id else None)
        entry = {
            "post_id": post_id,
            "fb_url": fb_url,
            "created_time": item.get("created_time"),
        }

        # 1. Detect Carousel Part (பகுதி 1, பகுதி 2, பகுதி 3)
        part_match = re.search(r"பகுதி\s*(\d+)", msg)
        if part_match:
            part_num = int(part_match.group(1))
            if part_num not in posted_parts:
                posted_parts[part_num] = entry
            for rk in CAROUSEL_PART_TO_RASHIS.get(part_num, []):
                if rk not in posted:
                    posted[rk] = entry

        # 2. Detect text post headers: (Aries) - ⭐
        for match in _RASHI_HEADER_RE.finditer(msg):
            rashi_key = match.group(1).strip().lower()
            if rashi_key not in posted:
                posted[rashi_key] = entry

        # 3. Detect hashtags: #Aries, #Taurus, etc.
        for tag in re.findall(r"#([A-Za-z]+)", msg):
            tag_low = tag.lower()
            if tag_low in ALL_RASHIS_EN and tag_low not in posted:
                posted[tag_low] = entry

        # 4. Detect Tamil Rashi names
        for ta_name, en_name in RASHI_TA_TO_EN.items():
            if ta_name in msg and en_name not in posted:
                posted[en_name] = entry

    return posted, overview_posted, posted_parts


async def fetch_posted_rashis_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Dict[str, Dict[str, Any]]:
    """Checks the Facebook Page feed for Rashis already posted for target_date (YYYY-MM-DD)."""
    posted, _, _ = await _fetch_feed_state_for_date(
        target_date=target_date,
        page_id=page_id,
        access_token=access_token,
        limit=limit,
    )
    return posted


async def fetch_posted_carousel_parts_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Dict[int, Dict[str, Any]]:
    """Checks Facebook Page for carousel parts (1, 2, 3) already posted for target_date."""
    _, _, parts = await _fetch_feed_state_for_date(
        target_date=target_date,
        page_id=page_id,
        access_token=access_token,
        limit=limit,
    )
    return parts


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
    effective_mode: str = "text",
) -> Dict[str, Any]:
    """Posts 12 individual Rashi updates as clean text posts."""
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
            logger.info(f"Posting {index + 1}/12 (text): {rashi_label} to Facebook...")
            post_res = await post_to_facebook(post_text)
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

    return _build_batch_summary(target_date, "text", results, newly_posted, skipped_existing)


async def post_daily_carousel_3_posts(
    horoscope_data: KpDailyHoroscopeResponse,
    target_date: str,
    delay_seconds: float = 15.0,
    dry_run: bool = False,
    skip_if_already_posted: bool = True,
    posters_map: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
    """Renders 12 1:1 square posters and publishes 3 carousel posts (4 Rasis each) to Facebook.

    Guarantees strict deduplication: checks Facebook and Instagram feed before posting to prevent duplicate spam.
    """
    group_size = settings.fb_carousel_group_size or 4
    predictions = horoscope_data.predictions
    groups = [predictions[i : i + group_size] for i in range(0, len(predictions), group_size)]

    # 1. Deduplication check: Query Facebook feed for already-posted carousel parts
    posted_parts: Dict[int, Dict[str, Any]] = {}
    if skip_if_already_posted and not dry_run:
        try:
            posted_parts = await fetch_posted_carousel_parts_for_date(target_date)
            if posted_parts:
                logger.info(
                    f"Facebook deduplication check: Found {len(posted_parts)}/{len(groups)} carousel part(s) already posted on Facebook for {target_date}: {list(posted_parts.keys())}"
                )
        except Exception as dedup_exc:
            logger.warning(f"Error checking Facebook feed for duplicate carousel parts: {dedup_exc}")

    parts_to_publish_fb = [
        idx for idx in range(1, len(groups) + 1)
        if not (skip_if_already_posted and not dry_run and idx in posted_parts)
    ]

    # Only generate posters if needed (or if posters_map not provided)
    poster_map: Dict[int, str] = posters_map or {}
    if not poster_map and (dry_run or parts_to_publish_fb or settings.ig_auto_post_enabled):
        loop = asyncio.get_running_loop()
        posters_meta = await loop.run_in_executor(None, generate_all_12_posters, horoscope_data)
        poster_map = {m[0]: m[3] for m in posters_meta}

    results: List[Dict[str, Any]] = []
    newly_posted = 0
    skipped_existing = 0

    for idx, group in enumerate(groups, start=1):
        group_names = ", ".join(f"{p.rashi_name_ta} ({p.rashi_name_en})" for p in group)
        image_paths = [poster_map[p.rashi_id] for p in group if p.rashi_id in poster_map]
        caption = format_carousel_caption(horoscope_data, idx, group)

        if dry_run:
            results.append({
                "post_part": idx,
                "rashis": group_names,
                "photo_count": len(image_paths),
                "image_paths": image_paths,
                "caption": caption,
                "dry_run": True,
                "success": True,
            })
            continue

        if skip_if_already_posted and idx in posted_parts:
            existing = posted_parts[idx]
            skipped_existing += 1
            logger.info(
                f"Skipping Carousel Post Part {idx}/{len(groups)} ({group_names}) - already posted on Facebook (ID: {existing.get('post_id')})."
            )
            results.append({
                "post_part": idx,
                "rashis": group_names,
                "success": True,
                "skipped": True,
                "reason": "already_posted_today",
                "post_id": existing.get("post_id"),
                "fb_url": existing.get("fb_url"),
                "photo_count": len(image_paths),
            })
            continue

        try:
            logger.info(f"Publishing Carousel Post {idx}/{len(groups)} ({group_names}) to Facebook...")
            post_res = await post_photo_carousel_to_facebook(image_paths, caption)
            newly_posted += 1
            results.append({
                "post_part": idx,
                "rashis": group_names,
                "success": True,
                "post_id": post_res.get("post_id"),
                "fb_url": post_res.get("fb_url"),
                "photo_count": len(image_paths),
            })
        except Exception as exc:
            logger.error(f"Failed to publish Carousel Post {idx}/{len(groups)} ({group_names}): {exc}")
            results.append({
                "post_part": idx,
                "rashis": group_names,
                "success": False,
                "error": str(exc),
            })

        has_more_to_publish = any(
            next_idx > idx and next_idx in parts_to_publish_fb
            for next_idx in range(idx + 1, len(groups) + 1)
        )
        if has_more_to_publish and delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    success_count = sum(1 for r in results if r.get("success"))
    failed_count = len(results) - success_count

    # Also post to Instagram if configured, passing existing posters and deduplication check
    ig_summary = None
    if settings.ig_auto_post_enabled:
        try:
            from app.services.instagram_publisher import post_daily_instagram_carousels
            logger.info("Instagram auto-post is enabled: Publishing carousels to Instagram with deduplication check...")
            ig_summary = await post_daily_instagram_carousels(
                horoscope_data=horoscope_data,
                target_date=target_date,
                delay_seconds=delay_seconds,
                dry_run=dry_run,
                skip_if_already_posted=skip_if_already_posted,
                posters_map=poster_map,
            )
        except Exception as ig_err:
            logger.error(f"Failed to publish Instagram carousels: {ig_err}")
            ig_summary = {"success": False, "error": str(ig_err)}

    individual_posts = [
        {
            "rashi_id": prediction.rashi_id,
            "rashi_name": f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})",
            "image_path": poster_map.get(prediction.rashi_id),
            "message": format_kp_daily_tamil_post(horoscope_data, prediction),
        }
        for prediction in predictions
    ]

    return {
        "success": failed_count == 0 and (success_count > 0 or dry_run),
        "dry_run": dry_run,
        "target_date": target_date,
        "post_mode": "carousel",
        "total_posts": len(groups),
        "total_rashis": len(predictions),
        "posts": individual_posts,
        "successful_posts": success_count,
        "newly_posted": newly_posted,
        "skipped_existing": skipped_existing,
        "failed_posts": failed_count,
        "results": results,
        "instagram": ig_summary,
    }


async def generate_and_post_daily_raasi_palan(
    target_date: Optional[str] = None,
    rashi: Optional[str] = None,
    dry_run: bool = False,
    skip_if_already_posted: Optional[bool] = None,
    post_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates today's KP Daily Raasi Palan in Tamil and posts it as carousel image posts (or text) to Facebook."""
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    target_rashi = (rashi or settings.fb_post_rashi or "all").strip()
    effective_mode = _resolve_post_mode(post_mode, is_batch=(target_rashi.lower() == "all"))

    if target_rashi.lower() == "all":
        skip_dup = True if skip_if_already_posted is None else skip_if_already_posted
        return await post_all_12_raasi_palans(
            target_date=target_date,
            delay_seconds=settings.fb_post_delay_seconds,
            dry_run=dry_run,
            skip_if_already_posted=skip_dup,
            post_mode=effective_mode,
        )

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

    loop = asyncio.get_running_loop()
    output_base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "generated_posters",
        horoscope_data.date,
    )
    poster_path = await loop.run_in_executor(None, generate_single_poster, horoscope_data, prediction, output_base)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "rashi": rashi_label,
            "post_mode": effective_mode,
            "has_image": True if effective_mode == "carousel" else False,
            "image_path": poster_path if effective_mode == "carousel" else None,
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

        if effective_mode == "carousel":
            caption = f"✨ {prediction.rashi_name_ta} ({prediction.rashi_name_en}) - இன்றைய தினசரி ராசிபலன் 🗓️ {target_date}\n\n#DailyHoroscope #{prediction.rashi_name_en}"
            post_result = await post_single_photo_to_facebook(poster_path, caption)
        else:
            post_result = await post_to_facebook(post_text)

        post_result.update({
            "target_date": target_date,
            "rashi": rashi_label,
            "post_mode": effective_mode,
            "posted_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "preview_text": post_text[:200] + "...",
        })
        return post_result


async def post_all_12_raasi_palans(
    target_date: Optional[str] = None,
    delay_seconds: float = 20.0,
    dry_run: bool = False,
    skip_if_already_posted: bool = True,
    post_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Computes and posts KP Daily Raasi Palan for all 12 Rashis as carousel posts (or text)."""
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    effective_mode = _resolve_post_mode(post_mode, is_batch=True)

    horoscope_data = compute_kp_daily_horoscope(
        target_date=target_date,
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
    )

    if effective_mode == "carousel":
        async with _get_publish_lock():
            return await post_daily_carousel_3_posts(
                horoscope_data=horoscope_data,
                target_date=target_date,
                delay_seconds=delay_seconds,
                dry_run=dry_run,
                skip_if_already_posted=skip_if_already_posted,
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
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "post_mode": "text",
            "has_image": False,
            "total_rashis": len(messages),
            "posts": messages,
        }

    async with _get_publish_lock():
        return await _post_all_12_sequential_unlocked(
            horoscope_data=horoscope_data,
            target_date=target_date,
            delay_seconds=delay_seconds,
            skip_if_already_posted=skip_if_already_posted,
            effective_mode="text",
        )
