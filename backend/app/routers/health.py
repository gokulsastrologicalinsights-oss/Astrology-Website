"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter
import xalen

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Verify backend status and XALEN astronomical engine availability."""
    try:
        # Perform quick sanity check on xalen engine (JD for J2000.0)
        jd_check = xalen.julian_day(2000, 1, 1, 12.0)
        engine_available = abs(jd_check - 2451545.0) < 1e-5
    except Exception as exc:
        engine_available = False
        error_msg = str(exc)
    else:
        error_msg = None

    return {
        "status": "healthy" if engine_available else "degraded",
        "service": "Gokul's Astrological Insights API",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "name": "XALEN Ephemeris & Vedic Astrological Engine",
            "version": "0.6.0",
            "rust_core_available": engine_available,
            "error": error_msg,
        },
    }
