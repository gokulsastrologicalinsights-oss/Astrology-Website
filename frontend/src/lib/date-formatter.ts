/**
 * Gokul's Astrological Insights - Authoritative Date & Time Standard Library
 * 
 * Standard Format Across the Entire Website:
 * - Date Format: DD/MM/YYYY (or DD-MM-YYYY)
 * - Date + Time Format: DD/MM/YYYY, hh:mm A
 * - Form input helper for HTML5 date (YYYY-MM-DD to DD/MM/YYYY and vice versa)
 * - Tamil & English localized display formats supporting (DD/MM/YYYY or DD Month YYYY)
 */

export type DateSeparator = "/" | "-";

export interface FormatDateOptions {
  separator?: DateSeparator; // Default is "/" -> DD/MM/YYYY
  includeTime?: boolean;     // Appends 12-hour time (e.g. 14/05/1998, 10:30 AM)
  timeSeconds?: boolean;     // Includes seconds if includeTime is true
  padDayMonth?: boolean;     // If true (default), single digits get leading zero: 05/04/2024
}

export interface DateParts {
  day: number;
  month: number;
  year: number;
  hours?: number;
  minutes?: number;
  seconds?: number;
}

/**
 * Parses any date input into sanitized numeric day, month, year, hours, minutes, seconds.
 * Supports:
 * - Date object
 * - ISO string: "2024-05-18T10:30:00Z"
 * - HTML date value: "YYYY-MM-DD"
 * - DD/MM/YYYY or DD-MM-YYYY
 * - Timestamps (number)
 */
export function parseDateInput(input: string | number | Date | null | undefined): DateParts | null {
  if (input === null || input === undefined || input === "") return null;

  if (input instanceof Date) {
    if (isNaN(input.getTime())) return null;
    return {
      day: input.getDate(),
      month: input.getMonth() + 1,
      year: input.getFullYear(),
      hours: input.getHours(),
      minutes: input.getMinutes(),
      seconds: input.getSeconds(),
    };
  }

  if (typeof input === "number") {
    const d = new Date(input);
    if (isNaN(d.getTime())) return null;
    return {
      day: d.getDate(),
      month: d.getMonth() + 1,
      year: d.getFullYear(),
      hours: d.getHours(),
      minutes: d.getMinutes(),
      seconds: d.getSeconds(),
    };
  }

  const str = String(input).trim();
  if (!str) return null;

  // Pattern: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss
  const isoMatch = str.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[T\s](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?/);
  if (isoMatch) {
    return {
      year: parseInt(isoMatch[1], 10),
      month: parseInt(isoMatch[2], 10),
      day: parseInt(isoMatch[3], 10),
      hours: isoMatch[4] !== undefined ? parseInt(isoMatch[4], 10) : undefined,
      minutes: isoMatch[5] !== undefined ? parseInt(isoMatch[5], 10) : undefined,
      seconds: isoMatch[6] !== undefined ? parseInt(isoMatch[6], 10) : undefined,
    };
  }

  // Pattern: DD/MM/YYYY or DD-MM-YYYY
  const dmyMatch = str.match(/^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})(?:[T\s](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?/);
  if (dmyMatch) {
    return {
      day: parseInt(dmyMatch[1], 10),
      month: parseInt(dmyMatch[2], 10),
      year: parseInt(dmyMatch[3], 10),
      hours: dmyMatch[4] !== undefined ? parseInt(dmyMatch[4], 10) : undefined,
      minutes: dmyMatch[5] !== undefined ? parseInt(dmyMatch[5], 10) : undefined,
      seconds: dmyMatch[6] !== undefined ? parseInt(dmyMatch[6], 10) : undefined,
    };
  }

  // Standard fallback
  const fallback = new Date(str);
  if (!isNaN(fallback.getTime())) {
    return {
      day: fallback.getDate(),
      month: fallback.getMonth() + 1,
      year: fallback.getFullYear(),
      hours: fallback.getHours(),
      minutes: fallback.getMinutes(),
      seconds: fallback.getSeconds(),
    };
  }

  return null;
}

/**
 * Standard date formatter for the whole website: DD/MM/YYYY
 * Example:
 * formatDate("2024-05-09") -> "09/05/2024"
 * formatDate(new Date()) -> "13/11/2026"
 */
export function formatDate(
  input: string | number | Date | null | undefined,
  separator: DateSeparator = "/"
): string {
  const parts = parseDateInput(input);
  if (!parts) return "—";

  const dd = parts.day.toString().padStart(2, "0");
  const mm = parts.month.toString().padStart(2, "0");
  const yyyy = parts.year.toString().padStart(4, "0");

  return `${dd}${separator}${mm}${separator}${yyyy}`;
}

/**
 * Alias for strict Date-Month-Year format: DD/MM/YYYY
 */
export function formatDateDMY(input: string | number | Date | null | undefined): string {
  return formatDate(input, "/");
}

/**
 * Format Date with Dash separator: DD-MM-YYYY
 */
export function formatDateDMYDash(input: string | number | Date | null | undefined): string {
  return formatDate(input, "-");
}

/**
 * Standard Date & Time Formatter: DD/MM/YYYY, hh:mm A
 * Example: "13/11/2026, 11:05 AM"
 */
export function formatDateTime(
  input: string | number | Date | null | undefined,
  includeSeconds: boolean = false,
  separator: DateSeparator = "/"
): string {
  const parts = parseDateInput(input);
  if (!parts) return "—";

  const dateStr = formatDate(input, separator);

  if (parts.hours === undefined || parts.minutes === undefined) {
    return dateStr;
  }

  const hours24 = parts.hours;
  const period = hours24 >= 12 ? "PM" : "AM";
  const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
  const hh = hours12.toString().padStart(2, "0");
  const mm = parts.minutes.toString().padStart(2, "0");

  if (includeSeconds && parts.seconds !== undefined) {
    const ss = parts.seconds.toString().padStart(2, "0");
    return `${dateStr}, ${hh}:${mm}:${ss} ${period}`;
  }

  return `${dateStr}, ${hh}:${mm} ${period}`;
}

/**
 * Standard 12-hour Time Formatter: hh:mm A
 * Example: "10:30 AM"
 */
export function formatTime12(
  timeStr: string | null | undefined,
  fallbackDate?: string | Date
): string {
  if (!timeStr || typeof timeStr !== "string") {
    if (fallbackDate) {
      const parts = parseDateInput(fallbackDate);
      if (parts && parts.hours !== undefined && parts.minutes !== undefined) {
        const period = parts.hours >= 12 ? "PM" : "AM";
        const h12 = parts.hours % 12 === 0 ? 12 : parts.hours % 12;
        return `${h12.toString().padStart(2, "0")}:${parts.minutes.toString().padStart(2, "0")} ${period}`;
      }
    }
    return "—";
  }

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
 * Converts standard HTML input value (YYYY-MM-DD) to display DD/MM/YYYY
 */
export function htmlDateToDisplay(htmlDate: string | null | undefined): string {
  if (!htmlDate) return "";
  return formatDate(htmlDate, "/");
}

/**
 * Converts user input DD/MM/YYYY or DD-MM-YYYY to HTML input value YYYY-MM-DD
 */
export function displayToHtmlDate(displayDate: string | null | undefined): string {
  if (!displayDate) return "";
  const parts = parseDateInput(displayDate);
  if (!parts) return "";
  const yyyy = parts.year.toString().padStart(4, "0");
  const mm = parts.month.toString().padStart(2, "0");
  const dd = parts.day.toString().padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

/**
 * Validates whether string is in valid DD/MM/YYYY or DD-MM-YYYY format
 */
export function isValidDMY(dateStr: string | null | undefined): boolean {
  if (!dateStr) return false;
  const match = dateStr.trim().match(/^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$/);
  if (!match) return false;
  const day = parseInt(match[1], 10);
  const month = parseInt(match[2], 10);
  const year = parseInt(match[3], 10);

  if (year < 1800 || year > 2200) return false;
  if (month < 1 || month > 12) return false;

  const daysInMonth = new Date(year, month, 0).getDate();
  return day >= 1 && day <= daysInMonth;
}
