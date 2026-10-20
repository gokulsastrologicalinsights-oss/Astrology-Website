"""Browser verification of Tools/Horoscope (/tools/horoscope) cleanup."""
import time
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright


def verify_tools_horoscope():
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

        print("[STEP 2] Navigating to /tools/horoscope...")
        page.goto("http://localhost:3000/tools/horoscope", wait_until="domcontentloaded")
        page.wait_for_selector("h1:has-text('My Horoscopes'), h1:has-text('எனது ஜாதகங்கள்')", timeout=10000)
        print("  Landed on /tools/horoscope.")

        # Wait for loading spinner to complete
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1) # Allow DOM settlement

        # Ensure directory for screenshots exists
        os.makedirs("browser_audit_screenshots", exist_ok=True)
        screenshot_path = "browser_audit_screenshots/cleaned_tools_horoscope.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  Captured full-page screenshot at: {screenshot_path}")

        # TEST 1: Check Page Title
        h1_text = page.locator("h1").first.inner_text()
        assert "My Horoscopes" in h1_text or "எனது ஜாதகங்கள்" in h1_text, f"Page title must be 'My Horoscopes', got: {h1_text}"
        print("  [PASS] Page title 'My Horoscopes' verified.")

        # TEST 2: Check Primary + Create New Horoscope Button at Top
        top_create_btn = page.locator("a[href='/horoscope']:has-text('Create New Horoscope'), a[href='/horoscope']:has-text('புதிய ஜாதகம்')").first
        assert top_create_btn.count() >= 1, "Primary '+ Create New Horoscope' button must be present at top"
        print("  [PASS] Top Primary '+ Create New Horoscope' button verified.")

        # TEST 3: Check Absence of Unwanted Elements
        content = page.content()

        # Tabs
        assert "Feature Directory" not in content, "Feature Directory tab must not exist"
        # Tool Cards
        assert "KP Astrology System" not in content, "KP Astrology System card must not exist"
        assert "Vimshottari Dasa Timeline" not in content, "Vimshottari Dasa Timeline card must not exist"
        assert "Horoscope Planetary Analysis" not in content, "Horoscope Planetary Analysis card must not exist"
        assert "Panchang & Additional Tools" not in content, "Panchang & Additional Tools card must not exist"
        # Promotional Banners
        assert "Calculation Integrity:" not in content, "Calculation Integrity banner must not exist"
        assert "Premium Access Active" not in content, "Premium Access promotional banner must not exist"
        print("  [PASS] All unwanted cards, tabs, and promotional banners are absent.")

        # TEST 4: Check Saved Horoscopes List or Empty State
        cards = page.locator("[data-testid='saved-horoscope-card']").all()
        empty_state = page.locator("text='No saved horoscopes yet.'").count() + page.locator("text='சேமிக்கப்பட்ட ஜாதகங்கள் எதுவும் இல்லை'").count()

        if len(cards) > 0:
            print(f"  Found {len(cards)} saved horoscope records.")
            first_card = cards[0]
            card_text = first_card.inner_text()
            print("  First Card Preview:\n ", card_text.replace("\n", " | "))

            # Check View action
            view_btn = first_card.locator("a:has-text('View'), a:has-text('காண்க')")
            assert view_btn.count() >= 1, "Card must have View/Open action"
            assert "/horoscope/results?id=" in view_btn.get_attribute("href"), "View action must link to results page"

            # Check Edit action
            edit_btn = first_card.locator("button[title*='Edit'], button[title*='திருத்து'], button[aria-label*='Edit']")
            assert edit_btn.count() >= 1, "Card must have Edit action"

            # Check Serial number
            serial_badge = first_card.locator(".font-mono")
            assert serial_badge.count() >= 1, "Card must display serial number"

            # Check Name
            name_el = first_card.locator("h3")
            assert name_el.count() >= 1 and len(name_el.inner_text().strip()) > 0, "Card must display name"

            print("  [PASS] Record contains Serial Number, Name, View/Open, and Edit actions.")
        elif empty_state > 0:
            print("  [PASS] Empty state 'No saved horoscopes yet.' verified.")
            empty_create = page.locator(".rounded-2xl a[href='/horoscope']")
            assert empty_create.count() >= 1, "Empty state must have Create New Horoscope button"
            print("  [PASS] Empty state contains Create New Horoscope button.")
        else:
            raise AssertionError("Neither horoscope cards nor valid empty state was found!")

        browser.close()
        print("\n[SUCCESS] Browser verification for /tools/horoscope passed completely!")

if __name__ == "__main__":
    verify_tools_horoscope()
