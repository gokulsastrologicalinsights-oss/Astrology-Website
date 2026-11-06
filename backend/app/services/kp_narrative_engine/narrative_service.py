"""Orchestrator Service for Automated KP Predictive Narrative Engine.

Coordinates birth calculation, natal promise evaluation, running dasha analysis,
upcoming milestone window scanning, and tailored remedial recommendations.
"""

from datetime import date, datetime, time as dt_time, timedelta
from typing import Any, Dict, Optional, Tuple
import uuid
from zoneinfo import ZoneInfo

from app.schemas.common import BirthInput
from app.schemas.kp_narrative import (
    KpNarrativeRequest,
    KpNarrativeResponse,
    PersonDetails,
)
from app.services.kp_service import calculate_kp_chart
from app.services.timezone_utils import resolve_birth_datetime
from app.services.kp_engine.vedic import sign_name
from .constants import (
    PLANET_NAMES_TA,
    SIGN_NAMES_TA,
    NAKSHATRA_NAMES_TA,
)
from .natal_evaluator import evaluate_natal_event_promise
from .dasha_evaluator import evaluate_running_dasha_impact
from .milestones_scanner import scan_upcoming_milestone_windows
from .remedies_evaluator import evaluate_tailored_remedies


def _calculate_age_str(birth_date: date, target_date: date) -> str:
    """Computes age in 'X years, Y months' format."""
    total_months = (target_date.year - birth_date.year) * 12 + (target_date.month - birth_date.month)
    if target_date.day < birth_date.day:
        total_months -= 1
    total_months = max(0, total_months)
    years = total_months // 12
    months = total_months % 12
    return f"{years} years, {months} months"


def generate_kp_predictive_narrative_data(
    birth_date: date,
    birth_time: dt_time,
    latitude: float,
    longitude: float,
    timezone_str: str = "Asia/Kolkata",
    person_name: str = "Native",
    gender: str = "male",
    target_date: Optional[date] = None,
    ayanamsa_id: int = 1,
    language: str = "en",
    months_ahead: int = 24,
) -> Dict[str, Any]:
    """Generates complete dictionary structure conforming to KpNarrativeResponse."""
    if target_date is None:
        target_date = date.today()

    # 1. Resolve birth datetime with proper timezone
    local_dt, utc_dt, jd, tz_name, offset_hours = resolve_birth_datetime(birth_date, birth_time, timezone_str)
    birth_dt = local_dt
    local_tz = local_dt.tzinfo

    # Resolve target datetime at noon local time
    target_dt = datetime.combine(target_date, dt_time(12, 0, 0), tzinfo=local_tz)

    # 2. Compute full KP chart using native ephemeris
    birth_input = BirthInput(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_str,
    )
    kp_chart = calculate_kp_chart(birth=birth_input, ayanamsa_id=ayanamsa_id)

    # 3. Extract lagna, moon sign, nakshatra
    lagna_sign_en = "Aries"
    lagna_sign_ta = "மேஷம்"
    if hasattr(kp_chart, "cusps") and kp_chart.cusps:
        lagna_sign_en = getattr(kp_chart.cusps[0], "sign", "Aries")
        lagna_sign_ta = SIGN_NAMES_TA.get(lagna_sign_en, lagna_sign_en)

    moon_sign_en = "Taurus"
    moon_sign_ta = "ரிஷபம்"
    nakshatra_en = "Rohini"
    nakshatra_ta = "ரோகிணி"

    planets_dict = getattr(kp_chart, "planets", {})
    if isinstance(planets_dict, dict) and "Moon" in planets_dict:
        m_info = planets_dict["Moon"]
        moon_sign_en = getattr(m_info, "sign", "Taurus")
        moon_sign_ta = SIGN_NAMES_TA.get(moon_sign_en, moon_sign_en)
        # Nakshatra
        nak_name = getattr(m_info, "nakshatra", None)
        if not nak_name and hasattr(m_info, "star_name"):
            nak_name = getattr(m_info, "star_name")
        if not nak_name and hasattr(m_info, "star_lord"):
            nak_name = getattr(m_info, "star_lord")
        if nak_name:
            nakshatra_en = str(nak_name)
            nakshatra_ta = NAKSHATRA_NAMES_TA.get(nakshatra_en, nakshatra_en)

    age_str = _calculate_age_str(birth_date, target_date)

    person_details = PersonDetails(
        name=person_name,
        birth_date=birth_date.strftime("%Y-%m-%d"),
        birth_time=birth_time.strftime("%H:%M:%S"),
        place="Location Coordinates",
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_str,
        gender=gender,
        lagna=lagna_sign_en,
        lagna_ta=lagna_sign_ta,
        moon_sign=moon_sign_en,
        moon_sign_ta=moon_sign_ta,
        nakshatra=nakshatra_en,
        nakshatra_ta=nakshatra_ta,
        current_age=age_str,
    )

    # 4. Section 1: Natal Event Promise
    natal_promise = evaluate_natal_event_promise(kp_chart)

    # 5. Section 2: Running Dasha-Bhukti-Antara Analysis
    running_dasha = evaluate_running_dasha_impact(kp_chart, birth_dt, target_dt)

    # 6. Section 3: Upcoming Milestone Windows (12-24 Months)
    milestone_windows = scan_upcoming_milestone_windows(
        kp_chart=kp_chart,
        birth_dt=birth_dt,
        start_dt=target_dt,
        months_ahead=months_ahead,
    )

    # 7. Section 4: Do's & Don'ts / Tailored Remedial Advice
    active_bhukti_lord = running_dasha.bhukti.lord
    active_md_lord = running_dasha.mahadasha.lord
    remedies = evaluate_tailored_remedies(
        kp_chart=kp_chart,
        active_bhukti_lord=active_bhukti_lord,
        active_mahadasha_lord=active_md_lord,
    )

    report_id = f"KPN-{uuid.uuid4().hex[:8].upper()}"

    resp = KpNarrativeResponse(
        report_id=report_id,
        generated_at=datetime.now().isoformat(),
        target_date=target_date.strftime("%Y-%m-%d"),
        person_details=person_details,
        natal_promise=natal_promise,
        running_dasha=running_dasha,
        milestone_windows=milestone_windows,
        remedies=remedies,
    )

    return resp.model_dump()
