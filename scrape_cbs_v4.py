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

        # Check for any baseball specific URLs after login
        print("Step 2: Searching for 'K-Love' league again...")
        # Check standard fantasy dashboard
        urls_to_check = [
            "https://www.cbssports.com/fantasy/baseball/my-leagues/",
            "https://www.cbssports.com/fantasy/baseball/games/",
            "https://www.cbssports.com/fantasy/my-teams/"
        ]

        found_league = False
        for url in urls_to_check:
            print(f"Checking {url}...")
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            # Check for "K-Love" in any link text
            links = await page.query_selector_all("a")
            for link in links:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                if "K-Love" in text:
                    print(f"Found K-Love league: {text} at {href}")
                    if href and not href.startswith("http"):
                        href = "https://www.cbssports.com" + href
                    
                    # Navigate and pull basic data
                    await page.goto(href, wait_until="domcontentloaded")
                    league_data = {
                        "league_name": "K-Love",
                        "source_url": href,
                        "player_pool": [],
                        "draft_settings": {},
                        "draft_order": [],
                        "rankings": []
                    }
                    
                    # Draft settings and order
                    # CBS usually has a 'League' menu. Let's look for settings/draft
                    settings_link = await page.get_by_role("link", name="Settings", exact=False).first
                    if await settings_link.count() > 0:
                        settings_url = await settings_link.get_attribute("href")
                        if settings_url:
                             if not settings_url.startswith("http"): settings_url = "https://www.cbssports.com" + settings_url
                             await page.goto(settings_url, wait_until="domcontentloaded")
                             league_data["draft_settings_raw"] = await page.inner_text("body")
                    
                    with open("cbs_league_data.json", "w") as f:
                        json.dump(league_data, f, indent=4)
                    print("Data saved.")
                    found_league = True
                    break
            if found_league: break
        
        if not found_league:
            print("No K-Love league found. Writing basic session info instead.")
            # Let's save the current page content to see what's happening
            # with open("debug_content.html", "w") as f:
            #     f.write(await page.content())
            print("Current URL: " + page.url)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
