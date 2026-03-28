import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launching with a headful-like user agent to avoid bot detection
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Step 1: Logging into CBS Sports...")
        try:
            await page.goto("https://www.cbssports.com/login", wait_until="domcontentloaded")
            await page.fill('input[name="email"]', "kevinl0326@gmail.com")
            await page.fill('input[name="password"]', "Idoitmyself$!25")
            await page.keyboard.press("Enter")
            await asyncio.sleep(5) # Wait for login processing
            print(f"Logged in. Current URL: {page.url}")
        except Exception as e:
            print(f"Login failed: {e}")
            await browser.close()
            return

        print("Step 2: Locating 'K-Love' league...")
        # Check standard fantasy dashboard
        dashboard_urls = [
            "https://www.cbssports.com/fantasy/baseball/",
            "https://www.cbssports.com/fantasy/my-teams/",
            "https://www.cbssports.com/fantasy/baseball/my-leagues/"
        ]
        
        league_url = None
        for url in dashboard_urls:
            print(f"Checking {url}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # Search for "K-Love" in link text
                link = await page.get_by_role("link", name="K-Love", exact=False).first
                if await link.count() > 0:
                    league_url = await link.get_attribute("href")
                    if league_url and not league_url.startswith("http"):
                        league_url = "https://www.cbssports.com" + league_url
                    print(f"Found League URL: {league_url}")
                    break
            except Exception:
                continue

        if not league_url:
            print("Could not find 'K-Love' league. Aborting.")
            await page.screenshot(path="search_failure.png")
            await browser.close()
            return

        # Step 3 & 5: Extract Data
        league_data = {
            "league_name": "K-Love",
            "source_url": league_url,
            "player_pool": [],
            "draft_settings": {},
            "draft_order": [],
            "rankings": []
        }

        # Sub-task: Draft Order
        print("Extracting Draft Order...")
        try:
            # Try to guess the draft order path or find a link
            await page.goto(league_url, wait_until="domcontentloaded")
            draft_link = page.get_by_role("link", name="Draft", exact=False).first
            if await draft_link.count() > 0:
                await draft_link.click()
                await asyncio.sleep(2)
                # Pull table data
                rows = await page.query_selector_all("tr")
                for row in rows:
                    text = await row.inner_text()
                    if text.strip():
                        league_data["draft_order"].append(text.split('\t')[0].strip())
        except Exception as e:
            print(f"Draft order extraction warning: {e}")

        # Sub-task: Rankings / Draft Room
        print("Extracting Player Rankings...")
        # Often leagues have a 'Draft Prep' or 'Rankings' section
        try:
            # Heuristic: look for player names in common table formats
            players = await page.query_selector_all(".player-name, .playerName, .playerLink")
            for p_elem in players[:100]: # Limit to top 100 for brevity
                name = await p_elem.inner_text()
                if name.strip():
                    league_data["rankings"].append(name.strip())
        except Exception as e:
            print(f"Rankings extraction warning: {e}")

        # Save to JSON
        with open("cbs_league_data.json", "w") as f:
            json.dump(league_data, f, indent=4)
        print("Successfully saved data to cbs_league_data.json")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
