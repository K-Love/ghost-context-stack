import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Step 1: Logging in...")
        await page.goto("https://www.cbssports.com/login", wait_until="domcontentloaded")
        await page.fill('input[name="email"]', "kevinl0326@gmail.com")
        await page.fill('input[name="password"]', "Idoitmyself$!25")
        await page.keyboard.press("Enter")
        await asyncio.sleep(8)

        # Let's see what links ARE on the page
        print("Step 2: Scanning for ANY league links...")
        await page.goto("https://www.cbssports.com/fantasy/", wait_until="domcontentloaded")
        links = await page.query_selector_all("a")
        league_candidates = []
        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute("href")
            # CBS fantasy leagues usually have numeric IDs or path patterns
            if href and ("/fantasy/baseball/league/" in href or "baseball.fantasysports.cbssports.com" in href):
                league_candidates.append({"text": text.strip(), "href": href})
        
        print(f"Found {len(league_candidates)} potential league links.")
        for c in league_candidates:
            print(f"- {c['text']} ({c['href']})")

        # If we find "K-Love" or if there's only one league, let's go there
        target_league = next((c for c in league_candidates if "K-Love" in c['text']), None)
        if not target_league and league_candidates:
            target_league = league_candidates[0] # Fallback to first baseball league found
            print(f"No exact match for 'K-Love'. Choosing first available: {target_league['text']}")

        if target_league:
            print(f"Targeting: {target_league['text']}")
            league_url = target_league['href']
            if not league_url.startswith("http"):
                league_url = "https://www.cbssports.com" + league_url
            
            await page.goto(league_url, wait_until="domcontentloaded")
            
            # Final data extraction (simplified for this pass)
            league_data = {
                "league_name": target_league['text'],
                "player_pool": [],
                "draft_order": [],
                "rankings": []
            }
            
            # Capture what we can
            content = await page.inner_text("body")
            league_data["raw_homepage_text"] = content[:5000] # for debug/parsing
            
            with open("cbs_league_data.json", "w") as f:
                json.dump(league_data, f, indent=4)
            print("Data saved.")
        else:
            print("No leagues found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
