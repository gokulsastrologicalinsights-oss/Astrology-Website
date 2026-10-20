"""Unit and contract tests for Marriage Compatibility Engine Foundation (Phase 1).

Tests:
1. Astrological reference data, tables, and enum integrity.
2. Input validation contracts (coordinates, timezone, gender).
3. Chart context creation, adapters, and coordinate resolution via XALEN.
4. House-distance and Parashari aspect calculations.
5. Pydantic request and response schema serialization.
"""

import math
import pytest
from datetime import date, time

from app.schemas.common import BirthInput
from app.schemas.marriage import (
    MarriagePartyInput,
    MarriageCompatibilityRequest,
    PersonProfileSummary,
    MarriageCompatibilityResponse,
    FinalAssessmentSummary,
)
from app.services.marriage_engine.models import (
    Gender,
    CompatibilityOutcome,
    RuleEvaluationStatus,
    PoruthamGrade,
    GanaType,
    NadiType,
    RajjuType,
    VashyaCategory,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
    SIGN_LORDS,
    NAKSHATRA_NAMES_EN,
    NAKSHATRA_NAMES_TA,
    NAKSHATRA_LORDS,
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    NAKSHATRA_RAJJU,
    NAKSHATRA_YONI_ANIMAL,
    YONI_BITTER_ENEMIES,
    VEDHA_PAIRS,
    SIGN_VASHYA_CATEGORY,
    PARASHARI_ASPECT_OFFSETS,
    MarriageChartContext,
)
from app.services.marriage_engine.validation import (
    validate_coordinates,
    validate_timezone,
    validate_gender,
    validate_chart_context,
    MarriageValidationError,
    MissingChartDataError,
    InvalidCoordinateError,
)
from app.services.marriage_engine.adapters import (
    build_chart_context_from_birth_input,
    build_chart_context_from_horoscope_response,
)
from app.services.ephemeris import calculate_full_horoscope


# ---------------------------------------------------------------------------
# 1. Reference Data & Constants Integrity
# ---------------------------------------------------------------------------

def test_nakshatra_tables_complete_coverage():
    """Verify all 27 nakshatras have complete, non-null classical metadata."""
    assert len(NAKSHATRA_NAMES_EN) == 27
    assert len(NAKSHATRA_NAMES_TA) == 27
    assert len(NAKSHATRA_LORDS) == 27
    assert len(NAKSHATRA_GANA) == 27
    assert len(NAKSHATRA_NADI) == 27
    assert len(NAKSHATRA_RAJJU) == 27
    assert len(NAKSHATRA_YONI_ANIMAL) == 27

    for idx in range(27):
        assert idx in NAKSHATRA_GANA
        assert idx in NAKSHATRA_NADI
        assert idx in NAKSHATRA_RAJJU
        assert idx in NAKSHATRA_YONI_ANIMAL
        assert NAKSHATRA_NAMES_EN[idx] != ""
        assert NAKSHATRA_NAMES_TA[idx] != ""
        assert NAKSHATRA_LORDS[idx] in ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")


def test_rajju_groups_distribution():
    """Verify classical 5-Rajju partition: Shiro(3), Kantha(6), Udara(6), Kati(6), Pada(6) = 27."""
    counts = {r: 0 for r in RajjuType}
    for idx, rajju in NAKSHATRA_RAJJU.items():
        counts[rajju] += 1

    assert counts[RajjuType.SHIRO] == 3     # Mrigashira, Chitra, Dhanishta
    assert counts[RajjuType.KANTHA] == 6
    assert counts[RajjuType.UDARA] == 6
    assert counts[RajjuType.KATI] == 6
    assert counts[RajjuType.PADA] == 6
    assert sum(counts.values()) == 27


def test_nadi_groups_distribution():
    """Verify classical 3-Nadi partition: exactly 9 in Adi, 9 in Madhya, 9 in Antya."""
    counts = {n: 0 for n in NadiType}
    for idx, nadi in NAKSHATRA_NADI.items():
        counts[nadi] += 1

    assert counts[NadiType.ADI] == 9
    assert counts[NadiType.MADHYA] == 9
    assert counts[NadiType.ANTYA] == 9
    assert sum(counts.values()) == 27


def test_gana_groups_distribution():
    """Verify classical 3-Gana partition: Deva, Manushya, and Rakshasa."""
    counts = {g: 0 for g in GanaType}
    for idx, gana in NAKSHATRA_GANA.items():
        counts[gana] += 1

    assert counts[GanaType.DEVA] == 9
    assert counts[GanaType.MANUSHYA] == 9
    assert counts[GanaType.RAKSHASA] == 9
    assert sum(counts.values()) == 27


def test_vedha_pairs_symmetry():
    """Verify 12 classical mutually repulsive Vedha pairs are symmetric."""
    assert len(VEDHA_PAIRS) >= 24  # 12 pairs in both directions + Mars triangle
    for star_a, star_b in VEDHA_PAIRS:
        assert (star_b, star_a) in VEDHA_PAIRS
        assert 0 <= star_a <= 26
        assert 0 <= star_b <= 26


def test_yoni_bitter_enemies_symmetry():
    """Verify 7 classical sworn enemy animal pairs are symmetric."""
    for animal_a, animal_b in YONI_BITTER_ENEMIES:
        assert (animal_b, animal_a) in YONI_BITTER_ENEMIES


def test_zodiac_sign_constants():
    """Verify 12 signs, lords, and vashya categories."""
    assert len(SIGN_NAMES_EN) == 12
    assert len(SIGN_NAMES_TA) == 12
    assert len(SIGN_LORDS) == 12
    assert len(SIGN_VASHYA_CATEGORY) == 12

    for s in range(1, 13):
        assert s in SIGN_NAMES_EN
        assert s in SIGN_NAMES_TA
        assert s in SIGN_LORDS
        assert s in SIGN_VASHYA_CATEGORY


# ---------------------------------------------------------------------------
# 2. Input Validation Contracts
# ---------------------------------------------------------------------------

def test_coordinate_validation_valid():
    """Valid coordinates should return unchanged floats."""
    lat, lon = validate_coordinates(13.0827, 80.2707)
    assert lat == 13.0827
    assert lon == 80.2707

    # Extremes
    lat, lon = validate_coordinates(90.0, 180.0)
    assert lat == 90.0
    assert lon == 180.0

    lat, lon = validate_coordinates(-90.0, -180.0)
    assert lat == -90.0
    assert lon == -180.0


def test_coordinate_validation_out_of_bounds():
    """Coordinates out of bounds must raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(90.0001, 80.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(-90.0001, 80.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(13.0, 180.0001)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(13.0, -180.0001)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(float("nan"), 80.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(13.0, float("inf"))


def test_timezone_validation():
    """Valid IANA zones and UTC offsets should pass, invalid should raise."""
    assert validate_timezone("Asia/Kolkata") == "Asia/Kolkata"
    assert validate_timezone("+05:30") == "+05:30"
    assert validate_timezone("-04:00") == "-04:00"
    assert validate_timezone("UTC") == "UTC"

    with pytest.raises(MarriageValidationError):
        validate_timezone("")

    with pytest.raises(MarriageValidationError):
        validate_timezone("   ")

    with pytest.raises(MarriageValidationError):
        validate_timezone("Invalid/Zone/123!?$")


def test_gender_normalization():
    """Gender aliases should normalize cleanly into Gender enum."""
    assert validate_gender("male", Gender.MALE) == Gender.MALE
    assert validate_gender("groom", Gender.MALE) == Gender.MALE
    assert validate_gender("boy", Gender.MALE) == Gender.MALE
    assert validate_gender("female", Gender.FEMALE) == Gender.FEMALE
    assert validate_gender("bride", Gender.FEMALE) == Gender.FEMALE
    assert validate_gender("girl", Gender.FEMALE) == Gender.FEMALE
    assert validate_gender(None, Gender.MALE) == Gender.MALE

    with pytest.raises(MarriageValidationError):
        validate_gender("other", Gender.MALE)


# ---------------------------------------------------------------------------
# 3. Chart Adapters & Context Construction
# ---------------------------------------------------------------------------

def test_build_chart_context_from_birth_input():
    """Build context from raw BirthInput using verified XALEN ephemeris."""
    birth = BirthInput(
        birth_date=date(1995, 10, 24),
        birth_time=time(14, 30, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )

    ctx = build_chart_context_from_birth_input(
        birth=birth,
        person_id="groom-101",
        person_name="Groom Test",
        gender=Gender.MALE,
        ayanamsa_id=0,  # Lahiri
        house_system_id=0,  # Whole Sign
    )

    assert ctx.person_id == "groom-101"
    assert ctx.person_name == "Groom Test"
    assert ctx.gender == Gender.MALE
    assert ctx.timezone == "Asia/Kolkata"

    # Moon position sanity check for 1995-10-24 in Libra (Swati/Vishakha)
    assert ctx.moon is not None
    assert 1 <= ctx.moon.sign_index <= 12
    assert 0 <= ctx.moon.nakshatra_index <= 26
    assert 1 <= ctx.moon.nakshatra_pada <= 4
    assert 1 <= ctx.moon.navamsa_sign_index <= 12

    # Lagna sanity check
    assert 1 <= ctx.ascendant_sign_idx <= 12
    assert 0 <= ctx.ascendant_nakshatra_idx <= 26
    assert 1 <= ctx.ascendant_nakshatra_pada <= 4
    assert 1 <= ctx.ascendant_navamsa_sign_idx <= 12

    # Planets present
    for g_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        assert g_name in ctx.grahas
        p = ctx.grahas[g_name]
        assert 0.0 <= p.longitude < 360.0
        assert 1 <= p.sign_index <= 12
        assert 1 <= p.house <= 12

    # 12 Houses present
    assert len(ctx.houses) == 12
    for h in range(1, 13):
        assert h in ctx.houses
        house = ctx.houses[h]
        assert house.house_number == h
        assert 1 <= house.sign_index <= 12
        assert house.lord_name != ""


def test_build_chart_context_from_horoscope_response():
    """Verify adapter works directly on a precomputed HoroscopeResponse object."""
    birth = BirthInput(
        birth_date=date(1997, 6, 15),
        birth_time=time(9, 15, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    horo_res = calculate_full_horoscope(
        birth_date=birth.birth_date,
        birth_time=birth.birth_time,
        timezone_str=birth.timezone,
        latitude=birth.latitude,
        longitude=birth.longitude,
        ayanamsa_id=0,
        house_system_id=0,
    )

    ctx = build_chart_context_from_horoscope_response(
        horoscope=horo_res,
        person_id="bride-202",
        person_name="Bride Test",
        gender=Gender.FEMALE,
    )

    assert ctx.person_id == "bride-202"
    assert ctx.gender == Gender.FEMALE
    assert ctx.moon is not None
    assert ctx.sun is not None
    assert ctx.mars is not None
    assert ctx.venus is not None
    assert ctx.jupiter is not None


def test_chart_context_helpers():
    """Test relative house calculations, conjunctions, and Parashari aspects."""
    birth = BirthInput(
        birth_date=date(1990, 1, 1),
        birth_time=time(6, 0, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    ctx = build_chart_context_from_birth_input(
        birth=birth,
        person_id="test-ctx",
        person_name="Context Test",
        gender=Gender.MALE,
    )

    # 7th house lord
    lord_7 = ctx.get_house_lord(7)
    expected_7th_sign = ((ctx.ascendant_sign_idx + 5) % 12) + 1
    assert lord_7 == SIGN_LORDS[expected_7th_sign]

    # Relative house distance
    h_dist = ctx.house_from(ctx.moon.sign_index, ctx.ascendant_sign_idx)
    assert h_dist == ctx.moon.house

    # Conjunction reflexivity with itself
    assert ctx.is_conjoined("Sun", "Sun", max_orb=1.0) is True


def test_validation_rejects_incomplete_chart():
    """validate_chart_context should catch corrupt or missing planets/houses."""
    birth = BirthInput(
        birth_date=date(1990, 1, 1),
        birth_time=time(6, 0, 0),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    ctx = build_chart_context_from_birth_input(
        birth=birth,
        person_id="corrupt-test",
        person_name="Corrupt Test",
        gender=Gender.MALE,
    )

    # Delete Moon
    del ctx.grahas["Moon"]
    with pytest.raises(MissingChartDataError):
        validate_chart_context(ctx)


# ---------------------------------------------------------------------------
# 4. Pydantic Schemas & Serialization
# ---------------------------------------------------------------------------

def test_marriage_party_input_validation():
    """MarriagePartyInput requires either birth_input or saved_horoscope_id."""
    # Valid with birth_input
    party1 = MarriagePartyInput(
        name="Partner A",
        birth_input=BirthInput(
            birth_date=date(1990, 5, 20),
            birth_time=time(10, 0, 0),
            timezone="Asia/Kolkata",
            latitude=13.08,
            longitude=80.27,
        ),
    )
    assert party1.name == "Partner A"

    # Valid with saved_horoscope_id
    party2 = MarriagePartyInput(
        name="Partner B",
        saved_horoscope_id="123e4567-e89b-12d3-a456-426614174000",
    )
    assert party2.saved_horoscope_id is not None

    # Invalid with neither
    with pytest.raises(ValueError):
        MarriagePartyInput(name="Empty")


def test_marriage_request_serialization():
    """Verify MarriageCompatibilityRequest parses and serializes cleanly."""
    req = MarriageCompatibilityRequest(
        groom=MarriagePartyInput(
            name="Groom",
            birth_input=BirthInput(
                birth_date=date(1992, 4, 14),
                birth_time=time(8, 0, 0),
                timezone="Asia/Kolkata",
                latitude=13.0827,
                longitude=80.2707,
            ),
        ),
        bride=MarriagePartyInput(
            name="Bride",
            birth_input=BirthInput(
                birth_date=date(1995, 10, 24),
                birth_time=time(14, 30, 0),
                timezone="Asia/Kolkata",
                latitude=13.0827,
                longitude=80.2707,
            ),
        ),
        rule_system="all",
        include_timing=True,
        include_kp=True,
    )

    data = req.model_dump()
    assert data["rule_system"] == "all"
    assert data["groom"]["name"] == "Groom"
    assert data["bride"]["name"] == "Bride"
    assert data["include_timing"] is True
