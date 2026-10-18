/**
 * Gokul's Astrological Insights - Geocoding Service
 *
 * Provider: OpenStreetMap Nominatim API (https://nominatim.openstreetmap.org)
 * Documentation: https://nominatim.org/release-docs/latest/api/Search/
 * Usage Policy: Public API requires a custom User-Agent and a reasonable query rate.
 *
 * Fallback: Curated offline dataset of 100+ global & South Indian metropolitan cities
 * with verified coordinates and IANA timezones (src/lib/cities.ts).
 *
 * This implementation NEVER fabricates coordinates or silently assumes Chennai.
 * If external geocoding is unreachable, the offline directory matches local cities,
 * and users can manually inspect/edit exact decimal coordinates.
 */

import { MAJOR_CITIES } from "./cities";

export interface LocationSearchResult {
  displayName: string;
  shortName: string;
  latitude: number;
  longitude: number;
  countryCode?: string;
  estimatedTimezone?: string;
  provider: "local-directory" | "osm-nominatim";
}

/**
 * Estimate IANA timezone from latitude/longitude and country code
 */
export function estimateTimezoneFromCoords(lat: number, lon: number, countryCode?: string): string {
  const code = (countryCode || "").toLowerCase();

  if (code === "in" || (lat >= 6.0 && lat <= 37.0 && lon >= 68.0 && lon <= 97.5)) {
    return "Asia/Kolkata";
  }
  if (code === "lk") return "Asia/Colombo";
  if (code === "sg") return "Asia/Singapore";
  if (code === "my") return "Asia/Kuala_Lumpur";
  if (code === "ae") return "Asia/Dubai";
  if (code === "gb" || code === "uk") return "Europe/London";
  if (code === "de") return "Europe/Berlin";
  if (code === "fr") return "Europe/Paris";

  // US rough bounding
  if (code === "us" || (lat >= 24 && lat <= 50 && lon >= -125 && lon <= -65)) {
    if (lon < -114) return "America/Los_Angeles";
    if (lon < -102) return "America/Denver";
    if (lon < -85) return "America/Chicago";
    return "America/New_York";
  }

  // Fallback to client browser timezone or UTC
  try {
    const local = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (local) return local;
  } catch {
    // Ignore
  }
  return "UTC";
}

/**
 * Search locations via offline directory first, then OpenStreetMap Nominatim if network allows.
 */
export async function searchLocations(query: string): Promise<LocationSearchResult[]> {
  const cleanQuery = query.trim().toLowerCase();
  if (!cleanQuery || cleanQuery.length < 2) return [];

  const results: LocationSearchResult[] = [];

  // 1. Search curated directory for instant matches
  const localMatches = MAJOR_CITIES.filter(
    (c) =>
      c.name.toLowerCase().includes(cleanQuery) ||
      c.stateOrCountry.toLowerCase().includes(cleanQuery)
  ).slice(0, 5);

  for (const m of localMatches) {
    results.push({
      displayName: `${m.name}, ${m.stateOrCountry}`,
      shortName: m.name,
      latitude: m.latitude,
      longitude: m.longitude,
      estimatedTimezone: m.timezone,
      provider: "local-directory",
    });
  }

  // 2. If user query has 3+ characters, query OpenStreetMap Nominatim API
  if (cleanQuery.length >= 3) {
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=5&q=${encodeURIComponent(
        cleanQuery
      )}`;

      const response = await fetch(url, {
        headers: {
          "Accept": "application/json",
          "User-Agent": "GokulsAstrologicalInsights/1.0 (contact: support@gokulastrology.com)",
        },
      });

      if (response.ok) {
        const osmData = await response.json();
        for (const item of osmData) {
          const lat = parseFloat(item.lat);
          const lon = parseFloat(item.lon);
          const countryCode = item.address?.country_code;

          // Avoid near-duplicate with local results
          const isDuplicate = results.some(
            (r) => Math.abs(r.latitude - lat) < 0.05 && Math.abs(r.longitude - lon) < 0.05
          );

          if (!isDuplicate) {
            results.push({
              displayName: item.display_name,
              shortName: item.name || item.display_name.split(",")[0],
              latitude: Number(lat.toFixed(4)),
              longitude: Number(lon.toFixed(4)),
              countryCode,
              estimatedTimezone: estimateTimezoneFromCoords(lat, lon, countryCode),
              provider: "osm-nominatim",
            });
          }
        }
      }
    } catch {
      // Graceful offline fallback: local directory matches already populated above
    }
  }

  return results.slice(0, 8);
}
