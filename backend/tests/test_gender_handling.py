from datetime import date
from types import SimpleNamespace
import pytest
from app.utils.gender import normalize_gender
from app.services.pdf_report_engine.data_builder import build_report_data


def test_normalize_gender_valid():
    assert normalize_gender("male") == "male"
    assert normalize_gender("FEMALE") == "female"
    assert normalize_gender("  Female  ") == "female"


def test_normalize_gender_missing():
    assert normalize_gender(None) is None
    assert normalize_gender("") is None
    assert normalize_gender("   ") is None


def test_normalize_gender_invalid():
    with pytest.raises(ValueError):
        normalize_gender("unknown_xyz")
    with pytest.raises(ValueError):
        normalize_gender("other")


def test_build_report_data_genders():
    bi = SimpleNamespace(
        birth_date=date(1990, 5, 15),
        birth_time="10:30:00",
        latitude=13.0827,
        longitude=80.2707,
        timezone="Asia/Kolkata",
    )
    for g, expected in [("male", "male"), ("female", "female"), (None, "Not Specified")]:
        data = build_report_data(
            birth_input=bi,
            native_name="Test Native",
            gender=g,
            ayanamsa_id=0,
            house_system_id=2,
            language="en",
            is_verified=True,
        )
        assert data.gender == expected
