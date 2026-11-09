"""Gokul's Astrological Insights - High-Concurrency PDF Storage & Caching Service.

Provides:
1. In-memory LRU/TTL byte cache to eliminate redundant ReportLab rendering cycles.
2. Supabase Storage integration with presigned download URLs.
3. Threadpool execution and background worker offloading for heavy 9-page PDF generation.
"""

import time
import hashlib
import logging
from typing import Optional, Dict, Tuple, Any
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.services.auth_service import get_supabase_client

logger = logging.getLogger("gai.pdf_storage")

# In-memory cache: cache_key -> (timestamp, pdf_bytes, filename)
_PDF_CACHE_TTL_SECONDS = 900.0  # 15 minutes TTL
_MAX_PDF_CACHE_ENTRIES = 50     # Max 50 rendered PDFs (~25-50 MB memory cap)
_PDF_MEMORY_CACHE: Dict[str, Tuple[float, bytes, str]] = {}


def generate_pdf_cache_key(
    report_type: str,
    identifier: str,
    language: str = "en",
    extra: str = "",
) -> str:
    """Computes a deterministic cache key for a generated PDF report."""
    raw = f"{report_type}:{identifier.strip().lower()}:{language.strip().lower()}:{extra}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def get_cached_pdf(cache_key: str) -> Optional[Tuple[bytes, str]]:
    """Checks the in-memory cache for a recently generated PDF report."""
    if not settings.enable_pdf_storage_cache:
        return None
    now = time.time()
    if cache_key in _PDF_MEMORY_CACHE:
        cached_time, pdf_bytes, filename = _PDF_MEMORY_CACHE[cache_key]
        if now - cached_time < _PDF_CACHE_TTL_SECONDS:
            logger.debug(f"[PDF Cache] HIT for key: {cache_key}")
            return pdf_bytes, filename
        else:
            del _PDF_MEMORY_CACHE[cache_key]
    return None


def store_cached_pdf(cache_key: str, pdf_bytes: bytes, filename: str) -> None:
    """Stores generated PDF bytes in the in-memory cache with eviction guard."""
    if not settings.enable_pdf_storage_cache:
        return
    now = time.time()
    if len(_PDF_MEMORY_CACHE) >= _MAX_PDF_CACHE_ENTRIES:
        # Evict oldest entry
        oldest_key = min(_PDF_MEMORY_CACHE.keys(), key=lambda k: _PDF_MEMORY_CACHE[k][0])
        del _PDF_MEMORY_CACHE[oldest_key]
    _PDF_MEMORY_CACHE[cache_key] = (now, pdf_bytes, filename)
    logger.debug(f"[PDF Cache] STORED for key: {cache_key} ({len(pdf_bytes)} bytes)")


def clear_pdf_cache() -> None:
    """Clears all in-memory PDF cached items."""
    _PDF_MEMORY_CACHE.clear()


async def get_supabase_storage_signed_url(
    file_path: str,
    bucket: Optional[str] = None,
    expires_in: int = 3600,
) -> Optional[str]:
    """Generates a presigned download URL from Supabase Storage if the file exists."""
    bucket_name = bucket or settings.pdf_storage_bucket
    supabase = get_supabase_client()
    if not supabase:
        return None

    def _sync_get_signed_url() -> Optional[str]:
        try:
            storage_client = supabase.storage.from_(bucket_name)
            # Create signed url
            res = storage_client.create_signed_url(file_path, expires_in=expires_in)
            if isinstance(res, dict) and "signedURL" in res:
                return res["signedURL"]
            elif isinstance(res, str):
                return res
            return None
        except Exception as exc:
            logger.debug(f"[PDF Storage] Presigned URL generation skipped: {exc}")
            return None

    return await run_in_threadpool(_sync_get_signed_url)


async def upload_pdf_to_supabase_storage(
    file_path: str,
    pdf_bytes: bytes,
    bucket: Optional[str] = None,
) -> bool:
    """Uploads generated PDF bytes to Supabase Storage in worker threadpool."""
    bucket_name = bucket or settings.pdf_storage_bucket
    supabase = get_supabase_client()
    if not supabase:
        return False

    def _sync_upload() -> bool:
        try:
            storage_client = supabase.storage.from_(bucket_name)
            try:
                storage_client.upload(
                    file_path,
                    pdf_bytes,
                    file_options={"content-type": "application/pdf", "upsert": "true"},
                )
            except Exception:
                # Attempt update if file already exists
                storage_client.update(
                    file_path,
                    pdf_bytes,
                    file_options={"content-type": "application/pdf", "upsert": "true"},
                )
            logger.info(f"[PDF Storage] Successfully uploaded {file_path} to {bucket_name}")
            return True
        except Exception as exc:
            logger.warning(f"[PDF Storage] Upload to Supabase Storage failed ({file_path}): {exc}")
            return False

    return await run_in_threadpool(_sync_upload)
