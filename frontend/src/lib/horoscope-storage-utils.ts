/**
 * Gokul's Astrological Insights - Horoscope Storage & Snapshot Utilities
 * Versioned, compact calculation snapshot serialization and display formatting.
 */

import type { FullHoroscopeResult } from "./types.ts";

/**
 * Prunes the deep Vimshottari Dasa tree to a manageable depth (default 3 levels:
 * Mahadasha -> Antardasha -> Pratyantardasha) and removes repeated nested dictionaries,
 * preventing huge payload overflows while preserving full temporal accuracy.
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
    if (node.star_lord) compactNode.star_lord = node.star_lord;
    if (node.benefit_bhavas) compactNode.benefit_bhavas = node.benefit_bhavas;
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
 * Retains full core Vedic horoscope, KP analysis, 5-level active period, and compacted dasa tree.
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
