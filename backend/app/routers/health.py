"""Health check endpoint."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter
import xalen

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Verify backend service availability."""
    try:
        # Perform server-side diagnostic check on astronomical core (JD for J2000.0)
        jd_check = xalen.julian_day(2000, 1, 1, 12.0)
        core_available = abs(jd_check - 2451545.0) < 1e-5
    except Exception as exc:
        core_available = False
        logger.error("Astronomical calculation core check failed: %s", exc, exc_info=True)
    else:
        if not core_available:
            logger.warning("Astronomical calculation core returned unexpected Julian Day value")

    return {
        "status": "healthy" if core_available else "degraded",
        "service": "Gokul's Astrological Insights API",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

