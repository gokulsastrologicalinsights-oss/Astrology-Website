"""Brighu Naadi Astrology Endpoints.

Dedicated router serving classical Brighu Naadi insights, Vastu birth environment,
Jeeva Karaka (Jupiter) & Karma Karaka (Saturn) diagnostics, and exact event milestone timing.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.brighu_naadi import BrighuNaadiRequest, BrighuNaadiResponse
from app.services.ephemeris import calculate_full_horoscope
from app.services.brighu_naadi.engine import evaluate_brighu_naadi

router = APIRouter(prefix="/api/v1/vedic/brighu-naadi", tags=["Brighu Naadi"])


@router.post("", response_model=BrighuNaadiResponse, summary="Calculate Brighu Naadi Sangraha Analysis")
def calculate_brighu_naadi_endpoint(request: BrighuNaadiRequest) -> BrighuNaadiResponse:
    """Calculates comprehensive Brighu Naadi diagnostics:

    - Vastu & Birth Environment (road direction, entrance door facing, town sector, nearby temple)
    - Jeeva Karaka (Jupiter) life force profile & 12 bhavas from Jupiter
    - Karma Karaka (Saturn) profession profile & career start age
    - Exact predicted milestone ages (marriage, career, property, fame, finance, caution)
    - Physical appearance & health alerts (Sun, Rahu, Ketu sign markers)
    - Matched classical combinations from Dr. N. Srinivasan Shastry's treatise
    """
    try:
        aya_id = request.ayanamsa if request.ayanamsa is not None else 0
        if isinstance(aya_id, str):
            aya_id = 0

        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=aya_id,
            house_system_id=0,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            gender=request.gender or "male",
        )

        planets_data = {}
        for p in horoscope.planets:
            s_idx = getattr(p, "sign_index", None)
            if s_idx is None:
                s_idx = getattr(p, "sign_id", 1)
            if isinstance(s_idx, str):
                from app.services.prediction_rules.evaluator import SIGN_NAME_TO_INDEX
                s_idx = SIGN_NAME_TO_INDEX.get(s_idx.lower(), 1)

            planets_data[p.name] = {
                "sign_index": int(s_idx),
                "degree": getattr(p, "degree_in_sign", 0.0),
                "is_retrograde": getattr(p, "is_retrograde", False),
            }

        asc_idx = getattr(horoscope.ascendant, "sign_index", None)
        if asc_idx is None:
            asc_idx = getattr(horoscope.ascendant, "sign_id", 1)
        if isinstance(asc_idx, str):
            from app.services.prediction_rules.evaluator import SIGN_NAME_TO_INDEX
            asc_idx = SIGN_NAME_TO_INDEX.get(asc_idx.lower(), 1)

        ascendant_sign = int(asc_idx)

        return evaluate_brighu_naadi(
            planets_data=planets_data,
            ascendant_sign=ascendant_sign,
            gender=request.gender or "male",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Brighu Naadi calculation error: {str(e)}",
        )
