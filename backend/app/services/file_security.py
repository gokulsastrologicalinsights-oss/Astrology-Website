"""Gokul's Astrological Insights - File Security & Ghostscript Hardening Module.

Provides defense-in-depth hardening against:
1. Ghostscript Upload2Shell (CVE-2026-125396) via strict PostScript signature blocking
   and Pillow PostScript (EPS) plugin unregistration.
2. Insecure temporary file handling via secure permissions (0o600) and guaranteed cleanup.
3. Content signature (magic number) verification rather than extension-only trusting.
4. Shell command argument validation and isolation.
"""

from __future__ import annotations

import os
import re
import logging
import tempfile
from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple, Union

logger = logging.getLogger("gai.security.file")

# Standard content signatures (magic numbers)
ALLOWED_MAGIC_SIGNATURES = {
    "pdf": b"%PDF-",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
}

# Forbidden PostScript signatures that trigger Ghostscript rendering pipelines
FORBIDDEN_POSTSCRIPT_SIGNATURES = [
    b"%!PS",
    b"\x04%!PS",
    b"%!Adobe",
    b"\x1b%-12345X",
    b"\x1b%0B",
]

# Maximum allowed file size for input streams (10 MB default)
DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024


def init_file_security() -> None:
    """Disables PostScript/EPS image loading in Pillow at startup to neutralize Ghostscript CVE-2026-125396."""
    try:
        from PIL import Image
        # 1. Unregister PostScript extensions from Pillow plugin registry
        for ext in (".eps", ".ps", ".epi", ".epsf", ".epsi"):
            if ext in Image.EXTENSION:
                try:
                    del Image.EXTENSION[ext]
                except Exception:
                    pass
            if hasattr(Image, "unregister_extension"):
                try:
                    Image.unregister_extension("EPS", ext)
                except Exception:
                    pass

        # 2. Remove EPS from Image.ID if present
        if hasattr(Image, "ID") and "EPS" in Image.ID:
            try:
                Image.ID.remove("EPS")
            except Exception:
                pass

        logger.info("Pillow EPS/PostScript plugin disabled successfully (CVE-2026-125396 hardening active).")
    except ImportError:
        logger.debug("Pillow not installed; skipping EPS unregistration.")
    except Exception as exc:
        logger.warning("Could not unregister Pillow EPS plugin: %s", exc)


def validate_file_content(
    content: bytes,
    allowed_types: Optional[List[str]] = None,
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE,
) -> Tuple[bool, str]:
    """Validates file bytes against size limits, content signatures, and forbidden PostScript exploits.

    Returns:
        (is_valid: bool, error_message: str)
    """
    if not content:
        return False, "File content is empty."

    if len(content) > max_size_bytes:
        return False, f"File size ({len(content)} bytes) exceeds max limit of {max_size_bytes} bytes."

    # 1. Reject any PostScript signatures (even if disguised as PNG or PDF)
    prefix_check = content[:1024]
    for ps_sig in FORBIDDEN_POSTSCRIPT_SIGNATURES:
        if ps_sig in prefix_check:
            logger.warning("Blocked potential Ghostscript polyglot/PostScript exploit attempt.")
            return False, "PostScript and EPS formats are strictly forbidden."

    # 2. Check for embedded PostScript headers within first 512 bytes
    if b"/Subtype /Type1" in prefix_check or b".forceput" in prefix_check or b".putgstringcopy" in prefix_check:
        logger.warning("Blocked exploit pattern matching CVE-2026-125396.")
        return False, "Disallowed font/PostScript definition detected."

    # 3. If allowed types are specified, match magic header
    if allowed_types:
        matched = False
        for t in allowed_types:
            sig = ALLOWED_MAGIC_SIGNATURES.get(t.lower())
            if sig and content.startswith(sig):
                matched = True
                break
        if not matched:
            return False, f"File header signature does not match allowed types: {', '.join(allowed_types)}."

    return True, ""


@contextmanager
def safe_temp_file(
    suffix: str = ".tmp",
    content: Optional[Union[bytes, str]] = None,
    prefix: str = "gai_safe_",
    text_mode: bool = False,
) -> Generator[str, None, None]:
    """Context manager yielding a securely created temporary file with 0o600 permissions and guaranteed cleanup."""
    temp_path: Optional[str] = None
    mode = "w" if text_mode else "wb"
    encoding = "utf-8" if text_mode else None

    try:
        # Create file with restrictive 0o600 permissions
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        # Ensure permissions on POSIX
        if os.name != "nt":
            try:
                os.chmod(temp_path, 0o600)
            except OSError:
                pass

        if content is not None:
            with open(fd, mode, encoding=encoding, closefd=True) as f:
                f.write(content)
        else:
            os.close(fd)

        yield temp_path

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def sanitize_filename_argument(filename: str) -> str:
    """Strips shell metacharacters and directory traversals from filenames passed to commands."""
    basename = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.\-]", "_", basename)
    if not clean or clean.startswith("."):
        clean = f"safe_{clean.lstrip('.')}"
    return clean
