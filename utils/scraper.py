from playwright.async_api import async_playwright
from .helper import render_actions

user_actions = ["click", "fill", "check", "hover"]


async def run_actions(url, actions, automation_id):
    async with async_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = await p.chromium.launch(channel="chrome")
        page = await browser.new_page()
        await page.goto(url)

        results = []

        for action in actions:
            result = await render_actions(
                page=page,
                user_action=action.model_dump(),
                automation_id=automation_id,
            )
            results.append(result)
            print(action.id)
        await browser.close()

        return results
