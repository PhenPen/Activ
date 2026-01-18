from playwright.sync_api import sync_playwright
import time

PROFILE_URL = "https://myriad.markets/profile/0x2993249A3D107B759c886a4BD4e02B70d471eA9B?tab=activity"

def scrape_activity():
    """
    Scrapes the activity tab of the target profile.
    Returns a list of activity dictionaries.
    """
    activities = []
    
    with sync_playwright() as p:
        # Launch browser with real UA
        browser = p.chromium.launch(headless=True)
        # Use a context to set UA
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = context.new_page()
        
        try:
            print(f"Navigating to {PROFILE_URL}...")
            page.goto(PROFILE_URL, timeout=60000)
            
            # Handle cookie banner
            try:
                if page.get_by_text("Allow all").is_visible():
                    page.get_by_text("Allow all").click()
                    print("Clicked 'Allow all' cookies.")
            except:
                pass

            # Ensure Activity tab is selected
            try:
                # Wait for tab to appear
                page.wait_for_selector("text=Activity", timeout=10000)
                # Click it just in case URL didn't switch it
                page.get_by_text("Activity").click()
                print("Clicked 'Activity' tab.")
            except Exception as e:
                print(f"Error clicking tab: {e}")

            # Wait for content to load
            print("Waiting for activity data (sold/bought)...")
            try:
                # Wait for 'sold' or 'bought' to appear
                page.wait_for_selector("text=sold", timeout=20000)
            except:
                print("Timeout waiting for 'sold' keyword.")

            # Scroll to trigger lazy load
            page.mouse.wheel(0, 1000)
            time.sleep(3)
            
            # Extract content using text parsing (more robust than selectors for this structure)
            page_text = page.locator("body").inner_text()
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            print(f"Extracted {len(lines)} lines of text from page.")
            
            # Parse the lines
            # Pattern from dump:
            # Line A: "Buy" (optional/sometimes missing or merged)
            # Line B: "Arii_Defi bought 175 shares of Below at $0.57 (100) on"
            # Line C: "XMR - above or below $600 on Monday at noon UTC?"
            # Line D: "4 hours ago"
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check for activity signature
                # We look for the main description line
                if "Arii_Defi" in line and ("bought" in line or "sold" in line) and "shares of" in line:
                    try:
                        # Extract details
                        description = line
                        
                        # Determine Type
                        act_type = "Unknown"
                        if "bought" in line:
                            act_type = "Buy"
                        elif "sold" in line:
                            act_type = "Sell"
                            
                        # Try to get Market (Next line)
                        market_name = "Unknown"
                        if i + 1 < len(lines):
                            market_name = lines[i+1]
                            
                        # Try to get Time (Line after market)
                        time_str = "Unknown"
                        if i + 2 < len(lines):
                            time_str = lines[i+2]
                        
                        # Basic Cleanup
                        # sometimes text dump might include extra lines, but usually strict structure holds
                        # Verify if 'time_str' looks like time (ends with 'ago')
                        # If not, maybe we shifted.
                        
                        activity = {
                            "type": act_type,
                            "description": description,
                            "market_name": market_name,
                            "timestamp_str": time_str
                        }
                        activities.append(activity)
                        
                        # Advance index effectively
                        i += 2 
                    except Exception as e:
                        print(f"Error parsing line {i}: {e}")
                
                i += 1
            
            print(f"Parsed {len(activities)} activities.")

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            browser.close()
            
    return activities

if __name__ == "__main__":
    # Test run
    import storage
    print("Running test scrape...")
    data = scrape_activity()
    print(f"Scraped {len(data)} items.")
    storage.save_new_activities(data)
