/**
 * Solar Astronomy Calculations (NOAA Solar Algorithm)
 * 
 * Provides exact astronomical Sunrise and Sunset calculations matching
 * backend/app/services/muhurta_engine/astronomy.py.
 */

export interface SolarTimes {
  sunriseTime: string; // "06:32 AM"
  sunsetTime: string;  // "05:55 PM"
  sunrise24: string;   // "06:31:58"
  sunset24: string;    // "17:54:42"
  dayLengthHours: number;
}

/**
 * Calculates local sunrise and sunset for a given date, latitude, longitude, and timezone offset.
 * Uses NOAA solar positioning equations with 50 arcmin depression for refraction and solar radius.
 */
export function calculateSolarTimes(
  dateStr: string, // "YYYY-MM-DD"
  latitude: number,
  longitude: number,
  tzOffsetHours: number = 5.5
): SolarTimes | null {
  try {
    if (!dateStr || isNaN(latitude) || isNaN(longitude)) return null;

    const parts = dateStr.split("-").map((p) => parseInt(p, 10));
    if (parts.length !== 3 || parts.some(isNaN)) return null;

    const [year, month, day] = parts;

    // Day of the year
    const isLeap = (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
    const daysInMonths = [31, isLeap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let dayOfYear = day;
    for (let i = 0; i < month - 1; i++) {
      dayOfYear += daysInMonths[i];
    }

    const lngHour = longitude / 15.0;
    const rad = Math.PI / 180.0;
    const deg = 180.0 / Math.PI;

    function computeSolarEvent(isSunrise: boolean): { hh: number; mm: number; ss: number; totalSeconds: number } {
      const tBase = dayOfYear + ((isSunrise ? 6.0 : 18.0) - lngHour) / 24.0;
      const m = 0.9856 * tBase - 3.289;
      const l =
        (m +
          1.916 * Math.sin(m * rad) +
          0.02 * Math.sin(2 * m * rad) +
          282.634) %
        360.0;

      let ra = (Math.atan(0.91764 * Math.tan(l * rad)) * deg) % 360.0;
      if (ra < 0) ra += 360.0;
      const lQuadrant = Math.floor(l / 90.0) * 90.0;
      const raQuadrant = Math.floor(ra / 90.0) * 90.0;
      ra = (ra + (lQuadrant - raQuadrant)) / 15.0;

      const sinDec = 0.39782 * Math.sin(l * rad);
      const cosDec = Math.cos(Math.asin(sinDec));

      // Standard zenith 90.8333 deg (50 arcmin depression)
      const zenith = 90.8333;
      let cosH =
        (Math.cos(zenith * rad) - sinDec * Math.sin(latitude * rad)) /
        (cosDec * Math.cos(latitude * rad));
      cosH = Math.max(-1.0, Math.min(1.0, cosH));

      const h =
        (isSunrise ? 360.0 - Math.acos(cosH) * deg : Math.acos(cosH) * deg) /
        15.0;
      const localMeanTime = h + ra - 0.06571 * tBase - 6.622;
      let ut = (localMeanTime - lngHour) % 24.0;
      if (ut < 0) ut += 24.0;

      let localHour = (ut + tzOffsetHours) % 24.0;
      if (localHour < 0) localHour += 24.0;

      let hh = Math.floor(localHour);
      const remMin = (localHour - hh) * 60.0;
      let mm = Math.floor(remMin);
      let ss = Math.round((remMin - mm) * 60.0);
      if (ss >= 60) {
        mm += 1;
        ss = 0;
      }
      if (mm >= 60) {
        hh = (hh + 1) % 24;
        mm = 0;
      }

      const totalSeconds = hh * 3600 + mm * 60 + ss;
      return { hh, mm, ss, totalSeconds };
    }

    const sr = computeSolarEvent(true);
    const ss = computeSolarEvent(false);

    function formatTime12(h: number, m: number): string {
      const period = h >= 12 ? "PM" : "AM";
      const h12 = h % 12 === 0 ? 12 : h % 12;
      return `${String(h12).padStart(2, "0")}:${String(m).padStart(2, "0")} ${period}`;
    }

    function formatTime24(h: number, m: number, s: number): string {
      return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    }

    let diffSecs = ss.totalSeconds - sr.totalSeconds;
    if (diffSecs < 0) diffSecs += 86400;
    const dayLengthHours = Math.round((diffSecs / 3600) * 100) / 100;

    return {
      sunriseTime: formatTime12(sr.hh, sr.mm),
      sunsetTime: formatTime12(ss.hh, ss.mm),
      sunrise24: formatTime24(sr.hh, sr.mm, sr.ss),
      sunset24: formatTime24(ss.hh, ss.mm, ss.ss),
      dayLengthHours,
    };
  } catch (err) {
    console.warn("Failed to calculate solar times:", err);
    return null;
  }
}
