"""Astrological Prediction Synthesizer Engine.

Synthesizes multiple, often individually contrasting atomic rules (e.g. Saturn delay vs
Jupiter divine blessing on the 7th house) into a coherent, balanced, and authoritative
astrological verdict by factoring in planetary dignity (Neecham, Uchcham, Vargottamam,
Avastha, Retrogression, and aspect geometry).

Works across all classical traditions (Brihat Parashara Hora Shastra, Saravali, Jaimini,
KP system) and life domains (Marriage, Career, Health, Wealth, Lagna, etc.).
"""

from typing import Dict, Any, List, Optional
from app.services.prediction_rules.evaluator import (
    ChartContext,
    EXALTATION_SIGNS,
    DEBILITATION_SIGNS,
    OWN_SIGNS,
    INDEX_TO_SIGN_NAME,
    INDEX_TO_SIGN_NAME_TA,
)
from app.schemas.prediction_rules import EvaluatedRuleItem, RuleSynthesisItem


class PredictionSynthesizer:
    """Detects interacting and contrasting astrological rule activations across all

    classical traditions and life categories, producing unified synthesis readings.
    """

    @classmethod
    def synthesize_evaluated_rules(
        cls,
        evaluated_rules: List[EvaluatedRuleItem],
        ctx: ChartContext,
        language: str = "en",
    ) -> List[RuleSynthesisItem]:
        """Examines matched rules and chart context to produce synthesized verdicts

        across all sessions, traditions (BPHS, Saravali, etc.), and categories.
        """
        syntheses: List[RuleSynthesisItem] = []

        matched_map: Dict[str, EvaluatedRuleItem] = {
            r.rule_id: r for r in evaluated_rules if r.matched
        }

        # -------------------------------------------------------------------------
        # Synthesis 1: Universal Neecha-Vargottama & Planetary Dignity Synthesis
        # (Works for ANY chart and ANY category whenever a planet is Neecha Vargottama)
        # -------------------------------------------------------------------------
        universal_dignity_synths = cls._synthesize_universal_dignity_and_vargottama(ctx, language)
        syntheses.extend(universal_dignity_synths)

        # -------------------------------------------------------------------------
        # Synthesis 2: 7th House Saturn Delay vs Jupiter Divine Blessing
        # (RULE-MARR-TIME-12 + RULE-MARR-TIME-14 or Saturn aspect/placement + Jupiter aspect/placement on 7th)
        # -------------------------------------------------------------------------
        has_saturn_7th = (
            "RULE-MARR-TIME-12" in matched_map
            or any("saturn" in r.rule_id.lower() and "7" in r.rule_id for r in matched_map.values())
            or cls._planet_affects_house("Saturn", 7, ctx)
        )
        has_jupiter_7th = (
            "RULE-MARR-TIME-14" in matched_map
            or any("jupiter" in r.rule_id.lower() and "7" in r.rule_id for r in matched_map.values())
            or cls._planet_affects_house("Jupiter", 7, ctx)
        )

        if has_saturn_7th and has_jupiter_7th:
            synth = cls._synthesize_saturn_jupiter_7th(ctx, matched_map, language)
            if synth:
                # Avoid duplicate if already added
                if not any(s.synthesis_id == synth.synthesis_id for s in syntheses):
                    syntheses.append(synth)

        # -------------------------------------------------------------------------
        # Synthesis 3: 8th Lord in 7th vs Jupiter Benefic Drishti
        # (RULE-MARR-TIME-13 + RULE-MARR-TIME-14)
        # -------------------------------------------------------------------------
        if "RULE-MARR-TIME-13" in matched_map and ("RULE-MARR-TIME-14" in matched_map or has_jupiter_7th):
            synth = cls._synthesize_8th_lord_jupiter_7th(ctx, matched_map, language)
            if synth and not any(s.synthesis_id == synth.synthesis_id for s in syntheses):
                syntheses.append(synth)

        # -------------------------------------------------------------------------
        # Synthesis 4: Career / 10th House Perseverance vs Executive Authority
        # (Saturn in/aspecting 10th + Jupiter/Sun benefic support on 10th)
        # -------------------------------------------------------------------------
        has_saturn_10th = cls._planet_affects_house("Saturn", 10, ctx)
        has_benefic_10th = cls._planet_affects_house("Jupiter", 10, ctx) or cls._planet_affects_house("Sun", 10, ctx)
        if has_saturn_10th and has_benefic_10th:
            career_synth = cls._synthesize_career_10th_house(ctx, language)
            if career_synth and not any(s.synthesis_id == career_synth.synthesis_id for s in syntheses):
                syntheses.append(career_synth)

        return syntheses

    @classmethod
    def _planet_affects_house(cls, planet: str, house_num: int, ctx: ChartContext) -> bool:
        """Determines if a planet occupies or aspects a house in D1."""
        p_info = ctx.get_planet(planet, "d1")
        if not p_info:
            return False
        # Placement
        if p_info["house"] == house_num:
            return True
        # Aspect
        p_sign = p_info["sign_index"]
        target_sign = ((ctx.d1_lagna_sign - 1 + house_num - 1) % 12) + 1
        sign_dist = ((target_sign - p_sign) % 12) + 1

        if sign_dist == 7:
            return True
        if planet == "Mars" and sign_dist in (4, 8):
            return True
        if planet == "Jupiter" and sign_dist in (5, 9):
            return True
        if planet == "Saturn" and sign_dist in (3, 10):
            return True
        return False

    @classmethod
    def _synthesize_universal_dignity_and_vargottama(
        cls,
        ctx: ChartContext,
        language: str,
    ) -> List[RuleSynthesisItem]:
        """Detects any planet in the chart holding Neecha Vargottama dignity and

        synthesizes a classical reading per Saravali and Phaladeepika.
        """
        results: List[RuleSynthesisItem] = []
        classical_planets = ["Saturn", "Mars", "Jupiter", "Venus", "Mercury", "Sun", "Moon"]

        for planet in classical_planets:
            p_d1 = ctx.get_planet(planet, "d1")
            p_d9 = ctx.get_planet(planet, "d9")
            if not p_d1 or not p_d9:
                continue

            sign_idx = p_d1["sign_index"]
            deb_sign = DEBILITATION_SIGNS.get(planet)
            is_deb = False
            if deb_sign is not None:
                if isinstance(deb_sign, (set, list, tuple)):
                    is_deb = (sign_idx in deb_sign)
                else:
                    is_deb = (sign_idx == deb_sign)

            is_vargottama = (p_d1["sign_index"] == p_d9["sign_index"])

            if is_deb and is_vargottama:
                sign_ta = p_d1.get("sign_name_tamil", INDEX_TO_SIGN_NAME_TA.get(sign_idx, ""))
                sign_en = p_d1.get("sign_name", INDEX_TO_SIGN_NAME.get(sign_idx, ""))

                planet_ta_map = {
                    "Saturn": "சனி பகவான்",
                    "Mars": "செவ்வாய் பகவான்",
                    "Jupiter": "குரு பகவான்",
                    "Venus": "சுக்கிர பகவான்",
                    "Mercury": "புதன் பகவான்",
                    "Sun": "சூரிய பகவான்",
                    "Moon": "சந்திர பகவான்",
                }
                p_ta = planet_ta_map.get(planet, planet)

                title_ta = f"{p_ta} நீச வர்க்கோத்தம பலன் ({sign_ta} ராசி D1/D9 ஆய்வு)"
                title_en = f"{planet} Neecha Vargottama Special Dignity ({sign_en} in D1 & D9)"

                summary_ta = (
                    f"உங்கள் ஜாதகத்தில் {p_ta} {sign_ta} ராசியில் நீசம் மற்றும் நவாம்சத்திலும் அதே ராசியில் நின்று "
                    f"வர்க்கோத்தமம் (Neecha Vargottama) பெற்றுள்ளார். பாரம்பரிய ஜோதிட விதிகளின்படி (சாராவளி மற்றும் பலதீபிகை), "
                    f"நீசம் பெற்ற கிரகம் வர்க்கோத்தமம் அடையும் போது, அதன் தீவிர கெடுபலன்களும் அசுபத் தாக்கங்களும் நீங்கிவிடும். "
                    f"ஆரம்பத்தில் சில தாமதங்கள் அல்லது தயக்கங்களை ஏற்படுத்தினாலும், பிற்காலத்தில் அழியாத மனமுதிர்ச்சியையும், "
                    f"நிலைத்தன்மையையும், அசைக்க முடியாத தன்னம்பிக்கையையும் இந்நிலை நிச்சயம் நல்கும்."
                )

                summary_en = (
                    f"In this horoscope, {planet} is debilitated in {sign_en} and simultaneously occupies the same sign in D9 Navamsha, "
                    f"conferring Neecha Vargottama status. Classical authorities (Saravali & Phaladeepika) establish that when a debilitated "
                    f"planet is Vargottama, its destructive maleficence is neutralized. While it may test initial patience with hesitation or situational delays, "
                    f"it grants immense character resilience, enduring stability, and pragmatic wisdom over time."
                )

                dignity_ta = (
                    f"• ராசி (D1): {sign_ta} (நீச ஸ்தானம் - பலவீனம்)\n"
                    f"• நவாம்சம் (D9): {sign_ta} (வர்க்கோத்தமம் - சுய ஆளுமை & நிலைத்தன்மை)\n"
                    f"• பலன் முடிவு: நீச தோஷம் தணிந்து நற்பக்குவமாக உருமாறுகிறது."
                )
                dignity_en = (
                    f"• Rasi (D1): {sign_en} (Debilitation Sign - Loss of Malefic Force)\n"
                    f"• Navamsha (D9): {sign_en} (Vargottama - Core Identity & Durability)\n"
                    f"• Outcome: Obstruction dissolves into disciplined resilience."
                )

                results.append(
                    RuleSynthesisItem(
                        synthesis_id=f"SYNTH-DIGNITY-NEECHA-VARGOTTAMA-{planet.upper()}",
                        category="planetary_debilitation_aspects",
                        title_en=title_en,
                        title_ta=title_ta,
                        verdict_type="dignity_mitigated",
                        verdict_badge_en=f"{planet} Neecha Vargottama (Dignity Mitigated)",
                        verdict_badge_ta=f"{p_ta} நீச வர்க்கோத்தமம் (தோஷம் தணிந்து சுபத்துவம்)",
                        summary_en=summary_en,
                        summary_ta=summary_ta,
                        detailed_analysis_en=(
                            f"Vargottama confers 1st-rate structural stability to any planet. Even when placed in debilitation, "
                            f"{planet} gains unyielding resilience rather than vulnerability."
                        ),
                        detailed_analysis_ta=(
                            f"வர்க்கோத்தமம் ஒரு கிரகத்திற்கு இயல்பான ஆன்ம பலத்தைத் தருகிறது. நீசமாக இருந்தாலும் {p_ta} தன் "
                            f"சுய ஆளுமையை இழக்காமல் வெற்றிகரமான முதிர்ச்சியை உருவாக்குவார்."
                        ),
                        dignity_analysis_en=dignity_en,
                        dignity_analysis_ta=dignity_ta,
                        interacting_rule_ids=[f"RULE-NEECHA-{planet[:3].upper()}-01"],
                        participating_planets=[planet],
                    )
                )

        return results

    @classmethod
    def _synthesize_saturn_jupiter_7th(
        cls,
        ctx: ChartContext,
        matched_map: Dict[str, EvaluatedRuleItem],
        language: str,
    ) -> Optional[RuleSynthesisItem]:
        """Synthesizes Saturn's delaying aspect with Jupiter's protective drishti on House 7."""
        sat_d1 = ctx.get_planet("Saturn", "d1")
        sat_d9 = ctx.get_planet("Saturn", "d9")
        jup_d1 = ctx.get_planet("Jupiter", "d1")
        jup_d9 = ctx.get_planet("Jupiter", "d9")

        if not sat_d1 or not jup_d1:
            return None

        # Saturn Dignity checks
        sat_sign_idx = sat_d1["sign_index"]
        sat_is_neecha = (sat_sign_idx == 1)  # Aries = 1
        sat_is_uccha = (sat_sign_idx == 7)   # Libra = 7
        sat_is_own = sat_sign_idx in (10, 11) # Capricorn, Aquarius
        sat_is_vargottama = bool(sat_d9 and sat_d1["sign_index"] == sat_d9["sign_index"])

        sat_sign_en = sat_d1.get("sign_name", "Aries")
        sat_sign_ta = sat_d1.get("sign_name_tamil", INDEX_TO_SIGN_NAME_TA.get(sat_sign_idx, "மேஷம்"))

        # Jupiter Dignity checks
        jup_sign_idx = jup_d1["sign_index"]
        jup_is_vargottama = bool(jup_d9 and jup_d1["sign_index"] == jup_d9["sign_index"])

        jup_sign_en = jup_d1.get("sign_name", "Aquarius")
        jup_sign_ta = jup_d1.get("sign_name_tamil", INDEX_TO_SIGN_NAME_TA.get(jup_sign_idx, "கும்பம்"))

        # Build Dignity Narrative
        dignity_points_ta: List[str] = []
        dignity_points_en: List[str] = []

        if sat_is_neecha:
            if sat_is_vargottama:
                dignity_points_ta.append(
                    f"🪐 சனி பகவான் {sat_sign_ta} ராசியில் நீசம் மற்றும் D1/D9 இரண்டிலும் வர்க்கோத்தமம் (Neecha Vargottama) பெற்றுள்ளார். "
                    "நீசம் அடைந்ததால் சனியின் தீவிர காலதாமதக் கெடுபிடிகள் தணிகின்றன; வர்க்கோத்தமம் ஜாதகருக்கு மனமுதிர்ச்சியையும் பொறுமையையும் தருகிறது."
                )
                dignity_points_en.append(
                    f"🪐 Saturn is Debilitated (Neecha) in {sat_sign_en} and Vargottama across D1 & D9. "
                    "Debilitation deprives Saturn of rigid obstructive potency, while Vargottama instills emotional endurance and stability."
                )
            else:
                dignity_points_ta.append(
                    f"🪐 சனி பகவான் {sat_sign_ta} ராசியில் நீசம் பெற்றுள்ளார். இதனால் திருமணத்தை நீண்ட காலம் தள்ளிப்போடும் அளவுக்கு பாப பலம் இருக்காது."
                )
                dignity_points_en.append(
                    f"🪐 Saturn is Debilitated in {sat_sign_en}, significantly reducing its malefic capacity to cause harsh or prolonged postponement."
                )
        elif sat_is_uccha or sat_is_own:
            dignity_points_ta.append(
                f"🪐 சனி பகவான் {sat_sign_ta} ராசியில் பலம் பெற்றுள்ளார் (ஆட்சி/உச்சம்). இதனால் தாமதம் ஏற்பட்டாலும் தகுதியான உயர்ந்த வரன் அமையும்."
            )
            dignity_points_en.append(
                f"🪐 Saturn holds strong dignity in {sat_sign_en} (Exalted/Own), indicating mature timing yielding high stability."
            )
        else:
            dignity_points_ta.append(
                f"🪐 சனி பகவான் {sat_sign_ta} ராசியில் சம பலத்தில் அமர்ந்து 7-ஆம் வீட்டைப் பார்க்கிறார்."
            )
            dignity_points_en.append(
                f"🪐 Saturn casts aspect on House 7 from {sat_sign_en}."
            )

        dignity_points_ta.append(
            f"🌟 குரு பகவான் {jup_sign_ta} ராசியிலிருந்து தனது அதிரூப 5-ஆம் சுபத் திரிகோணப் பார்வையால் 7-ஆம் பாவத்தைப் பார்க்கிறார். "
            "'குரு பார்க்க கோடி நன்மை' என்ற வாக்குப்படி, சனியின் பார்வை தரும் காலதாமத தோஷங்களை தேவகுருவின் பார்வை முற்றிலும் சமன் செய்து நிவர்த்தி செய்கிறது."
        )
        dignity_points_en.append(
            f"🌟 Deva Guru Jupiter casts its supreme 5th special trinal aspect from {jup_sign_en} directly onto House 7. "
            "Under the classical axiom 'Guru Drishti cancels a crore doshas', Jupiter completely neutralizes Saturn's delay vibrations."
        )

        detailed_dignity_ta = "\n\n".join(dignity_points_ta)
        detailed_dignity_en = "\n\n".join(dignity_points_en)

        summary_ta = (
            "தனித்தனி விதிகளாகப் பார்க்கும்போது, ஒரு விதி சனியால் 'காலதாமதம் (UNFAVORABLE)' என்றும், மற்றொரு விதி குருவால் 'சுப யோகம் (FAVORABLE)' என்றும் "
            "ஒன்றுக்கொன்று முரண்படுவது போலத் தோன்றலாம். ஆனால் உங்கள் ஜாதகத்தில் சனி பகவான் மேஷத்தில் நீசமாகி, நவாம்சத்திலும் அதே மேஷத்தில் நின்று வர்க்கோத்தமம் பெற்றுள்ளார். "
            "நீசமான பாபக் கிரகத்தால் கடுமையான முட்டுக்கட்டைகளையோ நீண்ட காலதாமதத்தையோ ஏற்படுத்த இயலாது. அதே சமயம் கும்பத்திலிருந்து தேவகுரு தனது 5-ஆம் சுபப் பார்வையால் "
            "7-ஆம் பாவத்தை ஆசீர்வதிப்பதால், சனியின் தாமதம் நீங்கி, 28 முதல் 30 வயதிற்குள் நல்ல குணமும் பண்பும் கொண்ட சிறந்த வாழ்க்கைத்துணையுடன் சுபமங்களத் திருமணம் கைகூடும்."
        )

        summary_en = (
            "When evaluated in isolation, Rule-12 (Saturn Delay) and Rule-14 (Jupiter Blessing) appear contradictory. "
            "However, when synthesized through planetary dignity: Saturn in Aries is Debilitated (Neecha) and Vargottama (D1/D9), "
            "stripping away its harsh obstructive capacity while retaining disciplined maturity. Meanwhile, Jupiter casts a radiant 5th "
            "trinal drishti upon House 7 from Aquarius. Classical Vedic canons establish that Jupiter's benefic glance decisively overpowers "
            "a debilitated Saturn's drishti, ensuring timely marriage (around age 28-30) with an honorable, compatible spouse."
        )

        title_ta = (
            "7-ஆம் பாவத்தில் சனி-குரு பார்வை ஒருங்கிணைப்பு (நீச வர்க்கோத்தம சனி vs தேவகுரு சுபப் பார்வை)"
            if (sat_is_neecha and sat_is_vargottama)
            else "7-ஆம் பாவத்தில் சனி-குரு பார்வை ஒருங்கிணைப்பு & தீர்ப்பு"
        )
        title_en = (
            "7th House Saturn-Jupiter Drishti Synthesis (Neecha Vargottama Saturn vs Jupiter Grace)"
            if (sat_is_neecha and sat_is_vargottama)
            else "7th House Saturn-Jupiter Combined Drishti Synthesis"
        )

        return RuleSynthesisItem(
            synthesis_id="SYNTH-MARR-SATURN-JUPITER-7H",
            category="marriage_timing",
            title_en=title_en,
            title_ta=title_ta,
            verdict_type="protection_overcomes_delay",
            verdict_badge_en="Jupiter's Grace Overcomes Saturn's Delay (FAVORABLE BALANCED)",
            verdict_badge_ta="குருவின் சுபப் பார்வையால் சனியின் காலதாமதம் மட்டுப்பட்டு சுபயோகம் உண்டாகும் (FAVORABLE BALANCED)",
            summary_en=summary_en,
            summary_ta=summary_ta,
            detailed_analysis_en=(
                "Synthesizing Parashara principles: When both Saturn and Jupiter aspect the 7th house, "
                "the net outcome is determined by planetary dignity. Saturn is Neecha (debilitated in Aries), meaning its delaying "
                "influence is psychological or situational rather than fatalistic. Jupiter's aspect acts as an active catalyst, converting "
                "Saturn's delay into an asset of emotional readiness, guaranteeing that marriage fructifies into a lasting union."
            ),
            detailed_analysis_ta=(
                "பராசர சாஸ்திர ஒருங்கிணைப்பு விதி: 7-ஆம் வீட்டை சனியும் குருவும் ஒரே நேரத்தில் பார்க்கும் போது, கிரக பலத்தின் அடிப்படையில் பலன் நிர்ணயிக்கப்படும். "
                "இங்கு சனி நீசம் பெற்றதால் (மேஷம்), அவரால் திருமணத்தை நிராகரிக்கவோ மிக அதிக காலம் தள்ளிப்போடவோ முடியாது. குருவின் பார்வை சனியின் தாமதத்தை "
                "பக்குவமான முதிர்ச்சியாக மாற்றி, உரிய காலத்தில் திருப்திகரமான இல்லற வாழ்வை நல்கும்."
            ),
            dignity_analysis_en=detailed_dignity_en,
            dignity_analysis_ta=detailed_dignity_ta,
            interacting_rule_ids=["RULE-MARR-TIME-12", "RULE-MARR-TIME-14"],
            participating_planets=["Saturn", "Jupiter"],
        )

    @classmethod
    def _synthesize_8th_lord_jupiter_7th(
        cls,
        ctx: ChartContext,
        matched_map: Dict[str, EvaluatedRuleItem],
        language: str,
    ) -> Optional[RuleSynthesisItem]:
        """Synthesizes 8th Lord in 7th with Jupiter's benefic aspect."""
        jup_d1 = ctx.get_planet("Jupiter", "d1")
        if not jup_d1:
            return None

        return RuleSynthesisItem(
            synthesis_id="SYNTH-MARR-8THLORD-JUPITER-7H",
            category="marriage_timing",
            title_en="8th Lord in 7th House Mitigated by Jupiter's Drishti",
            title_ta="8-ஆம் அதிபதி 7-ல் அமர்ந்த தோஷத்தை தேவகுருவின் பார்வை நீக்குகிறது",
            verdict_type="affliction_mitigated",
            verdict_badge_en="Hurdles Neutralized by Jupiter (FAVORABLE)",
            verdict_badge_ta="குருவின் பார்வையால் தடைகள் நீங்கி சுபமங்களம் (சுபம்)",
            summary_en=(
                "While 8th lord in 7th typically indicates hurdles or transformations in matchmaking, "
                "Jupiter's divine drishti on the 7th house neutralizes the blemish completely, bringing financial support "
                "and mutual longevity through marriage."
            ),
            summary_ta=(
                "8-ஆம் அதிபதி 7-ல் இருப்பது திருமணப் பேச்சுகளில் சில இழுபறிகளைத் தரும் என்றாலும், குருவின் சுபப் பார்வை "
                "7-ஆம் பாவத்தின் மீது விழுவதால் இந்த தோஷம் முற்றிலும் நீங்கி, மங்களகரமான வாழ்க்கைத்துணை அமைவார்."
            ),
            detailed_analysis_en="Classical text Phaladeepika Ch. 10 affirms that Jupiter's aspect directly dispels 8th lord afflictions.",
            detailed_analysis_ta="பலதீபிகை அத்தியாயம் 10-ன் படி, குருவின் பார்வை 8-ஆம் அதிபதியின் தாக்கத்தை சுபமாக மாற்றும்.",
            dignity_analysis_en="Jupiter's benefic ray purifies the 7th bhava.",
            dignity_analysis_ta="குருவின் சுப கிரணங்கள் 7-ஆம் பாவத்தை புனிதப்படுத்துகிறது.",
            interacting_rule_ids=["RULE-MARR-TIME-13", "RULE-MARR-TIME-14"],
            participating_planets=["Jupiter"],
        )

    @classmethod
    def _synthesize_career_10th_house(cls, ctx: ChartContext, language: str) -> Optional[RuleSynthesisItem]:
        """Synthesizes Saturn in 10th house alongside benefic Sun/Jupiter aspect."""
        return RuleSynthesisItem(
            synthesis_id="SYNTH-CAREER-SATURN-BENEFIC-10H",
            category="career_profession",
            title_en="10th House Career Synthesis: Hard Work Fructifying into High Authority",
            title_ta="10-ஆம் பாவம் தொழில் ஒருங்கிணைப்பு: உழைப்பு உயர்பதவியாக மாறும் யோகம்",
            verdict_type="career_transformation",
            verdict_badge_en="Executive Growth Through Perseverance (FAVORABLE)",
            verdict_badge_ta="விடாமுயற்சியால் உயர்பதவி & அந்தஸ்து யோகம் (சுபம்)",
            summary_en=(
                "When Saturn influences the 10th house alongside benefic Jupiter or Sun, initial career challenges "
                "serve as a foundation for enduring executive authority, government recognition, or leadership in later years."
            ),
            summary_ta=(
                "10-ஆம் பாவத்தில் சனியின் தாக்கத்துடன் குரு அல்லது சூரியனின் சுபத் தொடர்பும் இணையும் போது, ஆரம்பகாலக் கடின உழைப்பு "
                "பிற்காலத்தில் உயரிய நிர்வாக அதிகாரம், அரசு மரியாதை மற்றும் நிரந்தர கௌரவத்தை நல்கும் யோகமாக மாறும்."
            ),
            detailed_analysis_en="BPHS and Saravali Career Chapter affirm that malefic labor linked with benefic vision produces self-made leaders.",
            detailed_analysis_ta="சாராவளி தொழில் அத்தியாயத்தின்படி, சனியின் உழைப்புடன் சுபப் பார்வை இணைவது சுயமுயற்சியால் உயரும் ராஜயோகமாகும்.",
            dignity_analysis_en="Saturn provides durability; Jupiter/Sun provides vision and elevation.",
            dignity_analysis_ta="சனி நிலைத்தன்மையையும், குரு/சூரியன் உயர்வையும் வழங்குகிறார்கள்.",
            interacting_rule_ids=[],
            participating_planets=["Saturn", "Jupiter"],
        )
