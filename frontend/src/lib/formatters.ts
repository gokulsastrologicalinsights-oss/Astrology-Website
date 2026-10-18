/**
 * Gokul's Astrological Insights - Astronomical Coordinate Formatters
 * Formats decimal degrees to DMS with strict 60-second and 60-minute carryover.
 */

/**
 * Formats a decimal degree into Degrees, Minutes, and Seconds (DMS) string.
 * Example: 14.5 -> 14° 30' 00"
 * Handles mathematical carryover when seconds round up to 60 (e.g. 14.99999° -> 15° 00' 00").
 */
export function formatDms(deg: number): string {
  if (isNaN(deg) || deg === null || deg === undefined) return "—";
  let norm = deg % 360;
  if (norm < 0) norm += 360;

  let d = Math.floor(norm);
  const minFloat = (norm - d) * 60;
  let m = Math.floor(minFloat);
  let s = Math.round((minFloat - m) * 60);

  if (s >= 60) {
    s = 0;
    m += 1;
    if (m >= 60) {
      m = 0;
      d = (d + 1) % 360;
    }
  }

  return `${d}° ${m.toString().padStart(2, "0")}' ${s.toString().padStart(2, "0")}"`;
}

/**
 * Formats decimal degree into compact Degree and Minute (DM) string for chart compartments.
 * Example: 14.5 -> 14°30'
 */
export function formatDm(deg: number): string {
  if (isNaN(deg) || deg === null || deg === undefined) return "—";
  let norm = deg % 360;
  if (norm < 0) norm += 360;

  let d = Math.floor(norm);
  const minFloat = (norm - d) * 60;
  let m = Math.round(minFloat);

  if (m >= 60) {
    m = 0;
    d = (d + 1) % 360;
  }

  return `${d}°${m.toString().padStart(2, "0")}'`;
}

/**
 * Formats database permanent display_number into small serial string with leading zero.
 * Example: 1 -> "01", 9 -> "09", 12 -> "12"
 */
export function formatSerialNumber(num: number | null | undefined): string {
  if (num === null || num === undefined || isNaN(num) || num <= 0) return "—";
  return num < 10 ? `0${num}` : `${num}`;
}

/**
 * Formats birth date string (YYYY-MM-DD) into canonical display format (e.g. "15 January 1998").
 * Parses date string directly without Date object timezone conversion to preserve exact birth date.
 */
export function formatBirthDate(
  dateStr: string | null | undefined,
  language: "en" | "ta" = "en"
): string {
  if (!dateStr || typeof dateStr !== "string") return "—";
  const clean = dateStr.trim();
  const parts = clean.split("-");
  if (parts.length !== 3) return clean;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10);
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return clean;

  const monthsEn = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const monthsTa = [
    "ஜனவரி",
    "பிப்ரவரி",
    "மார்ச்",
    "ஏப்ரல்",
    "மே",
    "ஜூன்",
    "ஜூலை",
    "ஆகஸ்ட்",
    "செப்டம்பர்",
    "அக்டோபர்",
    "நவம்பர்",
    "டிசம்பர்",
  ];

  if (month >= 1 && month <= 12) {
    const monthName = language === "ta" ? monthsTa[month - 1] : monthsEn[month - 1];
    return `${day} ${monthName} ${year}`;
  }
  return clean;
}

/**
 * Formats birth time string (HH:MM or HH:MM:SS) into 12-hour AM/PM format (e.g. "10:30 AM").
 * Preserves stored timezone or UTC offset without accidental browser conversion.
 */
export function formatBirthTime(timeStr: string | null | undefined): string {
  if (!timeStr || typeof timeStr !== "string") return "—";
  const clean = timeStr.trim();
  const match = clean.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?/);
  if (!match) return clean;
  const hours24 = parseInt(match[1], 10);
  const minutes = match[2];
  if (isNaN(hours24)) return clean;
  const period = hours24 >= 12 ? "PM" : "AM";
  const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
  return `${hours12.toString().padStart(2, "0")}:${minutes} ${period}`;
}

