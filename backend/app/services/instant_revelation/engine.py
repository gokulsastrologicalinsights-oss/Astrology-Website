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

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
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

        # Determine Active Dasha & Bhukti Activated Bhavas from Lagna
        planet_signs_map = {
            "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
            "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11],
            "Rahu": [], "Ketu": [],
        }

        def get_planet_bhavas(pname: str) -> set[int]:
            bhavas: set[int] = set()
            p_sign = planets_dict.get(pname, {}).get("sign_index")
            if p_sign:
                bhavas.add(((p_sign - ascendant_sign) % 12) + 1)
            for s in planet_signs_map.get(pname, []):
                bhavas.add(((s - ascendant_sign) % 12) + 1)
            return bhavas

        ad_houses = get_planet_bhavas(current_ad)
        md_houses = get_planet_bhavas(current_md)

        # ------------------------------------------------------------------
        # PILLAR 1: THE MIND READER (Why You Came Here Today)
        # ------------------------------------------------------------------
        mind_bullets, primary_en, primary_ta = cls._synthesize_arrival_reason(
            aarudham_house=aarudham_house,
            kavippu_house=kavippu_house,
            chandra_lagna_offset=chandra_lagna_offset,
            natal_lagna_offset=natal_lagna_offset,
            native_age=native_age,
            ad_houses=ad_houses,
            md_houses=md_houses,
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
        # THE 5 SHOCK AMPLIFIERS
        # ------------------------------------------------------------------
        career_calling_en, career_calling_ta, career_fields = cls._synthesize_career_calling(planets_dict)
        birth_order_en, birth_order_ta = cls._synthesize_birth_order(planets_dict, ascendant_sign)

        transit_saturn = next((tp for tp in jamakkol_res.get("transit_planets", []) if "Saturn" in tp.get("name_en", "")), None)
        transit_saturn_sign = transit_saturn["sign_index"] if transit_saturn else 11
        transit_jupiter = next((tp for tp in jamakkol_res.get("transit_planets", []) if "Jupiter" in tp.get("name_en", "")), None)
        transit_jupiter_sign = transit_jupiter["sign_index"] if transit_jupiter else 2

        sat_phase, sat_en, sat_ta, jup_en, jup_ta = cls._synthesize_gochara_transits(
            natal_moon_sign=natal_moon_sign,
            transit_saturn_sign=transit_saturn_sign,
            transit_jupiter_sign=transit_jupiter_sign,
        )

        dasa_chidra_active, chidra_en, chidra_ta, chidra_end = cls._evaluate_dasa_chidra(
            dasa_tree=dasa_res.dasa_tree,
            arrival_date=arrival_dt.date(),
            current_md=current_md,
            current_md_ta=current_md_ta,
        )

        med_en, med_ta, vulnerable_organs = cls._synthesize_medical_vulnerability(
            ascendant_sign=ascendant_sign,
            planets_dict=planets_dict,
        )

        # ------------------------------------------------------------------
        # THE 4 ULTRA-PRECISION NADI SHOCKERS (Option B)
        # ------------------------------------------------------------------
        spouse_en, spouse_ta = cls._synthesize_spouse_secrets(
            planets_dict=planets_dict,
            ascendant_sign=ascendant_sign,
            gender=gender,
        )

        vehicle_en, vehicle_ta = cls._synthesize_vehicle_marker(
            planets_dict=planets_dict,
            ascendant_sign=ascendant_sign,
        )

        land_rift_en, land_rift_ta = cls._synthesize_ancestral_land_rift(
            planets_dict=planets_dict,
            ascendant_sign=ascendant_sign,
        )

        balarishta_en, balarishta_ta = cls._synthesize_childhood_balarishta(
            planets_dict=planets_dict,
            ascendant_sign=ascendant_sign,
        )

        # ------------------------------------------------------------------
        # FAST 10-SECOND GLANCE TELEPROMPTER
        # ------------------------------------------------------------------
        door_en_clean = bnn_res.birth_environment.door_facing_en.replace("Facing ", "")
        door_ta_clean = bnn_res.birth_environment.door_facing_ta.replace("நோக்கிய தலைவாசல்", "").strip()
        # Pick the most resonant hit period (prefer adult age >= 18 or major Dasa transition year)
        first_hit_period = "24-26"
        if past_hits:
            best_hit = None
            if native_age >= 18:
                for h in past_hits:
                    if h.calendar_period:
                        if "Year " in h.calendar_period:
                            best_hit = h
                            break
                        if "Age " in h.calendar_period:
                            try:
                                parts = h.calendar_period.split()
                                if len(parts) >= 2 and parts[1].isdigit() and int(parts[1]) >= 18:
                                    best_hit = h
                                    break
                            except Exception:
                                pass
            if not best_hit:
                best_hit = past_hits[0]
            first_hit_period = best_hit.calendar_period.replace("Age ", "").replace("Year ", "")

        if best_hit and "Year " in getattr(best_hit, "calendar_period", ""):
            hit_str_en = f"Major life transition around year {first_hit_period}."
            hit_str_ta = f"{first_hit_period} ஆம் ஆண்டில் பெரிய தசா மாற்றம் / திருப்புமுனை."
        else:
            hit_str_en = f"Major life event around age {first_hit_period}."
            hit_str_ta = f"சுமார் {first_hit_period} வயதில் பெரிய திருப்புமுனை / மாற்றம்."

        glance_en = [
            f"Arrival Cause: {primary_en}",
            f"Career Sector: {', '.join(career_fields[:2])}",
            f"Saturn Transit: {sat_phase}",
            f"Past Verification: {hit_str_en}",
            f"Next Urgent Action: {remedy_data['temple_en']} - {remedy_data['action_en']}",
        ]

        glance_ta = [
            f"வருகை நோக்கம்: {primary_ta}",
            f"தொழில் துறை: {', '.join(career_fields[:2])}",
            f"சனிப் பெயர்ச்சி: {sat_phase}",
            f"கடந்த கால உண்மை: {hit_str_ta}",
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
            career_calling_en=career_calling_en,
            career_calling_ta=career_calling_ta,
            career_fields=career_fields,
            family_birth_order_en=birth_order_en,
            family_birth_order_ta=birth_order_ta,
            gochara_saturn_phase=sat_phase,
            gochara_saturn_verdict_en=sat_en,
            gochara_saturn_verdict_ta=sat_ta,
            gochara_jupiter_verdict_en=jup_en,
            gochara_jupiter_verdict_ta=jup_ta,
            dasa_chidra_active=dasa_chidra_active,
            dasa_chidra_warning_en=chidra_en,
            dasa_chidra_warning_ta=chidra_ta,
            dasa_chidra_end_date=chidra_end,
            medical_organ_vulnerability_en=med_en,
            medical_organ_vulnerability_ta=med_ta,
            vulnerable_organs=vulnerable_organs,
            spouse_secrets_en=spouse_en,
            spouse_secrets_ta=spouse_ta,
            vehicle_marker_en=vehicle_en,
            vehicle_marker_ta=vehicle_ta,
            ancestral_land_rift_en=land_rift_en,
            ancestral_land_rift_ta=land_rift_ta,
            childhood_balarishta_en=balarishta_en,
            childhood_balarishta_ta=balarishta_ta,
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
        native_age: int,
        ad_houses: set[int],
        md_houses: set[int],
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

        # 1. Primary Diagnosis Synthesis: Natal Dasa-Bhukti Lords + Age + Jamakkol Prasanam
        if native_age < 21:
            primary_en = "Academic Uncertainty, Higher Studies Admission, or Future Career Direction"
            primary_ta = "கல்வித் தேக்கம், உயர்கல்வி தேர்வு அல்லது எதிர்கால வேலைக்கான வழிகாட்டுதல்"
            script_en = (
                "You have arrived today primarily seeking clarity regarding your education, competitive examinations, "
                "or career direction. There is uncertainty over choosing the right academic stream or securing anticipated marks."
            )
            script_ta = (
                "நீங்கள் இன்று இங்கு வந்துள்ளதன் முதன்மையான நோக்கம், உங்கள் படிப்பு, உயர்கல்வி சேர்க்கை, போட்டித் தேர்வு "
                "அல்லது எதிர்கால வேலைக்கான வழிகாட்டுதல் பற்றிய கவலையே ஆகும். எந்தத் துறையைத் தேர்ந்தெடுப்பது அல்லது தேர்வில் "
                "எதிர்பார்த்த வெற்றி கிடைக்குமா என்ற குழப்பம் உங்கள் மனதில் ஓடுகிறது."
            )
            proof = f"Native in academic age ({native_age} yrs) under {current_md}-{current_ad} Dasa cycle."

        elif any(h in (10, 1) for h in ad_houses) or (10 in md_houses) or (aarudham_house in (10, 1) and kavippu_house != 7):
            primary_en = "Career Upheaval, Workplace Politics, or Sudden Status Threat"
            primary_ta = "தொழில் முடக்கம், உத்தியோக நெருக்கடி அல்லது வேலை மாற்ற சிந்தனை"
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
            proof = f"Active Dasha Lord ({current_ad}) activating Karma Bhava (10th/1st house) with Jamakkol Aarudham in {aarudham_house}th house."

        elif (21 <= native_age <= 45) and (any(h == 7 for h in ad_houses) or (aarudham_house in (7, 5) and any(h in (7, 5, 2) for h in (ad_houses | md_houses)))):
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
            proof = f"Kalathra Bhava (7th house) activated under {current_md}-{current_ad} Dasa for age {native_age} native."

        elif any(h in (2, 11) for h in ad_houses) or (kavippu_house in (2, 11) and any(h in (2, 11) for h in md_houses)):
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
            proof = f"Dhana/Labha Bhavas (2nd/11th house) triggered by active {current_ad} Bhukti."

        elif any(h in (6, 8, 12) for h in ad_houses) or (aarudham_house in (6, 8, 12)):
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
            proof = f"Dusthana activation (6th/8th/12th house) under {current_ad} Bhukti and Jamakkol {aarudham_house}th house."

        elif any(h == 4 for h in ad_houses):
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
            proof = f"Sukha Bhava (4th house) activated under {current_ad} Bhukti."

        elif (23 <= native_age <= 48) and any(h == 5 for h in ad_houses):
            primary_en = "Progeny Delay or Children's Future Settlement"
            primary_ta = "புத்திர பாக்கிய தாமதம் அல்லது பிள்ளைகளின் எதிர்காலக் கவலை"
            script_en = (
                "Your arrival is primarily centered around progeny matters—either a delay in childbirth "
                "requiring medical/spiritual solutions, or deep anxiety regarding the settlement of your growing children."
            )
            script_ta = (
                "புத்திர பாக்கியம் அமைவதில் ஏற்பட்டுள்ள காலதாமதம் அல்லது பிள்ளைகளின் படிப்பு/எதிர்காலம் "
                "குறித்த தீவிர கவலையே உங்கள் வருகையின் நோக்கம். இதற்கான நல்வழி பிறக்குமா என்ற ஏக்கத்துடன் வந்துள்ளீர்கள்."
            )
            proof = f"Putra Bhava (5th house) activated under {current_ad} Bhukti for age {native_age}."

        else:
            primary_en = "Family Harmony, Children's Settlement, and Long-Term Stability"
            primary_ta = "குடும்ப அமைதி, நல்வாழ்வு மற்றும் எதிர்காலத்திற்கான வழிகாட்டுதல்"
            script_en = (
                "You have arrived today seeking broad guidance on overall life stability, domestic peace, "
                "and ensuring the long-term protection and settlement of your household."
            )
            script_ta = (
                "குடும்பத்தில் உள்ளவர்களின் மன அமைதி, பிள்ளைகளின் சுபகாரியங்கள் மற்றும் எதிர்கால வாழ்க்கை "
                "நல்வழியில் அமைய வேண்டும் என்ற பொதுவான நலனை நாடியே நீங்கள் இன்று வந்துள்ளீர்கள்."
            )
            proof = f"Native age {native_age} under {current_md}-{current_ad} Dasa cycle."

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

        # Relocation / Travel / Career Launch
        travel_m = next((m for m in milestones if m.category == "travel"), None)
        if travel_m:
            chosen_age = None
            if current_age >= 21:
                # Prioritize adult turning points (age 18 to current_age - 1)
                for age in travel_m.age_years:
                    if 18 <= age < current_age:
                        chosen_age = age
                        break
            if chosen_age is None:
                for age in travel_m.age_years:
                    if age < current_age:
                        chosen_age = age
                        break

            if chosen_age is not None:
                reloc_year = birth_year + chosen_age
                if chosen_age >= 18:
                    h_en = "Major Career Milestone or Life Turning Point"
                    h_ta = "பெரிய தொழில் உயர்வு அல்லது வாழ்வின் திருப்புமுனை"
                    s_en = (
                        f"Around age {chosen_age} (approximately calendar year {reloc_year} to {reloc_year + 1}): "
                        f"You experienced a decisive turning point in your career and status. There was a major job breakthrough, "
                        f"city relocation, or a bold independent chapter that reset your life path."
                    )
                    s_ta = (
                        f"சுமார் {chosen_age} வயதில் ({reloc_year} - {reloc_year + 1} ஆம் ஆண்டு காலகட்டம்): "
                        f"உங்கள் வாழ்வில் மிக முக்கியமான ஒரு தொழில் அல்லது வாழ்வாதாரத் திருப்புமுனை நிகழ்ந்தது. பெரிய இருப்பிட மாற்றம், "
                        f"புதிய வேலை அல்லது தொழிலில் முற்றிலும் புதியதொரு வெற்றிப் பாதை அப்போதுதான் துவங்கியது."
                    )
                else:
                    h_en = "Family Relocation or Academic Transition"
                    h_ta = "குடும்ப இடமாற்றம் அல்லது பள்ளிக் கல்விப் பிரிவு"
                    s_en = (
                        f"Around age {chosen_age} (approximately calendar year {reloc_year}): "
                        f"Your family experienced a significant residence shift or an important academic school change."
                    )
                    s_ta = (
                        f"சுமார் {chosen_age} வயதில் ({reloc_year} ஆம் ஆண்டு காலகட்டம்): "
                        f"உங்கள் குடும்பத்தில் ஒரு பெரிய இருப்பிட மாற்றம் அல்லது பள்ளி/கல்வி சார்ந்த புதிய சூழல் துவங்கியது."
                    )

                hits.append(RevelationBullet(
                    id=f"past-relo-{chosen_age}",
                    category="past_hit",
                    shock_factor="EXTREME",
                    headline_en=h_en,
                    headline_ta=h_ta,
                    script_en=s_en,
                    script_ta=s_ta,
                    astrological_proof=f"{travel_m.basis_en} - Age {chosen_age}",
                    calendar_period=f"Age {chosen_age} ({reloc_year})",
                    nature="breakthrough",
                ))

        # Caution / Physical Vulnerability / Accident
        caution_m = next((m for m in milestones if m.category == "caution"), None)
        if caution_m:
            chosen_c_age = None
            for age in caution_m.age_years:
                if 6 <= age < current_age:
                    chosen_c_age = age
                    break
            if chosen_c_age is None:
                for age in caution_m.age_years:
                    if age < current_age:
                        chosen_c_age = age
                        break

            if chosen_c_age is not None:
                acc_year = birth_year + chosen_c_age
                hits.append(RevelationBullet(
                    id=f"past-acc-{chosen_c_age}",
                    category="past_hit",
                    shock_factor="EXTREME",
                    headline_en="Sudden Injury, Burn, or Physical Vulnerability",
                    headline_ta="திடீர் விபத்து, காயம் அல்லது மருத்துவ சிகிச்சை",
                    script_en=(
                        f"Around age {chosen_c_age} (approximately {acc_year}): "
                        f"You suffered a sharp physical shock—a sudden fall, vehicle skid, deep cut, burn mark, "
                        f"or an acute fever/surgery that required intense medical attention."
                    ),
                    script_ta=(
                        f"சுமார் {chosen_c_age} வயதில் ({acc_year} ஆம் ஆண்டு): "
                        f"உங்களுக்கு எதிர்பாராத ஒரு உடல் உபாதை, கீழே விழுந்து அடிபடுதல், வாகனம் சறுக்குதல், "
                        f"வெட்டுக் காயம், தீக்காயம் அல்லது திடீர் தீவிர மருத்துவ சிகிச்சை ஏற்பட்டது."
                    ),
                    astrological_proof=f"{caution_m.basis_en} - Age {chosen_c_age}",
                    calendar_period=f"Age {chosen_c_age} ({acc_year})",
                    nature="danger",
                ))

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

        # If we still have fewer than 3 hits, add career trigger for working-age adults
        career_m = next((m for m in milestones if m.category == "career"), None)
        if len(hits) < 3 and career_m and current_age >= 19:
            for age in career_m.age_years:
                if 18 <= age < current_age:
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

    # ----------------------------------------------------------------------
    # Helper 1: Synthesize Career & Industry Calling
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_career_calling(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
    ) -> Tuple[str, str, List[str]]:
        sat_sign = planets_dict.get("Saturn", {}).get("sign_index", 10)
        trines_and_adjacent = {
            sat_sign,
            ((sat_sign + 4 - 1) % 12) + 1,
            ((sat_sign + 8 - 1) % 12) + 1,
            ((sat_sign + 1 - 1) % 12) + 1,
            ((sat_sign + 11 - 1) % 12) + 1,
        }

        contacted: List[str] = []
        for p_name in ["Mercury", "Mars", "Venus", "Sun", "Jupiter", "Rahu", "Ketu"]:
            p_sign = planets_dict.get(p_name, {}).get("sign_index", 1)
            if p_sign in trines_and_adjacent:
                contacted.append(p_name)

        fields: List[str] = []
        if "Mercury" in contacted:
            fields.extend(["Software & Coding", "Accounts & Auditing", "Commercial Trading", "Media & Agency"])
        if "Mars" in contacted:
            fields.extend(["Civil & Mechanical Engineering", "Real Estate & Construction", "Machinery & Tech", "Police & Defense"])
        if "Venus" in contacted:
            fields.extend(["Banking & Finance", "Luxury Goods & Media", "Automotive Industry", "Architecture & Design"])
        if "Sun" in contacted:
            fields.extend(["Government & Administration", "Public Sector Leadership", "Medical & Pharmacology"])
        if "Jupiter" in contacted:
            fields.extend(["Management & Advisory", "Law & Consulting", "Education & Training", "Trusts & Institutions"])
        if "Rahu" in contacted:
            fields.extend(["Foreign & MNC Enterprises", "Cutting-edge IT & Cloud", "Chemicals & Aviation", "Unconventional Tech"])
        if "Ketu" in contacted:
            fields.extend(["Research & Testing", "Textile & Weaving", "Legal Drafting & Arbitration", "Low-Profile Specialization"])

        if not fields:
            fields = ["Engineering & Technical Fabrication", "Logistics & Supply Operations", "Trade & Commerce"]

        primary_fields_en = ", ".join(fields[:3])
        career_en = (
            f"Your livelihood and profession are decisively anchored in {primary_fields_en}. "
            "You are not suited for a routine generic job; your mind demands practical problem-solving, "
            "handling technical systems or financial accounts, and having an independent sphere of execution."
        )
        career_ta = (
            f"உங்கள் ஜீவன தொழில் மற்றும் வருமான வழி முக்கியமாக {', '.join(fields[:3])} சார்ந்த துறைகளுடன் தொடர்புடையது. "
            "நீங்கள் ஒரு சாதாரண மேலோட்டமான பணியில் நீடிக்க முடியாது; கணக்கு, தொழில்நுட்பம், நிர்வாகம் அல்லது நடைமுறை "
            "சிக்கல்களுக்குத் தீர்வு காணும் தனித்துவமான பொறுப்புகளில் இருக்கும்போதே உங்கள் தொழில் வளம் பிரகாசிக்கும்."
        )
        return career_en, career_ta, fields[:4]

    # ----------------------------------------------------------------------
    # Helper 2: Synthesize Sibling Order & Family Secret
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_birth_order(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
    ) -> Tuple[str, str]:
        mars_sign = planets_dict.get("Mars", {}).get("sign_index", 1)
        mars_house = ((mars_sign - ascendant_sign) % 12) + 1
        sun_sign = planets_dict.get("Sun", {}).get("sign_index", 1)
        jup_sign = planets_dict.get("Jupiter", {}).get("sign_index", 1)

        is_eldest_pattern = (mars_house in (1, 4, 7, 10)) or (mars_sign in (sun_sign, jup_sign))
        is_youngest_pattern = (mars_house in (3, 8, 12))

        if is_eldest_pattern:
            order_en = (
                "In your family, you hold the position of the eldest child—either you are literally the firstborn, "
                "or you shoulder the primary family burdens and decisions as if you were the eldest. "
                "Furthermore, Shastric indications show that either before your birth or shortly after, "
                "there was a lost pregnancy (miscarriage) or a difficult health struggle for a sibling."
            )
            order_ta = (
                "உங்கள் குடும்பத்தில் நீங்கள் மூத்த பிள்ளையாகப் பிறந்தவர்; அல்லது மூத்த பிள்ளைக்குரிய அனைத்து குடும்பப் "
                "பொறுப்புகளையும், முடிவுகளையும் சுமப்பவராக இருப்பீர்கள். மேலும் உங்கள் பிறப்பிற்கு முன்போ அல்லது பிறப்பிற்குப் "
                "பின்னரோ தாயாருக்கு ஒரு கருச்சிதைவு அல்லது ஒரு உடன்பிறப்புக்குக் கடுமையான கண்டம் ஏற்பட்டிருக்க வாய்ப்பு அதிகம்."
            )
        elif is_youngest_pattern:
            order_en = (
                "You are either the youngest sibling or occupied a protected, independent position in youth. "
                "However, there is an unspoken distance or lack of deep reliance with your siblings; "
                "whatever you have achieved in life, you had to fight for single-handedly without relying on them."
            )
            order_ta = (
                "குடும்பத்தில் நீங்கள் இளைய பிள்ளையாகவோ அல்லது தனித்து நின்றவராகவோ இருப்பீர்கள். உடன்பிறந்தவர்களுடன் ஒரு "
                "மறைமுக இடைவெளி உண்டு; அவர்கள் உங்களுக்குப் பெரிய அளவில் கை கொடுக்காமல், நீங்கள் ஒவ்வொரு வெற்றியையும் "
                "சுய உழைப்பால் மட்டுமே சாதிக்கும் நிலை உள்ளது."
            )
        else:
            order_en = (
                "You occupy a middle or distinct birth rank among siblings, often serving as the emotional bridge "
                "for the parents while absorbing hidden domestic anxieties."
            )
            order_ta = (
                "நீங்கள் உடன்பிறந்தவர்களிடையே ஒரு சமநிலையான பாலமாக செயல்பட்டு, பெற்றோரின் மனக்கவலைகளையும் "
                "குடும்பப் பொறுப்புகளையும் அமைதியாகப் பகிர்ந்து கொள்ளும் சுபாவம் கொண்டவர்."
            )
        return order_en, order_ta

    # ----------------------------------------------------------------------
    # Helper 3: Synthesize Gochara Sledgehammer (Saturn & Jupiter Transits)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_gochara_transits(
        cls,
        natal_moon_sign: int,
        transit_saturn_sign: int,
        transit_jupiter_sign: int,
    ) -> Tuple[str, str, str, str, str]:
        shani_offset = ((transit_saturn_sign - natal_moon_sign) % 12) + 1
        guru_offset = ((transit_jupiter_sign - natal_moon_sign) % 12) + 1

        if shani_offset == 12:
            phase = "Sade Sati - 1st Phase (விரய சனி / Rising)"
            s_en = "You are under the 1st phase of Sade Sati (Viraya Shani). Unplanned expenses are dissolving your liquid savings, sleep is disrupted, and long journeys cause fatigue. Avoid risky speculative trading."
            s_ta = "தற்போது உங்களுக்கு ஏழரை சனியின் முதல் பகுதியான 'விரய சனி' நிலவுகிறது. வரவுக்கு மீறிய திடீர் செலவுகள் சேமிப்பைக் கரைக்கின்றன; தூக்கமின்மையும், வீண் அலைச்சலும் சோர்வடையச் செய்கின்றன. ஊக வணிகத்தில் ஈடுபடாதீர்கள்."
        elif shani_offset == 1:
            phase = "Sade Sati - 2nd Phase (ஜென்ம சனி / Peak)"
            s_en = "You are actively enduring the 2nd phase of Sade Sati (Janma Shani). This is the supreme testing phase—heavy mental anxiety, physical lethargy, and a feeling that people you helped are now judging or misunderstanding you. Maintain absolute humility."
            s_ta = "தற்போது உங்களுக்கு ஏழரை சனியின் உச்சகட்டமான 'ஜென்ம சனி' நடக்கிறது. மன உளைச்சல், தூக்கமின்மை, உடல் சோர்வு மற்றும் நீங்கள் நல்லதே செய்தாலும் பிறர் தவறாகக் குற்றம் சாட்டும் சூழ்நிலை வாட்டுகிறது. நிதானமும் பொறுமையும் மட்டுமே உங்களைக் காக்கும்."
        elif shani_offset == 2:
            phase = "Sade Sati - 3rd Phase (பாத சனி / Setting)"
            s_en = "You are passing through the 3rd phase of Sade Sati (Paadha Shani). Financial cash flow is under pressure and your words or tone can easily trigger heated family arguments. Keep commercial dealings strictly documented."
            s_ta = "தற்போது உங்களுக்கு ஏழரை சனியின் நிறைவுப் பகுதியான 'பாத சனி' நடக்கிறது. பண வரவில் சுணக்கம், பேச்சினால் உறவினர்களிடம் பகை மற்றும் குடும்பத்தில் வாக்குவாதங்கள் ஏற்பட வாய்ப்புள்ளது. பேச்சில் மிகுந்த கவனம் தேவை."
        elif shani_offset == 8:
            phase = "Ashtama Shani (அஷ்டம சனி - 8th House Transit)"
            s_en = "You are enduring Ashtama Shani (transiting Saturn in your 8th house). This is the primary reason for sudden road-blocks, delayed payments, health vulnerabilities in legs/digestion, and fear of prestige loss. Do NOT stand surety/guarantee for anyone."
            s_ta = "தற்போது உங்களுக்குக் கடுமையான 'அஷ்டம சனி' (ராசிக்கு 8-ல் சனி) நடக்கிறது. திட்டமிட்ட காரியங்கள் கடைசி வினாடியில் முட்டுக்கட்டையாவது, பண விரயம், மூட்டு/செரிமானக் கோளாறு மற்றும் வீண் அவப்பெயர் அச்சம் நிலவுகிறது. எவருக்கும் கடனுக்கு ஜாமீன் கையெழுத்து போடாதீர்கள்."
        elif shani_offset in (4, 10):
            phase = f"Kantaka Shani (கண்டக சனி - {shani_offset}th House)"
            s_en = f"You are under Kantaka Shani (Saturn in your {shani_offset}th house). Friction with superiors, mother's health, or unexpected repairs to house/vehicle drain your peace of mind. Avoid walking away from your job abruptly."
            s_ta = f"தற்போது உங்கள் ராசிக்கு {shani_offset}-ல் 'கண்டக சனி' அமர்ந்துள்ளது. தொழில் ரீதியான அழுத்தம், மேலதிகாரிகளுடன் மனஸ்தாபம் அல்லது வீடு/வாகனப் பழுதுகளால் அலைச்சல் நிலவுகிறது. ஆத்திரத்தில் வேலையை விட வேண்டாம்."
        elif shani_offset in (3, 6, 11):
            phase = "Upachaya Shani (வெற்றி சனி - Favorable Transit)"
            s_en = f"Transit Saturn is in your {shani_offset}th Upachaya house. You possess the inner resilience to conquer competitors and gradually liquidate historical debts."
            s_ta = f"கோச்சார சனிபகவான் உங்கள் ராசிக்கு {shani_offset}-ஆம் இடத்தில் அமர்ந்து விசேஷ வலிமையை அளிக்கிறார். மறைமுக எதிர்ப்புகளை முறியடிக்கும் தைரியமும், பழைய கடன்களைப் படிப்படியாக அடைக்கும் வழிகளும் திறக்கும்."
        else:
            phase = "Neutral Shani Transit (நடுத்தர சனி)"
            s_en = "Saturn transit is neutral. Focus on continuous daily discipline and shun get-rich-quick schemes."
            s_ta = "சனிப் பெயர்ச்சி நடுத்தர பலனையே தருகிறது. குறுக்கு வழிகளை நாடாமல் சீரான உழைப்பை மேற்கொள்ளுங்கள்."

        # Guru Gochara
        if guru_offset in (2, 5, 7, 9, 11):
            j_en = f"Transit Jupiter is in your {guru_offset}th house, casting an auspicious protective aspect. Divine grace is quietly operating behind the scenes; unexpected help will rescue you from tight corners."
            j_ta = f"கோச்சார குருபகவான் உங்கள் ராசிக்கு {guru_offset}-ஆம் இடத்தில் அமர்ந்து சுப பார்வையைத் தருகிறார். தெய்வ அனுகூலம் உங்களுக்குப் பாதுகாப்பாக உள்ளது; இக்கட்டான நேரங்களில் எதிர்பாராத மனிதர்கள் மூலம் உதவி கிடைக்கும்."
        else:
            j_en = f"Transit Jupiter is in your {guru_offset}th house (hidden sthana). Do not depend on sheer luck; double-check all documents and avoid financial complacency."
            j_ta = f"கோச்சார குருபகவான் உங்கள் ராசிக்கு {guru_offset}-ஆம் இடத்தில் மறைந்துள்ளார். எனவே அதிர்ஷ்டத்தை நம்பி பெரிய முதலீடுகள் செய்வதைத் தவிர்த்து, எச்சரிக்கையுடன் செயல்பட வேண்டும்."

        return phase, s_en, s_ta, j_en, j_ta

    # ----------------------------------------------------------------------
    # Helper 4: Evaluate Dasa Chidra Alert (Dasa Sandhi)
    # ----------------------------------------------------------------------
    @classmethod
    def _evaluate_dasa_chidra(
        cls,
        dasa_tree: List[Any],
        arrival_date: date,
        current_md: str,
        current_md_ta: str,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        for node in dasa_tree:
            s_iso = getattr(node, "start_date_iso", None)
            e_iso = getattr(node, "end_date_iso", None)
            if not s_iso or not e_iso:
                continue
            s_d = date.fromisoformat(s_iso[:10])
            e_d = date.fromisoformat(e_iso[:10])

            if s_d <= arrival_date <= e_d:
                days_left = (e_d - arrival_date).days
                if 0 <= days_left <= 365:
                    end_str = e_d.isoformat()
                    w_en = (
                        f"CRITICAL DASA CHIDRA ALERT: You are in the final {days_left} days of your {current_md} Mahadasha (terminating on {end_str}). "
                        "Classical treatises strictly warn that in Dasa Sandhi, old karmic energy dissolves to prepare for the incoming Dasa. "
                        "All initiatives drag, and forced actions collapse. Maintain status-quo until the new Mahadasha dawns."
                    )
                    w_ta = (
                        f"முக்கிய தசா சந்தி எச்சரிக்கை: நீங்கள் தற்போது உங்கள் {current_md_ta} மகாதிசையின் இறுதி {days_left} நாட்களான 'தசா சந்தியில்' ({end_str} வரை) உள்ளீர்கள். "
                        "சாஸ்திர விதிகளின்படி தசா சந்தி காலத்தில் பழைய வினைகள் முழுமையாகக் கழிந்து புதிய திசைக்கு வழிவிடும். "
                        "இந்த காலத்தில் எதை அவசரப்பட்டுத் துவங்கினாலும் முட்டுக்கட்டையே மிஞ்சும். இந்த தேதி முடியும் வரை பெரிய முடிவுகளைத் தள்ளிப்போடவும்."
                    )
                    return True, w_en, w_ta, end_str
                break
        return False, None, None, None

    # ----------------------------------------------------------------------
    # Helper 5: Synthesize Medical & Organ Vulnerability
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_medical_vulnerability(
        cls,
        ascendant_sign: int,
        planets_dict: Dict[str, Dict[str, Any]],
    ) -> Tuple[str, str, List[str]]:
        sixth_sign = ((ascendant_sign + 5 - 1) % 12) + 1

        organs_map = {
            1: (["Head & Cranium", "Blood Pressure", "Acid Reflux / Bile"],
                "தலைப்பகுதி, இரத்த அழுத்தம் மற்றும் பித்த உஷ்ணம்",
                "Severe vulnerability to cranial migraines, eye heat, elevated blood pressure, and acidic gastric fire. Maintain hydration and avoid spicy heating foods."),
            2: (["Throat & Thyroid", "Vocal Cords", "Cervical Neck"],
                "தொண்டை, தைராய்டு சுரப்பி மற்றும் கழுத்து நரம்பு",
                "Tendency toward chronic throat irritation, tonsil/thyroid imbalances, and stiffness in the cervical neck vertebrae. Avoid refrigerated items."),
            3: (["Shoulders & Arms", "Bronchial Asthma", "Nervous Fatigue"],
                "தோள்பட்டை, மூச்சுக்குழாய் மற்றும் நரம்பு சோர்வு",
                "Susceptibility to bronchial allergies, dry coughs, shoulder blade tension, and nervous exhaustion from overthinking. Practice Pranayama daily."),
            4: (["Chest & Lungs", "Gastric Ulcers", "Fluid Retention"],
                "மார்பு சளி, இரைப்பை புண் மற்றும் நீர் வீக்கம்",
                "Vulnerability to chest congestion, excess phlegm, stomach lining irritation, and water retention. Guard digestive fire."),
            5: (["Spine & Back", "Heart Palpitations", "Eye Strain"],
                "முதுகெலும்பு, இதய படபடப்பு மற்றும் கண் எரிச்சல்",
                "Tendency toward spinal stiffness, mid-back pain, heart palpitations under stress, and eye burning. Practice Surya Namaskar."),
            6: (["Lower Intestines", "Digestive Colic / IBS", "Skin Dermatitis"],
                "குடல் கோளாறு, செரிமான அழற்சி மற்றும் தோல் ஒவ்வாமை",
                "Afflictions centered in the lower abdomen: irritable bowel, food sensitivities, skin allergies, and digestive sluggishness. Consume probiotics."),
            7: (["Kidneys & Filtration", "Lumbar Spine", "Urinary Tract"],
                "சிறுநீரகம், கீழ் இடுப்பு மற்றும் சிறுநீர்ப் பாதை",
                "Vulnerability to renal filtration sluggishness, urinary burning sensations, and lower lumbar disc pain. Drink ample copper-charged water."),
            8: (["Excretory / Piles", "Reproductive Organs", "Sudden Surgeries"],
                "மூல நோய் / ஆசனவாய், மர்ம உறுப்பு மற்றும் தையல் காயங்கள்",
                "Risk of hemorrhoids/piles, fistula, reproductive heat, and sudden sharp surgical interventions or cuts. Avoid excessive sedentary heat."),
            9: (["Hips & Arteries", "Sciatica Nerve", "Liver Lipid Balance"],
                "இடுப்பு மூட்டு, சயாடிகா நரம்பு மற்றும் கல்லீரல்",
                "Tendency toward sciatic nerve irritation, hip joint stiffness, and fatty liver / cholesterol buildup. Avoid excess oily carbohydrates."),
            10: (["Knee Cartilage", "Arthritis / Rheumatism", "Bone Stiffness"],
                 "முழங்கால் மூட்டு தேய்மானம், வாதம் மற்றும் எலும்பு வலி",
                 "High vulnerability to knee cartilage degeneration, joint stiffness, cracking bones, and dry rheumatic tendencies. Apply warm sesame oil to knees."),
            11: (["Calf Muscles & Shins", "Circulatory Varicose Veins", "Neurological Spasms"],
                 "கால் கெண்டைக்கால், இரத்த நாள வீக்கம் மற்றும் நரம்பு சுளுக்கு",
                 "Tendency toward painful calf muscle cramps, lower limb varicose veins, and restless leg spasms at night. Elevate legs before sleeping."),
            12: (["Lymphatics & Feet", "Ankle Swelling", "Immune Depletion"],
                 "நிணநீர் மண்டலம், பாத வலி மற்றும் தூக்கமின்மை",
                 "Vulnerability to lymphatic congestion, swollen feet/ankles, cold extremities, and restless insomnia. Practice foot massage with castor oil."),
        }

        organs_list, ta_organs, en_desc = organs_map.get(sixth_sign, organs_map[1])
        ta_desc = f"ரோக ஸ்தானமான 6-ஆம் பாவக ரீதியாக {ta_organs} சார்ந்த பகுதிகளில் உபாதைகள் ஏற்பட வாய்ப்புள்ளது. முறையான உணவுப் பழக்கமும், முன்னெச்சரிக்கையும் அவசியம்."

        return en_desc, ta_desc, organs_list

    # ----------------------------------------------------------------------
    # Helper 6: Synthesize Spouse & In-Laws Secrets (Option B)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_spouse_secrets(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
        gender: str,
    ) -> Tuple[str, str]:
        # 7th house and its Lord
        seventh_sign = ((ascendant_sign + 6 - 1) % 12) + 1
        seventh_lord = SIGN_LORDS.get(seventh_sign, "Venus")
        seventh_lord_sign = planets_dict.get(seventh_lord, {}).get("sign_index", seventh_sign)

        sp_karaka = "Venus" if gender == "male" else "Mars"
        sp_sign = planets_dict.get(sp_karaka, {}).get("sign_index", seventh_sign)

        # 1. Direction from 7th Lord and Karaka
        dir_map = {
            1: ("East", "கிழக்கு திசை"),
            2: ("South", "தெற்கு திசை"),
            3: ("West", "மேற்கு திசை"),
            4: ("North", "வடக்கு திசை"),
            5: ("East", "கிழக்கு திசை"),
            6: ("South", "தெற்கு திசை"),
            7: ("West", "மேற்கு திசை"),
            8: ("North", "வடக்கு திசை"),
            9: ("East", "கிழக்கு திசை"),
            10: ("South", "தெற்கு திசை"),
            11: ("West", "மேற்கு திசை"),
            12: ("North", "வடக்கு திசை"),
        }
        sp_dir_en, sp_dir_ta = dir_map.get(seventh_lord_sign, dir_map.get(sp_sign, ("East", "கிழக்கு திசை")))

        # 2. Distance: Chara/Water signs or Rahu = Distant; Sthira = Local; Dvisvabhava = Moderate
        rahu_sign = planets_dict.get("Rahu", {}).get("sign_index", 1)
        if (seventh_lord_sign in (1, 4, 7, 10, 12)) or (rahu_sign in (seventh_sign, seventh_lord_sign)):
            dist_en = "Your spouse was born at a noticeable distance—either across district borders, beyond a major water body/river, or from another town."
            dist_ta = "உங்கள் வாழ்க்கைத் துணை உங்கள் சொந்த ஊரிலிருந்து குறிப்பிட்ட தூரமான பகுதியிலிருந்தோ, நதி/கடல் தாண்டிய மாவட்டத்திலிருந்தோ அல்லது வேறு ஊர் பின்னணியிலிருந்தோ அமைந்தவர்."
        elif seventh_lord_sign in (2, 5, 8, 11):
            dist_en = "Your spouse originates within a familiar district radius, often linked to maternal/paternal ancestral connections or known family circles."
            dist_ta = "உங்கள் வாழ்க்கைத் துணை உள்ளூரிலோ அல்லது தாய்/தந்தை வழிப் பழக்கப்பட்ட உறவினர்/நண்பர்கள் வட்டத்திலோ அமைந்தவர்."
        else:  # Dual signs (3, 6, 9)
            dist_en = "Your spouse was born in an adjoining taluk or neighboring district within convenient travel distance."
            dist_ta = "உங்கள் வாழ்க்கைத் துணை பக்கத்து தாலுகா அல்லது அண்டை மாவட்ட எல்லைப் பகுதியிலிருந்து அமைந்தவர்."

        # 3. Dignified, universally resonant personality
        personality_en = "Spouse possesses sharp intellect, strong domestic administration, and an unyielding, principled will with deep self-respect."
        personality_ta = "வாழ்க்கைத் துணை சிறந்த குடும்ப நிர்வாகத் திறனும், எதற்கும் தலைவணங்காத தன்மானமும், குடும்பப் பொறுப்புகளை உறுதியுடன் சுமக்கும் குணமும் கொண்டவர்."

        # 4. In-Laws Dynamics
        third_sign = ((ascendant_sign + 2 - 1) % 12) + 1  # 9th from 7th (Father-in-law)
        sat_sign = planets_dict.get("Saturn", {}).get("sign_index", 10)
        mars_sign = planets_dict.get("Mars", {}).get("sign_index", 1)

        has_inlaw_friction = (sat_sign in (seventh_sign, third_sign)) or (mars_sign in (seventh_sign, third_sign)) or (rahu_sign in (seventh_sign, third_sign))

        if has_inlaw_friction:
            inlaw_en = "During marriage negotiations, there was notable friction, stubbornness, or prolonged dragging from the in-laws' side before final wedding knots were tied."
            inlaw_ta = "திருமணப் பேச்சுவார்த்தை துவங்கிய காலத்தில், மாமனார் அல்லது மாமியார் வழியில் சிறு பிடிவாதம், எதிர்பார்ப்புகள் அல்லது இழுபறி ஏற்பட்டுப் பின்னரே திருமணம் கைக்கூடியது."
        else:
            inlaw_en = "The in-laws' household carries respected social standing and traditional values, maintaining a dignified boundary in domestic matters."
            inlaw_ta = "மாமனார் வழி குடும்பம் நல்ல கௌரவமும் பாரம்பரிய மதிப்பும் கொண்டவர்கள்; மரியாதையான குடும்பப் பின்னணியைக் கொண்டவர்கள்."

        sp_desc_en = f"Spouse direction: {sp_dir_en}. {dist_en} Temperament: {personality_en} In-laws context: {inlaw_en}"
        sp_desc_ta = f"வாழ்க்கைத் துணை வந்த திசை: {sp_dir_ta}. {dist_ta} சுபாவம்: {personality_ta} மாமனார் வழி ரகசியம்: {inlaw_ta}"

        return sp_desc_en, sp_desc_ta

    # ----------------------------------------------------------------------
    # Helper 7: Synthesize Vehicle & Conveyance Marker (Option B)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_vehicle_marker(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
    ) -> Tuple[str, str]:
        fourth_sign = ((ascendant_sign + 3 - 1) % 12) + 1
        fourth_lord = SIGN_LORDS.get(fourth_sign, "Moon")
        fourth_lord_sign = planets_dict.get(fourth_lord, {}).get("sign_index", fourth_sign)
        ven_sign = planets_dict.get("Venus", {}).get("sign_index", 2)
        sat_sign = planets_dict.get("Saturn", {}).get("sign_index", 10)
        mars_sign = planets_dict.get("Mars", {}).get("sign_index", 1)
        rahu_sign = planets_dict.get("Rahu", {}).get("sign_index", 1)

        # 1. 4th House Occupants (Direct Physical Conveyance Karakas)
        occupants_4th = [p for p in ["Saturn", "Mars", "Venus", "Moon", "Mercury", "Sun", "Jupiter", "Rahu", "Ketu"] if planets_dict.get(p, {}).get("sign_index") == fourth_sign]

        if "Saturn" in occupants_4th:
            color_en = "Royal Blue, Midnight Navy Blue, or Metallic Steel Grey"
            color_ta = "ராயல் ப்ளூ, அடர் நீலம், கருநீலம் அல்லது ஸ்டீல் கிரே"
        elif "Mars" in occupants_4th:
            color_en = "Deep Crimson Maroon, Bold Red, or Flame Metallic"
            color_ta = "அடர் மெரூன், சிவப்பு அல்லது சுடர் வண்ணம்"
        elif "Venus" in occupants_4th:
            color_en = "Diamond White, Pearl Silver, or Lustrous Cream"
            color_ta = "பளபளப்பான வெள்ளை, சில்வர் அல்லது முத்து நிறம்"
        elif "Moon" in occupants_4th:
            color_en = "Pure Pearl White, Classic Silver, or Sea-Mist Cream"
            color_ta = "தூய வெள்ளை, கிளாசிக் சில்வர் அல்லது முத்து நிறம்"
        elif "Sun" in occupants_4th:
            color_en = "Rich Maroon, Metallic Copper, or Warm Golden Metallic"
            color_ta = "அடர் மெரூன், காப்பர் அல்லது அரச கோல்டன் மெட்டாலிக்"
        elif "Mercury" in occupants_4th:
            color_en = "Metallic Titanium Grey, Silver, or Dual-Tone"
            color_ta = "டைட்டானியம் சாம்பல், சில்வர் அல்லது டூயல்-டோன் (இரட்டை வண்ணம்)"
        elif "Jupiter" in occupants_4th:
            color_en = "Golden Champagne, Royal Pearl, or Sandalwood Beige"
            color_ta = "கோல்டன் மெட்டாலிக், சந்தன கிரீம் அல்லது ராயல் வெள்ளை"
        elif "Rahu" in occupants_4th:
            color_en = "Phantom Matte Black, Shadow Charcoal, or Dark Dual-Tone"
            color_ta = "மேட் பிளாக் (Matte Black), சாம்பல் அல்லது நிழல் வண்ணம்"
        elif "Ketu" in occupants_4th:
            color_en = "Off-White, Minimalist Cement Grey, or Earthy Tone"
            color_ta = "ஆஃப்-ஒயிட் (Off-White), சாம்பல் அல்லது சிமெண்ட் கிரே"
        else:
            # Check Saturn or Mars aspect on 4th house
            sat_aspect_4th = ((fourth_sign - sat_sign) % 12) in (2, 6, 9)  # 3rd, 7th, 10th aspect
            mars_aspect_4th = ((fourth_sign - mars_sign) % 12) in (3, 6, 7)  # 4th, 7th, 8th aspect

            if sat_aspect_4th:
                color_en = "Royal Blue, Midnight Navy Blue, or Steel Grey"
                color_ta = "ராயல் ப்ளூ, அடர் நீலம் அல்லது ஸ்டீல் கிரே"
            elif mars_aspect_4th:
                color_en = "Deep Crimson Maroon, Bold Red, or Metallic Flame"
                color_ta = "அடர் மெரூன், சிவப்பு அல்லது மெட்டாலிக்"
            else:
                # Sign-based palette from 4th Lord or Venus
                color_map = {
                    1: ("Deep Maroon, Bold Red, or Metallic Charcoal Grey", "அடர் மெரூன், சிவப்பு அல்லது சாம்பல் நிறம்"),
                    2: ("Pearl White, Lustrous Silver, or Ivory Cream", "முத்து வெள்ளை, சில்வர் அல்லது பளபளப்பான வெளிர் நிறம்"),
                    3: ("Metallic Silver-Grey, Platinum, or Dual-Tone Dark", "சில்வர் கிரே, பிளாட்டினம் அல்லது இரட்டை வண்ணக் கலவை"),
                    4: ("Pure Pearl White, Classic Silver, or Sea-Mist Ivory", "தூய வெள்ளை, கிளாசிக் சில்வர் அல்லது முத்து நிறம்"),
                    5: ("Rich Maroon, Copper Red, or Bold Metallic Grey", "அடர் மெரூன், காப்பர் அல்லது மெட்டாலிக் சாம்பல்"),
                    6: ("Metallic Titanium Grey, Silver, or Dual-Tone", "டைட்டானியம் சாம்பல், சில்வர் அல்லது டூயல்-டோன்"),
                    7: ("Diamond White, Sleek Silver, or Elegant Pearl", "பளபளப்பான வெள்ளை, சில்வர் அல்லது முத்து நிறம்"),
                    8: ("Deep Wine Red, Midnight Black, or Dark Maroon", "அடர் ஒயின் ரெட், கருப்பு அல்லது மெரூன் நிறம்"),
                    9: ("Pearl White, Champagne Silver, or Metallic Royal Blue", "முத்து வெள்ளை, ஷாம்பெயின் சில்வர் அல்லது ராயல் நீலம்"),
                    10: ("Midnight Navy Blue, Charcoal Grey, or Classic Black", "அடர் கருநீலம், சாம்பல் அல்லது கிளாசிக் கருப்பு"),
                    11: ("Steel Grey, Royal Navy Blue, or Matte Black", "ஸ்டீல் கிரே, அடர் நீலம் அல்லது மேட் பிளாக்"),
                    12: ("Pearl White, Glaze Silver, or Light Metallic Grey", "முத்து வெள்ளை, சில்வர் அல்லது வெளிர் சாம்பல் நிறம்"),
                }
                color_en, color_ta = color_map.get(fourth_lord_sign, color_map.get(ven_sign, ("Pearl White, Silver, or Metallic Grey", "வெள்ளை, சில்வர் அல்லது சாம்பல்")))

        # 2. Vehicle Pristine Condition vs Scratches Evaluation
        own_signs_map = {
            "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
            "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11],
        }
        exalted_signs_map = {
            "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
            "Jupiter": 4, "Venus": 12, "Saturn": 7,
        }

        fl_is_own = fourth_lord_sign in own_signs_map.get(fourth_lord, [])
        fl_is_exalted = fourth_lord_sign == exalted_signs_map.get(fourth_lord)
        ven_is_own = ven_sign in [2, 7]
        ven_is_exalted = ven_sign == 12
        fl_house = ((fourth_lord_sign - ascendant_sign) % 12) + 1
        fl_dusthana = fl_house in (6, 8, 12)
        has_direct_malefic_4th = (mars_sign == fourth_sign) or (rahu_sign == fourth_sign)

        is_scratchless = (fl_is_own or fl_is_exalted or ven_is_own or ven_is_exalted) and not (has_direct_malefic_4th or fl_dusthana)

        if is_scratchless:
            blemish_en = (
                "The vehicle is maintained pristine, clean, and without noticeable scratches; you guard it with keen pride "
                "against even small grazes, keeping it spotless and attending to regular maintenance with care."
            )
            blemish_ta = (
                "வாகனம் எந்தவொரு பெரிய கீறலும் இன்றி மிக நேர்த்தியாகவும் சுத்தமாகவும் பராமரிக்கப்படுகிறது; வண்டியில் ஒரு சிறு கீறல் அல்லது "
                "தூசு கூட விழாமல் கண்ணும் கருத்துமாகப் பாதுகாக்கும் சுபாவம், மற்றும் முறையான ஆயில் பராமரிப்பில் தனி அக்கறை உண்டு."
            )
        else:
            blemish_en = (
                "Your vehicle carries a minor scratch or brush mark on the front/side bumper, mirror edge, or exhaust guard from tight traffic navigation, "
                "along with periodic tire puncture or battery/servicing maintenance."
            )
            blemish_ta = (
                "உங்கள் வாகனத்தில் முன்/பக்கவாட்டு பம்பர், மிரர் அல்லது விளிம்பில் டிராஃபிக்கில் உரசிய சிறு கீறல் அல்லது தட்டுப்பாடு அடையாளம் உண்டு; "
                "மேலும் டயர் பஞ்சர் அல்லது பேட்டரி/ஆயில் சர்வீஸ் தாமதத்தால் ஏற்படும் சிறு தொந்தரவு ஏற்படுவது இயல்பு."
            )

        v_en = f"You are naturally drawn to or operate vehicles in {color_en} (commuter two-wheeler or family car). Conveyance signature: {blemish_en}"
        v_ta = f"நீங்கள் இயற்கையாக விரும்பும் அல்லது இயக்கும் வாகன நிறம்: {color_ta} (இருசக்கர வாகனம் அல்லது பயன்பாட்டு கார்). வாகன நேரடி அடையாளம்: {blemish_ta}"

        return v_en, v_ta

    # ----------------------------------------------------------------------
    # Helper 8: Synthesize Ancestral Property & Paternal Land Rift (Option B)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_ancestral_land_rift(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
    ) -> Tuple[str, str]:
        ninth_sign = ((ascendant_sign + 8 - 1) % 12) + 1
        sun_sign = planets_dict.get("Sun", {}).get("sign_index", 1)
        sat_sign = planets_dict.get("Saturn", {}).get("sign_index", 10)
        mars_sign = planets_dict.get("Mars", {}).get("sign_index", 1)
        rahu_sign = planets_dict.get("Rahu", {}).get("sign_index", 1)
        ketu_sign = planets_dict.get("Ketu", {}).get("sign_index", 7)

        # Affliction on 9th house or Sun
        is_rift = (
            (sat_sign in (ninth_sign, sun_sign))
            or (rahu_sign in (ninth_sign, sun_sign))
            or (ketu_sign in (ninth_sign, sun_sign))
        )

        if is_rift:
            rift_en = (
                "In your paternal ancestral lineage (father's or grandfather's generation), there was an ancestral house, "
                "garden plot, or fertile land with a well that became entangled in a painful partition dispute or boundary/pathway friction with paternal relatives (pangalis), "
                "or was liquidated under distress/undervalued with lingering regret among elders."
            )
            rift_ta = (
                "உங்கள் தந்தை அல்லது பாட்டனார் காலத்தில், கிணறு, தோட்டம் அல்லது பூர்வீக நிலம்/வீடு விவகாரத்தில் பங்காளிகளுடன் "
                "(சித்தப்பா/பெரியப்பா வழி) பாகப்பிரிவினை சர்ச்சை, எல்லை வரப்பு/பாதை இழுபறி, அல்லது குடும்ப நெருக்கடியில் சொத்தை குறைந்த விலைக்கு விற்றுவிட்டுப் பின் "
                "ஏங்கிய ஒரு கசப்பான வரலாறு உண்டு."
            )
        else:
            rift_en = (
                "Your paternal lineage held proud, respectable community standing and landed property in their native soil, "
                "though ancestral temple worship (Kuladeivam) or a family promise remains an unresolved duty."
            )
            rift_ta = (
                "தந்தை வழி முன்னோர்கள் ஊர் மதிப்பும் நிலபுலன்களும் கொண்டவர்கள்; தலைமுறை மாற்றங்களில் பாகப்பிரிவினை மூலம் "
                "சொத்துக்கள் பிரிக்கப்பட்டிருந்தாலும், பூர்வீகக் குலதெய்வ வழிபாடு அல்லது முன்னோர் வாக்குறுதி சார்ந்த ஒரு கடமை இன்னும் நிலுவையில் உள்ளது."
            )

        return rift_en, rift_ta

    # ----------------------------------------------------------------------
    # Helper 9: Synthesize Childhood Balarishta Escape (Option B)
    # ----------------------------------------------------------------------
    @classmethod
    def _synthesize_childhood_balarishta(
        cls,
        planets_dict: Dict[str, Dict[str, Any]],
        ascendant_sign: int,
    ) -> Tuple[str, str]:
        ketu_sign = planets_dict.get("Ketu", {}).get("sign_index", 7)
        jup_sign = planets_dict.get("Jupiter", {}).get("sign_index", 9)
        diff = ((ketu_sign - jup_sign) % 12) + 1

        danger_ages_map = {
            1: [1, 3], 2: [2, 4], 3: [3, 5], 4: [4, 6],
            5: [5, 7], 6: [6, 8], 7: [7, 9], 8: [8, 10],
            9: [2, 5], 10: [3, 6], 11: [4, 7], 12: [1, 4],
        }
        ages = danger_ages_map.get(diff, [3, 6])
        min_age, max_age = ages[0], ages[-1]

        b_en = (
            f"Around ages {min_age} to {max_age}: You miraculously survived a critical childhood danger (Balarishta)—"
            "an intense high fever with convulsions, a severe fall resulting in a head or body injury, a frightening encounter with water/fire, "
            "or an acute respiratory crisis where your parents panicked for your life."
        )
        b_ta = (
            f"சிறுவயதில் சுமார் {min_age} முதல் {max_age} வயதுக்குள்: நீங்கள் ஒரு கடுமையான பாலாரிஷ்ட கண்டத்தைத் தாண்டி வந்துள்ளீர்கள். "
            "தீவிர காய்ச்சல்/இசிவு, கீழே விழுந்து தலையில் பலத்த அடி, அல்லது நீர்/நெருப்பு/மூச்சுத்திணறல் கண்டத்திலிருந்து பெற்றோர் பதறித் துடித்து "
            "உங்களைக் காப்பாற்றிய ஒரு மறக்க முடியாத சம்பவம் உண்டு."
        )

        return b_en, b_ta



