"""KP Reader 1 ("Casting the Horoscope") engine and reference module.

Authoritative implementation of the foundational principles, algorithms,
tables, and verification techniques published by Jyotish Marthand
Prof. K. S. Krishnamurti in:

    STELLAR ASTROLOGICAL READER NO. 1: CASTING THE HOROSCOPE
    (Using Ephemeris)
    Publishers: Krishman & Co., Madras / Stellar Astrological Research Institute.

Key Features Codified from KP Reader 1:
----------------------------------------
1. Authentic KP Ayanamsa:
   - Coincidence / Zero Year: 291 A.D. (VP291).
   - Precession Rate: Newcomb's rate = 50.2388475" / year.
   - Complete 1840-2001 published annual table of KP Ayanamsa values.
   - Formula for years beyond 2001 (add 50.2388475" per year).
2. Time & Sidereal Time Computation:
   - Standard Time -> Greenwich Mean Time (GMT) conversion.
   - Standard Time -> Local Mean Time (LMT) (4 minutes per 1 degree difference).
   - The 4-step Sidereal Time calculation method:
       Step 1: Greenwich noon sidereal time.
       Step 2: Longitude correction:
               East Longitude: deduct (longitude * 2 / 3) seconds.
               West Longitude: add (longitude * 2 / 3) seconds.
       Step 3: Add interval between previous noon and LMT.
       Step 4: Add interval correction (acceleration of sidereal over mean solar time
               at 10 seconds per hour).
3. Vimshottari Dasa Balance:
   - Nakshatra span: 13° 20' = 800 arcminutes.
   - Balance = (Remaining arcmin / 800) * Mahadasha years.
   - Reader 1 Table of Balance per 1 degree and per 1 minute (360-day Savana dasha year basis).
4. Rasi and Navamsa Chakra (108 Padas):
   - Continuous 108-division Navamsa cycle (3° 20' each).
   - Vargottama determination (planet occupying same sign in Rasi and Navamsa).
5. Ruling Planets (RP) & Verification:
   - Day Lord, Moon Sign/Star/Sub/Sub-sub Lords, Lagna Sign/Star/Sub/Sub-sub Lords.
   - Node representations: Rahu/Ketu representing sign lord, conjunctions, and aspects.
6. Worked Examples Test Cases:
   - Five Reader 1 verification cities (Agra, Allahabad, Ahmedabad, Boston, San Francisco).
   - The 1938/1933 marriage verification case demonstrating KP Ayanamsa correctness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .constants import (
    NAKSHATRAS,
    PLANET_ABBR,
    SIGN_LORDS,
    SIGNS,
    SIGNS_RULED_BY,
    VIMSHOTTARI_INDEX,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    WEEKDAY_LORDS,
)
from .vedic import (
    STAR_SPAN_ARCMIN,
    STAR_SPAN_DEG,
    normalize_longitude,
    sign_index,
    sign_name,
    star_index,
    star_lord,
    star_name,
    sub_info,
    sub_sub_info,
)

# ---------------------------------------------------------------------------
# 1. Authentic KP Reader 1 Ayanamsa Constants & Table
# ---------------------------------------------------------------------------

#: Year of coincidence of Tropical and Sidereal zodiacs according to Prof. K. S. Krishnamurti.
KP_COINCIDENCE_YEAR: int = 291

#: Rate of precession of equinoxes adopted by Prof. K. S. Krishnamurti (Newcomb's rate).
NEWCOMB_PRECESSION_RATE_ARCSEC: float = 50.2388475
NEWCOMB_PRECESSION_RATE_DEG: float = NEWCOMB_PRECESSION_RATE_ARCSEC / 3600.0  #: ~0.013955235416666667 deg/yr

#: Span of one Navamsa (quarter of a nakshatra, 1/9th of a sign): 3° 20' = 200 arcminutes.
NAVAMSA_SPAN_DEG: float = 10.0 / 3.0  #: 3.3333333333333335 degrees
NAVAMSA_SPAN_ARCMIN: float = 200.0

#: Authentic table of KP Ayanamsa published in KP Reader 1, page 59 (1840 to 2001).
#: Maps year -> (degrees, minutes).
KP_READER1_AYANAMSA_TABLE: dict[int, tuple[int, int]] = {
    1840: (21, 31), 1841: (21, 32), 1842: (21, 33), 1843: (21, 34), 1844: (21, 35),
    1845: (21, 36), 1846: (21, 37), 1847: (21, 37), 1848: (21, 38), 1849: (21, 39),
    1850: (21, 40), 1851: (21, 41), 1852: (21, 42), 1853: (21, 42), 1854: (21, 43),
    1855: (21, 44), 1856: (21, 45), 1857: (21, 46), 1858: (21, 47), 1859: (21, 47),
    1860: (21, 48), 1861: (21, 49), 1862: (21, 50), 1863: (21, 51), 1864: (21, 52),
    1865: (21, 52), 1866: (21, 53), 1867: (21, 54), 1868: (21, 55), 1869: (21, 56),
    1870: (21, 57), 1871: (21, 57), 1872: (21, 58), 1873: (21, 59), 1874: (22, 0),
    1875: (22, 1),  1876: (22, 2),  1877: (22, 2),  1878: (22, 3),  1879: (22, 4),
    1880: (22, 5),  1881: (22, 6),  1882: (22, 7),  1883: (22, 8),  1884: (22, 8),
    1885: (22, 9),  1886: (22, 10), 1887: (22, 11), 1888: (22, 12), 1889: (22, 13),
    1890: (22, 13), 1891: (22, 14), 1892: (22, 15), 1893: (22, 16), 1894: (22, 17),
    1895: (22, 18), 1896: (22, 18), 1897: (22, 19), 1898: (22, 20), 1899: (22, 21),
    1900: (22, 22), 1901: (22, 23), 1902: (22, 23), 1903: (22, 24), 1904: (22, 25),
    1905: (22, 26), 1906: (22, 27), 1907: (22, 28), 1908: (22, 29), 1909: (22, 30),
    1910: (22, 31), 1911: (22, 32), 1912: (22, 33), 1913: (22, 33), 1914: (22, 34),
    1915: (22, 35), 1916: (22, 36), 1917: (22, 37), 1918: (22, 38), 1919: (22, 38),
    1920: (22, 39), 1921: (22, 39), 1922: (22, 40), 1923: (22, 41), 1924: (22, 42),
    1925: (22, 43), 1926: (22, 44), 1927: (22, 44), 1928: (22, 45), 1929: (22, 46),
    1930: (22, 47), 1931: (22, 48), 1932: (22, 49), 1933: (22, 49), 1934: (22, 50),
    1935: (22, 51), 1936: (22, 52), 1937: (22, 53), 1938: (22, 54), 1939: (22, 54),
    1940: (22, 55), 1941: (22, 56), 1942: (22, 57), 1943: (22, 58), 1944: (22, 59),
    1945: (22, 59), 1946: (23, 0),  1947: (23, 1),  1948: (23, 2),  1949: (23, 3),
    1950: (23, 4),  1951: (23, 4),  1952: (23, 5),  1953: (23, 6),  1954: (23, 7),
    1955: (23, 8),  1956: (23, 9),  1957: (23, 10), 1958: (23, 10), 1959: (23, 11),
    1960: (23, 12), 1961: (23, 13), 1962: (23, 14), 1963: (23, 15), 1964: (23, 15),
    1965: (23, 16), 1966: (23, 17), 1967: (23, 18), 1968: (23, 19), 1969: (23, 20),
    1970: (23, 20), 1971: (23, 21), 1972: (23, 22), 1973: (23, 23), 1974: (23, 24),
    1975: (23, 25), 1976: (23, 25), 1977: (23, 26), 1978: (23, 27), 1979: (23, 28),
    1980: (23, 29), 1981: (23, 30), 1982: (23, 30), 1983: (23, 31), 1984: (23, 32),
    1985: (23, 33), 1986: (23, 34), 1987: (23, 35), 1988: (23, 35), 1989: (23, 36),
    1990: (23, 37), 1991: (23, 38), 1992: (23, 39), 1993: (23, 40), 1994: (23, 41),
    1995: (23, 41), 1996: (23, 42), 1997: (23, 43), 1998: (23, 44), 1999: (23, 45),
    2000: (23, 46), 2001: (23, 47),
}


def get_reader1_table_ayanamsa(year: int) -> tuple[int, int]:
    """Return the exact (degrees, minutes) published in KP Reader 1 for ``year`` (1840-2001).

    If outside 1840-2001, calculates using the explicit formula given on page 59:
    "If you want ayanamsa from the years beyond 2001, for each year add at the rate
    of 50.2388475 secs."
    """
    if year in KP_READER1_AYANAMSA_TABLE:
        return KP_READER1_AYANAMSA_TABLE[year]

    if year > 2001:
        base_deg = 23.0 + 47.0 / 60.0
        val = base_deg + (year - 2001) * NEWCOMB_PRECESSION_RATE_DEG
    else:
        base_deg = 21.0 + 31.0 / 60.0
        val = base_deg - (1840 - year) * NEWCOMB_PRECESSION_RATE_DEG

    d = int(val)
    m = int(round((val - d) * 60.0))
    if m == 60:
        d += 1
        m = 0
    return d, m


def calculate_reader1_ayanamsa(
    year_or_date: float | int | date | datetime,
    interpolate: bool = True,
) -> float:
    """Calculate the KP Reader 1 Ayanamsa in decimal degrees for a date or fractional year.

    For dates/years within 1840-2001, uses the authentic published table.
    Beyond 2001, follows the exact additive rate of 50.2388475" per year specified
    by Prof. K. S. Krishnamurti.
    """
    if isinstance(year_or_date, (datetime, date)):
        # Convert date to fractional year
        y = year_or_date.year
        start_of_year = date(y, 1, 1)
        end_of_year = date(y + 1, 1, 1)
        target_date = year_or_date.date() if isinstance(year_or_date, datetime) else year_or_date
        fraction = (target_date - start_of_year).total_seconds() / (
            end_of_year - start_of_year
        ).total_seconds()
        fractional_year = float(y) + fraction
    else:
        fractional_year = float(year_or_date)

    int_year = int(fractional_year)
    frac = fractional_year - int_year

    if not interpolate or abs(frac) < 1e-6:
        d, m = get_reader1_table_ayanamsa(int_year)
        return float(d) + float(m) / 60.0

    if int_year >= 2001:
        base_deg = 23.0 + 47.0 / 60.0
        return base_deg + (fractional_year - 2001.0) * NEWCOMB_PRECESSION_RATE_DEG
    elif int_year < 1840:
        base_deg = 21.0 + 31.0 / 60.0
        return base_deg - (1840.0 - fractional_year) * NEWCOMB_PRECESSION_RATE_DEG

    # Interpolate between table entries for int_year and int_year + 1
    d1, m1 = get_reader1_table_ayanamsa(int_year)
    d2, m2 = get_reader1_table_ayanamsa(int_year + 1)
    val1 = float(d1) + float(m1) / 60.0
    val2 = float(d2) + float(m2) / 60.0
    return val1 + frac * (val2 - val1)


def format_ayanamsa_dms(deg_float: float) -> str:
    """Format decimal degrees into 'DD° MM' SS"' representation."""
    d = int(deg_float)
    rem = (deg_float - d) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    if s >= 59.95:
        m += 1
        s = 0.0
        if m == 60:
            d += 1
            m = 0
    return f"{d}° {m:02d}' {s:04.1f}\""


# ---------------------------------------------------------------------------
# 2. Time & Sidereal Time Calculations (KP Reader 1 exact 4-step method)
# ---------------------------------------------------------------------------

def standard_to_gmt(std_time_hours: float, std_meridian_deg: float = 82.5) -> float:
    """Convert Standard Time (in decimal hours) to Greenwich Mean Time (GMT).

    For India (meridian 82°30' E), difference is always +5h 30m (+5.5 hrs).
    """
    offset_hours = std_meridian_deg / 15.0
    gmt = (std_time_hours - offset_hours) % 24.0
    return gmt


def standard_to_lmt(
    std_time_hours: float,
    local_longitude_deg: float,
    std_meridian_deg: float = 82.5,
) -> float:
    """Convert Standard Time to Local Mean Time (LMT) in decimal hours.

    Rule: 4 minutes per 1 degree difference from the standard meridian.
    If place is East of standard meridian, time is ahead (+); if West, behind (-).
    """
    diff_deg = local_longitude_deg - std_meridian_deg
    diff_minutes = diff_deg * 4.0
    diff_hours = diff_minutes / 60.0
    lmt = (std_time_hours + diff_hours) % 24.0
    return lmt


@dataclass(frozen=True)
class SiderealTimeStepAudit:
    """Audit breakdown of the 4 steps taught by KSK to compute Sidereal Time."""
    greenwich_noon_st_hours: float
    longitude_deg: float
    is_east: bool
    longitude_correction_seconds: float
    local_noon_st_hours: float
    elapsed_interval_lmt_hours: float
    interval_correction_seconds: float
    total_sidereal_time_hours: float
    formatted_st: str
    steps_description: list[str]


def calculate_sidereal_time_reader1(
    lmt_time_hours: float,
    longitude_deg: float,
    prev_noon_greenwich_st_hours: float,
    use_exact_acceleration: bool = False,
) -> SiderealTimeStepAudit:
    """Compute local Sidereal Time following Prof. K. S. Krishnamurti's 4-step method.

    From KP Reader 1, page 31:
    1. Note Sidereal Time given for previous noon at Greenwich.
    2. Longitude correction:
       - East Longitude: deduct (longitude * 2 / 3) seconds.
       - West Longitude: add (longitude * 2 / 3) seconds.
       (Since 360° = 240 seconds -> 2/3 sec per deg = 0.66667 s/deg).
    3. Add the interval between previous noon and LMT birth time.
    4. Add interval correction at 10 seconds per hour (or exact 9.8565 sec/hr).
    """
    steps: list[str] = []

    # Step 1: Greenwich noon ST
    st1 = prev_noon_greenwich_st_hours
    steps.append(f"Step 1: Greenwich Sidereal Time at previous noon = {format_hours_hms(st1)}")

    # Step 2: Longitude correction (2/3 second per degree)
    is_east = longitude_deg >= 0.0
    abs_long = abs(longitude_deg)
    long_corr_sec = abs_long * (2.0 / 3.0)

    if is_east:
        local_noon_st = st1 - (long_corr_sec / 3600.0)
        steps.append(
            f"Step 2 (East Longitude {abs_long:.2f}°): Deduct 2/3 sec/deg = "
            f"{long_corr_sec:.1f}s -> Local noon ST = {format_hours_hms(local_noon_st)}"
        )
    else:
        local_noon_st = st1 + (long_corr_sec / 3600.0)
        steps.append(
            f"Step 2 (West Longitude {abs_long:.2f}°): Add 2/3 sec/deg = "
            f"{long_corr_sec:.1f}s -> Local noon ST = {format_hours_hms(local_noon_st)}"
        )

    # Step 3: Elapsed interval since previous noon (in LMT)
    # If LMT is >= 12.0 (afternoon), interval = LMT - 12.0
    # If LMT is < 12.0 (morning), previous noon was yesterday: interval = 12.0 + LMT
    if lmt_time_hours >= 12.0:
        interval_hours = lmt_time_hours - 12.0
    else:
        interval_hours = 12.0 + lmt_time_hours

    steps.append(
        f"Step 3: Interval between previous noon and birth LMT = "
        f"{format_hours_hms(interval_hours)}"
    )

    # Step 4: Interval acceleration correction
    # Reader 1 standard: 10 seconds per hour. Exact astronomical: 9.8565 sec/hr.
    rate_sec = 9.856473 if use_exact_acceleration else 10.0
    int_corr_sec = interval_hours * rate_sec
    steps.append(
        f"Step 4: Acceleration correction for {interval_hours:.3f} hrs @ {rate_sec}s/hr = "
        f"{int_corr_sec:.1f}s"
    )

    total_st = (local_noon_st + interval_hours + (int_corr_sec / 3600.0)) % 24.0
    formatted = format_hours_hms(total_st)
    steps.append(f"Final Sidereal Time = {formatted}")

    return SiderealTimeStepAudit(
        greenwich_noon_st_hours=st1,
        longitude_deg=longitude_deg,
        is_east=is_east,
        longitude_correction_seconds=long_corr_sec,
        local_noon_st_hours=local_noon_st,
        elapsed_interval_lmt_hours=interval_hours,
        interval_correction_seconds=int_corr_sec,
        total_sidereal_time_hours=total_st,
        formatted_st=formatted,
        steps_description=steps,
    )


def format_hours_hms(hours_float: float) -> str:
    """Format decimal hours into 'HH:MM:SS' string."""
    h = int(hours_float)
    rem = (hours_float - h) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    if s >= 59.95:
        m += 1
        s = 0.0
        if m == 60:
            h = (h + 1) % 24
            m = 0
    return f"{h:02d}h {m:02d}m {int(round(s)):02d}s"


# ---------------------------------------------------------------------------
# 3. Vimshottari Dasa Balance Table and Math from KP Reader 1
# ---------------------------------------------------------------------------

#: Dasa balance rates per 1 degree and per 1 minute (360-day dasha year),
#: exactly as published in KP Reader 1, page 88.
READER1_DASA_BALANCE_RATES: dict[str, dict[str, Any]] = {
    "Ketu": {
        "dasa_years": 7,
        "per_degree": (0, 6, 9),    # 0 yrs, 6 mos, 9 days
        "days_per_minute": 3.15,
    },
    "Venus": {
        "dasa_years": 20,
        "per_degree": (1, 6, 0),    # 1 yr, 6 mos, 0 days
        "days_per_minute": 9.00,
    },
    "Sun": {
        "dasa_years": 6,
        "per_degree": (0, 5, 12),   # 0 yrs, 5 mos, 12 days
        "days_per_minute": 2.70,
    },
    "Moon": {
        "dasa_years": 10,
        "per_degree": (0, 9, 0),    # 0 yrs, 9 mos, 0 days
        "days_per_minute": 4.50,
    },
    "Mars": {
        "dasa_years": 7,
        "per_degree": (0, 6, 9),    # 0 yrs, 6 mos, 9 days
        "days_per_minute": 3.15,
    },
    "Rahu": {
        "dasa_years": 18,
        "per_degree": (1, 4, 6),    # 1 yr, 4 mos, 6 days
        "days_per_minute": 8.10,
    },
    "Jupiter": {
        "dasa_years": 16,
        "per_degree": (1, 2, 12),   # 1 yr, 2 mos, 12 days
        "days_per_minute": 7.20,
    },
    "Saturn": {
        "dasa_years": 19,
        "per_degree": (1, 5, 3),    # 1 yr, 5 mos, 3 days
        "days_per_minute": 8.55,
    },
    "Mercury": {
        "dasa_years": 17,
        "per_degree": (1, 3, 9),    # 1 yr, 3 mos, 9 days
        "days_per_minute": 7.65,
    },
}


@dataclass(frozen=True)
class DasaBalanceReader1:
    """Complete Vimshottari Dasa balance details computed according to KP Reader 1."""
    lord: str
    nakshatra: str
    nakshatra_index: int
    transited_arcmin: float
    balance_arcmin: float
    balance_years: int
    balance_months: int
    balance_days: float
    total_balance_days: float
    sub_lord: str
    sub_sub_lord: str
    balance_formatted: str


def calculate_dasa_balance_reader1(
    moon_longitude: float,
    use_360_day_year: bool = True,
) -> DasaBalanceReader1:
    """Calculate the Vimshottari Dasa balance at birth following KP Reader 1.

    Formula from Reader 1, page 86-88:
        Remaining portion of star = Star End - Moon Longitude
        Balance fraction = Remaining minutes / 800 minutes
        Balance = Balance fraction * Total Mahadasha years
    """
    moon_lon = normalize_longitude(moon_longitude)
    idx = star_index(moon_lon)
    star_start = idx * STAR_SPAN_DEG
    star_end = star_start + STAR_SPAN_DEG

    transited_deg = moon_lon - star_start
    balance_deg = star_end - moon_lon

    transited_arcmin = transited_deg * 60.0
    balance_arcmin = balance_deg * 60.0

    lord = star_lord(moon_lon)
    dasa_years = VIMSHOTTARI_YEARS[lord]

    # Fraction of star remaining: balance_arcmin / 800.0
    frac = balance_arcmin / STAR_SPAN_ARCMIN
    total_years_float = frac * dasa_years

    days_in_year = 360.0 if use_360_day_year else 365.25
    total_days = total_years_float * days_in_year

    years = int(total_years_float)
    rem_years = total_years_float - years
    months_float = rem_years * 12.0
    months = int(months_float)
    days = (months_float - months) * 30.0

    sub = sub_info(moon_lon)
    subsub = sub_sub_info(moon_lon)

    formatted = f"{years}y {months}m {days:.1f}d"

    return DasaBalanceReader1(
        lord=lord,
        nakshatra=NAKSHATRAS[idx],
        nakshatra_index=idx,
        transited_arcmin=transited_arcmin,
        balance_arcmin=balance_arcmin,
        balance_years=years,
        balance_months=months,
        balance_days=days,
        total_balance_days=total_days,
        sub_lord=sub.lord,
        sub_sub_lord=subsub.lord,
        balance_formatted=formatted,
    )


# ---------------------------------------------------------------------------
# 4. Rasi and Navamsa Chakra (108 Padas)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NavamsaInfo:
    """Navamsa breakdown of a sidereal longitude as tabulated in KP Reader 1."""
    longitude: float
    rasi_sign: str
    rasi_lord: str
    navamsa_sign: str
    navamsa_lord: str
    navamsa_index: int       # 0..11 (Aries=0 .. Pisces=11)
    pada: int                # 1..4 inside its nakshatra
    is_vargottama: bool      # True if Rasi Sign == Navamsa Sign


def get_navamsa_info(longitude: float) -> NavamsaInfo:
    """Compute the Navamsa sign, lord, and Vargottama status for any longitude.

    Matches the 108-entry Navamsa table published in KP Reader 1, pages 79-81.
    Each Navamsa spans 3° 20' (3.3333333333 degrees).
    Continuous cyclic index: (lon // (10/3)) % 12.
    """
    lon = normalize_longitude(longitude)
    r_idx = sign_index(lon)
    r_sign = SIGNS[r_idx]
    r_lord = SIGN_LORDS[r_sign]

    # Continuous 108-division Navamsa cycle
    n_idx = int(lon // NAVAMSA_SPAN_DEG) % 12
    n_sign = SIGNS[n_idx]
    n_lord = SIGN_LORDS[n_sign]

    # Pada inside the nakshatra (1..4)
    st_idx = star_index(lon)
    st_start = st_idx * STAR_SPAN_DEG
    pada = min(int((lon - st_start) // (STAR_SPAN_DEG / 4.0)) + 1, 4)

    is_varg = r_sign == n_sign

    return NavamsaInfo(
        longitude=lon,
        rasi_sign=r_sign,
        rasi_lord=r_lord,
        navamsa_sign=n_sign,
        navamsa_lord=n_lord,
        navamsa_index=n_idx,
        pada=pada,
        is_vargottama=is_varg,
    )


# ---------------------------------------------------------------------------
# 5. Ruling Planets with Node Representation (KP Reader 1 Verification)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RulingPlanetReader1:
    """Ruling planet entry with source hierarchy and node agent representations."""
    planet: str
    role: str
    represented_by: list[str] = field(default_factory=list)


def calculate_ruling_planets_reader1(
    ascendant_lon: float,
    moon_lon: float,
    weekday: int,  # 0=Monday .. 6=Sunday
    planet_positions: Optional[dict[str, float]] = None,
) -> list[RulingPlanetReader1]:
    """Compute Ruling Planets following Prof. K. S. Krishnamurti's exact procedure.

    From KP Reader 1, Section "AYANAMSA - VERIFICATION":
    Primary Ruling Planets:
    1. Day Lord
    2. Moon Sign Lord
    3. Moon Star Lord
    4. Lagna Sign Lord
    5. Lagna Star Lord
    Sub-lords:
    6. Lagna Sub Lord
    7. Moon Sub Lord
    Node representations:
    Rahu and Ketu represent the lord of the sign they occupy, and any planets
    they are conjoined with or aspected by.
    """
    asc_lon = normalize_longitude(ascendant_lon)
    mo_lon = normalize_longitude(moon_lon)

    day_lord = WEEKDAY_LORDS[weekday % 7]
    asc_sign_l = SIGN_LORDS[SIGNS[sign_index(asc_lon)]]
    asc_star_l = star_lord(asc_lon)
    asc_sub_l = sub_info(asc_lon).lord
    asc_subsub_l = sub_sub_info(asc_lon).lord

    mo_sign_l = SIGN_LORDS[SIGNS[sign_index(mo_lon)]]
    mo_star_l = star_lord(mo_lon)
    mo_sub_l = sub_info(mo_lon).lord
    mo_subsub_l = sub_sub_info(mo_lon).lord

    # Node representation mappings
    node_rep: dict[str, list[str]] = {"Rahu": [], "Ketu": []}
    if planet_positions:
        for node in ("Rahu", "Ketu"):
            if node in planet_positions:
                node_lon = planet_positions[node]
                sign_l = SIGN_LORDS[SIGNS[sign_index(node_lon)]]
                if sign_l not in node_rep[node]:
                    node_rep[node].append(sign_l)
                # Conjunctions (within 3°10' or in same sign)
                for other_p, other_lon in planet_positions.items():
                    if other_p not in ("Rahu", "Ketu"):
                        if sign_index(other_lon) == sign_index(node_lon):
                            if other_p not in node_rep[node]:
                                node_rep[node].append(other_p)

    raw_entries: list[tuple[str, str]] = [
        (day_lord, "Day Lord"),
        (mo_sign_l, "Moon Sign Lord"),
        (mo_star_l, "Moon Star Lord"),
        (mo_sub_l, "Moon Sub Lord"),
        (mo_subsub_l, "Moon Sub-sub Lord"),
        (asc_sign_l, "Lagna Sign Lord"),
        (asc_star_l, "Lagna Star Lord"),
        (asc_sub_l, "Lagna Sub Lord"),
        (asc_subsub_l, "Lagna Sub-sub Lord"),
    ]

    # Deduplicate while preserving order and concatenating roles
    result: list[RulingPlanetReader1] = []
    seen: dict[str, int] = {}
    for p, role in raw_entries:
        if p in seen:
            idx = seen[p]
            old_rp = result[idx]
            result[idx] = RulingPlanetReader1(
                planet=p,
                role=f"{old_rp.role}, {role}",
                represented_by=old_rp.represented_by,
            )
        else:
            rep = node_rep.get(p, [])
            seen[p] = len(result)
            result.append(RulingPlanetReader1(planet=p, role=role, represented_by=rep))

    # Add Rahu/Ketu if they represent any ruling planet
    for node, reps in node_rep.items():
        if node not in seen:
            intersecting = [r for r in reps if r in seen]
            if intersecting:
                result.append(
                    RulingPlanetReader1(
                        planet=node,
                        role=f"Node agent representing {', '.join(intersecting)}",
                        represented_by=reps,
                    )
                )

    return result


# ---------------------------------------------------------------------------
# 6. KP Reader 1 Verification Test Cases & Examples
# ---------------------------------------------------------------------------

#: Worked verification examples from KP Reader 1
READER1_WORKED_EXAMPLES: dict[str, dict[str, Any]] = {
    "Agra_1963": {
        "description": "Reader 1 Example 1: Birth 15-5-1963 at Agra 78°05' E, 6:30 PM IST",
        "date": date(1963, 5, 15),
        "std_time": 18.5,           # 6:30 PM
        "latitude": 27.18,
        "longitude": 78.083333,      # 78°05' E
        "std_meridian": 82.5,
        "expected_lmt": "18h 12m 20s",
        "expected_st": "09h 42m 29s",
        "ayanamsa_1963": (23, 15),   # 23° 15'
    },
    "Allahabad_1963": {
        "description": "Reader 1 Example 2: Birth 15-5-1963 at Allahabad 81°54' E, 25°28' N, 3:30 AM IST",
        "date": date(1963, 5, 15),
        "std_time": 3.5,            # 3:30 AM
        "latitude": 25.466667,
        "longitude": 81.90,          # 81°54' E
        "std_meridian": 82.5,
        "expected_lmt": "03h 27m 36s",
        "expected_st": "18h 55m 18s",
    },
    "Ahmedabad_1963": {
        "description": "Reader 1 Example 3: Birth 15-5-1963 at Ahmedabad 72°38' E, 23°02' N, 12:05 PM IST",
        "date": date(1963, 5, 15),
        "std_time": 12.083333,      # 12:05 PM
        "latitude": 23.033333,
        "longitude": 72.633333,      # 72°38' E
        "std_meridian": 82.5,
        "expected_lmt": "11h 25m 32s",
        "expected_st": "02h 54m 40s",
    },
    "Boston_1963": {
        "description": "Reader 1 Example 4: Birth 15-5-1963 at Boston 71°02' W, 42°21' N, 9:00 PM ST (UTC-5)",
        "date": date(1963, 5, 15),
        "std_time": 21.0,           # 9:00 PM
        "latitude": 42.35,
        "longitude": -71.033333,     # 71°02' W
        "std_meridian": -75.0,
        "expected_lmt": "21h 15m 52s",
        "expected_st": "12h 48m 11s",
    },
    "SanFrancisco_1963": {
        "description": "Reader 1 Example 5: Birth 15-5-1963 at San Francisco 122°25' W, 37°48' N, 7:00 AM ST (UTC-8)",
        "date": date(1963, 5, 15),
        "std_time": 7.0,            # 7:00 AM
        "latitude": 37.80,
        "longitude": -122.416667,    # 122°25' W
        "std_meridian": -120.0,
        "expected_lmt": "06h 50m 20s",
        "expected_st": "22h 20m 52s",
    },
    "Marriage_Verification_1938": {
        "description": "Reader 1 Ayanamsa Verification: Girl born 5-3-1938 at 7:40 PM IST (11°39' N, 78°12' E)",
        "date": date(1938, 3, 5),
        "std_time": 19.666667,      # 7:40 PM
        "latitude": 11.65,
        "longitude": 78.20,
        "std_meridian": 82.5,
        "ayanamsa_1938": (22, 54),   # 22° 54'
        "marriage_date": date(1961, 11, 19),
        "expected_dasa_at_marriage": "Rahu-Mercury-Jupiter-Rahu",
        "marriage_significators": [2, 7, 11],
    },
}
