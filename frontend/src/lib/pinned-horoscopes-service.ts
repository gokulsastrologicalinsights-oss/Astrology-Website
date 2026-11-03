import fs from "fs";
import path from "path";
import { createAdminClient } from "@/lib/supabase/admin";

export interface PinnedHoroscopeRecord {
  user_id: string;
  horoscope_id: string;
  pinned_at: string; // ISO 8601 string
}

function getCandidatePaths(): string[] {
  const cwd = process.cwd();
  return [
    path.join(cwd, "data", "pinned_horoscopes.json"),
    path.resolve(cwd, "..", "data", "pinned_horoscopes.json"),
  ];
}

/**
 * Loads pinned records from local JSON files (cross-environment fallback).
 */
export function loadLocalPinnedRecords(): PinnedHoroscopeRecord[] {
  const candidatePaths = getCandidatePaths();
  for (const filePath of candidatePaths) {
    try {
      if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath, "utf-8");
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          return parsed;
        }
      }
    } catch (err) {
      // Continue to next candidate
    }
  }
  return [];
}

/**
 * Persists pinned records to local JSON files in all candidate directories.
 */
export function saveLocalPinnedRecords(records: PinnedHoroscopeRecord[]): void {
  const candidatePaths = getCandidatePaths();
  const serialized = JSON.stringify(records, null, 2);

  for (const filePath of candidatePaths) {
    try {
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, serialized, "utf-8");
    } catch {
      // Ignore write errors to non-existent roots
    }
  }
}

/**
 * Retrieves all pinned horoscope records for a specific user, ordered newest pinned first.
 */
export async function getPinnedHoroscopesForUser(
  userId: string
): Promise<PinnedHoroscopeRecord[]> {
  const localList = loadLocalPinnedRecords();
  let userPinned = localList.filter((r) => r.user_id === userId);

  // Attempt database sync if public.pinned_horoscopes table exists
  try {
    const adminClient = createAdminClient();
    const { data: dbRecords, error } = await (adminClient.from("pinned_horoscopes") as any)
      .select("horoscope_id, user_id, pinned_at")
      .eq("user_id", userId);

    if (!error && Array.isArray(dbRecords)) {
      const dbMap = new Map<string, PinnedHoroscopeRecord>();
      for (const r of dbRecords) {
        dbMap.set(r.horoscope_id, {
          user_id: r.user_id,
          horoscope_id: r.horoscope_id,
          pinned_at: r.pinned_at,
        });
      }
      // Merge local and DB
      for (const loc of userPinned) {
        if (!dbMap.has(loc.horoscope_id)) {
          dbMap.set(loc.horoscope_id, loc);
        }
      }
      userPinned = Array.from(dbMap.values());
    }
  } catch {
    // Database table not present; local store is authoritative
  }

  // Sort descending by pinned_at (newest pinned first)
  return userPinned.sort(
    (a, b) => new Date(b.pinned_at).getTime() - new Date(a.pinned_at).getTime()
  );
}

/**
 * Checks if a specific horoscope is pinned by the user.
 */
export async function isHoroscopePinned(
  userId: string,
  horoscopeId: string
): Promise<boolean> {
  const pinned = await getPinnedHoroscopesForUser(userId);
  return pinned.some((p) => p.horoscope_id === horoscopeId);
}

/**
 * Sets the pinned status of a horoscope for a user.
 * Synchronizes across local JSON storage, calculation_result JSONB on the horoscope record,
 * and the public.pinned_horoscopes table (if available).
 */
export async function setPinnedStatus(
  userId: string,
  horoscopeId: string,
  isPinned: boolean
): Promise<{ success: boolean; is_pinned: boolean }> {
  const nowIso = new Date().toISOString();

  // 1. Update local storage
  const localRecords = loadLocalPinnedRecords();
  const existingIndex = localRecords.findIndex(
    (r) => r.user_id === userId && r.horoscope_id === horoscopeId
  );

  if (isPinned) {
    if (existingIndex >= 0) {
      localRecords[existingIndex].pinned_at = nowIso;
    } else {
      localRecords.unshift({
        user_id: userId,
        horoscope_id: horoscopeId,
        pinned_at: nowIso,
      });
    }
  } else {
    if (existingIndex >= 0) {
      localRecords.splice(existingIndex, 1);
    }
  }
  saveLocalPinnedRecords(localRecords);

  // 2. Fire-and-forget background synchronization to calculation_result and DB table
  (async () => {
    try {
      const adminClient = createAdminClient();
      const { data: horoscopeRecord } = await adminClient
        .from("saved_horoscopes")
        .select("calculation_result")
        .eq("id", horoscopeId)
        .single();

      if (horoscopeRecord) {
        const calc = horoscopeRecord.calculation_result || {};
        calc.is_pinned = isPinned;
        calc.pinned_at = isPinned ? nowIso : null;

        await adminClient
          .from("saved_horoscopes")
          .update({
            calculation_result: calc,
            updated_at: nowIso,
          })
          .eq("id", horoscopeId);
      }
    } catch (syncErr) {
      console.warn("Could not sync pinned status to calculation_result:", syncErr);
    }

    try {
      const adminClient = createAdminClient();
      if (isPinned) {
        await (adminClient.from("pinned_horoscopes") as any).upsert(
          {
            user_id: userId,
            horoscope_id: horoscopeId,
            pinned_at: nowIso,
          },
          { onConflict: "user_id,horoscope_id" }
        );
      } else {
        await (adminClient.from("pinned_horoscopes") as any)
          .delete()
          .eq("user_id", userId)
          .eq("horoscope_id", horoscopeId);
      }
    } catch {
      // Ignore if table does not exist
    }
  })();

  return { success: true, is_pinned: isPinned };
}

/**
 * Removes all pin entries for a horoscope (invoked upon horoscope deletion).
 */
export async function removeHoroscopePin(horoscopeId: string): Promise<void> {
  const localRecords = loadLocalPinnedRecords();
  const filtered = localRecords.filter((r) => r.horoscope_id !== horoscopeId);
  if (filtered.length !== localRecords.length) {
    saveLocalPinnedRecords(filtered);
  }

  try {
    const adminClient = createAdminClient();
    await (adminClient.from("pinned_horoscopes") as any)
      .delete()
      .eq("horoscope_id", horoscopeId);
  } catch {
    // Ignore
  }
}
