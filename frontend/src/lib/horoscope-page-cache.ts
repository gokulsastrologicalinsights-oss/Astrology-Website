/**
 * In-memory response cache for /api/horoscopes list queries.
 * Prevents redundant PostgREST roundtrips and high egress on repeated navigation.
 * Automatically invalidated upon creation, update, deletion, or pinning of horoscopes.
 */

interface CacheEntry {
  timestamp: number;
  data: any;
}

const PAGE_CACHE = new Map<string, CacheEntry>();
const CACHE_TTL_MS = 60_000; // 60 seconds

export function getCachedHoroscopesPage(cacheKey: string): any | null {
  const entry = PAGE_CACHE.get(cacheKey);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    PAGE_CACHE.delete(cacheKey);
    return null;
  }
  return entry.data;
}

export function setCachedHoroscopesPage(cacheKey: string, data: any): void {
  // Simple LRU-style eviction if cache grows beyond 200 items
  if (PAGE_CACHE.size >= 200) {
    const oldestKey = PAGE_CACHE.keys().next().value;
    if (oldestKey) PAGE_CACHE.delete(oldestKey);
  }
  PAGE_CACHE.set(cacheKey, { timestamp: Date.now(), data });
}

export function invalidateHoroscopesPageCache(): void {
  PAGE_CACHE.clear();
}
