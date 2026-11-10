"""Facebook Social Media Publishing Service.

Handles automated and manual posting of KP Daily Raasi Palan updates
for all 12 Rashis to Facebook Pages using the Meta Graph API.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

logger = logging.getLogger("gai.facebook")

FACEBOOK_API_BASE = "https://graph.facebook.com"

RASHIS_ORDER = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def format_kp_daily_tamil_post(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
) -> str:
    """Formats the KP Daily Horoscope for a given Rashi into the exact Tamil Facebook post text."""
    r_name_ta = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"

    # Filter Moon Sub-Lord hourly timeline windows
    golden_times = (
        ", ".join(
            f"{w.start_time} - {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "golden"
        )
        or prediction.golden_hour_window
        or "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"
    )

    neutral_times = (
        ", ".join(
            f"{w.start_time} - {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "neutral"
        )
        or "வழக்கமான நேரம்"
    )

    caution_times = (
        ", ".join(
            f"{w.start_time} - {w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "caution"
        )
        or prediction.caution_hour_window
        or "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"
    )

    # Format all 5 life aspects in points
    aspects_ta = "\n\n".join(
        f"• {a.aspect_name_tamil} ({a.score}% - {a.status}):\n"
        f"  {a.insight_ta}\n"
        f"  [வழிகாட்டல்: {a.key_recommendation_ta}]"
        for a in prediction.aspects
    )

    stars_display = int(round(prediction.daily_rating_stars)) if prediction.daily_rating_stars else 2

    post_message = (
        f"✨ கே.பி. தினசரி ராசிபலன்: {r_name_ta}\n"
        f"📅 தேதி: {horoscope_data.date} ({horoscope_data.day_of_week_ta})\n"
        f"📊 இன்றைய சாதக நிலை: {prediction.daily_score}% ({prediction.day_sentiment}) ⭐ {stars_display}/5\n\n"
        f"🎯 இன்றைய தாரக மந்திரம்:\n"
        f'"{prediction.brief_statement_ta}"\n\n'
        f"🌟 சாதகமான வாய்ப்பு: {prediction.peak_highlight_ta}\n"
        f"⚠️ கவனிக்க வேண்டியவை: {prediction.caution_trap_ta}\n\n"
        f"📋 அனைத்து அம்சங்களின் விரிவான பலன்கள்:\n"
        f"{aspects_ta}\n\n"
        f"⏱️ சந்திரனின் மணி நேர உப-அதிபதி கால அட்டவணை:\n"
        f"• Golden: {golden_times}\n"
        f"• Neutral: {neutral_times}\n"
        f"• Caution: {caution_times}\n\n"
        f"🍀 அதிர்ஷ்ட நிறம் & எண்: {prediction.lucky_color_ta} (#{prediction.lucky_number}) | திசை: {prediction.lucky_direction_ta}\n"
        f"🛡️ கே.பி. வழிகாட்டல்: {prediction.daily_remedy_ta}\n\n"
        f"🔮 Gokul's Astrological Insights - Gokul Murugan - Thiruverkadu"
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


async def generate_and_post_daily_raasi_palan(
    target_date: Optional[str] = None,
    rashi: Optional[str] = None,
    dry_run: bool = False,
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
        return await post_all_12_raasi_palans(
            target_date=target_date,
            delay_seconds=settings.fb_post_delay_seconds,
            dry_run=dry_run,
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

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "rashi": f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})",
            "message": post_text,
        }

    post_result = await post_to_facebook(post_text)
    post_result.update({
        "target_date": target_date,
        "rashi": f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})",
        "posted_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "preview_text": post_text[:200] + "...",
    })
    return post_result


async def post_all_12_raasi_palans(
    target_date: Optional[str] = None,
    delay_seconds: float = 20.0,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Computes and posts KP Daily Raasi Palan for all 12 Rashis sequentially.

    Introduces a 20-second delay between posts to prevent Facebook anti-spam rate limiting.
    """
    if not target_date:
        ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        target_date = ist_now.strftime("%Y-%m-%d")

    # Compute all 12 rashis at once using the astrological engine
    horoscope_data = compute_kp_daily_horoscope(
        target_date=target_date,
        timezone_str="Asia/Kolkata",
        rashi_filter="all",
    )

    results: List[Dict[str, Any]] = []
    messages: List[Dict[str, Any]] = []

    for index, prediction in enumerate(horoscope_data.predictions):
        post_text = format_kp_daily_tamil_post(horoscope_data, prediction)
        rashi_label = f"{prediction.rashi_name_ta} ({prediction.rashi_name_en})"

        if dry_run:
            messages.append({
                "rashi_id": prediction.rashi_id,
                "rashi_name": rashi_label,
                "message": post_text,
            })
            continue

        try:
            logger.info(f"Posting {index + 1}/12: {rashi_label} to Facebook...")
            post_res = await post_to_facebook(post_text)
            results.append({
                "rashi_id": prediction.rashi_id,
                "rashi": rashi_label,
                "success": True,
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

        # Anti-spam delay between posts if more posts remain
        if index < len(horoscope_data.predictions) - 1 and delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "target_date": target_date,
            "total_rashis": len(messages),
            "posts": messages,
        }

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "success": success_count > 0,
        "target_date": target_date,
        "total_attempted": len(results),
        "successful_posts": success_count,
        "failed_posts": len(results) - success_count,
        "results": results,
    }
