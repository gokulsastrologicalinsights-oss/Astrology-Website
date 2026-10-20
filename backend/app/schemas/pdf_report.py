"""Pydantic schemas for PDF Horoscope Report endpoints."""

from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput


class HoroscopePdfReportRequest(BaseModel):
    """Request model for generating a branded English/Tamil PDF horoscope report."""
    birth_input: Optional[BirthInput] = Field(
        None,
        description="Ad-hoc birth particulars. Required if saved_horoscope_id is not provided."
    )
    saved_horoscope_id: Optional[str] = Field(
        None,
        description="UUID of a previously saved horoscope. Requires authentication and ownership."
    )
    native_name: Optional[str] = Field(
        "Native",
        description="Full name of the native for personalized branding in the report."
    )
    gender: Optional[str] = Field(
        "male",
        description="Gender of native ('male' or 'female') for gender-specific interpretations."
    )
    language: str = Field(
        "en",
        description="Report language: 'en' for English, 'ta' for Tamil."
    )
    ayanamsa: int = Field(
        0,
        description="Ayanamsa ID (0=Lahiri Chitra Paksha, 1=KP, 2=Raman, etc.). Default 0."
    )
    house_system: int = Field(
        0,
        description="House system ID (0=Whole Sign, 2=Placidus/KP). Default 0."
    )
