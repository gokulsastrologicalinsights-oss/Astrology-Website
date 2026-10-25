"""Pydantic schemas for PDF Horoscope & KP Report endpoints."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import BirthInput
from app.schemas.kp import HoraryKpRequest


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


class KpPdfReportRequest(BaseModel):
    """Request model for generating a dedicated 6-page branded English/Tamil KP PDF report."""
    chart_type: str = Field(
        "natal",
        description="'natal' or 'horary'"
    )
    birth_input: Optional[BirthInput] = Field(
        None,
        description="Ad-hoc birth particulars for natal KP report."
    )
    horary_input: Optional[HoraryKpRequest] = Field(
        None,
        description="Ad-hoc horary query particulars (1-249)."
    )
    saved_chart_id: Optional[str] = Field(
        None,
        description="UUID of a previously saved KP chart (natal or horary)."
    )
    native_name: Optional[str] = Field(
        "Native",
        description="Full name of the native / querent for personalized branding."
    )
    gender: Optional[str] = Field(
        "male",
        description="Gender ('male' or 'female')."
    )
    language: str = Field(
        "en",
        description="Report language: 'en' for English, 'ta' for Tamil."
    )
    ayanamsa: int = Field(
        1,
        description="Ayanamsa ID (1=KP Krishnamurti Modern VP291, 0=Lahiri). Default 1."
    )
    house_system: int = Field(
        2,
        description="House system ID (2=Placidus semi-arc). Default 2."
    )
