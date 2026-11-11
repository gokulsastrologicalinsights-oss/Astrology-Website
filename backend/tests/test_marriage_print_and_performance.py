"""Regression tests for Marriage Compatibility performance, Nakshatra indexing,
saved-horoscope null metadata safety, and 5-page reference print data builder.
"""

from __future__ import annotations
import time
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.routers.marriage_compatibility import get_optional_current_user
from app.schemas.marriage import MarriageCompatibilityRequest, MarriagePartnerInput
from app.services.marriage_engine.service import run_marriage_compatibility_analysis

client = TestClient(app)


def test_marriage_analysis_fast_and_complete_print_data():
    """Verify analysis runs swiftly (<2s) without depth=5 OOM explosion and populates print_report_data."""
    req = MarriageCompatibilityRequest(
        groom=MarriagePartnerInput(
            name="Pradyumraj",
            gender="male",
            birth_date="1999-11-12",
            birth_time="04:15:00",
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        bride=MarriagePartnerInput(
            name="S.Krithika",
            gender="female",
            birth_date="2005-08-19",
            birth_time="14:15:00",
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        rule_system="all",
        ayanamsa_id=0,
        house_system_id=0,
        include_kp=True,
        include_timing=True,
    )

    t0 = time.perf_counter()
    res = run_marriage_compatibility_analysis(req)
    elapsed = time.perf_counter() - t0

    assert elapsed < 2.5, f"Marriage analysis took too long ({elapsed:.2f}s)"

    # Verify 0-indexed Tamil nakshatra mapping fix (Mula -> மூலம், Dhanishta -> அவிட்டம்)
    assert res.groom_profile.moon_nakshatra == "Mula"
    assert res.groom_profile.moon_nakshatra_tamil == "மூலம்"
    assert res.bride_profile.moon_nakshatra == "Dhanishta"
    assert res.bride_profile.moon_nakshatra_tamil == "அவிட்டம்"

    # Verify print_report_data structure for all 5 pages
    prd = res.print_report_data
    assert isinstance(prd, dict)

    dosha_audit = prd.get("dosha_audit")
    assert isinstance(dosha_audit, list) and len(dosha_audit) == 10
    expected_ids = {
        "kuja_dosha",
        "naga_dosha",
        "putra_dosha",
        "panchanai_dosha",
        "surya_dosha",
        "shukra_dosha",
        "seventh_house_dosha",
        "seventh_lord_dosha",
        "malefic_conjunctions",
        "vadha_vainashika",
    }
    assert {row["id"] for row in dosha_audit} == expected_ids

    seq = prd.get("dasa_bhukti_sequence")
    assert len(seq["groom_mahadashas"]) == 9
    assert len(seq["bride_mahadashas"]) == 9
    assert isinstance(seq["transitions"], list) and len(seq["transitions"]) > 0

    sandhi = prd.get("dasa_sandhi")
    assert sandhi["has_sandhi"] is True
    assert "தசா சந்தி" in sandhi["summary_ta"]

    pa = prd.get("planetary_analysis")
    assert len(pa["harmonious_connections"]) >= 1
    assert len(pa["incompatible_combinations"]) >= 1

    verdict = prd.get("sage_verdict")
    assert "அஷ்டகூட மதிப்பெண்" in verdict["summary_ta"]


def test_ashwini_zero_index_tamil_nakshatra():
    """Verify index 0 (Ashwini) maps to அசுவினி instead of empty string."""
    req = MarriageCompatibilityRequest(
        groom=MarriagePartnerInput(
            name="TestAshwini",
            gender="male",
            birth_date="1995-04-02",
            birth_time="08:00:00",
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
        bride=MarriagePartnerInput(
            name="TestRevati",
            gender="female",
            birth_date="1997-03-10",
            birth_time="09:00:00",
            timezone="Asia/Kolkata",
            latitude=13.0827,
            longitude=80.2707,
        ),
    )
    res = run_marriage_compatibility_analysis(req)
    assert res.groom_profile.moon_nakshatra == "Ashwini"
    assert res.groom_profile.moon_nakshatra_tamil == "அசுவினி"


def test_saved_horoscope_null_metadata_recomputation_safe():
    """Verify saved horoscope recomputation handles None timezone/ayanamsa_id/house_system_id without 500."""
    mock_user = {"id": "11111111-1111-1111-1111-111111111111", "role": "authenticated"}
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    saved_row = {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "user_id": mock_user["id"],
        "person_name": "SavedGroom",
        "birth_date": "1992-04-14",
        "birth_time": "05:30:00",
        "timezone": None,
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa_id": None,
        "house_system_id": None,
        "calculation_result": {},
    }

    mock_supabase = MagicMock()
    with patch("app.services.marriage_engine.service.get_supabase_client", return_value=mock_supabase), patch(
        "app.services.horoscope_cache.get_cached_saved_horoscope",
        return_value=saved_row,
    ):
        resp = client.post(
            "/api/v1/marriage-compatibility/analyze",
            json={
                "groom": {"saved_horoscope_id": saved_row["id"], "name": "SavedGroom"},
                "bride": {
                    "name": "Bride",
                    "gender": "female",
                    "birth_date": "1994-08-20",
                    "birth_time": "14:15:00",
                    "timezone": "Asia/Kolkata",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                },
            },
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["groom_profile"]["name"] == "SavedGroom"
        assert data["print_report_data"] is not None

    app.dependency_overrides.pop(get_optional_current_user, None)
