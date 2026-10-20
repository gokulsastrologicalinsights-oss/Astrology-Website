"""Test browser authentication and navigation to D1/D9."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
    page.wait_for_selector("input[type='password']", timeout=5000)
    print("Login page title:", page.title(), flush=True)

    # Fill credentials
    page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
    page.locator("input[type='password']").fill("Gokul741@")
    page.locator("button[type='submit']").click()

    page.wait_for_url("**/dashboard**", timeout=10000)
    print("Login successful! Landed on:", page.url, flush=True)

    # Check /tools
    page.goto("http://localhost:3000/tools", wait_until="domcontentloaded")
    page.wait_for_selector("a[href='/tools/d1-d9']", timeout=5000)
    print("Tools URL:", page.url, flush=True)
    card_count = page.locator("a[href='/tools/d1-d9']").count()
    print("D1/D9 card count on /tools:", card_count, flush=True)

    # Check /dashboard quick navigation
    page.goto("http://localhost:3000/dashboard", wait_until="domcontentloaded")
    dash_link_count = page.locator("a[href='/tools/d1-d9']").count()
    print("D1/D9 link count on /dashboard:", dash_link_count, flush=True)

    # Check /tools/d1-d9
    page.goto("http://localhost:3000/tools/d1-d9", wait_until="domcontentloaded")
    print("D1/D9 page URL:", page.url, flush=True)
    print("D1/D9 h1:", page.locator("h1").inner_text(), flush=True)

    browser.close()
