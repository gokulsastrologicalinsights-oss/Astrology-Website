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


def test_dr_krishna_kumar_compendium():
    """Verify Dr. S. Krishna Kumar Medical Astrology compendium evaluation."""
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
    res = calculate_medical_astrology(horoscope=horoscope)

    assert res.dr_krishna_kumar_compendium is not None
    comp = res.dr_krishna_kumar_compendium

    # Metadata & authorship
    assert "Dr. S. Krishna Kumar" in comp.author
    assert "Horoscope or Stethoscope" in comp.book_title
    assert len(comp.salient_features) >= 10

    # 27 Nakshatras complete matrix
    assert len(comp.all_27_nakshatras) == 27
    ashwini = comp.all_27_nakshatras[0]
    assert ashwini.number == 1
    assert ashwini.name == "Ashwini"
    assert "fever" in ashwini.disease_tendency_en.lower()

    # Native Moon Star resolution
    assert comp.native_moon_star is not None
    assert comp.native_moon_star.name in ["Uttarashada", "Uttara Ashadha", "Uttara Phalguni", "Shravana"]
    assert comp.native_moon_star.number == 21

    # 10 Gestational Months
    assert len(comp.gestational_months) == 10
    m1 = comp.gestational_months[0]
    assert m1.month == 1
    assert m1.ruling_planet == "Venus"
    assert "Kalala" in m1.sanskrit_term

    # 9 Progeny Curses
    assert len(comp.progeny_shapas) >= 9
    shapa_ids = {s.id for s in comp.progeny_shapas}
    assert "sarpa_shapa" in shapa_ids
    assert "pitru_shapa" in shapa_ids
    assert "matru_shapa" in shapa_ids

    # 12 Case studies
    assert len(comp.case_studies) == 12
    c1 = comp.case_studies[0]
    assert "Mental Aberration" in c1.title_en

    # 5 Tatwas & Navadwaras
    assert len(comp.tatwas_and_senses) == 5

    # Observations
    assert comp.caesarean_vs_normal_delivery_observation is not None
    assert comp.sperm_potency_observation is not None


def test_dr_chatterjee_compendium_full():
    """Verify Dr. S. S. Chatterjee's Advance Medical Astrology compendium evaluation."""
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
    res = calculate_medical_astrology(
        horoscope=horoscope,
        dasa=None,
        kp=None,
        gender="male",
    )

    assert res.dr_chatterjee_compendium is not None
    chat = res.dr_chatterjee_compendium

    # 1. Author and Title
    assert "Dr. S. S. Chatterjee" in chat.author
    assert "Advance Medical Astrology" in chat.book_title
    assert any("Electro-chemical" in f or "Death Point" in f for f in chat.salient_features)

    # 2. Death Point Calculation
    dp = chat.death_point
    assert dp is not None
    assert 0.0 <= dp.longitude_deg < 360.0
    assert 1 <= dp.sign_index <= 12
    assert dp.sign_name_en != ""
    assert dp.nakshatra_name != ""
    assert 1 <= dp.nakshatra_pada <= 4
    assert isinstance(dp.transit_saturn_aspect_active, bool)
    assert len(dp.aspect_details_en) > 10
    assert len(dp.aspect_details_ta) > 10

    # 3. Sapta Dhatus (7 tissues)
    assert len(chat.sapta_dhatus) == 7
    dhatu_names = {d.dhatu_name_en for d in chat.sapta_dhatus}
    assert any("Asthi" in name for name in dhatu_names)
    assert any("Rasa" in name for name in dhatu_names)
    assert any("Rakta" in name for name in dhatu_names)
    assert any("Mamsa" in name for name in dhatu_names)
    assert any("Medas" in name for name in dhatu_names)
    assert any("Majja" in name for name in dhatu_names)
    assert any("Shukra" in name for name in dhatu_names)

    # 4. Endocrine Glands (8 glands)
    assert len(chat.endocrine_glands) == 8
    gland_names = {g.gland_name_en for g in chat.endocrine_glands}
    assert any("Pituitary" in name for name in gland_names)
    assert any("Thyroid" in name for name in gland_names)
    assert any("Pancreas" in name for name in gland_names)
    assert any("Adrenal" in name for name in gland_names)

    # 5. Tridosha Anatomical Sites
    assert len(chat.tridosha_sites) == 5

    # 6. Diabetes Mellitus Special Diagnostic Module
    dm = chat.diabetes_assessment
    assert dm is not None
    assert dm.affliction_score >= 0
    assert dm.risk_level in ("Low", "Moderate", "High")
    assert len(dm.symptoms_noted) >= 5
    assert len(dm.remedial_measures_en) >= 6
    assert len(dm.remedial_measures_ta) >= 6

    # 7. 10 Modern Complex Diseases
    assert len(chat.modern_diseases) == 10
    disease_names = {d.name_en for d in chat.modern_diseases}
    assert any("Hepatitis" in name for name in disease_names)
    assert any("Lupus" in name for name in disease_names)
    assert any("Celiac" in name for name in disease_names)
    assert any("Vertigo" in name for name in disease_names)

    # 8. Natural Remedies Guide
    rem = chat.natural_remedies
    assert rem is not None
    assert len(rem.planetary_colour_therapy) == 7
    assert len(rem.metal_charged_waters) == 4
    assert len(rem.vega_dharana_urges) == 13

    # 9. 28 Evaluated Golden Rules
    assert len(chat.golden_rules) == 28
    for r in chat.golden_rules:
        assert r.id.startswith("chatterjee_")
        assert len(r.name) > 3
        assert len(r.traditional_interpretation) > 10
        assert r.system == "vedic"

    # 10. Practical Case Studies
    assert len(chat.case_studies) == 6
    case_ids = {c["case_id"] if isinstance(c, dict) else c.case_id for c in chat.case_studies}
    assert "chatterjee_case_1_diabetes" in case_ids
    assert "chatterjee_case_2_robust_health" in case_ids
    assert "chatterjee_case_6_khorana_nobel" in case_ids





def test_max_heindel_compendium_full():
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA['birth_date'],
        birth_time=TEST_BIRTH_DATA['birth_time'],
        timezone_str=TEST_BIRTH_DATA['timezone'],
        latitude=TEST_BIRTH_DATA['latitude'],
        longitude=TEST_BIRTH_DATA['longitude'],
        ayanamsa_id=TEST_BIRTH_DATA['ayanamsa'],
        house_system_id=TEST_BIRTH_DATA['house_system'],
        include_panchang=False,
    )
    resp = calculate_medical_astrology(horoscope=horoscope)
    assert resp.max_heindel_compendium is not None
    heindel = resp.max_heindel_compendium

    # 1. Treatise metadata & 19 Injunctions
    assert 'Astro-Diagnosis' in heindel.book_title
    assert 'Max Heindel' in heindel.authors
    assert len(heindel.healer_injunctions) == 19
    assert heindel.healer_injunctions[0]['id'] == '1'
    assert 'death' in heindel.healer_injunctions[0]['rule_en'].lower()

    # 2. 12 Sign Anatomies with Manilius & Heindel
    assert len(heindel.signs_anatomy) == 12
    aries = heindel.signs_anatomy[0]
    assert aries.sign_name_en == 'Aries'
    assert 'Head' in aries.manilius_rulership

    # 3. 10 Planetary Physiologies & Sense Organs
    assert len(heindel.planets_physiology) == 10
    assert len(heindel.sense_organs_affinities) == 4

    # 4. 3 Vicious Circles
    assert len(heindel.vicious_circles) == 3
    cross_names = {c.cross_name for c in heindel.vicious_circles}
    assert any('Cardinal' in name for name in cross_names)
    assert any('Fixed' in name for name in cross_names)
    assert any('Mutable' in name for name in cross_names)

    # 5. Hand & Nail Diagnosis
    assert len(heindel.nail_and_hand_diagnosis) >= 7

    # 6. Planetary Antidotes & Nebular Spots
    assert len(heindel.planetary_antidotes) == 2
    assert len(heindel.nebular_spots) == 3

    # 7. 43 Golden Aphorisms
    assert len(heindel.aphorisms) == 43
    assert 'iron' in heindel.aphorisms[0].aphorism_en.lower() or 'moon' in heindel.aphorisms[0].aphorism_en.lower()

    # 8. Matched Rules
    assert len(heindel.matched_rules) == 12
    for r in heindel.matched_rules:
        assert r.id.startswith('heindel_')


def test_jane_ridder_patrick_compendium_full():
    horoscope = calculate_full_horoscope(
        birth_date=TEST_BIRTH_DATA['birth_date'],
        birth_time=TEST_BIRTH_DATA['birth_time'],
        timezone_str=TEST_BIRTH_DATA['timezone'],
        latitude=TEST_BIRTH_DATA['latitude'],
        longitude=TEST_BIRTH_DATA['longitude'],
        ayanamsa_id=TEST_BIRTH_DATA['ayanamsa'],
        house_system_id=TEST_BIRTH_DATA['house_system'],
        include_panchang=False,
    )
    resp = calculate_medical_astrology(horoscope=horoscope)
    assert resp.jane_ridder_patrick_compendium is not None
    jrp = resp.jane_ridder_patrick_compendium

    # 1. Treatise metadata & Framework
    assert 'Jane Ridder-Patrick' in jrp.author
    assert 'A Handbook of Medical Astrology' in jrp.book_title
    assert len(jrp.alphabet_framework) >= 5

    # 2. Arabian Parts
    assert jrp.arabian_parts.part_of_sickness_coord is not None
    assert jrp.arabian_parts.part_of_surgery_coord is not None
    assert jrp.arabian_parts.part_of_death_coord is not None
    assert 'Taurus' in jrp.arabian_parts.part_of_sickness_coord or len(jrp.arabian_parts.part_of_sickness_coord) > 3

    # 3. Decumbiture & Strictures
    dec = jrp.decumbiture
    assert dec.asc_stricture_note is not None
    assert isinstance(dec.moon_in_via_combusta, bool)
    assert dec.critical_days_cycle_en is not None

    # 4. Three Crosses Reflex Dynamics
    assert len(jrp.three_crosses) == 3
    cross_names = [c['cross'] for c in jrp.three_crosses]
    assert any('Cardinal' in n for n in cross_names)
    assert any('Fixed' in n for n in cross_names)
    assert any('Mutable' in n for n in cross_names)

    # 5. Elemental Analysis
    elem = jrp.elemental_analysis
    assert elem.dominant_element in ['Fire', 'Earth', 'Air', 'Water']
    assert elem.fire_count >= 0
    assert elem.earth_count >= 0
    assert elem.air_count >= 0
    assert elem.water_count >= 0

    # 6. Biochemic Cell Salts (12)
    assert len(jrp.cell_salts) == 12
    assert jrp.cell_salts[0].sign == 'Aries'
    assert 'Kali' in jrp.cell_salts[0].abbreviation or 'phosphate' in jrp.cell_salts[0].cell_salt.lower()

    # 7. Bach Flower Remedies (12)
    assert len(jrp.bach_flowers) == 12
    assert jrp.bach_flowers[0].sign == 'Aries'
    assert 'Impatiens' in jrp.bach_flowers[0].flower_remedy

    # 8. Acupuncture Meridians (12)
    assert len(jrp.acupuncture_meridians) == 12
    assert jrp.acupuncture_meridians[0].sign == 'Aries'
    assert len(jrp.acupuncture_meridians[0].meridian) > 0

    # 9. Culpeper's 7 Rules & Stages of Therapy
    assert len(jrp.culpeper_therapeutic_rules) == 7
    assert len(jrp.stages_of_therapy) == 3

    # 10. Matched Classical Rules (24 rules registry)
    assert len(jrp.matched_rules) == 24
    for r in jrp.matched_rules:
        assert r.id.startswith('jrp_')
        assert r.remedy_en is not None
        assert r.remedy_ta is not None


def test_heinrich_daath_compendium_full():
    """Verify Heinrich Däath Medical Astrology Compendium comprehensive functionality."""
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
    resp = calculate_medical_astrology(horoscope=horoscope)
    assert resp.heinrich_daath_compendium is not None
    daath = resp.heinrich_daath_compendium

    # 1. Treatise Metadata
    assert "Heinrich Däath" in daath.author
    assert "Medical Astrology" in daath.book_title
    assert "Jatromathematics" in daath.historical_foundation
    assert len(daath.core_philosophy_en) > 50
    assert len(daath.core_philosophy_ta) > 50

    # 2. 12 Sign Anatomical Rulerships
    assert len(daath.signs_anatomy) == 12
    assert daath.signs_anatomy[0].sign_name_en == "Aries"
    assert "Cranium" in daath.signs_anatomy[0].principal_bones
    # Check kidney distinction on Libra and Scorpio
    libra_sign = next(s for s in daath.signs_anatomy if s.sign_name_en == "Libra")
    scorpio_sign = next(s for s in daath.signs_anatomy if s.sign_name_en == "Scorpio")
    assert libra_sign.kidney_pelvis_distinction is not None
    assert "secreting" in libra_sign.kidney_pelvis_distinction.lower() or "filtering" in libra_sign.kidney_pelvis_distinction.lower()
    assert scorpio_sign.kidney_pelvis_distinction is not None
    assert "pelvis" in scorpio_sign.kidney_pelvis_distinction.lower()

    # 3. 9 Planets Biodynamics & Materia Medica
    assert len(daath.planets_biodynamics) == 9
    sun_bio = next(p for p in daath.planets_biodynamics if p.planet == "Sun")
    assert "Dwadasatma" in sun_bio.esoteric_title
    assert "expansion" in sun_bio.biodynamic_motion.lower()
    assert len(sun_bio.typical_plants) > 0
    assert len(sun_bio.typical_drugs) > 0
    assert "Gold" in sun_bio.metals_minerals

    mars_bio = next(p for p in daath.planets_biodynamics if p.planet == "Mars")
    assert "centrifugal" in mars_bio.biodynamic_motion.lower()
    assert "Iron" in mars_bio.metals_minerals

    saturn_bio = next(p for p in daath.planets_biodynamics if p.planet == "Saturn")
    assert "centripetal" in saturn_bio.biodynamic_motion.lower()
    assert "Lead" in saturn_bio.metals_minerals

    # 4. Temperaments & Quadruplicities
    temp = daath.temperaments_and_crosses
    assert temp["dominant_temperament"] is not None
    assert len(temp["temperament_definitions"]) == 4
    assert len(temp["cross_definitions"]) == 3

    # 5. Antipathic Therapeutics (Contraria Contrariis Curantur)
    assert len(daath.antipathic_therapeutics) == 4
    sat_therapy = next(t for t in daath.antipathic_therapeutics if "Saturnine" in t.category)
    assert "Mars" in sat_therapy.curative_planetary_remedy

    # 6. Seven Ages of Man (Planetary Life-Periods)
    assert len(daath.seven_ages_of_man) == 7
    assert daath.seven_ages_of_man[0].planet == "Moon"
    assert daath.seven_ages_of_man[0].start_age == 0
    assert daath.seven_ages_of_man[0].end_age == 4
    assert any(p.is_native_current_age for p in daath.seven_ages_of_man)

    # 7. Decumbiture & Cycles
    dec = daath.decumbiture_and_cycles
    assert len(dec.lunar_critical_cycles) == 3
    assert len(dec.lunar_phases_metabolism) == 4
    assert "Uranus" in dec.climacteric_seven_year_law

    # 8. Strength Evaluation (5 dimensions)
    strength = daath.strength_evaluation
    assert "Anabolic" in strength.drikbalam_aspect_summary
    assert len(strength.nisargikabalam_mutual_receptions) > 0
    assert "Angles" in strength.mundane_strength_summary
    assert "Retrograde" in strength.motional_strength_summary
    assert "Hexis" in strength.directional_hexis_vs_diathesis

    # 9. 16 Matched Classical Rules
    assert len(daath.matched_rules) == 16
    for r in daath.matched_rules:
        assert r.id.startswith("daath_")
        assert r.remedy_en is not None
        assert r.remedy_ta is not None
