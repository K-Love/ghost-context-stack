import asyncio
from playwright.async_api import async_playwright
import json
import os

async def scrape_cbs():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("Logging in to CBS Sports...")
        await page.goto("https://www.cbssports.com/login", wait_until="networkidle")
        
        # Wait for and fill login form
        try:
            # Handle cookie overlays if visible
            try:
                if await page.query_selector('button:has-text("Accept")'):
                    await page.click('button:has-text("Accept")')
            except:
                pass

            # Update selectors based on HTML inspection
            # Email input has name="email" and id="name" (from the raw form data)
            # Password input is likely name="password" but let's be flexible
            await page.wait_for_selector('input[name="email"]', timeout=20000)
            await page.fill('input[name="email"]', "kevinl0326@gmail.com")
            
            # The password field wasn't clearly shown in the truncate but common is name="password"
            # Looking for any input with type="password"
            await page.fill('input[type="password"]', "Idoitmyself$!25")
            
            # Use the form's data-id or common button text
            await page.click('button[type="submit"]')
            
            print("Login submitted. Waiting for navigation...")
            await page.wait_for_url("**/cbssports.com/**", timeout=30000)
            print("Login successful or redirected.")

        except Exception as e:
            print(f"Login error: {e}")
            await page.screenshot(path="login_error.png")

        print("Navigating to league page...")
        await page.goto("https://wbs.baseball.cbssports.com")
        await page.wait_for_load_state("networkidle")

        league_data = {
            "draft_order": [],
            "settings": {},
            "rankings": []
        }

        # 1. Extract Settings (Scoring/Roster)
        print("Scraping settings...")
        try:
            await page.goto("https://wbs.baseball.cbssports.com/setup/league-settings/summary")
            # This is a guestimate of the URL, we'll try to find it via navigation if it fails
            content = await page.content()
            league_data["settings_raw"] = content[:5000] # Basic capture if specific parsing fails
        except:
            pass

        # 2. Extract Draft Order
        print("Scraping draft order...")
        try:
            await page.goto("https://wbs.baseball.cbssports.com/draft/order")
            await page.wait_for_selector("table", timeout=10000)
            
            # Look for tables with team names. CBS often uses classes like 'data' or 'Table'
            rows = await page.query_selector_all("tr")
            for row in rows:
                text = await row.inner_text()
                if text.strip():
                    league_data["draft_order"].append(text.split('\t'))
        except Exception as e:
            print(f"Draft order error: {e}")
            await page.screenshot(path="draft_order_error.png")

        # 3. Extract Rankings / Player Pool
        print("Scraping rankings...")
        try:
            # Rankings are often in the 'Draft' menu or 'Players' list
            await page.goto("https://wbs.baseball.cbssports.com/players/player-stats")
            await page.wait_for_load_state("networkidle")
            
            players = await page.query_selector_all("tr")
            for player in players[:50]: # Top 50 for now
                text = await player.inner_text()
                league_data["rankings"].append(text.split('\t'))
        except Exception as e:
            print(f"Rankings error: {e}")

        # Save to file
        with open("cbs_league_data.json", "w") as f:
            json.dump(league_data, f, indent=4)

        await browser.close()
        print("Scraping complete.")

if __name__ == "__main__":
    asyncio.run(scrape_cbs())
