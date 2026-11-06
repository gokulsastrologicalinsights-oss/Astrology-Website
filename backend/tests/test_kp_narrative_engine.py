"""Unit and integration tests for Feature 2: Automated KP Predictive Narrative Engine."""

import io
from datetime import date, time as dt_time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.common import BirthInput
from app.schemas.kp_narrative import (
    KpNarrativeRequest,
    KpNarrativePdfRequest,
    SaveKpNarrativeRequest,
)
from app.services.kp_narrative_engine import (
    generate_kp_predictive_narrative_data,
    KpNarrativePdfGenerator,
    KpNarrativeRepository,
)

client = TestClient(app)


def test_kp_narrative_calculation_direct():
    """Tests generating narrative data directly through the engine service."""
    b_date = date(1990, 5, 15)
    b_time = dt_time(14, 30, 0)
    lat = 13.0827
    lon = 80.2707
    tz = "Asia/Kolkata"

    res = generate_kp_predictive_narrative_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=lat,
        longitude=lon,
        timezone_str=tz,
        person_name="Gokul Test",
        gender="male",
        target_date=date(2026, 11, 6),
        language="ta",
        months_ahead=24,
    )

    assert "report_id" in res
    assert res["report_id"].startswith("KPN-")
    assert res["person_details"]["name"] == "Gokul Test"
    assert res["person_details"]["lagna"] != ""
    assert res["person_details"]["moon_sign"] != ""

    # Check Section 1: Natal Event Promise
    np_data = res["natal_promise"]
    assert "overall_synthesis_en" in np_data
    assert "overall_synthesis_ta" in np_data
    assert len(np_data["items"]) == 6

    # Verify evaluated primary cusps: 1, 2, 5, 7, 10, 11
    cusps_evaluated = [it["cusp"] for it in np_data["items"]]
    assert cusps_evaluated == [1, 2, 5, 7, 10, 11]

    for it in np_data["items"]:
        assert it["verdict"] in ("strongly_promised", "delayed_fruition", "denied_or_caution")
        assert it["plain_narrative_en"] != ""
        assert it["plain_narrative_ta"] != ""
        assert it["practical_takeaway_en"] != ""
        assert it["practical_takeaway_ta"] != ""

    # Check Section 2: Running Dasha-Bhukti Analysis
    rd_data = res["running_dasha"]
    assert rd_data["mahadasha"]["lord"] != ""
    assert rd_data["bhukti"]["lord"] != ""
    assert rd_data["antara"]["lord"] != ""
    assert rd_data["career_impact_en"] != ""
    assert rd_data["career_impact_ta"] != ""
    assert rd_data["finance_impact_en"] != ""
    assert rd_data["relationship_impact_en"] != ""
    assert rd_data["health_impact_en"] != ""
    assert 0 <= rd_data["favorable_score"] <= 100

    # Check Section 3: Upcoming Milestone Windows
    mw_list = res["milestone_windows"]
    assert len(mw_list) >= 1
    for m in mw_list:
        assert m["domain"] in ("career", "finance", "matrimony")
        assert m["window_title_en"] != ""
        assert m["window_title_ta"] != ""
        assert len(m["action_plan_en"]) > 0

    # Check Section 4: Do's & Don'ts and Remedies
    rem_data = res["remedies"]
    assert len(rem_data["dos_en"]) > 0
    assert len(rem_data["donts_en"]) > 0
    assert rem_data["deity_prayer_en"] != ""
    assert rem_data["charity_action_en"] != ""
    assert rem_data["lucky_day_color_en"] != ""


def test_kp_narrative_pdf_generation_direct():
    """Tests generating PDF booklet directly from the calculated data."""
    b_date = date(1995, 8, 20)
    b_time = dt_time(9, 15, 0)
    res = generate_kp_predictive_narrative_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=13.0827,
        longitude=80.2707,
        person_name="Ananya",
        gender="female",
        language="ta",
    )

    pdf_gen = KpNarrativePdfGenerator(res, language="ta")
    pdf_bytes = pdf_gen.generate()

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b"%PDF")


def test_kp_narrative_api_endpoints():
    """Tests /api/v1/kp-narrative/generate, /pdf, /save, /saved, /saved/{id}, /delete."""
    payload = {
        "birth_input": {
            "birth_date": "1992-03-25",
            "birth_time": "18:45:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
        },
        "person_name": "Suresh Kumar",
        "gender": "male",
        "language": "bilingual",
        "months_ahead": 24,
    }

    # 1. Generate Narrative API
    response = client.post("/api/v1/kp-narrative/generate", json=payload)
    assert response.status_code == 200, response.text
    narrative_resp = response.json()
    assert narrative_resp["person_details"]["name"] == "Suresh Kumar"
    assert len(narrative_resp["natal_promise"]["items"]) == 6

    # 2. PDF API
    pdf_req = {
        **payload,
        "precalculated_data": narrative_resp,
    }
    pdf_response = client.post("/api/v1/kp-narrative/pdf", json=pdf_req)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert len(pdf_response.content) > 5000

    # 3. Save Narrative API
    save_req = {
        "title": "Suresh KP Narrative Analysis",
        "person_name": "Suresh Kumar",
        "birth_date": "1992-03-25",
        "birth_time": "18:45:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "gender": "male",
        "language": "ta",
        "report_data": narrative_resp,
    }
    save_response = client.post("/api/v1/kp-narrative/save", json=save_req)
    assert save_response.status_code == 200
    save_data = save_response.json()
    saved_id = save_data["id"]
    assert saved_id is not None

    # 4. List Saved Narratives
    list_response = client.get("/api/v1/kp-narrative/saved")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] >= 1
    found = any(item["id"] == saved_id for item in list_data["items"])
    assert found is True

    # 5. Get Saved Narrative by ID
    get_response = client.get(f"/api/v1/kp-narrative/saved/{saved_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == saved_id
    assert get_data["person_name"] == "Suresh Kumar"

    # 6. Delete Saved Narrative by ID
    del_response = client.delete(f"/api/v1/kp-narrative/saved/{saved_id}")
    assert del_response.status_code == 200
    assert del_response.json()["status"] == "success"

    # Verify deleted
    get_del = client.get(f"/api/v1/kp-narrative/saved/{saved_id}")
    assert get_del.status_code == 404
