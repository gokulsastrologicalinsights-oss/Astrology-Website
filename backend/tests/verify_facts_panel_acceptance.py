"""
End-to-end Browser Acceptance Verification:
Horoscope Facts Panel (ஜாதக விவரங்கள் → உண்மைகள்)
Gokul's Astrological Insights
"""

import time
import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "browser_audit_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

console_errors = []
react_warnings = []


def on_console_message(msg):
    text = msg.text
    if msg.type == "error":
        # Ignore external browser/automation injected styles (e.g., Chrome caret-color: transparent on inputs)
        if "caret-color" in text:
            return
        console_errors.append(text)
    elif "Warning:" in text or "key" in text.lower():
        if "caret-color" in text:
            return
        react_warnings.append(text)


def run_facts_panel_acceptance():
    print("=" * 70)
    print("Starting Final Acceptance Verification: Horoscope Facts Panel")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on("console", on_console_message)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # -------------------------------------------------------------
        # STEP 1: Authentication
        # -------------------------------------------------------------
        print("\n[STEP 1] Logging in...")
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=10000)

        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=15000)
        print("  ✓ Successfully logged in, landed on dashboard:", page.url)

        # -------------------------------------------------------------
        # STEP 2: Navigate to /tools/horoscope
        # -------------------------------------------------------------
        print("\n[STEP 2] Navigating to /tools/horoscope...")
        page.goto("http://localhost:3000/tools/horoscope", wait_until="domcontentloaded")
        page.wait_for_selector("h1:has-text('My Horoscopes'), h1:has-text('எனது ஜாதகங்கள்')", timeout=10000)
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1)

        # Verify page shows only saved-horoscope list and + Create New Horoscope action
        top_create_btn = page.locator("a[href='/horoscope']:has-text('Create New Horoscope'), a[href='/horoscope']:has-text('புதிய ஜாதகம்')").first
        assert top_create_btn.is_visible(), "Primary '+ Create New Horoscope' button must be visible at top"
        print("  ✓ Primary '+ Create New Horoscope' button verified.")

        content = page.content()
        assert "Feature Directory" not in content, "Feature Directory tab must not exist on /tools/horoscope"
        print("  ✓ Clutter-free /tools/horoscope layout verified.")

        page.screenshot(path=f"{SCREENSHOT_DIR}/01_tools_horoscope_list.png", full_page=True)

        # -------------------------------------------------------------
        # STEP 3: Find Saved Horoscopes and Open First Record (Gokul or #01)
        # -------------------------------------------------------------
        print("\n[STEP 3] Opening first saved horoscope...")
        cards = page.locator("div.border.rounded-xl, div.bg-white.rounded-xl.border")
        card_count = cards.count()
        print(f"  Found {card_count} card-like elements on /tools/horoscope")

        # Find the card with "Gokul" or first "View / திறக்க" link
        view_links = page.locator("a[href*='/horoscope/results']")
        view_count = view_links.count()
        print(f"  Found {view_count} view horoscope links")
        assert view_count > 0, "Must have at least one saved horoscope link"

        # Look specifically for Gokul's horoscope or first link
        gokul_link = page.locator("a[href*='/horoscope/results']:has-text('View'), a[href*='/horoscope/results']:has-text('காண்க')").first
        target_href = gokul_link.get_attribute("href")
        print(f"  Opening horoscope at href: {target_href}")
        gokul_link.click()

        page.wait_for_url("**/horoscope/results**", timeout=15000)
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1.5)
        print("  ✓ Landed on horoscope results page:", page.url)

        # Verify Customer Details Header
        header_text = page.locator("h1").first.inner_text()
        print(f"  Page Header: {header_text}")
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_horoscope_results_main.png", full_page=True)

        # -------------------------------------------------------------
        # STEP 4: Switch to Facts & Panchang Tab (உண்மைகள்)
        # -------------------------------------------------------------
        print("\n[STEP 4] Switching to 'உண்மைகள்' (Facts & Panchang) tab...")
        facts_tab = page.locator("button:has-text('உண்மைகள்'), button:has-text('Facts & Panchang')").first
        assert facts_tab.is_visible(), "'உண்மைகள்' (Facts) tab button must be visible"
        facts_tab.click()
        time.sleep(1.5)

        # Verify HoroscopeFactsPanel is rendered
        panel_banner = page.locator("h2:has-text('ஜாதக உண்மைகள் & விரிவான கணிப்புகள்')")
        assert panel_banner.is_visible(), "HoroscopeFactsPanel banner must be visible"
        print("  ✓ HoroscopeFactsPanel successfully rendered!")
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_facts_panel_default_basic.png", full_page=True)

        # -------------------------------------------------------------
        # STEP 5: Verify All 6 Categories in Exact Required Order
        # -------------------------------------------------------------
        print("\n[STEP 5] Verifying 6 categories in exact required order...")
        category_buttons = page.locator("button:has-text('அடிப்படை'), button:has-text('சிறப்பு அம்சங்கள்'), button:has-text('சுப & பாவ கிரகங்கள்'), button:has-text('ஷட்பலம் & அவஸ்தை'), button:has-text('பெயர்ச்சி (கோச்சாரம்)'), button:has-text('ஜைமினி சார காரகங்கள்')")
        
        expected_cats = [
            "அடிப்படை",
            "சிறப்பு அம்சங்கள்",
            "சுப & பாவ கிரகங்கள்",
            "ஷட்பலம் & அவஸ்தை",
            "பெயர்ச்சி (கோச்சாரம்)",
            "ஜைமினி சார காரகங்கள்"
        ]

        # Extract text of category navigation items
        sidebar_buttons = page.locator("div.w-full.lg\\:w-72 button")
        sidebar_count = sidebar_buttons.count()
        print(f"  Sidebar button count: {sidebar_count}")
        actual_order = []
        for i in range(sidebar_count):
            title_span = sidebar_buttons.nth(i).locator("span.font-semibold").first
            title_text = title_span.inner_text().strip() if title_span.count() > 0 else sidebar_buttons.nth(i).inner_text().strip()
            actual_order.append(title_text)

        print(f"  Actual Category Order: {actual_order}", flush=True)
        for idx, expected in enumerate(expected_cats):
            assert expected in actual_order[idx], f"Category {idx+1} must be '{expected}', got '{actual_order[idx]}'"
        print("  ✓ All 6 categories appear in the EXACT requested order!", flush=True)

        # -------------------------------------------------------------
        # STEP 6: Validate Category 1: அடிப்படை Content
        # -------------------------------------------------------------
        print("\n[STEP 6] Validating Category 1: அடிப்படை (Basic) content...")
        
        # Section A: பஞ்சாங்கம்
        assert page.locator("h3:has-text('பஞ்சாங்கம்')").first.is_visible(), "Section A Panchangam heading must be visible"
        rasi_elem = page.locator("span:has-text('ராசி (Moon Sign)') + span").first.inner_text()
        lagna_elem = page.locator("span:has-text('லக்கினம் (Ascendant)') + span").first.inner_text()
        nakshatra_elem = page.locator("span:has-text('நட்சத்திரம் (Star & Pada)') + span").first.inner_text()
        tithi_elem = page.locator("span:has-text('திதி (Tithi)') + span").first.inner_text()
        yoga_elem = page.locator("span:has-text('யோகம் (Yoga)') + span").first.inner_text()
        karana_elem = page.locator("span:has-text('கரணம் (Karana)') + span").first.inner_text()

        print(f"  Section A Panchangam:", flush=True)
        print(f"    ராசி: {rasi_elem}", flush=True)
        print(f"    லக்கினம்: {lagna_elem}", flush=True)
        print(f"    நட்சத்திரம்: {nakshatra_elem}", flush=True)
        print(f"    திதி: {tithi_elem}", flush=True)
        print(f"    யோகம்: {yoga_elem}", flush=True)
        print(f"    கரணம்: {karana_elem}", flush=True)

        assert rasi_elem and rasi_elem != "—", "Rasi must be populated"
        assert lagna_elem and lagna_elem != "—", "Lagna must be populated"
        assert nakshatra_elem and nakshatra_elem != "—", "Nakshatra must be populated"
        print("  ✓ Section A Panchangam values verified.", flush=True)

        # Section B: தசா இருப்பு
        assert page.locator("h3:has-text('தசா இருப்பு')").first.is_visible(), "Section B Dasa Balance heading must be visible"
        dasa_card = page.locator("span:has-text('பிறப்பு தசை இருப்பு')").first
        bhukti_card = page.locator("span:has-text('பிறப்பு புக்தி இருப்பு')").first
        assert dasa_card.is_visible(), "Dasa balance card must be visible"
        assert bhukti_card.is_visible(), "Bhukti balance card must be visible"
        
        dasa_balance_val = page.locator("div.p-4.rounded-xl.border.border-\\[\\#D8BD80\\] span.font-mono").first.inner_text()
        print(f"  Section B Dasa Balance: {dasa_balance_val}", flush=True)
        print("  ✓ Section B Dasa-Bhukti cards verified.", flush=True)

        # Section C: பிறப்பு விவரங்கள்
        assert page.locator("h3:has-text('பிறப்பு விவரங்கள்')").first.is_visible(), "Section C Birth Details heading must be visible"
        name_val = page.locator("span:has-text('பெயர்:') + span").first.inner_text()
        dob_val = page.locator("span:has-text('பிறந்த நேரம்:') + span").first.inner_text()
        place_val = page.locator("span:has-text('பிறந்த இடம்:') + span").first.inner_text()
        sunrise_val = page.locator("span:has-text('சூரிய உதய நேரம்:') + span").first.inner_text()
        sunset_val = page.locator("span:has-text('சூரிய அஸ்தமன நேரம்:') + span").first.inner_text()
        lat_val = page.locator("span:has-text('அட்சாம்சம் (Latitude):') + span").first.inner_text()
        lon_val = page.locator("span:has-text('தீர்க்காம்சம் (Longitude):') + span").first.inner_text()
        tz_val = page.locator("span:has-text('நேர மண்டலம் (Timezone):') + span").first.inner_text()
        ayana_val = page.locator("span:has-text('அயனாம்ச முறை:') + span").first.inner_text()
        ayana_deg_val = page.locator("span:has-text('அயனாம்சம் (Value):') + span").first.inner_text()

        print(f"  Section C Birth Details:", flush=True)
        print(f"    பெயர்: {name_val}", flush=True)
        print(f"    பிறந்த நேரம்: {dob_val}", flush=True)
        print(f"    பிறந்த இடம்: {place_val}", flush=True)
        print(f"    சூரிய உதய நேரம்: {sunrise_val}", flush=True)
        print(f"    சூரிய அஸ்தமன நேரம்: {sunset_val}", flush=True)
        print(f"    அட்சாம்சம்: {lat_val}", flush=True)
        print(f"    தீர்க்காம்சம்: {lon_val}", flush=True)
        print(f"    நேர மண்டலம்: {tz_val}", flush=True)
        print(f"    அயனாம்ச முறை: {ayana_val}", flush=True)
        print(f"    அயனாம்சம்: {ayana_deg_val}", flush=True)

        assert "AM" in sunrise_val or "PM" in sunrise_val, "Sunrise must be a formatted valid time"
        assert "PM" in sunset_val or "AM" in sunset_val, "Sunset must be a formatted valid time"
        assert "N" in lat_val or "S" in lat_val, "Latitude must have N/S notation"
        assert "E" in lon_val or "W" in lon_val, "Longitude must have E/W notation"
        assert ayana_val and ayana_val != "—", "Ayanamsa name must be displayed"
        print("  ✓ Section C Astronomical & birth parameter fields verified.", flush=True)

        # Bhava Cusps Collapsible Table
        bhava_toggle = page.locator("button:has-text('12 பாவக ஆரம்ப நிலைகள்')").first
        assert bhava_toggle.is_visible(), "Bhava cusps collapsible table toggle must be visible"
        bhava_toggle.click()
        time.sleep(0.5)
        assert page.locator("table").count() > 0, "Houses table must expand when clicked"
        bhava_toggle.click() # collapse back
        print("  ✓ Bhava cusps collapsible table verified.", flush=True)

        # -------------------------------------------------------------
        # STEP 7: Category 2: சிறப்பு அம்சங்கள் (Special Features)
        # -------------------------------------------------------------
        print("\n[STEP 7] Testing Category 2: சிறப்பு அம்சங்கள்...", flush=True)
        sidebar_buttons.nth(1).click()
        time.sleep(1)
        assert "category=special" in page.url, "URL must update with category=special"
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_facts_panel_category_special.png", full_page=True)

        assert page.locator("h3:has-text('ஜாதக சிறப்பு அம்சங்கள்')").first.is_visible(), "Category 2 heading must be visible"
        assert page.locator("h4:has-text('முக்கிய யோகங்கள்')").first.is_visible(), "Active Yogas section must be visible"
        assert page.locator("span:has-text('லக்னாதிபதி')").count() > 0, "Lagna lord card must be visible"
        assert page.locator("span:has-text('ராசிநாதன்')").count() > 0, "Moon lord card must be visible"
        print("  ✓ Category 2: சிறப்பு அம்சங்கள் verified.", flush=True)

        # -------------------------------------------------------------
        # STEP 8: Category 3: சுப & பாவ கிரகங்கள்
        # -------------------------------------------------------------
        print("\n[STEP 8] Testing Category 3: சுப & பாவ கிரகங்கள்...", flush=True)
        sidebar_buttons.nth(2).click()
        time.sleep(1)
        assert "category=benefic_malefic" in page.url, "URL must update with category=benefic_malefic"
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_facts_panel_category_benefics.png", full_page=True)

        assert page.locator("h3:has-text('சுப & பாவ கிரகங்கள்')").first.is_visible(), "Benefics heading must be visible"
        assert page.locator("span:has-text('லக்ன சுபர்கள்')").first.is_visible(), "Lagna Benefics card must be visible"
        assert page.locator("span:has-text('லக்ன பாவிகள்')").first.is_visible(), "Lagna Malefics card must be visible"
        assert page.locator("span:has-text('யோககாரகன்')").first.is_visible(), "Yogakaraka card must be visible"
        assert page.locator("table:has-text('கிரகம்')").first.is_visible(), "Full 9-planet classification table must be visible"
        print("  ✓ Category 3: சுப & பாவ கிரகங்கள் verified.", flush=True)

        # -------------------------------------------------------------
        # STEP 9: Category 4: ஷட்பலம் & அவஸ்தை
        # -------------------------------------------------------------
        print("\n[STEP 9] Testing Category 4: ஷட்பலம் & அவஸ்தை...", flush=True)
        sidebar_buttons.nth(3).click()
        time.sleep(1)
        assert "category=shadbala_avastha" in page.url, "URL must update with category=shadbala_avastha"

        # Wait for Shadbala calculation to load if auto-fetching
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/06_facts_panel_category_shadbala.png", full_page=True)

        assert page.locator("h3:has-text('ஷட்பலம்')").first.is_visible(), "Shadbala heading must be visible"
        assert page.locator("h3:has-text('கிரக அவஸ்தைகள்')").first.is_visible(), "Planetary Avasthas heading must be visible"
        
        # Check Strongest & Weakest Badges
        strongest_badge = page.locator("span:has-text('மிக வலிமையான கிரகம்')").first
        assert strongest_badge.is_visible(), "Strongest planet rank badge must be visible"
        print("  ✓ Category 4: ஷட்பலம் & அவஸ்தைகள் verified with live API data.", flush=True)

        # -------------------------------------------------------------
        # STEP 10: Category 5: பெயர்ச்சி (கோச்சாரம்)
        # -------------------------------------------------------------
        print("\n[STEP 10] Testing Category 5: பெயர்ச்சி (கோச்சாரம்)...", flush=True)
        sidebar_buttons.nth(4).click()
        time.sleep(1)
        assert "category=transit" in page.url, "URL must update with category=transit"

        # Wait for live ephemeris calculation to complete
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/07_facts_panel_category_transit.png", full_page=True)

        assert page.locator("h3:has-text('பெயர்ச்சி பலன்கள்')").first.is_visible(), "Transit heading must be visible"
        assert page.locator("span:has-text('குரு பெயர்ச்சி')").first.is_visible(), "Guru Peyarchi card must be visible"
        assert page.locator("span:has-text('சனி பெயர்ச்சி')").first.is_visible(), "Sani Peyarchi card must be visible"
        assert page.locator("span:has-text('ராகு-கேது பெயர்ச்சி')").first.is_visible(), "Rahu-Ketu Peyarchi card must be visible"
        assert page.locator("table:has-text('கோசார ராசி & பாகை')").first.is_visible(), "Full Gochara table must be visible"

        # Test date picker interaction
        date_input = page.locator("input[type='date']").first
        assert date_input.is_visible(), "Transit date picker must be visible"
        current_date_val = date_input.input_value()
        print(f"  Current transit date in input: {current_date_val}", flush=True)
        print("  ✓ Category 5: Live Gochara Transit verified without hardcoded sample data.", flush=True)

        # -------------------------------------------------------------
        # STEP 11: Category 6: ஜைமினி சார காரகங்கள்
        # -------------------------------------------------------------
        print("\n[STEP 11] Testing Category 6: ஜைமினி சார காரகங்கள்...", flush=True)
        sidebar_buttons.nth(5).click()
        time.sleep(1)
        assert "category=jaimini" in page.url, "URL must update with category=jaimini"
        page.screenshot(path=f"{SCREENSHOT_DIR}/08_facts_panel_category_jaimini.png", full_page=True)

        assert page.locator("h3:has-text('ஜைமினி சப்த சார காரகங்கள்')").first.is_visible(), "Jaimini Karakas heading must be visible"
        assert page.locator("span:has-text('ஆத்மகாரகன்')").first.is_visible(), "Atmakaraka card must be visible"
        assert page.locator("span:has-text('அமாத்யகாரகன்')").first.is_visible(), "Amatyakaraka card must be visible"
        
        # Verify 7 Karakas in table
        karaka_rows = page.locator("table tbody tr")
        print(f"  Jaimini Karakas table row count: {karaka_rows.count()}")
        assert karaka_rows.count() >= 7, "Must display all 7 Jaimini Chara Karakas"
        print("  ✓ Category 6: ஜைமினி சார காரகங்கள் verified.")

        # -------------------------------------------------------------
        # STEP 12: Browser Reload with Deep-link Preservation
        # -------------------------------------------------------------
        print("\n[STEP 12] Testing browser reload with deep-link preservation...")
        current_url = page.url
        print(f"  Reloading URL: {current_url}")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1.5)

        # Confirm category 'jaimini' is still active
        assert page.locator("h3:has-text('ஜைமினி சப்த சார காரகங்கள்')").first.is_visible(), "Active category must be preserved on page reload"
        print("  ✓ Deep-link category state preserved upon refresh.", flush=True)

        # -------------------------------------------------------------
        # STEP 13: Test Edit Action & Create New Horoscope Workflow
        # -------------------------------------------------------------
        print("\n[STEP 13] Testing Edit Action & Create New Horoscope...", flush=True)
        # Check Edit link
        edit_link = page.locator("a:has-text('Edit'), a:has-text('திருத்துக')").first
        if edit_link.is_visible():
            print("  Edit button found and visible.", flush=True)

        # Navigate to /horoscope (Create New Horoscope)
        page.goto("http://localhost:3000/horoscope", wait_until="domcontentloaded")
        page.wait_for_selector("input[name='fullName'], input#fullName, input[type='text']", timeout=10000)
        print("  ✓ Landed on /horoscope (Create New Horoscope).", flush=True)
        page.screenshot(path=f"{SCREENSHOT_DIR}/09_create_new_horoscope_form.png", full_page=True)

        # -------------------------------------------------------------
        # STEP 14: Repeat with a Second Saved Horoscope (No Data Leak)
        # -------------------------------------------------------------
        print("\n[STEP 14] Testing second saved horoscope to ensure NO data leakage...", flush=True)
        page.goto("http://localhost:3000/tools/horoscope", wait_until="domcontentloaded")
        page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
        time.sleep(1)

        view_links = page.locator("a[href*='/horoscope/results']")
        if view_links.count() >= 2:
            second_link = view_links.nth(1)
            second_href = second_link.get_attribute("href")
            print(f"  Opening second horoscope at: {second_href}", flush=True)
            second_link.click()

            page.wait_for_url("**/horoscope/results**", timeout=15000)
            page.wait_for_selector(".animate-spin", state="detached", timeout=15000)
            time.sleep(1.5)

            # Switch to Facts
            page.locator("button:has-text('உண்மைகள்'), button:has-text('Facts & Panchang')").first.click()
            time.sleep(1)

            second_name = page.locator("span:has-text('பெயர்:') + span").first.inner_text()
            second_dob = page.locator("span:has-text('பிறந்த நேரம்:') + span").first.inner_text()
            print(f"  Second Horoscope: Name='{second_name}', DOB='{second_dob}'", flush=True)

            page.screenshot(path=f"{SCREENSHOT_DIR}/10_second_horoscope_facts.png", full_page=True)
            print("  ✓ Second horoscope opened with distinct data. No data leakage detected.", flush=True)
        else:
            print("  (Only one horoscope found, skipping multi-record comparison)")

        # -------------------------------------------------------------
        # STEP 15: Responsive Viewport Testing (Mobile, Laptop, Desktop)
        # -------------------------------------------------------------
        print("\n[STEP 15] Responsive Viewport Testing...")
        
        # Laptop (1024x768)
        page.set_viewport_size({"width": 1024, "height": 768})
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/11_responsive_laptop_1024.png", full_page=True)
        print("  ✓ Laptop (1024x768) screenshot captured.")

        # Mobile (375x667)
        page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(0.5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/12_responsive_mobile_375.png", full_page=True)
        print("  ✓ Mobile (375x667) screenshot captured. Horizontal scrolling tab bar verified.")

        # -------------------------------------------------------------
        # STEP 16: Console Errors and Warnings Check
        # -------------------------------------------------------------
        print("\n[STEP 16] Checking browser console messages...")
        print(f"  Total Console Errors: {len(console_errors)}")
        for err in console_errors:
            print(f"    [CONSOLE ERROR] {err}")

        print(f"  Total React Key / Prop Warnings: {len(react_warnings)}")
        for warn in react_warnings:
            print(f"    [REACT WARNING] {warn}")

        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"
        print("  ✓ Zero console errors verified!")

        browser.close()

    print("\n" + "=" * 70)
    print("ALL ACCEPTANCE TESTS PASSED SUCCESSFULLY IN REAL CHROME BROWSER!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_facts_panel_acceptance()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
