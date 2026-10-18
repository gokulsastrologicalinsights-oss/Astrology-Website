"""KP horary (Prashna): the 1-249 number system.

The zodiac contains 27 nakshatras x 9 Vimshottari sub-lords = 243 subs.  Six of
the twelve sign boundaries fall *inside* a sub and split it in two (the sub's
lord stays the same but its zodiac sign changes), which is why a KP horary
chart counts exactly **249** numbered divisions from 0° Aries.

* A querent's number ``n`` (1..249) selects division ``n``.
* The horary ascendant is the **midpoint** of that division.
* Everything else (planets, other cusps, rulers) comes from the moment and
  place of the question, computed with the normal engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_right
from functools import lru_cache

from .constants import VIMSHOTTARI_ORDER
from .vedic import (
    normalize_longitude,
    point_info,
    sign_lord_of_longitude,
    sign_name,
    star_lord,
    star_name,
    sub_divisions,
)

MAX_HORARY_NUMBER = 249

#: Tolerance for deciding a sign boundary falls strictly inside a sub.
_BOUNDARY_EPS = 1e-9


@dataclass(frozen=True)
class HoraryDiv:
    """One of the 249 KP horary divisions of the zodiac."""
    number: int
    start_deg: float
    end_deg: float
    sign: str
    sign_lord: str
    star: str
    star_lord: str
    sub_lord: str

    @property
    def mid_deg(self) -> float:
        return (self.start_deg + self.end_deg) / 2.0


def kp_divisions() -> list[HoraryDiv]:
    """Generate all 249 divisions in ascending zodiacal order.

    The table is computed once and cached; each call returns a fresh list
    over the immutable internal table, so callers may not corrupt the cache.
    """
    return list(_divisions_tuple())


@lru_cache(maxsize=None)
def _divisions_tuple() -> tuple[HoraryDiv, ...]:
    subs: list[tuple[float, float, int, str]] = []
    for sidx in range(27):
        for lord, start, end, _span in sub_divisions(sidx):
            subs.append((start, end, sidx, lord))

    divisions: list[HoraryDiv] = []
    num = 0
    for start, end, sidx, sub_owner in subs:
        boundaries = [
            b for b in (30.0 * k for k in range(1, 12))
            if start + _BOUNDARY_EPS < b < end - _BOUNDARY_EPS
        ]
        cursor = start
        for b in boundaries + [end]:
            seg_start, seg_end = cursor, b
            num += 1
            divisions.append(
                HoraryDiv(
                    number=num,
                    start_deg=seg_start,
                    end_deg=seg_end,
                    sign=sign_name(seg_start),
                    sign_lord=sign_lord_of_longitude(seg_start),
                    star=star_name(seg_start),
                    star_lord=star_lord(seg_start),
                    sub_lord=sub_owner,
                )
            )
            cursor = b
    return tuple(divisions)


@lru_cache(maxsize=None)
def _division_starts() -> tuple[float, ...]:
    return tuple(d.start_deg for d in _divisions_tuple())


def ascendant_from_kp_number(n: int) -> dict:
    """The horary ascendant (division midpoint) and its full KP lord chain.

    Returns a dict with ``ascendant`` (sidereal longitude), the division span
    and the sign / star / sub / sub-sub breakdown.
    """
    if not 1 <= n <= MAX_HORARY_NUMBER:
        raise ValueError(f"KP horary number must be within 1-{MAX_HORARY_NUMBER}")
    div = _divisions_tuple()[n - 1]
    mid = div.mid_deg
    info = point_info(mid)
    return {
        "number": n,
        "ascendant": mid,
        "span": (div.start_deg, div.end_deg),
        "sign": info.sign,
        "sign_lord": info.sign_lord,
        "star": info.star,
        "star_lord": info.star_lord,
        "sub_lord": info.sub_lord,
        "sub_sub_lord": info.sub_sub_lord,
        "pada": info.pada,
    }


def kp_number_for_longitude(lon: float) -> int:
    """Inverse lookup: which KP horary division contains this sidereal longitude.

    Uses binary search over the cached division-start table, so a single
    lookup is O(log 249) instead of rescanning the whole zodiac.  Longitudes
    outside [0, 360) are normalised first (the 249 divisions tile the full
    zodiac, so the lookup always succeeds).
    """
    lon = normalize_longitude(lon)
    starts = _division_starts()
    idx = bisect_right(starts, lon) - 1
    return max(idx, 0) + 1


def find_armc_for_ascendant(target_trop_asc: float, latitude: float, eps: float) -> float:
    """Find the Right Ascension of the Midheaven (ARMC) that yields target_trop_asc.

    Uses a coarse sweep in 5-degree increments to bracket the target, then performs
    bisection to locate the exact ARMC within sub-micro-arcsecond tolerance.
    """
    import swisseph as swe

    target = target_trop_asc % 360.0
    best_step = 0
    min_dist = 999.0
    for s in range(72):
        a = s * 5.0
        _, ascmc = swe.houses_armc(a, latitude, eps, b"P")
        cur_asc = ascmc[0] % 360.0
        diff = (target - cur_asc + 180.0) % 360.0 - 180.0
        if abs(diff) < min_dist:
            min_dist = abs(diff)
            best_step = s

    low = (best_step * 5.0 - 6.0) % 360.0
    high = (best_step * 5.0 + 6.0) % 360.0
    span = (high - low) % 360.0
    if span == 0.0:
        span = 360.0

    l = 0.0
    r = span
    for _ in range(48):
        m = (l + r) / 2.0
        test_armc = (low + m) % 360.0
        _, ascmc = swe.houses_armc(test_armc, latitude, eps, b"P")
        cur_asc = ascmc[0] % 360.0
        diff = (cur_asc - target + 180.0) % 360.0 - 180.0
        if diff > 0.0:
            r = m
        else:
            l = m

    return (low + (l + r) / 2.0) % 360.0


def compute_horary_cusps(
    target_sidereal_asc: float,
    latitude: float,
    ayanamsa_val: float,
    eps: float,
) -> tuple[list[float], float, float]:
    """Compute 12 Placidus house cusps where Cusp 1 is fixed to target_sidereal_asc.

    Returns (cusps_12, ascendant, midheaven).
    """
    import swisseph as swe

    target_trop = (target_sidereal_asc + ayanamsa_val) % 360.0
    armc = find_armc_for_ascendant(target_trop, latitude, eps)
    cusps_trop, ascmc = swe.houses_armc(armc, latitude, eps, b"P")
    cusps_sid = [(c - ayanamsa_val) % 360.0 for c in cusps_trop]
    mc_sid = (ascmc[1] - ayanamsa_val) % 360.0
    # Pin exact Ascendant on Cusp 1
    cusps_sid[0] = target_sidereal_asc
    return cusps_sid, target_sidereal_asc, mc_sid