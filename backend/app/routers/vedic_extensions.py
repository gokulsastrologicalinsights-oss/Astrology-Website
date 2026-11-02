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
from app.schemas.medical_astrology import MedicalAstrologyResponse, MedicalAstrologyRequest
from app.schemas.double_transit import DoubleTransitRequest, DoubleTransitResponse
from app.schemas.kaksha_alerts import KakshaAlertRequest, KakshaAlertsResponse
from app.services.ephemeris import calculate_full_horoscope
from app.services.nabhasha_engine import detect_nabhasha_yogas
from app.services.ashtakavarga_engine import (
    calculate_ashtakavarga,
    compute_all_prastara_matrices,
    build_all_kaksha_grids,
    evaluate_kaksha_transit,
)
from app.services.ashtakavarga_engine.kaksha_alert_engine import generate_kaksha_transit_alerts
from app.services.double_transit_engine import calculate_double_transit_radar, DOMAINS
from app.services.yoga_engine import calculate_vedic_yogas
from app.services.shadbala_engine import calculate_shadbala
from app.services.dosha_engine import calculate_unified_doshas
from app.services.varga_engine import calculate_shodashvarga
from app.services.medical_astrology_engine import calculate_medical_astrology
from app.services.kp_service import calculate_kp_chart
from app.services.dasa_service import calculate_dasa
from app.services.varga_engine import calculate_varga_d1_d9
from app.services.kn_rao_engine import (
    evaluate_kn_rao_advanced_research,
    evaluate_consolidated_kakshya_and_timing,
    evaluate_service_vs_self_employment,
    evaluate_technical_profession,
    evaluate_author_journalist,
    evaluate_marital_discord,
    evaluate_medical_timing,
    KnRaoAdvancedResearchResponse,
    ConsolidatedKakshyaResponse,
    ServiceVsSelfEmploymentResult,
    TechnicalProfessionResult,
    AuthorJournalistResult,
    MaritalDiscordResult,
    MedicalTimingResult,
)

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
def calculate_medical_astrology_endpoint(request: MedicalAstrologyRequest) -> MedicalAstrologyResponse:
    """Evaluate Classical Vedic & KP Medical Astrology adhering to strict research safety policies.
    
    Supports direct input birth parameters or synchronizing directly from a saved_horoscope_id.
    """
    try:
        b_date = request.birth_date
        b_time = request.birth_time
        tz = request.timezone or "Asia/Kolkata"
        lat = request.latitude
        lon = request.longitude
        ayanamsa = request.ayanamsa if request.ayanamsa is not None else 0
        house_system = request.house_system if request.house_system is not None else 0
        gender = request.gender or "male"

        # If saved_horoscope_id is supplied, look up chart details
        if request.saved_horoscope_id:
            clean_id = request.saved_horoscope_id.strip()
            row = None
            try:
                from app.services.auth_service import get_supabase_client
                supabase = get_supabase_client()
                if supabase:
                    res = supabase.table("saved_horoscopes").select("*").eq("id", clean_id).execute()
                    if res.data and len(res.data) > 0:
                        row = res.data[0]
            except Exception:
                pass

            if not row:
                import json
                from pathlib import Path
                local_path = Path("backend/data/saved_horoscope_writings.json")
                if local_path.exists():
                    try:
                        with open(local_path, "r", encoding="utf-8") as f:
                            saved_list = json.load(f)
                            for item in saved_list:
                                if str(item.get("id")) == clean_id:
                                    row = item
                                    break
                    except Exception:
                        pass

            if row:
                b_date = row.get("birth_date") or b_date
                b_time = row.get("birth_time") or b_time
                tz = row.get("timezone") or tz
                if row.get("latitude") is not None:
                    lat = float(row.get("latitude"))
                if row.get("longitude") is not None:
                    lon = float(row.get("longitude"))
                if row.get("ayanamsa") is not None:
                    ayanamsa = int(row.get("ayanamsa"))
                if row.get("house_system") is not None:
                    house_system = int(row.get("house_system"))
                if row.get("gender"):
                    gender = str(row.get("gender"))

        if not b_date or not b_time or lat is None or lon is None:
            raise HTTPException(
                status_code=422,
                detail="Incomplete birth parameters. Please provide birth_date, birth_time, latitude, and longitude, or a valid saved_horoscope_id.",
            )

        horoscope = calculate_full_horoscope(
            birth_date=b_date,
            birth_time=b_time,
            timezone_str=tz,
            latitude=lat,
            longitude=lon,
            ayanamsa_id=ayanamsa,
            house_system_id=house_system,
            include_panchang=False,
            include_outer_planets=False,
            include_nabhasha=False,
            include_ashtakavarga=False,
            include_vedic_yogas=False,
            include_varga=False,
            include_doshas=False,
            gender=gender,
        )

        # Calculate KP if possible
        kp_res = None
        try:
            from app.schemas.kp import KpRequest
            kp_req = KpRequest(
                birth_date=b_date,
                birth_time=b_time,
                timezone=tz,
                latitude=lat,
                longitude=lon,
                ayanamsa=ayanamsa,
                house_system=house_system,
            )
            kp_res = calculate_kp_chart(
                birth=kp_req,
                ayanamsa_id=ayanamsa,
                house_system_id=house_system,
            )
        except Exception:
            pass

        # Calculate Dasa if possible
        dasa_res = None
        try:
            from app.schemas.dasa import DasaRequest
            dasa_req = DasaRequest(
                birth_date=b_date,
                birth_time=b_time,
                timezone=tz,
                latitude=lat,
                longitude=lon,
                depth=3,
                ayanamsa=ayanamsa,
                house_system=house_system,
            )
            dasa_res = calculate_dasa(
                birth=dasa_req,
                depth=3,
                ayanamsa_id=ayanamsa,
                house_system_id=house_system,
            )
        except Exception:
            pass

        result = calculate_medical_astrology(
            horoscope=horoscope,
            dasa=dasa_res,
            kp=kp_res,
            gender=gender,
        )
        return result
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Medical astrology calculation failed: {str(exc)}")


# ---------------------------------------------------------------------------
# Double Transit ("Guru-Shani") Event Timing Radar
# ---------------------------------------------------------------------------

@router.post("/double-transit", response_model=DoubleTransitResponse, summary="Double Transit ('Guru-Shani') Event Timing Radar")
def calculate_double_transit_endpoint(request: DoubleTransitRequest) -> DoubleTransitResponse:
    """Calculates Double Transit (Guru-Shani Samyama) alignment windows across a 1-5 year horizon."""
    try:
        return calculate_double_transit_radar(request)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Double Transit calculation failed: {str(exc)}",
        )


@router.get("/double-transit/domains", summary="List available life domains for Double Transit Radar")
def get_double_transit_domains():
    """Returns domain metadata (Marriage, Career, Childbirth, Wealth, Property, Foreign, Health)."""
    return {"domains": list(DOMAINS.values())}


# ---------------------------------------------------------------------------
# Ashtakavarga Kaksha Transit Trigger Alert System
# ---------------------------------------------------------------------------

@router.post("/ashtakavarga/kaksha-alerts", response_model=KakshaAlertsResponse, summary="Ashtakavarga Kaksha Transit Trigger Alerts")
def calculate_kaksha_alerts_endpoint(request: KakshaAlertRequest) -> KakshaAlertsResponse:
    """Computes real-time Ashtakavarga Kaksha Trigger Alerts (1-Bindu Auspicious vs 0-Bindu Obstacle)."""
    try:
        return generate_kaksha_transit_alerts(request)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kaksha transit alerts calculation failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# K.N. Rao Advanced Astrological Research Engine Endpoints
# ---------------------------------------------------------------------------

def _extract_kn_rao_chart_inputs(request: HoroscopeRequest):
    """Internal helper to calculate ephemeris, D1/D9 vargas, and active dasha for K.N. Rao research."""
    horoscope = calculate_full_horoscope(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        timezone_str=request.timezone,
        latitude=request.latitude,
        longitude=request.longitude,
        ayanamsa_id=request.ayanamsa or 0,
        house_system_id=request.house_system or 0,
        include_panchang=False,
        include_outer_planets=False,
    )
    varga_res = calculate_varga_d1_d9(horoscope.planets, horoscope.ascendant)
    
    planets_data = {}
    for p in horoscope.planets:
        planets_data[p.name] = {
            "sign_index": p.sign_index,
            "degree_in_sign": p.degree_in_sign,
            "longitude": p.longitude,
            "is_retrograde": getattr(p, "is_retrograde", False),
            "is_combust": getattr(p, "is_combust", False),
            "nakshatra_name": getattr(p, "nakshatra_name", getattr(p, "nakshatra", "")),
        }
        
    d9_planets = {}
    d9_list = varga_res.d9_chart.get("planets", []) if isinstance(varga_res.d9_chart, dict) else []
    for dp in d9_list:
        p_name = dp.get("name")
        if p_name:
            d9_planets[p_name] = {
                "sign_index": dp.get("sign_index", 1),
                "degree_in_sign": dp.get("degree_in_sign", 0.0),
            }
            
    lagna_sign = horoscope.ascendant.sign_index
    lagna_deg = (
        horoscope.ascendant.degree_in_sign
        if hasattr(horoscope.ascendant, "degree_in_sign")
        else (horoscope.ascendant.degree % 30.0)
    )
    
    active_md = None
    active_ad = None
    try:
        birth_in = BirthInput(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone=request.timezone,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_id=request.ayanamsa or 0,
            house_system_id=request.house_system or 0,
        )
        dasa_res = calculate_dasa(birth_in)
        if dasa_res and dasa_res.active_period:
            active_md = dasa_res.active_period.mahadasha
            active_ad = dasa_res.active_period.antardasha
    except Exception:
        pass
        
    return planets_data, d9_planets, lagna_sign, lagna_deg, active_md, active_ad


@router.post(
    "/kn-rao-research",
    response_model=KnRaoAdvancedResearchResponse,
    summary="Comprehensive K.N. Rao Advanced Astrological Research Suite"
)
def calculate_kn_rao_research_endpoint(request: HoroscopeRequest) -> KnRaoAdvancedResearchResponse:
    """Calculates all empirical research findings from 'Advanced Techniques of Astrological Predictions' (BVB / K.N. Rao)."""
    try:
        planets_data, d9_planets, lagna_sign, lagna_deg, active_md, active_ad = _extract_kn_rao_chart_inputs(request)
        return evaluate_kn_rao_advanced_research(
            planets_data=planets_data,
            d9_planets=d9_planets,
            lagna_sign=lagna_sign,
            lagna_degree=lagna_deg,
            active_mahadasha=active_md,
            active_antardasha=active_ad,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"K.N. Rao Advanced Research calculation failed: {str(exc)}",
        )


@router.post(
    "/consolidated-kakshya",
    response_model=ConsolidatedKakshyaResponse,
    summary="Dr. R.K. Aggarwal Table III Kakshya Chart + P.C. Verma 8-Part Timing"
)
def calculate_consolidated_kakshya_endpoint(request: HoroscopeRequest) -> ConsolidatedKakshyaResponse:
    """Evaluates the 12-sign x 8-kakshya consolidated matrix and Mahadasha 8-part career trajectory."""
    try:
        planets_data, _, lagna_sign, _, active_md, _ = _extract_kn_rao_chart_inputs(request)
        return evaluate_consolidated_kakshya_and_timing(
            planets_data=planets_data,
            lagna_sign=lagna_sign,
            active_mahadasha_lord=active_md,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Consolidated Kakshya calculation failed: {str(exc)}",
        )


@router.post(
    "/career-research",
    summary="Empirical Career Research: Service vs Business, Tech Scoring, and Literary Talents"
)
def calculate_career_research_endpoint(request: HoroscopeRequest):
    """Evaluates S.N. Kapoor, R.C. Sharma, and Col. A.K. Gour career models."""
    try:
        planets_data, d9_planets, lagna_sign, _, _, _ = _extract_kn_rao_chart_inputs(request)
        service_res = evaluate_service_vs_self_employment(planets_data, lagna_sign)
        tech_res = evaluate_technical_profession(planets_data, d9_planets, lagna_sign)
        author_res = evaluate_author_journalist(planets_data, d9_planets, lagna_sign)
        return {
            "service_vs_self_employment": service_res,
            "technical_profession": tech_res,
            "author_vs_journalist": author_res,
        }
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Career research calculation failed: {str(exc)}",
        )


@router.post(
    "/marital-discord-research",
    response_model=MaritalDiscordResult,
    summary="Shunny Nigam 4 Main + 2 Supplementary Rules Marital Discord Analysis"
)
def calculate_marital_discord_endpoint(request: HoroscopeRequest) -> MaritalDiscordResult:
    """Evaluates Upapada 2nd house affliction, 7th lord D9 dignity, Venus afflictions, and dusthana links."""
    try:
        planets_data, d9_planets, lagna_sign, _, active_md, active_ad = _extract_kn_rao_chart_inputs(request)
        return evaluate_marital_discord(
            planets_data=planets_data,
            d9_planets=d9_planets,
            lagna_sign=lagna_sign,
            active_mahadasha=active_md,
            active_antardasha=active_ad,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Marital discord research calculation failed: {str(exc)}",
        )




