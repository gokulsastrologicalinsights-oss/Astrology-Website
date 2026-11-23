"""Robust Chromium-based PDF renderer for pixel-perfect Indic / Tamil typography.

Uses Playwright with automatic system browser discovery (Chromium, Chrome, Edge)
and container safety flags (--no-sandbox, --disable-dev-shm-usage).
Includes a direct CLI fallback using headless Chromium/Edge if Playwright
is unavailable or encounters driver initialization errors.
"""

import os
import sys
import shutil
import logging
import tempfile
import subprocess
import concurrent.futures
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("gai.pdf.browser_renderer")

BROWSER_CANDIDATE_PATHS = [
    # Linux / Docker / Cloud (Debian / Ubuntu / Render / AWS)
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/snap/bin/chromium",
    "/usr/local/bin/chromium",
    # Windows standard paths
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # macOS standard paths
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

CHROMIUM_LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--font-render-hinting=none",
]


def find_system_browser() -> Optional[str]:
    """Discovers an installed Chromium, Chrome, or Edge executable across Linux, Windows, and macOS."""
    # 1. Respect explicit environment variable if set and existing
    env_path = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2. Check candidate filesystem paths
    for p in BROWSER_CANDIDATE_PATHS:
        expanded = os.path.expandvars(p)
        if os.path.isfile(expanded):
            return expanded

    # 3. Check Windows AppData / ProgramFiles via environment variables
    if sys.platform == "win32":
        win_candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        ]
        for wp in win_candidates:
            if os.path.isfile(wp):
                return wp

    # 4. Search system PATH for common binary names
    for cmd in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge", "chrome"):
        found = shutil.which(cmd)
        if found and os.path.isfile(found):
            return found

    return None


def render_html_to_pdf_with_playwright(
    html_content: str,
    pdf_format: str = "A4",
    print_background: bool = True,
    margin: Optional[Dict[str, str]] = None,
    prefer_css_page_size: bool = True,
    display_header_footer: bool = False,
    header_template: Optional[str] = None,
    footer_template: Optional[str] = None,
    timeout: float = 45.0,
) -> bytes:
    """Renders HTML to PDF bytes using Playwright inside a dedicated threadpool."""
    from playwright.sync_api import sync_playwright

    margin_dict = margin or {"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
    browser_bin = find_system_browser()

    def _worker() -> bytes:
        with sync_playwright() as p:
            browser = None
            errors: List[str] = []

            # 1. Try launching with explicitly discovered system executable
            if browser_bin:
                try:
                    logger.debug("Launching Playwright with discovered executable: %s", browser_bin)
                    browser = p.chromium.launch(
                        executable_path=browser_bin,
                        args=CHROMIUM_LAUNCH_ARGS,
                        headless=True,
                    )
                except Exception as exc:
                    errors.append(f"executable_path({browser_bin}): {exc}")

            # 2. Try launching with standard channels if binary launch failed
            if browser is None:
                for channel in ("chromium", "chrome", "msedge"):
                    try:
                        logger.debug("Trying Playwright launch with channel: %s", channel)
                        browser = p.chromium.launch(
                            channel=channel,
                            args=CHROMIUM_LAUNCH_ARGS,
                            headless=True,
                        )
                        break
                    except Exception as exc:
                        errors.append(f"channel({channel}): {exc}")

            # 3. Try default Playwright bundled chromium
            if browser is None:
                try:
                    logger.debug("Trying Playwright launch with default chromium")
                    browser = p.chromium.launch(
                        args=CHROMIUM_LAUNCH_ARGS,
                        headless=True,
                    )
                except Exception as exc:
                    errors.append(f"default_chromium: {exc}")

            if browser is None:
                raise RuntimeError(f"All Playwright launch attempts failed: {'; '.join(errors)}")

            try:
                page = browser.new_page()
                page.set_content(html_content, wait_until="networkidle")
                page.evaluate("document.fonts.ready")

                pdf_kwargs: Dict[str, Any] = {
                    "format": pdf_format,
                    "print_background": print_background,
                    "margin": margin_dict,
                    "prefer_css_page_size": prefer_css_page_size,
                }
                if display_header_footer:
                    pdf_kwargs["display_header_footer"] = True
                    if header_template:
                        pdf_kwargs["header_template"] = header_template
                    if footer_template:
                        pdf_kwargs["footer_template"] = footer_template

                return page.pdf(**pdf_kwargs)
            finally:
                browser.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_worker)
        return future.result(timeout=timeout)


def render_html_to_pdf_with_cli(
    html_content: str,
    timeout: float = 30.0,
) -> bytes:
    """Renders HTML directly to PDF using headless Chromium / Edge CLI.

    Acts as a fail-safe secondary fallback if the Playwright Python library is
    unavailable, improperly installed, or experiences driver-level failures.
    """
    browser_bin = find_system_browser()
    if not browser_bin:
        raise FileNotFoundError("No Chromium/Chrome/Edge browser executable found on system for CLI rendering.")

    temp_html = None
    pdf_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html_content)
            temp_html = f.name

        pdf_path = temp_html.replace(".html", ".pdf")
        file_url = "file:///" + temp_html.replace("\\", "/")

        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            file_url,
        ]

        logger.info("Executing headless browser CLI for PDF generation: %s", browser_bin)
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if result.returncode != 0 or not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) == 0:
            stderr_msg = result.stderr.decode("utf-8", errors="replace") if result.stderr else "Unknown error"
            raise RuntimeError(f"Browser CLI PDF generation failed (exit {result.returncode}): {stderr_msg}")

        with open(pdf_path, "rb") as pf:
            return pf.read()

    finally:
        if temp_html and os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except OSError:
                pass
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except OSError:
                pass


def render_html_to_pdf(
    html_content: str,
    pdf_format: str = "A4",
    print_background: bool = True,
    margin: Optional[Dict[str, str]] = None,
    prefer_css_page_size: bool = True,
    display_header_footer: bool = False,
    header_template: Optional[str] = None,
    footer_template: Optional[str] = None,
    timeout: float = 45.0,
) -> bytes:
    """Master Chromium HTML-to-PDF renderer.

    1. Tries Playwright first with container-safe launch options and system executable detection.
    2. Falls back to direct headless Chromium CLI if Playwright encounters any issue.
    3. Raises RuntimeError only if both browser mechanisms fail.
    """
    try:
        return render_html_to_pdf_with_playwright(
            html_content=html_content,
            pdf_format=pdf_format,
            print_background=print_background,
            margin=margin,
            prefer_css_page_size=prefer_css_page_size,
            display_header_footer=display_header_footer,
            header_template=header_template,
            footer_template=footer_template,
            timeout=timeout,
        )
    except Exception as pw_err:
        logger.warning(
            "Playwright PDF rendering failed (%s). Attempting direct headless Chromium CLI fallback...",
            pw_err,
        )
        return render_html_to_pdf_with_cli(html_content=html_content, timeout=timeout)
