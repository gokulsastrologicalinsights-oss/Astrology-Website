"""Unit & Integration Tests for Feature 3: Instant KP Horary / Prashna (1-249) Automated Event Predictor."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.kp_horary_prediction import (
    InstantHoraryPredictionRequest,
    OutcomeVerdict,
)
from app.services.kp_horary_prediction_service import (
    calculate_instant_horary_prediction,
    get_all_topics,
    resolve_topic,
)

client = TestClient(app)


def test_get_all_topics():
    """Verify that all standard horary query topics are available with required metadata."""
    topics = get_all_topics()
    assert len(topics) >= 10
    
    topic_ids = {t.id for t in topics}
    assert "visa" in topic_ids
    assert "job" in topic_ids
    assert "court_case" in topic_ids
    assert "marriage" in topic_ids
    assert "property" in topic_ids

    # Check topic fields
    visa_topic = next(t for t in topics if t.id == "visa")
    assert visa_topic.primary_cusp == 12
    assert 12 in visa_topic.supporting_houses
    assert 3 in visa_topic.supporting_houses
    assert visa_topic.name_ta != ""
    assert "விசா" in visa_topic.name_ta


def test_resolve_topic_keywords():
    """Verify keyword and alias resolution for freeform querent questions."""
    resolved_visa = resolve_topic("unknown", "Will I get this visa approval?")
    assert resolved_visa["id"] == "visa"
    assert resolved_visa["primary_cusp"] == 12

    resolved_job = resolve_topic("job_interview", "Will my job interview succeed?")
    assert resolved_job["id"] == "job"
    assert resolved_job["primary_cusp"] == 6

    resolved_court = resolve_topic("litigation", "Will this court case settle in my favor?")
    assert resolved_court["id"] == "court_case"
    assert resolved_court["primary_cusp"] == 6


def test_direct_service_visa_prediction():
    """Test direct service calculation for a visa query."""
    req = InstantHoraryPredictionRequest(
        horary_number=145,
        question_topic="visa",
        question_text="Will I get this visa?",
        question_date="2026-11-06",
        question_time="14:30:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_name="Chennai, India",
    )
    res = calculate_instant_horary_prediction(req)

    assert res.horary_number == 145
    assert res.primary_cusp == 12
    assert res.outcome in [OutcomeVerdict.YES, OutcomeVerdict.DELAYED, OutcomeVerdict.NO]
    assert res.confidence_score >= 50
    assert res.cusp_sub_lord != ""
    assert res.cusp_sub_lord_ta != ""
    assert len(res.ruling_planets) >= 3

    # Timing
    assert res.timing.dasha_mahadasha != ""
    assert res.timing.moon_transit_star != ""
    assert res.timing.moon_transit_start != ""
    assert res.timing.moon_transit_end != ""
    assert res.timing.summary_en != ""
    assert res.timing.summary_ta != ""

    # Astrological Explanation in English and Tamil
    assert res.explanation.summary_en != ""
    assert res.explanation.summary_ta != ""
    assert res.explanation.primary_cusp_analysis_en != ""
    assert res.explanation.primary_cusp_analysis_ta != ""
    assert "உப-அதிபதி" in res.explanation.primary_cusp_analysis_ta


def test_direct_service_job_prediction():
    """Test direct service calculation for a job interview query."""
    req = InstantHoraryPredictionRequest(
        horary_number=77,
        question_topic="job",
        question_text="Will my job interview succeed?",
        question_date="2026-11-06",
        question_time="10:15:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_name="Chennai, India",
    )
    res = calculate_instant_horary_prediction(req)

    assert res.horary_number == 77
    assert res.primary_cusp == 6
    assert res.outcome in [OutcomeVerdict.YES, OutcomeVerdict.DELAYED, OutcomeVerdict.NO]
    assert res.outcome_badge in ["success", "warning", "danger"]
    assert len(res.supporting_houses) > 0
    assert 6 in res.supporting_houses
    assert 10 in res.supporting_houses
    assert 11 in res.supporting_houses


def test_direct_service_court_case_prediction():
    """Test direct service calculation for a legal court case dispute."""
    req = InstantHoraryPredictionRequest(
        horary_number=204,
        question_topic="court_case",
        question_text="Will this court case settle in my favor?",
        question_date="2026-11-06",
        question_time="11:45:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_name="Chennai, India",
    )
    res = calculate_instant_horary_prediction(req)

    assert res.horary_number == 204
    assert res.primary_cusp == 6
    assert 1 in res.supporting_houses
    assert 6 in res.supporting_houses
    assert 11 in res.supporting_houses
    assert res.explanation.summary_ta != ""


def test_api_topics_endpoint():
    """Test GET /api/v1/horoscope/kp/horary-predict/topics."""
    resp = client.get("/api/v1/horoscope/kp/horary-predict/topics")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 10
    topics_by_id = {item["id"]: item for item in data}
    assert "visa" in topics_by_id
    assert "job" in topics_by_id
    assert "court_case" in topics_by_id


def test_api_predict_instant_horary():
    """Test POST /api/v1/horoscope/kp/horary-predict."""
    payload = {
        "horary_number": 19,
        "question_topic": "job",
        "question_text": "Will my job interview succeed?",
        "question_date": "2026-11-06",
        "question_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "location_name": "Chennai, India",
    }
    resp = client.post("/api/v1/horoscope/kp/horary-predict", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["horary_number"] == 19
    assert res["question_topic"] == "job"
    assert res["outcome"] in ["YES", "DELAYED", "NO"]
    assert "timing" in res
    assert "explanation" in res
    assert res["timing"]["moon_transit_star"] != ""
    assert res["explanation"]["primary_cusp_analysis_ta"] != ""


def test_api_validation_horary_number():
    """Verify validation: seed numbers outside 1..249 return 422."""
    payload = {
        "horary_number": 250,
        "question_topic": "job",
    }
    resp = client.post("/api/v1/horoscope/kp/horary-predict", json=payload)
    assert resp.status_code == 422

    payload["horary_number"] = 0
    resp = client.post("/api/v1/horoscope/kp/horary-predict", json=payload)
    assert resp.status_code == 422
