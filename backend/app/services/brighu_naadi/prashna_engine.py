"""Brighu Prashna Nadi Oracle Engine.

Evaluates R. G. Rao's "Brighu Prashna Nadi" (107 predictions)
Formula: 107 - Completed Age = Remainder Prediction Number.
"""

from datetime import date, datetime
from typing import Optional
from app.schemas.brighu_naadi import BrighuPrashnaRequest, BrighuPrashnaResponse
from app.services.brighu_naadi.prashna_registry import (
    PRASHNA_PREDICTIONS,
    GURU_MANTRA,
    get_fallback_prediction,
)


def calculate_completed_age(birth_date_str: str, query_date_str: Optional[str] = None) -> int:
    """Calculate completed integer years of age between birth_date and query_date."""
    b_date = datetime.strptime(birth_date_str.strip(), "%Y-%m-%d").date()
    if query_date_str:
        q_date = datetime.strptime(query_date_str.strip(), "%Y-%m-%d").date()
    else:
        q_date = date.today()

    years = q_date.year - b_date.year
    if (q_date.month, q_date.day) < (b_date.month, b_date.day):
        years -= 1
    return max(0, years)


def evaluate_brighu_prashna(request: BrighuPrashnaRequest) -> BrighuPrashnaResponse:
    """Calculates the Brighu Prashna Nadi prophecy for the given querent."""
    # 1. Determine completed age
    if request.birth_date:
        completed_age = calculate_completed_age(request.birth_date, request.query_date)
    elif request.completed_age is not None:
        completed_age = max(0, int(request.completed_age))
    else:
        completed_age = 30  # Default baseline if omitted

    # 2. Formula from Book (pp. 1-2):
    # "If a query pertains to a person who has not yet completed one year of age,
    # refer to page 107. Otherwise, subtract completed number of years from 107."
    if completed_age == 0:
        prediction_num = 107
        formula = "Completed age < 1 year => Remainder 107 (Page 107)"
    else:
        rem = 107 - completed_age
        prediction_num = max(0, min(107, rem))
        formula = f"107 - {completed_age} (Completed Age) = {prediction_num}"

    # 3. Retrieve prediction from registry
    pred_data = PRASHNA_PREDICTIONS.get(prediction_num)
    if not pred_data:
        pred_data = get_fallback_prediction(prediction_num)

    sub_key = None
    if request.query_category and request.query_category.lower() != "general":
        sub_key = f"{prediction_num}_{request.query_category.lower()}"

    return BrighuPrashnaResponse(
        book_title="Brighu Prashna Nadi",
        author="R. G. Rao (Sagar Publications, 1994)",
        completed_age=completed_age,
        formula_applied=formula,
        prediction_number=prediction_num,
        sub_category_key=sub_key,
        guru_mantra=GURU_MANTRA,
        sanskrit_sloka=pred_data.get("sanskrit_sloka"),
        yoga_name_en=pred_data["yoga_name_en"],
        yoga_name_ta=pred_data["yoga_name_ta"],
        core_prophecy_en=pred_data["core_prophecy_en"],
        core_prophecy_ta=pred_data["core_prophecy_ta"],
        career_and_finance_en=pred_data["career_and_finance_en"],
        career_and_finance_ta=pred_data["career_and_finance_ta"],
        family_and_relationships_en=pred_data["family_and_relationships_en"],
        family_and_relationships_ta=pred_data["family_and_relationships_ta"],
        health_and_cautions_en=pred_data["health_and_cautions_en"],
        health_and_cautions_ta=pred_data["health_and_cautions_ta"],
        past_karma_cause_en=pred_data.get("past_karma_cause_en"),
        past_karma_cause_ta=pred_data.get("past_karma_cause_ta"),
        prescribed_remedy_en=pred_data["prescribed_remedy_en"],
        prescribed_remedy_ta=pred_data["prescribed_remedy_ta"],
        relief_timeline_en=pred_data["relief_timeline_en"],
        relief_timeline_ta=pred_data["relief_timeline_ta"],
    )
