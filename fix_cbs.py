import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Try with visible sometimes can help but headless should work
        context = await browser.new_context()
        page = await context.new_page()
        
        # CBS sometimes uses a two-step or multi-frame login
        # Let's try to find exactly what's failing.
        await page.goto("https://www.cbssports.com/login", wait_until="networkidle")
        
        # Check if email/password inputs exist. 
        # Using a broader wait for visibility
        await page.wait_for_selector('input[name="email"]', state="visible", timeout=20000)
        await page.fill('input[name="email"]', "kevinl0326@gmail.com")
        await page.fill('input[type="password"]', "Idoitmyself$!25")
        
        # Try clicking by text or common class
        login_btn = page.get_by_role("button", name="Log In").first
        if await login_btn.count() > 0:
            await login_btn.click()
        else:
            await page.click('button[type="submit"]')
        
        # Wait for the redirection - the URL changes when login is successful
        print(f"Login clicked at {page.url}. Monitoring URL changes...")
        try:
            # Wait for navigation to complete - CBS might redirect to a specific page
            await page.wait_for_timeout(5000)
            print(f"URL after 5s: {page.url}")
        except:
            pass

        # Explicitly go to the league URL now that session cookies should be set
        league_url = "https://wbs.baseball.cbssports.com"
        print(f"Navigating to league: {league_url}")
        await page.goto(league_url, wait_until="networkidle")
        print(f"Final URL: {page.url}")
        
        # If we got in, the URL should not contain 'login' or 'account' redirects
        if "login" not in page.url and "baseball.cbssports.com" in page.url:
            print("Successfully reached the league page!")
            # Try to grab draft order specifically
            print("Navigating to draft order...")
            await page.goto("https://wbs.baseball.cbssports.com/draft/order", wait_until="networkidle")
            
            # Use a generic selector to find any tables
            tables = await page.query_selector_all("table")
            print(f"Found {len(tables)} tables on draft order page.")
            
            content = await page.content()
            with open("draft_order_page.html", "w") as f:
                f.write(content)
                
            # Grab league settings too
            print("Navigating to league settings summary...")
            await page.goto("https://wbs.baseball.cbssports.com/setup/league-settings/summary", wait_until="networkidle")
            settings_content = await page.content()
            with open("league_settings.html", "w") as f:
                f.write(settings_content)

        else:
            print("Failed to reach league. Capturing error state...")
            await page.screenshot(path="final_fail.png")
            content = await page.content()
            with open("fail_content.html", "w") as f:
                f.write(content)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
