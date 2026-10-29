"""Remedial Gemstone & Rudraksha Sanctification Playbook PDF Generator.

Produces an authoritative, beautifully designed 3-page personalized playbook
explaining Anukula Vada vs Pratikula Shanti, the 3-Pillar + Yogakaraka gemstones,
body weight proportional Carat/Ratti formulas, consecration mantras, strict Dusthana
prohibitions, and personalized 1-to-14 Mukhi Rudraksha Prana Pratishtha rituals.
Supports bilingual English and Tamil rendering with NotoSansTamil fonts.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph as _RLParagraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.pdfgen import canvas

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
from app.services.remedy_engine.gemstone_advisory import GemstoneAdvisoryEngine
from app.schemas.pdf_report import GemstoneRudrakshaPlaybookPdfRequest

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36.0
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)


class Paragraph(_RLParagraph):
    def __init__(self, text: Any, *args, **kwargs):
        super().__init__(reorder_tamil_for_pdf(text), *args, **kwargs)


class PlaybookNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        if self._pageNumber > 1:
            try:
                self.setFont("NotoSansTamil-Bold", 7.5)
            except Exception:
                self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(GOLD_PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 26, reorder_tamil_for_pdf("Gokul's Astrological Insights | ரத்தின & ருத்ராட்ச கையேடு"))

            try:
                self.setFont("NotoSansTamil", 7.0)
            except Exception:
                self.setFont("Helvetica", 7.0)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "Sanctification & Safety Playbook")

            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 30, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 30)

        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(MARGIN, 26, PAGE_WIDTH - MARGIN, 26)

        try:
            self.setFont("NotoSansTamil", 6.8)
        except Exception:
            self.setFont("Helvetica", 6.8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(MARGIN, 16, "© Gokul's Astrological Insights • Classical Ratna Shastra (Ratna Samadhan - Grahabalabal Method & Shiva Purana)")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 16, page_str)
        self.restoreState()


def generate_gemstone_rudraksha_playbook_pdf_bytes(
    req: GemstoneRudrakshaPlaybookPdfRequest,
) -> bytes:
    """Calculates the full gemstone & rudraksha prescription and compiles a 3-page personalized playbook."""
    register_report_fonts()
    styles = get_report_styles()
    is_ta = req.language == "ta"

    adv = GemstoneAdvisoryEngine.evaluate_advisory(
        lagna_sign=req.ascendant_sign,
        moon_sign=req.moon_sign,
        running_mahadasha=req.running_mahadasha,
        running_bhukti=req.running_bhukti,
        body_weight_kg=req.body_weight_kg,
        has_kuja_dosha=req.has_kuja_dosha,
        has_sade_sati=req.has_sade_sati,
        has_kaal_sarp=req.has_kaal_sarp,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=38,
        bottomMargin=36,
    )
    story: List[Any] = []

    # --------------------------------------------------------------------------
    # PAGE 1: COVER, DOCTRINE & PILLARS 1 & 2
    # --------------------------------------------------------------------------
    doc_title = "ரத்தின & ருத்ராட்ச சாஸ்திர புனிதக் கையேடு (ரத்ன சமாதானம்)" if is_ta else "REMEDIAL GEMSTONE & RUDRAKSHA SANCTIFICATION PLAYBOOK (RATNA SAMADHAN)"
    doc_sub = "அனுகூல vs பிரதிகூல ரத்தின முறை, கிரகபலபலம் நெறிமுறை, யோககாரக ஆதரவு & ருத்ராட்ச பிரதிஷ்டை" if is_ta else "Classical Anukula Vada vs Pratikula Shanti, Grahabalabal Method, Yogakaraka Gems & Sanctification"

    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>{doc_title}</b></font>", styles["DocTitle"]))
    story.append(Paragraph(f"<font color='{NAVY_SECONDARY.hexval()}'>{doc_sub}</font>", styles["Subtitle"]))
    story.append(Spacer(1, 8))

    # Native Bio Header
    bio_data = [
        [
            Paragraph(f"<b>பெயர் / Native:</b> {req.native_name}", styles["NormalSmall"]),
            Paragraph(f"<b>லக்னம் / Ascendant:</b> <font color='{CRIMSON_ACCENT.hexval()}'><b>{adv.lagna_sign}</b></font>", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>உடல் எடை / Body Weight:</b> <b>{req.body_weight_kg:.1f} kg</b>", styles["NormalSmall"]),
            Paragraph(f"<b>சந்திர ராசி / Moon Sign:</b> {adv.moon_sign or 'N/A'}", styles["NormalSmall"]),
        ],
        [
            Paragraph(f"<b>தற்போதைய தசை / Dasha:</b> {adv.running_mahadasha or 'N/A'}", styles["NormalSmall"]),
            Paragraph(f"<b>சாஸ்திர விதி / Canon:</b> Ratna Samadhan (Grahabalabal) & Shiva Purana", styles["NormalSmall"]),
        ],
    ]
    t_bio = Table(bio_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    t_bio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_bio)
    story.append(Spacer(1, 8))

    # Anukula vs Pratikula Shastra Manifesto Box
    doctrine_p = adv.anukula_vs_pratikula_doctrine_ta["core_principle"] if is_ta else adv.anukula_vs_pratikula_doctrine_en["core_principle"]
    manifesto_box = [
        [Paragraph(f"<b>அனுகூல vs பிரதிகூல சாஸ்திர விதி (The Golden Rule of Vedic Gemology):</b><br/>{doctrine_p}", styles["NormalSmall"])],
    ]
    t_man = Table(manifesto_box, colWidths=[USABLE_WIDTH])
    t_man.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
        ('BOX', (0, 0), (-1, -1), 0.8, GOLD_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_man)
    story.append(Spacer(1, 10))

    # Helper function to render a Gemstone Table Entry
    def render_gem_block(rec: Any, title_badge_en: str, title_badge_ta: str) -> Table:
        badge = title_badge_ta if is_ta else title_badge_en
        gem_name = rec.primary_gem_ta if is_ta else rec.primary_gem_en
        metal = rec.prescribed_metal_ta if is_ta else rec.prescribed_metal_en
        finger = rec.ideal_finger_ta if is_ta else rec.ideal_finger_en
        day = rec.energization_day_ta if is_ta else rec.energization_day_en
        upratna = ", ".join(rec.upratna_substitutes_ta if is_ta else rec.upratna_substitutes_en)

        rows = [
            [
                Paragraph(f"<b>{badge}: {gem_name}</b> <font size='6' color='#64748B'>({rec.primary_gem_sanskrit})</font>", styles["TableHeader"]),
                Paragraph(f"<b>குறைந்தபட்ச எடை:</b> {rec.minimum_rattis} Ratti / {rec.minimum_carats} Carats", styles["TableHeader"]),
            ],
            [
                Paragraph(f"• <b>உலோகம்:</b> {metal} &nbsp;&nbsp;|&nbsp;&nbsp; <b>அணியும் விரல்:</b> {finger}", styles["NormalSmall"]),
                Paragraph(f"• <b>அணியும் நாள் / ஓரை:</b> {day}", styles["NormalSmall"]),
            ],
            [
                Paragraph(f"• <b>பிரதிஷ்டை மந்திரம்:</b> <font color='{NAVY_PRIMARY.hexval()}'><b>{rec.consecration_mantra_sanskrit}</b></font><br/><i>{rec.consecration_mantra_ta}</i>", styles["NormalSmall"]),
                Paragraph(f"• <b>மலிவான மாற்று கற்கள் (Uparatna):</b> {upratna}", styles["NormalSmall"]),
            ],
            [
                Paragraph(f"• <b>சுத்திகரிப்பு:</b> {rec.cleansing_vidhi_ta if is_ta else rec.cleansing_vidhi_en}", styles["NormalSmall"]),
                Paragraph(f"• <b>எச்சரிக்கை:</b> {rec.incompatible_gems_warning_ta if is_ta else rec.incompatible_gems_warning_en}", styles["NormalSmall"]),
            ],
        ]
        t = Table(rows, colWidths=[USABLE_WIDTH * 0.58, USABLE_WIDTH * 0.42])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    # Pillar 1: Life Stone
    story.append(render_gem_block(adv.life_stone, "PILLAR 1: LIFE STONE (JEEVAN RATNA)", "தூண் 1: உயிர் ரத்தினம் (ஜீவன் ரத்னம்)"))
    story.append(Spacer(1, 8))

    # Pillar 2: Lucky Stone
    story.append(render_gem_block(adv.lucky_stone, "PILLAR 2: LUCKY STONE (PUNYA RATNA)", "தூண் 2: புண்ணிய ரத்தினம் (பூர்வ புண்ணியம்)"))

    # --------------------------------------------------------------------------
    # PAGE 2: PILLARS 3 & 4 (SECONDARY SUPPORT) & STRICT PROHIBITIONS
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>பாக்கிய ரத்தினம், யோககாரகன் & கண்டிப்பான தடைகள்</b></font>" if is_ta else f"<font color='{GOLD_PRIMARY.hexval()}'><b>Fortune Stone, Secondary Yogakaraka & Strict Prohibitions</b></font>", styles["SectionTitle"]))
    story.append(Spacer(1, 6))

    # Pillar 3: Fortune Stone
    story.append(render_gem_block(adv.fortune_stone, "PILLAR 3: FORTUNE STONE (BHAGYA RATNA)", "தூண் 3: பாக்கிய ரத்தினம் (பாக்கிய ஸ்தானம்)"))
    story.append(Spacer(1, 8))

    # Pillar 4: Secondary Support Stone (if present)
    if adv.secondary_support_stone:
        story.append(render_gem_block(adv.secondary_support_stone, "SECONDARY SUPPORT STONE (YOGAKARAKA)", "இரண்டாம் நிலை ஆதரவு ரத்தினம் (யோககாரகன்)"))
        story.append(Spacer(1, 8))

    # Strict Prohibitions Box
    proh_rows = [
        [
            Paragraph("<b>கிரகம் / Graha</b>", styles["TableHeader"]),
            Paragraph("<b>ரத்தினம் / Gemstone</b>", styles["TableHeader"]),
            Paragraph("<b>தடைக்கான காரணம் / Shastric Reason</b>", styles["TableHeader"]),
        ]
    ]
    for pro in adv.prohibited_gemstones[:5]:
        proh_rows.append([
            Paragraph(f"<b>{pro.graha_name_ta if is_ta else pro.graha_name_en}</b>", styles["TableCellBold"]),
            Paragraph(pro.primary_gem_ta if is_ta else pro.primary_gem_en, styles["TableCell"]),
            Paragraph(pro.reason_ta if is_ta else pro.reason_en, styles["TableCell"]),
        ])
    t_proh = Table(proh_rows, colWidths=[USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.53])
    t_proh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CRIMSON_ACCENT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(Paragraph("<b>கண்டிப்பாக தவிர்க்க வேண்டிய ரத்தினங்கள் (Strictly Prohibited Dusthana Stones):</b>" if is_ta else "<b>Strictly Prohibited Gemstones (Dusthana 6th/8th/12th Lords):</b>", styles["NormalSmall"]))
    story.append(Spacer(1, 3))
    story.append(t_proh)
    story.append(Spacer(1, 8))

    # Conflicts Warning Box
    conflicts_text = "<br/>".join([f"• {c}" for c in (adv.conflicting_combinations_warning_ta if is_ta else adv.conflicting_combinations_warning_en)[:3]])
    story.append(Table([[Paragraph(f"<b>பகை கிரக ரத்தின முரண்பாட்டு விதிகள் (Planetary Conflict Rules):</b><br/>{conflicts_text}", styles["NormalSmall"])]], colWidths=[USABLE_WIDTH], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#FCA5A5")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    # --------------------------------------------------------------------------
    # PAGE 3: 1-TO-14 MUKHI RUDRAKSHA PRESCRIPTION & PRANA PRATISHTHA VIDHI
    # --------------------------------------------------------------------------
    if adv.recommended_rudraksha:
        story.append(PageBreak())
        story.append(Paragraph(f"<font color='{GOLD_PRIMARY.hexval()}'><b>பிரதிகூல சாந்தி: 1-14 முக ருத்ராட்ச பரிந்துரை & பிரதிஷ்டை விதி</b></font>" if is_ta else f"<font color='{GOLD_PRIMARY.hexval()}'><b>Pratikula Pacification: Rudraksha Prescription & Prana Pratishtha Playbook</b></font>", styles["SectionTitle"]))
        story.append(Spacer(1, 6))

        rec_r = adv.recommended_rudraksha
        rudra_intro = (
            f"<b>{req.native_name} அவர்களின் ஜாதகத்திற்கு பரிந்துரைக்கப்பட்ட ருத்ராட்ச கூட்டு:</b><br/>"
            f"{rec_r.personal_alignment_reason_ta if is_ta else rec_r.personal_alignment_reason_en}"
        )
        story.append(Table([[Paragraph(rudra_intro, styles["NormalSmall"])]], colWidths=[USABLE_WIDTH], style=[
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),
            ('BOX', (0, 0), (-1, -1), 0.5, GOLD_PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(Spacer(1, 8))

        # 3 Beads Table
        beads = [
            ("முதன்மை ருத்ராட்சம் / Primary", rec_r.primary_bead),
            ("துணை ருத்ராட்சம் / Secondary", rec_r.secondary_bead),
            ("பொதுக் கவசம் / Universal", rec_r.universal_bead),
        ]
        r_rows = [
            [
                Paragraph("<b>நிலை / Classification</b>", styles["TableHeader"]),
                Paragraph("<b>ருத்ராட்சம் / Bead</b>", styles["TableHeader"]),
                Paragraph("<b>அதிபதி / தெய்வம்</b>", styles["TableHeader"]),
                Paragraph("<b>பீஜ மந்திரம் / Beeja Mantra</b>", styles["TableHeader"]),
                Paragraph("<b>பலன் / Benefit</b>", styles["TableHeader"]),
            ]
        ]
        for badge, b in beads:
            if not b:
                continue
            r_rows.append([
                Paragraph(f"<b>{badge}</b>", styles["TableCellBold"]),
                Paragraph(f"{b.mukhi} Mukhi ({b.name_ta if is_ta else b.name_en})", styles["TableCell"]),
                Paragraph(b.ruling_deity_ta if is_ta else b.ruling_deity_en, styles["TableCell"]),
                Paragraph(f"<b>{b.beeja_mantra_sanskrit}</b>", styles["TableCellBold"]),
                Paragraph((b.astrological_benefits_ta if is_ta else b.astrological_benefits_en)[:70] + "...", styles["TableCell"]),
            ])

        t_r_beads = Table(r_rows, colWidths=[USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.18])
        t_r_beads.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_PRIMARY),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_ZEBRA]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_r_beads)
        story.append(Spacer(1, 10))

        # Prana Pratishtha Consecration Guide
        pratishtha_steps = (
            "<b>ருத்ராட்ச பிராண பிரதிஷ்டை மற்றும் அணியும் முறை (Prana Pratishtha Ritual):</b><br/>"
            "1. <b>சுத்திகரிப்பு (Purification):</b> வளர்பிறை திங்கள், பிரதோஷம் அல்லது சிவராத்திரி நாளில், பசும்பால், தயிர், தேன், நெய், கங்கை நீர் (பஞ்சாமிர்தம்) கொண்டு ருத்ராட்சத்தை தூய்மை செய்யவும்.<br/>"
            "2. <b>சந்தனம் & வில்வம்:</b> சுத்தமான நீரால் கழுவி, சந்தனம், குங்குமம் பூசி சிவலிங்கத்தின் முன் அல்லது வில்வ இலைகள் மீது வைக்கவும்.<br/>"
            "3. <b>சிவ பஞ்சாட்சர ஜெபம் (108x):</b> வலது கையில் ஏந்தி 108 முறை 'ஓம் நம சிவாய' (Om Namah Shivaya) மந்திரம் ஜெபிக்கவும்.<br/>"
            "4. <b>அணியும் நூல் / உலோகம்:</b> வெள்ளி, தங்கம் அல்லது தாமிரத்தில் கட்டி, சிவப்பு அல்லது மஞ்சள் பட்டு நூலில் கழுத்தில் அணியவும்.<br/>"
            "5. <b>தூய்மை நெறிமுறைகள்:</b> மரண வீடுகள் மற்றும் தீட்டு காலங்களில் கழற்றி பூஜை அறையில் வைக்கவும்; மற்ற காலங்களில் 24 மணி நேரமும் அணியலாம்."
        )
        story.append(Table([[Paragraph(pratishtha_steps, styles["NormalSmall"])]], colWidths=[USABLE_WIDTH], style=[
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#86EFAC")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))

    doc.build(story, canvasmaker=PlaybookNumberedCanvas)
    return buffer.getvalue()
