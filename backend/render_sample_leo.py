import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from io import BytesIO
from pathlib import Path
from PIL import Image

from app.services.facebook_card_renderer import (
    draw_shaped_text,
    measure_shaped_width,
    wrap_shaped_text,
    format_tamil_date_prefix,
    format_aspect_text_ta,
    _to_tamil_star,
    _to_tamil_planet,
    _rasterize_pdf_to_png,
    _draw_stars_row,
    CARD_PT_WIDTH,
    CARD_PT_HEIGHT,
)
from app.services.kp_daily_horoscope_service import compute_kp_daily_horoscope

data = compute_kp_daily_horoscope("2026-11-13", rashi_filter="Leo")
p = data.predictions[0]

buf = BytesIO()
c = canvas.Canvas(buf, pagesize=(CARD_PT_WIDTH, CARD_PT_HEIGHT))

# 1. Base template canvas
base_path = Path("backend/app/assets/social/pristine_navy_gold_base_1080.png")
c.drawImage(ImageReader(str(base_path)), 0, 0, width=CARD_PT_WIDTH, height=CARD_PT_HEIGHT)

def pt_x(px: float) -> float:
    return px * (540.0 / 1080.0)

def pt_y(py: float) -> float:
    return (1350.0 - py) * (675.0 / 1350.0)

# Colors
c_ivory = colors.HexColor("#FFFFFF")
c_gold_bright = colors.HexColor("#F4CE6A")
c_gold_border = colors.HexColor("#D4AF37")
c_date_badge = colors.HexColor("#221608")

# 2. Top Right Date Badge
date_str_ta = format_tamil_date_prefix(data.date)
weekday_ta = data.day_of_week_ta
draw_shaped_text(c, date_str_ta, pt_x(725), pt_y(38), font_key="bold", font_size=7.6, color=c_date_badge, align="left")
draw_shaped_text(c, weekday_ta, pt_x(725), pt_y(58), font_key="bold", font_size=7.2, color=c_date_badge, align="left")

# 3. Hero Section
# Zodiac Medallion (left)
rashi_asset = Path(f"backend/app/assets/social/rashi_{p.rashi_id}.png")
if rashi_asset.is_file():
    c.drawImage(ImageReader(str(rashi_asset)), pt_x(35), pt_y(265), width=pt_x(230), height=pt_x(230), mask="auto")

# Tamil Rashi Name
draw_shaped_text(c, p.rashi_name_ta, pt_x(390), pt_y(105), font_key="bold", font_size=23.5, color=c_ivory, align="center")

# English Pill
c.saveState()
c.setFillColor(colors.HexColor("#E8B83D"))
c.roundRect(pt_x(335), pt_y(148), pt_x(110), pt_x(30), pt_x(15), stroke=0, fill=1)
c.restoreState()
draw_shaped_text(c, p.rashi_name_en.upper(), pt_x(390), pt_y(140), font_key="bold", font_size=10.0, color=colors.HexColor("#000000"), align="center")

# Score Circle
c.saveState()
c.setFillColor(colors.HexColor("#081224"))
c.setStrokeColor(c_gold_border)
c.setLineWidth(1.8)
c.circle(pt_x(555), pt_y(118), pt_x(48), stroke=1, fill=1)
c.setStrokeColor(c_gold_bright)
c.setLineWidth(0.8)
c.circle(pt_x(555), pt_y(118), pt_x(42), stroke=1, fill=0)
c.restoreState()
draw_shaped_text(c, f"{p.daily_score}%", pt_x(555), pt_y(110), font_key="bold", font_size=13.0, color=c_gold_bright, align="center")
draw_shaped_text(c, "சாதகம்", pt_x(555), pt_y(128), font_key="bold", font_size=6.8, color=c_ivory, align="center")

# Stars & Day Sentiment Pill
_draw_stars_row(c, pt_x(645), pt_y(92), p.daily_rating_stars, size=4.8)
draw_shaped_text(c, f"({int(round(p.daily_rating_stars))}/5)", pt_x(700), pt_y(112), font_key="regular", font_size=7.5, color=colors.HexColor("#CBD5E1"), align="center")

sentiment_text = "சாதகமான நாள்" if p.daily_score >= 60 else ("மிகச் சிறப்பு" if p.daily_score >= 80 else "கவனமான நாள்")
c.saveState()
c.setFillColor(colors.HexColor("#1A2946"))
c.setStrokeColor(colors.HexColor("#3B5B8C"))
c.setLineWidth(0.8)
c.roundRect(pt_x(632), pt_y(142), pt_x(136), pt_x(26), pt_x(13), stroke=1, fill=1)
c.restoreState()
draw_shaped_text(c, sentiment_text, pt_x(700), pt_y(135), font_key="bold", font_size=7.5, color=c_ivory, align="center")

# Transit details metadata
moon_star = _to_tamil_star(data.moon_star_at_noon)
sub_lord = _to_tamil_planet(data.moon_sub_lord_at_noon)
day_lord = _to_tamil_planet(data.day_lord)

transit_items = [
    ("★ நட்சத்திரம்", moon_star),
    ("🗝 உப-அதிபதி", sub_lord),
    ("🪐 சூரியன் பகவான்", "சூரியன்"),
    ("♀ தின அதிபதி", day_lord),
]
for idx, (label, val) in enumerate(transit_items):
    tx = 280 + idx * 135
    draw_shaped_text(c, label, pt_x(tx), pt_y(212), font_key="regular", font_size=6.2, color=c_gold_bright, align="center")
    draw_shaped_text(c, val, pt_x(tx), pt_y(232), font_key="bold", font_size=7.8, color=c_ivory, align="center")

# 4. Department assessment (5 rows)
row_py = [425, 481, 537, 593, 649]
bar_colors = [
    colors.HexColor("#38BDF8"),
    colors.HexColor("#FACC15"),
    colors.HexColor("#F472B6"),
    colors.HexColor("#34D399"),
    colors.HexColor("#A78BFA"),
]

for idx, aspect in enumerate(p.aspects[:5]):
    py = row_py[idx]
    cleaned = format_aspect_text_ta(aspect.insight_ta, aspect.key_recommendation_ta)
    wrapped = wrap_shaped_text(cleaned, "regular", 6.6, max_width=pt_x(430), max_lines=1)
    line_txt = wrapped[0] if wrapped else cleaned
    draw_shaped_text(c, line_txt, pt_x(385), pt_y(py), font_key="regular", font_size=6.6, color=c_ivory, align="left")
    
    # Percentage
    pct_str = f"{aspect.score}%"
    draw_shaped_text(c, pct_str, pt_x(840), pt_y(py), font_key="bold", font_size=8.2, color=c_ivory, align="right")
    
    # Progress Bar
    bw = pt_x(165)
    bh = pt_x(14)
    bx = pt_x(855)
    by = pt_y(py + 6)
    c.saveState()
    c.setFillColor(colors.HexColor("#1A2538"))
    c.roundRect(bx, by, bw, bh, bh/2.0, stroke=0, fill=1)
    fill_w = max(bh, bw * (aspect.score / 100.0))
    c.setFillColor(bar_colors[idx])
    c.roundRect(bx, by, fill_w, bh, bh/2.0, stroke=0, fill=1)
    c.restoreState()

# 5. Golden Hours & Caution Hours
golden_times = ", ".join(f"{w.start_time} - {w.end_time}" for w in p.moon_sub_windows if w.sentiment == "golden") or "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"
caution_times = ", ".join(f"{w.start_time} - {w.end_time}" for w in p.moon_sub_windows if w.sentiment == "caution") or "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"

draw_shaped_text(c, golden_times, pt_x(277), pt_y(782), font_key="bold", font_size=6.8, color=c_ivory, align="center")
draw_shaped_text(c, caution_times, pt_x(803), pt_y(782), font_key="bold", font_size=7.2, color=c_ivory, align="center")

# 6. Lucky Details
lucky_color = p.lucky_color_ta.split("&")[0].strip() if p.lucky_color_ta else "சிவப்பு"
lucky_num = str(p.lucky_number)
lucky_dir = p.lucky_direction_ta or "கிழக்கு"
lucky_gem = "மாணிக்கம்"

draw_shaped_text(c, lucky_color, pt_x(153), pt_y(948), font_key="bold", font_size=9.2, color=c_ivory, align="center")
draw_shaped_text(c, lucky_num, pt_x(411), pt_y(948), font_key="bold", font_size=9.2, color=c_ivory, align="center")
draw_shaped_text(c, lucky_dir, pt_x(669), pt_y(948), font_key="bold", font_size=9.2, color=c_ivory, align="center")
draw_shaped_text(c, lucky_gem, pt_x(927), pt_y(938), font_key="bold", font_size=9.2, color=c_ivory, align="center")
draw_shaped_text(c, "(சூரிய பலம் பெற அணியலாம்)", pt_x(927), pt_y(954), font_key="regular", font_size=5.4, color=colors.HexColor("#CBD5E1"), align="center")

# 7. Remedy Bullets
rem_lines = [
    "காலை நேரத்தில் சூரிய நமஸ்காரம் செய்யவும்.",
    "\"ஓம் சூர்யாய நம:\" - 11 முறை ஜபிக்கவும்.",
    "சிவாலயத்தில் தீபம் ஏற்றி வழிபடுவது மனநிலையை அமைதியாக்கும்.",
]
bullet_y = [1075, 1115, 1155]
for idx, b_txt in enumerate(rem_lines):
    draw_shaped_text(c, f"•  {b_txt}", pt_x(345), pt_y(bullet_y[idx]), font_key="regular", font_size=7.8, color=c_ivory, align="left")

# 8. Footer Slide Pill
slide_txt = "ராசி 5 / 12"
draw_shaped_text(c, slide_txt, pt_x(958), pt_y(1248), font_key="bold", font_size=8.5, color=colors.HexColor("#000000"), align="center")

c.showPage()
c.save()

png_out = _rasterize_pdf_to_png(buf.getvalue())
preview_path = Path("backend/app/assets/social/sample_leo_preview.png")
with open(preview_path, "wb") as f:
    f.write(png_out)

with open("C:/Users/Gokul Murugan/.gemini/antigravity/brain/22f317b7-1821-4ecc-a633-15839561e733/sample_leo_preview.png", "wb") as f:
    f.write(png_out)

print(f"Pristine Leo preview generated cleanly ({len(png_out)} bytes)!")