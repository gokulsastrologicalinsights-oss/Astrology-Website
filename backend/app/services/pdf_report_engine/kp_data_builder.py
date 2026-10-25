"""Data aggregator for KP (Krishnamurti Paddhati) PDF reports.

Consolidates all calculations for both Natal KP Charts and Horary Prashna (1-249):
1. Placidus unequal house cusps and 249/2193 subdivisions.
2. 9 Grahas sidereal longitudes, star lords, sub lords, sub-sub lords.
3. 12 Cuspal Sub-Lords (CSL) and bhava promise arbiter.
4. 4-Tier ABCD House Significators (Bhaav Nirdeshan).
5. Planet-wise significator strength hierarchies.
6. Ruling Planets (RP) of the moment.
7. 5-level Vimshottari Dasa hierarchy and birth balance.
8. Core life event promise matrix (Marriage, Career, Wealth, Property, Health, etc.).
9. Panchang and astronomical calibration metadata.
"""

from __future__ import annotations
import logging
import uuid
from dataclasses import dataclass, field
from datetime import date, time, datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.schemas.common import BirthInput
from app.schemas.kp import (
    KpRequest,
    KpResponse,
    HoraryKpRequest,
    HoraryKpResponse,
    PlanetaryKpPosition,
    KpCuspDetail,
    PlanetSignificator,
    HouseSignificatorEntry,
    RulingPlanetsDetail,
    KpDasaBalance,
)
from app.services.kp_service import calculate_kp_chart, calculate_horary_chart
from app.services.kp_event_engine.event_rules import EVENT_REGISTRY

logger = logging.getLogger("gai.pdf.kp_builder")


@dataclass
class KpReportData:
    """Consolidated data model holding all calculated values for the 6-page KP report."""

    # Metadata & Native / Querent Info
    chart_type: str  # "natal" or "horary"
    title: str
    native_name: str
    gender: str
    birth_date: str
    birth_time: str
    location_name: str
    latitude: float
    longitude: float
    timezone_str: str
    ayanamsa_name: str
    ayanamsa_deg: float
    house_system_name: str
    report_id: str
    generated_at: str
    language: str = "en"
    is_verified: bool = True

    # Horary Specific
    horary_number: Optional[int] = None
    question_text: Optional[str] = None
    horary_division: Optional[Dict[str, Any]] = None
    ascendant_degree: Optional[float] = None

    # KP Core Calculation Data
    planetary_positions: List[Dict[str, Any]] = field(default_factory=list)
    cuspal_analysis: List[Dict[str, Any]] = field(default_factory=list)
    significators: List[Dict[str, Any]] = field(default_factory=list)
    house_significators: List[Dict[str, Any]] = field(default_factory=list)
    ruling_planets: Optional[Dict[str, Any]] = None
    dasa_hierarchy: Optional[Dict[str, Any]] = None

    # Panchang & Astronomical Details
    panchang: Optional[Dict[str, Any]] = None
    julian_day_ut1: float = 0.0
    true_obliquity: float = 23.44
    sidereal_time: str = ""

    # KP Event Predictions / Evaluation Matrix
    event_evaluations: List[Dict[str, Any]] = field(default_factory=list)


KEY_LIFE_EVENTS = [
    {
        "name_en": "Marriage & Matrimony",
        "name_ta": "திருமணம் மற்றும் தாம்பத்தியம்",
        "primary_cusp": 7,
        "supporting": [2, 7, 11],
        "denying": [1, 6, 10],
        "category": "Relationship",
        "desc_en": "Matrimonial union, spouse longevity, harmony.",
        "desc_ta": "திருமண வாழ்க்கை, வாழ்க்கைத் துணை, ஒற்றுமை.",
    },
    {
        "name_en": "Career & Employment",
        "name_ta": "தொழில் மற்றும் உத்தியோகம்",
        "primary_cusp": 10,
        "supporting": [2, 6, 10, 11],
        "denying": [5, 8, 12],
        "category": "Career",
        "desc_en": "Job opportunities, promotion, public standing.",
        "desc_ta": "வேலை வாய்ப்பு, பதவி உயர்வு, சமுதாய அந்தஸ்து.",
    },
    {
        "name_en": "Financial Prosperity & Wealth",
        "name_ta": "பொருளாதார வளர்ச்சி & தன சேர்க்கை",
        "primary_cusp": 2,
        "supporting": [2, 6, 11],
        "denying": [8, 12],
        "category": "Wealth",
        "desc_en": "Liquid cash, family wealth, jewelry, banking.",
        "desc_ta": "தன வரவு, சேமிப்பு, குடும்ப வளம், நிதி லாபம்.",
    },
    {
        "name_en": "Property & Vehicles",
        "name_ta": "சொத்து & வாகன யோகம்",
        "primary_cusp": 4,
        "supporting": [4, 11, 12],
        "denying": [3, 8],
        "category": "Assets",
        "desc_en": "Real estate, house construction, automobiles.",
        "desc_ta": "நிலம், வீடு கட்டுதல், வாகனம் வாங்கும் யோகம்.",
    },
    {
        "name_en": "Progeny & Child Birth",
        "name_ta": "புத்திர பாக்கியம் & குழந்தைகள்",
        "primary_cusp": 5,
        "supporting": [2, 5, 11],
        "denying": [1, 4, 8, 12],
        "category": "Family",
        "desc_en": "Conception, safe delivery, children's welfare.",
        "desc_ta": "சந்ததி பெருக்கம், சுகப்பிரசவம், பிள்ளைகள் நலம்.",
    },
    {
        "name_en": "Higher Education & Knowledge",
        "name_ta": "உயர் கல்வி & ஞானம்",
        "primary_cusp": 9,
        "supporting": [4, 9, 11],
        "denying": [3, 8],
        "category": "Education",
        "desc_en": "Collegiate degrees, competitive exams, research.",
        "desc_ta": "கல்லூரி படிப்பு, போட்டித் தேர்வுகள், ஆராய்ச்சி.",
    },
    {
        "name_en": "Health & Longevity",
        "name_ta": "உடல் நலம் & ஆயுள் பலம்",
        "primary_cusp": 1,
        "supporting": [1, 5, 11],
        "denying": [6, 8, 12],
        "category": "Health",
        "desc_en": "Physical vitality, recuperation, long life.",
        "desc_ta": "உடல் ஆரோக்கியம், நோய் நிவாரணம், தீர்க்காயுள்.",
    },
    {
        "name_en": "Foreign Travel & Relocation",
        "name_ta": "வெளிநாட்டுப் பயணம் & குடியேற்றம்",
        "primary_cusp": 12,
        "supporting": [3, 9, 12],
        "denying": [4, 8],
        "category": "Travel",
        "desc_en": "Overseas journeys, visa clearance, settling abroad.",
        "desc_ta": "கடல் கடந்த பயணம், விசா அனுகூலம், வெளிநாட்டு வாழ்க்கை.",
    },
]


def _evaluate_kp_event_matrix(
    cuspal_analysis: List[Dict[str, Any]],
    significators: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Evaluate core KP life events through Cuspal Sub-Lord (CSL) significations."""
    csl_by_house: Dict[int, str] = {}
    for c in cuspal_analysis:
        h = c.get("house")
        sub = c.get("sub_lord")
        if h and sub:
            csl_by_house[h] = sub

    sig_by_planet: Dict[str, List[int]] = {}
    for s in significators:
        p = s.get("planet")
        houses = s.get("signified_houses", [])
        if p:
            sig_by_planet[p] = houses

    results: List[Dict[str, Any]] = []
    for ev in KEY_LIFE_EVENTS:
        p_cusp = ev["primary_cusp"]
        csl = csl_by_house.get(p_cusp, "")
        signified = set(sig_by_planet.get(csl, []))

        supp = set(ev["supporting"])
        deny = set(ev["denying"])

        has_supp = signified & supp
        has_deny = signified & deny

        if has_supp and not has_deny:
            promise = "Positive"
            status_ta = "மிகவும் சாதகமானது"
            color = "#15803D"
        elif has_supp and len(has_supp) >= len(has_deny):
            promise = "Favorable"
            status_ta = "சாதகமானது"
            color = "#15803D"
        elif has_deny and not has_supp:
            promise = "Challenging"
            status_ta = "தடைகள் / கவனம் தேவை"
            color = "#991B1B"
        elif len(has_deny) > len(has_supp):
            promise = "Delayed"
            status_ta = "தாமதம் ஏற்படலாம்"
            color = "#B45309"
        else:
            promise = "Mixed"
            status_ta = "மிதமான பலன்"
            color = "#475569"

        results.append({
            "name_en": ev["name_en"],
            "name_ta": ev["name_ta"],
            "primary_cusp": p_cusp,
            "csl": csl,
            "signified_houses": sorted(list(signified)),
            "supporting_houses": ev["supporting"],
            "denying_houses": ev["denying"],
            "promise": promise,
            "status_ta": status_ta,
            "color": color,
            "desc_en": ev["desc_en"],
            "desc_ta": ev["desc_ta"],
        })

    return results


def _compute_panchang_dict(b_date: date, b_time: time, tz_str: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Compute 5 limbs of Panchang using full horoscope ephemeris."""
    try:
        from app.services.ephemeris import calculate_full_horoscope
        horo = calculate_full_horoscope(
            birth_date=b_date,
            birth_time=b_time,
            timezone_str=tz_str,
            latitude=lat,
            longitude=lon,
            include_panchang=True,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            include_varga=False,
            include_doshas=False,
        )
        if horo and horo.panchang:
            p = horo.panchang
            return {
                "tithi_paksha": p.tithi.paksha if hasattr(p.tithi, "paksha") else "",
                "tithi_name": p.tithi.name if hasattr(p.tithi, "name") else str(p.tithi),
                "vara": p.vara,
                "nakshatra": p.nakshatra,
                "yoga": p.yoga.name if hasattr(p.yoga, "name") else str(p.yoga),
                "karana": p.karana,
            }
    except Exception as exc:
        logger.warning("Could not calculate birth Panchang for KP report: %s", exc)
    return None


def build_kp_report_data(
    birth_input: Optional[BirthInput] = None,
    horary_input: Optional[HoraryKpRequest] = None,
    saved_chart_dict: Optional[Dict[str, Any]] = None,
    native_name: Optional[str] = "Native",
    gender: Optional[str] = "male",
    language: str = "en",
    ayanamsa_id: int = 1,
    house_system_id: int = 2,
    report_id: Optional[str] = None,
    is_verified: bool = True,
) -> KpReportData:
    """Build a comprehensive KpReportData object from birth inputs, horary inputs, or saved chart dict."""
    if report_id is None:
        report_id = f"KP-{uuid.uuid4().hex[:8].upper()}"

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Case 1: Saved KP Chart Dictionary
    if saved_chart_dict:
        chart_type = saved_chart_dict.get("chart_type", "natal")
        title = saved_chart_dict.get("title", "KP Chart")
        loc_name = saved_chart_dict.get("location_name", "Unknown Location")
        lat = float(saved_chart_dict.get("latitude", 13.0827))
        lon = float(saved_chart_dict.get("longitude", 80.2707))
        tz_str = saved_chart_dict.get("timezone", "Asia/Kolkata")
        b_date_str = str(saved_chart_dict.get("birth_date") or saved_chart_dict.get("question_date") or "1990-01-01")
        b_time_str = str(saved_chart_dict.get("birth_time") or saved_chart_dict.get("question_time") or "12:00:00")
        horary_num = saved_chart_dict.get("horary_number")
        q_text = saved_chart_dict.get("question_text")

        calc_res = saved_chart_dict.get("calculation_result", {})
        meta = calc_res.get("metadata", {})
        ayanamsa_name = meta.get("ayanamsa_name", "KP Krishnamurti VP291")
        ayanamsa_deg = float(meta.get("ayanamsa_deg", 24.1234))
        house_system_name = meta.get("house_system_name", "Placidus")
        jd = float(meta.get("julian_day_ut1", 2450000.0))

        planets = calc_res.get("planetary_positions", [])
        cusps = calc_res.get("cuspal_analysis", [])
        sigs = calc_res.get("significators", [])
        house_sigs = calc_res.get("house_significators", [])
        ruling = calc_res.get("ruling_planets", {})
        dasa = calc_res.get("dasa_hierarchy", {})
        horary_div = calc_res.get("horary_division")
        asc_deg = calc_res.get("ascendant_degree")

        # Parse birth date and time for panchang
        try:
            p_date = date.fromisoformat(b_date_str)
            p_time_parts = [int(float(x)) for x in b_time_str.split(":")[:3]]
            p_time = time(*p_time_parts)
            panchang = _compute_panchang_dict(p_date, p_time, tz_str, lat, lon)
        except Exception:
            panchang = None

        events = _evaluate_kp_event_matrix(cusps, sigs)

        return KpReportData(
            chart_type=chart_type,
            title=title,
            native_name=saved_chart_dict.get("customer_full_name") or native_name or "Querent",
            gender=gender or "male",
            birth_date=b_date_str,
            birth_time=b_time_str,
            location_name=loc_name,
            latitude=lat,
            longitude=lon,
            timezone_str=tz_str,
            ayanamsa_name=ayanamsa_name,
            ayanamsa_deg=ayanamsa_deg,
            house_system_name=house_system_name,
            report_id=report_id,
            generated_at=now_utc,
            language=language,
            is_verified=is_verified,
            horary_number=horary_num,
            question_text=q_text,
            horary_division=horary_div,
            ascendant_degree=asc_deg,
            planetary_positions=planets,
            cuspal_analysis=cusps,
            significators=sigs,
            house_significators=house_sigs,
            ruling_planets=ruling,
            dasa_hierarchy=dasa,
            panchang=panchang,
            julian_day_ut1=jd,
            event_evaluations=events,
        )

    # Case 2: Ad-hoc Horary Query (1-249)
    elif horary_input:
        chart_type = "horary"
        calc_response: HoraryKpResponse = calculate_horary_chart(horary_input)

        b_date_str = str(horary_input.question_date)
        b_time_str = str(horary_input.question_time)
        loc_name = horary_input.location_name or "Consultation Location"
        panchang = _compute_panchang_dict(
            horary_input.question_date,
            horary_input.question_time,
            horary_input.timezone,
            horary_input.latitude,
            horary_input.longitude,
        )

        planets_dict = [p.model_dump() for p in calc_response.planetary_positions]
        cusps_dict = [c.model_dump() for c in calc_response.cuspal_analysis]
        sigs_dict = [s.model_dump() for s in calc_response.significators]
        house_sigs_dict = [hs.model_dump() for hs in calc_response.house_significators]
        ruling_dict = calc_response.ruling_planets.model_dump() if calc_response.ruling_planets else None
        dasa_dict = calc_response.dasa_hierarchy.model_dump() if calc_response.dasa_hierarchy else None
        horary_div_dict = calc_response.horary_division.model_dump() if calc_response.horary_division else None

        events = _evaluate_kp_event_matrix(cusps_dict, sigs_dict)

        title = f"KP Horary Prashna #{horary_input.horary_number}"
        if horary_input.question_text:
            title += f": {horary_input.question_text[:35]}"

        return KpReportData(
            chart_type="horary",
            title=title,
            native_name=native_name or "Querent",
            gender=gender or "male",
            birth_date=b_date_str,
            birth_time=b_time_str,
            location_name=loc_name,
            latitude=horary_input.latitude,
            longitude=horary_input.longitude,
            timezone_str=horary_input.timezone,
            ayanamsa_name=calc_response.metadata.ayanamsa_name,
            ayanamsa_deg=calc_response.metadata.ayanamsa_deg,
            house_system_name=calc_response.metadata.house_system_name,
            report_id=report_id,
            generated_at=now_utc,
            language=language,
            is_verified=True,
            horary_number=horary_input.horary_number,
            question_text=horary_input.question_text,
            horary_division=horary_div_dict,
            ascendant_degree=calc_response.ascendant_degree,
            planetary_positions=planets_dict,
            cuspal_analysis=cusps_dict,
            significators=sigs_dict,
            house_significators=house_sigs_dict,
            ruling_planets=ruling_dict,
            dasa_hierarchy=dasa_dict,
            panchang=panchang,
            julian_day_ut1=calc_response.metadata.julian_day_ut1,
            event_evaluations=events,
        )

    # Case 3: Ad-hoc Natal KP Chart
    elif birth_input:
        chart_type = "natal"
        kp_req = KpRequest(
            birth_date=birth_input.birth_date,
            birth_time=birth_input.birth_time,
            timezone=birth_input.timezone,
            latitude=birth_input.latitude,
            longitude=birth_input.longitude,
            ayanamsa=ayanamsa_id,
            house_system=house_system_id,
        )
        calc_response: KpResponse = calculate_kp_chart(kp_req, ayanamsa_id=ayanamsa_id, house_system_id=house_system_id)

        b_date_str = str(birth_input.birth_date)
        b_time_str = str(birth_input.birth_time)
        loc_name = getattr(birth_input, "location_name", None) or "Birth Location"

        panchang = _compute_panchang_dict(
            birth_input.birth_date,
            birth_input.birth_time,
            birth_input.timezone,
            birth_input.latitude,
            birth_input.longitude,
        )

        planets_dict = [p.model_dump() for p in calc_response.planetary_positions]
        cusps_dict = [c.model_dump() for c in calc_response.cuspal_analysis]
        sigs_dict = [s.model_dump() for s in calc_response.significators]
        house_sigs_dict = [hs.model_dump() for hs in (calc_response.house_significators or [])]
        ruling_dict = calc_response.ruling_planets.model_dump() if calc_response.ruling_planets else None
        dasa_dict = calc_response.dasa_hierarchy.model_dump() if calc_response.dasa_hierarchy else None

        # Ascendant degree is cusp 1 degree
        asc_deg = None
        for c in calc_response.cuspal_analysis:
            if c.house == 1:
                asc_deg = c.cusp_degree
                break

        events = _evaluate_kp_event_matrix(cusps_dict, sigs_dict)

        return KpReportData(
            chart_type="natal",
            title=f"Natal KP Chart — {native_name}",
            native_name=native_name or "Native",
            gender=gender or "male",
            birth_date=b_date_str,
            birth_time=b_time_str,
            location_name=loc_name,
            latitude=birth_input.latitude,
            longitude=birth_input.longitude,
            timezone_str=birth_input.timezone,
            ayanamsa_name=calc_response.metadata.ayanamsa_name,
            ayanamsa_deg=calc_response.metadata.ayanamsa_deg,
            house_system_name=calc_response.metadata.house_system_name,
            report_id=report_id,
            generated_at=now_utc,
            language=language,
            is_verified=is_verified,
            ascendant_degree=asc_deg,
            planetary_positions=planets_dict,
            cuspal_analysis=cusps_dict,
            significators=sigs_dict,
            house_significators=house_sigs_dict,
            ruling_planets=ruling_dict,
            dasa_hierarchy=dasa_dict,
            panchang=panchang,
            julian_day_ut1=calc_response.metadata.julian_day_ut1,
            event_evaluations=events,
        )

    else:
        raise ValueError("Must provide either birth_input, horary_input, or saved_chart_dict.")
