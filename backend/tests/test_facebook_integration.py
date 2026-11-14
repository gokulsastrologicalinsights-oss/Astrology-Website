"""Tests for Facebook KP Daily Raasi Palan publishing integration."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from zoneinfo import ZoneInfo

from app.main import app
from app.services.facebook_publisher import (
    format_kp_daily_tamil_post,
    generate_and_post_daily_raasi_palan,
)
from app.services.facebook_scheduler import calculate_next_run, get_scheduler_status
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

client = TestClient(app)


def test_kp_daily_tamil_post_format():
    """Verifies that the Tamil post generator produces the exact required structure."""
    horoscope_data = compute_kp_daily_horoscope(
        target_date="2026-11-10",
        timezone_str="Asia/Kolkata",
        rashi_filter="Aries",
    )
    prediction = horoscope_data.predictions[0]
    post_text = format_kp_daily_tamil_post(horoscope_data, prediction)

    # Key headers and elements matching the website format
    assert "தினசரி ராசிபலன்" in post_text
    assert "**" not in post_text
    assert "📅 தேதி: 10 நவம்பர் 2026 – செவ்வாய்க்கிழமை" in post_text
    assert "♈ மேஷம் (Aries) - ⭐ இன்றைய சாதக நிலை: 25% (2/5 – சவாலான நாள்)" in post_text
    assert "🔮 இன்றைய பொதுப்பலன்:" in post_text
    assert "📊 இன்றைய விரிவான பலன்கள்:" in post_text
    assert "💼 தொழில் & உத்தியோகம் – 22%" in post_text
    assert "💰 தனம் & பணவரவு – 33%" in post_text
    assert "❤️ குடும்பம் & உறவுகள் – 24%" in post_text
    assert "🩺 உடல்நலம் & உற்சாகம் – 21%" in post_text
    assert "✈️ பயணம் & கல்வி – 26%" in post_text
    assert "⏰ இன்றைய நேர வழிகாட்டல்:" in post_text
    assert "🌟 அதிர்ஷ்ட நேரம்: 10:30 AM – 12:45 PM" in post_text
    assert "⚠️ கவனமான நேரம்: 04:30 PM – 06:00 PM" in post_text
    assert "🎨 அதிர்ஷ்ட நிறம்: பவள சிவப்பு" in post_text
    assert "🔢 அதிர்ஷ்ட எண்: 9" in post_text
    assert "🧭 அதிர்ஷ்ட திசை: கிழக்கு" in post_text
    assert "🛡️ இன்றைய ஆலோசனை:" in post_text
    assert "🙏 Gokul's Astrological Insights" in post_text
    assert "Gokul Murugan | Thiruverkadu" in post_text


def test_generate_and_post_dry_run():
    """Ensures dry-run mode returns formatted content without attempting HTTP calls."""
    import asyncio
    res = asyncio.run(generate_and_post_daily_raasi_palan(
        target_date="2026-11-10",
        rashi="Aries",
        dry_run=True,
    ))
    assert res["success"] is True
    assert res["dry_run"] is True
    assert "மேஷம்" in res["message"]
    assert "தினசரி ராசிபலன்" in res["message"]
    assert "**" not in res["message"]


def test_generate_all_12_rashis_dry_run():
    """Ensures posting for all 12 rashis in dry run produces 12 formatted items."""
    import asyncio
    res = asyncio.run(generate_and_post_daily_raasi_palan(
        target_date="2026-11-10",
        rashi="all",
        dry_run=True,
    ))
    assert res["success"] is True
    assert res["dry_run"] is True
    assert res["total_rashis"] == 12
    assert len(res["posts"]) == 12


def test_calculate_next_run():
    """Verifies scheduler calculation correctly identifies the upcoming target time."""
    next_run = calculate_next_run("06:00", "Asia/Kolkata")
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    assert next_run > now_ist
    assert next_run.hour == 6


def test_facebook_preview_endpoint():
    """Tests the /api/v1/social/facebook/preview API endpoint."""
    response = client.get("/api/v1/social/facebook/preview?date=2026-11-10&rashi=Aries")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["dry_run"] is True
    assert "மேஷம்" in data["message"]


def test_facebook_status_endpoint():
    """Tests the /api/v1/social/facebook/status API endpoint."""
    response = client.get("/api/v1/social/facebook/status")
    assert response.status_code == 200
    data = response.json()
    assert "credentials" in data
    assert "scheduler" in data
    assert "in_progress" in data["scheduler"]


def test_fetch_posted_rashis_for_date(monkeypatch):
    """Detects Rashis already posted for the target Tamil date and ignores other dates."""
    import asyncio
    from app.config import settings
    from app.services import facebook_publisher

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {
                "data": [
                    {
                        "id": "page_111",
                        "created_time": "2026-11-12T02:50:00+0000",
                        "permalink_url": "https://www.facebook.com/page/posts/111",
                        "message": "தினசரி ராசிபலன்\n📅 தேதி: 12 நவம்பர் 2026 – வியாழக்கிழமை\n\n♈ மேஷம் (Aries) - ⭐ இன்றைய சாதக நிலை: 25%",
                    },
                    {
                        "id": "page_222",
                        "created_time": "2026-11-12T02:51:00+0000",
                        "message": "தினசரி ராசிபலன்\n📅 தேதி: 12 நவம்பர் 2026 – வியாழக்கிழமை\n\n♉ ரிஷபம் (Taurus) - ⭐ இன்றைய சாதக நிலை: 63%",
                    },
                    {
                        "id": "page_old",
                        "created_time": "2026-11-11T02:50:00+0000",
                        "message": "தினசரி ராசிபலன்\n📅 தேதி: 11 நவம்பர் 2026 – புதன்கிழமை\n\n♊ மிதுனம் (Gemini) - ⭐ இன்றைய சாதக நிலை: 53%",
                    },
                ]
            }

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            return _FakeResponse()

    monkeypatch.setattr(settings, "fb_page_id", "1408545542343822")
    monkeypatch.setattr(settings, "fb_page_access_token", "fake-token")
    monkeypatch.setattr(facebook_publisher.httpx, "AsyncClient", _FakeAsyncClient)

    posted = asyncio.run(facebook_publisher.fetch_posted_rashis_for_date("2026-11-12"))
    assert set(posted.keys()) == {"aries", "taurus"}
    assert posted["aries"]["post_id"] == "page_111"
    assert posted["taurus"]["fb_url"] == "https://www.facebook.com/page_222"


def test_post_all_12_skips_already_posted_rashis(monkeypatch):
    """Ensures batch publishing skips Rashis already on Facebook and only posts remaining ones."""
    import asyncio
    from app.services import facebook_publisher

    posted_calls = []

    async def _fake_fetch(target_date, **kwargs):
        return {
            "aries": {"post_id": "fb_aries", "fb_url": "https://www.facebook.com/fb_aries"},
            "taurus": {"post_id": "fb_taurus", "fb_url": "https://www.facebook.com/fb_taurus"},
        }

    async def _fake_post(message, **kwargs):
        posted_calls.append(message)
        pid = f"fb_new_{len(posted_calls)}"
        return {"success": True, "post_id": pid, "page_id": "123", "fb_url": f"https://www.facebook.com/{pid}"}

    monkeypatch.setattr(facebook_publisher, "fetch_posted_rashis_for_date", _fake_fetch)
    monkeypatch.setattr(facebook_publisher, "post_to_facebook", _fake_post)

    res = asyncio.run(
        facebook_publisher.post_all_12_raasi_palans(
            target_date="2026-11-12",
            delay_seconds=0,
            dry_run=False,
            skip_if_already_posted=True,
            post_mode="text",
        )
    )
    assert res["success"] is True
    assert res["total_attempted"] == 12
    assert res["successful_posts"] == 12
    assert res["skipped_existing"] == 2
    assert res["newly_posted"] == 10
    assert res["failed_posts"] == 0
    assert len(posted_calls) == 10
    assert all("(Aries)" not in m and "(Taurus)" not in m for m in posted_calls)


def test_post_all_12_all_existing_returns_success(monkeypatch):
    """When all 12 Rashis are already posted for today, returns success=True with zero new posts."""
    import asyncio
    from app.services import facebook_publisher

    all_names = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ]

    async def _fake_fetch(target_date, **kwargs):
        return {name: {"post_id": f"fb_{name}", "fb_url": f"https://www.facebook.com/fb_{name}"} for name in all_names}

    async def _fail_if_called(*args, **kwargs):
        raise AssertionError("post_to_facebook should not be called when all 12 are already posted")

    monkeypatch.setattr(facebook_publisher, "fetch_posted_rashis_for_date", _fake_fetch)
    monkeypatch.setattr(facebook_publisher, "post_to_facebook", _fail_if_called)

    res = asyncio.run(
        facebook_publisher.post_all_12_raasi_palans(
            target_date="2026-11-12",
            delay_seconds=0,
            dry_run=False,
            skip_if_already_posted=True,
            post_mode="text",
        )
    )
    assert res["success"] is True
    assert res["successful_posts"] == 12
    assert res["skipped_existing"] == 12
    assert res["newly_posted"] == 0
    assert res["failed_posts"] == 0


def test_background_publish_endpoint_returns_202(monkeypatch):
    """POST /publish with background=true queues publishing and returns HTTP 202 immediately."""
    from app.config import settings
    from app.routers import facebook_social

    monkeypatch.setattr(settings, "fb_page_id", "1408545542343822")
    monkeypatch.setattr(settings, "fb_page_access_token", "fake-token")
    monkeypatch.setattr(
        facebook_social,
        "trigger_background_publish",
        lambda execution_date=None, rashi="all", force=False: {
            "success": True,
            "accepted": True,
            "status": "queued",
            "target_date": execution_date or "2026-11-12",
            "rashi": rashi,
        },
    )

    response = client.post(
        "/api/v1/social/facebook/publish",
        json={"date": "2026-11-12", "rashi": "all", "background": True},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] is True
    assert data["status"] == "queued"


def test_scheduler_background_publish_records_state_and_deduplicates(monkeypatch, tmp_path):
    """Verifies scheduler background trigger updates telemetry and blocks concurrent duplicate tasks."""
    import asyncio
    from app.services import facebook_scheduler

    monkeypatch.setattr(facebook_scheduler, "STATE_FILE", str(tmp_path / "fb_state.json"))
    monkeypatch.setattr(facebook_scheduler, "_publish_in_progress", False)
    monkeypatch.setattr(facebook_scheduler, "_background_publish_task", None)
    monkeypatch.setattr(
        facebook_scheduler,
        "_last_run_info",
        {
            "last_run_time": None,
            "last_posted_date": None,
            "status": "idle",
            "post_id": None,
            "error": None,
        },
    )

    calls = 0

    async def _fake_generate(target_date=None, rashi=None, dry_run=False, skip_if_already_posted=None):
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return {
            "success": True,
            "target_date": target_date,
            "total_attempted": 12,
            "successful_posts": 12,
            "newly_posted": 0,
            "skipped_existing": 12,
            "failed_posts": 0,
        }

    monkeypatch.setattr(facebook_scheduler, "generate_and_post_daily_raasi_palan", _fake_generate)

    async def _exercise():
        first = facebook_scheduler.trigger_background_publish(execution_date="2026-11-12", rashi="all")
        second = facebook_scheduler.trigger_background_publish(execution_date="2026-11-12", rashi="all")
        assert first["status"] == "queued"
        assert second["status"] == "already_running"
        await facebook_scheduler._background_publish_task
        status_snapshot = facebook_scheduler.get_scheduler_status()
        assert status_snapshot["in_progress"] is False
        assert status_snapshot["last_run"]["status"] == "success"
        assert status_snapshot["last_run"]["last_posted_date"] == "2026-11-12"
        assert status_snapshot["last_run"]["post_id"] == "12/12 posted (already on page)"

    asyncio.run(_exercise())
    assert calls == 1


def test_startup_catchup_syncs_state_without_reposting_when_all_12_on_facebook(monkeypatch, tmp_path):
    """Cold start after 06:00 AM IST without local state file does not re-post if Facebook already has 12/12."""
    import asyncio
    from app.config import settings
    from app.services import facebook_scheduler

    all_names = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ]
    state_file = tmp_path / "missing_state.json"
    monkeypatch.setattr(facebook_scheduler, "STATE_FILE", str(state_file))
    monkeypatch.setattr(settings, "fb_post_rashi", "all")
    monkeypatch.setattr(facebook_scheduler, "is_past_target_time", lambda *a, **kw: True)
    monkeypatch.setattr(
        facebook_scheduler,
        "_last_run_info",
        {
            "last_run_time": None,
            "last_posted_date": None,
            "status": "idle",
            "post_id": None,
            "error": None,
        },
    )

    async def _fake_fetch(target_date, **kwargs):
        return {name: {"post_id": f"fb_{name}", "fb_url": f"https://www.facebook.com/fb_{name}"} for name in all_names}

    async def _fail_if_executed(*args, **kwargs):
        raise AssertionError("_execute_daily_publish should not run when 12/12 already exist on Facebook")

    monkeypatch.setattr(facebook_scheduler, "fetch_posted_rashis_for_date", _fake_fetch)
    monkeypatch.setattr(facebook_scheduler, "_execute_daily_publish", _fail_if_executed)

    ran = asyncio.run(facebook_scheduler.run_startup_catchup_check())
    assert ran is True
    assert facebook_scheduler._last_run_info["status"] == "success"
    assert facebook_scheduler._last_run_info["post_id"] == "12/12 posted (already on page)"
    assert state_file.is_file()


def test_single_rashi_posts_text(monkeypatch):
    """Single-Rashi publish generates Tamil text post and publishes via post_to_facebook."""
    import asyncio
    from app.services import facebook_publisher

    posted_messages = []

    async def _fake_post_text(message, **kwargs):
        posted_messages.append(message)
        return {"success": True, "post_id": "fb_aries_txt", "fb_url": "https://www.facebook.com/fb_aries_txt"}

    monkeypatch.setattr(facebook_publisher, "post_to_facebook", _fake_post_text)

    res = asyncio.run(
        facebook_publisher.generate_and_post_daily_raasi_palan(
            target_date="2026-11-12",
            rashi="Aries",
            dry_run=False,
        )
    )
    assert res["success"] is True
    assert res["post_mode"] == "text"
    assert res["post_id"] == "fb_aries_txt"
    assert len(posted_messages) == 1
    assert "மேஷம் (Aries)" in posted_messages[0]
    assert "தினசரி ராசிபலன்" in posted_messages[0]


def test_post_all_12_publishes_all_rashis_as_text(monkeypatch):
    """Batch publishing posts all 12 Rashis as individual Tamil text posts."""
    import asyncio
    from app.services import facebook_publisher

    posted_messages = []

    async def _fake_fetch(target_date, **kwargs):
        return {}

    async def _fake_post_text(message, **kwargs):
        posted_messages.append(message)
        pid = f"fb_txt_{len(posted_messages)}"
        return {"success": True, "post_id": pid, "fb_url": f"https://www.facebook.com/{pid}"}

    monkeypatch.setattr(facebook_publisher, "fetch_posted_rashis_for_date", _fake_fetch)
    monkeypatch.setattr(facebook_publisher, "post_to_facebook", _fake_post_text)

    res = asyncio.run(
        facebook_publisher.post_all_12_raasi_palans(
            target_date="2026-11-12",
            delay_seconds=0,
            dry_run=False,
            skip_if_already_posted=True,
            post_mode="text",
        )
    )
    assert res["success"] is True
    assert res["post_mode"] == "text"
    assert res["total_attempted"] == 12
    assert res["successful_posts"] == 12
    assert res["newly_posted"] == 12
    assert res["failed_posts"] == 0
    assert len(posted_messages) == 12
    assert any("மேஷம்" in m for m in posted_messages)
    assert any("மீனம்" in m for m in posted_messages)

