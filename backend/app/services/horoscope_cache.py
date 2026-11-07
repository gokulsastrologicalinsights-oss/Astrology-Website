"""Gokul's Astrological Insights - High-Performance In-Memory Saved Horoscope Cache.

Dramatically slashes Supabase database egress and redundant PostgREST roundtrips
by caching saved horoscope records across rapid successive sub-module requests
(e.g., D1-D9 varga, doshas, shadbala, dasa, remedies, nakshatras, and rules).
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Cache configuration
_HOROSCOPE_CACHE_TTL_SECONDS = 300.0  # 60s TTL to cover multi-tab loads and sub-engine evaluations
_MAX_CACHE_ENTRIES = 300

# Cache storage: (clean_id, user_id, is_admin, include_calculation_result) -> (timestamp, record_dict)
_CACHE: Dict[Tuple[str, str, bool, bool], Tuple[float, Dict[str, Any]]] = {}

# Minimal columns required for calculations that do not need calculation_result (e.g. PDF engines)
METADATA_COLUMNS = (
    "id, user_id, display_number, person_name, birth_date, birth_time, timezone, "
    "birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
)

# Columns needed when calculation_result is required
FULL_COLUMNS = (
    "id, user_id, display_number, person_name, birth_date, birth_time, timezone, "
    "birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result, created_at, updated_at"
)


def get_cached_saved_horoscope(
    clean_id: str,
    user_id: str,
    is_admin: bool = False,
    include_calculation_result: bool = True,
) -> Optional[Dict[str, Any]]:
    """Retrieves a saved horoscope record with in-memory caching and selective column projection.

    Prevents repetitive 300-500 KB Supabase egress payloads when the same chart is evaluated
    across multiple sub-endpoints simultaneously.
    """
    now = time.time()
    cache_key = (clean_id, str(user_id), bool(is_admin), bool(include_calculation_result))

    # 1. Check in-memory cache
    if cache_key in _CACHE:
        cached_time, cached_record = _CACHE[cache_key]
        if now - cached_time < _HOROSCOPE_CACHE_TTL_SECONDS:
            return cached_record
        else:
            del _CACHE[cache_key]

    # 2. Also check if full record is already cached (can satisfy a metadata-only request)
    if not include_calculation_result:
        full_key = (clean_id, str(user_id), bool(is_admin), True)
        if full_key in _CACHE:
            cached_time, cached_record = _CACHE[full_key]
            if now - cached_time < _HOROSCOPE_CACHE_TTL_SECONDS:
                return cached_record

    # 3. Query Supabase with precise column selection
    from app.services.auth_service import get_supabase_client
    supabase = get_supabase_client()
    if not supabase:
        return None

    columns_to_select = FULL_COLUMNS if include_calculation_result else METADATA_COLUMNS

    try:
        resp = (
            supabase.table("saved_horoscopes")
            .select(columns_to_select)
            .eq("id", clean_id)
            .execute()
        )
        if not resp.data or len(resp.data) == 0:
            return None

        row = resp.data[0]
        # Enforce RLS / ownership safety
        if not is_admin and str(row.get("user_id")) != str(user_id):
            return None

        # 4. Store in cache
        if len(_CACHE) >= _MAX_CACHE_ENTRIES:
            # Simple eviction of oldest item
            oldest_key = min(_CACHE.keys(), key=lambda k: _CACHE[k][0])
            del _CACHE[oldest_key]

        _CACHE[cache_key] = (now, row)
        return row

    except Exception as err:
        logger.warning(f"Error fetching saved horoscope {clean_id} from Supabase: {err}")
        return None


def invalidate_saved_horoscope_cache(clean_id: Optional[str] = None):
    """Invalidates the in-memory cache for a specific horoscope or all entries."""
    global _CACHE
    if not clean_id:
        _CACHE.clear()
        return

    keys_to_delete = [k for k in _CACHE.keys() if k[0] == clean_id]
    for k in keys_to_delete:
        _CACHE.pop(k, None)
