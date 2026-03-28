import asyncio
from playwright.async_api import async_playwright

async def debug_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("1. Loading login page...")
        await page.goto("https://www.cbssports.com/login", wait_until="networkidle")
        
        # Fill email
        await page.fill('input[name="email"]', "kevinl0326@gmail.com")
        # Fill password - using a broad selector for password
        await page.fill('input[type="password"]', "Idoitmyself$!25")
        
        print("2. Clicking submit...")
        await page.click('button[type="submit"]')
        
        # Wait a bit for transition
        await page.wait_for_timeout(5000)
        
        print(f"3. Current URL: {page.url}")
        
        # Try to navigate straight to the league
        print("4. Attempting league navigation...")
        await page.goto("https://wbs.baseball.cbssports.com", wait_until="networkidle")
        print(f"5. Post-navigation URL: {page.url}")
        
        # Print first 1000 chars of body to see if we're on a login screen or league
        content = await page.content()
        print(f"6. Page content head: {content[:1000]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login())
