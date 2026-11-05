"""Instant Revelation Engine.

Synthesizes high-precision astrological calculations (Jamakkol Prasanam, Brighu Naadi,
Vimshottari Dasa-Bhukti-Anthara, Gochara transits) into conversational, cold-reading
teleprompter scripts for consulting astrologers.
"""

from __future__ import annotations

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from zoneinfo import ZoneInfo

from app.schemas.common import BirthInput
from app.schemas.instant_revelation import (
    InstantRevelationRequest,
    InstantRevelationResponse,
    RevelationBullet,
    FutureTimelineWindow,
)
from app.services.timezone_utils import resolve_birth_datetime
from app.services.ephemeris import (
    compute_planetary_positions,
    compute_ascendant_and_houses,
    get_sign_info,
    get_nakshatra_detail,
)
from app.services.dasa_service import calculate_dasa
from app.services.brighu_naadi.engine import evaluate_brighu_naadi
from app.services.jamakkol.calculator import calculate_jamakkol_prasanam

logger = logging.getLogger(__name__)

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

BODY_MARK_MAP = {
    1: {"en": "head, forehead, or upper face", "ta": "தலை, நெற்றி அல்லது முகத்தின் மேல் பகுதி"},
    2: {"en": "throat, neck, or lower jaw", "ta": "தொண்டை, கழுத்து அல்லது தாடைப் பகுதி"},
    3: {"en": "shoulders, collarbone, or right arm", "ta": "தோள்பட்டை, கழுத்தெலும்பு அல்லது வலது கை"},
    4: {"en": "chest, ribs, or breast area", "ta": "மார்பு, விலா எலும்பு அல்லது நெஞ்சுப் பகுதி"},
    5: {"en": "upper spine, heart center, or back", "ta": "முதுகெலும்பு, இதயப் பகுதி அல்லது மேல் முதுகு"},
    6: {"en": "lower abdomen, waist, or navel area", "ta": "அடிவயிறு, இடுப்பு அல்லது தொப்புள் பகுதி"},
    7: {"en": "pelvis, groin, or lower lumbar spine", "ta": "இடுப்பெலும்பு, அடி இடுப்பு அல்லது கீழ் முதுகு"},
    8: {"en": "private organs, tailbone, or upper thigh", "ta": "மர்மஸ்தானம், வால் எலும்பு அல்லது மேல் தொடை"},
    9: {"en": "hips, thighs, or arterial joints", "ta": "இடுப்பு, தொடை அல்லது மூட்டுப் பகுதி"},
    10: {"en": "knees, knee-caps, or joints", "ta": "முழங்கால், மூட்டு சில்லு அல்லது மூட்டுகள்"},
    11: {"en": "shins, calves, or left leg", "ta": "கால் கெண்டைக்கால், முழங்கால் கீழ் பகுதி அல்லது இடது கால்"},
    12: {"en": "feet, soles, or ankles", "ta": "பாதம், உள்ளங்கால் அல்லது கணுக்கால் பகுதி"},
}


class InstantRevelationEngine:
    """Master engine for synthesizing instant customer arrival revelations."""

    @classmethod
    def analyze(cls, req: InstantRevelationRequest) -> InstantRevelationResponse:
        """Run complete instant revelation synthesis."""
        # 1. Resolve Birth Particulars
        birth_local_dt, birth_utc_dt, birth_jd, tz_name, offset_hours = resolve_birth_datetime(
            req.birth_date,
            req.birth_time,
            req.timezone,
        )

        ayanamsa_id = req.ayanamsa or 0
        gender = (req.gender or "male").lower()
        client_name = req.name or "Client / ஜாதகர்"

        # 2. Compute Natal Planetary Positions & Ascendant
        planets_raw = compute_planetary_positions(birth_jd, ayanamsa_id=ayanamsa_id, include_outer=True)
        asc_info, mc_info, houses_raw = compute_ascendant_and_houses(
            birth_jd,
            lat=req.latitude,
            lon=req.longitude,
            ayanamsa_id=ayanamsa_id,
            house_system_id=0,
        )

        ascendant_sign = asc_info.sign_index
        lagna_sign_ta = SIGN_NAMES_TA[ascendant_sign - 1]
        lagna_sign_en = SIGN_NAMES_EN[ascendant_sign - 1]

        # Structure planets_data for Brighu Naadi and local lookup
        planets_dict: Dict[str, Dict[str, Any]] = {}
        for p in planets_raw:
            p_name = getattr(p, "name", "")
            lon = getattr(p, "longitude", 0.0) % 360.0
            sign_idx = getattr(p, "sign_index", int(lon // 30.0) + 1)
            is_retro = getattr(p, "is_retrograde", False)
            planets_dict[p_name] = {
                "longitude": lon,
                "sign_index": sign_idx,
                "degree": lon % 30.0,
                "is_retrograde": is_retro,
            }

        natal_moon_sign = planets_dict.get("Moon", {}).get("sign_index", 1)
        natal_moon_ta = SIGN_NAMES_TA[natal_moon_sign - 1]
        natal_moon_en = SIGN_NAMES_EN[natal_moon_sign - 1]

        # 3. Determine Consultation / Arrival Moment
        arrival_tz = ZoneInfo(req.timezone)
        if req.consultation_time:
            try:
                arrival_dt = datetime.fromisoformat(req.consultation_time)
                if arrival_dt.tzinfo is None:
                    arrival_dt = arrival_dt.replace(tzinfo=arrival_tz)
                else:
                    arrival_dt = arrival_dt.astimezone(arrival_tz)
            except Exception:
                arrival_dt = datetime.now(arrival_tz)
        else:
            arrival_dt = datetime.now(arrival_tz)

        arrival_lat = req.consultation_latitude if req.consultation_latitude is not None else req.latitude
        arrival_lon = req.consultation_longitude if req.consultation_longitude is not None else req.longitude
        arrival_iso = arrival_dt.isoformat()

        # 4. Compute Jamakkol Prasanam for Arrival Moment
        jamakkol_res = calculate_jamakkol_prasanam(
            query_dt_str=arrival_iso,
            latitude=arrival_lat,
            longitude=arrival_lon,
            tz_str=req.timezone,
            ayanamsa_id=ayanamsa_id,
        )

        pillars = jamakkol_res.get("three_pillars", {})
        udhayam_sign = pillars.get("udhayam", {}).get("sign_index", 1)
        aarudham_sign = pillars.get("aarudham", {}).get("sign_index", 1)
        kavippu_sign = pillars.get("kavippu", {}).get("sign_index", 1)

        # Calculate Jamakkol House Offsets
        aarudham_house = ((aarudham_sign - udhayam_sign) % 12) + 1
        kavippu_house = ((kavippu_sign - udhayam_sign) % 12) + 1

        # Current Transit Moon
        transit_moon_info = next((tp for tp in jamakkol_res.get("transit_planets", []) if tp.get("name_en") == "Moon"), None)
        transit_moon_sign = transit_moon_info["sign_index"] if transit_moon_info else 1
        chandra_lagna_offset = ((transit_moon_sign - natal_moon_sign) % 12) + 1
        natal_lagna_offset = ((transit_moon_sign - ascendant_sign) % 12) + 1

        # 5. Compute Active Vimshottari Dasa Tree & Active Path
        birth_input = BirthInput(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            timezone=req.timezone,
            latitude=req.latitude,
            longitude=req.longitude,
        )

        dasa_res = calculate_dasa(
            birth=birth_input,
            depth=3,
            ayanamsa_id=ayanamsa_id,
            target_date=arrival_dt.date(),
        )

        active_path = dasa_res.active_period
        current_md = active_path.mahadasha if active_path else "Jupiter"
        current_ad = active_path.antardasha if active_path else "Saturn"
        current_pd = active_path.pratyantardasha if active_path else "Mercury"

        current_md_ta = PLANET_NAMES_TA.get(current_md, current_md)
        current_ad_ta = PLANET_NAMES_TA.get(current_ad, current_ad)
        current_pd_ta = PLANET_NAMES_TA.get(current_pd, current_pd)

        current_dasa_str_en = f"{current_md} Dasa - {current_ad} Bhukti - {current_pd} Anthara"
        current_dasa_str_ta = f"{current_md_ta} தசை - {current_ad_ta} புக்தி - {current_pd_ta} அந்தரம்"

        # Calculate Native Current Age
        current_year = arrival_dt.year
        birth_year = birth_local_dt.year
        native_age = current_year - birth_year
        if (arrival_dt.month, arrival_dt.day) < (birth_local_dt.month, birth_local_dt.day):
            native_age -= 1
        native_age = max(1, native_age)

        # 6. Evaluate Brighu Naadi Sangraha
        bnn_res = evaluate_brighu_naadi(
            planets_data=planets_dict,
            ascendant_sign=ascendant_sign,
            gender=gender,
        )

        # ------------------------------------------------------------------
        # PILLAR 1: THE MIND READER (Why You Came Here Today)
        # ------------------------------------------------------------------
        mind_bullets, primary_en, primary_ta = cls._synthesize_arrival_reason(
            aarudham_house=aarudham_house,
            kavippu_house=kavippu_house,
            chandra_lagna_offset=chandra_lagna_offset,
            natal_lagna_offset=natal_lagna_offset,
            current_md=current_md,
            current_ad=current_ad,
            current_pd=current_pd,
            current_dasa_ta=current_dasa_str_ta,
            natal_moon_ta=natal_moon_ta,
            natal_moon_en=natal_moon_en,
            lagna_sign_ta=lagna_sign_ta,
            lagna_sign_en=lagna_sign_en,
        )

        # ------------------------------------------------------------------
        # PILLAR 2: VERIFIABLE PAST HITS (Shock-Value Cold Proof)
        # ------------------------------------------------------------------
        past_hits = cls._synthesize_past_hits(
            bnn_res=bnn_res,
            dasa_tree=dasa_res.dasa_tree,
            birth_year=birth_year,
            current_age=native_age,
            ascendant_sign=ascendant_sign,
            planets_dict=planets_dict,
        )

        # ------------------------------------------------------------------
        # PILLAR 3: PERSONAL & DOMESTIC IDENTIFIERS
        # ------------------------------------------------------------------
        personal_markers = cls._synthesize_personal_markers(
            bnn_res=bnn_res,
            ascendant_sign=ascendant_sign,
            planets_dict=planets_dict,
        )

        # ------------------------------------------------------------------
        # PILLAR 4: EXACT FUTURE TIMELINE WINDOWS (Next 12–24 Months)
        # ------------------------------------------------------------------
        future_windows = cls._synthesize_future_windows(
            dasa_tree=dasa_res.dasa_tree,
            arrival_date=arrival_dt.date(),
            ascendant_sign=ascendant_sign,
            planets_dict=planets_dict,
        )

        # ------------------------------------------------------------------
        # PILLAR 5: TURN-KEY INSTANT REMEDY
        # ------------------------------------------------------------------
        remedy_data = cls._synthesize_instant_remedy(
            current_md=current_md,
            current_ad=current_ad,
            ascendant_sign=ascendant_sign,
            kavippu_house=kavippu_house,
        )

        # ------------------------------------------------------------------
        # FAST 10-SECOND GLANCE TELEPROMPTER
        # ------------------------------------------------------------------
        door_en_clean = bnn_res.birth_environment.door_facing_en.replace("Facing ", "")
        door_ta_clean = bnn_res.birth_environment.door_facing_ta.replace("நோக்கிய தலைவாசல்", "").strip()
        first_hit_period = past_hits[0].calendar_period.replace("Age ", "") if past_hits and past_hits[0].calendar_period else "24-26"

        glance_en = [
            f"Arrival Cause: {primary_en}",
            f"Active Running Cycle: {current_dasa_str_en}",
            f"Vastu Check: Main door faces {door_en_clean}, road runs {bnn_res.birth_environment.road_direction_en}.",
            f"Past Verification: Major life event around age {first_hit_period}.",
            f"Next Urgent Action: {remedy_data['temple_en']} - {remedy_data['action_en']}",
        ]

        glance_ta = [
            f"வருகை நோக்கம்: {primary_ta}",
            f"நடப்பு தசா காலம்: {current_dasa_str_ta}",
            f"வீட்டு வாஸ்து: தலைவாசல் {door_ta_clean} திசை, பாதை {bnn_res.birth_environment.road_direction_ta}.",
            f"கடந்த கால உண்மை: சுமார் {first_hit_period} வயதில் பெரிய திருப்புமுனை / மாற்றம்.",
            f"உடனடி பரிகாரம்: {remedy_data['temple_ta']} - {remedy_data['action_ta']}",
        ]

        return InstantRevelationResponse(
            name=client_name,
            birth_date=req.birth_date,
            current_age=native_age,
            current_dasa_summary=current_dasa_str_en,
            current_dasa_summary_ta=current_dasa_str_ta,
            arrival_moment_iso=arrival_iso,
            primary_arrival_reason_en=primary_en,
            primary_arrival_reason_ta=primary_ta,
            arrival_reason_bullets=mind_bullets,
            past_verifiable_hits=past_hits,
            personal_and_home_markers=personal_markers,
            future_windows=future_windows,
            instant_remedy_en=remedy_data["primary_en"],
            instant_remedy_ta=remedy_data["primary_ta"],
            temple_recommendation_en=remedy_data["temple_en"],
            temple_recommendation_ta=remedy_data["temple_ta"],
            daily_karma_action_en=remedy_data["action_en"],
            daily_karma_action_ta=remedy_data["action_ta"],
            gem_or_rudraksha_en=remedy_data["gem_en"],
            gem_or_rudraksha_ta=remedy_data["gem_ta"],
            quick_glance_teleprompter_en=glance_en,
            quick_glance_teleprompter_ta=glance_ta,
        )

    # ----------------------------------------------------------------------
    # Helper: Synthesize Arrival Reason (Mind-Reading)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_arrival_reason(
        cls,
        aarudham_house: int,
        kavippu_house: int,
        chandra_lagna_offset: int,
        natal_lagna_offset: int,
        current_md: str,
        current_ad: str,
        current_pd: str,
        current_dasa_ta: str,
        natal_moon_ta: str,
        natal_moon_en: str,
        lagna_sign_ta: str,
        lagna_sign_en: str,
    ) -> Tuple[List[RevelationBullet], str, str]:
        bullets: List[RevelationBullet] = []

        # 1. Primary Diagnosis from Jamakkol Aarudham & Kavippu
        if aarudham_house in (10, 1) or kavippu_house == 10:
            primary_en = "Career Upheaval, Workplace Politics, or Sudden Status Threat"
            primary_ta = "தொழில் முடக்கம், உத்தியோக நெருக்கடி அல்லது வேலை இழப்பு அச்சம்"
            script_en = (
                "You have arrived today primarily due to intense professional turbulence and insecurity. "
                "In the last 45 to 60 days, an anticipated promotion or business opportunity was stalled, "
                "or colleagues/superiors have acted against you. You are contemplating whether to quit or hold on."
            )
            script_ta = (
                "நீங்கள் இன்று இங்கு வந்து அமர்ந்திருப்பதன் முதன்மையான காரணம், உங்கள் தொழில் அல்லது வேலையில் "
                "ஏற்பட்டுள்ள கடுமையான தேக்கமும் நிம்மதியின்மையுமே ஆகும். கடந்த 45 முதல் 60 நாட்களாக "
                "எதிர்பார்த்த பதவி உயர்வு அல்லது வியாபார வாய்ப்பு தடைபட்டுள்ளது அல்லது உடன் பணிபுரிபவர்களால் "
                "குடைச்சல் ஏற்பட்டுள்ளது. வேலையை விட்டுவிடலாமா அல்லது தொடரலாமா என்ற குழப்பம் உங்கள் மனதில் ஓடுகிறது."
            )
            proof = f"Jamakkol Aarudham in {aarudham_house}th house, Kavippu in {kavippu_house}th house affecting Karma Bhava."

        elif aarudham_house in (7, 5) or kavippu_house == 7:
            primary_en = "Marital Discord, Relationship Coldness, or Alliance Delays"
            primary_ta = "களத்திரப் போராட்டம், திருமணத் தடை அல்லது தாம்பத்யத்தில் கடும் பிரிவு"
            script_en = (
                "You have come to me carrying severe emotional weight regarding your marriage or life partner. "
                "There is deep communication breakdown, mutual suspicion, or outside family interference that has "
                "drained your peace of mind. If seeking marriage, promising proposals have collapsed at the final stage."
            )
            script_ta = (
                "உங்கள் வாழ்க்கைத் துணை அல்லது திருமண விவகாரத்தில் ஏற்பட்டுள்ள கடுமையான மனவேதனையுடன் "
                "நீங்கள் இன்று வந்துள்ளீர்கள். கணவன்-மனைவிக்குள் பேச்சுவார்த்தை குறைந்து, கருத்து வேறுபாடு அல்லது "
                "மூன்றாம் நபர்களின் தலையீட்டால் மன அமைதி பறிபோயுள்ளது. வரன் தேடுபவராக இருந்தால், "
                "கடைசி நேரத்தில் கைநழுவிப் போன வரன்களால் ஏமாற்றம் அடைந்துள்ளீர்கள்."
            )
            proof = f"Jamakkol Aarudham in 7th Kalathra Bhava, Kavippu afflicting relationship axis ({kavippu_house}th house)."

        elif aarudham_house in (2, 11) or kavippu_house in (2, 11):
            primary_en = "Frozen Finances, Blocked Payments, and Liquidity Trap"
            primary_ta = "கடுமையான பணத் தட்டுப்பாடு, வர வேண்டிய பணம் முடக்கம் மற்றும் கடன் அழுத்தம்"
            script_en = (
                "Your primary agitation today is financial choking. Money that belongs to you and was promised "
                "weeks ago has been unfairly blocked. You are struggling to meet immediate commitments and feeling "
                "that people whom you helped in the past are now ignoring your calls."
            )
            script_ta = (
                "இன்று உங்கள் மனதில் உள்ள மிகப்பெரிய பாரம் பண நெருக்கடி மற்றும் முடக்கப்பட்ட தனம் ஆகும். "
                "உங்களுக்கு வரவேண்டிய நியாயமான பணம் பல வாரங்களாகக் கிடைக்காமல் இழுத்தடிக்கப்படுகிறது. "
                "முன்பு நீங்கள் வலியச் சென்று உதவி செய்த நபர்கள் கூட, இன்று உங்கள் அழைப்பைத் தவிர்க்கின்றனர். "
                "கடன் மற்றும் பணத் தேவைகள் உங்கள் கழுத்தை நெரிக்கின்றன."
            )
            proof = f"Jamakkol Kavippu in {kavippu_house}th house blocking Dhana/Labha sthanas."

        elif aarudham_house in (6, 8, 12) or kavippu_house in (6, 8):
            primary_en = "Hidden Enemies, Sudden Health Vulnerability, or Debt Trap"
            primary_ta = "மறைமுக எதிர்ப்புகள், உடல்நலக் கோளாறு மற்றும் எதிர்பாராத அவப்பெயர் அச்சம்"
            script_en = (
                "You are under tremendous psychological pressure from unforeseen obstacles. "
                "You suspect someone is working against you behind the scenes. Along with debt pressure, "
                "your sleep is fragmented and physical vitality (digestion/legs) feels completely depleted."
            )
            script_ta = (
                "யாரோ உங்களுக்குப் பின்னால் நின்று சதி செய்வதைப் போன்ற தீவிர மன பயத்துடனும், தீராத "
                "கடன்/வழக்கு அல்லது உடல் உபாதையுடனும் நீங்கள் வந்துள்ளீர்கள். இரவில் சரியான தூக்கமில்லை; "
                "வயிற்றுப் பகுதி அல்லது உடல் சோர்வு உங்களை வாட்டுகிறது. எதிர்பாராத இழப்பு அல்லது வீண் பழி "
                "வந்துவிடுமோ என்ற அச்சம் உங்களை ஆட்டிப்படைக்கிறது."
            )
            proof = f"Jamakkol Aarudham in Dusthana ({aarudham_house}th Bhava) with Kavippu in {kavippu_house}th house."

        else: # 4th or 9th
            primary_en = "Property Dispute, Mother's Health, or Relocation Deadlock"
            primary_ta = "சொத்து விவகாரம், தாயாரின் உடல்நலக் குறைவு அல்லது இருப்பிட மாற்றத் தடை"
            script_en = (
                "Your arrival is centered around domestic peace, land/property matters, or your mother's health. "
                "A proposed house construction, purchase, or vehicle transaction has run into documentation issues "
                "or family friction, leaving you unsettled."
            )
            script_ta = (
                "குடும்ப அமைதி, வீடு/நிலம் தொடர்பான விவகாரங்கள் அல்லது தாயாரின் உடல்நலம் குறித்த கவலையே "
                "உங்கள் வருகையின் நோக்கம். நீங்கள் நினைத்த வீடு மாற்றம் அல்லது சொத்து வாங்குதல் விவகாரத்தில் "
                "சட்டச்சிக்கல் அல்லது உறவினர்களின் முட்டுக்கட்டை ஏற்பட்டுள்ளது."
            )
            proof = f"Jamakkol Aarudham in Sukha/Bhagya Bhava ({aarudham_house}th house)."

        bullets.append(RevelationBullet(
            id="mind-01",
            category="mind_reading",
            shock_factor="EXTREME",
            headline_en="Core Mind Reading: Why You Sat Down Today",
            headline_ta="உங்களின் முதன்மையான வருகை நோக்கம்",
            script_en=script_en,
            script_ta=script_ta,
            astrological_proof=proof,
            nature="danger",
        ))

        # 2. Secondary Indicator: Transit Moon Condition
        if chandra_lagna_offset == 8:
            chandrashtama_en = (
                "Furthermore, right now you are passing through Chandrashtama (transit Moon in your 8th house). "
                "Your thoughts are running in circles, you feel an inexplicable dread, and you feel that no one understands you."
            )
            chandrashtama_ta = (
                "மேலும், தற்சமயம் உங்களுக்கு 'சந்திராஷ்டமம்' (உங்கள் ராசிக்கு 8-ல் சந்திரன்) நிலவுகிறது. "
                "இதனால் எதிலும் பிடிப்பின்மை, மன உளைச்சல் மற்றும் நீங்கள் சொல்வதை எவரும் புரிந்துகொள்ளவில்லை என்ற "
                "ஆதங்கம் உங்கள் மனதில் கொந்தளிக்கிறது."
            )
            bullets.append(RevelationBullet(
                id="mind-02",
                category="mind_reading",
                shock_factor="HIGH",
                headline_en="Mental Cross-Section: Chandrashtama Alert",
                headline_ta="மன உளைச்சல்: சந்திராஷ்டம நிலை",
                script_en=chandrashtama_en,
                script_ta=chandrashtama_ta,
                astrological_proof=f"Transit Moon currently in 8th house from natal Moon ({natal_moon_en} / {natal_moon_ta}).",
                nature="danger",
            ))
        elif chandra_lagna_offset in (6, 12):
            bullets.append(RevelationBullet(
                id="mind-02",
                category="mind_reading",
                shock_factor="HIGH",
                headline_en="Sleeplessness & Expense Outflow",
                headline_ta="தூக்கமின்மை மற்றும் திடீர் விரயங்கள்",
                script_en="Over the last 72 hours, money has slipped through your hands unexpectedly, and sleep has eluded you past 2:30 AM.",
                script_ta="கடந்த 3 நாட்களாக எதிர்பாராத வீண் விரயங்கள் ஏற்பட்டுள்ளன; அதிகாலை 2:30 மணி வரை தூக்கம் வராமல் தவிக்கிறீர்கள்.",
                astrological_proof=f"Transit Moon activating 6th/12th Dusthana from Natal Moon.",
                nature="danger",
            ))

        # 3. Active Dasa-Bhukti context
        bullets.append(RevelationBullet(
            id="mind-03",
            category="mind_reading",
            shock_factor="HIGH",
            headline_en="Active Shastric Planetary Cycle",
            headline_ta="நடப்பு தசா-புக்தியின் நேரடித் தாக்கம்",
            script_en=f"You are actively running {current_md} Dasa with {current_ad} Bhukti and {current_pd} Anthara. Whatever promises are made to you are dragging until the very last minute.",
            script_ta=f"தற்போது உங்களுக்கு {current_dasa_ta} நடக்கிறது. எவர் உங்களுக்கு வாக்குறுதி கொடுத்தாலும், அது கடைசி நிமிடம் வரை இழுத்தடித்துதான் நடக்கும் நிலை உள்ளது.",
            astrological_proof=f"Native natal dasha timing: {current_md}-{current_ad}-{current_pd}.",
            nature="neutral",
        ))

        return bullets, primary_en, primary_ta

    # ----------------------------------------------------------------------
    # Helper: Synthesize Verifiable Past Hits (Shock Cold Proof)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_past_hits(
        cls,
        bnn_res: Any,
        dasa_tree: List[Any],
        birth_year: int,
        current_age: int,
        ascendant_sign: int,
        planets_dict: Dict[str, Dict[str, Any]],
    ) -> List[RevelationBullet]:
        hits: List[RevelationBullet] = []

        # 1. Past Career / Life Turning Point from BNN Milestones list
        milestones: List[Any] = getattr(bnn_res, "timing_milestones", [])

        # Relocation / Travel
        travel_m = next((m for m in milestones if m.category == "travel"), None)
        if travel_m:
            for age in travel_m.age_years:
                if age < current_age:
                    reloc_year = birth_year + age
                    hits.append(RevelationBullet(
                        id=f"past-relo-{age}",
                        category="past_hit",
                        shock_factor="EXTREME",
                        headline_en="Major Relocation or Career Turning Point",
                        headline_ta="பெரிய இடமாற்றம் அல்லது தொழில் திருப்புமுனை",
                        script_en=(
                            f"Around age {age} (approximately calendar year {reloc_year} to {reloc_year + 1}): "
                            f"You experienced a decisive turning point in your life. There was a major house shift, "
                            f"city relocation, or a dramatic reset in your daily career/education."
                        ),
                        script_ta=(
                            f"சுமார் {age} வயதில் ({reloc_year} - {reloc_year + 1} ஆம் ஆண்டு காலகட்டம்): "
                            f"உங்கள் வாழ்வில் மிக முக்கியமான ஒரு திருப்புமுனை நிகழ்ந்தது. பெரிய இருப்பிட மாற்றம், "
                            f"ஊர் மாற்றம் அல்லது கல்வி/தொழிலில் முற்றிலும் புதியதொரு பாதை அப்போதுதான் துவங்கியது."
                        ),
                        astrological_proof=f"{travel_m.basis_en} - Age {age}",
                        calendar_period=f"Age {age} ({reloc_year})",
                        nature="breakthrough",
                    ))
                    break

        # Caution / Physical Vulnerability / Accident
        caution_m = next((m for m in milestones if m.category == "caution"), None)
        if caution_m:
            for age in caution_m.age_years:
                if age < current_age:
                    acc_year = birth_year + age
                    hits.append(RevelationBullet(
                        id=f"past-acc-{age}",
                        category="past_hit",
                        shock_factor="EXTREME",
                        headline_en="Sudden Injury, Burn, or Physical Vulnerability",
                        headline_ta="திடீர் விபத்து, காயம் அல்லது மருத்துவ சிகிச்சை",
                        script_en=(
                            f"Around age {age} (approximately {acc_year}): "
                            f"You suffered a sharp physical shock—a sudden fall, vehicle skid, deep cut, burn mark, "
                            f"or an acute fever/surgery that required intense medical attention."
                        ),
                        script_ta=(
                            f"சுமார் {age} வயதில் ({acc_year} ஆம் ஆண்டு): "
                            f"உங்களுக்கு எதிர்பாராத ஒரு உடல் உபாதை, கீழே விழுந்து அடிபடுதல், வாகனம் சறுக்குதல், "
                            f"வெட்டுக் காயம், தீக்காயம் அல்லது திடீர் தீவிர மருத்துவ சிகிச்சை ஏற்பட்டது."
                        ),
                        astrological_proof=f"{caution_m.basis_en} - Age {age}",
                        calendar_period=f"Age {age} ({acc_year})",
                        nature="danger",
                    ))
                    break

        # Property / Asset Acquisition
        prop_m = next((m for m in milestones if m.category == "property"), None)
        if prop_m:
            for age in prop_m.age_years:
                if age < current_age:
                    prop_year = birth_year + age
                    hits.append(RevelationBullet(
                        id=f"past-prop-{age}",
                        category="past_hit",
                        shock_factor="HIGH",
                        headline_en="Major Asset / Land / Vehicle Acquisition",
                        headline_ta="சொத்து, நிலம் அல்லது புதிய வாகனம் சேர்க்கை",
                        script_en=(
                            f"Around age {age} ({prop_year}): "
                            f"You or your family registered a notable immovable property, constructed a home, "
                            f"or purchased a significant vehicle that marked an upgrade in status."
                        ),
                        script_ta=(
                            f"சுமார் {age} வயதில் ({prop_year} ஆம் ஆண்டு): "
                            f"நீங்கள் அல்லது உங்கள் குடும்பத்தினர் ஒரு புதிய நிலம், வீடு வாங்குதல், வீடு கட்டுதல் "
                            f"அல்லது ஒரு முக்கிய வாகன சேர்க்கையை வெற்றிகரமாகச் செய்தீர்கள்."
                        ),
                        astrological_proof=f"{prop_m.basis_en} - Age {age}",
                        calendar_period=f"Age {age} ({prop_year})",
                        nature="breakthrough",
                    ))
                    break

        # Check Past Dasa Transition (always a huge shock hit!)
        for node in dasa_tree:
            node_end_date = getattr(node, "end_date_iso", None)
            if node_end_date:
                try:
                    end_dt = date.fromisoformat(node_end_date[:10])
                    end_yr = end_dt.year
                    if (birth_year + 12) <= end_yr <= (birth_year + current_age - 1):
                        lord_en = node.lord
                        lord_ta = PLANET_NAMES_TA.get(lord_en, lord_en)
                        hits.append(RevelationBullet(
                            id=f"past-dasa-{end_yr}",
                            category="past_hit",
                            shock_factor="EXTREME",
                            headline_en="Major Life Cycle / Dasa Transition Shock",
                            headline_ta="தசா மாற்றம்: வாழ்வின் மாபெரும் தலைகீழ் மாற்றம்",
                            script_en=(
                                f"In year {end_yr}: You concluded your {lord_en} Mahadasha. That specific year "
                                f"brought a massive internal and external upheaval—old friendships dropped off, "
                                f"a dependable revenue stream closed, and you were forced to reinvent yourself."
                            ),
                            script_ta=(
                                f"{end_yr} ஆம் ஆண்டில்: உங்கள் {lord_ta} மகாதிசை நிறைவடைந்தது. அந்த குறிப்பிட்ட "
                                f"ஆண்டில் உங்கள் வாழ்க்கை தலைகீழாக மாறியது; பழைய நண்பர்கள் விலகினர், வழக்கமான "
                                f"வருமானம் தடைபட்டு நீங்கள் முற்றிலும் புதியதொரு களத்திற்கு மாற வேண்டியதாயிற்று."
                            ),
                            astrological_proof=f"Vimshottari Dasha transition from {lord_en} Mahadasha at Julian boundary.",
                            calendar_period=f"Year {end_yr}",
                            nature="danger",
                        ))
                        break
                except Exception:
                    pass

        # If we still have fewer than 2 hits, add career trigger
        career_m = next((m for m in milestones if m.category == "career"), None)
        if len(hits) < 3 and career_m:
            for age in career_m.age_years:
                if age < current_age:
                    c_year = birth_year + age
                    hits.append(RevelationBullet(
                        id=f"past-career-{age}",
                        category="past_hit",
                        shock_factor="HIGH",
                        headline_en="First Independent Income / Professional Genesis",
                        headline_ta="சுய சம்பாத்தியம் மற்றும் தொழில் உதயம்",
                        script_en=f"Around age {age} ({c_year}): You earned your first substantial independent income or began your professional voyage.",
                        script_ta=f"சுமார் {age} வயதில் ({c_year} ஆம் ஆண்டு): நீங்கள் முதன்முதலில் சுய சம்பாத்தியம் ஈட்டத் துவங்கினீர்கள் அல்லது உங்கள் சொந்த உழைப்பில் காலடி எடுத்து வைத்தீர்கள்.",
                        astrological_proof=f"{career_m.basis_en} - Age {age}",
                        calendar_period=f"Age {age} ({c_year})",
                        nature="breakthrough",
                    ))
                    break

        return hits[:3]

    # ----------------------------------------------------------------------
    # Helper: Synthesize Personal & Domestic Identifiers (Cold Reading)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_personal_markers(
        cls,
        bnn_res: Any,
        ascendant_sign: int,
        planets_dict: Dict[str, Dict[str, Any]],
    ) -> List[RevelationBullet]:
        markers: List[RevelationBullet] = []
        env = bnn_res.birth_environment

        # 1. Domestic Vastu: Door Facing & Road Direction
        door_en = env.door_facing_en
        door_ta = env.door_facing_ta
        road_en = env.road_direction_en
        road_ta = env.road_direction_ta
        temple_en = env.temple_near_birth_en
        temple_ta = env.temple_near_birth_ta

        markers.append(RevelationBullet(
            id="marker-vastu",
            category="personal_marker",
            shock_factor="EXTREME",
            headline_en="Birth Residence Vastu & Surroundings",
            headline_ta="பிறந்த வீட்டின் வாஸ்து மற்றும் சுற்றுப்புறம்",
            script_en=(
                f"Your ancestral/birth home has its main entrance {door_en}. "
                f"The street or road directly in front runs {road_en}. Furthermore, within close walking "
                f"proximity of the birthplace, there is a prominent {temple_en}."
            ),
            script_ta=(
                f"நீங்கள் பிறந்த வீட்டின் பிரதான தலைவாசல் {door_ta} நோக்கி அமைந்துள்ளது. "
                f"வீட்டின் முன் செல்லும் சாலை {road_ta} செல்கிறது. மேலும், உங்கள் பிறந்த இடத்திற்கு "
                f"அருகில் ஒரு பிரசித்தி பெற்ற {temple_ta} உள்ளது."
            ),
            astrological_proof="Brighu Naadi Sangraha: Rahu-Ketu door vector & Sun devata sthana.",
            nature="identity",
        ))

        # 2. Physical Scar / Mole Marker
        mars_sign = planets_dict.get("Mars", {}).get("sign_index", ascendant_sign)
        body_target = BODY_MARK_MAP.get(mars_sign, BODY_MARK_MAP.get(ascendant_sign, {"en": "shoulder or head", "ta": "தோள்பட்டை அல்லது தலை"}))

        markers.append(RevelationBullet(
            id="marker-body",
            category="personal_marker",
            shock_factor="HIGH",
            headline_en="Physical Identification Mark (Mole / Scar)",
            headline_ta="உடலில் அமைந்த மச்சம் / தழும்பு அடையாளம்",
            script_en=f"You possess a clear identification mark—a prominent mole, burn mark, or childhood scar—on your {body_target['en']}.",
            script_ta=f"உங்கள் உடலில் ஒரு தெளிவான அடையாளம்—குறிப்பாக {body_target['ta']}யில் ஒரு தழும்பு, மச்சம் அல்லது தழும்பு போன்ற அடையாளம் நிச்சயமாக இருக்கும்.",
            astrological_proof=f"Classical Saravali & BNN: Mars placed in {SIGN_NAMES_EN[mars_sign - 1]} governing anatomical sector.",
            nature="identity",
        ))

        # 3. Family Lineage / Maternal Trait
        moon_sign = planets_dict.get("Moon", {}).get("sign_index", 1)
        markers.append(RevelationBullet(
            id="marker-family",
            category="personal_marker",
            shock_factor="HIGH",
            headline_en="Maternal Health / Lineage Vulnerability",
            headline_ta="தாயார் வழி உடல்நலம் மற்றும் குடும்ப சுபாவம்",
            script_en="Your mother or maternal relatives have a chronic vulnerability toward joint pain, knee stiffness, or acidity/phlegm complaints.",
            script_ta="உங்கள் தாயார் அல்லது தாய்வழி உறவினர்களுக்கு முழங்கால் வலி, மூட்டு தேய்மானம் அல்லது நாள்பட்ட வாயு/கபம் தொடர்பான தொந்தரவுகள் இருப்பது இயல்பு.",
            astrological_proof="Matru Karaka Moon and 4th Bhava dosha signature.",
            nature="identity",
        ))

        return markers

    # ----------------------------------------------------------------------
    # Helper: Synthesize Future Timeline Windows (Next 12–24 Months)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_future_windows(
        cls,
        dasa_tree: List[Any],
        arrival_date: date,
        ascendant_sign: int,
        planets_dict: Dict[str, Dict[str, Any]],
    ) -> List[FutureTimelineWindow]:
        windows: List[FutureTimelineWindow] = []

        # Find periods spanning arrival_date to arrival_date + 730 days
        limit_date = arrival_date + timedelta(days=730)

        # Collect active and upcoming level-2 (Bhukti) or level-3 (Anthara) nodes
        flat_periods: List[Any] = []
        for md_node in dasa_tree:
            for ad_node in md_node.sub_periods:
                flat_periods.append((md_node.lord, ad_node))

        # Filter periods that intersect or start after arrival_date
        relevant: List[Tuple[str, Any]] = []
        for md_lord, ad_node in flat_periods:
            s_iso = ad_node.start_date_iso
            e_iso = ad_node.end_date_iso
            if not s_iso or not e_iso:
                continue
            s_d = date.fromisoformat(s_iso[:10])
            e_d = date.fromisoformat(e_iso[:10])
            if e_d >= arrival_date and s_d <= limit_date:
                relevant.append((md_lord, ad_node))

        # If none matched, synthesize fallback from current date
        if not relevant:
            d1 = arrival_date
            d2 = d1 + timedelta(days=90)
            d3 = d2 + timedelta(days=180)
            windows.append(FutureTimelineWindow(
                start_date=d1.isoformat(),
                end_date=d2.isoformat(),
                status="RED_ALERT",
                title_en="High Caution Phase: Restrict Commitments",
                title_ta="கவனமாக இருக்க வேண்டிய எச்சரிக்கை காலம்",
                script_en="For the next 90 days, do not lend money, do not quit your job in anger, and do not sign unverified agreements.",
                script_ta="அடுத்த 90 நாட்களுக்கு யாரிடமும் கடன் கொடுக்காதீர்கள்; கோபத்தில் வேலையை விடாதீர்கள்; அவசரப்பட்டு ஒப்பந்தங்களில் கையெழுத்திடாதீர்கள்.",
                do_rules_en=["Consolidate existing savings", "Maintain routine duties", "Chant Gayatri / Vishnu Sahasranama"],
                do_rules_ta=["இருப்பதை தக்கவைத்துக் கொள்ளவும்", "வழக்கமான பணிகளில் கவனம் செலுத்தவும்", "குலதெய்வ வழிபாடு செய்யவும்"],
                dont_rules_en=["No speculative stock investments", "No partnership disputes", "No vehicle speeding"],
                dont_rules_ta=["ஊக வணிக முதலீடுகள் வேண்டாம்", "கூட்டாளி சண்டைகள் வேண்டாம்", "வேகமாக வாகனம் ஓட்டுவதை தவிர்க்கவும்"],
            ))
            return windows

        for idx, (md_lord, ad_node) in enumerate(relevant[:3]):
            ad_lord = ad_node.lord
            s_d_str = ad_node.start_date_iso[:10]
            e_d_str = ad_node.end_date_iso[:10]
            md_ta = PLANET_NAMES_TA.get(md_lord, md_lord)
            ad_ta = PLANET_NAMES_TA.get(ad_lord, ad_lord)

            # Classify period nature
            is_malefic_sub = ad_lord in ("Rahu", "Ketu", "Saturn", "Mars")
            is_benefic_sub = ad_lord in ("Jupiter", "Venus", "Mercury")

            if is_malefic_sub:
                status = "RED_ALERT"
                title_en = f"Caution Window: {md_lord}-{ad_lord} Period"
                title_ta = f"எச்சரிக்கை காலம்: {md_ta}-{ad_ta} காலம்"
                script_en = (
                    f"From {s_d_str} to {e_d_str}: This is a high-friction window. Keep your temper in check. "
                    f"Avoid starting new litigations, avoid lending money to relatives, and do not make aggressive job switches."
                )
                script_ta = (
                    f"{s_d_str} முதல் {e_d_str} வரை: இது விழிப்புடன் இருக்க வேண்டிய காலக்கட்டம். "
                    f"யாரிடமும் வாக்குவாதம் செய்ய வேண்டாம்; உறவினர்களுக்குக் கடன் கொடுப்பதைத் தவிர்க்கவும்; "
                    f"ஆத்திரத்தில் வேலையை விட்டுவிட்டு புதிய முயற்சியில் இறங்க வேண்டாம்."
                )
                dos_en = ["Keep cash reserves intact", "Propitiate Navagraha & Kuladeivam", "Be conservative in speech"]
                dos_ta = ["பணத்தை பத்திரமாக வைத்திருக்கவும்", "குலதெய்வத்தை வழிபடவும்", "பேச்சில் நிதானம் காக்கவும்"]
                donts_en = ["Do not sign property sale deeds", "Do not guarantee loans for others", "Do not travel late at night"]
                donts_ta = ["ஜாமீன் கையெழுத்து போட வேண்டாம்", "சொத்து அவசர விற்பனை வேண்டாம்", "இரவு நேர பயணங்களை தவிர்க்கவும்"]

            elif is_benefic_sub:
                status = "GOLDEN_BREAKTHROUGH"
                title_en = f"Golden Breakthrough Window: {md_lord}-{ad_lord} Period"
                title_ta = f"வெற்றி மற்றும் திருப்புமுனை காலம்: {md_ta}-{ad_ta} காலம்"
                script_en = (
                    f"From {s_d_str} to {e_d_str}: Definite relief and victory! Delayed payments will be recovered, "
                    f"career promotions will materialize, and an auspicious family event will be finalized."
                )
                script_ta = (
                    f"{s_d_str} முதல் {e_d_str} வரை: மிகப்பெரிய நிம்மதியும் வெற்றியும் தேடி வரும் காலம்! "
                    f"தடைபட்ட பணம் வசூலாகும்; புதிய வேலை அல்லது வியாபார வளர்ச்சி உறுதியாகும்; "
                    f"குடும்பத்தில் சுப காரியப் பேச்சுக்கள் முடிவாகும்."
                )
                dos_en = ["Launch new professional initiatives", "Finalize property or marriage matters", "Invest in productive assets"]
                dos_ta = ["புதிய தொழில் முயற்சிகளைத் துவங்கலாம்", "திருமணம் / சொத்து காரியங்களை முடிக்கலாம்", "சுப காரியங்களை முன்னெடுக்கலாம்"]
                donts_en = ["Do not procrastinate", "Do not disclose plans prematurely to critics"]
                donts_ta = ["காரியங்களை தள்ளிப்போட வேண்டாம்", "எதிரிகளிடம் திட்டங்களை முன்கூட்டியே சொல்ல வேண்டாம்"]

            else:
                status = "PREPARATION"
                title_en = f"Transition & Consolidation: {md_lord}-{ad_lord} Period"
                title_ta = f"நிலைப்படுத்துதல் மற்றும் தயாரிப்பு காலம்: {md_ta}-{ad_ta} காலம்"
                script_en = (
                    f"From {s_d_str} to {e_d_str}: A period of gradual stabilization. Build your foundations quietly, "
                    f"clear pending debts, and do not expect overnight miracles."
                )
                script_ta = (
                    f"{s_d_str} முதல் {e_d_str} வரை: வாழ்க்கை படிப்படியாக சீராகும் காலம். "
                    f"நிலுவையில் உள்ள வேலைகளை முடிக்கவும்; கடன் பாக்கிகளை அடைக்க திட்டமிடவும்; அவசரப்படாமல் நிதானமாக முன்னேறவும்."
                )
                dos_en = ["Clear existing backlog", "Focus on health and wellness", "Maintain steady routines"]
                dos_ta = ["பழைய பாக்கிகளை அடைக்கவும்", "உடல் ஆரோக்கியத்தில் கவனம் செலுத்தவும்", "அமைதியாக உழைக்கவும்"]
                donts_en = ["Do not overextend your budget", "Do not enter into emotional partnerships"]
                donts_ta = ["வரவுக்கு மீறி செலவு செய்ய வேண்டாம்", "உணர்ச்சிவசப்பட்டு முடிவெடுக்க வேண்டாம்"]

            windows.append(FutureTimelineWindow(
                start_date=s_d_str,
                end_date=e_d_str,
                status=status,
                title_en=title_en,
                title_ta=title_ta,
                script_en=script_en,
                script_ta=script_ta,
                do_rules_en=dos_en,
                do_rules_ta=dos_ta,
                dont_rules_en=donts_en,
                dont_rules_ta=donts_ta,
            ))

        return windows

    # ----------------------------------------------------------------------
    # Helper: Synthesize Turn-Key Instant Remedy
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_instant_remedy(
        cls,
        current_md: str,
        current_ad: str,
        ascendant_sign: int,
        kavippu_house: int,
    ) -> Dict[str, str]:
        # Planetary Temple Mapping
        temple_map = {
            "Saturn": {
                "temple_en": "Thirunallar Saniswaran Temple or Kuchanur Saneeswaran",
                "temple_ta": "திருநள்ளாறு சனிபகவான் ஆலயம் அல்லது குச்சனூர் சுயம்பு சனீஸ்வரர்",
                "action_en": "Light a sesame oil lamp on 3 consecutive Saturdays before 8:00 AM; feed black crows cooked rice.",
                "action_ta": "தொடர்ந்து 3 சனிக்கிழமைகளில் காலை 8 மணிக்குள் நல்லெண்ணெய் தீபம் ஏற்றி வழிபடவும்; காகத்திற்கு எள் கலந்த சாதம் வைக்கவும்.",
                "gem_en": "Blue Sapphire (Neelam) or 7-Mukhi Rudraksha. Wear navy blue or dark grey.",
                "gem_ta": "நீலக்கல் அல்லது 7 முக ருத்ராட்சம். கருநீலம் அல்லது சாம்பல் நிற ஆடை உகந்தது.",
            },
            "Rahu": {
                "temple_en": "Thirunageswaram Naganathar or Sri Kalahasti Rahu-Ketu Temple",
                "temple_ta": "திருநாகேஸ்வரம் ராகு பகவான் ஆலயம் அல்லது ஸ்ரீ காளஹஸ்தி திருத்தலம்",
                "action_en": "Perform Milk Abhishekam during Rahu Kalam on a Sunday or Tuesday; feed stray animals.",
                "action_ta": "ஞாயிறு அல்லது செவ்வாய்க்கிழமை ராகு காலத்தில் பால் அபிஷேகம் செய்து வழிபடவும்; தெருவோர பிராணிகளுக்கு உணவு அளிக்கவும்.",
                "gem_en": "Hessonite (Gomed) or 8-Mukhi Rudraksha. Avoid pitch-black clothing on auspicious days.",
                "gem_ta": "கோமேதகம் அல்லது 8 முக ருத்ராட்சம். சுப தினங்களில் அடர் கருப்பு ஆடைகளைத் தவிர்க்கவும்.",
            },
            "Ketu": {
                "temple_en": "Keezhaperumpallam Naganathaswamy Temple",
                "temple_ta": "கீழப்பெரும்பள்ளம் கேது பகவான் ஆலயம்",
                "action_en": "Offer multicolored blanket to the needy; chant Ganesha Atharvashirsha.",
                "action_ta": "ஏழை எளியவர்களுக்கு பலவண்ண கம்பளி தானம் செய்யவும்; விநாயகர் அகவல் / சதுர்த்தி வழிபாடு செய்யவும்.",
                "gem_en": "Cat's Eye (Vaidooryam) or 9-Mukhi Rudraksha.",
                "gem_ta": "வைடூரியம் அல்லது 9 முக ருத்ராட்சம்.",
            },
            "Mars": {
                "temple_en": "Vaitheeswaran Koil Sevvai Sthalam (Angaraka)",
                "temple_ta": "வைத்தீஸ்வரன் கோவில் செவ்வாய் ஸ்தலம் (அங்காரகன்)",
                "action_en": "Light ghee lamp on Tuesdays to Lord Murugan; donate red lentils (Thoor dal).",
                "action_ta": "செவ்வாய்க்கிழமைகளில் முருகப்பெருமானுக்கு நெய் தீபம் ஏற்றி வழிபடவும்; துவரம்பருப்பு தானம் செய்யவும்.",
                "gem_en": "Red Coral (Pavazham) or 3-Mukhi Rudraksha. Wear shades of crimson or copper.",
                "gem_ta": "பவளம் அல்லது 3 முக ருத்ராட்சம். சிவப்பு அல்லது செப்பு நிற ஆடைகள் நலம் தரும்.",
            },
            "Jupiter": {
                "temple_en": "Alangudi Guru Sthalam or Thiruchendur Murugan Temple",
                "temple_ta": "ஆலங்குடி குரு ஸ்தலம் அல்லது திருச்செந்தூர் சுப்பிரமணிய சுவாமி திருக்கோவில்",
                "action_en": "Offer yellow chickpeas (Kondakadalai) garland to Lord Dakshinamurthy on Thursday.",
                "action_ta": "வியாழக்கிழமைகளில் தட்சிணாமூர்த்திக்கு கொண்டைக்கடலை மாலை சாற்றி வழிபடவும்.",
                "gem_en": "Yellow Sapphire (Pushparagam) or 5-Mukhi Rudraksha. Favor yellow/cream attire.",
                "gem_ta": "புஷ்பராகம் அல்லது 5 முக ருத்ராட்சம். மஞ்சள் அல்லது சந்தன நிற ஆடை சிறந்தது.",
            },
            "Venus": {
                "temple_en": "Kanjanoor Sukran Temple or Sri Rangam Ranganathar",
                "temple_ta": "கஞ்சனூர் சுக்கிரன் ஸ்தலம் அல்லது ஸ்ரீரங்கம் ரங்கநாதர் ஆலயம்",
                "action_en": "Donate white silk cloth or curd rice on Friday; honor and respect women elders.",
                "action_ta": "வெள்ளிக்கிழமைகளில் தயிர் சாதம் அல்லது வெள்ளை வஸ்திரம் தானம் செய்யவும்; பெண்களை மதிக்கவும்.",
                "gem_en": "Diamond / White Zircon or 6-Mukhi Rudraksha. Favor white and pastel tones.",
                "gem_ta": "வைரம் அல்லது 6 முக ருத்ராட்சம். வெள்ளை மற்றும் பட்டு ஆடைகள் சுபம் தரும்.",
            },
            "Mercury": {
                "temple_en": "Thiruvenkadu Budhan Temple or Madurai Meenakshi Amman",
                "temple_ta": "திருவெண்காடு புதன் ஸ்தலம் அல்லது மதுரை மீனாட்சி அம்மன் ஆலயம்",
                "action_en": "Feed green grass or green moong dal to a cow on Wednesday morning.",
                "action_ta": "புதன்கிழமைகளில் பசு மாடுகளுக்கு பசும்புல் அல்லது பாசிப்பயறு அளிக்கவும்.",
                "gem_en": "Emerald (Maragatham) or 4-Mukhi Rudraksha. Wear shades of green.",
                "gem_ta": "மரகதம் அல்லது 4 முக ருத்ராட்சம். பச்சை நிற ஆடைகள் புத்துணர்ச்சி தரும்.",
            },
            "Sun": {
                "temple_en": "Suryanar Koil or Thiruvannamalai Arunachaleswarar",
                "temple_ta": "சூரியனார் கோவில் அல்லது திருவண்ணாமலை அருணாசலேஸ்வரர்",
                "action_en": "Perform Surya Namaskar at sunrise and offer water (Arghya); respect father.",
                "action_ta": "காலை சூரிய உதயத்தில் சூரிய நமஸ்காரம் செய்து அர்க்கியம் விடவும்; தந்தையை வணங்கவும்.",
                "gem_en": "Ruby (Manikkam) or 1-to-12 Mukhi Rudraksha. Favor ruby red or orange tones.",
                "gem_ta": "மாணிக்கம் அல்லது 1 முக ருத்ராட்சம். செம்மஞ்சள் நிற ஆடைகள் உகந்தது.",
            },
            "Moon": {
                "temple_en": "Thingalur Chandran Temple or Tirupati Sri Venkateswara",
                "temple_ta": "திங்களூர் சந்திரன் ஸ்தலம் அல்லது திருப்பதி வெங்கடாசலபதி ஆலயம்",
                "action_en": "Offer milk / kheer to the destitute on Mondays; seek mother's blessings daily.",
                "action_ta": "திங்கட்கிழமைகளில் ஆதரவற்றோருக்கு பால் பாயாசம் வழங்கவும்; தாயாரின் பாதம் தொட்டு வணங்கவும்.",
                "gem_en": "Natural Pearl (Muthu) or 2-Mukhi Rudraksha. Favor silver and white.",
                "gem_ta": "முத்து அல்லது 2 முக ருத்ராட்சம். வெண்மை மற்றும் வெள்ளி ஆபரணங்கள் நன்று.",
            },
        }

        # Check dominant affliction planet: Antardasha lord first, then Mahadasha lord
        target_planet = current_ad if current_ad in temple_map else current_md
        data = temple_map.get(target_planet, temple_map["Saturn"])

        primary_en = f"Propitiate {target_planet} at {data['temple_en']} to immediately dissolve current blockages."
        primary_ta = f"தற்போதைய தடைகள் நீங்க {data['temple_ta']} சென்று {PLANET_NAMES_TA.get(target_planet, target_planet)} பகவானை வழிபடவும்."

        return {
            "primary_en": primary_en,
            "primary_ta": primary_ta,
            "temple_en": data["temple_en"],
            "temple_ta": data["temple_ta"],
            "action_en": data["action_en"],
            "action_ta": data["action_ta"],
            "gem_en": data["gem_en"],
            "gem_ta": data["gem_ta"],
        }
