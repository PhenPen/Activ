from playwright.sync_api import sync_playwright
import time

print("Starting test...")
with sync_playwright() as p:
    print("Playwright init done.")
    try:
        browser = p.chromium.launch(headless=True)
        print("Browser launched.")
        page = browser.new_page()
        print("Page created.")
        page.goto("https://www.google.com")
        print("Navigated to Google: ", page.title())
        
        print("Navigating to Myriad...")
        page.goto("https://myriad.markets/profile/0x2993249A3D107B759c886a4BD4e02B70d471eA9B?tab=activity", timeout=30000)
        print("Navigated to Myriad: ", page.title())
        
        # Dump partial content
        print("Content preview:", page.content()[:200])
        
        browser.close()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
