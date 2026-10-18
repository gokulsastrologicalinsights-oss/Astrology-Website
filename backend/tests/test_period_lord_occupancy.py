"""Comprehensive automated tests for Period Lord Occupancy and KP house calculations.

Verifies:
1. house_of_longitude modular boundary wrapping across 360°/0° Aries without House 12 collapse.
2. Canonical Placidus house occupancies for reference chart (Gokul 1999-01-03 05:58 IST).
3. Whole Sign cusps aligned strictly with sidereal rashi boundaries (Mercury in H1, not H12).
4. Four-Category Benefit Bhavas for Period Lords across all 5 Dasa levels.
5. 5-level Dasa hierarchy Vedic naming: Dasa, Bhukti, Andharam, Soochamam, Pranam.
6. KP House Significators (Tier 1 occupants, Tier 3 cuspal lords).
"""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient

from app.main import app
from app.services.kp_engine.significators import house_of_longitude, planet_significations
from app.services.benefit_bhavas import (
    build_horoscope_planet_contexts,
    calculate_benefit_bhavas,
    house_of_longitude as bhava_house_of_longitude,
)
from app.services.ephemeris import compute_ascendant_and_houses, compute_planetary_positions
from app.services.timezone_utils import resolve_birth_datetime

client = TestClient(app)

# Reference Chart: Gokul (1999-01-03 05:58:00 IST, Chennai: 13.0827°N, 80.2707°E)
GOKUL_PAYLOAD = {
    "birth_date": "1999-01-03",
    "birth_time": "05:58:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 1,        # KP
    "house_system": 2,    # Placidus
}


def test_house_of_longitude_wrapping():
    """Verify modular relative distance formula across 0° Aries boundary."""
    # Cusps with Sagittarius Ascendant (Cusp 1 = 250°, Cusp 4 = 352°, Cusp 5 = 23°, etc.)
    cusps = [
        250.0, 280.0, 315.0, 350.0,  # H1, H2, H3, H4
        20.0, 50.0, 70.0, 100.0,     # H5, H6, H7, H8
        135.0, 170.0, 205.0, 230.0   # H9, H10, H11, H12
    ]

    # Planet at 255° -> In H1 (250° to 280°)
    assert house_of_longitude(255.0, cusps) == 1
    assert bhava_house_of_longitude(255.0, cusps) == 1

    # Planet at 355° -> In H4 (350° to 20° wrapping over 0° Aries)
    assert house_of_longitude(355.0, cusps) == 4
    assert bhava_house_of_longitude(355.0, cusps) == 4

    # Planet at 5° Aries -> In H4 (350° to 20° wrapping over 0° Aries)
    assert house_of_longitude(5.0, cusps) == 4
    assert bhava_house_of_longitude(5.0, cusps) == 4

    # Planet at 21° -> In H5 (20° to 50°)
    assert house_of_longitude(21.0, cusps) == 5
    assert bhava_house_of_longitude(21.0, cusps) == 5

    # Planet at 90° -> In H7 (70° to 100°)
    assert house_of_longitude(90.0, cusps) == 7
    assert bhava_house_of_longitude(90.0, cusps) == 7

    # Planet at 175° -> In H10 (170° to 205°)
    assert house_of_longitude(175.0, cusps) == 10
    assert bhava_house_of_longitude(175.0, cusps) == 10

    # Planet at 240° -> In H12 (230° to 250°)
    assert house_of_longitude(240.0, cusps) == 12
    assert bhava_house_of_longitude(240.0, cusps) == 12


def test_reference_chart_kp_occupancies():
    """Verify that KP calculation places planets in correct houses and NOT in House 12."""
    res = client.post("/api/v1/horoscope/kp", json=GOKUL_PAYLOAD)
    assert res.status_code == 200, res.text
    data = res.json()

    # Get house significators (occupants = level_b)
    house_occupants = {hs["house"]: hs["level_b"] for hs in data["house_significators"]}

    # Moon is at ~90.17° (Punarvasu). Cusp 7 is ~69.55°, Cusp 8 is ~101.77°.
    # Moon MUST be in House 7 occupant list, NOT House 12!
    assert "Moon" in house_occupants[7], f"Expected Moon in H7, found in: {[h for h, occ in house_occupants.items() if 'Moon' in occ]}"
    assert "Moon" not in house_occupants[12]

    # Mars is at ~175.76° (Chitra). Cusp 10 is ~172.32°, Cusp 11 is ~203.36°.
    # Mars MUST be in House 10 occupant list, NOT House 12!
    assert "Mars" in house_occupants[10], f"Expected Mars in H10, found in: {[h for h, occ in house_occupants.items() if 'Mars' in occ]}"
    assert "Mars" not in house_occupants[12]

    # Saturn is at ~3.11° (Ashwini). Cusp 4 is ~352.32°, Cusp 5 is ~23.36°.
    # Saturn MUST be in House 4 occupant list, NOT House 12!
    assert "Saturn" in house_occupants[4], f"Expected Saturn in H4, found in: {[h for h, occ in house_occupants.items() if 'Saturn' in occ]}"
    assert "Saturn" not in house_occupants[12]

    # Rahu is at ~120.93° (Magha). Cusp 8 is ~101.77°, Cusp 9 is ~137.06°.
    # Rahu MUST be in House 8 occupant list, NOT House 12!
    assert "Rahu" in house_occupants[8], f"Expected Rahu in H8, found in: {[h for h, occ in house_occupants.items() if 'Rahu' in occ]}"
    assert "Rahu" not in house_occupants[12]


def test_reference_chart_whole_sign_cusps():
    """Verify that Whole Sign aligns with 30° sidereal rashi boundaries."""
    _, _, jd, _, _ = resolve_birth_datetime(
        date(1999, 1, 3), time(5, 58, 0), "Asia/Kolkata"
    )
    asc, mc, houses = compute_ascendant_and_houses(
        jd=jd,
        lat=13.0827,
        lon=80.2707,
        ayanamsa_id=0,      # Lahiri
        house_system_id=0,  # Whole Sign
    )
    assert asc.sign_index == 9  # Sagittarius (240° to 270°)
    # House 1 cusp must start exactly at 240.0°
    assert houses[0].cusp_degree == 240.0
    assert houses[0].sign_name == "Sagittarius"
    # House 2 cusp must start exactly at 270.0°
    assert houses[1].cusp_degree == 270.0
    assert houses[1].sign_name == "Capricorn"
    # House 12 cusp must start at 210.0°
    assert houses[11].cusp_degree == 210.0
    assert houses[11].sign_name == "Scorpio"

    # Now verify planetary positions under Whole Sign
    planets = compute_planetary_positions(jd, ayanamsa_id=0)
    contexts = build_horoscope_planet_contexts(
        planets=planets,
        ascendant_sign_idx=asc.sign_index,
        cusps=[h.cusp_degree for h in houses],
        houses=houses,
    )
    # Mercury is at ~240.28° (Sagittarius). Under Whole Sign, it MUST be in House 1 (Lagna), NOT House 12!
    merc_ctx = contexts["Mercury"]
    assert merc_ctx.occupied_house == 1, f"Expected Mercury in H1, got H{merc_ctx.occupied_house}"

    # Sun (~258°) and Venus (~275° wait, Venus is ~275° = Capricorn -> H2)
    sun_ctx = contexts["Sun"]
    assert sun_ctx.occupied_house == 1


def test_dasa_five_level_hierarchy_names():
    """Verify 5-level Dasa hierarchy naming in both KP and Dasa services."""
    # 1. KP endpoint
    res = client.post("/api/v1/horoscope/kp", json=GOKUL_PAYLOAD)
    assert res.status_code == 200
    kp_data = res.json()
    periods = kp_data["dasa_hierarchy"]["current_periods"]
    assert len(periods) == 5

    assert periods[0]["level"] == 1
    assert periods[0]["level_name"] == "Mahadasha"
    assert periods[0]["vedic_name"] == "Dasa"

    assert periods[1]["level"] == 2
    assert periods[1]["level_name"] == "Antardasha"
    assert periods[1]["vedic_name"] == "Bhukti"

    assert periods[2]["level"] == 3
    assert periods[2]["level_name"] == "Pratyantardasha"
    assert periods[2]["vedic_name"] == "Andharam"

    assert periods[3]["level"] == 4
    assert periods[3]["level_name"] == "Sookshmadasha"
    assert periods[3]["vedic_name"] == "Soochamam"  # Corrected from Pranam!

    assert periods[4]["level"] == 5
    assert periods[4]["level_name"] == "Pranadasha"
    assert periods[4]["vedic_name"] == "Pranam"     # Corrected from Soochamam!


def test_dasa_benefit_bhavas_four_categories():
    """Verify that Four-Category Benefit Bhavas correctly reflects Period Lord Occupancy in Category 3."""
    _, _, jd, _, _ = resolve_birth_datetime(
        date(1999, 1, 3), time(5, 58, 0), "Asia/Kolkata"
    )
    # Even when Placidus cusps are computed for the horoscope, Benefit Bhavas
    # canonically resolves to Vedic Rashi-Bhava (Whole Sign from Lagna).
    asc, mc, houses = compute_ascendant_and_houses(
        jd=jd,
        lat=13.0827,
        lon=80.2707,
        ayanamsa_id=1,      # KP
        house_system_id=2,  # Placidus
    )
    planets = compute_planetary_positions(jd, ayanamsa_id=1)
    contexts = build_horoscope_planet_contexts(
        planets=planets,
        ascendant_sign_idx=asc.sign_index,
        cusps=[h.cusp_degree for h in houses],
        houses=houses,
    )

    # 1. Venus / Sukran (occupied = 2):
    # Venus in Capricorn (idx 10), which is the 2nd sign from Sagittarius Lagna (idx 9).
    # Sun (star lord) in Sagittarius (idx 9) -> occupied 1, owns Leo (idx 5, 9th house) -> [9].
    # Venus owns Taurus (6) and Libra (11) -> [6, 11].
    # Result: '1 | 9 | 2 | 6, 11' (Venus MUST display house 2, NOT 1!)
    res_venus = calculate_benefit_bhavas("Venus", contexts)
    assert res_venus.period_lord == "Venus"
    assert res_venus.star_lord == "Sun"
    assert res_venus.star_lord_occupied == 1
    assert res_venus.star_lord_owned == [9]
    assert res_venus.period_lord_occupied == 2
    assert res_venus.period_lord_owned == [6, 11]
    assert res_venus.formatted == "1 | 9 | 2 | 6, 11"

    # 2. Moon (occupied = 8):
    # Moon in Cancer (idx 4), which is 8th sign from Sagittarius (idx 9).
    # Star lord Jupiter in Aquarius (idx 11) -> occupied 3, owns [1, 4].
    # Period lord Moon: occupied = 8, owned = [8].
    res_moon = calculate_benefit_bhavas("Moon", contexts)
    assert res_moon.star_lord == "Jupiter"
    assert res_moon.star_lord_occupied == 3
    assert res_moon.star_lord_owned == [1, 4]
    assert res_moon.period_lord_occupied == 8
    assert res_moon.period_lord_owned == [8]
    assert res_moon.formatted == "3 | 1, 4 | 8 | 8"

    # 3. Mars (occupied = 10):
    # Mars in Virgo (idx 6), which is 10th sign from Sagittarius (idx 9).
    # Star lord = Mars.
    res_mars = calculate_benefit_bhavas("Mars", contexts)
    assert res_mars.star_lord == "Mars"
    assert res_mars.star_lord_occupied == 10
    assert res_mars.star_lord_owned == [5, 12]
    assert res_mars.period_lord_occupied == 10
    assert res_mars.period_lord_owned == [5, 12]
    assert res_mars.formatted == "10 | 5, 12 | 10 | 5, 12"

    # 4. Saturn (occupied = 5):
    # Saturn in Aries (idx 1), which is 5th sign from Sagittarius (idx 9).
    res_saturn = calculate_benefit_bhavas("Saturn", contexts)
    assert res_saturn.period_lord_occupied == 5
    assert res_saturn.period_lord_owned == [2, 3]

    # 5. Rahu (occupied = 9) - Rahu owns no houses, category 4 omitted:
    # Rahu in Leo (idx 5), which is 9th sign from Sagittarius (idx 9).
    res_rahu = calculate_benefit_bhavas("Rahu", contexts)
    assert res_rahu.period_lord_occupied == 9
    assert res_rahu.period_lord_owned == []


def test_reference_chart_whole_sign_benefit_bhavas_exact_screenshot_match():
    """Verify that Whole Sign Benefit Bhavas EXACTLY matches the user's reference screenshot:
    - Sukran (Sun's star): '1 | 9 | 2 | 6, 11'
    - Mercury (Ketu's star): '3 | 1 | 7, 10'
    - Sun (Venus's star): '2 | 6, 11 | 1 | 9'
    - Ketu (Mars's star): '10 | 5, 12 | 3'
    - Rahu (Ketu's star): '3 | 9'
    - Saturn (Ketu's star): '3 | 5 | 2, 3'
    - Mars (Mars's star): '10 | 5, 12 | 10 | 5, 12'
    - Jupiter (Jupiter's star): '3 | 1, 4 | 3 | 1, 4'
    - Moon (Jupiter's star): '3 | 1, 4 | 8 | 8'
    """
    _, _, jd, _, _ = resolve_birth_datetime(
        date(1999, 1, 3), time(5, 58, 0), "Asia/Kolkata"
    )
    # Whole Sign cusps
    asc, mc, houses = compute_ascendant_and_houses(
        jd=jd,
        lat=13.0827,
        lon=80.2707,
        ayanamsa_id=1,      # KP
        house_system_id=0,  # Whole Sign
    )
    planets = compute_planetary_positions(jd, ayanamsa_id=1)
    contexts = build_horoscope_planet_contexts(
        planets=planets,
        ascendant_sign_idx=asc.sign_index,
        cusps=[h.cusp_degree for h in houses],
        houses=houses,
    )

    # 1. Sukran / Venus (Sun's star): 1 | 9 | 2 | 6, 11
    res_venus = calculate_benefit_bhavas("Venus", contexts)
    assert res_venus.star_lord == "Sun"
    assert res_venus.star_lord_occupied == 1
    assert res_venus.star_lord_owned == [9]
    assert res_venus.period_lord_occupied == 2
    assert res_venus.period_lord_owned == [6, 11]
    assert res_venus.formatted == "1 | 9 | 2 | 6, 11"

    # 2. Mercury (Ketu's star): 3 | 1 | 7, 10
    res_merc = calculate_benefit_bhavas("Mercury", contexts)
    assert res_merc.star_lord == "Ketu"
    assert res_merc.star_lord_occupied == 3
    assert res_merc.star_lord_owned == []  # Ketu owns no houses
    assert res_merc.period_lord_occupied == 1
    assert res_merc.period_lord_owned == [7, 10]
    assert res_merc.formatted == "3 | 1 | 7, 10"

    # 3. Sun (Venus's star): 2 | 6, 11 | 1 | 9
    res_sun = calculate_benefit_bhavas("Sun", contexts)
    assert res_sun.star_lord == "Venus"
    assert res_sun.star_lord_occupied == 2
    assert res_sun.star_lord_owned == [6, 11]
    assert res_sun.period_lord_occupied == 1
    assert res_sun.period_lord_owned == [9]
    assert res_sun.formatted == "2 | 6, 11 | 1 | 9"

    # 4. Ketu (Mars's star): 10 | 5, 12 | 3
    res_ketu = calculate_benefit_bhavas("Ketu", contexts)
    assert res_ketu.star_lord == "Mars"
    assert res_ketu.star_lord_occupied == 10
    assert res_ketu.star_lord_owned == [5, 12]
    assert res_ketu.period_lord_occupied == 3
    assert res_ketu.period_lord_owned == []  # Ketu owns no houses
    assert res_ketu.formatted == "10 | 5, 12 | 3"

    # 5. Rahu (Ketu's star): 3 | 9
    res_rahu = calculate_benefit_bhavas("Rahu", contexts)
    assert res_rahu.star_lord == "Ketu"
    assert res_rahu.star_lord_occupied == 3
    assert res_rahu.star_lord_owned == []
    assert res_rahu.period_lord_occupied == 9
    assert res_rahu.period_lord_owned == []
    assert res_rahu.formatted == "3 | 9"

    # 6. Saturn (Ketu's star): 3 | 5 | 2, 3
    res_sat = calculate_benefit_bhavas("Saturn", contexts)
    assert res_sat.star_lord == "Ketu"
    assert res_sat.star_lord_occupied == 3
    assert res_sat.star_lord_owned == []
    assert res_sat.period_lord_occupied == 5
    assert res_sat.period_lord_owned == [2, 3]
    assert res_sat.formatted == "3 | 5 | 2, 3"

    # 7. Mars (Mars's star): 10 | 5, 12 | 10 | 5, 12
    res_mars = calculate_benefit_bhavas("Mars", contexts)
    assert res_mars.star_lord == "Mars"
    assert res_mars.star_lord_occupied == 10
    assert res_mars.star_lord_owned == [5, 12]
    assert res_mars.period_lord_occupied == 10
    assert res_mars.period_lord_owned == [5, 12]
    assert res_mars.formatted == "10 | 5, 12 | 10 | 5, 12"

    # 8. Jupiter (Jupiter's star): 3 | 1, 4 | 3 | 1, 4
    res_jup = calculate_benefit_bhavas("Jupiter", contexts)
    assert res_jup.star_lord == "Jupiter"
    assert res_jup.star_lord_occupied == 3
    assert res_jup.star_lord_owned == [1, 4]
    assert res_jup.period_lord_occupied == 3
    assert res_jup.period_lord_owned == [1, 4]
    assert res_jup.formatted == "3 | 1, 4 | 3 | 1, 4"

    # 9. Moon (Jupiter's star): 3 | 1, 4 | 8 | 8
    res_moon = calculate_benefit_bhavas("Moon", contexts)
    assert res_moon.star_lord == "Jupiter"
    assert res_moon.star_lord_occupied == 3
    assert res_moon.star_lord_owned == [1, 4]
    assert res_moon.period_lord_occupied == 8
    assert res_moon.period_lord_owned == [8]
    assert res_moon.formatted == "3 | 1, 4 | 8 | 8"


def test_dasa_endpoint_returns_structured_occupancies_all_5_levels():
    """Verify that POST /api/v1/horoscope/dasa returns structured occupancy fields at all 5 levels."""
    payload = {
        **GOKUL_PAYLOAD,
        "depth": 5,
        "house_system": 0,  # Whole Sign
    }
    res = client.post("/api/v1/horoscope/dasa", json=payload)
    assert res.status_code == 200
    data = res.json()

    tree = data["dasa_tree"]
    assert len(tree) == 9

    def check_node(node, level):
        assert node["period_lord_occupied"] is not None, f"Level {level} {node['lord']} missing period_lord_occupied"
        assert 1 <= node["period_lord_occupied"] <= 12
        assert node["star_lord_occupied"] is not None, f"Level {level} {node['lord']} missing star_lord_occupied"
        assert 1 <= node["star_lord_occupied"] <= 12
        assert node["benefit_bhavas"] is not None and "|" in node["benefit_bhavas"]
        assert node["star_lord"] is not None

        # Verify Rahu and Ketu have empty owned houses
        if node["lord"] in ("Rahu", "Ketu"):
            assert node["period_lord_owned"] == []
        else:
            assert len(node["period_lord_owned"]) > 0

        # Recursively check sub periods
        for sub in node.get("sub_periods", []):
            check_node(sub, level + 1)

    for md in tree:
        check_node(md, 1)

    # Specific check for Mercury Mahadasha -> Venus Antardasha in Gokul's chart
    merc_md = next(md for md in tree if md["lord"] == "Mercury")
    assert merc_md["period_lord_occupied"] == 1
    assert merc_md["star_lord_occupied"] == 3
    assert merc_md["benefit_bhavas"] == "3 | 1 | 7, 10"

    venus_ad = next(ad for ad in merc_md["sub_periods"] if ad["lord"] == "Venus")
    assert venus_ad["period_lord_occupied"] == 2
    assert venus_ad["star_lord_occupied"] == 1
    assert venus_ad["benefit_bhavas"] == "1 | 9 | 2 | 6, 11"


def test_dasa_endpoint_with_placidus_house_system_returns_venus_house_2():
    """Verify that POST /api/v1/horoscope/dasa with house_system=2 (Placidus)
    still returns Venus in House 2 and NOT in House 1.
    """
    payload = {
        **GOKUL_PAYLOAD,
        "depth": 2,
        "house_system": 2,  # Placidus
    }
    res = client.post("/api/v1/horoscope/dasa", json=payload)
    assert res.status_code == 200
    data = res.json()

    tree = data["dasa_tree"]
    merc_md = next(md for md in tree if md["lord"] == "Mercury")
    venus_ad = next(ad for ad in merc_md["sub_periods"] if ad["lord"] == "Venus")

    # Venus MUST be in House 2, NOT 1
    assert venus_ad["period_lord_occupied"] == 2, f"Expected Venus in H2, got H{venus_ad['period_lord_occupied']}"
    assert venus_ad["star_lord_occupied"] == 1, f"Expected Sun in H1, got H{venus_ad['star_lord_occupied']}"
    assert venus_ad["benefit_bhavas"] == "1 | 9 | 2 | 6, 11"


def test_retrograde_planet_occupancy_integrity():
    """Verify that retrograde planets have their natal house occupancy determined strictly by longitude."""
    # Chart with retrograde Jupiter: e.g. 1980-01-01 12:00 IST Chennai
    _, _, jd, _, _ = resolve_birth_datetime(date(1980, 1, 1), time(12, 0, 0), "Asia/Kolkata")
    planets = compute_planetary_positions(jd, ayanamsa_id=0)
    jup = next(p for p in planets if p.name == "Jupiter")
    assert jup.is_retrograde is True, "Jupiter should be retrograde on 1980-01-01"

    asc, mc, houses = compute_ascendant_and_houses(jd, 13.0827, 80.2707, ayanamsa_id=0, house_system_id=0)
    contexts = build_horoscope_planet_contexts(planets, asc.sign_index, [h.cusp_degree for h in houses], houses)
    jup_ctx = contexts["Jupiter"]
    assert 1 <= jup_ctx.occupied_house <= 12
    # Longitude is in Leo (~140°). Ascendant is Pisces (~340°). Sign 5 - Sign 12 + 12 = 5 + 1 = 6th house.
    assert jup_ctx.occupied_house == 6


def test_multiple_ascendants_occupancy():
    """Verify house occupancy and Benefit Bhavas across diverse Ascendants (Lagnas)."""
    # 1. Aries Ascendant (0° to 30°)
    # Ascendant at 15° Aries, Sun at 45° (Taurus) -> Sun is in House 2
    cusps_aries = [float(h * 30.0) for h in range(12)]
    assert house_of_longitude(45.0, cusps_aries) == 2
    assert bhava_house_of_longitude(45.0, cusps_aries) == 2

    # 2. Cancer Ascendant (90° to 120°)
    # Ascendant at 105° (Cancer), Planet at 15° (Aries) -> Aries is 10th sign from Cancer -> House 10
    cusps_cancer = [float(((3 + h) % 12) * 30.0) for h in range(12)]
    assert house_of_longitude(15.0, cusps_cancer) == 10
    assert bhava_house_of_longitude(15.0, cusps_cancer) == 10

    # 3. Pisces Ascendant (330° to 360°)
    # Ascendant at 345° (Pisces), Planet at 15° (Aries) -> Aries is 2nd sign from Pisces -> House 2
    cusps_pisces = [float(((11 + h) % 12) * 30.0) for h in range(12)]
    assert house_of_longitude(15.0, cusps_pisces) == 2
    assert bhava_house_of_longitude(15.0, cusps_pisces) == 2


def test_cusp_boundary_precision():
    """Verify exact boundary behavior for planets 0.001° before vs after cusp boundaries."""
    cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]

    # Exactly on Cusp 2 (30.0°) -> In House 2
    assert house_of_longitude(30.0, cusps) == 2
    # 0.001° before Cusp 2 (29.999°) -> In House 1
    assert house_of_longitude(29.999, cusps) == 1
    # 0.001° after Cusp 2 (30.001°) -> In House 2
    assert house_of_longitude(30.001, cusps) == 2

    # Exactly on Cusp 1 (0.0°) -> In House 1
    assert house_of_longitude(0.0, cusps) == 1
    # 0.001° before Cusp 1 (359.999°) -> In House 12
    assert house_of_longitude(359.999, cusps) == 12
    # 0.001° after Cusp 1 (0.001°) -> In House 1
    assert house_of_longitude(0.001, cusps) == 1

