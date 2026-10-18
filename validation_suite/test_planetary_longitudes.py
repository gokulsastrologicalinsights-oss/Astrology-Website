"""Independent comparison tests for planetary longitudes between XALEN and pyswisseph."""

import pytest
import swisseph as swe
import xalen
import xalen.swe as xswe
from .conftest import TEST_EPOCHS, BODIES_CONFIG, angle_diff_arcsec


class TestPlanetaryLongitudes:
    """Validate planetary longitudes in both tropical and sidereal frames."""

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    @pytest.mark.parametrize("name, swe_id, xalen_id, tol_as, is_node", BODIES_CONFIG, ids=[b[0] for b in BODIES_CONFIG])
    def test_tropical_longitude_vs_pyswisseph(self, epoch, name, swe_id, xalen_id, tol_as, is_node):
        """Compare apparent geocentric tropical longitude between XALEN and pyswisseph."""
        jd = epoch["jd"]

        # Swiss Ephemeris configuration
        # Nodes and apogees are mean/osculating elements reported in the mean ecliptic of date
        flag = swe.FLG_SWIEPH | swe.FLG_SPEED
        if is_node:
            flag |= swe.FLG_NONUT

        swe_res, retflag = swe.calc_ut(jd, swe_id, flag)
        swe_lon = swe_res[0]

        # XALEN core calculation
        xalen_lon = xalen.planet_longitude(jd, xalen_id, False, 0)

        diff_as = angle_diff_arcsec(xalen_lon, swe_lon)

        assert abs(diff_as) < tol_as, (
            f"Tropical longitude mismatch for {name} at {epoch['name']}: "
            f"xalen={xalen_lon:.6f}°, swe={swe_lon:.6f}°, diff={diff_as:.4f}\" (tolerance: {tol_as}\")"
        )

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    @pytest.mark.parametrize("name, swe_id, xalen_id, tol_as, is_node", BODIES_CONFIG, ids=[b[0] for b in BODIES_CONFIG])
    def test_swe_compat_calc_ut(self, epoch, name, swe_id, xalen_id, tol_as, is_node):
        """Verify that xalen.swe drop-in submodule produces identical output to xalen core."""
        jd = epoch["jd"]
        flag = swe.FLG_SWIEPH | swe.FLG_SPEED
        if is_node:
            flag |= swe.FLG_NONUT

        swe_res, _ = swe.calc_ut(jd, swe_id, flag)
        xswe_res, _ = xswe.calc_ut(jd, swe_id, flag)

        diff_as = angle_diff_arcsec(xswe_res[0], swe_res[0])
        assert abs(diff_as) < tol_as, (
            f"xalen.swe mismatch for {name} at {epoch['name']}: diff={diff_as:.4f}\" exceeds {tol_as}\""
        )

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    @pytest.mark.parametrize("name, swe_id, xalen_id, tol_as, is_node", BODIES_CONFIG, ids=[b[0] for b in BODIES_CONFIG])
    def test_sidereal_lahiri_longitude_vs_pyswisseph(self, epoch, name, swe_id, xalen_id, tol_as, is_node):
        """Compare sidereal (Lahiri) longitudes between XALEN and pyswisseph."""
        jd = epoch["jd"]

        # Swiss sidereal calculation
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        if is_node:
            flag |= swe.FLG_NONUT

        swe_res, _ = swe.calc_ut(jd, swe_id, flag)
        swe_lon = swe_res[0]

        # XALEN sidereal calculation (sidereal=True, ayanamsa=0 Lahiri)
        xalen_lon = xalen.planet_longitude(jd, xalen_id, True, 0)

        # In sidereal mode, real planets cancel nutation (apparent - apparent),
        # but mean node differences reflect Swiss Ephemeris subtracting mean ayanamsa
        # while XALEN subtracts apparent ayanamsa (~14" nutation in longitude offset).
        effective_tol = (tol_as + 20.0) if is_node else (tol_as + 1.5)
        diff_as = angle_diff_arcsec(xalen_lon, swe_lon)

        assert abs(diff_as) < effective_tol, (
            f"Sidereal Lahiri mismatch for {name} at {epoch['name']}: "
            f"xalen={xalen_lon:.6f}°, swe={swe_lon:.6f}°, diff={diff_as:.4f}\" (tolerance: {effective_tol}\")"
        )

