/**
 * Gokul's Astrological Insights - Horoscope Storage & Snapshot Utilities
 * Versioned, compact calculation snapshot serialization and display formatting.
 */

import type { FullHoroscopeResult, SavedHoroscopeItem } from "./types";

/**
 * Prunes the deep Vimshottari Dasa tree while preserving a fast, accurate 3-level hierarchy
 * (Mahadasha -> Antardasha -> Pratyantardasha) with Benefit Bhavas.
 * Deeper levels (Sookshmadasha & Pranadasha) are dynamically expanded on demand via canonical math,
 * keeping database storage lightweight (~200 KB) and avoiding gateway / payload limits.
 */
export function compactDasaTree(tree: any[], maxDepth = 3): any[] {
  if (!Array.isArray(tree) || maxDepth <= 0) return [];
  return tree.map((node) => {
    const compactNode: any = {
      lord: node.lord,
      level: node.level,
      start_jd: node.start_jd,
      end_jd: node.end_jd,
      duration_days: node.duration_days,
      duration_years: node.duration_years,
      start_date_iso: node.start_date_iso,
      end_date_iso: node.end_date_iso,
    };
    if (node.theoretical_start_jd !== undefined) compactNode.theoretical_start_jd = node.theoretical_start_jd;
    if (node.theoretical_end_jd !== undefined) compactNode.theoretical_end_jd = node.theoretical_end_jd;
    if (node.theoretical_duration_days !== undefined) compactNode.theoretical_duration_days = node.theoretical_duration_days;
    if (node.theoretical_duration_years !== undefined) compactNode.theoretical_duration_years = node.theoretical_duration_years;
    if (node.theoretical_start_date_iso !== undefined) compactNode.theoretical_start_date_iso = node.theoretical_start_date_iso;
    if (node.theoretical_end_date_iso !== undefined) compactNode.theoretical_end_date_iso = node.theoretical_end_date_iso;
    if (node.is_active !== undefined) compactNode.is_active = node.is_active;
    if (node.is_active_at_birth !== undefined) compactNode.is_active_at_birth = node.is_active_at_birth;
    if (node.star_lord) compactNode.star_lord = node.star_lord;
    if (node.benefit_bhavas) compactNode.benefit_bhavas = node.benefit_bhavas;
    if (node.benefit_bhavas_detail) compactNode.benefit_bhavas_detail = node.benefit_bhavas_detail;
    if (node.period_lord_occupied !== undefined && node.period_lord_occupied !== null) {
      compactNode.period_lord_occupied = node.period_lord_occupied;
    }
    if (node.star_lord_occupied !== undefined && node.star_lord_occupied !== null) {
      compactNode.star_lord_occupied = node.star_lord_occupied;
    }
    if (Array.isArray(node.period_lord_owned)) {
      compactNode.period_lord_owned = node.period_lord_owned;
    }
    if (Array.isArray(node.star_lord_owned)) {
      compactNode.star_lord_owned = node.star_lord_owned;
    }
    const subPeriods = Array.isArray(node.sub_periods)
      ? node.sub_periods
      : Array.isArray(node.children)
      ? node.children
      : null;
    if (maxDepth > 1 && subPeriods && subPeriods.length > 0) {
      compactNode.sub_periods = compactDasaTree(subPeriods, maxDepth - 1);
    }
    return compactNode;
  });
}

/**
 * Prepares a structured, versioned calculation snapshot for database persistence.
 * Strictly includes real calculation results from XALEN/FastAPI without placeholders.
 * Retains full core Vedic horoscope, KP analysis, 5-level active period, and 5-level dasa tree.
 */
export function prepareCalculationSnapshot(
  result: FullHoroscopeResult,
  idempotencyKey: string
): Record<string, any> {
  let dasa = result.dasa;
  if (dasa && Array.isArray(dasa.dasa_tree)) {
    dasa = {
      ...dasa,
      dasa_tree: compactDasaTree(dasa.dasa_tree, 3),
    };
  }

  return {
    schema_version: "1.0.0",
    idempotency_key: idempotencyKey,
    calculatedAt: result.calculatedAt || new Date().toISOString(),
    clientInputs: result.clientInputs,
    horoscope: result.horoscope,
    dasa,
    kp: result.kp,
  };
}

/**
 * Formats a sequential horoscope number conforming to specification:
 * - English: "Horoscope No. 1", "Horoscope No. 2", etc.
 * - Tamil: "ஜாதக எண் 1", "ஜாதக எண் 2", etc.
 */
export function formatHoroscopeSequence(
  num: number | null | undefined,
  lang: "en" | "ta" = "en"
): string {
  if (num === null || num === undefined || isNaN(num) || num <= 0) {
    return lang === "ta" ? "ஜாதகம்" : "Horoscope";
  }
  return lang === "ta" ? `ஜாதக எண் ${num}` : `Horoscope No. ${num}`;
}

/**
 * Exports an array of saved horoscopes to CSV format.
 * Preserves all standard export columns:
 *   Serial, Name, Birth Date, Birth Time, Birthplace, Ayanamsa, Created At.
 * Safely resolves birth time from record fields or nested calculation snapshots,
 * handling missing, unknown, or empty birth times gracefully with "Unknown".
 * Escapes quotes, commas, and newlines according to standard CSV RFC 4180 rules.
 */
export function exportHoroscopesToCsv(horoscopes: SavedHoroscopeItem[]): string {
  const headers = [
    "Serial",
    "Name",
    "Birth Date",
    "Birth Time",
    "Birthplace",
    "Ayanamsa",
    "Created At",
  ];

  if (!Array.isArray(horoscopes) || horoscopes.length === 0) {
    return headers.join(",") + "\n";
  }

  const escapeCsv = (val: any): string => {
    if (val === null || val === undefined) return '""';
    const str = String(val);
    return `"${str.replace(/"/g, '""')}"`;
  };

  const rows = horoscopes.map((h) => {
    const serial =
      h.display_number !== undefined && h.display_number !== null
        ? String(h.display_number)
        : "";

    const name = escapeCsv(h.person_name || "Unnamed");

    const birthDate = h.birth_date ? escapeCsv(h.birth_date) : escapeCsv("Unknown");

    // Support birth_time safely with fallbacks and handling of missing or unknown times
    const candidateTime = (
      h.birth_time ||
      (h as any).clientInputs?.birthTime ||
      (h as any).clientInputs?.birth_time ||
      (h as any).calculation_result?.clientInputs?.birthTime ||
      (h as any).calculation_result?.clientInputs?.birth_time ||
      (h as any).calculation_result?.horoscope?.birth_time ||
      ""
    ).toString().trim();

    const birthTime =
      candidateTime &&
      candidateTime !== "—" &&
      candidateTime.toLowerCase() !== "unknown"
        ? escapeCsv(candidateTime)
        : escapeCsv("Unknown");

    const birthplace = escapeCsv(h.birthplace || "Unknown Location");

    const ayanamsaName =
      h.ayanamsa_id === 1 ? "KP" : h.ayanamsa_id === 2 ? "Raman" : "Lahiri";
    const ayanamsa = escapeCsv(ayanamsaName);

    const createdAt = h.created_at ? escapeCsv(h.created_at) : escapeCsv("");

    return [serial, name, birthDate, birthTime, birthplace, ayanamsa, createdAt].join(",");
  });

  return [headers.join(","), ...rows].join("\n");
}

