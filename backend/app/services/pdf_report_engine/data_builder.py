"""Data aggregator for Gokul's Astrological Insights PDF horoscope reports.

Assembles unified horoscope data by calling XALEN-based core engines:
1. Core Horoscope (D1 Rasi, Ascendant, Planets, Houses, Panchang)
2. 16 Shodashvarga Charts (D1 through D60 with Shashtyamsa deities)
3. Shadbala Engine (Six-fold planetary strength & rankings)
4. Ashtakavarga Engine (BAV, SAV 337 invariant, Shodhana reductions)
5. Vedic Yoga & Cancellation Engine (Raja, Dhana, Mahapurusha, NBRY, Kemadruma)
6. Unified Dosha Engine (Kuja, Kaal Sarp, Sadesati, Additional Doshas)
7. Vimshottari Dasa-Bhukti Engine & Classical Shastric Remedies
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional

from app.schemas.common import BirthInput
from app.schemas.horoscope import HoroscopeRequest, HoroscopeResponse
from app.schemas.varga import ShodashvargaResponse
from app.schemas.shadbala import ShadbalaResponse
from app.schemas.dosha import UnifiedDoshaResponse
from app.schemas.dasa import DasaResponse
from app.schemas.remedies import RemedyItem, NavagrahaTempleItem

from app.services.ephemeris import calculate_full_horoscope
from app.services.varga_engine import calculate_shodashvarga_from_horoscope_dict
from app.services.shadbala_engine import calculate_shadbala
from app.services.dosha_engine import calculate_unified_doshas
from app.services.dasa_service import calculate_dasa
from app.services.remedy_engine.repository import VERIFIED_REMEDIES, VERIFIED_TEMPLES

logger = logging.getLogger("gai.pdf.builder")


@dataclass
class ReportData:
    """Consolidated data model holding all calculated values for the 9-page report."""
    # Metadata & Native Info
    native_name: str
    gender: str
    birth_date: str
    birth_time: str
    birth_place: str
    latitude: float
    longitude: float
    timezone_str: str
    ayanamsa_name: str
    house_system_name: str
    is_verified: bool
    report_id: str
    generated_at: str
    language: str = "en"

    # Core Calculations
    horoscope: HoroscopeResponse = None
    shodashvarga: Optional[ShodashvargaResponse] = None
    shadbala: Optional[ShadbalaResponse] = None
    doshas: Optional[UnifiedDoshaResponse] = None
    dasa: Optional[DasaResponse] = None
    remedies: List[Dict[str, Any]] = field(default_factory=list)
    temples: List[Dict[str, Any]] = field(default_factory=list)


def build_report_data(
    birth_input: BirthInput,
    native_name: Optional[str] = None,
    gender: Optional[str] = "male",
    ayanamsa_id: int = 0,
    house_system_id: int = 0,
    language: str = "en",
    report_id: Optional[str] = None,
    is_verified: bool = True,
    horoscope_response: Optional[HoroscopeResponse] = None,
) -> ReportData:
    """Build a complete ReportData object from birth inputs or existing HoroscopeResponse."""
    import uuid
    from datetime import datetime, timezone

    if report_id is None:
        report_id = str(uuid.uuid4())[:8].upper()

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    name = native_name or "Native"
    place_str = f"{birth_input.latitude:.4f}°N, {birth_input.longitude:.4f}°E"

    ayanamsa_labels = {0: "Lahiri (Chitra Paksha)", 1: "KP Old", 2: "Raman", 3: "Yukteshwar", 4: "Fagan-Bradley"}
    ayanamsa_name = ayanamsa_labels.get(ayanamsa_id, "Lahiri")

    # 1. Core Horoscope
    if horoscope_response is None:
        horoscope_response = calculate_full_horoscope(
            birth_date=birth_input.birth_date,
            birth_time=birth_input.birth_time,
            timezone_str=birth_input.timezone,
            latitude=birth_input.latitude,
            longitude=birth_input.longitude,
            ayanamsa_id=ayanamsa_id,
            house_system_id=house_system_id,
            include_panchang=True,
            include_outer_planets=True,
            include_nabhasha=True,
            include_ashtakavarga=True,
            include_vedic_yogas=True,
            include_varga=True,
            gender=gender or "male",
        )

    horo_dict = horoscope_response.model_dump()

    # 2. Shodashvarga (16 divisional charts)
    shodashvarga_res = None
    try:
        shodashvarga_res = calculate_shodashvarga_from_horoscope_dict(horo_dict)
    except Exception as exc:
        logger.warning("Could not calculate Shodashvarga for PDF report: %s", exc)

    # 3. Shadbala
    shadbala_res = None
    try:
        shadbala_res = calculate_shadbala(
            planets=horoscope_response.planets,
            ascendant=horoscope_response.ascendant,
            houses=horoscope_response.houses,
            panchang=horoscope_response.panchang,
            birth_date=birth_input.birth_date.isoformat(),
            birth_time=birth_input.birth_time.isoformat() if hasattr(birth_input.birth_time, "isoformat") else str(birth_input.birth_time),
            timezone_str=birth_input.timezone,
            latitude=birth_input.latitude,
            longitude=birth_input.longitude,
        )
    except Exception as exc:
        logger.warning("Could not calculate Shadbala for PDF report: %s", exc)

    # 4. Unified Doshas
    dosha_res = None
    try:
        dosha_res = calculate_unified_doshas(
            planets=horoscope_response.planets,
            ascendant_sign_idx=horoscope_response.ascendant.sign_index,
            houses=horoscope_response.houses,
            ayanamsa_id=ayanamsa_id,
        )
    except Exception as exc:
        logger.warning("Could not calculate Unified Doshas for PDF report: %s", exc)

    # 5. Dasa-Bhukti Tree
    dasa_res = None
    try:
        dasa_res = calculate_dasa(
            birth=birth_input,
            depth=2,
            ayanamsa_id=ayanamsa_id,
            house_system_id=house_system_id,
            target_date=date.today(),
        )
    except Exception as exc:
        logger.warning("Could not calculate Dasa for PDF report: %s", exc)

    # 6. Remedies and Temples from validated knowledge base
    all_remedies = VERIFIED_REMEDIES
    all_temples = VERIFIED_TEMPLES

    return ReportData(
        native_name=name,
        gender=gender or "male",
        birth_date=str(birth_input.birth_date),
        birth_time=str(birth_input.birth_time),
        birth_place=place_str,
        latitude=birth_input.latitude,
        longitude=birth_input.longitude,
        timezone_str=birth_input.timezone,
        ayanamsa_name=ayanamsa_name,
        house_system_name="Placidus / KP" if house_system_id == 2 else "Whole Sign",
        is_verified=is_verified,
        report_id=report_id,
        generated_at=now_iso,
        language=language,
        horoscope=horoscope_response,
        shodashvarga=shodashvarga_res,
        shadbala=shadbala_res,
        doshas=dosha_res,
        dasa=dasa_res,
        remedies=all_remedies[:6],
        temples=all_temples[:4],
    )
