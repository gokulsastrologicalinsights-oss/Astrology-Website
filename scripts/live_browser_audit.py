"""Live Browser Acceptance Audit for Gokul's Astrological Insights.

Performs a read-only-first, live browser acceptance audit:
1. Multi-viewport testing at 1366x768, 1440x900, and 1920x1080.
2. Checks horizontal overflow, console errors, network failures.
3. Tests authentication and session security.
4. Audits:
   - Global Header (search, language toggle, help modal, profile dropdown, logout)
   - Tier 2 Navigation Bar (horizontal tabs with gold indicators)
   - Dashboard & Module Cards (compact grid, gold line headers)
   - Saved Horoscopes Listing (page header, status banner, toolbar, customer cards)
   - Individual Horoscope Details (header, pill toggle, birth details row, main tabs, secondary tabs)
   - 3-Chart Grid (Rasi D1, Navamsa D9, Bhava Chakra)
   - Dasa-Bhukti Table (navy header, 5-column table, sub-period expansion)
   - KP System View via mode pill toggle
   - Consultation & Reports Tabs
   - Notes Modal
5. Tests bilingual localization (English and Tamil) and typography.
6. Captures high-res visual screenshot evidence for each resolution.
"""

import os
import sys
import time
import json

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from playwright.sync_api import sync_playwright

OUTPUT_DIR = "browser_audit_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RESOLUTIONS = [
    {"name": "1366x768", "width": 1366, "height": 768},
    {"name": "1440x900", "width": 1440, "height": 900},
    {"name": "1920x1080", "width": 1920, "height": 1080},
]

AUTHORITATIVE_HORO_ID = "0e4ecbcb-51c9-43aa-9381-1f7c1cb46a8a"

audit_log = []
console_errors = []
network_failures = []

def record(category, test_name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] [{category}] {test_name}" + (f" -> {details}" if details else ""), flush=True)
    audit_log.append({
        "category": category,
        "test": test_name,
        "status": status,
        "details": str(details),
    })

def wait_for_ready(page, timeout=12000):
    """Waits for client hydration, removing loading spinners and rendering nav."""
    try:
        page.wait_for_selector(".animate-spin", state="detached", timeout=timeout)
    except Exception:
        pass
    try:
        page.wait_for_selector("nav[aria-label='Secondary Navigation Bar']", timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(300)

def check_horizontal_overflow(page, page_name, res_name):
    overflow = page.evaluate("""
        () => {
            const docWidth = document.documentElement.scrollWidth;
            const winWidth = window.innerWidth;
            return {
                hasOverflow: docWidth > winWidth + 2,
                scrollWidth: docWidth,
                innerWidth: winWidth
            };
        }
    """)
    passed = not overflow["hasOverflow"]
    details = f"scrollWidth={overflow['scrollWidth']}, innerWidth={overflow['innerWidth']}"
    record("Layout-Overflow", f"{page_name} at {res_name} no horizontal scroll", passed, details)
    return passed

def run_audit():
    print("=" * 80)
    print("  GOKUL'S ASTROLOGICAL INSIGHTS - LIVE BROWSER ACCEPTANCE AUDIT")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        # ----------------------------------------------------------------------
        # AUDIT 1: Unauthenticated Security & Redirect Check
        # ----------------------------------------------------------------------
        print("\n--- PHASE 1: Security & Unauthenticated Access ---")
        context_guest = browser.new_context(viewport={"width": 1366, "height": 768})
        page_guest = context_guest.new_page()

        page_guest.goto("http://localhost:3000/dashboard", wait_until="domcontentloaded")
        page_guest.wait_for_timeout(1000)
        is_redirected_login = "/login" in page_guest.url
        record("Security", "Unauthenticated /dashboard redirects to /login", is_redirected_login, page_guest.url)

        page_guest.goto("http://localhost:3000/horoscopes", wait_until="domcontentloaded")
        page_guest.wait_for_timeout(1000)
        is_redirected_horo = "/login" in page_guest.url
        record("Security", "Unauthenticated /horoscopes redirects to /login", is_redirected_horo, page_guest.url)

        context_guest.close()

        # ----------------------------------------------------------------------
        # PHASE 2: Authenticated Session Setup
        # ----------------------------------------------------------------------
        print("\n--- PHASE 2: Authentication & Session Setup ---")
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(f"CONSOLE {msg.type}: {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: console_errors.append(f"PAGE ERROR: {err}"))
        page.on("response", lambda resp: network_failures.append(f"HTTP {resp.status} {resp.url}") if resp.status >= 400 and not "/_next/" in resp.url and not "favicon" in resp.url else None)

        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[id='login-username'], input[name='identifier']", timeout=10000)
        page.wait_for_timeout(1500)

        # Fill credentials
        page.locator("input[id='login-username'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[id='login-password'], input[name='password']").first.fill("Gokul741@")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        wait_for_ready(page)
        record("Authentication", "Admin login successful and session established", True, page.url)

        # ----------------------------------------------------------------------
        # PHASE 3: Multi-Resolution Layout & Visual Audit (English)
        # ----------------------------------------------------------------------
        for res in RESOLUTIONS:
            res_name = res["name"]
            width = res["width"]
            height = res["height"]
            print(f"\n--- PHASE 3: Testing Resolution {res_name} ({width}x{height}) ---")

            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(400)

            # --- A. Dashboard Page ---
            page.goto("http://localhost:3000/dashboard", wait_until="domcontentloaded")
            wait_for_ready(page)
            check_horizontal_overflow(page, "Dashboard", res_name)

            has_brand = page.locator("text=Gokul's Astrological Insights").first.is_visible()
            record("UI-Header", f"Brand name visible at {res_name}", has_brand)

            has_search = page.locator("header input, input[placeholder*='features'], input[placeholder*='Search']").first.is_visible()
            record("UI-Header", f"Header search input visible at {res_name}", has_search)

            has_headphones = page.locator("button[aria-label*='Support'], button[title*='Support'], button[title*='Help'], button[title*='உதவி']").first.is_visible()
            record("UI-Header", f"Support headphones icon visible at {res_name}", has_headphones)

            has_nav = page.locator("nav[aria-label='Secondary Navigation Bar']").first.is_visible()
            record("UI-Navigation", f"Tier 2 navigation bar rendered at {res_name}", has_nav)

            cards_count = page.locator("a[href^='/tools'], a[href^='/horoscope'], a[href^='/remedies']").count()
            record("UI-Cards", f"Dashboard quick-access module cards rendered at {res_name}", cards_count >= 6, f"Count: {cards_count}")

            page.screenshot(path=f"{OUTPUT_DIR}/01_dashboard_{res_name}.png", full_page=True)

            # --- B. Tools Landing Page ---
            page.goto("http://localhost:3000/tools", wait_until="domcontentloaded")
            wait_for_ready(page)
            check_horizontal_overflow(page, "Tools-Hub", res_name)
            tools_count = page.locator("a[href*='/tools/']").count()
            record("UI-Tools", f"Tools landing page cards rendered at {res_name}", tools_count >= 4, f"Count: {tools_count}")
            page.screenshot(path=f"{OUTPUT_DIR}/02_tools_hub_{res_name}.png", full_page=True)

            # --- C. Saved Horoscopes Listing ---
            page.goto("http://localhost:3000/horoscopes", wait_until="domcontentloaded")
            try:
                page.wait_for_selector("a[href*='/horoscope/results?id=']", timeout=12000)
            except Exception:
                page.wait_for_timeout(2000)

            check_horizontal_overflow(page, "Saved-Horoscopes", res_name)

            has_toolbar_search = page.locator("input[placeholder*='Search'], input[placeholder*='பெயர்']").first.is_visible()
            has_find_btn = page.locator("button:has-text('Search'), button:has-text('கண்டுபிடி')").first.is_visible()
            has_export_btn = page.locator("button:has-text('Export'), button:has-text('பதிவிறக்கம்')").first.is_visible()
            record("UI-Toolbar", f"Saved horoscopes toolbar complete at {res_name}", has_toolbar_search and has_find_btn and has_export_btn)

            horo_links = page.locator("a[href*='/horoscope/results?id=']")
            card_count = horo_links.count()
            record("UI-Cards", f"Saved horoscope customer cards rendered at {res_name}", card_count >= 1, f"Found {card_count} cards")
            page.screenshot(path=f"{OUTPUT_DIR}/03_saved_horoscopes_{res_name}.png", full_page=True)

            # --- D. Individual Horoscope Detail Page (Screenshot 3 & 4 layout) ---
            detail_url = f"http://localhost:3000/horoscope/results?id={AUTHORITATIVE_HORO_ID}"
            page.goto(detail_url, wait_until="domcontentloaded")
            try:
                page.wait_for_selector("h1:has-text('Horoscope Details'), h1:has-text('ஜாதக விவரங்கள்')", timeout=12000)
            except Exception:
                page.wait_for_timeout(2000)

            check_horizontal_overflow(page, "Horoscope-Detail", res_name)

            # 1. Header Row
            has_detail_title = page.locator("h1:has-text('Horoscope Details'), h1:has-text('ஜாதக விவரங்கள்')").first.is_visible()
            record("UI-Detail", f"Horoscope detail title visible at {res_name}", has_detail_title)

            # 2. Pill Toggle [ ॐ Vedic Horoscope | ★ KP System ]
            has_vedic_pill = page.locator("button:has-text('Vedic Horoscope'), button:has-text('வேத ஜாதகம்')").first.is_visible()
            has_kp_pill = page.locator("button:has-text('KP System'), button:has-text('கே.பி ஜாதகம்')").first.is_visible()
            record("UI-Detail", f"Vedic/KP pill toggle visible at {res_name}", has_vedic_pill and has_kp_pill)

            # 3. Customer Info Row (Name, DOB, Age, Place, Time, Ayanamsa)
            has_customer_info = page.locator("text=Date of Birth:").or_(page.locator("text=பிறந்த தேதி:")).first.is_visible()
            record("UI-Detail", f"Horizontal customer details bar visible at {res_name}", has_customer_info)

            # 4. 3-Chart Grid Verification (Rasi D1, Navamsa D9, Bhava Chakra)
            has_rasi_chart = page.locator("h3:has-text('Rasi (D1)'), h3:has-text('ராசி (D1)')").first.is_visible()
            has_navamsa_chart = page.locator("h3:has-text('Navamsa (D9)'), h3:has-text('நவாம்சம் (D9)')").first.is_visible()
            has_bhava_chart = page.locator("h3:has-text('Bhava Chakra'), h3:has-text('பாவக சக்கரம்')").first.is_visible()
            record("UI-Charts", f"3-Chart landscape grid (Rasi, Navamsa, Bhava) rendered at {res_name}", has_rasi_chart and has_navamsa_chart and has_bhava_chart)

            page.screenshot(path=f"{OUTPUT_DIR}/04_horoscope_3charts_{res_name}.png", full_page=True)

            # 5. Dasa-Bhukti Tab Verification (Screenshot 4 Reference)
            dasa_tab = page.locator("button:has-text('Dasa-Bhukti'), button:has-text('தசா புத்தி')").first
            if dasa_tab.is_visible():
                dasa_tab.click()
                page.wait_for_timeout(600)
                has_dasa_card = page.locator("text='Mahadasha'").first.is_visible()
                has_bhukti_col = page.locator("th:has-text('Bukthi'), th:has-text('புத்தி')").first.is_visible()
                has_benefit_col = page.locator("th:has-text('Benefit Bhavas'), th:has-text('பலன் பாவங்கள்')").first.is_visible()
                record("UI-Dasa", f"Dasa-Bhukti cards & 5-col table rendered at {res_name}", has_dasa_card and has_bhukti_col and has_benefit_col)
                page.screenshot(path=f"{OUTPUT_DIR}/05_dasa_bhukti_{res_name}.png", full_page=True)

            # 6. KP Mode Pill Toggle Verification
            kp_pill_btn = page.locator("button:has-text('KP System'), button:has-text('கே.பி ஜாதகம்')").first
            if kp_pill_btn.is_visible():
                kp_pill_btn.click()
                page.wait_for_timeout(800)
                has_kp_section = page.locator("text=KP Krishnamurti Paddhati System").or_(page.locator("text=கே.பி. கிருஷ்ணமூர்த்தி பத்ததி முறை")).first.is_visible()
                record("UI-KP", f"KP Section rendered via pill toggle at {res_name}", has_kp_section)
                page.screenshot(path=f"{OUTPUT_DIR}/06_kp_mode_{res_name}.png", full_page=True)

                # Switch back to Vedic mode
                page.locator("button:has-text('Vedic Horoscope'), button:has-text('வேத ஜாதகம்')").first.click()
                page.wait_for_timeout(600)

            # 7. Consultation Main Tab Verification
            consult_tab = page.locator("button:has-text('Consultation'), button:has-text('ஆலோசனை')").first
            if consult_tab.is_visible():
                consult_tab.click()
                page.wait_for_timeout(600)
                has_consult_title = page.locator("textarea").first.is_visible()
                record("UI-Consultation", f"Consultation notes textarea rendered at {res_name}", has_consult_title)
                page.screenshot(path=f"{OUTPUT_DIR}/07_consultation_tab_{res_name}.png", full_page=True)

            # 8. Reports & Downloads Main Tab Verification
            reports_tab = page.locator("button:has-text('Reports'), button:has-text('அறிக்கைகள்')").first
            if reports_tab.is_visible():
                reports_tab.click()
                page.wait_for_timeout(600)
                has_reports_pdf = page.locator("button:has-text('Print / PDF'), button:has-text('அச்சிடுக / PDF')").first.is_visible()
                has_reports_csv = page.locator("button:has-text('Export CSV'), button:has-text('CSV பதிவிறக்கம்')").first.is_visible()
                record("UI-Reports", f"Reports & Downloads tab rendered at {res_name}", has_reports_pdf and has_reports_csv)
                page.screenshot(path=f"{OUTPUT_DIR}/08_reports_tab_{res_name}.png", full_page=True)

            # 9. Notes Modal Verification
            notes_btn = page.locator("button:has-text('Notes'), button:has-text('குறிப்புகள்')").first
            if notes_btn.is_visible():
                notes_btn.click()
                page.wait_for_timeout(500)
                has_modal = page.locator("h3:has-text('Horoscope Notes'), h3:has-text('ஜாதகக் குறிப்புகள்')").first.is_visible()
                record("UI-Modal", f"Notes modal opens at {res_name}", has_modal)
                page.screenshot(path=f"{OUTPUT_DIR}/09_notes_modal_{res_name}.png")
                # Close modal
                page.locator("button:has-text('Close'), button:has-text('மூடுக')").first.click()
                page.wait_for_timeout(400)

        # ----------------------------------------------------------------------
        # PHASE 4: Interactive Functional Verifications
        # ----------------------------------------------------------------------
        print("\n--- PHASE 4: Interactive Functional Verifications ---")

        # 1. Header Search Interaction
        page.goto("http://localhost:3000/dashboard", wait_until="domcontentloaded")
        wait_for_ready(page)
        search_input = page.locator("header input, input[placeholder*='features'], input[placeholder*='Search']").first
        search_input.fill("Horoscope")
        page.wait_for_timeout(500)
        search_dropdown = page.locator("div[class*='absolute'][class*='bg-white']").first
        record("Interactive-Search", "Header search queries and displays interactive dropdown", search_dropdown.is_visible())
        page.screenshot(path=f"{OUTPUT_DIR}/10_header_search_dropdown.png")

        # 2. Support Modal Interaction
        support_btn = page.locator("button[aria-label*='Support'], button[title*='Support'], button[title*='Help'], button[title*='உதவி']").first
        support_btn.click()
        page.wait_for_timeout(600)
        support_modal = page.locator("h3:has-text('Platform Guide'), h3:has-text('வழிகாட்டி')").first
        record("Interactive-Help", "Headphones support button opens Help & Support modal", support_modal.is_visible())
        page.screenshot(path=f"{OUTPUT_DIR}/11_help_support_modal.png")
        # Close help modal
        page.locator("button[aria-label='Close modal']").first.click()
        page.wait_for_timeout(400)

        # 3. Language Switcher Interaction: English -> Tamil
        lang_btn = page.locator("button:has-text('தமிழ்'), button:has-text('English')").first
        curr_text = lang_btn.inner_text().strip()
        lang_btn.click()
        page.wait_for_timeout(800)
        new_lang_btn = page.locator("button:has-text('தமிழ்'), button:has-text('English')").first
        new_text = new_lang_btn.inner_text().strip()
        record("Interactive-I18n", "Language toggle successfully alternates between English and Tamil", curr_text != new_text, f"Toggled: {curr_text} -> {new_text}")
        page.screenshot(path=f"{OUTPUT_DIR}/12_language_toggled_tamil.png")

        # Capture Tamil Horoscope Results in full glory
        page.goto(f"http://localhost:3000/horoscope/results?id={AUTHORITATIVE_HORO_ID}", wait_until="domcontentloaded")
        try:
            page.wait_for_selector("h1:has-text('ஜாதக விவரங்கள்')", timeout=10000)
        except Exception:
            page.wait_for_timeout(2000)
        page.screenshot(path=f"{OUTPUT_DIR}/13_tamil_horoscope_3charts.png", full_page=True)

        # 4. User Profile Dropdown & Logout presence
        avatar_btn = page.locator("button:has-text('G')").first
        avatar_btn.click()
        page.wait_for_timeout(500)
        logout_option = page.locator("button:has-text('Log Out'), button:has-text('வெளியேறு')").first
        record("Interactive-Auth", "User profile dropdown displays Log Out action", logout_option.is_visible())
        page.screenshot(path=f"{OUTPUT_DIR}/14_user_profile_dropdown.png")

        # ----------------------------------------------------------------------
        # PHASE 5: Tamil Typography & Accessibility Verification
        # ----------------------------------------------------------------------
        print("\n--- PHASE 5: Tamil Typography & Accessibility ---")
        page.goto(f"http://localhost:3000/horoscope/results?id={AUTHORITATIVE_HORO_ID}", wait_until="domcontentloaded")
        try:
            page.wait_for_selector("h1:has-text('Horoscope Details'), h1:has-text('ஜாதக விவரங்கள்')", timeout=12000)
        except Exception:
            page.wait_for_timeout(2000)

        is_tamil = page.locator("h1:has-text('ஜாதக விவரங்கள்')").first.is_visible()
        if not is_tamil:
            lang_btn = page.locator("button:has-text('தமிழ்')").first
            if lang_btn.is_visible():
                lang_btn.click()
                page.wait_for_timeout(1000)

        tamil_render_check = page.evaluate("""
            () => {
                const sampleTexts = [
                    "ஜாதக விவரங்கள்",
                    "ஜோதிடக் கருவிகள்",
                    "பாவக சக்கரம்",
                    "அஷ்டகவர்க பலன்கள்",
                    "ராசி (D1)",
                    "நவாம்சம் (D9)"
                ];
                const bodyText = document.body.innerText;
                const hasTofu = bodyText.includes("\uFFFD") || bodyText.includes("□");
                return {
                    hasTofu,
                    sampleFound: sampleTexts.filter(t => bodyText.includes(t))
                };
            }
        """)
        record("Typography", "Tamil glyph rendering without replacement character or tofu boxes", not tamil_render_check["hasTofu"] and len(tamil_render_check["sampleFound"]) >= 3, f"Found {len(tamil_render_check['sampleFound'])} sample terms: {', '.join(tamil_render_check['sampleFound'])}")

        browser.close()

    # --------------------------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("  AUDIT EXECUTION SUMMARY")
    print("=" * 80)
    total_tests = len(audit_log)
    passed_tests = sum(1 for t in audit_log if t["status"] == "PASS")
    failed_tests = total_tests - passed_tests

    print(f"Total Checks: {total_tests}")
    print(f"Passed:       {passed_tests}")
    print(f"Failed:       {failed_tests}")

    if console_errors:
        print(f"\nConsole Errors Logged ({len(console_errors)}):")
        for err in console_errors[:10]:
            print(f"  - {err}")
    else:
        print("\nConsole Errors: ZERO console errors detected during full audit.")

    if network_failures:
        print(f"\nNetwork Failures (HTTP 4xx/5xx) ({len(network_failures)}):")
        for f in network_failures[:10]:
            print(f"  - {f}")
    else:
        print("Network Requests: All application network requests returned successful 2xx/3xx.")

    print(f"\nScreenshots saved to: {os.path.abspath(OUTPUT_DIR)}/")

    # Save structured audit results JSON
    with open(os.path.join(OUTPUT_DIR, "audit_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "console_errors": console_errors,
            "network_failures": network_failures,
            "tests": audit_log
        }, f, indent=2, ensure_ascii=False)

    return failed_tests == 0

if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
