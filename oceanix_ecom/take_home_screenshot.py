import asyncio
from playwright.async_api import async_playwright
import os

async def take_home_screenshot():
    screenshot_dir = r"d:\OCEANIX\screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        print("Navigating to http://127.0.0.1:8000...")
        await page.goto("http://127.0.0.1:8000")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "current_home.png"), full_page=True)
        await browser.close()
        print("Home screenshot saved successfully!")

if __name__ == "__main__":
    asyncio.run(take_home_screenshot())
