"""Unit tests for Medical Astrology Engine and Rule Registry.

Verifies:
1. Documented rule matching and negative cases.
2. Vedic and KP separation.
3. Missing data handling.
4. Current Dasha selection against existing engine output.
5. English and Tamil bilingual rendering.
6. Source attribution and safety restrictions.
"""

import pytest
from app.schemas.medical_astrology import (
    SAFETY_DISCLAIMER_EN,
    SAFETY_DISCLAIMER_TA,
    MedicalAstrologyResponse,
)
from app.services.medical_astrology_engine.registry import (
    RULE_SET_VERSION,
    MEDICAL_RULES_REGISTRY,
    KALAPURUSHA_ANATOMY,
    PLANET_ANATOMY_GOVERNANCE,
)
from app.services.medical_astrology_engine.engine import calculate_medical_astrology
from app.services.ephemeris import calculate_full_horoscope
from app.services.kp_service import calculate_kp_chart
from app.services.dasa_service import calculate_dasa
from app.schemas.kp import KpRequest
from app.schemas.dasa import DasaRequest


# Standard test fixture data (1990-05-15 14:30:00 Chennai, India)
TEST_BIRTH_DATA = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 0,
    "house_system": 0,
}


def test_safety_disclaimer_integrity():
    """Verify exact safety disclaimer text is preserved in English and Tamil."""
    assert "Medical Astrology presents traditional astrological interpretations for educational and research purposes only" in SAFETY_DISCLAIMER_EN
    assert "Astrological combinations cannot diagnose, confirm or predict disease" in SAFETY_DISCLAIMER_EN
    assert "For health concerns, consult a qualified healthcare professional" in SAFETY_DISCLAIMER_EN

    assert "மருத்துவ ஜோதிடம் பாரம்பரிய ஜோதிட விளக்கங்களை கல்வி மற்றும் ஆராய்ச்சி நோக்கங்களுக்காக மட்டுமே வழங்குகிறது" in SAFETY_DISCLAIMER_TA
    assert "உடல்நலம் குறித்த கவலைகளுக்கு தகுதியான மருத்துவ நிபுணரை அணுகவும்" in SAFETY_DISCLAIMER_TA


def test_rule_registry_version_and_sources():
    """Verify rule registry versioning, classical sources, and non-empty citations."""
    assert RULE_SET_VERSION == "1.0.0"
    assert len(MEDICAL_RULES_REGISTRY) >= 15

    # Check BPHS Chapter 17 core rules exist
    bphs_keys = [k for k in MEDICAL_RULES_REGISTRY if k.startswith("bphs_17")]
    assert len(bphs_keys) >= 9

    for rule_id, rule in MEDICAL_RULES_REGISTRY.items():
        assert rule.id == rule_id
        assert rule.name and len(rule.name) > 3
        assert rule.source in {
            "Brihat Parashara Hora Shastra",
            "Phaladeepika",
            "Saravali",
            "Saravali & Phaladeepika",
            "Phaladeepika & Saravali",
            "KP Reader IV: Medical Astrology",
        }
        assert rule.traditional_interpretation and len(rule.traditional_interpretation) > 20
        assert rule.interpretation_tamil and len(rule.interpretation_tamil) > 20
        assert rule.system in {"vedic", "kp"}


def test_kalapurusha_anatomy_all_twelve_signs():
    """Verify Kalapurusha 12-sign anatomical mapping covers head to feet."""
    assert len(KALAPURUSHA_ANATOMY) == 12
    # Aries: Head / brain
    assert "Head" in KALAPURUSHA_ANATOMY[1]["organs_en"]
    assert "தலை" in KALAPURUSHA_ANATOMY[1]["organs_ta"]
    # Pisces: Feet
    assert "Feet" in KALAPURUSHA_ANATOMY[12]["organs_en"]
    assert "பாதங்கள்" in KALAPURUSHA_ANATOMY[12]["organs_ta"]


def test_planetary_anatomy_governance():
    """Verify all 9 grahas have documented anatomical and humor governance."""
    for graha in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        assert graha in PLANET_ANATOMY_GOVERNANCE
        info = PLANET_ANATOMY_GOVERNANCE[graha]
        assert info["organs_en"] and info["organs_ta"]
        assert info["dosha"]


def test_calculate_medical_astrology_full():
    """Verify end-to-end medical astrology evaluation with horoscope, dasa, and KP."""
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=TEST_BIRTH_DATA["ayanamsa"],
        house_system_id=TEST_BIRTH_DATA["house_system"],
        include_panchang=False,
    )

    kp_req = KpRequest(**TEST_BIRTH_DATA)
    kp_res = calculate_kp_chart(kp_req, ayanamsa_id=0, house_system_id=0)

    dasa_req = DasaRequest(depth=3, **TEST_BIRTH_DATA)
    dasa_res = calculate_dasa(dasa_req, depth=3)

    res = calculate_medical_astrology(
        horoscope=horoscope,
        dasa=dasa_res,
        kp=kp_res,
        gender="male",
    )

    assert isinstance(res, MedicalAstrologyResponse)
    assert res.rule_set_version == "1.0.0"
    assert res.disclaimer_en == SAFETY_DISCLAIMER_EN
    assert res.disclaimer_ta == SAFETY_DISCLAIMER_TA

    # Perspective A: Birth Chart
    bc = res.vedic_analysis.birth_chart
    assert bc.lagna_analysis.house_number == 1
    assert bc.sixth_house_analysis.house_number == 6
    assert bc.eighth_house_analysis.house_number == 8
    assert bc.twelfth_house_analysis.house_number == 12
    assert len(bc.anatomical_mappings) == 12

    # Perspective B: Current Period
    cp = res.vedic_analysis.current_period
    assert cp.mahadasha and cp.mahadasha != "Unknown"
    assert cp.traditional_synthesis_en
    assert cp.traditional_synthesis_ta

    # Perspective C: Historical Periods
    hp = res.vedic_analysis.historical_periods
    assert len(hp.periods) > 0
    assert hp.periods[0].period_name
    assert hp.periods[0].traditional_notes_en
    assert hp.periods[0].traditional_notes_ta

    # KP Analytical System
    kp_analysis = res.kp_analysis
    assert kp_analysis is not None
    assert kp_analysis.sixth_csl.cusp_number == 6
    assert kp_analysis.sixth_csl.csl_planet
    assert isinstance(kp_analysis.sixth_csl.signified_houses, list)
    assert kp_analysis.sixth_csl.primary_signification_en
    assert kp_analysis.sixth_csl.primary_signification_ta


def test_vedic_kp_separation():
    """Verify Vedic and KP systems remain strictly separated in response structure."""
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )
    kp_req = KpRequest(**TEST_BIRTH_DATA)
    kp_res = calculate_kp_chart(kp_req, ayanamsa_id=0, house_system_id=0)

    res = calculate_medical_astrology(horoscope=horoscope, kp=kp_res)

    # Vedic triggered rules should ONLY be from the vedic system
    for r in res.vedic_analysis.birth_chart.triggered_rules:
        assert r.system == "vedic"

    # KP rules should ONLY be from the kp system
    assert res.kp_analysis is not None
    for r in res.kp_analysis.kp_rules:
        assert r.system == "kp"


def test_missing_data_graceful_handling():
    """Verify that when dasa or kp are None, the engine does not fail and returns clean output."""
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )

    # Call with None for both dasa and kp
    res = calculate_medical_astrology(horoscope=horoscope, dasa=None, kp=None)

    assert isinstance(res, MedicalAstrologyResponse)
    assert res.vedic_analysis.birth_chart.lagna_analysis.house_number == 1
    assert res.kp_analysis is None
    assert res.vedic_analysis.current_period.mahadasha == "Unknown"
    assert len(res.vedic_analysis.historical_periods.periods) == 0


def test_negative_cases_no_false_matching():
    """Verify that rules with unfulfilled mandatory conditions are not marked active."""
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )
    res = calculate_medical_astrology(horoscope=horoscope)

    # Every active rule in birth chart must satisfy is_active=True and have conditions passed=True
    for r in res.vedic_analysis.birth_chart.triggered_rules:
        assert r.is_active is True
        assert r.status == "Qualifying"
        for cond in r.conditions:
            assert cond.passed is True


def test_kp_6th_csl_nonempty_significations_and_provenance():
    """Requirement 1: Verify 6th CSL and star lord have valid, nonempty house significations and provenance."""
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )
    kp_req = KpRequest(**TEST_BIRTH_DATA)
    kp_res = calculate_kp_chart(kp_req, ayanamsa_id=0, house_system_id=0)

    res = calculate_medical_astrology(horoscope=horoscope, kp=kp_res)
    assert res.kp_analysis is not None
    c6 = res.kp_analysis.sixth_csl

    # CSL and Star Lord must be populated
    assert c6.csl_planet == "Venus"
    assert c6.csl_star_lord == "Mercury"
    assert c6.star_lord == "Mercury"
    assert c6.cusp_number == 6
    assert c6.cusp_degree is not None
    assert c6.sign_name is not None

    # Signified houses must be non-empty and sorted
    assert len(c6.signified_houses) > 0
    assert 1 in c6.signified_houses
    assert 8 in c6.signified_houses

    # Signification sources provenance details must be populated
    assert len(c6.signification_details) > 0
    for detail in c6.signification_details:
        assert detail.house in c6.signified_houses
        assert detail.source_type in {"StarLord", "Occupant", "Owner", "Aspecting", "level_a", "level_b", "level_c", "level_d"}
        assert detail.description_en and len(detail.description_en) > 5
        assert detail.description_ta and len(detail.description_ta) > 5

    # Data availability
    assert c6.is_data_available is True
    assert c6.missing_data_reason is None
    assert "KP Reader IV" in c6.calculation_provenance

    # Explanation must be data-driven and contain actual planet and house numbers
    assert "Venus" in c6.primary_signification_en
    assert "Mercury" in c6.primary_signification_en
    assert "Venus" in c6.primary_signification_ta
    assert "Mercury" in c6.primary_signification_ta


def test_kp_category_evaluations_and_conflict_preservation():
    """Requirements 2, 3, 4, 5: Verify category statuses (present vs not_found) and conflict preservation."""
    # Chart 1: 1990-05-15 (Venus signifies 1, 2, 7, 8, 9, 10)
    horo1 = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )
    kp_req1 = KpRequest(**TEST_BIRTH_DATA)
    kp_res1 = calculate_kp_chart(kp_req1, ayanamsa_id=0, house_system_id=0)
    res1 = calculate_medical_astrology(horoscope=horo1, kp=kp_res1)
    c6_1 = res1.kp_analysis.sixth_csl

    # Recovery (1 is present)
    assert c6_1.recovery_status == "present"
    assert c6_1.recovery_signified is True
    assert 1 in c6_1.recovery_houses

    # Chronic (8 is present)
    assert c6_1.chronic_status == "present"
    assert c6_1.chronic_signified is True
    assert 8 in c6_1.chronic_houses

    # Genuine calculated absence of disease (6) and hospitalization (12)
    assert c6_1.disease_status == "not_found"
    assert c6_1.disease_signified is False
    assert c6_1.disease_houses == []

    assert c6_1.hospitalization_status == "not_found"
    assert c6_1.hospitalization_signified is False
    assert c6_1.hospitalization_houses == []

    # Chart 2: 1982-09-09 06:30 Chennai (Saturn signifies [1, 2, 3, 6, 7] - House 6 AND House 1 present)
    birth2 = {
        "birth_date": "1982-09-09",
        "birth_time": "06:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    horo2 = calculate_full_horoscope(
        birth_date=birth2["birth_date"],
        birth_time=birth2["birth_time"],
        timezone_str=birth2["timezone"],
        latitude=birth2["latitude"],
        longitude=birth2["longitude"],
        ayanamsa_id=1,
        house_system_id=2,
    )
    kp_req2 = KpRequest(ayanamsa=1, house_system=2, **birth2)
    kp_res2 = calculate_kp_chart(kp_req2, ayanamsa_id=1, house_system_id=2)
    res2 = calculate_medical_astrology(horoscope=horo2, kp=kp_res2)
    c6_2 = res2.kp_analysis.sixth_csl

    # House 6 is present
    assert c6_2.disease_status == "present"
    assert c6_2.disease_signified is True
    assert 6 in c6_2.disease_houses

    # House 1 is also present (Recovery) -> Conflict is preserved, not masked!
    assert c6_2.recovery_status == "present"
    assert c6_2.recovery_signified is True
    assert 1 in c6_2.recovery_houses

    # Chart 3: 2000-01-01 10:15 Chennai (Mars signifies [3, 10, 12] - Hospitalization 12 present)
    birth3 = {
        "birth_date": "2000-01-01",
        "birth_time": "10:15:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    horo3 = calculate_full_horoscope(
        birth_date=birth3["birth_date"],
        birth_time=birth3["birth_time"],
        timezone_str=birth3["timezone"],
        latitude=birth3["latitude"],
        longitude=birth3["longitude"],
        ayanamsa_id=1,
        house_system_id=2,
    )
    kp_req3 = KpRequest(ayanamsa=1, house_system=2, **birth3)
    kp_res3 = calculate_kp_chart(kp_req3, ayanamsa_id=1, house_system_id=2)
    res3 = calculate_medical_astrology(horoscope=horo3, kp=kp_res3)
    c6_3 = res3.kp_analysis.sixth_csl

    # House 12 is present
    assert c6_3.hospitalization_status == "present"
    assert c6_3.hospitalization_signified is True
    assert 12 in c6_3.hospitalization_houses

    # Houses 1, 5, 11 not present in chart 3
    assert c6_3.recovery_status == "not_found"
    assert c6_3.recovery_signified is False


def test_kp_missing_csl_and_significator_data_does_not_turn_into_no():
    """Requirements 6, 7, 10: Missing data returns 'data_unavailable', never four false negative 'No' results."""
    horo = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA["birth_date"],
        birth_time=TEST_BIRTH_DATA["birth_time"],
        timezone_str=TEST_BIRTH_DATA["timezone"],
        latitude=TEST_BIRTH_DATA["latitude"],
        longitude=TEST_BIRTH_DATA["longitude"],
        ayanamsa_id=0,
    )
    kp_req = KpRequest(**TEST_BIRTH_DATA)
    kp_res = calculate_kp_chart(kp_req, ayanamsa_id=0, house_system_id=0)

    # Simulate missing significator data for CSL planet
    mock_kp = kp_res.model_copy(deep=True)
    mock_kp.significators = []
    mock_kp.house_significators = []

    res = calculate_medical_astrology(horoscope=horo, kp=mock_kp)
    c6 = res.kp_analysis.sixth_csl

    assert c6.is_data_available is False
    assert c6.missing_data_reason is not None

    # Must be 'data_unavailable' — NEVER 'not_found' / 'No'!
    assert c6.recovery_status == "data_unavailable"
    assert c6.disease_status == "data_unavailable"
    assert c6.chronic_status == "data_unavailable"
    assert c6.hospitalization_status == "data_unavailable"

    # Simulate empty CSL on 6th cusp
    mock_kp2 = kp_res.model_copy(deep=True)
    for c in mock_kp2.cuspal_analysis:
        if c.house == 6:
            c.sub_lord = ""

    res2 = calculate_medical_astrology(horoscope=horo, kp=mock_kp2)
    c6_2 = res2.kp_analysis.sixth_csl

    assert c6_2.is_data_available is False
    assert c6_2.recovery_status == "data_unavailable"
    assert c6_2.disease_status == "data_unavailable"
    assert c6_2.chronic_status == "data_unavailable"
    assert c6_2.hospitalization_status == "data_unavailable"


def test_kp_screenshot_case_gokul_and_no_unresolved_placeholders():
    """Verify screenshot chart (1999-01-03 05:58:00 Chennai):
    1. Cusp 6 = 43.01° Taurus, Cusp Star = Moon, CSL = Rahu, CSL Star = Mercury.
    2. Cusp Star Lord and CSL Star Lord are strictly distinct.
    3. No unresolved placeholders ({csl}, {starLord}, etc.) in English or Tamil.
    4. Signified houses [7, 10, 12] deduplicated in summary.
    5. Four category statuses: Recovery (not_found), Disease (not_found), Chronic (not_found), Hospitalization (present).
    6. Multi-level provenance preserved (H12 dual mechanism).
    """
    import re
    from app.schemas.kp import (
        KpResponse,
        KpCuspDetail,
        PlanetaryKpPosition,
        PlanetSignificator,
        HouseSignificatorEntry,
        SignificatorStrengthEntry,
    )
    from app.schemas.common import CalculationMetadata

    gokul_kp = KpResponse(
        metadata=CalculationMetadata(
            ayanamsa_name="Lahiri",
            ayanamsa_id=0,
            house_system_id=2,
            ayanamsa_deg=23.8404,
            house_system_name="Placidus",
            birth_utc_iso="1999-01-03T00:28:00+00:00",
            calculation_frame="Geocentric Sidereal",
            julian_day_ut1=2451181.5194,
        ),
        planetary_positions=[
            PlanetaryKpPosition(
                planet="Rahu",
                body_id=9,
                longitude=119.5631,
                sign_index=4,
                sign_name="Cancer",
                sign_lord="Moon",
                star_lord="Mercury",
                sub_lord="Saturn",
                sub_sub_lord="Rahu",
                kp_number=83,
            ),
            PlanetaryKpPosition(
                planet="Mercury",
                body_id=3,
                longitude=255.4,
                sign_index=9,
                sign_name="Sagittarius",
                sign_lord="Jupiter",
                star_lord="Venus",
                sub_lord="Jupiter",
                sub_sub_lord="Mercury",
                kp_number=180,
            ),
            PlanetaryKpPosition(
                planet="Moon",
                body_id=1,
                longitude=85.1,
                sign_index=3,
                sign_name="Gemini",
                sign_lord="Mercury",
                star_lord="Jupiter",
                sub_lord="Saturn",
                sub_sub_lord="Moon",
                kp_number=60,
            ),
        ],
        cuspal_analysis=[
            KpCuspDetail(house=1, cusp_degree=248.5, sign_index=9, sign_name="Sagittarius", sign_lord="Jupiter", star_lord="Ketu", sub_lord="Venus", promise="Positive"),
            KpCuspDetail(house=2, cusp_degree=279.1, sign_index=10, sign_name="Capricorn", sign_lord="Saturn", star_lord="Sun", sub_lord="Venus", promise="Positive"),
            KpCuspDetail(house=3, cusp_degree=312.4, sign_index=11, sign_name="Aquarius", sign_lord="Saturn", star_lord="Rahu", sub_lord="Saturn", promise="Positive"),
            KpCuspDetail(house=4, cusp_degree=344.8, sign_index=12, sign_name="Pisces", sign_lord="Jupiter", star_lord="Saturn", sub_lord="Rahu", promise="Positive"),
            KpCuspDetail(house=5, cusp_degree=14.5, sign_index=1, sign_name="Aries", sign_lord="Mars", star_lord="Venus", sub_lord="Venus", promise="Positive"),
            KpCuspDetail(
                house=6,
                cusp_degree=43.006,
                sign_index=2,
                sign_name="Taurus",
                sign_lord="Venus",
                star_lord="Moon",
                sub_lord="Rahu",
                sub_sub_lord="Mercury",
                promise="Negative",
            ),
        ],
        significators=[
            PlanetSignificator(
                planet="Rahu",
                signified_houses=[12],
                strength_order=[
                    SignificatorStrengthEntry(house=12, type="StarLord"),
                    SignificatorStrengthEntry(house=12, type="Occupant"),
                ],
            )
        ],
        house_significators=[
            HouseSignificatorEntry(house=7, sign_name="Gemini", sign_lord="Mercury", star_lord="Rahu", sub_lord="Jupiter", sub_sub_lord="Jupiter", level_a=[], level_b=[], level_c=["Rahu"], level_d=["Mercury"], all_significators=["Rahu", "Mercury"]),
            HouseSignificatorEntry(house=10, sign_name="Virgo", sign_lord="Mercury", star_lord="Moon", sub_lord="Jupiter", sub_sub_lord="Rahu", level_a=[], level_b=[], level_c=["Rahu"], level_d=["Mercury"], all_significators=["Rahu", "Mercury"]),
            HouseSignificatorEntry(house=12, sign_name="Scorpio", sign_lord="Mars", star_lord="Saturn", sub_lord="Rahu", sub_sub_lord="Rahu", level_a=["Ketu"], level_b=["Rahu", "Mercury"], level_c=[], level_d=[], all_significators=["Rahu", "Mercury", "Ketu"]),
        ],
    )

    horo = calculate_full_horoscope(
        birth_date="1999-01-03",
        birth_time="05:58:00",
        timezone_str="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
        ayanamsa_id=0,
    )

    res = calculate_medical_astrology(horoscope=horo, kp=gokul_kp)
    c6 = res.kp_analysis.sixth_csl

    # 1. Cusp and planet parameters match screenshot exactly
    assert round(c6.cusp_degree, 2) == 43.01
    assert c6.sign_name == "Taurus"
    assert c6.cusp_star_lord == "Moon"
    assert c6.csl_planet == "Rahu"
    assert c6.csl_star_lord == "Mercury"

    # 2. Cusp Star Lord and CSL Star Lord are distinct
    assert c6.cusp_star_lord != c6.csl_star_lord
    assert c6.cusp_star_lord == "Moon"
    assert c6.csl_star_lord == "Mercury"

    # 3. No unresolved placeholders
    for text in (c6.primary_signification_en, c6.primary_signification_ta):
        assert "{csl}" not in text
        assert "{cslStarL}" not in text
        assert "{csl_star_l}" not in text
        assert "{starLord}" not in text
        assert "{star_lord}" not in text
        assert not re.search(r"\{[a-zA-Z0-9_]+\}", text), f"Found unresolved placeholder in: {text}"

    # 4. Signified houses deduplicated in summary
    assert c6.signified_houses == [7, 10, 12]
    assert "7, 10, 12" in c6.primary_signification_ta
    assert "7, 10, 12" in c6.primary_signification_en
    assert "Rahu" in c6.primary_signification_ta
    assert "Mercury" in c6.primary_signification_ta

    # 5. Four categories
    assert c6.recovery_status == "not_found"
    assert c6.disease_status == "not_found"
    assert c6.chronic_status == "not_found"
    assert c6.hospitalization_status == "present"
    assert c6.hospitalization_houses == [12]

    # 6. Provenance details: 4 rows (H12 dual mechanism preserved)
    assert len(c6.signification_details) == 4
    h12_details = [d for d in c6.signification_details if d.house == 12]
    assert len(h12_details) == 2
    types_h12 = {d.source_type for d in h12_details}
    assert "StarLord" in types_h12
    assert "Occupant" in types_h12

    # Check planet_channel
    star_h12 = [d for d in h12_details if d.source_type == "StarLord"][0]
    assert "Rahu -> Mercury" in star_h12.planet_channel


