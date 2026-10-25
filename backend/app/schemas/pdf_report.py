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


# ==============================================================================
# Client-Facing Printable PDF Reports Schemas
# ==============================================================================

class ShodashvargaPdfReportRequest(BaseModel):
    """Request model for generating a comprehensive 16-divisional Shodashvarga Chart Book."""
    birth_input: Optional[BirthInput] = Field(
        None,
        description="Ad-hoc birth particulars. Required if saved_horoscope_id is omitted."
    )
    saved_horoscope_id: Optional[str] = Field(
        None,
        description="UUID of saved horoscope."
    )
    native_name: str = Field(
        "Native",
        description="Full name of native."
    )
    gender: str = Field(
        "male",
        description="Gender of native ('male' or 'female')."
    )
    language: str = Field(
        "en",
        description="'en' or 'ta'"
    )
    ayanamsa: int = Field(
        0,
        description="Ayanamsa ID (0=Lahiri)."
    )
    house_system: int = Field(
        0,
        description="House system ID (0=Whole Sign)."
    )


class MuhurtaCertificatePdfRequest(BaseModel):
    """Request model for generating an auspicious ceremonial Muhurta Selection Certificate."""
    occasion: str = Field(
        "Marriage",
        description="Type of occasion: 'Marriage' (Vivaha), 'House Warming' (Griha Pravesha), 'Business Launch', 'Vehicle Purchase', etc."
    )
    primary_person_name: str = Field(
        "Native",
        description="Name of native or Groom."
    )
    secondary_person_name: Optional[str] = Field(
        None,
        description="Name of Bride or Partner (optional)."
    )
    primary_gotra: Optional[str] = Field(None, description="Gotra of primary person.")
    secondary_gotra: Optional[str] = Field(None, description="Gotra of secondary person.")
    primary_nakshatra: Optional[str] = Field(None, description="Birth star of primary person.")
    secondary_nakshatra: Optional[str] = Field(None, description="Birth star of secondary person.")
    event_date: str = Field(
        ...,
        description="Selected date in YYYY-MM-DD format."
    )
    start_time: str = Field(
        ...,
        description="Muhurta start time in HH:MM format."
    )
    end_time: str = Field(
        ...,
        description="Muhurta end time in HH:MM format."
    )
    location_name: str = Field(
        "Chennai, Tamil Nadu",
        description="Name of location."
    )
    latitude: float = Field(
        13.0827,
        description="Latitude of location."
    )
    longitude: float = Field(
        80.2707,
        description="Longitude of location."
    )
    language: str = Field(
        "en",
        description="'en' or 'ta'"
    )
    astrologer_name: Optional[str] = Field(
        "Gokul's Astrological Insights",
        description="Certified Astrologer or Institute name."
    )
    special_notes: Optional[str] = Field(
        None,
        description="Custom blessing or instruction note."
    )


class PanchaPakshiPdfReportRequest(BaseModel):
    """Request model for generating an Agastya Pancha Pakshi 24-Hour Bio-Rhythm Chart PDF."""
    nakshatra: str = Field(
        ...,
        description="Native's birth star (e.g. 'Ashwini', 'Rohini')."
    )
    paksha: str = Field(
        ...,
        description="'shukla' (bright fortnight) or 'krishna' (dark fortnight)."
    )
    target_date: str = Field(
        ...,
        description="Date for which to compute the 24-hour bio-rhythm (YYYY-MM-DD)."
    )
    latitude: float = Field(
        13.0827,
        description="Latitude for local sunrise/sunset calculation."
    )
    longitude: float = Field(
        80.2707,
        description="Longitude for local sunrise/sunset calculation."
    )
    location_name: str = Field(
        "Chennai, Tamil Nadu",
        description="Location name."
    )
    native_name: str = Field(
        "Native",
        description="Full name of native."
    )
    language: str = Field(
        "en",
        description="'en' or 'ta'"
    )


class GemstoneRudrakshaPlaybookPdfRequest(BaseModel):
    """Request model for generating the Remedial Gemstone & Rudraksha Sanctification Playbook."""
    ascendant_sign: str = Field(
        ...,
        description="Ascendant sign (e.g. 'Leo', 'Cancer')."
    )
    native_name: str = Field(
        "Native",
        description="Full name of native."
    )
    body_weight_kg: float = Field(
        68.0,
        description="Native's body weight in kg for proportional Ratti/Carat calculations."
    )
    moon_sign: Optional[str] = Field(
        None,
        description="Moon sign (Rasi) if known."
    )
    running_mahadasha: Optional[str] = Field(
        None,
        description="Currently running Mahadasha planet."
    )
    running_bhukti: Optional[str] = Field(
        None,
        description="Currently running Bhukti/Antardasha planet."
    )
    has_kuja_dosha: bool = Field(
        False,
        description="Whether native has Kuja/Manglik dosha."
    )
    has_sade_sati: bool = Field(
        False,
        description="Whether native has active Sade Sati."
    )
    has_kaal_sarp: bool = Field(
        False,
        description="Whether native has Kaal Sarp dosha."
    )
    language: str = Field(
        "en",
        description="'en' or 'ta'"
    )

