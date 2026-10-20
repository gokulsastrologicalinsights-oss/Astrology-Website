"""Inspect links on dashboard."""
from playwright.sync_api import sync_playwright

def run_inspection():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.goto("http://localhost:3000/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='password']", timeout=5000)

        # Fill credentials
        page.locator("input[type='text'], input[name='identifier']").first.fill("admin@gokul-astrology.local")
        page.locator("input[type='password']").fill("Gokul741@")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/dashboard**", timeout=10000)
        page.wait_for_selector("text=Quick Navigation", timeout=5000)
        
        links = [a.get_attribute("href") for a in page.locator("a").all()]
        print("All dashboard links containing /tools:", [l for l in links if l and "/tools" in l], flush=True)

        browser.close()

if __name__ == "__main__":
    run_inspection()

