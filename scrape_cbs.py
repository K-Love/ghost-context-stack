import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Navigating to login page...")
        await page.goto("https://www.cbssports.com/login", wait_until="networkidle")

        # Fill credentials
        print("Filling credentials...")
        await page.fill('input[name="email"]', "kevinl0326@gmail.com")
        await page.fill('input[name="password"]', "Idoitmyself$!25")
        
        print("Submitting login form...")
        await page.keyboard.press("Enter")
        
        # Give some time for navigation and session setup
        await asyncio.sleep(8)
        
        print(f"Current URL after login: {page.url}")
        
        # Navigate to Fantasy Baseball home
        print("Navigating to Fantasy Baseball...")
        try:
            await page.goto("https://www.cbssports.com/fantasy/baseball/", timeout=60000)
        except Exception as e:
            print(f"Initial navigation failed: {e}. Trying to reload.")
            await page.reload(timeout=60000)
        
        # Look for "K-Love" league
        print("Searching for K-Love league...")
        # Try to wait for any content that indicates leagues are loaded
        await asyncio.sleep(5)
        
        league_links = await page.query_selector_all('a:has-text("K-Love")')
        if not league_links:
            print("Trying My Leagues page...")
            try:
                await page.goto("https://www.cbssports.com/fantasy/baseball/my-leagues/", timeout=60000)
                await asyncio.sleep(5)
                league_links = await page.query_selector_all('a:has-text("K-Love")')
            except Exception as e:
                print(f"My Leagues navigation failed: {e}")

        if league_links:
            # We'll just try to click it
            await league_links[0].click()
            await page.wait_for_load_state("networkidle")
            league_url = page.url
            print(f"Landed on league page: {league_url}")
            
            league_data = {
                "league_name": "K-Love",
                "player_pool": [],
                "draft_settings": {},
                "draft_order": [],
                "rankings": []
            }
            
            # Navigate directly to common fantasy league components
            # We'll try to find sections like 'Draft', 'Roster', 'Players'
            
            # Draft Order
            draft_order_url = league_url.rstrip('/') + "/draft/order"
            print(f"Checking draft order at: {draft_order_url}")
            await page.goto(draft_order_url, wait_until="networkidle")
            # Scrape draft order
            rows = await page.query_selector_all('table tr')
            for row in rows:
                text = await row.inner_text()
                if text.strip():
                    league_data["draft_order"].append(text.strip().replace('\t', ' '))

            # League Settings (for Draft Rules)
            # Typically at /settings or /league/settings
            settings_url = league_url.rstrip('/') + "/settings"
            print(f"Checking settings at: {settings_url}")
            await page.goto(settings_url, wait_until="networkidle")
            league_data["draft_settings_raw"] = await page.inner_text('body')

            # Rankings / Draft Room
            # Use /draft/room or /draft/rankings
            rankings_url = league_url.rstrip('/') + "/draft/rankings"
            print(f"Checking rankings at: {rankings_url}")
            await page.goto(rankings_url, wait_until="networkidle")
            players = await page.query_selector_all('.playerName, .player-name')
            for player in players:
                name = await player.inner_text()
                if name.strip():
                    league_data["rankings"].append(name.strip())

            # Player Pool
            # Usually under /players/stats
            players_url = league_url.rstrip('/') + "/players/stats"
            print(f"Checking player pool at: {players_url}")
            await page.goto(players_url, wait_until="networkidle")
            pool = await page.query_selector_all('.playerName, .player-name')
            for item in pool:
                name = await item.inner_text()
                if name.strip():
                    league_data["player_pool"].append(name.strip())

            with open("cbs_league_data.json", "w") as f:
                json.dump(league_data, f, indent=4)
            print("Data saved.")
        else:
            print("Could not find K-Love league links.")
            await page.screenshot(path="leagues_not_found.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
