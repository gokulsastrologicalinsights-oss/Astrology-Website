"""Exhaustive automated test suite for KP Reader 3 (Predictive Stellar Astrology) engine & APIs."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.kp_engine.reader3 import (
    generate_kp_249_table,
    lookup_249_by_number,
    lookup_249_by_longitude,
    lookup_249_by_lords,
    search_249_table,
    compute_cuspal_sub_lords,
    compute_planetary_sub_lords,
    differentiate_twin_births,
    LAGNA_STAR_SIGNIFICATIONS,
    FAVORABLE_HOUSES_KP,
    UNFAVORABLE_HOUSES_KP,
)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. 249 Table Mathematics & Integrity
# ---------------------------------------------------------------------------

def test_249_table_count_and_continuity():
    """Verify exactly 249 divisions tile 0-360 degrees without gaps or overlaps."""
    table = generate_kp_249_table()
    assert len(table) == 249, f"Expected 249 divisions, got {len(table)}"

    # First division: Aries, Ashwini (Ketu), Ketu
    d1 = table[0]
    assert d1.number == 1
    assert d1.sign == "Aries"
    assert d1.sign_lord == "Mars"
    assert d1.star == "Ashwini"
    assert d1.star_lord == "Ketu"
    assert d1.sub_lord == "Ketu"
    assert abs(d1.start_deg - 0.0) < 1e-6
    assert d1.start_dms == "00°00'00\""
    assert d1.end_dms == "00°46'40\""

    # Last division: Pisces, Revati (Mercury), Saturn
    d249 = table[248]
    assert d249.number == 249
    assert d249.sign == "Pisces"
    assert d249.sign_lord == "Jupiter"
    assert d249.star == "Revati"
    assert d249.star_lord == "Mercury"
    assert d249.sub_lord == "Saturn"
    assert abs(d249.end_deg - 360.0) < 1e-5
    assert d249.end_dms == "360°00'00\""

    # Verify continuity: no gaps or overlaps across all 249 divisions
    for i in range(len(table) - 1):
        curr = table[i]
        nxt = table[i + 1]
        assert curr.number + 1 == nxt.number
        assert abs(curr.end_deg - nxt.start_deg) < 1e-5, (
            f"Discontinuity between #{curr.number} ({curr.end_deg}) and #{nxt.number} ({nxt.start_deg})"
        )


def test_249_table_sign_boundary_splits():
    """Verify the 6 classic KP sign-boundary sub splits expounded in Reader 3."""
    table = generate_kp_249_table()

    # Split 1: Krittika-Rahu at 30° (Aries / Taurus)
    div22 = table[21]
    div23 = table[22]
    assert div22.number == 22 and div22.sign == "Aries" and div22.star == "Krittika" and div22.sub_lord == "Rahu"
    assert abs(div22.end_deg - 30.0) < 1e-5
    assert div23.number == 23 and div23.sign == "Taurus" and div23.star == "Krittika" and div23.sub_lord == "Rahu"
    assert abs(div23.start_deg - 30.0) < 1e-5

    # Split 2: Punarvasu-Moon at 90° (Gemini / Cancer)
    div62 = table[61]
    div63 = table[62]
    assert div62.number == 62 and div62.sign == "Gemini" and div62.star == "Punarvasu" and div62.sub_lord == "Moon"
    assert abs(div62.end_deg - 90.0) < 1e-5
    assert div63.number == 63 and div63.sign == "Cancer" and div63.star == "Punarvasu" and div63.sub_lord == "Moon"
    assert abs(div63.start_deg - 90.0) < 1e-5

    # Split 3: Uttara Phalguni-Rahu at 150° (Leo / Virgo)
    div105 = table[104]
    div106 = table[105]
    assert div105.number == 105 and div105.sign == "Leo" and div105.star == "Uttara Phalguni" and div105.sub_lord == "Rahu"
    assert abs(div105.end_deg - 150.0) < 1e-5
    assert div106.number == 106 and div106.sign == "Virgo" and div106.star == "Uttara Phalguni" and div106.sub_lord == "Rahu"
    assert abs(div106.start_deg - 150.0) < 1e-5

    # Split 4: Vishakha-Moon at 210° (Libra / Scorpio)
    div145 = table[144]
    div146 = table[145]
    assert div145.number == 145 and div145.sign == "Libra" and div145.star == "Vishakha" and div145.sub_lord == "Moon"
    assert abs(div145.end_deg - 210.0) < 1e-5
    assert div146.number == 146 and div146.sign == "Scorpio" and div146.star == "Vishakha" and div146.sub_lord == "Moon"
    assert abs(div146.start_deg - 210.0) < 1e-5

    # Split 5: Uttara Ashadha-Rahu at 270° (Sagittarius / Capricorn)
    div188 = table[187]
    div189 = table[188]
    assert div188.number == 188 and div188.sign == "Sagittarius" and div188.star == "Uttara Ashadha" and div188.sub_lord == "Rahu"
    assert abs(div188.end_deg - 270.0) < 1e-5
    assert div189.number == 189 and div189.sign == "Capricorn" and div189.star == "Uttara Ashadha" and div189.sub_lord == "Rahu"
    assert abs(div189.start_deg - 270.0) < 1e-5

    # Split 6: Purva Bhadrapada-Moon at 330° (Aquarius / Pisces)
    div228 = table[227]
    div229 = table[228]
    assert div228.number == 228 and div228.sign == "Aquarius" and div228.star == "Purva Bhadrapada" and div228.sub_lord == "Moon"
    assert abs(div228.end_deg - 330.0) < 1e-5
    assert div229.number == 229 and div229.sign == "Pisces" and div229.star == "Purva Bhadrapada" and div229.sub_lord == "Moon"
    assert abs(div229.start_deg - 330.0) < 1e-5


def test_249_table_significations_completeness():
    """Verify all 249 divisions have complete Reader 3 anatomy, disease, mental, and career profiles."""
    table = generate_kp_249_table()
    for d in table:
        assert d.body_parts, f"Division #{d.number} missing body_parts"
        assert len(d.diseases) > 0, f"Division #{d.number} missing diseases"
        assert d.mental_qualities, f"Division #{d.number} missing mental qualities"
        assert len(d.professions) > 0, f"Division #{d.number} missing professions"


# ---------------------------------------------------------------------------
# 2. Lookup Methods
# ---------------------------------------------------------------------------

def test_lookup_249_by_number():
    """Verify 1-indexed lookup by number."""
    d = lookup_249_by_number(1)
    assert d.number == 1
    assert d.sub_lord == "Ketu"

    d42 = lookup_249_by_number(42)
    assert d42.number == 42
    assert d42.sign == "Gemini"
    assert d42.sub_lord == "Mercury"

    with pytest.raises(ValueError):
        lookup_249_by_number(0)

    with pytest.raises(ValueError):
        lookup_249_by_number(250)


def test_lookup_249_by_longitude():
    """Verify binary search lookup for various longitudes."""
    # 0.0 -> Div 1
    assert lookup_249_by_longitude(0.0).number == 1
    # 30.0 -> Div 23 (Taurus start)
    assert lookup_249_by_longitude(30.0).number == 23
    # 29.999 -> Div 22 (Aries end)
    assert lookup_249_by_longitude(29.999).number == 22
    # 180.0 -> Div 125 (Libra start, Chitra-Mercury)
    assert lookup_249_by_longitude(180.0).number == 125
    # 359.99 -> Div 249
    assert lookup_249_by_longitude(359.99).number == 249


def test_lookup_249_by_lords():
    """Verify retrieval by tri-lord combination."""
    matches = lookup_249_by_lords("Aries", "Ketu", "Ketu")
    assert len(matches) == 1
    assert matches[0].number == 1


def test_search_249_table():
    """Verify filtering by keywords and lord constraints."""
    police_subs = search_249_table(query="police")
    assert len(police_subs) > 0

    cancer_subs = search_249_table(sign="Cancer")
    assert all(d.sign == "Cancer" for d in cancer_subs)


# ---------------------------------------------------------------------------
# 3. Cuspal Sub-Lords Calculation
# ---------------------------------------------------------------------------

def test_compute_cuspal_sub_lords():
    """Verify 12 Cuspal Sub-Lords calculation and promise evaluation."""
    sample_cusps = [
        13.5, 42.1, 71.3, 100.2, 129.8, 160.4,
        193.5, 222.1, 251.3, 280.2, 309.8, 340.4,
    ]
    res = compute_cuspal_sub_lords(sample_cusps)
    assert len(res) == 12

    for c in res:
        assert 1 <= c.house <= 12
        assert 1 <= c.division_249_number <= 249
        assert c.sign in ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
        assert c.sub_lord in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
        assert c.promise in ("Positive", "Negative", "Mixed")
        assert len(c.favorable_houses) > 0
        assert len(c.unfavorable_houses) > 0
        assert "reader3_ruling" in dir(c)


# ---------------------------------------------------------------------------
# 4. Planetary Sub-Lords Calculation
# ---------------------------------------------------------------------------

def test_compute_planetary_sub_lords():
    """Verify planetary sub-lords and 3-tier KP agency decomposition."""
    sample_planets = {
        "Sun": 14.5,
        "Moon": 42.8,
        "Mars": 85.1,
        "Mercury": 28.5,
        "Jupiter": 133.2,
        "Venus": 355.0,
        "Saturn": 215.4,
        "Rahu": 18.0,
        "Ketu": 198.0,
    }
    sample_cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]

    psl = compute_planetary_sub_lords(
        positions=sample_planets,
        cusps=sample_cusps,
        lagna_sign="Aries",
    )
    assert len(psl) == 9

    sun_info = psl["Sun"]
    assert sun_info.planet == "Sun"
    assert sun_info.sign == "Aries"
    assert sun_info.star == "Bharani"
    assert sun_info.star_lord == "Venus"
    # For Aries, Venus rules 2 and 7
    assert sun_info.star_houses_for_lagna == [2, 7]
    assert "Source" in sun_info.source_planet
    assert "Nature" in sun_info.nature_star_lord or "Venus" in sun_info.nature_star_lord
    assert "Sub-Lord" in sun_info.decision_sub_lord


# ---------------------------------------------------------------------------
# 5. Twin Birth Differentiation
# ---------------------------------------------------------------------------

def test_twin_birth_differentiation():
    """Verify divergence between twin births born minutes apart."""
    # Twin 1: 13°30' (Bharani, Venus sub) vs Twin 2: 17°15' (Bharani, Mars sub)
    twin = differentiate_twin_births(lagna1_deg=13.5, lagna2_deg=17.25)
    assert twin.twin1_sub_lord != twin.twin2_sub_lord
    assert twin.twin1_div_number != twin.twin2_div_number
    assert "Traditional astrology fails" in twin.reader3_explanation


# ---------------------------------------------------------------------------
# 6. Lagna Star Significations
# ---------------------------------------------------------------------------

def test_lagna_star_significations_all_signs():
    """Verify all 12 Lagnas have all 9 Star Lords with owned houses."""
    assert len(LAGNA_STAR_SIGNIFICATIONS) == 12
    for lagna, stars in LAGNA_STAR_SIGNIFICATIONS.items():
        assert len(stars) == 9
        for star_lord, meta in stars.items():
            assert "houses_owned" in meta
            assert "functional_nature" in meta
            assert "reader3_ruling" in meta


# ---------------------------------------------------------------------------
# 7. FastAPI API Endpoints Integration Tests
# ---------------------------------------------------------------------------

def test_api_get_table_249(client):
    """GET /api/v1/horoscope/kp/reader3/table-249."""
    res = client.get("/api/v1/horoscope/kp/reader3/table-249")
    assert res.status_code == 200
    data = res.json()
    assert data["total_divisions"] == 249
    assert len(data["divisions"]) == 249


def test_api_get_table_249_filtered(client):
    """GET /api/v1/horoscope/kp/reader3/table-249 with filters."""
    res = client.get("/api/v1/horoscope/kp/reader3/table-249?sign=Taurus")
    assert res.status_code == 200
    data = res.json()
    assert all(d["sign"] == "Taurus" for d in data["divisions"])


def test_api_get_single_division(client):
    """GET /api/v1/horoscope/kp/reader3/table-249/{number}."""
    res = client.get("/api/v1/horoscope/kp/reader3/table-249/1")
    assert res.status_code == 200
    data = res.json()
    assert data["number"] == 1
    assert data["sub_lord"] == "Ketu"

    res_invalid = client.get("/api/v1/horoscope/kp/reader3/table-249/999")
    assert res_invalid.status_code == 400


def test_api_lookup_longitude(client):
    """GET /api/v1/horoscope/kp/reader3/lookup-longitude."""
    res = client.get("/api/v1/horoscope/kp/reader3/lookup-longitude?longitude=31.5")
    assert res.status_code == 200
    data = res.json()
    assert data["sign"] == "Taurus"
    assert data["star_lord"] == "Sun"


def test_api_cuspal_sub_lords(client):
    """POST /api/v1/horoscope/kp/reader3/cuspal-sub-lords with 12 cusps."""
    payload = {
        "cusp_longitudes": [0.0, 31.0, 62.0, 91.0, 120.0, 151.0, 180.0, 211.0, 242.0, 271.0, 300.0, 331.0]
    }
    res = client.post("/api/v1/horoscope/kp/reader3/cuspal-sub-lords", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["cuspal_sub_lords"]) == 12
    assert data["cuspal_sub_lords"][0]["house"] == 1


def test_api_planetary_sub_lords(client):
    """POST /api/v1/horoscope/kp/reader3/planetary-sub-lords."""
    payload = {
        "planet_positions": {
            "Sun": 15.0,
            "Moon": 40.0,
            "Mars": 75.0,
            "Mercury": 20.0,
            "Jupiter": 110.0,
            "Venus": 340.0,
            "Saturn": 200.0,
            "Rahu": 5.0,
            "Ketu": 185.0,
        },
        "lagna_sign": "Aries",
    }
    res = client.post("/api/v1/horoscope/kp/reader3/planetary-sub-lords", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Sun" in data["planetary_sub_lords"]
    assert data["planetary_sub_lords"]["Sun"]["star_houses_for_lagna"] == [2, 7]


def test_api_twin_divergence(client):
    """POST /api/v1/horoscope/kp/reader3/twin-divergence."""
    payload = {"lagna1_deg": 13.5, "lagna2_deg": 17.5}
    res = client.post("/api/v1/horoscope/kp/reader3/twin-divergence", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["twin1_sub_lord"] != data["twin2_sub_lord"]


def test_api_lagna_star_significations(client):
    """GET /api/v1/horoscope/kp/reader3/lagna-star-significations."""
    res = client.get("/api/v1/horoscope/kp/reader3/lagna-star-significations?lagna=Aries")
    assert res.status_code == 200
    data = res.json()
    assert data["lagna"] == "Aries"
    assert "Venus" in data["star_significations"]
    assert data["star_significations"]["Venus"]["houses_owned"] == [2, 7]
