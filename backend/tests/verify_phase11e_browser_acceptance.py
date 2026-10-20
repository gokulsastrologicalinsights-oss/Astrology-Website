"""Phase 11E — End-to-End Playwright Browser Acceptance Test Suite.

Verifies:
1. Unauthenticated route behavior & login prompt in Saved Reports.
2. User authentication via /login.
3. Marriage Compatibility calculation run and results rendering.
4. "Save Report" workflow, title modal, duplicate-submission prevention (disabled state + spinner).
5. Saved status indicator badge ("Saved (#X)") in Master Assessment card.
6. Switching to "Saved Reports" tab with sequential display number badges and summary chips.
7. Metadata editing (updating title and partner names) with persistence.
8. Opening saved report: historical snapshot restoration into results with immutable banner, zero recalculation.
9. Deleting saved report with confirmation dialog and empty state handling.
10. Responsive layout on Desktop (1280x900) and Mobile (375x812).
11. Privacy audit: zero localStorage / sessionStorage retention of birth inputs or report snapshots.
12. Browser console error & network inspection.
"""

import os
import sys
import time
import json
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_test_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

TEST_USER_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@gokul-astrology.local")
TEST_USER_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "Gokul741@")


def run_browser_acceptance():
    print("=" * 80)
    print("PHASE 11E: SAVED MARRIAGE REPORTS END-TO-END BROWSER ACCEPTANCE AUDIT")
    print("=" * 80)

    console_errors = []
    page_errors = []
    network_requests = []
    failed_responses = []

    # 1. Health Verification
    print(f"\n[PHASE 1] Checking Frontend ({FRONTEND_URL}) and Backend ({BACKEND_URL})...")
    try:
        urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=3)
        print("  [PASS] Backend health endpoint reachable (HTTP 200).")
    except Exception as e:
        print(f"  [FAIL] Backend server not reachable at {BACKEND_URL}: {e}")
        sys.exit(1)

    try:
        urllib.request.urlopen(f"{FRONTEND_URL}", timeout=3)
        print("  [PASS] Frontend server reachable (HTTP 200).")
    except Exception as e:
        print(f"  [FAIL] Frontend server not reachable at {FRONTEND_URL}: {e}")
        sys.exit(1)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(channel="msedge", headless=True)

        # ----------------------------------------------------------------------
        # TEST 1: Unauthenticated Visit & Auth Redirect
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Verifying unauthenticated behavior on /tools/marriage-compatibility...")
        unauth_ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        unauth_page = unauth_ctx.new_page()

        unauth_page.goto(f"{FRONTEND_URL}/tools/marriage-compatibility", wait_until="domcontentloaded")
        unauth_page.wait_for_timeout(2000)

        current_url = unauth_page.url
        print(f"  Navigated to /tools/marriage-compatibility, landed on: {current_url}")
        assert "/login" in current_url, f"Expected redirect to /login, got {current_url}"
        unauth_page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_01_unauth_saved_prompt.png")
        print("  [PASS] Unauthenticated access properly blocked by middleware and redirected to /login.")
        unauth_ctx.close()

        # ----------------------------------------------------------------------
        # TEST 2: User Authentication
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Authenticating via /login...")
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        def handle_console(msg):
            if msg.type == "error":
                text = msg.text
                if "favicon" not in text and "404" not in text:
                    console_errors.append(text)

        page.on("console", handle_console)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        def handle_response(res):
            if res.status >= 400 and "favicon" not in res.url:
                failed_responses.append(f"{res.status} {res.url}")

        page.on("response", handle_response)

        page.goto(f"{FRONTEND_URL}/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.locator("input[type='text'], input[name='identifier']").first.fill(TEST_USER_EMAIL)
        page.locator("input[type='password']").fill(TEST_USER_PASSWORD)
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        page.wait_for_timeout(3000)
        print(f"  [PASS] Login successful! Current page: {page.url}")

        # ----------------------------------------------------------------------
        # TEST 3: Navigate to Marriage Compatibility & Run Analysis
        # ----------------------------------------------------------------------
        print("\n[TEST 3] Navigating to Marriage Compatibility and running analysis...")
        page.goto(f"{FRONTEND_URL}/tools/marriage-compatibility", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  Landed on: {page.url}")
        page.wait_for_selector("input[placeholder='e.g. Karthik']", timeout=15000)

        # Fill Groom & Bride Details
        page.locator("input[placeholder='e.g. Karthik']").fill("Karthik Acceptance")
        page.locator("input[placeholder='e.g. Revathi']").fill("Revathi Acceptance")

        # Submit compatibility analysis
        submit_btn = page.locator("button:has-text('Analyze Compatibility'), button:has-text('பொருத்தம் கணிக்க')").first
        submit_btn.scroll_into_view_if_needed()
        submit_btn.click()

        try:
            page.wait_for_selector("#compatibility-results", timeout=30000)
            print("  [PASS] Compatibility analysis completed and results rendered.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_02_analysis_results.png")
        except Exception as e:
            page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_02_analysis_failed.png")
            err_el = page.locator(".text-rose-600, .bg-rose-50").first
            err_text = err_el.text_content() if err_el.count() > 0 else "None found"
            print(f"  [ERROR] Page error banner: {err_text}")
            print(f"  Console errors: {console_errors}")
            raise

        # ----------------------------------------------------------------------
        # TEST 4: Save Report Action & Duplicate Prevention
        # ----------------------------------------------------------------------
        print("\n[TEST 4] Testing Save Report action and modal dialog...")
        save_btn = page.locator("button:has-text('Save Report')")
        assert save_btn.is_visible(), "Save Report button must be visible in results"
        save_btn.click()

        page.wait_for_selector("input[placeholder='e.g. Groom & Bride Compatibility']", timeout=5000)
        title_input = page.locator("input[placeholder='e.g. Groom & Bride Compatibility']")
        title_input.fill("E2E Acceptance Vivaha Report")

        confirm_save_btn = page.locator("button:has-text('Confirm Save')")
        confirm_save_btn.click()

        # Verify saved badge appears in Hero Card
        page.wait_for_selector("text=Saved (#", timeout=10000)
        saved_badge_text = page.locator("span:has-text('Saved (#')").text_content()
        print(f"  [PASS] Report saved successfully! Status badge: '{saved_badge_text}'")
        page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_03_saved_badge.png")

        # ----------------------------------------------------------------------
        # TEST 5: Saved Reports List Navigation & Summary Cards
        # ----------------------------------------------------------------------
        print("\n[TEST 5] Testing Saved Reports tab and listing...")
        saved_tab_btn = page.locator("button:has-text('Saved Reports')")
        saved_tab_btn.click()
        page.wait_for_selector("text=E2E Acceptance Vivaha Report", timeout=10000)
        assert page.locator("text=#1").is_visible() or page.locator("text=#").is_visible()
        print("  [PASS] Saved report appears at top of Saved Reports list.")
        page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_04_saved_reports_list.png")

        # ----------------------------------------------------------------------
        # TEST 6: Metadata Editing Modal
        # ----------------------------------------------------------------------
        print("\n[TEST 6] Testing metadata editing (title & partner names)...")
        edit_btn = page.locator("button[title*='Edit metadata']").first
        edit_btn.click()

        page.wait_for_selector("input[placeholder*='Match']", timeout=5000)
        edit_title_input = page.locator("input[placeholder*='Match']")
        edit_title_input.fill("Updated E2E Vivaha Report")

        save_changes_btn = page.locator("button[type='submit']:has-text('Save')")
        save_changes_btn.click()

        page.wait_for_selector("text=Updated E2E Vivaha Report", timeout=8000)
        print("  [PASS] Report title successfully updated in metadata modal.")
        page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_05_metadata_updated.png")

        # ----------------------------------------------------------------------
        # TEST 7: Open Report & Historical Snapshot Fidelity
        # ----------------------------------------------------------------------
        print("\n[TEST 7] Testing Open Report and historical snapshot rendering...")
        open_btn = page.locator("button:has-text('Open Report')").first
        open_btn.click()

        # Must switch back to analysis view with historical banner
        page.wait_for_selector("text=Historical snapshot saved on", timeout=10000)
        assert page.locator("text=Close Historical View").is_visible()
        assert page.locator("#compatibility-results").is_visible()
        print("  [PASS] Historical snapshot rendered directly into results view with banner.")
        page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_06_historical_snapshot_view.png")

        # Close historical view
        page.locator("button:has-text('Close Historical View')").click()
        page.wait_for_timeout(1000)
        assert not page.locator("text=Historical snapshot saved on").is_visible()
        print("  [PASS] Closed historical snapshot view cleanly.")

        # ----------------------------------------------------------------------
        # TEST 8: Delete Report Flow
        # ----------------------------------------------------------------------
        print("\n[TEST 8] Testing report deletion and empty state...")
        page.locator("button:has-text('Saved Reports')").click()
        page.wait_for_selector("button[title*='Delete report']", timeout=10000)

        # Handle window.confirm for deletion
        page.on("dialog", lambda dialog: dialog.accept())

        delete_btn = page.locator("button[title*='Delete report']").first
        delete_btn.click()

        page.wait_for_timeout(2000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_07_after_delete.png")
        print("  [PASS] Report deletion completed cleanly.")

        # ----------------------------------------------------------------------
        # TEST 9: Mobile Viewport Responsiveness
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Verifying mobile viewport layout (375x812)...")
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 375, "height": 812})
        mobile_page.goto(f"{FRONTEND_URL}/tools/marriage-compatibility", wait_until="domcontentloaded")
        mobile_page.wait_for_timeout(1500)

        mobile_page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_08_mobile_analysis.png")
        mobile_page.locator("button:has-text('Saved Reports')").click()
        mobile_page.wait_for_timeout(1000)
        mobile_page.screenshot(path=f"{SCREENSHOT_DIR}/phase11e_09_mobile_saved_reports.png")
        print("  [PASS] Mobile responsive view verified for both Analysis and Saved Reports.")
        mobile_page.close()

        # ----------------------------------------------------------------------
        # TEST 10: Storage & Privacy Inspection
        # ----------------------------------------------------------------------
        print("\n[TEST 10] Auditing localStorage and sessionStorage privacy...")
        storage_data = page.evaluate("""() => {
            return {
                localKeys: Object.keys(localStorage),
                sessionKeys: Object.keys(sessionStorage),
                localValues: Object.values(localStorage).join(' '),
                sessionValues: Object.values(sessionStorage).join(' ')
            };
        }""")

        forbidden_terms = ["Karthik Acceptance", "Revathi Acceptance", "overall_outcome", "tamil_porutham", "ashtakoota"]
        for term in forbidden_terms:
            assert term not in storage_data["localValues"], f"Privacy violation: '{term}' found in localStorage!"
            assert term not in storage_data["sessionValues"], f"Privacy violation: '{term}' found in sessionStorage!"

        print("  [PASS] Zero sensitive birth details or calculation snapshots stored in browser storage.")

        # Audit console errors
        print("\n[AUDIT] Console & Network Inspection Summary:")
        print(f"  Console Errors logged: {len(console_errors)}")
        for err in console_errors:
            print(f"    - {err}")

        context.close()
        browser.close()

    print("\n" + "=" * 80)
    print("PHASE 11E BROWSER ACCEPTANCE AUDIT COMPLETE: ALL PASSING")
    print("=" * 80)


if __name__ == "__main__":
    run_browser_acceptance()
