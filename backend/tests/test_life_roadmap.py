"""Unit and integration tests for Feature 1: Automated Multi-Year Life Timeline Predictor (Life Roadmap)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_life_roadmap_domains_endpoint():
    """Verify domains endpoint returns 5 core domains with metadata and registered events."""
    resp = client.get("/api/v1/kp-prediction/life-roadmap/domains")
    assert resp.status_code == 200
    domains = resp.json()
    assert len(domains) == 5

    domain_ids = {d["id"] for d in domains}
    assert domain_ids == {"career", "relationships", "finance", "travel", "health"}

    career = next(d for d in domains if d["id"] == "career")
    assert "Career & Status" in career["name"]
    assert "Promotion" in career["events"]
    assert "Job" in career["events"]

    rel = next(d for d in domains if d["id"] == "relationships")
    assert "Marriage" in rel["events"]
    assert "Love affair" in rel["events"]

    fin = next(d for d in domains if d["id"] == "finance")
    assert "Financial gain" in fin["events"]
    assert "Property purchase" in fin["events"]

    travel = next(d for d in domains if d["id"] == "travel")
    assert "Foreign travel" in travel["events"]
    assert "Settlement abroad" in travel["events"]

    health = next(d for d in domains if d["id"] == "health")
    assert "Illness" in health["events"]
    assert "Accident / Surgery" in health["events"]


def test_life_roadmap_direct_birth_input_3_years():
    """Test generating a 3-year life roadmap using direct birth details."""
    payload = {
        "birth_date": "1995-10-25",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "customer_name": "Test Native",
        "horizon_years": 3,
        "start_date": "2026-11-06",
    }
    resp = client.post("/api/v1/kp-prediction/life-roadmap", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["customer_name"] == "Test Native"
    assert data["lagna"] == "Aquarius"
    assert data["moon_sign"] == "Libra"
    assert "Vishakha" in data["nakshatra"]
    assert data["horizon_years"] == 3
    assert data["start_date"] == "2026-11-06"

    # Scorecards for all 5 domains
    scorecards = data["domain_scorecards"]
    assert len(scorecards) == 5
    for sc in scorecards:
        assert sc["domain_id"] in {"career", "relationships", "finance", "travel", "health"}
        assert sc["summary_label"]
        assert sc["summary_text"]

    # Periods
    periods = data["chronological_periods"]
    assert len(periods) > 5  # typically 12-25 Antara periods in 3 years
    for p in periods:
        assert p["period_key"]
        assert p["mahadasha_lord"]
        assert p["bhukti_lord"]
        assert p["antara_lord"]
        assert p["start_date"]
        assert p["end_date"]
        assert p["duration_days"] > 0
        assert p["primary_status"] in ("green", "orange", "red", "neutral")
        assert len(p["all_milestones"]) > 0

    # Summary
    summary = data["overall_summary"]
    assert summary["total_dba_periods"] == len(periods)
    assert summary["high_probability_count"] >= 0
    assert summary["executive_verdict"]

    # Markdown report generated
    assert len(data["executive_roadmap_markdown"]) > 200
    assert "Multi-Year Life Roadmap" in data["executive_roadmap_markdown"]


def test_life_roadmap_horizon_years_1_and_5():
    """Verify 1-year and 5-year horizons scale appropriately."""
    base = {
        "birth_date": "1990-05-15",
        "birth_time": "08:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "start_date": "2026-11-06",
    }

    # 1 Year
    r1 = client.post("/api/v1/kp-prediction/life-roadmap", json={**base, "horizon_years": 1})
    assert r1.status_code == 200
    d1 = r1.json()
    p1_count = len(d1["chronological_periods"])

    # 5 Years
    r5 = client.post("/api/v1/kp-prediction/life-roadmap", json={**base, "horizon_years": 5})
    assert r5.status_code == 200
    d5 = r5.json()
    p5_count = len(d5["chronological_periods"])

    assert p5_count > p1_count


def test_life_roadmap_domain_filter():
    """Test filtering roadmap to a specific domain (e.g. career only)."""
    payload = {
        "birth_date": "1995-10-25",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "horizon_years": 3,
        "start_date": "2026-11-06",
        "filter_domain": "career",
    }
    resp = client.post("/api/v1/kp-prediction/life-roadmap", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    for p in data["chronological_periods"]:
        for m in p["all_milestones"]:
            assert m["domain_id"] == "career"


def test_life_roadmap_missing_birth_details_fails():
    """Missing birth details without horoscope_id should return 422."""
    payload = {
        "horizon_years": 3,
    }
    resp = client.post("/api/v1/kp-prediction/life-roadmap", json=payload)
    assert resp.status_code == 422
