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
    print("STARTING LIVE REPRODUCTION OF KP EVENTS PREDICTION SCAN", flush=True)
    print("=" * 70, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Capture console messages
        def on_console(msg):
            print(f"  [CONSOLE {msg.type.upper()}] {msg.text}", flush=True)
        page.on("console", on_console)

        def on_page_error(err):
            print(f"  [PAGE UNCAUGHT ERROR] {err}", flush=True)
        page.on("pageerror", on_page_error)

        # Capture requests
        def on_request(req):
            print(f"  --> [REQ] {req.method} {req.url}", flush=True)
        page.on("request", on_request)

        # Capture responses
        def on_response(res):
            print(f"  <-- [RES] {res.status} {res.url}", flush=True)
        page.on("response", on_response)

        # Capture failed requests
        def on_request_failed(req):
            print(f"  !!! [FAIL] {req.method} {req.url} -> {req.failure}", flush=True)
        page.on("requestfailed", on_request_failed)

        # Step 1: Login
        print("\n1. Logging in as admin...", flush=True)
        page.goto("http://localhost:3000/login", wait_until="networkidle")
        page.fill("input[name='identifier'], input[type='text']", "admin@gokul-astrology.local")
        page.fill("input[name='password'], input[type='password']", "Gokul741@")
        page.click("button[type='submit']")
        page.wait_for_timeout(4000)
        print("  Current URL after login:", page.url, flush=True)

        # Step 2: Navigate to /tools/kp-events-prediction
        print("\n2. Navigating to /tools/kp-events-prediction...", flush=True)
        page.goto("http://localhost:3000/tools/kp-events-prediction", wait_until="networkidle")
        page.wait_for_timeout(3000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/scan_01_loaded.png")

        # Check saved horoscopes dropdown
        selects = page.locator("select").all()
        print(f"  Found {len(selects)} select elements.", flush=True)
        for i, s in enumerate(selects):
            opts = s.locator("option").all_inner_texts()
            print(f"    Select {i}: {opts[:3]}", flush=True)

        # Check if button is visible
        buttons = page.locator("button").all()
        for b in buttons:
            txt = b.inner_text().strip()
            if "Scan" in txt or "கணக்கிடு" in txt:
                print(f"  Found scan button: '{txt}'", flush=True)

        scan_btn = page.locator("button:has-text('Scan Event Promise & Dates'), button:has-text('கணக்கிடு')").first
        if scan_btn.is_visible():
            print("\n3. Clicking scan button...", flush=True)
            scan_btn.click()
            print("  Clicked! Waiting 8 seconds...", flush=True)
            page.wait_for_timeout(8000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/scan_02_after_click.png")

            right_col = page.locator(".lg\\:col-span-8")
            print("  Right column visible:", right_col.is_visible(), flush=True)
            print("  Right column text:\n", right_col.inner_text()[:600], flush=True)
            page.screenshot(path=f"{SCREENSHOT_DIR}/scan_02_after_click.png", full_page=True)
        else:
            print("  Scan button NOT visible! Dumping page text:")
            print(page.locator("body").inner_text()[:500])

        browser.close()

if __name__ == "__main__":
    main()
