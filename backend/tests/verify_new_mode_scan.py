import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SCREENSHOT_DIR = "browser_test_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def main():
    print("=" * 70, flush=True)
    print("VERIFYING 'NEW' MODE IN KP EVENTS PREDICTION SCAN", flush=True)
    print("=" * 70, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Step 1: Login
        print("\n1. Logging in as admin...", flush=True)
        page.goto("http://localhost:3000/login", wait_until="networkidle")
        page.fill("input[name='identifier'], input[type='text']", "admin@gokul-astrology.local")
        page.fill("input[name='password'], input[type='password']", "Gokul741@")
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Step 2: Navigate to /tools/kp-events-prediction
        print("\n2. Navigating to /tools/kp-events-prediction...", flush=True)
        page.goto("http://localhost:3000/tools/kp-events-prediction", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Step 3: Switch to "New" mode tab
        print("\n3. Switching to 'New' mode...", flush=True)
        new_tab = page.locator("button:has-text('New')").first
        new_tab.click()
        page.wait_for_timeout(1000)

        # Fill manual inputs
        name_input = page.locator("input[placeholder*='Client name'], input[placeholder*='பெயர்']").first
        if name_input.is_visible():
            name_input.fill("Manual Verification Person")

        # Click Scan button
        scan_btn = page.locator("button:has-text('Scan Event Promise & Dates')").first
        print("  Clicking scan button in New mode...", flush=True)
        scan_btn.click()
        page.wait_for_timeout(8000)

        page.screenshot(path=f"{SCREENSHOT_DIR}/scan_03_new_mode_result.png", full_page=True)

        right_col = page.locator(".lg\\:col-span-8")
        print("  Results visible in New mode:", right_col.is_visible(), flush=True)
        print("  Snippet:", right_col.inner_text()[:400], flush=True)

        browser.close()

if __name__ == "__main__":
    main()
