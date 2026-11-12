"""Facebook Social Media Publishing Service.

Handles automated and manual posting of KP Daily Raasi Palan updates
for all 12 Rashis to Facebook Pages using the Meta Graph API.
Matches the official website formatting 1-to-1.
"""

from __future__ import annotations

import asyncio
import logging
import re
import sys
import weakref
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
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


def _format_tamil_date_prefix(date_str: str) -> str:
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


def _format_tamil_date(date_str: str, day_ta: str) -> str:
    """Formats YYYY-MM-DD into '10 நவம்பர் 2026 – செவ்வாய்க்கிழமை'."""
    return f"{_format_tamil_date_prefix(date_str)} – {day_ta}"


def _clean_brief(text: str) -> str:
    """Strips sign prefix (e.g., 'மேஷம் (8-ம் இடத்தில்...):') from the brief statement."""
    if not text:
        return ""
    cleaned = re.sub(r"^.*?\):\s*", "", text).strip(" \"'")
    return cleaned or text


def _format_aspect_text_ta(insight: str, rec: str) -> str:
    """Cleans technical KP jargon and combines insight and key recommendation into readable Tamil."""
    clean = re.sub(
        r"(?:KP\s*பாவகங்கள்|(?:\d+(?:\s*அல்லது\s*\d+)?|\[[\d,\s]+\]|\{houses\}|\d+(?:,\s*\d+)*)-ம்\s*பாவக[^.;]*[.;]?)",
        "",
        insight or "",
        flags=re.IGNORECASE,
    )
    clean = re.sub(r"\{houses\}", "", clean)
    clean = re.sub(r",\s*உப-அதிபதியின் ஆதிக்கத்தால்", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    if len(clean) < 35 and rec:
        rec_short = rec.split(";")[0].strip().rstrip(".")
        if rec_short:
            clean = f"{clean.rstrip('.')}. {rec_short}." if clean else f"{rec_short}."
    return clean or rec or insight


def format_kp_daily_tamil_post(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
) -> str:
    """Formats the KP Daily Horoscope for a given Rashi into the exact Tamil post text matching the website."""
    r_name_ta = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"
    symbol = RASHI_SYMBOLS.get(prediction.rashi_id, "✨")
    formatted_date = _format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)

    # Filter Moon Sub-Lord hourly timeline windows using en-dash
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
        f"{_format_aspect_text_ta(a.insight_ta, a.key_recommendation_ta)}"
        for a in prediction.aspects
    )

    stars_display = int(round(prediction.daily_rating_stars)) if prediction.daily_rating_stars else 2
    sentiment_ta = SENTIMENT_MAP_TA.get(prediction.day_sentiment, prediction.day_sentiment)
    lucky_color = prediction.lucky_color_ta.split("&")[0].strip() if prediction.lucky_color_ta else ""

    post_message = (
        f"தினசரி ராசிபலன்\n"
        f"📅 தேதி: {formatted_date}\n\n"
        f"{symbol} {r_name_ta} - ⭐ இன்றைய சாதக நிலை: {prediction.daily_score}% ({stars_display}/5 – {sentiment_ta})\n\n"
        f"🔮 இன்றைய பொதுப்பலன்:\n\n"
        f"{_clean_brief(prediction.brief_statement_ta)}\n\n"
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

    return post_message


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
    """Posts a text message directly to the Facebook Page feed.

    Returns a dictionary containing post id and status.
    """
    pid = (page_id or settings.fb_page_id or "").strip()
    token = (access_token or settings.fb_page_access_token or "").strip()

    if not pid:
        raise ValueError("FB_PAGE_ID is not configured in settings or environment.")
    if not token:
        raise ValueError("FB_PAGE_ACCESS_TOKEN is not configured in settings or environment.")

    url = f"{FACEBOOK_API_BASE}/{settings.fb_graph_api_version}/{pid}/feed"
    payload = {
        "message": message,
        "access_token": token,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, data=payload)
        resp_data = resp.json()

        if resp.status_code != 200 or "error" in resp_data:
            error_obj = resp_data.get("error", {})
            err_message = error_obj.get("message", f"Facebook API returned HTTP {resp.status_code}")
            err_type = error_obj.get("type", "OAuthException")
            err_code = error_obj.get("code")
            logger.error(f"Failed to post to Facebook Page {pid}: [{err_code}] {err_message}")
            raise RuntimeError(f"Facebook Graph API Error ({err_code} - {err_type}): {err_message}")

        post_id = resp_data.get("id")
        logger.info(f"Successfully posted to Facebook Page {pid}. Post ID: {post_id}")
        return {
            "success": True,
            "post_id": post_id,
            "page_id": pid,
            "fb_url": f"https://www.facebook.com/{post_id}" if post_id else None,
        }


_RASHI_HEADER_RE = re.compile(r"\(([A-Za-z]+)\)\s*-\s*⭐")


async def fetch_posted_rashis_for_date(
    target_date: str,
    page_id: Optional[str] = None,
    access_token: Optional[str] = None,
    limit: int = 40,
) -> Dict[str, Dict[str, Any]]:
    """Checks the Facebook Page feed for Rashis already posted for target_date (YYYY-MM-DD)."""
    pid = (page_id or settings.fb_page_id or "").strip()
    token = (access_token or settings.fb_page_access_token or "").strip()
    if not pid or not token:
        return {}

    date_marker = f"📅 தேதி: {_format_tamil_date_prefix(target_date)}"
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
                return {}
    except Exception as exc:
        logger.warning(f"Error reading existing Facebook Page posts for deduplication: {exc}")
        return {}

    posted: Dict[str, Dict[str, Any]] = {}
    for item in data.get("data", []):
        msg = item.get("message") or ""
        if "தினசரி ராசிபலன்" not in msg or date_marker not in msg:
            continue
        match = _RASHI_HEADER_RE.search(msg)
        if not match:
            continue
        rashi_key = match.group(1).strip().lower()
        post_id = item.get("id")
        if rashi_key not in posted:
            posted[rashi_key] = {
                "post_id": post_id,
                "fb_url": item.get("permalink_url") or (f"https://www.facebook.com/{post_id}" if post_id else None),
                "created_time": item.get("created_time"),
            }
    return posted


async def generate_and_post_daily_raasi_palan(
    target_date: Optional[str] = None,
    rashi: Optional[str] = None,
    dry_run: bool = False,
    skip_if_already_posted: Optional[bool] = None,
) -> Dict[str, Any]:
    """Generates today's KP Daily Raasi Palan in Tamil and posts it to Facebook.

    If rashi is 'all', posts all 12 Rashis in order with an anti-spam pacing delay.
    If dry_run is True, formats the message(s) and returns them without posting.
    """
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    target_rashi = (rashi or settings.fb_post_rashi or "all").strip()

    # If 'all' is requested, call batch handler for all 12 rashis
    if target_rashi.lower() == "all":
        skip_dup = True if skip_if_already_posted is None else skip_if_already_posted
        return await post_all_12_raasi_palans(
            target_date=target_date,
            delay_seconds=settings.fb_post_delay_seconds,
            dry_run=dry_run,
            skip_if_already_posted=skip_dup,
        )

    # Single Rashi posting
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

        post_result = await post_to_facebook(post_text)
        post_result.update({
            "target_date": target_date,
            "rashi": rashi_label,
            "posted_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "preview_text": post_text[:200] + "...",
        })
        return post_result


async def _post_all_12_unlocked(
    horoscope_data: KpDailyHoroscopeResponse,
    target_date: str,
    delay_seconds: float,
    skip_if_already_posted: bool,
) -> Dict[str, Any]:
    """Executes sequential 12-Rashi Facebook publishing while holding the publish lock."""
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
            results.append({
                "rashi_id": prediction.rashi_id,
                "rashi": rashi_label,
                "success": True,
                "skipped": True,
                "reason": "already_posted_today",
                "post_id": existing.get("post_id"),
                "fb_url": existing.get("fb_url"),
            })
            continue

        try:
            logger.info(f"Posting {index + 1}/12: {rashi_label} to Facebook...")
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

    success_count = sum(1 for r in results if r.get("success"))
    failed_count = len(results) - success_count
    return {
        "success": failed_count == 0 and success_count > 0,
        "target_date": target_date,
        "total_attempted": len(results),
        "successful_posts": success_count,
        "newly_posted": newly_posted,
        "skipped_existing": skipped_existing,
        "failed_posts": failed_count,
        "results": results,
    }


async def post_all_12_raasi_palans(
    target_date: Optional[str] = None,
    delay_seconds: float = 20.0,
    dry_run: bool = False,
    skip_if_already_posted: bool = True,
) -> Dict[str, Any]:
    """Computes and posts KP Daily Raasi Palan for all 12 Rashis sequentially.

    Skips Rashis already posted for target_date unless skip_if_already_posted=False,
    and serializes concurrent runs via an event-loop lock.
    """
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

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
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "total_rashis": len(messages),
            "posts": messages,
        }

    async with _get_publish_lock():
        return await _post_all_12_unlocked(
            horoscope_data=horoscope_data,
            target_date=target_date,
            delay_seconds=delay_seconds,
            skip_if_already_posted=skip_if_already_posted,
        )
