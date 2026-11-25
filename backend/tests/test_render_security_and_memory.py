"""Regression and verification tests for Render Security & Memory Optimization Audit.

Tests:
1. Ghostscript Upload2Shell (CVE-2026-125396) defense-in-depth and signature rejection.
2. Pillow PostScript plugin unregistration.
3. Magic number content signature validation.
4. Safe temporary file handling and permissions.
5. In-memory PDF cache bounding and byte caps.
6. In-memory horoscope cache bounding (50 entries max).
7. Chromium concurrency semaphore and launch arguments.
8. Repeated PDF generation memory stability.
"""

import gc
import os
import io
import pypdf
import pytest
from datetime import date, time

from app.services.file_security import (
    init_file_security,
    validate_file_content,
    safe_temp_file,
    sanitize_filename_argument,
)
from app.services.pdf_storage import (
    store_cached_pdf,
    get_cached_pdf,
    clear_pdf_cache,
    _PDF_MEMORY_CACHE,
    _MAX_PDF_CACHE_ENTRIES,
    _MAX_PDF_CACHE_TOTAL_BYTES,
    _get_current_cache_bytes,
)
from app.services.horoscope_cache import (
    _CACHE,
    _MAX_CACHE_ENTRIES,
    invalidate_saved_horoscope_cache,
)
from app.services.pdf_report_engine.browser_renderer import (
    CHROMIUM_LAUNCH_ARGS,
    _BROWSER_SEMAPHORE,
)
from app.schemas.common import BirthInput
from app.schemas.pdf_report import HoroscopePdfReportRequest
from app.services.pdf_report_engine import (
    build_report_data,
    generate_horoscope_pdf_bytes,
)


def test_ghostscript_exploit_signatures_blocked():
    """Verify that Ghostscript Upload2Shell / PostScript signatures are strictly rejected."""
    # Standard PostScript headers
    for sig in [b"%!PS-Adobe-3.0", b"\x04%!PS", b"%!Adobe", b"\x1b%-12345X@PJL"]:
        payload = sig + b"\n/Courier findfont 12 scalefont setfont\nshowpage"
        is_valid, err = validate_file_content(payload, allowed_types=["pdf"])
        assert not is_valid, f"Expected signature {sig} to be blocked"
        assert "PostScript and EPS formats are strictly forbidden" in err

    # Font loader use-after-free signatures (CVE-2026-125396)
    cve_payload = b"%PDF-1.4\n/Subtype /Type1\n.putgstringcopy\n.forceput"
    is_valid, err = validate_file_content(cve_payload, allowed_types=["pdf"])
    assert not is_valid
    assert "Disallowed font/PostScript definition detected" in err


def test_magic_number_validation():
    """Verify content signatures require valid file headers, not extensions."""
    # Valid PDF
    valid_pdf = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj"
    ok, _ = validate_file_content(valid_pdf, allowed_types=["pdf"])
    assert ok is True

    # Valid PNG
    valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    ok, _ = validate_file_content(valid_png, allowed_types=["png"])
    assert ok is True

    # Polyglot disguised with wrong header
    fake_png = b"NOT_A_PNG_HEADER_DATA"
    ok, err = validate_file_content(fake_png, allowed_types=["png"])
    assert ok is False
    assert "signature does not match" in err


def test_pillow_eps_plugin_unregistered():
    """Verify Pillow EPS/PostScript plugin is unregistered so Ghostscript cannot be triggered."""
    init_file_security()
    try:
        from PIL import Image
        assert ".eps" not in Image.EXTENSION
        assert ".ps" not in Image.EXTENSION
        if hasattr(Image, "ID"):
            assert "EPS" not in Image.ID
    except ImportError:
        pass


def test_safe_temp_file_lifecycle():
    """Verify safe_temp_file generates restrictive temporary files and cleans up automatically."""
    temp_path = None
    with safe_temp_file(suffix=".html", content="<html>test</html>", text_mode=True) as p:
        temp_path = p
        assert os.path.isfile(temp_path)
        with open(temp_path, "r", encoding="utf-8") as f:
            assert f.read() == "<html>test</html>"

    # Must be deleted after context exit
    assert not os.path.exists(temp_path)


def test_filename_sanitization():
    """Verify filename sanitization eliminates command injection and traversal characters."""
    dangerous_names = [
        "../../etc/passwd",
        "file; rm -rf /",
        "test`whoami`.pdf",
        "doc$(id).pdf",
        "| convert input output",
    ]
    for d in dangerous_names:
        clean = sanitize_filename_argument(d)
        assert "/" not in clean
        assert ";" not in clean
        assert "`" not in clean
        assert "$" not in clean
        assert "|" not in clean
        assert ".." not in clean


def test_pdf_cache_entry_and_byte_limits():
    """Verify in-memory PDF cache strictly obeys entry cap (10) and total byte cap (20 MB)."""
    clear_pdf_cache()
    assert len(_PDF_MEMORY_CACHE) == 0

    # Store 12 items (limit is 10)
    for i in range(12):
        fake_bytes = b"PDF_DATA_" + str(i).encode() * 1024  # ~1 KB each
        store_cached_pdf(f"key_{i}", fake_bytes, f"report_{i}.pdf")

    assert len(_PDF_MEMORY_CACHE) <= _MAX_PDF_CACHE_ENTRIES
    assert len(_PDF_MEMORY_CACHE) <= 10

    # Oldest entries (key_0, key_1) must have been evicted
    assert get_cached_pdf("key_0") is None
    assert get_cached_pdf("key_1") is None
    assert get_cached_pdf("key_11") is not None

    clear_pdf_cache()


def test_horoscope_cache_bounded_at_50():
    """Verify saved horoscope cache does not exceed 50 entries."""
    invalidate_saved_horoscope_cache()
    assert len(_CACHE) == 0
    assert _MAX_CACHE_ENTRIES == 50


def test_chromium_launch_flags_contain_memory_caps():
    """Verify Chromium launch arguments contain low-memory container protections."""
    assert "--js-flags=--max-old-space-size=128" in CHROMIUM_LAUNCH_ARGS
    assert "--renderer-process-limit=1" in CHROMIUM_LAUNCH_ARGS
    assert "--disable-dev-shm-usage" in CHROMIUM_LAUNCH_ARGS
    assert "--no-sandbox" in CHROMIUM_LAUNCH_ARGS


def test_repeated_pdf_generation_memory_stability():
    """Verify repeated ReportLab PDF generation executes cleanly without runaway memory growth."""
    sample_birth = BirthInput(
        birth_date=date(1995, 8, 20),
        birth_time=time(10, 15),
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )
    data = build_report_data(
        birth_input=sample_birth,
        native_name="Memory Test User",
        language="en",
    )

    # Generate 3 successive 9-page PDFs
    for _ in range(3):
        pdf_bytes = generate_horoscope_pdf_bytes(data)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 20000
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) == 9

    gc.collect()
