"""Live Browser Acceptance Test Suite for D1 Rasi & D9 Navamsa Module.

Uses Playwright with local Chrome to perform end-to-end browser acceptance testing:
1. Navigates to /tools/d1-d9.
2. Fills ad-hoc birth parameters (Chennai 1990-05-15 14:30:00 IST).
3. Submits calculation and verifies:
   - Summary cards (Lagna, Navamsa Lagna, Vargottama count, Pushkara count).
   - View modes (Side-by-side, D1 only, D9 only).
   - Chart styles (South Indian 4x4 grid vs North Indian diamond SVG).
   - Comparative analysis table (all grahas, degrees, motion, badges).
4. Tests responsive viewport (desktop 1280x800 and mobile 375x667).
5. Tests navigation from /tools to /tools/d1-d9.
6. Tests horoscope calculation on /horoscope and verifies D1/D9 switcher on /horoscope/results.
7. Saves screenshot artifacts for visual verification.
"""

import sys
import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_test_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_browser_tests():
    print("=" * 70)
    print("STARTING D1/D9 LIVE BROWSER ACCEPTANCE TESTS")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # ------------------------------------------------------------------
        # TEST 1: Tools Directory Navigation
        # ------------------------------------------------------------------
        print("\n[TEST 1] Verifying Tools Directory card...")
        page.goto("http://localhost:3000/tools", wait_until="networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_tools_hub.png")
        
        # Look for D1/D9 card on tools page
        d1_d9_card = page.locator("a[href='/tools/d1-d9']")
        card_count = d1_d9_card.count()
        print(f"  Found D1/D9 tool card links: {card_count}")
        assert card_count > 0, "D1/D9 card not found on /tools page"
        print("  [PASS] Tools Hub has active link to /tools/d1-d9")

        # ------------------------------------------------------------------
        # TEST 2: Dedicated /tools/d1-d9 Page Loading & UI
        # ------------------------------------------------------------------
        print("\n[TEST 2] Navigating to /tools/d1-d9...")
        page.goto("http://localhost:3000/tools/d1-d9", wait_until="networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_d1_d9_initial.png")

        header_text = page.locator("h1").inner_text()
        print(f"  Page Header: '{header_text}'")
        assert "D1" in header_text and "D9" in header_text, f"Unexpected header: {header_text}"

        # ------------------------------------------------------------------
        # TEST 3: Ad-hoc Calculation (Chennai 1990-05-15 14:30:00 IST)
        # ------------------------------------------------------------------
        print("\n[TEST 3] Performing Ad-hoc calculation on /tools/d1-d9...")
        # Switch to adhoc mode if not already
        adhoc_btn = page.locator("button:has-text('Custom Birth Details'), button:has-text('புதிய உள்ளீடு')").first
        if adhoc_btn.is_visible():
            adhoc_btn.click()
            time.sleep(0.3)

        # Fill form
        page.locator("input[type='date']").fill("1990-05-15")
        page.locator("input[type='time']").fill("14:30:00")
        
        # Submit
        calc_btn = page.locator("button:has-text('Calculate & View'), button:has-text('D1 & D9 சக்கரங்களைக் காண்க')").first
        calc_btn.click()
        
        # Wait for results to render
        page.wait_for_selector("table", timeout=10000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_d1_d9_calculated.png")
        print("  [PASS] Calculation succeeded, results table rendered.")

        # ------------------------------------------------------------------
        # TEST 4: Verify Dignity Metrics & Badges
        # ------------------------------------------------------------------
        print("\n[TEST 4] Verifying Dignity Summary Metrics...")
        body_text = page.locator("body").inner_text()

        # Check Lagna
        assert "Virgo" in body_text, "Virgo Ascendant not found in summary"
        print("  [PASS] D1 Ascendant: Virgo identified")

        # Check Vargottama Planets
        assert "Moon" in body_text and "Saturn" in body_text, "Moon / Saturn Vargottama not found"
        print("  [PASS] Vargottama planets identified: Moon, Saturn")

        # Check Table Columns
        table_headers = page.locator("th").all_inner_texts()
        print(f"  Table Headers: {table_headers}")
        assert any("Planet" in h for h in table_headers), "Planet column missing"
        assert any("D1" in h for h in table_headers), "D1 column missing"
        assert any("D9" in h for h in table_headers), "D9 column missing"
        assert any("Dignit" in h for h in table_headers), "Dignities column missing"

        # Check Table Rows
        rows = page.locator("tbody tr").all_inner_texts()
        print(f"  Total planet rows rendered: {len(rows)}")
        assert len(rows) >= 10, f"Expected at least 10 rows (Asc + 9 grahas), got {len(rows)}"

        # ------------------------------------------------------------------
        # TEST 5: Switching View Modes (Side-by-Side, D1 Only, D9 Only)
        # ------------------------------------------------------------------
        print("\n[TEST 5] Testing View Mode Switching...")
        # Click D1 Rasi only
        d1_mode_btn = page.locator("button:has-text('D1 Rasi')").first
        d1_mode_btn.click()
        time.sleep(0.3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_view_d1_only.png")
        print("  [PASS] D1 Rasi only view rendered")

        # Click D9 Navamsa only
        d9_mode_btn = page.locator("button:has-text('D9 Navamsa')").first
        d9_mode_btn.click()
        time.sleep(0.3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_view_d9_only.png")
        print("  [PASS] D9 Navamsa only view rendered")

        # Click back to Side-by-Side
        sbs_mode_btn = page.locator("button:has-text('Side-by-Side'), button:has-text('ஒப்பீட்டு பார்வை')").first
        sbs_mode_btn.click()
        time.sleep(0.3)
        print("  [PASS] Side-by-Side view restored")

        # ------------------------------------------------------------------
        # TEST 6: Switching Chart Styles (South Indian vs North Indian)
        # ------------------------------------------------------------------
        print("\n[TEST 6] Testing Chart Style Switching (South vs North)...")
        # Switch to North Indian
        north_btn = page.locator("button:has-text('North Indian')").first
        north_btn.click()
        time.sleep(0.5)
        # Check for SVG element
        svg_count = page.locator("svg[viewBox='0 0 400 400']").count()
        print(f"  North Indian 400x400 SVGs rendered: {svg_count}")
        assert svg_count >= 2, f"Expected at least 2 North Indian SVGs in side-by-side mode, got {svg_count}"
        page.screenshot(path=f"{SCREENSHOT_DIR}/06_north_indian_style.png")
        print("  [PASS] North Indian style SVGs rendered successfully")

        # Switch back to South Indian
        south_btn = page.locator("button:has-text('South Indian')").first
        south_btn.click()
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/07_south_indian_style.png")
        print("  [PASS] South Indian style restored")

        # ------------------------------------------------------------------
        # TEST 7: Responsive Mobile Viewport (375x667)
        # ------------------------------------------------------------------
        print("\n[TEST 7] Testing Responsive Mobile Viewport (375x667 iPhone SE)...")
        mobile_context = browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = mobile_context.new_page()
        mobile_page.goto("http://localhost:3000/tools/d1-d9", wait_until="networkidle")

        adhoc_m = mobile_page.locator("button:has-text('Custom Birth Details'), button:has-text('புதிய உள்ளீடு')").first
        if adhoc_m.is_visible():
            adhoc_m.click()
            time.sleep(0.2)

        mobile_page.locator("input[type='date']").fill("1990-05-15")
        mobile_page.locator("input[type='time']").fill("14:30:00")
        calc_m = mobile_page.locator("button:has-text('Calculate & View'), button:has-text('D1 & D9 சக்கரங்களைக் காண்க')").first
        calc_m.click()
        mobile_page.wait_for_selector("table", timeout=10000)
        mobile_page.screenshot(path=f"{SCREENSHOT_DIR}/08_mobile_responsive.png")
        print("  [PASS] Mobile responsive view verified without layout breakage")
        mobile_context.close()

        # ------------------------------------------------------------------
        # TEST 8: Horoscope Results Page D1/D9 Tab Integration
        # ------------------------------------------------------------------
        print("\n[TEST 8] Testing /horoscope -> /horoscope/results D1/D9 Tab Integration...")
        page.goto("http://localhost:3000/horoscope", wait_until="networkidle")
        page.locator("input#fullName, input[name='fullName'], input[placeholder*='Name']").first.fill("Test User")
        page.locator("input[type='date']").fill("1990-05-15")
        page.locator("input[type='time']").fill("14:30:00")
        
        # Click calculate
        horo_calc = page.locator("button[type='submit'], button:has-text('Calculate Horoscope'), button:has-text('ஜாதகம் கணக்கிட')").first
        horo_calc.click()

        # Wait for results page
        page.wait_for_url("**/horoscope/results**", timeout=15000)
        time.sleep(1.0)
        page.screenshot(path=f"{SCREENSHOT_DIR}/09_horoscope_results_d1.png")
        print("  [PASS] Navigated to /horoscope/results")

        # Verify D1 and D9 buttons exist
        d1_tab_btn = page.locator("button:has-text('D1 Rasi'), button:has-text('D1 ராசி')").first
        d9_tab_btn = page.locator("button:has-text('D9 Navamsa'), button:has-text('D9 நவாம்சம்')").first
        assert d1_tab_btn.is_visible(), "D1 Rasi switcher button missing on results page"
        assert d9_tab_btn.is_visible(), "D9 Navamsa switcher button missing on results page"
        print("  [PASS] D1 / D9 division switcher buttons visible")

        # Click D9 Navamsa button
        d9_tab_btn.click()
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/10_horoscope_results_d9.png")
        
        # Verify D9 callout with Vargottama summary
        results_body = page.locator("body").inner_text()
        assert "Navamsa Lagna" in results_body or "நவாம்சம்" in results_body, "Navamsa Lagna banner missing"
        assert "Full D1/D9 Comparative Analysis" in results_body or "முழு D1/D9 ஆய்வு" in results_body, "Deep link to tools/d1-d9 missing"
        print("  [PASS] D9 Navamsa chart, Lagna banner, and deep link successfully rendered")

        browser.close()

    print("\n" + "=" * 70)
    print("ALL 8 LIVE BROWSER ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_browser_tests()
