"""Shared fixtures and utilities for the independent XALEN validation suite."""

import pytest
import math
import swisseph as swe

def angle_diff_deg(a: float, b: float) -> float:
    """Compute the shortest signed angular difference (a - b) in degrees in [-180, 180)."""
    diff = (a - b + 180.0) % 360.0 - 180.0
    return diff

def angle_diff_arcsec(a: float, b: float) -> float:
    """Compute shortest signed angular difference (a - b) in arcseconds."""
    return angle_diff_deg(a, b) * 3600.0


# Standard test epochs (Julian Dates in UT1/UTC)
TEST_EPOCHS = [
    {"name": "J2000.0", "jd": 2451545.0, "desc": "Standard epoch 2000-01-01 12:00:00 UTC"},
    {"name": "Mid-20th Century", "jd": 2433282.5, "desc": "Historical epoch 1950-01-01 00:00:00 UTC"},
    {"name": "Late-20th Century", "jd": 2444239.5, "desc": "Historical epoch 1980-01-01 00:00:00 UTC"},
    {"name": "Modern Epoch", "jd": 2460310.5, "desc": "Contemporary epoch 2024-01-01 00:00:00 UTC"},
    {"name": "Current Timestamp", "jd": 2461331.08985, "desc": "Session epoch 2026-10-17 14:09:23 UTC"},
]

# Standard geographic test locations
TEST_LOCATIONS = [
    {"city": "Chennai", "country": "India", "lat": 13.0827, "lon": 80.2707, "type": "Vedic / Tropical latitude"},
    {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278, "type": "Prime Meridian / High latitude"},
    {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060, "type": "Western hemisphere"},
    {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "type": "Southern hemisphere"},
    {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "type": "Eastern longitude"},
]

# Classical bodies mapped between pyswisseph IDs and XALEN core IDs:
# Tuple: (name, swe_id, xalen_core_id, arcsec_tol_apparent, is_node)
#
# ID Mapping Note:
# - In pyswisseph / Swiss Ephemeris C library:
#     SUN=0, MOON=1, MERCURY=2, VENUS=3, MARS=4, JUPITER=5, SATURN=6, URANUS=7, NEPTUNE=8,
#     PLUTO=9, MEAN_NODE=10, TRUE_NODE=11.
# - In XALEN core direct API (`xalen.planet_longitude`):
#     0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn, 7=Uranus, 8=Neptune,
#     9=MeanNode(Rahu), 10=TrueNode, 11=Pluto.
# - In XALEN drop-in compat (`xalen.swe.calc_ut`):
#     Uses the exact Swiss Ephemeris body IDs (e.g. swe.PLUTO=9, swe.MEAN_NODE=10, swe.TRUE_NODE=11).
#
# Tolerance Documentation (against pyswisseph with Moshier fallback):
# - Sun, Mercury, Venus, Mars, Jupiter, Saturn, Pluto: < 1.5" (0.00042°)
# - Uranus, Neptune: < 2.5"
# - Moon: < 6.0" (reflects ELP2000 in XALEN vs Moshier lunar series in pyswisseph without .se1 files)
# - Mean Lunar Node: < 0.5" (pure analytic formula)
# - True Lunar Node: < 30.0" (~13"-24" perturbation truncation in Moshier fallback)
BODIES_CONFIG = [
    ("sun", swe.SUN, 0, 1.5, False),
    ("moon", swe.MOON, 1, 6.0, False),
    ("mercury", swe.MERCURY, 2, 1.5, False),
    ("venus", swe.VENUS, 3, 1.5, False),
    ("mars", swe.MARS, 4, 1.5, False),
    ("jupiter", swe.JUPITER, 5, 1.5, False),
    ("saturn", swe.SATURN, 6, 1.5, False),
    ("uranus", swe.URANUS, 7, 2.5, False),
    ("neptune", swe.NEPTUNE, 8, 2.5, False),
    ("pluto", swe.PLUTO, 11, 1.5, False),
    ("mean_node", swe.MEAN_NODE, 9, 0.5, True),
    ("true_node", swe.TRUE_NODE, 10, 30.0, True),
]


@pytest.fixture
def sample_epochs():
    return TEST_EPOCHS


@pytest.fixture
def sample_locations():
    return TEST_LOCATIONS


@pytest.fixture
def sample_bodies():
    return BODIES_CONFIG
