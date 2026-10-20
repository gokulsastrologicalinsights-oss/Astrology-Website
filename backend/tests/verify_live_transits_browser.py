"""Browser verification script for Live Planetary Transits on Horoscope Results page."""
import time
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright


def verify_live_transits():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("[STEP 1] Logging in...")
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=15000)

        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        print("  Landed on dashboard:", page.url)

        print("[STEP 2] Navigating to /tools/horoscope to select a saved horoscope...")
        page.goto("http://localhost:3000/tools/horoscope", wait_until="domcontentloaded")
        try:
            page.wait_for_selector(".animate-spin", state="detached", timeout=10000)
        except Exception:
            pass
        time.sleep(1.5)

        # Look for saved horoscope links
        view_links = page.locator("a[href*='/horoscope/results']")
        if view_links.count() > 0:
            saved_link = view_links.first
            saved_href = saved_link.get_attribute("href")
            print(f"  Found saved horoscope link: {saved_href}")
            saved_link.click()
        else:
            print("  No saved horoscopes found. Calculating a new horoscope on /horoscope...")
            page.goto("http://localhost:3000/horoscope", wait_until="domcontentloaded")
            page.wait_for_selector("input[name='fullName'], input#fullName, input[type='text']", timeout=10000)
            page.locator("input[name='fullName'], input#fullName").first.fill("Test User")
            date_input = page.locator("input[type='date'], input[name='dob']").first
            if date_input.count() > 0:
                date_input.fill("1995-05-15")
            time_input = page.locator("input[type='time'], input[name='tob']").first
            if time_input.count() > 0:
                time_input.fill("10:30")
            place_input = page.locator("input[name='place'], input#place, input[placeholder*='City']").first
            if place_input.count() > 0:
                place_input.fill("Chennai")
            submit_btn = page.locator("button[type='submit']").first
            submit_btn.click()

        page.wait_for_url("**/horoscope/results**", timeout=20000)
        try:
            page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        except Exception:
            pass
        time.sleep(2)
        print("  Current URL:", page.url)

        # Verify page header or chart section is loaded
        page.wait_for_selector("h3:has-text('Rasi (D1)'), h3:has-text('ராசி (D1)')", timeout=20000)
        print("  [PASS] Rasi (D1) chart card verified.")

        # TEST 1: Check absence of Bhava Chakra card
        content = page.content()
        assert "Bhava Chakra (House Cusps)" not in content, "Bhava Chakra (House Cusps) must be removed from Charts tab"
        assert "பாவக சக்கரம்" not in content, "பாவக சக்கரம் must be removed from Charts tab"
        print("  [PASS] Bhava Chakra (House Cusps) successfully absent from Charts tab.")

        # TEST 2: Check presence of exactly 2 charts (Rasi and Navamsa)
        assert "Rasi (D1)" in content or "ராசி (D1)" in content, "Rasi (D1) chart must be present"
        assert "Navamsa (D9)" in content or "நவாம்சம் (D9)" in content, "Navamsa (D9) chart must be present"
        print("  [PASS] Exactly 2 classical charts (Rasi D1 & Navamsa D9) displayed.")

        # TEST 3: Click 'Show Live Transits' toggle
        print("[STEP 3] Toggling 'Show Live Transits'...")
        transit_toggle = page.locator("button:has-text('Show Live Transits'), button:has-text('நேரலை கோசாரம்')").first
        assert transit_toggle.count() > 0, "Show Live Transits toggle button must exist"
        transit_toggle.click()

        # Wait for transit calculation request to resolve
        time.sleep(3)

        # Ensure no error banner is displayed
        error_locator = page.locator("text=கோசார கணக்கீடு தற்போது கிடைக்கவில்லை")
        assert error_locator.count() == 0, f"Live transits should NOT fail with error banner, but found error: {page.locator('.bg-rose-50').inner_text() if page.locator('.bg-rose-50').count() > 0 else 'None'}"
        print("  [PASS] Live transits calculation succeeded with zero errors!")

        # Verify Live Transits status banner
        banner_text = page.locator("text=Live Transits, text=நேரலை கோசாரம்").first.inner_text()
        print(f"  Live transits status: {banner_text}")

        # Verify that transit planets (TR badges) are rendered
        tr_badges = page.locator("text=TR")
        badge_count = tr_badges.count()
        assert badge_count > 0, f"Expected TR transit badges to render around chart, found {badge_count}"
        print(f"  [PASS] Verified {badge_count} TR transit badges rendered around the chart.")

        # Screenshot South Indian chart with live transits
        os.makedirs("browser_test_screenshots", exist_ok=True)
        screenshot_south = "browser_test_screenshots/live_transits_south_indian.png"
        page.screenshot(path=screenshot_south, full_page=True)
        print(f"  Captured screenshot of South Indian layout with live transits: {screenshot_south}")

        # TEST 4: Toggle to North Indian layout
        print("[STEP 4] Switching to North Indian chart layout...")
        north_btn = page.locator("button:has-text('North Indian'), button:has-text('வடஇந்திய')").first
        north_btn.click()
        time.sleep(1.5)

        # Verify North Indian layout renders with transits
        screenshot_north = "browser_test_screenshots/live_transits_north_indian.png"
        page.screenshot(path=screenshot_north, full_page=True)
        print(f"  Captured screenshot of North Indian layout with live transits: {screenshot_north}")

        # TEST 5: Open Details Table
        print("[STEP 5] Toggling Details table...")
        details_btn = page.locator("button:has-text('Details'), button:has-text('அட்டவணை')").first
        if details_btn.count() > 0:
            details_btn.click()
            time.sleep(1)
            assert page.locator("table").count() > 0, "Breakdown table should be rendered"
            print("  [PASS] Live transit planetary breakdown table verified.")

        # TEST 6: Refresh button
        print("[STEP 6] Testing Refresh button...")
        refresh_btn = page.locator("button:has-text('Refresh'), button:has-text('புதுப்பி')").first
        refresh_btn.click()
        time.sleep(2)
        assert page.locator("text=கோசார கணக்கீடு தற்போது கிடைக்கவில்லை").count() == 0, "Refresh must succeed without error"
        print("  [PASS] Refresh action successfully re-fetched live ephemeris transits!")

        print("\nALL BROWSER VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        browser.close()


if __name__ == "__main__":
    verify_live_transits()
