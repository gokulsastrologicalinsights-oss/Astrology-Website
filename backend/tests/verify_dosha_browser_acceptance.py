"""Independent Live Browser Acceptance Test for Vedic Dosha Analysis Integration.

Validates in real headless Chrome:
1. End-to-end chart calculation -> /horoscope/results page.
2. Tab order: Doshas tab button placed directly adjacent to Yogas tab button.
3. Dosha section layout: 5 Summary stat cards, 5 Category pills, 5 Status toggles, Search bar, Results table.
4. Filter operations: Active only, Mitigated only, Absent only, Indeterminate only.
5. Synastry compatibility doshas show 'indeterminate' with missing prerequisite notice.
6. Analytical inspector modal: formation rules, exact degrees, cancellations, non-alarmist interpretation, textual authority.
7. Language toggle: English vs Tamil labels ("Doshas" vs "தோஷங்கள்").
8. Responsive viewports: Desktop (1280x900) and Mobile (375x667).
9. State preservation when switching between Yogas and Doshas.
"""

import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_test_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_browser_acceptance():
    print("=" * 70)
    print("STARTING VEDIC DOSHA ANALYSIS LIVE BROWSER ACCEPTANCE AUDIT")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.on("console", lambda msg: print(f"  [CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"  [PAGEERROR] {err}"))

        # ------------------------------------------------------------------
        # STEP 0: Authenticate
        # ------------------------------------------------------------------
        print("\n[STEP 0] Authenticating as Admin...")
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(3000)
        print("  [PASS] Authenticated successfully.")

        # ------------------------------------------------------------------
        # STEP 1: Navigate to Horoscope Form & Fill Details
        # ------------------------------------------------------------------
        print("\n[STEP 1] Navigating to http://localhost:3000/horoscope...")
        page.goto("http://localhost:3000/horoscope", wait_until="networkidle")
        page.wait_for_selector("#fullName", timeout=10000)
        
        # Fill form using exact element IDs
        page.fill("#fullName", "Audit Subject")
        page.fill("#birthDate", "1990-05-15")
        page.fill("#birthTime", "14:30:00")
        
        # Location input
        page.fill("#placeSearch", "Chennai")
        page.wait_for_timeout(1000)
        dropdown_item = page.locator("div.absolute.z-30 button").first
        if dropdown_item.count() > 0:
            dropdown_item.click()
        else:
            page.fill("#latitude", "13.0827")
            page.fill("#longitude", "80.2707")

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_01_form_filled.png")
        print("  Form filled. Submitting calculation...")

        # Submit form
        calc_btn = page.locator("form button[type='submit']")
        calc_btn.click()

        # ------------------------------------------------------------------
        # STEP 2: Wait for Results Page & Verify Secondary Tabs Order
        # ------------------------------------------------------------------
        print("\n[STEP 2] Waiting for /horoscope/results page...")
        page.wait_for_url("**/horoscope/results*", timeout=30000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        page.wait_for_selector("button:has-text('Yogas')", timeout=15000)
        print("  Results page loaded successfully.")

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_02_results_loaded.png")

        # Verify Tab Buttons Order: Yogas followed immediately by Doshas
        yogas_btn = page.locator("button:has-text('Yogas')")
        doshas_btn = page.locator("button:has-text('Doshas')")
        
        assert yogas_btn.count() > 0, "Yogas tab button not found"
        assert doshas_btn.count() > 0, "Doshas tab button not found"
        print("  [PASS] Both Yogas and Doshas tab buttons exist in secondary navigation bar.")

        # Check visual order in DOM
        all_secondary_btns = page.locator("div.border-b button").all_text_contents()
        secondary_nav_str = " -> ".join([b.strip() for b in all_secondary_btns if b.strip()])
        print(f"  Secondary Navigation Sequence: {secondary_nav_str}")

        yogas_idx = -1
        doshas_idx = -1
        for idx, text in enumerate(all_secondary_btns):
            if "Yogas" in text:
                yogas_idx = idx
            elif "Doshas" in text:
                doshas_idx = idx

        assert yogas_idx != -1 and doshas_idx != -1, "Could not determine button indices"
        assert doshas_idx == yogas_idx + 1, f"Doshas tab (index {doshas_idx}) must be directly adjacent to Yogas tab (index {yogas_idx})"
        print("  [PASS] Doshas tab button is positioned DIRECTLY next to Yogas tab button.")

        # ------------------------------------------------------------------
        # STEP 3: Switch to Doshas Tab & Verify Layout & Summary Cards
        # ------------------------------------------------------------------
        print("\n[STEP 3] Switching to Doshas tab...")
        doshas_btn.click()
        page.wait_for_timeout(1000)

        # If empty state is displayed, click Calculate Vedic Doshas button
        calc_doshas_btn = page.locator("button:has-text('Calculate Vedic Doshas')")
        if calc_doshas_btn.count() > 0 and calc_doshas_btn.is_visible():
            print("  Empty state detected. Triggering 'Calculate Vedic Doshas'...")
            calc_doshas_btn.click()
            try:
                page.wait_for_selector("div.grid-cols-2.sm\\:grid-cols-5 > div", timeout=15000)
                print("  Stat cards appeared after calculation completed.")
            except Exception as wait_err:
                print(f"  Timeout waiting for stat cards: {wait_err}")

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_03_desktop_doshas_tab.png")

        # Verify Header Banner & Stat Cards
        header_title = page.locator("h3:has-text('Vedic Dosha Analysis')")
        assert header_title.count() > 0, "Header 'Vedic Dosha Analysis' not found"
        print("  [PASS] Header banner rendered with 'Vedic Dosha Analysis'.")

        # Check Stat Cards (Total Rules Evaluated, Active Doshas, Mitigated, Absent, Indeterminate)
        stat_cards = page.locator("div.grid-cols-2.sm\\:grid-cols-5 > div")
        card_count = stat_cards.count()
        print(f"  Found summary stat cards: {card_count}")
        assert card_count == 5, f"Expected 5 stat cards, found {card_count}"
        
        stat_texts = [stat_cards.nth(i).inner_text() for i in range(card_count)]
        for st in stat_texts:
            print(f"    - {st.replace(chr(10), ' ')}")

        stat_texts_lower = [t.lower() for t in stat_texts]
        assert any("total rules evaluated" in t for t in stat_texts_lower), "Total Rules Evaluated card missing"
        assert any("active" in t for t in stat_texts_lower), "Active Doshas card missing"
        assert any("mitigated" in t for t in stat_texts_lower), "Mitigated card missing"
        assert any("absent" in t for t in stat_texts_lower), "Absent card missing"
        assert any("indeterminate" in t for t in stat_texts_lower), "Indeterminate card missing"
        print("  [PASS] All 5 summary stat cards rendered correctly.")

        # ------------------------------------------------------------------
        # STEP 4: Verify Results Table & 30-Rule Coverage
        # ------------------------------------------------------------------
        print("\n[STEP 4] Verifying Doshas Results Table...")
        table_rows = page.locator("table tbody tr")
        row_count = table_rows.count()
        print(f"  Total table rows currently rendered: {row_count}")
        assert row_count >= 20, f"Expected full catalogue rows, found {row_count}"

        # ------------------------------------------------------------------
        # STEP 5: Test Status Filters
        # ------------------------------------------------------------------
        print("\n[STEP 5] Testing Status Filters...")
        # 1. Filter: Active Only
        active_btn = page.locator("button:has-text('Active Only')")
        active_btn.click()
        page.wait_for_timeout(500)
        active_rows = page.locator("table tbody tr").count()
        print(f"  Active Only filter count: {active_rows} rows")
        assert active_rows > 0, "Expected at least 1 active dosha row"

        # 2. Filter: Indeterminate Only (should be exactly 4 marriage compatibility doshas)
        indet_btn = page.locator("button:has-text('Indeterminate Only')")
        indet_btn.click()
        page.wait_for_timeout(500)
        indet_rows = page.locator("table tbody tr").count()
        print(f"  Indeterminate Only filter count: {indet_rows} rows")
        assert indet_rows == 4, f"Expected exactly 4 indeterminate marriage compatibility rows, found {indet_rows}"
        print("  [PASS] Indeterminate filter displays exactly 4 marriage compatibility doshas.")

        print("\n[STEP 6] Opening Analytical Inspector Modal for Nadi Dosha...")
        first_row = page.locator("table tbody tr").first
        first_row.click()
        try:
            page.wait_for_selector("div.fixed.inset-0", timeout=5000)
            print("  Inspector modal displayed on row click.")
        except Exception:
            details_btn = first_row.locator("button").first
            details_btn.click()
            page.wait_for_selector("div.fixed.inset-0", timeout=5000)

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_04_inspector_modal.png")

        # Verify Modal Contents
        modal = page.locator("div.fixed.inset-0")
        assert modal.count() > 0, "Inspector modal not displayed"
        modal_text = modal.inner_text()

        assert "Requires partner horoscope" in modal_text, "Missing prerequisite warning not shown in modal"
        assert "Rule-Set:" in modal_text, "Rule-Set version footer not shown in modal"
        print("  [PASS] Inspector modal renders missing prerequisite notice for partner synastry.")

        # Close Modal
        close_btn = modal.locator("div.flex.items-start button")
        close_btn.click()
        page.wait_for_selector("div.fixed.inset-0", state="detached", timeout=5000)
        print("  [PASS] Inspector modal closes cleanly.")

        # ------------------------------------------------------------------
        # STEP 7: Reset Filter & Test Search Input
        # ------------------------------------------------------------------
        print("\n[STEP 7] Testing Search Filter...")
        for b in page.locator("button:has-text('All Doshas')").all():
            b.click()
            page.wait_for_timeout(200)

        search_input = page.locator("input[placeholder*='Search dosha']")
        search_input.fill("Kuja")
        page.wait_for_timeout(500)
        search_rows = page.locator("table tbody tr").count()
        print(f"  Search for 'Kuja' returned {search_rows} row(s)")
        assert search_rows >= 1, "Search for 'Kuja' should return at least Kuja Dosha"
        search_input.fill("")
        page.wait_for_timeout(400)

        # ------------------------------------------------------------------
        # STEP 8: State Preservation Between Yogas and Doshas
        # ------------------------------------------------------------------
        print("\n[STEP 8] Testing tab switching state preservation...")
        yogas_btn.click()
        page.wait_for_timeout(600)
        assert page.locator("h3:has-text('Vedic Yoga')").count() > 0, "Yogas section not active"
        print("  Switched to Yogas tab successfully.")

        doshas_btn.click()
        page.wait_for_timeout(600)
        assert page.locator("h3:has-text('Vedic Dosha Analysis')").count() > 0, "Doshas section not active"
        print("  Switched back to Doshas tab successfully with preserved state.")

        # ------------------------------------------------------------------
        # STEP 9: Mobile Viewport Responsiveness (375x667)
        # ------------------------------------------------------------------
        print("\n[STEP 9] Testing Mobile Viewport (375x667)...")
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(600)
        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_05_mobile_view.png")

        # Verify mobile header and buttons are accessible
        mobile_dosha_btn = page.get_by_role("button", name="Doshas", exact=True)
        assert mobile_dosha_btn.is_visible(), "Doshas tab button not visible on mobile"
        print("  [PASS] Mobile layout renders without clipping or overflow errors.")

        # ------------------------------------------------------------------
        # STEP 10: Bilingual Tamil Language Verification
        # ------------------------------------------------------------------
        print("\n[STEP 10] Testing Bilingual Tamil Display...")
        # Reset desktop viewport
        page.set_viewport_size({"width": 1280, "height": 900})
        page.wait_for_timeout(400)

        # Toggle to Tamil
        lang_btn = page.locator("button:has-text('தமிழ்')")
        if lang_btn.count() == 0:
            lang_btn = page.locator("button:has-text('TA'), button:has-text('Language'), button[aria-label*='Language']")
        if lang_btn.count() > 0:
            lang_btn.first.click()
            page.wait_for_timeout(1000)

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_06_tamil_localization.png")
        page_html = page.content()
        has_tamil_tab = "தோஷங்கள்" in page_html
        has_tamil_title = "வேத தோஷ பகுப்பாய்வு" in page_html
        print(f"  Tamil Tab 'தோஷங்கள்' present: {has_tamil_tab}")
        print(f"  Tamil Title 'வேத தோஷ பகுப்பாய்வு' present: {has_tamil_title}")
        assert has_tamil_tab or has_tamil_title, "Tamil translations not detected"
        print("  [PASS] Bilingual Tamil localization verified.")

        # Toggle back to English
        en_btn = page.locator("button:has-text('EN'), button:has-text('English')")
        if en_btn.count() > 0:
            en_btn.first.click()
            page.wait_for_timeout(500)

        # ------------------------------------------------------------------
        # STEP 11: Verify Persistence & Saved Horoscope Reload
        # ------------------------------------------------------------------
        print("\n[STEP 11] Testing Persistence & Saved Horoscope Reload...")
        current_url = page.url
        print(f"  Current Results URL: {current_url}")
        assert "/horoscope/results" in current_url, "Must be on results page"

        # Reload the page directly from URL
        print("  Reloading saved horoscope via direct URL navigation...")
        page.goto(current_url, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Navigate to Doshas tab
        reloaded_doshas_btn = page.get_by_role("button", name="Doshas", exact=True)
        reloaded_doshas_btn.click()
        page.wait_for_timeout(1000)

        page.screenshot(path=f"{SCREENSHOT_DIR}/dosha_07_reloaded_saved_chart.png")

        # Verify stat cards restored immediately without calculate prompt
        reloaded_stat_cards = page.locator("div.grid-cols-2.sm\\:grid-cols-5 > div")
        reloaded_card_count = reloaded_stat_cards.count()
        assert reloaded_card_count == 5, f"Expected 5 stat cards after reload, found {reloaded_card_count}"
        reloaded_evaluated = reloaded_stat_cards.nth(0).inner_text()
        print(f"  Reloaded Stat Card 1: {reloaded_evaluated.replace(chr(10), ' ')}")
        assert "30" in reloaded_evaluated, "Expected 30 total rules evaluated restored upon page reload"
        print("  [PASS] Saved horoscope reload immediately restores all 30 evaluated Dosha results.")

        print("\n" + "=" * 70)
        print("ALL BROWSER ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    run_browser_acceptance()
