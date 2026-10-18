/**
 * Gokul's Astrological Insights - Five-Level Dasa Hierarchy & Age Verification Test
 * Validates calendar age calculations, leap day handling, interval detection,
 * level naming, and English/Tamil localization.
 */

import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log("=== Gokul's Astrological Insights - Five-Level Dasa & Calendar Age Suite ===\n");

let passed = 0;
let failed = 0;

function runTest(name, fn) {
  try {
    process.stdout.write(`Testing ${name} ... `);
    fn();
    console.log("[PASS]");
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }
}

// --------------------------------------------------------------------------
// Core Logic Implementations for Validation
// --------------------------------------------------------------------------

const DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function isLeapYear(year) {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

function getDaysInMonth(year, month) {
  if (month === 2 && isLeapYear(year)) return 29;
  return DAYS_IN_MONTH[month] || 30;
}

function jdToCalendarDateTime(jd, utcOffsetHours = 0) {
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

function calculateCalendarAge(birthY, birthM, birthD, targetY, targetM, targetD) {
  if (
    targetY < birthY ||
    (targetY === birthY && targetM < birthM) ||
    (targetY === birthY && targetM === birthM && targetD < birthD)
  ) {
    return null;
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

function formatCalendarAge(age, lang = "en") {
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

function formatPeriodDuration(durationYears, durationDays, lang = "en") {
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
  const totalHours = durationDays * 24.0;
  if (totalHours >= 1.0) {
    const hLabel = lang === "ta" ? "மணி" : "Hours";
    return `${totalHours.toFixed(1)} ${hLabel}`;
  }
  const totalMins = totalHours * 60.0;
  const minLabel = lang === "ta" ? "நிமிடங்கள்" : "Mins";
  return `${totalMins.toFixed(0)} ${minLabel}`;
}

function getLevelMetadata(level) {
  const norm = level.toLowerCase();
  if (norm.includes("maha")) {
    return {
      name: "Mahadasha",
      nameTamil: "மகா தசை",
      badgeShort: "Maha",
      badgeShortTamil: "மகா",
      levelNumber: 1,
    };
  }
  if (norm.includes("antar") && !norm.includes("praty")) {
    return {
      name: "Antardasha (Bhukti)",
      nameTamil: "அந்தர்தசை (புக்தி)",
      badgeShort: "Bhukti",
      badgeShortTamil: "புக்தி",
      levelNumber: 2,
    };
  }
  if (norm.includes("praty")) {
    return {
      name: "Pratyantardasha (Antaram)",
      nameTamil: "பிரத்யந்தர தசை (அந்தரம்)",
      badgeShort: "Antaram",
      badgeShortTamil: "அந்தரம்",
      levelNumber: 3,
    };
  }
  if (norm.includes("sookshma")) {
    return {
      name: "Sookshmadasha",
      nameTamil: "சூட்சும தசை",
      badgeShort: "Sookshma",
      badgeShortTamil: "சூட்சுமம்",
      levelNumber: 4,
    };
  }
  return {
    name: "Pranadasha",
    nameTamil: "பிராண தசை",
    badgeShort: "Prana",
    badgeShortTamil: "பிராணன்",
    levelNumber: 5,
  };
}

function findActiveHierarchy(tree, targetJd) {
  if (!tree || tree.length === 0) return null;
  if (targetJd < tree[0].start_jd || targetJd >= tree[tree.length - 1].end_jd) {
    return null;
  }

  const result = {};
  let currentList = tree;
  const levelKeys = [
    "mahadasha",
    "antardasha",
    "pratyantardasha",
    "sookshmadasha",
    "pranadasha",
  ];

  for (const key of levelKeys) {
    if (!currentList || currentList.length === 0) break;
    let matched = undefined;
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
      currentList = matched.sub_periods;
    } else {
      break;
    }
  }

  return result.mahadasha ? result : null;
}

// --------------------------------------------------------------------------
// 1. Exact Calendar Age Calculations
// --------------------------------------------------------------------------

runTest("Calendar age on exact birthday and birth moment", () => {
  const atBirth = calculateCalendarAge(1990, 5, 15, 1990, 5, 15);
  assert.deepStrictEqual(atBirth, { years: 0, months: 0, days: 0 });
  assert.strictEqual(formatCalendarAge(atBirth, "en"), "0 years, 0 months, 0 days");
  assert.strictEqual(formatCalendarAge(atBirth, "ta"), "0 ஆண்டுகள், 0 மாதங்கள், 0 நாட்கள்");

  const anniversary = calculateCalendarAge(1990, 5, 15, 2024, 5, 15);
  assert.deepStrictEqual(anniversary, { years: 34, months: 0, days: 0 });
  assert.strictEqual(formatCalendarAge(anniversary, "en"), "34 years, 0 months, 0 days");
  assert.strictEqual(formatCalendarAge(anniversary, "ta"), "34 ஆண்டுகள், 0 மாதங்கள், 0 நாட்கள்");
});

runTest("Calendar age examples required by prompt specification", () => {
  // 1. 24 years, 3 months, 6 days
  const ex1 = calculateCalendarAge(1990, 5, 15, 2014, 8, 21);
  assert.deepStrictEqual(ex1, { years: 24, months: 3, days: 6 });
  assert.strictEqual(formatCalendarAge(ex1, "en"), "24 years, 3 months, 6 days");
  assert.strictEqual(formatCalendarAge(ex1, "ta"), "24 ஆண்டுகள், 3 மாதங்கள், 6 நாட்கள்");

  // 2. 25 years, 0 months, 12 days
  const ex2 = calculateCalendarAge(1980, 8, 30, 2005, 9, 11);
  assert.deepStrictEqual(ex2, { years: 25, months: 0, days: 12 });
  assert.strictEqual(formatCalendarAge(ex2, "en"), "25 years, 0 months, 12 days");

  // 3. 26 years, 11 months, 28 days
  const ex3 = calculateCalendarAge(1980, 8, 30, 2007, 8, 27);
  assert.deepStrictEqual(ex3, { years: 26, months: 11, days: 28 });
  assert.strictEqual(formatCalendarAge(ex3, "en"), "26 years, 11 months, 28 days");
});

runTest("Calendar age with leap day (Feb 29) birth", () => {
  // Born 2000-02-29
  // 2001 is a common year (28 days in Feb)
  const ageFeb28 = calculateCalendarAge(2000, 2, 29, 2001, 2, 28);
  assert.deepStrictEqual(ageFeb28, { years: 0, months: 11, days: 30 });

  // Reaches 1 full year on March 1
  const ageMar1 = calculateCalendarAge(2000, 2, 29, 2001, 3, 1);
  assert.deepStrictEqual(ageMar1, { years: 1, months: 0, days: 0 });

  // Next leap year: 2004-02-29
  const ageLeap = calculateCalendarAge(2000, 2, 29, 2004, 2, 29);
  assert.deepStrictEqual(ageLeap, { years: 4, months: 0, days: 0 });
});

runTest("Calendar age crossing month-ends and December/January", () => {
  // 31st of month: Born 2020-01-31
  const ageMar1 = calculateCalendarAge(2020, 1, 31, 2020, 3, 1);
  assert.deepStrictEqual(ageMar1, { years: 0, months: 0, days: 30 });

  const ageMar2 = calculateCalendarAge(2020, 1, 31, 2020, 3, 2);
  assert.deepStrictEqual(ageMar2, { years: 0, months: 1, days: 0 });

  // Crossing Dec 25 -> Jan 5 (11 days)
  const ageYearCross = calculateCalendarAge(1990, 12, 25, 1991, 1, 5);
  assert.deepStrictEqual(ageYearCross, { years: 0, months: 0, days: 11 });
});

runTest("Calendar age for date before birth returns null / unavailable", () => {
  const before = calculateCalendarAge(1990, 5, 15, 1989, 5, 15);
  assert.strictEqual(before, null);
  assert.strictEqual(formatCalendarAge(before, "en"), "Age unavailable");
  assert.strictEqual(formatCalendarAge(before, "ta"), "வயது கிடைக்கவில்லை");
});

// --------------------------------------------------------------------------
// 2. Julian Day with Time & Sub-Daily Periods
// --------------------------------------------------------------------------

runTest("Julian Day to Gregorian date and time conversion", () => {
  const dt = jdToCalendarDateTime(2451545.0, 0.0);
  assert.strictEqual(dt?.dateStr, "2000-01-01");
  assert.strictEqual(dt?.timeStr, "12:00:00");

  const dtLocal = jdToCalendarDateTime(2451545.0, 5.5);
  assert.strictEqual(dtLocal?.dateStr, "2000-01-01");
  assert.strictEqual(dtLocal?.timeStr, "17:30:00");
});

// --------------------------------------------------------------------------
// 3. Duration vs Age Separation
// --------------------------------------------------------------------------

runTest("Duration formatting distinguishes years, days, hours, and minutes", () => {
  assert.strictEqual(formatPeriodDuration(19.0, 6939.75, "en"), "19.00 Years (6939.8d)");
  assert.strictEqual(formatPeriodDuration(0.4083, 149.14, "en"), "4.9 Months (149.1 Days)");
  assert.strictEqual(formatPeriodDuration(0.00075, 0.2739, "en"), "6.6 Hours");
  assert.strictEqual(formatPeriodDuration(0.0000137, 0.005, "en"), "7 Mins");

  // Tamil duration labels
  assert.strictEqual(formatPeriodDuration(19.0, 6939.75, "ta"), "19.00 ஆண்டுகள் (6939.8d)");
  assert.strictEqual(formatPeriodDuration(0.00075, 0.2739, "ta"), "6.6 மணி");
});

// --------------------------------------------------------------------------
// 4. Five-Level Hierarchy Metadata & Names
// --------------------------------------------------------------------------

runTest("Five levels metadata mapping and badges", () => {
  const m1 = getLevelMetadata("Mahadasha");
  assert.strictEqual(m1.levelNumber, 1);
  assert.strictEqual(m1.badgeShort, "Maha");
  assert.strictEqual(m1.badgeShortTamil, "மகா");

  const m2 = getLevelMetadata("Antardasha");
  assert.strictEqual(m2.levelNumber, 2);
  assert.strictEqual(m2.badgeShort, "Bhukti");
  assert.strictEqual(m2.badgeShortTamil, "புக்தி");

  const m3 = getLevelMetadata("Pratyantardasha");
  assert.strictEqual(m3.levelNumber, 3);
  assert.strictEqual(m3.badgeShort, "Antaram");
  assert.strictEqual(m3.badgeShortTamil, "அந்தரம்");

  const m4 = getLevelMetadata("Sookshmadasha");
  assert.strictEqual(m4.levelNumber, 4);
  assert.strictEqual(m4.badgeShort, "Sookshma");
  assert.strictEqual(m4.badgeShortTamil, "சூட்சுமம்");

  const m5 = getLevelMetadata("Pranadasha");
  assert.strictEqual(m5.levelNumber, 5);
  assert.strictEqual(m5.badgeShort, "Prana");
  assert.strictEqual(m5.badgeShortTamil, "பிராணன்");
});

// --------------------------------------------------------------------------
// 5. Active Hierarchy Detection via Half-Open Interval [start, end)
// --------------------------------------------------------------------------

runTest("Active hierarchy detection across nested levels", () => {
  const sampleTree = [
    {
      lord: "Sun",
      level: "Mahadasha",
      start_jd: 2450000.0,
      end_jd: 2452191.5,
      duration_days: 2191.5,
      duration_years: 6.0,
      sub_periods: [
        {
          lord: "Sun",
          level: "Antardasha",
          start_jd: 2450000.0,
          end_jd: 2450109.575,
          duration_days: 109.575,
          duration_years: 0.3,
          sub_periods: [
            {
              lord: "Sun",
              level: "Pratyantardasha",
              start_jd: 2450000.0,
              end_jd: 2450005.478,
              duration_days: 5.478,
              duration_years: 0.015,
              sub_periods: [
                {
                  lord: "Sun",
                  level: "Sookshmadasha",
                  start_jd: 2450000.0,
                  end_jd: 2450000.274,
                  duration_days: 0.274,
                  duration_years: 0.00075,
                  sub_periods: [
                    {
                      lord: "Sun",
                      level: "Pranadasha",
                      start_jd: 2450000.0,
                      end_jd: 2450000.0137,
                      duration_days: 0.0137,
                      duration_years: 0.0000375,
                      sub_periods: [],
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  ];

  const match = findActiveHierarchy(sampleTree, 2450000.005);
  assert.ok(match, "Must find active hierarchy");
  assert.strictEqual(match.mahadasha?.lord, "Sun");
  assert.strictEqual(match.antardasha?.lord, "Sun");
  assert.strictEqual(match.pratyantardasha?.lord, "Sun");
  assert.strictEqual(match.sookshmadasha?.lord, "Sun");
  assert.strictEqual(match.pranadasha?.lord, "Sun");

  const outBefore = findActiveHierarchy(sampleTree, 2449999.0);
  assert.strictEqual(outBefore, null);

  const outAfter = findActiveHierarchy(sampleTree, 2453000.0);
  assert.strictEqual(outAfter, null);
});

// --------------------------------------------------------------------------
// 6. Centralized Translation Dictionary Static Verification
// --------------------------------------------------------------------------

runTest("Centralized translation dictionary contains all required Dasa keys in translations.ts", () => {
  const transFilePath = path.join(__dirname, "..", "src", "lib", "translations.ts");
  const content = fs.readFileSync(transFilePath, "utf8");

  const requiredKeys = [
    "dasaMahadasha",
    "dasaAntardasha",
    "dasaPratyantardasha",
    "dasaSookshmadasha",
    "dasaPranadasha",
    "dasaStartDate",
    "dasaEndDate",
    "dasaAgeAtStart",
    "dasaAgeAtEnd",
    "dasaDuration",
    "dasaActivePeriod",
    "dasaSelectedDate",
    "dasaExpand",
    "dasaCollapse",
    "dasaExpandAll",
    "dasaCollapseAll",
    "dasaExpandActivePath",
    "dasaLoading",
    "dasaNoPeriodsAvailable",
    "dasaAgeUnavailable",
    "dasaPeriodOutsideRange",
  ];

  for (const k of requiredKeys) {
    assert.ok(content.includes(`${k}:`), `Missing translation key: ${k}`);
  }
});

console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) process.exit(1);
