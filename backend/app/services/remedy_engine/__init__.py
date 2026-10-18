"""Remedy Engine module for Gokul's Astrological Insights.

Provides clean-room, shastra-validated remedy knowledge base,
bilingual validation, Kaveri Delta Navagraha temple directory,
and classical Vedic astrological eligibility safeguards.
"""

from app.services.remedy_engine.repository import remedy_repository
from app.services.remedy_engine.taxonomy import PROBLEM_TAXONOMY_REGISTRY
from app.services.remedy_engine.validation import RemedyValidator
from app.services.remedy_engine.eligibility import RemedyEligibilityEngine
from app.services.remedy_engine.analysis import (
    generate_remedy_analysis,
    extract_chart_context,
    diagnose_chart_factors,
    rank_and_retrieve_remedies,
    evaluate_neecha_bhanga,
)

__all__ = [
    "remedy_repository",
    "PROBLEM_TAXONOMY_REGISTRY",
    "RemedyValidator",
    "RemedyEligibilityEngine",
    "generate_remedy_analysis",
    "extract_chart_context",
    "diagnose_chart_factors",
    "rank_and_retrieve_remedies",
    "evaluate_neecha_bhanga",
]
