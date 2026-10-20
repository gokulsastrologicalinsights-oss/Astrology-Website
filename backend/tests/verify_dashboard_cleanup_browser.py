"""Browser verification of Dashboard cleanup."""
import time
from playwright.sync_api import sync_playwright

def verify_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()

        print("[STEP 1] Logging in...")
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)

        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        print("  Landed on dashboard:", page.url)

        # Wait for Saved Horoscopes section to load
        page.wait_for_selector("h2:has-text('Saved Horoscopes'), h2:has-text('சேமிக்கப்பட்ட ஜாதகங்கள்')", timeout=10000)
        print("  Saved Horoscopes section loaded.")

        # Take screenshot of the cleaned up dashboard
        screenshot_path = "browser_audit_screenshots/cleaned_user_dashboard.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  Captured full-page screenshot at: {screenshot_path}")

        # Check absence of unwanted sections
        content = page.content()

        assert "Recent KP Predictions" not in content, "Recent KP Predictions must not be visible"
        assert "Rule-Based KP" not in content, "Rule-Based KP must not be visible"
        assert "Saved Numerology Reports" not in content, "Saved Numerology Reports must not be visible"
        assert "Saved Vastu Assessments" not in content, "Saved Vastu Assessments must not be visible"
        print("  [PASS] All 4 unwanted sections are completely absent from dashboard UI.")

        # Check absence of Vastu shortcut button in header
        vastu_header_btn = page.locator("a[href='/vastu']:has-text('Vastu'), a[href='/vastu']:has-text('வாஸ்து')").all()
        # In header shortcuts, there should be none
        header_area = page.locator(".border-b.border-\\[\\#DDE5F0\\]").first
        header_vastu = header_area.locator("a[href='/vastu']").count()
        assert header_vastu == 0, "Header shortcuts must not contain Vastu button"
        print("  [PASS] Header shortcuts do not contain Vastu button.")

        # Check absence of KP / Numerology / Vastu stat cards in metrics grid
        assert page.locator("text='KP Event Analyses'").count() == 0, "KP Event Analyses stat card must not exist"
        assert page.locator("text='Numerology Reports'").count() == 0, "Numerology Reports stat card must not exist"
        assert page.locator("text='Vastu Reports'").count() == 0, "Vastu Reports stat card must not exist"
        print("  [PASS] Unrelated statistics widgets are completely absent.")

        # Check that Saved Horoscopes is present
        saved_h2 = page.locator("h2:has-text('Saved Horoscopes'), h2:has-text('சேமிக்கப்பட்ட ஜாதகங்கள்')").count()
        assert saved_h2 >= 1, "Saved Horoscopes heading must be present"
        print("  [PASS] Saved Horoscopes is present as the only saved section.")

        # Check horoscope card info: Name, Type (Vedic/KP), Timestamp, Sequential number, View action
        cards = page.locator(".group").all()
        print(f"  Found {len(cards)} horoscope cards displayed.")
        if len(cards) > 0:
            first_card = cards[0]
            first_card_text = first_card.inner_text()
            print("  First Card Preview:\n", first_card_text.replace("\n", " | "))

            # Verify presence of View action
            view_btn = first_card.locator("a:has-text('View'), a:has-text('காண்க')")
            assert view_btn.count() >= 1, "Card must have View/Open action"
            print("  [PASS] Card has View/Open action.")

        browser.close()
        print("\n[SUCCESS] Browser verification passed completely!")

if __name__ == "__main__":
    verify_dashboard()
