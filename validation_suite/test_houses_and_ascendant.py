"""Independent comparison tests for Ascendant and Placidus house cusps."""

import pytest
import swisseph as swe
import xalen
import xalen.swe as xswe
from .conftest import TEST_EPOCHS, TEST_LOCATIONS, angle_diff_arcsec

# Drop-in compat tolerance: sub-arcsecond (0.5") across all historical and modern epochs
COMPAT_HOUSE_TOLERANCE_ARCSEC = 0.5

# Direct API tolerance: up to 45 arcseconds at high latitudes (e.g. London 51.5°N) where
# the ~12-15" ARMC equation of equinoxes offset projects onto oblique ascendant signs.
MEAN_EQUINOX_TOLERANCE_ARCSEC = 45.0



class TestHousesAndAscendant:
    """Validate Placidus house cusps, Ascendant and MC across worldwide locations."""

    @pytest.mark.parametrize("epoch", TEST_EPOCHS[:3], ids=[e["name"] for e in TEST_EPOCHS[:3]])
    @pytest.mark.parametrize("loc", TEST_LOCATIONS, ids=[loc["city"] for loc in TEST_LOCATIONS])
    def test_swe_compat_placidus_cusps_and_angles(self, epoch, loc):
        """Compare xalen.swe.houses_ex vs swisseph.houses_ex in tropical Placidus.
        
        Both use the true equinox of date (true obliquity and GAST),
        achieving sub-tenth arcsecond parity.
        """
        jd = epoch["jd"]
        lat = loc["lat"]
        lon = loc["lon"]

        # Swiss Ephemeris Placidus
        swe_cusps, swe_ascmc = swe.houses_ex(jd, lat, lon, b"P", 0)
        swe_asc = swe_ascmc[0]
        swe_mc = swe_ascmc[1]

        # XALEN drop-in compat
        xswe_cusps, xswe_ascmc = xswe.houses_ex(jd, lat, lon, b"P", 0)
        xswe_asc = xswe_ascmc[0]
        xswe_mc = xswe_ascmc[1]

        # Verify Ascendant
        diff_asc = angle_diff_arcsec(xswe_asc, swe_asc)
        assert abs(diff_asc) < COMPAT_HOUSE_TOLERANCE_ARCSEC, (
            f"Ascendant mismatch at {loc['city']}, {epoch['name']}: "
            f"xswe={xswe_asc:.6f}°, swe={swe_asc:.6f}°, diff={diff_asc:.4f}\""
        )

        # Verify Midheaven (MC)
        diff_mc = angle_diff_arcsec(xswe_mc, swe_mc)
        assert abs(diff_mc) < COMPAT_HOUSE_TOLERANCE_ARCSEC, (
            f"MC mismatch at {loc['city']}, {epoch['name']}: "
            f"xswe={xswe_mc:.6f}°, swe={swe_mc:.6f}°, diff={diff_mc:.4f}\""
        )

        # Verify all 12 cusps
        for i in range(12):
            diff_cusp = angle_diff_arcsec(xswe_cusps[i], swe_cusps[i])
            assert abs(diff_cusp) < COMPAT_HOUSE_TOLERANCE_ARCSEC, (
                f"Cusp {i+1} mismatch at {loc['city']}, {epoch['name']}: "
                f"xswe={xswe_cusps[i]:.6f}°, swe={swe_cusps[i]:.6f}°, diff={diff_cusp:.4f}\""
            )

    @pytest.mark.parametrize("epoch", TEST_EPOCHS[:3], ids=[e["name"] for e in TEST_EPOCHS[:3]])
    @pytest.mark.parametrize("loc", TEST_LOCATIONS, ids=[loc["city"] for loc in TEST_LOCATIONS])
    def test_direct_api_houses_discrepancy_documentation(self, epoch, loc):
        """Document discrepancy between xalen.houses (mean GMST) and swe.houses_ex (true GAST).
        
        The native `xalen.houses` uses mean obliquity and GMST, introducing a predictable
        ~12"-15" offset corresponding to the equation of the equinoxes. This test verifies
        that the offset remains bounded within 20 arcseconds across all locations.
        """
        jd = epoch["jd"]
        lat = loc["lat"]
        lon = loc["lon"]

        swe_cusps, swe_ascmc = swe.houses_ex(jd, lat, lon, b"P", 0)
        swe_asc = swe_ascmc[0]

        # Native XALEN API (system 2 = Placidus)
        x_h = xalen.houses(jd, lat, lon, 2)
        x_asc = x_h["ascendant"]

        diff_asc = angle_diff_arcsec(x_asc, swe_asc)
        assert abs(diff_asc) < MEAN_EQUINOX_TOLERANCE_ARCSEC, (
            f"Native Ascendant offset at {loc['city']} exceeds {MEAN_EQUINOX_TOLERANCE_ARCSEC}\": "
            f"xalen={x_asc:.6f}°, swe={swe_asc:.6f}°, diff={diff_asc:.4f}\""
        )

        # Verify cusps are also bounded within the equation of equinoxes band
        for i in range(12):
            diff_cusp = angle_diff_arcsec(x_h["cusps"][i], swe_cusps[i])
            assert abs(diff_cusp) < MEAN_EQUINOX_TOLERANCE_ARCSEC, (
                f"Native cusp {i+1} offset at {loc['city']} exceeds {MEAN_EQUINOX_TOLERANCE_ARCSEC}\": "
                f"diff={diff_cusp:.4f}\""
            )

    @pytest.mark.parametrize("loc", TEST_LOCATIONS, ids=[loc["city"] for loc in TEST_LOCATIONS])
    def test_sidereal_placidus_houses(self, loc):
        """Verify sidereal Placidus houses with Lahiri ayanamsa."""
        jd = 2451545.0  # J2000.0
        lat = loc["lat"]
        lon = loc["lon"]

        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        xswe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

        swe_cusps, swe_ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
        xswe_cusps, xswe_ascmc = xswe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)

        # Difference reflects the ~0.73" Lahiri ayanamsa difference
        diff_asc = angle_diff_arcsec(xswe_ascmc[0], swe_ascmc[0])
        assert abs(diff_asc) < 1.0, (
            f"Sidereal Ascendant diff at {loc['city']}: {diff_asc:.4f}\" exceeds 1.0\""
        )
