"""Dedicated API endpoints for classical Vedic extensions: Nabhasha Yogas and Ashtakavarga."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.common import BirthInput
from app.schemas.horoscope import HoroscopeRequest, KakshaTransitEvaluationRequest
from app.schemas.nabhasha import NabhashaResponse
from app.schemas.ashtakavarga import (
    AshtakavargaResponse,
    PrastaraResponse,
    KakshaResponse,
    KakshaTransitResult,
)
from app.schemas.yoga import VedicYogaResponse
from app.schemas.shadbala import ShadbalaResponse
from app.schemas.dosha import DoshaEvaluationRequest, UnifiedDoshaResponse
from app.schemas.varga import ShodashvargaResponse
from app.schemas.medical_astrology import MedicalAstrologyResponse
from app.services.ephemeris import calculate_full_horoscope
from app.services.nabhasha_engine import detect_nabhasha_yogas
from app.services.ashtakavarga_engine import (
    calculate_ashtakavarga,
    compute_all_prastara_matrices,
    build_all_kaksha_grids,
    evaluate_kaksha_transit,
)
from app.services.yoga_engine import calculate_vedic_yogas
from app.services.shadbala_engine import calculate_shadbala
from app.services.dosha_engine import calculate_unified_doshas
from app.services.varga_engine import calculate_shodashvarga
from app.services.medical_astrology_engine import calculate_medical_astrology
from app.services.kp_service import calculate_kp_chart
from app.services.dasa_service import calculate_dasa

router = APIRouter(prefix="/api/v1/vedic", tags=["Vedic Extensions"])


@router.post("/yogas", response_model=VedicYogaResponse)
def calculate_vedic_yogas_endpoint(request: HoroscopeRequest) -> VedicYogaResponse:
    """Evaluate comprehensive classical Vedic Yogas (Gajakesari, Raja, Dhana, Mahapurusha, etc.)."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=True,
            gender=request.gender or "male",
        )
        if not horoscope.vedic_yogas:
            raise HTTPException(status_code=500, detail="Vedic yoga calculation returned empty response")
        horoscope.vedic_yogas.metadata = horoscope.metadata
        return horoscope.vedic_yogas
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vedic yoga calculation failed: {str(exc)}")


@router.post("/nabhasha", response_model=NabhashaResponse)
def calculate_nabhasha_endpoint(request: HoroscopeRequest) -> NabhashaResponse:
    """Detect and return classical Nabhasha Yogas for the given birth data."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=True,
            include_ashtakavarga=False,
        )
        if not horoscope.nabhasha_yogas:
            raise HTTPException(status_code=500, detail="Nabhasha calculation returned empty response")
        horoscope.nabhasha_yogas.metadata = horoscope.metadata
        return horoscope.nabhasha_yogas
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Nabhasha calculation failed: {str(exc)}")


@router.post("/ashtakavarga", response_model=AshtakavargaResponse)
def calculate_ashtakavarga_endpoint(request: HoroscopeRequest) -> AshtakavargaResponse:
    """Compute Bhinnashtakavarga (BAV), Sarvashtakavarga (SAV), and Shodhana reductions."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=True,
        )
        if not horoscope.ashtakavarga:
            raise HTTPException(status_code=500, detail="Ashtakavarga calculation returned empty response")
        horoscope.ashtakavarga.metadata = horoscope.metadata
        return horoscope.ashtakavarga
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ashtakavarga calculation failed: {str(exc)}")


@router.post("/ashtakavarga/prastara", response_model=PrastaraResponse)
def calculate_prastara_endpoint(request: HoroscopeRequest) -> PrastaraResponse:
    """Compute complete 8-donor by 12-sign Prastara matrices for all 7 classical planets."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
        )
        contributor_signs = {
            p.name: p.sign_index
            for p in horoscope.planets
            if p.name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        }
        contributor_signs["Lagna"] = horoscope.ascendant.sign_index
        prastara_dict = compute_all_prastara_matrices(contributor_signs)
        grand_total = sum(p.total_bindus for p in prastara_dict.values())
        status_val = "PASSED" if grand_total == 337 else "FAILED_INVARIANT"
        return PrastaraResponse(
            metadata=horoscope.metadata,
            prastara=prastara_dict,
            grand_total_bindus=grand_total,
            validation_status=status_val,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prastara calculation failed: {str(exc)}")


@router.post("/ashtakavarga/kaksha", response_model=KakshaResponse)
def calculate_kaksha_endpoint(request: HoroscopeRequest) -> KakshaResponse:
    """Compute full 96-Kaksha breakdown (12 signs × 8 Kakshas) for all 7 classical planets."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
        )
        contributor_signs = {
            p.name: p.sign_index
            for p in horoscope.planets
            if p.name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        }
        contributor_signs["Lagna"] = horoscope.ascendant.sign_index
        prastara_dict = compute_all_prastara_matrices(contributor_signs)
        kaksha_grids = build_all_kaksha_grids(prastara_dict)
        return KakshaResponse(
            metadata=horoscope.metadata,
            kaksha_grids=kaksha_grids,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Kaksha calculation failed: {str(exc)}")


@router.post("/ashtakavarga/kaksha/transit", response_model=KakshaTransitResult)
def evaluate_kaksha_transit_endpoint(request: KakshaTransitEvaluationRequest) -> KakshaTransitResult:
    """Evaluate whether a transiting planet's current position falls in an auspicious Kaksha."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
        )
        contributor_signs = {
            p.name: p.sign_index
            for p in horoscope.planets
            if p.name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        }
        contributor_signs["Lagna"] = horoscope.ascendant.sign_index
        prastara_dict = compute_all_prastara_matrices(contributor_signs)

        result = evaluate_kaksha_transit(
            transiting_planet=request.transit.transiting_planet,
            prastara_dict=prastara_dict,
            transit_longitude=request.transit.transit_longitude,
            transit_sign_index=request.transit.transit_sign_index,
            transit_degree_in_sign=request.transit.transit_degree_in_sign,
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Kaksha transit evaluation failed: {str(exc)}")



@router.post("/shadbala", response_model=ShadbalaResponse)
def calculate_shadbala_endpoint(request: HoroscopeRequest) -> ShadbalaResponse:
    """Calculate classical Shadbala (Six-fold Planetary Strength) per BPHS Ch. 23."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=True,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            gender=request.gender or "male",
        )
        result = calculate_shadbala(
            planets=horoscope.planets,
            ascendant=horoscope.ascendant,
            houses=horoscope.houses,
            panchang=horoscope.panchang,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            metadata=horoscope.metadata,
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Shadbala calculation failed: {str(exc)}")


@router.post("/doshas", response_model=UnifiedDoshaResponse)
def calculate_doshas_endpoint(request: DoshaEvaluationRequest) -> UnifiedDoshaResponse:
    """Evaluate comprehensive classical Vedic Doshas (Kuja, Kaal Sarp, Sadesati, Pitru, Guru Chandal, Shrapit, Grahan)."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            gender=request.gender or "male",
        )
        result = calculate_unified_doshas(
            planets=horoscope.planets,
            ascendant_sign_idx=horoscope.ascendant.sign_index,
            houses=horoscope.houses,
            include_2nd_house_in_kuja=request.include_2nd_house_in_kuja,
            transit_date=request.transit_date,
            transit_time=request.transit_time,
            ayanamsa_id=request.ayanamsa,
            metadata=horoscope.metadata,
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Dosha calculation failed: {str(exc)}")


@router.post("/vargas", response_model=ShodashvargaResponse, summary="Calculate 16 classical Shodashvarga charts")
def calculate_shodashvarga_endpoint(request: HoroscopeRequest) -> ShodashvargaResponse:
    """Calculate all 16 canonical Shodashvarga divisional charts (D1 to D60) per BPHS Ch. 6."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            include_varga=False,
            gender=request.gender or "male",
        )
        result = calculate_shodashvarga(
            planets=horoscope.planets,
            ascendant=horoscope.ascendant,
            metadata=horoscope.metadata,
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Shodashvarga calculation failed: {str(exc)}")


@router.post("/medical-astrology", response_model=MedicalAstrologyResponse, summary="Calculate Classical Vedic & KP Medical Astrology")
def calculate_medical_astrology_endpoint(request: HoroscopeRequest) -> MedicalAstrologyResponse:
    """Evaluate Classical Vedic & KP Medical Astrology adhering to strict research safety policies."""
    try:
        horoscope = calculate_full_horoscope(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone_str=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa,
            house_system_id=request.house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            include_varga=False,
            include_doshas=False,
            gender=request.gender or "male",
        )

        # Calculate KP if possible
        kp_res = None
        try:
            from app.schemas.kp import KpRequest
            kp_req = KpRequest(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                timezone=request.timezone,
                latitude=request.latitude,
                longitude=request.longitude,
                ayanamsa=request.ayanamsa,
                house_system=request.house_system,
            )
            kp_res = calculate_kp_chart(
                birth=kp_req,
                ayanamsa_id=request.ayanamsa,
                house_system_id=request.house_system,
            )
        except Exception:
            pass

        # Calculate Dasa if possible
        dasa_res = None
        try:
            from app.schemas.dasa import DasaRequest
            dasa_req = DasaRequest(
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                timezone=request.timezone,
                latitude=request.latitude,
                longitude=request.longitude,
                depth=3,
                ayanamsa=request.ayanamsa,
                house_system=request.house_system,
            )
            dasa_res = calculate_dasa(
                birth=dasa_req,
                depth=3,
                ayanamsa_id=request.ayanamsa,
                house_system_id=request.house_system,
            )
        except Exception:
            pass

        result = calculate_medical_astrology(
            horoscope=horoscope,
            dasa=dasa_res,
            kp=kp_res,
            gender=request.gender or "male",
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Medical astrology calculation failed: {str(exc)}")



