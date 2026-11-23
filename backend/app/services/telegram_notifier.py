"""Telegram Admin Delivery Service for Daily KP Raasi Palan.

Sends the high-resolution daily Rashi infographic posters directly to the Admin's
Telegram chat or channel, enabling 1-click sharing to WhatsApp Status, WhatsApp Channels,
and other broadcast media without any account ban risks.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.parse
from typing import Any, Dict, List, Optional, Sequence

import httpx

from app.config import settings
from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction
from app.services.facebook_publisher import format_tamil_date

logger = logging.getLogger("gai.telegram")

TELEGRAM_API_BASE = "https://api.telegram.org"


def _get_bot_url(endpoint: str, bot_token: Optional[str] = None) -> str:
    token = (bot_token or settings.telegram_bot_token or "").strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured in settings or environment.")
    return f"{TELEGRAM_API_BASE}/bot{token}/{endpoint.lstrip('/')}"


async def verify_telegram_credentials(
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Verifies whether the Telegram bot token and chat ID are valid and responsive."""
    token = (bot_token or settings.telegram_bot_token or "").strip()
    target_chat = (chat_id or settings.telegram_chat_id or "").strip()

    if not token or not target_chat:
        return {
            "configured": False,
            "valid": False,
            "chat_id": target_chat or None,
            "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing.",
        }

    try:
        url = _get_bot_url("getMe", token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()
            if resp.status_code == 200 and data.get("ok"):
                bot_user = data.get("result", {})
                return {
                    "configured": True,
                    "valid": True,
                    "bot_id": bot_user.get("id"),
                    "bot_username": bot_user.get("username"),
                    "bot_name": bot_user.get("first_name"),
                    "chat_id": target_chat,
                }
            err_desc = data.get("description", f"HTTP {resp.status_code}")
            return {
                "configured": True,
                "valid": False,
                "chat_id": target_chat,
                "error": f"Telegram API error: {err_desc}",
            }
    except Exception as exc:
        return {
            "configured": True,
            "valid": False,
            "chat_id": target_chat,
            "error": str(exc),
        }


def format_telegram_caption(
    horoscope_data: KpDailyHoroscopeResponse,
    part_idx: int,
    predictions_group: Sequence[RashiDailyPrediction],
) -> str:
    """Formats a concise Tamil caption for the 4-Rasi photo album on Telegram."""
    date_str = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
    rashi_names = ", ".join(f"{p.rashi_name_ta}" for p in predictions_group)

    return (
        f"✨ இன்றைய தினசரி ராசிபலன் – பகுதி {part_idx}\n"
        f"📅 {date_str}\n"
        f"⭐ {rashi_names}\n\n"
        f"🙏 Gokul's Astrological Insights | Thiruverkadu\n"
        f"💡 WhatsApp Status-ல் பகிர: மேலுள்ள படங்களைத் தொட்டு 'Share' வழியே WhatsApp Status-க்கு பகிரவும்."
    )


async def send_telegram_media_group(
    photo_paths: Sequence[str],
    caption: str,
    chat_id: Optional[str] = None,
    bot_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Uploads a list of 1:1 square poster images as a single photo album with a caption."""
    target_chat = (chat_id or settings.telegram_chat_id or "").strip()
    if not target_chat:
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    existing_paths = [p for p in photo_paths if os.path.isfile(p)]
    if not existing_paths:
        raise FileNotFoundError(f"No valid photo files found to send in Telegram media group: {photo_paths}")

    url = _get_bot_url("sendMediaGroup", bot_token)

    # Telegram media parameter references files attached via 'attach://<key>'
    media_descriptors = []
    files_to_upload: Dict[str, Any] = {}
    file_handles = []

    try:
        for idx, fpath in enumerate(existing_paths):
            key = f"photo_{idx}"
            media_item: Dict[str, Any] = {
                "type": "photo",
                "media": f"attach://{key}",
            }
            if idx == 0 and caption:
                media_item["caption"] = caption[:1024]  # Telegram photo caption limit is 1024 chars
            media_descriptors.append(media_item)

            fh = open(fpath, "rb")
            file_handles.append(fh)
            files_to_upload[key] = (os.path.basename(fpath), fh, "image/png")

        data = {
            "chat_id": target_chat,
            "media": json.dumps(media_descriptors),
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, data=data, files=files_to_upload)
            res_data = resp.json()

            if resp.status_code == 200 and res_data.get("ok"):
                return {
                    "success": True,
                    "message_ids": [m.get("message_id") for m in res_data.get("result", [])],
                    "photo_count": len(existing_paths),
                }

            err_desc = res_data.get("description", f"HTTP {resp.status_code}")
            logger.error(f"Failed to send Telegram media group: {err_desc}")
            return {
                "success": False,
                "error": err_desc,
                "photo_count": len(existing_paths),
            }
    finally:
        for fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass


async def send_telegram_text(
    message: str,
    chat_id: Optional[str] = None,
    bot_token: Optional[str] = None,
    parse_mode: Optional[str] = "HTML",
    inline_keyboard: Optional[List[List[Dict[str, str]]]] = None,
) -> Dict[str, Any]:
    """Sends a text notification message to the Admin's Telegram."""
    target_chat = (chat_id or settings.telegram_chat_id or "").strip()
    if not target_chat:
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    url = _get_bot_url("sendMessage", bot_token)
    payload: Dict[str, Any] = {
        "chat_id": target_chat,
        "text": message,
        "disable_web_page_preview": False,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if inline_keyboard:
        payload["reply_markup"] = json.dumps({"inline_keyboard": inline_keyboard})

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload)
        res_data = resp.json()
        if resp.status_code == 200 and res_data.get("ok"):
            return {
                "success": True,
                "message_id": res_data.get("result", {}).get("message_id"),
            }
        err_desc = res_data.get("description", f"HTTP {resp.status_code}")
        return {"success": False, "error": err_desc}


async def send_daily_posters_to_telegram(
    horoscope_data: KpDailyHoroscopeResponse,
    posters_map: Dict[int, str],
    group_size: int = 4,
    chat_id: Optional[str] = None,
    bot_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Sends all 12 generated posters to the Admin's Telegram in 3 structured albums."""
    target_token = (bot_token or settings.telegram_bot_token or "").strip()
    target_chat = (chat_id or settings.telegram_chat_id or "").strip()

    if not target_token or not target_chat:
        logger.info("Telegram notification skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set.")
        return {
            "success": False,
            "skipped": True,
            "reason": "credentials_not_configured",
        }

    predictions = horoscope_data.predictions
    groups = [predictions[i : i + group_size] for i in range(0, len(predictions), group_size)]
    results: List[Dict[str, Any]] = []

    logger.info(
        f"Dispatching {len(predictions)} Rashi posters across {len(groups)} Telegram albums to chat {target_chat}..."
    )

    for idx, group in enumerate(groups, start=1):
        photo_paths = [posters_map[p.rashi_id] for p in group if p.rashi_id in posters_map]
        caption = format_telegram_caption(horoscope_data, idx, group)

        try:
            res = await send_telegram_media_group(
                photo_paths=photo_paths,
                caption=caption,
                chat_id=target_chat,
                bot_token=target_token,
            )
            res["part"] = idx
            res["rashis"] = ", ".join(p.rashi_name_ta for p in group)
            results.append(res)
        except Exception as exc:
            logger.error(f"Error sending Telegram album Part {idx}: {exc}")
            results.append({
                "part": idx,
                "success": False,
                "error": str(exc),
            })

        # Mild delay between albums
        if idx < len(groups):
            await asyncio.sleep(2.0)

    success_count = sum(1 for r in results if r.get("success"))

    # Send a quick 1-click WhatsApp shortcut message
    if success_count > 0:
        date_str = format_tamil_date(horoscope_data.date, horoscope_data.day_of_week_ta)
        wa_share_text = urllib.parse.quote(
            f"✨ இன்றைய தினசரி ராசிபலன் ({date_str})\n"
            f"அனைத்து ராசிகளுக்கான விரிவான பலன்களைக் காணுங்கள்:\n"
            f"https://gai-astrology-frontend.onrender.com"
        )
        wa_url = f"https://api.whatsapp.com/send?text={wa_share_text}"

        help_msg = (
            f"✅ <b>இன்றைய ராசிபலன் படங்கள் வெற்றிகரமாக டெலிகிராமிற்கு அனுப்பப்பட்டன!</b>\n\n"
            f"📅 <b>தேதி:</b> {date_str}\n"
            f"📸 <b>அனுப்பப்பட்ட படங்கள்:</b> {len(predictions)} ராசிகள் (3 ஆல்பங்கள்)\n\n"
            f"👉 <b>WhatsApp Status / Channel-ல் பகிர:</b>\n"
            f"1. மேலே உள்ள படங்களைத் தொட்டு <b>Share</b> கொடுக்கவும்.\n"
            f"2. <b>WhatsApp</b> தேர்வு செய்து <b>My Status</b> அல்லது உங்கள் <b>WhatsApp Channel</b>-ல் பகிரவும்."
        )
        keyboard = [[{"text": "📲 WhatsApp-ல் பகிர (Share Link)", "url": wa_url}]]
        try:
            await send_telegram_text(
                message=help_msg,
                chat_id=target_chat,
                bot_token=target_token,
                inline_keyboard=keyboard,
            )
        except Exception as msg_err:
            logger.warning(f"Failed to send Telegram helper message: {msg_err}")

    return {
        "success": success_count == len(groups),
        "target_date": horoscope_data.date,
        "total_parts": len(groups),
        "successful_parts": success_count,
        "results": results,
    }
