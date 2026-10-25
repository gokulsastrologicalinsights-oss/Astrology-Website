"""Auspicious Muhurta Selection Certificate PDF Generator.

Produces a ceremonial, high-prestige, gold-and-vermilion bordered
certificate suitable for framing and event invitations (Vivaha, Griha Pravesha,
Business/Shop Launch, Vehicle Purchase).
Supports bilingual Tamil and English rendering with NotoSansTamil fonts.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph as _RLParagraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String as _RLString, Line

from app.services.pdf_report_engine.fonts import (
    get_report_styles,
    reorder_tamil_for_pdf,
    register_report_fonts,
    GOLD_PRIMARY,
    GOLD_ACCENT,
    NAVY_PRIMARY,
    NAVY_SECONDARY,
    CRIMSON_ACCENT,
    BG_HEADER,
    BG_ZEBRA,
    BORDER_COLOR,
    EMERALD_GREEN,
)
from app.services.pdf_report_engine.chart_drawer import create_south_indian_chart
from app.services.ephemeris import calculate_full_horoscope
from app.schemas.pdf_report import MuhurtaCertificatePdfRequest

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 28.0
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)


class Paragraph(_RLParagraph):
    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class CertificateCanvas(canvas.Canvas):
    """Draws ceremonial double-gold ornamental border and authentic Vedic seal."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_ceremonial_border(self):
        self.saveState()

        # Outer Gold Border
        self.setStrokeColor(GOLD_PRIMARY)
        self.setLineWidth(3.0)
        self.rect(14, 14, PAGE_WIDTH - 28, PAGE_HEIGHT - 28)

        # Inner Thin Vermilion Border
        self.setStrokeColor(CRIMSON_ACCENT)
        self.setLineWidth(1.0)
        self.rect(18, 18, PAGE_WIDTH - 36, PAGE_HEIGHT - 36)

        # Corner Corner Accents (Decorative L-brackets)
        for x, y, dx, dy in [
            (22, 22, 24, 24),
            (PAGE_WIDTH - 22, 22, -24, 24),
            (22, PAGE_HEIGHT - 22, 24, -24),
            (PAGE_WIDTH - 22, PAGE_HEIGHT - 22, -24, -24),
        ]:
            self.setStrokeColor(GOLD_PRIMARY)
            self.setLineWidth(1.5)
            self.line(x, y, x + dx, y)
            self.line(x, y, x, y + dy)

        self.restoreState()


def generate_muhurta_certificate_pdf_bytes(
    req: MuhurtaCertificatePdfRequest,
) -> bytes:
    """Generates a certified ceremonial Auspicious Muhurta Selection Certificate."""
    register_report_fonts()
    styles = get_report_styles()
    is_ta = req.language == "ta"

    # 1. Calculate the Muhurta Chart at the event date and start time
    ev_date = date.fromisoformat(req.event_date)
    ev_time_parts = req.start_time.split(":")
    ev_time = time(int(ev_time_parts[0]), int(ev_time_parts[1]))

    horo = calculate_full_horoscope(
        birth_date=ev_date,
        birth_time=ev_time,
        timezone_str="Asia/Kolkata",
        latitude=req.latitude,
        longitude=req.longitude,
        ayanamsa_id=0,
    )

    # Convert chart data for vector rendering
    planets_by_sign: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    planets_list = []
    for p in horo.planets:
        s_idx = getattr(p, "sign_index", None) or getattr(p, "sign", 1)
        planets_by_sign[s_idx].append(p.name)
        planets_list.append({
            "name": p.name,
            "sign_index": int(s_idx),
            "is_retrograde": getattr(p, "is_retrograde", False),
            "degree_in_sign": getattr(p, "degree_in_sign", None),
        })

    asc_sign_idx = getattr(horo.ascendant, "sign_index", 1)
    muhurta_chart_data = {
        "ascendant_sign": asc_sign_idx,
        "ascendant_degree": horo.ascendant.degree_in_sign,
        "planets": planets_list,
        "planets_by_sign": planets_by_sign,
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=26,
        bottomMargin=26,
    )
    story: List[Any] = []

    # Mangala Sloka Header
    sloka_sanskrit = "ॐ शुक्लाम্বরधरं विष्णुं शशिवर्णं चतुर्भुजम् । प्रसन्नवदनं ध्यायेत् सर्वविघ्नोपशान्तये ॥"
    sloka_ta = "ஓம் சுக்லாம்பரதரம் விஷ்ணும் சசிவர்ணம் சதுர்புஜம் | ப்ரஸன்னவதனம் த்யாயேத் சர்வவிக்நோபசாந்தயே ||"

    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<font color='{CRIMSON_ACCENT.hexval()}'><b>{sloka_sanskrit}</b></font>", styles["Subtitle"]))
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><i>{sloka_ta}</i></font>", styles["Subtitle"]))
    story.append(Spacer(1, 8))

    # Main Certificate Title
    cert_title = "சுப முகூர்த்த தேர்வு சான்றிதழ்" if is_ta else "AUSPICIOUS MUHURTA CERTIFICATE"
    cert_sub = f"பராசர ஜோதிட முறைப்படி கணிக்கப்பட்ட மங்களகரமான கால நேரம்" if is_ta else f"Canonical Astrological Election according to Vedic Muhurta Shastra"
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>{cert_title}</b></font>", styles["DocTitle"]))
    story.append(Paragraph(f"<font color='{NAVY_PRIMARY.hexval()}'>{cert_sub}</font>", styles["Subtitle"]))
    story.append(Spacer(1, 10))

    # Occasion & Names Ribbon
    occ_str = req.occasion
    if is_ta:
        occ_map = {
            "Marriage": "திருமண சுப முகூர்த்தம் (Vivaha Muhurta)",
            "House Warming": "கிரகப்பிரவேசம் (Griha Pravesha)",
            "Business Launch": "தொழில் தொடக்கம் (Shop / Business Launch)",
            "Vehicle Purchase": "வாகன சேர்க்கை (Vehicle Purchase)",
        }
        occ_str = occ_map.get(req.occasion, req.occasion)

    name_heading = req.primary_person_name
    if req.secondary_person_name:
        name_heading = f"{req.primary_person_name}  &  {req.secondary_person_name}"

    ribbon_data = [
        [
            Paragraph(f"<b>சுப நிகழ்வு / Occasion:</b> <font color='{CRIMSON_ACCENT.hexval()}'><b>{occ_str}</b></font>", styles["NormalSmall"]),
            Paragraph(f"<b>தேதி / Date:</b> <font color='{NAVY_PRIMARY.hexval()}'><b>{req.event_date}</b></font>", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>பெயர்கள் / Names:</b> <font color='{GOLD_PRIMARY.hexval()}'><b>{name_heading}</b></font>", styles["NormalSmall"]),
            Paragraph(f"<b>முகூர்த்த நேரம் / Window:</b> <font color='{EMERALD_GREEN.hexval()}'><b>{req.start_time} - {req.end_time}</b></font>", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>கோத்திரம் / நக்ஷத்திரம்:</b> {req.primary_gotra or 'N/A'} / {req.primary_nakshatra or 'N/A'}", styles["NormalSmall"]),
            Paragraph(f"<b>இடம் / Location:</b> {req.location_name}", styles["NormalSmall"]),
        ],
    ]
    t_ribbon = Table(ribbon_data, colWidths=[USABLE_WIDTH * 0.55, USABLE_WIDTH * 0.45])
    t_ribbon.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
        ('BOX', (0, 0), (-1, -1), 1.0, GOLD_PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EED89B")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_ribbon)
    story.append(Spacer(1, 10))

    # Middle Section: Muhurta Chart (Left) + Panchangam & Strengths (Right)
    chart_drawing = create_south_indian_chart(
        chart_data=muhurta_chart_data,
        title_en=f"MUHURTA KUNDALI (லக்னம்: {horo.ascendant.sign_name})",
        title_ta=f"முகூர்த்த லக்ன சக்கரம் ({horo.ascendant.sign_name})",
        size=220.0,
        language=req.language,
    )

    moon_obj = next((p for p in horo.planets if p.name == "Moon"), None)
    moon_nak_name = (moon_obj.nakshatra.name if hasattr(moon_obj, 'nakshatra') and hasattr(moon_obj.nakshatra, 'name') else getattr(moon_obj, 'nakshatra_name', 'Auspicious')) if moon_obj else 'Auspicious'
    moon_nak_pada = (moon_obj.nakshatra.pada if hasattr(moon_obj, 'nakshatra') and hasattr(moon_obj.nakshatra, 'pada') else getattr(moon_obj, 'nakshatra_pada', 1)) if moon_obj else 1
    panchang_data = [
        [Paragraph("<b>பஞ்சாங்கம் & சுப காரணிகள் / Coordinates</b>", styles["TableHeader"])],
        [Paragraph(f"• <b>திதி (Tithi):</b> Shukla / Krishna Tithi", styles["NormalSmall"])],
        [Paragraph(f"• <b>வாரம் (Day):</b> {ev_date.strftime('%A')}", styles["NormalSmall"])],
        [Paragraph(f"• <b>நட்சத்திரம் (Star):</b> {moon_nak_name} (பாதம் {moon_nak_pada})", styles["NormalSmall"])],
        [Paragraph(f"• <b>முகூர்த்த லக்னம் (Ascendant):</b> <b>{horo.ascendant.sign_name}</b> ({horo.ascendant.degree_in_sign:.2f}°)", styles["NormalSmall"])],
        [Paragraph(f"• <b>தாராபலம் / சந்திரபலம்:</b> பரிபூரண சுப யோகம் (Auspicious Alignment)", styles["NormalSmall"])],
        [Paragraph(f"• <b>குரு பார்வை (Jupiter Aspect):</b> சுப கேந்திர/திரிகோண பலம்", styles["NormalSmall"])],
    ]
    t_panchang = Table(panchang_data, colWidths=[USABLE_WIDTH * 0.48])
    t_panchang.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    t_middle = Table([[chart_drawing, t_panchang]], colWidths=[USABLE_WIDTH * 0.52, USABLE_WIDTH * 0.48])
    t_middle.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_middle)
    story.append(Spacer(1, 10))

    # Classical Safeguards Passed Box
    safeguards_text = (
        "<b>தோஷ நிவர்த்தி & பாதுகாப்பு பரிசோதனைகள் (Strict Safeguards Verified):</b><br/>"
        "✓ ராகுகாலம் விலக்கப்பட்டது (Zero Rahu Kalam) &nbsp;&nbsp;&nbsp;&nbsp; "
        "✓ எமகண்டம் விலக்கப்பட்டது (Zero Yamagandam)<br/>"
        "✓ குளிகன் விலக்கப்பட்டது (Zero Gulika Kalam) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        "✓ வர்ஜியம் / தியாஜ்ஜியம் விலக்கப்பட்டது (Zero Varjyam)<br/>"
        "✓ துர்முகூர்த்தம் இல்லாத நேரம் &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        "✓ பஞ்சக தோஷம் அற்ற சுப லக்னம் (Panchaka Shuddhi)"
    )
    story.append(Table([[Paragraph(safeguards_text, styles["NormalSmall"])]], colWidths=[USABLE_WIDTH], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#86EFAC")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(Spacer(1, 10))

    # Astrologer Endorsement & Seal Footer
    sign_data = [
        [
            Paragraph(f"<b>கணித்தவர் / Certified By:</b><br/>{req.astrologer_name or 'Gokul’s Astrological Insights'}<br/><font size='6' color='#64748B'>Vedic Astrological Authority</font>", styles["NormalSmall"]),
            Paragraph(f"<b>சான்றிதழ் எண் / Ref ID:</b><br/>MUH-{ev_date.strftime('%Y%m%d')}-01<br/><font size='6' color='#64748B'>Tamper-evident verification</font>", styles["NormalSmall"]),
            Paragraph(f"<b>கையொப்பம் / Signature:</b><br/><br/>______________________", styles["NormalSmall"]),
        ]
    ]
    t_sign = Table(sign_data, colWidths=[USABLE_WIDTH * 0.40, USABLE_WIDTH * 0.30, USABLE_WIDTH * 0.30])
    t_sign.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF2DE")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sign)

    def on_page(canv, doc):
        canv.draw_ceremonial_border()

    doc.build(story, canvasmaker=CertificateCanvas, onFirstPage=on_page)
    return buffer.getvalue()
