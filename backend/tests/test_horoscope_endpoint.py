"""Automated tests for Horoscope endpoint (POST /api/v1/horoscope/calculate)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 0,
    "house_system": 2,
    "include_panchang": True,
    "include_outer_planets": True,
}


def test_horoscope_valid_calculation():
    response = client.post("/api/v1/horoscope/calculate", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    # Metadata
    meta = data["metadata"]
    assert meta["engine"] == "XALEN 0.6.0 (Rust)"
    assert meta["local_timezone"] == "Asia/Kolkata"
    assert meta["utc_offset_hours"] == 5.5
    assert meta["ayanamsa_id"] == 0
    assert meta["ayanamsa_name"] == "Lahiri"
    assert 23.0 < meta["ayanamsa_deg"] < 25.0

    # Ascendant & Midheaven
    asc = data["ascendant"]
    assert 0.0 <= asc["degree"] < 360.0
    assert 1 <= asc["sign_index"] <= 12
    assert asc["sign_name"] == "Virgo"
    assert asc["sign_name_tamil"] == "கன்னி"
    assert asc["nakshatra"]["name"] == "Uttara Phalguni"

    # Midheaven
    mc = data["midheaven"]
    assert 0.0 <= mc["degree"] < 360.0

    # Planets (12 total: 7 grahas + Rahu + Ketu + Uranus + Neptune + Pluto)
    planets = data["planets"]
    assert len(planets) == 12
    planet_names = [p["name"] for p in planets]
    assert "Sun" in planet_names
    assert "Moon" in planet_names
    assert "Mars" in planet_names
    assert "Jupiter" in planet_names
    assert "Rahu" in planet_names
    assert "Ketu" in planet_names

    # Check Sun attributes
    sun = next(p for p in planets if p["name"] == "Sun")
    assert sun["sign_name"] == "Taurus"
    assert sun["sign_name_tamil"] == "ரிஷபம்"
    assert 0.0 <= sun["degree_in_sign"] < 30.0
    assert sun["nakshatra"]["name"] == "Krittika"

    # Houses (12 total)
    houses = data["houses"]
    assert len(houses) == 12
    for idx, h in enumerate(houses, start=1):
        assert h["house_number"] == idx
        assert 0.0 <= h["cusp_degree"] < 360.0
        assert 1 <= h["sign_index"] <= 12

    # Panchang
    panchang = data["panchang"]
    assert panchang is not None
    assert panchang["tithi"]["paksha"] in ("Shukla", "Krishna")
    assert panchang["nakshatra"] == "Uttara Ashadha"
    assert panchang["vara"] == "Mangalavara"


def test_horoscope_different_ayanamsas():
    # Base Lahiri (id 0)
    res_lahiri = client.post("/api/v1/horoscope/calculate", json=VALID_PAYLOAD)
    assert res_lahiri.status_code == 200
    lahiri_asc = res_lahiri.json()["ascendant"]["degree"]
    lahiri_aya = res_lahiri.json()["metadata"]["ayanamsa_deg"]

    # KP Ayanamsa (id 1)
    payload_kp = {**VALID_PAYLOAD, "ayanamsa": 1}
    res_kp = client.post("/api/v1/horoscope/calculate", json=payload_kp)
    assert res_kp.status_code == 200
    assert res_kp.json()["metadata"]["ayanamsa_name"] == "KP"
    kp_asc = res_kp.json()["ascendant"]["degree"]
    assert kp_asc != lahiri_asc

    # Raman Ayanamsa (id 2)
    payload_raman = {**VALID_PAYLOAD, "ayanamsa": 2}
    res_raman = client.post("/api/v1/horoscope/calculate", json=payload_raman)
    assert res_raman.status_code == 200
    assert res_raman.json()["metadata"]["ayanamsa_name"] == "Raman"
    raman_asc = res_raman.json()["ascendant"]["degree"]
    raman_aya = res_raman.json()["metadata"]["ayanamsa_deg"]
    assert raman_asc != lahiri_asc
    # Difference in ascendant must match difference in ayanamsa
    assert abs((raman_asc - lahiri_asc) - (lahiri_aya - raman_aya)) < 0.01

    # Fagan-Bradley (id 3)
    payload_fb = {**VALID_PAYLOAD, "ayanamsa": 3}
    res_fb = client.post("/api/v1/horoscope/calculate", json=payload_fb)
    assert res_fb.status_code == 200
    assert res_fb.json()["metadata"]["ayanamsa_name"] == "Fagan-Bradley"
    fb_asc = res_fb.json()["ascendant"]["degree"]
    assert fb_asc != lahiri_asc


def test_horoscope_different_house_systems():
    res_plac = client.post("/api/v1/horoscope/calculate", json=VALID_PAYLOAD)
    assert res_plac.status_code == 200
    plac_cusps = [h["cusp_degree"] for h in res_plac.json()["houses"]]

    # Whole Sign (id 0)
    payload_ws = {**VALID_PAYLOAD, "house_system": 0}
    res_ws = client.post("/api/v1/horoscope/calculate", json=payload_ws)
    assert res_ws.status_code == 200
    assert res_ws.json()["metadata"]["house_system_name"] == "WholeSign"
    ws_cusps = [h["cusp_degree"] for h in res_ws.json()["houses"]]
    assert ws_cusps != plac_cusps

    # Equal House (id 1)
    payload_eq = {**VALID_PAYLOAD, "house_system": 1}
    res_eq = client.post("/api/v1/horoscope/calculate", json=payload_eq)
    assert res_eq.status_code == 200
    assert res_eq.json()["metadata"]["house_system_name"] == "Equal"
    eq_cusps = [h["cusp_degree"] for h in res_eq.json()["houses"]]
    assert eq_cusps != plac_cusps

    # Sripati / Porphyry (id 10)
    payload_sripati = {**VALID_PAYLOAD, "house_system": 10}
    res_sripati = client.post("/api/v1/horoscope/calculate", json=payload_sripati)
    assert res_sripati.status_code == 200
    assert res_sripati.json()["metadata"]["house_system_name"] == "Sripati"
    sripati_cusps = [h["cusp_degree"] for h in res_sripati.json()["houses"]]
    assert sripati_cusps != plac_cusps


def test_horoscope_explicit_offset_timezone():
    payload_offset = {**VALID_PAYLOAD, "timezone": "+05:30"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_offset)
    assert res.status_code == 200
    data = res.json()
    assert data["metadata"]["utc_offset_hours"] == 5.5


def test_horoscope_invalid_latitude():
    # Latitude > 90
    payload_bad_lat = {**VALID_PAYLOAD, "latitude": 95.0}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_lat)
    assert res.status_code == 422
    assert "Input Validation Error" in res.json()["error"]

    # Latitude < -90
    payload_bad_lat_neg = {**VALID_PAYLOAD, "latitude": -91.5}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_lat_neg)
    assert res.status_code == 422


def test_horoscope_invalid_longitude():
    # Longitude > 180
    payload_bad_lon = {**VALID_PAYLOAD, "longitude": 185.0}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_lon)
    assert res.status_code == 422

    # Longitude < -180
    payload_bad_lon_neg = {**VALID_PAYLOAD, "longitude": -190.0}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_lon_neg)
    assert res.status_code == 422


def test_horoscope_invalid_date():
    # Nonexistent date: Feb 30
    payload_bad_date = {**VALID_PAYLOAD, "birth_date": "1990-02-30"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_date)
    assert res.status_code == 422

    # Month 13
    payload_bad_month = {**VALID_PAYLOAD, "birth_date": "1990-13-15"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_month)
    assert res.status_code == 422


def test_horoscope_invalid_time():
    # Hour 25
    payload_bad_hour = {**VALID_PAYLOAD, "birth_time": "25:00:00"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_hour)
    assert res.status_code == 422

    # Minute 60
    payload_bad_minute = {**VALID_PAYLOAD, "birth_time": "14:60:00"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_minute)
    assert res.status_code == 422


def test_horoscope_invalid_timezone():
    # Bogus timezone
    payload_bad_tz = {**VALID_PAYLOAD, "timezone": "Atlantis/City"}
    res = client.post("/api/v1/horoscope/calculate", json=payload_bad_tz)
    assert res.status_code == 422
    assert "Unknown timezone" in res.json()["detail"]
