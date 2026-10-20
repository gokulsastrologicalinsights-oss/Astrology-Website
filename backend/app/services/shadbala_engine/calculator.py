"""Master orchestrator for the Shadbala (Six-fold Planetary Strength) engine.

Classical Reference:
- Brihat Parasara Hora Shastra (BPHS), Chapter 23: Shadbala and Bhava Bala.
- Evaluates the 7 classical grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
- Aggregates Sthana, Dig, Kala, Cheshta, Naisargika, and Drik balas.
- Computes virupas, rupas, required strength thresholds, strength ratios, and rankings.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from app.schemas.common import CalculationMetadata
from app.schemas.horoscope import AscendantInfo, HouseInfo, PanchangInfo, PlanetInfo
from app.schemas.shadbala import (
    SHADBALA_REQUIRED_VIRUPAS,
    PlanetShadbalaDetail,
    ShadbalaResponse,
)
from app.services.shadbala_engine.cheshta_bala import calc_cheshta_bala
from app.services.shadbala_engine.dig_bala import calc_dig_bala
from app.services.shadbala_engine.drik_bala import calc_drik_bala
from app.services.shadbala_engine.kala_bala import calc_kala_bala
from app.services.shadbala_engine.models import (
    AscendantCtx,
    BirthCtx,
    ChartCtx,
    HouseCtx,
    PlanetCtx,
)
from app.services.shadbala_engine.sthana_bala import calc_sthana_bala

# ---------------------------------------------------------------------------
# Classical Naisargika Bala (Natural Strength) per BPHS Ch. 23, Sloka 31.
# Units: virupas (60 virupas = 1 rupa).
# Proportional to luminous brightness:
# Sun (60) > Moon (51.43) > Venus (42.86) > Jupiter (34.29) > Mercury (25.71) > Mars (17.14) > Saturn (8.57)
# ---------------------------------------------------------------------------
NAISARGIKA_BALA: Dict[str, float] = {
    "Sun":     60.00,
    "Moon":    51.43,
    "Venus":   42.86,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars":    17.14,
    "Saturn":   8.57,
}

CLASSICAL_SEVEN = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def _build_chart_context(
    planets: List[PlanetInfo],
    ascendant: AscendantInfo,
    houses: List[HouseInfo],
    panchang: Optional[PanchangInfo],
    birth_date: str,
    birth_time: str,
    timezone_str: str,
    latitude: float,
    longitude: float,
) -> ChartCtx:
    """Transform API schema objects into engine internal dataclasses."""
    # Filter and extract classical 7 grahas
    planet_ctx_list: List[PlanetCtx] = []
    sun_lon = 0.0
    moon_lon = 0.0

    for p in planets:
        if p.name in CLASSICAL_SEVEN:
            ctx_p = PlanetCtx(
                name=p.name,
                body_id=p.body_id,
                longitude=p.longitude,
                degree_in_sign=p.degree_in_sign,
                sign_index=p.sign_index,
                speed_deg_per_day=p.speed_deg_per_day,
                is_retrograde=p.is_retrograde,
                nakshatra_lord=p.nakshatra.lord if p.nakshatra else "",
            )
            planet_ctx_list.append(ctx_p)
            if p.name == "Sun":
                sun_lon = p.longitude
            elif p.name == "Moon":
                moon_lon = p.longitude

    house_ctx_list = [
        HouseCtx(house_number=h.house_number, sign_index=h.sign_index)
        for h in houses
    ]

    asc_ctx = AscendantCtx(
        degree=ascendant.degree,
        sign_index=ascendant.sign_index,
        degree_in_sign=ascendant.degree_in_sign,
    )

    birth_ctx = BirthCtx(
        birth_date=birth_date,
        birth_time=birth_time,
        timezone_str=timezone_str,
        latitude=latitude,
        longitude=longitude,
    )

    # Determine day/night birth: Sun in houses 7-12 = above horizon (day birth)
    sign_to_house: Dict[int, int] = {h.sign_index: h.house_number for h in houses}
    sun_sign = int(sun_lon // 30.0) + 1
    sun_house = sign_to_house.get(sun_sign, 1)
    is_day_birth = sun_house in (7, 8, 9, 10, 11, 12)

    vara_name = panchang.vara if panchang and panchang.vara else ""

    return ChartCtx(
        planets=planet_ctx_list,
        houses=house_ctx_list,
        ascendant=asc_ctx,
        birth=birth_ctx,
        vara_name=vara_name,
        sun_longitude=sun_lon,
        moon_longitude=moon_lon,
        is_day_birth=is_day_birth,
    )


def calculate_shadbala(
    planets: List[PlanetInfo],
    ascendant: AscendantInfo,
    houses: List[HouseInfo],
    panchang: Optional[PanchangInfo] = None,
    birth_date: str = "2000-01-01",
    birth_time: str = "12:00",
    timezone_str: str = "UTC",
    latitude: float = 0.0,
    longitude: float = 0.0,
    metadata: Optional[CalculationMetadata] = None,
) -> ShadbalaResponse:
    """Calculate complete Shadbala for the seven classical grahas."""
    ctx = _build_chart_context(
        planets=planets,
        ascendant=ascendant,
        houses=houses,
        panchang=panchang,
        birth_date=birth_date,
        birth_time=birth_time,
        timezone_str=timezone_str,
        latitude=latitude,
        longitude=longitude,
    )

    details: List[PlanetShadbalaDetail] = []

    for p in ctx.planets:
        sthana = calc_sthana_bala(p, ctx)
        dig = calc_dig_bala(p, ctx)
        kala = calc_kala_bala(p, ctx)
        cheshta = calc_cheshta_bala(p)
        naisargika = NAISARGIKA_BALA.get(p.name, 0.0)
        drik = calc_drik_bala(p, ctx)

        total_virupas = round(
            sthana.total + dig + kala.total + cheshta + naisargika + drik, 4
        )
        total_rupas = round(total_virupas / 60.0, 4)
        required = SHADBALA_REQUIRED_VIRUPAS.get(p.name, 300.0)
        ratio = round(total_virupas / required, 4)
        is_strong = ratio >= 1.0

        details.append(
            PlanetShadbalaDetail(
                planet=p.name,
                sthana_bala=sthana,
                dig_bala=dig,
                kala_bala=kala,
                cheshta_bala=cheshta,
                naisargika_bala=naisargika,
                drik_bala=drik,
                total_virupas=total_virupas,
                total_rupas=total_rupas,
                required_virupas=required,
                ratio=ratio,
                is_strong=is_strong,
                rank=0,  # Assigned below
            )
        )

    # Sort descending by total_virupas to assign ranks 1 through 7
    details.sort(key=lambda d: d.total_virupas, reverse=True)
    for rank_idx, d in enumerate(details, start=1):
        d.rank = rank_idx

    strongest = details[0].planet if details else "None"
    weakest = details[-1].planet if details else "None"

    notes = [
        "Calculated according to Brihat Parasara Hora Shastra (BPHS), Chapter 27.",
        "Rahu and Ketu are chaya grahas (shadow planets) and excluded per classical canon.",
        "Saptavargaja Bala evaluates all 7 classical divisions (D1, D2, D3, D7, D9, D12, D30) using Panchadha Maitri compound dignities.",
        "Dig Bala uses continuous angular distance from Nirbala cardinal cusps divided by 3.",
        "Ayana Bala evaluates continuous declination-based solstice strength per BPHS.",
        "Drik Bala employs BPHS continuous piecewise 30°-300° Drishti and Vishesha Drishti divided by 4.",
    ]

    return ShadbalaResponse(
        metadata=metadata,
        planets=details,
        strongest_planet=strongest,
        weakest_planet=weakest,
        calculation_notes=notes,
    )
