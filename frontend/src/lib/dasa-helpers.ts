/**
 * Gokul's Astrological Insights - Dasa Timeline Helpers & Calendar Calculations
 * Exact Fliegel-Van Flandern Julian Day conversion and deterministic calendar age calculation.
 */

import { DasaPeriodNode, DasaPeriodAgeDict } from "./types";
import { LanguageCode } from "./translations";

export interface DateTimeParts {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
  dateStr: string; // YYYY-MM-DD
  timeStr: string; // HH:MM:SS
  iso: string;
}

/**
 * Days in Gregorian months (non-leap year)
 */
const DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function isLeapYear(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

function getDaysInMonth(year: number, month: number): number {
  if (month === 2 && isLeapYear(year)) return 29;
  return DAYS_IN_MONTH[month] || 30;
}

/**
 * Standard Fliegel-Van Flandern Julian Day to Gregorian Date and Time converter
 */
export function jdToCalendarDateTime(
  jd: number,
  utcOffsetHours: number = 0
): DateTimeParts | null {
  if (!jd || jd < 0 || isNaN(jd)) return null;

  const localJd = jd + utcOffsetHours / 24.0;
  const I = Math.floor(localJd + 0.5);
  const F = localJd + 0.5 - I;

  const J = I + 32044;
  const K = Math.floor((4 * J + 3) / 146097);
  const L = J - Math.floor((146097 * K) / 4);
  const M = Math.floor((4 * L + 3) / 1461);
  const N = L - Math.floor((1461 * M) / 4);
  const P = Math.floor((5 * N + 2) / 153);

  const day = N - Math.floor((153 * P + 2) / 5) + 1;
  const month = P + 3 - 12 * Math.floor(P / 10);
  const year = 100 * K + M - 4800 + Math.floor(P / 10);

  let totalSeconds = Math.round(F * 86400);
  if (totalSeconds >= 86400) totalSeconds = 86399;
  if (totalSeconds < 0) totalSeconds = 0;

  const hour = Math.floor(totalSeconds / 3600);
  const minute = Math.floor((totalSeconds % 3600) / 60);
  const second = totalSeconds % 60;

  const mStr = month.toString().padStart(2, "0");
  const dStr = day.toString().padStart(2, "0");
  const hStr = hour.toString().padStart(2, "0");
  const minStr = minute.toString().padStart(2, "0");
  const sStr = second.toString().padStart(2, "0");

  const dateStr = `${year}-${mStr}-${dStr}`;
  const timeStr = `${hStr}:${minStr}:${sStr}`;
  const iso = `${dateStr}T${timeStr}`;

  return { year, month, day, hour, minute, second, dateStr, timeStr, iso };
}

/**
 * Calculate exact Gregorian calendar age as { years, months, days }
 */
export function calculateCalendarAge(
  birthY: number,
  birthM: number,
  birthD: number,
  targetY: number,
  targetM: number,
  targetD: number
): DasaPeriodAgeDict | null {
  if (
    targetY < birthY ||
    (targetY === birthY && targetM < birthM) ||
    (targetY === birthY && targetM === birthM && targetD < birthD)
  ) {
    return null; // Target is before birth
  }

  let y = targetY - birthY;
  let m = targetM - birthM;
  let d = targetD - birthD;

  let curY = targetY;
  let curM = targetM;

  while (d < 0) {
    m -= 1;
    curM -= 1;
    if (curM === 0) {
      curM = 12;
      curY -= 1;
    }
    const daysInPrev = getDaysInMonth(curY, curM);
    d += daysInPrev;
  }

  if (m < 0) {
    y -= 1;
    m += 12;
  }

  return { years: y, months: m, days: d };
}

/**
 * Format age object into human-readable string in English or Tamil
 */
export function formatCalendarAge(
  age: DasaPeriodAgeDict | null | undefined,
  lang: LanguageCode = "en"
): string {
  if (!age) {
    return lang === "ta" ? "வயது கிடைக்கவில்லை" : "Age unavailable";
  }

  const { years, months, days } = age;

  if (lang === "ta") {
    const yUnit = years !== 1 ? "ஆண்டுகள்" : "ஆண்டு";
    const mUnit = months !== 1 ? "மாதங்கள்" : "மாதம்";
    const dUnit = days !== 1 ? "நாட்கள்" : "நாள்";
    return `${years} ${yUnit}, ${months} ${mUnit}, ${days} ${dUnit}`;
  }

  const yUnit = years !== 1 ? "years" : "year";
  const mUnit = months !== 1 ? "months" : "month";
  const dUnit = days !== 1 ? "days" : "day";
  return `${years} ${yUnit}, ${months} ${mUnit}, ${days} ${dUnit}`;
}

/**
 * Format total period duration clearly separated from age
 */
export function formatPeriodDuration(
  durationYears: number,
  durationDays: number,
  lang: LanguageCode = "en"
): string {
  if (durationYears >= 1.0) {
    const yLabel = lang === "ta" ? "ஆண்டுகள்" : "Years";
    return `${durationYears.toFixed(2)} ${yLabel} (${durationDays.toFixed(1)}d)`;
  }
  if (durationDays >= 30.0) {
    const approxMonths = (durationDays / 30.4375).toFixed(1);
    const mLabel = lang === "ta" ? "மாதங்கள்" : "Months";
    const dLabel = lang === "ta" ? "நாட்கள்" : "Days";
    return `${approxMonths} ${mLabel} (${durationDays.toFixed(1)} ${dLabel})`;
  }
  if (durationDays >= 1.0) {
    const dLabel = lang === "ta" ? "நாட்கள்" : "Days";
    return `${durationDays.toFixed(2)} ${dLabel}`;
  }
  // Sub-daily duration (hours/minutes)
  const totalHours = durationDays * 24.0;
  if (totalHours >= 1.0) {
    const hLabel = lang === "ta" ? "மணி" : "Hours";
    return `${totalHours.toFixed(1)} ${hLabel}`;
  }
  const totalMins = totalHours * 60.0;
  const minLabel = lang === "ta" ? "நிமிடங்கள்" : "Mins";
  return `${totalMins.toFixed(0)} ${minLabel}`;
}

/**
 * Find active periods down all 5 levels for a given target Julian Day
 * Using strict half-open interval: [start_jd <= target_jd < end_jd)
 */
export interface ActiveHierarchy {
  mahadasha?: DasaPeriodNode;
  antardasha?: DasaPeriodNode;
  pratyantardasha?: DasaPeriodNode;
  sookshmadasha?: DasaPeriodNode;
  pranadasha?: DasaPeriodNode;
}

export function findActiveHierarchy(
  tree: DasaPeriodNode[],
  targetJd: number,
  utcOffsetHours: number = 0,
  birthDate?: string
): ActiveHierarchy | null {
  if (!tree || tree.length === 0) return null;
  if (targetJd < tree[0].start_jd || targetJd >= tree[tree.length - 1].end_jd) {
    return null;
  }

  const result: ActiveHierarchy = {};
  let currentList: DasaPeriodNode[] | undefined = tree;
  const levelKeys: (keyof ActiveHierarchy)[] = [
    "mahadasha",
    "antardasha",
    "pratyantardasha",
    "sookshmadasha",
    "pranadasha",
  ];

  for (const key of levelKeys) {
    if (!currentList || currentList.length === 0) break;
    let matched: DasaPeriodNode | undefined = undefined;
    for (const node of currentList) {
      if (node.start_jd <= targetJd && targetJd < node.end_jd) {
        matched = node;
        break;
      }
    }
    if (!matched && currentList.length > 0 && targetJd === currentList[currentList.length - 1].end_jd) {
      matched = currentList[currentList.length - 1];
    }
    if (matched) {
      result[key] = matched;
      if (matched.sub_periods && matched.sub_periods.length > 0) {
        currentList = matched.sub_periods;
      } else {
        currentList = generateChildSubPeriods(matched, utcOffsetHours, birthDate);
      }
    } else {
      break;
    }
  }

  return result.mahadasha ? result : null;
}

/**
 * Visual styling and metadata for each level in the 5-level hierarchy
 */
export interface LevelMetadata {
  name: string;
  nameTamil: string;
  badgeShort: string;
  badgeShortTamil: string;
  badgeClass: string;
  borderClass: string;
  indentClass: string;
  levelNumber: number;
}

export function getLevelMetadata(level: string): LevelMetadata {
  const norm = level.toLowerCase();
  if (norm.includes("maha")) {
    return {
      name: "Mahadasha",
      nameTamil: "மகா தசை",
      badgeShort: "Maha",
      badgeShortTamil: "மகா",
      badgeClass: "bg-amber-100 text-amber-900 border-amber-300",
      borderClass: "border-amber-200",
      indentClass: "pl-0",
      levelNumber: 1,
    };
  }
  if (norm.includes("antar") && !norm.includes("praty")) {
    return {
      name: "Antardasha (Bhukti)",
      nameTamil: "அந்தர்தசை (புக்தி)",
      badgeShort: "Bhukti",
      badgeShortTamil: "புக்தி",
      badgeClass: "bg-indigo-100 text-indigo-900 border-indigo-300",
      borderClass: "border-indigo-200",
      indentClass: "pl-3 sm:pl-5",
      levelNumber: 2,
    };
  }
  if (norm.includes("praty")) {
    return {
      name: "Pratyantardasha (Antaram)",
      nameTamil: "பிரத்யந்தர தசை (அந்தரம்)",
      badgeShort: "Antaram",
      badgeShortTamil: "அந்தரம்",
      badgeClass: "bg-emerald-100 text-emerald-900 border-emerald-300",
      borderClass: "border-emerald-200",
      indentClass: "pl-6 sm:pl-10",
      levelNumber: 3,
    };
  }
  if (norm.includes("sookshma")) {
    return {
      name: "Sookshmadasha",
      nameTamil: "சூட்சும தசை",
      badgeShort: "Sookshma",
      badgeShortTamil: "சூட்சுமம்",
      badgeClass: "bg-purple-100 text-purple-900 border-purple-300",
      borderClass: "border-purple-200",
      indentClass: "pl-9 sm:pl-14",
      levelNumber: 4,
    };
  }
  return {
    name: "Pranadasha",
    nameTamil: "பிராண தசை",
    badgeShort: "Prana",
    badgeShortTamil: "பிராணன்",
    badgeClass: "bg-rose-100 text-rose-900 border-rose-300",
    borderClass: "border-rose-200",
    indentClass: "pl-12 sm:pl-18",
    levelNumber: 5,
  };
}

export const VIMSHOTTARI_ORDER: string[] = [
  "Ketu", "Venus", "Sun", "Moon", "Mars",
  "Rahu", "Jupiter", "Saturn", "Mercury",
];

export const VIMSHOTTARI_YEARS: Record<string, number> = {
  Ketu: 7,
  Venus: 20,
  Sun: 6,
  Moon: 10,
  Mars: 7,
  Rahu: 18,
  Jupiter: 16,
  Saturn: 19,
  Mercury: 17,
};

export const LEVEL_NAMES: string[] = [
  "Mahadasha",
  "Antardasha",
  "Pratyantardasha",
  "Sookshmadasha",
  "Pranadasha",
];

/**
 * Generate authentic 9 child subperiods on-the-fly using canonical Vimshottari proportions.
 * Ensures Sookshamam and Pranam are deterministically present and expandable across any chart.
 */
export function generateChildSubPeriods(
  parentNode: DasaPeriodNode,
  utcOffsetHours: number = 0,
  birthDate?: string
): DasaPeriodNode[] {
  const currentDepth = getLevelMetadata(parentNode.level).levelNumber;
  if (currentDepth >= 5) return [];

  const childLevel = LEVEL_NAMES[currentDepth];
  const parentLord = parentNode.lord;
  const parentPos = VIMSHOTTARI_ORDER.indexOf(parentLord);
  if (parentPos === -1) return [];

  const isBirthChain = !!parentNode.is_active_at_birth;
  let parentTheoStartJd = parentNode.theoretical_start_jd;
  let parentTheoEndJd = parentNode.theoretical_end_jd ?? parentNode.end_jd;

  if (parentTheoStartJd === undefined || isNaN(parentTheoStartJd)) {
    if (isBirthChain && currentDepth === 1) {
      const fullYears = VIMSHOTTARI_YEARS[parentLord] ?? 120;
      parentTheoStartJd = parentTheoEndJd - fullYears * 365.25;
    } else {
      parentTheoStartJd = parentNode.start_jd;
    }
  }

  const parentTheoDur = parentTheoEndJd - parentTheoStartJd;
  const birthJd = parentNode.start_jd;

  const children: DasaPeriodNode[] = [];
  let currTheoJd = parentTheoStartJd;

  let bYear: number | undefined;
  let bMonth: number | undefined;
  let bDay: number | undefined;
  if (birthDate) {
    const parts = birthDate.split("-").map(Number);
    if (parts.length === 3 && !isNaN(parts[0]) && !isNaN(parts[1]) && !isNaN(parts[2])) {
      bYear = parts[0];
      bMonth = parts[1];
      bDay = parts[2];
    }
  }

  for (let i = 0; i < 9; i++) {
    const lord = VIMSHOTTARI_ORDER[(parentPos + i) % 9];
    const cTheoDur = i === 8 ? parentTheoEndJd - currTheoJd : parentTheoDur * (VIMSHOTTARI_YEARS[lord] / 120.0);
    const cTheoEndJd = i === 8 ? parentTheoEndJd : currTheoJd + cTheoDur;
    const cTheoStartJd = currTheoJd;
    currTheoJd = cTheoEndJd;

    let cStartJd: number;
    let cEndJd: number;
    let cIsActiveAtBirth = false;

    if (!isBirthChain) {
      cStartJd = cTheoStartJd;
      cEndJd = cTheoEndJd;
      cIsActiveAtBirth = false;
    } else {
      // 1. Completed before birth -> omit
      if (cTheoEndJd <= birthJd + 1e-7) {
        continue;
      }
      // 2. Spans birth instant -> active at birth (clipped to birthJd)
      if (cTheoStartJd <= birthJd && cTheoEndJd > birthJd) {
        cStartJd = birthJd;
        cEndJd = cTheoEndJd;
        cIsActiveAtBirth = true;
      } else {
        // 3. Starts after birth -> full canonical duration
        cStartJd = cTheoStartJd;
        cEndJd = cTheoEndJd;
        cIsActiveAtBirth = false;
      }
    }

    const durDays = cEndJd - cStartJd;
    const sDt = jdToCalendarDateTime(cStartJd, utcOffsetHours);
    const eDt = jdToCalendarDateTime(cEndJd, utcOffsetHours);

    const isSubDaily = currentDepth + 1 >= 4;
    const sDateIso = sDt ? (isSubDaily ? `${sDt.dateStr}T${sDt.timeStr}` : sDt.dateStr) : undefined;
    const eDateIso = eDt ? (isSubDaily ? `${eDt.dateStr}T${eDt.timeStr}` : eDt.dateStr) : undefined;

    const tsDt = jdToCalendarDateTime(cTheoStartJd, utcOffsetHours);
    const teDt = jdToCalendarDateTime(cTheoEndJd, utcOffsetHours);
    const theoSDateIso = tsDt ? (isSubDaily ? `${tsDt.dateStr}T${tsDt.timeStr}` : tsDt.dateStr) : undefined;
    const theoEDateIso = teDt ? (isSubDaily ? `${teDt.dateStr}T${teDt.timeStr}` : teDt.dateStr) : undefined;

    let startAge: string | undefined;
    let endAge: string | undefined;
    let startAgeDict: DasaPeriodAgeDict | undefined;
    let endAgeDict: DasaPeriodAgeDict | undefined;

    if (bYear !== undefined && bMonth !== undefined && bDay !== undefined && sDt && eDt) {
      const sAgeObj = calculateCalendarAge(bYear, bMonth, bDay, sDt.year, sDt.month, sDt.day);
      const eAgeObj = calculateCalendarAge(bYear, bMonth, bDay, eDt.year, eDt.month, eDt.day);
      if (sAgeObj) {
        startAge = formatCalendarAge(sAgeObj, "en");
        startAgeDict = sAgeObj;
      }
      if (eAgeObj) {
        endAge = formatCalendarAge(eAgeObj, "en");
        endAgeDict = eAgeObj;
      }
    }

    children.push({
      lord,
      level: childLevel,
      start_jd: cStartJd,
      end_jd: cEndJd,
      duration_days: durDays,
      duration_years: durDays / 365.25,
      start_date_iso: sDateIso,
      end_date_iso: eDateIso,
      start_age: startAge,
      end_age: endAge,
      start_age_dict: startAgeDict,
      end_age_dict: endAgeDict,
      theoretical_start_jd: cTheoStartJd,
      theoretical_end_jd: cTheoEndJd,
      theoretical_duration_days: cTheoDur,
      theoretical_duration_years: cTheoDur / 365.25,
      theoretical_start_date_iso: theoSDateIso,
      theoretical_end_date_iso: theoEDateIso,
      is_active_at_birth: cIsActiveAtBirth,
      sub_periods: [],
    });
  }

  return children;
}

/**
 * Automatically calculates expanded row keys for the active path up to maxExpandDepth.
 * Used to expand the current Dasa, Bhukti, and sub-divisions when the table is opened.
 */
export function getActivePathExpandedKeys(
  tree: DasaPeriodNode[] | undefined,
  targetJd: number,
  utcOffsetHours: number = 0,
  birthDate?: string,
  maxExpandDepth: number = 3
): Record<string, boolean> {
  const map: Record<string, boolean> = {};
  if (!tree || tree.length === 0 || !targetJd) return map;

  const recurse = (nodes: DasaPeriodNode[], prefix: string, currDepth: number) => {
    for (let idx = 0; idx < nodes.length; idx++) {
      const n = nodes[idx];
      const k = prefix ? `${prefix}-${idx}` : `${idx}`;
      if (targetJd >= n.start_jd && targetJd < n.end_jd) {
        map[k] = true;
        if (currDepth < maxExpandDepth) {
          const ch =
            n.sub_periods && n.sub_periods.length > 0
              ? n.sub_periods
              : generateChildSubPeriods(n, utcOffsetHours, birthDate);
          if (ch && ch.length > 0) {
            recurse(ch, k, currDepth + 1);
          }
        }
        break;
      }
    }
  };

  tree.forEach((m, mIdx) => {
    if (targetJd >= m.start_jd && targetJd < m.end_jd) {
      const bList =
        m.sub_periods && m.sub_periods.length > 0
          ? m.sub_periods
          : generateChildSubPeriods(m, utcOffsetHours, birthDate);
      recurse(bList, `${mIdx}`, 2);
    }
  });

  return map;
}
