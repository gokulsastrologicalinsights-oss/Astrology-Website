"""Daily Rasi Palan 1:1 Square Image Poster Generator.

Generates high-resolution (1080 x 1080) social-media-ready Tamil infographic posters
for daily horoscope broadcasts across Facebook, Instagram, and WhatsApp.
"""

from __future__ import annotations

import logging
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple

from app.schemas.kp_daily_horoscope import KpDailyHoroscopeResponse, RashiDailyPrediction

logger = logging.getLogger("gai.daily_poster")

RASHI_SYMBOLS: Dict[int, str] = {
    1: "♈", 2: "♉", 3: "♊", 4: "♋",
    5: "♌", 6: "♍", 7: "♎", 8: "♏",
    9: "♐", 10: "♑", 11: "♒", 12: "♓"
}

RASHI_RULERS_TA: Dict[int, str] = {
    1: "செவ்வாய் ஆட்சி",
    2: "சுக்கிரன் ஆட்சி",
    3: "புதன் ஆட்சி",
    4: "சந்திரன் ஆட்சி",
    5: "சூரியன் ஆட்சி",
    6: "புதன் ஆட்சி",
    7: "சுக்கிரன் ஆட்சி",
    8: "செவ்வாய் ஆட்சி",
    9: "குரு ஆட்சி",
    10: "சனி ஆட்சி",
    11: "சனி ஆட்சி",
    12: "குரு ஆட்சி"
}

SENTIMENT_MAP_TA: Dict[str, str] = {
    "Excellent": "மிகச் சிறப்பான நாள்",
    "Favorable": "சாதகமான நாள்",
    "Mixed": "மிதமான நாள்",
    "Challenging": "கவனமான நாள்",
}

EDGE_PATHS = [
    # Windows
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # Linux / Docker / Cloud (Ubuntu / Render / GitHub Actions)
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
]


def find_browser_executable() -> str:
    for p in EDGE_PATHS:
        if os.path.isfile(p):
            return p
    for cmd in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge"):
        found = shutil.which(cmd)
        if found:
            return found
    raise FileNotFoundError("Browser executable (Chrome/Chromium/Edge) not found for poster rendering.")


def clean_brief_ta(text: str) -> str:
    """Strips technical sign and transit prefix (e.g., 'கன்னி (7-ம் இடத்தில்...):') from brief statement."""
    if not text:
        return "இன்றைய நாள் நற்பலன்களைத் தரும்."
    cleaned = re.sub(r"^.*?\):\s*", "", text).strip(" \"'")
    return cleaned or text


def clean_aspect_text(rec: str, insight: str) -> str:
    """Extracts concise, natural Tamil advice without technical jargon."""
    raw = (rec or insight or "சாதகமான பலன் உண்டு.").strip()
    clean = re.sub(r"(?:KP\s*பாவகங்கள்|(?:\d+(?:\s*அல்லது\s*\d+)?|\[[\d,\s]+\]|\{houses\}|\d+(?:,\s*\d+)*)-ம்\s*பாவக[^.;]*[.;]?)", "", raw, flags=re.IGNORECASE)
    clean = re.sub(r"\s+", " ", clean).strip(" -•–")
    # Cap to ~90 characters so it wraps smoothly into 2 clean lines without cut-off
    if len(clean) > 92:
        clean = clean[:89].rsplit(" ", 1)[0] + "..."
    return clean or "சாதகமான பலன் உண்டு."


def build_rashi_square_html(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
) -> str:
    glyph = RASHI_SYMBOLS.get(prediction.rashi_id, "✨")
    ruler = RASHI_RULERS_TA.get(prediction.rashi_id, "")
    sentiment_ta = SENTIMENT_MAP_TA.get(prediction.day_sentiment, prediction.day_sentiment)
    stars = int(round(prediction.daily_rating_stars)) if prediction.daily_rating_stars else 3

    golden_times = (
        ", ".join(
            f"{w.start_time}–{w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "golden"
        )
        or (prediction.golden_hour_window.replace(" - ", "–") if prediction.golden_hour_window else "")
        or "வழக்கமான நற்பலன் நேரம்"
    )

    caution_times = (
        ", ".join(
            f"{w.start_time}–{w.end_time}"
            for w in prediction.moon_sub_windows
            if w.sentiment == "caution"
        )
        or (prediction.caution_hour_window.replace(" - ", "–") if prediction.caution_hour_window else "")
        or "குறிப்பிடத்தக்க எச்சரிக்கை இல்லை"
    )

    lucky_color = prediction.lucky_color_ta.split("&")[0].strip() if prediction.lucky_color_ta else "மஞ்சள்"
    lucky_num = prediction.lucky_number or 3
    lucky_dir = prediction.lucky_direction_ta or "வடக்கு"

    aspects = prediction.aspects[:4] if prediction.aspects else []
    aspect_colors = [
        ("#38bdf8", "#0284c7"),
        ("#facc15", "#ca8a04"),
        ("#f472b6", "#db2777"),
        ("#4ade80", "#16a34a"),
    ]

    aspect_cards_html = ""
    for idx, asp in enumerate(aspects):
        c_fill, c_grad = aspect_colors[idx % len(aspect_colors)]
        short_rec = clean_aspect_text(asp.key_recommendation_ta, asp.insight_ta)
        aspect_cards_html += f"""
        <div class="aspect-card">
          <div class="aspect-header">
            <span>{asp.aspect_name_tamil}</span>
            <span class="aspect-pct" style="color: {c_fill};">{asp.score}%</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill" style="width: {asp.score}%; background: linear-gradient(90deg, {c_grad}, {c_fill});"></div>
          </div>
          <div class="aspect-hint">{short_rec}</div>
        </div>
        """

    brief = clean_brief_ta(prediction.brief_statement_ta)

    remedy = (prediction.daily_remedy_ta or "இறை வழிபாடு செய்து நற்பலன்களைப் பெறவும்.").strip()

    return f"""<!DOCTYPE html>
<html lang="ta">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Mukta+Malar:wght@400;500;600;700;800&family=Noto+Sans+Tamil:wght@400;500;600;700;800;900&display=swap');

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    width: 1080px;
    height: 1080px;
    background-color: #080c16;
    font-family: 'Noto Sans Tamil', 'Mukta Malar', 'Nirmala UI', sans-serif;
    color: #e2e8f0;
    overflow: hidden;
    position: relative;
  }}

  .bg-ambient {{
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 10%, #171c3d 0%, #0a0e1c 55%, #050711 100%);
    z-index: 1;
  }}

  .glow-top {{
    position: absolute;
    top: -80px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 250px;
    background: radial-gradient(circle, rgba(234, 179, 8, 0.12) 0%, transparent 70%);
    filter: blur(40px);
    z-index: 2;
  }}

  .outer-frame {{
    position: absolute;
    inset: 18px;
    border: 1px solid rgba(234, 179, 8, 0.22);
    border-radius: 20px;
    pointer-events: none;
    z-index: 4;
  }}

  .container {{
    position: relative;
    z-index: 3;
    width: 1080px;
    height: 1080px;
    padding: 28px 34px 22px 34px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5px solid rgba(255, 255, 255, 0.12);
    padding-bottom: 12px;
  }}

  .date-badge {{
    font-size: 22px;
    font-weight: 700;
    color: #e2e8f0;
  }}

  .brand-pill {{
    padding: 6px 20px;
    background: rgba(234, 179, 8, 0.18);
    border: 1.5px solid rgba(234, 179, 8, 0.55);
    border-radius: 20px;
    color: #fde047;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 0.5px;
  }}

  .sign-hero {{
    background: #111827;
    border: 2px solid rgba(234, 179, 8, 0.45);
    border-radius: 20px;
    padding: 16px 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
  }}

  .sign-left {{
    display: flex;
    align-items: center;
    gap: 20px;
  }}

  .zodiac-glyph {{
    font-size: 68px;
    color: #fbbf24;
    line-height: 1;
    text-shadow: 0 0 18px rgba(251, 191, 36, 0.55);
  }}

  .sign-name {{
    font-size: 48px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: 0.5px;
  }}

  .sign-english {{
    font-size: 21px;
    color: #cbd5e1;
    font-weight: 700;
    margin-top: 3px;
  }}

  .score-badge {{
    text-align: right;
    background: rgba(22, 101, 52, 0.45);
    border: 2px solid rgba(74, 222, 128, 0.6);
    border-radius: 18px;
    padding: 12px 24px;
  }}

  .score-val {{
    font-size: 38px;
    font-weight: 900;
    color: #4ade80;
    line-height: 1;
  }}

  .score-label {{
    font-size: 17.5px;
    font-weight: 800;
    color: #86efac;
    margin-top: 4px;
  }}

  .outlook-box {{
    background: rgba(15, 23, 42, 0.85);
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 14px 22px;
    font-size: 21px;
    line-height: 1.5;
    color: #f8fafc;
  }}

  .outlook-box strong {{
    color: #fde047;
    font-size: 22px;
  }}

  .aspects-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}

  .aspect-card {{
    background: #111827;
    border: 1.5px solid rgba(255, 255, 255, 0.11);
    border-radius: 16px;
    padding: 12px 18px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }}

  .aspect-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 6px;
    color: #ffffff;
  }}

  .aspect-pct {{
    font-weight: 900;
    font-size: 23px;
  }}

  .meter-bar {{
    width: 100%;
    height: 9px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
  }}

  .meter-fill {{
    height: 100%;
    border-radius: 6px;
  }}

  .aspect-hint {{
    font-size: 17.5px;
    color: #e2e8f0;
    line-height: 1.45;
    word-break: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 48px;
    font-weight: 600;
  }}

  .timing-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}

  .timing-card {{
    background: #111827;
    border: 1.5px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}

  .timing-icon {{
    font-size: 34px;
    line-height: 1;
  }}

  .timing-label {{
    font-size: 16px;
    color: #94a3b8;
    font-weight: 700;
  }}

  .timing-val {{
    font-size: 19px;
    font-weight: 800;
    color: #f8fafc;
    margin-top: 2px;
  }}

  .lucky-strip {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }}

  .lucky-pill {{
    background: #111827;
    border: 1.5px solid rgba(234, 179, 8, 0.32);
    border-radius: 16px;
    padding: 10px 8px;
    text-align: center;
  }}

  .lucky-title {{
    font-size: 16px;
    color: #94a3b8;
    font-weight: 700;
  }}

  .lucky-text {{
    font-size: 22px;
    font-weight: 900;
    color: #fde047;
    margin-top: 2px;
  }}

  .remedy-strip {{
    background: linear-gradient(135deg, rgba(88, 28, 135, 0.3) 0%, rgba(30, 27, 75, 0.5) 100%);
    border: 1.5px solid rgba(192, 132, 252, 0.4);
    border-radius: 16px;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}

  .remedy-icon {{
    font-size: 36px;
    line-height: 1;
  }}

  .remedy-body {{
    font-size: 18.5px;
    line-height: 1.45;
    color: #f8fafc;
  }}

  .remedy-body strong {{
    color: #d8b4fe;
    font-size: 20px;
  }}

  .footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1.5px solid rgba(255, 255, 255, 0.12);
    padding-top: 10px;
  }}

  .footer-brand {{
    font-size: 19.5px;
    font-weight: 800;
    color: #fde047;
  }}

  .footer-sub {{
    font-size: 16.5px;
    color: #cbd5e1;
    font-weight: 600;
  }}
</style>
</head>
<body>

<div class="bg-ambient"></div>
<div class="glow-top"></div>
<div class="outer-frame"></div>

<div class="container">

  <div class="top-bar">
    <div class="date-badge">🗓️ {horoscope_data.date} – {horoscope_data.day_of_week_ta}</div>
    <div class="brand-pill">தினசரி ராசிபலன்</div>
  </div>

  <div class="sign-hero">
    <div class="sign-left">
      <div class="zodiac-glyph">{glyph}</div>
      <div>
        <div class="sign-name">{prediction.rashi_name_ta}</div>
        <div class="sign-english">{prediction.rashi_name_en} • {ruler}</div>
      </div>
    </div>
    <div class="score-badge">
      <div class="score-val">{prediction.daily_score}%</div>
      <div class="score-label">{stars} / 5 {sentiment_ta}</div>
    </div>
  </div>

  <div class="outlook-box">
    🔮 <strong>இன்றைய சுருக்கம்:</strong> {brief}
  </div>

  <div class="aspects-grid">
    {aspect_cards_html}
  </div>

  <div class="timing-grid">
    <div class="timing-card">
      <div class="timing-icon">🌟</div>
      <div>
        <div class="timing-label">அதிர்ஷ்ட நேரம்</div>
        <div class="timing-val">{golden_times}</div>
      </div>
    </div>
    <div class="timing-card">
      <div class="timing-icon">⚠️</div>
      <div>
        <div class="timing-label">கவனமான நேரம்</div>
        <div class="timing-val">{caution_times}</div>
      </div>
    </div>
  </div>

  <div class="lucky-strip">
    <div class="lucky-pill">
      <div class="lucky-title">🎨 நிறம்</div>
      <div class="lucky-text">{lucky_color}</div>
    </div>
    <div class="lucky-pill">
      <div class="lucky-title">🔢 எண்</div>
      <div class="lucky-text">{lucky_num}</div>
    </div>
    <div class="lucky-pill">
      <div class="lucky-title">🧭 திசை</div>
      <div class="lucky-text">{lucky_dir}</div>
    </div>
  </div>

  <div class="remedy-strip">
    <div class="remedy-icon">🪔</div>
    <div class="remedy-body">
      <strong>இன்றைய பரிகாரம்:</strong> {remedy}
    </div>
  </div>

  <div class="footer">
    <div class="footer-brand">🙏 Gokul's Astrological Insights</div>
    <div class="footer-sub">Gokul Murugan | Thiruverkadu</div>
  </div>

</div>

</body>
</html>"""


def generate_single_poster(
    horoscope_data: KpDailyHoroscopeResponse,
    prediction: RashiDailyPrediction,
    output_dir: str,
    temp_user_data: Optional[str] = None,
) -> str:
    """Renders a single Rashi's 1080x1080 PNG poster and returns its path."""
    os.makedirs(output_dir, exist_ok=True)
    browser_bin = find_browser_executable()
    default_temp = tempfile.gettempdir()
    user_data = temp_user_data or os.path.join(default_temp, "rasipalan_render_profile")
    os.makedirs(user_data, exist_ok=True)

    html_path = os.path.join(output_dir, f"rashi_{prediction.rashi_id}_{prediction.rashi_name_en.lower()}.html")
    png_path = os.path.join(output_dir, f"rashi_{prediction.rashi_id}_{prediction.rashi_name_en.lower()}.png")

    html_content = build_rashi_square_html(horoscope_data, prediction)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_url = pathlib.Path(html_path).resolve().as_uri()
    cmd = [
        browser_bin,
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={user_data}",
        f"--screenshot={png_path}",
        "--window-size=1080,1080",
        "--hide-scrollbars",
        file_url,
    ]

    res = subprocess.run(cmd, capture_output=True, timeout=45)
    if not os.path.isfile(png_path):
        err_msg = res.stderr.decode("utf-8", errors="ignore") if res.stderr else "Unknown browser error"
        raise RuntimeError(f"Failed to render poster for Rashi {prediction.rashi_id}: {err_msg}")

    return png_path


def generate_all_12_posters(
    horoscope_data: KpDailyHoroscopeResponse,
    output_dir: Optional[str] = None,
) -> List[Tuple[int, str, str, str]]:
    """Generates 1:1 posters for all 12 Rashis. Returns list of (rashi_id, name_ta, name_en, png_path)."""
    base_dir = output_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "generated_posters",
        horoscope_data.date,
    )
    os.makedirs(base_dir, exist_ok=True)

    results = []
    for prediction in horoscope_data.predictions:
        png_file = generate_single_poster(horoscope_data, prediction, base_dir)
        results.append((prediction.rashi_id, prediction.rashi_name_ta, prediction.rashi_name_en, png_file))
        logger.info(f"Rendered poster for {prediction.rashi_name_ta} ({prediction.rashi_name_en}) -> {png_file}")

    return results
