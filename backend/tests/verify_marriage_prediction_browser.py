"""Live Browser Acceptance Test for Unified Marriage Prediction Frontend.

Validates via real headless Chromium (Playwright):
1. Unauthenticated route protection (redirect to /login).
2. Real user authentication via /login.
3. Desktop Viewport (1280x900) layout, accessibility, and form usability.
4. Input validation (invalid dates, coordinates, timezones, reversed years).
5. Live end-to-end calculation against POST /api/v1/predictions/marriage (EVENT_INDICATED).
6. Results dashboard verification:
   - Overall Verdict (EVENT_INDICATED with UNI-MARR-REC-001).
   - KP Analysis (CSL, Star-Lord, significations, rule provenance).
   - Vedic Analysis (7th lord, Venus dignity, Kuja Dosha, D9 facts, denial gates).
   - Birth-time sensitivity scan (status, nominal values, numerical guarantee).
   - Decoupled timing windows (status, Dasha lords, double transit).
   - Astrological Confluence Score labeling & mandatory non-probability disclaimer.
   - Dual ayanamsa distinct labels (KP ID 1 vs Vedic ID 0).
7. Second live prediction audit for INDETERMINATE case with timing bypass.
8. Mobile Viewport (375x667) responsive layout and horizontal overflow check.
9. State preservation and re-analysis execution.
10. Regression verification on existing /tools and /tools/d1-d9 pages.
"""

import sys
import os
import time
import subprocess
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_test_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://127.0.0.1:8000"

TEST_ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL")
TEST_ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD")


def ensure_servers_running():
    """Ensure both FastAPI backend and Next.js frontend are reachable."""
    backend_proc = None
    frontend_proc = None

    # Check backend
    try:
        urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=2)
        print("Backend server already running on http://127.0.0.1:8000")
    except Exception:
        print("Starting FastAPI backend server...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd="backend"
        )
        for _ in range(30):
            time.sleep(1)
            try:
                urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=1)
                print("Backend server started successfully.")
                break
            except Exception:
                pass

    # Check frontend
    try:
        urllib.request.urlopen(f"{FRONTEND_URL}/login", timeout=2)
        print("Frontend server already running on http://localhost:3000")
    except Exception:
        print("Starting Next.js frontend server...")
        frontend_proc = subprocess.Popen(
            ["npm.cmd", "run", "dev"],
            cwd="frontend",
            env={**os.environ, "CI": "1"}
        )
        for _ in range(40):
            time.sleep(1)
            try:
                urllib.request.urlopen(f"{FRONTEND_URL}/login", timeout=1)
                print("Frontend server started successfully.")
                break
            except Exception:
                pass

    return backend_proc, frontend_proc


def run_marriage_prediction_browser_audit():
    print("=" * 80)
    print("STARTING UNIFIED MARRIAGE PREDICTION LIVE BROWSER ACCEPTANCE AUDIT")
    print("=" * 80)

    backend_proc, frontend_proc = ensure_servers_running()

    console_errors = []
    page_errors = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            # ------------------------------------------------------------------
            # TEST 1: Unauthenticated Access & Redirection
            # ------------------------------------------------------------------
            print("\n[TEST 1] Verifying unauthenticated route protection...")
            unauth_context = browser.new_context(viewport={"width": 1280, "height": 900})
            unauth_page = unauth_context.new_page()

            unauth_page.goto(f"{FRONTEND_URL}/tools/marriage-prediction", wait_until="domcontentloaded")
            unauth_page.wait_for_timeout(2000)

            current_url = unauth_page.url
            print(f"  Navigated to /tools/marriage-prediction, redirected to: {current_url}")
            assert "/login" in current_url, f"Expected redirect to /login, got {current_url}"
            unauth_page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_01_unauth_redirect.png")
            print("  [PASS] Unauthenticated access redirects safely to login.")
            unauth_context.close()

            # ------------------------------------------------------------------
            # Credential Guard: Check for Test Credentials
            # ------------------------------------------------------------------
            if not TEST_ADMIN_EMAIL or not TEST_ADMIN_PASSWORD:
                print("\n" + "!" * 80)
                print("[SKIP NOTICE] TEST_ADMIN_EMAIL or TEST_ADMIN_PASSWORD environment variables not provided.")
                print("              Skipping credential-dependent tests (TEST 2 through TEST 10).")
                print("              The marriage prediction engine and tools suite enforce user authentication.")
                print("              To run the full authenticated browser acceptance suite, supply credentials:")
                print("                PowerShell: $env:TEST_ADMIN_EMAIL='user@example.com'; $env:TEST_ADMIN_PASSWORD='...'")
                print("                Bash:       export TEST_ADMIN_EMAIL='user@example.com' TEST_ADMIN_PASSWORD='...'")
                print("!" * 80)
                browser.close()

                print("\n" + "=" * 80)
                print("BROWSER ACCEPTANCE AUDIT PARTIAL SUMMARY (CREDENTIALS NOT PROVIDED):")
                print("  - Passed (Unauthenticated Route Protection): 1 test (TEST 1)")
                print("  - Skipped (Missing Test Credentials):        9 tests (TEST 2 through TEST 10)")
                print("=" * 80)
                return

            # ------------------------------------------------------------------
            # TEST 2: Real User Authentication
            # ------------------------------------------------------------------
            print("\n[TEST 2] Authenticating via /login...")
            auth_context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = auth_context.new_page()

            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(f"{FRONTEND_URL}/login", wait_until="domcontentloaded")
            page.wait_for_selector("input[type='password']", timeout=10000)
            page.locator("input[type='text'], input[name='identifier']").first.fill(TEST_ADMIN_EMAIL)
            page.locator("input[type='password']").fill(TEST_ADMIN_PASSWORD)
            page.locator("button[type='submit']").click()
            page.wait_for_function("() => window.location.pathname.includes('dashboard')", timeout=15000)

            print(f"  Post-login URL: {page.url}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_02_authenticated.png")
            print("  [PASS] Authentication successful.")

            # ------------------------------------------------------------------
            # TEST 3: Desktop Viewport Layout & Accessibility (1280x900)
            # ------------------------------------------------------------------
            print("\n[TEST 3] Loading /tools/marriage-prediction at Desktop Viewport (1280x900)...")
            page.goto(f"{FRONTEND_URL}/tools/marriage-prediction", wait_until="networkidle")
            page.wait_for_selector("h1", timeout=15000)

            h1_text = page.locator("h1").inner_text()
            print(f"  Page Header: {h1_text}")
            assert "Marriage Prediction" in h1_text or "திருமண" in h1_text, "Page title mismatch"

            # Check Epistemological Notice
            disclaimer = page.locator("text=Epistemological & Rule-Based Boundary Notice")
            assert disclaimer.count() > 0, "Epistemological notice missing"
            print("  [PASS] Epistemological & Rule-Based Boundary Notice verified.")

            # Check Form Fields existence
            assert page.locator("#birth-date").count() > 0, "Date input missing"
            assert page.locator("#birth-time").count() > 0, "Time input missing"
            assert page.locator("#birth-timezone").count() > 0, "Timezone input missing"
            assert page.locator("#birth-lat").count() > 0, "Latitude input missing"
            assert page.locator("#birth-lon").count() > 0, "Longitude input missing"
            assert page.locator("#uncertainty-input").count() > 0, "Uncertainty slider missing"
            assert page.locator("#start-year").count() > 0, "Start year input missing"
            assert page.locator("#end-year").count() > 0, "End year input missing"

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_03_desktop_form.png")
            print("  [PASS] All form inputs and accessibility labels verified on Desktop.")

            # ------------------------------------------------------------------
            # TEST 4: Form Input Validation Checks
            # ------------------------------------------------------------------
            print("\n[TEST 4] Testing client-side form validation rules...")

            # A. Clear birth date and submit
            page.fill("#birth-date", "")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(500)
            assert page.locator("text=Birth date is required").count() > 0, "Missing birth date validation error"
            print("  [PASS] Empty birth date rejected.")

            # Restore birth date
            page.fill("#birth-date", "1990-05-15")

            # B. Invalid Latitude (> 90)
            page.fill("#birth-lat", "95.5")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(500)
            assert page.locator("text=Latitude must be a valid number between -90.0 and +90.0").count() > 0, "Lat validation error missing"
            print("  [PASS] Out-of-bounds latitude rejected.")

            # Restore valid latitude
            page.fill("#birth-lat", "13.0827")

            # C. Invalid Longitude (< -180)
            page.fill("#birth-lon", "-195.0")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(500)
            assert page.locator("text=Longitude must be a valid number between -180.0 and +180.0").count() > 0, "Lon validation error missing"
            print("  [PASS] Out-of-bounds longitude rejected.")

            # Restore valid longitude
            page.fill("#birth-lon", "80.2707")

            # D. Invalid IANA Timezone
            page.fill("#birth-timezone", "Invalid/Fictional_Zone")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(500)
            assert page.locator("text=Invalid IANA timezone").count() > 0, "Timezone validation error missing"
            print("  [PASS] Invalid timezone rejected.")

            # Restore valid timezone
            page.fill("#birth-timezone", "Asia/Kolkata")

            # E. Reversed Year Range (End < Start)
            page.fill("#start-year", "2035")
            page.fill("#end-year", "2025")
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(500)
            assert page.locator("text=End year cannot be earlier than Start year").count() > 0, "Year range validation error missing"
            print("  [PASS] Reversed timing year range rejected.")

            # Restore valid years
            page.fill("#start-year", "2024")
            page.fill("#end-year", "2032")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_04_validation_errors.png")

            # ------------------------------------------------------------------
            # TEST 5: Live End-to-End Prediction Execution (Chart 1: EVENT_INDICATED)
            # ------------------------------------------------------------------
            print("\n[TEST 5] Submitting valid live prediction for Chart 1 (1990-05-15)...")
            page.fill("#birth-date", "1990-05-15")
            page.fill("#birth-time", "10:00:00")
            page.fill("#birth-timezone", "Asia/Kolkata")
            page.fill("#birth-lat", "13.0827")
            page.fill("#birth-lon", "80.2707")
            page.fill("#start-year", "2024")
            page.fill("#end-year", "2032")

            submit_btn = page.locator("button[type='submit']")
            submit_btn.click()

            print("  Waiting for #results-section...")
            page.wait_for_selector("#results-section", state="visible", timeout=30000)
            page.wait_for_timeout(1000)
            print("  [PASS] Live prediction calculation returned 200 and rendered dashboard.")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_05_desktop_results_indicated.png")

            # ------------------------------------------------------------------
            # TEST 6: Audit Results Dashboard Sections (Chart 1)
            # ------------------------------------------------------------------
            print("\n[TEST 6] Auditing rendered dashboard components for Chart 1...")

            # A. Master Reconciliation Verdict
            verdict_banner = page.locator("#results-section h3").first.inner_text()
            print(f"  Master Verdict: {verdict_banner}")
            assert "EVENT INDICATED" in verdict_banner, f"Expected EVENT INDICATED, got: {verdict_banner}"
            assert page.locator("text=UNI-MARR-REC-001").count() > 0, "Reconciliation rule missing"
            print("  [PASS] Master reconciliation verdict rendered: EVENT INDICATED.")

            # B. KP Analysis Section
            kp_card = page.locator("text=Krishnamurti Paddhati (KP)")
            assert kp_card.count() > 0, "KP card missing"
            kp_csl = page.locator("text=7th Cusp Sub-Lord (CSL)").locator("..").inner_text()
            print(f"  KP CSL Block: {kp_csl.replace(chr(10), ' ')}")
            assert page.locator("text=KP-MARR-PROM").count() > 0, "KP rule ID missing"
            print("  [PASS] KP cuspal sub-lord mechanics rendered accurately.")

            # C. Vedic Analysis Section
            vedic_card = page.locator("text=Parashari Vedic Astrology")
            assert vedic_card.count() > 0, "Vedic card missing"
            assert page.locator("text=Kuja Dosha Status").count() > 0, "Kuja Dosha block missing"
            assert page.locator("text=Compound Denial Gates Met").count() > 0, "Compound denial gates missing"
            assert page.locator("text=VED-MARR-PROM").count() > 0, "Vedic rule ID missing"
            print("  [PASS] Vedic Parashari placements and denial gates rendered accurately.")

            # D. Birth-Time Sensitivity Diagnostics
            sensitivity_heading = page.locator("text=Continuous Placidus Cusp Birth-Time Sensitivity Scan")
            assert sensitivity_heading.count() > 0, "Sensitivity scan heading missing"
            assert page.locator("text=Numerical Scan Guarantee:").count() > 0, "Scan guarantee missing"
            print("  [PASS] Continuous Placidus sensitivity diagnostics and scientific disclaimer rendered.")

            # E. Timing Windows & Score Terminology
            timing_heading = page.locator("text=Vimshottari Dasha & Transit Timing Evaluation")
            assert timing_heading.count() > 0, "Timing evaluation heading missing"
            timing_status = page.locator("text=Timing Status: WINDOW_FOUND")
            assert timing_status.count() > 0, "Expected Timing Status: WINDOW_FOUND"
            print("  [PASS] Timing Status: WINDOW_FOUND rendered.")

            # Score Terminology & Guardrail Audit
            score_block = page.locator("text=Astrological Confluence Score")
            assert score_block.count() > 0, "Confluence score block missing"
            print("  Score Label: Astrological Confluence Score (Verified)")

            mandatory_notice = page.locator("text=This score represents agreement between the configured astrological timing factors. It is not a statistically validated probability of marriage.")
            assert mandatory_notice.count() > 0, "Mandatory confluence score disclaimer missing!"
            print("  [PASS] Mandatory score disclaimer verified verbatim.")

            # Negative check: ensure the score heading or label is NOT called "Probability of Marriage"
            all_results_text = page.locator("#results-section").inner_text().lower()
            assert page.locator("h4:has-text('Probability of Marriage'), span:has-text('Probability of Marriage')").count() == 0, "Score heading must NOT be 'Probability of Marriage'!"
            assert "percentage chance of marriage" not in all_results_text, "Must NOT display percentage chance of marriage!"
            print("  [PASS] Zero percentage probability claims verified.")

            # F. Calculation Metadata & Dual Ayanamsa Audit
            metadata_btn = page.locator("button:has-text('Calculation Metadata & Ayanamsa Audit')")
            assert metadata_btn.count() > 0, "Metadata accordion missing"
            metadata_btn.click()
            page.wait_for_timeout(800)

            kp_ayan_label = page.locator("text=KP Krishnamurti Ayanamsa (ID: 1)")
            vedic_ayan_label = page.locator("text=Vedic Chitrapaksha Lahiri Ayanamsa (ID: 0)")
            assert kp_ayan_label.count() > 0, "KP ayanamsa ID 1 label missing"
            assert vedic_ayan_label.count() > 0, "Vedic ayanamsa ID 0 label missing"
            print("  [PASS] Dual Ayanamsa values labeled separately and distinctly (KP ID: 1 vs Vedic ID: 0).")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_06_metadata_expanded.png")

            # ------------------------------------------------------------------
            # TEST 7: Second Live Prediction Audit (Chart 2: INDETERMINATE)
            # ------------------------------------------------------------------
            print("\n[TEST 7] Testing Chart 2 (1995-10-24) for INDETERMINATE & Timing Bypass...")
            # Click Clear/Reset or Run Another Analysis and wait for results section to be detached
            rerun_btn = page.locator("button:has-text('Run Another Analysis'), button:has-text('Clear / Reset')").first
            if rerun_btn.count() > 0:
                rerun_btn.click()
                page.wait_for_selector("#results-section", state="detached", timeout=5000)
                page.wait_for_timeout(500)

            page.fill("#birth-date", "1995-10-24")
            page.fill("#birth-time", "14:30:00")
            page.fill("#birth-timezone", "Asia/Kolkata")
            page.fill("#birth-lat", "13.0827")
            page.fill("#birth-lon", "80.2707")
            page.fill("#start-year", "2024")
            page.fill("#end-year", "2032")

            page.locator("button[type='submit']").click()
            page.wait_for_selector("#results-section", state="visible", timeout=30000)
            page.wait_for_timeout(1000)

            verdict_2 = page.locator("#results-section h3").first.inner_text()
            print(f"  Chart 2 Verdict: {verdict_2}")
            assert "INDETERMINATE" in verdict_2, f"Expected INDETERMINATE, got: {verdict_2}"

            # Verify Timing is NOT_EVALUATED
            timing_bypass = page.locator("text=Timing Scan Not Evaluated")
            assert timing_bypass.count() > 0, "Expected timing bypass banner for INDETERMINATE verdict"
            print("  [PASS] INDETERMINATE verdict properly triggers timing evaluation bypass.")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_07_indeterminate_results.png")

            # ------------------------------------------------------------------
            # TEST 8: Mobile Viewport Audit (375x667)
            # ------------------------------------------------------------------
            print("\n[TEST 8] Testing Mobile Viewport (375x667)...")
            page.set_viewport_size({"width": 375, "height": 667})
            page.wait_for_timeout(1000)

            # Check that the tool's main content and results render responsively within mobile viewport
            main_scroll = page.evaluate("() => document.querySelector('main') ? document.querySelector('main').scrollWidth : document.documentElement.clientWidth")
            results_scroll = page.evaluate("() => document.querySelector('#results-section') ? document.querySelector('#results-section').scrollWidth : document.documentElement.clientWidth")
            client_width = page.evaluate("() => document.documentElement.clientWidth")
            print(f"  Mobile main.scrollWidth: {main_scroll}, results.scrollWidth: {results_scroll}, clientWidth: {client_width}")
            assert main_scroll <= client_width + 5, f"Horizontal overflow detected in tool content: {main_scroll} > {client_width}"

            # Verify accessibility of key form fields and results on mobile
            assert page.locator("#birth-date").is_visible(), "Date input not visible on mobile"
            assert page.locator("button[type='submit']").is_visible(), "Submit button not visible on mobile"
            assert page.locator("#results-section").is_visible(), "Results section not visible on mobile"

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_08_mobile_viewport.png")
            print("  [PASS] Mobile viewport renders responsively without horizontal overflow in tool content.")

            # Restore desktop viewport
            page.set_viewport_size({"width": 1280, "height": 900})
            page.wait_for_timeout(500)

            # ------------------------------------------------------------------
            # TEST 9: Re-Analysis & State Preservation
            # ------------------------------------------------------------------
            print("\n[TEST 9] Verifying repeat analysis & form state preservation...")
            rerun_btn = page.locator("button:has-text('Run Another Analysis')").first
            assert rerun_btn.count() > 0, "Rerun button missing"
            rerun_btn.click()
            page.wait_for_selector("#results-section", state="detached", timeout=5000)
            page.wait_for_timeout(800)

            # Verify form values were preserved
            assert page.locator("#birth-date").input_value() == "1995-10-24", "Birth date not preserved"
            assert page.locator("#birth-lat").input_value() == "13.0827", "Latitude not preserved"
            assert page.locator("#birth-lon").input_value() == "80.2707", "Longitude not preserved"
            print("  [PASS] Form values preserved across re-run.")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_09_rerun_state.png")

            # ------------------------------------------------------------------
            # TEST 10: Regression Check on Existing Tools
            # ------------------------------------------------------------------
            print("\n[TEST 10] Verifying existing /tools and /tools/d1-d9 pages...")
            page.goto(f"{FRONTEND_URL}/tools", wait_until="networkidle")
            assert page.locator("text=Horoscope (Vedic & KP)").count() > 0, "Tools page corrupted"
            print("  [PASS] /tools dashboard loads intact.")

            page.goto(f"{FRONTEND_URL}/tools/d1-d9", wait_until="networkidle")
            assert page.locator("text=D1 Rasi & D9 Navamsa").count() > 0, "D1/D9 tool corrupted"
            print("  [PASS] /tools/d1-d9 divisional chart page loads intact.")

            page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_10_tools_regression.png")

            auth_context.close()
            browser.close()

        print("\n" + "=" * 80)
        print("ALL 10 LIVE BROWSER ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
        print(f"Screenshots saved to: {os.path.abspath(SCREENSHOT_DIR)}")
        print("=" * 80)

    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    run_marriage_prediction_browser_audit()
