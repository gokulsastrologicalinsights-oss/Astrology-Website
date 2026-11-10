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
