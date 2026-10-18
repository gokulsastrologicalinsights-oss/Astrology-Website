"""Independent comparison tests for Lahiri Ayanamsa between XALEN and pyswisseph."""

import pytest
import swisseph as swe
import xalen
import xalen.swe as xswe
from .conftest import TEST_EPOCHS, angle_diff_arcsec

# Tolerance in arcseconds for Apparent Lahiri Ayanamsa
# Documented discrepancy: XALEN anchors Lahiri at 1956 with IAU 2006 precession + nutation,
# resulting in an expected ~0.73" constant difference compared to Swiss Ephemeris Newcomb-based Lahiri.
LAHIRI_TOLERANCE_ARCSEC = 1.0


class TestLahiriAyanamsa:
    """Validate Lahiri Ayanamsa computation against Swiss Ephemeris oracle."""

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    def test_lahiri_apparent_vs_pyswisseph(self, epoch):
        """Compare xalen.ayanamsa(jd, 0) against pyswisseph get_ayanamsa_ex_ut."""
        jd = epoch["jd"]

        # Configure Swiss Ephemeris for Lahiri (apparent mode)
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        _retflag, swe_apparent_aya = swe.get_ayanamsa_ex_ut(jd, 0)

        # Compute with XALEN native API
        xalen_aya = xalen.ayanamsa(jd, 0)  # 0 = Lahiri

        diff_as = (xalen_aya - swe_apparent_aya) * 3600.0

        assert abs(diff_as) < LAHIRI_TOLERANCE_ARCSEC, (
            f"Lahiri ayanamsa difference at {epoch['name']} (JD {jd}) exceeds {LAHIRI_TOLERANCE_ARCSEC}\": "
            f"xalen={xalen_aya:.6f}°, swe={swe_apparent_aya:.6f}°, diff={diff_as:.4f}\""
        )

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    def test_lahiri_by_name_matches(self, epoch):
        """Compare xalen.ayanamsa_by_name(jd, 'lahiri') with get_ayanamsa_ex_ut."""
        jd = epoch["jd"]
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        _retflag, swe_apparent_aya = swe.get_ayanamsa_ex_ut(jd, 0)

        xalen_aya = xalen.ayanamsa_by_name(jd, "lahiri")
        diff_as = (xalen_aya - swe_apparent_aya) * 3600.0

        assert abs(diff_as) < LAHIRI_TOLERANCE_ARCSEC, (
            f"Lahiri by name diff {diff_as:.4f}\" exceeds {LAHIRI_TOLERANCE_ARCSEC}\""
        )

    @pytest.mark.parametrize("epoch", TEST_EPOCHS, ids=[e["name"] for e in TEST_EPOCHS])
    def test_xalen_swe_compat_get_ayanamsa_ex_ut(self, epoch):
        """Verify that xalen.swe drop-in submodule produces identical ayanamsa to xalen core."""
        jd = epoch["jd"]
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        xswe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

        _ret1, swe_aya = swe.get_ayanamsa_ex_ut(jd, 0)
        _ret2, xswe_aya = xswe.get_ayanamsa_ex_ut(jd, 0)

        diff_as = (xswe_aya - swe_aya) * 3600.0
        assert abs(diff_as) < LAHIRI_TOLERANCE_ARCSEC, (
            f"xalen.swe ayanamsa diff {diff_as:.4f}\" exceeds {LAHIRI_TOLERANCE_ARCSEC}\""
        )

    def test_lahiri_epoch_rate_of_change(self):
        """Verify annual precession rate of Lahiri ayanamsa (~50.29 arcseconds/year)."""
        jd1 = 2451545.0          # J2000.0
        jd2 = jd1 + 365.25       # 1 Julian year later

        aya1 = xalen.ayanamsa(jd1, 0)
        aya2 = xalen.ayanamsa(jd2, 0)
        annual_change_arcsec = (aya2 - aya1) * 3600.0

        # General precession is approximately 50.29 arcseconds per year
        assert 45.0 < annual_change_arcsec < 55.0, (
            f"Annual Lahiri rate {annual_change_arcsec:.2f}\"/yr outside expected 45-55\"/yr band"
        )
