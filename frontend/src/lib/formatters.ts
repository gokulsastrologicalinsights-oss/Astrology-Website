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

/**
 * Calculates current calendar age in full completed years from YYYY-MM-DD birth date.
 */
export function calculateCalendarAge(birthDateStr?: string | null): number | null {
  if (!birthDateStr || typeof birthDateStr !== "string") return null;
  const parts = birthDateStr.trim().split("-");
  if (parts.length < 3) return null;
  const y = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10) - 1;
  const d = parseInt(parts[2], 10);
  if (isNaN(y) || isNaN(m) || isNaN(d)) return null;

  const today = new Date();
  let age = today.getFullYear() - y;
  const mDiff = today.getMonth() - m;
  if (mDiff < 0 || (mDiff === 0 && today.getDate() < d)) {
    age--;
  }
  return age >= 0 ? age : null;
}

export interface ParsedTime12Result {
  isValid: boolean;
  time24?: string;
  errorEn?: string;
  errorTa?: string;
}

/**
 * Parses a 12-hour time string (e.g. "10:30" or "10:30:15") and AM/PM period
 * into an authoritative 24-hour "HH:MM:SS" string for astronomical calculation.
 */
export function parse12HourTimeTo24(
  timeStr: string | null | undefined,
  period: "AM" | "PM"
): ParsedTime12Result {
  if (!timeStr || !timeStr.trim()) {
    return {
      isValid: false,
      errorEn: "Birth time is required.",
      errorTa: "பிறந்த நேரம் தேவை.",
    };
  }

  let clean = timeStr.trim().replace(/\./g, ":");

  // If user pasted or typed AM/PM into the text box, detect and strip
  let detectedPeriod = period;
  if (/am/i.test(clean)) {
    detectedPeriod = "AM";
    clean = clean.replace(/am/gi, "").trim();
  } else if (/pm/i.test(clean)) {
    detectedPeriod = "PM";
    clean = clean.replace(/pm/gi, "").trim();
  }

  const match = clean.match(/^(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?$/);
  if (!match) {
    return {
      isValid: false,
      errorEn: "Please enter time in HH:MM or HH:MM:SS format (e.g. 10:30).",
      errorTa: "வடிவம் HH:MM அல்லது HH:MM:SS ஆக இருக்க வேண்டும் (எ.கா: 10:30).",
    };
  }

  const hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  const seconds = match[3] !== undefined ? parseInt(match[3], 10) : 0;

  if (isNaN(hours) || hours < 1 || hours > 12) {
    return {
      isValid: false,
      errorEn: "Hours must be between 1 and 12 in 12-hour format.",
      errorTa: "12 மணி நேர அமைப்பில் மணி 1 முதல் 12 வரை இருக்க வேண்டும்.",
    };
  }

  if (isNaN(minutes) || minutes < 0 || minutes > 59) {
    return {
      isValid: false,
      errorEn: "Minutes must be between 00 and 59.",
      errorTa: "நிமிடம் 00 முதல் 59 வரை இருக்க வேண்டும்.",
    };
  }

  if (isNaN(seconds) || seconds < 0 || seconds > 59) {
    return {
      isValid: false,
      errorEn: "Seconds must be between 00 and 59.",
      errorTa: "வினாடி 00 முதல் 59 வரை இருக்க வேண்டும்.",
    };
  }

  let hours24 = hours;
  if (detectedPeriod === "AM") {
    if (hours === 12) {
      hours24 = 0;
    }
  } else {
    // PM
    if (hours !== 12) {
      hours24 = hours + 12;
    }
  }

  const hh = hours24.toString().padStart(2, "0");
  const mm = minutes.toString().padStart(2, "0");
  const ss = seconds.toString().padStart(2, "0");

  return {
    isValid: true,
    time24: `${hh}:${mm}:${ss}`,
  };
}

/**
 * Splits a 24-hour time string into a 12-hour display string and AM/PM period.
 */
export function parse24To12(time24?: string | null): { time12: string; period: "AM" | "PM" } {
  if (!time24 || !time24.trim()) {
    return { time12: "", period: "AM" };
  }
  const clean = time24.trim();
  const match = clean.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?/);
  if (!match) {
    return { time12: clean, period: "AM" };
  }
  const hours24 = parseInt(match[1], 10);
  const minutes = match[2];
  const seconds = match[3];
  if (isNaN(hours24)) return { time12: clean, period: "AM" };

  const period: "AM" | "PM" = hours24 >= 12 ? "PM" : "AM";
  const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
  const hh = hours12.toString().padStart(2, "0");
  const time12 = seconds && seconds !== "00" ? `${hh}:${minutes}:${seconds}` : `${hh}:${minutes}`;

  return { time12, period };
}

