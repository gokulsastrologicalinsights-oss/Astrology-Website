"""Unit and integration test suite for the Unified Classical Dosha Engine.

Validates:
1. Kuja / Manglik Dosha across Lagna, Moon, and Venus with 8 classical cancellations & 2nd house toggle.
2. Kaal Sarp Dosha (Full, Partial, Absent enclosure, Savya/Apasavya, 12 named subtypes, mitigations).
3. Sadesati, Kantaka, and Ashtama Shani with XALEN transit calculation and BAV bindus modifier.
4. Additional classical doshas (Pitru, Guru Chandal, Shrapit, Grahan Sun/Moon).
5. FastAPI endpoint POST /api/v1/vedic/doshas.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.dosha_engine import (
    DoshaChartContext,
    evaluate_kuja_dosha,
    evaluate_kaal_sarp_dosha,
    evaluate_sadesati,
    evaluate_additional_doshas,
    evaluate_pitru_dosha,
    evaluate_guru_chandal_dosha,
    evaluate_shrapit_dosha,
    evaluate_grahan_dosha,
    calculate_unified_doshas,
    SEVEN_GRAHAS,
)

client = TestClient(app)


def build_planet(name, sign_idx, deg=15.0, lon=None, is_retro=False):
    """Helper to build planet dict."""
    full_lon = lon if lon is not None else float((sign_idx - 1) * 30 + deg)
    return {
        "name": name,
        "sign_index": sign_idx,
        "longitude": full_lon,
        "degree_in_sign": deg,
        "is_retrograde": is_retro,
    }


# ===========================================================================
# 1. Kuja Dosha Tests
# ===========================================================================

def test_kuja_dosha_from_lagna_active():
    """Mars in 7th house from Lagna without cancellations triggers Kuja Dosha."""
    planets = [
        build_planet("Mars", 7),       # In Libra (sign 7)
        build_planet("Moon", 3),       # Gemini (sign 3) - 5th from Moon (non-kuja)
        build_planet("Venus", 5),      # Leo (sign 5) - 3rd from Venus (non-kuja)
        build_planet("Jupiter", 2),    # Taurus (sign 2) - aspects 6, 8, 10 (no aspect on 7)
        build_planet("Saturn", 12),    # Pisces (sign 12) - aspects 2, 6, 9 (no aspect on 7)
        build_planet("Sun", 8),
        build_planet("Mercury", 8),
        build_planet("Rahu", 9),
        build_planet("Ketu", 3),
    ]
    # Aries Lagna (sign 1) -> Mars in Libra is 7th house
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kuja_dosha(ctx, include_2nd_house=True)

    assert res.is_present is True
    assert res.is_cancelled is False
    assert res.details_by_reference["Lagna"].has_dosha is True
    assert res.details_by_reference["Lagna"].effective_intensity_percent == 100.0
    assert res.severity in ("Moderate", "High")


def test_kuja_dosha_2nd_house_toggle():
    """Mars in 2nd house triggers in South Indian mode, but is absent in North Indian mode."""
    planets = [
        build_planet("Mars", 2),       # In Taurus (sign 2)
        build_planet("Moon", 9),       # Sagittarius
        build_planet("Venus", 10),     # Capricorn
        build_planet("Jupiter", 5),
        build_planet("Saturn", 6),
        build_planet("Sun", 8),
        build_planet("Mercury", 8),
        build_planet("Rahu", 11),
        build_planet("Ketu", 5),
    ]
    # Aries Lagna -> Mars in Taurus is 2nd house
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)

    # South Indian convention includes 2nd house
    res_south = evaluate_kuja_dosha(ctx, include_2nd_house=True)
    assert res_south.details_by_reference["Lagna"].has_dosha is True

    # North Indian convention excludes 2nd house
    res_north = evaluate_kuja_dosha(ctx, include_2nd_house=False)
    assert res_north.details_by_reference["Lagna"].has_dosha is False


def test_kuja_cancellation_own_sign():
    """Mars in 1st house in Aries (own sign) cancels Kuja Dosha per BPHS Ch. 81."""
    planets = [
        build_planet("Mars", 1),       # Aries 1st house
        build_planet("Moon", 5),
        build_planet("Venus", 6),
        build_planet("Jupiter", 11),
        build_planet("Saturn", 12),
        build_planet("Sun", 9),
        build_planet("Mercury", 10),
        build_planet("Rahu", 3),
        build_planet("Ketu", 9),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kuja_dosha(ctx)

    lagna_detail = res.details_by_reference["Lagna"]
    assert lagna_detail.has_dosha is True
    assert lagna_detail.is_cancelled is True
    assert lagna_detail.effective_intensity_percent == 0.0
    assert any("own sign" in r.lower() for r in lagna_detail.cancellation_reasons)


def test_kuja_cancellation_exaltation():
    """Mars in Capricorn (exaltation) cancels Kuja Dosha."""
    planets = [
        build_planet("Mars", 10),      # Capricorn 4th house for Libra Lagna
        build_planet("Moon", 5),
        build_planet("Venus", 6),
        build_planet("Jupiter", 2),
        build_planet("Saturn", 12),
        build_planet("Sun", 9),
        build_planet("Mercury", 9),
        build_planet("Rahu", 1),
        build_planet("Ketu", 7),
    ]
    # Libra Lagna (sign 7) -> Capricorn is 4th house
    ctx = DoshaChartContext(planets, ascendant_sign_idx=7)
    res = evaluate_kuja_dosha(ctx)

    lagna_detail = res.details_by_reference["Lagna"]
    assert lagna_detail.has_dosha is True
    assert lagna_detail.is_cancelled is True
    assert any("exaltation" in r.lower() for r in lagna_detail.cancellation_reasons)


def test_kuja_cancellation_debilitation_in_7th_8th():
    """Mars in Cancer (debilitation) in 8th house cancels Kuja Dosha."""
    planets = [
        build_planet("Mars", 4),       # Cancer
        build_planet("Moon", 11),
        build_planet("Venus", 1),
        build_planet("Jupiter", 2),
        build_planet("Saturn", 12),
        build_planet("Sun", 6),
        build_planet("Mercury", 6),
        build_planet("Rahu", 5),
        build_planet("Ketu", 11),
    ]
    # Sagittarius Lagna (sign 9) -> Cancer is 8th house
    ctx = DoshaChartContext(planets, ascendant_sign_idx=9)
    res = evaluate_kuja_dosha(ctx)

    lagna_detail = res.details_by_reference["Lagna"]
    assert lagna_detail.has_dosha is True
    assert lagna_detail.is_cancelled is True
    assert any("debilitated" in r.lower() for r in lagna_detail.cancellation_reasons)


def test_kuja_cancellation_yogakaraka_cancer_leo():
    """Mars is Yogakaraka for Cancer and Leo Lagnas, cancelling Lagna Kuja Dosha."""
    # Cancer Lagna (sign 4), Mars in 4th house (sign 7 Libra)
    planets = [
        build_planet("Mars", 7),
        build_planet("Moon", 11),
        build_planet("Venus", 1),
        build_planet("Jupiter", 2),
        build_planet("Saturn", 12),
        build_planet("Sun", 6),
        build_planet("Mercury", 6),
        build_planet("Rahu", 5),
        build_planet("Ketu", 11),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=4)
    res = evaluate_kuja_dosha(ctx)

    lagna_detail = res.details_by_reference["Lagna"]
    assert lagna_detail.has_dosha is True
    assert lagna_detail.is_cancelled is True
    assert any("yogakaraka" in r.lower() for r in lagna_detail.cancellation_reasons)


def test_kuja_cancellation_jupiter_aspect():
    """Jupiter casting Parashari aspect on Mars cancels Kuja Dosha."""
    # Mars in 7th house (sign 7) for Aries Lagna (sign 1)
    # Jupiter in sign 3 (Gemini) casts 5th aspect on sign 7 (Gemini -> Cancer -> Leo -> Virgo -> Libra = 5th)
    planets = [
        build_planet("Mars", 7),
        build_planet("Jupiter", 3),    # 5th aspect on Libra
        build_planet("Moon", 2),
        build_planet("Venus", 2),
        build_planet("Saturn", 12),
        build_planet("Sun", 8),
        build_planet("Mercury", 8),
        build_planet("Rahu", 5),
        build_planet("Ketu", 11),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kuja_dosha(ctx)

    lagna_detail = res.details_by_reference["Lagna"]
    assert lagna_detail.has_dosha is True
    assert lagna_detail.is_cancelled is True
    assert any("jupiter" in r.lower() for r in lagna_detail.cancellation_reasons)


def test_kuja_multi_reference_breakdown():
    """Kuja Dosha evaluated independently from Lagna, Moon, and Venus."""
    # Ascendant = 1 (Aries)
    # Moon = 4 (Cancer)
    # Venus = 10 (Capricorn)
    # Mars in sign 1 -> 1st from Lagna (dosha), 10th from Moon (no dosha), 4th from Venus (dosha)
    # But Mars in sign 1 (Aries) is in own sign! So cancelled.
    planets = [
        build_planet("Mars", 1),
        build_planet("Moon", 4),
        build_planet("Venus", 10),
        build_planet("Jupiter", 11),
        build_planet("Saturn", 12),
        build_planet("Sun", 8),
        build_planet("Mercury", 8),
        build_planet("Rahu", 5),
        build_planet("Ketu", 11),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kuja_dosha(ctx)

    assert "Lagna" in res.details_by_reference
    assert "Moon" in res.details_by_reference
    assert "Venus" in res.details_by_reference
    assert res.details_by_reference["Lagna"].has_dosha is True
    assert res.details_by_reference["Moon"].has_dosha is False
    assert res.details_by_reference["Venus"].has_dosha is True
    assert res.is_cancelled is True


# ===========================================================================
# 2. Kaal Sarp Dosha Tests
# ===========================================================================

def test_kaal_sarp_full_savya():
    """All 7 planets situated strictly between Ketu (sign 7) and Rahu (sign 1) in zodiacal order."""
    # Ketu at 180° (Libra, sign 7), Rahu at 0° (Aries, sign 1)
    # Planets in signs 8, 9, 10, 11, 12 (between 180° and 360°)
    planets = [
        build_planet("Rahu", 1, deg=0.0, lon=0.0),
        build_planet("Ketu", 7, deg=0.0, lon=180.0),
        build_planet("Sun", 8, deg=10.0, lon=220.0),
        build_planet("Moon", 9, deg=15.0, lon=255.0),
        build_planet("Mars", 10, deg=20.0, lon=290.0),
        build_planet("Mercury", 8, deg=15.0, lon=225.0),
        build_planet("Jupiter", 11, deg=5.0, lon=305.0),
        build_planet("Venus", 12, deg=10.0, lon=340.0),
        build_planet("Saturn", 10, deg=5.0, lon=275.0),
    ]
    # Aries Lagna -> Rahu in 1st house -> Anant Kaal Sarp
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kaal_sarp_dosha(ctx)

    assert res.is_present is True
    assert res.dosha_type == "Full"
    assert res.subtype_name == "Anant Kaal Sarp"
    assert res.direction == "Savya (Ascending)"
    assert len(res.planets_inside) == 7
    assert len(res.planets_outside) == 0


def test_kaal_sarp_partial_ardha():
    """6 planets enclosed and 1 planet outside forms Partial Kaal Sarp."""
    planets = [
        build_planet("Rahu", 1, deg=0.0, lon=0.0),
        build_planet("Ketu", 7, deg=0.0, lon=180.0),
        build_planet("Sun", 8, deg=10.0, lon=220.0),
        build_planet("Moon", 9, deg=15.0, lon=255.0),
        build_planet("Mars", 10, deg=20.0, lon=290.0),
        build_planet("Mercury", 8, deg=15.0, lon=225.0),
        build_planet("Jupiter", 11, deg=5.0, lon=305.0),
        build_planet("Venus", 12, deg=10.0, lon=340.0),
        build_planet("Saturn", 4, deg=15.0, lon=105.0),  # In Cancer (on the other side)
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kaal_sarp_dosha(ctx)

    assert res.is_present is True
    assert res.dosha_type == "Partial"
    assert "Saturn" in res.planets_outside
    assert len(res.planets_inside) == 6


def test_kaal_sarp_absent():
    """Planets distributed on both sides -> Kaal Sarp Absent."""
    planets = [
        build_planet("Rahu", 1, deg=0.0, lon=0.0),
        build_planet("Ketu", 7, deg=0.0, lon=180.0),
        build_planet("Sun", 2, deg=10.0, lon=40.0),       # Side 1
        build_planet("Moon", 3, deg=15.0, lon=75.0),      # Side 1
        build_planet("Mars", 8, deg=20.0, lon=230.0),     # Side 2
        build_planet("Mercury", 9, deg=15.0, lon=255.0),  # Side 2
        build_planet("Jupiter", 10, deg=5.0, lon=275.0),  # Side 2
        build_planet("Venus", 4, deg=10.0, lon=100.0),    # Side 1
        build_planet("Saturn", 11, deg=5.0, lon=305.0),   # Side 2
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kaal_sarp_dosha(ctx)

    assert res.is_present is False
    assert res.dosha_type == "Absent"
    assert res.subtype_name is None


def test_kaal_sarp_12_subtypes():
    """Subtypes 1 to 12 correctly map to Rahu's house from Lagna."""
    expected_names = [
        "Anant Kaal Sarp", "Kulik Kaal Sarp", "Vasuki Kaal Sarp", "Shankhpal Kaal Sarp",
        "Padma Kaal Sarp", "Mahapadma Kaal Sarp", "Takshak Kaal Sarp", "Karkotak Kaal Sarp",
        "Shankhachood Kaal Sarp", "Ghatak Kaal Sarp", "Vishdhar Kaal Sarp", "Sheshnag Kaal Sarp"
    ]
    # For Lagna = 1, Rahu in sign 1..12 corresponds to houses 1..12
    for h in range(1, 13):
        ketu_sign = ((h - 1 + 6) % 12) + 1
        planets = [
            build_planet("Rahu", h, deg=0.0, lon=(h - 1) * 30.0),
            build_planet("Ketu", ketu_sign, deg=0.0, lon=((h - 1 + 6) % 12) * 30.0),
        ]
        # Place all 7 planets on one side of Rahu
        for idx, g in enumerate(SEVEN_GRAHAS):
            p_lon = ((h - 1) * 30.0 + 10.0 + idx * 20.0) % 360.0
            sign = int(p_lon // 30.0) + 1
            planets.append(build_planet(g, sign, deg=p_lon % 30.0, lon=p_lon))

        ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
        res = evaluate_kaal_sarp_dosha(ctx)
        assert res.subtype_name == expected_names[h - 1]


def test_kaal_sarp_mitigation_kendra_benefic():
    """Benefic in Kendra (Jupiter in 4th) mitigates Kaal Sarp."""
    planets = [
        build_planet("Rahu", 1, deg=0.0, lon=0.0),
        build_planet("Ketu", 7, deg=0.0, lon=180.0),
        build_planet("Sun", 8, deg=10.0, lon=220.0),
        build_planet("Moon", 9, deg=15.0, lon=255.0),
        build_planet("Mars", 10, deg=20.0, lon=290.0),
        build_planet("Mercury", 8, deg=15.0, lon=225.0),
        build_planet("Jupiter", 4, deg=5.0, lon=95.0),    # Exalted in Cancer (4th house for Aries Lagna)
        build_planet("Venus", 12, deg=10.0, lon=340.0),
        build_planet("Saturn", 10, deg=5.0, lon=275.0),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res = evaluate_kaal_sarp_dosha(ctx)

    assert res.is_present is True
    assert res.is_cancelled is True
    assert any("benefic" in r.lower() or "exalted" in r.lower() for r in res.cancellation_reasons)


# ===========================================================================
# 3. Sadesati and Saturn Transit Tests
# ===========================================================================

def test_sadesati_phases_and_offsets():
    """Check Rising, Peak, Setting, Kantaka, Ashtama, and Inactive phases."""
    # Natal Moon in Pisces (sign 12)
    planets = [
        build_planet("Moon", 12),
        build_planet("Sun", 1),
        build_planet("Mars", 2),
        build_planet("Mercury", 3),
        build_planet("Jupiter", 4),
        build_planet("Venus", 5),
        build_planet("Saturn", 6),
        build_planet("Rahu", 7),
        build_planet("Ketu", 1),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)

    # In 2026, Saturn is in Pisces / Aries. Let's test by checking explicit transit dates
    # or evaluating with known ephemeris dates:
    # 2025-01-01: Saturn was in Aquarius (sign 11) -> 12th from Pisces Moon -> Rising Phase!
    res_rising = evaluate_sadesati(ctx, transit_date="2025-01-01", transit_time="12:00:00")
    assert res_rising.phase == "Rising"
    assert res_rising.house_from_moon == 12
    assert res_rising.is_active is True

    # 2026-05-15: Saturn is in Pisces (sign 12) -> 1st from Pisces Moon -> Peak Phase!
    res_peak = evaluate_sadesati(ctx, transit_date="2026-05-15", transit_time="12:00:00")
    assert res_peak.phase == "Peak"
    assert res_peak.house_from_moon == 1
    assert res_peak.is_active is True

    # 2028-06-15: Saturn is in Aries (sign 1) -> 2nd from Pisces Moon -> Setting Phase!
    res_setting = evaluate_sadesati(ctx, transit_date="2028-06-15", transit_time="12:00:00")
    assert res_setting.phase == "Setting"
    assert res_setting.house_from_moon == 2
    assert res_setting.is_active is True

    # 2030-08-15: Saturn is in Taurus (sign 2) -> 3rd from Pisces Moon -> Inactive (None)!
    res_inactive = evaluate_sadesati(ctx, transit_date="2030-08-15", transit_time="12:00:00")
    assert res_inactive.phase == "None"
    assert res_inactive.is_active is False


def test_sadesati_ashtakavarga_bindu_modifier():
    """Saturn's BAV bindus modify transit nature (>= 4 -> Benefic / Constructive, < 3 -> Testing)."""
    planets = [
        build_planet("Moon", 12),
        build_planet("Sun", 1),
        build_planet("Mars", 2),
        build_planet("Mercury", 3),
        build_planet("Jupiter", 4),
        build_planet("Venus", 5),
        build_planet("Saturn", 6),
        build_planet("Rahu", 7),
        build_planet("Ketu", 1),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)

    # High bindus in transit sign (Pisces = 12)
    bav_high = {12: 5}
    res_high = evaluate_sadesati(ctx, transit_date="2026-05-15", saturn_bav_bindus=bav_high)
    assert res_high.saturn_ashtakavarga_bindus == 5
    assert res_high.nature_of_transit == "Benefic / Constructive"

    # Low bindus in transit sign
    bav_low = {12: 2}
    res_low = evaluate_sadesati(ctx, transit_date="2026-05-15", saturn_bav_bindus=bav_low)
    assert res_low.saturn_ashtakavarga_bindus == 2
    assert res_low.nature_of_transit == "Testing / Transformative"


# ===========================================================================
# 4. Additional Classical Dosha Tests
# ===========================================================================

def test_pitru_dosha_active_and_cancelled():
    """Pitru Dosha triggered by Saturn conjoining Sun, cancelled by Jupiter aspect."""
    # Sun and Saturn in Leo (sign 5) -> Sun afflicted by Saturn
    planets_active = [
        build_planet("Sun", 5, deg=12.0),
        build_planet("Saturn", 5, deg=15.0),
        build_planet("Jupiter", 2),   # Taurus - no aspect on Leo
        build_planet("Moon", 1),
        build_planet("Mars", 3),
        build_planet("Mercury", 6),
        build_planet("Venus", 7),
        build_planet("Rahu", 10),
        build_planet("Ketu", 4),
    ]
    ctx_active = DoshaChartContext(planets_active, ascendant_sign_idx=1)
    res_active = evaluate_pitru_dosha(ctx_active)
    # Sun is in own sign (Leo 5) which is a classical cancellation!
    assert res_active.is_present is True
    assert res_active.is_cancelled is True  # cancelled by Sun in own sign Leo

    # Let's test with Sun in Virgo (sign 6, not own sign) with Saturn
    planets_virgo = [
        build_planet("Sun", 6, deg=12.0),
        build_planet("Saturn", 6, deg=15.0),
        build_planet("Jupiter", 8),   # Scorpio (8th house) - no aspect on 6 or 9, 9th lord in dusthana
        build_planet("Moon", 1),
        build_planet("Mars", 3),
        build_planet("Mercury", 7),
        build_planet("Venus", 10),
        build_planet("Rahu", 11),
        build_planet("Ketu", 5),
    ]
    ctx_virgo = DoshaChartContext(planets_virgo, ascendant_sign_idx=1)
    res_virgo = evaluate_pitru_dosha(ctx_virgo)
    assert res_virgo.is_present is True
    assert res_virgo.is_cancelled is False
    assert res_virgo.severity in ("Moderate", "High")


def test_guru_chandal_dosha_orb_and_cancellation():
    """Guru Chandal triggered by Jupiter-Rahu conjunction; cancelled when orb > 10° or exalted."""
    # Close conjunction in Taurus (sign 2, orb 2.0°)
    planets_close = [
        build_planet("Jupiter", 2, deg=10.0),
        build_planet("Rahu", 2, deg=12.0),
        build_planet("Sun", 1),
        build_planet("Moon", 3),
        build_planet("Mars", 4),
        build_planet("Mercury", 5),
        build_planet("Venus", 6),
        build_planet("Saturn", 7),
        build_planet("Ketu", 8),
    ]
    ctx_close = DoshaChartContext(planets_close, ascendant_sign_idx=1)
    res_close = evaluate_guru_chandal_dosha(ctx_close)
    assert res_close.is_present is True
    assert res_close.is_cancelled is False

    # Wide conjunction (orb 15.0° > 10.0°)
    planets_wide = [
        build_planet("Jupiter", 2, deg=2.0),
        build_planet("Rahu", 2, deg=20.0),
        build_planet("Sun", 1),
        build_planet("Moon", 3),
        build_planet("Mars", 4),
        build_planet("Mercury", 5),
        build_planet("Venus", 6),
        build_planet("Saturn", 7),
        build_planet("Ketu", 8),
    ]
    ctx_wide = DoshaChartContext(planets_wide, ascendant_sign_idx=1)
    res_wide = evaluate_guru_chandal_dosha(ctx_wide)
    assert res_wide.is_present is True
    assert res_wide.is_cancelled is True


def test_shrapit_dosha_upachaya_mitigation():
    """Saturn-Rahu in Upachaya house (3rd house) mitigates Shrapit Dosha."""
    # Aries Lagna (1) -> Gemini is 3rd house (Upachaya)
    planets_upachaya = [
        build_planet("Saturn", 3, deg=10.0),
        build_planet("Rahu", 3, deg=12.0),
        build_planet("Jupiter", 8),
        build_planet("Sun", 1),
        build_planet("Moon", 4),
        build_planet("Mars", 5),
        build_planet("Mercury", 6),
        build_planet("Venus", 7),
        build_planet("Ketu", 9),
    ]
    ctx_upachaya = DoshaChartContext(planets_upachaya, ascendant_sign_idx=1)
    res_upachaya = evaluate_shrapit_dosha(ctx_upachaya)
    assert res_upachaya.is_present is True
    assert res_upachaya.is_cancelled is True
    assert any("upachaya" in r.lower() for r in res_upachaya.cancellation_reasons)


def test_grahan_dosha_sun_and_moon():
    """Grahan Dosha triggers when Sun/Moon is within 12° of Rahu/Ketu."""
    # Sun conjoined Rahu within 4° orb
    planets = [
        build_planet("Sun", 3, deg=10.0),
        build_planet("Rahu", 3, deg=13.0),
        build_planet("Moon", 9, deg=15.0),
        build_planet("Ketu", 9, deg=13.0),   # Moon conjoined Ketu within 2° orb
        build_planet("Jupiter", 6),   # Virgo - aspects 10, 12, 2 (no aspect on 3 or 9)
        build_planet("Saturn", 2),
        build_planet("Mars", 4),
        build_planet("Mercury", 5),
        build_planet("Venus", 1),
    ]
    ctx = DoshaChartContext(planets, ascendant_sign_idx=1)
    res_sun = evaluate_grahan_dosha(ctx, "Sun")
    res_moon = evaluate_grahan_dosha(ctx, "Moon")

    assert res_sun.is_present is True
    assert res_moon.is_present is True
    assert res_sun.severity == "High"
    assert res_moon.severity == "High"


# ===========================================================================
# 5. Full Orchestrator and API Integration Tests
# ===========================================================================

def test_calculate_unified_doshas_orchestrator():
    """calculate_unified_doshas returns all 4 sections with complete summary counts."""
    planets = [
        build_planet("Sun", 2, deg=1.0, lon=31.0),
        build_planet("Moon", 11, deg=18.0, lon=318.0),
        build_planet("Mars", 1, deg=14.0, lon=14.0),
        build_planet("Mercury", 1, deg=28.0, lon=28.0),
        build_planet("Jupiter", 3, deg=15.0, lon=75.0),
        build_planet("Venus", 1, deg=6.0, lon=6.0),
        build_planet("Saturn", 10, deg=0.0, lon=270.0),
        build_planet("Rahu", 11, deg=15.0, lon=315.0),
        build_planet("Ketu", 5, deg=15.0, lon=135.0),
    ]
    res = calculate_unified_doshas(
        planets=planets,
        ascendant_sign_idx=5,  # Leo Lagna
        include_2nd_house_in_kuja=True,
        transit_date="2026-05-15",
    )

    assert res.kuja_dosha is not None
    assert res.kaal_sarp_dosha is not None
    assert res.sadesati is not None
    assert len(res.additional_doshas) == 5
    assert res.summary_counts["total_doshas_evaluated"] == 8
    assert "total_active_doshas" in res.summary_counts
    assert "total_cancelled_doshas" in res.summary_counts


def test_doshas_api_endpoint():
    """Test POST /api/v1/vedic/doshas endpoint via TestClient."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
        "house_system": 0,
        "include_2nd_house_in_kuja": True,
        "transit_date": "2026-05-15",
        "transit_time": "12:00:00",
    }
    response = client.post("/api/v1/vedic/doshas", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # Validate top-level keys
    assert "kuja_dosha" in data
    assert "kaal_sarp_dosha" in data
    assert "sadesati" in data
    assert "additional_doshas" in data
    assert "summary_counts" in data

    # Validate Kuja Dosha details
    kd = data["kuja_dosha"]
    assert "details_by_reference" in kd
    assert "Lagna" in kd["details_by_reference"]
    assert "Moon" in kd["details_by_reference"]
    assert "Venus" in kd["details_by_reference"]
    assert "interpretation_tamil" in kd and len(kd["interpretation_tamil"]) > 0

    # Validate Kaal Sarp
    ks = data["kaal_sarp_dosha"]
    assert ks["dosha_type"] in ("Full", "Partial", "Absent")
    assert "interpretation_tamil" in ks and len(ks["interpretation_tamil"]) > 0

    # Validate Sadesati
    sd = data["sadesati"]
    assert sd["phase"] in ("Rising", "Peak", "Setting", "Kantaka", "Ashtama", "None")
    assert "phase_name_tamil" in sd

    # Validate Additional Doshas
    add_doshas = data["additional_doshas"]
    assert len(add_doshas) == 5
    ids = [d["id"] for d in add_doshas]
    assert "pitru_dosha" in ids
    assert "guru_chandal_dosha" in ids
    assert "shrapit_dosha" in ids
    assert "grahan_dosha_sun" in ids
    assert "grahan_dosha_moon" in ids
