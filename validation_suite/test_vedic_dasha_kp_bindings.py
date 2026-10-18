"""Unit and integration tests for the newly exposed Vimshottari Dasa and KP Python bindings."""

import pytest
import math
import xalen

J2000_JD = 2451545.0


# ============================================================================
# 1. Vimshottari Dasa Tests
# ============================================================================

class TestVimshottariDashaBindings:
    """Validate xalen.vimshottari_dasha Python binding."""

    def test_vimshottari_dasha_import_and_signature(self):
        """Verify vimshottari_dasha is callable and exported in xalen."""
        assert hasattr(xalen, "vimshottari_dasha")
        assert callable(xalen.vimshottari_dasha)

    def test_vimshottari_dasha_boundary_ashwini(self):
        """Verify Dasa starting at 0° (Ashwini nakshatra boundary)."""
        periods = xalen.vimshottari_dasha(0.0, J2000_JD, depth=1)
        assert len(periods) == 9

        # First lord at 0° Ashwini must be Ketu
        first = periods[0]
        assert first["lord"] == "Ketu"
        assert first["level"] == "Mahadasha"
        assert first["start_jd"] == J2000_JD
        assert abs(first["duration_years"] - 7.0) < 1e-4

        # Total 120 years from exact boundary
        total_days = sum(p["duration_days"] for p in periods)
        total_years = total_days / 365.25
        assert abs(total_years - 120.0) < 0.01

        # Correct lord sequence
        expected_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        actual_lords = [p["lord"] for p in periods]
        assert actual_lords == expected_lords

    def test_vimshottari_dasha_balance_mid_nakshatra(self):
        """Verify dasha balance when Moon is mid-nakshatra (e.g. 5.0° into Ashwini)."""
        periods = xalen.vimshottari_dasha(5.0, J2000_JD, depth=1)
        first = periods[0]
        assert first["lord"] == "Ketu"
        # Ashwini is 0 to 13.333°. At 5.0°, elapsed is 5/13.333 = 37.5%, remaining is 62.5% of 7 years = ~4.375 years
        assert 3.5 < first["duration_years"] < 5.0
        # Total cycle is less than 120 years because of elapsed birth balance
        total_years = sum(p["duration_days"] for p in periods) / 365.25
        assert 115.0 < total_years < 120.0

    @pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
    def test_vimshottari_dasha_nesting_depths(self, depth):
        """Verify hierarchical nesting depth from 1 (Maha) to 5 (Prana)."""
        periods = xalen.vimshottari_dasha(0.0, J2000_JD, depth=depth)
        assert len(periods) == 9

        first = periods[0]
        assert first["level"] == "Mahadasha"

        if depth == 1:
            assert len(first["sub_periods"]) == 0
        elif depth >= 2:
            antars = first["sub_periods"]
            assert len(antars) == 9
            assert antars[0]["level"] == "Antardasha"
            # Antardashas must sum to parent Mahadasha duration
            antar_sum = sum(a["duration_days"] for a in antars)
            assert abs(antar_sum - first["duration_days"]) < 0.01

            if depth >= 3:
                pratyantars = antars[0]["sub_periods"]
                assert len(pratyantars) == 9
                assert pratyantars[0]["level"] == "Pratyantardasha"
                pratyantar_sum = sum(pr["duration_days"] for pr in pratyantars)
                assert abs(pratyantar_sum - antars[0]["duration_days"]) < 0.01

                if depth >= 4:
                    sookshmas = pratyantars[0]["sub_periods"]
                    assert len(sookshmas) == 9
                    assert sookshmas[0]["level"] == "Sookshmadasha"

                    if depth == 5:
                        pranas = sookshmas[0]["sub_periods"]
                        assert len(pranas) == 9
                        assert pranas[0]["level"] == "Pranadasha"
                        # Pranadasha is terminal: has no children
                        assert len(pranas[0]["sub_periods"]) == 0

    def test_vimshottari_dasha_invalid_depth(self):
        """Reject depths outside 1-5."""
        with pytest.raises(ValueError, match="depth must be between 1 and 5"):
            xalen.vimshottari_dasha(0.0, J2000_JD, depth=0)
        with pytest.raises(ValueError, match="depth must be between 1 and 5"):
            xalen.vimshottari_dasha(0.0, J2000_JD, depth=6)

    def test_vimshottari_dasha_invalid_non_finite_inputs(self):
        """Reject NaN and infinite inputs with ValueError."""
        with pytest.raises(ValueError, match="moon_sidereal_deg must be a finite number"):
            xalen.vimshottari_dasha(float("nan"), J2000_JD, depth=2)
        with pytest.raises(ValueError, match="moon_sidereal_deg must be a finite number"):
            xalen.vimshottari_dasha(float("inf"), J2000_JD, depth=2)
        with pytest.raises(ValueError, match="jd must be a finite number"):
            xalen.vimshottari_dasha(0.0, float("nan"), depth=2)
        with pytest.raises(ValueError, match="jd must be a finite number"):
            xalen.vimshottari_dasha(0.0, float("-inf"), depth=2)

    def test_vimshottari_dasha_longitude_normalization(self):
        """Verify longitude wrapping for negative or >360° inputs."""
        p1 = xalen.vimshottari_dasha(0.0, J2000_JD, depth=1)
        p2 = xalen.vimshottari_dasha(360.0, J2000_JD, depth=1)
        p3 = xalen.vimshottari_dasha(720.0, J2000_JD, depth=1)
        p4 = xalen.vimshottari_dasha(-360.0, J2000_JD, depth=1)

        assert p1[0]["lord"] == p2[0]["lord"] == p3[0]["lord"] == p4[0]["lord"]
        assert abs(p1[0]["duration_days"] - p2[0]["duration_days"]) < 1e-6


# ============================================================================
# 2. KP Position & 249 Divisions Tests
# ============================================================================

class TestKpPositionBindings:
    """Validate xalen.kp_position and xalen.kp_number_to_sign."""

    def test_kp_position_import_and_signature(self):
        """Verify kp_position is callable and exported."""
        assert hasattr(xalen, "kp_position")
        assert callable(xalen.kp_position)

    def test_kp_position_zero_degrees(self):
        """At 0.0° (Aries 0°): Mars sign lord, Ketu star lord, Ketu sub lord, KP #1."""
        kp = xalen.kp_position(0.0)
        assert kp["sign_lord"] == "Mars"
        assert kp["star_lord"] == "Ketu"
        assert kp["sub_lord"] == "Ketu"
        assert kp["sub_sub_lord"] == "Ketu"
        assert kp["kp_number"] == 1

    def test_kp_position_sign_boundaries(self):
        """Spot check KP positions across sign boundaries."""
        # 30.0° = Taurus 0° (sign lord Venus, star lord Sun)
        kp_30 = xalen.kp_position(30.0)
        assert kp_30["sign_lord"] == "Venus"
        assert kp_30["star_lord"] == "Sun"

        # 90.0° = Cancer 0° (sign lord Moon, star lord Jupiter)
        kp_90 = xalen.kp_position(90.0)
        assert kp_90["sign_lord"] == "Moon"
        assert kp_90["star_lord"] == "Jupiter"

        # 359.99° = Pisces end (sign lord Jupiter, star lord Mercury, KP #249)
        kp_last = xalen.kp_position(359.99)
        assert kp_last["sign_lord"] == "Jupiter"
        assert kp_last["kp_number"] == 249

    def test_kp_position_invalid_input(self):
        """Reject non-finite degrees."""
        with pytest.raises(ValueError, match="sidereal_deg must be a finite number"):
            xalen.kp_position(float("nan"))
        with pytest.raises(ValueError, match="sidereal_deg must be a finite number"):
            xalen.kp_position(float("inf"))

    def test_kp_number_to_sign_valid(self):
        """Verify 1-based sign mapping for KP numbers."""
        assert xalen.kp_number_to_sign(1) == 1    # Aries
        assert xalen.kp_number_to_sign(249) == 12 # Pisces

    def test_kp_number_to_sign_invalid(self):
        """Reject KP numbers outside 1..249."""
        with pytest.raises(ValueError, match="kp_number must be between 1 and 249"):
            xalen.kp_number_to_sign(0)
        with pytest.raises(ValueError, match="kp_number must be between 1 and 249"):
            xalen.kp_number_to_sign(250)


# ============================================================================
# 3. KP Cuspal Analysis & Significators Tests
# ============================================================================

class TestKpCuspalAndSignificatorBindings:
    """Validate xalen.kp_cuspal_analysis and xalen.kp_significators."""

    @pytest.fixture
    def sample_chart_data(self):
        cusps = [i * 30.0 for i in range(12)]
        planets = {
            "Sun": 15.0,      # House 1 (Aries)
            "Moon": 65.0,     # House 3 (Gemini)
            "Mars": 280.0,    # House 10 (Capricorn)
            "Mercury": 45.0,  # House 2 (Taurus)
            "Jupiter": 190.0, # House 7 (Libra)
            "Venus": 310.0,   # House 11 (Aquarius)
            "Saturn": 130.0,  # House 5 (Leo)
            "Rahu": 95.0,     # House 4 (Cancer)
            "Ketu": 275.0,    # House 10 (Capricorn)
        }
        return cusps, planets

    def test_cuspal_analysis_valid(self, sample_chart_data):
        """Verify cuspal analysis on standard chart."""
        cusps, planets = sample_chart_data
        res = xalen.kp_cuspal_analysis(cusps, planets)
        assert len(res) == 12

        for i, c in enumerate(res):
            assert c["house"] == i + 1
            assert abs(c["cusp_deg"] - cusps[i]) < 1e-4
            assert c["sign_lord"] in ["Mars", "Venus", "Mercury", "Moon", "Sun", "Jupiter", "Saturn"]
            assert c["promise"] in ["Positive", "Negative", "Mixed"]

    def test_cuspal_analysis_supports_tuple_list(self, sample_chart_data):
        """Verify planets can be passed as list of (planet, deg) tuples."""
        cusps, planets_dict = sample_chart_data
        planets_list = [(k, v) for k, v in planets_dict.items()]
        res = xalen.kp_cuspal_analysis(cusps, planets_list)
        assert len(res) == 12

    def test_cuspal_analysis_supports_integer_planet_ids(self):
        """Verify planets can be passed with integer body IDs (0=Sun, 1=Moon, etc.)."""
        cusps = [i * 30.0 for i in range(12)]
        planets = [(0, 15.0), (1, 65.0), (4, 280.0)]
        res = xalen.kp_cuspal_analysis(cusps, planets)
        assert len(res) == 12

    def test_cuspal_analysis_invalid_cusp_length(self, sample_chart_data):
        """Reject cusp lists with other than 12 elements."""
        _, planets = sample_chart_data
        with pytest.raises(ValueError, match="cusps must contain exactly 12 house cusp values"):
            xalen.kp_cuspal_analysis([0.0, 30.0], planets)
        with pytest.raises(ValueError, match="cusps must contain exactly 12 house cusp values"):
            xalen.kp_cuspal_analysis([i * 25.0 for i in range(14)], planets)

    def test_cuspal_analysis_invalid_planet_name(self, sample_chart_data):
        """Reject unknown planet names with ValueError."""
        cusps, _ = sample_chart_data
        with pytest.raises(ValueError, match="unknown planet name"):
            xalen.kp_cuspal_analysis(cusps, [("Krypton", 15.0)])

    def test_significators_valid(self, sample_chart_data):
        """Verify KP significator computation."""
        cusps, planets = sample_chart_data
        sigs = xalen.kp_significators(cusps, planets)
        assert len(sigs) == 9  # 9 Vedic grahas

        for s in sigs:
            assert s["planet"] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            assert isinstance(s["signified_houses"], list)
            assert isinstance(s["strength_order"], list)
            for entry in s["strength_order"]:
                assert 1 <= entry["house"] <= 12
                assert entry["type"] in ["StarLord", "Occupant", "Owner", "Aspecting"]
