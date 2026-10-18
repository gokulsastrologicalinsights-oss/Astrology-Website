"""Comprehensive unit tests for Four-Category Benefit Bhavas Calculation Service.

Validates:
1. Four available categories: Star Lord Occ | Star Lord Own | Period Lord Occ | Period Lord Own.
   Reference Example B: '1 | 9 | 2 | 6, 11'
2. Rahu / Ketu omission cases:
   - Reference Example A: Mercury with Ketu star lord -> '3 | 1 | 7, 10' (Cat 2 omitted)
   - Reference Example C: Rahu period lord with Mars star lord -> '5 | 5, 12 | 11' (Cat 4 omitted)
   - Both period lord & star lord are Rahu/Ketu -> '8 | 2' (Cats 2 and 4 omitted)
   - Same planet Rahu/Ketu in own star -> '3 | 3' (Cats 2 and 4 omitted)
3. Multiple different Ascendants (Sagittarius, Aries, Taurus, Scorpio, Aquarius).
4. All five Dasa levels (Dasa, Bhukti, Andharam, Soochamam, Pranam) calculated independently.
   Verifies child periods do NOT copy parent's Benefit Bhavas.
5. Handling of unavailable calculation data (never invents a house number).
6. FastAPI endpoint integration (POST /api/v1/horoscope/dasa enriches dasa_tree).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.benefit_bhavas import (
    normalize_planet_name,
    resolve_star_lord,
    get_planet_occupied_house,
    get_planet_owned_houses,
    format_benefit_bhavas,
    calculate_benefit_bhavas,
    PlanetChartContext,
    build_horoscope_planet_contexts,
    enrich_dasa_tree,
)
from app.schemas.dasa import DasaPeriodNode

client = TestClient(app)


# ===========================================================================
# 1. Reference Examples from Specification
# ===========================================================================

def test_reference_example_b_all_four_categories():
    """Reference Example B: Sukran (Sun's star): 1 | 9 | 2 | 6, 11
    
    Sagittarius Ascendant (Sign 9):
    - Sun occupies 1st house (Sagittarius)
    - Sun owns 9th house (Leo)
    - Venus occupies 2nd house (Capricorn)
    - Venus owns 6th (Taurus) and 11th (Libra)
    """
    chart_contexts = {
        "Sun": PlanetChartContext(
            name="Sun",
            longitude=245.0,  # Sagittarius (house 1)
            star_lord="Ketu",
            occupied_house=1,
            owned_houses=[9],  # Leo is house 9
        ),
        "Venus": PlanetChartContext(
            name="Venus",
            longitude=275.0,  # Capricorn (house 2), in Uttara Ashadha (ruled by Sun)
            star_lord="Sun",
            occupied_house=2,
            owned_houses=[6, 11],  # Taurus=6, Libra=11
        ),
    }

    res = calculate_benefit_bhavas("Venus", chart_contexts)
    assert res.period_lord == "Venus"
    assert res.star_lord == "Sun"
    assert res.star_lord_occupied == 1
    assert res.star_lord_owned == [9]
    assert res.period_lord_occupied == 2
    assert res.period_lord_owned == [6, 11]
    assert res.formatted == "1 | 9 | 2 | 6, 11"


def test_reference_example_a_ketu_star_lord_omission():
    """Reference Example A: Mercury with Ketu star lord: 3 | 1 | 7, 10
    
    Sagittarius Ascendant (Sign 9):
    - Ketu occupies 3rd house (Aquarius), owns none (omitted)
    - Mercury occupies 1st house (Sagittarius), owns 7th (Gemini) and 10th (Virgo)
    """
    chart_contexts = {
        "Ketu": PlanetChartContext(
            name="Ketu",
            longitude=310.0,  # Aquarius (house 3)
            star_lord="Rahu",
            occupied_house=3,
            owned_houses=[],  # Ketu owns no houses
        ),
        "Mercury": PlanetChartContext(
            name="Mercury",
            longitude=242.0,  # Sagittarius (house 1), in Mula (ruled by Ketu)
            star_lord="Ketu",
            occupied_house=1,
            owned_houses=[7, 10],  # Gemini=7, Virgo=10
        ),
    }

    res = calculate_benefit_bhavas("Mercury", chart_contexts)
    assert res.period_lord == "Mercury"
    assert res.star_lord == "Ketu"
    assert res.star_lord_occupied == 3
    assert res.star_lord_owned == []  # Omitted in formatted
    assert res.period_lord_occupied == 1
    assert res.period_lord_owned == [7, 10]
    assert res.formatted == "3 | 1 | 7, 10"


def test_reference_example_c_rahu_period_lord_omission():
    """Reference Example C: Period lord is Rahu or Ketu:
    Star Lord Occupied | Star Lord Owned | Period Lord Occupied
    
    Sagittarius Ascendant:
    - Mars occupies 5th house (Aries), owns 5th (Aries) and 12th (Scorpio)
    - Rahu occupies 11th house (Libra), in Chitra (ruled by Mars)
    - Rahu owns none -> Category 4 omitted
    """
    chart_contexts = {
        "Mars": PlanetChartContext(
            name="Mars",
            longitude=5.0,  # Aries (house 5)
            star_lord="Ketu",
            occupied_house=5,
            owned_houses=[5, 12],
        ),
        "Rahu": PlanetChartContext(
            name="Rahu",
            longitude=185.0,  # Libra (house 11), in Chitra (Mars star)
            star_lord="Mars",
            occupied_house=11,
            owned_houses=[],
        ),
    }

    res = calculate_benefit_bhavas("Rahu", chart_contexts)
    assert res.period_lord == "Rahu"
    assert res.star_lord == "Mars"
    assert res.star_lord_occupied == 5
    assert res.star_lord_owned == [5, 12]
    assert res.period_lord_occupied == 11
    assert res.period_lord_owned == []
    assert res.formatted == "5 | 5, 12 | 11"


def test_both_period_lord_and_star_lord_are_nodes():
    """When both period lord and star lord are Rahu/Ketu:
    Categories 2 and 4 are both omitted:
    Result: Star Lord Occupied | Period Lord Occupied
    """
    chart_contexts = {
        "Rahu": PlanetChartContext(
            name="Rahu",
            longitude=220.0,  # Scorpio (house 8)
            star_lord="Saturn",
            occupied_house=8,
            owned_houses=[],
        ),
        "Ketu": PlanetChartContext(
            name="Ketu",
            longitude=40.0,  # Taurus (house 2), in Swati (Rahu star)
            star_lord="Rahu",
            occupied_house=2,
            owned_houses=[],
        ),
    }

    res = calculate_benefit_bhavas("Ketu", chart_contexts)
    assert res.star_lord_occupied == 8
    assert res.period_lord_occupied == 2
    assert res.formatted == "8 | 2"


def test_ketu_in_own_star():
    """Ketu in Ashwini (Ketu star): both period and star lord are Ketu."""
    chart_contexts = {
        "Ketu": PlanetChartContext(
            name="Ketu",
            longitude=5.0,  # Aries (house 3)
            star_lord="Ketu",
            occupied_house=3,
            owned_houses=[],
        ),
    }
    res = calculate_benefit_bhavas("Ketu", chart_contexts)
    assert res.formatted == "3 | 3"


# ===========================================================================
# 2. Different Ascendants and House Ownership Conventions
# ===========================================================================

def test_owned_houses_for_different_ascendants():
    # 1. Aries Ascendant (Sign 1)
    # Sun -> Leo (5)
    # Moon -> Cancer (4)
    # Mars -> Aries (1), Scorpio (8)
    # Mercury -> Gemini (3), Virgo (6)
    # Jupiter -> Sagittarius (9), Pisces (12)
    # Venus -> Taurus (2), Libra (7)
    # Saturn -> Capricorn (10), Aquarius (11)
    assert get_planet_owned_houses("Sun", ascendant_sign_idx=1) == [5]
    assert get_planet_owned_houses("Moon", ascendant_sign_idx=1) == [4]
    assert get_planet_owned_houses("Mars", ascendant_sign_idx=1) == [1, 8]
    assert get_planet_owned_houses("Mercury", ascendant_sign_idx=1) == [3, 6]
    assert get_planet_owned_houses("Jupiter", ascendant_sign_idx=1) == [9, 12]
    assert get_planet_owned_houses("Venus", ascendant_sign_idx=1) == [2, 7]
    assert get_planet_owned_houses("Saturn", ascendant_sign_idx=1) == [10, 11]
    assert get_planet_owned_houses("Rahu", ascendant_sign_idx=1) == []
    assert get_planet_owned_houses("Ketu", ascendant_sign_idx=1) == []

    # 2. Taurus Ascendant (Sign 2)
    # Sun -> Leo (4)
    # Moon -> Cancer (3)
    # Mars -> Aries (12), Scorpio (7)
    # Mercury -> Gemini (2), Virgo (5)
    # Jupiter -> Sagittarius (8), Pisces (11)
    # Venus -> Taurus (1), Libra (6)
    # Saturn -> Capricorn (9), Aquarius (10)
    assert get_planet_owned_houses("Sun", ascendant_sign_idx=2) == [4]
    assert get_planet_owned_houses("Venus", ascendant_sign_idx=2) == [1, 6]
    assert get_planet_owned_houses("Saturn", ascendant_sign_idx=2) == [9, 10]
    assert get_planet_owned_houses("Jupiter", ascendant_sign_idx=2) == [8, 11]

    # 3. Cancer Ascendant (Sign 4)
    # Moon -> Cancer (1)
    # Sun -> Leo (2)
    # Mercury -> Gemini (12), Virgo (3)
    # Venus -> Taurus (11), Libra (4)
    # Mars -> Aries (10), Scorpio (5)
    # Jupiter -> Sagittarius (6), Pisces (9)
    # Saturn -> Capricorn (7), Aquarius (8)
    assert get_planet_owned_houses("Moon", ascendant_sign_idx=4) == [1]
    assert get_planet_owned_houses("Sun", ascendant_sign_idx=4) == [2]
    assert get_planet_owned_houses("Mars", ascendant_sign_idx=4) == [5, 10]
    assert get_planet_owned_houses("Jupiter", ascendant_sign_idx=4) == [6, 9]
    assert get_planet_owned_houses("Saturn", ascendant_sign_idx=4) == [7, 8]

    # 4. Scorpio Ascendant (Sign 8)
    # Mars -> Aries (6), Scorpio (1)
    # Sun -> Leo (10)
    # Moon -> Cancer (9)
    # Venus -> Taurus (7), Libra (12)
    assert get_planet_owned_houses("Mars", ascendant_sign_idx=8) == [1, 6]
    assert get_planet_owned_houses("Sun", ascendant_sign_idx=8) == [10]
    assert get_planet_owned_houses("Moon", ascendant_sign_idx=8) == [9]
    assert get_planet_owned_houses("Venus", ascendant_sign_idx=8) == [7, 12]

    # 5. Aquarius Ascendant (Sign 11)
    # Saturn -> Capricorn (12), Aquarius (1)
    # Sun -> Leo (7)
    # Venus -> Taurus (4), Libra (9)
    assert get_planet_owned_houses("Saturn", ascendant_sign_idx=11) == [1, 12]
    assert get_planet_owned_houses("Sun", ascendant_sign_idx=11) == [7]
    assert get_planet_owned_houses("Venus", ascendant_sign_idx=11) == [4, 9]


# ===========================================================================
# 3. Star Lord Determination
# ===========================================================================

def test_resolve_star_lord():
    # 0° Aries -> Ashwini -> Ketu
    assert resolve_star_lord(0.0) == "Ketu"
    assert resolve_star_lord(10.0) == "Ketu"
    # 15° Aries -> Bharani -> Venus
    assert resolve_star_lord(15.0) == "Venus"
    # 28° Aries -> Krittika -> Sun
    assert resolve_star_lord(28.0) == "Sun"
    # 15° Taurus -> Rohini -> Moon
    assert resolve_star_lord(45.0) == "Moon"
    # 25° Taurus -> Mrigashira -> Mars
    assert resolve_star_lord(55.0) == "Mars"
    # 10° Gemini -> Ardra -> Rahu
    assert resolve_star_lord(70.0) == "Rahu"
    # 25° Gemini -> Punarvasu -> Jupiter
    assert resolve_star_lord(85.0) == "Jupiter"
    # 10° Cancer -> Pushya -> Saturn
    assert resolve_star_lord(100.0) == "Saturn"
    # 25° Cancer -> Ashlesha -> Mercury
    assert resolve_star_lord(115.0) == "Mercury"
    # 275° (5° Capricorn) -> Uttara Ashadha -> Sun
    assert resolve_star_lord(275.0) == "Sun"
    # 245° (5° Sagittarius) -> Mula -> Ketu
    assert resolve_star_lord(245.0) == "Ketu"


# ===========================================================================
# 4. Independent Calculation Across All Five Dasa Levels
# ===========================================================================

def test_all_five_dasa_levels_calculated_independently():
    """Verify that every level (Maha, Antar, Pratyantar, Sookshma, Prana) has its own
    independent Benefit Bhavas and that children never copy their parent's value.
    """
    chart_contexts = {
        "Venus": PlanetChartContext(
            name="Venus",
            longitude=275.0,
            star_lord="Sun",
            occupied_house=2,
            owned_houses=[6, 11],
        ),
        "Sun": PlanetChartContext(
            name="Sun",
            longitude=245.0,
            star_lord="Ketu",
            occupied_house=1,
            owned_houses=[9],
        ),
        "Mars": PlanetChartContext(
            name="Mars",
            longitude=5.0,
            star_lord="Ketu",
            occupied_house=5,
            owned_houses=[5, 12],
        ),
        "Jupiter": PlanetChartContext(
            name="Jupiter",
            longitude=85.0,
            star_lord="Jupiter",
            occupied_house=7,
            owned_houses=[1, 4],
        ),
        "Saturn": PlanetChartContext(
            name="Saturn",
            longitude=305.0,
            star_lord="Mars",
            occupied_house=3,
            owned_houses=[2, 3],
        ),
        "Ketu": PlanetChartContext(
            name="Ketu",
            longitude=310.0,
            star_lord="Rahu",
            occupied_house=3,
            owned_houses=[],
        ),
        "Rahu": PlanetChartContext(
            name="Rahu",
            longitude=130.0,
            star_lord="Venus",
            occupied_house=9,
            owned_houses=[],
        ),
    }

    # Build a 5-level nested node:
    # Level 1 (Maha): Venus
    # Level 2 (Antar): Sun
    # Level 3 (Pratyantar): Mars
    # Level 4 (Sookshma): Jupiter
    # Level 5 (Prana): Saturn
    prana_node = DasaPeriodNode(
        lord="Saturn",
        level="Pranadasha",
        start_jd=2460000.0,
        end_jd=2460001.0,
        duration_days=1.0,
        duration_years=0.0027,
    )
    sookshma_node = DasaPeriodNode(
        lord="Jupiter",
        level="Sookshmadasha",
        start_jd=2460000.0,
        end_jd=2460005.0,
        duration_days=5.0,
        duration_years=0.0137,
        sub_periods=[prana_node],
    )
    pratyantar_node = DasaPeriodNode(
        lord="Mars",
        level="Pratyantardasha",
        start_jd=2460000.0,
        end_jd=2460030.0,
        duration_days=30.0,
        duration_years=0.0821,
        sub_periods=[sookshma_node],
    )
    antar_node = DasaPeriodNode(
        lord="Sun",
        level="Antardasha",
        start_jd=2460000.0,
        end_jd=2460365.0,
        duration_days=365.0,
        duration_years=1.0,
        sub_periods=[pratyantar_node],
    )
    maha_node = DasaPeriodNode(
        lord="Venus",
        level="Mahadasha",
        start_jd=2460000.0,
        end_jd=2467300.0,
        duration_days=7300.0,
        duration_years=20.0,
        sub_periods=[antar_node],
    )

    enrich_dasa_tree([maha_node], chart_contexts)

    # 1. Level 1: Venus -> Star Lord Sun -> 1 | 9 | 2 | 6, 11
    assert maha_node.star_lord == "Sun"
    assert maha_node.benefit_bhavas == "1 | 9 | 2 | 6, 11"

    # 2. Level 2: Sun -> Star Lord Ketu -> 3 | 1 | 9 (Cat 2 omitted!)
    # Must NOT copy Venus's "1 | 9 | 2 | 6, 11"
    assert antar_node.star_lord == "Ketu"
    assert antar_node.benefit_bhavas == "3 | 1 | 9"
    assert antar_node.benefit_bhavas != maha_node.benefit_bhavas

    # 3. Level 3: Mars -> Star Lord Ketu -> 3 | 5 | 5, 12 (Cat 2 omitted!)
    assert pratyantar_node.star_lord == "Ketu"
    assert pratyantar_node.benefit_bhavas == "3 | 5 | 5, 12"
    assert pratyantar_node.benefit_bhavas != antar_node.benefit_bhavas

    # 4. Level 4: Jupiter -> Star Lord Jupiter -> 7 | 1, 4 | 7 | 1, 4
    assert sookshma_node.star_lord == "Jupiter"
    assert sookshma_node.benefit_bhavas == "7 | 1, 4 | 7 | 1, 4"
    assert sookshma_node.benefit_bhavas != pratyantar_node.benefit_bhavas

    # 5. Level 5: Saturn -> Star Lord Mars -> 5 | 5, 12 | 3 | 2, 3
    assert prana_node.star_lord == "Mars"
    assert prana_node.benefit_bhavas == "5 | 5, 12 | 3 | 2, 3"
    assert prana_node.benefit_bhavas != sookshma_node.benefit_bhavas


# ===========================================================================
# 5. Unavailable Data Handling
# ===========================================================================

def test_unavailable_data_does_not_invent_house_number():
    """If occupied house cannot be resolved, output 'Unavailable' rather than inventing a house."""
    res = format_benefit_bhavas(
        cat1_star_lord_occ=None,
        cat2_star_lord_own=[9],
        cat3_period_lord_occ=2,
        cat4_period_lord_own=[6, 11],
        star_lord="Sun",
        period_lord="Venus",
    )
    assert res == "Unavailable | 9 | 2 | 6, 11"

    res_empty_chart = calculate_benefit_bhavas("UnknownGraha", {})
    assert res_empty_chart.formatted == "Unavailable"


# ===========================================================================
# 6. End-to-End API Integration
# ===========================================================================

def test_api_endpoint_returns_benefit_bhavas():
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "depth": 2,
        "target_date": "2026-10-17",
    }
    response = client.post("/api/v1/horoscope/dasa", json=payload)
    assert response.status_code == 200
    data = response.json()

    tree = data["dasa_tree"]
    assert len(tree) == 9

    # Each Mahadasha has star_lord and benefit_bhavas
    for md in tree:
        assert md["star_lord"] is not None
        assert md["benefit_bhavas"] is not None
        assert " | " in md["benefit_bhavas"]

        # Each child Antardasha has star_lord and benefit_bhavas
        for ad in md["sub_periods"]:
            assert ad["star_lord"] is not None
            assert ad["benefit_bhavas"] is not None
            assert " | " in ad["benefit_bhavas"]
