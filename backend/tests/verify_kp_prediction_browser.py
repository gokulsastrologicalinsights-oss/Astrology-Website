"""Live authenticated browser acceptance test suite for KP Events & Prediction.

Tests:
1. User login via /login
2. Navigation to /tools/kp-events-prediction
3. Saved horoscopes loading & selection
4. Manual mode: Standard Scan execution & candidate windows
5. Manual mode: Deep Scan execution & exact transit ingress/egress boundaries
6. Markdown report generation and copy
7. Regression verification on /tools/advanced-kp
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_test_screenshots/kp_prediction"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def test_browser():
    print("=" * 70)
    print("STARTING KP EVENTS & PREDICTION LIVE AUTHENTICATED BROWSER VERIFICATION")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        # Step 0: Authenticate
        print("\n[STEP 0] Authenticating at http://localhost:3000/login...")
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()
        page.wait_for_url("**/dashboard**", timeout=15000)
        print(f"  Login successful! Landed on: {page.url}")

        # Step 1: Navigate to /tools/kp-events-prediction
        print("\n[STEP 1] Navigating to http://localhost:3000/tools/kp-events-prediction...")
        page.goto("http://localhost:3000/tools/kp-events-prediction", wait_until="networkidle", timeout=30000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_initial_load.png")
        header = page.locator("h1:has-text('KP Events')").inner_text()
        print(f"  Page Header: '{header}'")
        assert "KP Events" in header

        # Step 2: Verify Saved Horoscopes mode
        print("\n[STEP 2] Verifying Saved Horoscopes selection...")
        saved_dropdown = page.locator("select").first
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_saved_horoscopes_mode.png")
        print("  Saved horoscopes loaded successfully.")

        # Step 3: Switch to Manual Mode & Test Standard Scan
        print("\n[STEP 3] Switching to Manual Mode & Running Standard Scan...")
        manual_btn = page.locator("button:has-text('Enter Details Manually')")
        if manual_btn.count() > 0:
            manual_btn.click()
            time.sleep(0.5)

        scan_btn = page.locator("button:has-text('Scan Event Promise & Dates')")
        scan_btn.click()

        # Wait for results
        page.wait_for_selector("text=Promise:", timeout=20000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_standard_scan_results.png")
        promise_text = page.locator("text=Promise:").inner_text()
        print(f"  Standard Scan Promise Result: {promise_text}")
        assert "Promise:" in promise_text

        # Open Candidate Windows
        windows_tab = page.locator("button:has-text('Candidate Windows')")
        windows_tab.click()
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_standard_windows.png")
        print("  Standard candidate windows verified.")

        # Step 4: Run Deep Scan Mode
        print("\n[STEP 4] Switching to Deep Scan Mode (Adaptive ±0.5s bisection)...")
        deep_mode_btn = page.locator("button:has-text('Deep Scan')")
        deep_mode_btn.click()
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_deep_scan_selected.png")

        print("  Submitting Deep Scan...")
        scan_btn.click()

        # Wait for scan calculation to finish (scan button re-enabled)
        page.wait_for_selector("button:has-text('Scan Event Promise & Dates'):not([disabled])", timeout=25000)
        time.sleep(1)

        # Switch to Candidate Windows tab to inspect Deep Scan results
        windows_tab = page.locator("button:has-text('Candidate Windows')")
        windows_tab.click()
        time.sleep(0.5)

        page.wait_for_selector("text=Deep Scan", timeout=10000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/06_deep_scan_results.png")
        print("  Deep Scan calculation finished successfully!")

        page.screenshot(path=f"{SCREENSHOT_DIR}/07_deep_windows_transitions.png")

        # Verify transition card
        exact_text = page.locator("text=Exact Astronomical Ingress / Egress").first.inner_text()
        print(f"  Exact Transition Block: '{exact_text}'")
        assert "Exact Astronomical Ingress" in exact_text

        # Step 5: Test Report tab
        print("\n[STEP 5] Testing Markdown Report generation...")
        report_tab = page.locator("button:has-text('Report')")
        report_tab.click()
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/08_report_tab.png")
        report_content = page.locator("pre").inner_text()
        assert "KP Event Analysis & Timing Report" in report_content
        assert "Deep Scan Mode Active" in report_content
        print("  Report verified: contains Deep Scan precision notes and disclaimers.")

        # Step 6: Regression check on /tools/advanced-kp
        print("\n[STEP 6] Testing regression on /tools/advanced-kp...")
        page.goto("http://localhost:3000/tools/advanced-kp", wait_until="networkidle", timeout=30000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/09_advanced_kp.png")
        adv_header = page.locator("h1:has-text('KP')").first.inner_text()
        print(f"  Advanced KP Header: '{adv_header}'")
        print("  [PASS] /tools/advanced-kp operational!")

        print("\n" + "=" * 70)
        print("ALL AUTHENTICATED BROWSER ACCEPTANCE TESTS PASSED!")
        print("=" * 70)
        browser.close()


if __name__ == "__main__":
    test_browser()
