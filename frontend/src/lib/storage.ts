/**
 * Gokul's Astrological Insights - Safe Client-side Result Storage
 * Stores calculation payload in sessionStorage to avoid leaking sensitive birth details in URLs.
 */

import { FullHoroscopeResult } from "./types";

const ACTIVE_CALCULATION_KEY = "gokul_active_calculation";

let inMemoryCache: FullHoroscopeResult | null = null;

export function saveActiveCalculation(result: FullHoroscopeResult): void {
  inMemoryCache = result;
  if (typeof window !== "undefined") {
    try {
      sessionStorage.setItem(ACTIVE_CALCULATION_KEY, JSON.stringify(result));
    } catch {
      // Ignore quota or private mode errors
    }
  }
}

export function getActiveCalculation(): FullHoroscopeResult | null {
  if (inMemoryCache) {
    return inMemoryCache;
  }
  if (typeof window !== "undefined") {
    try {
      const stored = sessionStorage.getItem(ACTIVE_CALCULATION_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as FullHoroscopeResult;
        inMemoryCache = parsed;
        return parsed;
      }
    } catch {
      return null;
    }
  }
  return null;
}

export function clearActiveCalculation(): void {
  inMemoryCache = null;
  if (typeof window !== "undefined") {
    try {
      sessionStorage.removeItem(ACTIVE_CALCULATION_KEY);
    } catch {
      // Ignore
    }
  }
}
