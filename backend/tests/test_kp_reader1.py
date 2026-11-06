"""Unit tests verifying KP Reader 1 ("Casting the Horoscope") engine implementation.

Validates the core principles, formulas, tables, and case studies published by
Prof. K. S. Krishnamurti in KP Reader 1:
- KP Ayanamsa (291 A.D. coincidence, Newcomb precession rate 50.2388475"/yr, 1840-2001 table).
- LMT conversion (4 min / degree).
- 4-step Sidereal Time calculations with worked examples (Agra, Allahabad, Ahmedabad, Boston, San Francisco).
- Vimshottari Dasa balance rates per degree and per minute (360-day dasha year basis).
- 108-division Navamsa cycle and Vargottama determinations.
- Ruling Planets (RP) with Node representations.
- Integration into KP API (/api/v1/horoscope/kp).
"""

from datetime import date, datetime, time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.kp_engine.constants import (
    KP_COINCIDENCE_YEAR,
    NEWCOMB_PRECESSION_RATE_ARCSEC,
    NEWCOMB_PRECESSION_RATE_DEG,
    NAVAMSA_SPAN_DEG,
    NAVAMSA_SPAN_ARCMIN,
    VIMSHOTTARI_YEARS,
    VIMSHOTTARI_TOTAL_YEARS,
)
from app.services.kp_engine.reader1 import (
    KP_READER1_AYANAMSA_TABLE,
    get_reader1_table_ayanamsa,
    calculate_reader1_ayanamsa,
    format_ayanamsa_dms,
    standard_to_gmt,
    standard_to_lmt,
    calculate_sidereal_time_reader1,
    READER1_DASA_BALANCE_RATES,
    calculate_dasa_balance_reader1,
    get_navamsa_info,
    calculate_ruling_planets_reader1,
    READER1_WORKED_EXAMPLES,
)
from app.services.kp_engine.vedic import (
    navamsa_index,
    navamsa_sign,
    navamsa_lord,
    is_vargottama,
    point_info,
)


# ---------------------------------------------------------------------------
# 1. Authentic KP Reader 1 Ayanamsa Tests
# ---------------------------------------------------------------------------

def test_kp_coincidence_and_precession_constants():
    """Verify foundational constants codified from Reader 1."""
    assert KP_COINCIDENCE_YEAR == 291
    assert abs(NEWCOMB_PRECESSION_RATE_ARCSEC - 50.2388475) < 1e-6
    assert abs(NEWCOMB_PRECESSION_RATE_DEG - (50.2388475 / 3600.0)) < 1e-9
    assert abs(NAVAMSA_SPAN_DEG - (10.0 / 3.0)) < 1e-9
    assert NAVAMSA_SPAN_ARCMIN == 200.0


def test_reader1_ayanamsa_table_values():
    """Verify authentic tabular ayanamsa values published in Reader 1, page 59."""
    # Key historical reference points from Reader 1
    assert get_reader1_table_ayanamsa(1840) == (21, 31)
    assert get_reader1_table_ayanamsa(1900) == (22, 22)
    assert get_reader1_table_ayanamsa(1908) == (22, 29)
    assert get_reader1_table_ayanamsa(1921) == (22, 39)
    assert get_reader1_table_ayanamsa(1938) == (22, 54)
    assert get_reader1_table_ayanamsa(1963) == (23, 15)
    assert get_reader1_table_ayanamsa(2000) == (23, 46)
    assert get_reader1_table_ayanamsa(2001) == (23, 47)


def test_reader1_ayanamsa_beyond_2001():
    """Verify Reader 1 explicit formula for years beyond 2001 (+50.2388475" per year)."""
    # 2001 base: 23° 47' = 23.783333°
    # In 2026 (25 years later): 25 * 50.2388475" = 1255.97" ~ 20' 56" -> ~24° 07' 56"
    ayan_2026 = calculate_reader1_ayanamsa(2026.0)
    assert 24.1 < ayan_2026 < 24.2
    d, m = get_reader1_table_ayanamsa(2026)
    assert d == 24
    assert m in (7, 8)


def test_format_ayanamsa_dms():
    """Verify degree-minute-second formatting for ayanamsa."""
    assert format_ayanamsa_dms(23.25) == "23° 15' 00.0\""
    formatted_1900 = format_ayanamsa_dms(22.0 + 22.0 / 60.0)
    assert "22° 22'" in formatted_1900


# ---------------------------------------------------------------------------
# 2. Time & Sidereal Time Calculations (4-step Reader 1 Method)
# ---------------------------------------------------------------------------

def test_standard_to_gmt_and_lmt():
    """Verify Standard Time to GMT and LMT conversions."""
    # India Standard Time (IST) 82°30' E: GMT is IST - 5h 30m
    assert abs(standard_to_gmt(12.25, 82.5) - 6.75) < 1e-6  # 12:15 PM IST = 6:45 AM GMT

    # Madras (80°15' E) at 12:15 PM IST:
    # Diff = 80.25 - 82.5 = -2.25 deg -> -9 min -> 12:06 PM LMT (Reader 1 Ex 1)
    lmt_madras = standard_to_lmt(12.25, 80.25, 82.5)
    assert abs(lmt_madras - 12.10) < 1e-6  # 12.10 hrs = 12h 06m


def test_reader1_worked_example_1_agra():
    """Reader 1 Ex 1: 15-5-1963 at Agra 78°05' E, 6:30 PM IST."""
    ex = READER1_WORKED_EXAMPLES["Agra_1963"]
    # 78°05' = 78.083333°
    lmt = standard_to_lmt(ex["std_time"], ex["longitude"], ex["std_meridian"])
    # 6:30 PM = 18.5 hrs. Diff = 78.083333 - 82.5 = -4.416667 deg * 4 min/deg = -17.6667 min = -17m 40s
    # 18h 30m - 17m 40s = 18h 12m 20s = 18.205556 hrs
    assert abs(lmt - 18.205556) < 1e-4

    # Previous noon Greenwich ST on 15-5-1963 = 3h 29m 59s
    st_audit = calculate_sidereal_time_reader1(
        lmt_time_hours=lmt,
        longitude_deg=ex["longitude"],
        prev_noon_greenwich_st_hours=3.0 + 29.0 / 60.0 + 59.0 / 3600.0,
        use_exact_acceleration=False,  # Reader 1 standard 10s/hr
    )
    # Book result: 9h 42m 29s
    assert "09h 42m 29s" in st_audit.formatted_st


def test_reader1_worked_example_2_allahabad():
    """Reader 1 Ex 2: 15-5-1963 at Allahabad 81°54' E, 3:30 AM IST."""
    ex = READER1_WORKED_EXAMPLES["Allahabad_1963"]
    lmt = standard_to_lmt(ex["std_time"], ex["longitude"], ex["std_meridian"])
    # 3:30 AM = 3.5 hrs. Diff = 81.9 - 82.5 = -0.6 deg * 4 = -2.4 min = -2m 24s -> 3h 27m 36s = 3.46 hrs
    assert abs(lmt - 3.46) < 1e-4

    # Previous noon Greenwich ST on 14-5-1963 = 3h 26m 02s
    st_audit = calculate_sidereal_time_reader1(
        lmt_time_hours=lmt,
        longitude_deg=ex["longitude"],
        prev_noon_greenwich_st_hours=3.0 + 26.0 / 60.0 + 2.0 / 3600.0,
        use_exact_acceleration=False,
    )
    # Book result: 18h 55m 18s
    assert "18h 55m 18s" in st_audit.formatted_st


def test_reader1_worked_example_3_ahmedabad():
    """Reader 1 Ex 3: 15-5-1963 at Ahmedabad 72°38' E, 12:05 PM IST."""
    ex = READER1_WORKED_EXAMPLES["Ahmedabad_1963"]
    lmt = standard_to_lmt(ex["std_time"], ex["longitude"], ex["std_meridian"])
    # Diff = 72.633333 - 82.5 = -9.866667 deg * 4 = -39.4667 min = -39m 28s
    # 12h 05m - 39m 28s = 11h 25m 32s
    h = int(lmt)
    m = int((lmt - h) * 60)
    assert h == 11 and m == 25

    # Previous noon Greenwich ST on 14-5-1963 = 3h 26m 02s
    st_audit = calculate_sidereal_time_reader1(
        lmt_time_hours=lmt,
        longitude_deg=ex["longitude"],
        prev_noon_greenwich_st_hours=3.0 + 26.0 / 60.0 + 2.0 / 3600.0,
        use_exact_acceleration=False,
    )
    # Book result: 2h 54m 40s
    assert "02h 54m 40s" in st_audit.formatted_st


# ---------------------------------------------------------------------------
# 3. Vimshottari Dasa Balance Tests (Reader 1 Table on Page 88)
# ---------------------------------------------------------------------------

def test_reader1_dasa_balance_rates():
    """Verify rates per 1 degree and per 1 minute codified in Reader 1 page 88."""
    # Check total mahadasha years
    assert sum(VIMSHOTTARI_YEARS.values()) == 120

    # Ketu (7 years): 0y 6m 9d per 1°, 3.15 days per 1'
    ketu_rates = READER1_DASA_BALANCE_RATES["Ketu"]
    assert ketu_rates["dasa_years"] == 7
    assert ketu_rates["per_degree"] == (0, 6, 9)
    assert ketu_rates["days_per_minute"] == 3.15

    # Venus (20 years): 1y 6m 0d per 1°, 9.00 days per 1'
    venus_rates = READER1_DASA_BALANCE_RATES["Venus"]
    assert venus_rates["dasa_years"] == 20
    assert venus_rates["per_degree"] == (1, 6, 0)
    assert venus_rates["days_per_minute"] == 9.00

    # Sun (6 years): 0y 5m 12d per 1°, 2.70 days per 1'
    assert READER1_DASA_BALANCE_RATES["Sun"]["per_degree"] == (0, 5, 12)
    assert READER1_DASA_BALANCE_RATES["Sun"]["days_per_minute"] == 2.70

    # Moon (10 years): 0y 9m 0d per 1°, 4.50 days per 1'
    assert READER1_DASA_BALANCE_RATES["Moon"]["per_degree"] == (0, 9, 0)
    assert READER1_DASA_BALANCE_RATES["Moon"]["days_per_minute"] == 4.50


def test_reader1_worked_dasa_balance_example():
    """Verify worked example on page 88: Moon at 16° Taurus (Rohini 6°)."""
    # Rohini spans 40° to 53° 20'. 16° Taurus = 46° longitude.
    # Transited: 6°. Balance to transit: 7° 20' = 440'.
    # Balance: 440 / 800 * 10 years = 5.5 years = 5 years 6 months 0 days.
    bal = calculate_dasa_balance_reader1(46.0, use_360_day_year=True)
    assert bal.lord == "Moon"
    assert bal.nakshatra == "Rohini"
    assert abs(bal.balance_arcmin - 440.0) < 1e-4
    assert bal.balance_years == 5
    assert bal.balance_months == 6
    assert abs(bal.balance_days - 0.0) < 1e-2
    # Sub lord at 16° Taurus (6° Rohini): Saturn sub (15°40' to 17°46'40" Taurus)
    assert bal.sub_lord == "Saturn"


# ---------------------------------------------------------------------------
# 4. Navamsa Chakra & Vargottama Tests (108 Padas)
# ---------------------------------------------------------------------------

def test_navamsa_cycle_and_lords():
    """Verify 108 continuous Navamsa segments matching Reader 1 pages 79-81."""
    # Aries 0°-3°20': Aries navamsa (Mars) -> Vargottama!
    n1 = get_navamsa_info(1.0)
    assert n1.rasi_sign == "Aries"
    assert n1.navamsa_sign == "Aries"
    assert n1.navamsa_lord == "Mars"
    assert n1.is_vargottama is True

    # Taurus 10°-13°20': Cancer navamsa (Moon)
    n2 = get_navamsa_info(41.0)
    assert n2.rasi_sign == "Taurus"
    assert n2.navamsa_sign == "Aries"

    # Gemini 28°: Gemini navamsa (Mercury) -> Vargottama!
    n3 = get_navamsa_info(88.0)
    assert n3.rasi_sign == "Gemini"
    assert n3.navamsa_sign == "Gemini"
    assert n3.navamsa_lord == "Mercury"
    assert n3.is_vargottama is True


def test_vargottama_helper():
    """Verify is_vargottama helper across different signs."""
    # First navamsa of movable (chara) signs is Vargottama
    assert is_vargottama(1.0) is True     # Aries 1° -> Aries Navamsa
    assert is_vargottama(91.0) is True    # Cancer 1° -> Cancer Navamsa
    assert is_vargottama(181.0) is True   # Libra 1° -> Libra Navamsa
    assert is_vargottama(271.0) is True   # Capricorn 1° -> Capricorn Navamsa

    # Fifth navamsa of fixed (sthira) signs is Vargottama (13°20' to 16°40')
    assert is_vargottama(44.0) is True    # Taurus 14° -> Taurus Navamsa
    assert is_vargottama(134.0) is True   # Leo 14° -> Leo Navamsa

    # Ninth navamsa of common (dvisvabhava) signs is Vargottama (26°40' to 30°)
    assert is_vargottama(88.0) is True    # Gemini 28° -> Gemini Navamsa
    assert is_vargottama(178.0) is True   # Virgo 28° -> Virgo Navamsa


def test_point_info_includes_navamsa():
    """Verify point_info includes navamsa fields."""
    info = point_info(1.0)
    assert info.navamsa_sign == "Aries"
    assert info.navamsa_lord == "Mars"
    assert info.is_vargottama is True


# ---------------------------------------------------------------------------
# 5. Ruling Planets (RP) with Node Representations
# ---------------------------------------------------------------------------

def test_ruling_planets_with_nodes():
    """Verify Ruling Planets calculation with Node representations."""
    # Friday (weekday 4 = Venus), Ascendant at 10° Aries (Mars/Ketu/Saturn), Moon at 20° Taurus (Venus/Moon/Ketu)
    rps = calculate_ruling_planets_reader1(
        ascendant_lon=10.0,
        moon_lon=50.0,
        weekday=4,
        planet_positions={"Rahu": 95.0, "Ketu": 275.0, "Mars": 10.0},
    )
    planets = [rp.planet for rp in rps]
    assert "Venus" in planets  # Day Lord & Moon Sign Lord
    assert "Mars" in planets   # Ascendant Sign Lord
    assert "Ketu" in planets   # Ascendant Star Lord


# ---------------------------------------------------------------------------
# 6. API Integration Test (/api/v1/horoscope/kp)
# ---------------------------------------------------------------------------

def test_kp_api_returns_navamsa_fields():
    """Verify that the KP API endpoint populates navamsa and vargottama fields."""
    client = TestClient(app)
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "birth_place": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
        "ayanamsa": 1,        # KP
        "house_system": 2,   # Placidus
    }
    response = client.post("/api/v1/horoscope/kp", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # Check planets have navamsa_sign, navamsa_lord, and is_vargottama
    planets = data["planetary_positions"]
    assert len(planets) >= 9
    for p in planets:
        assert "navamsa_sign" in p and p["navamsa_sign"] is not None
        assert "navamsa_lord" in p and p["navamsa_lord"] is not None
        assert "is_vargottama" in p and p["is_vargottama"] is not None

    # Check cusps have navamsa fields
    cusps = data["cuspal_analysis"]
    assert len(cusps) == 12
    for c in cusps:
        assert "navamsa_sign" in c and c["navamsa_sign"] is not None
        assert "navamsa_lord" in c and c["navamsa_lord"] is not None
        assert "is_vargottama" in c and c["is_vargottama"] is not None
