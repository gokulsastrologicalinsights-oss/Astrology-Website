"""Unified Classical Dosha Engine package.

Exposes comprehensive classical Vedic dosha evaluations:
- Kuja (Manglik) Dosha (from Lagna, Moon, Venus)
- Kaal Sarp Dosha (Full, Partial, Absent with 12 canonical subtypes)
- Sadesati & Saturn Transit (Rising, Peak, Setting, Kantaka, Ashtama with Ashtakavarga bindus)
- Additional Classical Doshas (Pitru, Guru Chandal, Shrapit, Grahan)
"""

from app.services.dosha_engine.models import (
    DoshaChartContext,
    DoshaPlanet,
    SEVEN_GRAHAS,
    NINE_GRAHAS,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)
from app.services.dosha_engine.kuja_dosha import evaluate_kuja_dosha
from app.services.dosha_engine.kaal_sarp import evaluate_kaal_sarp_dosha, KAAL_SARP_SUBTYPES
from app.services.dosha_engine.sadesati import evaluate_sadesati, compute_transit_saturn
from app.services.dosha_engine.additional_doshas import (
    evaluate_additional_doshas,
    evaluate_pitru_dosha,
    evaluate_guru_chandal_dosha,
    evaluate_shrapit_dosha,
    evaluate_grahan_dosha,
)
from app.services.dosha_engine.engine import calculate_unified_doshas

__all__ = [
    "DoshaChartContext",
    "DoshaPlanet",
    "SEVEN_GRAHAS",
    "NINE_GRAHAS",
    "SIGN_NAMES_EN",
    "SIGN_NAMES_TA",
    "evaluate_kuja_dosha",
    "evaluate_kaal_sarp_dosha",
    "KAAL_SARP_SUBTYPES",
    "evaluate_sadesati",
    "compute_transit_saturn",
    "evaluate_additional_doshas",
    "evaluate_pitru_dosha",
    "evaluate_guru_chandal_dosha",
    "evaluate_shrapit_dosha",
    "evaluate_grahan_dosha",
    "calculate_unified_doshas",
]
