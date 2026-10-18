"""Metadata router exposing supported calculations, ayanamsas, houses, and limitations."""

from fastapi import APIRouter
from app.schemas.metadata import (
    MetadataResponse,
    AyanamsaOption,
    HouseSystemOption,
    LanguageOption,
    ChartCapability,
)
from app.services.ephemeris import AYANAMSA_NAMES, HOUSE_SYSTEM_NAMES

router = APIRouter(prefix="/api/v1", tags=["Metadata"])


@router.get("/metadata", response_model=MetadataResponse)
def get_metadata() -> MetadataResponse:
    """Return engine capabilities, supported ayanamsas, house systems, and verified features."""
    ayanamsas = [
        AyanamsaOption(
            id=aid,
            name=name,
            description=desc,
            is_default=(aid == 0),
        )
        for aid, (name, desc) in AYANAMSA_NAMES.items()
    ]

    houses = [
        HouseSystemOption(
            id=hid,
            name=name,
            description=desc,
            is_default=(hid == 0),
        )
        for hid, (name, desc) in HOUSE_SYSTEM_NAMES.items()
    ]

    languages = [
        LanguageOption(code="en", name="English", native_name="English"),
        LanguageOption(code="ta", name="Tamil", native_name="தமிழ்"),
    ]

    capabilities = [
        ChartCapability(
            id="vedic_horoscope",
            name="Vedic Birth Horoscope",
            description="Sidereal positions for 9 grahas + outer planets, 12 bhavas, nakshatras, and padas.",
        ),
        ChartCapability(
            id="panchang",
            name="Birth Panchang",
            description="Five limbs: Tithi, Nakshatra, Yoga, Karana, and Vara at exact moment of birth.",
        ),
        ChartCapability(
            id="vimshottari_dasa",
            name="Vimshottari Dasa Hierarchy",
            description="Mahadasha down to Pranadasha (depth 1..5) using 365.25-day year convention.",
        ),
        ChartCapability(
            id="kp_astrology",
            name="KP (Krishnamurti Paddhati) System",
            description="KP 249 sub-division table, cuspal sub-lords, and 4-tier planetary significators.",
        ),
        ChartCapability(
            id="chart_display_formats",
            name="Multi-Tradition Visualizations",
            description="Support for South Indian (fixed-sign) and North Indian (diamond/fixed-house) formats.",
        ),
    ]

    limitations = [
        "Astrological calculations are deterministic mathematical models based on traditional canons.",
        "They are not scientifically validated predictive claims and do not replace professional advice.",
        "Complex marriage cancellations and Shadbala calculations are currently in draft status.",
        "Historical daylight saving time for dates prior to 1970 requires validated timezone database lookup.",
    ]

    return MetadataResponse(
        engine="XALEN Ephemeris & Vedic Astrological Engine",
        version="1.0.0",
        verified_phases=["Phase A", "Phase B", "Phase C", "Phase D"],
        dasa_year_convention="Julian Year (365.25 Days / 120 Years = 43,830 Days)",
        kp_sub_divisions=249,
        supported_ayanamsas=ayanamsas,
        supported_house_systems=houses,
        supported_languages=languages,
        chart_capabilities=capabilities,
        limitations=limitations,
    )
