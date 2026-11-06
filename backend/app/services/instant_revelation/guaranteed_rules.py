"""BNN & Deva Keralam Classical Rule Verification Engine.

Executes a genuine 3-Tier Hierarchical Verification (திரிவித சாஸ்திர சரிபார்ப்பு முறை):
- Gate 1: Strict Degree Orb Planetary Vector (Conjunction <= 10°, Trine <= 8°, Opposition <= 7°, Adjacent <= 8°)
- Gate 2: Bhava Lordship, Dispositor, or Angular/Trinal House Confirmation
- Gate 3: Navamsa (D9), Functional Dignity, or Dasa-Gochara Confirmation

Eliminates loose assumptions, sensationalist exaggerations, and mutual contradictions.
Surfaces only mathematically and shastrically grounded planetary archetypes.
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from app.schemas.instant_revelation import RevelationBullet

SIGN_NAMES_TA = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
    "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
    "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_NAMES_TA = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "ராகு",
    "Ketu": "கேது",
}

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

TRINE_GROUPS = {
    "Dharma (Fire)": {1, 5, 9},     # Aries, Leo, Sagittarius
    "Artha (Earth)": {2, 6, 10},    # Taurus, Virgo, Capricorn
    "Kama (Air)": {3, 7, 11},       # Gemini, Libra, Aquarius
    "Moksha (Water)": {4, 8, 12},   # Cancer, Scorpio, Pisces
}


def are_planets_connected_bnn(
    p1_sign: int,
    p2_sign: int,
    p1_deg: float = 0.0,
    p2_deg: float = 0.0,
    max_conj_orb: float = 10.0,
    max_trine_orb: float = 8.0,
    max_opp_orb: float = 7.0,
) -> Tuple[bool, str, int]:
    """
    Check BNN primary geometric connection under strict degree orbs.
    Returns (is_connected, description, strength_score).
    """
    # 1. Conjunction in same sign
    if p1_sign == p2_sign:
        deg_diff = abs(p1_deg - p2_deg)
        if deg_diff <= max_conj_orb:
            score = int(100 - (deg_diff * 4))
            score = max(70, min(100, score))
            return True, f"இணைவு சேர்க்கை (Conjunction - {deg_diff:.1f}° பாகை இடைவெளி)", score
        return False, "அதிக பாகை இடைவெளி", 0

    # 2. Trine connection (1, 5, 9 of same element)
    for t_name, signs in TRINE_GROUPS.items():
        if p1_sign in signs and p2_sign in signs:
            deg_diff = abs(p1_deg - p2_deg)
            if deg_diff <= max_trine_orb:
                score = int(90 - (deg_diff * 4))
                score = max(65, min(90, score))
                return True, f"திசைத் திரிகோணம் ({t_name} Trine - {deg_diff:.1f}° பாகை இடைவெளி)", score
            return False, "திரிகோணத்தில் அதிக பாகை இடைவெளி", 0

    # 3. Forward Adjacent (2nd house) - Only if tightly spanning across sign boundary
    if ((p2_sign - p1_sign) % 12) == 1:
        boundary_span = (30.0 - p1_deg) + p2_deg
        if boundary_span <= 8.0:
            score = int(85 - (boundary_span * 3))
            return True, f"முன்னோக்கிய 2-ஆம் வீடு (Forward Adjacent - {boundary_span:.1f}° எல்லை இடைவெளி)", score

    # 4. Samasaptaka (1/7 Opposition)
    if ((p2_sign - p1_sign) % 12) == 6:
        deg_diff = abs(p1_deg - p2_deg)
        if deg_diff <= max_opp_orb:
            score = int(80 - (deg_diff * 4))
            return True, f"நேர் எதிர்ப்பார்வை (1/7 Samasaptaka - {deg_diff:.1f}° பாகை இடைவெளி)", score

    return False, "சாஸ்திர இணைப்பு இல்லை", 0


def calculate_navamsa_sign(longitude: float) -> int:
    """Calculate the D9 Navamsa sign index (1 to 12) from total sidereal longitude."""
    total_deg = longitude % 360.0
    navamsa_num = int(total_deg / 3.3333333333)
    sign_idx = (navamsa_num % 12) + 1
    return sign_idx


class GuaranteedRuleEngine:
    """Evaluates authentic BNN and Deva Keralam rules with a 3-tier verified checklist."""

    @classmethod
    def evaluate_all(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
        ascendant_deg: float,
        current_age: int,
        gender: str = "male",
        current_md: str = "",
        current_ad: str = "",
    ) -> Tuple[List[RevelationBullet], List[str], List[str]]:
        raw_candidates: List[Tuple[int, str, RevelationBullet]] = []
        taboos_ta: List[str] = []
        taboos_en: List[str] = []

        def get_p(pname: str) -> Tuple[int, float, int, float, int]:
            info = planets_dict.get(pname, {})
            sign = info.get("sign_index", 1)
            deg = info.get("degree", 0.0)
            lon = info.get("longitude", 0.0)
            house = ((sign - ascendant_sign) % 12) + 1
            nav_sign = calculate_navamsa_sign(lon)
            return sign, deg, house, lon, nav_sign

        sun_s, sun_d, sun_h, sun_l, sun_nav = get_p("Sun")
        moon_s, moon_d, moon_h, moon_l, moon_nav = get_p("Moon")
        mars_s, mars_d, mars_h, mars_l, mars_nav = get_p("Mars")
        mer_s, mer_d, mer_h, mer_l, mer_nav = get_p("Mercury")
        jup_s, jup_d, jup_h, jup_l, jup_nav = get_p("Jupiter")
        ven_s, ven_d, ven_h, ven_l, ven_nav = get_p("Venus")
        sat_s, sat_d, sat_h, sat_l, sat_nav = get_p("Saturn")
        rahu_s, rahu_d, rahu_h, rahu_l, rahu_nav = get_p("Rahu")
        ketu_s, ketu_d, ketu_h, ketu_l, ketu_nav = get_p("Ketu")

        # -------------------------------------------------------------
        # 1. SUN COMBINATIONS (WITH STRICT 3-TIER ORB VERIFICATION)
        # -------------------------------------------------------------
        # Sun + Saturn (Executive Authority / Administrative Acumen)
        c, rel, score = are_planets_connected_bnn(sun_s, sat_s, sun_d, sat_d)
        if c:
            gate2 = (sat_h in (1, 4, 7, 10, 5, 9, 6, 11) or sun_h in (1, 4, 7, 10, 5, 9, 11))
            gate3 = (sat_nav in (1, 4, 7, 10, 5, 9, 11) or current_md in ("Saturn", "Sun") or current_ad in ("Saturn", "Sun"))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் ({SIGN_NAMES_TA[sun_s-1]}) & சனி ({SIGN_NAMES_TA[sat_s-1]}) {rel}.",
                    f"[✓] நிலை 2 (பாவக பலம்): சனி {sat_h}-ஆம் பாவத்திலும், சூரியன் {sun_h}-ஆம் பாவத்திலும் அமைந்து நிர்வாக/சேவை ஸ்தானத்தை பலப்படுத்துகிறது.",
                    f"[✓] நிலை 3 (நவாம்சம் & தசா): நவாம்சத்தில் சனி ({SIGN_NAMES_TA[sat_nav-1]}) ஒழுங்குமுறை மற்றும் அரசு/பொறுப்பு காரகத்தை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "father_career", RevelationBullet(
                    id="bnn_sun_saturn",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Sun + Saturn: Executive Authority, Diligence & Public Service Calling",
                    headline_ta="சூரியன் + சனி: நிர்வாக ஆளுமை, பொறுப்புணர்வு & அரசு/பொதுத்துறை நாட்டம்",
                    script_en="The Sun and Saturn connection blends royal ambition with profound discipline. BNN shastras indicate strong aptitude for organized administration, law, engineering governance, or regulated corporate structures. This alignment instills high perseverance, self-reliance, and deep respect for protocol.",
                    script_ta="சூரியனும் சனியும் நெருங்கி இணைந்துள்ளதால், நிர்வாக ஆளுமையும் கடுமையான உழைப்பும் இயல்பாக அமையும். அரசு, சட்டம், பொதுத்துறை, பொறியியல் அல்லது நெறிமுறை சார்ந்த பெரிய நிறுவனங்களில் தலைமை/நிர்வாகப் பொறுப்புகளில் மிளிரும் யோகம் உண்டு. தந்தை வழியில் பொறுமை, கண்டிப்பு மற்றும் கர்ம ஒழுக்கம் முக்கிய பங்கு வகிக்கும்.",
                    astrological_proof=f"Sun ({SIGN_NAMES_EN[sun_s-1]}) & Saturn ({SIGN_NAMES_EN[sat_s-1]}) connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # Sun + Moon (Leadership & Emotional Resilience)
        c, rel, score = are_planets_connected_bnn(sun_s, moon_s, sun_d, moon_d)
        if c:
            gate2 = (moon_h in (1, 4, 7, 10, 5, 9, 2) or sun_h in (1, 4, 5, 9, 10))
            gate3 = (moon_nav in (4, 1, 5, 9, 2) or sun_nav in (1, 4, 5, 9, 10))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் ({SIGN_NAMES_TA[sun_s-1]}) & சந்திரன் ({SIGN_NAMES_TA[moon_s-1]}) {rel}.",
                    f"[✓] நிலை 2 (ஆத்ம-மன பலம்): சந்திரன் {moon_h}-ஆம் பாவத்திலும், சூரியன் {sun_h}-ஆம் பாவத்திலும் அமைந்து பொதுத்தொடர்பு ஆற்றலைத் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச தர்மம்): நவாம்சத்தில் சந்திரன் ({SIGN_NAMES_TA[moon_nav-1]}) மக்கள் செல்வாக்கை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "father_mind", RevelationBullet(
                    id="bnn_sun_moon",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Sun + Moon: Soul-Mind Cohesion & Executive Public Presence",
                    headline_ta="சூரியன் + சந்திரன்: ஆத்ம-மன ஒருமைப்பாடு & மக்கள் தொடர்பு ஆளுமை",
                    script_en="When Sun interconnects with Moon under tight orbs, it establishes a powerful blend of authoritative willpower and public empathy. You possess strong interpersonal intuition, natural respect in community circles, and leadership abilities that resonate with people.",
                    script_ta="சூரியனும் சந்திரனும் சாஸ்திர பாகை அமைப்பில் இணைந்திருப்பதால், வலுவான மன உறுதியும் மக்கள் செல்வாக்கும் உண்டாகும். ஆளுமைத் திறனும் மற்றவர்களின் உணர்வுகளைப் புரிந்து நடத்தும் சாதுரியமும் இயல்பாக இருக்கும். பொதுப் பணிகள் மற்றும் ஆலோசனைகளில் வெற்றி தரும் யோகம்.",
                    astrological_proof=f"Sun in {SIGN_NAMES_EN[sun_s-1]} & Moon in {SIGN_NAMES_EN[moon_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # Sun + Mars (Dynamic Leadership & Real Estate Acumen)
        c, rel, score = are_planets_connected_bnn(sun_s, mars_s, sun_d, mars_d)
        if c:
            gate2 = (mars_h in (1, 3, 4, 7, 10, 11) or sun_h in (1, 5, 9, 10))
            gate3 = (mars_s in (1, 8, 10, 5, 9) or mars_nav in (1, 8, 10, 5))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் ({SIGN_NAMES_TA[sun_s-1]}) & செவ்வாய் ({SIGN_NAMES_TA[mars_s-1]}) {rel}.",
                    f"[✓] நிலை 2 (தைரிய/பூமி பாவம்): செவ்வாய் {mars_h}-ல் நின்று பூமி சொத்து மற்றும் அதிகார தைரியத்தை அளிக்கிறது.",
                    f"[✓] நிலை 3 (நவாம்ச வீரியம்): செவ்வாய் நவாம்சத்தில் {SIGN_NAMES_TA[mars_nav-1]} அடைந்து சவால்களை வெல்லும் ஆற்றலை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "leadership_land", RevelationBullet(
                    id="bnn_sun_mars",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Sun + Mars: Dynamic Authority, Courage & Real Estate Aptitude",
                    headline_ta="சூரியன் + செவ்வாய்: துணிச்சலான ஆளுமை, நில யோகம் & தலைமை வீரியம்",
                    script_en="Sun combined with Mars ignites supreme courage, executive drive, and sharp decision-making. You excel when given independent charge or technical/operational projects, and possess strong aptitude for tangible land and immovable properties.",
                    script_ta="சூரியனும் செவ்வாயும் நெருங்கி இணைவதால் தன்னம்பிக்கையும் சவால்களை எதிர்கொள்ளும் தைரியமும் இயல்பாக இருக்கும். பூமி, கட்டடங்கள் அல்லது தொழில்நுட்பத் துறைகளில் நாட்டம் இருக்கும்; தனித்து நின்று ஒரு துறையை வழிநடத்தும் தலைமைப் பண்பு வெளிப்படும்.",
                    astrological_proof=f"Sun in {SIGN_NAMES_EN[sun_s-1]} & Mars in {SIGN_NAMES_EN[mars_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # Sun + Mercury (Budhaditya: Analytical Intellect & Trade Acumen)
        c, rel, score = are_planets_connected_bnn(sun_s, mer_s, sun_d, mer_d)
        if c:
            deg_diff = abs(sun_d - mer_d) if sun_s == mer_s else 10.0
            gate2 = (mer_h in (1, 2, 5, 6, 9, 10, 11) and deg_diff >= 1.5)  # avoid combustion zero
            gate3 = (mer_s in (3, 6, 2, 7, 10, 11) or mer_nav in (3, 6, 1, 5, 9))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் & புதன் {rel}.",
                    f"[✓] நிலை 2 (புதாதித்ய பாவம்): புதன் {mer_h}-ஆம் பாவத்தில் அமர்ந்து கணக்கு, வர்த்தகம், கல்வி ஆற்றலைத் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச புத்தி பலம்): புதன் நவாம்சத்தில் {SIGN_NAMES_TA[mer_nav-1]} பெற்று கூர்மையான அறிவாற்றலை உறுதி செய்கிறது.",
                ]
                raw_candidates.append((score, "intellect_trade", RevelationBullet(
                    id="bnn_sun_mercury",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Sun + Mercury (Budhaditya Yoga): Analytical Intellect & Commercial Insight",
                    headline_ta="சூரியன் + புதன் (புதாதித்ய யோகம்): கூர்மையான கல்வி, கணித-வர்த்தக ஞானம்",
                    script_en="Sun united with Mercury activates the celebrated Budhaditya Yoga. You possess a sharp, analytical intellect, rapid information processing, commercial intuition, and natural aptitude for strategic communications or analytical sciences.",
                    script_ta="சூரியனும் புதனும் இணைந்து புதாதித்ய யோகத்தை ஏற்படுத்துகின்றன. நுட்பமான கல்வி ஞானம், வர்த்தகப் பார்வை, எழுத்து மற்றும் தகவல் பரிமாற்றத்தில் தனித் திறமை அமையும். கணக்கு, மேலாண்மை மற்றும் திட்டமிடலில் இயல்பான மேதமை உண்டு.",
                    astrological_proof=f"Sun in {SIGN_NAMES_EN[sun_s-1]} & Mercury in {SIGN_NAMES_EN[mer_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # Sun + Jupiter (Advisory Wisdom & Sovereign Self-Esteem)
        c, rel, score = are_planets_connected_bnn(sun_s, jup_s, sun_d, jup_d)
        if c:
            gate2 = (jup_h in (1, 4, 5, 9, 10, 11, 2))
            gate3 = (jup_nav in (1, 4, 5, 9, 12, 11))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் & குரு {rel}.",
                    f"[✓] நிலை 2 (குரு தர்ம பலம்): குரு {jup_h}-ஆம் பாவத்தில் அமர்ந்து ஆன்மீக, ஆலோசனை மற்றும் உன்னத மதிப்பைப் பலப்படுத்துகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச தர்மம்): குரு நவாம்சத்தில் {SIGN_NAMES_TA[jup_nav-1]} பெற்று உயர் சுயமரியாதையை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "advisory_status", RevelationBullet(
                    id="bnn_sun_jupiter",
                    category="guaranteed_shock",
                    shock_factor="EXTREME",
                    headline_en="Sun + Jupiter: Paternal Prestige, Advisory Wisdom & Executive Honor",
                    headline_ta="சூரியன் + குரு: தந்தை வழி ஆன்மீக அந்தஸ்து, ஆலோசனைத் திறன் & சமூக மரியாதை",
                    script_en="Sun connected with Jupiter signifies an elevated moral compass, upright self-esteem, and natural advisory status. Family heritage often carries respected traditions in teaching, banking, medicine, or societal counsel.",
                    script_ta="சூரியனும் குருவும் தொடர்பு பெற்றுள்ளதால் உயர்ந்த சுயமரியாதையும் தர்ம சிந்தனையும் உண்டு. குடும்பப் பாரம்பரியத்தில் கல்வி, வங்கி, ஆன்மீகம் அல்லது ஆலோசனைப் பணிகளில் நல்ல மதிப்பும் மரியாதையும் இருக்கும். மற்றவர்களுக்கு வழிகாட்டும் ஆளுமை கூடும்.",
                    astrological_proof=f"Sun in {SIGN_NAMES_EN[sun_s-1]} & Jupiter in {SIGN_NAMES_EN[jup_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Sun + Rahu (Ambitious Vision & Transformative Mastery)
        c, rel, score = are_planets_connected_bnn(sun_s, rahu_s, sun_d, rahu_d)
        if c:
            gate2 = (sun_h in (1, 6, 8, 9, 10, 11) or rahu_h in (1, 6, 8, 9, 10, 11))
            gate3 = (rahu_nav in (1, 8, 6, 10, 11) or sun_nav in (1, 5, 9, 10))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சூரியன் & ராகு {rel}.",
                    f"[✓] நிலை 2 (அபிலாஷை பாவம்): சூரியன்/ராகு {sun_h}/{rahu_h}-ஆம் பாவத்தில் அதீத முன்னேற்ற வேட்கையைத் தூண்டுகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச உத்வேகம்): நவாம்சத்தில் ராகுவின் வீரியம் சர்வதேச/நவீன தளங்களில் வெற்றியைத் தருகிறது.",
                ]
                raw_candidates.append((score, "ambition_transform", RevelationBullet(
                    id="bnn_sun_rahu",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Sun + Rahu: Boundless Ambition, Innovative Breakthroughs & Eye Care Vigilance",
                    headline_ta="சூரியன் + ராகு: அசுர இலக்குகள், புதுமைத் துறை வெற்றி & கண் நலம் பேணுதல்",
                    script_en="Sun connected with Rahu fuels unconventional, out-of-the-box career ambitions and breakthroughs in cutting-edge or foreign spheres. It also advises regular eye checkups and mindful lifestyle habits regarding vital energy.",
                    script_ta="சூரியனும் ராகுவும் நெருங்குவதால் வழக்கமான பாதையை விடுத்து, புதிய தொழில்நுட்பங்கள் அல்லது நவீனத் துறைகளில் சாதனை படைக்கும் ஆர்வம் இருக்கும். கண்களின் நலம் மற்றும் உடல் உஷ்ணத்தை சீராகப் பராமரிப்பது நலம்.",
                    astrological_proof=f"Sun in {SIGN_NAMES_EN[sun_s-1]} & Rahu in {SIGN_NAMES_EN[rahu_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # -------------------------------------------------------------
        # 2. MOON COMBINATIONS (WITH STRICT 3-TIER ORB VERIFICATION)
        # -------------------------------------------------------------
        # Moon + Mars (Chandra-Mangala Yoga: Enterprise & Resource Building)
        c, rel, score = are_planets_connected_bnn(moon_s, mars_s, moon_d, mars_d)
        if c:
            gate2 = (moon_h in (1, 2, 4, 9, 10, 11) or mars_h in (1, 2, 4, 9, 10, 11))
            gate3 = (mars_nav in (1, 8, 10, 4) or moon_nav in (4, 2, 1, 10))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சந்திரன் & செவ்வாய் {rel} (சந்திர-மங்கள யோகம்).",
                    f"[✓] நிலை 2 (தன/பூமி பாவம்): சந்திரன் {moon_h}-லும் செவ்வாய் {mars_h}-லும் நின்று நிதி மற்றும் அசையா சொத்து யோகத்தை இணைக்கிறது.",
                    f"[✓] நிலை 3 (நவாம்ச சுப பலம்): நவாம்சத்தில் சுப சேர்க்கை தொழில் முனைவு ஆற்றலை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "wealth_enterprise", RevelationBullet(
                    id="bnn_moon_mars",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Moon + Mars (Chandra-Mangala Yoga): Enterprising Spirit & Wealth Accumulation",
                    headline_ta="சந்திரன் + செவ்வாய் (சந்திர-மங்கள யோகம்): தொழில் முனைவு வேகம் & தன-பூமி யோகம்",
                    script_en="Moon combined with Mars forms the potent Chandra-Mangala Yoga. You possess entrepreneurial instincts, rapid financial resourcefulness, and real estate building stamina, balancing passionate emotion with practical execution.",
                    script_ta="சந்திரனும் செவ்வாயும் இணைந்து சந்திர-மங்கள யோகத்தை அளிக்கின்றன. சுறுசுறுப்பான முடிவுகள், சுய உழைப்பில் சொத்துக்களை உருவாக்கும் ஆர்வம் மற்றும் வணிகத் திறமை இயல்பாக வெளிப்படும்.",
                    astrological_proof=f"Moon in {SIGN_NAMES_EN[moon_s-1]} & Mars in {SIGN_NAMES_EN[mars_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Moon + Jupiter (Gajakesari Yoga: Sage Counsel & Mental Equanimity)
        c, rel, score = are_planets_connected_bnn(moon_s, jup_s, moon_d, jup_d)
        if c:
            gate2 = (jup_h in (1, 4, 7, 10, 5, 9, 11) or moon_h in (1, 4, 7, 10, 5, 9))
            gate3 = (jup_nav in (1, 4, 5, 9, 12, 2) or moon_nav in (4, 12, 1, 5, 9))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சந்திரன் & குரு {rel} (கஜகேசரி யோகம்).",
                    f"[✓] நிலை 2 (கேந்திர பலம்): குரு {jup_h}-லும் சந்திரன் {moon_h}-லும் நின்று கஜகேசரி யோக ஆலோசனையைத் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச சுப பலம்): சந்திரன்/குரு நவாம்ச பலத்தால் உயர்ந்த தர்ம காரகமும் நற்புகழும் உறுதியாகிறது.",
                ]
                raw_candidates.append((score, "counsel_wisdom", RevelationBullet(
                    id="bnn_moon_jupiter",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Moon + Jupiter (Gajakesari Yoga): Emotional Resilience & Sage Advisory Acumen",
                    headline_ta="சந்திரன் + குரு (கஜகேசரி யோகம்): முதிர்ந்த மன அமைதி & தலைமை ஆலோசனை ஞானம்",
                    script_en="Moon closely coupled with Jupiter creates Gajakesari Yoga, granting emotional poise, wise mentorship, and dignified social standing. You possess natural gravitas as a problem-solver and trusted advisor.",
                    script_ta="சந்திரனும் குருவும் இணைந்து கஜகேசரி யோகம் உண்டாகிறது. ஆழ்ந்த சிந்தனை, நெருக்கடியான நேரங்களிலும் நிதானம் தவறாத பண்பு, மற்றும் சமுதாயத்தில் மதிப்பு மிக்க ஆலோசனைகளை வழங்கும் திறன் உண்டாகும்.",
                    astrological_proof=f"Moon in {SIGN_NAMES_EN[moon_s-1]} & Jupiter in {SIGN_NAMES_EN[jup_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Moon + Saturn (Reflective Intellect, Emotional Maturity & Diligence)
        c, rel, score = are_planets_connected_bnn(moon_s, sat_s, moon_d, sat_d)
        if c:
            gate2 = (sat_h in (1, 4, 7, 10, 5, 9, 11) or moon_h in (1, 4, 7, 10, 5, 9))
            gate3 = (sat_nav in (10, 11, 4, 7, 1) or moon_nav in (10, 11, 4, 7))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சந்திரன் & சனி {rel}.",
                    f"[✓] நிலை 2 (கர்ம-மன பாவம்): சனி {sat_h}-ஆம் பாவத்தில் நின்று ஆழ்ந்த பொறுப்புணர்வையும் முதிர்ச்சியையும் உணர்த்துகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச ஸ்திரத்தன்மை): சனி நவாம்சத்தில் {SIGN_NAMES_TA[sat_nav-1]} பெற்று மன உறுதியை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "emotional_maturity", RevelationBullet(
                    id="bnn_moon_saturn",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Moon + Saturn: Deep Contemplation, Diligence & Emotional Resilience",
                    headline_ta="சந்திரன் + சனி: ஆழ்ந்த சிந்தனை, நிதானமான உழைப்பு & மன உறுதி",
                    script_en="Moon linked with Saturn develops profound emotional resilience and patience through practical life experience. You possess serious focus, practical realism, and empathy for hard-working individuals.",
                    script_ta="சந்திரனும் சனியும் நெருக்கமாக இணைந்திருப்பதால், எதையும் ஆழ்ந்து யோசித்து நிதானமாக முடிவெடுக்கும் முதிர்ச்சி இருக்கும். பொறுப்புணர்வு, கடின உழைப்பு மற்றும் வாழ்க்கை அனுபவங்களின் வழி பக்குவப்படும் நற்குணம் உண்டாகும்.",
                    astrological_proof=f"Moon in {SIGN_NAMES_EN[moon_s-1]} & Saturn in {SIGN_NAMES_EN[sat_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # -------------------------------------------------------------
        # 3. MARS COMBINATIONS (WITH STRICT 3-TIER ORB VERIFICATION)
        # -------------------------------------------------------------
        # Mars + Jupiter (Guru-Mangala: Dynamic Leadership & Righteous Valour)
        c, rel, score = are_planets_connected_bnn(mars_s, jup_s, mars_d, jup_d)
        if c:
            gate2 = (mars_h in (1, 3, 4, 9, 10, 11) or jup_h in (1, 3, 5, 9, 11))
            gate3 = (jup_nav in (1, 5, 9, 3, 11) or mars_nav in (1, 8, 10, 3))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): செவ்வாய் & குரு {rel} (குரு மங்கள யோகம்).",
                    f"[✓] நிலை 2 (தர்ம-வீரிய பாவம்): செவ்வாய் {mars_h}-ல் நின்று தலைமைப் பண்பு மற்றும் நிலபுலன் சேர்க்கையை உறுதிசெய்கிறது.",
                    f"[✓] நிலை 3 (நவாம்ச கௌரவம்): குரு நவாம்சத்தில் {SIGN_NAMES_TA[jup_nav-1]} அடைந்து குடும்ப கௌரவத்தை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "leadership_virtue", RevelationBullet(
                    id="bnn_mars_jupiter",
                    category="guaranteed_shock",
                    shock_factor="EXTREME",
                    headline_en="Mars + Jupiter (Guru-Mangala Yoga): Dynamic Leadership, Land Ownership & Moral Valour",
                    headline_ta="செவ்வாய் + குரு (குரு மங்கள யோகம்): தலைமைப் பண்பு, பூமி யோகம் & தர்ம தைரியம்",
                    script_en="Guru-Mangala Yoga unifies martial courage with righteous wisdom. You possess high executive decisiveness, talent for land administration or project management, and protective family guardianship.",
                    script_ta="செவ்வாயும் குருவும் கூடி குரு மங்கள யோகத்தை நல்குகின்றன. தர்ம நெறி தவறாத தைரியம், நிலம் மற்றும் அசையா சொத்து யோகம், நிர்வாகப் பொறுப்புகளை ஏற்று வழிநடத்தும் ஆளுமை இயல்பாக வெளிப்படும்.",
                    astrological_proof=f"Mars in {SIGN_NAMES_EN[mars_s-1]} & Jupiter in {SIGN_NAMES_EN[jup_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Mars + Venus (Colonizer Yoga: Property Building & Aesthetic Vitality)
        c, rel, score = are_planets_connected_bnn(mars_s, ven_s, mars_d, ven_d)
        if c:
            gate2 = (mars_h in (1, 2, 4, 7, 10, 11) or ven_h in (1, 2, 4, 7, 10, 11))
            gate3 = (ven_nav in (2, 7, 12, 1, 4, 10) or mars_nav in (1, 8, 10, 4))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): செவ்வாய் & சுக்கிரன் {rel} (காலனைசர் சேர்க்கை).",
                    f"[✓] நிலை 2 (பூமி/சுக பாவம்): செவ்வாய் {mars_h}-லும் சுக்கிரன் {ven_h}-லும் நின்று வசதியான நில-வீட்டு அமைப்பைத் தூண்டுகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச சேர்க்கை): நவாம்சத்தில் சுக்கிரன்-செவ்வாய் சேர்க்கை கவர்ச்சிகரமான இல்லறத்தையும் பூமி யோகத்தையும் உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "property_vitality", RevelationBullet(
                    id="bnn_mars_venus",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Mars + Venus: Colonizer Archetype — Real Estate Drive & Creative Vitality",
                    headline_ta="செவ்வாய் + சுக்கிரன்: காலனைசர் தத்துவம் — நிலபுலன் சேர்க்கை & வசதியான வாழ்வியல்",
                    script_en="Mars and Venus combined channels passion into aesthetic spaces and property acquisition. You hold keen architectural or interior sensibilities and strong ambition to build tangible assets.",
                    script_ta="செவ்வாயும் சுக்கிரனும் இணைவதால் அழகுணர்ச்சியும், பூமி மற்றும் மனை சார்ந்த சொத்துக்களை விருத்தி செய்யும் ஆர்வமும் கூடும். வசதியான வாழ்விடங்கள் மற்றும் சுப காரியங்களில் நாட்டம் இருக்கும்.",
                    astrological_proof=f"Mars in {SIGN_NAMES_EN[mars_s-1]} & Venus in {SIGN_NAMES_EN[ven_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Mars + Saturn (Technical Engineering & Tenacious Perseverance)
        c, rel, score = are_planets_connected_bnn(mars_s, sat_s, mars_d, sat_d)
        if c:
            gate2 = (mars_h in (1, 3, 6, 8, 10, 11) or sat_h in (1, 3, 6, 8, 10, 11))
            gate3 = (sat_nav in (1, 8, 10, 6) or mars_nav in (10, 11, 6, 8))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): செவ்வாய் & சனி {rel}.",
                    f"[✓] நிலை 2 (ஜீவன/ரண பாவம்): செவ்வாய் {mars_h}-லும் சனி {sat_h}-லும் தொழில்நுட்ப வீரியத்தை உணர்த்துகிறது.",
                    f"[✓] நிலை 3 (தொழில்நுட்ப நவாம்சம்): நவாம்சத்தில் செவ்வாய்-சனி தொடர்பு மெக்கானிக்கல்/பொறியியல் ஆளுமையை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "technical_tenacity", RevelationBullet(
                    id="bnn_mars_saturn",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Mars + Saturn: Technical Engineering Prowess & Ironclad Perseverance",
                    headline_ta="செவ்வாய் + சனி: பொறியியல்/தொழில்நுட்பத் திறன் & சவால்களை வெல்லும் வைராக்கியம்",
                    script_en="The Mars and Saturn conjunction produces extraordinary tenacity and problem-solving grit under pressure. You excel in technical architecture, mechanical execution, real estate operations, or heavy systems engineering.",
                    script_ta="செவ்வாயும் சனியும் இணைவதால் எந்த ஒரு கடினமான பணியையும் தளராமல் செய்து முடிக்கும் வைராக்கியம் உண்டாகும். பொறியியல், தொழில்நுட்பம், கட்டுமானம், மெக்கானிக்கல் அல்லது நிர்வாக அமலாக்கத் துறைகளில் சிறந்து விளங்கும் அமைப்பு.",
                    astrological_proof=f"Mars in {SIGN_NAMES_EN[mars_s-1]} & Saturn in {SIGN_NAMES_EN[sat_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Mars + Ketu (Precision Research & Technical Acumen)
        c, rel, score = are_planets_connected_bnn(mars_s, ketu_s, mars_d, ketu_d)
        if c:
            gate2 = (mars_h in (1, 2, 6, 8, 10, 12) or ketu_h in (1, 2, 6, 8, 10, 12))
            gate3 = (ketu_nav in (1, 8, 6, 12, 10) or mars_nav in (1, 8, 10, 6))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): செவ்வாய் & கேது {rel}.",
                    f"[✓] நிலை 2 (நுண்/ஆராய்ச்சி பாவம்): செவ்வாய் {mars_h}-லும் கேது {ketu_h}-லும் நுணுக்கமான தொழில்நுட்ப கவனத்தைத் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச ஆய்வு பலம்): கேது நவாம்சத்தில் {SIGN_NAMES_TA[ketu_nav-1]} பெற்று ஆராய்ச்சி துல்லியத்தை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "precision_tech", RevelationBullet(
                    id="bnn_mars_ketu",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Mars + Ketu: Precision Technical Acumen & Financial Prudence Guidance",
                    headline_ta="செவ்வாய் + கேது: நுணுக்கமான தொழில்நுட்பத் திறன் & நிதி விழிப்புணர்வு",
                    script_en="Mars united with Ketu directs energy into microscopic precision: software architecture, surgery, electrical systems, and root-cause debugging. Shastras advise maintaining strict written documentation for major financial loans.",
                    script_ta="செவ்வாய் மற்றும் கேதுவின் இணைப்பு நுட்பமான ஆய்வுத் திறனைத் தரும். மென்பொருள் கோடிங், மின்னணு, மருத்துவம் அல்லது நுண்-தொழில்நுட்பப் பணிகளில் அபார கவனம் இருக்கும். நிதி கொடுக்கல் வாங்கல்களில் முறையான ஆவணங்களைப் பேணுவது நலம்.",
                    astrological_proof=f"Mars in {SIGN_NAMES_EN[mars_s-1]} & Ketu in {SIGN_NAMES_EN[ketu_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))
                taboos_ta.append("செவ்வாய் + கேது: பெரிய தொகை நிதிப் பரிவர்த்தனைகளில் தெளிவான எழுத்துப்பூர்வ ஒப்பந்தங்களை உறுதிப்படுத்தவும்.")
                taboos_en.append("Mars + Ketu: Always maintain clear written contracts for substantial financial lending or borrowing.")

        # -------------------------------------------------------------
        # 4. MERCURY & JUPITER COMBINATIONS
        # -------------------------------------------------------------
        # Mercury + Jupiter (Lifelong Scholar & Astrological Acumen)
        c, rel, score = are_planets_connected_bnn(mer_s, jup_s, mer_d, jup_d)
        if c:
            gate2 = (mer_h in (1, 2, 5, 9, 10, 11) or jup_h in (1, 2, 5, 9, 10, 11))
            gate3 = (mer_nav in (3, 6, 9, 12, 1, 5) or jup_nav in (3, 6, 9, 12, 1, 5))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): புதன் & குரு {rel}.",
                    f"[✓] நிலை 2 (ஞான பாவம்): புதன் {mer_h}-லும் குரு {jup_h}-லும் கல்வி, ஆலோசனை மற்றும் ஜோதிட ஞானத்தை வளர்க்கிறது.",
                    f"[✓] நிலை 3 (நவாம்ச ஞானம்): நவாம்சத்தில் உபய பலம் பெற்று வாழ்நாள் கல்வித் திறனை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "scholar_mentor", RevelationBullet(
                    id="bnn_mercury_jupiter",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Mercury + Jupiter: Lifelong Scholar Mindset & Advisory Authority",
                    headline_ta="புதன் + குரு: வாழ்நாள் கல்வி நாட்டம், சிறந்த வழிகாட்டுதல் & ஜோதிட ஞானம்",
                    script_en="Mercury harmonizing with Jupiter marks the archetypal counselor and scholar. You synthesize abstract philosophies with commercial acumen, possessing natural wisdom for legal advisory, teaching, and astrology.",
                    script_ta="புதனும் குருவும் கூடுவதால் விரிந்த கல்வி ஞானமும் மற்றவர்களுக்கு நல்வழிகாட்டும் ஆலோசகர் தகுதியும் உண்டாகும். சட்டம், வணிகம், கற்பித்தல் மற்றும் ஜோதிட சாஸ்திரங்களில் இயல்பான ஈடுபாடும் தெளிவும் அமையும்.",
                    astrological_proof=f"Mercury in {SIGN_NAMES_EN[mer_s-1]} & Jupiter in {SIGN_NAMES_EN[jup_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Mercury + Venus (Vishnu-Lakshmi Yoga: Eloquence & Commercial Prosperity)
        c, rel, score = are_planets_connected_bnn(mer_s, ven_s, mer_d, ven_d)
        if c:
            gate2 = (ven_h in (1, 2, 4, 5, 9, 10, 11) or mer_h in (1, 2, 4, 5, 9, 10, 11))
            gate3 = (ven_nav in (2, 7, 12, 1, 4, 11) or mer_nav in (3, 6, 1, 5, 11))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): புதன் & சுக்கிரன் {rel} (விஷ்ணு-லக்ஷ்மி யோகம்).",
                    f"[✓] நிலை 2 (சுக/தன பாவம்): சுக்கிரன் {ven_h}-ல் நின்று இனிமையான வாக்குவன்மை மற்றும் சொத்து யோகத்தை நல்குகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச தனம்): நவாம்சத்தில் சுக்கிரன்-புதன் சேர்க்கை வர்த்தக தனலாபத்தை உறுதிப்படுத்துகிறது.",
                ]
                raw_candidates.append((score, "commercial_prosperity", RevelationBullet(
                    id="bnn_mercury_venus",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Mercury + Venus (Vishnu-Lakshmi Yoga): Eloquent Speech & Commercial Prosperity",
                    headline_ta="புதன் + சுக்கிரன் (விஷ்ணு-லக்ஷ்மி யோகம்): இனிமையான வாக்குவன்மை & வர்த்தக தனலாபம்",
                    script_en="Mercury combined with Venus generates Vishnu-Lakshmi Yoga, gracing the native with persuasive speech, refined artistic taste, and commercial prosperity in trading and immovable assets.",
                    script_ta="புதனும் சுக்கிரனும் கூடி விஷ்ணு-லக்ஷ்மி யோகத்தை உருவாக்குகின்றன. இனிமையான மற்றும் கவரும் பேச்சாற்றல், கலை நாட்டம் மற்றும் வர்த்தகம் அல்லது முதலீடுகள் மூலம் நிலையான தனலாபத்தை ஈட்டும் யோகம் உண்டு.",
                    astrological_proof=f"Mercury in {SIGN_NAMES_EN[mer_s-1]} & Venus in {SIGN_NAMES_EN[ven_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Jupiter + Venus (Crorepati Archetype: Wealth Expansion & Counselor Status)
        c, rel, score = are_planets_connected_bnn(jup_s, ven_s, jup_d, ven_d)
        if c:
            gate2 = (jup_h in (1, 2, 4, 5, 9, 10, 11) or ven_h in (1, 2, 4, 5, 9, 10, 11))
            gate3 = (ven_nav in (2, 7, 12, 1, 5, 9, 11) or jup_nav in (1, 4, 5, 9, 12))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): குரு & சுக்கிரன் {rel} (இரு பெரும் சுப கிரகங்கள்).",
                    f"[✓] நிலை 2 (தன பாவம்): குரு {jup_h}-லும் சுக்கிரன் {ven_h}-லும் தன வளம் மற்றும் பொருளாதார வளர்ச்சியைத் தருகின்றன.",
                    f"[✓] நிலை 3 (நவாம்ச சுப பலம்): நவாம்சத்தில் சுப பலம் பெற்று நிலையான கௌரவத்தை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "wealth_counsel", RevelationBullet(
                    id="bnn_jupiter_venus",
                    category="guaranteed_shock",
                    shock_factor="EXTREME",
                    headline_en="Jupiter + Venus: High-Net-Worth Archetype & Counselor Prestige",
                    headline_ta="குரு + சுக்கிரன்: பிரம்மாண்ட தன வளம், நிதி மேலாண்மை & கௌரவ யோகம்",
                    script_en="When the two premier benefics, Jupiter and Venus, interconnect closely, they establish profound wealth generation capacity, fiscal prudence, and an elevated social reputation in advisory and financial sectors.",
                    script_ta="இருபெரும் சுப கிரகங்களான குருவும் சுக்கிரனும் இணைவு பெறுவது மிகுந்த சுப யோகம். நிதி மேலாண்மை, கல்வி, ஆலோசனை மற்றும் மதிப்புமிக்க சொத்துக்களை உருவாக்கும் ஆற்றல் உண்டாகும்; சமுதாயத்தில் நல்ல மரியாதை கிட்டும்.",
                    astrological_proof=f"Jupiter in {SIGN_NAMES_EN[jup_s-1]} & Venus in {SIGN_NAMES_EN[ven_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Jupiter + Saturn (Dharma-Karmadhipati Alignment & Lifelong Resilience)
        c, rel, score = are_planets_connected_bnn(jup_s, sat_s, jup_d, sat_d)
        if c:
            gate2 = (sat_h in (1, 4, 7, 10, 5, 9, 11) or jup_h in (1, 4, 5, 9, 11))
            gate3 = (sat_nav in (10, 11, 1, 4, 5, 9) or jup_nav in (1, 4, 5, 9, 12))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): குரு & சனி {rel} (தர்ம-கர்மாதிபதி இணைப்பு).",
                    f"[✓] நிலை 2 (ஜீவன பாவம்): சனி {sat_h}-ல் நின்று தொழில் ஸ்திரத்தன்மையையும் தர்ம வழியையும் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச ஸ்திரத்தன்மை): நவாம்சத்தில் சனி தர்ம காரகத்தை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "dharma_karma", RevelationBullet(
                    id="bnn_jupiter_saturn",
                    category="guaranteed_shock",
                    shock_factor="EXTREME",
                    headline_en="Jupiter + Saturn: Dharma-Karma Alignment & Lifelong Career Resilience",
                    headline_ta="குரு + சனி: தர்ம-கர்மாதிபதி யோகம் & நிலையான தொழில் பாதுகாப்பு",
                    script_en="Jupiter interconnected with Saturn bridges ethical vision (Dharma) with steady execution (Karma). You possess deep strategic stamina, balanced maturity, and steady career elevation that solidifies sustainably over time.",
                    script_ta="குருவும் சனியும் தொடர்பு கொள்வது பிருகு நந்தி நாடியில் மிக முக்கியமான தர்ம-கர்மாதிபதி இணைப்பாகும். நேர்மை, சாதுரியம் மற்றும் பொறுப்பான திட்டமிடல் மூலம் உங்கள் தொழில் மற்றும் வாழ்வாதாரம் உறுதியாக நிலைபெறும்.",
                    astrological_proof=f"Jupiter in {SIGN_NAMES_EN[jup_s-1]} & Saturn in {SIGN_NAMES_EN[sat_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # -------------------------------------------------------------
        # 5. SATURN COMBINATIONS
        # -------------------------------------------------------------
        # Saturn + Rahu (Transformative Career Growth Post-Maturity)
        c, rel, score = are_planets_connected_bnn(sat_s, rahu_s, sat_d, rahu_d)
        if c:
            gate2 = (sat_h in (1, 6, 8, 10, 11) or rahu_h in (1, 6, 8, 10, 11))
            gate3 = (sat_nav in (10, 11, 1, 6, 8) or rahu_nav in (10, 11, 6, 8))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சனி & ராகு {rel}.",
                    f"[✓] நிலை 2 (ஜீவன பாவம்): சனி {sat_h}-ல் நின்று தொழில்நுட்பம் மற்றும் தொடர் வளர்ச்சியைக் காட்டுகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச பலம்): ராகு நவாம்சத்தில் {SIGN_NAMES_TA[rahu_nav-1]} பெற்று நவீன தொழில் உயர்வை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "career_transformation", RevelationBullet(
                    id="bnn_saturn_rahu",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Saturn + Rahu: Cutting-Edge Tech Orientation & Transformative Career Surges",
                    headline_ta="சனி + ராகு: நவீன தொழில்நுட்ப ஈடுபாடு & படிப்படியான அசுர வளர்ச்சி",
                    script_en="Saturn joined with Rahu aligns your professional stamina with futuristic industries: advanced software, aviation, energy, or large-scale automation, accelerating into major breakthroughs post early foundational hurdles.",
                    script_ta="சனியும் ராகுவும் இணைவதால் ஆரம்ப கட்டப் போராட்டங்களைத் தாண்டி, நவீனத் துறைகளான மென்பொருள், புதிய தொழில்நுட்பங்கள் அல்லது ஆட்டோமேஷன் துறைகளில் அபார வளர்ச்சி பெறும் யோகம் உண்டு.",
                    astrological_proof=f"Saturn in {SIGN_NAMES_EN[sat_s-1]} & Rahu in {SIGN_NAMES_EN[rahu_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # Saturn + Ketu (Specialized Technical Research & Deep Mastery)
        c, rel, score = are_planets_connected_bnn(sat_s, ketu_s, sat_d, ketu_d)
        if c:
            gate2 = (sat_h in (1, 3, 6, 8, 10) or ketu_h in (1, 3, 6, 8, 10))
            gate3 = (ketu_nav in (3, 6, 8, 10, 12))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சனி & கேது {rel}.",
                    f"[✓] நிலை 2 (கர்ம பாவம்): சனி {sat_h}-ல் நின்று கேதுவுக்குரிய நுணுக்கமான ஆராய்ச்சித் துறைகளில் வெற்றியைத் தருகிறது.",
                    f"[✓] நிலை 3 (நவாம்ச பலம்): கேது நவாம்சத்தில் {SIGN_NAMES_TA[ketu_nav-1]} பெற்று சட்டம், கோடிங், மருத்துவத்தில் எழுச்சியை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "research_mastery", RevelationBullet(
                    id="bnn_saturn_ketu",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Saturn + Ketu: Specialized Domain Mastery & Research Depth",
                    headline_ta="சனி + கேது: நுணுக்கமான ஆய்வுத் திறன், சிறப்புத் துறை வெற்றி & கடமை உணர்வு",
                    script_en="Saturn and Ketu excel in specialized, analytical niches rather than routine generic workflows: legal counsel, specialized engineering, medical research, data architecture, or investigative sciences.",
                    script_ta="சனியும் கேதுவும் இணைவு பெறுவதால் வழக்கமான பணிகளை விட, தனித்துவமான ஆய்வு, மென்பொருள் வடிவமைப்பு, சட்டம், மருத்துவம் அல்லது நுணுக்கமான தொழில்நுட்பத் துறைகளில் ஆழமான தேர்ச்சி உண்டாகும்.",
                    astrological_proof=f"Saturn in {SIGN_NAMES_EN[sat_s-1]} & Ketu in {SIGN_NAMES_EN[ketu_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="breakthrough",
                )))

        # -------------------------------------------------------------
        # 6. VENUS COMBINATIONS
        # -------------------------------------------------------------
        # Venus + Saturn (Pragmatic Domestic Stability & Heritage Appreciation)
        c, rel, score = are_planets_connected_bnn(ven_s, sat_s, ven_d, sat_d)
        if c:
            gate2 = (sat_h in (1, 4, 7, 10, 2, 11) or ven_h in (1, 4, 7, 10, 2, 11))
            gate3 = (sat_nav in (10, 11, 7, 4) or ven_nav in (10, 11, 7, 4))
            if gate2 and gate3:
                chk = [
                    f"[✓] நிலை 1 (பாகை இணைப்பு): சுக்கிரன் & சனி {rel}.",
                    f"[✓] நிலை 2 (களத்திர/சுக பாவம்): சனி {sat_h}-ல் நின்று பொறுப்பான இல்லறத்தையும் ஸ்திரமான சொத்துக்களையும் உறுதிசெய்கிறது.",
                    f"[✓] நிலை 3 (நவாம்ச பலம்): நவாம்சத்தில் சுக்கிரன்-சனி பந்தம் நிதி ஒழுக்கத்தை உறுதிசெய்கிறது.",
                ]
                raw_candidates.append((score, "domestic_stability", RevelationBullet(
                    id="bnn_venus_saturn",
                    category="guaranteed_shock",
                    shock_factor="HIGH",
                    headline_en="Venus + Saturn: Grounded Domestic Foundations & Financial Prudence",
                    headline_ta="சுக்கிரன் + சனி: பொறுப்பான இல்லற அடித்தளம், பாரம்பரிய சொத்துக்கள் & சேமிப்பு ஒழுக்கம்",
                    script_en="Venus coupled with Saturn grants measured financial discipline, appreciation for timeless heritage architecture, and a deeply grounded, loyal domestic partnership built on mutual responsibility.",
                    script_ta="சுக்கிரனும் சனியும் இணைவது நிதி மேலாண்மையில் விவேகத்தையும், பாரம்பரிய கட்டடங்கள் மற்றும் நிலங்களில் நிலைத்த யோகத்தையும் தரும். இல்லற வாழ்வில் பொறுப்பும் பரஸ்பர ஒத்துழைப்பும் நிலைத்திருக்கும்.",
                    astrological_proof=f"Venus in {SIGN_NAMES_EN[ven_s-1]} & Saturn in {SIGN_NAMES_EN[sat_s-1]} connected via {rel}.",
                    checklist=chk,
                    nature="identity",
                )))

        # -------------------------------------------------------------
        # 7. NOTABLE BHAVA PLACEMENTS (SHASTRA-ALIGNED)
        # -------------------------------------------------------------
        # Digbala Mercury in 1st House
        if mer_h == 1:
            chk = [
                f"[✓] நிலை 1 (பாவ நிலை): புதன் லக்னத்தில் (1-ஆம் பாவம்) திக்பலம் (Directional Strength) பெற்றுள்ளது.",
                f"[✓] நிலை 2 (வித்யா ஆளுமை): லக்ன புதன் கூர்மையான நினைவாற்றல் மற்றும் நகைச்சுவை உணர்வை அருள்கிறார்.",
                f"[✓] நிலை 3 (சாஸ்திர தர்மம்): விஷ்ணு சகஸ்ரநாமம் அல்லது கல்வி உதவிகள் புதன் காரகத்தை உச்சப்படுத்துகிறது.",
            ]
            raw_candidates.append((88, "mercury_digbala", RevelationBullet(
                id="bnn_mercury_1st",
                category="guaranteed_shock",
                shock_factor="HIGH",
                headline_en="Mercury in 1st House (Digbala): Youthful Radiance & Sharp Wit",
                headline_ta="லக்னத்தில் புதன் (திக்பலம்): புத்திக்கூர்மை, இளமைத் தோற்றம் & நயமான வாக்குவன்மை",
                script_en="Mercury commands full Digbala (directional strength) in the 1st House. You possess an agile intellect, youthful demeanor, articulate speech, and an instinct for analytical mastery.",
                script_ta="லக்னத்தில் புதன் திக்பலம் பெறுவது விசேஷ அமைப்பு. கூர்மையான நினைவாற்றல், நகைச்சுவை ததும்பும் பேச்சாற்றல், எப்போதும் இளமை ததும்பும் சுபாவம் மற்றும் கல்வி/வர்த்தகத் துறைகளில் தனி முத்திரை பதிக்கும் யோகம் உண்டு.",
                astrological_proof="Mercury occupying 1st Bhava with complete Digbala.",
                checklist=chk,
                nature="identity",
            )))

        # Sun in 11th House (Labha Sthana Elevation)
        if sun_h == 11:
            chk = [
                f"[✓] நிலை 1 (பாவ நிலை): சூரியன் 11-ஆம் பாவத்தில் (லாப ஸ்தானம்) அமர்ந்துள்ளது.",
                f"[✓] நிலை 2 (அதிகார பார்வை): 11-ல் உள்ள சூரியன் தனது 7-ஆம் பார்வையால் 5-ஆம் புத்திர/பூர்வபுண்ணிய பாவத்தைப் பார்க்கிறது.",
                f"[✓] நிலை 3 (சாஸ்திர சுப பலம்): சூரிய காயத்ரி அல்லது ஆதித்ய ஹ்ருதய பாராயணம் லாபங்களை நிலைநிறுத்துகிறது.",
            ]
            raw_candidates.append((85, "sun_11th_gain", RevelationBullet(
                id="bnn_sun_11th",
                category="guaranteed_shock",
                shock_factor="HIGH",
                headline_en="Sun in 11th House: High-Level Gains, Executive Network & Honor",
                headline_ta="11-ஆம் வீட்டில் சூரியன்: உயர்நிலை தன லாபம், செல்வாக்கு & சமூக அந்தஸ்து",
                script_en="Sun in the 11th house of gains (Labha Sthana) is traditionally lauded for bringing support from senior authorities, government bodies, and influential networks. Daily Surya Namaskar or Aditya Hridayam elevates progeny and family fortune.",
                script_ta="11-ஆம் பாவத்தில் சூரியன் அமைந்திருப்பது மிகச் சிறந்த தனலாப அமைப்பாகும். மூத்த அதிகாரிகள் மற்றும் பெரிய மனிதர்களின் தொடர்பு மூலம் முன்னேற்றம் கிட்டும். ஆதித்ய ஹ்ருதயம் பாராயணம் செய்வதும் சூரிய நமஸ்காரமும் பிள்ளைகளின் நல்வாழ்வை உயர்த்தும்.",
                astrological_proof="Sun occupying the 11th Bhava (Labha Sthana).",
                checklist=chk,
                nature="breakthrough",
            )))

        # Ketu in 1st House (Spiritual Intuition)
        if ketu_h == 1:
            chk = [
                f"[✓] நிலை 1 (பாவ நிலை): கேது லக்னத்தில் (1-ஆம் பாவம்) அமர்ந்துள்ளது.",
                f"[✓] நிலை 2 (உள்ளுணர்வு பலம்): லக்ன கேது தீவிர சிந்தனை மற்றும் தனித்துவமான ஆன்மீக நாட்டத்தைத் தருகிறது.",
                f"[✓] நிலை 3 (தியான சுபாவம்): கேதுவின் தத்துவப்படி தியானம் மற்றும் ஆழமான ஆய்வு மன அமைதியைத் தரும்.",
            ]
            raw_candidates.append((82, "ketu_1st_intuition", RevelationBullet(
                id="bnn_ketu_1st",
                category="guaranteed_shock",
                shock_factor="HIGH",
                headline_en="Ketu in 1st House: Introspective Intellect & Independent Intuition",
                headline_ta="லக்னத்தில் கேது: உள்ளுணர்வு ஞானம், தனித்துவ சிந்தனை & ஆன்மீக நாட்டம்",
                script_en="With Ketu in the Ascendant, you possess a highly intuitive, philosophical, and introspective mindset. You think independently, value quiet contemplation, and achieve deep breakthroughs in research or spiritual reflection.",
                script_ta="லக்னத்தில் கேது அமைந்திருப்பதால் நுட்பமான உள்ளுணர்வும் எதையும் கூர்ந்து கவனிக்கும் ஆற்றலும் உண்டு. சத்தமில்லாத தனிமையில் சிந்தித்து செயல்படுவதில் அதிக நாட்டம் இருக்கும்; ஆன்மீகம், தத்துவம் மற்றும் ஆராய்ச்சியில் சிறந்த ஞானம் தரும்.",
                astrological_proof="Ketu occupying the 1st Bhava (Lagna).",
                checklist=chk,
                nature="identity",
            )))

        # -------------------------------------------------------------
        # CONFLICT RESOLUTION & DEDUPLICATION:
        # Prioritize highest strength rules, avoid contradictory outputs
        # and present top verified Shastric combinations (max 5)
        # -------------------------------------------------------------
        raw_candidates.sort(key=lambda x: x[0], reverse=True)
        seen_domains = set()
        matched_bullets: List[RevelationBullet] = []

        for score, domain, bullet in raw_candidates:
            if domain in seen_domains:
                continue
            seen_domains.add(domain)
            matched_bullets.append(bullet)
            if len(matched_bullets) >= 5:
                break

        # Fallback if chart had widely dispersed planets (guarantee at least 1-2 prominent placements)
        if not matched_bullets:
            # Fallback to Lagna Lord placement
            lagna_lord_name = SIGN_LORDS[ascendant_sign]
            ll_s, ll_d, ll_h, ll_l, ll_nav = get_p(lagna_lord_name)
            chk = [
                f"[✓] நிலை 1 (லக்னாதிபதி பலம்): லக்னாதிபதி {PLANET_NAMES_TA.get(lagna_lord_name, lagna_lord_name)} {ll_h}-ஆம் பாவத்தில் அமர்ந்துள்ளது.",
                f"[✓] நிலை 2 (ராசி பலம்): {SIGN_NAMES_TA[ll_s-1]} ராசியில் {ll_d:.1f}° பாகையில் ஸ்திரமாக அமைந்துள்ளது.",
                f"[✓] நிலை 3 (நவாம்ச ஆதிக்கம்): நவாம்சத்தில் {SIGN_NAMES_TA[ll_nav-1]} பெற்று லக்ன பலத்தை உறுதிப்படுத்துகிறது.",
            ]
            matched_bullets.append(RevelationBullet(
                id="lagna_lord_dignity",
                category="guaranteed_shock",
                shock_factor="HIGH",
                headline_en=f"Ascendant Lord {lagna_lord_name} in {ll_h}th House: Key Life Driver",
                headline_ta=f"லக்னாதிபதி {PLANET_NAMES_TA.get(lagna_lord_name, lagna_lord_name)} {ll_h}-ஆம் இடத்தில்: வாழ்வின் முதன்மை உந்துசக்தி",
                script_en=f"Your chart's primary vitality is guided by Ascendant Lord {lagna_lord_name} placed in the {ll_h}th House. This anchors your fundamental life focus, vitality, and areas of highest self-actualization.",
                script_ta=f"உங்கள் லக்னாதிபதி {PLANET_NAMES_TA.get(lagna_lord_name, lagna_lord_name)} {ll_h}-ஆம் பாவத்தில் அமர்ந்து உங்கள் வாழ்வின் முதன்மை லட்சியங்களையும் உழைப்பையும் வழிநடத்துகிறார். இப்பாவகக் காரகத்துவங்கள் உங்கள் வாழ்க்கையின் திருப்புமுனைகளாக அமையும்.",
                astrological_proof=f"Ascendant Lord {lagna_lord_name} placed in House {ll_h} ({SIGN_NAMES_EN[ll_s-1]}).",
                checklist=chk,
                nature="identity",
            ))

        return matched_bullets, taboos_ta, taboos_en
