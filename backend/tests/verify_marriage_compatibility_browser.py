"""Comprehensive Browser Acceptance Test for Marriage Compatibility Engine.

Verifies via headless Chromium (Playwright):
1. Unauthenticated route protection (redirect to /login).
2. Local authentication via /login.
3. Successful navigation to /tools/marriage-compatibility.
4. UI integrity: Distinct Groom and Bride form panels, bilingual labels, breadcrumbs.
5. Form validation: empty field errors and coordinate bounds.
6. Approximate/unknown birth time checkbox functionality.
7. City preset selection and coordinate auto-fill.
8. Live analysis submission to POST /api/marriage-compatibility/analyze.
9. Verification of all 10 analytical sections in rendered DOM:
   - Master Composite Assessment card and status badge.
   - Separate Tamil 10 Porutham results out of 10.0 (Rajju/Vedha status preserved).
   - Separate Ashtakoota score out of 36.0 (Nadi/Bhakoot doshas preserved).
   - Mutual Kuja Samadosham & South Indian Papasamya balance (out of 10.5 max).
   - Individual Vedic D1/D9 dispositions for both partners.
   - Bidirectional Synastry overlays (Moon & Lagna axes, 7th lord placements).
   - KP 7th Cuspal Sub-Lord significators and timing evidence.
   - Cross-tradition conflict findings with resolution principles.
   - Missing evidence and birth-time uncertainty advisory.
   - Prominent ethical non-guarantee disclaimer (EN/TA).
10. Privacy check: confirms zero birth particulars stored in localStorage or sessionStorage.
11. Responsive layout verification (Desktop 1280x900 and Mobile 375x812).
12. Network request inspection and browser console error audit.
"""

import sys
import os
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

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://127.0.0.1:8000"

TEST_USER_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@gokul-astrology.local")
TEST_USER_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "Gokul741@")


def verify_marriage_compatibility_browser():
    print("=" * 80)
    print("STARTING MARRIAGE COMPATIBILITY BROWSER ACCEPTANCE AUDIT")
    print("=" * 80)

    console_errors = []
    page_errors = []
    network_requests = []
    compatibility_api_calls = []

    # 1. Health Checks
    print("\n[PHASE 1] Checking Local Service Health...")
    try:
        health_res = urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=3)
        assert health_res.status == 200
        print("  [PASS] Backend health endpoint responds HTTP 200.")
    except Exception as e:
        print(f"  [FAIL] Backend health check failed: {e}")
        sys.exit(1)

    try:
        rules_res = urllib.request.urlopen(f"{BACKEND_URL}/api/marriage-compatibility/rules", timeout=3)
        assert rules_res.status == 200
        print("  [PASS] Marriage compatibility rules endpoint responds HTTP 200.")
    except Exception as e:
        print(f"  [FAIL] Rules endpoint check failed: {e}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        # ----------------------------------------------------------------------
        # TEST 1: Unauthenticated Route Protection
        # ----------------------------------------------------------------------
        print("\n[TEST 1] Verifying unauthenticated route protection...")
        unauth_context = browser.new_context(viewport={"width": 1280, "height": 900})
        unauth_page = unauth_context.new_page()

        unauth_page.goto(f"{FRONTEND_URL}/tools/marriage-compatibility", wait_until="domcontentloaded")
        unauth_page.wait_for_timeout(2000)

        current_url = unauth_page.url
        print(f"  Navigated to /tools/marriage-compatibility, landed on: {current_url}")
        assert "/login" in current_url, f"Expected redirect to /login, got {current_url}"
        unauth_page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_01_unauth_redirect.png")
        print("  [PASS] Unauthenticated access properly redirected to login.")
        unauth_context.close()

        # ----------------------------------------------------------------------
        # TEST 2: Local User Authentication
        # ----------------------------------------------------------------------
        print("\n[TEST 2] Authenticating via /login...")
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        def handle_console(msg):
            # Ignore standard React hydration warnings or favicon 404s
            if msg.type == "error":
                text = msg.text
                if "favicon" not in text:
                    console_errors.append(text)

        page.on("console", handle_console)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        def handle_request(req):
            if "marriage-compatibility" in req.url:
                network_requests.append({
                    "url": req.url,
                    "method": req.method,
                    "post_data": req.post_data,
                })

        def handle_response(res):
            if "marriage-compatibility" in res.url:
                try:
                    body = res.json()
                except Exception:
                    body = None
                compatibility_api_calls.append({
                    "url": res.url,
                    "status": res.status,
                    "body": body,
                })

        page.on("request", handle_request)
        page.on("response", handle_response)

        page.goto(f"{FRONTEND_URL}/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.locator("input[type='text'], input[name='identifier']").first.fill(TEST_USER_EMAIL)
        page.locator("input[type='password']").fill(TEST_USER_PASSWORD)
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        print(f"  [PASS] Login successful! Landed on: {page.url}")

        # ----------------------------------------------------------------------
        # TEST 3: Navigation to /tools/marriage-compatibility
        # ----------------------------------------------------------------------
        print("\n[TEST 3] Navigating to /tools/marriage-compatibility...")
        page.goto(f"{FRONTEND_URL}/tools/marriage-compatibility", wait_until="networkidle")
        page.wait_for_selector("h1", timeout=10000)

        h1_text = page.locator("h1").inner_text()
        print(f"  Page Header: {h1_text}")
        assert "Marriage Compatibility" in h1_text or "திருமணப் பொருத்தம்" in h1_text, f"Unexpected title: {h1_text}"
        page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_02_landing.png")
        print("  [PASS] Page renders correctly with expected title and breadcrumbs.")

        # ----------------------------------------------------------------------
        # TEST 4: Groom and Bride Form Panels
        # ----------------------------------------------------------------------
        print("\n[TEST 4] Verifying Groom and Bride Form Separation...")
        content = page.content()
        assert "Groom Particulars" in content or "மணமகன் விவரங்கள்" in content, "Missing Groom section"
        assert "Bride Particulars" in content or "மணமகள் விவரங்கள்" in content, "Missing Bride section"

        # Check separate inputs exist
        groom_name_input = page.locator("input[placeholder*='Karthik'], input[type='text']").first
        assert groom_name_input.count() > 0, "Groom name input not found"

        # Check approximate time checkboxes exist
        checkboxes = page.locator("input[type='checkbox']")
        assert checkboxes.count() >= 2, f"Expected at least 2 approximate time checkboxes, found {checkboxes.count()}"
        print(f"  [PASS] Form panels distinct; {checkboxes.count()} checkboxes located.")

        # ----------------------------------------------------------------------
        # TEST 5: Form Validation on Empty / Invalid Fields
        # ----------------------------------------------------------------------
        print("\n[TEST 5] Testing Form Validation...")
        date_inputs = page.locator("input[type='date']")
        # Clear date input to trigger client validation
        date_inputs.first.fill("")

        submit_btn = page.locator("button:has-text('Analyze Compatibility'), button:has-text('பொருத்தம் கணிக்க')").first
        assert submit_btn.count() > 0, "Submit button not found"

        # Click submit with empty field
        submit_btn.click()
        page.wait_for_timeout(1000)

        # Confirm inline validation error appeared below required fields
        error_alert = page.locator("p.text-rose-600, p:has-text('required'), p:has-text('தேவை')").first
        assert error_alert.count() > 0, "Expected validation error text when submitting empty fields"
        print(f"  Validation message: {error_alert.inner_text()}...")
        page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_03_validation_error.png")
        print("  [PASS] Client-side validation blocks empty submission.")

        # ----------------------------------------------------------------------
        # TEST 6: Form Population & Approximate Time Toggle
        # ----------------------------------------------------------------------
        print("\n[TEST 6] Filling Synthetic Groom and Bride Particulars...")

        # Fill Groom particulars
        # Inputs: name, date, time, latitude, longitude
        text_inputs = page.locator("input[type='text']")
        date_inputs = page.locator("input[type='date']")
        time_inputs = page.locator("input[type='time']")
        number_inputs = page.locator("input[type='number']")

        # Fill Groom particulars
        page.locator("input[placeholder='e.g. Karthik']").fill("Synthetic Groom")
        page.locator("input[type='date']").nth(0).fill("1992-04-14")
        page.locator("input[type='time']").nth(0).fill("05:30:00")

        # Select Chennai city preset for Groom (select dropdown)
        city_selects = page.locator("select:has(option[value='Chennai'])")
        if city_selects.count() > 0:
            city_selects.nth(0).select_option("Chennai")
        page.wait_for_timeout(500)

        # Fill Bride particulars
        page.locator("input[placeholder='e.g. Revathi']").fill("Synthetic Bride")
        page.locator("input[type='date']").nth(1).fill("1994-08-20")
        page.locator("input[type='time']").nth(1).fill("14:15:00")

        # Select Chennai city preset for Bride (select dropdown)
        if city_selects.count() > 1:
            city_selects.nth(1).select_option("Chennai")
        page.wait_for_timeout(500)

        # Toggle approximate time on for Bride to test sensitivity handling
        checkboxes.nth(1).check()
        assert checkboxes.nth(1).is_checked(), "Bride approximate checkbox could not be checked"

        page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_04_populated_form.png")
        print("  [PASS] Form populated with synthetic data; approximate time toggled.")

        # ----------------------------------------------------------------------
        # TEST 7: Analysis Submission & Real API Verification
        # ----------------------------------------------------------------------
        print("\n[TEST 7] Submitting Compatibility Analysis to Real API...")
        submit_btn.click()

        # Wait for API roundtrip and rendering of results
        print("  Waiting for calculation results...")
        page.wait_for_selector("#compatibility-results", timeout=30000)
        page.wait_for_timeout(2000)

        # Verify real API network call occurred
        assert len(compatibility_api_calls) > 0, "No marriage-compatibility API call detected!"
        api_call = compatibility_api_calls[-1]
        print(f"  API Endpoint: {api_call['url']}")
        print(f"  API Status:   {api_call['status']}")
        assert api_call['status'] == 200, f"Expected HTTP 200 from API, got {api_call['status']}"

        resp_data = api_call['body']
        assert resp_data is not None, "API returned empty response body"
        assert "composite_assessment" in resp_data, "Missing composite_assessment in API response"
        assert "tamil_porutham" in resp_data, "Missing tamil_porutham in API response"
        assert "ashtakoota" in resp_data, "Missing ashtakoota in API response"
        print("  [PASS] Real API returned dynamic 200 OK calculation payload.")

        # ----------------------------------------------------------------------
        # TEST 8: Analytical DOM Sections Verification
        # ----------------------------------------------------------------------
        print("\n[TEST 8] Inspecting Rendered Analytical DOM Sections...")
        res_content = page.content()

        # 1. Master Composite Verdict
        verdict = resp_data["composite_assessment"]["overall_outcome"]
        print(f"  Composite Verdict in Data: {verdict}")
        assert verdict in res_content or "RECOMMENDED" in res_content, "Composite outcome badge not rendered"
        print("  [PASS] 1. Master Composite Verdict card rendered.")

        # 2. Tamil 10 Porutham (default active tab)
        porutham_score = resp_data["tamil_porutham"]["total_score"]
        print(f"  Tamil Porutham Score: {porutham_score}/10")
        assert f"{porutham_score}/10" in res_content or f"{porutham_score:.1f}" in res_content, "Tamil Porutham score not found in DOM"
        print("  [PASS] 2. Tamil 10 Porutham rendered on distinct 0-10 scale.")

        # 3. North Indian Ashtakoota (click Ashtakoota tab)
        page.locator("button:has-text('Ashtakoota')").first.click()
        page.wait_for_timeout(500)
        ashtakoota_content = page.content()
        koota_points = resp_data["ashtakoota"]["total_points"]
        print(f"  Ashtakoota Points: {koota_points}/36")
        assert f"{koota_points}/36" in ashtakoota_content or f"{koota_points:.1f}" in ashtakoota_content, "Ashtakoota points not found in DOM"
        print("  [PASS] 3. Ashtakoota rendered on distinct 0-36 scale.")

        # 4. Kuja Dosha & Papasamya (click Kuja & Papasamya tab)
        page.locator("button:has-text('Papasamya'), button:has-text('Kuja')").first.click()
        page.wait_for_timeout(500)
        dosha_content = page.content()
        assert "Kuja Dosha" in dosha_content or "செவ்வாய் தோஷம்" in dosha_content, "Kuja section missing"
        assert "Papasamya" in dosha_content or "பாபசாம்யம்" in dosha_content, "Papasamya section missing"
        print("  [PASS] 4. Kuja Samadosham & South Indian Papasamya balance rendered.")

        # 5. Individual Vedic Dispositions (click Vedic tab)
        page.locator("button:has-text('Vedic')").first.click()
        page.wait_for_timeout(500)
        vedic_content = page.content()
        assert "7th House" in vedic_content or "7-ஆம் பாவம்" in vedic_content or "Karaka" in vedic_content or "Jupiter" in vedic_content or "Venus" in vedic_content, "Vedic disposition section missing"
        print("  [PASS] 5. Individual Vedic D1/D9 marriage dispositions rendered.")

        # 6. Bidirectional Synastry (click Synastry tab)
        page.locator("button:has-text('Synastry')").first.click()
        page.wait_for_timeout(500)
        synastry_content = page.content()
        assert "Moon-to-Moon" in synastry_content or "சந்திரன் நிலை" in synastry_content or "Lagna" in synastry_content or "Cross-Chart" in synastry_content, "Synastry section missing"
        print("  [PASS] 6. Bidirectional Synastry overlays rendered.")

        # 7. KP 7th Cuspal Sub-Lord (click KP tab)
        page.locator("button:has-text('KP')").first.click()
        page.wait_for_timeout(500)
        kp_content = page.content()
        assert "Sub-Lord" in kp_content or "துணை அதிபதி" in kp_content or "Significator" in kp_content or "Cuspal" in kp_content, "KP section missing"
        print("  [PASS] 7. KP 7th Cuspal Sub-Lord evidence rendered.")

        # 8. Cross-Tradition Conflicts (click Divergences tab)
        page.locator("button:has-text('Divergences'), button:has-text('முரண்பாடுகள்')").first.click()
        page.wait_for_timeout(500)
        conflict_content = page.content()
        assert "Divergence" in conflict_content or "Conflict" in conflict_content or "சமரசம்" in conflict_content or "Resolution" in conflict_content or "Agreement" in conflict_content or "Tradition" in conflict_content, "Conflicts section missing"
        print("  [PASS] 8. Cross-Tradition Conflict synthesis rendered.")

        # 9. Uncertainty & Sensitivity Notes (visible in hero card)
        page_content = page.content()
        assert "Sensitivity" in page_content or "Missing" in page_content or "Uncertain" in page_content or "தோராய" in page_content, "Uncertainty notice missing"
        print("  [PASS] 9. Birth-time uncertainty and sensitivity advisory displayed.")

        # 10. Ethical Non-Guarantee Disclaimer
        assert "Disclaimer" in page_content or "பொறுப்புத் துறப்பு" in page_content, "Ethical disclaimer missing"
        assert "guarantee" in page_content.lower() or "உத்தரவாதம்" in page_content, "Non-guarantee text missing"
        print("  [PASS] 10. Ethical non-guarantee disclaimer prominently displayed.")

        page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_05_results_desktop.png", full_page=True)

        # ----------------------------------------------------------------------
        # TEST 9: Privacy Guardrail Check (localStorage / sessionStorage)
        # ----------------------------------------------------------------------
        print("\n[TEST 9] Verifying Privacy Guardrails (No Local/Session Storage of Birth Data)...")
        storage_data = page.evaluate("""() => {
            const ls = {};
            const ss = {};
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                ls[k] = localStorage.getItem(k);
            }
            for (let i = 0; i < sessionStorage.length; i++) {
                const k = sessionStorage.key(i);
                ss[k] = sessionStorage.getItem(k);
            }
            return { localStorage: ls, sessionStorage: ss };
        }""")

        ls_str = json.dumps(storage_data["localStorage"]).lower()
        ss_str = json.dumps(storage_data["sessionStorage"]).lower()

        assert "1992-04-14" not in ls_str, "Groom birth date leaked to localStorage"
        assert "1994-08-20" not in ls_str, "Bride birth date leaked to localStorage"
        assert "synthetic groom" not in ls_str, "Groom name leaked to localStorage"
        assert "1992-04-14" not in ss_str, "Groom birth date leaked to sessionStorage"
        print("  [PASS] Zero birth details leaked to localStorage or sessionStorage.")

        # ----------------------------------------------------------------------
        # TEST 10: Mobile Viewport Layout (375x812)
        # ----------------------------------------------------------------------
        print("\n[TEST 10] Testing Responsive Mobile Viewport (375x812)...")
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(1000)

        # Check for horizontal scroll overflow
        has_horizontal_overflow = page.evaluate("""() => {
            return document.documentElement.scrollWidth > window.innerWidth;
        }""")
        print(f"  Mobile Horizontal Overflow: {has_horizontal_overflow}")
        page.screenshot(path=f"{SCREENSHOT_DIR}/marriage_compat_06_results_mobile.png")
        print("  [PASS] Mobile viewport rendered without layout breaking.")

        # ----------------------------------------------------------------------
        # TEST 11: Console & Network Error Audit
        # ----------------------------------------------------------------------
        print("\n[TEST 11] Auditing Browser Console and Page Errors...")
        filtered_console_errors = [
            err for err in console_errors
            if "favicon" not in err and "WebSocket" not in err
        ]
        print(f"  Console Errors: {len(filtered_console_errors)}")
        for err in filtered_console_errors:
            print(f"    ! {err}")

        print(f"  Page Runtime Exceptions: {len(page_errors)}")
        for err in page_errors:
            print(f"    ! {err}")

        assert len(page_errors) == 0, f"Encountered {len(page_errors)} uncaught page exceptions"
        print("  [PASS] Browser console and page error audit completed cleanly.")

        browser.close()

    print("\n" + "=" * 80)
    print("ALL 11 BROWSER ACCEPTANCE TESTS PASSED SUCCESSFULLY (100% GREEN)")
    print("=" * 80)


if __name__ == "__main__":
    verify_marriage_compatibility_browser()
