export type ValidGender = "male" | "female";

/**
 * Normalize an incoming gender value to "male" | "female" | null.
 * Returns null for missing, empty, or unrecognized values instead of
 * silently defaulting to "male".
 */
export function normalizeGender(value: unknown): ValidGender | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim().toLowerCase();
  if (trimmed === "male" || trimmed === "female") {
    return trimmed;
  }
  return null;
}

/**
 * Resolve gender from a saved horoscope record without assuming "male"
 * for genuinely unknown historical records.
 */
export function resolveSavedHoroscopeGender(record: any): ValidGender | null {
  if (!record || typeof record !== "object") return null;
  return (
    normalizeGender(record.calculation_result?.clientInputs?.gender) ??
    normalizeGender(record.gender) ??
    normalizeGender(record.calculation_result?.customer?.gender) ??
    normalizeGender(record.calculation_result?.horoscope?.request?.gender) ??
    null
  );
}
