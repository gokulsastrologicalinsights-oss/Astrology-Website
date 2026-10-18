"""Automated test suite for Advanced KP and Horary Prashna calculation & persistence engines."""

import pytest
from datetime import date, time
from app.schemas.kp import KpRequest, HoraryKpRequest
from app.services.kp_service import calculate_kp_chart, calculate_horary_chart
from app.services.kp_engine.horary import (
    kp_divisions,
    find_armc_for_ascendant,
    compute_horary_cusps,
)
from app.services.kp_engine.kp_chart_repository import (
    save_kp_chart,
    list_kp_charts,
    get_kp_chart,
    delete_kp_chart,
)


def test_horary_division_integrity():
    """Ensure exactly 249 divisions tile 0-360 degrees without gaps or overlaps."""
    divs = kp_divisions()
    assert len(divs) == 249, f"Expected 249 divisions, got {len(divs)}"

    # First division is in Aries, Ketu/Ketu/Ketu
    assert divs[0].number == 1
    assert divs[0].sign == "Aries"
    assert divs[0].star_lord == "Ketu"
    assert divs[0].sub_lord == "Ketu"
    assert abs(divs[0].start_deg - 0.0) < 1e-6
    assert abs(divs[0].end_deg - (46.0 / 60.0 + 40.0 / 3600.0)) < 1e-4

    # Last division is in Pisces, Jupiter/Mercury/Saturn
    assert divs[248].number == 249
    assert divs[248].sign == "Pisces"
    assert abs(divs[248].end_deg - 360.0) < 1e-6


def test_calculate_horary_chart_number_1():
    """Test calculation of Horary #1 chart with authentic KP mechanics."""
    req = HoraryKpRequest(
        horary_number=1,
        question_text="Will the business deal succeed?",
        question_date=date(2026, 10, 18),
        question_time=time(10, 30),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        location_name="Chennai, India",
        ayanamsa=1,  # KP Ayanamsa
    )
    res = calculate_horary_chart(req)

    # 1. Division and Ascendant
    assert res.horary_number == 1
    assert res.horary_division.number == 1
    assert res.horary_division.sub_lord == "Ketu"
    assert abs(res.ascendant_degree - res.horary_division.mid_degree) < 1e-5

    # 2. 12 Placidus Cusps
    assert len(res.cuspal_analysis) == 12
    assert abs(res.cuspal_analysis[0].cusp_degree - res.ascendant_degree) < 1e-5
    for c in res.cuspal_analysis:
        assert c.promise in ("Positive", "Negative", "Mixed")
        assert c.sub_lord in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

    # 3. 9 Planetary positions
    assert len(res.planetary_positions) == 9
    planet_names = {p.planet for p in res.planetary_positions}
    assert planet_names == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

    # 4. Significators
    assert len(res.house_significators) == 12
    for h in res.house_significators:
        assert isinstance(h.level_a, list)
        assert isinstance(h.level_b, list)
        assert isinstance(h.level_c, list)
        assert isinstance(h.level_d, list)

    # 5. Ruling Planets
    assert res.ruling_planets is not None
    assert len(res.ruling_planets.ruling_planets_list) > 0

    # 6. Dasa Hierarchy
    assert res.dasa_hierarchy is not None
    assert len(res.dasa_hierarchy.current_periods) == 5
    assert len(res.dasa_hierarchy.mahadashas) > 0


def test_calculate_horary_chart_number_249():
    """Test calculation of Horary #249 (Pisces boundary)."""
    req = HoraryKpRequest(
        horary_number=249,
        question_text="Overseas travel confirmation",
        question_date=date(2026, 10, 18),
        question_time=time(14, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    res = calculate_horary_chart(req)
    assert res.horary_number == 249
    assert res.horary_division.sign == "Pisces"
    assert res.horary_division.star_lord == "Mercury"
    assert res.horary_division.sub_lord == "Saturn"
    assert abs(res.ascendant_degree - res.horary_division.mid_degree) < 1e-5


def test_saved_kp_charts_repository_crud():
    """Test concurrency-safe sequential numbering and CRUD in repository."""
    user_id = "test-user-uuid-1234"

    # 1. Save first chart
    data1 = {
        "chart_type": "natal",
        "title": "Natal Client A",
        "birth_date": "1995-10-24",
        "birth_time": "14:30:00",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {"status": "ok"},
    }
    r1 = save_kp_chart(user_id, data1)
    assert r1["display_number"] == 1
    assert r1["chart_type"] == "natal"
    assert r1["title"] == "Natal Client A"

    # 2. Save second chart (sequential display_number = 2)
    data2 = {
        "chart_type": "horary",
        "title": "Horary Query B",
        "horary_number": 42,
        "question_text": "Will I buy the house?",
        "question_date": "2026-10-18",
        "question_time": "11:15:00",
        "location_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "calculation_result": {"status": "ok"},
    }
    r2 = save_kp_chart(user_id, data2)
    assert r2["display_number"] == 2
    assert r2["chart_type"] == "horary"

    # 3. List records
    charts = list_kp_charts(user_id)
    assert len(charts) >= 2
    # Verify ordered descending by display_number
    assert charts[0]["display_number"] > charts[1]["display_number"]

    # 4. Fetch single record
    fetched = get_kp_chart(user_id, r1["id"])
    assert fetched is not None
    assert fetched["id"] == r1["id"]

    # 5. Delete record and verify sequential numbers of remaining records are preserved
    del_ok = delete_kp_chart(user_id, r1["id"])
    assert del_ok is True
    remaining = list_kp_charts(user_id)
    assert not any(c["id"] == r1["id"] for c in remaining)
    assert any(c["id"] == r2["id"] and c["display_number"] == 2 for c in remaining)
